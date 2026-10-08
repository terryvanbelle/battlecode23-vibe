# The galaxy replica: siarnaq, unmodified, on battlecode-dev

A private copy of the Battlecode contest website ("galaxy", github.com/battlecode/galaxy, MIT license) for the
2023 practice project. The API is siarnaq itself at the pinned commit `f343088`, with no source file changed. Every
Google Cloud service it calls is replaced by a local stand-in. Compiles and matches run in a saturn replacement that
uses our pinned engine. The frontend is galaxy's own React app, built for this origin (`tools/galaxy/frontend`,
docs by the frontend agent). Contestant actions work as on play.battlecode.org: register, log in, create a team,
upload a zip, request and accept scrimmages, download sources and replays, watch replays.

**URL:** `https://galaxy.<external-ip-with-dashes>.sslip.io/`. On 2026-10-08 that was
`https://galaxy.136-86-167-127.sslip.io/`. The basic-auth login is user `owner`, with the password in
`~/.bc23-replica-password` on the driver and the VM. The siarnaq superuser `owner` has the same password, for
`/admin/` and for logging in to the frontend as staff. The host name follows the VM's external IP
(`docs/replica/DEPLOY.md` section 6). The first replica, galaxy-lite, was retired on 2026-10-08
(`docs/replica/README.md`): its host name `https://<ip-with-dashes>.sslip.io/` redirects here. Who plays here and
the operator tools (the field teams, their scrimmages, results into `progress/games.csv`, the ladder snapshot):
section 8.

Nothing here contacts battlecode.org or any Google API, at install time or at run time. Section 7 lists what was
checked.

## 1. What runs where

```
browser --https--> Caddy (user caddy, galaxy.<host>)
   | Authorization: Bearer <jwt> on /api/* ---------------------------------------------> siarnaq  127.0.0.1:8024
   | otherwise basic auth (owner), then:                                                  (gunicorn, bcreplica)
   |     /api/*, /admin/* -------------------------------------------------------------->   |  PostgreSQL 15 (unix socket)
   |     /static/*  /storage/*  /viewer/*  everything else (SPA) --> files in /srv/bc23-galaxy  |
   |                                                                                         | publish / create_task /
   |                                                                                         v create_job (stand-ins)
   |                                                       $GALAXY_HOME/spool/{pubsub,tasks,scheduler}/  (JSON files)
   |                                                              |                        |
   |              saturn.py (bcreplica, PrivateNetwork=yes: no network at all)   relay.py (bcreplica, loopback only)
   |              compile: javac + Verifier;  execute: engine 3.0.15              Cloud Tasks -> siarnaq (+ ID token)
   |              reads/writes /srv/bc23-galaxy/storage ---unix socket---> saturn reports -> siarnaq (+ ID token)
```

| Unit (systemd, all `User=bcreplica`, `Slice=bc23-replica.slice`) | What | State |
|---|---|---|
| `bc23-galaxy-web.service` | siarnaq: `python -m gunicorn siarnaq.wsgi:application --bind 127.0.0.1:8024 --workers 3` | enabled, running |
| `bc23-galaxy-relay.service` | `tools/galaxy/relay.py serve`: saturn's reports (unix socket) and Cloud Tasks to siarnaq | enabled, running |
| `bc23-galaxy-saturn.service` | `tools/galaxy/saturn.py run`: 1 compile slot + `GALAXY_EXECUTE_SLOTS` (5) engines; `PrivateNetwork=yes` | enabled, running |
| `bc23-galaxy-scheduler.service` + `.timer` | `relay.py fire-jobs` each minute: fires the recorded Cloud Scheduler jobs (the autoscrim job) whose cron matches | timer enabled 2026-10-08 01:19 UTC, once the field was in (section 8) |
| `postgresql@15-main` (Debian, user postgres) | database `siarnaq`, owned by role `bcreplica` (peer auth over the unix socket); `listen_addresses = ''` | enabled, running |
| `bc23-replica-caddy.service` (shared) | the galaxy site is a second site in the same Caddyfile | running |

Every galaxy unit has the galaxy-lite contract (`docs/replica/DEPLOY.md` section 4): it requires the egress
table, runs with `UMask=0027`, `ProtectSystem=strict`, `ProtectHome=read-only`, `NoNewPrivileges`, and has the
resolved and D-Bus sockets inaccessible. The web and relay units refuse to start without the nftables table. The
egress table lets `bcreplica` open new loopback connections to ports 8023 and 8024 only.

