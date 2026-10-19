"""a2_cstate: our carriers' anchor states from telemetry (extract tele_states.csv, type C, our side only) per phase
(mid r151-600, late r601+): T take, K carrying to a located island, Q to a predicted island, E holding an anchor with
no target (Carrier.java scoutMove), Y returning the anchor after C.ANCHOR_TIMEOUT, P place. With census anchors
built / placed / lost for both teams. Usage: python3 -I a2_cstate.py"""
import sys, os, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
LET = 'TKQEYP'


def main():
    pool = collections.defaultdict(collections.Counter)
    anc = collections.defaultdict(collections.Counter)
    print('game | k | anchors built/placed/lost us | them | carrier anchor-state turns mid: T K Q E Y P | late: T K Q E Y P')
    for m, g, k in A.ALL:
        d = A.G(m, g)
        cnt = collections.Counter()
        for r in A.rows(m, 'tele_states'):
            if int(r['game']) != g or r['side'] != d['us'] or r['type'] != 'C' or r['phase'] not in ('mid', 'late'):
                continue
            if r['letter'] in LET:
                cnt[(r['phase'], r['letter'])] += int(r['turns'])
        cu, ct = A.census(m, g)
        kk = 'L' if k != 'W' else 'W'
        for who, c in (('us', cu), ('them', ct)):
            for f in ('anchors_built', 'anchors_placed', 'anchors_lost'):
                anc[(kk, who)][f] += int(c[f] or 0)
        for key, v in cnt.items():
            pool[kk][key] += v
        f = lambda ph: ' '.join(str(cnt[(ph, x)]) for x in LET)
        print(f"{A.label(m, g)} | {k} | {cu['anchors_built']}/{cu['anchors_placed']}/{cu['anchors_lost']} | "
              f"{ct['anchors_built']}/{ct['anchors_placed']}/{ct['anchors_lost']} | {f('mid')} | {f('late')}")
    for kk in ('L', 'W'):
        u, t = anc[(kk, 'us')], anc[(kk, 'them')]
        f = lambda ph: ' '.join(f"{x} {pool[kk][(ph, x)]}" for x in LET)
        print(f"pooled {kk}: anchors built/placed/lost us {u['anchors_built']}/{u['anchors_placed']}/{u['anchors_lost']} "
              f"(placed/built {u['anchors_placed'] / max(1, u['anchors_built']):.2f}), them {t['anchors_built']}/"
              f"{t['anchors_placed']}/{t['anchors_lost']} ({t['anchors_placed'] / max(1, t['anchors_built']):.2f}) | "
              f"mid {f('mid')} | late {f('late')}")


if __name__ == '__main__':
    main()
