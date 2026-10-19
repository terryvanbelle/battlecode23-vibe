# per game: enemy island-rounds in the par windows (<300) vs our par exchange; dedupe identical games
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
import collections
def rowsfor(ms):
    seen=set(); out=[]
    for m,o in ms:
        G=games(m); T={(r['game'],int(r['round']),r['side']):r for r in rd(m,'timeline')}
        dd=collections.Counter()
        for d in rd(m,'deaths'):
            if d['type']=='L': dd[(d['game'],(int(d['round'])-1)//10*10,d['side'])]+=1
        for gi,g in G.items():
            sig=(o,g['map'],g['rounds'],g['won'])
            if sig in seen: continue
            seen.add(sig)
            us=g['us'];th=other(us)
            s=collections.Counter()
            for r0 in range(10,min(300,g['rounds']),10):
                a=T.get((gi,r0,us)); b=T.get((gi,r0,th))
                if not a or not b: continue
                la,lb=int(a['alive_L']),int(b['alive_L'])
                if la+lb<4: continue
                ratio=(la+1)/(lb+1)
                if not (0.8<=ratio<=1.25): continue
                k='isl' if int(b['islands'])>0 else 'noisl'
                s[k+'_w']+=1; s[k+'_u']+=dd[(gi,r0,us)]; s[k+'_t']+=dd[(gi,r0,th)]
                s['ourisl_w']+=int(a['islands'])>0
            out.append((m,gi,o,g['map'],g['won'],s))
    return out
AL=[(m,'AL') for m in ['9478']+AL_RANKED]
SG=[(m,o) for m,o in LOOSE.items() if o in STRONG]
for lab,ms in [('AL',AL),('S4',SG)]:
    R=rowsfor(ms)
    tot=collections.Counter()
    for m,gi,o,mp,w,s in R: tot.update(s)
    print(f"{lab} unique games {len(R)} (wins {sum(1 for r in R if r[4])}): par<300 windows where enemy holds >=1 island: {tot['isl_w']} deaths {tot['isl_u']}-{tot['isl_t']} exch {tot['isl_t']/max(1,tot['isl_u']):.2f} | enemy holds none: {tot['noisl_w']} deaths {tot['noisl_u']}-{tot['noisl_t']} exch {tot['noisl_t']/max(1,tot['noisl_u']):.2f} | we hold>=1 in {tot['ourisl_w']}")
    for w in [0,1]:
        t=collections.Counter()
        for m,gi,o,mp,ww,s in R:
            if ww==w: t.update(s)
        print(f"   {'wins' if w else 'losses'}: enemy-island windows {t['isl_w']} deaths {t['isl_u']}-{t['isl_t']} | none {t['noisl_w']} deaths {t['noisl_u']}-{t['noisl_t']} exch {t['noisl_t']/max(1,t['noisl_u']):.2f}")
