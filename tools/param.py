#!/usr/bin/env python3
"""Parameterised bots: C.java constants overridden at build time (owner, PROMPTS 114).

  tools/param.py space [BASE]                         # the search space: range, BASE's value, constraints
  tools/param.py make BASE NEW [NAME=VALUE ...]       # src/NEW = src/BASE with those C.java constants replaced
  tools/param.py make BASE NEW --out DIR ...          # ... written to DIR/NEW instead (Swiss runs: never src/)
  tools/param.py sample BASE --n K --seed S           # K random valid settings of the space, one JSON line each

Why build time and not a run-time switch: the engine hands a bot only bc.testing.* properties, the same ones to both
teams (RULES 9.7, 9.9); the replica and the ladder pass none; javac inlines static final constants, so a run-time read
would change both bytecode costs and the code that plays. A generated package keeps the base's semantics exactly and
can be screened, put on the panel and submitted like any other build.

The space holds the numeric constants that steer play in c_well9 (economy, siege, production, launchers, carriers,
navigation, anchors, mending, probes, hot wells). Left out: switches (booleans, ROLES, HQ_THREAT), constants dead
under the current switches (MANA2_*, AD_LOW, OPENING_ROUNDS, EARLY_CAP_UNTIL/CARRIER_*, PROBE_EARLY,
PROBE_FRONT_MIN, LAUNCHERS_PER_AMP), rule facts (THREAT_R2), bit layouts (PROBE_SHIFT), and the bytecode guards and
telemetry constants (zero overruns is a basics bar).
"""
import argparse, json, random, re, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# name, lo, hi, note[, opts]. Every range holds c_well9's value; integers are drawn uniformly. opts: 'off' drawn with
# probability 'p_off' (SIEGE_ROTATE_FROM 2000 = never rotate, c_well9's setting); 'optional': only in bases that
# define the constant (c_knob1's micro knobs).
SPACE = [
    # swarm economy (Carrier.swarmRole, HQ carrier cap)
    ('AD_NEED', 25, 100, 'HQ asks for Ad below this'),
    ('AD_EARLY_EVERY', 4, 16, 'one carrier in N mines Ad early (id % N)'),
    ('AD_ROLE_FROM', 100, 400, 'round the late Ad role starts'),
    ('AD_LATE_EVERY', 2, 8, 'one carrier in N mines Ad late'),
    ('CAP_PER_MN_WELL', 4, 12, 'carrier cap per known mana well'),
    ('CAP_MIN_PER_HQ', 3, 10, 'carrier cap floor per HQ'),
    ('CAP_MAX', 20, 45, 'carrier cap ceiling'),
    ('CAP_GROW_ROUNDS', 25, 100, 'floor grows by 1 per N rounds'),
    # siege and objectives (Launcher)
    ('SIEGE_ROTATE_FROM', 400, 1600, 'siege target rotation from this round', {'off': 2000, 'p_off': 0.5}),
    ('SIEGE_ROTATE', 50, 200, 'rounds per rotation step'),
    ('RING_MIN', 10, 20, 'siege ring inner r2 (aura is 9)'),
    ('RING_MAX', 26, 45, 'siege ring outer r2'),
    ('RAID_R2', 50, 200, 'raid wells within r2 of an enemy HQ'),
    ('RAID_CLEAR_ROUNDS', 20, 80, 'skip a cleared raid well this long'),
    ('ISLAND_HUNT_START', 0, 300, 'hunt enemy islands from this round'),
    ('SIGHTING_R2', 25, 150, 'shared sighting is an objective within r2'),
    ('RAID_ALARM', 2, 5, 'HQ alarm level that recalls'),
    ('RECALL_R2', 100, 400, 'recall launchers within r2 of the HQ'),
    ('RECALL_UNTIL', 300, 1000, 'recall only before this round'),
    # HQ production
    ('ANCHOR_START', 150, 400, 'anchors from this round'),
    ('ANCHOR_MIN_LAUNCHERS', 6, 20, 'launchers built before an anchor'),
    ('ROBOTS_BASE', 20, 45, 'carrier build gate: robots below base + per-well x wells'),
    ('ROBOTS_PER_WELL', 8, 25, 'per known well'),
    ('ANCHOR_PERIOD', 15, 60, 'one anchor per N rounds per HQ'),
    ('ANCHOR_TIMEOUT', 75, 300, 'carrier gives an unplaced anchor back after N turns'),
    ('HQ_DANGER_R2', 9, 34, 'HQ threatened by a fighter within r2'),
    ('LAUNCHER_BATCH', 1, 3, 'launchers per batch'),
    # launchers
    ('GROUP_MIN', 2, 7, 'launchers in vision to advance'),
    ('FOLLOW_R2', 4, 20, 'follow the leader beyond r2'),
    ('FORM_R2', 20, 100, 'forming zone r2 around our HQ'),
    ('HOME_DEFENCE_R2', 9, 100, 'lone launcher chases sightings within r2 of our HQ'),
    ('ISLAND_FRESH', 4, 16, 'republish island observations younger than N rounds'),
    # carriers
    ('CARRIER_RETURN_LOAD', 20, 40, 'return home at this load (capacity 40)'),
    ('AD_BANK_CAP', 75, 300, 'late Ad carrier switches to mana when its HQ banks this'),
    ('WELL_SEARCH_TURNS', 30, 120, 'turns searching for a well of its type'),
    ('UNJAM_TURNS', 3, 10, 'still turns before stepping aside'),
    ('WELL_CROWD_PATIENCE', 3, 12, 'turns at a crowded well before switching'),
    # navigation
    ('FIELD_MIN_D2', 10, 40, 'distance field only for targets beyond r2'),
    ('FIELD_RESTART', 8, 30, 'stale field restarts at most every N rounds'),
    ('FIELD_KEEP', 5, 20, 'a field used in the last N rounds is kept'),
    ('FORM_MAX_TURNS', 8, 30, 'forming launcher waits at most N turns'),
    ('FIELD_NEAR_D2', 50, 200, 'a field serves targets within r2 of its own'),
    ('FIELD_FAR_D2', 100, 300, '... while the target is beyond r2'),
    ('FIELD_YOUNG', 30, 120, 'a field younger than N rounds is kept'),
    # anchors, scouting, couriers (c_anc3)
    ('PRESS_BUCKET', 15, 50, 'pressure bucket rounds'),
    ('PRESS_SUM', 50, 200, 'fighter-rounds in a bucket that mark an HQ pressed'),
    ('ANCHOR_GATE_UNTIL', 800, 2000, 'anchor gate (not pressed, islands even) until this round'),
    ('ANCHOR_BLIND_FROM', 250, 800, 'anchors for unlocated islands from this round'),
    ('ANCHOR_BLIND_PERIOD', 75, 300, '... at most one per N rounds'),
    ('SCOUT_FROM', 75, 300, 'island scouts from this round'),
    ('SCOUT_EVERY', 8, 32, 'one carrier in N scouts (id % N == 1)'),
    ('SCOUT_MAX_TURNS', 100, 400, 'scout gives up after N turns'),
    ('COURIER_BLOCKED', 6, 24, 'threatened courier turns before taking the anchor home'),
    ('COURIER_SIGHT_R2', 25, 150, 'no anchor for an island with a sighting within r2'),
    # mending (c_mend1)
    ('MEND_HP', 40, 120, 'start mending at or below this HP'),
    ('MEND_FULL', 140, 200, 'stop mending at this HP (max 200)'),
    ('MEND_R2', 64, 256, 'mend on owned islands within r2'),
    ('MEND_RECHECK', 5, 20, 'rounds between mending-target checks'),
    ('MEND_SIGHT_R2', 16, 64, 'skip islands with a sighting within r2'),
    # well probes (c_well3-c_well9)
    ('PROBE_UNTIL', 100, 300, 'probe claims before this round'),
    ('PROBE_FAR', 12, 24, 'probe when the nearest mana well is farther (Chebyshev)'),
    ('PROBE_NEAR', 4, 10, 'diagonal probe points at +-N'),
    ('PROBE_TOWARD', 10, 24, 'midpoint toward the enemy capped at N'),
    ('PROBE_TURNS', 40, 100, 'a probe walks at most N turns'),
    ('PROBE_SEE', 4, 16, 'a probe point is covered within r2'),
    ('PROBE_POINT_TURNS', 8, 25, 'turns aimed at a point before dropping it when stuck'),
    ('REPICK_MARGIN', 2, 8, 'well re-pick margin (Chebyshev)'),
    # hot wells (c_well6)
    ('HOT_NEAR_D2', 50, 200, 'enemy fighter within r2 of our front well makes it hot'),
    ('HOT_HOME_D2', 36, 144, 'only wells beyond r2 of our HQ can turn hot'),
    ('HOT_FRONT_PCT', 20, 60, '... and at least N% of their r2 to the enemy HQ'),
    ('HOT_LEVEL', 1, 3, 'hot level set by a mark (2-bit field)'),
    ('HOT_DECAY', 16, 64, 'hot level drops by 1 every N rounds'),
    ('HOT_LOCAL', 32, 128, 'a fleeing carrier remembers its hot spot N rounds'),
    # micro knobs (c_knob1; c_well9 hard-codes 2 and 1)
    ('AHEAD_MIN', 0, 3, 'fight() steps in to fire when ahead by N (allies + 1 - enemy fighters)', {'optional': True}),
    ('HOLD_THREAT', 0, 3, 'otherwise fire only from tiles at most N enemy fighters reach', {'optional': True}),
    ('STAND_THREAT', -1, 3, 'after firing, stay put when at most N enemy fighters reach the tile (-1: kite)',
     {'optional': True}),
]
SPACE_NAMES = frozenset(sp[0] for sp in SPACE)

