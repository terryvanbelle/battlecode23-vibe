#!/usr/bin/env python3
"""Successive-halving race of C.java settings against an opponent pool (the follow-up to the Swiss of PROMPTS 114).

  tools/race.py init --base c_knob1 --seed 7 [--grid NAME=v1,v2,... ...] [--sample N [--k K --pool A,B --always C]]
        [--opps c_well9,arch_jm,...] [--maps M1,M2,...] [--rungs 8,16,32] [--keep 0.5] [--tag t] [--prefix c_rc]
        prints the new run dir gauntlet/<stamp>-race[-t]/: config.json, bots.tsv (the base, then the candidates: the
        grid's points other than the base's own, then the random draws of tools/param.py) and units.csv
  tools/race.py run DIR [--jobs 5]       build every bot and opponent into DIR/classes, then play the rungs (resumable)
  tools/race.py standings DIR            the table after the games so far
  tools/race.py analyse DIR              win share by level of each varied constant, on rung 1 (every bot, same cells)
  tools/race.py export DIR BOT NEWPKG    src/NEWPKG = the base with BOT's constants (tools/param.py make)

A unit is (opponent, map, seed), played from both sides: 2 games. Rung k plays units [rungs[k-1], rungs[k]) for the
base and every live candidate; then the candidates are ranked by games won over every unit so far (a game without a
result counts half; ties: the rung's own games, then a seeded draw) and the best ceil(keep x n) go on. The base is the
control: it plays every unit and is never cut, so each row's net against it is paired (same opponent, map, seed,
side). The winner is the top row of the last rung's table; it may be the base. Units go round-robin over the
opponents, each opponent's maps in a fresh seeded order per cycle, so every prefix is balanced over opponents and
near-balanced over maps. Games share the machine-wide slots of tools/gauntlet.sh with screens (tools/swiss.py play);
replays are reduced to census rows and deleted (--keep-replays keeps them). Runs on the VM (tools/vm-run.sh).
"""
import argparse, concurrent.futures as cf, csv, hashlib, itertools, json, math, random, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import param  # noqa: E402
import swiss  # noqa: E402

PANEL_MAPS = ['DefaultMap', 'Maze', 'Forest', 'ReverseFunnel', 'Cat', 'IslandHopping', 'Hah', 'BatSignal',
              'Cornucopia', 'MassiveL']
OPPS = ['c_well9', 'arch_jm', 'arch_swarm', 'arch_ampmid']
FIELDS = ['rung', 'bot', 'opp', 'map', 'seed', 'side', 'result', 'winner_side', 'rounds', 'reason', 'secs',
          'exc_lines']


def unit_seed(seed, opp, m, cycle):
    return 1 + int(hashlib.sha1(f'race/{seed}/{opp}/{m}/{cycle}'.encode()).hexdigest()[:7], 16)


def units(opps, maps, n, seed):
    """n units (opp, map, seed): opponents round-robin; each opponent's maps reshuffled for every cycle."""
    out, order = [], {}
    for i in range(n):
        o = opps[i % len(opps)]
        j = i // len(opps)
        cycle, pos = divmod(j, len(maps))
        if pos == 0:
            ms = list(maps)
            random.Random(f'race/{seed}/{o}/{cycle}').shuffle(ms)
            order[o] = ms
        m = order[o][pos]
        out.append((o, m, unit_seed(seed, o, m, cycle)))
    return out


def grid_points(grid, b):
    """Every combination of the grid's values as overrides of the base setting `b`, minus the base's own point and any
    point breaking a constraint."""
    names = list(grid)
    out = []
    for vals in itertools.product(*(grid[x] for x in names)):
        s = dict(b)
        s.update(zip(names, vals))
        if s == b or param.violations(s):
            continue
        out.append(s)
    return out


