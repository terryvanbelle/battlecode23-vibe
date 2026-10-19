import csv,sys,json
R='/home/terryvanbelle/projects/vibe/2023/matches/%s/extract/%s.csv'
spec=json.loads(sys.argv[1])
for label,(ms,opp,won) in spec.items():
    n=0; agg={}
    for m in ms:
        m=str(m); G={}
        for r in csv.DictReader(open(R%(m,'games'))): G.setdefault(r['game'],{})['us' if r['team']=='vibe23' else 'them']=r
        D=list(csv.DictReader(open(R%(m,'deaths'))))
        for g,d in G.items():
            if opp and not d['them']['team'].startswith(opp): continue
            if won is not None and int(d['us']['won'])!=won: continue
            n+=1; sa=d['us']['side']
            for x in D:
                if x['game']!=g or x['type']!='C' or not x['prog']: continue
                rd=int(x['round']); 
                if rd>300: continue
                p=float(x['prog']); 
                if sa=='B': p=1-p
                w='0-150' if rd<=150 else '150-300'
                who='us' if x['side']==sa else 'th'
                home = p<0.33 if who=='us' else p>0.67
                k=(w,who); a=agg.setdefault(k,[0,0]); a[0]+=1; a[1]+=home
    print(label,f"n={n}", ' | '.join(f"{w} {who}: {a[0]/n:.1f}/game ({a[1]/n:.1f} in own third)" for (w,who),a in sorted(agg.items())))
