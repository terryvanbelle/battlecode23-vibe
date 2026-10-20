# TRAINING_LOG.md

Append-only record of the project, one entry per step or attempt. Corrections are dated entries in place, never edits
of history. Times are PDT. Grep it; do not read it whole.

## 2026-10-07 07:45 — Start (PROMPTS 1-5)

- Repo `terryvanbelle/battlecode23-vibe` created. Prior-year repos are all present locally and up to date with GitHub
  (2020, 2024, 2025 working copies; 21, 22, 26 and anicolao/bcenv under `~/projects/vibe/reference/`). Cross-year advice
  `terryvanbelle/battlecode-vibe` cloned (branch `main` holds ADVICE.md plus the five topic guides COMBAT, ECONOMY,
  EXPLORATION, NAVIGATION, SYMMETRY).
- **Disclosure: brief exposure to 2023-tagged lines.** While locating how the topic guides tag their sources, a `grep
  2023` printed about 60 lines tagged with 2023 sources (fragments of 2023 post-mortem advice on kiting, carrier cargo
  throws, comms layouts, bug navigation and type ratios) before any filter existed. Nothing was read beyond that grep
  output. From then on, every prior-year document is read only through the filtered reading room
  (`~/projects/vibe/reference/readroom-no2023/`, built by `reference/battlecode-vibe-no2023/build_readroom.py`, which
  drops every block tagged 2023 or naming a 2023 team or unit; residual matches 0 over 2,057 files). ADVICE.md itself
  has no 2023-tagged lines.
- Owner prompt 3: 2024 local storage may be cleared. Removed the pushed 2024 repo's untracked build products
  (build, diag, engine, gauntlet, matches, tools/.venv), `bc24-benchmarks/`, `bc24-classify.tsv`, and the 2024 engine
  clones. Driver free disk 1.9 GB -> 2.9 GB.
- Engine: the official public jar `battlecode23-3.0.15.jar` (fat jar, all dependencies and 103 maps) downloads from
  releases.battlecode.org (3.0.14, the version the official runner used, is not downloadable). The cloned source
  `battlecode/battlecode23` master is exactly tag 3.0.15. `tools/get-engine.sh` pins the checksum and compiles one patched
  class (LiveMap.getSeed honours `-Dbc.game.seed`), since the engine otherwise seeds robot ids and every sandboxed Random
  from the map file, so (bots, map, side) would fully determine a game.
- First game (driver): examplefuncsplayer mirror on maptestsmall ran 2000 rounds in 2 min 41 s, won by A on the mana
  tiebreak.
- VM `battlecode-dev` (us-west1-b, 8 vCPU / 31 GB / 20 GB disk, 8.6 GB free) started; it is in the driver's zone and is
  reached on its internal IP. `battlecode-dev2` (2024's, us-west2-a) is left untouched.
- Throughput (examplefuncsplayer mirror, DefaultMap, 2000 rounds): K=1 52.7 s/game; K=4 3.7 games/min; K=8 8.9
  games/min; K=12 9.7 games/min. About 3 MB per replay.
- GitHub code search (REST `search/code`) returns HTTP 500 for every query today; discovery uses repository search,
  push/creation-date windows and the forks of `battlecode/battlecode23-scaffold` instead (864 candidates).

## 2026-10-07 08:00-13:00 — Phase 0 instruments, reading, field

- Reading (workflow, 26 agents): per-slice reports for bc22/26/25/21/20/24, bcenv, the basics guides mapped to 2023,
  galaxy; synthesis and gap reads in `research/prior/`. Rules digest (workflow, 13 agents, adversarially verified):
  `RULES.md` + `research/rules/`. TRAINING_ALGORITHM.md written (year-agnostic).
- Field (BENCHMARK.md): 864 repo-search candidates + 22 from a web sweep; 148 repos use the 2023 API; 18 excluded
  (engine and its forks, non-entrants); 968 packages compiled; 87 entrants after two selection rules and hash dedupe.
- Replay reader `tools/replay-dump.sh` (.bc23): rebuilt state from events; fixture tests pin numbers cross-checked
  against the raw stream and the engine's verdict.

## 2026-10-07 13:00-15:00 — Foundation bot g_iter0

- Draft bot vs examplefuncsplayer, 8 maps x 2 sides: 16/16. Replay trace found (1) overruns on every unit's first turn
  (map memory alloc + full scan): fixed by a bytecode-budgeted end-of-turn fill; (2) carriers mined 0 mana (wells seen
  out of write range were never shared): fixed by late reporting and role adaptation; (3) Ad floating.
- Exceptions 1-7 per game: a robot that moved since turn start wrote the shared array outside its write zone. Every write
  now re-checks legality (`Comms.put`). 0 since.
- foundation1/2 (all 103 maps x 2 sides): 206/206. Basics: 0 overruns, 0 exceptions; symmetry wrong on Sine (HQ evidence
  used at round 1 before every HQ had registered; fixed: no HQ evidence before round 2); 12 games never decided
  (ambiguous maps; fixed: candidates that predict the same enemy HQs count as decided).
- Anchor degeneracy (Forest trace): 89 anchors built, 85 taken, 4 placed; carriers hoarded unplaceable anchors all game.
  Fix: safe-side targets, free-tile approach, timeout and return, per-HQ anchor period, predicted islands by symmetry.
  foundation3: 206/206; basics PASS (0/0/0, symmetry never wrong, decided by r150 in 204/206, never-decided 0); anchors
  placed 51% of built (36% before); r2000 games 9 (18 before); Mn collected +3.6 SE.
- Snapshot **g_iter0** (code hash e6f2fc5356c6).

## 2026-10-07 15:00 — First field calibration (174 games, 2 per entrant, random maps/sides/seeds)

- g_iter0: 131-43 (75.3%); BT 1732 +- 66, rank 17 of 88; field score 75.0%; 16 entrants beat us 2-0.
- Loss census (43 games, medians, us vs them): carriers built 21 vs 78; launchers 58 vs 141; Mn collected 602 vs 6,492;
  Ad 442 vs 2,559; kills 29 vs 82; anchors placed 1 vs 4. Wins: collected Mn 1,245 vs 85.
- Trace (awesomelemonade.finalBot, ReverseFunnel): equal collection to r250; our carriers flatlined at 16 (cap) while
  theirs reached 50; Ad floated 1,000-1,900 from r300; our launchers stuck below the dividing wall r120-r250 (bug
  navigation flipped hand every 24 moves along a long wall). Strong bots mine mostly mana (camel_case on Risk: 1,700 Mn,
  27 Ad; awesomelemonade on ReverseFunnel: 12,186 Mn, 4,521 Ad); none upgraded wells.

## 2026-10-07 15:00-15:30 — Instruments: identity control, paired cells

- Identity control: the working bot (byte-identical to g_iter0) on 30 calibration cells: 30/30 identical results and
  identical island-rounds margins. Games are deterministic against external bots given (opponent, map, side, seed).
- A second "identity" run was not one: it compiled src/bot after the next change had been synced. Runs now record the
  code hash of the bot that played (`provenance.txt`).

## 2026-10-07 15:30 — Arm c_econ1: carrier production bounded by live robots per known well

- Pre-registered: the old cap counted carriers EVER built per HQ (4 + round/40, max 24), a lockout under attrition.
  Counter: carriers built in losses. Gate: paired on the 174 calibration cells vs g_iter0.
- Result: carriers built in losses 21 -> 34, Mn 602 -> 799, Ad 442 -> 813, Ad float at end 1,340 -> 880; outcomes
  identical 164, gained 7, lost 3: net +4 (+1.26 SE, sign p 0.34); island-rounds margin -9.7 (t -0.14). Neutral.
  Kept in the working line (a cap removal; it is the base for the next arms), not snapshotted as an accept.

## 2026-10-07 15:30 — Queued arms (each paired on the 174 calibration cells against its predecessor)

- c_nav1 (on c_econ1): bug navigation keeps its hand for the whole obstacle; flips only at the map edge or after
  2(W+H) moves; refuses steps onto currents that push straight back; waits for robots on the wall path. Counters wh/bf.
- c_mana1 (on c_nav1): mana-first carrier roles (adamantium only while the delivering HQ holds < 120 Ad; the first 40
  rounds alternate).
- diag-top4: the working bot vs awesomelemonade, camel_case, CyrilSharma, NotLLeon on DefaultMap/Maze/Forest, both
  sides, all replays kept, census with carrier state tokens and launcher micro rates.

## 2026-10-07 15:45 — Ladder replica live; tactics of the top four (diag-top4, g_iter0 code)

- The ladder replica started for real (87 field bots, `us:examplefuncsplayer`, `us:g_iter0`; one autoscrim round to
  seed ratings, then the matchmaker). Site and access: `ACCESS.md`.
- Profile (`tools/profile.py`, 24 games, means; alive counts at r100 and r250, collected by r100 and r250):

  | team | C100 | L100 | Mn100 | Ad100 | C250 | L250 | Mn250 | first anchor | exposed | dmg/contact |
  |---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
  | us | 22 | 10 | 296 | 449 | 21 | 8 | 913 | 118 | 0.168 | 13 |
  | CyrilSharma.finalBot | 18 | 18 | 682 | 86 | 30 | 46 | 2,450 | 276 | 0.002 | 5.7 |
  | awesomelemonade.finalBot | 18 | 17 | 653 | 177 | 30 | 50 | 2,322 | 314 | 0.005 | 2.4 |
  | jmerle.camel_case_v30_final | 18 | 17 | 760 | 59 | 30 | 53 | 2,460 | 349 | | |
  | NotLLeon.v7 | 14 | 14 | 478 | 7 | 20 | 20 | 1,392 | 196 | 0.137 | 9.2 |

- Timeline (awesomelemonade on DefaultMap, 3 HQs each, both teams start with 600 Ad + 600 Mn): by r20 they field 13
  launchers to our 6 and have killed 6 of ours for 3; they spent the whole starting mana on launchers and their
  carriers delivered 107 Mn by r20 (ours 56). Our launchers die by r140 (0 alive), our carriers by r180; the rest of the
  game is their island count climbing to 75%.
- Reading: total collection is equal to r100 (745 vs ~770); the split and the launcher count decide the game, and the
  early launcher fights are lost in numbers and exposure. The queued arms (mana-first roles; pinned-enemy micro and
  safe step-in; launcher batches) target exactly these. Their first anchor comes at r200-350, after map control.

## 2026-10-07 15:50 — Arm c_nav1: neutral, negative signature; c_nav2 queued

- c_nav1 vs c_econ1, 174 calibration cells: identical 164, gained 5, lost 5 (net 0); island-rounds margin -70 (t -0.58).
- Delivery: oscillation fell (aba -50 per game, t -2.8) but robots stood still more (launchers +3.1 points of their
  rounds, t +6.1; carriers +5.1, t +7.7), collection fell ~7% (Mn -125, t -1.67; Ad -126, t -1.68) and games ran 30
  rounds longer. Not accepted as is.
- Likeliest cause: the new 3-turn wait for a robot on the wall-following path (carriers crowd wells and the HQ).
  c_nav2 = c_nav1 without it, paired on the same cells against c_nav1 (queued). The working line drops the wait too.
- Arms built on c_nav1 (mana1, mana2, micro1, batch1, spawn1, army1) keep their paired comparisons against their own
  predecessors; the combined candidate will carry c_nav2's navigation if it holds.

## 2026-10-07 16:15 — Correctness audit (engine API; shared state) -> arm c_audit1

- Two read-only auditors on src/bot. Clean: every action guarded by its can* check, no reachable
  GameActionException, every write re-checked, encodings and symmetry images correct, costs and radii match RULES.
- Defects found and fixed (c_audit1 = c_spawn1 + c_nav2's navigation + these):
  - carriers moved once a turn when empty or light although the engine allows two (move cooldown 5 + 0.375 w < 10
    up to 13 kg): every outbound trip, well search and flight ran at half speed;
  - carriers mined only wells in the 16 shared slots, so a well a carrier saw out of write range waited for a
    delivery to be registered (62 of 103 maps have no mana well in HQ vision);
  - island slots have no timestamp and robots republished 60-round-old owners over newer news; HQs built anchors for
    enemy-held islands no carrier could place; launchers trusted a stale "enemy" owner over their own sighting and
    all walked to one stored tile of an enemy island (anchor decay scales with robots on its squares);
  - enemy sightings: the 4-bit round stamp wrapped after 256 rounds (old sightings looked fresh); clears reached
    beyond the launcher's vision;
  - the shared symmetry mask could eliminate all three; predicted anchor islands were never resolved;
  - launcher fight() cost ~47 + 8P bytecodes per enemy per tile (~12k in a 10-fighter fight, limit 10k): now
    per-enemy data once and a bytecode guard; "pinned" no longer counts current pushes.
- Gate: c_audit1 on the 174 calibration cells, paired against g_iter0's own calibration run (the cumulative line
  since the incumbent), moved to the front of the queue.

## 2026-10-07 16:30 — Arm c_mana1 rejected (the mechanism ran backwards)

- c_mana1 vs c_nav1, 174 calibration cells: identical 163, gained 2, lost 9 (net -7, -2.11 SE, sign p 0.065).
- Delivery inverted: mana collected -294 (t -4.5), adamantium +229 (t +3.3), mana by r250 -112 (t -6.7), launchers
  alive at r250 -1.7 (t -5.8), launchers built -4.2. The adaptive rule (adamantium while the HQ holds < 120 Ad) read
  "short" nearly always, because the HQ spends Ad on carriers as soon as it has it.
- The working line keeps c_nav1's policy (switch C.ROLES = 0); c_mana2 (1 in 5 on Ad, overrides only on real
  surplus/shortage) is still queued and decides whether ROLES becomes 2. Every arm queued after c_mana1 (micro1,
  batch1, spawn1, army1, audit1) carries c_mana1's roles: their comparisons against their own predecessors stand,
  but their absolute levels are depressed.

## 2026-10-07 16:50 — The line since g_iter0 (c_audit1) loses to g_iter0; HQ overruns found

- c_audit1 (econ1 + nav1 + mana1 + micro1 + batch1 + spawn1 + audit fixes) vs g_iter0's calibration run, same 174
  cells: identical 162, gained 3, lost 9 (net -6, -1.73 SE, sign p 0.15); island-rounds margin -259 (t -1.96).
- The economy tilted to adamantium: Ad collected +894 (t +8.3), carriers built +19 (t +10.3) and lost +6.9, Mn
  -107, launchers built -6.7 (t -3.4), anchors placed -0.2. Causes on record: c_mana1's roles (rejected), and a
  carrier bound (live robots, 30 + 15 per well) that no longer limits anything while carriers are built 1:1 with
  launchers.
- Basics regression: 111 HQ bytecode overruns in 10 of 174 games, all sieges we lost (HQ max 20,005-20,019 of
  20,000). Cause: spawn safety scored every spawn tile against every visible enemy for every build (up to 6 a turn).
  Fixed in the working line: threat per spawn tile once per turn, and the build loop stops below 4,000 bytecodes
  left. To be confirmed on replica games (siege cells are against field bots).
- Not accepted. The working line now: c_nav1's carrier roles (C.ROLES = 0), c_nav2's navigation, audit fixes, the
  HQ fix. Next evaluations go through the galaxy replica (PROMPTS 11).

## 2026-10-07 17:15 — Arm c_mana2 kept (roles)

- c_mana2 vs c_nav1, 174 calibration cells: identical 159, gained 10, lost 5 (net +5, +1.29 SE, sign p 0.30);
  island-rounds margin -40 (t -0.49).
- Delivered as designed: Mn by r100 +62 (t +8.9), Ad by r100 -112, launchers alive r100 +0.85 (t +5.3) and r250
  +1.3 (t +3.3), carriers built -7.3 and lost -2.2. Game-long Mn slightly lower (-78, t -1.1: fewer carriers).
- Working line: C.ROLES = 2.

## 2026-10-07 18:05 — Arm c_micro1 failed delivery (diag-top4)

- c_micro1 vs c_mana1, 24 games against four top bots: exposure +0.029 (t +1.75; bar: down), damage per contact
  +0.8, kills -5.3 (t -2.3), launchers alive r100 -1.7 (t -2.2); outcomes 1-2 net -1. The mechanism fired (pinned
  enemies seen in 24/24 games, mean 124; unsafe steps avoided mean 28) but moved the signature the wrong way.
- Working line: switch C.MICRO = false restores g_iter0's fight scoring (with the audit's bytecode-safe structure).
- Candidate for the replica panel: c_line3 = working line (mana2 roles, nav2, audit fixes, HQ fix, spawn safety,
  launcher batches, MICRO off, ARMY off). c_line2 (micro on) was never run and is removed.

## 2026-10-07 18:50 — Arm c_batch1 failed delivery (diag-top4)

- c_batch1 (launchers only in batches of 3 unless threatened) vs c_micro1, 24 games against four top bots: launchers
  alive r100 -3.0 (t -4.6) and r250 -1.9 (t -2.7), kills -9.5 (t -6.2), exposure +0.021 (t +3.8), damage per
  contact +1.5 (t +3.3), island-rounds -117 (t -2.6); outcomes 0-1. Holding mana for a batch delays every launcher
  and the batch does not fight better.
- Working line: C.LAUNCHER_BATCH = 1 (g_iter0's behaviour), applied with the telemetry change (the telemetry
  workflow is editing src/bot now). c_line3 still carries batches and micro-off; it will not be submitted.

## 2026-10-07 19:15 — Arm c_spawn1 (spawn on the tile fewest enemy fighters reach): kept, confounded by overruns

- c_spawn1 vs c_batch1, 24 games against four top bots: kills +21.9 (t +4.3), island-rounds +165 (t +2.1), launchers
  alive r100 +0.4 (t +1.3); launchers lost +18.8 (longer fights); exposure +0.023; outcomes 0-0 (24 losses each).
- It carried the per-build spawn scoring that overran sieged HQs: 22.6 overruns per game (t +3.4). The working line
  has the once-per-turn fix; spawn safety stays in and is judged with the line on the replica panel.

## 2026-10-07 19:45 — Arm c_army1 (launcher cohesion) passed delivery (diag-top4)

- c_army1 vs c_spawn1, 24 games against four top bots: exposure -0.030 (t -2.85), contact -0.040 (t -3.1),
  launchers lost -17.0 (t -2.8), launchers alive r100 +1.5 (t +2.4) and r250 +3.0 (t +3.3), kills unchanged (-0.7),
  island-rounds -73 (t -1.2); outcomes 1-0. Fired in 24/24 games (regroup turns mean 1,150, follow turns 126).
- Working line: C.ARMY = true and C.LAUNCHER_BATCH = 1, applied once the telemetry workflow releases src/bot; the
  combined line goes to the replica as a trial (docs/LADDER_STRATEGY.md).

## 2026-10-07 20:20 — Replica baseline panel (g_iter0); c_nav2 neutral; saturn at 7 engines

- Panel v1 with g_iter0 active (submission 24), 100 games through the replica (gauntlet/20261008-011350-panel1-g_iter0):
  31/100. By opponent: yaonam 9, Sprint1 6, reeceyang 6, britacatalin 4, pranayagra 2, NotLLeon 2, camel_case 1,
  CB_tuning2 1, vrangr1 0, awesomelemonade 0 (of 10 each). By map: Cat 6, DefaultMap 5, Hah 5, Maze 5, Cornucopia 3,
  IslandHopping 3, BatSignal 2, Forest 1, MassiveL 1, ReverseFunnel 0 (of 10 each). This is the validated build's
  panel run for every trial (docs/LADDER_STRATEGY.md).
- c_nav2 vs c_nav1 (174 calibration cells, the last pre-switch gauntlet): identical 166, gained 3, lost 5 (net -2,
  -0.71 SE). Stillness back to c_econ1's level (launchers -3.2 points, carriers -4.7, t -8), but collection did not
  recover (Mn +11, Ad -19): c_nav1's 7% collection drop came from another part of the change (hand kept per
  obstacle, current check or stall rule). Kept (neutral; fixes the stall). Open question for telemetry.
- The experiment queue on the VM has drained: saturn now runs 7 engines.

## 2026-10-07 21:15 — Baseline panel profile (tools/profile.py on the g_iter0 panel run)

- Opponents that beat g_iter0 on the panel (NotLLeon, awesomelemonade, CB_tuning2, camel_case, pranayagra, vrangr1):
  Mn by r100 374-571 (us 249), Ad by r100 16-386 (us 330), launchers alive r250 26-35 (us 7.8), exposure
  0.009-0.052 (us 0.123), damage per contact round 5.3-8.0 (us 14). The same signature as the diag-top4 study:
  early mana, launcher numbers, and fights not taken alone. Trial targets for the next candidate: Mn r100 up,
  launchers alive r250 up, exposure down.

## 2026-10-07 23:30 — First replica trial: c_line4 rejected (economy and army up, results down, HQ overruns)

- Trial per docs/LADDER_STRATEGY.md: c_line4 (submission 112: mana2 roles, nav2, audit fixes, spawn safety, cohesion
  on, no batches, telemetry) on panel v1 against g_iter0's panel run, same 100 cells:
  identical 88, gained 3, lost 9 (net -6, -1.73 SE); 25/100 vs 31/100.
- Delivered as designed: Mn by r100 +125 (t +11.1), launchers alive r100 +3.4 (t +10.6) and r250 +3.4 (t +4.4),
  kills +16.7 (t +2.9); exposure and damage per contact unchanged.
- Basics failure: HQ overruns 15.8 per game (t +4.4; 143 and 72 in the two 2000-round losses to britacatalin), only
  in sieges, which self-play does not reproduce. Fixed in the working line by bounding spawn scoring, the spawn-tile
  scan and the build loop by the bytecodes left (commit 89ed0d4).
- Where the games went: 9 of the 12 flipped cells were g_iter0 quick wins (r235-384, 5-7 anchors placed) that the
  candidate dragged to r572-2000 with 1-3 anchors. g_iter0 won 24 games by r400, c_line4 18. Overall anchor counts
  and first-anchor round are unchanged, so the loss is in specific quick-win games.
- HQ telemetry (bytecode channel, 100 games): build loop ended "threatened" (affordable carrier withheld under
  threat) in 43% of HQ turns, "poor" 39%, "anchor reserve" 16%; enemies within r2 9 of our HQs 2,934 HQ-rounds per
  game vs 190 near theirs. wantAnchor requires the HQ not to be threatened.
- Rejected; g_iter0 resubmitted (submission 113, validated). Next: the same line with the HQ bounds, after the
  08:00 UTC autoscrim, once the baseline reports say whether the HQ threat lockout is new.

## 2026-10-07 23:55 — Why c_line4 lost quick wins: adamantium for the anchor rush; c_line5 queued

