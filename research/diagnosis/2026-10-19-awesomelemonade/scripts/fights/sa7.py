# low-HP launchers (hp<=40): what they do, and how they die
import sys,os,collections; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from sa1 import par_rounds
from sa2 import GAMES, rows
for grp in ['AL','S4']:
    P={'U':collections.Counter(),'T':collections.Counter()}
    for opp,m,gi,path in GAMES:
        if (opp=='AL')!=(grp=='AL'): continue
        G=games(m); us=G[gi]['us']; th=other(us); st=par_rounds(m,gi,us)
        D={int(d['id']):int(d['round']) for d in rd(m,'deaths') if d['game']==gi and d['type']=='L'}
        for s,k in [(us,'U'),(th,'T')]:
            c=P[k]; byid=collections.defaultdict(list)
            for r in rows(path,s,gi): byid[int(r['id'])].append(r)
            for i,rs in byid.items():
                rs.sort(key=lambda r:int(r['round']))
                for a,b in zip(rs,rs[1:]+[None]):
                    rn=int(a['round'])
                    if rn>=300 or int(a['hp'])>40: continue
                    c['t']+=1
                    nd=int(a['near_eL_d2']) if a['near_eL_d2']!='' else 999
                    c['nd<=16']+=nd<=16; c['nd17_34']+=17<=nd<=34; c['nd>34']+=nd>34
                    c['fired']+=a['attacked']=='1'
                    c['moved']+=a['moved']=='1'
                    if b is not None and a['near_eL_d2']!='' and b['near_eL_d2']!='':
                        c['pair']+=1; c['away']+=int(b['near_eL_d2'])>nd; c['closer']+=int(b['near_eL_d2'])<nd
                    c['hp_own_hq_d2']+=int(a['d2_own_hq'])
                first=next((r for r in rs if int(r['hp'])<=40 and int(r['round'])<300),None)
                if first:
                    c['w']+=1; dr=D.get(i)
                    c['die10']+=dr is not None and dr-int(first['round'])<=10
                    c['die30']+=dr is not None and dr-int(first['round'])<=30
                    c['heal']+=any(int(r['hp'])>int(first['hp'])+20 for r in rs if int(r['round'])>int(first['round']))
    for k in 'UT':
        c=P[k]; t=max(1,c['t']); p=max(1,c['pair']); w=max(1,c['w'])
        print(f"{grp} {'US' if k=='U' else 'THEM'} hp<=40 launcher-turns r<300 n={c['t']}: nearest enemy L r2<=16 {c['nd<=16']/t:.2f}, 17-34 {c['nd17_34']/t:.2f}, >34/none {c['nd>34']/t:.2f} | fired {c['fired']/t:.2f} moved {c['moved']/t:.2f} | next turn farther {c['away']/p:.2f} closer {c['closer']/p:.2f} | launchers reaching hp<=40: {c['w']}, dead within 10r {c['die10']/w:.2f}, 30r {c['die30']/w:.2f}, healed +20 later {c['heal']/w:.2f}")
