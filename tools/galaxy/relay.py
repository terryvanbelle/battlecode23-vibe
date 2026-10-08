#!/usr/bin/env python3
"""The replica's loopback relay: the only process that makes internal calls to siarnaq (127.0.0.1:8024).

Runs as bcreplica in bc23-galaxy-relay.service, in the host network namespace but fenced to loopback (the
bc23-replica slice's IPAddressAllow=localhost and the nftables table, which lets bcreplica open new connections to
ports 8023 and 8024 only). It does three jobs, each with the identity siarnaq expects from galaxy's Google services:

1. saturn reports: listens on a unix socket ($GALAXY_HOME/run/relay.sock, mode 600) for the sandboxed saturn
   (saturn.py, no network). POST /v1/report {"url", "task_type", "payload"}: the URL path must be a submission or
   match report endpoint (and match the task type); the relay posts the payload with User-Agent Galaxy-Saturn and an
   ID token for saturn-compile@ / saturn-execute@ (audience "siarnaq", as saturn's idtoken client) and answers
   {"status": <siarnaq's status>, "body": ...}.
2. Cloud Tasks: delivers the tasks that siarnaq's tasks_v2 stand-in spools ($GALAXY_HOME/spool/tasks/<queue>/):
   the task's HTTP request with User-Agent Google-Cloud-Tasks, X-CloudTasks-* headers and an ID token for the task's
   OIDC service account. Up to 3 concurrent dispatches per queue (galaxy's queues: max_concurrent_dispatches 3);
   non-2xx or no answer -> retried with Cloud Tasks' default backoff (0.1 s doubling, at most 3600 s) up to 100
   attempts, then moved to the queue's dead/ directory.
3. `relay.py fire-jobs` (run each minute by bc23-galaxy-scheduler.timer, installed disabled): Cloud Scheduler for
   the jobs siarnaq recorded (the autoscrim job): a job fires when its cron schedule matches the current minute in
   its time zone, with User-Agent Google-Cloud-Scheduler and an ID token; no retry (Cloud Scheduler's default).

Every request goes to 127.0.0.1:8024 only, whatever host the URL names; the Host header is the galaxy site's name
(siarnaq's ALLOWED_HOSTS). Only paths under /api/ are relayed.

  python3 tools/galaxy/relay.py serve                 (the service)
  python3 tools/galaxy/relay.py fire-jobs [--job ID --force]
  python3 tools/galaxy/relay.py status
"""
import argparse
import base64
import datetime
import http.client
import http.server
import json
import logging
import os
import re
import signal
import socketserver
import sys
import threading
import time
import urllib.parse
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from replica_gcp import config, cron, fsutil, spool, tokens  # noqa: E402

log = logging.getLogger('relay')
REPORT_PATH_RE = re.compile(r'^/api/compete/[A-Za-z0-9_-]{1,16}/(submission|match)/[0-9]{1,12}/report/$')
API_PATH_RE = re.compile(r'^/api/[A-Za-z0-9_./-]{1,512}$')
REPORT_KIND = {'compile': ('submission', config.SATURN_COMPILE_EMAIL),
               'execute': ('match', config.SATURN_EXECUTE_EMAIL)}
HOP_BY_HOP = {'host', 'authorization', 'user-agent', 'content-length', 'connection', 'transfer-encoding',
              'keep-alive', 'proxy-authorization', 'te', 'trailer', 'upgrade', 'x-forwarded-for',
              'x-forwarded-proto', 'x-forwarded-host'}
TASK_MAX_ATTEMPTS = 100
TASK_MIN_BACKOFF, TASK_MAX_BACKOFF, TASK_MAX_DOUBLINGS = 0.1, 3600.0, 16
TASK_CONCURRENCY = 3
HTTP_TIMEOUT = 120


def local_path(url, pattern=API_PATH_RE):
    """The path of a URL that siarnaq built (https://<ALLOWED_HOSTS[0]>/api/...), checked; ValueError otherwise."""
    if not isinstance(url, str):
        raise ValueError('no URL')
    u = urllib.parse.urlsplit(url)
    if u.scheme not in ('https', 'http') or u.query or u.fragment or u.username or u.password:
        raise ValueError(f'unexpected URL {url!r}')
    if '..' in u.path or '//' in u.path or not pattern.match(u.path):
        raise ValueError(f'path not allowed: {u.path!r}')
    return u.path


