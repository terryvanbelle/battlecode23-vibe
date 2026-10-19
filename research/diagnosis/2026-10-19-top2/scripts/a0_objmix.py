# Our launchers' per-turn telemetry code (bytecode-channel code, tele_turns.csv from
# tools/replay-dump.sh --tele-turns into $EXT/<m>/tele_turns.csv), r <= RMAX (default 200): code = mode | obj << 3 | out << 5
# (Telemetry.launcherCode; mode 'NFHMSGW!'[c & 7], obj 0 sighting/recall/guard, 1 enemy island, 2 HQ/raid/site,
# 3 centre/mend; out = more enemy fighters than allies + 1 in vision). Shares of launcher turns per objective kind and
# per mode, and the out share within each objective kind, per game and pooled over losses and wins (turn-weighted).
# Rows with an empty code (no code that turn) are counted apart.
import sys, os, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200
EXT = os.environ.get('A0_EXT', os.path.join(os.path.dirname(SA), 'ext'))
MODES = 'NFHMSGW!'
OBJ = ('sight', 'island', 'hq/site', 'centre')


def mix(G):
    c = collections.Counter()
    with open(f"{EXT}/{G['m']}/tele_turns.csv") as fh:
        for r in csv.DictReader(fh):
            if int(r['game']) != G['g'] or r['side'] != G['us'] or r['type'] != 'L': continue
            rn = int(r['round'])
            if rn > RMAX: continue
            if r['code_bcc'] == '': c['nocode'] += 1; continue
            v = int(r['code_bcc']); o = (v >> 3) & 3; out = (v >> 5) & 1
            c['n'] += 1; c['o' + str(o)] += 1; c['m' + MODES[v & 7]] += 1; c['out'] += out; c[f'o{o}out'] += out
    return c


if __name__ == '__main__':
    f = lambda a, b: f"{a/b:.2f}" if b else '-'
    print(f'r <= {RMAX}; our launcher turns by objective kind (share), out share within kind, and mode share')
    print('| game | res | turns | ' + ' | '.join(OBJ) + ' | out in sight / hq-site | march M | fight F | hold H | stand S |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|')
    agg = {r: collections.Counter() for r in 'WL'}
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        c = mix(G); res = 'W' if G['won'] else 'L'; agg[res].update(c)
        print(f"| {label(G)} | {res} | {c['n']} | " + ' | '.join(f(c['o' + str(i)], c['n']) for i in range(4))
              + f" | {f(c['o0out'], c['o0'])} / {f(c['o2out'], c['o2'])} | {f(c['mM'], c['n'])} | {f(c['mF'], c['n'])} | {f(c['mH'], c['n'])} | {f(c['mS'], c['n'])} |")
    for res in 'LW':
        c = agg[res]
        print(f"{res} pooled: turns {c['n']}; " + ', '.join(f"{OBJ[i]} {f(c['o' + str(i)], c['n'])}" for i in range(4))
              + f"; out within sight {f(c['o0out'], c['o0'])}, within hq/site {f(c['o2out'], c['o2'])}; "
              + ', '.join(f"{m} {f(c['m' + m], c['n'])}" for m in MODES if c['m' + m]) + f"; rows without a code {c['nocode']}")
