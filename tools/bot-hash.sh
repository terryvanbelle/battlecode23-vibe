#!/usr/bin/env bash
# Content hash of one of our bot packages, invariant under the package name: tools/bot-hash.sh <pkg>
# Two packages with the same hash play identically (results are keyed by this, never by a directory name).
set -euo pipefail
cd "$(dirname "$0")/.."
P="${1:?usage: tools/bot-hash.sh <package>}"
for f in $(ls src/"$P"/*.java | sort); do
  sed -e "s/^package $P;/package PKG;/" -e "s/^import $P\./import PKG./" -e "s/^import static $P\./import static PKG./" "$f"
done | sha1sum | cut -c1-12
