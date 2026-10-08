#!/usr/bin/env bash
# Check the replica's isolation and web front. Run on the driver; prints PASS/FAIL/SKIP lines, exits 1 on any FAIL.
#   tools/replica/deploy/verify.sh            VM isolation checks (over ssh) + public web checks + GCP firewall audit
#   tools/replica/deploy/verify.sh vm | web | fw   one part (web includes fw)
# Never tests egress against Battlecode/MIT hosts: if the lockdown were broken, the test itself would contact them.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"
# shellcheck source=../../vm.sh
source "$HERE/../../vm.sh"; IP="${IP:-10.138.0.3}"
what="${1:-all}"; rc=0

vm_checks () {
  echo "--- on $BC_VM"
  gssh "bash -s" <<'VMEOF' || rc=1
set -uo pipefail
source /usr/local/lib/bc23-replica/config.sh || { echo "FAIL no /usr/local/lib/bc23-replica/config.sh (run deploy.sh)"; exit 1; }
R=$REPLICA_USER; fail=0
pass () { echo "PASS $*"; }
bad () { echo "FAIL $*"; fail=1; }
must_fail () { local d="$1"; shift; if "$@" >/dev/null 2>&1; then bad "$d (it succeeded)"; else pass "$d: blocked"; fi; }
must_work () { local d="$1"; shift; if "$@" >/dev/null 2>&1; then pass "$d: works"; else bad "$d (it failed)"; fi; }
as_r () { sudo -u "$R" "$@"; }
MD=http://169.254.169.254/computeMetadata/v1

# user
[ "$(id -nG "$R")" = "$REPLICA_GROUP" ] && pass "$R has no supplementary groups" || bad "$R groups: $(id -nG "$R")"
[ "$(getent passwd "$R" | cut -d: -f7)" = /usr/sbin/nologin ] && pass "$R shell is nologin" || bad "$R shell"
case "$(sudo getent shadow "$R" | cut -d: -f2)" in '!'*|'*'*) pass "$R password locked" ;; *) bad "$R password not locked" ;; esac
sudo -l -U "$R" 2>&1 | grep 'not allowed' >/dev/null && pass "$R has no sudo rights" || bad "$R may use sudo"
leak=$(sudo find "/home/$R" -maxdepth 3 \( -path '*/.config/gcloud' -o -name '.boto' -o -name '.netrc' -o -name '.git-credentials' \
  -o -name '*.json' -path '*cred*' -o -name '.ssh' \) 2>/dev/null | head -3)
[ -z "$leak" ] && pass "no credential files under /home/$R" || bad "credential-like files: $leak"
sudo -u "$R" env | grep -E '^(GOOGLE_APPLICATION_CREDENTIALS|CLOUDSDK_)' >/dev/null && bad "$R env has Google credentials vars" || pass "$R env has no Google credential vars"
id -nG "$OPERATOR_USER" | tr ' ' '\n' | grep -x "$REPLICA_GROUP" >/dev/null && pass "$OPERATOR_USER in group $REPLICA_GROUP" || bad "$OPERATOR_USER not in $REPLICA_GROUP"
[ "$(stat -c %a "$REPLICA_HOME")" = 2750 ] && pass "REPLICA_HOME $REPLICA_HOME mode 2750" || bad "REPLICA_HOME mode $(stat -c %a "$REPLICA_HOME" 2>&1)"

# lockdown loaded and persistent
[ "$(systemctl is-enabled "$UNIT_EGRESS")" = enabled ] && pass "$UNIT_EGRESS enabled" || bad "$UNIT_EGRESS not enabled"
systemctl is-active --quiet "$UNIT_EGRESS" && pass "$UNIT_EGRESS active" || bad "$UNIT_EGRESS not active"
sudo nft list table inet "$NFT_TABLE" 2>/dev/null | grep "skuid $(id -u "$R") " >/dev/null && pass "nft table matches uid $(id -u "$R")" || bad "nft table missing"

