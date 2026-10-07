"""Web pages and the self-hosted replay viewer of galaxy-lite (server-rendered, read-only: GET and HEAD only).

Served by the replica's own http.server (api.serve on 127.0.0.1:8023) behind Caddy (HTTPS, basic auth, GET/HEAD
only; docs/replica/DEPLOY.md). Guide: docs/replica/README.md ("Web pages"); viewer provenance: docs/replica/VIEWER.md.

  /                          the ladder: rank, team, displayed (penalized) rating, trend sparkline, mean, n,
                             ranked match record, games won-lost, last match; our builds (us:...) highlighted
  /team/<id>                 rating history charts (inline SVG) and every match of the team (100 per page)
  /match/<id>                status, both teams, rating changes, per-game rows, Watch and download links
  /matches?status=&page=     matches, newest first (50 per page); status = queued | running | done | error | cancelled
  /replay/<uuid>.bc23        the raw replay file, exactly as the engine wrote it (gzip'd flatbuffers)
  /viewer/visualizer.html?gameSource=/replay/<uuid>.bc23
                             the official Battlecode 2023 web client (3.0.15), self-hosted; the client's own form
                             visualizer.html?/replay/<uuid>.bc23 works too
  /viewer/out/<file>         the client's bundle and images, from $REPLICA_VIEWER_DIR (default $REPLICA_HOME/viewer),
                             installed by tools/replica/viewer.py

Pages carry no scripts and load nothing from elsewhere (inline CSS, inline SVG); a Content-Security-Policy header pins
that. The viewer page runs only the client bundle from /viewer/out/ plus one inline script (hash-pinned), and its
policy allows network requests to this origin only (connect-src 'self'), so the client cannot reach any other host.
No GET handler writes to the database.
"""
import base64
import datetime
import hashlib
import html
import math
import os
import re
import urllib.parse

from . import db
from .db import SaturnStatus

PAGE_SIZE_MATCHES = 50
PAGE_SIZE_TEAM = 100
SPARK_POINTS = 30
REPLAY_RE = re.compile(r'^/replay/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.bc23$')
VIEWER_FILE_RE = re.compile(r'^/viewer/out/([A-Za-z0-9_][A-Za-z0-9_.+=-]{0,80}\.(?:js|png))$')
STATUS_GROUPS = {'queued': ('NEW', 'QUE', 'TRY'), 'running': ('RUN',), 'done': ('OK!',), 'error': ('ERR',),
                 'cancelled': ('CAN',)}
STATUS_LABEL = {'NEW': 'queued', 'QUE': 'queued', 'TRY': 'retrying', 'RUN': 'running', 'OK!': 'done',
                'ERR': 'error', 'CAN': 'cancelled'}
STATUS_ICON = {'queued': '…', 'retrying': '↻', 'running': '▶', 'done': '✓', 'error': '✕',
               'cancelled': '–'}
CTYPES = {'.js': 'application/javascript; charset=utf-8', '.png': 'image/png'}

PAGE_CSP = ("default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; form-action 'self'; "
            "base-uri 'none'; frame-ancestors 'self'")


def viewer_dir():
    return os.path.abspath(os.path.expanduser(os.environ.get('REPLICA_VIEWER_DIR') or db.path('viewer')))


def viewer_installed():
    return os.path.isfile(os.path.join(viewer_dir(), 'out', 'app.js'))


# ---------------------------------------------------------------- responses
class Response:
    """What the HTTP handler sends: a body (bytes) or a file to stream (path), plus headers."""

    def __init__(self, code=200, body=b'', ctype='text/html; charset=utf-8', headers=None, file=None):
        self.code, self.body, self.ctype, self.file = code, body, ctype, file
        self.headers = {'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff'}
        if ctype.startswith('text/html'):
            self.headers['Content-Security-Policy'] = PAGE_CSP
        self.headers.update(headers or {})


def is_web_path(path):
    """True for the paths this module serves (everything else is the JSON API in api.py)."""
    return (path in ('/', '/matches', '/matches/', '/viewer', '/viewer/', '/favicon.ico')
            or path.startswith(('/team/', '/match/', '/replay/', '/viewer/')))


def handle(path, query, connect=None, if_none_match=None):
    """Route one GET/HEAD request. query: {name: last value}. connect: () -> sqlite connection (default db.connect)."""
    connect = connect or db.connect
    try:
        if path == '/favicon.ico':
            return Response(204, ctype='image/x-icon', headers={'Cache-Control': 'private, max-age=86400'})
        if path in ('/viewer', '/viewer/'):
            return Response(302, headers={'Location': '/viewer/visualizer.html'})
        if path == '/viewer/visualizer.html':
            return viewer_page()
        m = VIEWER_FILE_RE.match(path)
        if m:
            return viewer_file(m.group(1))
        m = REPLAY_RE.match(path)
        if m:
            return replay_file(m.group(1), if_none_match)
        conn = connect()
        try:
            if path == '/':
                return page_ladder(conn)
            if path in ('/matches', '/matches/'):
                return page_matches(conn, query)
            m = re.match(r'^/team/(\d+)/?$', path)
            if m:
                return page_team(conn, int(m.group(1)), query)
            m = re.match(r'^/match/(\d+)/?$', path)
            if m:
                return page_match(conn, int(m.group(1)))
        finally:
            conn.close()
        return not_found()
    except NotFound as e:
        return not_found(str(e))


class NotFound(Exception):
    pass


def not_found(what='Not found.'):
    return Response(404, layout('Not found', f'<h1>Not found</h1><p>{esc(what)}</p>'
                                             '<p><a href="/">Back to the ladder</a></p>'))


# ---------------------------------------------------------------- static files: replays and the viewer
def _file_response(path, ctype, cache, if_none_match=None):
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return None
    etag = f'"{st.st_size:x}-{st.st_mtime_ns:x}"'
    headers = {'ETag': etag, 'Cache-Control': cache}
    if if_none_match and etag in [t.strip() for t in if_none_match.split(',')]:
        return Response(304, ctype=ctype, headers=headers)
    return Response(200, ctype=ctype, headers=headers, file=path)