def parse_grid(items, b):
    grid = {}
    for it in items:
        name, _, vals = it.partition('=')
        sp = param.spec(name)
        if name not in b or sp is None:
            sys.exit(f'!! {name} is not in the space of the base')
        try:
            vs = [int(v) for v in vals.split(',') if v != '']
        except ValueError:
            sys.exit(f'!! {it}: values must be integers')
        bad = [v for v in vs if not (sp[1] <= v <= sp[2] or v == param.opts(sp).get('off'))]
        if not vs or bad:
            sys.exit(f'!! {it}: values outside {name} {sp[1]}..{sp[2]}: {bad}')
        grid[name] = vs
    return grid


def init(base, seed, grid=(), sample=0, k=None, always=(), pool=None, opps=OPPS, maps=PANEL_MAPS, rungs=(8, 16, 32),
         keep=0.5, tag='', prefix='c_rc', parent=None):
    text = param.c_java(base).read_text()
    b = param.base_setting(text)
    bad = param.violations(b)
    if bad:
        sys.exit(f'!! {base} breaks: ' + '; '.join(bad))
    rungs = list(rungs)
    if not rungs or any(x >= y for x, y in zip([0] + rungs, rungs)):
        sys.exit(f'!! --rungs must rise strictly from above 0: {rungs}')
    if not 0 < keep < 1:
        sys.exit(f'!! --keep {keep} must lie in (0, 1)')
    missing = [o for o in opps if not (REPO / 'src' / o).is_dir()]
    if missing:
        sys.exit('!! no package src/' + ', src/'.join(missing))
    cands = grid_points(parse_grid(grid, b), b) if grid else []
    if sample:
        unknown = [x for x in tuple(always) + tuple(pool or ()) if x not in b or x not in param.SPACE_NAMES]
        if unknown:
            sys.exit(f'!! not in the space of {base}: ' + ', '.join(unknown))
        cands += param.sample(sample, seed, names=set(b), base=b, k=k, always=always, pool=pool)
    if not cands:
        sys.exit('!! no candidates: give --grid and/or --sample')
    names = [f'{prefix}{i:02d}' for i in range(1, len(cands) + 1)]
    clash = sorted(set(names + [base]) & set(opps))
    if clash:
        sys.exit('!! a bot is also an opponent: ' + ', '.join(clash))
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    d = Path(parent or REPO / 'gauntlet') / (f'{stamp}-race' + (f'-{tag}' if tag else ''))
    d.mkdir(parents=True)
    keys = [s[0] for s in param.SPACE if s[0] in b]
    with open(d / 'bots.tsv', 'w') as fh:
        fh.write('\t'.join(['bot', 'kind'] + keys) + '\n')
        fh.write('\t'.join([base, 'base'] + [str(b[x]) for x in keys]) + '\n')
        for nm, s in zip(names, cands):
            fh.write('\t'.join([nm, 'variant'] + [str(s[x]) for x in keys]) + '\n')
    with open(d / 'units.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['unit', 'opp', 'map', 'seed'])
        for i, u in enumerate(units(list(opps), list(maps), rungs[-1], seed)):
            w.writerow([i, *u])
    cfg = {'base': base, 'base_hash': swiss.bot_hash(base), 'seed': seed, 'created_utc': stamp,
           'opps': {o: swiss.bot_hash(o) for o in opps}, 'maps': list(maps), 'rungs': rungs, 'keep': keep,
           'grid': parse_grid(grid, b) if grid else {},
           'sample': ({'n': sample, 'k': k, 'always': list(always), 'pool': list(pool or [])} if sample else None),
           'space': [list(s[:3]) for s in param.SPACE if s[0] in b], 'constraints': param.CONSTRAINTS}
    (d / 'config.json').write_text(json.dumps(cfg, indent=1) + '\n')
    return d


def read_units(d):
    return [(r['opp'], r['map'], int(r['seed'])) for r in csv.DictReader(open(Path(d) / 'units.csv'))]


def read_games(d):
    f = Path(d) / 'games.csv'
    return list(csv.DictReader(open(f))) if f.exists() else []


def build(d, cfg, bots):
    """DIR/src: the base and every opponent as they are, plus one generated package per candidate; DIR/classes."""
    d = Path(d)
    classes = d / 'classes'
    if (classes / '.built').exists():
        return
    want = dict(cfg['opps'], **{cfg['base']: cfg['base_hash']})
    for p, h in want.items():
        now = swiss.bot_hash(p)
        if now != h:
            sys.exit(f'!! src/{p} is {now}, the race was drawn for {h}')
    src = d / 'src'
    if src.exists():
        shutil.rmtree(src)
    src.mkdir()
    for p in want:
        shutil.copytree(REPO / 'src' / p, src / p)
    for name, kind, s in bots:
        if kind != 'base':
            param.make(cfg['base'], name, s, out=src, note=f'race {d.name}')
    if classes.exists():
        shutil.rmtree(classes)
    subprocess.run(['bash', '-c', f'source "{TOOLS}/lib.sh"; compile_src "$1" "$2"', '_', str(src), str(classes)],
                   check=True)
    (classes / '.built').write_text(' '.join(f'{p}={h}' for p, h in want.items()) + '\n')


def score(games, bot, keys=None):
    """Games won by `bot` (a game without a result counts half), over the units in `keys` when given."""
    s = 0.0
    for g in games:
        if g['bot'] != bot or (keys is not None and (g['opp'], g['map'], g['seed']) not in keys):
            continue
        s += 1.0 if g['result'] == 'win' else 0.5 if g['result'] == 'unknown' else 0.0
    return s


def cut(games, alive, ukeys, rkeys, keep, seed, k):
    """The survivors of rung k: best by score over every unit so far, then the rung's own units, then a seeded draw."""
    rng = random.Random(f'race/{seed}/cut/{k}')
    tie = {b: rng.random() for b in sorted(alive)}
    order = sorted(alive, key=lambda b: (-score(games, b, ukeys), -score(games, b, rkeys), tie[b]))
    return order[:max(1, math.ceil(keep * len(alive)))]


def table(cfg, games, players, ukeys):
    """Rows (bot, games, won, share, net vs the base on the same games, per-opponent won/played) best first."""
    base = cfg['base']
    res = {}
    for g in games:
        if (g['opp'], g['map'], g['seed']) in ukeys:
            res[(g['bot'], g['opp'], g['map'], g['seed'], g['side'])] = g['result']
    rows = []
    for b in players:
        mine = {kk[1:]: v for kk, v in res.items() if kk[0] == b}
        won = sum(1.0 if v == 'win' else 0.5 if v == 'unknown' else 0.0 for v in mine.values())
        net = 0
        for kk, v in mine.items():
            c = res.get((base,) + kk)
            if c is not None and b != base:
                net += (v == 'win') - (c == 'win')
        per = {}
        for kk, v in mine.items():
            w, n = per.get(kk[0], (0.0, 0))
            per[kk[0]] = (w + (1.0 if v == 'win' else 0.5 if v == 'unknown' else 0.0), n + 1)
        rows.append((b, len(mine), won, won / len(mine) if mine else 0.0, net, per))
    rows.sort(key=lambda r: (-r[3], -r[2], r[0] != base, r[0]))
    return rows


def render(cfg, games, players, ukeys, title):
    rows = table(cfg, games, players, ukeys)
    opps = list(cfg['opps'])
    lines = [title, f"{'#':>2} {'bot':10s} {'games':>5s} {'won':>6s} {'share':>6s} {'net':>5s}  " +
             ' '.join(f'{o[:11]:>11s}' for o in opps)]
    for i, (b, n, won, sh, net, per) in enumerate(rows, 1):
        cells = ' '.join(f"{('%g/%d' % per[o]) if o in per else '-':>11s}" for o in opps)
        lines.append(f"{i:2d} {b:10s} {n:5d} {won:6g} {sh:6.3f} {('base' if b == cfg['base'] else '%+d' % net):>5s}  "
                     + cells)
    return '\n'.join(lines) + '\n', rows


def run(d, jobs=5, census=True, keep_replays=False):
    d = Path(d)
    cfg = swiss.read_cfg(d)
    bots = swiss.read_bots(d)
    us = read_units(d)
    build(d, cfg, bots)
    base = cfg['base']
    alive = [b for b, kind, _ in bots if kind != 'base']
    lo = 0
    for k, hi in enumerate(cfg['rungs'], 1):
        f = d / f'rung{k}.json'
        st = json.loads(f.read_text()) if f.exists() else {'alive': alive}
        if 'kept' in st:
            alive, lo = st['kept'], hi
            continue
        f.write_text(json.dumps(st) + '\n')
        players = [base] + st['alive']
        rung_units = us[lo:hi]
        done = {(g['bot'], g['opp'], g['map'], g['seed'], g['side']) for g in read_games(d)}
        todo = [(b, o, m, s, side) for b in players for o, m, s in rung_units for side in 'AB'
                if (b, o, m, str(s), side) not in done]
        todo.sort(key=lambda g: -swiss.LONG.get(g[2], 1))
        total = len(players) * len(rung_units) * 2
        print(f'rung {k}: {len(players)} bots x units {lo}-{hi - 1}, {len(todo)} of {total} games to play', flush=True)
        new = not (d / 'games.csv').exists()
        with open(d / 'games.csv', 'a', newline='') as fh, cf.ThreadPoolExecutor(jobs) as ex:
            w = csv.DictWriter(fh, FIELDS)
            if new:
                w.writeheader()
            futs = {}
            for b, o, m, s, side in todo:
                ta, tb = (b, o) if side == 'A' else (o, b)
                futs[ex.submit(swiss.play, d, k, ta, tb, m, s, census=census, keep=keep_replays)] = (b, o, side)
            n = total - len(todo)
            for fu in cf.as_completed(futs):
                b, o, side = futs[fu]
                g = fu.result()
                res = 'unknown' if g['winner_side'] not in ('A', 'B') else \
                    'win' if g['winner_side'] == side else 'loss'
                w.writerow({'rung': k, 'bot': b, 'opp': o, 'map': g['map'], 'seed': g['seed'], 'side': side,
                            'result': res, 'winner_side': g['winner_side'], 'rounds': g['rounds'],
                            'reason': g['reason'], 'secs': g['secs'], 'exc_lines': g['exc_lines']})
                fh.flush()
                n += 1
                print(f"[k{k} {n:3d}/{total}] {b:>10s} vs {o:<11s} {g['map']:13s} {side} -> {res:7s} r{g['rounds']} "
                      f"{g['secs']}s", flush=True)
        games = read_games(d)
        ukeys = {(o, m, str(s)) for o, m, s in us[:hi]}
        rkeys = {(o, m, str(s)) for o, m, s in rung_units}
        last = k == len(cfg['rungs'])
        st['kept'] = st['alive'] if last else cut(games, st['alive'], ukeys, rkeys, cfg['keep'], cfg['seed'], k)
        f.write_text(json.dumps(st) + '\n')
        text, _ = render(cfg, games, players, ukeys, f'race {d.name}: rung {k}/{len(cfg["rungs"])}, units 0-{hi - 1}'
                         f' ({hi} units, {2 * hi} games a bot); kept: {" ".join(st["kept"])}')
        (d / f'rung{k}.txt').write_text(text)
        print(text, flush=True)
        alive, lo = st['kept'], hi
    hdr = subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), '--census-header'], capture_output=True, text=True)
    raw = d / 'census.raw'
    if raw.exists() and hdr.returncode == 0:
        (d / 'census.csv').write_text('rung,a,b,map,seed,' + hdr.stdout.strip() + '\n' + raw.read_text())
        raw.unlink()
    games = read_games(d)
    ukeys = {(o, m, str(s)) for o, m, s in us}
    text, rows = render(cfg, games, [base] + alive, ukeys, f'race {d.name}: final ({len(us)} units)')
    text += f"WINNER {rows[0][0]}" + (' (the base)' if rows[0][0] == base else ' (a variant)') + '\n'
    (d / 'final.txt').write_text(text)
    print(text + 'RACE DONE', flush=True)


