#!/usr/bin/env bash
# One command, run on the driver, that (re)applies the whole replica host setup on battlecode-dev. Idempotent.
#   tools/replica/deploy/deploy.sh             push these scripts, VM setup, GCP firewall, password, host name, verify
#   tools/replica/deploy/deploy.sh --no-web    lockdown only (user bcreplica + egress); no Caddy, no open ports
# Steps: 1 push tools/replica/deploy to the VM checkout; 2 sudo vm-setup.sh (user, egress, caddy); 3 gcp-firewall.sh
# apply; 4 set-password.sh (keeps an existing password); 5 refresh-hostname.sh; 6 verify.sh.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"
# shellcheck source=../../vm.sh
source "$HERE/../../vm.sh"; IP="${IP:-10.138.0.3}"
web=1; [ "${1:-}" = --no-web ] && web=0
DEST="$REMOTE_REPO/tools/replica/deploy"

echo "== 1 push $DEST"
gssh "mkdir -p ~/$DEST"
rsync -a -e "ssh ${SSHO[*]}" "$HERE/" "$USER_NAME@$IP:$DEST/"
echo "== 2 VM setup"
if [ $web = 1 ]; then gssh "sudo bash ~/$DEST/vm-setup.sh all"
else gssh "sudo bash ~/$DEST/vm-setup.sh install && sudo bash ~/$DEST/vm-setup.sh user && sudo bash ~/$DEST/vm-setup.sh egress"; fi
if [ $web = 1 ]; then
  echo "== 3 GCP firewall"; "$HERE/gcp-firewall.sh" apply
  echo "== 4 password"; "$HERE/set-password.sh"
  echo "== 5 host name"; "$HERE/refresh-hostname.sh"
  echo "== 6 verify (the first certificate can take a minute)"; sleep 20
  "$HERE/verify.sh"
else
  "$HERE/verify.sh" vm
fi