def replay_file(uuid, if_none_match=None):
    r = _file_response(db.path('replay', f'{uuid}.bc23'), 'application/octet-stream', 'private, no-cache',
                       if_none_match)
    if r is None:
        raise NotFound(f'No replay {uuid}.bc23 (the match may not have run yet).')
    return r


def viewer_file(name):
    root = os.path.join(viewer_dir(), 'out')
    r = _file_response(os.path.join(root, name), CTYPES[os.path.splitext(name)[1]], 'private, max-age=86400')
    if r is None:
        raise NotFound(f'No viewer file {name}' + ('' if viewer_installed() else
                                                     ' (the viewer is not installed: tools/replica/viewer.py)'))
    return r


# The 2023 client's visualizer.html (client/visualizer/visualizer.html at 3.0.15) mounts the bundle with the whole
# query string as the match file URL. This page does the same with three changes: no Google Fonts stylesheet (the
# client falls back to a local font), ?gameSource=<url> is accepted besides ?<url>, and only replays of this replica
# (/replay/<uuid>.bc23) are loaded. websocketURL is left at its default (null): the web build never opens a socket.
VIEWER_SCRIPT = """
(function () {
  var q = window.location.search.substring(1);
  var url = q;
  if (q.indexOf('gameSource=') === 0) url = q.substring(11);
  url = decodeURIComponent(url.split('&')[0]);
  var ok = /^\\/replay\\/[0-9a-f-]{36}\\.bc23$/.test(url);
  var config = {};
  if (ok) config.matchFileURL = url;
  window.battleClient = window.battlecode.mount(document.getElementById('client'), config);
})();
"""
VIEWER_SCRIPT_HASH = base64.b64encode(hashlib.sha256(VIEWER_SCRIPT.encode()).digest()).decode()
VIEWER_CSP = ("default-src 'self'; script-src 'self' 'sha256-" + VIEWER_SCRIPT_HASH + "'; "
              "style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self' data:; "
              "frame-src 'self'; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'none'; "
              "frame-ancestors 'self'")


def viewer_page():
    if not viewer_installed():
        return Response(503, layout('Replay viewer', '<h1>Replay viewer not installed</h1><p>Install it on the VM with '
                                    '<code>tools/replica/viewer.py install</code> (docs/replica/VIEWER.md). The raw '
                                    'replay files are still available from each match page.</p>'))
    body = ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Replay viewer - bc23 replica</title>'
            '<style>html,body{height:100%;overflow:hidden;margin:0}</style></head>\n<body>'
            '<div id="altContent"><h1>Loading Battlecode client...</h1></div><div id="client"></div>\n'
            '<script type="text/javascript" src="out/app.js" charset="utf-8"></script>\n'
            f'<script type="text/javascript">{VIEWER_SCRIPT}</script>\n</body></html>\n')
    return Response(200, body.encode(), headers={'Content-Security-Policy': VIEWER_CSP})


def viewer_url(replay_uuid):
    return f'/viewer/visualizer.html?gameSource=/replay/{replay_uuid}.bc23'


# ---------------------------------------------------------------- read models (bulk queries; shared with snapshot.py)
def _blank_record():
    return {'wins': 0, 'losses': 0, 'ties': 0}


def ladder(conn, episode=db.EPISODE, spark_points=SPARK_POINTS):
    """The ladder in galaxy's order (displayed rating desc, then id; api.list_teams '-rating'). Each row: rank, id,
    name, status, us, value, mean, n, ranked_record (W-L-T by summed scores, as api.scrimmaging_record), games
    ({won, lost} as api.game_record), last_match (finish time of the latest completed match), history (value after
    each ranked match, in creation order, as api.historical_rating; the last `spark_points`), matches (all)."""
    teams = conn.execute(
        "SELECT t.id, t.name, t.status, r.value, r.mean, r.n FROM team t JOIN rating r ON r.id=t.rating_id "
        "WHERE t.episode=? AND t.status != 'O' ORDER BY r.value DESC, t.id", (episode,)).fetchall()
    rec = {t['id']: {'Ranked': _blank_record(), 'Unranked': _blank_record()} for t in teams}
    matches = {t['id']: 0 for t in teams}
    for r in conn.execute(
            'SELECT mp.team, m.is_ranked, mp.score AS s, '
            '(SELECT SUM(o.score) FROM match_participant o WHERE o.match=mp.match AND o.team != mp.team) AS os, '
            f'{db.NO_INVISIBLE_MATCH} AS visible '
            'FROM match_participant mp JOIN match m ON m.id=mp.match WHERE m.episode=?', (episode,)):
        if r['team'] not in rec:
            continue
        matches[r['team']] += 1
        if r['s'] is None or r['os'] is None or not r['visible']:
            continue
        k = 'wins' if r['s'] > r['os'] else 'losses' if r['s'] < r['os'] else 'ties'
        rec[r['team']]['Ranked' if r['is_ranked'] else 'Unranked'][k] += 1
    games = {}
    for r in conn.execute(
            "SELECT t, SUM(w) AS w, COUNT(*) AS n FROM ("
            " SELECT team_a AS t, winner='A' AS w FROM game UNION ALL SELECT team_b, winner='B' FROM game) GROUP BY t"):
        games[r['t']] = {'won': r['w'] or 0, 'lost': (r['n'] or 0) - (r['w'] or 0)}
    last = dict(conn.execute(
        "SELECT mp.team, MAX(m.finished) FROM match_participant mp JOIN match m ON m.id=mp.match "
        "WHERE m.status='OK!' AND m.episode=? GROUP BY mp.team", (episode,)).fetchall())
    hist = {}
    for r in conn.execute(
            'SELECT mp.team, m.id AS match, m.created, r.value, r.mean, r.n FROM match_participant mp '
            'JOIN match m ON m.id=mp.match JOIN rating r ON r.id=mp.rating_id '
            f'WHERE m.is_ranked=1 AND m.episode=? AND {db.NO_INVISIBLE_MATCH} ORDER BY mp.team, m.created, m.id',
            (episode,)):
        hist.setdefault(r['team'], []).append(
            {'match': r['match'], 'timestamp': r['created'], 'rating': r['value'], 'mean': r['mean'], 'n': r['n']})
    out = []
    for i, t in enumerate(teams, 1):
        h = hist.get(t['id'], [])
        out.append({'rank': i, 'id': t['id'], 'name': t['name'], 'status': t['status'],
                    'us': t['name'].startswith('us:'), 'value': t['value'], 'mean': t['mean'], 'n': t['n'],
                    'ranked_record': rec[t['id']]['Ranked'], 'unranked_record': rec[t['id']]['Unranked'],
                    'games': games.get(t['id'], {'won': 0, 'lost': 0}), 'last_match': last.get(t['id']),
                    'matches': matches[t['id']], 'history': h[-spark_points:] if spark_points else h,
                    'history_len': len(h)})
    return out


