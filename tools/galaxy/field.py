#!/usr/bin/env python3
"""The practice field on the galaxy replica: the public 2023 bots (tools/field.txt) as ordinary contestant teams, and
their own scrimmage activity in spare VM cycles. Runs ON the VM as the operator (it needs the field accounts file and
the benchmark tree); every action goes through the site's public API as the field team's own user, as a contestant's
browser would (tools/galaxy/client.py). Standard library only.

  python3 tools/galaxy/field.py plan [--out F]       entrant -> team name, user, package, source dir, zip mode
                                                     (writes the mapping, default tools/galaxy/field-teams.tsv)
  python3 tools/galaxy/field.py seed [--only NAME]   register each user, log in, create the team, set the profile to
                                                     auto-accept ranked and unranked requests, upload the bot
                                                     (idempotent: a step already done is skipped)
  python3 tools/galaxy/field.py wait [--timeout S]   wait for every field submission to compile; list failures with a
                                                     compile-log tail (step lines and error lines only)
  python3 tools/galaxy/field.py status               one line per field team: id, rating, submission status
  python3 tools/galaxy/field.py activity [--poll S] [--max-backlog N] [--band K] [--once]
        field teams request RANKED scrimmages (3 random maps, shuffled order: galaxy's only ranked form) against the
        teams rated just above them, one request per poll, only while the match queue holds fewer than N waiting
        matches, so a request from our own team is never stuck behind field traffic. Galaxy enforces its own limits
        (the episode's hourly ranked limit per team, requests plus matches; ranked only upward; at most 3 active
        against one team); a refused request is logged and the team rests (429: one hour, 409: ten minutes).

Bots are packaged blind (CLAUDE.md rule 3: their source is never read): the zip holds the .java files of the package
directory under <package>/ (galaxy's layout), found by file name only (the directory named like the package that
holds RobotPlayer.java; a package whose files sit at the repository root takes them from there). Each candidate zip
is compiled locally first with all compiler output discarded; if the package alone does not compile (it needs a helper
package), the zip holds every top-level directory of the package's source root instead. Compile logs printed by
`wait` keep only saturn's step lines and javac's error lines, never a source excerpt.

Accounts: one user per team, named like the team; e-mail <user>@field.bc23-replica.invalid (e-mail is off). The
generated passwords live only in ~/.bc23-galaxy-field/accounts.json on the VM (directory 700, file 600); they are
never printed. Team names are the entrant names (printable ASCII, at most 32 characters); a longer name is shortened
by SHORT_NAMES and the mapping file records it.
"""
import argparse
import csv
import json
import os
import random
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from client import ApiError, Client, Session, multipart, rankings  # noqa: E402

BENCH_ROOT = os.environ.get('BENCH_ROOT', os.path.expanduser('~/projects/vibe/bc23-benchmarks'))
FIELD_FILE = os.path.join(REPO, 'tools', 'field.txt')
MAPPING = os.path.join(HERE, 'field-teams.tsv')
ACCOUNTS = os.path.expanduser(os.environ.get('GALAXY_FIELD_ACCOUNTS', '~/.bc23-galaxy-field/accounts.json'))
SPOOL = os.path.join(os.environ.get('GALAXY_HOME', '/home/bcreplica/galaxy'), 'spool', 'pubsub',
                     'replica-siarnaq-execute')
MAX_NAME = 32
SHORT_NAMES = {'team-remember-to-hydrate.sprint_1': 'remember-to-hydrate.sprint_1'}
EMAIL_DOMAIN = 'field.bc23-replica.invalid'
TERMINAL = ('OK!', 'ERR', 'CAN')
WAITING = ('NEW', 'QUE', 'TRY')


def log(*a):
    print(time.strftime('%Y-%m-%dT%H:%M:%S'), *a, flush=True)


# ---------------------------------------------------------------- names
def team_name(entrant):
    """Galaxy team name for an entrant: the name itself when it fits (printable ASCII, <= 32 characters)."""
    name = SHORT_NAMES.get(entrant, entrant)
    if len(name) > MAX_NAME:
        name = name[:MAX_NAME]
    if not re.fullmatch(r'[ -~]+', name):
        raise ValueError(f'team name {name!r} is not printable ASCII')
    return name


