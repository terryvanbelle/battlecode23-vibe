#!/usr/bin/env python3
"""Unit tests for the galaxy replica's operator tools (offline pieces only: no network, no games):
tools/galaxy/client.py (site guard, URL scope, multipart), field.py (names, blind packaging, compile-log filter,
opponent choice, queue count, accounts file), results.py (replay rows, paging, idempotent append) and snapshot.py
(records, markdown, chart). Run: python3 test/galaxy/test_field_tools.py (tools/unit-tests.sh runs it)."""
import csv
import io
import json
import os
import random
import shutil
import stat
import sys
import tempfile
import unittest
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GALAXY = os.path.join(REPO, 'tools', 'galaxy')
sys.path.insert(0, GALAXY)
import client  # noqa: E402
import field  # noqa: E402
import results  # noqa: E402
import snapshot  # noqa: E402


def touch(path, text='class X {}\n'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        fh.write(text)


class ClientTest(unittest.TestCase):
    def test_refuses_official_and_plain_http(self):
        official = 'battlecode' + '.org'
        for site in (f'https://play.{official}', f'https://api.{official}', f'https://{official}',
                     'http://galaxy.example.invalid'):
            with self.assertRaises(SystemExit, msg=site):
                client.Client(site=site, gate='Basic x')

    def test_path_scope(self):
        c = client.Client(site='https://galaxy.1-2-3-4.sslip.io', gate='Basic x')
        self.assertEqual(c.path_of('/api/x/?page=2'), '/api/x/?page=2')
        self.assertEqual(c.path_of('https://galaxy.1-2-3-4.sslip.io/api/x/?page=2'), '/api/x/?page=2')
        for bad in ('https://elsewhere.invalid/api/', 'http://galaxy.1-2-3-4.sslip.io/api/',
                    'https://galaxy.1-2-3-4.sslip.io:8443/api/', 'https://api.' + 'battlecode' + '.org/api/'):
            with self.assertRaises(SystemExit, msg=bad):
                c.path_of(bad)

    def test_multipart_and_error_code(self):
        body, ct = client.multipart({'package': 'p'}, {'source_code': ('s.zip', b'PK', 'application/zip')})
        b = ct.split('boundary=')[1]
        self.assertIn(b'name="package"\r\n\r\np\r\n', body)
        self.assertTrue(body.endswith(f'--{b}--\r\n'.encode()))
        e = client.ApiError(429, json.dumps({'detail': 'x', 'code': 'scrimmages_rate_limited'}))
        self.assertEqual(e.code_name(), 'scrimmages_rate_limited')
        self.assertEqual(client.ApiError(500, '<html>').code_name(), '')


class FieldNamesTest(unittest.TestCase):
    def test_team_and_user_names(self):
        self.assertEqual(field.team_name('CyrilSharma.finalBot'), 'CyrilSharma.finalBot')
        self.assertEqual(field.team_name('team-remember-to-hydrate.sprint_1'), 'remember-to-hydrate.sprint_1')
        self.assertEqual(len(field.team_name('x' * 40)), 32)
        self.assertEqual(field.user_name('a b/c.d'), 'a_b_c.d')

    def test_mapping_file_covers_the_field(self):
        rows = field.read_mapping()
        entrants = field.read_field()
        self.assertEqual(sorted(r['entrant'] for r in rows), sorted(entrants))
        teams = [r['team'] for r in rows]
        self.assertEqual(len(set(teams)), len(teams))
        for r in rows:
            self.assertLessEqual(len(r['team']), 32, r)
            self.assertRegex(r['team'], r'^[ -~]+$')
            self.assertIn(r['mode'], ('package', 'root'), r)
            self.assertEqual(field.entrant_of(r['team'], rows), r['entrant'])


class PackagingTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_named_dir_and_zip_modes(self):
        repo = os.path.join(self.d, 'owner_repo')
        touch(os.path.join(repo, 'src', 'bot', 'RobotPlayer.java'))
        touch(os.path.join(repo, 'src', 'bot', 'util', 'Nav.java'))
        touch(os.path.join(repo, 'src', 'bot', 'README.md'))
        touch(os.path.join(repo, 'src', 'helper', 'Lib.java'))
        touch(os.path.join(repo, 'test', 'bot', 'RobotPlayer.java'))         # tests never count
        touch(os.path.join(repo, 'src', 'bot', 'BotTest.java'))
        pdir = field.find_package_dir(repo, 'bot')
        self.assertEqual(pdir, os.path.join(repo, 'src', 'bot'))
        names = [arc for _, arc in field.zip_entries(pdir, 'bot', 'package', repo)]
        self.assertEqual(sorted(names), ['bot/RobotPlayer.java', 'bot/util/Nav.java'])
        names = [arc for _, arc in field.zip_entries(pdir, 'bot', 'root', repo)]
        self.assertEqual(sorted(names), ['bot/RobotPlayer.java', 'bot/util/Nav.java', 'helper/Lib.java'])
        z = zipfile.ZipFile(io.BytesIO(field.build_zip(field.zip_entries(pdir, 'bot', 'package', repo))))
        self.assertEqual(sorted(z.namelist()), ['bot/RobotPlayer.java', 'bot/util/Nav.java'])

    def test_package_at_repo_root(self):
        repo = os.path.join(self.d, 'flat')
        touch(os.path.join(repo, 'RobotPlayer.java'))
        touch(os.path.join(repo, 'Other.java'))
        touch(os.path.join(repo, 'docs', 'Gen.java'))
        pdir = field.find_package_dir(repo, 'realbot')
        self.assertEqual(pdir, repo)
        names = sorted(arc for _, arc in field.zip_entries(pdir, 'realbot', 'root', repo))
        self.assertEqual(names, ['realbot/Other.java', 'realbot/RobotPlayer.java'])

    def test_ambiguous(self):
        repo = os.path.join(self.d, 'twice')
        touch(os.path.join(repo, 'src', 'bot', 'RobotPlayer.java'))
        touch(os.path.join(repo, 'old', 'bot', 'RobotPlayer.java'))
        self.assertEqual(field.find_package_dir(repo, 'bot'), os.path.join(repo, 'src', 'bot'))
        touch(os.path.join(repo, 'src2', 'src', 'bot', 'RobotPlayer.java'))
        with self.assertRaises(LookupError):
            field.find_package_dir(repo, 'bot')
        with self.assertRaises(LookupError):
            field.find_package_dir(repo, 'none')

    def test_safe_log_tail_drops_source_excerpts(self):
        logs = ('>>> Starting step 4/6: Build source code\nRunning command: bash -c ...\n'
                '/w/src/bot/RobotPlayer.java:12: error: cannot find symbol\n'
                '        int secret = helperCall(rc);\n'
                '                     ^\n'
                '  symbol:   method helperCall(RobotController)\n'
                '1 error\n>>> Finished step 4/6: Build source code\n')
        tail = field.safe_log_tail(logs)
        self.assertIn('/w/src/bot/RobotPlayer.java:12: error: cannot find symbol', tail)
        self.assertIn('1 error', tail)
        self.assertFalse(any('secret' in l or l.strip() == '^' for l in tail))


class ActivityTest(unittest.TestCase):
    def ladder(self):
        rows = [(1, 'a', 300.0), (2, 'b', 250.0), (3, 'c', 240.0), (4, 'd', 240.0), (5, 'e', 100.0), (6, 'f', 50.0)]
        out = [{'rank': i + 1, 'id': tid, 'name': n, 'rating': r, 'status': 'R', 'has_active_submission': True}
               for i, (tid, n, r) in enumerate(rows)]
        out[0]['has_active_submission'] = False
        return out

    def test_pick_only_at_or_above(self):
        lad = self.ladder()
        rnd = random.Random(1)
        for _ in range(100):
            self.assertIn(field.pick_opponent(lad, 5, 2, rnd)['name'], {'c', 'd'})       # 240, 240: the two nearest
            self.assertIn(field.pick_opponent(lad, 3, 3, rnd)['name'], {'d', 'b'})       # equal rating is allowed
        self.assertIsNone(field.pick_opponent(lad, 2, 3, rnd))      # the top team's only superior has no submission
        self.assertIsNone(field.pick_opponent(lad, 99, 3, rnd))
        flat = [dict(t, rating=0.0, has_active_submission=True) for t in lad]
        seen = {field.pick_opponent(flat, 6, 2, rnd)['name'] for _ in range(200)}
        self.assertEqual(seen, {'a', 'b', 'c', 'd', 'e'})           # all tied at 0: any of them, not the lowest ids

    def test_hourly_cap_and_our_waiting(self):
        now = 10_000.0
        self.assertTrue(field.under_hourly_cap([], now, 4))
        self.assertTrue(field.under_hourly_cap([now - 4000] * 9 + [now - 10] * 3, now, 4))   # old ones expire
        self.assertFalse(field.under_hourly_cap([now - 10] * 4, now, 4))

        class Stub:
            def __init__(self, statuses): self.statuses = statuses
            def request(self, method, path):
                assert path.endswith('team_id=28'), path
                return {'results': [{'status': s} for s in self.statuses]}
        self.assertEqual(field.team_waiting(Stub(['OK!', 'QUE', 'RUN', 'CAN', 'TRY']), 'bc23', 28), 3)
        self.assertEqual(field.team_waiting(Stub(['OK!', 'ERR']), 'bc23', 28), 0)

    def test_queue_backlog_from_spool(self):
        d = tempfile.mkdtemp()
        try:
            for k, n in (('ready', 3), ('delayed', 1), ('leased', 5), ('dead', 2)):
                os.makedirs(os.path.join(d, k))
                for i in range(n):
                    touch(os.path.join(d, k, f'{i}.json'), '{}')
            touch(os.path.join(d, 'ready', '.tmp-x'), '{}')
            self.assertEqual(field.queue_backlog(d), 4)
        finally:
            shutil.rmtree(d)

    def test_accounts_file_is_private(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, 'sub', 'accounts.json')
            field.save_accounts({'u': {'password': 'x'}}, p)
            self.assertEqual(stat.S_IMODE(os.stat(p).st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(p)).st_mode), 0o700)
            self.assertEqual(field.load_accounts(p), {'u': {'password': 'x'}})
            os.chmod(p, 0o644)
            with self.assertRaises(SystemExit):
                field.load_accounts(p)
        finally:
            shutil.rmtree(d)


