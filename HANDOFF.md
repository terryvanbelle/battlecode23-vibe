# HANDOFF.md — current state (keep this current at every accept)

Updated 2026-10-10 09:30 PDT.

## Standing

- **Validated build g_iter8 = c_aura2** (submission 129, accepted 2026-10-10 06:15 PDT): g_iter7 (c_def3: anchor
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

## In flight (VM queue; self-play cells pinned by seed)

**Read head-to-heads against the identity control, never against 10/20**: on `test/cells/self-swarm1-panel.txt`
g_iter2's own code scores 4/20 against itself (TRAINING_LOG 2026-10-08 22:35); on the screen's map-seed cells it scores
10/20 (seat-neutral, 2026-10-09 01:30). Compare cell by cell, and arms built on g_iter3 against c_nav4's own runs.

| arm | change (from c_nav4 = g_iter3) | local result | next |
|---|---|---|---|
| c_hq1 | HQs build carriers under threat on spawn tiles no visible enemy fighter reaches | screen vs g_iter3 FAIL (h2h 8-12) | closed |
| c_role2 | adamantium role rotates over trips (id + trips), not ids | screen vs g_iter3 FAIL (h2h 10-10, roster Net -5) | closed |
| c_nav5 | Field.level bounded (search from the cached wave, guard 3,000 bytecodes) | panel identical to g_iter3 (100/100), same 3 overruns | accepted 09:28 PDT as g_iter4 |
| c_nav6 | g_iter4 + bounded fight scoring, second shot and track() in crowds | panel 98/100 identical, -2 (noise), 0 overruns | accepted 13:15 PDT as g_iter5 |
| c_anc3 | c_nav6 + anchor discipline | screen PASS (roster Net +16); panel 57/100, net +11 (p 0.003) | accepted 15:14 PDT as g_iter6 |
| c_def2 | c_nav6 + HQ raid alarm (slot 56) and recall of nearby launchers before r600 | standalone screen vs c_nav5 finishing (h2h 11-9) | superseded by c_def3 |
| c_cloud1 | c_nav6 + hold on recent contact, cloud-aware regroup, blind shot | standalone screen cancelled | superseded by c_cld2 |
| c_cld2 | g_iter6 (c_anc3) + c_cloud1's launcher changes | screen vs g_iter6 FAIL (h2h 9-11, roster +1) | closed |
| c_def3 | g_iter6 (c_anc3) + c_def2's raid alarm and recall | screen PASS; panel 60/100, net +3 (vrangr1 +3) | accepted 21:40 PDT as g_iter7 |
| c_flee2 | g_iter6 + carriers remember the raid they fled | screen vs c_anc3 PASS: h2h 12-8, roster +3, near misses 83 | rebased as c_flee3 |
| c_flee3 | g_iter7 (c_def3) + c_flee2 | screen PASS (12-8, +4); panel 56/100, net -4 | rejected 05:13 PDT |
| c_well3 | g_iter6 + home mana-well probe and re-pick at deposit | compiled, reviewed | rebased as c_well4 |
| c_aura1 | g_iter6 + aura-safe launcher movement (test/bot/AuraStepTest.java) | compiled, reviewed | rebased as c_aura2 |
| c_well4 | g_iter7 (c_def3) + c_well3 | screen FAIL (h2h 10-10, roster +1); MassiveL: probe never got carriers onto (2,0) | closed; debug the probe before retrying |
| c_aura2 | g_iter7 (c_def3) + c_aura1 | screen PASS (13-7, +2); panel 62/100, net +2; aura deaths 1,227 -> 35 | accepted 06:15 PDT as g_iter8 |
| c_well5 | g_iter8 + home mana-well probe made reliable, re-pick at deposit (`research/diagnosis/2026-10-10-g_iter8.md` rank 1) | screen PASS (h2h 12-8, roster +0 information only, 128 games 0 overruns) | trial (submission 130) started 11:39 PDT; judge vs gauntlet/20261010-121416-panel-c_aura2 |
| c_spread2 | g_iter8 + surplus launchers at a saturated siege ring press the other enemy HQs (rank 2) | unit tests PASS (test/bot/SpreadTest.java) | screen running (h2h at 13/20) |
| c_scout1 | g_iter8 + a claimed, replaceable island scout (rank 3) | unit tests PASS | screen queued |
| c_grp1 | formations of 6 at home, wait up to 25 turns | 9/20 vs g_iter2; screen vs g_iter3 FAIL (h2h 7-13) | closed |

Closed or superseded since g_iter2 (20 games vs g_iter2 on the h2h cells; identity 4): c_nav3 9, c_nav3a 8, c_swarm4b 8,
c_eco2 7, c_swarm3 6, c_swarm4a 6, c_role1 6, c_eco1 5. None is a measured regression; c_role1's per-trip adamantium
rotation is worth carrying into a later arm.

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
- Validated build: **g_iter8 = c_aura2** (submission 129, accepted 2026-10-10 06:15 PDT; baseline panel run
  `gauntlet/20261010-121416-panel-c_aura2`, 62/100). Before it **g_iter7 = c_def3** (submission 126; resubmitted as 128 after c_flee3's rejection, accepted 2026-10-09 21:40 PDT; baseline panel run
  `gauntlet/20261010-023758-panel-c_def3`, 60/100). Before it g_iter6 = c_anc3 (submission 125,
  `gauntlet/20261009-211419-panel-c_anc3`, 57/100). Before it g_iter5 = c_nav6 (submission 124,
  `gauntlet/20261009-191411-panel-c_nav6`, 46/100). Before it g_iter4 = c_nav5 (submission 123; panel identical to g_iter3's,
  `gauntlet/20261009-155042-panel-c_nav5`). Before it, **g_iter3 = c_nav4** (submission 122, accepted 2026-10-09 04:14 PDT: panel 48/100 vs g_iter2's 40,
  paired net +8, +2.31 SE; screen PASS `progress/screens/c_nav4-9f333d33cf78.json`). It is g_iter2 plus per-robot
  distance-field navigation and a capped forming wait (owner, PROMPTS 35). Baseline panel run for the next trials:
  `gauntlet/20261009-082005-panel-c_nav4`. Earlier: g_iter2 = c_swarm1 (`...-210429-panel1-c_swarm1`, 40/100), g_iter1 =
  c_line8a (`...-180016-panel1-c_line8a`, 33/100), g_iter0 (`...-011350-panel1-g_iter0`, 31/100). Local cells vs the
  previous incumbent: `test/cells/self-swarm1-panel.txt`; the pre-trial screen (`tools/screen.py`) now plays against
  g_iter3.
- Ranked vs unranked follows `docs/LADDER_STRATEGY.md` (owner, PROMPTS 17-18), state in `progress/ladder-state.json`:
  `tools/ladder_policy.py ranked` runs detached on the driver (`logs/ranked-policy.log`): ranked challenges upward
  only while the validated build is active (BURST one per 5 min while we have < 30 rated matches or the build is < 24 h
  old, else one per 30 min). Candidates go through `trial-start <package>` (incoming ranked auto-rejected, unranked
  panel) and `trial-end --accept|--reject`. Trials: c_line4 25/100 (rejected), c_line5 28 (rejected), c_line6 32 (even, not accepted; working base). Autoscrim: galaxy's own, every 8 hours over all teams (17:00, 01:00, 09:00 PDT). Field teams challenge in idle capacity, weighted toward the low end of the displayed ladder (under-played teams). Field-vs-field replays are pruned after 6 h.
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
