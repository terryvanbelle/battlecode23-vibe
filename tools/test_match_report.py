#!/usr/bin/env python3
"""Tests of docs/TELEMETRY.md part C (C.8): tools/match_report.py, the tools/contest.py hook and census_of,
tools/telemetry_query.py, and the no-strings guards of tools/basics.py and tools/delivery.py. Synthetic inputs and
the committed fixtures; no games, no network. Run by tools/unit-tests.sh."""
import contextlib, csv, importlib.util, io, json, os, shutil, subprocess, sys, tempfile, time, unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
FIX_TWO = REPO / 'test/fixtures/two-games.bc23'
FIX_SELF = REPO / 'test/fixtures/telemetry-selfplay.bc23'
# part A's fixtures (A.10 item 8); the merge step (TELEMETRY.md §8) removes the skips below
FIX_TELE = REPO / 'test/fixtures/tele-example-maptestsmall.bc23'
FIX_TELE_OFF = REPO / 'test/fixtures/tele-example-maptestsmall-indoff.bc23'

# vibe23 is player 1 (replay label B) with alternate order: game 1 is reversed
MATCH77 = {'id': 77, 'status': 'OK!', 'alternate_order': True, 'is_ranked': False, 'created': '2026-10-08T01:02:03Z',
           'maps': ['maptestsmall', 'SmallElements'], 'replay_url': '/x',
           'participants': [{'team': 2, 'teamname': 'teamX', 'player_index': 0, 'submission': 11, 'score': 2},
                            {'team': 1, 'teamname': 'vibe23', 'player_index': 1, 'submission': 24, 'score': 0}]}
LINE_KEYS = {'v', 'match', 'reported_at', 'created', 'ranked', 'status', 'us', 'submission', 'opponent', 'our_label',
             'score', 'replay', 'extract', 'report', 'shadow', 'games'}
GAME_KEYS = {'game', 'map', 'rev', 'side', 'result', 'rounds', 'win_reason', 'turn_round', 'lock_round', 'onset', 'us',
             'them', 'tele', 'anomalies'}
SIDE_KEYS = {'team', 'built', 'died', 'coll', 'at', 'deaths_by_cause', 'value_lost', 'dmg_hits', 'kills_hits',
             'spawn_kills', 'cargo_lost_Mn', 'eng', 'idle_funds', 'overruns', 'near', 'islands_end', 'anchors_placed',
             'kite', 'alone20', 'first_builds'}
ENG_KEYS = {'n', 'won', 'lost', 'n_par', 'won_par', 'n_ahead', 'won_ahead', 'n_behind', 'won_behind', 'exch',
            'first_hit', 'by_dn'}
TELE_KEYS = {'status', 'offset', 'sync', 'agree', 'exc_turns', 'states', 'states_by_phase', 'carrier_mn',
             'launcher_out', 'eng_codes', 'events', 'trip', 'fight'}


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, TOOLS / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **kw)
    return r, buf.getvalue()


def jsonl(path):
    with open(path) as fh:
        return [json.loads(l) for l in fh if l.strip()]


_TWO = {}


def two_root():
    """A root where match 77 (two-games.bc23) has been reported once; extracted once per test run, then copied."""
    if 'root' not in _TWO:
        tmp = Path(tempfile.mkdtemp(prefix='mr-two-'))
        mr = load('match_report_root', 'match_report.py')
        mr.ROOT = str(tmp)
        (tmp / 'm77.json').write_text(json.dumps(MATCH77))
        _TWO['rc'], _TWO['out'] = quiet(mr.main, ['match', str(FIX_TWO), '--match-json', str(tmp / 'm77.json')])
        _TWO['root'] = tmp
    dst = Path(tempfile.mkdtemp(prefix='mr-copy-')) / 'root'
    shutil.copytree(_TWO['root'], dst)
    return dst


# ---------------------------------------------------------------- C.8 item 1 (and C.2 census_of identity)
class MatchReportTwoGamesTest(unittest.TestCase):
    """`match` on two-games.bc23 (g_iter0 vs examplefuncsplayer) with vibe23 as player 1 and alternate order."""
    @classmethod
    def setUpClass(cls):
        cls.tmp = two_root()
        cls.mr = load('match_report_two', 'match_report.py')
        cls.mr.ROOT = str(cls.tmp)
        cls.mj = cls.tmp / 'm77.json'
        cls.rc, cls.out = _TWO['rc'], _TWO['out']
        cls.report = cls.tmp / 'research/matches/77.md'
        cls.lines = jsonl(cls.tmp / 'progress/telemetry.jsonl')

    def test_report_shape(self):
        self.assertEqual(self.rc, 0)
        txt = self.report.read_text()
        self.assertLessEqual(len(txt.encode()), 8192)
        self.assertTrue(txt.startswith('# Match 77: vibe23 (sub 24) vs teamX - 0-2   (unranked, 2026-10-08 01:02 UTC)'))
        self.assertIn('\nTelemetry: us none (this build carries no telemetry: replay-only sections)  |  replay ', txt)
        self.assertIn('| game | map | side | result | rounds | reason | turn/lock | Mn@100 us/them |', txt)
        for gi in (0, 1):
            self.assertIn(f'## Game {gi}: ', txt)
        self.assertEqual(txt.count('\nAnomalies: '), 2)
        self.assertIn('## Game 1: SmallElements, loss r188 (conquest) reversed', txt)
        self.assertIn('Our decisions: not available (tele=none', txt)
        self.assertIn('report: match 77 0-2 vs teamX -> research/matches/77.md', self.out)

    def test_json_line_has_every_key(self):
        self.assertEqual(len(self.lines), 1)
        d = self.lines[0]
        self.assertLessEqual(LINE_KEYS, set(d))
        self.assertEqual((d['v'], d['match'], d['us'], d['opponent'], d['our_label'], d['score'], d['submission'],
                          d['ranked'], d['report'], d['extract']),
                         (1, 77, 'vibe23', 'teamX', 'B', [0, 2], 24, False, 'research/matches/77.md',
                          'matches/77/extract'))
        self.assertEqual(len(d['games']), 2)
        for G in d['games']:
            self.assertLessEqual(GAME_KEYS, set(G))
            self.assertLessEqual(TELE_KEYS, set(G['tele']))
            for s in ('us', 'them'):
                self.assertLessEqual(SIDE_KEYS, set(G[s]))
                self.assertLessEqual(ENG_KEYS, set(G[s]['eng']))
            self.assertEqual(G['tele']['status'], 'none')
            self.assertIn('tele_missing', G['anomalies'])
            self.assertEqual(sum(n for n, w in G['us']['eng']['by_dn'].values()), G['us']['eng']['n'])
        g0 = d['games'][0]
        self.assertEqual((g0['us']['team'], g0['them']['team']), ('examplefuncsplayer', 'g_iter0'))
        self.assertEqual(g0['them']['at']['100']['Mn'], 278)       # census cMn100 of g_iter0
        self.assertNotIn('500', g0['us']['at'])                     # the game ended at r339

    def test_side_rev_result_match_run_rows(self):
        c = load('contest_rr', 'contest.py')
        rows = c.run_rows(MATCH77, str(FIX_TWO), 1)
        G = self.lines[0]['games']
        self.assertEqual([(r['game'], r['bot_side'], r['seed'] == 'map-rev', r['bot_result']) for r in rows],
                         [(g['game'], g['side'], g['rev'], g['result']) for g in G])

    def test_idempotent_then_force_supersedes(self):
        jp = self.tmp / 'progress/telemetry.jsonl'
        rc, out = quiet(self.mr.main, ['match', str(FIX_TWO), '--match-json', str(self.mj)])
        self.assertEqual(rc, 0)
        self.assertIn('already reported', out)
        self.assertEqual(len(jsonl(jp)), 1)
        quiet(self.mr.main, ['match', str(FIX_TWO), '--match-json', str(self.mj), '--force'])
        ls = jsonl(jp)
        self.assertEqual(len(ls), 2)
        self.assertTrue(ls[1]['supersedes'])
        self.assertEqual(self.mr.read_lines()[77]['reported_at'], ls[1]['reported_at'])

    def test_census_of_reads_extract_and_equals_fallback(self):
        c = load('contest_co', 'contest.py')
        rows = [dict(r, opponent='teamX', map=m, bot_side='B', seed=s, match=77)
                for r, m, s in (({'game': 0}, 'maptestsmall', 'map'), ({'game': 1}, 'SmallElements', 'map-rev'))]
        calls = []
        real = subprocess.run

        def spy(*a, **kw):
            calls.append(a[0])
            return real(*a, **kw)
        with mock.patch.dict(os.environ, {'MATCH_REPORT_ROOT': str(self.tmp)}), mock.patch.object(c.subprocess, 'run', spy):
            via_extract = c.census_of(str(FIX_TWO), rows)
        self.assertEqual(calls, [])
        with mock.patch.dict(os.environ, {'MATCH_REPORT_ROOT': str(self.tmp / 'nowhere')}), \
                mock.patch.object(c.subprocess, 'run', spy):
            fallback = c.census_of(str(FIX_TWO), rows)
        self.assertEqual(len(calls), 2)
        self.assertEqual(via_extract, fallback)
        self.assertEqual(len(via_extract), 4)
        self.assertTrue(via_extract[0].startswith('teamX,maptestsmall,B,map,maptestsmall,g_iter0,A,1,339,'))


