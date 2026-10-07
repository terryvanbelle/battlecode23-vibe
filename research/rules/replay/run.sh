#!/usr/bin/env bash
# research/rules/replay/run.sh [replay.bc23] [rounds, e.g. 1,100,500,2000]
# Compiles ReplayReader against the official engine jar (schema classes + flatbuffers runtime live inside it) and runs it.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JDK="${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}"
JAR="$HERE/../../../engine/battlecode23-3.0.15.jar"
mkdir -p "$HERE/classes"
"$JDK/bin/javac" -nowarn -source 8 -target 8 -cp "$JAR" -d "$HERE/classes" "$HERE/ReplayReader.java"
exec "$JDK/bin/java" -Xmx512m -cp "$HERE/classes:$JAR" ReplayReader \
  "${1:-$HERE/../../../matches/test1.bc23}" "${2:-1,100,500,2000}"
