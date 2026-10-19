"""Synthesis step (diag-top2, 2026-10-19): shared helpers for the synth_*.py re-checks.

Reuses the read-only loaders of a3_common (extract CSVs, map files, game list). Every synth_* script recomputes its
claim from the extracts (matches/<m>/extract/*.csv) and the engine map files; none reads an analyst's output.
Run each one with python3 -I from any directory.
"""
import sys, os, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import (games, rd, census, timeline, robots, trips, deaths, hqrows, wells, load_map, d2, med, mean,
                       num, label, other, CARL, MAXW, US)

HOT_HOME_D2, HOT_FRONT_PCT = 64, 36     # src/c_kx0/C.java:345-346


def front_gate(home_d2, enemy_d2):
    """Carrier.frontGate (src/c_kx0/Carrier.java:501-503)."""
    return home_d2 > HOT_HOME_D2 and 100 * home_d2 >= HOT_FRONT_PCT * enemy_d2


def mind2(p, pts):
    return min((d2(p, q) for q in pts), default=10 ** 9)


def distinct():
    """the 47 distinct games (9921 g0 repeats 9888 g0)"""
    return [G for G in games() if not G['dup']]


def losses(all31=False):
    return [G for G in (games() if all31 else distinct()) if not G['won']]


def wins():
    return [G for G in distinct() if G['won']]


def our_mn_wells(G):
    """our side's mana wells: nearer (d2) to one of our HQs than to every enemy HQ; with frontGate verdict"""
    us, th = G['hqs'][G['us']], G['hqs'][G['them']]
    out = []
    for x, y, t in wells(G['map']):
        if t != 2: continue
        hd, ed = mind2((x, y), us), mind2((x, y), th)
        if hd < ed:
            out.append(dict(xy=(x, y), homeD2=hd, enemyD2=ed, front=front_gate(hd, ed)))
    return out


def tele(G, side=None):
    return [r for r in rd(G['m'], 'tele_states') if int(r['game']) == G['g'] and (side is None or r['side'] == side)]


def fmt(v, nd=2):
    if v is None: return '-'
    if isinstance(v, float): return f'{v:.{nd}f}'
    return str(v)


def klass(G):
    """synthesis class of a game: W win; A decided by r260 (census turn_round) with our carrier deaths <= r150 at least
    theirs + 3; A0 decided by r260 without that carrier gap; BC later turn (synth_pergame splits it into B and C)."""
    u, t = G['us'], G['them']
    if G['won']: return 'W'
    turn = num(census(G, u)['turn_round'])
    cu = sum(1 for r in deaths(G, u) if r['type'] == 'C' and int(r['round']) <= 150)
    ct = sum(1 for r in deaths(G, t) if r['type'] == 'C' and int(r['round']) <= 150)
    if turn is not None and turn <= 260: return 'A' if cu >= ct + 3 else 'A0'
    return 'BC'
