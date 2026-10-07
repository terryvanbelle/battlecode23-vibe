#!/usr/bin/env python3
"""Build the external ladder field from the compiled benchmarks, by NAME and HASH only (no source is read).

    tools/bench-roster.py            # writes tools/field.txt and prints the roster table
    tools/bench-roster.py --check    # exit 1 if tools/field.txt differs from what would be written

1. Per repo, choose the package most likely to be the final bot (tools/bench-select.py scoring).
2. Merge byte-identical choices (same class-file hash): archive copies and forks of one team's bot are one entrant.
   The kept name prefers the team's own repository over the battlecode-archive copy.
3. Drop entrants listed in tools/field-exclude.txt (with a reason: duds, non-bots).
"""
import importlib.util, sys
from collections import defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = Path.home() / 'projects/vibe/bc23-benchmarks'
spec = importlib.util.spec_from_file_location('bench_select', TOOLS / 'bench-select.py')
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)


def load(man=ROOT / 'manifest.tsv', hashes=ROOT / 'hashes.tsv'):
    rows = [l.split('\t') for l in man.read_text().splitlines()[1:] if l.strip()]
    h = dict(l.split('\t')[:2] for l in hashes.read_text().splitlines()[1:] if l.strip())
    return rows, h


def roster(rows, h, exclude=()):
    by_repo = defaultdict(list)
    for name, package, classdir, repo, commit in (r[:5] for r in rows):
        if bs.JUNK.search(package) and 'final' not in package.lower():
            continue
        by_repo[repo].append((name, package))
    chosen = {repo: max(c, key=lambda x: bs.score(x[1])) for repo, c in by_repo.items()}
    by_hash = defaultdict(list)
    for repo, (name, package) in chosen.items():
        by_hash[h.get(name, name)].append((repo, name))
    field = []
    for hsh, members in by_hash.items():
        members.sort(key=lambda m: (m[0].startswith('battlecode-archive_'), m[0]))
        repo, name = members[0]
        aka = [m[0] for m in members[1:]]
        if name in exclude:
            continue
        field.append((name, repo, hsh, aka, len(by_repo[repo])))
    return sorted(field)


def main():
    rows, h = load()
    excl_file = TOOLS / 'field-exclude.txt'
    exclude = {l.split()[0] for l in excl_file.read_text().splitlines() if l.strip() and not l.startswith('#')} \
        if excl_file.exists() else set()
    field = roster(rows, h, exclude)
    text = '\n'.join(f[0] for f in field) + '\n'
    if '--check' in sys.argv:
        sys.exit(0 if (TOOLS / 'field.txt').read_text() == text else 1)
    (TOOLS / 'field.txt').write_text(text)
    for name, repo, hsh, aka, ncand in field:
        print(f"{name:46s} {repo:50s} {hsh}  cand={ncand:<3d} {'= ' + ', '.join(aka) if aka else ''}")
    print(f'{len(field)} entrants -> tools/field.txt')


if __name__ == '__main__':
    main()
