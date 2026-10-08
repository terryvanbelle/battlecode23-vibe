# galaxy-lite: the private Battlecode 2023 ladder replica

galaxy-lite is a small re-implementation of the official judging stack ("galaxy": siarnaq + saturn). It is
written in standard-library Python and runs only on `battlecode-dev`. Our builds and the downloaded 2023 bots play
ranked scrimmages under galaxy's rules, and the ratings are galaxy's Penalized Elo. The design study is
`research/prior/GALAXY.md` (sections 2, 6.4, 6.5 and 7). This guide covers how to operate the replica.

Since 2026-10-08 the real galaxy (siarnaq, unmodified, with local stand-ins for Google Cloud, and galaxy's own
frontend) also runs on battlecode-dev, at `https://galaxy.<external-ip-with-dashes>.sslip.io/`
(`docs/galaxy/README.md`). galaxy-lite keeps running beside it until the cutover.

On battlecode-dev the replica runs as systemd services under the locked-down user `bcreplica`. The owner reads
the ladder, the matches and the replays (in the official 2023 viewer) at `https://<external-ip-with-dashes>.sslip.io/`
(on 2026-10-07: https://136-86-167-127.sslip.io/), as user `owner`. The password is in
`~/.bc23-replica-password` on the driver and the VM. The host name follows the VM's external IP
(`docs/replica/DEPLOY.md` section 6; `tools/replica/deploy/refresh-hostname.sh` prints the current URL). The fallback is a snapshot committed to GitHub:
`progress/ladder.md` and `progress/ladder.png`.

Nothing in the replica contacts any network service. It has no Battlecode, MIT, GCP, GitHub, mail or Challonge
client. The engine runs with `-Dbc.server.websocket=false`. The only socket is the HTTP listener, which serves the
JSON API and the web pages, and it accepts only a loopback address. `test/replica/test_replica.py` fails if any
file under `tools/replica/` names `battlecode.org`, `googleapis`, `challonge`, `mailjet` or `github.com`. It
allows one exception: the deploy scripts' pinned Caddy download URL in `deploy/config.sh`. The replay viewer's
files came from a one-time download of the official 3.0.15 web client release, recorded with every URL and
sha256 in `docs/replica/VIEWER.md`.

## Files

| Path | What |
|---|---|
| `tools/replica.py` | the CLI (all commands below) |
| `tools/replica/db.py` | SQLite schema (galaxy's table, field and enum names), data dir, helpers |
| `tools/replica/rating.py` | Penalized Elo (`teams/models.py` `Rating`), `try_rating_update` (`compete/models.py:454-542`), the rating pump |
| `tools/replica/matchmaking.py` | `generate_4regular_graph` and `autoscrim` (`teams/managers.py`), scrimmage requests and their rules |
| `tools/replica/worker.py` | the runner (replaces saturn): claim, compile/verify, one engine run per match, report, pump, reaper |
| `tools/replica/api.py` | JSON read models and the HTTP server (127.0.0.1:8023): JSON API, and the web routes of `web.py` |
| `tools/replica/web.py` | the server-rendered web pages, the replay file route and the viewer page (read-only) |
| `tools/replica/viewer.py` | checks the downloaded web client against its pinned sha256s and installs it (no network code) |
| `tools/replica/snapshot.py` | writes `progress/ladder.md` and `progress/ladder.png` for GitHub |
| `test/replica/test_replica.py` | unit tests (run by `tools/unit-tests.sh`; no games); also loads `test_deploy.py` |
| `test/replica/fixtures/engine-3maps.log` | a real 3-map engine log (us:bot vs examplefuncsplayer, alternate order) |
| `tools/replica/deploy/` | OS lockdown, web front (Caddy) and the replica's systemd units: `docs/replica/DEPLOY.md` |
| `docs/replica/VIEWER.md` | where the replay viewer came from (URLs, sha256), what it may contact, how it was verified |

Data lives in `$REPLICA_HOME`: `replica.db` (SQLite, WAL mode), `replay/<uuid>.bc23` (one file per match holding
all its games), `sub/<submission id>/{source,binary}/`, `logs/` (`worker.log`, and `match-<id>.log` with the full
engine output of every attempt) and `viewer/` (the installed web client). Without `$REPLICA_HOME`, the code uses
`/home/bcreplica/replica` when that directory holds a DB (the services' data on battlecode-dev), else
`~/replica`. So operator commands on the VM read the services' DB and never split off a second one.

## Quick start (on battlecode-dev)

The web server and the worker already run as services (section "Services"). The DB belongs to user `bcreplica`,
so **commands that write go through the wrapper `bc23-replica`**. The wrapper runs `tools/replica.py` as
`bcreplica` with the services' environment. Read-only commands also work as `terryvanbelle`, who is in the
`bcreplica` group.

```bash
cd ~/projects/vibe/2023                       # code: pushed from the driver (see "Updating the code")
bc23-replica status                           # queue counts, running matches
bc23-replica seed-field --names a,b           # register field bots (tools/field.txt names; --limit N)
bc23-replica add-team us:bot                  # one of our builds: classes from build/classes/bot, snapshotted
bc23-replica autoscrim                        # one round: 4 ranked best-of-3 matches per team (round-robin if <= 4 teams)
bc23-replica wait                             # until nothing is queued or running (the worker service runs them)
python3 tools/replica.py ratings              # the ladder (read-only, as terryvanbelle)
```

From the driver: `source tools/vm.sh && IP=10.138.0.3 && gssh 'cd ~/projects/vibe/2023 && python3 tools/replica.py ratings'`.
`gssh 'bc23-replica autoscrim'` queues a round.

A fresh data dir starts with `bc23-replica init` (episode bc23 plus the 103 maps of `tools/maps.txt`, all
public). Running without the services, for example in a scratch dir, still works as before:
`REPLICA_HOME=~/scratch-replica python3 tools/replica.py init`, then `run-worker --slots N` in the foreground or
under `setsid nohup`.

## Teams and submissions

- **Naming.** Each of our builds is its own team, `us:<package>` (for example `us:bot`, `us:examplefuncsplayer`).
  A benchmark bot uses its manifest name (`bc23-benchmarks/manifest.tsv`: name, package, classdir, repo,
  commit). With no `--classdir` or `--source`, `add-team us:<pkg>` takes `build/classes/<pkg>` (`$CLASSES`), and a
  manifest name takes its manifest row.
- **Prebuilt classes** are registered without compiling: status `OK!`, accepted. For `us:` teams the package's
  class tree is copied to `sub/<id>/binary/`, so a later rebuild cannot change the bot. Benchmark class dirs are
  used in place, because they are immutable. Use `--snapshot` or `--no-snapshot` to override either default. The
  submission's description records `classes sha256:<16 hex>` of the package's class files. With `--verify`, the
  submission is queued and the worker runs only the engine `Verifier` before accepting it.
- **Source submissions** (`submit TEAM --source DIR|ZIP`) are compiled by the worker as the judge compiles them.
  The source is either a directory holding `<package>/` (for example `src`), the package directory itself, or a
  zip of at most 5 MiB. A zip is extracted with saturn's zip-slip check. Then `javac -source 8 -target 8
  -proc:none` runs through `tools/lib.sh compile_src`, followed by `battlecode.instrumenter.Verifier <pkg>
  <classes>`. A compile or verify failure is `OK!` with `accepted=0`, as in saturn. Only infrastructure errors are
  retried.
- **The active submission** is a team's newest accepted submission, as in galaxy. Matches pin the submission that
  was active when they were created.
- **Team mode.** Galaxy carries one team's rating across all of its uploads. To rehearse that, keep one team
  (`us:ladder`, say) and `submit` each new build to it. One team per build measures each build cleanly instead.
  Record which mode a result came from (GALAXY.md section 7, item 17).

## Matches

- **`autoscrim`** ports `TeamQuerySet.autoscrim` line for line. It takes REGULAR teams that have an accepted
  submission and sorts them by rating **mean** (ties by team id; galaxy leaves ties in database order). It builds
  a 4-regular graph whose edges are at most 4 rank places apart (a round-robin for 4 teams or fewer), randomizes
  edge direction and order, and draws `random.sample(public maps, best_of)` for each match. Matches are
  `is_ranked=1, alternate_order=1, source='autoscrim'`. Six teams give 12 matches.
- **`request BY TO [--ranked] [--order ?|+|-] [--maps a,b,c]`** creates a scrimmage request. It is accepted at
  once when the opponent's `auto_accept_reject_*` setting is `A`, the replica's default (galaxy's default is
  manual). Use `requests`, `accept ID` and `reject ID` for manual ones. With no maps, a request gets
  `autoscrim_best_of` (default 3) random public maps while the rules are off. With the rules on, a ranked request
  always gets 3 random public maps and an unranked one must name its maps, as in galaxy.
- **Rules** (`config enforce_rules=1`, default 0) switch on galaxy's ranked-request checks from
  `compete/serializers.py:400-465` and `compete/views.py:942-1041`:
  - ranked requests must use shuffled order, and their maps must be empty (3 random maps are drawn);
  - no ranked requests by or against staff teams;
  - ranked scrimmages are refused when `is_allowed_ranked_scrimmage=0`;
  - an hourly cap counts requests plus matches, so accepted requests count twice (section 7, item 7);
  - at most 3 active ranked matches or requests per pair;
  - ranked requests only against a team whose displayed rating is not lower.

  Some checks always apply: no self-requests, the opponent must have an accepted submission, and the maps must
  exist. Other settings are `ranked_scrimmage_hourly_limit`, `unranked_scrimmage_hourly_limit` and
  `autoscrim_best_of`. Show them with `config` and set them with `config key=value`.
- **Execution.** Each match is **one engine invocation with all its maps**, with the flags of GALAXY.md 6.4
  step 3:
  - `-Dbc.server.alternate-order=<alternate_order>`, so spawn sides flip on every second game while the code
    stays labelled A/B;
  - indicators off, `validate-maps=true`, `websocket=false`;
  - the replay is saved to `replay/<uuid>.bc23`;
  - no `-Dbc.game.seed`, so the map seeds decide;
  - the time limit is `REPLICA_GAME_TIMEOUT` (default 1800 s) times the number of maps.

  Scores are counted with saturn's regex `^\[server\]\s*.*\(([AB])\) wins \(round [0-9]+\)$` and reported as
  `[aWins, bWins]`. Each game's map, winner, round, reason and reversed flag go to the `game` table.
- **Job protocol** (saturn plus `SaturnInvocationSerializer`):
  - A claim moves `QUE`/`TRY` to `RUN` atomically, oldest first.
  - The result is `OK!`, or `TRY` on an engine error, a timeout or an unreadable log.
  - A `TRY` that was not an interruption adds 1 to `num_failures`. At 5 failures the job becomes `ERR`, which
    counts as unranked for ratings.
  - A report on a finalized job is refused, as siarnaq's 409 is.
  - Stricter than galaxy: an `OK!` with scores `[0,0]`, or with fewer wins than maps, is stored as `TRY`.
- **Stopping and the reaper.** SIGTERM or SIGINT stops the worker. It kills only the engines it started (their
  process groups) and reports them as interrupted `TRY` with no failure counted. They rerun on the next start.
  The reaper runs at worker start and every 60 s. It returns `RUN` matches to `TRY` when their worker process on
  this host is gone (interrupted) or when they have run longer than 2 x their time limit + 60 s (a failure).
  `requeue ID` puts back a match that is not `OK!`, and `cancel ID` cancels one. As in galaxy, a requeued `ERR`
  or `CAN` match whose participations were already rated (unchanged, as unranked) does not move the ratings when
  it later finishes. Only participations that were still waiting for an earlier match get the new result.

## Ratings

- Penalized Elo uses galaxy's constants: K = 24, scale 400, initial mean 1500, penalty 0.85. A ranked match moves
  each side's mean by `mu' = mu + 24 (S - E)`. `S` is the fraction of the match's games won. `E` is computed from
  both sides' means **just before this match**. The displayed rating is `value = mu - 1500 * 0.85^n`, so a new
  team shows 0.
- An unranked, errored or cancelled match leaves the rating unchanged (n does not grow).
- A team's displayed rating follows its participation with the highest n.
- **Creation order.** A participation is rated only once the team's previous participation is rated. For a ranked
  match, the opponent's previous participation must be rated as well. The *rating pump* (`rating.pump`) replaces
  galaxy's Cloud Tasks. It repeats `Match.try_rating_update` over unrated matches in creation order until nothing
  changes. It runs after every report, so results never depend on completion order. One match stuck in `RUN`
  blocks its two teams' chains until it finishes, errs out or is reaped (section 7, item 6).
- `ratings` prints: rank by displayed rating, mean, n, ranked match record (W-L-T by summed scores, as galaxy's
  `scrimmaging_record` computes it, leaving out matches against invisible `O` teams), and games won-lost. `history TEAM` prints the rating after each ranked match
  and the recent matches. `match ID` prints the games, with `--logs` for the job log.

## Export to the BT ladder

`export-games` appends one row per game of every `OK!` match not exported yet to `progress/games.csv` (or `--out
F`). The columns are `run,seq,teamA,teamB,map,winner,rounds,reason,seed`:

- `run` = `replica-<match id>`;
- `seq` = the game's number inside the match (1-based);
- `teamA`/`teamB` = the teams whose code ran as A/B (player_index 0/1);
- `winner` = the engine's A/B;
- `reason` = the end-of-game code from `tools/elolib.py` (`ISL75`, `TB_ISL`, `TB_ANCH`, `TB_EX`, `TB_MN`, `TB_AD`,
  `COIN`, `RESIGN`); the analysis tools drop `COIN` games (the engine's unseeded coin flip carries no information);
- `seed` = `map` for a game played with the map's own spawns, `map-rev` for one with HQ ownership flipped (games 2,
  4, ... of a match: the same packages as A and B, swapped spawns). The analysis tools' dedupe keys games on
  (teamA, teamB, map, seed), so both orientations are kept, while an exact repeat (same pairing, map and orientation,
  which the engine replays identically) is dropped.

Rows are marked as exported in the DB, so running it again appends nothing new. `--all` writes every completed
game and leaves the marks alone, which is useful for a fresh file. The API's `POST /replica/export-games` does
the same. `REPLICA_GAMES_CSV` overrides the default path.

**Under the services** the export needs both users: only `bcreplica` may mark games in the DB, and only the operator
may write `progress/games.csv`, which lives in the driver's checkout. From the driver:

```bash
bash tools/replica-export.sh      # export on the VM into /home/bcreplica/replica/export/, fetch, append new rows
```

It appends only rows whose (run, seq) is not already in `progress/games.csv`, so it can be re-run safely, and the
export files stay on the VM as the record.

## API

`python3 tools/replica.py serve [--port 8023]` starts the HTTP server: this JSON API plus the web pages
(next section). It refuses any non-loopback address. On battlecode-dev it runs as the service
`bc23-replica-api`. From the driver, reach it with `ssh -L 8023:127.0.0.1:8023 <vm>`, or read it through the
public front, which passes only GET and HEAD. The paths mirror siarnaq's, with the episode `bc23`.
Lists are paginated `{count, next, previous, results}` with `?page=` and `?page_size=` (max 1000). `team_id`
accepts an id or an exact name.

| Method and path | What |
|---|---|
| `GET /api/team/bc23/t/?ordering=-rating` | teams: `profile.rating` (value), `rating_mean`, `rating_n`, active submission |
| `GET /api/compete/bc23/match/?team_id=&status=` (also `/match/scrimmage/`) | matches, newest first, with games |
| `GET /api/compete/bc23/match/<id>/[?logs=1]` | one match: participants (score, rating, old_rating), maps, games, replay |
| `GET /api/compete/bc23/match/historical_rating/?team_id=` | rating after each ranked match, in creation order |
| `GET /api/compete/bc23/match/scrimmaging_record/?team_id=` | Ranked / Unranked / All wins, losses, ties |
| `POST /api/compete/bc23/request/` | `{requested_by, requested_to, is_ranked, player_order, map_names}` |
| `GET /api/compete/bc23/request/?status=P`; `POST .../request/<id>/accept/` or `/reject/`; `DELETE .../request/<id>/` | request inbox and outbox |
| `POST /api/compete/bc23/submission/` | `{team, package, prebuilt_classes or source, snapshot?, verify?, description?}` |
| `POST /api/team/bc23/t/create/` | `{name, status?}` |
| `POST /api/episode/e/bc23/autoscrim/` | `{best_of}` → `{matches: [ids]}` |
| `POST /api/compete/bc23/match/<id>/requeue/` | requeue a match that is not `OK!` |
| `GET /replica/status`, `GET /replica/ratings` | queue counts and running matches; the ratings table |
| `POST /replica/export-games` | `{out?, all?}` → `{rows, out}` |
| `GET /replica/replay/<uuid>.bc23` | the replay file |

## Web pages

The same server renders HTML pages (`tools/replica/web.py`). They are server-rendered, with inline CSS and inline
SVG charts, no scripts, and nothing loaded from another host. They follow the light or dark system setting and fit
a phone: on narrow screens, secondary columns hide and the charts switch to a narrow layout. Times are in
`REPLICA_TZ` (default `America/Los_Angeles`). Every page is read-only, and a test checks that GET and HEAD never
write the DB.

| Path | What |
|---|---|
| `/` | **the ladder**, in galaxy's order (displayed rating, then id): rank; team; **displayed rating** (penalized: `mean − 1500·0.85^n`); a sparkline of the displayed rating over the last 30 ranked matches, starting from 0; mean; n (rated matches); ranked matches W-L-T; games W-L (every game, ranked and unranked); time of the last completed match. Our builds (`us:...`) are tinted and badged. The header shows the running, queued and error counts. |
| `/team/<id>` | the team's rank, rating, mean, n, records and active submission; two inline-SVG charts, the displayed rating and the mean after each ranked match in creation order (hover a point for its match); and all its matches, 100 per page: opponent, score, W/L/T, rating change, mean change, maps, type, time and a Watch link. |
| `/match/<id>` | status (queued / retrying / running / done / error / cancelled), ranked or not, source, times and failure count; **Watch replay**, **Download .bc23** and JSON links; both teams with code A/B, score, rating and mean before, after and change, and the submission; one row per game: map, spawn sides (normal or swapped), winner, rounds and reason. Errored, retrying and cancelled matches also show the job log. |
| `/matches` | matches, newest first, 50 per page, with status filters (`?status=queued`, `running`, `done`, `error`, `cancelled`) and `?team=<id or name>`. |
| `/replay/<uuid>.bc23` | the raw replay file (ETag, HEAD) |
| `/viewer/visualizer.html?gameSource=/replay/<uuid>.bc23` | the replay viewer (next section) |

A match's rating change shows once the pump has rated it. A completed match waits for each team's earlier
matches (creation order), and the page says so.

## Replay viewer

The **Watch** links open the official Battlecode 2023 web client (release 3.0.15) under `/viewer/`. It is
self-hosted: the client's bundle and images are served from `$REPLICA_HOME/viewer/out/`. The page lets the client
load only replays of this replica, and its Content-Security-Policy keeps all of the client's network requests on
this origin. One replay holds every game of a match; pick a game in the viewer's Queue tab. Where the files came
from (the release URL and every sha256), what the bundle could contact, and how it was verified are in
`docs/replica/VIEWER.md`. To reinstall: `tools/replica/viewer.py install <download dir>`, as `bcreplica`.

## Snapshot for GitHub (the fallback when the web front is down)

```bash
python3 tools/replica/snapshot.py --from-vm   # on the driver: read the VM's ladder over ssh, write progress/ladder.{md,png}
python3 tools/replica/snapshot.py             # on the VM: read the DB directly, write <repo>/progress/ladder.{md,svg}
```

The result is `progress/ladder.md`: the ladder table (our builds in bold) and the 20 latest completed matches.
Next to it is `progress/ladder.png`, the table with rating sparklines drawn by matplotlib. matplotlib comes from
the driver's `tools/.venv`, and the script re-runs itself there. Where matplotlib is missing (the VM), the script
writes `ladder.svg` instead and removes the PNG, so only one image exists. `--from-vm` runs
`snapshot.py --json` on the VM as `terryvanbelle` and opens the DB read-only. `--recent N`, `--svg` and
`--out-dir D` adjust the output. Regenerate the files rather than edit them, and commit them together.

## Services (systemd on battlecode-dev, user bcreplica)

`tools/replica/deploy/vm-setup.sh services` installs the units. `deploy.sh` runs that step too. Each unit runs as
`bcreplica` in `bc23-replica.slice` (localhost-only IP), after and requiring the egress lockdown unit, with
`UMask=0027`, `ProtectSystem=strict`, `ProtectHome=read-only` and write access to `/home/bcreplica/replica` only
(contract: `DEPLOY.md` section 4). The worker and autoscrim units also run in a private network namespace with only
`lo` (`PrivateNetwork=yes`). The engines the worker starts therefore have no network at all. The code runs from
the operator's checkout `REPLICA_REPO`, which the services can only read. The environment is `/etc/bc23-replica/replica.env`: `REPLICA_HOME`, `REPLICA_REPO`, `JAVA_HOME`,
`BENCH_ROOT`, `REPLICA_SLOTS` and `REPLICA_TZ`. The setup writes that file once and keeps later edits.

| Unit | What | State as installed |
|---|---|---|
| `bc23-replica-api.service` | `tools/replica.py serve --host 127.0.0.1 --port 8023`: API, pages, viewer | enabled, running |
| `bc23-replica-worker.service` | `tools/replica.py run-worker --slots ${REPLICA_SLOTS}` (4) | enabled, running |
| `bc23-replica-autoscrim.service` | one `autoscrim` round; skipped while any match is still queued (`REPLICA_AUTOSCRIM_MAX_BACKLOG`, default 0) | started by the timer |
| `bc23-replica-autoscrim.timer` | every 4 hours (`*-*-* 00/4:00:00`), galaxy's documented cadence | **installed, disabled** |

```bash
sudo systemctl enable --now bc23-replica-autoscrim.timer    # start the 4-hourly rounds (the lead's decision)
systemctl list-timers 'bc23-replica*'                       # next run
sudo systemctl start bc23-replica-autoscrim.service         # one round now (or: bc23-replica autoscrim)
sudo journalctl -u bc23-replica-api -u bc23-replica-worker -n 50
sudo -u bcreplica tail /home/bcreplica/replica/logs/worker.log   # per-match lines; logs/match-<id>.log has the engine output
sudo systemctl restart bc23-replica-worker   # after worker code changes; running matches are requeued, no failure counted
sudo /usr/local/lib/bc23-replica/vm-setup.sh status          # all replica units, the URL, the listeners
```

The worker's 4 slots share the VM with the gauntlets. Keep the total at about 8 games or fewer, and lower
`REPLICA_SLOTS` in the env file while big gauntlets run. `vm-setup.sh teardown-services` stops and removes the
units and the wrapper; the data stays.

**Updating the code.** The services run whatever is in `~/projects/vibe/2023` on the VM. `vm_sync` also pushes
other agents' uncommitted `src/` and `tools/` work. To push only the replica:

```bash
source tools/vm.sh && IP=10.138.0.3
rsync -a --exclude __pycache__ -e "ssh ${SSHO[*]}" tools/replica/ "$USER_NAME@$IP:$REMOTE_REPO/tools/replica/"
rsync -a -e "ssh ${SSHO[*]}" tools/replica.py "$USER_NAME@$IP:$REMOTE_REPO/tools/replica.py"
gssh 'sudo systemctl restart bc23-replica-api'      # pages and API (cheap)
gssh 'sudo systemctl restart bc23-replica-worker'   # only when worker code changed
```

## Operating notes

- **Concurrency.** `run-worker --slots N` (default 4) runs N engines at once, so 4 slots means 4 JVMs of about
  1 GB each. The VM also hosts our gauntlets. Keep the replica plus gauntlet total at about 8 games or fewer.
  Galaxy's reference is 0.75 matches per vCPU. `--until-empty` exits when nothing is queued or running, and
  `--max-jobs N` stops after N jobs.
- **Scheduling.** Galaxy's documented autoscrim cadence is every 4 hours. On battlecode-dev that is
  `bc23-replica-autoscrim.timer`, installed disabled (section "Services").
- **Time and disk** (measured 2026-10-07, 4 replica slots alongside a 5-game gauntlet): a best-of-3 match took
  36-765 s, and a 6-team round of 12 matches took 20 minutes. Replays averaged 2.6 MB per match (31 MB for 12).
  There is no retention job yet (GALAXY.md 6.5 step 9). The installed viewer takes 7.3 MiB.
- **Environment.**
  - `REPLICA_HOME`: the data dir.
  - `REPLICA_REPO`: the checkout that holds `tools/lib.sh`, `tools/maps.txt`, `tools/field.txt`, `engine/`,
    `build/classes` and `progress/`. The default is the checkout the code sits in.
  - `REPLICA_GAMES_CSV` and `REPLICA_GAME_TIMEOUT`.
  - `BENCH_ROOT`: the manifest location.
  - `CLASSES`: our class dir.
  - `JAVA_HOME`: read by `tools/lib.sh`, which also pins the engine jar's sha256. The worker refuses to start on
    a mismatch.
- **Map pool.** All 103 maps of the 3.0.15 jar are public (`tools/maps.txt`). The official pool grew during the
  season (section 7, item 10). Use `init --maps-file F` for another pool.
- **Fidelity labels.** Record the mode with every result:
  - *faithful*: map seeds, `enforce_rules=1`, team mode;
  - *measurement*: one team per build, rules off.

  The HEAD galaxy constants cannot be date-checked for January 2023 (section 2).

## Differences from galaxy (deliberate)

- Single SQLite file, no users or auth, and no tournaments, brackets, email, avatars or resumes. Team and team
  profile are merged into one table.
- Ratings are finalized by the pump instead of Cloud Tasks. The results are identical: galaxy's 9 ported
  finalization tests pass, and `GalaxyDifferentialTest` checks the pump against a separate port of galaxy's
  task-driven algorithm on 120 random schedules with cancels, errors, requeues and tasks run in random order.
  Galaxy itself can differ only when an admin requeues an `ERR`/`CAN` match before its rating task has run.
- Bare `java` on the pinned jar instead of the Gradle scaffold. `websocket=false`. Prebuilt class dirs are
  accepted without compiling.
- `[0,0]` or partial scores are a retry, not a divide-by-zero. Stale `RUN` jobs are reaped.
- Requests are auto-accepted by default, and the rules are off by default (on with `enforce_rules=1`).
- Episode freeze and archive checks on autoscrim are not modelled.
- The autoscrim timer skips a round while more than `REPLICA_AUTOSCRIM_MAX_BACKLOG` (default 0) matches are
  `NEW`, `QUE` or `TRY`. Galaxy's Cloud Scheduler fires every 4 hours whatever the backlog, so its next round can
  pair teams by ratings that still wait on the previous round. With the guard, the replica's next round waits
  only on matches still `RUN`. A manual `autoscrim` has no such check.
- Autoscrim ties in rating mean are broken by team id. All new teams tie at 1500, so the first round pairs teams
  that were registered near each other: for `seed-field`, alphabetical neighbours in `tools/field.txt`, which
  often means two bots by the same author. Galaxy leaves the tie order to Postgres.

## Verified on 2026-10-07 (battlecode-dev)

- `init`; `seed-field --limit 5` registered us:examplefuncsplayer and 5 benchmarks.
- A source submission of us:examplefuncsplayer compiled through javac and the Verifier and was accepted.
- One `autoscrim` round produced 12 matches, 4 per team, and they ran with `run-worker --slots 4`:
  - SIGTERM after 54 s requeued the 4 running matches as interrupted `TRY` with 0 failures, and the restarted
    worker finished all 12 as `OK!`.
  - All 24 participations were rated, and an independent sequential recomputation of the ratings matched the DB
    exactly.
  - `export-games` wrote 36 rows.

Then the replica moved under `bcreplica` and its services:
- The DB was copied with SQLite's backup API into `/home/bcreplica/replica`. The 3 snapshotted submission paths
  were rewritten, and the integrity check passed. Replays, submissions and logs were copied as well. The old
  directory is kept on the VM as `~/replica.pre-bcreplica-20261007` (31 MB); delete it when no longer wanted.
- The api and worker services run as `bcreplica` in the slice. Match 13, an unranked request
  us:examplefuncsplayer vs Chahat08.toph queued through `bc23-replica request`, ran under the worker service and
  finished `OK!` 0-3.
- Every page, the viewer, its bundle and the replays load through Caddy with the owner password. Headless
  Chromium played a replay in the viewer with no failed requests and no CSP violations (`docs/replica/VIEWER.md`
  section 5). `tools/replica/deploy/verify.sh` passes, including its checks of the services and the viewer.
- `snapshot.py --from-vm` wrote `progress/ladder.md` and `progress/ladder.png` on the driver.

Not yet done:
- a concurrency knee measurement (GALAXY.md 6.5 step 7);
- the two-round requeue check of step 8;
- a replay retention job (step 9);
- a reboot test of the services (they are enabled, and `systemd-analyze verify` passes);
- running the timer: it is installed but disabled until the lead enables it;
- the two-user export flow under the services (section "Export to the BT ladder").

Only 33 of the 103 jar maps have run under `validate-maps=true` so far: the round's 31 distinct maps plus the
fixture run's.
