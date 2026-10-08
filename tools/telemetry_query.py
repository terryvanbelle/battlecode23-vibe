#!/usr/bin/env python3
"""Aggregate answers across reported matches (docs/TELEMETRY.md C.5). Reads progress/telemetry.jsonl (written by
tools/match_report.py), keeping the last line per match. Standard library only.

    tools/telemetry_query.py <question> [--since YYYY-MM-DD | --last N] [--opponent NAME] [--submission ID] [--map M]
                             [--ranked | --unranked] [--by opponent|map|submission|phase] [--csv] [--deep] [--file F]

Questions (information need from TELEMETRY.md §6 in brackets):
  econ       why our mana arrives late [1]: Mn and Ad collected at r50/100/250, carriers, carrier letter shares (by
             phase with --by phase), Mn-role share, trips (dots) and replay trip cycles (Tier 2)
  fights     why we lose launcher fights [2]: engagements, win share, exchange, first hit; the dN table (pooled win
             rate by our launchers minus theirs at the start, -3..+3, us vs opponents at the same dN); our launcher
             modes inside engagements; outnumbered share at contact; kite classes; FIGHT dots
  hq         what the HQ waited for [3]: reason shares (by phase with --by phase), idle funds, float anomalies, pressure
  opening    opening timeline [4]: C and L alive at r50/100/150, launchers among the first 12 builds, onsets
  deaths     our deaths [7]: by cause and type, value lost, spawn kills, cargo lost
  turning    earliest predictive round: turn and lock round distributions; how often the leader at R in L, Mn,
             army value and islands wins (R in 50..500 step 50; with --deep from matches/<id>/extract/timeline.csv,
             otherwise from the JSON's r50/100/150/250/500 samples)
  basics     basics bar on replica games [11, 14]: overruns, near misses, exception turns, BCC agreement and
             telemetry presence (grouped by submission unless --by says otherwise)
  losses     every loss with its report and the largest us-minus-them shortfall among Mn@100, L@250, engagement win
             share and value lost (relative: (us - them) / max(|us|, |them|, 1); value lost counts reversed)
  anomalies  anomalies by kind, then every game that has one
  field      Tier 2 (progress/field.jsonl), not built yet
Rows give, per group (text: mean +-SE nN): n games (or engagements for pooled rates), mean and standard error for us and for them, and the
paired difference us - them over games where both exist. --csv prints the same rows as CSV."""
import argparse, csv, json, math, os, statistics, sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.environ.get('MATCH_REPORT_ROOT') or REPO
CAUSES = ('launcher', 'throw', 'destab', 'hq_aura', 'self', 'resign')
KITE = ('stand_fire', 'fire_retreat', 'stepin_fire', 'fire_ambiguous', 'advance', 'retreat', 'hold')
PHASES = ('open', 'mid', 'late')
COLS = ['group', 'metric', 'unit', 'n_us', 'us', 'us_se', 'n_them', 'them', 'them_se', 'n_diff', 'diff', 'diff_se']


# ---------------------------------------------------------------- loading and selection
def load(path):
    """{match: last line} (a --force or --shadow line supersedes the earlier ones)."""
    out = {}
    if os.path.exists(path):
        with open(path) as fh:
            lines = fh.read().splitlines()
        for l in lines:
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if isinstance(d, dict) and 'match' in d:
                out[d['match']] = d
    return out


def select(lines, a):
    ms = list(lines.values())
    if a.opponent:
        ms = [m for m in ms if m.get('opponent') == a.opponent]
    if a.submission is not None:
        ms = [m for m in ms if str(m.get('submission')) == str(a.submission)]
    if a.ranked:
        ms = [m for m in ms if m.get('ranked') is True]
    if a.unranked:
        ms = [m for m in ms if m.get('ranked') is False]
    if a.since:
        ms = [m for m in ms if (m.get('created') or m.get('reported_at') or '')[:10] >= a.since]
    ms.sort(key=lambda m: (m.get('created') or m.get('reported_at') or '', m['match']))
    if a.last:
        ms = ms[-a.last:]
    return ms, [(m, G) for m in ms for G in m.get('games') or [] if not a.map or G.get('map') == a.map]


