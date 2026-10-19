# Late-collapse games: alive L (ours/theirs), production and deaths gap per 100 rounds; islands held.
import sys,os
F='/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights'
sys.path.insert(0,F)
from load import *
SEL=[('9904','0'),('9904','7'),('9509','1'),('9514','1'),('9514','0'),('9675','1'),('9701','1'),('9702','1'),('9904','5')]
for m,gi in SEL:
    g=games(m)[gi]; us,th=g['us'],other(g['us'])
    T={(int(r['round']),r['side']):r for r in rd(m,'timeline') if r['game']==gi}
    out=[]
    prev=None
    for R in range(100,min(g['rounds'],1000)+1,100):
        a=T.get((R,us)); b=T.get((R,th))
        if not a: break
        cur=(int(a['built_L']),int(b['built_L']),int(a['built_L'])-int(a['alive_L']),int(b['built_L'])-int(b['alive_L']))
        s=f"r{R} {a['alive_L']}/{b['alive_L']} i{a['islands']}/{b['islands']}"
        if prev: s+=f" b{cur[0]-prev[0]}/{cur[1]-prev[1]} d{cur[2]-prev[2]}/{cur[3]-prev[3]}"
        prev=cur; out.append(s)
    print(f"{m} g{gi} {g['map']} r{g['rounds']}: "+' | '.join(out))
