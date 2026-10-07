#!/usr/bin/env bash
# Stage the Battlecode 2023 engine under engine/ (gitignored):
#   engine/battlecode23-3.0.15.jar   the official public release (a fat jar with every dependency and all 103 maps);
#                                    a read-only download from releases.battlecode.org, checksum-pinned
#   engine/patch/                    one patched class, put FIRST on the classpath by tools/lib.sh:
#     battlecode/world/LiveMap.class  getSeed() honours -Dbc.game.seed=<int> (robot ids, every sandboxed Random and the
#                                     final coin flip derive from the map seed; the same patch as the 2020/2021/2024
#                                     projects). Without the property the engine is byte-for-byte official behaviour.
# Source for the patch: reference/battlecode23 at tag 3.0.15 (the release; verified by commit hash).
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO/tools/lib.sh"
VER=3.0.15
JAR="$ENGINE_DIR/battlecode23-$VER.jar"
mkdir -p "$ENGINE_DIR"
if [ ! -s "$JAR" ]; then
  curl -sf -m 300 -o "$JAR.tmp" "https://releases.battlecode.org/maven/org/battlecode/battlecode23/$VER/battlecode23-$VER.jar"
  mv "$JAR.tmp" "$JAR"
fi
got=$(sha256sum "$JAR" | cut -c1-64)
[ "$got" = "$ENGINE_SHA256" ] || { echo "!! engine checksum mismatch: $got" >&2; exit 1; }

SRC="${BC23_SRC:-$HOME/projects/vibe/reference/battlecode23}"
if [ ! -d "$SRC/engine" ]; then
  git clone -q --depth 1 --branch "$VER" https://github.com/battlecode/battlecode23.git "$SRC"
fi
PATCH_SRC="$ENGINE_DIR/patch-src/battlecode/world"; mkdir -p "$PATCH_SRC" "$ENGINE_DIR/patch"
python3 - "$SRC/engine/src/main/battlecode/world/LiveMap.java" "$PATCH_SRC/LiveMap.java" <<'EOF'
import sys
s = open(sys.argv[1]).read()
old = "    public int getSeed() {\n        return seed;"
new = "    public int getSeed() {\n        return Integer.getInteger(\"bc.game.seed\", seed);"
assert s.count(old) == 1, "LiveMap.getSeed not found exactly once"
open(sys.argv[2], 'w').write(s.replace(old, new))
EOF
javac -nowarn -source 8 -target 8 -cp "$JAR" -d "$ENGINE_DIR/patch" "$PATCH_SRC/LiveMap.java"
# the patched class must expose exactly the official members
diff <(javap -p -cp "$JAR" battlecode.world.LiveMap) <(javap -p -cp "$ENGINE_DIR/patch" battlecode.world.LiveMap) \
  || { echo "!! patched LiveMap signature differs from the release" >&2; exit 1; }
echo "$VER" > "$ENGINE_DIR/VERSION"
echo "engine $VER staged at $ENGINE_DIR (patch: LiveMap.getSeed honours bc.game.seed)"
