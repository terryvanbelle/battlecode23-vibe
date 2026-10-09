#!/usr/bin/env python3
"""The pre-trial screen (docs/ARCHETYPES.md section 5; owner, PROMPTS 22-23): a candidate is screened locally, on the
VM, before it may use scarce replica games. tools/ladder_policy.py trial-start refuses without a passing record.

    tools/screen.py <candidate> [--incumbent PKG] [--maps M1,M2,...] [--roster a,b|none] [--no-wait] [--rerun]
                    [--allow-identity] [--keep-replays] [--min-disk-gb 2.0] [--print-job]
    tools/screen.py collect <candidate>          # resume a --no-wait screen: wait, fetch, judge, write the record
    tools/screen.py show <candidate | record>    # a record as a table
    tools/screen.py roster                       # the archetype roster: hashes, validation records, gating
    tools/screen.py gate a|b --run DIR [--team PKG]   # VM-side fail-fast checks (stdlib only): exit 0 go on, 1 stop
    tools/screen.py ingest [RUN ...]             # add runs to the cache (default: every local gauntlet run)
    tools/screen.py calibrate <record> <panel run> [--incumbent-run RUN]   # after a trial (section 5.6)

Stages (every game: seed = the map's own seed, both sides; one VM job through the standing queue, MAXJOBS=2):
  (a) basics      candidate vs examplefuncsplayer on SmallElements, Contraction, FourNations, Tightrope (8 games):
                  8/8 wins and, in the candidate's rows, over = exceptions = deaths_self = sym_wrong = 0. Stops on fail.
  (b) head-to-head candidate vs the incumbent (validated.package of progress/ladder-state.json, read only) on the 10
                  panel maps x 2 sides: s = wins + 0.5 x coin; PASS at s >= n/2 + 1 (11 of 20), BORDERLINE at
                  s >= n/2 - 1 (9), FAIL below (stops the screen).
  (c) roster      candidate vs each roster archetype on the same cells, paired with the incumbent's games on identical
                  cells (cached by code hash: progress/screens/cache.csv). Per archetype, over pairs where neither game
                  was a coin flip: gained g (candidate won, incumbent lost), lost l. REGRESSION when net <= -3 and
                  net <= -2 sqrt(g + l); pooled over the gating archetypes when Net <= -4 and Net <= -2 sqrt(G + L).
  (d) basics      every candidate game of (a)-(c): over = exceptions = deaths_self = 0.
PASS when (a), (c) and (d) pass and (b) is PASS, or (b) is BORDERLINE with pooled gating Net >= +2; else FAIL.
Unknown games (timeouts, failed instrumentation) leave a stage INCOMPLETE only when they could change its verdict.

Roster: tools/archetypes.txt ('<package> [auto|gate|info|off]' lines, '*' = every src/arch_* package; the file absent
means '*'). An archetype GATES (its regression fails the screen) when its mode is gate, or when it is auto and has a
VALID validation record for its current code hash (progress/archetypes/<name>-<hash>.json, written by
tools/archsig.py check --write); otherwise it is played and reported as information only. An archetype with the
candidate's code hash is dropped; one with the incumbent's hash is the incumbent's own style (reported, not played:
its games would repeat stage (b)).

Record: progress/screens/<candidate>-<hash>.json (a --maps subset or a --roster override writes
<candidate>-<hash>.reduced.json, which never admits a trial: the roster can block a candidate, never accept one). Exit codes: 0 PASS, 1 FAIL, 2 INCOMPLETE or error, 3 refused. Identity control: screening a
byte-identical copy of the incumbent (--allow-identity) must read s = n/2 in (b) and 0 discordant pairs everywhere."""
import argparse, csv, datetime, fcntl, glob, importlib.util, json, math, os, random, re, shutil, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO, 'tools')
SCREENS = os.path.join(REPO, 'progress', 'screens')
CACHE = os.path.join(SCREENS, 'cache.csv')
ARCH_RECORDS = os.path.join(REPO, 'progress', 'archetypes')
REGISTRY = os.path.join(TOOLS, 'archetypes')
ROSTER_FILE = os.path.join(TOOLS, 'archetypes.txt')
STATE_DIR = os.path.join(REPO, 'build', 'screens')
LADDER_STATE = os.path.join(REPO, 'progress', 'ladder-state.json')

BASICS_MAPS = ['SmallElements', 'Contraction', 'FourNations', 'Tightrope']
PANEL_MAPS = ['DefaultMap', 'Maze', 'Forest', 'ReverseFunnel', 'Cat', 'IslandHopping', 'Hah', 'BatSignal',
              'Cornucopia', 'MassiveL']
VERBS = ('collect', 'show', 'roster', 'gate', 'ingest', 'calibrate')
EXAMPLE = 'examplefuncsplayer'
SEED = 'map'
ARCH_MIN_NET, POOL_MIN_NET, SE_MULT, BORDERLINE_RESCUE = -3, -4, 2.0, 2
MIN_DISK_GB = 2.0
GAME_TIMEOUT = 1800
CACHE_HDR = ['bot', 'bot_hash', 'opp', 'opp_hash', 'map', 'side', 'seed', 'result', 'winner_side', 'rounds', 'reason',
             'over', 'exceptions', 'deaths_self', 'run', 'added']
CALIB_HDR = ['date', 'candidate', 'candidate_hash', 'incumbent_hash', 'archetype', 'archetype_hash', 'local_g', 'local_l',
             'local_share', 'replica_g', 'replica_l', 'replica_share']
# the members of each style on the replica panel (docs/ARCHETYPES.md section 1); tools/archetypes/<name>.json overrides
DEFAULT_MEMBERS = {
    'arch_swarm': ['vrangr1.AFinalsBot', 'awesomelemonade.finalBot', 'jmerle.camel_case_v30_final', 'NotLLeon.v7'],
    'arch_ampmid': ['pranayagra.finalbotfinal'],
    'arch_horde': ['georgezhang02.CB_tuning2'],
    'arch_blob': ['britacatalin.FinalBot'],
    'arch_adecon': ['battlecode-archive.Sprint1', 'reeceyang.v5anaconda', 'yaonam.PoonPoonv4'],
}
HEX12 = re.compile(r'^[0-9a-f]{12}$')
PKG = re.compile(r'^[a-z][a-z0-9_]*$')


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def rel(p):
    return os.path.relpath(p, REPO) if p and os.path.isabs(p) else p


class Refused(Exception):
    pass


# ---------------------------------------------------------------- run files (pure readers)
def read_prov(run):
    out = {}
    p = os.path.join(run, 'provenance.txt')
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if '=' in line and ' ' not in line.split('=', 1)[0]:
                k, v = line.split('=', 1)
                out.setdefault(k, v)
    return out


def outcome(r):
    """A results.csv row -> win | loss | coin | unknown | dud (from the BOT's side)."""
    res = r.get('bot_result', '')
    if res in ('win', 'loss'):
        return 'coin' if 'coin flip' in (r.get('reason') or '').lower() else res
    return res if res in ('unknown', 'dud') else 'unknown'


def read_results(run):
    """{(opponent, map, side, seed): {'result', 'winner_side', 'rounds', 'reason'}}."""
    out = {}
    p = os.path.join(run, 'results.csv')
    if not os.path.exists(p):
        return out
    for r in csv.DictReader(open(p)):
        out[(r['opponent'], r['map'], r['bot_side'], r['seed'])] = {
            'result': outcome(r), 'winner_side': r.get('winner_side', ''), 'rounds': r.get('rounds', ''),
            'reason': r.get('reason', '')}
    return out


