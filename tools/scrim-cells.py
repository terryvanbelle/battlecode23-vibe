#!/usr/bin/env python3
"""Scrimmage cells under contest rules: each opponent gets N games on a random map from the full corpus, a random side
and a fresh engine seed. Reproducible from --rng (recorded in the run's cells file name by the caller).

    tools/scrim-cells.py --opponents tools/field.txt --games 2 --rng 7 > cells.txt
    tools/scrim-cells.py --opponents "a.b c.d" --games 4 --rng 9 --maps tools/maps.txt

Lines: "<opponent> <map> <A|B> <seed>" (the gauntlet's CELLS format). Opponents rotate so no opponent plays twice in a
row; sides are balanced per opponent (A/B alternate, first side random)."""
import argparse, os, random, sys

ap = argparse.ArgumentParser()
ap.add_argument('--opponents', required=True, help='a file with one name per line, or a space-separated list')
ap.add_argument('--games', type=int, default=2)
ap.add_argument('--rng', type=int, required=True)
ap.add_argument('--maps', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maps.txt'))
a = ap.parse_args()
opps = [l.strip() for l in open(a.opponents)] if os.path.exists(a.opponents) else a.opponents.split()
opps = [o for o in opps if o and not o.startswith('#')]
maps = [l.strip() for l in open(a.maps) if l.strip()]
rnd = random.Random(a.rng)
first = {o: rnd.choice('AB') for o in opps}
cells = []
for g in range(a.games):
    order = opps[:]
    rnd.shuffle(order)
    for o in order:
        side = first[o] if g % 2 == 0 else ('B' if first[o] == 'A' else 'A')
        cells.append(f'{o} {rnd.choice(maps)} {side} {rnd.randrange(1, 2**30)}')
sys.stdout.write('\n'.join(cells) + '\n')
