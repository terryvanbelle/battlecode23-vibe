import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
import collections
AL=[(m,'AL') for m in ['9478']+AL_RANKED]
SG=[(m,o) for m,o in LOOSE.items() if o in STRONG]
def engs(ms,filt):
    out=[]
    for m,o in ms:
        G=games(m)
        for e in rd(m,'engagements'):
            g=G[e['game']]
            if not filt(g): continue
            d=eng_us(e,g['us']); d['opp']=o; d['map']=g['map']; d['won']=g['won']; d['m']=m
            out.append(d)
    return out
def rep(E,label):
    n=len(E)
    if n==0: print(label,'n=0'); return
    fhU=sum(1 for e in E if e['fh']=='U'); fhT=sum(1 for e in E if e['fh']=='T')
    won=sum(1 for e in E if e['res']=='U'); lost=sum(1 for e in E if e['res']=='T')
    jU=sum(e['joinU'] for e in E); jT=sum(e['joinT'] for e in E)
    kU=sum(e['kills_by_U'] for e in E); kT=sum(e['kills_by_T'] for e in E)
    pkd=sum(e['peakU']-e['peakT'] for e in E)/n
    how=collections.Counter((e['fh'],e['fh_how']) for e in E)
    # first hit -> result
    fw=sum(1 for e in E if e['fh']=='U' and e['res']=='U'); fl=sum(1 for e in E if e['fh']=='T' and e['res']=='U')
    print(f"{label}: n={n} won {won} lost {lost} | first hit us {fhU} them {fhT} | won when we hit first {fw}/{fhU}, when they did {fl}/{fhT} | join us {jU} them {jT} (per eng {(jU-jT)/n:+.2f}) | peak diff {pkd:+.2f} | kills {kU}-{kT} | fh_how U:"+','.join(f"{k[1]}{v}" for k,v in how.items() if k[0]=='U')+" T:"+','.join(f"{k[1]}{v}" for k,v in how.items() if k[0]=='T'))
for lab,ms,f in [('AL loss',AL,lambda g:g['won']==0),('AL win',AL,lambda g:g['won']==1),('S4 loss',SG,lambda g:g['won']==0),('S4 win',SG,lambda g:g['won']==1)]:
    E=engs(ms,f)
    L=[e for e in E if e['peakU']>=1 and e['peakT']>=1 and (e['kills_by_U']+e['kills_by_T'])>0]
    rep([e for e in L if e['nU0']==e['nT0']],lab+' par decisive')
    rep([e for e in L if e['nU0']==e['nT0'] and e['r0']<300],lab+' par decisive <300')
    rep([e for e in L if e['r0']<300],lab+' all decisive <300')
    rep([e for e in L if e['r0']<300 and max(e['peakU'],e['peakT'])<=4],lab+' small(peak<=4) <300')
    rep([e for e in L if e['r0']<300 and max(e['peakU'],e['peakT'])>=5],lab+' big(peak>=5) <300')