def team_history(conn, team_id):
    """Every ranked participation with a final rating, in match creation order (api.historical_rating)."""
    return [dict(r) for r in conn.execute(
        'SELECT m.id AS match, m.created AS timestamp, r.value AS rating, r.mean, r.n FROM match_participant mp '
        'JOIN match m ON m.id=mp.match JOIN rating r ON r.id=mp.rating_id '
        f'WHERE mp.team=? AND m.is_ranked=1 AND {db.NO_INVISIBLE_MATCH} ORDER BY m.created, m.id', (team_id,))]


def match_rows(conn, ms):
    """Rows for match lists: the match fields plus participants (player_index order) with names, scores and old/new
    ratings (old = the rating just before the match, as rating.get_old_rating: none before a team's first match means
    the default Rating(), an unrated previous participation means unknown), maps, and whether the replay exists."""
    ms = list(ms)
    if not ms:
        return []
    ids = [m['id'] for m in ms]
    q = ','.join('?' * len(ids))
    parts = {}
    for p in conn.execute(
            'SELECT mp.*, t.name AS teamname, r.value AS new_value, r.mean AS new_mean, '
            'prev.id AS prev_id, prev.rating_id AS prev_rating, pr.value AS old_value, pr.mean AS old_mean '
            'FROM match_participant mp JOIN team t ON t.id=mp.team LEFT JOIN rating r ON r.id=mp.rating_id '
            'LEFT JOIN match_participant prev ON prev.id=mp.previous_participation '
            'LEFT JOIN rating pr ON pr.id=prev.rating_id '
            f'WHERE mp.match IN ({q}) ORDER BY mp.match, mp.player_index, mp.id', ids):
        if p['previous_participation'] is None:
            old_value, old_mean = 0.0, 1500.0
        elif p['prev_rating'] is None:
            old_value, old_mean = None, None
        else:
            old_value, old_mean = p['old_value'], p['old_mean']
        parts.setdefault(p['match'], []).append(
            {'team': p['team'], 'teamname': p['teamname'], 'player_index': p['player_index'], 'score': p['score'],
             'submission': p['submission'], 'rating': p['new_value'], 'mean': p['new_mean'],
             'old_rating': old_value, 'old_mean': old_mean})
    maps = {}
    for r in conn.execute('SELECT mm.match, map.name FROM match_map mm JOIN map ON map.id=mm.map '
                          f'WHERE mm.match IN ({q}) ORDER BY mm.match, mm.sort, mm.id', ids):
        maps.setdefault(r['match'], []).append(r['name'])
    out = []
    for m in ms:
        d = {k: m[k] for k in ('id', 'status', 'created', 'finished', 'is_ranked', 'source', 'num_failures',
                               'replay', 'alternate_order', 'worker', 'claimed_at')}
        d['participants'] = parts.get(m['id'], [])
        d['maps'] = maps.get(m['id'], [])
        d['has_replay'] = os.path.isfile(db.path('replay', f'{m["replay"]}.bc23'))
        d['watchable'] = d['has_replay'] and m['status'] == SaturnStatus.COMPLETED
        out.append(d)
    return out


def summary(conn):
    c = db.status_counts(conn, 'match')
    return {'teams': conn.execute("SELECT COUNT(*) FROM team WHERE status != 'O'").fetchone()[0],
            'games': conn.execute('SELECT COUNT(*) FROM game').fetchone()[0],
            'queued': sum(c.get(s, 0) for s in STATUS_GROUPS['queued']), 'running': c.get('RUN', 0),
            'done': c.get('OK!', 0), 'error': c.get('ERR', 0), 'cancelled': c.get('CAN', 0)}


# ---------------------------------------------------------------- formatting
esc = html.escape


def tzinfo():
    name = os.environ.get('REPLICA_TZ', 'America/Los_Angeles')
    try:
        import zoneinfo
        return zoneinfo.ZoneInfo(name)
    except Exception:
        return datetime.timezone.utc


def parse_ts(s):
    if not s:
        return None
    t = datetime.datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)


def fmt_time(s, with_zone=False):
    t = parse_ts(s)
    if t is None:
        return ''
    t = t.astimezone(tzinfo())
    out = f'{t:%b} {t.day} {t:%H:%M}'
    return out + f' {t:%Z}' if with_zone else out


def fmt_ago(s, now=None):
    t = parse_ts(s)
    if t is None:
        return ''
    secs = max(0, ((now or datetime.datetime.now(datetime.timezone.utc)) - t).total_seconds())
    if secs < 90:
        return 'just now'
    if secs < 5400:
        return f'{round(secs / 60)} min ago'
    if secs < 48 * 3600:
        return f'{round(secs / 3600)} h ago'
    return f'{round(secs / 86400)} d ago'


