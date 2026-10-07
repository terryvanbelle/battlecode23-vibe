#!/usr/bin/env bash
# Security scan of external benchmark sources BEFORE first compile (owner rule: their code is read only to rule out a
# security risk). Prints, per repo, COUNTS of risky patterns; no source is displayed unless --show is given for one
# repo, in which case only the matching lines (not their context) are printed so a hit can be ruled in or out.
#
#   tools/bench-scan.sh                # all repos under $BENCH_ROOT -> $BENCH_ROOT/_scan.tsv, summary to stdout
#   tools/bench-scan.sh --show <dir>   # matching lines of one repo
#
# Context: bots run inside the engine's instrumented sandbox, which rejects java.io file access, networking,
# reflection, threads and System.exit at load time (the robot explodes), and we compile with javac -proc:none (no
# annotation processors, so no code runs at compile time), and only *.java is ever compiled. Gradle/Kotlin/Scala files
# are never executed. The scan is a second line of defence and a record.
set -uo pipefail
BENCH_ROOT="${BENCH_ROOT:-$HOME/projects/vibe/bc23-benchmarks}"
PAT='Runtime\.getRuntime|ProcessBuilder|\.exec\(|java\.net\.|Socket|new URL\(|java\.io\.File|FileWriter|FileOutputStream|FileInputStream|java\.nio\.file|System\.exit|System\.setProperty|System\.getenv|java\.lang\.reflect|setAccessible|getDeclared(Method|Field)|Class\.forName|ClassLoader|sun\.misc\.Unsafe|\bnative\b|new Thread\(|ExecutorService|javax\.script|ScriptEngine'
if [ "${1:-}" = --show ]; then
  grep -rnoE --include='*.java' "$PAT" "$2" | head -100
  exit 0
fi
OUT="$BENCH_ROOT/_scan.tsv"
printf 'repo\tjava_files\trisky_hits\tpatterns\n' > "$OUT"
for d in "$BENCH_ROOT"/*/; do
  d=${d%/}; n=$(basename "$d"); case "$n" in _*) continue;; esac
  nj=$(find "$d" -name '*.java' | wc -l)
  hits=$(grep -rhoE --include='*.java' "$PAT" "$d" 2>/dev/null | sort | uniq -c | awk '{printf "%s:%s ", $2, $1}')
  nh=$(grep -rhoE --include='*.java' "$PAT" "$d" 2>/dev/null | wc -l)
  printf '%s\t%s\t%s\t%s\n' "$n" "$nj" "$nh" "$hits" >> "$OUT"
done
echo "scanned $(($(wc -l < "$OUT") - 1)) repos; with hits: $(awk -F'\t' 'NR>1 && $3>0' "$OUT" | wc -l)"
awk -F'\t' 'NR>1 && $3>0 {printf "  %-50s %s\n", $1, $4}' "$OUT"
