"""a1_snow: the first exchange and the snowball, from timeline.csv (every 10 rounds): launchers alive us/them at r30,
r50, r70, r100, r150; launchers lost by r50 and r100 each side; carriers lost by r100; Mn collected at r50/r100."""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
print('group\tmatch\tg\tmap\tL30\tL50\tL70\tL100\tL150\tLlost50\tLlost100\tClost100\tMn50\tMn100')
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN), ('other', [(m, g) for m in CARL for g in range(3) if (m, g) not in COLLAPSE + EARLYWIN])):
    for (m, g) in lst:
        G = games(m)[g]; us, th = G['us'], G['them']
        T = {(int(r['round']), r['side']): r for r in rows(m, 'timeline') if int(r['game']) == g}
        def v(side, rd, k):
            ks = [x for (x, s) in T if s == side and x <= rd]
            return int(f(T[(max(ks), side)][k])) if ks else 0
        def pair(rd, k): return '%d/%d' % (v(us, rd, k), v(th, rd, k))
        def lost(rd, t): return '%d/%d' % (v(us, rd, 'built_' + t) - v(us, rd, 'alive_' + t), v(th, rd, 'built_' + t) - v(th, rd, 'alive_' + t))
        print('\t'.join(str(x) for x in [grp + ('W' if G['won'] else 'L'), m, g, G['map'], pair(30, 'alive_L'), pair(50, 'alive_L'), pair(70, 'alive_L'),
              pair(100, 'alive_L'), pair(150, 'alive_L'), lost(50, 'L'), lost(100, 'L'), lost(100, 'C'), pair(50, 'coll_Mn'), pair(100, 'coll_Mn')]))