# Settings that make no sense are never drawn and never built (owner: "Don't include nonsensical settings, like
# max < min"). Each is a Python expression over the setting's names.
CONSTRAINTS = [
    'RING_MIN + 8 <= RING_MAX',             # a ring a launcher can stand in, outside the r2 9 aura
    'CAP_MIN_PER_HQ <= CAP_MAX',            # floor under the ceiling
    'AD_LATE_EVERY <= AD_EARLY_EVERY',      # the late Ad role is the larger one (anchors need Ad)
    'MEND_HP + 20 <= MEND_FULL',            # start mending at least one hit below the stop
    'PROBE_NEAR < PROBE_FAR',               # the diagonals lie nearer than "far"
    'PROBE_NEAR <= PROBE_TOWARD',           # ... and no farther than the front point
    'FIELD_NEAR_D2 < FIELD_FAR_D2',         # near and far bands of a field's target
    'ANCHOR_START <= ANCHOR_BLIND_FROM',    # blind anchors only once anchors are built
    'ANCHOR_START < ANCHOR_GATE_UNTIL',     # the gate covers the anchor phase
    'COURIER_BLOCKED < ANCHOR_TIMEOUT',     # blocked couriers give up before the timeout would
]

DECL = re.compile(r'public static final (int|long|boolean) ([^;]*);')


