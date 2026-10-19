"""a3_arrive.py: map geometry vs decisions. For each side, its 'worked' Mn wells = the Mn wells of its trips that started by
r60 (trips.csv). Arrival = first round an enemy launcher stands within r2 20 of a worked well (enemy sa_L, rounds < 300).
Geometry = walk moves from the nearest enemy HQ to that well (map BFS, walls only; launchers move 1 tile per 2 rounds,
RULES: move cooldown 20). Per game: our wells' arrival vs theirs, the walk, our carrier deaths by r100, Mn gap at r100.
Usage: python3 -I a3_arrive.py
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *


def worked(G, side):
    c = collections.Counter()
    for t in trips(G, side):
        if t['well_type'] == '2' and int(t['t0']) <= 60 and t['first_collect']:
            c[(int(t['well_x']), int(t['well_y']))] += int(t['collects'] or 0)
    return c


def arrival(G, side):
    """first round an enemy launcher is within r2 20 of one of side's worked Mn wells (the main one: most collects)"""
    w = worked(G, side)
    if not w: return None, None, None
    main = w.most_common(1)[0][0]
    enemy = G['them'] if side == G['us'] else G['us']
    first = None
    for r in sa(G['m'], G['g'], enemy, 'L', 300):
        if d2((r['x'], r['y']), main) <= 20:
            first = r['round']; break
    wk = min(walk(G['map'], h, main) for h in G['hqs'][enemy])
    return main, first, wk


def main():
    print('| match g | map | W/L | our main Mn well | enemy walk to it | enemy launcher arrives | their main Mn well | our walk to it | our launcher arrives | our C lost r100 | their C lost r100 | Mn gap r100 |')
    print('|' + '---|' * 12)
    rows = []
    for G in games():
        a = arrival(G, G['us']); b = arrival(G, G['them'])
        tlu = timeline(G, G['us']); tlt = timeline(G, G['them'])
        gap = int(tlu[100]['coll_Mn']) - int(tlt[100]['coll_Mn']) if 100 in tlu and 100 in tlt else None
        cu = sum(1 for d in deaths(G, G['us']) if d['type'] == 'C' and int(d['round']) <= 100)
        ct = sum(1 for d in deaths(G, G['them']) if d['type'] == 'C' and int(d['round']) <= 100)
        print(f"| {G['m']} g{G['g']} | {G['map']} | {'W' if G['won'] else 'L'} | {a[0]} | {a[2]} | {a[1]} | {b[0]} | {b[2]} | {b[1]} | {cu} | {ct} | {gap} |")
        if not G['dup']: rows.append((G, a, b, cu, ct, gap))
    print('\ndistinct games: arrival on our main Mn well (enemy) vs on theirs (ours); None = no arrival before r300')
    for res in ('L', 'W'):
        rs = [r for r in rows if (r[0]['won'] == 1) == (res == 'W')]
        ea = [r[1][1] for r in rs]; oa = [r[2][1] for r in rs]
        earlier = sum(1 for r in rs if r[1][1] is not None and (r[2][1] is None or r[1][1] < r[2][1]))
        print(f"  {res} n={len(rs)}: enemy arrives on our well median r{med([x for x in ea if x is not None])} "
              f"(none {sum(1 for x in ea if x is None)}), we arrive on theirs median r{med([x for x in oa if x is not None])} "
              f"(none {sum(1 for x in oa if x is None)}); they arrive first in {earlier}/{len(rs)}; enemy walk to our well median "
              f"{med([r[1][2] for r in rs if r[1][2] is not None])}, ours to theirs {med([r[2][2] for r in rs if r[2][2] is not None])}")
    # early arrival vs carrier deaths
    for lo, hi in ((0, 40), (41, 80), (81, 300)):
        rs = [r for r in rows if r[1][1] is not None and lo <= r[1][1] <= hi]
        if rs:
            print(f"  enemy arrival r{lo}-{hi}: n={len(rs)} W-L {sum(r[0]['won'] for r in rs)}-{sum(1-r[0]['won'] for r in rs)} our C lost r100 "
                  f"{sum(r[3] for r in rs)} (mean {mean([r[3] for r in rs]):.1f}), median Mn gap r100 {med([r[5] for r in rs])}")
    rs = [r for r in rows if r[1][1] is None]
    if rs:
        print(f"  no enemy arrival < r300: n={len(rs)} W-L {sum(r[0]['won'] for r in rs)}-{sum(1-r[0]['won'] for r in rs)} our C lost r100 {sum(r[3] for r in rs)}")


if __name__ == '__main__':
    main()
