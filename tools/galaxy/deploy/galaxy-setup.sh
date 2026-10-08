#!/usr/bin/env bash
# Root-side setup of the galaxy replica on battlecode-dev (Debian 12). Every step is idempotent. The driver runs it
# through tools/galaxy/deploy/deploy.sh. Doc: docs/galaxy/README.md. Requires the galaxy-lite host setup
# (tools/replica/deploy: user bcreplica, egress table, slice, Caddy).
#
#   sudo galaxy-setup.sh all [TARBALL]  install + packages + postgres + src + venv + dirs + secrets + env + units
#                                       + migrate + bootstrap + static + viewer + frontend + site + start
#   sudo galaxy-setup.sh install        copy these scripts to /usr/local/lib/bc23-galaxy (root-owned)
#   sudo galaxy-setup.sh packages       apt: postgresql-15, python3.11-venv (Debian mirror)
#   sudo galaxy-setup.sh postgres       unix-socket-only server (listen_addresses=''), role bcreplica, db siarnaq
#   sudo galaxy-setup.sh src TARBALL    /opt/bc23-galaxy/src from a `git archive` tarball of the pinned commit
#   sudo galaxy-setup.sh venv REQS      /opt/bc23-galaxy/venv: pip --require-hashes as the operator, then root-owned
#   sudo galaxy-setup.sh dirs | secrets | env | units | cli
#   sudo galaxy-setup.sh migrate | bootstrap | static
#   sudo galaxy-setup.sh viewer [SRC]   the 3.0.15 web client (pinned) + the galaxy viewer page
#   sudo galaxy-setup.sh frontend [DIR] copy the frontend build (default $FRONTEND_DIST) into /srv/bc23-galaxy
#   sudo galaxy-setup.sh site           enable the galaxy site in the Caddyfile (vm-setup.sh render)
#   sudo galaxy-setup.sh start | stop | status
#   sudo galaxy-setup.sh teardown [--purge-data]
#   galaxy-setup.sh print-site HOST HASH | print-units | print-env | print-cli    (no root; tests)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"
DOC=/home/$OPERATOR_USER/projects/vibe/2023/docs/galaxy/README.md
REPO_DIR=$REPLICA_REPO
die () { echo "galaxy-setup: $*" >&2; exit 1; }
say () { echo "== $*"; }
HOST_RE='^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$'
HASH_RE='^\$2[aby]\$[0-9]{2}\$[./A-Za-z0-9]{53}$'
UNITS="$UNIT_GWEB $UNIT_GRELAY $UNIT_GSATURN $UNIT_GSCHED $TIMER_GSCHED"
CSP="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; frame-src 'self'; worker-src 'self' blob:; manifest-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'"

