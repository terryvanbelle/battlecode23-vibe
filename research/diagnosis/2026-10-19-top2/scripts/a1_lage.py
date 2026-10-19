"""a1_lage: launcher deaths before RMAX per side (deaths.csv): age at death, share dying within 30 rounds of birth,
spawn kills, distance from own nearest HQ at death, and hits taken before death (engagement codes not needed)."""
import sys, math
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200
tot = collections.defaultdict(list)
print('group\tmatch\tg\tmap\twho\tL_dead\tage_med\tyoung30\tspawnkill\tdHQ_med\twithin8')
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        G = games(m)[g]
        hq = collections.defaultdict(list)
        for r in rows(m, 'hq'):
            if int(r['game']) == g and r['round'] == '25':
                hq[r['side']].append((int(r['x']), int(r['y'])))
        D = [d for d in rows(m, 'deaths') if int(d['game']) == g and int(d['round']) < RMAX and d['type'] == 'L']
        for who, side in (('us', G['us']), ('them', G['them'])):
            L = [d for d in D if d['side'] == side]
            ages = [int(d['age']) for d in L]
            dh = [min(math.sqrt(d2((int(d['x']), int(d['y'])), h)) for h in hq[side]) for d in L]
            y30 = sum(a <= 30 for a in ages); sk = sum(d['spawn_kill'] == '1' for d in L); w8 = sum(x <= 8 for x in dh)
            print('%s\t%d\t%d\t%s\t%s\t%d\t%s\t%d\t%d\t%s\t%d' % (grp, m, g, G['map'], who, len(L), med(ages) if ages else '-', y30, sk,
                  '%.1f' % med(dh) if dh else '-', w8))
            if (m, g) != (9921, 0):
                tot[(grp, who)].append((len(L), y30, sk, w8, ages))
print()
for k, v in tot.items():
    n = sum(x[0] for x in v)
    allages = [a for x in v for a in x[4]]
    print(k, 'L_dead', n, 'young30', sum(x[1] for x in v), 'spawnkill', sum(x[2] for x in v), 'within8', sum(x[3] for x in v), 'age_med', med(allages))
