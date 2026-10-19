# hit-level: did the victim answer (fire within its next turn), was the attacker on a cloud / victim on cloud, was victim marching
import sys,os,csv,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from sa1 import par_rounds
from sa2 import GAMES, rows
import mapread
def run(sel,label,rmax=300,state='par'):
    P={'U':collections.Counter(),'T':collections.Counter()}
    for opp,m,gi,path in GAMES:
        if not sel(opp): continue
        G=games(m); us=G[gi]['us']; th=other(us); st=par_rounds(m,gi,us)
        mp=mapread.load(G[gi]['map']); W=mp['W']; cl=mp['clouds']
        R={us:rows(path,us,gi),th:rows(path,th,gi)}
        idx={}
        for s in R:
            for r in R[s]: idx[(int(r['id']),int(r['round']))]=r
        for s,lab in [(us,'U'),(th,'T')]:
            c=P[lab]
            for r in R[s]:
                rn=int(r['round'])
                if rn>=rmax or (state and st(rn)!=state): continue
                if not(r['attacked']=='1' and r['atk_hit']=='1' and r['atk_target_type']=='L'): continue
                v=int(r['atk_target_id']); c['hit']+=1
                vr=idx.get((v,rn)); vn=idx.get((v,rn+1))
                ans=(vr is not None and vr['attacked']=='1' and vr['atk_order']!='') or (vn is not None and vn['attacked']=='1')
                # victim's own turn this round happened before the hit? approximate: use next-round answer only
                ans2=vn is not None and vn['attacked']=='1' and vn['atk_hit']=='1'
                c['ans_next']+=vn is not None and vn['attacked']=='1'; c['ans_next_hit']+=ans2
                c['victim_dead_next']+=vn is None
                tx,ty=int(r['atk_tx']),int(r['atk_ty'])
                c['att_cloud']+=int(r['on_cloud']); c['vic_cloud']+=cl[tx+ty*W]==1
                # victim's state in its previous turn: was it moving toward / in range
                vp=idx.get((v,rn-1))
                if vp is not None:
                    c['vp']+=1; c['vp_inrange']+=int(vp['enemy_L_16'])>0; c['vp_fired']+=vp['attacked']=='1'; c['vp_moved']+=vp['moved']=='1'
                    c['vp_hp']+=int(vp['hp'])
    for k in ['U','T']:
        c=P[k]; h=max(1,c['hit']); vp=max(1,c['vp'])
        print(f"{label} hits by {'US' if k=='U' else 'THEM'} n={c['hit']}: victim fired next turn {c['ans_next']/h:.2f} (hit {c['ans_next_hit']/h:.2f}), victim gone next turn {c['victim_dead_next']/h:.2f} | attacker on cloud {c['att_cloud']/h:.2f} victim on cloud {c['vic_cloud']/h:.2f} | victim prev turn: had enemy in range {c['vp_inrange']/vp:.2f} fired {c['vp_fired']/vp:.2f} moved {c['vp_moved']/vp:.2f} hp {c['vp_hp']/vp:.0f}")
if __name__=='__main__':
    for state in ['par',None]:
        print('## r<300',state)
        run(lambda o:o=='AL','AL 4g',300,state)
        run(lambda o:o!='AL','S4 6g',300,state)
