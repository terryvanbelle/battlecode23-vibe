# Launcher behaviour per game and side in the opening (r <= RMAX, default 150) from the per-turn launcher rows (sa_L).
#   grp     = mean launchers in a group on contact turns (1 + ally_L_20; contact = an enemy launcher within r2 20)
#   out     = share of contact turns where the launcher is locally outnumbered (enemy_L_20 > ally_L_20 + 1)
#   sup     = share of contact turns where it outnumbers them (ally_L_20 + 1 > enemy_L_20 + 1)
#   prog    = median progress of launcher turns toward the enemy (sqrt d own HQ / (sqrt d own + sqrt d enemy))
#   still   = share of attack turns with no move (the launcher fired from where it stood)
#   hitC/hitL = hits on carriers / launchers; c1 = first round of a hit on an enemy carrier
#   arrive  = first round a launcher of the side stands within r2 100 of an enemy HQ, and how many launchers of the side
#             are within r2 100 of that HQ that round
#   firstL  = first round with a launcher in contact (enemy launcher within r2 20)
import sys, os, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def stats(G, side, rmax=RMAX):
    rows = sa(G['m'], G['g'], side, 'L', rmax)
    c = collections.Counter(); grp = []; progs = []
    arrive = None; byr = collections.defaultdict(int); firstL = None; c1 = None
    for r in rows:
        dO, dE = r['d2_own_hq'], r['d2_enemy_hq']
        progs.append(math.sqrt(dO) / (math.sqrt(dO) + math.sqrt(dE)) if dO + dE > 0 else 0.5)
        if r['enemy_L_20'] > 0:
            if firstL is None: firstL = r['round']
            c['contact'] += 1; grp.append(1 + r['ally_L_20'])
            if r['enemy_L_20'] > r['ally_L_20'] + 1: c['out'] += 1
            if r['ally_L_20'] + 1 > r['enemy_L_20']: c['sup'] += 1
        if r['attacked']:
            c['att'] += 1
            if r['moved'] == 0: c['still'] += 1
            if r['atk_hit'] == '1':
                if r['atk_target_type'] == 'C':
                    c['hitC'] += 1
                    if c1 is None: c1 = r['round']
                elif r['atk_target_type'] == 'L': c['hitL'] += 1
        if dE <= 100: byr[r['round']] += 1
    if byr:
        r0 = min(byr); arrive = f"r{r0}:{byr[r0]} (max {max(byr.values())})"
    progs.sort()
    return dict(grp=round(sum(grp) / len(grp), 1) if grp else None,
                out=round(c['out'] / c['contact'], 2) if c['contact'] else None,
                sup=round(c['sup'] / c['contact'], 2) if c['contact'] else None,
                prog=round(progs[len(progs) // 2], 2) if progs else None,
                still=round(c['still'] / c['att'], 2) if c['att'] else None,
                hitC=c['hitC'], c1=c1, hitL=c['hitL'], arrive=arrive or '-', firstL=firstL)


if __name__ == '__main__':
    keys = ['grp', 'out', 'sup', 'prog', 'still', 'hitC', 'c1', 'hitL', 'arrive', 'firstL']
    print(f'r <= {RMAX}')
    print('| game | res | ' + ' | '.join(k + ' us/them' for k in keys) + ' |')
    print('|' + '---|' * (len(keys) + 2))
    agg = {k: collections.defaultdict(list) for k in ('W', 'L')}
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        a, b = stats(G, G['us']), stats(G, G['them'])
        res = 'W' if G['won'] else 'L'
        print(f"| {label(G)} | {res} | " + ' | '.join(f"{a[k]}/{b[k]}" for k in keys) + ' |')
        for k in ('grp', 'out', 'sup', 'prog', 'still', 'hitC', 'hitL'):
            if a[k] is not None: agg[res]['us_' + k].append(a[k])
            if b[k] is not None: agg[res]['th_' + k].append(b[k])
    med = lambda L: sorted(L)[len(L) // 2] if L else None
    print()
    for res in ('L', 'W'):
        print(res, ', '.join(f"{k} us {med(agg[res]['us_' + k])} them {med(agg[res]['th_' + k])}"
                             for k in ('grp', 'out', 'sup', 'prog', 'still', 'hitC', 'hitL')))
