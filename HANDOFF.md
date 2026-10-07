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

| job | candidate | change | control |
|---|---|---|---|
| cand-nav1 | c_nav1 | bug navigation keeps its hand per obstacle | c_econ1 (live-robot carrier bound; neutral, +4 net) |
| cand-mana1 | c_mana1 | mana-first roles, adaptive at delivery | c_nav1 |
| cand-mana2 | c_mana2 | 1 in 5 carriers on adamantium, overrides by HQ stock | c_nav1 |
| deliv-mana1/micro1/batch1 | c_micro1, c_batch1 | pinned-enemy micro, safe step-in; launcher batches of 3 | c_mana1, c_micro1 |

Cells: `test/cells/calib-g_iter0.txt` (174, every entrant twice) and `test/cells/diag-top4.txt` (24, four top bots).
Read with `tools/paired.py <cand run> <control run>` and `tools/delivery.py <cand run> <control run>`.

## The ladder replica (galaxy-lite)

- Site: https://136-86-167-127.sslip.io/ (user `owner`, password in `~/.bc23-replica-password`; `ACCESS.md`).
- Code `tools/replica/`, docs `docs/replica/` (README, DEPLOY, VIEWER). Runs as user `bcreplica` under systemd with an
  egress block; the replay viewer is the official 3.0.15 web client, downloaded once and checksum-pinned.
- To do next: archive the test DB, init, seed the 87 entrants + us:g_iter0 + examplefuncsplayer, start
  `tools/replica-matchmaker.py` (incumbent vs rating neighbours, random field bots in spare cycles), export games to
  `progress/games.csv`, commit `progress/ladder.{md,png}` after each round, rotate the site password (it was printed
  once in the session transcript, never committed).

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
