"""Analyst 1 (carlguo866 early collapses): shared loaders over matches/<id>/extract/*.csv."""
import csv, os, collections
R = '/home/terryvanbelle/projects/vibe/2023/matches'
CARL = [9888, 9900, 9912, 9914, 9915, 9921, 9925, 9929, 9931, 10060]
SUB = {9888: 189, 9900: 191}
# early collapses named in the task (L@250 = 0 for us); 9921 g0 duplicates 9888 g0
COLLAPSE = [(9888, 0), (9921, 0), (9888, 2), (9900, 0), (9915, 1), (9915, 2), (9929, 2), (9931, 0), (9931, 2)]
# early wins named in the task
EARLYWIN = [(9912, 0), (9914, 1), (9900, 2), (9921, 2), (9925, 2), (9925, 0), (9900, 1)]
US = 'vibe23'


def rows(m, f):
    p = os.path.join(R, str(m), 'extract', f + '.csv')
    with open(p) as fh:
        return list(csv.DictReader(fh))


def games(m):
    g = {}
    for r in rows(m, 'games'):
        k = int(r['game'])
        d = g.setdefault(k, {'match': m, 'game': k, 'map': r['map'], 'w': int(r['width']), 'h': int(r['height']),
                             'nisl': int(r['islands']), 'rounds': int(r['rounds']), 'sym': r['symmetry']})
        if r['team'] == US:
            d['us'] = r['side']; d['won'] = int(r['won']); d['reason'] = r['win_reason']
        else:
            d['them'] = r['side']; d['opp'] = r['team']
    return g


def census(m):
    out = {}
    for r in rows(m, 'census'):
        out[(int(r['game']), r['side'])] = r
    return out


def f(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def med(v):
    v = sorted(v)
    n = len(v)
    if n == 0:
        return float('nan')
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
