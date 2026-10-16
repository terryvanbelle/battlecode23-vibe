#!/usr/bin/env python3
"""When to play ranked and when to play unranked on the galaxy replica (owner, PROMPTS 17-18; docs/LADDER_STRATEGY.md).

Unranked games are for learning (fixed opponent, maps and order: the only controlled experiment); ranked games are for
rating (galaxy seeds tournaments by it), and only a validated build banks rating. Every match plays the submission
that is active when the match is CREATED, so a candidate on trial is exposed to autoscrims and incoming challenges.

States (progress/ladder-state.json):
  VALIDATED  the active submission is the validated build. Ranked challenges upward (galaxy allows no other):
             BURST (one per 5 min) while our rated matches are few (< 30: the displayed rating still carries a large
             volume penalty, 1500*0.85^n) or the build was validated in the last 24 h (likely underrated);
             MAINTAIN (one per 30 min) otherwise. Never while 2 or more of our matches wait in the queue.
  TRIAL      a candidate is active: no ranked challenges, incoming ranked requests auto-rejected, the candidate plays
             the unranked panel; then trial-end --accept (it becomes the validated build) or --reject (the
             validated build is resubmitted at once). A trial starts only if it can end before the next autoscrim,
             and only for a candidate that passed the pre-trial screen (tools/screen.py; docs/ARCHETYPES.md
             section 5): a PASS record in progress/screens/ for the candidate's code hash against the validated
             build's code hash. --skip-screen "<reason>" overrides (the reason is kept in the history); --force
             overrides only the autoscrim window.
  PARKED     (s['parked'], a list) a trial whose panel matches all exist. Galaxy fixed their submission when it
             created them, so trial-park puts the validated build back at once while the panel waits in the shared
             queue (after an autoscrim, for hours): incoming ranked is accepted again and another trial may start
             (the ranked loop still waits while the panel's matches fill the queue). The trial-start process keeps
             running and records the panel run on the parked entry; then trial-decide <package> --reject drops it, or
             --accept resubmits the package (unchanged code) and makes that new submission the validated build.

    tools/ladder_policy.py status
    tools/ladder_policy.py init <submission id> <package>      # declare the validated build (once)
    tools/ladder_policy.py trial-start <package> [--panel test/cells/panel-v1.txt] [--tag T] [--force]
                                            [--skip-screen "<reason>"]
    tools/ladder_policy.py trial-end --accept | --reject
    tools/ladder_policy.py trial-park                           # once every panel match exists (waits up to 20 min)
    tools/ladder_policy.py trial-decide <package | trial submission id> --accept | --reject
    tools/ladder_policy.py ranked                               # the ranked loop (run detached)
"""
import argparse, contextlib, datetime, fcntl, glob, importlib.util, json, os, random, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, 'progress', 'ladder-state.json')
SCREENS = os.path.join(REPO, 'progress', 'screens')
LOCK = os.path.join(REPO, 'build', 'ladder-state.lock')     # state_lock (build/ is not tracked)
_spec = importlib.util.spec_from_file_location('contest', os.path.join(REPO, 'tools', 'contest.py'))
contest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(contest)
E = contest.EPISODE

BURST_EVERY, MAINTAIN_EVERY = 300, 1800        # seconds between our ranked requests
YOUNG_N = 30                                    # rated matches until the volume penalty is small (1500*0.85^30 = 11)
FRESH_HOURS = 24                                # a newly validated build is likely underrated for this long
ACCEPT_NEXT = ('next (owner, PROMPTS 119): tools/progress-refresh.sh, then commit and push progress/ and '
               'research/matches/ (not while tools/unit-tests.sh runs)')
MAX_WAITING = 2                                 # our matches waiting in the queue: above this, no new ranked request
TRIAL_HOURS = 2.5                               # a panel trial must fit before the next autoscrim
BAND = 3                                        # challenge one of the BAND teams rated closest at or above us
PARK_TIMEOUT, PARK_POLL = 20 * 60, 30           # trial-park: wait this long (s) for the panel's matches, polling
PARK_PAGES = 10                                 # pages of our match list trial-park reads (newest first)
GAIN_K = 24                                     # siarnaq: a ranked match moves the mean by K (S - E)
BT_REFRESH = 3600                               # seconds between refits of the Bradley-Terry model (a fit takes ~20 s)
MIN_GAIN = 0.0                                  # challenge only a team whose expected gain exceeds this


