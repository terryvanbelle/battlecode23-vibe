#!/usr/bin/env bash
# Runs ON the VM (operator crontab, every 6 hours at :30): tools/galaxy/prune_replays.py in siarnaq's Django context,
# its one-line summary appended to logs/prune-replays.log. Installed by tools/galaxy/vm-prune.sh --install-cron.
R="$HOME/projects/vibe/2023"
sudo -n bc23-galaxy-manage shell -c "exec(open('$R/tools/galaxy/prune_replays.py').read())" 2>&1 \
  | grep prune-replays >> "$R/logs/prune-replays.log"