# ---------------------------------------------------------------------------------------------------------- renderers
print_site () {  # $1 base host (<ip-with-dashes>.sslip.io), $2 bcrypt hash of the owner password
  local host="$GALAXY_SITE_PREFIX$1" hash="$2"
  [[ $host =~ $HOST_RE ]] || die "bad host name '$host'"
  [[ $hash =~ $HASH_RE ]] || die "bad bcrypt hash"
  cat <<EOF

# The galaxy replica (siarnaq + galaxy's frontend). Rendered by $GALAXY_LIB/galaxy-setup.sh print-site through
# vm-setup.sh render while $GALAXY_FLAG exists. Doc: $DOC
$host {
	log {
		output file /var/log/caddy/galaxy-access.log {
			roll_size 10MiB
			roll_keep 5
		}
	}
	header {
		-Server
		Strict-Transport-Security "max-age=31536000"
		X-Content-Type-Options nosniff
		X-Frame-Options SAMEORIGIN
		Referrer-Policy same-origin
		Content-Security-Policy "$CSP"
	}
	encode zstd gzip

	# Logged-in API calls carry the frontend's JWT instead of the basic-auth login: siarnaq authenticates them
	# (an invalid token is a 401 on every DRF view, AllowAny ones included). The views that run no
	# authentication at all (token issue/refresh/verify, password reset) stay behind basic auth.
	@bearer_api {
		path /api/*
		not path /api/token/* /api/user/password_reset/*
		header_regexp Authorization ^Bearer\s+[A-Za-z0-9._~+/=-]+$
	}
	handle @bearer_api {
		reverse_proxy 127.0.0.1:$GALAXY_PORT
	}

	# The web app manifest is fetched without credentials by browsers; it is a public static file.
	handle /manifest.json {
		root * $GALAXY_WWW/frontend
		file_server
	}

	handle {
		basic_auth {
			$OWNER_LOGIN $hash
		}
		@backend path /api/* /admin /admin/*
		handle @backend {
			reverse_proxy 127.0.0.1:$GALAXY_PORT {
				header_up -Authorization
				# This request carried the site's Basic login. A 401 answer to it (siarnaq's "not logged in" for the
				# logged-out frontend) makes browsers drop the cached login as rejected, and every later page asks
				# for the password again. Same answer, status 403, no challenge; the frontend treats both alike.
				@siarnaq_401 status 401
				handle_response @siarnaq_401 {
					header -WWW-Authenticate
					copy_response 403
				}
			}
		}
		handle_path /static/* {
			root * $GALAXY_WWW/static
			file_server
		}
		handle_path /storage/* {
			root * $GALAXY_WWW/storage
			header Cache-Control "private, no-cache"
			file_server {
				hide .tmp-*
			}
		}
		handle_path /viewer/* {
			root * $GALAXY_WWW/viewer
			file_server
		}
		handle /replay/* {
			respond 404
		}
		handle {
			root * $GALAXY_WWW/frontend
			try_files {path} /index.html
			file_server
		}
	}
}
EOF
}

print_env () {
  cat <<EOF
# Environment of the galaxy replica units ($UNIT_GWEB, $UNIT_GRELAY, $UNIT_GSATURN, $UNIT_GSCHED) and of
# $GALAXY_CLI. Written once by $GALAXY_LIB/galaxy-setup.sh env; later runs keep your edits. Restart the units after
# a change. Doc: $DOC
GALAXY_HOME=$GALAXY_HOME
GALAXY_STORAGE_ROOT=$GALAXY_WWW/storage
GALAXY_STATIC_ROOT=$GALAXY_WWW/static
GALAXY_REPO=$REPO_DIR
PYTHONPATH=$REPO_DIR/tools/galaxy/standins:$REPO_DIR/tools/galaxy:$GALAXY_SRC/backend
DJANGO_SETTINGS_MODULE=replica_settings
DJANGO_CONFIGURATION=Replica
SIARNAQ_REVISION=galaxy-${GALAXY_COMMIT:0:7}-bc23-replica
JAVA_HOME=$REPLICA_JAVA_HOME
GALAXY_COMPILE_SLOTS=$GALAXY_COMPILE_SLOTS
GALAXY_EXECUTE_SLOTS=$GALAXY_EXECUTE_SLOTS
GALAXY_GAME_TIMEOUT=1800
GALAXY_NACK_DELAY=10
GALAXY_GUNICORN_WORKERS=$GALAXY_GUNICORN_WORKERS
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
LANG=C.UTF-8
EOF
}

unit_common () {  # $1 extra InaccessiblePaths, $2 ReadWritePaths
  cat <<EOF
User=$REPLICA_USER
Group=$REPLICA_GROUP
Slice=$SLICE
UMask=0027
EnvironmentFile=$GALAXY_ENV
# Unix sockets bypass nftables: no varlink or D-Bus to systemd-resolved (DNS lookups made on our behalf).
InaccessiblePaths=-/run/systemd/resolve -/run/dbus/system_bus_socket$1
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$2
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
LockPersonality=yes
EOF
}

print_units () {  # every unit after a '### <name>' line
  local head="Documentation=file://$DOC
Requires=$UNIT_EGRESS
After=$UNIT_EGRESS network.target"
  local nftcheck="ExecStartPre=+/bin/sh -c 'exec /usr/sbin/nft list table inet $NFT_TABLE >/dev/null'"
  cat <<EOF
### $UNIT_GWEB
[Unit]
Description=bc23 galaxy replica: siarnaq (galaxy $GALAXY_COMMIT, Django + gunicorn) on 127.0.0.1:$GALAXY_PORT
$head postgresql.service $UNIT_HOSTNAME
Wants=postgresql.service

[Service]
Type=simple
$(unit_common "" "$GALAXY_HOME $GALAXY_WWW/storage")
WorkingDirectory=$GALAXY_SRC/backend
# host network namespace (Caddy and the relay connect to it): rely on the nftables table, refuse to start without it
$nftcheck
ExecStart=$GALAXY_VENV/bin/python -m gunicorn siarnaq.wsgi:application --bind 127.0.0.1:$GALAXY_PORT --workers \${GALAXY_GUNICORN_WORKERS} --timeout 120 --access-logfile - --forwarded-allow-ips 127.0.0.1
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
### $UNIT_GRELAY
[Unit]
Description=bc23 galaxy replica: loopback relay (saturn reports, Cloud Tasks) to siarnaq on 127.0.0.1:$GALAXY_PORT
$head

[Service]
Type=simple
$(unit_common "" "$GALAXY_HOME")
WorkingDirectory=$GALAXY_HOME
$nftcheck
ExecStart=/usr/bin/python3 $REPO_DIR/tools/galaxy/relay.py serve
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
### $UNIT_GSATURN
[Unit]
Description=bc23 galaxy replica: saturn (compile submissions, run matches; no network)
$head $UNIT_GRELAY
Wants=$UNIT_GRELAY

[Service]
Type=simple
$(unit_common " $GALAXY_HOME/secrets" "$GALAXY_HOME $GALAXY_WWW/storage")
WorkingDirectory=$GALAXY_HOME
# compiler and engines need no network at all: an own namespace holding only lo; reports go through the relay's
# unix socket. The relay's token key ($GALAXY_HOME/secrets) is not even visible here.
PrivateNetwork=yes
ExecStart=/usr/bin/python3 $REPO_DIR/tools/galaxy/saturn.py run
# SIGTERM to saturn only: it stops its engines, reports them interrupted (no failure counted) and nacks
KillMode=mixed
TimeoutStopSec=120
Restart=on-failure
RestartSec=30s

[Install]
WantedBy=multi-user.target
### $UNIT_GSCHED
[Unit]
Description=bc23 galaxy replica: Cloud Scheduler stand-in (fire recorded jobs due this minute)
$head

[Service]
Type=oneshot
$(unit_common "" "$GALAXY_HOME")
WorkingDirectory=$GALAXY_HOME
ExecStart=/usr/bin/python3 $REPO_DIR/tools/galaxy/relay.py fire-jobs
### $TIMER_GSCHED
[Unit]
Description=bc23 galaxy replica: Cloud Scheduler stand-in, every minute (autoscrim job: episode autoscrim_schedule)
Documentation=file://$DOC

[Timer]
OnCalendar=*-*-* *:*:00
AccuracySec=1s
Persistent=false
Unit=$UNIT_GSCHED

[Install]
WantedBy=timers.target
EOF
}

print_cli () {
  cat <<EOF
#!/usr/bin/env bash
# siarnaq's manage.py and the galaxy replica tools as user $REPLICA_USER with the units' environment ($GALAXY_ENV).
# Installed by $GALAXY_LIB/galaxy-setup.sh cli. Doc: $DOC
#   bc23-galaxy-manage <manage.py command ...>     e.g. migrate, showmigrations, shell -c '...', createsuperuser
#   bc23-galaxy-manage bootstrap <command>         tools/galaxy/bootstrap.py (status, purge-teams PREFIX, ...)
#   bc23-galaxy-manage relay status|fire-jobs      tools/galaxy/relay.py
#   bc23-galaxy-manage saturn status               tools/galaxy/saturn.py
set -euo pipefail
ENV_FILE=$GALAXY_ENV
RUN_AS=$REPLICA_USER
NFT_TABLE=$NFT_TABLE
PY=$GALAXY_VENV/bin/python
BACKEND=$GALAXY_SRC/backend
EOF
  cat <<'EOF'
# Commands run here (outside the units' slice and sandbox) are fenced by the nftables table alone: require it.
sudo -n /usr/sbin/nft list table inet "$NFT_TABLE" >/dev/null 2>&1 || {
  echo "bc23-galaxy-manage: egress table inet $NFT_TABLE is not loaded; refusing to run" >&2; exit 1; }
mapfile -t envs < <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' "$ENV_FILE")
repo=$(sed -n 's/^GALAXY_REPO=//p' "$ENV_FILE" | tail -1)
case "${1:-}" in
  bootstrap) shift; set -- "$repo/tools/galaxy/bootstrap.py" "$@" ;;
  relay) shift; PY=/usr/bin/python3; set -- "$repo/tools/galaxy/relay.py" "$@" ;;
  saturn) shift; PY=/usr/bin/python3; set -- "$repo/tools/galaxy/saturn.py" "$@" ;;
  '') echo "usage: bc23-galaxy-manage <manage.py command> | bootstrap ... | relay ... | saturn ..." >&2; exit 2 ;;
  *) set -- "$BACKEND/manage.py" "$@" ;;
esac
cd "$BACKEND"
exec sudo -u "$RUN_AS" env -i PATH=/usr/local/bin:/usr/bin:/bin HOME="/home/$RUN_AS" "${envs[@]}" "$PY" "$@"
EOF
}

case "${1:-}" in
  print-site) print_site "${2:?host}" "${3:?hash}"; exit 0 ;;
  print-units) print_units; exit 0 ;;
  print-env) print_env; exit 0 ;;
  print-cli) print_cli; exit 0 ;;
esac
[ "$(id -u)" = 0 ] || die "run as root (sudo)"
[ "$(hostname -s)" = "$BC_VM" ] || [ "${BC_REPLICA_ANY_HOST:-0}" = 1 ] || die "this is $(hostname -s), not $BC_VM"
id -u "$REPLICA_USER" >/dev/null 2>&1 || die "no user $REPLICA_USER: run tools/replica/deploy/deploy.sh first"
as_r () { (cd / && runuser -u "$REPLICA_USER" -- "$@"); }

# -------------------------------------------------------------------------------------------------------------- steps
install_step () {
  say "install scripts to $GALAXY_LIB"
  install -d -o root -g root -m 0755 "$GALAXY_LIB"
  if [ "$HERE" != "$GALAXY_LIB" ]; then
    install -o root -g root -m 0755 "$HERE/config.sh" "$HERE/galaxy-setup.sh" "$GALAXY_LIB/"
  fi
}

packages_step () {
  say "packages: postgresql-$PG_MAJOR, python3.11-venv (Debian mirror)"
  local need=()
  dpkg -s "postgresql-$PG_MAJOR" >/dev/null 2>&1 || need+=("postgresql-$PG_MAJOR")
  dpkg -s python3.11-venv >/dev/null 2>&1 || need+=(python3.11-venv)
  [ ${#need[@]} = 0 ] && { echo "already installed"; return 0; }
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${need[@]}" >/dev/null \
    || { apt-get update -q >/dev/null; DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${need[@]}" >/dev/null; }
}

postgres_step () {
  say "postgres $PG_MAJOR: unix socket only, role $REPLICA_USER, database $GALAXY_DB"
  local conf=/etc/postgresql/$PG_MAJOR/main/conf.d/bc23-galaxy.conf
  [ -d "$(dirname "$conf")" ] || die "no cluster $PG_MAJOR/main (packages step)"
  printf '%s\n' "# bc23 galaxy replica ($GALAXY_LIB/galaxy-setup.sh): no TCP listener at all; clients use the unix socket" \
    "listen_addresses = ''" > "$conf.new"
  if ! cmp -s "$conf.new" "$conf"; then mv -f "$conf.new" "$conf"; systemctl restart "postgresql@$PG_MAJOR-main"; else rm -f "$conf.new"; fi
  systemctl enable --quiet postgresql
  systemctl is-active --quiet "postgresql@$PG_MAJOR-main" || systemctl start "postgresql@$PG_MAJOR-main"
  local q
  q=$(runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$REPLICA_USER'")
  [ "$q" = 1 ] || runuser -u postgres -- psql -q -c "CREATE ROLE $REPLICA_USER LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE"
  q=$(runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_database WHERE datname='$GALAXY_DB'")
  [ "$q" = 1 ] || runuser -u postgres -- psql -q -c "CREATE DATABASE $GALAXY_DB OWNER $REPLICA_USER ENCODING 'UTF8' TEMPLATE template0"
  ss -ltnH | awk '{print $4}' | grep -E ':5432$' && die "postgres still listens on TCP" || true
}

src_step () {  # $1 tarball (git archive of $GALAXY_COMMIT)
  local tar="${1:?tarball}"
  say "galaxy source $GALAXY_COMMIT -> $GALAXY_SRC"
  [ -s "$tar" ] || die "no tarball $tar"
  local c; c=$(python3 -c 'import sys, tarfile; print(tarfile.open(sys.argv[1]).pax_headers.get("comment", ""))' "$tar")
  [ "$c" = "$GALAXY_COMMIT" ] || die "tarball is a git archive of '$c', not $GALAXY_COMMIT"
  install -d -o root -g root -m 0755 "$GALAXY_OPT"
  rm -rf "$GALAXY_SRC.new"; install -d -o root -g root -m 0755 "$GALAXY_SRC.new"
  tar -xf "$tar" -C "$GALAXY_SRC.new" --no-same-owner --no-same-permissions
  [ -f "$GALAXY_SRC.new/backend/manage.py" ] || die "tarball has no backend/manage.py"
  printf 'galaxy commit %s, git archive sha256 %s, installed %s\n' "$GALAXY_COMMIT" "$(sha256sum "$tar" | cut -c1-64)" \
    "$(date -u +%FT%TZ)" > "$GALAXY_SRC.new/REPLICA_SOURCE"
  chown -R root:root "$GALAXY_SRC.new"; chmod -R go-w,a+rX "$GALAXY_SRC.new"
  rm -rf "$GALAXY_SRC.old"; [ -e "$GALAXY_SRC" ] && mv "$GALAXY_SRC" "$GALAXY_SRC.old"
  mv "$GALAXY_SRC.new" "$GALAXY_SRC"; rm -rf "$GALAXY_SRC.old"
}

venv_step () {  # $1 requirements.txt (hash-locked)
  local reqs="${1:-$REPO_DIR/tools/galaxy/requirements.txt}"
  say "venv $GALAXY_VENV from $reqs (pip as $OPERATOR_USER, then root-owned)"
  [ -s "$reqs" ] || die "no $reqs"
  install -d -o root -g root -m 0755 "$GALAXY_OPT"
  local new="$GALAXY_VENV.new"
  rm -rf "$new"; install -d -o "$OPERATOR_USER" -g "$OPERATOR_USER" -m 0755 "$new"
  cp "$reqs" /tmp/bc23-galaxy-requirements.txt; chmod 0644 /tmp/bc23-galaxy-requirements.txt
  runuser -u "$OPERATOR_USER" -- python3 -m venv "$new"
  # every distribution is pinned by sha256; odfpy (sdist only) builds with the venv's own setuptools, no download
  runuser -u "$OPERATOR_USER" -- "$new/bin/python" -m pip install -q --disable-pip-version-check --no-input \
    --require-hashes --no-deps --no-build-isolation -r /tmp/bc23-galaxy-requirements.txt
  runuser -u "$OPERATOR_USER" -- "$new/bin/python" -m pip check
  rm -f /tmp/bc23-galaxy-requirements.txt
  if find "$new" -path '*/site-packages/google*' -maxdepth 6 | grep -q .; then die "a google package got into the venv"; fi
  chown -R root:root "$new"; chmod -R go-w "$new"
  rm -rf "$GALAXY_VENV.old"; [ -e "$GALAXY_VENV" ] && mv "$GALAXY_VENV" "$GALAXY_VENV.old"
  mv "$new" "$GALAXY_VENV"; rm -rf "$GALAXY_VENV.old"
  "$GALAXY_VENV/bin/python" -m pip freeze --disable-pip-version-check | wc -l | xargs echo "packages:"
}

dirs_step () {
  say "directories: $GALAXY_HOME (bcreplica), $GALAXY_WWW (root:caddy), $GALAXY_ETC"
  getent group caddy >/dev/null || die "no group caddy (run tools/replica/deploy/deploy.sh first)"
  install -d -o "$REPLICA_USER" -g "$REPLICA_GROUP" -m 2750 "$GALAXY_HOME"
  local d
  for d in spool storage-meta saturn run logs; do install -d -o "$REPLICA_USER" -g "$REPLICA_GROUP" -m 2750 "$GALAXY_HOME/$d"; done
  install -d -o "$REPLICA_USER" -g "$REPLICA_GROUP" -m 0700 "$GALAXY_HOME/secrets"
  install -d -o root -g caddy -m 0751 "$GALAXY_WWW"     # bcreplica traverses to storage/ and static/
  install -d -o "$REPLICA_USER" -g caddy -m 2750 "$GALAXY_WWW/storage" "$GALAXY_WWW/static"
  for d in bc23-replica-public bc23-replica-secure bc23-replica-ephemeral; do
    install -d -o "$REPLICA_USER" -g caddy -m 2750 "$GALAXY_WWW/storage/$d"
  done
  install -d -o root -g root -m 0755 "$GALAXY_ETC"
}

secrets_step () {
  say "secrets in $GALAXY_HOME/secrets (generated here, never printed)"
  as_r python3 - "$GALAXY_HOME/secrets" <<'PY'
import os, secrets, sys
d = sys.argv[1]
os.umask(0o077)
for name, make in (('django-secret-key', lambda: secrets.token_urlsafe(48)),
                   ('admin-password', lambda: secrets.token_urlsafe(24)),
                   ('oidc-hmac.key', lambda: secrets.token_hex(32))):
    p = os.path.join(d, name)
    if os.path.exists(p):
        print(f'kept {name}')
        continue
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as fh:
        fh.write(make() + '\n')
    print(f'created {name}')
PY
}

env_step () {
  install -d -o root -g root -m 0755 "$GALAXY_ETC"
  if [ ! -s "$GALAXY_ENV" ]; then print_env > "$GALAXY_ENV.new"; chmod 0644 "$GALAXY_ENV.new"; mv -f "$GALAXY_ENV.new" "$GALAXY_ENV"; say "wrote $GALAXY_ENV"
  else say "keeping $GALAXY_ENV"; fi
}

units_step () {
  say "units: $UNITS (the scheduler timer stays disabled)"
  [ -f "/etc/systemd/system/$UNIT_EGRESS" ] || die "no $UNIT_EGRESS (galaxy-lite host setup first)"
  local name
  for name in $UNITS; do
    print_units | awk -v u="### $name" '$0 == u {on = 1; next} /^### / {on = 0} on' > "/etc/systemd/system/$name.new"
    [ -s "/etc/systemd/system/$name.new" ] || die "no unit text for $name"
    mv -f "/etc/systemd/system/$name.new" "/etc/systemd/system/$name"
  done
  systemctl daemon-reload
  systemctl enable --quiet "$UNIT_GWEB" "$UNIT_GRELAY" "$UNIT_GSATURN"
}

cli_step () {
  print_cli > "$GALAXY_CLI.new"; chmod 0755 "$GALAXY_CLI.new"; mv -f "$GALAXY_CLI.new" "$GALAXY_CLI"
  say "installed $GALAXY_CLI"
}

egress_ports_step () {  # bcreplica must reach 127.0.0.1:$GALAXY_PORT (relay -> siarnaq)
  if nft list table inet "$NFT_TABLE" 2>/dev/null | grep -E "dport \{?[^}]*\b$GALAXY_PORT\b" >/dev/null; then
    echo "egress table already allows loopback port $GALAXY_PORT"; return 0; fi
  case " $REPLICA_LO_PORTS " in *" $GALAXY_PORT "*) ;; *) die "add $GALAXY_PORT to REPLICA_LO_PORTS in tools/replica/deploy/config.sh" ;; esac
  replica_install_step
  bash "$REPO_DIR/tools/replica/deploy/vm-setup.sh" egress
}