# ---------------------------------------------------------------- pure policy (tested)
def next_cron(expr, now):
    """Next fire time of a galaxy autoscrim cron of the form 'M */N * * *' or 'M H * * *' (UTC); None if unknown."""
    try:
        m, h = expr.split()[:2]
        minute = int(m)
    except (ValueError, AttributeError):
        return None
    if h.startswith('*/'):
        step = int(h[2:])
        hours = list(range(0, 24, step))
    elif h.isdigit():
        hours = [int(h)]
    else:
        return None
    day = now.replace(minute=0, second=0, microsecond=0)
    for d in range(2):
        for hh in hours:
            t = (day + datetime.timedelta(days=d)).replace(hour=hh, minute=minute)
            if t > now:
                return t
    return None


def ranked_mode(n_rated, validated_since, now):
    """'BURST' while ratings are young or the build is freshly validated, else 'MAINTAIN'."""
    if n_rated < YOUNG_N:
        return 'BURST'
    if validated_since and now - validated_since < datetime.timedelta(hours=FRESH_HOURS):
        return 'BURST'
    return 'MAINTAIN'


def may_challenge(state, active_submission, waiting, last_request, mode, now):
    """(ok, reason) for one ranked request now."""
    if state.get('trial'):
        return False, 'trial in progress'
    v = state.get('validated') or {}
    if active_submission != v.get('submission'):
        return False, f'active submission {active_submission} is not the validated build {v.get("submission")}'
    if waiting >= MAX_WAITING:
        return False, f'{waiting} of our matches already wait'
    every = BURST_EVERY if mode == 'BURST' else MAINTAIN_EVERY
    if last_request and (now - last_request).total_seconds() < every:
        return False, 'interval'
    return True, mode


def trial_window_ok(next_autoscrim, now, hours=TRIAL_HOURS):
    return next_autoscrim is None or next_autoscrim - now >= datetime.timedelta(hours=hours)


def screen_check(screens_dir, cand_hash, inc_hash):
    """(ok, path, reason): progress/screens/ holds a pre-trial screen record (tools/screen.py) for this candidate code
    hash, against this incumbent code hash, with verdict PASS and the full map set. Found by hash, never by name."""
    if not cand_hash or not inc_hash:
        return False, None, f'unknown code hash (candidate {cand_hash}, incumbent {inc_hash})'
    why = f'no screen record for code hash {cand_hash}'
    for p in sorted(glob.glob(os.path.join(screens_dir, f'*-{cand_hash}.json'))):
        try:
            with open(p) as fh:
                rec = json.load(fh)
        except (OSError, ValueError):
            why = f'{os.path.basename(p)} is unreadable'
            continue
        if rec.get('candidate_hash') != cand_hash:
            continue
        if rec.get('incumbent_hash') != inc_hash:
            why = f'{os.path.basename(p)} screened against incumbent {rec.get("incumbent_hash")}, not {inc_hash}'
        elif rec.get('reduced'):
            why = f'{os.path.basename(p)} is a reduced screen'
        elif rec.get('verdict') != 'PASS':
            why = f'{os.path.basename(p)} verdict {rec.get("verdict")}: ' + '; '.join(rec.get('reasons') or [])
        else:
            return True, p, 'PASS'
    return False, None, why


