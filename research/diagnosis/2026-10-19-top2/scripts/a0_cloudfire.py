# Turns that start with an enemy launcher within r2 16 (geometric, sa_L) and end with no attack, split by clouds: the
# shooter on a cloud, the nearest enemy launcher (near_eL_dx/dy, within r2 20) on a cloud, either, or neither. A robot
# on a cloud is invisible beyond r2 4 and a robot on a cloud sees only r2 4 (RULES 6.1/6.3); attacks need no vision.
# Also, per side, the share of in-range turns with a cloud involved that still fire (blind or tracked shots), and the
# pooled share that hit anything / hit a launcher (atk_hit).
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200

if __name__ == '__main__':
    tot = {s: collections.Counter() for s in ('us', 'them')}
    print(f'r <= {RMAX}; per game: in-range turns with a cloud involved (shooter or nearest enemy on a cloud): n, fired share; without a cloud: n, fired share')
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        M = load_map(G['map']); W = M['W']; cl = M['clouds']
        line = []
        for who, side in (('us', G['us']), ('them', G['them'])):
            c = collections.Counter()
            for r in sa(G['m'], G['g'], side, 'L', RMAX):
                if r['enemy_L_16'] <= 0: continue
                ec = r['near_eL_dx'] is not None and cl[(r['x'] + r['near_eL_dx']) + (r['y'] + r['near_eL_dy']) * W]
                cloudy = bool(r['on_cloud']) or bool(ec)
                k = 'cl' if cloudy else 'clear'
                c[k] += 1; c[k + '_fire'] += bool(r['attacked'])
                hit = bool(r['attacked']) and r['atk_hit'] == '1'
                c[k + '_hit'] += hit; c[k + '_hitL'] += hit and r['atk_target_type'] == 'L'
            for k, v in c.items(): tot[who][k] += v
            f = lambda a, b: f"{a/b:.2f}" if b else '-'
            line.append(f"{who} cloud {c['cl']} fired {f(c['cl_fire'], c['cl'])}, clear {c['clear']} fired {f(c['clear_fire'], c['clear'])}")
        print(f"{label(G)} {'W' if G['won'] else 'L'} | " + ' | '.join(line))
    for who in ('us', 'them'):
        c = tot[who]
        print(f"pooled {who}: cloud turns {c['cl']} fired {c['cl_fire']/max(1,c['cl']):.2f} hit {c['cl_hit']/max(1,c['cl']):.2f} hit a launcher {c['cl_hitL']/max(1,c['cl']):.2f}; "
              f"clear turns {c['clear']} fired {c['clear_fire']/max(1,c['clear']):.2f} hit {c['clear_hit']/max(1,c['clear']):.2f} hit a launcher {c['clear_hitL']/max(1,c['clear']):.2f}")
