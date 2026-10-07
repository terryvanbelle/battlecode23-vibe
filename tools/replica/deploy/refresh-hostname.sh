#!/usr/bin/env bash
# Recompute the replica's public host name (<external-ip-with-dashes>.sslip.io), rewrite the Caddyfile, reload Caddy.
# battlecode-dev's external IP is ephemeral: it changes whenever the VM is stopped and started. The unit
# bc23-replica-hostname.service runs this at every boot (before Caddy starts). Run it by hand when that failed
# (journalctl -u bc23-replica-hostname) or after any change of IP:
#   tools/replica/deploy/refresh-hostname.sh               on the driver: IP from gcloud, then fixes the VM over ssh
#   sudo /usr/local/lib/bc23-replica/refresh-hostname.sh   on the VM: IP from the metadata server (root only)
#   ... refresh-hostname.sh 203.0.113.7                    either place: use this IP
# Prints the URL. Caddy then gets a Let's Encrypt certificate for the new name on its own (ports 80/443 must be open).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"
die () { echo "refresh-hostname: $*" >&2; exit 1; }
IPV4_RE='^([0-9]{1,3}\.){3}[0-9]{1,3}$'

boot=0; [ "${1:-}" = --boot ] && { boot=1; shift; }
ip="${1:-}"
[ -z "$ip" ] || [[ $ip =~ $IPV4_RE ]] || die "not an IPv4 address: '$ip'"

if [ "$(hostname -s)" != "$BC_VM" ]; then
  # ---- driver mode
  if [ -z "$ip" ]; then
    ip=$(gcloud compute instances describe "$BC_VM" --zone "$BC_ZONE" --project "$BC_PROJECT" \
           --format='value(networkInterfaces[0].accessConfigs[0].natIP)')
  fi
  [[ $ip =~ $IPV4_RE ]] || die "no external IP for $BC_VM (is it running? has it an access config?)"
  # shellcheck source=../../vm.sh
  source "$HERE/../../vm.sh"; IP="${IP:-10.138.0.3}"
  exec ssh "${SSHO[@]}" "$USER_NAME@$IP" "sudo $LIB_DIR/refresh-hostname.sh $ip"
fi

# ---- VM mode (root)
if [ "$(id -u)" != 0 ]; then
  args=(); [ $boot = 1 ] && args+=(--boot); [ -n "$ip" ] && args+=("$ip")
  exec sudo "$LIB_DIR/refresh-hostname.sh" "${args[@]}"
fi
if [ -z "$ip" ]; then
  for _ in $(seq 1 20); do   # up to ~100 s at boot
    ip=$(curl -fsS -m 3 -H 'Metadata-Flavor: Google' \
      http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip 2>/dev/null || true)
    [ -n "$ip" ] && break
    sleep 2
  done
fi
[[ $ip =~ $IPV4_RE ]] || die "no external IP from the metadata server"
host="${ip//./-}.sslip.io"
install -d -o root -g root -m 0755 "$ETC_DIR"
old=$(head -1 "$ETC_DIR/hostname" 2>/dev/null || true)
if [ "$host" != "$old" ]; then
  printf '%s\n' "$host" > "$ETC_DIR/hostname.new" && mv -f "$ETC_DIR/hostname.new" "$ETC_DIR/hostname"
  echo "host name: ${old:-<none>} -> $host"
fi
if [ -s "$ETC_DIR/owner.bcrypt" ]; then
  if [ $boot = 1 ]; then "$LIB_DIR/vm-setup.sh" render --boot   # Caddy starts after this unit
  elif [ "$host" != "$old" ] || ! systemctl is-active --quiet "$UNIT_CADDY"; then "$LIB_DIR/vm-setup.sh" render
  fi
else
  echo "no password hash yet: run tools/replica/deploy/set-password.sh from the driver"
fi
echo "https://$host/"
