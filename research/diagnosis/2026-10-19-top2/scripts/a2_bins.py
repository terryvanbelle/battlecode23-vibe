"""a2_bins: phase-window summary of a2_sa.py's sa_bins.csv, us vs them, pooled over losses (carl, max) and wins, and
per game with --per-game. Shares are of launcher-turns (position, ring, island heal range) or of contact turns
(outnumbered, alone). heal/100r and dmg/100r are team HP per 100 rounds. HQ: mean enemy launchers in vision per
HQ-round and the share of HQ-rounds with 3+. Carriers: anchor-carrying share of carrier-turns, placements.
Usage: python3 -I a2_bins.py [--per-game]"""
import sys, os, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
WIN = [(0, 3), (3, 6), (6, 10), (10, 21)]


def load():
    d = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    with open(A.SP + '/a2/out/sa_bins.csv') as fh:
        for r in csv.DictReader(fh):
            b = int(r['bin'])
            for lo, hi in WIN:
                if lo <= b < hi:
                    w = (lo, hi)
            key = (int(r['match']), int(r['game']))
            d[key][(r['who'], w)].update({k: int(v) for k, v in r.items() if k not in ('match', 'game', 'who', 'bin')})
            d[key][(r['who'], w)]['bins'] += 1
    return d


def line(c):
    lt = c['L_turns'] or 1; ct = c['L_contact'] or 1; h = c['H_rounds'] or 1; cc = c['C_turns'] or 1; nb = c['bins'] or 1
    return (f"L/rnd {lt / (100 * nb):.1f} home/mid/far {c['L_home'] / lt:.2f}/{c['L_mid'] / lt:.2f}/{c['L_far'] / lt:.2f} ring {c['L_ring'] / lt:.2f} "
            f"isl {c['L_isl'] / lt:.2f} | heal/100r {c['L_heal'] / nb:.0f} dmg/100r {c['L_dmg'] / nb:.0f} | contact {c['L_contact'] / lt:.2f} "
            f"outn {c['L_outn'] / ct:.2f} alone {c['L_alone'] / ct:.2f} ahead2 {c['L_ahead'] / ct:.2f} | HQ eL34 {c['H_eL34'] / h:.2f} press3 {c['H_press3'] / h:.2f} "
            f"eL9 {c['H_eL9'] / h:.2f} | C/rnd {c['C_turns'] / (100 * nb):.1f} anchor {c['C_anchor'] / cc:.3f} place {c['C_place']} threat {c['C_threat'] / cc:.3f}")


def main():
    d = load()
    pool = collections.defaultdict(collections.Counter)
    for m, g, k in A.ALL:
        if (m, g) not in d:
            continue
        if '--per-game' in sys.argv:
            print(f"== {A.label(m, g)} ({k}, {A.G(m, g)['rounds']})")
        for w in WIN:
            for who in ('us', 'them'):
                c = d[(m, g)].get((who, w))
                if not c:
                    continue
                if '--per-game' in sys.argv:
                    print(f"  r{w[0] * 100}-{w[1] * 100 - 1} {who:4s} {line(c)}")
                pool[(k, who, w)].update(c)
                pool[('L' if k != 'W' else 'W', who, w)].update(c)
    for k in ('Lc', 'Lm', 'L', 'W'):
        print(f"== pooled {k}")
        for w in WIN:
            for who in ('us', 'them'):
                c = pool.get((k, who, w))
                if c:
                    print(f"  r{w[0] * 100}-{w[1] * 100 - 1} {who:4s} {line(c)}")


if __name__ == '__main__':
    main()
