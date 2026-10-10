"""Shared ladder bookkeeping over progress/games.csv (one row per scrimmage, in play order).
Columns: run,seq,teamA,teamB,map,winner(A|B),rounds,reason,seed. Our team appears as 'us:<build>'; a stock baseline
submitted under 'us:' as a smoke test (BASELINES) is a rated player but not one of our builds.

Ratings are a batch Bradley-Terry fit over every game at once, on the Elo scale (400 points = 10:1 odds), and each of
our builds is its own player: a sequential Elo depends on play order and lets a new build inherit an old one's rating.
A prior of PRIOR virtual wins and as many virtual losses against a 1500 anchor, per player, keeps unbeaten or winless
records finite and sets the level (the score equations force sum tanh((R - 1500) / (2 SCALE)) = 0, so the mean sits
near 1500, not at it): compare ratings within one fit, never across fits. The prior must stay small. Games pair near
neighbours, so they pin each rating against its neighbours but the stretch of the whole scale only weakly, and every
player's pull toward 1500 points inward along that stretch (audit 2026-10-10 F1: at 1 virtual win + 1 loss the
field's spread came out 13% narrow, our builds 69-96 points low against the field, and the +- 95% intervals covered
40-55% of the time). 0.1 is unbiased on the real schedule (simulated slope 0.997); much smaller drives a short
perfect record to an extreme (the 0-6 examplefuncsplayer: 835 at 0.1, 435 at 0.01, 35 at 0.001).
Each pair of players counts at most PAIR_CAP games in the fit (its games and wins scaled down in proportion; records
shown stay raw), so one heavily repeated pairing cannot pull the fit when matchups are not transitive. 200 games pin a
pair's win rate to about +- 3.5 points.
The reason column holds a code (REASONS); seed '' or 'map' is the map file's own seed, 'map-rev' the same map with the
HQ ownership flipped (the engine's alternate-order games inside a ladder match)."""
import sys, csv, os, math, collections, operator
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES = os.path.join(REPO, 'progress', 'games.csv')
STATE = os.path.join(REPO, 'progress', 'ladder-state.json')   # tools/ladder_policy.py

# engine 3.0.15 Server.java:613-634 end-of-match reasons -> codes (a 40-character cut would merge all tiebreaks)
REASONS = [
    ('capturing 75% of sky islands', 'ISL75'),
    ('having more sky islands', 'TB_ISL'),
    ('more reality anchors', 'TB_ANCH'),
    ('more elixir net worth', 'TB_EX'),
    ('more mana net worth', 'TB_MN'),
    ('more adamantium net worth', 'TB_AD'),
    ('coin flip', 'COIN'),
    ('resigned', 'RESIGN'),
]


def reason_code(text):
    """Engine 'Reason:' text (or an existing code) -> code."""
    text = text or ''
    if text in {c for _, c in REASONS}:
        return text
    for k, c in REASONS:
        if k in text:
            return c
    return 'OTHER'
HDR = ['run', 'seq', 'teamA', 'teamB', 'map', 'winner', 'rounds', 'reason', 'seed']
def dedupe(rows):
    """One game per (A-spawn owner, B-spawn owner, map, seed): the engine replays the same pairing identically unless
    the seed differs (a predecessor project found 491 of 2825 ladder games were exact repeats). 'map-rev' with X as
    team A puts X on the B spawns: the same game as (Y, X) on 'map' (audit 2026-10-10 D1: 79 such twins counted twice,
    every decisive one with the same winner and round count); seed '' is 'map' (D3). Keeps the first occurrence.
    Coin-flip results (reason COIN: the engine's unseeded Math.random tiebreak) carry no information and are dropped;
    so are rows whose winner is not A or B, with a count on stderr (D2: they were counted as B wins)."""
    seen = set(); out = []; bad = 0
    for r in rows:
        if r.get('reason') == 'COIN': continue
        if r.get('winner') not in ('A', 'B'): bad += 1; continue
        a, b, s = r['teamA'], r['teamB'], (r.get('seed') or 'map')
        if s == 'map-rev': a, b, s = b, a, 'map'   # X as team A on the B spawns = (Y, X) on the map's own orientation
        k = (a, b, r['map'], s)
        if k in seen: continue
        seen.add(k); out.append(r)
    if bad: print(f'elolib.dedupe: skipped {bad} rows with winner not A|B', file=sys.stderr)
    return out
