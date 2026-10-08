#!/usr/bin/env python3
"""Snapshot of the replica ladder for GitHub: progress/ladder.md (markdown tables) and progress/ladder.png (the
ladder as an image, with rating sparklines). The owner's fallback when the web pages are unreachable.

RETIRED with galaxy-lite (2026-10-08, docs/replica/README.md): progress/ladder.{md,png} now come from the galaxy
replica (tools/galaxy/snapshot.py). This script reads only galaxy-lite's archived DB (--home <archive dir>); give it
--out-dir elsewhere so it does not overwrite the current snapshot.

  python3 tools/replica/snapshot.py --from-vm      on the driver: read the ladder on battlecode-dev over ssh
                                                   (tools/vm.sh gssh), write the files into this checkout
  python3 tools/replica/snapshot.py                on the VM: read the DB directly, write <repo>/progress/
  python3 tools/replica/snapshot.py --json         print the snapshot data as JSON (what --from-vm runs remotely)
Options: --home DIR (data dir; default as db.home(): $REPLICA_HOME, else /home/bcreplica/replica when it holds a DB,
else ~/replica), --out-dir DIR (default <repo>/progress), --recent N (latest completed matches listed; default 20),
--svg (write ladder.svg instead of ladder.png).

The image is a PNG drawn with matplotlib, which lives in the driver's tools/.venv (the script re-runs itself there,
as tools/elo.py does). Where matplotlib is missing (the VM), it writes ladder.svg instead; GitHub shows both inline.
Only one of the two is kept, so no stale image stays behind. The DB is opened read-only (any member of group
bcreplica can run this).
"""
import argparse
import json
import os
import sqlite3
import subprocess
import sys

if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from replica import db, web   # noqa: E402
else:
    from . import db, web

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VENV_PYTHON = os.path.join(REPO, 'tools', '.venv', 'bin', 'python')
VM_COMMAND = 'cd ~/projects/vibe/2023 && python3 tools/replica/snapshot.py --json'


