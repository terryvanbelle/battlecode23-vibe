# c_eco3 panel, 4/5-island maps: result, enemy first island round (1+ islands) and first 2+ (3+ on 5-island) round,
# armies at the 1-island round; how many games ISLE_MARGIN_SMALL=2 would move the drain trigger earlier.
import sys,os,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
ms=['9901','9902','9903','9904','9905','9906','9907','9908','9909','9910']
c=collections.Counter()
for m in ms:
    G=games(m); TL=rd(m,'timeline'); opp=None
    T={(r['game'],int(r['round']),r['side']):r for r in TL}
    isl={r['game']:int(r['islands']) for r in rd(m,'games') if r['team']=='vibe23'}
    for gi,g in G.items():
        n=isl[gi]
        if n>5: continue
        th=other(g['us']); now=2 if n==4 else 3
        f1=next((R for R in range(10,g['rounds']+10,10) if (gi,R,th) in T and int(T[(gi,R,th)]['islands'])>=now-1),None)
        f2=next((R for R in range(10,g['rounds']+10,10) if (gi,R,th) in T and int(T[(gi,R,th)]['islands'])>=now),None)
        lev=f"{T[(gi,f1,g['us'])]['alive_L']}/{T[(gi,f1,th)]['alive_L']}" if f1 else '-'
        moved=f1 is not None and (f2 is None or f2-f1>=30)
        c[('moved' if moved else 'same', g['won'])]+=1
        if f1: print(f"{m} g{gi} {g['map']:15s} n={n} {'WIN ' if g['won'] else 'loss'} r{g['rounds']}: enemy >= {now-1} isl @r{f1} (L {lev}), >= {now} @r{f2}")
print(dict(c))
