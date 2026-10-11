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
options set time.useUTC although the axis is titled "Local Date & Time"), so the replica shows each time 7 h later."""
import argparse, bisect, collections, datetime as dt, json, os, sys
_venv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'bin', 'python')
if os.path.exists(_venv) and '.venv' not in sys.prefix and __name__ == '__main__': os.execv(_venv, [_venv] + sys.argv)
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, 'progress', 'ladder-state.json')
CACHE = os.path.join(REPO, 'build', 'rating-history.json')
PDT = ZoneInfo('America/Los_Angeles'); UTC = dt.timezone.utc
# the reference palette's categorical slots 1-3 (blue, orange, violet), validated together on the light surface
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e6e5e0'
CURVE = '#2a78d6'
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


# ---------------------------------------------------------------- data
def fetch():
    """The replica's responses, GET only, as our team (tools/contest.py holds the credentials)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import contest
    ep = contest.EPISODE
    hist = contest.api('GET', f'/api/compete/{ep}/match/historical_rating/')
    tid = (hist or {}).get('team_id') or contest.me()['id']
    keep = ('id', 'package', 'description', 'created', 'status', 'accepted')
    subs = [{k: s.get(k) for k in keep} for s in contest.pages(f'/api/compete/{ep}/submission/')]
    return {'fetched_at': dt.datetime.now(UTC).isoformat(), 'episode': ep, 'team_id': tid, 'historical_rating': hist,
            'matches': contest.matches(tid, limit_pages=None), 'submissions': subs,
            'tournaments': contest.pages(f'/api/episode/{ep}/tournament/')}


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
def draw(points, table, bundle, path):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FuncFormatter
    curve_only = 'matches' not in bundle   # a raw historical_rating response: no match list, so no markers
    W, H, L, R, B, T = 13.0, 6.6, 0.06, 0.985, 0.19, (0.9 if curve_only else 0.78)   # the top band holds the labels
    fig = plt.figure(figsize=(W, H), facecolor=SURFACE)
    ax = fig.add_axes([L, B, R - L, T - B], facecolor=SURFACE)
    xs = [to_pdt(t) for t, _ in points]; ys = [r for _, r in points]
    ax.plot(xs, ys, '-', color=CURVE, lw=2, solid_joinstyle='round', solid_capstyle='round', zorder=3)
    ax.plot(xs, ys, 'o', color=CURVE, ms=2.6, mew=0, zorder=4)
    end = parse_ts(bundle['fetched_at']) if bundle.get('fetched_at') else points[-1][0]
    span = max((end - points[0][0]).total_seconds(), 3600)
    x0 = to_pdt(points[0][0] - dt.timedelta(seconds=0.01 * span)); x1 = to_pdt(max(end, points[-1][0]) + dt.timedelta(seconds=0.01 * span))
    ax.set_xlim(x0, x1)
    lo, hi = min(ys), max(ys); pad = 0.06 * max(hi - lo, 50)
    ax.set_ylim(lo - pad, hi + pad)
    # tournaments, as galaxy's plotLines (none on the replica so far)
    for t in bundle.get('tournaments') or []:
        if t.get('display_date'):
            d = to_pdt(parse_ts(t['display_date']))
            if x0 <= d <= x1:
                ax.axvline(d, color=INK2, lw=1, zorder=1)
                ax.annotate(t.get('name_long') or t.get('name_short') or '', (d, 0.02), xycoords=('data', 'axes fraction'),
                            xytext=(3, 0), textcoords='offset points', fontsize=8, color=INK2, rotation=90, va='bottom')
    # each submission's first rated match: a dotted line, a ringed marker on the curve, a label above the plot. The
    # surface ring sits under the curve (it only cuts the dotted line), so close markers never hide a segment.
    xnum = mdates.date2num([to_pdt(r['created']) for r in table])
    a, b = mdates.date2num(x0), mdates.date2num(x1)
    frac = [(x - a) / (b - a) for x in xnum]
    lab = spread(frac, 0.155 / (W * (R - L)), 0.0, 1.0)   # 0.155 in between label centres (8 pt text, rotated)
    for r, x, f in zip(table, xnum, lab):
        col, filled, _ = KINDS[r['kind']]
        ax.axvline(x, color=col, lw=1, ls=(0, (1, 2.5)), alpha=0.8, zorder=2)
        ax.plot([x], [r['after']], 'o', ms=8, mfc=col if filled else SURFACE, mec=col, mew=2, zorder=6)
        ax.plot([x], [r['after']], 'o', ms=12, mfc='none', mec=SURFACE, mew=2, zorder=2.5)   # the surface ring
        ax.annotate(f"#{r['sub']} {r['package']}", xy=(x, 1.0), xycoords=('data', 'axes fraction'),
                    xytext=(f, 1.045), textcoords='axes fraction', rotation=90, ha='center', va='bottom', fontsize=8,
                    color=INK, annotation_clip=False,
                    arrowprops=dict(arrowstyle='-', color=col, lw=0.9, shrinkA=1, shrinkB=0, relpos=(0.5, 0.0)))
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
    ax.set_xlabel(f'Date & time ({zl})', color=INK2, fontsize=10); ax.set_ylabel('Rating', color=INK2, fontsize=10)
    fig.suptitle(f'Rating History - {team_info(bundle)[0]} (replica)', x=L, y=0.985, ha='left', fontsize=14, color=INK,
                 fontweight='bold')
    hs = [Line2D([], [], color=CURVE, lw=2, marker='o', ms=3, label="rating after each rated match (the Team page's curve)")]
    for k in [k for k in KINDS if any(r['kind'] == k for r in table)]:
        col, filled, text = KINDS[k]
        hs.append(Line2D([], [], color=col, lw=1, ls=(0, (1, 2)), marker='o', ms=7, mfc=col if filled else SURFACE,
                         mec=col, mew=2, label=text))
    leg = ax.legend(handles=hs, loc='lower right', fontsize=8.5, frameon=True, facecolor=SURFACE, edgecolor=GRID)
    for t in leg.get_texts(): t.set_color(INK)
    n = len(points)
    canc = sum(1 for _, m, _ in rated(bundle.get('matches') or [], bundle.get('team_id')) if m.get('status') != 'OK!')
    marks = ("No submission markers: this file is the curve alone (they need the match list of a live run or "
             "build/rating-history.json)." if curve_only else
             "Dotted lines: each submission's first completed rated match, labelled #submission build." if table else
             "No submission has a completed rated match yet.")
    note = (f"{n} rated matches (ranked, non-tournament scrimmages{f'; {canc} cancelled, rating unchanged' if canc else ''}), "
            f"{to_pdt(points[0][0]):%b %d %H:%M} to {to_pdt(points[-1][0]):%b %d %H:%M}. Latest rating "
            f"{points[-1][1]:,.0f}.\n{marks} All times are {zl} (the replica's chart shows UTC, "
            f"{utc_lead(points[-1][0])} h later).")
    fig.text(L, 0.018, note, fontsize=9, color=INK2, ha='left', va='bottom')
    fig.savefig(path, dpi=120, facecolor=SURFACE); plt.close(fig)


def write_md(points, table, never, bundle, path, png):
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
    draw(points, table, bundle, png)
    write_md(points, table, never, bundle, md, os.path.basename(png))
    print(f'{len(points)} rated matches, latest rating {points[-1][1]:.0f} at {to_pdt(points[-1][0]):%Y-%m-%d %H:%M} '
          f'{zname(points[-1][0])}; {len(table)} submissions with a rated match, {len(never)} without')
    for r in table:
        print(f"  #{r['sub']:<4} {r['package']:<10} {r['kind']:<9} match {r['match']:<5} {to_pdt(r['created']):%m-%d %H:%M} {zname(r['created'])} "
              f"{r['before'] if r['before'] is None else round(r['before'])} -> {r['after']:.0f}, {r['matches']} rated")
    print('wrote', png); print('wrote', md)


if __name__ == '__main__':
    main()