# ---------------------------------------------------------------- a synthetic extract (mocked ReplayDump output)
GAMES_HDR = ('match,game,map,width,height,symmetry,islands,rounds,side,team,won,win_reason,tb_margin,vtb500,vtb1000,'
             'vtb1500,tele,tele_offset,tele_sync_n,tele_sync,tele_agree_n,tele_agree,tele_valid,tele_invalid,'
             'tele_exc_turns,tele_dots,tele_unknown_kinds')


def read_csv(path):
    with open(path, newline='') as fh:
        return list(csv.DictReader(fh))


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0].keys())
    with open(path, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow(r)


def synthetic_extract(d):
    """One 2000-round game, us = A ('both' telemetry with every anomaly trigger), them = B."""
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    g = {'match': 9, 'game': 0, 'map': 'Forest', 'width': 30, 'height': 30, 'symmetry': 'ROT', 'islands': 4,
         'rounds': 2000, 'win_reason': 'tb_islands', 'tb_margin': 1, 'vtb500': 'B', 'vtb1000': 'A', 'vtb1500': 'B',
         'tele_sync_n': 40}
    write_csv(d / 'games.csv', [
        dict(g, side='A', team='vibe23', won=0, tele='both', tele_offset=3, tele_sync=0.95, tele_agree_n=1000,
             tele_agree=0.998, tele_valid=1.0, tele_invalid=2, tele_exc_turns=4, tele_dots=50, tele_unknown_kinds=1),
        dict(g, side='B', team='teamX', won=1, tele='none', tele_sync=0.02, tele_agree_n=0, tele_dots=0,
             tele_unknown_kinds=0)], GAMES_HDR.split(','))
    base = {'match': 9, 'game': 0, 'map': 'Forest', 'rounds': 2000, 'win_reason': 'tb_islands', 'turn_round': 900,
            'lock_round': 1200, 'onset_L': 300, 'onset_Mn': '', 'onset_value': 800, 'onset_islands': 1000}
    us = dict(base, team='vibe23', side='A', won=0, built_C=20, built_L=40, built_A=2, built_D=0, built_B=0,
              died_C=5, died_L=30, died_A=1, died_D=0, died_B=0, coll_Ad=3000, coll_Mn=5000, coll_Ex=0, isl_end=1,
              anchors_placed=3, near=0, over=2, counters='ex=1;nm=0;', tele='both', tele_offset=3, tele_agree=0.998,
              tele_exc_turns=4, tele_carrier_mn=0.6, tele_L_out=0.25, deaths_launcher=30, deaths_throw=0,
              deaths_destab=0, deaths_aura=5, deaths_self=1, deaths_resign=0, value_lost=2000, dmg_hits=4000,
              kills_hits=25, spawn_kills=2, cargo_lost_Ad=10, cargo_lost_Mn=20, anchors_lost=1, eng_n=3, eng_won=1,
              eng_lost=1, eng_n_par=1, eng_won_par=1, eng_n_ahead=1, eng_won_ahead=0, eng_n_behind=1,
              eng_won_behind=0, exch_ratio=0.9, first_hit_rate=0.5, idle_funds=500, kite_stand_fire=0.5,
              kite_fire_retreat=0.1, kite_stepin_fire=0.1, kite_fire_ambiguous=0.1, kite_advance=0.1,
              kite_retreat=0.05, kite_hold=0.05, alone20=0.2, first_builds='1:C 1:L 2:C')
    them = dict(base, team='teamX', side='B', won=1, built_C=25, built_L=45, died_C=3, died_L=28, isl_end=3,
                near=0, over=0, counters='', tele='none', deaths_launcher=25, deaths_aura=0, deaths_self=3,
                value_lost=1800, idle_funds=10)
    write_csv(d / 'census.csv', [us, them], list(us.keys()))
    tl = []
    for r in list(range(10, 2001, 10)):
        for s in 'AB':
            bank = 500 + (r - 600) if s == 'A' and 600 <= r <= 700 else 100
            tl.append({'match': 9, 'game': 0, 'round': r, 'side': s, 'alive_C': 10 if s == 'A' else 12,
                       'alive_L': 8 if s == 'A' else 9, 'coll_Mn': r * (2 if s == 'A' else 3), 'coll_Ad': r,
                       'bank_Mn': bank, 'army_value': 400 if s == 'A' else 500, 'islands': 1 if s == 'A' else 2})
    write_csv(d / 'timeline.csv', tl)
    eng = {'match': 9, 'game': 0, 'dur': 5, 'x0': 1, 'y0': 1, 'first_hit': 'A', 'dmg_by_A': 100, 'dmg_by_B': 90,
           'kills_by_A': 1, 'kills_by_B': 1, 'codes_B': ''}
    write_csv(d / 'engagements.csv', [
        dict(eng, eng=0, r0=310, r1=315, prog0=0.4, nA0=2, nB0=4, val_lost_A=90, val_lost_B=0, result='B',
             codes_A='F=3;Fo=2;H=1'),
        dict(eng, eng=1, r0=400, r1=410, prog0=0.5, nA0=3, nB0=3, val_lost_A=0, val_lost_B=135, result='A',
             codes_A='F=4;M=1;Ho=2'),
        dict(eng, eng=2, r0=900, r1=905, prog0=0.6, nA0=5, nB0=1, val_lost_A=45, val_lost_B=45, result='draw',
             codes_A='')])
    rob = {'match': 9, 'game': 0, 'born': 1, 'died': '', 'cause': '', 'x_born': 1, 'y_born': 1, 'turns': 100,
           'bc_max': 1, 'bc_over': 0, 'bc_near': 0, 'codes': ''}
    write_csv(d / 'robots.csv', [
        dict(rob, id=3, side='A', type='H', max_still=2000, still_r0=1),
        dict(rob, id=101, side='A', type='C', max_still=50, still_r0=100),    # collecting r100-130: 19 free rounds
        dict(rob, id=102, side='A', type='C', max_still=45, still_r0=500),    # never collected: a stall
        dict(rob, id=201, side='A', type='L', max_still=40, still_r0=300),    # engagement r310-315: 34 free
        dict(rob, id=202, side='A', type='L', max_still=35, still_r0=400),    # engagement r400-410: 24 free
        dict(rob, id=301, side='B', type='L', max_still=90, still_r0=10)])
    write_csv(d / 'trips.csv', [{'match': 9, 'game': 0, 'side': 'A', 'carrier': 101, 't0': 90, 'first_collect': 100,
                                 'last_collect': 130, 't_end': 160, 'outcome': 'deposit'}])
    write_csv(d / 'hq.csv', [{'match': 9, 'game': 0, 'round': 25, 'side': 'A', 'hq_id': 3, 'bank_Mn': 120,
                              'pressure34': 5, 'pressure9': 2, 'idle_funds': 10, 'codes': 'p=25'},
                             {'match': 9, 'game': 0, 'round': 50, 'side': 'A', 'hq_id': 3, 'bank_Mn': 300,
                              'pressure34': 0, 'pressure9': 0, 'idle_funds': 0, 'codes': 'w=25'}])
    ts = {'match': 9, 'game': 0, 'side': 'A', 'detail': '', 'share': 0, 'src_bcc': 0, 'src_str': 0}
    write_csv(d / 'tele_states.csv', [
        dict(ts, type='C', phase='all', code=2, letter='G', turns=30), dict(ts, type='C', phase='all', code=4,
                                                                            letter='C', turns=50),
        dict(ts, type='C', phase='all', code=5, letter='C', turns=20), dict(ts, type='H', phase='all', code=3,
                                                                            letter='p', turns=60),
        dict(ts, type='H', phase='all', code=4, letter='w', turns=40), dict(ts, type='C', phase='open', code=2,
                                                                            letter='G', turns=30)])
    ev = lambda kind, **kw: json.dumps(dict({'match': 9, 'game': 0, 'round': kw.pop('round', 100), 'id': kw.pop('id', 101),
                                             'side': kw.pop('side', 'A'), 'type': 'C', 'kind': kind}, **kw))
    lines = [ev('TRIP', t_start=100, t_deposit=140, wait=1, explore=0, flee=0, load=40),
             ev('TRIP', t_start=200, t_deposit=250, wait=2, explore=0, flee=0, load=40),
             ev('TRIP', t_start=300, t_deposit=360, wait=3, explore=3, flee=1, load=20),
             ev('FIGHT', tiles=9, threat=2, stay_threat=1, outnumbered=1, moved=1, min_d2=5, stay_min_d2=9),
             ev('FIGHT', tiles=9, threat=0, stay_threat=1, outnumbered=1, moved=1, min_d2=13, stay_min_d2=9),
             ev('FIGHT', tiles=0, threat=4, stay_threat=0, outnumbered=0, moved=0, min_d2=255, stay_min_d2=255),
             ev('FIGHT', tiles=5, threat=3, stay_threat=3, outnumbered=0, moved=1, guard_break=1, shots_after=1),
             ev('ROLE', reason='spawn', hq_mn=-1), ev('ROLE', reason='spawn', hq_mn=-1),
             ev('ROLE', reason='hq_stock', hq_mn=420),
             ev('WELL', source=2), ev('WELL', source=5), ev('WELL', source=2),
             ev('SYM', cand_after=1, r0=45), ev('CNTM', decided_round=50, tele_max_cost=300, tele_deferrals=2),
             ev('COMMS', round=100, slots=[1, 0, None, 2] + [0] * 60),
             ev('K20'), ev('TRIP', side='B', t_start=1, t_deposit=2), '{not json']
    (d / 'tele_events.jsonl').write_text('\n'.join(lines) + '\n')
    return d


class MatchReportSyntheticTest(unittest.TestCase):
    """Every summary number and anomaly from a hand-made extract (no ReplayDump run)."""
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='mr-syn-'))
        cls.mr = load('match_report_syn', 'match_report.py')
        cls.mr.ROOT = str(cls.tmp)
        cls.mr.letter_mismatch = lambda replay, gi, side: 2
        cls.ex = cls.mr.Extract(str(synthetic_extract(cls.tmp / 'extract')))
        games, _, _ = cls.mr.build('none.bc23', cls.ex, 'A', False, 9)
        cls.G = games[0]

    def test_game_fields(self):
        G = self.G
        self.assertEqual((G['result'], G['rounds'], G['win_reason'], G['tb_margin'], G['first_contact']),
                         ('loss', 2000, 'tb_islands', 1, 310))
        self.assertEqual(G['vtb'], {'500': 'them', '1000': 'us', '1500': 'them'})
        self.assertEqual(G['onset'], {'L': 300, 'Mn': None, 'value': 800, 'islands': 1000})
        us = G['us']
        self.assertEqual(us['at']['100'], {'C': 10, 'L': 8, 'Mn': 200, 'Ad': 100, 'value': 400, 'bank_Mn': 100,
                                           'islands': 1})
        self.assertEqual(us['eng']['by_dn'], {'-3': [0, 0], '-2': [1, 0], '-1': [0, 0], '0': [1, 1], '1': [0, 0],
                                              '2': [0, 0], '3': [1, 0]})
        self.assertEqual(G['them']['eng']['by_dn']['2'], [1, 1])        # their view of the first engagement
        self.assertEqual(us['deaths_by_cause']['self'], 1)
        self.assertEqual((us['idle_bank_Mn_p50'], us['pressure9'], us['pressure34']), (120, 2, 5))
        self.assertEqual(us['kite']['stand_fire'], 0.5)
        self.assertIsNone(G['them']['kite'])

    def test_tele_fields(self):
        t = self.G['tele']
        self.assertEqual((t['status'], t['offset'], t['agree'], t['exc_turns'], t['invalid'], t['letter_mismatch']),
                         ('both', 3, 0.998, 4, 2, 2))
        self.assertEqual(t['states'], {'C': {'C': 0.7, 'G': 0.3}, 'HQ': {'p': 0.6, 'w': 0.4}})
        self.assertEqual(t['states_by_phase']['open'], {'C': {'G': 1.0}})
        self.assertEqual(t['eng_codes'], {'F': 7, 'Fo': 2, 'H': 1, 'Ho': 2, 'M': 1})
        self.assertEqual(t['events'], {'CNTM': 1, 'COMMS': 1, 'FIGHT': 4, 'K20': 1, 'ROLE': 3, 'SYM': 1, 'TRIP': 3,
                                       'WELL': 3})
        self.assertEqual(t['trip'], {'n': 3, 'cycle_p50': 50, 'wait_mean': 2.0, 'explore_mean': 1.0, 'flee_mean': 0.33,
                                     'load_mean': 33.3})
        self.assertEqual(t['fight'], {'n': 4, 'riskier_than_stay': 0.3333, 'stepin_outnumbered': 0.25,
                                      'outnumbered': 0.5, 'moved': 0.75, 'fired': 0.25, 'guard_breaks': 1})
        d = t['dots']
        self.assertEqual((d['roles'], d['role_hq_mn_p50'], d['well_sources'], d['sym_decided'], d['comms_fill']),
                         ({'spawn': 2, 'hq_stock': 1}, 420, {'seen': 2, 'crowd_switch': 1}, 45,
                          {'100': 2, '500': None}))
        self.assertEqual((d['tele_max_cost'], d['tele_deferrals']), (300, 2))

    def test_anomalies(self):
        self.assertEqual(self.G['anomalies'], [
            'overruns:2', 'exc:6', 'bcc_disagree:0.0020', 'tele_offset:3', 'tele_invalid:2', 'stall:C#102@r500-r544',
            'stall:L#201@r300-r339', 'float:Mn500@r600-r700', 'idle_hq:0.25', 'unknown_kinds:1', 'letter_mismatch:2',
            'opp_exc:3'])
        self.assertEqual(self.G['stalls'], 2)

    def test_report_sections(self):
        line = {'replay': 'none.bc23', 'extract': 'extract'}
        txt, level = self.mr.render_fit(self.ex, '# Match 9', line, [self.G])
        self.assertEqual(level, 0)
        for s in ('We lost on the islands tiebreak at r2000 (margin 1). Tiebreak standing r500/1000/1500: them/us/them.',
                  'Our decisions (tele=both, offset 3, agree 0.9980):', '  Carrier: open G 1.00; Mn role 0.60',
                  'in engagements F .69 H .23 M .08; outnumbered at contact 0.31',
                  'trips 3, cycle p50 50, wait/trip 2.00, explore/trip 1.00',
                  'FIGHT 4: riskier than stay 0.33, step-ins outnumbered 0.25', 'symmetry decided r45',
                  'by dN at start (won/n): behind 0/1, -1 0/0, par 1/1, +1 0/0, ahead 0/1.',
                  '| 400-410 | 0.50 | 3/3 | us | 100/90 | 1/1 | 0/135 | won | F=4;M=1;Ho=2 |',
                  '| 1000 | 10/12 | 8/9 | 2000/3000 |', 'Anomalies: overruns:2, exc:6'):
            self.assertIn(s, txt)


