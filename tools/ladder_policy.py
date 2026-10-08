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
             validated build is resubmitted at once). A trial starts only if it can end before the next autoscrim.

    tools/ladder_policy.py status
    tools/ladder_policy.py init <submission id> <package>      # declare the validated build (once)
    tools/ladder_policy.py trial-start <package> [--panel test/cells/panel-v1.txt] [--tag T] [--force]
    tools/ladder_policy.py trial-end --accept | --reject
    tools/ladder_policy.py ranked                               # the ranked loop (run detached)
"""
import argparse, datetime, importlib.util, json, os, random, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, 'progress', 'ladder-state.json')
_spec = importlib.util.spec_from_file_location('contest', os.path.join(REPO, 'tools', 'contest.py'))
contest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(contest)
E = contest.EPISODE

BURST_EVERY, MAINTAIN_EVERY = 300, 1800        # seconds between our ranked requests
YOUNG_N = 30                                    # rated matches until the volume penalty is small (1500*0.85^30 = 11)
FRESH_HOURS = 24                                # a newly validated build is likely underrated for this long
MAX_WAITING = 2                                 # our matches waiting in the queue: above this, no new ranked request
TRIAL_HOURS = 2.5                               # a panel trial must fit before the next autoscrim
BAND = 3                                        # challenge one of the BAND teams rated closest at or above us


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


# ---------------------------------------------------------------- state and galaxy facts
def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {'validated': None, 'trial': None, 'history': []}


def save_state(s):
    tmp = STATE + '.tmp'
    with open(tmp, 'w') as fh:
        json.dump(s, fh, indent=1)
        fh.write('\n')
    os.replace(tmp, STATE)


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
# watching when autoscrim matches appear. Ours is every 8 hours on the hour, UTC (docs/galaxy/README.md section 6).
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
    print(f'mode {ranked_mode(n_rated(ms), parse_t(v.get("since")), now)}; next autoscrim {nxt}')


def cmd_init(sub_id, package):
    s = load_state()
    s['validated'] = {'submission': sub_id, 'package': package, 'since': utcnow().isoformat()}
    s['history'].append({'at': utcnow().isoformat(), 'event': 'init', 'submission': sub_id, 'package': package})
    save_state(s)
    print('validated build', sub_id, package)


def cmd_trial_start(package, panel, tag, force):
    s = load_state()
    if s.get('trial'):
        raise SystemExit(f'a trial is already in progress: {s["trial"]}')
    sub = active_submission()
    v = s.get('validated') or {}
    if not sub or sub['id'] != v.get('submission'):
        raise SystemExit(f'the active submission is not the validated build ({sub and sub["id"]} vs {v.get("submission")})')
    now = utcnow()
    nxt = next_autoscrim(now)
    if not force and not trial_window_ok(nxt, now):
        raise SystemExit(f'next autoscrim at {nxt}: a trial needs {TRIAL_HOURS} h; start after it fires (or --force)')
    contest.set_auto_accept(ranked='R', unranked='A')          # incoming ranked challenges would play the candidate
    new = contest.submit(package, f'{package} (trial)')
    done = contest.wait_submission(new['id'])
    if done['status'] != 'OK!' or not done['accepted']:
        contest.set_auto_accept(ranked='A', unranked='A')
        raise SystemExit(f'candidate {package} did not compile: {done["status"]}\n{done.get("logs", "")[-1500:]}')
    s['trial'] = {'submission': new['id'], 'package': package, 'started': utcnow().isoformat(), 'panel': panel}
    s['history'].append({'at': utcnow().isoformat(), 'event': 'trial-start', 'submission': new['id'], 'package': package})
    save_state(s)
    print('trial', new['id'], package, '- running the panel')
    run = contest.block(panel, tag or f'panel-{package}')
    s = load_state()
    s['trial']['run'] = os.path.relpath(run, REPO)
    save_state(s)
    print('panel done:', run, '- decide with tools/paired.py <this run> <the validated build\'s panel run>, then trial-end')


def cmd_trial_end(accept):
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
    s['history'].append({'at': utcnow().isoformat(), 'event': event, 'submission': t['submission'], 'package': t['package']})
    s['trial'] = None
    save_state(s)
    print(event, t['package'], '- validated build is', s['validated'])


def cmd_ranked(poll=60):
    rnd = random.Random()
    team = contest.me()
    tid = team['id']
    last = None
    note = None
    while True:
        try:
            now = utcnow()
            s = load_state()
            ms = our_matches(tid)
            sub = active_submission()
            v = s.get('validated') or {}
            mode = ranked_mode(n_rated(ms), parse_t(v.get('since')), now)
            ok, why = may_challenge(s, sub and sub['id'], waiting(ms), last, mode, now)
            if ok:
                opp = contest.pick_upward(contest.rankings(), tid, BAND, rnd)
                if opp:
                    r = contest.request(opp['id'], True, [], '?')
                    last = now
                    print(time.strftime('%H:%M:%S'), mode, 'ranked request', r['id'], 'to', opp['name'], 'rated', opp['rating'], flush=True)
                    note = None
                elif note != 'top':
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
    s.add_argument('--tag'); s.add_argument('--force', action='store_true')
    s = sp.add_parser('trial-end'); g = s.add_mutually_exclusive_group(required=True)
    g.add_argument('--accept', action='store_true'); g.add_argument('--reject', action='store_true')
    sp.add_parser('ranked')
    a = ap.parse_args()
    if a.cmd == 'status':
        cmd_status()
    elif a.cmd == 'init':
        cmd_init(a.submission, a.package)
    elif a.cmd == 'trial-start':
        cmd_trial_start(a.package, a.panel, a.tag, a.force)
    elif a.cmd == 'trial-end':
        cmd_trial_end(a.accept)
    elif a.cmd == 'ranked':
        cmd_ranked()
    return 0


if __name__ == '__main__':
    sys.exit(main())