def user_name(team):
    """The team's user: Django usernames allow letters, digits and @ . + - _ only."""
    return re.sub(r'[^A-Za-z0-9@.+_-]', '_', team)[:150]


def read_field(path=FIELD_FILE):
    return [l.split('#', 1)[0].strip() for l in open(path) if l.split('#', 1)[0].strip()]


def read_manifest(root=BENCH_ROOT):
    with open(os.path.join(root, 'manifest.tsv')) as fh:
        return {r['name']: r for r in csv.DictReader(fh, delimiter='\t')}


# ---------------------------------------------------------------- blind packaging (file names only)
def _is_test(rel):
    """Test code is left out, by the rule tools/benchcompile/BenchCompiler.java used to build the benchmarks:
    a test/ or tests/ directory (any case) or a file named *Test.java."""
    t = '/' + rel.replace(os.sep, '/').lower() + '/'
    return '/test/' in t or '/tests/' in t or '/.git/' in t or rel.endswith('Test.java')


def find_package_dir(repo_dir, package):
    """The directory holding the package's RobotPlayer.java, by names only: <...>/<package>/RobotPlayer.java;
    else the single directory anywhere in the repo that holds a RobotPlayer.java (a package kept at the root)."""
    named, any_rp = [], []
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = sorted(d for d in dirs if d != '.git')
        rel = os.path.relpath(root, repo_dir)
        if 'RobotPlayer.java' in files and not _is_test(rel):
            any_rp.append(root)
            if os.path.basename(root) == package:
                named.append(root)
    if len(named) == 1:
        return named[0]
    if len(named) > 1:
        src = [d for d in named if '/src/' in d + '/']
        if len(src) == 1:
            return src[0]
        raise LookupError(f'{package}: {len(named)} directories named like the package hold a RobotPlayer.java')
    if len(any_rp) == 1:
        return any_rp[0]
    raise LookupError(f'{package}: no unique RobotPlayer.java directory ({len(any_rp)} found)')


def java_files(d, recursive=True):
    out = []
    for root, dirs, files in os.walk(d):
        dirs[:] = sorted(x for x in dirs if x != '.git')
        for f in sorted(files):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, d)
            if f.endswith('.java') and not _is_test(rel):
                out.append(rel)
        if not recursive:
            break
    return out


def zip_entries(pkg_dir, package, mode, repo_dir):
    """[(file on disk, name in the zip)]. mode 'package': the package's files under <package>/; mode 'root': every
    top-level directory of the package's source root too (helper packages), each under its own name."""
    at_root = os.path.abspath(pkg_dir) == os.path.abspath(repo_dir) or os.path.basename(pkg_dir) != package
    own = [(os.path.join(pkg_dir, r), f'{package}/{r}') for r in java_files(pkg_dir, recursive=not at_root)]
    if mode == 'package' or at_root:
        return own
    root = os.path.dirname(pkg_dir)
    out = list(own)
    for d in sorted(os.listdir(root)):
        full = os.path.join(root, d)
        if d == package or not os.path.isdir(full) or d.startswith('.') or _is_test(d):
            continue
        out += [(os.path.join(full, r), f'{d}/{r}') for r in java_files(full)]
    return out


def build_zip(entries):
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for full, arc in entries:
            z.write(full, arc)
    return buf.getvalue()


def compiles(zip_bytes):
    """Compile the zip as saturn does (tools/lib.sh compile_src) with every byte of compiler output discarded."""
    d = tempfile.mkdtemp(prefix='bc23-field-')
    try:
        with zipfile.ZipFile(__import__('io').BytesIO(zip_bytes)) as z:
            z.extractall(os.path.join(d, 'src'))
        rc = subprocess.run(['bash', '-c', 'source "$1" >/dev/null 2>&1 && compile_src "$2" "$3"', '_',
                             os.path.join(REPO, 'tools', 'lib.sh'), os.path.join(d, 'src'), os.path.join(d, 'out')],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900).returncode
        return rc == 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


