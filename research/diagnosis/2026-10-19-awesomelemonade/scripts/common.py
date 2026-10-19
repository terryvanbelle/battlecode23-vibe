import csv, os, collections
R='/home/terryvanbelle/projects/vibe/2023/matches'
AL={8826:'c_hr1',9042:'c_isle1',9478:'c_loose1',9893:'c_sm1',9904:'c_eco3',9509:'rk',9511:'rk',9514:'rk',9675:'rk',9701:'rk',9702:'rk',9703:'rk'}
def rows(m,f):
    p=os.path.join(R,str(m),'extract',f+'.csv')
    with open(p) as fh: return list(csv.DictReader(fh))
def games(m):
    g={}
    for r in rows(m,'games'):
        k=int(r['game']); g.setdefault(k,{'map':r['map'],'w':int(r['width']),'h':int(r['height']),'nisl':int(r['islands']),'rounds':int(r['rounds'])})
        if r['team']=='vibe23': g[k]['us']=r['side']; g[k]['won']=int(r['won'])
        else: g[k]['opp']=r['team']
    return g
def islands():
    I=collections.defaultdict(lambda: collections.defaultdict(list)); H=collections.defaultdict(list)
    for line in open('/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/islands.csv'):
        p=line.strip().split(',')
        if p[0]=='I': I[p[1]][int(p[2])].append((int(p[3]),int(p[4])))
        elif p[0]=='H': H[p[1]].append((p[2],int(p[3]),int(p[4])))
    return I,H
def d2(a,b): return (a[0]-b[0])**2+(a[1]-b[1])**2
