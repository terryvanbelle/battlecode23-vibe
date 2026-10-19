# Focus fire on launchers, r <= RMAX (default 200): for every launcher killed (deaths.csv, cause launcher), the attackers'
# rows (sa_L of the killing side, atk_target_id = victim, atk_hit 1): distinct attackers in the kill round and in the
# last 5 rounds, and rounds from the victim's first hit to its death (time to kill; a launcher has 200 HP = 10 hits).
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200

if __name__ == '__main__':
    agg = {(res, who): collections.defaultdict(list) for res in 'WL' for who in ('us', 'them')}
    for G in all_games():
        res = 'W' if G['won'] else 'L'
        for who, killer in (('us', G['us']), ('them', G['them'])):
            hits = collections.defaultdict(list)          # victim id -> [(round, attacker)]
            for r in sa(G['m'], G['g'], killer, 'L', RMAX):
                if r['attacked'] and r['atk_hit'] == '1' and r['atk_target_type'] == 'L' and r['atk_target_id'] is not None:
                    hits[r['atk_target_id']].append((r['round'], r['id']))
            for d in rd(G['m'], 'deaths'):
                if int(d['game']) != G['g'] or d['type'] != 'L' or d['side'] == killer or int(d['round']) > RMAX: continue
                h = hits.get(int(d['id']))
                if not h: continue
                dr = int(d['round'])
                A = agg[(res, who)]
                A['kill_round'].append(len({a for (rr, a) in h if rr == dr}))
                A['last5'].append(len({a for (rr, a) in h if dr - 5 < rr <= dr}))
                A['ttk'].append(dr - min(rr for (rr, a) in h))
    med = lambda L: sorted(L)[len(L) // 2] if L else None
    mean = lambda L: sum(L) / len(L) if L else 0
    print(f'r <= {RMAX}; kills of launchers credited from the killer side\'s per-turn rows')
    print('| games | killer | kills | attackers in kill round (mean) | attackers in last 5 rounds (mean) | share killed by 3+ in last 5 | rounds first hit to death (median) |')
    print('|---|---|---|---|---|---|---|')
    for res in 'LW':
        for who in ('us', 'them'):
            A = agg[(res, who)]
            n = len(A['last5'])
            print(f"| {'losses' if res == 'L' else 'wins'} | {who} | {n} | {mean(A['kill_round']):.2f} | {mean(A['last5']):.2f} | "
                  f"{sum(1 for x in A['last5'] if x >= 3)/max(1,n):.2f} | {med(A['ttk'])} |")
