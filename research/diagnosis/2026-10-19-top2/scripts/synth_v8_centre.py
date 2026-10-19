"""synth_v8_centre.py: scope of a centre-first skip (Carrier.explore, src/c_kx0/Carrier.java:708-712).

For each of the 47 distinct games: the map centre (W/2, H/2), its least d2 to the enemy's HQs (true locations; the bot
would use MapMem.enemyHQs(), the symmetry candidates, which can add more), and our Mn collected by r100 (census cMn100)
us/them, with the result. Lists the games where that d2 <= 100 (the proposed CENTRE_SKIP_R2), then <= 200.
Usage: python3 -I synth_v8_centre.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_common import *


def main():
    rows = []
    for G in distinct():
        m = load_map(G['map'])
        c = (m['W'] // 2, m['H'] // 2)
        dd = mind2(c, G['hqs'][G['them']])
        cu, ct = census(G, G['us']), census(G, G['them'])
        rows.append((dd, label(G), 'W' if G['won'] else 'L', cu['cMn100'], ct['cMn100']))
    for lim in (100, 200):
        sel = [r for r in rows if r[0] <= lim]
        print(f'## centre within r2 {lim} of an enemy HQ: {len(sel)} games, {sum(r[2] == "L" for r in sel)} losses')
        for r in sorted(sel): print(f'  d2 {r[0]:4} {r[1]} {r[2]} Mn by r100 us {r[3]} them {r[4]}')


main()
