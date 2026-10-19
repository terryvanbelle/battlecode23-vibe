"""a1_feed: do we feed launchers in one at a time? For each launcher born before RMAX (robots.csv), its first contact turn
(sa_L.csv, an enemy launcher within r2 20 at the start of the turn): its age then, its own side's launchers within r2 20
counting itself (ally_L_20 + 1) against the enemy's (enemy_L_20), whether it was alone, outnumbered (enemy > own), and
whether it died within 20 rounds of that contact (robots.csv died). Cohorts: the opening wave (born r <= 2) and the later
launchers (born r > 2: the reinforcements, LAUNCHER_BATCH = 1 each). Usage: a1_feed.py SA300_DIR [RMAX]"""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
SA = sys.argv[1]
RMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 200
tot = collections.defaultdict(collections.Counter)
print('group\tmatch\tg\tmap\twho\tcohort\tn\tcontact\tage_med\town_med\tenemy_med\talone\toutnum\tdied20\tdHQ_med')
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        if (m, g) == (9921, 0): continue          # identical replay of 9888 g0
        G = games(m)[g]
        rob = {int(r['id']): r for r in rows(m, 'robots') if int(r['game']) == g and r['type'] == 'L'}
        for who, side in (('us', G['us']), ('them', G['them'])):
            p = os.path.join(SA, '%dg%d%s' % (m, g, side), 'sa_L.csv')
            if not os.path.exists(p): continue
            first = {}
            with open(p) as fh:
                for r in csv.DictReader(fh):
                    i = int(r['id'])
                    if i in first or int(r['enemy_L_20']) == 0: continue
                    first[i] = (int(r['round']), int(r['ally_L_20']) + 1, int(r['enemy_L_20']), int(r['d2_own_hq']) ** 0.5)
            for coh in ('wave', 'later'):
                ids = [i for i, r in rob.items() if r['side'] == side and int(r['born']) < RMAX and
                       ((int(r['born']) <= 2) == (coh == 'wave'))]
                c = collections.Counter(); ages = []; own = []; en = []; dhs = []
                for i in ids:
                    c['n'] += 1
                    if i not in first: continue
                    rd, a, e, dh = first[i]
                    if rd >= RMAX: continue
                    dhs.append(dh)
                    c['contact'] += 1
                    ages.append(rd - int(rob[i]['born'])); own.append(a); en.append(e)
                    c['alone'] += a == 1; c['outnum'] += e > a
                    dd = rob[i]['died']
                    c['died20'] += dd != '' and int(dd) - rd <= 20
                print('%s\t%d\t%d\t%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%d\t%d\t%d\t%.1f' % (grp, m, g, G['map'], who, coh, c['n'], c['contact'],
                      med(ages), med(own), med(en), c['alone'], c['outnum'], c['died20'], med(dhs)))
                t = tot[(grp, who, coh)]; t.update(c)
                t['own_sum'] += sum(own); t['en_sum'] += sum(en); t['age_sum'] += sum(ages); t['dh_sum'] += sum(dhs); t['dh8'] += sum(1 for x in dhs if x <= 8)
print()
for k in sorted(tot):
    t = tot[k]; n = max(1, t['contact'])
    print('%s %s %s: launchers %d, first contact before r%d %d; at first contact own %.2f vs enemy %.2f (means), alone %.2f, '
          'outnumbered %.2f, died within 20 rounds %.2f; mean age %.1f, mean tiles from own HQ %.1f, within 8 tiles %.2f' % (k[0], k[1], k[2], t['n'], RMAX, t['contact'], t['own_sum'] / n,
          t['en_sum'] / n, t['alone'] / n, t['outnum'] / n, t['died20'] / n, t['age_sum'] / n, t['dh_sum'] / n, t['dh8'] / n))
