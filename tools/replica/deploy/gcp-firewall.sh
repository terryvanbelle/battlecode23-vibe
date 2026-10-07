#!/usr/bin/env bash
# The only inbound ports this deployment opens on GCP: tcp:80 (ACME HTTP-01 challenge, then redirect to https) and
# tcp:443, from 0.0.0.0/0, to instances carrying network tag bc23-replica-web (only battlecode-dev). Run on the driver.
#   tools/replica/deploy/gcp-firewall.sh apply    create the rule if missing, tag the VM
#   tools/replica/deploy/gcp-firewall.sh remove   untag the VM, delete the rule
#   tools/replica/deploy/gcp-firewall.sh show
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"
G=(--project="$BC_PROJECT")
I=("$BC_VM" --zone="$BC_ZONE" "${G[@]}")

show () {
  gcloud compute firewall-rules describe "$FW_RULE" "${G[@]}" \
    --format='table(name,network.basename(),direction,sourceRanges.list(),allowed[].map().firewall_rule().list(),targetTags.list(),disabled)' \
    2>/dev/null || echo "no firewall rule $FW_RULE"
  echo "tags on $BC_VM: $(gcloud compute instances describe "${I[@]}" --format='value(tags.items)')"
}

case "${1:-show}" in
  apply)
    if gcloud compute firewall-rules describe "$FW_RULE" "${G[@]}" >/dev/null 2>&1; then
      echo "rule $FW_RULE exists"
    else
      net=$(gcloud compute instances describe "${I[@]}" --format='value(networkInterfaces[0].network.basename())')
      gcloud compute firewall-rules create "$FW_RULE" "${G[@]}" --network="${net:-default}" --direction=INGRESS \
        --priority=1000 --action=ALLOW --rules=tcp:80,tcp:443 --source-ranges=0.0.0.0/0 --target-tags="$FW_TAG" \
        --description="bc23 galaxy replica web front: Caddy, HTTPS + basic auth (80 = ACME + redirect). See docs/replica/DEPLOY.md"
    fi
    gcloud compute instances add-tags "${I[@]}" --tags="$FW_TAG"
    show ;;
  remove)
    gcloud compute instances remove-tags "${I[@]}" --tags="$FW_TAG" || true
    gcloud compute firewall-rules delete "$FW_RULE" "${G[@]}" --quiet || true
    show ;;
  show) show ;;
  *) sed -n '2,6p' "$0" >&2; exit 2 ;;
esac
