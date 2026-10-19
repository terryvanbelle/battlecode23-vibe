"""a2_econ: economy and production by phase window from timeline.csv (10-round samples), us vs them.
Per window: Mn and Ad collected, Ad share of collection, launchers / carriers / amplifiers built, mean carriers and
launchers alive, mean bank Mn+Ad (all HQs), launcher deaths (deaths.csv). Pooled medians over losses and wins, and
per game with --per-game. Usage: python3 -I a2_econ.py [--per-game]"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
WIN = [(0, 300), (300, 600), (600, 1000), (1000, 2001)]


def window(tl, a, b, end):
    b = min(b, end)
    if a >= end:
        return None
    r0, r1 = A.at(tl, a) or {k: 0 for k in tl[min(tl)]}, A.at(tl, b)
    if a == 0:
        r0 = {k: 0 for k in r1}
    rs = [r for r in tl if a < r <= b]
    o = {}
    for f in ('coll_Mn', 'coll_Ad', 'built_L', 'built_C', 'built_A'):
        o[f] = r1[f] - r0[f]
    tot = o['coll_Mn'] + o['coll_Ad']
    o['ad_share'] = o['coll_Ad'] / tot if tot else float('nan')
    for f in ('alive_C', 'alive_L', 'alive_A'):
        o[f] = sum(tl[r][f] for r in rs) / len(rs) if rs else 0
    o['bank'] = sum(tl[r]['bank_Mn'] + tl[r]['bank_Ad'] for r in rs) / len(rs) if rs else 0
    o['bank_Ad'] = sum(tl[r]['bank_Ad'] for r in rs) / len(rs) if rs else 0
    return o


def main():
    pg = '--per-game' in sys.argv
    pool = collections.defaultdict(list)
    for m, g, k in A.ALL:
        d = A.G(m, g)
        t = A.timeline(m, g)
        if pg:
            print(f"== {A.label(m, g)} ({k}, {d['rounds']})")
        for a, b in WIN:
            u, th = window(t['us'], a, b, d['rounds']), window(t['them'], a, b, d['rounds'])
            if u is None:
                continue
            w = f'{a}-{min(b, 2001) - 1}'
            if pg:
                print(f"  {w}: Mn {u['coll_Mn']}/{th['coll_Mn']} Ad {u['coll_Ad']}/{th['coll_Ad']} Ad share {u['ad_share']:.2f}/{th['ad_share']:.2f} "
                      f"| built L {u['built_L']}/{th['built_L']} C {u['built_C']}/{th['built_C']} A {u['built_A']}/{th['built_A']} "
                      f"| alive C {u['alive_C']:.1f}/{th['alive_C']:.1f} L {u['alive_L']:.1f}/{th['alive_L']:.1f} A {u['alive_A']:.1f}/{th['alive_A']:.1f} "
                      f"| bank {u['bank']:.0f}/{th['bank']:.0f} (Ad {u['bank_Ad']:.0f}/{th['bank_Ad']:.0f})")
            kk = 'L' if k != 'W' else 'W'
            # normalise to per-100-round rates so windows of different length pool
            span = (min(b, d['rounds'] + 1) - a) / 100
            pool[(kk, w)].append((u, th, span))
    for kk in ('L', 'W'):
        print(f"== median over {'losses' if kk == 'L' else 'wins'} (per 100 rounds for flows)")
        for a, b in WIN:
            w = f'{a}-{min(b, 2001) - 1}'
            P = pool.get((kk, w))
            if not P:
                continue
            def mm(f, who, rate=True):
                return A.med([(x[who][f] / x[2]) if rate else x[who][f] for x in P])
            print(f"  {w} (n={len(P)}): Mn/100r {mm('coll_Mn', 0):.0f}/{mm('coll_Mn', 1):.0f} Ad/100r {mm('coll_Ad', 0):.0f}/{mm('coll_Ad', 1):.0f} "
                  f"Ad share {mm('ad_share', 0, False):.2f}/{mm('ad_share', 1, False):.2f} | built L/100r {mm('built_L', 0):.1f}/{mm('built_L', 1):.1f} "
                  f"C/100r {mm('built_C', 0):.1f}/{mm('built_C', 1):.1f} A {mm('built_A', 0, False)}/{mm('built_A', 1, False)} | alive C {mm('alive_C', 0, False):.1f}/{mm('alive_C', 1, False):.1f} "
                  f"L {mm('alive_L', 0, False):.1f}/{mm('alive_L', 1, False):.1f} | bank {mm('bank', 0, False):.0f}/{mm('bank', 1, False):.0f} Ad {mm('bank_Ad', 0, False):.0f}/{mm('bank_Ad', 1, False):.0f}")


if __name__ == '__main__':
    main()
