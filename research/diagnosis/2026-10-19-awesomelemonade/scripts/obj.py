import sys; sys.path.insert(0,'/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al')
from common import *
MS=[9478,9904,9509,9511,9514,9675,9701,9702,9703, 9475,9476,9479,9480,9901,9902,9905,9906]
DUP={(9702,0),(9702,2),(9703,1)}
agg=collections.defaultdict(collections.Counter)
for m in MS:
    G=games(m)
    T=rows(m,'timeline'); tl=collections.defaultdict(dict)
    for r in T: tl[int(r['game'])].setdefault(int(r['round']),{})[r['side']]=r
    per=collections.defaultdict(collections.Counter)
    for r in rows(m,'tele_states'):
        if r['type']!='L' or r['phase']!='all': continue
        g=int(r['game'])
        if r['side']!=G[g]['us']: continue
        code=int(r['code']); obj=(code>>3)&3
        per[g]['tot']+=int(r['turns']); per[g]['isl']+= int(r['turns']) if obj==1 else 0
    for g,info in G.items():
        if (m,g) in DUP or g not in per: continue
        us=info['us']; th='B' if us=='A' else 'A'; t=tl[g]
        eir=sum(int(t[r][th]['islands'])*10 for r in t)
        opp=info['opp'].split('.')[0]; grp='al' if opp=='awesomelemonade' else 'strong'
        k=(grp,'W' if info['won'] else 'L'); c=agg[k]
        c['n']+=1; c['tot']+=per[g]['tot']; c['isl']+=per[g]['isl']; c['eir']+=eir; c['zero']+= (per[g]['isl']==0 and eir>0); c['enemyheld']+= eir>0
        if grp=='al': print(m,g,info['map'],k[1],'L turns',per[g]['tot'],'enemy_island-obj turns',per[g]['isl'],'enemy island-rounds',eir)
for k,c in sorted(agg.items()): print(k,'n',c['n'],'isl-obj share %.3f'%(c['isl']/c['tot']),'isl-obj turns per enemy island-round %.2f'%(c['isl']/max(1,c['eir'])),'games with enemy islands but 0 isl-obj turns %d/%d'%(c['zero'],c['enemyheld']))