- Baseline reports (match_report on g_iter0's 10 panel matches) vs c_line4's: HQ enemy pressure is the same for both
  (2,628 vs 2,934 HQ-rounds per game near our HQs), idle funds the same (1,715 vs 1,604; opponents ~750). The HQ
  threat lockout is a standing weakness of both, not the cause of the drop (next arm: threat = real danger only).
- The flipped quick wins: at r150 g_iter0 banked 390-750 Ad and placed 2-5 anchors by r200-250 (conquest at
  r235-309); c_line4 banked 90-140 Ad (mana2 roles) and placed 1-2. Against mid-tier bots, the early anchor rush is
  worth more on the panel than the larger army mana2 buys against the top bots.
- c_line5 = the working line with the HQ siege bounds and g_iter0's balanced roles (C.ROLES = 0); src/bot keeps
  ROLES = 2 until the panel decides. Trial at 08:05 UTC, after the 08:00 autoscrim (a trial must end before the next).

## 2026-10-08 02:15 — Fight telemetry (c_line4 trial, 100 games, 62 engagements per game)

- Engagement win share 0.35 vs theirs 0.61; exchange ratio 1.20 vs 1.75; first hit 0.42 vs 0.58.
- By launcher difference at contact (dN = ours - theirs): dN=0 we win 0.31, they win 0.61; dN=+1 0.69 vs 0.78;
  dN=+2 0.73 vs 0.79; dN=-1 0.18 vs 0.22. The gap is micro, largest at parity.
- Move/fire classes: we step in and fire 0.155 of launcher-turns (them 0.107), stand and fire 0.198 (them 0.259),
  fire-and-retreat 0.096 (0.084). We walk into range and they shoot first.
- Next micro arm (after the role decision): at parity, hold just outside the enemy's reach and let them step in
  (stand-and-fire); step in only to finish a target or when ahead. Judged on the panel by win@dN=0 and first-hit rate.

## 2026-10-08 03:20 — Siege overruns found and fixed (spawn-safety scoring); parity-hold micro switch added

- A self-play siege (bot with C.MICRO2 vs c_line5, DefaultMap) reproduced the replica's HQ overruns: 6 in one game.
  Per-step profiling of HQ #7 (debug copy, r570-586): build() cost 15,500-18,000 bytecodes with 24-30 enemies in
  view, of which spawn-threat scoring alone 15,000 (29 tiles x fighters x ~21 bytecodes); it left the tile loop
  under its 3,500 guard, so the HQ could not build at all and then overran in telemetry or the fill.
- Fix: threat scored lazily, only for tiles where a build is possible (under a siege most spawn tiles are occupied),
  cached per turn, skipped when it would not fit. Same scenario after the fix: HQ max 17,923, 0 overruns, 0 near
  misses. c_line5 (on trial) predates this fix; the next candidate carries it.
- New switch C.MICRO2 (parity hold, off): unless ahead by 2+, a launcher does not step into more enemy reach to
  fire, and stays to fire when it can already hit (replica telemetry: we lose at parity 0.31 vs 0.61).

## 2026-10-08 05:50 — c_line5 rejected; self-play against g_iter0 finds the island regressions; c_line6 on trial

- c_line5 (balanced roles, partial siege guard) vs g_iter0 on panel v1: 28/100 vs 31 (identical 93, gained 2, lost 5,
  net -3, -1.13 SE); vs c_line4 net +3. Overruns 2.3 per game (c_line4 15.8). Quick wins by r400: 18 (g_iter0 24).
  Ad bank at r250 still -133 (t -6.0): more carriers built early (the live-robot bound replaced g_iter0's cap).
- Local self-play against g_iter0 (our own builds, CLAUDE.md rule 10) reproduces the regression, one cell Maze:
  working line + early cap: lost r287, anchors placed 2 vs 6 though Ad banked 446 vs 202. Telemetry (ANCH records):
  several carriers chased the same island and far targets (34 tiles; a loaded carrier moves every other turn).
  Fix 1: older island sightings (<= 60 rounds) fill EMPTY shared slots again (the audit's 8-round rule had kept
  them out): placed 4 vs 7, lost r413. Fix 2 test: cohesion off: WON r778, placed 8 vs 5.
- c_line6 = balanced roles, early carrier cap (g_iter0's 4 + round/40 per HQ until r300), lazy spawn scoring
  (siege fix), island-slot fill, cohesion OFF; trial now. c_line6a = the same with cohesion on, for a VM self-play
  suite against g_iter0 on the 10 panel maps, both sides (our builds only).

## 2026-10-08 06:15 — Self-play suite: cohesion off 15/20, on 7/20 against g_iter0

- VM self-play (our builds only), the 10 panel maps x both sides against g_iter0: c_line6 (cohesion off) 15/20,
  losses Forest x2 (r2000), BatSignal A, Cat B, MassiveL B; c_line6a (cohesion on) 7/20. Working line: C.ARMY = false.

## 2026-10-08 06:45 — c_line6 trial: even with g_iter0 (32 vs 31), not accepted; it becomes the working base

- c_line6 (balanced roles, early carrier cap, lazy spawn scoring, island-slot fill, cohesion off) on panel v1:
  32/100 vs g_iter0 31 (identical 91, gained 5, lost 4, net +1, +0.33 SE). Basics clean: 0 overruns, 0 exceptions.
  Delivered: Ad bank r250 back to g_iter0's level (+18), anchors placed +0.33 (t +2.3), launchers alive r100 +0.8
  (t +4.3) and r250 +1.4 (t +2.9), kills +7.6. Quick wins by r400 21 (g_iter0 24).
- Not accepted (no stacking on non-inferiority); g_iter0 resubmitted. The working line (src/bot) is c_line6: the
  next arms (HQ real-danger threat, parity-hold micro) build on it and pass the new pre-trial screen first
  (head-to-head vs the incumbent and an archetype roster; owner, PROMPTS 22-23; workflow building it now).

## 2026-10-08 07:50 — Local screens on c_line6 (20 pinned self-play cells vs g_iter0)

- c_line7t (HQ threatened only under real danger): 13/20 vs c_line6's 15/20 on the same cells (gained 1, lost 3);
  anchors placed -0.7 (t -2.0), island-rounds -385 (t -1.6). Fails the screen: building under nearby threat costs
  anchors. Closed for now (re-open: a version that withholds anchor builds only, not carriers).
- c_line7m (parity hold): 16/20 (gained 1, lost 0; 19 identical). Passes, but g_iter0's fights barely exercise the
  change; the archetype roster (swarm style) is the real test. Next replica trial after the 16:00 UTC autoscrim,
  once the full screen with archetypes has run.

## 2026-10-08 11:00 PDT — Local work: anchor gate (c_line8a) 18/20 vs g_iter0; on the ladder now

- Self-play losses of c_line6 against g_iter0 studied with full telemetry (local replays carry dots):
  - Forest (both sides, r2000): 188 anchors taken, 40 targets chosen, 147 timeouts after 150 turns, 4 placed:
    HQs built anchors whenever an island was unreported, and carriers took them with no target. Fix: C.ANCHOR_GATE
    (anchors only for located neutral islands; take one only with a target).
  - Cat (side B): our launchers lost the early fights (alive 7 vs 9 at r30, 1 vs 5 at r100); then 24 carriers died,
    most at one contested well cluster, fleeing or on their way; mana income froze at 213 from r100.
- c_line8a (c_line6 + anchor gate) on the 20 pinned self-play cells: 18/20 vs c_line6's 15/20 (gained 4, lost 1);
  anchors built 9.95 vs 21.45 (t -2.1), launchers alive r250 +1.4 (t +2.5), carriers lost 15.1 vs 28.5.
- Submitted as a trial at 11:00 PDT (owner, PROMPTS 32: submit whenever locally superior; ladder asynchronous).
  c_line7m's trial was ended at 5/10 matches (9/50 vs c_line6's 10/50); its remaining matches still report.
- In flight locally: c_line8b (8a without spawn safety; early-fight hypothesis), c_line8c (8a + danger-aware wells).

## 2026-10-08 11:35 PDT — Field-vs-field volume restored (owner, PROMPTS 33)

- vrangr1.AFinalsBot beats us 10-0 on the panel yet sat 77th on galaxy's displayed ladder: its rating mean is 1,567
  (13th of 88) but it had 7 rated matches, so the volume penalty (1500 x 0.85^7 = 481) dominates; median n was 15,
  min 5. Our own Bradley-Terry fit (progress/ELO.md) already ranks it 5th.
- Restored galaxy's 8-hourly autoscrim over every team and uncapped field activity in idle capacity; challengers are
  now weighted toward the low end of the displayed ladder (mostly under-played teams) so n grows where it is lowest.

## 2026-10-08 12:45 PDT — ACCEPT: c_line8a becomes the validated build (g_iter1)

- Panel v1 on the replica: c_line8a 33/100 vs g_iter0 31 (identical 90, gained 6, lost 4, net +2, +0.63 SE).
  Island-rounds margin +403 (t +2.44), launchers alive r250 +2.7 (t +5.5), kills +35 (t +4.3), anchors built -3.8
  (t -2.8, the gate working), carriers lost +9.5 (longer, more contested games); 0 overruns, 0 exceptions.
- Local: 18/20 vs g_iter0 on the pinned self-play cells (c_line6 15/20).
- Decision: accepted on the combination (local head-to-head, panel direction, consistent secondary signals) under
  the owner's operating model (PROMPTS 32: submit when superior, optimise time); the panel alone is not significant.
  Alias g_iter1 = c_line8a (code 83d878c19411, submission 120). Next candidates are screened against it.
- Also: c_line9a (launcher-first opening) 14/20 vs g_iter0 locally (c_line8a 18): worse against g_iter0; its runs
  against the swarm archetype are in progress (the opening targets swarm-style bots).

## 2026-10-08 13:45 PDT — Big swing: the swarm archetype as a candidate (c_swarm1)

- Locally the swarm archetype (our code, built from observed field behaviour: docs/ARCHETYPES.md 4.1, v4c, code
  b646f1e92c6b) beats g_iter0 19-1, c_line6 15-5 and the incumbent g_iter1 (c_line8a) 17-3, with 0 overruns and 0
  exceptions in 60 games. Its policies differ from our line in economy (mana-first roles, live-carrier census cap),
  opening (LLLL C, no amplifiers), anchors (none before r250), combat (focus fire, step in only 2+ ahead, killable
  targets) and siege (a ring at r2 16-34 of the enemy HQ, carrier raids).
- c_line9a (launcher-first opening on our line) delivered little: launchers alive r100 8.65 vs 8.30 against the swarm
  (5/20 vs c_line8a's 3/20) and 14/20 vs g_iter0 (c_line8a 18/20). Closed: the gap is the whole economy and fight
  model, not the build order.
- c_swarm1 = a frozen copy of arch_swarm v4c, on trial now (owner, PROMPTS 32: submit what is locally superior).

## 2026-10-08 17:00 PDT — ACCEPT: c_swarm1 becomes the validated build (g_iter2)

- Panel v1: c_swarm1 40/100 vs g_iter1 (c_line8a) 33: identical 79, gained 14, lost 7 (net +7, +1.53 SE); vs g_iter0
  net +9 (+2.32 SE, sign p 0.035). Delivered: Mn r100 +192 (t +14.8), launchers alive r100 +5.8 (t +17.1) and r250
  +15.9 (t +13.7), kills +19 (t +2.3); 0 overruns, 0 exceptions. Weakness: island-rounds -396 (t -2.8).
- Local: 17-3 vs g_iter1, 19-1 vs g_iter0; 13/20 vs arch_blob, 14/20 vs arch_adecon.
- Against vrangr1 it is now 1-9 (every earlier build 0-10): mana at r100 close to theirs on most maps, games decided
  late by island conquest. Next: islands (c_swarm2 = c_swarm1 + anchor gate, queued locally).
- Tooling found on the way: the block collector compared match maps in request order (the API lists them
  alphabetically) and scanned only 5 pages; both fixed.

## 2026-10-08 17:15 PDT — c_swarm2 (swarm + anchor gate) closed

- c_swarm2 vs g_iter2 (c_swarm1) head-to-head: 8/20; vs g_iter1: 15/20 (c_swarm1 17/20). The gate does not help the
  swarm, whose anchors start late anyway. Next: c_swarm3 (anchors from r150 at 8 launchers) on the same cells.

## 2026-10-08 18:30 PDT — c_swarm3 closed; commit-margin arms c_swarm4a/b

- c_swarm3 (anchors from r150 at 8 launchers): 6/20 vs g_iter2, 14/20 vs g_iter1 (g_iter2: 17). Earlier anchors
  hurt the swarm. Closed.
- Replica vs awesomelemonade (g_iter2, 0-10): even economy and launcher counts at r100, but engagements won 18% vs
  76%, first hit 22% vs 78%, exchange 0.49 vs 2.2. Their launchers stand and fire 37% of turns (ours 17%); ours hold
  (no move, no fire) 41% (theirs 27%): the parity hold keeps ours out of the fight unless 2+ ahead.
- c_swarm4a (commit when 1 ahead) and c_swarm4b (commit at parity), on the local cells vs g_iter2 and g_iter1.

## 2026-10-08 18:40 PDT — archetype roster and pre-trial screen landed
- Workflow (10 agents): five archetypes from replica replays only (arch_swarm, arch_blob, arch_adecon, arch_horde,
  arch_ampmid), the screen `tools/screen.py`, the trial-start gate in `tools/ladder_policy.py`, build provenance
  (`HASHES=1` code hashes, `seed_mode`, `opp_hash.*` in provenance.txt).
- Verifier: no rule breach (no field code, sources are replays and match reports, local opponents only ours).
  Fidelity: swarm INVALID (fights at prog 0.44 vs members 0.27-0.35; Mn@100 396 vs 492-618), adecon 8/11 core
  metrics, blob 8/11 plus 2 overruns (wins from an early lead where its member wins from behind), horde throws half
  the member's, ampmid passes only on a float boundary and descends from our code. Strength vs g_iter0 is close to
  the members' for all five. Fixed in screen.py: a --roster override now writes a reduced record; calibrate's share.
- Dry run: c_line6 vs c_line8a, 2 maps, PASS (reduced). A full screen is about 108 candidate games + 80 incumbent
  games once per incumbent hash, about 1.5 h.
- Open: tools/archsig.py (VALID records; needs an epsilon), lineage-aware own-style flag, a faster swarm archetype
  (S1 = 149 of our 284 panel losses, slot empty since arch_swarm became g_iter2), identity control and backtest.

## 2026-10-08 19:00 PDT — c_swarm4a/b closed; the panel says economy, not the first hit; arms c_eco1/2
- c_swarm4a (commit at +1): 6/20 vs g_iter2, 17/20 vs g_iter1 (g_iter2 17). c_swarm4b (commit at parity): 8/20 vs
  g_iter2. Committing earlier loses in self-play. Closed.
- New extractor columns (engagements.csv fh_*: how the first hit was fired, whether the victim had just moved, the
  pair's range history, clouds, ids). On g_iter2's panel (matches 1017-1026), launcher-vs-launcher engagements before
  r400 without spawn kills: we land the first hit in 0.55-0.72 against every opponent (awesomelemonade 0.55). The
  earlier "first hit 22%" counted spawn kills under late sieges. Before r400 we win 0.59-0.64 of engagements against
  vrangr1, jmerle, georgezhang and NotLLeon, 0.50 against pranayagra, 0.20 against awesomelemonade (n0 2.3 vs 4.6:
  they meet us with twice the launchers; their group_p50 19 vs our 6, focus 0.62 vs 0.33, kill_conv 1.00 vs 0.60).
- The losses are economic. Per 100 rounds, over games alive at the segment end (all 10 matches): carriers built ours
  7, 5, 3, 4 (r100-500) against 8, 10, 10, 12; live carriers r300 19/23, r500 14/42, r700 11/65; Mn collected r400-500
  304 vs 935; Ad r0-100 70 vs 184 (our Ad is 14% of our Mn; theirs 46%). HQ build-loop exits: mid game poor 38%,
  carrier withheld under threat 24%, anchor reserve 18%, cap 8%; late game threat 58%.
- Arms (from c_swarm1): c_eco1 = carrier cap 10 per known Mn well, 8 per HQ growing one per 30 rounds, max 60 (was 8,
  6 per 50, 30). c_eco2 = c_eco1 plus more adamantium: AD_NEED 100, one carrier in 4 early, one in 3 from r150 (was 50,
  8, 4 from r200).

## 2026-10-08 20:45 PDT — c_eco1/2 closed; c_nav3 (distance fields) for the owner's navigation report
- c_eco1 (carrier cap x2): 5/20 vs g_iter2, 16/20 vs g_iter1. c_eco2 (cap + more Ad): 7/20 vs g_iter2, 13/20 vs
  g_iter1. Closed: the cap bound only 8% of HQ turns (threat 24%, poor 38%); more carriers bought fewer anchors and,
  with more Ad carriers, fewer launchers, and self-play is decided on islands (14 of 20 h2h-swarm4a games by 75%).
- Owner (PROMPTS 35): launchers pooled doing nothing in the lower-left of Target (match 1208 vs BrysonJGalapon.aloha,
  game 1). Replay: 8 of our launchers marched into the dead end of the west-edge corridor (0,13)-(0,18) toward the
  predicted enemy HQ due north and stood 50-317 rounds in march mode; 20+ others idled 40-150 rounds forming up at
  home (GROUP_MIN 4 with few launchers built); carriers stood 60-100 rounds. Reproduced in local self-play on Target.
  Cause, from the local game's BUG/OBJ records: greedy steps lead into any pocket that points at the target; cohesion
  (regroup/follow) switched targets and reset the wall-following state, so a launcher that had wall-followed out came
  back; in a crowded pocket two edge flips stopped wall-following for good; followers trailed a stuck leader.
- c_nav3 (from c_swarm1): src/c_nav3/Field.java, a breadth-first distance field per robot toward one target over 64-bit
  wall rows (sensed walls plus their symmetric images; unknown open; HQ squares blocked), built a row at a time in the
  bytecodes left at the end of each turn; a marching launcher plans its team target from its first turn; Nav descends
  the field (downhill, else wait 2 turns, sidestep, then step back every other turn), falls back to greedy and
  wall-following while no field covers it; a field is rebuilt only when a downhill square proves to be a wall; a
  wall-hit request never replaces a young, in-use or nearby field; no permanent stall at the map edge; forming at home
  waits at most 15 move-ready turns.
- Local, Target, c_nav3 vs c_swarm1 (seed 1): launchers still >= 40 rounds 9 of 199 vs the incumbent's 57 of 148
  (first version); final version wins by 75% islands at r640-797 (the v1 game went to r2000; self-play c_swarm1 r816);
  remaining: late-born launchers can still reach the pocket before their field covers it (about 25 turns lost), and
  carrier queues at the HQ. 0 overruns; launcher mean bytecodes 7,200 (field work) vs 2,500.

## 2026-10-08 21:15 PDT — c_nav3 borderline locally; c_nav3a isolates the forming cap
- c_nav3: 9/20 vs g_iter2 (screen BORDERLINE), 16/20 vs g_iter1 (g_iter2: 17). Wins BatSignal, Cat, Forest on both
  sides; loses both sides of Maze (r402-420), Hah, IslandHopping, DefaultMap. In those losses c_nav3 has fewer
  launchers at r100 (13/18, 7/9, 12/16, 6/12) and loses the launcher war (IslandHopping: 17 of its carriers killed by
  r300 against 0); Maze A also had no adamantium carrier after r200 (roles go by id % 4: with ~10-17 carriers a team
  can draw none, a flaw the incumbent shares).
- c_nav3a = c_nav3 with the forming wait uncapped (as g_iter2): on Target it still wins by 75% islands at r760, one
  launcher held 45 rounds in march mode (incumbent: two for 840), forming idle 10 launchers / 518 rounds (incumbent
  12 / 972). h2h queued.

## 2026-10-08 22:35 PDT — Identity control: the self-play head-to-head cells favour the incumbent's seat 16-4
- c_swarm1id (g_iter2's code under another package, same code hash) vs c_swarm1 on `test/cells/self-swarm1-panel.txt`:
  4/20 (2/10 as A, 2/10 as B). Our randomness is seeded by robot id only, so these mirror games are fixed by the seed:
  the 20 pinned seeds give the opponent seat 16 wins (p = 0.006 for fair coins). 10/20 is not the neutral mark on
  these cells; every arm today must be read paired, cell by cell, against the identity run.
- Re-read: c_swarm2 8, c_swarm3 6, c_swarm4a 6, c_swarm4b 8, c_eco1 5, c_eco2 7, c_nav3 9, c_nav3a 8, c_nav4 7,
  c_role1 6, against identity 4. Paired vs identity: c_nav3 gains 7 cells, loses 2 (net +5, 1.7 SE); c_nav4 gains 5,
  loses 2 (net +3). Earlier closures today were decided on a bar that was wrong; none of them is a measured
  regression either (20 games resolve about +-4).
- vs g_iter1 (`self-g_iter1-panel.txt`, no identity yet): c_nav4 17/20, c_nav3 16, g_iter2 17.
- c_nav4 = c_nav3 with fields descended only after greedy hits a wall toward their target (sticky per target) and
  immediate sidesteps: Target r739 win, few stalls. c_role1 = adamantium role by (id + trips) % k: 6/20.
- The pre-trial screen's stage (b) bar (PASS at 11/20) assumed 10 neutral. Queued: the full screen for c_nav4 and an
  identity screen (c_swarm1id, --allow-identity, --roster none) to measure the baseline on the screen's own cells.

## 2026-10-09 01:20 PDT — c_nav4 screen PASS; replica trial started (submission 122)
- Screen (progress/screens/c_nav4-9f333d33cf78.json): basics 8/8, h2h 12-8 on the screen's map-seed cells, roster
  information only (no VALID archetype): adecon +0, ampmid +2, blob -1, horde +0 (Net +1), 108 games with 0 overruns,
  0 exceptions, 0 self-deaths. The identity screen on the same cells (c_swarm1id) runs next for the stage-(b) baseline.
- Trial: tools/ladder_policy.py trial-start c_nav4 at 01:20 PDT, panel v1 requested (10 x 10); it queues behind the
  01:00 autoscrim round; next autoscrim 09:00 PDT. Baseline: g_iter2 40/100 (gauntlet/20261008-210429-panel1-c_swarm1).

## 2026-10-09 01:30 PDT — Identity screen: the screen's own cells are seat-neutral (10/20)
- c_swarm1id on the screen's map-seed cells: basics 8/8, h2h 10/20 (record progress/screens/c_swarm1id-b646f1e92c6b.
  reduced.json, identity control ok). So the screen's stage-(b) bar (PASS at 11) is centred; the 16-4 seat bias is a
  property of `test/cells/self-swarm1-panel.txt`'s pinned seeds only.
- c_nav4 vs identity on the same cells, paired: gained 6, lost 4 (net +2, inside noise). Locally neutral to slightly
  positive; the replica panel decides.
- Queued: c_hq1 = c_nav4 + carriers built under threat on spawn tiles no visible enemy fighter reaches (h2h-hq1).

## 2026-10-09 02:15 PDT — c_hq1 locally neutral
- c_hq1 (c_nav4 + carriers under threat on safe spawn tiles): 8/20 vs g_iter2 on the h2h cells; paired against c_nav4's
  run on the same cells only 3 cells differ (Cornucopia A -1, Cornucopia B +1, DefaultMap A +1): net +1. In self-play
  the HQs are rarely threatened early enough for the change to matter; it targets sieges by stronger field bots, so it
  is a candidate for a later replica trial rather than a local verdict.
- c_nav4 trial: the 10 panel matches wait behind the 01:00 PDT autoscrim round (none started at 02:13 PDT).

## 2026-10-09 04:15 PDT — c_nav4 accepted: g_iter3 (panel 48/100, net +8 over g_iter2)
- Panel v1 (gauntlet/20261009-082005-panel-c_nav4) vs g_iter2's (20261008-210429-panel1-c_swarm1): 100 cells matched,
  88 identical, 10 gained, 2 lost: net +8 (+2.31 SE), sign test p 0.039; island-rounds +233 (t +1.6). Per match:
  vrangr1 0-10 (g_iter2 1-9), jmerle 3-7 (2-8), georgezhang 6-4 (3-7), awesomelemonade 1-9 (0-10), pranayagra 3-7
  (2-8), NotLLeon 5-5 (4-6), Sprint1 7-3 (5-5), reeceyang 7-3 (8-2), yaonam 9-1 (9-1), britacatalin 7-3 (6-4).
- trial-end --accept at 04:14 PDT: g_iter3 = c_nav4 (submission 122, hash 9f333d33cf78); ranked loop back in BURST.
  Navigation (owner, PROMPTS 35) was worth more on the panel than any economy or fight arm tried since g_iter2.
- Next: c_hq1 and c_grp1 (both on c_nav4, locally neutral to slightly positive) go through the screen against g_iter3.

## 2026-10-09 04:45 PDT — c_grp1 fails the screen against g_iter3 (h2h 7-13)
- c_grp1 (formations of 6, wait up to 25 turns) vs c_nav4 on the screen's seat-neutral cells (identity 10/20): 7-13,
  stage (b) FAIL, screen stopped. Bigger home formations cost more than they buy in self-play; closed. The group-size
  gap to awesomelemonade (19 vs 6) needs a different mechanism than waiting longer at home.

## 2026-10-09 05:15 PDT — c_hq1 fails the screen (h2h 8-12); c_role2 queued
- c_hq1 (carriers under threat on safe spawn tiles) vs g_iter3 on the screen cells: 8-12, stage (b) FAIL; closed.
- c_role2 = g_iter3 + the per-trip adamantium rotation of c_role1 (no team without adamantium carriers): screen queued.
- Ranked loop at the hourly limit (429) in BURST for g_iter3; it retries.

## 2026-10-09 07:15 PDT — c_role2 fails the screen (h2h 10-10, roster Net -5)
- c_role2 (g_iter3 + per-trip adamantium rotation) vs g_iter3: basics 8/8, h2h 10/20 BORDERLINE, roster information
  Net -5 (arch_ampmid 13 -> 9, -4 regression flag), 128 games clean. FAIL (BORDERLINE without a roster gain); closed.
- Three arms on g_iter3 failed the screen (c_grp1 7-13, c_hq1 8-12, c_role2 10-10 / -5). Next: mine g_iter3's
  replica games for remaining basics failures (stalls, idle funds, symmetry) before more economy or grouping arms.

## 2026-10-09 07:30 PDT — Basics: g_iter3 overran 3 launcher turns; c_nav5 bounds the field lookup
- g_iter3's replica panel: 3 overruns in match 1811 game 2 (Cornucopia vs georgezhang, launchers aged 10-50,
  r1801-1979, 10,000-10,010 bytecodes); g_iter2's panel had none. The only unguarded addition in the turn's own work
  is Field.level: on a cache miss it scanned up to 400 waves (~10 bytecodes each).
- c_nav5 = g_iter3 with Field.level searching outward from the cached wave and stopping under C.FIELD_LEVEL_GUARD
  (3,000) bytecodes left, and the field descent skipped below the same guard. Target locally: win r812, 0 overruns.
  Screen queued; trial after the 09:00 PDT autoscrim if it passes (decisions otherwise unchanged).

## 2026-10-09 08:28 PDT — Scrimmages paused for local games (owner, PROMPTS 36)
- VM load average was 14 on 8 vCPU (saturn's 7 engines plus the screen). Stopped the field activity, disabled the
  autoscrim timer (the 09:00 PDT round will not fire) and stopped our ranked loop. saturn keeps running (7 matches in
  flight, none queued), so a trial can still play its panel. Resume commands in HANDOFF.md (Standing).

## 2026-10-09 08:50 PDT — c_nav5 trial started (submission 123) with logged overrides
- Screen c_nav5 vs g_iter3: basics 8/8, h2h 10-10, roster 99 of 100 cells identical (blob +1), 128 games with 0
  overruns and 0 exceptions: no regression; formally BORDERLINE without a +2 roster gain, as expected for a guard-only
  change. trial-start --skip-screen (reason in the history) --force (autoscrim timer paused by the owner, PROMPTS 36-37).
- Plan (owner, PROMPTS 37: c_nav5 in before the autoscrim): judge the panel against g_iter3's
  (gauntlet/20261009-082005-panel-c_nav4), accept if no regression, then fire the missed 09:00 PDT autoscrim round by
  hand (the relay fires only on the cron minute, no catch-up), re-enable the timer, restart field activity and the
  ranked loop.

## 2026-10-09 09:28 PDT — c_nav5 accepted (g_iter4); overruns NOT fixed; scrimmages resumed
- Panel (gauntlet/20261009-155042-panel-c_nav5) vs g_iter3's: 100 of 100 cells identical (48/100), net 0.
- The 3 overruns recur identically (match 2124 game 2, Cornucopia vs georgezhang, r1801 launcher 11274 age 10, r1811
  same launcher age 20, r1979 launcher 12789 age 50; 10,000-10,010 bytecodes): Field.level was not the cause.
  Accepted anyway (no regression, a strictly safer lookup) so the autoscrim plays it (owner, PROMPTS 37). Cause open.
- Resumed at 09:28 PDT: the missed 09:00 autoscrim round fired by hand (relay fire-jobs --force -> 204; 169 queued),
  timer re-enabled, field activity and the ranked loop restarted.

## 2026-10-09 10:12 PDT — Overrun cause found: fight() in a crowd of 48 enemy carriers; c_nav6
- Match 2124 game 2 (identical to 1811): launcher 11274 in fight mode every turn at 8,600-9,900 bytecodes from r1792,
  overran at r1801 and r1811; launcher 12789 at ~8,830 a turn for 50 rounds, then 9,100-10,010. Within r2 20 of
  11274 at r1800: 48 enemy carriers (georgezhang's carrier swarm), 1 own launcher, 1 own carrier. fight() scores 9
  tiles against every visible enemy (~6,500 bytecodes for 48), its 2,000 guard left too little for the second shot
  (shoot scans all enemies again) and the end of the turn. track() (32 x 32 matching, telemetry only) is bounded too.
- c_nav6 = g_iter4 + fight() scores every fighter and HQ but at most 10 non-fighters, guard 2,500; shoot() takes its
  best target so far under 1,500 left; track() at most 12 fighters and only with 6,000 left. Local: Target win r1490
  vs c_nav5, Forest stress game (2,000 rounds) 0 overruns both sides (self-play crowds stay smaller). Screen queued.

## 2026-10-09 10:20 PDT — Diagnosis workflow on g_iter3; three arms being built
- research/diagnosis/2026-10-09-g_iter3.md (4 lenses + judge, read-only on the replica panel and ranked games). Key:
  the r200+ stall is where resources go, not how much we gather. In losses we build 12.4 anchors, place 2.2 and lose
  9.5 (77%, 39% with no target, couriers never flee); anchors take 27% of mid-game Mn spend and 53% of Ad; Ad banks
  at besieged HQs (passive income they cannot spend). A gate "no anchor while any HQ is pressed (pressure34 >= 100 in
  this or the previous 25-round bucket) or the enemy holds more islands" blocks 53% of anchors in losses vs 7% in
  wins. Home raids before r300 are lost 1 vs 3-4 while 8-22 launchers are elsewhere. Cloud maps: launchers regroup
  mid-fight (cannot see allies in clouds) and never fire blind.
- Judge's ranking: 1 c_anc3 (anchor gate + located targets + island scout + couriers that flee + Ad bank cap), 2 c_def2
  (HQ raid alarm, recall our-half launchers before r600), 3 c_cloud1 (hold on recent contact, blind shot at a
  vanished enemy's tile). The judge also confirmed the overrun cause as the fight path (c_nav6). All three are being
  implemented on c_nav6 by an implement/review workflow; screens and replica trials follow.

## 2026-10-09 10:50 PDT — c_anc3, c_def2, c_cloud1 implemented and reviewed (on c_nav6)
- Implement/review workflow (wf_1e0fbff5-a9e, 6 agents, compile-only): c_anc3 (anchor gate on HQ pressure / island
  deficit via slot-61 bits 4-7, located targets, island scout id % 16 == 1, couriers flee/return, Ad bank cap 150);
  reviewer fixed a missed ANCH timeout record and stale anchor state after a throw. c_def2 (HQ raid alarm in slot 56,
  recall of launchers within r2 225 nearer the HQ than the siege target before r600): ready as written. c_cloud1
  (hold on recent contact, cloud-aware regroup, blind shot at a vanished fighter's unsensable tile); reviewer fixed the
  ghost choice (nearest qualifying tile) and kept the hold out of enemy HQ auras. Build tag of c_anc3 set to 101 (102
  is arch_adecon's). Unit tests PASS. Specs: research/diagnosis/2026-10-09-g_iter3.md.

## 2026-10-09 12:15 PDT — c_nav6 screen PASS; replica trial started (submission 124)
- Screen vs g_iter4: basics 8/8, h2h 11-9, roster 99 of 100 cells identical (adecon -1, swarm +1/-1), 128 games with
  0 overruns and 0 near misses (c_nav4's screen: near 5, c_role2's: 41). Trial started 12:14 PDT; judge against
  gauntlet/20261009-155042-panel-c_nav5; the georgezhang Cornucopia cell (2124 g2) must show 0 overruns.
- Screens queued behind it: c_anc3 (running), c_def2, c_cloud1.

## 2026-10-09 13:15 PDT — c_nav6 accepted (g_iter5): overruns gone on the replica, panel net -2 (noise)
- Panel (gauntlet/20261009-191411-panel-c_nav6) vs g_iter4's: 98 of 100 cells identical, 0 gained, 2 lost (Sprint1,
  britacatalin; net -2, -1.41 SE, sign test p 0.5); 46/100. Overruns 0 in all 100 games, including the georgezhang
  Cornucopia cell (2332 g2) that overran 3 times under g_iter3/4. Accepted on the basics bar (zero overruns), the
  cost inside noise. c_anc3, c_def2 and c_cloud1 are built on c_nav6.

## 2026-10-09 14:15 PDT — c_anc3 screen PASS (roster Net +16); replica trial started (submission 125)
- Screen vs g_iter4 (c_nav5): basics 8/8, h2h 12-8, roster information Net +16 (gained 18, lost 2: adecon 16->20,
  ampmid 13->15, blob 14->17, horde 9->14, swarm 12->14), 128 games with 0 overruns, 0 exceptions (near misses 32,
  carriers' island loops; watch). The largest local gain of any arm against the roster.
- Trial: trial-start --skip-screen (the record is against c_nav5; g_iter5 c_nav6 was accepted during the screen and
  plays 98/100 panel cells identically). Started 14:14 PDT, 2 h 46 before the 17:00 autoscrim; replica queue 2 + 7.
  Judge against gauntlet/20261009-191411-panel-c_nav6 and the judge's mechanism metrics (anchors built/lost in
  losses, 'a' share, launchers built r251-600, ReverseFunnel).

## 2026-10-09 15:15 PDT — c_anc3 accepted (g_iter6): panel 57/100, net +11 over g_iter5 (p 0.003)
- Panel (gauntlet/20261009-211419-panel-c_anc3) vs g_iter5's: 87 identical, 12 gained, 1 lost: net +11 (+3.05 SE),
  sign test p 0.0034; island-rounds +84. Per match: vrangr1 1-9 (0-10), jmerle 4-6 (3-7), georgezhang 5-5 (6-4),
  awesomelemonade 2-8 (1-9), pranayagra 4-6 (3-7), NotLLeon 5-5 (5-5), Sprint1 10-0 (6-4), reeceyang 9-1 (7-3),
  yaonam 9-1 (9-1), britacatalin 8-2 (6-4). 0 overruns, 0 exceptions.
- Mechanism (census, per game, c_anc3 vs c_nav6 panels): anchors lost in losses 1.2 vs 10.7, in wins 0.9 vs 4.5;
  anchors placed in wins 5.0 vs 5.5 (kept); carriers built in losses 62.5 vs 49.3; launchers built in wins 151 vs 108.
  The diagnosis' anchor-waste finding (research/diagnosis/2026-10-09-g_iter3.md) held on the replica.
- trial-end --accept 15:14 PDT: g_iter6 = c_anc3 (submission 125). Next: c_def2 and c_cloud1 rebased onto c_anc3.

## 2026-10-09 15:30 PDT — c_cld2, c_def3: the cloud and raid-recall arms rebased onto g_iter6
- c_cld2 = c_anc3 + c_cloud1's Launcher.java and its two constants (c_anc3 did not touch Launcher). c_def3 = c_anc3 +
  the c_nav6 -> c_def2 patch (C, Comms, HQ, Launcher); one hunk (the Comms constants line) merged by hand (ALARM = 56
  beside c_anc3's PRESS_SHIFT); every island loop stops at id 35, so slot 56 stays the alarm's. Unit tests PASS.
  c_cloud1's standalone screen against c_nav5 was cancelled; c_def2's finishes for information. Screens queued.

## 2026-10-09 17:50 PDT — c_cld2 fails the screen against g_iter6; c_def2 standalone roster -6
- c_cld2 (g_iter6 + cloud fighting) vs c_anc3: h2h 9-11 BORDERLINE, roster information Net +1 (horde +3, adecon -2),
  128 games clean. FAIL; closed for now (its expected effect was small and local to cloud maps).
- c_def2 standalone (vs c_nav5, recorded for information): h2h 11-9 but roster Net -6 (2 gained, 8 lost; four of five
  styles worse). c_def3 (the same on g_iter6) is being screened now; a repeat of that pattern closes the recall idea.

## 2026-10-09 19:40 PDT — c_def3 screen PASS, trial started (submission 126); g_iter6 diagnosis; arms being built
- c_def3 (g_iter6 + raid recall) vs c_anc3: basics 8/8, h2h 11-9, roster Net 0 (the standalone c_def2 had -6), 128
  games clean. Replica trial started 19:38 PDT; judge against gauntlet/20261009-211419-panel-c_anc3.
- research/diagnosis/2026-10-09-g_iter6.md (4 lenses + judge on panel 2430-2439 and ranked). Anchor drain fixed; left:
  the carrier fleet stops growing at ~r150 (r400 gap 23 = 14.8 not built + 8.2 extra killed); a carrier that fled
  walks back to the same well and dies on 46-72% of those trips (no-flee trips 2-4%); 34% of carriers are born
  during a fight near their HQ; MassiveL/Forest home mana wells never found or re-picked; 931 launcher deaths to
  enemy HQ auras on the panel (followers walk in, none can walk out). Judge's ranking: 1 c_flee2 (carriers remember
  the raid they fled), 2 c_well3 (home mana-well probe + re-pick at deposit), 3 c_aura1 (aura-safe movement).
  Implement/review workflow running on c_anc3.

## 2026-10-09 20:05 PDT — c_flee2, c_well3, c_aura1 implemented and reviewed (on c_anc3)
- Workflow wf_682bf1fd-0d0 (6 agents, compile-only), specs in research/diagnosis/2026-10-09-g_iter6.md.
  c_flee2 (carriers hold near home after a flee, drop the raided well, avoid wells near fresh sightings, flee to a
  safe HQ): reviewer cut the worst hold-turn scan from ~12k to ~7.7k bytecodes (avoided() only on nearer candidates,
  pickWell(-role)) and reset offRole. c_well3 (one carrier per HQ probes 5 points for a home mana well, re-pick a
  nearer well at deposit; slot 61 bits 8-11 as probe claims): ready as written. c_aura1 (launchers inside an enemy
  HQ aura may only step outward; regroup moves avoid auras; fight() prefers the outermost aura tile): reviewer raised
  the outward weight (C.AURA_OUT_W 2,000,000) so a deeper tile can never tie with standing still.
- test/bot/AuraStepTest.java: the 7 aura-step cases. Unit tests PASS. Screens queued.

## 2026-10-09 21:40 PDT — c_def3 accepted (g_iter7): panel 60/100, net +3 over g_iter6, gains on vrangr1
- Panel (gauntlet/20261010-023758-panel-c_def3) vs g_iter6's: 95 identical, 4 gained, 1 lost: net +3 (+1.34 SE, sign
  test p 0.375); island-rounds +191 (t +1.66). Gains vrangr1 +3 (4-6 vs 1-9, the raiding team the recall targets),
  georgezhang +1; loss jmerle -1. 0 overruns, 0 exceptions. Accepted at the judge's bar (net >= +2): weaker evidence
  than c_anc3's, but mechanism-consistent and nearly free (95 cells identical).
- g_iter7 = c_def3 (submission 126). c_flee2, c_well3 and c_aura1 are built on c_anc3: rebase onto c_def3 before
  their trials (their screens compare against c_anc3, 95/100 identical on the panel).

## 2026-10-09 22:00 PDT — c_well4, c_aura2: c_well3 and c_aura1 rebased onto g_iter7 (c_def3)
- Patches c_anc3 -> c_well3 and c_anc3 -> c_aura1 applied to copies of c_def3; one hunk (c_aura1's march() step-out,
  anchored on the telemetry line c_def3 changed) inserted by hand; launcher additions complete (21 lines each).
  Unit tests PASS. Their pending screens against c_anc3 cancelled; c_flee2's running screen finishes, then rebases.

## 2026-10-09 23:10 PDT — c_flee2 screen PASS (vs c_anc3); rebased as c_flee3 on g_iter7
- c_flee2 vs c_anc3: basics 8/8, h2h 12-8, roster information Net +3 (horde +2, ampmid +1, blob +1, adecon -1),
  128 games with 0 overruns, 0 exceptions, but 83 near misses (carrier well scans): watch carrier bc_max on the replica.
- c_flee3 = c_def3 + the c_anc3 -> c_flee2 patch (C, Carrier, Comms, HQState), applied cleanly; added-line counts equal
  per file. Unit tests PASS. Screen queued after c_well4 and c_aura2. Next trial window: after the 01:00 PDT
  autoscrim (until 06:30); the strongest of c_flee3 / c_well4 / c_aura2 goes first.

## 2026-10-09 23:55 PDT — Replica: a stuck ranked match blocked our rating chain for 7 hours; fixed
- Our displayed rating sat at 1582.1 from 17:48 PDT. Match 2565 (ranked, c_anc3 vs battlecode-archive.sprintBot,
  Buggy/Crossword/Spots, created 16:45 PDT) timed out at the replica's 1800 s per-game limit on each of 4 attempts
  (~540 robot threads, engine at ~45% CPU on the shared VM); saturn nacks errored tasks, so it was redelivered for
  ever and, still RUN, blocked every later rating (siarnaq rates a team's matches in creation order): 20+ finished
  ranked matches were unrated.
- Staff actions (galaxy's own admin actions): Cancel tasks + Recalculate ratings on 2565 (a finalized non-completed
  match counts as unranked); the chain resumed at once (rating 1594.1, catching up). GALAXY_GAME_TIMEOUT raised to
  7200 s (live env and tools/galaxy/deploy/galaxy-setup.sh; real saturn has no per-game limit); saturn restarted
  (in-flight matches redelivered). Documented in docs/galaxy/README.md (deviations).
- Our launchers now spend most of their bytecodes every turn (distance fields, end-of-turn fill), so big games are
  slower to simulate; harmless in the real contest (no wall-clock limit), but it lengthens replica matches.

## 2026-10-10 01:00 PDT — c_well4 closed: screen FAIL and the probe did not fire on MassiveL
- c_well4 vs c_def3: h2h 10-10 BORDERLINE, roster +1, 128 games clean: FAIL. Local MassiveL game (seed 786634174,
  c_well4 as A with HQs (7,5) and (2,37)): all 331 of A's mana deposits at (0,39), none at (7,5)'s well (2,0). The
  probe/re-pick did not take; debug before any re-screen (the judge's verify: (2,0) collected by ~r150).

## 2026-10-10 01:03 PDT — c_flee3 trial started (submission 127)
- trial-start --skip-screen: screened as c_flee2 against c_anc3 (h2h 12-8, roster +3, 0 overruns; near misses 83, so
  watch carrier bytecodes); c_flee3 = the same patch on g_iter7. Started after the 01:00 autoscrim fired (176 matches,
  bound to c_def3); the panel queues behind them. Judge against gauntlet/20261010-023758-panel-c_def3 (60/100).

## 2026-10-10 02:45 PDT — c_aura2 screen PASS (h2h 13-7)
- c_aura2 (g_iter7 + aura-safe launcher movement) vs c_def3: basics 8/8, h2h 13-7, roster information Net +2 (ampmid
  +3, horde -1), 128 games with 0 overruns, 0 exceptions (near misses 58). Next trial after c_flee3's: on c_def3 if
  c_flee3 is rejected, rebased onto c_flee3 if it is accepted.

## 2026-10-10 03:45 PDT — Replica: second slow sprintBot match cancelled; our rating 1594 -> 1639
- Match 2593 (autoscrim, pranayagra.finalbotfinaltwo vs battlecode-archive.sprintBot, 17:00 PDT) was the only
  non-final match left blocking the rating chain (ours waited at 2832 behind it); re-run from scratch after the
  saturn restart and ~3.75 h into its attempt. Staff Cancel + Recalculate ratings: our backlog of c_anc3/c_def3 ranked
  results finalized, rating 1594.1 -> 1639.0. sprintBot's games are the slow ones (~540 robots); watch for more.

## 2026-10-10 05:15 PDT — c_flee3 rejected (panel 56/100, net -4); c_aura2 trial started (submission 129)
- c_flee3 panel (gauntlet/20261010-080243-panel-c_flee3) vs g_iter7's: 94 identical, 1 gained, 5 lost: net -4
  (-1.63 SE, p 0.22); 56/100. Losses britacatalin -2, awesomelemonade, pranayagra, reeceyang; gain jmerle. 0 overruns.
  Its screens (h2h 12-8, roster +3/+4) did not carry to the field: carriers holding near home after a raid cost more
  against strong teams than the trips they saved. trial-end --reject: c_def3 resubmitted (submission 128).
- c_aura2 (aura-safe movement; screen h2h 13-7, roster +2) trial started 05:14 PDT, 3 h 46 before the 09:00 autoscrim;
  judge against gauntlet/20261010-023758-panel-c_def3 and the aura deaths per game.

## 2026-10-10 06:15 PDT — c_aura2 accepted (g_iter8): panel 62/100, net +2; aura deaths 1,227 -> 35
- Panel (gauntlet/20261010-121416-panel-c_aura2) vs g_iter7's: 96 identical, 3 gained (NotLLeon, georgezhang, jmerle),
  1 lost (reeceyang): net +2 (+1.00 SE, p 0.63); island-rounds +205 (t +2.05). Our launchers killed by enemy HQ auras
  over the 100 games: 35 vs 1,227. 0 overruns, 0 exceptions. Accepted: a movement-basics fix with a measured
  mechanism, at the judge's bar (net >= +2).
- g_iter8 = c_aura2 (submission 129). c_flee3 rejected earlier tonight; c_well4 closed.

## 2026-10-10 08:30 PDT — g_iter8 diagnosis; building c_well5, c_spread2, c_scout1
- research/diagnosis/2026-10-10-g_iter8.md. Judge's ranking: 1 c_well5 (the home mana-well probe made reliable plus
  the re-pick at deposit: c_well4's own screen census shows MassiveL Mn@250 1,406-1,553 vs 739-771 in the 6 of 10 cells
  where the probe fired, Forest 5 of 10; I closed c_well4 on one local game where it happened not to fire), 2 c_spread2
  (surplus launchers at a saturated siege ring press the other enemy HQs: Cornucopia 3/10 in every build, the free HQs
  build 42-82 launchers in r200-500 while 15-29 of ours camp one HQ), 3 c_scout1 (a claimed, replaceable island
  scout: first anchor r400-450 on BatSignal/ReverseFunnel). Rejected: carriers sharing raids (c_rep1; c_flee3 family),
  guards/recall variants, wounded retreat, island guards. Implement/review workflow running on c_aura2.

## 2026-10-10 09:20 PDT — c_well5, c_spread2, c_scout1 implemented and reviewed (on c_aura2)
- Workflow wf_fe3d6b50-d8c (6 agents, compile-only); specs in research/diagnosis/2026-10-10-g_iter8.md.
  c_well5: c_well4's probe made reliable (front probe when no mana well is known before r30, diagonal order kept);
  reviewer made probeFront deterministic (a distance tie drew from the robot RNG and would have shifted Cornucopia and
  Maze). Risk: the front probe can fire on ~18 of 103 pool maps, not only Forest. c_spread2: surplus launchers at a
  saturated siege ring hop to the other enemy HQs (id bit splits the ring); reviewer stopped ring holders from following
  a departing spreader (the whole ring would have left) and added a 6,000-bytecode floor on the hop turn. c_scout1: a
  claimed, replaceable island scout; reviewer raised the draw guard to 3,000 bytecodes.
- Bot unit tests added: test/bot/ProbeFrontTest.java (8 cases), test/bot/SpreadTest.java. Unit tests PASS. Screens
  queued vs g_iter8.

## 2026-10-10 10:45 PDT — Rating code audited (owner, PROMPTS 42): prior and SE fixed, Newton fit, 58 tests
- research/audits/2026-10-10-elo.md. An independent Newton fit reproduced elolib.fit to 9e-6 Elo: the code computed
  its formula. But the "weak" prior (1 virtual win + 1 loss vs 1500 per player) compressed the whole scale by ~13%
  (simulated slope 0.81-0.89), so the published +-95% covered the truth only ~40-55% of the time; the diagonal SE
  also understated field bots. Now: prior 0.1 (simulated slope 0.997), SE relative to the mean rating (full inverse),
  Newton solve (0.2 s instead of 65 s). Data path: swapped-label replays (map-rev) were counted twice (85 merged),
  non-A/B winners were counted as B wins, seed '' vs 'map' keyed apart, examplefuncsplayer was listed as one of our
  builds; consumers: the incumbent fallback only knew g_iterN names, --build printed made-up numbers for unknown
  builds. All fixed; tools/test_elo.py (58 tests: synthetic recovery, SE calibration, side/order invariance, prior,
  pair cap, dedupe, load, the incumbent and 'our record') wired into tools/unit-tests.sh.
- Effect: field SD 531 -> 601; our builds +68..+93 vs the field, order unchanged; field scores +0.7..+2.0 points
  (c_aura2 84.1%, c_def3 84.9%); intervals wider (c_aura2 +-67). The field-score charts and ELO.md are regenerated.

## 2026-10-10 11:40 PDT — c_well5 screen PASS; trial started (submission 130)
- Screen (progress/screens/c_well5-7fd593bc5ec7.json) vs c_aura2: (a) 8/8; (b) h2h 12-8 PASS; (c) no gating archetype,
  information-only Net -1 (ampmid -2, blob +1); (d) 128 games, 0 overruns, 0 exceptions, 0 deaths_self (near misses 95).
- trial-start c_well5 at 11:39 PDT, 5 h 21 before the 17:00 autoscrim (logs/trial-c_well5.log). Judge with
  tools/paired.py against gauntlet/20261010-121416-panel-c_aura2 (62/100), plus the MassiveL/Forest mana census.
  c_spread2's screen is running (h2h 13/20 played); c_scout1's is queued behind it.

## 2026-10-10 12:45 PDT — c_well5 rejected (panel 64/100, net +2): its front probe feeds carriers on Forest; c_well6
- Panel (gauntlet/20261010-183910-panel-c_well5) vs g_iter8's: 94 identical, 4 gained, 2 lost: net +2 (+0.82 SE,
  p 0.69); 64/100. Gains: reeceyang Forest, jmerle MassiveL, pranayagra MassiveL, vrangr1 Cornucopia (tb_anchors,
  same mana: noise); losses britacatalin MassiveL, vrangr1 MassiveL. 0 overruns, 0 exceptions.
- Mechanism (census, paired by cell): mana collected by r250 +71 (t +2.6); MassiveL +460 (890 -> 1,351, t +5.4: the
  probe now fires); Forest +295. But on Forest carriers alive at r250 fell from 38-45 to 13-21 in 7 of 10 cells, and
  matches/<id>/extract/deaths.csv shows why: our carriers dead by r250 on Forest 19 (awesomelemonade), 25 (jmerle),
  20 (vrangr1) against 3, 1 and 2 under c_aura2, killed by launchers at prog 0.4-0.5 from r29: the front probe finds
  the midline mana well (29,48) and every mana carrier of that HQ walks to it into the enemy's opening launchers. In
  the other 3 cells (georgezhang, reeceyang, yaonam) the same well doubled mana at r250 (1,055-1,113 -> 2,289-2,354).
- Rejected: net +2 at p 0.69 is no evidence, and the build adds a visible basics failure (carriers fed to the enemy).
  trial-end --reject: c_aura2 resubmitted (submission 131). Keeping c_aura2 also keeps c_spread2's and c_scout1's screens
  (both against c_aura2) valid for the next trial.
- c_well6 = c_well5 + hot wells (C.HOT): a carrier that sees an enemy fighter within r2 100 of its well (a well farther
  than r2 64 from our nearest HQ) drops it and marks it hot in its shared well slot (bits 14-15, level 3) at its next
  write turn; HQ 0 lowers every hot level by 1 each 32 rounds; every carrier skips a hot well (nearestCool). With no
  hot well the choice is c_well5's. test/bot/HotWellTest.java. Judge on the Forest carrier deaths by r250 and the
  MassiveL mana, then the panel.

## 2026-10-10 13:20 PDT — c_spread2 screen PASS; trial started (submission 132)
- Screen (progress/screens/c_spread2-82d101cf0b6a.json) vs c_aura2: (a) 8/8; (b) h2h 12-8 PASS (8-8 after 16, then
  4 straight wins); (c) no gating archetype, information-only Net +5 (horde +3, blob +1, swarm +1); (d) 128 games,
  0 overruns, 0 exceptions, 0 deaths_self. Near misses (main work above 90% of the limit) 826 against c_well5's 95 on
  the same cells, census near doubled on Cornucopia (41,279 vs 20,660), where launchers now press the other enemy HQs;
  bc_max_L 9,750 vs 9,683. The hop itself runs only with 6,000 bytecodes left, so the likely source is heavier fight
  turns at more HQs: trace it in the trial's replays (robots.csv bc_near, NM records) before any acceptance.
- trial-start c_spread2 at 13:20 PDT, 3 h 40 before the 17:00 autoscrim (logs/trial-c_spread2.log). Judge with
  tools/paired.py against gauntlet/20261010-121416-panel-c_aura2 (62/100), plus Cornucopia and the overruns.
- c_well6 reworked after a three-lens review (workflow wf_ecf0f79b-8c2): a hot spot (the fighter's tile) instead of a
  hot well, so Forest's side-by-side midline wells (29,48) and (30,48) are both hot (one at a time made carriers
  ping-pong); only front wells turn hot (farther than r2 64 from our HQ and at least 60% of the enemy distance: a raid
  near Pillars' (7,10), r2 100 from both our HQs, would have sent carriers to the enemy's (27,10)); the replacement is
  the cool well nearest our HQ, not nearest the carrier; with every well of the role hot, a carrier takes any cool well
  at once instead of exploring toward the centre (and the fight); no RNG draws (HQState.nearest draws on ties); the
  probe never adopts a hot well. The review found no encoding or bytecode defect (worst realistic case about +1,500).

## 2026-10-10 14:15 PDT — c_spread2 rejected (panel 61/100, net -1)
- Panel (gauntlet/20261010-202004-panel-c_spread2) vs g_iter8's: 93 identical, 3 gained, 4 lost: net -1 (p 1.0);
  61/100. Cornucopia, the target map, went 3 -> 5 (conquests of vrangr1 r856 and reeceyang r804), but Forest
  (georgezhang, tiebreak), DefaultMap (jmerle) and ReverseFunnel (pranayagra, vrangr1) were lost. Paired census: kills
  -23.2 a game (t -3.1), island-rounds -241 (t -2.2): shedding half a saturated ring weakens the main front on maps
  where the ring was not idle. 0 overruns, 0 exceptions (bc_max_L 9,801 vs 9,747); the screen's near-miss rise was
  not traced further.
- trial-end --reject: c_aura2 resubmitted (submission 133). Re-open condition: a spread gated on evidence that the free
  HQs are producing (their launcher count or sightings near the other HQs), not on ring size alone.
- Next: c_scout1 screen (h2h 11-9, roster running), then c_well6; the next trial window opens after the 17:00 autoscrim.

## 2026-10-10 14:15 PDT — second g_iter8 diagnosis launched (wf_bb0064f5-9d8)
- The g_iter8 judge's ranks 1-3 are spent (c_well5 rejected -> c_well6 screening, c_spread2 rejected, c_scout1
  screening). Four read-only lenses: opponent study (what awesomelemonade, vrangr1, jmerle, pranayagra, georgezhang do,
  to copy the decisive behaviours), three-panel cell analysis (c_aura2, c_well5, c_spread2 played identical cells:
  won 3/3, lost 0/3, mixed), unused mechanics and API sweep, combat exchange; a judge ranks the arms (one structural
  at least) and specs the top 3 for a build on c_aura2.

## 2026-10-10 15:30 PDT — c_scout1 screen PASS (at the bar); second g_iter8 diagnosis: c_lane1, c_end1, c_mend1
- c_scout1 (progress/screens/c_scout1-dad053d52c92.json) vs c_aura2: (a) 8/8; (b) h2h 11-9 PASS (at the bar);
  (c) information-only Net -2 (horde -2); (d) 128 games, 0 overruns, 0 exceptions (near misses 60). Trial after the
  17:00 autoscrim.
- Diagnosis research/diagnosis/2026-10-10-g_iter8b.md (wf_bb0064f5-9d8). Key findings: on Forest every early striker
  (vrangr1, awesomelemonade, jmerle, NotLLeon) walks the cloud-covered top band to our (11,48) and presses it from
  r75-100 while our army goes south: siegeTarget's centroid rule picks (48,11) or (52,30), never the lane HQ (48,48);
  Forest's 6 strikers' cells were lost in all 10 builds since c_swarm1 (60/60 reads). The strong teams heal 2.7-4.3 HP
  per island-round against our 1.1-1.6 at equal island time (no launcher decision reads its health). Late tiebreaks
  are lost on island swings from r1700 (3233 g2: islands 4-2 at r1700 with 268 v 9 launchers, lost by 5).
- Judge's ranks: 1 c_lane1 (lane siege target: the enemy HQ nearest any of ours, with 3+ own HQs or a decided
  symmetry, which changes Forest only of the 103 engine maps; launchers keep marching through clouds), 2 c_end1
  (island duty from r1700: attackers and defenders), 3 c_mend1 (wounded launchers heal on a nearby island we own; no
  change before our first anchor). Rejected: c_lane2 (needs c_lane1 and c_well6 first), c_amp1, c_ws1, c_raid1, c_ward1.
  Build workflow wf_cc9fc191-79f running on c_aura2.

## 2026-10-10 16:05 PDT — c_lane1, c_end1, c_mend1 built and reviewed; screens queued
- Build workflow wf_cc9fc191-79f (implement + adversarial review per arm, compile and unit test only). Each reviewer
  fixed something: c_lane1 (doc of objKind now read by the cloud march; Lane1Test 29 cases incl. siegeTarget's
  short-turn and rank paths; the implementer added LANE_GUARD 4,000 bytecodes for the recompute), c_end1 (a
  non-keeper finding no island re-ran the 35-id loop every march turn, about 2,700 bytecodes: a complete pass is now
  cached END_RECHECK rounds; End1Test), c_mend1 (mendDue gate: nothing before r250 and only with MEND_MIN_LEFT 6,000
  bytecodes left; Mend1Test 24 cases). docs/TELEMETRY.md 1.1 notes the arms' objKind variants. unit-tests PASS
  (65 packages).
- Screens queued behind c_well6's (running since 15:30): c_lane1, c_mend1, c_end1. c_end1 changes only games past
  r1700, so its h2h will sit near the identity 10/20; judge it on the late-game cells.
- Next: c_scout1's trial right after the 17:00 autoscrim fires.

## 2026-10-10 17:25 PDT — rating history chart (PROMPTS 44); c_scout1 trial; c_well6 screen FAIL on one overrun
- tools/rating_history.py (workflow wf_b9c56eda-f87: implement, two adversarial verifiers, fix): the replica's Team
  Settings "Rating History" curve (GET .../match/historical_rating/, siarnaq's displayed rating after each ranked,
  non-tournament match: 316 points) in PDT, with each submission's first completed rated match marked (15
  submissions; trial candidates never play rated games). Outputs progress/rating-history.png and .md; in the progress
  refresh and README. Galaxy's own chart draws UTC under "Local Date & Time" (Highcharts useUTC). test_tools 79 tests.
- c_scout1 trial started 17:10 PDT (submission 134) after the 17:00 autoscrim was created on c_aura2.
- c_well6 screen: (a) PASS, (b) BORDERLINE 10-10 (both Forest games won), (c) info Net +1, (d) FAIL: 1 overrun in 128
  games: a launcher at 10,001 on Cornucopia vs arch_ampmid (B side). Replayed deterministically on the VM
  (matches/ov-well6.bc23): r1108 launcher #10196, main work 9,758 on a calm march (code M, objective switched from an
  island to the enemy HQ, 17 allies in vision, 0 enemies), then the unguarded indicator string pushed the turn past
  10,000. All 4 near misses in that game are calm marches or follows with 15-65 allies: a big-blob march path costs
  9,000-9,800 bytecodes. The launcher code is c_aura2's (c_well6 changes only carriers and Comms micro-costs), so the
  incumbent carries the same tail. Diagnosing with a checkpoint build (src/x_bcp, not committed) on 6 VM games.

## 2026-10-10 18:20 PDT — rating history: clipped at 1,400 with our BT ratings (PROMPTS 45); launcher overrun traced
- tools/rating_history.py (workflow wf_7ef84c72-0ba: implement, two verifiers, fix): left axis from 1,400 (28 early
  points off the chart, noted); a right axis in Bradley-Terry points tied to the left by BT = -7,305 + 5.75 x galaxy
  (least squares over the 72 Rankings teams rated >= 1,400 with >= 30 BT games, r 0.98; residual +-31 galaxy points at
  95%, stated in the footer): one replica point is about 5.8 BT points, so raw BT numbers cannot share the left axis.
  Each build's BT over its rated tenure (re-uploads merged) with the fit's 95% band; trial candidates as diamonds at
  their trial start. Our galaxy rating ends every tenure below the build's converted BT, within the conversion scatter
  for c_def3, 8-38 points for c_swarm1-c_aura2 (field teams at our level sit about 12 below the line too).
- Overrun diagnosis (checkpoint build src/x_bcp, 6 VM games, deleted after): on the 10 near-miss launcher turns, all
  calm marches in 65-launcher blobs: pre-run sensing 2,050, pickObjective 3,237 (island loop, enemy HQs, raid wells),
  regroup's ally loop 2,328, Nav 464-2,429. Fix prepared (scratchpad bcfix.py; src/c_bc1 = c_aura2 + fix, compiled):
  the indicator string only with C.IND_GUARD 400 bytecodes left (end-of-turn telemetry measured at most 309 for
  launchers), and regroup finds the closest ally in a second pass only below GROUP_MIN (same results, about 650 fewer
  bytecodes in a 65 blob). It goes on whichever build c_scout1's trial leaves validated, trialled as a basics fix.

## 2026-10-10 19:25 PDT — c_lane1 screen FAIL (21 overruns); launcher bytecode base c_bc1 under way
- c_lane1 (progress/screens/c_lane1-db3cdf131b4d.json) vs c_aura2: (a) 8/8; (b) BORDERLINE 10-10 (Forest 0-2, every
  other map 1-1); (c) information-only Net -4 (arch_swarm -4 flagged REGRESSION, ampmid -2, horde +2); (d) FAIL: 21
  launcher overruns, all on Cornucopia side B (vs c_aura2 5, vs arch_ampmid 16; bc_max_L up to 10,094). Launchers in
  big Cornucopia blobs already run within a few hundred bytecodes of the limit (c_well6's single overrun), so every
  arm that adds launcher work tips over: c_mend1 and c_end1 (screens queued) likely too.
- Basics first: workflow wf_467d580f-1a9 builds c_bc1 = c_aura2 + a decision-preserving launcher bytecode cut (the
  indicator guard and regroup second pass from bcfix.py, plus pickObjective's island loop / enemyHQs allocation / the
  pre-run sensing; goal at least 2,000 more off the worst calm-march turn), verified by an equivalence review and a
  checkpoint measurement on VM games against c_aura2. The launcher arms are then rebased on it.

## 2026-10-10 21:15 PDT — c_scout1 rejected (panel 60/100, net -2)
- Panel (gauntlet/20261011-001032-panel-c_scout1, matches 4124-4133) vs g_iter8's: 96 identical, 1 gained (yaonam),
  3 lost (NotLLeon, Sprint1, vrangr1): net -2 (p 0.63); 60/100; 0 overruns, 0 exceptions. Mechanism measured: first
  anchor 24 rounds earlier (t -3.8), BatSignal 332-492 -> 275-299 in all 10 cells, ReverseFunnel earlier in 6; but
  anchors placed unchanged (3.7) and the island-rounds margin -145 (t -2.1): locating islands earlier did not turn into
  holding them. trial-end --reject: c_aura2 resubmitted (submission 135). The panel waited 2 h behind the 17:00
  autoscrim backlog (trial started 17:10, first match 20:00).
- All three g_iter8 judge arms are now closed (c_well5 -> c_well6 pending a fix, c_spread2, c_scout1). Next: c_bc1,
  the launcher bytecode base (basics), then the launcher arms rebased on it.

## 2026-10-10 21:20 PDT — c_bc1 (launcher bytecode base) verified; trial started (submission 136); arms rebasing
- c_bc1 (workflow wf_467d580f-1a9): c_aura2 + decision-preserving launcher cuts. Measured with identical checkpoint
  builds on 6 VM games each (Cornucopia vs arch_ampmid both sides, vs c_aura2 both sides, vs arch_horde; MassiveL vs
  c_aura2): launcher near misses 44 (c_aura2) -> 0, overruns 0 -> 0; median calm-march turn with 50+ allies
  6,856 -> 3,664 (regroup 2,086 -> 137, pickObjective 1,794 -> 1,022, pre-run 1,681 -> 1,447); worst launcher turn
  9,111 -> 8,417. The equivalence review found one divergence (the end-of-turn re-sense skipped after an overrun),
  fixed (enemiesStale); Bc1Test compares the cut code with c_aura2's on 217,142 cases. Not met: the 2,000 goal on the
  computePredWells turns (the pass runs to its 4,500-left guard, so earlier savings are spent there); a follow-up
  (skip passes whose inputs are unchanged) can cut those without changing decisions.
- trial-start c_bc1 --skip-screen (reason recorded: basics fix, identity build the h2h cannot resolve) at 21:21 PDT.
  Accept on a non-worse panel with 0 overruns: it is the basics base for every launcher arm.
- Rebase workflow wf_3649d981-a9f: c_lane1 -> c_lane2, c_mend1 -> c_mend2, c_end1 -> c_end2, c_well6 -> c_well7 on
  c_bc1 (caches must include each arm's inputs). c_end1's pending screen cancelled; c_mend1's finishes for information.

## 2026-10-10 21:55 PDT — c_mend1 screen PASS; arms rebased onto c_bc1; screens queued
- c_mend1 (progress/screens/c_mend1-52217dc460cb.json) vs c_aura2: (a) 8/8; (b) h2h 12-8 PASS; (c) information-only Net
  +3 (horde +3, blob +1, ampmid -1); (d) 128 games, 0 overruns, 0 exceptions (near misses 49). The best screen of the
  evening, and its mending adds launcher work only for wounded launchers after our first anchor.
- Rebase workflow wf_3649d981-a9f: c_lane2, c_mend2, c_end2, c_well7 on c_bc1, each reviewed (arm hunks identical
  to the c_aura2 versions, c_bc1 caches keyed on inputs the arms never write or returning before them; c_lane2's lane
  branch runs before the siegeTarget cache, checked by a 236,326-call differential test against c_lane1). unit-tests
  PASS. Screens queued vs c_aura2 (decision-identical to c_bc1): c_well7, c_end2, c_lane2. c_mend2 rests on c_mend1's
  screen (same arm, decision-identical base).
- Order once c_bc1's trial ends: if accepted, trial c_mend2 next (--skip-screen: screened as c_mend1); if rejected,
  trial c_mend1.

## 2026-10-10 22:45 PDT — c_bc1 accepted as g_iter9 (basics); the single-reference-panel bias
- c_bc1 panel (gauntlet/20261011-042052-panel-c_bc1, matches 4180-4189) vs g_iter8's: 92 identical, 2 gained, 6 lost:
  net -4 (-1.41 SE, p 0.29); 58/100; island-rounds margin -198 (t -2.05); 0 overruns, 0 exceptions; bc_max_L 9,352
  (c_aura2 9,747); census near-miss sum 17,730 vs 25,835. Decisions are c_aura2's for the same inputs, but more
  bytecodes left change the fill (map processing, distance fields) and let computePredWells finish more often (raid
  targets), so games diverge.
- Accepted as a basics fix (precedent: c_nav6 accepted at -2 as noise): every launcher arm needs its headroom (c_lane1
  overran 21 times on c_aura2's code).
- Methodology finding: every candidate panel since c_aura2 lost island-rounds against c_aura2's panel (c_well5 -84,
  c_spread2 -77, c_scout1 -145, c_bc1 -198) and the flips total 15 lost vs 10 gained. Games are deterministic, so one
  build's panel is a single draw of its bytecode-timing-dependent outcomes; any change re-draws the borderline cells,
  and a lucky reference draw makes every candidate regress against it. From now on judge a candidate against both
  c_bc1's and c_aura2's panels (two draws of one policy, 58 and 62) and report both nets.
- Next: c_mend2 trial after the 01:00 autoscrim (--skip-screen: screened as c_mend1 vs c_aura2, decision-identical
  base). Screens of c_well7, c_end2, c_lane2 run against c_aura2's hash (decision-identical to c_bc1).

## 2026-10-11 00:10 PDT — c_well7 screen PASS (0 near misses); parallel trial panels under way
- c_well7 (c_well6's hot wells on c_bc1; progress/screens/c_well7-56a91347aa7b.json) vs c_aura2's hash
  (decision-identical to c_bc1): (a) 8/8; (b) h2h 11-9 PASS; (c) information-only Net -1; (d) 128 games, 0 overruns,
  0 exceptions, 0 near misses (c_well6 on c_aura2's launcher code: 1 overrun, 86 near misses). Candidates for the
  window after the 01:00 autoscrim: c_mend2 (screened as c_mend1), c_well7.
- The replica's post-autoscrim backlog delays a trial panel about 3 hours (c_scout1: first panel match 20:00 for a
  17:10 start), so trials serialize to about one per 8-hour window. Workflow wf_4befd2d5-a5f: contest.block pairs a
  panel match by our participant's submission (overlapping panels share opponents and maps), and ladder_policy gets
  trial-park (once every panel match is created, resubmit the validated build and free the trial slot while the panel
  plays) and trial-decide (accept or reject a parked trial from its finished panel). A match plays the submission
  active at its creation, so a candidate is exposed for minutes, not hours.

## 2026-10-11 01:03 PDT — first overlapping trials: c_mend2 and c_well7 parked
- The 01:00 autoscrim was created on c_bc1 (matches 4426-4486 at 01:00:00). trial-start c_mend2 (--skip-screen:
  screened as c_mend1) at 01:00:48, all 10 panel matches created (4561-4570), trial-park at 01:01: c_bc1 active again
  as submission 138. trial-start c_well7 (--skip-screen: screened vs c_aura2) at 01:02:11, matches 4571-4580, parked
  at 01:03: c_bc1 active as 140. Each candidate was the active submission for about one minute.
- Both panels play behind the autoscrim backlog. Judge each with tools/paired.py against both reference panels
  (c_bc1 gauntlet/20261011-042052-panel-c_bc1 and c_aura2 gauntlet/20261010-121416-panel-c_aura2), then
  trial-decide <package> --accept|--reject.

## 2026-10-11 01:45 PDT — c_end2 screen FAIL on the h2h rule only; trial started anyway (third overlapping panel)
- c_end2 (progress/screens/c_end2-ebd40b4d39ad.json): (a) 8/8; (b) BORDERLINE 9-11; (c) information-only Net -1 (swarm
  -2, horde +1); (d) 128 games, 0 overruns, 0 exceptions, near misses 2. The arm acts only past r1700: 6 of the 20 h2h
  games got there and split 3-3; the other 14 are c_bc1 self-play noise. The screen cannot see the cells it targets
  (replica tiebreak losses by island swings from r1700).
- trial-start c_end2 --skip-screen (reason recorded) at 01:45 PDT; its panel waits for galaxy's hourly unranked
  limit (two panels just used 40), and a background job parks it as soon as all 10 matches exist. Ranked incoming is on
  auto-reject and no autoscrim is due before 09:00, so the longer exposure plays no rated game.

## 2026-10-11 02:15 PDT — c_lane2 closed (Forest 0-4 locally); next batch c_amp2, c_ward2, c_bc2
- c_lane2 screen (progress/screens/c_lane2-e701d86b88df.json): h2h FAIL 7-13. Forest, the only map the lane rule
  changes, 0-2 again (c_lane1: 0-2): 0-4 against our own build's southern push; the other maps are c_bc1 self-play
  noise. Closed; re-open with a lane that does not leave home exposed (e.g. the lane only once (11,48) is pressed).
- Build workflow wf_5fc712aa-9ea on c_bc1: c_amp2 (the second diagnosis's amplifier scout/relay: 3 of 5 top teams field
  amplifiers with their army; ours never write comms in the field), c_ward2 (the forming pool answers raids on home
  wells; carriers bring the raid home), c_bc2 (decision-preserving computePredWells cut: skip unchanged passes, box
  rejection, integer duplicate check). The judge deferred c_amp1/c_ward1 for unmeasured payoff; overlapping panels make
  measuring cheap.

## 2026-10-11 03:40 PDT — c_amp2, c_ward2, c_bc2 built and reviewed; screens queued (vs c_bc1)
- Workflow wf_5fc712aa-9ea. c_amp2 (one team amplifier: island scout, then relay with the army so field robots write
  islands, wells and symmetry; census bits 10-15): the review moved its field well flush into the bounded end-of-turn
  phase (up to ~700 unguarded bytecodes on launcher fight turns) and cached the legacy write-zone test. c_ward2 (the
  forming pool answers raids on home wells; carriers report the raid with its sighting stamp): clean. c_bc2
  (computePredWells: skip a pass whose inputs are unchanged, box rejection, integer duplicate check): the review found
  the box test cost more than c_bc1's near test when enemy HQs are spread (passes cut where c_bc1's finished: the
  forbidden direction), fixed with c_bc1's near test inside the box and an entry guard; Bc2Test 1,899,878 checks vs a
  verbatim copy of c_bc1. unit-tests PASS. Screens queued against c_bc1: c_amp2, c_ward2, c_bc2.

## 2026-10-11 05:14 PDT — c_mend2 accepted as g_iter10 (wounded launchers heal on our islands)
- Panel (gauntlet/20261011-080046-panel-c_mend2, matches 4561-4570): 61/100. vs c_bc1 (its base): 95 identical, 4
  gained (NotLLeon, georgezhang, pranayagra, vrangr1), 1 lost: net +3 (p 0.38), island-rounds margin +183 (t +2.30).
  vs c_aura2: 91 identical, 4 gained, 5 lost: net -1, island-rounds -14. Mechanism: healed HP a game 1,561 -> 3,430
  (t +4.79 vs c_bc1; +3.75 vs c_aura2), launcher deaths 89.3 -> 81.8 (t -2.37), kills +7 (t +1.3). 0 overruns.
- Accepted (trial-decide 137 --accept; resubmitted as 143): a measured mechanism the opponent study named (the strong
  teams heal 2.7-4.3 HP per island-round) and positive against its own base; the c_aura2 reference is the lucky draw
  (every candidate regressed against it).
- c_well7 and c_end2 (built on c_bc1) are judged against c_bc1's panel; a positive one is then stacked on c_mend2.
  c_amp2, c_ward2, c_bc2 (screens running vs c_bc1) are rebased onto c_mend2 for their trials.

## 2026-10-11 06:05 PDT — c_well7 rejected (panel 60/100: +2 vs c_bc1, -2 vs c_aura2); the front probe is the feeder
- Panel gauntlet/20261011-080209-panel-c_well7 (matches 4571-4580): vs c_bc1 90 identical, 6 gained, 4 lost, net +2
  (p 0.75), island-rounds +21; vs c_aura2 net -2, island-rounds -177. 0 overruns. Mana by r250: MassiveL 831 -> 1,313
  (t +5.97), Forest 1,098 -> 1,430 (t +1.65); Forest carriers alive at r250 40.1 -> 31.3 (t -2.44).
- Hot wells barely cut the Forest feeding: our carriers dead by r250 on Forest, per panel opponent: c_well7 11-21
  against 7 teams (c_well5 19-25; c_bc1 0-2; c_aura2 0-2). The MassiveL gain comes from the diagonal near-well probe
  (home well (2,0)); the Forest feeding from the front point (the midline well (29,48)). trial-decide 139 --reject.
- Next: c_well9 = c_mend2 + the diagonal probe only (no front-only probe, no front point in the regular probe).
- c_amp2's screen is slower: the first screen against c_bc1 also plays c_bc1's 100 roster games (cached by hash).

## 2026-10-11 06:50 PDT — arms rebased onto c_mend2; c_well9 (diagonal probe only); screens
- Rebase workflow wf_2b9c2cc2-d32 (its reviews re-run after the spend-limit stop, owner PROMPTS 46-47): c_amp3, c_ward3,
  c_bc3, c_well8, c_end3 on c_mend2, all reviewed ready (c_amp3 note: while our amplifier lives its stricter write
  zone stops a mender waiting beside its island from reporting enemies there, which weakens mend's contested-island
  filter; a follow-up to measure). c_well9 = c_well8 with C.PROBE_FRONT false (no front-only probe and no midpoint in
  the regular probe; the diagonals that find MassiveL's (2,0) stay). unit-tests PASS.
- Screens vs c_mend2: c_well9 queued; c_ward3 and c_bc3 held back until c_well9's collect caches c_mend2's 100 roster
  games (each queued job would otherwise replay them). c_amp2's screen (vs c_bc1) finishes and stands in for c_amp3.

## 2026-10-11 07:25 PDT — c_end2 rejected; token race fixed; blind fire (owner, PROMPTS 48)
- c_end2's block crashed when parallel panels refreshed the login token through one shared temp file
  (FileNotFoundError on token.json.tmp); contest._save_token now writes a per-process temp file (test added), and the
  panel was collected with RESUME. Panel gauntlet/20261011-084600-panel-c_end2 (4581-4590): vs c_bc1 99 identical, 1
  lost (reeceyang Forest tiebreak): net -1; vs c_aura2 net -5. Of 17 cells past r1700 no tiebreak loss flipped
  (britacatalin, georgezhang, NotLLeon unchanged); three wins ended earlier by conquest. trial-decide 141 --reject.
- Blind fire: a launcher may attack any tile within r2 16 without seeing it (RULES 5.2), and vision drops to r2 4 when
  the target or the viewer stands on a cloud (RULES 6.1); a shot costs only the action cooldown. Census blind_rate
  (shots that hit nothing) on c_mend2's panel: awesomelemonade 0.70, pranayagra 0.60, vrangr1 and jmerle 0.56, NotLLeon
  0.52, reeceyang 0.45, georgezhang 0.43; Sprint1, britacatalin, yaonam 0.00; us 0.00. The teams that beat us fire blind,
  the ones we beat do not. Workflow wf_109a1464-007 extends ReplayDump to classify every shot by the shooter's
  visibility of the target tile, cloud and hit, and measures blind-fire damage and our deaths from it on the panels.

## 2026-10-11 07:45 PDT — c_amp2 screen FAIL; c_amp2/c_amp3 closed
- c_amp2 (progress/screens/c_amp2-ea369b77633e.json) vs c_bc1: (a) 8/8; (b) BORDERLINE 9-11; (c) information-only Net
  -6 (adecon -3, ampmid -2, horde -1); (d) 128 games, 0 overruns (near misses 1). The amplifier costs a launcher's
  worth of resources and shows no payoff locally; the judge's objection (a long, unmeasured payoff chain) stands.
  Closed with c_amp3; re-open only with a measured information gap the relay would fill (e.g. the blind-fire
  telemetry showing hits on islands we never saw).
- The unit-test run for the token fix hit its 40-minute limit with the driver busy (blind-fire replay dumps, refresh);
  rerun when the driver is quiet, before committing tools/contest.py.

## 2026-10-11 09:15 PDT — c_bc3 trial parked (after the 09:00 autoscrim)
- The 09:00 autoscrim was created on c_mend2 (matches 4849-4938 at 09:00:00). trial-start c_bc3 (--skip-screen:
  decision-preserving computePredWells cut, Bc3Test 1,899,878 cases) at 09:14; panel matches 4943-4952; parked at
  09:15 with c_mend2 active again as 145. Judge against c_mend2's panel and c_bc1's.

## 2026-10-12 PDT — Codex recovery, instrument correction, and driver continuation

- Read PROMPTS, CLAUDE, HANDOFF, LEARNINGS, the training algorithm/rules, recent log and replica documentation.
  HANDOFF was stale: latest committed state is validated c_mend2 active 145, c_bc3 trial 144 parked with matches
  4943-4952; c_well7/c_end2/c_lane2/c_amp2/c_amp3 are closed. Reconciled the handoff without claiming live VM results.
- This cloud environment has no GCP identity, gcloud CLI, SSH credentials or VM route. The owner started Codex via tmux
  on the original claude-driver; docs/CONTINUATION.md describes preserving both live checkouts/processes, checking
  collector/pruning health, collecting the existing c_bc3 panel against both references, and resuming c_well9/c_ward3.
  No VM action, scrimmage request, candidate game, or promotion was performed here.
- Published contest.py still used one token.json.tmp, despite the prior log's uncommitted fix. Reconstructed unique
  private temporary writes with cleanup. Both simultaneous-writer and failed-write regressions pass and fail against
  the original implementation. Reconcile any unpublished driver fix instead of overwriting it.
- Ranked policy checked the active build before POST without the trial-state lock. Trial-start could activate a
  candidate in between. Hold the existing lock through fresh checks and match creation; three concurrency tests pass
  (both ordering cases, lock release on 409/429/500/network failure). Both ordering regressions fail on original code.
  Locks remain local to one checkout; preserve one authoritative driver and ranked process.
- Instrument correction: historical blind_rate is a miss fraction, not shots outside vision. Retracted the 43-70%
  visibility claim in LEARNINGS. Pinned engine 3.0.15 (af42086) records no move events, stores hit victim IDs, emits
  positions after currents, and omits dead endpoints. Added conservative visible/outside_vision/unknown shot classes,
  unknown-inclusive rate bounds, and optional per-shot CSV. Historical columns retain their values; miss_rate is an
  explicit alias. Geometry reviewed independently (self-shots remain legal, unsupported map origins are unknown).
  Fourteen targeted reader tests, including eight geometry/integration regressions, pass. Re-extract the panels for
  visibility evidence before proposing a blind-fire arm or attributing damage/deaths to it.
- Installed JDK 8 locally and built engine tag 3.0.15 for unit/fixture verification only (JSI 3457c7fd; local jar SHA256
  bdc00ae46ff683a6de688c9ea7bfc46f2981077f59af9b07a81e5761bffec34f). This gitignored jar is not the checksum-pinned
  release and is never for deployment or candidate verdicts. All 79 bot packages compile and bot unit mains pass;
  analysis tests (111, one skip), rating tests (58), match reports (36, two skips), ranked/token regressions (3/2) and
  operator tests (21) pass. The analysis suite retains pinned historical census hashes and verifies the added columns.
  The full unit entrypoint was run: release-backed replica/Galaxy compile integration refuses this jar's checksum,
  as intended. Full release-backed verification remains required on claude-driver before adoption. The frontend
  suite has four existing skips; the analysis suite has one missing-optional-fixture skip.

## 2026-10-12 PDT — preserve web interaction; CLI handoff withdrawn (owner, PROMPTS 58)

- The owner rejects ongoing CLI interaction. Keep this web session as project controller and use the existing VMs as
  remote compute workers. Corrected the continuation documentation; do not follow the earlier CLI handoff prompt.
- Rechecked environment readiness: no outbound identity or secret binding, VPN disabled, no private TCP grants.
  Plugin discovery found no suitable GCP/SSH execution integration. The documented remote path is configured VPN,
  private TCP grants and protected SSH authentication; IAP WebSocket compatibility is unverified. These access
  settings require environment configuration; starting a separate Codex CLI does not establish them.
- No VM connection has yet succeeded. Repository fixes remain on codex/continue-bc23 / draft PR 1, and no live
  submission, queue, credentials or services were changed. Ongoing interaction must remain through the web UI.

## 2026-10-12 PDT — one-time access setup authorized; environment Edit is a setup conversation

- Owner PROMPTS 59 authorizes one-time commands with detailed instructions; PROMPTS 60 identifies the environment
  editor as a chat. Official cloud documentation confirms that environment configuration can be refined in that
  conversation and republished. First request confirmation of Tailscale VPN and raw TCP grant support there.
- Plan the smallest route: Tailscale on claude-driver only, web-side grant for that peer's exact tailnet IPv4,
  authenticated SSH with pinned host keys, then existing internal access to battlecode-dev. Native SSH remains the
  straightforward option; Tailscale SSH may avoid a separate private-key binding, subject to explicit tailnet rules
  and a successful actual connection check. No VM installation or configuration has happened yet.

## 2026-10-12 PDT — private driver worker prepared for web control

- PROMPTS 61 reports the environment editor cannot configure VPN/TCP. The prepared SSH helper is not a connection.
  Switch to outbound GitHub Actions job transport on claude-driver; no cloud VPN or new SSH credentials are needed.
- PROMPTS 62: owner created battlecode23-control, added it to the connection, and published the environment.
  Verified repo ID 1415998276, visibility private, connector reads and authenticated git clone. It was empty.
- Prepared checksum-pinned non-root installer for the existing driver account, isolated repo-scoped runner, exact
  private-repo/main/actor guards, job hash/deadline validation, permanent single-use request IDs, filtered job
  environment, bounded/redacted logs, and private response publication with a live repository privacy check.
  Public bot repo contains only the template; actual executable workflow belongs to the private control repo.
- First job is read-only driver inspection. No live VM was accessed, no bot was promoted, and no games were requested.
  One-time VM registration remains necessary; ongoing interaction stays in this web chat.
- Published private control commit abeb44ec5aff729b4ca6574035aebf2623105652. Verified connector reads the request and
  lists Actions run 38294065532, queued with the expected actor terryvanbelle. No actor override is needed.
  Request inspect-driver-20261012T185336Z pins job a4f1a84f0e87be734f723fe140d6f48336859f4bdf167c1234de59c50f6ff61d.
- Local mocked installer and real local supervisor/publisher regressions cover credential boundaries, origin/cwd
  preservation, output bounds, timeout process groups, and response integrity: 34 tests pass. Official-jar integration remains a
  driver check because this cloud's temporary source-built jar has a different checksum; do not weaken the pin.
- Final full-suite attempt with local socket permission: 79 packages and bot unit mains pass; 111 analysis, 3 ranked,
  2 token, 34 worker, 58 ratings, 36 reports, and 21 operator tests pass. Replica/Galaxy failures are only their
  enforced official-engine checksum checks (one each); frontend passes with four existing optional build skips.

## 2026-10-12 PDT — correct GitHub runner metadata encoding

- PROMPTS 63: owner registered the driver runner successfully, then bootstrap rejected its saved metadata before
  service installation. GitHub's pinned runner SaveSettings -> IOUtil.SaveObject writes JSON with Encoding.UTF8,
  which emits a BOM. Python json.load with plain utf-8 rejects it; the broad error handler mislabeled it a mismatch.
- Correct the reader to utf-8-sig, accepting both BOM and plain UTF-8 without changing the exact private repo,
  runner name, or work-directory checks. Preserve the registration and credential files on retry. Update the
  simulated fresh registration to match the upstream encoding and test an already-registered BOM resume.
- The read-only inspection Actions run is still queued; this web session has not accessed either VM yet.
- All 36 worker tests pass (14 installer/workflow and 22 supervisor/publisher). New cases reproduce actual BOM
  encoding, resume service installation with registration preserved, and reject wrong/malformed metadata unchanged.

## 2026-10-12 12:06–12:17 PDT — web worker live; existing VMs recovered

- PROMPTS 64 reports the service started. Actions run 38294065532 succeeded; response ID/hash/exit/log integrity
  verified. Driver is claude-driver, terryvanbelle, original checkout /home/terryvanbelle/projects/vibe/2023,
  HEAD 079541c; official engine SHA matches the required 3.0.15 pin. JDK8 is present at the established path.
- Follow-up inventory preserves all 37 dirty files in build/codex-recovery/20261012T191037Z/dirty-work.tar.gz,
  with tracked.patch, status.json and head.txt. The 28,551-byte own-code patch was independently reviewed: its
  old shot inference is superseded by the audited classifier, and its token fix by unique mkstemp+cleanup tests.
  Preserve the archive; no independent old fix is lost by adopting the prepared branch.
- Strict host-key-checked internal gcloud SSH to battlecode-dev succeeded. Replica web/relay/saturn and scheduler
  timer are active. The deployed project tree is a mirror, not a Git checkout. Driver has about 9 GB free and game VM
  about 3.5 GB. Existing ranked process PID 2657389 remains running; do not launch a duplicate.
- Validated build remains c_mend2/145. Parked c_bc3/144 panel is marked done at 2026-10-11 13:32 PDT, pending
  explicit 100-cell, terminal-status, source-hash and basics checks before decision. Existing queue/screens inspected
  next. A first read-only training export exceeded the worker's bounded-output budget; retry with bounded summaries.

## 2026-10-12 13:05 PDT — recovered candidate evidence; c_bc3 held, c_well9 failed; official check repairs pending
- c_mend2/145 remains validated. c_bc3/144 panel gauntlet/20261011-161413-panel-c_bc3 is complete: matches
  4943-4952 all terminal OK!, 100 unique matching cells, 200 paired census rows, current source hash ed3aceb26a90.
  Its 61/100 win/loss outcomes equal c_mend2's on every cell; 37 game durations differ. Paired island-round margin
  -136.8 (t -1.79) vs gauntlet/20261011-080046-panel-c_mend2; vs gauntlet/20261011-042052-panel-c_bc1, net +3,
  margin +46.58 (t +0.48). Full win_reason data confirm no coin cells in all three panels.
- Replay overruns/self deaths and decoded exception turns are zero. Indicator counters are blank throughout:
  counter-based ex/nm zeros are unobserved defaults. Raw near counts are 17,509 vs c_mend2's 17,923; median launcher
  maxima 9,175 vs 9,174, worst 9,363 each. Those end-turn measures include background fill and telemetry, not the
  cost of computePredWells. Hold c_bc3 until its method benchmark is recovered or pre-fill work savings are measured;
  do not duplicate the completed panel or promote on equal win outcomes alone.
- c_well9's existing screen collected FAIL (h2h 9-11, roster Net 0); no VALID archetype records rescue the borderline
  h2h. No ladder trial. c_ward3's queued job is missing: requeue its full VM screen after source/cache checks.
- Official-engine driver unit-tests ran 12:25:55-12:46:26 PDT, failing only the Python 3.9 bootstrap tar fixture and
  RealDataTest.test_replays_agree's false cross-label equivalence. Repairs are prepared; official rerun pending.
- Live rows/API parity agree: galaxy-3357/2 is legobridge A / NolanChai B, PairedProgramming, map-rev, B wins r1631;
  galaxy-4694/3 is NolanChai A / legobridge B, map, A wins r1421. Same physical spawn owners, different observable
  rc.getTeam() labels: these are distinct simulations. Preserve both raw rows; elolib.dedupe now retains labelled
  pair/map/seed-orientation keys, normalizes blank seed to map, and still drops exact repeats. The strict same-labelled
  winner/round invariant remains, with a live counterexample and disagreement fixtures. Local repair checks: ELO 60,
  tools 111 (1 skipped), match reports 36 (2 skipped), field tools 21; all passed. Regenerate live ratings/views after
  adopting the correction; no raw games were deleted or rewritten.

## 2026-10-12 13:41 PDT — official checks pass; progress published to main

- Corrected official-engine suite on claude-driver: 13:11:10–13:33:38 PDT, exit 0, no timeout, start/finish HEAD
  83ae37a. All 79 bot packages and bot mains passed; analysis 111, ranked 3, token 2, worker 36, ratings 60,
  reports 36 (2 skipped), replica 83, frontend 13, backend 46, operator 30 passed.
- Owner verified the profile quote at 13:05 PDT and repository note, then explicitly required every update reach
  main (PROMPTS 69–70). Snapshot 9e8d180 is on main: 15,708 raw games (all prior published rows preserved), refreshed
  Rankings/rating history/BT/field-score/progress charts, telemetry, c_well9 FAIL record and screen cache. Rankings
  snapshot 13:19 PDT: vibe23 #5/88, rating 1682.8; rating history fetched at 13:21 PDT.
- Recovering summary.txt filled all 100 incumbent reference cells: cache 6,572 cells, no conflicts. c_well9 remains
  FAIL, h2h 9–11, gating Net 0; information-only roster Net +1 with complete comparisons, basics 0 over/ex/self deaths.
- The recursive Ward check found the recorded job under queue/cancelled/, with no run/log markers. Preserve the
  cancelled entry; schedule a fresh current-hash screen rather than interpreting standard status's missing as proof
  there was no job. No candidate promoted. c_bc3 remains held for actual computePredWells cost/guard evidence.
- Bounded incremental collector started 13:34 PDT. By 13:38 it had appended 229 games and audited 427 unavailable
  retention-eligible field replay files, preserving the prior CSV byte prefix. It continues under a 20-minute budget.
- Owner requires continuous independent diagnosis/idea generation/testing until told to stop (PROMPTS 75). Model
  budget discussion: 92% remaining, next reset 6d20h; setup-period usage is not a steady-state diagnosis forecast.

## 2026-10-12 13:44 PDT — ranked controller adopted; Ward3 screen resumed

- Safely replaced exact old ranked PID 2657389 after the official pass with one controller, PID 3037528. The old
  process's UID/cwd/argv/start ticks/sleep state and singleton were checked; pidfd TERM and existing state lock covered
  replacement. Validated submission 145 was preserved. New logs: build/codex-recovery/ranked-20261012T204100Z/.
- Fresh full c_ward3 screen queued as 20261012-204410-scr-c_ward3-3d2ef1dd0da7, tag scr-3d2ef1dd0da7-0b3c. Candidate
  hash 3d2ef1dd0da7, incumbent c_mend2 d62033781fbd. All eight own source hashes and screen/helper hashes agreed with
  the VM; disk >2 GiB, no pending/running jobs, no STOP/filler. Preserved the known cancelled predecessor unchanged.
  Reused queue runner PID 254430/flock; did not start another runner or sync/delete source directories. Volume is
  up to 128 candidate games, 0 incumbent repeats (all 100 reference cells cached).
- Continue independently while it plays: instrumented c_bc3/c_mend2 method cost/guard comparison and replay-based
  economy/combat/healing diagnosis. No candidate promoted and no new field panel requested.

## 2026-10-12 14:20 PDT — official CBC3 cost diagnosis; conservative Mend3 arm

- Official jar 5d4e42a5 / VM JDK8 instrumented computePredWells probe: 192 cases repeated twice, no cost drift or
  pending debt; 58 finite-budget list differences, no differences at 1,000,000. Cached tight_sparse 818 -> 320,
  cached empty 87 -> 208. Only two of six reachable 10k warmup shapes saved work. No unconditional
  decision-preservation claim; hold c_mend2/145. Full provenance/limits and callsite interpretation in
  research/diagnosis/2026-10-12-c_bc3-cost.md; driver artifacts build/codex-recovery/cbc-probe-20261012T210624Z.
- c_mend3 db9f54f47fea differs from frozen Mend2 only in Launcher healing fallback: nearest blocked, no visible
  enemies, fallback entry >=7500, between-island guard6000. Fresh four-slot sightings, original island ownership,
  radius, tie order and ordinary-path reads preserved. 852 prototype selector/guard checks pass. Official full
  suite and instrumented method/full-turn delivery diagnostics pending; no games/submission yet.
- Collector finished 13:54 PDT, exit0/no timeout, 15,708 ->17,701 raw rows with prior byte prefix preserved,
  1,006 unavailable eligible field replay audit records. Final batch adds zero, seven matches unfinished. Ward3
  screen running stageC since14:05 PDT after stagesA/B and zero missing incumbent cells; no duplicate panel.

## 2026-10-12 15:05 PDT — official Mend3 checks, published evidence and productivity diagnosis

- Full official suite PASS at644abde,14:31:26–14:53:59 PDT, same start/end HEAD,80packages +852Mend3checks, all
  tool/replica checks; no timeout. Canonical driver nowmain with live data preserved. Artifact unit-20261012T213126Z.
- Main920aea3:17,701rawgames (+1993),1,006 replay-gap audit records,21 recovered reports; consistent chart set
  captured14:42. Fresh rankings#28/88 rating1568.6,501rated matches latest14:11Oct12. Earlier#5snapshot is historical.
- Official Mend3 method117repeated cases: no drift/common decision changes, allpendingdebt0;18fallbacks,3returns
  below6000,min5912. Safe-nearest331both, visiblebypass335vs332, second-safe619vs332; method-entry budget differs
  from later fallback-entry budget. Full live delivery pending, no trial. Exact artifacts and standalone probes
  exportedunder research/diagnosis/2026-10-12; CBC results retain58finite-budget list differences/192cases.
- Native host blind-cooldown13cases/205assertions PASS onofficial5d4/JDK8: clear hidden hit20,CD0->10->0; forced
  cloud control0->12->2. Strictsum<=10 correctly rejects later debt. No metered hook cost or bot change claimed.
- Forest4566/4570g4: actualown carriers95/96atr1000, favorablecombat but poorcollection; earlyequal-worker
  populations alreadylag productivity. G trace moving-turn ABA19.1%/14.8%; repeated(5,20) empty-cargo episodes
  last342/417/297rounds with observedG335/409/291 and freeendroundneighbours. Roles/goals andin-turnmovesunknown;
  IDsdivisibleby4 may beAD carriers. InspectField/Carrier.moveTwice cancellation andstaticwalls; do not attribute
  these to currents or a mana target without evidence. Physical well footprint andnativeown-only route fixture next.

## 2026-10-12 15:20 PDT — Forest routing falsifier and native workload launch

- Official headers: both existing Forest game4 terrain hashes equal built-in;4 checks,zero rounds walked. HomeMn6clear cells; centralpair12distinct cells, not18. Conditional standard resident benchmarks6/11.667kg/r; upgrades/current/turnover remain separate.
- Actual12004/11476 pickup atAD(9,21),11128none; allthreehaveADbirthassignment. Do not call(5,20)stall a directMn-route diagnosis.
- Official owned native fixture12cases366assertions confirms firstdetour/secondreturn cd0→5→10, but simpleveto fails firstcollection through64turns underpersistentblockers and suppressesunjam. Noarm/promote; nextvariant mustdeliver actualcollection/return. HostClock syntheticample, notinstruction-metered. Exactsource/result/manifest androutingreport published.
- Read-only API15:07: rank26/rating1581.1,latest6490 3–0 vsDukeBas at14:43; active145/noownpending. Recentmixedhigher-ratedopponents give lossrates butboundedwindow doesnotcausallydecompose fullrankdrop. No evidence ofVMoutage.
- CBCnative4own-archetype games launched15:15:35,supervisor291639,privateoutputcbc-native-20261012T221535Z/output,2jobs,600s games/45minsupervisor. NumericextractIDs fixed; exception/finalturncoverage censorcosts/callers/budgets. Firstarchivevalidationfailedpre-games; exactroot-directory+6fileverificationfixed,newrequestsuccessful. Mend3followonwillreusefirstMend2controlpair.
- Schema reminder: trips.collects iskg summed overtrip, coordinate/type isdominant only; action-level capacity attribution required for mixed/spanningtrips.

## 2026-10-12 15:43 PDT — centre Mana supply isolated; Ward3 closed FAIL

- Official field-action reader: zero unpaired pickups/well places, ten serialization fixtures,48 exact timeline reconciliations. OuronlyMana site through1000 ishome(8,12) in4566g4/4570g4. Enemycentrepickups first36/38 and125/196; centre903/544kg explainsalmostall945/471kg gaps101–250, home+42/−73kg. No upgraded/converted wells/deposits, allpickups1kg. Capacityreport/source/results published, discoveryvsselectionstillunknown.
- Sourceaudit: Mana no-alternative crowdswitch clearswell, butnextgather choosesrejectedknownwell beforeexplore; isolatedreachability/deliveryfixture next. KeepADroute andMana explorationarms separate.
- Officialowned native routefixture320cases/35,424checks,280firstdetours/240pretriggeridentities/28completeopen-downidentities, actual30kgdeposits40/40locked policies vs29/40baseline. TemporaryADblockers cost10r; native targetchangepathsnotyetexercised; budgets synthetic. Exactcase/sample exports plusfulltraceSHA3b386639... inoriginalartifact carrier-route-delivery-20261012T223859Z. Experimentalpackageimplementationpending, noaccept.
- Ward3normalcollector PASStransport/FAILscreen:8/8basics,9–11h2h,informationNet+2/gatingNet0,128games allzeroover/ex/selfdeath/near. No trial. Canonicalunique cache6572→6828,+256/no conflicts/originalprefixpreserved; rootcachealso6828unique. Finishedrecord/results committed.
- CBCfirstpair ordinarycontrolfinishedr2000/Mend2islandwin; profilingonexit1at15:23:34 after469.7s, confirmed JavaheapOOM whilewritingprofilerfooter. No onreplay/identity;CBCcandidatepairneverran. Preserve11.36MBoffcontrol/classes/source; on-only higherheap recoverywillrequire exactfingerprint/footer identity, stillcensor nativecaps. NoMend3followon launched.

## 2026-10-12 15:58 PDT — pre-register isolated c_route1 source

- c_route1 hash471eafaef776 copiesMend2 withonlyC/Carrier changes. Mechanism: outboundgather outsidecrowdband, exactactivewellfield/validwave/epoch/once-round memory;4eligible no-progress rounds thenexisting-handbug lockedthroughcollection/reset. Counterrr emittedwith600admission; absenceunknown. NoHQ/wellselection/role/Nav/Launcher changes/RNGdraws.
- Expectedtrigger: longempty-carrierfieldloops motivatingForestADhotspot; actualfieldfrequencyunknown. Sourceinstrument: officialnativeactual-source fixture, thenrealinstructionmeter andfixedown-vs-own delivery; fullunit+normalcandidate screen gate, nofieldtrialwithoutPASS. Price: extrafieldlookup/tracking/note, possiblelostbackgroundwork andtemporaryblocker10-rounddelay; guard6500/4000provisional. Falsifiers: overrun/exception,disabled-control drift,lowerMana delivery ornoresource improvementdespite rr/stallrescue. Dosezero=false,initialstall4,conservative8extensionpredeclared.
- Targeted54guard/counterchecks pass; disabled26originalCarrier methods/classinitializer symbolicbytecodeunchanged. Actual-source prototypeenabled48/48native30kgdeposits vs37/48baseline/disabled,48zeroidentities/pretriggeridentities,8real target resets. Officialactual-source fixture/full81-package suite/price/game delivery pending; candidateexperimentalnotactive.
- CBC on-onlyrecovery launched15:50,supervisor342825,privatecbc-on-recovery-20261012T225032Z-55d78b51:2048m/900s/onegame,offreused,frozenclasses/source. Identity/caps pending.
- Officialcrowdbranchfixture156checks/10scenarios confirms reachabilityrepair: original0explore/0kg vs3explore/discovery/30kg mockedtransfers. Actualown instructions/API charges; syntheticcontrollerbodyandphysics, notwhole-game delivery. Dedicatedc_explore1 preparation remains separate.

## 2026-10-12 16:12 PDT — c_route1 official actual-source native delivery

Request native-route1-delivery-20261012T231155Z, worker SHA10e8eb2f06cf421105b87e1a68c80d30b4809f349e4b93f473fba64e207f803c, official jar5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a. Pinned candidate471eafaef776 and base d62033781fbd, three private JVM/class trees.144cases: enabled48/48 actual30kgHQdeposits vs37/48base anddisabled;22enabled recoveries.48zero-arm/fulltrace identities,48pretrigger identities,48first-move identities,4free-route fulltrace identities;4before/4after actual switchWell resets. Native assertions6296base/6296disabled/4686enabled. Controlled occupancy/map knowledge and synthetic100000Clock budget; no sandbox instruction meter or fullCarrier.run. Temporary AD blocker remains10rounds slower (54→64). Published owned fixture/cases/sample/provenance in research/diagnosis/2026-10-12/carrier/source-route-*. Fulltraces preserved build/codex-recovery/carrier-candidate-route-v2-20261012T231243Z on both VMs. Full81package suite still running; instrumented cost worker failed before Java due nested newline quoting, repair pending. No screen/promotion; active145unchanged.

## 2026-10-12 16:24 PDT — CBC native recovery censored, Mend followon withheld

Read-only request inspect-route1-unit-cbc-20261012T232339Z, worker SHA4768f55b8d67936800baa410a4a8ac05a584d371e51cce3f77ff1878b845c625. Recovery completed15:56:07 in327.601s, one2048MB on-game, originaloff reused unchanged. State/bytecode/footer fingerprints identical (Mend2winsCornucopia byislands r2000). Both native profiles hit2,000,000OPEN events;0usable intervals and0aligned ownlauncher budgets. Native costs staynull, entry counts onlylowerbounds. Own575launchers/469309recorded turns,573zero-through-last-turn ex counters/2missing. No Mend3fullprofile pair from this control, no additional controlgame. Exact recovery hashes/provenance/caps preserved research/diagnosis/2026-10-12/native-profiler/recovery-result.json. DriverHEAD5d81f87, existing ranked controllerverified, active145 unchanged, full81package suite stillrunning throughmatchreports at16:24.

## 2026-10-12 16:28 PDT — route method costs and full suite pass

Official fixed worker meter-route1-cost-fixed-20261012T232352Z SHAcef2e4287caf2dcb47bdd3f5df375c04bad3425cf6e8703fd4c1cdd25816eced passed1077cases/4224assertions,0repeatdiff/0zero-armdiff,1031completed returns/debt0 and46explicit0/50-budget paused paths. Ordinary warmgather2775vs2619/cold3339vs3183 (+156). Locked gather902vs2352; lockedmovement691vs666. Synthetic399-wave stressgather10616from12500; note+4deferred/+11formatted,600admission notfloor. Actual native RC plus owninstructions/callsitecharges; initialization/G.startTurn/fullrun/scan/unjam/travel-tail/background excluded. Exactcases/provenance under carrier/source-route-cost-*. Privatefullresults build/codex-recovery/carrier-route-cost-20261012T232530Z. Fullsuite ondriver5d81f87 ran16:04:34–16:25:29 sameHEAD,81packages/54Route1/852Mend3 andall apparatus checks PASS. Preserved verification/route1-unit.json. Next completegame delivery and normal screen; activeMend2/145 unchanged.

2026-10-12 16:29 PDT label correction: the902vs2352 cost is recovery-entry gather (stall_enter_cached), while691vs666 is already-locked gather, not moveTwice. Values and scope unchanged; exact case JSON is authoritative.

## 2026-10-12 16:38 PDT — isolated blind-shot arm, method gate passed

Published experimental c_blind1 (9ce6956c844b) from frozen Mend2 d62033781fbd. Only C/Launcher change;13 other classes preserve normalized source. Hook follows all ordinary shots/movement; actual current square/team multiplier and cd+rounded cost<=10; clear shooter and legal hidden cloud target only. No RNG or movement/pursuit changes. Official request meter-blind-cost-20261012T232035Z, worker SHAd8bd7b6606177e13abcb410c21db644ca2f19eea3754a2a4a2598945998d590e:448cases/5770assertions, zero repeats, zero compiled220-original-method/15-class differences, max measured461, minimum firing return3867. First hidden shot+bs costs227; no-cloud168;12 sensable clouds455; period2/4 active+6, inactive11 with initial bs0. All fixture counters initially zero, inner scan guard unexercised; no whole-turn price. Native ordinary attack traces preserved. New targeted test SHA2d935ae29cc6c529e4cd21af02ec72fb42d17a1c9f12dbc7602d5ad28df6c2af has1804 local prototype checks; official full82-package suite pending. Preregistered SmallElements/Mend2+arch_ampmid/both-side zero/4/2/1 block, max20 complete games; controlled fullturn5arms/32rounds precedes natural delivery, explicit hidden20damage/useful hit, miss/ally0/CD0/action-counter/basics gates. Complete-coverage zero useful damage closes arm before score expansion. Source, official artifact and full preregistration in research/diagnosis/2026-10-12/blind-price/. No game, submission or promotion yet; active145unchanged.

## 2026-10-12 16:44 PDT — close twelve-round crowded-well discovery dose

Official request check-explore1-forest-20261012T233716Z, worker SHA942b9813c920b57a467d386a901378c82580661d4a5a288d22c11bd4902ae9e1, passed2,320native checks/331logical/222zero identities for scratch409cfdfcbfd8. Unknown Forest home(8,12), start(10,12), episode r50:11Xturns reach(22,33)r61, deadline r62 restores home; zero centre discovery/pickup/HQtransfer through32ticks. Explicit shared pair selects(29,48)r50, sensesr70, actually collects30Mn and transfers30toalliedHQ. Native actual RC/world and owninstructions, prescribed carriers/shared memory/occupants; RobotPlayer bookkeeping/exception/record/yield/scheduler omitted. Dense2442 gather leaves401 after measured helper tail from3100;4500→1617/4550→1681. No safe universalguard claim. Closed this dose as Forest supply repair withoutfield screen; source staysscratch. EvidenceSHA95be4afb4d7dbaed49a93bc5e7b7d445e39b575defabd2206b545ac5302f3037 and reproducible helpers/report published in crowd-search. Reopen only as separate live-map frontier policy with independently frozen dose/zero/native pickup-to-HQ gate; no Forest coordinate constants. Blind1 adoption succeeded ca7a850 preserving89livefiles/35screenstates/inodes/locks;82package suite started16:41:49 PID3081844. Route fullgame enqueue refused before anygame on olderVMReplayDump; private verified reader correction pending, not broadsync. Active145 unchanged.

## 2026-10-12 16:50 PDT — crowd fixture symmetry correction pending

Audit found NativeFixture inherited CarrierCrowdProbe MapMem.cand=1 (forced ROT) on Forest, whose valid reflection is cand2. This artificial memory state can alter navigation/field wall images. Original official409 source/result stay valid for their prescribed state and remain archived, but the16:44closure is now conditional; clean Forest closure awaits corrected native fixtures with unresolvedcand7/validcand2. Main report/HANDOFF annotated immediately. No candidate source change, field screen or promotion. Scratch frontier tests will use both corrected memory states too.

## 2026-10-12 17:04 PDT — corrected symmetry controls close crowd-search dose

Official request verify-explore1-symmetry-20261012T235508Z, worker SHAddfbd103b0260bf69bf194905f4ad7ba1dc97388816e1303b7a50c25c1bc8fcc, passed55native worlds/2,756checks plus331logical/222zero methods for unchanged409cfdfcbfd8. Fresh MapMem/Field and both initial7(unresolved) and2(validreflection) reproduce unknown0discovery/0pickup/0deposit, known r50select/r70seen/30pickup+30HQtransfer. Unresolved7narrows3; valid2retains2. Allsixlegalcollectionoccupants CENTER/0displacedrobot-rounds acrossfourcases. ActualNav/Field/exploretargets nowrecorded. Corrected artifactSHA239e956604db3b1a489edac1de4fed3d7452e3c4f618be51bc59ff554fbffbab/native57dc84b41b61b803b3236914b0671c002360977ca918db98974b2724608ee956, additivev2helpers/evidencepreservev1. Cleaninitialized-caseclosure restored; fieldknowledge remains unknown, nofield screen ortrackedfailedpackage.

## 2026-10-12 17:20 PDT — Blind1 full suite and controlled RobotPlayer delivery

Official82-package suite on canonicalca7a850 ran16:41:49–17:06:26, exit0/no timeout/sameHEAD. All1,804Blind1checks,54Route1,852Mend3 andcomplete apparatus suites pass; verification/blind1-unit.json preserved. Request verify-blind1-full-turn-20261013T001343Z SHA1f720682d5012171e989961eed2106b210f3e9ae819cbd9be1fee310a3aaeb77 passedfive32-round fullcoldSandboxedRobotPlayer fixtures. Exactbase/zero native state/API/bytecode/indicator/mapfieldidentity. Every-turn27blindshots/19hiddenhits/380native damage/8zero-damage misses/0allieddamage;4ordinaryvisible shots preserved.26schedulednextstartsCD0+1finalturnright-censored. Sparse4 gives6shots/80hidden damage;2 gives13shots/180damage. Mainworkmax4,562 vs4,336base; padded totals do notprice usefulwork. ColdMapMembacklog52vs51r2/26vs24r3 clearsr4, fieldwaves9vs10r5 andpartialrowlagr6 catchupidenticallyr7(19waves). Scriptedboxedactors/forcedcutoff do notestablishnaturalgame strength orharmlessplanningdelay. ArtifactSHA4676ddf483b78d0cebd52a64dcd4f4c87f45e8692261567a1a7f48fc1587ee54 retained; publicproofreport beingprepared. Nextalreadypreregistered naturalSmallElements baseline/zero/doses withusefulhit andplanning/outcome guards. No fieldsubmission/promotion;145 remainsactive.

## 2026-10-12 17:39 PDT — Publish controlled Blind1 evidence

The complete official full-loop artifact, independent planning audit and eleven reproducibility helpers are preserved in research/diagnosis/2026-10-12/blind-full-loop/. Verified all fourteen payload hashes before and after copying. Frozen manifest SHA256 3b5309d76da9fa09e0e6053df8c56de0f15e9cd236176f1494cfa63e076ada6b; native artifact remains 4676ddf483b78d0cebd52a64dcd4f4c87f45e8692261567a1a7f48fc1587ee54. This publication adds evidence only: no bot, protocol, submission or promotion change. Natural-game zero identity, useful hidden damage and planning/outcome guards remain required.

## 2026-10-12 17:42 PDT — Publish isolated HQ-derived Mana discovery arm

c_seam1 preserves frozen normalized source 5e11b3da11c9, based on Mend2 d62033781fbd; only C/Carrier differ after package normalization. Empty Mana carriers with the existing crowd trigger and no known alternative get a bounded 24-round search toward unknown HQ-derived midline waypoints. Retired coordinates exclude duplicate projections; role/cargo/new-well/episode/deadline resets and finite retreat preserve normal behavior outside the episode. Official method evidence 9e96568f809039d56cd507e0da990c44392ba378e0a5feb5e7bcfeb1a5b5678b shows 30 Mana collected and transferred under unresolved7 and valid2; zero and twelve-round controls deliver zero. It excludes complete RobotPlayer bookkeeping, catches, near-miss dispatch and scheduling. Measured gather maximum3272 and helper-tail minimum1161 are fixture results, not safety bounds. Seam1Test passes26 logical regression checks with the local source-built jar; official83-package full suite and full native delivery remain pending. All packet hashes verified before copying, with thirteen other classes unchanged. See research/diagnosis/2026-10-12-seam-search.md and seam-search/. No screen, submission or promotion; c_mend2/145 remains active.

## 2026-10-12 17:49 PDT — Recover usable sampled healing measurements

The sampled Mend2 control completed on the official engine with exact full state, metered-bytecode and footer identity against the preserved off replay. Three prospectively selected own launcher lifetimes are uncapped: 266,778 OPEN events and2,268 turns, aligned counters and final zero exceptions. The non-null no-op profiler preserves cached class instrumentation for all other robots. MendUpdate costs average26 instructions in this selected sample, mostly due-check exits;16 owned-target scan witnesses include subsequent march, objective selection and the Launcher tail. Remaining Launcher tail p90 is4,667 and maximum5,506; this is not a whole-RobotPlayer floor. These traces provide no blocked-nearest/fallback opportunity or population workload weights. Public evidence and exact reproduction helpers are in research/diagnosis/2026-10-13-c_mend3-sampled-control.md and its packet. Frozen Mend3 two-game candidate off/on run launched17:41:21, supervisor497217, one shared slot/nice5,2,048MiB,900seconds per game, zero new controls. Exact candidate pair identity and selected-ID coverage remain required before measuring fallback delivery; no candidate outcome inspected or promotion.

## 2026-10-12 18:12 PDT — Preserve completed Route1 and Mend3 limits

Route1 completed both normal Forest sides against frozen Mend2, losing each at round2000. It reported36/52 recoveries but deposited9,702/11,702 Mana versus16,591/14,112. Its overrun/exception/main-work near-miss/wrong-mask checks pass; the symmetry deadline fails1/2, with sideB at304. Opposing Mend2 sideB resolves350 in the other game, so this is not a new-code causal diagnosis. Exact completed CSVs/report/provenance are in research/diagnosis/2026-10-13/route1-full-bot/. Actor-specific deposits remain unknown while bounded saved-log extraction is repaired; no new games or wider value block.

Mend3 completed two off/on games17:52:55 with exact intra-pair state/bytecode/footer identity and complete uncapped three-ID cost scope. Its world-state fingerprint also equals the preserved Mend2 control. One measured fallback entry at11979/r1472 costs1,256 and returns7,293; selected MendUpdate and Launcher.run totals each increase594, while march/objective/after-mend tail totals stay identical. Selected target and causal healing delivery remain unknown; the20HP contextual healing window is not attributed to fallback. See research/diagnosis/2026-10-13/mend-sampled-candidate/. Incumbent c_mend2/145 stays active; neither candidate is promoted or expanded.

## 2026-10-14 08:30 PDT — CLI session resumed; replica restarted; c_bc3 rejected; trials resume
- This session (stopped by the weekly usage limit 2026-10-11 09:20) resumed after the owner's "try again" (PROMPTS
  76-81). The web/runner session's work (2026-10-12, PROMPTS 51-75) was fast-forwarded from origin/main (5f90d1c).
- The galaxy replica had been down since 2026-10-12 18:48 PDT: every galaxy unit stopped and postgresql@15-main masked
  at runtime (systemd journal), right after the other session's last API reads from the driver; no document or prompt
  records a reason. Its units were still enabled (a pause, not a teardown). Restarted (unmask --runtime, then postgres,
  hostname, web, relay, saturn, scheduler timer, caddy); the API answers; the ranked loop (dead since 2026-10-12 13:34
  PDT) restarted. No autoscrim or rated game ran for 38 hours.
- c_bc3 rejected (trial-decide 144): its panel matched c_mend2 game for game (61/100) with no measured benefit.
- Screens queued vs c_mend2 (reference cached): c_blind1 (blind shots at hidden cloud tiles with the free action:
  the owner's free-action principle, LEARNINGS 1), c_mend3 (second safe island when the nearest is contested),
  c_seam1 (Forest Mana search toward HQ-derived waypoints). Trials start after the 09:00 autoscrim, parked so the
  panels overlap.

## 2026-10-14 09:00 PDT — c_blind1 and c_mend3 trials parked; c_blind2 building
- The 09:00 autoscrim was created on c_mend2 (matches 6831-6951). trial-start c_blind1 (--skip-screen, reason
  recorded; screen running in parallel) -> panel 6982-6991, parked 09:01, c_mend2 active as 147; c_mend3 -> panel
  6992-7001, parked 09:01, c_mend2 active as 149.
- The blind-fire classifier and the token-race fix from this session's uncommitted 2026-10-11 work (archived by the
  web session in build/codex-recovery/20261012T191037Z) are superseded on main by the web session's own versions
  (ReplayDump --shots, census shot_visible/shot_outside_vision/shot_visibility_unknown; contest._save_token with
  mkstemp; aa7470c). The archived patch is dropped.
- c_blind1 aims at unseen cloud tiles by a rotating index (no prior) and never from a cloud. Workflow wf_2d77b4f5-efd
  builds c_blind2: memory targeting first (the last-seen tile of an enemy fighter that went out of sight within 6
  rounds, also from inside a cloud), then c_blind1's scan; the field's shooters aim at remembered positions.

## 2026-10-14 10:02 PDT — c_seam1 trial parked; c_blind2 built; rating and limit questions (PROMPTS 85-87)
- trial-start c_seam1 (--skip-screen, reason recorded) at 10:01 after the hourly unranked limit reset; panel
  7002-7011; parked 10:02 (c_mend2 active as 151). Three panels play: c_blind1, c_mend3, c_seam1.
- c_blind2 (workflow wf_2d77b4f5-efd): c_blind1 + memory targeting (8 slots of enemy fighters' last-seen tiles and
  last move direction; shoot the most recent hidden one within r2 16, also from a cloud when the cooldown fits;
  C.BLIND_MEM_DEBT 0 keeps the strict cooldown rule, so a cloud tile's 1.2 multiplier blocks most in-cloud shots).
  The review capped a 9,857-bytecode all-candidates-visible spike at ~1,400 (one pass, memLast skip); Blind2Test 163
  checks. Full unit tests running.
- The hourly request limit is siarnaq's own per-episode cap (ranked/unranked_scrimmage_hourly_limit, defaults 10/10),
  set to 20/40 on the replica (PROMPTS 15-16); a 10-match panel counts 20 (requests plus created matches).
- Bradley-Terry vs galaxy Elo: held-out accuracy test running (workflow wf_ca33769b-078). Galaxy's Elo with K 24
  reverts about 3.5% of a gap per match (time constant ~30 matches, ~half a day at our pace) and wanders about +-26
  points at equilibrium (3-game shares), several ranks on its compressed scale; each new build restarts from the
  team's rating. Planned: a ranked selector that maximises expected rating gain, 24 x (P_BT - E_galaxy), and
  declines incoming ranked challenges with negative expected gain.

## 2026-10-14 10:35 PDT — usage audit (owner, PROMPTS 88)
- Workflow wf_066b5a64-a7a (tally on Sonnet, recommendation on Opus). The first week held about 265M list-price units
  and ran out after 4.0 days; 56% was one-off setup. Steady state (10-09, 10-10) ~35M a day: at the edge of 7 days.
  Biggest avoidable costs: workflow agents waiting inside a turn (5-minute cache rewrites, 18%); main-context reads
  at a median ~600k (20%); fixed-interval checks; background-job wake-ups (9%).
- Agent-side changes adopted: workflow agents never wait more than ~4 minutes in a turn (queue, stop, collect with a
  fresh agent); Sonnet/medium effort for mechanical stages (rebase, compile/test, tallies), Opus for diagnosis,
  judging, design and review; one reviewer for small diffs; one shared digest per diagnosis run; chained background
  steps. Planned: an event watcher, a cron progress refresh, a weekly budget meter. Owner-side (suggested): earlier
  auto-compaction (autoCompactWindow ~300k, untested name), cancel the 2-hour refresh loop, task check every 55 min.
  LEARNINGS 3 "Budget".

## 2026-10-14 10:40 PDT — BT predicts better than galaxy Elo (held out); stuck match 6282 cancelled (rating 1581 -> 1654)
- Workflow wf_ca33769b-078 (measure + independent verify, scratchpad btacc/). Per game, our matches after 2026-10-10
  00:00 PDT (378 matches, 1,834 games), BT fitted only on earlier matches, galaxy from pre-match ratings (siarnaq's
  expected_score, n rebuilt; reproduces all 12,724 rated updates): log-loss galaxy 0.628 vs BT 0.572 (rolling;
  difference -0.056 [-0.072, -0.041]), accuracy +3.1 points; ranked only 0.640 vs 0.605; c_mend2 0.616 vs 0.576;
  second cutoff 2026-10-11 12:00: 0.614 vs 0.568. Galaxy's gaps are too narrow on unranked panels (calibration slope
  2.8), but on ranked games its scale is about right: there BT wins because it ranks opponents with less noise.
  Stability: c_mend2's galaxy rating ranged 191 points over 33 hours of unchanged code; BT within ~6 galaxy-equivalent.
  BT's ranked bias +0.038 [+0.009, +0.067] of win share at the first cutoff, mostly c_def3 and c_aura2 (builds
  validated after good panels run high early); c_mend2 +0.015. The test covers opponents ranked 1-44 of 87 only.
- The verifier found ranked match 6282 (AnOvercookedFork.quals vs battlecode-archive.sprintBot, created 2026-10-12
  09:00 PDT) stuck in RUN, blocking every later rating in creation order (172 finished participations unrated; ours
  frozen at 1581.07). Staff Cancel + Recalculate ratings (galaxy's own admin actions, via the Django shell as
  bcreplica), as for 2565 and 2593 (2026-10-09): our rating 1654 a minute later. sprintBot games are the slow ones;
  the planned event watcher must flag any match in RUN for more than 2 hours.

## 2026-10-14 10:55 PDT — event watcher replaces the task-check loop (owner, PROMPTS 90)
- tools/watch_events.py: exits on the first new event (PANEL_DONE, SCREEN_DONE, STUCK_MATCH > 2 h, RANKED_DEAD,
  REPLICA_DOWN, VM_DOWN) or a 50-minute HEARTBEAT; completions are reported once (build/watch-events.seen); the
  stuck-match scan reads the newest 400 matches every 15 minutes. CLAUDE.md rule 7: never end a turn without it (or
  another background job) armed; on a HEARTBEAT take the next target from TRAINING_ALGORITHM §2. Tests:
  WatchEventsTest (stuck matches, panels done, dedupe, seen file).

## 2026-10-14 11:46 PDT: ranked opponents by expected gain; watcher stuck-match fix

- `ladder_policy ranked` now challenges the open team at or above us with the largest expected gain 24 (P_BT - E_galaxy)
  (BT refit hourly from progress/games.csv), and sends nothing when no gain is positive; without a BT estimate it falls
  back to the 3 closest teams above. Today c_mend2 (galaxy 1654): 11 of 13 teams above offer -2 to -6, NotLLeon.v7 +3.1,
  CyrilSharma.finalBot -0.4. Galaxy's scale is compressed (BT 290 points across those teams, galaxy 120); all 73 teams
  below offer +0.3 to +8.5 when they challenge us, so incoming ranked stays on auto-accept (docs/LADDER_STRATEGY.md).
- tools/watch_events.py: STUCK_MATCH now means seen in RUN for over 1 hour (first-seen map in build/); its first run
  flagged 90 QUE matches that were only waiting behind the 09:00 autoscrim. New QUEUE_STALLED: QUE over 2 h with
  nothing RUN.
- Unit tests PASS.

## 2026-10-14 12:22 PDT: VM queue runner was down two days; QUEUE_RUNNER_DEAD alarm; HANDOFF refreshed

- The VM queue runner exited on a STOP file at 2026-10-12 18:48 PDT (the same minute every galaxy unit stopped); the
  four screens queued this morning (c_blind1, c_mend3, c_seam1, c_blind2) sat pending. Restarted at 11:47 PDT; the
  c_blind1 screen runs. tools/watch_events.py reports QUEUE_RUNNER_DEAD (jobs pending, queue/.lock free).
- HANDOFF.md rewritten for 2026-10-14 (old in-flight section archived in research/diagnosis/2026-10-12-handoff-inflight.md);
  tools/progress-refresh.sh added (from the session scratchpad). LEARNINGS: liveness alarms. Unit tests PASS.
- 2026-10-14 12:30 PDT: watcher STUCK_MATCH 6932 (field ranked maxwelljones14 vs battlecode-archive.sprintBot, RUN 67 min while the 5 others had just started); cancelled and re-rated (second sprintBot hang after 6282).
- 2026-10-14 13:10 PDT: progress refresh: 1,645 games from 546 matches into games.csv; Elo, field score, rating history, ladder snapshot regenerated. The match-report sweep was stopped by Claude Code under driver memory pressure (2 GB) and is not restarted until the owner asks.

## 2026-10-14 13:22 PDT: free-action audit (owner principle 1), carriers and HQs

- Carrier throws (up to 50 damage; cargo is lost on death anyway): c_mend2 already throws at w >= 8, threat r2 <= 9,
  HP <= 60. Since 10-11 (797 games, telemetry_query deaths): our carriers die 35.3 a game (them 54.7) but lose only
  95.6 Mn of cargo a game in all (under 3 kg each), so a wider death-throw adds little. Anchors lost 1.3 a game (them
  1.1) is the larger leak: escorting or routing anchor carriers, not throwing.
- HQ: action CD 2, its only actions are builds (the damage aura is passive); amplifier has no action. No other idle
  free action in the rules (RULES 2, 5.2). Not pursued.
- Anchors: 1.3 lost a game (160 Ad+Mn each) vs them 1.1, after c_anc3's courier survival rules (from 9.5 of 12.4 in losses): no clear gap left. Audit closed; next target from the panels.

## 2026-10-14 13:23 PDT: c_blind1 panel (gauntlet/20261014-160033-panel-c_blind1): 63/100, mechanism inert

- Paired: vs c_mend2 net +2 (+0.71 SE, 5-3), island-rounds -68 (t -0.62); vs c_bc1 net +5 (+1.51 SE), +115 (t +1.02).
- Mechanism: our shots 1,611 -> 12,537 a game, 10,551 outside vision, of which 20.2 hit (0.2%; ~400 damage, ~1% of our
  33.7k). Paired against c_mend2: damage +96 (t 0.07), kills +2.2 (t 0.24), hits +2.7 (t 0.03): no measurable effect.
  Launchers built 154 -> 145. Basics: 0 overruns, exceptions, self deaths.
- Held parked: decide together with c_blind2 (memory-targeted blind shots), whose panel is still playing.

## 2026-10-14 13:53 PDT: c_mend3 rejected (gauntlet/20261014-160116-panel-c_mend3, 61/100)

- vs c_mend2: 98 identical, net 0, island-rounds +3 (t +0.10), 82 identical margins; vs c_bc1 net +3 (+1.34 SE),
  +187 (t +2.32). Healed HP +97 a game (t 0.6), kills +2.1 (t 1.2), damage -225 (t -0.4); 0 overruns/exceptions.
  The second-safe-island fallback almost never fires on the panel: no measurable effect. Rejected (trial-decide 148).
- c_blind1 screen PASS (h2h 11-9, roster info Net +2, 128 games 0 overruns): progress/screens/c_blind1-9ce6956c844b.json.

## 2026-10-14 14:55 PDT: c_seam1 rejected (gauntlet/20261014-170135-panel-c_seam1, 59/100); c_seam2 built

- vs c_mend2 net -2 (-0.53 SE, 6-8), island-rounds -62 (t -0.53); vs c_bc1 net +1, +122 (t +0.94).
- Mechanism works on Forest (10 cells): Mn collected by r250 +285 (t +2.58), carriers built +35 (t +1.4). It costs
  elsewhere (90 cells): Mn by r100 -19 (t -3.48), Mn collected -357 (t -1.89), launchers -8.9 (t -2.41).
  0 overruns/exceptions. Rejected (trial-decide 150).
- c_seam2 = c_seam1 with the crowd search started only when no other Mana well is in the shared array (Seam2Test).
- 2026-10-14 15:19 PDT: c_seam2 screen refused: VM disk 1.54 GB free (20 GB, 92% used). The operator crontab on the VM is
  empty: the 6-hourly tools/galaxy/prune_replays.py job last ran 2026-10-12 17:30 PDT (lost in the 10-12 18:48
  outage), and field-vs-field replays have accumulated (/srv/bc23-galaxy 5.0 GB). Running the prune and reinstalling
  the crontab were both denied by the session's permission classifier: waiting for the owner.

## 2026-10-14 15:19 PDT: c_blind2 and c_blind1 rejected; c_mend2 stays validated

- c_blind2 (gauntlet/20261014-172209-panel-c_blind2): 100 of 100 outcomes identical to c_blind1; vs c_mend2 net +2,
  island-rounds -126 (t -1.26), damage -980 (t -0.88), kills -4.4; outside-vision hits 23.7 a game (c_blind1 20.2) from
  11,260 such shots. Launchers built -5.8 (c_blind1 -8.9). 0 overruns/exceptions.
- Neither blind-fire arm shows a measurable effect on damage, kills or margins (LEARNINGS 1: ~1% of damage), so neither
  is accepted on a +2 net that is within noise. Both rejected (trial-decide 152, 146). The principle stays: free actions
  are worth auditing, and this one was audited.
- 2026-10-14 15:20 PDT: c_seam2 trial started (--force: parked within a minute; --skip-screen: VM disk) and parked: submission 154, panel matches 7022-7031, run gauntlet/20261014-221959-panel-c_seam2; c_mend2 active again as 155.

## 2026-10-14 16:18 PDT: c_seam2 rejected: identical to c_seam1 on all 100 cells; Forest-mana line closed for now

- Panel gauntlet/20261014-221959-panel-c_seam2 (submission 154, matches 7022-7031): every game has c_seam1's winner and
  round count (100 identical margins), so the no-other-known-Mana-well gate never bound: each search c_seam1 started
  already had no alternative in the shared array. The off-Forest cost (Mn by r100 -19, t -3.5; launchers -8.9) comes
  from those searches themselves. Rejected (trial-decide 154); its queued screen cancelled.
- VM disk: the owner ran tools/galaxy/vm-prune.sh: 657 field replays, 2.0 GB freed (3.4 GB free, 82%). Its cron line
  lost the path's quotes (open(/home/...)); fixed with tools/galaxy/prune-local.sh, reinstall pending.
- 2026-10-14 16:24 PDT: owner reran vm-prune.sh --install-cron: crontab now '30 */6 * * * bash .../tools/galaxy/prune-local.sh' (0 replays due; 3.4 GB free).

## 2026-10-14 17:12 PDT: carrier gap diagnosis; c_cap1 built (CAP_MAX 30 -> 45)

- telemetry_query econ since 10-11 (1,177 games): Mn@250 +204 vs opponents, Ad@250 -264, carriers built 60 vs 109.
- c_mend2 panel by result: in the 39 losses opponents build 158 carriers to our 62 and collect 4x our Mn, while our
  HQs end holding 1,269 Ad unspent (391 at r500): Ad is not the late constraint. Late HQ turn-end reasons: cap 'c' 21%,
  threatened 't' 35%, poor 'p' 30%; HQ enemy pressure r2<=9 965 vs 63.
- c_cap1 = c_mend2 with CAP_MAX 45 (census slot is 16-bit); Cap1Test; unit tests PASS. The 't' withholding is next.
- 2026-10-14 17:14 PDT: c_cap1 trial parked: parked: c_cap1 (submission 156) since 2026-10-14 17:14 PDT: panel playing (run gauntlet/20261015-001351-panel-c_cap1, trial-start pid 3224890)

## 2026-10-14 17:58 PDT: c_thr1 trial parked (submission 158, panel 7218-7227)
c_thr1 = c_mend2 + a threatened HQ still builds a carrier when a free spawn tile is out of reach (r2 26) of every
visible enemy fighter (HQ.safeCarrierTile; unsafe when bytecodes are short). Target: the 't' withhold reason, 35% of
late HQ turns in losses. Test: test/bot/Thr1Test.java. Screen 20261015-005655-scr-c_thr1-b63813a927a3 queued.
c_mend2 active again as 159. Judge by paired.py vs c_mend2/c_bc1 panels; mechanism: built_C, coll_Mn, reason 't'.
- 2026-10-14 18:22 PDT: watcher STUCK_MATCH 7035 (field ranked battlecode-archive.sprintBot vs pranayagra.finalbotfinaltwo, created 17:00 PDT; third sprintBot hang). New tools/galaxy/cancel-match.sh <id> [--cancel] (the 6932 method as one command); the cancel was denied by the permission classifier, owner asked to allow Bash(tools/galaxy/cancel-match.sh:*).
- 2026-10-14 18:53 PDT: owner ran tools/galaxy/cancel-match.sh 7035 --cancel: 7035 RUN -> CAN, re-rating requested.

## 2026-10-14 18:54 PDT: causal graph of panel losses, first pass (owner, PROMPTS 101-102); c_ad1 held
- tools/causal_dag.py: 2,000 games (836 losses), 20 panels on the same 100 cells; nodes "trail by T in X at round R",
  Mantel-Haenszel risk differences within cells; edges = onset of B after A, same cell. Backward-walk roots: Mn@200
  219, Mn@50 82, Army@100 82, Mn@100 69, Calive@150 61. Main chain: Mn behind by r200 -> launchers alive behind
  r300+ -> loss. Adamantium is NOT a loss root: Ad@100 behind has within-cell RD -0.19 (behind in 69% of wins).
  So c_ad1 (more early Ad) is unsupported: held, not submitted (owner: only submit on a positive result).
- Mn@200 decomposed within 41 mixed cells (research/diagnosis/causal-mn200.py; loss minus win, same cell): our Mn
  -132, theirs +90; carriers built equal (-0.1) but we lose 1.2 more and they lose 2.4 fewer (alive gap 3.9); our Mn
  per carrier-round -3.6 (38 per 100); launchers built -2.1, kills -2.7 vs their kills +2.5. Losses are decided by
  the early fight war over carriers and launchers, not by build counts. Next: which early fights (engagements.csv)
  separate them; candidate only if a cause is found and fixable.
- 2026-10-14 19:23 PDT: causal-graph drill-down (research/diagnosis/2026-10-14-causal-dag-feasibility.md, "First run"): Mn@200 root
  -> carriers dying, not built; enemy carrier kills are mostly a consequence of fight wins (stratified -2.4 -> -0.67);
  early fights lost by reinforcement rate (fights 57 rounds longer, enemy feeds 9.8 more launchers in), not first hit
  or start numbers; divergence starts r60-100 as ~2 rounds more waiting a trip. No single fixable root: no bot from
  it (owner: submit only on a positive result). Forest "stuck" trips are the map (our median trip 87, theirs 92).

## 2026-10-14 21:11 PDT: c_cap1 rejected (panel 7208-7217)
- vs c_mend2: identical 98, gained 0, lost 2, net -2 (-1.41 SE); island-round margin -188 (t -2.63). vs c_bc1: net +1
  (+0.45 SE). Mechanism (census, our rows, 100 cells): carriers built 70.8 vs 60.6 (42 cells changed), but Ad
  collected +473 and Mn -350, launchers built 144 vs 154. The extra carriers mined adamantium (AD flag while under the
  cap) and paid for themselves in Ad, not in Mn: more carriers without more mana. Rejected. Consistent with the
  causal graph: the gap is mana and fights, not carrier count as such.

## 2026-10-14 21:37 PDT: c_thr1 rejected (panel 7218-7227)
- vs c_mend2: identical 93, gained 3, lost 4, net -1 (-0.38 SE); island-round margin -69 (t -0.92). vs c_bc1: net +2
  (+0.71 SE). Mechanism: carriers built 64.5 vs 60.6 (55 cells changed), Mn -203, Ad +10, launchers 149.7 vs 154.0.
  Like c_cap1, more carriers cost launchers and did not raise mana. Both carrier-count arms are closed: the
  withheld-carrier and cap reasons were not the binding constraint on income (see the causal-graph run).

## 2026-10-14 22:50 PDT: plateau step 4 (copy the offence that beats us): c_open1, carrier-first opening
- 26 of 100 panel cells are lost by nearly every build since c_anc3; 8 are awesomelemonade.finalBot's (jmerle 5,
  vrangr1 4). Against them (296 games): first 12 builds L 3.6 vs our 7.9 (they open CCCC LLLL, noted 2026-10-10 but
  never tried); C alive@100 +1.1, Mn@100 +49, L alive@150 +3.6, carriers built 90 vs 35; fights won 71%, first hit
  0.68, and at every dN they win 10-20 points more.
- c_open1 = c_mend2 + through round C.CARRIER_FIRST_UNTIL (10) the HQ builds a carrier before a launcher when both
  are affordable. Open1Test; unit-tests PASS. Local DefaultMap vs c_mend2 (one game, a check only): r50 carriers 13
  vs 11, launchers 14 vs 12, Mn collected 353 vs 297; lost r581 on islands.

## 2026-10-15 03:59 PDT: c_open1 rejected (panel 7404-7413 area, gauntlet/20261015-080211-panel-c_open1)
- vs c_mend2: identical 85, gained 5, lost 10, net -5 (-1.29 SE); island-round margin -492 (t -3.42). vs c_bc1: net
  -2 (-0.50 SE), margin -309 (t -2.24). awesomelemonade 1-2: the opening did not touch the cells it targeted.
- Mechanism (census, 100 cells): carriers built 60.0 vs 60.6 over the game, launchers 145.9 vs 154.0, Mn collected
  -475, carriers died 36.6 vs 33.6, launchers died 88.6 vs 81.8. The early carrier lead (r50 +2 locally) did not
  last: carriers built before the launchers die without cover, and the late launcher start costs fights. Copying
  awesomelemonade's build order alone does not copy their economy (their edge is fights at equal dN as well).
- 2026-10-15 04:00 PDT: equal-numbers launcher fights (last 12 panels; 1,997 won, 1,777 lost): our launcher-turn modes in the fight
  cells are alike (F 0.24/0.23, H 0.21/0.21, M 0.19/0.17, N 0.24/0.23) except regroup G 0.030 won vs 0.071 lost and
  outnumbered Fo/Ho 0.008 vs 0.046. Regroup runs only with no enemy in sight (a launcher left alone turns back), so
  it reads as an effect of losing allies, not a cause. No micro lever found in mode shares.
- 2026-10-15 04:36 PDT: plateau step 3 (API sweep): unused RobotController calls are adjacentLocation, canActLocation, canSenseRobot(AtLocation),
  disintegrate, get{Action,Movement}CooldownTurns, getAnchor, resign, senseAnchor, senseAnchorPlantedHealth,
  senseMapInfo, senseNearbyCloudLocations, senseRobot, setIndicatorLine. Currents are handled (MapMem). Well upgrades
  (1,400 own-type deposited: rate 3) are unused by us and by the field; payback ~470 rounds at our trip rates: not
  pursued. c_mend2 panel whole-game totals: wins us/them launchers 167/98, Mn 6,121/2,348; losses 134/296 and
  2,975/12,301. Losses end with the economy collapsed under siege (HQ pressure r2<=9 965 vs 63), the late state the
  causal graph traces to r150-300 fight losses.

## 2026-10-15 05:47 PDT: c_siege1, launcher batches under a siege
- c_mend2 panel deaths per game, losses vs wins: our launchers spawn-killed 17.6 vs 0.5 (~1,000 Mn a lost game),
  enemy launchers killed by our HQ aura 23.4 vs 0.6; HQ pressure r2<=9 965 vs 63. A threatened HQ built a launcher
  whenever Mn >= 45 and fed them one at a time into the siege.
- c_siege1 = c_mend2 + a threatened HQ with >= C.SIEGE_MIN (2) enemy fighters in view builds launchers only when
  it can spawn min(C.SIEGE_BATCH_MAX 5, enemies + 1) this turn (HQ action cooldown 2: 5 builds a turn, RULES 3.1).
  c_batch1 (2026-10-07, batches outside threats) failed because waiting delayed every launcher; this batches only
  where single launchers die at birth. Siege1Test; unit-tests PASS.

## 2026-10-15 06:32 PDT — c_siege1 rejected

Panel `gauntlet/20261015-124815-panel-c_siege1` (submission 162). Paired vs c_mend2: identical 93, gained 2, lost 5, net −3
(−1.13 SE), island margin −159 (t −1.54); vs c_bc1 net 0 (3/3). Mechanism did not engage: spawn-killed launchers per
lost game 17.0 vs 17.7 (wins 0.5 both), so the losses' spawn kills are not batch-able starts. Cost: launchers built
146.6 vs 154.0, Mn 4608 vs 4894, launchers died 80.4 vs 81.8. Holding mana under siege only delays production; the
spawn kills are a symptom of an already-lost front. Rejected; c_mend2 remains validated (sub 163).

## 2026-10-15 12:20 PDT — jmerle state-action study (owner, PROMPTS 108); c_well9 accepted (owner question, PROMPTS 109)

- New tool: ReplayDump `--sa` + `tools/sa_extract.py` write per-unit-turn state -> action rows for one team (state at
  the start of the robot's own turn; attack-before/after-move inferred from distances only). jmerle's side and ours of
  240 panel games: 11.1M / 3.8M launcher turns, 7.1M / 3.0M carrier turns (research/clone/jmerle/, gitignored).
- Launcher micro is close to ours, except blind fire (in-range turns on a cloud: jmerle attacks 85%, 34% hit; ours 31%,
  only when visible: about 570 damage a game, the c_blind1/2 effect) and pressing when outnumbered out of range
  (toward 33% / away 9%; ours 12% / 37%).
- Carriers: completed trips are as efficient (median cycle 48 vs 44, 0.55 kg a carrier-turn both); jmerle's small
  deposits were Ad and Mn handed over on separate turns. The gap is outside trips: through r600 our carriers spend 37%
  of turns empty and not collecting (jmerle 15%) and 14% on outbound legs that never reach a well (2%). Forest: 66% vs
  8%; one home mana well with ~5 open tiles caps us (2,510 Mn by r600 is about its ceiling); a VM Forest game showed
  77 of 95 carriers ping-pong G/W/S between crowded wells (one for 358 rounds), a symptom of saturation; jmerle doubles
  its Forest mana by holding the midline well (30,48).
- Map control decides it: in c_mend2's panel games jmerle collected 24,088 Mn on Cornucopia (ours 1,712), 10,483 on
  IslandHopping (480), 9,416 on Maze (1,980); we lost every carrier built there (57/57 on Maze; jmerle lost 1), killed
  by launchers in our half (prog 0.1-0.3) at age 10-20. Launcher positions in our losses: jmerle home/mid/deep 55/28/18%
  at r0-100 rising to 30/25/45% by r400; ours 78/14/8% to 59/4/37%, with 13-22% within r2 36 of their HQ.
  jmerle mines 89% mana (ours 69-81%; our Ad bank 184 at r400, 255 at r600 against its 40-75).
- Our record against the real jmerle by map (24 panels): win Cat 24/24, BatSignal 22/24, Hah 22/24, DefaultMap 17/24;
  lose MassiveL 22/24, Cornucopia, Forest, IslandHopping, Maze and ReverseFunnel 24/24: the fidelity target for a mimic.
- Next: arch_jm = c_mend2 + mana-first, blind fire, midfield front, press out of range; used only once c_mend2 vs
  arch_jm reproduces that per-map record on the VM.
- c_well9 (c_mend2 + c_well5's diagonal near-well probe only; its screen had failed 9-11 so it never had a panel; owner
  asked why c_well5 rates high in BT yet was rejected: one 64/100 panel, rating 2080 +- 88 vs c_mend2 2019 +- 42).
  trial-start --skip-screen 09:02 PDT (submission 164). Panel gauntlet/20261015-160249-panel-c_well9: 63/100; vs c_mend2
  90 identical, 6 gained, 4 lost, net +2, island-rounds +324 (t +1.61); vs c_bc1 net +5 (8-3), +507 (t +2.51).
  Mechanism: MassiveL Mn +2,841 a game (8,093 vs 5,252), launchers +23 there; Forest carrier deaths 70.9 vs 67.7 (no
  feeding); 0 exceptions. Accepted 12:18 PDT (trial-end --accept): g_iter11 = c_well9, submission 164.

## 2026-10-15 12:50 PDT: arch_jm built (jmerle sparring partner); carrier census vs jmerle
- arch_jm (99742df) = c_mend2 + c_blind2 blind fire (BLIND_MEM_DEBT 13), mana-first Ad (bank cap 80 = anchor), GROUP_MIN 2
  with a midfield front point (prog 0.5, +0.1 per 75 rounds from r150), close-in out of range (hp > 60). Driver game vs
  c_mend2 DefaultMap seed 1: lost (conquest r431), 0 overruns, 0 exceptions. Micro and mana share match jmerle (out of
  range toward/away 35-45%/2-10% vs 33-38%/7-13%; Mn share 0.85-0.88 vs 0.89); launcher positions do not yet
  (home/mid/deep r100-200 58/37/5 vs 45/29/26: c_mend2 besieged its exposed HQ and the raid recall pulled launchers home).
  Fidelity run queued on the VM: fid-arch_jm, c_mend2 vs arch_jm, 10 panel maps, both sides.
- Carriers alive / empty per game, r<=600, from the 240 panel games (jmerle side vs ours): Forest r300 jmerle 52/7, ours
  38/26; r600 85/12 vs 44/33. jmerle runs MORE carriers on Forest and nearly all are loaded; ours sit empty (collecting
  on 1% of empty turns vs 10%). Mn delivered by r600: 5,649 vs 2,510 (9.4 vs 4.2 a turn, i.e. one well's ~5 open tiles).
  ReverseFunnel 28/4 vs 22/11 at r300. Cause on Forest: we mine one home well; jmerle also mines the midline well. The
  cap formula (min(30, max((6 + r/50) x nHQ, 8 x Mn wells))) reaches 30 by r50 on 4-HQ maps whatever the well capacity,
  but extra carriers cost only Ad, which we cannot spend there anyway, so the fix is map control (midline wells), not
  the cap.
- 12:55 PDT fidelity (gauntlet/20261015-192936-fid-arch_jm, c_mend2 vs arch_jm, 10 maps x 2 sides, random seeds): c_mend2
  12/20. Agreement with c_mend2's record against the real jmerle on 12/20 games: matches on Cat, DefaultMap, Hah (we win)
  and Forest, Maze (we lose) both sides, IslandHopping and ReverseFunnel 1 of 2; misses BatSignal (arch_jm wins; jmerle
  loses 22/24), Cornucopia and MassiveL (arch_jm loses both at r2000 on islands; jmerle wins 24/24 and 22/24). Partial
  pass: the mimic reproduces the Forest and Maze losses with code we can read, so ablate it there next (abl-jm: c_well9
  vs arch_jm and four one-behaviour-off variants, Forest/Maze/IslandHopping/ReverseFunnel, paired seeds 1101/2202).

## 2026-10-15 14:40 PDT: mimic ablation finds our own Forest regression; c_well10 = c_well9 with hot wells off
- abl-jm and abl2-jm (gauntlet/20261015-194740-abl-jm, -203812-abl2-jm): c_well9 vs arch_jm, its four one-off and four
  one-on variants, and c_mend2 as control; Forest/Maze/IslandHopping/ReverseFunnel x 2 sides x seeds 1101/2202 (16 cells
  each). c_well9 wins: c_mend2 6/16 (Forest 0/4), arch_jm 5/16, one-off 5-7/16, one-on 6-8/16. No arch_jm behaviour
  carries the result: the control does as well. Maze goes by side (c_well9 wins as A, loses as B, every opponent).
- Mechanism (--sa collect sites, Forest seed 1101): c_mend2 and the mimic mine the midline wells (25-35,45) from r500,
  2,000-2,400 Mn per 250 rounds; c_well9 mines 35 there and only its home well (50,10), the other home wells fading after
  r500. c_well9 inherits c_well6's hot wells (C.HOT), added to stop c_well5's front probe feeding carriers on Forest; c_well9
  has no front probe (PROBE_FRONT false), so the mark only keeps carriers off the midline wells. This also explains the
  Forest carrier census above (33 of 44 carriers empty at r600).
- c_well10 = c_well9 with C.HOT false. Queued w10-jm (same cells vs c_mend2 and arch_jm; c_well9 had 6/16 and 5/16).
- The mimic idea (owner, PROMPTS 108) paid off as a diagnostic: playing a jmerle-like opponent made the Forest gap
  reproducible and the control exposed it as our regression, not a jmerle behaviour.
- 15:05 PDT w10-jm (gauntlet/20261015-214208-w10-jm, same 32 cells): c_well10 vs c_mend2 6/16 (Forest 1/4), vs arch_jm 5/16
  (Forest 1/4): identical totals to c_well9's 6/16 and 5/16. Hot wells off lets carriers mine the midline (its one Forest
  win: 1,900 Mn at (25-30,45) in r750-1000 while c_mend2 got 12 there), but who holds the midline is decided by the
  launchers, game by game. Forest is a midline-control map; HOT is not the lever. Screen queued for the 10-map record
  (20261015-215222-scr-c_well10).
- 15:25 PDT Forest's contested wells are the mana pair (29,48)/(30,48), top centre on the mirror axis (arch_jm's front
  point, the HQ midpoint, lies ~20 tiles south of them, so its front never engaged there). Units within r2 64 of
  (29.5,48), 24 panel games vs jmerle, average per round: jmerle launchers 1.9 (r0-100), 4.7 (r200), 6.9 (r500), 8.6
  (r600-700); carriers 1.8, 7.4, 15.2, 22.4. Ours: 0.0 launchers and 0.0-0.2 carriers in every bucket. Our launchers stall
  at 24-25 alive from r300 while jmerle's grow 38 -> 72. Next candidate: a contested-well objective (launchers hold the
  centre mana well and carriers mine it) on maps that have one.
