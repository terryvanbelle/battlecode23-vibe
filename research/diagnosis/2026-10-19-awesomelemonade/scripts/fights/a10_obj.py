import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
import collections
AL=[(m,'AL') for m in ['9478']+AL_RANKED]
SG=[(m,o) for m,o in LOOSE.items() if o in STRONG]
def go(ms,f,label):
    seen=set(); c=collections.Counter(); n=0
    for m,o in ms:
        G=games(m); T={(r['game'],int(r['round']),r['side']):r for r in rd(m,'timeline')}
        dup={gi for gi,g in G.items() if (o,g['map'],g['rounds'],g['won']) in seen}
        for gi,g in G.items(): seen.add((o,g['map'],g['rounds'],g['won']))
        for d in rd(m,'deaths'):
            g=G[d['game']]
            if d['game'] in dup or d['type']!='L' or not f(g) or d['side']!=g['us']: continue
            r=int(d['round'])
            if r>=300: continue
            r0=max(10,(r-1)//10*10); a=T.get((d['game'],r0,g['us'])); b=T.get((d['game'],r0,other(g['us'])))
            ratio=(int(a['alive_L'])+1)/(int(b['alive_L'])+1)
            if not 0.8<=ratio<=1.25: continue
            k=decode(d['last_code'])
            if not k: c['none']+=1; n+=1; continue
            p=float(d['prog']) if d['prog'] else 0.5
            if g['us']=='B': p=1-p
            if k['obj']==2: kind='mid' if int(d['id'])%3==0 and 0.3<=p<=0.7 else 'siege/raid'
            else: kind={0:'sighting',1:'island',3:'centre/mend'}[k['obj']]
            c[kind]+=1; c[kind+'_'+k['mode']]+=1; n+=1
    print(label,'n',n,' '.join(f"{k} {c[k]/n:.2f}" for k in ['sighting','mid','siege/raid','island','centre/mend','none']),'| marching deaths by kind:',' '.join(f"{k} {c[k+'_M']}" for k in ['sighting','mid','siege/raid','island','centre/mend']))
go(AL,lambda g:g['won']==0,'AL loss par<300'); go(AL,lambda g:g['won']==1,'AL win par<300'); go(SG,lambda g:g['won']==0,'S4 loss par<300'); go(SG,lambda g:g['won']==1,'S4 win par<300')
