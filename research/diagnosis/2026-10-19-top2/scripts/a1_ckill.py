"""a1_ckill: who kills our carriers before RMAX (deaths.csv killer_type, cause), the cargo lost, and the carrier's age;
also the Ad value lost (50 per carrier) against the Mn the side collected by RMAX (timeline cum Mn, nearest row)."""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150
tot = collections.defaultdict(collections.Counter)
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        if (m, g) == (9921, 0): continue
        G = games(m)[g]
        for who, side in (('us', G['us']), ('them', G['them'])):
            t = tot[(grp, who)]
            for d in rows(m, 'deaths'):
                if int(d['game']) != g or d['side'] != side or d['type'] != 'C' or int(d['round']) >= RMAX: continue
                t['dead'] += 1; t['killer_' + (d['killer_type'] or d['cause'] or '?')] += 1
                t['cargo'] += int(f(d['cargo_Ad'])) + int(f(d['cargo_Mn'])); t['age'] += int(f(d['age']))
                t['young20'] += int(f(d['age'])) <= 20
for k in sorted(tot):
    t = tot[k]; n = max(1, t['dead'])
    print('%s %s: carriers dead before r%d %d; killers %s; cargo lost %d kg; mean age %.1f; died within 20 rounds of birth %d' % (
        k[0], k[1], RMAX, t['dead'], {kk[7:]: v for kk, v in t.items() if kk.startswith('killer_')}, t['cargo'], t['age'] / n, t['young20']))