def spec(name):
    for s in SPACE:
        if s[0] == name:
            return s
    return None


def c_java(base):
    return REPO / 'src' / base / 'C.java'


def constants(text):
    """{name: (type, value text)} of every public static final constant in a C.java text."""
    out = {}
    for m in DECL.finditer(text):
        for part in m.group(2).split(','):
            name, _, val = part.partition('=')
            out[name.strip()] = (m.group(1), val.strip())
    return out


def int_value(v):
    return int(v.rstrip('Ll').replace('_', ''))


def opts(s):
    return s[4] if len(s) > 4 else {}


def base_setting(text):
    """The base's value of every space constant it defines (ValueError when a required one is missing or not an
    int; an optional one the base lacks is left out)."""
    c = constants(text)
    out = {}
    for s in SPACE:
        if s[0] not in c and opts(s).get('optional'):
            continue
        if s[0] not in c or c[s[0]][0] != 'int':
            raise ValueError(f'{s[0]} is not an int constant of the base')
        out[s[0]] = int_value(c[s[0]][1])
    return out


def violations(setting):
    """The constraints a full setting breaks (empty = valid); a constraint on a constant the setting lacks is moot."""
    out = []
    for e in CONSTRAINTS:
        try:
            if not eval(e, {}, dict(setting)):
                out.append(e)
        except NameError:
            pass
    return out


def apply(text, overrides):
    """C.java text with each NAME's value replaced; only declarations change, comments stay as they are."""
    c = constants(text)
    for name, val in overrides.items():
        if name not in c:
            raise ValueError(f'no constant {name}')
        typ = c[name][0]
        if typ == 'boolean':
            if val not in ('true', 'false'):
                raise ValueError(f'{name} is boolean: {val!r}')
        elif not re.fullmatch(r'-?\d+', str(val)):
            raise ValueError(f'{name} is {typ}: {val!r}')
    pat = re.compile(r'\b(' + '|'.join(map(re.escape, overrides)) + r')(\s*=\s*)([-\w.]+)') if overrides else None

    def decl(m):
        if pat is None:
            return m.group(0)
        typ = m.group(1)
        return pat.sub(lambda v: v.group(1) + v.group(2) + str(overrides[v.group(1)]) + ('L' if typ == 'long' else ''),
                       m.group(0))
    return DECL.sub(decl, text)


