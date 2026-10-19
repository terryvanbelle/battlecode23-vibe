# Who dies first and where (deaths.csv), per game: our first 6 deaths (type, round, prog from our HQ, our last
# telemetry code letter), deaths by r150 per side and type, and where our carriers die by r150 (prog bands).
# prog in deaths.csv is from side A's HQ; it is flipped for side B so 0 = our HQ.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *


def deaths(G):
    out = []
    for d in rd(G['m'], 'deaths'):
        if int(d['game']) != G['g']: continue
        p = float(d['prog']) if d['prog'] else None
        if p is not None and G['us'] == 'B': p = 1 - p
        out.append(dict(r=int(d['round']), side=d['side'], t=d['type'], prog=p, cause=d['cause'],
                        tok=d['last_token'], hp=d['hp_before'], ktype=d['killer_type'], cargo=int(d['cargo_Mn'] or 0) + int(d['cargo_Ad'] or 0)))
    out.sort(key=lambda x: x['r'])
    return out


if __name__ == '__main__':
    print('| game | res | our first 6 deaths (type r prog token) | dead by r150 us C/L | them C/L | our C deaths r<=150 at prog <0.3 / 0.3-0.6 / >0.6 |')
    print('|---|---|---|---|---|---|')
    tot = {'W': collections.Counter(), 'L': collections.Counter()}
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        D = deaths(G); us = G['us']; res = 'W' if G['won'] else 'L'
        ours = [d for d in D if d['side'] == us and d['cause'] != 'self']
        f6 = ' '.join(f"{d['t']}{d['r']}@{d['prog']:.2f}{d['tok'] or ''}" for d in ours[:6])
        c = collections.Counter((d['side'] == us, d['t']) for d in D if d['r'] <= 150 and d['cause'] != 'self')
        band = collections.Counter(('a' if d['prog'] < 0.3 else 'b' if d['prog'] < 0.6 else 'c') for d in ours
                                   if d['r'] <= 150 and d['t'] == 'C' and d['prog'] is not None)
        print(f"| {label(G)} | {res} | {f6} | {c[(True,'C')]}/{c[(True,'L')]} | {c[(False,'C')]}/{c[(False,'L')]} | "
              f"{band['a']}/{band['b']}/{band['c']} |")
        tot[res]['n'] += 1
        for k in ('C', 'L'):
            tot[res]['us' + k] += c[(True, k)]; tot[res]['th' + k] += c[(False, k)]
        tot[res]['first_C'] += ours[0]['t'] == 'C' if ours else 0
        for b in 'abc': tot[res]['band' + b] += band[b]
    print()
    for res in ('L', 'W'):
        t = tot[res]; n = t['n']
        print(f"{res}: games {n}; dead by r150 per game us C {t['usC']/n:.1f} L {t['usL']/n:.1f}, them C {t['thC']/n:.1f} "
              f"L {t['thL']/n:.1f}; our first death a carrier in {t['first_C']}/{n}; our C deaths r<=150 by prog band "
              f"<0.3 {t['banda']}, 0.3-0.6 {t['bandb']}, >0.6 {t['bandc']}")
