"""a3_rate.py: when does our Mn fall behind, and is it fewer carriers or less Mn per carrier? (timeline.csv, every 10 rounds)
Per 10-round window r0-150, pooled over distinct losses / wins: Mn and Ad collected per window, carriers alive (window
mean of the two ends), Mn collected per carrier-round, cumulative Mn gap us - them, carriers lost (deaths.csv).
Usage: python3 -I a3_rate.py [RMAX]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *

RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def main():
    for res in ('L', 'W'):
        gs = [G for G in games() if not G['dup'] and (G['won'] == (res == 'W'))]
        print(f"\n{res} (distinct n={len(gs)}) | window | us: dMn dAd carriers-alive Mn/carrier-round C-lost | them: same | cum Mn gap")
        print('| window | us dMn | us dAd | us C alive | us Mn per C-round | us C lost | them dMn | them dAd | them C alive | them Mn per C-round | them C lost | cum Mn us-them |')
        print('|' + '---|' * 12)
        cum = 0
        for r0 in range(0, RMAX, 10):
            r1 = r0 + 10
            line = [f'r{r0+1}-{r1}']
            vals = {}
            for who in ('us', 'them'):
                dMn = dAd = calive = lost = 0
                for G in gs:
                    s = G[who]
                    tl = timeline(G, s)
                    a = tl.get(r0); b = tl.get(r1)
                    if b is None: continue
                    mn0 = int(a['coll_Mn']) if a else 0; ad0 = int(a['coll_Ad']) if a else 0
                    c0 = int(a['alive_C']) if a else 0
                    dMn += int(b['coll_Mn']) - mn0; dAd += int(b['coll_Ad']) - ad0
                    calive += (c0 + int(b['alive_C'])) / 2 * 10
                    lost += sum(1 for d in deaths(G, s) if d['type'] == 'C' and r0 < int(d['round']) <= r1)
                vals[who] = dMn
                line += [str(dMn), str(dAd), f'{calive/10/len(gs):.1f}', f'{dMn/calive:.3f}' if calive else '-', str(lost)]
            cum += vals['us'] - vals['them']
            line.append(str(cum))
            print('| ' + ' | '.join(line) + ' |')


if __name__ == '__main__':
    main()
