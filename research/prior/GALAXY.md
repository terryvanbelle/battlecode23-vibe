# Galaxy (the official Battlecode judging stack): a design study for a private replica on battlecode-dev

Slice: `galaxy`. Source: `/home/terryvanbelle/projects/vibe/reference/galaxy`, a shallow clone with one commit
(`f343088`, 2026-01-06, "modified scaffold for 26, and configs templates (#982)"). Written 2026-10-07.
Galaxy is infrastructure, not a bot project. It contains no games, win rates or p-values, so sections 2 to 4 report
design evidence (code, tests, configuration, operations docs) in place of experiment results. Anything I derived
rather than read is marked **(inference)**.

---

## 0. Recommendation at a glance

**Build "galaxy-lite": a small, stdlib-only Python re-implementation of siarnaq's competition core.** It mirrors the
siarnaq tables and copies the rating, ordering and matchmaking code line for line. A worker speaks saturn's job and
report JSON but runs our pinned engine jar with bare `java`. Do not deploy the real siarnaq or saturn. Section 6.3
gives the reasons. In short, every external-service path in galaxy comes through `google-cloud-*`, `anymail`,
`requests` (Challonge), go-git (GitHub), or Gradle's `update` task, which calls `api.battlecode.org`. A replica that
installs none of those libraries cannot reach Battlecode or GCP infrastructure, even by mistake. A copy of real
siarnaq has to be patched in about 10 places. Two of those places (Cloud Tasks for ratings, GCS for source uploads)
fail silently when they are turned off.

What to copy exactly from galaxy (details in section 2):
- **Penalized Elo**: `TEAMS_ELO_INITIAL = 1500.0`, `TEAMS_ELO_K = 24.0`, `TEAMS_ELO_SCALE = 400.0`,
  `TEAMS_ELO_PENALTY = 0.85` (`backend/siarnaq/settings.py:322-327`). Formulas are in
  `backend/siarnaq/api/teams/models.py:13-58`.
- **Score = fraction of games won in the match.** Ranked matches play 3 random public maps. Order is shuffled and
  sides alternate every map.
- **Ratings are applied in match-creation order per team, not in completion order.**
  See `MatchParticipant.try_rating_update`, `backend/siarnaq/api/compete/models.py:454-542`.
- **Autoscrim**: a 4-regular graph over teams sorted by rating *mean*, with neighbours at most 4 rank places apart,
  best of 3. See `backend/siarnaq/api/teams/managers.py:11-90, 163-253`.
- **Saturn's winner parsing**: regex `` `(?m)^\[server\]\s*.*\(([AB])\) wins \(round [0-9]+\)$` ``
  (`saturn/pkg/run/java.go:16`). Scores are reported as `[aWins, bWins]`.

---

## 1. Scope

### 1.1 Read in full
| Path (under `reference/galaxy/`) | Size | Why |
|---|---|---|
| `backend/siarnaq/settings.py` | 20,430 B | every config, credential and service switch |
| `backend/siarnaq/api/compete/{models,managers,serializers,signals,views,admin,urls,permissions,filters}.py` | ~100 KB | submissions, matches, scrimmage requests, ratings, the report endpoints |
| `backend/siarnaq/api/teams/{models,managers,signals,serializers,views,filters,urls,permissions}.py` | ~44 KB | the Rating model, autoscrim, team API |
| `backend/siarnaq/api/episodes/{models,views,signals,serializers,admin,managers,permissions,urls}.py` | ~41 KB | episode settings, maps, autoscrim schedule, tournaments |
| `backend/siarnaq/api/user/{authentication,signals,models,managers,views,permissions,urls}.py` | ~32 KB | auth, email, resume export |
| `backend/siarnaq/gcloud/{saturn,tasks,titan}.py`, `bracket/__init__.py`, `urls.py`, `middleware.py`, `api/views.py`, `api/refs.py` | ~9 KB | the GCP and Challonge clients |
| `backend/siarnaq/api/compete/test_models.py:160-330` (rating finalization tests), `api/teams/tests.py` (test list) | part of 2,663 test lines | the expected rating behaviour |
| `saturn/cmd/saturn/main.go`, `saturn/pkg/saturn/*.go`, `saturn/pkg/run/*.go` | 1,746 Go lines, 45,563 B | the match runner |
| `saturn/Dockerfile`, `saturn/development/{Dockerfile,docker-compose.yml,configs/*.json}`, `saturn/Makefile` | ~16 KB | how saturn is run locally |
| `titan/**` (Go, Dockerfile, bootstrap.sh) | 320 Go lines | the malware scanner |
| `deploy/main.tf`, `provider.tf`, `state.tf`, `variables.tf`, `deploy/saturn/*`, part of `deploy/galaxy/main.tf` and `deploy/siarnaq/main.tf` | 2,190 tf lines in total | production sizing and queue settings |
| All galaxy `.md` docs: `README.md`, `backend/README.md`, `saturn/README.md`, `titan/README.md`, `deploy/README.md`, `docs-general/{operations,emails}.md`, `docs-general/onboard.md:24-120`, `backend/docs/tournament-development.md`, `frontend/docs/local-setup.md` | 1,392 lines, 75 KB | operations knowledge |
| Migration headers (dates) for all apps; `teams/migrations/0001,0005,0008`; `user/migrations/0002` | — | timeline (the clone has no history) |
| `environment-dev.yml`, `backend/environment.yml`, `backend/Dockerfile`, `pyproject.toml`, `.github/workflows/ci.yml` (first 120 lines), `.pre-commit-config.yaml` (repo lines) | — | dependencies |

### 1.2 Read in part (targeted)
- `backend/siarnaq/bracket/challonge.py` (15.5 KB): lines 1-80 and 288-440, plus a grep for every HTTP call.
- Frontend: `.env.development`, `.env.production`, `src/api/helpers.ts:130-160`, `MatchReplayButton.tsx`,
  `RequestScrimModal.tsx` (grep), `teamApi.ts` and `authApi.ts` (grep). I grepped the whole frontend for
  external hosts.
- Outside galaxy, **code only**, to check what saturn actually executes:
  `reference/battlecode23-scaffold/build.gradle` (lines 1-130 and 240-300) and `gradle.properties` (grep).
  From `reference/battlecode23/engine/src/main/battlecode/` I grepped and read short sections of
  `server/{Server,Config,Main,NetServer}.java`, `world/GameMapIO.java` and `instrumenter/Verifier.java`.
- Our own tools, so the plan reuses them: `2023/tools/{lib.sh, gauntlet.sh, vm.sh, vm-run.sh, throughput.sh,
  elolib.py, sprt.py (head), get-engine.sh, build.sh}`.

### 1.3 Skimmed or skipped, and why
- `frontend/src/content/bc23.ts` was skipped. It is the official bc23 episode content page. The replica does not
  need it, and skipping it avoids 2023 game content. The other `content/*.ts` files were seen only as grep lines
  (links to releases.battlecode.org).
- `frontend/src/api/_autogen/**` (generated OpenAPI client), `frontend/package-lock.json`, the React views, the
  PNG diagrams, and `bracket/example-data/*.json` were skipped as not needed for a headless replica.
- The rest of the backend tests (`compete/test_views.py`, 65 KB) were skipped. The model tests cover the rating
  semantics.
- `saturn/development/pubsubclient.go` was read only as a function list. It is a helper for the Pub/Sub emulator.

### 1.4 Rule compliance
`readroom-no2023/` has no `galaxy` copy, and the slice says to read galaxy directly. Before opening any galaxy
`.md`, I counted lines matching `2023|bc23|post-?mortem|strategy` in each one. Every file had 0 hits. I read no
`.md` or `.txt` file outside galaxy. I read no competitor or benchmark bot. Nothing was run or built, and there were
no network calls.

