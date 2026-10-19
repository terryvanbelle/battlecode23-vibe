# last own turn before death, both sides: local numbers, hp, fired, moved, d2 to nearest enemy L; our code at death
import sys,os,csv,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from sa1 import par_rounds
from sa2 import GAMES, rows
def run(sel,label,rmax=300,state='par'):
    P={'U':collections.Counter(),'T':collections.Counter()}
    for opp,m,gi,path in GAMES:
        if not sel(opp): continue
        G=games(m); us=G[gi]['us']; th=other(us); st=par_rounds(m,gi,us)
        D={int(d['id']):d for d in rd(m,'deaths') if d['game']==gi and d['type']=='L'}
        for s,lab in [(us,'U'),(th,'T')]:
            last={}
            for r in rows(path,s,gi):
                i=int(r['id'])
                if i in D and int(r['round'])<=int(D[i]['round']): last[i]=r
            c=P[lab]
            for i,d in D.items():
                if d['side']!=s: continue
                rn=int(d['round'])
                if rn>=rmax or (state and st(rn)!=state): continue
                r=last.get(i)
                if r is None: c['norow']+=1; continue
                c['n']+=1
                a,e=int(r['ally_L_20']),int(r['enemy_L_20'])
                c['out']+=e>a+1; c['adv']+=a-e; c['hp']+=int(r['hp']); c['hp<=40']+=int(r['hp'])<=40
                c['inrange']+=int(r['enemy_L_16'])>0; c['noenemy20']+=e==0
                c['fired']+=r['attacked']=='1'; c['moved']+=r['moved']=='1'
                c['same_round']+=int(r['round'])==rn
                nd=r['near_eL_d2']; 
                if nd!='': c['nd']+=1; c['nd_le16']+=int(nd)<=16
                if s==us:
                    k=decode(d['last_code'])
                    if k: c['M']+=k['mode']=='M'; c['F']+=k['mode']=='F'; c['H']+=k['mode']=='H'
    for k in ['U','T']:
        c=P[k]; n=max(1,c['n'])
        extra=f" | code M {c['M']/n:.2f} F {c['F']/n:.2f} H {c['H']/n:.2f}" if k=='U' else ''
        print(f"{label} {'OUR' if k=='U' else 'THEIR'} L deaths n={c['n']} (no row {c['norow']}): last turn hp {c['hp']/n:.0f} (<=40 {c['hp<=40']/n:.2f}) enemy L in range {c['inrange']/n:.2f} none within r2 20 {c['noenemy20']/n:.2f} fired {c['fired']/n:.2f} moved {c['moved']/n:.2f} | local adv {c['adv']/n:+.2f} outnumbered {c['out']/n:.2f}"+extra)
if __name__=='__main__':
    for state in ['par',None]:
        print('## r<300',state)
        run(lambda o:o=='AL','AL 4g',300,state); run(lambda o:o!='AL','S4 6g',300,state)
