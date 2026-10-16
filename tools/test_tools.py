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


class ShotVisibilityTest(unittest.TestCase):
    """The replay has no in-turn move events: distinguish proven geometry from unresolved timing.

    The Java probe uses synthetic positions/terrain, not games. Fixture checks join every emitted shot back to the
    census, including hits, misses and unknowns, so the aggregate never silently drops unresolved shots.
    """
    FIX = ReplayDumpTest.FIX

    @classmethod
    def setUpClass(cls):
        import hashlib
        header = subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), '--census-header'],
                                capture_output=True, text=True, timeout=600)
        if header.returncode:
            raise RuntimeError(header.stderr)
        reader = REPO / 'build' / ('replaydump-' + hashlib.sha1((TOOLS / 'replaydump/ReplayDump.java').read_bytes()).hexdigest()[:12])
        cls.tmp = tempfile.TemporaryDirectory()
        cls.cp = os.pathsep.join((cls.tmp.name, str(reader), str(REPO / 'engine/battlecode23-3.0.15.jar')))
        src = Path(cls.tmp.name) / 'ShotGeometryProbe.java'
        src.write_text(r'''
package replaydump;
import java.util.*;
public class ShotGeometryProbe {
    static int[] ints(String s) { if (s.equals("-")) return new int[0]; return Arrays.stream(s.split(",")).mapToInt(Integer::parseInt).toArray(); }
    static ReplayDump.Robot robot(int id, int type, int pre, int post, int turn, int born, boolean dead) {
        ReplayDump.Robot r = new ReplayDump.Robot(); r.id=id; r.type=type; r.team=1; r.preX=pre%10; r.preY=pre/10;
        r.x=post%10; r.y=post/10; r.turnIdx=turn; r.turnRound=turn<0 ? -1 : 5; r.born=born; r.died=dead ? 5 : -1; return r;
    }
    public static void main(String[] a) throws Exception {
        if (a[0].equals("timing")) {
            ReplayDump d = new ReplayDump(a[1]); d.W=d.H=10; d.originX=d.originY=0;
            d.wall=new boolean[100]; d.cloud=new boolean[100]; d.current=new int[100];
            d.cloud[46]=d.cloud[47]=true; d.shotsOut=System.out;
            ReplayDump.Robot actor=robot(101,2,44,44,1,0,false);
            // The victim has not acted: use pre=(6,4), not end=(7,4) after its later move.
            d.classifyShot(actor,robot(102,2,46,47,2,0,false),102,false,5,1,new ReplayDump.ShotGeometry(10,10,d.wall,d.cloud,d.current));
            d.shotPositions.clear(); d.turnEndPositions.clear();
            d.classifyShot(actor,robot(102,2,46,47,0,0,false),102,false,5,2,new ReplayDump.ShotGeometry(10,10,d.wall,d.cloud,d.current));
            d.shotPositions.clear(); d.turnEndPositions.clear();
            d.classifyShot(actor,robot(102,1,46,47,-1,5,false),102,false,5,3,new ReplayDump.ShotGeometry(10,10,d.wall,d.cloud,d.current));
            d.shotPositions.clear(); d.turnEndPositions.clear();
            d.classifyShot(actor,robot(102,1,46,46,0,0,true),102,false,5,4,new ReplayDump.ShotGeometry(10,10,d.wall,d.cloud,d.current));
            d.shotPositions.clear(); d.turnEndPositions.clear();
            d.classifyShot(robot(101,2,45,44,1,0,false),null,-48,false,5,5,new ReplayDump.ShotGeometry(10,10,d.wall,d.cloud,d.current));
            d.shotPositions.clear(); d.turnEndPositions.clear(); d.current[45]=1; // WEST current, not an own move
            d.classifyShot(robot(101,2,45,44,1,0,false),null,-48,false,5,6,new ReplayDump.ShotGeometry(10,10,d.wall,d.cloud,d.current));
            d.shotPositions.clear(); d.turnEndPositions.clear(); d.current[45]=0;
            d.classifyShot(robot(101,2,44,44,1,0,true),null,-48,false,5,7,new ReplayDump.ShotGeometry(10,10,d.wall,d.cloud,d.current));
            d.shotPositions.clear(); d.turnEndPositions.clear();
            d.classifyShot(actor,robot(102,1,46,47,-1,5,true),102,false,5,8,new ReplayDump.ShotGeometry(10,10,d.wall,d.cloud,d.current));
            d.shotPositions.clear(); d.turnEndPositions.clear(); d.originX=2;
            d.classifyShot(actor,null,-48,false,5,9,new ReplayDump.ShotGeometry(10,10,d.wall,d.cloud,d.current));
            return;
        }
        int w=Integer.parseInt(a[1]), h=Integer.parseInt(a[2]);
        boolean[] walls=new boolean[w*h], clouds=new boolean[w*h]; int[] currents=new int[w*h];
        for(int p:ints(a[3])) walls[p]=true; for(int p:ints(a[4])) clouds[p]=true;
        if(!a[5].equals("-")) for(String pair:a[5].split(",")) { int[] v=Arrays.stream(pair.split(":")).mapToInt(Integer::parseInt).toArray(); currents[v[0]]=v[1]; }
        ReplayDump.ShotGeometry g=new ReplayDump.ShotGeometry(w,h,walls,clouds,currents);
        if(a[0].equals("end")) System.out.println(Arrays.toString(g.endpoints(Integer.parseInt(a[6]),Integer.parseInt(a[7]),Integer.parseInt(a[8]))));
        else if(a[0].equals("during")) System.out.println(Arrays.toString(g.duringTurn(Integer.parseInt(a[6]),ints(a[7]),Integer.parseInt(a[8]))));
        else if(a[0].equals("budget")) System.out.println(ReplayDump.ShotGeometry.maxMoves(Integer.parseInt(a[6])));
        else { ReplayDump.ShotGeometry.Verdict v=g.classify(ints(a[6]),ints(a[7]),Integer.parseInt(a[8]),Integer.parseInt(a[9]));
            System.out.println(ReplayDump.ShotGeometry.NAMES[v.state]+","+v.visible+","+v.outside); }
    }
}
''')
        built = subprocess.run(['javac', '-nowarn', '-encoding', 'UTF-8', '-d', cls.tmp.name, '-cp', cls.cp, str(src)],
                               capture_output=True, text=True, timeout=120)
        if built.returncode:
            raise RuntimeError(built.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def probe(self, mode, *args, clouds=(), walls=(), currents=(), size=(10, 10)):
        fmt = lambda values: ','.join(map(str, values)) or '-'
        command = ['java', '-cp', self.cp, 'replaydump.ShotGeometryProbe', mode, *map(str, size), fmt(walls), fmt(clouds),
                   fmt(f'{p}:{d}' for p, d in currents), *map(str, args)]
        return subprocess.run(command, capture_output=True, text=True, check=True, timeout=30).stdout.strip()

    def test_cloud_vision_boundary_and_clear_shots(self):
        self.assertEqual(self.probe('classify', '44', '46', 16, 20, clouds=(46,)), 'visible,1,0')
        self.assertEqual(self.probe('classify', '44', '47', 16, 20, clouds=(47,)), 'outside_vision,0,1')
        self.assertEqual(self.probe('classify', '44', '47', 16, 20, clouds=(44,)), 'outside_vision,0,1')
        self.assertEqual(self.probe('classify', '44', '48', 16, 20), 'visible,1,0')
        self.assertEqual(self.probe('classify', '44', '49', 16, 20), 'unknown,0,0')

    def test_self_and_wall_targets_are_legal_visible_misses(self):
        self.assertEqual(self.probe('classify', '44', '44', 16, 20, clouds=(44,)), 'visible,1,0')
        self.assertEqual(self.probe('classify', '44', '47', 16, 20, walls=(47,)), 'visible,1,0')

    def test_movement_timing_and_empty_geometry_stay_unknown(self):
        self.assertEqual(self.probe('classify', '44,45', '47', 16, 20, clouds=(47,)), 'unknown,1,1')
        self.assertEqual(self.probe('classify', '-', '47', 16, 20, clouds=(47,)), 'unknown,0,0')

    def test_inverse_current_preserves_blocked_and_pushed_sources(self):
        import ast
        ends = ast.literal_eval(self.probe('end', 45, 44, 1, currents=((45, 1),)))
        self.assertEqual(set(ends), {44, 45})
        self.assertEqual(set(ast.literal_eval(self.probe('end', 44, 44, 1, currents=((44, 5),)))), {44})
        self.assertEqual(set(ast.literal_eval(self.probe('during', 45, '44,45', 1))), {44, 45})

    def test_dead_robot_has_no_fake_stationary_endpoint(self):
        import ast
        ends = ast.literal_eval(self.probe('end', 44, -1, 1))
        self.assertEqual(len(ends), 9)
        self.assertIn(45, ends)
        self.assertEqual(self.probe('end', 44, 99, 1), '[]')

    def test_passability_and_minimum_cooldown_move_bounds(self):
        import ast
        self.assertEqual([int(self.probe('budget', t)) for t in range(6)], [0, 4, 1, 2, 1, 1])
        points = ast.literal_eval(self.probe('end', 44, -1, 4, walls=tuple(5 + y * 10 for y in range(10))))
        self.assertTrue(all(p % 10 < 5 for p in points))

    def test_hit_turn_order_spawn_and_current_timing(self):
        import csv, io
        result = subprocess.run(['java', '-cp', self.cp, 'replaydump.ShotGeometryProbe', 'timing', str(self.FIX)],
                                capture_output=True, text=True, check=True, timeout=30).stdout
        states = [row[12] for row in csv.reader(io.StringIO(result))]
        self.assertEqual(states, ['visible', 'outside_vision', 'visible', 'unknown', 'unknown', 'unknown', 'unknown', 'visible', 'unknown'])

    def test_fixture_shots_join_exactly_to_census_and_keep_miss_semantics(self):
        import csv, io
        def dump(*args):
            return subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), str(self.FIX), *args],
                                  capture_output=True, text=True, check=True, timeout=600).stdout
        shots = list(csv.DictReader(io.StringIO(dump('--shots'))))
        census = list(csv.DictReader(io.StringIO(dump('--census'))))
        with tempfile.TemporaryDirectory() as extracted:
            dump('--extract', extracted, '--games', '0', '--match', '9', '--shots')
            with open(Path(extracted) / 'shots.csv') as stream:
                emitted = list(csv.DictReader(stream))
            self.assertEqual([{**row, 'match': '9'} for row in shots], emitted)
            # Per-shot output is opt-in (large miss-heavy field replays); aggregate bounds are always in census.
            dump('--extract', extracted, '--games', '0')
            self.assertFalse((Path(extracted) / 'shots.csv').exists())
        for team in census:
            own = [s for s in shots if s['side'] == team['side'] and s['action'] == 'launch']
            n = len(own)
            self.assertEqual(n, int(team['shots']))
            self.assertEqual(team['miss_rate'], team['blind_rate'])
            self.assertAlmostEqual(float(team['miss_rate']), sum(s['hit'] == '0' for s in own) / n, places=3)
            counts = {v: sum(s['visibility'] == v for s in own) for v in ('visible', 'outside_vision', 'unknown')}
            self.assertEqual([int(team[k]) for k in ('shot_visible', 'shot_outside_vision', 'shot_visibility_unknown')], list(counts.values()))
            self.assertEqual(sum(counts.values()), n)
            self.assertEqual(float(team['outside_vision_rate_lower']), counts['outside_vision'] / n)
            self.assertEqual(float(team['outside_vision_rate_upper']), (counts['outside_vision'] + counts['unknown']) / n)
            for state, stem in (('outside_vision', 'outside_vision'), ('unknown', 'unknown_visibility')):
                for hit, suffix in (('1', 'hits'), ('0', 'misses')):
                    self.assertEqual(int(team[stem + '_' + suffix]), sum(s['visibility'] == state and s['hit'] == hit for s in own))


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


class ReplayDumpSaTest(unittest.TestCase):
    """--sa (behavioural-cloning rows) on two-games.bc23 game 0, team A (g_iter0): per-turn rows must add up to the
    summary's whole-game totals (built C12 L27 A3, anchors 5/5/5, deposited Ad640 Mn1080, collected Ad702 Mn1156,
    154 launcher shots), HQ round 1 sees the +200/+200 grant, and a launcher never moves two turns running (move
    cooldown 20 at m = 1, RULES.md 5.1) once current pushes are undone. tools/sa_extract.py drives it per panel."""
    FIX = ReplayDumpMultiGameTest.FIX

    @classmethod
    def setUpClass(cls):
        import csv
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / 'sa'
        cls.log = subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), str(cls.FIX), '--sa', '--team', 'A', '--game', '0',
                                  '--out', str(cls.out)], capture_output=True, text=True, timeout=600).stdout
        cls.raw = {k: (cls.out / f'sa_{k}.csv').read_text().splitlines() for k in ('L', 'HQ', 'C')}
        cls.rows = {k: list(csv.DictReader(v)) for k, v in cls.raw.items()}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_shape(self):
        self.assertIn('0 maptestsmall team=A name=g_iter0 rows_L=', self.log)
        for k, lines in self.raw.items():
            n = len(lines[0].split(','))
            self.assertGreater(len(lines), 100, k)
            for line in lines[1:]:
                self.assertEqual(len(line.split(',')), n, (k, line))

    def test_totals_match_summary(self):
        L, H, C = self.rows['L'], self.rows['HQ'], self.rows['C']
        s = lambda rows, col: sum(int(r[col]) for r in rows)
        self.assertEqual((s(H, 'built_C'), s(H, 'built_L'), s(H, 'built_A')), (12, 27, 3))
        self.assertEqual(s(H, 'anchors_std') + s(H, 'anchors_acc'), 5)
        self.assertEqual((s(C, 'anchor_take'), s(C, 'anchor_place')), (5, 5))
        self.assertEqual((s(C, 'dep_ad'), s(C, 'dep_mn')), (640, 1080))
        self.assertEqual(sum(int(r['collect_amt']) for r in C if r['collect_res'] == 'Ad'), 702)
        self.assertEqual(sum(int(r['collect_amt']) for r in C if r['collect_res'] == 'Mn'), 1156)
        self.assertEqual(s(L, 'n_attacks'), 154)
        h1 = H[0]
        self.assertEqual((h1['round'], h1['bank_Ad'], h1['bank_Mn'], h1['built_C'], h1['built_L']), ('1', '200', '200', '3', '2'))

    def test_launcher_turn_logic(self):
        last, consecutive = {}, 0
        for r in self.rows['L']:
            if r['moved'] == '1':
                consecutive += last.get(r['id']) == int(r['round']) - 1
                last[r['id']] = int(r['round'])
            if r['attacked'] == '1' and r['atk_order'] in ('before', 'after', 'either'):
                d_s, d_e = int(r['atk_d2_start']), int(r['atk_d2_end'])
                self.assertTrue(d_s <= 16 or d_e <= 16, r)
                self.assertEqual(r['atk_order'], 'either' if d_s <= 16 and d_e <= 16 else 'before' if d_s <= 16 else 'after')
            if r['atk_hit'] == '1':
                self.assertIn(r['atk_target_type'], 'CLADB')
                self.assertGreater(int(r['atk_target_hp_before']), 0)
        self.assertEqual(consecutive, 0)
        self.assertEqual(set(r['move_dir'] for r in self.rows['L']) - set(ReplayDumpSaTest.DIRS), set())

    DIRS = ('CENTER', 'NORTH', 'NORTHEAST', 'EAST', 'SOUTHEAST', 'SOUTH', 'SOUTHWEST', 'WEST', 'NORTHWEST', '?')

    def test_driver_panel(self):
        """sa_extract.py finds the opponent's games in a panel's results.csv and extracts both sides."""
        import csv, gzip
        sx = load('sa_extract', 'sa_extract.py')
        with tempfile.TemporaryDirectory() as d:
            panel = Path(d) / 'g' / '20990101-000000-panel-x'
            (panel / 'replays').mkdir(parents=True)
            os.symlink(self.FIX, panel / 'replays' / '77.bc23')
            (panel / 'results.csv').write_text('opponent,map,bot_side,winner_side,rounds,bot_result,reason,seed,game,match,submission\n'
                                               'examplefuncsplayer,maptestsmall,A,A,339,win,,map,0,77,1\n'
                                               'other.bot,maptestsmall,A,A,339,win,,map,0,78,1\n')
            self.assertEqual(list(sx.panel_games(panel / 'results.csv', 'example').items()),
                             [(('77', 'A'), ('examplefuncsplayer', [0]))])
            self.assertIsNone(sx.find_replay(str(panel), 78))
            out = Path(d) / 'clone'
            with open(os.devnull, 'w') as null:
                old, sys.stdout = sys.stdout, null
                try:
                    rc = sx.main(['example', '--panels', str(Path(d) / 'g' / '*-panel-*'), '--out', str(out)])
                finally:
                    sys.stdout = old
            self.assertEqual(rc, 0)
            with gzip.open(out / 'sa_HQ.csv.gz', 'rt') as f:
                opp = list(csv.DictReader(f))
            with gzip.open(out / 'ours_sa_L.csv.gz', 'rt') as f:
                ours = list(csv.DictReader(f))
            self.assertEqual((opp[0]['panel'], opp[0]['opponent'], opp[0]['match'], opp[0]['map']),
                             ('20990101-000000-panel-x', 'examplefuncsplayer', '77', 'maptestsmall'))
            self.assertEqual(len(ours), len(self.rows['L']))
            self.assertEqual(sum(int(r['n_attacks']) for r in ours), 154)