replica_install_step () {  # the galaxy-lite host scripts from the checkout (vm-setup.sh renders the galaxy site too)
  [ -f "$REPO_DIR/tools/replica/deploy/vm-setup.sh" ] || die "no $REPO_DIR/tools/replica/deploy/vm-setup.sh"
  bash "$REPO_DIR/tools/replica/deploy/vm-setup.sh" install
}

migrate_step () { say "migrate"; "$GALAXY_CLI" migrate --noinput; }

bootstrap_step () {
  say "bootstrap: episode bc23 + maps, service user, superuser owner (password from $PASSWORD_FILE on stdin)"
  [ -s "$PASSWORD_FILE" ] || die "no $PASSWORD_FILE"
  "$GALAXY_CLI" bootstrap all < "$PASSWORD_FILE"
}

static_step () { say "collectstatic -> $GALAXY_WWW/static"; "$GALAXY_CLI" collectstatic --noinput --clear -v 0; }

viewer_step () {  # $1 download dir
  local src="${1:-$VIEWER_DOWNLOAD}"
  say "viewer: $src -> $GALAXY_WWW/viewer"
  (umask 022; python3 "$REPO_DIR/tools/galaxy/viewer_page.py" install "$src" "$GALAXY_WWW/viewer")
  chown -R root:caddy "$GALAXY_WWW/viewer"; chmod -R u=rwX,g=rX,o= "$GALAXY_WWW/viewer"
}

