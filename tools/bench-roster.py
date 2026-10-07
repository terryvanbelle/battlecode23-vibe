#!/usr/bin/env python3
"""Build the external ladder field from the compiled benchmarks, by NAME and HASH only (no source is read).

    tools/bench-roster.py            # writes tools/field.txt and prints the roster table
    tools/bench-roster.py --check    # exit 1 if tools/field.txt differs from what would be written

1. Per repo, choose the package most likely to be the final bot by two rules: names alone (tools/bench-select.py
   scoring) and names-then-last-commit-date (choice_key; dates from tools/bench-dates.py). Both picks enter the field.
2. Merge byte-identical choices (same class-file hash): archive copies and forks of one team's bot are one entrant.
   The kept name prefers the team's own repository over the battlecode-archive copy.
3. Drop entrants listed in tools/field-exclude.txt (with a reason: duds, non-bots).
"""
import importlib.util, re, sys
from collections import defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = Path.home() / 'projects/vibe/bc23-benchmarks'
spec = importlib.util.spec_from_file_location('bench_select', TOOLS / 'bench-select.py')
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)


def load(man=ROOT / 'manifest.tsv', hashes=ROOT / 'hashes.tsv', dates=ROOT / 'dates.tsv'):
    rows = [l.split('\t') for l in man.read_text().splitlines()[1:] if l.strip()]
    h = dict(l.split('\t')[:2] for l in hashes.read_text().splitlines()[1:] if l.strip())
    d = {}
    if dates.exists():
        for l in dates.read_text().splitlines()[1:]:
            f = l.split('\t')
            if len(f) >= 3: d[f[0]] = f[2]
    return rows, h, d


WORDNUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}


def name_class(pkg):
    """Explicit release names first; 'before...' snapshots of a later bot are older versions."""
    n = pkg.lower()
    s = 0
    if 'final' in n: s = 1000
    elif 'postqual' in n: s = 900
    elif 'qual' in n: s = 800
    elif 'seeding' in n: s = 700
    elif 'submi' in n: s = 650
    elif 'sprint2' in n or 'sprint_2' in n: s = 300
    elif 'sprint' in n: s = 200
    if n.startswith('before'): s -= 500
    return s


def version(pkg):
    n = pkg.lower()
    nums = [int(x) for x in re.findall(r'\d+', n)]
    for w, v in WORDNUM.items():
        if w in n: nums.append(v)
    return tuple(nums)


def choice_key(name, pkg, date):
    """Name class, then the last commit touching the package (newest wins), then version numbers."""
    return (name_class(pkg), date or '', version(pkg))


def roster(rows, h, exclude=(), dates=None):
    dates = dates or {}
    by_repo = defaultdict(list)
    for name, package, classdir, repo, commit in (r[:5] for r in rows):
        if bs.JUNK.search(package) and 'final' not in package.lower():
            continue
        by_repo[repo].append((name, package))
    # two selection rules disagree on about a third of repos (names vs last-commit dates); neither is reliable alone,
    # so both picks enter the field (deduplicated by content hash) and the ladder rates them
    by_hash = defaultdict(list)
    for repo, c in by_repo.items():
        picks = {max(c, key=lambda x: choice_key(x[0], x[1], dates.get(x[0]))), max(c, key=lambda x: bs.score(x[1]))}
        for name, package in picks:
            if (repo, name) not in by_hash[h.get(name, name)]:
                by_hash[h.get(name, name)].append((repo, name))
    field = []
    for hsh, members in by_hash.items():
        members.sort(key=lambda m: (m[0].startswith('battlecode-archive_'), m[0]))
        repo, name = members[0]
        aka = sorted({m[0] for m in members[1:]} - {repo})
        if name in exclude:
            continue
        field.append((name, repo, hsh, aka, len(by_repo[repo])))
    return sorted(field)


def main():
    rows, h, d = load()
    excl_file = TOOLS / 'field-exclude.txt'
    exclude = {l.split()[0] for l in excl_file.read_text().splitlines() if l.strip() and not l.startswith('#')} \
        if excl_file.exists() else set()
    field = roster(rows, h, exclude, d)
    text = '\n'.join(f[0] for f in field) + '\n'
    if '--check' in sys.argv:
        sys.exit(0 if (TOOLS / 'field.txt').read_text() == text else 1)
    (TOOLS / 'field.txt').write_text(text)
    for name, repo, hsh, aka, ncand in field:
        print(f"{name:46s} {repo:50s} {hsh}  cand={ncand:<3d} {'= ' + ', '.join(aka) if aka else ''}")
    print(f'{len(field)} entrants -> tools/field.txt')


if __name__ == '__main__':
    main()