class WatchEventsTest(unittest.TestCase):
    """tools/watch_events.py pure parts (owner, PROMPTS 90): the watcher that wakes the session on events."""
    @classmethod
    def setUpClass(cls):
        cls.w = load('watch_events', TOOLS / 'watch_events.py')

    def test_vm_probe_expands_on_the_vm(self):
        cmd = self.w.vm_check_cmd().replace('source tools/vm.sh && ensure_vm >/dev/null 2>&1 && gssh ', 'echo ')
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
        self.assertIn('$(ls -t logs/*scr-*.log', out)       # sent literally, not run on the driver
        self.assertIn('tail -1 $f', out)
        self.assertIn('echo SWISS:$(basename $d)', out)

    def test_stuck_matches(self):
        now = 10_000.0
        ms = [{'id': 1, 'status': 'RUN', 'created': 'x'},   # seen RUN 1h01 ago: stuck
              {'id': 2, 'status': 'RUN', 'created': 'x'},   # seen RUN 30 min ago: not yet
              {'id': 5, 'status': 'RUN', 'created': 'x'},   # first seen now
              {'id': 3, 'status': 'OK!', 'created': 'x'},   # finished: dropped from the map
              {'id': 4, 'status': 'QUE', 'created': 'x'}]   # queued: never stuck by age
        stuck, since = self.w.stuck_matches(ms, {'1': now - 3660, '2': now - 1800, '3': now - 9000}, now)
        self.assertEqual(stuck, [1])
        self.assertEqual(since, {'1': now - 3660, '2': now - 1800, '5': now})

    def test_queue_stalled(self):
        import datetime as dt
        now = dt.datetime(2026, 10, 14, 18, 0, tzinfo=dt.timezone.utc)
        old = {'id': 4, 'status': 'QUE', 'created': '2026-10-14T11:00:00-04:00'}    # 3h queued
        new = {'id': 6, 'status': 'QUE', 'created': '2026-10-14T13:30:00-04:00'}    # 30 min queued
        run = {'id': 7, 'status': 'RUN', 'created': '2026-10-14T09:00:00-04:00'}
        self.assertTrue(self.w.queue_stalled([old, new], now))
        self.assertFalse(self.w.queue_stalled([old, run], now))     # the backlog is moving
        self.assertFalse(self.w.queue_stalled([new], now))

    def test_panels_done_and_dedupe(self):
        txt = ("trial: None\n"
               "parked: c_blind1 (submission 146) since 2026-10-14 09:01 PDT: panel done (run gauntlet/x)\n"
               "parked: c_mend3 (submission 148) since 2026-10-14 09:01 PDT: panel playing (run gauntlet/y)\n")
        self.assertEqual(self.w.panels_done(txt), ['c_blind1'])
        self.assertEqual(self.w.new_events(['PANEL_DONE c_blind1', 'HEARTBEAT'], {'PANEL_DONE c_blind1'}), ['HEARTBEAT'])

    def test_seen_file(self):
        d = tempfile.mkdtemp(); p = str(Path(d, 'seen'))
        self.assertEqual(self.w.load_seen(p), set())
        self.w.mark_seen('SCREEN_DONE j1', p); self.w.mark_seen('STUCK_MATCH 6282', p)
        self.assertEqual(self.w.load_seen(p), {'SCREEN_DONE j1', 'STUCK_MATCH 6282'})


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
            {'team': 1, 'teamname': 'us', 'player_index': 1, 'submission': 24}, {'team': 2, 'teamname': 'TeamX', 'player_index': 0}]}
        orig = self.c.games_of
        self.c.games_of = lambda rep: [(0, 'm1', 'B', 300), (1, 'm2', 'A', 400)]
        try:
            rows = self.c.run_rows(m, 'x', 1)
        finally:
            self.c.games_of = orig
        self.assertEqual([(r['opponent'], r['map'], r['bot_side'], r['bot_result'], r['seed']) for r in rows],
                         [('TeamX', 'm1', 'B', 'win', 'map'), ('TeamX', 'm2', 'B', 'loss', 'map-rev')])
        self.assertEqual({r['submission'] for r in rows}, {24})

    def test_pick_upward(self):
        import random
        ladder = [{'id': 1, 'name': 'a', 'rating': 900, 'status': 'R', 'active': True},
                  {'id': 2, 'name': 'b', 'rating': 700, 'status': 'R', 'active': True},
                  {'id': 3, 'name': 'c', 'rating': 650, 'status': 'R', 'active': False},
                  {'id': 4, 'name': 'us', 'rating': 600, 'status': 'R', 'active': True},
                  {'id': 5, 'name': 'd', 'rating': 500, 'status': 'R', 'active': True}]
        picks = {self.c.pick_upward(ladder, 4, 1, random.Random(k))['id'] for k in range(20)}
        self.assertEqual(picks, {2})                       # closest above with a submission; never below
        self.assertIsNone(self.c.pick_upward(ladder, 1, 3, random.Random(0)))

    @staticmethod
    def match(mid, opp, maps, sub, status='OK!'):
        return {'id': mid, 'status': status, 'maps': maps, 'participants': [
            {'team': 1, 'teamname': 'us', 'player_index': 0, 'submission': sub},
            {'team': 2, 'teamname': opp, 'player_index': 1, 'submission': 9}]}

    def block_env(self, active_ids, match_lists):
        """contest.block with every replica call stubbed. Successive active-submission reads return active_ids, and
        successive match-list reads return match_lists (the first sets the floor); the last element repeats. Returns
        (the opponents requested, {'rows': the rows written})."""
        c, made, written = self.c, [], {}
        act, ml = list(active_ids), list(match_lists)

        def active():
            return {'id': act.pop(0) if len(act) > 1 else act[0], 'package': 'p'}

        def matches(tid, limit_pages=1):
            return ml.pop(0) if len(ml) > 1 else ml[0]

        def request(opp, ranked, maps, order):
            made.append(opp)
            return {'id': 500 + len(made)}
        stubs = dict(me=lambda: {'id': 1, 'name': 'us'}, active_submission=active, matches=matches, request=request,
                     download=lambda m, d: f'rep-{m["id"]}', report_hook=lambda *a: None,
                     run_rows=lambda m, rep, tid: [{'match': m['id'], 'submission': c.our_submission(m, tid)}],
                     games_of=lambda rep: [(0, 'm1', 'A', 100)], census_of=lambda rep, rows: [],
                     write_run=lambda run, rows, census: written.update(rows=rows))
        for k, f in stubs.items():
            self.addCleanup(setattr, c, k, getattr(c, k))
            setattr(c, k, f)
        return made, written

    def cells_file(self):
        d = tempfile.mkdtemp()
        Path(d, 'cells.txt').write_text('TeamX m1,m2 +\nTeamY m3 +\n')
        return str(Path(d, 'cells.txt')), d

    def test_block_pairs_by_submission_with_overlapping_panels(self):
        """Two panels of identical cells overlap (a parked trial's, submission 140, and the next one's, 142), with the
        same match floor: each block takes only the matches its own submission plays, even when the other panel's
        finish first and come first in the list (the opponent, map set and floor alone would take them)."""
        import io, json, contextlib
        cells, d = self.cells_file()
        floor = [self.match(100, 'TeamZ', ['m9'], 130)]
        a = [self.match(101, 'TeamX', ['m2', 'm1'], 140), self.match(102, 'TeamY', ['m3'], 140)]
        b = [self.match(103, 'TeamX', ['m1', 'm2'], 142), self.match(104, 'TeamY', ['m3'], 142)]
        for sub, mine in ((140, a), (142, b)):
            run = os.path.join(d, f'run{sub}')
            made, written = self.block_env([sub], [floor, b[::-1] + a[::-1] + floor])
            with contextlib.redirect_stdout(io.StringIO()):
                self.c.block(cells, 't', poll=0, max_wait=1, run=run)
            self.assertEqual(made, ['TeamX', 'TeamY'])
            self.assertEqual(sorted(r['match'] for r in written['rows']), [m['id'] for m in mine])
            self.assertEqual({r['submission'] for r in written['rows']}, {sub})
            log = [json.loads(l) for l in open(os.path.join(run, 'requests.jsonl'))]
            self.assertEqual([e['submission'] for e in log], [sub, sub])
        # the parked panel's matches still wait while the next panel's are done: none of those is taken
        run = os.path.join(d, 'run140-waiting')
        made, written = self.block_env([140], [floor, b[::-1] + [dict(m, status='RUN') for m in a[::-1]] + floor])
        with contextlib.redirect_stdout(io.StringIO()):
            self.c.block(cells, 't', poll=0.01, max_wait=0.1, run=run)
        self.assertEqual(written['rows'], [])

    def test_block_stops_when_the_active_submission_changes(self):
        import io, json, contextlib
        cells, d = self.cells_file()
        run = os.path.join(d, 'run')
        made, _ = self.block_env([140, 140, 141], [[self.match(100, 'TeamZ', ['m9'], 130)]])
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            self.c.block(cells, 't', poll=0, max_wait=1, run=run)
        self.assertIn('141, not 140', str(cm.exception))
        self.assertEqual(made, ['TeamX'])                                           # the second request was not made
        self.assertEqual([json.loads(l)['submission'] for l in open(os.path.join(run, 'requests.jsonl'))], [140])

    def test_block_resume_keeps_the_old_rule_for_old_entries(self):
        """RESUME: an entry written before the submission field pairs by opponent, map set and floor; the new request
        records the active submission and pairs with it only. A resumed block whose entries name another submission
        than the active one makes no new request."""
        import io, json, contextlib
        from unittest import mock
        cells, d = self.cells_file()
        run = Path(d, 'run')
        run.mkdir()
        old = {'cell': 0, 'opponent': 'TeamX', 'maps': ['m1', 'm2'], 'order': '+', 'request': 7, 'at': 0}
        (run / 'requests.jsonl').write_text(json.dumps(old) + '\n')
        (run / 'match_floor.txt').write_text('100')
        ms = [self.match(108, 'TeamY', ['m3'], 140), self.match(107, 'TeamY', ['m3'], 142),
              self.match(105, 'TeamX', ['m1', 'm2'], 140), self.match(99, 'TeamX', ['m1', 'm2'], 142)]
        made, written = self.block_env([142], [ms])
        with mock.patch.dict(os.environ, {'RESUME': str(run)}), contextlib.redirect_stdout(io.StringIO()):
            self.c.block(cells, 't', poll=0, max_wait=1)
        self.assertEqual(made, ['TeamY'])
        self.assertEqual(sorted(r['match'] for r in written['rows']), [105, 107])
        self.assertEqual([json.loads(l).get('submission') for l in open(run / 'requests.jsonl')], [None, 142])
        run2 = Path(d, 'run2')
        run2.mkdir()
        (run2 / 'requests.jsonl').write_text(json.dumps(dict(old, submission=140)) + '\n')
        (run2 / 'match_floor.txt').write_text('100')
        made, _ = self.block_env([142], [ms])
        with mock.patch.dict(os.environ, {'RESUME': str(run2)}), self.assertRaises(SystemExit), \
                contextlib.redirect_stdout(io.StringIO()):
            self.c.block(cells, 't', poll=0, max_wait=1)
        self.assertEqual(made, [])

    def test_answers_submission_rule(self):
        M = self.match
        req = {'opponent': 'TeamX', 'maps': ['m1'], 'submission': 140}
        self.assertTrue(self.c.answers(M(101, 'TeamX', ['m1'], 140), req, 1, 100))
        self.assertFalse(self.c.answers(M(101, 'TeamX', ['m1'], 142), req, 1, 100))      # the other panel's
        self.assertFalse(self.c.answers(M(101, 'TeamX', ['m1'], None), req, 1, 100))     # a null submission
        self.assertFalse(self.c.answers(M(100, 'TeamX', ['m1'], 140), req, 1, 100))      # at the floor
        old = {k: v for k, v in req.items() if k != 'submission'}                        # an entry from before
        self.assertTrue(self.c.answers(M(101, 'TeamX', ['m1'], 142), old, 1, 100))
        bare = M(101, 'TeamX', ['m1'], 140)
        del bare['participants'][0]['submission']                                        # an API without the field
        self.assertTrue(self.c.answers(bare, req, 1, 100))
        self.assertIsNone(self.c.our_submission(bare, 1))

    def test_block_plays_only_the_given_submission(self):
        """trial-start passes its candidate's submission: a block that finds another one active makes no request, and
        a resumed run whose requests name another submission is not resumed."""
        import io, json, contextlib
        cells, d = self.cells_file()
        made, _ = self.block_env([140], [[self.match(100, 'TeamZ', ['m9'], 130)]])
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            self.c.block(cells, 't', poll=0, max_wait=1, run=os.path.join(d, 'run'), submission=141)
        self.assertIn('140, not 141', str(cm.exception))
        self.assertEqual(made, [])
        run = Path(d, 'run2')
        run.mkdir()
        (run / 'requests.jsonl').write_text(json.dumps({'cell': 0, 'opponent': 'TeamX', 'maps': ['m1', 'm2'],
                                                        'order': '+', 'request': 7, 'submission': 140, 'at': 0}) + '\n')
        made, _ = self.block_env([141], [[self.match(100, 'TeamZ', ['m9'], 130)]])
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            self.c.block(cells, 't', poll=0, max_wait=1, run=str(run), submission=141)
        self.assertIn('made by submission 140, not 141', str(cm.exception))
        self.assertEqual(made, [])

    def test_block_resume_of_an_old_run_keeps_its_first_build(self):
        """A run from before the submission field, resumed after the active submission changed: its first provenance
        line names the build its requests played, so no new request plays another build; resumed while that build is
        still active, the new request records it."""
        import io, json, contextlib
        from unittest import mock
        cells, d = self.cells_file()
        run = Path(d, 'run')
        run.mkdir()
        old = {'cell': 0, 'opponent': 'TeamX', 'maps': ['m1', 'm2'], 'order': '+', 'request': 7, 'at': 0}
        (run / 'requests.jsonl').write_text(json.dumps(old) + '\n')
        (run / 'match_floor.txt').write_text('100')
        (run / 'provenance.txt').write_text('team=us team_id=1 site=x cells=c match_floor=100 '
                                            'latest_accepted_submission=140 package=p\n')
        ms = [self.match(108, 'TeamY', ['m3'], 140), self.match(105, 'TeamX', ['m1', 'm2'], 140)]
        made, _ = self.block_env([142], [ms])
        with mock.patch.dict(os.environ, {'RESUME': str(run)}), self.assertRaises(SystemExit) as cm, \
                contextlib.redirect_stdout(io.StringIO()):
            self.c.block(cells, 't', poll=0, max_wait=1)
        self.assertIn('142, not 140', str(cm.exception))
        self.assertEqual(made, [])
        made, written = self.block_env([140], [ms])
        with mock.patch.dict(os.environ, {'RESUME': str(run)}), contextlib.redirect_stdout(io.StringIO()):
            self.c.block(cells, 't', poll=0, max_wait=1)
        self.assertEqual(made, ['TeamY'])
        self.assertEqual(sorted(r['match'] for r in written['rows']), [105, 108])
        self.assertEqual([json.loads(l).get('submission') for l in open(run / 'requests.jsonl')], [None, 140])

    def test_refuses_real_site(self):
        env = dict(os.environ, CONTEST_SITE='https://play.battlecode.org')
        r = subprocess.run([sys.executable, str(TOOLS / 'contest.py'), 'me'], env=env, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('refusing', r.stderr + r.stdout)
        with self.assertRaises(SystemExit):
            self.c.http('GET', 'https://api.battlecode.org/api/episode/e/')


class LadderPolicyTest(unittest.TestCase):
    """tools/ladder_policy.py: ranked only with the validated build active, burst while young or fresh, trials only
    when they end before the next autoscrim (docs/LADDER_STRATEGY.md)."""
    @classmethod
    def setUpClass(cls):
        cls.p = load('ladder_policy', TOOLS / 'ladder_policy.py')
        cls.real = cls.p.contest

    def t(self, h, m=0, day=8):
        import datetime
        return datetime.datetime(2026, 10, day, h, m, tzinfo=datetime.timezone.utc)

    def test_next_cron(self):
        self.assertEqual(self.p.next_cron('0 */8 * * *', self.t(2, 30)), self.t(8))
        self.assertEqual(self.p.next_cron('0 */8 * * *', self.t(16, 0)), self.t(0, day=9))
        self.assertEqual(self.p.next_cron('15 3 * * *', self.t(4)), self.t(3, 15, day=9))
        self.assertIsNone(self.p.next_cron('garbage', self.t(1)))

    def test_mode(self):
        import datetime
        self.assertEqual(self.p.ranked_mode(5, None, self.t(9)), 'BURST')
        self.assertEqual(self.p.ranked_mode(40, self.t(9) - datetime.timedelta(hours=2), self.t(9)), 'BURST')
        self.assertEqual(self.p.ranked_mode(40, self.t(9) - datetime.timedelta(hours=30), self.t(9)), 'MAINTAIN')

    def test_may_challenge(self):
        import datetime
        st = {'validated': {'submission': 24}, 'trial': None}
        now = self.t(9)
        self.assertEqual(self.p.may_challenge(st, 24, 0, None, 'BURST', now), (True, 'BURST'))
        self.assertFalse(self.p.may_challenge(dict(st, trial={'submission': 30}), 30, 0, None, 'BURST', now)[0])
        self.assertFalse(self.p.may_challenge(st, 30, 0, None, 'BURST', now)[0])          # a candidate is active
        self.assertFalse(self.p.may_challenge(st, 24, 2, None, 'BURST', now)[0])          # queue busy
        self.assertFalse(self.p.may_challenge(st, 24, 0, now - datetime.timedelta(minutes=10), 'MAINTAIN', now)[0])
        self.assertTrue(self.p.may_challenge(st, 24, 0, now - datetime.timedelta(minutes=10), 'BURST', now)[0])

    def test_pick_open_skips_resting(self):
        import random, datetime
        now = self.t(9)
        ladder = [{'id': 1, 'name': 'a', 'rating': 900, 'status': 'R', 'active': True},
                  {'id': 2, 'name': 'b', 'rating': 800, 'status': 'R', 'active': True},
                  {'id': 4, 'name': 'us', 'rating': 700, 'status': 'R', 'active': True}]
        rested = {2: now + datetime.timedelta(minutes=5)}
        self.assertEqual(self.p.pick_open(ladder, 4, rested, now, random.Random(0))['id'], 1)
        rested[1] = now + datetime.timedelta(minutes=5)
        self.assertIsNone(self.p.pick_open(ladder, 4, rested, now, random.Random(0)))

    def test_expected_gain(self):
        self.assertAlmostEqual(self.p.expected_gain(0.5, 1600, 1600), 0.0)
        self.assertAlmostEqual(self.p.expected_gain(0.626, 1654.1, 1656.2), 24 * (0.626 - 0.496978), places=3)   # we are 2.1 below: E < 0.5
        self.assertLess(self.p.expected_gain(0.157, 1654, 1776), 0)     # BT: far weaker than galaxy thinks

    def test_pick_gain(self):
        import datetime
        now = self.t(9)
        ladder = [{'id': 1, 'name': 'a', 'rating': 900, 'status': 'R', 'active': True},
                  {'id': 2, 'name': 'b', 'rating': 750, 'status': 'R', 'active': True},
                  {'id': 3, 'name': 'c', 'rating': 760, 'status': 'R', 'active': False},
                  {'id': 5, 'name': 'd', 'rating': 600, 'status': 'R', 'active': True},
                  {'id': 4, 'name': 'us', 'rating': 700, 'status': 'R', 'active': True}]
        P = {'a': 0.45, 'b': 0.60, 'c': 0.99, 'd': 0.99}    # c inactive, d below us: never picked
        opp, g = self.p.pick_gain(ladder, 4, {}, now, P)
        self.assertEqual(opp['id'], 1)                     # 24 (0.45 - 0.240) = 5.0 beats 24 (0.60 - 0.429) = 4.1
        opp, g = self.p.pick_gain(ladder, 4, {1: now + datetime.timedelta(minutes=5)}, now, P)
        self.assertEqual(opp['id'], 2)                     # a rests
        opp, g = self.p.pick_gain(ladder, 4, {}, now, {'a': 0.1, 'b': 0.3})
        self.assertIsNone(opp); self.assertLess(g, 0)      # every gain negative: no request
        self.assertEqual(self.p.pick_gain(ladder, 4, {}, now, {}), (None, None))   # no estimates

    def test_trial_window(self):
        self.assertTrue(self.p.trial_window_ok(self.t(16), self.t(9)))
        self.assertFalse(self.p.trial_window_ok(self.t(8), self.t(6)))
        self.assertTrue(self.p.trial_window_ok(None, self.t(6)))

    @staticmethod
    def screen_record(d, name, ch, ih, verdict='PASS', reduced=False):
        import json
        p = Path(d, f'{name}-{ch}' + ('.reduced' if reduced else '') + '.json')
        p.write_text(json.dumps({'v': 1, 'candidate': name, 'candidate_hash': ch, 'incumbent': 'inc',
                                 'incumbent_hash': ih, 'reduced': reduced, 'verdict': verdict, 'reasons': []}))
        return p

    def test_screen_check(self):
        """A PASS record for the candidate's code hash against the incumbent's hash admits a trial; nothing else does."""
        d = tempfile.mkdtemp()
        ch, ih = 'a' * 12, 'b' * 12
        self.assertFalse(self.p.screen_check(d, ch, ih)[0])                          # no record
        self.screen_record(d, 'x', ch, 'c' * 12)
        ok, _, why = self.p.screen_check(d, ch, ih)
        self.assertFalse(ok)
        self.assertIn('not ' + ih, why)                                               # other incumbent
        self.screen_record(d, 'x', ch, ih, verdict='FAIL')
        self.assertFalse(self.p.screen_check(d, ch, ih)[0])
        self.screen_record(d, 'x', ch, ih, reduced=True)                              # reduced map set: never
        self.assertFalse(self.p.screen_check(d, ch, ih)[0])
        p = self.screen_record(d, 'renamed', ch, ih)                                  # found by hash, not name
        self.assertEqual(self.p.screen_check(d, ch, ih), (True, str(p), 'PASS'))
        self.assertFalse(self.p.screen_check(d, None, ih)[0])

    def trial_env(self, records=(), state=None, **over):
        """ladder_policy with a temporary state and screens dir, stub hashes, and a contest stub that records calls
        (`over`: replacement stubs, given the call list and the temporary dir: name -> f(calls, d))."""
        import json, types
        d = tempfile.mkdtemp()
        st = Path(d, 'state.json')
        st.write_text(json.dumps(state or {'validated': {'submission': 24, 'package': 'inc'}, 'trial': None,
                                           'history': []}))
        for ch in records:
            self.screen_record(d, 'cand', ch, 'b' * 12)
        calls = []

        def stub(name, ret=None):
            def f(*a, **k):
                calls.append(name)
                return ret
            return f
        real = self.real
        fake = types.SimpleNamespace(
            pages=stub('pages', [{'id': 24, 'accepted': True}]), set_auto_accept=stub('set_auto_accept'),
            submit=stub('submit', {'id': 30}), wait_submission=stub('wait', {'status': 'OK!', 'accepted': True}),
            block=stub('block', os.path.join(d, 'run')), me=stub('me', {'id': 1, 'name': 'us'}),
            matches=stub('matches', []), read_cells=real.read_cells, answers=real.answers,
            our_submission=real.our_submission)
        for k, mk in over.items():
            setattr(fake, k, mk(calls, d))
        saved = (self.p.contest, self.p.STATE, self.p.SCREENS, self.p.bot_hash, self.p.next_autoscrim, self.p.LOCK)
        self.p.contest, self.p.STATE, self.p.SCREENS, self.p.LOCK = fake, str(st), d, str(Path(d, 'state.lock'))
        self.p.bot_hash = lambda pkg: {'cand': 'a' * 12, 'inc': 'b' * 12}.get(pkg)
        self.p.next_autoscrim = lambda now: None
        self.addCleanup(lambda: setattr(self.p, 'contest', saved[0]) or setattr(self.p, 'STATE', saved[1]) or
                        setattr(self.p, 'SCREENS', saved[2]) or setattr(self.p, 'bot_hash', saved[3]) or
                        setattr(self.p, 'next_autoscrim', saved[4]) or setattr(self.p, 'LOCK', saved[5]))
        return st, calls

    def test_trial_start_refuses_without_screen(self):
        import io, contextlib
        st, calls = self.trial_env()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_start('cand', 'panel.txt', None, True)                  # --force: the window only
        self.assertIn('tools/screen.py cand', str(cm.exception))
        self.assertEqual(calls, [])                                                   # refused before any replica call
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_start('cand', 'panel.txt', None, False, skip_screen='  ')  # a reason is required
        self.assertEqual(calls, [])

    def test_trial_start_with_screen_or_skip(self):
        import io, json, contextlib
        st, calls = self.trial_env(records=['a' * 12])
        with contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_start('cand', 'panel.txt', None, False)
        ev = json.loads(st.read_text())['history'][-1]
        self.assertEqual((ev['event'], ev['screen']), ('trial-start', os.path.relpath(
            os.path.join(self.p.SCREENS, f'cand-{"a" * 12}.json'), self.p.REPO)))
        self.assertIn('submit', calls)
        st, calls = self.trial_env()
        with contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_start('cand', 'panel.txt', None, False, skip_screen='owner asked')
        ev = json.loads(st.read_text())['history'][-1]
        self.assertEqual(ev['screen_skipped'], 'owner asked')
        self.assertNotIn('screen', ev)

    # ------------------------------------------------ parked trials (the queue backlog after an autoscrim)
    @staticmethod
    def panel_file():
        p = Path(tempfile.mkdtemp(), 'panel.txt')
        p.write_text('TeamX m1,m2 +\nTeamY m3 +\n')
        return str(p)

    @staticmethod
    def open_trial(panel, **extra):
        return {'validated': {'submission': 24, 'package': 'inc'}, 'history': [], 'parked': [],
                'trial': dict({'submission': 30, 'package': 'cand', 'panel': panel, 'run_dir': 'gauntlet/x-panel-cand',
                               'pid': 4242, 'hash': 'a' * 12}, **extra)}

    @staticmethod
    def parked(**extra):
        return dict({'submission': 30, 'package': 'cand', 'panel': 'p.txt', 'run_dir': 'gauntlet/x-panel-cand',
                     'pid': 4242, 'hash': 'a' * 12, 'parked': '2026-10-11T03:00:00+00:00', 'run': 'gauntlet/x-panel-cand'},
                    **extra)

    def parked_state(self, *ps, trial=None):
        return {'validated': {'submission': 31, 'package': 'inc', 'panel_run': 'gauntlet/v'}, 'trial': trial,
                'history': [], 'parked': list(ps) or [self.parked()]}

    @staticmethod
    def recorder(name, ret):
        """A trial_env override: a stub that records (name, first argument) and returns ret."""
        def mk(calls, d):
            def f(*a, **k):
                calls.append((name, a[0] if a else k))
                return ret
            return f
        return mk

    def test_panel_created(self):
        M = ContestClientTest.match
        cells = [('TeamX', ['m1'], '+'), ('TeamX', ['m1'], '+'), ('TeamY', ['m3'], '+')]
        ms = [M(5, 'TeamX', ['m1'], 30, 'QUE'), M(4, 'TeamY', ['m3'], 24), M(3, 'TeamX', ['m1'], 30, 'NEW')]
        self.assertEqual(self.p.panel_created(cells, ms, 1, 30), [5, 3, None])   # one match per cell; not 24's

    def test_trial_park_waits_for_every_match_then_resubmits(self):
        import io, json, contextlib
        M = ContestClientTest.match
        phases = [[M(41, 'TeamX', ['m1', 'm2'], 30, 'QUE'), M(40, 'TeamY', ['m3'], 24)],   # the validated build's
                  [M(42, 'TeamY', ['m3'], 30, 'NEW'), M(41, 'TeamX', ['m2', 'm1'], 30, 'QUE'), M(40, 'TeamY', ['m3'], 24)]]

        def matches(calls, d):
            def f(tid, limit_pages=1):
                calls.append('matches')
                return phases.pop(0) if len(phases) > 1 else phases[0]
            return f
        st, calls = self.trial_env(state=self.open_trial(self.panel_file()), matches=matches,
                                   submit=self.recorder('submit', {'id': 31}),
                                   set_auto_accept=self.recorder('auto', None))
        with contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_park(poll=0, timeout=60)
        self.assertEqual(calls, ['me', 'matches', 'matches', ('submit', 'inc'), 'wait',
                                 ('auto', {'ranked': 'A', 'unranked': 'A'})])
        s = json.loads(st.read_text())
        self.assertIsNone(s['trial'])
        self.assertEqual(s['validated']['submission'], 31)                      # the resubmitted validated build
        p, = s['parked']
        self.assertEqual((p['submission'], p['package'], p['run_dir'], p['pid'], p['panel_matches']),
                         (30, 'cand', 'gauntlet/x-panel-cand', 4242, [41, 42]))
        self.assertEqual((s['history'][-1]['event'], s['history'][-1]['submission']), ('park', 30))

    def test_trial_park_refusals(self):
        import io, json, contextlib
        M = ContestClientTest.match
        st, calls = self.trial_env()
        with self.assertRaises(SystemExit):
            self.p.cmd_trial_park(poll=0, timeout=0)                           # no trial
        one = self.recorder('matches', [M(41, 'TeamX', ['m1', 'm2'], 30, 'QUE'), M(40, 'TeamY', ['m3'], 24)])
        st, calls = self.trial_env(state=self.open_trial(self.panel_file()), matches=one)
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_park(poll=0, timeout=0)                           # timed out: the trial stays open
        self.assertIn('1 of 2 panel matches', str(cm.exception))
        s = json.loads(st.read_text())
        self.assertEqual((s['trial']['submission'], s['parked'], s['validated']['submission']), (30, [], 24))
        self.assertNotIn('submit', [c if isinstance(c, str) else c[0] for c in calls])

    def test_trial_start_with_parked_trials_records_the_run_on_the_parked_entry(self):
        """trial-start refuses while a trial is open but not while trials are parked; when its panel ends after the
        trial was parked, the run goes on the parked entry (matched by submission) and in the history."""
        import io, json, contextlib
        st, calls = self.trial_env(records=['a' * 12], state=self.open_trial('p.txt'))
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_start('cand', 'panel.txt', None, False)
        self.assertEqual(calls, [])
        seen = {}

        def block(calls, d):
            def f(panel, tag, run=None, submission=None):   # trial-park runs while the panel plays
                st = Path(d, 'state.json')
                s = json.loads(st.read_text())
                seen.update(trial=dict(s['trial']), run=run, submission=submission)
                s['parked'].append(dict(s['trial'], parked='2026-10-11T03:00:00+00:00'))
                s['trial'] = None
                st.write_text(json.dumps(s))
                return run
            return f
        st, calls = self.trial_env(records=['a' * 12], state=self.parked_state(self.parked(submission=28, run=None)),
                                   block=block, pages=self.recorder('pages', [{'id': 31, 'accepted': True}]))
        with contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_start('cand', 'panel.txt', None, False)
        rel = os.path.relpath(seen['run'], self.p.REPO)
        self.assertEqual((seen['trial']['run_dir'], seen['trial']['pid'], seen['trial']['hash']),
                         (rel, os.getpid(), 'a' * 12))
        self.assertEqual(seen['submission'], 30)                   # the block plays the candidate only
        s = json.loads(st.read_text())
        old, new = s['parked']
        self.assertEqual((old['submission'], old['run']), (28, None))
        self.assertEqual((new['submission'], new['run']), (30, rel))
        self.assertIn('panel_done', new)
        self.assertEqual((s['history'][-1]['event'], s['history'][-1]['run']), ('panel-done', rel))

    def test_trial_decide_reject(self):
        import io, json, contextlib
        st, calls = self.trial_env(state=self.parked_state())
        with contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_decide('cand', False)
        s = json.loads(st.read_text())
        self.assertEqual((s['parked'], s['validated']['submission'], calls), ([], 31, []))
        ev = s['history'][-1]
        self.assertEqual((ev['event'], ev['submission'], ev['parked'], ev['run']), ('reject', 30, True,
                                                                                  'gauntlet/x-panel-cand'))

    def test_trial_decide_accept(self):
        import io, json, contextlib
        other = self.parked(submission=32, package='cand2', run=None)
        st, calls = self.trial_env(state=self.parked_state(self.parked(), other),
                                   submit=self.recorder('submit', {'id': 33}))
        with contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_decide('30', True)                                 # by trial submission id
        s = json.loads(st.read_text())
        self.assertEqual(calls, [('submit', 'cand'), 'wait'])
        v = s['validated']
        self.assertEqual((v['submission'], v['package'], v['panel_run']), (33, 'cand', 'gauntlet/x-panel-cand'))
        self.assertIn('since', v)
        self.assertEqual([p['submission'] for p in s['parked']], [32])         # the other parked trial stays
        ev = s['history'][-1]
        self.assertEqual((ev['event'], ev['submission'], ev['trial_submission']), ('accept', 33, 30))

    def test_trial_decide_refusals(self):
        import io, json, contextlib
        playing = tempfile.mkdtemp()
        cases = [  # (state, key, accept, message)
            (self.parked_state(self.parked(run=None, run_dir=playing)), 'cand', False, 'still playing'),
            (self.parked_state(self.parked(run=None, run_dir=playing)), 'cand', True, 'still playing'),
            (self.parked_state(trial=self.open_trial('p.txt')['trial'] | {'package': 'cand3', 'submission': 34}),
             'cand', True, 'trial is in progress'),
            (self.parked_state(self.parked(hash='c' * 12)), 'cand', True, 'not the code'),
            (self.parked_state(), 'nope', False, 'no parked trial nope'),
            (self.parked_state(self.parked(), self.parked(submission=32)), 'cand', False, '2 parked trials'),
        ]
        for state, key, accept, msg in cases:
            st, calls = self.trial_env(state=state)
            before = st.read_text()
            with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
                self.p.cmd_trial_decide(key, accept)
            self.assertIn(msg, str(cm.exception))
            self.assertEqual((calls, st.read_text()), ([], before))
        # a compile failure keeps the trial parked and the validated build
        st, calls = self.trial_env(state=self.parked_state(),
                                   wait_submission=self.recorder('wait', {'status': 'ERR', 'accepted': False}))
        before = st.read_text()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_decide('cand', True)
        self.assertEqual(st.read_text(), before)
        # a panel resumed by hand (RESUME=<run dir>) is done once results.csv exists in its run directory
        Path(playing, 'results.csv').write_text('opponent\n')
        st, calls = self.trial_env(state=self.parked_state(self.parked(run=None, run_dir=playing)))
        with contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_decide('cand', False)
        self.assertEqual(json.loads(st.read_text())['history'][-1]['run'], playing)

    def test_status_shows_parked(self):
        import io, contextlib
        st, calls = self.trial_env(
            state=self.parked_state(self.parked(), self.parked(submission=32, package='cand2', run=None)),
            me=self.recorder('me', {'id': 1, 'name': 'us', 'profile': {'rating': 1500}}),
            pages=self.recorder('pages', [{'id': 31, 'accepted': True, 'package': 'inc'}]))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.p.cmd_status()
        self.assertIn('parked: cand (submission 30) since 2026-10-10 20:00 PDT: panel done (gauntlet/x-panel-cand)',
                      out.getvalue())
        self.assertIn('parked: cand2 (submission 32) since 2026-10-10 20:00 PDT: panel playing', out.getvalue())

    def test_panel_created_needs_the_submission_field(self):
        """trial-park never parks on a guess: a row without a submission does not count (block's fallback aside)."""
        bare = ContestClientTest.match(5, 'TeamX', ['m1'], 30, 'QUE')
        del bare['participants'][0]['submission']
        self.assertEqual(self.p.panel_created([('TeamX', ['m1'], '+')], [bare], 1, 30), [None])

    def test_trial_park_keeps_the_trial_open_when_the_resubmission_fails(self):
        """The validated build's resubmission does not compile: the candidate stays active, so the trial stays open
        and incoming ranked challenges stay rejected (auto-accept is restored only after the resubmission)."""
        import io, json, contextlib
        M = ContestClientTest.match
        full = self.recorder('matches', [M(42, 'TeamY', ['m3'], 30, 'NEW'), M(41, 'TeamX', ['m1', 'm2'], 30, 'QUE')])
        st, calls = self.trial_env(state=self.open_trial(self.panel_file()), matches=full,
                                   wait_submission=self.recorder('wait', {'status': 'ERR', 'accepted': False}),
                                   set_auto_accept=self.recorder('auto', None))
        before = st.read_text()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_park(poll=0, timeout=60)
        self.assertIn('the trial stays open', str(cm.exception))
        self.assertNotIn('auto', [c[0] for c in calls if isinstance(c, tuple)])
        self.assertEqual(st.read_text(), before)

    def test_trial_park_refuses_when_the_trial_ended_meanwhile(self):
        import io, json, contextlib
        M = ContestClientTest.match
        full = [M(42, 'TeamY', ['m3'], 30, 'NEW'), M(41, 'TeamX', ['m1', 'm2'], 30, 'QUE')]

        def matches(calls, d):
            def f(tid, limit_pages=1):                      # trial-end runs while trial-park polls
                st = Path(d, 'state.json')
                s = json.loads(st.read_text())
                s['trial'] = None
                st.write_text(json.dumps(s))
                return full
            return f
        st, calls = self.trial_env(state=self.open_trial(self.panel_file()), matches=matches)
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_park(poll=0, timeout=60)
        self.assertIn('was ended', str(cm.exception))
        self.assertNotIn('submit', calls)
        self.assertEqual(json.loads(st.read_text())['parked'], [])

    def test_trial_start_records_a_compile_timeout(self):
        """The candidate has not compiled when wait_submission gives up: it may still become active, so the trial is
        recorded (without a panel) for trial-end --reject, and no panel runs."""
        import io, json, contextlib

        def timeout(calls, d):
            def f(sid):
                calls.append('wait')
                raise SystemExit(f'submission {sid} not compiled after 1800s')
            return f
        st, calls = self.trial_env(records=['a' * 12], wait_submission=timeout)
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_start('cand', 'panel.txt', None, False)
        self.assertIn('trial-end --reject', str(cm.exception))
        self.assertNotIn('block', calls)
        s = json.loads(st.read_text())
        self.assertEqual((s['trial']['submission'], s['trial']['compile'], s['history'][-1]['compile']),
                         (30, 'timeout', 'timeout'))

    def test_trial_start_refuses_to_resume_a_block(self):
        """RESUME=<run> with recorded requests: trial-start would submit a new candidate the old requests did not
        play; the block is resumed by hand instead (tools/contest.py block keeps their submission)."""
        import io, contextlib
        from unittest import mock
        st, calls = self.trial_env(records=['a' * 12])
        run = Path(tempfile.mkdtemp())
        (run / 'requests.jsonl').write_text('{}\n')
        with mock.patch.dict(os.environ, {'RESUME': str(run)}), self.assertRaises(SystemExit) as cm, \
                contextlib.redirect_stdout(io.StringIO()):
            self.p.cmd_trial_start('cand', 'panel.txt', None, False)
        self.assertIn('tools/contest.py block', str(cm.exception))
        self.assertEqual(calls, [])

    def test_state_writers_wait_for_the_lock(self):
        """A state writer (here trial-decide) waits while another command holds the state lock, so that neither of two
        overlapping writes is lost."""
        import io, json, contextlib, threading
        st, calls = self.trial_env(state=self.parked_state())
        errs = []

        def decide():
            try:
                self.p.cmd_trial_decide('cand', False)
            except BaseException as e:
                errs.append(e)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            with self.p.state_lock():
                th = threading.Thread(target=decide)
                th.start()
                th.join(0.3)
                self.assertTrue(th.is_alive())                                  # waiting for the lock
                s = json.loads(st.read_text())                                  # the holder's write
                s['history'].append({'event': 'panel-done', 'submission': 28})
                self.p.save_state(s)
            th.join(10)
        self.assertFalse(th.is_alive())
        self.assertEqual(errs, [])
        s = json.loads(st.read_text())
        self.assertEqual((s['parked'], [e['event'] for e in s['history']]), ([], ['panel-done', 'reject']))
        self.assertIn('waiting for the ladder-state lock', out.getvalue())


class ScreenTest(unittest.TestCase):
    """tools/screen.py (docs/ARCHETYPES.md section 5): the bars, the paired roster judgement, the cache, the record,
    the job script and the refusals. Offline: synthetic run directories, no VM."""
    @classmethod
    def setUpClass(cls):
        cls.s = load('screen', TOOLS / 'screen.py')

    CEN_HDR = 'cell_opponent,cell_map,cell_side,cell_seed,map,team,side,won,over,exceptions,deaths_self,sym_wrong,tele,' \
              'tele_exc_turns,counters'

    def mkrun(self, root, name, bot, bh, opp_h, games, seed_mode='map', bad=None):
        """A gauntlet run dir. games: [(opponent, map, bot_side, result)], result win|loss|coin|unknown; bad: {cell
        index: (column, value)} for the bot's census row."""
        d = Path(root, name)
        d.mkdir(parents=True)
        prov = f'bot={bot}\nbot_hash={bh}\ncells=0\n' + (f'seed_mode={seed_mode}\n' if seed_mode else '')
        prov += ''.join(f'opp_hash.{o}={h}\n' for o, h in opp_h.items())
        (d / 'provenance.txt').write_text(prov)
        res = ['opponent,map,bot_side,winner_side,rounds,bot_result,reason,seed']
        cen = [self.CEN_HDR]
        for i, (o, m, side, r) in enumerate(games):
            other = 'B' if side == 'A' else 'A'
            win_side = side if r == 'win' else other if r == 'loss' else ('A' if r == 'coin' else '?')
            reason = 'The winning team won on tiebreakers (coin flip).' if r == 'coin' else 'capturing 75%'
            res.append(f'{o},{m},{side},{win_side},500,{"win" if r == "coin" else r},{reason},map')
            if r == 'unknown':
                continue
            row = {'over': 0, 'exceptions': 0, 'deaths_self': 0, 'sym_wrong': 0}
            if bad and i in bad:
                row[bad[i][0]] = bad[i][1]
            cen.append(f'{o},{m},{side},map,{m},{bot},{side},{int(r == "win")},{row["over"]},{row["exceptions"]},'
                       f'{row["deaths_self"]},{row["sym_wrong"]},both,0,ex=0;nm=0;')
            cen.append(f'{o},{m},{side},map,{m},{o},{other},{int(r != "win")},0,0,0,0,both,0,ex=0;nm=0;')
        (d / 'results.csv').write_text('\n'.join(res) + '\n')
        (d / 'census.csv').write_text('\n'.join(cen) + '\n')
        (d / 'summary.txt').write_text('done\n')
        return str(d)

    # ---------------------------------------------------------------- bars
    def test_h2h_bars(self):
        j = self.s.judge_h2h
        self.assertEqual(self.s.h2h_bars(20), (11, 9))
        self.assertEqual(j(['win'] * 11 + ['loss'] * 9, 20)['verdict'], 'PASS')
        self.assertEqual(j(['win'] * 10 + ['loss'] * 10, 20)['verdict'], 'BORDERLINE')
        self.assertEqual(j(['win'] * 9 + ['loss'] * 11, 20)['verdict'], 'BORDERLINE')
        self.assertEqual(j(['win'] * 8 + ['loss'] * 12, 20)['verdict'], 'FAIL')
        d = j(['win'] * 10 + ['coin'] * 2 + ['loss'] * 8, 20)                     # a coin game scores 0.5
        self.assertEqual((d['score'], d['verdict']), (11.0, 'PASS'))
        self.assertEqual(j(['win'] * 10 + ['unknown'] + ['loss'] * 9, 20)['verdict'], 'INCOMPLETE')
        self.assertEqual(j(['win'] * 5 + ['unknown'] * 2 + ['loss'] * 13, 20)['verdict'], 'FAIL')  # holds either way
        self.assertEqual(j(['win'] * 12 + ['missing'] + ['loss'] * 7, 20)['verdict'], 'PASS')

    def test_basics_bars(self):
        jb = self.s.judge_basics
        zero = {'over': 0, 'exceptions': 0, 'deaths_self': 0, 'sym_wrong': 0, 'near': 3}
        self.assertEqual(jb(['win'] * 8, zero, 8)['verdict'], 'PASS')
        self.assertEqual(jb(['win'] * 7 + ['unknown'], zero, 8)['verdict'], 'INCOMPLETE')
        d = jb(['win'] * 7 + ['loss'], zero, 8)
        self.assertEqual(d['verdict'], 'FAIL')
        self.assertIn('1 of 8 games not won', d['failed'])
        for k in ('over', 'exceptions', 'deaths_self', 'sym_wrong'):
            self.assertEqual(jb(['win'] * 8, dict(zero, **{k: 1}), 8)['verdict'], 'FAIL', k)
        self.assertEqual(jb(['win'] * 8, dict(zero, near=50), 8)['verdict'], 'PASS')   # near misses never gate

    def test_game_basics(self):
        gb = self.s.game_basics
        b = gb({'over': '2', 'exceptions': '1', 'deaths_self': '1', 'sym_wrong': '0', 'tele': 'both',
                'counters': 'ex=3;nm=4;'})
        self.assertEqual((b['over'], b['exceptions'], b['near'], b['strings']), (2, 4, 4, True))  # uncaught + caught
        b = gb({'over': '0', 'exceptions': '0', 'tele': 'bcc', 'tele_exc_turns': '5', 'counters': '', 'sym_wrong': '9'})
        self.assertEqual((b['exceptions'], b['sym_wrong']), (5, 0))     # bytecode channel; symmetry n/a without strings

    def test_regression_rule(self):
        r = self.s.regression_verdict
        self.assertEqual(r(0, 3, 0, -3), 'ok')            # net -3 but within 2 SE (2 sqrt 3 = 3.46)
        self.assertEqual(r(0, 4, 0, -3), 'REGRESSION')    # net -4 = -2 sqrt 4
        self.assertEqual(r(1, 5, 0, -3), 'ok')            # net -4 > -2 sqrt 6
        self.assertEqual(r(0, 2, 0, -3), 'ok')            # 2 SE but under 3 games
        self.assertEqual(r(0, 3, 1, -3), 'incomplete')    # the missing pair, lost, would make it a regression
        self.assertEqual(r(5, 0, 1, -3), 'ok')
        self.assertEqual(r(0, 4, 0, -4), 'REGRESSION')    # pooled bar
        self.assertEqual(r(0, 3, 0, -4), 'ok')

    def test_pairs_and_censoring(self):
        c = self.s.pair_counts([('win', 'loss'), ('loss', 'win'), ('win', 'win'), ('loss', 'loss'), ('coin', 'win'),
                                ('win', 'unknown'), ('win', 'missing')])
        self.assertEqual((c['g'], c['l'], c['both_won'], c['both_lost'], c['coin'], c['missing']), (1, 1, 1, 1, 1, 2))
        self.assertEqual((c['candidate_wins'], c['incumbent_wins']), (4, 3))
        # calibrate's local share is candidate_wins / candidate_decided (4/6), not / (cells - coin - missing) (4/4)
        self.assertEqual(c['candidate_decided'], 6)
        self.assertEqual(self.s.censoring(self.s.pair_counts([('win', 'loss'), ('loss', 'loss')])), 'censored-low')
        self.assertEqual(self.s.censoring(self.s.pair_counts([('win', 'win'), ('loss', 'win')])), 'censored-high')
        self.assertIsNone(self.s.censoring(self.s.pair_counts([('win', 'win'), ('loss', 'loss')])))

    def roster_stage(self, *archs):
        return self.s.judge_roster([{'name': n, 'gating': g, 'pairs': p} for n, g, p in archs])

    def test_roster_and_overall(self):
        W, L_ = ('win', 'loss'), ('loss', 'win')
        same = [('win', 'win')] * 10 + [('loss', 'loss')] * 10
        ok_a = {'verdict': 'PASS'}
        h2h = lambda v, s=11.0: {'verdict': v, 'score': s, 'games': 20, 'borderline_at': 9}
        d_ok = {'verdict': 'PASS'}
        c = self.roster_stage(('x', True, [L_] * 4 + same[:16]))
        self.assertEqual((c['verdict'], c['archetypes'][0]['verdict']), ('FAIL', 'REGRESSION'))
        c = self.roster_stage(('x', False, [L_] * 4 + same[:16]))           # information only: never fails
        self.assertEqual((c['verdict'], c['archetypes'][0]['verdict']), ('PASS', 'REGRESSION'))
        self.assertEqual(c['info_pooled']['net'], -4)
        c = self.roster_stage(('x', True, [L_] * 2 + same[:18]), ('y', True, [L_] * 2 + same[:18]))
        self.assertEqual((c['verdict'], c['pooled']['net']), ('FAIL', -4))  # pooled: -4 = -2 sqrt 4
        self.assertEqual([e['verdict'] for e in c['archetypes']], ['ok', 'ok'])
        gain = self.roster_stage(('x', True, [W] * 2 + same[:18]))
        self.assertEqual(self.s.overall({'a': ok_a, 'b': h2h('PASS'), 'c': gain, 'd': d_ok})[0], 'PASS')
        self.assertEqual(self.s.overall({'a': ok_a, 'b': h2h('BORDERLINE', 10.0), 'c': gain, 'd': d_ok})[0], 'PASS')
        one = self.roster_stage(('x', True, [W] + same[:19]))
        v, why = self.s.overall({'a': ok_a, 'b': h2h('BORDERLINE', 10.0), 'c': one, 'd': d_ok})
        self.assertEqual(v, 'FAIL')
        self.assertIn('without a pooled roster gain', why[0])
        empty = self.roster_stage()
        self.assertEqual(empty['verdict'], 'PASS')
        self.assertIn('note', empty)
        self.assertEqual(self.s.overall({'a': ok_a, 'b': h2h('BORDERLINE', 10.0), 'c': empty, 'd': d_ok})[0], 'FAIL')
        self.assertEqual(self.s.overall({'a': ok_a, 'b': h2h('PASS'), 'c': empty, 'd': d_ok})[0], 'PASS')
        self.assertEqual(self.s.overall({'a': {'verdict': 'FAIL', 'failed': ['over = 1']}})[0], 'FAIL')
        self.assertEqual(self.s.overall({'a': ok_a, 'b': h2h('INCOMPLETE'), 'c': gain, 'd': d_ok})[0], 'INCOMPLETE')
        self.assertEqual(self.s.overall({'a': ok_a, 'b': h2h('PASS'), 'c': gain, 'd': {'verdict': 'FAIL'}})[0], 'FAIL')

    # ---------------------------------------------------------------- cache
    def test_cache_rows_and_keys(self):
        root = tempfile.mkdtemp()
        ch, ah = '1' * 12, '2' * 12
        run = self.mkrun(root, 'r1', 'cand', ch, {'arch_x': ah},
                         [('arch_x', 'Maze', 'A', 'win'), ('arch_x', 'Maze', 'B', 'loss'), ('arch_x', 'Cat', 'A', 'coin'),
                          ('arch_x', 'Cat', 'B', 'unknown')])
        rows, why = self.s.run_cache_rows(run)
        self.assertIsNone(why)
        self.assertEqual(len(rows), 4)                         # 2 decided games x both teams; coin, unknown never
        self.assertEqual(rows[0]['seed'], 'map')
        keys = {self.s.cache_key(r): r['result'] for r in rows}
        self.assertEqual(keys[(ch, ah, 'Maze', 'A', 'map')], 'win')
        self.assertEqual(keys[(ah, ch, 'Maze', 'B', 'map')], 'loss')   # the same game from the archetype's side
        self.assertEqual(keys[(ch, ah, 'Maze', 'B', 'map')], 'loss')
        self.assertEqual(list(rows[0]), self.s.CACHE_HDR)
        self.assertNotIn('cand', {k[0] for k in keys})          # keyed by code hash, never by package name
        for sm in (None, 'random'):
            r = self.mkrun(root, f'r-{sm}', 'cand', ch, {'arch_x': ah}, [('arch_x', 'Maze', 'A', 'win')], seed_mode=sm)
            self.assertEqual(self.s.run_cache_rows(r)[0], [])
        r = self.mkrun(root, 'r-nohash', 'cand', ch, {}, [('arch_x', 'Maze', 'A', 'win')])
        self.assertEqual(self.s.run_cache_rows(r)[0], [])       # the opponent's code is unknown

    def test_cache_ingest_and_determinism(self):
        import io, contextlib
        root = tempfile.mkdtemp()
        cache = os.path.join(root, 'cache.csv')
        ch, ah = '1' * 12, '2' * 12
        r1 = self.mkrun(root, 'r1', 'cand', ch, {'arch_x': ah}, [('arch_x', 'Maze', 'A', 'win')])
        r2 = self.mkrun(root, 'r2', 'renamed', ch, {'arch_x': ah}, [('arch_x', 'Maze', 'A', 'win')])
        new, _, conf = self.s.ingest([r1, r2], path=cache)
        self.assertEqual((len(new), conf), (4, {}))
        self.assertEqual(len(self.s.ingest([r1], path=cache)[0]), 0)                   # idempotent per run
        idx, _ = self.s.load_cache(cache)
        self.assertEqual(idx[(ch, ah, 'Maze', 'A', 'map')]['result'], 'win')
        r3 = self.mkrun(root, 'r3', 'cand', ch, {'arch_x': ah}, [('arch_x', 'Maze', 'A', 'loss')])
        with contextlib.redirect_stderr(io.StringIO()) as err:
            _, _, conf = self.s.ingest([r3], path=cache)
        self.assertIn((ch, ah, 'Maze', 'A', 'map'), conf)                              # a determinism failure
        self.assertIn('determinism failure', err.getvalue())
        idx, _ = self.s.load_cache(cache)
        self.assertNotIn((ch, ah, 'Maze', 'A', 'map'), idx)                            # never used

    # ---------------------------------------------------------------- roster, job, judge, record
    def test_roster_file(self):
        p = self.s.parse_roster_file
        pk = ['arch_a', 'arch_b', 'arch_c']
        self.assertEqual(p(None, pk), [('arch_a', 'auto'), ('arch_b', 'auto'), ('arch_c', 'auto')])  # absent = '*'
        self.assertEqual(p('# c\narch_b gate\n* info\narch_c off\nc_line6\n', pk),
                         [('arch_b', 'gate'), ('c_line6', 'auto'), ('arch_a', 'info')])
        self.assertEqual(p('arch_a\n', pk), [('arch_a', 'auto')])                   # no '*': only the named
        with self.assertRaises(ValueError):
            p('arch_a sometimes\n', pk)
        g = self.s.gating_of
        self.assertEqual([g('auto', True, None)[0], g('auto', False, None)[0], g('gate', False, None)[0],
                          g('info', True, None)[0], g('auto', True, False)[0]], [True, False, True, False, False])

    def state(self, roster, maps=('Maze', 'Cat')):
        return {'candidate': 'cand', 'candidate_hash': '1' * 12, 'incumbent': 'inc', 'incumbent_hash': '3' * 12,
                'example_hash': '4' * 12, 'identity': False, 'maps': list(maps), 'basics_maps': ['SmallElements'],
                'reduced': True, 'roster': roster, 'roster_source': 'test', 'excluded': [], 'tag': 'scr-111-abcd',
                'created': '2026-10-08T00:00:00+00:00', 'job': 'j'}

    def test_job_script(self):
        st = self.state([{'name': 'arch_x', 'hash': '2' * 12, 'mode': 'auto', 'gating': False, 'why': '',
                          'inc_cached': [['arch_x', 'Maze', 'A', 'map']]}])
        js = self.s.build_job(st)
        self.assertIn('MAXJOBS=2 CENSUS=1 SEED_MODE=map', js)
        self.assertIn('examplefuncsplayer SmallElements B map\n', js)
        self.assertIn('inc Cat B map\n', js)
        self.assertIn('|| end stop-a', js)
        self.assertIn('|| end stop-b', js)
        self.assertIn('HASHES=1 bash tools/build.sh arch_x || {', js)     # an archetype that fails is excluded
        self.assertIn('SKIP_COMPILE=1', js)
        self.assertRegex(js, r"cached-arch_x.txt\" <<'EOF_CELLS'\narch_x Maze A map\nEOF_CELLS")
        self.assertIn('BOT=inc TAG=scr-111-abcd-inc', js)
        self.assertLess(js.index('-inc CELLS'), js.index('-c CELLS'))      # the incumbent's cells first
        self.assertIn('rm -rf "$1/replays"', js)
        self.assertNotIn('end stop-a', self.s.build_job(dict(st, no_stop=True)))
        r = subprocess.run(['bash', '-n'], input=js, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def judge_fixture(self, inc_results, cand_results, h2h, identity=False):
        """Runs a, b, inc, c for maps Maze and Cat, one archetype arch_x (gating), and a cache with the inc run."""
        root = tempfile.mkdtemp()
        ch, ah, ih, eh = '1' * 12, '2' * 12, ('1' * 12 if identity else '3' * 12), '4' * 12
        cells = [('Maze', 'A'), ('Maze', 'B'), ('Cat', 'A'), ('Cat', 'B')]
        runs = {
            'a': self.mkrun(root, 'a', 'cand', ch, {'examplefuncsplayer': eh},
                            [('examplefuncsplayer', 'SmallElements', s, 'win') for s in 'AB']),
            'b': self.mkrun(root, 'b', 'cand', ch, {'inc': ih}, [('inc', m, s, r) for (m, s), r in zip(cells, h2h)]),
            'inc': self.mkrun(root, 'inc', 'inc', ih, {'arch_x': ah},
                              [('arch_x', m, s, r) for (m, s), r in zip(cells, inc_results)]),
            'c': self.mkrun(root, 'c', 'cand', ch, {'arch_x': ah},
                            [('arch_x', m, s, r) for (m, s), r in zip(cells, cand_results)])}
        cache = os.path.join(root, 'cache.csv')
        self.s.ingest(list(runs.values()), path=cache)
        st = self.state([{'name': 'arch_x', 'hash': ah, 'mode': 'gate', 'gating': True, 'why': 'test'}])
        st.update({'incumbent_hash': ih, 'identity': identity})
        stages, verdict, reasons = self.s.judge(st, runs, {'end': 'done', 'excluded': {}, 'changed': {}}, cache)
        return st, stages, verdict, reasons

    def test_judge_end_to_end(self):
        st, stages, verdict, reasons = self.judge_fixture(['win', 'win', 'loss', 'win'], ['loss', 'win', 'win', 'win'],
                                                          ['win', 'win', 'win', 'loss'])
        self.assertEqual(stages['a']['verdict'], 'PASS')
        self.assertEqual((stages['b']['score'], stages['b']['verdict']), (3.0, 'PASS'))     # n = 4: PASS at 3
        e = stages['c']['archetypes'][0]
        self.assertEqual((e['g'], e['l'], e['both_won'], e['incumbent_wins'], e['candidate_wins']), (1, 1, 2, 3, 3))
        self.assertEqual(stages['d']['games'], 2 + 4 + 4)
        self.assertEqual(verdict, 'PASS')
        rec = self.s.make_record(st, stages, verdict, reasons)
        for k in ('v', 'candidate', 'candidate_hash', 'incumbent', 'incumbent_hash', 'created', 'finished', 'job',
                  'seed_mode', 'maps', 'stages', 'verdict', 'reasons', 'reduced'):
            self.assertIn(k, rec)
        self.assertEqual(set(rec['stages']), {'a', 'b', 'c', 'd'})
        for k in ('name', 'hash', 'incumbent_wins', 'candidate_wins', 'g', 'l', 'both_won', 'both_lost', 'coin',
                  'censored', 'verdict', 'gating'):
            self.assertIn(k, e)
        lp = load('ladder_policy', TOOLS / 'ladder_policy.py')               # the reader agrees with the writer
        d = tempfile.mkdtemp()
        import json
        Path(d, 'cand-' + '1' * 12 + '.json').write_text(json.dumps(dict(rec, reduced=False)))
        self.assertTrue(lp.screen_check(d, '1' * 12, '3' * 12)[0])
        Path(d, 'cand-' + '1' * 12 + '.json').write_text(json.dumps(rec))  # this one is reduced
        self.assertFalse(lp.screen_check(d, '1' * 12, '3' * 12)[0])

    def test_judge_regression_and_provenance(self):
        _, stages, verdict, _ = self.judge_fixture(['win'] * 4, ['loss'] * 4, ['win'] * 4)
        self.assertEqual((stages['c']['archetypes'][0]['verdict'], verdict), ('REGRESSION', 'FAIL'))
        self.assertEqual(stages['c']['archetypes'][0]['censored'], 'censored-high')
        st, stages, verdict, _ = self.judge_fixture(['win'] * 4, ['win'] * 4, ['win'] * 4)
        st['candidate_hash'] = '9' * 12                                           # the VM played other code
        root = tempfile.mkdtemp()
        a = self.mkrun(root, 'a', 'cand', '1' * 12, {'examplefuncsplayer': '4' * 12},
                       [('examplefuncsplayer', 'SmallElements', s, 'win') for s in 'AB'])
        stages, verdict, reasons = self.s.judge(st, {'a': a}, {'end': 'stop-a', 'excluded': {}, 'changed': {}},
                                                os.path.join(root, 'c.csv'))
        self.assertEqual((stages['a']['verdict'], verdict), ('INCOMPLETE', 'INCOMPLETE'))
        self.assertIn('provenance', stages['a']['why'])

    def test_identity_control(self):
        """A byte-identical incumbent: every map a side split (s = n/2) and 0 discordant pairs -> BORDERLINE, Net 0,
        FAIL, and the record says the control holds."""
        st, stages, verdict, reasons = self.judge_fixture(['win', 'loss', 'win', 'loss'], ['win', 'loss', 'win', 'loss'],
                                                          ['win', 'loss', 'loss', 'win'], identity=True)
        self.assertEqual((stages['b']['verdict'], stages['c']['pooled']['net'], verdict), ('BORDERLINE', 0, 'FAIL'))
        self.assertEqual(self.s.make_record(st, stages, verdict, reasons)['identity_control'], 'ok')

    def test_refusals(self):
        import argparse, io, contextlib
        ns = lambda **k: argparse.Namespace(**dict(dict(incumbent='g_iter0', maps=None, roster='none', rerun=False,
                                                         allow_identity=False, keep_replays=False, min_disk_gb=0,
                                                         print_job=True), **k))
        for bad in ('collect', 'gate', 'no_such_package_x', 'Bad-Name'):
            with self.assertRaises(self.s.Refused):
                self.s.prepare(ns(candidate=bad))
        with self.assertRaises(self.s.Refused):
            self.s.prepare(ns(candidate='g_iter0'))                                   # the incumbent itself
        with self.assertRaises(self.s.Refused):
            self.s.prepare(ns(candidate='c_line6', maps='Maze,NoSuchMap'))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.s.main(['collect', 'no_such_package_x']), 2)
        # a finished record for the same candidate and incumbent hashes is printed instead of a new screen
        import json
        saved = self.s.SCREENS
        self.s.SCREENS = tempfile.mkdtemp()
        try:
            ch, ih = self.s.bot_hash('c_line6'), self.s.bot_hash('g_iter0')
            st = self.state([])
            st.update({'candidate': 'c_line6', 'candidate_hash': ch, 'incumbent': 'g_iter0', 'incumbent_hash': ih,
                       'reduced': False})
            rec = self.s.make_record(st, {}, 'FAIL', ['x'])
            Path(self.s.SCREENS, f'c_line6-{ch}.json').write_text(json.dumps(rec))
            with self.assertRaises(self.s.Refused) as cm:
                self.s.prepare(ns(candidate='c_line6', roster=None))        # the full roster: a full record
            self.assertIn('a finished record exists', str(cm.exception))
        finally:
            self.s.SCREENS = saved
        # a map subset or a roster override (which could drop a gating archetype) never writes an admitting record
        P = list(self.s.PANEL_MAPS)
        self.assertFalse(self.s.is_reduced(P, None))
        self.assertTrue(self.s.is_reduced(P[:2], None))
        self.assertTrue(self.s.is_reduced(P, 'none'))
        self.assertTrue(self.s.is_reduced(P, 'arch_blob'))

    def test_calibration_pieces(self):
        root = tempfile.mkdtemp()
        hdr = 'opponent,map,bot_side,winner_side,rounds,bot_result,reason,seed\n'
        Path(root, 'c').mkdir()
        Path(root, 'i').mkdir()
        Path(root, 'c', 'results.csv').write_text(hdr + 'm1,Cat,A,A,9,win,x,map\nm1,Cat,B,A,9,loss,x,map-rev\n'
                                                  'm2,Cat,A,A,9,win,x,map\nother,Cat,A,A,9,win,x,map\n')
        Path(root, 'i', 'results.csv').write_text(hdr + 'm1,Cat,A,B,9,loss,x,map\nm1,Cat,B,A,9,loss,x,map-rev\n'
                                                  'm2,Cat,A,A,9,win,x,map\nother,Cat,A,B,9,loss,x,map\n')
        g, l, wins, dec = self.s.panel_pairs(str(Path(root, 'c')), str(Path(root, 'i')), {'m1', 'm2'})
        self.assertEqual((g, l, wins, dec), (1, 0, 2, 3))
        row = lambda lg, ll, ls, rg, rl, rs: {'local_g': str(lg), 'local_l': str(ll), 'local_share': ls,
                                              'replica_g': str(rg), 'replica_l': str(rl), 'replica_share': rs}
        opp = row(3, 0, '0.5', 0, 2, '0.4')
        self.assertFalse(self.s.suspect(None, opp))                    # one trial with opposite signs: not yet
        self.assertTrue(self.s.suspect(opp, opp))                      # two consecutive
        self.assertTrue(self.s.suspect(None, row(0, 0, '0.9', 0, 0, '0.5')))   # share gap > 0.30
        self.assertFalse(self.s.suspect(opp, row(1, 0, '0.5', 0, 1, '0.45')))  # |net| < 2

    def test_reserved_and_markers(self):
        self.assertEqual(set(self.s.VERBS), {'collect', 'show', 'roster', 'gate', 'ingest', 'calibrate'})
        m = self.s.job_markers('x\nSCREEN-EXCLUDE arch_b compile-failed\nSCREEN-CHANGED arch_c expected 1 compiled 2\n'
                               'SCREEN-END done\n')
        self.assertEqual((m['end'], m['excluded'], m['changed']), ('done', {'arch_b': 'compile-failed'}, {'arch_c': '2'}))

    def test_gate_cli(self):
        root = tempfile.mkdtemp()
        ok = self.mkrun(root, 'ok', 'cand', '1' * 12, {}, [('examplefuncsplayer', 'Cat', s, 'win') for s in 'AB'])
        over = self.mkrun(root, 'over', 'cand', '1' * 12, {}, [('examplefuncsplayer', 'Cat', s, 'win') for s in 'AB'],
                          bad={1: ('over', 3)})
        b = self.mkrun(root, 'b', 'cand', '1' * 12, {}, [('inc', m, s, 'loss') for m in ('Cat', 'Maze') for s in 'AB'])
        bl = self.mkrun(root, 'bl', 'cand', '1' * 12, {}, [('inc', m, s, r) for m, r in (('Cat', 'win'), ('Maze', 'loss'))
                                                         for s in 'AB'])
        run = lambda *a: subprocess.run([sys.executable, str(TOOLS / 'screen.py'), 'gate', *a], capture_output=True,
                                        text=True).returncode
        self.assertEqual(run('a', '--run', ok), 0)
        self.assertEqual(run('a', '--run', over), 1)
        self.assertEqual(run('b', '--run', b), 1)                    # s = 0 of 4 < n/2 - 1: stop
        self.assertEqual(run('b', '--run', bl), 0)                   # BORDERLINE goes on to the roster


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


# ---------------------------------------------------------------- TELEMETRY.md part B (ReplayDump extraction)
FIX_MIRROR = REPO / 'test/fixtures/example-mirror-maptestsmall.bc23'
FIX_TWO = REPO / 'test/fixtures/two-games.bc23'
# bot (TELEMETRY.md part A, PADK 14) vs examplefuncsplayer, maptestsmall, GAME_SEED=1, indicators on; A wins r330
FIX_SELF = REPO / 'test/fixtures/telemetry-selfplay.bc23'
# part A's fixtures (A.10 item 8): the same cell with indicators on, and with -Dbc.engine.show-indicators=false
FIX_TELE = REPO / 'test/fixtures/tele-example-maptestsmall.bc23'
FIX_TELE_OFF = REPO / 'test/fixtures/tele-example-maptestsmall-indoff.bc23'


def dump(fix, *args, cache=True, timeout=900):
    """tools/replay-dump.sh output, cached under build/test-cache by the hash of the reader's source and the fixture."""
    import hashlib
    if not cache:
        return subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), *([str(fix)] if fix else []), *args],
                              capture_output=True, text=True, timeout=timeout).stdout
    h = hashlib.sha1((TOOLS / 'replaydump/ReplayDump.java').read_bytes() + (Path(fix).read_bytes() if fix else b'')).hexdigest()[:12]
    d = REPO / 'build' / 'test-cache' / h
    d.mkdir(parents=True, exist_ok=True)
    f = d / ('b-' + (Path(fix).stem if fix else 'none') + ''.join(args).replace('-', '_').replace('/', '_') + '.txt')
    if f.exists():
        return f.read_text()
    out = dump(fix, *args, cache=False, timeout=timeout)
    if out.strip():
        f.write_text(out)
    return out


