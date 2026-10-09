"""Shared ladder bookkeeping over progress/games.csv (one row per scrimmage, in play order).
Columns: run,seq,teamA,teamB,map,winner(A|B),rounds,reason,seed. Our team appears as 'us:<build>'.

Ratings are a batch Bradley-Terry fit over every game at once, on the Elo scale (400 points = 10:1 odds), and each of
our builds is its own player: a sequential Elo depends on play order and lets a new build inherit an old one's rating.
A weak prior (one virtual win and one loss against a 1500 anchor) keeps unbeaten or winless records finite; the anchor
fixes the scale at 1500. Each pair of players counts at most PAIR_CAP games in the fit (its games and wins scaled down
in proportion; records shown stay raw), so one heavily repeated pairing cannot pull the fit when matchups are not
transitive. 200 games pin a pair's win rate to about +- 3.5 points.
The reason column holds a code (REASONS); seed '' or 'map' is the map file's own seed, 'map-rev' the same map with the
HQ ownership flipped (the engine's alternate-order games inside a ladder match)."""
import sys, csv, os, math, collections
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES = os.path.join(REPO, 'progress', 'games.csv')

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
    """One game per (teamA, teamB, map, seed): the engine replays the same pairing identically unless the seed differs
    (a predecessor project found 491 of 2825 ladder games were exact repeats). Keeps the first occurrence. Coin-flip
    results (reason COIN: the engine's unseeded Math.random tiebreak) carry no information and are dropped."""
    seen = set(); out = []
    for r in rows:
        if r.get('reason') == 'COIN': continue
        k = (r['teamA'], r['teamB'], r['map'], r.get('seed') or '')
        if k in seen: continue
        seen.add(k); out.append(r)
    return out
SCALE = 400 / math.log(10)
PAIR_CAP = 200
def is_ours(name): return name.startswith('us:')
def build_of(name): return name[3:] if is_ours(name) else None
def load():
    return list(csv.DictReader(open(GAMES))) if os.path.exists(GAMES) else []
def expected(ra, rb): return 1 / (1 + 10 ** ((rb - ra) / 400))
def fit(rows, prior=1.0, iters=100000, tol=1e-10, pair_cap=PAIR_CAP):
    """Bradley-Terry by minorise-maximise. -> (R, SE, games, wins): rating, standard error (Elo points,
    from the diagonal of the Fisher information), games and wins per player. Players are the names in
    teamA/teamB as written ('us:g_iter5' is a player, 'us:g_iter3' another).
    Iterates to tol (audit 2026-10-03 MEAS11: the old 3,000-iteration cap stopped every rating 30-46 points low;
    convergence takes ~24,000 iterations on ~19,000 games) and warns on stderr if iters runs out first.
    pair_cap: a pair with n > pair_cap games enters with weight pair_cap / n on each of its games (0 = no cap); the
    returned games and wins are the raw counts."""
    rows = dedupe(rows)
    W = collections.Counter(); games = collections.Counter(); N = collections.defaultdict(collections.Counter)
    Wp = collections.defaultdict(collections.Counter)   # wins of p over q
    for r in rows:
        a, b = r['teamA'], r['teamB']; win, lose = (a, b) if r['winner'] == 'A' else (b, a)
        W[win] += 1; games[a] += 1; games[b] += 1; N[a][b] += 1; N[b][a] += 1; Wp[win][lose] += 1
    f = lambda n: min(1.0, pair_cap / n) if pair_cap else 1.0                    # each game of a pair weighs f(its count)
    Ww = {p: sum(k * f(N[p][q]) for q, k in Wp[p].items()) for p in N}              # effective wins
    N = {p: {q: n * f(n) for q, n in N[p].items()} for p in N}                      # effective pair counts
    P = list(games); ix = {p: i for i, p in enumerate(P)}
    nb = [[(ix[q], n) for q, n in N[p].items()] for p in P]; w = [Ww.get(p, 0.0) + prior for p in P]
    v = [1.0] * len(P); delta = 0.0; done = not P
    for _ in range(iters):
        new = [w[i] / (sum(n / (v[i] + v[j]) for j, n in nb[i]) + 2 * prior / (v[i] + 1)) for i in range(len(P))]
        delta = max(abs(math.log(new[i] / v[i])) for i in range(len(P)))
        v = new
        if delta < tol: done = True; break
    if not done: print(f'elolib.fit: not converged after {iters} iterations (delta {delta:.2e} > tol {tol:.0e})', file=sys.stderr)
    s = {p: v[ix[p]] for p in P}
    R = collections.defaultdict(lambda: 1500.0); SE = collections.defaultdict(lambda: float('inf'))
    for p in s:
        R[p] = 1500 + SCALE * math.log(s[p])
        info = sum(n * s[p] * s[q] / (s[p] + s[q]) ** 2 for q, n in N[p].items()) + 2 * prior * s[p] / (s[p] + 1) ** 2
        SE[p] = SCALE / math.sqrt(info)
    return R, SE, games, W
def field_score(R, player, field):
    """Expected score of `player` against every bot of `field`, one game each."""
    return sum(expected(R[player], R[b]) for b in field) / len(field) if field else 0.0
def current_build(rows):
    """The incumbent: the validated build of progress/ladder-state.json when it has games, else the build of our most
    recent game among the submitted line (g_iterN), else of our most recent game.
    (2026-09-26: an unrated candidate's first block was centred on the build of our latest game -- the enclosure
    archetype's 48-game probe at 1406 -- and drew a pool 400 points weak: arm81's first block went 45-3.)"""
    v = validated_build()
    if v and any(build_of(t) == v for r in rows for t in (r['teamA'], r['teamB']) if is_ours(t)):
        return v
    last = None
    for r in reversed(rows):
        for t in (r['teamA'], r['teamB']):
            if not is_ours(t): continue
            b = build_of(t)
            if b.startswith('g_iter'): return b
            last = last or b
    return last
def ladder_bots():
    p = os.path.join(REPO, 'tools', 'field.txt')
    return [l.strip() for l in open(p) if l.strip() and not l.startswith('#')]
def append(rows):
    new = not os.path.exists(GAMES)
    with open(GAMES, 'a', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=HDR)
        if new: w.writeheader()
        for r in rows: w.writerow(r)


def validated_build():
    """The validated build (a package name) recorded by tools/ladder_policy.py in progress/ladder-state.json, or None.
    Since the replica cutover (2026-10-07) accepted builds keep their package names (c_nav5, ...), not g_iterN."""
    import json
    try:
        with open(os.path.join(REPO, 'progress', 'ladder-state.json')) as fh:
            return ((json.load(fh).get('validated') or {}).get('package')) or None
    except (OSError, ValueError):
        return None


def accepted_builds(players):
    """Our accepted snapshots us:g_iterN among the players, in accept (numeric) order."""
    import re
    b = [(int(m.group(1)), p) for p in players if (m := re.fullmatch(r'us:g_iter(\d+)', p))]
    return [p for _, p in sorted(b)]