def read_census(run):
    """{cell: (bot's row, opponent's row)} from census.csv (the BOT's row is the one on the cell's side)."""
    out = {}
    p = os.path.join(run, 'census.csv')
    if not os.path.exists(p):
        return out
    by = {}
    for r in csv.DictReader(open(p)):
        by.setdefault((r['cell_opponent'], r['cell_map'], r['cell_side'], r['cell_seed']), []).append(r)
    for k, rs in by.items():
        ours = [r for r in rs if r.get('side') == k[2]]
        theirs = [r for r in rs if r.get('side') != k[2]]
        out[k] = (ours[0] if ours else None, theirs[0] if theirs else None)
    return out


def counters(row):
    out = {}
    for kv in (row.get('counters') or '').strip(';').split(';'):
        if '=' in kv:
            k, v = kv.split('=', 1)
            try:
                out[k] = int(v)
            except ValueError:
                pass
    return out


def _int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def game_basics(row):
    """One team's census row -> {over, exceptions, deaths_self, sym_wrong, near, strings}. Exceptions = robots destroyed
    by an uncaught exception (census `exceptions`) + caught ones (the bot's counter `ex` when its indicator strings are
    present, else `tele_exc_turns` from the bytecode channel)."""
    c = counters(row)
    strings = 'ex' in c
    caught = c['ex'] if strings else (_int(row.get('tele_exc_turns')) if row.get('tele') == 'bcc' else 0)
    return {'over': _int(row.get('over')), 'exceptions': _int(row.get('exceptions')) + caught,
            'deaths_self': _int(row.get('deaths_self')), 'sym_wrong': _int(row.get('sym_wrong')) if strings else 0,
            'near': c.get('nm', 0), 'strings': strings}


def sum_basics(rows):
    tot = {'over': 0, 'exceptions': 0, 'deaths_self': 0, 'sym_wrong': 0, 'near': 0, 'no_census': 0}
    for r in rows:
        if r is None:
            tot['no_census'] += 1
            continue
        b = game_basics(r)
        for k in ('over', 'exceptions', 'deaths_self', 'sym_wrong', 'near'):
            tot[k] += _int(b.get(k))
    return tot


# ---------------------------------------------------------------- judging (pure, tested)
def h2h_bars(n):
    """(pass_at, borderline_at): 11 and 9 of 20 games, n/2 + 1 and n/2 - 1 in general."""
    return n / 2 + 1, n / 2 - 1


def h2h_level(s, n):
    p, b = h2h_bars(n)
    return 'PASS' if s >= p else 'BORDERLINE' if s >= b else 'FAIL'


def judge_basics(outcomes, basics, n_cells):
    """Stage (a). outcomes: list of win|loss|coin|unknown|dud|missing (one per cell); basics: sum_basics of the
    candidate's rows."""
    wins = sum(o == 'win' for o in outcomes)
    bad_games = sum(o in ('loss', 'coin') for o in outcomes)
    unknown = n_cells - wins - bad_games
    bars = {k: basics.get(k, 0) for k in ('over', 'exceptions', 'deaths_self', 'sym_wrong')}
    failed = [f'{k} = {v}' for k, v in bars.items() if v]
    if bad_games:
        failed.insert(0, f'{bad_games} of {n_cells} games not won')
    verdict = 'FAIL' if failed else ('INCOMPLETE' if unknown else 'PASS')
    d = {'verdict': verdict, 'games': n_cells, 'wins': wins, 'unknown': unknown}
    d.update(bars)
    d['near'] = basics.get('near', 0)
    if basics.get('no_census'):
        d['no_census'] = basics['no_census']
    if failed:
        d['failed'] = failed
    return d


def judge_h2h(outcomes, n_cells):
    """Stage (b): the verdict holds only if it is the same whichever way the unknown games would have gone."""
    wins = sum(o == 'win' for o in outcomes)
    coin = sum(o == 'coin' for o in outcomes)
    losses = sum(o == 'loss' for o in outcomes)
    unknown = n_cells - wins - coin - losses
    s = wins + 0.5 * coin
    lo, hi = h2h_level(s, n_cells), h2h_level(s + unknown, n_cells)
    p, b = h2h_bars(n_cells)
    return {'verdict': lo if lo == hi else 'INCOMPLETE', 'games': n_cells, 'wins': wins, 'losses': losses, 'coin': coin,
            'unknown': unknown, 'score': s, 'pass_at': p, 'borderline_at': b}


def pair_counts(pairs):
    """pairs: [(candidate outcome, incumbent outcome)] on identical cells. Pairs with a coin flip are excluded;
    pairs with an unknown or missing game are counted as `missing`."""
    c = {'cells': len(pairs), 'g': 0, 'l': 0, 'both_won': 0, 'both_lost': 0, 'coin': 0, 'missing': 0,
         'candidate_wins': 0, 'candidate_decided': 0, 'incumbent_wins': 0, 'incumbent_decided': 0}
    for cand, inc in pairs:
        c['candidate_wins'] += cand == 'win'
        c['candidate_decided'] += cand in ('win', 'loss')
        c['incumbent_wins'] += inc == 'win'
        c['incumbent_decided'] += inc in ('win', 'loss')
        if 'coin' in (cand, inc):
            c['coin'] += 1
        elif cand not in ('win', 'loss') or inc not in ('win', 'loss'):
            c['missing'] += 1
        elif cand == inc:
            c['both_won' if cand == 'win' else 'both_lost'] += 1
        elif cand == 'win':
            c['g'] += 1
        else:
            c['l'] += 1
    return c


def is_regression(net, discordant, min_net):
    return net <= min_net and net <= -SE_MULT * math.sqrt(discordant)


def regression_verdict(g, l, missing, min_net):
    """REGRESSION | ok | incomplete (ok now, but the missing pairs, all lost, would make it a regression)."""
    if is_regression(g - l, g + l, min_net):
        return 'REGRESSION'
    if missing and is_regression(g - l - missing, g + l + missing, min_net):
        return 'incomplete'
    return 'ok'


def censoring(c):
    if not c['incumbent_decided']:
        return None
    if c['incumbent_wins'] == 0:
        return 'censored-low'
    if c['incumbent_wins'] == c['incumbent_decided']:
        return 'censored-high'
    return None


def judge_roster(archs):
    """Stage (c). archs: [{'name', 'gating', 'pairs': [(cand, inc)], ...}] -> stage dict (entries get counts)."""
    out = []
    G = L = M = 0
    iG = iL = 0
    for a in archs:
        c = pair_counts(a['pairs'])
        e = {k: v for k, v in a.items() if k != 'pairs'}
        e.update({k: c[k] for k in ('cells', 'incumbent_wins', 'candidate_wins', 'candidate_decided', 'g', 'l',
                                    'both_won', 'both_lost', 'coin', 'missing')})
        e['net'] = c['g'] - c['l']
        e['censored'] = censoring(c)
        e['verdict'] = regression_verdict(c['g'], c['l'], c['missing'], ARCH_MIN_NET)
        if a.get('gating'):
            G, L, M = G + c['g'], L + c['l'], M + c['missing']
        else:
            iG, iL = iG + c['g'], iL + c['l']
        out.append(e)
    pooled = {'g': G, 'l': L, 'net': G - L, 'se': round(math.sqrt(G + L), 2), 'missing': M,
              'verdict': regression_verdict(G, L, M, POOL_MIN_NET)}
    gating = [e for e in out if e.get('gating')]
    failed = [f'{e["name"]}: net {e["net"]:+d} (g {e["g"]}, l {e["l"]})' for e in gating if e['verdict'] == 'REGRESSION']
    if pooled['verdict'] == 'REGRESSION':
        failed.append(f'pooled: Net {pooled["net"]:+d} (G {G}, L {L})')
    incomplete = [e['name'] for e in gating if e['verdict'] == 'incomplete'] + \
        (['pooled'] if pooled['verdict'] == 'incomplete' else [])
    verdict = 'FAIL' if failed else ('INCOMPLETE' if incomplete else 'PASS')
    d = {'verdict': verdict, 'pooled': pooled,
         'info_pooled': {'g': iG, 'l': iL, 'net': iG - iL, 'se': round(math.sqrt(iG + iL), 2)},
         'archetypes': out}
    if not gating:
        d['note'] = 'no gating archetype (no VALID record for a current hash): stage (c) passes by default'
    if failed:
        d['failed'] = failed
    if incomplete:
        d['incomplete'] = incomplete
    return d


