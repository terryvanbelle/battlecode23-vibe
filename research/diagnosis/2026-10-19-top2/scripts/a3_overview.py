"""a3_overview.py: per-game opening economy table, us/them (timeline.csv every 10 rounds; robots.csv; deaths.csv; map).
Columns: map features (area, HQs, walk moves HQ->nearest Mn well, Ad well), Mn and Ad collected by r50/r100, launchers
and carriers built by r50/r100, carriers lost by r100, launchers alive at r100.  Usage: python3 -I a3_overview.py [--csv]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *


def row(G):
    out = dict(G=G)
    for s, k in ((G['us'], 'u'), (G['them'], 't')):
        tl = timeline(G, s)
        mf = mapfeat(G, s)
        out[k + 'walk_mn'] = mf['walk_mn']; out[k + 'walk_ad'] = mf['walk_ad']; out[k + 'd2_mn'] = mf['d2_mn']
        for r in (30, 50, 100, 150):
            out[f'{k}Mn{r}'] = int(tl[r]['coll_Mn']) if r in tl else None
            out[f'{k}Ad{r}'] = int(tl[r]['coll_Ad']) if r in tl else None
            out[f'{k}La{r}'] = int(tl[r]['alive_L']) if r in tl else None
            out[f'{k}Ca{r}'] = int(tl[r]['alive_C']) if r in tl else None
        rb = robots(G, s)
        for r in (50, 100):
            out[f'{k}Lb{r}'] = sum(1 for x in rb if x['type'] == 'L' and int(x['born']) <= r)
            out[f'{k}Cb{r}'] = sum(1 for x in rb if x['type'] == 'C' and int(x['born']) <= r)
        out[k + 'Cd100'] = sum(1 for x in deaths(G, s) if x['type'] == 'C' and int(x['round']) <= 100)
    out['area'] = G['W'] * G['H']
    return out


def main():
    rows = [row(G) for G in games()]
    if '--csv' in sys.argv:
        keys = [k for k in rows[0] if k != 'G']
        print('match,game,map,won,dup,nhq,' + ','.join(keys))
        for r in rows:
            G = r['G']
            print(f"{G['m']},{G['g']},{G['map']},{G['won']},{int(G['dup'])},{G['nhq']}," + ','.join(fmt(r[k]) for k in keys))
        return
    print('| match g | map | W x H | HQs | walk Mn/Ad (us) | walk Mn (them) | W/L | Mn@50 | Mn@100 | Ad@100 | L built r50 | '
          'L built r100 | C built r100 | C lost r100 | L alive r100 |')
    print('|' + '---|' * 15)
    for r in rows:
        G = r['G']
        print(f"| {G['m']} g{G['g']}{' (dup)' if G['dup'] else ''} | {G['map']} | {G['W']}x{G['H']} | {G['nhq']} | "
              f"{r['uwalk_mn']}/{r['uwalk_ad']} | {r['twalk_mn']} | {'W' if G['won'] else 'L'} | {r['uMn50']}/{r['tMn50']} | "
              f"{r['uMn100']}/{r['tMn100']} | {r['uAd100']}/{r['tAd100']} | {r['uLb50']}/{r['tLb50']} | "
              f"{r['uLb100']}/{r['tLb100']} | {r['uCb100']}/{r['tCb100']} | {r['uCd100']}/{r['tCd100']} | "
              f"{r['uLa100']}/{r['tLa100']} |")
    # pooled medians, distinct games
    for lab, sel in (('losses', lambda G: not G['won']), ('wins', lambda G: G['won'])):
        rs = [r for r in rows if sel(r['G']) and not r['G']['dup']]
        print(f"\n{lab} (distinct n={len(rs)}): median us/them")
        for k in ('Mn30', 'Mn50', 'Mn100', 'Mn150', 'Ad50', 'Ad100', 'Lb50', 'Lb100', 'Cb50', 'Cb100', 'Cd100', 'La100', 'Ca100'):
            print(f"  {k:6s} {fmt(med([r['u' + k] for r in rs]),1)} / {fmt(med([r['t' + k] for r in rs]),1)}"
                  f"   (sum {sum(r['u'+k] or 0 for r in rs)} / {sum(r['t'+k] or 0 for r in rs)})")


if __name__ == '__main__':
    main()
