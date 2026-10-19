"""synth_v4_islands.py: re-check of the island and anchor-gate claims (analyst 2), from timeline.csv, hq.csv, census.

Per class (synth_common.klass) and side: median first round holding an island (timeline, 10-round samples; games that
never do are counted apart), anchors built / placed (census), anchors placed before r400 (timeline anchors_placed).
Gate rebuild (HQ.java:68, rounds 400..min(end, 1490), timeline samples): 'deficit' = their islands > ours (true counts,
not Comms.islThem); 'pressed' = some HQ of ours has pressure34 >= 100 (C.PRESS_SUM) in the current 25-round bucket
(hq.csv; the bot also looks at the previous bucket, so this undercounts 'pressed'). Shares of samples.
TimesUp (9911 g2) timeline r400-2000 every 100 rounds: islands and anchors placed, us/them, and our bank Ad/Mn.
Usage: python3 -I synth_v4_islands.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_common import *


def first_isl(G, side):
    tl = timeline(G, side)
    for rn in sorted(tl):
        if num(tl[rn]['islands'], 0) >= 1: return rn
    return None


def placed_by(G, side, rn):
    tl = timeline(G, side)
    ks = [k for k in tl if k <= rn]
    return num(tl[max(ks)]['anchors_placed'], 0) if ks else 0


def gate(G):
    tu, tt = timeline(G, G['us']), timeline(G, G['them'])
    pr = collections.defaultdict(int)
    for r in hqrows(G, G['us']):
        pr[int(r['round'])] = max(pr[int(r['round'])], num(r['pressure34'], 0))
    c = collections.Counter()
    for rn in sorted(tu):
        if rn < 400 or rn >= 1500 or rn not in tt: continue
        deficit = num(tt[rn]['islands'], 0) > num(tu[rn]['islands'], 0)
        b = ((rn + 24) // 25) * 25
        pressed = pr.get(b, 0) >= 100
        c['n'] += 1
        c['deficit'] += deficit
        c['pressed'] += pressed
        c['open'] += not deficit and not pressed
    return c


def main():
    groups = collections.defaultdict(list)
    for G in distinct(): groups[klass(G)].append(G)
    for k in ('A', 'A0', 'BC', 'W'):
        gs = groups[k]
        print(f'\n## class {k} ({len(gs)} games)')
        for s in ('us', 'them'):
            f = [first_isl(G, G[s]) for G in gs]
            built = sum(num(census(G, G[s])['anchors_built'], 0) for G in gs)
            placed = sum(num(census(G, G[s])['anchors_placed'], 0) for G in gs)
            pre400 = sum(placed_by(G, G[s], 399) for G in gs)
            print(f"  {s:4}: first island median r{med([x for x in f if x is not None])} (never in {sum(x is None for x in f)}), "
                  f"anchors built {built}, placed {placed}, placed before r400 {pre400}")
        c = collections.Counter()
        for G in gs: c.update(gate(G))
        if c['n']:
            print(f"  gate rebuild r400-1490: samples {c['n']}, deficit {c['deficit'] / c['n']:.2f}, "
                  f"pressed {c['pressed'] / c['n']:.2f}, open (neither) {c['open'] / c['n']:.2f}")
    G = [x for x in games() if x['m'] == 9911 and x['g'] == 2][0]
    tu, tt = timeline(G, G['us']), timeline(G, G['them'])
    print('\n## TimesUp 9911 g2: round islands us/them, anchors placed us/them, our bank Ad/Mn')
    for rn in range(400, 2001, 100):
        k = max(x for x in tu if x <= rn)
        print(f"  r{rn}: islands {tu[k]['islands']}/{tt[k]['islands']}, placed {tu[k]['anchors_placed']}/{tt[k]['anchors_placed']}, "
              f"bank {tu[k]['bank_Ad']}/{tu[k]['bank_Mn']}, L {tu[k]['alive_L']}/{tt[k]['alive_L']}")
    c = gate(G)
    print(f"  gate rebuild: samples {c['n']}, deficit {c['deficit']}, pressed {c['pressed']}, open {c['open']}")


main()