def groups(games, by):
    key = {'opponent': lambda m, G: str(m.get('opponent')), 'map': lambda m, G: str(G.get('map')),
           'submission': lambda m, G: str(m.get('submission'))}.get(by)
    if key is None:
        return {'all': games}
    out = defaultdict(list)
    for m, G in games:
        out[key(m, G)].append((m, G))
    return dict(sorted(out.items()))


# ---------------------------------------------------------------- statistics
def ok(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def stat(xs):
    xs = [float(x) for x in xs if ok(x)]
    if not xs:
        return 0, None, None
    m = sum(xs) / len(xs)
    se = statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else None
    return len(xs), m, se


def row(group, metric, us, them=None, unit='game'):
    """A per-game row: us and them are lists aligned by game (None = missing)."""
    n1, m1, s1 = stat(us)
    r = {'group': group, 'metric': metric, 'unit': unit, 'n_us': n1, 'us': m1, 'us_se': s1,
         'n_them': 0, 'them': None, 'them_se': None, 'n_diff': 0, 'diff': None, 'diff_se': None}
    if them is not None:
        r['n_them'], r['them'], r['them_se'] = stat(them)
        r['n_diff'], r['diff'], r['diff_se'] = stat([a - b for a, b in zip(us, them) if ok(a) and ok(b)])
    return r


def pooled(group, metric, us_nw, them_nw=None, unit='eng'):
    """A pooled rate: (n, won) summed over games; SE = sqrt(p (1 - p) / n)."""
    def one(nw):
        n, w = nw
        if not n:
            return 0, None, None
        p = w / n
        return n, p, math.sqrt(p * (1 - p) / n)
    r = {'group': group, 'metric': metric, 'unit': unit}
    r['n_us'], r['us'], r['us_se'] = one(us_nw)
    r['n_them'], r['them'], r['them_se'] = one(them_nw) if them_nw else (0, None, None)
    if r['us'] is not None and r['them'] is not None:
        r['n_diff'], r['diff'], r['diff_se'] = min(r['n_us'], r['n_them']), r['us'] - r['them'], \
            math.sqrt(r['us_se'] ** 2 + r['them_se'] ** 2)
    else:
        r['n_diff'], r['diff'], r['diff_se'] = 0, None, None
    return r


# ---------------------------------------------------------------- accessors
def g(d, *path):
    for k in path:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def at(G, side, R, k):
    return g(G, side, 'at', str(R), k)


def won_share(G, side):
    n, w = g(G, side, 'eng', 'n'), g(G, side, 'eng', 'won')
    return w / n if ok(n) and n > 0 and ok(w) else None


def builds(G, side):
    """(launchers among the first 12 builds, round of the 12th build) from first_builds 'r:T r:T ...'."""
    fb = g(G, side, 'first_builds')
    if not fb:
        return None, None
    items = [t.split(':', 1) for t in fb.split() if ':' in t]
    L = sum(1 for r, t in items[:12] if t == 'L')
    r12 = int(items[11][0]) if len(items) >= 12 and items[11][0].isdigit() else None
    return L, r12


def eng_modes(G):
    codes = g(G, 'tele', 'eng_codes') or {}
    tot = sum(v for v in codes.values() if ok(v))
    if not tot:
        return {}, None
    by = Counter()
    for k, v in codes.items():
        by[k[:1]] += v
    return {l: v / tot for l, v in by.items()}, sum(v for k, v in codes.items() if k.endswith('o')) / tot


def has_tele(G):
    return g(G, 'tele', 'status') not in (None, 'none')


def share_of(G, path, letter):
    d = g(G, *path)
    if not has_tele(G) or not isinstance(d, dict) or not d:
        return None
    return d.get(letter, 0.0)


# ---------------------------------------------------------------- questions
def per_game(gs, metrics):
    out = []
    for name, games in gs.items():
        for metric, fu, ft in metrics:
            us = [fu(G) for m, G in games]
            them = [ft(G) for m, G in games] if ft else None
            out.append(row(name, metric, us, them))
    return out


def both(f):
    return (lambda G: f(G, 'us')), (lambda G: f(G, 'them'))


def letters(games, path):
    s = set()
    for m, G in games:
        d = g(G, *path)
        if isinstance(d, dict) and has_tele(G):
            s |= set(d)
    return sorted(s)


def state_rows(gs, by, typ, prefix):
    """Letter shares of one unit type (us): overall, or per phase (group = phase) with --by phase."""
    out = []
    for name, games in gs.items():
        if by == 'phase':
            for p in PHASES:
                for l in letters(games, ('tele', 'states_by_phase', p, typ)):
                    out.append(row(p, f'{prefix}{l}', [share_of(G, ('tele', 'states_by_phase', p, typ), l)
                                                       for m, G in games]))
        else:
            for l in letters(games, ('tele', 'states', typ)):
                out.append(row(name, f'{prefix}{l}', [share_of(G, ('tele', 'states', typ), l) for m, G in games]))
    return out


def q_econ(gs, a):
    M = []
    for k in ('Mn', 'Ad'):
        for R in (50, 100, 250):
            M.append((f'{k}@{R} collected', *both(lambda G, s, R=R, k=k: at(G, s, R, k))))
    M += [('C alive@100', *both(lambda G, s: at(G, s, 100, 'C'))),
          ('C built', *both(lambda G, s: g(G, s, 'built', 'C'))),
          ('Mn-role share (tele)', lambda G: g(G, 'tele', 'carrier_mn'), None),
          ('trips (dots)', lambda G: g(G, 'tele', 'trip', 'n'), None),
          ('trip cycle p50 (dots)', lambda G: g(G, 'tele', 'trip', 'cycle_p50'), None),
          ('wait/trip (dots)', lambda G: g(G, 'tele', 'trip', 'wait_mean'), None),
          ('explore/trip (dots)', lambda G: g(G, 'tele', 'trip', 'explore_mean'), None),
          ('trip cycle p50 (replay)', *both(lambda G, s: g(G, s, 'tier2', 'trip_cycle_p50'))),
          ('partial loads (replay)', *both(lambda G, s: g(G, s, 'tier2', 'partial_loads'))),
          ('carriers per well (replay)', *both(lambda G, s: g(G, s, 'tier2', 'carriers_per_well')))]
    return per_game(gs, M) + state_rows(gs, a.by, 'C', 'carrier ')


def q_fights(gs, a):
    M = [('engagements', *both(lambda G, s: g(G, s, 'eng', 'n'))),
         ('eng won share', *both(won_share)),
         ('exchange ratio', *both(lambda G, s: g(G, s, 'eng', 'exch'))),
         ('first-hit rate', *both(lambda G, s: g(G, s, 'eng', 'first_hit'))),
         ('outnumbered at contact (tele)', lambda G: eng_modes(G)[1], None),
         ('F/H turns outnumbered (tele)', lambda G: g(G, 'tele', 'launcher_out'), None),
         ('FIGHT riskier than stay (dots)', lambda G: g(G, 'tele', 'fight', 'riskier_than_stay'), None),
         ('FIGHT step-in outnumbered (dots)', lambda G: g(G, 'tele', 'fight', 'stepin_outnumbered'), None)]
    M += [(f'kite {k}', *both(lambda G, s, k=k: g(G, s, 'kite', k))) for k in KITE]
    out = per_game(gs, M)
    for name, games in gs.items():
        for k in range(-3, 4):
            nw = lambda s: [sum(x) for x in zip(*([g(G, s, 'eng', 'by_dn', str(k)) or [0, 0] for m, G in games]
                                                  or [[0, 0]]))]
            out.append(pooled(name, f'win@dN={k:+d}', nw('us'), nw('them')))
        ls = sorted({l for m, G in games for l in eng_modes(G)[0]})
        for l in ls:
            out.append(row(name, f'mode {l} in engagements (tele)',
                           [eng_modes(G)[0].get(l, 0.0) if eng_modes(G)[0] else None for m, G in games]))
    return out


def q_hq(gs, a):
    M = [('idle funds (HQ-rounds)', *both(lambda G, s: g(G, s, 'idle_funds'))),
         ('bank Mn when idle p50', *both(lambda G, s: g(G, s, 'idle_bank_Mn_p50'))),
         ('float anomalies', lambda G: sum(1 for x in G.get('anomalies') or [] if x.startswith('float:')), None),
         ('enemy pressure r2<=9', *both(lambda G, s: g(G, s, 'pressure9')))]
    return per_game(gs, M) + state_rows(gs, a.by, 'HQ', 'HQ ')


def q_opening(gs, a):
    M = []
    for k in ('C', 'L'):
        for R in (50, 100, 150):
            M.append((f'{k} alive@{R}', *both(lambda G, s, R=R, k=k: at(G, s, R, k))))
    M += [('L in first 12 builds', *both(lambda G, s: builds(G, s)[0])),
          ('round of 12th build', *both(lambda G, s: builds(G, s)[1])),
          ('turn round (game)', lambda G: G.get('turn_round'), None),
          ('lock round (game)', lambda G: G.get('lock_round'), None)]
    M += [(f'onset {k} (game)', lambda G, k=k: g(G, 'onset', k), None) for k in ('L', 'Mn', 'value', 'islands')]
    return per_game(gs, M)


def q_deaths(gs, a):
    M = [(f'deaths {c}', *both(lambda G, s, c=c: g(G, s, 'deaths_by_cause', c))) for c in CAUSES]
    M += [(f'died {t}', *both(lambda G, s, t=t: g(G, s, 'died', t))) for t in 'CLA']
    M += [('value lost', *both(lambda G, s: g(G, s, 'value_lost'))),
          ('spawn kills', *both(lambda G, s: g(G, s, 'spawn_kills'))),
          ('cargo lost Mn', *both(lambda G, s: g(G, s, 'cargo_lost_Mn'))),
          ('anchors lost', *both(lambda G, s: g(G, s, 'anchors_lost')))]
    return per_game(gs, M)


def q_basics(gs, a):
    M = [('overruns', lambda G: g(G, 'us', 'overruns'), None),
         ('near misses', lambda G: g(G, 'us', 'near'), None),
         ('exception turns (tele)', lambda G: g(G, 'tele', 'exc_turns'), None),
         ('self deaths', lambda G: g(G, 'us', 'deaths_by_cause', 'self'), None),
         ('BCC agreement', lambda G: g(G, 'tele', 'agree'), None),
         ('telemetry present', lambda G: 1.0 if has_tele(G) else 0.0, None),
         ('anomalies', lambda G: len(G.get('anomalies') or []), None)]
    return per_game(gs, M)


def timeline_at(m, G, R, deep_cache):
    """{side: row} at round R from the match's extract timeline.csv (None when absent)."""
    ext = m.get('extract')
    if not ext:
        return None
    p = ext if os.path.isabs(ext) else os.path.join(ROOT, ext)
    p = os.path.join(p, 'timeline.csv')
    if p not in deep_cache:
        rows = defaultdict(dict)
        if os.path.exists(p):
            with open(p, newline='') as fh:
                for r in csv.DictReader(fh):
                    rows[(r.get('game'), r.get('round'))][r.get('side')] = r
        deep_cache[p] = rows
    return deep_cache[p].get((str(G.get('game')), str(R)))


def q_turning(gs, a):
    out = []
    TL = {'L': 'alive_L', 'Mn': 'coll_Mn', 'value': 'army_value', 'islands': 'islands'}
    AT = {'L': 'L', 'Mn': 'Mn', 'value': 'value', 'islands': 'islands'}
    cache = {}
    for name, games in gs.items():
        for k in ('turn_round', 'lock_round'):
            xs = [G.get(k) for m, G in games]
            out.append(row(name, k, xs))
            vals = [x for x in xs if ok(x)]
            for q, lab in ((0.25, 'p25'), (0.5, 'p50'), (0.75, 'p75')):
                v = sorted(vals)[min(len(vals) - 1, max(0, math.ceil(q * len(vals)) - 1))] if vals else None
                out.append({'group': name, 'metric': f'{k} {lab}', 'unit': 'game', 'n_us': len(vals), 'us': v,
                            'us_se': None, 'n_them': 0, 'them': None, 'them_se': None, 'n_diff': 0, 'diff': None,
                            'diff_se': None})
            out.append(row(name, f'{k} never', [0.0 if ok(x) else 1.0 for x in xs]))
        for R in range(50, 501, 50):
            for M in ('L', 'Mn', 'value', 'islands'):
                n = w = 0
                for m, G in games:
                    if G.get('result') not in ('win', 'loss'):
                        continue
                    if a.deep:
                        t = timeline_at(m, G, R, cache)
                        us_side = G.get('side')
                        th_side = 'B' if us_side == 'A' else 'A'
                        u = _num(t[us_side].get(TL[M])) if t and us_side in t else None
                        v = _num(t[th_side].get(TL[M])) if t and th_side in t else None
                    else:
                        u, v = at(G, 'us', R, AT[M]), at(G, 'them', R, AT[M])
                    if not ok(u) or not ok(v) or u == v:
                        continue
                    n += 1
                    w += 1 if (u > v) == (G['result'] == 'win') else 0
                if n:
                    out.append(pooled(name, f'leader@{R} by {M} wins', (n, w), unit='game'))
    return out


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def rel_delta(u, t):
    if not ok(u) or not ok(t):
        return None
    return (u - t) / max(abs(u), abs(t), 1)


def q_losses(ms, games, a):
    out = []
    for m, G in games:
        if G.get('result') != 'loss':
            continue
        cands = [('Mn@100', at(G, 'us', 100, 'Mn'), at(G, 'them', 100, 'Mn'), 1),
                 ('L@250', at(G, 'us', 250, 'L'), at(G, 'them', 250, 'L'), 1),
                 ('eng won share', won_share(G, 'us'), won_share(G, 'them'), 1),
                 ('value lost', g(G, 'us', 'value_lost'), g(G, 'them', 'value_lost'), -1)]
        scored = [(rel_delta(u, t) * sgn, k, u, t) for k, u, t, sgn in cands if rel_delta(u, t) is not None]
        worst = min(scored, default=None)
        out.append({'match': m['match'], 'game': G.get('game'), 'map': G.get('map'), 'opponent': m.get('opponent'),
                    'rounds': G.get('rounds'), 'win_reason': G.get('win_reason'),
                    'worst': worst[1] if worst else '', 'worst_us': worst[2] if worst else '',
                    'worst_them': worst[3] if worst else '', 'worst_rel': round(worst[0], 3) if worst else '',
                    'report': m.get('report')})
    return out


def q_anomalies(ms, games, a):
    out = []
    for m, G in games:
        for x in G.get('anomalies') or []:
            out.append({'match': m['match'], 'game': G.get('game'), 'map': G.get('map'),
                        'opponent': m.get('opponent'), 'kind': x.split(':', 1)[0], 'anomaly': x})
    return out


# ---------------------------------------------------------------- output
def f(x, se=False):
    if x is None:
        return '-'
    if abs(x) >= 100:
        return f'{x:.0f}'
    if abs(x) >= 10:
        return f'{x:.1f}'
    return f'{x:.3f}'


def cell(r, k):
    if r[k] is None:
        return '-'
    s = (f'{r[k]:+.3f}' if abs(r[k]) < 10 else f'{r[k]:+.1f}') if k == 'diff' else f(r[k])
    return f"{s} +-{f(r[k + '_se'])} n{r['n_' + k]}" if r[k + '_se'] is not None else f"{s} n{r['n_' + k]}"


def print_rows(rows, title, as_csv, out=sys.stdout):
    if as_csv:
        w = csv.DictWriter(out, fieldnames=COLS, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else ('' if v is None else v)) for k, v in r.items()})
        return
    print(title, file=out)
    if not rows:
        print('  (no data)', file=out)
        return
    gw = max(5, max(len(r['group']) for r in rows))
    mw = max(6, max(len(r['metric']) for r in rows))
    print(f"{'group':{gw}s}  {'metric':{mw}s}  {'us':24s}  {'them':24s}  us - them", file=out)
    for r in rows:
        print(f"{r['group']:{gw}s}  {r['metric']:{mw}s}  {cell(r, 'us'):24s}  {cell(r, 'them'):24s}  {cell(r, 'diff')}",
              file=out)