---

## 2. What worked: galaxy design choices with the evidence available

Galaxy has run the official ladder since bc23. The first siarnaq migrations are dated 2022-11-26, and the initial
`Rating` table already has `mean` (default 1500.0), `n` and `value` (`teams/migrations/0001_initial.py`).
**Caveat:** the clone has a single commit, so I cannot confirm that the HEAD constants (K = 24 and so on) were the
values live in January 2023. The fields and docstrings are unchanged since the initial migration, which makes it
likely (**inference**).

### 2.1 Penalized Elo: the exact formulas and parameters
Sources: `backend/siarnaq/api/teams/models.py:13-58` and `settings.py:322-327`. The docstring calls it "An
immutable database model for a Penalized Elo rating."

A rating is a triple (`mean` μ, `n` = number of rated matches played, `value` v). Each update creates a new Rating
row, and the old row is never changed.

- **Displayed (penalized) value**, recomputed on every save (`Rating.save`, lines 32-38):
  `v = μ − 1500 · 0.85^n`
- **Expected score** against a set of opponents (`expected_score`, lines 52-58), using opponents' **means**:
  `E = (1/|O|) · Σ_o 1 / (1 + 10^(−(μ − μ_o)/400))`
- **Step** after a ranked match that completed successfully (`step`, lines 43-50):
  `μ' = μ + 24 · (S − E)`, `n' = n + 1`, where
  `S = self.score / (self.score + Σ opponent.score)` (`compete/models.py:513-518`). The `score` values are game
  wins inside the match, so a 3-map match gives S ∈ {0, 1/3, 2/3, 1}.
- **New team**: `TeamProfile.save` creates `Rating()` (μ = 1500, n = 0), so the value is **0** at creation.
  A team's first participation uses an unsaved default `Rating()` as its "old rating" (`get_old_rating`,
  `compete/models.py:435-443`).
- **Unranked, failed or cancelled match**: the participant gets the old rating unchanged, and n does not increase
  (`compete/models.py:495-510`).
- **Team display rating**: a `post_save` signal copies a participant's new rating to `TeamProfile.rating`, but only
  if it has a higher n (`rating__n__lt=instance.rating.n`, `teams/signals.py:14-28`).
- For two players, μ is zero-sum (**inference**: both sides use pre-match means, so E_a + E_b = 1 and
  S_a + S_b = 1).

Size of the effect (computed from the formulas):

| n (rated matches) | 0 | 1 | 3 | 5 | 10 | 15 | 20 | 25 | 30 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| penalty 1500·0.85^n | 1500 | 1275 | 921 | 666 | 295 | 131 | 58 | 26 | 11 | 2.3 |

| μ_self − μ_opp | win 3-0 | win 2-1 | lose 1-2 | lose 0-3 |
|---|---|---|---|---|
| 0 | +12.0 | +4.0 | −4.0 | −12.0 |
| +100 | +8.6 | +0.6 | −7.4 | −15.4 |
| +200 | +5.8 | **−2.2** | −10.2 | −18.2 |
| +400 | +2.2 | −5.8 | −13.8 | −21.8 |

A team 200 points above its opponent loses rating on a 2-1 win.

### 2.2 Ratings are finalized lazily, in creation order
`MatchParticipant.try_rating_update` (`compete/models.py:454-542`) explains the ordering in its docstring:
"matches should have their ratings applied in the order they are listed to the client, which is in order of match
creation (this ensures that matches do not spontaneously shuffle). This is usually different to the order of match
completion."

How it is built:
- Each `MatchParticipant` has `previous_participation`, a linked list per team ordered by pk. It is filled in by the
  `connect_linked_list` signal (`compete/signals.py:13-24`) and by `MatchParticipantManager.bulk_create`
  (`compete/managers.py:116-142`).
- A participation is finalized when three things hold: its previous participation has a rating; the match is
  unranked or finalized; and, for a completed ranked match, every opponent's *previous* rating is known. Each side
  then steps from **its own and the opponent's rating just before this match**, not from current ratings.
- After finalizing, it calls `request_rating_update()` on the team's next match, which is a Cloud Task POST to
  `/match/<id>/rating_update/` (`compete/models.py:299-328`, `compete/views.py:839-852`). A `post_save` on every
  `Match` also asks for an update (`compete/signals.py:27-30`).
- Tests: `MatchParticipantRatingFinalizationTestCase`, 9 cases (`compete/test_models.py:160-485`), split by match
  type (ranked/unranked), match status (completed/failed/in progress) and previous participation (finalized/not
  finalized/none). Example assertions: "Expect rating increase after win"; "Expect no rating because previous not
  ready"; "Expect no change because no result".
- **Inference:** the final values depend only on each team's chain order, never on completion order. A replica can
  therefore use a simple "repeat until nothing changes" loop instead of Cloud Tasks and get bit-identical results.

### 2.3 Ranked match format: random maps, random order, alternating sides, all games played
- In `ScrimmageRequestSerializer.to_internal_value` (`compete/serializers.py:431-465`), a ranked request must send
  `map_names` empty ("must be empty for ranked"). The server then picks
  `random.sample(maps.keys(), 3)` from the episode's `is_public=True` maps, with the comment "Ranked matches default
  to best-of-3."
- `validate` (lines 400-414) requires `player_order == "?"` (shuffled) for ranked ("Ranked matches must use shuffled
  order"), and forbids ranked games for staff teams or against them.
- `determine_order` (`compete/models.py:624-635`) uses `random.getrandbits(1)` to choose player index 0.
  `alternate_order` is True for shuffled requests (`determine_is_alternating`).
- Saturn passes `-PalternateOrder` to the scaffold, which sets `-Dbc.server.alternate-order`
  (`battlecode23-scaffold/build.gradle:288`). In the bc23 engine this flips **spawn positions**, not code labels,
  on every other map: `teamsReversed = !teamsReversed` (`engine/.../server/Server.java:176-181`) feeds
  `GameMapIO.loadMap(..., teamsReversed)`. The winner line still prints `<teamA package> (A)` for team A's code
  (`Server.java:584-605`), so saturn's A/B tally follows the code, not the position.
- **All three maps are always played.** The engine stops early only if `bc.game.best-of-three` is true and there are
  3 maps (`Main.java:72`). The scaffold's `run` task never sets it, and `Config.java` has no default for it
  (**inference**: it reads as false).
- **Seeds:** neither saturn nor the scaffold overrides the seed, so every game uses the map file's seed. The same
  two submissions on the same map and side replay identically. Our own `tools/elolib.py` docstring confirms the
  engine behaviour: "the engine replays the same pairing identically unless the seed differs (2026-09-24: 491 of
  2825 ladder games were exact repeats of an earlier game)".
- Saturn's official runs set `-PoutputVerbose=false` and `-PshowIndicators=false` (`java.go:174-203`), and
  `validateMaps=true` from `gradle.properties:13`.

### 2.4 Autoscrim matchmaking
`TeamQuerySet.autoscrim` is at `teams/managers.py:163-253`, and `generate_4regular_graph` at lines 11-90.
- Only REGULAR teams with an accepted submission take part. They are sorted by `-profile__rating__mean`: "We
  intentionally use the rating mean and not the penalized rating value, to maximize the information-gain for any new
  teams with extremely low penalized scores. We like high entropy!"
