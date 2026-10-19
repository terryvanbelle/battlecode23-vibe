"""a1_wells: per game and side, the wells mined before round R (trips.csv: collects by well, its type and its distance
to each side's nearest HQ) and how trips ended (deposit / death / other)."""
import sys, math
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
R = int(sys.argv[1]) if len(sys.argv) > 1 else 150
sel = COLLAPSE + EARLYWIN
if len(sys.argv) > 2:
    sel = [tuple(int(x) for x in s.split(':')) for s in sys.argv[2].split(',')]
for (m, g) in sel:
    G = games(m)[g]; us = G['us']; th = G['them']
    hq = collections.defaultdict(list)
    for r in rows(m, 'hq'):
        if int(r['game']) == g and r['round'] == '25':
            hq[r['side']].append((int(r['x']), int(r['y'])))
    def dist(side, x, y):
        return min(math.sqrt(d2((x, y), h)) for h in hq[side])
    W = collections.defaultdict(lambda: collections.Counter())
    for t in rows(m, 'trips'):
        if int(t['game']) != g or t['first_collect'] == '' or int(t['first_collect']) >= R:
            continue
        key = (t['side'], t['well_x'], t['well_y'], t['well_type'])
        W[key]['collects'] += int(t['collects'])
        W[key]['trips'] += 1
        W[key][t['outcome']] += 1
    print('\n== %d g%d %s  HQ us %s them %s  (wells with a first collect before r%d)' % (m, g, G['map'], hq[us], hq[th], R))
    print('side well type d_ourHQ d_theirHQ trips collects deposit death other')
    for k in sorted(W, key=lambda k: (k[0] != us, -W[k]['collects'])):
        side, x, y, ty = k
        c = W[k]
        own = us if side == us else th; opp = th if side == us else us
        print('%s (%s,%s) %s %.1f %.1f %d %d %d %d %d' % ('us' if side == us else 'them', x, y, {'1': 'Ad', '2': 'Mn', '3': 'Ex'}.get(ty, ty),
              dist(own, int(x), int(y)), dist(opp, int(x), int(y)), c['trips'], c['collects'], c['deposit'], c['death'], c['trips'] - c['deposit'] - c['death']))
