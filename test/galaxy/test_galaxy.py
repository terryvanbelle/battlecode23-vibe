#!/usr/bin/env python3
"""Tests of the galaxy replica's back end (tools/galaxy): Google Cloud stand-ins, spool queues, ID tokens, cron, the
saturn replacement (messages, report payloads, compile success/failure, path layout), the relay, and the deploy
renderers. Standard library only; no network, no Django, no game (the execute path runs a fake engine). The compile
tests use the real JDK and engine jar when present (tools/lib.sh) and skip otherwise.
Run: python3 test/galaxy/test_galaxy.py
"""
import base64
import datetime
import importlib
import io
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
GALAXY = os.path.join(REPO, 'tools', 'galaxy')
STANDINS = os.path.join(GALAXY, 'standins')
for p in (STANDINS, GALAXY, os.path.join(REPO, 'tools')):
    if p not in sys.path:
        sys.path.insert(0, p)

TMP = tempfile.mkdtemp(prefix='galaxy-test-')
os.environ.update(GALAXY_HOME=os.path.join(TMP, 'home'), GALAXY_STORAGE_ROOT=os.path.join(TMP, 'storage'),
                  GALAXY_BASE_HOST='1-2-3-4.sslip.io', GALAXY_RELAY_SOCKET=os.path.join(TMP, 'r.sock'),
                  GALAXY_NACK_DELAY='0')

from replica_gcp import config, cron, fsutil, spool, storage, tokens  # noqa: E402

tokens.generate_key()
logging.disable(logging.CRITICAL)      # saturn/relay log expected errors (tracebacks) in these tests

import google  # noqa: E402
import google.auth  # noqa: E402
import google.auth.exceptions  # noqa: E402
import google.auth.transport.requests  # noqa: E402
import google.cloud.pubsub as pubsub  # noqa: E402
import google.cloud.scheduler as scheduler  # noqa: E402
import google.cloud.secretmanager as secretmanager  # noqa: E402
import google.cloud.storage as gcs  # noqa: E402
import google.cloud.tasks_v2 as tasks_v2  # noqa: E402
from google.auth import impersonated_credentials  # noqa: E402
from google.oauth2 import id_token  # noqa: E402

import relay  # noqa: E402
import saturn  # noqa: E402

SECURE = config.BUCKET_SECURE


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


def read(path, mode='r'):
    with open(path, mode, **({} if 'b' in mode else {'errors': 'replace'})) as fh:
        return fh.read()


def zip_bytes(entries):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        for name, data in entries.items():
            z.writestr(name, data)
    return buf.getvalue()


# ------------------------------------------------------------------------------------------------ stand-in packages
class StandinImports(unittest.TestCase):
    def test_every_google_module_is_a_standin(self):
        for m in (google, google.auth, id_token, gcs, pubsub, tasks_v2, scheduler, secretmanager,
                  impersonated_credentials, google.auth.transport.requests):
            self.assertTrue(os.path.abspath(m.__file__).startswith(STANDINS + os.sep), m.__name__)

    def test_fail_closed(self):
        with self.assertRaises(AttributeError):
            gcs.Batch                                           # noqa: B018
        with self.assertRaises(ImportError):
            importlib.import_module('google.cloud.bigquery')
        with self.assertRaises(ImportError):
            importlib.import_module('google.api_core.exceptions')
        with self.assertRaises(NotImplementedError):
            gcs.Client().list_buckets()
        with self.assertRaises(NotImplementedError):
            gcs.Client().bucket(SECURE).blob('a/b').rewrite(None)
        with self.assertRaises(NotImplementedError):
            secretmanager.SecretManagerServiceClient()
        with self.assertRaises(google.auth.exceptions.DefaultCredentialsError):
            google.auth.default()
        with self.assertRaises(google.auth.exceptions.TransportError):
            google.auth.transport.requests.Request()('https://example.invalid/')
        with self.assertRaises(NotImplementedError):
            id_token.fetch_id_token(None, 'x')
        with self.assertRaises(NotImplementedError):
            pubsub.SubscriberClient()

    def test_no_network_code_or_external_host(self):
        """The stand-ins and their back end never open sockets and name no Google/Battlecode host."""
        bad_import = re.compile(r'^\s*(import|from)\s+(socket|http|urllib(?!\.parse\b)|requests|ssl|smtplib|ftplib)\b',
                                re.M)
        for root in (STANDINS, os.path.join(GALAXY, 'replica_gcp')):
            for dirpath, _, files in os.walk(root):
                for f in files:
                    if f.endswith('.py'):
                        text = read(os.path.join(dirpath, f))
                        self.assertIsNone(bad_import.search(text), f)
                        self.assertIsNone(re.search(r'https?://', text), f)
        for dirpath, dirnames, files in os.walk(GALAXY):
            dirnames[:] = [d for d in dirnames if d not in ('frontend', '__pycache__')]
            for f in files:
                text = read(os.path.join(dirpath, f))
                for needle in ('battlecode.org', 'googleapis', 'mailjet.com', 'challonge.com', 'mitbattlecode'):
                    self.assertFalse(needle in text, f'{os.path.join(dirpath, f)} names {needle}')
                urls = set(re.findall(r'https?://[A-Za-z0-9.-]+', text)) - {'https://github.com'}
                urls = {u for u in urls if not re.match(r'https?://(127\.0\.0\.1|localhost|galaxy\.)', u)}
                self.assertEqual(urls, set(), os.path.join(dirpath, f))


