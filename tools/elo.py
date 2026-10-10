#!/usr/bin/env python3
"""The ladder (progress/games.csv): every field bot (tools/field.txt) plus each of our builds, rated by a batch
Bradley-Terry fit on the Elo scale (tools/elolib.py) over every recorded game: our scrimmages, and the replica's
autoscrims among field bots (owner PROMPTS 1: in spare VM cycles random ladder bots scrimmage each other).
A bot that has played no recorded game is unrated.
   tools/elo.py                        # ranking table; also writes progress/ELO.md and progress/elo.png
   tools/elo.py --band 8 --as c_nav5   # graded pool: the 8 rated bots nearest to c_nav5's rating, either side
   tools/elo.py --pool 6 --explore 2   # old pool: the 6 rated bots just above us + 2 bots with the fewest games
   tools/elo.py --build c_aura2        # one build: record (Wilson 95%), rating, expected score vs the field
--as names the build whose rating centres the pool; unset, or a build with no games yet (a candidate,
'bot'; a note on stderr), it is the incumbent (elolib.incumbent): the validated build of progress/ladder-state.json,
else the latest accepted build with games. --build of a build with no rated games exits non-zero."""
import argparse, math, os, sys, collections
# the chart needs matplotlib, which lives in tools/.venv: re-exec there when it exists
_venv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'bin', 'python')
if os.path.exists(_venv) and '.venv' not in sys.prefix: os.execv(_venv, [_venv] + sys.argv)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import elolib
ap = argparse.ArgumentParser(); ap.add_argument('--pool', type=int, default=0); ap.add_argument('--explore', type=int, default=0); ap.add_argument('--build', default='')
ap.add_argument('--as', dest='as_build', default='', help='the build whose rating centres --pool/--band')
ap.add_argument('--established', type=int, default=0,
                help='the N rated bots we have the most games against: a FIXED field, so consecutive blocks are comparable')
ap.add_argument('--challenge', type=int, default=0,
                help='the N bots that beat us at least half the time, fewest games against us first, then highest rating')
ap.add_argument('--band', type=int, default=0,
                help='the N rated bots nearest to us in rating on EITHER side: the graded pool (slightly better and slightly worse)')
ap.add_argument('--quiet', action='store_true'); a = ap.parse_args()
rows = elolib.load(); R, SE, games, wins = elolib.fit(rows)
bots = elolib.ladder_bots()
rated = [b for b in bots if games[b] > 0]; unrated = [b for b in bots if games[b] == 0]
ours = sorted({t for r in rows for t in (r['teamA'], r['teamB']) if elolib.is_ours(t)}, key=lambda p: -R[p])
inc = elolib.incumbent(rows)
if a.as_build and games['us:' + a.as_build] == 0:   # a candidate with no games yet, or a typo (audit C3)
    typo = '' if os.path.isdir(os.path.join(elolib.REPO, 'src', a.as_build)) else f' (src/{a.as_build} does not exist: a typo?)'
    print(f"elo.py: --as {a.as_build} has no rated games{typo}; centring on the incumbent {inc or '-'}", file=sys.stderr)
me = 'us:' + (a.as_build if a.as_build and games['us:' + a.as_build] > 0 else (inc or ''))
table = sorted([(R[p], p) for p in rated + ours], key=lambda x: -x[0])
rank = {p: i + 1 for i, (_, p) in enumerate(table)}
opp_games = collections.Counter(); opp_wins = collections.Counter()   # per bot, against all our builds
for r in rows:
    opp = r['teamB'] if elolib.is_ours(r['teamA']) else r['teamA'] if elolib.is_ours(r['teamB']) else None
    if opp is None: continue
    opp_games[opp] += 1; opp_wins[opp] += (r['winner'] == 'A') == (opp == r['teamA'])