# ---------------------------------------------------------------- C.8 item 2: robustness
class MatchReportRobustTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='mr-rob-'))
        cls.mr = load('match_report_rob', 'match_report.py')
        cls.mr.ROOT = str(cls.tmp)
        cls.mr.letter_mismatch = lambda replay, gi, side: None

    def report(self, d, us='A'):
        ex = self.mr.Extract(str(d))
        games, _, _ = self.mr.build('none.bc23', ex, us, False, 9)
        return self.mr.render_fit(ex, '# Match 9', {'replay': 'r', 'extract': 'e'}, games)[0], games

    def test_without_dots_and_tier2(self):
        d = synthetic_extract(self.tmp / 'a')
        (d / 'tele_events.jsonl').unlink()
        (d / 'trips.csv').unlink()
        rows = read_csv(d / 'census.csv')
        keep = [k for k in rows[0] if not k.startswith('kite_') and k not in ('alone20', 'first_builds')]
        write_csv(d / 'census.csv', [{k: r[k] for k in keep} for r in rows], keep)
        txt, games = self.report(d)
        self.assertIn('Dots: not available (no data dots', txt)
        G = games[0]
        self.assertIsNone(G['tele']['trip'])
        self.assertIsNone(G['tele']['dots'])
        self.assertIsNone(G['us']['kite'])
        self.assertNotIn('stall:C#102@r500-r544', G['anomalies'])   # carriers need trips.csv
        self.assertIn('stall:L#201@r300-r339', G['anomalies'])

    def test_only_games_and_census(self):
        d = synthetic_extract(self.tmp / 'b')
        for f in d.iterdir():
            if f.name not in ('games.csv', 'census.csv'):
                f.unlink()
        txt, games = self.report(d)
        for s in ('Economy and army: not available', 'Engagements: not available', 'Dots: not available'):
            self.assertIn(s, txt)
        self.assertIsNone(games[0]['us']['eng']['by_dn'])

    def test_no_telemetry_columns(self):
        d = synthetic_extract(self.tmp / 'c')
        for f in d.iterdir():
            if f.name != 'census.csv':
                f.unlink()
        rows = read_csv(d / 'census.csv')
        keep = [k for k in rows[0] if not k.startswith('tele')]
        write_csv(d / 'census.csv', [{k: r[k] for k in keep} for r in rows], keep)
        txt, games = self.report(d)
        self.assertIn('Our decisions: not available (no telemetry columns).', txt)
        self.assertEqual(games[0]['result'], 'loss')                  # no games.csv: census `won`

    def test_legacy_fallback_when_extract_fails(self):
        real = self.mr.run_dump

        def no_extract(*args, **kw):
            if '--extract' in args:
                return subprocess.CompletedProcess(args, 2, '', 'unknown mode --extract')
            return real(*args, **kw)
        with mock.patch.object(self.mr, 'run_dump', no_extract):
            ex, note = self.mr.extract(str(FIX_TWO), str(self.tmp / 'legacy'), 77)
        self.assertIn('--extract failed (unknown mode --extract)', note)
        self.assertFalse((self.tmp / 'legacy').exists())
        self.assertEqual(ex.games(), [0, 1])
        games, _, _ = self.mr.build(str(FIX_TWO), ex, 'A', True, 77)
        txt, _ = self.mr.render_fit(ex, '# Match 77', {'replay': 'r', 'extract': 'e'}, games, [f'Extraction: {note}.'])
        self.assertIn('Engagements: not available', txt)
        self.assertEqual([G['result'] for G in games], ['win', 'win'])
        self.assertEqual(games[0]['us']['at']['100']['Mn'], 278)     # census snapshot columns

    def test_ten_games_fit_in_8kb(self):
        src = synthetic_extract(self.tmp / 'ten-src')
        d = self.tmp / 'ten'
        d.mkdir()
        for f in src.glob('*.csv'):
            rows = read_csv(f)
            write_csv(d / f.name, [dict(r, game=k) for k in range(10) for r in rows], list(rows[0].keys()))
        shutil.copy(src / 'tele_events.jsonl', d)
        txt, games = self.report(d)
        self.assertEqual(len(games), 10)
        self.assertLessEqual(len(txt.encode()), 8192)
        for k in range(10):
            self.assertIn(f'## Game {k}: ', txt)
        self.assertEqual(txt.count('\nAnomalies: '), 10)