SCALE = 400 / math.log(10)
PAIR_CAP = 200
PRIOR = 0.1
BASELINES = {'examplefuncsplayer'}   # stock bots once submitted as 'us:' (old replica smoke test): rated, not ours
def is_ours(name): return name.startswith('us:') and name[3:] not in BASELINES
def build_of(name): return name[3:] if is_ours(name) else None
def load():
    """The rows of progress/games.csv ([] when it is missing). Rows whose winner is not exactly A or B (a blank, a tie,
    a short line) are skipped with a count on stderr: every reader would have counted them as B wins (audit D2)."""
    if not os.path.exists(GAMES): return []
    with open(GAMES) as fh: rows = list(csv.DictReader(fh))
    ok = [r for r in rows if r.get('winner') in ('A', 'B')]
    if len(ok) < len(rows): print(f'elolib.load: skipped {len(rows) - len(ok)} rows with winner not A|B', file=sys.stderr)
    return ok
def expected(ra, rb): return 1 / (1 + 10 ** ((rb - ra) / 400))
def _sig(x): return 1 / (1 + math.exp(-x)) if x >= 0 else math.exp(x) / (1 + math.exp(x))
def _logsig(x): return -math.log1p(math.exp(-x)) if x >= 0 else x - math.log1p(math.exp(x))
def _cholesky(A):
    """Lower-triangular L with A = L L^T, A symmetric positive definite (lists of rows); pure Python, no numpy."""
    m = len(A); L = [[0.0] * m for _ in range(m)]
    for i in range(m):
        Li = L[i]
        for j in range(i + 1):
            s = A[i][j] - sum(map(operator.mul, Li[:j], L[j][:j]))
            if i == j: Li[i] = math.sqrt(s)
            else: Li[j] = s / L[j][j]
    return L
def _forward(L, b, j0=0):
    """y with L y = b, b zero above j0."""
    y = [0.0] * len(L)
    for i in range(j0, len(L)):
        y[i] = (b[i] - sum(map(operator.mul, L[i][j0:i], y[j0:i]))) / L[i][i]
    return y
def _backward(L, y):
    """x with L^T x = y."""
    m = len(L); x = [0.0] * m
    for i in reversed(range(m)):
        x[i] = (y[i] - sum(L[k][i] * x[k] for k in range(i + 1, m))) / L[i][i]
    return x
def fit(rows, prior=PRIOR, iters=100, tol=1e-10, pair_cap=PAIR_CAP):
    """Bradley-Terry MAP fit by Newton's method. -> (R, SE, games, wins): rating, standard error (Elo points), games and
    wins per player. Players are the names in teamA/teamB as written ('us:c_nav5' is a player, 'us:c_nav4' another).
    SE is the standard error of the rating minus the mean rating of all fitted players, from the centred inverse of the
    penalised information matrix (audit 2026-10-10 F2: the diagonal alone is the SE with every other rating known, and
    it understated field bots that are pinned only through each other: 91% coverage at 95% on the real schedule, down
    to two thirds of the true SE; the full inverse adds the weakly identified common level, which no comparison uses).
    Newton converges in about 10 steps (the old minorise-maximise took 7,800 at prior 1 and about 75,000 at 0.1); it
    stops when the largest step is below tol (in ln strength) and warns on stderr if iters runs out first.
    pair_cap: a pair with n > pair_cap games enters with weight pair_cap / n on each of its games (0 = no cap); the
    returned games and wins are the raw counts. Self-play rows (teamA == teamB) have no likelihood but would add
    information (shrink the SE) and inflate the counts: they are dropped with a warning (audit F5)."""
    if not prior > 0:   # explicit, not assert (python -O strips asserts)
        raise ValueError(f'fit: prior must be > 0 (it keeps winless/unbeaten ratings finite and anchors the scale at 1500), got {prior!r}')
    rows = dedupe(rows)
    nself = sum(1 for r in rows if r['teamA'] == r['teamB'])
    if nself:
        print(f'elolib.fit: dropped {nself} self-play rows (teamA == teamB)', file=sys.stderr)
        rows = [r for r in rows if r['teamA'] != r['teamB']]
    W = collections.Counter(); games = collections.Counter(); N = collections.defaultdict(collections.Counter)
    Wp = collections.defaultdict(collections.Counter)   # wins of p over q
    for r in rows:
        a, b = r['teamA'], r['teamB']; win, lose = (a, b) if r['winner'] == 'A' else (b, a)
        W[win] += 1; games[a] += 1; games[b] += 1; N[a][b] += 1; N[b][a] += 1; Wp[win][lose] += 1
    f = lambda n: min(1.0, pair_cap / n) if pair_cap else 1.0                    # each game of a pair weighs f(its count)
    R = collections.defaultdict(lambda: 1500.0); SE = collections.defaultdict(lambda: float('inf'))
    P = list(games); ix = {p: i for i, p in enumerate(P)}; m = len(P)
    if not m: return R, SE, games, W
    # one edge per pair: (i, j, effective games, effective wins of i over j)
    E = [(ix[p], ix[q], n * f(n), Wp[p][q] * f(n)) for p in P for q, n in N[p].items() if ix[p] < ix[q]]
    w = [0.0] * m                                                                   # effective wins
    for i, j, n, wi in E: w[i] += wi; w[j] += n - wi
    def objective(th):   # penalised log-likelihood
        return (sum(wi * _logsig(th[i] - th[j]) + (n - wi) * _logsig(th[j] - th[i]) for i, j, n, wi in E)
                + prior * sum(_logsig(t) + _logsig(-t) for t in th))
    def info_grad(th):   # information matrix (minus the Hessian) and gradient of the objective
        g = [w[i] + prior * (1 - 2 * _sig(th[i])) for i in range(m)]
        I = [[0.0] * m for _ in range(m)]
        for i in range(m): s = _sig(th[i]); I[i][i] = 2 * prior * s * (1 - s)
        for i, j, n, wi in E:
            p = _sig(th[i] - th[j]); c = n * p * (1 - p)
            g[i] -= n * p; g[j] -= n * (1 - p); I[i][i] += c; I[j][j] += c; I[i][j] -= c; I[j][i] -= c
        return I, g
    th = [0.0] * m; step = 0.0; done = False
    for _ in range(iters):
        I, g = info_grad(th); L = _cholesky(I); d = _backward(L, _forward(L, g))   # Newton step: I d = g
        step = max(abs(x) for x in d)
        t, L0 = 1.0, objective(th)
        while t > 1e-9:   # halve the step until the objective does not fall (it is concave: a short enough step rises)
            new = [a + t * b for a, b in zip(th, d)]
            if objective(new) >= L0 - 1e-12 * (1 + abs(L0)): break
            t /= 2
        th = new
        if step < tol: done = True; break
    if not done: print(f'elolib.fit: not converged after {iters} iterations (step {step:.2e} > tol {tol:.0e})', file=sys.stderr)
    # SE of theta_i - mean(theta): var = (I^-1)_ii - 2 (I^-1 1)_i / m + 1' I^-1 1 / m^2, with (I^-1)_ii = |column i of L^-1|^2
    L = _cholesky(info_grad(th)[0]); u = _backward(L, _forward(L, [1.0] * m)); tot = sum(u)
    for i, p in enumerate(P):
        e = [0.0] * m; e[i] = 1.0; col = _forward(L, e, i)
        var = sum(x * x for x in col[i:]) - 2 * u[i] / m + tot / (m * m)
        R[p] = 1500 + SCALE * th[i]; SE[p] = SCALE * math.sqrt(max(var, 0.0))
    return R, SE, games, W
