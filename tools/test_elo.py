#!/usr/bin/env python3
"""Unit tests for the ladder ratings (owner, PROMPTS 42: "double-check your ELO code and ensure it's all tested"):
tools/elolib.py (the Bradley-Terry fit, dedupe, load/append, the incumbent), tools/elo.py (progress/ELO.md and its pool
options, run on a fixture in a temporary tree) and tools/field_score.py. Every bug of the 2026-10-10 audit (F1-F3,
F5, F6, D1-D5, C1, C3, C4) has a regression test here, named in its docstring. Stdlib only: tools/unit-tests.sh runs
system python3, which has no numpy. Never writes progress/ (it only reads progress/games.csv in RealDataTest).
Run by tools/unit-tests.sh."""
import collections, contextlib, csv, importlib.util, io, json, math, os, random, shutil, statistics, subprocess, sys
import tempfile, unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import elolib as el   # noqa: E402  (field_score.py's own `import elolib` then shares this module, and its patches)

SCALE = 400 / math.log(10)


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, TOOLS / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def write(path, text):
    with open(path, 'w', newline='') as fh:
        fh.write(text)


def row(a, b, w, m='M', seed='map', reason='', run='t', seq=0, rounds=100):
    return dict(run=run, seq=seq, teamA=a, teamB=b, map=m, winner=w, rounds=rounds, reason=reason, seed=seed)


def series(a, b, wins_a, n, tag='m'):
    """n games of a (team A) against b on distinct maps, a winning the first wins_a."""
    return [row(a, b, 'A' if i < wins_a else 'B', m=f'{tag}{i}') for i in range(n)]


def quiet(fn, *args, **kw):
    """fn(*args, **kw) with stderr captured -> (result, stderr text)."""
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        out = fn(*args, **kw)
    return out, buf.getvalue()


def sig(x):
    return 1 / (1 + math.exp(-x))


def bisect(f, lo, hi):
    """The root of an increasing f on [lo, hi]."""
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return (lo + hi) / 2


def pairs_of(rows, cap):
    """Independent effective counts: {(p, q): (games, wins of p over q)} for p < q, each game weighted min(1, cap/n)."""
    n = collections.Counter(); w = collections.Counter()
    for r in rows:
        a, b = sorted((r['teamA'], r['teamB'])); n[a, b] += 1
        w[a, b] += (r['winner'] == 'A') == (r['teamA'] == a)
    f = lambda k: min(1.0, cap / k) if cap else 1.0
    return {k: (n[k] * f(n[k]), w[k] * f(n[k])) for k in n}


def ref_mm(rows, prior, cap, tol=1e-13, iters=10 ** 6):
    """The minorise-maximise fit (Hunter 2004; elolib's solver before the audit), as an independent reference."""
    E = pairs_of(rows, cap)
    P = sorted({p for k in E for p in k}); v = {p: 1.0 for p in P}
    W = collections.Counter(); nb = collections.defaultdict(list)
    for (p, q), (n, wp) in E.items():
        W[p] += wp; W[q] += n - wp; nb[p].append((q, n)); nb[q].append((p, n))
    for _ in range(iters):
        new = {p: (W[p] + prior) / (sum(n / (v[p] + v[q]) for q, n in nb[p]) + 2 * prior / (v[p] + 1)) for p in P}
        delta = max(abs(math.log(new[p] / v[p])) for p in P); v = new
        if delta < tol:
            break
    return {p: 1500 + SCALE * math.log(v[p]) for p in P}


def loglik(th, E, prior):
    """Penalised log-likelihood at theta (ln strengths, a dict), coded from the model, not from elolib."""
    L = sum(w * math.log(sig(th[p] - th[q])) + (n - w) * math.log(sig(th[q] - th[p])) for (p, q), (n, w) in E.items())
    return L + prior * sum(math.log(sig(t)) + math.log(sig(-t)) for t in th.values())


def invert(A):
    """Gauss-Jordan inverse with partial pivoting."""
    m = len(A); M = [list(r) + [float(i == j) for j in range(m)] for i, r in enumerate(A)]
    for c in range(m):
        piv = max(range(c, m), key=lambda r: abs(M[r][c])); M[c], M[piv] = M[piv], M[c]
        d = M[c][c]; M[c] = [x / d for x in M[c]]
        for r in range(m):
            if r != c and M[r][c]:
                k = M[r][c]; M[r] = [x - k * y for x, y in zip(M[r], M[c])]
    return [r[m:] for r in M]


def fixture(seed=7, m=12, games=300, big=50):
    """m players with random true ratings, random pairings, and (p0, p1) played `big` extra times (above a cap of 20)."""
    rng = random.Random(seed); true = [rng.gauss(1500, 400) for _ in range(m)]; rows = []
    pairs = [(rng.randrange(m), rng.randrange(m)) for _ in range(games)] + [(0, 1)] * big
    for g, (i, j) in enumerate(pairs):
        if i == j:
            j = (i + 1) % m
        a, b = (i, j) if rng.random() < .5 else (j, i)
        rows.append(row(f'p{a}', f'p{b}', 'A' if rng.random() < el.expected(true[a], true[b]) else 'B', m=f'm{g}', seq=g))
    return rows


class ExpectedTest(unittest.TestCase):
    def test_values_and_symmetry(self):
        self.assertEqual(el.expected(1500, 1500), 0.5)
        self.assertAlmostEqual(el.expected(1900, 1500), 10 / 11, places=12)      # 400 points = 10:1 odds
        self.assertAlmostEqual(el.expected(1500 + SCALE * math.log(3), 1500), 0.75, places=12)
        for a, b in [(1200, 1750), (2400, 300), (1500.5, 1499.5)]:
            self.assertAlmostEqual(el.expected(a, b) + el.expected(b, a), 1.0, places=12)
            self.assertAlmostEqual(el.expected(a + 77, b + 77), el.expected(a, b), places=12)


