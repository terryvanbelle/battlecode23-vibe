"""a3_hqfirst.py: per HQ, when does carrier mana first arrive, and how much by r50/r100, split by whether the HQ's
nearest Mn well is inside HQ vision (r2 <= 34). Maps are symmetric, so each of our HQs has a mirror HQ on their side with
the same layout: the comparison us vs them per stratum is a decision comparison on identical geometry.
Carrier Mn into an HQ = bank_Mn(r+1) - left_Mn(r) minus the passive +6 on rounds r % 5 == 0 (RULES 3.1; sa_HQ banks are
read at the start of the HQ's turn). First deposit = first round with carrier Mn > 0.
Usage: python3 -I a3_hqfirst.py [-v]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *

V = '-v' in sys.argv


def per_hq(G, side):
    rows = sa(G['m'], G['g'], side, 'HQ', 300)
    by = collections.defaultdict(list)
    for r in rows: by[(r['x'], r['y'])].append(r)
    mf = {p['hq']: p for p in mapfeat(G, side)['per']}
    out = []
    for hq, rs in by.items():
        rs.sort(key=lambda r: r['round'])
        first = None; mn50 = mn100 = mn150 = 0
        for i in range(len(rs) - 1):
            r, nx = rs[i], rs[i + 1]
            if nx['round'] != r['round'] + 1: continue
            left = r['bank_Mn'] - 45 * r['built_L'] - 15 * r['built_A']
            car = nx['bank_Mn'] - left - (6 if r['round'] % 5 == 0 else 0)
            if car > 0:
                if first is None: first = r['round']
                if r['round'] <= 50: mn50 += car
                if r['round'] <= 100: mn100 += car
                if r['round'] <= 150: mn150 += car
        p = mf.get(hq)
        out.append(dict(hq=hq, walk=p['walk_mn'] if p else None, d2=p['d2_mn'] if p else None, first=first,
                        mn50=mn50, mn100=mn100, mn150=mn150))
    return out


def main():
    agg = collections.defaultdict(list)
    for G in games():
        for who in ('us', 'them'):
            for h in per_hq(G, G[who]):
                if V: print(label(G), who, h)
                if G['dup']: continue
                vis = 'in vision' if h['d2'] is not None and h['d2'] <= 34 else 'out of vision'
                k = (vis, 'W' if G['won'] else 'L', who)
                agg[k].append(h)
    print('| nearest Mn well | games | side | HQs | first carrier Mn (median round) | no carrier Mn by r100 | carrier Mn r50 (mean/HQ) | r100 | r150 |')
    print('|' + '---|' * 9)
    for vis in ('in vision', 'out of vision'):
        for res in ('L', 'W'):
            for who in ('us', 'them'):
                hs = agg[(vis, res, who)]
                if not hs: continue
                print(f"| {vis} | {res} | {who} | {len(hs)} | {fmt(med([h['first'] for h in hs if h['first'] is not None]))} | "
                      f"{sum(1 for h in hs if h['first'] is None or h['first'] > 100)} | {mean([h['mn50'] for h in hs]):.0f} | "
                      f"{mean([h['mn100'] for h in hs]):.0f} | {mean([h['mn150'] for h in hs]):.0f} |")


if __name__ == '__main__':
    main()
