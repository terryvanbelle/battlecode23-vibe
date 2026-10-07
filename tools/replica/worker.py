"""The match runner (replaces saturn): N slots, each claims a job, runs it and reports through saturn's protocol.

Sources (galaxy f343088):
  saturn/pkg/run/java.go           RunMatch flags, javaWinnerRegex, DetermineScores ([aWins, bWins]), VerifySubmission
  saturn/pkg/run/file.go           GetArchive (zip-slip check: every entry must stay under the target root)
  saturn/pkg/saturn/task.go        RUN -> OK! | TRY (errored or interrupted); 409 from siarnaq -> abort (ABT)
  backend/siarnaq/api/compete/serializers.py:35-69   SaturnInvocationSerializer.update (409 when finalized,
                                   num_failures += 1 on a TRY that was not interrupted, ERR at SATURN_MAX_FAILURES)
  backend/siarnaq/api/compete/serializers.py:320-343 MatchReportSerializer (scores by player_index)
Differences from saturn, all deliberate (GALAXY.md 6.4):
  * one bare-java engine invocation per match with all its maps (no Gradle, no scaffold, no GitHub, no GCS);
  * -Dbc.server.websocket=false (saturn's scaffold leaves the 0.0.0.0:6175 listener on);
  * an OK! with scores [0,0] or fewer wins than maps is reported as TRY instead (galaxy would divide by zero);
  * a stale-RUN reaper returns jobs of dead workers (interrupted) or overdue jobs (a failure) to TRY;
  * prebuilt class dirs (benchmarks, our builds) are registered without compiling.
The engine classpath, JAVA_HOME and the jar checksum come from tools/lib.sh (engine_cp, ENGINE_SHA256).
"""
import hashlib
import logging
import os
import re
import shutil
import signal
import socket
import subprocess
import threading
import time
import zipfile

from . import db, rating
from .db import SaturnStatus

LIB_SH = os.path.join(db.TOOLS, 'lib.sh')
JAVA_WINNER_REGEX = re.compile(r'(?m)^\[server\]\s*.*\(([AB])\) wins \(round [0-9]+\)$')   # saturn java.go:16
GAME_START_REGEX = re.compile(r'^\[server\] (\S+) vs\. (\S+) on (\S+)\s*$')
WINNER_LINE_REGEX = re.compile(r'^\[server\]\s*.*\(([AB])\) wins \(round ([0-9]+)\)$')
REASON_REGEX = re.compile(r'^\[server\] Reason: (.*?)\s*$')
MAX_SOURCE_ZIP = 5 * 1024 * 1024   # SubmissionSerializer FileValidator(max_size=5 MiB)
GAME_TIMEOUT = int(os.environ.get('REPLICA_GAME_TIMEOUT', '1800'))   # seconds per game, as tools/lib.sh run_game

log = logging.getLogger('replica.worker')


class AlreadyFinalized(Exception):
    """siarnaq's 409: the invocation is already finalized; saturn then aborts the task (TaskAborted)."""


# ---------------------------------------------------------------- engine environment (from tools/lib.sh)
class Engine:
    def __init__(self, java, cp, jar, sha256):
        self.java, self.cp, self.jar, self.sha256 = java, cp, jar, sha256

    @classmethod
    def from_lib(cls, check_sha=True):
        out = subprocess.run(
            ['bash', '-c', 'source "$1" >/dev/null || exit 1; cp="$(engine_cp)" || exit 1; '
             'printf "%s\\n" "$cp" "$JAVA_HOME" "$ENGINE_SHA256" "$ENGINE_DIR/battlecode23-$ENGINE_VER.jar"',
             '_', LIB_SH], capture_output=True, text=True, check=True).stdout.splitlines()
        cp, java_home, sha, jar = out[:4]
        java = os.path.join(java_home, 'bin', 'java')
        if not os.path.exists(java):
            java = shutil.which('java') or 'java'
        if check_sha:
            h = hashlib.sha256()
            with open(jar, 'rb') as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b''):
                    h.update(chunk)
            if h.hexdigest() != sha:
                raise RuntimeError(f'engine jar {jar} sha256 {h.hexdigest()} != pinned {sha}')
        return cls(java, cp, jar, sha)

    def javac(self):
        return os.path.join(os.path.dirname(self.java), 'javac')


