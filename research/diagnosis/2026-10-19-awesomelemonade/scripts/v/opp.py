# Kill opportunities by stepping in: shooter move-ready, no enemy L within r2 16 at its turn start, an enemy L with
# hp<=20 within r2 (16,26]. Conversion = shooter killed a <=20hp launcher this turn. Also: threat at the best kill tile.
import sys,os,csv,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
from sa1 import par_rounds
from sa2 import GAMES, rows
N8=[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy]
def d2(a,b,c,d): return (a-c)**2+(b-d)**2
RMAX=int(sys.argv[1]) if len(sys.argv)>1 else 300
STATE=sys.argv[2] if len(sys.argv)>2 and sys.argv[2]!='all' else None
tot={}
for opp,m,gi,path in GAMES:
    grp='AL' if opp=='AL' else 'S4'
    G=games(m); us=G[gi]['us']; th=other(us); st=par_rounds(m,gi,us)
    R={}
    for s in (us,th):
        byr=collections.defaultdict(list); moved={}
        for r in rows(path,s,gi):
            rn=int(r['round']); i=int(r['id'])
            rec=dict(id=i,hp=int(r['hp']),x=int(r['x']),y=int(r['y']),mv=r['moved']=='1',att=r['attacked']=='1',
                     hitL=r['atk_hit']=='1' and r['atk_target_type']=='L',thp=int(r['atk_target_hp_before']) if r['atk_target_hp_before'] else None,
                     ds=int(r['atk_d2_start']) if r['atk_d2_start'] else None,e16=int(r['enemy_L_16']),a20=int(r['ally_L_20']),e20=int(r['enemy_L_20']))
            byr[rn].append(rec); moved[(i,rn)]=rec['mv']
        R[s]=(byr,moved)
    for s,lab in ((us,'U'),(th,'T')):
        o=th if s==us else us
        byr,moved=R[s]; obyr,omoved=R[o]
        key=(grp,lab); c=tot.setdefault(key,collections.Counter())
        for rn,recs in byr.items():
            if rn>=RMAX or (STATE and st(rn)!=STATE): continue
            en=obyr.get(rn,[])
            if not en: continue
            for S in recs:
                ready=not moved.get((S['id'],rn-1),False)
                if not ready or S['e16']>0: continue
                weak=[V for V in en if V['hp']<=20 and 16<d2(S['x'],S['y'],V['x'],V['y'])<=26]
                if not weak: continue
                c['opp']+=1
                k=S['att'] and S['hitL'] and S['thp'] is not None and S['thp']<=20
                c['conv']+=k
                # threat at best kill tile: enemy L (all) within r2 26 of tile, minus the victim
                bt=99
                for V in weak:
                    for dx,dy in N8:
                        tx,ty=S['x']+dx,S['y']+dy
                        if d2(tx,ty,V['x'],V['y'])>16: continue
                        t=sum(1 for E in en if E['id']!=V['id'] and d2(tx,ty,E['x'],E['y'])<=26)
                        bt=min(bt,t)
                ahead=S['a20']+1-S['e20']>=2
                c[f'bt{min(bt,3)}']+=1; c[f'bt{min(bt,3)}_conv']+=k
                c['ahead']+=ahead; c['ahead_conv']+=ahead and k
        # exposure: own launcher-turns with hp<=20 having an enemy within (16,26] that is move-ready (did not move last round)
        for rn,recs in byr.items():
            if rn>=RMAX or (STATE and st(rn)!=STATE): continue
            en=obyr.get(rn,[])
            for S in recs:
                if S['hp']>20: continue
                c['w20']+=1
                if any(16<d2(S['x'],S['y'],E['x'],E['y'])<=26 and not omoved.get((E['id'],rn-1),False) for E in en): c['w20_exp']+=1
                if any(d2(S['x'],S['y'],E['x'],E['y'])<=16 for E in en): c['w20_inr']+=1
                if S['hp']<=40: pass
            for S in recs:
                if 20<S['hp']<=40:
                    c['w40']+=1
                    if any(d2(S['x'],S['y'],E['x'],E['y'])<=26 for E in en): c['w40_reach']+=1
for (grp,lab),c in sorted(tot.items()):
    o=max(1,c['opp'])
    f=lambda k: f"{c[k+'_conv']}/{c[k]}={c[k+'_conv']/max(1,c[k]):.2f}"
    print(f"{grp} {'US  ' if lab=='U' else 'THEM'} r<{RMAX} {STATE}: step-in kill opps {c['opp']} converted {c['conv']} ({c['conv']/o:.2f}) | by threat at best kill tile: 0 {f('bt0')} 1 {f('bt1')} 2 {f('bt2')} 3+ {f('bt3')} | ahead2 {c['ahead_conv']}/{c['ahead']} | own hp<=20 turns {c['w20']}: in r2 16 of enemy {c['w20_inr']/max(1,c['w20']):.2f}, exposed to ready step-in {c['w20_exp']/max(1,c['w20']):.2f} | hp21-40 turns {c['w40']} within r2 26 {c['w40_reach']/max(1,c['w40']):.2f}")
