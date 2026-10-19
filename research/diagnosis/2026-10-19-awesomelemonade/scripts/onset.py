import csv, sys, json
R='/home/terryvanbelle/projects/vibe/2023/matches/%s/extract/%s.csv'
def load(m,f):
    with open(R%(m,f)) as fh: return list(csv.DictReader(fh))
def run(label, ms, opp, won, thr=5):
    print(f"== {label}")
    seen=set(); res=[]
    for m in ms:
        G={}
        for r in load(m,'games'): G.setdefault(r['game'],{})['us' if r['team']=='vibe23' else 'them']=r
        T={}
        for r in load(m,'timeline'): T[(r['game'],int(r['round']),r['side'])]=r
        for g,d in sorted(G.items(),key=lambda x:int(x[0])):
            if opp and not d['them']['team'].startswith(opp): continue
            if won is not None and int(d['us']['won'])!=won: continue
            sa,sb=d['us']['side'],d['them']['side']
            # dedupe identical games by signature at r100/r300
            sig=(d['us']['map'],d['us']['rounds'],tuple(T.get((g,300,sa),{}).get('built_L','') for _ in [0]))
            if sig in seen: continue
            seen.add(sig)
            on=None
            for rd in range(10,2001,10):
                a=T.get((g,rd,sa)); b=T.get((g,rd,sb))
                if not a or not b: break
                if int(b['alive_L'])-int(a['alive_L'])>=thr:
                    on=rd; break
            if on is None:
                res.append((d['us']['map'],m,None)); print(f"  {m} {d['us']['map']:18s} never behind by {thr}"); continue
            a=T[(g,on,sa)]; b=T[(g,on,sb)]
            bg=int(a['built_L'])-int(b['built_L']); lg=(int(a['built_L'])-int(a['alive_L']))-(int(b['built_L'])-int(b['alive_L']))
            kind='ATTR' if lg>-bg else 'PROD'
            res.append((d['us']['map'],m,on,bg,lg,kind))
            print(f"  {m} {d['us']['map']:18s} onset r{on:4d}: alive {a['alive_L']}/{b['alive_L']} built gap {bg:+d} lost gap {lg:+d} -> {kind}; Mn {a['coll_Mn']}/{b['coll_Mn']} C {a['alive_C']}/{b['alive_C']} isl {a['islands']}/{b['islands']}")
    ons=[r for r in res if r[2]]
    import statistics as st
    if ons: print(f"  n={len(res)} behind>={thr}: {len(ons)}; median onset r{st.median(r[2] for r in ons):.0f}; ATTR {sum(r[5]=='ATTR' for r in ons)} PROD {sum(r[5]=='PROD' for r in ons)}")
spec=json.loads(sys.argv[1])
for label,(ms,opp,won) in spec.items(): run(label,[str(m) for m in ms],opp,won)