- 17:30 PDT c_well10 screen PASS (20261015-215222-scr-c_well10): basics 8/8, h2h 11/20 vs c_well9 (PASS at 11), roster
  net +0 (arch_jm 1-1, arch_horde +1, arch_swarm -1), 148 games with 0 overruns/exceptions/self-deaths. Trial started
  17:32 PDT, submission 165, panel gauntlet/20261016-003246-panel-c_well10. Purpose: c_mid1 (contested-well objective,
  in build) sits on c_well10, so the panel measures what hot wells off costs or gains against the field first.
- 20:20 PDT c_well10 rejected (trial-end --reject; c_well9 resubmitted as submission 166). Panel
  gauntlet/20261016-003246-panel-c_well10: 62/100 (vrangr1 2, jmerle 5, georgezhang02 7, awesomelemonade 2, pranayagra 4,
  NotLLeon 7, Sprint1 10, reeceyang 9, yaonam 9, britacatalin 7). Paired vs c_well9: 95 identical, gained 2, lost 3, net
  -1; island-rounds -210 a game (t -2.12). Per map (c_well10 minus c_well9, per game): MassiveL island margin -1,429, Mn
  -1,784; Cornucopia -701 (carrier deaths -38); Maze -259 (carrier deaths +14); Forest +34, Mn +677, carrier deaths +17;
  DefaultMap +266, Mn +1,509. Hot wells earn their keep on MassiveL and Cornucopia; the contested-well candidate (c_mid1)
  must keep C.HOT on and exempt only a contested well our launchers hold.
