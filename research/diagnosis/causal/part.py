import csv, glob, os
from collections import defaultdict
R=200; rows=[]
for p in sorted(glob.glob('gauntlet/*-panel-*')):
    if not os.path.exists(p+'/results.csv'): continue
    res=defaultdict(dict)
    for r in csv.DictReader(open(p+'/results.csv')):
        if r['bot_result'] in('win','loss'): res[int(r['match'])][int(r['game'])]=r
    for m,gs in res.items():
        E=defaultdict(list); T=defaultdict(dict)
        for r in csv.DictReader(open(f'matches/{m}/extract/engagements.csv')):
            if int(r['r0'])<=R and int(r['game']) in gs: E[int(r['game'])].append(r)
        for r in csv.DictReader(open(f'matches/{m}/extract/timeline.csv')):
            if int(r['game']) in gs and int(r['round'])<=R+10: T[int(r['game'])][(int(r['round']),r['side'])]=int(r['alive_L'])
        for g,r in gs.items():
            us=r['bot_side']; th='B' if us=='A' else 'A'
            ee=[e for e in E[g] if int(e['n'+us+'0'])>0 and int(e['n'+th+'0'])>0]
            if not ee: continue
            al=lambda s,rd: T[g].get((max(10,(rd//10)*10),s),0)
            pu=[int(e['join'+us])/max(1,al(us,int(e['r0']))) for e in ee]
            pt=[int(e['join'+th])/max(1,al(th,int(e['r0']))) for e in ee]
            rows.append(dict(cell=(r['opponent'],r['map'],us,r['seed']),win=r['bot_result']=='win',
                part_us=sum(pu)/len(pu), part_them=sum(pt)/len(pt),
                alive_us=sum(al(us,int(e['r0'])) for e in ee)/len(ee), alive_them=sum(al(th,int(e['r0'])) for e in ee)/len(ee),
                join_us=sum(int(e['join'+us]) for e in ee)/len(ee), join_them=sum(int(e['join'+th]) for e in ee)/len(ee),
                dur=sum(int(e['dur']) for e in ee)/len(ee)))
by=defaultdict(list)
for x in rows: by[x['cell']].append(x)
keys=[k for k in rows[0] if k not in('cell','win')]
print(f'launcher fights <= r{R}: within-cell loss / win / diff +- se')
for k in keys:
    d=[];lm=[];wm=[]
    for c,xs in by.items():
        L=[x[k] for x in xs if not x['win']]; W=[x[k] for x in xs if x['win']]
        if L and W: lm.append(sum(L)/len(L)); wm.append(sum(W)/len(W)); d.append(lm[-1]-wm[-1])
    m=sum(d)/len(d); se=(sum((q-m)**2 for q in d)/(len(d)-1))**.5/len(d)**.5
    print(f'{k:11s} {sum(lm)/len(lm):6.2f} {sum(wm)/len(wm):6.2f} {m:+6.2f} +-{se:4.2f}')
