#!/usr/bin/env bash
# Parallel games, bare java per game (no Gradle). Adapted from the 2024 project's gauntlet.sh.
#
#   BOT=bot OPPONENTS="g_iter1 examplefuncsplayer" MAPS="DefaultMap Maze" tools/gauntlet.sh   # product, both sides
#   CELLS=cells.txt tools/gauntlet.sh            # exactly the "opponent map side [seed]" lines in the file
#   TAG=name MAXJOBS=8 GAME_TIMEOUT=1200 SKIP_COMPILE=1 CLASSES=build/private KEEP_ALL=1 ...
#
# Names: a package under src/ (ours, compiled into $CLASSES) or a benchmark (owner.package from
# $BENCH_ROOT/manifest.tsv). External opponents need SCRIM=1 (ladder games come from the scrimmage tools; a diagnostic
# may choose cells but is never recorded in the ladder). The opponent's System.out is silenced.
# Seeds: the cell's 4th field when given; else SEED_MODE=map (official behaviour: the map file's seed) or random (default).
#
# Output gauntlet/<run-id>/: results.csv (opponent,map,bot_side,winner_side,rounds,bot_result,reason,seed),
# summary.txt, replays/ (wins deleted unless KEEP_ALL=1; losses and unknowns kept), unknown/dud logs.
# Runs from a private copy: bash reads scripts lazily by byte offset, so editing this file mid-run would corrupt it.
if [ -z "${BC23_REEXEC:-}" ]; then
  _self="$(dirname "${BASH_SOURCE[0]}")/.reexec-gauntlet.$$"
  cat "${BASH_SOURCE[0]}" > "$_self" || exit 1
  BC23_REEXEC="$_self" exec bash "$_self" "$@"
fi
rm -f "$BC23_REEXEC"
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO/tools/lib.sh"
BOT="${BOT:-bot}"; OPPONENTS="${OPPONENTS:-examplefuncsplayer}"
MAXJOBS="${MAXJOBS:-2}"; TAG="${TAG:-}"; SEED_MODE="${SEED_MODE:-random}"
MAPS="${MAPS:-$(tr '\n' ' ' < "$REPO/tools/maps.txt")}"
MANIFEST="$BENCH_ROOT/manifest.tsv"
resolve () {  # name -> "package url"
  local n="$1"
  if [ -d "$CLASSES/$n" ]; then echo "$n $CLASSES"; return; fi
  if [ -f "$MANIFEST" ]; then
    local line; line=$(awk -F'\t' -v n="$n" '$1==n{print $2" "$3; exit}' "$MANIFEST")
    [ -n "$line" ] && { echo "$line"; return; }
  fi
  echo "!! unknown team $n" >&2; return 1
}
# Never recompile a class tree that running games are reading.
if [ "${SKIP_COMPILE:-0}" != 1 ] && ps -eo args | grep -q "[j]ava .*-Dbc.game.team-[ab].url=$CLASSES "; then
  echo "!! $CLASSES is in use by running games; use CLASSES=<private tree> or SKIP_COMPILE=1" >&2; exit 3
fi
if [ "${SKIP_COMPILE:-0}" = 1 ] && [ -d "$CLASSES" ]; then echo "reusing $CLASSES (SKIP_COMPILE=1)" >&2
else rm -rf "$CLASSES" && CLASSES="$CLASSES" bash "$REPO/tools/build.sh" >/dev/null || { echo "!! compile failed" >&2; exit 1; }; fi