def judge_final_basics(basics, games):
    bars = {k: basics.get(k, 0) for k in ('over', 'exceptions', 'deaths_self')}
    d = {'verdict': 'FAIL' if any(bars.values()) else 'PASS', 'games': games}
    d.update(bars)
    d['sym_wrong'] = basics.get('sym_wrong', 0)
    d['near'] = basics.get('near', 0)
    if basics.get('no_census'):
        d['no_census'] = basics['no_census']
    return d


def overall(stages):
    """(verdict, reasons) from the stage dicts (None = not run)."""
    reasons = []
    for k, name in (('a', 'basics'), ('b', 'head-to-head'), ('c', 'roster'), ('d', 'basics over the screen')):
        s = stages.get(k)
        if s and s['verdict'] == 'FAIL':
            why = '; '.join(s.get('failed', [])) or (f'score {s["score"]} of {s["games"]} < {s["borderline_at"]}'
                                                       if k == 'b' else '')
            reasons.append(f'({k}) {name} FAIL' + (f': {why}' if why else ''))
    if reasons:
        return 'FAIL', reasons
    missing = [k for k in 'abcd' if not stages.get(k) or stages[k]['verdict'] == 'INCOMPLETE']
    if missing:
        return 'INCOMPLETE', [f'({k}) incomplete' + (f': {stages[k].get("why")}' if stages.get(k) and
                                                       stages[k].get('why') else '') for k in missing]
    b = stages['b']
    if b['verdict'] == 'PASS':
        return 'PASS', []
    net = stages['c']['pooled']['net']
    if net >= BORDERLINE_RESCUE:
        return 'PASS', [f'(b) BORDERLINE ({b["score"]} of {b["games"]}) rescued by pooled roster Net {net:+d}']
    return 'FAIL', [f'(b) BORDERLINE ({b["score"]} of {b["games"]}) without a pooled roster gain '
                    f'(Net {net:+d} < +{BORDERLINE_RESCUE})']


EXIT = {'PASS': 0, 'FAIL': 1, 'INCOMPLETE': 2}


# ---------------------------------------------------------------- the cache (progress/screens/cache.csv)
def cache_key(row):
    return (row['bot_hash'], row['opp_hash'], row['map'], row['side'], row['seed'])


_ELOLIB = []


def reason_code(text):
    try:
        if not _ELOLIB:
            _ELOLIB.append(_load('elolib'))
        return _ELOLIB[0].reason_code(text)
    except Exception:
        return (text or '')[:20].replace(',', ';')


def run_cache_rows(run, now=None):
    """Cache rows for one gauntlet run: (rows, why-not). Two rows per decided game, one from each team's side, when
    both teams are our packages with recorded code hashes and the seeds are not random. Coin flips, unknown and dud
    games are never cached."""
    prov = read_prov(run)
    if not os.path.exists(os.path.join(run, 'summary.txt')):
        return [], 'unfinished (no summary.txt)'
    if prov.get('seed_mode') not in ('map', 'cells'):
        return [], f'seed_mode {prov.get("seed_mode") or "not recorded"}'
    bot, bh = prov.get('bot'), prov.get('bot_hash', '')
    if not HEX12.match(bh or ''):
        return [], f'bot_hash {bh or "missing"}'
    res = read_results(run)
    cen = read_census(run)
    now = now or utcnow()
    rows = []
    for (opp, mp, side, seed), r in sorted(res.items()):
        oh = prov.get(f'opp_hash.{opp}', '')
        if not HEX12.match(oh) or r['result'] not in ('win', 'loss') or not (seed == 'map' or seed.isdigit()):
            continue
        ours, theirs = cen.get((opp, mp, side, seed), (None, None))
        for team, th, other, oth, s, won, crow in ((bot, bh, opp, oh, side, r['result'] == 'win', ours),
                                                   (opp, oh, bot, bh, 'B' if side == 'A' else 'A',
                                                    r['result'] != 'win', theirs)):
            b = game_basics(crow) if crow else {}
            rows.append({'bot': team, 'bot_hash': th, 'opp': other, 'opp_hash': oth, 'map': mp, 'side': s,
                         'seed': seed, 'result': 'win' if won else 'loss', 'winner_side': r['winner_side'],
                         'rounds': r['rounds'], 'reason': reason_code(r['reason']),
                         'over': b.get('over', ''), 'exceptions': b.get('exceptions', ''),
                         'deaths_self': b.get('deaths_self', ''), 'run': rel(run), 'added': now})
    return rows, None


def load_cache(path=CACHE):
    """(index {key: row}, conflicts {key: [results]}): a key seen with two different results is a determinism
    failure and is never used."""
    idx, seen, conflicts = {}, {}, {}
    if not os.path.exists(path):
        return idx, conflicts
    for r in csv.DictReader(open(path)):
        k = cache_key(r)
        seen.setdefault(k, set()).add((r['result'], r['winner_side']))
        idx.setdefault(k, r)
    for k, v in seen.items():
        if len(v) > 1:
            conflicts[k] = sorted(v)
            idx.pop(k, None)
    return idx, conflicts


def ingest(runs, path=CACHE, quiet=False):
    """Append the cache rows of runs not yet ingested (file-locked). Returns (added rows, skipped runs, conflicts)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lock = os.path.join(STATE_DIR, 'cache.lock') if path == CACHE else path + '.lock'   # build/ is not committed
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    with open(lock, 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        done = set()
        if os.path.exists(path):
            done = {r['run'] for r in csv.DictReader(open(path))}
        new, skipped = [], []
        for run in runs:
            if rel(os.path.abspath(run)) in done:
                continue
            rows, why = run_cache_rows(os.path.abspath(run))
            if why:
                skipped.append((rel(os.path.abspath(run)), why))
            new += rows
        if new:
            fresh = not os.path.exists(path) or os.path.getsize(path) == 0
            with open(path, 'a', newline='') as fh:
                w = csv.DictWriter(fh, fieldnames=CACHE_HDR, lineterminator='\n')
                if fresh:
                    w.writeheader()
                w.writerows(new)
    _, conflicts = load_cache(path)
    if conflicts and not quiet:
        for k, v in sorted(conflicts.items()):
            print(f'!! determinism failure in the cache, key {k}: {v} (key not used)', file=sys.stderr)
    return new, skipped, conflicts


def local_runs():
    return sorted(d for d in glob.glob(os.path.join(REPO, 'gauntlet', '*')) if os.path.isdir(d)
                  and os.path.exists(os.path.join(d, 'results.csv')))


# ---------------------------------------------------------------- packages and the roster
def bot_hash(pkg):
    if not pkg or not PKG.match(pkg) or not os.path.isdir(os.path.join(REPO, 'src', pkg)):
        return None
    r = subprocess.run(['bash', os.path.join(TOOLS, 'bot-hash.sh'), pkg], capture_output=True, text=True)
    h = r.stdout.strip()
    return h if r.returncode == 0 and HEX12.match(h) else None


def arch_packages():
    return sorted(os.path.basename(d) for d in glob.glob(os.path.join(REPO, 'src', 'arch_*')) if os.path.isdir(d))


def parse_roster_file(text, packages):
    """'<package> [auto|gate|info|off]' lines ('#' comments); '*' stands for every package in `packages` not listed by
    name. Returns [(name, mode)] without the 'off' entries, named entries first, then '*' in sorted order."""
    named, star = [], None
    for line in (text if text is not None else '*').splitlines():
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        p = line.split()
        mode = p[1] if len(p) > 1 else 'auto'
        if mode not in ('auto', 'gate', 'info', 'off'):
            raise ValueError(f'roster: unknown mode {mode!r} in {line!r}')
        if p[0] == '*':
            star = mode
        elif not PKG.match(p[0]):
            raise ValueError(f'roster: bad package name {p[0]!r}')
        elif p[0] not in [n for n, _ in named]:
            named.append((p[0], mode))
    names = {n for n, _ in named}
    out = list(named) + ([(n, star) for n in sorted(packages) if n not in names] if star else [])
    return [(n, m) for n, m in out if m != 'off']


def validation_record(name, h):
    """The archetype's validation record for this code hash: (path or None, VALID?)."""
    p = os.path.join(ARCH_RECORDS, f'{name}-{h}.json')
    if not h or not os.path.exists(p):
        return None, False
    try:
        r = json.load(open(p))
    except (OSError, ValueError):
        return rel(p), False
    return rel(p), r.get('verdict') == 'VALID' and not r.get('quick') and r.get('hash', h) == h


