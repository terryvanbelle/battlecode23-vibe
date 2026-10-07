#!/usr/bin/env bash
# tools/replay-dump.sh <replay.bc23> [mode flags...]   (see tools/replaydump/ReplayDump.java for the modes)
# Compiles ReplayDump on demand into build/replaydump-<source hash> so a stale class is never used.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO/tools/lib.sh"
SRC="$REPO/tools/replaydump/ReplayDump.java"
H=$(sha1sum "$SRC" | cut -c1-12)
OUT="$REPO/build/replaydump-$H"
if [ ! -f "$OUT/replaydump/ReplayDump.class" ]; then
  mkdir -p "$OUT.tmp.$$" && javac -nowarn -encoding UTF-8 -source 8 -target 8 -d "$OUT.tmp.$$" -cp "$(engine_cp)" "$SRC" \
    && { mv "$OUT.tmp.$$" "$OUT" 2>/dev/null || rm -rf "$OUT.tmp.$$"; }
fi
exec java -Xmx${DUMP_XMX:-1g} -cp "$OUT:$(engine_cp)" replaydump.ReplayDump "$@"