frontend_step () {  # $1 build dir (index.html + assets)
  local src="${1:-$FRONTEND_DIST}" dst="$GALAXY_WWW/frontend"
  if [ ! -f "$src/index.html" ]; then
    say "frontend: no build at $src; installing a placeholder page"
    rm -rf "$dst.new"; install -d -m 0750 -o root -g caddy "$dst.new"
    printf '%s\n' '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Battlecode</title></head>' \
      '<body><p>The galaxy frontend is not installed yet (tools/galaxy/frontend/build.sh, then' \
      'galaxy-setup.sh frontend). The API is at <a href="/api/specs/">/api/</a>.</p></body></html>' > "$dst.new/index.html"
  else
    say "frontend: $src -> $dst"
    [ -f "$src/REPLICA_BUILD.txt" ] && cat "$src/REPLICA_BUILD.txt"   # tools/galaxy/frontend/build.sh (bundle vetted)
    rm -rf "$dst.new"; cp -r "$src" "$dst.new"
  fi
  chown -R root:caddy "$dst.new"; chmod -R u=rwX,g=rX,o= "$dst.new"
  rm -rf "$dst.old"; [ -e "$dst" ] && mv "$dst" "$dst.old"
  mv "$dst.new" "$dst"; rm -rf "$dst.old"
}

