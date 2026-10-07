#!/usr/bin/env python3
"""galaxy-lite CLI: the private Battlecode 2023 ladder replica (design: research/prior/GALAXY.md 6.4; guide:
docs/replica/README.md). Runs on battlecode-dev; data in $REPLICA_HOME (default ~/replica).

  tools/replica.py init [--maps-file F] [--enforce-rules]       create the DB, episode bc23 and its maps
  tools/replica.py config [key=value ...]                       show or set episode settings
  tools/replica.py add-team NAME [--package P] [--classdir D | --source S] [--status R|S|X|O] [--no-snapshot]
  tools/replica.py submit TEAM [--package P] (--classdir D | --source S) [--verify] [--snapshot|--no-snapshot]
  tools/replica.py seed-field [--limit N | --names a,b] [--no-baseline]
  tools/replica.py request BY TO [--ranked] [--order ?|+|-] [--maps m1,m2,m3]
  tools/replica.py requests [--status P] | accept ID | reject ID
  tools/replica.py autoscrim [--best-of 3]
  tools/replica.py run-worker [--slots 4] [--until-empty] [--max-jobs N] [--timeout-per-game S]
  tools/replica.py serve [--port 8023]                          JSON API on 127.0.0.1
  tools/replica.py ratings | history TEAM | match ID | matches [--team T] [--status S] [--limit N]
  tools/replica.py wait [--timeout S] [IDS...] | status | export-games [--out F] [--all]
  tools/replica.py requeue ID | cancel ID | pump | reap
Team names: our builds are us:<package> (classes from build/classes/<package>, snapshotted into the data dir);
benchmarks use their manifest name (bc23-benchmarks/manifest.tsv: name, package, classdir, repo, commit).
"""
import argparse
import json
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from replica import api, db, matchmaking, rating, worker  # noqa: E402

BENCH_ROOT = os.path.expanduser(os.environ.get('BENCH_ROOT', '~/projects/vibe/bc23-benchmarks'))
CLASSES = os.environ.get('CLASSES', os.path.join(db.REPO, 'build', 'classes'))


def manifest():
    f = os.path.join(BENCH_ROOT, 'manifest.tsv')
    rows = {}
    if os.path.exists(f):
        with open(f) as fh:
            hdr = fh.readline().rstrip('\n').split('\t')
            for line in fh:
                r = dict(zip(hdr, line.rstrip('\n').split('\t')))
                rows.setdefault(r['name'], r)
    return rows


def resolve(name, package=None, classdir=None, source=None):
    """(package, classdir, source) for a team name: us:<pkg> -> build/classes; a manifest name -> its row."""
    if classdir or source:
        if not package:
            package = name[3:] if name.startswith('us:') else None
        if not package:
            raise SystemExit(f'--package is required for {name}')
        return package, classdir, source
    if name.startswith('us:'):
        package = package or name[3:]
        return package, CLASSES, None
    row = manifest().get(name)
    if row is None:
        raise SystemExit(f'{name}: not us:<package> and not in {BENCH_ROOT}/manifest.tsv; give --classdir/--source')
    return package or row['package'], row['classdir'], None


def out(obj, as_json):
    if as_json:
        print(json.dumps(obj, indent=1))
        return True
    return False


def ensure_init(conn):
    db.get_episode(conn)   # raises with a hint when 'init' was not run


# ---------------------------------------------------------------- commands
def cmd_init(a, conn):
    maps = db.read_maps_file(a.maps_file) if a.maps_file else None
    ep = db.init_episode(conn, maps=maps)
    if a.enforce_rules:
        ep = db.set_episode(conn, enforce_rules=1)
    n = conn.execute('SELECT COUNT(*) FROM map WHERE episode=? AND is_public=1', (db.EPISODE,)).fetchone()[0]
    print(f'replica at {db.home()}: episode {ep["name_short"]}, {n} public maps, enforce_rules={ep["enforce_rules"]}')