def siarnaq_request(method, path, body=b'', headers=None, timeout=HTTP_TIMEOUT):
    """One HTTP request to siarnaq on loopback. Returns (status, body bytes); raises OSError when unreachable."""
    host, port = config.siarnaq_addr()
    if host not in ('127.0.0.1', 'localhost', '::1'):
        raise ValueError('siarnaq must be on loopback')
    h = {'Host': config.galaxy_host(), 'Connection': 'close'}
    h.update(headers or {})
    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        conn.request(method, path, body=body, headers=h)
        resp = conn.getresponse()
        return resp.status, resp.read()
    finally:
        conn.close()


def bearer(email, audience):
    return 'Bearer ' + tokens.mint(email, audience)


# ---------------------------------------------------------------- 1. saturn reports over the unix socket
def relay_report(req, send=siarnaq_request):
    """Validate and forward one saturn report. Returns (http status for saturn, JSON answer)."""
    if not isinstance(req, dict):
        return 400, {'error': 'expected a JSON object'}
    kind = REPORT_KIND.get(req.get('task_type'))
    if kind is None:
        return 400, {'error': f'unknown task type {req.get("task_type")!r}'}
    try:
        path = local_path(req.get('url'), REPORT_PATH_RE)
    except ValueError as e:
        return 400, {'error': str(e)}
    if f'/{kind[0]}/' not in path:
        return 400, {'error': f'a {req.get("task_type")} task reports to /{kind[0]}/, not {path}'}
    payload = req.get('payload')
    if not isinstance(payload, dict) or not isinstance(payload.get('invocation'), dict):
        return 400, {'error': 'payload must hold an invocation'}
    body = json.dumps(payload).encode()
    try:
        status, resp = send('POST', path, body, {'Content-Type': 'application/json',
                                                 'User-Agent': config.SATURN_USER_AGENT,
                                                 'Authorization': bearer(kind[1], 'siarnaq')})
    except (OSError, http.client.HTTPException) as e:
        log.warning('report %s: siarnaq unreachable: %s', path, e)
        return 502, {'error': f'siarnaq unreachable: {e}'}
    log.info('report %s %s -> %d', path, payload['invocation'].get('status'), status)
    return 200, {'status': status, 'body': resp[:2000].decode('utf-8', 'replace')}


