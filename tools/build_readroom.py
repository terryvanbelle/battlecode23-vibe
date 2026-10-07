#!/usr/bin/env python3
"""Build the filtered reading room: every .md/.txt under each prior repo, with forbidden-year blocks removed."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filter_year import filt, TAG
V = '/home/terryvanbelle/projects/vibe'
SRC = {'bc22': 'reference/battlecode22-vibe', 'bc26': 'reference/battlecode26-vibe', 'bc25': '2025',
       'bc21': 'reference/battlecode21-vibe', 'bc20': '2020', 'bc24': '2024', 'bcenv': 'reference/bcenv',
       'advice': 'reference/battlecode-vibe'}
SKIP = {'.git', '.venv', 'node_modules', 'gauntlet', 'matches', 'build', 'site-packages', '__pycache__'}
RR = f'{V}/reference/readroom-no2023'
tot = hits = 0
for k, s in SRC.items():
    root = f'{V}/{s}'
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in files:
            if not (f.endswith('.md') or f.endswith('.txt')):
                continue
            p = os.path.join(d, f)
            if os.path.getsize(p) > 2_000_000:
                continue
            out = os.path.join(RR, k, os.path.relpath(p, root))
            if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(p):
                tot += 1
                continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            try:
                t = filt(open(p, errors='replace').read())
            except Exception as e:
                print('ERR', p, e)
                continue
            open(out, 'w').write(t)
            tot += 1
            hits += len(TAG.findall(t))
print(f'files {tot}, residual hits {hits}')