# ---------------------------------------------------------------- C.8 item 3: the contest.py hook and census_of
class ContestHookTest(unittest.TestCase):
    def setUp(self):
        self.c = load('contest_hook', 'contest.py')
        self.calls = []
        self.m = {'id': 5, 'status': 'OK!', 'participants': [], 'replay_url': '/r'}
        self.c.me = lambda: {'id': 1}
        self.c.api = lambda method, path, *a, **kw: self.m
        self.c.download = lambda m, out: '/tmp/5.bc23'
        self.c.games_of = lambda p: []

    def fetch(self, run):
        def fake(cmd, **kw):
            self.calls.append((cmd, json.loads(Path(cmd[cmd.index('--match-json') + 1]).read_text())))
            return run(cmd, **kw)
        with mock.patch.object(self.c.subprocess, 'run', fake), mock.patch.object(sys, 'argv', ['contest.py', 'fetch', '5']):
            return quiet(self.c.main)

    def test_fetch_calls_report(self):
        with mock.patch.dict(os.environ, {'NO_MATCH_REPORT': ''}):
            (rc, out) = self.fetch(lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, 'report: match 5 0-1 vs x\n', ''))
        self.assertEqual(rc, 0)
        cmd, m = self.calls[0]
        self.assertTrue(cmd[1].endswith('tools/match_report.py'))
        self.assertEqual(cmd[2:4], ['match', '/tmp/5.bc23'])
        self.assertEqual(cmd[-2:], ['--team-id', '1'])
        self.assertEqual(m, self.m)
        self.assertIn('report: match 5 0-1 vs x', out)
        self.assertFalse(os.path.exists(cmd[cmd.index('--match-json') + 1]))   # the temporary JSON is removed

    def test_failures_never_raise(self):
        def boom(cmd, **kw):
            raise subprocess.TimeoutExpired(cmd, 1800)
        with mock.patch.dict(os.environ, {'NO_MATCH_REPORT': ''}):
            rc, out = self.fetch(boom)
            self.assertEqual(rc, 0)
            self.assertIn('report: match 5 failed: ', out)
            rc, out = self.fetch(lambda cmd, **kw: subprocess.CompletedProcess(cmd, 1, '', 'Traceback\nValueError: x\n'))
            self.assertIn('report: match 5 failed: ValueError: x', out)

    def test_no_match_report_skips(self):
        with mock.patch.dict(os.environ, {'NO_MATCH_REPORT': '1'}):
            rc, out = self.fetch(lambda cmd, **kw: self.fail('called'))
        self.assertEqual(self.calls, [])
        self.assertIn('/tmp/5.bc23', out)

    def test_block_reports_before_census(self):
        c, log = self.c, []
        tmp = Path(tempfile.mkdtemp(prefix='mr-block-'))
        (tmp / 'cells.txt').write_text('teamX m1,m2 +\n')
        m = {'id': 9, 'status': 'OK!', 'maps': ['m1', 'm2'], 'participants': [
            {'team': 1, 'teamname': 'vibe23', 'player_index': 0}, {'team': 2, 'teamname': 'teamX', 'player_index': 1}]}
        seen = []
        c.me = lambda: {'id': 1, 'name': 'vibe23'}
        c.matches = lambda tid, limit_pages=1: (seen.append(1) or []) if not seen else [m]
        c.pages = lambda path, limit=None: [{'id': 3, 'accepted': True, 'package': 'bot'}]
        c.request = lambda *a: {'id': 100}
        c.download = lambda mm, d: '/x/9.bc23'
        c.report_hook = lambda mm, rep, tid: log.append(('hook', mm['id'], rep, tid))
        c.run_rows = lambda mm, rep, tid: [{'game': 0}]
        c.census_of = lambda rep, rows: log.append(('census', rep)) or []
        c.write_run = lambda run, rows, cr: None
        with mock.patch.dict(os.environ, {'RESUME': str(tmp / 'run')}):
            quiet(c.block, str(tmp / 'cells.txt'), 't', poll=0)
        self.assertEqual(log, [('hook', 9, '/x/9.bc23', 1), ('census', '/x/9.bc23')])

    def test_census_of_stamp_rules(self):
        c = self.c
        tmp = Path(tempfile.mkdtemp(prefix='mr-co-'))
        rep = tmp / '7.bc23'
        rep.write_bytes(b'0123456789')
        ext = tmp / 'matches/7/extract'
        ext.mkdir(parents=True)
        (ext / 'census.csv').write_text('match,game,map,team\n7,0,m,a\n7,0,m,b\n7,1,n,a\n')
        rows = [{'game': 0, 'match': 7, 'opponent': 'X', 'map': 'm', 'bot_side': 'A', 'seed': 'map'},
                {'game': 2, 'match': 7, 'opponent': 'X', 'map': 'k', 'bot_side': 'A', 'seed': 'map'}]
        h = load('mr_hash', 'match_report.py').dump_hash()
        calls = []
        fake = lambda cmd, **kw: calls.append(cmd[3:5]) or subprocess.CompletedProcess(cmd, 0, 'k,c\n\n', '')
        with mock.patch.dict(os.environ, {'MATCH_REPORT_ROOT': str(tmp)}), mock.patch.object(c.subprocess, 'run', fake):
            (ext / '.stamp').write_text(f'{h} 10\n')
            self.assertEqual(c.census_of(str(rep), rows), ['X,m,A,map,m,a', 'X,m,A,map,m,b', 'X,k,A,map,k,c'])
            self.assertEqual(calls, [['--game', '2']])                  # game 2 is not in the extract: fallback
            (ext / '.stamp').write_text(f'{h} 11\n')                    # another replay of the same id
            calls.clear()
            c.census_of(str(rep), rows)
            self.assertEqual(calls, [['--game', '0'], ['--game', '2']])
            (ext / '.stamp').write_text('000000000000 10\n')            # an older ReplayDump
            calls.clear()
            c.census_of(str(rep), rows)
            self.assertEqual(len(calls), 2)


