# Ad share of collection and HQ pressure (hq pressure34>0 share), by phase; AL vs S4 (c_eco3 panel + AL ranked), loss/win.
import sys,os,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
GR={'AL':[('9904','AL')]+[(m,'AL') for m in AL_RANKED],'S4':[(m,o) for m,o in ECO.items() if o!='AL']}
for name,ms in GR.items():
  for won in (0,1):
    for lo,hi in ((100,300),(300,600)):
        c=collections.Counter()
        for m,o in ms:
            G=games(m); T={(r['game'],int(r['round']),r['side']):r for r in rd(m,'timeline')}
            for gi,g in G.items():
                if g['won']!=won: continue
                for s,k in ((g['us'],'u'),(other(g['us']),'t')):
                    a,b=T.get((gi,lo,s)),T.get((gi,hi,s))
                    if not a or not b: continue
                    c[k+'Ad']+=int(b['coll_Ad'])-int(a['coll_Ad']); c[k+'Mn']+=int(b['coll_Mn'])-int(a['coll_Mn'])
                    if k=='u': c['n']+=1
        n=max(1,c['n'])
        print(f"{name} {'win ' if won else 'loss'} r{lo}-{hi} n={c['n']}: ours Ad {c['uAd']/n:.0f} Mn {c['uMn']/n:.0f} (Ad share {c['uAd']/max(1,c['uAd']+c['uMn']):.2f}) | theirs Ad {c['tAd']/n:.0f} Mn {c['tMn']/n:.0f} (Ad share {c['tAd']/max(1,c['tAd']+c['tMn']):.2f})")
