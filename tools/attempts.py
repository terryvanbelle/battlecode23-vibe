#!/usr/bin/env python3
"""The attempts ledger (owner, PROMPTS 130): every bot attempt, its description and its score at each stage of the
acceptance funnel. progress/attempts.csv is the source (one row per attempt); progress/ATTEMPTS.md is rendered from it.

  tools/attempts.py set <codename> field=value ...   add or update a row (fields: COLUMNS; '+=' appends with '; ')
  tools/attempts.py h2h <codename> <results.csv> [--random]
                         score an all-maps head-to-head run into h2h_map (or h2h_random): "W/N vs OPP, signal +S"
                         (signal = maps won on both sides minus maps lost on both sides), appended to the cell
  tools/attempts.py sync     fill EMPTY screen / panel / outcome cells from progress/screens/*.json, the panel runs
                             (gauntlet/*-panel-<codename>/results.csv) and progress/ladder-state.json
  tools/attempts.py render   write progress/ATTEMPTS.md
  tools/attempts.py check    list src/ packages with no row (exit 1 if any)
  tools/attempts.py refresh  sync, render, check (tools/progress-refresh.sh runs this)

Cells filled by hand win over sync, which only fills empty cells; the panel net comes from tools/paired.py at the
decision and is recorded with set.
"""
import collections, csv, glob, json, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CSV = REPO / 'progress' / 'attempts.csv'
MD = REPO / 'progress' / 'ATTEMPTS.md'
COLUMNS = ['codename', 'date', 'base', 'description', 'other_tests', 'h2h_map', 'h2h_random', 'screen', 'panel',
           'outcome', 'sources']
SHOWN = [('codename', 'Codename'), ('date', 'Built (PDT)'), ('base', 'Base'), ('description', 'What it changes'),
         ('other_tests', 'Other local tests'), ('h2h_map', 'Local h2h, map seeds'),
         ('h2h_random', 'Local h2h, random seeds'), ('screen', 'Screen'), ('panel', 'Panel trial'),
         ('outcome', 'Outcome')]
NOT_ATTEMPTS = ('arch_', 'bot', 'examplefuncsplayer')   # archetypes (opponent models), the harness, the starter bot
PANEL_MAPS = "DefaultMap Maze Forest ReverseFunnel Cat IslandHopping Hah BatSignal Cornucopia MassiveL".split()


def load(path=None):
    path = Path(path or CSV)
    if not path.exists():
        return []
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for c in COLUMNS:
            r[c] = (r.get(c) or '').strip()
    return rows


def save(rows, path=None):
    path = Path(path or CSV)
    rows = sorted(rows, key=lambda r: (r['date'] or '9999', r['codename']))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, '') for c in COLUMNS})


def row_for(rows, name, create=True):
    for r in rows:
        if r['codename'] == name:
            return r
    if not create:
        return None
    r = {c: '' for c in COLUMNS}
    r['codename'] = name
    rows.append(r)
    return r


def set_fields(rows, name, assigns):
    r = row_for(rows, name)
    for a in assigns:
        i = a.find('=')
        if i <= 0:
            raise SystemExit(f'attempts: bad assignment {a!r} (field=value or field+=value)')
        append = a[i - 1] == '+'
        k, v = a[:i - 1] if append else a[:i], a[i + 1:]
        k = k.strip()
        if k not in COLUMNS or k == 'codename':
            raise SystemExit(f'attempts: unknown field {k!r} (fields: {", ".join(COLUMNS[1:])})')
        v = v.strip()
        r[k] = f'{r[k]}; {v}' if append and r[k] and v else (v if not append else r[k] or v)
    return r


def h2h_cell(results_csv):
    """'W/N vs OPP, signal +S' for each opponent of an all-maps run (results.csv of tools/gauntlet.sh)."""
    with open(results_csv, newline='') as f:
        rows = list(csv.DictReader(f))
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        by[r.get('opponent', '?')][r['map']].append(r['bot_result'] == 'win')
    cells = []
    for opp, m in by.items():
        n = sum(len(v) for v in m.values())
        w = sum(sum(v) for v in m.values())
        both = sum(1 for v in m.values() if len(v) >= 2 and all(v))
        none = sum(1 for v in m.values() if len(v) >= 2 and not any(v))
        cells.append(f'{w}/{n} vs {opp}, signal {both - none:+d}')
    return '; '.join(cells)


