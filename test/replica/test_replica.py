#!/usr/bin/env python3
"""Unit tests for galaxy-lite (tools/replica): no games, no network. Run: python3 test/replica/test_replica.py
Ported from galaxy (f343088): compete/test_models.py MatchParticipantLinkedListTestCase and
MatchParticipantRatingFinalizationTestCase, teams/tests.py Generate4RegularGraphTestCase and AutoscrimmageTestCase.
Plus the hand tables of research/prior/GALAXY.md 2.1, the request rules, the worker's report protocol and engine-log
parsing (captured 3-map engine log), the export, the API, and a hostname guard."""
import csv
import io
import json
import os
import random
import re
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, 'tools'))
_TMP = tempfile.mkdtemp(prefix='replica-test-')
os.environ['REPLICA_HOME'] = _TMP

from replica import api, db, matchmaking, rating, web, worker  # noqa: E402
from replica.db import SaturnStatus  # noqa: E402
import elolib  # noqa: E402

FIXTURE = os.path.join(HERE, 'fixtures', 'engine-3maps.log')


def new_db(maps=('m0', 'm1', 'm2', 'm3', 'm4')):
    conn = db.connect(':memory:')
    db.init_episode(conn, maps=list(maps))
    return conn


def make_team(conn, name, n_submissions=1, accepted=True, status='R'):
    tid = db.create_team(conn, name, status=status)
    with db.tx(conn):
        for _ in range(n_submissions):
            db.insert_submission(conn, tid, 'pkg', status='OK!', accepted=accepted, binary_path='/nonexistent')
    return tid


def row(conn, table, pk):
    return conn.execute(f'SELECT * FROM {table} WHERE id=?', (pk,)).fetchone()


# ================================================================ penalized Elo (GALAXY.md 2.1 tables)
class RatingFormulaTest(unittest.TestCase):
    def test_constants(self):
        self.assertEqual((rating.TEAMS_ELO_INITIAL, rating.TEAMS_ELO_K, rating.TEAMS_ELO_SCALE,
                          rating.TEAMS_ELO_PENALTY), (1500.0, 24.0, 400.0, 0.85))

    def test_penalty_table(self):
        # n: 1500 * 0.85**n, as printed in GALAXY.md 2.1 (rounded there to the shown precision)
        table = {0: 1500, 1: 1275, 3: 921, 5: 666, 10: 295.3, 15: 131, 20: 58, 25: 26, 30: 11, 40: 2.3}
        for n, want in table.items():
            pen = 1500 - rating.penalized(1500, n)
            places = 1 if isinstance(want, float) else 0
            self.assertAlmostEqual(round(pen, places), want, places=6, msg=f'n={n}')

    def test_delta_table(self):
        # rows: mean_self - mean_opp; columns: win 3-0, win 2-1, lose 1-2, lose 0-3
        table = {0: (12.0, 4.0, -4.0, -12.0), 100: (8.6, 0.6, -7.4, -15.4), 200: (5.8, -2.2, -10.2, -18.2),
                 400: (2.2, -5.8, -13.8, -21.8)}
        for diff, cols in table.items():
            got = [round(rating.delta_mean(1500 + diff, 1500, w, l), 1) for w, l in ((3, 0), (2, 1), (1, 2), (0, 3))]
            self.assertEqual(got, list(cols), msg=f'diff={diff}')

    def test_new_team_value_zero_and_step(self):
        r = rating.Rating()
        self.assertEqual((r.mean, r.n, r.value), (1500.0, 0, 0.0))
        s = r.step([rating.Rating()], 1.0)
        self.assertEqual((s.mean, s.n), (1512.0, 1))
        self.assertAlmostEqual(s.value, 1512.0 - 1275.0)

    def test_two_player_zero_sum(self):
        a, b = rating.Rating(1600, 7), rating.Rating(1450, 3)
        da = a.step([b], 2 / 3).mean - a.mean
        db_ = b.step([a], 1 / 3).mean - b.mean
        self.assertAlmostEqual(da + db_, 0.0)

    def test_saved_value(self):
        conn = new_db()
        rid = db.insert_rating(conn, 1600.0, 10)
        self.assertAlmostEqual(db.get_rating(conn, rid)['value'], 1600 - 1500 * 0.85 ** 10)


# ================================================================ galaxy MatchParticipantLinkedListTestCase
class MatchParticipantLinkedListTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = new_db()
        self.t = [make_team(self.conn, f'team{i}') for i in (1, 2, 3)]

    def make_match(self):
        return db.insert_match(self.conn, alternate_order=False, is_ranked=False)

    def create(self, team):
        return db.insert_participant(self.conn, team_id=team, match_id=self.make_match(), player_index=0)

    def prev(self, pid):
        return row(self.conn, 'match_participant', pid)['previous_participation']

    def nxt(self, pid):
        r = self.conn.execute('SELECT id FROM match_participant WHERE previous_participation=?', (pid,)).fetchone()
        return r['id'] if r else None

    def test_individual_create_single_element(self):
        ps = [self.create(t) for t in self.t]
        for p in ps:
            self.assertIsNone(self.prev(p))
            self.assertIsNone(self.nxt(p))

    def test_individual_create_multiple_element(self):
        p1, p2, p3 = self.create(self.t[0]), self.create(self.t[1]), self.create(self.t[0])
        self.assertIsNone(self.prev(p1))
        self.assertEqual(self.nxt(p1), p3)
        self.assertIsNone(self.prev(p2))
        self.assertIsNone(self.nxt(p2))
        self.assertEqual(self.prev(p3), p1)
        self.assertIsNone(self.nxt(p3))

    def test_bulk_create_participation_single_previous_none(self):
        with db.tx(self.conn):
            for t in self.t:
                self.create(t)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM match_participant WHERE previous_participation '
                                           'IS NOT NULL').fetchone()[0], 0)

    def test_bulk_create_participation_multiple_previous_exists(self):
        with db.tx(self.conn):
            for t in self.t:
                self.create(t)
        with db.tx(self.conn):
            objs = [self.create(t) for t in self.t]
        for o in objs:
            r = row(self.conn, 'match_participant', o)
            prev = row(self.conn, 'match_participant', r['previous_participation'])
            self.assertEqual(r['team'], prev['team'])
            self.assertIsNone(prev['previous_participation'])