# egress as the replica user: everything off-host fails
must_fail "$R: curl https://example.com" as_r curl -sS -m 10 -o /dev/null https://example.com
must_fail "$R: curl http://1.1.1.1 (no DNS involved)" as_r curl -sS -m 5 -o /dev/null http://1.1.1.1/
must_fail "$R: curl http://169.254.169.254" as_r curl -sS -m 5 -o /dev/null http://169.254.169.254/
must_fail "$R: metadata service-account token" as_r curl -fsS -m 5 -H 'Metadata-Flavor: Google' "$MD/instance/service-accounts/default/token"
must_fail "$R: DNS lookup of example.com" as_r python3 -c "import socket; socket.getaddrinfo('example.com', 443)"
must_fail "$R: loopback DNS stub 127.0.0.53" as_r python3 -c "
import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(3)
s.sendto(bytes.fromhex('123401000001000000000000076578616d706c6503636f6d0000010001'), ('127.0.0.53', 53)); s.recv(512)"
must_fail "$R: loopback MTA 127.0.0.1:25" as_r python3 -c "import socket; socket.create_connection(('127.0.0.1', 25), 3)"
must_fail "$R: loopback port 2019 (Caddy admin default)" as_r python3 -c "import socket; socket.create_connection(('127.0.0.1', 2019), 3)"
# unix-socket paths around nftables, and nftables.service's "flush ruleset"
must_fail "$R: resolvectl query example.com (D-Bus to systemd-resolved)" as_r resolvectl query example.com
must_work "$OPERATOR_USER: resolvectl query example.com (control)" resolvectl query example.com
if [ -n "${NFT_DROPIN:-}" ] && [ -f "$NFT_DROPIN" ] && systemctl show -p ExecStart nftables.service | grep -F "$NFT_COMBINED" >/dev/null; then
  pass "nftables.service loads /etc/nftables.conf and the egress table in one transaction (drop-in)"
  sudo nft -c -f "$NFT_COMBINED" >/dev/null 2>&1 && pass "$NFT_COMBINED passes nft -c" || bad "$NFT_COMBINED fails nft -c"
else bad "no nftables.service drop-in: starting or reloading nftables.service would flush the egress table (re-run deploy.sh)"; fi
[ -n "${DBUS_POLICY:-}" ] && [ -f "$DBUS_POLICY" ] && pass "D-Bus policy $DBUS_POLICY present" || bad "no D-Bus policy for $R"
# the slice layer on its own (as root, so nftables plays no part), with a control run outside the slice
must_work "root via systemd-run outside $SLICE: metadata server" sudo systemd-run --quiet --wait --pipe --collect \
  curl -fsS -m 5 -H 'Metadata-Flavor: Google' "$MD/instance/id"
must_fail "root inside $SLICE: metadata server" sudo systemd-run --quiet --wait --pipe --collect --slice="$SLICE" \
  curl -fsS -m 5 -H 'Metadata-Flavor: Google' "$MD/instance/id"

# everyone else unaffected
must_work "$OPERATOR_USER: curl https://example.com" curl -sS -m 15 -o /dev/null https://example.com
must_work "$OPERATOR_USER: metadata server" curl -fsS -m 5 -H 'Metadata-Flavor: Google' "$MD/instance/id"
must_work "root: curl https://example.com" sudo curl -sS -m 15 -o /dev/null https://example.com
must_work "root: metadata server" sudo curl -fsS -m 5 -H 'Metadata-Flavor: Google' "$MD/instance/id"

# loopback to the replica port is allowed (temporary server if the port is free)
port=${REPLICA_LO_PORTS%% *}
if ss -ltn | awk '{print $4}' | grep -E "[:.]$port\$" >/dev/null; then
  echo "SKIP temporary server: port $port in use (assuming it is the replica)"
  must_work "$R: connect 127.0.0.1:$port" as_r python3 -c "import socket; socket.create_connection(('127.0.0.1', $port), 3)"
else
  sudo -u "$R" python3 -m http.server "$port" --bind 127.0.0.1 --directory /usr/share/doc/curl >/dev/null 2>&1 &
  srv=$!; sleep 1.5
  must_work "$R: http://127.0.0.1:$port (own server)" as_r curl -fsS -m 5 -o /dev/null "http://127.0.0.1:$port/"
  must_work "$OPERATOR_USER: http://127.0.0.1:$port ($R's replies)" curl -fsS -m 5 -o /dev/null "http://127.0.0.1:$port/"
  sudo kill "$srv" 2>/dev/null; wait "$srv" 2>/dev/null
fi

# the replica's own services (vm-setup.sh services); retired since 2026-10-08 (vm-setup.sh retire-lite)
if [ -n "${LITE_RETIRED_FLAG:-}" ] && [ -f "$LITE_RETIRED_FLAG" ]; then
  for u in "$UNIT_API" "$UNIT_WORKER" "$TIMER_AUTOSCRIM"; do
    a=$(systemctl is-active "$u" 2>/dev/null || true); e=$(systemctl is-enabled "$u" 2>/dev/null || true)
    case "$a $e" in active*|*" enabled") bad "galaxy-lite retired, but $u is $a/$e" ;; *) pass "galaxy-lite retired: $u $a/$e" ;; esac
  done
  bound=$(ss -ltnH "sport = :$REPLICA_PORT" | awk '{print $4}' | sort -u | tr '\n' ' ')
  [ -z "$bound" ] && pass "galaxy-lite retired: nothing listens on port $REPLICA_PORT" || bad "port $REPLICA_PORT still bound: $bound"
  [ ! -e "$REPLICA_HOME/replica.db" ] && pass "galaxy-lite data archived ($(ls -d "$REPLICA_HOME"/archive/*-retired 2>/dev/null | tail -1))" \
    || bad "galaxy-lite retired, but $REPLICA_HOME/replica.db is still in place"
