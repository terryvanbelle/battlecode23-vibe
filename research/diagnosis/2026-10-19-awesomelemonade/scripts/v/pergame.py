# Per-game classification of AL games (dedup): gap at r250 split production/deaths, Mn gap, carriers lost by r150,
# AL first island round (timeline islands>0), armies at that round, result.
import sys,os,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
ms=[('9904','AL'),('9478','AL')]+[(m,'AL') for m in AL_RANKED]
if len(sys.argv)>1 and sys.argv[1]=='S4': ms=[(m,o) for m,o in ECO.items() if o!='AL']
seen=set()
for m,o in ms:
    G=games(m); TL=rd(m,'timeline')
    T={(r['game'],int(r['round']),r['side']):r for r in TL}
    for gi,g in sorted(G.items(),key=lambda x:int(x[0])):
        sig=(o,g['map'],g['rounds'],g['won'])
        if sig in seen: continue
        seen.add(sig)
        us,th=g['us'],other(g['us'])
        def gap(R):
            a=T.get((gi,R,us)); b=T.get((gi,R,th))
            if not a or not b: return None
            bu,bt,au,at=int(a['built_L']),int(b['built_L']),int(a['alive_L']),int(b['alive_L'])
            return (au-at,bu-bt,(bt-at)-(bu-au),int(a['coll_Mn'])-int(b['coll_Mn']),int(a['alive_C'])-int(b['alive_C']))
        fi=next((R for R in range(10,g['rounds']+10,10) if (gi,R,th) in T and int(T[(gi,R,th)]['islands'])>0),None)
        fu=next((R for R in range(10,g['rounds']+10,10) if (gi,R,us) in T and int(T[(gi,R,us)]['islands'])>0),None)
        lev=None
        if fi and (gi,fi,us) in T:
            a,b=int(T[(gi,fi,us)]['alive_L']),int(T[(gi,fi,th)]['alive_L']); lev=f"{a}/{b}"
        cl=sum(1 for d in rd(m,'deaths') if d['game']==gi and d['side']==us and d['type']=='C' and int(d['round'])<=150)
        g2=gap(200); g3=gap(250)
        f=lambda x: 'end' if x is None else f"{x[0]:+d}={x[1]:+d}p{x[2]:+d}d Mn{x[3]:+d} C{x[4]:+d}"
        print(f"{m} g{gi} {g['map']:18s} {'WIN ' if g['won'] else 'loss'} r{g['rounds']:4d} | r200 {f(g2):28s} | r250 {f(g3):30s} | C lost<=150 {cl:2d} | AL isl@{fi} (L {lev}) ours@{fu}")
