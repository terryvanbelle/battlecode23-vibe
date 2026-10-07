#!/usr/bin/env bash
# Sync the repo's src/tools/test/engine to the VM and run a command there, detached (survives the ssh session).
#   tools/vm-run.sh <name> '<command run from ~/projects/vibe/2023 on the VM>'
# Output: ~/projects/vibe/2023/logs/<name>.log on the VM (tools/vm-tail.sh <name> to follow).
# setsid + nohup + </dev/null: the job must not hold the ssh channel open or die with it.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO/tools/vm.sh"
NAME="$1"; CMD="$2"
ensure_vm
[ "${NO_SYNC:-0}" = 1 ] || vm_sync
gssh "mkdir -p ~/$REMOTE_REPO/logs && cd ~/$REMOTE_REPO && setsid nohup bash -c $(printf '%q' "$CMD") > logs/$NAME.log 2>&1 < /dev/null & echo started $NAME on $VM"