class Storage(unittest.TestCase):
    def test_write_read_metadata_titan(self):
        c = gcs.Client(credentials=object())
        blob = c.bucket(SECURE).blob('episode/bc23/submission/7/source.zip')
        with blob.open('wb') as f:
            f.write(b'PK')
            f.write(b'data')
        self.assertTrue(os.path.isfile(os.path.join(TMP, 'storage', SECURE, 'episode/bc23/submission/7/source.zip')))
        got = c.bucket(SECURE).get_blob('episode/bc23/submission/7/source.zip')
        self.assertIsNone(got.metadata)
        self.assertEqual(got.download_as_bytes(), b'PKdata')
        self.assertEqual(got.size, 6)
        got.metadata = {'Titan-Status': 'Unverified'}       # titan.request_scan
        got.patch()
        again = c.bucket(SECURE).get_blob('episode/bc23/submission/7/source.zip')
        self.assertEqual(again.metadata, {'Titan-Status': 'Verified'})
        self.assertIsNone(c.bucket(SECURE).get_blob('episode/bc23/submission/8/source.zip'))
        url = got.generate_signed_url(expiration=datetime.timedelta(hours=1), method='GET',
                                      credentials=impersonated_credentials.Credentials(
                                          source_credentials=None, target_principal='x@y.invalid',
                                          target_scopes='scope', lifetime=5))
        self.assertEqual(url, f'/storage/{SECURE}/episode/bc23/submission/7/source.zip')
        with self.assertRaises(NotImplementedError):
            got.generate_signed_url(method='PUT')

    def test_public_url_and_text_modes(self):
        b = gcs.Client.create_anonymous_client().bucket(config.BUCKET_PUBLIC).blob('team/3/avatar.png')
        self.assertEqual(b.public_url, f'/storage/{config.BUCKET_PUBLIC}/team/3/avatar.png')
        b.upload_from_string(b'\x89PNG')
        self.assertEqual(b.download_as_bytes(), b'\x89PNG')
        t = gcs.Client().bucket(config.BUCKET_EPHEMERAL).blob('notes/a b.txt')
        with t.open('w') as fh:
            fh.write('héllo')
        self.assertEqual(t.download_as_text(), 'héllo')
        self.assertEqual(t.public_url, f'/storage/{config.BUCKET_EPHEMERAL}/notes/a%20b.txt')
        with t.open('wb', content_type='application/pdf', predefined_acl='publicRead') as fh:
            fh.write(b'%PDF')
        meta = storage.load_meta(config.BUCKET_EPHEMERAL, 'notes/a b.txt')
        self.assertEqual((meta['contentType'], meta['acl'], meta['size']), ('application/pdf', 'publicRead', '4'))

    def test_failed_write_leaves_nothing(self):
        blob = gcs.Client().bucket(SECURE).blob('x/partial.zip')
        with self.assertRaises(RuntimeError):
            with blob.open('wb') as f:
                f.write(b'half')
                raise RuntimeError('boom')
        self.assertFalse(blob.exists())
        self.assertEqual([f for f in os.listdir(os.path.join(TMP, 'storage', SECURE, 'x'))], [])

    def test_names_that_escape_are_refused(self):
        b = gcs.Client().bucket(SECURE)
        for name in ('../x', '/abs', 'a//b', 'a/./b', 'a/../b', '.hidden', 'a/.tmp-1', 'a\\b', 'a\nb', ''):
            with self.assertRaises(ValueError, msg=repr(name)):
                b.blob(name)
        for bucket in ('..', 'UPPER', 'a', '../etc', 'a/b'):
            with self.assertRaises(ValueError, msg=repr(bucket)):
                gcs.Client().bucket(bucket)


