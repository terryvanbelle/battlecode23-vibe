# Replica host: lockdown and web access (battlecode-dev)

How the private galaxy replica ("galaxy-lite", `research/prior/GALAXY.md` 6.4) is fenced off on battlecode-dev, and
how the owner reaches it from a browser. Scripts: `tools/replica/deploy/`. Set up 2026-10-07.

**Web access:** `https://<external-ip-with-dashes>.sslip.io/`. On 2026-10-07 that was
`https://136-86-167-127.sslip.io/`. Log in as `owner`. The password is in `/home/terryvanbelle/.bc23-replica-password`
(mode 600) on the driver and on the VM. It is never printed, committed or put on a command line.
The address changes whenever the VM is stopped and started (section 6). Until the replica's web server listens on
`127.0.0.1:8023`, a logged-in request gets `502 Bad Gateway`.

**Second site (2026-10-08):** the galaxy replica (siarnaq + galaxy's frontend) is served by the same Caddy at
`https://galaxy.<external-ip-with-dashes>.sslip.io/`, with the same `owner` login, from `127.0.0.1:8024` and static
files under `/srv/bc23-galaxy`. Its routing, access rules and services are in `docs/galaxy/README.md`; this document
covers the host guards both sites share. The galaxy site is rendered into the same Caddyfile while
`/etc/bc23-replica/galaxy.enabled` exists.

**galaxy-lite retired (2026-10-08):** `sudo /usr/local/lib/bc23-replica/vm-setup.sh retire-lite` stopped and disabled
the galaxy-lite units, archived their data under `/home/bcreplica/replica/archive/<stamp>-retired/` and created
`/etc/bc23-replica/galaxy-lite.retired`. While that flag exists, the first site block is a 302 redirect from
`https://<ip-with-dashes>.sslip.io/<path>` to `https://galaxy.<ip-with-dashes>.sslip.io/<path>` (no password asked,
nothing proxied), nothing listens on 8023, and `vm-setup.sh services` leaves the units stopped. `verify.sh` checks
that state instead of the old site's access rules. The diagram below and the old site's checks in section 5 describe
galaxy-lite as it ran; the host guards (user, egress, Caddy, host name, firewall) are unchanged and serve the galaxy
site (`docs/galaxy/README.md`, `docs/replica/README.md`).

```
browser --https:443, basic auth--> Caddy (user caddy) --http, 127.0.0.1:8023--> replica web server (user bcreplica)
          (http:80 = ACME challenge + 308 redirect)       GET/HEAD only;            DB + replays in /home/bcreplica/replica
                                                          Authorization stripped    egress: loopback only
```

## 1. What was installed

| Item | Where | Notes |
|---|---|---|
| User `bcreplica` (uid 999), group `bcreplica` (gid 994) | `/etc/passwd`, home `/home/bcreplica` (0750) | System user, password locked, shell `nologin`, no supplementary groups, no sudo, no gcloud config, no keys or tokens. |
| `REPLICA_HOME` | `/home/bcreplica/replica` (2750, setgid) | Data root for the replica (DB, submissions, replays, logs). |
| `terryvanbelle` added to group `bcreplica` | | Read access to the DB and replays (new login sessions only). |
| Debian package `nftables` 1.0.6 | apt (Debian mirror) | `nftables.service` stays **disabled**. Nothing else in the ruleset is touched. |
| Egress table `inet bc23_replica_egress` | `/etc/bc23-replica/egress.nft` | Rules in section 3. |
| Unit `bc23-replica-egress.service` | `/etc/systemd/system/` | oneshot, `WantedBy=sysinit.target`, ordered before `network-pre.target`: loaded at every boot before networking. |
| Slice `bc23-replica.slice` | `/etc/systemd/system/` | `IPAddressDeny=any`, `IPAddressAllow=localhost`: a second, independent egress fence for replica services (section 4). |
| Drop-in `nftables.service.d/bc23-replica-egress.conf` + `/etc/bc23-replica/nftables-with-egress.nft` | `/etc/systemd/system/` | `/etc/nftables.conf` starts with `flush ruleset`. If anyone starts or reloads the (disabled) `nftables.service`, it now loads that file and the egress table in one atomic nft transaction instead of deleting the table. |
| D-Bus policy `bc23-replica.conf` | `/etc/dbus-1/system.d/` | `bcreplica` may not send to `systemd-resolved` (`org.freedesktop.resolve1`), `networkd` or `timesyncd`: no DNS lookups on its behalf (section 3). |
| Caddy v2.11.7, static binary | `/usr/local/bin/caddy` (root, 0755) | See the provenance table below. |
| User and group `caddy` (system) | home `/var/lib/caddy` (0700) | Holds the ACME account and the certificates. |
| `Caddyfile` | `/etc/caddy/Caddyfile` (0640 root:caddy) | Rendered from `/etc/bc23-replica/hostname` and `/etc/bc23-replica/owner.bcrypt` (0600 root). Never edit it by hand. |
| Unit `bc23-replica-caddy.service` | `/etc/systemd/system/` | Runs as `caddy`. Only capability: `CAP_NET_BIND_SERVICE`. `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`, `NoNewPrivileges`. |
| Unit `bc23-replica-hostname.service` | `/etc/systemd/system/` | At every boot, before Caddy starts, sets the site name from the current external IP (section 6). |
| Root-owned script copies | `/usr/local/lib/bc23-replica/{config,vm-setup,refresh-hostname}.sh` | The systemd units run these copies, never the user-writable repo checkout. |
| Access log | `/var/log/caddy/access.log` (rolls at 10 MiB, keeps 5) | `Authorization` is logged as `REDACTED`. |
| GCP firewall rule `bc23-replica-web` | project `tvanbelle-vibecode`, network `default` | INGRESS allow `tcp:80,tcp:443` from `0.0.0.0/0` to target tag `bc23-replica-web`. |
| Network tag `bc23-replica-web` | instance `battlecode-dev` (us-west1-b) | Only this VM carries the tag. |
| Password files | `/home/terryvanbelle/.bc23-replica-password` on the driver and the VM | 20 random letters and digits (Python `secrets`), mode 600. |

Caddy provenance. These are the official release assets from github.com/caddyserver/caddy. They were downloaded on
the VM by `vm-setup.sh caddy`, which checks the published checksums file and both pins in `config.sh` before
installing anything:

| | |
|---|---|
| Tarball URL | `https://github.com/caddyserver/caddy/releases/download/v2.11.7/caddy_2.11.7_linux_amd64.tar.gz` |
| Checksums file | `https://github.com/caddyserver/caddy/releases/download/v2.11.7/caddy_2.11.7_checksums.txt`. It lists **SHA-512** (the release publishes no SHA-256 list). |
| Tarball SHA-512 | `a7a433a1b133efc3c8d10eb0b99d52a24b5ef5c322dc77f5282182b1c0402139ab83f3a99f0c52409df77d20123fb0b523edad8a66d8f5e49136197bf61ef0e7` (matches the checksums file) |
| Tarball SHA-256 | `727b91701a392de6ebc5027509f548bf39979e5216340d0faed8fa5e69c84f8b` (pinned when first downloaded) |
| Installed binary SHA-256 | `678ade3bfc088749c81a681adc603333ee0bb023b6a6cfe3c0f58bef8ff854e9` (`caddy version`: `v2.11.7 h1:yj0Y4fYZGPkSvibBJ1sTWE33xC0fxztVyXEW5iIdUT4=`) |

The cosign signatures (`.sig`/`.pem`) were not checked because cosign is not installed.

Caddy's own network use: it talks to Let's Encrypt (`acme-v02.api.letsencrypt.org`) to get and renew the
certificate. The ACME account has no e-mail address. Caddy has no telemetry. None of this is Battlecode or MIT
infrastructure.

## 2. Every port opened

| Layer | Port | From | To | Why |
|---|---|---|---|---|
| GCP firewall `bc23-replica-web` | tcp/443 | 0.0.0.0/0 | instances tagged `bc23-replica-web` (battlecode-dev only) | HTTPS + basic auth |
| GCP firewall `bc23-replica-web` | tcp/80 | 0.0.0.0/0 | same | Let's Encrypt HTTP-01 challenge; every other request gets a 308 redirect to https |
| VM listener (Caddy) | tcp `*:80`, `*:443` | | | HTTP/3 (udp/443) is turned off (`protocols h1 h2`) because udp/443 is not opened |
| VM listener (Caddy admin API) | none | | | A unix socket, `/run/caddy/admin.sock`, in a 0750 `caddy:caddy` directory. Other users, `bcreplica` included, cannot reconfigure Caddy. The default `localhost:2019` is not used. |
| VM listener (replica web server) | tcp `127.0.0.1:8023` | loopback only | | Must not bind `0.0.0.0` |
| VM listener (galaxy replica: siarnaq under gunicorn) | tcp `127.0.0.1:8024` | loopback only | | `docs/galaxy/README.md`; PostgreSQL for it has no TCP listener (unix socket only) |

Nothing else was opened. The rules that already existed are unchanged: `default-allow-ssh` (22),
`default-allow-rdp` (3389, nothing listens there), `default-allow-icmp` and `default-allow-internal`
(10.128.0.0/9). These are project-wide defaults and also cover the other VMs, including `battlecode-dev2`, which is
off-limits. So **sshd on tcp/22 is reachable from the whole internet**. It accepts public keys only
(`passwordauthentication no`, `permitrootlogin no`). The driver reaches the VM on its internal IP, so narrowing
`default-allow-ssh` would not affect the agents, but it is the owner's call. `systemd-resolved` also answers LLMNR on
`0.0.0.0:5355`; only the VPC can reach it (`default-allow-internal`), and it was checked as closed from outside. Because of `default-allow-internal`, anything that binds `0.0.0.0` on the VM can be reached from the
driver. The engine's websocket port 6175 is one example, which is why the runner must pass
`-Dbc.server.websocket=false`. Ports 8023, 8024, 2019 and 6175 are checked as closed from outside.

The public front is **read-only**: Caddy passes only `GET` and `HEAD` and answers any other method with 405, after
basic auth. Viewing rankings and replays needs nothing more. Submissions, requests and autoscrims are made on the VM,
for example with the replica CLI over ssh. A browser that holds the basic-auth credentials therefore cannot be
tricked by a cross-site form into queueing work. To allow writes from the web, set `PUBLIC_READ_ONLY=0` in
`tools/replica/deploy/config.sh` and redeploy. Do this only together with CSRF protection in the replica web server.

## 3. The egress lockdown

`/etc/bc23-replica/egress.nft`, generated with the numeric uid:

```
table inet bc23_replica_egress {
  chain output { type filter hook output priority filter - 10; policy accept;
                 meta skuid 999 jump replica }                      # only bcreplica's sockets
  chain replica {
    ip daddr 169.254.169.254 drop     # GCE metadata server: no service-account token, no metadata DNS
    ip6 daddr fd20:ce::254 drop       # its IPv6 address
    oifname != "lo" log (6/min) ; oifname != "lo" drop             # nothing leaves the host
    ct state established,related accept                            # replies on loopback (web server -> Caddy)
    tcp dport { 8023, 8024 } accept                                 # new loopback connections: the replicas' ports only
    drop                                                            # DNS stub 127.0.0.53, MTA :25, anything else local
  }
}
```

- The file touches only its own table (no `flush ruleset`). Loading it is one atomic transaction, so
  `systemctl reload bc23-replica-egress` has no unprotected moment.
- The VM's `/etc/resolv.conf` points at 169.254.169.254, so name resolution fails for `bcreplica` as well
  (`Could not resolve host`). That is intended: the replica needs no names.
- Users other than `bcreplica` are untouched. `terryvanbelle` and root still reach the internet and the metadata
  server (verified).
- To let `bcreplica` open more loopback ports, edit `REPLICA_LO_PORTS` in `config.sh` and redeploy. Since
  2026-10-08 it is `8023 8024`: the galaxy replica's relay reaches siarnaq on 127.0.0.1:8024.
- Dropped packets are logged at 6 per minute: `sudo journalctl -k -g bc23-replica-egress-drop`.

- **The table survives `nftables.service`.** Its `ExecStart`/`ExecReload` run `flush ruleset` from
  `/etc/nftables.conf`. A drop-in makes both load `/etc/bc23-replica/nftables-with-egress.nft`, which includes
  `/etc/nftables.conf` and then `egress.nft`, in one transaction. `systemctl stop nftables` still flushes
  everything; `PartOf=nftables.service` then stops the egress unit and, through `Requires=`, the replica services
  (fail closed). The API unit also refuses to start when the table is missing, and so does the CLI wrapper.

**Unix sockets.** nftables filters IP sockets, not unix sockets, and only for processes running as `bcreplica`.
`systemd-resolved` answers name lookups over D-Bus and over a varlink socket (`/run/systemd/resolve/io.systemd.Resolve`,
mode 0666), and then sends the DNS query itself, as its own user. Security review on 2026-10-07: `bcreplica` could
resolve any name both ways (`resolvectl query example.com` returned addresses). Closed as follows:

| Path | Replica services and the engines they start | CLI wrapper / `sudo -u bcreplica` |
|---|---|---|
| D-Bus to resolved, networkd, timesyncd | closed: D-Bus policy, plus `InaccessiblePaths=` on the bus socket | closed: D-Bus policy (`Access denied`) |
| varlink `io.systemd.Resolve` | closed: `InaccessiblePaths=-/run/systemd/resolve` | **open** (see below) |
| abstract unix sockets (only exim's `@/var/spool/exim4/exim_daemon_notify` exists) | worker and autoscrim: closed (`PrivateNetwork=yes`, an own namespace); API: open, harmless | open, harmless |
| setuid helpers (the MTA, `exim4`, local delivery only) | closed: `NoNewPrivileges=yes` | open |

What stays open applies only to commands an operator runs by hand as `bcreplica`, and only to deliberate misuse.
`/etc/nsswitch.conf` is `hosts: files myhostname dns` (no `resolve`), so neither glibc's resolver, Python nor the JVM
uses the varlink socket by accident. If `libnss-resolve` is ever installed, `getaddrinfo` would go through varlink and
lookups run by hand as `bcreplica` would reach DNS through resolved. The services would still be blocked. Work handed
to a process running as another user is also outside this fence.

## 4. Contract for the replica's services (for whoever writes the systemd units)

Implemented by `vm-setup.sh services`, which `deploy.sh` runs as part of `all`. It installs
`bc23-replica-api.service` and `bc23-replica-worker.service` (enabled and running),
`bc23-replica-autoscrim.service` with `bc23-replica-autoscrim.timer` (installed **disabled**), the environment
file `/etc/bc23-replica/replica.env` and the CLI wrapper `/usr/local/bin/bc23-replica`. The units add filesystem
hardening on top of this contract (`ProtectSystem=strict`, `ProtectHome=read-only`, `ReadWritePaths=$REPLICA_HOME`).
`verify.sh` checks that both services are active, run as `bcreplica` in the slice and bind 127.0.0.1:8023 only.
How to operate them is in `docs/replica/README.md` ("Services").

Added by the security review (2026-10-07), on top of the contract below:
- `InaccessiblePaths=-/run/systemd/resolve -/run/dbus/system_bus_socket` in every replica unit (section 3).
- `PrivateNetwork=yes` for the worker and the autoscrim unit. The worker, and every engine it starts, runs in its
  own network namespace that holds only `lo`. Nothing there can reach the host, the VPC or the internet. A listener
  such as the engine's websocket would not be reachable even without `-Dbc.server.websocket=false`, and parallel
  games cannot collide on a port. The API cannot use this, because Caddy has to reach it on the host's loopback.
- `ExecStartPre=+… nft list table inet bc23_replica_egress` on the API unit only. A `+` command still runs inside
  the unit's private network namespace, where the host's table is not visible, so it cannot be used on the worker.
  The worker does not depend on the table.

```
[Unit]
Requires=bc23-replica-egress.service
After=bc23-replica-egress.service

[Service]
User=bcreplica
Group=bcreplica
Slice=bc23-replica.slice        # cgroup IP filter: localhost only, even if the nftables table were gone
UMask=0027                      # group bcreplica (terryvanbelle) can read the DB and replays
Environment=REPLICA_HOME=/home/bcreplica/replica
# web server: bind 127.0.0.1:8023 only; it gets the original Host header and X-Forwarded-For from Caddy,
# no Authorization header, and only GET/HEAD from the internet
```

Code, the JDK (`/home/terryvanbelle/jdk`), the engine jar and the benchmark class dirs are world-readable under
`/home/terryvanbelle` (0755). `bcreplica` can read them where they are. `~/.ssh` and `~/.config` are 0700 and
stay unreadable. To read the SQLite DB as `terryvanbelle` while the replica writes it, use the API or open it
read-only (`sqlite3 'file:/home/bcreplica/replica/replica.db?mode=ro'`). A WAL database needs its `-shm` file to
be group-readable (UMask above).

Ad hoc commands as the replica user: `sudo -u bcreplica <cmd>` (the nftables fence applies).

## 5. Deploy, verify

All from the driver, in the repo root:

```
tools/replica/deploy/deploy.sh            # everything, idempotent (gcloud on the driver makes it take ~6 min)
tools/replica/deploy/deploy.sh --no-web   # lockdown only (user + egress), no Caddy, no open ports
tools/replica/deploy/verify.sh            # ~101 PASS/FAIL checks (galaxy-lite retired, galaxy replica); exit 1 on any FAIL
tools/replica/deploy/verify.sh vm|web|fw  # one part (web includes fw, the GCP firewall audit)
python3 test/replica/test_deploy.py       # offline checks of the scripts and rendered configs
```

What `verify.sh` checks:
- **On the VM:** the user's groups, shell, lock, sudo rights and credential files. The egress unit is enabled and
  active, and the table matches the uid. As `bcreplica`, all of these must fail: `https://example.com`,
  `http://1.1.1.1`, `http://169.254.169.254`, the metadata token URL, a DNS lookup, the loopback DNS stub, the MTA,
  and `127.0.0.1:2019`. A root process inside `bc23-replica.slice` must be blocked from the metadata server, with a
  control run outside the slice that must work. As `terryvanbelle` and as root, `example.com` and the metadata server
  must work. A temporary server as `bcreplica` on 127.0.0.1:8023 must be reachable. Caddy runs as `caddy` and
  listens on 80 and 443 only. File modes are checked, and the clear password must not appear in the Caddyfile.
  Side channels: `resolvectl query` as `bcreplica` must be denied (D-Bus policy). The `nftables.service` drop-in must
  be in place and its combined file must pass `nft -c`. Both services must have the resolved sockets inaccessible.
  The worker must run in a private network namespace that holds only `lo`, and `curl http://1.1.1.1` from inside it
  must fail. In the host namespace `bcreplica` may listen on loopback only, and nothing may listen on tcp/3389. A
  list of all non-loopback listeners is printed for information.
- **The galaxy replica** (when `/usr/local/lib/bc23-galaxy` is installed): its three units run as `bcreplica` in
  the slice with the resolved sockets inaccessible; saturn has a private network namespace holding only `lo` (no
  route out, not even to 127.0.0.1:8024) and cannot see the token key; 8024 is bound to 127.0.0.1 only; PostgreSQL has
  no TCP listener; the venv holds no Google library; siarnaq imports every `google.*` module from the stand-ins; no
  external host appears in the running settings (`bc23-galaxy-manage bootstrap audit`). From the driver, the galaxy
  site's routing and access rules (`docs/galaxy/README.md`, "Caddy"), including forged JWTs and forged saturn/Cloud
  Tasks tokens (401), and port 8024 closed from outside.
- **From the driver:** `http://` returns 308 to `https://`. `https://` without credentials returns 401 with a
  verified certificate and `WWW-Authenticate: Basic`. A wrong password returns 401, and the right one returns
  200 or 502. POST returns 401 without credentials and 405 with them. GET, HEAD and OPTIONS on the viewer, the
  replay API and the JSON API paths (and `//replica/status`) return 401 without credentials. A request whose
  `Host` header names the backend (`127.0.0.1:8023`) is not proxied: it gets an empty answer. The issuer is Let's
  Encrypt. Ports 8023, 2019 and 6175 are closed from outside. The driver's password file is mode 600.
- **GCP firewall (from the driver, `gcloud`):** every enabled INGRESS rule on the VM's network that applies to the
  VM (by tag or to all instances) and admits a non-RFC1918 source is listed. `bc23-replica-web` tcp:80/443 → PASS.
  The project's pre-existing defaults (tcp:22, tcp:3389, icmp) → INFO. Anything else → FAIL. The VM's service
  accounts are printed: on 2026-10-07 there were none, so the metadata server issues no token to anyone on the VM.
- Egress tests never target Battlecode or MIT hosts: if the fence were broken, the test itself would reach them.

Manual spot checks on the VM:

```
sudo -u bcreplica curl -m 10 https://example.com                  # fails: Could not resolve host
sudo -u bcreplica curl -m 5 http://169.254.169.254/               # fails: timeout
curl -s -H Metadata-Flavor:Google http://169.254.169.254/computeMetadata/v1/instance/id   # works
sudo nft list table inet bc23_replica_egress                       # counters show what was dropped
sudo /usr/local/lib/bc23-replica/vm-setup.sh status
```

Manual checks from anywhere:

```
curl -sI http://136-86-167-127.sslip.io/                                    # 308 -> https
curl -s -o /dev/null -w '%{http_code}\n' https://136-86-167-127.sslip.io/   # 401
```

## 6. After a VM restart: the host name

The external IP is **ephemeral**: stopping and starting battlecode-dev gives it a new one, and with it a new name
`<new-ip-with-dashes>.sslip.io`. **`refresh-hostname.sh` must run after every VM restart.** The boot unit
`bc23-replica-hostname.service` does this automatically: it reads the IP from the metadata server, rewrites the
Caddyfile, and Caddy then gets a certificate for the new name within about a minute. If the boot run failed
(`systemctl status bc23-replica-hostname`), or to learn the new URL, run it by hand:

```
tools/replica/deploy/refresh-hostname.sh                  # on the driver: IP from gcloud; prints the URL
sudo /usr/local/lib/bc23-replica/refresh-hostname.sh      # on the VM: IP from the metadata server
```

Old bookmarks stop working after a restart. **Owner decision, not taken:** reserve a static external IP so the URL
never changes. This promotes the current address in place:
`gcloud compute addresses create bc23-replica-ip --addresses=136.86.167.127 --region=us-west1 --project=tvanbelle-vibecode`.
A reserved address is billed while the VM is stopped too; check current GCP pricing. After that, the boot unit
finds the same IP and changes nothing.

Let's Encrypt allows 50 certificates per registered domain per week and 5 duplicates per exact name per week. That
is ample for occasional restarts. A restart with an unchanged IP reuses the stored certificate.

## 7. Rotate the password

```
tools/replica/deploy/set-password.sh --rotate   # new 20-char password: driver file, VM file, bcrypt hash, reload
tools/replica/deploy/set-password.sh            # re-push the driver's existing password (e.g. after a failed push)
```

The old password stops working when Caddy reloads, a second later. Browsers then ask again.

## 8. Tear down

```
tools/replica/deploy/teardown.sh web                     # close 80/443 (rule + tag) and remove Caddy, its certs,
                                                         # logs and user; the lockdown and bcreplica stay
tools/replica/deploy/teardown.sh all                     # also remove the lockdown, slice, scripts and user
                                                         # bcreplica (refuses while bcreplica runs anything);
                                                         # /home/bcreplica is kept
tools/replica/deploy/teardown.sh all --purge-data --purge-password   # also delete /home/bcreplica and both password files
```

The same steps by hand. On the driver:

```
gcloud compute instances remove-tags battlecode-dev --zone=us-west1-b --project=tvanbelle-vibecode --tags=bc23-replica-web
gcloud compute firewall-rules delete bc23-replica-web --project=tvanbelle-vibecode --quiet
rm -f ~/.bc23-replica-password
```

On the VM:

```
sudo systemctl disable --now bc23-replica-caddy bc23-replica-hostname
sudo rm -f /etc/systemd/system/bc23-replica-{caddy,hostname}.service
sudo rm -rf /etc/caddy /var/lib/caddy /var/log/caddy /usr/local/bin/caddy
sudo userdel caddy
# full teardown also:
sudo systemctl disable --now bc23-replica-egress          # removes the nft table
sudo rm -f /etc/systemd/system/bc23-replica-egress.service /etc/systemd/system/bc23-replica.slice
sudo rm -f /etc/systemd/system/nftables.service.d/bc23-replica-egress.conf /etc/dbus-1/system.d/bc23-replica.conf
sudo busctl call org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus ReloadConfig
sudo systemctl daemon-reload
sudo rm -rf /etc/bc23-replica /usr/local/lib/bc23-replica
sudo gpasswd -d terryvanbelle bcreplica
sudo userdel bcreplica              # add -r to delete /home/bcreplica too
sudo apt-get purge nftables         # optional
rm -f ~/.bc23-replica-password
```

## 9. Exposure and what is not verified

- **The name is public.** Every Let's Encrypt certificate goes into the Certificate Transparency logs, so scanners
  will find the URL and probe it. Everything behind it needs the password: 20 random characters, about 119 bits.
  Each wrong guess costs Caddy one bcrypt check (cost 14), about a second of one CPU core. A sustained flood could
  slow games on the VM. If that happens, run `teardown.sh web` or narrow the firewall rule's `--source-ranges`.
- Correct logins are cached by Caddy (`hash_cache`), so only the first request of a connection pays the bcrypt cost.
  A browser's first page load waits about 1-2 s. After that, requests on the same connection take milliseconds.
- **Not verified, because it needs a real reboot:** that the egress table, the boot host-name refresh and Caddy all
  come up correctly on boot. A reboot would have killed games other agents had running. What was verified: the
  units are enabled; `systemd-analyze verify` is clean; and starting `bc23-replica-hostname.service` by hand on the
  running VM rewrote the Caddyfile and reloaded Caddy without blocking. An early version deadlocked on a blocking
  reload; this is fixed. Check after the first restart with `tools/replica/deploy/verify.sh`.
- `teardown.sh` has not been run, since that would have destroyed the deployment. Its VM half is
  `vm-setup.sh teardown-web` / `teardown-all`.
- Security review, 2026-10-07. What was verified and what was not:
  - `nftables.service` was not actually started or stopped, because that would have restarted the replica services.
    The drop-in's combined file was loaded the way `nftables.service` loads it, inside a throwaway network namespace
    (`unshare -n`). That namespace already held another table. The load flushed that table and left `inet filter`
    and the egress table with the `skuid 999` rule.
  - The worker under `PrivateNetwork=yes` has not yet run a real queued match, because the queue was empty and adding
    a match would have changed the ladder data. An equivalent transient unit ran one engine game. It had the same
    user, slice, `PrivateNetwork`, `InaccessiblePaths` and filesystem protection, and used the worker's exact engine
    flags (examplefuncsplayer mirror on SmallElements, 24 s, winner line parsed).
  - A `bcreplica` listener on `0.0.0.0` outside the units could not even complete a TCP handshake from the driver:
    nftables matches the listener's uid on the SYN-ACK too.
  - Caddy's running configuration, read over its admin socket, equals `caddy adapt` of the Caddyfile on disk. The
    replica code (`tools/replica/*.py`) contains no external URL, only SVG namespace strings. The viewer bundle's only
    Battlecode URL is `play.battlecode.org/replays/`. It is built only from a tournament JSON that the user loads by
    hand, and `connect-src 'self'` would block the request anyway (VIEWER.md section 4).
- Not checked: the cosign signatures on the Caddy release (see section 1).
