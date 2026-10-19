"""synth_v6_home.py: where is our army when our carriers die at home? (re-check of analyst 1's 'the army does not come
home', Frog only, for every game with per-turn dumps)

Per-turn launcher rows (tools/replay-dump.sh --sa, the analysts' dumps: maxwell games top2/a0/sa all rounds, carl games
top2/a1/sa300 to about r300). For each of our carrier deaths at round <= 250 within d2 100 of one of our HQs
(deaths.csv), at the death round: our launchers alive (rows that round), ours within r2 100 of the death tile ('near'),
ours nearer the enemy HQs than ours ('away'), and their launchers within r2 100 of the death tile.
Per class (synth_common.klass): deaths covered, medians, and the share of deaths where we had >= 3 launchers 'away'
and fewer near than they did (an army elsewhere while the home well is camped: what a wider recall could answer).
Usage: python3 -I synth_v6_home.py
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_common import *

SP = '/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/top2'


def sa_pos(G, side):
    for p in (f"{SP}/a0/sa/{G['m']}g{G['g']}{side}/sa_L.csv", f"{SP}/a1/sa300/{G['m']}g{G['g']}{side}/sa_L.csv"):
        if os.path.exists(p):
            by = collections.defaultdict(list)
            with open(p) as fh:
                for r in csv.DictReader(fh):
                    rn = int(r['round'])
                    if rn > 260: break
                    by[rn].append((int(r['x']), int(r['y'])))
            return by
    return None


def main():
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    for G in distinct():
        u, t = G['us'], G['them']
        pu, pt = sa_pos(G, u), sa_pos(G, t)
        if pu is None or pt is None: continue
        k = klass(G)
        ours, theirs = G['hqs'][u], G['hqs'][t]
        for r in deaths(G, u):
            if r['type'] != 'C' or int(r['round']) > 250: continue
            xy = (int(r['x']), int(r['y']))
            if mind2(xy, ours) > 100: continue
            rn = int(r['round'])
            L = pu.get(rn, []); E = pt.get(rn, [])
            near = sum(1 for p in L if d2(p, xy) <= 100)
            away = sum(1 for p in L if mind2(p, theirs) < mind2(p, ours))
            en = sum(1 for p in E if d2(p, xy) <= 100)
            a = agg[k]
            a['alive'].append(len(L)); a['near'].append(near); a['away'].append(away); a['enear'].append(en)
            a['elsewhere'].append(away >= 3 and near < en)
            a['games'].append(G['m'] * 10 + G['g'])
    for k in ('A', 'A0', 'BC', 'W'):
        a = agg[k]
        n = len(a['alive'])
        if not n: print(f'{k}: no covered deaths'); continue
        print(f"{k:3}: home carrier deaths <= r250 covered {n} (games {len(set(a['games']))}); median our launchers alive "
              f"{med(a['alive'])}, near the death r2<=100 {med(a['near'])}, theirs near {med(a['enear'])}, ours nearer the enemy HQ "
              f"{med(a['away'])}; deaths with >=3 of ours away and fewer near than theirs: {sum(a['elsewhere'])} ({sum(a['elsewhere']) / n:.2f})")


main()
