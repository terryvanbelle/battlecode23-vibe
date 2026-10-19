"""synth_v3_launchers.py: re-check of the launcher trickle and besieged-spawn claims (analysts 1 and 2), from
robots.csv, deaths.csv and hq.csv only (no per-turn dumps).

Launchers born r3-250 (after the opening wave), per side and class (synth_common.klass: A, A0, BC, W): born, dead within
20 rounds of birth, dead within d2 100 of an own HQ (deaths.csv), median life (alive at the end: life to the end).
Besieged spawns, whole game, our side: launchers born at an HQ whose 25-round bucket has pressure34 >= 75 (an average
of 3+ enemy fighters in HQ vision): count, share of all our launchers, median life, kills credited to them (deaths.csv
killer_id), Mn spent (45 each); the rest of our launchers for comparison.
Usage: python3 -I synth_v3_launchers.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_common import *


def kills_by(G, side):
    c = collections.Counter()
    for r in deaths(G, other(side)):
        if r['killer_id']: c[int(r['killer_id'])] += 1
    return c


def pressure(G, side):
    return {(int(r['x']), int(r['y']), int(r['round'])): num(r['pressure34'], 0) for r in hqrows(G, side)}


def bucket_p(pr, h, b):
    end = ((b + 24) // 25) * 25
    v = pr.get((h[0], h[1], end))
    if v is None:
        ks = [k for k in pr if k[0] == h[0] and k[1] == h[1] and k[2] >= b]
        v = pr[min(ks, key=lambda k: k[2])] if ks else 0
    return v


def main():
    groups = collections.defaultdict(list)
    for G in distinct(): groups[klass(G)].append(G)
    print('## launchers born r3-250')
    for k in ('A', 'A0', 'BC', 'W'):
        for s in ('us', 'them'):
            born = d20 = home = 0
            lives = []
            for G in groups[k]:
                side = G[s]
                hqs = G['hqs'][side]
                dl = {int(r['id']): r for r in deaths(G, side) if r['type'] == 'L'}
                for r in robots(G, side):
                    if r['type'] != 'L': continue
                    b = int(r['born'])
                    if not 3 <= b <= 250: continue
                    born += 1
                    died = int(r['died']) if r['died'] else G['rounds']
                    lives.append(died - b)
                    if r['died'] and died - b <= 20: d20 += 1
                    dr = dl.get(int(r['id']))
                    if dr and mind2((int(dr['x']), int(dr['y'])), hqs) <= 100: home += 1
            print(f'  {k:3} {s:4}: born {born}, dead within 20 rounds {d20} ({d20 / max(1, born):.2f}), '
                  f'died within d2 100 of own HQ {home} ({home / max(1, born):.2f}), median life {med(lives)}')
    print('\n## our besieged spawns (bucket pressure34 >= 75), whole game')
    for k in ('A', 'A0', 'BC', 'W'):
        nb = nall = kb = kr = 0
        lb, lr = [], []
        for G in groups[k]:
            side = G['us']
            pr = pressure(G, side)
            kc = kills_by(G, side)
            for r in robots(G, side):
                if r['type'] != 'L' or int(r['born']) <= 2: continue
                nall += 1
                b = int(r['born'])
                h = min(G['hqs'][side], key=lambda q: d2(q, (int(r['x_born']), int(r['y_born']))))
                life = (int(r['died']) if r['died'] else G['rounds']) - b
                if bucket_p(pr, h, b) >= 75:
                    nb += 1; lb.append(life); kb += kc[int(r['id'])]
                else:
                    lr.append(life); kr += kc[int(r['id'])]
        print(f'  {k:3}: besieged {nb} of {nall} ({nb / max(1, nall):.2f}), median life {med(lb)} vs {med(lr)}, '
              f'kills each {kb / max(1, nb):.2f} vs {kr / max(1, nall - nb):.2f}, Mn {45 * nb}')


main()
