#!/usr/bin/env python3
"""The replica's saturn: compiles submissions and runs matches for siarnaq, with saturn's message and report formats.

Runs as bcreplica in bc23-galaxy-saturn.service, inside a private network namespace (PrivateNetwork=yes: only `lo`,
no route anywhere). Its only way out is the relay's unix socket ($GALAXY_HOME/run/relay.sock), through which it posts
saturn's reports; the relay (relay.py) forwards them to siarnaq on 127.0.0.1:8024 with an ID token.

  python3 tools/galaxy/saturn.py run [--compile-slots 1] [--execute-slots 3]      (the service)
  python3 tools/galaxy/saturn.py status                                           (queue counts)

Pub/Sub: siarnaq's publisher stand-in spools each message as a JSON file ($GALAXY_HOME/spool/pubsub/<topic>/,
replica_gcp/spool.py). Compile slots consume the compile topic, execute slots the execute topic (galaxy runs them as
separate saturn instance groups: compile parallelism 1, execute 12 per instance). A slot leases the oldest message,
runs it and acks it, or nacks it for redelivery, exactly where saturn's subscriber does (pkg/saturn/queue.go):
invalid JSON -> ack (dropped); task finished OK!/aborted -> ack; task errored or interrupted -> nack. Messages
leased by a process that died go back to the queue when the service starts (Pub/Sub's ack deadline).

Task protocol (saturn pkg/saturn/task.go, report.go): report {"invocation": {"status": "RUN", ...}} first (409 from
siarnaq = already finalized: abort and ack), run the recipe, then report the outcome: the runner's details plus
"invocation": {status: OK!|TRY, logs, interrupted}. Logs are drained on every report, as saturn's buffer is.

Compile recipe (pkg/run/java.go): Hello world; Prepare scaffold; Download source code (zip, saturn's zip-slip check);
Build source code (javac -source 8 -target 8 -proc:none through tools/lib.sh compile_src, then the engine's
battlecode.instrumenter.Verifier, as galaxy-lite's worker does); Upload binary (zip of the class tree); Compile
succeeded. Failures of the user's code are OK! with accepted=false; infrastructure failures are TRY.

Execute recipe: Hello world; Prepare scaffold; Download binary (A and B); Run match (one engine run with all maps,
alternate order as requested; tools/replica/worker.py match_command: the pinned 3.0.15 jar plus engine/patch,
-Dbc.server.websocket=false); Upload replay (public); Determine scores (saturn's regex: [A wins, B wins]).

Deviations (docs/galaxy/README.md): no Gradle scaffold or git clone (the engine and JDK are pinned on the VM); a
nack is redelivered after GALAXY_NACK_DELAY seconds (default 10) instead of at once; scores that do not add up to
the number of maps, or a malformed binary archive, are an error (TRY) rather than an OK! siarnaq cannot rate; each
game has a time limit (GALAXY_GAME_TIMEOUT: 1800 s if unset; the deployed env sets 7200 s, docs/galaxy/README.md).
"""
import argparse
import base64
import http.client
import io
import json
import logging
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import traceback
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
for p in (HERE, TOOLS):
    if p not in sys.path:
        sys.path.insert(0, p)

from replica_gcp import config, spool, storage  # noqa: E402

LIB_SH = os.path.join(TOOLS, 'lib.sh')
JAVA_WINNER_REGEX = re.compile(r'(?m)^\[server\]\s*.*\(([AB])\) wins \(round [0-9]+\)$')   # saturn java.go:16
MAX_EXTRACTED = 256 * 1024 * 1024     # refuse archives that expand beyond this (zip bombs)
REVISION = 'bc23-replica tools/galaxy/saturn.py'

log = logging.getLogger('saturn')

RUNNING, COMPLETED, ABORTED, ERRORED, INTERRUPTED = range(5)
STATUS_STRING = {RUNNING: 'RUN', COMPLETED: 'OK!', ERRORED: 'TRY', INTERRUPTED: 'TRY', ABORTED: 'ABT'}


def game_timeout():
    return int(os.environ.get('GALAXY_GAME_TIMEOUT') or 1800)


def nack_delay():
    return float(os.environ.get('GALAXY_NACK_DELAY') or 10)