if a.challenge:
    hard = [b for b in bots if opp_games[b] and opp_wins[b] * 2 >= opp_games[b]]
    hard.sort(key=lambda b: (opp_games[b], -R[b]))
    print(' '.join(hard[:a.challenge])); raise SystemExit
if a.established:
    print(' '.join(sorted(rated, key=lambda b: (-opp_games[b], -R[b]))[:a.established])); raise SystemExit
if a.pool or a.explore or a.band:
    import random
    pool = []
    if a.band: pool = sorted(rated, key=lambda b: abs(R[b] - R[me]))[:a.band]   # nearest on either side
    elif a.pool:
        above = sorted((b for b in rated if R[b] >= R[me]), key=lambda b: R[b])
        below = sorted((b for b in rated if R[b] < R[me]), key=lambda b: -R[b])
        pool = (above + below)[:a.pool]   # the closest above us, then the closest below if there are too few
    if a.explore:                         # bots we know least: fewest games, random among ties
        cand = sorted((b for b in bots if b not in pool), key=lambda b: (opp_games[b], random.random()))
        pool += cand[:a.explore]
    print(' '.join(pool)); raise SystemExit
def wilson(w, n, z=1.96):
    if n == 0: return (0, 0, 0)
    p = w / n; d = 1 + z * z / n; c = p + z * z / (2 * n); m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, (c - m) / d, (c + m) / d)
if a.build:
    p_ = 'us:' + a.build
    if games[p_] == 0: sys.exit(f"elo.py: build {a.build} has no rated games in progress/games.csv")   # not 1500 +- inf (C3)
    p, lo, hi = wilson(wins[p_], games[p_])
    print(f"{a.build}: {wins[p_]}/{games[p_]} = {p:.1%} [{lo:.1%}, {hi:.1%}]; rating {R[p_]:.0f} +- {1.96 * SE[p_]:.0f}, "
          f"rank {rank.get(p_, '-')} of {len(table)}; expected score vs the {len(rated)}-rated-bot field "
          f"{elolib.field_score(R, p_, rated):.1%}")
    raise SystemExit
ndist = len(elolib.dedupe(rows))
# Each opponent's record. RUN_MIN marks a thin record: 30 games pin a win rate to about +-18 points at 95%.
RUN_MIN = 30
last_seen = {}
for i, r in enumerate(rows):
    for t in (r['teamA'], r['teamB']):
        if elolib.is_ours(t): last_seen[t] = i
recent = sorted(ours, key=lambda p: -last_seen[p])
vs = collections.defaultdict(lambda: [0, 0])   # (build, bot) -> [bot wins, games], distinct games only
for r in elolib.dedupe(rows):
    ta, tb = r['teamA'], r['teamB']
    if elolib.is_ours(ta) == elolib.is_ours(tb): continue
    us_, opp = (ta, tb) if elolib.is_ours(ta) else (tb, ta)
    vs[us_, opp][1] += 1; vs[us_, opp][0] += (r['winner'] == 'A') == (opp == ta)
# The INCUMBENT's record against the bot whatever the count (fewer than RUN_MIN games marked *), else the most recent of
# our builds that played it (a record by an old build against a bot later builds met only a few times misleads).
# the incumbent: the validated build (progress/ladder-state.json) when it has games, else the latest accepted build with
# games (elolib.incumbent)
incumbent = 'us:' + inc if inc else None
def recent_run(bot):
    order = ([incumbent] if incumbent else []) + [p for p in recent if p != incumbent]
    for p in order:
        w, n = vs[p, bot]
        if n > 0: return f"{(n - w) / n:.0%} ({elolib.build_of(p)} {n - w}-{w}{'*' if n < RUN_MIN else ''})"   # our wins
    return ''
def higher_field(p):   # expected score against only the ladder bots rated above p
    up = [b for b in rated if R[b] > R[p]]
    return f"{elolib.field_score(R, p, up):.1%} (vs {len(up)})" if up else '-'