def registry(name):
    p = os.path.join(REGISTRY, f'{name}.json')
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return {}


def gating_of(mode, valid, reg_gate):
    if mode == 'gate':
        return True, 'gate (tools/archetypes.txt)'
    if mode == 'info':
        return False, 'info (tools/archetypes.txt)'
    if reg_gate is False:
        return False, 'registry: gate false'
    if valid:
        return True, 'VALID record for this hash'
    return False, 'no VALID record for this hash: information only'


def resolve_roster(override=None, roster_file=ROSTER_FILE, hashes=None):
    """[{name, hash, mode, gating, why, record}] for every roster package that exists."""
    if override is not None:
        entries = [] if override in ('', 'none') else [(n.strip(), 'auto') for n in override.split(',') if n.strip()]
        source = '--roster'
    else:
        text = open(roster_file).read() if os.path.exists(roster_file) else None
        entries = parse_roster_file(text, arch_packages())
        source = rel(roster_file) if text is not None else 'src/arch_* (no tools/archetypes.txt)'
    out = []
    for name, mode in entries:
        h = (hashes or {}).get(name) if hashes is not None else bot_hash(name)
        if not h:
            out.append({'name': name, 'hash': None, 'mode': mode, 'gating': False, 'why': 'no such package',
                        'record': None, 'missing': True})
            continue
        rec, valid = validation_record(name, h)
        g, why = gating_of(mode, valid, registry(name).get('gate'))
        out.append({'name': name, 'hash': h, 'mode': mode, 'gating': g, 'why': why, 'record': rec})
    return out, source


def compile_check(pkgs, outdir):
    """{package: (compiles, error tail)}: one javac over every package (they are independent), then one per package
    only when that fails, to name the culprit (javac starts slowly on the driver)."""
    def javac(ps):
        shutil.rmtree(outdir, ignore_errors=True)
        os.makedirs(outdir, exist_ok=True)
        files = [f for p in ps for f in sorted(glob.glob(os.path.join(REPO, 'src', p, '*.java')))]
        script = (f'source {TOOLS}/lib.sh && javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none '
                  f'-d "$OUT" -cp "$(engine_cp)" "$@"')
        r = subprocess.run(['bash', '-c', script, 'javac'] + files, capture_output=True, text=True,
                           env=dict(os.environ, OUT=outdir))
        return r.returncode == 0 and bool(files), (r.stderr or r.stdout or 'no sources')[-1500:]
    ok, err = javac(pkgs)
    out = {p: (True, '') for p in pkgs} if ok else {p: javac([p]) for p in pkgs}
    shutil.rmtree(outdir, ignore_errors=True)
    return out


# ---------------------------------------------------------------- cells and the job script
def cells_for(opp, maps):
    return [(opp, m, s, SEED) for m in maps for s in ('A', 'B')]


def cells_text(cells):
    return ''.join(f'{o} {m} {s} {sd}\n' for o, m, s, sd in cells)


def heredoc(path, cells):
    body = cells_text(cells)
    return f"cat > {path} <<'EOF_CELLS'\n{body}EOF_CELLS\n"


def build_job(st):
    """The VM job (bash, run by tools/vm-queue.sh from the repo root). Stages a and b stop the screen on a definitive
    failure; the incumbent's missing roster cells run before the candidate's (stage c). Every archetype is compiled on
    its own: one that does not compile is excluded, not fatal. If an archetype's compiled hash differs from the one
    expected when the screen was queued, all its incumbent cells are played (the cache has none for the new code)."""
    cand, inc, tag = st['candidate'], st['incumbent'], st['tag']
    D = f'build/{tag}-cells'
    keep = st.get('keep_replays')
    L = [f'# tools/screen.py job: {cand} ({st["candidate_hash"]}) vs incumbent {inc} ({st["incumbent_hash"]}); '
         f'created {st["created"]}',
         'set -u',
         f'export MAXJOBS=2 CENSUS=1 SEED_MODE=map GAME_TIMEOUT={st.get("game_timeout", GAME_TIMEOUT)} '
         f'CLASSES="$PWD/build/{tag}"',
         f'D={D}; rm -rf "$D" "$CLASSES"; mkdir -p "$D"',
         'end () { rm -rf "$CLASSES" "$D"; echo "SCREEN-END $1"; exit 0; }',
         'hash_of () { awk -v p="$1" \'$1 == p {print $2; exit}\' "$CLASSES/.hashes" 2>/dev/null; }',
         'run_of () { ls -d gauntlet/*-"$1" 2>/dev/null | tail -1; }',
         ('prune () { :; }' if keep else 'prune () { [ -n "$1" ] && rm -rf "$1/replays"; }   # replays: rerun the cell'),
         heredoc('"$D/a.txt"', cells_for(EXAMPLE, st['basics_maps'])).rstrip('\n'),
         heredoc('"$D/b.txt"', cells_for(inc, st['maps'])).rstrip('\n')]
    for a in st['roster']:
        x = a['name']
        L.append(heredoc(f'"$D/all-{x}.txt"', cells_for(x, st['maps'])).rstrip('\n'))
        L.append(heredoc(f'"$D/cached-{x}.txt"', [tuple(c) for c in a.get('inc_cached', [])]).rstrip('\n'))
    L += ['echo "SCREEN compile $(date -u +%FT%TZ)"',
          f'HASHES=1 bash tools/build.sh {cand} {inc} {EXAMPLE} || end compile-failed']
    for a in st['roster']:
        x = a['name']
        L.append(f'HASHES=1 bash tools/build.sh {x} || {{ echo "SCREEN-EXCLUDE {x} compile-failed"; '
                 f'rm -rf "$CLASSES/{x}"; }}')
    L += ['cat "$CLASSES/.hashes"',
          'echo "SCREEN stage a $(date -u +%FT%TZ)"',
          f'BOT={cand} TAG={tag}-a CELLS="$D/a.txt" SKIP_COMPILE=1 bash tools/gauntlet.sh',
          f'R=$(run_of {tag}-a); [ -n "$R" ] || end no-run-a',
          f'python3 tools/screen.py gate a --run "$R" --team {cand} || ' +
          ('echo "SCREEN-GATE a would stop (--no-stop)"' if st.get('no_stop') else 'end stop-a'),
          'prune "$R"',
          'echo "SCREEN stage b $(date -u +%FT%TZ)"',
          f'BOT={cand} TAG={tag}-b CELLS="$D/b.txt" SKIP_COMPILE=1 bash tools/gauntlet.sh',
          f'R=$(run_of {tag}-b); [ -n "$R" ] || end no-run-b',
          f'python3 tools/screen.py gate b --run "$R" --team {cand} || ' +
          ('echo "SCREEN-GATE b would stop (--no-stop)"' if st.get('no_stop') else 'end stop-b'),
          'prune "$R"',
          ': > "$D/inc.txt"; : > "$D/c.txt"']
    for a in st['roster']:
        x = a['name']
        L.append(f'if [ -d "$CLASSES/{x}" ]; then\n'
                 f'  if [ "$(hash_of {x})" = "{a["hash"]}" ]; then grep -vxF -f "$D/cached-{x}.txt" "$D/all-{x}.txt" '
                 f'>> "$D/inc.txt"\n'
                 f'  else echo "SCREEN-CHANGED {x} expected {a["hash"]} compiled $(hash_of {x})"; '
                 f'cat "$D/all-{x}.txt" >> "$D/inc.txt"; fi\n'
                 f'  cat "$D/all-{x}.txt" >> "$D/c.txt"\n'
                 f'fi')
    L += ['echo "SCREEN incumbent cells $(grep -c . "$D/inc.txt") $(date -u +%FT%TZ)"',
          f'if [ -s "$D/inc.txt" ]; then BOT={inc} TAG={tag}-inc CELLS="$D/inc.txt" SKIP_COMPILE=1 bash tools/gauntlet.sh;'
          f' prune "$(run_of {tag}-inc)"; fi',
          'echo "SCREEN stage c $(grep -c . "$D/c.txt") $(date -u +%FT%TZ)"',
          f'if [ -s "$D/c.txt" ]; then BOT={cand} TAG={tag}-c CELLS="$D/c.txt" SKIP_COMPILE=1 bash tools/gauntlet.sh;'
          f' prune "$(run_of {tag}-c)"; fi',
          'end done']
    return '\n'.join(L) + '\n'


