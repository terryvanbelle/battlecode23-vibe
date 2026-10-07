"""Read models and the JSON API of galaxy-lite (stdlib http.server on 127.0.0.1:8023, no auth, loopback only).

Paths mirror siarnaq's (backend/siarnaq/api/*/urls.py and views.py) with the episode 'bc23'; JSON follows the
serializers (MatchSerializer, MatchParticipantSerializer, TeamPublicSerializer, HistoricalRatingSerializer,
ScrimmageRecordSerializer) plus replica fields marked 'replica' in the docs. Lists are paginated like DRF
({count, next, previous, results}) with ?page= and a replica ?page_size= (default 50, max 1000).

  GET    /api/episode/e/<ep>/                          episode settings
  GET    /api/episode/<ep>/map/                        maps
  POST   /api/episode/e/<ep>/autoscrim/                {"best_of": 3} -> {"matches": [ids]}
  GET    /api/team/<ep>/t/?ordering=-rating&search=    teams (ordering: rating, -rating, name, -name, id, -id)
  GET    /api/team/<ep>/t/<id>/
  POST   /api/team/<ep>/t/create/                      {"name", "status"?}                      (replica)
  GET    /api/compete/<ep>/submission/?team_id=
  GET    /api/compete/<ep>/submission/<id>/
  POST   /api/compete/<ep>/submission/                 {"team", "package", "prebuilt_classes" | "source",
                                                        "snapshot"?, "verify"?, "description"?}
  GET    /api/compete/<ep>/request/?status=P&team_id=                                            (replica)
  POST   /api/compete/<ep>/request/                    {"requested_by", "requested_to", "is_ranked",
                                                        "player_order", "map_names"}
  POST   /api/compete/<ep>/request/<id>/accept/ | /reject/ ;  DELETE /api/compete/<ep>/request/<id>/
  GET    /api/compete/<ep>/match/?team_id=&status=&page=     (also /match/scrimmage/)
  GET    /api/compete/<ep>/match/<id>/                 one match with its games
  GET    /api/compete/<ep>/match/historical_rating/?team_id=
  GET    /api/compete/<ep>/match/scrimmaging_record/?team_id=
  POST   /api/compete/<ep>/match/<id>/requeue/                                                   (replica)
  GET    /replica/status                               queue counts and running matches
  POST   /replica/export-games                         {"out"?, "all"?} -> {"rows": n, "out": path}
  GET    /replica/replay/<uuid>.bc23                   the replay file
team_id and the team fields of POST bodies take a team id or an exact team name.
The same server renders the web pages and serves the replay viewer (web.py: /, /team/<id>, /match/<id>, /matches,
/replay/<uuid>.bc23, /viewer/...). HEAD is answered like GET without a body.
"""
import csv
import http.server
import ipaddress
import json
import os
import re
import shutil
import sys
import urllib.parse

from . import db, matchmaking, rating, web, worker
from .db import SaturnStatus

GAMES_CSV = os.environ.get('REPLICA_GAMES_CSV') or os.path.join(db.REPO, 'progress', 'games.csv')
GAMES_HDR = ['run', 'seq', 'teamA', 'teamB', 'map', 'winner', 'rounds', 'reason', 'seed']


# ---------------------------------------------------------------- read models
def rating_value(conn, rating_id):
    return None if rating_id is None else db.get_rating(conn, rating_id)['value']


def team_public(conn, t):
    r = db.get_rating(conn, t['rating_id'])
    sub = db.active_submission(conn, t['id'])
    pkg = conn.execute('SELECT package FROM submission WHERE id=?', (sub,)).fetchone()['package'] if sub else None
    return {
        'id': t['id'], 'episode': t['episode'], 'name': t['name'], 'members': [], 'status': t['status'],
        'profile': {'rating': r['value'], 'rating_mean': r['mean'], 'rating_n': r['n'],
                    'auto_accept_reject_ranked': t['auto_accept_reject_ranked'],
                    'auto_accept_reject_unranked': t['auto_accept_reject_unranked']},
        'has_active_submission': sub is not None, 'active_submission': sub, 'package': pkg,
    }


