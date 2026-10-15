import csv, glob, os
from collections import defaultdict, Counter
W=[(0,60),(60,100),(100,150)]
rows=[]
for p in sorted(glob.glob('gauntlet/*-panel-*')):
    if not os.path.exists(p+'/results.csv'): continue
    res=defaultdict(dict)
    for r in csv.DictReader(open(p+'/results.csv')):
        if r['bot_result'] in('win','loss'): res[int(r['match'])][int(r['game'])]=r
    for m,gs in res.items():
        T=defaultdict(list)
        for r in csv.DictReader(open(f'matches/{m}/extract/trips.csv')):
            g=int(r['game'])
            if g in gs and r['side']==gs[g]['bot_side'] and int(r['t0'])<150: T[g].append(r)
        for g,r in gs.items():
            x=dict(cell=(r['opponent'],r['map'],r['bot_side'],r['seed']),win=r['bot_result']=='win')
            for a,b in W:
                tt=[t for t in T[g] if a<=int(t['t0'])<b]; n=max(1,len(tt))
                dep=[t for t in tt if t['outcome']=='deposit']
                x[f'trips{a}']=len(tt)
                x[f'wait{a}']=sum(int(t['wait_rounds']) for t in tt)/n
                x[f'cycle{a}']=sum(int(t['t_end'])-int(t['t0']) for t in dep)/max(1,len(dep))
                x[f'toWell{a}']=sum(int(t['first_collect'])-int(t['t0']) for t in tt if int(t['first_collect'] or -1)>=0)/n
                x[f'nodep{a}']=1-len(dep)/n
                x[f'wells{a}']=len({(t['well_x'],t['well_y']) for t in tt})
            rows.append(x)
by=defaultdict(list)
for x in rows: by[x['cell']].append(x)
keys=[k for k in rows[0] if k not in('cell','win')]
print('our trips by start window: within-cell loss / win / diff +- se')
for k in keys:
    d=[];lm=[];wm=[]
    for c,xs in by.items():
        a=[x[k] for x in xs if not x['win']]; b=[x[k] for x in xs if x['win']]
        if a and b: lm.append(sum(a)/len(a)); wm.append(sum(b)/len(b)); d.append(lm[-1]-wm[-1])
    m=sum(d)/len(d); se=(sum((q-m)**2 for q in d)/(len(d)-1))**.5/len(d)**.5
    print(f'{k:10s} {sum(lm)/len(lm):7.2f} {sum(wm)/len(wm):7.2f} {m:+6.2f} +-{se:4.2f}')
