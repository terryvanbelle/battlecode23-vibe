import sys; sys.path.insert(0,'/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al')
from common import *
I,H=islands()
Z=int(sys.argv[1]) if len(sys.argv)>1 else 25
MS=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else list(AL)
DUP={(9702,0),(9702,2),(9703,1)}
def per_game(m):
    G=games(m); T=rows(m,'timeline'); E=rows(m,'engagements'); Dd=rows(m,'deaths')
    tl=collections.defaultdict(dict)
    for r in T: tl[int(r['game'])].setdefault(int(r['round']),{})[r['side']]=r
    res=[]
    for g,info in sorted(G.items()):
        if (m,g) in DUP: continue
        us=info['us']; th='B' if us=='A' else 'A'; t=tl[g]; rs=sorted(t); mp=info['map']
        E1=next((r for r in rs if int(t[r][th]['islands'])>=1),None)
        O1=next((r for r in rs if int(t[r][us]['islands'])>=1),None)
        hq=[(x,y) for s,x,y in H[mp] if s==th]
        fi=min(I[mp], key=lambda i: min(d2(s,h) for s in I[mp][i] for h in hq))
        sq=I[mp][fi]
        def near(x,y): return min(d2((x,y),s) for s in sq)<=Z
        agg=collections.defaultdict(lambda: collections.Counter())
        if E1 is not None:
            for e in E[0:]:
                if int(e['game'])!=g: continue
                r0=int(e['r0'])
                if r0<E1: continue
                zone='fort' if near(int(e['x0']),int(e['y0'])) else 'open'
                nu,nt=int(e['nA0' if us=='A' else 'nB0']),int(e['nB0' if us=='A' else 'nA0'])
                par = 'par' if abs(nu-nt)<=1 else ('ahead' if nu>nt else 'behind')
                for k in (zone, zone+'_'+par):
                    c=agg[k]; c['n']+=1; c['nu']+=nu; c['nt']+=nt
                    c['du']+=float(e['dmg_by_'+us]); c['dt']+=float(e['dmg_by_'+th])
                    c['ku']+=int(e['kills_by_'+us]); c['kt']+=int(e['kills_by_'+th])
                    c['won']+= e['result']==us; c['lost']+= e['result']==th
            for d in Dd:
                if int(d['game'])!=g or d['type']!='L': continue
                if int(d['round'])<E1: continue
                zone='fort' if near(int(d['x']),int(d['y'])) else 'open'
                who='Lu' if d['side']==us else 'Lt'
                agg[zone][who]+=1
                if d['side']==us:
                    code=int(d['last_code']) if d['last_code'] not in ('','-') else -1
                    obj=(code>>3)&3 if code>=0 else -1
                    agg[zone]['Lu_obj%d'%obj]+=1
        Lat = (int(t[E1][us]['alive_L']),int(t[E1][th]['alive_L'])) if E1 else None
        res.append(dict(m=m,g=g,map=mp,won=info['won'],opp=info['opp'],E1=E1,O1=O1,fi=fi,Lat=Lat,agg=agg,rounds=info['rounds']))
    return res
if __name__=='__main__':
    tot=collections.defaultdict(collections.Counter)
    for m in MS:
        for r in per_game(m):
            if r['E1'] is None: continue
            key=('W' if r['won'] else 'L')
            for z,c in r['agg'].items(): tot[(key,z)].update(c)
            f=r['agg']['fort']; o=r['agg']['open']
            print(r['m'],r['g'],r['map'],'W' if r['won'] else 'L','E1',r['E1'],'O1',r['O1'],'fi',r['fi'],'L@E1',r['Lat'],
                  'fort n%d du%d ku%d dt%d kt%d Lu%d Lt%d isl_obj_deaths%d'%(f['n'],f['du'],f['ku'],f['dt'],f['kt'],f['Lu'],f['Lt'],f['Lu_obj1']),
                  '| open n%d du%d ku%d dt%d kt%d Lu%d Lt%d'%(o['n'],o['du'],o['ku'],o['dt'],o['kt'],o['Lu'],o['Lt']))
    print('--- totals')
    for (k,z),c in sorted(tot.items()):
        dpk_u=c['du']/c['ku'] if c['ku'] else float('nan'); dpk_t=c['dt']/c['kt'] if c['kt'] else float('nan')
        print(k,z,'n',c['n'],'nu/nt %d/%d'%(c['nu'],c['nt']),'dmg/kill us %.0f them %.0f'%(dpk_u,dpk_t),'kills us %d them %d'%(c['ku'],c['kt']),'engW %d engL %d'%(c['won'],c['lost']),'Ldeaths us %d them %d'%(c['Lu'],c['Lt']), 'our L deaths by obj', {o:c['Lu_obj%d'%o] for o in (-1,0,1,2,3)})
