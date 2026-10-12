#!/usr/bin/env python3
"""Unit tests for the galaxy replica's operator tools (offline pieces only: no network, no games):
tools/galaxy/client.py (site guard, URL scope, multipart), field.py (names, blind packaging, compile-log filter,
opponent choice, queue count, accounts file), results.py (replay rows, paging, idempotent append) and snapshot.py
(records, markdown, chart). Run: python3 test/galaxy/test_field_tools.py (tools/unit-tests.sh runs it)."""
import csv
import contextlib
import copy
import datetime
import io
import json
import os
import random
import shutil
import stat
import sys
import tempfile
import unittest
from unittest import mock
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

    def test_challenger_weights_favour_the_low_end(self):
        lad = self.ladder()                                  # best first
        ids = {t['name']: t['id'] for t in lad}
        w = field.challenger_weights(lad, ['a', 'f', 'c'], ids)
        self.assertEqual(w, [1, 6, 3])

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

    def collector_matches(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        ours = self.match()
        ours.update(id=101, maps=['Cee', 'Maze'], episode='bc23', tournament_round=None,
                    created=(now - datetime.timedelta(hours=1)).isoformat(),
                    replay_url='/storage/bc23-replica-secure/episode/bc23/replays/00000000-0000-0000-0000-000000000101.bc23')
        ours['participants'][1]['score'] = 2
        ours['participants'][0]['score'] = 0
        field_match = copy.deepcopy(ours)
        field_match.update(id=100, created=(now - datetime.timedelta(hours=10)).isoformat(),
                           replay_url='/storage/bc23-replica-secure/episode/bc23/replays/00000000-0000-0000-0000-000000000100.bc23')
        field_match['participants'][1]['teamname'] = 'field-a'
        return field_match, ours

    @contextlib.contextmanager
    def collector_fixture(self, matches, errors):
        """Run main against local files and mocked API/replay decoding only."""
        with tempfile.TemporaryDirectory(prefix='bc23-results-test-') as directory, contextlib.ExitStack() as stack:
            games = os.path.join(directory, 'games.csv')
            state = os.path.join(directory, 'state.json')
            gate = os.path.join(directory, 'test-gate')
            keep = os.path.join(directory, 'replays')
            touch(gate, 'test-only-placeholder\n')
            existing = {'run': 'galaxy-90', 'seq': '1', 'teamA': 'a', 'teamB': 'b', 'map': 'Cee', 'winner': 'A',
                        'rounds': '55', 'reason': '', 'seed': 'map'}
            partial = dict(existing, run='galaxy-100')
            results.append_rows(games, [existing, partial])
            results.save_state({'low_water': 100}, state)
            with open(games, 'rb') as source:
                original_games = source.read()
            with open(state, 'rb') as source:
                original_state = source.read()
            c = client.Client(site='https://replica.example.invalid', gate='Basic test-only-placeholder', episode='bc23')

            def request(method, url, **kwargs):
                c.path_of(url)  # Exercise the real same-origin guard without opening a connection.
                if url in errors:
                    raise client.ApiError(errors[url], 'test-only unavailable replay')
                return b'test-only replay placeholder'

            c.request = mock.Mock(side_effect=request)
            staff = mock.Mock()
            staff.api.return_value = {'results': sorted(matches, key=lambda m: -m['id']), 'next': None}
            ours = mock.Mock()
            ours.pages.return_value = [{'id': 24, 'package': 'g_iter0'}]
            real_load, real_save = results.load_state, results.save_state
            stack.enter_context(mock.patch.object(results, 'Client', return_value=c))
            stack.enter_context(mock.patch.object(results, 'GATE_FILE', gate))
            stack.enter_context(mock.patch.object(results, 'Session', side_effect=lambda _c, user, _pw: ours if user == 'our-user' else staff))
            stack.enter_context(mock.patch.object(results, 'team_credentials', return_value=('our-user', 'test-only-placeholder')))
            stack.enter_context(mock.patch.object(results, 'entrant_names', return_value={}))
            stack.enter_context(mock.patch.object(results, 'games_of', return_value=[(0, 'Cee', 'A', 101), (1, 'Maze', 'A', 102)]))
            stack.enter_context(mock.patch.object(results, 'load_state', side_effect=lambda: real_load(state)))
            save = stack.enter_context(mock.patch.object(results, 'save_state', side_effect=lambda value: real_save(value, state)))
            output = stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            yield {'args': ['--games', games, '--keep', keep], 'games': games, 'state': state, 'original_games': original_games,
                   'original_state': original_state, 'gaps': os.path.join(directory, 'field-replay-gaps.jsonl'),
                   'save': save, 'request': c.request, 'output': output}

    def test_collector_audits_missing_old_field_replay_then_collects_ours(self):
        for status in (404, 410):
            with self.subTest(status=status):
                field_match, ours = self.collector_matches()
                with self.collector_fixture([field_match, ours], {field_match['replay_url']: status}) as fixture:
                    self.assertEqual(results.main(fixture['args']), 0)
                    with open(fixture['games'], 'rb') as source:
                        collected = source.read()
                    self.assertTrue(collected.startswith(fixture['original_games']))
                    rows = list(csv.DictReader(io.StringIO(collected.decode())))
                    self.assertEqual(len(rows), 4)
                    self.assertNotIn(('galaxy-100', '2'), {(r['run'], r['seq']) for r in rows})
                    self.assertEqual([(r['run'], r['winner']) for r in rows[-2:]], [('galaxy-101', 'A')] * 2)
                    with open(fixture['gaps']) as source:
                        gaps = [json.loads(line) for line in source]
                    self.assertEqual(len(gaps), 1)
                    self.assertEqual(gaps[0]['missing_sequences'], [2])
                    self.assertEqual(gaps[0]['http_status'], status)
                    self.assertEqual(gaps[0]['reason'], 'retention_eligible_replay_unavailable')
                    self.assertNotIn('winner', gaps[0])
                    with open(fixture['state']) as source:
                        self.assertEqual(json.load(source), {'low_water': 102})
                    self.assertIn('retention-eligible field replay unavailable', fixture['output'].getvalue())
                    self.assertEqual(results.main(fixture['args'] + ['--full']), 0)
                    with open(fixture['games'], 'rb') as source:
                        self.assertEqual(source.read(), collected)
                    with open(fixture['gaps']) as source:
                        self.assertEqual(len(source.readlines()), 1)

    def test_collector_does_not_skip_other_replay_failures_or_advance_checkpoint(self):
        base, _ = self.collector_matches()
        cases = []
        for code in (401, 403, 500, 502):
            cases.append(('HTTP ' + str(code), copy.deepcopy(base), code))
        for key, value in (('created', datetime.datetime.now(datetime.timezone.utc).isoformat()),
                           ('created', '2026-10-01T00:00:00'), ('created', 'bad date'),
                           ('tournament_round', 7), ('episode', 'bc24'),
                           ('replay_url', '/replay/obsolete'),
                           ('replay_url', base['replay_url'].replace('/bc23/', '/bc24/'))):
            match = copy.deepcopy(base)
            match[key] = value
            cases.append((key + '=' + str(value), match, 404))
        match = copy.deepcopy(base)
        del match['tournament_round']
        cases.append(('unknown tournament scope', match, 404))
        for code in (404, 410):
            match = copy.deepcopy(base)
            match['participants'][1]['teamname'] = 'vibe23'
            cases.append(('our replay ' + str(code), match, code))
        for name, match, code in cases:
            with self.subTest(case=name), self.collector_fixture([match], {match['replay_url']: code}) as fixture:
                with self.assertRaises(client.ApiError):
                    results.main(fixture['args'])
                fixture['save'].assert_not_called()
                with open(fixture['state'], 'rb') as source:
                    self.assertEqual(source.read(), fixture['original_state'])
                with open(fixture['games'], 'rb') as source:
                    self.assertEqual(source.read(), fixture['original_games'])
                self.assertFalse(os.path.exists(fixture['gaps']))

    def test_collector_missing_replay_url_is_fatal_for_field_and_ours(self):
        field_match, ours = self.collector_matches()
        for match in (field_match, ours):
            match['replay_url'] = None
            with self.subTest(match=match['id']), self.collector_fixture([match], {}) as fixture:
                with self.assertRaisesRegex(RuntimeError, 'no replay_url'):
                    results.main(fixture['args'])
                fixture['save'].assert_not_called()
                fixture['request'].assert_not_called()
                with open(fixture['state'], 'rb') as source:
                    self.assertEqual(source.read(), fixture['original_state'])

    def test_collector_audits_a_gap_before_later_failure_without_advancing(self):
        field_match, ours = self.collector_matches()
        errors = {field_match['replay_url']: 404, ours['replay_url']: 404}
        with self.collector_fixture([field_match, ours], errors) as fixture:
            with self.assertRaises(client.ApiError):
                results.main(fixture['args'])
            fixture['save'].assert_not_called()
            with open(fixture['state'], 'rb') as source:
                self.assertEqual(source.read(), fixture['original_state'])
            with open(fixture['games'], 'rb') as source:
                self.assertEqual(source.read(), fixture['original_games'])
            with open(fixture['gaps']) as source:
                self.assertEqual([json.loads(line)['match'] for line in source], [100])

    def test_incremental_max_batches_move_past_an_audited_gap(self):
        field_match, ours = self.collector_matches()
        with self.collector_fixture([field_match, ours], {field_match['replay_url']: 404}) as fixture:
            args = fixture['args'] + ['--max', '1']
            self.assertEqual(results.main(args), 0)
            fixture['save'].assert_not_called()
            self.assertEqual(fixture['request'].call_count, 1)
            self.assertEqual(results.main(args), 0)
            self.assertEqual(fixture['request'].call_count, 2)
            self.assertEqual(fixture['request'].call_args.args[1], ours['replay_url'])
            with open(fixture['games']) as source:
                rows = list(csv.DictReader(source))
            self.assertEqual([(r['run'], r['seq']) for r in rows[-2:]], [('galaxy-101', '1'), ('galaxy-101', '2')])
            with open(fixture['gaps']) as source:
                self.assertEqual(len(source.readlines()), 1)
            self.assertIn('acknowledged before batching', fixture['output'].getvalue())
            self.assertEqual(results.main(args), 0)
            with open(fixture['state']) as source:
                self.assertEqual(json.load(source), {'low_water': 102})

    def test_audited_gap_suppression_revalidates_identity_and_eligibility(self):
        field_match, _ = self.collector_matches()
        with self.collector_fixture([field_match], {field_match['replay_url']: 404}) as fixture:
            self.assertEqual(results.main(fixture['args'] + ['--max', '1']), 0)
            field_match['participants'][1]['teamname'] = 'vibe23'
            with self.assertRaises(client.ApiError):
                results.main(fixture['args'] + ['--max', '1'])
            self.assertEqual(fixture['request'].call_count, 2)
            fixture['save'].assert_not_called()
        field_match, _ = self.collector_matches()
        with self.collector_fixture([field_match], {field_match['replay_url']: 404}) as fixture:
            self.assertEqual(results.main(fixture['args'] + ['--max', '1']), 0)
            partial = {'run': 'galaxy-100', 'seq': '2', 'teamA': 'a', 'teamB': 'b', 'map': 'Maze', 'winner': 'A',
                       'rounds': '55', 'reason': '', 'seed': 'map'}
            # A changed set of missing sequences must not inherit an older audit.
            with open(fixture['games']) as source:
                rows = list(csv.DictReader(source))
            rows = [row for row in rows if row['run'] != 'galaxy-100']
            os.remove(fixture['games'])
            results.append_rows(fixture['games'], rows + [partial])
            self.assertEqual(results.main(fixture['args'] + ['--max', '1']), 0)
            self.assertEqual(fixture['request'].call_count, 2)
            with open(fixture['gaps']) as source:
                self.assertEqual([json.loads(line)['missing_sequences'] for line in source], [[2], [1]])

    def test_full_scan_retries_audited_gap_and_collects_restored_replay(self):
        field_match, _ = self.collector_matches()
        errors = {field_match['replay_url']: 404}
        with self.collector_fixture([field_match], errors) as fixture:
            self.assertEqual(results.main(fixture['args'] + ['--max', '1']), 0)
            errors.clear()  # The same replay URL is now available again.
            self.assertEqual(results.main(fixture['args'] + ['--full']), 0)
            self.assertEqual(fixture['request'].call_count, 2)
            with open(fixture['games']) as source:
                rows = list(csv.DictReader(source))
            self.assertIn(('galaxy-100', '2'), {(r['run'], r['seq']) for r in rows})
            with open(fixture['gaps']) as source:
                self.assertEqual(len(source.readlines()), 1)

    def test_collector_dry_run_does_not_write_gap_rows_or_checkpoint(self):
        field_match, ours = self.collector_matches()
        with self.collector_fixture([field_match, ours], {field_match['replay_url']: 404}) as fixture:
            self.assertEqual(results.main(fixture['args'] + ['--dry-run']), 0)
            fixture['save'].assert_not_called()
            self.assertFalse(os.path.exists(fixture['gaps']))
            with open(fixture['games'], 'rb') as source:
                self.assertEqual(source.read(), fixture['original_games'])
            with open(fixture['state'], 'rb') as source:
                self.assertEqual(source.read(), fixture['original_state'])
            self.assertIn('would audit', fixture['output'].getvalue())

    def test_retention_gap_checks_exact_age_participants_and_url_scope(self):
        match, _ = self.collector_matches()
        c = client.Client(site='https://replica.example.invalid', gate='Basic test', episode='bc23')
        now = datetime.datetime.now(datetime.timezone.utc)
        match['created'] = (now - datetime.timedelta(hours=6)).isoformat()
        self.assertIsNone(results.replay_gap(match, client.ApiError(404, ''), 'vibe23', c, set(), now=now))
        match['created'] = (now - datetime.timedelta(hours=6, seconds=1)).isoformat()
        self.assertIsNotNone(results.replay_gap(match, client.ApiError(404, ''), 'vibe23', c, set(), now=now))
        unicode_match = copy.deepcopy(match)
        unicode_match['created'] = (now - datetime.timedelta(hours=10)).isoformat().replace('+00:00', 'Z')
        unicode_match['participants'][0]['teamname'] = 'field-雪\nname'
        unicode_match['maps'] = ['迷宮\nmap']
        gap = results.replay_gap(unicode_match, client.ApiError(404, ''), 'vibe23', c, set(), now=now)
        self.assertIsNotNone(gap)
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'gaps.jsonl')
            results.append_gap(path, gap)
            with open(path) as source:
                lines = source.readlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0]), gap)
            self.assertEqual(results.recorded_gaps(path), {results.gap_key(gap)})
        protected = copy.deepcopy(match)
        protected['participants'][0]['teamname'] = 'vibe23'
        self.assertIsNone(results.replay_gap(protected, client.ApiError(404, ''), 'another-ours-name', c, set(), now=now))
        another_episode = client.Client(site=c.site, gate='Basic test', episode='bc24')
        other = dict(match, episode='bc24', replay_url=match['replay_url'].replace('bc23', 'bc24'))
        self.assertIsNone(results.replay_gap(other, client.ApiError(404, ''), 'vibe23', another_episode, set(), now=now))
        for participants in ([], match['participants'][:1], [dict(match['participants'][0], teamname=''), match['participants'][1]]):
            bad = dict(match, participants=participants)
            self.assertIsNone(results.replay_gap(bad, client.ApiError(404, ''), 'vibe23', c, set(), now=now))
        for url in ('https://elsewhere.invalid' + match['replay_url'], 'https://api.' + 'battlecode' + '.org' + match['replay_url']):
            with self.assertRaises(SystemExit):
                results.replay_gap(dict(match, replay_url=url), client.ApiError(404, ''), 'vibe23', c, set(), now=now)


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
