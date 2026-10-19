"""a3_convert.py: how fast each side turns mana into launchers, and HQ idle funds, rounds 1-R (default 150).
sa_HQ banks are read at the start of the HQ's turn (r1 shows 200/200 with the r1 builds in built_*), so per HQ turn:
  left_Mn = bank_Mn - 45 built_L - 15 built_A,  left_Ad = bank_Ad - 50 built_C - 30 built_A - 80 anchors_std
  received(r) = bank(r+1) - left(r)        (passive income + carrier deposits that arrive before the next turn)
Per side: Mn available r1-R (the 200 round-1 stock per HQ plus everything received), launchers built r1-R, conversion
45 L / Mn available (maxwell builds its first launchers in r2-3, so round 1 cannot be dropped), mean left Mn per
HQ turn, HQ turns with left Mn >= 45 (a launcher affordable and not built) and left Ad >= 50, and Mn holding time
(mean left Mn / Mn received per HQ-round). Ours also: hq.csv telemetry codes p (poor) and t (carrier withheld under threat).
Usage: python3 -I a3_convert.py [R]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *

RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def side_stats(G, side):
    rows = sa(G['m'], G['g'], side, 'HQ', 300)
    byhq = collections.defaultdict(list)
    for r in rows:
        if r['round'] <= RMAX + 1: byhq[r['hq_id']].append(r)
    recMn = recAd = 0; L = C = 0; leftMn = []; leftAd = []; idleMn = idleAd = 0; turns = 0
    for hid, rs in byhq.items():
        rs.sort(key=lambda r: r['round'])
        for i, r in enumerate(rs):
            if r['round'] > RMAX: break
            lm = r['bank_Mn'] - 45 * r['built_L'] - 15 * r['built_A']
            la = r['bank_Ad'] - 50 * r['built_C'] - 30 * r['built_A'] - 80 * (r['anchors_std'] or 0)
            L += r['built_L']; C += r['built_C']
            turns += 1; leftMn.append(lm); leftAd.append(la)
            if lm >= 45: idleMn += 1
            if la >= 50: idleAd += 1
            if i + 1 < len(rs) and rs[i + 1]['round'] == r['round'] + 1:
                recMn += rs[i + 1]['bank_Mn'] - lm; recAd += rs[i + 1]['bank_Ad'] - la
    recMn += 200 * len(byhq); recAd += 200 * len(byhq)          # the round-1 stock of every HQ
    return dict(recMn=recMn, recAd=recAd, L=L, C=C, leftMn=mean(leftMn), leftAd=mean(leftAd), idleMn=idleMn, idleAd=idleAd,
                turns=turns, conv=45 * L / recMn if recMn else None)


def codes(G):
    c = collections.Counter()
    for r in hqrows(G, G['us']):
        if int(r['round']) > RMAX or not r['codes']: continue
        for kv in r['codes'].split(';'):
            k, v = kv.split('=')
            c[k] += int(v)
    return c


def idle_csv(G, side):
    """hq.csv idle_funds (ReplayDump: HQ-rounds ending with Ad >= 50 or Mn >= 45, nothing built, a free spawn tile)"""
    return sum(int(r['idle_funds']) for r in hqrows(G, side) if int(r['round']) <= RMAX)


def main():
    print(f'rounds 1-{RMAX}')
    print('| match g | map | W/L | Mn available us/them | L built us/them | 45L / Mn available us/them | mean left Mn per HQ turn us/them | '
          'HQ turns left Mn>=45 us/them | left Ad>=50 us/them | our codes p / t |')
    print('|' + '---|' * 10)
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    for G in games():
        u = side_stats(G, G['us']); t = side_stats(G, G['them']); c = codes(G)
        print(f"| {G['m']} g{G['g']} | {G['map']} | {'W' if G['won'] else 'L'} | {u['recMn']}/{t['recMn']} | {u['L']}/{t['L']} | "
              f"{fmt(u['conv'],2)}/{fmt(t['conv'],2)} | {u['leftMn']:.0f}/{t['leftMn']:.0f} | {u['idleMn']}/{t['idleMn']} | "
              f"{u['idleAd']}/{t['idleAd']} | {c['p']}/{c['t']} |")
        if G['dup']: continue
        k = 'W' if G['won'] else 'L'
        for who, s in (('us', u), ('them', t)):
            for kk, v in s.items(): agg[(k, who)][kk].append(v)
        agg[(k, 'us')]['p'].append(c['p']); agg[(k, 'us')]['t'].append(c['t'])
        agg[(k, 'us')]['idlecsv'].append(idle_csv(G, G['us'])); agg[(k, 'them')]['idlecsv'].append(idle_csv(G, G['them']))
    print('\npooled over distinct games (sums; turns are HQ turns)')
    for k in ('L', 'W'):
        for who in ('us', 'them'):
            a = agg[(k, who)]
            rec = sum(a['recMn']); L = sum(a['L']); turns = sum(a['turns'])
            lm = sum(m * n for m, n in zip(a['leftMn'], a['turns'])) / turns
            la = sum(m * n for m, n in zip(a['leftAd'], a['turns'])) / turns
            print(f"  {k} {who:4s} Mn available {rec} L built {L} conversion {45*L/rec:.3f} | mean left Mn {lm:.1f} Ad {la:.1f} per HQ turn | "
                  f"Mn holding time {lm / (rec / turns):.1f} rounds | turns left Mn>=45 {sum(a['idleMn'])}/{turns} ({sum(a['idleMn'])/turns:.3f}) "
                  f"left Ad>=50 {sum(a['idleAd'])}/{turns} ({sum(a['idleAd'])/turns:.3f}) | Ad received {sum(a['recAd'])} C built {sum(a['C'])}"
                  + f" | hq.csv idle_funds {sum(a['idlecsv'])}"
                  + (f" | codes p {sum(a['p'])} t {sum(a['t'])}" if who == 'us' else ''))


if __name__ == '__main__':
    main()
