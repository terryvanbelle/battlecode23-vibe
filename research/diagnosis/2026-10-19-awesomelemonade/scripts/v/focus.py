# Same-round focus: per (round,target) hits by one side; step-in hits' rank within the round's hits on that target.
import sys,os,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
from sa1 import par_rounds
from sa2 import GAMES, rows
RMAX=300; STATE=sys.argv[1] if len(sys.argv)>1 and sys.argv[1]!='all' else None
tot={}
for opp,m,gi,path in GAMES:
    grp='AL' if opp=='AL' else 'S4'
    G=games(m); us=G[gi]['us']; th=other(us); st=par_rounds(m,gi,us)
    for s,lab in ((us,'U'),(th,'T')):
        c=tot.setdefault((grp,lab),collections.Counter())
        H=collections.defaultdict(list)
        for r in rows(path,s,gi):
            rn=int(r['round'])
            if rn>=RMAX or (STATE and st(rn)!=STATE): continue
            if r['attacked']=='1' and r['atk_hit']=='1' and r['atk_target_type']=='L' and r['atk_target_hp_before']:
                ds=int(r['atk_d2_start']) if r['atk_d2_start'] else 0
                H[(rn,r['atk_target_id'])].append((int(r['atk_target_hp_before']),ds>16))
        for k,hs in H.items():
            hs.sort(key=lambda h:-h[0])
            n=len(hs); top=hs[0][0]
            c['tr']+=1; c['hits']+=n; c[f'n{min(n,4)}']+=1
            killed=hs[-1][0]<=20
            c['kills']+=killed
            if killed: c['kill_multi']+=n>=2; c['kill_hp0']+=top
            for j,(hp,si) in enumerate(hs):
                if si:
                    c['si']+=1; c['si_rank2']+=j>=1; c['si_kill']+=hp<=20
                    if hp<=20: c['si_kill_rank2']+=j>=1
    pass
for (grp,lab),c in sorted(tot.items()):
    tr=max(1,c['tr']); k=max(1,c['kills']); si=max(1,c['si'])
    print(f"{grp} {'US  ' if lab=='U' else 'THEM'} r<300 {STATE}: target-rounds {c['tr']} hits {c['hits']} hits/target-round {c['hits']/tr:.2f} (1:{c['n1']/tr:.2f} 2:{c['n2']/tr:.2f} 3:{c['n3']/tr:.2f} 4+:{c['n4']/tr:.2f}) | kills {c['kills']} kill/target-round {c['kills']/tr:.3f}, kills with >=2 hits that round {c['kill_multi']/k:.2f}, mean hp at round's first hit on killed {c['kill_hp0']/k:.0f} | step-in hits {c['si']}: not first hit on target that round {c['si_rank2']/si:.2f}, kills {c['si_kill']} of which after a same-round hit {c['si_kill_rank2']}")