- 21:54 PDT c_mid1 committed (10f9d74) and screened (20261016-045404-scr-c_mid1-5c619ca1048d). Built on c_well10 by a
  workflow (Mid.java site choice: a mana well in band p 35-65% under every surviving symmetry, beyond r2 64 of our HQs
  and every enemy HQ candidate, with a twin within r2 2; launcher squad id%3==0 on 100-round tours, holders within
  r2 20 outside a free zone of r2 8; carriers mine while screened, leave through home for 64 rounds when outnumbered or
  crowded), then rebased onto c_well9: C.HOT on, the site and its twin never hot (Carrier.front false there, Mid.update
  clears an earlier mark, hotLocal true there while a carrier avoids it). PROBE_FRONT on: the front probe is the only
  path that finds Forest's pair. Dev game before the rebase (c_mid1 vs c_well9, Forest seed 1): won r1738 by
  conquest, Mn 17,758 vs 5,519, launchers alive at r1000 139 vs 34, carriers lost 6 vs 157, 0 exceptions, launcher max
  bytecode 9,173.
- 23:07 PDT c_mid1 screen PASS (20261016-045404-scr-c_mid1-5c619ca1048d): basics 8/8, h2h 13/20 vs c_well9 (Forest 2-0,
  Cornucopia 2-0, MassiveL 2-0), roster info-only net +7 (arch_jm +4: 10 -> 14 of 20, ampmid/blob/horde +1, no
  losses), 148 games with 0 overruns/exceptions/self-deaths. Dev game vs arch_jm (Forest seed 1, after the rebase):
  won r1776 by conquest, Mn collected by r1000 9,517 vs ~4,600, launchers 115 vs 33. Trial waits for the 01:00 PDT
  autoscrim (2.5-hour window).
