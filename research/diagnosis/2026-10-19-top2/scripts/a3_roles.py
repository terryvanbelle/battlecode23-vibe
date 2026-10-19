"""a3_roles.py: who collects our adamantium, rounds 1-R (default 150). Joins our per-turn collects (sa_C collect_res,
collect_amt) to our telemetry role bit (tele_turns code_bcc & 1: 1 = Mn role, 0 = Ad role; Telemetry.carrierCode) and
counts: Ad and Mn collected by Ad-role and by Mn-role carriers, carriers born with the Ad role, carrier-turns per role,
and the collecting turns spent on Ad wells. Opponent: Ad and Mn collected (no roles).
Usage: python3 -I a3_roles.py [R]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *

RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def ours(G):
    tt = tele(G['m'], 300)
    rows = sa(G['m'], G['g'], G['us'], 'C', 300)
    c = collections.Counter(); first_role = {}; nturn = collections.Counter(); unk = 0
    for r in rows:
        if r['round'] > RMAX: break
        k = (G['g'], r['round'], r['id'])
        tv = tt.get(k)
        role = None
        if tv and tv[1] is not None and tv[1] < 32:
            role = 'Mn' if tv[1] & 1 else 'Ad'
            if r['id'] not in first_role: first_role[r['id']] = role
        nturn[role] += 1
        if r['collect_res'] in ('Ad', 'Mn') and r['collect_amt']:
            c[(role, r['collect_res'])] += r['collect_amt']
            c[(role, r['collect_res'], 'turns')] += 1
    return c, first_role, nturn


def theirs(G):
    c = collections.Counter()
    for r in sa(G['m'], G['g'], G['them'], 'C', 300):
        if r['round'] > RMAX: break
        if r['collect_res'] in ('Ad', 'Mn') and r['collect_amt']:
            c[r['collect_res']] += r['collect_amt']
    return c


def main():
    print(f'rounds 1-{RMAX}')
    print('| match g | map | W/L | carriers born Ad-role / all | carrier-turns Ad role / Mn role / no code | Ad by Ad-role | Ad by Mn-role | '
          'Mn by Mn-role | Mn by Ad-role | our Ad / Mn | their Ad / Mn |')
    print('|' + '---|' * 11)
    tot = collections.defaultdict(collections.Counter)
    for G in games():
        c, fr, nt = ours(G); th = theirs(G)
        nad = sum(1 for v in fr.values() if v == 'Ad')
        print(f"| {G['m']} g{G['g']} | {G['map']} | {'W' if G['won'] else 'L'} | {nad}/{len(fr)} | {nt['Ad']}/{nt['Mn']}/{nt[None]} | "
              f"{c[('Ad','Ad')]} | {c[('Mn','Ad')]} | {c[('Mn','Mn')]} | {c[('Ad','Mn')]} | "
              f"{c[('Ad','Ad')]+c[('Mn','Ad')]+c[(None,'Ad')]} / {c[('Ad','Mn')]+c[('Mn','Mn')]+c[(None,'Mn')]} | {th['Ad']} / {th['Mn']} |")
        if G['dup']: continue
        k = 'W' if G['won'] else 'L'
        tot[k]['n'] += 1; tot[k]['bornAd'] += nad; tot[k]['born'] += len(fr)
        for kk, v in c.items(): tot[k][kk] += v
        for kk, v in nt.items(): tot[k][('turns', kk)] += v
        tot[k]['thAd'] += th['Ad']; tot[k]['thMn'] += th['Mn']
    print('\nsums over distinct games')
    for k in ('L', 'W'):
        t = tot[k]
        adall = t[('Ad', 'Ad')] + t[('Mn', 'Ad')] + t[(None, 'Ad')]
        mnall = t[('Ad', 'Mn')] + t[('Mn', 'Mn')] + t[(None, 'Mn')]
        print(f"  {k} n={t['n']}: carriers born Ad-role {t['bornAd']}/{t['born']} ({t['bornAd']/t['born']:.3f}); carrier-turns Ad role "
              f"{t[('turns','Ad')]} Mn role {t[('turns','Mn')]} none {t[('turns',None)]} (Ad share {t[('turns','Ad')]/(t[('turns','Ad')]+t[('turns','Mn')]):.3f})")
        print(f"     our Ad {adall} (by Ad-role {t[('Ad','Ad')]}, by Mn-role {t[('Mn','Ad')]}, no code {t[(None,'Ad')]}), our Mn {mnall} "
              f"(by Ad-role {t[('Ad','Mn')]}); Ad share of our collection {adall/(adall+mnall):.3f}; theirs Ad {t['thAd']} Mn {t['thMn']} "
              f"(share {t['thAd']/(t['thAd']+t['thMn']):.3f}); collect turns on Ad by Mn-role {t[('Mn','Ad','turns')]}, by Ad-role {t[('Ad','Ad','turns')]}")


if __name__ == '__main__':
    main()