def num(v, nd=1):
    return '–' if v is None else f'{v:.{nd}f}'.replace('-', '−')


def signed(v, nd=1):
    if v is None:
        return ''
    return ('+' if v >= 0 else '−') + f'{abs(v):.{nd}f}'


def record(r):
    return f'{r["wins"]}-{r["losses"]}-{r["ties"]}'


def chip(status):
    label = STATUS_LABEL.get(status, status)
    return (f'<span class="chip st-{esc(label)}"><span class="ic" aria-hidden="true">{STATUS_ICON.get(label, "")}'
            f'</span>{esc(label)}</span>')


def breakable(name):
    """Escaped team name with line-break opportunities after '.', ':' and '_' (no mid-word breaks on phones)."""
    return re.sub(r'([.:_])', r'\1<wbr>', esc(name))


def team_link(tid, name):
    if name.startswith('us:'):
        return f'<a class="us" href="/team/{int(tid)}">{breakable(name)}</a> <span class="badge">us</span>'
    return f'<a href="/team/{int(tid)}">{breakable(name)}</a>'


def pager(base, page, total, size, extra=None):
    pages = max(1, math.ceil(total / size))
    if pages <= 1:
        return ''

    def href(p):
        qs = dict(extra or {})
        qs['page'] = p
        return esc(base + '?' + urllib.parse.urlencode({k: v for k, v in qs.items() if v not in (None, '')}))
    prev = f'<a href="{href(page - 1)}">← newer</a>' if page > 1 else '<span class="muted">← newer</span>'
    nxt = f'<a href="{href(page + 1)}">older →</a>' if page < pages else '<span class="muted">older →</span>'
    return f'<nav class="pager">{prev}<span>page {page} of {pages}</span>{nxt}</nav>'


CSS = """
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--border:rgba(11,11,11,.10);--s1:#2a78d6;--us:rgba(42,120,214,.10);--good:#0ca30c;
--bad:#d03b3b;--goodtxt:#006300;--badtxt:#b42c2c;--link:#1c5cab;--wash:rgba(11,11,11,.04)}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;
--ink2:#c3c2b7;--grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,.10);--s1:#3987e5;--us:rgba(57,135,229,.18);
--goodtxt:#0ca30c;--badtxt:#e66767;--link:#86b6ef;--wash:rgba(255,255,255,.05)}}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
header{background:var(--surface);border-bottom:1px solid var(--border)}
header .in{max-width:1100px;margin:0 auto;padding:10px 16px;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline}
header .brand{font-weight:700;color:var(--ink)}header nav a{margin-right:14px}header nav a.on{color:var(--ink);font-weight:600}
header .q{margin-left:auto;color:var(--ink2);font-size:13px}
main{max-width:1100px;margin:0 auto;padding:16px}
h1{font-size:22px;margin:4px 0 6px}h2{font-size:17px;margin:22px 0 8px}
p{margin:6px 0}.muted{color:var(--muted)}.sub{color:var(--ink2);font-size:13px}
.wrap{overflow-x:auto;border:1px solid var(--border);border-radius:8px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{padding:6px 9px;border-bottom:1px solid var(--grid);text-align:left;white-space:nowrap;vertical-align:middle}
tr:last-child td{border-bottom:none}
th{font-size:12px;color:var(--ink2);font-weight:600}
.num{text-align:right}td.team{white-space:normal;overflow-wrap:break-word}
td.maps{white-space:normal;font-size:13px;color:var(--ink2)}
tr.us td{background:var(--us)}a.us{font-weight:600}
.badge{display:inline-block;font-size:11px;line-height:1;padding:2px 5px;border-radius:4px;border:1px solid var(--s1);
color:var(--ink);margin-left:4px;vertical-align:1px}
.chip{display:inline-flex;gap:4px;align-items:center;font-size:13px}
.chip .ic{display:inline-block;width:16px;height:16px;border-radius:50%;font-size:10px;line-height:16px;
text-align:center;color:#fff;background:var(--muted)}
.st-done .ic{background:var(--good)}.st-error .ic{background:var(--bad)}.st-running .ic{background:var(--s1)}
.res-W{color:var(--goodtxt);font-weight:600}.res-L{color:var(--badtxt);font-weight:600}
.btn{display:inline-block;padding:6px 12px;border-radius:6px;background:var(--s1);color:#fff;font-weight:600}
.btn:hover{text-decoration:none;filter:brightness(1.08)}
.btn.sec{background:transparent;color:var(--link);border:1px solid var(--border)}
.stats{display:flex;flex-wrap:wrap;gap:8px 26px;margin:10px 0}
.stats div{min-width:84px}.stats b{display:block;font-size:20px;font-weight:600}.stats span{font-size:12px;color:var(--ink2)}
.filters{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.filters a{padding:3px 10px;border:1px solid var(--border);border-radius:14px;font-size:13px;background:var(--surface)}
.filters a.on{border-color:var(--s1);color:var(--ink);font-weight:600}
.pager{display:flex;gap:18px;align-items:center;margin:12px 0;font-size:14px}
.chart{overflow-x:auto;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:6px 4px}
.chart svg{display:block;width:100%;min-width:600px;height:auto}
svg .ln{fill:none;stroke:var(--s1);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
svg .dot{fill:var(--s1);stroke:var(--surface);stroke-width:2}
svg .grid{stroke:var(--grid);stroke-width:1}svg .base{stroke:var(--axis);stroke-width:1}
svg text{fill:var(--muted);font-size:13px;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.only-sm{display:none}
svg .hit{fill:transparent}svg .hit:hover{fill:var(--wash)}
svg.spark{width:96px;height:24px;display:block}
details{margin:10px 0}pre{white-space:pre-wrap;font-size:12px;background:var(--surface);border:1px solid var(--border);
border-radius:6px;padding:8px;max-height:420px;overflow:auto}
footer{max-width:1100px;margin:0 auto;padding:8px 16px 28px;color:var(--muted);font-size:12px}
@media (max-width:640px){.hide-sm{display:none}body{font-size:14px}th,td{padding:5px 5px}main{padding:12px}
th.rec{white-space:normal}svg.spark{width:52px}.only-lg{display:none}.only-sm{display:block}.only-sm .chart svg{min-width:0}}
"""