# ------------------------------------------------------------------------------------------------ queues and tokens
class Spool(unittest.TestCase):
    def test_lease_ack_nack_delay_recover(self):
        q = spool.Queue(os.path.join(TMP, 'q1')).ensure()
        a, b = q.put({'n': 1}), q.put({'n': 2})
        self.assertLess(a, b)
        self.assertEqual(q.lease(), (a, {'n': 1}))
        q.nack(a, {'n': 1, 'again': True}, delay=30)
        self.assertEqual(q.lease(), (b, {'n': 2}))
        self.assertIsNone(q.lease())
        q.promote_due(now_ns=time.time_ns() + 31 * 10**9)
        self.assertEqual(q.lease(), (a, {'n': 1, 'again': True}))
        self.assertEqual(q.counts(), {'ready': 0, 'leased': 2, 'delayed': 0, 'dead': 0})
        q.ack(a)
        self.assertEqual(q.recover(), 1)              # b was leased by a "dead" consumer
        self.assertEqual(q.lease()[0], b)
        q.bury(b, {'n': 2})
        self.assertEqual(q.counts()['dead'], 1)

    def test_concurrent_consumers_take_each_message_once(self):
        q = spool.Queue(os.path.join(TMP, 'q2')).ensure()
        ids = {q.put({'i': i}) for i in range(60)}
        got, lock = [], threading.Lock()

        def consume():
            while True:
                item = q.lease()
                if item is None:
                    return
                with lock:
                    got.append(item[0])
                q.ack(item[0])
        ts = [threading.Thread(target=consume) for _ in range(6)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        self.assertEqual(sorted(got), sorted(ids))

    def test_resource_ids(self):
        self.assertEqual(spool.resource_id('projects/p/topics/replica-siarnaq-compile', 'topics'),
                         'replica-siarnaq-compile')
        for bad in ('projects/p/topics/../x', 'projects/p/queues/q', 'x', 'projects/p/topics/a/b'):
            with self.assertRaises(ValueError, msg=bad):
                spool.resource_id(bad, 'topics')


class Tokens(unittest.TestCase):
    def test_round_trip_and_rejections(self):
        t = tokens.mint('saturn-execute@bc23-replica.invalid', 'siarnaq')
        claims = id_token.verify_oauth2_token(id_token=t, request=google.auth.transport.requests.Request())
        self.assertEqual(claims['email'], 'saturn-execute@bc23-replica.invalid')
        self.assertEqual(claims['aud'], 'siarnaq')
        h, p, s = t.split('.')
        forged_payload = base64.urlsafe_b64encode(json.dumps(dict(claims, email='x@y.z')).encode()).rstrip(b'=')
        bad = [h + '.' + p + '.' + s[:-2] + ('AA' if s[-2:] != 'AA' else 'BB'),       # signature
               h + '.' + forged_payload.decode() + '.' + s,                          # payload swapped
               'eyJhbGciOiJub25lIn0.' + p + '.',                                       # alg none
               tokens.mint('a@b.c', 'siarnaq', now=time.time() - 7200),                 # expired
               'garbage', '', 'a.b.c', t + 'x']
        for b in bad:
            with self.assertRaises(ValueError, msg=b[:40]):
                id_token.verify_oauth2_token(b, None)
        with self.assertRaises(ValueError):
            tokens.verify(t, audience='other')

    def test_key_is_private(self):
        st = os.stat(tokens.key_path())
        self.assertEqual(st.st_mode & 0o777, 0o600)
        with open(tokens.key_path()) as fh:
            self.assertGreaterEqual(len(bytes.fromhex(fh.read().strip())), 32)


class Cron(unittest.TestCase):
    def test_matches(self):
        d = datetime.datetime
        self.assertTrue(cron.matches('0 */4 * * *', d(2026, 10, 7, 8, 0)))
        self.assertFalse(cron.matches('0 */4 * * *', d(2026, 10, 7, 9, 0)))
        self.assertFalse(cron.matches('0 */4 * * *', d(2026, 10, 7, 8, 1)))
        self.assertTrue(cron.matches('30 9-17/2 * jan-mar,oct mon-fri', d(2026, 10, 7, 11, 30)))   # a Wednesday
        self.assertFalse(cron.matches('30 9-17/2 * * sat,sun', d(2026, 10, 7, 11, 30)))
        self.assertTrue(cron.matches('0 0 1 * 7', d(2026, 10, 4, 0, 0)))    # Sunday (7) OR the 1st
        self.assertTrue(cron.matches('0 0 1 * 7', d(2026, 10, 1, 0, 0)))
        self.assertEqual(cron.next_fire('0 */4 * * *', d(2026, 10, 7, 8, 0)), d(2026, 10, 7, 12, 0))
        for bad in ('* * * *', '61 * * * *', '* 24 * * *', '*/0 * * * *', '5-1 * * * *', 'x * * * *'):
            with self.assertRaises(ValueError, msg=bad):
                cron.parse(bad)


# ------------------------------------------------------------------------------------------- publishers (siarnaq side)
class Publishers(unittest.TestCase):
    def test_pubsub_publish_as_siarnaq_does(self):
        client = pubsub.PublisherClient(credentials=None,
                                        publisher_options=pubsub.types.PublisherOptions(enable_message_ordering=True),
                                        client_options={'api_endpoint': 'ignored:443'})
        topic = client.topic_path(config.PROJECT, config.TOPIC_COMPILE)
        self.assertEqual(topic, f'projects/{config.PROJECT}/topics/{config.TOPIC_COMPILE}')
        payload = {'episode': {'name': 'bc23', 'language': 'java8', 'scaffold': ''},
                   'metadata': {'report-url': 'https://galaxy.x/api/compete/bc23/submission/1/report/',
                                'task-type': 'compile'},
                   'details': {'source': {'bucket': SECURE, 'name': 'a.zip'}, 'package': 'p'}}
        mid = client.publish(topic=topic, data=json.dumps(payload).encode(), ordering_key='compile-order').result()
        q = spool.topic_queue(config.TOPIC_COMPILE)
        leased = q.lease()
        self.assertEqual(leased[0], mid)
        self.assertEqual(leased[1]['ordering_key'], 'compile-order')
        self.assertEqual(saturn.parse_message(leased[1]), payload)
        q.ack(mid)
        with self.assertRaises(ValueError):
            pubsub.PublisherClient().publish(topic, b'x', ordering_key='k').result()
        with self.assertRaises(TypeError):
            client.publish(topic, 'not bytes')
        fut = client.publish('projects/p/queues/not-a-topic', b'x', ordering_key='k')
        self.assertIsInstance(fut.exception(), ValueError)

    def test_cloud_tasks_create_task_as_siarnaq_does(self):
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(config.PROJECT, config.LOCATION, config.QUEUE_RATING)
        task = tasks_v2.Task(http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST, url='https://galaxy.x/api/compete/bc23/match/5/rating_update/',
            oidc_token=tasks_v2.OidcToken(service_account_email=config.SERVICE_EMAIL)))
        made = client.create_task(request=dict(parent=parent, task=task))
        self.assertTrue(made.name.startswith(parent + '/tasks/'))
        q = spool.task_queue(config.QUEUE_RATING)
        tid, rec = q.lease()
        self.assertEqual(rec['http_request']['http_method'], 'POST')
        self.assertEqual(rec['http_request']['oidc_token']['service_account_email'], config.SERVICE_EMAIL)
        q.ack(tid)
        with self.assertRaises(NotImplementedError):
            tasks_v2.Task(app_engine_http_request={'x': 1})
        with self.assertRaises(TypeError):
            tasks_v2.HttpRequest(nonsense=1)

    def test_scheduler_records_jobs(self):
        parent = f'projects/{config.PROJECT}/locations/{config.LOCATION}'
        name = f'{parent}/jobs/replica-autoscrim-bc23'
        job = scheduler.Job(name=name, description='d', schedule='0 */4 * * *', time_zone='UTC',
                            http_target=scheduler.HttpTarget(
                                uri='https://galaxy.x/api/episode/e/bc23/autoscrim/', http_method=scheduler.HttpMethod.POST,
                                headers={'Content-Type': 'application/json; charset=utf-8'}, body=b'{"best_of": 3}',
                                oidc_token=scheduler.OidcToken(service_account_email=config.SERVICE_EMAIL)))
        client = scheduler.CloudSchedulerClient(credentials=None)
        client.create_job(request=dict(parent=parent, job=job))
        rec = json.loads(read(spool.job_path('replica-autoscrim-bc23')))
        self.assertEqual((rec['schedule'], rec['http_target']['http_method']), ('0 */4 * * *', 'POST'))
        job.schedule = 'not cron'
        with self.assertRaises(ValueError):
            client.update_job(request=dict(job=job))
        client.delete_job(request=dict(name=name))
        self.assertFalse(os.path.exists(spool.job_path('replica-autoscrim-bc23')))


