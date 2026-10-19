# Late economy in level-at-r250 AL losses: per 100 rounds Mn collected, alive carriers, carriers built/died, bank Ad/Mn.
import sys,os,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
SEL=[('9904','0'),('9904','7'),('9509','1'),('9514','1'),('9675','1'),('9701','1'),('9702','1')]
agg=collections.defaultdict(lambda: collections.Counter())
for m,gi in SEL:
    g=games(m)[gi]; us,th=g['us'],other(g['us'])
    T={(int(r['round']),r['side']):r for r in rd(m,'timeline') if r['game']==gi}
    D=collections.Counter()
    for d in rd(m,'deaths'):
        if d['game']==gi and d['type']=='C': D[(d['side'],int(d['round'])//100)]+=1
    out=[]
    for R in range(200,min(g['rounds'],800)+1,100):
        a,b=T.get((R,us)),T.get((R,th)); a0,b0=T.get((R-100,us)),T.get((R-100,th))
        if not a or not a0: break
        mu=int(a['coll_Mn'])-int(a0['coll_Mn']); mt=int(b['coll_Mn'])-int(b0['coll_Mn'])
        cu=int(a['built_C'])-int(a0['built_C']); ct=int(b['built_C'])-int(b0['built_C'])
        out.append(f"r{R}: Mn {mu}/{mt} C {a['alive_C']}/{b['alive_C']} +{cu}/+{ct} -{D[(us,(R-1)//100)]}/-{D[(th,(R-1)//100)]} bankAd {a['bank_Ad']}/{b['bank_Ad']} bankMn {a['bank_Mn']}/{b['bank_Mn']}")
        k=agg[R]; k['n']+=1; k['mu']+=mu; k['mt']+=mt; k['cu']+=int(a['alive_C']); k['ct']+=int(b['alive_C']); k['dcu']+=D[(us,(R-1)//100)]; k['dct']+=D[(th,(R-1)//100)]; k['bau']+=int(a['bank_Ad']); k['bat']+=int(b['bank_Ad']); k['bcu']+=cu; k['bct']+=ct
    print(f"{m} g{gi} {g['map']}: "+' | '.join(out))
for R,k in sorted(agg.items()):
    n=k['n']; print(f"mean r{R-100}-{R} n={n}: Mn {k['mu']/n:.0f}/{k['mt']/n:.0f} alive C {k['cu']/n:.1f}/{k['ct']/n:.1f} C built {k['bcu']/n:.1f}/{k['bct']/n:.1f} C died {k['dcu']/n:.1f}/{k['dct']/n:.1f} bank Ad {k['bau']/n:.0f}/{k['bat']/n:.0f}")
