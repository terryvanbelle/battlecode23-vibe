"""a2_kills: who kills what, by phase window (deaths.csv cause == launcher; the killer's side is the victim's other
side). Our kills of their carriers / launchers, and theirs of ours, pooled over losses and wins; the 'carrier kill
share' of each side's launcher kills. Usage: python3 -I a2_kills.py"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
WIN = [(0, 300), (300, 600), (600, 1000), (1000, 2001)]


def main():
    pool = collections.defaultdict(collections.Counter)
    for m, g, k in A.ALL:
        d = A.G(m, g)
        kk = 'L' if k != 'W' else 'W'
        for x in A.rows(m, 'deaths'):
            if int(x['game']) != g or x['cause'] != 'launcher':
                continue
            r = int(x['round'])
            w = next(f'{a}-{b - 1}' for a, b in WIN if a <= r < b)
            victim = 'us' if x['side'] == d['us'] else 'them'
            pool[(kk, w)][f"{'their' if victim == 'us' else 'our'}_kills_{x['type']}"] += 1
    for kk in ('L', 'W'):
        print(f"== {'losses' if kk == 'L' else 'wins'}")
        for a, b in WIN:
            w = f'{a}-{b - 1}'
            c = pool[(kk, w)]
            oc, ol, oa = c['our_kills_C'], c['our_kills_L'], c['our_kills_A']
            tc, tl, ta = c['their_kills_C'], c['their_kills_L'], c['their_kills_A']
            print(f"  {w}: our kills C {oc} L {ol} A {oa} (carrier share {oc / max(1, oc + ol):.2f}) | their kills C {tc} L {tl} "
                  f"(carrier share {tc / max(1, tc + tl):.2f})")


if __name__ == '__main__':
    main()