# ------------------------------------------------------------------------------------------------ saturn replacement
class FakeReporter:
    def __init__(self, codes=None):
        self.codes, self.reports = list(codes or []), []

    def report(self, task):
        payload = saturn.build_report(task)
        self.reports.append(payload)
        code = self.codes.pop(0) if self.codes else 204
        if code == 409:
            task.finish(saturn.ABORTED)
        if not 200 <= code < 300:
            raise saturn.ReportError(f'bad status code: {code}')


def compile_payload(sub_id, package='examplefuncsplayer'):
    return {'episode': {'name': 'bc23', 'language': 'java8', 'scaffold': ''},
            'metadata': {'report-url': f'https://galaxy.x/api/compete/bc23/submission/{sub_id}/report/',
                         'task-type': 'compile'},
            'details': {'source': {'bucket': SECURE, 'name': f'episode/bc23/submission/{sub_id}/source.zip'},
                        'binary': {'bucket': SECURE, 'name': f'episode/bc23/submission/{sub_id}/binary.zip'},
                        'team-name': 'team', 'package': package}}


class TaskProtocol(unittest.TestCase):
    def run_task(self, runner, codes=None, stop=False):
        rep = FakeReporter(codes)
        ev = threading.Event()
        if stop:
            ev.set()
        ack = saturn.Task(compile_payload(1), rep, ev).run(runner)
        return ack, rep.reports

    def test_report_payloads(self):
        def runner(t):
            t.debug('hello')
            t.finish(saturn.COMPLETED, {'accepted': True})
        ack, reports = self.run_task(runner)
        self.assertTrue(ack)
        self.assertEqual(reports[0], {'invocation': {'status': 'RUN', 'logs': '', 'interrupted': False}})
        self.assertEqual(reports[1], {'accepted': True,
                                      'invocation': {'status': 'OK!', 'logs': 'hello\n', 'interrupted': False}})

    def test_409_on_start_aborts_and_acks(self):
        ran = []
        ack, reports = self.run_task(lambda t: ran.append(1), codes=[409])
        self.assertTrue(ack)
        self.assertEqual((ran, len(reports)), ([], 1))

    def test_errors_report_try_and_nack(self):
        def runner(t):
            raise RuntimeError('engine exploded')
        ack, reports = self.run_task(runner)
        self.assertFalse(ack)
        self.assertEqual(reports[-1]['invocation'], {'status': 'TRY', 'logs': '', 'interrupted': False})
        ack, reports = self.run_task(lambda t: None, codes=[500])     # first report fails: TRY, nack
        self.assertFalse(ack)
        self.assertEqual(reports[-1]['invocation']['status'], 'TRY')
        ack, _ = self.run_task(lambda t: t.finish(saturn.COMPLETED, {'scores': [1, 0]}), codes=[204, 502])
        self.assertFalse(ack)                                          # final report not delivered: redeliver

    def test_interrupted(self):
        def runner(t):
            raise saturn.Interrupted('stopped')
        ack, reports = self.run_task(runner, stop=True)
        self.assertFalse(ack)
        self.assertEqual(reports[-1]['invocation'], {'status': 'TRY', 'logs': '', 'interrupted': True})

    def test_recipe_logs_like_saturn(self):
        rep = FakeReporter()
        t = saturn.Task(compile_payload(1), rep)
        t.run(lambda task: saturn.run_recipe(task, [('Hello world', saturn.step_hello),
                                                    ('Done', lambda x: x.finish(saturn.COMPLETED, {'accepted': True}))]))
        logs = rep.reports[-1]['invocation']['logs']
        self.assertIn('>>> Starting step 1/2: Hello world\nWelcome to Saturn!\n', logs)
        self.assertIn('>>> Ending step 2/2\n\n', logs)

    def test_parse_message(self):
        good = {'data': base64.b64encode(json.dumps({'metadata': {'task-type': 'compile'}}).encode()).decode()}
        self.assertEqual(saturn.parse_message(good), {'metadata': {'task-type': 'compile'}})
        for bad in ({'data': 'not base64!'}, {'data': base64.b64encode(b'{nope').decode()}, {},
                    {'data': base64.b64encode(b'[1]').decode()},
                    {'data': base64.b64encode(b'{"metadata": 3}').decode()}):
            self.assertIsNone(saturn.parse_message(bad), bad)

    def test_unknown_task_type_is_nacked(self):
        ex = saturn.Executor(engine_env=object(), reporter=FakeReporter())
        self.assertFalse(ex.handle({'metadata': {'task-type': 'mine-bitcoin'}}, os.path.join(TMP, 'w')))


