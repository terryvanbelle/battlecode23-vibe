# shellcheck shell=bash
# Settings of the galaxy replica deployment (siarnaq + stand-ins + saturn replacement + relay), sourced, never run.
# Builds on the galaxy-lite host setup (tools/replica/deploy/config.sh: user bcreplica, egress table, slice, Caddy).
# Doc: docs/galaxy/README.md.
_GHERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$_GHERE/../../replica/deploy/config.sh" ]; then
  # shellcheck source=../../replica/deploy/config.sh
  source "$_GHERE/../../replica/deploy/config.sh"
else
  # shellcheck source=/dev/null
  source /usr/local/lib/bc23-replica/config.sh
fi

GALAXY_COMMIT=f343088f4d471b0664b2ff41129f0435a8dca1c2   # github.com/battlecode/galaxy (MIT), pinned
GALAXY_OPT=/opt/bc23-galaxy             # root-owned, read-only for the services
GALAXY_SRC=$GALAXY_OPT/src              # git archive of $GALAXY_COMMIT (siarnaq is $GALAXY_SRC/backend, unmodified)
GALAXY_VENV=$GALAXY_OPT/venv            # Python 3.11 venv: tools/galaxy/requirements.txt (hash-locked, PyPI)
GALAXY_HOME=/home/$REPLICA_USER/galaxy  # bcreplica: secrets/ spool/ storage-meta/ saturn/ run/ (+ frontend-dist/)
GALAXY_WWW=/srv/bc23-galaxy             # root:caddy 0751, what Caddy serves: frontend/ viewer/ static/ storage/
GALAXY_ETC=/etc/bc23-galaxy
GALAXY_ENV=$GALAXY_ETC/galaxy.env       # EnvironmentFile of the units and the CLI (written once; edits are kept)
GALAXY_LIB=/usr/local/lib/bc23-galaxy   # root-owned copies of these scripts
GALAXY_CLI=/usr/local/bin/bc23-galaxy-manage
GALAXY_FLAG=$ETC_DIR/galaxy.enabled     # present: vm-setup.sh render adds the galaxy site to the Caddyfile
GALAXY_PORT=8024                        # siarnaq (gunicorn) on 127.0.0.1 only; in REPLICA_LO_PORTS
GALAXY_SITE_PREFIX=galaxy.              # the site is galaxy.<ip-with-dashes>.sslip.io
GALAXY_DB=siarnaq                       # PostgreSQL database, owned by role $REPLICA_USER (peer auth, unix socket)
PG_MAJOR=15
UNIT_GWEB=bc23-galaxy-web.service       # siarnaq under gunicorn
UNIT_GRELAY=bc23-galaxy-relay.service   # saturn reports + Cloud Tasks -> siarnaq on loopback
UNIT_GSATURN=bc23-galaxy-saturn.service # compile + execute (PrivateNetwork=yes)
UNIT_GSCHED=bc23-galaxy-scheduler.service
TIMER_GSCHED=bc23-galaxy-scheduler.timer   # installed DISABLED (autoscrim cadence; the lead's decision)
GALAXY_COMPILE_SLOTS=1                  # galaxy: saturn-compile parallelism 1
GALAXY_EXECUTE_SLOTS=5                  # concurrent engines (each ~1 GB); default for a new env file (5 since galaxy-lite retired)
GALAXY_GUNICORN_WORKERS=3
VIEWER_DOWNLOAD=/home/$OPERATOR_USER/projects/vibe/bc23-viewer-3.0.15   # docs/replica/VIEWER.md
FRONTEND_DIST=$GALAXY_HOME/frontend-dist   # where tools/galaxy/frontend/build.sh installs by default
