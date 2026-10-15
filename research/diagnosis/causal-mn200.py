import csv, glob, os
from collections import defaultdict
R=200
rows=[]
for p in sorted(glob.glob('gauntlet/*-panel-*')):
    if not os.path.exists(p+'/results.csv'): continue
    res=defaultdict(dict)
    for r in csv.DictReader(open(p+'/results.csv')):
        if r['bot_result'] in('win','loss'): res[int(r['match'])][int(r['game'])]=r
    for m,gs in res.items():
        tl=defaultdict(lambda: defaultdict(dict))
        for r in csv.DictReader(open(f'matches/{m}/extract/timeline.csv')):
            g=int(r['game']); rd=int(r['round'])
            if g in gs and rd<=R: tl[g][rd][r['side']]=r
        dth=defaultdict(lambda: defaultdict(int))
        dp=f'matches/{m}/extract/deaths.csv'
        for g,r in gs.items():
            us=r['bot_side']; th='B' if us=='A' else 'A'
            rr=sorted(tl[g]); 
            if not rr: continue
            last=tl[g][rr[-1]]
            if us not in last or th not in last: continue
            f=lambda s,k: float(last[s][k] or 0)
            crU=sum(float(tl[g][x][us]['alive_C']) for x in rr if us in tl[g][x])*10
            crT=sum(float(tl[g][x][th]['alive_C']) for x in rr if th in tl[g][x])*10
            rows.append(dict(cell=(r['opponent'],r['map'],us,r['seed']),win=r['bot_result']=='win',
              dMn=f(us,'coll_Mn')-f(th,'coll_Mn'), MnU=f(us,'coll_Mn'), MnT=f(th,'coll_Mn'),
              CbU=f(us,'built_C'), CaU=f(us,'alive_C'), CdU=f(us,'built_C')-f(us,'alive_C'),
              CbT=f(th,'built_C'), CaT=f(th,'alive_C'), CdT=f(th,'built_C')-f(th,'alive_C'),
              crU=crU, crT=crT, effU=f(us,'coll_Mn')/max(1,crU)*100, effT=f(th,'coll_Mn')/max(1,crT)*100,
              LbU=f(us,'built_L'), LaU=f(us,'alive_L'), LbT=f(th,'built_L'), killsU=f(us,'kills'), killsT=f(th,'kills'),
              AdU=f(us,'coll_Ad')))
by=defaultdict(list)
for x in rows: by[x['cell']].append(x)
keys=[k for k in rows[0] if k not in('cell','win')]
acc=defaultdict(list); nc=0
for c,xs in by.items():
    W=[x for x in xs if x['win']]; L=[x for x in xs if not x['win']]
    if not W or not L: continue
    nc+=1
    for k in keys: acc[k].append(sum(x[k] for x in L)/len(L)-sum(x[k] for x in W)/len(W))
allL=[x for x in rows if not x['win']]
print(f'r{R}: {nc} mixed cells; loss-minus-win within cell (mean over cells); all-loss mean in brackets')
for k in keys:
    v=acc[k]; m=sum(v)/len(v); sd=(sum((a-m)**2 for a in v)/(len(v)-1))**.5/len(v)**.5
    print(f'{k:8s} {m:+8.2f} +-{sd:5.2f}   [{sum(x[k] for x in allL)/len(allL):8.2f}]')
