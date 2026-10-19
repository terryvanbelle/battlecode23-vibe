import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from a3_deaths import *
import statistics
OBJ={0:'sight',1:'isle',2:'site/siege',3:'centre/mend',None:'none'}
def codes(rows,label):
    rs=[r for r in rows if r['mine']]
    n=len(rs)
    c=collections.Counter(); o=collections.Counter(); out=0; nc=0
    for r in rs:
        k=r['code']
        if k is None: nc+=1; continue
        c[k['mode']]+=1; o[OBJ[k['obj']]]+=1; out+=k['out']
    ages=sorted(r['age'] for r in rs)
    print(f"{label} n={n} notele {nc/n:.2f} | mode "+' '.join(f'{m}{c[m]/n:.2f}' for m in 'FHMNSGW')+" | obj "+' '.join(f'{k}{o[k]/n:.2f}' for k in ['sight','isle','site/siege','centre/mend'])+f" | outnumbered {out/n:.2f} | age p25/50 {ages[n//4]}/{ages[n//2]} age<=20 {sum(1 for a in ages if a<=20)/n:.2f}")
for lab,ms,f in [('AL loss',AL,lambda g:g['won']==0),('AL win',AL,lambda g:g['won']==1),('S4 loss',SG,lambda g:g['won']==0),('S4 win',SG,lambda g:g['won']==1)]:
    rows=collect(ms,f)
    for bk in ['par','behind','ahead']:
        for early in [True,False]:
            rs=[r for r in rows if r['bk']==bk and r['early']==early]
            if sum(1 for r in rs if r['mine'])>=20: codes(rs,f'{lab:8s} {bk:6s} {"<300" if early else "300+"}')