- With 4 teams or fewer it plays a full round-robin. Otherwise it builds a 4-regular graph whose edges join teams at
  most 4 rank places apart. Every node except the first and last has neighbours both above and below it
  (docstring). Tests check exactly 4 participations per team, `|u−v| ≤ 4`, and 3 maps per match
  (`teams/tests.py:21-110`).
- Edge direction is randomized to set player order. Edge order is shuffled "so that match queue priority is not
  biased". Each match draws its own `random.sample(maps, best_of)`, with `alternate_order=True` and `is_ranked=True`.
- Scheduling: `Episode.autoscrim_schedule` is a cron string pushed to Cloud Scheduler (`episodes/signals.py:15-84`),
  always best of 3 ("Autoscrims are always best of 3. Future devs are welcome to change this"). The operations doc
  gives "To do every 4 hours, specify as `0 */4 * * *`." and also says "Take this with a grain of salt, this might
  be wrong."
- Size of the effect: each round gives every team exactly 4 ranked matches (12 games). With 10 teams that is
  20 matches.

### 2.5 Job protocol: idempotent, capped retries, safe to preempt
- Statuses (`compete/models.py:38-62`): `NEW, QUE, RUN, TRY, OK!, ERR, CAN`. Saturn first reports `RUN`, then
  `OK!`, or `TRY` on errors and interruptions (`saturn/pkg/saturn/task.go:40-72, 88-124`).
- Siarnaq's `SaturnInvocationSerializer.update` (`compete/serializers.py:35-69`):
  - It refuses with **409** once the invocation is finalized (`AlreadyFinalized`).
  - It adds 1 to `num_failures` on `TRY` unless `interrupted`.
  - At `SATURN_MAX_FAILURES = 5` (`settings.py:344`) it forces `ERR`.
- Saturn turns a 409 into `TaskAborted` and acks the message (`report.go:80-82`). Duplicate deliveries of a
  finished job are therefore dropped.
- Each subscriber loop pulls one message at a time: `Synchronous = true`, `MaxOutstandingMessages = 1`
  (`saturn/pkg/saturn/queue.go:30-31`). It nacks on failure, so Pub/Sub redelivers.
- Workers run on **preemptible** VMs (`deploy/saturn/main.tf:120`). The shutdown script `nc localhost 8005` hits
  the monitor port, which cancels the context, and the task is reported as interrupted (`monitor.go`, `task.go:142-145`).

### 2.6 Kill switches and local modes
- Siarnaq: when `GCLOUD_ENABLE_ACTIONS = False` (the `Local` config, `settings.py:371`), `get_publish_client()`
  returns `NullPublisher` (`gcloud/saturn.py:10-26`), `get_task_client()` returns `NullClient`
  (`gcloud/tasks.py:8-19`), Titan and avatars are skipped, and the Scheduler sync returns early.
  `EMAIL_ENABLED = False` silences email.
- Saturn: `-onsaturn=false` reads the secret from a local JSON file, reads and writes local paths instead of GCS,
  and writes the report to a file path instead of POSTing it (`secret.go:18-31`, `gcs.go:20-22, 31-44, 61-78`,
  `report.go:86-90`).
- The pattern is good. It is not complete, though. Section 6.2 lists the paths it misses.

### 2.7 Production sizing (for scale reference)
From `deploy/galaxy/main.tf:191-250` and `deploy/main.tf:52-54`:
- Execute pool: `t2d-standard-16`, `parallelism = 12` matches per machine, up to 10 machines, autoscaled on
  `num_undelivered_messages` with `load_ratio = 50`.
- Compile pool: `t2d-standard-2`, `parallelism = 1`, up to 5 machines.
- **12 concurrent matches per 16 vCPU (0.75 per vCPU)** is the only official concurrency figure.
- Cloud Tasks rating queue: `max_concurrent_dispatches = 3`, `max_dispatches_per_second = 10`
  (`deploy/siarnaq/main.tf:231-239`).

### 2.8 Visibility rules useful for a reference opponent
`MatchSerializer.to_representation` (`compete/serializers.py:268-317`):
- Matches against STAFF teams have replay and scores redacted for other viewers.
- INVISIBLE teams' matches are hidden entirely.
- Staff teams are never rated (`TeamStatus` docstring: "Staff teams do not have ratings").

The operations doc uses this for the class "Reference Player" (staff, unranked requests on a fixed map set, checked
by a `ClassRequirement`). In the replica, a frozen baseline bot can play the same role.

---

## 3. What did not work, and directions galaxy closed

All of these come from galaxy's own code, migrations and docs.

1. **Pub/Sub message ordering is off.** The siarnaq publisher sets `enable_message_ordering=True` with ordering keys
   `compile-order` and `execute-order`. The subscription has
   `enable_message_ordering = false  # Counterintuitive! See issue 514` (`deploy/saturn/main.tf:50`). FIFO is
   therefore not guaranteed. This does not matter for ratings, which are ordered by creation (section 2.2).
2. **Ranked auto-accept was switched off mid-bc23.** In migration `teams/0005` (dated 2023-01-22),
   `auto_accept_ranked` changed from `default=True` (initial migration) to `default=False`, and `RunPython` set it
   to False for **every** team. The code does not give a reason. In 2025 the boolean became a three-way
   `auto_accept_reject_{ranked,unranked}` with default `M` (manual) (`teams/0008`, 2025-01-23).
3. **Rate limits were added later.** `is_allowed_ranked_scrimmage` dates from 2025-01-13, and
   `ranked/unranked_scrimmage_hourly_limit` (default 10) from 2025-01-23 (`episodes/0010, 0011`). In January 2023
   these limits did not exist in this form. Whatever existed then is not visible in a shallow clone.
4. **Local mode silently disables ratings and storage.**
   - With `NullClient`, `request_rating_update` does nothing, so **ratings never finalize in `Local`**.
   - With actions off, `SubmissionViewSet.create` does not save the uploaded source anywhere
     (`compete/views.py:172-186`).
   - A copy run "as is" would accept submissions and matches and leave every rating at 0. This is the top trap
     for option A (section 6.3).
5. **The archived-episode guard is broken.** `Episode.autoscrim` logs "Refusing to autoscrim: archived." but has
   no `return`, so it goes ahead anyway (`episodes/models.py:158-160`).
6. **Tournament tooling is fragile.** "Methods are not transaction-safe! If a method call breaks in the middle of a
   run, then some state in the backend or Challonge may have been changed already"
   (`backend/docs/tournament-development.md`). Re-enqueuing a round is "_really hard_ right now ... Track in #594"
   (`bracket/challonge.py`, around line 305). Rounds need an odd number of maps: "We require an odd number of maps
   to prevent ties" (`episodes/views.py:218-220`).
7. **Infrastructure rough edges noted by the maintainers:**
   - Staging "is not https; unfortunately using HTTPS will error with unhelpful messages. See #526" (onboard.md).
   - Titan's Eventarc deadline is "[not long enough](https://github.com/battlecode/galaxy/issues/239)" and has to be
     fixed by hand (`deploy/README.md`).
   - "Mailjet's free plan ... only allows us 200 emails per day, which we can blow by during IAP" (`emails.md`).
   - `export_resumes` has `check_safety=False,  # TODO: actually check safety, see #628`
     (`user/managers.py:60`).
   - The `MatchSerializer` redaction branch has "TODO: Not sure why removing this doesn't work(shows hidden
     matches) but need to ship the PR" (`compete/serializers.py:285-286`).
8. **Saturn's local mode is not offline.** The README's quick start needs Docker, the gcloud CLI and
   `make dev-fetch-secret`. That target reads the `production-saturn` secret from project `mitbattlecode` with
   `gcloud secrets versions access` (`saturn/Makefile`, `saturn/README.md`). Every task also clones or pulls the
   scaffold from GitHub and runs `./gradlew update` (section 6.2). It cannot serve as an isolated replica runner.