class ResultsTest(unittest.TestCase):
    def match(self, alt=True):
        return {'id': 41, 'status': 'OK!', 'alternate_order': alt, 'maps': ['Cee', 'Maze', 'Zig'],
                'participants': [
                    {'team': 9, 'teamname': 'remember-to-hydrate.sprint_1', 'player_index': 1, 'score': 1,
                     'submission': 5},
                    {'team': 28, 'teamname': 'vibe23', 'player_index': 0, 'score': 2, 'submission': 24}]}

    def test_rows(self):
        games = results.parse_games('0 Cee A 900\n1 Maze B 2000\n2 Zig A 431\nnoise\n')
        self.assertEqual(games, [(0, 'Cee', 'A', 900), (1, 'Maze', 'B', 2000), (2, 'Zig', 'A', 431)])
        names = {'remember-to-hydrate.sprint_1': 'team-remember-to-hydrate.sprint_1'}
        rows, probs = results.match_rows(self.match(), games, 'vibe23', {24: 'g_iter0'}, names)
        self.assertEqual(probs, [])
        self.assertEqual([(r['run'], r['seq'], r['teamA'], r['teamB'], r['map'], r['winner'], r['rounds'], r['seed'])
                          for r in rows],
                         [('galaxy-41', '1', 'us:g_iter0', 'team-remember-to-hydrate.sprint_1', 'Cee', 'A', '900', 'map'),
                          ('galaxy-41', '2', 'us:g_iter0', 'team-remember-to-hydrate.sprint_1', 'Maze', 'B', '2000',
                           'map-rev'),
                          ('galaxy-41', '3', 'us:g_iter0', 'team-remember-to-hydrate.sprint_1', 'Zig', 'A', '431', 'map')])
        self.assertTrue(all(r['reason'] == '' for r in rows))
        rows, _ = results.match_rows(self.match(alt=False), games, 'vibe23', {}, {})
        self.assertEqual([r['seed'] for r in rows], ['map'] * 3)
        self.assertEqual(rows[0]['teamA'], 'us:submission-24')
        self.assertEqual(rows[0]['teamB'], 'remember-to-hydrate.sprint_1')

    def test_problems_and_no_winner(self):
        rows, probs = results.match_rows(self.match(), [(0, 'Cee', 'A', 9), (1, 'Maze', '-', 9)], 'vibe23', {}, {})
        self.assertEqual(len(rows), 1)
        self.assertTrue(any('no winner' in p for p in probs))
        self.assertTrue(any('maps' in p for p in probs))

    def test_scan_low_water(self):
        ms = [{'id': i, 'status': 'OK!' if i not in (17, 19) else 'QUE'} for i in range(20, 0, -1)]
        pages = {n + 1: {'results': ms[n * 10:(n + 1) * 10], 'next': 'x' if n == 0 else None} for n in range(2)}
        reads = []

        def read(n):
            reads.append(n)
            return pages[n]
        got, low = results.scan(read, 0)
        self.assertEqual((len(got), low, reads), (20, 17, [1, 2]))
        reads.clear()
        got, low = results.scan(read, 17)
        self.assertEqual(([m['id'] for m in got][-1], low, reads), (17, 17, [1]))
        reads.clear()
        done = [{'id': i, 'status': 'OK!'} for i in range(20, 10, -1)]
        got, low = results.scan(lambda n: {'results': done, 'next': 'x'}, 15)
        self.assertEqual((len(got), low), (6, 21))

    def test_append_is_idempotent(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, 'games.csv')
            row = {'run': 'galaxy-1', 'seq': '1', 'teamA': 'a', 'teamB': 'b', 'map': 'm', 'winner': 'A',
                   'rounds': '5', 'reason': '', 'seed': 'map'}
            results.append_rows(p, [row])
            have = results.recorded(p)
            self.assertEqual(have, {('galaxy-1', '1')})
            results.append_rows(p, [r for r in [row] if (r['run'], r['seq']) not in have])
            with open(p) as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 1)
            self.assertEqual(list(rows[0]), results.HDR)
            sys.path.insert(0, os.path.join(REPO, 'tools'))
            import elolib
            self.assertEqual(results.HDR, elolib.HDR)
        finally:
            shutil.rmtree(d)


