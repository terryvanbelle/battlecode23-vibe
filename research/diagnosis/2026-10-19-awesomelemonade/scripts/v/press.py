# Share of HQ 25-round rows with pressure34 >= 100 (the c_anc3 'pressed' test), r200-700, by group; and t-code share in them.
import sys,os,collections
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
GR={'AL':[('9904','AL')]+[(m,'AL') for m in AL_RANKED],'S4':[(m,o) for m,o in ECO.items() if o!='AL'],
    'weak5':[(m,'w') for m in ['9903','9907','9908','9909','9910']]}
for name,ms in GR.items():
  for won in (0,1):
    c=collections.Counter()
    for m,o in ms:
        G=games(m)
        for r in rd(m,'hq'):
            g=G[r['game']]
            if g['won']!=won or r['side']!=g['us'] or not (200<int(r['round'])<=700): continue
            c['n']+=1; p=int(r['pressure34'])>=100; c['p']+=p
    n=max(1,c['n']); print(f"{name} {'win ' if won else 'loss'} r200-700: HQ rows {c['n']}, pressed {c['p']/n:.2f}")
