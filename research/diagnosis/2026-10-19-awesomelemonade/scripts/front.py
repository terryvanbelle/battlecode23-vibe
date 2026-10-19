import csv, sys, json, statistics as st
R='/home/terryvanbelle/projects/vibe/2023/matches/%s/extract/%s.csv'
def load(m,f):
    with open(R%(m,f)) as fh: return list(csv.DictReader(fh))
W=[(0,100),(100,150),(150,200),(200,250),(250,300)]
def run(label, ms, opp, won, permap=False):
    rows={w:[] for w in W}; carr={w:[[],[],[],[]] for w in W}; pm={}
    n=0
    for m in ms:
        G={}
        for r in load(m,'games'): G.setdefault(r['game'],{})['us' if r['team']=='vibe23' else 'them']=r
        T={}
        for r in load(m,'timeline'): T[(r['game'],int(r['round']),r['side'])]=r
        D=load(m,'deaths')
        for g,d in G.items():
            if opp and not d['them']['team'].startswith(opp): continue
            if won is not None and int(d['us']['won'])!=won: continue
            n+=1; sa=d['us']['side']; sb=d['them']['side']
            for x in D:
                if x['game']!=g or x['type']!='L' or not x['prog']: continue
                rd=int(x['round']); p=float(x['prog'])
                if sa=='B': p=1-p
                for w in W:
                    if w[0]<rd<=w[1]:
                        rows[w].append(p)
                        if permap: pm.setdefault((d['us']['map'],m),{}).setdefault(w,[]).append(p)
            for w in W:
                lo,hi=w
                # Mn per alive carrier per 50 rounds, Ad collected
                for side,i in ((sa,0),(sb,1)):
                    cs=[int(T[(g,r,side)]['alive_C']) for r in range(lo+10,hi+1,10) if (g,r,side) in T]
                    a=T.get((g,hi,side)); b=T.get((g,lo,side)) if lo else None
                    if not a or not cs: continue
                    dMn=int(a['coll_Mn'])-(int(b['coll_Mn']) if b else 0); dAd=int(a['coll_Ad'])-(int(b['coll_Ad']) if b else 0)
                    carr[w][i].append((dMn,dAd,st.mean(cs),hi-lo))
    print(f"== {label} n={n}")
    for w in W:
        v=rows[w]
        if not v: continue
        def cstat(i):
            L=carr[w][i]
            if not L: return "-"
            mn=sum(x[0] for x in L); ad=sum(x[1] for x in L); cr=sum(x[2]*x[3] for x in L)
            return f"C {sum(x[2] for x in L)/len(L):4.1f} Mn/C-round {mn/cr:.3f} Ad/C-round {ad/cr:.3f} AdShare {ad/max(1,ad+mn):.2f}"
        print(f"  r{w[0]}-{w[1]}: L deaths {len(v)}, median front (0=our HQ) {st.median(v):.2f}, share <0.33 {sum(p<0.33 for p in v)/len(v):.2f}, >0.67 {sum(p>0.67 for p in v)/len(v):.2f} | us {cstat(0)} | th {cstat(1)}")
    if permap:
        for k,ws in sorted(pm.items()):
            print("   ",k, ' '.join(f"{w[0]}-{w[1]}:{st.median(v):.2f}({len(v)})" for w,v in sorted(ws.items())))
spec=json.loads(sys.argv[1])
for label,(ms,opp,won) in spec.items(): run(label,[str(m) for m in ms],opp,won, len(sys.argv)>2)
