"""Analyst 3 (opening economy, all 48 top-2 games): shared loaders. Run every a3_*.py with python3 -I from any directory.

Inputs (read-only):
  matches/<m>/extract/{games,census,robots,trips,deaths,hq,timeline}.csv     (both teams, from the replay)
  per-turn --sa dumps (both teams):   carl (not 10060): $A3_SA_CARL/<m>g<g><side>   (rounds < 300, made by a1_split.sh)
                                      10060:            $A3_SA_10060/<m>g<g><side>
                                      maxwell:          $A3_SA_MAX/<m>g<g><side>
  our telemetry turn codes:           $A3_TT_CARL/<m>/tele_turns.csv, $A3_TT_MAX/<m>/tele_turns.csv
  map files:                          engine resources (wells, walls)
Regenerate missing dumps with tools/replay-dump.sh <replay> --sa --team A|B --game N --match M --out DIR (see a0_dump.sh),
always under flock + DUMP_XMX=500m.
"""
import csv, os, struct, functools, collections, statistics

REPO = '/home/terryvanbelle/projects/vibe/2023'
R = REPO + '/matches'
SP = '/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/top2'
SA_CARL = os.environ.get('A3_SA_CARL', SP + '/a1/sa300')
SA_10060 = os.environ.get('A3_SA_10060', SP + '/a2/sa')
SA_MAX = os.environ.get('A3_SA_MAX', SP + '/a0/sa')
TT_CARL = os.environ.get('A3_TT_CARL', SP + '/a1/tt')
TT_MAX = os.environ.get('A3_TT_MAX', SP + '/a0/ext')
MAPDIR = '/home/terryvanbelle/projects/vibe/reference/battlecode23/engine/src/main/battlecode/world/resources'

CARL = [9888, 9900, 9912, 9914, 9915, 9921, 9925, 9929, 9931, 10060]
MAXW = [9911, 9913, 9918, 9924, 9928, 9930]
US = 'vibe23'
DUP = {(9921, 0)}          # 9921 g0 replays 9888 g0 exactly (Frog); excluded from pooled statistics


def other(s): return 'B' if s == 'A' else 'A'


def d2(a, b): return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def med(v):
    v = [x for x in v if x is not None]
    return statistics.median(v) if v else None


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def num(x, d=None):
    if x in (None, ''): return d
    try: return int(x)
    except ValueError:
        try: return float(x)
        except ValueError: return d


@functools.lru_cache(None)
def rd(m, f):
    with open(f'{R}/{m}/extract/{f}.csv') as fh:
        return list(csv.DictReader(fh))


@functools.lru_cache(None)
def games():
    """the 48 games in task order: dict m g map W H nhq us them won reason rounds opp dup"""
    out = []
    for m in CARL + MAXW:
        gs = {}
        for r in rd(m, 'games'):
            g = int(r['game'])
            d = gs.setdefault(g, dict(m=m, g=g, map=r['map'], W=int(r['width']), H=int(r['height']),
                                      rounds=int(r['rounds']), nisl=int(r['islands'])))
            if r['team'] == US:
                d.update(us=r['side'], them=other(r['side']), won=int(r['won']), reason=r['win_reason'])
            else:
                d['opp'] = 'carl' if m in CARL else 'maxwell'
        for g in sorted(gs):
            G = gs[g]
            G['dup'] = (m, g) in DUP
            G['hqs'] = hq_pos(m, g)
            G['nhq'] = len(G['hqs'][G['us']])
            out.append(G)
    return out


def label(G): return f"{G['m']} g{G['g']} {G['map']}"


@functools.lru_cache(None)
def hq_pos(m, g):
    out = collections.defaultdict(list)
    for r in rd(m, 'robots'):
        if int(r['game']) == g and r['type'] == 'H':
            out[r['side']].append((int(r['x_born']), int(r['y_born'])))
    return {k: sorted(v) for k, v in out.items()}


def census(G, side):
    for r in rd(G['m'], 'census'):
        if int(r['game']) == G['g'] and r['side'] == side: return r


def timeline(G, side):
    """{round: row} every 10 rounds"""
    return {int(r['round']): r for r in rd(G['m'], 'timeline') if int(r['game']) == G['g'] and r['side'] == side}


def robots(G, side=None):
    return [r for r in rd(G['m'], 'robots') if int(r['game']) == G['g'] and (side is None or r['side'] == side)]


def trips(G, side=None):
    return [r for r in rd(G['m'], 'trips') if int(r['game']) == G['g'] and (side is None or r['side'] == side)]


