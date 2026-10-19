"""a3_closs.py: carriers lost before round R (default 100), both teams (deaths.csv, trips.csv, map).
Per side, distinct losses / wins: count, cause and killer type, where (d2 to the victim's nearest own HQ; prog = sqrt(d own)/(sqrt(d own)+sqrt(d enemy)), nearest HQs), whether
the victim's current or last trip well is a 'home' well (r2 <= C.HOT_HOME_D2 = 64 of an own HQ, never marked hot,
Carrier.frontGate), cargo lost (Ad/Mn), age at death, our last telemetry token (deaths.csv last_token), and the round of
the first carrier death. Per game listing with -v.
Usage: python3 -I a3_closs.py [R] [-v]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *

R = int([a for a in sys.argv[1:] if a.isdigit()][0]) if any(a.isdigit() for a in sys.argv[1:]) else 100
V = '-v' in sys.argv


def lastwell(G, side):
    """{carrier: [(t0, t_end, well, type)]}"""
    out = collections.defaultdict(list)
    for t in trips(G, side):
        if t['well_x']:
            out[int(t['carrier'])].append((int(t['t0']), int(t['t_end']), (int(t['well_x']), int(t['well_y'])), int(t['well_type'] or 0)))
    return out


def main():
    agg = collections.defaultdict(collections.Counter)
    lists = collections.defaultdict(list)
    for G in games():
        for who in ('us', 'them'):
            s = G[who]
            lw = lastwell(G, s)
            hqs = G['hqs'][s]
            ds = [d for d in deaths(G, s) if d['type'] == 'C' and int(d['round']) <= R]
            if V and ds:
                print(label(G), 'W' if G['won'] else 'L', who, len(ds), 'first', min(int(d['round']) for d in ds))
            if G['dup']: continue
            k = ('W' if G['won'] else 'L', who)
            a = agg[k]
            a['games'] += 1
            for d in ds:
                rnd = int(d['round']); cid = int(d['id']); p = (int(d['x']), int(d['y']))
                a['n'] += 1
                a['cause:' + d['cause'] + '/' + (d['killer_type'] or '-')] += 1
                hd = min(d2(h, p) for h in hqs)
                a['hq_d2<=64' if hd <= 64 else 'hq_d2>64'] += 1
                w = [x for x in lw.get(cid, []) if x[0] <= rnd]
                if w:
                    well = w[-1][2]; wt = w[-1][3]
                    whd = min(d2(h, well) for h in hqs)
                    a['well_home' if whd <= 64 else 'well_front'] += 1
                    a['well_Mn' if wt == 2 else 'well_Ad'] += 1
                    if d2(p, well) <= 20: a['died_within_r2_20_of_well'] += 1
                else:
                    a['no_well_yet'] += 1
                a['cargo_Ad'] += int(d['cargo_Ad'] or 0); a['cargo_Mn'] += int(d['cargo_Mn'] or 0)
                a['age_sum'] += int(d['age'] or 0)
                if who == 'us': a['tok:' + (d['last_token'] or '?')] += 1
                lists[k].append(rnd)
                eh = min(d2(h, p) for h in G['hqs'][G['them' if who == 'us' else 'us']])
                pr = hd ** 0.5 / (hd ** 0.5 + eh ** 0.5) if hd + eh > 0 else 0.5     # own-side progress (0 own HQ, 1 theirs)
                a['prog<0.3' if pr < 0.3 else 'prog0.3-0.5' if pr < 0.5 else 'prog>=0.5'] += 1
                if int(d['age'] or 0) <= 10: a['age<=10'] += 1
            if ds: lists[k + ('first',)].append(min(int(d['round']) for d in ds))
    print(f'carriers lost by r{R}, distinct games')
    keys = ['games', 'n', 'hq_d2<=64', 'hq_d2>64', 'prog<0.3', 'prog0.3-0.5', 'prog>=0.5', 'well_home', 'well_front', 'well_Mn',
            'well_Ad', 'no_well_yet', 'age<=10', 'died_within_r2_20_of_well', 'cargo_Mn', 'cargo_Ad']
    print('| group | ' + ' | '.join(keys) + ' | mean age | first death (median round) | causes | our last tokens |')
    print('|' + '---|' * (len(keys) + 5))
    for k in (('L', 'us'), ('L', 'them'), ('W', 'us'), ('W', 'them')):
        a = agg[k]
        causes = ', '.join(f"{c[6:]} {v}" for c, v in a.most_common() if c.startswith('cause:'))
        toks = ', '.join(f"{c[4:]} {v}" for c, v in a.most_common() if c.startswith('tok:'))
        print(f"| {k[0]} {k[1]} | " + ' | '.join(str(a[x]) for x in keys) + f" | {a['age_sum']/max(1,a['n']):.0f} | "
              f"{med(lists[k + ('first',)])} | {causes} | {toks} |")


if __name__ == '__main__':
    main()
