import sys,os,collections; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from sa1 import par_rounds
from sa2 import GAMES, rows
for state in ['par',None]:
  for grp in ['AL','S4']:
    P={'U':collections.Counter(),'T':collections.Counter()}
    for opp,m,gi,path in GAMES:
        if (opp=='AL')!=(grp=='AL'): continue
        G=games(m); us=G[gi]['us']; th=other(us); st=par_rounds(m,gi,us)
        for s,k in [(us,'U'),(th,'T')]:
            c=P[k]
            for r in rows(path,s,gi):
                rn=int(r['round'])
                if rn>=300 or (state and st(rn)!=state): continue
                if not(r['attacked']=='1' and r['atk_hit']=='1' and r['atk_target_type']=='L'): continue
                ds=r['atk_d2_start']; ds=int(ds) if ds else 99
                if ds<=16: continue
                c['n']+=1
                h=int(r['atk_target_hp_before']); mn=r['enemy_L_hp_min16']
                if mn!='' and h<=int(mn): c['focus']+=1
                c['hp']+=h; c['kill']+=h<=20
    for k in 'UT':
        c=P[k]; n=max(1,c['n'])
        print(f"r<300 {state} {grp} {'US' if k=='U' else 'THEM'} STEP-IN hits on L n={c['n']}: target is min-hp in range {c['focus']/n:.2f}, mean target hp {c['hp']/n:.0f}, kill share {c['kill']/n:.3f}")
