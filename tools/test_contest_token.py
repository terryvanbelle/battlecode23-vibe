#!/usr/bin/env python3
"""Atomic token-cache regressions; synthetic tokens only, no credentials or HTTP."""
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import threading
import unittest
from unittest import mock


class ContestTokenTest(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('contest_token_test', Path(__file__).with_name('contest.py'))
        self.client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.client)
        self.tmp = tempfile.TemporaryDirectory(prefix='bc23-token-test-')
        self.addCleanup(self.tmp.cleanup)
        self.client.CACHE = os.path.join(self.tmp.name, 'cache')

    def test_overlapping_writers_publish_complete_private_tokens(self):
        barrier = threading.Barrier(2)
        replace = os.replace
        published, errors = [], []
        tokens = [{'access': 'synthetic-a', 'refresh': 'a' * 4096},
                  {'access': 'synthetic-b', 'refresh': 'b' * 8192}]

        def coordinated_replace(src, dst):
            # Both writers have finished their temporary files before either renames.
            barrier.wait(timeout=5)
            with open(src) as fh:
                published.append(json.load(fh))
            replace(src, dst)

        def save(tok):
            try:
                self.client._save_token(tok)
            except BaseException as error:
                errors.append(error)

        with mock.patch.object(self.client.os, 'replace', side_effect=coordinated_replace):
            writers = [threading.Thread(target=save, args=(tok,)) for tok in tokens]
            for writer in writers:
                writer.start()
            for writer in writers:
                writer.join(10)
                self.assertFalse(writer.is_alive(), 'token writer hung')
        self.assertEqual(errors, [])
        self.assertCountEqual(published, tokens)
        path = Path(self.client.CACHE) / 'token.json'
        self.assertIn(json.loads(path.read_text()), tokens)
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
        self.assertEqual(list(path.parent.iterdir()), [path])

    def test_failed_write_keeps_previous_token_and_cleans_temporary_file(self):
        original = {'access': 'synthetic-original', 'refresh': 'synthetic-refresh'}
        self.client._save_token(original)
        path = Path(self.client.CACHE) / 'token.json'
        before = path.read_bytes()
        with mock.patch.object(self.client.json, 'dump', side_effect=OSError('synthetic disk failure')):
            with self.assertRaisesRegex(OSError, 'disk failure'):
                self.client._save_token({'access': 'synthetic-new'})
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(list(path.parent.iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