ORDERINGS = {'rating': 'r.value', '-rating': 'r.value DESC', 'name': 't.name', '-name': 't.name DESC',
             'id': 't.id', '-id': 't.id DESC', 'mean': 'r.mean', '-mean': 'r.mean DESC'}


def list_teams(conn, episode=db.EPISODE, ordering='-rating', search=None):
    order = ORDERINGS.get(ordering or '-rating')
    if order is None:
        raise ValueError(f'unknown ordering {ordering!r}')
    q = "SELECT t.* FROM team t JOIN rating r ON r.id=t.rating_id WHERE t.episode=? AND t.status != 'O' "
    args = [episode]
    if search:
        q += 'AND t.name LIKE ? '
        args.append(f'%{search}%')
    q += f'ORDER BY {order}, t.id'
    return [team_public(conn, t) for t in conn.execute(q, args)]


def participant_json(conn, p):
    t = conn.execute('SELECT name, rating_id FROM team WHERE id=?', (p['team'],)).fetchone()
    old = rating.get_old_rating(conn, p)
    old_value = old.value if old is not None else rating_value(conn, t['rating_id'])
    return {'team': p['team'], 'teamname': t['name'], 'submission': p['submission'], 'match': p['match'],
            'player_index': p['player_index'], 'score': p['score'], 'rating': rating_value(conn, p['rating_id']),
            'old_rating': old_value}


def game_json(conn, g):
    names = {r['id']: r['name'] for r in conn.execute('SELECT id, name FROM team WHERE id IN (?, ?)',
                                                      (g['team_a'], g['team_b']))}
    win = g['team_a'] if g['winner'] == 'A' else g['team_b'] if g['winner'] == 'B' else None
    return {'idx': g['idx'], 'map': g['map'], 'team_a': names.get(g['team_a']), 'team_b': names.get(g['team_b']),
            'reversed': bool(g['reversed']), 'winner': g['winner'], 'winner_name': names.get(win),
            'round': g['round'], 'reason': g['reason']}


def match_json(conn, m, with_games=True, with_logs=False):
    replay = db.path('replay', f'{m["replay"]}.bc23')
    d = {'id': m['id'], 'status': m['status'], 'episode': m['episode'], 'tournament_round': None,
         'participants': [participant_json(conn, p) for p in db.participants(conn, m['id'])],
         'maps': db.match_map_names(conn, m['id']), 'alternate_order': bool(m['alternate_order']),
         'created': m['created'], 'is_ranked': bool(m['is_ranked']),
         'replay_url': f'/replica/replay/{m["replay"]}.bc23' if os.path.exists(replay) else None,
         'replay_path': replay if os.path.exists(replay) else None,
         'source': m['source'], 'num_failures': m['num_failures'], 'finished': m['finished']}
    if with_games:
        d['games'] = [game_json(conn, g) for g in
                      conn.execute('SELECT * FROM game WHERE match=? ORDER BY idx', (m['id'],))]
    if with_logs:
        d['logs'] = m['logs']
    return d


def list_matches(conn, episode=db.EPISODE, team_id=None, status=None, page=1, page_size=50, base=''):
    q, args = 'FROM match m WHERE m.episode=? ', [episode]
    if team_id is not None:
        q += 'AND EXISTS (SELECT 1 FROM match_participant WHERE match=m.id AND team=?) '
        args.append(team_id)
    if status:
        q += 'AND m.status=? '
        args.append(status)
    return paginate(conn, q, args, 'ORDER BY m.id DESC', lambda m: match_json(conn, m), page, page_size, base,
                    select='SELECT m.* ')


def paginate(conn, q, args, order, fn, page, page_size, base, select='SELECT * '):
    page, page_size = max(1, int(page or 1)), min(1000, max(1, int(page_size or 50)))
    count = conn.execute('SELECT COUNT(*) ' + q, args).fetchone()[0]
    rows = conn.execute(select + q + order + ' LIMIT ? OFFSET ?', args + [page_size, (page - 1) * page_size])
    link = lambda p: f'{base}{"&" if "?" in base else "?"}page={p}&page_size={page_size}' if base else p
    return {'count': count, 'next': link(page + 1) if page * page_size < count else None,
            'previous': link(page - 1) if page > 1 else None, 'results': [fn(r) for r in rows]}