class FitTest(unittest.TestCase):
    """elolib.fit on hand-checkable and seeded inputs, against closed forms and independent references."""

    def test_empty_input(self):
        """F3: fit([]) and an all-COIN input return empty results (it raised ValueError: max() of an empty sequence)."""
        for rows in ([], [row('x', 'y', 'A', reason='COIN')]):
            (R, SE, games, W), err = quiet(el.fit, rows)
            self.assertEqual((dict(R), dict(SE), dict(games), dict(W)), ({}, {}, {}, {}))
            self.assertEqual(err, '')
            self.assertEqual(R['anyone'], 1500.0); self.assertEqual(SE['anyone'], float('inf'))

    def test_single_game_closed_form(self):
        """One game a > b: R = 1500 +- SCALE t with t solving 1 - sig(2t) + prior (1 - 2 sig(t)) = 0, and the SE of
        R - mean = (R_a - R_b) / 2: SCALE / sqrt(2 (2c + q)), c = sig(2t)(1 - sig(2t)), q = 2 prior sig(t)(1 - sig(t))."""
        for prior in (el.PRIOR, 1.0):
            t = bisect(lambda t: -(1 - sig(2 * t) + prior * (1 - 2 * sig(t))), 0, 20)
            c = sig(2 * t) * (1 - sig(2 * t)); q = 2 * prior * sig(t) * (1 - sig(t))
            R, SE, games, W = el.fit([row('a', 'b', 'A')], prior=prior)
            self.assertAlmostEqual(R['a'], 1500 + SCALE * t, places=6)
            self.assertAlmostEqual(R['b'], 1500 - SCALE * t, places=6)
            self.assertAlmostEqual(SE['a'], SCALE / math.sqrt(2 * (2 * c + q)), places=6)
            self.assertAlmostEqual(SE['a'], SE['b'], places=9)
            self.assertEqual((games['a'], games['b'], W['a'], W['b']), (1, 1, 1, 0))
        R, _, _, _ = el.fit([row('a', 'b', 'A')], prior=1.0)                   # the old documented value at prior 1
        self.assertAlmostEqual(R['a'], 1591.7315, places=3)

    def test_three_of_four(self):
        """X beats Y 3 of 4: the MLE gap is 400 log10(3) = 190.85; the default prior's MAP solves 3 - 4 sig(2t) +
        prior (1 - 2 sig(t)) = 0."""
        rows = series('X', 'Y', 3, 4)
        R, _, _, _ = el.fit(rows, prior=1e-6)
        self.assertAlmostEqual(R['X'] - R['Y'], 400 * math.log10(3), delta=0.01)
        t = bisect(lambda t: -(3 - 4 * sig(2 * t) + el.PRIOR * (1 - 2 * sig(t))), 0, 20)
        R, _, _, _ = el.fit(rows)
        self.assertAlmostEqual(R['X'] - R['Y'], 2 * SCALE * t, places=6)

    def test_mirrored_records_sum_to_3000(self):
        R, _, _, _ = el.fit(series('a', 'b', 7, 10) + series('c', 'a', 4, 9, 'n'))
        self.assertGreater(R['a'], R['b'])
        R2, _, _, _ = el.fit(series('a', 'b', 3, 10))
        self.assertAlmostEqual(R2['a'] + R2['b'], 3000, places=6)

    def test_level_identity(self):
        """The score equations sum to sum_i tanh((R_i - 1500) / (2 SCALE)) = 0: the prior sets the level, not the mean."""
        R, _, _, _ = el.fit(fixture())
        self.assertAlmostEqual(sum(math.tanh((r - 1500) / (2 * SCALE)) for r in R.values()), 0.0, places=6)

    def test_score_equations(self):
        """At the fit, for every player: effective wins + prior = sum_q n_eff E(R_p, R_q) + 2 prior E(R_p, 1500), with
        (p0, p1) above the cap (50 games, cap 20)."""
        rows = fixture()
        for prior in (el.PRIOR, 1.0):
            R, _, _, _ = el.fit(rows, prior=prior, pair_cap=20)
            lhs = collections.Counter(); rhs = collections.Counter()
            for (p, q), (n, w) in pairs_of(rows, 20).items():
                lhs[p] += w; lhs[q] += n - w
                rhs[p] += n * el.expected(R[p], R[q]); rhs[q] += n * el.expected(R[q], R[p])
            self.assertEqual(len(R), 12)
            for p in R:
                self.assertAlmostEqual(lhs[p] + prior, rhs[p] + 2 * prior * el.expected(R[p], 1500), places=6)

    def test_matches_minorise_maximise(self):
        """F1: the Newton solve agrees with the old minorise-maximise fit (an independent algorithm) to 1e-4 Elo."""
        rows = fixture()
        for prior in (1.0, el.PRIOR):
            ref = ref_mm(rows, prior, 20)
            R, _, _, _ = el.fit(rows, prior=prior, pair_cap=20)
            self.assertEqual(set(R), set(ref))
            for p in ref:
                self.assertAlmostEqual(R[p], ref[p], delta=1e-4)

    def test_se_is_the_centred_inverse_of_the_hessian(self):
        """F2: SE_i = SCALE sqrt((C H^-1 C)_ii), H the penalised information (here a finite-difference Hessian of an
        independently coded log-likelihood, inverted by Gauss-Jordan), C = I - 11'/m: the SE of R_i - mean R."""
        rows = fixture(); E = pairs_of(rows, 20)
        R, SE, _, _ = el.fit(rows, pair_cap=20)
        P = sorted(R); m = len(P); th = {p: (R[p] - 1500) / SCALE for p in P}; h = 1e-3

        def L(**dx):
            t = dict(th)
            for k, v in dx.items():
                t[k] += v
            return loglik(t, E, el.PRIOR)
        H = [[0.0] * m for _ in range(m)]
        for i, p in enumerate(P):
            for j, q in enumerate(P):
                if i == j:
                    H[i][i] = -(L(**{p: h}) - 2 * L() + L(**{p: -h})) / h ** 2
                elif j > i:
                    d = (L(**{p: h, q: h}) - L(**{p: h, q: -h}) - L(**{p: -h, q: h}) + L(**{p: -h, q: -h})) / (4 * h * h)
                    H[i][j] = H[j][i] = -d
        V = invert(H); row_ = [sum(r) / m for r in V]; tot = sum(row_) / m
        for i, p in enumerate(P):
            se = SCALE * math.sqrt(V[i][i] - 2 * row_[i] + tot)
            self.assertAlmostEqual(SE[p] / se, 1.0, delta=1e-4)
            self.assertLess(SE[p], SCALE / math.sqrt(H[i][i]) * 3)                  # sanity: same order as the diagonal

    def test_se_round_robin_closed_form(self):
        """F2: a balanced round robin (each pair 1-1) puts everyone at exactly 1500, and the centred SE is
        SCALE sqrt((1 - 1/m) / (c m + q)), c = 0.5, q = 2 prior / 4: smaller than the diagonal SCALE / sqrt(c (m - 1) + q)."""
        m = 6; P = [f'p{i}' for i in range(m)]
        rows = [row(P[i], P[j], w, m=f'{w}') for i in range(m) for j in range(i + 1, m) for w in 'AB']
        R, SE, games, W = el.fit(rows)
        c, q = 0.5, 2 * el.PRIOR * 0.25
        for p in P:
            self.assertAlmostEqual(R[p], 1500.0, places=9)
            self.assertAlmostEqual(SE[p], SCALE * math.sqrt((1 - 1 / m) / (c * m + q)), places=6)
            self.assertLess(SE[p], SCALE / math.sqrt(c * (m - 1) + q))
            self.assertEqual((games[p], W[p]), (2 * (m - 1), m - 1))

    def test_se_chain_wider_than_diagonal(self):
        """F2: on a chain (each player meets only its neighbours) a rating is pinned only through the others, so the
        centred SE exceeds the diagonal SE (the SE with every other rating known) that elolib used to report."""
        P = [f'p{i}' for i in range(10)]
        rows = [r for i in range(9) for r in series(P[i], P[i + 1], 10, 20, f'c{i}_')]
        R, SE, _, _ = el.fit(rows)
        for i, p in enumerate(P):
            th = (R[p] - 1500) / SCALE; info = 2 * el.PRIOR * sig(th) * (1 - sig(th))
            for j in (i - 1, i + 1):
                if 0 <= j < 10:
                    pr = sig((R[p] - R[P[j]]) / SCALE); info += 20 * pr * (1 - pr)
            self.assertGreater(SE[p], SCALE / math.sqrt(info) * 1.05, p)

    def test_row_order_invariance(self):
        rows = fixture(); R, SE, g, W = el.fit(rows)
        for seed in (1, 2):
            sh = list(rows); random.Random(seed).shuffle(sh)
            R2, SE2, g2, W2 = el.fit(sh)
            for p in R:
                self.assertAlmostEqual(R2[p], R[p], delta=1e-6); self.assertAlmostEqual(SE2[p], SE[p], delta=1e-6)
            self.assertEqual((g2, W2), (g, W))

    def test_side_swap_invariance(self):
        """The fit has no side term: every game recorded with the sides swapped and the winner flipped fits the same."""
        rows = fixture()
        sw = [dict(r, teamA=r['teamB'], teamB=r['teamA'], winner='B' if r['winner'] == 'A' else 'A') for r in rows]
        R, SE, g, W = el.fit(rows); R2, SE2, g2, W2 = el.fit(sw)
        for p in R:
            self.assertAlmostEqual(R2[p], R[p], delta=1e-9); self.assertAlmostEqual(SE2[p], SE[p], delta=1e-9)
        self.assertEqual((g2, W2), (g, W))

    def test_prior_keeps_perfect_records_finite(self):
        """An unbeaten and a winless player get finite ratings; a weaker prior stretches them further apart."""
        rows = series('a', 'b', 5, 5) + series('b', 'c', 4, 6, 'n') + series('c', 'd', 6, 6, 'o')
        gaps = []
        for prior in (1.0, el.PRIOR, 0.01):
            (R, SE, _, _), err = quiet(el.fit, rows, prior=prior)
            self.assertEqual(err, '')
            for p in 'abcd':
                self.assertTrue(math.isfinite(R[p]) and math.isfinite(SE[p]) and SE[p] > 0, (prior, p))
            self.assertTrue(R['a'] > R['b'] > R['c'] > R['d'])
            gaps.append(R['a'] - R['d'])
        self.assertTrue(gaps[0] < gaps[1] < gaps[2], gaps)

    def test_extreme_chain(self):
        """A 20-0 chain a > b > c > d converges with no warning to finite, ordered ratings."""
        rows = series('a', 'b', 20, 20) + series('b', 'c', 20, 20, 'n') + series('c', 'd', 20, 20, 'o')
        (R, _, _, _), err = quiet(el.fit, rows)
        self.assertEqual(err, '')
        self.assertTrue(R['a'] > R['b'] > R['c'] > R['d'] and all(math.isfinite(R[p]) for p in 'abcd'))

    def test_prior_must_be_positive(self):
        """F6: prior 0 crashed with a math domain error (winless) or diverged (unbeaten); now it is refused."""
        for prior in (0, 0.0, -1.0, float('nan')):
            with self.assertRaises(ValueError):
                el.fit([row('a', 'b', 'A')], prior=prior)

    def test_not_converged_warns(self):
        (R, _, _, _), err = quiet(el.fit, fixture(), iters=1)
        self.assertIn('not converged after 1 iterations', err)
        self.assertEqual(len(R), 12)

    def test_self_play_rows_dropped(self):
        """F5: 100 self-play rows (no likelihood) cut SE_p from 64.7 to 23.0 and inflated games to 230, wins to 120."""
        base = series('p', 'q', 20, 30)
        R, SE, g, W = el.fit(base)
        (R2, SE2, g2, W2), err = quiet(el.fit, base + [row('p', 'p', 'A', m=f's{i}') for i in range(100)])
        self.assertIn('dropped 100 self-play rows', err)
        for p in 'pq':
            self.assertAlmostEqual(R2[p], R[p], places=9); self.assertAlmostEqual(SE2[p], SE[p], places=9)
        self.assertEqual((g2['p'], W2['p']), (30, 20))
        self.assertEqual((g2, W2), (g, W))

    def test_invalid_winners_skipped(self):
        """D2: a winner other than exactly A or B ('', None from a short line, a tie, lower case) was a B win."""
        valid = [row('X', 'Y', 'A')]
        bad = [row('X', 'Y', w, m=f'b{i}') for i, w in enumerate(['', None, 'T', 'a', 'Tie', ' A', 'b'])]
        R0, SE0, g0, W0 = el.fit(valid)
        (R, SE, g, W), err = quiet(el.fit, valid + bad)
        self.assertIn('skipped 7 rows with winner not A|B', err)
        self.assertEqual((dict(R), dict(g), dict(W)), (dict(R0), dict(g0), dict(W0)))
        (R, _, g, _), err = quiet(el.fit, bad)
        self.assertEqual((dict(R), dict(g)), ({}, {}))


