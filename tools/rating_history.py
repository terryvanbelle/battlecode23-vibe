#!/usr/bin/env python3
"""The replica's Team Settings "Rating History" chart, redrawn with each submission's first rated scrimmage marked
(owner, PROMPTS 44: "Can you create a version of the replica's Rating History graph from the Team Settings page? On it
please also mark the first time that each submission was used in a rated scrimmage game").
   tools/rating_history.py                       # fetch from the replica (GET only) -> progress/rating-history.png/.md
   tools/rating_history.py --from-json FILE      # offline, from a cached bundle (build/rating-history.json) or a raw
                                                 # historical_rating response
The curve is exactly the Team page's: GET /api/compete/<episode>/match/historical_rating/ (no team_id = our team), the
points siarnaq returns for every ranked, non-tournament match of ours with a rating (its penalized displayed rating
after the match, ordered by match creation; a cancelled ranked match is a point too, its rating unchanged). The
markers come from our scrimmage list (GET .../match/scrimmage/?team_id=<us>, every page): for each of our submissions,
the first COMPLETED match (status OK!) of that same population whose participant row for us carries the submission.
Package names come from the submission list (its package field, then the description's first word), then
progress/ladder-state.json's history, else "sub N"; the builds that were the validated build at some point are the
init/accept events of that history. A live run caches the raw responses in build/rating-history.json (not committed).
Times are Pacific (owner, PROMPTS 28): PDT, or PST once daylight time ends. Galaxy's own chart draws UTC (its Highcharts
options set time.useUTC although the axis is titled "Local Date & Time"), so the replica shows each time 7 h later.

The left axis starts at FLOOR = 1400 (owner, PROMPTS 45: "clip the new graph y-axis at >= 1400 ... I'd also like to see
the Bradley-Terry ELO values on the same graph"). The right axis is our Bradley-Terry fit (progress/ELO.md's: elolib.fit
over every recorded game, each build its own player), tied to the left one by a calibration, not a second free scale:
BT = a + b * galaxy by least squares over the field teams on the replica's Rankings page that the fit also rates (galaxy
rating >= FLOOR, >= CAL_MIN_GAMES BT games; not us, not a baseline). The BT scale is about 5x wider than galaxy's
(siarnaq's match-level Elo with K 24 compresses it), so BT numbers never go on the galaxy axis raw. On it: each package
that was our active rated build, as a step at its BT rating (+- 95%) over its tenure (its first rated match to the next
package's; re-uploads of a package merge), and each trial candidate that never played a rated match (a trial-start in
ladder-state.json's history), as a hollow diamond at its trial start. Both are today's full fit, drawn at those times.
The bands and bars carry the BT fit's 95% only; the calibration's own scatter (field teams about the line, 95%) is
reported beside them, since a step's gap to the curve compares with that. A live run also caches the Rankings page."""
import argparse, bisect, collections, datetime as dt, json, math, os, random, sys
_venv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'bin', 'python')
if os.path.exists(_venv) and '.venv' not in sys.prefix and __name__ == '__main__': os.execv(_venv, [_venv] + sys.argv)
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elolib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, 'progress', 'ladder-state.json')
CACHE = os.path.join(REPO, 'build', 'rating-history.json')
PDT = ZoneInfo('America/Los_Angeles'); UTC = dt.timezone.utc
FLOOR = 1400          # the left axis's lowest rating (owner, PROMPTS 45)
CAL_MIN_GAMES = 30    # a field team enters the BT calibration with at least this many BT games
PEER = 40             # field teams within this many galaxy points of our latest rating: the line's local misfit
Z95 = 1.96
# the reference palette's blue, orange, violet and aqua, validated together on the light surface (all pairs: CVD dE
# 9.2 at worst; aqua is under 3:1 against the surface, so every aqua mark is labelled and tabled in the .md)
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e6e5e0'
CURVE = '#2a78d6'
BTC = '#1baf7a'       # our Bradley-Terry fit (right axis)
KINDS = {   # kind -> (marker colour, filled marker?, legend text)
    'validated': ('#eb6834', True, 'first rated match: the build was validated with this submission'),
    'reupload': ('#eb6834', False, 'first rated match: re-upload of an already validated build'),
    'trial': ('#4a3aa7', True, 'first rated match: a build never validated'),
}
LABEL = {'validated': 'validated', 'reupload': 're-upload', 'trial': 'trial'}


# ---------------------------------------------------------------- pure data steps (no network; unit tested)
def parse_ts(s):
    """An API timestamp (ISO 8601 with offset; the replica answers in -04:00) -> an aware UTC datetime."""
    t = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    return (t if t.tzinfo else t.replace(tzinfo=UTC)).astimezone(UTC)


def to_pdt(t):
    """An aware datetime -> a naive America/Los_Angeles datetime (what the axis and the tables show)."""
    return t.astimezone(PDT).replace(tzinfo=None)


def zname(t):
    """The Pacific zone's abbreviation at t: 'PDT', or 'PST' once daylight time ends."""
    return t.astimezone(PDT).tzname()


def zone_label(times):
    """The abbreviation(s) a set of times needs: 'PDT', 'PST' or 'PDT/PST'."""
    return '/'.join(sorted({zname(t) for t in times})) or 'PDT'


def utc_lead(t):
    """Hours the replica's UTC chart reads ahead of our Pacific time at t (7 in PDT, 8 in PST)."""
    return round(-t.astimezone(PDT).utcoffset().total_seconds() / 3600)


def team_info(bundle):
    """(team name, episode) from the historical_rating response, else the bundle, else neutral words."""
    team = (((bundle.get('historical_rating') or {}).get('team_rating') or {}).get('team') or {})
    return team.get('name') or 'our team', bundle.get('episode') or team.get('episode') or '<episode>'


def points_from_history(js):
    """The historical_rating response -> [(UTC datetime, rating)] in time order, as galaxy's formatRatingHistory maps
    team_rating.rating_history. None (HTTP 204: no ranked matches) or a missing team_rating -> []."""
    rh = ((js or {}).get('team_rating') or {}).get('rating_history') or []
    return sorted((parse_ts(p['timestamp']), float(p['rating'])) for p in rh if p.get('rating') is not None)


def ours(match, team_id):
    return next((p for p in match.get('participants') or [] if p.get('team') == team_id), None)


def rated(matches, team_id):
    """[(UTC created, match, our participant)] for the chart's population: ranked, not a tournament match, our rating
    not null (siarnaq's get_historical_rating filter), ordered by created. One entry per match id: the list is crawled
    page by page newest first, so a match created mid-crawl can shift another onto the next page and repeat it (the
    later copy, fetched later, is kept)."""
    out = {}
    for m in matches:
        p = ours(m, team_id)
        if p is None or not m.get('is_ranked') or m.get('tournament_round') is not None or p.get('rating') is None:
            continue
        out[m['id']] = (parse_ts(m['created']), m, p)
    return sorted(out.values(), key=lambda x: (x[0], x[1]['id']))


