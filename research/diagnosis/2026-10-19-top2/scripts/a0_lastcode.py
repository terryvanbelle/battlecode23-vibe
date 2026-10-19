# Our launchers' last telemetry code before death (deaths.csv last_code, bytecode channel; decode as in the earlier
# diagnosis: mode = 'NFHMSGW!'[c & 7], objective kind = (c >> 3) & 3 (0 sighting/recall/guard, 1 island, 2 siege HQ/raid
# well/mid site, 3 centre or mending island), out = (c >> 5) & 1 (enemy fighters in vision > ours + 1)), r <= RMAX.
# Also the local counts at the dying launcher's last per-turn row (sa_L: allies and enemies within r2 20).
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200
OBJ = ['sighting', 'island', 'hq/raid/site', 'centre/mend']

if __name__ == '__main__':
    agg = {r: collections.Counter() for r in ('W', 'L')}
    loc = {r: [] for r in ('W', 'L')}
    for G in all_games():
        res = 'W' if G['won'] else 'L'
        last = {}
        for r in sa(G['m'], G['g'], G['us'], 'L', RMAX):
            last[r['id']] = r
        for d in rd(G['m'], 'deaths'):
            if int(d['game']) != G['g'] or d['side'] != G['us'] or d['type'] != 'L' or int(d['round']) > RMAX: continue
            agg[res]['n'] += 1
            if d['last_code'] != '':
                c = int(d['last_code'])
                agg[res]['obj_' + OBJ[(c >> 3) & 3]] += 1
                agg[res]['out'] += (c >> 5) & 1
                agg[res]['mode_' + 'NFHMSGW!'[c & 7]] += 1
            L = last.get(int(d['id']))
            if L: loc[res].append((L['ally_L_20'] + 1, L['enemy_L_20']))
    for res in ('L', 'W'):
        a = agg[res]; n = a['n']
        print(f"{res}: our launcher deaths r<={RMAX}: {n}; last objective " +
              ', '.join(f"{k[4:]} {a[k]} ({a[k]/n:.2f})" for k in sorted(a) if k.startswith('obj_')) +
              f"; outnumbered in vision {a['out']} ({a['out']/n:.2f}); modes " +
              ', '.join(f"{k[5:]} {a[k]}" for k in sorted(a) if k.startswith('mode_')))
        P = loc[res]
        if P:
            print(f"    last per-turn row: mean ours within r2 20 (self incl.) {sum(p[0] for p in P)/len(P):.2f}, "
                  f"theirs {sum(p[1] for p in P)/len(P):.2f}; alone (no ally within r2 20) {sum(1 for p in P if p[0]==1)}/{len(P)}; "
                  f"theirs > ours {sum(1 for p in P if p[1] > p[0])}/{len(P)}")
