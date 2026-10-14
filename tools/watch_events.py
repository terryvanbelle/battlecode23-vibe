#!/usr/bin/env python3
"""Event watcher that keeps the session working without a fixed-interval loop (owner, PROMPTS 90).

    tools/watch_events.py [--heartbeat MIN] [--poll SEC]

Runs in the background (Bash run_in_background) and EXITS on the first new event, which wakes the agent; at the end
of every turn the agent re-arms it. Events, each reported once (keys kept in build/watch-events.seen):
  PANEL_DONE <package>      a parked trial's panel finished (tools/ladder_policy.py status says "panel done")
  SCREEN_DONE <job>         a VM screen job finished (SCREEN-END in its log) and has no collected record yet
  STUCK_MATCH <id>          a replica match in RUN or QUE for more than 2 hours (siarnaq rates in creation order, so
                            one stuck match freezes every later rating: 2565, 2593, 6282)
  RANKED_DEAD               the ranked loop process is gone
  REPLICA_DOWN              the replica API does not answer
  VM_DOWN                   the VM does not answer ssh
  HEARTBEAT                 nothing happened for --heartbeat minutes (default 50, under the 1-hour prompt cache): the
                            agent takes the next item from TRAINING_ALGORITHM's target sources
The pure parts (event keys, staleness) are tested in tools/test_tools.py WatchEventsTest."""
import argparse, datetime as dt, json, os, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN = os.path.join(REPO, 'build', 'watch-events.seen')
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


def stuck_matches(matches, now, hours=2.0):
    """Ids of matches still RUN/QUE more than `hours` after creation (pure)."""
    out = []
    for m in matches:
        if m.get('status') in ('RUN', 'QUE') and (now - parse_ts(m['created'])).total_seconds() > hours * 3600:
            out.append(m['id'])
    return sorted(out)


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


def sh(cmd, timeout=120):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=REPO)
    except subprocess.TimeoutExpired:
        return None


_last_stuck_scan = [0.0]


def check(stuck_every=900, stuck_pages=40):
    """Every candidate event key right now (side effects: API, ssh, ps). The stuck-match scan reads the newest
    stuck_pages x 10 matches (an autoscrim creates ~176 at once) at most every stuck_every seconds."""
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
            ev += [f'STUCK_MATCH {i}' for i in stuck_matches(ms, dt.datetime.now(dt.timezone.utc))]
        except Exception:
            pass
    r = sh("bash -c 'source tools/vm.sh && ensure_vm && gssh \"cd ~/projects/vibe/2023; for f in $(ls -t logs/*scr-*.log 2>/dev/null | head -6); do tail -1 $f | grep -q SCREEN-END && basename $f .log; done\"'", 90)
    if r is None or r.returncode != 0:
        ev.append('VM_DOWN')
    else:
        for job in r.stdout.split():
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
        once = [e for e in fresh if e.split()[0] in ('PANEL_DONE', 'SCREEN_DONE', 'STUCK_MATCH')]
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
