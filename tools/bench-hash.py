#!/usr/bin/env python3
"""Content hash of every compiled benchmark package (no source is read): sha1 over the sorted (relative path, bytes) of
every .class file under classdir/<package path>. Identical bots published in several repos (team repo + archive copy,
forks) get the same hash, so the ladder field keeps one of them.

    tools/bench-hash.py [manifest.tsv]   -> writes <bench_root>/hashes.tsv: name  hash  n_classes
"""
import hashlib, os, sys
from pathlib import Path

man = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / 'projects/vibe/bc23-benchmarks/manifest.tsv'


def pkg_hash(classdir, package):
    root = Path(classdir) / package.replace('.', '/')
    h = hashlib.sha1()
    n = 0
    for p in sorted(root.rglob('*.class')):
        h.update(str(p.relative_to(root)).encode())
        h.update(p.read_bytes())
        n += 1
    return h.hexdigest()[:12], n


def main():
    rows = [l.split('\t') for l in man.read_text().splitlines()[1:] if l.strip()]
    out = ['name\thash\tn_classes']
    for name, package, classdir, repo, commit in (r[:5] for r in rows):
        hsh, n = pkg_hash(classdir, package)
        out.append(f'{name}\t{hsh}\t{n}')
    (man.parent / 'hashes.tsv').write_text('\n'.join(out) + '\n')
    print(f'{len(rows)} packages hashed -> {man.parent / "hashes.tsv"}')


if __name__ == '__main__':
    main()
