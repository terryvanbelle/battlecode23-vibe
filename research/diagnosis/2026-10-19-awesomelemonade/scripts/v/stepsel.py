# Step-in hits: was a weaker enemy launcher reachable (r2<=26 from the shooter's start) than the one hit?
import sys,os,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
from sa1 import par_rounds
from sa2 import GAMES, rows
STATE=sys.argv[1] if len(sys.argv)>1 and sys.argv[1]!="all" else None
RLO=int(sys.argv[2]) if len(sys.argv)>2 else 0; RHI=int(sys.argv[3]) if len(sys.argv)>3 else 300
def d2(a,b,c,d): return (a-c)**2+(b-d)**2
tot={}
for opp,m,gi,path in GAMES:
    grp='AL' if opp=='AL' else 'S4'
    G=games(m); us=G[gi]['us']; th=other(us); st=par_rounds(m,gi,us)
    R={s:collections.defaultdict(dict) for s in (us,th)}
    for s in (us,th):
        for r in rows(path,s,gi):
            R[s][int(r['round'])][int(r['id'])]=r
    for s,lab in ((us,'U'),(th,'T')):
        o=th if s==us else us
        c=tot.setdefault((grp,lab),collections.Counter())
        for rn,rr in R[s].items():
            if not (RLO<=rn<RHI) or (STATE and st(rn)!=STATE): continue
            en=R[o].get(rn,{})
            for i,r in rr.items():
                if not(r['attacked']=='1' and r['atk_hit']=='1' and r['atk_target_type']=='L' and r['atk_d2_start']): continue
                if int(r['atk_d2_start'])<=16: continue
                th_=int(r['atk_target_hp_before']); tid=int(r['atk_target_id'])
                x,y=int(r['x']),int(r['y'])
                # current hp estimate: row hp this round (start of its turn), else next round
                alt=[int(e['hp']) for j,e in en.items() if j!=tid and d2(x,y,int(e['x']),int(e['y']))<=26]
                c['n']+=1; c['kill']+=th_<=20
                if alt:
                    a=min(alt)
                    c['alt']+=1
                    if th_>20 and a<=20: c['missed_kill']+=1
                    if a+40<=th_: c['weaker40']+=1
                c['thp']+=th_
for (grp,lab),c in sorted(tot.items()):
    n=max(1,c['n'])
    print(f"{grp} {'US  ' if lab=='U' else 'THEM'} r{RLO}-{RHI} {STATE}: step-in hits {c['n']} kills {c['kill']} ({c['kill']/n:.3f}) | a <=20hp enemy L also reachable but a >20hp one hit: {c['missed_kill']} ({c['missed_kill']/n:.3f}) | a target 40+hp weaker reachable: {c['weaker40']/n:.2f} | mean target hp {c['thp']/n:.0f}")