def match_command(engine, *, names, urls, packages, maps, alternate_order, replay, timeout):
    """The single engine invocation of GALAXY.md 6.4 step 3 (saturn's RunMatch flags, run with bare java)."""
    return [
        'timeout', str(int(timeout)), engine.java, '-Xmx768m', '-XX:+UseSerialGC',
        '-Dbc.server.mode=headless', '-Dbc.server.websocket=false',
        '-Dbc.server.robot-player-to-system-out=false', '-Dbc.server.debug=false',
        '-Dbc.engine.debug-methods=false', '-Dbc.engine.enable-profiler=false',
        '-Dbc.engine.show-indicators=false', '-Dbc.server.validate-maps=true',
        f'-Dbc.game.team-a={names[0]}', f'-Dbc.game.team-b={names[1]}',
        f'-Dbc.game.team-a.url={urls[0]}', f'-Dbc.game.team-b.url={urls[1]}',
        f'-Dbc.game.team-a.package={packages[0]}', f'-Dbc.game.team-b.package={packages[1]}',
        f'-Dbc.game.maps={",".join(maps)}',
        f'-Dbc.server.alternate-order={"true" if alternate_order else "false"}',
        f'-Dbc.server.save-file={replay}',
        '-cp', engine.cp, 'battlecode.server.Main', '-c=-',
    ]


# ---------------------------------------------------------------- log parsing
def saturn_scores(out):
    """saturn DetermineScores: count winner lines -> [aWins, bWins]."""
    scores = [0, 0]
    for w in JAVA_WINNER_REGEX.findall(out):
        if w == 'A':
            scores[0] += 1
        elif w == 'B':
            scores[1] += 1
        else:
            raise ValueError(f'unknown winner: {w}')
    return scores


def parse_games(out, maps, alternate_order):
    """Per-game rows from engine stdout: [{idx, map, reversed, winner, round, reason}], in play order.
    The engine prints '<pkgA> vs. <pkgB> on <map>' before each game and 'Reason: ...' after each winner line; game i
    has spawns reversed when alternate_order is set and i is odd (Server.java teamsReversed)."""
    games, current_map = [], None
    for line in out.splitlines():
        m = GAME_START_REGEX.match(line)
        if m:
            current_map = m.group(3)
            continue
        m = WINNER_LINE_REGEX.match(line)
        if m:
            idx = len(games)
            games.append({'idx': idx, 'map': current_map or (maps[idx] if idx < len(maps) else '?'),
                          'reversed': bool(alternate_order and idx % 2 == 1),
                          'winner': m.group(1), 'round': int(m.group(2)), 'reason': None})
            current_map = None
            continue
        m = REASON_REGEX.match(line)
        if m and games and games[-1]['reason'] is None:
            games[-1]['reason'] = m.group(1)
    return games


# ---------------------------------------------------------------- report protocol
def report(conn, table, pk, status, *, logs='', interrupted=False, scores=None, accepted=None, games=None,
           pump=True):
    """SaturnInvocationSerializer.update (+ MatchReportSerializer / SubmissionReportSerializer).
    Returns the stored status. Raises AlreadyFinalized (siarnaq's 409) if the invocation is already finalized."""
    assert table in ('match', 'submission')
    if table == 'match' and status == SaturnStatus.COMPLETED:
        n_maps = len(db.match_map_names(conn, pk))
        if not scores or sum(scores) == 0 or sum(scores) != n_maps:
            logs += f'[replica] OK! with scores {scores} for {n_maps} maps is treated as TRY.\n'
            status, scores, games = SaturnStatus.RETRY, None, None
    with db.tx(conn):
        inst = conn.execute(f'SELECT * FROM {table} WHERE id=?', (pk,)).fetchone()
        if inst is None:
            raise LookupError(f'no {table} {pk}')
        if inst['status'] in SaturnStatus.FINALIZED:
            raise AlreadyFinalized(f'{table} {pk} is already finalized ({inst["status"]})')
        if table == 'match' and scores:
            parts = db.participants(conn, pk)
            if len(scores) != len(parts):
                raise ValueError('must provide either no or all scores')
            for p, s in zip(parts, scores):
                conn.execute('UPDATE match_participant SET score=? WHERE id=?', (int(s), p['id']))
        if table == 'submission' and accepted is not None:
            conn.execute('UPDATE submission SET accepted=? WHERE id=?', (1 if accepted else 0, pk))
        num_failures = inst['num_failures']
        new_logs = inst['logs'] + (logs or '')
        if status == SaturnStatus.RETRY and not interrupted:
            num_failures += 1
        if num_failures >= db.SATURN_MAX_FAILURES:
            status = SaturnStatus.ERRORED
            new_logs += '[siarnaq] Maximum retries reached.\n'
        extra = ''
        if table == 'match':
            extra = ', finished=?' if status in SaturnStatus.FINALIZED else ''
        args = [status, new_logs, num_failures] + ([db.now()] if extra else []) + [pk]
        conn.execute(f'UPDATE {table} SET status=?, logs=?, num_failures=?{extra} WHERE id=?', args)
        if table == 'match' and status == SaturnStatus.COMPLETED and games:
            parts = db.participants(conn, pk)
            conn.execute('DELETE FROM game WHERE match=?', (pk,))
            for g in games:
                conn.execute('INSERT INTO game(match, idx, map, team_a, team_b, reversed, winner, round, reason) '
                             'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                             (pk, g['idx'], g['map'], parts[0]['team'], parts[1]['team'], 1 if g['reversed'] else 0,
                              g['winner'], g['round'], g['reason']))
    if pump and table == 'match':
        rating.pump(conn)
    return status


