"""synth_v2_binding.py: which resource binds after the early squeeze? (hq.csv, timeline.csv, tele_states.csv)

For the synthesis classes (synth_pergame.synth_class) A (decided by r260 with a carrier gap) and W (wins):
  team bank Ad / Mn summed over HQs at r100, r150, r200, r250 (hq.csv, end of 25-round bucket), medians over games;
  carriers and launchers built r101-250 (hq.csv buckets 125..250), sums, us/them;
  our HQ telemetry letters over the whole game (tele_states phase 'all'): share t (carrier withheld under threat, Ad
  available), p (too poor), c (carrier cap).
If Ad piles up while Mn stays near 0 and the HQ shows 't', carriers are not the binding cost: Mn income is.
Usage: python3 -I synth_v2_binding.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_common import *

def bank(G, side, rn, k):
    return sum(num(r[k], 0) for r in hqrows(G, side) if int(r['round']) == rn)


def built(G, side, lo, hi, k):
    return sum(num(r[k], 0) for r in hqrows(G, side) if lo < int(r['round']) <= hi)


def letters(G):
    c = collections.Counter()
    for r in tele(G, G['us']):
        if r['type'] == 'H' and r['phase'] == 'all': c[r['letter']] += int(r['turns'])
    return c


def main():
    groups = collections.defaultdict(list)
    for G in distinct(): groups[klass(G)].append(G)
    for k in ('A', 'A0', 'BC', 'W'):
        gs = groups[k]
        print(f'\n## class {k}: {len(gs)} distinct games')
        for rn in (100, 150, 200, 250):
            vals = {s: (med([bank(G, G[s], rn, 'bank_Ad') for G in gs]), med([bank(G, G[s], rn, 'bank_Mn') for G in gs]))
                    for s in ('us', 'them')}
            print(f"  r{rn}: median team bank Ad/Mn  us {vals['us'][0]}/{vals['us'][1]}   them {vals['them'][0]}/{vals['them'][1]}")
        for s in ('us', 'them'):
            print(f"  built r101-250 ({s}): carriers {sum(built(G, G[s], 100, 250, 'built_C') for G in gs)}, "
                  f"launchers {sum(built(G, G[s], 100, 250, 'built_L') for G in gs)}")
        L = collections.Counter()
        for G in gs: L.update(letters(G))
        tot = sum(L.values())
        print('  our HQ letters (whole game): ' + ', '.join(f'{x} {L[x] / tot:.2f}' for x in ('t', 'p', 'c', 'a', '.')))


main()