ICON = ("data:image/svg+xml," + urllib.parse.quote(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><rect width='16' height='16' rx='3' fill='#2a78d6'/>"
    "<path d='M3 12 L6 8 L9 10 L13 4' stroke='#fff' stroke-width='2' fill='none'/></svg>", safe=''))


def layout(title, body, active=None, status=None):
    def nav(href, label, key):
        return f'<a href="{href}"{" class=on" if active == key else ""}>{label}</a>'
    q = ''
    if status is not None:
        q = (f'<span class="q">{status["running"]} running · {status["queued"]} queued'
             + (f' · {status["error"]} errors' if status['error'] else '') + '</span>')
    now = fmt_time(db.now(), with_zone=True)
    return ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="robots" content="noindex, nofollow">'
            f'<title>{esc(title)} - bc23 replica</title><link rel="icon" href="{ICON}">'
            f'<style>{CSS}</style></head>\n<body><header><div class="in"><span class="brand">bc23 replica</span>'
            f'<nav>{nav("/", "Ladder", "ladder")}{nav("/matches", "Matches", "matches")}</nav>{q}</div></header>\n'
            f'<main>{body}</main>\n<footer>galaxy-lite, a private replica of the Battlecode 2023 ladder '
            f'(Penalized Elo, autoscrim, best of 3). Rendered {esc(now)}. Read-only.</footer></body></html>\n'
            ).encode()


# ---------------------------------------------------------------- SVG charts
def nice_ticks(lo, hi, count=5):
    if hi <= lo:
        hi = lo + 1
    raw = (hi - lo) / max(1, count - 1)
    mag = 10 ** math.floor(math.log10(raw))
    step = next(s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw)
    start = math.floor(lo / step) * step
    ticks, t = [], start
    while t <= hi + step * 0.5:
        ticks.append(round(t, 6))
        t += step
        if t > hi and ticks[-1] >= hi:
            break
    return ticks


def sparkline(values, width=96, height=24, pad=3):
    """A one-series sparkline: 2px line, end dot. Empty when there are fewer than 2 values."""
    if len(values) < 2:
        return ''
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    xs = [pad + (width - 2 * pad) * i / (len(values) - 1) for i in range(len(values))]
    ys = [height - pad - (height - 2 * pad) * (v - lo) / span for v in values]
    pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in zip(xs, ys))
    return (f'<svg class="spark" viewBox="0 0 {width} {height}" role="img" aria-label="rating trend">'
            f'<polyline class="ln" points="{pts}"/><circle class="dot" cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="3"/>'
            '</svg>')


def line_chart(points, label, ymin=None, width=900, height=250):
    """points: [(x_label, value, tooltip)] in order. One series (2px line), hairline grid, y ticks, end dot and
    value label, per-point hover targets with native tooltips (<title>)."""
    if not points:
        return '<p class="muted">No rated ranked matches yet.</p>'
    left, right, top, bottom = 56, 70, 14, 30
    vals = [p[1] for p in points]
    lo = min(vals) if ymin is None else min(ymin, min(vals))
    hi = max(vals)
    if hi - lo < 10:
        lo, hi = lo - 5, hi + 5
    ticks = nice_ticks(lo, hi)
    lo, hi = min(ticks[0], lo), max(ticks[-1], hi)
    pw, ph = width - left - right, height - top - bottom
    n = len(points)
    x = (lambda i: left + pw / 2) if n == 1 else (lambda i: left + pw * i / (n - 1))
    y = lambda v: top + ph - ph * (v - lo) / (hi - lo)
    out = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">']
    for t in ticks:
        out.append(f'<line class="grid" x1="{left}" x2="{width - right}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>'
                   f'<text x="{left - 6}" y="{y(t) + 4:.1f}" text-anchor="end">{num(t, 0)}</text>')
    out.append(f'<line class="base" x1="{left}" x2="{width - right}" y1="{top + ph}" y2="{top + ph}"/>')
    for i in sorted({0, n - 1, *(round((n - 1) * k / 4) for k in range(1, 4))}):
        out.append(f'<text x="{x(i):.1f}" y="{height - 9}" text-anchor="middle">{esc(str(points[i][0]))}</text>')
    pts = ' '.join(f'{x(i):.1f},{y(v):.1f}' for i, (_, v, _) in enumerate(points))
    if n > 1:
        out.append(f'<polyline class="ln" points="{pts}"/>')
    half = max(3.0, pw / max(1, n - 1) / 2)
    for i, (_, v, tip) in enumerate(points):
        x0, x1 = max(left, x(i) - half), min(width - right, x(i) + half)
        out.append(f'<rect class="hit" x="{x0:.1f}" y="{top}" width="{x1 - x0:.1f}" height="{ph}">'
                   f'<title>{esc(tip)}</title></rect>')
    xe, ye = x(n - 1), y(vals[-1])
    out.append(f'<circle class="dot" cx="{xe:.1f}" cy="{ye:.1f}" r="4"/>'
               f'<text x="{xe + 8:.1f}" y="{ye + 4:.1f}" style="fill:var(--ink)">{num(vals[-1])}</text></svg>')
    return '<div class="chart">' + ''.join(out) + '</div>'


def chart(points, label, ymin=None):
    """The same chart twice: a wide one for desktops and a narrow one for phones (CSS shows one), so the axis text
    stays readable at both sizes."""
    return (f'<div class="only-lg">{line_chart(points, label, ymin)}</div>'
            f'<div class="only-sm">{line_chart(points, label, ymin, width=420, height=230)}</div>')