# ---------------------------------------------------------------- the judge (driver side, after the job)
def job_markers(log):
    m = {'end': None, 'excluded': {}, 'changed': {}}
    for line in (log or '').splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == 'SCREEN-END' and len(p) > 1:
            m['end'] = p[1]
        elif p[0] == 'SCREEN-EXCLUDE' and len(p) > 2:
            m['excluded'][p[1]] = p[2]
        elif p[0] == 'SCREEN-CHANGED' and len(p) > 5:
            m['changed'][p[1]] = p[5]
    return m


def check_prov(run, bot_h, opp_h):
    """[] when the run's recorded hashes equal the expected ones, else the differences."""
    prov = read_prov(run)
    bad = []
    if prov.get('bot_hash') != bot_h:
        bad.append(f'bot_hash {prov.get("bot_hash")} != {bot_h}')
    for o, h in (opp_h or {}).items():
        if prov.get(f'opp_hash.{o}') != h:
            bad.append(f'opp_hash.{o} {prov.get(f"opp_hash.{o}")} != {h}')
    return bad


def judge(st, runs, markers, cache_path=CACHE):
    """Every stage from the fetched runs ({'a'|'b'|'inc'|'c': run dir or None}) and the job log markers. Returns the
    record (without file names of the state)."""
    cand, inc, ch, ih = st['candidate'], st['incumbent'], st['candidate_hash'], st['incumbent_hash']
    stages = {}
    cand_rows = []

    def outcomes(run, opp, maps):
        res = read_results(run) if run else {}
        cen = read_census(run) if run else {}
        cells = cells_for(opp, maps)
        return [res.get(c, {}).get('result', 'missing') for c in cells], [cen.get(c, (None, None))[0] for c in cells
                                                                          if c in res]

    # (a)
    ra = runs.get('a')
    if not ra:
        stages['a'] = {'verdict': 'INCOMPLETE', 'why': f'no stage (a) run (job end: {markers.get("end")})'}
    else:
        bad = check_prov(ra, ch, {EXAMPLE: st['example_hash']})
        outs, rows = outcomes(ra, EXAMPLE, st['basics_maps'])
        cand_rows += rows
        stages['a'] = judge_basics(outs, sum_basics(rows), len(outs))
        stages['a']['run'] = rel(ra)
        if bad:
            stages['a'].update({'verdict': 'INCOMPLETE', 'why': 'provenance: ' + '; '.join(bad)})
    # (b)
    rb = runs.get('b')
    if not rb:
        if markers.get('end') != 'stop-a':
            stages['b'] = {'verdict': 'INCOMPLETE', 'why': f'no stage (b) run (job end: {markers.get("end")})'}
    else:
        bad = check_prov(rb, ch, {inc: ih})
        outs, rows = outcomes(rb, inc, st['maps'])
        cand_rows += rows
        stages['b'] = judge_h2h(outs, len(outs))
        stages['b']['run'] = rel(rb)
        if bad:
            stages['b'].update({'verdict': 'INCOMPLETE', 'why': 'provenance: ' + '; '.join(bad)})
    stopped = markers.get('end') in ('stop-a', 'stop-b')
    # (c)
    if not stopped:
        idx, conflicts = load_cache(cache_path)
        rc, ri = runs.get('c'), runs.get('inc')
        prov_c = read_prov(rc) if rc else {}
        bad_c = check_prov(rc, ch, {}) if rc else []
        bad_i = check_prov(ri, ih, {}) if ri else []
        res_c = read_results(rc) if rc else {}
        cen_c = read_census(rc) if rc else {}
        archs, excluded = [], list(st.get('excluded', []))
        for a in st['roster']:
            x = a['name']
            if x in markers.get('excluded', {}):
                excluded.append({'name': x, 'reason': f'did not compile on the VM ({markers["excluded"][x]})'})
                continue
            played = prov_c.get(f'opp_hash.{x}') or markers.get('changed', {}).get(x) or a['hash']
            entry = {'name': x, 'hash': played, 'mode': a['mode'], 'gating': a['gating'], 'why': a['why'],
                     'record': a.get('record')}
            if played != a['hash']:
                rec, valid = validation_record(x, played)
                entry['record'] = rec
                entry['note'] = f'code changed after the screen was queued: expected {a["hash"]}, played {played}'
                if a['gating'] and not (valid and a['mode'] == 'auto'):
                    excluded.append({'name': x, 'reason': f'hash on the VM ({played}) differed from the validated '
                                                          f'hash ({a["hash"]})'})
                    continue
                entry['gating'], entry['why'] = gating_of(a['mode'], valid, registry(x).get('gate'))
            if played == ih:
                entry['own_style'] = True
                entry['gating'] = False
                entry['why'] = "incumbent's own style (same code hash): never gates"
            pairs = []
            for c in cells_for(x, st['maps']):
                co = res_c.get(c, {}).get('result', 'missing')
                key = (ih, played, c[1], c[2], c[3])
                if key in conflicts:
                    io = 'missing'
                else:
                    io = idx.get(key, {}).get('result', 'missing')
                pairs.append((co, io))
                if c in res_c:
                    cand_rows.append(cen_c.get(c, (None, None))[0])
            entry['pairs'] = pairs
            archs.append(entry)
        stages['c'] = judge_roster(archs)
        stages['c']['excluded'] = excluded
        stages['c']['runs'] = [rel(rc)] if rc else []
        stages['c']['incumbent_runs'] = [rel(ri)] if ri else []
        if bad_c or bad_i:
            stages['c'].update({'verdict': 'INCOMPLETE', 'why': 'provenance: ' + '; '.join(bad_c + bad_i)})
        elif st['roster'] and not rc and markers.get('end') != 'done':
            stages['c'].update({'verdict': 'INCOMPLETE', 'why': f'no stage (c) run (job end: {markers.get("end")})'})
    # (d)
    if stages.get('a') and stages['a'].get('run'):
        stages['d'] = judge_final_basics(sum_basics(cand_rows), len(cand_rows))
    verdict, reasons = overall(stages)
    return stages, verdict, reasons