| Path | Owner | What |
|---|---|---|
| `/opt/bc23-galaxy/src/` | root, read-only | `git archive` of galaxy `f343088f4d471b0664b2ff41129f0435a8dca1c2` (all of it; siarnaq is `backend/`). `REPLICA_SOURCE` records the commit and the archive's sha256. |
| `/opt/bc23-galaxy/venv/` | root, read-only | Python 3.11 venv from `tools/galaxy/requirements.txt` (44 pins, each with its sha256, PyPI only) |
| `/home/bcreplica/galaxy/` | bcreplica 2750 | `secrets/` (0700: Django key, the migration admin's password, the ID-token HMAC key), `spool/`, `storage-meta/`, `saturn/` (work dirs), `run/relay.sock` (0600), `frontend-dist/` (the frontend build) |
| `/srv/bc23-galaxy/` | root:caddy 0751 | what Caddy serves: `frontend/` (copied from `frontend-dist`), `viewer/` (the 3.0.15 client + our page), `static/` (Django collectstatic, bcreplica), `storage/<bucket>/` (the buckets, bcreplica:caddy 2750) |
| `/etc/bc23-galaxy/galaxy.env` | root 0644 | environment of the units and the CLI (written once; edits kept). No secrets. |
| `/usr/local/lib/bc23-galaxy/` | root | installed copies of `tools/galaxy/deploy/{config,galaxy-setup}.sh` |
| `/usr/local/bin/bc23-galaxy-manage` | root | siarnaq's `manage.py` and the tools as `bcreplica` with the units' environment |

The Python code runs from the operator's checkout (`~/projects/vibe/2023/tools/galaxy`, read-only to the units), as
galaxy-lite's does. PYTHONPATH puts `tools/galaxy/standins` first, then `tools/galaxy`, then the galaxy backend.

## 2. The stand-ins (`tools/galaxy/standins/google/`, back end `tools/galaxy/replica_gcp/`)

The `google` package is shadowed as a whole: no Google client library is installed in the venv, and `verify.sh`
checks that. Each stand-in implements only what siarnaq calls. A name it does not define raises AttributeError or
ImportError, and an unimplemented method or option raises NotImplementedError. `replica_settings.py` refuses to start
siarnaq unless every `google.*` module it imports comes from the stand-ins. The stand-ins contain no network code; a
unit test checks for socket, http and urllib imports and for any URL.

| siarnaq imports | Calls it makes (galaxy f343088) | Replica behaviour |
|---|---|---|
| `google.cloud.storage` | `Client(credentials=)`, `Client()`, `create_anonymous_client()`, `bucket().blob()`, `get_blob()`, `blob.open("wb", content_type=, predefined_acl=)`, `upload_from_string`, `download_as_bytes`, `metadata` + `patch()`, `generate_signed_url(expiration=, method="GET", credentials=)`, `public_url` | A bucket is the directory `/srv/bc23-galaxy/storage/<bucket>/`; writes are atomic (a temp file, then a rename). Metadata (content type, ACL, custom metadata) lives in `$GALAXY_HOME/storage-meta/` and is never served. `public_url` and every signed URL are the same-origin path `/storage/<bucket>/<name>`, which Caddy serves behind basic auth. Names with `..`, empty, hidden or absolute components are refused. **Titan** (ClamAV malware scan): a patch to `Titan-Status: Unverified` is marked `Verified` at once. |
| `google.cloud.pubsub` | `PublisherClient(credentials=, publisher_options=PublisherOptions(enable_message_ordering=True), client_options={api_endpoint})`, `topic_path`, `publish(topic=, data=, ordering_key=).result()`, `resume_publish` | Each message is one JSON file in `$GALAXY_HOME/spool/pubsub/<topic>/ready/`, with its data (base64), ordering key and publish time. Ids sort by publish time. The endpoint is ignored. Errors come back through the future, and the ordering key pauses until `resume_publish`, as in the real client. |
| `google.cloud.tasks_v2` | `CloudTasksClient().queue_path()`, `create_task(request=dict(parent=, task=Task(http_request=HttpRequest(http_method=POST, url=, oidc_token=OidcToken(service_account_email=)))))` | The task goes to `$GALAXY_HOME/spool/tasks/<queue>/`. The relay delivers it (section 3). Used for `rating_update` (the rating queue) and bracket publishing. |
| `google.cloud.scheduler` (also `scheduler_v1`) | `CloudSchedulerClient(credentials=).create_job/update_job/delete_job(request=dict(...))` | The job is recorded in `$GALAXY_HOME/spool/scheduler/<job>.json`. The cron is validated. The scheduler timer fires it (section 4). |
| `google.cloud.secretmanager` | imported by `siarnaq/settings.py` (Staging/Production only) | Constructing a client raises. |
| `google.auth`, `.credentials`, `.impersonated_credentials`, `.compute_engine.credentials`, `.exceptions`, `.transport.requests` | imported by settings and titan; `impersonated_credentials.Credentials(...)` built before signing | Credentials can be built but never yield a token. `default()` raises DefaultCredentialsError, and the transport raises TransportError. |
| `google.oauth2.id_token` | `verify_oauth2_token(id_token=, request=)` in `GoogleCloudAuthentication` | Verifies the replica's own ID tokens: compact JWS, HS256 with a 256-bit key generated on the VM (`secrets/oidc-hmac.key`), issuer `bc23-replica-oidc`, expiry of at most 1 h, verified e-mail. Anything else raises ValueError, and siarnaq answers 401. |

Service identities are reserved `.invalid` addresses: `siarnaq-agent@bc23-replica.invalid` (Cloud Tasks and
Scheduler OIDC, `GCLOUD_SERVICE_EMAIL`), `saturn-compile@` and `saturn-execute@bc23-replica.invalid`
(`GALAXY_ADMIN_EMAILS`). siarnaq maps them to its staff user `galaxy-admin`.

**Settings** (`tools/galaxy/replica_settings.py`, class `Replica(Base)`, `DJANGO_CONFIGURATION=Replica`):
- `GCLOUD_ENABLE_ACTIONS=True`, with the replica's bucket, topic and queue names.
- `ALLOWED_HOSTS[0]`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` and `FRONTEND_ORIGIN` are the galaxy host, read
  from `/etc/bc23-replica/hostname` at start (a host change restarts the web unit).
- `DEBUG=False`. TLS is terminated by Caddy (`SECURE_PROXY_SSL_HEADER`), and DRF `NUM_PROXIES=1`.
- PostgreSQL over `/var/run/postgresql`.
- `EMAIL_ENABLED=False`, `EMAIL_VERIFICATION_ENABLED/REQUIRED=False`, and `EMAIL_BACKEND` drops every message and
  logs it (`replica_gcp/mail.py`). The sender is `no-reply@bc23-replica.invalid`, and `ANYMAIL` and
  `CHALLONGE_API_KEY` are empty.
- `SECRET_KEY` and `SUPERUSER_PASSWORD` (which migration `user/0002` uses for the superuser `admin`) are read from
  `$GALAXY_HOME/secrets/`. They are generated on the VM and never printed. The `admin` user's e-mail is set to
  `admin@bc23-replica.invalid`.

## 3. saturn and the relay

**saturn** (`tools/galaxy/saturn.py`) is saturn's subscriber, task protocol and Java recipes (`saturn/pkg/saturn`,
`pkg/run/java.go`), reimplemented around our pinned engine.
- **Messages.** A slot leases the oldest spooled message (an atomic rename) and parses saturn's `TaskPayload`. An
  invalid message is acknowledged and dropped. A finished task (OK!, or aborted on 409) is acknowledged. An errored
  or interrupted task is nacked: it is redelivered after `GALAXY_NACK_DELAY` (10 s), or at once when interrupted.
  Messages leased by a dead process return to the queue when the service starts.
- **Reports, exactly saturn's payload.** It first reports `{"invocation": {"status": "RUN", "logs": "",
  "interrupted": false}}`, and siarnaq's 409 aborts the task. It ends with the runner's details (`{"accepted":
  bool}` or `{"scores": [a, b]}`) plus `invocation` (`OK!` or `TRY`, the logs since the last report,
  `interrupted`). The logs follow saturn's step format (`>>> Starting step 3/6: Download source code` ...).
  siarnaq counts the failures and sets ERR at 5.
- **Compile.** The steps are: Hello world, Prepare scaffold, Download source code, Build source code, Upload binary,
  Compile succeeded.
  - The source zip is extracted with saturn's zip-slip check, plus a 256 MiB expansion limit.
  - It is compiled with `javac -source 8 -target 8 -proc:none` (`tools/lib.sh compile_src`), then checked by the
    engine's `battlecode.instrumenter.Verifier <package>` (galaxy-lite's worker does the same).
  - Every failure of the user's code (malformed zip, illegal path, empty package, a compile or Verifier error) is
    `OK!` with `accepted: false`, as in saturn.
  - The class tree is zipped to `episode/bc23/submission/<id>/binary.zip` in the secure bucket.
- **Execute.** The steps are: Hello world, Prepare scaffold, Download binary (A and B), Run match, Upload replay,
  Determine scores.
  - There is one engine run with all the maps and saturn's flags, through `tools/replica/worker.py`'s
    `match_command`: the pinned 3.0.15 jar with `engine/patch` first, `-Dbc.server.websocket=false`,
    `validate-maps=true`, indicators off, the given alternate order, and no seed.
  - Team names are siarnaq's.
  - The replay goes to `episode/bc23/replays/<uuid>.bc23` (public ACL).
  - Scores are counted with saturn's regex.
- **Concurrency.** `GALAXY_EXECUTE_SLOTS=5` engines (about 1 GB each; 3 until galaxy-lite was retired on
  2026-10-08) plus 1 compile slot. Edit `/etc/bc23-galaxy/galaxy.env` and restart `bc23-galaxy-saturn` to change
  it (a restart interrupts running matches; they are redelivered). The VM also runs the experiment queue
  (`tools/vm-queue.sh`, 5 game slots).
- **Isolation.** saturn, javac and the engines run in a private network namespace that holds only `lo`, so they
  cannot reach the host's loopback either. The token key directory is not visible to them. saturn's only channel
  out is the relay's unix socket.

**The relay** (`tools/galaxy/relay.py`) is the only process that calls siarnaq. Every call goes to
`127.0.0.1:8024`, whatever host the URL names, with `Host: galaxy.<host>`, and only for `/api/` paths.
- **saturn's reports.** It accepts only `POST /v1/report` for a submission or match report path that matches the
  task type. It adds `User-Agent: Galaxy-Saturn` and an ID token for `saturn-compile@`/`saturn-execute@` (audience
  `siarnaq`), then answers with siarnaq's status.
- **Cloud Tasks.** It adds `User-Agent: Google-Cloud-Tasks`, the `X-CloudTasks-*` headers and an ID token for the
  task's service account. There are 3 concurrent dispatches per queue, as galaxy's queues have. A non-2xx answer is
  retried with Cloud Tasks' default backoff (0.1 s, doubling, at most 1 h) up to 100 attempts, after which the task
  goes to `dead/`.

## 4. Operating

```bash
# from the driver
tools/galaxy/deploy/deploy.sh                 # (re)deploy everything, then verify.sh (needs tools/replica/deploy first)
tools/galaxy/deploy/deploy.sh status          # push code, then one galaxy-setup.sh step: status | units | start | ...
tools/galaxy/deploy/deploy.sh frontend        # install a new frontend build from /home/bcreplica/galaxy/frontend-dist
tools/replica/deploy/verify.sh                # isolation + both sites (galaxy checks included)
python3 tools/galaxy/e2e.py --site https://galaxy.136-86-167-127.sslip.io   # contestant flow, about 2 min
# on the VM
sudo /usr/local/lib/bc23-galaxy/galaxy-setup.sh status
bc23-galaxy-manage bootstrap status           # episode, users, teams, submissions and matches by status
bc23-galaxy-manage bootstrap audit            # every host name in the running settings/episode/staff e-mails
bc23-galaxy-manage bootstrap purge-teams e2e- # delete throwaway teams/users (and their matches and files)
bc23-galaxy-manage saturn status              # queue counts;  bc23-galaxy-manage relay status: tasks and jobs
bc23-galaxy-manage showmigrations             # any manage.py command, as bcreplica
sudo journalctl -u bc23-galaxy-web -u bc23-galaxy-relay -u bc23-galaxy-saturn -n 100
```

- **Autoscrims.** Episode bc23 has `autoscrim_schedule = "0 */4 * * *"`, galaxy's documented example, interpreted
  in UTC (the job's `time_zone`). siarnaq recorded it as the job `replica-autoscrim-bc23`. The timer that fires it,
  `bc23-galaxy-scheduler.timer`, was enabled on 2026-10-08 01:19 UTC after the 87 field teams compiled; the first
  round is due at 04:00 UTC (21:00 PDT), then every 4 hours. `sudo systemctl disable --now
  bc23-galaxy-scheduler.timer` pauses the rounds. One round by hand:
  `bc23-galaxy-manage relay fire-jobs --job replica-autoscrim-bc23 --force`. That is galaxy's path: a POST to
  `/api/episode/e/bc23/autoscrim/` as `Google-Cloud-Scheduler` with best of 3. It was checked on 2026-10-08
  (204, `admin_authenticated`).
- **Frontend.** `tools/galaxy/frontend/build.sh` installs into `/home/bcreplica/galaxy/frontend-dist`. Then
  `deploy.sh frontend` copies it to `/srv/bc23-galaxy/frontend` (a staging copy, then a rename). With
  `OUT=/srv/bc23-galaxy/frontend` the build installs there directly. Until a build exists the step installs a
  placeholder page.
- **Viewer.** `/viewer/` holds the official 3.0.15 web client. The files are verified against
  `tools/replica/viewer.py` PINS (`docs/replica/VIEWER.md`) and installed by `galaxy-setup.sh viewer`.
  - The page is `tools/galaxy/viewer_page.py`'s `visualizer.html` plus `galaxy-viewer.js`, with no inline script.
  - It loads only `/storage/bc23-replica-secure/episode/<ep>/replays/<uuid>.<ep>`, given as `?<path>` (the
    frontend's Replay! link for bc23), as `?gameSource=<path>`, or as the same path on this origin.
- **Episode settings.** `bootstrap.py` holds the bc23 episode as deployed (dates, release 3.0.15, autoscrim
  schedule, ranked scrimmages allowed). `deploy.sh` (step `bootstrap`) re-applies it, so changes made in `/admin/`
  are reverted by a full redeploy: change `EPISODE` in `tools/galaxy/bootstrap.py` instead.
- **Restart and boot.** All units are enabled. The web unit starts after the hostname unit, so it reads the
  current host name. `refresh-hostname.sh` restarts it when the IP changes.
- **Teardown.** `sudo /usr/local/lib/bc23-galaxy/galaxy-setup.sh teardown` removes the units, the CLI and the site.
  It keeps the data, the database, `/opt` and `/srv`; add `--purge-data` to remove them as well. PostgreSQL stays
  installed.

## 5. Caddy: routing and access control

The site block is `galaxy-setup.sh print-site`, rendered into `/etc/caddy/Caddyfile` by `vm-setup.sh render`.
1. **Bearer requests.** A request to `/api/*` (except `/api/token/*` and `/api/user/password_reset/*`) whose
   `Authorization` is `Bearer <token>` goes straight to siarnaq, with no basic auth. Those are the logged-in
   frontend's calls. siarnaq judges the token. A forged or expired JWT gets 401 on every DRF view, AllowAny ones
   included, because authentication runs before permissions. A forged saturn, Cloud Tasks or Scheduler token gets
   401 from the stand-in verifier. The token, refresh and password-reset views run no authentication at all, so
   they stay behind basic auth. That keeps password guessing for siarnaq accounts off the internet.
2. **`/manifest.json`** is served without auth, because browsers fetch the web app manifest without credentials. It
   is a public static file.
3. **Everything else needs basic auth (`owner`).**
   - `/api/*` and `/admin/*` go to siarnaq with the Authorization header removed.
   - `/static/` (Django admin and DRF assets), `/storage/` (the buckets; `.tmp-*` hidden) and `/viewer/` are
     files.
   - Any other path is the frontend, with SPA fallback to `index.html`. `/replay/*` is a 404.
   - A **401 from siarnaq on this path becomes a 403 without `WWW-Authenticate`**. A 401 answer to a request that
     carried Basic credentials makes Chromium evict them from its cache as rejected. With a 401, every later page
     load would ask for the password again; this was observed. The frontend treats 401 and 403 alike.
4. **Headers on all responses.**
   - `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'
     data: blob:; font-src 'self' data:; connect-src 'self'; frame-src 'self'; worker-src 'self' blob:;
     manifest-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'`. A
     mis-built bundle cannot reach another host from a browser.
   - `Referrer-Policy: same-origin`, because Django's CSRF check for the admin login needs the Origin header.
   - HSTS, nosniff and `X-Frame-Options: SAMEORIGIN`.

**Browser test (2026-10-08).** Headless Chromium 154 ran on the VM, installed for the test and purged afterwards
(25 packages, profile directories deleted). The test is `tools/galaxy/browser_check.py`. The browser reached the
site through Caddy on 127.0.0.1 with the real certificate, and every other host went to a dead proxy.
- **One password entry.** Chromium's basic-auth challenge was answered once, as a person types the password once;
  any later challenge would have been cancelled and counted. With the 403 rule there were **none**.
- **Cached credentials.** Same-origin `fetch()` calls without an Authorization header (the logged-out frontend's
  API calls, downloads), and new top-level pages, carried the cached Basic credentials preemptively. Logged-in API
  calls carried only `Bearer`.
- **The walk.** Logged-out home, rankings, queue and resources pages; login through the form; upload of
  examplefuncsplayer on the Submissions page (compiled, accepted); a request in the scrimmage modal (3 random maps,
  alternating); sign out from the user menu; login as the opponent; Accept in the inbox. The match ran 3-0. Replay!
  opened `/viewer/visualizer.html?/storage/bc23-replica-secure/episode/bc23/replays/<uuid>.bc23`, and the client
  logged `Game un-gzipped!`, `Applying events!`, `Running a game`.
- **Hosts contacted:** only the galaxy host (plus `data:` URIs). There were no blocked requests and no CSP
  violations.
- **Console errors:** the logged-out frontend's expected 403s (`/api/user/u/me/`, `/api/team/bc23/t/me/`), a 404
  for `tournament/next` (no tournament exists) and a 400 for `scrimmaging_record` while logged out. siarnaq answers
  the same way there.
- A probe without any CDP auth handling confirmed it: after one visit with the login, typed URLs (`/bc23/rankings`,
  `/login`, `/bc23/queue`) loaded with preemptive Basic.

## 6. Differences from galaxy

| Galaxy | Replica | Why |
|---|---|---|
| Cloud Run + Cloud SQL Postgres | gunicorn 23 on the VM + Debian PostgreSQL 15 (unix socket) | No Google. Postgres rather than SQLite: `submission/tournament/` uses `DISTINCT ON` (501 on SQLite), and gunicorn's concurrent writers lock SQLite. |
| Python 3.10 environment (`backend/environment.yml`) | Python 3.11 venv, with `tools/galaxy/py310compat.py` restoring the one 3.10 behaviour siarnaq relies on: `random.sample` of a dict view, which picks the 3 maps of every ranked request (`compete/serializers.py`); on plain 3.11 every ranked request was a 500 (found and fixed 2026-10-08). Package versions as galaxy's except: Django 4.1.2 → 4.1.13, Pillow 9.0.1 → 9.5.0, conda psycopg2 2.9.3 → psycopg2-binary 2.9.9 (no 3.11 wheels or support before these), gunicorn 20.1.0 → 23.0.0 (request-smuggling fixes; the API path is reachable from the internet with a Bearer header); unpinned transitive packages pinned to late-2022 releases; no `google-*` packages, and `django-storages` without the `[google]` extra | Debian 12 ships 3.11. Hash-locked: `tools/galaxy/requirements.txt`. |
| GCS signed URLs (expire after 1 h) and public `storage.googleapis.com` URLs | same-origin `/storage/<bucket>/<name>`, no signature or expiry, behind basic auth | Same-origin and CSP-clean. The owner is the only basic-auth user. |
| Titan scans PDFs with ClamAV | marked Verified at once | Only the owner uploads. |
| Pub/Sub redelivers a nacked message at once | after 10 s | A failure that repeats does not spin. |
| saturn clones the scaffold (GitHub) and runs Gradle | bare javac/java with the pinned jar, as galaxy-lite does | No network. Same flags (GALAXY.md 6.4). |
| saturn reports a match OK! whatever the winner lines say | scores that do not add up to the maps, or a malformed binary zip, are TRY | siarnaq would divide by zero rating such a match. |
| no per-game limit | 1800 s per game (`GALAXY_GAME_TIMEOUT`) | A hung engine does not hold a slot. |
| Cloud Scheduler fires the autoscrim job | the job is recorded; a systemd timer fires it each minute its cron matches (enabled 2026-10-08) | No Google. |
| saturn on autoscaled cloud machines | 5 engines on one 8-vCPU VM shared with the experiment queue | One autoscrim round (176 matches of 3 games for 88 teams) takes several hours here (section 8, capacity). |
| logged-out API calls get 401 | 403 (no challenge) on the basic-auth path | Keeps the browser's basic-auth login (section 5). |
| episode hourly scrimmage limits 10 ranked, 10 unranked (model defaults; staff-editable per episode) | 20 ranked, 40 unranked (`tools/galaxy/bootstrap.py`; set 2026-10-07) | Owner, PROMPTS 15-16: galaxy counts a request and its match, so 10 meant 5 requests an hour; the VM is the real limit. |
| e-mail via Mailjet (password reset, verification) | never sent | Owner rule: no external contact. **Password reset cannot work**; reset in `/admin/` or with `bc23-galaxy-manage changepassword <user>`. |
| tournaments and brackets via Challonge | not usable | `bracket/challonge.py` would call api.challonge.com. bcreplica has no DNS or egress, so the call fails. Do not create tournaments. |
| swagger UI (`/api/specs/swagger-ui/`) loads its assets from a CDN | blocked by the CSP (the page stays blank) | `/api/specs/` (the schema) works. |
| frontend from play.battlecode.org | the same app, built by `tools/galaxy/frontend` (same-origin API, local fonts, bc23 replays in `/viewer/`) | The frontend agent's notes. The Resources page for bc23 has no content in this frontend version. |

Strings that name official hosts and remain reachable, all inert:
- siarnaq's admin replay link `https://releases.battlecode.org/client/...` (`episodes/admin.py`, tournament rounds
  only, clicked by hand). The admin's CSP does not stop navigation; do not click it.
- The e-mail templates' links (never rendered).
- The episode's `scaffold` URL (`https://github.com/battlecode/battlecode23-scaffold`), shown to contestants and
  never fetched.
- `bootstrap audit` on 2026-10-08: own hosts `galaxy.136-86-167-127.sslip.io` and `bc23-replica.invalid`, the link
  `github.com` (`episode.scaffold`), and no external host.

## 7. Verified (2026-10-08, battlecode-dev)

- **Deploy.** `deploy.sh` installed: PostgreSQL 15 with no TCP listener; the source (archive comment = pinned
  commit); the venv (`--require-hashes`, `pip check` clean, as the operator, then root-owned); the secrets, units,
  CLI, 56 migrations, bootstrap, collectstatic, the viewer (24 files against the pins), the frontend copy, and the
  Caddy site with a Let's Encrypt certificate. The old site kept answering (401 without, 200 with the password).
- **`verify.sh`:** 116 PASS, 0 FAIL. The galaxy checks:
  - Units: active, running as bcreplica in the slice, resolved sockets inaccessible.
  - saturn: its namespace holds only `lo`; `curl http://1.1.1.1` and `127.0.0.1:8024` from inside it fail; it
    sees no secrets.
  - Ports and sockets: 8024 bound to 127.0.0.1 only; bcreplica may connect to it; the relay socket is mode 600;
    PostgreSQL has no TCP listener and `listen_addresses` is empty.
  - Imports and settings: no Google library in the venv; stand-ins only; no external host in settings; actions
    on, e-mail off, DEBUG off.
  - Site, without credentials: 401 everywhere except `/manifest.json`.
  - Site, with the password: frontend, deep link, API, static, viewer, bundle and asset return 200; `/replay/*`
    is 404; CSP and Referrer-Policy present; a logged-out API call returns 403 without a challenge.
  - Forged tokens: a JWT on an AllowAny GET and on the registration POST, a saturn report token and a Cloud Tasks
    token are each 401.
  - Bearer on the token endpoint, admin, frontend, storage and viewer gets 401 (basic auth).
  - A foreign Host header is not proxied, and port 8024 is closed from outside.
- **End to end through the real host** (`tools/galaxy/e2e.py`, from the driver):
  - Two contestants registered (`POST /api/user/u/`) and logged in (`/api/token/`), and created teams.
  - Each uploaded examplefuncsplayer's source zip (`POST /api/compete/bc23/submission/`), which compiled OK! and
    was accepted. The download URL returned the same zip.
  - An unranked request on SmallElements went to B's inbox, B accepted it, and the match ran OK! (0-1).
  - The replay downloaded from the API's `replay_url` (674 283 bytes, gzip).
  - The two `rating_update` Cloud Tasks were delivered (204).
  - User and team avatars, a resume (Titan stand-in) and a team report were uploaded and served from `/storage/`.
    siarnaq's report GET answers `{}`, as in galaxy.
  - Throwaway teams and users were purged afterwards: `bootstrap status` shows 0 teams, 0 submissions and 0
    matches.
- **Egress.** The kernel's drop log showed only the probes made by `verify.sh` itself during these runs.
- **Unit tests.** `test/galaxy/test_galaxy.py` (46 tests: stand-ins, spool, tokens, cron, saturn protocol and
  report payloads, real javac/Verifier compiles of success and failure, zip-slip, execute with a fake engine,
  relay, deploy renderers) runs in `tools/unit-tests.sh`.

**Not verified:**
- A reboot. The units are enabled, but boot ordering with the hostname unit has not been exercised.
- An autoscrim round with teams, fired by the timer: the first is due 2026-10-08 04:00 UTC. The
  scheduler-to-autoscrim call was exercised with no teams. Ranked requests work since the 3.10 compatibility fix
  (section 6); the first ranked matches ran on 2026-10-08 (section 8).
- `galaxy-setup.sh teardown`.

## 8. Who plays here, and the operator tools (2026-10-08)

**Teams.** 88 regular teams, each with an accepted submission and auto-accept on for ranked and unranked requests
(as many real teams had):
- **vibe23**, ours, created by the lead with `tools/contest.py` as a contestant (HANDOFF.md).
- **The field**: the 87 public 2023 bots of `tools/field.txt`, created by `tools/galaxy/field.py seed` (on the VM)
  entirely through the public API, each as its own user: sign-up (`POST /api/user/u/`), login, team creation, the
  team profile (`PATCH /api/team/bc23/t/me/`), then the source zip (`POST /api/compete/bc23/submission/`). All 87
  compiled and were accepted on the first upload. There is no examplefuncsplayer team (none existed in the contest).
- Team names are the entrant names, except `team-remember-to-hydrate.sprint_1` (33 characters; galaxy allows 32),
  which is `remember-to-hydrate.sprint_1`. `tools/galaxy/field-teams.tsv` maps every entrant to its team, user,
  package, source directory and zip mode.
- The bots were packaged blind (CLAUDE.md rule 3): the package directory is found by file names only, the zip holds
  its `.java` files under `<package>/`, and `field.py plan` compiles each candidate zip first with all compiler output
  discarded. 86 zips hold the package alone; `DukeBas._main` needs its repository's helper packages, so its zip holds
  the whole source root.
- The field users' passwords exist only on the VM, in `~/.bc23-galaxy-field/accounts.json` of the operator
  (directory 700, file 600; `field.py` refuses a readable file). They are never printed or committed.

**Staff actions**, as galaxy's staff would take them: the episode (`bootstrap.py`), the autoscrim schedule (the timer,
section 4) and nothing else. The episode has no eligibility criteria.

**Field activity** (`field.py activity`, the replacement of galaxy-lite's matchmaker), detached on the VM as the
operator:
```bash
cd ~/projects/vibe/2023; setsid nohup python3 tools/galaxy/field.py activity > logs/field-activity.log 2>&1 < /dev/null &
kill <pid>                                  # stops cleanly (SIGTERM); never pkill -f a pattern
```
Once a minute, while fewer than 2 matches wait in saturn's execute queue (`ready` + `delayed` in the spool), a random
field team requests a RANKED scrimmage, logged in as its own user, against one of the 3 teams rated closest at or
above it (galaxy refuses ranked requests to lower-rated teams). Ranked requests always use 3 random maps in shuffled
order. The opponent's auto-accept turns the request into a match. Galaxy's limits are enforced by the server and
handled: a 429 (the episode's hourly ranked limit, requests plus matches) rests that team for an hour, a 409 (at most 3 active
against one team, or the opponent fell below) for 10 minutes. Because matches run in arrival order, a request from our
team waits behind at most 2 field matches, plus the running ones. Our team is an ordinary opponent for the field.

**Results** (`tools/galaxy/results.py`, on the driver, over the public site; read-only). It lists every match
(`GET /api/compete/bc23/match/`, newest first) as the superuser `owner`, who sees every replay link, and downloads
each finished match's replay (one file with all its games). It reads the file with `tools/replay-dump.sh <file>
--games` and appends one row per game to `progress/games.csv`:
- `run=galaxy-<match id>`, `seq` = game number, `teamA`/`teamB` = player 0/1. Field teams appear under their entrant
  name. Our team appears as `us:<package>` of the submission that played, read from our own submission list as
  vibe23, so each build is its own player in `tools/elo.py` (`elolib.is_ours` is the `us:` prefix).
- `winner`, `rounds`, and `reason` = '' (the replay holds no end reason). `seed` = `map`, or `map-rev` for the odd
  games of an alternate-order match (autoscrims and ranked requests).
- A `(run, seq)` already in the file is never written again. `~/.cache/bc23-galaxy-results/state.json` keeps the
  oldest unfinished match, so a run reads only the newer pages. Replays are deleted after parsing (`--keep DIR`
  keeps them). A game without a winner is skipped and reported.

**Ladder snapshot** (`tools/.venv/bin/python tools/galaxy/snapshot.py`, on the driver). It reads the Rankings page's
data (`GET /api/team/bc23/t/?ordering=-rating,name`, logged out) and the latest matches. It writes
`progress/ladder.md` (table, games W-L from `games.csv`, latest matches) and `progress/ladder.png` (ranked bars, our
team in blue). Both say that the rating is the replica's displayed rating (penalized Elo), not the BT fit of
`progress/ELO.md`.

**Check-in routine (driver):** `python3 tools/galaxy/results.py`, then `tools/.venv/bin/python tools/galaxy/snapshot.py`,
then `tools/elo.py` as before; commit `progress/games.csv` and `progress/ladder.{md,png}` together.

**Capacity.** One autoscrim round for 88 teams is 176 matches of 3 games. galaxy-lite ran about 23 such matches an
hour on 3 engines, so 5 engines give roughly 35-40 an hour while the experiment queue also runs 5 games. A round
then takes about 4.5-5 hours, a little longer than the 4-hour schedule. Matches run in arrival order, so for several
hours after each round fires, our requests wait behind the round, and the field activity stays idle (the queue is
never short). If that starves our work, the staff remedies are a longer schedule (`EPISODE['autoscrim_schedule']` in
`bootstrap.py`, re-applied by `bootstrap episode`, e.g. `0 */8 * * *`) or more engines once the experiment queue
drains.

**Verified (2026-10-08, after the cutover).** `field.py seed` and `wait`: 87 of 87 field submissions compiled and
accepted, and a second `seed` changes nothing. Every team shows auto-accept A/A and an active submission through the
API. The first ranked requests from the field activity were accepted and played as alternate-order best-of-3
matches (e.g. match 12). `results.py` appended the finished matches (our unranked 10-map blocks as `us:g_iter0`, the
ranked match with `map-rev` on game 2), and a second run added nothing. `verify.sh`: 101 PASS, 0 FAIL, including
the retired galaxy-lite checks (units stopped and disabled, nothing on 8023, data archived, the old host name a 302
to the galaxy site). `tools/unit-tests.sh` passes, with `test/galaxy/test_field_tools.py` (19 tests).
