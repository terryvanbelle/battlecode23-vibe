"""SQLite schema and data helpers for galaxy-lite.

Table, column and enum names follow siarnaq (backend/siarnaq/api/{episodes,teams,compete}/models.py) so code ports
one to one. Differences, all deliberate:
  * team holds TeamProfile's fields (rating_id, auto_accept_reject_*): one row per team instead of two tables.
  * submission gains source_path / binary_path / prebuilt_classes (local files instead of GCS objects).
  * match gains source ('request'|'autoscrim'|'manual'), request_id, claimed_at, worker, finished (bookkeeping for
    the local worker and the stale-RUN reaper); match.replay is the replay uuid as in galaxy.
  * game is new: one row per game of a match (map, code-A team, reversed spawn flag, winner, round, reason).
  * episode gains autoscrim_best_of and enforce_rules (galaxy hard-codes best of 3 and always enforces the rules).
Data dir: $REPLICA_HOME (default: /home/bcreplica/replica when it holds a DB, else ~/replica) with replica.db,
replay/, sub/, logs/ and viewer/. Repo: $REPLICA_REPO (see REPO).
"""
import contextlib
import datetime
import os
import sqlite3
import uuid

# The repo checkout that holds tools/lib.sh (engine_cp, compile_src), tools/maps.txt, tools/field.txt, engine/,
# build/classes and progress/. Default: the checkout this code sits in; REPLICA_REPO overrides it (for example when
# the code runs from an installed copy).
REPO = os.path.abspath(os.path.expanduser(os.environ.get('REPLICA_REPO') or
                                          os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
TOOLS = os.path.join(REPO, 'tools')
EPISODE = 'bc23'


# ---------------------------------------------------------------- enums (galaxy TextChoices values)
class SaturnStatus:
    CREATED = 'NEW'      # created, not yet queued
    QUEUED = 'QUE'       # waiting for a worker
    RUNNING = 'RUN'      # claimed by a worker
    RETRY = 'TRY'        # failed or interrupted, waiting to be retried
    COMPLETED = 'OK!'    # finished successfully
    ERRORED = 'ERR'      # failed SATURN_MAX_FAILURES times; no more retries
    CANCELLED = 'CAN'    # cancelled by a client
    FINALIZED = (COMPLETED, ERRORED, CANCELLED)
    ACTIVE = (CREATED, QUEUED, RUNNING, RETRY)


class TeamStatus:
    REGULAR = 'R'
    INACTIVE = 'X'
    STAFF = 'S'
    INVISIBLE = 'O'
    ALL = (REGULAR, INACTIVE, STAFF, INVISIBLE)


class ScrimmageRequestStatus:
    PENDING = 'P'
    ACCEPTED = 'Y'
    REJECTED = 'N'


class PlayerOrder:
    REQUESTER_FIRST = '+'
    REQUESTER_LAST = '-'
    SHUFFLED = '?'
    ALL = (REQUESTER_FIRST, REQUESTER_LAST, SHUFFLED)


class ScrimmageRequestAcceptReject:
    AUTO_ACCEPT = 'A'
    AUTO_REJECT = 'R'
    MANUAL = 'M'
    ALL = (AUTO_ACCEPT, AUTO_REJECT, MANUAL)


SATURN_MAX_FAILURES = 5          # settings.py:344
MAX_MAPS_PER_SCRIMMAGE = 10      # settings.py
MAX_SCRIMMAGES_AGAINST_TEAM = 3  # settings.py

SCHEMA = """
CREATE TABLE IF NOT EXISTS episode (
  name_short TEXT PRIMARY KEY,
  name_long TEXT NOT NULL DEFAULT '',
  is_allowed_ranked_scrimmage INTEGER NOT NULL DEFAULT 1,
  ranked_scrimmage_hourly_limit INTEGER NOT NULL DEFAULT 10,
  unranked_scrimmage_hourly_limit INTEGER NOT NULL DEFAULT 10,
  autoscrim_best_of INTEGER NOT NULL DEFAULT 3,
  enforce_rules INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS map (
  id INTEGER PRIMARY KEY,
  episode TEXT NOT NULL REFERENCES episode(name_short),
  name TEXT NOT NULL,
  is_public INTEGER NOT NULL DEFAULT 0,
  UNIQUE (episode, name)
);
CREATE TABLE IF NOT EXISTS rating (
  id INTEGER PRIMARY KEY,
  mean REAL NOT NULL DEFAULT 1500.0,
  n INTEGER NOT NULL DEFAULT 0,
  value REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS team (
  id INTEGER PRIMARY KEY,
  episode TEXT NOT NULL REFERENCES episode(name_short),
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'R' CHECK (status IN ('R','X','S','O')),
  rating_id INTEGER NOT NULL REFERENCES rating(id),
  auto_accept_reject_ranked TEXT NOT NULL DEFAULT 'A' CHECK (auto_accept_reject_ranked IN ('A','R','M')),
  auto_accept_reject_unranked TEXT NOT NULL DEFAULT 'A' CHECK (auto_accept_reject_unranked IN ('A','R','M')),
  created TEXT NOT NULL,
  UNIQUE (episode, name)
);
CREATE TABLE IF NOT EXISTS submission (
  id INTEGER PRIMARY KEY,
  episode TEXT NOT NULL REFERENCES episode(name_short),
  team INTEGER NOT NULL REFERENCES team(id),
  status TEXT NOT NULL DEFAULT 'NEW',
  created TEXT NOT NULL,
  logs TEXT NOT NULL DEFAULT '',
  num_failures INTEGER NOT NULL DEFAULT 0,
  accepted INTEGER NOT NULL DEFAULT 0,
  package TEXT NOT NULL DEFAULT '',
  description TEXT NOT NULL DEFAULT '',
  source_path TEXT,
  binary_path TEXT,
  prebuilt_classes TEXT,
  verify INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS submission_team ON submission(team, accepted);
CREATE TABLE IF NOT EXISTS match (
  id INTEGER PRIMARY KEY,
  episode TEXT NOT NULL REFERENCES episode(name_short),
  status TEXT NOT NULL DEFAULT 'NEW',
  created TEXT NOT NULL,
  logs TEXT NOT NULL DEFAULT '',
  num_failures INTEGER NOT NULL DEFAULT 0,
  alternate_order INTEGER NOT NULL,
  is_ranked INTEGER NOT NULL,
  replay TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'manual' CHECK (source IN ('request','autoscrim','manual')),
  request_id INTEGER REFERENCES scrimmage_request(id),
  claimed_at TEXT,
  worker TEXT,
  finished TEXT
);
CREATE INDEX IF NOT EXISTS match_status ON match(status, id);
CREATE TABLE IF NOT EXISTS match_map (
  id INTEGER PRIMARY KEY,
  match INTEGER NOT NULL REFERENCES match(id),
  map INTEGER NOT NULL REFERENCES map(id),
  sort INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS match_map_match ON match_map(match, sort);
CREATE TABLE IF NOT EXISTS match_participant (
  id INTEGER PRIMARY KEY,
  team INTEGER NOT NULL REFERENCES team(id),
  submission INTEGER NOT NULL REFERENCES submission(id),
  match INTEGER NOT NULL REFERENCES match(id),
  player_index INTEGER NOT NULL,
  score INTEGER,
  rating_id INTEGER REFERENCES rating(id),
  previous_participation INTEGER UNIQUE REFERENCES match_participant(id)
);
CREATE INDEX IF NOT EXISTS mp_team ON match_participant(team, id);
CREATE INDEX IF NOT EXISTS mp_match ON match_participant(match, player_index);
CREATE INDEX IF NOT EXISTS mp_pending ON match_participant(rating_id, id);
CREATE TABLE IF NOT EXISTS scrimmage_request (
  id INTEGER PRIMARY KEY,
  episode TEXT NOT NULL REFERENCES episode(name_short),
  created TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'P' CHECK (status IN ('P','Y','N')),
  is_ranked INTEGER NOT NULL,
  requested_by INTEGER NOT NULL REFERENCES team(id),
  requested_to INTEGER NOT NULL REFERENCES team(id),
  player_order TEXT NOT NULL CHECK (player_order IN ('+','-','?'))
);
CREATE TABLE IF NOT EXISTS request_map (
  id INTEGER PRIMARY KEY,
  request INTEGER NOT NULL REFERENCES scrimmage_request(id),
  map INTEGER NOT NULL REFERENCES map(id),
  sort INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS game (
  id INTEGER PRIMARY KEY,
  match INTEGER NOT NULL REFERENCES match(id),
  idx INTEGER NOT NULL,
  map TEXT NOT NULL,
  team_a INTEGER NOT NULL REFERENCES team(id),
  team_b INTEGER NOT NULL REFERENCES team(id),
  reversed INTEGER NOT NULL,
  winner TEXT CHECK (winner IN ('A','B')),
  round INTEGER,
  reason TEXT,
  exported TEXT,
  UNIQUE (match, idx)
);
"""


# ---------------------------------------------------------------- paths and connections
SERVICE_HOME = '/home/bcreplica/replica'   # where the systemd services keep the data (docs/replica/DEPLOY.md)


def home():
    """$REPLICA_HOME; else the services' data dir when this host has one (battlecode-dev: readable by the bcreplica
    group, writable only by user bcreplica), so operator commands never split off a second DB; else ~/replica."""
    if os.environ.get('REPLICA_HOME'):
        return os.path.abspath(os.path.expanduser(os.environ['REPLICA_HOME']))
    if os.path.isfile(os.path.join(SERVICE_HOME, 'replica.db')):
        return SERVICE_HOME
    return os.path.abspath(os.path.expanduser('~/replica'))


def path(*parts):
    return os.path.join(home(), *parts)


def ensure_dirs():
    for d in ('', 'replay', 'sub', 'logs'):
        os.makedirs(path(d), exist_ok=True)


def db_path():
    return path('replica.db')


def connect(file=None):
    """Autocommit connection (isolation_level=None); write with `with tx(conn):` (BEGIN IMMEDIATE)."""
    file = file or db_path()
    conn = sqlite3.connect(file, timeout=60, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA busy_timeout = 60000')
    if file != ':memory:':
        conn.execute('PRAGMA journal_mode = WAL')
    conn.executescript(SCHEMA)
    return conn


@contextlib.contextmanager
def tx(conn):
    """One write transaction. Nested use joins the outer transaction."""
    if conn.in_transaction:
        yield conn
        return
    conn.execute('BEGIN IMMEDIATE')
    try:
        yield conn
    except BaseException:
        conn.execute('ROLLBACK')
        raise
    conn.execute('COMMIT')


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds')


def ago(**kw):
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(**kw)).isoformat(timespec='microseconds')


def parse_time(s):
    return datetime.datetime.fromisoformat(s)


# ---------------------------------------------------------------- episode and maps
def read_maps_file(file=None):
    file = file or os.path.join(TOOLS, 'maps.txt')
    with open(file) as fh:
        return [l.strip() for l in fh if l.strip() and not l.startswith('#')]


def init_episode(conn, name_short=EPISODE, maps=None, public=True):
    """Create the episode (if missing) and add the maps (default: tools/maps.txt, all public)."""
    maps = read_maps_file() if maps is None else maps
    with tx(conn):
        conn.execute('INSERT OR IGNORE INTO episode(name_short, name_long) VALUES (?, ?)',
                     (name_short, 'Battlecode 2023 (private replica)'))
        for m in maps:
            conn.execute('INSERT OR IGNORE INTO map(episode, name, is_public) VALUES (?, ?, ?)',
                         (name_short, m, 1 if public else 0))
    return get_episode(conn, name_short)


def get_episode(conn, name_short=EPISODE):
    row = conn.execute('SELECT * FROM episode WHERE name_short=?', (name_short,)).fetchone()
    if row is None:
        raise LookupError(f'no episode {name_short!r}; run: tools/replica.py init')
    return row


EPISODE_SETTINGS = ('is_allowed_ranked_scrimmage', 'ranked_scrimmage_hourly_limit', 'unranked_scrimmage_hourly_limit',
                    'autoscrim_best_of', 'enforce_rules', 'name_long')


def set_episode(conn, name_short=EPISODE, **kw):
    for k in kw:
        if k not in EPISODE_SETTINGS:
            raise ValueError(f'unknown episode setting {k!r} (known: {", ".join(EPISODE_SETTINGS)})')
    with tx(conn):
        for k, v in kw.items():
            conn.execute(f'UPDATE episode SET {k}=? WHERE name_short=?', (v, name_short))
    return get_episode(conn, name_short)


def public_maps(conn, episode=EPISODE):
    """{name: id} of the episode's public maps, in id order."""
    return {r['name']: r['id'] for r in
            conn.execute('SELECT id, name FROM map WHERE episode=? AND is_public=1 ORDER BY id', (episode,))}


# ---------------------------------------------------------------- ratings and teams
TEAMS_ELO_INITIAL = 1500.0
TEAMS_ELO_PENALTY = 0.85


def insert_rating(conn, mean=TEAMS_ELO_INITIAL, n=0):
    """Rating.objects.create(...): Rating.save recomputes value = mean - 1500 * 0.85**n."""
    value = mean - TEAMS_ELO_INITIAL * TEAMS_ELO_PENALTY ** n
    return conn.execute('INSERT INTO rating(mean, n, value) VALUES (?, ?, ?)', (mean, n, value)).lastrowid


def get_rating(conn, rating_id):
    return conn.execute('SELECT * FROM rating WHERE id=?', (rating_id,)).fetchone()


def create_team(conn, name, episode=EPISODE, status=TeamStatus.REGULAR,
                auto_ranked=ScrimmageRequestAcceptReject.AUTO_ACCEPT,
                auto_unranked=ScrimmageRequestAcceptReject.AUTO_ACCEPT):
    """Team.save + TeamProfile.save: a new team gets a fresh Rating() (mean 1500, n 0, value 0)."""
    if status not in TeamStatus.ALL:
        raise ValueError(f'bad team status {status!r}')
    if not name or len(name) > 64 or any(not (' ' <= c <= '~') for c in name):
        raise ValueError('team name must be 1-64 printable ASCII characters')
    with tx(conn):
        rid = insert_rating(conn)
        return conn.execute(
            'INSERT INTO team(episode, name, status, rating_id, auto_accept_reject_ranked, '
            'auto_accept_reject_unranked, created) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (episode, name, status, rid, auto_ranked, auto_unranked, now())).lastrowid


def get_team(conn, key, episode=EPISODE):
    """A team by id (int or digit string) or by exact name."""
    if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
        row = conn.execute('SELECT * FROM team WHERE id=? AND episode=?', (int(key), episode)).fetchone()
        if row is not None:
            return row
    row = conn.execute('SELECT * FROM team WHERE name=? AND episode=?', (str(key), episode)).fetchone()
    if row is None:
        raise LookupError(f'no team {key!r}')
    return row


def is_staff(team_row):
    return team_row['status'] in (TeamStatus.STAFF, TeamStatus.INVISIBLE)


def active_submission(conn, team_id):
    """Team.get_active_submission / with_active_submission: the newest accepted submission (highest pk)."""
    row = conn.execute('SELECT id FROM submission WHERE team=? AND accepted=1 ORDER BY id DESC LIMIT 1',
                       (team_id,)).fetchone()
    return row['id'] if row else None


def copy_rating_to_profile(conn, team_id, rating_id):
    """teams/signals.py copy_rating_to_profile: the team's displayed rating follows the participation's new rating,
    but only if it has a higher n."""
    n = get_rating(conn, rating_id)['n']
    conn.execute('UPDATE team SET rating_id=? WHERE id=? AND (SELECT n FROM rating WHERE rating.id=team.rating_id) < ?',
                 (rating_id, team_id, n))


# ---------------------------------------------------------------- submissions
def insert_submission(conn, team_id, package, episode=EPISODE, status=SaturnStatus.CREATED, accepted=False,
                      description='', source_path=None, binary_path=None, prebuilt_classes=None, verify=True):
    return conn.execute(
        'INSERT INTO submission(episode, team, status, created, accepted, package, description, source_path, '
        'binary_path, prebuilt_classes, verify) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (episode, team_id, status, now(), 1 if accepted else 0, package, description, source_path, binary_path,
         prebuilt_classes, 1 if verify else 0)).lastrowid


# ---------------------------------------------------------------- matches
def insert_match(conn, *, is_ranked, alternate_order, episode=EPISODE, status=SaturnStatus.CREATED,
                 source='manual', request_id=None):
    return conn.execute(
        'INSERT INTO match(episode, status, created, alternate_order, is_ranked, replay, source, request_id) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (episode, status, now(), 1 if alternate_order else 0, 1 if is_ranked else 0, str(uuid.uuid4()), source,
         request_id)).lastrowid


def set_match_maps(conn, match_id, map_ids):
    for i, m in enumerate(map_ids):
        conn.execute('INSERT INTO match_map(match, map, sort) VALUES (?, ?, ?)', (match_id, m, i))


def match_map_names(conn, match_id):
    return [r['name'] for r in conn.execute(
        'SELECT map.name FROM match_map JOIN map ON map.id=match_map.map WHERE match_map.match=? '
        'ORDER BY match_map.sort, match_map.id', (match_id,))]


def insert_participant(conn, *, team_id, match_id, player_index, submission_id=None, score=None, rating_id=None):
    """MatchParticipant.objects.create(...) with its save() and post_save signals:
      * save(): an empty submission is filled with the team's active submission;
      * compete/signals.py connect_linked_list: previous_participation = the team's participation with the highest
        lower pk (the same rule MatchParticipantManager.bulk_create applies with a subquery);
      * teams/signals.py copy_rating_to_profile when the row is created with a rating."""
    if submission_id is None:
        submission_id = active_submission(conn, team_id)
        if submission_id is None:
            raise ValueError(f'team {team_id} has no accepted submission')
    pid = conn.execute(
        'INSERT INTO match_participant(team, submission, match, player_index, score, rating_id) '
        'VALUES (?, ?, ?, ?, ?, ?)', (team_id, submission_id, match_id, player_index, score, rating_id)).lastrowid
    prev = conn.execute('SELECT id FROM match_participant WHERE team=? AND id<? ORDER BY id DESC LIMIT 1',
                        (team_id, pid)).fetchone()
    if prev is not None:
        conn.execute('UPDATE match_participant SET previous_participation=? WHERE id=?', (prev['id'], pid))
    if rating_id is not None:
        copy_rating_to_profile(conn, team_id, rating_id)
    return pid


# Galaxy's rating-history and record views leave out every match that has an INVISIBLE team in it
# (compete/views.py:459 get_historical_rating and :681 scrimmaging_record, .exclude(...team__status=INVISIBLE)).
# An SQL condition on a match aliased `m`.
NO_INVISIBLE_MATCH = ("NOT EXISTS (SELECT 1 FROM match_participant x JOIN team xt ON xt.id=x.team "
                      "WHERE x.match=m.id AND xt.status='O')")


def participants(conn, match_id):
    return conn.execute('SELECT * FROM match_participant WHERE match=? ORDER BY player_index, id',
                        (match_id,)).fetchall()


def enqueue(conn, match_ids=None, table='match'):
    """SaturnInvokableQuerySet.enqueue: CREATED -> QUEUED (num_failures reset). The worker polls the table."""
    assert table in ('match', 'submission')
    with tx(conn):
        if match_ids is None:
            conn.execute(f"UPDATE {table} SET status='QUE', num_failures=0 WHERE status='NEW'")
        else:
            for m in match_ids:
                conn.execute(f"UPDATE {table} SET status='QUE', num_failures=0 WHERE id=? AND status='NEW'", (m,))


def requeue(conn, match_id):
    """Admin requeue (enqueue_all) of a match that is not COMPLETED: back to QUEUED with failures reset.
    COMPLETED matches are refused (their ratings may already be final). Returns True if the match was requeued."""
    with tx(conn):
        cur = conn.execute("UPDATE match SET status='QUE', num_failures=0, claimed_at=NULL, worker=NULL "
                           "WHERE id=? AND status!='OK!'", (match_id,))
        if cur.rowcount:
            conn.execute('UPDATE match_participant SET score=NULL WHERE match=? AND rating_id IS NULL', (match_id,))
        return cur.rowcount > 0


def cancel(conn, match_ids, table='match'):
    """SaturnInvokableQuerySet.cancel: everything not COMPLETED becomes CANCELLED."""
    assert table in ('match', 'submission')
    with tx(conn):
        for m in match_ids:
            conn.execute(f"UPDATE {table} SET status='CAN' WHERE id=? AND status!='OK!'", (m,))


def status_counts(conn, table='match'):
    assert table in ('match', 'submission')
    return {r['status']: r['c'] for r in conn.execute(f'SELECT status, COUNT(*) c FROM {table} GROUP BY status')}