class Archives(unittest.TestCase):
    def setUp(self):
        self.rep = FakeReporter()
        self.task = saturn.Task(compile_payload(2), self.rep)
        self.root = tempfile.mkdtemp(dir=TMP)

    def put(self, name, data):
        storage.write_bytes(SECURE, name, data)
        return {'bucket': SECURE, 'name': name}

    def test_extracts(self):
        spec = self.put('z/ok.zip', zip_bytes({'pkg/A.java': 'class A {}', 'pkg/sub/B.java': 'x'}))
        saturn.get_archive(self.task, spec, self.root)
        self.assertTrue(os.path.isfile(os.path.join(self.root, 'pkg', 'sub', 'B.java')))

    def test_zip_slip_and_malformed_reject_the_submission(self):
        for name, data in (('z/slip.zip', zip_bytes({'../evil.java': 'x'})),
                           ('z/abs.zip', zip_bytes({'/etc/evil': 'x'})),
                           ('z/bad.zip', b'this is not a zip')):
            task = saturn.Task(compile_payload(2), FakeReporter())
            with self.assertRaises(saturn.TaskFinished, msg=name):
                saturn.get_archive(task, self.put(name, data), self.root)
            self.assertEqual((task.status, task.details), (saturn.COMPLETED, {'accepted': False}))
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.root), 'evil.java')))
        with self.assertRaises(ValueError):          # a binary (execute) is an error, not a rejection
            saturn.get_archive(saturn.Task({}, FakeReporter()), self.put('z/bad2.zip', b'nope'), self.root,
                               reject_on_malformed=False)

    def test_put_archive_layout(self):
        d = os.path.join(self.root, 'classes')
        os.makedirs(os.path.join(d, 'pkg'))
        with open(os.path.join(d, 'pkg', 'RobotPlayer.class'), 'wb') as fh:
            fh.write(b'\xca\xfe')
        spec = {'bucket': SECURE, 'name': 'episode/bc23/submission/9/binary.zip'}
        saturn.put_archive(spec, d, public=False)
        z = zipfile.ZipFile(io.BytesIO(storage.read_bytes(SECURE, spec['name'])))
        self.assertEqual(z.namelist(), ['pkg/RobotPlayer.class'])
        self.assertEqual(storage.load_meta(SECURE, spec['name'])['acl'], 'projectPrivate')


def have_engine():
    jh = os.environ.get('JAVA_HOME') or os.path.expanduser('~/jdk/jdk8u504-b01')
    return os.path.exists(os.path.join(jh, 'bin', 'javac')) and \
        os.path.exists(os.path.join(REPO, 'engine', 'battlecode23-3.0.15.jar'))


@unittest.skipUnless(have_engine(), 'no JDK 8 or engine jar')
class Compile(unittest.TestCase):
    """The compile recipe with the real javac and Verifier (no game)."""

    @classmethod
    def setUpClass(cls):
        cls.env = saturn.EngineEnv()

    def compile(self, sub_id, files, package='examplefuncsplayer'):
        storage.write_bytes(SECURE, f'episode/bc23/submission/{sub_id}/source.zip', zip_bytes(files))
        rep = FakeReporter()
        ack = saturn.Task(compile_payload(sub_id, package), rep).run(
            saturn.Runners(os.path.join(TMP, f'work-{sub_id}'), self.env).compile)
        return ack, rep.reports[-1]

    def example(self):
        src = os.path.join(REPO, 'src', 'examplefuncsplayer')
        return {f'examplefuncsplayer/{f}': read(os.path.join(src, f))
                for f in os.listdir(src) if f.endswith('.java')}

    def test_success(self):
        ack, rep = self.compile(101, self.example())
        self.assertTrue(ack)
        self.assertEqual((rep['accepted'], rep['invocation']['status']), (True, 'OK!'), rep['invocation']['logs'])
        z = zipfile.ZipFile(io.BytesIO(storage.read_bytes(SECURE, 'episode/bc23/submission/101/binary.zip')))
        self.assertIn('examplefuncsplayer/RobotPlayer.class', z.namelist())
        self.assertIn('>>> Starting step 4/6: Build source code', rep['invocation']['logs'])

    def test_compile_error_is_rejected(self):
        files = self.example()
        files['examplefuncsplayer/RobotPlayer.java'] += '\nthis does not compile'
        ack, rep = self.compile(102, files)
        self.assertTrue(ack)
        self.assertEqual((rep['accepted'], rep['invocation']['status']), (False, 'OK!'))
        self.assertFalse(storage.exists(SECURE, 'episode/bc23/submission/102/binary.zip'))

    def test_verifier_rejects_wrong_package_and_empty_package(self):
        ack, rep = self.compile(103, self.example(), package='otherpackage')
        self.assertEqual((ack, rep['accepted']), (True, False))
        ack, rep = self.compile(104, self.example(), package='')
        self.assertEqual((ack, rep['accepted']), (True, False))
        self.assertIn('Package name must not be empty.', rep['invocation']['logs'])

    def test_forbidden_api_is_rejected(self):
        files = {'evil/RobotPlayer.java': 'package evil;\nimport battlecode.common.*;\npublic class RobotPlayer {\n'
                 '  public static void run(RobotController rc) throws GameActionException {\n'
                 '    try { new java.io.FileInputStream("/etc/passwd"); } catch (Exception e) {}\n  }\n}\n'}
        ack, rep = self.compile(105, files, package='evil')
        self.assertEqual((ack, rep['accepted']), (True, False), rep['invocation']['logs'])


class FakeEngine:
    """A stand-in `java` for the execute recipe: writes the replay and prints saturn-readable winner lines."""

    def __init__(self, root, winners='AB', exit_code=0):
        self.java = os.path.join(root, 'fake-java')
        with open(self.java, 'w') as fh:
            fh.write('#!/bin/sh\nfor a in "$@"; do case "$a" in -Dbc.server.save-file=*) '
                     'printf "\\037\\213replay" > "${a#-Dbc.server.save-file=}";; esac; done\n'
                     'echo "[server] -------------------- Match Starting --------------------"\n')
            for i, w in enumerate(winners):
                fh.write(f'echo "[server]               team ({w}) wins (round {100 + i})"\n')
            fh.write(f'exit {exit_code}\n')
        os.chmod(self.java, 0o755)
        self.cp, self.jar, self.sha256 = 'cp', 'battlecode23-3.0.15.jar', '0' * 64


