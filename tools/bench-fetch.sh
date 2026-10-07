#!/usr/bin/env bash
# Fetch and classify candidate benchmark repositories WITHOUT reading their code.
#
#   tools/bench-fetch.sh [discovery.tsv]
#
# For each candidate (full_name in column 1): a shallow, blob-filtered, sparse clone of *.java and build metadata only
# into $BENCH_ROOT/<owner>_<repo>/. Classification counts .java files that use 2023-only API names (counts only, no
# content is displayed). Repos with zero such files are deleted. Writes $BENCH_ROOT/_classify.tsv:
#   dir  full_name  files_2023  files_java  commit  verdict
set -uo pipefail
BENCH_ROOT="${BENCH_ROOT:-$HOME/projects/vibe/bc23-benchmarks}"
DISC="${1:-$BENCH_ROOT/_discovery.tsv}"
OUT="$BENCH_ROOT/_classify.tsv"
JOBS="${JOBS:-4}"
API23='RobotType\.(LAUNCHER|CARRIER|AMPLIFIER|BOOSTER|DESTABILIZER)|ResourceType\.(ADAMANTIUM|MANA|ELIXIR)|Anchor\.(STANDARD|ACCELERATING)|WellInfo|senseNearbyWells|placeAnchor|takeAnchor|senseNearbyIslands'
mkdir -p "$BENCH_ROOT"
[ -f "$OUT" ] || printf 'dir\tfull_name\tfiles_2023\tfiles_java\tcommit\tverdict\n' > "$OUT"

fetch_one () {
  local fn="$1" dir; dir="$BENCH_ROOT/$(echo "$fn" | tr '/' '_')"
  grep -q -P "\t$fn\t" "$OUT" && return 0                        # already classified
  rm -rf "$dir"
  if ! GIT_TERMINAL_PROMPT=0 timeout 300 git clone -q --depth 1 --filter=blob:none --no-checkout \
        "https://github.com/$fn.git" "$dir" 2>/dev/null; then
    printf '%s\t%s\t0\t0\t-\tclone-failed\n' "$(basename "$dir")" "$fn" >> "$OUT"; rm -rf "$dir"; return 0
  fi
  git -C "$dir" sparse-checkout set --no-cone '*.java' '*.scala' '*.kt' 'version.txt' '*.gradle' 'gradle.properties' \
    >/dev/null 2>&1
  timeout 600 git -C "$dir" checkout -q 2>/dev/null
  local nj n23 commit
  nj=$(find "$dir" -name '*.java' -not -path '*/.git/*' | wc -l)
  n23=$(grep -rlE --include='*.java' "$API23" "$dir" 2>/dev/null | wc -l)
  commit=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo '?')
  if [ "$n23" -gt 0 ]; then
    rm -rf "$dir/.git"
    printf '%s\t%s\t%s\t%s\t%s\tbc23\n' "$(basename "$dir")" "$fn" "$n23" "$nj" "$commit" >> "$OUT"
  else
    rm -rf "$dir"
    printf '%s\t%s\t0\t%s\t%s\tnot-2023\n' "$(basename "$dir")" "$fn" "$nj" "$commit" >> "$OUT"
  fi
}
export -f fetch_one; export BENCH_ROOT OUT API23
tail -n +2 "$DISC" | cut -f1 | sort -u | xargs -P "$JOBS" -I{} bash -c 'fetch_one "$@"' _ {}
echo "classified: $(($(wc -l < "$OUT") - 1)) repos; bc23: $(grep -c $'\tbc23$' "$OUT"); disk: $(du -sh "$BENCH_ROOT" | cut -f1)"