# ================================================================ galaxy MatchParticipantRatingFinalizationTestCase
class MatchParticipantRatingFinalizationTestCase(unittest.TestCase):
    """Test suite for the delayed rating finalization algorithm (9 cases, ported one to one).
    Partitions: match type (ranked, unranked) x match status (completed, failed, in progress) x previous
    participation (finalized, not finalized, does not exist)."""

    def setUp(self):
        self.conn = new_db()
        self.t1, self.t2, self.t3 = (make_team(self.conn, n) for n in ('team1', 'team2', 'team3'))

    # helpers mirroring the Django calls
    def rating_create(self, **kw):
        return db.insert_rating(self.conn, **kw)

    def match_create(self, is_ranked, status):
        return db.insert_match(self.conn, alternate_order=True, is_ranked=is_ranked, status=status)

    def mp_create(self, team, match, player_index, score=None, rating_id=None):
        with db.tx(self.conn):
            return db.insert_participant(self.conn, team_id=team, match_id=match, player_index=player_index,
                                         score=score, rating_id=rating_id)

    def set_status(self, match, status):   # m.status = ...; m.save()
        self.conn.execute('UPDATE match SET status=? WHERE id=?', (status, match))

    def update(self, match):                 # m.try_rating_update()
        rating.match_try_rating_update(self.conn, match)

    def mp(self, pid):                       # refresh_from_db()
        return row(self.conn, 'match_participant', pid)

    def r(self, rid):
        return None if rid is None else db.get_rating(self.conn, rid)

    def profile_rating(self, team):
        return row(self.conn, 'team', team)['rating_id']

    def test_finalize_ranked_completed_previous_ready(self):
        r1 = self.rating_create(n=10)
        r2 = self.rating_create(n=20)
        m1 = self.match_create(False, SaturnStatus.COMPLETED)
        self.mp_create(self.t1, m1, 0, score=1, rating_id=r1)
        self.mp_create(self.t2, m1, 1, score=0, rating_id=r2)
        m2 = self.match_create(True, SaturnStatus.RUNNING)
        red = self.mp_create(self.t1, m2, 0, score=1)
        self.mp_create(self.t3, m2, 1, score=0)
        self.set_status(m2, SaturnStatus.COMPLETED)
        self.update(m2)
        red = self.mp(red)
        # Expect rating increase after win
        self.assertIsNotNone(red['rating_id'])
        self.assertGreater(self.r(red['rating_id'])['mean'], rating.get_old_rating(self.conn, red).mean)
        self.assertEqual(self.r(red['rating_id'])['n'], self.r(r1)['n'] + 1)
        self.assertEqual(self.profile_rating(self.t1), red['rating_id'])

    def test_finalize_ranked_completed_previous_not_ready(self):
        m1 = self.match_create(True, SaturnStatus.RUNNING)
        self.mp_create(self.t1, m1, 0)
        self.mp_create(self.t2, m1, 1)
        m2 = self.match_create(True, SaturnStatus.RUNNING)
        red = self.mp_create(self.t1, m2, 0, score=1)
        self.mp_create(self.t3, m2, 1, score=0)
        self.set_status(m2, SaturnStatus.COMPLETED)
        self.update(m2)
        # Expect no rating because previous not ready
        self.assertIsNone(self.mp(red)['rating_id'])

    def test_finalize_ranked_completed_previous_nonexistent(self):
        m1 = self.match_create(True, SaturnStatus.COMPLETED)
        red = self.mp_create(self.t1, m1, 0, score=1)
        self.mp_create(self.t2, m1, 1, score=0)
        self.set_status(m1, SaturnStatus.COMPLETED)
        self.update(m1)
        red = self.mp(red)
        # Expect rating increase after win
        self.assertIsNotNone(red['rating_id'])
        self.assertGreater(self.r(red['rating_id'])['mean'], rating.get_old_rating(self.conn, red).mean)
        self.assertEqual(self.r(red['rating_id'])['n'], 1)
        self.assertEqual(self.profile_rating(self.t1), red['rating_id'])

    def test_finalize_ranked_failed_previous_ready(self):
        r1 = self.rating_create(n=10)
        r2 = self.rating_create(n=20)
        m1 = self.match_create(False, SaturnStatus.COMPLETED)
        red1 = self.mp_create(self.t1, m1, 0, score=1, rating_id=r1)
        self.mp_create(self.t2, m1, 1, score=0, rating_id=r2)
        m2 = self.match_create(True, SaturnStatus.RUNNING)
        red2 = self.mp_create(self.t1, m2, 0)
        self.mp_create(self.t3, m2, 1)
        self.set_status(m2, SaturnStatus.ERRORED)
        self.update(m2)
        # Expect no change because no result
        self.assertEqual(self.mp(red1)['rating_id'], self.mp(red2)['rating_id'])

    def test_finalize_ranked_failed_previous_not_ready(self):
        m1 = self.match_create(True, SaturnStatus.RUNNING)
        self.mp_create(self.t1, m1, 0)
        self.mp_create(self.t2, m1, 1)
        m2 = self.match_create(True, SaturnStatus.RUNNING)
        red = self.mp_create(self.t1, m2, 0)
        self.mp_create(self.t3, m2, 1)
        self.set_status(m2, SaturnStatus.ERRORED)
        self.update(m2)
        # Expect no rating because previous not ready
        self.assertIsNone(self.mp(red)['rating_id'])

    def test_finalize_ranked_inprogress_previous_ready(self):
        r1 = self.rating_create(n=10)
        r2 = self.rating_create(n=20)
        m1 = self.match_create(False, SaturnStatus.COMPLETED)
        self.mp_create(self.t1, m1, 0, score=1, rating_id=r1)
        self.mp_create(self.t2, m1, 1, score=0, rating_id=r2)
        m2 = self.match_create(True, SaturnStatus.CREATED)
        red = self.mp_create(self.t1, m2, 0)
        self.mp_create(self.t3, m2, 1)
        self.set_status(m2, SaturnStatus.RUNNING)
        self.update(m2)
        # Expect no rating because no result
        self.assertIsNone(self.mp(red)['rating_id'])

    def test_finalize_unranked_completed_previous_ready(self):
        r1 = self.rating_create(n=10)
        r2 = self.rating_create(n=20)
        m1 = self.match_create(False, SaturnStatus.COMPLETED)
        red1 = self.mp_create(self.t1, m1, 0, score=1, rating_id=r1)
        self.mp_create(self.t2, m1, 1, score=0, rating_id=r2)
        m2 = self.match_create(False, SaturnStatus.RUNNING)
        red2 = self.mp_create(self.t1, m2, 0, score=1)
        self.mp_create(self.t3, m2, 1, score=0)
        self.set_status(m2, SaturnStatus.COMPLETED)
        self.update(m2)
        # Expect no change because unranked
        self.assertEqual(self.mp(red1)['rating_id'], self.mp(red2)['rating_id'])
        self.assertEqual(self.profile_rating(self.t1), self.mp(red2)['rating_id'])

    def test_finalize_unranked_completed_previous_not_ready(self):
        m1 = self.match_create(True, SaturnStatus.RUNNING)
        self.mp_create(self.t1, m1, 0)
        self.mp_create(self.t2, m1, 1)
        m2 = self.match_create(False, SaturnStatus.RUNNING)
        red = self.mp_create(self.t1, m2, 0, score=1)
        self.mp_create(self.t3, m2, 1, score=0)
        self.set_status(m2, SaturnStatus.COMPLETED)
        self.update(m2)
        # Expect no rating because previous not ready
        self.assertIsNone(self.mp(red)['rating_id'])

    def test_finalize_unranked_completed_previous_nonexistent(self):
        m1 = self.match_create(False, SaturnStatus.RUNNING)
        red = self.mp_create(self.t1, m1, 0, score=1)
        self.mp_create(self.t2, m1, 1, score=0)
        self.set_status(m1, SaturnStatus.COMPLETED)
        self.update(m1)
        red = self.mp(red)
        # Expect no change because unranked
        self.assertIsNotNone(red['rating_id'])
        self.assertEqual(self.r(red['rating_id'])['value'], rating.get_old_rating(self.conn, red).value)
        self.assertEqual(self.r(red['rating_id'])['n'], 0)
        self.assertEqual(self.r(self.profile_rating(self.t1))['value'], self.r(red['rating_id'])['value'])


# ================================================================ the rating pump (creation order)
class RatingPumpTest(unittest.TestCase):
    def setUp(self):
        self.conn = new_db()
        self.a, self.b, self.c = (make_team(self.conn, n) for n in 'abc')

    def ranked(self, x, y):
        with db.tx(self.conn):
            m = db.insert_match(self.conn, alternate_order=True, is_ranked=True, status='QUE')
            db.insert_participant(self.conn, team_id=x, match_id=m, player_index=0)
            db.insert_participant(self.conn, team_id=y, match_id=m, player_index=1)
            db.set_match_maps(self.conn, m, [1, 2, 3])
        return m

    def finish(self, m, scores):
        self.conn.execute("UPDATE match SET status='RUN' WHERE id=?", (m,))
        worker.report(self.conn, 'match', m, SaturnStatus.COMPLETED, scores=scores)

    def final(self):
        return {t: (round(r['mean'], 9), r['n']) for t in (self.a, self.b, self.c)
                for r in [db.get_rating(self.conn, row(self.conn, 'team', t)['rating_id'])]}

    def play(self, order):
        ms = [self.ranked(self.a, self.b), self.ranked(self.b, self.c), self.ranked(self.a, self.c),
              self.ranked(self.a, self.b)]
        results = [[3, 0], [1, 2], [2, 1], [0, 3]]
        for i in order:
            self.finish(ms[i], results[i])
        return ms

    def test_completion_order_does_not_matter(self):
        self.play([0, 1, 2, 3])
        in_order = self.final()
        self.setUp()
        self.play([3, 2, 1, 0])
        self.assertEqual(self.final(), in_order)
        self.assertEqual(in_order[self.a][1], 3)

    def test_blocked_chain_until_previous_finalizes(self):
        m1 = self.ranked(self.a, self.b)
        m2 = self.ranked(self.a, self.c)
        self.finish(m2, [3, 0])
        p = db.participants(self.conn, m2)
        self.assertIsNone(p[0]['rating_id'])          # a's previous (m1) is not finalized
        self.assertIsNone(p[1]['rating_id'])          # c waits too: its opponent's old rating is unknown
        self.conn.execute("UPDATE match SET status='RUN' WHERE id=?", (m1,))
        for _ in range(db.SATURN_MAX_FAILURES):       # m1 fails 5 times -> ERR -> unranked for ratings
            worker.report(self.conn, 'match', m1, SaturnStatus.RETRY)
        self.assertEqual(row(self.conn, 'match', m1)['status'], SaturnStatus.ERRORED)
        p1 = db.participants(self.conn, m1)
        self.assertEqual(db.get_rating(self.conn, p1[0]['rating_id'])['n'], 0)
        p = db.participants(self.conn, m2)
        self.assertEqual(db.get_rating(self.conn, p[0]['rating_id'])['n'], 1)
        self.assertAlmostEqual(db.get_rating(self.conn, p[0]['rating_id'])['mean'], 1512.0)
        self.assertAlmostEqual(db.get_rating(self.conn, p[1]['rating_id'])['mean'], 1488.0)