class PairCapTest(unittest.TestCase):
    """PAIR_CAP: a pair with n > cap games enters with weight cap / n on each game; the counts returned stay raw."""

    def test_cap_equals_scaled_pair(self):
        capped = series('a', 'b', 700, 1000) + series('b', 'c', 12, 20, 'n')
        scaled = series('a', 'b', 140, 200) + series('b', 'c', 12, 20, 'n')
        R, SE, g, W = el.fit(capped, pair_cap=200)
        R2, SE2, _, _ = el.fit(scaled, pair_cap=0)
        for p in 'abc':
            self.assertAlmostEqual(R[p], R2[p], places=7); self.assertAlmostEqual(SE[p], SE2[p], places=7)
        self.assertEqual((g['a'], g['b'], W['a'], W['b']), (1000, 1020, 700, 312))

    def test_cap_above_every_pair_is_no_cap(self):
        rows = fixture()
        R, SE, _, _ = el.fit(rows, pair_cap=0); R2, SE2, _, _ = el.fit(rows, pair_cap=10 ** 6)
        R3, _, _, _ = el.fit(rows, pair_cap=20)
        for p in R:
            self.assertAlmostEqual(R[p], R2[p], places=9); self.assertAlmostEqual(SE[p], SE2[p], places=9)
        self.assertGreater(max(abs(R[p] - R3[p]) for p in R), 1.0)    # (p0, p1)'s 50 games do move the fit at cap 20

    def test_default_cap(self):
        self.assertEqual(el.PAIR_CAP, 200)
        rows = series('a', 'b', 150, 250) + series('b', 'c', 5, 9, 'n')
        R, _, _, _ = el.fit(rows); R2, _, _, _ = el.fit(rows, pair_cap=200)
        self.assertEqual(dict(R), dict(R2))


