# HANDOFF.md — current state (keep this current at every accept)

Updated 2026-10-15 12:20 PDT. The CLI session on claude-driver runs the project (the 2026-10-12 web-session state is
archived in `research/diagnosis/2026-10-12-handoff-inflight.md`). On 2026-10-12 18:48 PDT every galaxy unit stopped and
the VM queue runner exited on a STOP file, with no recorded reason; both were restarted on 2026-10-14 (the replica in
the morning, the runner at 11:47 PDT). `tools/watch_events.py` now reports either failure (REPLICA_DOWN,
QUEUE_RUNNER_DEAD) and must be armed at the end of every turn (CLAUDE.md rule 7).

## Standing

- **Validated build g_iter11 = c_well9** (submission 164, accepted 2026-10-15 12:18 PDT; active again as submission 166
  since 20:20 PDT, after c_well10's rejected trial): g_iter10 (c_mend2) plus
  c_well5's diagonal near-well mana probe only (no front probe: c_well5/c_well7 fed Forest carriers to the midline
  well). Panel 63/100 (`gauntlet/20261015-160249-panel-c_well9`): vs c_mend2 net +2 (6-4), island-rounds +324
  (t +1.61); vs c_bc1 net +5 (8-3), +507 (t +2.51). MassiveL mana +2,841 a game; Forest carrier deaths unchanged;
  0 exceptions. Judge candidates against c_well9's and c_mend2's panels.
- Before it **g_iter10 = c_mend2** (submission 143/163, accepted 2026-10-11 05:14 PDT): g_iter9 (c_bc1) plus
  wounded launchers (80 HP or less) heal on a nearby island we own (none before our first anchor). Panel 61/100: net +3
  vs c_bc1's panel (island-rounds +183, t +2.3), -1 vs c_aura2's; healed HP a game 1,561 -> 3,430 (t +4.8), launcher
  deaths -7.5 (t -2.4); 0 overruns. Panel run `gauntlet/20261011-080046-panel-c_mend2`.