# ---------------------------------------------------------------- C.8 item 4: telemetry_query
def qgame(gi, mp, res, mn, mn_t, l250, l250_t, dn, dn_t, launcher, launcher_t, over, status, exc, anomalies, side='A'):
    S = lambda mn, l250, dn, launcher, over: {
        'at': {'100': {'Mn': mn, 'L': 3}, '250': {'L': l250}}, 'eng': {'n': sum(n for n, w in dn.values()),
                                                                      'won': sum(w for n, w in dn.values()), 'by_dn': dn},
        'deaths_by_cause': {'launcher': launcher, 'self': 0}, 'value_lost': launcher * 45, 'overruns': over, 'near': 0}
    return {'game': gi, 'map': mp, 'side': side, 'result': res, 'rounds': 2000, 'turn_round': 100 * (gi + 1),
            'lock_round': None, 'onset': {}, 'us': S(mn, l250, dn, launcher, over),
            'them': S(mn_t, l250_t, dn_t, launcher_t, 0),
            'tele': {'status': status, 'exc_turns': exc, 'agree': 1.0 if status == 'bcc' else None},
            'anomalies': anomalies}


def query_lines():
    m = lambda mid, opp, sub, ranked, day, games, **kw: dict({'v': 1, 'match': mid, 'opponent': opp, 'submission': sub,
                                                              'ranked': ranked, 'created': f'2026-10-0{day}T00:00:00Z',
                                                              'report': f'research/matches/{mid}.md', 'games': games}, **kw)
    return [
        m(1, 'X', 24, True, 1, [qgame(0, 'Forest', 'win', 100, 50, 9, 8, {'0': [2, 1], '1': [1, 1]},
                                      {'0': [2, 1], '-1': [1, 0]}, 3, 5, 0, 'bcc', 0, ['near:1']),
                                qgame(1, 'Lake', 'loss', 60, 120, 4, 10, {'0': [1, 0], '-1': [2, 0]},
                                      {'0': [1, 1], '1': [2, 2]}, 5, 2, 1, 'none', None, [])]),
        m(3, 'X', 25, True, 3, [qgame(0, 'Forest', 'win', 999, 0, 0, 0, {}, {}, 0, 0, 0, 'none', None, [])]),
        m(2, 'Y', 24, False, 2, [qgame(0, 'Forest', 'win', 80, 80, 6, 6, {'0': [1, 1]}, {'0': [1, 0]}, 2, 4, 0, 'none',
                                       None, [])]),
        m(3, 'X', 25, True, 3, [qgame(0, 'Forest', 'win', 120, 60, 7, 5, {'2': [1, 1]}, {'-2': [1, 0]}, 6, 1, 2, 'bcc',
                                      4, ['overruns:2', 'stall:L#5@r1-r40'])], supersedes=True)]


class TelemetryQueryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q = load('telemetry_query_t', 'telemetry_query.py')
        cls.tmp = Path(tempfile.mkdtemp(prefix='tq-'))
        cls.f = cls.tmp / 'telemetry.jsonl'
        cls.f.write_text(''.join(json.dumps(l) + '\n' for l in query_lines()))

    def run_q(self, *args):
        buf = io.StringIO()
        rc = self.q.main([*args, '--file', str(self.f)], out=buf)
        self.assertEqual(rc, 0)
        return buf.getvalue()

    def rows(self, *args):
        return {(r['group'], r['metric']): r for r in csv.DictReader(io.StringIO(self.run_q(*args, '--csv')))}

    def test_econ(self):
        r = self.rows('econ')[('all', 'Mn@100 collected')]
        self.assertEqual((r['n_us'], r['us'], r['us_se'], r['them'], r['diff'], r['n_diff']),
                         ('4', '90.0', '12.9099', '77.5', '12.5', '4'))      # match 3's superseded line is ignored
        self.assertIn('Mn@100 collected', self.run_q('econ'))

    def test_fights_dn_table(self):
        R = self.rows('fights')
        r0 = R[('all', 'win@dN=+0')]
        self.assertEqual((r0['n_us'], r0['us'], r0['n_them'], r0['them'], r0['diff']), ('4', '0.5', '4', '0.5', '0.0'))
        self.assertEqual(r0['us_se'], '0.25')
        self.assertEqual((R[('all', 'win@dN=-1')]['us'], R[('all', 'win@dN=-1')]['n_us'],
                          R[('all', 'win@dN=-1')]['them'], R[('all', 'win@dN=-1')]['n_them']), ('0.0', '2', '0.0', '1'))
        self.assertEqual((R[('all', 'win@dN=+1')]['us'], R[('all', 'win@dN=+1')]['them'],
                          R[('all', 'win@dN=+1')]['n_them']), ('1.0', '1.0', '2'))
        self.assertEqual((R[('all', 'win@dN=+2')]['us'], R[('all', 'win@dN=+2')]['them']), ('1.0', ''))
        self.assertEqual(R[('all', 'eng won share')]['us'], '0.6667')         # (2/3 + 0 + 1 + 1) / 4

    def test_deaths(self):
        R = self.rows('deaths')
        r = R[('all', 'deaths launcher')]
        self.assertEqual((r['us'], r['them'], r['diff']), ('4.0', '3.0', '1.0'))
        self.assertEqual(R[('all', 'value lost')]['us'], '180.0')

    def test_basics_by_submission(self):
        R = self.rows('basics')
        self.assertEqual((R[('24', 'overruns')]['us'], R[('24', 'overruns')]['n_us']), ('0.3333', '3'))
        self.assertEqual(R[('25', 'overruns')]['us'], '2.0')
        self.assertEqual(R[('24', 'telemetry present')]['us'], '0.3333')
        self.assertEqual((R[('24', 'exception turns (tele)')]['us'], R[('24', 'exception turns (tele)')]['n_us']),
                         ('0.0', '1'))
        self.assertEqual(R[('25', 'exception turns (tele)')]['us'], '4.0')

    def test_filters(self):
        r = self.rows('econ', '--opponent', 'X')[('all', 'Mn@100 collected')]
        self.assertEqual((r['n_us'], r['us']), ('3', '93.3333'))
        self.assertEqual(self.rows('econ', '--last', '1')[('all', 'Mn@100 collected')]['us'], '120.0')
        self.assertEqual(self.rows('econ', '--last', '2')[('all', 'Mn@100 collected')]['n_us'], '2')
        self.assertEqual(self.rows('econ', '--map', 'Lake')[('all', 'Mn@100 collected')]['us'], '60.0')
        self.assertEqual(self.rows('econ', '--unranked')[('all', 'Mn@100 collected')]['us'], '80.0')
        self.assertEqual(self.rows('econ', '--since', '2026-10-02')[('all', 'Mn@100 collected')]['n_us'], '2')
        by = self.rows('econ', '--by', 'opponent')
        self.assertEqual((by[('X', 'Mn@100 collected')]['n_us'], by[('Y', 'Mn@100 collected')]['n_us']), ('3', '1'))

    def test_losses_anomalies_turning(self):
        L = list(csv.DictReader(io.StringIO(self.run_q('losses', '--csv'))))
        self.assertEqual([(r['match'], r['game'], r['worst'], r['worst_us'], r['worst_them'], r['worst_rel'])
                          for r in L], [('1', '1', 'eng won share', '0.0', '1.0', '-1.0')])   # L@250 is -0.6
        A = list(csv.DictReader(io.StringIO(self.run_q('anomalies', '--csv'))))
        self.assertEqual(sorted(r['kind'] for r in A), ['near', 'overruns', 'stall'])
        self.assertIn('stall', self.run_q('anomalies'))
        T = self.rows('turning')
        self.assertEqual((T[('all', 'turn_round p50')]['us'], T[('all', 'lock_round never')]['us']), ('100', '1.0'))
        self.assertEqual((T[('all', 'leader@100 by Mn wins')]['us'], T[('all', 'leader@100 by Mn wins')]['n_us']),
                         ('1.0', '3'))                                          # the 80/80 tie is excluded
        self.assertNotIn(('all', 'leader@100 by L wins'), T)                    # every game tied

    def test_field_not_built(self):
        buf = io.StringIO()
        self.assertEqual(self.q.main(['field', '--file', str(self.f)], out=buf), 2)


