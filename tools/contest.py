#!/usr/bin/env python3
"""Contestant client for the galaxy replica: everything a team does on play.battlecode.org, through the same HTTP API
the website uses (siarnaq), so that our ladder play is exactly the contest's (owner, PROMPTS 11). Standard library only.

    tools/contest.py register --email E                     # sign up our team user (credentials file below)
    tools/contest.py create-team <name>                     # create our team in the episode
    tools/contest.py auto-accept [--ranked A|R|M] [--unranked A|R|M]
    tools/contest.py login                                  # JWT for our team user
    tools/contest.py me                                     # our team: rating, active submission
    tools/contest.py submit <package> [-m TEXT] [--wait]    # zip src/<package>/ as the contest expects and upload it
    tools/contest.py submissions                            # our submissions and their compile status
    tools/contest.py teams [--search TEXT]                  # the ladder (rating order)
    tools/contest.py request <team> [--ranked] [--maps a,b,c] [--order + | - | ?]
    tools/contest.py outbox | inbox                         # pending scrimmage requests
    tools/contest.py accept <id> | reject <id>
    tools/contest.py matches [--team NAME] [--pages N]      # scrimmages, newest first
    tools/contest.py fetch <match id ...> [--out DIR]       # download replays (one file per match, all its games)
    tools/contest.py block <cells> --tag T                  # a block of unranked requests (one line: team map,map,...
                                                            # [order]); waits, downloads, writes a run directory
                                                            # (results.csv, census.csv) for tools/paired.py

Site: $CONTEST_SITE (default https://galaxy.136-86-167-127.sslip.io). The site sits behind a basic-auth gate: requests
without a JWT (login, replay downloads) carry the gate login (user owner, password in ~/.bc23-replica-password); API
requests carry our team's JWT, as the website does. Our team user's credentials: ~/.bc23-galaxy-team (two lines: user
name, password; mode 600). Tokens are cached in ~/.cache/bc23-contest/token.json (mode 600).

Galaxy's own rules apply (enforced by the server, not here): per-episode hourly limits on ranked and unranked
requests, counting requests AND matches of the last hour, so an accepted request counts twice. Galaxy's default is
10 and 10 (5 accepted requests an hour); our replica uses 20 ranked and 40 unranked (owner, PROMPTS 15-16). Up to 10
maps per unranked request; ranked requests use 3 random maps in shuffled order, only against teams rated at least as
high, at most 3 active ranked scrimmages against one team.

Run directory (`block`): gauntlet/<stamp>-<tag>/ with results.csv (opponent,map,bot_side,winner_side,rounds,
bot_result,reason,seed) and census.csv, one row per game. bot_side is our player label in the replay (A = player
index 0); seed is 'map' for a game on the map's own spawns and 'map-rev' for an alternate-order game (HQ ownership
flipped), so (opponent, map, bot_side, seed) names the same physical game in any run that used the same request."""
import argparse, base64, csv, io, json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request, uuid, zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get('CONTEST_SITE', 'https://galaxy.136-86-167-127.sslip.io').rstrip('/')
EPISODE = os.environ.get('CONTEST_EPISODE', 'bc23')
GATE_USER = 'owner'
GATE_FILE = os.path.expanduser('~/.bc23-replica-password')
TEAM_FILE = os.path.expanduser('~/.bc23-galaxy-team')
CACHE = os.path.expanduser('~/.cache/bc23-contest')
# never the real contest (owner, PROMPTS 12: none of this may affect play.battlecode.org)
if 'battlecode.org' in urllib.parse.urlparse(SITE).netloc:
    raise SystemExit(f'refusing CONTEST_SITE={SITE}: this client talks only to our replica')


# ---------------------------------------------------------------- HTTP
def _gate():
    pw = open(GATE_FILE).read().strip()
    return 'Basic ' + base64.b64encode(f'{GATE_USER}:{pw}'.encode()).decode()


