#!/usr/bin/env bash
# Undo deploy.sh. Run on the driver.
#   tools/replica/deploy/teardown.sh web    close tcp:80,443 (rule + tag) and remove Caddy (binary, units, certificates,
#                                           logs, user caddy). The lockdown and user bcreplica stay.
#   tools/replica/deploy/teardown.sh all [--purge-data] [--purge-password]
#                                           also remove the egress lockdown, the slice and user bcreplica. Refuses while
#                                           processes run as bcreplica. /home/bcreplica (DB, replays) is kept unless
#                                           --purge-data; the password files are kept unless --purge-password.
# The nftables package stays installed (remove with: sudo apt-get purge nftables).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"
# shellcheck source=../../vm.sh
source "$HERE/../../vm.sh"; IP="${IP:-10.138.0.3}"
what="${1:-}"; shift || true
purge_data=""; purge_pw=0
for a in "$@"; do case "$a" in --purge-data) purge_data=--purge-data ;; --purge-password) purge_pw=1 ;;
  *) echo "unknown option $a" >&2; exit 2 ;; esac; done
case "$what" in
  web) "$HERE/gcp-firewall.sh" remove; gssh "sudo $LIB_DIR/vm-setup.sh teardown-web" ;;
  all) "$HERE/gcp-firewall.sh" remove; gssh "sudo $LIB_DIR/vm-setup.sh teardown-all $purge_data" ;;
  *) sed -n '2,10p' "$0" >&2; exit 2 ;;
esac
if [ $purge_pw = 1 ]; then gssh "rm -f '$PASSWORD_FILE'"; rm -f "$PASSWORD_FILE"; echo "password files removed"; fi
