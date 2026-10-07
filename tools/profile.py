#!/usr/bin/env python3
"""Per-team tactical profile from a run's census (both teams' rows): how each bot spends and fights, side by side.

    tools/profile.py <run> [<run> ...] [--cols C100,L100,...] [--us-only]

Means over the run's games for each team (our build = the 'bot' / 'us:*' / snapshot rows, shown as 'us').
Default columns: win share, length, robots alive at r100/r250 (C, L), mana and adamantium collected by r100/r250,
robots built, anchors built/placed and the first anchor's round, island-rounds held, launcher exposure and damage
per contact round. This is the tactics view the rules allow for external bots: what they do in games, never their code."""
import argparse, csv, collections, os, sys

DEFAULT = ('won,rounds,C100,L100,cMn100,cAd100,C250,L250,cMn250,cAd250,built_C,built_L,built_A,'
           'anchors_built,anchors_placed,first_anchor,island_rounds,exposed,dmg/contact')


def value(row, col):
    v = row.get(col)
    if v not in (None, ''):
        try:
            return float(v)
        except ValueError:
            return None
    for tok in (row.get('micro_L') or '').split():
        k, _, x = tok.partition('=')
        if k == col:
            return float(x)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runs', nargs='+')
    ap.add_argument('--cols', default=DEFAULT)
    ap.add_argument('--us-only', action='store_true')
    a = ap.parse_args()
    cols = a.cols.split(',')
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    games = collections.Counter()
    for run in a.runs:
        for r in csv.DictReader(open(os.path.join(run, 'census.csv'))):
            ours = r['side'] == r['cell_side']
            who = 'us' if ours else r['team']
            if a.us_only and not ours:
                continue
            games[who] += 1
            for c in cols:
                v = value(r, c)
                if v is not None:
                    agg[who][c].append(v)
    w = max([len(t) for t in agg] + [4])
    print(f'{"team":{w}s} {"n":>4s} ' + ' '.join(f'{c[:12]:>12s}' for c in cols))
    order = sorted(agg, key=lambda t: (t != 'us', t))
    for t in order:
        cells = []
        for c in cols:
            v = agg[t][c]
            if not v:
                cells.append(f'{"":>12s}')
            else:
                m = sum(v) / len(v)
                cells.append(f'{m:12.3f}' if abs(m) < 10 and m != int(m) else f'{m:12.0f}')
        print(f'{t:{w}s} {games[t]:4d} ' + ' '.join(cells))
    return 0


if __name__ == '__main__':
    sys.exit(main())
