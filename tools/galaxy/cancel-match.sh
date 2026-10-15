#!/usr/bin/env bash
# Show, or cancel and re-rate, a replica match stuck in RUN (galaxy's own staff Cancel + Recalculate, through the
# Django shell as bcreplica on the VM). The watcher's STUCK_MATCH event names the match.
#   tools/galaxy/cancel-match.sh <match-id>            # print status, creation time and participants
#   tools/galaxy/cancel-match.sh <match-id> --cancel   # cancel it and request re-rating
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
id="${1:?usage: cancel-match.sh <match-id> [--cancel]}"; [[ "$id" =~ ^[0-9]+$ ]] || { echo "bad match id: $id"; exit 2; }
act=0; [ "${2:-}" = "--cancel" ] && act=1
py="from siarnaq.api.compete.models import Match
m = Match.objects.get(pk=$id)
print('match', m.pk, m.status, 'created', m.created, 'ranked', m.is_ranked, [str(p.team) for p in m.participants.all()])
if $act:
    qs = Match.objects.filter(pk=$id); qs.cancel()
    if hasattr(qs, 'request_rerating'): Match.objects.filter(pk=$id).request_rerating()
    print('now', Match.objects.get(pk=$id).status)"
source "$REPO/tools/vm.sh"; ensure_vm >/dev/null
printf '%s\n' "$py" | gssh "sudo -u bcreplica bash -c 'set -a; . /etc/bc23-galaxy/galaxy.env; set +a; cd /opt/bc23-galaxy/src/backend; /opt/bc23-galaxy/venv/bin/python manage.py shell'" 2>&1 | grep -v "^$" | tail -5
