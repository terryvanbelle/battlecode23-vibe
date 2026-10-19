import sys; sys.path.insert(0,'/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al')
from common import *
I,H=islands()
for mp in sys.argv[1:]:
    hq={'A':[(x,y) for t,x,y in H[mp] if t=='A'],'B':[(x,y) for t,x,y in H[mp] if t=='B']}
    print(mp,'HQ A',hq['A'],'B',hq['B'])
    for i,sq in sorted(I[mp].items()):
        cx=sum(x for x,y in sq)/len(sq); cy=sum(y for x,y in sq)/len(sq)
        dA=min(min(d2(s,h) for s in sq) for h in hq['A'])**.5; dB=min(min(d2(s,h) for s in sq) for h in hq['B'])**.5
        print('  isl',i,'n',len(sq),'c(%.0f,%.0f)'%(cx,cy),'dA %.1f dB %.1f'%(dA,dB))