class Execute(unittest.TestCase):
    def payload(self, mid, maps, alternate=True):
        sub = lambda i: {'source': {'bucket': SECURE, 'name': f'episode/bc23/submission/{i}/source.zip'},  # noqa: E731
                         'binary': {'bucket': SECURE, 'name': f'episode/bc23/submission/{i}/binary.zip'},
                         'team-name': f'team {i}', 'package': 'examplefuncsplayer'}
        return {'episode': {'name': 'bc23', 'language': 'java8', 'scaffold': ''},
                'metadata': {'report-url': f'https://galaxy.x/api/compete/bc23/match/{mid}/report/',
                             'task-type': 'execute'},
                'details': {'maps': maps, 'replay': {'bucket': SECURE, 'name': f'episode/bc23/replays/{mid}.bc23'},
                            'alternate-order': alternate, 'a': sub(201), 'b': sub(202)}}

    def setUp(self):
        for i in (201, 202):
            storage.write_bytes(SECURE, f'episode/bc23/submission/{i}/binary.zip',
                                zip_bytes({'examplefuncsplayer/RobotPlayer.class': b'\xca\xfe'}))

    def run_match(self, mid, maps, winners, exit_code=0):
        root = tempfile.mkdtemp(dir=TMP)
        env = saturn.EngineEnv(FakeEngine(root, winners, exit_code))
        rep = FakeReporter()
        ack = saturn.Task(self.payload(mid, maps), rep).run(saturn.Runners(os.path.join(root, 'w'), env, 10).execute)
        return ack, rep.reports[-1]

    def test_scores_and_replay(self):
        ack, rep = self.run_match(301, ['MapA', 'MapB', 'MapC'], 'ABA')
        self.assertTrue(ack)
        self.assertEqual((rep['scores'], rep['invocation']['status']), ([2, 1], 'OK!'))
        self.assertTrue(storage.read_bytes(SECURE, 'episode/bc23/replays/301.bc23').startswith(b'\x1f\x8b'))
        self.assertEqual(storage.load_meta(SECURE, 'episode/bc23/replays/301.bc23')['acl'], 'publicRead')
        logs = rep['invocation']['logs']
        self.assertIn('-Dbc.server.websocket=false', logs)
        self.assertIn('-Dbc.server.alternate-order=true', logs)
        self.assertIn('-Dbc.game.maps=MapA,MapB,MapC', logs)
        self.assertIn('-Dbc.game.team-a=team 201', logs)

    def test_engine_failure_and_unreadable_output_are_retried(self):
        ack, rep = self.run_match(302, ['MapA'], 'A', exit_code=1)
        self.assertEqual((ack, rep['invocation']['status'], 'scores' in rep), (False, 'TRY', False))
        ack, rep = self.run_match(303, ['MapA', 'MapB'], 'A')         # one winner line for two maps
        self.assertEqual((ack, rep['invocation']['status']), (False, 'TRY'))

    def test_bad_maps_refused(self):
        with self.assertRaises(ValueError):
            saturn.Runners(TMP, None).execute(saturn.Task(self.payload(304, ['../x']), FakeReporter()))


# ------------------------------------------------------------------------------------------------------------- relay
class FakeSiarnaq:
    def __init__(self, status=204):
        self.status, self.calls = status, []

    def __call__(self, method, path, body=b'', headers=None):
        self.calls.append((method, path, body, dict(headers or {})))
        if isinstance(self.status, Exception):
            raise self.status
        return self.status, b'{}'