site_step () {
  say "Caddy: galaxy site on"
  install -d -o root -g root -m 0755 "$ETC_DIR"
  touch "$GALAXY_FLAG"
  "$LIB_DIR/vm-setup.sh" render
}

start_step () {
  say "start $UNIT_GRELAY $UNIT_GWEB $UNIT_GSATURN"
  systemctl restart "$UNIT_GRELAY" "$UNIT_GWEB"
  systemctl restart "$UNIT_GSATURN"
  sleep 3
  local u
  for u in "$UNIT_GRELAY" "$UNIT_GWEB" "$UNIT_GSATURN"; do systemctl is-active --quiet "$u" || die "$u did not start (journalctl -u $u)"; done
}

stop_step () { systemctl stop "$UNIT_GSATURN" "$UNIT_GWEB" "$UNIT_GRELAY" "$TIMER_GSCHED" 2>/dev/null || true; }

status_step () {
  local u
  for u in $UNITS postgresql.service; do
    printf '%-32s enabled=%-9s active=%s\n' "$u" "$(systemctl is-enabled "$u" 2>/dev/null || true)" "$(systemctl is-active "$u" 2>/dev/null || true)"
  done
  [ -f "$GALAXY_FLAG" ] && [ -s "$ETC_DIR/hostname" ] && echo "url: https://$GALAXY_SITE_PREFIX$(head -1 "$ETC_DIR/hostname")/"
  ss -ltnH "sport = :$GALAXY_PORT" | awk '{print "listen", $4}'
  [ -f "$GALAXY_SRC/REPLICA_SOURCE" ] && cat "$GALAXY_SRC/REPLICA_SOURCE"
  [ -x "$GALAXY_CLI" ] && "$GALAXY_CLI" saturn status && "$GALAXY_CLI" relay status
}

