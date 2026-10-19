"""a1_frogad: Frog (9888 g0) mana-role carriers mining adamantium. For each of our carriers that collected Ad before RMAX
while its telemetry role bit said mana (code_bcc & 1): its birth round, role bit at birth and at its first Ad collect
(any role change in between), turns spent in state X (explore) and G before that collect, the well, and its trips.
Usage: a1_frogad.py TT_DIR SA300_DIR [RMAX] [match] [game]"""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
TT, SA = sys.argv[1], sys.argv[2]
RMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 150
m = int(sys.argv[4]) if len(sys.argv) > 4 else 9888
g = int(sys.argv[5]) if len(sys.argv) > 5 else 0
G = games(m)[g]; us = G['us']
ST = "!GCWSXRDFVTKQEYP"
code = collections.defaultdict(dict)
with open(os.path.join(TT, str(m), 'tele_turns.csv')) as fh:
    for r in csv.DictReader(fh):
        if int(r['game']) == g and r['side'] == us and r['type'] == 'C' and int(r['round']) < RMAX and r['code_bcc'] != '':
            code[int(r['id'])][int(r['round'])] = int(r['code_bcc'])
col = collections.defaultdict(list)
with open(os.path.join(SA, '%dg%d%s' % (m, g, us), 'sa_C.csv')) as fh:
    for r in csv.DictReader(fh):
        if r['collect_res'] not in ('', '-') and int(r['round']) < RMAX:
            col[int(r['id'])].append((int(r['round']), r['collect_res'], int(r['x']), int(r['y'])))
born = {int(r['id']): int(r['born']) for r in rows(m, 'robots') if int(r['game']) == g and r['side'] == us and r['type'] == 'C'}
print('id\tborn\trole@birth\trole@firstAd\trole changes\tX turns before\tG turns before\tfirst Ad collect r\tat\tAd collects\tMn collects')
for i in sorted(col):
    ad = [c for c in col[i] if c[1] in ('Ad', 'ADAMANTIUM', '1')]
    if not ad: continue
    r0 = ad[0][0]
    cs = code.get(i, {})
    if not cs: continue
    if not (cs.get(r0, 0) & 1): continue
    rounds = sorted(cs)
    roles = [cs[r] & 1 for r in rounds]
    ch = sum(1 for a, b in zip(roles, roles[1:]) if a != b)
    xb = sum(1 for r in rounds if r < r0 and ST[(cs[r] >> 1) & 15] == 'X')
    gb = sum(1 for r in rounds if r < r0 and ST[(cs[r] >> 1) & 15] == 'G')
    print('%d\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%s\t%d\t%d' % (i, born.get(i, '?'), 'Mn' if roles[0] else 'Ad', 'Mn' if cs[r0] & 1 else 'Ad', ch, xb, gb, r0,
          '(%d,%d)' % (ad[0][2], ad[0][3]), len(ad), sum(1 for c in col[i] if c[1] not in ('Ad', 'ADAMANTIUM', '1'))))
