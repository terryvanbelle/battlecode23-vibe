#!/usr/bin/env bash
# Controlled own actors only. Compilation is separate from the five native full-loop fixtures.
set -euo pipefail
umask 077
if [[ ${BLIND_FULL_BOUNDED:-} != 1 ]]; then
  exec timeout --signal=TERM --kill-after=5s 170s env BLIND_FULL_BOUNDED=1 bash "$0" "$@"
fi
BLIND_FULL_HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BLIND_FULL_REPO=${1:?usage: run.sh [--prepare] REPO FRESH_OUTPUT}
BLIND_FULL_PREPARE=false
if [[ $BLIND_FULL_REPO == --prepare ]]; then BLIND_FULL_PREPARE=true; shift; BLIND_FULL_REPO=${1:?repo}; fi
BLIND_FULL_OUT=${2:?fresh output directory}
BLIND_FULL_REPO=$(cd "$BLIND_FULL_REPO" && pwd)
[[ ! -e $BLIND_FULL_OUT ]]
[[ $(hostname -s) == battlecode-dev ]] || { echo 'official full-loop fixture requires battlecode-dev' >&2; exit 3; }
BLIND_FULL_JAR="$BLIND_FULL_REPO/engine/battlecode23-3.0.15.jar"
printf '%s  %s\n' 5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a "$BLIND_FULL_JAR" | sha256sum --check --status
BLIND_FULL_JDK=${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}
mkdir -m 700 "$BLIND_FULL_OUT"
"$BLIND_FULL_JDK/bin/java" -version > "$BLIND_FULL_OUT/jdk.txt" 2>&1
grep -q 'version "1\.8\.' "$BLIND_FULL_OUT/jdk.txt"
python3 "$BLIND_FULL_HERE/prepare.py" "$BLIND_FULL_OUT/prepared" > "$BLIND_FULL_OUT/source-provenance.json"
mkdir "$BLIND_FULL_OUT/host" "$BLIND_FULL_OUT/base-classes"
find "$BLIND_FULL_OUT/prepared/baseline-source" -name '*.java' -type f -print | sort > "$BLIND_FULL_OUT/base.list"
"$BLIND_FULL_JDK/bin/javac" -source 8 -target 8 -encoding UTF-8 -nowarn -proc:none -cp "$BLIND_FULL_JAR" -d "$BLIND_FULL_OUT/base-classes" @"$BLIND_FULL_OUT/base.list"
for BLIND_FULL_PERIOD in 0 4 2 1; do
  mkdir "$BLIND_FULL_OUT/prepared/period-$BLIND_FULL_PERIOD/classes"
  find "$BLIND_FULL_OUT/prepared/period-$BLIND_FULL_PERIOD/source" -name '*.java' ! -name BlindCalibration.java -type f -print | sort > "$BLIND_FULL_OUT/period-$BLIND_FULL_PERIOD.list"
  "$BLIND_FULL_JDK/bin/javac" -source 8 -target 8 -encoding UTF-8 -nowarn -proc:none -cp "$BLIND_FULL_JAR" -d "$BLIND_FULL_OUT/prepared/period-$BLIND_FULL_PERIOD/classes" @"$BLIND_FULL_OUT/period-$BLIND_FULL_PERIOD.list"
done
"$BLIND_FULL_JDK/bin/javac" -source 8 -target 8 -encoding UTF-8 -nowarn -proc:none -cp "$BLIND_FULL_JAR" -d "$BLIND_FULL_OUT/host" "$BLIND_FULL_HERE/ControlledBlindGame.java"
python3 "$BLIND_FULL_HERE/test_summary.py" > "$BLIND_FULL_OUT/parser-tests.txt" 2>&1
if [[ $BLIND_FULL_PREPARE == true ]]; then printf 'official blind full-loop preparation: %s\n' "$BLIND_FULL_OUT";exit 0;fi
BLIND_FULL_RUN_DEADLINE=$(( $(date +%s) + 140 ))
mkdir -p /tmp/bc23-game-slots
BLIND_FULL_LOCKED=false
BLIND_FULL_SLOT_DEADLINE=$(( $(date +%s) + 45 ))
while [[ $BLIND_FULL_LOCKED == false ]]; do
  for BLIND_FULL_SLOT in 1 2 3 4 5; do
    exec 9>"/tmp/bc23-game-slots/slot.$BLIND_FULL_SLOT"
    if flock -n 9; then BLIND_FULL_LOCKED=true;break;fi
    exec 9>&-
  done
  if [[ $BLIND_FULL_LOCKED == false ]]; then
    [[ $(date +%s) -lt $BLIND_FULL_SLOT_DEADLINE ]] || { echo 'shared native fixture slot unavailable' >&2;exit 5; }
    sleep 1
  fi
done
blind_full_arm() {
  local blind_full_name=$1 blind_full_package=$2 blind_full_classes=$3 blind_full_remaining
  blind_full_remaining=$(( BLIND_FULL_RUN_DEADLINE - $(date +%s) ))
  [[ $blind_full_remaining -gt 0 ]]
  timeout --signal=TERM --kill-after=5s "${blind_full_remaining}s" "$BLIND_FULL_JDK/bin/java" -Xmx512m -XX:+UseSerialGC \
    -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false -cp "$BLIND_FULL_OUT/host:$BLIND_FULL_JAR" \
    ControlledBlindGame "$blind_full_package" "$blind_full_classes" "$BLIND_FULL_OUT/$blind_full_name" "$blind_full_name" \
    > "$BLIND_FULL_OUT/$blind_full_name.stdout.log" 2> "$BLIND_FULL_OUT/$blind_full_name.stderr.log"
}
blind_full_arm base c_mend2 "$BLIND_FULL_OUT/base-classes"
blind_full_arm 0 c_blind1 "$BLIND_FULL_OUT/prepared/period-0/classes"
python3 "$BLIND_FULL_HERE/summarize.py" --zero "$BLIND_FULL_OUT/base" "$BLIND_FULL_OUT/0" --output "$BLIND_FULL_OUT/zero-gate.json"
# No active arm starts unless exact live zero identity passes.
for BLIND_FULL_PERIOD in 4 2 1; do
  blind_full_arm "$BLIND_FULL_PERIOD" c_blind1 "$BLIND_FULL_OUT/prepared/period-$BLIND_FULL_PERIOD/classes"
done
python3 "$BLIND_FULL_HERE/summarize.py" --all "$BLIND_FULL_OUT" --output "$BLIND_FULL_OUT/result.json"
printf 'official blind controlled full-loop outputs: %s\n' "$BLIND_FULL_OUT"
