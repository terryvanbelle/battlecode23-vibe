#!/usr/bin/env bash
# Analyst 2: per-turn (--sa) dumps of match 10060 (IslandHopping, Maze, SweetDreams), both teams, which the other
# analysts' dump dirs lack. One dump at a time machine-wide (flock), 500 MB heap. Output: $A2_SA_OWN/<m>g<g><side>/
set -euo pipefail
REPO=/home/terryvanbelle/projects/vibe/2023
SP=/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad
OUT=${A2_SA_OWN:-$SP/top2/a2/sa}
for m in 10060; do for g in 0 1 2; do for t in A B; do
  flock "$SP/dump.lock" env DUMP_XMX=500m "$REPO/tools/replay-dump.sh" "$REPO/build/top2/replays/$m.bc23" \
    --sa --team "$t" --game "$g" --match "$m" --out "$OUT/${m}g${g}$t" 2>&1 | tail -1
done; done; done
