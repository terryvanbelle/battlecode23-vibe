#!/usr/bin/env python3
"""Snapshot of the galaxy replica's ladder for GitHub: progress/ladder.md (tables) and progress/ladder.png (a chart).
The owner's fallback when the site is out of reach (ACCESS.md).

  tools/.venv/bin/python tools/galaxy/snapshot.py [--out-dir progress] [--ours vibe23] [--recent 20]
  python3 tools/galaxy/snapshot.py --json            print the collected data instead

The ladder is the data of the site's Rankings page: GET /api/team/<ep>/t/?ordering=-rating,name, every page, read
logged out through the site's gate, as the page does. Rating is the replica's displayed rating, siarnaq's penalized
Elo (mean - 1500 * 0.85^n after n rated matches), so a new team climbs from 0 over its first ~20 ranked matches.
Recent matches come from the match list (the Queue page's data, logged out: scores but no replay links). The games
column counts the games of each team recorded in progress/games.csv from the replica (runs galaxy-*; our builds
'us:*' are summed into our team), which tools/galaxy/results.py downloads.

matplotlib lives in the driver's tools/.venv; the script re-runs itself there when the system python lacks it.
"""
import argparse
import csv
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from client import Client, rankings  # noqa: E402

VENV_PYTHON = os.path.join(REPO, 'tools', '.venv', 'bin', 'python')
GAMES = os.path.join(REPO, 'progress', 'games.csv')
MAPPING = os.path.join(HERE, 'field-teams.tsv')
try:
    from zoneinfo import ZoneInfo
    LOCAL = ZoneInfo('America/Los_Angeles')         # the owner's time zone (PROMPTS.md)
except Exception:                                    # no tz database: a fixed PDT offset
    LOCAL = datetime.timezone(datetime.timedelta(hours=-7), 'PDT')

# chart tokens (light surface): context bars in the de-emphasis gray, our team in the accent
C = {'surface': '#fcfcfb', 'ink': '#0b0b0b', 'ink2': '#52514e', 'muted': '#898781', 'grid': '#e1e0d9',
     'bar': '#c3c2b7', 'ours': '#2a78d6'}


def game_records(path=GAMES, mapping=MAPPING, ours='vibe23'):
    """{galaxy team name: [won, lost]} over the galaxy-* games in games.csv."""
    to_team = {}
    if os.path.exists(mapping):
        with open(mapping) as fh:
            to_team = {r['entrant']: r['team'] for r in csv.DictReader((l for l in fh if not l.startswith('#')),
                                                                        delimiter='\t')}
    rec = {}
    if not os.path.exists(path):
        return rec
    with open(path) as fh:
        for r in csv.DictReader(fh):
            if not r['run'].startswith('galaxy-'):
                continue
            for side, name in (('A', r['teamA']), ('B', r['teamB'])):
                team = ours if name.startswith('us:') else to_team.get(name, name)
                wl = rec.setdefault(team, [0, 0])
                wl[0 if r['winner'] == side else 1] += 1
    return rec


def collect(c, ours='vibe23', recent=20):
    ladder = rankings(c)
    ms, page = [], 1
    while len(ms) < recent:
        r = c.request('GET', f'/api/compete/{c.episode}/match/?page={page}')
        ms += r.get('results', [])
        if not r.get('next'):
            break
        page += 1
    rec = game_records(ours=ours)
    for t in ladder:
        t['games'] = rec.get(t['name'], [0, 0])
        t['ours'] = t['name'] == ours
    matches = [{'id': m['id'], 'status': m['status'], 'created': m['created'], 'is_ranked': m['is_ranked'],
                'maps': m.get('maps') or [],
                'participants': [{'teamname': p['teamname'], 'score': p['score'], 'player_index': p['player_index']}
                                 for p in sorted(m.get('participants') or [], key=lambda p: p['player_index'])]}
               for m in ms[:recent]]
    return {'generated': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'site': c.site, 'episode': c.episode, 'ours': ours, 'ladder': ladder, 'recent': matches}


def fmt_time(iso):
    t = datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(LOCAL)
    return t.strftime('%b %-d %H:%M %Z')


def md_escape(s):
    return ''.join('\\' + ch if ch in '\\`*_{}[]<>()#+!|~' else ch for ch in str(s))


def num(v):
    return '–' if v is None else f'{v:.1f}'


def render_md(data, image='ladder.png'):
    lad = data['ladder']
    rated = [t for t in lad if t['has_active_submission']]
    played = sum(1 for t in lad if sum(t['games']))
    lines = [
        '# Galaxy replica ladder',
        '',
        f'Snapshot of the Rankings page of our private galaxy replica ({data["site"]}/{data["episode"]}/rankings), '
        f'taken {fmt_time(data["generated"])}. Written by `tools/galaxy/snapshot.py`: regenerate it, do not edit it. '
        'The live site, with replays, is described in ACCESS.md.',
        '',
        f'**Rating is the galaxy replica\'s displayed rating**: siarnaq\'s penalized Elo, mean − 1500·0.85^n after n '
        'rated matches, so every team starts at 0 and climbs over its first ~20 ranked matches. It is not the '
        f'Bradley-Terry fit of `progress/ELO.md`. {len(lad)} teams ({len(rated)} with an accepted submission). '
        f'Games W-L counts the games recorded in `progress/games.csv` from the replica ({played} teams have some); '
        f'our team is **{md_escape(data["ours"])}**, whose builds appear there as `us:<package>`.',
        '',
        f'![Galaxy replica ladder]({image})',
        '',
        '| # | Team | Rating | Games W-L | Submission |',
        '|---:|---|---:|---|---|',
    ]
    for t in lad:
        name = md_escape(t['name'])
        if t['ours']:
            name = f'**{name}**'
        lines.append(f'| {t["rank"]} | {name} | {num(t["rating"])} | {t["games"][0]}-{t["games"][1]} | '
                     f'{"accepted" if t["has_active_submission"] else "none"} |')
    if not lad:
        lines.append('| | (no teams yet) | | | |')
    lines += ['', '## Latest matches', '', '| Match | Created | Player 0 | Score | Player 1 | Maps | Type | Status |',
              '|---:|---|---|---|---|---|---|---|']
    for m in data['recent']:
        ps = m['participants'] + [None, None]
        a, b = ps[0], ps[1]

        def team(p):
            if p is None:
                return ''
            n = md_escape(p['teamname'])
            return f'**{n}**' if p['teamname'] == data['ours'] else n
        sc = '–'.join('?' if p is None or p['score'] is None else str(p['score']) for p in (a, b))
        lines.append(f'| {m["id"]} | {fmt_time(m["created"])} | {team(a)} | {sc} | {team(b)} | '
                     f'{md_escape(", ".join(m["maps"]))} | {"ranked" if m["is_ranked"] else "unranked"} | '
                     f'{m["status"]} |')
    if not data['recent']:
        lines.append('| | (none yet) | | | | | | |')
    return '\n'.join(lines) + '\n'