class ReportHandler(http.server.BaseHTTPRequestHandler):
    server_version = 'bc23-galaxy-relay'
    protocol_version = 'HTTP/1.0'

    def address_string(self):
        return 'saturn'

    def log_message(self, fmt, *args):
        log.debug('unix socket: ' + fmt, *args)

    def _answer(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != '/v1/report':
            return self._answer(404, {'error': 'unknown path'})
        try:
            n = int(self.headers.get('Content-Length') or 0)
        except ValueError:
            n = -1
        if not 0 < n <= 32 * 1024 * 1024:
            return self._answer(400, {'error': 'bad Content-Length'})
        try:
            req = json.loads(self.rfile.read(n))
        except ValueError:
            return self._answer(400, {'error': 'invalid JSON'})
        code, obj = relay_report(req)
        self._answer(code, obj)

    def do_GET(self):
        self._answer(405, {'error': 'POST /v1/report only'})


class UnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

    def server_bind(self):
        path = self.server_address
        os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
        old = os.umask(0o177)
        try:
            super().server_bind()
        finally:
            os.umask(old)


# ---------------------------------------------------------------- 2. Cloud Tasks
def task_backoff(attempt):
    return min(TASK_MAX_BACKOFF, TASK_MIN_BACKOFF * 2 ** min(max(attempt - 1, 0), TASK_MAX_DOUBLINGS))


def dispatch_task(queue_id, task_id, task, send=siarnaq_request, now=None):
    """Deliver one task. Returns True on a 2xx answer."""
    hr = task.get('http_request') or {}
    url = hr.get('url')
    try:
        path = local_path(url)
    except ValueError as e:
        log.error('task %s/%s: %s; not delivered', queue_id, task_id, e)
        return None   # permanent: bury
    method = hr.get('http_method') or 'POST'
    if method not in ('POST', 'GET', 'HEAD', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'):
        return None
    body = base64.b64decode(hr.get('body') or '')
    headers = {k: v for k, v in (hr.get('headers') or {}).items() if k.lower() not in HOP_BY_HOP}
    if body and not any(k.lower() == 'content-type' for k in headers):
        headers['Content-Type'] = 'application/octet-stream'
    created = task.get('create_time') or ''
    try:
        eta = datetime.datetime.fromisoformat(created).timestamp()
    except ValueError:
        eta = time.time()
    headers.update({'User-Agent': config.TASKS_USER_AGENT, 'X-CloudTasks-QueueName': queue_id,
                    'X-CloudTasks-TaskName': task_id,
                    'X-CloudTasks-TaskRetryCount': str(int(task.get('dispatch_count') or 0)),
                    'X-CloudTasks-TaskExecutionCount': str(int(task.get('response_count') or 0)),
                    'X-CloudTasks-TaskETA': f'{eta:.6f}'})
    oidc = hr.get('oidc_token') or {}
    email = oidc.get('service_account_email')
    if email in config.ADMIN_EMAILS:
        headers['Authorization'] = bearer(email, oidc.get('audience') or url)
    elif email:
        log.warning('task %s/%s: OIDC e-mail %r is not a replica service account; sent without a token',
                    queue_id, task_id, email)
    try:
        status, resp = send(method, path, body, headers)
    except (OSError, http.client.HTTPException) as e:
        log.warning('task %s/%s %s %s: no answer: %s', queue_id, task_id, method, path, e)
        task['last_attempt'] = {'status': None, 'error': str(e), 'time': time.time()}
        return False
    task['response_count'] = int(task.get('response_count') or 0) + 1
    task['last_attempt'] = {'status': status, 'body': resp[:300].decode('utf-8', 'replace'), 'time': time.time()}
    ok = 200 <= status < 300
    (log.info if ok else log.warning)('task %s/%s %s %s -> %d', queue_id, task_id, method, path, status)
    return ok


class TaskDispatcher:
    def __init__(self, stop, poll=0.5, send=siarnaq_request):
        self.stop, self.poll, self.send = stop, poll, send
        self.started = set()
        self.threads = []

    def process_one(self, queue_id):
        q = spool.task_queue(queue_id)
        item = q.lease()
        if item is None:
            return False
        task_id, task = item
        ok = dispatch_task(queue_id, task_id, task, self.send)
        if ok:
            q.ack(task_id)
            return True
        task['dispatch_count'] = int(task.get('dispatch_count') or 0) + 1
        if ok is None or task['dispatch_count'] >= TASK_MAX_ATTEMPTS:
            log.error('task %s/%s: giving up after %d attempt(s)', queue_id, task_id, task['dispatch_count'])
            q.bury(task_id, task)
        else:
            q.nack(task_id, task, delay=task_backoff(task['dispatch_count']))
        return True

    def worker(self, queue_id):
        while not self.stop.is_set():
            try:
                busy = self.process_one(queue_id)
            except Exception:
                log.exception('task queue %s: dispatcher error', queue_id)
                busy = False
            if not busy:
                self.stop.wait(self.poll)

    def discover(self):
        for queue_id in spool.task_queue_ids():
            if queue_id in self.started:
                continue
            n = spool.task_queue(queue_id).ensure().recover()
            if n:
                log.info('task queue %s: %d leased task(s) returned', queue_id, n)
            self.started.add(queue_id)
            for _ in range(TASK_CONCURRENCY):
                t = threading.Thread(target=self.worker, args=(queue_id,), daemon=True)
                t.start()
                self.threads.append(t)


# ---------------------------------------------------------------- 3. Cloud Scheduler jobs (timer)
def load_jobs():
    d = spool.scheduler_dir()
    jobs = []
    try:
        names = sorted(f for f in os.listdir(d) if f.endswith('.json') and not f.startswith('.'))
    except FileNotFoundError:
        return jobs
    for f in names:
        try:
            with open(os.path.join(d, f)) as fh:
                jobs.append((f[:-5], json.load(fh)))
        except (OSError, ValueError) as e:
            log.error('job %s unreadable: %s', f, e)
    return jobs


def fire_job(job_id, job, send=siarnaq_request):
    ht = job.get('http_target') or {}
    path = local_path(ht.get('uri'))
    headers = {k: v for k, v in (ht.get('headers') or {}).items() if k.lower() not in HOP_BY_HOP}
    headers['User-Agent'] = config.SCHEDULER_USER_AGENT
    headers['X-CloudScheduler'] = 'true'
    headers['X-CloudScheduler-JobName'] = job_id
    oidc = ht.get('oidc_token') or {}
    if oidc.get('service_account_email') in config.ADMIN_EMAILS:
        headers['Authorization'] = bearer(oidc['service_account_email'], oidc.get('audience') or ht.get('uri'))
    status, resp = send(ht.get('http_method') or 'POST', path, base64.b64decode(ht.get('body') or ''), headers)
    log.info('job %s %s -> %d %s', job_id, path, status, resp[:200].decode('utf-8', 'replace'))
    return status


def fire_jobs(now=None, only=None, force=False, send=siarnaq_request):
    """Fire every recorded job whose schedule matches this minute (once per minute: a state file remembers)."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    fired = []
    for job_id, job in load_jobs():
        if only and job_id != only:
            continue
        try:
            tz = zoneinfo.ZoneInfo(job.get('time_zone') or 'Etc/UTC')
            local = now.astimezone(tz).replace(second=0, microsecond=0)
            due = force or cron.matches(job.get('schedule') or '', local)
        except (ValueError, zoneinfo.ZoneInfoNotFoundError) as e:
            log.error('job %s: bad schedule or time zone: %s', job_id, e)
            continue
        if not due:
            continue
        stamp = local.isoformat()
        state = os.path.join(spool.scheduler_dir(), '.state', job_id)
        try:
            with open(state) as fh:
                if fh.read().strip() == stamp and not force:
                    continue
        except FileNotFoundError:
            pass
        fsutil.atomic_write_bytes(state, (stamp + '\n').encode())
        try:
            fired.append((job_id, fire_job(job_id, job, send)))
        except (OSError, http.client.HTTPException, ValueError) as e:
            log.error('job %s: not delivered: %s', job_id, e)
            fired.append((job_id, None))
    return fired


# ---------------------------------------------------------------- main
def serve():
    stop = threading.Event()
    server = UnixServer(config.relay_socket(), ReportHandler)
    th = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.5}, daemon=True)
    th.start()
    disp = TaskDispatcher(stop)

    def on_signal(signum, frame):
        log.info('signal %d: stopping', signum)
        stop.set()
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    log.info('relay: unix socket %s -> http://%s:%d (Host: %s)', config.relay_socket(), *config.siarnaq_addr(),
             config.galaxy_host())
    while not stop.is_set():
        disp.discover()
        stop.wait(2)
    server.shutdown()
    server.server_close()
    try:
        os.unlink(config.relay_socket())
    except FileNotFoundError:
        pass
    log.info('relay stopped')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('serve')
    f = sub.add_parser('fire-jobs')
    f.add_argument('--job')
    f.add_argument('--force', action='store_true', help='fire now whatever the schedule says (needs --job)')
    sub.add_parser('status')
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    if a.cmd == 'serve':
        serve()
    elif a.cmd == 'fire-jobs':
        if a.force and not a.job:
            ap.error('--force needs --job')
        for job_id, status in fire_jobs(only=a.job, force=a.force):
            print(job_id, status)
    else:
        for q in spool.task_queue_ids():
            print('tasks', q, spool.task_queue(q).counts())
        for job_id, job in load_jobs():
            print('job', job_id, repr(job.get('schedule')), job.get('time_zone'),
                  (job.get('http_target') or {}).get('uri'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