elif [ -n "${UNIT_API:-}" ] && [ -f "/etc/systemd/system/$UNIT_API" ]; then
  for u in "$UNIT_API" "$UNIT_WORKER"; do
    systemctl is-active --quiet "$u" && pass "$u active" || bad "$u not active"
    pid=$(systemctl show -p MainPID --value "$u")
    [ "$(ps -o user= -p "$pid" 2>/dev/null)" = "$R" ] && pass "$u runs as $R" || bad "$u user: $(ps -o user= -p "$pid" 2>&1)"
    [ "$(systemctl show -p Slice --value "$u")" = "$SLICE" ] && pass "$u in $SLICE" || bad "$u slice: $(systemctl show -p Slice --value "$u")"
  done
  for u in "$UNIT_API" "$UNIT_WORKER"; do
    case "$(systemctl show -p InaccessiblePaths --value "$u")" in
      *"/run/systemd/resolve"*"/run/dbus/system_bus_socket"*) pass "$u: no varlink/D-Bus to systemd-resolved" ;;
      *) bad "$u: systemd-resolved sockets reachable (unit predates the fix; re-run deploy.sh, restart it)" ;; esac
  done
  wpid=$(systemctl show -p MainPID --value "$UNIT_WORKER")
  if [ "$(systemctl show -p PrivateNetwork --value "$UNIT_WORKER")" = yes ] && [ "${wpid:-0}" != 0 ] \
     && [ "$(sudo readlink "/proc/$wpid/ns/net")" != "$(sudo readlink /proc/1/ns/net)" ]; then
    pass "$UNIT_WORKER and its engines run in a private network namespace"
    links=$(sudo nsenter -t "$wpid" -n ip -o link show | awk -F': ' '{print $2}' | tr '\n' ' ')
    [ "$links" = "lo " ] && pass "worker namespace has only lo" || bad "worker namespace links: $links"
    must_fail "inside the worker namespace (as root): http://1.1.1.1" sudo nsenter -t "$wpid" -n curl -sS -m 5 -o /dev/null http://1.1.1.1/
  else bad "$UNIT_WORKER shares the host network namespace (PrivateNetwork=$(systemctl show -p PrivateNetwork --value "$UNIT_WORKER"))"; fi
  bound=$(ss -ltnH "sport = :$REPLICA_PORT" | awk '{print $4}' | sort -u | tr '\n' ' ')
  [ "$bound" = "127.0.0.1:$REPLICA_PORT " ] && pass "port $REPLICA_PORT bound to 127.0.0.1 only" || bad "port $REPLICA_PORT bound to: $bound"
  must_work "$OPERATOR_USER: replica ladder page on 127.0.0.1:$REPLICA_PORT" curl -fsS -m 10 -o /dev/null "http://127.0.0.1:$REPLICA_PORT/"
  echo "INFO $TIMER_AUTOSCRIM: $(systemctl is-enabled "$TIMER_AUTOSCRIM" 2>/dev/null) (installed disabled; enabling it is the operator's call)"
fi

