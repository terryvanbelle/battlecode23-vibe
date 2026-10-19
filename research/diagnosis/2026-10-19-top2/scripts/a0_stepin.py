# Step-ins against partly unseen enemies, r <= RMAX (default 200), from sa_L of both sides. A step-in is a launcher turn
# that starts with an enemy launcher within r2 20 (enemy_L_20 >= 1), moves, and ends nearer the nearest enemy launcher.
# Its new tile is the robot's position at its next row (or its death tile, deaths.csv). reach = enemy launchers whose
# start-of-turn position (same round) is within r2 16 of the new tile (they can hit it without moving); seen = enemy_L_20
# at the start of the turn. A blind step-in has reach > seen (it stepped into more guns than it saw); a deep one has
# reach >= 3. Outcome: the launcher dies within 5 rounds (deaths.csv). Approximation: robots act in id order within a
# round, so start-of-turn positions of the other side can be up to one move stale.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200


def stepins(G, side):
    own = sa(G['m'], G['g'], side, 'L', RMAX + 1); opp = sa(G['m'], G['g'], other(side), 'L', RMAX + 1)
    epos = collections.defaultdict(list)
    for r in opp: epos[r['round']].append((r['x'], r['y']))
    nxt = {}
    for r in own: nxt[(r['id'], r['round'])] = (r['x'], r['y'])
    death = {int(d['id']): (int(d['round']), (int(d['x']), int(d['y']))) for d in rd(G['m'], 'deaths')
             if int(d['game']) == G['g'] and d['side'] == side and d['type'] == 'L'}
    c = collections.Counter()
    for r in own:
        if r['round'] > RMAX or r['enemy_L_20'] < 1 or r['moved'] != 1: continue
        p = (r['x'], r['y']); E = epos[r['round']]
        if not E: continue
        q = nxt.get((r['id'], r['round'] + 1))
        dd = death.get(r['id'])
        if q is None and dd and dd[0] == r['round']: q = dd[1]
        if q is None: continue
        if min(d2(q, e) for e in E) >= min(d2(p, e) for e in E): continue
        reach = sum(1 for e in E if d2(q, e) <= 16)
        dies = bool(dd and r['round'] <= dd[0] <= r['round'] + 5)
        blind = reach > r['enemy_L_20']
        c['n'] += 1; c['blind'] += blind; c['deep'] += reach >= 3; c['dies'] += dies
        c['blind_dies'] += blind and dies; c['clear_dies'] += (not blind) and dies
        c['deep_dies'] += reach >= 3 and dies
    return c


if __name__ == '__main__':
    f = lambda a, b: f"{a/b:.2f}" if b else '-'
    print(f'r <= {RMAX}')
    print('| game | res | step-ins us/them | blind share us/them | reach>=3 share us/them | dies in 5 after blind us/them | after seen-only us/them |')
    print('|---|---|---|---|---|---|---|')
    agg = {r: {'us': collections.Counter(), 'them': collections.Counter()} for r in 'WL'}
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        res = 'W' if G['won'] else 'L'
        a, b = stepins(G, G['us']), stepins(G, G['them'])
        agg[res]['us'].update(a); agg[res]['them'].update(b)
        print(f"| {label(G)} | {res} | {a['n']}/{b['n']} | {f(a['blind'],a['n'])}/{f(b['blind'],b['n'])} | {f(a['deep'],a['n'])}/{f(b['deep'],b['n'])} | "
              f"{f(a['blind_dies'],a['blind'])}/{f(b['blind_dies'],b['blind'])} | {f(a['clear_dies'],a['n']-a['blind'])}/{f(b['clear_dies'],b['n']-b['blind'])} |")
    for res in 'LW':
        for who in ('us', 'them'):
            c = agg[res][who]
            print(f"{res} {who}: step-ins {c['n']}, blind {c['blind']} ({f(c['blind'],c['n'])}), reach>=3 {c['deep']} ({f(c['deep'],c['n'])}); "
                  f"dies within 5 rounds: after blind {f(c['blind_dies'],c['blind'])}, after seen-only {f(c['clear_dies'],c['n']-c['blind'])}, after reach>=3 {f(c['deep_dies'],c['deep'])}")