def first_rated_use(matches, team_id):
    """submission id -> {match, created (UTC), rating, old_rating, matches, cancelled} for each of OUR submissions that
    played a rated match: the first completed (OK!) one by created. 'matches' counts all its chart points, 'cancelled'
    those not completed. A submission with no completed rated match is absent."""
    out, n, bad = {}, collections.Counter(), collections.Counter()
    for t, m, p in rated(matches, team_id):
        s = p.get('submission')
        if s is None:
            continue
        n[s] += 1
        if m.get('status') != 'OK!':
            bad[s] += 1
            continue
        if s not in out:
            out[s] = {'match': m['id'], 'created': t, 'rating': float(p['rating']),
                      'old_rating': None if p.get('old_rating') is None else float(p['old_rating'])}
    for s, d in out.items():
        d['matches'], d['cancelled'] = n[s], bad[s]
    return out


def rating_before(points, t, fallback=None):
    """The rating of the last chart point strictly before t (the previous point), else the fallback."""
    i = bisect.bisect_left([x for x, _ in points], t)
    return points[i - 1][1] if i > 0 else fallback


def package_names(submissions, history=()):
    """submission id -> package: the submission's package field, its description's first word, the ladder-state
    history (event 'submission'/'package'), else 'sub N'."""
    out = {}
    for e in history:
        if e.get('submission') is not None and e.get('package'):
            out[e['submission']] = e['package']
    for s in submissions:
        name = s.get('package') or ((s.get('description') or '').split() or [None])[0]
        if name:
            out[s['id']] = name
    return out


def name_of(names, sid):
    return names.get(sid) or f'sub {sid}'


def kind_of(sid, package, history):
    """'validated' (an init/accept event names this submission), 'reupload' (another submission of a package that was
    validated at some point) or 'trial' (a build never validated)."""
    ok = [e for e in history if e.get('event') in ('init', 'accept')]
    if any(e.get('submission') == sid for e in ok):
        return 'validated'
    return 'reupload' if package and any(e.get('package') == package for e in ok) else 'trial'


def validated_unrated(never, history):
    """[(submission, package, UTC accept time, next validated submission, its package, UTC time)] for each validated
    submission in `never` (no rated match): the init/accept event that made it the validated build and the next one,
    which replaced it before the ranked loop played it (c_pack1, #175: validated 26 minutes, PROMPTS 121). The next
    entries are None for the current validated build (pure)."""
    ok = sorted((e for e in history if e.get('event') in ('init', 'accept') and e.get('at')), key=lambda e: e['at'])
    out = []
    for sid, pkg, kind in never:
        if kind != 'validated':
            continue
        for i, e in enumerate(ok):
            if e.get('submission') == sid:
                nx = ok[i + 1] if i + 1 < len(ok) else None
                out.append((sid, pkg, parse_ts(e['at']), nx and nx.get('submission'), nx and nx.get('package'),
                            nx and parse_ts(nx['at'])))
                break
    return out