# the galaxy replica (tools/galaxy/deploy): siarnaq, relay, saturn, PostgreSQL, stand-ins
if [ -f /usr/local/lib/bc23-galaxy/config.sh ] && [ -f "/etc/systemd/system/bc23-galaxy-web.service" ]; then
  source /usr/local/lib/bc23-galaxy/config.sh
  for u in "$UNIT_GWEB" "$UNIT_GRELAY" "$UNIT_GSATURN"; do
    systemctl is-active --quiet "$u" && pass "$u active" || bad "$u not active"
    pid=$(systemctl show -p MainPID --value "$u")
    [ "$(ps -o user= -p "$pid" 2>/dev/null)" = "$R" ] && pass "$u runs as $R" || bad "$u user: $(ps -o user= -p "$pid" 2>&1)"
    [ "$(systemctl show -p Slice --value "$u")" = "$SLICE" ] && pass "$u in $SLICE" || bad "$u slice: $(systemctl show -p Slice --value "$u")"
    case "$(systemctl show -p InaccessiblePaths --value "$u")" in
      *"/run/systemd/resolve"*"/run/dbus/system_bus_socket"*) pass "$u: no varlink/D-Bus to systemd-resolved" ;;
      *) bad "$u: systemd-resolved sockets reachable" ;; esac
  done
  [ "$(systemctl is-enabled "$TIMER_GSCHED" 2>/dev/null)" != enabled ] && echo "INFO $TIMER_GSCHED: disabled (autoscrim rounds off; enabling it is the lead's call)" \
    || echo "INFO $TIMER_GSCHED: enabled (autoscrim rounds follow the episode's autoscrim_schedule)"
  spid=$(systemctl show -p MainPID --value "$UNIT_GSATURN")
  if [ "$(systemctl show -p PrivateNetwork --value "$UNIT_GSATURN")" = yes ] && [ "${spid:-0}" != 0 ] \
     && [ "$(sudo readlink "/proc/$spid/ns/net")" != "$(sudo readlink /proc/1/ns/net)" ]; then
    pass "$UNIT_GSATURN (compiler and engines) runs in a private network namespace"
    links=$(sudo nsenter -t "$spid" -n ip -o link show | awk -F': ' '{print $2}' | tr '\n' ' ')
    [ "$links" = "lo " ] && pass "saturn namespace has only lo" || bad "saturn namespace links: $links"
    must_fail "inside the saturn namespace (as root): http://1.1.1.1" sudo nsenter -t "$spid" -n curl -sS -m 5 -o /dev/null http://1.1.1.1/
    must_fail "inside the saturn namespace (as root): siarnaq on 127.0.0.1:$GALAXY_PORT" sudo nsenter -t "$spid" -n curl -sS -m 5 -o /dev/null "http://127.0.0.1:$GALAXY_PORT/"
    n=$(sudo nsenter -t "$spid" -m ls -A "$GALAXY_HOME/secrets" 2>/dev/null | wc -l)
    [ "$n" = 0 ] && pass "saturn cannot see $GALAXY_HOME/secrets (token key)" || bad "saturn sees $n file(s) in $GALAXY_HOME/secrets"
  else bad "$UNIT_GSATURN shares the host network namespace"; fi
  bound=$(ss -ltnH "sport = :$GALAXY_PORT" | awk '{print $4}' | sort -u | tr '\n' ' ')
  [ "$bound" = "127.0.0.1:$GALAXY_PORT " ] && pass "port $GALAXY_PORT bound to 127.0.0.1 only" || bad "port $GALAXY_PORT bound to: $bound"
  must_work "$R: connect 127.0.0.1:$GALAXY_PORT (relay -> siarnaq)" as_r python3 -c "import socket; socket.create_connection(('127.0.0.1', $GALAXY_PORT), 3)"
  [ -S "$GALAXY_HOME/run/relay.sock" ] && [ "$(sudo stat -c '%a %U' "$GALAXY_HOME/run/relay.sock")" = "600 $R" ] \
    && pass "relay socket mode 600 $R" || bad "relay socket: $(sudo stat -c '%a %U' "$GALAXY_HOME/run/relay.sock" 2>&1)"
  [ -z "$(sudo ss -ltnH 'sport = :5432')" ] && pass "PostgreSQL has no TCP listener (unix socket only)" || bad "PostgreSQL listens on TCP 5432"
  [ "$(sudo runuser -u postgres -- psql -tAc 'SHOW listen_addresses' 2>/dev/null)" = "" ] && pass "postgres listen_addresses is empty" || bad "postgres listen_addresses not empty"
  g=$(sudo find "$GALAXY_VENV" -path '*site-packages/google*' -maxdepth 6 2>/dev/null | head -3)
  [ -z "$g" ] && pass "venv holds no Google client library" || bad "google packages in the venv: $g"
  aud=$(sudo "$GALAXY_CLI" bootstrap audit 2>/dev/null | grep -v '^{')
  echo "$aud" | grep -E '^(own|link|external) ' | sed 's/^/INFO host in config: /'
  echo "$aud" | grep -qx 'external hosts: none' && pass "no external host in siarnaq's settings, episode or staff e-mails" \
    || bad "external hosts in the running configuration: $(echo "$aud" | sed -n 's/^external hosts: //p')"
  echo "$aud" | grep -q '^stand-ins: True' && pass "siarnaq imports every google.* module from the stand-ins" || bad "stand-ins: $(echo "$aud" | grep stand-ins)"
  echo "$aud" | grep -qx 'actions: GCLOUD_ENABLE_ACTIONS=True EMAIL_ENABLED=False EMAIL_BACKEND=replica_gcp.mail.DropEmailBackend DEBUG=False' \
    && pass "GCLOUD_ENABLE_ACTIONS on, e-mail off (drop backend), DEBUG off" || bad "settings: $(echo "$aud" | grep '^actions')"
fi

# listeners in the host namespace: bcreplica binds loopback only; nothing behind the internet-open RDP port
uid=$(id -u "$R")
l=$(sudo ss -ltnupeH | awk -v u=" uid:$uid " 'index($0, u) {print $5}' | grep -vE '^(127\.|\[::1\]|\[::ffff:127\.)' | sort -u | tr '\n' ' ')
[ -z "$l" ] && pass "$R listens on loopback only" || bad "$R listens on: $l"
[ -z "$(sudo ss -ltnH 'sport = :3389')" ] && pass "nothing listens on tcp/3389 (open to the internet by default-allow-rdp)" \
  || bad "a listener on tcp/3389, which default-allow-rdp opens to the internet"