---

## 4. Method lessons

### 4.1 What the official ladder measures (and what it does not)
- **Noise floor (inference, computed).** Take K = 24, best-of-3, and an evenly matched field (p = 0.5 per game,
  so Var(S) = 0.25/3 = 0.083). The slope of E is (ln 10/400)·0.25 = 0.00144 per point, so a = K·slope = 0.0345
  per match. The stationary standard deviation of μ is √(576·0.083/(1−(1−a)²)) ≈ **27 Elo points**. Two
  identical bots will usually show ratings tens of points apart. Ranking gaps under about 50 points mean nothing.
- **Memory (inference).** 1/a ≈ 29 matches, so the official rating mostly reflects a team's last ~30 ranked
  matches. A new submission takes over a team's old rating and needs about that many matches to show its own
  strength.
- **Provisional penalty.** A new team shows 0 and needs about 20 matches to come within 60 points of its mean
  (table in 2.1). Rankings sort by `value`, so new teams sit at the bottom until they have played. Autoscrim pairs
  by `mean`, so they still meet opponents of their true level.
- **Ranked challenges only go upward.** "You cannot request a ranked scrimmage against a team ranked lower than you"
  (`ScrimmageLowerRank`, `compete/views.py:84-89, 1023-1032`, comparing `value`). The top team can only move
  through autoscrims and challenges from below.
- **Repeats are not new data.** Ranked matches use map seeds, so a re-requested pairing with the same maps and sides
  is the same game. Ratings still move each time.
- **Order dependence.** Our own project found the same thing for sequential Elo. The `tools/elolib.py` docstring
  says: "The old sequential K=32 Elo ... depended on play order: 96 easy calibration games lifted 'us' from rank
  65 to rank 4". Galaxy's Elo has this property by design.

### 4.2 Gating and statistics
Use the replica to **predict and reproduce the official ladder's behaviour**: rating paths, the cost of the
penalty, how a new submission moves. Do **not** use it to accept builds. Gates should stay on the Bradley-Terry fit
(`tools/elolib.py`, with a pair cap of 200) plus SPRT (`tools/sprt.py`, p0 = 0.50, p1 = 0.58, α = β = 0.05). The
replica worker should also write **per-game** rows (map, side, winner, round, reason, seed) into
`progress/games.csv`, so each 3-game match feeds the BT fit with 3 data points.

### 4.3 Process rules that galaxy's operators wrote down
- "Tournament submission freeze times ... should be set to be slightly later than the nominal time ... 7:00:30 or
  7:01", which "enables an autoscrimmage round to run before the submission deadline, which can be helpful to
  converge seeds" (`operations.md`).
- First fix for failed runs: "select ... 'Force requeue'. This approach is quick and requires no code change, so
  it's always an easy place to start."
- "_You can only delete a suffix of matches_". The rating linked list (`on_delete=RESTRICT` on
  `previous_participation`) is what forces this.
- "**NB! Teh Dev team will always run examplefuncsplayer, and never change**". This is a fixed calibration
  anchor. The replica should keep a frozen anchor team the same way (examplefuncsplayer plus one frozen build of
  ours).
- Backend style rule: "you are likely able to avoid loops ... You are very likely looking for a Signal"
  (`backend/README.md`). This is why rating updates run through signals and tasks. The replica should use one
  explicit sequential loop instead, which is simpler and has no races.

### 4.4 Human interventions visible in the record
The only mid-season intervention the code shows is the 2023-01-22 forced switch-off of ranked auto-accept
(section 3, item 2). The cause is not recorded.

### 4.5 How an agent went wrong
Not applicable. Galaxy is a human-maintained codebase with no agent logs.

---

## 5. Bot architecture and the basics: what the judge does to a bot

Galaxy has no bot code. These are the judge-side facts a 2023 bot (and our replica) has to respect:

| Judge behaviour | Evidence | What it means for 2023 |
|---|---|---|
| Source zip ≤ **5 MiB**, unzipped into the scaffold `src/`; zip-slip and malformed zips → `accepted=false` | `compete/serializers.py:100-102`; `saturn/pkg/run/file.go:37-54` | the package directory goes at the zip root |
| Built with the scaffold's Gradle (Java `sourceCompatibility = 1.8`, output to `build/classes`), then `battlecode.instrumenter.Verifier <package> <classes>`; non-zero exit → rejected | `build.gradle:6-15, 244-256`; `java.go:132-160`; `Verifier.java:22-28` | the replica uses `javac -source 8 -target 8` + Verifier with the 3.0.15 jar |
| An empty package name is rejected | `java.go:136-142` | the `package` field is required |
| Binary = zip of `build/classes` (every compiled package) | `java.go:109-117` | several packages per submission are fine; the engine loads only `package` |
| Ranked runs: `outputVerbose=false`, `showIndicators=false`, `validateMaps=true`, no seed override | `java.go:178-195`, `gradle.properties:13` | prints and indicators cost nothing in ranked; results are deterministic per map and side |
| All 3 maps played; sides flip each map under alternate order | section 2.3 | bots must handle both spawn sides on every symmetry (rotation and reflection) |
| Winner = count of `(A) wins` / `(B) wins` lines | `java.go:16, 206-235` | the replica parses the same lines our `parse_result` already reads |
| No per-game wall-clock timeout in saturn | `scaffold.go:150-160` (only `ctx`) | the engine's 2000-round cap ends games; our runner keeps `timeout 1800` and reports `TRY` on timeout |
| Map pool = `is_public` maps in the DB, growing as maps are released | `serializers.py:433-446` | the replica decides its pool: all 103 maps in the jar (`tools/maps.txt`) or a dated subset |

Engine detail (**inference** from `Server.java:457` and `Config.java:71`): the scaffold passes
`-Dbc.server.map-path=maps`, but the engine reads `bc.game.map-path`. Maps resolve from `./maps`, or else from the
fat jar's built-in maps (`GameMapIO.java:142-146`).

---

## 6. Tools and infrastructure

### 6.1 Inventory and reuse verdicts