def make(base, new, overrides, out=None, force=False, check=True, note=''):
    """Write package `new` = src/`base` with C.java overrides; returns the package dir. Refuses an existing dir."""
    if not re.fullmatch(r'[a-z_][a-z0-9_]*', new):
        raise ValueError(f'bad package name {new!r}')
    src = REPO / 'src' / base
    dst = Path(out or REPO / 'src') / new
    if dst.exists() and not force:
        raise FileExistsError(f'{dst} exists')
    text = (src / 'C.java').read_text()
    if check:
        setting = dict(base_setting(text))
        setting.update({k: int(v) for k, v in overrides.items() if k in setting})
        bad = violations(setting)
        if bad:
            raise ValueError('nonsensical setting: ' + '; '.join(bad))
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for f in sorted(src.glob('*.java')):
        t = f.read_text()
        if f.name == 'C.java':
            t = apply(t, overrides)
            ovs = ' '.join(f'{k}={v}' for k, v in sorted(overrides.items())) or '(none)'
            lines = ['// GENERATED by tools/param.py from ' + base + (f' ({note})' if note else '') + '; overrides:']
            line = '//  '
            for w in ovs.split():
                if len(line) + len(w) > 118:
                    lines.append(line)
                    line = '//  '
                line += ' ' + w
            lines.append(line)
            t = re.sub(r'^(package \w+;)\n', lambda m: m.group(1) + '\n' + '\n'.join(lines) + '\n', t, count=1, flags=re.M)
        t = re.sub(r'^package ' + re.escape(base) + ';', f'package {new};', t, flags=re.M)
        t = re.sub(r'\b' + re.escape(base) + r'\.(?=[A-Z])', new + '.', t)   # qualified references, not comments
        (dst / f.name).write_text(t)
    return dst


def draw(rng, s):
    o = opts(s)
    if 'off' in o and rng.random() < o['p_off']:
        return o['off']
    return rng.randint(s[1], s[2])


def sample(n, seed, tries=10000, names=None, base=None, k=None, always=(), pool=None):
    """n random settings of the space (only `names` when given: the constants a base defines), each satisfying every
    constraint (deterministic for a seed). Local mode (base and k given): each setting is `base` with k constants
    re-drawn, the ones in `always` among them, the others from `pool` when given (else from the whole space)."""
    rng = random.Random(seed)
    space = [sp for sp in SPACE if names is None or sp[0] in names]
    out = []
    while len(out) < n:
        for _ in range(tries):
            if k is None:
                s = {sp[0]: draw(rng, sp) for sp in space}
            else:
                s = dict(base)
                forced = [sp for sp in space if sp[0] in always]
                rest = [sp for sp in space if sp[0] not in always and (pool is None or sp[0] in pool)]
                for sp in forced + rng.sample(rest, max(0, k - len(forced))):
                    s[sp[0]] = draw(rng, sp)
            if not violations(s):
                break
        else:
            raise RuntimeError('no valid setting found')
        out.append(s)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('space')
    p.add_argument('base', nargs='?', default='c_well9')
    p = sub.add_parser('make')
    p.add_argument('base')
    p.add_argument('new')
    p.add_argument('overrides', nargs='*', help='NAME=VALUE')
    p.add_argument('--out', help='parent dir of the new package (default src/)')
    p.add_argument('--force', action='store_true', help='replace an existing package dir')
    p = sub.add_parser('sample')
    p.add_argument('base')
    p.add_argument('--n', type=int, required=True)
    p.add_argument('--seed', type=int, required=True)
    a = ap.parse_args(argv)
    if a.cmd == 'space':
        b = base_setting(c_java(a.base).read_text())
        for s in SPACE:
            if s[0] not in b:
                continue
            extra = f"  ({opts(s)['off']} = off, p {opts(s)['p_off']})" if 'off' in opts(s) else ''
            print(f'{s[0]:22s} {s[1]:5d} .. {s[2]:<5d} {a.base}={b[s[0]]:<6d} {s[3]}{extra}')
        print('constraints: ' + '; '.join(CONSTRAINTS))
        bad = violations(b)
        if bad:
            print(f'!! {a.base} itself breaks: ' + '; '.join(bad))
    elif a.cmd == 'make':
        ov = {}
        for kv in a.overrides:
            k, eq, v = kv.partition('=')
            if not eq:
                ap.error(f'expected NAME=VALUE: {kv}')
            ov[k] = v
        d = make(a.base, a.new, ov, out=a.out, force=a.force)
        print(f'wrote {d}')
    elif a.cmd == 'sample':
        b = base_setting(c_java(a.base).read_text())   # the space must fit the base
        for s in sample(a.n, a.seed, names=set(b)):
            print(json.dumps(s, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, FileExistsError) as e:
        sys.exit(f'!! {e}')