n_ours = sum(1 for r in rows if elolib.is_ours(r['teamA']) or elolib.is_ours(r['teamB']))
n_base = sum(1 for r in rows if not (elolib.is_ours(r['teamA']) or elolib.is_ours(r['teamB']))
             and {r['teamA'], r['teamB']} & {'us:' + b for b in elolib.BASELINES})
base = f", {n_base} of the stock {'/'.join(sorted(elolib.BASELINES))}" if n_base else ''
lines = ["# Ladder", "",
         f"{len(rows)} games ({n_ours} ours{base}, {len(rows) - n_ours - n_base} between field bots on the ladder replica), "
         f"{ndist} distinct "
         f"(a repeated pairing on the same map, orientation and seed replays the same game and counts once), "
         f"rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most "
         f"{elolib.PAIR_CAP} games (so one heavily repeated pairing cannot pull the fit); "
         f"each of our builds is its own player. {len(rated)} of {len(bots)} ladder bots met.", "",
         f"Our builds (rating +- 95%, relative to the mean rating of all {len(games)} players; field score = expected score "
         f"against every rated ladder bot ({len(rated)} of {len(bots)}), one game each; "
         "vs higher = the same against only the ladder bots rated above the build, with their count):", "",
         "| build | rating | rank | games | record | field score | vs higher |", "|---|---|---|---|---|---|---|"]
for p in ours:
    lines.append(f"| {elolib.build_of(p)} | {R[p]:.0f} +- {1.96 * SE[p]:.0f} | {rank[p]} of {len(table)} | {games[p]} | "
                 f"{wins[p]}-{games[p] - wins[p]} | {elolib.field_score(R, p, rated):.1%} | {higher_field(p)} |")
lines += ["", f"Our record = OUR win rate (our W-L) against the bot by the incumbent "
          f"({elolib.build_of(incumbent) if incumbent else '-'}), whatever the count; * marks fewer than {RUN_MIN} games "
          f"(+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our "
          f"builds that did; blank if none has.", "",
          "| rank | player | rating | +- 95% | games | W-L | our record |", "|---|---|---|---|---|---|---|"]
for i, (r, p) in enumerate(table):
    name = f"**{p}**" if elolib.is_ours(p) else p
    lines.append(f"| {i + 1} | {name} | {r:.0f} | {1.96 * SE[p]:.0f} | {games[p]} | {wins[p]}-{games[p] - wins[p]} | "
                 f"{'' if elolib.is_ours(p) else recent_run(p)} |")
if unrated: lines += ["", "Not yet met: " + ", ".join(unrated)]
open(os.path.join(elolib.REPO, 'progress', 'ELO.md'), 'w').write('\n'.join(lines) + '\n')
if not a.quiet: print('\n'.join(lines[2:3] + lines[6:6 + len(ours) + 2]))
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, max(4, 0.16 * len(table))))
    ys = list(range(len(table)))[::-1]
    for y, (r, p) in zip(ys, table):
        c = '#d62728' if elolib.is_ours(p) else '#1f77b4'
        ax.errorbar(r, y, xerr=1.96 * SE[p], fmt='o', ms=3, color=c, ecolor=c, elinewidth=0.8, capsize=0)
    ax.set_yticks(ys); ax.set_yticklabels([p for _, p in table], fontsize=5.5)
    for t, (_, p) in zip(ax.get_yticklabels(), table):
        if elolib.is_ours(p): t.set_color('#d62728'); t.set_fontweight('bold')
    ax.set_xlabel('rating (Bradley-Terry, Elo scale), 95% interval relative to the mean rating'); ax.grid(axis='x', alpha=.3)
    ax.set_title(f"Ladder: {len(rows)} scrimmages; our builds in red"); ax.set_ylim(-1, len(table))
    fig.tight_layout(); fig.savefig(os.path.join(elolib.REPO, 'progress', 'elo.png'), dpi=120)
except Exception as e: print('plot skipped:', e)
