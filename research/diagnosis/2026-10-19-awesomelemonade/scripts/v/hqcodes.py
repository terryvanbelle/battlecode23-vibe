# HQ break reasons (hq.csv codes, counts per 25-round bucket) by phase, AL losses vs AL wins vs S4 (c_eco3 + ranked).
import sys,os,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
GR={'AL':[('9904','AL')]+[(m,'AL') for m in AL_RANKED],'S4':[(m,o) for m,o in ECO.items() if o!='AL']}
for name,ms in GR.items():
  for won in (0,1):
    for lo,hi in ((0,300),(300,700)):
        c=collections.Counter(); bad=collections.Counter(); seen=set()
        for m,o in ms:
            G=games(m)
            for r in rd(m,'hq'):
                g=G[r['game']]
                if g['won']!=won or r['side']!=g['us']: continue
                rn=int(r['round'])
                if not(lo<rn<=hi): continue
                for kv in r['codes'].split(';'):
                    if not kv: continue
                    k,v=kv.split('='); c[k]+=int(v)
                bad['n']+=1; bad['Ad']+=int(r['bank_Ad']); bad['Mn']+=int(r['bank_Mn'])
        t=sum(c.values()) or 1
        print(f"{name} {'win ' if won else 'loss'} r{lo}-{hi}: HQ turns {t} | "+' '.join(f"{k}={v/t:.2f}" for k,v in c.most_common(8))+f" | mean bank Ad {bad['Ad']/max(1,bad['n']):.0f} Mn {bad['Mn']/max(1,bad['n']):.0f}")
