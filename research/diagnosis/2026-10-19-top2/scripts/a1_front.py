"""a1_front: would our home mana wells ever turn hot? For each of our mana wells with a first collect before RMAX
(trips.csv), Carrier.frontGate(homeD2, enemyD2) of src/c_kx0 (homeD2 > C.HOT_HOME_D2 = 64 and 100*homeD2 >= 36*enemyD2),
evaluated with the true HQs (hq.csv; the bot uses its enemy HQ candidates, which equal the true HQs once the symmetry
is decided), the trips there, how they ended, and our carrier deaths within r2 34 of the well before RMAX (deaths.csv).
Usage: a1_front.py [RMAX]"""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150
print('group\tmatch\tg\tmap\twell\thomeD2\tenemyD2\tfront\ttrips\tdeposit\tdeath\tC dead r2<=34')
tot = collections.Counter()
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        if (m, g) == (9921, 0): continue
        G = games(m)[g]; us, th = G['us'], G['them']
        hq = collections.defaultdict(list)
        for r in rows(m, 'hq'):
            if int(r['game']) == g and r['round'] == '25':
                hq[r['side']].append((int(r['x']), int(r['y'])))
        W = collections.defaultdict(collections.Counter)
        for t in rows(m, 'trips'):
            if int(t['game']) == g and t['side'] == us and t['first_collect'] != '' and int(t['first_collect']) < RMAX and t['well_type'] == '2':
                k = (int(t['well_x']), int(t['well_y'])); W[k]['trips'] += 1; W[k][t['outcome']] += 1
        dead = [(int(d['x']), int(d['y'])) for d in rows(m, 'deaths') if int(d['game']) == g and d['side'] == us and d['type'] == 'C' and int(d['round']) < RMAX]
        for k, c in sorted(W.items(), key=lambda kv: -kv[1]['trips']):
            hd = min(d2(k, h) for h in hq[us]); ed = min(d2(k, h) for h in hq[th])
            fr = hd > 64 and 100 * hd >= 36 * ed
            nd = sum(1 for p in dead if d2(p, k) <= 34)
            print('%s\t%d\t%d\t%s\t(%d,%d)\t%d\t%d\t%s\t%d\t%d\t%d\t%d' % (grp, m, g, G['map'], k[0], k[1], hd, ed, 'front' if fr else 'home', c['trips'], c['deposit'], c['death'], nd))
            key = (grp, 'front' if fr else 'home')
            tot[key + ('wells',)] += 1; tot[key + ('trips',)] += c['trips']; tot[key + ('deposit',)] += c['deposit']; tot[key + ('death',)] += c['death']; tot[key + ('near',)] += nd
print()
for grp in ('collapse', 'earlywin'):
    for kind in ('home', 'front'):
        k = (grp, kind)
        print('%s %s wells %d: trips %d, deposits %d, deaths %d, our carrier deaths within r2 34 %d' % (grp, kind, tot[k + ('wells',)], tot[k + ('trips',)], tot[k + ('deposit',)], tot[k + ('death',)], tot[k + ('near',)]))