class SnapshotTest(unittest.TestCase):
    def test_records_and_render(self):
        d = tempfile.mkdtemp()
        try:
            g = os.path.join(d, 'games.csv')
            with open(g, 'w') as fh:
                fh.write('run,seq,teamA,teamB,map,winner,rounds,reason,seed\n'
                         'galaxy-1,1,us:g_iter0,team-remember-to-hydrate.sprint_1,m,A,5,,map\n'
                         'galaxy-1,2,us:c_x,team-remember-to-hydrate.sprint_1,m,B,5,,map-rev\n'
                         'replica-1,1,us:g_iter0,x,m,A,5,ISL75,map\n')
            rec = snapshot.game_records(g, os.path.join(GALAXY, 'field-teams.tsv'), 'vibe23')
            self.assertEqual(rec, {'vibe23': [1, 1], 'remember-to-hydrate.sprint_1': [1, 1]})
            data = {'generated': '2026-10-08T01:00:00+00:00', 'site': 'https://galaxy.x', 'episode': 'bc23',
                    'ours': 'vibe23',
                    'ladder': [{'rank': 1, 'id': 3, 'name': 'a_b', 'rating': 237.04, 'has_active_submission': True,
                                'games': [3, 0], 'ours': False},
                               {'rank': 2, 'id': 28, 'name': 'vibe23', 'rating': 0.0, 'has_active_submission': True,
                                'games': [0, 3], 'ours': True}],
                    'recent': [{'id': 7, 'status': 'OK!', 'created': '2026-10-08T00:30:00Z', 'is_ranked': True,
                                'maps': ['Cee'], 'participants': [{'teamname': 'vibe23', 'score': 0, 'player_index': 0},
                                                                  {'teamname': 'a_b', 'score': 1, 'player_index': 1}]}]}
            md = snapshot.render_md(data)
            self.assertIn("galaxy replica's displayed rating", md)
            self.assertIn('| 1 | a\\_b | 237.0 | 3-0 | accepted |', md)
            self.assertIn('| 2 | **vibe23** | 0.0 | 0-3 | accepted |', md)
            self.assertIn('Oct 7 18:00 PDT', md)
            if snapshot.have_matplotlib():                 # the driver's tools/.venv
                paths = snapshot.write(data, d)
                with open(paths[0], 'rb') as fh:
                    self.assertEqual(fh.read(8), b'\x89PNG\r\n\x1a\n')
        finally:
            shutil.rmtree(d)


