#!/usr/bin/env python3
"""Last-commit date of every benchmark package, from GitHub metadata only (no source is read).

    tools/bench-dates.py          -> $BENCH_ROOT/dates.tsv: name  path  last_commit_iso

The package directory is located in the sparse clone by the RobotPlayer.java whose package matches (paths only).
Archive repositories uploaded in one commit give every package the same date; selection then falls back to names.
"""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(os.environ.get('BENCH_ROOT', Path.home() / 'projects/vibe/bc23-benchmarks'))


def gh(path, params):
    args = ['gh', 'api', '-X', 'GET', path] + sum([['-f', f'{k}={v}'] for k, v in params.items()], [])
    for _ in range(5):
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout)
        if 'rate limit' in (r.stderr + r.stdout).lower():
            time.sleep(60)
            continue
        return None
    return None


def main():
    rows = [l.split('\t') for l in (ROOT / 'manifest.tsv').read_text().splitlines()[1:] if l.strip()]
    disc = {}
    for l in (ROOT / '_classify.tsv').read_text().splitlines()[1:]:
        f = l.split('\t')
        disc[f[0]] = f[1]                       # dir -> owner/repo
    out_p = ROOT / 'dates.tsv'
    done = {}
    if out_p.exists():
        for l in out_p.read_text().splitlines()[1:]:
            f = l.split('\t')
            done[f[0]] = l
    out = ['name\tpath\tlast_commit']
    pkgdirs = {}                                        # repo -> {package leaf: relative dir}, one walk per repo
    for name, package, classdir, repo, commit in (r[:5] for r in rows):
        if name in done:
            out.append(done[name])
            continue
        full = disc.get(repo)
        if repo not in pkgdirs:
            pkgdirs[repo] = {}
            for p in (ROOT / repo).rglob('RobotPlayer.java'):
                pkgdirs[repo].setdefault(p.parent.name, p.parent.relative_to(ROOT / repo))
        rp = pkgdirs[repo].get(package.split('.')[-1])
        date = ''
        if full and rp is not None:
            d = gh(f'repos/{full}/commits', {'path': str(rp), 'per_page': 1})
            time.sleep(0.3)
            if d:
                date = d[0]['commit']['committer']['date']
        out.append(f'{name}\t{rp}\t{date}')
        if len(out) % 50 == 0:
            out_p.write_text('\n'.join(out) + '\n')
    out_p.write_text('\n'.join(out) + '\n')
    print(f'{len(out) - 1} packages dated -> {out_p}')


if __name__ == '__main__':
    main()
