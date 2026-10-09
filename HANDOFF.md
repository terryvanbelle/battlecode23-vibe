# HANDOFF.md — current state (keep this current at every accept)

Updated 2026-10-09 01:20 PDT.

## Standing

- **Validated build g_iter2 = c_swarm1** (submission 121, code hash b646f1e92c6b; details in the replica section):
  panel 40/100, replica ladder #18 of 88 (rating 1484, 18 rated matches) on 2026-10-08 17:38 PDT.
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
g_iter2's own code scores 4/20 against itself (TRAINING_LOG 2026-10-08 22:45). Compare cell by cell.

| job | candidate | change | state |
|---|---|---|---|
| trial (replica) | c_nav4 (submission 122) | distance fields after a wall hit; forming wait capped | screen PASS; panel v1 requested 01:20 PDT 2026-10-09, behind the 01:00 autoscrim; judge with `tools/paired.py` against `gauntlet/20261008-210429-panel1-c_swarm1`, then `trial-end --accept/--reject` before 09:00 PDT |
| scr-c_swarm1id | identity | g_iter2's code under another package | screen stages a-b on the screen's cells: the stage-(b) baseline |

Results today (20 games vs g_iter2 on the h2h cells; identity 4): c_nav3 9 (paired vs identity +5), c_nav3a 8,
c_nav4 7 (+3), c_swarm4b 8, c_eco2 7, c_swarm3 6, c_swarm4a 6, c_role1 6, c_eco1 5. Plan: replica trial of c_nav4
after the 01:00 PDT autoscrim if the screen does not show a regression (`--skip-screen` with the reason if only the
uncalibrated stage-(b) bar fails).

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
- Validated build: **g_iter2 = c_swarm1** (submission 121, accepted 2026-10-08 17:00 PDT: panel 40/100 vs g_iter1's 33
  and g_iter0's 31; locally 17-3 vs g_iter1). It is the swarm archetype (docs/ARCHETYPES.md 4.1) frozen as a candidate.
  Baseline panel run for the next trials: `gauntlet/20261008-210429-panel1-c_swarm1`. Earlier: g_iter1 = c_line8a
  (`...-180016-panel1-c_line8a`, 33/100), g_iter0 (`...-011350-panel1-g_iter0`, 31/100). Local screen cells vs the
  incumbent: `test/cells/self-swarm1-panel.txt` (and vs g_iter1, g_iter0, the archetypes).
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
