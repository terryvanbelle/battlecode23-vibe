"""a1_cdeath: carrier deaths before RMAX per side (deaths.csv): count, distance to own nearest HQ (tiles), prog from
own HQ, last state token, cargo lost, distinct killers. Also launcher deaths: prog from own HQ."""
import sys, math
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200
print('group\tmatch\tg\tmap\twho\tC_dead\tC_dHQ_med\tC_prog_med\tC_tokens\tC_killers\tL_dead\tL_prog_med\tL_in_enemy_half')
tot = collections.defaultdict(collections.Counter)
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        G = games(m)[g]
        hq = collections.defaultdict(list)
        for r in rows(m, 'hq'):
            if int(r['game']) == g and r['round'] == '25':
                hq[r['side']].append((int(r['x']), int(r['y'])))
        D = [d for d in rows(m, 'deaths') if int(d['game']) == g and int(d['round']) < RMAX]
        for who, side in (('us', G['us']), ('them', G['them'])):
            C = [d for d in D if d['side'] == side and d['type'] == 'C']
            L = [d for d in D if d['side'] == side and d['type'] == 'L']
            def progo(d):
                p = f(d['prog'], float('nan'))
                return p if side == 'A' else 1 - p
            dh = [min(math.sqrt(d2((int(d['x']), int(d['y'])), h)) for h in hq[side]) for d in C]
            tok = collections.Counter(d['last_token'] for d in C)
            kil = len({d['killer_id'] for d in C})
            lp = [progo(d) for d in L]
            print('%s\t%d\t%d\t%s\t%s\t%d\t%.1f\t%.2f\t%s\t%d\t%d\t%.2f\t%d' % (grp, m, g, G['map'], who, len(C), med(dh) if dh else float('nan'),
                  med([progo(d) for d in C]) if C else float('nan'), ' '.join('%s%d' % kv for kv in tok.most_common(4)), kil, len(L),
                  med(lp) if lp else float('nan'), sum(p > 0.5 for p in lp)))
            if (m, g) != (9921, 0):
                t = tot[(grp, who)]
                t['C'] += len(C); t['L'] += len(L); t['L_enemy_half'] += sum(p > 0.5 for p in lp)
                t['C_within8'] += sum(x <= 8 for x in dh); t['games'] += 1
                for k, v in tok.items():
                    t['tok_' + k] += v
print()
for k, t in tot.items():
    print(k, dict(t))
