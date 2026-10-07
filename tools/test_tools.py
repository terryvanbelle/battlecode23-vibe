#!/usr/bin/env python3
"""Unit tests for the analysis and process tools (synthetic inputs; no games). Run by tools/unit-tests.sh."""
import importlib.util, os, subprocess, sys, tempfile, unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, TOOLS / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class FilterYearTest(unittest.TestCase):
    """The reading-room filter must drop every block tagged with the forbidden year and keep everything else."""

    def setUp(self):
        self.f = load('filter_year', 'filter_year.py')

    def test_drops_tagged_bullet_with_continuation(self):
        md = "# T\n\n- keep me [2024 X]\n- drop me [2023 Y] first line\n  continuation of the dropped bullet\n- keep too\n"
        out = self.f.filt(md)
        self.assertIn('keep me', out)
        self.assertIn('keep too', out)
        self.assertNotIn('drop me', out)
        self.assertNotIn('continuation of the dropped', out)

    def test_drops_whole_section_under_tagged_heading(self):
        md = "# A\n\n### 3c. Something [2023 Team]\n\ntext in section\n\n```\ncode\n```\n\n### 3d. Other\n\nkept\n"
        out = self.f.filt(md)
        self.assertNotIn('text in section', out)
        self.assertNotIn('code', out)
        self.assertIn('kept', out)
        self.assertIn('3d. Other', out)

    def test_drops_code_block_introduced_by_dropped_colon_line(self):
        md = "para one\n\nLayout used (1024 bits) [2023 Z]:\n\n```\nsecret layout\n```\n\nafter\n"
        out = self.f.filt(md)
        self.assertNotIn('secret layout', out)
        self.assertIn('after', out)
        self.assertIn('para one', out)

    def test_nested_child_of_tagged_parent_dropped(self):
        md = "- parent [2014, 2023, 2025 Q]\n  - child a\n  - child b\n- sibling\n"
        out = self.f.filt(md)
        self.assertNotIn('child a', out)
        self.assertIn('sibling', out)

    def test_team_and_unit_names_without_year_are_dropped(self):
        md = "- kite like Gone Fishin' did\n- carriers throw cargo at the launcher\n- generic advice\n"
        out = self.f.filt(md)
        self.assertEqual(out.strip(), '- generic advice')

    def test_untagged_text_unchanged(self):
        md = "# Title\n\nPlain paragraph.\n\n- a\n- b\n"
        self.assertEqual(self.f.filt(md).strip(), md.strip())


class ParseResultTest(unittest.TestCase):
    """tools/lib.sh parse_result reads the engine's end-of-match lines."""

    def run_parse(self, text):
        cmd = f'source "{TOOLS}/lib.sh"; parse_result "$(cat)"'
        return subprocess.run(['bash', '-c', cmd], input=text, capture_output=True, text=True).stdout.strip()

    def test_win_line(self):
        log = ("[server] -------------------- Match Starting --------------------\n"
               "[server] a vs. b on maptestsmall\n"
               "[server]               a (A) wins (round 2000)\n"
               "[server] Reason: The winning team won on tiebreakers (more mana net worth).\n")
        self.assertEqual(self.run_parse(log), 'RESULT A 2000 The winning team won on tiebreakers (more mana net worth).')

    def test_b_wins_early(self):
        log = "[server]   x (B) wins (round 734)\n[server] Reason: The winning team won by anchoring sky islands.\n"
        self.assertEqual(self.run_parse(log), 'RESULT B 734 The winning team won by anchoring sky islands.')

    def test_garbage(self):
        self.assertEqual(self.run_parse('java.lang.OutOfMemoryError\n'), 'RESULT ? ? ?')


class BenchSelectTest(unittest.TestCase):
    """Name-only choice of a repo's final bot."""

    def setUp(self):
        self.s = load('bench_select', 'bench-select.py')

    def test_final_beats_versions(self):
        self.assertGreater(self.s.score('finalbot'), self.s.score('v12'))
        self.assertGreater(self.s.score('qualsbot'), self.s.score('sprint2'))
        self.assertGreater(self.s.score('v9'), self.s.score('v3'))

    def test_junk_pattern(self):
        for junk in ('examplefuncsplayer', 'testbot', 'donothing', 'template'):
            self.assertTrue(self.s.JUNK.search(junk), junk)
        self.assertFalse(self.s.JUNK.search('launcherbot'))