echo "INFO non-loopback listeners (reachable from the VPC; from the internet only where the GCP firewall opens them):" \
  "$(sudo ss -ltnupH | awk '$5 !~ /^(127\.|\[::1\]|\[::ffff:127\.)/ {split($7, p, "\""); print $1 "/" $5 "(" p[2] ")"}' | sort -u | tr '\n' ' ')"

# web front
if [ -x "$CADDY_BIN" ]; then
  systemctl is-active --quiet "$UNIT_CADDY" && pass "$UNIT_CADDY active" || bad "$UNIT_CADDY not active"
  [ "$(systemctl is-enabled "$UNIT_HOSTNAME")" = enabled ] && pass "$UNIT_HOSTNAME enabled (boot refresh)" || bad "$UNIT_HOSTNAME not enabled"
  [ "$(ps -o user= -C caddy | sort -u)" = caddy ] && pass "caddy runs as user caddy" || bad "caddy user: $(ps -o user= -C caddy)"
  ports=$(sudo ss -ltnpH | awk '/"caddy"/ {print $4}' | sort -u | tr '\n' ' ')
  case "$ports" in "*:443 *:80 "|"*:80 *:443 ") pass "caddy listens on 80 and 443 only (admin API on a unix socket)" ;;
    *) bad "caddy listens on: $ports" ;; esac
  [ "$(sudo stat -c '%a %U:%G' "$CADDYFILE")" = "640 root:caddy" ] && pass "Caddyfile 640 root:caddy" || bad "Caddyfile perms"
  [ "$(stat -c '%a %U' "$PASSWORD_FILE" 2>/dev/null)" = "600 $OPERATOR_USER" ] && pass "VM password file mode 600" || bad "VM password file"
  sudo grep -qFf "$PASSWORD_FILE" "$CADDYFILE" && bad "clear password appears in the Caddyfile" || pass "Caddyfile holds no clear password"
  sudo grep -q 'basic_auth' "$CADDYFILE" && pass "Caddyfile has basic_auth" || bad "no basic_auth"
fi
exit $fail
VMEOF
}

