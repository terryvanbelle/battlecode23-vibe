# The first launcher contact of each game (sa_L, both sides): t0 = first round a launcher of either side has an enemy
# launcher within r2 20. At t0: launchers of each side within r2 64 of the contact point (the launcher that saw it),
# launchers alive per side, contact prog (0 = our HQ, Euclidean), and launcher deaths per side in [t0, t0 + W)
# (deaths.csv), W = 40. Also the same counts at the first contact in which a launcher dies within 10 rounds ("first
# lethal contact").
import sys, os, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
WIN = 40


def prog(G, p):
    H = hqs(G['m'], G['g'])
    du = min(d2(p, h) for h in H[G['us']]); dt = min(d2(p, h) for h in H[G['them']])
    return math.sqrt(du) / (math.sqrt(du) + math.sqrt(dt))


def contact(G, after=0):
    rows = {s: sa(G['m'], G['g'], s, 'L', 600) for s in (G['us'], G['them'])}
    byr = {s: collections.defaultdict(list) for s in rows}
    for s in rows:
        for r in rows[s]: byr[s][r['round']].append(r)
    dl = [(int(d['round']), d['side']) for d in rd(G['m'], 'deaths') if int(d['game']) == G['g'] and d['type'] == 'L']
    rounds = sorted(set(byr[G['us']]) | set(byr[G['them']]))
    for rn in rounds:
        if rn < after: continue
        for s in (G['us'], G['them']):
            for r in byr[s][rn]:
                if r['enemy_L_20'] > 0:
                    p = (r['x'], r['y'])
                    nU = sum(1 for q in byr[G['us']][rn] if d2((q['x'], q['y']), p) <= 64)
                    nT = sum(1 for q in byr[G['them']][rn] if d2((q['x'], q['y']), p) <= 64)
                    kU = sum(1 for (dr, ds) in dl if rn <= dr < rn + WIN and ds == G['them'])
                    kT = sum(1 for (dr, ds) in dl if rn <= dr < rn + WIN and ds == G['us'])
                    lethal = any(rn <= dr < rn + 10 for (dr, ds) in dl)
                    return dict(t0=rn, nU=nU, nT=nT, aU=len(byr[G['us']][rn]), aT=len(byr[G['them']][rn]),
                                prog=round(prog(G, p), 2), kU=kU, kT=kT, lethal=lethal)
    return None


def first_lethal(G):
    a = 0
    for _ in range(60):
        c = contact(G, a)
        if c is None or c['lethal']: return c
        a = c['t0'] + 1
    return None


if __name__ == '__main__':
    print(f'| game | res | first contact r | near (r2 64) us v them | alive us v them | prog | L kills in {WIN} r us/them | '
          f'first lethal contact r | near | alive | prog | kills {WIN} r us/them |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|')
    agg = {r: collections.Counter() for r in 'WL'}
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        c = contact(G); f = first_lethal(G); res = 'W' if G['won'] else 'L'
        cell = lambda c: (f"r{c['t0']} | {c['nU']}v{c['nT']} | {c['aU']}v{c['aT']} | {c['prog']} | {c['kU']}/{c['kT']}"
                          if c else '- | - | - | - | -')
        print(f"| {label(G)} | {res} | {cell(c)} | {cell(f)} |")
        if f:
            a = agg[res]; a['n'] += 1; a['behind'] += f['nU'] < f['nT']; a['ahead'] += f['nU'] > f['nT']
            a['kU'] += f['kU']; a['kT'] += f['kT']; a['home'] += f['prog'] < 0.45
    for res in 'LW':
        a = agg[res]
        print(f"{res}: first lethal contact: us fewer near in {a['behind']}/{a['n']}, more in {a['ahead']}/{a['n']}; "
              f"at prog < 0.45 in {a['home']}/{a['n']}; launcher kills in the next {WIN} rounds us {a['kU']} them {a['kT']}")
