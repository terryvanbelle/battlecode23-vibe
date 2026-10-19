import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from a2_decomp import per_game
from load import *
ms=[(m,o) for m,o in LOOSE.items() if o in STRONG or o=='AL']+[(m,'AL') for m in AL_RANKED]
for m,o in ms:
    G=games(m)
    for gi,g in sorted(G.items(),key=lambda x:int(x[0])):
        r=per_game([(m,o)],lambda gg,gi=gi: gg['gi']==gi, bucket='par', phase='<300')
        if r and r[0][4]>=5:
            s=r[0]; print(m,gi,o,g['map'],'W' if g['won'] else 'L',f"win {s[4]} deaths {s[0]}-{s[1]} dmg {s[2]}-{s[3]}")