def spread(xs, gap, lo=0.0, hi=1.0):
    """Label positions (axes fractions) moved apart to at least `gap`, as little as possible, inside [lo, hi];
    returned in the input order."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    pos = [xs[i] for i in order]
    for k in range(len(pos)):
        pos[k] = max(pos[k], lo if k == 0 else pos[k - 1] + gap)
    for k in range(len(pos) - 1, -1, -1):
        pos[k] = min(pos[k], hi if k == len(pos) - 1 else pos[k + 1] - gap)
    for k in range(len(pos)):   # a crowd wider than [lo, hi] keeps its spacing from lo
        pos[k] = max(pos[k], lo if k == 0 else pos[k - 1] + gap)
    out = [0.0] * len(xs)
    for k, i in enumerate(order):
        out[i] = pos[k]
    return out


def rows(points, firsts, names, history):
    """One row per submission with a rated match, in first-use order (the .md table and the chart's markers)."""
    out = []
    for sid, d in sorted(firsts.items(), key=lambda kv: (kv[1]['created'], kv[0])):
        pk = names.get(sid)
        out.append({'sub': sid, 'package': name_of(names, sid), 'kind': kind_of(sid, pk, history),
                    'match': d['match'], 'created': d['created'], 'after': d['rating'],
                    'before': rating_before(points, d['created'], d['old_rating']),
                    'matches': d['matches'], 'cancelled': d['cancelled']})
    return out


def below_floor(points, floor=FLOOR):
    """(count, time of the last) of the chart points under the floor, which the clipped axis leaves out; (0, None)."""
    lo = [t for t, r in points if r < floor]
    return len(lo), (max(lo) if lo else None)


def calibrate(pairs):
    """Least squares BT = a + b * galaxy over [(galaxy, bt), ...] -> (a, b, r, n, s), r the Pearson correlation, s the
    residual SD in BT points (n - 2 degrees of freedom; s / b in galaxy points: how far one field team sits from the
    line); None with fewer than 3 pairs or no spread on either side."""
    n = len(pairs)
    if n < 3:
        return None
    mx = sum(x for x, _ in pairs) / n; my = sum(y for _, y in pairs) / n
    sxx = sum((x - mx) ** 2 for x, _ in pairs); syy = sum((y - my) ** 2 for _, y in pairs)
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    if sxx <= 0 or syy <= 0:
        return None
    b = sxy / sxx
    s = math.sqrt(max(syy - b * sxy, 0.0) / (n - 2))
    return my - b * mx, b, sxy / math.sqrt(sxx * syy), n, s


def peer_offset(pairs, cal, galaxy, band=PEER):
    """(count, mean galaxy - (BT - a) / b) over the calibration teams within `band` galaxy points of `galaxy`: where
    the line sits against field teams at our level (negative: they rate lower in galaxy than their BT converts to);
    None when no team is that close."""
    a, b = cal[0], cal[1]
    d = [g - (v - a) / b for g, v in pairs if abs(g - galaxy) <= band]
    return (len(d), sum(d) / len(d)) if d else None


def crossings(p, q, poly):
    """How many segments of the polyline `poly` ([(x, y), ...]) properly cross the segment p-q (display pixels): the
    leader-versus-curve test of the label placement."""
    (px, py), (qx, qy) = p, q
    lo, hi = min(px, qx), max(px, qx)
    side = lambda ax_, ay, bx, by, cx, cy: (bx - ax_) * (cy - ay) - (by - ay) * (cx - ax_)
    n = 0
    for (ax_, ay), (bx, by) in zip(poly[:-1], poly[1:]):
        if max(ax_, bx) < lo or min(ax_, bx) > hi:
            continue
        d1, d2 = side(ax_, ay, bx, by, px, py), side(ax_, ay, bx, by, qx, qy)
        d3, d4 = side(px, py, qx, qy, ax_, ay), side(px, py, qx, qy, bx, by)
        n += (d1 * d2 < 0) and (d3 * d4 < 0)
    return n


def calibration_pairs(rankings, R, games, team_id=None, floor=FLOOR, min_games=CAL_MIN_GAMES):
    """[(galaxy rating, BT rating)] for the field teams of the Rankings page that the BT fit rates: galaxy rating >=
    floor, >= min_games BT games, not our team (its id, or an 'us:' player) and not a stock baseline (elolib.BASELINES).
    The replica's team names are the fit's player names (<github user>.<bot>)."""
    out = []
    for t in rankings or []:
        name, g = t.get('name') or '', t.get('rating')
        if (g is None or g < floor or t.get('id') == team_id or name.startswith('us:') or name in elolib.BASELINES
                or (games.get(name) or 0) < min_games):
            continue
        out.append((float(g), float(R[name])))
    return out


def tenures(markers, end=None):
    """[(package, start), ...] (each submission's first rated match, any order) -> [(package, start, end)]: the package
    that was the active rated build from its first rated match to the next package's; consecutive markers of the same
    package merge (a re-upload is the same build). The last one ends at `end` (None: open, the chart's right edge)."""
    out = []
    for pkg, t in sorted(markers, key=lambda m: m[1]):
        if out and out[-1][0] == pkg:
            continue
        if out:
            out[-1][2] = t
        out.append([pkg, t, end])
    return [tuple(x) for x in out]


def trial_candidates(history, rated_pkgs):
    """[(package, UTC time of its first trial-start)] for each package with a trial-start event in ladder-state.json's
    history and no rated match (not in `rated_pkgs`), in time order."""
    out = {}
    for e in history:
        pkg = e.get('package')
        if e.get("event") == "trial-start" and pkg and pkg not in rated_pkgs and e.get("at"):
            t = parse_ts(e['at'])
            if pkg not in out or t < out[pkg]:
                out[pkg] = t
    return sorted(out.items(), key=lambda kv: (kv[1], kv[0]))


def bt_layer(rankings, fit, table, history, points, team_id=None):
    """The right axis's data: {'cal': (a, b, r, n, s), 'peers': peer_offset at our latest rating, 'steps': [...],
    'trials': [...]} from the Rankings page, an elolib.fit result (R, SE, games, ...) and the rows; None when the
    calibration cannot be fitted. A build the fit does not rate (no recorded game yet) has 'bt' None. 'galaxy_end': the
    chart's rating when the tenure ended (its last point before the next build's first rated match; the latest point
    for the current build)."""
    R, SE, games = fit[0], fit[1], fit[2]
    pairs = calibration_pairs(rankings, R, games, team_id)
    cal = calibrate(pairs)
    if cal is None:
        return None
    def rec(pkg):
        p = 'us:' + pkg
        return (R[p], SE[p], games[p]) if elolib.is_ours(p) and games.get(p) else None
    steps = [{'package': pkg, 'start': s, 'end': e, 'bt': rec(pkg),
              'galaxy_end': points[-1][1] if e is None else rating_before(points, e)}
             for pkg, s, e in tenures([(r['package'], r['created']) for r in table])]
    trials = [{'package': pkg, 'at': t, 'bt': rec(pkg)}
              for pkg, t in trial_candidates(history, {r['package'] for r in table})]
    return {'cal': cal, 'peers': peer_offset(pairs, cal, points[-1][1]), 'steps': steps, 'trials': trials}


# ---------------------------------------------------------------- data
def fetch():
    """The replica's responses, GET only, as our team (tools/contest.py holds the credentials), and the Rankings page
    (team names and displayed ratings: the BT calibration)."""
    import contest
    ep = contest.EPISODE
    hist = contest.api('GET', f'/api/compete/{ep}/match/historical_rating/')
    tid = (hist or {}).get('team_id') or contest.me()['id']
    keep = ('id', 'package', 'description', 'created', 'status', 'accepted')
    subs = [{k: s.get(k) for k in keep} for s in contest.pages(f'/api/compete/{ep}/submission/')]
    return {'fetched_at': dt.datetime.now(UTC).isoformat(), 'episode': ep, 'team_id': tid, 'historical_rating': hist,
            'matches': contest.matches(tid, limit_pages=None), 'submissions': subs,
            'tournaments': contest.pages(f'/api/episode/{ep}/tournament/'), 'rankings': contest.rankings()}


def load(path):
    with open(path) as fh:
        js = json.load(fh)
    if isinstance(js, dict) and 'team_rating' in js:   # a raw historical_rating response: the curve alone
        js = {'historical_rating': js, 'team_id': js.get('team_id')}
    return js


def history_events(path):
    try:
        with open(path) as fh:
            return json.load(fh).get('history', [])
    except (OSError, ValueError):
        return []


# ---------------------------------------------------------------- outputs
def _dense(xy, step=3.0):
    """Display-space polyline vertices (an n x 2 array) with points added every `step` pixels along each segment."""
    import numpy as np
    out = [xy[:1]]
    for p, q in zip(xy[:-1], xy[1:]):
        k = max(1, int(np.hypot(*(q - p)) / step))
        out.append(p + (q - p) * (np.arange(1, k + 1) / k)[:, None])
    return np.vstack(out)


def footer(points, table, bundle, bt, bt_note=''):
    """The figure's note, one string per line."""
    curve_only = 'matches' not in bundle
    zl = zone_label([t for t, _ in points])
    nlow, tlow = below_floor(points)
    canc = sum(1 for _, m, _ in rated(bundle.get('matches') or [], bundle.get('team_id')) if m.get('status') != 'OK!')
    lines = [f"{len(points)} rated matches (ranked, non-tournament scrimmages{f'; {canc} cancelled, rating unchanged' if canc else ''}), "
             f"{to_pdt(points[0][0]):%b %d %H:%M} to {to_pdt(points[-1][0]):%b %d %H:%M}. Latest rating {points[-1][1]:,.0f}. "
             f"All times are {zl} (the replica's chart shows UTC, {utc_lead(points[-1][0])} h later)."]
    if nlow:
        climb = nlow == sum(1 for t, _ in points if t <= tlow)   # every point up to the last low one is low
        low = {KINDS[r.get('kind', 'validated')][1] for r in table if r['after'] < FLOOR}   # filled? of each marker
        glyphs = ' '.join(g for g, filled in (('▼', True), ('▽', False)) if filled in low)
        lines.append(f"The left axis starts at {FLOOR:,}: {nlow} points below it ({'the climb from 0, ' if climb else ''}the last "
                     f"at {to_pdt(tlow):%b %d %H:%M} {zname(tlow)}) are off the chart"
                     + (f"; {glyphs} on the floor: a first rated match below it (filled or hollow as the circles)."
                        if low else "."))
    lines.append("No submission markers: this file is the curve alone (they need the match list of a live run or "
                 "build/rating-history.json)." if curve_only else
                 "Dotted lines: each submission's first completed rated match, labelled #submission build." if table else
                 "No submission has a completed rated match yet.")
    if bt:
        a, b, r, n, s = bt['cal']
        lines += ["Right axis: our Bradley-Terry fit as in progress/ELO.md (today's fit over every recorded game, each build "
                  "its own player), the left axis relabelled through",
                  f"BT = {a:,.0f} + {b:.2f} x galaxy rating, least squares over the {n} field teams of the Rankings page rated "
                  f">= {FLOOR:,} with >= {CAL_MIN_GAMES} BT games (r = {r:.3f}).",
                  f"Green bands and bars: the BT fit's 95% only. Field teams scatter ±{Z95 * s / b:.0f} galaxy points (95%) "
                  f"about that line, so a step's gap to the blue curve compares with ±{Z95 * s / b:.0f}, not with its band."]
    elif bt_note:
        lines.append(bt_note)
    return lines


def draw(points, table, bundle, path, bt=None, bt_note=''):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
    import matplotlib.patheffects as patheffects, numpy as np
    from matplotlib.legend_handler import HandlerTuple
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import FuncFormatter
    from matplotlib.transforms import Bbox
    curve_only = 'matches' not in bundle   # a raw historical_rating response: no match list, so no markers
    if curve_only:
        bt = None
    note = footer(points, table, bundle, bt, bt_note)
    W, H, DPI = 13.0, 7.6, 120
    L, R = 0.06, (0.925 if bt else 0.985)
    B, T = (0.95 + 0.155 * len(note)) / H, 1 - (0.66 if curve_only else 1.45) / H   # the top band holds the labels
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor=SURFACE)
    ax = fig.add_axes([L, B, R - L, T - B], facecolor=SURFACE)
    xs = [to_pdt(t) for t, _ in points]; ys = [r for _, r in points]
    ax.plot(xs, ys, '-', color=CURVE, lw=2, solid_joinstyle='round', solid_capstyle='round', zorder=3)
    ax.plot(xs, ys, 'o', color=CURVE, ms=2.6, mew=0, zorder=4)
    end = parse_ts(bundle['fetched_at']) if bundle.get('fetched_at') else points[-1][0]
    span = max((end - points[0][0]).total_seconds(), 3600)
    x0 = to_pdt(points[0][0] - dt.timedelta(seconds=0.01 * span)); x1 = to_pdt(max(end, points[-1][0]) + dt.timedelta(seconds=0.01 * span))
    ax.set_xlim(x0, x1)
    # y: from FLOOR when a point is under it (clipped), else from the data but never under FLOOR; the top fits the curve
    # and every BT band (in galaxy terms), with headroom for the labels
    a_, b_ = (bt['cal'][0], bt['cal'][1]) if bt else (0.0, 1.0)
    to_g = lambda v: (v - a_) / b_
    marks = [] if not bt else [m for m in bt['steps'] + bt['trials'] if m['bt']]
    ext = [r for r in ys if r >= FLOOR]
    for m in marks:
        ext += [to_g(m['bt'][0] - Z95 * m['bt'][1]), to_g(m['bt'][0] + Z95 * m['bt'][1])]
    lo, hi = (min(ext), max(ext)) if ext else (FLOOR, FLOOR + 100)
    pad = 0.06 * max(hi - lo, 50)
    y0 = FLOOR if below_floor(points)[0] else max(FLOOR, lo - pad)
    ax.set_ylim(y0, hi + 1.5 * pad)
    # tournaments, as galaxy's plotLines (none on the replica so far)
    for t in bundle.get('tournaments') or []:
        if t.get('display_date'):
            d = to_pdt(parse_ts(t['display_date']))
            if x0 <= d <= x1:
                ax.axvline(d, color=INK2, lw=1, zorder=1)
                ax.annotate(t.get('name_long') or t.get('name_short') or '', (d, 0.02), xycoords=('data', 'axes fraction'),
                            xytext=(3, 0), textcoords='offset points', fontsize=8, color=INK2, rotation=90, va='bottom')
    # each submission's first rated match: a dotted line, a ringed marker on the curve, a label above the plot. The
    # surface ring sits under the curve (it only cuts the dotted line), so close markers never hide a segment. A first
    # rated match under the floor is a down triangle on it.
    xnum = mdates.date2num([to_pdt(r['created']) for r in table])
    ringed = [(x, r['after']) for r, x in zip(table, xnum) if r['after'] >= y0]   # the markers on the curve
    a, b = mdates.date2num(x0), mdates.date2num(x1)
    frac = [(x - a) / (b - a) for x in xnum]
    lab = spread(frac, 0.155 / (W * (R - L)), 0.0, 1.0)   # 0.155 in between label centres (8 pt text, rotated)
    for r, x, f in zip(table, xnum, lab):
        col, filled, _ = KINDS[r['kind']]
        ax.axvline(x, color=col, lw=1, ls=(0, (1, 2.5)), alpha=0.8, zorder=2)
        if r['after'] >= y0:
            ax.plot([x], [r['after']], 'o', ms=8, mfc=col if filled else SURFACE, mec=col, mew=2, zorder=6)
            ax.plot([x], [r['after']], 'o', ms=12, mfc='none', mec=SURFACE, mew=2, zorder=2.5)   # the surface ring
        else:
            ax.plot([x], [y0], 'v', ms=8, mfc=col if filled else SURFACE, mec=col, mew=1.6, zorder=6, clip_on=False)
        ax.annotate(f"#{r['sub']} {r['package']}", xy=(x, 1.0), xycoords=('data', 'axes fraction'),
                    xytext=(f, 1.045), textcoords='axes fraction', rotation=90, ha='center', va='bottom', fontsize=8,
                    color=INK, annotation_clip=False,
                    arrowprops=dict(arrowstyle='-', color=col, lw=0.9, shrinkA=1, shrinkB=0, relpos=(0.5, 0.0)))
    # our Bradley-Terry ratings on the calibrated right axis: a step per tenure with its 95% band, and a hollow diamond
    # with 95% bars per trial candidate never rated, at its trial start. All under the galaxy curve; the bars and the
    # diamond wear a surface stroke, so a cap that lands on a step line of the same green stays visible.
    boxes, labels = [], []   # per BT mark, same order: ('band'|'bar', lower left, upper right); (text, candidates)
    if bt:
        halo = [patheffects.withStroke(linewidth=3.4, foreground=SURFACE)]
        for s in bt['steps']:
            if not s['bt']:
                continue
            v, se, _ = s['bt']; y, h = to_g(v), Z95 * se / b_
            xa, xb = to_pdt(s['start']), (to_pdt(s['end']) if s['end'] else x1)
            ax.fill_between([xa, xb], y - h, y + h, color=BTC, alpha=0.17, lw=0, zorder=1.6)
            ax.plot([xa, xb], [y, y], '-', color=BTC, lw=2.2, solid_capstyle='butt', zorder=2.8)
            boxes.append(('band', (xa, y - h), (xb, y + h)))
            at = lambda f: xa + (xb - xa) * f
            cands = []   # (anchor, offset pt, ha, va, leader's end on the label, leader shrink pt), nearest first:
            for k in range(10):   # just above or below the band, over its middle, a quarter point, its start or end
                for xx, dx, ha, rx in ((at(0.5), 0, 'center', 0.5), (at(0.25), 0, 'center', 0.5),
                                       (at(0.75), 0, 'center', 0.5), (xa, 1, 'left', 0), (xb, -1, 'right', 1)):
                    cands += [((xx, y + h), (dx, 2 + 11 * k), ha, 'bottom', (rx, 0), 0),
                              ((xx, y - h), (dx, -2 - 11 * k), ha, 'top', (rx, 1), 0)]
            labels.append((f"{s['package']}\nBT {v:,.0f} ±{Z95 * se:.0f}", cands))
        for tr in bt['trials']:
            if not tr['bt']:
                continue
            v, se, _ = tr['bt']; y, h = to_g(v), Z95 * se / b_
            x = to_pdt(tr['at'])
            eb = ax.errorbar([x], [y], yerr=[h], fmt='D', ms=6.5, mfc=SURFACE, mec=BTC, mew=1.8, ecolor=BTC,
                             elinewidth=1.3, capsize=3, capthick=1.3, zorder=2.9)
            for art in [eb[0], *eb[1], *eb[2]]:
                art.set_path_effects(halo)
            boxes.append(('bar', (x, y - h), (x, y + h)))
            # right on a cap, else beside the diamond with the leader on the diamond (never along the bar, where a
            # leader reads as a longer whisker)
            cands = [((x, y + h), (0, 4), 'center', 'bottom', (0.5, 0), 0),
                     ((x, y - h), (0, -4), 'center', 'top', (0.5, 1), 0)]
            for k in range(10):
                for dx in (10, 26, 44):
                    for dy in sorted({11 * k, -11 * k}):
                        cands += [((x, y), (dx, dy), 'left', 'center', (0, 0.5), 5),
                                  ((x, y), (-dx, dy), 'right', 'center', (1, 0.5), 5)]
            cands.sort(key=lambda c: math.hypot(*c[1]))   # stable: the caps first, then the nearest
            labels.append((f"{tr['package']}\nBT {v:,.0f} ±{Z95 * se:.0f}", cands))
        sec = ax.secondary_yaxis('right', functions=(lambda g: a_ + b_ * g, lambda v: (v - a_) / b_))
        sec.set_ylabel('Bradley-Terry rating, Elo points (our fit, tied to the left axis)', color=INK2, fontsize=10)
        sec.tick_params(colors=INK2, labelsize=9)
        sec.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
        sec.spines['right'].set_color(BTC); sec.spines['right'].set_linewidth(1.5)
    # axes in galaxy's terms, recessive
    loc = mdates.AutoDateLocator(minticks=6, maxticks=14)
    fmt = mdates.ConciseDateFormatter(loc, formats=['%Y', '%b', '%b %d', '%H:%M', '%H:%M', '%S.%f'],
                                      zero_formats=['', '%Y', '%b', '%b %d', '%H:%M', '%H:%M'],
                                      offset_formats=['', '%Y', '%Y', '%Y', '%Y', '%Y'])
    ax.xaxis.set_major_locator(loc); ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.grid(axis='y', color=GRID, lw=1, ls='-'); ax.set_axisbelow(True)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'): ax.spines[s].set_color('#b8b7b1')
    ax.tick_params(colors=INK2, labelsize=9)
    zl = zone_label([t for t, _ in points])
    ax.set_xlabel(f'Date & time ({zl})', color=INK2, fontsize=10)
    ax.set_ylabel('Rating, Elo points (replica, as on the Team page)', color=INK2, fontsize=10)
    fig.suptitle(f"Rating History - {team_info(bundle)[0]} (replica){', with our Bradley-Terry ratings' if bt else ''}",
                 x=L, y=0.985, ha='left', fontsize=14, color=INK, fontweight='bold')
    hs = [Line2D([], [], color=CURVE, lw=2, marker='o', ms=3, label="rating after each rated match (the Team page's curve)")]
    hm = {}
    for k in [k for k in KINDS if any(r['kind'] == k for r in table)]:
        col, filled, text = KINDS[k]
        hs.append(Line2D([], [], color=col, lw=1, ls=(0, (1, 2)), marker='o', ms=7, mfc=col if filled else SURFACE,
                         mec=col, mew=2, label=text))
    if bt and any(s['bt'] for s in bt['steps']):
        hs.append((Patch(facecolor=BTC, alpha=0.17, lw=0), Line2D([], [], color=BTC, lw=2.2)))
        hm[len(hs) - 1] = "our build's Bradley-Terry rating (today's fit) over its rated tenure, the fit's 95% (right axis)"
    if bt and any(t['bt'] for t in bt['trials']):
        hs.append(Line2D([], [], color=BTC, ls='none', marker='D', ms=6, mfc=SURFACE, mec=BTC, mew=1.8))
        hm[len(hs) - 1] = "trial candidate never rated: its BT rating (today's fit), drawn at its trial start, the fit's 95%"
    texts = [hm.get(i) or h.get_label() for i, h in enumerate(hs)]
    leg = ax.legend(hs, texts, loc='lower right', fontsize=8.5, frameon=True, facecolor=SURFACE, edgecolor=GRID,
                    handler_map={tuple: HandlerTuple(ndivide=1, pad=0)})
    for t in leg.get_texts(): t.set_color(INK)
    # BT labels (two lines: build, rating). In one pass each label takes its first candidate (nearest first) that costs
    # nothing, else the cheapest by cost + 0.5 per pixel of leader; a layout is two passes (the second re-places each
    # label against all the others), tried over several label orders, the cheapest kept. A label must not cover the
    # axes edges, the legend, another label (with a gap beside it) or a trial's bars and caps, should not cover the
    # galaxy curve or a leader, and only lightly another build's band. Its leader is thin and grey (never a bar's
    # green) and should not cross or run along the curve, pass through a submission marker, cross another leader, a
    # label, the legend or a trial's bars, run along its own bar, or (lightly) cross a band.
    if labels:
        rend = fig.canvas.get_renderer()
        axbb = ax.get_window_extent(rend)
        AREA = {'legend': 20.0, 'label': 20.0, 'bar': 100.0, 'band': 1.0}       # per square pixel a label covers
        GAP = {'legend': (8, 3), 'label': (8, 3), 'bar': (2, 2), 'band': (2, 2)}   # clearance (x, y), pixels
        LINE = {'legend': 300.0, 'label': 300.0, 'bar': 2000.0, 'band': 15.0}    # per leader point (2 px) inside
        TEXT = dict(fontsize=8, color=INK, linespacing=1.15)
        px_pt = DPI / 72.0
        fixed = [(leg.get_window_extent(rend), 'legend')]   # then label i's own band or bars at 1 + i
        for kind, p, q in boxes:
            (u0, v0), (u1, v1) = ax.transData.transform([(mdates.date2num(p[0]), p[1]), (mdates.date2num(q[0]), q[1])])
            u0, u1, v0, v1 = min(u0, u1), max(u0, u1), min(v0, v1), max(v0, v1)
            if kind == 'bar':   # the caps' half width and their thickness
                u0, u1, v0, v1 = u0 - 3 * px_pt - 1, u1 + 3 * px_pt + 1, v0 - 2, v1 + 2
            fixed.append((Bbox.from_extents(u0, v0, u1, v1), kind))
        curve_xy = ax.transData.transform(np.column_stack([mdates.date2num(xs), ys]))
        cur, poly = _dense(curve_xy), [tuple(p) for p in curve_xy]
        rings = ax.transData.transform(ringed) if ringed else np.empty((0, 2))
        hits = lambda pts, bb: int(((pts[:, 0] >= bb.x0) & (pts[:, 0] <= bb.x1) & (pts[:, 1] >= bb.y0) & (pts[:, 1] <= bb.y1)).sum())
        def near(seg, pts, r):   # how many points of seg lie within r pixels of one of pts
            if not len(seg) or not len(pts):
                return 0
            lo, hi = seg.min(0) - r, seg.max(0) + r
            P = pts[(pts[:, 0] >= lo[0]) & (pts[:, 0] <= hi[0]) & (pts[:, 1] >= lo[1]) & (pts[:, 1] <= hi[1])]
            return int((np.hypot(seg[:, None, 0] - P[None, :, 0], seg[:, None, 1] - P[None, :, 1]).min(1) <= r).sum()) if len(P) else 0
        def overlap(bb, o, kind):
            gx, gy = GAP[kind]
            w = min(bb.x1 + gx, o.x1) - max(bb.x0 - gx, o.x0); hh = min(bb.y1 + gy, o.y1) - max(bb.y0 - gy, o.y0)
            return AREA[kind] * w * hh if w > 0 and hh > 0 else 0.0
        # every candidate's geometry, in display pixels: the text box from the label's measured size and its alignment
        FX, FY = {'left': 0.0, 'center': 0.5, 'right': 1.0}, {'bottom': 0.0, 'center': 0.5, 'top': 1.0}
        geo = []   # per label: [(text box, leader points, leader start, leader end, length, anchor centre), ...]
        for text, cands in labels:
            t = ax.text(0, 0, text, transform=None, **TEXT); w, h = t.get_window_extent(rend).size; t.remove()
            opts = []
            for xy, off, ha, va, rel, shrink in cands:
                centre = ax.transData.transform((mdates.date2num(xy[0]), xy[1]))
                X, Y = centre[0] + off[0] * px_pt, centre[1] + off[1] * px_pt
                bb = Bbox.from_bounds(X - FX[ha] * w, Y - FY[va] * h, w, h)
                start = np.array([bb.x0 + rel[0] * w, bb.y0 + rel[1] * h])
                d = float(np.hypot(*(centre - start)))
                tip = centre + (start - centre) * min(1.0, shrink * px_pt / d) if d > 0 else centre
                length = float(np.hypot(*(tip - start)))
                seg = _dense(np.array([start, tip]), 2.0) if length > 1 else np.empty((0, 2))
                opts.append((bb, seg, tuple(start), tuple(tip), length, centre))
            geo.append(opts)
        def static_cost(i, k):   # a candidate's cost against everything but the other labels
            bb, seg, s0, s1, _, centre = geo[i][k]
            c = 0.0 if (axbb.x0 <= bb.x0 - 2 and bb.x1 + 2 <= axbb.x1 and axbb.y0 <= bb.y0 - 2 and bb.y1 + 2 <= axbb.y1) else 1e7
            for j, (o, kind) in enumerate(fixed):
                if j == 1 + i:   # its own band or bars: the label sits beside them, its leader stays off the bar
                    c += LINE['bar'] * hits(seg[np.hypot(*(seg - centre).T) > 10], o)
                else:
                    c += overlap(bb, o, kind) + LINE[kind] * hits(seg, o)
            c += 300.0 * hits(cur, bb.padded(2))
            if len(seg) > 1:   # the leader across or along the curve, or through a submission marker
                c += 600.0 * crossings(s0, s1, poly) + 100.0 * near(seg, cur, 3) + 300.0 * near(seg, rings, 14)
            return c
        # A label's candidates as arrays, so a placement prices all of them at once against each placed label: box
        # extents, padded boxes, leader ends, leader point counts, and every leader point with its candidate's index.
        # Each pair term is the scalar formula's arithmetic, element by element and in the same order, so the layout
        # is the one the candidate-by-candidate search chose (it took 30+ minutes at 40+ labels: PROMPTS 121).
        A = []
        for i, opts in enumerate(geo):
            ext = np.array([[o[0].x0, o[0].y0, o[0].x1, o[0].y1] for o in opts])
            segs = [o[1] for o in opts]
            A.append({'ext': ext, 'pad': ext + [-2.0, -2.0, 2.0, 2.0],
                      's0': np.array([o[2] for o in opts]), 's1': np.array([o[3] for o in opts]),
                      'nseg': np.array([len(s) for s in segs]), 'pts': np.vstack(segs),
                      'own': np.repeat(np.arange(len(opts)), [len(s) for s in segs]),
                      'static': np.array([static_cost(i, k) for k in range(len(opts))]),
                      'half': np.array([0.5 * o[4] for o in opts])})
        pair = {}   # (label i, label j, j's candidate) -> (base, crossing) cost arrays over i's candidates
        def pair_cost(i, j, kk):
            if (i, j, kk) not in pair:
                a, K = A[i], len(geo[i])
                ob, oseg, o0, o1 = geo[j][kk][:4]
                gx, gy = GAP['label']; x0, y0, x1, y1 = a['ext'].T
                w = np.minimum(x1 + gx, ob.x1) - np.maximum(x0 - gx, ob.x0)
                hh = np.minimum(y1 + gy, ob.y1) - np.maximum(y0 - gy, ob.y0)
                ov = np.where((w > 0) & (hh > 0), AREA['label'] * w * hh, 0.0)
                P = a['pts']   # this label's leader points inside the other label's box, per candidate
                inb = (P[:, 0] >= ob.x0) & (P[:, 0] <= ob.x1) & (P[:, 1] >= ob.y0) & (P[:, 1] <= ob.y1)
                lead = np.bincount(a['own'][inb], minlength=K)
                px0, py0, px1, py1 = a['pad'].T   # the other leader's points inside this label's padded box
                under = ((oseg[:, None, 0] >= px0) & (oseg[:, None, 0] <= px1) & (oseg[:, None, 1] >= py0)
                         & (oseg[:, None, 1] <= py1)).sum(0) if len(oseg) else np.zeros(K, int)
                base = ov + LINE['label'] * lead + 300.0 * under
                cr = np.zeros(K)
                if len(oseg) > 1:   # crossings(s0, s1, [o0, o1]) for every candidate with a leader
                    (ax_, ay), (bx, by) = o0, o1
                    p, q = a['s0'], a['s1']
                    side = lambda ax_, ay, bx, by, cx, cy: (bx - ax_) * (cy - ay) - (by - ay) * (cx - ax_)
                    d1, d2 = side(ax_, ay, bx, by, p[:, 0], p[:, 1]), side(ax_, ay, bx, by, q[:, 0], q[:, 1])
                    d3 = side(p[:, 0], p[:, 1], q[:, 0], q[:, 1], ax_, ay)
                    d4 = side(p[:, 0], p[:, 1], q[:, 0], q[:, 1], bx, by)
                    lo, hi = np.minimum(p[:, 0], q[:, 0]), np.maximum(p[:, 0], q[:, 0])
                    x = ~((max(ax_, bx) < lo) | (min(ax_, bx) > hi)) & (d1 * d2 < 0) & (d3 * d4 < 0)
                    cr = np.where((a['nseg'] > 1) & x, 600.0, 0.0)
                pair[i, j, kk] = (base, cr)
            return pair[i, j, kk]
        def costs(i, placed):   # every candidate of label i against the labels placed so far
            c = A[i]['static'].copy()
            for j, kk in placed.items():
                if j != i:   # another label: under this one or under this leader; its leader under this label or crossed
                    base, cr = pair_cost(i, j, kk)
                    c += base; c += cr
            return c
        def layout(order):
            placed = {}
            for i in order + order:   # the first free candidate, else the cheapest by cost + 0.5 per pixel of leader
                c = costs(i, placed); tot = c + A[i]['half']
                free = np.flatnonzero(c == 0)
                placed[i] = int(np.argmin(tot[:free[0] + 1] if len(free) else tot))
            return sum(float(costs(i, placed)[k]) + float(A[i]['half'][k]) for i, k in placed.items()), placed
        n = len(labels)
        first = sorted(range(n), key=lambda i: boxes[i][0] != 'bar')   # trial candidates first: a point has fewer places
        rnd = random.Random(0)
        orders = [first, first[::-1], sorted(range(n), key=lambda i: boxes[i][0] == 'bar')] + [rnd.sample(range(n), n) for _ in range(9)]
        _, placed = min((layout(o) for o in orders), key=lambda r: r[0])
        for i, k in sorted(placed.items()):
            xy, off, ha, va, rel, shrink = labels[i][1][k]
            ax.annotate(labels[i][0], xy, xytext=off, textcoords='offset points', ha=ha, va=va, zorder=7,
                        annotation_clip=False, bbox=dict(boxstyle='square,pad=0.1', fc=SURFACE, ec='none', alpha=0.85),
                        arrowprops=dict(arrowstyle='-', color=INK2, lw=0.7, shrinkA=0, shrinkB=shrink, relpos=rel), **TEXT)
    fig.text(L, 0.018, '\n'.join(note), fontsize=8.5, color=INK2, ha='left', va='bottom', linespacing=1.45)
    fig.savefig(path, dpi=DPI, facecolor=SURFACE); plt.close(fig)