def is_reduced(maps, roster_override):
    """A screen on a map subset, or with a --roster override (which could drop a gating archetype), never admits a
    trial: its record is <candidate>-<hash>.reduced.json."""
    return list(maps) != PANEL_MAPS or roster_override is not None


def record_path(cand, h, reduced):
    return os.path.join(SCREENS, f'{cand}-{h}' + ('.reduced' if reduced else '') + '.json')


def make_record(st, stages, verdict, reasons):
    rec = {'v': 1, 'candidate': st['candidate'], 'candidate_hash': st['candidate_hash'],
           'incumbent': st['incumbent'], 'incumbent_hash': st['incumbent_hash'],
           'created': st['created'], 'finished': utcnow(), 'job': st.get('job'), 'seed_mode': 'map',
           'maps': {'basics': st['basics_maps'], 'panel': st['maps']}, 'reduced': st['reduced'],
           'roster_source': st.get('roster_source'), 'no_stop': st.get('no_stop', False), 'stages': stages,
           'verdict': verdict, 'reasons': reasons}
    if st.get('identity'):
        rec['identity'] = True
        b, c = stages.get('b'), stages.get('c')
        ok = bool(b and c and b.get('score') == b.get('games', 0) / 2 and
                  all(e['g'] == 0 and e['l'] == 0 and e['missing'] == 0 for e in c.get('archetypes', [])))
        rec['identity_control'] = 'ok' if ok else ('DEFECT: an identical build must read s = n/2 and 0 discordant '
                                                   'pairs, with no missing pair (a determinism failure in the cache '
                                                   'shows as missing)')
    return rec


# ---------------------------------------------------------------- printing
def summary(rec):
    st = rec['stages']
    L = [f'screen {rec["candidate"]} ({rec["candidate_hash"]}) vs incumbent {rec["incumbent"]} ({rec["incumbent_hash"]})'
         + (' [REDUCED (map subset or roster override): never admits a trial]' if rec.get('reduced') else ''),
         f'maps: {", ".join(rec["maps"]["panel"])}']
    a = st.get('a')
    if a:
        L.append(f'(a) basics       {a["verdict"]:10s} {a.get("wins", "?")}/{a.get("games", "?")} wins vs {EXAMPLE}; '
                 f'over {a.get("over", "?")}, exceptions {a.get("exceptions", "?")}, deaths_self '
                 f'{a.get("deaths_self", "?")}, sym_wrong {a.get("sym_wrong", "?")}, near {a.get("near", "?")}'
                 + (f'  [{a["why"]}]' if a.get('why') else ''))
    b = st.get('b')
    if b:
        L.append(f'(b) head-to-head {b["verdict"]:10s} s = {b.get("score")} of {b.get("games")} (wins {b.get("wins")}, '
                 f'losses {b.get("losses")}, coin {b.get("coin")}, unknown {b.get("unknown")}); PASS at '
                 f'{b.get("pass_at")}, BORDERLINE at {b.get("borderline_at")}' + (f'  [{b["why"]}]' if b.get('why') else ''))
    c = st.get('c')
    if c:
        p = c['pooled']
        L.append(f'(c) roster       {c["verdict"]:10s} pooled gating Net {p["net"]:+d} (G {p["g"]}, L {p["l"]}, SE '
                 f'{p["se"]}); information-only archetypes Net {c["info_pooled"]["net"]:+d}'
                 + (f'  [{c["why"]}]' if c.get('why') else '') + (f'  ({c["note"]})' if c.get('note') else ''))
        L.append(f'    {"archetype":12s} {"hash":12s} {"gates":5s} {"inc":>4s} {"cand":>4s} {"g":>3s} {"l":>3s} '
                 f'{"net":>4s} {"bothW":>5s} {"bothL":>5s} {"coin":>4s} {"miss":>4s}  verdict / flags')
        for e in c['archetypes']:
            flags = [f for f in (e.get('censored'), 'own style' if e.get('own_style') else None) if f]
            L.append(f'    {e["name"]:12s} {e["hash"] or "?":12s} {"yes" if e.get("gating") else "no":5s} '
                     f'{e["incumbent_wins"]:>4d} {e["candidate_wins"]:>4d} {e["g"]:>3d} {e["l"]:>3d} {e["net"]:>+4d} '
                     f'{e["both_won"]:>5d} {e["both_lost"]:>5d} {e["coin"]:>4d} {e["missing"]:>4d}  {e["verdict"]}'
                     + (f' ({", ".join(flags)})' if flags else '') + (f' - {e["note"]}' if e.get('note') else ''))
        for x in c.get('excluded', []):
            L.append(f'    excluded {x["name"]}: {x["reason"]}')
    d = st.get('d')
    if d:
        L.append(f'(d) basics all   {d["verdict"]:10s} {d["games"]} candidate games: over {d["over"]}, exceptions '
                 f'{d["exceptions"]}, deaths_self {d["deaths_self"]} (sym_wrong {d.get("sym_wrong")}, near '
                 f'{d.get("near")}' + (f', no census {d["no_census"]}' if d.get('no_census') else '') + ')')
    L.append(f'VERDICT {rec["verdict"]}' + (': ' + '; '.join(rec['reasons']) if rec.get('reasons') else ''))
    if rec.get('identity'):
        L.append(f'identity control: {rec.get("identity_control")}')
    return '\n'.join(L)


# ---------------------------------------------------------------- commands
def state_path(cand, h):
    return os.path.join(STATE_DIR, f'{cand}-{h}.state.json')


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w') as fh:
        json.dump(obj, fh, indent=1)
        fh.write('\n')
    os.replace(tmp, path)


def incumbent_package():
    try:
        return (json.load(open(LADDER_STATE)).get('validated') or {}).get('package')
    except (OSError, ValueError):
        return None


