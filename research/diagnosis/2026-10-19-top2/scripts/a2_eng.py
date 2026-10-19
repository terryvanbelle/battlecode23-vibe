"""a2_eng: engagements (engagements.csv) and launcher deaths (deaths.csv) by phase window, us vs them.
Per window: engagements, won/lost, value lost us:them in engagements, exchange (their value lost / ours), launcher deaths
us/them, and where our launchers die: prog from OUR HQ (deaths.csv prog is from team A's HQs; 1 - prog when we are B):
home < 0.35, mid 0.35-0.65, their side > 0.65. Pooled over losses (carl, max) and wins.
Usage: python3 -I a2_eng.py [--per-game]"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
WIN = [(0, 300), (300, 600), (600, 1000), (1000, 2001)]


def wname(r):
    for a, b in WIN:
        if a <= r < b:
            return f'{a}-{b - 1 if b < 2001 else 2000}'


def per_game(m, g):
    d = A.G(m, g)
    us, th = d['us'], d['them']
    s = collections.defaultdict(collections.Counter)
    for e in A.rows(m, 'engagements'):
        if int(e['game']) != g:
            continue
        w = wname(int(e['r0']))
        c = s[w]
        c['eng'] += 1
        res = e['result']
        c['won'] += res == us; c['lost'] += res == th
        c['vl_us'] += int(e['val_lost_' + us]); c['vl_them'] += int(e['val_lost_' + th])
        c['k_us'] += int(e['kills_by_' + us]); c['k_them'] += int(e['kills_by_' + th])
        n_us, n_th = int(e['n' + us + '0']), int(e['n' + th + '0'])
        dn = n_us - n_th
        c['par'] += dn == 0; c['behind'] += dn <= -2; c['ahead'] += dn >= 2
        c['won_behind'] += dn <= -2 and res == us; c['won_par'] += dn == 0 and res == us; c['won_ahead'] += dn >= 2 and res == us
    for x in A.rows(m, 'deaths'):
        if int(x['game']) != g or x['type'] != 'L':
            continue
        w = wname(int(x['round']))
        c = s[w]
        if x['side'] == us:
            c['dL_us'] += 1
            p = A.num(x['prog'])
            if p is None:
                c['dL_us_unk'] += 1
                continue
            if us == 'B':
                p = 1 - p
            c['dL_us_home' if p < 0.35 else 'dL_us_mid' if p <= 0.65 else 'dL_us_far'] += 1
            if x['cause'] == 'hq_aura':
                c['dL_us_aura'] += 1
            if x['spawn_kill'] == '1':
                c['dL_us_spawn'] += 1
        else:
            c['dL_them'] += 1
            p = A.num(x['prog'])
            if p is not None:
                if th == 'B':
                    p = 1 - p
                c['dL_them_home' if p < 0.35 else 'dL_them_mid' if p <= 0.65 else 'dL_them_far'] += 1
            if x['spawn_kill'] == '1':
                c['dL_them_spawn'] += 1
    return s


def fmt(c):
    ex = c['vl_them'] / c['vl_us'] if c['vl_us'] else float('nan')
    return (f"eng {c['eng']} won/lost {c['won']}/{c['lost']} (behind {c['won_behind']}/{c['behind']}, par {c['won_par']}/{c['par']}, "
            f"ahead {c['won_ahead']}/{c['ahead']}) | value lost us/them {c['vl_us']}/{c['vl_them']} exch {ex:.2f} | "
            f"L deaths us/them {c['dL_us']}/{c['dL_them']} | our L deaths home/mid/far {c['dL_us_home']}/{c['dL_us_mid']}/{c['dL_us_far']} "
            f"(aura {c['dL_us_aura']}, spawn {c['dL_us_spawn']}) | their L deaths home/mid/far {c['dL_them_home']}/{c['dL_them_mid']}/{c['dL_them_far']} (spawn {c['dL_them_spawn']})")


def main():
    pg = '--per-game' in sys.argv
    pool = collections.defaultdict(collections.Counter)
    for m, g, k in A.ALL:
        s = per_game(m, g)
        if pg:
            print(f"== {A.label(m, g)} ({k}, {A.G(m, g)['rounds']})")
        for a, b in WIN:
            w = f'{a}-{b - 1 if b < 2001 else 2000}'
            if w in s:
                if pg:
                    print(f"  {w}: {fmt(s[w])}")
                pool[(k, w)].update(s[w])
                pool[('L' if k != 'W' else 'W', w)].update(s[w])
    for k in ('Lc', 'Lm', 'L', 'W'):
        print(f"== pooled {k}")
        for a, b in WIN:
            w = f'{a}-{b - 1 if b < 2001 else 2000}'
            if (k, w) in pool:
                print(f"  {w}: {fmt(pool[(k, w)])}")


if __name__ == '__main__':
    main()
