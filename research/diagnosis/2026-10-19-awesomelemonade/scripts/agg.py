import csv, sys, statistics as st
R='/home/terryvanbelle/projects/vibe/2023/matches/%s/extract/%s.csv'
def load(m,f):
    with open(R%(m,f)) as fh: return list(csv.DictReader(fh))
RS=[0,100,150,200,250,300,400]
def gamerecs(m, opp=None):
    out=[]
    G={}
    for r in load(m,'games'): G.setdefault(r['game'],{})['us' if r['team']=='vibe23' else 'them']=r
    T={}
    for r in load(m,'timeline'): T[(r['game'],int(r['round']),r['side'])]=r
    H={}
    for r in load(m,'hq'): H.setdefault((r['game'],r['side']),[]).append(r)
    for g,d in G.items():
        if opp and not d['them']['team'].startswith(opp): continue
        sa,sb=d['us']['side'],d['them']['side']
        rec={'m':m,'g':g,'map':d['us']['map'],'won':int(d['us']['won']),'opp':d['them']['team'],'R':int(d['us']['rounds']),'sa':sa,'sb':sb}
        for rd in RS:
            for side,key in ((sa,'us'),(sb,'th')):
                if rd==0:
                    rec[(key,rd)]={k:0 for k in ('alive_L','built_L','lost_L','coll_Mn','coll_Ad','alive_C','built_C','lost_C','bank_Ad','bank_Mn','built_A','islands','kills')}; continue
                r=T.get((g,rd,side))
                if not r: rec[(key,rd)]=None; continue
                x={k:int(r[k]) for k in ('alive_L','built_L','coll_Mn','coll_Ad','alive_C','built_C','bank_Ad','bank_Mn','built_A','islands','kills','alive_A')}
                x['lost_L']=x['built_L']-x['alive_L']; x['lost_C']=x['built_C']-x['alive_C']
                rec[(key,rd)]=x
        # hq buckets per window
        for key,side in (('us',sa),('th',sb)):
            for i in range(1,len(RS)):
                lo,hi=RS[i-1],RS[i]
                rows=[r for r in H.get((g,side),[]) if lo<int(r['round'])<=hi]
                rec[('hq',key,hi)]=rows
        out.append(rec)
    return out
def mean(v): return sum(v)/len(v) if v else float('nan')
def window_table(recs,label):
    print(f"== {label}  (n={len(recs)} games)")
    print("  win      n  dAlive  dBuilt  dLost | built us/th  lost us/th | Mn us/th   C built us/th  C lost us/th | bankAd us/th bankMn us/th | A us/th")
    for i in range(1,len(RS)):
        lo,hi=RS[i-1],RS[i]
        rr=[r for r in recs if r[('us',hi)] and r[('th',hi)]]
        if not rr: continue
        def d(key,k): return [r[(key,hi)][k]-r[(key,lo)][k] for r in rr]
        bu,bt=d('us','built_L'),d('th','built_L'); lu,lt=d('us','lost_L'),d('th','lost_L')
        mu,mt=d('us','coll_Mn'),d('th','coll_Mn'); cu,ct=d('us','built_C'),d('th','built_C'); clu,clt=d('us','lost_C'),d('th','lost_C')
        db=mean(bu)-mean(bt); dl=mean(lu)-mean(lt)
        print(f"  {lo:3d}-{hi:3d} {len(rr):2d}  {db-dl:+6.1f}  {db:+6.1f}  {-dl:+6.1f} | {mean(bu):5.1f}/{mean(bt):5.1f} {mean(lu):5.1f}/{mean(lt):5.1f} | {mean(mu):4.0f}/{mean(mt):4.0f}  {mean(cu):4.1f}/{mean(ct):4.1f}  {mean(clu):4.1f}/{mean(clt):4.1f} | {mean([r[('us',hi)]['bank_Ad'] for r in rr]):4.0f}/{mean([r[('th',hi)]['bank_Ad'] for r in rr]):4.0f} {mean([r[('us',hi)]['bank_Mn'] for r in rr]):4.0f}/{mean([r[('th',hi)]['bank_Mn'] for r in rr]):4.0f} | {mean([r[('us',hi)]['alive_A'] for r in rr]):.1f}/{mean([r[('th',hi)]['alive_A'] for r in rr]):.1f}")
    print("  cumulative at r:  alive us/th  gap = built gap - lost gap ; C alive us/th ; Mn us/th ; isl us/th")
    for hi in RS[1:]:
        rr=[r for r in recs if r[('us',hi)] and r[('th',hi)]]
        if not rr: continue
        g=lambda key,k: mean([r[(key,hi)][k] for r in rr])
        print(f"   r{hi:3d} n={len(rr):2d}  {g('us','alive_L'):5.1f}/{g('th','alive_L'):5.1f}  {g('us','alive_L')-g('th','alive_L'):+6.1f} = {g('us','built_L')-g('th','built_L'):+6.1f} - {g('us','lost_L')-g('th','lost_L'):+6.1f} ; C {g('us','alive_C'):4.1f}/{g('th','alive_C'):4.1f} ; Mn {g('us','coll_Mn'):5.0f}/{g('th','coll_Mn'):5.0f} ; isl {g('us','islands'):.2f}/{g('th','islands'):.2f}")
def hq_table(recs,label):
    print(f"== HQ {label}")
    for i in range(1,len(RS)):
        hi=RS[i]
        rr=[r for r in recs if r[('us',hi)] and r[('th',hi)]]
        cnt={}; tot=0; pu=[];pt=[];iu=[];it=[]
        for r in rr:
            for row in r[('hq','us',hi)]:
                tot+=1
                for kv in row['codes'].split(';'):
                    if '=' in kv:
                        k,v=kv.split('='); cnt[k]=cnt.get(k,0)+int(v)
                pu.append(int(row['pressure34'])>0); iu.append(int(row['idle_funds']))
            for row in r[('hq','th',hi)]:
                pt.append(int(row['pressure34'])>0); it.append(int(row['idle_funds']))
        s=sum(cnt.values()) or 1
        codes=' '.join(f"{k}={100*v/s:.0f}%" for k,v in sorted(cnt.items(),key=lambda x:-x[1])[:5])
        print(f"  ..{hi:3d}: pressured34 buckets us {100*mean(pu):3.0f}% th {100*mean(pt):3.0f}% | idle_funds/bucket us {mean(iu):4.1f} th {mean(it):4.1f} | our HQ codes {codes}")
if __name__=='__main__':
    import json
    spec=json.loads(sys.argv[1])
    for label,(ms,opp,won) in spec.items():
        recs=[]
        for m in ms: recs+=gamerecs(str(m),opp)
        if won is not None: recs=[r for r in recs if r['won']==won]
        window_table(recs,label)
        if len(sys.argv)>2: hq_table(recs,label)