def cmd_config(a, conn):
    kw = {}
    for kv in a.settings:
        k, _, v = kv.partition('=')
        kw[k] = int(v) if v.lstrip('-').isdigit() else v
    ep = db.set_episode(conn, **kw) if kw else db.get_episode(conn)
    for k in ep.keys():
        print(f'{k} = {ep[k]}')


def add_team(conn, name, package=None, classdir=None, source=None, status='R', snapshot=None, verify=False,
             quiet=False):
    package, classdir, source = resolve(name, package, classdir, source)
    try:
        tid = db.get_team(conn, name)['id']
        created = False
    except LookupError:
        tid = db.create_team(conn, name, status=status)
        created = True
    sid = None
    if created:
        sid = worker.submit(conn, tid, package, prebuilt_classes=classdir if not source else None, source=source,
                            snapshot=snapshot, verify=verify)
    if not quiet:
        s = conn.execute('SELECT * FROM submission WHERE id=?', (sid,)).fetchone() if sid else None
        what = (f'submission {sid} {s["status"]} accepted={s["accepted"]} {s["binary_path"] or s["source_path"]}'
                if s else 'exists; no new submission (use submit)')
        print(f'team {tid} {name}: {what}')
    return tid, sid


def cmd_add_team(a, conn):
    ensure_init(conn)
    add_team(conn, a.name, a.package, a.classdir, a.source, a.status, a.snapshot, a.verify)


def cmd_submit(a, conn):
    ensure_init(conn)
    package, classdir, source = resolve(a.team, a.package, a.classdir, a.source)
    sid = worker.submit(conn, a.team, package, prebuilt_classes=None if source else classdir, source=source,
                        snapshot=a.snapshot, verify=a.verify, description=a.description or '')
    s = conn.execute('SELECT * FROM submission WHERE id=?', (sid,)).fetchone()
    print(f'submission {sid} for {a.team}: {s["status"]} accepted={s["accepted"]} '
          f'{s["binary_path"] or s["source_path"]}')


def cmd_seed_field(a, conn):
    ensure_init(conn)
    with open(os.path.join(db.TOOLS, 'field.txt')) as fh:
        field = [l.strip() for l in fh if l.strip() and not l.startswith('#')]
    if a.names:
        want = [n.strip() for n in a.names.split(',') if n.strip()]
        missing = [n for n in want if n not in field]
        if missing:
            raise SystemExit(f'not in tools/field.txt: {missing}')
        field = want
    elif a.limit is not None:
        field = field[:a.limit]
    man = manifest()
    if not a.no_baseline:
        if os.path.isfile(os.path.join(CLASSES, 'examplefuncsplayer', 'RobotPlayer.class')):
            add_team(conn, 'us:examplefuncsplayer')
        else:
            add_team(conn, 'us:examplefuncsplayer', source=os.path.join(db.REPO, 'src'))
    for name in field:
        if name not in man:
            print(f'!! {name}: not in manifest; skipped', file=sys.stderr)
            continue
        add_team(conn, name)


def cmd_request(a, conn):
    ensure_init(conn)
    maps = [m for m in (a.maps or '').split(',') if m]
    try:
        rid, st, mid = matchmaking.create_request(conn, requested_by=a.by, requested_to=a.to, is_ranked=a.ranked,
                                                  player_order=a.order, map_names=maps)
    except matchmaking.RequestError as e:
        raise SystemExit(f'refused ({e.http}): {e}')
    print(f'request {rid}: status {st}' + (f', match {mid} queued' if mid else ''))


def cmd_requests(a, conn):
    for r in api.list_requests(conn, status=a.status):
        print(f'{r["id"]:5d} {r["status"]} {"ranked" if r["is_ranked"] else "unranked"} {r["requested_by_name"]} -> '
              f'{r["requested_to_name"]} order {r["player_order"]} maps {",".join(r["maps"])} match {r["match"]}')


