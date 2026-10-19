"""a3_decomp.py: decompose the Mn-collected gap (us - them) over rounds 1-R into
  count  = (carrier-rounds us - them) x their Mn per carrier-round      (fewer carriers alive: deaths, builds)
  rate   = our carrier-rounds x (our Mn per carrier-round - theirs)      (each carrier collects less Mn)
and split our rate shortfall into the Ad we collected instead (each kg of Ad is one collect action not spent on Mn; RULES
3.3: 1 kg per collect at an unupgraded well) and the rest (walking, fleeing, waiting, exploring).
Carrier-rounds from timeline.csv alive_C every 10 rounds (trapezoid). Distinct games, losses and wins.
Usage: python3 -I a3_decomp.py [R]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *

R = int(sys.argv[1]) if len(sys.argv) > 1 else 100


def cr(tl):
    s = 0; prev = 0
    for r in range(10, R + 1, 10):
        a = int(tl[r]['alive_C']) if r in tl else 0
        s += (prev + a) / 2 * 10; prev = a
    return s


def main():
    print(f'rounds 1-{R}')
    for res in ('L', 'W'):
        gs = [G for G in games() if not G['dup'] and (G['won'] == (res == 'W'))]
        tot = dict(cu=0, ct=0, mu=0, mt=0, au=0, at=0)
        per = []
        for G in gs:
            tu = timeline(G, G['us']); tt = timeline(G, G['them'])
            if R not in tu or R not in tt: continue
            cu, ct = cr(tu), cr(tt)
            mu, mt = int(tu[R]['coll_Mn']), int(tt[R]['coll_Mn'])
            au, at = int(tu[R]['coll_Ad']), int(tt[R]['coll_Ad'])
            for k, v in (('cu', cu), ('ct', ct), ('mu', mu), ('mt', mt), ('au', au), ('at', at)): tot[k] += v
            rt = mt / ct if ct else 0
            per.append((G, mu - mt, (cu - ct) * rt, cu * ((mu / cu if cu else 0) - rt), au - at))
        rt = tot['mt'] / tot['ct']; ru = tot['mu'] / tot['cu']
        gap = tot['mu'] - tot['mt']; cnt = (tot['cu'] - tot['ct']) * rt; rate = tot['cu'] * (ru - rt)
        # the Ad we collected beyond their Ad share of their own carrier-rounds
        ad_excess = tot['au'] - tot['cu'] * tot['at'] / tot['ct']
        print(f"  {res} n={len(per)}: Mn gap {gap} = count {cnt:.0f} + rate {rate:.0f}  (carrier-rounds {tot['cu']:.0f} vs {tot['ct']:.0f}; "
              f"Mn per carrier-round {ru:.3f} vs {rt:.3f}; Ad per carrier-round {tot['au']/tot['cu']:.3f} vs {tot['at']/tot['ct']:.3f}; "
              f"our Ad beyond their Ad rate {ad_excess:.0f} kg = {ad_excess / max(1, -rate) * 100 if rate < 0 else float('nan'):.0f}% of the rate term)")
        print(f"     per game: count term < rate term in {sum(1 for p in per if p[2] < p[3])}/{len(per)} games")
        if res == 'L':
            for G, g, c, r_, a in sorted(per, key=lambda p: p[1]):
                print(f"     {label(G):28s} gap {g:5d} count {c:6.0f} rate {r_:6.0f} Ad gap {a:4d}")


if __name__ == '__main__':
    main()
