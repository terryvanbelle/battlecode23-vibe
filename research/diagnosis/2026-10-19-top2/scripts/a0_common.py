# Analyst 0 (maxwelljones14) shared helpers. Run every a0_*.py with python3 -I from any directory.
# Extracts: matches/<id>/extract/*.csv. Per-turn dumps: tools/replay-dump.sh <replay> --sa --team A|B --game N --match M
# --out $SA/<m>g<g><side> (see a0_dump.sh); SA defaults to the session scratchpad and can be set with A0_SA.
import csv, os, struct, functools, collections
REPO = '/home/terryvanbelle/projects/vibe/2023'
R = REPO + '/matches'
SA = os.environ.get('A0_SA', '/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/'
                    '4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/top2/a0/sa')
MAPDIR = '/home/terryvanbelle/projects/vibe/reference/battlecode23/engine/src/main/battlecode/world/resources'
MAXWELL = [9911, 9913, 9918, 9924, 9928, 9930]
OPP = 'maxwelljones14.MPWorking'


def rd(m, f):
    with open(f'{R}/{m}/extract/{f}.csv') as fh:
        return list(csv.DictReader(fh))


def other(s): return 'B' if s == 'A' else 'A'


def d2(a, b): return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


@functools.lru_cache(None)
def games_of(m):
    out = {}
    for r in rd(m, 'games'):
        if r['team'] == 'vibe23':
            out[int(r['game'])] = dict(m=m, g=int(r['game']), map=r['map'], W=int(r['width']), H=int(r['height']),
                                       sym=r['symmetry'], nisl=int(r['islands']), rounds=int(r['rounds']),
                                       us=r['side'], them=other(r['side']), won=int(r['won']), reason=r['win_reason'])
    return out


def all_games():
    L = []
    for m in MAXWELL:
        for g, G in sorted(games_of(m).items()):
            L.append(G)
    return L


def hqs(m, g):
    """{side: [(x, y), ...]} from hq.csv"""
    out = collections.defaultdict(set)
    for r in rd(m, 'hq'):
        if int(r['game']) == g:
            out[r['side']].add((int(r['x']), int(r['y'])))
    return {k: sorted(v) for k, v in out.items()}


# ---- map file (flatbuffer GameMap: 6 walls, 7 clouds, 8 currents, 9 islands, 10 resources)
def _u32(b, o): return struct.unpack_from('<I', b, o)[0]
def _i32(b, o): return struct.unpack_from('<i', b, o)[0]
def _u16(b, o): return struct.unpack_from('<H', b, o)[0]


@functools.lru_cache(None)
def load_map(name):
    b = open(os.path.join(MAPDIR, name + '.map23'), 'rb').read()
    t = _u32(b, 0)
    vt = t - _i32(b, t)
    vlen = _u16(b, vt)

    def fo(i):
        p = vt + 4 + 2 * i
        return 0 if p >= vt + vlen else _u16(b, p)

    def vec(i, fmt):
        o = fo(i)
        if not o: return []
        p = t + o
        p += _u32(b, p)
        n = _u32(b, p)
        p += 4
        return list(struct.unpack_from('<%d%s' % (n, fmt), b, p))
    mn = t + fo(1); mx = t + fo(2)
    W, H = _i32(b, mx) - _i32(b, mn), _i32(b, mx + 4) - _i32(b, mn + 4)
    return dict(W=W, H=H, walls=vec(6, 'B'), clouds=vec(7, 'B'), currents=vec(8, 'i'), islands=vec(9, 'i'),
                res=vec(10, 'i'))


def wells(name):
    """[(x, y, type)] type 1 Ad, 2 Mn"""
    m = load_map(name); W = m['W']
    return [(k % W, k // W, v) for k, v in enumerate(m['res']) if v > 0]


def bfs(name, src):
    """8-connected walk distance (moves) from the tiles in src, walls blocked; currents and clouds ignored."""
    m = load_map(name); W, H = m['W'], m['H']; wall = m['walls']
    dist = [-1] * (W * H)
    q = collections.deque()
    for (x, y) in src:
        dist[x + y * W] = 0; q.append((x, y))
    while q:
        x, y = q.popleft(); dd = dist[x + y * W]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (dx or dy) and 0 <= nx < W and 0 <= ny < H:
                    k = nx + ny * W
                    if dist[k] < 0 and not wall[k]:
                        dist[k] = dd + 1; q.append((nx, ny))
    return dist


_SKIP = ('map', 'move_dir', 'move_dirs', 'atk_target_type', 'collect_res', 'throw_target_type', 'atk_hit')


@functools.lru_cache(None)
def sa(m, g, side, kind, rmax=10 ** 6):
    """per-turn rows of one team (kind L, HQ or C) up to round rmax (rows are in round order); cached"""
    p = f'{SA}/{m}g{g}{side}/sa_{kind}.csv'
    rows = []
    with open(p) as fh:
        for r in csv.DictReader(fh):
            if int(r['round']) > rmax: break
            rows.append(r)
    for r in rows:
        for k, v in r.items():
            if k in _SKIP:
                continue
            if v not in ('', None):
                try: r[k] = int(v)
                except ValueError: pass
            else:
                r[k] = None
    return rows


def label(G):
    return f"{G['m']} g{G['g']} {G['map']}"