def read_csv(path):
    import csv
    with open(path) as fh:
        return list(csv.DictReader(fh))


def extract(fix, outdir, *args):
    r = subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), str(fix), '--extract', str(outdir), *args],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return r.stdout


def events_model(events_text, map_text):
    """An independent reimplementation of TELEMETRY.md B.2 hit attribution and death causes over `--events` output,
    with the design's count rule (the last hit is lethal when a dead victim took more hits than damage entries; the
    others pair with damage entries in order; unpaired entries are end-of-round damage). The Java reader pairs a hit
    with the damage entry right before it instead. Returns {side: {key: value}}."""
    import re
    rows = map_text.splitlines()[1:]
    hq = {'A': [], 'B': []}
    for i, line in enumerate(rows):
        y = len(rows) - 1 - i
        for x, ch in enumerate(line):
            if ch == 'H':
                hq['A'].append((x, y))
            elif ch == 'h':
                hq['B'].append((x, y))
    maxhp = {'CARRIER': 150, 'LAUNCHER': 200, 'AMPLIFIER': 120, 'DESTABILIZER': 300, 'BOOSTER': 400}
    other = {'A': 'B', 'B': 'A'}
    rob = {}
    out = {s: {k: 0 for k in ('launcher', 'throw', 'hq_aura', 'self', 'dmg_hits', 'kills_hits', 'dmg_aura', 'kills_aura')}
           for s in 'AB'}

    def near_hq(side, p, r2=9):
        return any((p[0] - h[0]) ** 2 + (p[1] - h[1]) ** 2 <= r2 for h in hq[other[side]])

    def hqs_in_reach2(side, p):
        return sum(1 for h in hq[other[side]]
                   if max(abs(p[0] - h[0]) - 2, 0) ** 2 + max(abs(p[1] - h[1]) - 2, 0) ** 2 <= 9)

    pat = re.compile(r'^r(\d+)\s+(\w+) (.*)$')
    by_round = {}
    for line in events_text.splitlines():
        m = pat.match(line)
        if m:
            by_round.setdefault(int(m.group(1)), []).append((m.group(2), m.group(3)))
    for rn in sorted(by_round):
        hits, negs, died, pre = {}, {}, [], {}
        for kind, rest in by_round[rn]:
            f = rest.split()
            if kind == 'spawn':
                rid = int(f[1].split('#')[1])
                x, y = map(int, f[3].split(','))
                rob[rid] = {'side': f[0], 'type': f[1].split('#')[0], 'pos': (x, y), 'hp': maxhp.get(f[1].split('#')[0], 1)}
            elif kind == 'act':
                rid, act, tgt = int(f[1].split('#')[1]), f[2], int(f[3])
                if act in ('LAUNCH_ATTACK', 'THROW_ATTACK') and tgt >= 0:
                    hits.setdefault(tgt, []).append((f[0], 'launcher' if act == 'LAUNCH_ATTACK' else 'throw'))
                elif act == 'CHANGE_HEALTH' and rid in rob:
                    rob[rid]['hp'] += tgt
                    if tgt < 0:
                        negs.setdefault(rid, []).append(-tgt)
            elif kind == 'move':
                rid = int(f[1].split('#')[1])
                if rid in rob:
                    pre[rid] = rob[rid]['pos']
                    rob[rid]['pos'] = tuple(map(int, f[4].split(',')))
            elif kind == 'died':
                rid = int(f[1].split('#')[1])
                died.append((rid, f[0], tuple(map(int, f[3].split(','))), int(f[4].split('=')[1])))
        dead = {d[0] for d in died}
        for v in set(hits) | set(negs):
            h, n = hits.get(v, []), negs.get(v, [])
            if v in dead and len(h) > len(n):
                paired, eor = n[:len(h) - 1], n[len(h) - 1:]
            else:
                paired, eor = n[:len(h)], n[len(h):]
            for (side, _), amt in zip(h, paired):
                out[side]['dmg_hits'] += amt
            if v in rob and v not in dead:
                side = rob[v]['side']
                p0, p1 = pre.get(v, rob[v]['pos']), rob[v]['pos']
                for amt in eor:
                    if near_hq(side, p0) or near_hq(side, p1):
                        out[other[side]]['dmg_aura'] += amt
            elif v in rob:
                side = rob[v]['side']
                for amt in eor:
                    if near_hq(side, rob[v]['pos']):
                        out[other[side]]['dmg_aura'] += amt
        for rid, side, pos, hp in died:
            h, n = hits.get(rid, []), negs.get(rid, [])
            if len(h) > len(n):
                cause = h[-1][1]
                out[h[-1][0]]['dmg_hits'] += hp
                out[h[-1][0]]['kills_hits'] += 1
            elif near_hq(side, pos) or (0 < hp <= 4 * hqs_in_reach2(side, pos)):
                cause = 'hq_aura'
                out[other[side]]['dmg_aura'] += hp
                out[other[side]]['kills_aura'] += 1
            else:
                cause = 'self'
            out[side][cause] += 1
    return out


