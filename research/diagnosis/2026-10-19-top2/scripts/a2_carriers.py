"""a2_carriers: carrier deaths by window (deaths.csv, prog from the dead carrier's own HQ) and our HQ build-loop exit
codes by telemetry phase (tele_states.csv, HQ letters: p poor, t threatened (carrier withheld), c carrier cap,
a anchor reserve, w batch wait, s no spawn tile, b/g/. loop exits). Usage: python3 -I a2_carriers.py"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
WIN = [(0, 300), (300, 600), (600, 1000), (1000, 2001)]


def wn(r):
    for a, b in WIN:
        if a <= r < b:
            return f'{a}-{b - 1}'


def main():
    pool = collections.defaultdict(collections.Counter)
    hq = collections.defaultdict(collections.Counter)
    print('game | k | carrier deaths us/them per window (ours at home prog<0.35) | HQ letters mid (r151-600) | late (r601+)')
    for m, g, k in A.ALL:
        d = A.G(m, g)
        s = collections.defaultdict(collections.Counter)
        for x in A.rows(m, 'deaths'):
            if int(x['game']) != g or x['type'] != 'C':
                continue
            w = wn(int(x['round']))
            who = 'us' if x['side'] == d['us'] else 'them'
            s[w][who] += 1
            p = A.num(x['prog'])
            if p is not None:
                if x['side'] == 'B':
                    p = 1 - p
                if p < 0.35:
                    s[w][who + '_home'] += 1
            s[w][who + '_Mn'] += int(x['cargo_Mn'] or 0)
            s[w][who + '_Ad'] += int(x['cargo_Ad'] or 0)
            s[w][who + '_anch'] += int(x['anchors'] or 0)
        kk = 'L' if k != 'W' else 'W'
        for w in s:
            pool[(kk, w)].update(s[w])
        ph = collections.defaultdict(collections.Counter)
        for r in A.rows(m, 'tele_states'):
            if int(r['game']) != g or r['side'] != d['us'] or r['type'] != 'H' or r['phase'] not in ('mid', 'late'):
                continue
            ph[r['phase']][r['letter']] += int(r['turns'])
            hq[(kk, r['phase'])][r['letter']] += int(r['turns'])
        def sh(c):
            n = sum(c.values())
            return ' '.join(f"{l}{v / n:.2f}" for l, v in c.most_common(4)) if n else '-'
        print(f"{A.label(m, g)} | {k} | " + ' '.join(f"{w}:{s[w]['us']}({s[w]['us_home']})/{s[w]['them']}" for w in sorted(s, key=lambda z: int(z.split('-')[0])))
              + f" | {sh(ph['mid'])} | {sh(ph['late'])}")
    for kk in ('L', 'W'):
        print(f"== pooled {kk}")
        for a, b in WIN:
            w = f'{a}-{b - 1}'
            c = pool[(kk, w)]
            print(f"  {w}: carrier deaths us/them {c['us']}/{c['them']} (ours at home {c['us_home']}, theirs at their home {c['them_home']}); "
                  f"cargo lost Mn {c['us_Mn']}/{c['them_Mn']} Ad {c['us_Ad']}/{c['them_Ad']}; anchors lost {c['us_anch']}/{c['them_anch']}")
        for p in ('mid', 'late'):
            c = hq[(kk, p)]; n = sum(c.values())
            print(f"  HQ letters {p}: " + ' '.join(f"{l} {v / n:.2f}" for l, v in c.most_common()))


if __name__ == '__main__':
    main()