- 23:00 PDT spawn-camping check (jmerle sa data, the 4 latest panels): our launcher deaths on IslandHopping have median
  age 22 rounds (60% at most 30), 86% within r2 100 of our HQ, 67% alone; Cornucopia 33/47%/74%/51%; Maze 43/37%/84%;
  jmerle's die at median 127-313 rounds, 1-32% near its HQ. Alone in contact (no ally launcher within r2 20):
  IslandHopping ours 41-66% from r200 vs jmerle 10-13%. Not a new lever: c_siege1 (batching under siege) found the
  spawn kills to be a symptom of a front already lost; the cause is early map control (jmerle home/mid/deep 55/28/18%
  at r0-100, ours 78/14/8%).
- 23:45 PDT mid1-jm (VM gauntlet/20261016-061013-mid1-jm, the 32 abl2-jm/w10-jm cells): c_mid1 vs c_mend2 10/16, vs
  arch_jm 9/16, 19/32 (c_well9 and c_well10 11/32 each). Forest 8/8 (c_well10 2/8, c_well9 vs c_mend2 0/4); Maze 4/8,
  IslandHopping 3/8, ReverseFunnel 4/8: the other maps unchanged within noise. The contested-well squad fixes Forest.
- 01:10 PDT c_mid1 trial started 01:06 (submission 167, panel matches 8014-8023, run
  gauntlet/20261016-080646-panel-c_mid1) and parked; c_well9 active again as submission 168.
- 01:15 PDT site coverage: Mid.pick needs a well that is some HQ's nearest mana well (urgent) and beyond r2 64 of
  every HQ, so c_mid1 has a site only on Forest (HQ (11,48)) and Cornucopia (all three HQs); its screen games on
  BatSignal, Cat, DefaultMap and Hah are identical to c_well9's. Maze's mid wells fail it ((27,18) r2 45 from our HQ
  (21,21); (12,26) no HQ's nearest). ReverseFunnel home well (sa data, 4 panels, r0-600): carriers adjacent ours
  7.2/7.8/6.1 vs jmerle 8.1/8.7/8.7 per 200-round bucket, Mn collects there 5.9/5.8/4.6 vs 7.0/7.4/7.4 a round
  (jmerle 4,354 Mn a game there, ours 3,289): our home well runs below saturation.

## 2026-10-16 02:25 PDT: c_raid1 not superior locally; IslandHopping is lost to an early HQ assault; c_front1
- c_raid1 (d14555c) = c_mid1 + mana raid (C.RAID_MANA: a predicted mana well nearer an enemy HQ than each of ours is a
  raid candidate at any distance; other types rank after every mana well; the site excluded). VM raid1-jm
  (gauntlet/20261016-083137-raid1-jm: the 32 study cells + Cornucopia x c_mend2/arch_jm x A/B x 1101/2202): 19/40 vs
  c_mid1 22/40 (mid1-jm 19/32 + gauntlet/20261016-083254-mid1-corn 3/8). Cornucopia 4/8 (c_mid1 3/8; vs arch_jm 4/4 vs
  2/4), Forest 8/8 both, IslandHopping 3/8 both, Maze 1/8 (4/8: the army now tours five enemy mana wells across the
  maze), ReverseFunnel 3/8 (4/8; two games identical). Loss replays only (gauntlet wins are pruned without KEEP_ALL;
  CENSUS=1 from now on): Cornucopia's enemy Mn by r500 falls in 2 of 3 paired cells; IslandHopping's is unchanged
  (2,376-2,818 vs 2,135-2,838) because the game is lost before the raid starts (launchers at r500 1-6 vs 19-39 in both).
  Held, not screened.
- c_well9's panel by opponent: awesomelemonade 2/10, vrangr1 2/10, pranayagra 3/10, jmerle 5/10, NotLLeon 6/10, the rest
  8-10/10; by map Cornucopia and Forest 4/10. In contact our launchers hold (neither move nor fire) 35-41% of turns,
  the top teams 22-31%, the gap being their blind fire (rejected 10-14: c_blind1/2 inert).
- IslandHopping early collapse (c_raid1 vs arch_jm, s1101, side A): even at r50 (carriers 10/10, launchers 11/11), then
  the army marched on the enemy HQ (44,3) and lost 5 launchers to 1 at r2 37-81 of it in r78-95; kills by r150 10 vs
  21, launchers 10 vs 18, Mn collected equal (728 vs 765). Same shape in c_well9's panel game vs awesomelemonade
  (IslandHopping): ahead 14-10 in launchers at r150, then 12 launchers lost in the enemy half in r150-250 against 6,
  no robots left by r400 (Mn collected 859 in the game against 17,220).
- c_front1 = c_mid1 + arch_jm's midfield front (C.FRONT ported unchanged: the army holds a point 50% of the way from our
  HQ centroid to the siege target before r150, 60/70/80% from r150/225/300, raid and ring from r375). Front1Test 7
  cases. VM front1-jm on the same 40 cells with CENSUS=1.
- 03:15 PDT c_front1 not superior locally: VM front1-jm (gauntlet/20261016-092753-front1-jm, CENSUS=1) 19/40 vs c_mid1
  22/40. Cornucopia 4/8 (3/8), Forest 6/8 (8/8; arch_jm 2/4), IslandHopping 3/8 (3/8), Maze 1/8 (4/8), ReverseFunnel
  5/8 (4/8). Held, not screened. Maze falls to 1/8 under both army-objective changes (raid, front); its results go by
  side. Driver replay of the IslandHopping s1101 A cell (lost r655, same as the VM): launchers 12 vs 14 at r150, then
  12 -> 7 by r175 (B 14 -> 11), our carriers 14 -> 6 in r225-275 while B's rise to 18; collected Mn 1,261 vs 1,376 at
  r250, 1,786 vs 3,424 at r525; shots 323 vs 546 by r250.
- 03:15 PDT the losses to jmerle are mana stalls (c_well9 panel census): our collected Mn a game on Cornucopia 561,
  IslandHopping 480, Maze 1,972, Forest 5,410; jmerle 16,972, 10,483, 14,298, 18,069; every carrier we build dies
  (built = died, 53-65). Cornucopia (7601 game 2): ahead in the war (launchers 19 vs 9 at r100, kills 34 vs 24 at
  r150) but our Mn collection stops near r100 (412, then 561 flat from r200) while Ad mining goes on: the ring's mana
  wells are in the contested middle and all turn hot; c_mid1's site covers one of them. IslandHopping (7601 game 6):
  armies even, our Mn stalls at r125 (415; 459 at r300) while jmerle's rises 469 -> 1,675, its launchers parked on our
  home mana well (16,15) while our army is away. Our launchers answer sightings only within C.SIGHTING_R2 64 of
  themselves, and the c_def2 recall fires only on HQ alarms (enemy fighters outnumber ours in HQ vision) and rallies on
  the HQ tile, so a home well 12 tiles out is undefended. Neither jmerle nor awesomelemonade upgrades a well (every
  PLACE_RESOURCE target is an HQ).

## 2026-10-16 04:56 PDT: the losses are a production race lost at home; c_rally1 and c_guard1
- c_well9 panel census (gauntlet/20261015-160249-panel-c_well9, 37 losses / 63 wins, medians us vs them). Losses:
  r100 launchers 13 vs 11, carriers 12 vs 12, Mn collected 410 vs 497, Ad 86 vs 68; r250 launchers 13 vs 20,
  carriers 18 vs 22, Mn 1,125 vs 1,487, Ad 259 vs 390, banked Mn 250 vs 410; game totals launchers built 101 vs
  204, Mn collected 2,214 vs 9,236, carriers lost 46 vs 17. Wins: r100 launchers 16 vs 8, Mn 520 vs 347; r250 33
  vs 7. Start and passive income are 970 of our ~1,370 Mn by r100 (RULES 3.1), so mining decides from r100 on: the
  r250 launcher gap (7) is about the mining gap (362 Mn, 6 launchers).
- Deaths located in all 100 games (scratchpad cdeath.py: our and their deaths with distance from their own nearest
  HQ and map progress). Launcher trades in losses are even in every 50-round bucket to r300 (2.4/2.5, 5.7/5.8,
  6.4/6.4, 6.7/6.9, 7.3/7.0, 8.4/7.2), but their launchers die in our third of the map from r50 (2.1-3.1 a bucket):
  the war is fought in our half. Our carriers die about 2:1 from r50 (1.9-2.2 vs 0.9-1.0 a bucket). Carriers lost
  r0-300, losses: ours 10.7 a game (2.7 within 2 tiles of our HQ, 3.7 at 3-5, 2.9 at 6-8), theirs 5.8 (1.7 at 15+
  tiles: they mine far out); r300-600: ours 20.9 (13.3 within 5 tiles: spawn and deposit camping). Wins mirror
  it: their carriers 17.4 a game r0-300, 11.4 within 5 tiles of their HQ. Whoever wins the launcher war camps the
  other's HQs; the race is lost in r100-250 on production, not on trades.
- Cat vs vrangr1 (7600 game 1, lost r428, Mn 115 vs 3,170; one mana well, (20,31)): our two opening groups of 4 met
  the enemy one after the other (HQ (14,34)'s at r12-16, HQ (11,24)'s at r20-24) and lost 6 launchers to 2 in r20-38.