class ReplayExtractLegacyTest(unittest.TestCase):
    """B.7 item 1: the existing modes are byte-identical to the reader before part B (hashes of its outputs on
    2026-10-08, source sha1 of tools/replaydump/ReplayDump.java before the change), and the census only grows."""
    LEGACY = {  # (fixture, args) -> sha1 of the output
        ('M', ()): '8a3071ba06b5d0ed25db40f9f85effe32a8b8913', ('M', ('--bytecode',)): '5fad107e9327d8ec24dbe64e8af2ed3bfbb4753c',
        ('M', ('--games',)): 'e2dbbf109d4bdded73b0a21268ef54580e8376dc', ('T', ()): '2d67e8b40261dafce2f5d900b78566599452fa32',
        ('T', ('--bytecode',)): '31c3b41cb17580f4c8ed2f4dbfa65e22807fb675', ('T', ('--games',)): '3072d677138f2388163ceec03a17b7d9d66f8377',
        ('T', ('--game', '1')): '099411ff811f2e8d35568dc3dd79a6f92d61d5de',
        ('T', ('--game', '1', '--bytecode')): '72512430c2e322f595ee792b50761048dd7ad026'}
    LEGACY_CENSUS = {('M', ()): 'cb654e05ef363fd28b2af7867ced093a9ba23450', ('T', ()): 'c0db421ae17bad6f5ce961d42dadde4e39fcb699',
                     ('T', ('--game', '1')): '96735b6e87468512adaede88c0ec8528fd03343b'}
    OLD_HEADER_SHA1, OLD_COLS = '0121035532342219b3864b11dfc397bbc8fa53f5', 73
    FIX = {'M': FIX_MIRROR, 'T': FIX_TWO}

    def sha(self, text):
        import hashlib
        return hashlib.sha1(text.encode()).hexdigest()

    def test_existing_modes_unchanged(self):
        for (f, args), want in self.LEGACY.items():
            self.assertEqual(self.sha(dump(self.FIX[f], *args)), want, (f, args))

    def test_census_legacy_columns_unchanged_and_appended(self):
        for (f, args), want in self.LEGACY_CENSUS.items():
            lines = dump(self.FIX[f], *args, '--census').splitlines()
            hdr = lines[0].split(',')
            self.assertEqual(self.sha(','.join(hdr[:self.OLD_COLS]) + '\n'), self.OLD_HEADER_SHA1)
            for row in lines[1:]:
                self.assertEqual(len(row.split(',')), len(hdr), row[:80])
            legacy = '\n'.join(','.join(line.split(',')[:self.OLD_COLS]) for line in lines) + '\n'
            self.assertEqual(self.sha(legacy), want, (f, args))
        full = dump(None, '--census-header').strip()
        self.assertEqual(full, dump(FIX_MIRROR, '--census').splitlines()[0])
        columns = full.split(',')
        historical_extension = (ReplayExtractTest.T1 + ',' + ReplayExtractTest.T2).split(',')
        historical_end = self.OLD_COLS + len(historical_extension)
        self.assertEqual(columns[self.OLD_COLS:historical_end], historical_extension)
        self.assertEqual(columns[historical_end:],
                         ('miss_rate,shot_visible,shot_outside_vision,shot_visibility_unknown,'
                          'outside_vision_rate_lower,outside_vision_rate_upper,outside_vision_hits,outside_vision_misses,'
                          'unknown_visibility_hits,unknown_visibility_misses').split(','))


