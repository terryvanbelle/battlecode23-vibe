#!/usr/bin/env bash
# Build galaxy's own frontend (React + Vite) for the private replica at https://galaxy.136-86-167-127.sslip.io/.
#   bash tools/galaxy/frontend/build.sh [--no-install]     (on battlecode-dev, as the operator user)
# Steps:
#   1. export frontend/ of the pinned galaxy commit with `git archive` from GALAXY_SRC into a fresh work dir (the
#      checkout's working tree is never used, so local edits there cannot leak into the build);
#   2. apply replica.patch (same-origin backend, bc23 replay link -> /viewer/visualizer.html, self-hosted fonts, CSP,
#      default episode bc23, email verification off);
#   3. pin the environment: delete every other .env file, check .env.production, export the same values (Vite gives
#      the process environment priority over .env files);
#   4. npm ci --ignore-scripts (registry.npmjs.org only, every tarball checked against the lockfile's integrity; no
#      package install script runs, so openapi-generator-cli does not fetch its jar);
#   5. npm run build (tsc && vite build), niced so the game queue keeps the CPU; src/api/_autogen is used as committed
#      (generate_types.sh is never run);
#   6. check_bundle.py: refuse the build if any battlecode.org URL (or any other host) is fetched automatically;
#   7. install into $OUT (default /home/bcreplica/galaxy/frontend-dist) by staging and renaming, owner bcreplica.
# Env: GALAXY_SRC (git checkout of github.com/battlecode/galaxy, default ~/projects/vibe/reference/galaxy),
#      NODE_HOME (default ~/opt/node, from install-node.sh), WORK (default $REPO/build/galaxy-frontend),
#      OUT, KEEP_NODE_MODULES=1 to keep the 0.5 GB node_modules after the build.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO="$(cd "$HERE/../../.." && pwd)"
GALAXY_COMMIT=f343088f4d471b0664b2ff41129f0435a8dca1c2
GALAXY_SRC="${GALAXY_SRC:-$HOME/projects/vibe/reference/galaxy}"
NODE_HOME="${NODE_HOME:-$HOME/opt/node}"
WORK="${WORK:-$REPO/build/galaxy-frontend}"
OUT="${OUT:-/home/bcreplica/galaxy/frontend-dist}"
SITE=https://galaxy.136-86-167-127.sslip.io
install=1; [ "${1:-}" = --no-install ] && install=0

[ -x "$NODE_HOME/bin/node" ] || { echo "build: no node in $NODE_HOME (run tools/galaxy/frontend/install-node.sh)" >&2; exit 1; }
export PATH="$NODE_HOME/bin:$PATH"
git -C "$GALAXY_SRC" cat-file -e "$GALAXY_COMMIT^{commit}" 2>/dev/null \
  || { echo "build: $GALAXY_SRC lacks galaxy commit $GALAXY_COMMIT" >&2; exit 1; }

# 1-2. pinned source + patch
rm -rf "$WORK"; mkdir -p "$WORK/src"
git -C "$GALAXY_SRC" archive "$GALAXY_COMMIT" frontend | tar -x -C "$WORK/src"
patch -d "$WORK/src" -p1 --forward --batch --fuzz=0 --no-backup-if-mismatch -s < "$HERE/replica.patch"
cd "$WORK/src/frontend"

# 3. environment: only the patched .env.production, and the same values in the process environment
find . -maxdepth 1 -name '.env*' ! -name .env.production -print -delete
grep -q 'battlecode\.org' .env.production && { echo "build: .env.production still names battlecode.org" >&2; exit 1; }
export VITE_THIS_URL="$SITE" VITE_REPLAY_URL="$SITE" VITE_BACKEND_URL="" VITE_EMAIL_VERIFICATION_ENABLED=false
export NODE_ENV=production

# 4-5. dependencies and build
echo "build: node $(node --version), npm $(npm --version)"
nice -n 19 npm ci --ignore-scripts --no-audit --no-fund --loglevel=error --include=dev
nice -n 19 npm run build
DIST="$WORK/src/frontend/build"
[ -f "$DIST/index.html" ] || { echo "build: no $DIST/index.html" >&2; exit 1; }

# 6. no automatic contact with battlecode.org or any other host
python3 "$HERE/check_bundle.py" "$DIST" > "$WORK/bundle-urls.txt" \
  || { cat "$WORK/bundle-urls.txt"; echo "build: bundle check FAILED; not installed" >&2; exit 1; }
tail -3 "$WORK/bundle-urls.txt"
( cd "$DIST" && find . -type f ! -name '*.map' -print0 | sort -z | xargs -0 sha256sum ) > "$WORK/dist.sha256"
echo "galaxy $GALAXY_COMMIT + replica.patch $(sha256sum "$HERE/replica.patch" | cut -c1-16), node $(node --version)," \
  "built $(date -u +%FT%TZ)" > "$DIST/REPLICA_BUILD.txt"
[ "${KEEP_NODE_MODULES:-0}" = 1 ] || rm -rf "$WORK/src/frontend/node_modules"

# 7. install: stage next to $OUT, then swap with two renames
if [ $install = 1 ]; then
  parent="$(dirname "$OUT")"
  sudo -n test -d "$parent" || sudo -n install -d -o bcreplica -g bcreplica -m 2750 "$parent"
  sudo -n rm -rf "$OUT.new" "$OUT.old"
  sudo -n cp -r "$DIST" "$OUT.new"
  sudo -n chown -R bcreplica:bcreplica "$OUT.new"
  sudo -n find "$OUT.new" -type d -exec chmod 2755 {} + -o -type f -exec chmod 0644 {} +
  if sudo -n test -e "$OUT"; then sudo -n mv "$OUT" "$OUT.old"; fi
  sudo -n mv "$OUT.new" "$OUT"
  sudo -n rm -rf "$OUT.old"
  echo "build: installed $OUT ($(sudo -n find "$OUT" -type f | wc -l) files)"
else
  echo "build: built $DIST (not installed)"
fi
