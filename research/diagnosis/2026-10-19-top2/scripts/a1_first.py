"""a1_first: the first large engagement of each game (the first with joinUs + joinThem >= 8, r0 < 200): deaths by
type and side inside it (deaths.csv eng id), its span, and the launchers alive on each side at r0 and r1 (timeline)."""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
MINJ = 8
print('group\tmatch\tg\tmap\tr0-r1\tprog_us\tn0 us/th\tjoin us/th\tL alive@r0 us/th\tdeadL us/th\tdeadC us/th\tL alive@r1+10 us/th')
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        G = games(m)[g]; us = G['us']; th = G['them']
        T = {(int(r['round']), r['side']): r for r in rows(m, 'timeline') if int(r['game']) == g}
        def alive(side, rnd):
            k = max(x for (x, s) in T if s == side and x <= max(10, rnd))
            return int(T[(k, side)]['alive_L'])
        E = [r for r in rows(m, 'engagements') if int(r['game']) == g and int(r['r0']) < 200
             and int(r['join' + us]) + int(r['join' + th]) >= MINJ]
        if not E:
            print(grp, m, g, G['map'], 'none'); continue
        e = E[0]
        D = collections.Counter()
        for d in rows(m, 'deaths'):
            if int(d['game']) == g and d['eng'] == e['eng']:
                D[(d['side'], d['type'])] += 1
        p = f(e['prog0']); p = p if us == 'A' else 1 - p
        r0, r1 = int(e['r0']), int(e['r1'])
        print('%s\t%d\t%d\t%s\t%d-%d\t%.2f\t%s/%s\t%s/%s\t%d/%d\t%d/%d\t%d/%d\t%d/%d' % (
            grp, m, g, G['map'], r0, r1, p, e['n' + us + '0'], e['n' + th + '0'], e['join' + us], e['join' + th],
            alive(us, r0), alive(th, r0), D[(us, 'L')], D[(th, 'L')], D[(us, 'C')], D[(th, 'C')], alive(us, r1 + 10), alive(th, r1 + 10)))
