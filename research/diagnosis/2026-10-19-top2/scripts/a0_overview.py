# Per-game overview of the 18 maxwelljones14 games (extract CSVs + map files + our HQ per-turn rows).
# Columns: map size, HQs per side, islands, walk distance between the nearest HQ pair, result; units built by r1-3,
# r50, r100 (robots.csv); alive L and C at r50/r100/r150 and collected Mn/Ad at r100 (timeline.csv); deaths by r100;
# first round an enemy launcher stands within r2 34 of one of our HQs (our sa_HQ rows) and the peak count by r150.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *


def tl(m, g):
    T = {}
    for r in rd(m, 'timeline'):
        if int(r['game']) == g:
            T[(int(r['round']), r['side'])] = r
    return T


def builds(m, g, side, r0, r1, typ):
    return sum(1 for r in rd(m, 'robots') if int(r['game']) == g and r['side'] == side and r['type'] == typ
               and r0 <= int(r['born']) <= r1)


def deaths_by(m, g, side, rmax, typ):
    return sum(1 for d in rd(m, 'deaths') if int(d['game']) == g and d['side'] == side and d['type'] == typ
               and int(d['round']) <= rmax)


def first_hq_contact(G):
    rows = sa(G['m'], G['g'], G['us'], 'HQ')
    first = None; peak = 0; peak_r = None
    for r in rows:
        if r['enemy_L_34'] and r['enemy_L_34'] > 0 and first is None: first = (r['round'], r['enemy_L_34'])
        if r['round'] <= 150 and (r['enemy_L_34'] or 0) > peak: peak = r['enemy_L_34']; peak_r = r['round']
    return first, peak, peak_r


def walk(G):
    H = hqs(G['m'], G['g'])
    d = bfs(G['map'], H[G['us']])
    W = load_map(G['map'])['W']
    return min(d[x + y * W] for (x, y) in H[G['them']])


def row(G):
    m, g, us, th = G['m'], G['g'], G['us'], G['them']
    T = tl(m, g)
    nhq = len(hqs(m, g)[us])
    def a(rn, s, k):
        r = T.get((rn, s)); return int(r[k]) if r else -1
    fc, pk, pkr = first_hq_contact(G)
    return dict(
        game=label(G), res='W' if G['won'] else 'L', rounds=G['rounds'], size=f"{G['W']}x{G['H']}", hq=nhq,
        isl=G['nisl'], walk=walk(G),
        b3=f"{builds(m,g,us,1,3,'L')}L{builds(m,g,us,1,3,'C')}C/{builds(m,g,th,1,3,'L')}L{builds(m,g,th,1,3,'C')}C",
        bL50=f"{builds(m,g,us,1,50,'L')}/{builds(m,g,th,1,50,'L')}",
        bL100=f"{builds(m,g,us,1,100,'L')}/{builds(m,g,th,1,100,'L')}",
        bC100=f"{builds(m,g,us,1,100,'C')}/{builds(m,g,th,1,100,'C')}",
        L50=f"{a(50,us,'alive_L')}/{a(50,th,'alive_L')}", L100=f"{a(100,us,'alive_L')}/{a(100,th,'alive_L')}",
        L150=f"{a(150,us,'alive_L')}/{a(150,th,'alive_L')}",
        C100=f"{a(100,us,'alive_C')}/{a(100,th,'alive_C')}",
        Mn100=f"{a(100,us,'coll_Mn')}/{a(100,th,'coll_Mn')}", Ad100=f"{a(100,us,'coll_Ad')}/{a(100,th,'coll_Ad')}",
        dC100=f"{deaths_by(m,g,us,100,'C')}/{deaths_by(m,g,th,100,'C')}",
        dL100=f"{deaths_by(m,g,us,100,'L')}/{deaths_by(m,g,th,100,'L')}",
        hq1=f"r{fc[0]}:{fc[1]}" if fc else '-', hqpk=f"{pk}@r{pkr}" if pkr else '0',
    )


if __name__ == '__main__':
    rows = [row(G) for G in all_games()]
    rows.sort(key=lambda r: (r['res'], r['rounds']))
    keys = list(rows[0].keys())
    print('| ' + ' | '.join(keys) + ' |')
    print('|' + '---|' * len(keys))
    for r in rows:
        print('| ' + ' | '.join(str(r[k]) for k in keys) + ' |')
