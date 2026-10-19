import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
import collections
AL=[(m,'AL') for m in ['9478']+AL_RANKED]
SG=[(m,o) for m,o in LOOSE.items() if o in STRONG]
def go(ms,f,label,R=300):
    seen=set(); s=collections.Counter(); n=0
    for m,o in ms:
        G=games(m); T={(r['game'],int(r['round']),r['side']):r for r in rd(m,'timeline')}
        for gi,g in G.items():
            sig=(o,g['map'],g['rounds'],g['won'])
            if sig in seen or not f(g): continue
            seen.add(sig)
            a=T.get((gi,R,g['us'])); b=T.get((gi,R,other(g['us'])))
            if not a or not b: continue
            n+=1
            s['bu']+=int(a['built_L']); s['bt']+=int(b['built_L']); s['au']+=int(a['alive_L']); s['at']+=int(b['alive_L'])
    du=s['bu']-s['au']; dt=s['bt']-s['at']
    print(f"{label} r{R} n={n}: built L {s['bu']/n:.1f} vs {s['bt']/n:.1f} | died {du/n:.1f} vs {dt/n:.1f} | alive {s['au']/n:.1f} vs {s['at']/n:.1f} | gap from production {(s['bu']-s['bt'])/n:+.1f}, from deaths {(dt-du)/n:+.1f}")
for R in [200,300]:
    go(AL,lambda g:g['won']==0,'AL loss',R); go(AL,lambda g:g['won']==1,'AL win',R); go(SG,lambda g:g['won']==0,'S4 loss',R); go(SG,lambda g:g['won']==1,'S4 win',R)