web_checks () {
  echo "--- from the driver"
  local host fail=0 got
  host=$(gssh "head -1 $ETC_DIR/hostname")
  [ -n "$host" ] || { echo "FAIL no host name on the VM"; rc=1; return; }
  echo "url: https://$host/"
  pass () { echo "PASS $*"; }
  bad () { echo "FAIL $*"; fail=1; }
  got=$(curl -sS -m 20 -o /dev/null -w '%{http_code} %{redirect_url}' "http://$host/" || true)
  case "$got" in 30[178]" https://$host/") pass "http redirects to https ($got)" ;; *) bad "http: $got" ;; esac
  if gssh "test -f $LITE_RETIRED_FLAG"; then         # galaxy-lite retired: its host name only points at the galaxy site
    got=$(curl -sS -m 20 -o /dev/null -w '%{http_code} %{redirect_url} %{ssl_verify_result}' "https://$host/bc23/rankings?x=1" || true)
    [ "$got" = "302 https://galaxy.$host/bc23/rankings?x=1 0" ] && pass "galaxy-lite retired: https://$host/ redirects to the galaxy site ($got)" \
      || bad "retired host: $got"
    got=$(curl -sS -m 20 -H 'Host: 127.0.0.1:8023' -o /dev/null -w '%{http_code} %{size_download}' "https://$host/replica/status" || true)
    case "$got" in 30*|401*|*" 0") pass "foreign Host header is not proxied ($got)" ;; *) bad "foreign Host header: $got" ;; esac
    local ext=${host%.sslip.io} p; ext=${ext//-/.}
    for p in "$REPLICA_PORT" 2019 6175; do
      if curl -sS -m 5 -o /dev/null "http://$ext:$p/" 2>/dev/null; then bad "port $p reachable from outside"; else pass "port $p closed from outside"; fi
    done
    [ "$(stat -c %a "$PASSWORD_FILE")" = 600 ] && pass "driver password file mode 600" || bad "driver password file mode"
    if gssh "test -f $ETC_DIR/galaxy.enabled"; then galaxy_web_checks "galaxy.$host"; fi
    [ $fail = 0 ] || rc=1
    return 0
  fi
  got=$(curl -sS -m 20 -o /dev/null -w '%{http_code} %{ssl_verify_result}' "https://$host/" || true)
  [ "$got" = "401 0" ] && pass "https without credentials: 401 (certificate verified)" || bad "https no creds: $got"
  curl -sS -m 20 -D - -o /dev/null "https://$host/" 2>/dev/null | grep -i '^www-authenticate: basic' >/dev/null \
    && pass "401 carries WWW-Authenticate: Basic" || bad "no WWW-Authenticate header"
  got=$(printf 'user = "%s:%s"\n' "$OWNER_LOGIN" "not-the-password" | curl -sS -m 20 -K - -o /dev/null -w '%{http_code}' "https://$host/" || true)
  [ "$got" = 401 ] && pass "https with a wrong password: 401" || bad "wrong password: $got"
  if [ -s "$PASSWORD_FILE" ]; then
    got=$(printf 'user = "%s:%s"\n' "$OWNER_LOGIN" "$(head -1 "$PASSWORD_FILE")" | curl -sS -m 20 -K - -o /dev/null -w '%{http_code}' "https://$host/" || true)
    case "$got" in 200|502) pass "https with the password: $got (502 = replica web server not running yet)" ;; *) bad "with password: $got" ;; esac
    if [ "$got" = 200 ]; then
      got=$(printf 'user = "%s:%s"\n' "$OWNER_LOGIN" "$(head -1 "$PASSWORD_FILE")" | curl -sS -m 20 -K - -o /dev/null -w '%{http_code}' "https://$host/viewer/visualizer.html" || true)
      [ "$got" = 200 ] && pass "replay viewer page: 200" || bad "replay viewer page: $got (503 = viewer not installed: tools/replica/viewer.py)"
    fi
  else bad "no $PASSWORD_FILE on the driver"; fi
  got=$(curl -sS -m 20 -X POST -d x=1 -o /dev/null -w '%{http_code}' "https://$host/api/probe" || true)
  [ "$got" = 401 ] && pass "POST without credentials: 401" || bad "POST no creds: $got"
  local p m nbad=0
  for p in /viewer/visualizer.html /viewer/out/app.js /replica/status "/api/team/bc23/t/?ordering=-rating" //replica/status; do
    for m in GET HEAD OPTIONS; do
      got=$(curl -sS -m 20 -X "$m" -o /dev/null -w '%{http_code}' "https://$host$p" 2>/dev/null || true)
      [ "$got" = 401 ] || { bad "$m $p without credentials: $got"; nbad=1; }
    done
  done
  [ $nbad = 1 ] || pass "GET/HEAD/OPTIONS of viewer, replay API and JSON API paths without credentials: 401"
  # a Host header naming another site (e.g. the backend) must not reach the backend: Caddy answers empty
  got=$(curl -sS -m 20 -H 'Host: 127.0.0.1:8023' -o /dev/null -w '%{http_code} %{size_download}' "https://$host/replica/status" || true)
  case "$got" in 401*|*" 0") pass "foreign Host header is not proxied ($got)" ;; *) bad "foreign Host header: $got" ;; esac
  if [ "$PUBLIC_READ_ONLY" = 1 ] && [ -s "$PASSWORD_FILE" ]; then
    got=$(printf 'user = "%s:%s"\n' "$OWNER_LOGIN" "$(head -1 "$PASSWORD_FILE")" | curl -sS -m 20 -K - -X POST -d x=1 -o /dev/null -w '%{http_code}' "https://$host/api/probe" || true)
    [ "$got" = 405 ] && pass "POST with the password: 405 (read-only public front)" || bad "POST with password: $got"
  fi
  got=$(echo | openssl s_client -connect "$host:443" -servername "$host" 2>/dev/null | openssl x509 -noout -issuer -enddate 2>/dev/null | tr '\n' ' ')
  case "$got" in *"Let's Encrypt"*) pass "certificate: $got" ;; *) echo "INFO certificate: ${got:-none}" ;; esac
  local ext=${host%.sslip.io}; ext=${ext//-/.}
  for p in "$REPLICA_PORT" 2019 6175; do
    if curl -sS -m 5 -o /dev/null "http://$ext:$p/" 2>/dev/null; then bad "port $p reachable from outside"; else pass "port $p closed from outside"; fi
  done
  [ "$(stat -c %a "$PASSWORD_FILE")" = 600 ] && pass "driver password file mode 600" || bad "driver password file mode"
  if gssh "test -f $ETC_DIR/galaxy.enabled"; then galaxy_web_checks "galaxy.$host"; fi
  [ $fail = 0 ] || rc=1
}

