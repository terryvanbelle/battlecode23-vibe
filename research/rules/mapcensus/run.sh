#!/usr/bin/env bash
# Rebuild and rerun the Battlecode 2023 map census (writes maps.tsv next to this script).
set -euo pipefail
cd "$(dirname "$0")"
JDK=~/jdk/jdk8u504-b01/bin
JAR=/home/terryvanbelle/projects/vibe/2023/engine/battlecode23-3.0.15.jar
CONSTS=/home/terryvanbelle/projects/vibe/reference/battlecode23/client/visualizer/src/constants.ts
mkdir -p classes
"$JDK/javac" -cp "$JAR" -d classes MapCensus.java
"$JDK/java" -Xmx300m -cp "classes:$JAR" MapCensus "$CONSTS" > maps.tsv
wc -l maps.tsv
