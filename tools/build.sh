#!/usr/bin/env bash
# Compile our bots: every package under src/ into build/classes (or $CLASSES). Fails on any compile error.
#   tools/build.sh            # all packages
#   tools/build.sh pkg ...    # only these packages (src/<pkg>)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO/tools/lib.sh"
mkdir -p "$CLASSES"
if [ $# -eq 0 ]; then set -- $(cd "$REPO/src" && ls -d */ 2>/dev/null | tr -d /); fi
for p in "$@"; do
  [ -d "$REPO/src/$p" ] || { echo "!! no src/$p" >&2; exit 1; }
  rm -rf "$CLASSES/$p"
  files=$(find "$REPO/src/$p" -name '*.java')
  javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -d "$CLASSES" -cp "$(engine_cp):$CLASSES" $files
done
echo "built: $*"