| Component (path) | Purpose | Quality | Verdict for 2023 | What must change |
|---|---|---|---|---|
| `backend/siarnaq/api/teams/models.py` `Rating` | penalized Elo | small, clear, tested | **steal as is** (port about 25 lines) | none; keep the constants |
| `compete/models.py:454-542` `try_rating_update` + linked list | creation-ordered finalization | correct, subtle | **steal the logic**, replace Cloud Tasks with a loop | remove the `request_rating_update` HTTP and Task hop |
| `teams/managers.py:11-90, 163-253` `generate_4regular_graph`, `autoscrim` | matchmaking | tested | **steal as is** | ORM → SQL |
| `compete/serializers.py:400-465`, `compete/views.py:942-1041` | ranked request rules (3 random maps, shuffled order, no staff, upward only, ≤3 active per pair, hourly cap) | fine; hourly cap double-counts (section 7) | **adapt** behind flags | default off for agent scripting; on for "official emulation" |
| `compete/serializers.py:35-69, 320-343` | report protocol (RUN/OK!/TRY/ERR, 409, 5 failures) | robust | **steal the semantics** | the worker calls functions directly |
| `compete/views.py` list/history endpoints (`scrimmage`, `historical_rating`, `scrimmaging_record`), `/api/team/<ep>/t/?ordering=-rating` | the scriptable API shape | good | **adapt** (mirror the paths and JSON) | no JWT; bind to localhost; larger page size |
| Rest of siarnaq (users, email, avatars, resumes, eligibility, tournaments/Challonge, admin) | the competitor portal | production grade | **skip** | not needed; each is an external-call risk |
| `saturn/` Go worker | Pub/Sub → Gradle → GCS → POST report | solid, but tied to GCP, GitHub and Gradle | **skip the binary, port the protocol** | bare-java runner on the 3.0.15 jar; local files; direct DB report |
| `saturn/development/*`, `Makefile` | Docker + Pub/Sub emulator dev setup | convenient for them | **skip** | no Docker or Go on the VM; it fetches a production secret |
| `titan/` | ClamAV scan of uploads | fine | **skip** | no untrusted uploads |
| `deploy/**` Terraform | GCP production infrastructure | — | **skip; never run** | it would target `mitbattlecode` (section 6.2) |
| `frontend/` | React portal | large (14 kLOC excluding generated code) | **skip** (optional later) | the production `.env` points at `api.battlecode.org` |
| `docs-general/operations.md` | runbook | useful | **read-only reference** | — |
| Ours: `tools/lib.sh` `run_game`, `parse_result`, `compile_src` | bare-java game and compile | in use | **steal as is** in the runner | add `-Dbc.server.alternate-order`, multi-map, `-Dbc.server.websocket=false` |
| Ours: `tools/elolib.py`, `tools/sprt.py` | BT ladder, SPRT gate | in use | **keep as the gate** | the replica exports per-game rows |
| Ours: `tools/throughput.sh` | concurrency measurement | in use | **use** to set replica parallelism | — |
| Ours: `tools/vm.sh`, `tools/vm-run.sh` | sync and detached runs on battlecode-dev | in use; `vm.sh` already names the VM as host of "the private galaxy replica" | **use** to deploy the replica | — |

### 6.2 Every code path that contacts an external service, and how to neutralize it

"Guarded" means the code skips the call when `GCLOUD_ENABLE_ACTIONS` or `EMAIL_ENABLED` is False.
**UNGUARDED** means it makes the call in any configuration.

| # | Where | Service and target | Guard | How to disable or stub |
|---|---|---|---|---|
| 1 | `settings.py:20-37, 473-509, 568-595` (`Staging`/`Production.pre_setup`) | `google.auth.default()`, impersonation of `*-siarnaq-agent@mitbattlecode`, **Secret Manager** `staging-siarnaq`/`production-siarnaq`; Staging connects to Postgres at `db.staging.battlecode.org:5432` | only those configs | never set `DJANGO_CONFIGURATION=Staging/Production` (`manage.py` defaults to `Local`); option B avoids Django entirely |
| 2 | `settings.py:465-471, 560-566` | **GCS** static files `mitbattlecode-*-public` via `collectstatic` | only those configs | as above |
| 3 | `gcloud/saturn.py:23-36`, used by `compete/managers.py:38-83` | **Pub/Sub** publish to `us-east1-pubsub.googleapis.com:443`, topics `*-siarnaq-compile`/`execute` | guarded (`NullPublisher`) | replace with a local queue (DB status `QUE` polled by the worker) |
| 4 | `gcloud/tasks.py:16-21`, used by `compete/models.py:299-328` (ratings) and `episodes/models.py:453-482` (bracket) | **Cloud Tasks** queues `*-siarnaq-rating`, `*-siarnaq-bracket` | guarded (`NullClient`), **which means ratings never update** | run `try_rating_update` from a local sequential loop |
| 5 | `episodes/signals.py:15-84` | **Cloud Scheduler** job `<prefix>-autoscrim-<episode>` | guarded | cron or systemd timer on the VM calling the local autoscrim |
| 6 | `compete/views.py:172-186` | **GCS** write of submission source to `GCLOUD_BUCKET_SECURE` | guarded (upload skipped, **source lost**) | write to a local path |
| 7 | `gcloud/titan.py:22-104` via `compete/views.py:227-237`, `user/views.py:172-180`, `teams/views.py:298-306` | **GCS** read and signed URLs (impersonated credentials) | guarded (returns `url: ""`) | local file path |
| 8 | `user/views.py:182-203`; `gcloud/titan.py:13-19, 107-123` | **GCS** resume and avatar upload, Titan metadata | guarded | drop the endpoints |
| 9 | `teams/views.py:308-325` (`ClassRequirementViewSet.report` PUT) | **GCS** `storage.Client(...)` write + `titan.request_scan` | **UNGUARDED** | remove. On a GCP VM, Application Default Credentials come from the metadata server, so this would try a real write to bucket `nowhere-secure` |
| 10 | `user/managers.py:41-83` (admin action `episodes/admin.py:27-29`) | **GCS** write to `GCLOUD_BUCKET_EPHEMERAL` with `predefined_acl="publicRead"` | **UNGUARDED** | remove the admin action |
| 11 | `compete/models.py:256-263`, `teams/models.py:258-272`, `user/models.py:129-143` | builds `https://storage.googleapis.com/<bucket>/...` URLs (anonymous client; **inference**: no call at build time) | n/a | return local URLs |
| 12 | `user/authentication.py:14-87` (first entry in `DEFAULT_AUTHENTICATION_CLASSES`, `settings.py:178-181`) | **Google OAuth2 ID-token check** (`id_token.verify_oauth2_token` fetches Google certificates) when the User-Agent is `Google-Cloud-Scheduler`, `Google-Cloud-Tasks` or `Galaxy-Saturn` and a Bearer header is present | none | remove the class |
| 13 | `user/signals.py:15-86`, `EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"` (`settings.py:348`) | **Mailjet** (password reset, email verification) | guarded by `EMAIL_ENABLED` | also set `EMAIL_BACKEND` to the locmem or console backend |
| 14 | `bracket/challonge.py` (`URL_BASE = "https://api.challonge.com/v2.1/"`, `requests` calls at lines 73, 120, 136, 149, 434), reached from `Tournament.initialize`, `TournamentRound.enqueue`, the `pre_save` `report_to_bracket` signal (`compete/signals.py:71-89`), `publish_public_bracket` | **Challonge** | **UNGUARDED** (fails only because the key is `""`) | no tournaments; stub the module to raise |
| 15 | `episodes/admin.py:223-231`; frontend `api/helpers.ts:146-155`, `views/Resources.tsx:33-39` | links to `releases.battlecode.org` (client, specs, javadoc; bc22 and bc23 use `visualizer.html?<gameSource>`) | n/a (links only) | omit; open replays in a local client |
| 16 | `frontend/.env.production` (`VITE_BACKEND_URL=https://api.battlecode.org`) | a production frontend build talks to the **official API** | n/a | skip the frontend. If ever used, build only with a local `.env` |
| 17 | `saturn/pkg/saturn/secret.go:32-50` | **Secret Manager** (`onsaturn=true`) | flag | not used (no saturn) |
| 18 | `saturn/pkg/saturn/queue.go:23-58` | **Pub/Sub** subscriber (honours `PUBSUB_EMULATOR_HOST`) | none | not used |
| 19 | `saturn/pkg/saturn/report.go:25-38, 60-85` | **Google ID token** client + POST to `report-url` (`https://<ALLOWED_HOSTS[0]>/...`, i.e. `api.battlecode.org` in production) | `onsaturn` | not used; the worker reports locally |
| 20 | `saturn/pkg/run/gcs.go:19-97` | **GCS** binaries and replays (`publicRead` for replays) | `onsaturn` | not used |
| 21 | `saturn/pkg/run/scaffold.go:162-195` | **GitHub** clone and pull of `episode.scaffold` with a token, on **every task** | none (even `onsaturn=false`) | not used; pinned local jar |
| 22 | `saturn/pkg/run/java.go:50-78` → scaffold `build.gradle:65-82, 108-125, 132-150` | `./gradlew update` → GET `https://api.battlecode.org/api/episode/e/bc23/?format=json`; Maven `gcs://mitbattlecode-releases/maven` (on saturn) or `https://releases.battlecode.org/maven`; `mavenCentral`; Gradle wrapper download | none | not used. Never run the scaffold's `update`, `run` or `verify` on the replica |
| 23 | `saturn/Makefile` `dev-fetch-secret`; `saturn/development/Dockerfile` | gcloud **Secret Manager** (`production-saturn`, project `mitbattlecode`); apt from `packages.cloud.google.com` | none | never run |
| 24 | `titan/**` | **GCS** + Eventarc; ClamAV signature updates (**inference**: the image refreshes signatures over the network) | none | skip |
| 25 | `deploy/provider.tf`, `state.tf`, `main.tf` | Terraform impersonates `terraform@mitbattlecode.iam.gserviceaccount.com`; state in `gs://mitbattlecode-terraform-state`; DNS zone `battlecode-dns-zone`; Cloud Build triggers on `battlecode/galaxy` tags | none | never run `terraform` in this tree |
| 26 | `.github/workflows/ci.yml`, `.pre-commit-config.yaml` | GitHub Actions; hooks fetched from GitHub | n/a | never run locally |
| 27 | Engine `Config.java:33` (`bc.server.websocket=true`), `NetServer.java:39` (`new InetSocketAddress(port)`) | **inbound** websocket listener on `0.0.0.0:6175` for every game | none | pass `-Dbc.server.websocket=false` (our `lib.sh` and `gauntlet.sh` do not set it today) |
| 28 | Ours: `tools/get-engine.sh` | one GET of the jar from `releases.battlecode.org` (checksum-pinned) and a GitHub clone for the patch source | — | already staged; do not re-run in loops |