def standings(d):
    d = Path(d)
    cfg = swiss.read_cfg(d)
    games = read_games(d)
    us = read_units(d)
    played = {(g['opp'], g['map'], g['seed']) for g in games}
    hi = max([i + 1 for i, (o, m, s) in enumerate(us) if (o, m, str(s)) in played], default=0)
    players = [cfg['base']] + sorted({g['bot'] for g in games} - {cfg['base']})
    text, _ = render(cfg, games, players, {(o, m, str(s)) for o, m, s in us[:hi]}, f'race {d.name}: {len(games)} games')
    return text


def analyse(d):
    """Win share by level of each constant that varies among the bots, on rung 1's games (every bot played them)."""
    d = Path(d)
    bots = swiss.read_bots(d)
    games = [g for g in read_games(d) if g['rung'] == '1']
    setting = {b: s for b, _, s in bots}
    out = []
    for x in bots[0][2]:
        levels = sorted({s[x] for s in setting.values()})
        if len(levels) < 2:
            continue
        parts = []
        for v in levels:
            gs = [g for g in games if setting[g['bot']][x] == v]
            won = sum(1.0 if g['result'] == 'win' else 0.5 if g['result'] == 'unknown' else 0.0 for g in gs)
            parts.append(f'{v}: {won:g}/{len(gs)}' + (f' {won / len(gs):.3f}' if gs else ''))
        out.append(f'{x:22s} ' + '  '.join(parts))
    return '\n'.join(out) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init')
    p.add_argument('--base', default='c_knob1')
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--grid', action='append', default=[], help='NAME=v1,v2,... (repeat: the full product)')
    p.add_argument('--sample', type=int, default=0, help='random candidates drawn by tools/param.py')
    p.add_argument('--k', type=int, help='--sample in local mode: each draw re-draws only k constants')
    p.add_argument('--always', default='')
    p.add_argument('--pool', default='')
    p.add_argument('--opps', default=','.join(OPPS))
    p.add_argument('--maps', default=','.join(PANEL_MAPS))
    p.add_argument('--rungs', default='8,16,32', help='cumulative units a surviving bot has played after each rung')
    p.add_argument('--keep', type=float, default=0.5)
    p.add_argument('--tag', default='')
    p.add_argument('--prefix', default='c_rc')
    p = sub.add_parser('run')
    p.add_argument('dir')
    p.add_argument('--jobs', type=int, default=5)
    p.add_argument('--no-census', action='store_true')
    p.add_argument('--keep-replays', action='store_true')
    for c in ('standings', 'analyse'):
        sub.add_parser(c).add_argument('dir')
    p = sub.add_parser('export')
    p.add_argument('dir')
    p.add_argument('bot')
    p.add_argument('newpkg')
    a = ap.parse_args(argv)
    if a.cmd == 'init':
        if a.pool and not a.k:
            sys.exit('!! --pool needs --k (local mode)')
        print(init(a.base, a.seed, a.grid, a.sample, a.k, tuple(x for x in a.always.split(',') if x),
                   tuple(x for x in a.pool.split(',') if x) or None, a.opps.split(','), a.maps.split(','),
                   [int(x) for x in a.rungs.split(',')], a.keep, a.tag, a.prefix))
    elif a.cmd == 'run':
        run(a.dir, a.jobs, not a.no_census, a.keep_replays)
    elif a.cmd == 'standings':
        print(standings(a.dir), end='')
    elif a.cmd == 'analyse':
        print(analyse(a.dir), end='')
    elif a.cmd == 'export':
        bots = {b: s for b, _, s in swiss.read_bots(a.dir)}
        cfg = swiss.read_cfg(a.dir)
        d = param.make(cfg['base'], a.newpkg, bots[a.bot], note=f'race {Path(a.dir).name} bot {a.bot}')
        print(f'wrote {d}')


if __name__ == '__main__':
    main()