def claim(conn, table, worker_id):
    """Atomically claim the oldest QUEUED or RETRY job (status -> RUN, saturn's first report). Returns its row."""
    assert table in ('match', 'submission')
    with db.tx(conn):
        row = conn.execute(f"SELECT id FROM {table} WHERE status IN ('QUE','TRY') ORDER BY id LIMIT 1").fetchone()
        if row is None:
            return None
        if table == 'match':
            cur = conn.execute("UPDATE match SET status='RUN', claimed_at=?, worker=? "
                               "WHERE id=? AND status IN ('QUE','TRY')", (db.now(), worker_id, row['id']))
        else:
            cur = conn.execute("UPDATE submission SET status='RUN' WHERE id=? AND status IN ('QUE','TRY')",
                               (row['id'],))
        if cur.rowcount != 1:
            return None
        return conn.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone()


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def reap_stale(conn, timeout_per_game=GAME_TIMEOUT, host=None):
    """Return RUN matches to TRY: a dead worker process on this host -> interrupted (no failure counted); a match
    running longer than 2 x its time limit -> a failure. Returns [(match_id, reason)]."""
    host = host or socket.gethostname()
    reaped = []
    for m in conn.execute("SELECT * FROM match WHERE status='RUN'").fetchall():
        n_maps = max(1, len(db.match_map_names(conn, m['id'])))
        limit = 2 * timeout_per_game * n_maps + 60
        w = (m['worker'] or '').split(':')
        dead = len(w) >= 2 and w[0] == host and w[1].isdigit() and not _pid_alive(int(w[1]))
        overdue = m['claimed_at'] is not None and \
            (db.parse_time(db.now()) - db.parse_time(m['claimed_at'])).total_seconds() > limit
        if not (dead or overdue):
            continue
        why = f'worker {m["worker"]} is gone' if dead else f'running longer than {limit} s'
        try:
            report(conn, 'match', m['id'], SaturnStatus.RETRY, interrupted=dead,
                   logs=f'[replica] reaped stale RUN: {why}.\n')
            reaped.append((m['id'], why))
        except AlreadyFinalized:
            pass
    return reaped


# ---------------------------------------------------------------- submissions
def _pkg_dir(root, package):
    return os.path.join(root, *package.split('.'))


def classes_digest(classdir, package):
    """sha256 over the package's class files (relative path + content), for provenance."""
    h = hashlib.sha256()
    root = _pkg_dir(classdir, package)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for f in sorted(filenames):
            p = os.path.join(dirpath, f)
            h.update(os.path.relpath(p, classdir).encode() + b'\0')
            with open(p, 'rb') as fh:
                h.update(fh.read())
    return h.hexdigest()


