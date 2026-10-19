import sys, statistics as st; sys.path.insert(0,'/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al')
from common import *
I,H=islands()
games_sel={(9478,0),(9478,5),(9478,7),(9904,5),(9904,7),(9509,1),(9514,1)}
ctrl={(9475,5),(9480,9),(9901,5),(9902,4),(9906,9)}
for label,sel in (('al level losses',games_sel),('strong level losses',ctrl)):
    acc=collections.defaultdict(list)
    for m,g in sorted(sel):
        G=games(m); info=G[g]; us=info['us']; th='B' if us=='A' else 'A'
        T=rows(m,'timeline'); t={}
        for r in T:
            if int(r['game'])==g: t.setdefault(int(r['round']),{})[r['side']]=r
        rs=sorted(t); E1=next(r for r in rs if int(t[r][th]['islands'])>=1)
        hq=[(x,y) for s,x,y in H[info['map']] if s==th]
        for d in rows(m,'deaths'):
            if int(d['game'])!=g or d['type']!='L': continue
            r=int(d['round']); who='them' if d['side']==th else 'us'
            ph='pre' if E1-150<=r<E1 else ('post' if E1<=r<E1+150 else None)
            if ph: acc[(who,ph)].append(int(d['age']))
    print(label, {k:(len(v), round(st.mean(v)), st.median(v)) for k,v in sorted(acc.items())})
