"""a1_role: our carriers' role (telemetry code_bcc & 1: 1 = mana role; carrierCode = state << 1 | mana) joined with
what they collected that turn (sa_C.csv collect_res/collect_amt), r < RMAX. Shows mana-role carriers mining adamantium.
Usage: a1_role.py TT_DIR SA_DIR RMAX match:game[,match:game...]   (TT_DIR/<match>/tele_turns.csv from --extract
--tele-turns; SA_DIR/<match>g<game><side>/sa_C.csv from a1_split.sh)"""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
TT, SA, RMAX = sys.argv[1], sys.argv[2], int(sys.argv[3])
sel = [tuple(int(x) for x in s.split(':')) for s in sys.argv[4].split(',')]
STATES = "!GCWSXRDFVTKQEYP"
print('match\tg\tmap\tcollect turns by (role, resource): amount')
for (m, g) in sel:
    G = games(m)[g]; us = G['us']
    code = {}
    with open(os.path.join(TT, str(m), 'tele_turns.csv')) as fh:
        for r in csv.DictReader(fh):
            if int(r['game']) == g and r['side'] == us and r['type'] == 'C' and int(r['round']) < RMAX and r['code_bcc'] != '':
                code[(int(r['round']), int(r['id']))] = int(r['code_bcc'])
    amt = collections.Counter(); turns = collections.Counter(); ids = collections.defaultdict(set)
    with open(os.path.join(SA, '%dg%d%s' % (m, g, us), 'sa_C.csv')) as fh:
        for r in csv.DictReader(fh):
            rd = int(r['round'])
            if rd >= RMAX or r['collect_res'] in ('', '-'):
                continue
            c = code.get((rd, int(r['id'])))
            role = '?' if c is None else ('Mn' if c & 1 else 'Ad')
            k = (role, r['collect_res'])
            amt[k] += int(r['collect_amt'] or 0); turns[k] += 1; ids[k].add(r['id'])
    print('%d\t%d\t%s\t%s' % (m, g, G['map'], '  '.join('role %s -> %s: %d kg in %d turns by %d carriers' % (k[0], k[1], amt[k], turns[k], len(ids[k])) for k in sorted(amt))))
