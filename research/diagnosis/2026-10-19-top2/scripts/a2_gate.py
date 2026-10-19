"""a2_gate: reconstruct our HQ anchor gate (HQ.java:68-76) per 25-round bucket from the extracts.
gate = round >= ANCHOR_GATE_UNTIL(1500) || (!anyPressed && islThem <= islUs). pressed(HQ) = pressure34 of the current or
previous 25-round bucket >= PRESS_SUM 100 (HQ.swarmEconomy; hq.csv pressure34 is the same sum of enemy fighters in HQ
vision). Island counts are the TRUE counts (timeline.csv), not the shared-array belief Comms.islThem/islUs uses, so the
deficit test is an approximation. Also: buckets with an HQ that has built >= ANCHOR_MIN_LAUNCHERS (20) launchers, and
the HQ telemetry share of HQ-turns with wantAnchor set (tele_states.csv detail anchor=1), phase mid (r151-600) and late.
Usage: python3 -I a2_gate.py"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A


def gate_rows(m, g):
    d = A.G(m, g)
    us = d['us']
    pr = collections.defaultdict(dict)      # hq_id -> {round: pressure34}
    bl = collections.defaultdict(dict)
    for r in A.rows(m, 'hq'):
        if int(r['game']) != g or r['side'] != us:
            continue
        pr[r['hq_id']][int(r['round'])] = int(r['pressure34'])
        bl[r['hq_id']][int(r['round'])] = int(r['built_L'])
    t = A.timeline(m, g)
    out = []
    cum = collections.Counter()
    end = d['rounds']
    for R in range(25, end + 1, 25):
        pressed = False
        for h in pr:
            cum[h] += bl[h].get(R, 0)
            if pr[h].get(R, 0) >= 100 or pr[h].get(R - 25, 0) >= 100:
                pressed = True
        a, b = A.at(t['us'], R), A.at(t['them'], R)
        deficit = b['islands'] > a['islands']
        l20 = sum(1 for h in cum if cum[h] >= 20)
        out.append((R, pressed, deficit, l20, a['islands'], b['islands']))
    return out


def tele_want(m, g):
    d = A.G(m, g)
    res = {}
    tot = collections.Counter(); want = collections.Counter()
    for r in A.rows(m, 'tele_states'):
        if int(r['game']) != g or r['side'] != d['us'] or r['type'] != 'H':
            continue
        n = int(r['turns'])
        tot[r['phase']] += n
        if 'anchor=1' in r['detail']:
            want[r['phase']] += n
    for ph in ('mid', 'late'):
        res[ph] = (want[ph], tot[ph])
    return res


def main():
    print('game | k | rounds | buckets r400-min(end,1500) | closed: pressed only / deficit only / both / open | '
          'open & an HQ with 20 L | first open bucket | want-anchor HQ-turns mid / late')
    agg = collections.Counter()
    for m, g, k in A.ALL:
        rows = [x for x in gate_rows(m, g) if 400 <= x[0] < 1500]
        n = len(rows)
        po = sum(1 for x in rows if x[1] and not x[2]); do = sum(1 for x in rows if x[2] and not x[1])
        bo = sum(1 for x in rows if x[1] and x[2]); op = sum(1 for x in rows if not x[1] and not x[2])
        opl = sum(1 for x in rows if not x[1] and not x[2] and x[3] > 0)
        fo = next((x[0] for x in rows if not x[1] and not x[2] and x[3] > 0), None)
        tw = tele_want(m, g)
        print(f"{A.label(m, g)} | {k} | {A.G(m, g)['rounds']} | {n} | {po}/{do}/{bo}/{op} | {opl} | {fo} | "
              f"{tw['mid'][0]}/{tw['mid'][1]} {tw['late'][0]}/{tw['late'][1]}")
        kk = 'L' if k != 'W' else 'W'
        agg[kk, 'n'] += n; agg[kk, 'po'] += po; agg[kk, 'do'] += do; agg[kk, 'bo'] += bo; agg[kk, 'op'] += op; agg[kk, 'opl'] += opl
    for kk in ('L', 'W'):
        n = agg[kk, 'n']
        print(f"pooled {kk}: buckets {n}: pressed only {agg[kk, 'po'] / n:.2f}, deficit only {agg[kk, 'do'] / n:.2f}, "
              f"both {agg[kk, 'bo'] / n:.2f}, open {agg[kk, 'op'] / n:.2f}, open with a 20-L HQ {agg[kk, 'opl'] / n:.2f}")


if __name__ == '__main__':
    main()
