"""a2_islfight: where launcher contacts happen relative to islands, per team and phase window, over the losses (and
wins with --wins). A contact turn is a launcher turn with an enemy launcher within r2 20 (sa_L enemy_L_20 > 0).
own-isl = the launcher stands within r2 4 of its own team's island (heal range, RULES 8.1); at-their-isl = an
enemy-held island tile within r2 16 (the enemy fights next to its heal zone). hp = own launcher hp at contact (200 max);
hp ratio = (own hp + ally_L_hp_sum20) / enemy_L_hp_sum20 summed over contact turns.
Usage: python3 -I a2_islfight.py [--wins] [--per-game]"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
WIN = [(0, 300), (300, 600), (600, 1000), (1000, 2100)]


def i(x, d=-1):
    try:
        return int(x)
    except ValueError:
        return d


def run(m, g, side):
    acc = collections.defaultdict(collections.Counter)
    for r in A.sa_iter(m, g, side, 'L', ['round', 'hp', 'enemy_L_20', 'ally_L_hp_sum20', 'enemy_L_hp_sum20',
                                        'd2_island_own', 'd2_island_enemy']):
        en = i(r['enemy_L_20'], 0)
        if en <= 0:
            continue
        rn = int(r['round'])
        w = next(x for x in WIN if x[0] <= rn < x[1])
        c = acc[w]
        c['contact'] += 1
        io, ie = i(r['d2_island_own']), i(r['d2_island_enemy'])
        if 0 <= io <= 4: c['own'] += 1
        if 0 <= ie <= 16: c['theirs'] += 1
        hp = i(r['hp'], 0)
        c['hp'] += hp
        c['mine_hp'] += hp + i(r['ally_L_hp_sum20'], 0)
        c['their_hp'] += i(r['enemy_L_hp_sum20'], 0)
    return acc


def fmt(c):
    n = c['contact'] or 1
    return (f"contact {c['contact']:6d} own-isl {c['own'] / n:.2f} at-their-isl {c['theirs'] / n:.2f} "
            f"hp {c['hp'] / n:.0f} hp-ratio {c['mine_hp'] / max(1, c['their_hp']):.2f}")


def main():
    kinds = ('Lc', 'Lm', 'W') if '--wins' in sys.argv else ('Lc', 'Lm')
    pool = collections.defaultdict(collections.Counter)
    for m, g, k in A.ALL:
        if k not in kinds:
            continue
        d = A.G(m, g)
        for who in ('us', 'them'):
            acc = run(m, g, d[who])
            for w, c in acc.items():
                pool[(k, who, w)].update(c)
                pool[('L' if k != 'W' else 'W', who, w)].update(c)
                if '--per-game' in sys.argv:
                    print(f"{A.label(m, g)} {k} {who:4s} r{w[0]}-{w[1] - 1}: {fmt(c)}")
    for k in ('Lc', 'Lm', 'L', 'W'):
        if not any(key[0] == k for key in pool):
            continue
        print(f"== pooled {k}")
        for w in WIN:
            for who in ('us', 'them'):
                c = pool.get((k, who, w))
                if c:
                    print(f"  r{w[0]}-{w[1] - 1} {who:4s} {fmt(c)}")


if __name__ == '__main__':
    main()
