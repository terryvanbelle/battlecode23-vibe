# per 10-round window at global army par: damage dealt and launcher kills -> dmg per kill, game-bootstrap CIs
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
import collections, random
def per_game(matches, filt=lambda g:True, bucket='par', phase=None):
    out=[]
    for m,opp in matches:
        G=games(m); tl=rd(m,'timeline'); D=rd(m,'deaths')
        T={(r['game'],int(r['round']),r['side']):r for r in tl}
        dd=collections.Counter(); hpb=collections.Counter()
        for d in D:
            if d['type']!='L': continue
            k=(d['game'],(int(d['round'])-1)//10*10,d['side']); dd[k]+=1
        for gi,g in G.items():
            if not filt(g): continue
            us=g['us'];th=other(us); s=[0,0,0,0,0]  # ourL deaths, theirL deaths, dmg us, dmg them, windows
            for r0 in range(10,g['rounds']-10,10):
                a=T.get((gi,r0,us)); b=T.get((gi,r0,th)); a2=T.get((gi,r0+10,us)); b2=T.get((gi,r0+10,th))
                if not (a and b and a2 and b2): continue
                la,lb=int(a['alive_L']),int(b['alive_L'])
                if la+lb<4: continue
                ratio=(la+1)/(lb+1)
                bk='par' if 0.8<=ratio<=1.25 else ('ahead' if ratio>1.25 else 'behind')
                if bk!=bucket: continue
                if phase=='<300' and r0>=300: continue
                if phase=='300+' and r0<300: continue
                s[0]+=dd[(gi,r0,us)]; s[1]+=dd[(gi,r0,th)]
                s[2]+=int(a2['dmg_dealt'])-int(a['dmg_dealt']); s[3]+=int(b2['dmg_dealt'])-int(b['dmg_dealt']); s[4]+=1
            if s[4]: out.append(s)
    return out
def summ(rows,label):
    S=[sum(r[i] for r in rows) for i in range(5)]
    def stat(rs):
        T=[sum(r[i] for r in rs) for i in range(5)]
        return (T[1]/T[0] if T[0] else 0, T[2]/T[3] if T[3] else 0, (T[2]/T[1]) if T[1] else 0, (T[3]/T[0]) if T[0] else 0)
    st=stat(rows); random.seed(1); bs=[stat([random.choice(rows) for _ in rows]) for _ in range(2000)]
    ci=lambda i: (sorted(b[i] for b in bs)[50], sorted(b[i] for b in bs)[1949])
    c=[ci(i) for i in range(4)]
    print(f'{label}: games {len(rows)} windows {S[4]} | deaths ours {S[0]} theirs {S[1]} exch {st[0]:.2f} [{c[0][0]:.2f},{c[0][1]:.2f}] | dmg ours {S[2]} theirs {S[3]} ratio {st[1]:.2f} [{c[1][0]:.2f},{c[1][1]:.2f}] | dmg/kill ours {st[2]:.0f} [{c[2][0]:.0f},{c[2][1]:.0f}] theirs {st[3]:.0f} [{c[3][0]:.0f},{c[3][1]:.0f}]')
if __name__=='__main__':
    AL=[(m,'AL') for m in ['9478']+AL_RANKED]
    SG=[(m,o) for m,o in LOOSE.items() if o in STRONG]
    WK=[(m,o) for m,o in LOOSE.items() if o not in STRONG and o!='AL']
    for ph in [None,'<300','300+']:
      for bk in ['par','ahead','behind']:
        print('==',bk,ph or 'all')
        summ(per_game(AL,bucket=bk,phase=ph),'AL n31')
        summ(per_game(AL,lambda g:g['won']==0,bucket=bk,phase=ph),'AL losses')
        summ(per_game(AL,lambda g:g['won']==1,bucket=bk,phase=ph),'AL wins')
        summ(per_game(SG,bucket=bk,phase=ph),'strong4 n40')
        for o in ['jmerle','vrangr1','pranayagra','NotLLeon']:
            summ(per_game([(m,x) for m,x in SG if x==o],bucket=bk,phase=ph),'  '+o)
        summ(per_game(WK,bucket=bk,phase=ph),'weak5 n50')