class Relay(unittest.TestCase):
    def test_report_forwarding(self):
        fake = FakeSiarnaq(409)
        code, ans = relay.relay_report({'url': 'https://galaxy.old-host.sslip.io/api/compete/bc23/match/12/report/',
                                        'task_type': 'execute',
                                        'payload': {'scores': [1, 2], 'invocation': {'status': 'OK!'}}}, send=fake)
        self.assertEqual((code, ans['status']), (200, 409))
        method, path, body, headers = fake.calls[0]
        self.assertEqual((method, path), ('POST', '/api/compete/bc23/match/12/report/'))
        self.assertEqual(headers['User-Agent'], 'Galaxy-Saturn')
        claims = tokens.verify(headers['Authorization'].split()[1], audience='siarnaq')
        self.assertEqual(claims['email'], config.SATURN_EXECUTE_EMAIL)
        self.assertEqual(json.loads(body), {'scores': [1, 2], 'invocation': {'status': 'OK!'}})

    def test_report_validation(self):
        fake = FakeSiarnaq()
        good = {'task_type': 'compile', 'payload': {'invocation': {}}}
        for url, kind in (('https://g/api/compete/bc23/match/1/report/', 'compile'),            # wrong kind
                          ('https://g/api/compete/bc23/submission/1/report/?x=1', 'compile'),   # query
                          ('https://g/api/compete/bc23/submission/1/../../user/u/report/', 'compile'),
                          ('https://g/api/compete/bc23/submission/1/', 'compile'),
                          ('https://g/admin/', 'compile'), ('file:///etc/passwd', 'compile'),
                          ('https://g/api/compete/bc23/submission/1/report/', 'deploy')):
            code, _ = relay.relay_report(dict(good, url=url, task_type=kind), send=fake)
            self.assertEqual(code, 400, url)
        self.assertEqual(relay.relay_report(dict(good, url='https://g/api/compete/bc23/submission/1/report/',
                                                 payload={}), send=fake)[0], 400)
        self.assertEqual(fake.calls, [])
        code, ans = relay.relay_report(dict(good, url='https://g/api/compete/bc23/submission/1/report/'),
                                       send=FakeSiarnaq(ConnectionRefusedError('down')))
        self.assertEqual(code, 502)

    def test_unix_socket_end_to_end(self):
        fake = FakeSiarnaq(204)
        orig = relay.siarnaq_request
        relay.siarnaq_request = fake
        relay_report_defaults = relay.relay_report.__defaults__
        relay.relay_report.__defaults__ = (fake,)
        server = relay.UnixServer(config.relay_socket(), relay.ReportHandler)
        th = threading.Thread(target=server.serve_forever, daemon=True)
        th.start()
        try:
            self.assertEqual(os.stat(config.relay_socket()).st_mode & 0o777, 0o600)
            task = saturn.Task(compile_payload(5), saturn.RelayReporter())
            task.status, task.details = saturn.COMPLETED, {'accepted': True}
            task.reporter.report(task)
            self.assertEqual(fake.calls[-1][1], '/api/compete/bc23/submission/5/report/')
            self.assertEqual(json.loads(fake.calls[-1][2])['invocation']['status'], 'OK!')
            fake.status = 409
            task2 = saturn.Task(compile_payload(5), saturn.RelayReporter())
            with self.assertRaises(saturn.TaskFinished):
                task2.reporter.report(task2)
            self.assertEqual(task2.status, saturn.ABORTED)
        finally:
            server.shutdown()
            server.server_close()
            relay.siarnaq_request = orig
            relay.relay_report.__defaults__ = relay_report_defaults

    def test_cloud_tasks_dispatch_and_retry(self):
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(config.PROJECT, config.LOCATION, 'test-queue')
        client.create_task(request=dict(parent=parent, task=tasks_v2.Task(http_request=tasks_v2.HttpRequest(
            url='https://galaxy.x/api/compete/bc23/match/9/rating_update/',
            oidc_token=tasks_v2.OidcToken(service_account_email=config.SERVICE_EMAIL)))))
        fake = FakeSiarnaq(500)
        disp = relay.TaskDispatcher(threading.Event(), send=fake)
        self.assertTrue(disp.process_one('test-queue'))
        q = spool.task_queue('test-queue')
        self.assertEqual(q.counts()['delayed'], 1)
        method, path, body, headers = fake.calls[0]
        self.assertEqual((method, path, headers['User-Agent']), ('POST', '/api/compete/bc23/match/9/rating_update/',
                                                                 'Google-Cloud-Tasks'))
        self.assertEqual(headers['X-CloudTasks-QueueName'], 'test-queue')
        self.assertEqual(tokens.verify(headers['Authorization'][7:])['email'], config.SERVICE_EMAIL)
        q.promote_due(now_ns=time.time_ns() + 10**10)
        fake.status = 204
        self.assertTrue(disp.process_one('test-queue'))
        self.assertEqual(q.counts(), {'ready': 0, 'leased': 0, 'delayed': 0, 'dead': 0})
        self.assertEqual(fake.calls[1][3]['X-CloudTasks-TaskRetryCount'], '1')
        self.assertEqual(relay.task_backoff(1), 0.1)
        self.assertEqual(relay.task_backoff(100), 3600.0)

    def test_task_outside_api_is_buried_without_a_call(self):
        q = spool.task_queue('test-queue2').ensure()
        q.put({'http_request': {'url': 'https://galaxy.x/admin/', 'http_method': 'POST'}})
        fake = FakeSiarnaq()
        relay.TaskDispatcher(threading.Event(), send=fake).process_one('test-queue2')
        self.assertEqual((fake.calls, q.counts()['dead']), ([], 1))

    def test_scheduler_fires_once_per_matching_minute(self):
        parent = f'projects/{config.PROJECT}/locations/{config.LOCATION}'
        scheduler.CloudSchedulerClient().create_job(request=dict(parent=parent, job=scheduler.Job(
            name=f'{parent}/jobs/replica-autoscrim-test', schedule='0 */4 * * *', time_zone='UTC',
            http_target=scheduler.HttpTarget(uri='https://galaxy.x/api/episode/e/bc23/autoscrim/',
                                             body=b'{"best_of": 3}', headers={'Content-Type': 'application/json'},
                                             oidc_token=scheduler.OidcToken(service_account_email=config.SERVICE_EMAIL)))))
        fake = FakeSiarnaq()
        at = datetime.datetime(2026, 10, 8, 4, 0, 10, tzinfo=datetime.timezone.utc)
        self.assertEqual(relay.fire_jobs(now=at, only='replica-autoscrim-test', send=fake), [('replica-autoscrim-test', 204)])
        self.assertEqual(relay.fire_jobs(now=at, only='replica-autoscrim-test', send=fake), [])     # same minute
        self.assertEqual(relay.fire_jobs(now=at + datetime.timedelta(minutes=1), only='replica-autoscrim-test',
                                         send=fake), [])
        method, path, body, headers = fake.calls[0]
        self.assertEqual((path, body, headers['User-Agent']), ('/api/episode/e/bc23/autoscrim/', b'{"best_of": 3}',
                                                               'Google-Cloud-Scheduler'))
        self.assertEqual(tokens.verify(headers['Authorization'][7:])['email'], config.SERVICE_EMAIL)


# ------------------------------------------------------------------------------------------------ deploy renderers
SETUP = os.path.join(GALAXY, 'deploy', 'galaxy-setup.sh')
VM_SETUP = os.path.join(REPO, 'tools', 'replica', 'deploy', 'vm-setup.sh')
HASH = '$2a$14$' + 'abcdefghijklmnopqrstuu' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ01234'


def sh(*args, env=None):
    return subprocess.run(['bash', *args], capture_output=True, text=True, env=dict(os.environ, **(env or {})))


