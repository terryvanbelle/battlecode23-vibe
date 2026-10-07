# shellcheck shell=bash
# Shared settings for the replica deployment scripts. Sourced, never run.
# Used on the driver (gcloud, ssh) and on battlecode-dev (root setup); see docs/replica/DEPLOY.md.

# GCP
BC_VM=battlecode-dev
BC_ZONE=us-west1-b
BC_PROJECT=tvanbelle-vibecode
FW_RULE=bc23-replica-web          # VPC firewall rule: tcp:80,443 from 0.0.0.0/0 ...
FW_TAG=bc23-replica-web           # ... to instances carrying this network tag only

# The replica (galaxy-lite) runs as this user with no credentials and no off-host egress.
REPLICA_USER=bcreplica
REPLICA_GROUP=bcreplica           # terryvanbelle is a member: read access to the DB and replays
REPLICA_HOME=/home/bcreplica/replica
REPLICA_PORT=8023                 # replica web server; must bind 127.0.0.1 only
REPLICA_LO_PORTS="8023"           # loopback TCP ports bcreplica may open NEW connections to (space-separated)
OPERATOR_USER=terryvanbelle

# Public web access: Caddy (HTTPS + basic auth) -> 127.0.0.1:$REPLICA_PORT
OWNER_LOGIN=owner
PUBLIC_READ_ONLY=1                # 1: the public front passes only GET/HEAD (405 otherwise); writes stay on the VM
PASSWORD_FILE=/home/terryvanbelle/.bc23-replica-password   # clear text, mode 600, on the driver AND the VM
PASSWORD_LEN=20
CADDY_VERSION=2.11.7
CADDY_TARBALL="caddy_${CADDY_VERSION}_linux_amd64.tar.gz"
CADDY_BASE_URL="https://github.com/caddyserver/caddy/releases/download/v${CADDY_VERSION}"
CADDY_SUMS="caddy_${CADDY_VERSION}_checksums.txt"
# Pinned when the version was chosen (2026-10-07). The release checksums file lists SHA-512; both are checked.
CADDY_SHA256=727b91701a392de6ebc5027509f548bf39979e5216340d0faed8fa5e69c84f8b
CADDY_SHA512=a7a433a1b133efc3c8d10eb0b99d52a24b5ef5c322dc77f5282182b1c0402139ab83f3a99f0c52409df77d20123fb0b523edad8a66d8f5e49136197bf61ef0e7

# Installed layout on the VM (root-owned; systemd units run these copies, never the user-writable repo checkout)
LIB_DIR=/usr/local/lib/bc23-replica
ETC_DIR=/etc/bc23-replica          # hostname, owner.bcrypt, egress.nft
CADDY_BIN=/usr/local/bin/caddy
CADDYFILE=/etc/caddy/Caddyfile
NFT_TABLE=bc23_replica_egress      # table inet bc23_replica_egress
UNIT_EGRESS=bc23-replica-egress.service
UNIT_HOSTNAME=bc23-replica-hostname.service
UNIT_CADDY=bc23-replica-caddy.service
SLICE=bc23-replica.slice           # second, independent egress layer for replica services (IPAddressDeny)
# nftables.service's "flush ruleset" (start/reload of /etc/nftables.conf) would delete the egress table: a drop-in
# makes nftables.service load /etc/nftables.conf and egress.nft in one atomic transaction instead.
NFT_DROPIN=/etc/systemd/system/nftables.service.d/bc23-replica-egress.conf
NFT_COMBINED=/etc/bc23-replica/nftables-with-egress.nft
# D-Bus policy: $REPLICA_USER may not ask systemd-resolved (DNS), networkd or timesyncd to do network work for it
DBUS_POLICY=/etc/dbus-1/system.d/bc23-replica.conf

# The replica's own services (vm-setup.sh services): run as $REPLICA_USER from the operator's checkout on the VM
UNIT_API=bc23-replica-api.service          # web pages, replay viewer, JSON API on 127.0.0.1:$REPLICA_PORT
UNIT_WORKER=bc23-replica-worker.service    # the match runner (saturn replacement)
UNIT_AUTOSCRIM=bc23-replica-autoscrim.service
TIMER_AUTOSCRIM=bc23-replica-autoscrim.timer   # installed DISABLED; enable: systemctl enable --now bc23-replica-autoscrim.timer
AUTOSCRIM_CALENDAR='*-*-* 00/4:00:00'      # every 4 hours (galaxy's documented example cadence)
REPLICA_ENV=/etc/bc23-replica/replica.env  # EnvironmentFile of the services (written once; operator edits are kept)
REPLICA_REPO=/home/$OPERATOR_USER/projects/vibe/2023
REPLICA_JAVA_HOME=/home/$OPERATOR_USER/jdk/jdk8u504-b01
REPLICA_BENCH_ROOT=/home/$OPERATOR_USER/projects/vibe/bc23-benchmarks
REPLICA_SLOTS=4                            # concurrent engines of the worker (each ~1 GB); default for a new env file
REPLICA_CLI=/usr/local/bin/bc23-replica    # wrapper: the replica CLI as $REPLICA_USER with the services' environment
