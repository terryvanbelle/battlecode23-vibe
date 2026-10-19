import csv, sys
R='/home/terryvanbelle/projects/vibe/2023/matches/%s/extract/%s.csv'
def load(m,f):
    with open(R%(m,f)) as fh: return list(csv.DictReader(fh))
def games(m):
    g={}
    for r in load(m,'games'):
        g.setdefault(r['game'],{})[r['team']=='vibe23' and 'us' or 'them']=r
    return g
def tl(m):
    d={}
    for r in load(m,'timeline'):
        d[(r['game'],int(r['round']),r['side'])]=r
    return d
cols=['alive_L','built_L','alive_C','built_C','alive_A','built_A','coll_Mn','coll_Ad','bank_Mn','bank_Ad','carried_Mn','kills','islands']
if __name__=='__main__':
    ms=sys.argv[1].split(',')
    rounds=[int(x) for x in sys.argv[2].split(',')]
    for m in ms:
        G=games(m); T=tl(m)
        for g in sorted(G,key=int):
            us=G[g]['us']; th=G[g]['them']; sa=us['side']; sb=th['side']
            print(f"{m} g{g} {us['map']} {th['team'][:10]} won={us['won']} R={us['rounds']}")
            print("  rnd  aL/bL/lost(us)   aL/bL/lost(th)  C us/th (built)   Mn us/th   Ad us/th  bankMn  bankAd  amp  isl")
            for rd in rounds:
                a=T.get((g,rd,sa)); b=T.get((g,rd,sb))
                if not a or not b: continue
                f=lambda r,k:int(r[k])
                print(f"  {rd:4d} {f(a,'alive_L'):3d}/{f(a,'built_L'):3d}/{f(a,'built_L')-f(a,'alive_L'):3d}    {f(b,'alive_L'):3d}/{f(b,'built_L'):3d}/{f(b,'built_L')-f(b,'alive_L'):3d}    {f(a,'alive_C'):2d}/{f(b,'alive_C'):2d} ({f(a,'built_C')}/{f(b,'built_C')})   {f(a,'coll_Mn'):4d}/{f(b,'coll_Mn'):4d}  {f(a,'coll_Ad'):4d}/{f(b,'coll_Ad'):4d}  {f(a,'bank_Mn'):3d}/{f(b,'bank_Mn'):3d} {f(a,'bank_Ad'):3d}/{f(b,'bank_Ad'):3d}  {f(a,'built_A')}/{f(b,'built_A')}  {f(a,'islands')}/{f(b,'islands')}")
