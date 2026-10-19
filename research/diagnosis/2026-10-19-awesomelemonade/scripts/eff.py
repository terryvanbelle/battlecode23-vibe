import csv, sys, json
R='/home/terryvanbelle/projects/vibe/2023/matches/%s/extract/%s.csv'
def load(m,f):
    with open(R%(m,f)) as fh: return list(csv.DictReader(fh))
W=[(0,100),(100,200),(200,300)]
def run(label, ms, opp, won):
    acc={w:[0]*8 for w in W}; n=0
    for m in ms:
        G={}
        for r in load(m,'games'): G.setdefault(r['game'],{})['us' if r['team']=='vibe23' else 'them']=r
        T={}
        for r in load(m,'timeline'): T[(r['game'],int(r['round']),r['side'])]=r
        for g,d in G.items():
            if opp and not d['them']['team'].startswith(opp): continue
            if won is not None and int(d['us']['won'])!=won: continue
            n+=1; sa,sb=d['us']['side'],d['them']['side']
            for w in W:
                lo,hi=w
                if (g,hi,sa) not in T: continue
                a=acc[w]
                for i,side in ((0,sa),(1,sb)):
                    e=T[(g,hi,side)]; s=T.get((g,lo,side))
                    a[i]+=int(e['dmg_dealt'])-(int(s['dmg_dealt']) if s else 0)
                    a[2+i]+=int(e['kills'])-(int(s['kills']) if s else 0)
                    a[4+i]+=sum(int(T[(g,r,side)]['alive_L'])*10 for r in range(lo+10,hi+1,10))
                    a[6+i]+=sum(int(T[(g,r,side)]['in_contact'])*10 for r in range(lo+10,hi+1,10))
    print(f"== {label} n={n}")
    for w in W:
        a=acc[w]
        print(f"  r{w[0]}-{w[1]}: dmg us/th {a[0]}/{a[1]} kills {a[2]}/{a[3]} dmg/kill {a[0]/max(1,a[2]):.0f}/{a[1]/max(1,a[3]):.0f} | L-rounds {a[4]}/{a[5]} dmg per L-round {a[0]/max(1,a[4]):.3f}/{a[1]/max(1,a[5]):.3f} | in_contact rounds {a[6]}/{a[7]} dmg per contact {a[0]/max(1,a[6]):.1f}/{a[1]/max(1,a[7]):.1f}")
spec=json.loads(sys.argv[1])
for label,(ms,opp,won) in spec.items(): run(label,[str(m) for m in ms],opp,won)
