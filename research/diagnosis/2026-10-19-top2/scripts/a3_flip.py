"""a3_flip.py: per loss, the size of the economic hole at r100 against what an opening-economy change could buy.
Columns: win reason and length; Mn gap r100 (timeline coll_Mn); launchers built by r100 us/them (timeline built_L,
cumulative); launchers alive r100; carriers lost r100 us/them; enemy launcher arrival on our main Mn well (a3_arrive);
our Ad excess r100 = our coll_Ad - their Ad per carrier-round x our carrier-rounds (a3_decomp), as launchers (/45):
the most launchers that mining Mn instead of the extra Ad could have bought by r100 (upper bound: it ignores that the
Ad paid for carriers). 'closable' = the launcher gap r100 is <= that bound.
Usage: python3 -I a3_flip.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3_common import *
import a3_arrive

R = 100


def cr(tl):
    s = 0; prev = 0
    for r in range(10, R + 1, 10):
        a = int(tl[r]['alive_C']) if r in tl else 0
        s += (prev + a) / 2 * 10; prev = a
    return s


def built(tl, k):
    return int(tl[R][k])          # timeline built_* is cumulative


def main():
    print('| match g | map | reason | rounds | Mn gap r100 | L built r100 us/them | L alive r100 us/them | C lost r100 us/them | '
          'enemy arrival on our main Mn well | our Ad excess r100 (kg) | as launchers | launcher gap closable |')
    print('|' + '---|' * 12)
    n = closable = 0
    rows = []
    for G in games():
        if G['dup'] or G['won']: continue
        tu = timeline(G, G['us']); tt = timeline(G, G['them'])
        if R not in tu or R not in tt: continue
        lu, lt = built(tu, 'built_L'), built(tt, 'built_L')
        cu, ct = cr(tu), cr(tt)
        at = int(tt[R]['coll_Ad']); au = int(tu[R]['coll_Ad'])
        ex = au - cu * at / ct if ct else 0
        cl_u = sum(1 for d in deaths(G, G['us']) if d['type'] == 'C' and int(d['round']) <= R)
        cl_t = sum(1 for d in deaths(G, G['them']) if d['type'] == 'C' and int(d['round']) <= R)
        arr = a3_arrive.arrival(G, G['us'])[1]
        ok = lt - lu <= max(0, ex) / 45
        n += 1; closable += ok
        rows.append((G, lt - lu, ex, int(tu[R]['alive_L']), int(tt[R]['alive_L']), lu, lt))
        print(f"| {G['m']} g{G['g']} | {G['map']} | {G['reason']} | {G['rounds']} | {int(tu[R]['coll_Mn']) - int(tt[R]['coll_Mn'])} | "
              f"{lu}/{lt} | {tu[R]['alive_L']}/{tt[R]['alive_L']} | {cl_u}/{cl_t} | {arr} | {ex:.0f} | {max(0, ex) / 45:.1f} | {'yes' if ok else 'no'} |")
    gaps = [r[1] for r in rows]
    print(f"\nlosses n={n}: launcher gap r100 (them - us) median {med(gaps)}, sum {sum(gaps)}; our Ad excess r100 sum "
          f"{sum(r[2] for r in rows):.0f} kg = {sum(max(0, r[2]) for r in rows) / 45:.1f} launchers (positive parts); "
          f"launcher gap closable by the Ad excess in {closable}/{n} (of which gap <= 0 already: {sum(1 for g in gaps if g <= 0)})")
    print(f"  launchers built r100 us/them {sum(r[5] for r in rows)}/{sum(r[6] for r in rows)}; alive r100 us/them "
          f"{sum(r[3] for r in rows)}/{sum(r[4] for r in rows)}; launchers lost by r100 us/them {sum(r[5]-r[3] for r in rows)}/"
          f"{sum(r[6]-r[4] for r in rows)}; games with fewer alive at r100 {sum(1 for r in rows if r[3] < r[4])}/{n}, "
          f"with fewer built {sum(1 for r in rows if r[5] < r[6])}/{n}")


if __name__ == '__main__':
    main()