class ReplayExtractTest(unittest.TestCase):
    """B.7 items 2-5 and 7: --extract, identities, golden vectors, fingerprints, speed. Pinned values were
    cross-checked by independent computations: events_model() (a Python reimplementation over --events), --metrics
    (the legacy snapshot path) and the engine's verdicts (two-games: conquest r339 and r188; mirror: A 420 Mn vs 17)."""
    T1 = ('win_reason,tele,tele_offset,tele_agree,tele_exc_turns,tstates_C,tstates_L,tstates_HQ,tstates_A,tele_carrier_mn,'
          'tele_L_out,deaths_launcher,deaths_throw,deaths_destab,deaths_aura,deaths_self,deaths_resign,value_lost,cargo_lost_Ad,'
          'cargo_lost_Mn,anchors_lost,spawn_kills,dmg_hits,kills_hits,dmg_aura,kills_aura,eng_n,eng_won,eng_lost,eng_n_par,'
          'eng_won_par,eng_n_ahead,eng_won_ahead,eng_n_behind,eng_won_behind,exch_ratio,first_hit_rate,turn_round,lock_round,'
          'onset_L,onset_Mn,onset_value,onset_islands,idle_funds')
    T2 = ('kite_stand_fire,kite_fire_retreat,kite_stepin_fire,kite_fire_ambiguous,kite_advance,kite_retreat,kite_hold,'
          'exposed_end,alone20,group_p50,trip_cycle_p50,partial_loads,carriers_per_well,blind_rate,focus,kill_conv,first_builds')
    HEADERS = {   # TELEMETRY.md B.4, verbatim
        'games.csv': 'match,game,map,width,height,symmetry,islands,rounds,side,team,won,win_reason,tb_margin,vtb500,vtb1000,'
                     'vtb1500,tele,tele_offset,tele_sync_n,tele_sync,tele_agree_n,tele_agree,tele_valid,tele_invalid,'
                     'tele_exc_turns,tele_dots,tele_unknown_kinds',
        'deaths.csv': 'match,game,round,id,side,type,age,x,y,prog,cause,killer_id,killer_type,hp_before,cargo_Ad,cargo_Mn,'
                      'cargo_Ex,anchors,spawn_kill,eng,last_code,last_token',
        'engagements.csv': 'match,game,eng,r0,r1,dur,x0,y0,prog0,nA0,nB0,hpA0,hpB0,peakA,peakB,joinA,joinB,first_hit,dmg_by_A,'
                           'dmg_by_B,kills_by_A,kills_by_B,val_lost_A,val_lost_B,aura_dmg_A,aura_dmg_B,surv_A,surv_B,held,'
                           'result,codes_A,codes_B,fh_att_type,fh_how,fh_vic_type,fh_vic_moved,'
                           'fh_att_moved_prev,fh_in_start,fh_in_prev,fh_cloud,fh_round,fh_att,fh_vic',
        'timeline.csv': 'match,game,round,side,alive_C,alive_L,alive_A,alive_D,alive_B,built_C,built_L,built_A,coll_Ad,coll_Mn,'
                        'coll_Ex,bank_Ad,bank_Mn,bank_Ex,carried_Ad,carried_Mn,carried_Ex,army_value,value_lost,dmg_dealt,'
                        'kills,islands,anchors_placed,in_contact',
        'hq.csv': 'match,game,round,side,hq_id,x,y,bank_Ad,bank_Mn,bank_Ex,built_C,built_L,built_A,built_K,pressure34,'
                  'pressure9,idle_funds,codes',
        'robots.csv': 'match,game,id,side,type,born,died,cause,x_born,y_born,turns,max_still,still_r0,bc_max,bc_over,bc_near,codes',
        'tele_states.csv': 'match,game,side,type,phase,code,letter,detail,turns,share,src_bcc,src_str',
        'trips.csv': 'match,game,side,carrier,t0,first_collect,last_collect,t_end,well_x,well_y,well_type,collects,load,'
                     'wait_rounds,outcome,codes',
    }

    @classmethod
    def setUpClass(cls):
        import time
        cls.tmp = Path(tempfile.mkdtemp())
        t0 = time.time()
        cls.mirror_out = extract(FIX_MIRROR, cls.tmp / 'mirror')
        cls.mirror_secs = time.time() - t0
        cls.two_out = extract(FIX_TWO, cls.tmp / 'two', '--match', '77')
        cls.m = {f: read_csv(cls.tmp / 'mirror' / f) for f in cls.HEADERS}
        cls.t = {f: read_csv(cls.tmp / 'two' / f) for f in cls.HEADERS}
        cls.m['census.csv'] = read_csv(cls.tmp / 'mirror' / 'census.csv')
        cls.t['census.csv'] = read_csv(cls.tmp / 'two' / 'census.csv')

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmp, ignore_errors=True)

    # -- item 2: --extract on two-games.bc23
    def test_extract_files_and_headers(self):
        for d in ('two', 'mirror'):
            for f, h in self.HEADERS.items():
                self.assertEqual((self.tmp / d / f).read_text().splitlines()[0], h, (d, f))
            self.assertEqual((self.tmp / d / 'census.csv').read_text().splitlines()[0],
                             'match,game,' + dump(None, '--census-header').strip())
            self.assertFalse((self.tmp / d / 'tele_events.jsonl').exists())   # no side has dots
            self.assertFalse((self.tmp / d / 'tele_turns.csv').exists())
        self.assertEqual(self.two_out.splitlines(), ['0 maptestsmall 339 A conquest tele_A=none tele_B=none',
                                                     '1 SmallElements 188 A conquest tele_A=none tele_B=none'])
        self.assertEqual(self.mirror_out.strip(), '0 maptestsmall 2000 A tb_mn tele_A=none tele_B=none')

    def test_extract_games_and_census_rows(self):
        g = self.t['games.csv']
        self.assertEqual(len(g), 4)
        self.assertEqual([(r['match'], r['game'], r['side'], r['team'], r['won'], r['win_reason'], r['tele']) for r in g],
                         [('77', '0', 'A', 'g_iter0', '1', 'conquest', 'none'), ('77', '0', 'B', 'examplefuncsplayer', '0', 'conquest', 'none'),
                          ('77', '1', 'A', 'g_iter0', '1', 'conquest', 'none'), ('77', '1', 'B', 'examplefuncsplayer', '0', 'conquest', 'none')])
        lines = (self.tmp / 'two' / 'census.csv').read_text().splitlines()[1:]
        for gi in (0, 1):
            per_game = [line for line in dump(FIX_TWO, '--game', str(gi), '--census', '--no-header').splitlines() if line]
            self.assertEqual([line for line in lines if line.startswith(f'77,{gi},')], [f'77,{gi},' + line for line in per_game])
        mlines = (self.tmp / 'mirror' / 'census.csv').read_text().splitlines()[1:]
        self.assertEqual(mlines, ['0,0,' + line for line in dump(FIX_MIRROR, '--census', '--no-header').splitlines() if line])

    # -- item 3: identities on the mirror (examplefuncsplayer vs itself, A wins on the mana tiebreak 420 vs 17)
    def test_deaths_add_up_and_pinned_split(self):
        summ = dump(FIX_MIRROR)
        died = {'A': 17 + 26, 'B': 47 + 49}
        self.assertIn('died:   CARRIER=17 LAUNCHER=26', summ)
        self.assertIn('died:   CARRIER=47 LAUNCHER=49', summ)
        by = {}
        for r in self.m['deaths.csv']:
            by.setdefault(r['side'], {}).setdefault(r['cause'], 0)
            by[r['side']][r['cause']] += 1
        self.assertEqual({s: sum(v.values()) for s, v in by.items()}, died)
        self.assertEqual(by['B'], {'launcher': 46, 'throw': 40, 'hq_aura': 10})   # 86 hit kills + 10 HQ damage
        self.assertEqual(by['A'], {'launcher': 27, 'throw': 6, 'hq_aura': 10})
        for c in self.m['census.csv']:
            s = c['side']
            self.assertEqual(sum(int(c['deaths_' + k]) for k in ('launcher', 'throw', 'destab', 'aura', 'self', 'resign')), died[s])
            self.assertEqual(int(c['kills_hits']), by['B' if s == 'A' else 'A'].get('launcher', 0) + by['B' if s == 'A' else 'A'].get('throw', 0))

    def test_python_reimplementation_agrees(self):
        """events_model() over --events (count-based pairing) against the Java census (adjacency pairing)."""
        cases = [(FIX_MIRROR, (), self.m['census.csv']), (FIX_TWO, (), self.t['census.csv'][:2]),
                 (FIX_TWO, ('--game', '1'), self.t['census.csv'][2:])]
        for fix, g, census in cases:
            model = events_model(dump(fix, *g, '--events'), dump(fix, *g, '--map-at', '1'))
            for c in census:
                mine = model[c['side']]
                got = {k: int(c[col]) for k, col in (('launcher', 'deaths_launcher'), ('throw', 'deaths_throw'),
                                                     ('hq_aura', 'deaths_aura'), ('self', 'deaths_self'),
                                                     ('dmg_hits', 'dmg_hits'), ('kills_hits', 'kills_hits'),
                                                     ('dmg_aura', 'dmg_aura'), ('kills_aura', 'kills_aura'))}
                self.assertEqual(got, mine, (fix.name, g, c['side']))
        a, b = self.m['census.csv']
        self.assertEqual((a['dmg_hits'], a['kills_hits'], b['dmg_hits'], b['kills_hits']), ('15653', '86', '9133', '33'))

    def test_engagement_damage_within_census(self):
        for d in (self.m, self.t):
            for c in d['census.csv']:
                engs = [e for e in d['engagements.csv'] if e['game'] == c['game']]
                s = c['side']
                self.assertLessEqual(sum(int(e['dmg_by_' + s]) for e in engs), int(c['dmg_hits']))
                self.assertLessEqual(sum(int(e['kills_by_' + s]) for e in engs), int(c['kills_hits']))
                self.assertEqual(int(c['eng_n']), len(engs))
                self.assertEqual(int(c['eng_won']), sum(e['result'] == s for e in engs))
                for e in engs:
                    self.assertLessEqual(int(e['r0']), int(e['r1']))
                    self.assertLessEqual(int(e['surv_' + s]), int(e['join' + s]))
        # every hit lies in a fight cell: the engagements hold all hit damage
        for d in (self.m, self.t):
            for c in d['census.csv']:
                engs = [e for e in d['engagements.csv'] if e['game'] == c['game']]
                self.assertEqual(sum(int(e['dmg_by_' + c['side']]) for e in engs), int(c['dmg_hits']))

    def test_model_identities(self):
        """HP never above the maximum, team totals = HQ banks + cargo every round, every hit attributed."""
        for fix, g, rounds in ((FIX_MIRROR, (), 2000), (FIX_TWO, (), 339), (FIX_TWO, ('--game', '1'), 188)):
            self.assertEqual(dump(fix, *g, '--checks').strip(),
                             f'checks rounds={rounds} hp_over_max=0 hp_nonpos_alive=0 inv_negative=0 team_total_mismatch=0 '
                             'dead_inv_nonzero=0 unattributed_hits=0')
        for d in (self.m, self.t):
            for r in d['deaths.csv']:
                cap = {'C': 150, 'L': 200, 'A': 120, 'D': 300, 'B': 400, 'H': 1}[r['type']]
                self.assertLessEqual(int(r['hp_before']), cap)
                self.assertGreater(int(r['hp_before']), 0)

    def test_trips_add_up_to_collected(self):
        for d in (self.m, self.t):
            for c in d['census.csv']:
                trips = [t for t in d['trips.csv'] if t['game'] == c['game'] and t['side'] == c['side']]
                self.assertEqual(sum(int(t['collects']) for t in trips), int(c['coll_Ad']) + int(c['coll_Mn']) + int(c['coll_Ex']))
                dep = [t for t in trips if t['outcome'] == 'deposit']
                self.assertEqual(sum(int(t['load']) for t in dep), int(c['dep_Ad']) + int(c['dep_Mn']) + int(c['dep_Ex']))
        # the mirror bot never deposits: its trips end by a throw, a death or the end of the game
        self.assertEqual({t['outcome'] for t in self.m['trips.csv']} - {'throw', 'death', 'end'}, set())

    def test_timeline_matches_metrics(self):
        """timeline.csv against the legacy --metrics path (snapshot(): team totals, alive counts, islands, collected)."""
        import csv, io
        for fix, g, d, gi in ((FIX_MIRROR, (), self.m, '0'), (FIX_TWO, (), self.t, '0'), (FIX_TWO, ('--game', '1'), self.t, '1')):
            met = list(csv.DictReader(io.StringIO(dump(fix, *g, '--metrics'))))
            tl = {(r['round'], r['side']): r for r in d['timeline.csv'] if r['game'] == gi}
            n = 0
            for m in met:
                r = tl.get((m['round'], m['team']))
                if r is None:
                    continue
                n += 1
                self.assertEqual((int(m['carriers']), int(m['launchers']), int(m['amplifiers']), int(m['others'])),
                                 (int(r['alive_C']), int(r['alive_L']), int(r['alive_A']), int(r['alive_D']) + int(r['alive_B'])))
                for res in ('Ad', 'Mn', 'Ex'):
                    self.assertEqual(int(m[res]), int(r['bank_' + res]) + int(r['carried_' + res]), (m['round'], res))
                self.assertEqual((m['islands'], m['collected_Mn'], m['collected_Ad']), (r['islands'], r['coll_Mn'], r['coll_Ad']))
            self.assertGreater(n, 4)
        # tiebreak leaders at r500/1000/1500 from the metrics' team totals (islands and anchors are 0 in the mirror)
        met = {(r['round'], r['team']): r for r in csv.DictReader(io.StringIO(dump(FIX_MIRROR, '--metrics')))}
        for col, rnd in (('vtb500', '500'), ('vtb1000', '1000'), ('vtb1500', '1500')):
            a, b = met[(rnd, 'A')], met[(rnd, 'B')]
            want = next((('A' if int(a[k]) > int(b[k]) else 'B') for k in ('islands', 'Ex', 'Mn', 'Ad') if a[k] != b[k]), '-')
            self.assertEqual({r[col] for r in self.m['games.csv']}, {want}, col)
        self.assertEqual({(r['win_reason'], r['tb_margin']) for r in self.m['games.csv']}, {('tb_mn', '403')})   # 420 - 17

    def test_robots_and_hq_rows(self):
        for d in (self.m, self.t):
            for c in d['census.csv']:
                rb = [r for r in d['robots.csv'] if r['game'] == c['game'] and r['side'] == c['side']]
                for ty, col in (('C', 'built_C'), ('L', 'built_L'), ('A', 'built_A')):
                    self.assertEqual(sum(r['type'] == ty and r['born'] != '0' for r in rb), int(c[col]))
                self.assertEqual(sum(r['died'] != '' for r in rb if r['type'] != 'H'),
                                 sum(int(c[k]) for k in ('died_C', 'died_L', 'died_A', 'died_D', 'died_B')))
                self.assertEqual(max(int(r['bc_max']) for r in rb if r['type'] == 'C') if any(r['type'] == 'C' for r in rb) else 0,
                                 int(c['bc_max_C']))
                hq = [h for h in d['hq.csv'] if h['game'] == c['game'] and h['side'] == c['side']]
                self.assertEqual(sum(int(h['built_C']) for h in hq), int(c['built_C']))
                self.assertEqual(sum(int(h['built_L']) for h in hq), int(c['built_L']))
                self.assertEqual(sum(int(h['built_K']) for h in hq), int(c['anchors_built']))
                self.assertEqual(sum(int(h['idle_funds']) for h in hq), int(c['idle_funds']))

    # -- item 4: golden vectors (A.9), packed here independently from the table's inputs
    def test_decode_record_golden_vectors(self):
        import json

        def pack(*fields):   # (value, offset)
            return sum(v << o for v, o in fields)

        def loc(x, y):
            return x * 64 + y + 1
        hdr = (2115895297, pack((1, 0), (37, 8)), pack((loc(12, 7), 0), (2, 12), (1, 16), (3, 17)), pack((16, 0), (42, 8)))
        role = (pack((2, 0), (1, 4), (1, 8)), 30, 420, pack((loc(5, 5), 0), (4, 12)))
        well = (pack((loc(20, 33), 0), (2, 12), (2, 14), (2, 17)), 45, pack((5, 0), (7, 8)), 0)
        trip = (pack((loc(20, 33), 0), (2, 12), (2, 14), (40, 16), (1, 24)), pack((180, 0), (195, 16)),
                pack((215, 0), (231, 16)), pack((3, 0), (1, 16), (20, 24)))
        fight = (pack((1, 0), (1, 2), (1, 3), (1, 4), (3, 5), (1, 14), (3, 16), (1, 24)), pack((1, 0), (1, 8), (13, 16)),
                 pack((2, 0), (1, 8), (9, 16), (9, 24)), pack((140, 0), (4, 8), (10234, 16)))
        table = {'HDR': (2115895297, 9473, 467720, 10768), 'ROLE': (274, 30, 420, 16710), 'WELL': (304418, 45, 1797, 0),
                 'TRIP': (19440930, 12779700, 15139031, 335609859), 'FIGHT': (16990333, 852225, 151585026, 670696588)}
        self.assertEqual({'HDR': hdr, 'ROLE': role, 'WELL': well, 'TRIP': trip, 'FIGHT': fight}, table)
        want = {
            'HDR': {'kind': 'HDR', 'version': 1, 'type': 'C', 'spawn_round': 37, 'spawn': [12, 7], 'roles': 2, 'micro': 0, 'army': 0,
                    'spawn_safety': 1, 'launcher_batch': 3, 'padk': 16, 'sync': 42, 'build': 0},
            'ROLE': {'kind': 'ROLE', 'old': 2, 'new': 1, 'reason': 'hq_stock', 'hq_ad': 30, 'hq_mn': 420, 'hq': [5, 5], 'trips': 4},
            'WELL': {'kind': 'WELL', 'well': [20, 33], 'well_type': 2, 'source': 2, 'role': 2, 'd2': 45, 'shared_wells': 5,
                     'seen_wells': 7, 'search_turns': 0, 'crowd_turns': 0, 'prev_well': None},
            'TRIP': {'kind': 'TRIP', 'well': [20, 33], 'well_type': 2, 'role': 2, 'load': 40, 'hq': 1, 't_start': 180,
                     't_first_collect': 195, 't_last_collect': 215, 't_deposit': 231, 'wait': 3, 'explore': 0, 'flee': 1, 'collect': 20},
            'FIGHT': {'kind': 'FIGHT', 'ready': 1, 'superior': 0, 'outnumbered': 1, 'any_can_hit': 1, 'moved': 1, 'dir': 'EAST',
                      'guard_break': 0, 'micro': 0, 'shots_before': 0, 'shots_after': 1, 'enemy_fighters': 3, 'ally_fighters': 1,
                      'threat': 1, 'can_hit': 1, 'min_d2': 13, 'pinned': 0, 'stay_threat': 2, 'stay_can_hit': 1, 'stay_min_d2': 9,
                      'tiles': 9, 'hp': 140, 'enemies': 4, 'target': 10234}}
        kinds = {'HDR': 0, 'ROLE': 8, 'WELL': 9, 'TRIP': 10, 'FIGHT': 14}
        for name, words in table.items():
            for k in (name, str(kinds[name])):
                out = dump(None, '--decode-record', k, *map(str, words), '--type', 'C' if name != 'FIGHT' else 'L').strip()
                self.assertEqual(json.loads(out), want[name], name)
                self.assertEqual(list(json.loads(out)), list(want[name]), name)   # key order = A.6
                self.assertEqual(out, json.dumps(want[name], separators=(',', ':')))
        self.assertEqual(dump(None, '--decode-record', '20', '1', '2', '3', '4').strip(), '{"kind":"K20"}')
        self.assertEqual(json.loads(dump(None, '--decode-record', '5', str(3 | 5 << 16), '0', '0', '7', '--type', 'L')),
                         {'kind': 'CNTT', 'shots': 3, 'stepped_in': 5, 'kited': 0, 'pinned_seen': 0, 'unsafe_avoided': 0,
                          'regroups': 0, 'follows': 7, 'guard_breaks': 0})
        comms = json.loads(dump(None, '--decode-record', '25', str(1 | 2 << 16), '3', '0', str(65535 << 16)))
        self.assertEqual(comms['kind'], 'COMMS')
        self.assertEqual(comms['slots'][8:16], [1, 2, 3, 0, 0, 0, 0, 65535])
        self.assertEqual(comms['slots'][:8], [None] * 8)
        exc = json.loads(dump(None, '--decode-record', '1', str(2 | 3 << 4 | 2 << 12 | 7 << 16), '100', '101', '1', '--type', 'L'))
        self.assertEqual(exc, {'kind': 'EXC', 'site': 2, 'gae_type': 3, 'phase': 2, 'code': 7, 'token': '!', 'r0': 100,
                               'round_now': 101, 'exc_class': 1})
        cntm = json.loads(dump(None, '--decode-record', 'CNTM', '0', '0', '0', '0'))
        self.assertEqual((cntm['decided_round'], cntm['cand']), (-1, 0))
        anch = json.loads(dump(None, '--decode-record', '12', str(1 | 255 << 4), '0', '0', '0'))
        self.assertEqual((anch['island'], anch['target']), (-1, None))

    # -- item 5: fingerprints
    def test_fingerprint(self):
        a = dump(FIX_TWO, '--fingerprint', cache=False).splitlines()
        b = dump(FIX_TWO, '--fingerprint', cache=False).splitlines()
        self.assertEqual(a, b)
        self.assertEqual(len(a), 2)
        f0, f1 = a[0].split(), a[1].split()
        self.assertEqual((f0[:3], f1[:3]), (['0', 'maptestsmall', '339'], ['1', 'SmallElements', '188']))
        self.assertNotEqual(f0[3], f1[3])
        self.assertNotEqual(f0[4], f1[4])
        self.assertTrue(all(len(x) == 40 for x in f0[3:] + f1[3:]))

    # -- item 7: speed
    def test_extract_speed(self):
        self.assertLess(self.mirror_secs, 60)

    def test_extract_game_selection_and_match_id(self):
        d = self.tmp / 'sel'
        out = extract(FIX_TWO, d, '--games', '1')
        self.assertEqual(out.strip(), '1 SmallElements 188 A conquest tele_A=none tele_B=none')
        g = read_csv(d / 'games.csv')
        self.assertEqual([(r['match'], r['game'], r['map']) for r in g], [('0', '1', 'SmallElements')] * 2)
        # the same game's rows as in the full extract, apart from the match id
        full = [line.split(',', 1)[1] for line in (self.tmp / 'two' / 'deaths.csv').read_text().splitlines()[1:] if line.startswith('77,1,')]
        self.assertEqual([line.split(',', 1)[1] for line in (d / 'deaths.csv').read_text().splitlines()[1:]], full)

    def test_contact_columns_are_shares(self):
        for d in (self.m, self.t):
            for c in d['census.csv']:
                ks = [float(c['kite_' + k]) for k in ('stand_fire', 'fire_retreat', 'stepin_fire', 'fire_ambiguous',
                                                       'advance', 'retreat', 'hold') if c['kite_' + k] != '']
                if ks:
                    self.assertAlmostEqual(sum(ks), 1.0, delta=0.004)
                self.assertTrue(len(c['first_builds'].split()) <= 12)


