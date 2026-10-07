#!/usr/bin/env bash
# Freeze src/bot/ as a permanent opponent package:  tools/snapshot.sh g_iter3
# Rewrites `package bot;` -> `package <name>;` and intra-package imports; refuses existing names and reserved names.
# Prints the content hash of the frozen package (tools/bot-hash.sh) so results can be keyed by code, not by name.
set -euo pipefail
cd "$(dirname "$0")/.."
NAME="${1:?usage: tools/snapshot.sh <package-name>}"
case "$NAME" in bot|examplefuncsplayer) echo "refusing to overwrite $NAME" >&2; exit 1;; *[!a-z0-9_]*) echo "name must be [a-z0-9_]+" >&2; exit 1;; esac
DEST="src/$NAME"; [ -e "$DEST" ] && { echo "$DEST already exists" >&2; exit 1; }
mkdir -p "$DEST"
for f in src/bot/*.java; do
  sed -e "s/^package bot;/package $NAME;/" -e "s/^import bot\./import $NAME./" -e "s/^import static bot\./import static $NAME./" "$f" > "$DEST/$(basename "$f")"
done
grep -L "^package $NAME;" "$DEST"/*.java | grep -q . && { echo "package rewrite failed" >&2; rm -rf "$DEST"; exit 1; }
echo "snapshotted src/bot/ -> $DEST/ ($(ls "$DEST" | wc -l) files), code hash $(bash tools/bot-hash.sh "$NAME")"
