#!/usr/bin/env python3
"""Event watcher that keeps the session working without a fixed-interval loop (owner, PROMPTS 90).

    tools/watch_events.py [--heartbeat MIN] [--poll SEC]

Runs in the background (Bash run_in_background) and EXITS on the first new event, which wakes the agent; at the end
of every turn the agent re-arms it. Events, each reported once (keys kept in build/watch-events.seen):
  PANEL_DONE <package>      a parked trial's panel finished (tools/ladder_policy.py status says "panel done")
  SCREEN_DONE <job>         a VM screen job finished (SCREEN-END in its log) and has no collected record yet
  SWISS_DONE <run>          a VM Swiss tournament (tools/swiss.py) wrote final.txt and research/swiss/<run>/ lacks it
  RACE_DONE <run>           a VM race (tools/race.py) wrote final.txt and research/race/<run>/ lacks it
  STUCK_MATCH <id>          a replica match the watcher has seen in RUN for more than 1 hour (siarnaq rates in creation
                            order, so one stuck match freezes every later rating: 2565, 2593, 6282). Age since creation
                            is no test: after an autoscrim, matches wait in QUE for hours and start late (2026-10-14:
                            90 false alarms).
  QUEUE_STALLED             matches wait in QUE more than 2 hours after creation and none is RUN (the runner is down)
  RANKED_DEAD               the ranked loop process is gone
  REPLICA_DOWN              the replica API does not answer
  VM_DOWN                   the VM does not answer ssh
  QUEUE_RUNNER_DEAD         VM jobs are pending and nobody holds queue/.lock, the runner's flock (a STOP file left it down 2026-10-12 18:48 to
                            10-14 11:47 PDT, and four screens waited unseen)
  HEARTBEAT                 nothing happened for --heartbeat minutes (default 50, under the 1-hour prompt cache): the
                            agent takes the next item from TRAINING_ALGORITHM's target sources
The pure parts (event keys, staleness) are tested in tools/test_tools.py WatchEventsTest."""
import argparse, datetime as dt, json, os, shlex, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN = os.path.join(REPO, 'build', 'watch-events.seen')
RUN_SINCE = os.path.join(REPO, 'build', 'watch-events.run.json')   # match id -> first time the watcher saw it RUN
sys.path.insert(0, os.path.join(REPO, 'tools'))


def load_seen(path=SEEN):
    try:
        return set(l.strip() for l in open(path) if l.strip())
    except FileNotFoundError:
        return set()


def mark_seen(key, path=SEEN):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as fh:
        fh.write(key + '\n')


def parse_ts(s):
    """An API timestamp (ISO 8601 with offset) -> aware UTC datetime."""
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(dt.timezone.utc)


def stuck_matches(matches, run_since, now, hours=1.0):
    """Ids of matches seen in RUN for more than `hours`, and the updated first-seen-RUN map {id: epoch seconds},
    keeping only matches still in RUN (pure; `now` is epoch seconds)."""
    since = {}
    for m in matches:
        if m.get('status') == 'RUN':
            since[str(m['id'])] = run_since.get(str(m['id']), now)
    return sorted(int(i) for i, t in since.items() if now - t > hours * 3600), since


def queue_stalled(matches, now, hours=2.0):
    """True when a match waits in QUE more than `hours` after creation while none is RUN (pure; aware `now`)."""
    if any(m.get('status') == 'RUN' for m in matches):
        return False
    return any(m.get('status') == 'QUE' and (now - parse_ts(m['created'])).total_seconds() > hours * 3600
               for m in matches)


def panels_done(status_text):
    """Packages of parked trials whose panel is done, from `ladder_policy.py status` output (pure)."""
    out = []
    for line in status_text.splitlines():
        line = line.strip()
        if line.startswith('parked:') and 'panel done' in line:
            out.append(line.split()[1])
    return out


def new_events(candidates, seen):
    """Candidate event keys not reported before, in order (pure)."""
    return [c for c in candidates if c not in seen]


