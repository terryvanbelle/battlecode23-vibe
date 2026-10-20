#!/usr/bin/env python3
"""Paired comparison of two gauntlet runs that played the same cells (opponent, map, side, seed).

    tools/paired.py <candidate run dir> <control run dir> [--margin island_rounds]

Each cell is a pair: the candidate's game and the control's game on identical inputs. Only discordant pairs (one won,
the other lost) inform the win comparison; a coin-flip game (the engine's unseeded final tiebreak) is excluded.
Reports: cells matched, identical results, gained (candidate won, control lost), lost, net with its SE = sqrt(g+l),
an exact two-sided sign-test p, and, when both runs have a census, the paired mean difference of a per-cell margin
(default: our island-rounds minus theirs) with its t statistic.
An identity control (two byte-identical builds) must read 0 discordant pairs; anything else is a harness defect.
Exit 2 (panel review 2026-10-20) when the two runs' provenance names different panel cells files, when fewer than 90%
of the smaller run's cells match, or when a run is marked incomplete; --force reports anyway. D = gained + lost (the
discordant cells) is printed with the net, since a +3 at D 24 is not a +3 at D 6."""
import argparse, csv, math, os, sys


def load(run):
    res = {}
    for r in csv.DictReader(open(os.path.join(run, 'results.csv'))):
        if r['bot_result'] not in ('win', 'loss'):
            continue
        coin = 'coin flip' in r['reason']
        res[(r['opponent'], r['map'], r['bot_side'], r['seed'])] = (r['bot_result'] == 'win', coin, r)
    cen = {}
    p = os.path.join(run, 'census.csv')
    if os.path.exists(p):
        rows = list(csv.DictReader(open(p)))
        by = {}
        for r in rows:
            by.setdefault((r['cell_opponent'], r['cell_map'], r['cell_side'], r['cell_seed']), []).append(r)
        for k, rs in by.items():
            ours = [r for r in rs if r['side'] == k[2]]
            theirs = [r for r in rs if r['side'] != k[2]]
            if ours and theirs:
                cen[k] = (ours[0], theirs[0])
    return res, cen


def sign_p(g, l):
    n = g + l
    if n == 0:
        return 1.0
    k = min(g, l)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def prov(run):
    """key=value pairs of a run's provenance.txt (the last value wins; a resumed run appends), {} when absent."""
    out = {}
    try:
        for w in open(os.path.join(run, 'provenance.txt')).read().split():
            if '=' in w:
                k, v = w.split('=', 1)
                out[k] = v
    except OSError:
        pass
    return out


def margin(ours, theirs, key):
    try:
        return float(ours[key]) - float(theirs[key])
    except (KeyError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('candidate')
    ap.add_argument('control')
    ap.add_argument('--margin', default='island_rounds')
    ap.add_argument('--force', action='store_true', help='report even when the runs do not match')
    a = ap.parse_args()
    c_res, c_cen = load(a.candidate)
    k_res, k_cen = load(a.control)
    for name, run in (('candidate', a.candidate), ('control', a.control)):
        pv = os.path.join(run, 'provenance.txt')
        print(f'{name}: ' + (open(pv).read().replace(chr(10), ' ').strip() if os.path.exists(pv) else 'no provenance.txt (run predates code hashes)'))
    keys = sorted(set(c_res) & set(k_res))
    bad = []
    pc, pk = prov(a.candidate), prov(a.control)
    if pc.get('cells') and pk.get('cells') and os.path.normpath(pc['cells']) != os.path.normpath(pk['cells']):
        bad.append(f'different panels: candidate {pc["cells"]}, control {pk["cells"]}')
    if len(keys) < 0.9 * min(len(c_res), len(k_res)):
        bad.append(f'only {len(keys)} cells match ({len(c_res)} and {len(k_res)})')
    for name, pv in (('candidate', pc), ('control', pk)):
        if pv.get('incomplete', '0') != '0':
            bad.append(f'the {name} run is incomplete ({pv["incomplete"]} requests unresolved)')
    if bad:
        print('NOT COMPARABLE: ' + '; '.join(bad), file=sys.stderr)
        if not a.force:
            return 2
    same = gained = lost = coin = 0
    by_opp = {}
    for k in keys:
        cw, cc, _ = c_res[k]
        kw, kc, _ = k_res[k]
        if cc or kc:
            coin += 1
            continue
        if cw == kw:
            same += 1
        elif cw:
            gained += 1
            by_opp.setdefault(k[0], [0, 0])[0] += 1
        else:
            lost += 1
            by_opp.setdefault(k[0], [0, 0])[1] += 1
    net = gained - lost
    se = math.sqrt(gained + lost) if gained + lost else 0
    print(f'cells matched {len(keys)} (candidate {len(c_res)}, control {len(k_res)}); coin-flip excluded {coin}')
    print(f'identical {same}, gained {gained}, lost {lost} (D {gained + lost}): net {net:+d} '
          f'(t {net / se:+.2f})' if se else f'identical {same}, gained 0, lost 0 (D 0): net 0', end='')
    print(f'; sign test p = {sign_p(gained, lost):.3g}')
    diffs = []
    for k in keys:
        if k in c_cen and k in k_cen:
            m1 = margin(*c_cen[k], a.margin)
            m0 = margin(*k_cen[k], a.margin)
            if m1 is not None and m0 is not None:
                diffs.append(m1 - m0)
    if len(diffs) >= 2:
        mean = sum(diffs) / len(diffs)
        sd = math.sqrt(sum((d - mean) ** 2 for d in diffs) / (len(diffs) - 1))
        t = mean / (sd / math.sqrt(len(diffs))) if sd > 0 else 0.0
        print(f'margin {a.margin}: paired mean difference {mean:+.2f} over {len(diffs)} cells (t {t:+.2f}); '
              f'identical margins {sum(1 for d in diffs if d == 0)}')
    if by_opp:
        worst = sorted(by_opp.items(), key=lambda kv: kv[1][0] - kv[1][1])
        print('by opponent (gained-lost): ' + ', '.join(f'{o} {g}-{l}' for o, (g, l) in worst))
    return 0


if __name__ == '__main__':
    sys.exit(main())
