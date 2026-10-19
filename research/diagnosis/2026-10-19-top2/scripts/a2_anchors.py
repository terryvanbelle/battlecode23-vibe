"""a2_anchors: every anchor placement (sa_C anchor_place) of either team in the 19 games: round, Euclidean progress e
of the tile from the placer's own HQs (d own / (d own + d enemy), nearest HQs), whether any of the placer's HQs was
'pressed' by our c_anc3 rule at the time (hq.csv pressure34 of the current or previous 25-round bucket >= 100), and the
island counts (timeline) of both teams then (placer first). Pooled: placements by the opponent while pressed or behind
on islands, which our HQ gate (HQ.java:68) forbids for us before r1500. Usage: python3 -I a2_anchors.py [--list]"""
import sys, os, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
import a0_common as Z


def pressed_fn(m, g, side):
    pr = collections.defaultdict(dict)
    for r in A.rows(m, 'hq'):
        if int(r['game']) == g and r['side'] == side:
            pr[r['hq_id']][int(r['round'])] = int(r['pressure34'])

    def f(rn):
        b = ((rn - 1) // 25 + 1) * 25
        return any(p.get(b, 0) >= 100 or p.get(b - 25, 0) >= 100 for p in pr.values())
    return f


def main():
    pool = collections.Counter()
    for m, g, k in A.ALL:
        d = A.G(m, g)
        hq = Z.hqs(m, g)
        t = A.timeline(m, g)
        for who in ('us', 'them'):
            side = d[who]
            own, en = hq[side], hq['B' if side == 'A' else 'A']
            pf = pressed_fn(m, g, side)
            for r in A.sa_iter(m, g, side, 'C', ['round', 'x', 'y', 'anchor_place']):
                if r['anchor_place'] in ('', '0'):
                    continue
                rn, x, y = int(r['round']), int(r['x']), int(r['y'])
                du = min(math.hypot(x - a, y - b) for a, b in own); de = min(math.hypot(x - a, y - b) for a, b in en)
                e = du / (du + de) if du + de else 0.5
                pr = pf(rn)
                mine = A.at(t[who], rn)['islands']; other = A.at(t['them' if who == 'us' else 'us'], rn)['islands']
                behind = other > mine
                cls = ('L' if k != 'W' else 'W') + who
                pool[cls] += 1; pool[cls + '_pressed'] += pr; pool[cls + '_behind'] += behind
                pool[cls + '_either'] += pr or behind; pool[cls + '_far'] += e > 0.5; pool[cls + '_pre400'] += rn < 400
                pool[cls + '_pre1500_either'] += (pr or behind) and rn < 1500
                if '--list' in sys.argv:
                    print(f"{A.label(m, g)} {k} {who} r{rn} ({x},{y}) e {e:.2f} pressed {int(pr)} islands {mine}/{other}")
    for cls in ('Lthem', 'Lus', 'Wthem', 'Wus'):
        n = pool[cls]
        if n:
            print(f"{cls}: placements {n}; while pressed {pool[cls + '_pressed']} ({pool[cls + '_pressed'] / n:.2f}), while behind on islands "
                  f"{pool[cls + '_behind']} ({pool[cls + '_behind'] / n:.2f}), either {pool[cls + '_either']} (before r1500: {pool[cls + '_pre1500_either']}); "
                  f"on the far half (e > 0.5) {pool[cls + '_far']}; before r400 {pool[cls + '_pre400']}")


if __name__ == '__main__':
    main()
