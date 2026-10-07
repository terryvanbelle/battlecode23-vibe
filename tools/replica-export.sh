#!/usr/bin/env bash
# Move finished ladder-replica games into progress/games.csv on the driver (run from the repo root on the driver).
#   bash tools/replica-export.sh
# On the VM: `bc23-replica export-games` (runs as bcreplica, marks the games) writes a new file under
# /home/bcreplica/replica/export/. Every export file there is then fetched and its rows appended when their (run, seq)
# is not in progress/games.csv yet, so a failed or repeated run never loses or duplicates a game.
set -euo pipefail
REPO=$(cd "$(dirname "$0")/.." && pwd)
source "$REPO/tools/vm.sh"
IP=${IP:-10.138.0.3}
X=/home/bcreplica/replica/export
gssh "sudo -u bcreplica mkdir -p $X && f=$X/games-\$(date -u +%Y%m%dT%H%M%S).csv && cd ~/projects/vibe/2023 && bc23-replica export-games --out \$f >/dev/null && ls $X"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
gssh "cd $X && tar cf - games-*.csv 2>/dev/null" | tar xf - -C "$TMP"
python3 - "$REPO/progress/games.csv" "$TMP"/games-*.csv <<'PY'
import csv, sys
out, files = sys.argv[1], sorted(sys.argv[2:])
sys.path.insert(0, out.rsplit('/progress/', 1)[0] + '/tools')
import elolib
have = {(r['run'], r['seq']) for r in csv.DictReader(open(out))}
add = []
for f in files:
    for r in csv.DictReader(open(f)):
        k = (r['run'], r['seq'])
        if k not in have:
            have.add(k)
            add.append({h: r.get(h, '') for h in elolib.HDR})
with open(out, 'a', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=elolib.HDR)
    for r in add:
        w.writerow(r)
print(f'replica-export: {len(add)} new games appended from {len(files)} export files')
PY
