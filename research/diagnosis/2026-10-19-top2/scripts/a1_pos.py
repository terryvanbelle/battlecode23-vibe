"""a1_pos: launcher positions and grouping per side from the per-turn --sa dumps (sa_L.csv), r < RMAX.
prog = sqrt(d2_own_hq) / (sqrt(d2_own_hq) + sqrt(d2_enemy_hq)) (0 = at own HQ). Contact = an enemy launcher within
r2 20. Group = 1 + ally launchers within r2 20. Outnumbered = enemy_L_20 > ally_L_20 + 1.
Usage: a1_pos.py SA_DIR [RMAX]   (SA_DIR holds <match>g<game><side>/sa_L.csv, from a1_split.sh)"""
import sys, math
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
SA = sys.argv[1]
RMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 150
csv.field_size_limit(10 ** 8)

def load(m, side, g):
    p = os.path.join(SA, '%dg%d%s' % (m, g, side), 'sa_L.csv')
    out = []
    with open(p) as fh:
        for r in csv.DictReader(fh):
            if int(r['game']) != g:
                continue
            rd = int(r['round'])
            if rd >= RMAX:
                continue
            do, de = int(r['d2_own_hq']), int(r['d2_enemy_hq'])
            a, b = math.sqrt(max(do, 0)), math.sqrt(max(de, 0))
            out.append(dict(round=rd, id=int(r['id']), prog=a / (a + b) if a + b > 0 else 0.5, aL=int(r['ally_L_20']),
                            eL=int(r['enemy_L_20']), e16=int(r['enemy_L_16']), att=int(r['attacked'] or 0),
                            hit=r['atk_hit'] == '1', tt=r['atk_target_type'], d2s=r['atk_d2_start']))
    return out

def summ(R):
    n = len(R)
    if n == 0:
        return {}
    c = [r for r in R if r['eL'] > 0]
    s = dict(turns=n, prog_med=med([r['prog'] for r in R]), enemy_half=sum(r['prog'] > 0.5 for r in R) / n,
             contact=len(c), grp=sum(1 + r['aL'] for r in c) / max(1, len(c)), enemies=sum(r['eL'] for r in c) / max(1, len(c)),
             outnum=sum(r['eL'] > r['aL'] + 1 for r in c) / max(1, len(c)), alone=sum(r['aL'] == 0 for r in c) / max(1, len(c)),
             hitsL=sum(r['att'] and r['hit'] and r['tt'] == 'L' for r in R), hitsC=sum(r['att'] and r['hit'] and r['tt'] == 'C' for r in R),
             contact_prog=med([r['prog'] for r in c]) if c else float('nan'))
    return s

if __name__ == '__main__':
    keys = ['turns', 'prog_med', 'enemy_half', 'contact', 'contact_prog', 'grp', 'enemies', 'outnum', 'alone', 'hitsL', 'hitsC']
    print('group\tmatch\tg\tmap\tside\t' + '\t'.join(keys))
    tot = collections.defaultdict(lambda: collections.defaultdict(list))
    for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
        for (m, g) in lst:
            G = games(m)[g]
            for who, side in (('us', G['us']), ('them', G['them'])):
                try:
                    s = summ(load(m, side, g))
                except FileNotFoundError:
                    continue
                if not s:
                    continue
                if (m, g) != (9921, 0):
                    for k in keys:
                        tot[(grp, who)][k].append(s[k])
                print('%s\t%d\t%d\t%s\t%s\t' % (grp, m, g, G['map'], who) + '\t'.join(('%.2f' % s[k]) if isinstance(s[k], float) else str(s[k]) for k in keys))
    print('\nmedians over games (9921 g0 excluded as a duplicate of 9888 g0)')
    for k2, d in tot.items():
        print('%s %s\t' % k2 + '\t'.join('%s=%.2f' % (k, med(d[k])) for k in keys))