RUN_ID="$(date +%Y%m%d-%H%M%S)${TAG:+-$TAG}"
mkdir -p "$REPO/gauntlet"
until mkdir "$REPO/gauntlet/$RUN_ID" 2>/dev/null; do sleep 1; RUN_ID="$(date +%Y%m%d-%H%M%S)-$$${TAG:+-$TAG}"; done
OUT="$REPO/gauntlet/$RUN_ID"; mkdir -p "$OUT/replays"
if [ -n "${CELLS:-}" ]; then cp "$CELLS" "$OUT/cells.txt"
else for o in $OPPONENTS; do for m in $MAPS; do for s in A B; do echo "$o $m $s"; done; done; done > "$OUT/cells.txt"; fi
NG=$(grep -c . "$OUT/cells.txt")
for o in $BOT $(awk '{print $1}' "$OUT/cells.txt" | sort -u); do resolve "$o" >/dev/null || exit 1; done
if [ "${SCRIM:-0}" != 1 ]; then
  for o in $(awk '{print $1}' "$OUT/cells.txt" | sort -u); do [ -d "$CLASSES/$o" ] || { echo "!! $o is external: SCRIM=1 needed" >&2; exit 1; }; done
fi
# provenance: the content hash of the code that plays (results are keyed by code, never by a package or dir name;
# identity run 2 of 2026-10-07 compiled a src/bot that had changed under it and was misread as an identity control)
if [ -d "$REPO/src/$BOT" ]; then BOT_HASH=$(bash "$REPO/tools/bot-hash.sh" "$BOT"); else BOT_HASH=$(awk -F'\t' -v n="$BOT" '$1==n{print $2}' "$BENCH_ROOT/hashes.tsv"); fi
printf 'bot=%s\nbot_hash=%s\ncells=%s\n' "$BOT" "${BOT_HASH:-?}" "$(sha1sum "$OUT/cells.txt" | cut -c1-12)" > "$OUT/provenance.txt"
echo "gauntlet $RUN_ID bot=$BOT hash=${BOT_HASH:-?} games=$NG jobs=$MAXJOBS seeds=$SEED_MODE"
: > "$OUT/results.raw"