# ================================================================ galaxy Generate4RegularGraphTestCase
class Generate4RegularGraphTestCase(unittest.TestCase):
    def inner_test(self, n):
        edges = matchmaking.generate_4regular_graph(n)
        # Canonicalize
        edges = [(min(u, v), max(u, v)) for u, v in edges]
        # Graph is valid
        self.assertTrue(all(0 <= u < v < n for u, v in edges))
        self.assertEqual(len(set(edges)), len(edges))
        # Graph is 4-regular
        deg = [0] * n
        for u, v in edges:
            deg[u] += 1
            deg[v] += 1
        self.assertEqual(deg, [4] * n)
        # Graph satisfies specified properties
        self.assertTrue(all(abs(u - v) <= 4 for u, v in edges))
        nb = {i: set() for i in range(n)}
        for u, v in edges:
            nb[u].add(v)
            nb[v].add(u)
        for i in range(1, n - 1):
            self.assertLess(min(nb[i]), i)
            self.assertGreater(max(nb[i]), i)

    def test_graph_valid_small(self):
        for n in range(5, 35):
            with self.subTest(n=n):
                random.seed(1)
                # Repeat several times because the graph is random.
                for repetition in range(100):
                    self.inner_test(n)

    def test_graph_valid_large(self):
        random.seed(1)
        for repetition in range(10):
            self.inner_test(500)

    def test_too_small(self):
        with self.assertRaises(ValueError):
            matchmaking.generate_4regular_graph(4)