def cmd_accept(a, conn):
    print('matches', matchmaking.accept(conn, [a.id]))


def cmd_reject(a, conn):
    matchmaking.reject(conn, [a.id])
    print('rejected', a.id)


def cmd_autoscrim(a, conn):
    ensure_init(conn)
    ms = matchmaking.autoscrim(conn, best_of=a.best_of)
    teams = len(matchmaking.autoscrim_teams(conn))
    print(f'autoscrim: {len(ms)} matches for {teams} teams' + (f' (ids {ms[0]}-{ms[-1]})' if ms else ''))


def cmd_run_worker(a, conn):
    ensure_init(conn)
    worker.setup_logging()
    w = worker.Worker(slots=a.slots, poll=a.poll, timeout_per_game=a.timeout_per_game, until_empty=a.until_empty,
                      max_jobs=a.max_jobs)

    def stop(signum, frame):
        worker.log.info('signal %d: stopping (running engines are interrupted and requeued)', signum)
        w.stop.set()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    w.run()


def cmd_serve(a, conn):
    api.serve(a.host, a.port)


def fmt_rec(r):
    return f'{r["wins"]}-{r["losses"]}-{r["ties"]}'


def cmd_ratings(a, conn):
    rows = api.ratings_table(conn)
    if out(rows, a.json):
        return
    print(f'{"rank":>4} {"team":<40} {"rating":>8} {"mean":>8} {"n":>3} {"matches W-L-T":>13} {"games W-L":>9}')
    for r in rows:
        print(f'{r["rank"]:>4} {r["name"]:<40} {r["value"]:>8.1f} {r["mean"]:>8.1f} {r["n"]:>3} '
              f'{fmt_rec(r["ranked_record"]):>13} {r["games"]["won"]:>4}-{r["games"]["lost"]:<4}')


def cmd_history(a, conn):
    tid = db.get_team(conn, a.team)['id']
    h = api.historical_rating(conn, tid)
    ms = api.list_matches(conn, team_id=tid, page_size=a.limit)
    if out({'historical_rating': h, 'matches': ms, 'record': api.scrimmaging_record(conn, tid)}, a.json):
        return
    print(f'{a.team}: rating history (ranked, in match-creation order)')
    for r in h['team_rating']['rating_history']:
        print(f'  match {r["match"]:5d} {r["timestamp"][:19]}  value {r["rating"]:8.1f}  mean {r["mean"]:8.1f}  '
              f'n {r["n"]}')
    print(f'recent matches ({ms["count"]} total):')
    for m in ms['results']:
        print('  ' + match_line(m, tid))


def match_line(m, tid=None):
    ps = m['participants']
    names = ' vs '.join(f'{p["teamname"]}' for p in ps)
    sc = '-'.join('?' if p['score'] is None else str(p['score']) for p in ps)
    deltas = ' '.join(f'{p["teamname"]}:{p["old_rating"]:.0f}->{p["rating"]:.0f}' for p in ps
                      if p['rating'] is not None and p['old_rating'] is not None)
    return (f'match {m["id"]:5d} {m["status"]} {"R" if m["is_ranked"] else "U"} {names} {sc} '
            f'[{",".join(m["maps"])}] {deltas}')


def cmd_match(a, conn):
    m = conn.execute('SELECT * FROM match WHERE id=?', (a.id,)).fetchone()
    if m is None:
        raise SystemExit(f'no match {a.id}')
    d = api.match_json(conn, m, with_logs=a.logs)
    if out(d, a.json):
        return
    print(match_line(d))
    print(f'  created {d["created"]}  finished {d["finished"]}  source {d["source"]}  failures {d["num_failures"]}'
          f'  alternate_order {d["alternate_order"]}')
    print(f'  replay {d["replay_path"]}')
    for g in d['games']:
        print(f'  game {g["idx"] + 1}: {g["map"]:<16} A={g["team_a"]} B={g["team_b"]} '
              f'{"(spawns reversed) " if g["reversed"] else ""}winner {g["winner"]} ({g["winner_name"]}) '
              f'round {g["round"]}: {g["reason"]}')
    if a.logs:
        print(d['logs'])


