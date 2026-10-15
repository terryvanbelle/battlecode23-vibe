import csv, glob, os
from collections import defaultdict, Counter
R=200
rows=[]; codesL=Counter(); codesW=Counter()
for p in sorted(glob.glob('gauntlet/*-panel-*')):
    if not os.path.exists(p+'/results.csv'): continue
    res=defaultdict(dict)
    for r in csv.DictReader(open(p+'/results.csv')):
        if r['bot_result'] in('win','loss'): res[int(r['match'])][int(r['game'])]=r
    for m,gs in res.items():
        D=defaultdict(list); E=defaultdict(list)
        for r in csv.DictReader(open(f'matches/{m}/extract/deaths.csv')):
            if int(r['round'])<=R and int(r['game']) in gs: D[int(r['game'])].append(r)
        for r in csv.DictReader(open(f'matches/{m}/extract/engagements.csv')):
            if int(r['r0'])<=R and int(r['game']) in gs: E[int(r['game'])].append(r)
        for g,r in gs.items():
            us=r['bot_side']; th='B' if us=='A' else 'A'; win=r['bot_result']=='win'
            pr=lambda x: float(x) if us=='A' else 1-float(x)
            x=dict(cell=(r['opponent'],r['map'],us,r['seed']),win=win)
            d=D[g]
            x['C_lost']=sum(1 for e in d if e['side']==us and e['type']=='C')
            x['C_lost_home']=sum(1 for e in d if e['side']==us and e['type']=='C' and pr(e['prog'])<0.5)
            x['C_lost_away']=x['C_lost']-x['C_lost_home']
            x['C_killed']=sum(1 for e in d if e['side']==th and e['type']=='C')
            x['L_lost']=sum(1 for e in d if e['side']==us and e['type']=='L')
            x['L_lost_away']=sum(1 for e in d if e['side']==us and e['type']=='L' and pr(e['prog'])>=0.5)
            x['L_killed']=sum(1 for e in d if e['side']==th and e['type']=='L')
            x['spawnkill_us']=sum(1 for e in d if e['side']==us and e['spawn_kill']=='1')
            x['C_cargo_lost']=sum(float(e['cargo_Mn'] or 0)+float(e['cargo_Ad'] or 0) for e in d if e['side']==us and e['type']=='C')
            e_=E[g]
            x['eng']=len(e_)
            x['eng_won']=sum(1 for e in e_ if e['result']==us); x['eng_lost']=sum(1 for e in e_ if e['result']==th)
            x['eng_away']=sum(1 for e in e_ if pr(e['prog0'])>=0.5)
            x['fh_us']=sum(1 for e in e_ if e['first_hit']==us)/max(1,len(e_))
            x['dN0']=sum(int(e['n'+us+'0'])-int(e['n'+th+'0']) for e in e_)/max(1,len(e_))
            f=min(e_,key=lambda e:int(e['r0'])) if e_ else None
            x['first_r0']=int(f['r0']) if f else R; x['first_won']=1 if f and f['result']==us else 0
            x['first_dN']=(int(f['n'+us+'0'])-int(f['n'+th+'0'])) if f else 0
            rows.append(x)
            for e in d:
                if e['side']==us and e['type']=='C': (codesW if win else codesL)[e['last_code']]+=1
by=defaultdict(list)
for x in rows: by[x['cell']].append(x)
keys=[k for k in rows[0] if k not in('cell','win')]
acc=defaultdict(list)
for c,xs in by.items():
    W=[x for x in xs if x['win']]; L=[x for x in xs if not x['win']]
    if not W or not L: continue
    for k in keys: acc[k].append((sum(x[k] for x in L)/len(L), sum(x[k] for x in W)/len(W)))
print(f'<= r{R}, {len(acc["eng"])} mixed cells: loss mean / win mean / diff +- se')
for k in keys:
    v=acc[k]; d=[a-b for a,b in v]; m=sum(d)/len(d); se=(sum((q-m)**2 for q in d)/(len(d)-1))**.5/len(d)**.5
    print(f'{k:13s} {sum(a for a,b in v)/len(v):7.2f} {sum(b for a,b in v)/len(v):7.2f} {m:+7.2f} +-{se:5.2f}')
tl=sum(codesL.values()); tw=sum(codesW.values())
print('our carrier last_code at death (all games): code lossshare winshare')
for c,_ in (codesL+codesW).most_common(10): print(f'  {c!r:6} {codesL[c]/tl:.2f} {codesW[c]/tw:.2f}')
