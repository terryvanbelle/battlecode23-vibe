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

## Switch to the real galaxy (owner, PROMPTS 11-12; in progress since 2026-10-07 16:10 PDT)

- The owner wants the exact look and feel of play.battlecode.org and wants us to submit bots, challenge opponents
  and download results through the replica, as in the contest; none of it may affect the real play.battlecode.org.
- Being built (two background agents): galaxy's own siarnaq backend, unmodified, with local stand-ins for Google
  Cloud (storage, Pub/Sub, Cloud Tasks), a saturn replacement that compiles and runs games, and galaxy's own frontend
  built with the backend URL overridden to our host (the stock build points at api.battlecode.org). New host:
  https://galaxy.136-86-167-127.sslip.io/ (same basic-auth gate). Code in `tools/galaxy/`, docs in `docs/galaxy/`.
- After it: seed the field as teams through the API, our team submits through `tools/contest.py`, all games against
  other teams through scrimmage requests (galaxy limits: 10 unranked requests of up to 10 maps per hour, 10 ranked
  of 3 random maps, ranked only upward), results and replays downloaded through the API (`ReplayDump --games`
  reads multi-game match files). The galaxy-lite replica below is retired at cutover.

## The ladder replica (galaxy-lite)

- Site: https://136-86-167-127.sslip.io/ (user `owner`, password in `~/.bc23-replica-password`, rotated 2026-10-07;
  `ACCESS.md`). Code `tools/replica/`, docs `docs/replica/` (README, DEPLOY, VIEWER). Runs as user `bcreplica` under
  systemd: egress blocked by nftables, the worker in its own network namespace, resolver access denied over D-Bus;
  `tools/replica/deploy/verify.sh` checks all of it. The replay viewer is the official 3.0.15 web client, downloaded
  once and checksum-pinned.
- Started for real 2026-10-07 15:40 PDT (`tools/replica-reset.sh`; the test data is archived under
  `/home/bcreplica/replica/archive/`): 87 field bots + `us:examplefuncsplayer` + `us:g_iter0`, one autoscrim round
  (178 matches) to seed the ratings, worker at 3 slots (`REPLICA_SLOTS` in `/etc/bc23-replica/replica.env`; raise it
  when the gauntlet queue is idle). `tools/replica-matchmaker.py` (VM, `logs/matchmaker.log`) keeps 6 matches queued
  once the backlog drains: half by our incumbent against its rating neighbours, half by random field teams.
- Each check-in: `bash tools/replica-export.sh` (games into `progress/games.csv`, idempotent), then
  `tools/.venv/bin/python tools/replica/snapshot.py --from-vm` and commit `progress/ladder.{md,png}`.
- A new incumbent enters with `bc23-replica add-team us:<build>` and a line in `tools/incumbent.txt`.

## Compute

- Driver `claude-driver` (2 vCPU, 2 GB): this session; one diagnostic game at a time at most.
- VM `battlecode-dev` (us-west1-b, 8 vCPU, 31 GB, 20 GB disk), internal IP 10.138.0.3. Standing queue
  (`tools/vm-enqueue.sh`, runner `tools/vm-queue.sh`); gauntlet games share 5 slots (`/tmp/bc23-game-slots`), the
  replica worker has its own. Games against top bots run 1,000-2,000 rounds and take several minutes each.
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
