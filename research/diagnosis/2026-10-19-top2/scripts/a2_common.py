"""Analyst 2 (long and late games vs carlguo866 and maxwelljones14): shared loaders over matches/<id>/extract/*.csv.
Run every a2_*.py with python3 -I from any directory. Per-turn dumps (--sa) are read from the other analysts' dump dirs
in the session scratchpad (A2_SA_* env vars override): carl matches a1/sa/<match><side>/ (all games of the match in one
file), maxwell games a0/sa/<match>g<game><side>/, and our own a2/sa/<match>g<game><side>/ for anything missing."""
import csv, os, collections, functools
REPO = '/home/terryvanbelle/projects/vibe/2023'
R = REPO + '/matches'
SP = '/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/top2'
SA_CARL = os.environ.get('A2_SA_CARL', SP + '/a1/sa')
SA_MAX = os.environ.get('A2_SA_MAX', SP + '/a0/sa')
SA_OWN = os.environ.get('A2_SA_OWN', SP + '/a2/sa')
US = 'vibe23'
CARL = 'carlguo866.submit26_final'
MAX = 'maxwelljones14.MPWorking'
# (match, game, label): the task's long/late losses and long wins
LOSS_C = [(9912, 1), (9912, 2), (9914, 0), (9914, 2), (9915, 0), (9929, 1), (9931, 1), (10060, 0), (10060, 1), (9888, 1)]
LOSS_M = [(9911, 2), (9924, 2), (9928, 0), (9930, 2), (9924, 0)]
WINS = [(9921, 1), (9925, 1), (9929, 0), (10060, 2)]
ALL = [(m, g, 'Lc') for m, g in LOSS_C] + [(m, g, 'Lm') for m, g in LOSS_M] + [(m, g, 'W') for m, g in WINS]


def rows(m, f):
    with open(os.path.join(R, str(m), 'extract', f + '.csv')) as fh:
        return list(csv.DictReader(fh))


@functools.lru_cache(None)
def games(m):
    g = {}
    for r in rows(m, 'games'):
        k = int(r['game'])
        d = g.setdefault(k, {'m': m, 'g': k, 'map': r['map'], 'W': int(r['width']), 'H': int(r['height']),
                             'nisl': int(r['islands']), 'rounds': int(r['rounds']), 'sym': r['symmetry']})
        if r['team'] == US:
            d['us'] = r['side']; d['won'] = int(r['won']); d['reason'] = r['win_reason']
        else:
            d['them'] = r['side']; d['opp'] = r['team']
    return g


def G(m, g):
    return games(m)[g]


def label(m, g):
    d = G(m, g)
    return f"{m} g{g} {d['map']}"


def opp_short(m, g):
    return 'carl' if G(m, g)['opp'] == CARL else 'max'


@functools.lru_cache(None)
def _tl(m):
    out = collections.defaultdict(dict)
    for r in rows(m, 'timeline'):
        out[(int(r['game']), r['side'])][int(r['round'])] = {k: num(v) for k, v in r.items() if k not in ('side',)}
    return out


def timeline(m, g):
    """{'us': {round: row}, 'them': {round: row}} (every 10 rounds; numeric values)."""
    d = G(m, g)
    t = _tl(m)
    return {'us': t[(g, d['us'])], 'them': t[(g, d['them'])]}


@functools.lru_cache(None)
def _census(m):
    return {(int(r['game']), r['side']): r for r in rows(m, 'census')}


def census(m, g):
    d = G(m, g)
    c = _census(m)
    return c[(g, d['us'])], c[(g, d['them'])]


def at(tl, r):
    """the timeline row at round r, or the last one before it"""
    ks = [k for k in tl if k <= r]
    return tl[max(ks)] if ks else None


def num(x, d=None):
    if x is None or x == '':
        return d
    try:
        v = float(x)
        return int(v) if v == int(v) else v
    except ValueError:
        return x


def med(v):
    v = sorted(x for x in v if x is not None)
    n = len(v)
    if n == 0:
        return float('nan')
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def sa_path(m, g, side, kind):
    """per-turn dump file and whether it holds every game of the match (filter on column game)"""
    p = f'{SA_MAX}/{m}g{g}{side}/sa_{kind}.csv'
    if os.path.exists(p):
        return p, False
    p = f'{SA_OWN}/{m}g{g}{side}/sa_{kind}.csv'
    if os.path.exists(p):
        return p, False
    p = f'{SA_CARL}/{m}{side}/sa_{kind}.csv'
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return p, True
    return None, False


def sa_iter(m, g, side, kind, cols=None):
    """yield per-turn rows (dicts of str) of one team, one game; cols limits the keys kept"""
    p, multi = sa_path(m, g, side, kind)
    if p is None:
        return
    gs = str(g)
    with open(p) as fh:
        rd = csv.reader(fh)
        hdr = next(rd)
        ig = hdr.index('game')
        idx = [(c, hdr.index(c)) for c in (cols or hdr)]
        for row in rd:
            if multi and row[ig] != gs:
                continue
            yield {c: row[i] for c, i in idx}
