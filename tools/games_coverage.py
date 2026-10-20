#!/usr/bin/env python3
"""Every replica match our gauntlet runs downloaded (gauntlet/*/results.csv, column match) must be in
progress/games.csv as run galaxy-<match>; a missing one silently moves the BT ratings (panel review 2026-10-20: c_gx1's
3-7 match 10350 was absent, rank 5 shown as rank 2). tools/progress-refresh.sh runs this after results.py; on a miss it
runs results.py --full once and checks again.
   tools/games_coverage.py [--games F] [--root DIR]   # exit 1 and list the missing match ids"""
import argparse, csv, glob, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def missing(games, root):
    """{match id: results.csv path} of the run matches absent from games.csv."""
    with open(games, newline='') as fh:
        have = {r['run'] for r in csv.DictReader(fh)}
    out = {}
    for f in sorted(glob.glob(os.path.join(root, '*', 'results.csv'))):
        with open(f, newline='') as fh:
            for r in csv.DictReader(fh):
                m = (r.get('match') or '').strip()
                if m and 'galaxy-' + m not in have:
                    out.setdefault(m, f)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--games', default=os.path.join(REPO, 'progress', 'games.csv'))
    ap.add_argument('--root', default=os.path.join(REPO, 'gauntlet'))
    a = ap.parse_args()
    miss = missing(a.games, a.root)
    for m, f in sorted(miss.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
        print(f'missing galaxy-{m} ({os.path.relpath(f, REPO)})')
    print(f'games coverage: {len(miss)} run matches missing from {os.path.relpath(a.games, REPO)}')
    return 1 if miss else 0


if __name__ == '__main__':
    sys.exit(main())
