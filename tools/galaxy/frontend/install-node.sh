#!/usr/bin/env bash
# Install Node.js (LTS) for the current user only, to build galaxy's frontend (tools/galaxy/frontend/build.sh).
#   bash tools/galaxy/frontend/install-node.sh        (on battlecode-dev, as the operator user; no sudo)
# Result: ~/opt/node-<version>-linux-x64 and the symlink ~/opt/node (build.sh uses ~/opt/node/bin). Nothing is put on
# the system PATH or in /usr. The official tarball and SHASUMS256.txt come from nodejs.org over HTTPS; the tarball is
# installed only if its sha256 equals both its line in SHASUMS256.txt and the pin below (pinned 2026-10-07; the
# SHASUMS line was fetched independently from the driver and the VM and matched).
set -euo pipefail
NODE_VERSION=v24.21.0                     # LTS "Krypton", released 2026-09-07
NODE_SHA256=fd8e59d5a511510f6a298afb548f18c7d2b1be404d8b4a27d94fbe49f56cb2d6   # node-v24.21.0-linux-x64.tar.xz
NAME="node-$NODE_VERSION-linux-x64"
DEST="$HOME/opt"
[ "$(uname -m)" = x86_64 ] || { echo "install-node: x86_64 only" >&2; exit 1; }
if [ -x "$DEST/$NAME/bin/node" ]; then
  echo "install-node: $DEST/$NAME already installed"
else
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  base="https://nodejs.org/dist/$NODE_VERSION"
  curl --proto '=https' -fsSL --max-time 300 -o "$tmp/$NAME.tar.xz" "$base/$NAME.tar.xz"
  curl --proto '=https' -fsSL --max-time 60 -o "$tmp/SHASUMS256.txt" "$base/SHASUMS256.txt"
  listed="$(awk -v f="$NAME.tar.xz" '$2==f {print $1}' "$tmp/SHASUMS256.txt")"
  actual="$(sha256sum "$tmp/$NAME.tar.xz" | cut -d' ' -f1)"
  [ "$listed" = "$NODE_SHA256" ] || { echo "install-node: SHASUMS256.txt lists '$listed', pin is $NODE_SHA256" >&2; exit 1; }
  [ "$actual" = "$NODE_SHA256" ] || { echo "install-node: tarball sha256 $actual != $NODE_SHA256" >&2; exit 1; }
  mkdir -p "$DEST"
  tar -xJf "$tmp/$NAME.tar.xz" -C "$tmp"
  mv "$tmp/$NAME" "$DEST/$NAME"
  echo "install-node: installed $DEST/$NAME (sha256 $actual verified)"
fi
ln -sfn "$NAME" "$DEST/node"
"$DEST/node/bin/node" --version