def historical_rating(conn, team_id):
    """MatchViewSet.get_historical_rating: ranked, non-tournament participations with a final rating, in match
    creation order, leaving out matches that involve an invisible team."""
    t = conn.execute('SELECT * FROM team WHERE id=?', (team_id,)).fetchone()
    rows = conn.execute(
        'SELECT m.id AS match, m.created, r.value, r.mean, r.n FROM match_participant mp '
        'JOIN match m ON m.id=mp.match JOIN rating r ON r.id=mp.rating_id '
        f'WHERE mp.team=? AND m.is_ranked=1 AND {db.NO_INVISIBLE_MATCH} ORDER BY m.created, m.id',
        (team_id,)).fetchall()
    return {'team_id': team_id, 'team_rating': {
        'team': team_public(conn, t),
        'rating_history': [{'timestamp': r['created'], 'rating': r['value'], 'mean': r['mean'], 'n': r['n'],
                            'match': r['match']} for r in rows]}}


def scrimmaging_record(conn, team_id):
    """MatchViewSet.scrimmaging_record: match-level wins/losses/ties by summed scores (unscored matches don't count;
    matches that involve an invisible team are left out)."""
    rec = {k: {'wins': 0, 'losses': 0, 'ties': 0} for k in ('Ranked', 'Unranked', 'All')}
    rows = conn.execute(
        'SELECT m.is_ranked, '
        ' (SELECT SUM(score) FROM match_participant WHERE match=m.id AND team=?) AS this_team_score, '
        ' (SELECT SUM(score) FROM match_participant WHERE match=m.id AND team!=?) AS other_team_score '
        'FROM match m WHERE EXISTS (SELECT 1 FROM match_participant WHERE match=m.id AND team=?) '
        f'AND {db.NO_INVISIBLE_MATCH}', (team_id, team_id, team_id)).fetchall()
    for r in rows:
        a, b = r['this_team_score'], r['other_team_score']
        if a is None or b is None:
            continue
        k = 'wins' if a > b else 'losses' if a < b else 'ties'
        rec['Ranked' if r['is_ranked'] else 'Unranked'][k] += 1
        rec['All'][k] += 1
    return {'team_id': team_id, **rec}


def game_record(conn, team_id):
    """Replica extra: games won and lost (all completed matches)."""
    r = conn.execute(
        "SELECT SUM(CASE WHEN (g.winner='A' AND g.team_a=?) OR (g.winner='B' AND g.team_b=?) THEN 1 ELSE 0 END) w, "
        'COUNT(*) n FROM game g WHERE g.team_a=? OR g.team_b=?', (team_id,) * 4).fetchone()
    return {'won': r['w'] or 0, 'lost': (r['n'] or 0) - (r['w'] or 0)}


def ratings_table(conn, episode=db.EPISODE):
    """Teams ranked by displayed (penalized) rating, with mean, n and records."""
    out = []
    for i, t in enumerate(list_teams(conn, episode, '-rating'), 1):
        rec = scrimmaging_record(conn, t['id'])['Ranked']
        g = game_record(conn, t['id'])
        out.append({'rank': i, 'id': t['id'], 'name': t['name'], 'status': t['status'],
                    'value': t['profile']['rating'], 'mean': t['profile']['rating_mean'],
                    'n': t['profile']['rating_n'], 'ranked_record': rec, 'games': g})
    return out


