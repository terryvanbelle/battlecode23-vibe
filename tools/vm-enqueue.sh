#!/usr/bin/env bash
# Append a job to the VM's standing queue (tools/vm-queue.sh), after syncing the repo tree.
#   tools/vm-enqueue.sh <name> '<command line, run from the repo root on the VM>'
#   FILLER=1 tools/vm-enqueue.sh x '<cmd>'   # replace the idle filler job instead (FILLER=0 x '' removes it)
# Job files are <UTC stamp>-<name>.job so they run in submission order; the log is logs/<stamp>-<name>.log on the VM.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; source "$REPO/tools/vm.sh"
NAME="${1:?name}"; CMD="${2-}"; ensure_vm
[ "${NO_SYNC:-0}" = 1 ] || vm_sync
STAMP="$(date -u +%Y%m%d-%H%M%S)"
if [ "${FILLER:-0}" = 1 ]; then DEST="queue/filler.job"; else DEST="queue/pending/$STAMP-$NAME.job"; fi
if [ "${FILLER:-0}" = 1 ] && [ -z "$CMD" ]; then gssh "rm -f ~/$REMOTE_REPO/queue/filler.job"; echo "filler removed"; exit 0; fi
printf '%s\n' "$CMD" | gssh "mkdir -p ~/$REMOTE_REPO/queue/pending && cat > ~/$REMOTE_REPO/$DEST.tmp && mv ~/$REMOTE_REPO/$DEST.tmp ~/$REMOTE_REPO/$DEST"
echo "queued $DEST (log: logs/$( [ "${FILLER:-0}" = 1 ] && echo 'filler-<stamp>' || echo "$STAMP-$NAME").log)"
