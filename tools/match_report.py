#!/usr/bin/env python3
"""Match reports (docs/TELEMETRY.md part C): every replica replay we download becomes a short report (one screen per
game) and one stable JSON line, so that no game is wasted (owner, PROMPTS 11 and 13). Standard library only.

    tools/match_report.py match <replay.bc23> (--match-json FILE | --match-id ID) [--team-id N] [--shadow REPLAY] [--force]
    tools/match_report.py sweep [--pages N] [--max N]              # our finished matches not yet reported (download+match)
    tools/match_report.py file <replay.bc23> --us A|B --label NAME  # any local replay -> matches/local/NAME.{md,json}
    tools/match_report.py prune [--dry-run]                        # replay retention under matches/ (sweep runs it)
    tools/match_report.py field                                    # Tier 2 (field-vs-field sample): not built yet

Our side is the participant whose team id is --team-id, else whose teamname is $CONTEST_TEAM (default vibe23); it is
replay label A when its player_index is 0. Game i is reversed (HQ ownership flipped) when alternate_order is set and i
is odd, as in contest.run_rows; the labels do not change. Nothing here requests scrimmages or submits.

Outputs, under $MATCH_REPORT_ROOT (default: the repository):
  matches/<id>/extract/       tools/replay-dump.sh --extract (TELEMETRY.md B.4); .stamp = "<ReplayDump sha1[:12]> <replay
                              size>" (tools/contest.py census_of trusts census.csv only when the hash is current)
  research/matches/<id>.md    the report (TELEMETRY.md C.3), at most 8 KB: when longer, detail drops level by level
                              (narratives first, then tables) until it fits
  progress/telemetry.jsonl    one line per match, append-only (C.4, schema v 1); --force or a new --shadow appends a
                              line with "supersedes": true; readers take the last line per match
`match` is idempotent: a match with a line of the current v is skipped (--force redoes the report and the line; the
extract is reused while its stamp is current). When --extract fails (an older reader), the report falls back to
--games and per-game --census and marks every other section "not available".

JSON line = C.4 exactly, plus these keys (all optional for readers):
  line: "maps", "dump" (ReplayDump hash), "extract_note" (legacy fallback reason or null), "supersedes"
  GAME: "tb_margin", "vtb" {"500": "us"|"them"|null, ...}, "first_contact", "stalls" (count; anomalies list <= 3)
  SIDE: "built"/"died" carry all of C L A D B; "at" also has 1000 and 1500, and each at.R has "bank_Mn" and "islands"
        (Mn and Ad at R are cumulative collected; C and L alive; value = army value); "cargo_lost_Ad", "anchors_lost",
        "idle_bank_Mn_p50" (HQ bank Mn in 25-round buckets with idle funds), "pressure9", "pressure34" (enemy
        launcher-rounds near our HQs), "tier2" {exposed_end, group_p50, trip_cycle_p50, partial_loads,
        carriers_per_well, blind_rate, focus, kill_conv} or null
  tele: "invalid", "letter_mismatch", "dots" {roles, role_hq_mn_p50, well_sources, obj, anchor, bug, sym_decided,
        sym_conflicts, comms_fill, exc, nm, ovr, tele_max_cost, tele_errors, tele_deferrals} or null;
        "trip" adds flee_mean and load_mean; "fight" adds outnumbered, moved, fired, guard_breaks
FIGHT definitions: riskier_than_stay = turns whose chosen tile has more threat than staying, over turns that scored the
stay tile; stepin_outnumbered = turns outnumbered that moved closer to the nearest fighter than staying, over all.
Anomalies (C.3) add tele_offset:<k> (decoder offset not 0, TELEMETRY §9) and tele_invalid:<n>. A stall run of a
carrier excludes its collecting rounds (trips.csv; carriers are skipped without it), and every stall excludes rounds
inside any engagement of the game."""
import argparse, csv, datetime, fcntl, hashlib, importlib.util, json, math, os, re, shutil, statistics, subprocess, sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.environ.get('MATCH_REPORT_ROOT') or REPO
TEAM = os.environ.get('CONTEST_TEAM', 'vibe23')
V = 1
MAX_REPORT = 8192
TIMEOUT = 1800
DUMP = os.path.join(REPO, 'tools', 'replay-dump.sh')
DUMP_SRC = os.path.join(REPO, 'tools', 'replaydump', 'ReplayDump.java')
TYPES = 'CLADB'
CAUSES = ('launcher', 'throw', 'destab', 'hq_aura', 'self', 'resign')
CAUSE_COL = {'launcher': 'deaths_launcher', 'throw': 'deaths_throw', 'destab': 'deaths_destab', 'hq_aura': 'deaths_aura',
             'self': 'deaths_self', 'resign': 'deaths_resign'}
AT_ROUNDS = (50, 100, 150, 250, 500, 1000, 1500)
TABLE_ROUNDS = (50, 100, 150, 250, 500, 1000)
KITE = ('stand_fire', 'fire_retreat', 'stepin_fire', 'fire_ambiguous', 'advance', 'retreat', 'hold')
TIER2 = ('exposed_end', 'group_p50', 'trip_cycle_p50', 'partial_loads', 'carriers_per_well', 'blind_rate', 'focus',
         'kill_conv')
TYPE_KEY = {'H': 'HQ', 'C': 'C', 'L': 'L', 'A': 'A', 'D': 'D', 'B': 'B'}
PHASES = ('open', 'mid', 'late')
WELL_SRC = {1: 'shared', 2: 'seen', 3: 'any_shared', 4: 'any_seen', 5: 'crowd_switch'}
OBJ_KIND = {0: 'sighting', 1: 'enemy_island', 2: 'enemy_hq', 3: 'centre', 4: 'regroup_ally', 5: 'regroup_home',
            6: 'follow', 7: 'home_defence'}
ANCH_EV = {1: 'target', 2: 'rejected', 3: 'retarget', 4: 'timeout', 5: 'returned', 6: 'placed', 7: 'took'}
BUG_REASON = {1: 'closer', 2: 'new_target', 3: 'budget'}
NA = 'not available'


# ---------------------------------------------------------------- paths and small helpers
def p_matches():
    return os.path.join(ROOT, 'matches')


def p_reports():
    return os.path.join(ROOT, 'research', 'matches')


def p_jsonl():
    return os.path.join(ROOT, 'progress', 'telemetry.jsonl')


def rel(p):
    """A path relative to ROOT when it lies inside it (the JSON line and the report name files this way)."""
    a, r = os.path.abspath(p), os.path.abspath(ROOT)
    return os.path.relpath(a, r) if a.startswith(r + os.sep) else a


def num(v):
    """'12' -> 12, '0.5' -> 0.5, '' / None / junk -> None."""
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return v if not (isinstance(v, float) and not math.isfinite(v)) else None
    s = str(v).strip()
    if not s or s == '-':
        return None
    try:
        return int(s)
    except ValueError:
        try:
            x = float(s)
            return x if math.isfinite(x) else None
        except ValueError:
            return None


def rnd(x, nd=4):
    return None if x is None else round(x, nd)