- c_rally1 (c_mid1 + retreat cohesion, C.KITE_RALLY/RALLY_HOME): an outnumbered launcher (enemies > allies + 1) that
  steps without firing scores tiles by threat, then r2 from the nearest fighter (cap 50) against r2 to our nearest
  HQ (cap 400; Launcher.kiteScore), where c_mid1 walked straight away from the fighter (Rally1Test 7 cases). VM
  rally1-80 (the 40 study cells + 40 h2h vs c_mid1): study cells 23/40 (c_mid1 22/40): Cornucopia 4/8 (3/8),
  Forest 8/8, IslandHopping 2/8 (3/8), Maze 3/8 (4/8), ReverseFunnel 6/8 (4/8); h2h running (Cat 0/3 so far).
- c_guard1 (c_mid1 + home-well defence, C.GUARD): writes need an HQ within r2 9 (RULES 7), so no robot ever reported
  raiders at a home well 12 tiles out. A carrier now keeps the fighter it last fled out of write range and reports
  it at its next write turn (within GUARD_REPORT_AGE 24 rounds); after the recall, a launcher takes a fresh sighting
  (stamp age <= 1) in our home zone (r2 GUARD_HOME_R2 200 of our nearest HQ and nearer it than every predicted enemy
  HQ) within r2 GUARD_R2 400 of itself when it is nearer than its site or siege target; forming and grouping
  unchanged; one that arrives and sees nobody skips that sighting until it is restamped (Guard1Test 8 cases). VM
  guard1-80 on the same 80 cells.
- 05:18 PDT c_mid1 trial rejected (submission 167, panel 8014-8023, gauntlet/20261016-080646-panel-c_mid1): 62/100
  vs c_well9's 63/100; paired: identical 97, gained 1, lost 2, net -1 (-0.58 SE); island-rounds -193 (t -1.30). By
  map Forest +1 (Mn +442 a game, enemy Mn -3,275), Cornucopia -1, MassiveL -1 (Mn -2,352, launchers built -32); the
  other seven maps identical or nearly (the site exists only where a mid-band mana well is some HQ's nearest). The
  local gain (jmerle-study cells 19/32 vs 11/32, Forest 8/8) was the mimic's Forest, not the ladder's. c_well9 stays
  validated (submission 168). c_rally1 and c_guard1 are c_mid1-based; off Forest, Cornucopia and MassiveL that base
  plays as c_well9.
- c_rally1 held: VM rally1-80 (gauntlet/20261016-105904-rally1) 41/80; study cells 23/40 (c_mid1 22/40), h2h vs
  c_mid1 18/40 (Forest 0/4, Cat 1/4, Cornucopia 1/4). Not locally superior.
- c_guard1 delivery (VM dev game vs c_mid1, IslandHopping 1101, won r673): 6 carrier reports 9-19 rounds after the
  sighting, 21 launcher guard objectives.
- c_guard2 (c_guard1 + a sentry amplifier per HQ, C.SENTRY): an HQ whose nearest shared mana well lies beyond its own
  vision (r2 > SENTRY_MIN_R2 34) and within GUARD_HOME_R2 200 builds one amplifier (30 Ad + 15 Mn) from r30 when no
  sentry heartbeat (AD_FLAGS bit 12 + HQ index, set every turn by the sentry, read and cleared by the HQ every
  SENTRY_CHECK 16 rounds) was seen and none was built since the last check; the sentry holds a post SENTRY_OUT 3
  tiles beyond the well on the HQ-well line and reports and backs away from fighters as amplifiers did
  (Guard2Test 13 cases). Delivery (VM dev game vs c_mid1, IslandHopping 1101, won r891): 2 sentries built r76, none
  died, 43 GUARD lines. VM guard2-80 on the same 80 cells.

## 2026-10-16 05:52 PDT: our carriers walk empty; Forest's home mana well is packed short

- Carrier turn use r40-200, our side vs jmerle's in the same games (research/clone/jmerle, panels from 10-14 on;
  scratchpad cecon.py): we collect on 0.36 of carrier turns to their 0.52 (Cornucopia 0.47/0.52, Forest 0.23/0.39,
  IslandHopping 0.31/0.52, Maze 0.51/0.68) and walk empty on 0.36 to their 0.10 (Forest 0.59/0.12). Mn collected a
  carrier turn: Forest 0.184 vs 0.315, Maze 0.400 vs 0.579, IslandHopping 0.209 vs 0.516. Their deposits are mixed
  (5 and 25-30 kg); ours are all 30 kg (CARRIER_RETURN_LOAD).
- Forest by well (9 games, collects a game per 100 rounds): our home mana well (8,12) gives 386-469, theirs (the
  mirror) 482-592; they also take 127-700 from the contested midline mana pair (29,48)/(30,48), we take 6 then 0
  (hot). At r47 of 7415 game 4 the well (8,12) had walls on three sides, five collectors on its open neighbours and
  the well tile empty, with two to three carriers queued behind; one carrier walked between home and that well from
  r3 to r200 without a single collect. Local census of c_rally1 (telemetry): carriers wait at a crowded well (W) on
  0.21 of turns on Hah, 0.16 ReverseFunnel, 0.13 BatSignal, 0.11 Cornucopia and Cat; go to a well (G) 0.42 on Forest.
- c_pack1 (c_well9 + well packing, C.PACK): within r2 8 of its well a carrier walks to the nearest free collect
  square (the well tile or a passable neighbour without a robot or a current) instead of at the well tile, holding
  while our carrier on the well tile is full (its exit must stay open); a collector with more than 5 kg of room steps
  onto a free well tile (not onto a current, nor into a cloud from clear air), so the square it frees takes a queued
  carrier (PackTest 7 cases).
- Trip phases r40-400 (scratchpad trips.py; outbound = deposit to first collect, return = last collect to deposit):
  ReverseFunnel outbound 16.8 turns for 1.4 tiles (jmerle 3.4 for 1.3), MassiveL 25.7 for 5.0 (15.3 for 2.5), Forest
  34.8 for 13.2 (10.7 for 8.1): our carriers queue or wander before their first collect. IslandHopping: 129 trips
  completed to their 521 with similar cycles (52 vs 55 turns) and similar carrier turns: ours move loaded on 0.32 of
  turns (0.22) and rarely deposit, the raider problem c_guard1/2 address. Cornucopia Mn per carrier turn is equal
  (0.436 vs 0.442).
- 06:20 PDT guard1-80 at 61/80: study cells 24/40 (c_mid1 22/40, c_rally1 23/40), h2h vs c_mid1 14/21 (Forest 4/4,
  Cornucopia 3/4, Cat 3/4). guard2-80 study 12/27 so far. c_gp1 = c_guard1 + c_pack1's packing (same code and
  constants; Gp1Test 15 cases: PackTest's and Guard1Test's): Forest's site pair has 8 usable collect squares (two well
  tiles, (29,47)/(30,47)/(29,49)/(30,49), two cloud squares; the others are currents) where c_mid1 kept 3.4-4.2
  carriers on collect tiles with 51-57 within r2 64 from r600.
- 06:23 PDT finished local gauntlets' replays pruned on the VM (owner, PROMPTS 113): 19 runs, free disk 1.6 -> 2.2 GB.
- 06:34 PDT c_gp1 delivery game vs c_well9 (Forest 1101): won at r2000, collMn 20,316 vs 7,089, cMn100 615 vs 378,
  cMn250 2,079 vs 1,088, L250 66 vs 44; midline mana 396-652 collects per 100 rounds and home well 477-545 (175-381 on
  well tiles); 0 exceptions, 0 overruns.
- 06:41 PDT guard1-80 finished 45/80: study cells 24/40, h2h vs c_mid1 21/40 (Forest 4/4, Cat 3/4, Cornucopia 3/4;
  DefaultMap, Maze, ReverseFunnel 1/4 each), so c_guard1 is c_mid1's equal head to head. guard2-80 stopped at 40 games
  (study cells 18/40: c_mend2 9/20, arch_jm 9/20): c_guard2 held. c_pack1's screen passed stage (b) (12 of its first 18
  games) and runs its roster stage. c_gp1's screen was first queued with --roster none, but a reduced record never
  admits a trial: cancelled and requeued with the full roster (job 20261016-134053-scr-c_gp1-5ab98ca6e5b2).
- 07:06 PDT field contrast on c_well9's panel (census, 100 games): 89 games end by conquest before r2000 (11 reach the
  tiebreak, 7-4), so island endgames are worth at most ~4 games. Per game they collect Ad 3,438 / Mn 5,938 to our
  2,005 / 4,686 (+40% resources). Launcher fights vs the three teams that beat us most (awesomelemonade 2/10, vrangr1
  2/10, pranayagra 3/10): they stand and fire on 0.33-0.38 of contact turns to our 0.17-0.20 and hold (no move, no shot)
  on 0.22-0.27 to our 0.35-0.40; kill conversion 0.86-0.93 to 0.69-0.74; awesomelemonade's exchange 1.91 to our 0.74.
  Every top team fires every turn: 55-69% of their shots hit nothing (pranayagra on Forest, 7604 g4: 166k unseen-square
  shots, 503 hits, plus up to 478 of unknown visibility, against 3,338 visible hits). Blind fire was already tried and
  rejected (c_blind1/c_blind2, 10-14: ~20 unseen hits a game, ~1% of damage); a c_blind1 rebuild was started by mistake
  and discarded before any change. No panel team collects elixir; pranayagra, vrangr1, georgezhang02 build amplifiers.
- 07:06 PDT awesomelemonade DefaultMap loss (7603 g3, r663): damage even to r250 (11.5k each, kills 57 vs 64), but
  their carriers 19-21 to our 11-14 from r150, Mn collected 2,116 to 1,618 by r250 (+31%), launchers 20 to 9 at r250;
  our army is gone by r325 and the HQs then build 2 launchers per 25 rounds into a 50-120 launcher siege. 6 of our
  carriers die by r72 (raids), 7 in r172-221, 17 in the r270-313 collapse. Our HQs withhold an affordable carrier under
  threat ('t') on 66% of HQ turns in r100-300 (c_thr1 and c_cap1, which built more carriers, were rejected: extra
  carriers did not raise mana). c_gp1's MassiveL debug game (vs c_well9, 1101): Mn 9,231 to 6,715, island-rounds 3,093
  to 2,315, lost the r2000 tiebreak 1-2 islands; no MassiveL economy problem in c_gp1.
- 07:02 PDT VM gp1-80: c_gp1 on guard1-80's 80 cells (seeds from cells, paired with c_guard1's 45/80).
- 08:06 PDT c_pack1 screen PASS (progress/screens/c_pack1-b6ac7e5c5e37.json): basics 8/8, h2h vs c_well9 13/20, roster
  info Net +3 (arch_ampmid +4, arch_jm +1, arch_adecon -1, arch_horde -1), 148 games 0 overruns, exceptions, self
  deaths. gp1-80 at 48 games: study cells 27/40 (c_guard1 24/40 on the same cells; arch_jm Cornucopia 2/4 vs 4/4).
- 08:20 PDT owner, PROMPTS 114: a practice session, so high-risk/high-reward attempts are welcome; new research project:
  random C.java constants, a Swiss tournament of 2^N bots (3 maps, both sides, the best bot included), and a panel run
  for a winner that is not the incumbent.
- 08:34 PDT parameter search tooling. tools/param.py: `make BASE NEW NAME=VALUE ...` builds a package with C.java
  constants overridden at build time (the engine passes bots only bc.testing.* properties, the same to both teams, the
  replica passes none, and javac inlines static finals, so a generated package is the only override the panel and
  ladder can run); `space` lists 73 numeric constants with ranges that hold c_well9's values (switches, dead constants,
  rule facts, bit layouts and bytecode guards left out) and 10 constraints (RING_MIN + 8 <= RING_MAX, MEND_HP + 20 <=
  MEND_FULL, PROBE_NEAR < PROBE_FAR, FIELD_NEAR_D2 < FIELD_FAR_D2, ANCHOR_START <= ANCHOR_BLIND_FROM, ...); `sample`
  draws uniform valid settings (SIEGE_ROTATE_FROM off with p 0.5). tools/swiss.py: init/run/standings/analyse/export;
  Monrad pairing without rematches, one seed per pair and map for both sides, points = games won, Buchholz, base first
  on ties; games take gauntlet.sh's machine-wide slots; replays reduced to census rows. Measured VM rate ~130 games/h
  across 5 slots (gp1-80 + c_pack1 screen: 200 games in ~85 min), so N=4: 16 bots (c_well9 + 15 variants), 4 rounds x
  8 pairs x 6 games = 192 games, ~2-3 h beside the c_gp1 screen; N=5 (480 games) would take ~5-6 h.
  Maps Forest (clouds, economy, r2000 mirrors), DefaultMap (small open), Maze (walls, navigation). Run
  gauntlet/20261016-153444-swiss-n4 on the VM (log logs/swiss1.log), seed 114.
- 08:34 PDT watcher bug: tools/watch_events.py's VM probe put the remote command in double quotes, so $(ls logs/...)
  and $f expanded on the driver (no screen logs there) and SCREEN_DONE could never fire. Fixed (single-quoted, tested),
  and SWISS_DONE <run> added (final.txt on the VM, no research/swiss/<run>/final.txt here).
- 08:43 PDT VM gp1-80 final: c_gp1 52/80 on guard1-80's cells (c_guard1 45/80 on the same cells): study cells 27/40
  (arch_jm 15/20, c_mend2 12/20; c_guard1 24/40), vs c_mid1 25/40 (Cat 4/4, Forest 4/4, Maze 1/4). c_gp1's screen
  56/120 through its roster part.
- 08:43 PDT c_knob1 = c_well9 with fight()'s two hard-coded micro thresholds as constants (C.AHEAD_MIN 2: step in to
  fire when ahead by 2+; C.HOLD_THREAT 1: else fire only from tiles at most 1 enemy fighter reaches). javap: every
  class's bytecode identical to c_well9's but C (the two new fields), so c_knob1 at its defaults is the incumbent.
  tools/param.py: optional space entries (AHEAD_MIN, HOLD_THREAT 0-3) used only for bases that define them.
- 09:22 PDT Swiss round 1 (48 games, 48 min; Forest 340 s a game at r1970, DefaultMap 77 s, Maze 60 s): c_well9 beat
  c_sw06 4-2; c_sw07, c_sw11, c_sw12 6-0; c_sw05, c_sw08, c_sw14 0-6 (two of them anchor from r160-168, base 250).
  c_pack1's trial parked 09:22 (submission 169, panel matches 8201-8210); c_well9 active again as 170.
- 09:47 PDT tools/param.py local mode (`swiss.py init --k K --always A,B`): each variant is the base with only K
  constants re-drawn (the --always ones among them), for a second, attributable search around the incumbent.
- 10:01 PDT c_gp1 screen PASS (job 20261016-134053-scr-c_gp1-5ab98ca6e5b2): (a) 8/8, (b) h2h 12/20 vs c_well9,
  (c) roster info Net +9 (arch_jm +5, arch_ampmid +2, arch_swarm +2), no archetype gate, (d) 148 games 0 overruns,
  0 exceptions, 0 self-deaths. Record progress/screens/c_gp1-5ab98ca6e5b2.json.
- 10:02 PDT c_gp1 trial started (submission 171, panel requests 4343-4352); trial-park queued to put c_well9 back
  once the panel's matches exist. c_pack1's panel (submission 169) still waits in the queue. If c_pack1 is accepted
  first, c_gp1 must also beat it (paired, same cells).
- 10:10 PDT idle adamantium as ammunition (a carrier withdraws 40 Ad from its HQ, transferResource(hq, AD, -40), and
  throws it for 50 damage), measured before building on c_well9's panel extracts (matches/7600-7609, hq.csv): in our 37
  losses the HQs end with 1,165 Ad unspent (median ~700) and enemy fighters stand within r2 9 of an HQ holding >= 90
  Ad in 2,783 HQ-buckets (520 Ad on average there), but only 96 of those buckets fall in r0-300; the rest are sieges
  of games already lost (enemy 157 launchers at the end). The lever acts after the turn (r215): not built.
- 10:10 PDT Swiss after round 2: c_sw12 and c_sw07 10/12, c_well9 9/12 (3rd), c_sw11 8/12. The three variants share a
  direction against c_well9: fewer adamantium miners (AD_EARLY_EVERY 9-16 vs 8, AD_LATE_EVERY 6-7 vs 4), higher
  carrier cap (CAP_MAX 39-43 vs 30), fewer per mana well (CAP_PER_MN_WELL 6-7 vs 8), later anchors (ANCHOR_START
  291-374 vs 250). It fits the census: we float Ad (bank_end_Ad 982 in wins, 1,165 in losses; theirs 361/507).
  c_adlo1 = c_well9 with AD_EARLY_EVERY 12, AD_LATE_EVERY 7, CAP_MAX 40, CAP_PER_MN_WELL 7, ANCHOR_START 330
  (tools/param.py make): delivery game vs c_well9 on DefaultMap queued on the driver.
- 10:14 PDT 'behind' engagements on c_well9's panel (matches 7600-7609, engagements.csv): vs awesomelemonade 328 of
  478 start with us outnumbered, median 0 of our launchers vs 9 of theirs, 303 in our own third of the axis, only 46
  by r300; vrangr1, pranayagra, jmerle, britacatalin, georgezhang02 alike (sizes 0 v 4-9, mostly own third, mostly
  after r300). They are sieges and raids with no defender, not fights we pick badly: the micro contrast measured on
  all engagements is mostly the late siege. The lever stays the r100-300 home economy (c_guard1, c_pack1, c_gp1).
- 10:33 PDT c_adlo1 delivery game vs c_well9 (driver, DefaultMap seed 1101): won by conquest r560; 0 exceptions, 0
  overruns; Ad bank r500 142 vs 560, 11 anchors built vs 0, C250 17 vs 10 (one game: no verdict). Screen on the VM
  after the Swiss frees the game slots.
- 10:36 PDT Swiss economy on rounds 1-3 (122 games, census.raw): c_sw07 0.83 of games, c_well9 0.65, c_sw11 0.65,
  c_sw12 0.61. Over the 16 bots (Spearman): AD_LATE_EVERY vs Ad share of collection -0.30 (the knob acts), vs games
  won +0.07; ANCHOR_START vs won +0.30 (the two variants anchoring from r160-168 are last); bank500_Ad vs won -0.15.
  The leaders' shared economy direction is weak evidence; ANCHOR_START is the clearest.
- 10:36 PDT tools/swiss.py init --pool A,B,... (with --k): local-mode variants re-draw only constants from the pool
  (plus --always); unknown names, --pool without --k and --k above the pool size are refused. For a second, focused
  search (e.g. the economy constants around c_well9). Unit test ParamTest.test_local_mode_pool.
- 11:16 PDT Swiss 20261016-153444-swiss-n4 DONE (owner, PROMPTS 114; 192 games 08:34-11:16 PDT, 0 exceptions, 0
  games without a result; research/swiss/20261016-153444-swiss-n4/: config, bots, games, census, final, analyse).
  Final: c_sw07 18/24 (matches 3-1-0), c_sw06 16, c_sw12 16, c_well9 15 (2-2-0, unbeaten, top Buchholz 59), c_sw15
  14 ... c_sw14 6. WINNER c_sw07, a variant: 66 of 73 constants differ from c_well9; it drew c_well9 3-3 (Forest
  1-1, DefaultMap 1-1, Maze 1-1) and won on its results against the other variants (Forest 5/8, DefaultMap 7/8, Maze
  6/8; c_well9 3/8, 6/8, 6/8: Forest is c_well9's weak map here as on the panel, 4/10). Side A won 108 of 192 (Maze
  41-23). Rank correlation with points over the 16 bots: FORM_MAX_TURNS -0.69, ANCHOR_PERIOD -0.61, SCOUT_FROM
  +0.60, MEND_HP +0.58, WELL_CROWD_PATIENCE -0.54, ANCHOR_GATE_UNTIL +0.50; at n=16 |rho| >= 0.50 is p < 0.05 and
  ~4 of 73 constants pass that by chance, none passes Bonferroni (|rho| ~0.78): no constant is established.
  c_sw07 exported as src/c_tune1 (tools/swiss.py export; header names the run): next, its panel trial (owner:
  "run that bot against the panel"), --skip-screen with the owner's reason, parked behind c_pack1 and c_gp1.
- 11:43 PDT c_tune1 (= c_sw07) panel trial started (owner, PROMPTS 114: "run that bot against the panel"):
  submission 173, panel requests 4353-4362, --skip-screen with the owner's reason; parked at once (panel matches
  8221-8230, bound to 173); c_well9 active again as 174. Three panels now wait in the replica queue: c_pack1
  8201-8210, c_gp1 8211-8220, c_tune1 8221-8230 (c_tune1 expected ~18:30-19:30 PDT). Its screen and c_adlo1's run
  on the VM for information (jobs 20261016-182059-scr-c_tune1-dbaa8dbe5c83, 20261016-182323-scr-c_adlo1-3abbc150aa18).
