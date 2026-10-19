# launcher exchange in 10-round windows conditioned on the global army state at the window start
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
import collections
def run(matches,label,filt=lambda g:True):
    acc=collections.defaultdict(lambda:[0,0,0])  # bucket -> [our L deaths, their L deaths, windows]
    for m,opp in matches:
        G=games(m); tl=rd(m,'timeline'); D=rd(m,'deaths')
        alive={}
        for r in tl: alive[(r['game'],int(r['round']),r['side'])]=int(r['alive_L'])
        dd=collections.Counter()
        for d in D:
            if d['type']!='L': continue
            dd[(d['game'],(int(d['round'])-1)//10*10,d['side'])]+=1
        for gi,g in G.items():
            if not filt(g): continue
            us=g['us'];th=other(us)
            for r0 in range(10,g['rounds'],10):
                a=alive.get((gi,r0,us)); b=alive.get((gi,r0,th))
                if a is None or b is None: continue
                if a+b<4: continue
                ratio=(a+1)/(b+1)
                bk='par' if 0.8<=ratio<=1.25 else ('ahead' if ratio>1.25 else 'behind')
                ph='<300' if r0<300 else '300+'
                for key in [(bk,ph),(bk,'all')]:
                    x=acc[key]; x[0]+=dd[(gi,r0,us)]; x[1]+=dd[(gi,r0,th)]; x[2]+=1
    print(label)
    for bk in ['behind','par','ahead']:
        s=[]
        for ph in ['<300','300+','all']:
            u,t,n=acc[(bk,ph)]
            s.append(f'{ph}: win{n} ours {u} theirs {t} exch {t/u if u else float("nan"):.2f}')
        print('  ',bk,' | '.join(s))
AL=[(m,'AL') for m in ['9478']+AL_RANKED]
run(AL,'AL c_loose1 (9478+ranked, n=31) all games')
run(AL,'AL losses',lambda g:g['won']==0)
run(AL,'AL wins',lambda g:g['won']==1)
SG=[(m,o) for m,o in LOOSE.items() if o in STRONG]
run(SG,'strong4 c_loose1 panel (n=40) all')
run(SG,'strong4 losses',lambda g:g['won']==0)
run(SG,'strong4 wins',lambda g:g['won']==1)
for m,o in LOOSE.items():
    if o in STRONG: run([(m,o)],o+' all')
run([('9904','AL')],'AL 9904 c_eco3 all')
