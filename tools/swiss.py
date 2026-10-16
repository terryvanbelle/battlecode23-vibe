#!/usr/bin/env python3
"""Swiss tournament of random C.java settings around a base bot (owner, PROMPTS 114).

  tools/swiss.py init --base c_well9 --n 4 --seed 114 [--maps Forest,DefaultMap,Maze] [--tag t]
        prints the new run dir gauntlet/<stamp>-swiss[-t]/: config.json and bots.tsv, 2^n bots = the base itself and
        2^n - 1 variants drawn by tools/param.py (every space constant random, every constraint met)
  tools/swiss.py run DIR [--jobs 5]        build every bot into DIR/classes, then play the rounds (resumable)
  tools/swiss.py standings DIR             the table after the games so far
  tools/swiss.py analyse DIR               rank correlation of each constant with the points
  tools/swiss.py export DIR BOT NEWPKG     src/NEWPKG = the base with BOT's constants (tools/param.py make)

Runs on the VM (tools/vm-run.sh). A round pairs bots of equal standing (Monrad: sorted by points, Buchholz, then a
seeded draw; neighbours meet unless they met before) and each pair plays every map from both sides on one seed per
map, 2 x maps games. A won game is a point; a game without a result gives half a point each. Standings: points, then
Buchholz (the opponents' points), then the base ahead of a variant (a variant must beat the incumbent outright). Games
take the machine-wide slots of tools/gauntlet.sh (/tmp/bc23-game-slots), so they share the VM with screens and
gauntlets. Replays are reduced to census rows (tools/replay-dump.sh --census) and deleted (--keep-replays keeps them).
"""
import argparse, concurrent.futures as cf, csv, fcntl, hashlib, json, os, random, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import param  # noqa: E402

LONG = {'Forest': 4, 'Cornucopia': 4, 'MassiveL': 3}   # long maps start first, so a round's tail is short
FIELDS = ['round', 'a', 'b', 'map', 'seed', 'winner', 'winner_side', 'rounds', 'reason', 'secs', 'exc_lines']


def bot_hash(pkg):
    return subprocess.run(['bash', str(TOOLS / 'bot-hash.sh'), pkg], capture_output=True, text=True,
                          check=True).stdout.strip()


def read_cfg(d):
    return json.loads((Path(d) / 'config.json').read_text())


def read_bots(d):
    """[(name, kind, {constant: value})] in bots.tsv order."""
    rows = list(csv.reader(open(Path(d) / 'bots.tsv'), delimiter='\t'))
    names = rows[0][2:]
    return [(r[0], r[1], dict(zip(names, map(int, r[2:])))) for r in rows[1:]]


def read_games(d):
    f = Path(d) / 'games.csv'
    return list(csv.DictReader(open(f))) if f.exists() else []


def read_pairs(d):
    """{round: [(x, y)]} for every paired round."""
    out = {}
    for f in Path(d).glob('round*.json'):
        out[int(f.stem[5:])] = [tuple(p) for p in json.loads(f.read_text())]
    return out


def game_seed(seed, r, x, y, m):
    """One engine seed per (round, pair, map), the same for both sides."""
    return 1 + int(hashlib.sha1(f'{seed}/{r}/{x}/{y}/{m}'.encode()).hexdigest()[:7], 16)


def points(games, names):
    pts = {b: 0.0 for b in names}
    for g in games:
        if g['winner'] in pts:
            pts[g['winner']] += 1
        else:                                  # no result: half each
            pts[g['a']] += 0.5
            pts[g['b']] += 0.5
    return pts


def table(names, games, pairs, base):
    """Rows (bot, points, buchholz, games, match W-D-L) best first."""
    pts = points(games, names)
    opp = {b: [] for b in names}
    rec = {b: [0, 0, 0] for b in names}
    for r, prs in pairs.items():
        for x, y in prs:
            opp[x].append(y)
            opp[y].append(x)
            gs = [g for g in games if int(g['round']) == r and {g['a'], g['b']} == {x, y}]
            if not gs:
                continue
            px, py = points(gs, [x, y]).values()
            for b, mine, theirs in ((x, px, py), (y, py, px)):
                rec[b][0 if mine > theirs else 1 if mine == theirs else 2] += 1
    played = {b: sum(1 for g in games if b in (g['a'], g['b'])) for b in names}
    buch = {b: sum(pts[o] for o in opp[b]) for b in names}
    order = sorted(names, key=lambda b: (-pts[b], -buch[b], b != base, b))
    return [(b, pts[b], buch[b], played[b], '-'.join(map(str, rec[b]))) for b in order]