def prepare(a, vmjobs=None):
    """Every refusal check and the job state; raises Refused. Pure apart from hashing, compiling and the VM disk."""
    cand = a.candidate
    if cand in VERBS or not PKG.match(cand or ''):
        raise Refused(f'{cand!r} is not a package name (reserved words: {", ".join(VERBS)})')
    if not os.path.isdir(os.path.join(REPO, 'src', cand)):
        raise Refused(f'no src/{cand}')
    inc = a.incumbent or incumbent_package()
    if not inc or not os.path.isdir(os.path.join(REPO, 'src', inc)):
        raise Refused(f'no incumbent package ({inc!r}): pass --incumbent PKG')
    if inc == cand:
        raise Refused('the candidate and the incumbent are the same package')
    ch, ih, eh = bot_hash(cand), bot_hash(inc), bot_hash(EXAMPLE)
    if not (ch and ih and eh):
        raise Refused(f'cannot hash the packages ({cand} {ch}, {inc} {ih}, {EXAMPLE} {eh})')
    identity = ch == ih
    if identity and not a.allow_identity:
        raise Refused(f'{cand} has the incumbent\'s code hash {ch}: nothing to screen (--allow-identity for the '
                      f'identity control)')
    maps = [m.strip() for m in a.maps.split(',')] if a.maps else list(PANEL_MAPS)
    with open(os.path.join(TOOLS, 'maps.txt')) as fh:
        known = set(fh.read().split())
    if not maps or any(m not in known for m in maps) or len(set(maps)) != len(maps):
        raise Refused(f'--maps must name distinct maps of tools/maps.txt: {maps}')
    reduced = is_reduced(maps, getattr(a, 'roster', None))
    rp = record_path(cand, ch, reduced)
    if os.path.exists(rp) and not a.rerun:
        with open(rp) as fh:
            old = json.load(fh)
        if old.get('incumbent_hash') == ih and old.get('finished'):
            raise Refused(f'a finished record exists ({rel(rp)}), verdict {old.get("verdict")}; --rerun to screen '
                          f'again\n' + summary(old))
    sp = state_path(cand, ch)
    if os.path.exists(sp) and not a.rerun:
        old = json.load(open(sp))
        if not old.get('finished') and vmjobs and vmjobs.status(old['job']) in ('pending', 'running'):
            raise Refused(f'screen job {old["job"]} is still {vmjobs.status(old["job"])}: tools/screen.py collect '
                          f'{cand} (or --rerun)')
    roster, source = resolve_roster(a.roster)
    excluded = []
    kept = []
    for e in roster:
        if e.get('missing'):
            excluded.append({'name': e['name'], 'reason': 'no such package'})
        elif e['hash'] == ch:
            excluded.append({'name': e['name'], 'reason': "the candidate's own code hash"})
        elif e['hash'] == ih:
            excluded.append({'name': e['name'], 'own_style': True,
                             'reason': "the incumbent's own style (the incumbent's code hash): its games would repeat "
                                       "stage (b)"})
        else:
            kept.append(e)
    # compile check on the driver before anything is queued (the candidate refuses; an archetype is excluded)
    comp = compile_check([cand] + [e['name'] for e in kept], os.path.join(REPO, 'build', 'screen-check'))
    if not comp[cand][0]:
        raise Refused(f'src/{cand} does not compile:\n{comp[cand][1]}')
    roster = []
    for e in kept:
        if comp[e['name']][0]:
            roster.append(e)
        else:
            excluded.append({'name': e['name'], 'reason': 'does not compile on the driver'})
    if vmjobs is not None and a.min_disk_gb > 0 and not getattr(a, 'print_job', False):
        free = vmjobs.free_disk_gb()
        if free < a.min_disk_gb:
            raise Refused(f'the VM has {free:.2f} GB free (< {a.min_disk_gb}): prune gauntlet/ replays first')
    # the incumbent's cached roster cells
    ingest(local_runs(), quiet=True)
    idx, _ = load_cache()
    for e in roster:
        e['inc_cached'] = [list(c) for c in cells_for(e['name'], maps) if (ih, e['hash'], c[1], c[2], c[3]) in idx]
    tag = f'scr-{ch}-{random.Random().randrange(16 ** 4):04x}'
    return {'v': 1, 'candidate': cand, 'candidate_hash': ch, 'incumbent': inc, 'incumbent_hash': ih,
            'example_hash': eh, 'identity': identity, 'maps': maps, 'basics_maps': list(BASICS_MAPS),
            'reduced': reduced, 'roster': roster, 'roster_source': source, 'excluded': excluded, 'tag': tag,
            'created': utcnow(), 'keep_replays': bool(a.keep_replays), 'game_timeout': GAME_TIMEOUT,
            'no_stop': bool(getattr(a, 'no_stop', False))}


def volume(st):
    n = len(st['maps']) * 2
    k = len(st['roster'])
    inc = sum(n - len(e['inc_cached']) for e in st['roster'])
    return 2 * len(st['basics_maps']) + n + n * k, inc


def collect(st, vmjobs, poll=60):
    job = st['job']
    s = vmjobs.status(job)
    if s in ('pending', 'running'):
        print(f'waiting for {job} ({s}); polling every {poll} s', flush=True)
        s = vmjobs.wait(job, poll=poll)
    log = vmjobs.job_log(job) if s == 'done' else ''
    markers = job_markers(log)
    runs = {}
    for k in ('a', 'b', 'inc', 'c'):
        found = vmjobs.find_runs(f'{st["tag"]}-{k}')
        runs[k] = vmjobs.fetch(found[-1]) if found else None
    fetched = [r for r in runs.values() if r]
    ingest(fetched)
    if s != 'done':
        stages, verdict, reasons = {}, 'INCOMPLETE', [f'job {job} is {s}']
    else:
        stages, verdict, reasons = judge(st, runs, markers)
        if markers['end'] is None:
            verdict, reasons = 'INCOMPLETE', reasons + ['the job log has no SCREEN-END line (the job died)']
    rec = make_record(st, stages, verdict, reasons)
    path = record_path(st['candidate'], st['candidate_hash'], st['reduced'])
    save_json(path, rec)
    st['finished'] = rec['finished']
    st['record'] = rel(path)
    save_json(state_path(st['candidate'], st['candidate_hash']), st)
    print(summary(rec))
    print(f'wrote {rel(path)}; cache {rel(CACHE)} (the coordinator commits both)')
    return EXIT.get(verdict, 2)


def cmd_screen(a):
    vmjobs = _load('vmjobs')
    try:
        st = prepare(a, vmjobs)
    except Refused as e:
        print(f'screen refused: {e}', file=sys.stderr)
        return 3
    job_script = build_job(st)
    cand_games, inc_games = volume(st)
    print(f'screen {st["candidate"]} ({st["candidate_hash"]}) vs {st["incumbent"]} ({st["incumbent_hash"]}); roster '
          f'({st["roster_source"]}): ' + (', '.join(f'{e["name"]} {e["hash"]} {"GATES" if e["gating"] else "info"}'
                                                    for e in st['roster']) or 'empty')
          + (f'; excluded: {", ".join(x["name"] + " (" + x["reason"] + ")" for x in st["excluded"])}'
             if st['excluded'] else ''))
    print(f'games: candidate {cand_games}, incumbent {inc_games} (cached {sum(len(e["inc_cached"]) for e in st["roster"])})')
    if a.print_job:
        print(job_script)
        return 0
    st['job'] = vmjobs.enqueue(f'scr-{st["candidate"]}-{st["candidate_hash"]}', job_script)
    save_json(state_path(st['candidate'], st['candidate_hash']), st)
    print(f'queued {st["job"]}; state {rel(state_path(st["candidate"], st["candidate_hash"]))}')
    if a.no_wait:
        print(f'resume with: tools/screen.py collect {st["candidate"]}')
        return 2
    return collect(st, vmjobs)


def find_state(cand):
    h = bot_hash(cand)
    p = state_path(cand, h) if h else None
    if p and os.path.exists(p):
        return p
    alt = sorted(glob.glob(os.path.join(STATE_DIR, f'{cand}-*.state.json')), key=os.path.getmtime)
    return alt[-1] if alt else None


def cmd_collect(a):
    p = find_state(a.candidate)
    if not p:
        print(f'no screen state for {a.candidate} under {rel(STATE_DIR)}', file=sys.stderr)
        return 2
    return collect(json.load(open(p)), _load('vmjobs'), poll=a.poll)


def find_record(arg):
    if os.path.exists(arg):
        return arg
    h = bot_hash(arg)
    for p in ([record_path(arg, h, False), record_path(arg, h, True)] if h else []):
        if os.path.exists(p):
            return p
    alt = sorted(glob.glob(os.path.join(SCREENS, f'{arg}-*.json')), key=os.path.getmtime)
    return alt[-1] if alt else None


def cmd_show(a):
    p = find_record(a.target)
    if not p:
        print(f'no screen record for {a.target}', file=sys.stderr)
        return 2
    rec = json.load(open(p))
    print(summary(rec))
    print(f'({rel(p)})')
    return EXIT.get(rec.get('verdict'), 2)