class ReplayTelemetryTest(unittest.TestCase):
    """B.3 on a game with part A's telemetry (dots, v2 strings and the bytecode channel on one side)."""

    @classmethod
    def setUpClass(cls):
        if not FIX_SELF.exists():
            raise unittest.SkipTest(f'no fixture {FIX_SELF}')
        cls.tmp = Path(tempfile.mkdtemp())
        extract(FIX_SELF, cls.tmp, '--tele-turns', '--match', '5')
        cls.tele = dump(FIX_SELF, '--tele')

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_tele_summary(self):
        import re
        lines = self.tele.splitlines()
        self.assertEqual(lines[0], 'game 0 map maptestsmall rounds 330')
        a = lines[1]
        m = re.match(r'side A team bot tele=both offset=0 sync=(\d+)/(\d+) \(([\d.]+)\) agree=(\d+)/(\d+) \(([\d.]+)\) '
                     r'valid=([\d.]+) invalid=0 exc_turns=0 dots=(\d+) unknown_kinds=0 letter_mismatch=0$', a)
        self.assertIsNotNone(m, a)
        self.assertGreaterEqual(float(m.group(3)), 0.99)
        self.assertGreaterEqual(float(m.group(6)), 0.999)
        self.assertGreater(int(m.group(5)), 1000)
        self.assertIn('side B team examplefuncsplayer tele=none', lines)
        self.assertTrue(any(line.startswith('side A records HDR=') for line in lines))

    def test_events_jsonl(self):
        import json
        ev = [json.loads(line) for line in (self.tmp / 'tele_events.jsonl').read_text().splitlines()]
        self.assertTrue(ev)
        common = ['match', 'game', 'round', 'id', 'side', 'type', 'kind']
        for e in ev:
            self.assertEqual(list(e)[:7], common)
            self.assertEqual((e['match'], e['side']), (5, 'A'))
            self.assertFalse(e['kind'].startswith('K'), e)
        robots = read_csv(self.tmp / 'robots.csv')
        ours = {int(r['id']) for r in robots if r['side'] == 'A' and int(r['turns']) > 0}
        hdr = [e for e in ev if e['kind'] == 'HDR']
        self.assertEqual(sorted(e['id'] for e in hdr), sorted(ours))   # one HDR per robot that took a turn
        self.assertTrue(all(e['version'] == 1 and e['sync'] == 42 for e in hdr))
        comms = [e for e in ev if e['kind'] == 'COMMS']
        self.assertTrue(comms and all(len(e['slots']) == 64 for e in comms))

    def test_bot_trips_match_replay_trips(self):
        """The bot's own TRIP records (what the carrier saw) against trips.csv rebuilt from the replay alone."""
        import json
        ev = [json.loads(line) for line in (self.tmp / 'tele_events.jsonl').read_text().splitlines()]
        rep = {(int(t['carrier']), int(t['t_end'])): t for t in read_csv(self.tmp / 'trips.csv') if t['outcome'] == 'deposit'}
        bot = [e for e in ev if e['kind'] == 'TRIP']
        self.assertGreater(len(bot), 20)
        n = 0
        for e in bot:
            t = rep.get((e['id'], e['t_deposit']))
            if t is None or e['t_first_collect'] == 0:
                continue
            n += 1
            self.assertEqual((int(t['first_collect']), int(t['last_collect']), int(t['load'])),
                             (e['t_first_collect'], e['t_last_collect'], e['load']), e)
            self.assertEqual([int(t['well_x']), int(t['well_y'])], e['well'], e)
        self.assertGreaterEqual(n, 0.9 * len(bot))

    def test_codes_two_channels_agree(self):
        turns = read_csv(self.tmp / 'tele_turns.csv')
        both = [t for t in turns if t['code_bcc'] and t['code_str']]
        self.assertGreater(len(both), 1000)
        self.assertEqual(sum(t['code_bcc'] != t['code_str'] for t in both), 0)
        self.assertTrue(all(t['side'] == 'A' for t in turns))
        self.assertTrue(all(t['code_bcc'] == '' for t in turns if t['sync'] == '1'))
        c = {r['side']: r for r in read_csv(self.tmp / 'census.csv')}
        self.assertEqual((c['A']['tele'], c['A']['tele_offset'], c['A']['tele_agree'], c['A']['tele_exc_turns']), ('both', '0', '1.0000', '0'))
        self.assertEqual((c['B']['tele'], c['B']['tele_offset'], c['B']['tstates_C']), ('none', '', ''))
        self.assertTrue(c['A']['tstates_C'] and c['A']['tstates_L'] and c['A']['tstates_HQ'])
        st = read_csv(self.tmp / 'tele_states.csv')
        for ty in ('C', 'L', 'H'):
            self.assertAlmostEqual(sum(float(r['share']) for r in st if r['type'] == ty and r['phase'] == 'all'), 1.0, delta=0.01)
        self.assertTrue(all(int(r['turns']) == int(r['src_bcc']) + int(r['src_str']) for r in st))


