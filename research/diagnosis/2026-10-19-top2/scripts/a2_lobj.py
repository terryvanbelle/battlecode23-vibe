"""a2_lobj: our launchers' telemetry (tele_states.csv, type L): share of launcher-turns by objective kind
(sighting = shared sighting / recall / home guard; enemy_island; enemy_hq = siege ring, raid well or contested-well
site; centre = no target or a mending island) and by mode (N idle, M march, S stand (ring hold / site hold / mend hold),
F fight, H hold-and-shoot), per telemetry phase (open r1-150, mid r151-600, late r601+), pooled over losses / wins.
Usage: python3 -I a2_lobj.py [--per-game]"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A


def main():
    pool = collections.defaultdict(collections.Counter)
    for m, g, k in A.ALL:
        d = A.G(m, g)
        pg = collections.defaultdict(collections.Counter)
        for r in A.rows(m, 'tele_states'):
            if int(r['game']) != g or r['side'] != d['us'] or r['type'] != 'L' or r['phase'] == 'all':
                continue
            det = dict(x.split('=') for x in r['detail'].split(';'))
            n = int(r['turns'])
            for c in (pool[(('L' if k != 'W' else 'W'), r['phase'])], pg[r['phase']]):
                c['n'] += n
                c['obj_' + det['obj']] += n
                c['mode_' + r['letter']] += n
                c[det['obj'] + '_' + r['letter']] += n
        if '--per-game' in sys.argv:
            for ph in ('mid', 'late'):
                c = pg[ph]
                if c['n']:
                    print(f"{A.label(m, g)} {k} {ph}: " + ' '.join(f"{o} {c['obj_' + o] / c['n']:.2f}" for o in ('sighting', 'enemy_island', 'enemy_hq', 'centre'))
                          + f" | S@hq {c['enemy_hq_S'] / c['n']:.2f}")
    for kk in ('L', 'W'):
        for ph in ('open', 'mid', 'late'):
            c = pool[(kk, ph)]
            if not c['n']:
                continue
            print(f"{'losses' if kk == 'L' else 'wins'} {ph} (launcher-turns {c['n']}): obj " +
                  ' '.join(f"{o} {c['obj_' + o] / c['n']:.2f}" for o in ('sighting', 'enemy_island', 'enemy_hq', 'centre')) +
                  ' | mode ' + ' '.join(f"{l} {c['mode_' + l] / c['n']:.2f}" for l in 'NMSFHGW') +
                  f" | stand at enemy_hq objective {c['enemy_hq_S'] / c['n']:.2f}")


if __name__ == '__main__':
    main()
