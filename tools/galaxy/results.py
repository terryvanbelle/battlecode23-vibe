#!/usr/bin/env python3
"""Download finished matches from the galaxy replica and append their games to progress/games.csv (on the driver,
over the public HTTPS site; read-only on the replica). Resumable and idempotent: a (run, seq) already in the file is
never written again, so an interrupted or repeated run loses or duplicates nothing.

  python3 tools/galaxy/results.py [--games F] [--ours vibe23] [--keep DIR] [--max N] [--full] [--dry-run]

For each match in the site's match list (GET /api/compete/<ep>/match/, newest first, as the Queue page lists it;
read with the staff login `owner`, which sees every match's replay link and participants' submissions) that finished
OK!, it downloads the match's replay file from its replay_url (one file holding all the match's games), reads it
with `tools/replay-dump.sh <file> --games` (one line per game: index map winner rounds) and appends one row per game:
  run=galaxy-<match id>, seq=game number (1-based), teamA/teamB = the player_index 0/1 teams, winner A|B, rounds,
  reason='' (the replay does not carry the engine's reason text), seed='map', or 'map-rev' for the odd games of an
  alternate-order match (the engine flips HQ ownership there; team A stays team A).
Names: field teams appear under their entrant name (tools/galaxy/field-teams.tsv maps a shortened team name back),
so their rows join the earlier ones; our team appears as 'us:<package of the submission that played>' (from our
team's own submission list, logged in as our team user, ~/.bc23-galaxy-team), so each build is its own player in
tools/elo.py. A game without a winner is skipped (tools/elolib.py would count it as B).

Progress: ~/.cache/bc23-galaxy-results/state.json keeps the oldest match id that was not finished at the last run, so
a run reads only the pages above it (--full reads every page). Replays are deleted after parsing unless --keep DIR.
"""
import argparse
import csv
import fcntl
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'tools'))
from client import GATE_FILE, ApiError, Client, Session  # noqa: E402

HDR = ['run', 'seq', 'teamA', 'teamB', 'map', 'winner', 'rounds', 'reason', 'seed']   # tools/elolib.py HDR
GAMES = os.path.join(REPO, 'progress', 'games.csv')
MAPPING = os.path.join(HERE, 'field-teams.tsv')
TEAM_FILE = os.path.expanduser('~/.bc23-galaxy-team')
STATE = os.path.expanduser('~/.cache/bc23-galaxy-results/state.json')
TERMINAL = ('OK!', 'ERR', 'CAN')


def run_id(match_id):
    return f'galaxy-{match_id}'


def parse_games(text):
    """replay-dump --games output -> [(index, map, winner, rounds)]."""
    out = []
    for line in text.splitlines():
        p = line.split()
        if len(p) == 4 and p[0].isdigit() and p[3].isdigit():
            out.append((int(p[0]), p[1], p[2], int(p[3])))
    return out


def games_of(path):
    r = subprocess.run(['bash', os.path.join(REPO, 'tools', 'replay-dump.sh'), path, '--games'],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise RuntimeError(f'replay-dump failed ({r.returncode}): {r.stderr.strip()[-300:]}')
    return parse_games(r.stdout)


def entrant_names(path=MAPPING):
    """Galaxy team name -> entrant name, for the names that differ."""
    if not os.path.exists(path):
        return {}
    with open(path) as fh:
        return {r['team']: r['entrant'] for r in csv.DictReader((l for l in fh if not l.startswith('#')), delimiter='\t')
                if r['team'] != r['entrant']}


def player_name(p, ours, packages, names):
    """A participant's name in games.csv: 'us:<package>' for our team, else the entrant name."""
    if p['teamname'] == ours:
        pkg = packages.get(p.get('submission'))
        return f'us:{pkg}' if pkg else f'us:submission-{p.get("submission")}'
    return names.get(p['teamname'], p['teamname'])


def match_rows(match, games, ours, packages, names):
    """games.csv rows for one finished match (games: [(index, map, winner, rounds)]); games without a winner are
    left out. Returns (rows, problems)."""
    ps = sorted(match['participants'], key=lambda p: p['player_index'])
    a, b = (player_name(p, ours, packages, names) for p in ps)
    rows, problems = [], []
    maps = list(match.get('maps') or [])
    if sorted(g[1] for g in games) != sorted(maps):          # the replay's order is the play order
        problems.append(f'replay games {[g[1] for g in games]} vs match maps {maps}')
    wins = [sum(1 for g in games if g[2] == s) for s in 'AB']
    scores = [p.get('score') for p in ps]
    if None not in scores and wins != scores:
        problems.append(f'replay wins {wins} vs scores {scores}')
    for i, m, w, rounds in games:
        if w not in ('A', 'B'):
            problems.append(f'game {i + 1} on {m}: no winner')
            continue
        rev = bool(match.get('alternate_order')) and i % 2 == 1
        rows.append({'run': run_id(match['id']), 'seq': str(i + 1), 'teamA': a, 'teamB': b, 'map': m, 'winner': w,
                     'rounds': str(rounds), 'reason': '', 'seed': 'map-rev' if rev else 'map'})
    return rows, problems


def recorded(path):
    """{(run, seq)} already in games.csv."""
    if not os.path.exists(path):
        return set()
    with open(path) as fh:
        return {(r['run'], r['seq']) for r in csv.DictReader(fh)}


def append_rows(path, rows):
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, 'a', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=HDR, lineterminator='\n')
        if new:
            w.writeheader()
        for r in rows:
            w.writerow(r)
        fh.flush()
        os.fsync(fh.fileno())


