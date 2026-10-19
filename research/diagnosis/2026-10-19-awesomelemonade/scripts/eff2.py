import csv,sys
R='/home/terryvanbelle/projects/vibe/2023/matches/%s/extract/%s.csv'
m=sys.argv[1]; games=sys.argv[2].split(',')
T={}
for r in csv.DictReader(open(R%(m,'timeline'))): T[(r['game'],int(r['round']),r['side'])]=r
for g in games:
    for lo,hi in ((0,100),(100,150),(150,200),(200,250),(250,300)):
        out=[]
        for s in 'AB':
            e=T[(g,hi,s)]; b=T.get((g,lo,s))
            dd=int(e['dmg_dealt'])-(int(b['dmg_dealt']) if b else 0); k=int(e['kills'])-(int(b['kills']) if b else 0)
            lr=sum(int(T[(g,r,s)]['alive_L'])*10 for r in range(lo+10,hi+1,10))
            out.append((dd,k,lr))
        print(f"g{g} r{lo}-{hi}: dmg {out[0][0]}/{out[1][0]} kills {out[0][1]}/{out[1][1]} dmg/kill {out[0][0]/max(1,out[0][1]):.0f}/{out[1][0]/max(1,out[1][1]):.0f} L-rounds {out[0][2]}/{out[1][2]}")
