# Launcher gap decomposition (ours minus theirs) = production gap - deaths gap, by group, at several rounds.
import sys,os,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
GR={'AL-eco3':[('9904','AL')],'AL-loose1+ranked':[('9478','AL')]+[(m,'AL') for m in AL_RANKED],
    'S4-eco3':[(m,o) for m,o in ECO.items() if o!='AL'],'S4-loose1':[(m,o) for m,o in LOOSE.items() if o in STRONG]}
for name,ms in GR.items():
  for won in (0,1):
    seen=set(); rows_=collections.defaultdict(list)
    for m,o in ms:
        G=games(m); T={(r['game'],int(r['round']),r['side']):r for r in rd(m,'timeline')}
        for gi,g in G.items():
            sig=(o,g['map'],g['rounds'],g['won'])
            if sig in seen or g['won']!=won: continue
            seen.add(sig)
            for R in (150,200,250,300):
                a=T.get((gi,R,g['us'])); b=T.get((gi,R,other(g['us'])))
                if not a or not b: continue
                bu,bt,au,at=int(a['built_L']),int(b['built_L']),int(a['alive_L']),int(b['alive_L'])
                rows_[R].append((bu-bt,(bt-at)-(bu-au),au-at,int(a['coll_Mn'])-int(b['coll_Mn']),int(a['kills']),int(b['kills'])))
    for R in (150,200,250,300):
        v=rows_[R]; n=len(v)
        if not n: continue
        s=[sum(x[k] for x in v)/n for k in range(4)]
        att=sum(1 for x in v if x[2]<=-3 and -x[1]>=-x[0]); 
        print(f"{name} {'win ' if won else 'loss'} r{R} n={n}: alive gap {s[2]:+.1f} = production {s[0]:+.1f} + deaths {s[1]:+.1f} | coll_Mn gap {s[3]:+.0f} | games behind>=3 with deaths>=production share {att}/{sum(1 for x in v if x[2]<=-3)}")