class RecoveryTest(unittest.TestCase):
    """F1/F2 regression: ratings simulated from known truth on a near-neighbour schedule, as the replica pairs bots.
    30 players evenly from 500 to 2500 (SD 597, the real field's spread), each meeting its 5 nearest on either side 12
    times (1,620 games, 108 per player, the real file's density), 20 replications, seeded. Measured at this seed: the
    slope of fit on truth has mean 0.987 and SD 0.066 per replication, so the mean's SE is 0.015 and [0.95, 1.05] is
    +-3.4 SE around 1; the +-1.96 SE intervals (600, binomial SD 0.009 at 95%) cover 0.930; the z-scores' SD is 1.11.
    The prior of 1 virtual win + 1 loss (before the audit) gives slope 0.806, coverage 0.418 and z SD 2.56."""
    M, K, N, REPS = 30, 5, 12, 20

    def simulate(self, prior):
        rng = random.Random(20261010); truth = [500 + 2000 * i / (self.M - 1) for i in range(self.M)]
        sched = [(i, j) for i in range(self.M) for j in range(i + 1, min(self.M, i + self.K + 1)) for _ in range(self.N)]
        slopes, zs = [], []
        for _ in range(self.REPS):
            rows = []
            for g, (i, j) in enumerate(sched):
                a, b = (i, j) if g % 2 else (j, i)
                rows.append(row(f'p{a}', f'p{b}', 'A' if rng.random() < el.expected(truth[a], truth[b]) else 'B', m=f'm{g}'))
            R, SE, _, _ = el.fit(rows, prior=prior)
            fit = [R[f'p{i}'] for i in range(self.M)]
            mt, mf = statistics.fmean(truth), statistics.fmean(fit)
            slopes.append(sum((t - mt) * (f - mf) for t, f in zip(truth, fit)) / sum((t - mt) ** 2 for t in truth))
            zs += [((fit[i] - mf) - (truth[i] - mt)) / SE[f'p{i}'] for i in range(self.M)]
        return statistics.fmean(slopes), sum(abs(z) <= 1.96 for z in zs) / len(zs), statistics.pstdev(zs)

    def test_recovery_and_coverage(self):
        slope, cover, zsd = self.simulate(el.PRIOR)
        self.assertTrue(0.95 <= slope <= 1.05, slope)        # F1: the scale is not compressed (0.987)
        self.assertTrue(0.90 <= cover <= 0.99, cover)        # F2: +- 1.96 SE of R - mean covers about 95% (0.930)
        self.assertTrue(0.85 <= zsd <= 1.25, zsd)            # (1.11)

    def test_old_prior_fails_it(self):
        """The test discriminates: the pre-audit prior compresses the scale well outside the band."""
        slope, cover, _ = self.simulate(1.0)
        self.assertLess(slope, 0.90); self.assertLess(cover, 0.80)


class DedupeTest(unittest.TestCase):
    def test_repeat_kept_once_first(self):
        first = row('X', 'Y', 'A', rounds=812); again = row('X', 'Y', 'B', rounds=812, run='u')
        out = el.dedupe([first, again])
        self.assertEqual(len(out), 1); self.assertIs(out[0], first)

    def test_both_orientations_kept(self):
        self.assertEqual(len(el.dedupe([row('X', 'Y', 'A'), row('X', 'Y', 'A', seed='map-rev')])), 2)

    def test_swapped_label_twin_merged(self):
        """D1: (X, Y, M, map-rev) puts X on the B spawns: the same game as (Y, X, M, map); it was counted twice."""
        twin = [row('X', 'Y', 'A', seed='map-rev'), row('Y', 'X', 'B', seed='map')]
        self.assertEqual(len(el.dedupe(twin)), 1)
        _, _, g, W = el.fit(twin)
        self.assertEqual((g['X'], W['X'], g['Y'], W['Y']), (1, 1, 1, 0))
        self.assertEqual(len(el.dedupe([row('Y', 'X', 'B'), row('X', 'Y', 'A', seed='map-rev')])), 1)

    def test_swapped_labels_same_orientation_are_different_games(self):
        self.assertEqual(len(el.dedupe([row('X', 'Y', 'A'), row('Y', 'X', 'A')])), 2)
        self.assertEqual(len(el.dedupe([row('X', 'Y', 'A', seed='7'), row('Y', 'X', 'B', seed='7')])), 2)

    def test_blank_seed_is_map(self):
        """D3: seed '' (or none) is documented as the map's own seed, the same game as 'map'; they were keyed apart."""
        self.assertEqual(len(el.dedupe([row('X', 'Y', 'A', seed=''), row('X', 'Y', 'A', seed='map')])), 1)
        nokey = row('X', 'Y', 'A'); del nokey['seed']
        self.assertEqual(len(el.dedupe([nokey, row('X', 'Y', 'A', seed='map')])), 1)
        self.assertEqual(len(el.dedupe([row('X', 'Y', 'A', seed='map'), row('X', 'Y', 'A', seed='123')])), 2)
        self.assertEqual(len(el.dedupe([row('X', 'Y', 'A', seed='1'), row('X', 'Y', 'A', seed='2')])), 2)

    def test_coin_dropped(self):
        out = el.dedupe([row('X', 'Y', 'A', reason='COIN'), row('X', 'Y', 'B', reason=''),
                         row('X', 'Y', 'B', reason='TB_ISL', m='N')])
        self.assertEqual([r['reason'] for r in out], ['', 'TB_ISL'])

    def test_invalid_winner_does_not_shadow_a_valid_duplicate(self):
        """D2: an invalid row is skipped before its key is seen, so a later valid copy survives."""
        out, err = quiet(el.dedupe, [row('X', 'Y', ''), row('X', 'Y', 'A')])
        self.assertEqual([r['winner'] for r in out], ['A'])
        self.assertIn('skipped 1 rows', err)


class LoadAppendTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.saved = el.GAMES; el.GAMES = os.path.join(self.d, 'games.csv')

    def tearDown(self):
        el.GAMES = self.saved; shutil.rmtree(self.d)

    def test_missing_file(self):
        self.assertEqual(el.load(), [])

    def test_append_round_trip(self):
        el.append([row('X', 'Y', 'A', run='r', seq=1), row('Y', 'X', 'B', run='r', seq=2, m='N')])
        el.append([row('X', 'Z', 'A', run='s', seq=1)])
        text = Path(el.GAMES).read_text()
        self.assertEqual(text.count('run,seq,teamA'), 1)
        rows = el.load()
        self.assertEqual([list(r) for r in rows], [el.HDR] * 3)
        self.assertEqual([r['teamB'] for r in rows], ['Y', 'X', 'Z'])
        _, _, g, W = el.fit(rows)
        self.assertEqual((g['X'], W['X']), (3, 3))

    def test_append_to_empty_file_writes_header(self):
        """D4: a 0-byte games.csv got no header, so the first game became the header and fit raised KeyError."""
        write(el.GAMES, '')
        el.append([row('X', 'Y', 'A', run='r', seq=1), row('Y', 'X', 'B', run='r', seq=2, m='N')])
        rows = el.load()
        self.assertEqual(len(rows), 2); self.assertEqual(list(rows[0]), el.HDR)
        el.fit(rows)

    def test_mixed_line_endings(self):
        write(el.GAMES, ','.join(el.HDR) + '\r\n' + 'r,1,X,Y,M,A,10,,map\r\n' + 'g,1,Y,X,M,B,20,,map\n' + 'g,2,X,Y,N,B,30,,map-rev\n')
        rows = el.load()
        self.assertEqual([(r['run'], r['seed']) for r in rows], [('r', 'map'), ('g', 'map'), ('g', 'map-rev')])

    def test_short_and_invalid_rows_skipped(self):
        """D2: a short line (winner None) and a blank winner were read as B wins; load() skips them with a count."""
        write(el.GAMES, ','.join(el.HDR) + '\n' + 'r,1,X,Y,M,A,10,,map\n' + 'r,2,X,Y,N\n' + 'r,3,X,Y,O,,10,,map\n')
        rows, err = quiet(el.load)
        self.assertEqual([r['seq'] for r in rows], ['1'])
        self.assertIn('skipped 2 rows with winner not A|B', err)


class FieldScoreFnTest(unittest.TestCase):
    def test_values(self):
        R = {'p': 1500.0, 'a': 1500.0, 'b': 1900.0}
        self.assertAlmostEqual(el.field_score(R, 'p', ['a', 'b']), (0.5 + 1 / 11) / 2, places=12)
        self.assertEqual(el.field_score(R, 'p', []), 0.0)

    def test_matches_field_score_tool_with_an_unrated_bot(self):
        """C4: ELO.md's field score and field_score.py's agree, over the RATED bots: an unmet bot used to count at the
        defaultdict's 1500 in ELO.md only."""
        fs = load('field_score', 'field_score.py')
        rows = series('us:b1', 'x1', 8, 10) + series('x1', 'x2', 6, 10, 'n') + series('us:b1', 'x2', 9, 10, 'o')
        R, _, games, _ = el.fit(rows)
        bots = ['x1', 'x2', 'ghost']
        rated = [b for b in bots if games[b] > 0]
        self.assertEqual(rated, ['x1', 'x2'])
        self.assertAlmostEqual(el.field_score(R, 'us:b1', rated), fs.metrics(R['us:b1'], [R[b] for b in rated])[0], places=12)
        self.assertNotAlmostEqual(el.field_score(R, 'us:b1', bots), el.field_score(R, 'us:b1', rated), places=3)


class IncumbentTest(unittest.TestCase):
    """C1: with package-named builds the fallback found no g_iterN but g_iter0, the oldest, ~250 points weak."""
    ROWS = [row('us:g_iter0', 'x', 'A'), row('us:c_nav4', 'x', 'A'), row('us:c_aura2', 'x', 'A'), row('us:c_flee3', 'x', 'B')]
    HIST = [{'event': 'init', 'package': 'g_iter0'}, {'event': 'trial-start', 'package': 'c_nav4'},
            {'event': 'accept', 'package': 'c_nav4'}, {'event': 'trial-start', 'package': 'c_aura2'},
            {'event': 'accept', 'package': 'c_aura2'}, {'event': 'trial-start', 'package': 'c_flee3'},
            {'event': 'reject', 'package': 'c_flee3'}]

    def test_ours_and_baselines(self):
        """D5: the stock examplefuncsplayer, submitted as 'us:' for a smoke test, is rated but is not one of our builds."""
        self.assertTrue(el.is_ours('us:c_aura2')); self.assertEqual(el.build_of('us:c_aura2'), 'c_aura2')
        self.assertFalse(el.is_ours('us:examplefuncsplayer')); self.assertIsNone(el.build_of('us:examplefuncsplayer'))
        self.assertFalse(el.is_ours('examplefuncsplayer')); self.assertFalse(el.is_ours('jmerle.camel_case'))
        self.assertIn('examplefuncsplayer', el.BASELINES)

    def test_validated_build_with_games_wins(self):
        st = {'validated': {'package': 'c_nav4'}, 'history': self.HIST}
        self.assertEqual(el.incumbent(self.ROWS, st), 'c_nav4')       # even though c_aura2 and c_flee3 played later

    def test_no_state_is_our_latest_game(self):
        self.assertEqual(el.incumbent(self.ROWS[:3], {}), 'c_aura2')
        self.assertEqual(el.incumbent(self.ROWS, {}), 'c_flee3')      # with no history a rejected candidate can win

    def test_validated_without_games_walks_history(self):
        st = {'validated': {'package': 'c_aura3'}, 'history': self.HIST + [{'event': 'accept', 'package': 'c_aura3'}]}
        self.assertEqual(el.incumbent(self.ROWS, st), 'c_aura2')      # the reject of c_flee3 is skipped
        st = {'validated': {'package': 'c_new'}, 'history': self.HIST[:3]}
        self.assertEqual(el.incumbent(self.ROWS, st), 'c_nav4')       # not g_iter0

    def test_baseline_never(self):
        rows = self.ROWS[:2] + [row('us:examplefuncsplayer', 'x', 'B')]
        self.assertEqual(el.incumbent(rows, {}), 'c_nav4')
        self.assertIsNone(el.incumbent([row('us:examplefuncsplayer', 'x', 'B')], {}))
        self.assertIsNone(el.incumbent([], {}))

    def test_state_file(self):
        d = tempfile.mkdtemp(); saved = el.STATE; el.STATE = os.path.join(d, 'ladder-state.json')
        try:
            self.assertEqual((el.ladder_state(), el.validated_build()), ({}, None))
            write(el.STATE, json.dumps({'validated': {'package': 'c_nav4'}, 'history': self.HIST}))
            self.assertEqual(el.validated_build(), 'c_nav4'); self.assertEqual(el.incumbent(self.ROWS), 'c_nav4')
            for bad in ('{not json', '[1, 2]'):
                write(el.STATE, bad)
                self.assertEqual((el.ladder_state(), el.validated_build()), ({}, None))
        finally:
            el.STATE = saved; shutil.rmtree(d)