def pair(order, met):
    """Neighbours in `order` meet, never twice (backtracking); None when no such pairing exists."""
    if not order:
        return []
    p = order[0]
    for i in range(1, len(order)):
        q = order[i]
        if q in met[p]:
            continue
        sub = pair(order[1:i] + order[i + 1:], met)
        if sub is not None:
            return [(p, q)] + sub
    return None


def pairing(names, games, pairs, r, seed, base):
    rng = random.Random(f'{seed}/pair/{r}')
    if r == 1:
        order = list(names)
        rng.shuffle(order)
    else:
        rows = table(names, games, pairs, base)
        draw = {b: rng.random() for b in names}
        order = [b for b, *_ in sorted(rows, key=lambda t: (-t[1], -t[2], draw[t[0]]))]
    met = {b: set() for b in names}
    for prs in pairs.values():
        for x, y in prs:
            met[x].add(y)
            met[y].add(x)
    return pair(order, met) or pair(order, {b: set() for b in names})   # a rematch only when nothing else fits


def acquire_slot():
    """A machine-wide game slot (flock on the slot files tools/gauntlet.sh uses); the open file holds it."""
    slotdir = os.environ.get('SLOTDIR', '/tmp/bc23-game-slots')
    n = int(os.environ.get('GAME_SLOTS', '5'))
    os.makedirs(slotdir, exist_ok=True)
    while True:
        for i in range(1, n + 1):
            f = open(f'{slotdir}/slot.{i}', 'a')
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return f
            except OSError:
                f.close()
        time.sleep(2)


def parse(out):
    """(winner side or '?', round or '?', reason) from engine output, as tools/lib.sh parse_result."""
    w = re.findall(r'\(([AB])\) wins', out)
    n = re.findall(r'wins \(round (\d+)\)', out)
    why = re.findall(r'Reason: (.*)', out)
    return (w[-1] if w else '?', n[-1] if n else '?', why[-1].strip() if why else '?')


def play(d, r, ta, tb, m, seed, census=True, keep=False):
    d = Path(d)
    (d / 'replays').mkdir(exist_ok=True)
    replay = d / 'replays' / f'r{r}__{ta}__{tb}__{m}__s{seed}.bc23'
    env = dict(os.environ, CLASSES=str(d / 'classes'), GAME_SEED=str(seed))
    slot = acquire_slot()
    t0 = time.time()
    try:
        p = subprocess.run(['bash', '-c', f'source "{TOOLS}/lib.sh"; run_game "$@"', '_', ta, tb, m, str(replay),
                            '-Dbc.engine.silence-a=true', '-Dbc.engine.silence-b=true'],
                           env=env, capture_output=True, text=True)
    finally:
        slot.close()
    secs = round(time.time() - t0)
    out = p.stdout + p.stderr
    side, rounds, why = parse(out)
    winner = ta if side == 'A' else tb if side == 'B' else '?'
    exc = sum(1 for line in out.splitlines() if 'Exception' in line and not line.lstrip().startswith('at '))
    if census and replay.exists():
        c = subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), str(replay), '--census', '--no-header'],
                           capture_output=True, text=True)
        if c.returncode == 0 and c.stdout.strip():
            with open(d / 'census.raw', 'a') as fh:
                for line in c.stdout.strip().splitlines():
                    fh.write(f'{r},{ta},{tb},{m},{seed},{line}\n')
    if not keep and replay.exists():
        replay.unlink()
    return {'round': r, 'a': ta, 'b': tb, 'map': m, 'seed': seed, 'winner': winner, 'winner_side': side,
            'rounds': rounds, 'reason': why.replace(',', ';'), 'secs': secs, 'exc_lines': exc}


