import csv, glob, os
from collections import defaultdict, Counter
R=200; rows=[]; cnt={True:Counter(),False:Counter()}
for p in sorted(glob.glob('gauntlet/*-panel-*')):
    if not os.path.exists(p+'/results.csv'): continue
    res=defaultdict(dict)
    for r in csv.DictReader(open(p+'/results.csv')):
        if r['bot_result'] in('win','loss'): res[int(r['match'])][int(r['game'])]=r
    for m,gs in res.items():
        E=defaultdict(list)
        for r in csv.DictReader(open(f'matches/{m}/extract/engagements.csv')):
            if int(r['r0'])<=R and int(r['game']) in gs: E[int(r['game'])].append(r)
        for g,r in gs.items():
            us=r['bot_side']; th='B' if us=='A' else 'A'; win=r['bot_result']=='win'
            x=dict(cell=(r['opponent'],r['map'],us,r['seed']),win=win)
            ee=[e for e in E[g] if int(e['n'+us+'0'])>0 and int(e['n'+th+'0'])>0]   # launcher vs launcher only
            n=max(1,len(ee))
            x['n']=len(ee)
            x['won']=sum(e['result']==us for e in ee)/n
            x['fh_us']=sum(e['first_hit']==us for e in ee)/n
            x['we_walked_in']=sum(e['first_hit']==th and e['fh_vic_moved']=='1' for e in ee)/n      # hit first after our own step
            x['they_walked_in']=sum(e['first_hit']==us and e['fh_vic_moved']=='1' for e in ee)/n
            x['they_stepin']=sum(e['first_hit']==th and e['fh_how']=='stepin' for e in ee)/n
            x['they_stand']=sum(e['first_hit']==th and e['fh_how']=='stand' for e in ee)/n
            x['won|fh_us']=None
            a=[e for e in ee if e['first_hit']==us]; b=[e for e in ee if e['first_hit']==th]
            x['won|fh_us']=sum(e['result']==us for e in a)/len(a) if a else None
            x['won|fh_them']=sum(e['result']==us for e in b) /len(b) if b else None
            x['dN']=sum(int(e['n'+us+'0'])-int(e['n'+th+'0']) for e in ee)/n
            x['outnumbered']=sum(int(e['n'+us+'0'])<int(e['n'+th+'0']) for e in ee)/n
            x['peak_diff']=sum(int(e['peak'+us])-int(e['peak'+th]) for e in ee)/n
            x['join_diff']=sum(int(e['join'+us])-int(e['join'+th]) for e in ee)/n
            rows.append(x)
            for e in ee:
                if e['first_hit']==th: cnt[win][(e['fh_how'],e['fh_vic_moved'])]+=1
by=defaultdict(list)
for x in rows: by[x['cell']].append(x)
keys=[k for k in rows[0] if k not in('cell','win')]
print(f'launcher-vs-launcher engagements <= r{R}; within-cell loss mean / win mean / diff +- se')
for k in keys:
    d=[];lm=[];wm=[]
    for c,xs in by.items():
        L=[x[k] for x in xs if not x['win'] and x[k] is not None]; W=[x[k] for x in xs if x['win'] and x[k] is not None]
        if L and W: lm.append(sum(L)/len(L)); wm.append(sum(W)/len(W)); d.append(lm[-1]-wm[-1])
    m=sum(d)/len(d); se=(sum((q-m)**2 for q in d)/(len(d)-1))**.5/len(d)**.5
    print(f'{k:14s} {sum(lm)/len(lm):6.2f} {sum(wm)/len(wm):6.2f} {m:+6.2f} +-{se:4.2f}  ({len(d)} cells)')
print('enemy first hits by (how, our victim moved): loss share / win share')
tl=sum(cnt[False].values()); tw=sum(cnt[True].values())
for k,_ in (cnt[False]+cnt[True]).most_common(8): print(' ',k, f'{cnt[False][k]/tl:.2f} {cnt[True][k]/tw:.2f}')