# ================================================================ galaxy AutoscrimmageTestCase (core partitions)
class AutoscrimTest(unittest.TestCase):
    def test_many_regular_teams(self):
        n = 50
        conn = new_db(maps=('map0', 'map1', 'map2'))
        ts = [make_team(conn, f'team{i}') for i in range(n)]
        ms = matchmaking.autoscrim(conn, best_of=3)
        self.assertEqual(len(ms), 2 * n)
        self.assertEqual(conn.execute('SELECT COUNT(*) FROM match').fetchone()[0], 2 * n)
        for t in ts:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM match_participant WHERE team=?', (t,)).fetchone()[0], 4)
        for m in ms:
            r = row(conn, 'match', m)
            self.assertEqual(len(db.match_map_names(conn, m)), 3)
            self.assertEqual((r['status'], r['is_ranked'], r['alternate_order'], r['source']),
                             ('QUE', 1, 1, 'autoscrim'))
        for name in ('map0', 'map1', 'map2'):
            self.assertTrue(conn.execute('SELECT 1 FROM match_map JOIN map ON map.id=match_map.map WHERE map.name=?',
                                         (name,)).fetchone())
        for p in conn.execute('SELECT * FROM match_participant'):
            self.assertEqual(p['team'], row(conn, 'submission', p['submission'])['team'])

    def test_neighbours_by_rating_mean(self):
        # with 12 teams of distinct means, every autoscrim edge joins teams at most 4 rank places apart
        conn = new_db()
        ts = [make_team(conn, f't{i}') for i in range(12)]
        with db.tx(conn):
            for i, t in enumerate(ts):
                rid = db.insert_rating(conn, 2000 - 10 * i, 0)
                conn.execute('UPDATE team SET rating_id=? WHERE id=?', (rid, t))
        rank = {t: i for i, t in enumerate(ts)}
        for m in matchmaking.autoscrim(conn, best_of=3):
            a, b = [p['team'] for p in db.participants(conn, m)]
            self.assertLessEqual(abs(rank[a] - rank[b]), 4)

    def test_teams_count_0_and_1(self):
        conn = new_db()
        self.assertEqual(matchmaking.autoscrim(conn, best_of=3), [])
        make_team(conn, 'only')
        self.assertEqual(matchmaking.autoscrim(conn, best_of=3), [])

    def test_teams_count_2_to_4_round_robin(self):
        for n in (2, 3, 4):
            conn = new_db()
            ts = [make_team(conn, f't{i}') for i in range(n)]
            ms = matchmaking.autoscrim(conn, best_of=3)
            self.assertEqual(len(ms), n * (n - 1) // 2)
            pairs = {frozenset(p['team'] for p in db.participants(conn, m)) for m in ms}
            self.assertEqual(len(pairs), len(ms))
            self.assertTrue(all(len(p) == 2 for p in pairs))

    def test_excluded_teams_and_maps(self):
        conn = new_db(maps=('pub0', 'pub1', 'pub2'))
        conn.execute("INSERT INTO map(episode, name, is_public) VALUES ('bc23', 'secret', 0)")
        good = [make_team(conn, f'g{i}') for i in range(3)]
        make_team(conn, 'staff', status='S')
        make_team(conn, 'inactive', status='X')
        make_team(conn, 'rejected', accepted=False)
        make_team(conn, 'nosub', n_submissions=0)
        ms = matchmaking.autoscrim(conn, best_of=3)
        teams = {p['team'] for m in ms for p in db.participants(conn, m)}
        self.assertEqual(teams, set(good))
        for m in ms:
            self.assertNotIn('secret', db.match_map_names(conn, m))

    def test_not_enough_maps(self):
        conn = new_db(maps=('a', 'b'))
        make_team(conn, 'x')
        make_team(conn, 'y')
        with self.assertRaises(ValueError):
            matchmaking.autoscrim(conn, best_of=3)

    def test_best_of_must_be_a_positive_integer(self):
        # Regression (review 2026-10-07): galaxy's AutoscrimSerializer has best_of = IntegerField(min_value=1). The
        # replica took best_of=0 and queued matches with no maps (each failed 5 times and ended ERR); '3' raised
        # TypeError. Both the API body and `config autoscrim_best_of=0` reached it.
        conn = new_db()
        for i in range(3):
            make_team(conn, f't{i}')
        for bad in (0, -1, '0', 'x', '1.5', True):
            with self.subTest(best_of=bad), self.assertRaises(ValueError):
                matchmaking.autoscrim(conn, best_of=bad)
        db.set_episode(conn, autoscrim_best_of=0)
        with self.assertRaises(ValueError):
            matchmaking.autoscrim(conn)
        self.assertEqual(conn.execute('SELECT COUNT(*) FROM match').fetchone()[0], 0)
        for ok in ('2', 2.0):
            with self.subTest(best_of=ok):
                ms = matchmaking.autoscrim(conn, best_of=ok)
                self.assertEqual({len(db.match_map_names(conn, m)) for m in ms}, {2})


# ================================================================ scrimmage requests and their rules
class RequestRulesTest(unittest.TestCase):
    def setUp(self):
        self.conn = new_db(maps=[f'm{i}' for i in range(8)])
        self.lo = make_team(self.conn, 'low')
        self.hi = make_team(self.conn, 'high')
        self.staff = make_team(self.conn, 'staff', status='S')
        with db.tx(self.conn):   # 'high' has a better displayed rating
            rid = db.insert_rating(self.conn, 1700, 10)
            self.conn.execute('UPDATE team SET rating_id=? WHERE id=?', (rid, self.hi))

    def rules(self, on=True, **kw):
        db.set_episode(self.conn, enforce_rules=1 if on else 0, **kw)

    def req(self, by, to, ranked=True, order='?', maps=None):
        return matchmaking.create_request(self.conn, requested_by=by, requested_to=to, is_ranked=ranked,
                                          player_order=order, map_names=maps)

    def refused(self, msg, http=None, **kw):
        with self.assertRaises(matchmaking.RequestError) as cm:
            self.req(**kw)
        self.assertIn(msg, str(cm.exception))
        if http:
            self.assertEqual(cm.exception.http, http)

    def test_always_checked(self):
        self.rules(False)
        self.refused('yourself', by='low', to='low')
        self.refused('invalid', by='low', to='high', ranked=False, maps=['nope'])
        nosub = make_team(self.conn, 'nosub', n_submissions=0)
        self.refused('No valid opponent', by='low', to=nosub)
        self.refused('no accepted submission', by=nosub, to='low')

    def test_ranked_rules_on(self):
        self.rules(True)
        self.refused('must be empty for ranked', by='low', to='high', maps=['m0', 'm1', 'm2'])
        self.refused('shuffled order', by='low', to='high', order='+')
        self.refused('against staff must be unranked', by='low', to='staff')
        self.refused('Staff can only have unranked', by='staff', to='low')
        self.refused('ranked lower than you', http=409, by='high', to='low')
        self.refused('must not be empty', by='low', to='high', ranked=False)
        rid, st, mid = self.req('low', 'high')
        self.assertEqual(st, 'Y')
        maps = db.match_map_names(self.conn, mid)
        self.assertEqual(len(maps), 3)
        self.assertEqual(len(set(maps)), 3)
        self.assertTrue(row(self.conn, 'match', mid)['alternate_order'])

    def test_ranked_disabled(self):
        self.rules(True, is_allowed_ranked_scrimmage=0)
        self.refused('disabled', http=409, by='low', to='high')
        self.req('low', 'high', ranked=False, maps=['m0'])

    def test_hourly_limit(self):
        self.rules(True, unranked_scrimmage_hourly_limit=4)
        # each accepted request counts twice (the request and the match it created): GALAXY.md section 7 item 7
        self.req('low', 'high', ranked=False, maps=['m0'])
        self.req('low', 'high', ranked=False, maps=['m1'])
        self.refused('too many scrimmages in the past hour', http=429, by='low', to='high', ranked=False,
                     maps=['m2'])

    def test_pair_cap(self):
        self.rules(True, ranked_scrimmage_hourly_limit=100)
        with db.tx(self.conn):   # three active ranked matches between the pair (e.g. from autoscrim)
            for _ in range(3):
                m = db.insert_match(self.conn, alternate_order=True, is_ranked=True, status='QUE')
                db.insert_participant(self.conn, team_id=self.lo, match_id=m, player_index=0)
                db.insert_participant(self.conn, team_id=self.hi, match_id=m, player_index=1)
        self.refused('too many running scrimmages', http=409, by='low', to='high')

    def test_rules_off_allows_scripting(self):
        self.rules(False)
        rid, st, mid = self.req('high', 'low', ranked=True, order='+', maps=['m5', 'm6'])
        self.assertEqual(st, 'Y')
        self.assertEqual(db.match_map_names(self.conn, mid), ['m5', 'm6'])
        ps = db.participants(self.conn, mid)
        self.assertEqual([p['team'] for p in ps], [self.hi, self.lo])   # requester first
        self.assertFalse(row(self.conn, 'match', mid)['alternate_order'])
        rid, st, mid = self.req('high', 'low', ranked=False, order='-')
        self.assertEqual([p['team'] for p in db.participants(self.conn, mid)], [self.lo, self.hi])
        self.assertEqual(len(db.match_map_names(self.conn, mid)), 3)

    def test_manual_and_auto_reject(self):
        self.rules(False)
        self.conn.execute("UPDATE team SET auto_accept_reject_unranked='M', auto_accept_reject_ranked='R' "
                          'WHERE id=?', (self.hi,))
        rid, st, mid = self.req('low', 'high', ranked=False, maps=['m0'])
        self.assertEqual((st, mid), ('P', None))
        (mid,) = matchmaking.accept(self.conn, [rid])
        self.assertEqual(row(self.conn, 'scrimmage_request', rid)['status'], 'Y')
        self.assertEqual(row(self.conn, 'match', mid)['status'], 'QUE')
        self.assertEqual(matchmaking.accept(self.conn, [rid]), [])          # no longer pending
        rid, st, mid = self.req('low', 'high', ranked=True)
        self.assertEqual((st, mid), ('N', None))


# ================================================================ worker: engine command, log parsing, protocol
class WorkerTest(unittest.TestCase):
    def setUp(self):
        with open(FIXTURE) as fh:
            self.log = fh.read()
        self.conn = new_db(maps=('maptestsmall', 'SmallElements', 'Pizza', 'Other'))
        self.a = make_team(self.conn, 'us:bot')
        self.b = make_team(self.conn, 'us:examplefuncsplayer')

    def match(self, maps=('maptestsmall', 'SmallElements', 'Pizza'), ranked=True):
        ids = db.public_maps(self.conn)
        with db.tx(self.conn):
            m = db.insert_match(self.conn, alternate_order=True, is_ranked=ranked, status='QUE')
            db.insert_participant(self.conn, team_id=self.a, match_id=m, player_index=0)
            db.insert_participant(self.conn, team_id=self.b, match_id=m, player_index=1)
            db.set_match_maps(self.conn, m, [ids[x] for x in maps])
        return m

    def test_saturn_regex_on_captured_log(self):
        self.assertEqual(worker.saturn_scores(self.log), [3, 0])

    def test_parse_games_on_captured_log(self):
        g = worker.parse_games(self.log, ['maptestsmall', 'SmallElements', 'Pizza'], True)
        self.assertEqual([x['map'] for x in g], ['maptestsmall', 'SmallElements', 'Pizza'])
        self.assertEqual([x['winner'] for x in g], ['A', 'A', 'A'])
        self.assertEqual([x['round'] for x in g], [286, 145, 179])
        self.assertEqual([x['reversed'] for x in g], [False, True, False])
        self.assertTrue(all(x['reason'] == 'The winning team won by capturing 75% of sky islands.' for x in g))
        g = worker.parse_games(self.log, ['maptestsmall', 'SmallElements', 'Pizza'], False)
        self.assertEqual([x['reversed'] for x in g], [False, False, False])

    def test_parse_b_wins_and_noise(self):
        log = (self.log.replace('bot (A) wins (round 145)', 'examplefuncsplayer (B) wins (round 2000)', 1)
               .replace('capturing 75% of sky islands.', 'tiebreakers (more reality anchors).', 1))
        log = '[server] noise (A) wins (round 3) trailing\nrobot says (B) wins (round 9)\n' + log
        self.assertEqual(worker.saturn_scores(log), [2, 1])
        g = worker.parse_games(log, [], True)
        self.assertEqual([(x['winner'], x['round']) for x in g], [('A', 286), ('B', 2000), ('A', 179)])
        self.assertEqual(g[0]['reason'], 'The winning team won by tiebreakers (more reality anchors).')

    def test_match_command(self):
        eng = worker.Engine('/jdk/bin/java', '/e/patch:/e/battlecode23-3.0.15.jar', '/e/j.jar', 'x')
        cmd = worker.match_command(eng, names=['us:bot', 'X.y'], urls=['/c1', '/c2'], packages=['bot', 'y'],
                                   maps=['A', 'B', 'C'], alternate_order=True, replay='/r/u.bc23', timeout=5400)
        s = ' '.join(cmd)
        for flag in ('-Dbc.server.websocket=false', '-Dbc.server.alternate-order=true', '-Dbc.game.maps=A,B,C',
                     '-Dbc.engine.show-indicators=false', '-Dbc.server.validate-maps=true',
                     '-Dbc.server.save-file=/r/u.bc23', '-Dbc.game.team-a=us:bot', '-Dbc.game.team-b.package=y',
                     '-Dbc.server.mode=headless', 'battlecode.server.Main -c=-'):
            self.assertIn(flag, s)
        self.assertEqual(cmd[:3], ['timeout', '5400', '/jdk/bin/java'])
        self.assertNotIn('bc.game.seed', s)
        self.assertNotIn('best-of-three', s)

    def test_report_ok_stores_scores_games_and_rates(self):
        m = self.match()
        job = worker.claim(self.conn, 'match', 'host:1:0')
        self.assertEqual((job['id'], job['status']), (m, 'RUN'))
        self.assertIsNone(worker.claim(self.conn, 'match', 'host:1:1'))
        games = worker.parse_games(self.log, db.match_map_names(self.conn, m), True)
        st = worker.report(self.conn, 'match', m, 'OK!', scores=worker.saturn_scores(self.log), games=games)
        self.assertEqual(st, 'OK!')
        self.assertEqual([p['score'] for p in db.participants(self.conn, m)], [3, 0])
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM game WHERE match=?', (m,)).fetchone()[0], 3)
        ra = db.get_rating(self.conn, row(self.conn, 'team', self.a)['rating_id'])
        self.assertEqual((ra['mean'], ra['n']), (1512.0, 1))
        with self.assertRaises(worker.AlreadyFinalized):
            worker.report(self.conn, 'match', m, 'OK!', scores=[3, 0])

    def test_zero_or_partial_scores_are_retry(self):
        m = self.match()
        worker.claim(self.conn, 'match', 'h:1:0')
        self.assertEqual(worker.report(self.conn, 'match', m, 'OK!', scores=[0, 0]), 'TRY')
        self.assertEqual(row(self.conn, 'match', m)['num_failures'], 1)
        worker.claim(self.conn, 'match', 'h:1:0')
        self.assertEqual(worker.report(self.conn, 'match', m, 'OK!', scores=[1, 1]), 'TRY')
        self.assertEqual([p['score'] for p in db.participants(self.conn, m)], [None, None])
        self.assertIn('treated as TRY', row(self.conn, 'match', m)['logs'])

    def test_five_failures_then_err_interrupt_not_counted(self):
        m = self.match()
        worker.claim(self.conn, 'match', 'h:1:0')
        worker.report(self.conn, 'match', m, 'TRY', interrupted=True)
        self.assertEqual(row(self.conn, 'match', m)['num_failures'], 0)
        for i in range(4):
            self.assertEqual(worker.report(self.conn, 'match', m, 'TRY'), 'TRY')
        self.assertEqual(worker.report(self.conn, 'match', m, 'TRY'), 'ERR')
        r = row(self.conn, 'match', m)
        self.assertEqual((r['status'], r['num_failures']), ('ERR', 5))
        self.assertIn('[siarnaq] Maximum retries reached.', r['logs'])
        # ERR = unranked for ratings: both keep their rating, n unchanged
        self.assertTrue(all(db.get_rating(self.conn, p['rating_id'])['n'] == 0
                            for p in db.participants(self.conn, m)))

    def test_reaper(self):
        m1, m2 = self.match(), self.match()
        worker.claim(self.conn, 'match', 'thishost:999999999:0')    # a dead worker on this host
        worker.claim(self.conn, 'match', 'otherhost:1:0')
        self.conn.execute('UPDATE match SET claimed_at=? WHERE id=?', (db.ago(hours=10), m2))
        reaped = dict(worker.reap_stale(self.conn, timeout_per_game=60, host='thishost'))
        self.assertEqual(set(reaped), {m1, m2})
        self.assertEqual((row(self.conn, 'match', m1)['status'], row(self.conn, 'match', m1)['num_failures']),
                         ('TRY', 0))
        self.assertEqual((row(self.conn, 'match', m2)['status'], row(self.conn, 'match', m2)['num_failures']),
                         ('TRY', 1))
        self.assertEqual(worker.reap_stale(self.conn, timeout_per_game=60, host='thishost'), [])

    def test_unzip_checked_refuses_zip_slip(self):
        d = tempfile.mkdtemp(dir=_TMP)
        z = os.path.join(d, 'evil.zip')
        import zipfile
        with zipfile.ZipFile(z, 'w') as zf:
            zf.writestr('../escape.txt', 'x')
        self.assertIn('illegal path', worker.unzip_checked(z, os.path.join(d, 'out')))
        self.assertFalse(os.path.exists(os.path.join(d, 'escape.txt')))

    def test_submit_prebuilt_snapshot(self):
        cls = tempfile.mkdtemp(dir=_TMP)
        os.makedirs(os.path.join(cls, 'bot'))
        with open(os.path.join(cls, 'bot', 'RobotPlayer.class'), 'wb') as fh:
            fh.write(b'\xca\xfe')
        sid = worker.submit(self.conn, 'us:bot', 'bot', prebuilt_classes=cls)
        s = row(self.conn, 'submission', sid)
        self.assertEqual((s['status'], s['accepted']), ('OK!', 1))
        self.assertTrue(s['binary_path'].startswith(_TMP) and s['binary_path'] != cls)    # snapshot for us:*
        self.assertTrue(os.path.isfile(os.path.join(s['binary_path'], 'bot', 'RobotPlayer.class')))
        with self.assertRaises(ValueError):
            worker.submit(self.conn, 'us:bot', 'nopkg', prebuilt_classes=cls)

    @unittest.skipUnless(os.path.isfile(os.path.join(REPO, 'engine', 'battlecode23-3.0.15.jar')), 'no engine jar')
    def test_compile_source_submission(self):
        """javac -proc:none (tools/lib.sh compile_src) + battlecode.instrumenter.Verifier; failures are OK! with
        accepted=false (saturn VerifySubmission), and the binary path is recorded for the runner."""
        eng = worker.Engine.from_lib()
        good = worker.submit(self.conn, 'us:examplefuncsplayer', 'examplefuncsplayer',
                             source=os.path.join(REPO, 'src'))
        bad_src = tempfile.mkdtemp(dir=_TMP)
        os.makedirs(os.path.join(bad_src, 'broken'))
        with open(os.path.join(bad_src, 'broken', 'RobotPlayer.java'), 'w') as fh:
            fh.write('package broken; public class RobotPlayer { int x = ; }\n')
        bad = worker.submit(self.conn, 'us:bot', 'broken', source=bad_src)
        missing = worker.submit(self.conn, 'us:bot', 'nosuchpkg', source=bad_src)
        for _ in range(3):
            worker.compile_submission(self.conn, worker.claim(self.conn, 'submission', 'h:1:0'), eng)
        g, b, m = (row(self.conn, 'submission', s) for s in (good, bad, missing))
        self.assertEqual((g['status'], g['accepted']), ('OK!', 1))
        self.assertTrue(os.path.isfile(os.path.join(g['binary_path'], 'examplefuncsplayer', 'RobotPlayer.class')))
        self.assertEqual((b['status'], b['accepted']), ('OK!', 0))
        self.assertIn('compile failed', b['logs'])
        self.assertEqual((m['status'], m['accepted']), ('OK!', 0))
        self.assertEqual(db.active_submission(self.conn, self.b), good)

    def test_export_games(self):
        m = self.match()
        worker.claim(self.conn, 'match', 'h:1:0')
        worker.report(self.conn, 'match', m, 'OK!', scores=[3, 0],
                      games=worker.parse_games(self.log, db.match_map_names(self.conn, m), True))
        out = os.path.join(tempfile.mkdtemp(dir=_TMP), 'games.csv')
        self.assertEqual(api.export_games(self.conn, out), 3)
        self.assertEqual(api.export_games(self.conn, out), 0)      # already exported
        with open(out) as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(list(rows[0].keys()), api.GAMES_HDR)
        self.assertEqual([(r['run'], r['seq'], r['teamA'], r['teamB'], r['map'], r['winner'], r['rounds'], r['seed'])
                          for r in rows],
                         [(f'replica-{m}', '1', 'us:bot', 'us:examplefuncsplayer', 'maptestsmall', 'A', '286', 'map'),
                          (f'replica-{m}', '2', 'us:bot', 'us:examplefuncsplayer', 'SmallElements', 'A', '145', 'map-rev'),
                          (f'replica-{m}', '3', 'us:bot', 'us:examplefuncsplayer', 'Pizza', 'A', '179', 'map')])
        self.assertTrue(all(r['reason'] in {c for _, c in elolib.REASONS} | {'OTHER'} for r in rows), rows)
        self.assertNotIn('OTHER', [r['reason'] for r in rows])
        self.assertEqual(api.export_games(self.conn, out, all_games=True), 3)


# ================================================================ API (loopback, ephemeral port)
class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import http.server
        cls.dbfile = os.path.join(_TMP, 'api.db')
        os.environ['REPLICA_HOME'] = _TMP
        conn = db.connect(cls.dbfile)
        db.init_episode(conn, maps=['m0', 'm1', 'm2', 'm3'])
        make_team(conn, 'alpha')
        make_team(conn, 'beta')
        conn.close()
        cls._orig = db.db_path
        db.db_path = lambda: cls.dbfile
        cls.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), api.Handler)
        cls.base = f'http://127.0.0.1:{cls.httpd.server_address[1]}'
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        db.db_path = cls._orig

    def call(self, method, p, body=None):
        req = urllib.request.Request(self.base + p, method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
                return r.status, (json.loads(data) if data else None)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b'null')

    def test_flow(self):
        code, teams = self.call('GET', '/api/team/bc23/t/?ordering=-rating')
        self.assertEqual((code, teams['count']), (200, 2))
        self.assertEqual(teams['results'][0]['profile']['rating'], 0.0)
        code, req = self.call('POST', '/api/compete/bc23/request/',
                              {'requested_by': 'alpha', 'requested_to': 'beta', 'is_ranked': True,
                               'player_order': '?', 'map_names': []})
        self.assertEqual((code, req['status'], len(req['maps'])), (201, 'Y', 3))
        code, ms = self.call('GET', '/api/compete/bc23/match/?team_id=alpha')
        self.assertEqual((code, ms['count'], ms['results'][0]['status']), (200, 1, 'QUE'))
        mid = ms['results'][0]['id']
        code, m = self.call('GET', f'/api/compete/bc23/match/{mid}/')
        self.assertEqual((code, m['is_ranked'], m['games']), (200, True, []))
        code, r = self.call('GET', '/api/compete/bc23/match/scrimmaging_record/?team_id=beta')
        self.assertEqual(r['Ranked'], {'wins': 0, 'losses': 0, 'ties': 0})
        code, h = self.call('GET', '/api/compete/bc23/match/historical_rating/?team_id=beta')
        self.assertEqual((code, h['team_rating']['rating_history']), (200, []))
        code, s = self.call('GET', '/replica/status')
        self.assertEqual(s['matches'], {'QUE': 1})
        code, e = self.call('POST', '/api/compete/bc23/request/', {'requested_by': 'alpha', 'requested_to': 'alpha',
                                                                  'is_ranked': False, 'map_names': ['m0']})
        self.assertEqual(code, 400)
        code, e = self.call('GET', '/api/compete/bc23/match/999/')
        self.assertEqual(code, 404)
        code, a = self.call('POST', '/api/episode/e/bc23/autoscrim/', {'best_of': 3})
        self.assertEqual((code, len(a['matches'])), (200, 1))

    def test_serve_refuses_non_loopback(self):
        with self.assertRaises(SystemExit):
            api.serve('0.0.0.0', 0)


