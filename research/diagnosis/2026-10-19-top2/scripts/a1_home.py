"""a1_home: who holds each side's home mana wells, r < RMAX. Home wells of a side = mana wells its carriers collected
from before RMAX (trips.csv) that lie nearer its own HQs than the enemy's. For each side's home wells: launcher-turns
of each side within r2 R2 of such a well (sa_L.csv), the first round an enemy launcher stood there, and the owner's
carrier deaths within r2 R2 of them (deaths.csv).
Usage: a1_home.py SA300_DIR [RMAX] [R2]"""
import sys, math
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
SA = sys.argv[1]
RMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 150
R2 = int(sys.argv[3]) if len(sys.argv) > 3 else 34

def hqs(m, g):
    h = collections.defaultdict(list)
    for r in rows(m, 'hq'):
        if int(r['game']) == g and r['round'] == '25':
            h[r['side']].append((int(r['x']), int(r['y'])))
    return h

def homewells(m, g, side, other, H):
    w = set()
    for t in rows(m, 'trips'):
        if int(t['game']) == g and t['side'] == side and t['well_type'] == '2' and t['first_collect'] and int(t['first_collect']) < RMAX:
            p = (int(t['well_x']), int(t['well_y']))
            if min(d2(p, h) for h in H[side]) < min(d2(p, h) for h in H[other]):
                w.add(p)
    return w

def near(x, y, W):
    return any(d2((x, y), p) <= R2 for p in W)

print('group\tmatch\tg\tmap\twells\tour wells: L-turns us/them, first enemy r, our C deaths\ttheir wells: L-turns us/them, first r, their C deaths')
tot = collections.defaultdict(collections.Counter)
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        G = games(m)[g]; us, th = G['us'], G['them']
        H = hqs(m, g)
        W = {us: homewells(m, g, us, th, H), th: homewells(m, g, th, us, H)}
        cnt = collections.Counter(); first = {}
        for side in (us, th):
            p = os.path.join(SA, '%dg%d%s' % (m, g, side), 'sa_L.csv')
            if not os.path.exists(p):
                break
            with open(p) as fh:
                for r in csv.DictReader(fh):
                    rd = int(r['round'])
                    if rd >= RMAX: continue
                    x, y = int(r['x']), int(r['y'])
                    for owner in (us, th):
                        if near(x, y, W[owner]):
                            cnt[(owner, side)] += 1
                            if side != owner and (owner not in first or rd < first[owner]): first[owner] = rd
        else:
            cd = collections.Counter()
            for d in rows(m, 'deaths'):
                if int(d['game']) == g and d['type'] == 'C' and int(d['round']) < RMAX and near(int(d['x']), int(d['y']), W[d['side']]):
                    cd[d['side']] += 1
            print('%s\t%d\t%d\t%s\t%s|%s\t%d/%d first %s, C dead %d\t%d/%d first %s, C dead %d' % (
                grp, m, g, G['map'], sorted(W[us]), sorted(W[th]), cnt[(us, us)], cnt[(us, th)], first.get(us, '-'), cd[us],
                cnt[(th, us)], cnt[(th, th)], first.get(th, '-'), cd[th]))
            if (m, g) != (9921, 0):
                t = tot[grp]
                t['own_us'] += cnt[(us, us)]; t['own_them'] += cnt[(us, th)]; t['their_us'] += cnt[(th, us)]; t['their_them'] += cnt[(th, th)]
                t['Cdead_us'] += cd[us]; t['Cdead_them'] += cd[th]; t['games'] += 1
print()
for k, t in tot.items():
    print(k, 'at OUR home Mn wells: launcher-turns us %d, them %d; our carriers killed there %d | at THEIR home Mn wells: us %d, them %d; their carriers killed there %d (games %d)' % (
        t['own_us'], t['own_them'], t['Cdead_us'], t['their_us'], t['their_them'], t['Cdead_them'], t['games']))
