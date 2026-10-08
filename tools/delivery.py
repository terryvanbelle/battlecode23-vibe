#!/usr/bin/env python3
"""Delivery check (TRAINING_ALGORITHM §2 step 5): does the candidate's mechanism fire, and does its signature move,
compared with the control on the SAME cells (opponent, map, side, seed)? Wins are not the question here.

    tools/delivery.py <candidate run> <control run> [--metrics exposed,dmg/contact,kills,died_L] [--fire pn,ua]

Metrics are census columns (our team's row) or fields of the launcher micro string (micro_L: contact, hit|contact,
hit|fighter, move|contact, exposed, dmg/contact, hit). For each metric: paired mean difference (candidate - control)
over cells where both values exist, its SE and t. --fire names counters from the bot's indicator (census `counters`):
reported as the share of candidate games where the counter is > 0 and its mean, or n/a when no candidate row carries
the counter at all (replica games: no indicator strings).
Three-way reading, as pre-registered by the caller: PASS when the move is >= 1 SE beyond the bar in the intended
direction, FAIL when >= 2 SE short, otherwise INCONCLUSIVE (extend the block)."""
import argparse, csv, math, os, sys


def ours(run):
    out = {}
    for r in csv.DictReader(open(os.path.join(run, 'census.csv'))):
        k = (r['cell_opponent'], r['cell_map'], r['cell_side'], r['cell_seed'])
        if r['side'] == k[2]:
            out[k] = r
    return out


def value(row, metric):
    if metric in row and row[metric] not in ('', None):
        try:
            return float(row[metric])
        except ValueError:
            return None
    micro = row.get('micro_L', '')
    for tok in micro.split():
        if '=' in tok:
            k, v = tok.split('=', 1)
            if k == metric:
                return float(v)
    for kv in row.get('counters', '').strip(';').split(';'):
        if '=' in kv:
            k, v = kv.split('=', 1)
            if k == metric:
                return float(v)
    return None


def paired(c, k, metric):
    d = []
    for key in c:
        if key in k:
            a, b = value(c[key], metric), value(k[key], metric)
            if a is not None and b is not None:
                d.append(a - b)
    if len(d) < 2:
        return len(d), 0.0, float('nan'), float('nan')
    mean = sum(d) / len(d)
    sd = math.sqrt(sum((x - mean) ** 2 for x in d) / (len(d) - 1))
    se = sd / math.sqrt(len(d))
    return len(d), mean, se, (mean / se if se > 0 else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('candidate')
    ap.add_argument('control')
    ap.add_argument('--metrics', default='exposed,dmg/contact,hit|contact,kills,died_L,won,island_rounds')
    ap.add_argument('--fire', default='')
    a = ap.parse_args()
    c, k = ours(a.candidate), ours(a.control)
    print(f'cells: candidate {len(c)}, control {len(k)}, shared {len(set(c) & set(k))}')
    for m in a.metrics.split(','):
        n, mean, se, t = paired(c, k, m)
        cm = [value(c[x], m) for x in c if x in k and value(c[x], m) is not None]
        km = [value(k[x], m) for x in k if x in c and value(k[x], m) is not None]
        avg = lambda v: sum(v) / len(v) if v else float('nan')
        print(f'{m:14s} candidate {avg(cm):9.3f}  control {avg(km):9.3f}  paired diff {mean:+9.3f} +- {se:.3f} (t {t:+.2f}, n {n})')
    for f in [x for x in a.fire.split(',') if x]:
        raw = [value(r, f) for r in c.values()]
        if raw and all(v is None for v in raw):     # replica rows carry no counters (TELEMETRY.md C.6): not a zero
            print(f'fires {f:8s} n/a (no counters in {len(raw)} games)')
            continue
        vals = [v or 0 for v in raw]
        if vals:
            print(f'fires {f:8s} in {sum(1 for v in vals if v > 0)}/{len(vals)} candidate games, mean {sum(vals) / len(vals):.1f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
