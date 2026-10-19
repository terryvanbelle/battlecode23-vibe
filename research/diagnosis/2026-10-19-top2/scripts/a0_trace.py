# Per-round launcher trace of one game (sa_L, both sides), rounds R0..R1: for each launcher its position, allies and
# enemies within r2 20 (self excluded), moved, attacked and hit target, and our objective code where known.
# usage: a0_trace.py MATCH GAME R0 R1
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
m, g, R0, R1 = map(int, sys.argv[1:5])
G = games_of(m)[g]
H = hqs(m, g)
print(label(G), 'us', G['us'], 'HQ', H[G['us']], '| them', G['them'], 'HQ', H[G['them']])
for side, who in ((G['us'], 'us'), (G['them'], 'them')):
    byr = collections.defaultdict(list)
    for r in sa(m, g, side, 'L', R1):
        if r['round'] >= R0: byr[r['round']].append(r)
    print(f'--- {who}')
    for rn in sorted(byr):
        cells = [f"{r['id'] % 1000:03d}@({r['x']},{r['y']}) a{r['ally_L_20']} e{r['enemy_L_20']}"
                 f"{' mv' if r['moved'] == 1 else ''}{' hit' + str(r['atk_target_type']) if r['attacked'] and r['atk_hit'] == '1' else (' fire' if r['attacked'] else '')}"
                 for r in sorted(byr[rn], key=lambda r: r['id'])]
        print(f"r{rn}: " + ' | '.join(cells))
