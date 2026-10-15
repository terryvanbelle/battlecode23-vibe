#!/usr/bin/env python3
"""Behavioural-cloning rows of one opponent from our panel replays (ReplayDump --sa). Standard library only.

    tools/sa_extract.py OPPONENT [--panels GLOB] [--out DIR] [--no-ours] [--plain]

OPPONENT is a substring of results.csv's `opponent` column (e.g. jmerle). For every panel matching GLOB (default
gauntlet/*-panel-*), the games against that opponent are grouped by match; the replay is the panel's
replays/<match>.bc23, else matches/<match>/<match>.bc23 (panels whose replay is gone are skipped and listed). The
opponent's team is the side other than `bot_side`. Output (DIR default research/clone/<OPPONENT>):
    sa_L.csv.gz, sa_HQ.csv.gz, sa_C.csv.gz             the opponent's launcher / HQ / carrier turns
    ours_sa_L.csv.gz, ours_sa_HQ.csv.gz, ours_sa_C.csv.gz   our side of the same games (unless --no-ours)
with leading columns panel,opponent then ReplayDump's match,game,map,... (column meanings: ReplayDump.sa()).
gzip by default because one panel's match is ~100 MB of rows per side; --plain writes .csv. One java at a time.
"""
import argparse
import csv
import glob
import os
import re
import subprocess
import sys
from collections import OrderedDict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMP = os.path.join(REPO, 'tools', 'replay-dump.sh')
KINDS = ('sa_L.csv', 'sa_HQ.csv', 'sa_C.csv')


def find_replay(panel_dir, match, repo=REPO):
    """The match's replay file, or None."""
    for p in (os.path.join(panel_dir, 'replays', f'{match}.bc23'), os.path.join(repo, 'matches', str(match), f'{match}.bc23')):
        if os.path.isfile(p):
            return p
    return None


def panel_games(results_csv, opponent):
    """{(match, bot_side): (opponent name, [game indices])} of the rows whose opponent contains `opponent`."""
    out = OrderedDict()
    with open(results_csv, newline='') as f:
        for row in csv.DictReader(f):
            if opponent not in row.get('opponent', ''):
                continue
            key = (row['match'], row['bot_side'])
            name, games = out.setdefault(key, (row['opponent'], []))
            g = int(row['game'])
            if g not in games:
                games.append(g)
    return out


def other(side):
    return 'B' if side == 'A' else 'A'


def run_sa(replay, side, games, match, out_dir, prefix, panel, opponent, gz):
    """One ReplayDump --sa run appending to out_dir/<prefix>sa_*.csv[.gz]; returns its per-game stdout lines."""
    clean = lambda s: re.sub(r'[,\n]', '_', s)
    cmd = ['bash', DUMP, replay, '--sa', '--team', side, '--out', out_dir, '--games', ','.join(map(str, sorted(games))),
           '--match', str(match), '--append', '--file-prefix', prefix, '--pre-hdr', 'panel,opponent',
           '--pre-val', f'{clean(panel)},{clean(opponent)}']
    if gz:
        cmd.append('--gzip')
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f'replay-dump failed on {replay}: {p.stderr.strip()[-500:]}')
    return [l for l in p.stdout.splitlines() if ' team=' in l]


def parse_line(line):
    """'0 Map team=B name=X rows_L=1 rows_HQ=2 rows_C=3 ...' -> dict."""
    f = line.split()
    d = {'game': int(f[0]), 'map': f[1]}
    for kv in f[2:]:
        if '=' in kv:
            k, v = kv.split('=', 1)
            d[k] = v
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('opponent')
    ap.add_argument('--panels', default=os.path.join(REPO, 'gauntlet', '*-panel-*'))
    ap.add_argument('--out')
    ap.add_argument('--no-ours', action='store_true')
    ap.add_argument('--plain', action='store_true', help='write .csv instead of .csv.gz')
    a = ap.parse_args(argv)
    out = a.out or os.path.join(REPO, 'research', 'clone', re.sub(r'[^A-Za-z0-9_.-]', '_', a.opponent))
    os.makedirs(out, exist_ok=True)
    gz = not a.plain
    ext = '' if a.plain else '.gz'
    prefixes = [''] + ([] if a.no_ours else ['ours_'])
    tmp = os.path.join(out, '.tmp')
    os.makedirs(tmp, exist_ok=True)
    for pre in prefixes:
        for k in KINDS:
            p = os.path.join(tmp, pre + k + ext)
            if os.path.exists(p):
                os.remove(p)
    tot = {pre: [0, 0, 0] for pre in prefixes}
    n_games, missing, mismatched = 0, [], []
    for pd in sorted(glob.glob(a.panels)):
        rc = os.path.join(pd, 'results.csv')
        if not os.path.isfile(rc):
            continue
        panel = os.path.basename(pd.rstrip('/'))
        for (match, bot_side), (opp_name, games) in panel_games(rc, a.opponent).items():
            replay = find_replay(pd, match)
            if replay is None:
                missing.append(f'{panel}:{match}')
                continue
            for pre, side in (('', other(bot_side)), ('ours_', bot_side)):
                if pre not in prefixes:
                    continue
                lines = run_sa(replay, side, games, match, tmp, pre, panel, opp_name, gz)
                for d in map(parse_line, lines):
                    if (pre == '') != (a.opponent in d.get('name', '')):
                        mismatched.append(f'{panel}:{match}:{d["game"]}:{pre or "opp"}:{d.get("name")}')
                    for i, k in enumerate(('rows_L', 'rows_HQ', 'rows_C')):
                        tot[pre][i] += int(d.get(k, 0))
                if pre == '':
                    n_games += len(lines)
            print(f'{panel} match {match} games {len(games)} done', flush=True)
    for pre in prefixes:
        for k in KINDS:
            src = os.path.join(tmp, pre + k + ext)
            if os.path.exists(src):
                os.replace(src, os.path.join(out, pre + k + ext))
    os.rmdir(tmp) if not os.listdir(tmp) else None
    print(f'games {n_games}  out {out}')
    for pre in prefixes:
        print(f'{pre or "opponent_"}rows L={tot[pre][0]} HQ={tot[pre][1]} C={tot[pre][2]}')
    if missing:
        print(f'replay missing ({len(missing)}): {" ".join(missing)}')
    if mismatched:
        print(f'WARNING team-name mismatch ({len(mismatched)}): {" ".join(mismatched[:10])}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
