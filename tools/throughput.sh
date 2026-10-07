#!/usr/bin/env bash
# Measure game throughput on this machine: K concurrent games of A vs B on MAP, wall time per batch.
#   tools/throughput.sh <teamA> <teamB> <map> "1 4 8"
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO/tools/lib.sh"
A="$1" B="$2" MAP="$3"; KS="${4:-1 4 8}"
OUT="${TMPDIR:-/tmp}/tp.$$"; mkdir -p "$OUT"
for k in $KS; do
  t0=$(date +%s.%N)
  for i in $(seq 1 "$k"); do
    ( GAME_SEED=$((1000 + i)) run_game "$A" "$B" "$MAP" "$OUT/g$k-$i.bc23" > "$OUT/g$k-$i.log" 2>&1 ) &
  done
  wait
  t1=$(date +%s.%N)
  res=$(for i in $(seq 1 "$k"); do parse_result "$(cat "$OUT/g$k-$i.log")" | cut -d' ' -f2-3; done | sort | uniq -c | tr '\n' ';')
  awk -v k="$k" -v a="$t0" -v b="$t1" -v r="$res" 'BEGIN{w=b-a; printf "K=%d wall=%.1fs per-game=%.1fs games/min=%.2f  %s\n", k, w, w/k, 60*k/w, r}'
done
du -sh "$OUT" | cut -f1 | sed 's/^/replays+logs: /'
rm -rf "$OUT"
