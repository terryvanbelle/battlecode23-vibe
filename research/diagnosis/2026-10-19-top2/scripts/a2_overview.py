"""a2_overview: per game, army and economy every 100 rounds (timeline.csv) and the split round: the first 10-round
sample from which the opponent's live launchers stay >= ours + 5 to the end (losses) / ours >= theirs + 5 (wins).
Usage: python3 -I a2_overview.py [--csv OUT]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A


def split_round(tl_us, tl_them, won, margin=5):
    rs = sorted(set(tl_us) & set(tl_them))
    last_bad = None
    for r in rs:
        a, b = tl_us[r]['alive_L'], tl_them[r]['alive_L']
        lead = (b - a) if not won else (a - b)
        if lead < margin:
            last_bad = r
    nxt = [r for r in rs if last_bad is None or r > last_bad]
    return nxt[0] if nxt else None


def main():
    out = []
    print('game | res | rounds | split(L+5) | L us/them r100 r200 r300 r400 r500 r750 r1000 | C us/them r300 r500 | '
          'Mn coll/100r us/them around split (-100..0, 0..+100) | built_L/100r around split')
    for m, g, k in A.ALL:
        d = A.G(m, g)
        t = A.timeline(m, g)
        u, th = t['us'], t['them']
        sr = split_round(u, th, d['won'])
        def L(r):
            a, b = A.at(u, r), A.at(th, r)
            return f"{a['alive_L']}/{b['alive_L']}" if a and r <= d['rounds'] else '-'
        def C(r):
            a, b = A.at(u, r), A.at(th, r)
            return f"{a['alive_C']}/{b['alive_C']}" if a and r <= d['rounds'] else '-'
        def rate(tl, f, r0, r1):
            a, b = A.at(tl, r0), A.at(tl, r1)
            if a is None or b is None: return None
            return b[f] - a[f]
        if sr:
            mb = (rate(u, 'coll_Mn', sr - 100, sr), rate(th, 'coll_Mn', sr - 100, sr), rate(u, 'coll_Mn', sr, sr + 100), rate(th, 'coll_Mn', sr, sr + 100))
            lb = (rate(u, 'built_L', sr - 100, sr), rate(th, 'built_L', sr - 100, sr), rate(u, 'built_L', sr, sr + 100), rate(th, 'built_L', sr, sr + 100))
        else:
            mb = lb = (None,) * 4
        print(f"{A.label(m, g)} | {k} {d['reason']} | {d['rounds']} | {sr} | " + ' '.join(L(r) for r in (100, 200, 300, 400, 500, 750, 1000))
              + f" | {C(300)} {C(500)} | {mb[0]}/{mb[1]} {mb[2]}/{mb[3]} | {lb[0]}/{lb[1]} {lb[2]}/{lb[3]}")
        out.append((m, g, k, sr))
    return out


if __name__ == '__main__':
    main()