galaxy_web_checks () {  # $1 galaxy host. Uses pass/bad/fail of web_checks.
  local g="$1" got cred hdr
  echo "url: https://$g/"
  cred () { printf 'user = "%s:%s"\n' "$OWNER_LOGIN" "$(head -1 "$PASSWORD_FILE")"; }
  code () { curl -sS -m 30 -o /dev/null -w '%{http_code}' "$@" 2>/dev/null || true; }
  got=$(curl -sS -m 30 -o /dev/null -w '%{http_code} %{ssl_verify_result}' "https://$g/" || true)
  [ "$got" = "401 0" ] && pass "galaxy: https without credentials: 401 (certificate verified)" || bad "galaxy no creds: $got"
  local p nbad=0
  for p in / /api/episode/e/bc23/ /admin/ /static/admin/css/base.css /storage/bc23-replica-secure/ /viewer/visualizer.html /api/token/; do
    got=$(code "https://$g$p"); [ "$got" = 401 ] || { bad "galaxy: GET $p without credentials: $got"; nbad=1; }
  done
  [ $nbad = 1 ] || pass "galaxy: frontend, API, admin, static, storage, viewer, token endpoint without credentials: 401"
  got=$(cred | code -K - "https://$g/"); [ "$got" = 200 ] && pass "galaxy: frontend with the password: 200" || bad "galaxy frontend: $got"
  got=$(cred | code -K - "https://$g/scrimmaging/some/deep/link"); [ "$got" = 200 ] && pass "galaxy: SPA fallback for a deep link: 200" || bad "galaxy deep link: $got"
  got=$(cred | curl -sS -m 30 -K - "https://$g/api/episode/e/bc23/" 2>/dev/null | python3 -c 'import json, sys; d = json.load(sys.stdin); print(d["name_short"], d["release_version_public"])' 2>/dev/null || true)
  [ "$got" = "bc23 3.0.15" ] && pass "galaxy: GET /api/episode/e/bc23/ with the password: episode bc23 3.0.15" || bad "galaxy episode API: $got"
  for p in /static/admin/css/base.css /viewer/visualizer.html /viewer/out/app.js /viewer/galaxy-viewer.js /favicon.png; do
    got=$(cred | code -K - "https://$g$p"); [ "$got" = 200 ] || { bad "galaxy: GET $p with the password: $got"; nbad=1; }
  done
  [ $nbad = 1 ] || pass "galaxy: static, viewer page, viewer bundle, frontend asset with the password: 200"
  got=$(cred | code -K - "https://$g/replay/00000000-0000-0000-0000-000000000000.bc23"); [ "$got" = 404 ] && pass "galaxy: /replay/* is not the SPA: 404" || bad "galaxy /replay: $got"
  got=$(code "https://$g/manifest.json"); [ "$got" = 200 ] && pass "galaxy: /manifest.json without credentials: 200 (browsers fetch it credential-less)" || bad "galaxy manifest: $got"
  hdr=$(cred | curl -sS -m 30 -K - -D - -o /dev/null "https://$g/api/user/u/me/" 2>/dev/null | tr -d '\r')
  case "$hdr" in *" 403"*) echo "$hdr" | grep -qi '^www-authenticate' && bad "galaxy: logged-out /api/user/u/me/ still carries a challenge" \
      || pass "galaxy: logged-out API call with the site login: 403 without a challenge (keeps the browser's login)" ;;
    *) bad "galaxy: logged-out /api/user/u/me/ with the site login: $(echo "$hdr" | head -1)" ;; esac
  hdr=$(cred | curl -sS -m 30 -K - -D - -o /dev/null "https://$g/" 2>/dev/null | tr -d '\r')
  echo "$hdr" | grep -i '^content-security-policy:' | grep -q "connect-src 'self'" && pass "galaxy: CSP header with connect-src 'self'" || bad "galaxy: no CSP connect-src 'self'"
  echo "$hdr" | grep -qi '^referrer-policy: same-origin' && pass "galaxy: Referrer-Policy same-origin (Django CSRF origin check)" || bad "galaxy: Referrer-Policy"
  # Bearer requests skip basic auth and must be judged by siarnaq: a bad token is a 401 everywhere, AllowAny too
  local jwt='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjo0MTAyNDQ0ODAwLCJ1c2VyX2lkIjoxfQ.c2lnbmF0dXJlLW5vdC12YWxpZA'
  hdr=$(curl -sS -m 30 -D - -o /dev/null -H "Authorization: Bearer $jwt" "https://$g/api/episode/e/bc23/" 2>/dev/null | tr -d '\r')
  case "$hdr" in *" 401"*"www-authenticate: Bearer"*|*" 401"*"WWW-Authenticate: Bearer"*) pass "galaxy: forged JWT on an AllowAny endpoint: 401 from siarnaq (Bearer challenge)" ;;
    *) bad "galaxy: forged JWT on GET /api/episode/e/bc23/: $(echo "$hdr" | head -1)" ;; esac
  got=$(code -X POST -H "Authorization: Bearer $jwt" -H 'Content-Type: application/json' -d '{}' "https://$g/api/user/u/")
  [ "$got" = 401 ] && pass "galaxy: forged JWT on registration (AllowAny POST): 401" || bad "galaxy: forged JWT register: $got"
  got=$(code -X POST -A Galaxy-Saturn -H "Authorization: Bearer $jwt" -H 'Content-Type: application/json' \
        -d '{"invocation": {"status": "OK!"}, "scores": [1, 0]}' "https://$g/api/compete/bc23/match/1/report/")
  [ "$got" = 401 ] && pass "galaxy: forged saturn report (User-Agent Galaxy-Saturn, bad ID token): 401" || bad "galaxy: forged report: $got"
  got=$(code -X POST -A Google-Cloud-Tasks -H "Authorization: Bearer $jwt" "https://$g/api/compete/bc23/match/1/rating_update/")
  [ "$got" = 401 ] && pass "galaxy: forged Cloud Tasks call: 401" || bad "galaxy: forged task: $got"
  for p in /api/token/ /admin/ / /storage/bc23-replica-secure/ /viewer/visualizer.html; do
    got=$(code -H "Authorization: Bearer $jwt" "https://$g$p")
    [ "$got" = 401 ] || { bad "galaxy: Bearer on $p (not a JWT-authenticated path): $got"; nbad=1; }
  done
  [ $nbad = 1 ] || pass "galaxy: a Bearer header does not open the token endpoint, admin, frontend, storage or viewer (401)"
  got=$(curl -sS -m 20 -H 'Host: 127.0.0.1:8024' -o /dev/null -w '%{http_code} %{size_download}' "https://$g/api/episode/e/bc23/" || true)
  case "$got" in 401*|*" 0") pass "galaxy: foreign Host header is not proxied ($got)" ;; *) bad "galaxy: foreign Host header: $got" ;; esac
  got=$(echo | openssl s_client -connect "$g:443" -servername "$g" 2>/dev/null | openssl x509 -noout -issuer 2>/dev/null)
  case "$got" in *"Let's Encrypt"*) pass "galaxy: certificate $got" ;; *) echo "INFO galaxy certificate: ${got:-none}" ;; esac
  local ext=${g#galaxy.}; ext=${ext%.sslip.io}; ext=${ext//-/.}
  if curl -sS -m 5 -o /dev/null "http://$ext:8024/" 2>/dev/null; then bad "port 8024 reachable from outside"; else pass "port 8024 closed from outside"; fi
}

