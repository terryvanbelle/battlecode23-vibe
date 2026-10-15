import csv, glob, os
from collections import defaultdict
rows=[]
for p in sorted(glob.glob('gauntlet/*-panel-*')):
    if not os.path.exists(p+'/results.csv'): continue
    res=defaultdict(dict)
    for r in csv.DictReader(open(p+'/results.csv')):
        if r['bot_result'] in('win','loss'): res[int(r['match'])][int(r['game'])]=r
    for m,gs in res.items():
        S=defaultdict(lambda: defaultdict(float))
        for r in csv.DictReader(open(f'matches/{m}/extract/tele_states.csv')):
            g=int(r['game'])
            if g in gs and r['type']=='C' and r['phase']=='open' and r['side']==gs[g]['bot_side']:
                S[g][r['letter']]+=float(r['turns'])
        for g,r in gs.items():
            t=sum(S[g].values())
            if t: rows.append(dict(cell=(r['opponent'],r['map'],r['bot_side'],r['seed']),win=r['bot_result']=='win',sh={k:v/t for k,v in S[g].items()}))
L=sorted({k for x in rows for k in x['sh']})
by=defaultdict(list)
for x in rows: by[x['cell']].append(x)
print('our carrier turns by letter, r<=150, within-cell loss / win / diff +- se')
for k in L:
    d=[];lm=[];wm=[]
    for c,xs in by.items():
        a=[x['sh'].get(k,0) for x in xs if not x['win']]; b=[x['sh'].get(k,0) for x in xs if x['win']]
        if a and b: lm.append(sum(a)/len(a)); wm.append(sum(b)/len(b)); d.append(lm[-1]-wm[-1])
    if not d: continue
    m=sum(d)/len(d); se=(sum((q-m)**2 for q in d)/(len(d)-1))**.5/len(d)**.5
    print(f'{k} {sum(lm)/len(lm):.3f} {sum(wm)/len(wm):.3f} {m:+.4f} +-{se:.4f}')
