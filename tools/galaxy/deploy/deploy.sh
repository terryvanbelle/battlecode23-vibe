#!/usr/bin/env bash
# Deploy (or redeploy) the galaxy replica on battlecode-dev from the driver. Idempotent. Doc: docs/galaxy/README.md.
#   tools/galaxy/deploy/deploy.sh              push code, galaxy-setup.sh all (with a fresh git archive), verify
#   tools/galaxy/deploy/deploy.sh STEP [ARG]   push code, then one galaxy-setup.sh step (e.g. units, start, frontend)
# Needs the galaxy-lite host setup first (tools/replica/deploy/deploy.sh: bcreplica, egress table, Caddy, password).
# The galaxy source is `git archive` of the pinned commit from GALAXY_CHECKOUT (default
# ~/projects/vibe/reference/galaxy); the VM checks the archive's embedded commit id before installing it.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO="$(cd "$HERE/../../.." && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"
# shellcheck source=../../vm.sh
source "$REPO/tools/vm.sh"; IP="${IP:-10.138.0.3}"
GALAXY_CHECKOUT="${GALAXY_CHECKOUT:-$HOME/projects/vibe/reference/galaxy}"
[ "$(hostname -s)" != "$BC_VM" ] || { echo "deploy: run this on the driver" >&2; exit 1; }

echo "== push tools/galaxy and tools/replica/deploy to the VM checkout"
for d in tools/galaxy tools/replica/deploy; do
  gssh "mkdir -p ~/$REMOTE_REPO/$d"
  rsync -a --exclude __pycache__ -e "ssh ${SSHO[*]}" "$REPO/$d/" "$USER_NAME@$IP:$REMOTE_REPO/$d/"
done
SETUP="sudo bash ~/$REMOTE_REPO/tools/galaxy/deploy/galaxy-setup.sh"
if [ $# -gt 0 ]; then
  gssh "$SETUP $*"
  exit 0
fi
echo "== galaxy source: git archive $GALAXY_COMMIT"
tar=/tmp/bc23-galaxy-${GALAXY_COMMIT:0:12}.tar
git -C "$GALAXY_CHECKOUT" archive --format=tar "$GALAXY_COMMIT" > "$tar.local"
gssh "cat > $tar" < "$tar.local"; rm -f "$tar.local"
echo "== galaxy-setup.sh all"
gssh "$SETUP all $tar && rm -f $tar"
echo "== verify"
"$REPO/tools/replica/deploy/verify.sh"