fw_checks () {  # every enabled INGRESS rule that applies to the VM and admits a non-private source
  echo "--- GCP firewall ($BC_PROJECT)"
  python3 - "$BC_PROJECT" "$BC_VM" "$BC_ZONE" "$FW_RULE" <<'PY' || rc=1
import ipaddress, json, subprocess, sys
proj, vm, zone, own = sys.argv[1:5]
def g(*a):
    return json.loads(subprocess.run(['gcloud', *a, '--project', proj, '--format=json'], capture_output=True,
                                     text=True, check=True).stdout or 'null')
inst = g('compute', 'instances', 'describe', vm, '--zone', zone)
tags = set((inst.get('tags') or {}).get('items') or [])
sas = {s['email'] for s in inst.get('serviceAccounts') or []}
nets = {ni['network'].rsplit('/', 1)[-1] for ni in inst['networkInterfaces']}
print('INFO service accounts on %s: %s' % (vm, ', '.join(sorted(sas)) or 'none (no metadata token exists)'))
# what may be open to the internet: our rule (80, 443); the project's pre-existing defaults (22 ssh, 3389 rdp, icmp)
expected = {('tcp', '80'): 'own', ('tcp', '443'): 'own', ('tcp', '22'): 'default', ('tcp', '3389'): 'default',
            ('icmp', '*'): 'default'}
PRIVATE = [ipaddress.ip_network(n) for n in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', 'fc00::/7')]
def internal(s):
    n = ipaddress.ip_network(s, strict=False)
    return any(n.version == p.version and n.subnet_of(p) for p in PRIVATE)
fail = 0
for r in g('compute', 'firewall-rules', 'list') or []:
    if r.get('disabled') or r.get('direction') != 'INGRESS' or r['network'].rsplit('/', 1)[-1] not in nets:
        continue
    if r.get('targetTags') and not tags & set(r['targetTags']):
        continue
    if r.get('targetServiceAccounts') and not sas & set(r['targetServiceAccounts']):
        continue
    public = [s for s in r.get('sourceRanges') or [] if not internal(s)]
    if not public:
        continue
    for a in r.get('allowed') or []:
        proto, ports = a.get('IPProtocol'), a.get('ports') or ['*']
        for p in ports:
            kind = expected.get((proto, p))
            what = '%s %s:%s from %s' % (r['name'], proto, p, ','.join(public))
            if kind == 'own' and r['name'] == own:
                print('PASS internet-open: %s (Caddy)' % what)
            elif kind == 'default':
                print('INFO internet-open (pre-existing project default, not the replica): %s' % what)
            else:
                print('FAIL unexpected internet-open: %s' % what); fail = 1
sys.exit(fail)
PY
}

case "$what" in
  all) vm_checks; web_checks; fw_checks ;;
  vm) vm_checks ;;
  web) web_checks; fw_checks ;;
  fw) fw_checks ;;
  *) sed -n '2,6p' "$0" >&2; exit 2 ;;
esac
[ $rc = 0 ] && echo "verify: PASS" || { echo "verify: FAIL"; exit 1; }
