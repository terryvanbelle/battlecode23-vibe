#!/usr/bin/env bash
# Replay retention on the VM (docs/galaxy/README.md): sync the repo tree, run tools/galaxy/prune-local.sh once now, and
# with --install-cron also (re)install it in the operator crontab every 6 hours at :30 (the crontab was lost in the
# 2026-10-12 18:48 PDT outage). The only command the owner's permission rule allows for this (PROMPTS 93).
#   tools/galaxy/vm-prune.sh [--install-cron]
set -euo pipefail
cd "$(dirname "$0")/../.."
source tools/vm.sh
ensure_vm >/dev/null
vm_sync >/dev/null
L=projects/vibe/2023/logs/prune-replays.log
gssh "bash projects/vibe/2023/tools/galaxy/prune-local.sh; tail -1 $L; df -h / | tail -1"
if [ "${1:-}" = --install-cron ]; then
  # the cron line holds no quotes: the first version nested them and cron got open(/home/...) (2026-10-14)
  gssh '(crontab -l 2>/dev/null | grep -v -e prune_replays.py -e prune-local.sh; echo "30 */6 * * * bash $HOME/projects/vibe/2023/tools/galaxy/prune-local.sh") | crontab - && crontab -l'
fi
