import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapread
R='/home/terryvanbelle/projects/vibe/2023/matches'
AL_PANEL={'9478':'c_loose1','9904':'c_eco3','9893':'c_sm1','9042':'c_isle1','8826':'c_hr1'}
AL_RANKED=['9509','9511','9514','9675','9701','9702','9703']
LOOSE={'9476':'jmerle','9475':'vrangr1','9479':'pranayagra','9480':'NotLLeon','9478':'AL',
       '9477':'georgezhang02','9481':'archive','9482':'reeceyang','9483':'yaonam','9484':'britacatalin'}
ECO={'9902':'jmerle','9901':'vrangr1','9905':'pranayagra','9906':'NotLLeon','9904':'AL'}
STRONG={'jmerle','vrangr1','pranayagra','NotLLeon'}
def rd(m,f): return list(csv.DictReader(open(f'{R}/{m}/extract/{f}.csv')))
def games(m):
    """per game: dict(map, rounds, us='A'|'B', won)"""
    out={}
    for r in rd(m,'games'):
        if r['team']=='vibe23':
            out[r['game']]=dict(gi=r['game'],m=m,map=r['map'],rounds=int(r['rounds']),us=r['side'],won=int(r['won']),W=int(r['width']),H=int(r['height']))
    return out
def other(s): return 'B' if s=='A' else 'A'
def eng_us(e,us):
    """engagement with fields renamed to us/them"""
    t=other(us)
    g=lambda k: e[k.replace('X',us).replace('Y',t)]
    d=dict(e)
    for k in ['nX0','hpX0','peakX','joinX','kills_by_X','val_lost_X','surv_X','codes_X']:
        d[k.replace('X','U')]=g(k); d[k.replace('X','T')]=e[k.replace('X',t)]
    d['dmgU']=e['dmg_by_'+us]; d['dmgT']=e['dmg_by_'+t]
    m={us:'U',t:'T'}
    d['fh']=m.get(e['first_hit'],'-'); d['res']=m.get(e['result'],'draw'); d['heldU']=m.get(e['held'],'-')
    p=e['prog0']; d['progU']=(float(p) if us=='A' else 1-float(p)) if p else None
    for k in ['nU0','nT0','hpU0','hpT0','peakU','peakT','joinU','joinT','kills_by_U','kills_by_T','val_lost_U','val_lost_T','surv_U','surv_T','r0','r1','dur','x0','y0']:
        d[k]=int(d[k]) if k in d and d[k]!='' else (int(e[k]) if k in e and e[k]!='' else 0)
    d['dmgU']=int(d['dmgU']); d['dmgT']=int(d['dmgT'])
    return d
def decode(code):
    if code=='' or code is None: return None
    c=int(code); return dict(mode='NFHMSGW!'[c&7], obj=(c>>3)&3, out=(c>>5)&1)
