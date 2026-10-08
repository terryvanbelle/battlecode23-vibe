# HANDOFF.md — current state (keep this current at every accept)

Updated 2026-10-07 ~15:45 PDT.

## Standing

- **Incumbent g_iter0** (code hash e6f2fc5356c6): the foundation bot. Field calibration (174 games, 2 per entrant):
  131-43 (75.3%), BT 1732 +- 66, rank 17 of 88 (`progress/ELO.md`). Beats examplefuncsplayer 206/206 on every map.
  Basics battery PASS (0 overruns, 0 exceptions, 0 near misses, symmetry never wrong, decided by r150 in 204/206).
- **Why we lose** (43 calibration losses and a 24-game block against four top bots): the opponents' carriers mine mana
  from the start (by r100: 470-866 Mn and 0-179 Ad against our 204-350 Mn and 308-440 Ad), so they field 2-6x our
  launchers by r250; our launchers fight one at a time and stay inside enemy reach (14-28% of launcher-rounds against
  their 0.3-3%), taking 9-26 damage per contact round against their 3.5-7.7; by about r150 they hold our half.

## In flight (VM queue, each paired on identical cells)

| job | candidate | change | control | state |
|---|---|---|---|---|
| cand-nav1 | c_nav1 | bug navigation keeps its hand per obstacle | c_econ1 | done: net 0, more stalls, -7% collection |
| cand-mana1 | c_mana1 | mana-first roles, adaptive at delivery | c_nav1 | done: rejected, net -7; mined MORE Ad |
| cand-mana2 | c_mana2 | 1 in 5 carriers on adamantium, overrides by HQ stock | c_nav1 | done: kept (net +5, Mn r100 +62, launchers up); working line C.ROLES = 2 |
| deliv-mana1/micro1/batch1 | c_micro1, c_batch1 | pinned-enemy micro, safe step-in; launcher batches of 3 | c_mana1, c_micro1 | queued |
| deliv-spawn1 | c_spawn1 | spawn on the tile fewest enemy fighters reach | c_batch1 | queued |
| deliv-army1 | c_army1 | launcher cohesion (`C.ARMY`): regroup, follow the lowest id | c_spawn1 | queued |
| cand-nav2 | c_nav2 | c_nav1 without the 3-turn wait for robots on the wall path | c_nav1 | queued |
| cand-audit1 | c_audit1 | the whole line since g_iter0 + audit fixes; carries c_mana1's roles | g_iter0 calibration | done: net -6 (-1.7 SE), Ad-heavy economy, 111 HQ overruns (fixed in src/bot) |

Cells: `test/cells/calib-g_iter0.txt` (174, every entrant twice) and `test/cells/diag-top4.txt` (24, four top bots).
Read with `tools/paired.py <cand run> <control run>` and `tools/delivery.py <cand run> <control run>`.

## The galaxy replica (owner, PROMPTS 11-12)

- Galaxy's own siarnaq backend (unmodified; Google Cloud replaced by local stand-ins) and galaxy's own frontend run on
  battlecode-dev at https://galaxy.136-86-167-127.sslip.io/ (gate: user owner, `~/.bc23-replica-password`; galaxy
  superuser `owner`, same password). Docs `docs/galaxy/README.md`; code `tools/galaxy/`. Nothing contacts
  battlecode.org: the stock frontend build pointed at api.battlecode.org and is overridden; CSP self only.
- Our team: **vibe23** (user vibe23, credentials `~/.bc23-galaxy-team`, mode 600), auto-accepts ranked and unranked.
  Everything goes through `tools/contest.py`: `submit <package> --wait`, `request <team> --maps a,b --order +`,
  `matches`, `fetch <id>`, `block <cells> --tag T` (a block of unranked requests, downloaded into a run directory
  for `tools/paired.py`). Hourly limits count requests AND the matches they create (an accepted request counts
  twice); galaxy's default 10/10 was raised to 40 unranked and 20 ranked (owner, PROMPTS 15-16), so about 20 panel
  requests (200 games) and 10 ranked challenges an hour; the VM is the real limit. Ranked: 3 random maps, upward only.
- Active submission: 24 = g_iter0 (2026-10-07 17:45 PDT). Baseline panel (test/cells/panel-v1.txt, 10 opponents x 10
  maps) running from the driver: `logs/panel1-g_iter0.log`, run dir `gauntlet/*-panel1-g_iter0`.