class TaskFinished(Exception):
    """saturn's panic(taskFinished{}): unwinds the recipe once the task has its final status."""


class ReportError(Exception):
    pass


class Interrupted(Exception):
    pass


# ---------------------------------------------------------------- the relay client (HTTP over a unix socket)
class _UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, path, timeout):
        super().__init__('relay', timeout=timeout)
        self._path = path

    def connect(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        s.connect(self._path)
        self.sock = s


def relay_post(path, obj, sock_path=None, timeout=150):
    """POST JSON to the relay; returns (status, parsed JSON body)."""
    conn = _UnixHTTPConnection(sock_path or config.relay_socket(), timeout)
    try:
        conn.request('POST', path, body=json.dumps(obj).encode(), headers={'Content-Type': 'application/json'})
        resp = conn.getresponse()
        body = resp.read()
        try:
            return resp.status, json.loads(body or b'{}')
        except ValueError:
            return resp.status, {'raw': body[:500].decode('utf-8', 'replace')}
    finally:
        conn.close()


class RelayReporter:
    """saturn's GCPTokenedReporter, with the relay doing the token and the loopback request."""

    def __init__(self, sock_path=None, post=relay_post):
        self.sock_path, self.post = sock_path, post

    def report(self, task):
        payload = build_report(task)
        meta = task.payload.get('metadata') or {}
        req = {'url': meta.get('report-url'), 'task_type': meta.get('task-type'), 'payload': payload}
        try:
            status, body = self.post('/v1/report', req, self.sock_path)
        except (OSError, http.client.HTTPException) as e:
            raise ReportError(f'relay unreachable: {e}') from None
        if status != 200:
            raise ReportError(f'relay refused the report: {status} {body}')
        code = int(body.get('status', 0))
        log.debug('report sent: %d', code)
        if code == 409:
            task.finish(ABORTED)
        if not 200 <= code < 300:
            raise ReportError(f'bad status code: {code}')


def build_report(task):
    """saturn report.go: the runner's details plus "invocation" (logs drained, as ioutil.ReadAll drains them)."""
    payload = dict(task.details or {})
    logs, task.logs = ''.join(task.logs), []
    payload['invocation'] = {'status': STATUS_STRING[task.status], 'logs': logs,
                             'interrupted': task.status == INTERRUPTED}
    return payload


# ---------------------------------------------------------------- tasks and recipes
class Task:
    def __init__(self, payload, reporter, stop=None):
        self.payload, self.reporter = payload, reporter
        self.stop = stop or threading.Event()
        self.status, self.details, self.logs = RUNNING, None, []

    def debug(self, msg):
        """A zerolog message inside the task's context: it lands in the task logs (saturn's hook)."""
        self.logs.append(f'{msg}\n')
        log.debug('%s', msg.rstrip()[:300])

    def finish(self, status, details=None):
        if self.status != RUNNING:
            return
        self.status, self.details = status, details
        raise TaskFinished()

    def run(self, runner):
        """Task.Run: True = acknowledge the message, False = nack it for redelivery."""
        err = None
        try:
            self.reporter.report(self)
            runner(self)
        except TaskFinished:
            pass
        except Exception as e:      # an error return in saturn
            err = e
            log.error('task error: %s\n%s', e, traceback.format_exc())
        if self.status == RUNNING:  # defer t.Finish(TaskErrored, nil)
            self.status = ERRORED
        try:
            self.finalize_report()
        except TaskFinished:
            pass
        except Exception as e:
            err = e if err is None else Exception(f'{err}, t.FinalizeReport: {e}')
            log.error('final report failed: %s', e)
        if self.status in (ERRORED, INTERRUPTED):
            return False
        return err is None

    def finalize_report(self):
        if self.status == ABORTED:
            return
        if self.stop.is_set() and self.status != COMPLETED:
            self.status = INTERRUPTED       # saturn: ctx.Err() != nil (it would override even a completed task)
        self.reporter.report(self)


def run_recipe(task, steps):
    n = len(steps)
    for i, (name, fn) in enumerate(steps, 1):
        task.debug(f'>>> Starting step {i}/{n}: {name}')
        try:
            fn(task)
        except (TaskFinished, Interrupted):
            raise
        except Exception as e:
            task.debug(f'Step returned with an error: {e}.')
            raise
        finally:
            task.debug(f'>>> Ending step {i}/{n}\n')


def step_hello(task):
    task.debug('Welcome to Saturn!')
    task.debug(f'Node: {socket.gethostname()}')
    task.debug(f'Revision: {REVISION}')


def run_cmd(task, cmd, timeout, cwd=None, env=None):
    """Run a command in its own process group; stop() kills the group. Returns (exit code, output)."""
    task.debug('Running command: ' + ' '.join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                            text=True, errors='replace', cwd=cwd, env=env, start_new_session=True)
    chunks, deadline = [], time.time() + timeout
    while True:
        try:
            out, _ = proc.communicate(timeout=1)
            chunks.append(out or '')
            break
        except subprocess.TimeoutExpired:
            if task.stop.is_set() or time.time() > deadline:
                _kill_group(proc)
                out, _ = proc.communicate()
                chunks.append(out or '')
                if task.stop.is_set():
                    raise Interrupted('stopped while running ' + os.path.basename(cmd[0]))
                return 124, ''.join(chunks)
    return proc.returncode, ''.join(chunks)


def _kill_group(proc):
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


# ---------------------------------------------------------------- storage (saturn pkg/run/file.go, gcs.go)
def file_spec(d, what):
    if not isinstance(d, dict) or not isinstance(d.get('bucket'), str) or not isinstance(d.get('name'), str):
        raise ValueError(f'bad file specification for {what}: {d!r}')
    storage.object_path(d['bucket'], d['name'])     # validates bucket and name
    return d['bucket'], d['name']


def get_archive(task, spec, root, reject_on_malformed=True):
    """GetArchive: fetch a zip and extract it under root; an unreadable archive or an entry outside root finishes a
    compile as OK! with accepted=false (reject_on_malformed) and is an error otherwise."""
    bucket, name = file_spec(spec, 'archive')
    data = storage.read_bytes(bucket, name)
    task.debug(f'File retrieved, total {len(data)} bytes.')
    root = os.path.abspath(root)

    def refuse(msg):
        task.debug(msg)
        if reject_on_malformed:
            task.finish(COMPLETED, {'accepted': False})
        raise ValueError(msg)

    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
        infos = zf.infolist()
    except (zipfile.BadZipFile, ValueError, OSError) as e:
        refuse(f'Archive is malformed: {e}')
    total = 0
    for info in infos:
        local = os.path.abspath(os.path.join(root, info.filename))
        if not local.startswith(root + os.sep):
            refuse(f'Archive contains illegal path: {local}')
        total += info.file_size
    if total > MAX_EXTRACTED:
        refuse(f'Archive expands to {total} bytes (limit {MAX_EXTRACTED}).')
    with zf:
        for info in infos:
            local = os.path.abspath(os.path.join(root, info.filename))
            task.debug(f'Extracting: {local}')
            if info.is_dir():
                continue
            os.makedirs(os.path.dirname(local), exist_ok=True)
            with zf.open(info) as r, open(local, 'wb') as w:
                shutil.copyfileobj(r, w)


def put_archive(spec, root, public):
    """PutArchive: zip every file under root (paths relative to root) into the object."""
    bucket, name = file_spec(spec, 'archive')
    tmp = root.rstrip('/') + '.zip'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zw:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames.sort()
            for f in sorted(filenames):
                p = os.path.join(dirpath, f)
                zw.write(p, os.path.relpath(p, root))
    storage.write_file(bucket, name, tmp, 'application/octet-stream', 'publicRead' if public else 'projectPrivate')
    os.unlink(tmp)


# ---------------------------------------------------------------- the engine
class EngineEnv:
    """The pinned engine (tools/lib.sh: jar sha256, engine/patch first on the classpath) and the JDK."""

    def __init__(self, engine=None):
        if engine is None:
            from replica import worker as rworker
            engine = rworker.Engine.from_lib()
        self.engine = engine

    def describe(self):
        return f'engine {os.path.basename(self.engine.jar)} (sha256 {self.engine.sha256[:16]}), java {self.engine.java}'


PACKAGE_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$')


class Runners:
    def __init__(self, workdir, engine_env, game_timeout_s=None):
        self.workdir, self.env = workdir, engine_env
        self.game_timeout = game_timeout_s or game_timeout()

    def _prepare(self, task):
        task.debug('Flushing build directory.')
        shutil.rmtree(self.workdir, ignore_errors=True)
        os.makedirs(self.workdir)
        task.debug(f'Using {self.env.describe()}.')

    # ---- compile
    def compile(self, task):
        d = task.payload.get('details') or {}
        src_root = os.path.join(self.workdir, 'src')
        classes = os.path.join(self.workdir, 'build', 'classes')

        def download(t):
            get_archive(t, d.get('source'), src_root, reject_on_malformed=True)

        def build(t):
            pkg = d.get('package') or ''
            if pkg == '':
                t.debug('Package name must not be empty.')
                t.finish(COMPLETED, {'accepted': False})
            os.makedirs(src_root, exist_ok=True)
            rc, out = run_cmd(t, ['bash', '-c', 'source "$1" >/dev/null && compile_src "$2" "$3"', '_', LIB_SH,
                                  src_root, classes], timeout=600)
            t.debug(out)
            if rc != 0 or not PACKAGE_RE.match(pkg):
                t.finish(COMPLETED, {'accepted': False})
            rc, out = run_cmd(t, [self.env.engine.java, '-cp', self.env.engine.cp, 'battlecode.instrumenter.Verifier',
                                  pkg, classes], timeout=600)
            t.debug(out)
            if rc != 0:
                t.finish(COMPLETED, {'accepted': False})

        def upload(t):
            put_archive(d.get('binary'), classes, public=False)

        def succeeded(t):
            t.finish(COMPLETED, {'accepted': True})

        run_recipe(task, [('Hello world', step_hello), ('Prepare scaffold', self._prepare),
                          ('Download source code', download), ('Build source code', build),
                          ('Upload binary', upload), ('Compile succeeded', succeeded)])

    # ---- execute
    def execute(self, task):
        from replica import worker as rworker
        d = task.payload.get('details') or {}
        data = os.path.join(self.workdir, 'data')
        replay = os.path.join(data, 'replay.bin')
        out_box = {}
        a, b = d.get('a') or {}, d.get('b') or {}
        maps = d.get('maps')
        if not isinstance(maps, list) or not maps or not all(isinstance(m, str) and re.match(r'^[A-Za-z0-9_-]+$', m)
                                                              for m in maps):
            raise ValueError(f'bad map list {maps!r}')

        def download(t):
            for key, sub in (('A', a), ('B', b)):
                get_archive(t, sub.get('binary'), os.path.join(data, key), reject_on_malformed=False)

        def run_match(t):
            cmd = rworker.match_command(
                self.env.engine, names=[str(a.get('team-name')), str(b.get('team-name'))],
                urls=[os.path.join(data, 'A'), os.path.join(data, 'B')],
                packages=[str(a.get('package')), str(b.get('package'))], maps=maps,
                alternate_order=bool(d.get('alternate-order')), replay=replay,
                timeout=self.game_timeout * len(maps))
            rc, out = run_cmd(t, cmd, timeout=self.game_timeout * len(maps) + 60, cwd=self.workdir)
            t.debug(out)
            if rc != 0:
                raise RuntimeError(f'RunCommand: exit status {rc}' + (' (time limit)' if rc == 124 else ''))
            out_box['out'] = out

        def upload_replay(t):
            bucket, name = file_spec(d.get('replay'), 'replay')
            storage.write_file(bucket, name, replay, 'application/octet-stream', 'publicRead')

        def scores(t):
            out = out_box.get('out')
            if out is None:
                raise RuntimeError('could not find match output')
            s = [0, 0]
            for w in JAVA_WINNER_REGEX.findall(out):
                if w == 'A':
                    s[0] += 1
                elif w == 'B':
                    s[1] += 1
                else:
                    raise RuntimeError(f'unknown winner: {w}')
            if sum(s) != len(maps):
                raise RuntimeError(f'could not determine winner: {sum(s)} winner lines for {len(maps)} maps')
            t.finish(COMPLETED, {'scores': s})

        run_recipe(task, [('Hello world', step_hello), ('Prepare scaffold', self._prepare),
                          ('Download binary', download), ('Run match', run_match), ('Upload replay', upload_replay),
                          ('Determine scores', scores)])


# ---------------------------------------------------------------- the subscriber
def parse_message(msg):
    """The TaskPayload of a spooled Pub/Sub message, or None for an invalid one (saturn acks those)."""
    try:
        payload = json.loads(base64.b64decode(msg['data'], validate=True))
    except (KeyError, TypeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    for k, t in (('episode', dict), ('metadata', dict), ('details', dict)):
        if k in payload and not isinstance(payload[k], t):
            return None
    return payload


class Executor:
    def __init__(self, compile_slots=1, execute_slots=3, engine_env=None, reporter=None, poll=1.0):
        self.compile_slots, self.execute_slots = compile_slots, execute_slots
        self.engine_env = engine_env
        self.reporter = reporter or RelayReporter()
        self.poll = poll
        self.stop = threading.Event()

    def handle(self, payload, workdir):
        """saturn.Handle: dispatch on metadata.task-type. Returns True to ack."""
        runners = Runners(workdir, self.engine_env)
        kind = (payload.get('metadata') or {}).get('task-type')
        runner = {'compile': runners.compile, 'execute': runners.execute}.get(kind)
        if runner is None:
            log.error('no such task type: %r', kind)
            return False
        return Task(payload, self.reporter, self.stop).run(runner)

    def slot(self, topic, k):
        q = spool.topic_queue(topic).ensure()
        workdir = config.galaxy_home('saturn', f'{topic}-{k}')
        while not self.stop.is_set():
            item = q.lease()
            if item is None:
                self.stop.wait(self.poll)
                continue
            msg_id, msg = item
            payload = parse_message(msg)
            if payload is None:
                log.error('slot %s-%d: invalid message %s; dropped', topic, k, msg_id)
                q.ack(msg_id)
                continue
            meta = payload.get('metadata') or {}
            log.info('slot %s-%d: starting %s %s', topic, k, meta.get('task-type'), meta.get('report-url'))
            t0 = time.time()
            try:
                ok = self.handle(payload, workdir)
            except Exception:
                log.exception('slot %s-%d: handler crashed', topic, k)
                ok = False
            if ok:
                q.ack(msg_id)
            else:
                msg = dict(msg, delivery_attempt=int(msg.get('delivery_attempt') or 0) + 1)
                q.nack(msg_id, msg, delay=0 if self.stop.is_set() else nack_delay())
            log.info('slot %s-%d: %s %s in %.0fs', topic, k, 'acked' if ok else 'nacked', msg_id, time.time() - t0)

    def run(self):
        for topic in (config.TOPIC_COMPILE, config.TOPIC_EXECUTE):
            n = spool.topic_queue(topic).ensure().recover()
            if n:
                log.info('returned %d unacknowledged %s message(s) to the queue', n, topic)
        if self.engine_env is None:
            self.engine_env = EngineEnv()
        log.info('saturn: %d compile + %d execute slots; %s; relay %s', self.compile_slots, self.execute_slots,
                 self.engine_env.describe(), config.relay_socket())
        threads = [threading.Thread(target=self.slot, args=(config.TOPIC_COMPILE, k), daemon=True)
                   for k in range(self.compile_slots)]
        threads += [threading.Thread(target=self.slot, args=(config.TOPIC_EXECUTE, k), daemon=True)
                    for k in range(self.execute_slots)]
        for t in threads:
            t.start()
        while any(t.is_alive() for t in threads):
            time.sleep(0.5)
        log.info('saturn stopped')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--compile-slots', type=int, default=int(os.environ.get('GALAXY_COMPILE_SLOTS') or 1))
    r.add_argument('--execute-slots', type=int, default=int(os.environ.get('GALAXY_EXECUTE_SLOTS') or 3))
    sub.add_parser('status')
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    if a.cmd == 'status':
        for topic in (config.TOPIC_COMPILE, config.TOPIC_EXECUTE):
            print(topic, spool.topic_queue(topic).counts())
        return 0
    if not (0 <= a.compile_slots <= 4 and 0 <= a.execute_slots <= 16):
        ap.error('slots: compile 0..4, execute 0..16')
    ex = Executor(a.compile_slots, a.execute_slots)

    def on_signal(signum, frame):
        log.info('signal %d: stopping (running tasks are reported as interrupted)', signum)
        ex.stop.set()
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    ex.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