class EloScriptTest(unittest.TestCase):
    """tools/elo.py run end to end on a fixture in a temporary tree (its REPO is its own location, so nothing touches
    progress/). The fixture, per bot: botA: the incumbent c_new 10-19 (29 games, *), the old g_iter0 20-10; botB:
    c_new 15-15 as team B (30 games, no *); botC: g_iter0 3-0, then c_old 2-1; botD: only the stock
    examplefuncsplayer (0-3); botE: the rejected candidate c_cand 2-0, our last games; botF: no games. Field bots
    play each other in a ring. Plus a duplicate, a swapped-label twin and a blank-winner row."""
    BOTS = ['botA', 'botB', 'botC', 'botD', 'botE', 'botF']
    STATE = {'validated': {'package': 'c_new'},
             'history': [{'event': 'init', 'package': 'g_iter0'}, {'event': 'trial-start', 'package': 'c_old'},
                         {'event': 'accept', 'package': 'c_old'}, {'event': 'trial-start', 'package': 'c_new'},
                         {'event': 'accept', 'package': 'c_new'}, {'event': 'trial-start', 'package': 'c_cand'},
                         {'event': 'reject', 'package': 'c_cand'}]}

    @classmethod
    def games(cls):
        g = [row('us:g_iter0', 'botC', 'A', m=f'c{i}') for i in range(3)]
        g += [row('botA', 'us:g_iter0', 'B' if i < 20 else 'A', m=f'a{i}') for i in range(30)]
        g += [row('us:examplefuncsplayer', 'botD', 'B', m=f'd{i}') for i in range(3)]
        g += [row('us:c_old', 'botC', 'A' if i < 2 else 'B', m=f'o{i}') for i in range(3)]
        g += [row('us:c_new', 'botA', 'A' if i < 10 else 'B', m=f'n{i}') for i in range(29)]
        g += [row('botB', 'us:c_new', 'B' if i < 15 else 'A', m=f'b{i}') for i in range(30)]
        for x, y in [('botA', 'botB'), ('botB', 'botC'), ('botC', 'botD'), ('botD', 'botE'), ('botE', 'botA')]:
            g += [row(x, y, 'A' if i < 6 else 'B', m=f'{x}{y}{i}') for i in range(10)]
        g += [row('botA', 'botB', 'B', m='botAbotB0', run='dup')]               # a repeat of an existing game
        g += [row('botB', 'botA', 'A', m='botAbotB1', seed='map-rev', run='twin')]  # its swapped-label twin
        g += [row('botC', 'botE', '', m='blank')]                                # no winner: skipped
        g += [row('us:c_cand', 'botE', 'A', m=f'e{i}') for i in range(2)]
        return [dict(r, seq=i) for i, r in enumerate(g)]

    @classmethod
    def tree(cls, state):
        d = Path(tempfile.mkdtemp())
        (d / 'tools').mkdir(); (d / 'progress').mkdir()
        for b in ('c_new', 'c_old', 'c_cand', 'c_next'):
            (d / 'src' / b).mkdir(parents=True)
        for f in ('elo.py', 'elolib.py'):
            shutil.copy(TOOLS / f, d / 'tools' / f)
        (d / 'tools' / 'field.txt').write_text('# fixture\n' + '\n'.join(cls.BOTS) + '\n')
        if state is not None:
            (d / 'progress' / 'ladder-state.json').write_text(json.dumps(state))
        with open(d / 'progress' / 'games.csv', 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=el.HDR); w.writeheader()
            for r in cls.games():
                w.writerow(r)
        return d

    @classmethod
    def run_elo(cls, d, *args):
        return subprocess.run([sys.executable, str(d / 'tools' / 'elo.py'), '--quiet', *args], capture_output=True,
                              text=True, timeout=120)

    @classmethod
    def setUpClass(cls):
        cls.d = cls.tree(cls.STATE)
        cls.out = cls.run_elo(cls.d)
        cls.md = (cls.d / 'progress' / 'ELO.md').read_text()
        cls.rows = [r for r in cls.games() if r['winner'] in ('A', 'B')]
        cls.R, cls.SE, cls.g, cls.W = el.fit(cls.rows)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d)

    def cells(self, first):
        line = next(l for l in self.md.splitlines() if l.startswith(f'| {first} |'))
        return [c.strip() for c in line.strip('|').split('|')]

    def test_runs_and_skips_the_blank_winner(self):
        self.assertEqual(self.out.returncode, 0, self.out.stderr)
        self.assertIn('skipped 1 rows with winner not A|B', self.out.stderr)

    def test_header_counts(self):
        """D1 and D5 in the header: 152 rows read (the blank one skipped), 6 + 3 baseline games apart from ours, 150
        distinct (the repeat and the twin count once)."""
        n = len(self.rows); ours = 3 + 30 + 3 + 29 + 30 + 2
        self.assertEqual((n, len(el.dedupe(self.rows))), (152, 150))
        self.assertIn(f'{n} games ({ours} ours, 3 of the stock examplefuncsplayer, {n - ours - 3} between field bots on '
                      f'the ladder replica), 150 distinct', self.md)
        self.assertIn('5 of 6 ladder bots met', self.md)
        self.assertIn(f'relative to the mean rating of all {len(self.g)} players', self.md)
        self.assertIn('against every rated ladder bot (5 of 6)', self.md)

    def test_our_builds_table(self):
        """Every cell of the builds table; the baseline is not a build (D5); the field score is over the rated bots (C4)."""
        rated = self.BOTS[:5]
        table = sorted([(self.R[p], p) for p in rated + ['us:g_iter0', 'us:c_old', 'us:c_new', 'us:c_cand']], key=lambda x: -x[0])
        rank = {p: i + 1 for i, (_, p) in enumerate(table)}
        builds = [l.split('|')[1].strip() for l in self.md.split('| build |')[1].split('\n\n')[0].splitlines()[2:]]
        self.assertEqual(builds, [el.build_of(p) for _, p in table if el.is_ours(p)])
        for b in ('g_iter0', 'c_old', 'c_new', 'c_cand'):
            p = 'us:' + b; up = [x for x in rated if self.R[x] > self.R[p]]
            vh = f"{el.field_score(self.R, p, up):.1%} (vs {len(up)})" if up else '-'
            self.assertEqual(self.cells(b), [b, f'{self.R[p]:.0f} +- {1.96 * self.SE[p]:.0f}', f'{rank[p]} of 9', str(self.g[p]),
                                             f'{self.W[p]}-{self.g[p] - self.W[p]}', f'{el.field_score(self.R, p, rated):.1%}', vh])
        self.assertNotIn('examplefuncsplayer |', self.md)
        self.assertEqual((self.g['us:g_iter0'], self.W['us:g_iter0']), (33, 23))

    def test_ladder_table_and_our_record(self):
        """The incumbent's record first, whatever the count (* below 30), our wins first, also as team B; else the most
        recent build that met the bot; blank when none did (a baseline is not ours)."""
        self.assertIn('by the incumbent (c_new)', self.md)
        expect = {'botA': '34% (c_new 10-19*)', 'botB': '50% (c_new 15-15)', 'botC': '67% (c_old 2-1*)', 'botD': '',
                  'botE': '100% (c_cand 2-0*)'}
        for b, rec in expect.items():
            line = next(l for l in self.md.splitlines() if f'| {b} |' in l)
            c = [x.strip() for x in line.strip('|').split('|')]
            self.assertEqual(c[1:], [b, f'{self.R[b]:.0f}', f'{1.96 * self.SE[b]:.0f}', str(self.g[b]),
                                     f'{self.W[b]}-{self.g[b] - self.W[b]}', rec])
        self.assertIn('| **us:c_new** |', self.md)
        self.assertEqual(len([l for l in self.md.splitlines() if l.startswith('| ') and ' of 9 |' not in l and
                              l.split('|')[1].strip().isdigit()]), 9)
        self.assertTrue(self.md.rstrip().endswith('Not yet met: botF'))

    def test_build_option(self):
        """C3: --build of a build with no rated games printed 1500 +- inf and a field score; it now exits non-zero."""
        out = self.run_elo(self.d, '--build', 'c_new')
        self.assertEqual(out.returncode, 0)
        self.assertTrue(out.stdout.startswith(f"c_new: {self.W['us:c_new']}/{self.g['us:c_new']} = "), out.stdout)
        self.assertIn(f"expected score vs the 5-rated-bot field {el.field_score(self.R, 'us:c_new', self.BOTS[:5]):.1%}", out.stdout)
        out = self.run_elo(self.d, '--build', 'g_iter4')
        self.assertNotEqual(out.returncode, 0)
        self.assertIn('g_iter4 has no rated games', out.stderr); self.assertEqual(out.stdout, '')

    def test_pools(self):
        rated = self.BOTS[:5]; me = self.R['us:c_new']
        band = self.run_elo(self.d, '--band', '2')
        self.assertEqual(band.stdout.split(), sorted(rated, key=lambda b: abs(self.R[b] - me))[:2])
        old = self.run_elo(self.d, '--band', '2', '--as', 'c_old')
        self.assertEqual(old.stdout.split(), sorted(rated, key=lambda b: abs(self.R[b] - self.R['us:c_old']))[:2])
        pool = self.run_elo(self.d, '--pool', '3')
        above = sorted((b for b in rated if self.R[b] >= me), key=lambda b: self.R[b])
        below = sorted((b for b in rated if self.R[b] < me), key=lambda b: -self.R[b])
        self.assertEqual(pool.stdout.split(), (above + below)[:3])
        est = self.run_elo(self.d, '--established', '3')
        self.assertEqual(est.stdout.split(), ['botA', 'botB', 'botC'])    # 59, 30, 6 games against our builds
        ch = self.run_elo(self.d, '--challenge', '5')                      # botB beat us 15 of 30; botD only the baseline
        self.assertEqual(ch.stdout.split(), ['botB'])

    def test_as_unknown_build(self):
        """C3: --as a build with no games centres on the incumbent, with a note on stderr (a typo flagged as one)."""
        base = self.run_elo(self.d, '--band', '2').stdout
        typo = self.run_elo(self.d, '--band', '2', '--as', 'c_nwe')
        self.assertEqual(typo.stdout, base)
        self.assertIn('--as c_nwe has no rated games (src/c_nwe does not exist: a typo?); centring on the incumbent c_new', typo.stderr)
        cand = self.run_elo(self.d, '--band', '2', '--as', 'c_next')
        self.assertEqual(cand.stdout, base)
        self.assertIn('--as c_next has no rated games; centring on the incumbent c_new', cand.stderr)

    def test_incumbent_fallbacks(self):
        """C1 end to end: the validated build without games falls back to the latest accepted build with games (not
        g_iter0); with no state file, to the build of our latest game."""
        st = json.loads(json.dumps(self.STATE)); st['validated']['package'] = 'c_next'
        for state, want in ((st, 'c_new'), (None, 'c_cand')):
            d = self.tree(state)
            try:
                self.assertEqual(self.run_elo(d).returncode, 0)
                self.assertIn(f'by the incumbent ({want})', (d / 'progress' / 'ELO.md').read_text())
            finally:
                shutil.rmtree(d)


