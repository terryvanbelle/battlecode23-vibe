"""synth_v1_carriers.py: re-check of the carrier-squeeze claims (analysts 0, 1, 3).

For distinct losses and wins, both sides, carriers dead by round R (deaths.csv type C):
  n, killed by a launcher, within d2 64 of the victim's nearest own HQ, within r2 34 of one of the victim side's own
  mana wells (nearer its HQs than the enemy's), and of those how many are at a well Carrier.frontGate calls "home"
  (never hot: C.HOT_HOME_D2 64, C.HOT_FRONT_PCT 36, true HQ positions).
Our trips (trips.csv) started by R to our own mana wells, by frontGate class: trips, deposits, deaths.
Our fatal trips by R with telemetry codes F>=3 and (G+C+W)>=3 (flee then back to work: the flee-and-return loop).
Usage: python3 -I synth_v1_carriers.py [R=150]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_common import *

R = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def codes(s):
    out = {}
    for kv in (s or '').split(';'):
        if '=' in kv:
            k, v = kv.split('=')
            out[k] = int(v)
    return out


def side_stats(G, side):
    hqs = G['hqs'][side]
    ehq = G['hqs'][other(side)]
    g2 = dict(G, us=side, them=other(side))
    mw = our_mn_wells(g2)
    n = byL = nearHQ = atWell = atHome = 0
    for r in deaths(G, side):
        if r['type'] != 'C' or int(r['round']) > R: continue
        n += 1
        byL += r['cause'] == 'launcher'
        p = (int(r['x']), int(r['y']))
        nearHQ += mind2(p, hqs) <= 64
        ws = [w for w in mw if d2(p, w['xy']) <= 34]
        if ws:
            atWell += 1
            atHome += any(not w['front'] for w in ws)
    return dict(n=n, byL=byL, nearHQ=nearHQ, atWell=atWell, atHome=atHome)


def our_trips(G):
    mw = {w['xy']: w for w in our_mn_wells(G)}
    out = collections.Counter()
    loop = fatal = 0
    for t in trips(G, G['us']):
        if int(t['t0']) > R: continue
        if t['outcome'] == 'death':
            fatal += 1
            c = codes(t['codes'])
            if c.get('F', 0) >= 3 and c.get('G', 0) + c.get('C', 0) + c.get('W', 0) >= 3: loop += 1
        if not t['well_x'] or t['well_type'] not in ('2', 'Mn', 'MANA'): continue
        xy = (int(t['well_x']), int(t['well_y']))
        if xy not in mw: continue
        cls = 'front' if mw[xy]['front'] else 'home'
        out[cls + '_trips'] += 1
        out[cls + '_' + t['outcome']] += 1
    out['fatal'] = fatal
    out['loop'] = loop
    return out


def main():
    print(f'# synth_v1_carriers R={R}')
    for name, gs in (('losses (30 distinct)', losses()), ('wins (17)', wins())):
        tot = {s: collections.Counter() for s in ('us', 'them')}
        tr = collections.Counter()
        games_home_well = 0
        for G in gs:
            for s, side in (('us', G['us']), ('them', G['them'])):
                tot[s].update(side_stats(G, side))
            tr.update(our_trips(G))
            games_home_well += any(not w['front'] for w in our_mn_wells(G))
        print(f'\n## {name}')
        for s in ('us', 'them'):
            t = tot[s]
            print(f"  {s:4}: carriers dead<=r{R} {t['n']}, by launcher {t['byL']}, within d2 64 of own HQ {t['nearHQ']}, "
                  f"within r2 34 of own Mn well {t['atWell']} (of which at a frontGate-'home' well {t['atHome']})")
        print(f"  our trips to own Mn wells started <=r{R}: home wells {tr['home_trips']} trips, {tr['home_deposit']} deposits, "
              f"{tr['home_death']} deaths; front wells {tr['front_trips']} trips, {tr['front_deposit']} deposits, {tr['front_death']} deaths")
        print(f"  our fatal trips <=r{R}: {tr['fatal']}, of which flee-and-return (F>=3 and G+C+W>=3): {tr['loop']}")
        print(f"  games where at least one own-side Mn well is frontGate-'home': {games_home_well}/{len(gs)}")
    # well type encoding check
    vals = collections.Counter(t['well_type'] for G in distinct() for t in trips(G, G['us']))
    print('\nwell_type values in trips.csv:', dict(vals))


main()