def build(d, cfg, bots):
    """DIR/src: the base as it is plus one generated package per variant; DIR/classes: all compiled."""
    d = Path(d)
    classes = d / 'classes'
    if (classes / '.built').exists():
        return
    h = bot_hash(cfg['base'])
    if h != cfg['base_hash']:
        sys.exit(f"!! src/{cfg['base']} is {h}, the run was drawn for {cfg['base_hash']}")
    src = d / 'src'
    if src.exists():
        shutil.rmtree(src)
    src.mkdir()
    shutil.copytree(REPO / 'src' / cfg['base'], src / cfg['base'])
    for name, kind, s in bots:
        if kind != 'base':
            param.make(cfg['base'], name, s, out=src)
    if classes.exists():
        shutil.rmtree(classes)
    subprocess.run(['bash', '-c', f'source "{TOOLS}/lib.sh"; compile_src "$1" "$2"', '_', str(src), str(classes)],
                   check=True)
    (classes / '.built').write_text(f"{cfg['base']} {h}\n")


def write_standings(d, cfg, names, final=False):
    d = Path(d)
    games, pairs = read_games(d), read_pairs(d)
    rows = table(names, games, pairs, cfg['base'])
    done = max([int(g['round']) for g in games], default=0)
    lines = [f"Swiss {d.name}: base {cfg['base']} ({cfg['base_hash']}), {len(names)} bots, maps {' '.join(cfg['maps'])},"
             f" {len(games)} games, rounds played {done}/{cfg['rounds']}",
             f"{'#':>2} {'bot':12s} {'points':>6s} {'buchholz':>8s} {'games':>5s} {'matches W-D-L':>13s}"]
    for i, (b, p, bh, n, rec) in enumerate(rows, 1):
        lines.append(f"{i:2d} {b:12s} {p:6.1f} {bh:8.1f} {n:5d} {rec:>13s}" + ('  <- base' if b == cfg['base'] else ''))
    unknown = sum(1 for g in games if g['winner'] == '?')
    if unknown:
        lines.append(f'{unknown} games without a result (half a point each)')
    if final:
        w = rows[0][0]
        lines.append(f"WINNER {w}" + (' (the base)' if w == cfg['base'] else ' (a variant)'))
    text = '\n'.join(lines) + '\n'
    (d / ('final.txt' if final else 'standings.txt')).write_text(text)
    return text


def run(d, jobs=5, census=True, keep=False):
    d = Path(d)
    cfg = read_cfg(d)
    bots = read_bots(d)
    names = [b for b, _, _ in bots]
    build(d, cfg, bots)
    for r in range(1, cfg['rounds'] + 1):
        f = d / f'round{r}.json'
        if not f.exists():
            prs = pairing(names, read_games(d), read_pairs(d), r, cfg['seed'], cfg['base'])
            f.write_text(json.dumps(prs))
        prs = [tuple(p) for p in json.loads(f.read_text())]
        done = {(g['a'], g['b'], g['map']) for g in read_games(d) if int(g['round']) == r}
        todo = []
        for x, y in prs:
            for m in cfg['maps']:
                s = game_seed(cfg['seed'], r, x, y, m)
                todo += [(ta, tb, m, s) for ta, tb in ((x, y), (y, x)) if (ta, tb, m) not in done]
        todo.sort(key=lambda g: -LONG.get(g[2], 1))
        total = len(prs) * 2 * len(cfg['maps'])
        print(f'round {r}: {len(prs)} pairs, {len(todo)} of {total} games to play', flush=True)
        new = not (d / 'games.csv').exists()
        with open(d / 'games.csv', 'a', newline='') as fh, cf.ThreadPoolExecutor(jobs) as ex:
            w = csv.DictWriter(fh, FIELDS)
            if new:
                w.writeheader()
            futs = [ex.submit(play, d, r, *g, census=census, keep=keep) for g in todo]
            k = total - len(todo)
            for fu in cf.as_completed(futs):
                g = fu.result()
                w.writerow(g)
                fh.flush()
                k += 1
                print(f"[r{r} {k:3d}/{total}] {g['a']:>10s} vs {g['b']:<10s} {g['map']:12s} -> {g['winner']:10s} "
                      f"r{g['rounds']} {g['secs']}s", flush=True)
        print(write_standings(d, cfg, names), flush=True)
    hdr = subprocess.run(['bash', str(TOOLS / 'replay-dump.sh'), '--census-header'], capture_output=True, text=True)
    raw = d / 'census.raw'
    if raw.exists() and hdr.returncode == 0:
        (d / 'census.csv').write_text('round,a,b,map,seed,' + hdr.stdout.strip() + '\n' + raw.read_text())
        raw.unlink()
    print(write_standings(d, cfg, names, final=True), flush=True)
    print('SWISS DONE', flush=True)


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(xs, ys):
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx = sum((a - mx) ** 2 for a in rx) ** 0.5
    sy = sum((b - my) ** 2 for b in ry) ** 0.5
    return sxy / (sx * sy) if sx and sy else 0.0


