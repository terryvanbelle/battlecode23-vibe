"""a1_cexp: carrier exposure per side, r < RMAX (sa_C.csv): carrier-turns, turns with an enemy launcher within r2 20,
carriers that died before RMAX and how many separate exposure episodes (a turn exposed after one or more unexposed
turns) each dead carrier had; for our side, the telemetry state of the exposed turns (tele_turns code_bcc >> 1).
Usage: a1_cexp.py SA300_DIR TT_DIR [RMAX]"""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
SA, TT = sys.argv[1], sys.argv[2]
RMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 150
STATES = "!GCWSXRDFVTKQEYP"
tot = collections.defaultdict(collections.Counter)
print('group\tmatch\tg\tmap\twho\tC-turns\texposed\tdead\tepisodes/dead med\tour exposed-turn states')
for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
    for (m, g) in lst:
        if (m, g) == (9921, 0): continue
        G = games(m)[g]
        dead = {int(d['id']): int(d['round']) for d in rows(m, 'deaths') if int(d['game']) == g and d['type'] == 'C' and int(d['round']) < RMAX}
        code = {}
        ttp = os.path.join(TT, str(m), 'tele_turns.csv')
        if os.path.exists(ttp):
            with open(ttp) as fh:
                for r in csv.DictReader(fh):
                    if int(r['game']) == g and r['side'] == G['us'] and r['type'] == 'C' and int(r['round']) < RMAX and r['code_bcc']:
                        code[(int(r['round']), int(r['id']))] = int(r['code_bcc'])
        for who, side in (('us', G['us']), ('them', G['them'])):
            p = os.path.join(SA, '%dg%d%s' % (m, g, side), 'sa_C.csv')
            if not os.path.exists(p): continue
            c = collections.Counter(); seq = collections.defaultdict(list); st = collections.Counter()
            with open(p) as fh:
                for r in csv.DictReader(fh):
                    rd = int(r['round'])
                    if rd >= RMAX: continue
                    e = int(r['enemy_L_20']) > 0
                    c['turns'] += 1; c['exp'] += e
                    seq[int(r['id'])].append((rd, e))
                    if e and who == 'us':
                        k = code.get((rd, int(r['id'])))
                        st[STATES[(k >> 1) & 15] if k is not None else '?'] += 1
            eps = []
            for i, s in seq.items():
                if i not in dead: continue
                s.sort(); n = 0; prev = False
                for rd, e in s:
                    if e and not prev: n += 1
                    prev = e
                eps.append(n)
            sd = sum(1 for i in dead if any(True for _ in [0]) and i in seq)
            print('%s\t%d\t%d\t%s\t%s\t%d\t%d\t%d\t%s\t%s' % (grp, m, g, G['map'], who, c['turns'], c['exp'], len(eps), med(eps) if eps else '-',
                  ' '.join('%s%d' % kv for kv in st.most_common(6))))
            t = tot[(grp, who)]; t['turns'] += c['turns']; t['exp'] += c['exp']; t['dead'] += len(eps); t['eps'] += sum(eps)
            t.update({'st_' + k: v for k, v in st.items()})
print()
for k, t in tot.items():
    sts = {kk[3:]: v for kk, v in t.items() if kk.startswith('st_')}
    print(k, 'carrier-turns %d exposed %d (%.3f) dead %d, exposure episodes per dead carrier %.1f; states %s' % (
        t['turns'], t['exp'], t['exp'] / max(1, t['turns']), t['dead'], t['eps'] / max(1, t['dead']), sts))