def render_png(data, path):
    """Ranked horizontal bars of the displayed rating, one per team; our team in the accent, the rest gray."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker  # noqa: F401
    lad = data['ladder'] or [{'name': '(no teams yet)', 'rating': 0, 'ours': False, 'rank': 1}]
    n = len(lad)
    row = 0.19                                            # inches per team
    fig_h = 1.3 + row * n
    fig, ax = plt.subplots(figsize=(8.6, fig_h), dpi=120)
    fig.patch.set_facecolor(C['surface'])
    ax.set_facecolor(C['surface'])
    vals = [t['rating'] or 0 for t in lad]
    ys = list(range(n))
    colors = [C['ours'] if t['ours'] else C['bar'] for t in lad]
    ax.barh(ys, vals, height=0.72, color=colors, edgecolor='none', zorder=2)
    ax.set_yticks(ys)
    ax.set_yticklabels([f'{t["rank"]}. {t["name"]}' for t in lad], fontsize=7.2, color=C['ink2'])
    for lab, t in zip(ax.get_yticklabels(), lad):
        if t['ours']:
            lab.set_color(C['ink'])
            lab.set_fontweight('bold')
    ax.invert_yaxis()
    ax.set_ylim(n - 0.5, -0.5)
    top = max(vals + [100])                              # before any rated match every team is at 0
    ax.set_xlim(0, top * 1.12)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    for y, t, v in zip(ys, lad, vals):
        if t['ours'] or t['rank'] <= 3:                  # selective labels: the leaders and our team
            ax.text(v + top * 0.01, y, f'{v:.0f}', va='center', ha='left', fontsize=7.2,
                    color=C['ink'] if t['ours'] else C['ink2'], fontweight='bold' if t['ours'] else 'normal')
    ax.grid(axis='x', color=C['grid'], linewidth=0.8, zorder=0)
    ax.tick_params(axis='x', colors=C['muted'], labelsize=7.5, length=0)
    ax.tick_params(axis='y', length=0)
    ax.xaxis.set_ticks_position('top')
    for s in ('top', 'right', 'bottom'):
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_color(C['bar'])
    title = 'Galaxy replica ladder: displayed rating (penalized Elo)'
    sub = (f'{fmt_time(data["generated"])} · {len(data["ladder"])} teams · our team {data["ours"]} in blue · '
           'rating = mean − 1500·0.85^n, from 0')
    fig.text(0.015, 1 - 0.32 / fig_h, title, fontsize=11, fontweight='bold', color=C['ink'], ha='left')
    fig.text(0.015, 1 - 0.55 / fig_h, sub, fontsize=7.8, color=C['ink2'], ha='left')
    fig.subplots_adjust(left=0.36, right=0.97, top=1 - 1.0 / fig_h, bottom=0.25 / fig_h)
    fig.savefig(path, dpi=120, facecolor=C['surface'])
    plt.close(fig)


def write(data, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, 'ladder.png')
    render_png(data, png + '.tmp.png')
    os.replace(png + '.tmp.png', png)
    md = os.path.join(out_dir, 'ladder.md')
    with open(md + '.tmp', 'w') as fh:
        fh.write(render_md(data, 'ladder.png'))
    os.replace(md + '.tmp', md)
    svg = os.path.join(out_dir, 'ladder.svg')
    if os.path.exists(svg):                              # an image of the old format would be stale
        os.remove(svg)
    return [png, md]


def have_matplotlib():
    try:
        import matplotlib  # noqa: F401
        return True
    except ImportError:
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--site', default=None)
    ap.add_argument('--connect', default=os.environ.get('GALAXY_CONNECT') or None)
    ap.add_argument('--out-dir', default=os.path.join(REPO, 'progress'))
    ap.add_argument('--ours', default='vibe23')
    ap.add_argument('--recent', type=int, default=20)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    if (argv is None and not a.json and not have_matplotlib() and os.path.exists(VENV_PYTHON)
            and '.venv' not in sys.prefix):
        os.execv(VENV_PYTHON, [VENV_PYTHON, os.path.abspath(__file__)] + sys.argv[1:])
    kw = {'connect': a.connect}
    if a.site:
        kw['site'] = a.site
    data = collect(Client(**kw), a.ours, a.recent)
    if a.json:
        print(json.dumps(data))
        return 0
    for p in write(data, a.out_dir):
        print(f'snapshot: wrote {p}')
    print(f'snapshot: {len(data["ladder"])} teams from {data["site"]} at {fmt_time(data["generated"])}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
