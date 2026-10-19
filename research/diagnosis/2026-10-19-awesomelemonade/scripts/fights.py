import csv, sys, json
R='/home/terryvanbelle/projects/vibe/2023/matches/%s/extract/%s.csv'
def load(m,f):
    with open(R%(m,f)) as fh: return list(csv.DictReader(fh))
W=[(0,100),(100,200),(200,300)]
def run(label, ms, opp, won):
    games=[]
    for m in ms:
        G={}
        for r in load(m,'games'): G.setdefault(r['game'],{})['us' if r['team']=='vibe23' else 'them']=r
        T={}
        for r in load(m,'timeline'): T[(r['game'],int(r['round']),r['side'])]=r
        E=load(m,'engagements'); D=load(m,'deaths')
        for g,d in G.items():
            if opp and not d['them']['team'].startswith(opp): continue
            if int(d['us']['won'])!=won: continue
            games.append((m,g,d['us']['side'],d['them']['side'],T,[e for e in E if e['game']==g],[x for x in D if x['game']==g]))
    print(f"== {label} n={len(games)}")
    for lo,hi in W:
        agg=dict(dU=0,dT=0,dU_isl=0,dT_isl=0,dU_home=0,dT_home=0,dU_cU=0,dT_cT=0,ne=0,nlev=0,kA_lev=0,kB_lev=0,dmgA=0,dmgB=0,kA=0,kB=0,fhA=0,lev_dmgA=0,lev_dmgB=0,aura_U=0,aura_T=0,isl_rounds=0)
        for (m,g,sa,sb,T,E,D) in games:
            def oppisl(rd):
                r10=(rd//10)*10
                r=T.get((g,r10,sb)); return int(r['islands']) if r else 0
            for x in D:
                rd=int(x['round'])
                if not (lo<rd<=hi) or x['type']!='L': continue
                prog=float(x['prog']) if x['prog'] else 0.5
                if sa=='B': prog=1-prog
                if x['side']==sa:
                    agg['dU']+=1; agg['dU_isl']+=oppisl(rd)>0; agg['dU_home']+=prog<0.33; agg['aura_U']+=x['cause']=='hq_aura'
                else:
                    agg['dT']+=1; agg['dT_isl']+=oppisl(rd)>0; agg['dT_home']+=prog>0.67; agg['aura_T']+=x['cause']=='hq_aura'
            for rd in range(lo+10,hi+1,10): agg['isl_rounds']+= 10 if oppisl(rd)>0 else 0
            for e in E:
                r0=int(e['r0'])
                if not (lo<r0<=hi): continue
                # side A in engagements = side A of the match; flip if we are B
                us='A' if sa=='A' else 'B'; th='B' if us=='A' else 'A'
                n0u,n0t=int(e['n'+us+'0']),int(e['n'+th+'0'])
                ku,kt=int(e['kills_by_'+us]),int(e['kills_by_'+th]); du,dt=int(e['dmg_by_'+us]),int(e['dmg_by_'+th])
                agg['ne']+=1; agg['kA']+=ku; agg['kB']+=kt; agg['dmgA']+=du; agg['dmgB']+=dt; agg['fhA']+=e['first_hit']==us
                if abs(n0u-n0t)<=1:
                    agg['nlev']+=1; agg['kA_lev']+=ku; agg['kB_lev']+=kt; agg['lev_dmgA']+=du; agg['lev_dmgB']+=dt
        n=len(games); a=agg
        f=lambda v:v/n
        print(f"  r{lo}-{hi}: L deaths us {f(a['dU']):.1f} th {f(a['dT']):.1f} | under opp island us {a['dU_isl']}/{a['dU']} th {a['dT_isl']}/{a['dT']} (opp-island game-rounds {a['isl_rounds']}) | own-third deaths us {a['dU_home']} th {a['dT_home']} | hq_aura us {a['aura_U']} th {a['aura_T']}")
        print(f"     engagements/game {f(a['ne']):.1f}, first_hit ours {a['fhA']/max(1,a['ne']):.2f}; kills us/th {a['kA']}/{a['kB']} dmg/kill us {a['dmgA']/max(1,a['kA']):.0f} th {a['dmgB']/max(1,a['kB']):.0f}; level fights {a['nlev']}: kills {a['kA_lev']}/{a['kB_lev']} dmg {a['lev_dmgA']}/{a['lev_dmgB']}")
spec=json.loads(sys.argv[1])
for label,(ms,opp,won) in spec.items(): run(label,[str(m) for m in ms],opp,won)