def bt_md(bt, points):
    """The .md section on the right axis: the calibration and its scatter, our rated builds' BT ratings over their
    tenures next to the galaxy rating at the end of each, and the trial candidates never rated."""
    a, b, r, n, sd = bt['cal']
    f = lambda v: '-' if v is None else f'{v:,.0f}'
    hm = lambda t: f'{to_pdt(t):%m-%d %H:%M}'
    zl = zone_label([s['start'] for s in bt['steps']] + [t['at'] for t in bt['trials']] + [points[-1][0]])
    def cells(x):
        if not x['bt']:
            return '- | - | 0 | -'
        v, se, g = x['bt']
        return f'{v:,.0f} | {Z95 * se:.0f} | {g} | {(v - a) / b:,.0f}'
    band = sorted(Z95 * x['bt'][1] / b for x in bt['steps'] + bt['trials'] if x['bt'])
    scat = Z95 * sd / b
    rng = f' (±{band[0]:.0f} to ±{band[-1]:.0f} galaxy points here)' if band else ''
    peers = bt.get('peers')
    local = (f"; the line also misfits locally: the {peers[0]} field team{'s' if peers[0] != 1 else ''} within {PEER} galaxy "
             f"points of our latest rating ({points[-1][1]:,.0f}) rate{'s' if peers[0] == 1 else ''} {abs(peers[1]):.0f} galaxy "
             f"points {'below' if peers[1] < 0 else 'above'} what {'its' if peers[0] == 1 else 'their'} BT converts to, on "
             f"average" if peers else '')
    out = ['## Bradley-Terry ratings (the right axis)', '',
           "Our Bradley-Terry fit, as in [ELO.md](ELO.md): `tools/elolib.py` over every recorded game of "
           "progress/games.csv, each build its own player; +- 95% = 1.96 SE; a rating is relative to that fit's mean, so "
           "it compares only within the fit. Every rating below is today's fit, drawn over the build's rated tenure or at "
           "its trial start. The chart's right axis is the left one relabelled through",
           '', f'**BT = {a:,.1f} + {b:.3f} x galaxy rating** (r = {r:.3f}, {n} teams; residual SD {sd:.0f} BT = '
           f'{sd / b:.0f} galaxy points),', '',
           f"a least-squares fit over the field teams of the replica's Rankings page that our fit also rates, with a "
           f"galaxy rating of at least {FLOOR:,} and at least {CAL_MIN_GAMES} BT games (not us, not a stock baseline). One "
           f"galaxy point is about {b:.1f} BT points: siarnaq's match-level Elo (K 24) compresses the scale, so BT numbers "
           f"never go on the galaxy axis raw. \"As galaxy\" = (BT - a) / b, where the line puts a team that strong. It is "
           f"not exact: single field teams sit within ±{scat:.0f} galaxy points of the line 95% of the time{local}. The "
           f"+- 95% column, and the chart's green bands and bars, carry the BT fit's SE alone{rng}, so a gap between "
           f"\"As galaxy\" and \"Galaxy at end of tenure\" compares with ±{scat:.0f}, not with them. Our galaxy rating "
           f"carries over from build to build; each build is its own BT player.", '',
           f'| Build | Rated tenure ({zl}) | BT rating | +- 95% | BT games | As galaxy | Galaxy at end of tenure |',
           '|---|---|---:|---:|---:|---:|---:|']
    for s in bt['steps']:
        span = f"{hm(s['start'])} to {hm(s['end']) if s['end'] else 'now'}"
        out.append(f"| {s['package']} | {span} | {cells(s)} | {f(s['galaxy_end'])}{'' if s['end'] else ' (latest)'} |")
    if bt['trials']:
        out += ['', 'Trial candidates that never played a rated match (hollow diamonds, at their trial start):', '',
                f'| Build | Trial start ({zl}) | BT rating | +- 95% | BT games | As galaxy |', '|---|---|---:|---:|---:|---:|']
        for t in bt['trials']:
            out.append(f"| {t['package']} | {hm(t['at'])} | {cells(t)} |")
    nog = [x['package'] for x in bt['steps'] + bt['trials'] if not x['bt']]
    if nog:
        out += ['', 'Not on the chart, no recorded game in the fit yet: ' + ', '.join(nog) + '.']
    return out


