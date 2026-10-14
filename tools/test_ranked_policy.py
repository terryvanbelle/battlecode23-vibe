#!/usr/bin/env python3
"""Ranked/trial concurrency regressions, with a mocked replica and the real state lock; no games or HTTP calls."""
import contextlib
import fcntl
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import threading
import types
import unittest
from unittest import mock


class LoopStopped(BaseException):
    """Stop the ranked loop at its first sleep without its network-error handler swallowing the stop."""


class LockOutput(io.StringIO):
    def __init__(self, waiting):
        super().__init__()
        self.waiting = waiting

    def write(self, text):
        if 'waiting for the ladder-state lock' in text:
            self.waiting.set()
        return super().write(text)


class RankedPolicyConcurrencyTest(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('ranked_policy_test', Path(__file__).with_name('ladder_policy.py'))
        self.p = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.p)
        tmp = tempfile.TemporaryDirectory(prefix='bc23-ranked-test-')
        self.addCleanup(tmp.cleanup)
        self.p.STATE = os.path.join(tmp.name, 'state.json')
        self.p.LOCK = os.path.join(tmp.name, 'state.lock')
        self.p.save_state({'validated': {'submission': 24, 'package': 'inc'}, 'trial': None, 'history': []})
        self.active = 24
        self.requested = []
        self.errors = []
        self.p.bot_hash = lambda package: 'a' * 12
        self.p.next_autoscrim = lambda now: None
        real = self.p.contest

        def wait_submission(sid):
            self.active = sid                    # accepted compile activates the candidate, as on the replica
            return {'status': 'OK!', 'accepted': True}

        def request(*args):
            self.requested.append(self.active)  # match creation fixes the active submission
            return {'id': 50}

        self.client = types.SimpleNamespace(
            ApiError=real.ApiError, pick_upward=real.pick_upward,
            me=lambda: {'id': 1, 'name': 'us'},
            matches=lambda *args, **kw: [],
            pages=lambda *args, **kw: [{'id': self.active, 'package': 'inc', 'accepted': True}],
            rankings=lambda: [{'id': 1, 'name': 'us', 'rating': 700, 'active': True, 'status': 'R'},
                              {'id': 2, 'name': 'opponent', 'rating': 800, 'active': True, 'status': 'R'}],
            request=request, set_auto_accept=lambda **kw: None,
            submit=lambda *args: {'id': 30}, wait_submission=wait_submission,
            block=lambda *args, **kw: os.path.join(tmp.name, 'panel'))
        self.p.contest = self.client
        self.p.bt_probs = lambda package: None   # no BT model: the loop falls back to the closest teams above us
        self.sleep_patch = mock.patch.object(self.p.time, 'sleep', side_effect=LoopStopped)
        self.sleep_patch.start()
        self.addCleanup(self.sleep_patch.stop)

    def start(self, fn):
        def run():
            try:
                fn()
            except LoopStopped:
                pass
            except BaseException as error:
                self.errors.append(error)
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def finish(self, *threads):
        for thread in threads:
            thread.join(5)
            self.assertFalse(thread.is_alive(), 'policy command did not finish')
        self.assertEqual(self.errors, [])

    def trial(self):
        self.p.cmd_trial_start('cand', 'panel.txt', 'race-test', False, skip_screen='mocked concurrency test')

    def test_trial_cannot_activate_between_ranked_check_and_post(self):
        checked, allow_post, waiting = threading.Event(), threading.Event(), threading.Event()
        rankings = self.client.rankings

        def pause_after_check():
            checked.set()
            if not allow_post.wait(15):
                raise RuntimeError('ranked test did not release opponent selection')
            return rankings()

        self.client.rankings = pause_after_check
        out = LockOutput(waiting)
        with contextlib.redirect_stdout(out):
            ranked = self.start(self.p.cmd_ranked)
            trial = None
            try:
                self.assertTrue(checked.wait(5), 'ranked eligibility was not checked')
                trial = self.start(self.trial)
                # This comes from flock's real blocking path, rather than relying on a scheduling delay.
                self.assertTrue(waiting.wait(5), 'trial did not wait for the ranked request lock')
                self.assertEqual(self.active, 24)
                self.assertIsNone(self.p.load_state()['trial'])
            finally:
                allow_post.set()
                self.finish(*([ranked, trial] if trial else [ranked]))
        self.assertEqual(self.requested, [24])
        self.assertEqual(self.active, 30)
        self.assertEqual(self.p.load_state()['trial']['submission'], 30)

    def test_ranked_rechecks_after_waiting_for_trial_compile(self):
        compiling, allow_compile, waiting = threading.Event(), threading.Event(), threading.Event()
        wait_submission = self.client.wait_submission

        def pause_compile(sid):
            compiling.set()
            if not allow_compile.wait(15):
                raise RuntimeError('ranked test did not release candidate compile')
            return wait_submission(sid)

        self.client.wait_submission = pause_compile
        out = LockOutput(waiting)
        with contextlib.redirect_stdout(out):
            trial = self.start(self.trial)
            ranked = None
            try:
                self.assertTrue(compiling.wait(5), 'candidate did not reach compile wait')
                ranked = self.start(self.p.cmd_ranked)
                self.assertTrue(waiting.wait(5), 'ranked loop did not wait for the trial lock')
            finally:
                allow_compile.set()
                self.finish(*([trial, ranked] if ranked else [trial]))
        self.assertEqual(self.requested, [])
        self.assertIn('paused: trial in progress', out.getvalue())

    def assert_lock_free(self):
        fd = os.open(self.p.LOCK, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(fd)

    def test_request_failures_release_lock_before_backoff_or_poll(self):
        for error, expected_sleep in ((self.client.ApiError(429, 'hourly limit'), 600),
                                      (self.client.ApiError(409, 'three active matches'), 60),
                                      (self.client.ApiError(500, 'replica failure'), 60),
                                      (RuntimeError('network hiccup'), 60)):
            with self.subTest(error=str(error)):
                self.client.request = mock.Mock(side_effect=error)
                sleeps = []

                def stop(seconds):
                    self.assert_lock_free()
                    sleeps.append(seconds)
                    raise LoopStopped()

                with mock.patch.object(self.p.time, 'sleep', side_effect=stop), contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(LoopStopped):
                        self.p.cmd_ranked()
                self.client.request.assert_called_once_with(2, True, [], '?')
                self.assertEqual(sleeps, [expected_sleep])


if __name__ == '__main__':
    unittest.main()