def queue_status(conn):
    running = [{'id': m['id'], 'worker': m['worker'], 'claimed_at': m['claimed_at'],
                'teams': [p['teamname'] for p in match_json(conn, m, with_games=False)['participants']]}
               for m in conn.execute("SELECT * FROM match WHERE status='RUN' ORDER BY id")]
    pending = conn.execute('SELECT COUNT(*) FROM match_participant WHERE rating_id IS NULL').fetchone()[0]
    return {'home': db.home(), 'matches': db.status_counts(conn, 'match'),
            'submissions': db.status_counts(conn, 'submission'),
            'teams': conn.execute('SELECT COUNT(*) FROM team').fetchone()[0],
            'games': conn.execute('SELECT COUNT(*) FROM game').fetchone()[0],
            'games_unexported': conn.execute('SELECT COUNT(*) FROM game WHERE exported IS NULL').fetchone()[0],
            'participations_unrated': pending, 'running': running}


def list_requests(conn, episode=db.EPISODE, status=None, team_id=None):
    q, args = 'SELECT * FROM scrimmage_request WHERE episode=? ', [episode]
    if status:
        q += 'AND status=? '
        args.append(status)
    if team_id is not None:
        q += 'AND (requested_by=? OR requested_to=?) '
        args += [team_id, team_id]
    return [request_json(conn, r) for r in conn.execute(q + 'ORDER BY id DESC', args)]


def request_json(conn, r):
    name = lambda t: conn.execute('SELECT name, rating_id FROM team WHERE id=?', (t,)).fetchone()
    by, to = name(r['requested_by']), name(r['requested_to'])
    maps = [x['name'] for x in conn.execute('SELECT map.name FROM request_map JOIN map ON map.id=request_map.map '
                                            'WHERE request=? ORDER BY sort, request_map.id', (r['id'],))]
    match = conn.execute('SELECT id FROM match WHERE request_id=?', (r['id'],)).fetchone()
    return {'id': r['id'], 'episode': r['episode'], 'created': r['created'], 'status': r['status'],
            'is_ranked': bool(r['is_ranked']), 'requested_by': r['requested_by'], 'requested_by_name': by['name'],
            'requested_by_rating': rating_value(conn, by['rating_id']), 'requested_to': r['requested_to'],
            'requested_to_name': to['name'], 'requested_to_rating': rating_value(conn, to['rating_id']),
            'player_order': r['player_order'], 'maps': maps, 'match': match['id'] if match else None}


def submission_json(conn, s):
    t = conn.execute('SELECT name FROM team WHERE id=?', (s['team'],)).fetchone()
    return {'id': s['id'], 'status': s['status'], 'logs': s['logs'], 'episode': s['episode'], 'team': s['team'],
            'teamname': t['name'], 'created': s['created'], 'accepted': bool(s['accepted']),
            'package': s['package'], 'description': s['description'], 'source_path': s['source_path'],
            'binary_path': s['binary_path'], 'prebuilt_classes': s['prebuilt_classes']}


