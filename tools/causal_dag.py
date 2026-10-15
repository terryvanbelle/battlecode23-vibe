#!/usr/bin/env python3
"""Cause/effect graph of our panel losses (owner, PROMPTS 101-102).

Every panel plays the same 100 cells (opponent, map, side, seed), and a cell is deterministic for a given build, so
the outcome varies within a cell only because the build changed. Nodes are "we trail by at least T in variable X at
round R" (from matches/<id>/extract/timeline.csv and hq.csv); the loss node is the game's result. Every association
is measured WITHIN cells (Mantel-Haenszel risk difference over cells where both sides of the split occur), so the
opponent's strength cannot confound it.

  tools/causal_dag.py [--panels GLOB] [--out FILE]

Output (markdown): node lift on loss, the edges A@r1 -> B@r2 (onset of B after r1, stratified), and for every loss
the backward walk from "loss" to its root (the earliest active node with no active parent), clustered.
"""
import argparse, csv, glob, os, sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUNDS = (50, 100, 150, 200, 300, 400, 600)
# variable: (timeline expression on one side, "behind" threshold); diffs are us - them
VARS = {
    'Ad': (lambda r: r['coll_Ad'], 25), 'Mn': (lambda r: r['coll_Mn'], 60),
    'Cbuilt': (lambda r: r['built_C'], 3), 'Calive': (lambda r: r['alive_C'], 3),
    'Lbuilt': (lambda r: r['built_L'], 3), 'Lalive': (lambda r: r['alive_L'], 3),
    'Army': (lambda r: r['army_value'], 200), 'Isl': (lambda r: r['islands'], 1),
    'Kills': (lambda r: r['kills'], 3),
}
PRESS_T = 30            # HQ besieged: enemy launcher-rounds within r2 9 of our HQs, cumulative, at least this and more
                        # than we inflict on theirs
NUM = ('alive_C', 'alive_L', 'built_C', 'built_L', 'coll_Ad', 'coll_Mn', 'army_value', 'islands', 'kills')
MIN_N, MIN_RD = 30, 0.15


def load_game_states(match, games, side_of):
    """{game: {(var, round): True/False}} for one match's extract."""
    ex = os.path.join(REPO, 'matches', str(match), 'extract')
    tl = defaultdict(dict)                       # game -> round -> side -> row
    with open(os.path.join(ex, 'timeline.csv')) as f:
        for r in csv.DictReader(f):
            g = int(r['game'])
            if g in games: tl[g].setdefault(int(r['round']), {})[r['side']] = {k: float(r[k] or 0) for k in NUM}
    press = defaultdict(lambda: defaultdict(float))   # game -> (round bucket end, side) -> cumulative pressure9 on side
    hqp = os.path.join(ex, 'hq.csv')
    if os.path.exists(hqp):
        with open(hqp) as f:
            for r in csv.DictReader(f):
                g = int(r['game'])
                if g in games: press[g][(int(r['round']), r['side'])] += float(r['pressure9'] or 0)
    out = {}
    for g in games:
        us = side_of[g]; them = 'B' if us == 'A' else 'A'
        rows = tl.get(g, {})
        if not rows: continue
        rs = sorted(rows)
        st = {}
        for R in ROUNDS:
            past = [x for x in rs if x <= R]
            if not past: continue
            row = rows[past[-1]]                  # carry the final state forward once the game is over
            if us not in row or them not in row: continue
            for v, (fn, t) in VARS.items():
                st[(v, R)] = fn(row[us]) - fn(row[them]) <= -t
            pu = sum(p for (rr, s), p in press[g].items() if rr <= R and s == us)
            pt = sum(p for (rr, s), p in press[g].items() if rr <= R and s == them)
            st[('Besieged', R)] = pu >= PRESS_T and pu > pt
        out[g] = st
    return out


def load(panels):
    games = []                                    # dicts: cell, build, win, states
    for p in panels:
        build = os.path.basename(p).split('-panel-')[-1]
        by_match = defaultdict(dict)
        with open(os.path.join(p, 'results.csv')) as f:
            for r in csv.DictReader(f):
                if r['bot_result'] not in ('win', 'loss'): continue
                by_match[int(r['match'])][int(r['game'])] = r
        for m, gs in by_match.items():
            try:
                states = load_game_states(m, set(gs), {g: r['bot_side'] for g, r in gs.items()})
            except FileNotFoundError:
                continue
            for g, r in gs.items():
                if g in states:
                    games.append({'cell': (r['opponent'], r['map'], r['bot_side'], r['seed']), 'build': build,
                                  'win': r['bot_result'] == 'win', 'st': states[g], 'rounds': int(r['rounds'] or 0)})
    return games