def cmd_roster(a):
    roster, source = resolve_roster(a.roster)
    inc = incumbent_package()
    ih = bot_hash(inc)
    print(f'roster from {source}; incumbent {inc} ({ih})')
    for e in roster:
        own = e['hash'] and e['hash'] == ih
        print(f'  {e["name"]:14s} {e["hash"] or "-":12s} mode {e["mode"]:5s} '
              f'{"own" if own else "GATES" if e["gating"] else "info ":5s}  '
              + ("the incumbent's own style: not played (its games are stage b)" if own else e['why'])
              + (f'  record {e["record"]}' if e.get('record') else ''))
    return 0


def gate_eval(stage, run):
    """(go_on, summary dict) for the VM-side fail-fast checks."""
    res = read_results(run)
    cen = read_census(run)
    outs = [v['result'] for v in res.values()]
    if stage == 'a':
        d = judge_basics(outs, sum_basics([cen.get(c, (None, None))[0] for c in res]), len(outs))
        return d['verdict'] == 'PASS', d
    d = judge_h2h(outs, len(outs))
    return d['verdict'] != 'FAIL', d


def cmd_gate(a):
    go, d = gate_eval(a.stage, a.run)
    print(f'gate {a.stage}: {"go on" if go else "STOP"} {json.dumps(d)}')
    return 0 if go else 1


def cmd_ingest(a):
    runs = a.runs or local_runs()
    new, skipped, conflicts = ingest(runs)
    print(f'cache {rel(CACHE)}: {len(new)} rows added from {len(runs)} runs; {len(skipped)} runs not cacheable; '
          f'{len(conflicts)} conflicting keys')
    if a.verbose:
        for r, why in skipped:
            print(f'  skipped {r}: {why}')
    return 1 if conflicts else 0


def panel_pairs(cand_run, inc_run, members):
    """Replica pairs against a style's members: (g, l, candidate wins, decided) over identical panel cells."""
    def load(run):
        out = {}
        for r in csv.DictReader(open(os.path.join(run, 'results.csv'))):
            out[(r['opponent'], r['map'], r['bot_side'], r['seed'])] = outcome(r)
        return out
    c, i = load(cand_run), load(inc_run)
    g = l = wins = dec = 0
    for k, co in c.items():
        if k[0] not in members:
            continue
        if co in ('win', 'loss'):
            dec += 1
            wins += co == 'win'
        io = i.get(k)
        if co in ('win', 'loss') and io in ('win', 'loss') and co != io:
            g += co == 'win'
            l += co == 'loss'
    return g, l, wins, dec


def suspect(prev, cur):
    """docs/ARCHETYPES.md 5.6: opposite signs of local and replica net (both |net| >= 2) on two consecutive trials, or
    a share gap above 0.30 now."""
    def opp(r):
        ln, rn = int(r['local_g']) - int(r['local_l']), int(r['replica_g']) - int(r['replica_l'])
        return abs(ln) >= 2 and abs(rn) >= 2 and (ln > 0) != (rn > 0)
    gap = cur['local_share'] != '' and cur['replica_share'] != '' and \
        abs(float(cur['local_share']) - float(cur['replica_share'])) > 0.30
    return gap or bool(prev and opp(prev) and opp(cur))


def cmd_calibrate(a):
    rec = json.load(open(find_record(a.record) or a.record))
    inc_run = a.incumbent_run
    if not inc_run:
        try:
            v = json.load(open(LADDER_STATE)).get('validated') or {}
        except (OSError, ValueError):
            v = {}
        if v.get('package') == rec['incumbent'] and v.get('panel_run'):
            inc_run = os.path.join(REPO, v['panel_run'])
    if not inc_run:
        print('the incumbent\'s panel run is unknown: --incumbent-run gauntlet/<run>', file=sys.stderr)
        return 2
    path = os.path.join(ARCH_RECORDS, 'calibration.csv')
    old = list(csv.DictReader(open(path))) if os.path.exists(path) else []
    rows = []
    for e in rec['stages'].get('c', {}).get('archetypes', []):
        members = registry(e['name']).get('members') or DEFAULT_MEMBERS.get(e['name'])
        if not members:
            print(f'  {e["name"]}: no members known; skipped')
            continue
        g, l, wins, dec = panel_pairs(a.panel_run, inc_run, set(members))
        # the candidate's share over ITS decided games: candidate_wins also counts wins whose paired incumbent game
        # was a coin flip or missing, so cells - coin - missing is the wrong denominator (it can exceed 1)
        ldec = e.get('candidate_decided', e['cells'] - e['coin'] - e['missing'])
        row = {'date': utcnow(), 'candidate': rec['candidate'], 'candidate_hash': rec['candidate_hash'],
               'incumbent_hash': rec['incumbent_hash'], 'archetype': e['name'], 'archetype_hash': e['hash'],
               'local_g': e['g'], 'local_l': e['l'],
               'local_share': f'{e["candidate_wins"] / ldec:.3f}' if ldec else '',
               'replica_g': g, 'replica_l': l, 'replica_share': f'{wins / dec:.3f}' if dec else ''}
        prev = [r for r in old if r['archetype'] == e['name']]
        flag = suspect(prev[-1] if prev else None, {k: str(v) for k, v in row.items()})
        rows.append(row)
        print(f'  {e["name"]:12s} local g {e["g"]} l {e["l"]} share {row["local_share"] or "-"}   replica g {g} l {l} '
              f'share {row["replica_share"] or "-"}' + ('   SUSPECT: revalidate before it gates again' if flag else ''))
    os.makedirs(ARCH_RECORDS, exist_ok=True)
    fresh = not os.path.exists(path)
    with open(path, 'a', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=CALIB_HDR, lineterminator='\n')
        if fresh:
            w.writeheader()
        w.writerows(rows)
    print(f'appended {len(rows)} rows to {rel(path)}')
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in VERBS:
        ap = argparse.ArgumentParser(prog='screen.py ' + argv[0])
        v = argv.pop(0)
        if v == 'collect':
            ap.add_argument('candidate'); ap.add_argument('--poll', type=int, default=60)
            return cmd_collect(ap.parse_args(argv))
        if v == 'show':
            ap.add_argument('target')
            return cmd_show(ap.parse_args(argv))
        if v == 'roster':
            ap.add_argument('--roster')
            return cmd_roster(ap.parse_args(argv))
        if v == 'gate':
            ap.add_argument('stage', choices=['a', 'b']); ap.add_argument('--run', required=True)
            ap.add_argument('--team')
            return cmd_gate(ap.parse_args(argv))
        if v == 'ingest':
            ap.add_argument('runs', nargs='*'); ap.add_argument('-v', '--verbose', action='store_true')
            return cmd_ingest(ap.parse_args(argv))
        if v == 'calibrate':
            ap.add_argument('record'); ap.add_argument('panel_run'); ap.add_argument('--incumbent-run')
            return cmd_calibrate(ap.parse_args(argv))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('candidate')
    ap.add_argument('--incumbent')
    ap.add_argument('--maps', help='comma-separated subset of the panel maps (a reduced screen never admits a trial)')
    ap.add_argument('--roster', help="comma-separated archetype packages, or 'none' (default: tools/archetypes.txt); "
                                     "an override makes the record reduced (it never admits a trial)")
    ap.add_argument('--no-wait', action='store_true')
    ap.add_argument('--rerun', action='store_true')
    ap.add_argument('--allow-identity', action='store_true')
    ap.add_argument('--keep-replays', action='store_true')
    ap.add_argument('--no-stop', action='store_true',
                    help='play every stage even after (a) or (b) fails (backtests, dry runs; the verdict is unchanged)')
    ap.add_argument('--min-disk-gb', type=float, default=MIN_DISK_GB)
    ap.add_argument('--print-job', action='store_true', help='print the VM job script and exit (nothing is queued)')
    return cmd_screen(ap.parse_args(argv))


if __name__ == '__main__':
    sys.exit(main())
