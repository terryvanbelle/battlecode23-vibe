# Fire discipline per side, r <= RMAX (default 200), from sa_L. For launcher turns that start with an enemy launcher in
# range (enemy_L_16 > 0): share that hit a launcher (hitL16), share that fired at nothing / a carrier / did not fire.
# For turns that start with an enemy launcher at r2 17-20 only (enemy_L_20 > 0, enemy_L_16 == 0): share that moved,
# share that fired (step-in shot) and share that hit a launcher. Exposure: share of turns with enemy_L_16 > 0 where the
# launcher is outnumbered within r2 20 (enemy_L_20 > ally_L_20 + 1). Hits per contact turn = launcher hits / turns with
# enemy_L_20 > 0. Damage taken per contact turn is the other side's hits per our contact turn.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200


def fire(G, side):
    c = collections.Counter()
    for r in sa(G['m'], G['g'], side, 'L', RMAX):
        hitL = r['attacked'] and r['atk_hit'] == '1' and r['atk_target_type'] == 'L'
        if r['enemy_L_20'] > 0: c['contact'] += 1; c['hitL_all'] += bool(hitL)
        if r['enemy_L_16'] > 0:
            c['in16'] += 1; c['in16_hitL'] += bool(hitL); c['in16_nofire'] += not r['attacked']
            c['in16_out'] += r['enemy_L_20'] > r['ally_L_20'] + 1
            c['in16_moved'] += r['moved'] == 1
        elif r['enemy_L_20'] > 0:
            c['edge'] += 1; c['edge_moved'] += r['moved'] == 1; c['edge_fire'] += bool(r['attacked'])
            c['edge_hitL'] += bool(hitL)
    return c


if __name__ == '__main__':
    print(f'r <= {RMAX}')
    print('| game | res | in-range turns us/them | hitL share us/them | no fire us/them | moved us/them | outnumbered us/them | edge turns us/them | edge step-in hit us/them | L hits per contact turn us/them |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    agg = {r: collections.Counter() for r in 'WL'}
    f = lambda a, b: f"{a/b:.2f}" if b else '-'
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        res = 'W' if G['won'] else 'L'
        a, b = fire(G, G['us']), fire(G, G['them'])
        print(f"| {label(G)} | {res} | {a['in16']}/{b['in16']} | {f(a['in16_hitL'],a['in16'])}/{f(b['in16_hitL'],b['in16'])} | "
              f"{f(a['in16_nofire'],a['in16'])}/{f(b['in16_nofire'],b['in16'])} | {f(a['in16_moved'],a['in16'])}/{f(b['in16_moved'],b['in16'])} | "
              f"{f(a['in16_out'],a['in16'])}/{f(b['in16_out'],b['in16'])} | {a['edge']}/{b['edge']} | "
              f"{f(a['edge_hitL'],a['edge'])}/{f(b['edge_hitL'],b['edge'])} | {f(a['hitL_all'],a['contact'])}/{f(b['hitL_all'],b['contact'])} |")
        for k, v in a.items(): agg[res]['us_' + k] += v
        for k, v in b.items(): agg[res]['th_' + k] += v
    for res in 'LW':
        A = agg[res]
        print(f"{res} pooled: in-range turns us {A['us_in16']} them {A['th_in16']}; hitL share us {f(A['us_in16_hitL'],A['us_in16'])} them {f(A['th_in16_hitL'],A['th_in16'])}; "
              f"no fire us {f(A['us_in16_nofire'],A['us_in16'])} them {f(A['th_in16_nofire'],A['th_in16'])}; moved in range us {f(A['us_in16_moved'],A['us_in16'])} them {f(A['th_in16_moved'],A['th_in16'])}; "
              f"outnumbered in range us {f(A['us_in16_out'],A['us_in16'])} them {f(A['th_in16_out'],A['th_in16'])}; edge step-in hit us {f(A['us_edge_hitL'],A['us_edge'])} them {f(A['th_edge_hitL'],A['th_edge'])}; "
              f"edge moved us {f(A['us_edge_moved'],A['us_edge'])} them {f(A['th_edge_moved'],A['th_edge'])}; "
              f"L hits per contact turn us {f(A['us_hitL_all'],A['us_contact'])} them {f(A['th_hitL_all'],A['th_contact'])}")
