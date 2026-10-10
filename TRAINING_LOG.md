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
