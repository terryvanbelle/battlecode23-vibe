#!/usr/bin/env python3
"""Record scrimmage results into progress/games.csv (one row per game; idempotent per run id).

    tools/scrim-record.py gauntlet/<run> --label <build>     # a gauntlet block: BOT played as 'us:<build>'

Columns: run,seq,teamA,teamB,map,winner,rounds,reason,seed  (reason is a code, see REASONS; seed '' or 'map' = the map
file's own seed). Coin-flip games (engine Math.random, unseeded) are recorded with reason COIN and excluded from paired
counts by the analysis tools. Self-play between our own packages never enters games.csv (it grades nothing).
Then tools/elo.py refreshes progress/ELO.md and progress/elo.png."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elolib

REASONS, reason_code = elolib.REASONS, elolib.reason_code


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--label', default='')
    a = ap.parse_args()
    run = os.path.basename(a.run.rstrip('/'))
    src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
    ours = set(os.listdir(src_dir)) if os.path.isdir(src_dir) else set()
    if any(r['run'] == run for r in elolib.load()):
        print('already recorded', run)
        return 0
    new = []
    for i, line in enumerate(open(os.path.join(a.run, 'results.csv'))):
        if line.startswith('opponent,'):
            continue
        f = line.rstrip('\n').split(',')
        if len(f) < 7 or f[5] not in ('win', 'loss'):
            continue
        opp, m, side, w, rnd, res, reason = f[:7]
        if opp in ours:
            print(f'refused: {run} plays {opp}, one of our packages; self-play never enters games.csv')
            return 3
        us = 'us:' + (a.label or 'bot')
        A, B = (us, opp) if side == 'A' else (opp, us)
        seed = f[7] if len(f) > 7 else ''
        new.append(dict(run=run, seq=i, teamA=A, teamB=B, map=m, winner=w, rounds=rnd, reason=reason_code(reason), seed=seed))
    elolib.append(new)
    print(f'recorded {len(new)} games from {run}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