class Py310CompatTest(unittest.TestCase):
    """siarnaq's ranked requests sample maps from a dict view (Python 3.10 behaviour, an error on 3.11)."""

    def test_sample_of_dict_keys(self):
        import random
        import py310compat
        py310compat.apply()
        self.assertFalse(py310compat.apply())                  # idempotent
        maps = {f'm{i}': i for i in range(10)}
        got = random.sample(maps.keys(), 3)                    # api/compete/serializers.py, verbatim
        self.assertEqual(len(set(got)), 3)
        self.assertTrue(set(got) <= set(maps))
        self.assertEqual(len(random.Random(4).sample({1, 2, 3}, 2)), 2)
        self.assertEqual(random.Random(1).sample(range(100), 5), random.Random(1).sample(list(range(100)), 5))
        with self.assertRaises(TypeError):
            random.sample(iter([1, 2]), 1)                     # non-sequences other than sets still fail


class RetiredLiteCaddyTest(unittest.TestCase):
    """galaxy-lite's host name after `vm-setup.sh retire-lite`: a redirect to the galaxy site, nothing proxied."""

    def test_render(self):
        import subprocess
        vm_setup = os.path.join(REPO, 'tools', 'replica', 'deploy', 'vm-setup.sh')
        setup = os.path.join(GALAXY, 'deploy', 'galaxy-setup.sh')
        h = '$2a$14$' + 'abcdefghijklmnopqrstuu' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ01234'
        env = dict(os.environ, GALAXY_SETUP=setup)

        def render(*flags):
            r = subprocess.run(['bash', vm_setup, 'print-caddyfile', '136-86-167-127.sslip.io', h, *flags],
                               capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            return r.stdout
        live, retired = render('1'), render('1', '1')
        old = retired[retired.index('\n136-86-167-127.sslip.io {'):retired.index('galaxy.136-86-167-127.sslip.io {')]
        self.assertIn('redir https://galaxy.136-86-167-127.sslip.io{uri} 302', old)
        self.assertNotIn('reverse_proxy', old)
        self.assertNotIn('basic_auth', old)
        self.assertIn('reverse_proxy 127.0.0.1:8023', live)
        self.assertNotIn('127.0.0.1:8023', retired)
        self.assertEqual(live[live.index('galaxy.136-86-167-127.sslip.io {'):],
                         retired[retired.index('galaxy.136-86-167-127.sslip.io {'):])     # the galaxy site unchanged
        self.assertEqual(retired.count('{'), retired.count('}'))
        alone = render('0', '1')
        self.assertIn('410', alone)
        self.assertNotIn('galaxy.', alone)


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1).result
    sys.exit(0 if r.wasSuccessful() else 1)
