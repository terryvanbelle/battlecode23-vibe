# per-turn launcher fight metrics from --sa dumps (both teams), for one game
import sys,os,csv,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sa')
def load_sa(tag,side):
    rows=[]
    for r in csv.DictReader(open(f'{D}/{tag}{side}/sa_L.csv')):
        for k in ['round','id','hp','x','y','ally_L_20','enemy_L_20','enemy_L_16','attacked','moved','on_cloud']: r[k]=int(r[k]) if r[k]!='' else 0
        for k in ['d2_island_own','d2_island_enemy','near_eL_d2','enemy_L_hp_min16','atk_target_hp_before','atk_d2_start','d2_enemy_hq','d2_own_hq']:
            r[k]=int(r[k]) if r[k] not in ('',None) else None
        rows.append(r)
    return rows
def par_rounds(m,gi,us):
    T={(int(r['round']),r['side']):r for r in rd(m,'timeline') if r['game']==gi}
    st={}
    for (rn,s),r in T.items():
        if s!=us: continue
        b=T.get((rn,other(us)))
        la,lb=int(r['alive_L']),int(b['alive_L'])
        ratio=(la+1)/(lb+1)
        st[rn]='par' if 0.8<=ratio<=1.25 else ('ahead' if ratio>1.25 else 'behind')
    return lambda rn: st.get(max(10,(rn-1)//10*10),'?')
def analyse(tag,m,gi,rmax=300,state=None):
    G=games(m); us=G[gi]['us']; th=other(us)
    S={us:load_sa(tag,us),th:load_sa(tag,th)}
    st=par_rounds(m,gi,us)
    deaths={}
    for d in rd(m,'deaths'):
        if d['game']==gi and d['type']=='L': deaths[int(d['id'])]=int(d['round'])
    out={}
    for side in [us,th]:
        R=[r for r in S[side] if r['round']<rmax and (state is None or st(r['round'])==state)]
        c=collections.Counter()
        byid=collections.defaultdict(list)
        for r in S[side]: byid[r['id']].append(r)
        for r in R:
            inr=r['enemy_L_16']>0
            c['turns']+=1; c['inrange']+=inr
            if inr:
                c['inr_att']+=r['attacked']>0
                c['inr_out']+=r['enemy_L_20']>r['ally_L_20']+1
                c['inr_cloud']+=r['on_cloud']
                c['inr_hp<=80']+=r['hp']<=80
            if r['enemy_L_20']>0 and r['hp']<=80:
                c['wounded_vis']+=1
            if r['attacked'] and r['atk_hit']=='1' and r['atk_target_type']=='L':
                c['hitL']+=1
                hb=r['atk_target_hp_before']
                if hb is not None and hb<=20: c['killL']+=1
                if r['enemy_L_hp_min16'] is not None and hb is not None and hb<=r['enemy_L_hp_min16']: c['focus']+=1
                if r['atk_d2_start'] is not None and r['atk_d2_start']>16: c['hit_stepin']+=1
                c['hit_local_adv']+=r['ally_L_20']-r['enemy_L_20']
                c['hit_outnum']+=r['enemy_L_20']>r['ally_L_20']+1
                c['hit_cloud']+=r['on_cloud']
            if r['attacked'] and r['atk_hit']=='1' and r['atk_target_type']=='C': c['hitC']+=1
            if r['attacked'] and r['atk_hit']!='1': c['miss']+=1
            if r['d2_island_own'] is not None and r['d2_island_own']>=0 and r['d2_island_own']<=4: c['on_own_isl']+=1
            if r['d2_island_enemy'] is not None and r['d2_island_enemy']>=0 and r['d2_island_enemy']<=4: c['on_enemy_isl']+=1
        # healing: hp rises between consecutive turns
        heal=0; heal_isl=0
        for i,rs in byid.items():
            rs.sort(key=lambda r:r['round'])
            for a,b in zip(rs,rs[1:]):
                if b['round']>=rmax or (state and st(b['round'])!=state): continue
                if b['hp']>a['hp']: heal+=b['hp']-a['hp']
        c['healed']=heal
        # wounded fate: launchers whose hp first drops to <=80 before rmax: die within 30 rounds?
        wd=0; wn=0; wrec=0
        for i,rs in byid.items():
            fw=next((r for r in rs if r['hp']<=80),None)
            if not fw or fw['round']>=rmax or (state and st(fw['round'])!=state): continue
            wn+=1
            dr=deaths.get(i)
            if dr is not None and dr-fw['round']<=30: wd+=1
            if any(r['hp']>=140 and r['round']>fw['round'] for r in rs): wrec+=1
        c['wounded_n']=wn; c['wounded_die30']=wd; c['wounded_recover']=wrec
        c['deathsL']=sum(1 for i,rnd in deaths.items() if rnd<rmax and (state is None or st(rnd)==state) and i in byid)
        out[side]=c
    return us,th,out
def show(tag,m,gi,rmax=300,state=None):
    us,th,o=analyse(tag,m,gi,rmax,state)
    print(f'== {tag} r<{rmax} state={state}')
    for s,lab in [(us,'US'),(th,'THEM')]:
        c=o[s]; h=max(1,c['hitL']); ir=max(1,c['inrange'])
        print(f"  {lab}: turns {c['turns']} inrange {c['inrange']} fire|inrange {c['inr_att']/ir:.2f} outnumbered|inrange {c['inr_out']/ir:.2f} cloud|inrange {c['inr_cloud']/ir:.2f} hp<=80|inrange {c['inr_hp<=80']/ir:.2f} | "
              f"hitsL {c['hitL']} killsL {c['killL']} conv {c['killL']/h:.3f} focus(min-hp target) {c['focus']/h:.2f} stepin {c['hit_stepin']/h:.2f} local adv at hit {c['hit_local_adv']/h:+.2f} outnum at hit {c['hit_outnum']/h:.2f} | hitsC {c['hitC']} misses {c['miss']} | "
              f"healed {c['healed']} on own isl turns {c['on_own_isl']} | deathsL {c['deathsL']} hitsL taken/death | wounded n {c['wounded_n']} die<=30r {c['wounded_die30']} recover>=140 {c['wounded_recover']}")
    a,b=o[us],o[th]
    print(f"  L-on-L damage per death: ours dealt {20*a['hitL']}/{b['deathsL']} = {20*a['hitL']/max(1,b['deathsL']):.0f}; theirs {20*b['hitL']}/{a['deathsL']} = {20*b['hitL']/max(1,a['deathsL']):.0f}")
if __name__=='__main__':
    for tag,m,gi in [('9478g8','9478','8'),('9476g8','9476','8'),('9478g5','9478','5')]:
        show(tag,m,gi,300,None); show(tag,m,gi,300,'par'); show(tag,m,gi,3000,None)