- 11:50 PDT Do screens predict the panel? Over the 20 trials with a 20-game screen and a panel (Spearman against the
  panel's paired net vs the incumbent): stage b (h2h wins of 20) +0.45, stage c roster info net +0.42; a z-score blend
  weighted 0.25-0.5 to h2h reaches Pearson +0.58-0.59 (c_anc3's +16/+9 carries much of it). Both local measures carry
  signal; neither alone is enough. c_well9's panel by opponent: vrangr1 2/10, awesomelemonade 2/10, pranayagra 3/10,
  jmerle 5/10, NotLLeon 6/10, the other five 8-10/10: the three teams that beat us most hold the gain.
- 11:58 PDT tools/race.py (new): successive-halving race of C.java settings against an opponent pool (default
  c_well9 + arch_jm + arch_swarm + arch_ampmid, the panel's 10 maps). A unit is (opponent, map, fresh seed) played
  from both sides; rung k plays the next units for the base (the control, never cut) and every live candidate, then
  the best ceil(keep x n) by games won go on; the table's net vs the base is paired. `analyse` gives the win share by
  level of each varied constant on rung 1 (all bots, same cells). The watcher reports RACE_DONE. RaceTest (6 tests,
  one end-to-end with faked games).
- 11:59 PDT Race gauntlet/20261016-185924-race-micro on the VM (log logs/race-micro.log): base c_knob1 (= c_well9 with
  fight()'s two thresholds as constants) and the full grid AHEAD_MIN 0-3 x HOLD_THREAT 0-3 (15 variants + the base),
  rungs 8/16/32 units, keep 0.5: 256 + 144 + 160 = 560 games. Why: the three teams that beat us most stand and fire on
  0.33-0.38 of contact turns to our 0.17-0.20 and hold on 0.22-0.27 to our 0.35-0.40 (07:06 today); the parity hold
  (AHEAD_MIN 2, HOLD_THREAT 1) is the switch that keeps ours out. c_swarm4a/b (step in at 1 or 0 ahead) were rejected
  on 10-08 on g_iter2, a much older bot; the hold-threat axis was never varied.
- 12:15 PDT race-micro stopped after 2 games (dir renamed .stopped on the VM): Cornucopia games ran to r2000 in 387-535 s
  with the replica's 6 match JVMs and two screens on the VM's 8 cores (load 24), so 560 games would take ~15 h. Replaced
  by a one-factor-at-a-time design with a third knob. c_knob2 = c_knob1 + C.STAND_THREAT (-1 = c_well9): with the shot
  spent, a launcher stays on a tile at most STAND_THREAT enemy fighters reach instead of kiting; kiting spends the move
  (launcher move cooldown 20, RULES 2: one move every other turn), so the kited launcher cannot step back in and holds
  the next turn, the likely source of our 0.35-0.40 hold share. Race gauntlet/20261016-191511-race-micro2 (log
  logs/race-micro2.log): base c_knob2 (= c_well9: 2/1/-1) and 9 points: AHEAD_MIN 1, 0; HOLD_THREAT 2, 3; STAND_THREAT
  0, 1, 2; (1, 2, 1); (0, 3, 2); rungs 8/16/32 units, keep 0.5: 160 + 96 + 128 = 384 games. tools/race.py init
  --point NAME=v,NAME=v (one candidate; duplicates and the base's own point refused; RaceTest.test_points).
- 12:18 PDT Archetype fidelity, 20-21 trials with a screen and a panel (Spearman of each archetype's screen net with
  the panel's paired net): against the archetype's own member teams arch_swarm +0.03, arch_ampmid -0.04, arch_blob
  +0.05, arch_adecon +0.26, arch_horde -0.31; against the panel total arch_swarm +0.43, arch_adecon +0.43, arch_blob
  +0.37, arch_ampmid +0.18, arch_horde +0.04 (arch_jm: 2 trials). No archetype models its members' matchup; several
  track overall soundness. c_well9 beats them 20/20 (adecon), 18/20 (blob), 16/20 (swarm), 15/20 (ampmid), 14/20
  (horde), 10/20 (arch_jm): only arch_jm and the mirror sit near 50%, where a game carries the most information.
- 12:18 PDT c_tune1 screen (for information; its trial is running): basics 8/8, h2h vs c_well9 9/20 (borderline band:
  pass 11, borderline 9), roster stage running. With the Swiss's 3-3, 12/26 head to head: no better than c_well9 in
  the mirror; the panel decides.
- 13:00 PDT race-micro2 at 13/160 rung-1 games after 45 min: the long maps run first and every Cornucopia and Forest game
  so far reached r2000 in 520-700 s (VM load 27 on 8 cores: the replica's ~6 match JVMs, the race's 5 slots, the
  c_tune1 screen). Rung 1 should take ~4-5 h, the race ~10 h. Replica (12:50): matches 8194-8200 running; our three
  panels (c_pack1 8201-8210, c_gp1 8211-8220, c_tune1 8221-8230) queued next, in that order.
- 13:02 PDT Swiss census by bot (research/swiss/20261016-153444-swiss-n4): points follow damage taken per contact turn
  (top four 10.0-10.9, bottom three 12.3-13.8) and launchers lost (126-156 vs 171-173 a game); hit|contact and
  move|contact barely differ (0.67-0.71, 0.42-0.44). The bottom bots mend late (MEND_HP 41-45 vs 78-94) and form long
  (FORM_MAX_TURNS 21-28 vs 8-16): the correlations mostly flag settings that break the bot, and c_well9 (80, 15) sits
  with the leaders. Small moves the leaders share: FORM_MAX_TURNS 8-11, ANCHOR_PERIOD 18-19 (c_well9 15, 30), a
  follow-up --point race after the micro race.

## 2026-10-16 13:49 PDT: c_sim1, launchers judge a fight by health (focus-fire simulation)
- Cat vs vrangr1 (c_well9 panel match 7600 game 1, lost r428; per-turn launcher states of both sides, ReplayDump --sa):
  our two groups of four met theirs at r13-37 and lost 6 launchers to 2; hits per contact turn were close (0.69 vs
  0.76), but their fire was concentrated: census focus 0.18 vs 0.58, kill conversion 0.37 vs 1.00, first hit 0.13 vs
  0.88, exchange 0.30 vs 3.31. At r45 three of ours (180/200/120 HP) held off six of theirs at 20/20/40/180/20/80:
  the count rule (allies + 1 - enemies >= 2) said behind, a focus-fire simulation says won (we keep 20%); their
  damaged launchers then walked to our HQ. Panel-wide (census, 100 games): against the three teams that beat us most
  our focus is 0.42 to their 0.54, kill conversion 0.72 to 0.91, exchange 0.97 to 1.57; against the other seven we
  lead on both (0.55/0.91 to 0.34/0.61). Hah vs vrangr1 (same match, game 5) is a different loss: ahead r80-140 (8-10
  launchers to 4-8), then a fight at r130-150 beside their HQ, where their new launchers joined at once while four of
  ours sat at our HQ; 10 to 6 became 6 to 11 and the carriers went next (16 to 2 by r220).
- c_sim1 = c_knob2 + C.SIM_KEEP 60 + C.SIM_STAND 1 (Launcher.simKeep): fight()'s "ahead" is a simulation over the
  fighters in vision (self + up to 11 of our launchers vs up to 12 enemy launchers and destabilizers; shots to kill
  = HP/20 rounded up; each round both sides fire one shot per live unit at the other side's weakest): ahead when it
  wipes them and keeps >= 60% of our shots-to-kill. Full health: 2v1 keeps 75, 3v2 63, 4v3 55, 3v1 86, 6v4 66, equal
  numbers lose. Ahead with the shot spent, a launcher stays put instead of kiting. Count rule below 5,000 bytecodes
  left (SIM_MIN_LEFT). Offline flips at SIM_KEEP 60 (same-round positions and HPs): Cat 7600 g1 37 of 204 contact turns
  to engage (2v1 15, 3v2 8, damaged 2v2/1v1 14), 2 to hold; DefaultMap vs awesomelemonade (7603 g3) 75 of 979 to
  engage (2v1 33, 3v2 17, 4v3 13), 6 to hold. Sim1Test 20 cases; param.py SIM_KEEP (-1..90), SIM_STAND (optional).
- 13:41 PDT delivery games on the driver (Cat 1101, both sides): side B won both (c_well9 r470, c_sim1 r479, 75% of
  islands): no strength signal; 0 exceptions, 0 overruns, launcher bytecode max 9,176 (c_well9 9,174). VM disk at
  1.91 GB free refused the screen: 84 replays of finished runs deleted (build/codex-recovery from 10-12/13,
  guard1, guard2; owner, PROMPTS 113), 2.2 GB free. Screen queued next after c_tune1's (stage c at 100/120), ahead
  of c_adlo1's: job renamed 20261016-182322-scr-c_sim1-5365e65c3cb8 (the queue runs pending jobs in name order) and
  the screen state's job id updated to match.

## 2026-10-16 14:38 PDT: c_pack1 accepted as g_iter12 (panel 8201-8210); c_tune1 screen FAIL (information only)
- c_pack1 panel gauntlet/20261016-160153-panel-c_pack1: 67/100 (c_well9 63/100). Paired vs c_well9: 86 identical,
  gained 9, lost 5, net +4 (+1.07 SE, sign p 0.42); island-rounds -242 (t -1.73). By opponent: pranayagra 3-0,
  vrangr1 2-0, reeceyang 0-1, the rest even. By map: BatSignal +2, Hah +2-1, others +1/0; Cornucopia 0-2.
- Mechanism (census, our rows, 100 paired cells): Mn collected +336 a game (t +0.89; Maze +1,506, Forest +786, Cat
  +655, DefaultMap +556; Cornucopia -359, ReverseFunnel -244), carriers built -3.4 and died -4.7 (t -1.83), Ad -159
  (t -1.43), launchers built +5.1, kills +7.1. Packing pays in mana where the home well is crowded. Screen PASS
  (h2h 13/20). Accepted (trial-decide 169 --accept): submission 175 is the validated build; c_gp1 and c_tune1 must
  now beat c_pack1's panel.
- c_tune1 screen (Swiss winner c_sw07, panel trial already started --skip-screen on the owner's direction): FAIL,
  h2h 9/20 borderline, roster information Net +5 (arch_horde +2), 148 games 0 overruns or exceptions. Its panel
  decides.
- Hah vs vrangr1 (c_well9 panel 7600 g5) follow-up: the four launchers at home r125-160 were three at (10-14, 8-11)
  seeing two allies each and one at the other HQ (4,18): the GROUP_MIN 4 forming hold kept them home ~35 rounds while
  the main group fought beside the enemy HQ. c_tune1 already has GROUP_MIN 3 and FORM_MAX_TURNS 11, so its panel
  tests a shorter hold; c_join1 (skip the hold for a fight sighting within r2 64) would not have fired here (the
  fight was ~30 tiles away) and is not built.
- Ranked map record (527 ranked matches with extracts, all builds): panel maps 0.58 (157 games) vs other maps 0.52
  (1,424); since 10-14 other maps 0.46 (184) vs panel maps 0.65 (17). The gap is within ~1.5 SE in each era: no
  overfitting claim, but every local tool (screen, race, Swiss) plays only the 10 panel maps; worth watching.
- Ranked 8190 vs pranayagra (1-2): maptestsmall lost to a r5 launcher rush, then 45 spawn kills over 1,800 rounds
  (Mn 5 collected all game); Pakbot lost (0 carriers alive at r100, launchers 1 vs 18 at r250).

## 2026-10-16 15:04 PDT: c_gp1 accepted as g_iter13 (panel 8211-8220, 71/100); c_sim1 screen FAIL 5/20
- c_gp1 (c_guard1 + c_pack1's packing; c_guard1 = c_mid1's contested-well site + home-well defence) panel
  gauntlet/20261016-170213-panel-c_gp1: 71/100, the best panel so far (c_pack1 67, c_well9 63). Paired vs c_pack1:
  82 identical, gained 11, lost 7, net +4 (+0.94 SE); island-rounds +94 (t +0.50). Flips by map: Cornucopia 4-0,
  Forest 3-0 (our two weakest maps: ranked panel-map record 0.29 on Forest/Cornucopia), ReverseFunnel 1-0, Hah 2-2,
  IslandHopping 1-1, Maze, Cat, DefaultMap, MassiveL 0-1. Census vs c_pack1: carriers built -11.0 (t -3.60) and
  died -10.1 (t -2.96), Mn +172 (t +0.46), Ad -530 (t -2.00), kills -21.9 (t -1.90). Vs c_well9: net +8 (+1.89 SE).
  Accepted (trial-decide 171 --accept): submission 176 is the validated build. c_tune1 (c_well9-based) must now
  beat c_gp1's panel.
- c_sim1 screen FAIL: h2h 5/20 vs c_well9 (basics 8/8, 0 overruns or exceptions). Judging "ahead" by the focus-fire
  simulation (engage 2v1, 3v2 at health) and standing after firing lose clearly to the count rule (AHEAD_MIN 2) and
  kiting. Rejected without a panel; no follow-up on simulation-based engagement.

## 2026-10-16 15:42 PDT: c_tune1 rejected (panel 8221-8230, 63/100); PROMPTS 119 (progress/ on every accept)
- c_tune1 (Swiss winner c_sw07 of 20261016-153444-swiss-n4; trial --skip-screen on the owner's direction, PROMPTS
  114) panel gauntlet/20261016-184324-panel-c_tune1: 63/100. Paired vs c_gp1 (validated): 74 identical, gained 9,
  lost 17, net -8 (-1.57 SE), island-rounds -579 (t -2.71); georgezhang02 0-4, vrangr1 1-4. Vs c_well9: net 0,
  island-rounds -727 (t -3.53). Its screen was FAIL (h2h 9/20). Rejected (trial-decide 173 --reject). LEARNINGS:
  self-play tournaments select against our own style, not the field.
- Owner, PROMPTS 119: "Please update the progress directory whenever accepting a new candidate". The two accepts
  today (c_pack1 14:38, c_gp1 15:04) left progress/ behind; refresh started 15:27 PDT. ladder_policy now prints the
  step after an accept (ACCEPT_NEXT); TRAINING_ALGORITHM step 7 and docs/LADDER_STRATEGY.md name
  tools/progress-refresh.sh. tools/web-worker test_timeout_kills_parent_and_child_process_group flaked under driver
  load 7 (the job's 1 s timeout beat the child's pid write); timeout 3 s, bound 10 s.
- 16:39 PDT carrier deaths, ranked 8190-8237 (327 games, sub 175/176, deaths.csv r<=300): lost games 14.0 of ours per
  game vs 6.6 of theirs; won games 3.8 vs 16.8. In losses ours die in F 614 (317 empty), G 450 (318 empty), C 178,
  V 174, W 100; all to launchers; prog quartiles 0.10/0.20/0.31 (home wells; c_well6's hot memory covers front wells
  only). Cee 8236 g0: carriers built 18/19 by r250 but alive 11/17. Workflow c_flee1 (on c_gp1: replay diagnosis,
  3 designs, judge, implement, review) and c_expl1 (frontier exploration, on c_keep2) running. keep2-h2h 40/83 at
  16:30 (both-sides maps: Fractured 2-0; Contraction, Checkmate2 0-2). progress/ pushed 16:05 (e86cc9f; 23 reports).
- 17:26 PDT c_adlo1 screen (vs c_well9, its base): PASS, h2h 11/20, roster info net +0, basics 148 games clean. Ported
  to the incumbent: c_adlo2 = tools/param.py make c_gp1 (AD_EARLY_EVERY 12, AD_LATE_EVERY 7, CAP_MAX 40,
  CAP_PER_MN_WELL 7, ANCHOR_START 330); its screen vs c_gp1 queued (20261017-002503-scr-c_adlo2-dc0032eb1894;
  --min-disk-gb 1.5: the VM has 1.9 GB free, replays are not the bulk). keep2-h2h 73/148 (both-sides maps: won
  Fractured, RockWall; lost Checkmate2, Contraction, PipesAndParabolas; Orbit 1-1).
- 18:13 PDT keep2-h2h DONE (c_keep2 vs c_gp1, 103 maps both sides, census): 103/206, net 0; the fix moved 8 maps (won
  both sides Fractured, RockWall, Spin, TimesUp; lost Checkmate2, Contraction, PipesAndParabolas, Sun); Orbit,
  SoundWave, Turtle 1-1. Neutral in self-play: c_keep2 parked, not screened (PROMPTS 102). Its replays pruned (VM
  2.4 GB free).
- 18:27 PDT disk purge (owner, PROMPTS 120). Driver 5.1 -> 8.9 GB free: run replays except the c_gp1/c_pack1 panels
  (32 dirs), match replays before 7600 (492 files, extracts and reports kept; the replica keeps every replay of our
  matches), build/codex-recovery bulk (Oct 12-13 progress snapshots and logs; the 20261012T191037Z recovery bundle
  kept), stale replay-dump caches and class trees. battlecode-dev 1.9 -> 3.7 GB free: Oct 8 fidelity extracts (10,
  results/summaries kept), codex-recovery, old class trees, dev/diagnostic replays, journal to 100 MB. Kept: the
  replica's replay store (/srv, 4.3 GB of our matches), running jobs, other projects' dirs; battlecode-dev2 untouched.
- 18:45 PDT c_flee1 workflow DONE (9 agents; research/diagnosis/2026-10-16-carrier-deaths.md). Replay diagnosis, 12 lost
  games, 230 carrier deaths by r300 (each is 8 launcher hits): RETURN (walks back right after losing sight of a
  raider; 64% the turn after the sighting, 85% within r2 34 of our HQ) 53% of deaths; INTO (flee step toward home
  through the raiders) 24%; STUCK 11%; AWAY 3%; FRESH 3%. Once hit, ours die 0.86 vs theirs 0.57; ours hover at r2
  18-29 (median r2 to the shooter 5 rounds after the first hit 26 vs 40). c_flee1 = c_gp1 + 4-round threat memory
  (ghost flee), r2 36 stand-off in Nav.can, scored two-step flee over all visible/remembered fighters, deposit first
  next to an HQ, throw cargo when hit while >= 14 kg, drop a home well after a second flight within 30 rounds;
  sub-switches FLEE1_MOVE/MEMORY/BANK/LIGHTEN/DROP; Flee1Test 69 cases. Driver River 1101 c_gp1 vs c_flee1 (B):
  B won r535 conquest; carriers dead by r300 7 vs 13; 0 exceptions, 0 overruns. Screen queued
  (20261017-014229-scr-c_flee1-b9c3e3993ad4).
- 18:45 PDT c_expl1 workflow DONE (9 agents) = c_keep2 + frontier explore: 5-tile grid of uncovered points (MapMem bits,
  cloud points stood on, mirror-covered once symmetry is decided), per-HQ fan slot claim in Comms 55 (only while
  islands < 35), resumable pass under a 6,000 bytecode floor, neighbour hand-off; old explore as fallback. Offline
  sim: mean turns to a known well 15.2 -> ~10 (SoundWave 28.7 -> 11.8, Turtle 42.1 -> 21.6; Cat 1.2 -> 4.5).
  Expl1Test 639,256 cases (2 s). Screen queued (20261017-014454-scr-c_expl1-9ed33910e495).
- 19:22 PDT race-micro2 DONE (research/race/20261016-191511-race-micro2/; c_knob2 = c_well9's micro knobs as the base, 9 points, rungs
  8/16/32 units vs c_well9, arch_jm, arch_swarm, arch_ampmid): final c_rc01 47/64, c_rc04 45, base 44, c_rc05 42;
  winner c_rc01 +3 over 64 paired games (noise). Rung-1 share by level: AHEAD_MIN 0 .469 / 1 .625 / 2 .635;
  HOLD_THREAT 1 .635 / 2 .594 / 3 .500; STAND_THREAT -1 .675 / 0 .625 / 1 .656 / 2 .344: the base values are
  best on each knob. Micro knobs are at a local optimum; nothing exported.
- 20:44 PDT c_adlo2 screen (vs c_gp1): PASS, h2h 13/20, roster info net +3, basics 148 games clean. Panel trial started
  (tools/ladder_policy.py trial-start c_adlo2; logs/trial-c_adlo2.log). flee1-h2h (c_flee1 vs c_gp1, 103 maps both
  sides) 34/60 at 20:12 (both-sides maps won 7, lost 3: AllElements, Cube, Forest). Driver Forest 1101 c_gp1 vs
  c_flee1 (B): A won r2000 on islands; B's carriers dead by r400 7 vs 11, Mn@100 523 vs 434, but Mn@300 1654 vs
  1940 and L@600 32 vs 67: fewer deaths, less mid-game mining (stand-off/drop timidity is the suspect).
- 21:14 PDT c_flee1 screen (vs c_gp1, panel maps): FAIL, h2h 8/20, basics (d) over 6 (all on Cornucopia, side B;
  near-limit turns 2,114/2,381 on Cornucopia; 29-298 elsewhere). flee1-h2h at 146/206: 85/146, won both sides 21
  maps, lost both 9 (AllElements, Cube, Forest, Frog, IslandHopping, IslandHoppingTwo, Minefield, MoonPhases,
  RaceToTheTop): strong in self-play overall, weak on the large panel maps. Next: the overrun source (Cornucopia
  replay), then ablations of the FLEE1 sub-switches on the panel maps.
- 21:52 PDT flee1-h2h DONE (c_flee1 vs c_gp1, all 103 maps both sides): 114/206, won both sides 26 maps, lost both 15
  (AllElements, Cube, Forest, Frog, IslandHopping, IslandHoppingTwo, Minefield, MoonPhases, RaceToTheTop, Spiderweb,
  Spin, Swooshy, TimesUp, VeryReasonable, Zig): net +11 maps, replays pruned. Cornucopia overruns: all 6 carriers
  were in FH2 (flight) the turn before; the fm<0 fallback ran c_gp1's Nav.moveTo with ~2,000 bytecodes left.
  c_flee4 = c_flee1 + FLEE1_MIN_LEFT 3500, GUARD 4000, FLEE4_FALLBACK_LEFT 5000 (else one Nav.moveAway step);
  Flee4Test 69 cases. Ablations from c_flee4, one switch off each: c_flee5 DROP, c_flee6 MEMORY, c_flee7 MOVE,
  c_flee8 LIGHTEN; VM job abl-flee4 (200 games vs c_gp1, panel maps, both sides, seeds map and 1101).

## 2026-10-16 22:58 PDT — Rating history fixed (owner, PROMPTS 121): stale chart, frozen replica ratings
- Owner: "rating-history.md doesn't have c_pack1 or c_gp1". Two causes. (1) tools/rating_history.py's label layout
  grew with the trial candidates (40+ labels, ~5M pair-cost calls): 34 min per run, so progress-refresh.sh's
  `timeout 900` killed it silently at 15:4x and the .md/.png stayed at 10-15 20:43 PDT. The layout now prices every
  candidate of a label at once with cached per-pair arrays (same arithmetic): byte-identical PNG and .md on the same
  bundle, 124 s offline, 41 s live. progress-refresh.sh now names a failed or timed-out step ("!! <step> FAILED")
  and exits 1. (2) Replica match 7880 (sprintBot vs pranayagra.finalbotfinal, ranked, created 10-16 01:00 PDT) sat
  in RUN for 21 h; siarnaq rates in creation order, so 340 finished participations, all 24 of c_gp1's ranked
  matches among them, had no rating. Staff Cancel + Recalculate (tools/galaxy/cancel-match.sh 7880 --cancel): 0
  unrated, vibe23 1653 -> 1710. The watcher's STUCK_MATCH scan read only the newest 400 matches via the API and
  7880 had left that window; it now adds every RUN match from galaxy's database (run_ids_cmd). c_pack1 (#175)
  never played a ranked match (validated 14:38-15:04 PDT, replaced by c_gp1 #176): the .md now says so.
- c_expl1 screen PASS (marginal): h2h 11/20, roster info-only net -7 (arch_jm -3, horde -2, swarm -2), 148 games
  clean. All-maps h2h queued before any trial (VM expl1-h2h, 206 games). c_flee4 on Cornucopia (map seed, side B):
  2 overruns (down from 6), both on the turn after FH2; won r2000 on islands.
- 23:42 PDT c_adlo2 rejected (panel gauntlet/20261017-034428-panel-c_adlo2 vs c_gp1's: identical 91, gained 3, lost
  6, net -3, -1.0 SE; island margin -217 rounds, t -2.0): c_adlo1's parameter settings do not carry over to c_gp1.
  c_gp1 re-validated as submission 178. c_flee9 = c_flee4 + FLEE9_HOLD (a flight check that leaves the carrier in
  place with < 9,000 bytecodes left collects if at its well and ends the turn): debug trace of c_flee4's overrun on
  the VM, a ghost flight scored and stayed at 5,413 used and gather took 7,109 more. Flee9Test 69 cases. VM:
  flee9-panel (56 games vs c_gp1: panel both sides seeds map/1101, Cornucopia/MassiveL seeds 2-5) and expl1-h2h run
  beside abl-flee4.
- 00:35 PDT abl-flee4 DONE (vs c_gp1, panel maps both sides, seeds map + 1101, 40 games each; the variant's score):
  c_flee4 base 21/40 (map 8, 1101 13), c_flee5 DROP off 18 (paired vs base +1 -4), c_flee6 MEMORY off 20 (+5 -6),
  c_flee7 MOVE off 17 (+3 -7), c_flee8 LIGHTEN off 22 (+4 -3; map seeds 11/20). All within noise (SD ~3 on 40).
  Overruns only with MEMORY on and only on Cornucopia (base 3, DROP off 3; 0 for MEMORY/MOVE/LIGHTEN off), as the
  debug trace said (ghost flight, then gather). MEMORY off mines more: mean Mn 6,232 vs 5,751 (+8%). The flee package
  is about even with c_gp1 on the panel maps (c_flee1 was +11 maps over all 103). Replays pruned.
- 01:22 PDT Basics gap found mining c_gp1's ranked losses (telemetry_query econ --ranked --by map since 10-14): our
  Mn collected by r100 is 0-35% of the opponent's on 8 maps (SoundWave 0/380, Spin 16/165, Turtle 11/111, Orbit
  25/148, Quiet 64/270, Rewind 136/534, Scatter 202/588, maptestsmall 93/265; 0.9-1.3x elsewhere). Turtle 8248 g2:
  our Mn carriers spent 586 turns in X (explore) and none mining; one HQ of each team sits in a walled pocket ~33
  walking tiles from its wells. Workflow econ-weak-maps (one agent per map + synthesis) and VM econ8-self (c_gp1
  self-play on the 8 maps, both sides, map seed, 16 games) running.
- 02:28 PDT econ-weak-maps workflow DONE (8 map agents + synthesis): SoundWave/Turtle/Scatter = blind opening search
  (no Mn well in HQ vision; centre-first leg into walls or the enemy half), Orbit/Spin = dead-end well choice (every
  Mn well hot or the avoided mid site; the any-type fallback kept an Ad well for life; carriers explored holding
  cargo), Quiet/maptestsmall/Rewind = combat symptoms. econ8-self (c_gp1 self-play, deterministic, A = B rows):
  side A collapses on SoundWave (Mn@100 0 vs 140, @250 18 vs 920), Orbit (@250 65 vs 317, Ad 1336), Quiet, Spin.
  expl1-h2h DONE: c_expl1 110/206 vs c_gp1 (+7, ~1 SE), maps won both 15 / lost both 8; SoundWave and Turtle won
  both sides, Scatter lost both. c_mn1 = c_expl1 + MN_TRIP (a fallback well lasts one trip once a role well is
  known) + MN_AVOID_JUMP (site-only role well: fallback at once) + MN_BANK (no well, cargo >= 10: bank, not explore);
  Mn1Test 13 checks; unit-tests PASS. c_flee9 flee9-panel DONE: 30/56, 0 overruns (Cornucopia/MassiveL seeds 2-5
  included), panel 20/40 = noise; flee9-h2h (all maps both sides) queued. VM econ8-mn1 / econ8-expl1 (8 maps both
  sides vs c_gp1, KEEP_ALL) running; c_expl1 trial-start submitted.
- 03:35 PDT econ8 h2h vs c_gp1 (8 weak maps both sides, map seed): c_mn1 7/16, c_expl1 8/16. c_mn1's Mn: Spin as A
  @250 190 vs c_expl1 67 (won), Orbit as B @250 363 vs 280 (Ad 624 vs 1172); SoundWave identical Mn yet c_mn1 lost both
  on the r2000 tiebreak that c_expl1 won (late-game chaos: one seed is too thin). Side bias: ranked since 10-14 side A
  75-84 (0.47), B 63-51 (0.55). Offline (all 103 maps): siegeTarget's first target is a fake reflection image for both
  sides on 87 maps, side-dependent on only 3. c_sym1 = c_gp1 + SYM_CENTROID (undecided symmetry, no enemy HQ seen:
  launchers march to the centroid of the predicted enemy HQs until r2 20 of it; Quiet diagnosis: both corners marched
  to (3,16) first, the split group met the opponent's four 1-0 v 4). Sym1Test 7 checks; unit-tests PASS. VM queued:
  mn1-h2h, sym1-h2h (all maps both sides vs c_gp1), self-all (c_gp1 mirror, every map, side A: side-bias audit).
- 04:14 PDT trial-start c_expl1 (submission 179) died at 03:40 on a DNS failure (sslip.io lookup, Errno -5) after 10
  of the panel's 14 requests; a first resume died the same way. tools/contest.py http() now resends on a failed lookup
  or refused connection (any method) and on any network error for a GET, 6 times 5-160 s apart
  (test_network_failures_resend_only_when_safe); unit-tests PASS. Panel resumed (RESUME=gauntlet/20261017-091445-
  panel-c_expl1). Interim VM: flee9-h2h 85/147 (57.8%), mn1-h2h 13/24, sym1-h2h 10/25, self-all 30/103.
- 05:42 PDT c_expl1 trial REJECTED: panel 68/100 vs c_gp1's 71 (paired: 97 identical, lost 3 vs awesomelemonade,
  Sprint1, vrangr1; net -3, sign p 0.25); c_gp1 resubmitted as 180. Local expl1-h2h +7 did not transfer (the panel's
  maps and opponents barely exercise blind search). flee9-h2h DONE 116/206 vs c_gp1: won both sides 29 maps, lost both
  16 (identical list to c_flee1's), split 58. Screen c_flee9 queued (20261017-124217).
- 05:53 PDT Panel losses with an army lead: 13 of c_expl1's 32 panel losses (and 27 in panel matches 8211-8230) had
  launchers at r250 >= theirs. Cornucopia (3 HQs a side) vs awesomelemonade 8616 g2: launchers 27/12 at r250, we
  killed 1 enemy carrier per 100 rounds in r200-500 while theirs grew 21 -> 40 and their launchers 12 -> 56 by r550
  (pranayagra 8617 g2: 25/11, 0 carriers killed r200-400, their launchers 11 -> 33 in r250-350). Launcher turns in the
  mid phase: S/N (stand, nothing) at the enemy HQ 48%. Map at r450 (8613 g2, vrangr1): our ring held (10,18) while their
  carriers mined beside their HQs (48,18) and (29,51). The carrier raid (raidWell) covers only predicted wells within
  r2 100 of the siege target. c_hunt1 = c_gp1 + C.HUNT: once those are all cleared the raid goes on to the other
  enemy HQs' predicted wells (nearest the siege target first) before the ring; the raided-well table becomes an
  open-addressing hash (64 slots, O(1) lookups, no RNG eviction). Hunt1Test 16 checks. VM hunt1-h2h queued.
- 06:19 PDT c_flee9 screen FAIL (progress/screens/c_flee9-8ef1bc98cf8c.json): basics PASS (0 overruns, 0 exceptions),
  h2h 8/20 vs c_gp1 on the panel maps (flee9-h2h on the same maps 9/20; its +13 maps are off the panel). Not trialled.
- 07:08 PDT VM all-maps runs vs c_gp1 (103 maps x both sides, seed map): hunt1-h2h 107/206 (won both sides 12 maps,
  lost both 8; panel maps 12/20, Cornucopia and Forest won both), mn1-h2h 107/206 (15/11; panel 9/20, Cornucopia lost
  both), sym1-h2h 106/206 (21/18; panel 10/20). self-all (c_gp1 mirror, every map): side A 50/103, so self-play has no
  systematic side bias (ranked side A 0.47 vs B 0.55 since 10-14 is not a bot asymmetry). Near-identical builds split
  most maps by side (hunt1: 83 of 103 split), so won-both minus lost-both is the map signal: flee9 +13, hunt1 +4,
  mn1 +4, sym1 +3.
- 08:00 PDT c_hunt1 screen PASS (progress/screens/c_hunt1-03d3e2b496cb.json): basics clean (148 games, 0 overruns),
  h2h 12/20 vs c_gp1, roster info-only net -2 (3 of 120 roster games changed: the wider raid rarely fires against the
  archetypes). trial-start refused at 07:58 (the next autoscrim, 09:00 PDT, falls inside the 2.5 h panel): start after it.
  The driver cannot finish a Cornucopia game (two runs hit run-dev's 30 min timeout). c_rot1 = tools/param.py c_gp1
  with SIEGE_ROTATE_FROM 300, SIEGE_ROTATE 100 (Cornucopia 8613 g2 r765: ~30 launchers held the ring at one enemy HQ
  while 12 enemy carriers mined between our HQs; c_hunt1 extends only once the target's raid wells are cleared, which
  a ring in constant contact never does). VM rot1-h2h (all maps both sides vs c_gp1) queued.
- 08:38 PDT rot1-h2h DONE: c_rot1 115/206 vs c_gp1 (won both sides 16 maps: BattleSuns, Cave, Cee, Cornucopia,
  Eyelands, FishCake, Fractured, Grievance, IslandHoppingTwo, KingdomRush, LookingGlass, MoonPhases, Potions,
  ReverseFunnel, Spots, Tightrope; lost both 4: Buggy, Lines, ThirtyFive, USA; net +12 maps, the best map signal after
  flee9's +13; panel maps 12/20 with Cornucopia and ReverseFunnel won both). Screen c_rot1 queued
  (20261017-153742). c_hr1 = param c_hunt1 with c_rot1's rotation (stack of the two siege fixes): VM hr1-h2h queued.
- 09:05 PDT trial-start c_hunt1 (submission 181) after the 09:00 autoscrim; panel requests 4406 on.
- 09:51 PDT c_rot2 (param c_gp1: SIEGE_ROTATE_FROM 200, SIEGE_ROTATE 100) and c_rot3 (FROM 300, ROTATE 50): the
  rotation timing neighbours of c_rot1; VM rot2-h2h, rot3-h2h queued 09:15. VM load average 28 on 8 cores with the
  c_hunt1 panel, the c_rot1 screen and hr1-h2h: stopping rot2/rot3 was refused by the permission classifier, so they
  run on; no new VM work until the load drops.
- 11:25 PDT STUCK_MATCH 8689 (ranked autoscrim 09:00 PDT, battlecode-archive.sprintBot vs pranayagra.finalbotfinaltwo,
  RUN > 1 h): cancelled + re-rated (tools/galaxy/cancel-match.sh 8689 --cancel, now CAN). The same pairing hung as
  7880 on 10-16 (sprintBot vs pranayagra.finalbotfinal): a repeat offender; not our match.
- 11:35 PDT c_rot1 screen PASS (a 8/8, b h2h 12/20 vs c_gp1, c roster info-only net -2, d 128 games clean). Next
  panel candidate after c_hunt1 (trial-park/trial-decide once c_hunt1's panel matches all exist).
- 11:36 PDT c_hunt1 trial parked (panel matches 8802-8811; c_gp1 active again as 182); c_rot1 trial-start (submission
  183, requests 4416 on, log logs/trial-c_rot1.log). Decide each with paired.py vs gauntlet/20261016-170213-panel-c_gp1,
  then trial-decide c_hunt1 / trial-end c_rot1.
- 12:28 PDT h2h vs c_gp1, all maps both sides (203/206 = map signal): hr1-h2h (c_hunt1 + rotation) 117/206, won both 20,
  lost both 6 (+14 maps), panel maps 13/20: best local result yet (c_rot1 115, 16/4; c_hunt1 107, 12/8: the two
  stack). rot3-h2h (ROTATE 50) 110/206, 16/9, panel 12/20: worse than c_rot1's ROTATE 100. Lines and USA lost both
  sides in all three. c_hr1 screen queued (20261017-192824-scr-c_hr1-83b5e566de21). VM replays of the three pruned.
- 12:54 PDT Lines (lost both sides by c_rot1/c_hr1/c_rot3 on the map seed): c_hr1 vs c_gp1 on seed 1 wins both sides
  (A r1295, B r850, conquest). The h2h's single map seed per side makes one map's both-sides result seed luck, not a
  structural loss. Second sample queued: hr1-h2h-r (c_hr1 vs c_gp1, all maps both sides, random seeds).
- 13:25 PDT rot2-h2h (ROTATE_FROM 200) 115/206, won both 20 / lost both 8, panel 12/20: no better than c_rot1. USA lost
  both sides by every rotation build, and on seed 1 too (c_hr1 A lost r863, B lost r740). USA has one HQ per team, so
  rotation should be a no-op there: but MapMem.enemyHQs() returns one image per live symmetry until the enemy HQ is
  seen, and from r300 siegeTarget cycled the army between those guesses (c_hr1's launchers turned back north at
  r320-380; 11 vs 25 launchers at r500). **c_hr2** = c_hr1 + ROT_KNOWN (rotate only when MapMem.decided() or every
  enemy HQ is seen; pure rotRank, Hr2Test). hr2-h2h queued; unit tests running.
- 14:00 PDT c_hunt1 trial (submission 181) **REJECTED**: panel vs c_gp1's (paired.py) 98 games identical, gained 1
  (pranayagra.finalbotfinal), lost 1 (georgezhang02.CB_tuning2), net 0; island-rounds margin +109 (t 0.82). The raid
  extension rarely fires against the field. c_gp1 stays validated (182).
- 14:23 PDT c_hr1 screen PASS (a 8/8, b h2h 13/20 vs c_gp1, c info-only net -2, d 128 games clean; arch_horde excluded:
  compile-failed on the VM, as arch_adecon in c_rot1's screen: intermittent, under load). c_hr2 unit tests PASS.
  c_hr1 waits for c_rot1's panel (c_hr2 may supersede it: hr2-h2h running).
- 14:24 PDT c_rot1 trial parked (panel matches 8812-8821; c_gp1 active as 184); c_hr1 trial-start (submission 185,
  requests 4427 on, log logs/trial-c_hr1.log).
- 14:26 PDT c_rot1 panel done (parked; paired.py vs c_gp1's): 99 identical, gained 1 (pranayagra.finalbotfinal), lost 0,
  net +1 (1.0 SE), island-rounds +34 (t 0.33). Positive but within noise; local h2h 115/206 (+12 maps). Decision held
  until c_hr1's panel (its superset: rotation + hunt) is done: accept the better one if positive (trial-decide
  --accept is refused while c_hr1's trial is open anyway).
- 15:17 PDT c_hr1 panel (submission 185) vs c_gp1's: 97 identical, gained 2 (awesomelemonade, pranayagra), lost 1
  (georgezhang02), net +1 (0.58 SE), island-rounds +50 (t 0.41); vs c_rot1's panel net 0. Local: hr1-h2h 117/206
  (map seeds) and hr1-h2h-r 100/185 so far (random seeds): two samples ~55% (z ~2). **c_hr1 ACCEPTED** (trial-end;
  validated 185); parked c_rot1 rejected (subsumed by c_hr1). progress-refresh running.
- 15:17 PDT hr2-h2h (c_hr2 = c_hr1 + ROT_KNOWN) 108/206: vs hr1-h2h game by game 127 identical, gained 11 (USA B among
  them), lost 20: net -9. Rotating between symmetry guesses pays on most maps (the cycle visits the candidates,
  eliminating wrong ones and finding the real HQs), though it costs USA. c_hr2 dropped.
- 16:00 PDT hr1-h2h-r DONE: c_hr1 vs c_gp1, random seeds, 115/206 (55.8%); with hr1-h2h 232/412 (56.3%). c_hr3/c_hr4
  unit tests PASS; hr3-h2h, hr4-h2h vs c_hr1 running. VM replays of analyzed runs pruned (2.4 GB free). c_hr1's panel:
  71/100, losses spread over all 10 maps (jmerle 6, awesomelemonade 6, vrangr1 5, pranayagra 5, NotLLeon 3,
  britacatalin 2, georgezhang 1). Ranked reports (last 150): wins Mn@100 ratio median 1.44, losses 0.87; 160 of 392
  losses at par or ahead in launchers at r250. Workflow panel-loss-diagnosis running (4 groups + verify/synthesis).
- 16:51 PDT vs c_hr1, all maps both sides (map seeds): hr4-h2h (SIEGE_ROTATE_FROM 250) 112/206, won both 14 / lost both 5
  (+9 maps), panel maps 11/20; hr3-h2h (SIEGE_ROTATE 150) 97/206, 4/10 (-6): slower rotation is worse, an earlier
  start better. c_hr4: random-seed h2h (hr4-h2h-r) and screen (20261017-235104-scr-c_hr4-03ad65820c33) queued.
- 16:58 PDT panel-loss-diagnosis DONE (research/diagnosis/2026-10-17-panel-losses-c_hr1.md; c_hr1 panel 72-28 by
  results.csv). The losses are mostly decided by carriers dying at HOME wells before r300 (12.6 a game in losses vs
  3.3 in wins; builds equal), inside even launcher fights; the enemy army doubles ours by ~r280 in 25/28 losses
  (1/72 wins). Hot-well marks (c_well6) cover front wells only. Last step: islands; our launchers spend ~0 turns on
  enemy islands in losses (2.65 per enemy-held round in wins) even at one island short of conquest. Rejected as
  causes: piecemeal arrival (an effect), far-well raid, blind fire. Plans: c_isle1 (conquest-threat: even-id
  launchers take the nearest enemy island; sticky 'theirs' slot; ablation c_isle2) and c_drop1 (a second flight from
  the same well drops it for 40 rounds, home wells included, no hold). Workflow build-c_isle1 implementing both.
- 17:20 PDT build-c_isle1 workflow DONE (implement + adversarial review): c_isle1 (Isle1Test 1920 checks; review fixed
  the stale-target drop: a launcher marches on the other parity from its island scan, so "seen this round" never
  fired for half of them), c_isle2 (ISLE_STICKY off), c_drop1 (Drop1Test 28317 cases; review fixed 4 defects: a later
  flight changed the handed-back well, a role change stranded the carrier, the c_mid1 site could be dropped, the
  drop count was not in telemetry). isle1-h2h and drop1-h2h vs c_hr1 queued (VM load 34); unit tests running.
- 18:15 PDT STUCK_MATCH 8860 (ranked autoscrim 17:00 PDT, ethanlabelle.v19 vs CyrilSharma.finalBot, RUN > 1 h; not
  ours): cancelled + re-rated (tools/galaxy/cancel-match.sh 8860 --cancel).
- 20:48 PDT vs c_hr1, all maps both sides: hr4-h2h-r (random seeds) 94/206: with hr4-h2h 206/412, exactly even: c_hr4
  dropped. drop1-h2h 108/206, won both 12 / lost both 7 (+5 maps), panel maps 12/20: mildly positive, screen queued.
  isle1-h2h 102/206, 8/9, panel 10/20: neutral locally, as expected (its trigger, an enemy one island short of
  conquest, is a field-loss pattern that self-play rarely reaches); c_isle2 not run.
- 21:01 PDT c_hr4 screen PASS (h2h 11/20, basics clean) but 206/412 over two all-maps samples vs c_hr1: not trialled.
- 21:48 PDT c_isle1 trial-start --skip-screen (submission 186, requests 4467 on, log logs/trial-c_isle1.log): its
  trigger is field-only (an enemy 1-2 islands short of conquest: 0/72 c_hr1 panel wins, 7 losses), local h2h neutral;
  the ladder was idle until the 01:00 PDT autoscrim. Basics (overruns) come from the panel census. Rating with c_hr1
  1681 over 35 rated matches (c_gp1 1690).
- 21:55 PDT c_hr1 panel engagements starting r<=300 (exch = enemy value lost / ours): in LOSSES ahead-mid won 0.70,
  exch 0.98; par-mid 0.35, 0.81; par-home 0.44, 0.75; behind-home n 81, 0.52. In WINS ahead-mid 0.90, 2.64; par-mid
  0.61, 1.99; par-home 0.65, 1.25. Against the strongest bots our fights trade about even even when ahead: a combat
  gap that self-play micro tuning cannot see. Workflow micro-gap-diagnosis running (3 CSV lenses, 1 replay pass,
  verify/synthesis).
- 22:46 PDT c_isle1 panel (submission 186) vs c_hr1's: 97 identical, gained 2 (georgezhang02 and britacatalin on
  Cornucopia: r2000 tiebreak losses became conquest wins r1358/r1909), lost 1 (awesomelemonade Cornucopia: a r2000 win
  became a r1095 loss), net +1 (0.58 SE); island-rounds +106 (t 1.01); 0 overruns, 0 exceptions. Local neutral
  (102/206). Every measure non-negative and the flips are the island race the change targets: **c_isle1 ACCEPTED**
  (validated 186). drop1-h2h-r (random seeds) 112/206: c_drop1 220/412 vs c_hr1 over two samples (53.4%).
- 23:14 PDT c_drop1 screen PASS vs c_hr1 (h2h 12/20, basics clean over 148 games). c_di1 = c_isle1 + c_drop1's Carrier/DROP (tests copied as Di1Isle1Test, Di1Drop1Test: both pass); di1-h2h vs c_isle1 running.
- 00:08 PDT c_di1 unit-tests PASS (committed 8b7f9bf). di1-h2h (map seeds) vs c_isle1 108/206 (asA 51, asB 57), map signal +5 (10 both-sides wins, 5 both-sides losses), panel maps 12/20. Screen c_di1 and di1-h2h-r (random seeds) queued.
- 00:16 PDT micro-gap-diagnosis workflow done: research/diagnosis/2026-10-18-launcher-micro-vs-strong.md. Per-shot micro is at parity with the strong bots (first hit 0.35/0.36, damage per kill 255/245); losses come from more ahead/par fights turning (27% vs 9% in wins, 46% of our early launcher deaths) and from army size. Ranked micro levers are small (+0-1 game/100): GHOST (2-round fighter memory in 'ahead'), UHIT (leave a cloud when hit unseen; MassiveL 68 vs 0). Economy check (strong opponents, 8823-8832): builds equal (carriers 21.4/22.7 by r200 in losses) but alive carriers diverge from r100 (r200 12.6 vs 19.8 in losses, 19.0 vs 13.1 in wins), mirror-symmetric: whoever wins the early well fights snowballs. c_gh1 (c_di1+GHOST) and c_uh1 (c_di1+UHIT) being built by the ghost-uhit-build workflow.
- 01:24 PDT di1-h2h-r (random seeds) 102/206 vs c_isle1 (signal -1, panel maps 12/20): c_di1 210/412 over two samples (51.0%), panel maps 24/40. Screen running. c_gh1 (GHOST) and c_uh1 (UHIT) built and reviewed (Gh1Test, Uh1Test pass); gh1-h2h vs c_di1 started.
- 01:36 PDT unit-tests PASS with c_gh1 and c_uh1 (Gh1Test 8942476 checks, Uh1Test 23404576 checks).
- 01:41 PDT Idle-Ad finding (panel 8823-8832, strong opponents): HQ samples under pressure (enemy fighter in r2 34) 57% in losses (38% with >= 90 Ad banked) vs 6.5% in wins; our banked Ad 217 r300 -> 518 r600 -> 866 r800 in losses while Mn stays ~100 (HQ.build builds carriers only when !threatened; passive +6 Ad per 5 rounds per HQ). Strong bots keep banks ~200. Building c_gren1 = c_di1 + C.GREN: a threatened HQ with >= 90 Ad builds adjacent carriers (<= 3 near it) that withdraw 40 Ad and throw it (50 damage) at besiegers within r2 9, revert after 15 calm turns (workflow gren-build).
- 02:52 PDT c_gren1 built and reviewed (5 findings fixed: the birth rule now reads an HQ mark, AD_FLAGS bit 12+i 'built a grenadier last round', since ALARM is rewritten before the newborn acts; GREN_MAX counts the HQ's own grenadier IDs; idle top-ups keep 80 Ad). Gren1Test 172739 checks; unit-tests PASS.
- 03:20 PDT gh1-h2h (map seeds) c_gh1 vs c_di1 106/206 (asA 48, asB 58), map signal +3 (15/12), panel maps 9/20. c_gren1 diagnostic game vs arch_swarm (DefaultMap s1): won r542, never besieged so no grenadier fired; checks clean, exc_turns 0. gren1-h2h vs c_di1 started.
- 04:11 PDT c_di1 screen PASS vs c_isle1: (a) 8/8, (b) h2h 12/20, (c) roster net +1 (information only), (d) 148 games over 0 exc 0. trial-start c_di1 issued.
- 05:20 PDT c_di1 panel (gauntlet/20261018-111111-panel-c_di1) vs c_isle1's: identical 96, gained 1, lost 3, net -2 (-1.00 SE); island-rounds +42.8 (t 0.47); flips: pranayagra +1, awesomelemonade -1, britacatalin -1, georgezhang -1. **c_di1 REJECTED** (validated stays c_isle1, resubmitted as 188). Local 210/412 did not carry over. The GHOST/UHIT/GREN arms move onto c_isle1: c_gh2, c_uh2, c_gren2 = c_gh1/c_uh1/c_gren1 with C.DROP false (tests copied as Gh2Test, Uh2Test, Gren2Test; all pass).
- 05:24 PDT gren1-h2h c_gren1 vs c_di1 99/206 (asA 41, asB 58), map signal -4 (2/6), panel maps 11/20. Census of 8 loss replays: grenadiers fire (c_gren1 throws 5-25 a lost game, bank_end_Ad 100-366 vs c_di1's 98-9425) but do not turn games; c_gren1/c_gren2 parked. gh2-h2h-r (c_gh2 vs c_isle1, random seeds) and uh2-h2h (c_uh2 vs c_isle1, map seeds) started.
- 05:51 PDT unit-tests PASS with c_gh2, c_uh2, c_gren2 (Uh2Test's stack probe needed its class name renamed).
- 07:06 PDT gh2-h2h-r (random seeds) c_gh2 vs c_isle1 110/206 (asA 50, asB 60), map signal +7 (27/20), panel maps 8/20: GHOST 216/412 over two samples (c_gh1 vs c_di1 106/206). uh2-h2h (map seeds) c_uh2 vs c_isle1 95/206, signal -8 (8/16), panel maps 10/20: UHIT dropped. Screen c_gh2 and gh2-h2h (map seeds) started.
- 08:39 PDT screen c_gh2 (97a1c6db7095) FAIL: (a) 8/8, (b) 9/20 vs c_isle1 BORDERLINE without a pooled roster gain (info-only Net +5), (d) 148 games clean. gh2-h2h (map seeds) 107/206 vs c_isle1 (asA 45, asB 62), signal +4, panel maps 9/20. GHOST: 217/412 overall but 17/40 on the panel maps plus 9/20 in the screen: REJECTED at the screen, no trial. progress/ATTEMPTS.md started (owner, PROMPTS 130).
- 08:41 PDT unit-tests PASS with tools/attempts.py (AttemptsTest, 4 cases). Instrument check from the attempts table (43 panel trials with a net): screen (b) predicts the panel. b ≥ 12 (16 trials) mean net +1.7; b 10-11 (10) -0.3; b ≤ 9 (7) -2.6. The c_gh2 screen reject stands.
- 08:44 PDT plateau step 2 (ablate what we carry): abl1 on the VM (gauntlet/20261018-154424-abl1, 1240 games, MAXJOBS 6). c_isle1 vs c_ab01..c_ab15 = c_isle1 with one switch off each (tools/param.py, packages in build/abl1/ on the VM, not src/): RECALL, SPAWN_SAFETY, ARMY, PACK, SCOUT, ANCHOR_FLEE, AURA_SAFE, MEND, PROBE, HOT, MID, GUARD, HUNT, ISLE_THREAT false, SIEGE_ROTATE_FROM 2000. The 10 panel maps, both sides, 4 fixed seeds (919953836, 840799072, 215706231, 353760905). c_ab00 (identity) plays side A at the same seeds: the baseline for paired gains and losses per ablation, and a determinism check. The screen's (b) predicts the panel (08:41), so an ablation that wins on the panel maps is a candidate.
- 09:39 PDT c_isle1 panel (gauntlet/20261018-044752-panel-c_isle1, matches 9039-9048) vs the four strong bots (awesomelemonade 3/10, jmerle 4/10, vrangr1 5/10, pranayagra 5/10; the other six 46/60). Concentration is not the gap: in r100-350 fights we bring as large a share of our alive launchers as they do (0.31-0.45 vs 0.18-0.40); they simply have more alive (20-23 vs 12-16 in losses). The divergence starts before r100: in the 23 losses carriers built are equal at r100 (15.3 vs 15.5) but alive 12.5 vs 14.4, Mn collected 480 vs 543; by r300 alive carriers 11.9 vs 27.6, launchers built 53.7 vs 67.5. Our carrier deaths by r200: 9.2 a game in losses, 195 of 212 in the home 40% of the HQ-to-HQ axis. The 17 wins mirror it (their carriers die at their home). Early (r<=100) midfield fights in losses: peak 4.2 vs 3.9 launchers, value lost 450 vs 378 a fight; in wins 4.9 vs 2.9, 364 vs 545.
- 10:33 PDT abl1 partial (294/1240): c_ab03 (C.ARMY false: no launcher cohesion) 59/79 vs c_isle1 on the panel maps; paired vs the c_ab00 baseline gained 29, lost 9, net +20 (z +3.2), positive on 7 of 10 maps. c_ab01 RECALL off net +1, c_ab02 SPAWN_SAFETY off -5. Built src/c_loose1 = c_isle1 + ARMY=false (tools/param.py); screen queued (20261018-173314-scr-c_loose1-4ea6d24d2ebb); unit-tests running. VM disk 1.44 GB free: pruned build/classes-*, the gh2 h2h replays and abl1 replays except c_ab03's (2.2 GB free; abl1-prune loop keeps it so).
- 11:05 PDT unit-tests PASS with c_loose1.
- 11:07 PDT plateau step 7 design workflow (wf_9dfbc5a6-daf, research/diagnosis/2026-10-18-structural-designs.md): four structural designs vs the strong bots' early economy lead (economy, doctrine, information, copy), one judge. Winner c_evac1 (economy merged with copy): an HQ whose vision held >= 25 enemy fighter-rounds per bucket is flagged raided (AD_FLAGS bits 12-15); while another HQ is clear, carriers choose wells, deliver (bounded) and flee via the nearest clear HQ, and the raided HQ builds no carriers below 150 Ad. Evidence: in the 23 strong-bot losses the pressed zone yields about 4% of our Mn and about half our carrier deaths; 3.0-4.9 of 9.2 deaths a game by r200 are in scope; expected +1 to +2 panel games. Rejected: the doctrine design (a launcher screen in front of the home well: the c_front1/c_grp1/c_ward3 family, and against c_loose1's result). Implementation workflow running (wf_b703e46a-f35: implement, two reviews, fix).
- 12:15 PDT c_evac1 built by workflow wf_b703e46a-f35 (implement, identity and logic/bytecode reviews, fix): src/c_evac1 per the spec, c_evac0 = c_evac1 with C.EVAC false (javap: every c_isle1 method instruction-identical; unraided c_evac1 is not a replay, since added bytecodes shift MapMem/Field fill), Evac1Test 652 checks (mutation-checked on 8 broken copies). Fixed in review: evacHome kept after a throw; duplicate WELL record after a drop. Tools: ReplayDump LET_HQ code 10 'r', match_report WELL source 0 = 'evac' for c_evac* packages, docs/TELEMETRY.md. unit-tests PASS. c_loose1 screen: (a) 8/8, (b) 15/20 vs c_isle1; roster running.
- 12:44 PDT abl1 paused at 547/1240 (vm-stop; the rest in build/abl1/cells-rest.txt on the VM, 693 cells, to resume as TAG=abl1b): c_ab05 SCOUT off net -1, c_ab06 ANCHOR_FLEE off -3, c_ab07 AURA_SAFE off -2 (28 games). Trial c_loose1 started (submission 189, --skip-screen: (a) 8/8, (b) 15/20, roster still running; gauntlet/20261018-194500-panel-c_loose1) to finish before the 17:00 PDT autoscrim. The `timeout 900` around trial-start killed its block after all 10 requests were made: resumed at 12:59 with RESUME=<run> tools/contest.py block test/cells/panel-v1.txt --tag panel-c_loose1 (never wrap trial-start in timeout; run it in the background). c_evac1 driver game Maze vs arch_jm seed 919953836: won r374, HQ pressure on 1 turn, no raid (mechanism not exercised); DefaultMap vs arch_swarm next.
- 13:22 PDT screen c_loose1 (4ea6d24d2ebb) PASS: (a) 8/8, (b) 15/20 vs c_isle1, (c) information-only roster net +17 (117/120 vs the incumbent's 100/120; every archetype up: horde +5, swarm +4, jm +3, ampmid +3, blob +2), (d) 148 games clean (near 2). evac1-p4 started on the VM (MAXJOBS 2 beside the trial): c_evac1 vs c_isle1, the 10 panel maps x both sides x the 4 abl1 seeds (test/cells/panelmaps-4seeds-c_isle1.txt).
- 13:30 PDT c_evac1 driver game DefaultMap vs arch_swarm seed 919953836: won r451 (conquest); the raided carrier hold fired (HQ reason 'r', 14-25 HQ turns in the hq.csv codes), our carrier deaths by r300 3 vs 31. The mechanism is exercised; its effect is measured by evac1-p4.
- 13:34 PDT **c_loose1 ACCEPTED** (submission 189, validated): panel gauntlet/20261018-194500-panel-c_loose1 79/100 vs c_isle1's 73; paired net +6 (84 identical, gained 11, lost 5, +1.50 SE, sign p 0.21), island-rounds +303 (t +1.74). Strong bots 23/40 vs 17/40 (awesomelemonade 4, jmerle 5, pranayagra 7, vrangr1 7); gained vrangr1 3-1, awesomelemonade 2-1, NotLLeon 2-0, pranayagra 2-0, jmerle 1-0; lost georgezhang02 0-1, yaonam 0-1, britacatalin 1-1. LEARNINGS: ablation sweeps and the screen (b) instrument. Next: progress-refresh, resume abl1 (on c_loose1 now: rebase the remaining switches), c_evac2 = c_loose1 + EVAC after evac1-p4.
- 14:35 PDT evac2-p4 (c_evac2 = c_loose1 + raided-zone evacuation vs c_loose1, panel maps x4 fixed seeds) stopped at 30/67:
  paired with abl2's identity games (c_lb00) 62 identical, gained 1, lost 4, net -3 (Maze -3). It cannot reach the 40/80
  bar and changes too few games to matter: **c_evac2 dropped** (c_evac1's EVAC family closed; the deferred EYES design
  stays unbuilt). abl2 at 151/1000 (AURA_SAFE off +2, n 79). abl3 started (gauntlet/20261018-213333-abl3): 12 economy
  and production knobs on c_loose1 plus identity c_ec00 (CAP_MAX 45, CAP_PER_MN_WELL 12, CAP_MIN_PER_HQ 9,
  CAP_GROW_ROUNDS 25, AD_NEED 100, AD_EARLY_EVERY 4, AD_LATE_EVERY 3/6, ANCHOR_START 400, ANCHOR_MIN_LAUNCHERS 20,
  CARRIER_RETURN_LOAD 39, AD_BANK_CAP 300): the panel losses are to army size, which production sets.
- 16:01 PDT loose1-panel-losses workflow done (4 lenses, adversarial verify, judge; 9 agents):
  research/diagnosis/2026-10-18-panel-losses-c_loose1.md. 16 of 21 losses are army collapses first (median r300): a
  mana gap from r100 to r300 with an even launcher trade (r200-300: they collect 908 Mn per 100 rounds, we 547); 38-54%
  of it is the middle wells, the rest fewer live carriers (HQs pressured 32% of SL buckets vs 14% in SW) and less Mn
  per carrier (fleeing 6.5% of carrier turns vs 0.7%; Ad mined while Ad floats, 213 vs 67 at r300). c_loose1 cut our
  carrier deaths 3.83 a game (t -3.6). Small maps (BatSignal, Hah, ReverseFunnel: 9 of 21 losses) lose the island
  race: first anchor waits for r400 in 12 of 19 games, enemy islands undercounted, a ReverseFunnel anchor sink (23
  built, 0 placed). abl2 so far: AURA_SAFE off +2, MEND off -4, PROBE off -4, HOT off -3 (62 games). Built src/c_lx0 =
  c_loose1 + ANCHOR_SLACK (99 off), ANCHOR_RESERVE_MAX (2000 off), MID_URGENT (true = c_loose1); abl4 (build/abl4 on
  the VM, 680 cells, queued for abl2's slot): ANCHOR_BLIND_FROM 250, ISLE_MARGIN_SMALL 2, ANCHOR_SLACK 3,
  ANCHOR_RESERVE_MAX 50, MID_URGENT false, HOT_HOME_D2 48 + HOT_FRONT_PCT 20, BLIND 250 + SLACK 3, AD_BANK_CAP 100;
  identity c_lx00 must replay abl2's c_lb00 games exactly.
- 16:33 PDT abl2: HOT off net -7 (Cornucopia -4), MID off -6 (Cornucopia -4, Forest -4): both earn their keep, so
  the diagnosis's HOT and MID changes stay in abl4. abl3: CAP_MAX 45 +2 (neutral). abl4 extended to 920 cells with
  three Mid-squad knobs for the middle-well part of the mana gap (MID_MOD 2, MID_TOUR 200, MID_P_LO/HI 30/70), and
  queued on the VM to start when abl2 writes its summary (job abl4 waits; abl4-prune follows it).
- 18:54 PDT c_lx0 gains a fourth identity-default switch, SCREEN_ALL (false = c_loose1): true extends c_mid1's site
  rule to every well (a gathering carrier within r2 64 of its well keeps mining while our fighters outnumber theirs in
  vision, none is in attack range and one of our launchers is nearer the threat; diagnosis 1.3: our carriers flee on
  6.5% of turns in strong-bot losses vs 0.7% in wins). Unit tests PASS. abl4 rebuilt from it: 14 variants plus
  identity, 1160 cells (adds MEND_HP 120, MEND_R2 256, SCREEN_ALL true), still waiting for abl2. abl2: ISLE_THREAT off
  +2 (n 80), HUNT off -7, GUARD off +1; abl3: CAP_MIN_PER_HQ 9 -2, CAP_GROW_ROUNDS 25 -2, AD_NEED 100 +1 (n 67).
  Ladder (17:57 PDT snapshot): vibe23 #5, 1732.7; c_loose1 ranked 129/196, weakest vs awesomelemonade 5/19 and
  carlguo866 5/15 (not on the panel).
- 22:12 PDT abl2 DONE (stopped at 981/1000; c_lb12 decided): on c_loose1 no switch is worth removing. Paired net vs
  identity c_lb00 (n 80): AURA_SAFE off +2, MEND off -4, PROBE off -4, HOT off -7, MID off -5, GUARD off +1, HUNT off
  -7, ISLE_THREAT off +2, SIEGE_ROTATE_FROM 2000 -1, RECALL off -1, ARMY on GROUP_MIN 2 -23 (z -4.0), GROUP_MIN 3 -18
  (n 60). Cohesion stays off; HOT, MID, HUNT, MEND, PROBE earn their keep; AURA_SAFE, GUARD, ISLE_THREAT, RECALL and
  SIEGE_ROTATE are dead weight on the panel maps (candidates for bytecode savings, not for a win). abl3 so far:
  AD_LATE_EVERY 3 -6 and 6 -5 (4 is the local optimum), AD_EARLY_EVERY 4 -1, AD_NEED 100 +2, ANCHOR_START 400 +3
  (z 0.9), CAP_MAX 45 +2. abl4 started (gauntlet/20261019-051106-abl4, 1160 cells).
- 23:05 PDT abl4 identity check: c_lx00 (c_lx0 copy) replays abl2's c_lb00 games exactly, 39/39 (winner side and
  rounds): ANCHOR_SLACK, ANCHOR_RESERVE_MAX, MID_URGENT and SCREEN_ALL are inert at their defaults. abl3: ANCHOR_START
  400 +3 (z 0.9), ANCHOR_MIN_LAUNCHERS 20 +1, CARRIER_RETURN_LOAD 39 -8 (n 79).
- 23:53 PDT abl3 DONE (gauntlet/20261018-213333-abl3, 1000 games): no economy knob is clearly positive on c_loose1.
  Paired net vs identity c_ec00 (n 80): CAP_MAX 45 +2, CAP_PER_MN_WELL 12 -1, CAP_MIN_PER_HQ 9 -2, CAP_GROW_ROUNDS 25
  -2, AD_NEED 100 +2, AD_EARLY_EVERY 4 -1, AD_LATE_EVERY 3 -5, 6 -5, ANCHOR_START 400 +3, ANCHOR_MIN_LAUNCHERS 20 +1,
  CARRIER_RETURN_LOAD 39 -8, AD_BANK_CAP 300 -1. The current values sit at or near a local optimum in self-play.
  abl4 so far: ANCHOR_BLIND_FROM 250 -1 (3 games changed), ISLE_MARGIN_SMALL 2 and ANCHOR_SLACK 3 change 0 of 80
  games: the strong-bot mechanisms the diagnosis found (late blind anchors, anchor sinks, enemy island fortresses) do
  not arise in self-play, so these levers can only be judged on the panel. abl5 started (stack of the abl3
  near-misses, 360 cells): c_st01 CAP_MAX 45 + AD_NEED 100 + ANCHOR_START 400; c_st02 = c_st01 + ANCHOR_MIN_LAUNCHERS
  20; c_st03 CAP_MAX 45 + AD_NEED 100; c_st04 ANCHOR_START 400 + ANCHOR_MIN_LAUNCHERS 20.

## 2026-10-19

- 01:13 PDT built src/c_sm1 = c_lx0 + ANCHOR_BLIND_FROM 250 + ISLE_MARGIN_SMALL 2 + ANCHOR_SLACK 3 +
  ANCHOR_RESERVE_MAX 50 (diagnosis 2026-10-18-panel-losses-c_loose1 changes 1-4, the small-map island race and the
  dead anchor reserve). Self-play cannot judge it (abl4: the four levers change 0-3 of 80 games each), so it goes to the
  panel: screen when abl5 frees a VM slot, trial after the 01:00 PDT autoscrim round. Unit tests PASS. abl4 so far:
  ANCHOR_RESERVE_MAX 50 +1, MID_URGENT false -2; abl5: c_st01 (CAP_MAX 45 + AD_NEED 100 + ANCHOR_START 400) +3 (n 70).
- 03:46 PDT abl5 (stacks of abl3 near-misses vs c_loose1, paired with identity c_st00, n 80): c_st01 CAP_MAX 45 +
  AD_NEED 100 + ANCHOR_START 400 +4 (z 1.0); c_st02 = c_st01 + ANCHOR_MIN_LAUNCHERS 20 +6 (46/80, gained 11, lost 5,
  z 1.5); c_st03 CAP_MAX 45 + AD_NEED 100 +3; c_st04 ANCHOR_START 400 + ANCHOR_MIN_LAUNCHERS 20 +4 (n 47). The parts
  add up. Built src/c_eco3 = c_st02 (unit tests PASS). abl4: BLIND 250 + SLACK 3 -1 (inert), AD_BANK_CAP 100 -2
  (n 63), MID_URGENT false -1, HOT_HOME_D2 48 + HOT_FRONT_PCT 20 0. Candidates now pull anchors opposite ways: c_sm1
  (earlier on small maps, the diagnosis vs strong bots) and c_eco3 (later, self-play); the panel decides.
- 04:59 PDT c_sm1 screen (20261019-105251-scr-c_sm1-5282467d56a4): (a) 8/8, (b) 10/20 vs c_loose1 = the identity
  level, as abl4 predicted for self-play-inert levers; (c) roster and (d) basics still running. Trial c_sm1 started
  (submission 190, --skip-screen with that reason, requests 4614-4623, logs/trial-c_sm1.log) to finish before the
  09:00 PDT autoscrim. abl4 paused at 855/1160 to keep two VM runs (rest: build/abl4/cells-rest.txt, 305 cells:
  c_lx11 MID band, c_lx12 MEND_HP 120, c_lx13 MEND_R2 256, c_lx14 SCREEN_ALL). abl4 so far: AD_BANK_CAP 100 -1,
  MID_MOD 2 +1, MID_TOUR 200 -2.

### 05:36 PDT: c_sm1 rejected (panel, submission 190)
- Panel gauntlet/20261019-115903-panel-c_sm1: 80/100. Paired vs c_loose1: 99 of 100 games identical, gained 1
  (jmerle), lost 0, net +1 (p = 1).
- Island-rounds per game vs c_loose1 by map: BatSignal +90, Hah +60, ReverseFunnel +23 (the small maps the levers
  aimed at moved a little but no result flipped); Cornucopia -1413 (anchors built -4.9: ANCHOR_SLACK 3 starves
  anchors on a 5-island map where we already win). Mean -92 (t -0.88).
- Lesson: the small-map losses are decided before anchors matter (army collapse first, as the diagnosis said);
  anchor timing alone does not flip them. Next: c_eco3 screen (started 05:35 PDT).

### 06:29 PDT: c_eco3 ACCEPTED (panel, submission 192)
- c_eco3 = c_loose1 with CAP_MAX 45, AD_NEED 100, ANCHOR_START 400, ANCHOR_MIN_LAUNCHERS 20 (abl5 stack c_st02 of
  four abl3 near-misses, self-play net +6, z 1.5). Screen skipped with a recorded reason (param-only; the sweep is 80
  paired games against c_loose1). Trial started 05:43, panel gauntlet/20261019-123523-panel-c_eco3: 82/100 vs
  c_loose1's 79. Paired: 97 identical, gained 3 (georgezhang02, jmerle, pranayagra), lost 0, net +3 (+1.73 SE,
  sign p 0.25).
- Island-rounds -196 per game (t -1.50): the first anchor comes 65-247 rounds later on every map and Cornucopia
  (-1085, a map we win anyway) carries most of it. The economy trade cost islands and bought results.
- c_sm1 screen (information only after its panel reject): FAIL, (b) 10/20, roster net +0, basics clean.
- Next: rebase c_mid3 (MID_URGENT false, MID_MOD 2) on c_eco3; abl4b running (305 cells).

### 08:16 PDT: abl4 complete; awesomelemonade diagnosis; KILL_STEP built (abl7)
- abl4 + abl4b (1160 games, c_lx0 levers vs c_loose1): every lever within +-2 of identity over 80 games (MEND_HP 120
  +1, MEND_R2 256 -1, SCREEN_ALL -1, MID_P 30/70 -2, MID_MOD 2 +1, RESERVE 50 +1). Nothing to take forward from
  self-play.
- Workflow diag-awesomelemonade (research/diagnosis/2026-10-19-awesomelemonade.md; 19 distinct losses, panel and
  ranked): at equal armies before r300 our exchange is 0.89 vs it (1.19 vs the other strong bots). Its step-in hits
  kill 0.157 vs our 0.080 (S4 0.112/0.115); 27% of our step-in hits go to a target 40+ HP healthier than a reachable
  one (its 16%); it chains same-round kills (42% of kills take 2+ hits that round, ours 24%). Our parity hold never
  lets a launcher step in for a one-shot kill. Fortress verified (damage per kill 197 -> 289 after its first anchor,
  it heals 27% of damage taken) but second-order. Late losses: HQ code 't' 57% of HQ turns with 185 Ad idle.
- Built src/c_kx0 (c_ex0 + C.KILL_STEP, 0 = identical bytecode up to local slots), c_ks1 (kill tile = one threat
  less, +5,000) and c_ks2 (plus focus on the lowest-HP fighter in range). abl7 on the VM: identity c_k700 and
  KILL_STEP 1/2 vs c_eco3, 80 games each (micro, so self-play can judge it).

### 10:48 PDT: abl6-abl8; replica replay indicators rechecked; c_adp1 screen
- abl6 (middle squad, vs c_eco3, 80 games each): c_mid3 (MID_URGENT false + MID_MOD 2) net -3, MID_MOD 1 net -2,
  MID_MOD 2 alone 0. c_mid3 dropped (not positive).
- abl7 (KILL_STEP): 1 = net 0 (8/8 discordant), 2 = net -2. c_ks2 dropped; c_ks1 gets a 103-map h2h vs c_eco3
  (ks1-h2h, running) before any panel.
- abl8 (AD_PRESS_MN): net +2 (gained 3, lost 1). c_adp1 screen queued with --roster none (c_eco3 has no cached roster
  games, so the full screen would end too late for a trial before 17:00); stage (a)/(b)/(d) only.
- Owner PROMPTS 131-132: replica replays carry no indicator data (0 strings, dots or lines over 160,212 robot-turns of
  990f5131; control fixture 9,098 of 9,098). The circles were IvanGeffner's destabilize effects (r784, r788 at
  (23,30-31) on FourNations) and the selected robot's range rings; the "Indicator String:" field is always shown.
  docs/TELEMETRY.md section 0 notes it.
- VM disk 1.66 GB: purged old sweep replays (abl2-abl5, evac1/2-p4), build/classes-evac1/2, /var/log/syslog.1 and
  journald archives to 50M (2.4 GB free). Replica replays older than 4 days hold 2.8 GB; not touched (the owner views
  them on the site).

## 2026-10-19 13:05 PDT: c_adp1 ACCEPTED; c_ks1 dropped; match 10023 cancelled; top-2 diagnosis started

- **c_adp1 accepted (submission 193)**: c_kx0 with AD_PRESS_MN true. Panel gauntlet/20261019-182439-panel-c_adp1
  83/100; paired vs c_eco3's panel: 99 identical, gained 1 (britacatalin), lost 0, net +1 (+1.00 SE); island-rounds
  +60 (t +0.74). With abl8 (gained 3, lost 1) the change gains 4 and loses 1 over 180 paired games. awesomelemonade
  stays 4/10, so the targeted mechanism flipped no AL game. Accepted on the c_hr1/c_isle1 precedent (net +1, nothing
  lost) and the low risk to wins (pressed HQ in 1% of rows of wins).
- **c_ks1 dropped**: ks1-h2h (gauntlet/20261019-170220-ks1-h2h, 103 maps both sides) 101/206 vs c_eco3, signal -2.
- **Replica match 10023** (sprintBot vs pranayagra.finalbotfinal, autoscrim 09:00) stuck in RUN: cancelled 11:57 with
  tools/galaxy/cancel-match.sh --cancel. The same pairing stuck before (7880).
- **Top-2 gap**: ladder #5 (1767) behind carlguo866 1826, awesomelemonade 1826, maxwelljones14 1805, IvanGeffner
  1769. Ranked vs carlguo866 11/30, vs maxwelljones14 6/18 (neither is on the panel). In our 31 losses to them median
  Mn@100 292 vs 373 and L@250 6 vs 19; in our 17 wins Mn@100 598 vs 347. Workflow diag-top2 (4 analysts +
  synthesis) on the 16 matches.

## 2026-10-19 14:41 PDT: diag-top2 (carlguo866, maxwelljones14); five switches in c_kx0; sweep abl9

- **Diagnosis** research/diagnosis/2026-10-19-top2.md (workflow diag-top2: 4 analysts + synthesis, 48 ranked games).
  The openings are identical (4 launchers + 4 carriers per HQ). M1 (17 of 31 losses): we lose the home economy by
  r150: the opponent's launchers camp our home Mn well (frontGate calls it home, so it never turns hot), our carriers
  die there (105 vs 17 by r100), Mn binds (launchers r101-250 210 vs 407). M2 (5): the first launcher war lost at
  parity (our victims die 2 v 2, theirs 5 v 1.5). M3 (9): midgame islands (they hold one at r300, we at r470; the
  deficit clause closes our anchor gate 0.73 of samples). Basics: sealed spawn pockets (Jail 2 carriers, ThirtyFive 3
  of 4 opening launchers stuck all game). Per-shot micro is even (51 vs 48 hits per 100 contact turns).
- **c_kx0 switches** (defaults = c_eco3/c_adp1; unit tests PASS): SPAWN_POCKET (HQ.sealed: flood fill per spawn tile,
  cached), JOIN_MIN (lone kind-0 launcher near home waits for a partner, FORM_MAX_TURNS cap), CENTRE_SKIP_R2 (no
  centre-first leg next to an enemy HQ), GATE_DEFICIT_UNTIL (island-deficit gate clause ends earlier), CAMP_MIN (a
  camped home well turns hot; the synthesis's edit was inert because markHot/hotLocal filter by front(): hotCamp
  carries it). Static scan: pockets of 1-3 tiles only on Clown, Jail, ThirtyFive.
- **abl9** (VM gauntlet/20261019-210733-abl9, vs c_adp1, 388 games): identity c_k900 40; JOIN_MIN 2, GATE_DEFICIT
  800, CAMP_MIN 2 on panel maps x both sides x 4 seeds (80 each); SPAWN_POCKET 4 on Clown/Jail/ThirtyFive x 2 x 4;
  CENTRE_SKIP_R2 100 on the 21 centre maps x 2 x 2.

## 2026-10-19 16:43 PDT: abl9 results; c_gd1 built for the panel

- **abl9 + abl9b** (vs c_adp1; identity c_k900 86 games): JOIN_MIN 2 net -6 (7/13, z -1.3), CAMP_MIN 2 -3 (3/6),
  GATE_DEFICIT_UNTIL 800 inert (0 of 80 changed), SPAWN_POCKET 4 +1 (8/7 of 24 on Clown/Jail/ThirtyFive; ThirtyFive
  +1; ThirtyFive still_L 0.51-0.55 vs 0.58-0.61 in the same games), CENTRE_SKIP_R2 100 net 0 (SoundWave +2, Lantern +2,
  River +1, Fractured -2, Maze -2, PairedProgramming -1). The gauntlet keeps only BOT-loss replays, so kept replays
  cannot pair.
- JOIN_MIN and CAMP_MIN dropped (negative in self-play); CENTRE_SKIP held (net 0, -2 on the panel map Maze).
- **c_gd1** = c_kx0 + AD_PRESS_MN + GATE_DEFICIT_UNTIL 800 + SPAWN_POCKET 4 (unit tests PASS): panel trial after the
  17:00 autoscrim (GATE_DEFICIT is panel-only; SPAWN_POCKET is inert on panel maps).

## 2026-10-19 18:28 PDT: c_gd1 and c_gx1 parked; IvanGeffner probe; GHOST and OPEN_CAMP switches; abl10, abl11

- **IvanGeffner after the accept**: c_adp1 (sub 193) went 1/24 in ranked games vs IvanGeffner, c_eco3 (sub 192)
  11/15. 9 of c_eco3's 11 wins were IvanGeffner resigning at r401; the maps of the two sets barely overlap, the one
  shared (AllElements) replayed identically, and the record before c_eco3 was 6/33. Likely map draw, not
  AD_PRESS_MN. Probe ivan-probe (logs/ivan-probe.log; matches 10334-10336): c_adp1 replays c_eco3's ranked wins
  9922, 9933 and 10037 on the same maps and order; identical games would clear AD_PRESS_MN.
- **c_gd1 parked** (submission 194, panel matches 10337-10346, run gauntlet/20261020-001652-panel-c_gd1).
- **GHOST** ported into c_kx0 (agent; bytecode-identical when off; Gh2Test PASS on the ON build). abl10 (vs c_adp1,
  panel maps x 2 x 4): net -2 (7/9). **c_gx1** = c_adp1 + GHOST: trial (submission 196) parked 18:28, panel matches
  10347-10356.
- **OPEN_CAMP** in c_kx0 (agent; javap-identical when off): plateau step 4, copy the offence that beats us.
  Launchers born before r60 march to the mirror of their HQ's nearest Mn well (the enemy's home well; symmetry:
  single candidate, else the one mapping our HQ to the siege target) and hold r2 4-9 from it until r200. abl11 (VM,
  vs c_adp1, 160 games): c_k1101 (hold r2 4-9) and c_k1102 (hold r2 20).

## 2026-10-19 20:30 PDT: OPEN_CAMP +6 (c_cp1 to h2h); defences inert vs a camper; IvanGeffner cleared; BANK_FROM; jams

- **abl11 (OPEN_CAMP, vs c_adp1, 8 panel maps x both sides x 5 seeds, paired with abl9's identity c_k900)**: c_k1101
  (hold r2 4-9) 46/80, gained 21, lost 15, net +6 (z +1.0; Cat -4, Cornucopia +4); c_k1102 (hold r2 20) net +4.
  **c_cp1** = c_kx0 AD_PRESS_MN + OPEN_CAMP (= c_k1101): cp1-h2h (103 maps both sides vs c_adp1) running on the VM.
- **abl12 (defences vs the camper c_k1101, 80 games each)**: c_adp1 34/80, CAMP_MIN 2 36/80, JOIN_MIN 2 31/80. Inert
  within noise and negative in self-play (abl9): neither defence goes forward; the third leg (both) was stopped.
- **IvanGeffner probe (matches 10334-10336)**: c_adp1 replays c_eco3's ranked wins 9922/9933/10037 on the same maps
  with the same results (8 of 9 wins, the same Marsh tiebreak loss). The 1/24 vs 11/15 gap was the map draw, not
  AD_PRESS_MN. IvanGeffner resigns at r401 on many maps (5 of these 9 games).
- **Tiebreak audit (ranked, matches >= 9400)**: 25 of 318 games reached r2000 and we lost 16, mostly after losing the
  fights (12 tb_islands). LookingGlass 9493/9500/9502: islands tied 4-4, lost on Mn (136 banked vs 2,166 after
  collecting 35k vs 18k). Re-anchoring an own island counts 0 for tiebreak 2 (RULES 8.4), so the lever is the bank:
  **C.BANK_FROM** (c_kx0; from that round an unthreatened HQ builds no launchers while the shared island counts are
  tied). abl13: c_k1301 (1850) and c_k1302 (1700) vs c_adp1 on 8 r2000-prone maps (LookingGlass, Potions,
  Cornucopia, Forest, Fractured, SoundWave, ThirtyFive, Cee) x both sides x 3 seeds, identity c_k1300.
- **Jams**: ranked 10146 Potions (lost the islands tiebreak by 1 while ahead 20 to 10 launchers at r1000): from r915
  at least 15 of our units froze in the HQ pocket (the 1-wide corridor y=11 x 31-36 and the 2-wide column x 38-39) and
  the HQ could not build (665 Mn floated). Since match 9400 only Potions shows jam losses (2 of 4 games); self-play on
  Potions did not reproduce it (one carrier stuck 1,296 rounds in a bottle room). Cornucopia 10114 (won the r2000
  tiebreak with 734 launchers to 4): couriers spent hundreds of turns in E (no target) and Y; islands 2, 5, 7 were
  never taken, likely stale enemy-owned island slots (a launcher far from an HQ cannot write the neutral sighting).

## 2026-10-19 21:17 PDT: c_gd1 ACCEPTED (submission 198)

- Parked panel gauntlet/20261020-001652-panel-c_gd1: 86/100; paired with c_adp1's panel: 91 identical, gained 6, lost 3,
  net +3 (+1.00 SE; jmerle +2, awesomelemonade +1, pranayagra +1, vrangr1 1-1, britacatalin -1). GATE_DEFICIT_UNTIL
  800 was inert in self-play (abl9 c_k902) and SPAWN_POCKET 4 touches no panel map, so the gain is the deficit gate on
  the panel (diag-top2 M3) or replica noise between builds; trial-decide --accept at 21:17 PDT.
- 21:46 PDT **c_gx1 rejected** (GHOST): parked panel gauntlet/20261020-012643-panel-c_gx1 vs c_adp1's panel 98 identical,
  gained 1, lost 1 (net 0); vs c_gd1's net -3. With abl10's -2 in self-play, GHOST is closed.

## 2026-10-19 22:26 PDT: home raids are a consequence; audit of c_gd1 launched
- **Home-raid metric** (`raid.py`, ranked matches >= 9400): an undefended home raid before r600 (enemy group >= 4 at prog
  <= 0.2 from our side, <= 1 of ours) appears in 67% of 343 losses and 15% of 689 wins. prog is measured from side A's
  HQs (ReplayDump: dA/(dA+dB)) and mirrored for side B; hq.csv of 10346 g2 confirms the sides. But at the first raid our
  live launchers trail theirs by >= 2 in 199 of 229 raided losses (ahead in 21); in raided wins we lead in 60 of 100.
  The raid follows a lost army; a recall defence would bring home an army that is already outnumbered. Not pursued.
- **Launcher-lead arcs** (alive L, us minus them, at r150/250/400/600; `arc.py`): losses `----` 38%, `---.` 12%; wins
  `+++.`/`++++` 74%. Half of our losses trail by r150. In those 197 losses at r150: built_L -3.3, alive_L -6.7, kills
  -7.4, coll_Mn -210, alive_C -4.6. Behind at r150: carlguo866 46%, maxwelljones14 48%, AnOvercookedFork 43%,
  IvanGeffner 37%, awesomelemonade 36%, jmerle 35%; vrangr1/georgezhang02/yaonam 10%, NotLLeon/Sprint1/reeceyang 0%.
  Averages per opponent are level at r30-150 (built_L 24.3 vs 23.3 carlguo866, 27.5 vs 26.3 awesomelemonade), so it is
  per-game variance in early fights (diag-top2 M1/M2), not the build order.
- **Pinned resource**: vs awesomelemonade our HQ bank of Ad averages 128 at r200, 262 at r450, 425 at r600 (theirs ~90);
  vs carlguo866 88/211/356. Field census: no team but IvanGeffner (Ex in 26% of games, destabilizers 1.8/game) and
  vrangr1 (7%) uses elixir; awesomelemonade builds 195 launchers per game to our 152.
- Plateau protocol step 1 (last bot audit 2026-10-07): workflow `audit-c_gd1` (4 lenses: shared state, movement and
  jams, launcher combat, economy; one adversarial verifier per lens; read-only, no JVM). c_im1 unit tests running; its
  trial waits for the 01:00 PDT autoscrim (trial window 2.5 h). abl13 at 78/144.
- 23:14 PDT **abl13 (BANK_FROM) inert in self-play**: gauntlet/20261020-031646-abl13 vs c_adp1, 8 r2000-prone maps x 2
  sides x 3 seeds: identity c_k1300 30/48, c_k1301 (1850) 30/48 with 48 of 48 games identical, c_k1302 (1700) 30/48 with
  47 identical (SoundWave differs, same result). 20 identity games reach r2000 (14 W, 6 L) and none flip. c_bk1 parked
  as a field-only lever to stack on a later candidate. c_im1 committed (b172f29, unit tests PASS); trial after 01:00.

## 2026-10-20 01:18 PDT: audit-c_gd1 (3 of 4 lenses verified); FIELD_WALL_SIDE; c_im1 trial parked
- **audit-c_gd1** (shared state, movement, economy verified; combat lens still running). Verdicts:
  - CONFIRMED, medium: **stale field with a sidestep** (Nav.java:145). A field is rebuilt only when no downhill and no
    same-wave square is free (Nav:157), so a carrier whose downhill squares proved to be walls sidesteps and steps back
    (moveTwice A->B->A) for the rest of the game. c_gd1 panel: carriers still 100+ rounds on x=5 in 10 of 10 Forest
    games (3,2,1,3,5,3,2,1,2,8; 9,243 carrier-rounds; 10337 g4 #10780 1,110 rounds); ranked 9913 g1 PairedProgramming
    #10151 444 rounds (a loss), 9929 g0 Forest #10840 416. The verifier rebuilt the stale fields (levels 4 vs a true
    13) and reproduced the loop. These are the V13 "frozen carriers" of diag-top2, now located.
  - CONFIRMED, low (mostly in won games): island news published 1 turn in 5 (phantom islands in 17 of 609 games, all
    in wins); ISLE_STICKY overwriting neutral with a 15-round-old 'theirs' (1 game of 609); blind anchors carried with
    no target (99.4% of the wasted turns in wins); the carrier census partial at phase 32 of each epoch and the carrier
    room spent twice (both bind in won games); anchors taken with no island target.
  - PLAUSIBLE, low: Potions corridor plug (the proposed fix would not clear the observed stall); unjam blind to a
    within-turn oscillation; MassiveL crowd switching (2 of 10 panel games, both won); island slots carry no time.
- **C.FIELD_WALL_SIDE** in c_kx0 (Nav.moveTo: wallDown requests the rebuild, throttled by FIELD_RESTART, before the
  sidestep; false = c_eco3). Identity copy c_fw0 vs c_gd1: javap differs only by the dead GHOST/OPEN_CAMP methods and
  BANK_FROM's never-true round test. **c_fw1** = c_gd1 + FIELD_WALL_SIDE: fw1-h2h (103 maps x 2 sides vs c_gd1,
  SEED_MODE=map, replays kept for the stuck-carrier count) running on the VM; unit tests running.
- **c_im1** trial 199 started 01:12 after the 01:00 autoscrim; parked 01:18 (panel 10567-10576), c_gd1 active as 200.

## 2026-10-20 03:29 PDT: combat lens, SHOOT_KNOWN, cloud-fire contrast, MEMSHOT; c_fw1 delivered and on trial
- **fw1-h2h** (c_fw1 vs c_gd1, 103 maps x 2 sides): 100/206, signal -3 (neutral). Delivery from the kept replays of
  Forest, MassiveL, PairedProgramming x both sides: carriers still 100+ rounds c_fw1 0 in 6 games; c_gd1 5 (2,285
  rounds) on Forest side A and 1 on PairedProgramming in each game; 0 exceptions, 0 overruns. A basics fix with
  delivery shown: trial 201 started 02:50, parked 02:55 (panel 10577-10586; c_gd1 active as 202).
- **Combat lens** (audit-c_gd1): CONFIRMED low-medium, a step-in onto a cloud loses the planned shot (vision r2 4 after
  the move; ours attacked after 4 of 258 cloud step-ins vs strong teams, theirs 274 of 274) -> C.SHOOT_KNOWN, c_sk1
  (sk1-h2h running). CONFIRMED low: aura avoidance ignores the end-of-round current push (deaths in won games); a
  launcher with its action spent steps randomly 1 turn in 3 (rand(3) beats CENTER +1); C.MICRO2 is never read.
  PLAUSIBLE: track() resets the pinned list on blind turns. Record: research/diagnosis/2026-10-20-audit-c_gd1.md.
- **Cloud-fire contrast** (per-turn launcher dumps of 51 games vs strong teams, `cloud/c2.py`, `c3.py`): in contact
  (an enemy launcher within r2 20 by replay truth) both sides stand on clouds about as often (ours 32.9%, theirs
  30.5%) and lose as much HP the next turn (5.4 from a cloud, 8.2 from clear). But hits per contact turn: on a cloud
  ours 0.26, theirs 0.36; on clear ours 0.58, theirs 0.60. From clouds they fire 18,503 shots at d2 > 4 (unseen) and
  hit 5,648 (31%); ours fire only at what they see (3,258 such shots, all hits). About 45 hits (900 damage) a game.
  c_blind2's memory targeting never fired on its panel (100/100 games identical to c_blind1): the idea is untested.
- **C.MEMSHOT** in c_kx0 (an action still unused at the end of the turn fires at memPick's tile: an enemy fighter seen
  at most MEMSHOT_AGE 2 rounds ago, tile within r2 16, not sensable now, the robot not in vision; MEM = GHOST ||
  MEMSHOT; false = c_eco3). **c_ms1** = c_gd1 + SHOOT_KNOWN + MEMSHOT: ms1-h2h running on the VM; unit tests running.
- 03:58 PDT STUCK_MATCH 10487 (ranked autoscrim 01:00 PDT, battlecode-archive.sprintBot vs pranayagra.finalbotfinaltwo,
  RUN > 1 h; the repeat offender of 7880 and 8689; not ours): cancelled + re-rated (tools/galaxy/cancel-match.sh).