def print_list(rows, cols, title, as_csv, out=sys.stdout):
    if as_csv:
        w = csv.DictWriter(out, fieldnames=cols, lineterminator='\n', extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: ('' if r.get(k) is None else r.get(k)) for k in cols})
        return
    print(title, file=out)
    for r in rows:
        print('  ' + '  '.join(f'{k}={r.get(k)}' for k in cols), file=out)
    if not rows:
        print('  (none)', file=out)


def main(argv=None, out=sys.stdout):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('question', choices=['econ', 'fights', 'hq', 'opening', 'deaths', 'turning', 'basics', 'losses',
                                         'anomalies', 'field'])
    w = ap.add_mutually_exclusive_group()
    w.add_argument('--since')
    w.add_argument('--last', type=int)
    ap.add_argument('--opponent')
    ap.add_argument('--submission')
    ap.add_argument('--map')
    r = ap.add_mutually_exclusive_group()
    r.add_argument('--ranked', action='store_true')
    r.add_argument('--unranked', action='store_true')
    ap.add_argument('--by', choices=['opponent', 'map', 'submission', 'phase'])
    ap.add_argument('--csv', action='store_true')
    ap.add_argument('--deep', action='store_true')
    ap.add_argument('--file', default=os.path.join(ROOT, 'progress', 'telemetry.jsonl'))
    a = ap.parse_args(argv)
    if a.question == 'field':
        print('field: Tier 2 (progress/field.jsonl from match_report.py field), not built yet', file=out)
        return 2
    ms, games = select(load(a.file), a)
    title = (f'{a.question}: {len(games)} games in {len(ms)} matches'
             + ''.join(f' {k}={v}' for k, v in (('opponent', a.opponent), ('submission', a.submission), ('map', a.map),
                                                 ('since', a.since), ('last', a.last)) if v))
    if a.question == 'losses':
        print_list(q_losses(ms, games, a), ['match', 'game', 'map', 'opponent', 'rounds', 'win_reason', 'worst',
                                            'worst_us', 'worst_them', 'worst_rel', 'report'], title, a.csv, out)
        return 0
    if a.question == 'anomalies':
        rows = q_anomalies(ms, games, a)
        if not a.csv:
            kinds = Counter(r['kind'] for r in rows)
            games_k = {k: len({(r['match'], r['game']) for r in rows if r['kind'] == k}) for k in kinds}
            matches_k = {k: len({r['match'] for r in rows if r['kind'] == k}) for k in kinds}
            print(title, file=out)
            for k, n in kinds.most_common():
                print(f'  {k:16s} {n:4d} anomalies in {games_k[k]:3d} games, {matches_k[k]:3d} matches', file=out)
            title = 'by game:'
        print_list(rows, ['match', 'game', 'map', 'opponent', 'kind', 'anomaly'], title, a.csv, out)
        return 0
    by = a.by or ('submission' if a.question == 'basics' else None)
    gs = groups(games, by)
    fn = {'econ': q_econ, 'fights': q_fights, 'hq': q_hq, 'opening': q_opening, 'deaths': q_deaths,
          'turning': q_turning, 'basics': q_basics}[a.question]
    a.by = by
    print_rows(fn(gs, a), title, a.csv, out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
