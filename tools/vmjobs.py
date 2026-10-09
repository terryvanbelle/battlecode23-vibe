#!/usr/bin/env python3
"""The VM's standing queue, seen from the driver (docs/ARCHETYPES.md section 6.5): the only code that talks to the VM
queue for tools/screen.py (and tools/archsig.py). It wraps tools/vm-enqueue.sh (which syncs src/ tools/ test/ first)
and tools/vm.sh (ensure_vm, gssh, SSHO) through bash; it never rsyncs anything toward the VM itself.

    tools/vmjobs.py status <job>                 # pending | running | done | missing
    tools/vmjobs.py wait <job> [--poll 60] [--timeout S]
    tools/vmjobs.py runs <tag>                   # VM gauntlet/*-<tag> run ids, oldest first
    tools/vmjobs.py fetch <run> [--replays] [--extract]   # VM gauntlet/<run>/ -> local gauntlet/<run>/
    tools/vmjobs.py log <job>                    # the job's log (logs/<job>.log on the VM)
    tools/vmjobs.py disk                         # free GB in the VM's home file system

A job id is '<UTC stamp>-<name>', as tools/vm-enqueue.sh names the job file."""
import argparse, os, re, shlex, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = 'projects/vibe/2023'
_SAFE = re.compile(r'^[A-Za-z0-9_.+-]+$')


def _safe(name, what='name'):
    if not _SAFE.match(name or ''):
        raise ValueError(f'unsafe {what}: {name!r}')
    return name


def _bash(script, capture=True, timeout=600, stdin=None):
    """Run a bash script with tools/vm.sh sourced and the VM ensured."""
    full = f'source {shlex.quote(os.path.join(REPO, "tools", "vm.sh"))} && ensure_vm && {script}'
    r = subprocess.run(['bash', '-c', full], capture_output=capture, text=True, timeout=timeout, input=stdin)
    if r.returncode != 0:
        raise RuntimeError(f'VM command failed ({r.returncode}): {script[:200]}\n{(r.stderr or "")[-800:]}')
    return r.stdout if capture else ''


def ssh(cmd, timeout=300):
    """One command on the VM, from the repo root."""
    return _bash(f'gssh {shlex.quote(f"cd ~/{REMOTE} && {cmd}")}', timeout=timeout)


def parse_enqueued(out):
    """tools/vm-enqueue.sh's 'queued queue/pending/<job>.job ...' line -> '<job>'."""
    m = re.search(r'queued queue/pending/(\S+)\.job', out or '')
    return m.group(1) if m else None


def enqueue(name, script):
    """Queue a job script (synced first by vm-enqueue.sh); returns the job id '<UTC stamp>-<name>'."""
    _safe(name)
    r = subprocess.run(['bash', os.path.join(REPO, 'tools', 'vm-enqueue.sh'), name, script],
                       capture_output=True, text=True, timeout=1800)
    job = parse_enqueued(r.stdout)
    if r.returncode != 0 or not job:
        raise RuntimeError(f'vm-enqueue failed ({r.returncode}): {(r.stdout + r.stderr)[-800:]}')
    return job


def status(job):
    _safe(job, 'job')
    out = ssh(f'for d in pending running done; do [ -f queue/$d/{job}.job ] && {{ echo $d; exit 0; }}; done; echo missing')
    return out.strip().splitlines()[-1] if out.strip() else 'missing'


def wait(job, poll=60, timeout=None, quiet=False):
    """Poll until the job is done (or missing); returns the last status. Network hiccups are retried."""
    t0 = time.time()
    last = None
    while True:
        try:
            st = status(job)
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            st = None
            if not quiet:
                print(time.strftime('%H:%M:%S'), 'vm status error, retrying:', str(e)[:120], file=sys.stderr, flush=True)
        if st and st != last and not quiet:
            print(time.strftime('%H:%M:%S'), job, st, file=sys.stderr, flush=True)
        if st in ('done', 'missing'):
            return st
        last = st or last
        if timeout is not None and time.time() - t0 > timeout:
            return last or 'unknown'
        time.sleep(poll)


def find_runs(tag):
    """VM gauntlet run ids ending in -<tag>, oldest first (run ids start with their creation time)."""
    _safe(tag, 'tag')
    out = ssh(f'ls -d gauntlet/*-{tag} 2>/dev/null || true')
    return sorted(os.path.basename(l.strip()) for l in out.splitlines() if l.strip())


def fetch(run, replays=False, extract=False, dest=None):
    """rsync the VM's gauntlet/<run>/ to the driver (without replays/ and extract/ unless asked); returns the path."""
    _safe(run, 'run')
    dest = dest or os.path.join(REPO, 'gauntlet', run)
    os.makedirs(dest, exist_ok=True)
    ex = ([] if replays else ['--exclude', 'replays/']) + ([] if extract else ['--exclude', 'extract/'])
    exs = ' '.join(shlex.quote(x) for x in ex)
    _bash(f'rsync -a {exs} -e "ssh ${{SSHO[*]}}" "$USER_NAME@$IP:{REMOTE}/gauntlet/{run}/" {shlex.quote(dest + "/")}',
          timeout=1800)
    return dest


def job_log(job):
    _safe(job, 'job')
    return ssh(f'cat logs/{job}.log 2>/dev/null || true')


def free_disk_gb():
    out = ssh('df -k --output=avail ~ | tail -1')
    return int(out.strip().split()[-1]) / 1024 / 1024


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('status').add_argument('job')
    s = sp.add_parser('wait'); s.add_argument('job'); s.add_argument('--poll', type=int, default=60)
    s.add_argument('--timeout', type=float)
    sp.add_parser('runs').add_argument('tag')
    s = sp.add_parser('fetch'); s.add_argument('run'); s.add_argument('--replays', action='store_true')
    s.add_argument('--extract', action='store_true')
    sp.add_parser('log').add_argument('job')
    sp.add_parser('disk')
    a = ap.parse_args()
    if a.cmd == 'status':
        print(status(a.job))
    elif a.cmd == 'wait':
        print(wait(a.job, a.poll, a.timeout))
    elif a.cmd == 'runs':
        print('\n'.join(find_runs(a.tag)))
    elif a.cmd == 'fetch':
        print(fetch(a.run, a.replays, a.extract))
    elif a.cmd == 'log':
        sys.stdout.write(job_log(a.job))
    elif a.cmd == 'disk':
        print(f'{free_disk_gb():.2f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
