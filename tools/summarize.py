#!/usr/bin/env python3
"""Summarise a gauntlet results.csv: overall, per opponent (with side split), unknown/dud counts, end reasons.

    tools/summarize.py <results.csv> [bot-name]
"""
import csv, sys
from collections import Counter, defaultdict


def summarize(rows, bot='bot'):
    out = []
    n = len(rows)
    w = sum(r['bot_result'] == 'win' for r in rows)
    out.append(f"bot={bot} games={n} wins={w} ({100.0 * w / n if n else 0:.1f}%)")
    per = defaultdict(lambda: Counter())
    for r in rows:
        per[r['opponent']][(r['bot_side'], r['bot_result'])] += 1
    for o in sorted(per):
        c = per[o]
        t = sum(c.values())
        wins = c[('A', 'win')] + c[('B', 'win')]
        out.append(f"  vs {o:44s} {wins:3d}/{t:<3d} ({100.0 * wins / t:5.1f}%)  asA={c[('A', 'win')]} asB={c[('B', 'win')]}")
    res = Counter(r['bot_result'] for r in rows)
    out.append(f"unknown: {res['unknown']}  duds: {res['dud']}")
    reasons = Counter(r['reason'] for r in rows)
    out.append('reasons: ' + '; '.join(f'{k} x{v}' for k, v in reasons.most_common()))
    return '\n'.join(out)


if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        rows = list(csv.DictReader(f))
    print(summarize(rows, sys.argv[2] if len(sys.argv) > 2 else 'bot'))