Not present anywhere in galaxy: **Sentry**, **SendGrid** (Mailjet is used instead), **Mailchimp**, and **Google
OAuth for user login** (users log in with username and password → `/api/token/` JWT). The only Google OAuth use is
row 12.

**Extra guards for the replica (whichever option is chosen):**
1. Run the API and worker as a dedicated Unix user `bcreplica` with no gcloud configuration, no
   `GOOGLE_APPLICATION_CREDENTIALS` and no GitHub token.
2. Add an nftables egress block for that uid: `meta skuid bcreplica oifname != "lo" drop`, plus an explicit drop to
   `169.254.169.254`. Blocking the metadata server means no client library can obtain the VM's service-account
   token.
3. Bind HTTP to `127.0.0.1` only. Reach it from the driver with `ssh -L`.
4. Add a unit test that fails if the replica source contains `battlecode.org`, `googleapis`, `challonge`,
   `mailjet` or `github.com`.
5. Run the engine with `-Dbc.server.websocket=false`.
6. Remember that the VM's own service account belongs to `tvanbelle-vibecode` and has no rights in `mitbattlecode`.
   An accidental authenticated call would be refused. That is a last line of defence, not a design.

### 6.3 Options compared

| | **A. Real siarnaq (Django 4.1.2) + local Postgres or SQLite + DB-as-queue + our runner** | **B. "galaxy-lite": stdlib re-implementation of the same data model and rating code + our runner** |
|---|---|---|
| Rating exactness | exact by construction, **if** the Cloud Tasks hop is replaced (otherwise ratings never update) | exact if ported line for line; checked by porting galaxy's 9 finalization tests plus a hand-computed table |
| Features | everything: admin UI, users, request inbox and outbox, history endpoints, Swagger | only what we need: teams, submissions, requests (ranked and unranked), autoscrim, history, ratings, per-game export |
| External-call risk | high surface. `google-cloud-{pubsub,storage,tasks,scheduler,secret-manager}`, `anymail`, `requests` and `google.auth` are installed and imported. Two **unguarded** GCS paths and an unguarded Challonge path need patches; about 10 patch sites in total (6.2 rows 3-14) | near zero: none of those libraries is installed |
| Dependencies | Python **3.10**-era pins (`environment.yml`: `python=3.10`, `pillow=9.0.1`, `psycopg2=2.9.3`, google-cloud 2022 versions). Debian 12 ships Python 3.11, so expect build or pin friction (**inference**). Postgres install is optional | none beyond Debian 12's Python 3.11 stdlib (`sqlite3`, `http.server`, `zipfile`, `subprocess`), JDK 8, the engine jar |
| SQLite fit | mostly. `SubmissionQuerySet.for_tournaments` uses `.distinct(fields)`, which is Postgres-only (the view catches `NotSupportedError` → 501); `select_for_update` is a no-op. bulk_create PK return needs SQLite ≥ 3.35 (**inference**: Debian 12 has 3.40) | designed for SQLite (WAL, a single writer process) |
| Code to write | settings class, ~10 patches, worker as a management command | ~700-1,000 lines: schema, rating, matchmaking, rules, worker, API/CLI, tests |
| Effort (**inference**) | 2.5-3 agent-days, plus ongoing risk of missing a path on upgrades | 1.5 agent-days |
| Resources | Postgres (~200 MB disk, ~0.3 GB RAM), venv ~0.5 GB | <5 MB code, SQLite in the tens of MB |
| Later frontend | possible (Node 20, ~1 GB `node_modules`) | none (CLI + JSON), which suits an agent-driven project |

**Recommendation: B.** Every behaviour we need (ratings, ordering, matchmaking, request rules, report semantics)
is small, pure logic that can be copied. Everything that makes A expensive (auth, email, storage, Scheduler, Tasks,
Challonge, Titan) is exactly what we must switch off. A smaller surface is also easier to show safe.

### 6.4 Recommended design (galaxy-lite)

**Layout:** `tools/replica/` in our repo, synced to the VM by `tools/vm.sh`. Data lives in `~/replica/` on the
VM: `replica.db`, `sub/<id>/{source.zip,binary/,compile.log}`, `replay/<uuid>.bc23`, `logs/`.