def submit(conn, team, package, *, prebuilt_classes=None, source=None, snapshot=None, verify=False,
           description=''):
    """Create a submission. prebuilt_classes: a class dir holding <package>/RobotPlayer.class, accepted at once
    (or queued for the Verifier only, with verify=True); snapshot copies <classdir>/<package>/ into the data dir so
    later rebuilds do not change it (default: on for 'us:' teams). source: a source dir (holding <package>/ or being
    it) or a .zip, queued for compile + verify. Returns the submission id."""
    t = db.get_team(conn, team)
    if not package or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*', package):
        raise ValueError(f'bad package name {package!r}')
    if (prebuilt_classes is None) == (source is None):
        raise ValueError('give exactly one of prebuilt_classes or source')
    db.ensure_dirs()
    if prebuilt_classes is not None:
        classdir = os.path.abspath(os.path.expanduser(prebuilt_classes))
        rp = os.path.join(_pkg_dir(classdir, package), 'RobotPlayer.class')
        if not os.path.isfile(rp):
            raise ValueError(f'no {rp}')
        snapshot = t['name'].startswith('us:') if snapshot is None else snapshot
        digest = classes_digest(classdir, package)[:16]
        desc = (description + ' ' if description else '') + f'classes sha256:{digest}'
        with db.tx(conn):
            sid = db.insert_submission(conn, t['id'], package, status=SaturnStatus.QUEUED if verify else
                                       SaturnStatus.COMPLETED, accepted=not verify, description=desc,
                                       prebuilt_classes=classdir, binary_path=classdir, verify=verify)
            if not verify:
                conn.execute('UPDATE submission SET logs=? WHERE id=?',
                             (f'[replica] prebuilt classes {classdir} registered without compiling.\n', sid))
        if snapshot:
            dst = path_binary(sid)
            shutil.copytree(_pkg_dir(classdir, package), _pkg_dir(dst, package), dirs_exist_ok=True)
            with db.tx(conn):
                conn.execute('UPDATE submission SET binary_path=? WHERE id=?', (dst, sid))
        return sid
    src = os.path.abspath(os.path.expanduser(source))
    if not os.path.exists(src):
        raise ValueError(f'no {src}')
    with db.tx(conn):
        return db.insert_submission(conn, t['id'], package, status=SaturnStatus.QUEUED, description=description,
                                    source_path=src)


def path_binary(sid):
    return db.path('sub', str(sid), 'binary')


def unzip_checked(zpath, root):
    """saturn GetArchive: refuse an archive with any entry outside root (zip slip). Returns an error or None."""
    root = os.path.abspath(root)
    try:
        zf = zipfile.ZipFile(zpath)
    except zipfile.BadZipFile as e:
        return f'Archive is malformed: {e}'
    with zf:
        for info in zf.infolist():
            local = os.path.abspath(os.path.join(root, info.filename))
            if not local.startswith(root + os.sep):
                return f'Archive contains illegal path: {local}'
        for info in zf.infolist():
            local = os.path.abspath(os.path.join(root, info.filename))
            if info.is_dir():
                continue
            os.makedirs(os.path.dirname(local), exist_ok=True)
            with zf.open(info) as r, open(local, 'wb') as w:
                shutil.copyfileobj(r, w)
    return None


