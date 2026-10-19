# share of each side's alive launchers that are in contact (timeline in_contact), per global army state
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
import collections
AL=[(m,'AL') for m in ['9478']+AL_RANKED]
SG=[(m,o) for m,o in LOOSE.items() if o in STRONG]
def run(ms,f,label):
    acc=collections.defaultdict(lambda:[0,0,0,0,0])
    for m,o in ms:
        G=games(m); T={(r['game'],int(r['round']),r['side']):r for r in rd(m,'timeline')}
        for gi,g in G.items():
            if not f(g): continue
            us=g['us'];th=other(us)
            for r0 in range(10,g['rounds'],10):
                a=T.get((gi,r0,us)); b=T.get((gi,r0,th))
                if not a or not b: continue
                la,lb=int(a['alive_L']),int(b['alive_L'])
                if la+lb<4: continue
                ratio=(la+1)/(lb+1)
                bk='par' if 0.8<=ratio<=1.25 else ('ahead' if ratio>1.25 else 'behind')
                ph='<300' if r0<300 else '300+'
                x=acc[(bk,ph)]; x[0]+=la; x[1]+=lb; x[2]+=int(a['in_contact']); x[3]+=int(b['in_contact']); x[4]+=1
    for k in [('par','<300'),('par','300+'),('behind','<300'),('ahead','<300')]:
        x=acc[k]
        if x[4]: print(f"{label} {k}: samples {x[4]} alive {x[0]/x[4]:.1f} vs {x[1]/x[4]:.1f} | in contact {x[2]/x[4]:.2f} vs {x[3]/x[4]:.2f} | share {x[2]/max(1,x[0]):.3f} vs {x[3]/max(1,x[1]):.3f}")
run(AL,lambda g:g['won']==0,'AL loss'); run(AL,lambda g:g['won']==1,'AL win'); run(SG,lambda g:g['won']==0,'S4 loss'); run(SG,lambda g:g['won']==1,'S4 win')
