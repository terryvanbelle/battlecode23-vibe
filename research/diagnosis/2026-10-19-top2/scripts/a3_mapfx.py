"""a3_mapfx.py: map effects vs decision effects on the opening economy, distinct games (47).
Maps are symmetric, so every layout feature (walk HQ -> nearest Mn well, area, HQs) is the same for both sides; a feature
can only matter through how the two bots play it. Strata by walk moves to the nearest Mn well and by area; per stratum:
W/L, median Mn gap us-them at r30/r50/r100, our carriers lost by r100 (deaths.csv), median Ad@100 us/them, and the share
of games with Mn@50 behind. Also the same-map pairs (one map, two outcomes or two opponents).
Usage: python3 -I a3_mapfx.py
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *


def feats(G):
    out = dict(G=G)
    mf = mapfeat(G, G['us'])
    out['walk'] = mf['walk_mn']; out['area'] = mf['area']; out['d2'] = mf['d2_mn']
    for who in ('us', 'them'):
        tl = timeline(G, G[who])
        for r in (30, 50, 100):
            out[f'{who}Mn{r}'] = int(tl[r]['coll_Mn']) if r in tl else None
            out[f'{who}Ad{r}'] = int(tl[r]['coll_Ad']) if r in tl else None
        out[f'{who}Cd'] = sum(1 for d in deaths(G, G[who]) if d['type'] == 'C' and int(d['round']) <= 100)
        out[f'{who}Cd50'] = sum(1 for d in deaths(G, G[who]) if d['type'] == 'C' and int(d['round']) <= 50)
    return out


def summ(rows, lab):
    if not rows: return
    w = sum(1 for r in rows if r['G']['won'])
    def gap(k): return med([r['us' + k] - r['them' + k] for r in rows if r['us' + k] is not None and r['them' + k] is not None])
    behind50 = sum(1 for r in rows if r['usMn50'] < r['themMn50'])
    print(f"| {lab} | {len(rows)} | {w}-{len(rows)-w} | {fmt(gap('Mn30'))} | {fmt(gap('Mn50'))} | {fmt(gap('Mn100'))} | {behind50}/{len(rows)} | "
          f"{sum(r['usCd50'] for r in rows)}/{sum(r['themCd50'] for r in rows)} | {sum(r['usCd'] for r in rows)}/{sum(r['themCd'] for r in rows)} | "
          f"{fmt(med([r['usAd100'] for r in rows]))}/{fmt(med([r['themAd100'] for r in rows]))} |")


def main():
    rows = [feats(G) for G in games() if not G['dup']]
    hdr = ('| stratum | n | W-L | Mn gap r30 (med) | r50 | r100 | Mn@50 behind | C lost r50 us/them | C lost r100 us/them | Ad@100 us/them (med) |')
    print(hdr); print('|' + '---|' * 10)
    for lab, f in (('walk to Mn <= 3', lambda r: r['walk'] <= 3), ('walk 4-6', lambda r: 4 <= r['walk'] <= 6),
                   ('walk 7-9', lambda r: 7 <= r['walk'] <= 9), ('walk >= 10', lambda r: r['walk'] >= 10),
                   ('area <= 900', lambda r: r['area'] <= 900), ('area 901-1800', lambda r: 900 < r['area'] <= 1800),
                   ('area > 1800', lambda r: r['area'] > 1800),
                   ('1 HQ', lambda r: r['G']['nhq'] == 1), ('2 HQs', lambda r: r['G']['nhq'] == 2), ('3-4 HQs', lambda r: r['G']['nhq'] >= 3),
                   ('carl', lambda r: r['G']['opp'] == 'carl'), ('maxwell', lambda r: r['G']['opp'] == 'maxwell'),
                   ('all', lambda r: True)):
        summ([r for r in rows if f(r)], lab)
    print('\nwins vs losses inside strata (walk to Mn): median Mn gap r100 and carriers lost r100 us/them')
    for lab, f in (('walk <= 3', lambda r: r['walk'] <= 3), ('walk 4-6', lambda r: 4 <= r['walk'] <= 6),
                   ('walk 7-9', lambda r: 7 <= r['walk'] <= 9), ('walk >= 10', lambda r: r['walk'] >= 10)):
        for res in (1, 0):
            rs = [r for r in rows if f(r) and r['G']['won'] == res]
            if rs:
                print(f"  {lab:10s} {'W' if res else 'L'} n={len(rs):2d} Mn30 gap {fmt(med([r['usMn30']-r['themMn30'] for r in rs]))} "
                      f"Mn100 gap {fmt(med([r['usMn100']-r['themMn100'] for r in rs]))} C lost r100 {sum(r['usCd'] for r in rs)}/"
                      f"{sum(r['themCd'] for r in rs)}  maps: {', '.join(r['G']['map'] for r in rs)}")
    print('\nsame-map pairs')
    by = collections.defaultdict(list)
    for r in rows: by[r['G']['map']].append(r)
    for mp, rs in sorted(by.items()):
        if len(rs) < 2: continue
        for r in rs:
            G = r['G']
            print(f"  {mp:18s} {G['m']} g{G['g']} {G['opp']:7s} {'W' if G['won'] else 'L'} Mn30 {r['usMn30']}/{r['themMn30']} "
                  f"Mn50 {r['usMn50']}/{r['themMn50']} Mn100 {r['usMn100']}/{r['themMn100']} Ad100 {r['usAd100']}/{r['themAd100']} "
                  f"C lost r100 {r['usCd']}/{r['themCd']}")
    # correlation: Mn gap at r100 vs carriers lost difference, and vs Ad@100
    import math
    def corr(x, y):
        mx, my = sum(x) / len(x), sum(y) / len(y)
        sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
        return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)
    gap = [r['usMn100'] - r['themMn100'] for r in rows]
    print(f"\nPearson r over 47 distinct games: Mn gap r100 vs (C lost r100 them - us) {corr(gap, [r['themCd']-r['usCd'] for r in rows]):.2f}; "
          f"vs our Ad@100 {corr(gap, [r['usAd100'] for r in rows]):.2f}; vs walk to Mn {corr(gap, [r['walk'] for r in rows]):.2f}; "
          f"vs area {corr(gap, [r['area'] for r in rows]):.2f}; vs Mn gap r30 {corr(gap, [r['usMn30']-r['themMn30'] for r in rows]):.2f}")
    won = [r['G']['won'] for r in rows]
    print(f"Pearson r with the result (1 = win): Mn gap r100 {corr(won, gap):.2f}; Mn gap r30 {corr(won, [r['usMn30']-r['themMn30'] for r in rows]):.2f}; "
          f"our Ad@100 {corr(won, [r['usAd100'] for r in rows]):.2f}; Ad gap r100 {corr(won, [r['usAd100']-r['themAd100'] for r in rows]):.2f}; "
          f"C lost diff r100 {corr(won, [r['themCd']-r['usCd'] for r in rows]):.2f}; walk {corr(won, [r['walk'] for r in rows]):.2f}; area {corr(won, [r['area'] for r in rows]):.2f}")


if __name__ == '__main__':
    main()
