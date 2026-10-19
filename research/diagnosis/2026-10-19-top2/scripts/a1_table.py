"""a1_table: one row per carlguo866 game: outcome, early economy and army (census + timeline)."""
import sys
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *

def tl(m):
    t = collections.defaultdict(dict)
    for r in rows(m, 'timeline'):
        t[(int(r['game']), r['side'])][int(r['round'])] = r
    return t

hdr = ['match', 'g', 'map', 'WxH', 'nHQ', 'res', 'rnd', 'grp', 'cMn100', 'cAd100', 'C100', 'L100', 'bL100', 'bC100',
       'L150', 'L250', 'dC150', 'dL150', 'kills150', 'turn', 'first_builds_us', 'first_builds_them']
print('\t'.join(hdr))
for m in CARL:
    G = games(m); C = census(m); T = tl(m)
    hqs = collections.Counter((int(r['game']), r['side']) for r in rows(m, 'hq') if r['round'] == '25')
    for g in sorted(G):
        d = G[g]; us, th = d['us'], d['them']
        cu, ct = C[(g, us)], C[(g, th)]
        def at(side, r, k):
            rr = T[(g, side)]
            ks = [x for x in rr if x <= r]
            return int(f(rr[max(ks)][k])) if ks else 0
        grp = 'collapse' if (m, g) in COLLAPSE else ('earlywin' if (m, g) in EARLYWIN else ('win' if d['won'] else 'loss'))
        dC = lambda s: at(s, 150, 'built_C') - at(s, 150, 'alive_C')
        dL = lambda s: at(s, 150, 'built_L') - at(s, 150, 'alive_L')
        row = [m, g, d['map'], '%dx%d' % (d['w'], d['h']), hqs[(g, us)] // 2 if False else hqs[(g, us)] // 1, 'W' if d['won'] else 'L', d['rounds'], grp,
               '%s/%s' % (cu['cMn100'], ct['cMn100']), '%s/%s' % (cu['cAd100'], ct['cAd100']),
               '%s/%s' % (cu['C100'], ct['C100']), '%s/%s' % (cu['L100'], ct['L100']),
               '%d/%d' % (at(us, 100, 'built_L'), at(th, 100, 'built_L')), '%d/%d' % (at(us, 100, 'built_C'), at(th, 100, 'built_C')),
               '%d/%d' % (at(us, 150, 'alive_L'), at(th, 150, 'alive_L')),
               '%s/%s' % (cu['L250'], ct['L250']), '%d/%d' % (dC(us), dC(th)), '%d/%d' % (dL(us), dL(th)),
               '%d/%d' % (at(us, 150, 'kills'), at(th, 150, 'kills')), cu['turn_round'], cu['first_builds'], ct['first_builds']]
        print('\t'.join(str(x) for x in row))
