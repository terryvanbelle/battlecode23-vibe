# Our mana-role carriers in the opening (r <= RMAX, default 100): per-turn code from tele_turns.csv
# (Telemetry.carrierCode: state = "!GCWSXRDFVTKQEYP"[(c >> 1) & 15], mana role = c & 1) joined to sa_C positions.
# Per game: mana-role carrier turns, share in X (explore: no known mana well, Carrier.explore() goes to the map centre
# first) and F (flee); X turns within r2 100 of an enemy HQ; median prog of X turns (0 = our HQ); the map centre's prog.
import sys, os, csv, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 100
EXT = os.environ.get('A0_EXT', os.path.join(os.path.dirname(SA), 'ext'))
ST = '!GCWSXRDFVTKQEYP'


def prog(G, p):
    H = hqs(G['m'], G['g'])
    du = math.sqrt(min(d2(p, h) for h in H[G['us']])); dt = math.sqrt(min(d2(p, h) for h in H[G['them']]))
    return du / (du + dt) if du + dt else 0


if __name__ == '__main__':
    print(f'r <= {RMAX}')
    print('| game | res | mana-role turns | X share | F share | X turns within r2 100 of enemy HQ | median prog of X turns | centre prog |')
    print('|---|---|---|---|---|---|---|---|')
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        code = {}
        with open(f"{EXT}/{G['m']}/tele_turns.csv") as fh:
            for r in csv.DictReader(fh):
                if int(r['game']) != G['g'] or r['side'] != G['us'] or r['type'] != 'C' or r['code_bcc'] == '': continue
                if int(r['round']) > RMAX: continue
                code[(int(r['round']), int(r['id']))] = int(r['code_bcc'])
        EH = hqs(G['m'], G['g'])[G['them']]
        c = collections.Counter(); px = []
        for r in sa(G['m'], G['g'], G['us'], 'C', RMAX):
            v = code.get((r['round'], r['id']))
            if v is None or not (v & 1): continue
            s = ST[(v >> 1) & 15]; c['n'] += 1; c[s] += 1
            if s == 'X':
                p = (r['x'], r['y']); px.append(prog(G, p))
                c['Xnear'] += min(d2(p, h) for h in EH) <= 100
        f = lambda a: f"{a/c['n']:.2f}" if c['n'] else '-'
        cp = prog(G, (G['W'] // 2, G['H'] // 2))
        print(f"| {label(G)} | {'W' if G['won'] else 'L'} | {c['n']} | {f(c['X'])} | {f(c['F'])} | {c['Xnear']} | "
              f"{sorted(px)[len(px)//2]:.2f} | {cp:.2f} |" if px else
              f"| {label(G)} | {'W' if G['won'] else 'L'} | {c['n']} | {f(c['X'])} | {f(c['F'])} | {c['Xnear']} | - | {cp:.2f} |")
