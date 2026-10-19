"""a1_alive: carriers and launchers alive (us/them) and Mn collected so far (us/them) every 25 rounds to RMAX, from
timeline.csv; shows whether our carriers collapse before our launchers. Usage: a1_alive.py [RMAX]"""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 250
rs = list(range(25, RMAX + 1, 25))
print('group\tmatch\tg\tmap\tseries\t' + '\t'.join('r%d' % r for r in rs))
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        if (m, g) == (9921, 0): continue
        G = games(m)[g]; us, th = G['us'], G['them']
        T = {(int(r['round']), r['side']): r for r in rows(m, 'timeline') if int(r['game']) == g}
        def at(side, rd, col):
            ks = [k for (k, s) in T if s == side and k <= rd]
            return T[(max(ks), side)][col] if ks else '-'
        for lab, col in (('C alive', 'alive_C'), ('L alive', 'alive_L'), ('Mn coll', 'coll_Mn')):
            print('%s\t%d\t%d\t%s\t%s\t' % (grp, m, g, G['map'], lab) + '\t'.join('%s/%s' % (at(us, r, col), at(th, r, col)) for r in rs))
