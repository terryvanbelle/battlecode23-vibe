"""synth_v5_basics.py: basics check (CLAUDE.md rule 9) over the 47 distinct games, from robots.csv and census.csv.

Robots that never moved: max_still >= 0.9 x turns and turns >= 50 (carriers and launchers), per side, listed with
their birth tile and the map, plus whether the birth tile is in a sealed pocket (8-connected flood fill over passable
tiles from the birth tile, the HQ tiles blocked, reaches fewer than 30 tiles).
Also census: exceptions and bytecode overruns ('over') per side, summed.
Usage: python3 -I synth_v5_basics.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_common import *


def pocket(name, xy, hqs):
    m = load_map(name); W, H = m['W'], m['H']; wall = m['walls']
    seen = {xy}; st = [xy]
    while st and len(seen) < 30:
        x, y = st.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (x + dx, y + dy)
                if n in seen or not (0 <= n[0] < W and 0 <= n[1] < H) or wall[n[0] + n[1] * W] or n in hqs: continue
                seen.add(n); st.append(n)
    return len(seen) < 30


def main():
    tot = collections.Counter()
    for G in distinct():
        hqs = set(G['hqs']['A']) | set(G['hqs']['B'])
        for s in ('us', 'them'):
            c = census(G, G[s])
            tot[(s, 'exc')] += num(c['exceptions'], 0)
            tot[(s, 'over')] += num(c['over'], 0)
            for r in robots(G, G[s]):
                if r['type'] not in ('C', 'L'): continue
                t, ms = int(r['turns']), int(r['max_still'])
                if t >= 50 and ms >= 0.9 * t:
                    xy = (int(r['x_born']), int(r['y_born']))
                    sealed = pocket(G['map'], xy, hqs)
                    tot[(s, 'still')] += 1
                    tot[(s, 'sealed')] += sealed
                    print(f"{label(G)} {s:4} {r['type']} id {r['id']} born r{r['born']} at {xy} turns {t} max_still {ms} "
                          f"codes {r['codes']} sealed_pocket={sealed}")
    print('\nsummary:', {f'{a}_{b}': v for (a, b), v in sorted(tot.items())})


main()
