#!/usr/bin/env bash
# One command for the bot and the apparatus (run after EVERY change to the bot or any tool):
#   1. compile every bot package under src/ (a compile error fails the suite);
#   2. compile test/bot/*Test.java against the bot and run each *Test main (no JUnit in the engine jar);
#   3. python tool tests (tools/test_tools.py: synthetic inputs and committed fixtures; tools/test_match_report.py:
#      match reports, the contest.py report hook, telemetry_query, the basics/delivery guards);
#   4. the replica tests (test/replica) and the galaxy frontend build checks (test/galaxy/test_frontend.py);
#   5. the galaxy back-end tests (test/galaxy/test_galaxy.py: stand-ins, saturn, relay, deploy renderers);
#   6. the galaxy operator tools (test/galaxy/test_field_tools.py: field seeding, activity, results, snapshot).
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; source "$REPO/tools/lib.sh"
# one run at a time: overlapping runs shared build directories and raced (a predecessor project's lesson)
mkdir -p "$REPO/build"; exec 9>"$REPO/build/.unit-tests.lock"; flock -w 1800 9 || { echo "unit-tests: lock busy"; exit 1; }
fail=0
OUT="$REPO/build/tests"; rm -rf "$OUT"; mkdir -p "$OUT"
CLASSES="$OUT/bots" bash "$REPO/tools/build.sh" > /dev/null || { echo "unit-tests: bot compile FAILED"; exit 1; }
echo "bots: compiled $(ls "$REPO/src" | wc -l) packages"
if ls "$REPO"/test/bot/*Test.java >/dev/null 2>&1; then
  mkdir -p "$OUT/tests"; javac -nowarn -encoding UTF-8 -d "$OUT/tests" -cp "$(engine_cp):$OUT/bots" "$REPO"/test/bot/*.java
  for t in "$REPO"/test/bot/*Test.java; do
    cls="$(sed -n 's/^package \(.*\);/\1/p' "$t" | head -1)"; cls="${cls:+$cls.}$(basename "$t" .java)"
    java -cp "$OUT/tests:$OUT/bots:$(engine_cp)" "$cls" || fail=1
  done
fi
tt=$(python3 "$REPO/tools/test_tools.py" 2>&1) || fail=1
printf '%s\n' "$tt" | tail -1
mt=$(python3 "$REPO/tools/test_match_report.py" 2>&1) && echo "match reports: $(printf '%s\n' "$mt" | grep -E '^(Ran|OK)' | tr '\n' ' ')" || { printf '%s\n' "$mt" | tail -40; fail=1; }
rt=$(python3 "$REPO/test/replica/test_replica.py" 2>&1) && echo "replica: $(printf '%s\n' "$rt" | grep -E '^(Ran|OK)' | tr '\n' ' ')" || { printf '%s\n' "$rt" | tail -40; fail=1; }
gt=$(python3 "$REPO/test/galaxy/test_frontend.py" 2>&1) && echo "galaxy frontend: $(printf '%s\n' "$gt" | grep -E '^(Ran|OK)' | tr '\n' ' ')" || { printf '%s\n' "$gt" | tail -40; fail=1; }
bt=$(python3 "$REPO/test/galaxy/test_galaxy.py" 2>&1) && echo "galaxy backend: $(printf '%s\n' "$bt" | grep -E '^(Ran|OK)' | tr '\n' ' ')" || { printf '%s\n' "$bt" | tail -40; fail=1; }
ft=$(python3 "$REPO/test/galaxy/test_field_tools.py" 2>&1) && echo "galaxy tools: $(printf '%s\n' "$ft" | grep -E '^(Ran|OK)' | tr '\n' ' ')" || { printf '%s\n' "$ft" | tail -40; fail=1; }
[ $fail = 0 ] && echo "unit-tests: PASS" || { echo "unit-tests: FAIL"; exit 1; }
