"""Directory-backed queues: Pub/Sub topics, Cloud Tasks queues; and the Cloud Scheduler job records.

A queue is a directory with four subdirectories:
  ready/<id>.json                 deliverable now, consumed in file-name order (ids sort by creation time)
  leased/<id>.json                taken by a consumer (Pub/Sub: unacknowledged); returned to ready/ by recover()
  delayed/<due_ns>--<id>.json     redelivery after a nack or a retry backoff; promote_due() moves it back to ready/
  dead/<id>.json                  given up (Cloud Tasks after max attempts); kept for inspection
Every write is a temporary file plus a rename, and a lease is a rename, so concurrent consumers never take the
same message twice.

Layout under $GALAXY_HOME/spool/: pubsub/<topic id>/, tasks/<queue id>/, scheduler/<job id>.json.
"""
import itertools
import json
import os
import re
import threading
import time

from . import config, fsutil

ID_RE = re.compile(r'^[0-9]{20}-[0-9]+-[0-9]+$')
RESOURCE_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._~%+-]{0,254}$')
_counter = itertools.count()
_counter_lock = threading.Lock()


def new_id():
    """Sortable unique id: creation time in ns, pid, per-process counter."""
    with _counter_lock:
        n = next(_counter)
    return f'{time.time_ns():020d}-{os.getpid()}-{n}'


def check_resource(name, what):
    if not isinstance(name, str) or not RESOURCE_RE.match(name):
        raise ValueError(f'bad {what} id {name!r}')
    return name


def resource_id(path, kind):
    """projects/<p>/topics/<id> -> id (kind 'topics'); .../locations/<l>/queues/<id> (kind 'queues'); jobs."""
    parts = path.split('/') if isinstance(path, str) else []
    if len(parts) < 2 or parts[-2] != kind:
        raise ValueError(f'not a {kind} resource path: {path!r}')
    return check_resource(parts[-1], kind)


class Queue:
    def __init__(self, root):
        self.root = root
        self.ready = os.path.join(root, 'ready')
        self.leased = os.path.join(root, 'leased')
        self.delayed = os.path.join(root, 'delayed')
        self.dead = os.path.join(root, 'dead')

    def ensure(self):
        for d in (self.ready, self.leased, self.delayed, self.dead):
            os.makedirs(d, exist_ok=True)
        return self

    @staticmethod
    def _names(d):
        try:
            return sorted(f for f in os.listdir(d) if f.endswith('.json') and not f.startswith('.'))
        except FileNotFoundError:
            return []

    def put(self, obj, msg_id=None, delay=0.0):
        msg_id = msg_id or new_id()
        if not ID_RE.match(msg_id):
            raise ValueError(f'bad message id {msg_id!r}')
        if delay > 0:
            due = time.time_ns() + int(delay * 1e9)
            fsutil.atomic_write_json(os.path.join(self.delayed, f'{due:020d}--{msg_id}.json'), obj)
        else:
            fsutil.atomic_write_json(os.path.join(self.ready, f'{msg_id}.json'), obj)
        return msg_id

    def lease(self):
        """Take the oldest ready message: (id, obj), or None. A file that is not valid JSON is moved to dead/."""
        self.promote_due()
        for f in self._names(self.ready):
            src, dst = os.path.join(self.ready, f), os.path.join(self.leased, f)
            try:
                os.rename(src, dst)
            except FileNotFoundError:
                continue  # another consumer won
            msg_id = f[:-5]
            try:
                with open(dst) as fh:
                    return msg_id, json.load(fh)
            except ValueError:
                os.makedirs(self.dead, exist_ok=True)
                os.replace(dst, os.path.join(self.dead, f))
        return None

    def ack(self, msg_id):
        try:
            os.unlink(os.path.join(self.leased, f'{msg_id}.json'))
        except FileNotFoundError:
            pass

    def nack(self, msg_id, obj=None, delay=0.0):
        """Return a leased message (optionally rewritten) for redelivery now or after `delay` seconds."""
        src = os.path.join(self.leased, f'{msg_id}.json')
        if obj is None:
            with open(src) as fh:
                obj = json.load(fh)
        self.put(obj, msg_id, delay)
        try:
            os.unlink(src)
        except FileNotFoundError:
            pass

    def bury(self, msg_id, obj):
        fsutil.atomic_write_json(os.path.join(self.dead, f'{msg_id}.json'), obj)
        self.ack(msg_id)

    def promote_due(self, now_ns=None):
        now_ns = time.time_ns() if now_ns is None else now_ns
        for f in self._names(self.delayed):
            due, _, rest = f.partition('--')
            if not due.isdigit() or int(due) > now_ns:
                if due.isdigit():
                    break  # sorted by due time
                continue
            try:
                os.rename(os.path.join(self.delayed, f), os.path.join(self.ready, rest))
            except FileNotFoundError:
                pass

    def recover(self):
        """Return every leased message to ready/ (a consumer died before acking; Pub/Sub's ack deadline)."""
        n = 0
        for f in self._names(self.leased):
            try:
                os.rename(os.path.join(self.leased, f), os.path.join(self.ready, f))
                n += 1
            except FileNotFoundError:
                pass
        return n

    def counts(self):
        return {k: len(self._names(getattr(self, k))) for k in ('ready', 'leased', 'delayed', 'dead')}


def topic_queue(topic_id):
    return Queue(config.spool_dir('pubsub', check_resource(topic_id, 'topic')))


def task_queue(queue_id):
    return Queue(config.spool_dir('tasks', check_resource(queue_id, 'queue')))


def task_queue_ids():
    try:
        return sorted(d for d in os.listdir(config.spool_dir('tasks')) if RESOURCE_RE.match(d))
    except FileNotFoundError:
        return []


def scheduler_dir():
    return config.spool_dir('scheduler')


def job_path(job_id):
    return os.path.join(scheduler_dir(), check_resource(job_id, 'job') + '.json')
