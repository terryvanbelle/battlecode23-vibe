"""synth_pergame.py: one row per game (all 48, 9921 g0 marked dup) with the indicators the synthesis classifies on.

Columns (us/them unless noted), all from matches/<m>/extract/*.csv:
  res rounds reason turn lock    games.csv / census (turn_round, lock_round)
  Cd150   carriers dead <= r150 (deaths.csv)
  Chome   our carriers dead <= r150 within r2 34 of one of our own-side mana wells that Carrier.frontGate calls home
  Mn100   collected Mn by r100 (census cMn100)
  L100 L250  launchers alive (census L100, L250)
  Cd3-6   carriers dead r300-599
  isl1    first round (timeline, 10-round samples) the side holds >= 1 island; '-' never
  anc     anchors placed (census)
  besL    our launchers built in 25-round HQ buckets with pressure34 >= 75 (3+ enemy fighters in HQ vision on average;
          hq.csv), and their median life in rounds (robots.csv, matched by HQ position and bucket)
  t%      share of our HQ turns with telemetry letter t (carrier withheld under threat), whole game (tele_states)
  X%      share of our Mn-role carrier turns in state X (explore) in the open phase (<= r150)
  type    synthesis class (see synth_classes in this file)
Usage: python3 -I synth_pergame.py [--csv]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_common import *

CSV = '--csv' in sys.argv


def cnum(G, side, k):
    return num(census(G, side)[k])


def cdead(G, side, lo, hi):
    return sum(1 for r in deaths(G, side) if r['type'] == 'C' and lo <= int(r['round']) <= hi)


def chome(G):
    mw = [w for w in our_mn_wells(G) if not w['front']]
    n = 0
    for r in deaths(G, G['us']):
        if r['type'] != 'C' or int(r['round']) > 150: continue
        p = (int(r['x']), int(r['y']))
        n += any(d2(p, w['xy']) <= 34 for w in mw)
    return n


def isl1(G, side):
    tl = timeline(G, side)
    for rn in sorted(tl):
        if num(tl[rn]['islands'], 0) >= 1: return rn
    return None


def besieged(G):
    """our launchers born in a bucket (25 rounds ending at hq.csv round) at an HQ with pressure34 >= 75"""
    hb = {}
    for r in hqrows(G, G['us']):
        hb[(int(r['x']), int(r['y']), int(r['round']))] = num(r['pressure34'], 0)
    lives, n = [], 0
    for r in robots(G, G['us']):
        if r['type'] != 'L': continue
        b = int(r['born'])
        if b <= 2: continue
        x, y = int(r['x_born']), int(r['y_born'])
        # the HQ that built it: nearest of ours (spawn tiles are within r2 9)
        h = min(G['hqs'][G['us']], key=lambda q: d2(q, (x, y)))
        end = ((b + 24) // 25) * 25
        p = hb.get((h[0], h[1], end))
        if p is None:
            # last partial bucket (round = game end)
            ks = [k for k in hb if k[0] == h[0] and k[1] == h[1] and k[2] >= b]
            p = hb[min(ks, key=lambda k: k[2])] if ks else 0
        if p >= 75:
            n += 1
            died = int(r['died']) if r['died'] else G['rounds']
            lives.append(died - b)
    return n, med(lives)


def tshare(G):
    tot = t = 0
    for r in tele(G, G['us']):
        if r['type'] == 'H' and r['phase'] == 'all':
            k = int(r['turns'])
            tot += k
            if r['letter'] == 't': t += k
    return t / tot if tot else None


def xshare(G):
    tot = x = 0
    for r in tele(G, G['us']):
        if r['type'] == 'C' and r['phase'] == 'open' and 'role=Mn' in r['detail']:
            k = int(r['turns'])
            tot += k
            if r['letter'] == 'X': x += k
    return x / tot if tot else None


def row(G):
    u, t = G['us'], G['them']
    d = dict(game=f"{G['m']} g{G['g']}", map=G['map'], opp=G['opp'], dup=G['dup'], won=G['won'], rounds=G['rounds'],
             reason=G['reason'], turn=census(G, u)['turn_round'], lock=census(G, u)['lock_round'])
    d['Cd150'] = (cdead(G, u, 0, 150), cdead(G, t, 0, 150))
    d['Chome'] = chome(G)
    d['Mn100'] = (cnum(G, u, 'cMn100'), cnum(G, t, 'cMn100'))
    d['L100'] = (cnum(G, u, 'L100'), cnum(G, t, 'L100'))
    d['L250'] = (cnum(G, u, 'L250'), cnum(G, t, 'L250'))
    d['Cd36'] = (cdead(G, u, 300, 599), cdead(G, t, 300, 599))
    d['isl1'] = (isl1(G, u), isl1(G, t))
    d['anc'] = (cnum(G, u, 'anchors_placed'), cnum(G, t, 'anchors_placed'))
    d['besL'] = besieged(G)
    d['t'] = tshare(G)
    d['X'] = xshare(G)
    d['type'] = synth_class(d)
    return d


def synth_class(d):
    """A: decided by r260 (turn_round <= 260) with our carrier deaths <= r150 at least theirs + 3 (home-well squeeze);
    A0: decided by r260 without that carrier gap (launcher fight lost first);
    C: turn later than r260 and the game ended on an island tiebreak, or by conquest at r800+ with L250 within 5;
    B: other late turns (midgame break)."""
    if d['won']: return 'W'
    turn = num(d['turn'])
    cu, ct = d['Cd150']
    if turn is not None and turn <= 260:
        return 'A' if cu >= ct + 3 else 'A0'
    if d['reason'].startswith('tb_'): return 'C'
    lu, lt = d['L250']
    if d['rounds'] >= 800 and abs(lu - lt) <= 5: return 'C'
    return 'B'


def p(v):
    if isinstance(v, tuple): return '/'.join(fmt(x, 0) if not isinstance(x, float) else f'{x:.0f}' for x in v)
    if isinstance(v, float): return f'{v:.2f}'
    return str(v)


def main():
    rows = [row(G) for G in games()]
    cols = ['game', 'map', 'opp', 'won', 'rounds', 'reason', 'turn', 'lock', 'Cd150', 'Chome', 'Mn100', 'L100', 'L250',
            'Cd36', 'isl1', 'anc', 'besL', 't', 'X', 'type']
    if CSV:
        print(','.join(cols))
        for d in rows: print(','.join(p(d[c]).replace(',', ';') for c in cols))
        return
    print('| ' + ' | '.join(cols) + ' |')
    print('|' + '---|' * len(cols))
    for d in rows:
        print('| ' + ' | '.join(p(d[c]) + ('*' if c == 'game' and d['dup'] else '') for c in cols) + ' |')
    print('\n* duplicate replay (9921 g0 = 9888 g0)')
    cnt = collections.Counter(d['type'] for d in rows)
    print('types over 48 games (dup included):', dict(cnt))
    cnt = collections.Counter(d['type'] for d in rows if not d['dup'])
    print('types over 47 distinct:', dict(cnt))
    for ty in ('A', 'A0', 'B', 'C'):
        print(ty, [f"{d['map']}({d['game']})" for d in rows if d['type'] == ty])


main()
