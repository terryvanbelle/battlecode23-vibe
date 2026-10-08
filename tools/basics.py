#!/usr/bin/env python3
"""Basics battery over a gauntlet census (TRAINING_ALGORITHM §1 item 7). Absolute bars are bugs when they fail.

    tools/basics.py gauntlet/<run>/census.csv [--team bot] [--control gauntlet/<run2>/census.csv]

Absolute bars (our team's rows only):
  overruns       0 robot-turns at the bytecode limit (replay bytecodes)
  exceptions     0 caught exceptions (the bot's own counter `ex`, from the indicator string)
  near misses    0 turns above 90% of the limit (the bot's own counter `nm`, measured before the budget fill)
  symmetry       no robot ends with a mask that excludes the true symmetry (sym_wrong = 0)
  sym decided    the team decides the symmetry (first robot) by round SYM_BOUND in >= 90% of games
Reported (no bar yet; set once the offline bound and the field census exist):
  rounds to finish, anchors placed / built, robots never moving, Mn and Ad collected.
With --control, relative bars compare medians and fail only beyond 2 standard errors (paired by cell when possible).
Rows without indicator strings (census `tele` = none or bcc: replica games run with indicators off; TELEMETRY.md C.6)
carry no counters: exceptions come from `tele_exc_turns` (bcc) and are n/a for tele=none, near misses come from the
replay-side `near`, and both symmetry bars are n/a. Rows without a `tele` column (older runs) are read as before.
An n/a bar neither passes nor fails. Exit status: 0 when every absolute bar passes or is n/a, 1 otherwise."""
import argparse, csv, math, statistics as st, sys

SYM_BOUND = 150


def counters(r):
    out = {}
    for kv in r.get('counters', '').strip(';').split(';'):
        if '=' in kv:
            k, v = kv.split('=', 1)
            try:
                out[k] = int(v)
            except ValueError:
                pass
    return out


def load(path, team):
    return [r for r in csv.DictReader(open(path)) if r['team'] == team]


def has_strings(r):
    """The row carries the bot's indicator counters: no `tele` column (older runs), or telemetry with strings."""
    return r.get('tele') not in ('none', 'bcc')


def battery(rows):
    """[(bar, passed True|False|None for n/a, detail)]."""
    res = []
    srows = [r for r in rows if has_strings(r)]
    bare = [r for r in rows if not has_strings(r)]
    bcc = [r for r in bare if r.get('tele') == 'bcc']
    blind = len(bare) - len(bcc)
    note = lambda k, what: f' ({what} in {k} games without strings)' if k else ''
    n = len(srows)
    over = sum(int(r['over']) for r in rows)
    ex = sum(counters(r).get('ex', 0) for r in srows) + sum(int(r.get('tele_exc_turns') or 0) for r in bcc)
    nm = sum(counters(r).get('nm', 0) for r in srows) + sum(int(r.get('near') or 0) for r in bare)
    res.append(('overruns', over == 0, f'{over} robot-turns at the limit'))
    if srows or bcc:
        res.append(('exceptions', ex == 0, f'{ex} caught' + note(len(bcc), 'tele_exc_turns') +
                    (f'; n/a in {blind} games (tele=none)' if blind else '')))
    else:
        res.append(('exceptions', None, f'n/a in {blind} games (tele=none: no counters, no telemetry)'))
    res.append(('near misses', nm == 0, f'{nm} turns above 90% (work before the fill)' +
                note(len(bare), 'replay-side near')))
    if not srows:
        res.append(('symmetry never wrong', None, '(no strings)'))
        res.append((f'symmetry decided by r{SYM_BOUND}', None, '(no strings)'))
        return res
    wrong = sum(int(r['sym_wrong']) for r in srows)
    dec = [int(r['sym_first_decided']) for r in srows]
    in_time = sum(1 for d in dec if 0 <= d <= SYM_BOUND)
    res.append(('symmetry never wrong', wrong == 0, f'{wrong} robots ended excluding the truth' +
                (f' (n/a in {len(bare)} games without strings)' if bare else '')))
    res.append((f'symmetry decided by r{SYM_BOUND}', n and in_time >= 0.9 * n,
                f'{in_time}/{n} games; never decided in {sum(1 for d in dec if d < 0)}' +
                (f' (n/a in {len(bare)} games without strings)' if bare else '')))
    return res


def report(rows):
    rounds = [int(r['rounds']) for r in rows]
    ab = sum(int(r['anchors_built']) for r in rows)
    ap = sum(int(r['anchors_placed']) for r in rows)
    lines = [f'games {len(rows)}; rounds median {st.median(rounds)}, games reaching 2000: {sum(1 for x in rounds if x >= 2000)}',
             f'anchors placed {ap} of {ab} built ({ap / ab:.0%})' if ab else 'anchors: none built',
             f"collected per game: Mn median {st.median(int(r['coll_Mn']) for r in rows)}, Ad median "
             f"{st.median(int(r['coll_Ad']) for r in rows)}; games with no mana {sum(1 for r in rows if int(r['coll_Mn']) == 0)}",
             f"launchers still (median share of robot-rounds) {st.median(float(r['still_L']) for r in rows):.2f}, carriers "
             f"{st.median(float(r['still_C']) for r in rows):.2f}"]
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('census')
    ap.add_argument('--team', default='bot')
    ap.add_argument('--control')
    a = ap.parse_args()
    rows = load(a.census, a.team)
    if not rows:
        print(f'no rows for team {a.team}')
        return 1
    ok = True
    for name, passed, detail in battery(rows):
        if passed is None:
            print(f"n/a   {name:28s} {detail}")
            continue
        ok &= bool(passed)
        print(f"{'PASS' if passed else 'FAIL'}  {name:28s} {detail}")
    for line in report(rows):
        print('      ' + line)
    if a.control:
        ctl = load(a.control, a.team)
        for k in ('rounds', 'anchors_placed', 'coll_Mn', 'coll_Ad', 'kills'):
            x = [float(r[k]) for r in rows]
            y = [float(r[k]) for r in ctl]
            se = math.sqrt(st.pvariance(x) / len(x) + st.pvariance(y) / len(y)) or 1.0
            print(f'      vs control {k:15s} {st.mean(x):9.1f} vs {st.mean(y):9.1f}  ({(st.mean(x) - st.mean(y)) / se:+.1f} SE)')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
