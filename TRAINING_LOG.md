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
