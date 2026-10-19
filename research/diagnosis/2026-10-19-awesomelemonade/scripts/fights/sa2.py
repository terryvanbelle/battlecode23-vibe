# local numbers at each launcher-on-launcher hit, per game, pooled by opponent (new dumps + the c_hr1 dumps in micro/sa)
import sys,os,csv,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from sa1 import par_rounds
NEW=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sa')
OLD='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/micro/sa'
GAMES=[('AL','9478','8',f'{NEW}/9478g8'),('AL','9478','5',f'{NEW}/9478g5'),('AL','8826','5',f'{OLD}/8826'),('AL','8826','7',f'{OLD}/8826'),
       ('jmerle','9476','8',f'{NEW}/9476g8'),('vrangr1','8823','4',f'{OLD}/8823'),('jmerle','8824','8',f'{OLD}/8824'),('pranayagra','8827','0',f'{OLD}/8827'),('pranayagra','8827','9',f'{OLD}/8827'),('NotLLeon','8828','1',f'{OLD}/8828')]
def rows(path,side,gi):
    out=[]
    with open(f'{path}{side}/sa_L.csv') as f:
        for r in csv.DictReader(f):
            if r['game']!=gi: continue
            out.append(r)
    return out
I=lambda v: int(v) if v not in ('',None) else None
def game_stats(opp,m,gi,path,rmax=300,state='par'):
    G=games(m); us=G[gi]['us']; th=other(us); st=par_rounds(m,gi,us)
    res={}
    for side in [us,th]:
        c=collections.Counter(); hb=[]
        for r in rows(path,side,gi):
            rn=int(r['round'])
            if rn>=rmax or (state and st(rn)!=state): continue
            a,e=int(r['ally_L_20']),int(r['enemy_L_20'])
            if int(r['enemy_L_16'])>0:
                c['inr']+=1; c['inr_out']+=e>a+1; c['inr_adv']+=a-e; c['inr_hp']+=int(r['hp'])
            if r['attacked']=='1' and r['atk_hit']=='1' and r['atk_target_type']=='L':
                c['hit']+=1; c['adv']+=a-e; c['out']+=e>a+1; c['ahead']+=a>e+1
                h=I(r['atk_target_hp_before']); mn=I(r['enemy_L_hp_min16'])
                if h is not None and h<=20: c['kill']+=1
                if h is not None and mn is not None and h<=mn: c['focus']+=1
                if I(r['atk_d2_start']) is not None and I(r['atk_d2_start'])>16: c['stepin']+=1
            if r['attacked']=='1' and r['atk_hit']!='1': c['miss']+=1
        res[side]=c
    return us,th,res
def pool(sel,label,rmax=300,state='par'):
    P={'U':collections.Counter(),'T':collections.Counter()}
    for opp,m,gi,path in GAMES:
        if not sel(opp): continue
        us,th,res=game_stats(opp,m,gi,path,rmax,state)
        P['U'].update(res[us]); P['T'].update(res[th])
        u,t=res[us],res[th]
        print(f"   {opp:10s} {m} g{gi}: hits {u['hit']}/{t['hit']} kills {u['kill']}/{t['kill']} | local adv at hit {u['adv']/max(1,u['hit']):+.2f}/{t['adv']/max(1,t['hit']):+.2f} | hits while outnumbered {u['out']/max(1,u['hit']):.2f}/{t['out']/max(1,t['hit']):.2f} | in-range turns outnumbered {u['inr_out']/max(1,u['inr']):.2f}/{t['inr_out']/max(1,t['inr']):.2f} | focus {u['focus']/max(1,u['hit']):.2f}/{t['focus']/max(1,t['hit']):.2f} | blind misses {u['miss']}/{t['miss']}")
    u,t=P['U'],P['T']
    print(f"{label}: hits {u['hit']}/{t['hit']} kills {u['kill']}/{t['kill']} conv {u['kill']/max(1,u['hit']):.3f}/{t['kill']/max(1,t['hit']):.3f} | local adv at hit {u['adv']/max(1,u['hit']):+.2f}/{t['adv']/max(1,t['hit']):+.2f} | hits while outnumbered {u['out']/max(1,u['hit']):.2f}/{t['out']/max(1,t['hit']):.2f} | hits while ahead2 {u['ahead']/max(1,u['hit']):.2f}/{t['ahead']/max(1,t['hit']):.2f} | in-range turns outnumbered {u['inr_out']/max(1,u['inr']):.2f}/{t['inr_out']/max(1,t['inr']):.2f} adv {u['inr_adv']/max(1,u['inr']):+.2f}/{t['inr_adv']/max(1,t['inr']):+.2f} | focus {u['focus']/max(1,u['hit']):.2f}/{t['focus']/max(1,t['hit']):.2f} stepin {u['stepin']/max(1,u['hit']):.2f}/{t['stepin']/max(1,t['hit']):.2f}")
if __name__=='__main__':
    for state in ['par',None]:
        print('##### r<300 state',state)
        pool(lambda o:o=='AL','AL (4 games)',300,state)
        pool(lambda o:o!='AL','S4 (6 games)',300,state)