def compile_submission(conn, sub, engine):
    """Compile (javac -proc:none, via tools/lib.sh compile_src) and verify (battlecode.instrumenter.Verifier).
    A compile or verify failure is OK! with accepted=false (saturn VerifySubmission); infrastructure errors raise."""
    sid, pkg = sub['id'], sub['package']
    work = db.path('sub', str(sid))
    if not pkg:
        return report(conn, 'submission', sid, SaturnStatus.COMPLETED, accepted=False,
                      logs='Package name must not be empty.\n')
    binary = sub['binary_path'] if sub['prebuilt_classes'] else path_binary(sid)
    logs = ''
    if not sub['prebuilt_classes']:
        src_root = os.path.join(work, 'source')
        shutil.rmtree(src_root, ignore_errors=True)
        shutil.rmtree(binary, ignore_errors=True)
        os.makedirs(src_root, exist_ok=True)
        src = sub['source_path']
        if src.endswith('.zip'):
            if os.path.getsize(src) > MAX_SOURCE_ZIP:
                return report(conn, 'submission', sid, SaturnStatus.COMPLETED, accepted=False,
                              logs=f'Source archive is larger than {MAX_SOURCE_ZIP} bytes.\n')
            err = unzip_checked(src, src_root)
            if err:
                return report(conn, 'submission', sid, SaturnStatus.COMPLETED, accepted=False, logs=err + '\n')
        elif os.path.isdir(_pkg_dir(src, pkg)):
            shutil.copytree(_pkg_dir(src, pkg), _pkg_dir(src_root, pkg))
        elif os.path.isdir(src) and os.path.basename(os.path.normpath(src)) == pkg.split('.')[-1]:
            shutil.copytree(src, _pkg_dir(src_root, pkg))
        else:
            return report(conn, 'submission', sid, SaturnStatus.COMPLETED, accepted=False,
                          logs=f'No package directory {pkg} under {src}.\n')
        r = subprocess.run(['bash', '-c', 'source "$1" >/dev/null; compile_src "$2" "$3"', '_', LIB_SH, src_root,
                            binary], capture_output=True, text=True)
        logs += r.stdout + r.stderr
        if r.returncode != 0:
            return report(conn, 'submission', sid, SaturnStatus.COMPLETED, accepted=False,
                          logs=logs + f'[replica] compile failed (exit {r.returncode}).\n')
    r = subprocess.run([engine.java, '-cp', engine.cp, 'battlecode.instrumenter.Verifier', pkg, binary],
                       capture_output=True, text=True, timeout=600)
    logs += r.stdout + r.stderr
    ok = r.returncode == 0
    if ok and not sub['prebuilt_classes']:
        with db.tx(conn):
            conn.execute('UPDATE submission SET binary_path=? WHERE id=?', (binary, sid))
    return report(conn, 'submission', sid, SaturnStatus.COMPLETED, accepted=ok,
                  logs=logs + f'[replica] Verifier exit {r.returncode}: {"accepted" if ok else "rejected"}.\n')


# ---------------------------------------------------------------- execute
def execute_match(conn, m, engine, *, timeout_per_game=GAME_TIMEOUT, stop=None):
    """Run one claimed match (status RUN) and report it. Returns the stored status."""
    mid = m['id']
    parts = db.participants(conn, mid)
    maps = db.match_map_names(conn, mid)
    names, urls, packages = [], [], []
    for p in parts:
        t = conn.execute('SELECT name FROM team WHERE id=?', (p['team'],)).fetchone()
        s = conn.execute('SELECT package, binary_path FROM submission WHERE id=?', (p['submission'],)).fetchone()
        names.append(t['name'])
        urls.append(s['binary_path'])
        packages.append(s['package'])
    if len(parts) != 2 or not maps or not all(urls):
        return report(conn, 'match', mid, SaturnStatus.RETRY,
                      logs=f'[replica] bad match: {len(parts)} participants, {len(maps)} maps, binaries {urls}.\n')
    replay = db.path('replay', f'{m["replay"]}.bc23')
    timeout = timeout_per_game * len(maps)
    cmd = match_command(engine, names=names, urls=urls, packages=packages, maps=maps,
                        alternate_order=bool(m['alternate_order']), replay=replay, timeout=timeout)
    logfile = db.path('logs', f'match-{mid}.log')
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                            text=True, errors='replace', start_new_session=True)
    chunks, interrupted = [], False
    while True:
        try:
            out, _ = proc.communicate(timeout=2)
            chunks.append(out or '')
            break
        except subprocess.TimeoutExpired:
            if stop is not None and stop.is_set():
                interrupted = True
                _kill_group(proc)
                out, _ = proc.communicate()
                chunks.append(out or '')
                break
    out = ''.join(chunks)
    rc = proc.returncode
    secs = time.time() - t0
    with open(logfile, 'a') as fh:
        fh.write(f'==== {db.now()} match {mid} attempt {m["num_failures"] + 1} exit {rc} {secs:.0f}s\n'
                 f'==== {" ".join(cmd)}\n{out}\n')
    if interrupted:
        return report(conn, 'match', mid, SaturnStatus.RETRY, interrupted=True,
                      logs=f'[replica] interrupted after {secs:.0f}s; will be retried.\n')
    if rc != 0:
        tail = '\n'.join(out.splitlines()[-15:])
        why = 'timed out' if rc == 124 else f'exit {rc}'
        return report(conn, 'match', mid, SaturnStatus.RETRY,
                      logs=f'[replica] engine {why} after {secs:.0f}s (log {logfile}).\n{tail}\n')
    try:
        scores = saturn_scores(out)
    except ValueError as e:
        return report(conn, 'match', mid, SaturnStatus.RETRY, logs=f'could not determine winner: {e}\n')
    games = parse_games(out, maps, bool(m['alternate_order']))
    summary = ' '.join(f'{g["map"]}:{g["winner"]}@{g["round"]}' for g in games)
    return report(conn, 'match', mid, SaturnStatus.COMPLETED, scores=scores, games=games,
                  logs=f'[replica] scores {scores} in {secs:.0f}s: {summary}\n')


