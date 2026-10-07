#!/usr/bin/env bash
# Shared helpers: JDK, engine classpath, one-game runner, result parsing. Source this; do not execute.
# Layout (identical on the driver and the VM):
#   ~/jdk/jdk8u504-b01                 JDK 8 (the engine and bots are Java 8)
#   ~/projects/vibe/2023               this repo; engine/ staged by tools/get-engine.sh (gitignored)
#   ~/projects/vibe/bc23-benchmarks    external bots (never read; compiled by tools/bench-compile.sh)
REPO="${REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
export JAVA_HOME="${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}"
export PATH="$JAVA_HOME/bin:$PATH"
ENGINE_DIR="$REPO/engine"
ENGINE_VER=3.0.15
ENGINE_SHA256=5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a
BENCH_ROOT="${BENCH_ROOT:-$HOME/projects/vibe/bc23-benchmarks}"
BENCH_CLASSES="${BENCH_CLASSES:-$BENCH_ROOT/_classes}"
CLASSES="${CLASSES:-$REPO/build/classes}"          # our bots (src/<package>), compiled by tools/build.sh

# engine classpath: the seed patch first, then the official fat jar
engine_cp () {
  local jar="$ENGINE_DIR/battlecode23-$ENGINE_VER.jar"
  [ -f "$jar" ] || { echo "!! no engine; run tools/get-engine.sh" >&2; return 1; }
  if [ -d "$ENGINE_DIR/patch/battlecode" ]; then echo "$ENGINE_DIR/patch:$jar"; else echo "$jar"; fi
}

# Where a team's classes live: our class tree, else a benchmark's class dir (manifest name owner.package -> dir).
team_url () {
  local t="$1"
  if [ -d "$CLASSES/$t" ]; then echo "$CLASSES"; return 0; fi
  if [ -f "$BENCH_ROOT/manifest.tsv" ]; then
    local d; d=$(awk -F'\t' -v n="$t" '$1==n {print $3; exit}' "$BENCH_ROOT/manifest.tsv")
    if [ -n "$d" ]; then echo "$d"; return 0; fi
  fi
  echo "!! no compiled classes for team $t" >&2; return 1
}

# team_pkg <team>: the java package the engine loads for a team (benchmarks are named owner.package)
team_pkg () {
  local t="$1"
  if [ -d "$CLASSES/$t" ]; then echo "$t"; return 0; fi
  awk -F'\t' -v n="$t" '$1==n {print $2; exit}' "$BENCH_ROOT/manifest.tsv"
}

# run_game <teamA> <teamB> <map> <replay> [extra -D flags]  -> engine stdout
#   GAME_SEED=<int> overrides the map seed (engine/patch); unset = official behaviour.
#   SHOW_LOGS=1 sends robot System.out to stdout (our @tag diagnostic lines). GAME_OPTS: more -D flags.
run_game () {
  local TA="$1" TB="$2" MAP="$3" REPLAY="$4"; shift 4
  local UA UB PA PB
  UA="$(team_url "$TA")" || return 1; UB="$(team_url "$TB")" || return 1
  PA="$(team_pkg "$TA")"; PB="$(team_pkg "$TB")"
  timeout "${GAME_TIMEOUT:-1800}" java -Xmx${GAME_XMX:-768m} -XX:+UseSerialGC -XX:ReservedCodeCacheSize=256m \
    -Dbc.server.mode=headless -Dbc.server.websocket=false -Dbc.server.debug=false -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false \
    -Dbc.server.validate-maps=false -Dbc.engine.show-indicators=true \
    -Dbc.server.robot-player-to-system-out=${SHOW_LOGS:-false} \
    -Dbc.server.robot-player-replay-file-per-team-limit-bytes=${LOG_LIMIT:-4000000} \
    ${CUSTOM_MAPS:+-Dbc.game.map-path=$CUSTOM_MAPS} \
    -Dbc.game.team-a="$TA" -Dbc.game.team-b="$TB" \
    -Dbc.game.team-a.package="$PA" -Dbc.game.team-b.package="$PB" \
    -Dbc.game.team-a.url="$UA" -Dbc.game.team-b.url="$UB" \
    -Dbc.game.maps="$MAP" -Dbc.server.save-file="$REPLAY" ${GAME_SEED:+-Dbc.game.seed=$GAME_SEED} "$@" ${GAME_OPTS:-} \
    -cp "$(engine_cp)" battlecode.server.Main -c=- < /dev/null
}

# engine_busy: true while a battlecode engine runs on this machine (pgrep -f would match its own shell)
engine_busy () {
  ps -eo pid,args | awk '$2 ~ /(^|\/)java$/ && /battlecode\.server\.Main/' | grep -q .
}

# parse_result <engine stdout> -> "RESULT <A|B|?> <round|?> <reason>"
parse_result () {
  local LOG="$1" W R RE
  W=$(printf '%s\n' "$LOG"  | sed -n 's/.*(\([AB]\)) wins.*/\1/p' | tail -1)
  R=$(printf '%s\n' "$LOG"  | sed -n 's/.*wins (round \([0-9]*\)).*/\1/p' | tail -1)
  RE=$(printf '%s\n' "$LOG" | sed -n 's/.*Reason: //p' | tail -1)
  printf 'RESULT %s %s %s\n' "${W:-?}" "${R:-?}" "${RE:-?}"
}

# compile_src <srcdir> <outdir> : javac every .java under srcdir (all packages), no annotation processing
compile_src () {
  local SRC="$1" OUT="$2"; mkdir -p "$OUT"
  local files; files=$(find "$SRC" -name '*.java' | grep -v '/test/' || true)
  [ -n "$files" ] || { echo "!! no java sources under $SRC" >&2; return 1; }
  javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -d "$OUT" -cp "$(engine_cp)" $files
}
