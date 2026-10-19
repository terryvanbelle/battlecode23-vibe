import sys; sys.path.insert(0,'/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al')
from common import *
MS=[9478,9904,9509,9511,9514,9675,9701,9702,9703, 9475,9476,9479,9480,9901,9902,9905,9906]
DUP={(9702,0),(9702,2),(9703,1),(9904,0)}  # 9904 g0 == 9478 g0
W=150
agg=collections.defaultdict(collections.Counter)
for m in MS:
    G=games(m); T=rows(m,'timeline'); E=rows(m,'engagements')
    tl=collections.defaultdict(dict)
    for r in T: tl[int(r['game'])].setdefault(int(r['round']),{})[r['side']]=r
    for g,info in sorted(G.items()):
        if (m,g) in DUP: continue
        us=info['us']; th='B' if us=='A' else 'A'; t=tl[g]; rs=sorted(t)
        E1=next((r for r in rs if int(t[r][th]['islands'])>=1),None)
        if E1 is None: continue
        lu,lt=int(t[E1][us]['alive_L']),int(t[E1][th]['alive_L'])
        if lt==0 or lu/lt<0.8: continue
        # cumulative dmg/kills from timeline at E1-W, E1, E1+W
        def cum(r,s,k):
            r=max(10,min(r,rs[-1])); r=r-r%10
            return float(t[r][s][k]) if r in t else 0.0
        pre=dict(du=cum(E1,us,'dmg_dealt')-cum(E1-W,us,'dmg_dealt'),ku=cum(E1,us,'kills')-cum(E1-W,us,'kills'),dt=cum(E1,th,'dmg_dealt')-cum(E1-W,th,'dmg_dealt'),kt=cum(E1,th,'kills')-cum(E1-W,th,'kills'))
        post=dict(du=cum(E1+W,us,'dmg_dealt')-cum(E1,us,'dmg_dealt'),ku=cum(E1+W,us,'kills')-cum(E1,us,'kills'),dt=cum(E1+W,th,'dmg_dealt')-cum(E1,th,'dmg_dealt'),kt=cum(E1+W,th,'kills')-cum(E1,th,'kills'))
        opp=info['opp'].split('.')[0]; grp='al' if opp=='awesomelemonade' else 'strong'
        Lend=(int(t[min(rs[-1],E1+W- (E1+W)%10)][us]['alive_L']),int(t[min(rs[-1],E1+W-(E1+W)%10)][th]['alive_L']))
        print(m,g,info['map'],grp,'W' if info['won'] else 'L','E1',E1,'L@E1 %d/%d'%(lu,lt),'L@E1+150 %d/%d'%Lend,'pre us %.0f/%d them %.0f/%d'%(pre['du'],pre['ku'],pre['dt'],pre['kt']),'post us %.0f/%d them %.0f/%d'%(post['du'],post['ku'],post['dt'],post['kt']))
        k=(grp,'W' if info['won'] else 'L')
        for ph,d in (('pre',pre),('post',post)):
            for x,v in d.items(): agg[k][ph+x]+=v
        agg[k]['n']+=1
for k,c in sorted(agg.items()):
    f=lambda a,b: c[a]/c[b] if c[b] else float('nan')
    print(k,'n',c['n'],'dmg/kill us pre %.0f post %.0f; them pre %.0f post %.0f; kills us/them pre %d/%d post %d/%d'%(f('predu','preku'),f('postdu','postku'),f('predt','prekt'),f('postdt','postkt'),c['preku'],c['prekt'],c['postku'],c['postkt']))
