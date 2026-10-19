# HQ defence (hq.csv, 25-round buckets, r <= RMAX, default 300): for our HQs the share of HQ turns by build-loop stop
# code (p poor, t threatened: carrier withheld, c carrier cap, a anchor reserve, s no spawn tile), the first bucket
# whose pressure34 (enemy fighter-rounds within r2 34 of the HQ) reaches 100 ("pressed", Comms pressed bit), the pressure
# summed over the window for our HQs and theirs, carriers built by our HQs in the window, and spawn kills (deaths.csv
# spawn_kill: died within 1 round of birth) of our units by RMAX.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 300

if __name__ == '__main__':
    print(f'r <= {RMAX}')
    print('| game | res | our HQ codes t / p / c | first pressed bucket (ours) | pressure34 on our HQs / theirs | C built us/them | L built us/them | spawn kills us/them |')
    print('|---|---|---|---|---|---|---|---|')
    agg = {r: collections.Counter() for r in ('W', 'L')}
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        res = 'W' if G['won'] else 'L'
        codes = collections.Counter(); first = None; pr = {G['us']: 0, G['them']: 0}
        bc = {G['us']: 0, G['them']: 0}; bl = {G['us']: 0, G['them']: 0}
        for r in rd(G['m'], 'hq'):
            if int(r['game']) != G['g'] or int(r['round']) > RMAX: continue
            s = r['side']; pr[s] += int(r['pressure34']); bc[s] += int(r['built_C']); bl[s] += int(r['built_L'])
            if s == G['us']:
                for kv in r['codes'].split(';'):
                    if '=' in kv: k, v = kv.split('='); codes[k] += int(v)
                if int(r['pressure34']) >= 100 and first is None: first = int(r['round'])
        tot = sum(codes.values()) or 1
        sk = collections.Counter(d['side'] for d in rd(G['m'], 'deaths') if int(d['game']) == G['g']
                                 and d['spawn_kill'] == '1' and int(d['round']) <= RMAX)
        print(f"| {label(G)} | {res} | {codes['t']/tot:.2f} / {codes['p']/tot:.2f} / {codes['c']/tot:.2f} | "
              f"{('r' + str(first)) if first else '-'} | {pr[G['us']]} / {pr[G['them']]} | {bc[G['us']]}/{bc[G['them']]} | "
              f"{bl[G['us']]}/{bl[G['them']]} | {sk[G['us']]}/{sk[G['them']]} |")
        a = agg[res]; a['n'] += 1; a['t'] += codes['t'] / tot; a['pressed'] += first is not None
        a['pr_us'] += pr[G['us']]; a['pr_th'] += pr[G['them']]
    for res in ('L', 'W'):
        a = agg[res]; n = a['n']
        print(f"{res}: mean t share {a['t']/n:.2f}; our HQ pressed by r{RMAX} in {a['pressed']}/{n}; "
              f"mean pressure34 on our HQs {a['pr_us']/n:.0f} vs on theirs {a['pr_th']/n:.0f}")
