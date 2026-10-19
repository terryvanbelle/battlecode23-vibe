# Army spread per side, r in [R0, R1] (default 20-200), from sa_L: share of launcher turns with no ally launcher within
# r2 20 (alone), mean allies within r2 20, and the number of launcher clusters per round (single linkage at r2 20,
# rounds with 4+ launchers alive). Group sizes: mean size of the cluster a launcher belongs to. The "par" line repeats
# the pooled numbers over rounds where both sides have 4+ launchers alive and the counts differ by at most 1 (so army
# size cannot explain the spread), with the share of the side's launchers in its largest cluster (big).
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
R0 = int(sys.argv[1]) if len(sys.argv) > 1 else 20
R1 = int(sys.argv[2]) if len(sys.argv) > 2 else 200


def clusters(pts):
    n = len(pts); par = list(range(n))
    def f(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if d2(pts[i], pts[j]) <= 20: par[f(i)] = f(j)
    return collections.Counter(f(i) for i in range(n))


def alive(G):
    rows = {s: collections.Counter(r['round'] for r in sa(G['m'], G['g'], s, 'L', R1)) for s in (G['us'], G['them'])}
    return rows


def spread(G, side, only=None):
    byr = collections.defaultdict(list); alone = n = al = 0
    for r in sa(G['m'], G['g'], side, 'L', R1):
        if r['round'] < R0: continue
        if only is not None and r['round'] not in only: continue
        byr[r['round']].append((r['x'], r['y']))
        n += 1; alone += r['ally_L_20'] == 0; al += r['ally_L_20']
    ncl = []; memb = []; big = []
    for rn, pts in byr.items():
        if len(pts) < 4 or rn % 5: continue
        c = clusters(pts); ncl.append(len(c))
        memb.extend(v for v in c.values() for _ in range(v))
        big.append(max(c.values()) / len(pts))
    return dict(alone=alone / n if n else 0, allies=al / n if n else 0, ncl=sum(ncl) / len(ncl) if ncl else 0,
                grp=sum(memb) / len(memb) if memb else 0, big=sum(big) / len(big) if big else 0, n=n)


if __name__ == '__main__':
    print(f'r {R0}-{R1}')
    print('| game | res | alone us/them | allies r2 20 us/them | clusters per round us/them | mean group a launcher is in us/them | largest cluster share us/them |')
    print('|---|---|---|---|---|---|---|')
    agg = {r: collections.defaultdict(list) for r in 'WL'}
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        res = 'W' if G['won'] else 'L'
        a, b = spread(G, G['us']), spread(G, G['them'])
        print(f"| {label(G)} | {res} | {a['alone']:.2f}/{b['alone']:.2f} | {a['allies']:.1f}/{b['allies']:.1f} | {a['ncl']:.1f}/{b['ncl']:.1f} | {a['grp']:.1f}/{b['grp']:.1f} | {a['big']:.2f}/{b['big']:.2f} |")
        for k in a: agg[res]['us_' + k].append(a[k]); agg[res]['th_' + k].append(b[k])
    mean = lambda L: sum(L) / len(L)
    for res in 'LW':
        A = agg[res]
        print(res, ', '.join(f"{k} us {mean(A['us_'+k]):.2f} them {mean(A['th_'+k]):.2f}" for k in ('alone', 'allies', 'ncl', 'grp', 'big')))
    print('par rounds (both sides 4+ launchers alive, counts within 1):')
    pagg = {r: collections.defaultdict(list) for r in 'WL'}
    for G in all_games():
        res = 'W' if G['won'] else 'L'
        A = alive(G)
        par = {rn for rn in A[G['us']] if A[G['us']][rn] >= 4 and A[G['them']].get(rn, 0) >= 4
               and abs(A[G['us']][rn] - A[G['them']][rn]) <= 1}
        if len(par) < 20: continue
        a, b = spread(G, G['us'], par), spread(G, G['them'], par)
        print(f"   {label(G)} {res} par rounds {len(par)}: alone {a['alone']:.2f}/{b['alone']:.2f}, group {a['grp']:.1f}/{b['grp']:.1f}, largest cluster share {a['big']:.2f}/{b['big']:.2f}")
        for k in a: pagg[res]['us_' + k].append(a[k]); pagg[res]['th_' + k].append(b[k])
    for res in 'LW':
        A = pagg[res]
        if A['us_alone']:
            print(f"   {res} (games {len(A['us_alone'])}):", ', '.join(f"{k} us {mean(A['us_'+k]):.2f} them {mean(A['th_'+k]):.2f}" for k in ('alone', 'grp', 'big')))