def median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def pctl(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    return xs[min(len(xs) - 1, int(math.ceil(q * len(xs))) - 1 if q > 0 else 0)]


def fmt(x, nd=2):
    if x is None:
        return '-'
    if isinstance(x, bool):
        return str(int(x))
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        if x.is_integer() and abs(x) >= 10:
            return str(int(x))
        return f'{x:.{nd}f}'
    return str(x)


def sh(x):
    """A share as '.31' (1.0 -> '1.00')."""
    return '-' if x is None else (f'{x:.2f}'[1:] if 0 <= x < 1 else f'{x:.2f}')


def shares(d, k=6, lo=0.01):
    if not d:
        return '-'
    items = sorted(((v, l) for l, v in d.items() if v is not None and v >= lo), key=lambda t: (-t[0], t[1]))[:k]
    return ' '.join(f'{l} {sh(v)}' for v, l in items) or '-'


def other(side):
    return 'B' if side == 'A' else 'A'


def dump_hash():
    try:
        with open(DUMP_SRC, 'rb') as fh:
            return hashlib.sha1(fh.read()).hexdigest()[:12]
    except OSError:
        return ''


def read_text(p):
    with open(p) as fh:
        return fh.read()


def run_dump(*args, timeout=TIMEOUT):
    return subprocess.run(['bash', DUMP, *[str(a) for a in args]], capture_output=True, text=True, timeout=timeout)


def load_contest():
    spec = importlib.util.spec_from_file_location('contest', os.path.join(REPO, 'tools', 'contest.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- extraction (TELEMETRY.md B.4)
class Extract:
    """The --extract files of one replay, read by column name; a missing file or column is None, never an error."""
    NAMES = ('games', 'census', 'deaths', 'engagements', 'timeline', 'hq', 'robots', 'tele_states', 'trips')

    def __init__(self, d=None, tables=None, legacy=None):
        self.dir, self.legacy = d, legacy
        self.t, self.fields, self._idx = {}, {}, {}
        for n in self.NAMES:
            p = os.path.join(d, n + '.csv') if d else None
            if p and os.path.exists(p):
                with open(p, newline='') as fh:
                    rd = csv.DictReader(fh)
                    self.t[n] = list(rd)
                    self.fields[n] = list(rd.fieldnames or [])
        for n, rows in (tables or {}).items():
            self.t[n] = rows
            self.fields[n] = list(rows[0].keys()) if rows else []
        ev = os.path.join(d, 'tele_events.jsonl') if d else None
        self.events = ev if ev and os.path.exists(ev) else None

    def has(self, n):
        return n in self.t

    def col(self, n, c):
        return c in self.fields.get(n, ())

    def rows(self, n, game, side=None):
        """Rows of table n for one game (and side); None when the file is missing."""
        if n not in self.t:
            return None
        idx = self._idx.get(n)
        if idx is None:
            idx = self._idx[n] = defaultdict(list)
            for r in self.t[n]:
                idx[str(r.get('game'))].append(r)
        rows = idx.get(str(game), [])
        return [r for r in rows if r.get('side') == side] if side else rows

    def row(self, n, game, side):
        rows = self.rows(n, game, side)
        return rows[0] if rows else None

    def games(self):
        src = self.t.get('games') or self.t.get('census') or []
        return sorted({int(r['game']) for r in src if str(r.get('game', '')).isdigit()})


def extract(replay, out, match_id, force=False):
    """Run --extract into `out` (cached by the stamp). Returns (Extract, note); note is None unless the legacy fallback
    was used."""
    stamp = os.path.join(out, '.stamp')
    want = f'{dump_hash()} {os.path.getsize(replay)}'
    if not force and os.path.exists(stamp) and read_text(stamp).strip() == want \
            and os.path.exists(os.path.join(out, 'games.csv')):
        return Extract(out), None
    tmp = out + '.tmp'
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    why = ''
    try:
        r = run_dump(replay, '--extract', tmp, '--match', match_id)
        ok = r.returncode == 0 and os.path.exists(os.path.join(tmp, 'games.csv'))
        if not ok:
            why = ((r.stderr or '') + (r.stdout or '')).strip().splitlines()[-1:] or [f'exit {r.returncode}']
            why = why[0][:160]
    except subprocess.TimeoutExpired:
        ok, why = False, f'timeout after {TIMEOUT}s'
    if ok:
        shutil.rmtree(out, ignore_errors=True)
        os.replace(tmp, out)
        with open(stamp, 'w') as fh:
            fh.write(want + '\n')
        return Extract(out), None
    shutil.rmtree(tmp, ignore_errors=True)
    note = f'--extract failed ({why}); legacy --games and --census only'
    return legacy_extract(replay, match_id, note), note


def legacy_extract(replay, match_id, note):
    """In-memory games and census tables from the modes every reader version has (nothing is written to disk)."""
    r = run_dump(replay, '--games')
    games = []
    for line in r.stdout.splitlines():
        p = line.split()
        if len(p) == 4 and p[0].isdigit():
            games.append((int(p[0]), p[1], p[2], p[3]))
    if not games:
        raise SystemExit(f'cannot read {replay}: {(r.stderr or "").strip()[-200:]}')
    hdr = run_dump('--census-header').stdout.strip().split(',')
    census, grows = [], []
    for gi, mp, w, rounds in games:
        txt = run_dump(replay, '--game', gi, '--census', '--no-header').stdout
        teams = {}
        for line in txt.splitlines():
            if line.strip() and len(hdr) > 1:
                row = dict(zip(hdr, line.split(',')))
                row.update({'match': str(match_id), 'game': str(gi)})
                census.append(row)
                teams[row.get('side')] = row.get('team')
        for s in 'AB':
            grows.append({'match': str(match_id), 'game': str(gi), 'map': mp, 'rounds': rounds, 'side': s,
                          'team': teams.get(s, s), 'won': '1' if w == s else '0'})
    return Extract(None, {'games': grows, 'census': census}, legacy=note)


# ---------------------------------------------------------------- data dots (tele_events.jsonl)
class Dots:
    """Aggregates of one side's decoded data-dot records in one game."""

    def __init__(self):
        self.kinds, self.wells, self.roles, self.obj, self.anch = Counter(), Counter(), Counter(), Counter(), Counter()
        self.trips, self.role_mn, self.bug, self.comms = [], [], [], []
        self.bug_reason, self.fight, self.exc = Counter(), Counter(), Counter()
        self.sym_r, self.sym_conflicts, self.cntm = None, 0, {}

    def add(self, d):
        g = lambda k, dflt=0: d.get(k) if isinstance(d.get(k), (int, float)) else dflt
        k = d.get('kind')
        self.kinds[k] += 1
        if k == 'TRIP':
            cyc = g('t_deposit') - g('t_start') if g('t_deposit') and g('t_start') else None
            self.trips.append((cyc, g('wait'), g('explore'), g('flee'), g('load'), g('collect')))
        elif k == 'WELL':
            self.wells[WELL_SRC.get(g('source'), str(g('source')))] += 1
        elif k == 'ROLE':
            reason = str(d.get('reason'))
            self.roles[reason] += 1
            if reason == 'hq_stock' and g('hq_mn', -1) >= 0:
                self.role_mn.append(g('hq_mn'))
        elif k == 'OBJ':
            self.obj[OBJ_KIND.get(g('obj_kind'), str(g('obj_kind')))] += 1
        elif k == 'FIGHT':
            f = self.fight
            f['n'] += 1
            if g('tiles') > 0:
                f['scored'] += 1
                if g('threat') > g('stay_threat'):
                    f['riskier'] += 1
            if g('outnumbered'):
                f['out'] += 1
                if g('moved') and g('min_d2', 255) < 255 and g('min_d2', 255) < g('stay_min_d2', 255):
                    f['stepin_out'] += 1
            f['moved'] += 1 if g('moved') else 0
            f['fired'] += 1 if g('shots_before') + g('shots_after') > 0 else 0
            f['guard_breaks'] += 1 if g('guard_break') else 0
        elif k == 'BUG':
            self.bug.append(g('moves'))
            self.bug_reason[BUG_REASON.get(g('reason'), str(g('reason')))] += 1
        elif k == 'SYM':
            if g('conflict'):
                self.sym_conflicts += 1
            if g('cand_after') in (1, 2, 4):
                r = g('r0') or g('round')
                self.sym_r = r if self.sym_r is None else min(self.sym_r, r)
        elif k == 'CNTM':
            self.cntm[d.get('id')] = d
            dr = g('decided_round', -1)
            if dr >= 0:
                self.sym_r = dr if self.sym_r is None else min(self.sym_r, dr)
        elif k == 'COMMS':
            slots = d.get('slots') or []
            self.comms.append((g('round'), sum(1 for s in slots if s)))
        elif k == 'ANCH':
            self.anch[ANCH_EV.get(g('event'), str(g('event')))] += 1
        elif k == 'EXC':
            self.exc[f"site{g('site')}"] += 1

    def comms_at(self, r):
        best = min(self.comms, key=lambda c: (abs(c[0] - r), c[0]), default=None)
        return best[1] if best and abs(best[0] - r) <= 25 else None

    def trip(self):
        if not self.trips:
            return None
        col = lambda i: [t[i] for t in self.trips]
        return {'n': len(self.trips), 'cycle_p50': median(col(0)), 'wait_mean': rnd(mean(col(1)), 2),
                'explore_mean': rnd(mean(col(2)), 2), 'flee_mean': rnd(mean(col(3)), 2), 'load_mean': rnd(mean(col(4)), 1)}

    def fights(self):
        f = self.fight
        if not f['n']:
            return None
        n = f['n']
        return {'n': n, 'riskier_than_stay': rnd(f['riskier'] / f['scored']) if f['scored'] else None,
                'stepin_outnumbered': rnd(f['stepin_out'] / n), 'outnumbered': rnd(f['out'] / n),
                'moved': rnd(f['moved'] / n), 'fired': rnd(f['fired'] / n), 'guard_breaks': f['guard_breaks']}

    def summary(self):
        last = list(self.cntm.values())
        return {'roles': dict(self.roles), 'role_hq_mn_p50': median(self.role_mn), 'well_sources': dict(self.wells),
                'obj': dict(self.obj), 'anchor': dict(self.anch),
                'bug': {'n': len(self.bug), 'p90_moves': pctl(self.bug, 0.9), 'reasons': dict(self.bug_reason)},
                'sym_decided': self.sym_r, 'sym_conflicts': self.sym_conflicts,
                'comms_fill': {str(r): self.comms_at(r) for r in (100, 500)},
                'exc': self.kinds.get('EXC', 0), 'exc_sites': dict(self.exc), 'nm': self.kinds.get('NM', 0),
                'ovr': self.kinds.get('OVR', 0),
                'tele_max_cost': max((num(c.get('tele_max_cost')) or 0 for c in last), default=None),
                'tele_errors': sum(num(c.get('tele_errors')) or 0 for c in last),
                'tele_deferrals': sum(num(c.get('tele_deferrals')) or 0 for c in last)}


def read_dots(path, games=None):
    """{(game, side): Dots} from a tele_events.jsonl (streamed; unparseable lines are skipped)."""
    out = defaultdict(Dots)
    if not path or not os.path.exists(path):
        return {}
    with open(path) as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            gi = d.get('game')
            if games is not None and gi not in games:
                continue
            out[(gi, d.get('side'))].add(d)
    return dict(out)


# ---------------------------------------------------------------- per-game summaries (TELEMETRY.md C.4)
def state_shares(rows, side, phase):
    """{TYPE_KEY: {letter: share}} from tele_states.csv rows (turns summed by letter)."""
    acc = defaultdict(Counter)
    for r in rows or []:
        if r.get('side') == side and r.get('phase') == phase:
            acc[TYPE_KEY.get(r.get('type'), r.get('type'))][r.get('letter')] += num(r.get('turns')) or 0
    out = {}
    for t, c in acc.items():
        tot = sum(c.values())
        if tot:
            out[t] = {l: rnd(v / tot) for l, v in sorted(c.items())}
    return out


def parse_codes(s):
    out = Counter()
    for kv in (s or '').split(';'):
        if '=' in kv:
            k, v = kv.split('=', 1)
            if num(v) is not None:
                out[k.strip()] += num(v)
    return out


def eng_letters(codes):
    """Launcher codes inside engagements -> ({letter: share}, outnumbered share)."""
    tot = sum(codes.values())
    if not tot:
        return {}, None
    by = Counter()
    for k, v in codes.items():
        by[k[:1]] += v
    out = sum(v for k, v in codes.items() if k.endswith('o'))
    return {l: rnd(v / tot) for l, v in sorted(by.items())}, rnd(out / tot)


def eng_view(e, us):
    """One engagements.csv row from our side's point of view (prog 0 = our HQ)."""
    th = other(us)
    p = num(e.get('prog0'))
    res = e.get('result')
    return {'r0': num(e.get('r0')), 'r1': num(e.get('r1')), 'prog': None if p is None else (p if us == 'A' else 1 - p),
            'n_us': num(e.get('n%s0' % us)), 'n_them': num(e.get('n%s0' % th)),
            'first': 'us' if e.get('first_hit') == us else 'them' if e.get('first_hit') == th else '-',
            'dmg_us': num(e.get('dmg_by_' + us)), 'dmg_them': num(e.get('dmg_by_' + th)),
            'kills_us': num(e.get('kills_by_' + us)), 'kills_them': num(e.get('kills_by_' + th)),
            'lost_us': num(e.get('val_lost_' + us)) or 0, 'lost_them': num(e.get('val_lost_' + th)) or 0,
            'result': 'won' if res == us else 'lost' if res == th else 'draw', 'codes': e.get('codes_' + us) or ''}


def by_dn(engs, side):
    out = {str(k): [0, 0] for k in range(-3, 4)}
    for e in engs or []:
        v = eng_view(e, side)
        if v['n_us'] is None or v['n_them'] is None:
            continue
        k = str(max(-3, min(3, v['n_us'] - v['n_them'])))
        out[k][0] += 1
        out[k][1] += 1 if v['result'] == 'won' else 0
    return out


def side_summary(ex, gi, s, rounds):
    c = ex.row('census', gi, s) or {}
    g = ex.row('games', gi, s) or {}
    tl = {num(r.get('round')): r for r in ex.rows('timeline', gi, s) or []}
    out = {'team': g.get('team') or c.get('team')}
    out['built'] = {t: num(c.get('built_' + t)) for t in TYPES}
    out['died'] = {t: num(c.get('died_' + t)) for t in TYPES}
    out['coll'] = {k: num(c.get('coll_' + k)) for k in ('Ad', 'Mn', 'Ex')}
    at = {}
    for R in AT_ROUNDS:
        r = tl.get(R)
        if r is not None:
            at[str(R)] = {'C': num(r.get('alive_C')), 'L': num(r.get('alive_L')), 'Mn': num(r.get('coll_Mn')),
                          'Ad': num(r.get('coll_Ad')), 'value': num(r.get('army_value')),
                          'bank_Mn': num(r.get('bank_Mn')), 'islands': num(r.get('islands'))}
        elif R in (100, 250) and num(c.get(f'C{R}')) is not None:           # legacy census snapshot
            at[str(R)] = {'C': num(c.get(f'C{R}')), 'L': num(c.get(f'L{R}')), 'Mn': num(c.get(f'cMn{R}')),
                          'Ad': num(c.get(f'cAd{R}')), 'value': None, 'bank_Mn': None, 'islands': None}
    out['at'] = at
    if ex.col('census', 'deaths_launcher'):
        out['deaths_by_cause'] = {k: num(c.get(col)) for k, col in CAUSE_COL.items()}
    elif ex.has('deaths'):
        cnt = Counter(r.get('cause') for r in ex.rows('deaths', gi, s))
        out['deaths_by_cause'] = {k: cnt.get(k, 0) for k in CAUSES}
    else:
        out['deaths_by_cause'] = None
    for k in ('value_lost', 'dmg_hits', 'kills_hits', 'spawn_kills', 'cargo_lost_Mn', 'cargo_lost_Ad', 'anchors_lost'):
        out[k] = num(c.get(k))
    engs = ex.rows('engagements', gi)
    eng = {k: num(c.get('eng_' + k)) for k in ('n', 'won', 'lost', 'n_par', 'won_par', 'n_ahead', 'won_ahead',
                                                'n_behind', 'won_behind')}
    if eng['n'] is None and engs is not None:
        views = [eng_view(e, s) for e in engs]
        eng.update(n=len(views), won=sum(v['result'] == 'won' for v in views),
                   lost=sum(v['result'] == 'lost' for v in views))
    eng['exch'] = num(c.get('exch_ratio'))
    eng['first_hit'] = num(c.get('first_hit_rate'))
    eng['by_dn'] = by_dn(engs, s) if engs is not None else None
    out['eng'] = eng
    out['idle_funds'] = num(c.get('idle_funds'))
    out['overruns'] = num(c.get('over'))
    out['near'] = num(c.get('near'))
    out['islands_end'] = num(c.get('isl_end'))
    out['anchors_placed'] = num(c.get('anchors_placed'))
    kite = {k: num(c.get('kite_' + k)) for k in KITE}
    out['kite'] = kite if any(v is not None for v in kite.values()) else None
    out['alone20'] = num(c.get('alone20'))
    out['first_builds'] = c.get('first_builds') or None
    t2 = {k: num(c.get(k)) for k in TIER2}
    out['tier2'] = t2 if any(v is not None for v in t2.values()) else None
    hq = ex.rows('hq', gi, s)
    out['idle_bank_Mn_p50'] = rnd(median(num(r.get('bank_Mn')) for r in hq or [] if (num(r.get('idle_funds')) or 0) > 0), 1)
    out['pressure9'] = sum(num(r.get('pressure9')) or 0 for r in hq) if hq is not None else None
    out['pressure34'] = sum(num(r.get('pressure34')) or 0 for r in hq) if hq is not None else None
    return out


def tele_summary(ex, gi, s, dots, letter_mm):
    g = ex.row('games', gi, s) or {}
    c = ex.row('census', gi, s) or {}
    status = g.get('tele') or c.get('tele') or None
    ts = ex.rows('tele_states', gi)
    states = state_shares(ts, s, 'all')
    codes = Counter()
    for e in ex.rows('engagements', gi) or []:
        codes += parse_codes(e.get('codes_' + s))
    return {'status': status, 'offset': num(g.get('tele_offset', c.get('tele_offset'))),
            'sync': num(g.get('tele_sync')), 'agree': num(g.get('tele_agree', c.get('tele_agree'))),
            'exc_turns': num(g.get('tele_exc_turns', c.get('tele_exc_turns'))), 'invalid': num(g.get('tele_invalid')),
            'unknown_kinds': num(g.get('tele_unknown_kinds')), 'letter_mismatch': letter_mm,
            'states': states, 'states_by_phase': {p: state_shares(ts, s, p) for p in PHASES} if states else {},
            'carrier_mn': num(c.get('tele_carrier_mn')), 'launcher_out': num(c.get('tele_L_out')),
            'eng_codes': dict(sorted(codes.items())),
            'events': dict(sorted(dots.kinds.items())) if dots else {},
            'trip': dots.trip() if dots else None, 'fight': dots.fights() if dots else None,
            'dots': dots.summary() if dots else None}


def stall_runs(ex, gi, us):
    """[(max_still, type, id, a, b)] of our carriers and launchers still >= 30 rounds outside engagements (and, for
    carriers, outside their collecting windows)."""
    robots = ex.rows('robots', gi, us)
    if not robots:
        return []
    cover = [(num(e.get('r0')), num(e.get('r1'))) for e in ex.rows('engagements', gi) or []]
    trips = ex.rows('trips', gi, us)
    coll = defaultdict(list)
    for t in trips or []:
        a, b = num(t.get('first_collect')), num(t.get('last_collect'))
        if a is not None and b is not None:
            coll[t.get('carrier')].append((a, b))
    out = []
    for r in robots:
        ty, ms, r0 = r.get('type'), num(r.get('max_still')), num(r.get('still_r0'))
        if ty not in ('C', 'L') or ms is None or ms < 30 or r0 is None or (ty == 'C' and trips is None):
            continue
        a, b = r0, r0 + ms - 1
        win = cover + (coll.get(r.get('id'), []) if ty == 'C' else [])
        free = sum(1 for x in range(a, b + 1) if not any(lo is not None and hi is not None and lo <= x <= hi
                                                          for lo, hi in win))
        if free >= 30:
            out.append((ms, ty, r.get('id'), a, b))
    return sorted(out, key=lambda t: (-t[0], t[3]))


def float_runs(ex, gi, us):
    tl = sorted(ex.rows('timeline', gi, us) or [], key=lambda r: num(r.get('round')) or 0)
    runs, cur = [], []
    for r in tl + [None]:
        if r is not None and (num(r.get('bank_Mn')) or 0) >= 500:
            cur.append(r)
            continue
        if len(cur) >= 10:
            runs.append((min(num(x.get('bank_Mn')) for x in cur), num(cur[0].get('round')), num(cur[-1].get('round'))))
        cur = []
    return runs


def anomalies(ex, gi, us, G):
    them = other(us)
    c, ct = ex.row('census', gi, us) or {}, ex.row('census', gi, them) or {}
    t, S = G['tele'], G['us']
    out = []
    if (S['overruns'] or 0) > 0:
        out.append(f"overruns:{S['overruns']}")
    if (S['near'] or 0) > 0:
        out.append(f"near:{S['near']}")
    cnt = {}
    for kv in (c.get('counters') or '').strip(';').split(';'):
        if '=' in kv:
            cnt[kv.split('=', 1)[0]] = num(kv.split('=', 1)[1])
    self_d = (S['deaths_by_cause'] or {}).get('self') or 0
    exc = (t['exc_turns'] or 0) + (cnt.get('ex') or 0) + self_d
    if exc > 0:
        out.append(f'exc:{exc}')
    if t['agree'] is not None and 1 - t['agree'] > 0.001:
        out.append(f"bcc_disagree:{1 - t['agree']:.4f}")
    if t['status'] == 'none':
        out.append('tele_missing')
    if t['status'] in ('bcc', 'both') and t['offset'] not in (None, 0):
        out.append(f"tele_offset:{t['offset']}")
    if (t['invalid'] or 0) > 0:
        out.append(f"tele_invalid:{t['invalid']}")
    stalls = stall_runs(ex, gi, us)
    G['stalls'] = len(stalls)
    for ms, ty, rid, a, b in stalls[:3]:
        out.append(f'stall:{ty}#{rid}@r{a}-r{b}')
    for lo, a, b in float_runs(ex, gi, us):
        out.append(f'float:Mn{lo}@r{a}-r{b}')
    nhq = sum(1 for r in ex.rows('robots', gi, us) or [] if r.get('type') == 'H') \
        or len({r.get('hq_id') for r in ex.rows('hq', gi, us) or []})
    if nhq and G['rounds'] and S['idle_funds'] is not None:
        share = S['idle_funds'] / (nhq * G['rounds'])
        if share > 0.2:
            out.append(f'idle_hq:{share:.2f}')
    if (t['unknown_kinds'] or 0) > 0:
        out.append(f"unknown_kinds:{t['unknown_kinds']}")
    if (t['letter_mismatch'] or 0) > 0:
        out.append(f"letter_mismatch:{t['letter_mismatch']}")
    opp_self = (G['them']['deaths_by_cause'] or {}).get('self') or 0
    if opp_self > 0:
        out.append(f'opp_exc:{opp_self}')
    return out


def letter_mismatch(replay, gi, side):
    """letter_mismatch of one side from --tele (only meaningful where strings exist)."""
    try:
        txt = run_dump(replay, '--tele', '--game', gi, timeout=900).stdout
    except subprocess.TimeoutExpired:
        return None
    for line in txt.splitlines():
        m = re.match(rf'side {side} .*letter_mismatch=(\d+)', line)
        if m:
            return int(m.group(1))
    return None


def game_summary(ex, gi, us, rev, dots, letter_mm):
    them = other(us)
    gu, gt = ex.row('games', gi, us) or {}, ex.row('games', gi, them) or {}
    cu, ct = ex.row('census', gi, us) or {}, ex.row('census', gi, them) or {}
    rounds = num(gu.get('rounds')) or num(cu.get('rounds'))
    won = lambda gr, cr: (gr.get('won') if gr else cr.get('won')) == '1'
    res = 'win' if won(gu, cu) else 'loss' if won(gt, ct) else 'unknown'
    vtb = {}
    for R in (500, 1000, 1500):
        v = gu.get(f'vtb{R}')
        vtb[str(R)] = 'us' if v == us else 'them' if v == them else None
    engs = ex.rows('engagements', gi)
    G = {'game': gi, 'map': gu.get('map') or cu.get('map'), 'rev': rev, 'side': us, 'result': res, 'rounds': rounds,
         'win_reason': gu.get('win_reason') or cu.get('win_reason') or None, 'tb_margin': num(gu.get('tb_margin')),
         'vtb': vtb, 'turn_round': num(cu.get('turn_round')), 'lock_round': num(cu.get('lock_round')),
         'onset': {k: num(cu.get('onset_' + k)) for k in ('L', 'Mn', 'value', 'islands')},
         'first_contact': min((num(e.get('r0')) for e in engs if num(e.get('r0')) is not None), default=None)
         if engs else None,
         'us': side_summary(ex, gi, us, rounds), 'them': side_summary(ex, gi, them, rounds),
         'tele': tele_summary(ex, gi, us, dots, letter_mm)}
    G['anomalies'] = anomalies(ex, gi, us, G)
    return G


# ---------------------------------------------------------------- the report (TELEMETRY.md C.3)
def l_deaths(ex, gi, us):
    """Our launcher deaths split hit / aura / other (None without deaths.csv)."""
    rows = ex.rows('deaths', gi, us)
    if rows is None:
        return None
    L = [r.get('cause') for r in rows if r.get('type') == 'L']
    hit = sum(1 for x in L if x in ('launcher', 'throw'))
    aura = sum(1 for x in L if x == 'hq_aura')
    return hit, aura, len(L) - hit - aura


def at(S, R, k):
    return (S['at'].get(str(R)) or {}).get(k)


def summary_row(ex, G):
    us, th = G['us'], G['them']
    e = us['eng']

    def wn(n, w):
        return f'{fmt(w)}/{fmt(n)}'
    eng = '-' if e['n'] is None else (f"{fmt(e['won'])}/{fmt(e['lost'])} ({wn(e['n_par'], e['won_par'])}, "
                                      f"{wn(e['n_ahead'], e['won_ahead'])}, {wn(e['n_behind'], e['won_behind'])})")
    died = sum(v or 0 for v in us['died'].values()) if any(v is not None for v in us['died'].values()) else None
    ld = l_deaths(ex, G['game'], G['side'])
    dd = fmt(died) + (f' ({ld[0]}/{ld[1]}/{ld[2]})' if ld else '')
    kinds = Counter(a.split(':', 1)[0] for a in G['anomalies'])
    an = ' '.join(k if n == 1 else f'{k}x{n}' for k, n in kinds.items()) or '-'
    tl = f"{fmt(G['turn_round'])}/{fmt(G['lock_round'])}"
    return (f"| {G['game']} | {G['map']} | {G['side']}{'r' if G['rev'] else ''} | {G['result']} | {fmt(G['rounds'])} | "
            f"{G['win_reason'] or '-'} | {tl} | {fmt(at(us, 100, 'Mn'))}/{fmt(at(th, 100, 'Mn'))} | "
            f"{fmt(at(us, 100, 'L'))}/{fmt(at(th, 100, 'L'))} | {fmt(at(us, 250, 'L'))}/{fmt(at(th, 250, 'L'))} | "
            f"{eng} | {fmt(e['exch'])} | {dd} | {an} |")


def reason_phrase(G):
    r, res, m = G['win_reason'], G['result'], G['tb_margin']
    we = 'We won' if res == 'win' else 'We lost' if res == 'loss' else 'Result unknown'
    if r == 'conquest':
        return f"{we} by conquest at r{fmt(G['rounds'])}."
    if r == 'resign':
        return f"{we} by {'their' if res == 'win' else 'our'} resignation at r{fmt(G['rounds'])}."
    if r and r.startswith('tb_'):
        return f"{we} on the {r[3:]} tiebreak at r{fmt(G['rounds'])} (margin {fmt(m)})."
    if r == 'coin':
        return f'{we} on the coin flip (every tiebreak equal).'
    return f"{we} at r{fmt(G['rounds'])} (reason {r or 'unknown'})."


def biggest_cause(S):
    d = S['deaths_by_cause'] or {}
    k = max(d, key=lambda x: (d[x] or 0, x), default=None)
    return f'{k} {d[k]}' if k and d[k] else 'none'


def narrative(G, level):
    us, th = G['us'], G['them']
    s = [reason_phrase(G)]
    vt = G['vtb']
    if any(vt.values()):
        s[0] += ' Tiebreak standing r500/1000/1500: ' + '/'.join(vt[k] or '-' for k in ('500', '1000', '1500')) + '.'
    if level >= 3:
        return ' '.join(s)
    R = 100 if str(100) in us['at'] else max((int(k) for k in us['at']), default=None)
    if R:
        s.append(f"At r{R} we had collected Mn {fmt(at(us, R, 'Mn'))} and Ad {fmt(at(us, R, 'Ad'))} with "
                 f"{fmt(at(us, R, 'C'))} carriers alive, against Mn {fmt(at(th, R, 'Mn'))}, Ad {fmt(at(th, R, 'Ad'))} "
                 f"and {fmt(at(th, R, 'C'))}.")
    s.append(f"Launchers alive r100 {fmt(at(us, 100, 'L'))} vs {fmt(at(th, 100, 'L'))}, r250 {fmt(at(us, 250, 'L'))} "
             f"vs {fmt(at(th, 250, 'L'))}; first contact r{fmt(G['first_contact'])}.")
    if level >= 2:
        return ' '.join(s)
    s.append(f"Value lost: us {fmt(us['value_lost'])} (largest cause {biggest_cause(us)}), them "
             f"{fmt(th['value_lost'])} ({biggest_cause(th)}); islands at the end {fmt(us['islands_end'])} vs "
             f"{fmt(th['islands_end'])}.")
    return ' '.join(s)


def turning_line(ex, G):
    o = G['onset']
    s = (f"Turning point: turn r{fmt(G['turn_round'])}, lock r{fmt(G['lock_round'])}; onset L r{fmt(o['L'])}, "
         f"Mn r{fmt(o['Mn'])}, value r{fmt(o['value'])}, islands r{fmt(o['islands'])}")
    engs = ex.rows('engagements', G['game'])
    if engs is None:
        return s + f'; engagements {NA}.'
    t = G['turn_round']
    if t is None:
        return s + '.'
    near = [eng_view(e, G['side']) for e in engs]
    near = [v for v in near if v['r0'] is not None and t - 50 <= v['r0'] <= t + 10]
    if not near:
        return s + f'; no engagement in r{max(0, t - 50)}-r{t + 10}.'
    v = max(near, key=lambda v: (abs(v['lost_them'] - v['lost_us']), -v['r0']))
    return s + (f"; largest swing near it: r{v['r0']}-{v['r1']} at prog {fmt(v['prog'])}, us {fmt(v['n_us'])} vs them "
                f"{fmt(v['n_them'])}, {v['result']}, value lost {v['lost_us']}:{v['lost_them']}.")


def econ_table(G, level):
    us, th = G['us'], G['them']
    if not us['at'] and not th['at']:
        return [f'Economy and army: {NA} (no timeline).']
    rows = [R for R in TABLE_ROUNDS if str(R) in us['at']]
    if level == 1:
        rows = [R for R in rows if R in (100, 250, 500, 1000)]
    out = ['Economy and army (us/them; Mn and Ad collected, bank Mn, army value):',
           '| r | C | L | Mn | Ad | bank Mn | army | isl |', '|---|---|---|---|---|---|---|---|']
    for R in rows:
        a, b = us['at'][str(R)], th['at'].get(str(R), {})
        out.append(f'| {R} | ' + ' | '.join(f'{fmt(a.get(k))}/{fmt(b.get(k))}'
                                             for k in ('C', 'L', 'Mn', 'Ad', 'bank_Mn', 'value', 'islands')) + ' |')
    end = G.get('_end')
    if end:
        a, b = end
        out.append(f"| end {fmt(G['rounds'])} | " + ' | '.join(f'{fmt(a.get(k))}/{fmt(b.get(k))}' for k in (
            'alive_C', 'alive_L', 'coll_Mn', 'coll_Ad', 'bank_Mn', 'army_value', 'islands')) + ' |')
    return out


def engagement_lines(ex, G, level):
    engs = ex.rows('engagements', G['game'])
    if engs is None:
        return [f'Engagements: {NA} (no engagements.csv).']
    if not engs:
        return ['Engagements: none.']
    views = [eng_view(e, G['side']) for e in engs]
    k = {0: 5, 1: 3, 2: 1}.get(level, 0)
    res = Counter(v['result'] for v in views)
    dn = G['us']['eng']['by_dn'] or {}
    bucket = lambda ks: (sum(dn.get(str(x), [0, 0])[1] for x in ks), sum(dn.get(str(x), [0, 0])[0] for x in ks))
    b = [('behind', (-3, -2)), ('-1', (-1,)), ('par', (0,)), ('+1', (1,)), ('ahead', (2, 3))]
    out = [f"Engagements: {len(views)} (won {res['won']}, lost {res['lost']}, draw {res['draw']}); by dN at start "
           f"(won/n): " + ', '.join(f'{name} {bucket(ks)[0]}/{bucket(ks)[1]}' for name, ks in b) + '.']
    if k:
        top = sorted(views, key=lambda v: (-abs(v['lost_them'] - v['lost_us']), v['r0'] or 0))[:k]
        out += [f'Top {len(top)} by value swing (prog 0 = our HQ):',
                '| r0-r1 | prog | n us/them | first | dmg us/them | kills us/them | lost us/them | result | our codes |',
                '|---|---|---|---|---|---|---|---|---|']
        for v in top:
            codes = v['codes'] if len(v['codes']) <= 36 else v['codes'][:33] + '...'
            out.append(f"| {v['r0']}-{v['r1']} | {fmt(v['prog'])} | {fmt(v['n_us'])}/{fmt(v['n_them'])} | {v['first']} "
                       f"| {fmt(v['dmg_us'])}/{fmt(v['dmg_them'])} | {fmt(v['kills_us'])}/{fmt(v['kills_them'])} | "
                       f"{v['lost_us']}/{v['lost_them']} | {v['result']} | {codes or '-'} |")
    return out


def decision_lines(G, level, shadow_note=None):
    t = G['tele']
    if t['status'] in (None, 'none'):
        why = 'tele=none: this build carries no telemetry' if t['status'] == 'none' else 'no telemetry columns'
        return [f'Our decisions: {NA} ({why}).']
    out = [f"Our decisions (tele={t['status']}, offset {fmt(t['offset'])}, agree {fmt(t['agree'], 4)}):"]
    st, ph = t['states'], t['states_by_phase']
    car = '; '.join(f"{p} {shares((ph.get(p) or {}).get('C'), 5)}" for p in PHASES if (ph.get(p) or {}).get('C'))
    S = G['us']
    hq = (f"  HQ: {shares(st.get('HQ'))}; idle funds {fmt(S['idle_funds'])} HQ-rounds (bank Mn there p50 "
          f"{fmt(S['idle_bank_Mn_p50'], 1)}); pressure9 {fmt(S['pressure9'])}")
    el, out_share = eng_letters(Counter(t['eng_codes']))
    lau = (f"  Launcher: all {shares(st.get('L'))}; in engagements {shares(el)}; outnumbered at contact "
           f"{fmt(out_share)} (all F/H turns {fmt(t['launcher_out'])})")
    if st.get('A'):
        lau += f"; amp {shares(st.get('A'), 3)}"
    if level >= 2:
        out = [out[0][:-1] + f"; carrier {shares(st.get('C'), 4)}, Mn role {fmt(t['carrier_mn'])}; HQ "
               f"{shares(st.get('HQ'), 4)}; launcher {shares(st.get('L'), 4)}."]
    else:
        out += [f"  Carrier: {car or '-'}; Mn role {fmt(t['carrier_mn'])}", hq, lau]
    d = t['dots']
    if d is None:
        out.append(f"  Dots: {NA} (no data dots: indicators were off; a shadow re-run, C.7, recovers them).")
        return out
    tr, fi = t['trip'], t['fight']
    trip = (f"trips {tr['n']}, cycle p50 {fmt(tr['cycle_p50'])}, wait/trip {fmt(tr['wait_mean'])}, explore/trip "
            f"{fmt(tr['explore_mean'])}, flee/trip {fmt(tr['flee_mean'])}") if tr else 'trips none'
    fight = (f"FIGHT {fi['n']}: riskier than stay {fmt(fi['riskier_than_stay'])}, step-ins outnumbered "
             f"{fmt(fi['stepin_outnumbered'])}, outnumbered {fmt(fi['outnumbered'])}, guard breaks "
             f"{fi['guard_breaks']}") if fi else 'FIGHT none'
    if level >= 2:
        out.append(f'  Dots{shadow_note or ""}: {trip}; {fight}.')
        return out
    kv = lambda c: ' '.join(f'{k} {v}' for k, v in sorted(c.items(), key=lambda t: (-t[1], t[0]))) or '-'
    roles = d['roles']
    cf = d['comms_fill']
    out.append(f"  Dots{shadow_note or ''}: {trip}; wells {kv(d['well_sources'])}; role changes "
               f"{sum(roles.values())} ({kv(roles)}; HQ Mn at stock changes p50 {fmt(d['role_hq_mn_p50'])})")
    out.append(f"  Dots: OBJ {kv(d['obj'])}; {fight}; BUG {d['bug']['n']} (p90 moves {fmt(d['bug']['p90_moves'])}); "
               f"symmetry decided r{fmt(d['sym_decided'])}; COMMS fill r100 {fmt(cf.get('100'))}/64, r500 "
               f"{fmt(cf.get('500'))}/64; anchors {kv(d['anchor'])}; EXC {d['exc']} NM {d['nm']} OVR {d['ovr']}; "
               f"tele max cost {fmt(d['tele_max_cost'])}, deferrals {d['tele_deferrals']}")
    return out


def deaths_line(ex, G):
    def one(S):
        d = S['deaths_by_cause']
        died = ' '.join(f'{k} {v}' for k, v in S['died'].items() if v)
        if d is None:
            return f"{sum(v or 0 for v in S['died'].values())} ({died or '-'})"
        causes = ' '.join(f'{k} {v}' for k, v in d.items() if v) or 'none'
        return f"{sum(v or 0 for v in S['died'].values())} ({died or '-'}) by {causes}"
    us, th = G['us'], G['them']
    s = (f"Deaths: us {one(us)}; them {one(th)}; spawn kills us {fmt(us['spawn_kills'])} them {fmt(th['spawn_kills'])}; "
         f"cargo lost us Mn {fmt(us['cargo_lost_Mn'])} Ad {fmt(us['cargo_lost_Ad'])}; anchors lost us "
         f"{fmt(us['anchors_lost'])}")
    rows = ex.rows('deaths', G['game'], G['side'])
    last = Counter(r.get('last_token') for r in rows or [] if r.get('type') == 'L' and r.get('last_token'))
    if last:
        s += '; our launchers died in ' + ' '.join(f'{k} {v}' for k, v in last.most_common(4))
    return s + '.'


def game_section(ex, G, level, shadow_note=None):
    out = [f"## Game {G['game']}: {G['map']}, {G['result']} r{fmt(G['rounds'])} ({G['win_reason'] or '?'})"
           + (' reversed' if G['rev'] else ''),
           'What happened: ' + narrative(G, level)]
    if level <= 2:
        out.append(turning_line(ex, G))
    if level <= 1:
        out += econ_table(G, level)
    if level <= 2:
        out += engagement_lines(ex, G, level)
        out += decision_lines(G, level, shadow_note)
        out.append(deaths_line(ex, G))
    out.append('Anomalies: ' + (', '.join(G['anomalies']) or 'none') +
               (f" (stall runs: {G['stalls']})" if G.get('stalls', 0) > 3 else ''))
    return out


def tele_header(games):
    ts = [G['tele'] for G in games]
    st = Counter(t['status'] or 'unknown' for t in ts)
    if set(st) == {'none'}:
        return 'us none (this build carries no telemetry: replay-only sections)'
    status = ', '.join(f'{k} x{v}' if len(st) > 1 else k for k, v in st.items()) or 'unknown'
    mn = lambda k: min((t[k] for t in ts if t[k] is not None), default=None)
    offs = sorted({t['offset'] for t in ts if t['offset'] is not None})
    exc = sum(t['exc_turns'] or 0 for t in ts) if any(t['exc_turns'] is not None for t in ts) else None
    return (f"us {status} (sync {fmt(mn('sync'), 3)}, agree {fmt(mn('agree'), 4)}, offset "
            f"{','.join(map(str, offs)) or '-'}, exc turns {fmt(exc)})")


def render(ex, title, line, games, level, extra=()):
    out = [title,
           f"Telemetry: {tele_header(games)}  |  replay {line['replay']}  |  extract {line['extract']}"]
    out += list(extra)
    out += ['',
            '| game | map | side | result | rounds | reason | turn/lock | Mn@100 us/them | L@100 | L@250 | '
            'eng won/lost (par, ahead, behind) | exch | our deaths (L hit/aura/other) | anomalies |',
            '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    out += [summary_row(ex, G) for G in games]
    out.append('Side r = reversed game. eng: won/lost, then won/n at par (dN 0), ahead (dN >= 2), behind (dN <= -2); '
               'dN = our launchers minus theirs at the start.')
    for G in games:
        out.append('')
        out += game_section(ex, G, level, line.get('_shadow_note', {}).get(G['game']))
    return '\n'.join(out) + '\n'


def render_fit(ex, title, line, games, extra=()):
    """The most detailed report within MAX_REPORT bytes (level 0 full ... 3 headline, narrative and anomalies)."""
    for level in range(4):
        txt = render(ex, title, line, games, level, extra)
        if len(txt.encode()) <= MAX_REPORT:
            return txt, level
    return txt[:MAX_REPORT - 40].rsplit('\n', 1)[0] + '\n(truncated at 8 KB)\n', 4


# ---------------------------------------------------------------- the JSON line store (TELEMETRY.md C.4)
def read_lines(path=None):
    """{match id: last line} of progress/telemetry.jsonl."""
    path = path or p_jsonl()
    out = {}
    if os.path.exists(path):
        for l in read_text(path).splitlines():
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if isinstance(d, dict) and 'match' in d:
                out[d['match']] = d
    return out


def append_line(d, path=None):
    path = path or p_jsonl()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.write(json.dumps(d, separators=(',', ':')) + '\n')
        fcntl.flock(fh, fcntl.LOCK_UN)


def clean(G):
    return {k: v for k, v in G.items() if not k.startswith('_')}


# ---------------------------------------------------------------- shadow re-runs (TELEMETRY.md C.7)
def fingerprints(replay):
    """{game: (map, rounds, state_sha1, bytecode_sha1)} from --fingerprint."""
    out = {}
    for line in run_dump(replay, '--fingerprint').stdout.splitlines():
        p = line.split()
        if len(p) == 5 and p[0].isdigit():
            out[int(p[0])] = (p[1], p[2], p[3], p[4])
    return out


def verify_shadow(fp_rep, fp_sh):
    """Replica game -> shadow game with an identical state fingerprint (same index preferred). Returns (verified
    {i: j}, mismatched [i], bytecode_differs [i]): only verified games may borrow the shadow's dots."""
    ver, bad, bcw = {}, [], []
    for i, (mp, rounds, st, bc) in sorted(fp_rep.items()):
        cands = [j for j, f in sorted(fp_sh.items()) if f[2] == st and f[0] == mp]
        j = i if i in cands else (cands[0] if cands else None)
        if j is None or j in ver.values():
            bad.append(i)
            continue
        ver[i] = j
        if fp_sh[j][3] != bc:
            bcw.append(i)
    return ver, bad, bcw


# ---------------------------------------------------------------- commands
def participant(match, team_id=None):
    ps = match.get('participants') or []
    for p in ps:
        if (team_id is not None and p.get('team') == team_id) or (team_id is None and p.get('teamname') == TEAM):
            return p, next((q for q in ps if q is not p), {})
    return None, None


def build(replay, ex, us, rev_alt, mid, shadow=None):
    """GAME objects for every game of the extract, plus per-game shadow notes."""
    games = ex.games()
    dots = read_dots(ex.events, set(games))
    sh_dots, notes, shadow_info = {}, {}, None
    if shadow:
        ver, bad, bcw = verify_shadow(fingerprints(replay), fingerprints(shadow))
        sx, _ = extract(shadow, os.path.join(p_matches(), str(mid), 'shadow-extract'), mid)
        sd = read_dots(sx.events)
        for i, j in ver.items():
            if (j, us) in sd:
                sh_dots[i] = sd[(j, us)]
                notes[i] = f' (shadow game {j})'
        shadow_info = {'replay': rel(shadow), 'verified_games': sorted(ver), 'mismatch_games': bad,
                       'bytecode_differs': bcw}
    out = []
    for gi in games:
        d = sh_dots.get(gi) or dots.get((gi, us))
        st = (ex.row('games', gi, us) or {}).get('tele')
        lm = None
        if gi in sh_dots:
            lm = letter_mismatch(shadow, ver[gi], us)
        elif st in ('dots', 'both'):
            lm = letter_mismatch(replay, gi, us)
        G = game_summary(ex, gi, us, bool(rev_alt) and gi % 2 == 1, d, lm)
        tl = ex.rows('timeline', gi)
        if tl:
            last = max(num(r.get('round')) or 0 for r in tl)
            pick = {r.get('side'): r for r in tl if num(r.get('round')) == last}
            if us in pick and other(us) in pick:
                G['_end'] = (pick[us], pick[other(us)])
        out.append(G)
    return out, notes, shadow_info


def cmd_match(replay, match, team_id=None, shadow=None, force=False):
    mid = int(match['id'])
    mdir = os.path.join(p_matches(), str(mid))
    os.makedirs(mdir, exist_ok=True)
    with open(os.path.join(mdir, '.lock'), 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        last = read_lines().get(mid)
        report = os.path.join(p_reports(), f'{mid}.md')
        if last and last.get('v') == V and not force and \
                not (shadow and (last.get('shadow') or {}).get('replay') != rel(shadow)):
            print(f'match {mid}: already reported ({rel(report)}); --force to redo')
            return 0
        me, opp = participant(match, team_id)
        if me is None:
            raise SystemExit(f'match {mid}: {TEAM if team_id is None else team_id} is not a participant')
        us = 'A' if me.get('player_index') == 0 else 'B'
        ex, note = extract(replay, os.path.join(mdir, 'extract'), mid)     # a current stamp is reused, even on --force
        games, notes, shadow_info = build(replay, ex, us, match.get('alternate_order'), mid, shadow)
        score = [sum(G['result'] == 'win' for G in games), sum(G['result'] == 'loss' for G in games)]
        line = {'v': V, 'match': mid,
                'reported_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'created': match.get('created'), 'ranked': bool(match.get('is_ranked')), 'status': match.get('status'),
                'us': me.get('teamname'), 'submission': me.get('submission'), 'opponent': opp.get('teamname'),
                'our_label': us, 'score': score, 'replay': rel(replay), 'extract': rel(os.path.join(mdir, 'extract')),
                'report': rel(report), 'shadow': shadow_info, 'games': [clean(G) for G in games],
                'maps': match.get('maps'), 'dump': dump_hash(), 'extract_note': note}
        if last:
            line['supersedes'] = True
        created = (match.get('created') or '')[:16].replace('T', ' ')
        title = (f"# Match {mid}: {line['us']} (sub {fmt(line['submission'])}) vs {line['opponent']} - "
                 f"{score[0]}-{score[1]}   ({'ranked' if line['ranked'] else 'unranked'}, {created or '?'} UTC)")
        extra = [f'Extraction: {note}.'] if note else []
        if shadow_info:
            extra.append(f"Shadow: {shadow_info['replay']}: verified games {shadow_info['verified_games']}, mismatched "
                         f"{shadow_info['mismatch_games']}, bytecodes differ {shadow_info['bytecode_differs']}.")
        txt, level = render_fit(ex, title, dict(line, _shadow_note=notes), games, extra)
        os.makedirs(p_reports(), exist_ok=True)
        with open(report + '.tmp', 'w') as fh:
            fh.write(txt)
        os.replace(report + '.tmp', report)
        append_line(line)
        nan = sum(len(G['anomalies']) for G in games)
        print(f"report: match {mid} {score[0]}-{score[1]} vs {line['opponent']} -> {rel(report)} "
              f"(detail level {level}, {nan} anomalies)")
        return 0


def cmd_file(replay, us, label):
    """Any local replay: the report and JSON line go to matches/local/<label>.md and .json (not the progress log)."""
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', label):
        raise SystemExit('label: letters, digits, . _ - only')
    base = os.path.join(p_matches(), 'local')
    m = re.match(r'(\d+)', os.path.basename(replay))
    mid = int(m.group(1)) if m else 0
    ex, note = extract(replay, os.path.join(base, label, 'extract'), mid)
    games, _, _ = build(replay, ex, us, False, mid)
    g0 = ex.games()[0] if ex.games() else 0
    me = (ex.row('games', g0, us) or {}).get('team', us)
    opp = (ex.row('games', g0, other(us)) or {}).get('team', other(us))
    score = [sum(G['result'] == 'win' for G in games), sum(G['result'] == 'loss' for G in games)]
    line = {'v': V, 'match': mid, 'label': label,
            'reported_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'created': None, 'ranked': None, 'status': 'local', 'us': me, 'submission': None, 'opponent': opp,
            'our_label': us, 'score': score, 'replay': rel(replay), 'extract': rel(os.path.join(base, label, 'extract')),
            'report': rel(os.path.join(base, label + '.md')), 'shadow': None, 'games': [clean(G) for G in games],
            'maps': [G['map'] for G in games], 'dump': dump_hash(), 'extract_note': note}
    title = f'# Local {label}: {me} vs {opp} - {score[0]}-{score[1]}   (side {us})'
    txt, level = render_fit(ex, title, line, games, [f'Extraction: {note}.'] if note else [])
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, label + '.md'), 'w') as fh:
        fh.write(txt)
    with open(os.path.join(base, label + '.json'), 'w') as fh:
        fh.write(json.dumps(line, separators=(',', ':')) + '\n')
    print(f"report: {label} {score[0]}-{score[1]} vs {opp} -> {line['report']} (detail level {level})")
    return 0


def prune(dry=False, now=None):
    """Replays under matches/<id>/ of reported matches: kept 14 days, 30 for losses and anomaly matches (an anomaly
    other than tele_missing, which every pre-telemetry build shows). Extract directories are kept."""
    import time
    now = now or time.time()
    lines = read_lines()
    removed = []
    if not os.path.isdir(p_matches()):
        return removed
    for name in sorted(os.listdir(p_matches())):
        if not name.isdigit() or int(name) not in lines:
            continue
        L = lines[int(name)]
        gs = L.get('games') or []
        keep = 30 if any(g.get('result') == 'loss' for g in gs) or \
            any(a != 'tele_missing' for g in gs for a in g.get('anomalies') or []) else 14
        for f in (f'{name}.bc23', 'shadow.bc23'):
            p = os.path.join(p_matches(), name, f)
            if os.path.exists(p) and now - os.path.getmtime(p) > keep * 86400:
                removed.append(p)
                if not dry:
                    os.remove(p)
    for p in removed:
        print(('would remove ' if dry else 'removed ') + rel(p))
    return removed


def free_gb(path=None):
    p = path or ROOT
    while not os.path.exists(p):
        p = os.path.dirname(p)
    return shutil.disk_usage(p).free / 2 ** 30


MIN_FREE_GB = float(os.environ.get('MATCH_REPORT_MIN_FREE_GB', '2'))   # the driver's disk is shared with other projects


def cmd_sweep(pages=2, max_n=30, contest=None):
    c = contest or load_contest()
    if free_gb() < MIN_FREE_GB:
        print(f'sweep: refusing, {free_gb():.1f} GB free (< {MIN_FREE_GB:g} GB)')
        return 1
    tid = c.me()['id']
    done = read_lines()
    todo = sorted((m for m in c.matches(tid, pages) if m.get('status') == 'OK!' and m.get('id') not in done),
                  key=lambda m: m['id'])
    n = 0
    for m in todo[:max_n]:
        if free_gb() < MIN_FREE_GB:
            print(f'sweep: stopping, {free_gb():.1f} GB free (< {MIN_FREE_GB:g} GB)')
            break
        try:
            p = c.download(m, os.path.join(p_matches(), str(m['id'])))
            if p:
                cmd_match(p, m, team_id=tid)
                n += 1
        except (Exception, SystemExit) as e:
            print(f"sweep: match {m.get('id')} failed: {e}")
    prune()
    print(f'sweep: {n} reported, {max(0, len(todo) - n)} left')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('match')
    s.add_argument('replay')
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument('--match-json')
    g.add_argument('--match-id', type=int)
    s.add_argument('--team-id', type=int)
    s.add_argument('--shadow')
    s.add_argument('--force', action='store_true')
    s = sp.add_parser('sweep')
    s.add_argument('--pages', type=int, default=2)
    s.add_argument('--max', type=int, default=30)
    s = sp.add_parser('file')
    s.add_argument('replay')
    s.add_argument('--us', required=True, choices=['A', 'B'])
    s.add_argument('--label', required=True)
    s = sp.add_parser('prune')
    s.add_argument('--dry-run', action='store_true')
    sp.add_parser('field')
    a = ap.parse_args(argv)
    if a.cmd == 'match':
        if a.match_json:
            m = json.loads(read_text(a.match_json))
        else:
            c = load_contest()
            m = c.api('GET', f'/api/compete/{c.EPISODE}/match/{a.match_id}/')
        return cmd_match(a.replay, m, a.team_id, a.shadow, a.force)
    if a.cmd == 'sweep':
        return cmd_sweep(a.pages, a.max)
    if a.cmd == 'file':
        return cmd_file(a.replay, a.us, a.label)
    if a.cmd == 'prune':
        prune(a.dry_run)
        return 0
    print('field: Tier 2 (TELEMETRY.md C.1), not built yet')
    return 2


if __name__ == '__main__':
    sys.exit(main())