def field_score(R, player, field):
    """Expected score of `player` against every bot of `field`, one game each. Pass rated bots only: a name with no
    games reads as R's default 1500, the prior, not a measurement."""
    return sum(expected(R[player], R[b]) for b in field) / len(field) if field else 0.0
def ladder_bots():
    with open(os.path.join(REPO, 'tools', 'field.txt')) as fh:
        return [l.strip() for l in fh if l.strip() and not l.startswith('#')]
def append(rows):
    new = not os.path.exists(GAMES) or os.path.getsize(GAMES) == 0   # an empty file needs the header too (audit D4)
    with open(GAMES, 'a', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=HDR)
        if new: w.writeheader()
        for r in rows: w.writerow(r)


def ladder_state():
    """progress/ladder-state.json (tools/ladder_policy.py) as a dict; {} when missing or unreadable."""
    import json
    try:
        with open(STATE) as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def validated_build(state=None):
    """The validated build (a package name) recorded by tools/ladder_policy.py in progress/ladder-state.json, or None.
    Since the replica cutover (2026-10-07) accepted builds keep their package names (c_nav5, ...), not g_iterN."""
    s = ladder_state() if state is None else state
    return ((s.get('validated') or {}).get('package')) or None


def incumbent(rows, state=None):
    """The incumbent (a package name): the validated build of progress/ladder-state.json when it has games, else the
    latest build of its history accepted (or the init build) that has games, else the build of our most recent game
    (with no state file this can be a rejected candidate), else None. A baseline (BASELINES) is never one.
    (2026-09-26: an unrated candidate's first block was centred on the build of our latest game -- the enclosure
    archetype's 48-game probe at 1406 -- and drew a pool 400 points weak: arm81's first block went 45-3. Audit
    2026-10-10 C1: the fallback looked for the pre-cutover g_iterN names, so it fell back to g_iter0, the oldest.)"""
    s = ladder_state() if state is None else state
    played = {build_of(t) for r in rows for t in (r['teamA'], r['teamB']) if is_ours(t)}
    v = validated_build(s)
    if v and v in played:
        return v
    for h in reversed(s.get('history') or []):
        if h.get('event') in ('accept', 'init') and h.get('package') in played:
            return h['package']
    for r in reversed(rows):
        for t in (r['teamA'], r['teamB']):
            if is_ours(t): return build_of(t)
    return None