def cmd_matches(a, conn):
    tid = db.get_team(conn, a.team)['id'] if a.team else None
    ms = api.list_matches(conn, team_id=tid, status=a.status, page_size=a.limit)
    if out(ms, a.json):
        return
    for m in ms['results']:
        print(match_line(m))
    print(f'({ms["count"]} matches)')


def cmd_wait(a, conn):
    t0, last = time.time(), None
    while True:
        if a.ids:
            q = ','.join('?' * len(a.ids))
            left = conn.execute(f"SELECT COUNT(*) FROM match WHERE id IN ({q}) AND status NOT IN ('OK!','ERR','CAN')",
                                a.ids).fetchone()[0]
        else:
            left = sum(conn.execute(f"SELECT COUNT(*) FROM {t} WHERE status IN ('NEW','QUE','RUN','TRY')"
                                    ).fetchone()[0] for t in ('match', 'submission'))
        c = db.status_counts(conn, 'match')
        line = f'{time.strftime("%H:%M:%S")} matches {" ".join(f"{k}={v}" for k, v in sorted(c.items()))}'
        if line[9:] != last:
            print(line, flush=True)
            last = line[9:]
        if left == 0:
            return
        if a.timeout and time.time() - t0 > a.timeout:
            raise SystemExit(f'wait: timed out with {left} jobs unfinished')
        time.sleep(a.poll)


def cmd_status(a, conn):
    s = api.queue_status(conn)
    if out(s, a.json):
        return
    print(f'home {s["home"]}: {s["teams"]} teams, {s["games"]} games ({s["games_unexported"]} not exported), '
          f'{s["participations_unrated"]} participations awaiting a rating')
    print('matches:     ' + ' '.join(f'{k}={v}' for k, v in sorted(s['matches'].items())))
    print('submissions: ' + ' '.join(f'{k}={v}' for k, v in sorted(s['submissions'].items())))
    for r in s['running']:
        print(f'  running match {r["id"]} {" vs ".join(r["teams"])} on {r["worker"]} since {r["claimed_at"][:19]}')


def cmd_export(a, conn):
    n = api.export_games(conn, a.out, a.all)
    print(f'export-games: {n} rows -> {a.out or api.GAMES_CSV}')


def cmd_requeue(a, conn):
    print('requeued' if db.requeue(conn, a.id) else 'not requeued (COMPLETED or missing)', a.id)


def cmd_cancel(a, conn):
    db.cancel(conn, [a.id])
    rating.pump(conn)
    print('cancelled', a.id)


def cmd_pump(a, conn):
    print('finalized', rating.pump(conn), 'participations')