class ReplayDumpTest(unittest.TestCase):
    """The replay reader on a committed fixture: examplefuncsplayer mirror on maptestsmall, 2000 rounds, A wins on the
    mana tiebreak. Pinned numbers were cross-checked against the raw event stream (204 SPAWN_UNIT actions = 2 x 102
    built; B's 96 deaths = A's 86 attributed kills + 10 from HQ damage) and the engine's verdict (A 420 Mn vs B 17)."""
    FIX = REPO / 'test/fixtures/example-mirror-maptestsmall.bc23'

    @classmethod
    def setUpClass(cls):
        # outputs are cached by the hash of the reader's source and the fixture: they rerun whenever either changes
        import hashlib
        h = hashlib.sha1((TOOLS / 'replaydump/ReplayDump.java').read_bytes() + cls.FIX.read_bytes()).hexdigest()[:12]
        cache = REPO / 'build' / 'test-cache' / h
        cache.mkdir(parents=True, exist_ok=True)

        def dump(*args):
            f = cache / ('dump' + ''.join(args).replace('-', '_') + '.txt')
            if f.exists():
                return f.read_text()
            out = subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), str(cls.FIX), *args],
                                 capture_output=True, text=True, timeout=600).stdout
            if out.strip():
                f.write_text(out)
            return out
        cls.summary = dump()
        cls.census = dump('--census')
        cls.bc = dump('--bytecode')

    def test_result_and_builds(self):
        self.assertIn('result: A (examplefuncsplayer) wins at round 2000', self.summary)
        self.assertEqual(self.summary.count('built:  CARRIER=48 LAUNCHER=54'), 2)

    def test_deaths_and_kills(self):
        self.assertIn('died:   CARRIER=47 LAUNCHER=49', self.summary)
        self.assertIn('kills=86', self.summary)

    def test_final_bank_matches_tiebreak(self):
        self.assertIn('r2000[Ad441 Mn420 Ex0', self.summary)
        self.assertIn('r2000[Ad46 Mn17 Ex0', self.summary)

    def test_census_shape(self):
        lines = self.census.strip().splitlines()
        self.assertEqual(len(lines), 3)
        hdr = lines[0].split(',')
        for row in lines[1:]:
            self.assertEqual(len(row.split(',')), len(hdr))
        a = dict(zip(hdr, lines[1].split(',')))
        self.assertEqual((a['side'], a['won'], a['rounds'], a['built_C'], a['built_L']), ('A', '1', '2000', '48', '54'))

    def test_bytecode_limits(self):
        self.assertIn('A HQ', self.bc)
        for line in self.bc.splitlines()[1:]:
            f = line.split()
            self.assertEqual(f[-2], '0', line)   # no overruns in the example bot


class ReplayDumpMultiGameTest(unittest.TestCase):
    """A galaxy match file holds one game per map: --games lists them and --game N reads one (fixture: g_iter0 vs
    examplefuncsplayer on maptestsmall then SmallElements, alternate order; the engine printed A wins r339 and r188)."""
    FIX = REPO / 'test/fixtures/two-games.bc23'

    def dump(self, *args):
        return subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), str(self.FIX), *args],
                              capture_output=True, text=True, timeout=600).stdout

    def test_games_and_selection(self):
        self.assertEqual(self.dump('--games').split('\n')[:2], ['0 maptestsmall A 339', '1 SmallElements A 188'])
        g1 = self.dump('--game', '1')
        self.assertIn('map SmallElements', g1)
        self.assertIn('wins at round 188', g1)
        self.assertNotIn('maptestsmall', g1)


