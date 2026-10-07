#!/usr/bin/env python3
"""Discover public Battlecode 2023 bot repositories on GitHub, by search metadata only.

    tools/bench-discover.py [--out FILE]

Never reads repository contents: repository search (name/description/topics/creation date) and code search for
2023-only API names return repository identities, which are written as a TSV:
    full_name  source_query  created_at  pushed_at  size_kb  fork
Classification (does a repo really hold a 2023 bot?) is done later by tools/bench-fetch.sh, which counts files that use
2023-only API names without displaying them.
"""
import json, subprocess, sys, time
from pathlib import Path

OUT = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else \
    Path.home() / 'projects/vibe/bc23-benchmarks/_discovery.tsv'

REPO_QUERIES = [
    'battlecode23', 'battlecode2023', 'battlecode 2023', 'battlecode-2023', 'bc23', 'bc2023', 'battlecode tempest',
    'battlecode23-scaffold', 'battlecode 23', 'battle code 2023', 'mit battlecode 2023', 'battlecode_2023',
    'topic:battlecode2023', 'topic:battlecode-2023', 'topic:battlecode23',
]
# season window: game release 2023-01-09, archive 2023-02-06; repos are often created a little before or after
DATE_QUERIES = [f'battlecode created:{a}..{b}' for a, b in [
    ('2022-12-15', '2023-01-08'), ('2023-01-09', '2023-01-15'), ('2023-01-16', '2023-01-22'),
    ('2023-01-23', '2023-01-31'), ('2023-02-01', '2023-02-15'), ('2023-02-16', '2023-04-30'),
    ('2023-05-01', '2023-12-31')]] + [f'battlecode pushed:{a}..{b}' for a, b in [
    ('2023-01-09', '2023-01-14'), ('2023-01-15', '2023-01-21'), ('2023-01-22', '2023-01-28'),
    ('2023-01-29', '2023-02-04'), ('2023-02-05', '2023-02-28'), ('2023-03-01', '2023-06-30')]] + [
    'battlecode in:readme 2023', 'tempest in:readme battlecode', 'battlecode language:java created:2023-01-01..2023-02-28']
FORK_ROOTS = ['battlecode/battlecode23-scaffold']
CODE_QUERIES = [  # 2023-only API names (Tempest); language:java
    '"RobotType.LAUNCHER"', '"RobotType.CARRIER"', '"RobotType.AMPLIFIER"', '"ResourceType.ADAMANTIUM"',
    '"ResourceType.ELIXIR"', '"Anchor.STANDARD"', '"Anchor.ACCELERATING"', 'senseNearbyWells', 'WellInfo battlecode',
    'senseNearbyIslands', 'placeAnchor', 'takeAnchor', '"RobotType.DESTABILIZER"', '"RobotType.BOOSTER"',
    'battlecode23', 'canCollectResource',
]


def gh(path, params):
    args = ['gh', 'api', '-X', 'GET', path] + sum([['-f', f'{k}={v}'] for k, v in params.items()], [])
    for attempt in range(6):
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout)
        if 'rate limit' in (r.stderr + r.stdout).lower() or '403' in r.stderr or '429' in r.stderr:
            time.sleep(65)
            continue
        sys.stderr.write(f'!! {path} {params}: {r.stderr.strip()[:200]}\n')
        return None
    return None


def main():
    rows = {}

    def add(item, q):
        fn = item['full_name']
        if fn not in rows:
            rows[fn] = [fn, q, item.get('created_at', ''), item.get('pushed_at', ''), str(item.get('size', '')),
                        str(item.get('fork', ''))]
    for q in REPO_QUERIES + DATE_QUERIES:
        for page in range(1, 11):
            d = gh('search/repositories', {'q': q, 'per_page': 100, 'page': page})
            time.sleep(2.5)
            if not d or not d.get('items'):
                break
            for it in d['items']:
                add(it, q)
            if len(d['items']) < 100:
                break
        print(f'repo  {q!r}: total {len(rows)}', file=sys.stderr)
    def forks(root, depth):
        for page in range(1, 50):
            d = gh(f'repos/{root}/forks', {'per_page': 100, 'page': page})
            time.sleep(1)
            if not d:
                break
            for it in d:
                add(it, 'fork:' + root)
                if depth < 2 and it.get('forks_count', 0) > 0:
                    forks(it['full_name'], depth + 1)
            if len(d) < 100:
                break
    for r in FORK_ROOTS:
        forks(r, 1)
        print(f'forks {r}: total {len(rows)}', file=sys.stderr)
    for q in CODE_QUERIES if '--code' in sys.argv else []:
        for page in range(1, 11):
            d = gh('search/code', {'q': q + ' language:java', 'per_page': 100, 'page': page})
            time.sleep(7)
            if not d or not d.get('items'):
                break
            for it in d['items']:
                add(it['repository'], 'code:' + q)
            if len(d['items']) < 100:
                break
        print(f'code  {q!r}: total {len(rows)}', file=sys.stderr)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        f.write('full_name\tsource_query\tcreated_at\tpushed_at\tsize_kb\tfork\n')
        for r in sorted(rows.values()):
            f.write('\t'.join(r) + '\n')
    print(f'{len(rows)} candidate repositories -> {OUT}')


if __name__ == '__main__':
    main()