# ---------------------------------------------------------------- C.8 item 5: basics.py and delivery.py guards
class GuardsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = load('basics_g', 'basics.py')

    def test_old_rows_unchanged(self):
        rows = [{'over': '0', 'counters': 'ex=1;nm=2;', 'sym_wrong': '0', 'sym_first_decided': '40', 'near': '5'}] * 2
        self.assertEqual(self.b.battery(rows), [
            ('overruns', True, '0 robot-turns at the limit'), ('exceptions', False, '2 caught'),
            ('near misses', False, '4 turns above 90% (work before the fill)'),
            ('symmetry never wrong', True, '0 robots ended excluding the truth'),
            ('symmetry decided by r150', True, '2/2 games; never decided in 0')])

    def test_bcc_and_none_rows(self):
        bcc = {'tele': 'bcc', 'tele_exc_turns': '3', 'near': '7', 'over': '0', 'counters': '', 'sym_wrong': '0',
               'sym_first_decided': '-1'}
        res = {name: (p, d) for name, p, d in self.b.battery([bcc])}
        self.assertEqual(res['exceptions'], (False, '3 caught (tele_exc_turns in 1 games without strings)'))
        # replay-side near includes the end-of-turn fill: informational, not a bar, for games without strings
        self.assertEqual(res['near misses'][0], None)
        self.assertIn('replay-side near 7', res['near misses'][1])
        self.assertEqual(res['symmetry never wrong'], (None, '(no strings)'))
        self.assertEqual(res['symmetry decided by r150'], (None, '(no strings)'))
        none = dict(bcc, tele='none', tele_exc_turns='', near='0')
        res = {name: (p, d) for name, p, d in self.b.battery([none])}
        self.assertIsNone(res['exceptions'][0])
        self.assertIn('n/a', res['exceptions'][1])
        self.assertEqual(res['near misses'][0], None)

    def test_cli(self):
        d = Path(tempfile.mkdtemp(prefix='guards-'))
        hdr = 'team,over,near,counters,sym_wrong,sym_first_decided,tele,tele_exc_turns,rounds,anchors_built,' \
              'anchors_placed,coll_Mn,coll_Ad,still_L,still_C'
        (d / 'census.csv').write_text(hdr + '\nbot,0,0,,0,-1,bcc,0,300,1,1,10,10,0.5,0.5\n')
        r = subprocess.run([sys.executable, str(TOOLS / 'basics.py'), str(d / 'census.csv')], capture_output=True,
                           text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('n/a   symmetry never wrong', r.stdout)
        self.assertIn('PASS  exceptions', r.stdout)
        run = d / 'run'
        run.mkdir()
        (run / 'census.csv').write_text('cell_opponent,cell_map,cell_side,cell_seed,side,won,counters\nX,m,A,map,A,1,\n')
        r = subprocess.run([sys.executable, str(TOOLS / 'delivery.py'), str(run), str(run), '--metrics', 'won',
                            '--fire', 'pn'], capture_output=True, text=True)
        self.assertIn('fires pn       n/a (no counters in 1 games)', r.stdout)


# ---------------------------------------------------------------- C.8 item 6: integration on telemetry fixtures
class MatchReportFileTest(unittest.TestCase):
    """`file` on a fixture with indicators on (strings, BCC and dots) and, when part A's fixtures exist, indicators
    off (BCC only)."""
    def run_file(self, fix, label):
        if not fix.exists():
            self.skipTest(f'no fixture {fix}')
        tmp = Path(tempfile.mkdtemp(prefix='mr-file-'))
        mr = load(f'match_report_{label}', 'match_report.py')
        mr.ROOT = str(tmp)
        rc, out = quiet(mr.main, ['file', str(fix), '--us', 'A', '--label', label])
        self.assertEqual(rc, 0)
        return (tmp / f'matches/local/{label}.md').read_text(), json.loads((tmp / f'matches/local/{label}.json').read_text())

    def check_states(self, txt, d):
        t = d['games'][0]['tele']
        for typ in ('C', 'L', 'HQ'):
            self.assertTrue(t['states'].get(typ), typ)
        self.assertRegex(txt, r'  Carrier: open [A-Z] \.\d\d')
        self.assertRegex(txt, r'  HQ: [.a-z] \.\d\d')
        self.assertRegex(txt, r'  Launcher: all [A-Z] \.\d\d')

    def test_selfplay_fixture(self):
        txt, d = self.run_file(FIX_SELF, 'selfplay')
        self.check_states(txt, d)
        self.assertRegex(txt, r'Dots: trips \d+, cycle p50 \d+')
        self.assertRegex(txt, r'FIGHT \d+: riskier than stay \d\.\d\d')
        t = d['games'][0]['tele']
        self.assertEqual((t['status'], t['offset'], t['letter_mismatch']), ('both', 0, 0))
        self.assertGreater(t['trip']['n'], 0)
        self.assertGreater(t['fight']['n'], 0)
        self.assertLessEqual(len(txt.encode()), 8192)

    def test_tele_fixture(self):
        txt, d = self.run_file(FIX_TELE, 'tele')
        self.check_states(txt, d)
        self.assertIn('Dots: trips ', txt)
        self.assertIn('FIGHT ', txt)

    def test_tele_indoff_fixture(self):
        txt, d = self.run_file(FIX_TELE_OFF, 'indoff')
        self.check_states(txt, d)
        self.assertEqual(d['games'][0]['tele']['status'], 'bcc')
        self.assertIn('Dots: not available', txt)


# ---------------------------------------------------------------- C.8 item 7 (Tier 2 pieces): shadow, sweep, prune
class ShadowSweepPruneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mr = load('match_report_ssp', 'match_report.py')

    def test_verify_shadow(self):
        rep = {0: ('m', '300', 'aa', 'b1'), 1: ('m2', '200', 'bb', 'b2'), 2: ('m3', '100', 'cc', 'b3')}
        sh = {0: ('m', '300', 'aa', 'b1'), 1: ('m2', '200', 'bX', 'b2'), 2: ('m3', '100', 'cc', 'bZ')}
        self.assertEqual(self.mr.verify_shadow(rep, sh), ({0: 0, 2: 2}, [1], [2]))
        self.assertEqual(self.mr.verify_shadow(rep, {0: ('m3', '100', 'cc', 'b3')}), ({2: 0}, [0, 1], []))

    def test_shadow_line_on_real_replay(self):
        tmp = two_root()
        self.mr.ROOT = str(tmp)
        mj = tmp / 'm77.json'
        quiet(self.mr.main, ['match', str(FIX_TWO), '--match-json', str(mj), '--shadow', str(FIX_TWO)])
        quiet(self.mr.main, ['match', str(FIX_TWO), '--match-json', str(mj), '--shadow', str(FIX_TWO)])
        ls = jsonl(tmp / 'progress/telemetry.jsonl')
        self.assertEqual(len(ls), 2)                     # the repeated shadow run is idempotent too
        self.assertEqual(ls[1]['shadow']['verified_games'], [0, 1])
        self.assertEqual(ls[1]['shadow']['mismatch_games'], [])
        self.assertTrue(ls[1]['supersedes'])
        self.assertIn('Shadow: ', (tmp / 'research/matches/77.md').read_text())

    def test_sweep(self):
        tmp = Path(tempfile.mkdtemp(prefix='mr-sw-'))
        self.mr.ROOT = str(tmp)
        self.mr.append_line({'v': 1, 'match': 5, 'games': []})
        done, dl = [], []

        class C:
            me = staticmethod(lambda: {'id': 1})
            matches = staticmethod(lambda tid, pages: [{'id': 5, 'status': 'OK!'}, {'id': 7, 'status': 'ERR'},
                                                       {'id': 6, 'status': 'OK!'}, {'id': 8, 'status': 'OK!'}])

            @staticmethod
            def download(m, d):
                dl.append(m['id'])
                return f"{d}/{m['id']}.bc23"
        with mock.patch.object(self.mr, 'cmd_match', lambda p, m, team_id=None: done.append((m['id'], team_id))), \
                mock.patch.object(self.mr, 'free_gb', lambda path=None: 100.0):
            rc, out = quiet(self.mr.cmd_sweep, 1, 1, C)
        self.assertEqual((rc, dl, done), (0, [6], [(6, 1)]))
        self.assertIn('sweep: 1 reported, 1 left', out)
        with mock.patch.object(self.mr, 'free_gb', lambda path=None: 1.5):
            rc, out = quiet(self.mr.cmd_sweep, 1, 30, C)
        self.assertEqual((rc, dl), (1, [6]))
        self.assertIn('refusing', out)

    def test_prune(self):
        tmp = Path(tempfile.mkdtemp(prefix='mr-pr-'))
        self.mr.ROOT = str(tmp)
        now = time.time()
        for mid, res, an, age in ((1, 'win', ['tele_missing'], 20), (2, 'loss', [], 20), (3, 'win', ['near:1'], 31),
                                  (4, 'win', [], 10)):
            p = tmp / f'matches/{mid}/{mid}.bc23'
            p.parent.mkdir(parents=True)
            p.write_bytes(b'x')
            os.utime(p, (now - age * 86400, now - age * 86400))
            self.mr.append_line({'v': 1, 'match': mid, 'games': [{'result': res, 'anomalies': an}]})
        (tmp / 'matches/9').mkdir()
        (tmp / 'matches/9/9.bc23').write_bytes(b'x')                    # not reported: never removed
        os.utime(tmp / 'matches/9/9.bc23', (now - 90 * 86400, now - 90 * 86400))
        removed, _ = quiet(self.mr.prune, False, now)
        self.assertEqual(sorted(Path(p).name for p in removed), ['1.bc23', '3.bc23'])
        self.assertTrue((tmp / 'matches/2/2.bc23').exists())
        self.assertTrue((tmp / 'matches/9/9.bc23').exists())


if __name__ == '__main__':
    unittest.main()