# ---------------------------------------------------------------- pages
def page_ladder(conn):
    rows = ladder(conn)
    st = summary(conn)
    now = datetime.datetime.now(datetime.timezone.utc)
    body = ['<h1>Ladder</h1>',
            f'<p class="sub">{st["teams"]} teams · {st["done"]} matches done · {st["games"]} games. '
            'Ranked by the displayed rating, galaxy\'s Penalized Elo: mean − 1500·0.85<sup>n</sup>, '
            'so a team climbs from 0 over its first ~20 rated matches. '
            f'Trend: displayed rating over the last {SPARK_POINTS} ranked matches. Ranked W-L-T counts ranked '
            'matches; Games W-L counts every game, ranked and unranked.</p>']
    if not rows:
        body.append('<p class="muted">No teams yet.</p>')
        return Response(200, layout('Ladder', ''.join(body), 'ladder', st))
    body.append('<div class="wrap"><table><thead><tr><th class="num">#</th><th>Team</th><th class="num">Rating</th>'
                '<th>Trend</th><th class="num hide-sm">Mean</th><th class="num hide-sm">n</th>'
                '<th class="rec" title="ranked matches won-lost-tied">Ranked W-L-T</th><th class="hide-sm" title="games won-lost, ranked and unranked">Games W-L</th><th class="hide-sm">Last match</th></tr></thead>'
                '<tbody>')
    for r in rows:
        spark = sparkline([0.0] + [h['rating'] for h in r['history']] if r['history_len'] <= SPARK_POINTS
                          else [h['rating'] for h in r['history']])
        status = '' if r['status'] == 'R' else f' <span class="muted">({esc({"X": "inactive", "S": "staff"}.get(r["status"], r["status"]))})</span>'
        last = (f'<span title="{esc(fmt_time(r["last_match"], True))}">{esc(fmt_ago(r["last_match"], now))}</span>'
                if r['last_match'] else '<span class="muted">–</span>')
        body.append(
            f'<tr{" class=us" if r["us"] else ""}><td class="num">{r["rank"]}</td>'
            f'<td class="team">{team_link(r["id"], r["name"])}{status}</td><td class="num"><b>{num(r["value"])}</b></td>'
            f'<td>{spark}</td><td class="num hide-sm">{num(r["mean"])}</td><td class="num hide-sm">{r["n"]}</td>'
            f'<td>{record(r["ranked_record"])}</td><td class="hide-sm">{r["games"]["won"]}-{r["games"]["lost"]}</td>'
            f'<td class="hide-sm">{last}</td></tr>')
    body.append('</tbody></table></div>')
    return Response(200, layout('Ladder', ''.join(body), 'ladder', st))


def _status_where(group):
    if group in STATUS_GROUPS:
        sts = STATUS_GROUPS[group]
        return f'm.status IN ({",".join("?" * len(sts))})', list(sts)
    return None, []


def _int(v, default=1):
    try:
        return max(1, int(v))
    except (TypeError, ValueError):
        return default


