import sys; sys.path.insert(0,'/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al')
from common import *
MS=[9478,9904,9509,9511,9514,9675,9701,9702,9703, 9475,9476,9479,9480,9901,9902,9905,9906]
DUP={(9702,0),(9702,2),(9703,1)}
agg=collections.defaultdict(collections.Counter)
for m in MS:
    G=games(m); T=rows(m,'timeline')
    tl=collections.defaultdict(dict)
    for r in T: tl[int(r['game'])].setdefault(int(r['round']),{})[r['side']]=r
    for g,info in sorted(G.items()):
        if (m,g) in DUP: continue
        us=info['us']; th='B' if us=='A' else 'A'; t=tl[g]; rs=sorted(t)
        E1=next((r for r in rs if int(t[r][th]['islands'])>=1),None)
        if E1 is None: continue
        prev=0; drops=[]; ourdrops=[]; po=0
        for r in rs:
            e=int(t[r][th]['islands']); o=int(t[r][us]['islands'])
            if e<prev: drops.append(r)
            if o<po: ourdrops.append(r)
            prev=e; po=o
        opp=info['opp'].split('.')[0]; grp='al' if opp=='awesomelemonade' else 'strong'
        k=(grp,'W' if info['won'] else 'L'); c=agg[k]; c['n']+=1; c['drained_any']+= bool(drops); c['drained_by_E1+150']+= any(d<=E1+150 for d in drops); c['our_isl_lost']+=len(ourdrops); c['their_isl_lost']+=len(drops)
        if grp=='al' or drops: print(m,g,info['map'],k,'E1',E1,'their island drops at',drops[:5],'our island drops at',ourdrops[:5])
for k,c in sorted(agg.items()): print(k,dict(c))
