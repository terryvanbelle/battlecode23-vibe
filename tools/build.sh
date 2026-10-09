#!/usr/bin/env bash
# Compile our bots: every package under src/ into build/classes (or $CLASSES). Fails on any compile error.
#   tools/build.sh            # all packages
#   tools/build.sh pkg ...    # only these packages (src/<pkg>)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO/tools/lib.sh"
mkdir -p "$CLASSES"
if [ $# -eq 0 ]; then set -- $(cd "$REPO/src" && ls -d */ 2>/dev/null | tr -d /); fi
# HASHES=1 (set by tools/gauntlet.sh and tools/screen.py jobs): also write $CLASSES/.hashes, "<package> <code hash>" of
# the code compiled into this tree (tools/bot-hash.sh, taken before and after javac; '?' when the sources changed in
# between, e.g. a vm_sync landing mid-compile). Run provenance reads it, so SKIP_COMPILE=1 runs record the code that
# plays, not whatever src/ holds later (docs/ARCHETYPES.md section 6.7). Off by default: about 1 s per package.
for p in "$@"; do
  [ -d "$REPO/src/$p" ] || { echo "!! no src/$p" >&2; exit 1; }
  rm -rf "$CLASSES/$p"
  [ "${HASHES:-0}" = 1 ] && h0=$(bash "$REPO/tools/bot-hash.sh" "$p")
  files=$(find "$REPO/src/$p" -name '*.java')
  javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -d "$CLASSES" -cp "$(engine_cp):$CLASSES" $files
  if [ "${HASHES:-0}" = 1 ]; then
    h1=$(bash "$REPO/tools/bot-hash.sh" "$p"); [ "$h0" = "$h1" ] || h1='?'
    { [ -f "$CLASSES/.hashes" ] && awk -v p="$p" '$1 != p' "$CLASSES/.hashes"; echo "$p $h1"; } > "$CLASSES/.hashes.tmp.$$"
    mv "$CLASSES/.hashes.tmp.$$" "$CLASSES/.hashes"
  else rm -f "$CLASSES/.hashes"; fi     # a tree recompiled without hashes must not keep stale ones
done
echo "built: $*"