class ContestClientTest(unittest.TestCase):
    """tools/contest.py offline pieces: the submission zip layout, multipart encoding, cells, game rows, site guard."""
    @classmethod
    def setUpClass(cls):
        cls.c = load('contest', TOOLS / 'contest.py')

    def test_zip_layout(self):
        import zipfile, io
        z = zipfile.ZipFile(io.BytesIO(self.c.zip_package('examplefuncsplayer')))
        names = z.namelist()
        self.assertIn('examplefuncsplayer/RobotPlayer.java', names)
        self.assertTrue(all(n.startswith('examplefuncsplayer/') and n.endswith('.java') for n in names))

    def test_multipart(self):
        body, ct = self.c.multipart({'package': 'p'}, {'source_code': ('s.zip', b'PK', 'application/zip')})
        b = ct.split('boundary=')[1]
        self.assertIn(b'name="package"\r\n\r\np\r\n', body)
        self.assertIn(b'filename="s.zip"', body)
        self.assertTrue(body.endswith(f'--{b}--\r\n'.encode()))

    def test_cells_and_rows(self):
        d = tempfile.mkdtemp()
        Path(d, 'c.txt').write_text('# x\nTeamX m1,m2 -\nTeamY m3\n')
        self.assertEqual(self.c.read_cells(str(Path(d, 'c.txt'))), [('TeamX', ['m1', 'm2'], '-'), ('TeamY', ['m3'], '+')])
        m = {'id': 7, 'alternate_order': True, 'participants': [
            {'team': 1, 'teamname': 'us', 'player_index': 1}, {'team': 2, 'teamname': 'TeamX', 'player_index': 0}]}
        orig = self.c.games_of
        self.c.games_of = lambda rep: [(0, 'm1', 'B', 300), (1, 'm2', 'A', 400)]
        try:
            rows = self.c.run_rows(m, 'x', 1)
        finally:
            self.c.games_of = orig
        self.assertEqual([(r['opponent'], r['map'], r['bot_side'], r['bot_result'], r['seed']) for r in rows],
                         [('TeamX', 'm1', 'B', 'win', 'map'), ('TeamX', 'm2', 'B', 'loss', 'map-rev')])

    def test_refuses_real_site(self):
        env = dict(os.environ, CONTEST_SITE='https://play.battlecode.org')
        r = subprocess.run([sys.executable, str(TOOLS / 'contest.py'), 'me'], env=env, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('refusing', r.stderr + r.stdout)
        with self.assertRaises(SystemExit):
            self.c.http('GET', 'https://api.battlecode.org/api/episode/e/')


class ProfileTest(unittest.TestCase):
    """profile.py: our rows are those whose side equals the cell side; means per team; micro_L fields are columns."""
    def test_means(self):
        d = tempfile.mkdtemp()
        hdr = 'cell_opponent,cell_map,cell_side,cell_seed,team,side,won,C100,micro_L\n'
        rows = ['X,m,A,1,bot,A,1,10,exposed=0.100 dmg/contact=4.0', 'X,m,A,1,X,B,0,20,exposed=0.300 dmg/contact=8.0',
                'X,m,B,2,X,A,1,30,', 'X,m,B,2,bot,B,0,30,exposed=0.300 dmg/contact=6.0']
        Path(d, 'census.csv').write_text(hdr + '\n'.join(rows) + '\n')
        out = subprocess.run([sys.executable, str(TOOLS / 'profile.py'), d, '--cols', 'won,C100,exposed,dmg/contact'],
                             capture_output=True, text=True).stdout.splitlines()
        us = out[1].split()
        x = out[2].split()
        self.assertEqual(us[:2], ['us', '2'])
        self.assertEqual([float(v) for v in us[2:]], [0.5, 20.0, 0.2, 5.0])
        self.assertEqual(x[:2], ['X', '2'])
        self.assertEqual([float(v) for v in x[2:]], [0.5, 25.0, 0.3, 8.0])


class MatchmakerTest(unittest.TestCase):
    """tools/replica-matchmaker.py: opponents come from the band of ranks around the challenger, never itself."""

    def setUp(self):
        self.m = load('matchmaker', 'replica-matchmaker.py')

    def test_band(self):
        import random
        teams = [(f't{i}', 2000 - i) for i in range(20)]
        rnd = random.Random(1)
        for _ in range(200):
            to = self.m.pick(teams, 't10', 3, rnd)
            self.assertIn(to, {'t7', 't8', 't9', 't11', 't12', 't13'})
        self.assertIn(self.m.pick(teams, 't0', 3, rnd), {'t1', 't2', 't3'})
        self.assertIsNone(self.m.pick(teams, 'nobody', 3, rnd))
        self.assertIsNone(self.m.pick([('solo', 1500)], 'solo', 3, rnd))


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=0).result
    print(f"test_tools: {r.testsRun} tests, {len(r.failures)} failures, {len(r.errors)} errors")
    sys.exit(0 if r.wasSuccessful() else 1)