class Deploy(unittest.TestCase):
    def test_bash_syntax(self):
        for f in (SETUP, os.path.join(GALAXY, 'deploy', 'deploy.sh'), os.path.join(GALAXY, 'deploy', 'config.sh')):
            self.assertEqual(sh('-n', f).returncode, 0, f)

    def test_site(self):
        r = sh(SETUP, 'print-site', '136-86-167-127.sslip.io', HASH)
        self.assertEqual(r.returncode, 0, r.stderr)
        c = r.stdout
        self.assertIn('galaxy.136-86-167-127.sslip.io {', c)
        self.assertIn(f'owner {HASH}', c)
        self.assertIn("connect-src 'self'", c)
        self.assertIn('Referrer-Policy same-origin', c)
        self.assertIn('not path /api/token/* /api/user/password_reset/*', c)
        self.assertRegex(c, r'header_regexp Authorization \^Bearer')
        self.assertIn('reverse_proxy 127.0.0.1:8024', c)
        self.assertIn('header_up -Authorization', c)
        self.assertIn('hide .tmp-*', c)
        self.assertIn('try_files {path} /index.html', c)
        self.assertIn('copy_response 403', c)          # no 401 to a Basic-authenticated request (browser cache)
        self.assertIn('header -WWW-Authenticate', c)
        # without basic_auth: the bearer branch (siarnaq only) and the static web app manifest, nothing else
        bearer = c[c.index('handle @bearer_api {'):c.index('\thandle /manifest.json {')]
        self.assertNotIn('file_server', bearer)
        manifest = c[c.index('\thandle /manifest.json {'):c.index('\thandle {')]
        self.assertNotIn('reverse_proxy', manifest)
        self.assertEqual(c.count('basic_auth'), 1)
        for bad in ('1.2.3.4.sslip.io; evil', 'UPPER.sslip.io', ''):
            self.assertNotEqual(sh(SETUP, 'print-site', bad, HASH).returncode, 0, bad)
        self.assertNotEqual(sh(SETUP, 'print-site', '1-2-3-4.sslip.io', 'nohash').returncode, 0)

    def test_caddyfile_with_and_without_galaxy(self):
        plain = sh(VM_SETUP, 'print-caddyfile', '136-86-167-127.sslip.io', HASH)
        both = sh(VM_SETUP, 'print-caddyfile', '136-86-167-127.sslip.io', HASH, '1', env={'GALAXY_SETUP': SETUP})
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertEqual(both.returncode, 0, both.stderr)
        self.assertNotIn('galaxy.', plain.stdout)
        self.assertTrue(both.stdout.startswith(plain.stdout))
        self.assertIn('galaxy.136-86-167-127.sslip.io {', both.stdout)

    def test_units(self):
        r = sh(SETUP, 'print-units')
        self.assertEqual(r.returncode, 0, r.stderr)
        units = dict(re.findall(r'^### (\S+)\n(.*?)(?=^### |\Z)', r.stdout, re.S | re.M))
        self.assertEqual(set(units), {'bc23-galaxy-web.service', 'bc23-galaxy-relay.service', 'bc23-galaxy-saturn.service',
                                      'bc23-galaxy-scheduler.service', 'bc23-galaxy-scheduler.timer'})
        for name, text in units.items():
            if name.endswith('.service'):
                for line in ('User=bcreplica', 'Slice=bc23-replica.slice', 'Requires=bc23-replica-egress.service',
                             'ProtectSystem=strict', 'NoNewPrivileges=yes', 'UMask=0027'):
                    self.assertIn(line, text, f'{name}: {line}')
                self.assertIn('/run/systemd/resolve', text)
        self.assertIn('--bind 127.0.0.1:8024', units['bc23-galaxy-web.service'])
        self.assertIn('PrivateNetwork=yes', units['bc23-galaxy-saturn.service'])
        self.assertIn('/home/bcreplica/galaxy/secrets', units['bc23-galaxy-saturn.service'])
        for name in ('bc23-galaxy-web.service', 'bc23-galaxy-relay.service'):
            self.assertNotIn('PrivateNetwork', units[name])
            self.assertIn('nft list table inet bc23_replica_egress', units[name])
        self.assertIn('OnCalendar=*-*-* *:*:00', units['bc23-galaxy-scheduler.timer'])

    def test_env_and_cli(self):
        env = sh(SETUP, 'print-env').stdout
        pp = re.search(r'^PYTHONPATH=(.*)$', env, re.M).group(1).split(':')
        self.assertTrue(pp[0].endswith('/tools/galaxy/standins'), pp)
        self.assertIn('DJANGO_CONFIGURATION=Replica', env)
        self.assertNotRegex(env, r'(?i)secret|password')
        cli = sh(SETUP, 'print-cli').stdout
        self.assertIn('nft list table inet', cli)
        self.assertIn('sudo -u "$RUN_AS" env -i', cli)

    def test_egress_port_and_requirements(self):
        out = subprocess.run(['bash', '-c', 'source "$1"; echo "$REPLICA_LO_PORTS"', '_',
                              os.path.join(REPO, 'tools', 'replica', 'deploy', 'config.sh')],
                             capture_output=True, text=True).stdout.split()
        self.assertIn('8024', out)
        reqs = read(os.path.join(GALAXY, 'requirements.txt'))
        pins = re.findall(r'^([A-Za-z0-9_.-]+)==(\S+) \\\n    --hash=sha256:([0-9a-f]{64})', reqs, re.M)
        self.assertGreater(len(pins), 30)
        self.assertEqual(len(pins), len(re.findall(r'^[A-Za-z]', reqs, re.M)))
        self.assertFalse([n for n, _, _ in pins if n.lower().startswith('google')])


class ViewerPage(unittest.TestCase):
    def test_page_and_replay_pattern(self):
        import viewer_page
        self.assertIn('src="out/app.js"', viewer_page.PAGE)
        self.assertIn('src="galaxy-viewer.js"', viewer_page.PAGE)
        self.assertEqual(viewer_page.PAGE.count('<script'), 2)       # no inline script: CSP script-src 'self'
        pat = re.compile(viewer_page.REPLAY_PATH_RE.replace('\\/', '/'))
        ok = '/storage/bc23-replica-secure/episode/bc23/replays/7d21a717-d249-4601-999c-be794d725fde.bc23'
        self.assertTrue(pat.match(ok))
        for bad in ('https://evil.example/x.bc23', '//evil.example' + ok, ok + '?x', ok.replace('secure', 'public'),
                    '/storage/bc23-replica-secure/episode/bc23/submission/1/source.zip'):
            self.assertFalse(pat.match(bad), bad)


if __name__ == '__main__':
    unittest.main(verbosity=1)
