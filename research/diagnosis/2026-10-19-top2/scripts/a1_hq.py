"""a1_hq: per game, our and their HQ rows (hq.csv, 25-round buckets) up to r200: summed over each side's HQs the
launchers and carriers built in the bucket, the Mn and Ad banked at its end, enemy pressure (pressure34) and our HQ
build-stop codes (t = carrier withheld under threat)."""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200
TOT = collections.defaultdict(collections.Counter)
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        if (m, g) == (9921, 0):
            continue
        G = games(m)[g]; us = G['us']; th = G['them']
        B = collections.defaultdict(lambda: collections.Counter())
        codes = collections.defaultdict(collections.Counter)
        for r in rows(m, 'hq'):
            if int(r['game']) != g or int(r['round']) > RMAX:
                continue
            k = (int(r['round']), r['side'])
            for c in ('built_L', 'built_C', 'bank_Mn', 'bank_Ad', 'pressure34'):
                B[k][c] += int(r[c])
            if r['side'] == us and r['codes']:
                for kv in r['codes'].split(';'):
                    a, b = kv.split('=')
                    codes[int(r['round'])][a] += int(b)
        print('\n== %s %d g%d %s' % (grp, m, g, G['map']))
        print('r   bL us/th  bC us/th  bankMn us/th  bankAd us/th  press34 us/th  our codes')
        for rd in sorted({k[0] for k in B}):
            u, t = B[(rd, us)], B[(rd, th)]
            T = TOT[grp]
            if rd > 25:
                T['bL_us'] += u['built_L']; T['bL_th'] += t['built_L']; T['bC_us'] += u['built_C']; T['bC_th'] += t['built_C']
            T['press_us'] += u['pressure34']; T['press_th'] += t['pressure34']; T['t_codes'] += codes[rd]['t']
            if rd == RMAX: T['bankAd_us'] += u['bank_Ad']; T['bankAd_th'] += t['bank_Ad']; T['bankMn_us'] += u['bank_Mn']; T['bankMn_th'] += t['bank_Mn']
            print('%3d  %2d/%2d  %2d/%2d  %4d/%4d  %4d/%4d  %4d/%4d  %s' % (rd, u['built_L'], t['built_L'], u['built_C'], t['built_C'],
                  u['bank_Mn'], t['bank_Mn'], u['bank_Ad'], t['bank_Ad'], u['pressure34'], t['pressure34'],
                  ' '.join('%s=%d' % kv for kv in sorted(codes[rd].items()))))
print('\ntotals r26-r%d (built), r1-r%d (pressure34 sums, our t codes), banks at r%d' % (RMAX, RMAX, RMAX))
for grp, T in TOT.items():
    print('%s: launchers built us %d them %d; carriers built us %d them %d; pressure34 on our HQs %d, on theirs %d; our HQ turns with a carrier withheld under threat (t) %d; bank Ad us %d them %d, bank Mn us %d them %d' % (
        grp, T['bL_us'], T['bL_th'], T['bC_us'], T['bC_th'], T['press_us'], T['press_th'], T['t_codes'], T['bankAd_us'], T['bankAd_th'], T['bankMn_us'], T['bankMn_th']))
