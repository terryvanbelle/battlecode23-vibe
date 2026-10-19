import sys; sys.path.insert(0,'/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al')
from common import *
out=[]
for m,b in AL.items():
    G=games(m); T=rows(m,'timeline'); C=rows(m,'census')
    tl=collections.defaultdict(dict)
    for r in T: tl[int(r['game'])].setdefault(int(r['round']),{})[r['side']]=r
    cen={(int(r['game']),r['side']):r for r in C}
    for g,info in sorted(G.items()):
        us=info['us']; th='B' if us=='A' else 'A'; t=tl[g]; rs=sorted(t)
        def first(side):
            for r in rs:
                if int(t[r][side]['islands'])>=1: return r
            return None
        E1=first(th); O1=first(us)
        def L(r,s): return int(t[r][s]['alive_L']) if r in t else None
        eL=(L(E1,us),L(E1,th)) if E1 else None
        # drain: decreases in enemy islands
        drops=0; prev=0; maxE=0; eir=0; oir=0
        for r in rs:
            e=int(t[r][th]['islands']); o=int(t[r][us]['islands'])
            if e<prev: drops+=prev-e
            prev=e; maxE=max(maxE,e); eir+=e*10; oir+=o*10
        cu=cen.get((g,us),{}); ct=cen.get((g,th),{})
        out.append((m,b,g,info['map'],info['nisl'],info['won'],info['rounds'],E1,O1,eL,cu.get('first_anchor'),ct.get('first_anchor'),cu.get('anchors_placed'),ct.get('anchors_placed'),drops,eir,oir,cu.get('healed'),ct.get('healed')))
print('m build g map nisl won rounds E1 O1 L@E1(us,th) fa_us fa_th placed_us placed_th enemy_isl_drops eIR oIR healed_us healed_th')
for o in out: print(*o)