- Our ranked play: `python3 tools/contest.py ladder` runs detached on the driver (log `logs/ladder-vibe23.log`), one
  ranked challenge every 10 minutes to a team rated closest at or above us (galaxy: ranked only upward; weaker teams
  challenge us). Galaxy's autoscrim (ranked, every team) fires every 8 hours (00:00, 08:00, 16:00 UTC).
- Every replica game must count (owner, PROMPTS 13): a workflow is adding bot telemetry (indicator strings plus
  indicator dots/lines, which cost 0 bytecodes per call and are uncapped), new ReplayDump extractors (engagements,
  timelines, death causes, opponent tactics) and a per-match report for every downloaded match
  (`docs/TELEMETRY.md` when done). The next candidate is submitted only with telemetry on (c_line3 was held back).
- The field: 87 teams, one per public 2023 bot (`tools/galaxy/field.py`, mapping `tools/galaxy/field-teams.tsv`; one
  name shortened: `remember-to-hydrate.sprint_1`), each its own user (passwords only on the VM,
  `~/.bc23-galaxy-field/accounts.json`), all compiled, auto-accept on. Autoscrims: `bc23-galaxy-scheduler.timer`
  enabled 2026-10-08 01:19 UTC, every 8 h from 08:00 UTC (176 matches per round, about 4.5-5 h on 5 engines: our
  requests queue behind a round; `docs/galaxy/README.md` section 8, capacity). Field activity on the VM
  (`field.py activity`, `logs/field-activity.log`): random field teams request ranked scrimmages upward, one a
  minute while fewer than 2 matches wait. saturn has 5 engines.
- Each check-in: `python3 tools/galaxy/results.py` (finished matches into `progress/games.csv` as `galaxy-<match>`,
  our rows `us:<package>`; idempotent), `tools/.venv/bin/python tools/galaxy/snapshot.py` (`progress/ladder.{md,png}`
  from the Rankings page), `tools/elo.py`; commit them together.
- galaxy-lite (the first replica, `tools/replica/`) was retired 2026-10-08 01:01 UTC: units stopped and disabled, data
  archived under `/home/bcreplica/replica/archive/20261008-010127-retired/`, its 159 games already in `games.csv`
  (`replica-*`), its host name redirects to the galaxy site (`docs/replica/README.md`).

## Compute

- Driver `claude-driver` (2 vCPU, 2 GB): this session; one diagnostic game at a time at most.
- VM `battlecode-dev` (us-west1-b, 8 vCPU, 31 GB, 20 GB disk), internal IP 10.138.0.3. Standing queue
  (`tools/vm-enqueue.sh`, runner `tools/vm-queue.sh`); gauntlet games share 5 slots (`/tmp/bc23-game-slots`), the
  galaxy saturn has its own 5 engines. Games against top bots run 1,000-2,000 rounds and take several minutes each.
- `battlecode-dev2` (us-west2-a) belongs to the paused 2024 project: never touch it.

## Gotchas a fresh reader will hit

- The engine seeds robot ids and sandboxed randomness from the map file; our `-Dbc.game.seed` patch varies spawned
  robots only. Identical code on an identical cell replays identically, even against external bots (30/30 checked).
  The final tiebreak is an unseeded coin flip: such games are recorded as COIN and ignored.
- Runs record the code hash of the bot that played (`provenance.txt`). A package name is not provenance: one
  "identity" run compiled a src/bot that had changed under it.
- An uncaught exception destroys the robot (HQs included). Every shared-array write is re-checked at write time.
- Replays carry no robot stdout: our counters are in the indicator string (`note|ov=,ex=,nm=,sm=,sd=,wh=,bf=...`); the
  first character of the note is a state token (carriers: G C W R D F X K T).
- Some field bots fire every round at empty tiles (blind fire): count hits, not attacks.
- Debug prints need both flags: `GAME_OPTS='-Dbc.testing.debug=true'` (the bot reads it) and `SHOW_LOGS=true` (the server
  forwards robot stdout). With only the first, nothing appears; checked with a probe bot on 2026-10-07.
- `vm-run.sh` must background with `cd X; CMD &`, not `cd X && CMD &` (the latter holds ssh open until the job ends).
- Never `pkill -f` a pattern that can match the caller (it killed the issuing shell once on 2026-10-07).