def vm_check_cmd():
    """The VM probe: finished screen jobs, finished Swiss runs (SWISS:<run>) and races (RACE:<run>), and a dead queue
    runner. The remote command is single-quoted for the local shell: until 2026-10-16 it sat in double quotes, so
    $(ls logs/...) and $f expanded on the driver (no screen logs there) and SCREEN_DONE could never fire."""
    remote = ('cd ~/projects/vibe/2023; '
              'for f in $(ls -t logs/*scr-*.log 2>/dev/null | head -6); do tail -1 $f | grep -q SCREEN-END && basename $f .log; done; '
              'for d in $(ls -d gauntlet/*-swiss* 2>/dev/null); do [ -f $d/final.txt ] && echo SWISS:$(basename $d); done; '
              'for d in $(ls -d gauntlet/*-race* 2>/dev/null); do [ -f $d/final.txt ] && echo RACE:$(basename $d); done; '
              'ls queue/pending | grep -q . && flock -n queue/.lock true && echo RUNNER-DEAD; true')
    return 'bash -c ' + shlex.quote('source tools/vm.sh && ensure_vm >/dev/null 2>&1 && gssh ' + shlex.quote(remote))


def sh(cmd, timeout=120):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=REPO)
    except subprocess.TimeoutExpired:
        return None


_last_stuck_scan = [0.0]


def check(stuck_every=900, stuck_pages=40):
    """Every candidate event key right now (side effects: API, ssh, ps). The stuck-match scan reads the newest
    stuck_pages x 10 matches (an autoscrim creates ~176 at once) at most every stuck_every seconds, so a stuck RUN
    match is reported 1 to 1.25 hours after the watcher first saw it running (the map persists across re-arms)."""
    ev = []
    r = sh('timeout 60 python3 tools/ladder_policy.py status')
    if r is None or r.returncode != 0 or 'Connection refused' in (r.stdout + r.stderr):
        ev.append('REPLICA_DOWN')
    else:
        ev += [f'PANEL_DONE {p}' for p in panels_done(r.stdout)]
    if sh("ps -eo args | grep -q '[l]adder_policy.py ranked'").returncode != 0:
        ev.append('RANKED_DEAD')
    if time.time() - _last_stuck_scan[0] >= stuck_every:
        _last_stuck_scan[0] = time.time()
        try:
            import contest
            ms = contest.pages('/api/compete/bc23/match/?ordering=-id', limit=stuck_pages)
            try:
                run_since = json.load(open(RUN_SINCE))
            except (FileNotFoundError, ValueError):
                run_since = {}
            stuck, run_since = stuck_matches(ms, run_since, time.time())
            with open(RUN_SINCE, 'w') as fh:
                json.dump(run_since, fh)
            ev += [f'STUCK_MATCH {i}' for i in stuck]
            if queue_stalled(ms, dt.datetime.now(dt.timezone.utc)):
                ev.append('QUEUE_STALLED')
        except Exception:
            pass
    r = sh(vm_check_cmd(), 90)
    if r is None or r.returncode != 0:
        ev.append('VM_DOWN')
    else:
        for job in r.stdout.split():
            if job == 'RUNNER-DEAD':
                ev.append('QUEUE_RUNNER_DEAD')
                continue
            if job.startswith(('SWISS:', 'RACE:')):
                kind, run = job.split(':', 1)
                if not os.path.exists(os.path.join(REPO, 'research', kind.lower(), run, 'final.txt')):
                    ev.append(f'{kind}_DONE {run}')
                continue
            pkg_hash = job.split('-scr-', 1)[-1]                     # <package>-<hash>
            if not os.path.exists(os.path.join(REPO, 'progress', 'screens', pkg_hash + '.json')):
                ev.append(f'SCREEN_DONE {job}')
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--heartbeat', type=float, default=50.0)
    ap.add_argument('--poll', type=float, default=60.0)
    o = ap.parse_args()
    t0 = time.time()
    while True:
        seen = load_seen()
        fresh = new_events(check(), seen)
        # transient states (down, dead) are re-reported each time the watcher is armed; completions only once
        once = [e for e in fresh if e.split()[0] in ('PANEL_DONE', 'SCREEN_DONE', 'SWISS_DONE', 'RACE_DONE', 'STUCK_MATCH')]
        if fresh:
            for e in once:
                mark_seen(e)
            print('\n'.join(fresh), flush=True)
            return
        if time.time() - t0 > o.heartbeat * 60:
            print('HEARTBEAT', flush=True)
            return
        time.sleep(o.poll)


if __name__ == '__main__':
    main()