def http(method, path, body=None, token=None, raw=False, ctype=None, timeout=120):
    """One request. token=None -> the basic-auth gate; else 'Bearer <token>'. Returns parsed JSON (or bytes if raw)."""
    url = path if path.startswith('http') else SITE + path
    if not url.startswith(SITE + '/'):
        raise SystemExit(f'refusing a request outside the replica site: {url}')
    data = None
    headers = {'Authorization': f'Bearer {token}' if token else _gate(), 'Accept': 'application/json'}
    if body is not None:
        if ctype:
            data, headers['Content-Type'] = body, ctype
        else:
            data, headers['Content-Type'] = json.dumps(body).encode(), 'application/json'
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = r.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors='replace')[:500]
        raise ApiError(e.code, detail) from None
    if raw:
        return out
    return json.loads(out) if out else None


class ApiError(Exception):
    def __init__(self, code, detail):
        super().__init__(f'HTTP {code}: {detail}')
        self.code, self.detail = code, detail


def _save_token(tok):
    os.makedirs(CACHE, mode=0o700, exist_ok=True)
    p = os.path.join(CACHE, 'token.json')
    fd = os.open(p + '.tmp', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as fh:
        json.dump(tok, fh)
    os.replace(p + '.tmp', p)


def login():
    user, pw = [l.strip() for l in open(TEAM_FILE).read().splitlines()[:2]]
    tok = http('POST', '/api/token/', {'username': user, 'password': pw})
    tok['at'] = time.time()
    _save_token(tok)
    return tok['access']


def token():
    """A valid access token: cached, refreshed, or a fresh login."""
    p = os.path.join(CACHE, 'token.json')
    if os.path.exists(p):
        tok = json.load(open(p))
        if time.time() - tok.get('at', 0) < 240:
            return tok['access']
        try:
            new = http('POST', '/api/token/refresh/', {'refresh': tok['refresh']})
            tok.update(new)
            tok['at'] = time.time()
            _save_token(tok)
            return tok['access']
        except ApiError:
            pass
    return login()


def api(method, path, body=None, **kw):
    return http(method, path, body, token=token(), **kw)


def pages(path, limit=None):
    """Follow galaxy's paginated lists ({count, next, results})."""
    out, url, n = [], path, 0
    while url and (limit is None or n < limit):
        r = api('GET', url)
        if isinstance(r, list):
            return r
        out += r.get('results', [])
        url = r.get('next')
        n += 1
    return out


# ---------------------------------------------------------------- account
def register(username, password, email, first='Vibe', last='Bot', country='US'):
    """POST /api/user/u/ (the sign-up form). No JWT yet: the request carries the site gate."""
    body = {'username': username, 'password': password, 'email': email, 'first_name': first, 'last_name': last,
            'profile': {'gender': '*', 'country': country}}
    return http('POST', '/api/user/u/', body)


def create_team(name, quote=''):
    return api('POST', f'/api/team/{EPISODE}/t/', {'name': name, 'episode': EPISODE, 'profile': {'quote': quote}})


def set_auto_accept(ranked='A', unranked='A'):
    return api('PATCH', f'/api/team/{EPISODE}/t/me/',
               {'profile': {'auto_accept_reject_ranked': ranked, 'auto_accept_reject_unranked': unranked}})


# ---------------------------------------------------------------- team and submissions
def me():
    return api('GET', f'/api/team/{EPISODE}/t/me/')


def team_by_name(name):
    for t in pages(f'/api/team/{EPISODE}/t/?search={urllib.parse.quote(name)}', limit=5):
        if t['name'] == name:
            return t
    raise SystemExit(f'no team named {name!r}')


def zip_package(package, src=None):
    """The submission archive: the package directory at the zip root (src/<package>/** -> <package>/**)."""
    root = src or os.path.join(REPO, 'src')
    pdir = os.path.join(root, package)
    if not os.path.isdir(pdir):
        raise SystemExit(f'no package directory {pdir}')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(pdir):
            for f in sorted(files):
                if f.endswith('.java'):
                    full = os.path.join(base, f)
                    z.write(full, os.path.relpath(full, root))
    return buf.getvalue()


def multipart(fields, files):
    b = uuid.uuid4().hex
    out = io.BytesIO()
    for k, v in fields.items():
        out.write(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, (fname, data, ct) in files.items():
        out.write(f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{fname}"\r\nContent-Type: {ct}\r\n\r\n'.encode())
        out.write(data)
        out.write(b'\r\n')
    out.write(f'--{b}--\r\n'.encode())
    return out.getvalue(), f'multipart/form-data; boundary={b}'


def submit(package, description='', src=None):
    body, ct = multipart({'package': package, 'description': description[:128]},
                         {'source_code': ('submission.zip', zip_package(package, src), 'application/zip')})
    return api('POST', f'/api/compete/{EPISODE}/submission/', body, ctype=ct)


def wait_submission(sid, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = api('GET', f'/api/compete/{EPISODE}/submission/{sid}/')
        if s['status'] in ('OK!', 'ERR', 'CAN'):
            return s
        time.sleep(10)
    raise SystemExit(f'submission {sid} not compiled after {timeout}s')


# ---------------------------------------------------------------- scrimmages
def request(team, ranked=False, maps=(), order='?'):
    tid = team if isinstance(team, int) else team_by_name(team)['id']
    body = {'is_ranked': ranked, 'requested_to': tid, 'player_order': order, 'map_names': list(maps)}
    return api('POST', f'/api/compete/{EPISODE}/request/', body)


def matches(team_id=None, limit_pages=1):
    q = f'?team_id={team_id}' if team_id else ''
    return pages(f'/api/compete/{EPISODE}/match/scrimmage/{q}', limit=limit_pages)


def download(match, out_dir):
    """The match's replay file (all its games) -> out_dir/<match id>.bc23. Returns the path or None if not ready."""
    url = match.get('replay_url')
    if not url or match.get('status') != 'OK!':
        return None
    if url.startswith('/'):
        url = SITE + url
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, f'{match["id"]}.bc23')
    if not os.path.exists(p):
        data = http('GET', url, raw=True, timeout=600)
        with open(p + '.tmp', 'wb') as fh:
            fh.write(data)
        os.replace(p + '.tmp', p)
    return p


def games_of(replay):
    """[(index, map, winner A|B|-, rounds)] from the replay (tools/replay-dump.sh --games)."""
    out = subprocess.run(['bash', os.path.join(REPO, 'tools', 'replay-dump.sh'), replay, '--games'],
                         capture_output=True, text=True, timeout=900).stdout
    rows = []
    for line in out.splitlines():
        p = line.split()
        if len(p) == 4 and p[0].isdigit():
            rows.append((int(p[0]), p[1], p[2], int(p[3])))
    return rows


def our_label(match, team_id):
    for p in match['participants']:
        if p['team'] == team_id:
            return 'A' if p['player_index'] == 0 else 'B'
    return None


def opponent_name(match, team_id):
    for p in match['participants']:
        if p['team'] != team_id:
            return p['teamname']
    return '?'


def run_rows(match, replay, team_id):
    """results.csv rows for one match (one per game)."""
    lab = our_label(match, team_id)
    opp = opponent_name(match, team_id)
    rows = []
    for i, m, w, rounds in games_of(replay):
        rev = bool(match.get('alternate_order')) and i % 2 == 1
        res = 'win' if w == lab else 'loss' if w in ('A', 'B') else 'unknown'
        sub = next((p.get('submission', '') for p in match['participants'] if p['team'] == team_id), '')
        rows.append({'opponent': opp, 'map': m, 'bot_side': lab, 'winner_side': w, 'rounds': rounds,
                     'bot_result': res, 'reason': '', 'seed': 'map-rev' if rev else 'map', 'game': i,
                     'match': match['id'], 'submission': sub})
    return rows


# ---------------------------------------------------------------- blocks
def read_cells(path):
    """Lines: <team name> <map,map,...> [order]; '#' comments."""
    cells = []
    for line in open(path):
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        p = line.split()
        cells.append((p[0], p[1].split(','), p[2] if len(p) > 2 else '+'))
    return cells


def block(cells_file, tag, poll=60, max_wait=6 * 3600):
    """Issue every request of the block (waiting out galaxy's hourly limit), wait for the matches, download them and
    write a run directory. Requests are recorded in the run directory as they are made, so a crash can be resumed by
    re-running with RESUME=<dir>."""
    cells = read_cells(cells_file)
    team = me()
    tid = team['id']
    run = os.environ.get('RESUME') or os.path.join(REPO, 'gauntlet', time.strftime('%Y%m%d-%H%M%S') + '-' + tag)
    os.makedirs(run, exist_ok=True)
    log_p = os.path.join(run, 'requests.jsonl')
    done = [json.loads(l) for l in open(log_p)] if os.path.exists(log_p) else []
    # matches that existed before this block (an earlier panel's identical requests) are never taken as ours
    floor_p = os.path.join(run, 'match_floor.txt')
    if not os.path.exists(floor_p):
        ids = [m['id'] for m in matches(tid, limit_pages=1)]
        open(floor_p, 'w').write(str(max(ids) if ids else 0))
    floor = int(open(floor_p).read().strip() or 0)
    subs = pages(f'/api/compete/{EPISODE}/submission/', limit=1)
    active = next((x for x in subs if x.get('accepted')), {})
    with open(os.path.join(run, 'provenance.txt'), 'a') as fh:
        fh.write(f'team={team["name"]} team_id={tid} site={SITE} cells={cells_file} match_floor={floor} '
                 f'latest_accepted_submission={active.get("id")} package={active.get("package")}\n')
    for k, (opp, maps, order) in enumerate(cells):
        if any(d['cell'] == k for d in done):
            continue
        while True:
            try:
                r = request(opp, False, maps, order)
                break
            except ApiError as e:
                if e.code == 429 or (e.code == 400 and ('limit' in e.detail.lower() or 'too many' in e.detail.lower())):
                    print(time.strftime('%H:%M:%S'), 'hourly request limit reached; waiting', flush=True)
                    time.sleep(300)
                    continue
                raise
        d = {'cell': k, 'opponent': opp, 'maps': maps, 'order': order, 'request': r['id'], 'at': time.time()}
        with open(log_p, 'a') as fh:
            fh.write(json.dumps(d) + '\n')
        done.append(d)
        print(time.strftime('%H:%M:%S'), 'requested', opp, len(maps), 'maps, request', r['id'], flush=True)
    # match each request to its match: same opponent, same maps in order, created after the request
    t0 = time.time()
    rows, census_rows, hdr = [], [], None
    pending = {d['request']: d for d in done}
    found = {}
    while pending and time.time() - t0 < max_wait:
        ms = matches(tid, limit_pages=5)
        for m in ms:
            if m['id'] in found.values() or m['id'] <= floor:
                continue
            for rid, d in list(pending.items()):
                if opponent_name(m, tid) == d['opponent'] and list(m.get('maps') or []) == d['maps'] \
                        and m['status'] in ('OK!', 'ERR', 'CAN') and rid not in found:
                    found[rid] = m['id']
                    rep = download(m, os.path.join(run, 'replays'))
                    if rep:
                        rows += run_rows(m, rep, tid)
                        census_rows += census_of(rep, rows[-len(games_of(rep)):])
                    del pending[rid]
                    break
        if pending:
            time.sleep(poll)
    write_run(run, rows, census_rows)
    print(f'{run}: {len(rows)} games from {len(found)} matches; {len(pending)} requests unresolved')
    return run


def census_of(replay, game_rows):
    out = []
    for g in game_rows:
        txt = subprocess.run(['bash', os.path.join(REPO, 'tools', 'replay-dump.sh'), replay, '--game', str(g['game']),
                              '--census', '--no-header'], capture_output=True, text=True, timeout=900).stdout
        for line in txt.splitlines():
            if line.strip():
                out.append(f"{g['opponent']},{g['map']},{g['bot_side']},{g['seed']},{line}")
    return out


def write_run(run, rows, census_rows):
    hdr = ['opponent', 'map', 'bot_side', 'winner_side', 'rounds', 'bot_result', 'reason', 'seed', 'game', 'match',
           'submission']
    with open(os.path.join(run, 'results.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=hdr)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    if census_rows:
        h = subprocess.run(['bash', os.path.join(REPO, 'tools', 'replay-dump.sh'), '--census-header'],
                           capture_output=True, text=True).stdout.strip()
        with open(os.path.join(run, 'census.csv'), 'w') as fh:
            fh.write('cell_opponent,cell_map,cell_side,cell_seed,' + h + '\n')
            for line in sorted(census_rows):
                fh.write(line + '\n')


# ---------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('register'); s.add_argument('--email', required=True)
    s = sp.add_parser('create-team'); s.add_argument('name'); s.add_argument('--quote', default='')
    s = sp.add_parser('auto-accept'); s.add_argument('--ranked', default='A', choices=['A', 'R', 'M'])
    s.add_argument('--unranked', default='A', choices=['A', 'R', 'M'])
    sp.add_parser('login')
    sp.add_parser('me')
    s = sp.add_parser('submit'); s.add_argument('package'); s.add_argument('-m', default=''); s.add_argument('--src')
    s.add_argument('--wait', action='store_true')
    sp.add_parser('submissions')
    s = sp.add_parser('teams'); s.add_argument('--search', default='')
    s = sp.add_parser('request'); s.add_argument('team'); s.add_argument('--ranked', action='store_true')
    s.add_argument('--maps', default=''); s.add_argument('--order', default='?', choices=['+', '-', '?'])
    sp.add_parser('outbox'); sp.add_parser('inbox')
    s = sp.add_parser('accept'); s.add_argument('id', type=int)
    s = sp.add_parser('reject'); s.add_argument('id', type=int)
    s = sp.add_parser('matches'); s.add_argument('--team'); s.add_argument('--pages', type=int, default=1)
    s = sp.add_parser('fetch'); s.add_argument('ids', nargs='+', type=int); s.add_argument('--out', default='replays')
    s = sp.add_parser('block'); s.add_argument('cells'); s.add_argument('--tag', required=True)
    a = ap.parse_args()
    E = EPISODE
    if a.cmd == 'register':
        user, pw = [l.strip() for l in open(TEAM_FILE).read().splitlines()[:2]]
        r = register(user, pw, a.email); print('registered', r.get('username'), r.get('id'))
    elif a.cmd == 'create-team':
        t = create_team(a.name, a.quote); print('team', t.get('id'), t.get('name'))
    elif a.cmd == 'auto-accept':
        t = set_auto_accept(a.ranked, a.unranked); print('profile', (t.get('profile') or {}))
    elif a.cmd == 'login':
        login(); print('logged in')
    elif a.cmd == 'me':
        t = me(); print(json.dumps(t, indent=1)[:3000])
    elif a.cmd == 'submit':
        s = submit(a.package, a.m, a.src); print('submission', s['id'], s['status'])
        if a.wait:
            s = wait_submission(s['id']); print('submission', s['id'], s['status'], 'accepted' if s['accepted'] else 'NOT accepted')
            if s['status'] != 'OK!':
                print(s.get('logs', '')[-2000:])
    elif a.cmd == 'submissions':
        for s in pages(f'/api/compete/{E}/submission/', limit=2):
            print(s['id'], s['status'], 'accepted' if s['accepted'] else '-', s['package'], s['created'][:16], s['description'])
    elif a.cmd == 'teams':
        ts = pages(f'/api/team/{E}/t/?search={urllib.parse.quote(a.search)}', limit=20)
        for t in ts:
            rating = ((t.get('profile') or {}).get('rating'))
            print(t['id'], t['name'], rating, t.get('status'))
    elif a.cmd == 'request':
        r = request(a.team, a.ranked, [m for m in a.maps.split(',') if m], a.order)
        print('request', r['id'], 'to', r.get('requested_to_name', a.team), r.get('maps'))
    elif a.cmd in ('outbox', 'inbox'):
        for r in pages(f'/api/compete/{E}/request/{a.cmd}/', limit=5):
            print(r['id'], r.get('requested_by_name'), '->', r.get('requested_to_name'), 'ranked' if r['is_ranked'] else 'unranked',
                  r.get('maps'), r.get('status'))
    elif a.cmd in ('accept', 'reject'):
        api('POST', f'/api/compete/{E}/request/{a.id}/{a.cmd}/'); print(a.cmd, a.id)
    elif a.cmd == 'matches':
        tid = team_by_name(a.team)['id'] if a.team else me()['id']
        for m in matches(tid, a.pages):
            ps = ' vs '.join(f"{p['teamname']}({p['score']})" for p in sorted(m['participants'], key=lambda p: p['player_index']))
            print(m['id'], m['status'], 'ranked' if m['is_ranked'] else 'unranked', ps, ','.join(m.get('maps') or []))
    elif a.cmd == 'fetch':
        tid = me()['id']
        for i in a.ids:
            m = api('GET', f'/api/compete/{E}/match/{i}/')
            p = download(m, a.out)
            print(i, p or f'not ready ({m["status"]})')
            if p:
                for g in games_of(p):
                    print('  game', *g)
    elif a.cmd == 'block':
        block(a.cells, a.tag)
    return 0


if __name__ == '__main__':
    sys.exit(main())
