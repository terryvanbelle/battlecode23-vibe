#!/usr/bin/env bash
# Preparation only. Run on battlecode-dev; no downloads, network, git writes, or player sandbox.
set -euo pipefail
BC23_PROBE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [[ ${1:-} != --bounded-child ]]; then
  command -v timeout >/dev/null
  export BC23_PROBE_BOUND=1
  exec timeout --signal=TERM --kill-after=5s 170s bash "$BC23_PROBE_DIR/run.sh" --bounded-child
fi
[[ ${BC23_PROBE_BOUND:-} == 1 ]] || { echo 'blind probe: use the bounded run.sh entry point' >&2; exit 1; }
if [[ $(hostname -s) != battlecode-dev ]]; then
  echo 'blind probe: run only on battlecode-dev' >&2
  exit 1
fi
BC23_PROBE_REPO=${BC23_PROBE_REPO:-/home/terryvanbelle/projects/vibe/2023}
BC23_PROBE_JDK=${BC23_PROBE_JDK:-${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}}
BC23_PROBE_JAR="$BC23_PROBE_REPO/engine/battlecode23-3.0.15.jar"
BC23_PROBE_PIN=5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a
[[ -x "$BC23_PROBE_JDK/bin/java" && -x "$BC23_PROBE_JDK/bin/javac" ]]
[[ -f "$BC23_PROBE_JAR" ]]
printf '%s  %s\n' "$BC23_PROBE_PIN" "$BC23_PROBE_JAR" | sha256sum --check --status
BC23_PROBE_OUT=$(mktemp -d "$BC23_PROBE_DIR/run-XXXXXX")
mkdir "$BC23_PROBE_OUT/classes"
printf 'blind probe: official release 3.0.15; native host correctness; instruction metering absent\n'
printf 'blind probe: isolated output %s\n' "$BC23_PROBE_OUT"
sha256sum "$BC23_PROBE_DIR/NativeBlindProbe.java" > "$BC23_PROBE_OUT/source.sha256"
"$BC23_PROBE_JDK/bin/java" -version > "$BC23_PROBE_OUT/jdk.txt" 2>&1
grep -q 'version "1\.8\.' "$BC23_PROBE_OUT/jdk.txt"
"$BC23_PROBE_JDK/bin/javac" -source 8 -target 8 -encoding UTF-8 -nowarn \
  -cp "$BC23_PROBE_JAR" -d "$BC23_PROBE_OUT/classes" "$BC23_PROBE_DIR/NativeBlindProbe.java"
"$BC23_PROBE_JDK/bin/java" -Xmx256m -cp "$BC23_PROBE_OUT/classes:$BC23_PROBE_JAR" NativeBlindProbe \
  | tee "$BC23_PROBE_OUT/results.jsonl"
grep -q '"summary":"PASS"' "$BC23_PROBE_OUT/results.jsonl"