def init(base, n, seed, maps, tag='', prefix='c_sw', rounds=None, k=None, always=(), pool=None):
    text = param.c_java(base).read_text()
    b = param.base_setting(text)
    bad = param.violations(b)
    if bad:
        sys.exit(f'!! {base} breaks: ' + '; '.join(bad))
    unknown = [x for x in tuple(always) + tuple(pool or ()) if x not in b or x not in param.SPACE_NAMES]
    if unknown:
        sys.exit(f'!! not in the space of {base}: ' + ', '.join(unknown))
    if pool is not None and k is not None and k > len(set(always) | set(pool)):
        sys.exit(f'!! --k {k} exceeds --always plus --pool ({len(set(always) | set(pool))} constants)')
    variants = param.sample(2 ** n - 1, seed, names=set(b), base=b, k=k, always=always, pool=pool)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    d = REPO / 'gauntlet' / (f'{stamp}-swiss' + (f'-{tag}' if tag else ''))
    d.mkdir(parents=True)
    keys = [s[0] for s in param.SPACE if s[0] in b]
    with open(d / 'bots.tsv', 'w') as fh:
        fh.write('\t'.join(['bot', 'kind'] + keys) + '\n')
        fh.write('\t'.join([base, 'base'] + [str(b[k]) for k in keys]) + '\n')
        for i, s in enumerate(variants, 1):
            fh.write('\t'.join([f'{prefix}{i:02d}', 'variant'] + [str(s[k]) for k in keys]) + '\n')
    cfg = {'base': base, 'base_hash': bot_hash(base), 'n': n, 'rounds': rounds or n, 'maps': maps, 'seed': seed,
           'created_utc': stamp,
           'mode': ('local k=%d always=%s' % (k, ','.join(always)) + (' pool=%s' % ','.join(pool) if pool else '')) if k
           else 'full',
           'space': [list(s[:3]) for s in param.SPACE if s[0] in b],
           'constraints': param.CONSTRAINTS}
    (d / 'config.json').write_text(json.dumps(cfg, indent=1) + '\n')
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init')
    p.add_argument('--base', default='c_well9')
    p.add_argument('--n', type=int, required=True, help='2^n bots')
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--maps', default='Forest,DefaultMap,Maze')
    p.add_argument('--rounds', type=int, help='default n')
    p.add_argument('--tag', default='')
    p.add_argument('--prefix', default='c_sw')
    p.add_argument('--k', type=int, help='local mode: each variant re-draws only k constants (default: all)')
    p.add_argument('--always', default='', help='local mode: constants every variant re-draws (comma-separated)')
    p.add_argument('--pool', default='', help='local mode: draw the other constants only from these (comma-separated)')
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
        print(init(a.base, a.n, a.seed, a.maps.split(','), a.tag, a.prefix, a.rounds, a.k,
                   tuple(x for x in a.always.split(',') if x), tuple(x for x in a.pool.split(',') if x) or None))
    elif a.cmd == 'run':
        run(a.dir, a.jobs, not a.no_census, a.keep_replays)
    elif a.cmd == 'standings':
        print(write_standings(a.dir, read_cfg(a.dir), [b for b, _, _ in read_bots(a.dir)]), end='')
    elif a.cmd == 'analyse':
        bots = read_bots(a.dir)
        names = [b for b, _, _ in bots]
        pts = points(read_games(a.dir), names)
        ys = [pts[b] for b in names]
        res = [(k, spearman([s[k] for _, _, s in bots], ys)) for k in bots[0][2]]
        for k, rho in sorted(res, key=lambda t: -abs(t[1])):
            print(f'{k:22s} {rho:+.2f}')
    elif a.cmd == 'export':
        bots = {b: s for b, _, s in read_bots(a.dir)}
        cfg = read_cfg(a.dir)
        d = param.make(cfg['base'], a.newpkg, bots[a.bot], note=f'Swiss {Path(a.dir).name} bot {a.bot}')
        print(f'wrote {d}')


if __name__ == '__main__':
    main()
