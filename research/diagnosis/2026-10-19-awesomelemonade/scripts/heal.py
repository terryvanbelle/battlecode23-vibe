import sys; sys.path.insert(0,'/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al')
from common import *
MS=[9478,9904,9475,9476,9479,9480,9901,9902,9905,9906,9477,9481,9482,9483,9484, 9509,9511,9514,9675,9701,9702,9703]
DUP={(9702,0),(9702,2),(9703,1)}
agg=collections.defaultdict(lambda: collections.Counter())
for m in MS:
    G=games(m); C=rows(m,'census')
    cen={(int(r['game']),r['side']):r for r in C}
    for g,info in G.items():
        if (m,g) in DUP: continue
        us=info['us']; th='B' if us=='A' else 'A'
        cu,ct=cen[(g,us)],cen[(g,th)]
        opp=info['opp'].split('.')[0]
        key=(opp if opp=='awesomelemonade' else ('strong' if opp in ('jmerle','vrangr1','pranayagra','NotLLeon') else 'weak'), 'W' if info['won'] else 'L')
        c=agg[key]; c['n']+=1
        for k,v in (('dmg_u',cu['dmg']),('dmg_t',ct['dmg']),('heal_u',cu['healed']),('heal_t',ct['healed']),('ir_u',cu['island_rounds']),('ir_t',ct['island_rounds']),('kills_u',cu['kills']),('kills_t',ct['kills']),('fa_t_early', 1 if 0<=int(ct['first_anchor'])<=300 else 0),('fa_u_early', 1 if 0<=int(cu['first_anchor'])<=300 else 0),('anch_t_first', 1 if int(ct['first_anchor'])>=0 and (int(cu['first_anchor'])<0 or int(ct['first_anchor'])<int(cu['first_anchor'])) else 0),('no_anchor_t',1 if int(ct['first_anchor'])<0 else 0)):
            c[k]+=float(v)
for k,c in sorted(agg.items()):
    print(k,'n',c['n'],'healed/dmg_received: them %.3f us %.3f'%(c['heal_t']/max(1,c['dmg_u']),c['heal_u']/max(1,c['dmg_t'])),
          'heal per isl-round them %.2f us %.2f'%(c['heal_t']/max(1,c['ir_t']),c['heal_u']/max(1,c['ir_u'])),
          'isl-rounds/game them %.0f us %.0f'%(c['ir_t']/c['n'],c['ir_u']/c['n']),
          'dmg/kill us %.0f them %.0f'%(c['dmg_u']/max(1,c['kills_u']),c['dmg_t']/max(1,c['kills_t'])),
          'they anchor first %d, they never anchor %d, their fa<=300 %d, ours<=300 %d'%(c['anch_t_first'],c['no_anchor_t'],c['fa_t_early'],c['fa_u_early']))