def load_state(path=STATE):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_state(state, path=STATE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + '.tmp', 'w') as fh:
        json.dump(state, fh)
    os.replace(path + '.tmp', path)


def scan(read_page, low_water):
    """Matches newest first, page by page, down to the oldest unfinished match of the last run (low_water; 0 = all).
    read_page(n) -> {'results': [...], 'next': url|None}. Returns (matches, new low water)."""
    out, page = [], 1
    while True:
        r = read_page(page)
        ms = r.get('results', [])
        out += ms
        if not r.get('next') or not ms or min(m['id'] for m in ms) < low_water:
            break
        page += 1
    out = [m for m in out if m['id'] >= low_water]
    unfinished = [m['id'] for m in out if m['status'] not in TERMINAL]
    if unfinished:
        new_low = min(unfinished)
    elif out:
        new_low = max(m['id'] for m in out) + 1
    else:
        new_low = low_water
    return out, new_low


def team_credentials(path=TEAM_FILE):
    with open(path) as fh:
        user, pw = [l.strip() for l in fh.read().splitlines()[:2]]
    return user, pw


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--site', default=None)
    ap.add_argument('--connect', default=os.environ.get('GALAXY_CONNECT') or None)
    ap.add_argument('--games', default=GAMES)
    ap.add_argument('--ours', default='vibe23', help='our team name on the replica')
    ap.add_argument('--staff-user', default='owner', help='the superuser that lists every match (password: the gate '
                    'password file, as set by bootstrap owner)')
    ap.add_argument('--keep', help='keep the downloaded replays in this directory (<match id>.bc23)')
    ap.add_argument('--max', type=int, default=0, help='at most this many matches this run (0 = all)')
    ap.add_argument('--full', action='store_true', help='read every page, ignoring the saved progress')
    ap.add_argument('--dry-run', action='store_true', help='print the rows, write nothing')
    a = ap.parse_args(argv)
    kw = {'connect': a.connect}
    if a.site:
        kw['site'] = a.site
    c = Client(**kw)
    ep = c.episode
    lock = open(os.path.join(tempfile.gettempdir(), f'bc23-galaxy-results-{os.getuid()}.lock'), 'w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        raise SystemExit('results: another run is in progress')
    with open(GATE_FILE) as fh:
        staff = Session(c, a.staff_user, fh.readline().strip())
    state = {} if a.full else load_state()
    low = int(state.get('low_water', 0))
    ms, new_low = scan(lambda n: staff.api('GET', f'/api/compete/{ep}/match/?page={n}'), low)
    have = recorded(a.games)
    names = entrant_names()
    packages, ours_session = {}, None
    todo = [m for m in sorted(ms, key=lambda m: m['id']) if m['status'] == 'OK!' and m.get('participants')
            and not all((run_id(m['id']), str(i + 1)) in have for i in range(len(m.get('maps') or [1])))]
    if a.max:
        todo = todo[:a.max]
    added, matches, problems = 0, 0, 0
    workdir = a.keep or tempfile.mkdtemp(prefix='bc23-galaxy-replays-')
    os.makedirs(workdir, exist_ok=True)
    try:
        for m in todo:
            if any(p['teamname'] == a.ours for p in m['participants']):
                sub_ids = {p.get('submission') for p in m['participants'] if p['teamname'] == a.ours}
                if not sub_ids <= set(packages):
                    if ours_session is None:
                        ours_session = Session(c, *team_credentials())
                    for s in ours_session.pages(f'/api/compete/{ep}/submission/'):
                        packages[s['id']] = s['package']
            url = m.get('replay_url')
            if not url:
                print(f'match {m["id"]}: no replay_url; skipped')
                continue
            path = os.path.join(workdir, f'{m["id"]}.bc23')
            if not os.path.exists(path):
                data = c.request('GET', url, raw=True, timeout=600)
                with open(path + '.tmp', 'wb') as fh:
                    fh.write(data)
                os.replace(path + '.tmp', path)
            try:
                games = games_of(path)
            finally:
                if not a.keep:
                    os.remove(path)
            rows, probs = match_rows(m, games, a.ours, packages, names)
            for p in probs:
                print(f'match {m["id"]}: {p}')
            problems += bool(probs)
            rows = [r for r in rows if (r['run'], r['seq']) not in have]
            if a.dry_run:
                for r in rows:
                    print(','.join(r[h] for h in HDR))
            else:
                append_rows(a.games, rows)
            have |= {(r['run'], r['seq']) for r in rows}
            added += len(rows)
            matches += 1
    finally:
        if not a.keep:
            try:
                os.rmdir(workdir)
            except OSError:
                pass
    if not a.dry_run and not (a.max and len(todo) == a.max):
        save_state({'low_water': new_low})
    unfinished = sum(1 for m in ms if m['status'] not in TERMINAL)
    print(f'results: {added} games from {matches} matches appended to {a.games}'
          f'{" (dry run)" if a.dry_run else ""}; {unfinished} matches not finished yet; {problems} with warnings')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except ApiError as e:
        raise SystemExit(f'results: {e}')
