#!/usr/bin/env bash
# Replay retention on the VM (docs/galaxy/README.md): run tools/galaxy/prune_replays.py once now, and with
# --install-cron also (re)install it in the operator crontab every 6 hours at :30 (the crontab was lost in the
# 2026-10-12 18:48 PDT outage). The only command the owner's permission rule allows for this (PROMPTS 93).
#   tools/galaxy/vm-prune.sh [--install-cron]
set -euo pipefail
cd "$(dirname "$0")/../.."
source tools/vm.sh
ensure_vm >/dev/null
P=/home/terryvanbelle/projects/vibe/2023/tools/galaxy/prune_replays.py
L=/home/terryvanbelle/projects/vibe/2023/logs/prune-replays.log
RUN="sudo -n bc23-galaxy-manage shell -c \"exec(open('$P').read())\" 2>&1 | grep prune-replays >> $L"
gssh "$RUN; tail -1 $L; df -h / | tail -1"
if [ "${1:-}" = --install-cron ]; then
  gssh "(crontab -l 2>/dev/null | grep -v prune_replays.py; echo '30 */6 * * * $RUN') | crontab - && crontab -l"
fi
