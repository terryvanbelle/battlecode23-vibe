"""a3_trips.py: carriers' first well choice and trip times, both teams (trips.csv, robots.csv, map walk distances).

Per game and side:
  open_*  : the carriers born in rounds 1-2 (4 per HQ): first trip's well type, walk moves from the spawning HQ to that
            well (BFS, walls only) minus the walk to that HQ's nearest Mn well ('extra'), rounds born -> first collect,
            and the first trip's outcome and end round
  firstMn : the team's first Mn deposit round; Mn and Ad deposited by r50 and r100 (trip loads by well type)
  cycle   : median rounds per completed deposit trip that started by r100 (t_end - t0) and its legs: out (t0 -> first
            collect), fill (first -> last collect), back (last collect -> t_end); median load
Usage: python3 -I a3_trips.py [-v]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *

V = '-v' in sys.argv


def spawn_hq(G, side, rb):
    p = (int(rb['x_born']), int(rb['y_born']))
    return min(G['hqs'][side], key=lambda h: d2(h, p))


def analyse(G, side):
    name = G['map']
    born = {int(r['id']): r for r in robots(G, side) if r['type'] == 'C'}
    tr = collections.defaultdict(list)
    for t in trips(G, side):
        tr[int(t['carrier'])].append(t)
    for v in tr.values(): v.sort(key=lambda t: int(t['t0']))
    mf = mapfeat(G, side)
    nearest_mn = {p['hq']: p['walk_mn'] for p in mf['per']}
    nearest_ad = {p['hq']: p['walk_ad'] for p in mf['per']}
    out = dict(open=[], dep=collections.Counter(), firstMn=None, cyc=[], out_=[], fill=[], back=[], load=[], wait=[])
    for cid, rb in born.items():
        b = int(rb['born'])
        ts = [t for t in tr.get(cid, []) if t['well_type'] in ('1', '2')]
        if b <= 2:
            hq = spawn_hq(G, side, rb)
            if ts:
                t = ts[0]
                w = (int(t['well_x']), int(t['well_y']))
                wk = walk(name, hq, w)
                typ = int(t['well_type'])
                ref = nearest_mn[hq] if typ == 2 else nearest_ad[hq]
                out['open'].append(dict(id=cid, typ=typ, walk=wk, extra=None if wk is None or ref is None else wk - ref,
                                        fc=int(t['first_collect']) - b if t['first_collect'] else None,
                                        end=int(t['t_end']), outcome=t['outcome'], load=int(t['load'] or 0),
                                        well=w, hq=hq))
            else:
                out['open'].append(dict(id=cid, typ=0, walk=None, extra=None, fc=None, end=None, outcome='none', load=0,
                                        well=None, hq=hq))
    for cid, ts in tr.items():
        for t in ts:
            if t['outcome'] != 'deposit' or t['well_type'] not in ('1', '2'): continue
            te = int(t['t_end']); typ = int(t['well_type']); load = int(t['load'] or 0)
            for R in (50, 75, 100, 150):
                if te <= R: out['dep'][(typ, R)] += load
            if typ == 2 and (out['firstMn'] is None or te < out['firstMn']): out['firstMn'] = te
            if int(t['t0']) <= 100 and t['first_collect']:
                out['cyc'].append(te - int(t['t0']))
                out['out_'].append(int(t['first_collect']) - int(t['t0']))
                out['fill'].append(int(t['last_collect']) - int(t['first_collect']))
                out['back'].append(te - int(t['last_collect']))
                out['load'].append(load); out['wait'].append(int(t['wait_rounds'] or 0))
    return out


def main():
    agg = collections.defaultdict(list)
    print('| match g | map | W/L | side | opening carriers: first well type Mn/Ad/none | walk to first well (median) | extra moves vs nearest '
          'well of that type (sum) | rounds to first collect (median) | first trips died | first Mn deposit | Mn dep r50/r100 | '
          'Ad dep r50/r100 | trip cycle / out / fill / back (median, trips started <= r100) | load |')
    print('|' + '---|' * 14)
    for G in games():
        for s, who in ((G['us'], 'us'), (G['them'], 'them')):
            a = analyse(G, s)
            op = a['open']
            nm = sum(1 for o in op if o['typ'] == 2); na = sum(1 for o in op if o['typ'] == 1); nn = sum(1 for o in op if o['typ'] == 0)
            ex = [o['extra'] for o in op if o['extra'] is not None]
            died = sum(1 for o in op if o['outcome'] in ('death', 'throw'))
            print(f"| {G['m']} g{G['g']} | {G['map']} | {'W' if G['won'] else 'L'} | {who} | {nm}/{na}/{nn} | "
                  f"{fmt(med([o['walk'] for o in op]))} | {sum(ex)} | {fmt(med([o['fc'] for o in op]))} | {died} | "
                  f"{fmt(a['firstMn'])} | {a['dep'][(2, 50)]}/{a['dep'][(2, 100)]} | {a['dep'][(1, 50)]}/{a['dep'][(1, 100)]} | "
                  f"{fmt(med(a['cyc']))} / {fmt(med(a['out_']))} / {fmt(med(a['fill']))} / {fmt(med(a['back']))} | {fmt(med(a['load']))} |")
            if V:
                for o in op: print('   ', o)
            if G['dup']: continue
            k = ('W' if G['won'] else 'L', who)
            agg[k + ('nm',)].append(nm / len(op)); agg[k + ('na',)].append(na / len(op)); agg[k + ('nn',)].append(nn / len(op))
            agg[k + ('extra',)].append(sum(ex) / len(op))
            agg[k + ('fc',)].append(med([o['fc'] for o in op]))
            agg[k + ('died',)].append(died / len(op))
            agg[k + ('firstMn',)].append(a['firstMn'])
            for R in (50, 75, 100, 150):
                agg[k + ('mn', R)].append(a['dep'][(2, R)]); agg[k + ('ad', R)].append(a['dep'][(1, R)])
            agg[k + ('cyc',)] += a['cyc']; agg[k + ('out',)] += a['out_']; agg[k + ('fill',)] += a['fill']
            agg[k + ('back',)] += a['back']; agg[k + ('load',)] += a['load']; agg[k + ('wait',)] += a['wait']
            agg[k + ('ntrips',)].append(len(a['cyc']))
    print('\npooled, distinct games: L = our losses (n=30), W = our wins (n=17)')
    for res in ('L', 'W'):
        for who in ('us', 'them'):
            k = (res, who)
            print(f"  {res} {who:4s} opening first well Mn {mean(agg[k+('nm',)]):.2f} Ad {mean(agg[k+('na',)]):.2f} none "
                  f"{mean(agg[k+('nn',)]):.2f} | extra moves/carrier {mean(agg[k+('extra',)]):.2f} | first collect med "
                  f"{med(agg[k+('fc',)])} | first trip died {mean(agg[k+('died',)]):.2f} | first Mn deposit med "
                  f"{med(agg[k+('firstMn',)])} | Mn dep r50/75/100/150 med {med(agg[k+('mn',50)])}/{med(agg[k+('mn',75)])}/"
                  f"{med(agg[k+('mn',100)])}/{med(agg[k+('mn',150)])} sum {sum(agg[k+('mn',100)])} | Ad dep r50/100 med "
                  f"{med(agg[k+('ad',50)])}/{med(agg[k+('ad',100)])} sum r100 {sum(agg[k+('ad',100)])}")
            print(f"           deposit trips started<=r100: n {sum(agg[k+('ntrips',)])} cycle {med(agg[k+('cyc',)])} out "
                  f"{med(agg[k+('out',)])} fill {med(agg[k+('fill',)])} back {med(agg[k+('back',)])} load {med(agg[k+('load',)])} "
                  f"wait {med(agg[k+('wait',)])} (mean cycle {mean(agg[k+('cyc',)]):.1f}, mean load {mean(agg[k+('load',)]):.1f})")


if __name__ == '__main__':
    main()