def connect_ro(home):
    f = os.path.join(home, 'replica.db')
    if not os.path.isfile(f):
        raise SystemExit(f'snapshot: no replica DB at {f}')
    conn = sqlite3.connect(f'file:{f}?mode=ro', uri=True, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def collect(conn, recent=20, home=None):
    """Everything the renderers need, JSON-serializable."""
    rows = web.ladder(conn)
    ms = conn.execute("SELECT * FROM match WHERE status='OK!' ORDER BY finished DESC, id DESC LIMIT ?",
                      (recent,)).fetchall()
    matches = []
    for m in web.match_rows(conn, ms):
        matches.append({k: m[k] for k in ('id', 'status', 'created', 'finished', 'is_ranked', 'source', 'maps')}
                       | {'participants': [{k: p[k] for k in ('team', 'teamname', 'score', 'rating', 'old_rating')}
                                           for p in m['participants']]})
    return {'generated': db.now(), 'home': home, 'summary': web.summary(conn), 'ladder': rows, 'recent': matches}


def fetch_from_vm():
    """Run `snapshot.py --json` on battlecode-dev through tools/vm.sh (gssh) and return the parsed data."""
    vm_sh = os.path.join(REPO, 'tools', 'vm.sh')
    out = subprocess.run(['bash', '-c', 'source "$1" && IP="${IP:-10.138.0.3}" && gssh "$2"', '_', vm_sh, VM_COMMAND],
                         capture_output=True, text=True, timeout=180)
    if out.returncode != 0:
        raise SystemExit(f'snapshot: remote run failed ({out.returncode}): {out.stderr.strip()[-800:]}')
    return json.loads(out.stdout)


# ---------------------------------------------------------------- markdown
def md_escape(s):
    return ''.join('\\' + ch if ch in '\\`*_{}[]<>()#+!|~' else ch for ch in str(s))


def render_md(data, image='ladder.png'):
    s = data['summary']
    when = web.fmt_time(data['generated'], with_zone=True)
    lines = [
        '# Replica ladder',
        '',
        f'Snapshot of the private Battlecode 2023 ladder replica (galaxy-lite on battlecode-dev), taken {when}. '
        'Written by `tools/replica/snapshot.py`: regenerate it, do not edit it. The live pages, with replays, are the '
        "replica's web front (docs/replica/README.md).",
        '',
        f'{s["teams"]} teams, {s["done"]} matches done, {s["queued"]} queued, {s["running"]} running, '
        f'{s["error"]} errors, {s["games"]} games. Rating is galaxy\'s displayed (penalized) rating, '
        'mean − 1500·0.85^n, so a new team climbs from 0 over its first ~20 rated matches. Ranked W-L-T counts '
        'ranked matches; Games W-L counts every game, ranked and unranked. Our builds (`us:`) are in bold.',
        '',
        f'![Replica ladder]({image})',
        '',
        '| # | Team | Rating | Mean | n | Ranked W-L-T | Games W-L | Last match |',
        '|---:|---|---:|---:|---:|---|---|---|',
    ]
    for r in data['ladder']:
        name = md_escape(r['name'])
        if r['us']:
            name = f'**{name}**'
        lines.append(f'| {r["rank"]} | {name} | {web.num(r["value"])} | {web.num(r["mean"])} | {r["n"]} | '
                     f'{web.record(r["ranked_record"])} | {r["games"]["won"]}-{r["games"]["lost"]} | '
                     f'{web.fmt_time(r["last_match"]) or "–"} |')
    if not data['ladder']:
        lines.append('| | (no teams yet) | | | | | | |')
    lines += ['', '## Latest completed matches', '',
              '| Match | Finished | Team A | Score | Team B | Maps | Type |', '|---:|---|---|---|---|---|---|']

    def team(p):
        if p is None:
            return ''
        return f'**{md_escape(p["teamname"])}**' if p['teamname'].startswith('us:') else md_escape(p['teamname'])
    for m in data['recent']:
        a, b = (m['participants'] + [None, None])[:2]
        sc = '–'.join('?' if p is None or p['score'] is None else str(p['score']) for p in (a, b))
        lines.append(f'| {m["id"]} | {web.fmt_time(m["finished"])} | {team(a)} | {sc} | {team(b)} | '
                     f'{md_escape(", ".join(m["maps"]))} | {"ranked" if m["is_ranked"] else "unranked"} |')
    if not data['recent']:
        lines.append('| | (none yet) | | | | | |')
    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------- the image: one layout, two renderers
# Roles -> light-theme colours (the web pages' tokens); the SVG adds dark-mode values.
COLORS = {'bg': '#fcfcfb', 't': '#0b0b0b', 't2': '#52514e', 'm': '#898781', 'g': '#e1e0d9',
          'us': (42 / 255, 120 / 255, 214 / 255, 0.10), 'ln': '#2a78d6'}
SIZES = {'body': 13, 'h': 11, 'title': 18}


def layout(data, width=900):
    """(width, height, items) in pixels, y down. Items: ('rect', x, y, w, h, role), ('line', x1, y1, x2, y2, role),
    ('text', x, y, text, role, size, anchor, bold), ('poly', [(x, y)...], role), ('dot', x, y, r, role)."""
    rows = data['ladder']
    s = data['summary']
    row_h, top = 24, 84
    height = top + row_h * max(1, len(rows)) + 30
    items = [('text', 20, 32, 'bc23 replica ladder', 't', 'title', 'start', True),
             ('text', 20, 54, f'{web.fmt_time(data["generated"], with_zone=True)} · {s["teams"]} teams · '
              f'{s["done"]} matches done · {s["queued"]} queued · {s["running"]} running · {s["games"]} games · '
              'rating = mean − 1500·0.85^n', 't2', 'body', 'start', False)]
    cols = [('#', 36, 'end'), ('Team', 52, 'start'), ('Rating', 470, 'end'), ('Mean', 548, 'end'), ('n', 588, 'end'),
            ('Ranked W-L-T', 606, 'start'), ('Games W-L', 708, 'start'), ('Trend', 792, 'start')]
    for label, x, anchor in cols:
        items.append(('text', x, top - 8, label, 't2', 'h', anchor, True))
    items.append(('line', 16, top - 2, width - 16, top - 2, 'g'))
    for i, r in enumerate(rows):
        y0 = top + i * row_h
        if r['us']:
            items.append(('rect', 16, y0, width - 32, row_h, 'us'))
        name = r['name'] if len(r['name']) <= 52 else r['name'][:51] + '…'
        vals = [str(r['rank']), name, web.num(r['value']), web.num(r['mean']), str(r['n']),
                web.record(r['ranked_record']), f'{r["games"]["won"]}-{r["games"]["lost"]}']
        for (label, x, anchor), v in zip(cols, vals):
            items.append(('text', x, y0 + 16, v, 't', 'body', anchor, r['us'] and label in ('Team', 'Rating')))
        hist = [h['rating'] for h in r['history']]
        if r['history_len'] <= web.SPARK_POINTS:
            hist = [0.0] + hist      # the whole history: start from the initial displayed rating, 0
        if len(hist) >= 2:
            lo, hi = min(hist), max(hist)
            span = (hi - lo) or 1.0
            x0, w, h = 792, 90, row_h - 8
            pts = [(x0 + w * k / (len(hist) - 1), y0 + 4 + h - h * (v - lo) / span) for k, v in enumerate(hist)]
            items += [('poly', pts, 'ln'), ('dot', pts[-1][0], pts[-1][1], 3, 'ln')]
        items.append(('line', 16, y0 + row_h, width - 16, y0 + row_h, 'g'))
    if not rows:
        items.append(('text', 52, top + 16, 'no teams yet', 'm', 'body', 'start', False))
    items.append(('text', 20, height - 10, f'Trend: displayed rating over the last {web.SPARK_POINTS} ranked matches. '
                  'Bold rows are our builds (us:).', 'm', 'body', 'start', False))
    return width, height, items


SVG_STYLE = """
.bg{fill:#fcfcfb}.t{fill:#0b0b0b}.t2{fill:#52514e}.m{fill:#898781}.g{stroke:#e1e0d9;stroke-width:1}
.us{fill:rgba(42,120,214,.10)}.ln{fill:none;stroke:#2a78d6;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.dot{fill:#2a78d6;stroke:#fcfcfb;stroke-width:2}
text{font-family:system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;font-size:13px}
.h{font-size:11px}.title{font-size:18px}.b{font-weight:600}
@media (prefers-color-scheme:dark){.bg{fill:#1a1a19}.t{fill:#fff}.t2{fill:#c3c2b7}.g{stroke:#2c2c2a}
.us{fill:rgba(57,135,229,.18)}.ln{stroke:#3987e5}.dot{fill:#3987e5;stroke:#1a1a19}}
"""


def render_svg(data):
    esc = web.esc
    width, height, items = layout(data)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" aria-label="Replica ladder">',
           f'<style>{SVG_STYLE}</style>', f'<rect class="bg" width="{width}" height="{height}" rx="8"/>']
    for it in items:
        kind = it[0]
        if kind == 'rect':
            _, x, y, w, h, role = it
            out.append(f'<rect class="{role}" x="{x}" y="{y}" width="{w}" height="{h}"/>')
        elif kind == 'line':
            _, x1, y1, x2, y2, role = it
            out.append(f'<line class="{role}" x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}"/>')
        elif kind == 'text':
            _, x, y, text, role, size, anchor, bold = it
            cls = ' '.join([role] + ([size] if size != 'body' else []) + (['b'] if bold else []))
            out.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(text)}</text>')
        elif kind == 'poly':
            out.append('<polyline class="ln" points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in it[1]) + '"/>')
        elif kind == 'dot':
            _, x, y, r, role = it
            out.append(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
    out.append('</svg>')
    return '\n'.join(out) + '\n'


def have_matplotlib():
    try:
        import matplotlib  # noqa: F401
        return True
    except ImportError:
        return False


def render_png(data, path, dpi=120):
    """The same layout drawn with matplotlib (Agg): one axes in pixel units, y down."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    width, height, items = layout(data)
    px = 72 / 100            # points per layout pixel at the 100-dpi design scale
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    fig.patch.set_facecolor(COLORS['bg'])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis('off')
    ha = {'start': 'left', 'end': 'right', 'middle': 'center'}
    for it in items:
        kind = it[0]
        if kind == 'rect':
            _, x, y, w, h, role = it
            ax.add_patch(Rectangle((x, y), w, h, facecolor=COLORS[role], edgecolor='none'))
        elif kind == 'line':
            _, x1, y1, x2, y2, role = it
            ax.plot([x1, x2], [y1, y2], color=COLORS[role], linewidth=1 * px, solid_capstyle='butt')
        elif kind == 'text':
            _, x, y, text, role, size, anchor, bold = it
            ax.text(x, y, text, color=COLORS[role], fontsize=SIZES[size] * px, ha=ha[anchor], va='baseline',
                    fontweight='bold' if bold else 'normal', family='DejaVu Sans')
        elif kind == 'poly':
            xs, ys = zip(*it[1])
            ax.plot(xs, ys, color=COLORS['ln'], linewidth=2 * px, solid_joinstyle='round', solid_capstyle='round')
        elif kind == 'dot':
            _, x, y, r, role = it
            ax.add_patch(Circle((x, y), r + 1, facecolor=COLORS['ln'], edgecolor=COLORS['bg'], linewidth=2 * px))
    fig.savefig(path, dpi=dpi, facecolor=COLORS['bg'])
    plt.close(fig)


def write(data, out_dir, fmt='png'):
    """Write ladder.md and ladder.<fmt>; remove the other image format so no stale image stays. Returns the paths."""
    os.makedirs(out_dir, exist_ok=True)
    image = f'ladder.{fmt}'
    paths = []
    p = os.path.join(out_dir, image)
    if fmt == 'png':
        render_png(data, p + '.tmp.png')
        os.replace(p + '.tmp.png', p)
    else:
        with open(p + '.tmp', 'w') as fh:
            fh.write(render_svg(data))
        os.replace(p + '.tmp', p)
    paths.append(p)
    p = os.path.join(out_dir, 'ladder.md')
    with open(p + '.tmp', 'w') as fh:
        fh.write(render_md(data, image))
    os.replace(p + '.tmp', p)
    paths.append(p)
    other = os.path.join(out_dir, 'ladder.svg' if fmt == 'png' else 'ladder.png')
    if os.path.exists(other):
        os.remove(other)
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--home')
    ap.add_argument('--out-dir', default=os.path.join(REPO, 'progress'))
    ap.add_argument('--recent', type=int, default=20)
    ap.add_argument('--svg', action='store_true', help='write ladder.svg instead of ladder.png')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--json', action='store_true', help='print the data as JSON instead of writing files')
    g.add_argument('--from-vm', action='store_true', help='fetch the data from battlecode-dev over ssh')
    a = ap.parse_args(argv)
    if (argv is None and not a.json and not a.svg and not have_matplotlib() and os.path.exists(VENV_PYTHON)
            and '.venv' not in sys.prefix):
        os.execv(VENV_PYTHON, [VENV_PYTHON, os.path.abspath(__file__)] + sys.argv[1:])   # matplotlib lives there
    if a.from_vm:
        data = fetch_from_vm()
    else:
        home = os.path.abspath(os.path.expanduser(a.home)) if a.home else db.home()
        conn = connect_ro(home)
        try:
            data = collect(conn, a.recent, home)
        finally:
            conn.close()
    if a.json:
        print(json.dumps(data))
        return 0
    fmt = 'png' if not a.svg and have_matplotlib() else 'svg'
    for p in write(data, a.out_dir, fmt):
        print(f'snapshot: wrote {p}')
    print(f'snapshot: {len(data["ladder"])} teams, data from {data.get("home")} at '
          f'{web.fmt_time(data["generated"], with_zone=True)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