- Before it **g_iter9 = c_bc1** (submission 136, accepted 2026-10-10 22:44 PDT): g_iter8 (c_aura2) plus
  decision-preserving launcher bytecode cuts (launcher near misses 44 -> 0 in 6 VM games; median calm-march turn
  6,856 -> 3,664). Panel 58/100 (net -4 vs c_aura2's, p 0.29; accepted as a basics fix, like c_nav6 at -2). Judge
  candidates against BOTH c_bc1's and c_aura2's panels: the same policy drawn twice (62 and 58); every candidate since
  c_aura2 lost island-rounds against its panel (-77 to -198), so a single reference draw biases toward rejection.
- Before it **g_iter8 = c_aura2** (submission 129, accepted 2026-10-10 06:15 PDT): g_iter7 (c_def3: anchor
  discipline + raid recall, panel 60/100) plus aura-safe launcher movement (inside an enemy HQ aura only outward steps;
  regroup moves avoid auras). Panel 62/100 (net +2); our launchers killed by enemy HQ auras 35 vs 1,227 per 100 games.
  Lineage: g_iter3 = c_nav4 (distance fields, 48), g_iter5 = c_nav6 (0 overruns), g_iter6 = c_anc3 (anchor discipline,
  57), g_iter7 = c_def3 (raid recall, 60).
- **Why we lose** (g_iter2's 10 panel matches, 1017-1026, `research/matches/`): not the opening fights. Before r400 we
  land the first hit in 55-72% of launcher duels and win 59-64% of engagements against vrangr1, jmerle, georgezhang and
  NotLLeon (awesomelemonade: 20%, they meet us with twice the launchers, group size 19 vs our 6). We lose the middle
  game: from r200 we build 3-5 carriers per 100 rounds against their 10-12, live carriers r500 14 vs 42, Mn r400-500
  304 vs 935; our HQs withhold carriers under threat (24% of mid-game HQ turns, 58% late) and are Mn-poor 38%.
  Raising the carrier cap or the Ad share lost in self-play (c_eco1 5/20, c_eco2 7/20).
- **Navigation** (owner, PROMPTS 35): on Target the incumbent strands launchers in dead-end corridors (march mode, up to
  317 rounds) and idles them forming up at home (40-150 rounds). c_nav3 adds per-robot distance fields
  (`src/c_nav3/Field.java`, TRAINING_LOG 2026-10-08 20:45): locally on Target it wins by 75% islands at r640-797 with
  no launcher still 40+ rounds; 0 overruns.


## In flight (2026-10-16 11:45 PDT)

- **Owner's parameter-search project (PROMPTS 114; practice session, bold attempts welcome).** `tools/param.py`
  builds a package with C.java constants overridden at build time (`make BASE NEW NAME=VALUE ...`; `space` = 73
  numeric constants with ranges and 10 constraints; `sample` = random valid settings). `tools/swiss.py` runs a Swiss
  tournament of the base plus random variants (`init` [--pool A,B,.. --k K for a focused search], `run`,
  `standings`, `analyse`, `export DIR BOT NEWPKG`). First run done 11:16 PDT (below).
- **Watcher fix (08:34 PDT):** SCREEN_DONE never fired before (the VM probe expanded on the driver); it does now.

- **Owner idea (PROMPTS 108): a jmerle mimic as a sparring partner.** `tools/sa_extract.py` + ReplayDump `--sa` wrote
  state-action rows for jmerle.camel_case_v30_final and our side of the same 240 panel games
  (`research/clone/jmerle/`, gitignored, 367 MB). `src/arch_jm` (c_mend2 + mana-first, blind fire, midfield front,
  close-in) matches jmerle's micro and mana share; fidelity 12/20 games agree with our record against the real jmerle
  (Forest and Maze reproduced; Cornucopia, MassiveL, BatSignal not). Its ablation found no single jmerle behaviour that
  carries the result; the c_mend2 control beat c_well9 on Forest 4-0, which exposed the real gap (TRAINING_LOG
  2026-10-15 14:40-15:25): **Forest's contested mana wells (29,48)/(30,48)**, which jmerle holds from r0 (launchers
  1.9 -> 8.6, carriers 1.8 -> 22.4 within r2 64) and we never visit (0.0 in every bucket).
- **c_well10 rejected** (c_well9 with hot wells off; screen PASS 11/20; panel 62/100, net -1 vs c_well9, island-rounds
  -210 t -2.12). Hot wells pay for themselves: MassiveL -1,429 island-rounds and -1,784 Mn a game without them,
  Cornucopia -701; Forest +677 Mn but +16.6 carrier deaths. Keep C.HOT on.
- **c_mid1** (10f9d74; contested-well objective on c_well9: HQ 0 picks a mana well in band p 35-65% beyond r2 64 of
  every HQ, launchers with id%3==0 hold it for 100-round tours, carriers mine it while screened and leave through home
  when outnumbered; PROBE_FRONT on, C.HOT on with the site exempt). Screen queued 21:54 PDT
  (20261016-045404-scr-c_mid1-5c619ca1048d): PASS, h2h 13/20, roster net +7 (arch_jm +4); local 19/32 on the
  jmerle-study cells (c_well9 11/32; Forest 8/8). **Trial rejected 05:18 PDT** (submission 167, panel
  gauntlet/20261016-080646-panel-c_mid1): 62/100 vs 63, paired net -1 (-0.58 SE), 97 identical; Forest +1,
  Cornucopia -1, MassiveL -1, the rest identical (the site exists only where a mid-band mana well is some HQ's
  nearest).
- **c_raid1** (d14555c; c_mid1 + mana raid: enemy-side mana wells are raid targets at any distance, mana before Ad):
  held, 19/40 on the 40 study cells (c_mid1 22/40): Cornucopia better (4/8 vs 3/8), Maze worse (1/8 vs 4/8: the army
  tours five enemy wells). A narrower variant (only the nearest enemy-side mana well) is untested.
- **c_front1** (e38aa0c; c_mid1 + arch_jm's midfield front, C.FRONT): held, 19/40 on the 40 study cells (c_mid1
  22/40): ReverseFunnel 5/8 and Cornucopia 4/8 better, Forest 6/8 and Maze 1/8 worse.
- **Losses to jmerle are mana stalls** (TRAINING_LOG 2026-10-16 03:15): our Mn collection stops near r100-125 on
  Cornucopia and IslandHopping while jmerle's launchers sit on our contested or home mana wells; launchers react only
  to sightings within r2 64 and the HQ recall rallies on the HQ tile.
- **The losses are a production race lost at home** (TRAINING_LOG 2026-10-16 04:56): launcher trades are even per 50
  rounds to r300, but the war is in our half from r50 and our carriers die 2:1 (10.7 vs 5.8 a game by r300, 6.4
  within 5 tiles of our HQs); launchers 13 vs 11 at r100, 13 vs 20 at r250 on mining.
- **c_rally1** (c_mid1 + an outnumbered launcher's step weighs r2 to our nearest HQ, Launcher.kiteScore): held,
  41/80 on VM rally1-80 (study cells 23/40, c_mid1 22/40; h2h vs c_mid1 18/40).
- **c_guard1** (c_mid1 + home-well defence, C.GUARD: carriers report the raider they fled at their next write turn;
  launchers within r2 400 take fresh home-zone sightings nearer than their site or siege target): 45/80 on VM
  guard1-80, study cells 24/40 (c_mid1 22/40), h2h vs c_mid1 21/40 (Forest 4/4, Cat 3/4, Cornucopia 3/4; DefaultMap,
  Maze, ReverseFunnel 1/4 each).
- **c_guard2** (c_guard1 + one sentry amplifier per HQ at the home mana well beyond the HQ's vision, C.SENTRY, AD_FLAGS
  heartbeat bits 12-15): held, study cells 18/40 on VM guard2-80 (stopped at 40 of 80 games, 06:41 PDT).
- **Carriers walk empty** (TRAINING_LOG 2026-10-16 05:52): r40-200 we collect on 0.36 of carrier turns to jmerle's
  0.52 and walk empty on 0.36 to their 0.10; Forest's home mana well (walls on three sides) yields 386-469 collects
  per 100 rounds to their 482-592 (they fill the well tile), and they take up to 700 from the midline mana pair that
  we never mine (hot).
- **c_pack1** (c_well9 + well packing, C.PACK: near its well a carrier takes the nearest free collect square, a
  collector steps onto a free well tile): delivery on Forest vs c_well9, home well 491-545 collects per 100 rounds
  to 475-482, 106-165 of them on the well tile. Screen queued 06:09 PDT (job 20261016-130923-scr-c_pack1-b6ac7e5c5e37;
  `tools/screen.py collect c_pack1`), started with --min-disk-gb 1.4 (1.6 GB free); finished gauntlets' replays pruned
  06:23 PDT (owner, PROMPTS 113): 2.2 GB free. Screen PASS 08:06 PDT (h2h 13/20, roster info Net +3, 148 games 0
  overruns or exceptions; progress/screens/c_pack1-b6ac7e5c5e37.json): trial from 09:00 PDT.
- **c_gp1** (c_guard1 + c_pack1's packing, same code and constants): delivery game vs c_well9 on Forest 1101 won
  at r2000, collMn 20,316 to 7,089; VM gp1-80 52/80 (c_guard1 45/80 on the same cells). Screen PASS 10:01 PDT
  (h2h 12/20, roster info Net +9: arch_jm +5, arch_ampmid +2, arch_swarm +2; 148 games 0 overruns or exceptions;
  progress/screens/c_gp1-5ab98ca6e5b2.json). **Trial started 10:02 PDT** (submission 171, panel requests
  4343-4352), parked once its matches exist. Both panels (c_pack1 169, c_gp1 171) wait in the queue; the watcher
  reports PANEL_DONE for each. Compare paired with c_well9's panel (63/100) via tools/paired.py, then
  `trial-decide <pkg> --accept|--reject`; if c_pack1 is accepted first, c_gp1 must also beat c_pack1.
- **Replica queue (10:54 PDT):** ~35 matches/h; 95 queued ahead of our panels (c_pack1 8201-8210, c_gp1
  8211-8220), which should start ~13:40 and end ~16:30 PDT.
- **Swiss DONE 11:16 PDT** (research/swiss/20261016-153444-swiss-n4/): WINNER c_sw07 18/24 (c_sw06 16, c_sw12 16,
  c_well9 15, unbeaten); c_sw07 drew c_well9 3-3 head to head. No constant is established by the correlations
  (n=16). c_sw07 = **src/c_tune1**: **trial started 11:43 PDT** (submission 173, --skip-screen "owner PROMPTS
  114"), parked (panel matches 8221-8230; c_well9 active again as 174); expected ~18:30-19:30 PDT. Its screen and
  c_adlo1's run on the VM for information (`tools/screen.py collect <pkg>` on SCREEN_DONE).
- **c_adlo1** (tools/param.py make c_well9: AD_EARLY_EVERY 12, AD_LATE_EVERY 7, CAP_MAX 40, CAP_PER_MN_WELL 7,
  ANCHOR_START 330): the direction shared by the Swiss leaders after round 2 (c_sw12, c_sw07, c_sw11), and we float
  Ad (bank_end_Ad 982-1,165 vs 361-507). Delivery game on the driver first.
- **c_front1** screen FAIL (b 10/20 borderline, roster info Net -16).
- Rejected 10-15: c_cap1, c_thr1, c_open1, c_siege1, c_well10 (TRAINING_LOG). c_ad1 committed, held (Ad is not a loss root).

**Ranked play** chooses the open team above us with the largest expected gain (`docs/LADDER_STRATEGY.md`).

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
- Validated build: **g_iter11 = c_well9** (submission 164, accepted 2026-10-15 12:18 PDT, resubmitted as 166 at 20:20 PDT; baseline panel run
  `gauntlet/20261015-160249-panel-c_well9`, 63/100). Before it **g_iter10 = c_mend2** (accepted as 143, 2026-10-11 05:14 PDT; baseline panel run
  `gauntlet/20261011-080046-panel-c_mend2`, 61/100). Before it **g_iter9 = c_bc1** (submission 136, accepted 2026-10-10 22:44 PDT; baseline panel run
  `gauntlet/20261011-042052-panel-c_bc1`, 58/100). Before it **g_iter8 = c_aura2** (submission 129, accepted
  2026-10-10 06:15 PDT; baseline panel run `gauntlet/20261010-121416-panel-c_aura2`, 62/100). Before it **g_iter7 = c_def3** (submission 126; resubmitted as 128 after c_flee3's rejection, accepted 2026-10-09 21:40 PDT; baseline panel run
  `gauntlet/20261010-023758-panel-c_def3`, 60/100). Before it g_iter6 = c_anc3 (submission 125,
  `gauntlet/20261009-211419-panel-c_anc3`, 57/100). Before it g_iter5 = c_nav6 (submission 124,
  `gauntlet/20261009-191411-panel-c_nav6`, 46/100). Before it g_iter4 = c_nav5 (submission 123; panel identical to g_iter3's,
  `gauntlet/20261009-155042-panel-c_nav5`). Before it, **g_iter3 = c_nav4** (submission 122, accepted 2026-10-09 04:14 PDT: panel 48/100 vs g_iter2's 40,
  paired net +8, +2.31 SE; screen PASS `progress/screens/c_nav4-9f333d33cf78.json`). It is g_iter2 plus per-robot
  distance-field navigation and a capped forming wait (owner, PROMPTS 35). Baseline panel run for the next trials:
  `gauntlet/20261009-082005-panel-c_nav4`. Earlier: g_iter2 = c_swarm1 (`...-210429-panel1-c_swarm1`, 40/100), g_iter1 =
  c_line8a (`...-180016-panel1-c_line8a`, 33/100), g_iter0 (`...-011350-panel1-g_iter0`, 31/100). Local cells vs the
  previous incumbent: `test/cells/self-swarm1-panel.txt`; the pre-trial screen (`tools/screen.py`) reads the current
  validated package from `progress/ladder-state.json` (last recorded: c_well9).
- Ranked vs unranked follows `docs/LADDER_STRATEGY.md` (owner, PROMPTS 17-18), state in `progress/ladder-state.json`:
  `tools/ladder_policy.py ranked` runs detached on the driver (PID 3179283 since 2026-10-14 11:46 PDT; log
  `logs/ranked-policy.log`): ranked challenges upward
  only while the validated build is active (BURST one per 5 min while we have < 30 rated matches or the build is < 24 h
  old, else one per 30 min). Candidates go through `trial-start <package>` (incoming ranked auto-rejected, unranked
  panel) and `trial-end --accept|--reject`; or `trial-park` (once the panel's matches exist the validated build
  is back while the panel plays) and later `trial-decide <package> --accept|--reject`, so panels overlap. Trials: c_line4 25/100 (rejected), c_line5 28 (rejected), c_line6 32 (even, not accepted; working base). Autoscrim: galaxy's own, every 8 hours over all teams (17:00, 01:00, 09:00 PDT). Field teams challenge in idle capacity, weighted toward the low end of the displayed ladder (under-played teams). Field-vs-field replays are pruned after 6 h.
- Pre-trial screen (owner, PROMPTS 22-23; `docs/ARCHETYPES.md` section 5, `docs/LADDER_STRATEGY.md`): `trial-start`
  refuses a candidate without a PASS record in `progress/screens/` (`tools/screen.py <package>`: basics vs
  examplefuncsplayer, 20 head-to-head vs the validated build, 20 per archetype paired with the validated build's
  games; about 1.5 h on the VM). Archetypes `src/arch_{swarm,blob,adecon,horde,ampmid}` (notes `research/archetypes/`)
  are built from replica replays only. None gates yet: no VALID record exists (`tools/archsig.py` not built; the
  2026-10-08 verifier found 4 of 5 just outside their tolerances), so the roster is information only and a BORDERLINE
  head-to-head fails. arch_swarm has g_iter2's code hash, so the S1 slot is empty until a stronger swarm archetype is built.
- Every replica game must count (owner, PROMPTS 13): bot telemetry (docs/TELEMETRY.md; galaxy runs with indicators
  off, so contest replays carry a 6-bit state code per robot-turn in the bytecode count), ReplayDump extractors (engagements,
  timelines, death causes, opponent tactics) and a per-match report for every downloaded match (`research/matches/`,
  `progress/telemetry.jsonl`, `tools/telemetry_query.py`). Every submitted build carries telemetry.
- The field: 87 teams, one per public 2023 bot (`tools/galaxy/field.py`, mapping `tools/galaxy/field-teams.tsv`; one
  name shortened: `remember-to-hydrate.sprint_1`), each its own user (passwords only on the VM,
  `~/.bc23-galaxy-field/accounts.json`), all compiled, auto-accept on. Autoscrims: `bc23-galaxy-scheduler.timer`
  enabled 2026-10-07 18:19 PDT, every 8 h from 01:00 PDT (176 matches per round, about 3-4 h on 7 engines: our
  requests queue behind a round; `docs/galaxy/README.md` section 8, capacity). Field activity on the VM
  (`field.py activity`, `logs/field-activity.log`): random field teams request ranked scrimmages upward, one a
  minute while fewer than 2 matches wait. saturn has 7 engines (since the experiment queue drained).
- Each check-in: `python3 tools/galaxy/results.py` (finished matches into `progress/games.csv` as `galaxy-<match>`,
  our rows `us:<package>`; idempotent), `tools/.venv/bin/python tools/galaxy/snapshot.py` (`progress/ladder.{md,png}`
  from the Rankings page), `tools/elo.py`; commit them together.
- galaxy-lite (the first replica, `tools/replica/`) was retired 2026-10-07 18:01 PDT: units stopped and disabled, data
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
  robots only. Repeat claims require matching code, map orientation, A/B labels, configuration and JDK (30/30 selected
  field checks agreed; RULES 9.8 lists residual nondeterminism). The final tiebreak is an unseeded coin flip: identify
  it from full replay-derived win_reason before pairing; galaxy result rows often have blank reason fields.
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
