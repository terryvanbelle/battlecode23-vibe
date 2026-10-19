"""a1_eng: engagements before r250 (engagements.csv), from our side: where (prog_us: 0 = our HQ), size at start/peak,
how many launchers joined, kills, who won. Per game for COLLAPSE and EARLYWIN, plus group aggregates."""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 250
verbose = '-v' in sys.argv

def eng_rows(m, g, us):
    out = []
    for r in rows(m, 'engagements'):
        if int(r['game']) != g or int(r['r0']) >= RMAX:
            continue
        th = 'B' if us == 'A' else 'A'
        p = f(r['prog0'], float('nan'))
        e = dict(r0=int(r['r0']), r1=int(r['r1']), x=int(r['x0']), y=int(r['y0']),
                 prog_us=(p if us == 'A' else 1 - p), n_us=int(r['n' + us + '0']), n_th=int(r['n' + th + '0']),
                 pk_us=int(r['peak' + us]), pk_th=int(r['peak' + th]), j_us=int(r['join' + us]), j_th=int(r['join' + th]),
                 k_us=int(r['kills_by_' + us]), k_th=int(r['kills_by_' + th]), first=('us' if r['first_hit'] == us else 'them' if r['first_hit'] == th else '-'),
                 res=('won' if r['result'] == us else 'lost' if r['result'] == th else r['result']),
                 fh=r['fh_att_type'] + '>' + r['fh_vic_type'] + ':' + r['fh_how'])
        out.append(e)
    return out

agg = {}
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    A = collections.Counter()
    for (m, g) in lst:
        G = games(m)[g]
        es = eng_rows(m, g, G['us'])
        if verbose:
            print('\n== %d g%d %s (%s) us=%s' % (m, g, G['map'], grp, G['us']))
            print('r0-r1 prog_us n0 us/th peak us/th join us/th kills us/th first result fh')
            for e in es[:14]:
                print('%d-%d %.2f %d/%d %d/%d %d/%d %d/%d %s %s %s' % (e['r0'], e['r1'], e['prog_us'], e['n_us'], e['n_th'], e['pk_us'], e['pk_th'],
                      e['j_us'], e['j_th'], e['k_us'], e['k_th'], e['first'], e['res'], e['fh']))
        if (m, g) == (9921, 0):      # identical replay of 9888 g0: listed, not counted twice
            continue
        for e in es:
            A['n'] += 1
            A['won'] += e['res'] == 'won'; A['lost'] += e['res'] == 'lost'
            A['k_us'] += e['k_us']; A['k_th'] += e['k_th']
            A['j_us'] += e['j_us']; A['j_th'] += e['j_th']
            A['pk_us'] += e['pk_us']; A['pk_th'] += e['pk_th']
            A['first_th'] += e['first'] == 'them'
            A['behind0'] += e['n_us'] < e['n_th']
            A['ours_half'] += e['prog_us'] < 0.5
            A['k_th_ours_half'] += e['k_th'] if e['prog_us'] < 0.5 else 0
            A['k_us_ours_half'] += e['k_us'] if e['prog_us'] < 0.5 else 0
            A['n_us0_zero'] += e['n_us'] == 0
            A['fh_vic_C'] += e['fh'].startswith('L>C')
    A['games'] = len([x for x in lst if x != (9921, 0)])
    agg[grp] = A
print('\nby group, engagements with r0 <', RMAX)
keys = ['games', 'n', 'won', 'lost', 'first_th', 'behind0', 'n_us0_zero', 'ours_half', 'k_us', 'k_th', 'k_us_ours_half', 'k_th_ours_half', 'pk_us', 'pk_th', 'j_us', 'j_th', 'fh_vic_C']
print('group\t' + '\t'.join(keys))
for grp, A in agg.items():
    print(grp + '\t' + '\t'.join(str(A[k]) for k in keys))