class ReplayTelemetryFixturesTest(unittest.TestCase):
    """B.7 item 6 (part A's fixtures; the merge step removes the skip): the same cell with indicators on and off."""

    @classmethod
    def setUpClass(cls):
        for f in (FIX_TELE, FIX_TELE_OFF):
            if not f.exists():
                raise unittest.SkipTest(f'no fixture {f}')

    def test_status_on_and_off(self):
        import re
        on = dump(FIX_TELE, '--tele')
        m = re.search(r'side A team \S+ tele=both offset=0 sync=\d+/\d+ \(([\d.]+)\) agree=\d+/\d+ \(([\d.]+)\) .* '
                      r'unknown_kinds=0 letter_mismatch=0', on)
        self.assertIsNotNone(m, on)
        self.assertGreaterEqual(float(m.group(1)), 0.99)
        self.assertGreaterEqual(float(m.group(2)), 0.999)
        self.assertRegex(on, r'side B team \S+ tele=none')
        self.assertRegex(dump(FIX_TELE_OFF, '--tele'), r'side A team \S+ tele=bcc offset=0 ')

    def test_same_game_and_codes_survive_indicators_off(self):
        f_on = dump(FIX_TELE, '--fingerprint').split()
        f_off = dump(FIX_TELE_OFF, '--fingerprint').split()
        self.assertEqual(f_on[3], f_off[3])   # state_sha1: indicators change nothing in the game
        import shutil
        tmp = Path(tempfile.mkdtemp())
        try:
            extract(FIX_TELE, tmp / 'on', '--tele-turns')
            extract(FIX_TELE_OFF, tmp / 'off', '--tele-turns')
            on = {(t['round'], t['id']): t for t in read_csv(tmp / 'on' / 'tele_turns.csv')}
            off = [t for t in read_csv(tmp / 'off' / 'tele_turns.csv') if t['code_bcc']]
            self.assertGreater(len(off), 1000)
            # the end-to-end proof: a replica-style replay (indicators off) carries the codes the strings recorded
            same = sum(on.get((t['round'], t['id']), {}).get('code_str') == t['code_bcc'] for t in off)
            self.assertGreaterEqual(same / len(off), 0.999)
            self.assertFalse((tmp / 'off' / 'tele_events.jsonl').exists())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class FieldScoreTest(unittest.TestCase):
    """tools/field_score.py: the submissions' fit R0 + a ln(1 + t) and its projection (owner, PROMPTS 39)."""

    def setUp(self):
        self.fs = load('field_score', 'field_score.py')

    def test_fit_recovers_the_curve(self):
        import math
        ts = [0.0, 0.5, 1.0, 2.0, 3.0]
        rs = [1800 + 100 * math.log(1 + t) for t in ts]
        r0, a, cov = self.fs.fit_log(ts, rs, [30.0] * len(ts))
        self.assertAlmostEqual(r0, 1800, places=6)
        self.assertAlmostEqual(a, 100, places=6)
        mid, half = self.fs.predict((r0, a, cov), 7.0)
        self.assertAlmostEqual(mid, 1800 + 100 * math.log(8), places=6)
        self.assertGreater(half, 0)

    def test_too_few_submissions(self):
        self.assertIsNone(self.fs.fit_log([0.0, 1.0], [1800.0, 1850.0], [30.0, 30.0]))

    def test_metrics_rank_and_scores(self):
        fs, vh, nup, rank = self.fs.metrics(1500.0, [1400.0, 1500.0, 1600.0, 1700.0])
        self.assertEqual((nup, rank), (2, 3))
        self.assertTrue(0.0 < vh < 0.5 < fs + 0.25)