class FieldScoreToolTest(unittest.TestCase):
    """tools/field_score.py's pure parts (its charts and main() write progress/ and are not run here)."""

    @classmethod
    def setUpClass(cls):
        cls.fs = load('field_score', 'field_score.py')

    def test_metrics_exact(self):
        fs, vh, nup, rank = self.fs.metrics(1500.0, [1400.0, 1500.0, 1600.0, 1700.0])
        e1, e2 = 1 / (1 + 10 ** 0.25), 1 / (1 + 10 ** 0.5)               # E(1500, 1600), E(1500, 1700); E(1500, 1400) = 1 - e1
        self.assertAlmostEqual(fs, (1 - e1 + 0.5 + e1 + e2) / 4, places=12); self.assertAlmostEqual(fs, 0.43506, places=5)
        self.assertAlmostEqual(vh, (e1 + e2) / 2, places=12); self.assertAlmostEqual(vh, 0.30009, places=5)
        self.assertEqual((nup, rank), (2, 3))                             # the tie at 1500 is not above
        fs, vh, nup, rank = self.fs.metrics(1800.0, [1400.0, 1700.0])
        self.assertTrue(math.isnan(vh)); self.assertEqual((nup, rank), (0, 1))

    def test_fit_log_weighted_and_scaled(self):
        """Weighted least squares with unequal SEs on noisy data, against the normal equations solved independently;
        the covariance is scaled by the reduced chi-square when it exceeds 1, and never scaled down."""
        ts = [0.0, 0.4, 1.1, 1.9, 2.6, 3.0]; ses = [20.0, 35.0, 25.0, 50.0, 30.0, 40.0]
        for noise in ([90, -60, 75, -120, 40, -20], [2, -1, 1, -2, 1, 0]):
            rs = [1800 + 100 * math.log1p(t) + e for t, e in zip(ts, noise)]
            r0, a, cov = self.fs.fit_log(ts, rs, ses)
            w = [1 / s ** 2 for s in ses]; x = [math.log1p(t) for t in ts]
            A = [[sum(w), sum(wi * xi for wi, xi in zip(w, x))], [sum(wi * xi for wi, xi in zip(w, x)), sum(wi * xi * xi for wi, xi in zip(w, x))]]
            Ai = invert(A); b = [sum(wi * y for wi, y in zip(w, rs)), sum(wi * xi * y for wi, xi, y in zip(w, x, rs))]
            e0, e1 = Ai[0][0] * b[0] + Ai[0][1] * b[1], Ai[1][0] * b[0] + Ai[1][1] * b[1]
            chi = sum(wi * (y - e0 - e1 * xi) ** 2 for wi, xi, y in zip(w, x, rs)); k = max(1.0, chi / (len(ts) - 2))
            self.assertAlmostEqual(r0, e0, places=6); self.assertAlmostEqual(a, e1, places=6)
            for i in range(2):
                for j in range(2):
                    self.assertAlmostEqual(cov[i][j], Ai[i][j] * k, places=9)
            self.assertEqual(k > 1, noise[0] == 90)

    def test_submissions(self):
        d = tempfile.mkdtemp(); saved = el.STATE; el.STATE = os.path.join(d, 'ladder-state.json')
        try:
            write(el.STATE, json.dumps({'history': [
                {'event': 'init', 'package': 'g0', 'at': '2026-10-08T02:35:39+00:00'},
                {'event': 'trial-start', 'package': 'c1', 'at': '2026-10-10T13:13:57+00:00'},
                {'event': 'accept', 'package': 'c1', 'at': '2026-10-10T14:00:00+00:00'},
                {'event': 'trial-start', 'package': 'c2', 'at': '2026-10-10T15:00:00Z'},
                {'event': 'reject', 'package': 'c2', 'at': '2026-10-10T16:00:00+00:00'},
                {'event': 'trial-start', 'package': 'c2', 'at': '2026-10-11T15:00:00+00:00'}]}))
            s = self.fs.submissions()
            self.assertEqual(s['g0'], (self.fs.dt.datetime(2026, 10, 7, 19, 35, 39), True))   # init counts as accepted
            self.assertEqual(s['c1'], (self.fs.dt.datetime(2026, 10, 10, 6, 13, 57), True))    # UTC -> PDT
            self.assertEqual(s['c2'], (self.fs.dt.datetime(2026, 10, 10, 8, 0, 0), False))     # first trial-start kept
        finally:
            el.STATE = saved; shutil.rmtree(d)

    def test_horizons_and_exclusions(self):
        self.assertEqual([h[1].strftime('%m-%d %H:%M') for h in self.fs.HORIZONS], ['10-14 00:00', '10-21 00:00', '10-28 00:00', '11-04 00:00'])
        self.assertIs(self.fs.EXCLUDE, el.BASELINES); self.assertEqual(self.fs.MIN_GAMES, 30)


