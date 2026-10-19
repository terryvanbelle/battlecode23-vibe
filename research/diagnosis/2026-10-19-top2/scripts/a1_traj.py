"""a1_traj: per BUCKET rounds, each side's launchers (sa_L.csv, one row per launcher-turn; the last row of each launcher
in the bucket): count, median prog from own HQ, how many stand in the enemy half (prog > 0.5), the median and max
group size (1 + ally launchers within r2 20), and how many are in contact (an enemy launcher within r2 20).
Usage: a1_traj.py SA300_DIR match game [RMAX] [BUCKET]"""
import sys, math
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
SA, m, g = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
RMAX = int(sys.argv[4]) if len(sys.argv) > 4 else 200
BK = int(sys.argv[5]) if len(sys.argv) > 5 else 10
G = games(m)[g]
def load(side):
    last = {}
    with open(os.path.join(SA, '%dg%d%s' % (m, g, side), 'sa_L.csv')) as fh:
        for r in csv.DictReader(fh):
            rd = int(r['round'])
            if rd >= RMAX: continue
            b = (rd - 1) // BK
            do, de = math.sqrt(int(r['d2_own_hq'])), math.sqrt(int(r['d2_enemy_hq']))
            last[(b, r['id'])] = (do / (do + de) if do + de else .5, int(r['ally_L_20']), int(r['enemy_L_20']), int(r['x']), int(r['y']))
    out = collections.defaultdict(list)
    for (b, i), v in last.items(): out[b].append(v)
    return out
U, T = load(G['us']), load(G['them'])
print('%d g%d %s: per %d rounds; us | them: n, prog_med, in enemy half, group med/max, in contact, centroid' % (m, g, G['map'], BK))
for b in range(0, (RMAX - 1) // BK + 1):
    s = []
    for V in (U[b], T[b]):
        if not V: s.append('-'); continue
        gs = [1 + v[1] for v in V]
        s.append('%2d %.2f %2d %s/%2d %2d (%d,%d)' % (len(V), med([v[0] for v in V]), sum(v[0] > .5 for v in V), med(gs), max(gs),
                 sum(v[2] > 0 for v in V), sum(v[3] for v in V) / len(V), sum(v[4] for v in V) / len(V)))
    print('r%3d-%3d  %-34s | %s' % (b * BK + 1, b * BK + BK, s[0], s[1]))