def mh_rd(games, expo, outcome, keep=lambda g: True):
    """Mantel-Haenszel risk difference of outcome(g) for expo(g) True vs False, stratified by cell.
    Returns (rd, n_exposed, n_unexposed, n_cells) over cells where both arms occur."""
    cells = defaultdict(lambda: [0, 0, 0, 0])    # a=exp&out, n1=exp, c=unexp&out, n0=unexp
    for g in games:
        if not keep(g): continue
        e = expo(g)
        if e is None: continue
        o = outcome(g)
        if o is None: continue
        c = cells[g['cell']]
        if e: c[0] += o; c[1] += 1
        else: c[2] += o; c[3] += 1
    num = den = 0.0; n1 = n0 = k = 0
    for a, m1, cc, m0 in cells.values():
        if m1 == 0 or m0 == 0: continue
        w = m1 * m0 / (m1 + m0)
        num += w * (a / m1 - cc / m0); den += w; n1 += m1; n0 += m0; k += 1
    return (num / den if den else 0.0), n1, n0, k


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--panels', default='gauntlet/*-panel-*')
    ap.add_argument('--out', default=os.path.join(REPO, 'research', 'diagnosis', 'causal-dag.md'))
    a = ap.parse_args()
    panels = sorted(p for p in glob.glob(os.path.join(REPO, a.panels)) if os.path.exists(os.path.join(p, 'results.csv')))
    games = load(panels)
    losses = [g for g in games if not g['win']]
    nodes = sorted({k for g in games for k in g['st']}, key=lambda k: (k[1], k[0]))
    lines = [f'# Causal graph of panel losses (tools/causal_dag.py)', '',
             f'{len(games)} games ({len(losses)} losses) from {len(panels)} panels on the same cells; '
             f'{len({g["cell"] for g in games})} cells. Risk differences are Mantel-Haenszel within cells.', '']
    # 1. node -> loss
    lift = {}
    lines += ['## Nodes: loss risk when the node is on vs off (same cell)', '',
              '| node | on in losses | on in wins | RD(loss) | games on/off | cells |', '|---|---|---|---|---|---|']
    for nd in nodes:
        rd, n1, n0, k = mh_rd(games, lambda g: g['st'].get(nd), lambda g: not g['win'])
        lift[nd] = rd
        onl = sum(1 for g in losses if g['st'].get(nd)) / max(1, len(losses))
        onw = sum(1 for g in games if g['win'] and g['st'].get(nd)) / max(1, len(games) - len(losses))
        lines.append(f'| {nd[0]}@{nd[1]} | {onl:.2f} | {onw:.2f} | {rd:+.2f} | {n1}/{n0} | {k} |')
    # 2. edges A@r1 -> B@r2 (r2 > r1): onset of B among games where B was off at r1's round (or r1 is B's first round)
    edges = defaultdict(list)                     # child -> [(parent, rd)]
    for b in nodes:
        for p in nodes:
            if p[1] >= b[1] or p[0] == b[0]: continue
            prior = (b[0], p[1])
            rd, n1, n0, k = mh_rd(games, lambda g: g['st'].get(p), lambda g: g['st'].get(b),
                                  keep=lambda g: not g['st'].get(prior, False))
            if n1 >= MIN_N and n0 >= MIN_N and rd >= MIN_RD:
                edges[b].append((p, rd))
    lines += ['', f'## Edges (parent on raises the child\'s onset by at least {MIN_RD:.2f}, same cell, '
              f'at least {MIN_N} games each arm)', '']
    for b in nodes:
        if edges[b]:
            best = sorted(edges[b], key=lambda e: -e[1])[:4]
            lines.append(f'- {b[0]}@{b[1]} <- ' + ', '.join(f'{p[0]}@{p[1]} ({rd:+.2f})' for p, rd in best))
    # 3. backward walk per loss: from loss take the active node with the highest loss lift at the latest round, then
    #    repeatedly its active parent with the strongest edge, until no active parent: that node is the root
    loss_parents = [nd for nd in nodes if lift[nd] >= MIN_RD]
    roots = defaultdict(int); chains = defaultdict(int); unexplained = 0
    for g in losses:
        act = [nd for nd in loss_parents if g['st'].get(nd)]
        if not act:
            unexplained += 1; continue
        cur = max(act, key=lambda nd: (nd[1], lift[nd]))
        chain = [cur]
        while True:
            ps = [(p, rd) for p, rd in edges[cur] if g['st'].get(p) and p not in chain]
            if not ps: break
            cur = max(ps, key=lambda e: e[1])[0]; chain.append(cur)
        roots[cur] += 1
        chains[' -> '.join(f'{n[0]}@{n[1]}' for n in reversed(chain)) + ' -> loss'] += 1
    lines += ['', f'## Roots of the {len(losses)} losses (backward walk)', '',
              f'No active loss-linked node: {unexplained}.', '']
    for r, n in sorted(roots.items(), key=lambda x: -x[1]):
        lines.append(f'- {r[0]}@{r[1]}: {n}')
    lines += ['', '## Most common chains', '']
    for c, n in sorted(chains.items(), key=lambda x: -x[1])[:15]:
        lines.append(f'- {n}: {c}')
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'{len(games)} games, {len(losses)} losses; wrote {os.path.relpath(a.out, REPO)}')


if __name__ == '__main__':
    sys.exit(main())
