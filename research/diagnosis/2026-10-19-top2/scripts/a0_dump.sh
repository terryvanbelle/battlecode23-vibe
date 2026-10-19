#!/usr/bin/env bash
# Analyst 0: regenerate the per-turn (--sa) dumps of the 18 maxwelljones14 games, both teams, one dump at a time
# machine-wide (flock), 500 MB heap. About 3.5 minutes on the driver. Output: $A0_SA/<match>g<game><side>/sa_{L,HQ,C}.csv
set -euo pipefail
REPO=/home/terryvanbelle/projects/vibe/2023
SP=/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad
OUT=${A0_SA:-$SP/top2/a0/sa}
for m in 9911 9913 9918 9924 9928 9930; do for g in 0 1 2; do for t in A B; do
  flock "$SP/dump.lock" env DUMP_XMX=500m "$REPO/tools/replay-dump.sh" "$REPO/build/top2/replays/$m.bc23" \
    --sa --team "$t" --game "$g" --match "$m" --out "$OUT/${m}g${g}$t" 2>&1 | tail -1
done; done; done