class RealDataTest(unittest.TestCase):
    """Invariants of progress/games.csv (read only): what the writers promise and dedupe assumes."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(el.GAMES):
            raise unittest.SkipTest('no progress/games.csv')
        with open(el.GAMES) as fh:
            cls.rows = list(csv.DictReader(fh))

    def test_rows(self):
        self.assertEqual([r for r in self.rows if r['winner'] not in ('A', 'B')], [])
        self.assertEqual([r for r in self.rows if r['teamA'] == r['teamB']], [])
        runs = collections.Counter((r['run'], r['seq']) for r in self.rows)
        self.assertEqual([k for k, v in runs.items() if v > 1], [])
        field = set(el.ladder_bots())
        self.assertEqual(sorted({t for r in self.rows for t in (r['teamA'], r['teamB'])
                                 if not t.startswith('us:') and t not in field}), [])

    def test_replays_agree(self):
        """dedupe keeps one row per physical game: when any copy of a game (a repeat or a swapped-label twin) was decided
        before round 2000, every copy has the same winner and round count (only round-2000 games may end on the unseeded
        coin flip)."""
        grp = collections.defaultdict(set)
        for r in self.rows:
            if r['reason'] == 'COIN':
                continue
            a, b, s = r['teamA'], r['teamB'], r['seed'] or 'map'
            if s == 'map-rev':
                a, b, s = b, a, 'map'
            grp[a, b, r['map'], s].add((r['teamA'] if r['winner'] == 'A' else r['teamB'], r['rounds']))
        bad = {k: v for k, v in grp.items() if len(v) > 1 and any(int(x[1]) < 2000 for x in v)}
        self.assertEqual(bad, {})


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=0).result
    print(f"test_elo: {r.testsRun} tests, {len(r.failures)} failures, {len(r.errors)} errors, {len(r.skipped)} skipped")
    sys.exit(0 if r.wasSuccessful() else 1)
