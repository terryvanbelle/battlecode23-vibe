# launcher deaths: geometry (island, cloud, enemy HQ, prog) and our telemetry at death, by global army state
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
import collections
def hqpos(m):
    out=collections.defaultdict(set)
    for r in rd(m,'hq'): out[(r['game'],r['side'])].add((int(r['x']),int(r['y'])))
    return out
def collect(matches, filt=lambda g:True):
    rows=[]
    for m,opp in matches:
        G=games(m); T={(r['game'],int(r['round']),r['side']):r for r in rd(m,'timeline')}; HQ=hqpos(m)
        for d in rd(m,'deaths'):
            if d['type']!='L': continue
            g=G[d['game']]
            if not filt(g): continue
            us=g['us']; th=other(us); mine=d['side']==us
            r=int(d['round']); r0=max(10,(r-1)//10*10)
            a=T.get((d['game'],r0,us)); b=T.get((d['game'],r0,th))
            if not a or not b: continue
            la,lb=int(a['alive_L']),int(b['alive_L']); ratio=(la+1)/(lb+1)
            bk='par' if 0.8<=ratio<=1.25 else ('ahead' if ratio>1.25 else 'behind')
            x,y=int(d['x']),int(d['y'])
            mp=mapread.load(g['map']); W=mp['W']
            it=mapread.island_tiles(g['map'])
            di=min((x-ix)**2+(y-iy)**2 for v in it.values() for ix,iy in v)
            cl=mp['clouds'][x+y*W]==1
            vside=d['side']; kside=other(vside)
            dkhq=min(((x-hx)**2+(y-hy)**2 for hx,hy in HQ[(d['game'],kside)]),default=999)   # killer's HQ
            dvhq=min(((x-hx)**2+(y-hy)**2 for hx,hy in HQ[(d['game'],vside)]),default=999)
            p=float(d['prog']) if d['prog'] else None
            if p is not None and vside=='B': p=1-p   # prog from the victim's side: 0 = victim HQ
            kisl=int((b if mine else a)['islands'])   # islands held by the killer side at window start
            visl=int((a if mine else b)['islands'])
            rows.append(dict(opp=opp,mine=mine,bk=bk,early=r<300,r=r,di=di,cl=cl,dkhq=dkhq,dvhq=dvhq,p=p,kisl=kisl,visl=visl,
                             code=decode(d['last_code']),cause=d['cause'],hp=int(d['hp_before'] or 0),age=int(d['age'])))
    return rows
def share(rows,f): return (sum(1 for r in rows if f(r))/len(rows)) if rows else float('nan')
def report(rows,label):
    for mine in [True,False]:
        rs=[r for r in rows if r['mine']==mine]
        n=len(rs)
        if not n: continue
        print(f"{label} {'OUR' if mine else 'THEIR'} L deaths n={n}: isl r2<=4 {share(rs,lambda r:r['di']<=4):.2f} "
              f"(killer holds>=1 isl {share(rs,lambda r:r['di']<=4 and r['kisl']>0):.2f}, victim holds {share(rs,lambda r:r['di']<=4 and r['visl']>0):.2f}) "
              f"cloud {share(rs,lambda r:r['cl']):.2f} killerHQ r2<=34 {share(rs,lambda r:r['dkhq']<=34):.2f} r2<=9 {share(rs,lambda r:r['dkhq']<=9):.2f} "
              f"own-HQ r2<=34 {share(rs,lambda r:r['dvhq']<=34):.2f} prog>.6 {share(rs,lambda r:r['p'] is not None and r['p']>0.6):.2f} prog<.4 {share(rs,lambda r:r['p'] is not None and r['p']<0.4):.2f} hq_aura {share(rs,lambda r:r['cause']=='hq_aura'):.2f}")
AL=[(m,'AL') for m in ['9478']+AL_RANKED]
SG=[(m,o) for m,o in LOOSE.items() if o in STRONG]
if __name__=='__main__':
    for lab,ms,f in [('AL all',AL,lambda g:True),('AL loss',AL,lambda g:g['won']==0),('AL win',AL,lambda g:g['won']==1),('S4 all',SG,lambda g:True),('S4 loss',SG,lambda g:g['won']==0)]:
        rows=collect(ms,f)
        for bk in ['par']:
            for early in [True,False]:
                report([r for r in rows if r['bk']==bk and r['early']==early],f'{lab} {bk} {"<300" if early else "300+"}')
        report(rows,f'{lab} ALL')
