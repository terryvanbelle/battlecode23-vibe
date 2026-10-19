"""a3_builds.py: HQ builds in rounds 1-50, both teams (robots.csv born/type; sa_HQ per-round banks).
Prints per game the build string by round (e.g. 1:LLLLC 2:C ...) compressed per side, counts by r10/r25/r50, the first
launcher/carrier after round 2, and per side the rounds 1-50 on which an HQ held >= 45 Mn at the start of its turn and
built no launcher that turn (idle mana; sa_HQ bank is read at the HQ's turn, built_L the count built that turn).
Usage: python3 -I a3_builds.py [-v]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *

V = '-v' in sys.argv


def seq(G, side, rmax=50):
    by = collections.defaultdict(str)
    for r in robots(G, side):
        b = int(r['born'])
        if r['type'] != 'H' and 1 <= b <= rmax: by[b] += r['type']
    return by


def idle(G, side, rmax=50):
    """HQ-rounds (r3..rmax) where bank_Mn >= 45 + 45*built_L at the turn and ... : sa_HQ bank is after the HQ's actions"""
    rows = sa(G['m'], G['g'], side, 'HQ', rmax)
    n_mn = n_ad = 0; bank_mn = []; bank_ad = []
    for r in rows:
        if r['round'] < 3: continue
        # bank after this turn's builds: an HQ that ends its turn with >= 45 Mn could have built one more launcher
        if r['bank_Mn'] >= 45: n_mn += 1
        if r['bank_Ad'] >= 50: n_ad += 1
        bank_mn.append(r['bank_Mn']); bank_ad.append(r['bank_Ad'])
    return n_mn, n_ad, mean(bank_mn), mean(bank_ad)


def main():
    agg = collections.defaultdict(list)
    print('| match g | map | W/L | side | r1 | r2-10 | r11-25 | r26-50 | L/C by r25 | L/C by r50 | HQ-rounds r3-50 ending with Mn>=45 | Ad>=50 | mean bank Mn/Ad r3-50 |')
    print('|' + '---|' * 13)
    for G in games():
        for s, who in ((G['us'], 'us'), (G['them'], 'them')):
            sq = seq(G, s)
            def cnt(a, b, t): return sum(sq[r].count(t) for r in range(a, b + 1))
            def span(a, b):
                return ' '.join(f'{r}:{sq[r]}' for r in range(a, b + 1) if sq[r]) or '-'
            im, ia, bm, ba = idle(G, s)
            nh = len(G['hqs'][s])
            print(f"| {G['m']} g{G['g']} | {G['map']} | {'W' if G['won'] else 'L'} | {who} | {sq[1]} | {span(2, 10)} | "
                  f"{span(11, 25)} | {span(26, 50)} | {cnt(1, 25, 'L')}/{cnt(1, 25, 'C')} | {cnt(1, 50, 'L')}/{cnt(1, 50, 'C')} | "
                  f"{im} ({im / nh:.0f}/HQ) | {ia} | {bm:.0f}/{ba:.0f} |")
            if G['dup']: continue
            k = ('W' if G['won'] else 'L', who)
            agg[k + ('L25',)].append(cnt(1, 25, 'L')); agg[k + ('C25',)].append(cnt(1, 25, 'C'))
            agg[k + ('L50',)].append(cnt(1, 50, 'L')); agg[k + ('C50',)].append(cnt(1, 50, 'C'))
            agg[k + ('A50',)].append(cnt(1, 50, 'A'))
            agg[k + ('r1L',)].append(sq[1].count('L') / nh); agg[k + ('r1C',)].append(sq[1].count('C') / nh)
            agg[k + ('idleMn',)].append(im / nh); agg[k + ('idleAd',)].append(ia / nh)
            agg[k + ('bankMn',)].append(bm); agg[k + ('bankAd',)].append(ba)
            agg[k + ('L2_50',)].append(cnt(2, 50, 'L') / nh); agg[k + ('C2_50',)].append(cnt(2, 50, 'C') / nh)
    print('\nmedians, distinct games (L = our losses, W = our wins); per-HQ where noted')
    for res in ('L', 'W'):
        for who in ('us', 'them'):
            k = (res, who)
            print(f"  {res} {who:4s} r1 L/HQ {med(agg[k+('r1L',)])} C/HQ {med(agg[k+('r1C',)])} | L/C by r25 {med(agg[k+('L25',)])}/"
                  f"{med(agg[k+('C25',)])} | by r50 {med(agg[k+('L50',)])}/{med(agg[k+('C50',)])} A {sum(agg[k+('A50',)])} | "
                  f"r2-50 per HQ L {mean(agg[k+('L2_50',)]):.2f} C {mean(agg[k+('C2_50',)]):.2f} | "
                  f"HQ-rounds Mn>=45 per HQ {med(agg[k+('idleMn',)])} (mean {mean(agg[k+('idleMn',)]):.1f}) Ad>=50 {med(agg[k+('idleAd',)])} | "
                  f"bank Mn {mean(agg[k+('bankMn',)]):.0f} Ad {mean(agg[k+('bankAd',)]):.0f}")


if __name__ == '__main__':
    main()