def screen_cell(rec):
    st = rec.get('stages', {})
    parts = []
    a = st.get('a')
    if a:
        parts.append(f"a {a.get('wins', '?')}/{a.get('games', '?')}")
    b = st.get('b')
    if b:
        parts.append(f"b {b.get('wins', '?')}/{b.get('games', '?')}")
    c = st.get('c')
    if c:
        pooled, info = c.get('pooled') or {}, c.get('info_pooled') or {}
        if pooled.get('g') or pooled.get('l'):
            parts.append(f"c {pooled.get('net', 0):+d}")
        elif info:
            parts.append(f"c {info.get('net', 0):+d} info")
    d = st.get('d')
    if d:
        bad = [f'{k} {d[k]}' for k in ('over', 'exceptions', 'deaths_self') if d.get(k)]
        parts.append('d ' + (', '.join(bad) if bad else 'clean'))
    verdict = rec.get('verdict') or ''
    return f"{verdict}: {', '.join(parts)}" if parts else verdict


def screens_by_package(repo=REPO):
    best = {}
    for f in glob.glob(str(repo / 'progress' / 'screens' / '*.json')):
        try:
            rec = json.loads(Path(f).read_text())
        except (OSError, ValueError):
            continue
        name = rec.get('candidate')
        if not name or not rec.get('verdict'):
            continue
        if name not in best or (rec.get('finished') or '') > (best[name].get('finished') or ''):
            best[name] = rec
    return best


def panel_version(run):
    """The panel version a run played (its provenance.txt cells= looked up in test/cells/panels.json), or None."""
    try:
        cells = next((w[6:] for w in (run / 'provenance.txt').read_text().split() if w.startswith('cells=')), None)
        reg = json.loads((REPO / 'test' / 'cells' / 'panels.json').read_text())['versions']
    except (OSError, ValueError, KeyError):
        return None
    return next((v['version'] for v in reg if cells and Path(v['cells']) == Path(cells)), None)


def panel_scores(repo=REPO):
    """{package: 'W/N'} from the latest gauntlet/*-panel-<package>/results.csv."""
    out = {}
    for d in sorted(glob.glob(str(repo / 'gauntlet' / '*-panel-*'))):
        f = Path(d) / 'results.csv'
        if not f.exists():
            continue
        name = Path(d).name.split('-panel-', 1)[1]
        with open(f, newline='') as fh:
            rows = list(csv.DictReader(fh))
        if rows:
            ver = panel_version(Path(d))
            out[name] = (f'{ver}: ' if ver else '') + f"{sum(r['bot_result'] == 'win' for r in rows)}/{len(rows)}"
    return out


def ladder_outcomes(repo=REPO):
    """{package: outcome} from progress/ladder-state.json's history (the last decision wins)."""
    p = repo / 'progress' / 'ladder-state.json'
    if not p.exists():
        return {}
    st = json.loads(p.read_text())
    out = {}
    for e in st.get('history', []):
        pkg, ev = e.get('package'), e.get('event')
        if not pkg:
            continue
        if ev == 'accept':
            out[pkg] = f"ACCEPTED (sub {e.get('submission')})"
        elif ev == 'reject':
            out[pkg] = 'REJECTED (panel)'
        elif ev == 'trial-start' and pkg not in out:
            out[pkg] = 'in trial'
        elif ev == 'init':
            out[pkg] = 'baseline'
    tr = st.get('trial')
    if tr and tr.get('package'):
        out[tr['package']] = 'in trial'
    return out


def sync(rows, repo=REPO):
    changed = 0
    screens, panels, outcomes = screens_by_package(repo), panel_scores(repo), ladder_outcomes(repo)
    for r in rows:
        n = r['codename']
        if not r['screen'] and n in screens:
            r['screen'] = screen_cell(screens[n]); changed += 1
        if not r['panel'] and n in panels:
            r['panel'] = panels[n]; changed += 1
        if n in outcomes and (not r['outcome'] or (r['outcome'] in ('in trial', 'in progress')
                                                     and outcomes[n] != 'in trial')):
            r['outcome'] = outcomes[n]; changed += 1
    return changed


def missing(rows, repo=REPO):
    have = {r['codename'] for r in rows}
    return sorted(p.name for p in (repo / 'src').iterdir()
                  if p.is_dir() and not p.name.startswith(NOT_ATTEMPTS[0]) and p.name not in NOT_ATTEMPTS[1:]
                  and p.name not in have)