teardown_step () {  # [--purge-data]
  say "teardown: galaxy units, CLI, Caddy site"
  systemctl disable --now $UNITS 2>/dev/null || true
  local u; for u in $UNITS; do rm -f "/etc/systemd/system/$u"; done
  systemctl daemon-reload
  rm -f "$GALAXY_CLI" "$GALAXY_FLAG"
  [ -s "$ETC_DIR/hostname" ] && [ -s "$ETC_DIR/owner.bcrypt" ] && "$LIB_DIR/vm-setup.sh" render || true
  if [ "${1:-}" = --purge-data ]; then
    runuser -u postgres -- psql -q -c "DROP DATABASE IF EXISTS $GALAXY_DB" || true
    rm -rf "$GALAXY_HOME" "$GALAXY_WWW" "$GALAXY_OPT" "$GALAXY_ETC"
    echo "purged data, source, venv (postgresql itself stays installed)"
  else
    echo "kept $GALAXY_HOME, $GALAXY_WWW, $GALAXY_OPT, $GALAXY_ETC and the database $GALAXY_DB"
  fi
  rm -rf "$GALAXY_LIB"
}

step="${1:-}"; shift || true
case "$step" in
  all)
    install_step; replica_install_step; packages_step; postgres_step
    [ -n "${1:-}" ] && src_step "$1"
    [ -f "$GALAXY_SRC/backend/manage.py" ] || die "no galaxy source in $GALAXY_SRC (pass the tarball)"
    [ -x "$GALAXY_VENV/bin/python" ] || venv_step
    dirs_step; secrets_step; env_step; egress_ports_step; units_step; cli_step
    migrate_step; bootstrap_step; static_step; viewer_step; frontend_step; site_step; start_step; status_step ;;
  install) install_step ;;
  packages) packages_step ;;
  postgres) postgres_step ;;
  src) src_step "${1:-}" ;;
  venv) venv_step "${1:-}" ;;
  dirs) dirs_step ;;
  secrets) secrets_step ;;
  env) env_step ;;
  egress) egress_ports_step ;;
  units) units_step ;;
  cli) cli_step ;;
  migrate) migrate_step ;;
  bootstrap) bootstrap_step ;;
  static) static_step ;;
  viewer) viewer_step "${1:-}" ;;
  frontend) frontend_step "${1:-}" ;;
  site) site_step ;;
  start) start_step ;;
  stop) stop_step ;;
  status) status_step ;;
  teardown) teardown_step "${1:-}" ;;
  *) sed -n '2,/^set -e/{/^#/p}' "$0" >&2; exit 2 ;;
esac