**Schema** (SQLite; galaxy's names and enums kept so the code ports one to one):
- `episode(name_short, autoscrim_best_of=3, ranked_hourly_limit, unranked_hourly_limit, enforce_rules)`
- `map(id, episode, name, is_public)`, seeded from `tools/maps.txt` (103 names)
- `team(id, name, status R|X|S|O, rating_id)`. Use **one team per build** (`us:g_iter7`) and one per benchmark
  bot, so each rating belongs to one fixed bot. A "team mode" can instead have one team receive successive
  submissions, to rehearse what the official ladder does to a new upload.
- `rating(id, mean=1500, n=0, value)`, immutable rows, `value = mean − 1500·0.85^n`
- `submission(id, team, status, num_failures, logs, accepted, package, created, source_path, binary_path)`.
  Add `prebuilt_classes` so benchmark class dirs from `tools/bench-compile.sh` can be registered without
  recompiling.
- `match(id, status, num_failures, logs, is_ranked, alternate_order, replay_uuid, created, source:
  'request'|'autoscrim'|'manual')`, `match_map(match, map, sort)`
- `match_participant(id, match, team, submission, player_index, score, rating_id NULL, previous_participation)`
- `scrimmage_request(id, created, status P|Y|N, is_ranked, requested_by, requested_to, player_order + | - | ?)` +
  `request_map`
- extension `game(match, idx, map, team_a_code, reversed, winner A|B, round, reason)`, filled from the engine log

**Rating pump** (replaces Cloud Tasks): after every report, loop
`SELECT participants WHERE rating_id IS NULL ORDER BY id` and apply galaxy's `try_rating_update` rule. Repeat until
a pass finalizes nothing. Treat `scores == [0,0]` or `sum(scores) != #maps` on an `OK!` as an **error** (`TRY`)
instead of letting it divide by zero (section 7, item 5).

**Matchmaking:** `autoscrim()` and `generate_4regular_graph()` copied verbatim. Ranked request rules follow
`compete/views.py:942-1041` and `compete/serializers.py:400-465` when `enforce_rules=1`.

**Worker** (replaces saturn): N parallel slots, each a loop:
1. Claim a job atomically: `UPDATE match SET status='RUN' WHERE id=? AND status IN ('QUE','TRY')`.
2. **Compile:** unzip with saturn's zip-slip check; reject an empty package; run
   `javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none` against the engine jar (our `compile_src`);
   then `java -cp <jar> battlecode.instrumenter.Verifier <pkg> <classes>`. Exit 0 → `accepted=1`. Status is `OK!`
   either way. Infrastructure errors → `TRY`.
3. **Execute:** a **single engine invocation** with every map, as saturn does:
   ```
   timeout $GAME_TIMEOUT java -Xmx768m -XX:+UseSerialGC -Dbc.server.mode=headless -Dbc.server.websocket=false \
     -Dbc.server.robot-player-to-system-out=false -Dbc.server.debug=false -Dbc.engine.debug-methods=false \
     -Dbc.engine.enable-profiler=false -Dbc.engine.show-indicators=false -Dbc.server.validate-maps=true \
     -Dbc.game.team-a=<name0> -Dbc.game.team-b=<name1> -Dbc.game.team-a.url=<bin0> -Dbc.game.team-b.url=<bin1> \
     -Dbc.game.team-a.package=<pkg0> -Dbc.game.team-b.package=<pkg1> -Dbc.game.maps=m1,m2,m3 \
     -Dbc.server.alternate-order=<alternate_order> -Dbc.server.save-file=<replay> \
     -cp <engine_cp> battlecode.server.Main -c=-
   ```
   The `engine_cp` from `lib.sh` puts the seed patch first, but without `-Dbc.game.seed` that patch behaves exactly
   like the official engine. Count winners with saturn's regex (`java.go:16`) and also store each map's
   `round`/`Reason`. Game *i* has spawn sides reversed when `alternate_order` is set and *i* is odd (0-based). This
   is also why the faithful runner keeps one invocation per match: splitting maps into separate runs with A/B
   swapped is close but **not proven** bit-identical (team labels change).
4. **Report** through the same state machine as `SaturnInvocationSerializer`: 409-equivalent no-op if finalized,
   `num_failures++` on non-interrupted `TRY`, `ERR` at 5. Then run the rating pump.

**API** (mirrors galaxy paths and JSON for familiarity; no auth; 127.0.0.1 only), plus a CLI `tools/replica.py`:
- `POST /api/compete/bc23/submission/` `{team, package, source_zip | prebuilt_classes}`
- `POST /api/compete/bc23/request/` `{requested_by, requested_to, is_ranked, player_order, map_names}`. Auto-accept
  is on by default for local teams. Galaxy's default is manual, but no human is answering requests here.
- `POST /api/episode/e/bc23/autoscrim/` `{best_of: 3}`
- `GET /api/team/bc23/t/?ordering=-rating` returns `value`, `mean`, `n` and the record
- `GET /api/compete/bc23/match/?team_id=&page=` and `GET .../match/<id>/` (with per-game rows),
  `GET .../match/historical_rating/?team_id=`, `GET .../match/scrimmaging_record/?team_id=`
- `POST /replica/export-games` → append rows to `progress/games.csv` (run = `replica-<match>`; the
  `seed` column = `map`)

**Scheduling:** a cron or systemd user timer runs `tools/replica.py autoscrim` every 4 h (galaxy's documented
example), or the agent triggers it on demand.

### 6.5 Step-by-step build plan
1. **Lockdown first (0.5 h).** Create user `bcreplica`; add the nftables egress drop for that uid (loopback only,
   metadata server blocked); create `~/replica`. Check that `curl https://example.com` as `bcreplica` fails.
2. **Core port + tests (4-6 h).**
   - Port `Rating` and `try_rating_update` into `rating.py`.
   - Port the 9 cases of `MatchParticipantRatingFinalizationTestCase` into `test_replica.py`.
   - Add the hand-computed delta and penalty tables from section 2.1. For example: equal means, 3-0 → +12.0;
     2-1 → +4.0; n=10 penalty 295.3.
   - Port `generate_4regular_graph` and its property tests (`teams/tests.py:21-52`: degree 4, `|u−v| ≤ 4`,
     neighbours on both sides).
3. **Schema + rules (2 h).** SQLite DDL; request validation (flags); autoscrim; map seeding from `tools/maps.txt`.
4. **Worker (3-4 h).** Compile and execute as in 6.4 by reusing `tools/lib.sh` (`engine_cp`, `compile_src`).
   Use a captured engine log as a fixture for the winner regex and the per-game parser. Treat timeout and
   zero-score outcomes as `TRY`.
5. **API + CLI (2-3 h).** `http.server` JSON handlers bound to 127.0.0.1; `tools/replica.py` subcommands `submit`,
   `request`, `autoscrim`, `ratings`, `history`, `wait`, `export-games`.
6. **Guard test (0.5 h).** Grep for forbidden hostnames; assert the `-Dbc.server.websocket=false` flag is present.
7. **Measure concurrency (1 h).** Run `tools/throughput.sh <a> <b> <map> "2 4 6 8"` on the VM. Pick the number of
   replica slots so that replica plus gauntlet jobs stay at or below the measured knee. Galaxy's reference is 0.75
   matches per vCPU, which would be 6 on 8 vCPU if the VM were otherwise idle.
8. **End-to-end check (2 h).**
   - Register examplefuncsplayer + 5 builds or benchmarks; run 2 autoscrim rounds (12 matches each with 6 teams).
   - Check that every team has 4 participations per round and that ratings finalize in creation order even when
     completions are reordered (kill and requeue one match).
   - Check that the BT export appends 3 rows per match.
9. **Service (0.5 h).** systemd user units `replica-api` and `replica-worker`, plus the autoscrim timer. Logs to
   `~/replica/logs`. A replay retention job keeps losses and the last N matches and gzips the rest.

### 6.6 Effort and resources
- **Effort (inference): about 1.5 agent-days for B.** A would take 2.5-3 days.
- **CPU:** the replica shares battlecode-dev (8 vCPU) with the gauntlet. Plan 4-6 concurrent matches, measured.
  One match is 3 games in sequence inside one JVM.
- **RAM:** about 1 GB per game JVM (`-Xmx768m` plus overhead) → ≤ 6 GB of 31 GB.
- **Disk (20 GB, shared):**
  - Code < 5 MB; DB tens of MB.
  - Replays: our only size sample is `2023/matches/test1.bc23` at 821,251 B. Assume about 1-3 MB per 3-game match
    (**inference**), so 1,000 matches ≈ 1-3 GB.
  - Budget ≤ 3 GB with retention (step 9).
  - Galaxy ran with indicators off. Do the same in ranked emulation so replays stay small.
- **Software:** nothing new. Python 3.11 stdlib, `~/jdk/jdk8u504-b01`, `engine/battlecode23-3.0.15.jar`
  (sha256-pinned in `lib.sh`). No Docker, Go, Postgres or Node.

### 6.7 What must change for 2023
- **Engine:** 3.0.15 fat jar. Its 103 built-in maps load from the jar when `./maps` does not have them. It must
  run without Gradle; the scaffold's `update` would query `api.battlecode.org`.
- **Replay:** `.bc23`, one file per match holding all 3 games. Check that `tools/replaydump` handles multi-game
  files before relying on it.
- **Java 8:** `javac -source 8 -target 8` and the engine's `Verifier`; the JDK is already on the VM.
- **VM layout:** run the replica on battlecode-dev (`tools/vm.sh` already reserves this role). The driver
  (e2-small) only issues CLI calls over SSH.

---

## 7. Pitfalls and gotchas

No costs in time are recorded in galaxy. The risks are stated as found.

1. **Silent no-op ratings in siarnaq `Local`** (`gcloud/tasks.py:16-19` → `NullClient`). Every rating stays 0.
2. **Silent loss of uploaded source in `Local`** (`compete/views.py:172-186`). Compiles have nothing to build.
3. **Unguarded GCS writes** (`teams/views.py:308-325`, `user/managers.py:73-83`). On a GCP VM, Application Default
   Credentials come from the metadata server, so these become real authenticated calls. The second sets
   `publicRead`.
4. **`GoogleCloudAuthentication` runs first** and contacts Google whenever a request carries an internal User-Agent
   and a Bearer header.
5. **Divide by zero in ratings (inference).** Saturn reports `scores [0,0]` with status `OK!` if no winner lines
   match (`java.go:216-232`). `total_score` is then 0 in `compete/models.py:514-517`. In galaxy that task fails
   and the team's rating chain is blocked behind it.
6. **One stuck match blocks a team's rating chain.** It also blocks every opponent whose next match waits on that
   team. Galaxy releases it only through `ERR` after 5 failures, cancellation, or an admin requeue. In the replica,
   add a `stale RUN` reaper (for example, after 2 × GAME_TIMEOUT).
7. **Double counting in the hourly limit (inference).** `existing_requests_from_requestor` counts all requests in
   the past hour, including accepted ones, and `match_count` also counts the matches they created. Autoscrim
   matches count against the *ranked* cap (`compete/views.py:960-985`). The effective ranked request budget is
   about half the configured limit.
8. **Upward-only ranked challenges**, compared on `value` (penalized). A veteran cannot request ranked games
   against a new team. New teams (value near 0) can challenge anyone.
9. **Repeated pairings are identical games** (map seeds), yet still move ratings. For information, the replica can
   offer a non-faithful mode with `-Dbc.game.seed` (our LiveMap patch). Label it as such.
10. **Map pool drift:** the official public pool grew over the season. The jar has all 103 maps. Decide and record
    which pool a replica run uses.
11. **The scaffold's `map-path` flag is a no-op** (**inference**): it passes `bc.server.map-path`, but the engine
    reads `bc.game.map-path`. It works only because of the jar fallback.
12. **Websocket listener on `0.0.0.0:6175` in every game** (`Config.java:33`, `NetServer.java:39`). Parallel games
    contend for the port. Pass `-Dbc.server.websocket=false`, in our gauntlet too.
13. **Saturn's own local mode still needs** GitHub with a token, `api.battlecode.org` (Gradle `update` on every
    task), `releases.battlecode.org` Maven, Docker and a production secret. Do not try to "just run saturn locally".
