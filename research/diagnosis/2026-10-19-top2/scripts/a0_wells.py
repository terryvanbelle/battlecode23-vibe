# Where launchers go in the opening (r <= RMAX, default 100): the share of a side's launcher turns standing within
# r2 25 of the OTHER side's mana wells (a mana well belongs to the side whose nearest HQ, by walk distance, is nearer),
# and the share of its hits on carriers that land within r2 25 of those wells. Also where the side's carriers are hit.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 100


def owned_mn_wells(G):
    H = hqs(G['m'], G['g']); W = load_map(G['map'])['W']
    du = bfs(G['map'], H[G['us']]); dt = bfs(G['map'], H[G['them']])
    own = {G['us']: [], G['them']: []}
    for x, y, t in wells(G['map']):
        if t != 2: continue
        k = x + y * W
        if du[k] < dt[k]: own[G['us']].append((x, y))
        elif dt[k] < du[k]: own[G['them']].append((x, y))
    return own


def near(p, L, r2=25): return any(d2(p, q) <= r2 for q in L)


def stats(G, side, own):
    other_w = own[other(side)]
    L = sa(G['m'], G['g'], side, 'L', RMAX)
    n = sum(1 for r in L)
    at = sum(1 for r in L if near((r['x'], r['y']), other_w))
    hc = [r for r in L if r['attacked'] and r['atk_hit'] == '1' and r['atk_target_type'] == 'C']
    hcw = sum(1 for r in hc if r['atk_tx'] is not None and near((r['atk_tx'], r['atk_ty']), other_w))
    return dict(turns=n, at_w=round(at / n, 2) if n else None, hitC=len(hc), hitC_at_w=hcw)


if __name__ == '__main__':
    print(f'r <= {RMAX}; at_w = share of launcher turns within r2 25 of the other side\'s mana wells; hitC_at_w = '
          'hits on carriers there')
    print('| game | res | our Mn wells | at_w us/them | hitC us/them | hitC_at_w us/them |')
    print('|---|---|---|---|---|---|')
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        own = owned_mn_wells(G)
        a, b = stats(G, G['us'], own), stats(G, G['them'], own)
        res = 'W' if G['won'] else 'L'
        print(f"| {label(G)} | {res} | {len(own[G['us']])} | {a['at_w']}/{b['at_w']} | {a['hitC']}/{b['hitC']} | "
              f"{a['hitC_at_w']}/{b['hitC_at_w']} |")
        for k in ('at_w', 'hitC', 'hitC_at_w'):
            agg[res]['us_' + k].append(a[k] or 0); agg[res]['th_' + k].append(b[k] or 0)
    med = lambda L: sorted(L)[len(L) // 2]
    for res in ('L', 'W'):
        print(res, ', '.join(f"{k}: us {med(agg[res]['us_' + k])} them {med(agg[res]['th_' + k])} (sum {sum(agg[res]['us_' + k]):.0f}/{sum(agg[res]['th_' + k]):.0f})"
                             for k in ('at_w', 'hitC', 'hitC_at_w')))