def deaths(G, side=None):
    return [r for r in rd(G['m'], 'deaths') if int(r['game']) == G['g'] and (side is None or r['side'] == side)]


def hqrows(G, side=None):
    return [r for r in rd(G['m'], 'hq') if int(r['game']) == G['g'] and (side is None or r['side'] == side)]


# ---- map file (flatbuffer GameMap: 6 walls, 7 clouds, 8 currents, 9 islands, 10 resources); same reader as a0_common
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
    return dict(W=W, H=H, walls=vec(6, 'B'), clouds=vec(7, 'B'), res=vec(10, 'i'))


def wells(name):
    """[(x, y, type)] type 1 Ad, 2 Mn"""
    m = load_map(name); W = m['W']
    return [(k % W, k // W, v) for k, v in enumerate(m['res']) if v > 0]


@functools.lru_cache(None)
def bfs(name, src):
    """8-connected walk distance (moves) from the tiles in src (tuple), walls blocked; currents and clouds ignored."""
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


def walk(name, a, b):
    """walk moves from tile a to the nearest tile adjacent to (or on) b (a carrier collects from Chebyshev 1)"""
    m = load_map(name); W = m['W']
    dist = bfs(name, (a,))
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            x, y = b[0] + dx, b[1] + dy
            if 0 <= x < W and 0 <= y < m['H'] and dist[x + y * W] >= 0:
                v = dist[x + y * W]
                if best is None or v < best: best = v
    return best


def mapfeat(G, side):
    """per side: walk distance HQ -> nearest Mn / Ad well (min over this side's HQs, and per HQ), d2 nearest Mn"""
    name = G['map']; ws = wells(name)
    mn = [(x, y) for x, y, t in ws if t == 2]; ad = [(x, y) for x, y, t in ws if t == 1]
    per = []
    for h in G['hqs'][side]:
        wm = min((walk(name, h, w) for w in mn if walk(name, h, w) is not None), default=None)
        wa = min((walk(name, h, w) for w in ad if walk(name, h, w) is not None), default=None)
        dm = min((d2(h, w) for w in mn), default=None)
        per.append(dict(hq=h, walk_mn=wm, walk_ad=wa, d2_mn=dm))
    return dict(per=per, walk_mn=min(p['walk_mn'] for p in per), walk_ad=min(p['walk_ad'] for p in per),
                walk_mn_mean=mean([p['walk_mn'] for p in per]), d2_mn=min(p['d2_mn'] for p in per),
                n_mn=len(mn), n_ad=len(ad), area=G['W'] * G['H'])


# ---- per-turn dumps
def sa_dir(G, side):
    m = G['m']
    base = SA_MAX if m in MAXW else SA_10060 if m == 10060 else SA_CARL
    return f"{base}/{m}g{G['g']}{side}"


_SKIP = ('map', 'move_dir', 'move_dirs', 'atk_target_type', 'collect_res', 'throw_target_type', 'atk_hit', 'pos_note')


@functools.lru_cache(maxsize=8)
def sa(m, g, side, kind, rmax=300):
    G = [x for x in games() if x['m'] == m and x['g'] == g][0]
    p = f'{sa_dir(G, side)}/sa_{kind}.csv'
    rows = []
    with open(p) as fh:
        for r in csv.DictReader(fh):
            if int(r['round']) > rmax: break
            for k, v in r.items():
                if k in _SKIP: continue
                r[k] = num(v)
            rows.append(r)
    return rows


@functools.lru_cache(maxsize=4)
def tele(m, rmax=300):
    """our telemetry codes: {(game, round, id): (type, code_bcc)} for rounds <= rmax"""
    base = TT_MAX if m in MAXW else TT_CARL
    out = {}
    with open(f'{base}/{m}/tele_turns.csv') as fh:
        next(fh)
        for line in fh:
            p = line.split(',', 8)          # match,game,round,id,side,type,used,code_bcc,...
            rn = int(p[2])
            if rn > rmax: continue
            c = p[7]
            out[(int(p[1]), rn, int(p[3]))] = (p[5], int(c) if c else None)
    return out


CSTATES = "!GCWSXRDFVTKQEYP"      # Telemetry.CARRIER_STATES; carrier code = state << 1 | (role == Mn)
HQCODES = ".bgpwcastx"            # Telemetry L_HQ: code & 15


def pool(games_, key):
    return [key(G) for G in games_]


def fmt(x, nd=0):
    if x is None: return '-'
    if isinstance(x, float): return f'{x:.{nd}f}'
    return str(x)