def cmd_reap(a, conn):
    print(worker.reap_stale(conn, a.timeout_per_game))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('init')
    s.add_argument('--maps-file')
    s.add_argument('--enforce-rules', action='store_true')
    s.set_defaults(fn=cmd_init)
    s = sub.add_parser('config')
    s.add_argument('settings', nargs='*')
    s.set_defaults(fn=cmd_config)
    for name, fn in (('add-team', cmd_add_team), ('submit', cmd_submit)):
        s = sub.add_parser(name)
        s.add_argument('name' if name == 'add-team' else 'team')
        s.add_argument('--package')
        g = s.add_mutually_exclusive_group()
        g.add_argument('--classdir', help='prebuilt class dir holding <package>/RobotPlayer.class')
        g.add_argument('--source', help='source dir (holding <package>/) or .zip, compiled by the worker')
        s.add_argument('--verify', action='store_true', help='run the engine Verifier on prebuilt classes first')
        s.add_argument('--snapshot', dest='snapshot', action='store_true', default=None)
        s.add_argument('--no-snapshot', dest='snapshot', action='store_false')
        if name == 'add-team':
            s.add_argument('--status', default='R', choices=db.TeamStatus.ALL)
        else:
            s.add_argument('--description')
        s.set_defaults(fn=fn)
    s = sub.add_parser('seed-field')
    g = s.add_mutually_exclusive_group()
    g.add_argument('--limit', type=int)
    g.add_argument('--names')
    s.add_argument('--no-baseline', action='store_true')
    s.set_defaults(fn=cmd_seed_field)
    s = sub.add_parser('request')
    s.add_argument('by')
    s.add_argument('to')
    s.add_argument('--ranked', action='store_true')
    s.add_argument('--order', default='?', choices=db.PlayerOrder.ALL)
    s.add_argument('--maps')
    s.set_defaults(fn=cmd_request)
    s = sub.add_parser('requests')
    s.add_argument('--status')
    s.set_defaults(fn=cmd_requests)
    for name, fn in (('accept', cmd_accept), ('reject', cmd_reject), ('requeue', cmd_requeue),
                     ('cancel', cmd_cancel)):
        s = sub.add_parser(name)
        s.add_argument('id', type=int)
        s.set_defaults(fn=fn)
    s = sub.add_parser('autoscrim')
    s.add_argument('--best-of', type=int)
    s.set_defaults(fn=cmd_autoscrim)
    s = sub.add_parser('run-worker')
    s.add_argument('--slots', type=int, default=4)
    s.add_argument('--poll', type=float, default=2.0)
    s.add_argument('--timeout-per-game', type=int, default=worker.GAME_TIMEOUT)
    s.add_argument('--until-empty', action='store_true', help='exit when no job is queued or running')
    s.add_argument('--max-jobs', type=int)
    s.set_defaults(fn=cmd_run_worker)
    s = sub.add_parser('serve')
    s.add_argument('--host', default='127.0.0.1')
    s.add_argument('--port', type=int, default=8023)
    s.set_defaults(fn=cmd_serve)
    s = sub.add_parser('ratings')
    s.add_argument('--json', action='store_true')
    s.set_defaults(fn=cmd_ratings)
    s = sub.add_parser('history')
    s.add_argument('team')
    s.add_argument('--limit', type=int, default=20)
    s.add_argument('--json', action='store_true')
    s.set_defaults(fn=cmd_history)
    s = sub.add_parser('match')
    s.add_argument('id', type=int)
    s.add_argument('--logs', action='store_true')
    s.add_argument('--json', action='store_true')
    s.set_defaults(fn=cmd_match)
    s = sub.add_parser('matches')
    s.add_argument('--team')
    s.add_argument('--status')
    s.add_argument('--limit', type=int, default=20)
    s.add_argument('--json', action='store_true')
    s.set_defaults(fn=cmd_matches)
    s = sub.add_parser('wait')
    s.add_argument('ids', nargs='*', type=int)
    s.add_argument('--timeout', type=float, default=0)
    s.add_argument('--poll', type=float, default=10)
    s.set_defaults(fn=cmd_wait)
    s = sub.add_parser('status')
    s.add_argument('--json', action='store_true')
    s.set_defaults(fn=cmd_status)
    s = sub.add_parser('export-games')
    s.add_argument('--out')
    s.add_argument('--all', action='store_true', help='every completed game, ignoring and keeping export marks')
    s.set_defaults(fn=cmd_export)
    sub.add_parser('pump').set_defaults(fn=cmd_pump)
    s = sub.add_parser('reap')
    s.add_argument('--timeout-per-game', type=int, default=worker.GAME_TIMEOUT)
    s.set_defaults(fn=cmd_reap)
    a = p.parse_args(argv)
    db.ensure_dirs()
    conn = db.connect()
    try:
        a.fn(a, conn)
    except (LookupError, ValueError) as e:
        raise SystemExit(f'replica: {e}')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
