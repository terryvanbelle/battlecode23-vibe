"""a1_stuck: carriers born before RMAX that stood still for >= STILL consecutive rounds (robots.csv max_still), per game
and side, with their state-token counts (robots.csv codes) and how they died. Usage: a1_stuck.py [RMAX] [STILL]"""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200
STILL = int(sys.argv[2]) if len(sys.argv) > 2 else 50
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        if (m, g) == (9921, 0): continue
        G = games(m)[g]
        for who, side in (('us', G['us']), ('them', G['them'])):
            n = 0; out = []
            for r in rows(m, 'robots'):
                if int(r['game']) != g or r['side'] != side or r['type'] != 'C' or int(r['born']) >= RMAX: continue
                n += 1
                if int(r['max_still'] or 0) >= STILL:
                    out.append('#%s born r%s at (%s,%s) still %s died r%s by %s [%s]' % (r['id'], r['born'], r['x_born'], r['y_born'], r['max_still'], r['died'] or '-', r['cause'] or '-', r['codes']))
            print('%s\t%d\t%d\t%s\t%s\tcarriers %d, still >= %d rounds: %d%s' % (grp, m, g, G['map'], who, n, STILL, len(out), ('\n\t' + '\n\t'.join(out)) if out else ''))