# One machine-wide game semaphore for every gauntlet (GAME_SLOTS slot files, flock): two runners side by side never
# exceed the measured knee. The replica worker keeps its own separate slots (docs/replica).
SLOTDIR="${SLOTDIR:-/tmp/bc23-game-slots}"; GAME_SLOTS="${GAME_SLOTS:-5}"; mkdir -p "$SLOTDIR"
acquire_slot () {
  while true; do
    for i in $(seq 1 "$GAME_SLOTS"); do
      exec {SLOTFD}>"$SLOTDIR/slot.$i"
      if flock -n "$SLOTFD"; then return 0; fi
      exec {SLOTFD}>&-
    done
    sleep 2
  done
}
game () {  # opp map side [seed]
  local OPP="$1" MAP="$2" SIDE="$3" SEED="${4:-}" rb ro PB UB PA UA
  acquire_slot
  rb=$(resolve "$BOT"); ro=$(resolve "$OPP")
  PB=${rb%% *}; UB=${rb#* }; PA=${ro%% *}; UA=${ro#* }
  if [ -z "$SEED" ]; then if [ "$SEED_MODE" = map ]; then SEED=map; else SEED=$(( (RANDOM << 15) | RANDOM )); fi; fi
  local TA TB KA KB UAA UBB silence
  if [ "$SIDE" = A ]; then TA=$BOT; TB=$OPP; KA=$PB; KB=$PA; UAA=$UB; UBB=$UA; silence=-Dbc.engine.silence-b=true
  else TA=$OPP; TB=$BOT; KA=$PA; KB=$PB; UAA=$UA; UBB=$UB; silence=-Dbc.engine.silence-a=true; fi
  local REPLAY="$OUT/replays/${OPP}__${MAP}__s${SEED}__bot${SIDE}.bc23"
  local seedopt=""; [ "$SEED" != map ] && seedopt="-Dbc.game.seed=$SEED"
  local LOG TO=0
  LOG=$(timeout "${GAME_TIMEOUT:-1800}" java -Xmx${GAME_XMX:-768m} -XX:+UseSerialGC -XX:ReservedCodeCacheSize=256m \
    -Dbc.server.mode=headless -Dbc.server.websocket=false -Dbc.server.debug=false -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false \
    -Dbc.server.validate-maps=false -Dbc.server.robot-player-to-system-out=false \
    -Dbc.server.robot-player-replay-file-per-team-limit-bytes=${LOG_LIMIT:-4000000} \
    ${CUSTOM_MAPS:+-Dbc.game.map-path=$CUSTOM_MAPS} "$silence" \
    -Dbc.game.team-a="$TA" -Dbc.game.team-b="$TB" -Dbc.game.team-a.package="$KA" -Dbc.game.team-b.package="$KB" \
    -Dbc.game.team-a.url="$UAA" -Dbc.game.team-b.url="$UBB" \
    -Dbc.game.maps="$MAP" -Dbc.server.save-file="$REPLAY" $seedopt \
    -cp "$(engine_cp)" battlecode.server.Main -c=- 2>&1 </dev/null) || TO=$?
  local R; R=$(parse_result "$LOG"); set -- $R; local W="$2" RND="$3"; shift 3; local RE="$*"
  local res; if [ "$W" = "$SIDE" ]; then res=win; elif [ "$W" = "?" ]; then res=unknown; else res=loss; fi
  if printf '%s\n' "$LOG" | grep -q "Error instrumenting ${PA}\."; then res=dud; RE="opponent failed to instrument"; fi
  if printf '%s\n' "$LOG" | grep -q "Error instrumenting ${PB}\."; then res=unknown; RE="BOT failed to instrument"; fi
  if [ "$W" = "?" ] && [ "$TO" = 124 ]; then res=unknown; RE="timeout after ${GAME_TIMEOUT:-1800}s"; fi
  if [ "$res" = unknown ] || [ "$res" = dud ]; then
    printf '%s\n' "$LOG" | grep -v '^\s*at ' | head -60 > "$OUT/${res}__${OPP}__${MAP}__s${SEED}__bot${SIDE}.log"; fi
  printf '%s,%s,%s,%s,%s,%s,%s,%s\n' "$OPP" "$MAP" "$SIDE" "$W" "$RND" "$res" "${RE//,/;}" "$SEED" >> "$OUT/results.raw"
  # CENSUS=1: one census row per team per game (tools/replay-dump.sh --census), keyed by opponent/map/side/seed, before
  # the replay can be deleted
  if [ "${CENSUS:-0}" = 1 ] && [ -s "$REPLAY" ]; then
    bash "$REPO/tools/replay-dump.sh" "$REPLAY" --census --no-header 2>/dev/null \
      | sed "s/^/$OPP,$MAP,$SIDE,$SEED,/" >> "$OUT/census.raw"
  fi
  [ "$res" = win ] && [ "${KEEP_ALL:-0}" != 1 ] && rm -f "$REPLAY"
  printf '  [%3d/%d] %-7s %-20s %-40s r%s\n' "$(wc -l < "$OUT/results.raw")" "$NG" "$res" "$MAP" "$OPP" "$RND"
}
export -f game resolve parse_result engine_cp acquire_slot
export OUT BOT ENGINE_DIR ENGINE_VER REPO MANIFEST GAME_XMX KEEP_ALL NG CLASSES SEED_MODE GAME_TIMEOUT LOG_LIMIT CUSTOM_MAPS CENSUS SLOTDIR GAME_SLOTS
xargs -P "$MAXJOBS" -L 1 bash -c 'game "$0" "$1" "$2" "${3:-}"' < "$OUT/cells.txt"

{ echo "opponent,map,bot_side,winner_side,rounds,bot_result,reason,seed"; sort "$OUT/results.raw"; } > "$OUT/results.csv"
if [ -f "$OUT/census.raw" ]; then
  hdr=$(bash "$REPO/tools/replay-dump.sh" --census-header 2>/dev/null)
  { echo "cell_opponent,cell_map,cell_side,cell_seed,$hdr"; sort "$OUT/census.raw"; } > "$OUT/census.csv"; rm -f "$OUT/census.raw"
fi
rm -f "$OUT/results.raw"; rmdir "$OUT/replays" 2>/dev/null || true
{ python3 "$REPO/tools/summarize.py" "$OUT/results.csv" "$BOT"; echo "bot_hash: ${BOT_HASH:-?}"; } | tee "$OUT/summary.txt"
echo "wrote $OUT/"
