#!/usr/bin/env bash
# One diagnostic game with robot output captured (our bot's System.out; the opponent is silenced).
#   tools/run-dev.sh <teamA> <teamB> <map> [seed]      -> matches/dev-<A>-<B>-<map>-<seed>.{bc23,log}
# DEBUG=1 sets -Dbc.testing.debug=true (our bot prints caught exceptions). Compiles src/ into a private class tree so it
# can run beside a gauntlet. On the driver it plays one game at a time (CLAUDE rule 1); run it on the VM via vm-run.sh
# for anything heavier.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO/tools/lib.sh"
A="$1"; B="$2"; MAP="$3"; SEED="${4:-1}"
export CLASSES="$REPO/build/dev-classes-$$"
bash "$REPO/tools/build.sh" > /dev/null
mkdir -p "$REPO/matches"
base="$REPO/matches/dev-$A-$B-$MAP-$SEED"
# the team named bot (or DEV_TEAM) keeps its output; the other side is silenced
DEV_TEAM="${DEV_TEAM:-bot}"
silence=""
[ "$A" = "$DEV_TEAM" ] || silence="-Dbc.engine.silence-a=true"
[ "$B" = "$DEV_TEAM" ] || silence="$silence -Dbc.engine.silence-b=true"
SHOW_LOGS=true GAME_SEED="$SEED" GAME_OPTS="$silence ${DEBUG:+-Dbc.testing.debug=true}" \
  run_game "$A" "$B" "$MAP" "$base.bc23" > "$base.log" 2>&1 || true
rm -rf "$CLASSES"
parse_result "$(cat "$base.log")"
echo "replay $base.bc23  log $base.log ($(grep -c . "$base.log") lines)"