def _kill_group(proc):
    """Stop an engine this worker started (its own process group; never other java processes)."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


# ---------------------------------------------------------------- the worker
class Worker:
    def __init__(self, slots=4, poll=2.0, timeout_per_game=GAME_TIMEOUT, until_empty=False, max_jobs=None,
                 engine=None):
        if not 1 <= slots <= 16:
            raise ValueError('slots must be 1..16')
        self.slots, self.poll, self.timeout_per_game = slots, poll, timeout_per_game
        self.until_empty, self.max_jobs = until_empty, max_jobs
        self.engine = engine or Engine.from_lib()
        self.stop = threading.Event()
        self.jobs_lock = threading.Lock()
        self.jobs_started = 0
        self.host = socket.gethostname()

    def _take_budget(self):
        with self.jobs_lock:
            if self.max_jobs is not None and self.jobs_started >= self.max_jobs:
                return False
            self.jobs_started += 1
            return True

    def slot(self, k):
        conn = db.connect()
        wid = f'{self.host}:{os.getpid()}:{k}'
        while not self.stop.is_set():
            if not self._take_budget():
                break
            job = claim(conn, 'submission', wid)
            kind = 'submission'
            if job is None:
                job = claim(conn, 'match', wid)
                kind = 'match'
            if job is None:
                with self.jobs_lock:
                    self.jobs_started -= 1
                if self.until_empty:
                    active = sum(conn.execute(f"SELECT COUNT(*) FROM {t} WHERE status IN ('QUE','TRY','RUN')"
                                              ).fetchone()[0] for t in ('match', 'submission'))
                    if active == 0:
                        break
                self.stop.wait(self.poll)
                continue
            try:
                if kind == 'submission':
                    log.info('slot %d: compile submission %d (%s)', k, job['id'], job['package'])
                    st = compile_submission(conn, job, self.engine)
                else:
                    log.info('slot %d: match %d start', k, job['id'])
                    st = execute_match(conn, job, self.engine, timeout_per_game=self.timeout_per_game,
                                       stop=self.stop)
                row = conn.execute(f'SELECT logs FROM {kind} WHERE id=?', (job['id'],)).fetchone()
                last = (row['logs'].strip().splitlines() or [''])[-1]
                log.info('slot %d: %s %d -> %s %s', k, kind, job['id'], st, last)
            except AlreadyFinalized as e:
                log.warning('slot %d: %s (aborted)', k, e)
            except Exception as e:   # infrastructure error -> TRY (saturn: TaskErrored)
                log.exception('slot %d: %s %d failed', k, kind, job['id'])
                try:
                    report(conn, kind, job['id'], SaturnStatus.RETRY, logs=f'[replica] worker error: {e!r}\n')
                except AlreadyFinalized:
                    pass
        conn.close()

    def run(self):
        conn = db.connect()
        for mid, why in reap_stale(conn, self.timeout_per_game, self.host):
            log.info('reaped match %d: %s', mid, why)
        log.info('worker %s:%d: %d slots, %ds per game, engine %s', self.host, os.getpid(), self.slots,
                 self.timeout_per_game, self.engine.jar)
        threads = [threading.Thread(target=self.slot, args=(k,), daemon=True) for k in range(self.slots)]
        for t in threads:
            t.start()
        last_reap = time.time()
        while any(t.is_alive() for t in threads):
            time.sleep(1)
            if time.time() - last_reap > 60:
                last_reap = time.time()
                for mid, why in reap_stale(conn, self.timeout_per_game, self.host):
                    log.info('reaped match %d: %s', mid, why)
        rating.pump(conn)
        conn.close()
        log.info('worker stopped')


def setup_logging(to_file=True):
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    root = logging.getLogger('replica')
    root.setLevel(logging.INFO)
    if not root.handlers:
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        root.addHandler(sh)
        if to_file:
            db.ensure_dirs()
            fh = logging.FileHandler(db.path('logs', 'worker.log'))
            fh.setFormatter(fmt)
            root.addHandler(fh)
