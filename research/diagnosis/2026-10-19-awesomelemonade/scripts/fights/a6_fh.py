import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from a5_eng import *
for lab,ms,f in [('AL loss',AL,lambda g:g['won']==0),('AL win',AL,lambda g:g['won']==1),('S4 loss',SG,lambda g:g['won']==0),('S4 win',SG,lambda g:g['won']==1),('S4 all',SG,lambda g:True),('AL all',AL,lambda g:True)]:
    E=engs(ms,f)
    L=[e for e in E if e['peakU']>=1 and e['peakT']>=1 and (e['kills_by_U']+e['kills_by_T'])>0 and e['r0']<300]
    for side in ['U','T']:
        F=[e for e in L if e['fh']==side]
        n=len(F)
        if not n: continue
        c=collections.Counter()
        for e in F:
            c['how_'+e['fh_how']]+=1; c['att_'+e['fh_att_type']]+=1; c['vic_'+e['fh_vic_type']]+=1
            c['vicmoved']+=e['fh_vic_moved']=='1'; c['attmovedprev']+=e['fh_att_moved_prev']=='1'; c['in_start']+=e['fh_in_start']=='1'; c['in_prev']+=e['fh_in_prev']=='1'
            c['cloud_'+e['fh_cloud']]+=1
            c['won']+=e['res']=='U'
        keys=['how_stepin','how_stand','how_out','how_move','att_L','att_C','vic_L','vic_C','vicmoved','attmovedprev','in_start','in_prev','cloud_a','cloud_v','cloud_av','won']
        print(f"{lab} fh={side} n={n}: "+' '.join(f"{k}={c[k]/n:.2f}" for k in keys))
