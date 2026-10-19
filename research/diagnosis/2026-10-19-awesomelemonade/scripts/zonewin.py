import sys; sys.path.insert(0,'/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al')
from common import *
I,H=islands()
sel=[(9478,0),(9478,5),(9478,7),(9904,5),(9904,7),(9509,1),(9514,1),(9478,9),(9703,0),(9703,2)]
tot=collections.Counter()
for m,g in sel:
    G=games(m); info=G[g]; us=info['us']; th='B' if us=='A' else 'A'; mp=info['map']
    t={}
    for r in rows(m,'timeline'):
        if int(r['game'])==g: t.setdefault(int(r['round']),{})[r['side']]=r
    rs=sorted(t); E1=next(r for r in rs if int(t[r][th]['islands'])>=1)
    hq=[(x,y) for s,x,y in H[mp] if s==th]; ohq=[(x,y) for s,x,y in H[mp] if s==us]
    fi=min(I[mp], key=lambda i: min(d2(s,h) for s in I[mp][i] for h in hq)); sq=I[mp][fi]
    c=collections.Counter()
    for d in rows(m,'deaths'):
        if int(d['game'])!=g or d['type']!='L': continue
        r=int(d['round'])
        if not (E1<=r<E1+150): continue
        p=(int(d['x']),int(d['y'])); z='zone' if min(d2(p,s) for s in sq)<=36 else 'out'
        c[('us' if d['side']==us else 'them')+'_'+z]+=1
        if d['side']==us: c['us_prog_sum']+=float(d['prog'])
    dHQ=min(d2(s,h) for s in sq for h in hq)**.5
    print(m,g,mp,'W' if info['won'] else 'L','E1',E1,'first isl',fi,'area',len(sq),'d(its HQ) %.1f'%dHQ,'L deaths E1..E1+150 in r2<=36 of it us/them %d/%d, elsewhere %d/%d'%(c['us_zone'],c['them_zone'],c['us_out'],c['them_out']),'our mean prog %.2f'%(c['us_prog_sum']/max(1,c['us_zone']+c['us_out'])))
    if not info['won']: tot.update(c)
print('level losses total',dict(tot))