def match_table(rows, perspective=None):
    """perspective: a team id -> columns opponent / score / result / rating change for that team."""
    if not rows:
        return '<p class="muted">No matches.</p>'
    out = ['<div class="wrap"><table><thead><tr><th class="num">Match</th><th>Status</th>']
    if perspective is None:
        out.append('<th>Team A</th><th class="num">Score</th><th>Team B</th>')
    else:
        out.append('<th>Opponent</th><th class="num">Score</th><th>Result</th><th class="num">Rating Δ</th>'
                   '<th class="num hide-sm">μ Δ</th>')
    out.append('<th class="hide-sm">Maps</th><th class="hide-sm">Type</th><th>Time</th><th>Replay</th></tr></thead><tbody>')
    for m in rows:
        ps = m['participants']
        when = m['finished'] or m['created']
        cells = [f'<td class="num"><a href="/match/{m["id"]}">{m["id"]}</a></td><td>{chip(m["status"])}</td>']
        us_row = False
        if perspective is None or len(ps) != 2:
            a, b = (ps + [None, None])[:2]
            sa = '?' if a is None or a['score'] is None else a['score']
            sb = '?' if b is None or b['score'] is None else b['score']
            us_row = any(p and p['teamname'].startswith('us:') for p in (a, b))
            cells.append(f'<td class="team">{team_link(a["team"], a["teamname"]) if a else ""}</td>'
                         f'<td class="num">{sa}–{sb}</td>'
                         f'<td class="team">{team_link(b["team"], b["teamname"]) if b else ""}</td>')
        else:
            me = next(p for p in ps if p['team'] == perspective)
            op = next(p for p in ps if p is not me)
            if me['score'] is None or op['score'] is None:
                score, res = '–', ''
            else:
                score = f'{me["score"]}–{op["score"]}'
                r = 'W' if me['score'] > op['score'] else 'L' if me['score'] < op['score'] else 'T'
                res = f'<span class="res-{r}">{r}</span>'
            delta = dmean = ''
            if m['is_ranked'] and me['rating'] is not None and me['old_rating'] is not None:
                delta = (f'<span title="{num(me["old_rating"])} → {num(me["rating"])}">'
                         f'{signed(me["rating"] - me["old_rating"])}</span>')
                dmean = (f'<span title="μ {num(me["old_mean"])} → {num(me["mean"])}">'
                         f'{signed(me["mean"] - me["old_mean"])}</span>')
            cells.append(f'<td class="team">{team_link(op["team"], op["teamname"])}</td><td class="num">{score}</td>'
                         f'<td>{res}</td><td class="num">{delta}</td><td class="num hide-sm">{dmean}</td>')
        cells.append(f'<td class="maps hide-sm">{esc(", ".join(m["maps"]))}</td>'
                     f'<td class="hide-sm">{"ranked" if m["is_ranked"] else "unranked"}</td>'
                     f'<td title="{esc(fmt_time(when, True))}">{esc(fmt_time(when))}</td>'
                     + (f'<td><a href="{esc(viewer_url(m["replay"]))}">Watch</a></td>' if m['watchable']
                        else '<td class="muted">–</td>'))
        out.append(f'<tr{" class=us" if us_row and perspective is None else ""}>' + ''.join(cells) + '</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def page_matches(conn, query):
    group = query.get('status') or ''
    if group and group not in STATUS_GROUPS:
        group = ''
    team = query.get('team') or ''
    where, args = ['m.episode=?'], [db.EPISODE]
    w, a = _status_where(group)
    if w:
        where.append(w)
        args += a
    tname = None
    if team:
        t = conn.execute('SELECT id, name FROM team WHERE id=? OR name=?',
                         (int(team) if team.isdigit() else -1, team)).fetchone()
        if t is None:
            raise NotFound(f'No team {team!r}.')
        tname = t['name']
        where.append('EXISTS (SELECT 1 FROM match_participant WHERE match=m.id AND team=?)')
        args.append(t['id'])
    page = _int(query.get('page'))
    total = conn.execute(f'SELECT COUNT(*) FROM match m WHERE {" AND ".join(where)}', args).fetchone()[0]
    ms = conn.execute(f'SELECT m.* FROM match m WHERE {" AND ".join(where)} ORDER BY m.id DESC LIMIT ? OFFSET ?',
                      args + [PAGE_SIZE_MATCHES, (page - 1) * PAGE_SIZE_MATCHES]).fetchall()
    st = summary(conn)
    filt = ['<nav class="filters">']
    for key, label in [('', f'all'), ('queued', f'queued {st["queued"]}'), ('running', f'running {st["running"]}'),
                       ('done', f'done {st["done"]}'), ('error', f'error {st["error"]}'),
                       ('cancelled', f'cancelled {st["cancelled"]}')]:
        qs = urllib.parse.urlencode({k: v for k, v in (('status', key), ('team', team)) if v})
        filt.append(f'<a href="/matches{"?" + esc(qs) if qs else ""}"{" class=on" if key == group else ""}>{label}</a>')
    filt.append('</nav>')
    title = 'Matches' + (f' of {tname}' if tname else '')
    body = [f'<h1>{esc(title)}</h1>', f'<p class="sub">{total} matches, newest first. Queued includes retries; a match '
            'that fails 5 times becomes an error.</p>', ''.join(filt),
            match_table(match_rows(conn, ms)),
            pager('/matches', page, total, PAGE_SIZE_MATCHES, {'status': group, 'team': team})]
    return Response(200, layout(title, ''.join(body), 'matches', st))


def page_team(conn, tid, query):
    t = conn.execute('SELECT * FROM team WHERE id=?', (tid,)).fetchone()
    if t is None:
        raise NotFound(f'No team {tid}.')
    lad = ladder(conn, spark_points=1)
    row = next((r for r in lad if r['id'] == tid), None)
    sub = conn.execute('SELECT * FROM submission WHERE team=? AND accepted=1 ORDER BY id DESC LIMIT 1',
                       (tid,)).fetchone()
    hist = team_history(conn, tid)
    page = _int(query.get('page'))
    total = conn.execute('SELECT COUNT(*) FROM match m WHERE EXISTS (SELECT 1 FROM match_participant '
                         'WHERE match=m.id AND team=?)', (tid,)).fetchone()[0]
    ms = conn.execute('SELECT m.* FROM match m WHERE EXISTS (SELECT 1 FROM match_participant WHERE match=m.id AND '
                      'team=?) ORDER BY m.id DESC LIMIT ? OFFSET ?',
                      (tid, PAGE_SIZE_TEAM, (page - 1) * PAGE_SIZE_TEAM)).fetchall()
    r = db.get_rating(conn, t['rating_id'])
    us = t['name'].startswith('us:')
    body = [f'<h1>{esc(t["name"])}{" <span class=badge>us</span>" if us else ""}</h1>']
    meta = []
    if sub is not None:
        meta.append(f'active submission {sub["id"]} (package <code>{esc(sub["package"])}</code>, '
                    f'{esc(fmt_time(sub["created"], True))})')
    else:
        meta.append('no accepted submission')
    if t['status'] != 'R':
        meta.append({'X': 'inactive', 'S': 'staff (unrated)', 'O': 'invisible'}.get(t['status'], t['status']))
    body.append(f'<p class="sub">{" · ".join(meta)}</p>')
    stats = [('rank', f'{row["rank"]} of {len(lad)}' if row else '–'),
             ('rating (displayed)', num(r['value'])), ('mean μ', num(r['mean'])), ('rated matches n', r['n'])]
    if row:
        stats += [('ranked W-L-T', record(row['ranked_record'])),
                  ('games W-L', f'{row["games"]["won"]}-{row["games"]["lost"]}')]
    body.append('<div class="stats">' + ''.join(f'<div><b>{v}</b><span>{esc(k)}</span></div>' for k, v in stats)
                + '</div>')
    body.append('<h2>Displayed rating after each ranked match</h2>')
    pts = [('start', 0.0, 'before the first match: 0.0')] + [
        (i + 1, h['rating'], f'match {h["match"]} ({fmt_time(h["timestamp"])}): {num(h["rating"])}, n={h["n"]}')
        for i, h in enumerate(hist)]
    body.append(chart(pts if hist else [], 'displayed rating history', ymin=0))
    body.append('<h2>Mean μ (no penalty)</h2>')
    pts = [('start', 1500.0, 'before the first match: 1500.0')] + [
        (i + 1, h['mean'], f'match {h["match"]} ({fmt_time(h["timestamp"])}): μ {num(h["mean"])}')
        for i, h in enumerate(hist)]
    body.append(chart(pts if hist else [], 'mean rating history'))
    body.append('<p class="sub">x axis: rated ranked matches in creation order (the order galaxy applies ratings). '
                'Hover a point for its match.</p>')
    body.append(f'<h2>Matches ({total})</h2>')
    body.append(match_table(match_rows(conn, ms), perspective=tid))
    body.append(pager(f'/team/{tid}', page, total, PAGE_SIZE_TEAM))
    return Response(200, layout(t['name'], ''.join(body), None, summary(conn)))


def page_match(conn, mid):
    m = conn.execute('SELECT * FROM match WHERE id=?', (mid,)).fetchone()
    if m is None:
        raise NotFound(f'No match {mid}.')
    d = match_rows(conn, [m])[0]
    games = conn.execute('SELECT * FROM game WHERE match=? ORDER BY idx', (mid,)).fetchall()
    names = {p['player_index']: p['teamname'] for p in d['participants']}
    body = [f'<h1>Match {mid} {chip(m["status"])}</h1>']
    meta = ['ranked' if m['is_ranked'] else 'unranked', f'source {esc(m["source"])}',
            f'created {esc(fmt_time(m["created"], True))}']
    if m['finished']:
        meta.append(f'finished {esc(fmt_time(m["finished"], True))}')
    if m['num_failures']:
        meta.append(f'{m["num_failures"]} failed attempts (an error at {db.SATURN_MAX_FAILURES})')
    if m['alternate_order']:
        meta.append('spawn sides alternate between games')
    body.append(f'<p class="sub">{" · ".join(meta)}</p>')
    if m['status'] == SaturnStatus.RUNNING:
        body.append(f'<p>Running on worker <code>{esc(m["worker"] or "?")}</code> since '
                    f'{esc(fmt_time(m["claimed_at"], True))}.</p>')
    links = []
    if d['watchable']:
        links.append(f'<a class="btn" href="{esc(viewer_url(m["replay"]))}">Watch replay</a>')
    if d['has_replay'] and m['status'] == SaturnStatus.COMPLETED:
        links.append(f'<a class="btn sec" href="/replay/{esc(m["replay"])}.bc23" download="match-{mid}.bc23">'
                     'Download .bc23</a>')
    links.append(f'<a class="btn sec" href="/api/compete/{db.EPISODE}/match/{mid}/">JSON</a>')
    body.append('<p>' + ' '.join(links) + '</p>')
    if d['watchable']:
        body.append('<p class="sub">The replay holds all games of the match; pick a game in the viewer\'s queue tab.</p>')
    body.append('<h2>Teams</h2><div class="wrap"><table><thead><tr><th>Code</th><th>Team</th><th class="num">Score</th>'
                '<th class="num hide-sm">Rating before</th><th class="num">after</th><th class="num">Δ</th>'
                '<th class="num hide-sm">μ before</th><th class="num hide-sm">after</th>'
                '<th class="num hide-sm">Δμ</th><th class="hide-sm">Submission</th></tr></thead><tbody>')
    for p in d['participants']:
        rated = p['rating'] is not None and p['old_rating'] is not None
        body.append(
            f'<tr{" class=us" if p["teamname"].startswith("us:") else ""}><td>{"AB"[p["player_index"]] if p["player_index"] in (0, 1) else p["player_index"]}</td>'
            f'<td class="team">{team_link(p["team"], p["teamname"])}</td>'
            f'<td class="num">{"–" if p["score"] is None else p["score"]}</td>'
            f'<td class="num hide-sm">{num(p["old_rating"])}</td><td class="num">{num(p["rating"])}</td>'
            f'<td class="num">{signed(p["rating"] - p["old_rating"]) if rated else ""}</td>'
            f'<td class="num hide-sm">{num(p["old_mean"])}</td><td class="num hide-sm">{num(p["mean"])}</td>'
            f'<td class="num hide-sm">{signed(p["mean"] - p["old_mean"]) if rated else ""}</td>'
            f'<td class="hide-sm">{p["submission"]}</td></tr>')
    body.append('</tbody></table></div>')
    if m['is_ranked'] and any(p['rating'] is None for p in d['participants']) and m['status'] == 'OK!':
        body.append('<p class="sub">Ratings are applied in match-creation order: this match is rated once each '
                    'team\'s earlier matches are.</p>')
    body.append('<h2>Games</h2>')
    if games:
        body.append('<div class="wrap"><table><thead><tr><th class="num">#</th><th>Map</th><th>Spawns</th>'
                    '<th>Winner</th><th class="num">Rounds</th><th class="hide-sm">Reason</th></tr></thead><tbody>')
        for g in games:
            w = names.get({'A': 0, 'B': 1}.get(g['winner']), '?')
            body.append(f'<tr><td class="num">{g["idx"] + 1}</td><td>{esc(g["map"])}</td>'
                        f'<td>{"swapped" if g["reversed"] else "normal"}</td>'
                        f'<td class="team">{esc(g["winner"] or "?")} · {breakable(w)}</td>'
                        f'<td class="num">{"" if g["round"] is None else g["round"]}</td>'
                        f'<td class="maps hide-sm">{esc(g["reason"] or "")}</td></tr>')
        body.append('</tbody></table></div><p class="sub">Code A is the first team above. With alternating order, '
                    'games 2, 4, ... swap the spawn sides while the code keeps its A/B label.</p>')
    else:
        body.append(f'<p class="muted">No game results yet. Maps: {esc(", ".join(d["maps"]))}.</p>')
    if m['logs'] and m['status'] in (SaturnStatus.ERRORED, SaturnStatus.RETRY, SaturnStatus.CANCELLED):
        body.append(f'<details><summary>Job log</summary><pre>{esc(m["logs"][-20000:])}</pre></details>')
    return Response(200, layout(f'Match {mid}', ''.join(body), 'matches', summary(conn)))