# ================================================================ web pages, replay viewer, snapshot (tools/replica/web.py ...)
class WebTest(unittest.TestCase):
    """The server-rendered pages, the replay and viewer routes, HEAD/ETag handling, the snapshot renderers and the
    viewer installer, on a small DB with two completed ranked matches and one queued match."""

    @classmethod
    def setUpClass(cls):
        import http.server
        cls._env = {k: os.environ.get(k) for k in ('REPLICA_HOME', 'REPLICA_VIEWER_DIR')}
        cls.home = tempfile.mkdtemp(dir=_TMP)
        os.environ['REPLICA_HOME'] = cls.home
        os.environ['REPLICA_VIEWER_DIR'] = os.path.join(cls.home, 'viewer')
        db.ensure_dirs()
        conn = db.connect()
        maps = ('maptestsmall', 'SmallElements', 'Pizza')
        db.init_episode(conn, maps=list(maps) + ['Other'])
        cls.a = make_team(conn, 'us:bot')
        cls.b = make_team(conn, 'Evil<script>alert(1)</script>')
        cls.c = make_team(conn, 'gamma|*_')
        ids = db.public_maps(conn)

        def match(t0, t1):
            with db.tx(conn):
                m = db.insert_match(conn, alternate_order=True, is_ranked=True, status='QUE')
                db.insert_participant(conn, team_id=t0, match_id=m, player_index=0)
                db.insert_participant(conn, team_id=t1, match_id=m, player_index=1)
                db.set_match_maps(conn, m, [ids[x] for x in maps])
            return m
        with open(FIXTURE) as fh:
            log = fh.read()
        cls.m1 = match(cls.a, cls.b)
        worker.claim(conn, 'match', 'h:1:0')
        worker.report(conn, 'match', cls.m1, 'OK!', scores=[3, 0], games=worker.parse_games(log, list(maps), True))
        cls.m2 = match(cls.b, cls.c)
        worker.claim(conn, 'match', 'h:1:0')
        games = [{'idx': i, 'map': mp, 'reversed': i % 2 == 1, 'winner': w, 'round': 100 + i, 'reason': 'r'}
                 for i, (mp, w) in enumerate(zip(maps, 'BAB'))]
        worker.report(conn, 'match', cls.m2, 'OK!', scores=[1, 2], games=games)
        cls.m3 = match(cls.a, cls.c)   # stays queued
        cls.uuid = conn.execute('SELECT replay FROM match WHERE id=?', (cls.m1,)).fetchone()[0]
        cls.replay = b'\x1f\x8b' + bytes(range(256)) * 40
        with open(db.path('replay', cls.uuid + '.bc23'), 'wb') as fh:
            fh.write(cls.replay)
        conn.close()
        cls.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), api.Handler)
        cls.base = f'http://127.0.0.1:{cls.httpd.server_address[1]}'
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        for k, v in cls._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def get(self, p, method='GET', headers=None):
        req = urllib.request.Request(self.base + p, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()

    def page(self, p, code=200):
        st, h, body = self.get(p)
        self.assertEqual(st, code, p)
        self.assertTrue(h['Content-Type'].startswith('text/html'), p)
        self.assertIn("default-src 'none'", h['Content-Security-Policy'])
        text = body.decode()
        self.assertNotIn('<script', text, p)                 # pages carry no scripts (and names are escaped)
        self.assertNotRegex(text, r'(?i)(https?:)?//[a-z0-9.-]+\.[a-z]{2,}', p)   # and load nothing from elsewhere
        return text

    def test_ladder_equals_api_ratings_table(self):
        conn = db.connect()
        try:
            want = api.ratings_table(conn)
            got = web.ladder(conn)
        finally:
            conn.close()
        self.assertEqual([(r['rank'], r['id'], r['name'], r['value'], r['mean'], r['n'], r['ranked_record'],
                           r['games']) for r in got],
                         [(r['rank'], r['id'], r['name'], r['value'], r['mean'], r['n'], r['ranked_record'],
                           r['games']) for r in want])
        self.assertEqual([r['n'] for r in got if r['id'] == self.b], [2])
        self.assertTrue(all(r['last_match'] for r in got))

    def test_ladder_page(self):
        t = self.page('/')
        self.assertIn('Evil&lt;script&gt;alert(1)&lt;/script&gt;', t)
        self.assertRegex(t, r'<tr class=us><td class="num">\d+</td><td class="team"><a class="us" href="/team/%d">'
                            r'us:<wbr>bot</a> <span class="badge">us</span>' % self.a)
        self.assertEqual(t.count('<svg class="spark"'), 3)
        self.assertIn('1 queued', t)

    def test_team_page(self):
        t = self.page(f'/team/{self.a}')
        self.assertIn('Displayed rating after each ranked match', t)
        self.assertEqual(t.count('<div class="chart">'), 4)    # two charts, each in a desktop and a phone size
        self.assertIn('<polyline class="ln"', t)
        self.assertIn(f'href="/match/{self.m1}"', t)
        self.assertIn(f'/viewer/visualizer.html?gameSource=/replay/{self.uuid}.bc23', t)
        self.assertIn('<span class="res-W">W</span>', t)
        self.assertIn('<span title="\u03bc 1500.0 \u2192 1512.0">+12.0</span>', t)   # mean change on the team page
        self.page('/team/9999', 404)

    def test_match_page(self):
        t = self.page(f'/match/{self.m1}')
        for mp in ('maptestsmall', 'SmallElements', 'Pizza'):
            self.assertIn(f'<td>{mp}</td>', t)
        self.assertIn('Watch replay', t)
        self.assertIn('+12.0', t)       # mean change of a 3-0 win at equal means (GALAXY.md 2.1)
        self.assertIn('\u221212.0', t)
        self.assertIn('swapped', t)
        t = self.page(f'/match/{self.m3}')
        self.assertNotIn('Watch replay', t)
        self.assertIn('queued', t)
        self.page('/match/9999', 404)

    def test_matches_page_and_filters(self):
        t = self.page('/matches')
        for m in (self.m1, self.m2, self.m3):
            self.assertIn(f'<a href="/match/{m}">{m}</a>', t)
        t = self.page('/matches?status=queued')
        self.assertIn(f'<a href="/match/{self.m3}">', t)
        self.assertNotIn(f'<a href="/match/{self.m1}">', t)
        t = self.page(f'/matches?status=done&team={self.c}')
        self.assertIn(f'<a href="/match/{self.m2}">', t)
        self.assertNotIn(f'<a href="/match/{self.m1}">', t)

    def test_replay_file_head_and_etag(self):
        st, h, body = self.get(f'/replay/{self.uuid}.bc23')
        self.assertEqual((st, body, h['Content-Type']), (200, self.replay, 'application/octet-stream'))
        st, h2, body = self.get(f'/replay/{self.uuid}.bc23', 'HEAD')
        self.assertEqual((st, body, h2['Content-Length']), (200, b'', str(len(self.replay))))
        st, _, body = self.get(f'/replay/{self.uuid}.bc23', headers={'If-None-Match': h['ETag']})
        self.assertEqual((st, body), (304, b''))
        self.assertEqual(self.get('/replay/00000000-0000-0000-0000-000000000000.bc23')[0], 404)
        self.assertEqual(self.get('/replay/../replica.db')[0], 404)
        st, _, body = self.get('/replica/status', 'HEAD')    # HEAD on the JSON API: headers only
        self.assertEqual((st, body), (200, b''))

    def test_viewer(self):
        import base64
        import hashlib
        from replica import viewer
        self.assertEqual(self.get('/viewer/visualizer.html')[0], 503)
        src = tempfile.mkdtemp(dir=_TMP)
        os.makedirs(os.path.join(src, 'out'))
        files = {'visualizer.html': b'<html></html>', 'out/app.js': b'window.battlecode={mount:function(){}};',
                 'out/red_carrier-3QDuG23.png': b'\x89PNG fake'}
        for rel, data in files.items():
            with open(os.path.join(src, rel), 'wb') as fh:
                fh.write(data)
        pins = {rel: hashlib.sha256(data).hexdigest() for rel, data in files.items()}
        self.assertEqual(viewer.check(src, pins=pins), [])
        with self.assertRaises(SystemExit):              # the real pins do not match the fake files
            viewer.install(src)
        dest = viewer.install(src, pins=pins)
        self.assertEqual(dest, web.viewer_dir())
        self.assertEqual(sorted(os.listdir(os.path.join(dest, 'out'))), ['app.js', 'red_carrier-3QDuG23.png'])
        st, h, body = self.get(f'/viewer/visualizer.html?gameSource=/replay/{self.uuid}.bc23')
        self.assertEqual(st, 200)
        text = body.decode()
        self.assertNotIn('googleapis', text)
        script = re.search(r'<script type="text/javascript">(.*?)</script>', text, re.S).group(1)
        digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
        self.assertIn(f"'sha256-{digest}'", h['Content-Security-Policy'])
        self.assertIn("connect-src 'self'", h['Content-Security-Policy'])
        self.assertIn('src="out/app.js"', text)
        st, h, body = self.get('/viewer/out/app.js')
        self.assertEqual((st, body), (200, files['out/app.js']))
        self.assertTrue(h['Content-Type'].startswith('application/javascript'))
        self.assertEqual(self.get('/viewer/out/red_carrier-3QDuG23.png')[1]['Content-Type'], 'image/png')
        self.assertEqual(self.get('/viewer/out/nope.js')[0], 404)
        self.assertEqual(self.get('/viewer/out/..%2fVERSION')[0], 404)
        self.assertEqual(self.get('/viewer/out/x.html')[0], 404)
        with open(os.path.join(src, 'out', 'app.js'), 'ab') as fh:
            fh.write(b'tampered')
        self.assertEqual(viewer.check(src, pins=pins), [('out/app.js', 'sha256 mismatch')])

    def test_get_and_head_never_write(self):
        conn = db.connect()
        before = '\n'.join(conn.iterdump())
        for p in ('/', f'/team/{self.a}', f'/match/{self.m1}', '/matches?status=done', f'/replay/{self.uuid}.bc23',
                  '/replica/ratings', '/replica/status'):
            self.get(p)
            self.get(p, 'HEAD')
        self.assertEqual('\n'.join(conn.iterdump()), before)
        conn.close()

    def test_snapshot(self):
        import xml.dom.minidom
        from replica import snapshot
        conn = snapshot.connect_ro(self.home)
        try:
            data = snapshot.collect(conn, home=self.home)
        finally:
            conn.close()
        data = json.loads(json.dumps(data))              # what --from-vm receives
        md = snapshot.render_md(data)
        self.assertIn('**us:bot**', md)
        self.assertIn('gamma\\|\\*\\_', md)
        self.assertIn('Evil\\<script\\>', md)
        self.assertEqual(len([l for l in md.splitlines() if l.startswith('| ') and l[2:3].isdigit()]), 3 + 2)
        svg = snapshot.render_svg(data)
        doc = xml.dom.minidom.parseString(svg)           # well-formed (names escaped)
        self.assertEqual(doc.documentElement.tagName, 'svg')
        self.assertEqual(svg.count('<polyline'), 3)
        out = tempfile.mkdtemp(dir=_TMP)
        paths = snapshot.write(data, out, 'svg')
        self.assertEqual(sorted(os.path.basename(p) for p in paths), ['ladder.md', 'ladder.svg'])
        with open(os.path.join(out, 'ladder.md')) as fh:
            self.assertIn('![Replica ladder](ladder.svg)', fh.read())
        if snapshot.have_matplotlib():                  # the driver's tools/.venv; not the system python
            snapshot.write(data, out, 'png')
            self.assertEqual(sorted(os.listdir(out)), ['ladder.md', 'ladder.png'])   # the stale svg is removed

    def test_chart_helpers(self):
        self.assertEqual(web.nice_ticks(0, 100), [0, 25, 50, 75, 100])
        self.assertEqual(web.sparkline([1.0]), '')
        self.assertIn('<polyline', web.sparkline([0.0, 5.0, 3.0]))
        self.assertIn('No rated ranked matches', web.line_chart([], 'x'))
        self.assertEqual(web.signed(-2.25), '\u22122.2')


# ================================================================ records and history leave out invisible teams
class InvisibleTeamRecordTest(unittest.TestCase):
    """Regression (review 2026-10-07): galaxy's get_historical_rating and scrimmaging_record exclude every match
    with an INVISIBLE ('O') team in it (compete/views.py:459, :681), for every viewer. The replica counted them. The
    rating itself still includes such a match (galaxy rates it like any other; only the views hide it)."""

    def test_record_and_history(self):
        conn = new_db(maps=('a', 'b', 'c'))
        x, y = make_team(conn, 'x'), make_team(conn, 'y')
        inv = make_team(conn, 'inv', status='O')

        def play(t0, t1, scores):
            with db.tx(conn):
                m = db.insert_match(conn, alternate_order=True, is_ranked=True, status='RUN')
                db.insert_participant(conn, team_id=t0, match_id=m, player_index=0)
                db.insert_participant(conn, team_id=t1, match_id=m, player_index=1)
                db.set_match_maps(conn, m, [1, 2, 3])
            worker.report(conn, 'match', m, SaturnStatus.COMPLETED, scores=scores)
            return m
        play(x, inv, [3, 0])
        m2 = play(x, y, [1, 2])
        self.assertEqual(api.scrimmaging_record(conn, x)['Ranked'], {'wins': 0, 'losses': 1, 'ties': 0})
        self.assertEqual(api.scrimmaging_record(conn, inv)['All'], {'wins': 0, 'losses': 0, 'ties': 0})
        hist = api.historical_rating(conn, x)['team_rating']['rating_history']
        self.assertEqual([h['match'] for h in hist], [m2])
        self.assertEqual(hist[0]['n'], 2)              # the hidden match still counts for the rating
        self.assertEqual(api.historical_rating(conn, inv)['team_rating']['rating_history'], [])
        self.assertEqual([h['match'] for h in web.team_history(conn, x)], [m2])
        lad = {r['id']: r for r in web.ladder(conn)}
        self.assertEqual(lad[x]['ranked_record'], {'wins': 0, 'losses': 1, 'ties': 0})
        self.assertEqual([h['match'] for h in lad[x]['history']], [m2])
        self.assertNotIn(inv, lad)
        self.assertEqual({r['id']: r['ranked_record'] for r in api.ratings_table(conn)},
                         {k: v['ranked_record'] for k, v in lad.items()})


# ================================================================ differential check against galaxy's own algorithm
class GalaxyTriggerModel:
    """An independent object-model port of galaxy's rating finalization, driven the way galaxy drives it: a Match
    save (post_save update_match_ratings) and each newly finalized participation (request_rating_update on the
    team's next match) enqueue a Match.try_rating_update task, and Cloud Tasks runs the tasks in any order.
    Deliberately shares no code with tools/replica/rating.py (teams/models.py Rating, compete/models.py:299-345 and
    435-542, teams/signals.py copy_rating_to_profile)."""
    FINAL = ('OK!', 'ERR', 'CAN')

    class R:
        def __init__(self, mean=1500.0, n=0, saved=False):
            self.mean, self.n, self.saved = mean, n, saved
            self.value = mean - 1500.0 * 0.85 ** n if saved else 0   # Rating.value defaults to 0 until save()

        def save(self):
            self.value, self.saved = self.mean - 1500.0 * 0.85 ** self.n, True
            return self

        def step(self, opps, score):
            e = sum(1 / (1 + 10 ** (-(self.mean - o.mean) / 400.0)) for o in opps) / len(opps)
            return type(self)(self.mean + 24.0 * (score - e), self.n + 1).save()

    def __init__(self):
        self.profile, self.parts, self.matches, self.tasks = {}, [], {}, []

    def team(self, t):
        self.profile[t] = self.R().save()

    def match(self, mid, is_ranked, teams):
        self.matches[mid] = {'status': 'QUE', 'is_ranked': is_ranked, 'parts': []}
        for i, t in enumerate(teams):
            prev = next((p for p in reversed(self.parts) if p['team'] == t), None)
            p = {'team': t, 'match': mid, 'score': None, 'rating': None, 'prev': prev}
            self.parts.append(p)
            self.matches[mid]['parts'].append(p)
        self.tasks.append(mid)

    def old(self, p):
        return p['prev']['rating'] if p['prev'] is not None else self.R()

    def participant_update(self, p, opponents):
        m = self.matches[p['match']]
        if p['rating'] is not None:
            return
        old = self.old(p)
        if old is None:
            return
        if (not m['is_ranked']) or (m['status'] in self.FINAL and m['status'] != 'OK!'):
            p['rating'] = old if old.saved else old.save()
        elif m['status'] in self.FINAL:
            opp = [self.old(o) for o in opponents]
            total = p['score'] + sum(o['score'] for o in opponents)
            if all(r is not None for r in opp):
                p['rating'] = old.step(opp, p['score'] / total)
        if p['rating'] is not None:
            if self.profile[p['team']].n < p['rating'].n:
                self.profile[p['team']] = p['rating']
            nxt = next((q for q in self.parts if q['prev'] is p), None)
            if nxt is not None:
                self.tasks.append(nxt['match'])

    def match_update(self, mid):
        m = self.matches[mid]
        if m['is_ranked'] and m['status'] not in self.FINAL:
            return
        for p in m['parts']:
            self.participant_update(p, [o for o in m['parts'] if o is not p])

    def report(self, mid, status, scores=None):
        m = self.matches[mid]
        if m['status'] in self.FINAL:
            return
        for p, s in zip(m['parts'], scores or []):
            p['score'] = s
        m['status'] = status
        self.tasks.append(mid)

    def drain(self, rng):
        while self.tasks:
            self.match_update(self.tasks.pop(rng.randrange(len(self.tasks))))


class GalaxyDifferentialTest(unittest.TestCase):
    """Random schedules of ranked and unranked matches between 2-6 teams, finished in random order as OK! (random
    scores), ERR (5 failures), CAN or left running, then some ERR/CAN matches requeued and finished. Galaxy's
    tasks run in random order and at random times; an admin requeue comes after the pending tasks have run. Every
    participation's rating (mean, n, value) and every team's displayed rating must equal the replica's."""
    SEEDS = 120

    def one(self, seed):
        rng = random.Random(seed)
        g, conn = GalaxyTriggerModel(), new_db(maps=('a', 'b', 'c'))
        teams = [make_team(conn, f't{i}') for i in range(rng.randint(2, 6))]
        for t in teams:
            g.team(t)
        mids = []
        for _ in range(rng.randint(1, 25)):
            a, b = rng.sample(teams, 2)
            ranked = rng.random() < 0.75
            with db.tx(conn):
                m = db.insert_match(conn, is_ranked=ranked, alternate_order=True, status='QUE')
                db.insert_participant(conn, team_id=a, match_id=m, player_index=0)
                db.insert_participant(conn, team_id=b, match_id=m, player_index=1)
                db.set_match_maps(conn, m, [1, 2, 3])
            rating.pump(conn)
            g.match(m, ranked, [a, b])
            mids.append(m)
            if rng.random() < 0.3:
                g.drain(rng)

        def finish_ok(m):
            w = rng.randint(0, 3)
            worker.report(conn, 'match', m, 'OK!', scores=[w, 3 - w])
            g.report(m, 'OK!', [w, 3 - w])
        for m in rng.sample(mids, len(mids)):
            r = rng.random()
            if r < 0.1:
                continue                                    # still running
            conn.execute("UPDATE match SET status='RUN' WHERE id=?", (m,))
            if r < 0.2:
                db.cancel(conn, [m])
                rating.pump(conn)
                g.report(m, 'CAN')
            elif r < 0.3:
                for _ in range(db.SATURN_MAX_FAILURES):
                    worker.report(conn, 'match', m, 'TRY')
                g.report(m, 'ERR')
            else:
                finish_ok(m)
            if rng.random() < 0.5:
                g.drain(rng)
        g.drain(rng)
        for m in mids:                                      # admin force_requeue (enqueue_all: no post_save)
            if row(conn, 'match', m)['status'] in ('ERR', 'CAN') and rng.random() < 0.5:
                self.assertTrue(db.requeue(conn, m))
                g.matches[m]['status'] = 'QUE'
                conn.execute("UPDATE match SET status='RUN' WHERE id=?", (m,))
                g.tasks.append(m)                           # saturn's RUN report saves the match
                finish_ok(m)
        g.drain(rng)
        rating.pump(conn)
        got = conn.execute('SELECT * FROM match_participant ORDER BY id').fetchall()
        self.assertEqual(len(got), len(g.parts))
        for r, p in zip(got, g.parts):
            if p['rating'] is None:
                self.assertIsNone(r['rating_id'], (seed, r['id']))
                continue
            self.assertIsNotNone(r['rating_id'], (seed, r['id']))
            rr = db.get_rating(conn, r['rating_id'])
            self.assertEqual(rr['n'], p['rating'].n, (seed, r['id']))
            self.assertAlmostEqual(rr['mean'], p['rating'].mean, places=9, msg=(seed, r['id']))
            self.assertAlmostEqual(rr['value'], p['rating'].value, places=9, msg=(seed, r['id']))
        for t in teams:
            tr = db.get_rating(conn, row(conn, 'team', t)['rating_id'])
            gp = g.profile[t]
            self.assertEqual((tr['n'], round(tr['mean'], 9), round(tr['value'], 9)),
                             (gp.n, round(gp.mean, 9), round(gp.value, 9)), (seed, t))

    def test_pump_equals_galaxy_trigger_model(self):
        for seed in range(self.SEEDS):
            self.one(seed)


# ================================================================ guard: no external hosts in the replica source
class GuardTest(unittest.TestCase):
    """Every file under tools/replica (and the CLI tools/replica.py) is scanned, case-insensitively.
    ALLOWED lists the only exceptions, each an exact URL prefix in one file: the deploy scripts' pinned, checksummed
    download of the Caddy web server (a root-run setup step, not replica runtime code)."""
    FORBIDDEN = ('battlecode.org', 'googleapis', 'challonge', 'mailjet', 'github.com')
    ALLOWED = {os.path.join('deploy', 'config.sh'): ('https://github.com/caddyserver/caddy/releases/download/',)}

    def files(self):
        root = os.path.join(REPO, 'tools', 'replica')
        out = [os.path.join(REPO, 'tools', 'replica.py')]
        for d, _, fs in os.walk(root):
            out += [os.path.join(d, f) for f in fs if not f.endswith('.pyc') and '__pycache__' not in d]
        return out

    def test_no_forbidden_hosts(self):
        files = self.files()
        self.assertGreaterEqual(len(files), 6)
        root = os.path.join(REPO, 'tools', 'replica')
        for f in files:
            with open(f, 'rb') as fh:
                text = fh.read().decode('utf-8', 'replace').lower()
            for prefix in self.ALLOWED.get(os.path.relpath(f, root), ()):
                text = text.replace(prefix.lower(), '<allowed>')
            for bad in self.FORBIDDEN:
                self.assertNotIn(bad, text, msg=f'{f} mentions {bad}')

    def test_no_network_client_imports(self):
        for f in self.files():
            with open(f, 'rb') as fh:
                text = fh.read().decode('utf-8', 'replace')
            for mod in ('urllib.request', 'http.client', 'requests', 'google', 'smtplib', 'ftplib'):
                self.assertIsNone(re.search(rf'^\s*(import|from)\s+{re.escape(mod)}\b', text, re.M),
                                  msg=f'{f} imports {mod}')

    def test_engine_websocket_off(self):
        with open(os.path.join(REPO, 'tools', 'replica', 'worker.py')) as fh:
            self.assertIn("'-Dbc.server.websocket=false'", fh.read())


def tearDownModule():
    shutil.rmtree(_TMP, ignore_errors=True)


def load_tests(loader, tests, pattern):
    """Also run the offline deploy checks (test_deploy.py), so tools/unit-tests.sh, which runs this file, covers
    them too. Under `unittest discover` (pattern set) that file is collected on its own instead."""
    if pattern is None:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import test_deploy
        tests.addTests(loader.loadTestsFromModule(test_deploy))
    return tests


if __name__ == '__main__':
    unittest.main(verbosity=1)