class RatingHistoryTest(unittest.TestCase):
    """tools/rating_history.py: the Team page's rating curve and each submission's first rated match (PROMPTS 44)."""

    US = 28

    def setUp(self):
        self.rh = load('rating_history', 'rating_history.py')

    def m(self, mid, created, sub, rating=1500.0, ranked=True, tour=None, status='OK!', other_sub=None, old=None):
        return {'id': mid, 'status': status, 'created': created, 'is_ranked': ranked, 'tournament_round': tour,
                'participants': [{'team': 9, 'submission': other_sub, 'rating': 1400.0, 'old_rating': 1400.0},
                                 {'team': self.US, 'submission': sub, 'rating': rating, 'old_rating': old}]}

    def test_points_from_history_in_time_order(self):
        js = {'team_id': self.US, 'team_rating': {'rating_history': [
            {'timestamp': '2026-10-08T03:00:00-04:00', 'rating': 300.0},
            {'timestamp': '2026-10-08T06:30:00Z', 'rating': 400.0},    # 02:30 -04:00: earlier than the first entry
            {'timestamp': '2026-10-08T04:00:00-04:00', 'rating': None}]}}
        pts = self.rh.points_from_history(js)
        self.assertEqual([r for _, r in pts], [400.0, 300.0])
        self.assertEqual(pts[0][0].utcoffset(), self.rh.dt.timedelta(0))
        self.assertEqual(self.rh.points_from_history(None), [])          # HTTP 204: no ranked matches
        self.assertEqual(self.rh.points_from_history({'team_id': 1, 'team_rating': None}), [])

    def test_first_use_is_earliest_by_created_not_by_list_order(self):
        ms = [self.m(30, '2026-10-09T12:00:00-04:00', 7, 1600.0),       # newest first, as the API lists them
              self.m(20, '2026-10-09T10:00:00-04:00', 7, 1580.0, old=1570.0),
              self.m(25, '2026-10-09T11:00:00-04:00', 7, 1590.0)]
        f = self.rh.first_rated_use(ms, self.US)
        self.assertEqual(list(f), [7])
        self.assertEqual((f[7]['match'], f[7]['rating'], f[7]['old_rating'], f[7]['matches']), (20, 1580.0, 1570.0, 3))

    def test_population_skips_unranked_tournament_null_rating_and_cancelled(self):
        ms = [self.m(1, '2026-10-09T01:00:00-04:00', 5, ranked=False),
              self.m(2, '2026-10-09T02:00:00-04:00', 5, tour={'id': 3}),
              self.m(3, '2026-10-09T03:00:00-04:00', 5, rating=None),      # not rated yet
              self.m(4, '2026-10-09T04:00:00-04:00', 5, status='CAN'),     # a chart point, but no game was played
              self.m(5, '2026-10-09T05:00:00-04:00', 5),
              self.m(6, '2026-10-09T06:00:00-04:00', 6, ranked=False)]     # 6 played only unranked: absent
        f = self.rh.first_rated_use(ms, self.US)
        self.assertEqual(sorted(f), [5])
        self.assertEqual((f[5]['match'], f[5]['matches'], f[5]['cancelled']), (5, 2, 1))
        self.assertEqual([m['id'] for _, m, _ in self.rh.rated(ms, self.US)], [4, 5])

    def test_duplicate_match_ids_count_once(self):
        # the newest-first page crawl can repeat a match when one is created mid-crawl; the later copy is kept
        ms = [self.m(2, '2026-10-09T02:00:00-04:00', 5, 1510.0),
              self.m(1, '2026-10-09T01:00:00-04:00', 5, 1500.0, status='CAN'),
              self.m(1, '2026-10-09T01:00:00-04:00', 5, 1500.0, status='CAN'),
              self.m(2, '2026-10-09T02:00:00-04:00', 5, 1510.0)]
        self.assertEqual([m['id'] for _, m, _ in self.rh.rated(ms, self.US)], [1, 2])
        f = self.rh.first_rated_use(ms, self.US)
        self.assertEqual((f[5]['match'], f[5]['matches'], f[5]['cancelled']), (2, 2, 1))

    def test_other_teams_submissions_ignored(self):
        ms = [self.m(1, '2026-10-09T01:00:00-04:00', None, other_sub=99),   # the opponent's submission id
              self.m(2, '2026-10-09T02:00:00-04:00', 8, other_sub=99)]
        ms.append({'id': 3, 'status': 'OK!', 'created': '2026-10-09T03:00:00-04:00', 'is_ranked': True,
                   'tournament_round': None, 'participants': [{'team': 9, 'submission': 98, 'rating': 1.0},
                                                              {'team': 10, 'submission': 97, 'rating': 2.0}]})
        self.assertEqual(sorted(self.rh.first_rated_use(ms, self.US)), [8])

    def test_pdt_conversion(self):
        t = self.rh.parse_ts('2026-10-10T19:40:46.376414-04:00')
        self.assertEqual(self.rh.to_pdt(t), self.rh.dt.datetime(2026, 10, 10, 16, 40, 46, 376414))
        self.assertEqual(self.rh.to_pdt(self.rh.parse_ts('2026-10-08T02:35:39Z')), self.rh.dt.datetime(2026, 10, 7, 19, 35, 39))
        self.assertEqual(self.rh.to_pdt(self.rh.parse_ts('2026-11-02T20:00:00Z')).hour, 12)   # PST after Nov 1
        oct_, nov = self.rh.parse_ts('2026-10-10T23:40:00Z'), self.rh.parse_ts('2026-11-02T20:00:00Z')
        self.assertEqual([self.rh.zone_label([oct_]), self.rh.zone_label([nov]), self.rh.zone_label([nov, oct_])],
                         ['PDT', 'PST', 'PDT/PST'])
        self.assertEqual((self.rh.utc_lead(oct_), self.rh.utc_lead(nov)), (7, 8))   # galaxy's UTC chart reads later

    def test_md_curve_only_and_names_from_the_response(self):
        hist = {'team_id': self.US, 'team_rating': {'team': {'name': 'teamX', 'episode': 'bcXX'}, 'rating_history': [
            {'timestamp': '2026-10-08T03:00:00-04:00', 'rating': 300.0}]}}
        pts = self.rh.points_from_history(hist)
        self.assertEqual(self.rh.team_info({'historical_rating': hist}), ('teamX', 'bcXX'))
        self.assertEqual(self.rh.team_info({'historical_rating': None, 'episode': 'bc23'}), ('our team', 'bc23'))
        with tempfile.TemporaryDirectory() as d:
            md = os.path.join(d, 'r.md')
            self.rh.write_md(pts, [], [], {'historical_rating': hist, 'team_id': self.US}, md, 'r.png')   # raw response
            text = Path(md).read_text()
            self.assertIn('/api/compete/bcXX/match/historical_rating/', text)
            self.assertIn('No submission markers', text)
            self.assertNotIn('| Submission |', text)
            self.assertNotIn('Kind:', text)
            self.assertIn('7 h later', text)

    def test_names_kinds_rows_and_label_spread(self):
        hist = [{'event': 'init', 'submission': 24, 'package': 'g_iter0'},
                {'event': 'trial-start', 'submission': 120, 'package': 'c_a'},
                {'event': 'accept', 'submission': 120, 'package': 'c_a'},
                {'event': 'trial-start', 'submission': 121, 'package': 'c_b'},
                {'event': 'reject', 'submission': 121, 'package': 'c_b'}]
        subs = [{'id': 113, 'package': 'g_iter0'}, {'id': 121, 'package': None, 'description': 'c_b (trial)'},
                {'id': 130, 'package': '', 'description': ''}]
        names = self.rh.package_names(subs, hist)
        self.assertEqual([self.rh.name_of(names, s) for s in (24, 113, 120, 121, 130)],
                         ['g_iter0', 'g_iter0', 'c_a', 'c_b', 'sub 130'])
        self.assertEqual([self.rh.kind_of(s, names.get(s), hist) for s in (24, 113, 120, 121, 130)],
                         ['validated', 'reupload', 'validated', 'trial', 'trial'])
        ms = [self.m(1, '2026-10-09T01:00:00-04:00', 24, 200.0, old=0.0),
              self.m(2, '2026-10-09T02:00:00-04:00', 24, 300.0),
              self.m(3, '2026-10-09T03:00:00-04:00', 113, 280.0, old=300.0)]
        pts = [(self.rh.parse_ts(m['created']), m['participants'][1]['rating']) for m in ms]
        rows = self.rh.rows(pts, self.rh.first_rated_use(ms, self.US), names, hist)
        self.assertEqual([(r['sub'], r['kind'], r['before'], r['after']) for r in rows],
                         [(24, 'validated', 0.0, 200.0), (113, 'reupload', 300.0, 280.0)])   # the first: old_rating
        pos = self.rh.spread([0.5, 0.0, 0.51, 1.0, 0.505], 0.02)
        self.assertTrue(all(0.0 <= p <= 1.0 for p in pos))
        self.assertGreaterEqual(min(abs(a - b) for i, a in enumerate(pos) for b in pos[i + 1:]), 0.02 - 1e-9)
        self.assertEqual(sorted(range(5), key=lambda i: pos[i]), [1, 0, 4, 2, 3])          # order kept
        for got, want in zip(self.rh.spread([0.99, 1.0, 0.98], 0.02), [0.98, 1.0, 0.96]):   # pushed back under hi
            self.assertAlmostEqual(got, want)
        for got, want in zip(self.rh.spread([0.5, 0.5, 0.5], 0.6), [0.0, 0.6, 1.2]):       # too wide: spaced from lo
            self.assertAlmostEqual(got, want)

    def test_calibrate_recovers_a_line_and_filters_the_field(self):
        # BT = -7000 + 5 * galaxy exactly, then with symmetric noise that keeps the slope and the intercept
        exact = [(g, -7000.0 + 5.0 * g) for g in (1400.0, 1500.0, 1550.0, 1650.0, 1700.0)]
        a, b, r, n, sd = self.rh.calibrate(exact)
        self.assertAlmostEqual(a, -7000.0, places=6); self.assertAlmostEqual(b, 5.0, places=9)
        self.assertAlmostEqual(r, 1.0, places=9); self.assertEqual(n, 5); self.assertAlmostEqual(sd, 0.0, places=4)
        noisy = [(g, -7000.0 + 5.0 * g + e) for g in (1400.0, 1600.0) for e in (-40.0, 40.0)]   # +-40 at each x
        a, b, r, n, sd = self.rh.calibrate(noisy)
        self.assertAlmostEqual(b, 5.0); self.assertAlmostEqual(a, -7000.0); self.assertTrue(0.99 < r < 1.0)
        self.assertEqual(n, 4)
        self.assertAlmostEqual(sd, (4 * 40.0 ** 2 / (4 - 2)) ** 0.5)       # residual SD on n - 2 degrees of freedom
        # the line's local misfit: teams within the band of a galaxy rating, galaxy minus the converted BT
        pairs = [(1500.0, -7000.0 + 5.0 * 1510.0), (1530.0, -7000.0 + 5.0 * 1520.0), (1700.0, 0.0)]
        self.assertEqual(self.rh.peer_offset(pairs, (-7000.0, 5.0), 1520.0, band=40), (2, 0.0))   # -10 and +10
        self.assertEqual(self.rh.peer_offset(pairs, (-7000.0, 5.0), 1505.0, band=10), (1, -10.0))
        self.assertIsNone(self.rh.peer_offset(pairs, (-7000.0, 5.0), 1600.0, band=40))
        self.assertIsNone(self.rh.calibrate(exact[:2]))                     # too few
        self.assertIsNone(self.rh.calibrate([(1500.0, 1.0), (1500.0, 2.0), (1500.0, 3.0)]))   # no galaxy spread
        ranks = [{'id': 1, 'name': 'a.bot', 'rating': 1600.0}, {'id': 2, 'name': 'b.bot', 'rating': 1399.0},   # < floor
                 {'id': 3, 'name': 'c.bot', 'rating': 1500.0},                                              # 29 games
                 {'id': self.US, 'name': 'vibe23', 'rating': 1610.0},                                       # our team
                 {'id': 5, 'name': 'examplefuncsplayer', 'rating': 1450.0},                                 # a baseline
                 {'id': 6, 'name': 'd.bot', 'rating': None}, {'id': 7, 'name': 'e.bot', 'rating': 1450.0}]  # e: no BT
        R = {'a.bot': 2100.0, 'b.bot': 900.0, 'c.bot': 1500.0, 'vibe23': 2000.0, 'examplefuncsplayer': 800.0,
             'd.bot': 1700.0}
        games = {'a.bot': 30, 'b.bot': 200, 'c.bot': 29, 'vibe23': 300, 'examplefuncsplayer': 300, 'd.bot': 99}
        self.assertEqual(self.rh.calibration_pairs(ranks, R, games, self.US), [(1600.0, 2100.0)])

    def test_tenures_merge_reuploads_and_trials_never_rated(self):
        t = lambda h: self.rh.parse_ts(f'2026-10-09T{h:02d}:00:00Z')
        marks = [('c_b', t(5)), ('g0', t(1)), ('g0', t(2)), ('c_a', t(3)), ('c_a', t(4)), ('c_a', t(6))]   # any order
        self.assertEqual(self.rh.tenures(marks),
                         [('g0', t(1), t(3)), ('c_a', t(3), t(5)), ('c_b', t(5), t(6)), ('c_a', t(6), None)])
        self.assertEqual(self.rh.tenures([('g0', t(1))], end=t(9)), [('g0', t(1), t(9))])
        self.assertEqual(self.rh.tenures([]), [])
        hist = [{'event': 'init', 'package': 'g0', 'at': '2026-10-09T00:00:00Z'},
                {'event': 'trial-start', 'package': 'c_x', 'at': '2026-10-09T04:00:00Z'},
                {'event': 'trial-start', 'package': 'c_a', 'at': '2026-10-09T02:30:00Z'},   # rated later: no diamond
                {'event': 'trial-start', 'package': 'c_y', 'at': '2026-10-09T03:00:00Z'},
                {'event': 'trial-start', 'package': 'c_x', 'at': '2026-10-09T08:00:00Z'}]   # re-trial: the first counts
        self.assertEqual(self.rh.trial_candidates(hist, {'g0', 'c_a', 'c_b'}), [('c_y', t(3)), ('c_x', t(4))])
        # the layer: a build without recorded games has bt None; galaxy_end is the last point before the next build
        pts = [(t(1), 1300.0), (t(2), 1450.0), (t(3), 1500.0), (t(7), 1520.0)]
        table = [{'package': 'g0', 'created': t(1)}, {'package': 'c_a', 'created': t(3)}]
        ranks = [{'id': i, 'name': f'f{i}', 'rating': 1400.0 + 100 * i} for i in range(4)]
        R = {f'f{i}': 700.0 + 500 * i for i in range(4)}; R.update({'us:g0': 1800.0, 'us:c_y': 1900.0})
        SE = {'us:g0': 20.0, 'us:c_y': 40.0}
        games = {**{f'f{i}': 50 for i in range(4)}, 'us:g0': 300, 'us:c_y': 100}
        lay = self.rh.bt_layer(ranks, (R, SE, games), table, hist, pts, team_id=self.US)
        a, b, r, n, sd = lay['cal']
        self.assertAlmostEqual(b, 5.0); self.assertAlmostEqual(a, -6300.0); self.assertEqual(n, 4)
        self.assertEqual(lay['peers'][0], 1); self.assertAlmostEqual(lay['peers'][1], 0.0)   # f1 (1,500) near 1,520
        self.assertEqual([(s['package'], s['end'], s['bt'], s['galaxy_end']) for s in lay['steps']],
                         [('g0', t(3), (1800.0, 20.0, 300), 1450.0), ('c_a', None, None, 1520.0)])
        self.assertEqual([(x['package'], x['bt']) for x in lay['trials']], [('c_y', (1900.0, 40.0, 100)), ('c_x', None)])

    def test_floor_clip_count_and_footer(self):
        t = lambda h: self.rh.parse_ts(f'2026-10-09T{h:02d}:00:00Z')
        pts = [(t(1), 0.0), (t(2), 900.0), (t(3), 1399.9), (t(4), 1400.0), (t(5), 1500.0)]
        self.assertEqual(self.rh.below_floor(pts), (3, t(3)))                # 1,400 itself is on the chart
        self.assertEqual(self.rh.below_floor(pts[3:]), (0, None))
        self.assertEqual(self.rh.below_floor(pts + [(t(6), 1390.0)]), (4, t(6)))   # a later dip counts too
        bundle = {'matches': [], 'team_id': self.US}
        note = '\n'.join(self.rh.footer(pts, [{'after': 300.0, 'kind': 'validated'}], bundle, None))
        self.assertIn('3 points below it (the climb from 0, the last at Oct 08 20:00 PDT)', note)
        self.assertIn('; ▼ on the floor: a first rated match below it', note)
        note = '\n'.join(self.rh.footer(pts, [{'after': 300.0, 'kind': 'validated'}, {'after': 1300.0, 'kind': 'reupload'},
                                              {'after': 1500.0, 'kind': 'trial'}], bundle, None))
        self.assertIn('; ▼ ▽ on the floor', note)                            # a hollow one is named too
        note = '\n'.join(self.rh.footer(pts + [(t(6), 1390.0)], [], bundle, {'cal': (-7000.0, 5.0, 0.98, 70, 80.0)}))
        self.assertIn('4 points below it (the last at', note)               # not a prefix: no "climb" wording
        self.assertNotIn('on the floor', note)
        self.assertIn('BT = -7,000 + 5.00 x galaxy rating', note)
        self.assertIn('70 field teams', note)
        self.assertIn("the BT fit's 95% only. Field teams scatter ±31 galaxy points (95%)", note)   # 1.96 x 80 / 5

    def test_leader_crossings(self):
        zig = [(0.0, 0.0), (10.0, 10.0), (20.0, 0.0), (30.0, 10.0)]
        self.assertEqual(self.rh.crossings((0.0, 5.0), (30.0, 5.0), zig), 3)       # across every segment
        self.assertEqual(self.rh.crossings((5.0, 5.0), (5.0, 20.0), zig), 0)       # from on the curve: not across
        self.assertEqual(self.rh.crossings((5.0, -1.0), (5.0, 20.0), zig), 1)
        self.assertEqual(self.rh.crossings((40.0, 0.0), (50.0, 10.0), zig), 0)     # beside it
        self.assertEqual(self.rh.crossings((0.0, 1.0), (1.0, 0.0), [(0.0, 0.0), (1.0, 1.0)]), 1)   # two leaders


class ParamTest(unittest.TestCase):
    """tools/param.py (owner, PROMPTS 114): C.java overrides at build time and the random search space."""
    @classmethod
    def setUpClass(cls):
        cls.p = load('param', 'param.py')
        cls.text = (REPO / 'src' / 'c_well9' / 'C.java').read_text()

    def test_space_fits_the_base(self):
        b = self.p.base_setting(self.text)          # every space constant is an int constant of c_well9
        for s in self.p.SPACE:
            if self.p.opts(s).get('optional') and s[0] not in b:
                continue
            self.assertTrue(s[1] <= b[s[0]] <= s[2] or b[s[0]] == self.p.opts(s).get('off'), s[0])
        self.assertEqual(self.p.violations(b), [])
        self.assertEqual(len({s[0] for s in self.p.SPACE}), len(self.p.SPACE))
        required = [s[0] for s in self.p.SPACE if not self.p.opts(s).get('optional')]
        self.assertEqual(sorted(b), sorted(required))      # c_well9 lacks only the optional micro knobs

    def test_optional_knobs(self):
        k = self.p.base_setting((REPO / 'src' / 'c_knob1' / 'C.java').read_text())
        self.assertEqual((k['AHEAD_MIN'], k['HOLD_THREAT']), (2, 1))   # c_well9's hard-coded values
        self.assertEqual(len(k), len(self.p.SPACE))
        b = self.p.base_setting(self.text)
        for s in self.p.sample(5, 3, names=set(b)):
            self.assertEqual(set(s), set(b))
        for s in self.p.sample(5, 3, names=set(k)):
            self.assertEqual(set(s), set(k))

    def test_apply_changes_only_declarations(self):
        out = self.p.apply(self.text, {'RING_MIN': 12, 'CAP_MAX': 24, 'AURA_SAFE': 'false', 'AURA_OUT_W': 5})
        c = self.p.constants(out)
        self.assertEqual(c['RING_MIN'][1], '12')
        self.assertEqual(c['RING_MAX'][1], '34')           # its neighbour in the same declaration is kept
        self.assertEqual(c['CAP_MAX'][1], '24')
        self.assertEqual(c['AURA_SAFE'][1], 'false')
        self.assertEqual(c['AURA_OUT_W'][1], '5L')
        strip = lambda s: [l for l in s.splitlines() if 'static final' not in l]
        self.assertEqual(strip(out), strip(self.text))     # comments and everything else unchanged
        with self.assertRaises(ValueError):
            self.p.apply(self.text, {'NO_SUCH': 1})
        with self.assertRaises(ValueError):
            self.p.apply(self.text, {'RING_MIN': 'x'})

    def test_sample_is_valid_and_deterministic(self):
        a, b = self.p.sample(20, 5), self.p.sample(20, 5)
        self.assertEqual(a, b)
        self.assertNotEqual(a, self.p.sample(20, 6))
        for s in a:
            self.assertEqual(self.p.violations(s), [])
            for sp in self.p.SPACE:
                self.assertTrue(sp[1] <= s[sp[0]] <= sp[2] or s[sp[0]] == self.p.opts(sp).get('off'), sp[0])

    def test_local_mode(self):
        b = self.p.base_setting((REPO / 'src' / 'c_knob1' / 'C.java').read_text())
        ss = self.p.sample(30, 4, names=set(b), base=b, k=6, always=('AHEAD_MIN', 'HOLD_THREAT'))
        self.assertEqual(ss, self.p.sample(30, 4, names=set(b), base=b, k=6, always=('AHEAD_MIN', 'HOLD_THREAT')))
        for s in ss:
            self.assertEqual(set(s), set(b))
            self.assertLessEqual(sum(s[x] != b[x] for x in b), 6)          # at most k constants move
            self.assertEqual(self.p.violations(s), [])
        moved = {x for s in ss for x in b if s[x] != b[x]}
        self.assertIn('AHEAD_MIN', moved)
        self.assertGreater(len(moved), 20)                                   # different constants per variant

    def test_local_mode_pool(self):
        b = self.p.base_setting((REPO / 'src' / 'c_well9' / 'C.java').read_text())
        pool = ('AD_EARLY_EVERY', 'AD_LATE_EVERY', 'CAP_MAX', 'CAP_PER_MN_WELL', 'ANCHOR_START')
        ss = self.p.sample(30, 5, names=set(b), base=b, k=3, pool=pool)
        self.assertEqual(ss, self.p.sample(30, 5, names=set(b), base=b, k=3, pool=pool))
        moved = {x for s in ss for x in b if s[x] != b[x]}
        self.assertLessEqual(moved, set(pool))                               # nothing outside the pool moves
        self.assertGreater(len(moved), 3)
        for s in ss:
            self.assertEqual(self.p.violations(s), [])

    def test_make_renames_and_guards(self):
        with tempfile.TemporaryDirectory() as td:
            d = self.p.make('c_well9', 'c_ptest', {'RING_MIN': 12}, out=td, note='unit test')
            for f in (REPO / 'src' / 'c_well9').glob('*.java'):
                g = (d / f.name).read_text()
                self.assertIn('package c_ptest;', g)
                self.assertNotIn('package c_well9;', g)
            self.assertIn('GENERATED by tools/param.py from c_well9 (unit test)', (d / 'C.java').read_text())
            with self.assertRaises(FileExistsError):           # never overwrites a package
                self.p.make('c_well9', 'c_ptest', {}, out=td)
            with self.assertRaises(ValueError):                 # max < min is refused
                self.p.make('c_well9', 'c_ptest2', {'RING_MIN': 30}, out=td)
        with self.assertRaises(FileExistsError):
            self.p.make('c_well9', 'c_well9', {})


class SwissTest(unittest.TestCase):
    """tools/swiss.py (owner, PROMPTS 114): pairing, points, standings, seeds."""
    @classmethod
    def setUpClass(cls):
        cls.s = load('swiss', 'swiss.py')

    def g(self, r, a, b, m, winner):
        return {'round': str(r), 'a': a, 'b': b, 'map': m, 'winner': winner}

    def test_pairings_never_repeat(self):
        names = [f'b{i:02d}' for i in range(16)]
        games, pairs = [], {}
        for r in range(1, 5):
            prs = self.s.pairing(names, games, pairs, r, 9, 'b00')
            self.assertEqual(sorted(x for p in prs for x in p), sorted(names))    # everyone plays once
            for x, y in prs:
                for old in pairs.values():
                    self.assertNotIn((x, y), old)
                    self.assertNotIn((y, x), old)
                for m in ('M1', 'M2', 'M3'):                                      # lower name wins
                    games += [self.g(r, x, y, m, min(x, y)), self.g(r, y, x, m, min(x, y))]
            pairs[r] = prs
        rows = self.s.table(names, games, pairs, 'b00')
        self.assertEqual(rows[0][0], 'b00')
        self.assertEqual(rows[0][1], 24.0)               # 4 rounds x 6 games, all won
        self.assertEqual(rows[0][4], '4-0-0')

    def test_points_buchholz_and_base_tiebreak(self):
        games = [self.g(1, 'x', 'base', 'M', 'x'), self.g(1, 'base', 'x', 'M', 'base'),
                 self.g(1, 'y', 'z', 'M', '?'), self.g(1, 'z', 'y', 'M', 'z')]
        pairs = {1: [('x', 'base'), ('y', 'z')]}
        rows = self.s.table(['x', 'base', 'y', 'z'], games, pairs, 'base')
        self.assertEqual([r[0] for r in rows], ['z', 'base', 'x', 'y'])   # 1.5; then 1-1 with the base first
        self.assertEqual(dict((r[0], r[1]) for r in rows)['y'], 0.5)      # half a point for a game without result
        self.assertEqual(dict((r[0], r[4]) for r in rows)['base'], '0-1-0')

    def test_seed_shared_by_both_sides(self):
        a = self.s.game_seed(1, 2, 'p', 'q', 'Forest')
        self.assertEqual(a, self.s.game_seed(1, 2, 'p', 'q', 'Forest'))
        self.assertNotEqual(a, self.s.game_seed(1, 2, 'p', 'q', 'Maze'))
        self.assertTrue(1 <= a < 2 ** 28 + 1)

    def test_parse_engine_output(self):
        out = '[server] c_sw01 (B) wins (round 2000)\n[server] Reason: The winning team won on tiebreakers.\n'
        self.assertEqual(self.s.parse(out), ('B', '2000', 'The winning team won on tiebreakers.'))
        self.assertEqual(self.s.parse('crash'), ('?', '?', '?'))

    def test_spearman(self):
        self.assertAlmostEqual(self.s.spearman([1, 2, 3], [10, 20, 30]), 1.0)
        self.assertAlmostEqual(self.s.spearman([1, 2, 3], [3, 2, 1]), -1.0)


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=0).result
    print(f"test_tools: {r.testsRun} tests, {len(r.failures)} failures, {len(r.errors)} errors")
    sys.exit(0 if r.wasSuccessful() else 1)
