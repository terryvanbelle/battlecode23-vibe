# Our carriers' fatal trips (trips.csv, outcome death, t_end <= RMAX, default 150): the per-trip token counts (codes,
# carrier states "!GCWSXRDFVTKQEYP": F flee, G go to well, C collect, W wait, X explore, ...). A flee-return trip has
# F >= 5 and G + X + W + C >= 5 (it fled and came back for the same work); an explore trip has X >= 10. Per game and
# pooled over losses and wins. Also the mean turns of each token per fatal trip.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def parse(s):
    c = collections.Counter()
    for kv in filter(None, s.split(';')):
        k, v = kv.split('='); c[k] += int(v)
    return c


if __name__ == '__main__':
    print(f'r <= {RMAX}; our carriers fatal trips')
    print('| game | res | fatal trips | flee-return | explore X>=10 | mean F | mean X | mean G | mean C+W |')
    print('|---|---|---|---|---|---|---|---|---|')
    agg = {r: collections.Counter() for r in 'WL'}
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        res = 'W' if G['won'] else 'L'; c = collections.Counter()
        for t in rd(G['m'], 'trips'):
            if int(t['game']) != G['g'] or t['side'] != G['us'] or t['outcome'] != 'death' or int(t['t_end']) > RMAX: continue
            k = parse(t['codes'])
            c['n'] += 1; c['F'] += k['F']; c['X'] += k['X']; c['G'] += k['G']; c['CW'] += k['C'] + k['W']
            c['fr'] += k['F'] >= 5 and k['G'] + k['X'] + k['W'] + k['C'] >= 5
            c['ex'] += k['X'] >= 10
        agg[res].update(c)
        m = lambda k: f"{c[k]/c['n']:.1f}" if c['n'] else '-'
        print(f"| {label(G)} | {res} | {c['n']} | {c['fr']} | {c['ex']} | {m('F')} | {m('X')} | {m('G')} | {m('CW')} |")
    for res in 'LW':
        c = agg[res]; m = lambda k: f"{c[k]/c['n']:.1f}" if c['n'] else '-'
        print(f"{res}: fatal trips {c['n']}, flee-return {c['fr']}, explore X>=10 {c['ex']}; mean F {m('F')} X {m('X')} G {m('G')} C+W {m('CW')}")
