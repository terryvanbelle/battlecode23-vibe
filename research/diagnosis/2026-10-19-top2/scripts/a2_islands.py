"""a2_islands: island timing per game from timeline.csv (10-round samples): first round each team holds 1 and 2+
islands, islands held at the split round (a2_overview), mean islands held per window, anchors placed per window, and
the island-rounds each team held before the split. Usage: python3 -I a2_islands.py"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
from a2_overview import split_round
WIN = [(0, 300), (300, 600), (600, 1000), (1000, 2001)]


def first(tl, f, v):
    for r in sorted(tl):
        if tl[r][f] >= v:
            return r
    return None


def main():
    print('game | k | N(need) | split | first 1 isl us/them | first 2+ us/them | isl at split us/them | isl-rounds before split us/them | '
          'mean isl per window us/them | anchors placed per window us/them')
    pool = collections.defaultdict(list)
    for m, g, k in A.ALL:
        d = A.G(m, g)
        t = A.timeline(m, g)
        u, th = t['us'], t['them']
        sr = split_round(u, th, d['won'])
        need = (3 * d['nisl'] + 3) // 4
        a, b = A.at(u, sr), A.at(th, sr)
        irb_u = sum(u[r]['islands'] * 10 for r in u if r <= sr)
        irb_t = sum(th[r]['islands'] * 10 for r in th if r <= sr)
        mw = []; aw = []
        for lo, hi in WIN:
            rs = [r for r in u if lo < r <= min(hi, d['rounds'])]
            if not rs:
                continue
            mw.append(f"{sum(u[r]['islands'] for r in rs) / len(rs):.1f}/{sum(th[r]['islands'] for r in rs if r in th) / len(rs):.1f}")
            u0, u1 = A.at(u, lo) if lo else None, A.at(u, min(hi, d['rounds']))
            t0, t1 = A.at(th, lo) if lo else None, A.at(th, min(hi, d['rounds']))
            aw.append(f"{u1['anchors_placed'] - (u0['anchors_placed'] if u0 else 0)}/{t1['anchors_placed'] - (t0['anchors_placed'] if t0 else 0)}")
        print(f"{A.label(m, g)} | {k} | {d['nisl']}({need}) | {sr} | {first(u, 'islands', 1)}/{first(th, 'islands', 1)} | "
              f"{first(u, 'islands', 2)}/{first(th, 'islands', 2)} | {a['islands']}/{b['islands']} | {irb_u}/{irb_t} | {' '.join(mw)} | {' '.join(aw)}")
        pool[k != 'W'].append((first(u, 'islands', 1), first(th, 'islands', 1), sr))
    for lost, P in pool.items():
        print(('losses' if lost else 'wins') + f": median first island us {A.med([p[0] for p in P])} (none in {sum(p[0] is None for p in P)}), "
              f"them {A.med([p[1] for p in P])} (none in {sum(p[1] is None for p in P)}); "
              f"their first island before the split in {sum(1 for p in P if p[1] is not None and p[1] <= p[2])}/{len(P)}")


if __name__ == '__main__':
    main()