def bot_hash(package):
    """tools/bot-hash.sh <package>, or None when src/<package> does not exist."""
    if not package or not os.path.isdir(os.path.join(REPO, 'src', package)):
        return None
    r = subprocess.run(['bash', os.path.join(REPO, 'tools', 'bot-hash.sh'), package], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def panel_created(cells, ms, tid, sub):
    """For each panel cell (opponent, maps, order), the id of a distinct match of ours that answers it and is played by
    submission `sub` (any status: created is enough, as the submission is fixed then), or None while none exists. Our
    participant row must name `sub` (no fallback when the row has no submission: parking on a guess would let the
    validated build replace the candidate before the panel's matches are fixed)."""
    used, out = set(), []
    for opp, maps, _ in cells:
        req = {'opponent': opp, 'maps': maps, 'submission': sub}
        m = next((m for m in ms if m['id'] not in used and contest.our_submission(m, tid) == sub
                  and contest.answers(m, req, tid, 0)), None)
        if m is not None:
            used.add(m['id'])
        out.append(m and m['id'])
    return out


def find_parked(s, key):
    """The parked trial named by its package or its trial submission id; SystemExit when none or several match."""
    ps = [p for p in s.get('parked') or [] if p.get('package') == key or str(p.get('submission')) == str(key)]
    if not ps:
        have = ', '.join(f'{p.get("package")} ({p.get("submission")})' for p in s.get('parked') or []) or 'none'
        raise SystemExit(f'no parked trial {key} (parked: {have})')
    if len(ps) > 1:
        raise SystemExit(f'{len(ps)} parked trials of {key} (submissions {[p.get("submission") for p in ps]}): '
                         f'name one by its submission id')
    return ps[0]


def panel_run(p):
    """A parked trial's finished panel run (relative to REPO): the run its trial-start process recorded, else its run
    directory once results.csv exists there (block writes it last, e.g. after a RESUME); None while it plays."""
    if p.get('run'):
        return p['run']
    rd = p.get('run_dir')
    if rd and os.path.exists(os.path.join(REPO, rd, 'results.csv')):
        return rd
    return None


def pdt(iso):
    """An ISO time as PDT for the owner (owner, PROMPTS 28)."""
    from zoneinfo import ZoneInfo
    t = parse_t(iso)
    return t.astimezone(ZoneInfo('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M %Z') if t else '?'


# ---------------------------------------------------------------- state and galaxy facts
def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {'validated': None, 'trial': None, 'history': []}


def save_state(s):
    tmp = f'{STATE}.{os.getpid()}.tmp'          # one per process: two writers never share a temporary file
    with open(tmp, 'w') as fh:
        json.dump(s, fh, indent=1)
        fh.write('\n')
    os.replace(tmp, STATE)


@contextlib.contextmanager
def state_lock():
    """Hold the state's lock (flock on build/ladder-state.lock) through one read-modify-write. Several processes
    write the state: each trial-start process (when its trial starts, and hours later when its panel ends), trial-park,
    trial-decide, trial-end and init; without the lock, the later of two overlapping writes drops the other's. The
    commands that change the active submission hold it from their checks to their state write, compile wait included.
    Ranked requests hold it from their eligibility checks through the POST too, so a trial cannot activate a candidate
    between the active-submission check and match creation. Not reentrant."""
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    fd = os.open(LOCK, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(time.strftime('%H:%M:%S'), 'waiting for the ladder-state lock (another ladder_policy command)',
                  flush=True)
            fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def parse_t(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00')) if s else None


def active_submission():
    """Galaxy's active submission: our most recent accepted one."""
    subs = contest.pages(f'/api/compete/{E}/submission/', limit=2)
    acc = [x for x in subs if x.get('accepted')]
    return max(acc, key=lambda x: x['id']) if acc else None


def our_matches(tid, pages=5):
    return contest.matches(tid, limit_pages=pages)


def n_rated(ms):
    return sum(1 for m in ms if m.get('is_ranked') and m.get('status') == 'OK!')


def waiting(ms):
    return sum(1 for m in ms if m.get('status') in ('NEW', 'QUE', 'RUN', 'TRY'))


# The episode API does not publish the autoscrim schedule (staff-only, as in the contest): a contestant learns it by
# watching when autoscrim matches appear. Ours is every 8 hours: 00:00, 08:00, 16:00 UTC = 17:00, 01:00, 09:00 PDT.
AUTOSCRIM_CRON = os.environ.get('AUTOSCRIM_CRON', '0 */8 * * *')


def next_autoscrim(now):
    return next_cron(AUTOSCRIM_CRON, now)


# ---------------------------------------------------------------- commands
def cmd_status():
    s = load_state()
    team = contest.me()
    ms = our_matches(team['id'])
    sub = active_submission()
    now = utcnow()
    nxt = next_autoscrim(now)
    v = s.get('validated') or {}
    print(f'team {team["name"]} rating {(team.get("profile") or {}).get("rating")}  rated matches {n_rated(ms)}  waiting {waiting(ms)}')
    print(f'active submission {sub and sub["id"]} ({sub and sub["package"]}); validated {v.get("submission")} ({v.get("package")})')
    print(f'trial: {s.get("trial")}')
    for p in s.get('parked') or []:
        run = panel_run(p)
        # compared with the panel run of the build validated NOW (another parked trial may have been accepted since)
        print(f'parked: {p.get("package")} (submission {p.get("submission")}) since {pdt(p.get("parked"))}: ' +
              (f'panel done ({run}); tools/paired.py {run} {v.get("panel_run")}, then trial-decide '
               f'{p.get("submission")} --accept|--reject' if run else
               f'panel playing (run {p.get("run_dir")}, trial-start pid {p.get("pid")})'))
    print(f'mode {ranked_mode(n_rated(ms), parse_t(v.get("since")), now)}; next autoscrim {nxt}')


def cmd_init(sub_id, package):
    with state_lock():
        s = load_state()
        s['validated'] = {'submission': sub_id, 'package': package, 'since': utcnow().isoformat()}
        s['history'].append({'at': utcnow().isoformat(), 'event': 'init', 'submission': sub_id, 'package': package})
        save_state(s)
    print('validated build', sub_id, package)


def screen_gate(s, package, skip_screen):
    """The pre-trial screen check, before any replica call: the history fields for the trial-start event, or
    SystemExit naming the command to run."""
    v = s.get('validated') or {}
    if skip_screen is not None:
        if not skip_screen.strip():
            raise SystemExit('--skip-screen needs a reason')
        return {'screen_skipped': skip_screen.strip()}
    ch, ih = bot_hash(package), bot_hash(v.get('package'))
    ok, path, why = screen_check(SCREENS, ch, ih)
    if not ok:
        raise SystemExit(f'no passing pre-trial screen for {package} ({ch}) against the validated build '
                         f'{v.get("package")} ({ih}): {why}\nrun: tools/screen.py {package}   '
                         f'(docs/ARCHETYPES.md section 5; override: --skip-screen "<reason>")')
    return {'screen': os.path.relpath(path, REPO)}


def cmd_trial_start(package, panel, tag, force, skip_screen=None):
    resume = os.environ.get('RESUME')
    if resume and os.path.exists(os.path.join(resume, 'requests.jsonl')):
        # a resumed panel keeps the build its requests were made with; this command would submit a new one
        raise SystemExit(f'RESUME={resume} holds requests of an earlier block: resume it with RESUME={resume} '
                         f'tools/contest.py block <cells> --tag <tag> (it keeps their submission), not with trial-start')
    with state_lock():                  # held until the trial is recorded: no other command changes the active build
        s = load_state()
        if s.get('trial'):                                      # parked trials do not count: their matches exist
            raise SystemExit(f'a trial is already in progress: {s["trial"]}')
        screen = screen_gate(s, package, skip_screen)          # before any replica call
        sub = active_submission()
        v = s.get('validated') or {}
        if not sub or sub['id'] != v.get('submission'):
            raise SystemExit(f'the active submission is not the validated build ({sub and sub["id"]} vs '
                             f'{v.get("submission")})')
        now = utcnow()
        nxt = next_autoscrim(now)
        if not force and not trial_window_ok(nxt, now):
            raise SystemExit(f'next autoscrim at {nxt}: a trial needs {TRIAL_HOURS} h; start after it fires (or --force)')
        contest.set_auto_accept(ranked='R', unranked='A')          # incoming ranked challenges would play the candidate
        code = bot_hash(package)                                    # the code submitted now
        new = contest.submit(package, f'{package} (trial)')
        trial = {'submission': new['id'], 'package': package, 'started': utcnow().isoformat(), 'panel': panel,
                 'run_dir': None, 'pid': os.getpid(), 'hash': code}
        try:
            done = contest.wait_submission(new['id'])
        except SystemExit as e:
            # not compiled yet, but it may still compile and become active: recorded as an open trial without a
            # panel, so that status shows it and trial-end --reject puts the validated build back
            s['trial'] = dict(trial, pid=None, compile='timeout')
            s['history'].append(dict({'at': utcnow().isoformat(), 'event': 'trial-start', 'submission': new['id'],
                                      'package': package, 'compile': 'timeout'}, **screen))
            save_state(s)
            raise SystemExit(f'{e}: recorded as an open trial without a panel; end it with trial-end --reject')
        if done['status'] != 'OK!' or not done['accepted']:
            contest.set_auto_accept(ranked='A', unranked='A')
            raise SystemExit(f'candidate {package} did not compile: {done["status"]}\n{done.get("logs", "")[-1500:]}')
        tag = tag or f'panel-{package}'
        run_dir = resume or os.path.join(REPO, 'gauntlet', time.strftime('%Y%m%d-%H%M%S') + '-' + tag)
        # the run directory, this process and the code hash go on the trial so that a parked trial keeps them (the
        # hash: trial-decide --accept resubmits the package and refuses if its code changed since)
        s['trial'] = dict(trial, run_dir=os.path.relpath(run_dir, REPO))
        s['history'].append(dict({'at': utcnow().isoformat(), 'event': 'trial-start', 'submission': new['id'],
                                  'package': package}, **screen))
        save_state(s)
    print('trial', new['id'], package, '- running the panel')
    # the block plays the candidate only: it stops before a request if another submission is active
    run = contest.block(panel, tag, run=run_dir, submission=new['id'])
    rel = os.path.relpath(run, REPO)
    with state_lock():
        s = load_state()
        # trials are asynchronous (owner, PROMPTS 32): this trial may have been parked or ended, and another started,
        # while its panel was still playing; record the run on this trial, open or parked (matched by submission); a
        # parked or ended trial's run also goes in the history
        parked = next((p for p in s.get('parked') or [] if p.get('submission') == new['id']), None)
        if s.get('trial') and s['trial'].get('submission') == new['id']:
            s['trial']['run'] = rel
            then = 'trial-end'
        else:
            if parked is not None:
                parked['run'] = rel
                parked['panel_done'] = utcnow().isoformat()
            s['history'].append({'at': utcnow().isoformat(), 'event': 'panel-done', 'submission': new['id'],
                                 'package': package, 'run': rel})
            then = (f'trial-decide {new["id"]}' if parked is not None else      # the id: unambiguous
                    'nothing to decide (the trial was ended)')
        save_state(s)
    print('panel done:', run,
          f'- decide with tools/paired.py <this run> <the validated build\'s panel run>, then {then}')


def cmd_trial_end(accept):
    with state_lock():                  # the reject's compile wait included: parked entries written meanwhile survive
        s = load_state()
        t = s.get('trial')
        if not t:
            raise SystemExit('no trial in progress')
        if accept:
            s['validated'] = {'submission': t['submission'], 'package': t['package'], 'since': utcnow().isoformat(),
                              'panel_run': t.get('run')}
            event = 'accept'
        else:
            v = s['validated']
            back = contest.submit(v['package'], f'{v["package"]} (validated, resubmitted after a rejected trial)')
            done = contest.wait_submission(back['id'])
            if done['status'] != 'OK!' or not done['accepted']:
                raise SystemExit(f'resubmitting {v["package"]} failed: {done["status"]}')
            v['submission'] = back['id']
            event = 'reject'
        contest.set_auto_accept(ranked='A', unranked='A')
        s['history'].append({'at': utcnow().isoformat(), 'event': event, 'submission': t['submission'],
                             'package': t['package']})
        s['trial'] = None
        save_state(s)
    print(event, t['package'], '- validated build is', s['validated'])
    if event == 'accept':
        print(ACCEPT_NEXT)


def panel_cells(t):
    """The trial's panel cells (its --panel path, as given to trial-start: relative to the caller's directory or the
    repository)."""
    p = t.get('panel') or ''
    if not os.path.isabs(p) and not os.path.exists(p):
        p = os.path.join(REPO, p)
    return contest.read_cells(p)


def cmd_trial_park(poll=PARK_POLL, timeout=PARK_TIMEOUT):
    """Park the open trial once every panel request has a created match played by the candidate: resubmit the validated
    build (as trial-end --reject does), restore auto-accept, and move the trial to s['parked'], so that the validated
    build plays while the panel waits in the queue and another trial can start."""
    s = load_state()
    t = s.get('trial')
    if not t:
        raise SystemExit('no trial in progress')
    cells = panel_cells(t)
    tid = contest.me()['id']
    t0 = time.time()
    while True:
        got = panel_created(cells, our_matches(tid, PARK_PAGES), tid, t['submission'])
        n = sum(1 for g in got if g is not None)
        if n == len(cells):
            break
        if time.time() - t0 >= timeout:
            raise SystemExit(f'trial {t["package"]} (submission {t["submission"]}): {n} of {len(cells)} panel matches '
                             f'exist after {timeout / 60:g} min; the trial stays open (run trial-park again later, or '
                             f'trial-end)')
        print(time.strftime('%H:%M:%S'), f'{n} of {len(cells)} panel matches exist; waiting', flush=True)
        time.sleep(poll)
    # under the lock from here to the write: the state read now (the trial, the validated build, the trial-start
    # process's run if its panel already ended) is the one written back
    with state_lock():
        s = load_state()
        if (s.get('trial') or {}).get('submission') != t['submission']:
            raise SystemExit(f'trial {t["package"]} (submission {t["submission"]}) was ended while trial-park waited')
        v = s['validated']
        back = contest.submit(v['package'], f'{v["package"]} (validated, resubmitted: trial {t["package"]} parked)')
        done = contest.wait_submission(back['id'])
        if done['status'] != 'OK!' or not done['accepted']:
            raise SystemExit(f'resubmitting {v["package"]} failed: {done["status"]}; the trial stays open')
        contest.set_auto_accept(ranked='A', unranked='A')
        v['submission'] = back['id']
        entry = dict({'run_dir': None, 'pid': None}, **s['trial'])
        entry.update(parked=utcnow().isoformat(), panel_matches=got)
        s.setdefault('parked', []).append(entry)
        s['trial'] = None
        s['history'].append({'at': utcnow().isoformat(), 'event': 'park', 'submission': entry['submission'],
                             'package': entry['package'], 'validated_resubmitted': back['id']})
        save_state(s)
    print('parked', entry['package'], f'(submission {entry["submission"]}, panel matches {got}); validated build',
          v['package'], 'is active again as', back['id'])


def cmd_trial_decide(key, accept):
    """Decide a parked trial whose panel is done. --reject drops it; --accept resubmits its package (the code the panel
    played: same code hash) and makes that new submission the validated build. --accept is refused while a trial is
    open, since the resubmission would replace the candidate under test as the active submission. Under the state lock
    throughout: a trial-start waits until the accept is recorded (and then screens against the new validated build)."""
    with state_lock():
        s = load_state()
        p = find_parked(s, key)
        run = panel_run(p)
        if not run:
            raise SystemExit(f'the panel of {p["package"]} (submission {p["submission"]}) is still playing '
                             f'(run {p.get("run_dir")}, trial-start pid {p.get("pid")})')
        if accept:
            if s.get('trial'):
                raise SystemExit(f'a trial is in progress ({s["trial"].get("package")}, submission '
                                 f'{s["trial"].get("submission")}): park or end it before accepting {p["package"]}')
            h = bot_hash(p['package'])
            if p.get('hash') and h != p['hash']:
                raise SystemExit(f'src/{p["package"]} is not the code its trial played (code hash {h}, trial '
                                 f'{p["hash"]})')
            new = contest.submit(p['package'], f'{p["package"]} (validated: parked trial {p["submission"]} accepted)')
            done = contest.wait_submission(new['id'])
            if done['status'] != 'OK!' or not done['accepted']:
                raise SystemExit(f'resubmitting {p["package"]} failed: {done["status"]}; it stays parked')
            s['validated'] = {'submission': new['id'], 'package': p['package'], 'since': utcnow().isoformat(),
                              'panel_run': run}
            # an accept event names the submission that became the validated build (tools/rating_history.py kind_of)
            ev = {'event': 'accept', 'submission': new['id'], 'package': p['package'],
                  'trial_submission': p['submission']}
        else:
            ev = {'event': 'reject', 'submission': p['submission'], 'package': p['package']}
        s['parked'] = [q for q in s['parked'] if q is not p]
        s['history'].append(dict({'at': utcnow().isoformat()}, **ev, parked=True, run=run))
        save_state(s)
    print(ev['event'], p['package'], '- validated build is', s['validated'])
    if ev['event'] == 'accept':
        print(ACCEPT_NEXT)


def expected_gain(p_bt, r_us, r_opp, k=GAIN_K):
    """Expected change of our galaxy rating from one ranked match: K (P - E), P our win chance from the BT fit, E the
    share galaxy expects from the two displayed ratings (LEARNINGS: BT predicts better than the ladder's Elo)."""
    return k * (p_bt - 1 / (1 + 10 ** ((r_opp - r_us) / 400)))


def pick_gain(ladder, tid, rested, now, P, min_gain=MIN_GAIN):
    """(team, gain): the open team rated at or above us (galaxy allows no other ranked request) with the largest
    expected gain above min_gain, or (None, best gain seen or None). Teams P has no estimate for are skipped."""
    me = next((t for t in ladder if t['id'] == tid), None)
    if me is None or me['rating'] is None:
        return None, None
    best, bg = None, None
    for t in ladder:
        if (t['id'] == tid or not t['active'] or t['status'] != 'R' or t['rating'] is None
                or t['rating'] < me['rating'] or rested.get(t['id'], now) > now or t['name'] not in P):
            continue
        g = expected_gain(P[t['name']], me['rating'], t['rating'])
        if bg is None or g > bg:
            best, bg = t, g
    return (best, bg) if bg is not None and bg > min_gain else (None, bg)


def bt_probs(package):
    """{player name: P(the build `package` beats it)} from a BT fit over progress/games.csv, or None when the
    build has no games. Field players are named as galaxy names the teams."""
    if os.path.join(REPO, 'tools') not in sys.path:
        sys.path.insert(0, os.path.join(REPO, 'tools'))
    import elolib
    R = elolib.fit(elolib.dedupe(elolib.load()))[0]
    u = 'us:' + package
    if u not in R:
        return None
    return {n: elolib.expected(R[u], r) for n, r in R.items() if n != u}


def pick_open(ladder, tid, rested, now, rnd):
    """pick_upward over the teams not resting (409: 3 active ranked matches with them, or they fell below us)."""
    open_ = [t for t in ladder if t['id'] == tid or rested.get(t['id'], now) <= now]
    return contest.pick_upward(open_, tid, BAND, rnd)


def cmd_ranked(poll=60):
    rnd = random.Random()
    team = contest.me()
    tid = team['id']
    last = None
    note = None
    rested = {}                     # team id -> time it may be challenged again
    P, P_for, P_at = None, None, 0.0  # BT win chances of the validated build, refreshed hourly
    while True:
        try:
            pkg = (load_state().get('validated') or {}).get('package')
            if pkg and (pkg != P_for or time.time() - P_at > BT_REFRESH):
                try:
                    P = bt_probs(pkg)
                except Exception as e:  # no model: fall back to the closest teams above us
                    print(time.strftime('%H:%M:%S'), 'BT fit failed:', e, flush=True)
                    P = None
                P_for, P_at = pkg, time.time()
            # Match creation fixes the active submission. Serialize the fresh checks and request with every command
            # that changes it; otherwise trial-start can activate its candidate after the check but before the POST.
            with state_lock():
                now = utcnow()
                s = load_state()
                ms = our_matches(tid)
                sub = active_submission()
                v = s.get('validated') or {}
                mode = ranked_mode(n_rated(ms), parse_t(v.get('since')), now)
                ok, why = may_challenge(s, sub and sub['id'], waiting(ms), last, mode, now)
                if ok:
                    ladder = contest.rankings()
                    if P:
                        opp, gain = pick_gain(ladder, tid, rested, now, P)
                        if opp is None and note != 'gain':
                            print(time.strftime('%H:%M:%S'), 'no open team above us with a positive expected gain'
                                  f' (best {gain if gain is None else round(gain, 1)}): no ranked request', flush=True)
                            note = 'gain'
                    else:
                        opp, gain = pick_open(ladder, tid, rested, now, rnd), None
                    if opp:
                        try:
                            r = contest.request(opp['id'], True, [], '?')
                        except contest.ApiError as e:
                            if e.code != 409:
                                raise
                            rested[opp['id']] = now + datetime.timedelta(minutes=15)
                            print(time.strftime('%H:%M:%S'), 'resting', opp['name'], '15 min:', e.detail[:80], flush=True)
                            continue
                        last = now
                        print(time.strftime('%H:%M:%S'), mode, 'ranked request', r['id'], 'to', opp['name'], 'rated',
                              opp['rating'], '' if gain is None else f'expected gain {gain:+.1f}', flush=True)
                        note = None
                    elif P is None and note != 'top':
                        print(time.strftime('%H:%M:%S'), 'nobody rated at or above us: weaker teams challenge us', flush=True)
                        note = 'top'
                elif why not in ('interval',) and why != note:
                    print(time.strftime('%H:%M:%S'), 'paused:', why, flush=True)
                    note = why
        except contest.ApiError as e:
            print(time.strftime('%H:%M:%S'), 'refused:', e.code, e.detail[:120], flush=True)
            if e.code == 429:
                time.sleep(600)
        except Exception as e:      # a network hiccup must not end the loop
            print(time.strftime('%H:%M:%S'), 'error:', e, flush=True)
        time.sleep(poll)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('status')
    s = sp.add_parser('init'); s.add_argument('submission', type=int); s.add_argument('package')
    s = sp.add_parser('trial-start'); s.add_argument('package'); s.add_argument('--panel', default='test/cells/panel-v1.txt')
    s.add_argument('--tag'); s.add_argument('--force', action='store_true', help='ignore the autoscrim window only')
    s.add_argument('--skip-screen', metavar='REASON', help='start without a passing pre-trial screen (logged)')
    s = sp.add_parser('trial-end'); g = s.add_mutually_exclusive_group(required=True)
    g.add_argument('--accept', action='store_true'); g.add_argument('--reject', action='store_true')
    sp.add_parser('trial-park')
    s = sp.add_parser('trial-decide'); s.add_argument('package', help='the parked trial: its package or submission id')
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument('--accept', action='store_true'); g.add_argument('--reject', action='store_true')
    sp.add_parser('ranked')
    a = ap.parse_args()
    if a.cmd == 'status':
        cmd_status()
    elif a.cmd == 'init':
        cmd_init(a.submission, a.package)
    elif a.cmd == 'trial-start':
        cmd_trial_start(a.package, a.panel, a.tag, a.force, a.skip_screen)
    elif a.cmd == 'trial-end':
        cmd_trial_end(a.accept)
    elif a.cmd == 'trial-park':
        cmd_trial_park()
    elif a.cmd == 'trial-decide':
        cmd_trial_decide(a.package, a.accept)
    elif a.cmd == 'ranked':
        cmd_ranked()
    return 0


if __name__ == '__main__':
    sys.exit(main())