# ---------------------------------------------------------------- export to progress/games.csv
def export_games(conn, out=None, all_games=False):
    """Append one row per game of every COMPLETED match not yet exported (all_games: every game, flags untouched)
    to progress/games.csv: run=replica-<match>, seq=game number in the match (1-based), teamA/teamB = the teams
    whose code ran as A/B (player_index 0/1), reason = the elolib code (ISL75, TB_*, COIN, ...), seed = 'map', or
    'map-rev' for a game with HQ ownership flipped (alternate order: same packages, swapped spawns), so that the
    analysis tools' dedupe on (teamA, teamB, map, seed) keeps both orientations."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import elolib
    out = out or GAMES_CSV
    q = ("SELECT g.*, ta.name AS na, tb.name AS nb FROM game g JOIN match m ON m.id=g.match "
         "JOIN team ta ON ta.id=g.team_a JOIN team tb ON tb.id=g.team_b WHERE m.status='OK!' "
         + ('' if all_games else 'AND g.exported IS NULL ') + 'ORDER BY g.match, g.idx')
    with db.tx(conn):
        rows = conn.execute(q).fetchall()
        if not rows:
            return 0
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        new = not os.path.exists(out) or os.path.getsize(out) == 0
        with open(out, 'a', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=GAMES_HDR)
            if new:
                w.writeheader()
            for g in rows:
                w.writerow({'run': f'replica-{g["match"]}', 'seq': g['idx'] + 1, 'teamA': g['na'], 'teamB': g['nb'],
                            'map': g['map'], 'winner': g['winner'], 'rounds': g['round'],
                            'reason': elolib.reason_code(g['reason']),
                            'seed': 'map-rev' if g['reversed'] else 'map'})
            fh.flush()
            os.fsync(fh.fileno())
        if not all_games:
            stamp = db.now()
            conn.executemany('UPDATE game SET exported=? WHERE id=?', [(stamp, g['id']) for g in rows])
    return len(rows)


# ---------------------------------------------------------------- HTTP
class HttpError(Exception):
    def __init__(self, code, detail):
        super().__init__(detail)
        self.code, self.detail = code, detail


def _team_id(conn, key, episode):
    if key is None or key == '':
        return None
    try:
        return db.get_team(conn, key, episode)['id']
    except LookupError:
        raise HttpError(400, f'Could not find requested team {key!r}.')


def _bool(v):
    return v if isinstance(v, bool) else str(v).lower() in ('1', 'true', 'yes', 'on')


ROUTES = []


def route(method, pattern):
    def deco(fn):
        ROUTES.append((method, re.compile('^' + pattern + '$'), fn))
        return fn
    return deco


@route('GET', r'/api/episode/e/(?P<ep>[\w-]+)/')
def h_episode(conn, q, body, ep):
    return dict(db.get_episode(conn, ep))


@route('GET', r'/api/episode/(?P<ep>[\w-]+)/map/')
def h_maps(conn, q, body, ep):
    return [dict(r) for r in conn.execute('SELECT * FROM map WHERE episode=? ORDER BY id', (ep,))]


@route('POST', r'/api/episode/e/(?P<ep>[\w-]+)/autoscrim/')
def h_autoscrim(conn, q, body, ep):
    return {'matches': matchmaking.autoscrim(conn, episode=ep, best_of=body.get('best_of'))}


@route('GET', r'/api/team/(?P<ep>[\w-]+)/t/')
def h_teams(conn, q, body, ep):
    teams = list_teams(conn, ep, q.get('ordering', '-rating'), q.get('search'))
    page, size = int(q.get('page', 1)), int(q.get('page_size', 50))
    sl = teams[(page - 1) * size: page * size]
    return {'count': len(teams), 'next': page + 1 if page * size < len(teams) else None,
            'previous': page - 1 if page > 1 else None, 'results': sl}


@route('GET', r'/api/team/(?P<ep>[\w-]+)/t/(?P<tid>\d+)/')
def h_team(conn, q, body, ep, tid):
    return team_public(conn, db.get_team(conn, int(tid), ep))


@route('POST', r'/api/team/(?P<ep>[\w-]+)/t/create/')
def h_team_create(conn, q, body, ep):
    tid = db.create_team(conn, body['name'], episode=ep, status=body.get('status', 'R'))
    return team_public(conn, db.get_team(conn, tid, ep)), 201


@route('GET', r'/api/compete/(?P<ep>[\w-]+)/submission/')
def h_submissions(conn, q, body, ep):
    tid = _team_id(conn, q.get('team_id'), ep)
    qq, args = 'FROM submission WHERE episode=? ', [ep]
    if tid is not None:
        qq += 'AND team=? '
        args.append(tid)
    return paginate(conn, qq, args, 'ORDER BY id DESC', lambda s: submission_json(conn, s), q.get('page'),
                    q.get('page_size'), '')


@route('GET', r'/api/compete/(?P<ep>[\w-]+)/submission/(?P<sid>\d+)/')
def h_submission(conn, q, body, ep, sid):
    s = conn.execute('SELECT * FROM submission WHERE id=?', (int(sid),)).fetchone()
    if s is None:
        raise HttpError(404, 'Not found.')
    return submission_json(conn, s)


@route('POST', r'/api/compete/(?P<ep>[\w-]+)/submission/')
def h_submit(conn, q, body, ep):
    sid = worker.submit(conn, body['team'], body['package'], prebuilt_classes=body.get('prebuilt_classes'),
                        source=body.get('source'), snapshot=body.get('snapshot'),
                        verify=_bool(body.get('verify', False)), description=body.get('description', ''))
    return submission_json(conn, conn.execute('SELECT * FROM submission WHERE id=?', (sid,)).fetchone()), 201


@route('GET', r'/api/compete/(?P<ep>[\w-]+)/request/')
def h_requests(conn, q, body, ep):
    return list_requests(conn, ep, q.get('status'), _team_id(conn, q.get('team_id'), ep))


@route('POST', r'/api/compete/(?P<ep>[\w-]+)/request/')
def h_request(conn, q, body, ep):
    rid, status, match = matchmaking.create_request(
        conn, requested_by=body['requested_by'], requested_to=body['requested_to'],
        is_ranked=_bool(body.get('is_ranked', False)), player_order=body.get('player_order', '?'),
        map_names=body.get('map_names') or [], episode=ep)
    return request_json(conn, conn.execute('SELECT * FROM scrimmage_request WHERE id=?', (rid,)).fetchone()), 201


@route('POST', r'/api/compete/(?P<ep>[\w-]+)/request/(?P<rid>\d+)/accept/')
def h_accept(conn, q, body, ep, rid):
    matchmaking.accept(conn, [int(rid)])
    return None, 204


@route('POST', r'/api/compete/(?P<ep>[\w-]+)/request/(?P<rid>\d+)/reject/')
def h_reject(conn, q, body, ep, rid):
    matchmaking.reject(conn, [int(rid)])
    return None, 204


@route('DELETE', r'/api/compete/(?P<ep>[\w-]+)/request/(?P<rid>\d+)/')
def h_cancel(conn, q, body, ep, rid):
    matchmaking.cancel_request(conn, [int(rid)])
    return None, 204


@route('GET', r'/api/compete/(?P<ep>[\w-]+)/match/(?:scrimmage/)?')
def h_matches(conn, q, body, ep):
    tid = _team_id(conn, q.get('team_id'), ep)
    return list_matches(conn, ep, tid, q.get('status'), q.get('page', 1), q.get('page_size', 50))


@route('GET', r'/api/compete/(?P<ep>[\w-]+)/match/(?P<mid>\d+)/')
def h_match(conn, q, body, ep, mid):
    m = conn.execute('SELECT * FROM match WHERE id=? AND episode=?', (int(mid), ep)).fetchone()
    if m is None:
        raise HttpError(404, 'Not found.')
    return match_json(conn, m, with_logs=_bool(q.get('logs', False)))


@route('POST', r'/api/compete/(?P<ep>[\w-]+)/match/(?P<mid>\d+)/requeue/')
def h_requeue(conn, q, body, ep, mid):
    if not db.requeue(conn, int(mid)):
        raise HttpError(409, 'Match is COMPLETED (or missing); not requeued.')
    return None, 204


@route('GET', r'/api/compete/(?P<ep>[\w-]+)/match/historical_rating/')
def h_hist(conn, q, body, ep):
    tid = _team_id(conn, q.get('team_id'), ep)
    if tid is None:
        raise HttpError(400, 'team_id is required.')
    return historical_rating(conn, tid)


@route('GET', r'/api/compete/(?P<ep>[\w-]+)/match/scrimmaging_record/')
def h_record(conn, q, body, ep):
    tid = _team_id(conn, q.get('team_id'), ep)
    if tid is None:
        raise HttpError(400, 'team_id is required.')
    return scrimmaging_record(conn, tid)


@route('GET', r'/replica/status/?')
def h_status(conn, q, body):
    return queue_status(conn)


@route('GET', r'/replica/ratings/?')
def h_ratings(conn, q, body):
    return ratings_table(conn)


@route('POST', r'/replica/export-games/?')
def h_export(conn, q, body):
    out = body.get('out') or GAMES_CSV
    return {'rows': export_games(conn, out, _bool(body.get('all', False))), 'out': out}


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'galaxy-lite/1'

    head = False   # a HEAD request: headers only

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, payload=None, ctype='application/json', raw=None):
        data = raw if raw is not None else (b'' if payload is None and code == 204 else
                                            json.dumps(payload, indent=1).encode())
        self.send_response(code)
        if code != 204:
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        if code != 204 and not self.head:
            self.wfile.write(data)

    def _send_web(self, r):
        """Send a web.Response; a file body is streamed from one open descriptor (size from fstat)."""
        fh = None
        try:
            if r.file is not None:
                try:
                    fh = open(r.file, 'rb')
                except FileNotFoundError:
                    r = web.not_found()
            size = os.fstat(fh.fileno()).st_size if fh else len(r.body)
            self.send_response(r.code)
            if r.code not in (204, 304):
                self.send_header('Content-Type', r.ctype)
                self.send_header('Content-Length', str(size))
            for k, v in r.headers.items():
                self.send_header(k, v)
            self.end_headers()
            if self.head or r.code in (204, 304):
                return
            if fh:
                shutil.copyfileobj(fh, self.wfile, 1 << 16)
            else:
                self.wfile.write(r.body)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            if fh:
                fh.close()

    def _handle(self, method):
        u = urllib.parse.urlsplit(self.path)
        q = {k: v[-1] for k, v in urllib.parse.parse_qs(u.query).items()}
        self.head = method == 'HEAD'
        if self.head:
            method = 'GET'
        if method == 'GET' and web.is_web_path(u.path):
            try:
                r = web.handle(u.path, q, if_none_match=self.headers.get('If-None-Match'))
            except Exception as e:  # a page bug must not take the server down; the error goes to the service log
                print(f'web: {u.path}: {type(e).__name__}: {e}', file=sys.stderr, flush=True)
                r = web.Response(500, web.layout('Error', '<h1>Server error</h1><p>The page failed to render; '
                                                 'see the replica API service log.</p>'))
            return self._send_web(r)
        p = u.path if u.path.endswith('/') or u.path.startswith('/replica/') else u.path + '/'
        m = re.match(r'^/replica/replay/([0-9a-f-]{36})\.bc23$', u.path)
        if method == 'GET' and m:
            f = db.path('replay', f'{m.group(1)}.bc23')
            if not os.path.isfile(f):
                return self._send(404, {'detail': 'Not found.'})
            with open(f, 'rb') as fh:
                return self._send(200, ctype='application/octet-stream', raw=fh.read())
        body = {}
        if method in ('POST', 'PUT'):
            n = int(self.headers.get('Content-Length') or 0)
            if n:
                try:
                    body = json.loads(self.rfile.read(n) or b'{}')
                except json.JSONDecodeError:
                    return self._send(400, {'detail': 'JSON parse error'})
        conn = db.connect()
        try:
            for meth, rx, fn in ROUTES:
                mm = rx.match(p) if meth == method else None
                if mm:
                    res = fn(conn, q, body, **mm.groupdict())
                    code = 200
                    if isinstance(res, tuple):
                        res, code = res
                    return self._send(code, res)
            return self._send(404, {'detail': 'Not found.'})
        except HttpError as e:
            return self._send(e.code, {'detail': e.detail})
        except matchmaking.RequestError as e:
            return self._send(e.http, {'detail': str(e)})
        except (LookupError, ValueError, KeyError) as e:
            return self._send(400, {'detail': f'{type(e).__name__}: {e}'})
        finally:
            conn.close()

    def do_GET(self):
        self._handle('GET')

    def do_POST(self):
        self._handle('POST')

    def do_DELETE(self):
        self._handle('DELETE')

    def do_HEAD(self):
        self._handle('HEAD')


def serve(host='127.0.0.1', port=8023):
    if not ipaddress.ip_address(host).is_loopback:
        raise SystemExit(f'refusing to bind {host}: the replica API listens on the loopback interface only')
    db.ensure_dirs()
    db.connect().close()   # create the schema before the first request
    httpd = http.server.ThreadingHTTPServer((host, port), Handler)
    print(f'galaxy-lite API and web pages on http://{host}:{port}/ (data {db.home()}; replay viewer '
          f'{"at " + web.viewer_dir() if web.viewer_installed() else "NOT installed: tools/replica/viewer.py install"})',
          flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