def write_md(points, table, never, bundle, path, png, bt=None, bt_note='', history=()):
    f = lambda v: '-' if v is None else f'{v:,.0f}'
    curve_only = 'matches' not in bundle
    name, ep = team_info(bundle)
    last = points[-1][0]
    when = lambda t: f'{to_pdt(t):%Y-%m-%d %H:%M} {zname(t)}'
    lines = ['# Rating history (replica)', '',
             "The replica's Team Settings > Rating History chart for " + name + ": siarnaq's penalized displayed rating "
             "after each rated (ranked, non-tournament) scrimmage, from "
             f"`GET /api/compete/{ep}/match/historical_rating/`" +
             (", with each submission's first completed rated match marked" if not curve_only else '') +
             ". Regenerate with `tools/rating_history.py`; " +
             (f"data fetched {when(parse_ts(bundle['fetched_at']))}." if bundle.get('fetched_at') else
              "drawn from a cached file."), '',
             f'![rating history]({png})', '',
             f"{len(points)} rated matches; latest rating {points[-1][1]:,.0f} ({when(last)}). Times are Pacific; "
             f"the replica's own chart shows UTC (galaxy sets Highcharts `time.useUTC` under an axis titled \"Local Date & "
             f"Time\"), so it reads {utc_lead(last)} h later than this page.", '']
    if curve_only:
        lines.append("No submission markers: this file holds the historical_rating response alone. The markers need the "
                     "match list, from a live run of `tools/rating_history.py` or `--from-json build/rating-history.json`.")
    elif not table:
        lines.append('No submission has a completed rated match yet.')
    else:
        zl = zone_label([r['created'] for r in table])
        lines += ["Kind: validated = the submission an init/accept event of progress/ladder-state.json names; "
                  "re-upload = another upload of a build validated at some point; trial = a build never validated.", '',
                  f'| Submission | Build | Kind | First rated match | Time ({zl}) | Rating before | Rating after | Rated matches |',
                  '|---:|---|---|---:|---|---:|---:|---:|']
        for r in table:
            n = f"{r['matches']}" + (f" ({r['cancelled']} cancelled)" if r['cancelled'] else '')
            lines.append(f"| #{r['sub']} | {r['package']} | {LABEL[r['kind']]} | {r['match']} | {to_pdt(r['created']):%Y-%m-%d %H:%M} "
                         f"| {f(r['before'])}{chr(92) + '*' if r['before'] == 0 else ''} | {f(r['after'])} | {n} |")
        if any(r['before'] == 0 for r in table):
            lines += ['', "\\* Not a missing value: the API's old_rating for our first rated match. Siarnaq displays the "
                      "penalized rating Elo mean - 1500 x 0.85^n (n = rated games so far), which starts at 1500 - 1500 = 0."]
    if never:
        lines += ['', 'No rated match: ' + ', '.join(f'#{s} {p} ({LABEL[k]})' for s, p, k in never) + '.']
        for sid, pkg, t0, nsid, npkg, t1 in validated_unrated(never, history):
            lines += ['', f"#{sid} {pkg} was the validated build from {to_pdt(t0):%m-%d %H:%M} " +
                      (f"to {to_pdt(t1):%m-%d %H:%M} {zname(t1)}, when #{nsid} {npkg} replaced it before any ranked match "
                       f"was created: it has no point on the curve." if t1 else
                       f"{zname(t0)} and has not played a ranked match yet.")]
    nlow, tlow = below_floor(points)
    if nlow:
        lines += ['', f"The chart's left axis starts at {FLOOR:,} (owner, PROMPTS 45): {nlow} rated matches below it, the last at "
                  f"{when(tlow)}, are off the chart (the table keeps their submissions)."]
    if bt:
        lines += [''] + bt_md(bt, points)
    elif bt_note:
        lines += ['', bt_note]
    with open(path, 'w') as fh:
        fh.write('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from-json', help='a cached bundle (build/rating-history.json) or a raw historical_rating response')
    ap.add_argument('--state', default=STATE, help='ladder-state.json (validated builds, package names)')
    ap.add_argument('--outdir', default=os.path.join(REPO, 'progress')); o = ap.parse_args()
    if o.from_json:
        bundle = load(o.from_json)
    else:
        bundle = fetch()
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, 'w') as fh:
            json.dump(bundle, fh)
        print('cached', os.path.relpath(CACHE, REPO))
    points = points_from_history(bundle.get('historical_rating'))
    if not points:
        sys.exit('rating_history: no ranked matches (the Team page shows an empty chart)')
    history = history_events(o.state)
    names = package_names(bundle.get('submissions') or [], history)
    firsts = first_rated_use(bundle.get('matches') or [], bundle.get('team_id'))
    table = rows(points, firsts, names, history)
    never = [(s['id'], name_of(names, s['id']), kind_of(s['id'], names.get(s['id']), history))
             for s in sorted(bundle.get('submissions') or [], key=lambda s: s['id'])
             if s['id'] not in firsts and s.get('status') == 'OK!']
    os.makedirs(o.outdir, exist_ok=True)
    png = os.path.join(o.outdir, 'rating-history.png'); md = os.path.join(o.outdir, 'rating-history.md')
    bt, bt_note = None, ''
    if 'matches' in bundle:
        if not bundle.get('rankings'):
            bt_note = ('No Bradley-Terry axis: this bundle has no Rankings page (a live run of tools/rating_history.py '
                       'caches it).')
        else:
            bt = bt_layer(bundle['rankings'], elolib.fit(elolib.load()), table, history, points, bundle.get('team_id'))
            if bt is None:
                bt_note = 'No Bradley-Terry axis: fewer than 3 field teams to calibrate it on.'
    draw(points, table, bundle, png, bt, bt_note)
    write_md(points, table, never, bundle, md, os.path.basename(png), bt, bt_note, history)
    print(f'{len(points)} rated matches, latest rating {points[-1][1]:.0f} at {to_pdt(points[-1][0]):%Y-%m-%d %H:%M} '
          f'{zname(points[-1][0])}; {len(table)} submissions with a rated match, {len(never)} without')
    for r in table:
        print(f"  #{r['sub']:<4} {r['package']:<10} {r['kind']:<9} match {r['match']:<5} {to_pdt(r['created']):%m-%d %H:%M} {zname(r['created'])} "
              f"{r['before'] if r['before'] is None else round(r['before'])} -> {r['after']:.0f}, {r['matches']} rated")
    if bt:
        a, b, r, n, sd = bt['cal']
        print(f'calibration: BT = {a:.1f} + {b:.3f} x galaxy, r {r:.3f}, {n} teams, residual SD {sd:.0f} BT = '
              f'{sd / b:.1f} galaxy (+- {Z95 * sd / b:.0f} at 95%)')
        if bt.get('peers'):
            print(f"  {bt['peers'][0]} field teams within {PEER} of our latest rating: galaxy - converted BT "
                  f"{bt['peers'][1]:+.1f} on average")
        bts = lambda x: 'no games' if not x['bt'] else f"BT {x['bt'][0]:.0f} +- {Z95 * x['bt'][1]:.0f} ({x['bt'][2]} games)"
        for x in bt['steps']:
            stop = f"{to_pdt(x['end']):%m-%d %H:%M}" if x['end'] else 'now'
            print(f"  {x['package']:<10} {to_pdt(x['start']):%m-%d %H:%M} to {stop}: {bts(x)}, galaxy {x['galaxy_end']:.0f} at the end")
        for x in bt['trials']:
            print(f"  trial {x['package']:<10} {to_pdt(x['at']):%m-%d %H:%M}: {bts(x)}")
    elif bt_note:
        print(bt_note)
    print('wrote', png); print('wrote', md)


if __name__ == '__main__':
    main()
