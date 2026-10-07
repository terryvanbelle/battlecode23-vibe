#!/usr/bin/env bash
# Start the real ladder on the VM from a clean database (run ON the VM from ~/projects/vibe/2023).
#   bash tools/replica-reset.sh            # archives the current replica data (never deletes), inits, seeds the field
#                                          # (tools/field.txt) + examplefuncsplayer + our incumbent (tools/incumbent.txt)
# The worker service keeps running; it picks up matches as they are queued. Start the matchmaker separately:
#   setsid nohup python3 tools/replica-matchmaker.py > logs/matchmaker.log 2>&1 < /dev/null &
set -euo pipefail
H=/home/bcreplica/replica
STAMP=$(date -u +%Y%m%d-%H%M%S)
sudo systemctl stop bc23-replica-worker
# archive everything except the installed viewer (kept in place)
sudo -u bcreplica bash -c "mkdir -p $H/archive/$STAMP && cd $H && for f in replica.db replica.db-shm replica.db-wal replay sub logs; do [ -e \$f ] && mv \$f archive/$STAMP/; done; mkdir -p replay sub logs"
bc23-replica init
bc23-replica seed-field
INC=$(cat tools/incumbent.txt | head -1)
PKG=${INC#us:}
[ -d build/classes/$PKG ] || CLASSES=build/classes bash tools/build.sh "$PKG"
bc23-replica add-team "$INC"
sudo systemctl start bc23-replica-worker
bc23-replica status
python3 tools/replica.py ratings | head -5
echo "archived the previous data under $H/archive/$STAMP"
