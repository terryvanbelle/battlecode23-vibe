# Opening engagements (engagements.csv, r0 <= RMAX, default 200) per game, renamed to us/them: start counts, peak
# counts, joiners, kills, who hit first, prog (0 = our HQ), result. Totals: kills and losses in engagements that start
# with us behind (dN <= -1), level, or ahead (dN >= 1), and the share of engagements where they join more launchers.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200
VERB = '-v' in sys.argv


def engs(G):
    us, th = G['us'], G['them']
    out = []
    for e in rd(G['m'], 'engagements'):
        if int(e['game']) != G['g'] or int(e['r0']) > RMAX: continue
        I = lambda k: int(e[k]) if e[k] != '' else 0
        p = float(e['prog0']) if e['prog0'] else None
        if p is not None and us == 'B': p = 1 - p
        out.append(dict(r0=I('r0'), r1=I('r1'), nU=I('n' + us + '0'), nT=I('n' + th + '0'), pU=I('peak' + us),
                        pT=I('peak' + th), jU=I('join' + us), jT=I('join' + th), kU=I('kills_by_' + us),
                        kT=I('kills_by_' + th), fh={us: 'us', th: 'them'}.get(e['first_hit'], '-'), prog=p,
                        res={us: 'won', th: 'lost'}.get(e['result'], 'draw')))
    return out


if __name__ == '__main__':
    agg = {r: collections.Counter() for r in ('W', 'L')}
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        res = 'W' if G['won'] else 'L'
        E = engs(G)
        if VERB:
            print(f"{label(G)} {res}")
            for e in E[:8]:
                print(f"   r{e['r0']}-{e['r1']} prog {e['prog']:.2f} start {e['nU']}v{e['nT']} peak {e['pU']}v{e['pT']} "
                      f"join {e['jU']}v{e['jT']} kills {e['kU']}v{e['kT']} first {e['fh']} {e['res']}")
        for e in E:
            dn = e['nU'] - e['nT']
            b = 'behind' if dn <= -1 else 'level' if dn == 0 else 'ahead'
            a = agg[res]
            a['n_' + b] += 1; a['kU_' + b] += e['kU']; a['kT_' + b] += e['kT']
            a['peak_more_them'] += e['pT'] > e['pU']; a['peak_more_us'] += e['pU'] > e['pT']; a['n'] += 1
            a['kU'] += e['kU']; a['kT'] += e['kT']
            if e['prog'] is not None and e['prog'] < 0.4: a['home'] += 1; a['kU_home'] += e['kU']; a['kT_home'] += e['kT']
    print(f'engagements starting r <= {RMAX}')
    for res in ('L', 'W'):
        a = agg[res]
        print(f"{res}: n {a['n']}, kills us/them {a['kU']}/{a['kT']}; start behind n {a['n_behind']} kills {a['kU_behind']}/{a['kT_behind']}, "
              f"level n {a['n_level']} kills {a['kU_level']}/{a['kT_level']}, ahead n {a['n_ahead']} kills {a['kU_ahead']}/{a['kT_ahead']}; "
              f"peak them > us in {a['peak_more_them']}, us > them in {a['peak_more_us']}; at prog < 0.4 (our side): n {a['home']} kills {a['kU_home']}/{a['kT_home']}")
