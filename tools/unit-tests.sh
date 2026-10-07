#!/usr/bin/env bash
# One command for the bot and the apparatus (run after EVERY change to the bot or any tool):
#   1. compile every bot package under src/ (a compile error fails the suite);
#   2. compile test/bot/*Test.java against the bot and run each *Test main (no JUnit in the engine jar);
#   3. python tool tests (tools/test_tools.py: synthetic inputs and committed fixtures).
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; source "$REPO/tools/lib.sh"
fail=0
OUT="$REPO/build/tests"; rm -rf "$OUT"; mkdir -p "$OUT"
CLASSES="$OUT/bots" bash "$REPO/tools/build.sh" > /dev/null || { echo "unit-tests: bot compile FAILED"; exit 1; }
echo "bots: compiled $(ls "$REPO/src" | wc -l) packages"
if ls "$REPO"/test/bot/*Test.java >/dev/null 2>&1; then
  javac -nowarn -encoding UTF-8 -d "$OUT/tests" -cp "$(engine_cp):$OUT/bots" "$REPO"/test/bot/*.java
  for t in "$REPO"/test/bot/*Test.java; do
    cls="$(sed -n 's/^package \(.*\);/\1/p' "$t" | head -1)"; cls="${cls:+$cls.}$(basename "$t" .java)"
    java -cp "$OUT/tests:$OUT/bots:$(engine_cp)" "$cls" || fail=1
  done
fi
python3 "$REPO/tools/test_tools.py" 2>&1 | tail -1 || fail=1
python3 "$REPO/tools/test_tools.py" > /dev/null 2>&1 || fail=1
[ $fail = 0 ] && echo "unit-tests: PASS" || { echo "unit-tests: FAIL"; exit 1; }