14. **Python pins:** siarnaq expects Python 3.10 (`environment.yml`) with 2022 library pins. Debian 12 ships 3.11.
    This is one more reason for option B.
15. **API ergonomics if real siarnaq is ever used:** `PAGE_SIZE: 10` with no `page_size` parameter, throttle
    `400/min`, JWT lifetime 5 days (`settings.py:177-195`), `IsEmailVerified` on most write endpoints, and
    `EMAIL_VERIFICATION_REQUIRED = False` only in `Base`/`Local`.
16. **Autoscrim's archived check does not stop it** (`episodes/models.py:158-160`).
17. **Team rating carries across submissions.** In galaxy a new upload inherits the team's μ, n and value. If the
    replica uses one team per build, it measures something different from the official ladder by design.
    Document the mode with every result.

---

## 8. Top 15 takeaways for the 2023 project (ranked by expected value)

1. **Build galaxy-lite (option B), not a siarnaq copy.** Stdlib Python, SQLite, our bare-java runner. It has the
   smallest external-call surface and is about 1.5 agent-days of work (inference).
2. **Copy the rating exactly:** μ' = μ + 24·(S − E), E over opponents' pre-match means on a 400 scale,
   S = game-win fraction, displayed value = μ − 1500·0.85^n, new team shows 0
   (`teams/models.py:13-58`, `settings.py:322-327`).
3. **Finalize ratings in match-creation order per team,** using both sides' ratings from just before the match.
   A fixed-point loop over pending participants reproduces galaxy without Cloud Tasks
   (`compete/models.py:454-542`). Port the 9 galaxy tests to prove it.
4. **Ranked format = 3 random public maps, shuffled order, alternating spawn sides, all 3 games played, map seeds.**
   Use a single engine run with `-Dbc.server.alternate-order=true` to match saturn exactly.
5. **Lock the replica down at the OS level:** dedicated uid, nftables loopback-only egress, metadata server
   blocked, HTTP on 127.0.0.1, no credentials, and a hostname-grep test.
6. **Never run anything in `deploy/`, `saturn/Makefile`, the frontend production build, or the scaffold's Gradle
   tasks.** Each one reaches `mitbattlecode` GCP, `api.battlecode.org`, `releases.battlecode.org` or GitHub
   (6.2 rows 16-25).
7. **Keep gating on our BT fit + SPRT.** The official ladder's steady-state noise is about ±27 points (1 SD) and
   its memory is about 30 matches (inference, section 4.1). Use the replica to predict official ladder dynamics.
8. **Export per-game rows from every replica match into `progress/games.csv`.** That is three BT data points per
   match instead of one Elo step.
9. **Autoscrim = 4-regular graph by rating *mean*, best of 3, 4 matches per team per round** (round-robin for 4
   teams or fewer). Copy `generate_4regular_graph` verbatim; schedule it every 4 h or on demand.
10. **Use one team per build** for clean measurement. Add a "team mode" with successive uploads to rehearse the
    official experience: inherited rating, a ~30-match memory, and upward-only challenges.
11. **Make error handling stricter than galaxy:** treat `[0,0]` or partial scores as `TRY`; reap stale `RUN`
    jobs; cap failures at 5 → `ERR` (unranked for ratings), as galaxy does.
12. **Pass `-Dbc.server.websocket=false`** in every engine invocation (replica and gauntlet). This removes the
    0.0.0.0:6175 listener and the port contention.
13. **Compile like the judge:** 5 MiB zip limit, zip-slip check, non-empty package, `javac -source 8 -target 8`,
    then `battlecode.instrumenter.Verifier <pkg> <classes>`. A compile failure is `OK!` with `accepted=false`, not
    a retry.
14. **Size concurrency by measurement:** galaxy ran 12 matches per 16 vCPU. Measure on battlecode-dev with
    `tools/throughput.sh`, share the VM with the gauntlet, and keep replay retention under ~3 GB of the 20 GB disk.
15. **Record the replica mode with every result:** faithful (map seeds, `enforce_rules`, team mode) or measurement
    (seeded, one team per build). Note that HEAD galaxy parameters cannot be date-verified for January 2023 from a
    shallow clone. Galaxy's own record shows rules changing mid-season (auto-accept off on 2023-01-22) and in later
    years (rate limits in 2025).
