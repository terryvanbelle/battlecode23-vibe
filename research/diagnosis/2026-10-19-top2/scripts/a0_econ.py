# Opening economy per game and side from the per-turn carrier rows (sa_C) and the map file:
#   mnvis  = least d2 from one of the side's HQs to a mana well (HQ vision is r2 34: above 34 the HQ cannot see it)
#   mnwalk = walk distance (8-connected, walls) from the side's nearest HQ to its nearest mana well
#   fMn    = first round a carrier of the side collects mana; fMnDep = first mana deposit
#   Mn50/Mn100 = mana collected by r50 / r100 (sum of collect_amt with collect_res Mn)
#   idle100 = share of carrier turns r<=100 with an empty carrier farther than r2 8 from every own HQ and not collecting
#             (searching or walking to a well)
#   cdie100 = carriers of the side dead by r100 (deaths.csv)
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *


def side_stats(G, side):
    m, g = G['m'], G['g']
    H = hqs(m, g)[side]
    ws = wells(G['map']); W = load_map(G['map'])['W']
    d = bfs(G['map'], H)
    mnvis = min(min(d2((x, y), h) for h in H) for x, y, t in ws if t == 2)
    mnwalk = min(d[x + y * W] for x, y, t in ws if t == 2)
    rows = sa(m, g, side, 'C', 100)
    fMn = fDep = None; mn50 = mn100 = ad100 = 0; idle = tot = 0
    for r in rows:
        rn = r['round']
        if r['collect_res'] == 'Mn' and r['collect_amt']:
            if fMn is None: fMn = rn
            if rn <= 50: mn50 += r['collect_amt']
            if rn <= 100: mn100 += r['collect_amt']
        if r['collect_res'] == 'Ad' and r['collect_amt'] and rn <= 100: ad100 += r['collect_amt']
        if (r['dep_mn'] or 0) > 0 and fDep is None: fDep = rn
        if rn <= 100:
            tot += 1
            empty = (r['ad'] or 0) + (r['mn'] or 0) == 0
            if empty and (r['d2_own_hq'] or 0) > 8 and not r['collect_amt']: idle += 1
    cdie = sum(1 for x in rd(m, 'deaths') if int(x['game']) == g and x['side'] == side and x['type'] == 'C'
               and int(x['round']) <= 100)
    return dict(mnvis=mnvis, mnwalk=mnwalk, fMn=fMn, fMnDep=fDep, Mn50=mn50, Mn100=mn100, Ad100=ad100,
                idle100=round(idle / tot, 2) if tot else None, cdie100=cdie)


if __name__ == '__main__':
    keys = ['mnvis', 'mnwalk', 'fMn', 'fMnDep', 'Mn50', 'Mn100', 'Ad100', 'idle100', 'cdie100']
    print('| game | res | ' + ' | '.join(k + ' us/them' for k in keys) + ' |')
    print('|' + '---|' * (len(keys) + 2))
    out = []
    for G in all_games():
        a, b = side_stats(G, G['us']), side_stats(G, G['them'])
        out.append((G, a, b))
    out.sort(key=lambda t: (t[0]['won'], t[1]['mnvis']))
    for G, a, b in out:
        print(f"| {label(G)} | {'W' if G['won'] else 'L'} | " + ' | '.join(f"{a[k]}/{b[k]}" for k in keys) + ' |')
    # split by HQ vision of the nearest mana well (same for both sides on a symmetric map)
    print()
    for vis in (True, False):
        sel = [t for t in out if (t[1]['mnvis'] <= 34) == vis]
        w = sum(t[0]['won'] for t in sel)
        med = lambda L: sorted(L)[len(L) // 2] if L else None
        print(f"nearest Mn well {'inside' if vis else 'outside'} HQ vision (r2 34): games {len(sel)}, our wins {w}; "
              f"median Mn100 us {med([t[1]['Mn100'] for t in sel])} them {med([t[2]['Mn100'] for t in sel])}; "
              f"median fMn us {med([t[1]['fMn'] or 999 for t in sel])} them {med([t[2]['fMn'] or 999 for t in sel])}; "
              f"median idle100 us {med([t[1]['idle100'] for t in sel])} them {med([t[2]['idle100'] for t in sel])}")