def kind(outcome):
    o = outcome.upper()
    if o.startswith('ACCEPTED'): return 'accepted'
    if o.startswith('REJECTED (PANEL'): return 'rejected on the panel'
    if o.startswith('REJECTED (SCREEN'): return 'rejected at the screen'
    if o.startswith('DROPPED'): return 'dropped before the next stage'
    if o.startswith('BASELINE'): return 'baseline'
    if o.startswith(('IN TRIAL', 'IN PROGRESS')): return 'in progress'
    return 'other (parked, subsumed, not tested)'


def esc(s):
    return s.replace('|', '\\|').replace('\n', ' ')


def render(rows, path=None):
    rows = sorted(rows, key=lambda r: (r['date'] or '9999', r['codename']))
    kinds = collections.Counter(kind(r['outcome']) for r in rows)
    lines = [
        '# Attempts',
        '',
        'Every bot attempt, newest last, with its score at each stage of the acceptance funnel (owner, PROMPTS 130).',
        'Generated by `tools/attempts.py render` from `progress/attempts.csv`; update a row with `tools/attempts.py set`.',
        '',
        '**The funnel** (since 2026-10-11; earlier attempts were judged by calibration cells against field bots, '
        '20-game head-to-heads and ladder trials, listed under "Other local tests"):',
        '1. **Local h2h**: every map, both sides (206 games) against the incumbent, first with map seeds, then random '
        'seeds. *Signal* = maps won on both sides minus maps lost on both sides.',
        '2. **Screen** (`tools/screen.py`): (a) basics vs examplefuncsplayer; (b) head-to-head on the 10 panel maps, '
        'both sides, against the validated build (PASS at 11/20, BORDERLINE at 9); (c) the archetype roster, paired '
        'with the incumbent (net; "info" = no gating archetype); (d) overruns, exceptions and self-deaths over all '
        'candidate games.',
        '3. **Panel trial**: 100 games on the replica against 10 field bots; *net* = games gained minus games lost '
        'against the validated build\'s panel (`tools/paired.py`; most games are identical). The panel is versioned '
        '(`test/cells/panels.json`, prefix v1/v2; rows without a prefix played v1): v1 from 2026-10-07, v2 from '
        '2026-10-20 (the ten opponents nearest us by BT, 100 distinct maps).',
        '4. **Outcome**: accepted (submission id), rejected, dropped before the next stage, parked or subsumed.',
        '',
        'Totals: ' + ', '.join(f'{v} {k}' for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]))
        + f' ({len(rows)} attempts).',
        '',
        '| ' + ' | '.join(h for _, h in SHOWN) + ' |',
        '|' + '|'.join('---' for _ in SHOWN) + '|',
    ]
    for r in rows:
        cells = [esc(r[k]) for k, _ in SHOWN]
        cells[0] = f'`{cells[0]}`'
        lines.append('| ' + ' | '.join(cells) + ' |')
    Path(path or MD).write_text('\n'.join(lines) + '\n')


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__); return 0
    cmd, rest = argv[0], argv[1:]
    rows = load()
    if cmd == 'set':
        if len(rest) < 2:
            raise SystemExit('usage: tools/attempts.py set <codename> field=value ...')
        set_fields(rows, rest[0], rest[1:]); save(rows); render(load()); return 0
    if cmd == 'h2h':
        if len(rest) < 2:
            raise SystemExit('usage: tools/attempts.py h2h <codename> <results.csv> [--random]')
        field = 'h2h_random' if '--random' in rest[2:] else 'h2h_map'
        cell = h2h_cell(rest[1])
        set_fields(rows, rest[0], [f'{field}+={cell}']); save(rows); render(load())
        print(f'{rest[0]} {field}: {cell}'); return 0
    if cmd == 'sync':
        print(f'attempts: {sync(rows)} cells filled'); save(rows); return 0
    if cmd == 'render':
        render(rows); print(f'wrote {MD.relative_to(REPO)} ({len(rows)} attempts)'); return 0
    if cmd in ('check', 'refresh'):
        if cmd == 'refresh':
            n = sync(rows); save(rows); rows = load(); render(rows)
            print(f'attempts: {n} cells filled; wrote {MD.relative_to(REPO)} ({len(rows)} attempts)')
        miss = missing(rows)
        if miss:
            print(f'!! attempts without a row: {" ".join(miss)}'); return 1
        print('attempts: every package has a row'); return 0
    raise SystemExit(f'attempts: unknown command {cmd!r}')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