def plan(field=None, manifest=None, check=True):
    """One row per entrant: entrant, team, user, package, repo, source (package dir relative to the repo), mode."""
    field = field or read_field()
    manifest = manifest or read_manifest()
    rows = []
    for e in field:
        m = manifest[e]
        repo_dir = os.path.join(BENCH_ROOT, m['repo'])
        pkg_dir = find_package_dir(repo_dir, m['package'])
        mode = 'package'
        if check:
            if not compiles(build_zip(zip_entries(pkg_dir, m['package'], 'package', repo_dir))):
                mode = 'root' if compiles(build_zip(zip_entries(pkg_dir, m['package'], 'root', repo_dir))) else 'FAILS'
        t = team_name(e)
        rows.append({'entrant': e, 'team': t, 'user': user_name(t), 'package': m['package'], 'repo': m['repo'],
                     'source': os.path.relpath(pkg_dir, repo_dir), 'mode': mode})
    return rows


MAP_HDR = ['entrant', 'team', 'user', 'package', 'repo', 'source', 'mode']


def write_mapping(rows, path=MAPPING):
    with open(path + '.tmp', 'w', newline='') as fh:
        fh.write('# Field entrants on the galaxy replica (tools/galaxy/field.py plan). team = galaxy team name '
                 '(<= 32 printable ASCII); user = its user; source = the package directory in the repo (".": the '
                 'repo root); mode = zip contents (package | root: the whole source root).\n')
        w = csv.DictWriter(fh, fieldnames=MAP_HDR, delimiter='\t', lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow(r)
    os.replace(path + '.tmp', path)


def read_mapping(path=MAPPING):
    with open(path) as fh:
        return list(csv.DictReader((l for l in fh if not l.startswith('#')), delimiter='\t'))


def entrant_of(team, mapping_rows):
    """Galaxy team name -> entrant name (they differ only for shortened names)."""
    for r in mapping_rows:
        if r['team'] == team:
            return r['entrant']
    return team


# ---------------------------------------------------------------- accounts (secrets: never printed)
def load_accounts(path=ACCOUNTS):
    if not os.path.exists(path):
        return {}
    st = os.stat(path)
    if st.st_mode & 0o077:
        raise SystemExit(f'{path} must be mode 600 (it holds the field users\' passwords)')
    with open(path) as fh:
        return json.load(fh)


def save_accounts(acc, path=ACCOUNTS):
    d = os.path.dirname(path)
    os.makedirs(d, mode=0o700, exist_ok=True)
    os.chmod(d, 0o700)
    fd = os.open(path + '.tmp', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as fh:
        json.dump(acc, fh, indent=1, sort_keys=True)
    os.replace(path + '.tmp', path)


# ---------------------------------------------------------------- seeding (the contestant's sign-up flow)
def seed_one(c, row, acc, save, ep):
    user = row['user']
    a = acc.setdefault(user, {})
    if 'password' not in a:
        a['password'] = secrets.token_urlsafe(24)
        save()                                   # stored before the account exists: a crash never loses it
    if not a.get('user_id'):
        try:
            r = c.request('POST', '/api/user/u/', {
                'username': user, 'password': a['password'], 'email': f'{user.lower()}@{EMAIL_DOMAIN}',
                'first_name': 'Field', 'last_name': row['entrant'].split('.')[0][:30] or 'Team',
                'profile': {'gender': '?', 'country': 'US', 'school': '',
                            'biography': f'Public Battlecode 2023 bot {row["entrant"]} (practice field).'}})
            a['user_id'] = r['id']
        except ApiError as e:
            if e.code != 400 or 'exists' not in e.detail:
                raise
        save()
    s = Session(c, user, a['password'])
    if not a.get('user_id'):
        a['user_id'] = s.api('GET', '/api/user/u/me/')['id']
        save()
    try:
        team = s.api('GET', f'/api/team/{ep}/t/me/')
    except ApiError as e:
        if e.code != 404:
            raise
        team = s.api('POST', f'/api/team/{ep}/t/', {'name': row['team'], 'episode': ep})
        log('team created', row['team'], team['id'])
    a['team_id'] = team['id']
    prof = team.get('profile') or {}
    if prof.get('auto_accept_reject_ranked') != 'A' or prof.get('auto_accept_reject_unranked') != 'A':
        s.api('PATCH', f'/api/team/{ep}/t/me/', {'profile': {
            'auto_accept_reject_ranked': 'A', 'auto_accept_reject_unranked': 'A',
            'quote': '', 'biography': f'{row["entrant"]}: a public Battlecode 2023 bot in the practice field.'}})
    save()
    subs = s.pages(f'/api/compete/{ep}/submission/', limit=3)
    if any(x['accepted'] for x in subs) or any(x['status'] not in TERMINAL for x in subs):
        return s, 'has submission'
    mode = row.get('mode') or 'package'
    repo_dir = os.path.join(BENCH_ROOT, row['repo'])
    pkg_dir = os.path.normpath(os.path.join(repo_dir, row['source']))
    data = build_zip(zip_entries(pkg_dir, row['package'], 'package' if mode == 'FAILS' else mode, repo_dir))
    body, ct = multipart({'package': row['package'], 'description': f'{row["entrant"]} (public source)'},
                         {'source_code': ('source.zip', data, 'application/zip')})
    sub = s.api('POST', f'/api/compete/{ep}/submission/', body, ctype=ct)
    a.setdefault('submissions', []).append(sub['id'])
    save()
    return s, f'uploaded submission {sub["id"]} ({len(data)} bytes, {mode})'


def sessions(c, acc, mapping):
    return {r['team']: Session(c, r['user'], acc[r['user']]['password'])
            for r in mapping if r['user'] in acc and acc[r['user']].get('team_id')}


# ---------------------------------------------------------------- compile results
LOG_KEEP = re.compile(r'^>>>|error:|^\d+ errors?$|Verifier|[Ii]llegal|not allowed|must not|[Rr]efus|malformed|'
                      r'Exception|Package name|exit|status')


def safe_log_tail(logs, n=12):
    """The tail of a compile log without any source excerpt: saturn's step lines and javac's error lines only
    (javac prints the offending source line and a caret under each error; those are dropped)."""
    keep = [l.rstrip() for l in (logs or '').splitlines() if LOG_KEEP.search(l) and not l.lstrip().startswith('^')]
    return keep[-n:]


def latest_submission(s, ep):
    subs = s.pages(f'/api/compete/{ep}/submission/', limit=1)
    return subs[0] if subs else None


# ---------------------------------------------------------------- activity
def queue_backlog(spool=SPOOL, client=None, ep='bc23'):
    """Matches waiting for an engine: saturn's execute queue (ready + delayed messages in the replica's Pub/Sub
    spool, readable by group bcreplica). Without access to it, count unstarted matches in the API's match list."""
    try:
        return sum(len([f for f in os.listdir(os.path.join(spool, k)) if not f.startswith('.')])
                   for k in ('ready', 'delayed'))
    except OSError:
        if client is None:
            raise
    n = 0
    for page in range(1, 31):
        r = client.request('GET', f'/api/compete/{ep}/match/?page={page}')
        ms = r.get('results', [])
        n += sum(1 for m in ms if m['status'] in WAITING)
        if not r.get('next') or (ms and all(m['status'] in TERMINAL for m in ms)):
            break
    return n


def pick_opponent(ladder, team_id, band, rnd):
    """A team rated at or above the challenger (galaxy refuses ranked requests to lower-rated teams), among the
    `band` closest above it; None when nobody is. ladder: rankings() rows."""
    me = next((t for t in ladder if t['id'] == team_id), None)
    if me is None or me['rating'] is None:
        return None
    above = [t for t in ladder if t['id'] != team_id and t['has_active_submission'] and t['status'] == 'R'
             and t['rating'] is not None and t['rating'] >= me['rating']]
    rnd.shuffle(above)                                    # ties (every new team is at 0) are broken at random
    above.sort(key=lambda t: t['rating'] - me['rating'])
    return rnd.choice(above[:band]) if above else None


def under_hourly_cap(times, now, max_per_hour):
    """True if fewer than max_per_hour requests were made in the hour before now (times: request epoch seconds)."""
    return sum(1 for t in times if now - t < 3600) < max_per_hour


def team_waiting(c, ep, team_id):
    """Matches of one team that are queued or running (first page of its scrimmages, newest first)."""
    r = c.request('GET', f'/api/compete/{ep}/match/scrimmage/?team_id={team_id}')
    return sum(1 for m in r.get('results', []) if m['status'] in WAITING + ('RUN',))


def activity(c, acc, mapping, ep, poll=60, max_backlog=1, band=3, once=False, seed=None, ladder_ttl=300,
             max_per_hour=4, pause_team='vibe23'):
    # owner, PROMPTS 29 (2026-10-08): once the field's ordering was known, field-vs-field games were cut back so that
    # our candidates' games run sooner: at most max_per_hour requests an hour, none while any match waits beyond
    # max_backlog, and none while pause_team (our team) has a match queued or running
    rnd = random.Random(seed)
    sess = sessions(c, acc, mapping)
    ids = {r['team']: acc[r['user']]['team_id'] for r in mapping if r['team'] in sess}
    rest = {}                                             # team -> time it may request again
    stop = {'now': False}

    def on_signal(signum, frame):
        stop['now'] = True
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    ladder, ladder_at, made = None, 0, 0
    times = []
    log(f'field activity: {len(sess)} field teams; at most {max_per_hour} ranked requests an hour, one per {poll}s while '
        f'fewer than {max_backlog} matches wait and {pause_team} has none waiting; opponents among the {band} closest '
        f'teams rated at or above')
    while not stop['now']:
        try:
            backlog = queue_backlog(client=c, ep=ep)
            ok = backlog < max_backlog and under_hourly_cap(times, time.time(), max_per_hour)
            if ok:
                if ladder is None or time.time() - ladder_at > ladder_ttl:
                    ladder, ladder_at = rankings(c, ep), time.time()
                ours = next((t['id'] for t in ladder if t['name'] == pause_team), None)
                if ours is not None and team_waiting(c, ep, ours) > 0:
                    ok = False
            if ok:
                active = {t['id'] for t in ladder if t['has_active_submission']}
                pool = [n for n in sess if ids[n] in active and rest.get(n, 0) <= time.time()]
                rnd.shuffle(pool)
                for name in pool[:5]:
                    opp = pick_opponent(ladder, ids[name], band, rnd)
                    if opp is None:
                        continue
                    try:
                        r = sess[name].api('POST', f'/api/compete/{ep}/request/', {
                            'is_ranked': True, 'requested_to': opp['id'], 'player_order': '?', 'map_names': []})
                        made += 1
                        times.append(time.time())
                        log(f'request {r["id"]}: {name} -> {opp["name"]} (ranked; {name} {fmt(rating_of(ladder, ids[name]))}'
                            f', {opp["name"]} {fmt(opp["rating"])}; backlog {backlog}; {made} made)')
                        ladder_at = 0                    # ratings move: re-read before the next pick
                        break
                    except ApiError as e:
                        code = e.code_name()
                        if e.code == 429:
                            rest[name] = time.time() + 3600
                        elif e.code == 409:
                            rest[name] = time.time() + 600
                        log(f'refused: {name} -> {opp["name"]}: HTTP {e.code} {code or e.detail[:120]}')
            if once:
                break
        except ApiError as e:
            log(f'API error: {e}')
        except Exception as e:                            # a transient failure must not stop the process
            log(f'error: {type(e).__name__}: {e}')
            if once:
                raise
        for _ in range(poll):
            if stop['now']:
                break
            time.sleep(1)
    log(f'field activity: stopped after {made} requests')
    return made


def rating_of(ladder, team_id):
    return next((t['rating'] for t in ladder if t['id'] == team_id), None)


def fmt(v):
    return '-' if v is None else f'{v:.0f}'


# ---------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--site', default=None, help='replica site URL (default: client.SITE)')
    ap.add_argument('--connect', default=os.environ.get('GALAXY_CONNECT', '127.0.0.1'),
                    help="TCP address for the site (default 127.0.0.1: the VM's own Caddy; '' = DNS)")
    sp = ap.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('plan'); s.add_argument('--out', default=MAPPING); s.add_argument('--no-check', action='store_true')
    s = sp.add_parser('seed'); s.add_argument('--only', action='append')
    s = sp.add_parser('wait'); s.add_argument('--timeout', type=int, default=3600)
    sp.add_parser('status')
    s = sp.add_parser('activity'); s.add_argument('--poll', type=int, default=60)
    s.add_argument('--max-backlog', type=int, default=1); s.add_argument('--band', type=int, default=3)
    s.add_argument('--max-per-hour', type=int, default=4); s.add_argument('--pause-team', default='vibe23')
    s.add_argument('--once', action='store_true')
    a = ap.parse_args(argv)
    kw = {'connect': a.connect or None}
    if a.site:
        kw['site'] = a.site
    c = Client(**kw)
    ep = c.episode
    if a.cmd == 'plan':
        rows = plan(check=not a.no_check)
        write_mapping(rows, a.out)
        for r in rows:
            if r['team'] != r['entrant'] or r['mode'] != 'package':
                print(f'{r["entrant"]}: team {r["team"]!r}, zip mode {r["mode"]}')
        print(f'plan: {len(rows)} entrants -> {a.out}')
        return 0
    mapping = read_mapping()
    acc = load_accounts()
    if a.cmd == 'seed':
        todo = [r for r in mapping if not a.only or r['entrant'] in a.only or r['team'] in a.only]
        for r in todo:
            try:
                _, what = seed_one(c, r, acc, lambda: save_accounts(acc), ep)
                log(f'{r["team"]}: team {acc[r["user"]].get("team_id")}, {what}')
            except (ApiError, LookupError, OSError) as e:
                log(f'{r["team"]}: FAILED {e}')
        return 0
    sess = sessions(c, acc, mapping)
    if a.cmd in ('wait', 'status'):
        t0 = time.time()
        while True:
            subs = {}
            for r in mapping:
                if r['team'] in sess:
                    subs[r['team']] = latest_submission(sess[r['team']], ep)
            pending = [n for n, x in subs.items() if x is None or x['status'] not in TERMINAL]
            if a.cmd == 'status' or not pending or time.time() - t0 > a.timeout:
                break
            log(f'{len(subs) - len(pending)} of {len(subs)} compiled; waiting for {len(pending)}')
            time.sleep(30)
        ladder = {t['id']: t for t in rankings(c, ep)}
        ok = 0
        for r in mapping:
            x = subs.get(r['team'])
            tid = acc.get(r['user'], {}).get('team_id')
            st = 'no account' if r['team'] not in sess else 'no submission' if x is None else \
                f'submission {x["id"]} {x["status"]} {"accepted" if x["accepted"] else "NOT accepted"}'
            if x and x['accepted']:
                ok += 1
            if a.cmd == 'status' or not (x and x['accepted']):
                print(f'{r["team"]:34s} team {tid} rating {fmt((ladder.get(tid) or {}).get("rating"))}  {st}')
                if x and x['status'] in TERMINAL and not x['accepted']:
                    for line in safe_log_tail(x.get('logs')):
                        print('    | ' + line)
        print(f'{ok} of {len(mapping)} field teams have an accepted submission')
        return 0 if ok == len(mapping) else 1
    if a.cmd == 'activity':
        activity(c, acc, mapping, ep, a.poll, a.max_backlog, a.band, a.once, max_per_hour=a.max_per_hour,
                 pause_team=a.pause_team)
        return 0
    return 2


if __name__ == '__main__':
    sys.exit(main())
