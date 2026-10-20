# Side asymmetry audit, 2026-10-20 (owner, PROMPTS 139-140: play symmetry)

Workflow wf_ff483959-431: three independent investigations (map and engine statistics; replays and transformed-map experiments; code audit of src/c_kx0) and a synthesis. Scratch data: the session scratchpad side/ (not kept).

## Synthesis

**Side asymmetry: merged verdict, how much of the 59 vs 49 panel gap each cause explains, and one candidate spec**

**Verdict: (c) a mix, but it is not a map or engine effect, and no fixable bot cause explains the panel gap.**

**1. What makes the per-map self-play bias**

- **The maps and the engine are not the cause.** All 103 maps are exactly symmetric: no feature differs between the teams on any map (mapfeats.csv). Moving first barely matters:
  - With truly random seeds the first mover wins 49.2% (90/183, identical bots) and 48.8% pooled.
  - Swapping the HQ IDs left Grievance at A 7/7.
  - Squares is the one exception: its HQs are adjacent and central (d² 10), and the first mover won 25/30 across every orientation.
- **Most of the extreme counts are a measurement artifact.** About 6,700 of the 12,438 pooled games used the map's own seed. Each of those games is deterministic, so near-identical builds replay the same game:
  - 4,274 games share their exact (map, winner, rounds) with another game. On Risk, 34 of 53 are the same B win at round 407.
  - Excess between-map variance is 0.083 with the map seed and 0.0095 with random seeds.
  - In paired cells, the same side won both games 75.8% of the time with the map seed, 76.6% with other fixed seeds, and 52.6% with random seeds.
- **What survives random seeds is our bot's code.** The A/B label itself has no effect: a map transformed by its own symmetry reproduced the ID-swapped game at the same round in 48/48 pairs. Our code is still not mirror-invariant: 144/144 transformed games diverged and 52% changed winner.
  - **Seed-locked maps** (the bias goes away with random seeds): Risk, Heart, Spiral, ArtistRendition, maptestsmall, SomethingFishy, and BuildSite (5-5 on random seeds). The cause is decisions keyed on robot ID: `Nav.java:26`, `Carrier.java:173-175`, and the per-unit random stream seeded by ID in `G.java:58`.
  - **Position-locked maps** (the bias survives new seeds): Grievance, Diagonal, Rectangle, Sneaky, TicTacToe, Tightrope and SmallElements.
- **The one position cause shown to change outcomes is the army's siege target.** It is measured from a centroid of our HQs rounded down, and ties go to the lower x, then the lower y (`c_kx0/Launcher.java:706,742`; c_gd1 `:473,509`). Evidence:
  - Rounding the centroid up instead flipped Grievance (B 5/6), TicTacToe (A 6/6) and Sneaky (B 5/6).
  - The c_gdy ablation cut Diagonal's west-side wins from 24/24 to 13/24.
  - My simulation: the two teams' targets are not mirror images on 23 maps at game start and 16 once the symmetry is decided.

**2. The panel gap (A 59, B 49; 22 cells won on one side only, 16 by A, sign p=0.052)**

| Cause | Share of the 10-game gap | Evidence |
|---|---|---|
| Move order | 0 | We won 54 games moving first and 54 moving second |
| Map features | 0 | No per-team differences on any map |
| ID luck | 0 expected | It makes cells discordant but has no direction |
| Self-play favoured side | about 2 at most | Matches 13 of the 22 one-sided cells (11 by chance); r=0.18, p=0.076 |
| Round-1 HQ build cliff | about 1 at most | On the 18 maps where our B HQs build at least 3 fewer units, the panel went A 11, B 10 (my check) |
| Siege-target mismatch | 0 to 5 | On the 22 panel maps where the opening targets are not mirror images: A 17, B 11, one-sided cells 7-1. Elsewhere 42-38 (9-5). Fisher p=0.35 |
| Unexplained | about 5 to 9 | Consistent with chance, and with field bots that are themselves side-dependent |

Across 468 paired replica cells for all builds, A minus B is +1.3±2.0 pp. A free replication is already running: c_ms1's v2b block (trial 207, 3 of 10 matches done). On those three opponents it has 13/30 as B against 15/30 as A on v2. c_gd1 had 12/30 against 15/30 on the same opponents.

**3. Where the investigations disagree**

- **Squares:** mechanics put it with the ID-following maps, but its ID swap also swapped move order. The code investigation's transform experiment separates the two (30 games), so Squares is a move-order map.
- **"Random seeds":** the replays investigation's 5,665 games include fixed seeds other than the map seed, which are also deterministic; that is where Risk 2-14 comes from. The mechanics split (1,030 truly random games) is cleaner. c_gd1 on Risk with random seeds: A 5/8 and A 5/6.
- **Round-1 cliff:** the code investigation called its effect suggestive (p=0.027 by category). A dose-response test contradicts it:
  - In c_gd1 self-play on random seeds, A won 7/18 where B was at least 3 units short, 38/60 where B was 1-2 short, 49/89 where builds were equal, and 6/16 where A was short. There is no upward trend.
  - The panel shows 11-10 on the B-short maps. I weight the dose-response test more.
- **Where the gap sits:** the investigations sliced the 22 one-sided cells by one-HQ maps (14 vs 8), maps where A builds more (8-2) and self-play bias bands. All are after-the-fact slices of 22 cells and none is significant.

**4. Fixable bot causes, ranked by expected gain against the field (all small)**

1. **Round-1 build cliff** (`HQ.java:75` reserve of 7,000 bytecodes; `:208-216` runs a flood fill for every improving tile).
   - c_gd1 B HQs are short on round 1 in 91/194 cases, A HQs in 56/194; B misses 164 units, A 74 (my recount).
   - It is the only cause whose fix is a pure improvement: the same tiles, built sooner. The fix is shown to work (section 5), but no outcome effect has been measured, so expect about 1 panel game at most.
2. **Siege-target equivariance.** It has the strongest causal evidence in self-play but no shown gain against the field. Making the targets mirror images only replaces A's or B's current choice on each map, arbitrarily. c_gdy also turned 10/24 Grievance self-play games into round-2000 tiebreaks.
   - Possible design, if wanted for measurement: compare distances to the exact centroid with integer math, (n·e.x−Σx)²+(n·e.y−Σy)². Break ties with team A on `enc(e)` and team B on `enc(img(sym,e))` once the symmetry is decided; before that, use the frame that makes our own HQ list smallest in sort order.
   - Simulated: mirror-consistent targets on 92/103 maps at game start (now 80) and 103/103 once decided (now 87).
   - No rule without the team label can fix the 11 maps where a team's own HQs are symmetric (including Grievance, Rectangle and SmallElements).
3. **ID-keyed roles and wall-following hand:** zero expected gain. Each unit's random stream is also seeded by its ID, so the luck stays either way.
4. **Rounded-down map centres, direction order and x-major sensing order:** zero expected gain, spread across many places and unmeasured.

The step worth more than any of these is not a bot change: run head-to-heads on explicit random seeds, the same seed for both sides. se-h2h ran on map seeds (`TRAINING_LOG.md:2640`), so its 206 games are 206 single deterministic draws.

**5. Candidate spec: `SPAWN_TWO_STEP`**

`C.java`, after line 165:
```java
/** Round-1 batch (side audit 2026-10-20): with SPAWN_POCKET > 0 tryBuild ran sealed() for every tile that beat the best
 *  so far; HQs whose goal lies toward low x ran 10-16 fills on round 1 and the 7,000 reserve stopped them at 1-4 of 5
 *  (c_gd1: B 91/194 HQs short, A 56/194). true: fill only the chosen tile (a sealed one is cached and the scan repeats:
 *  same tile as before); round 1 builds while R1_BUILD_LEFT remain. false = c_eco3. */
public static final boolean SPAWN_TWO_STEP = false;
public static final int R1_BUILD_LEFT = 4500;
```

`HQ.java:75`:
```java
int keep = 7000;
if (C.SPAWN_TWO_STEP && G.round == 1) keep = C.R1_BUILD_LEFT;
for (guard = 0; guard < 6 && rc.isActionReady() && Clock.getBytecodesLeft() > keep; guard++) {
```

`HQ.java:208-216`: keep the existing loop as the `else` branch, and add before it:
```java
MapLocation best = null;
if (C.SPAWN_TWO_STEP && C.SPAWN_POCKET != 0) {
    for (;;) {                                   // each pass caches one more sealed tile, or builds
        long bd = Long.MAX_VALUE; int bi = -1;
        for (int i = spawnTiles.length; --i >= 0; ) {
            if (Clock.getBytecodesLeft() < 3500) break;
            if (pocket != null && pocket[i] == 2) continue;
            MapLocation l = spawnTiles[i];
            if (!rc.canBuildRobot(t, l)) continue;
            long d = tileThreat(i) * 100_000L + l.distanceSquaredTo(goal);
            if (d < bd) { bd = d; bi = i; }
        }
        if (bi < 0) break;
        if (!sealed(bi)) { best = spawnTiles[bi]; break; }
    }
} else { long bd = Long.MAX_VALUE; /* existing loop unchanged */ }
```

The old loop already picked the nearest buildable tile that is not sealed, with ties to the first tile in its scan, so this picks the same tile.

**Prototype (scratch only, round 1, seed 1600199891).**
- Two-step alone: B HQs went from 1-4 to 5 on most maps tested. One A HQ on LookingGlass fell from 5 to 4.
- Two-step plus `R1_BUILD_LEFT=4500`: every HQ built 5 on all 37 maps tested, except one Squares A HQ (4, stopped for a reason other than bytecodes).
- The largest HQ round-1 total was 16,629 bytecodes against the 20,000 limit.

**Verification plan.**
1. Run `tools/unit-tests.sh`.
2. Build `tools/param.py make c_kx0 c_r1a AD_PRESS_MN=true GATE_DEFICIT_UNTIL=800 SPAWN_POCKET=4 SPAWN_TWO_STEP=true`. Check that the same build with the switch false reproduces c_gd1's map-seed games (same winner and round on about 13 maps); the false setting adds 2 bytecodes per HQ turn.
3. Run round 1 on all 103 maps: zero HQs short on either side, and zero overruns on rounds 1-3.
4. Run a VM head-to-head, c_r1a vs c_gd1: 103 maps × A/B × 2 explicit seeds, the same seed on both sides, 412 games. Use the first two seeds per map from `side-id-cells.txt`, so the side-id run's c_gd1 vs c_gd1 games serve as the identity reference.
5. Targeted check on the 18 maps where c_gd1's B HQs are at least 3 units short (BatSignal, Cat, DefaultMap, FishCake, Frog, IslandHopping, LightWork, LookingGlass, Movepls, Piglets, Resign, Scatter, Snowflake, Sus, Tacocat, TreasureMap, Turtle, VeryReasonable). If the cliff costs games, c_r1a as A (facing a short c_gd1-B) should beat c_r1a as B by at least 8 of 36.

**What would justify a panel trial.**
- A standalone trial needs at least 221/412 (+1.5 SD), the targeted gap of at least 8 of 36, and zero overruns.
- If the result is within ±1 SD, do not trial it alone; stack it on the next panel candidate as a basics fix.
- At 190/412 or below, drop it and investigate.

**Could not establish:** the mechanism behind the remaining panel gap; why one lane favours one side on Grievance and TicTacToe; and how much each smaller tie-break site (direction order, map centres, spawn ties, sensing order) contributes. AllElements was not tested.

The driver's load average reached 4.6 while I ran my one sequential game at a time, from other processes. I did not touch the VM, launched no jobs, and changed nothing in the repo.

Files are in /tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/side/merge/:
- sim.py, sim2.py (siege-target simulation)
- src/c_gdw (two-step only)
- srcv/c_gdv (two-step plus round-1 limit)
- r1w.txt, r1v.txt, r1v2.txt (round-1 build results)

## Investigation: mechanics

The per-map side bias does not come from the maps, and move order explains almost none of it. It comes from our own bot. Most of it is luck in the robot IDs fixed by each map's seed. The rest is code that does not behave the same when the map is mirrored.

(1) All 103 maps are exactly symmetric. MapCensus sym_all is never NONE. My per-team check (scratchpad/side/mapfeats.csv, via MapDump.java) found 0 maps with any A/B difference in: path distance to the nearest Mn/Ad/Ex well or island, island-distance sums, islands nearer each team, or clouds/currents/walls/wells within r²34 of the HQs. The lowest map-file HQ ID moves first: team B on 59 maps, team A on 44.

(2) Pooled self-play (12,438 games, 142 runs, A 48.6%): the first mover wins 52.8%. On a per-map basis, first mover explains about 4% of the between-map variance beyond binomial noise (A-first maps average 0.519 A share, B-first 0.430; permutation p=0.049). On the 51 maps with p<0.001, the favoured side is the first mover on only 33.

(3) The bias is a fixed-seed effect. With the map seed (6,653 games), between-map variance beyond noise is 0.083; with random seeds (1,030 games) it is 0.0095, about 9x smaller. Per-map shares under the two correlate only 0.19. In paired cells (the same two builds, one game per side), the same side won both games in 75.8% of 3,275 map-seed cells and 76.6% of 1,942 fixed-seed cells, but 52.6% of 515 random-seed cells (50% means no side effect). Other fixed seeds give different, uncorrelated per-map biases.

(4) Identical bots: c_gp1 vs itself on map seeds (run 20261017-101854-self-all), the first mover won 59/103. Its winner matched the pooled favoured side on 92/103 maps, so each map's pooled count is essentially one deterministic game replayed by near-identical builds. My VM run gauntlet/20261020-173606-side-id (c_gd1 vs c_gd1, 199 games, no failed games): the first mover won 90/183 random-seed games (49.2%). The 16 map-seed games matched the local runs exactly (same winner and round on 13 of 13).

(5) Causal test (local, 26 games on 13 extreme maps): I gave every HQ the ID of its mirror image, which swaps who moves first and which IDs each team draws. Geometry, teams and seed stayed the same. A rewritten but unswapped Risk reproduced the original (B, round 574). The first mover won 14/26. The winner followed the IDs on 7 maps (Risk, Heart, Squares, Spiral, ArtistRendition, maptestsmall, SomethingFishy). On those maps random seeds erase the bias: the map-seed winner side took 19/42 games, and Risk and Heart reverse to A 5:1. The winner stayed with its map position on 6 maps (Diagonal, Rectangle, Sneaky, TicTacToe, Tightrope, SmallElements). On those the bias survives random seeds: 29/36, with Diagonal 6:0 and TicTacToe 0:6; Grievance, not swap-tested, is also 6:0. No swapped game repeated its original's round count, so c_gd1 is not symmetric under the map's mirror or rotation.

(6) Field: c_gd1 on panel v2 (us A) and v2b (us B) won 59 vs 49. Of 22 cells won on one side only, A took 16 (sign test p≈0.05). The side we won on matched the self-play favoured side in 13/22 and the first mover in 11/22. Correlation with the self-play per-map share is 0.18 (permutation p=0.076). A beat B in every self-play-bias band: 20-19 on B-favoured maps, 18-16 neutral, 21-14 A-favoured. Across 468 (opponent, map) cells of replica history played on both sides (8,096 games, all builds): A minus B +1.3±2.0 pp, moving first minus second −1.7±2.0 pp, self-play favoured side minus the other −0.3±2.0 pp.

Conclusion: move order is negligible. About half of the extreme-map bias is luck in the seed-fixed robot IDs, which our code uses for decisions. The other half sticks to map position and survives new seeds and swapped IDs, so it comes from code that is not invariant under the map's symmetry. The self-play bias does not carry over to the field, and the panel A/B gap is borderline and unexplained by map bias.

Scratch files are in /tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/side/: mapfeats.csv, perMap_selfplay.csv, vm_results.csv, exp_results.txt (swap test), sideid_full.csv (VM run), mapdump/MapSwap.java, maps_swap/. VM leftovers: build/side-id (c_gd1 classes), /tmp/side-id-cells.txt, logs/side-id.log and logs/side-id2.log. My first job (side-id) was stopped by tools/vm-stop.sh during its compile, before it played any game, and restarted as side-id2. se-h2h was not touched. Nothing under src/, test/, tools/ or docs was changed and nothing was committed.

Causes:

- **Seed-fixed robot-ID luck. All spawned robots draw IDs from one shared generator seeded by the map seed (shuffled blocks; the first-moving HQ draws first). c_gd1 makes many decisions from its own ID, so with the map seed each team's mix of roles and wall-following hands is fixed for each map and side. Our c_* builds share this code, so the same side gets the same luck across builds.** (high; bot side-dependent: True). Evidence: c_gd1 has no Random, Math.random or hash collections (grep), and RULES.md:19 says a GAME_SEED changes only spawned-robot IDs. So any seed effect must act through ID-based code: Nav.java:26 left=(G.id&1)==0; Carrier.java:173,175 Ad role by id%AD_LATE_EVERY / id%AD_EARLY_EVERY; Carrier.java:917 scout id%SCOUT_EVERY; Carrier.java:1024 odd-id prober; Launcher.java:757,800 lowest-ID leader; Launcher.java:935 even-id island threat; (round+id)%k scans at Carrier.java:55, Launcher.java:51, Amplifier.java:14, RobotPlayer.java:64. Same side won both games of a paired cell: 75.8% with the map seed (n=3,275) vs 52.6% with random seeds (n=515). Excess between-map variance 0.083 vs 0.0095. ID-swap test: winner follows the IDs on 7/13 maps, and on those random seeds give the map-seed winner side only 19/42 (Risk and Heart reverse to A 5:1). Fix idea: Stop basing decisions on raw ID parity or modulo. Use a per-team spawn counter (the HQ writes a build index to the shared array and the new robot reads it), or geometry, for roles, scouts, squads and wall-following hand (for example, try both hands or pick the one toward the target). Use random seeds, not only the map seed, when measuring builds.
- **Seed-independent bias tied to map position: our code does not act the same when the map is mirrored or rotated, so on some maps one physical side wins whatever the seed or IDs.** (medium; bot side-dependent: True). Evidence: On 6 of 13 maps the winner stayed with its position when the HQ IDs (and so move order and ID draws) were swapped: Diagonal, Rectangle, Sneaky, TicTacToe, Tightrope, SmallElements. On those maps random seeds keep the map-seed winner side 29/36 (Diagonal 6:0, TicTacToe 0:6, Rectangle 5:1, Sneaky 5:1); Grievance is 6:0 though not swap-tested. Maps are exactly symmetric (0 per-team feature differences on 103 maps), and no swapped game repeated its original's round count. Candidate sources: fixed direction order N,NE,E,SE,... in G.java:39-42 used for tie-breaks; engine sensing results come in column-major order (RULES.md:386-388); wall-following hand by ID parity is not mirror-invariant on HORI/VERT maps. Identity random-seed games: A won 100/183 (54.6%, mild; A is on the west on 82 maps). Fix idea: Make tie-breaks symmetric: order candidates by distance to the target or the enemy, rotate the direction list by a geometry-based start, and do not rely on the order of sense results. Check by replaying a map with mirrored HQ IDs (scratchpad/side/mapdump/MapSwap.java) and checking the game comes out as an exact mirror (same round count).
- **Engine move order (the lowest map-file HQ ID acts first every round): a real but negligible effect.** (high; bot side-dependent: False). Evidence: Identical bots on random seeds: first mover won 90/183 (49.2%). ID-swap test: 14/26. Identical c_gp1 on map seeds: 59/103 (p≈0.17). Pooled self-play: 52.8% of games but 49.1% on non-map seeds (n=5,765). Explains about 4% of the between-map variance (p=0.049). Spiral and Grievance are won by the second mover. Against the field, moving first minus second −1.7±2.0 pp over 468 paired replica cells. Fix idea: None needed. Do not tune for move order.
- **The panel A/B gap (59 vs 49) does not follow the self-play map bias. It looks like noise from single deterministic, chaotic games per cell, not a systematic weakness on side B.** (medium; bot side-dependent: False). Evidence: 22 cells won on one side only, 16 as A (two-sided sign p≈0.05). Matches the self-play favoured side 13/22 and the first mover 11/22. Correlation with self-play share 0.18 (permutation p=0.076). A beat B in every bias band (20-19, 18-16, 21-14). Replica history, 468 paired cells: A minus B +1.3±2.0 pp, self-play favoured side minus the other −0.3±2.0 pp. LEARNINGS.md:118-120: switches that do nothing still flip 0-9 of 80 deterministic cells. Fix idea: Read single-game panel A/B differences as noise. If side B matters, replay the 22 discordant cells with ID-independent role and nav code, or compare with a v3 mixed-side panel.

Open questions:

- Which ID-based decision carries most of the seed luck: wall-following hand (Nav.java:26), carrier Ad/Mn role (Carrier.java:173-175), or squad and leader selection? One test: a param build with a seed-independent hand or role, run on a few map seeds.
- Which mirror-asymmetric code makes Diagonal, Grievance, TicTacToe, Rectangle and Sneaky depend on position: G.DIRS tie-break order, column-major sensing order, or an engine order such as currents or end-of-round processing? Not established.
- Grievance, AllElements and BuildSite were not in the ID-swap test.
- The mild A edge in identical-bot random-seed games (100/183) may be a west-side effect (A is west on 82 maps); not significant and not tested.
- Ranked ladder games could not be separated from panels and scrimmages in matches/*/extract/games.csv, so the raw replica A 0.590 (n=6,826) vs B 0.504 (n=1,270) is confounded by design (panel v1 was all side A). Only the 468 paired cells were used.

## Investigation: replays

Short version: move order is not what decides the winner. Our own code is. The games that stay biased even with random seeds come from one part of our code making a different choice for each side. The extreme per-map counts mostly come from the map's fixed seed, which fixes the ID draw and replays the same game many times.

(1) The pooled counts over-state the bias. 6,773 of the 12,438 self-play games use the map's own seed, so spawned IDs are fixed and the game is deterministic. 4,274 of those games share their exact (map, winner, rounds) with another game: on Risk, 34 of 53 are the same B win at r407; on Sneaky, 29 of 53 are the same A win at r362. With random seeds (5,665 games) the bias is much smaller: Risk 2-14, Heart 4-6, BuildSite 5-5, Rectangle 4-6, SomethingFishy 4-6. A chi²/df test of per-map side bias gives 5.4 with random seeds against 22.6 with map seeds.

(2) Move order is not the driver. With random seeds the team that moves first wins 48.8%. On the c_gd1 panel, cells won when moving first and second are 54 and 54 (11 discordant each way). I built Grievance with the HQ IDs swapped, so A moves first: A still won 7 of 7 (map seed and seeds 1-6). The unchanged copy reproduces the original game exactly (A at r589).

(3) Grievance (A 6 of 7 for c_gd1 over map, 1, 2, 3, 5, 6, with B winning seed 4). In seed 2 the two economies are the same until r70 (Mn collected 319 vs 311). The decisive split is the army's target in Launcher.siegeTarget. It aims at the enemy HQ nearest our HQ centroid, but the centroid is rounded down (Launcher.java:509), and ties go to the lower x, then lower y (Launcher.java:473). So A, with HQs at (0,0) and (0,59), gets centroid (0,29) and targets (59,0). B, with HQs at (59,59) and (59,0), gets (59,29) and targets (0,0); the mirror of A's choice would be (0,59). Both armies therefore march down the same bottom lane: from r35 to r60, A's launchers sit at y≈20-26 in A's frame and B's mirrored at y≈33-35, in all three seeds checked. Two tests confirm it:
- A copy of c_gd1 with the centroid rounded up (no other change) swaps the routes: A now at y≈32-37, B at y≈20. B then wins 5 of 6 (seeds 1-5; A only at the map seed).
- Grievance mirrored top-to-bottom (same HQ squares, IDs and move order) also flips the result: B wins 3 of 4.

The same rounding test flipped TicTacToe (base B 5/5, rounded-up A 6/6) and Sneaky (base A 4/5, rounded-up B 5/6), and partly SmallElements (base B 5/5, rounded-up B 4/6). This target mismatch exists on 15 maps once the symmetry is known, and 21 if you count the rounds before it is. But those maps are not more biased under random seeds than the others (chi²/df 5.5 vs 5.8 for other multi-HQ maps and 4.0 for one-HQ maps). So it explains specific maps, not the whole pattern.

(4) Risk (one HQ per side) is about the IDs, not the layout. With random seeds c_gd1 goes A 5, B 3; with the HQ IDs swapped, A 7, B 1. At the map seed, the first mirror difference is at r4: A's third carrier #10752 has id%8==0, so it takes the adamantium role (Carrier.java:175) and mines Ad from r6, while B's matching carrier #12991 mines Mn. At r7 the first launcher to differ is B's #12929, its only odd-ID early launcher. Wall-following side comes from ID parity (Nav.java:26), and on a mirrored map a left-hand follower's mirror image is a right-hand follower. By r100 A has C0 L1 against B's C5 L4. In seed 1 it was B that drew the early Ad carrier, and B lost.

(5) The first difference of all comes at round 1 on Grievance. When two spawn squares are equally good, the HQ (HQ.java:208-212) keeps whichever comes first in the engine's fixed tile order, so A's 4th launcher appears at (3,0) while B's appears at (59,56), not the mirror (56,59). Whether this changes outcomes was not measured.

(6) On the panel, the 59 vs 49 gap (A vs B) is concentrated on one-HQ maps: 14 vs 8 of 26 cells. On maps with the mismatched target it is 9 vs 7 of 14, and on other multi-HQ maps 36 vs 34 of 60. Neither move order nor the target choice explains it; that is not established.

Files are in /tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/side/watch/:
- results.txt and results2.txt: the VM runs.
- siege.csv: each team's target on all 103 maps.
- hqs.csv: HQ IDs and positions.
- py/mirror.py, py/army.py, py/board.py, py/siege.py: the analysis scripts.
- vsrc/c_gd1: the rounded-up variant (one changed line).
Map variants are in ../maps and ../mapvar/src/MapVariant.java; local replays in ../games.

A note on the driver: a sibling agent was also running games on the driver. When I noticed, I stopped my local loop and moved my runs to the VM in two detached jobs, run one after the other (side-watch and side-watch2, both finished). Their replays on the VM have been deleted. Nothing in src/, tools/ or docs was changed and nothing was committed.

Causes:

- **Launcher.siegeTarget picks the army's enemy HQ with a rule fixed to map coordinates: the HQ-centroid is rounded down (Launcher.java:509, x/o.length), and ties go to the lower x, then lower y (Launcher.java:473, G.enc). On maps with several HQs this gives the two teams non-mirror targets, so both armies march down the same lane. Whichever team's own route favours it wins, every seed.** (high; bot side-dependent: True). Evidence: Grievance: A targets (59,0), B targets (0,0); B's mirror choice would be (0,59). From r35 to r60 A's launchers are at y≈20-26 in A's frame and B's mirrored at y≈33-35, in seeds map, 1 and 2. c_gd1 on Grievance: A wins 6 of 7. Rounding the centroid up (the only change) swaps the routes (A y≈32-37, B y≈20) and B wins 5 of 6. Grievance mirrored top-to-bottom: B 3 of 4. TicTacToe: base B 5/5, rounded-up A 6/6. Sneaky: base A 4/5, rounded-up B 5/6. SmallElements: base B 5/5, rounded-up B 4/6 (partial). 15 of 103 maps (21 counting the rounds before symmetry is known) have mismatched targets (watch/siege.csv). Fix idea: Make the target choice mirror-symmetric: compute the centroid exactly (doubled coordinates) and break ties relative to our own HQs (for example, the enemy HQ that mirrors a chosen own HQ under the known symmetry), not by map x/y. Better still, choose the lane on merit, since on these maps the lane decides the game: try both lanes per map in self-play or on the panel.
- **Unit roles and wall-following side are keyed on robot ID: Ad carrier id%8==0 (Carrier.java:175), wall-following side id&1 (Nav.java:26), the MID squad id%3, the island branch id&1, and each unit's random stream seeded from its ID (G.java:58). At the map's own seed, spawned IDs are fixed per map and side, so each map deals a fixed draw per side. On mirrored (reflection) maps, same-parity wall-following is not even the mirror image.** (medium; bot side-dependent: True). Evidence: Risk at the map seed: the first mirror difference is r4, when A's carrier #10752 (id%8==0) mines Ad from r6 and B's matching carrier #12991 mines Mn. At r7 the first launcher to differ is B's #12929, its only odd-ID early launcher. A is wiped by r100 (C0 L1 vs B C5 L4). Seed 1 reverses who has the Ad carrier, and B loses. With random seeds c_gd1 on Risk goes A 5, B 3. Random seeds remove most of the extreme per-map counts: Heart 4-6, BuildSite 5-5, Rectangle 4-6, SomethingFishy 4-6, against 49-4 to 1-52 at the map seed. Fix idea: Derive roles and wall-following side from the HQ's build counter, not the engine ID, and make the side a function of the map symmetry (left for A matches right for B on mirrored maps). Both sides then get the same role sequence regardless of how IDs interleave; this also removes the map-seed lottery on the replica.
- **Measurement artifact: map-seed self-play games are deterministic, so near-identical builds replay the same game. The pooled per-map counts are not independent samples.** (high; bot side-dependent: False). Evidence: 4,274 of 6,773 map-seed self-play games share their exact (map, winner, rounds) with another game. Risk: 34 of 53 map-seed games are the same B win at r407. Sneaky: 29 of 53 are the same A win at r362. Per-map side bias chi²/df is 22.6 with map seeds against 5.4 with random seeds. Fix idea: Judge side bias, and run h2h sweeps, with random GAME_SEEDs (or several per cell); report map-seed results as single deterministic games.
- **Move order (the engine runs the lowest-ID HQ, and the units spawned after it, first) is not a material cause.** (high; bot side-dependent: False). Evidence: With random seeds the first mover wins 48.8% (2,763 of 5,665). On the c_gd1 panel, cells won moving first vs second are 54 vs 54 (11 discordant each way). Grievance with HQ IDs swapped (A moves first): A 7 of 7, the same as the original. The unchanged copy reproduces the original game exactly (A at r589). Fix idea: None needed.
- **When two spawn squares are equally good, the HQ (HQ.java:208-212, strict < in the engine's fixed tile order) picks a square set by map coordinates, so the two sides' opening spawns are not mirror images.** (low; bot side-dependent: True). Evidence: Round 1 on Grievance, every seed: A's 4th launcher appears at (3,0) while B's appears at (59,56), not the mirror (56,59). The A and B carriers also differ ((0,3) vs mirror (0,2)). This is the first mirror difference in every Grievance game, but its effect on the outcome was not isolated. Fix idea: Break spawn-square ties by a rule relative to the map symmetry (or toward the map centre), not by the engine's tile order.

Open questions:

- Why does the shared lane on Grievance favour the team marching east along the bottom from (0,0), and on TicTacToe the team marching toward the high-x, low-y side? The terrain on the two routes differs (currents, clouds, wells), but which feature decides the first fights (r51-60) was not established.
- Many maps stay side-biased with random seeds without a mismatched siege target: Hah 105-269, Maze 291-127, Sine 29-3, Sun 4-22, Spiderweb 3-23, Checkmate2 20-6. Other coordinate-fixed tie-breaks are untested: the fixed direction order (G.DIRS) in movement and micro, island-ID order, well choice and Mid.site.
- The panel gap (c_gd1 as A 59/100, as B 49/100) sits mostly on one-HQ maps (14 vs 8 of 26). It is not explained by move order (54 vs 54) or the siege target. The replica uses the map's own seed, so the ID draw may matter, but opponent spawns interleave with ours; this needs the panel replays.
- Rounding the centroid up only swaps which side gets the good lane; it is not a fix. Whether a symmetric or merit-based lane choice improves results against field bots is unknown.
- VM battlecode-dev root disk was at 99% (299 MB free) at 18:20 PDT, from other jobs; my side-watch replays were deleted.

## Investigation: code

The per-map side bias has two sources. Most of the large per-map tallies in the pooled data are a sampling artifact. On top of that, the bot is genuinely not mirror-invariant, and that produces real position effects on some maps. 7,185 of the 12,850 pooled rows used the fixed seed 'map'. A game is deterministic given (map, seed, build), so near-identical builds replay the same game (Risk 0-57 on the map seed). In paired cells the same side won both games 4,106 times against 1,317 for the same build. Counting each (map, seed) once on other seeds gives A 580 vs B 654 (47.0%), with modest heterogeneity (chi2 162 on 103 df). The replica panel also ran on seed 'map'. I tested this with a transform experiment on the VM (run 20261020-183122-side-xform, c_gd1, 8 maps x 6 seeds x FX/FY/ROT/SW, 198 games, started 11:31 PDT). It changed each map's absolute orientation while keeping HQ IDs and turn order. The map's own symmetry reproduced the HQ-ID-swap game with the labels swapped, at the same round, in 48/48 pairs. So the harness is correct and the A/B label itself has zero effect. Even so, 144/144 FX/FY/ROT games diverged from the identity game at the same seed, and the winner flipped in 75 of them (52%). Swapping turn order kept the winner in 31/48. The winner follows absolute orientation and position: Diagonal's west HQ won 30/30, Jail's east HQ 25/30, Rectangle's west 21/30. On Grievance A won 12/12 in the identity and FX orientations but 4/12 in FY and ROT. Squares is the exception: there the first mover won 25/30. A new c_gd1-specific asymmetry is the HQ's round-1 bytecode cliff. Across all 103 maps, HQs in the east half built fewer than 5 units on round 1 in 94/187 cases, against 52/199 in the west half; A out-built B on round 1 on 48 maps and B out-built A on 11. Its effect on results is only suggestive (side-id A 59.5% when A out-builds, 35.3% when B does, 53.1% when equal; c_gd1 self-play A 108/199 = 54.3%). Two local ablations isolated the strongest cause on Diagonal: the siege-target tie-break plus the floored centroid (Launcher.java:706 and :742). With canonical per-team tie-breaking (scratch build c_gdy), Diagonal's west wins dropped from 24/24 to 13/24, and on the VM (run 20261020-193331-side-abl) Grievance went to A 10/24 with identity A 2/6, against c_gd1's 16/24 and 6/6. Turning SPAWN_POCKET off (c_gdz) did not remove Diagonal's west dominance: 11/11 west wins before I stopped that run. The repo is untouched. All scratch work is in /tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/side/ (xform/MapXform.java and xform/maps, sym/r1all.txt, r1final.json, abl/src/c_gdy, abl/results.txt, vm-side-xform/results.csv, vm-side-abl/results.csv, siege.py).

Causes:

- **Evaluation artifact: most pooled games use the fixed per-map seed 'map', so each map's tally is mostly one deterministic game repeated across near-identical builds, not many independent samples.** (high; bot side-dependent: False). Evidence: 7,185 of 12,850 pooled rows used seed 'map'. 74.7% of map-seed games went to that map's majority side. Paired cells: same side won both 4,106 vs same build won both 1,317. Several maps reverse between the map seed and other seeds (AbsoluteW 0-57 vs 19-7, Pizza 55-2 vs 6-20, maptestsmall 60-3 vs 6-10, SomethingFishy 54-3 vs 4-6). Seed-level count: A 580 vs B 654 (47.0%), chi2 162/103. The B-favoured list largely vanished on explicit seeds for c_gd1 (Risk A 5/6, Heart A 5/6). The replica panel v2/v2b results.csv also shows seed 'map'. Fix idea: Run every local and replica cell on several explicit seeds with both sides at the same seed, and count per (map, seed). Add a mirror regression panel built with MapXform (the 8 maps x FX/FY/ROT, 1-2 seeds): measure the winner-flip rate and round discordance against identity. c_gd1 baseline: 144/144 diverged, 52% flipped. The T=S vs SW consistency (48/48) serves as the harness check.
- **The siege target is not mirror-equivariant: ties go to the lower x, then y (Launcher.java:706, G.enc(ehq[i]) < G.enc(ehq[bi])), and the 'our centroid' it measures from is floored (Launcher.java:742). The two teams therefore march to targets that are not mirror images of each other. The same target feeds campSymOf (Launcher.java:1330) and pickObjective distances (1194/1208/1258).** (high; bot side-dependent: True). Evidence: Simulated on all 103 maps: targets are non-equivariant on 23 maps at game start (all three symmetry candidates alive) and 16 once the symmetry is decided. Diagonal at start: both teams target (4,35). TicTacToe: both centroids floor to x=14 (true 14.5), so both armies attack the west HQs. Grievance: A targets B4 (59,0) and B targets A3 (0,0); the mirror would be A5 (0,59). Grievance outcome follows this pairing: A wins 12/12 in identity and FX, 4/12 in FY and ROT, where the pairing becomes A->B2, B->A5. Per-map heterogeneity is higher on these maps: pooled seed-level chi2/df 2.44 (16 maps) and 1.91 (7) vs 1.37 (80 equivariant); c_gd1 side-id 2.20/2.00 vs 1.05. 7 of the 8 A-favoured listed maps vs 2 of the 8 B-favoured fall in this class. Ablation c_gdy (canonical frame tie and canonical centroid only): Diagonal west wins 13/24 vs 24/24 for c_gd1 (local runs, same seeds); Grievance A 10/24 vs 16/24, identity 2/6 vs 6/6 (VM). Fix idea: Give each team a canonical frame: the transform f among {id, FX, FY, ROT} that makes its own sorted HQ list lexicographically smallest. The enemy's HQs are S(ours), so its frame is S∘f and every rule becomes equivariant. Break location ties by fenc(l) = enc(f(l)) and compute centroids with a floor in canonical coordinates, then map back. The centroid-sign frame used in c_gdy fails when a team's centroid sits on a centre line (TicTacToe x, Grievance y). Check strength before adopting: c_gdy turned 10/24 Grievance games into 2000-round tiebreak games vs 1/30 for c_gd1.
- **The HQ round-1 bytecode cliff depends on orientation (c_gd1 and the other SPAWN_POCKET=4 builds). The build loop needs more than 7,000 bytecodes left (HQ.java:73). tryBuild scans spawnTiles in descending engine x-major order with a strict '<' (HQ.java:210-215) toward the floored (W/2,H/2) (HQ.java:205/207) and runs the sealed() flood fill (HQ.java:226-250) for each new best tile. East HQs hit more improvements, so more fills.** (medium; bot side-dependent: True). Evidence: From an instrumented scratch copy (c_gdx), all 103 maps, seed 1600199891: round-1 builds range 1-5 per HQ. Short (<5) in 94/187 east-half HQs vs 52/199 west-half; B HQs short 91/194 vs A 56/194; A out-built B on 48 maps, B out-built A on 11, equal on 44. Examples: BatSignal B first iteration 9,830 bytecodes, 16 fills, 2 builds. RiskFX A 7,266 bytecodes, 11 fills, 3 builds vs 5 in the identity game (replay indicator 'b' = bytecode stop). Identity Risk A had a 121-bytecode margin on its 5th build. Outcome link is suggestive only: side-id A 59.5% (84 games) when A out-builds, 35.3% (17) when B does, 53.1% (98) when equal. Map-level permutation p=0.027 (A-more vs equal), but r(diff, A share)=0.03. Pocket builds against non-pocket builds won 41.9% as B vs 51.1% as A (272 games each). Panel cells won only on one side: 8 vs 2 on A-out-builds maps. Ablation c_gdz (SPAWN_POCKET=0) still had west 11/11 on Diagonal, so this cliff is not the Diagonal cause. Fix idea: Choose the spawn tile in two steps: first the argmin of (threat, dist2, canonical fenc) over buildable tiles, independent of scan order; then run sealed() only on that tile, re-picking if it is sealed. Alternatively precompute pocket[] for every spawn tile once in a fixed order. Relax the 7,000 guard on round 1 so every HQ builds its full batch regardless of orientation.
- **Floored centres and default goals favour high-x/high-y positions: new MapLocation(G.W/2, G.H/2) at HQ.java:205/207, Carrier.java:717 and Launcher.java:1269; Mid centre floor at Mid.java:65 with the tie 'e < best' at Mid.java:80; Amplifier.java:35/39; rally centroid at Launcher.java:513; camp-home tie at Launcher.java:1307.** (medium; bot side-dependent: True). Evidence: On even-sized maps (W/2, H/2) is half a tile toward the high-x/high-y team (Risk 20x20: (10,10) vs the true (9.5,9.5)); on round 1 it is the launcher goal for every HQ, because ourHQs is not yet registered. Jail: the east HQ, nearer (10,15), won 25/30 across all orientations. Risk: the north HQ won 16/18 with HQs on the west edge but 5/12 on the east edge, so this rounding cannot be the only cause. Not ablated on its own. Fix idea: Compute every centre, centroid and default goal in the team's canonical frame (floor there, map back), e.g. centre = f^-1(((W-1)/2, (H-1)/2)). Replace 'e < best' and the other coordinate ties with fenc.
- **Direction tie-breaks use a fixed absolute order. Nav field descent (Nav.java:127-141, loop i=7..0 with strict '<') resolves ties NW, W, SW, S, SE, E, NE, N; moveAway (Nav.java:269-275, strict '>') does the same. fight() (Launcher.java:523-590) uses integer scores plus G.rand(3) noise with strict '>', so residual ties go to CENTER, then N, NE, E, and so on. midHold (Launcher.java:782), packPick (Carrier.java:642-652) and the sealed() neighbour order (HQ.java:237) are similar.** (medium; bot side-dependent: True). Evidence: Shown non-invariant overall: identity Risk at seed 1600199891 and RiskFX already differ at round 1 (spawn tiles (3,3) vs (16,3)/(17,4)), and no transformed game reproduced its identity round (0/144). The individual contribution of each site was not measured. Fix idea: Iterate a frame-mapped direction table, FDIRS[i] = f(DIRS[i]), wherever a loop picks a best direction with strict comparisons, so ties resolve the same way relative to each team's own corner. Keep Nav's ID-parity handedness, which is random by ID and so has no side bias in expectation.
- **Engine iteration order is x-major (GameWorld.getAllLocationsWithinRadiusSquaredWithoutMap, GameWorld.java:462-476: x outer, y inner), and senseNearbyRobots/MapInfos/Wells inherit it. Scans with strict min/max and budgeted processing therefore depend on orientation: MapMem.process (MapMem.java:115-138) consumes pending tiles from the end of the array under a bytecode reserve, and the HQ spawn scan has a Clock break (HQ.java:211). The HQ's RNG comes from a map-fixed HQ ID (G.java:58, rng = id*7919+13), so G.nearest ties (G.java:154, used at HQ.java:205) are decided by a constant per-map, per-side coin.** (low; bot side-dependent: True). Evidence: Code reading plus engine source. HQ IDs come from the map file (Grievance B2, A3, B4, A5 at every seed), so the HQ's random ties do not average out over seeds. The share of the measured bias due to these sites was not separated. Fix idea: Add fenc as a secondary key in strict-comparison scans over sensed objects. Replace the random tie in G.nearest with fenc (or seed the HQ RNG from a frame-invariant quantity). Process pending map tiles in canonical order, or accept the timing noise and drop the RNG and ID dependence only where a choice is made.
- **Turn order: the first mover is the lowest map-file HQ ID. This is an engine and map property, decisive only where HQs are close.** (medium; bot side-dependent: False). Evidence: Squares (adjacent central HQs, B2@21,20 vs A3@18,19, dist2 10): the first mover won 25/30 across all orientations and both ID assignments. Elsewhere, swapping HQ IDs kept the winner in 31/48 (Risk SW: A 6/6 with A moving first, A 5/6 with A moving second). Fix idea: Nothing to make invariant. If Squares-type maps matter, the second mover could hold spawns out of the enemy's first-turn reach (SPAWN_SAFETY already scores threats once enemies are seen).
- **Ruled out: team identity (rc.getTeam, Team.A/B) and shared-array slot ownership.** (high; bot side-dependent: False). Evidence: The team is used only as us/them (G.java:49-50); each team has its own shared array. The map-symmetry transform equals the ID swap with labels swapped in 48/48 pairs (identical rounds), so the A/B label has no effect anywhere in the bot or engine. HQ index roles (registration order = map ID order) pair mirror partners on all 8 maps checked. Fix idea: None needed.

Open questions:

- Does the siege-target fix cost strength? c_gdy turned 10/24 Grievance games into 2000-round tiebreak games; it needs a local panel and side-mixed replica test before adoption.
- What remains after the siege fix? c_gdy on Diagonal still never reproduced a mirrored round, and B (the second mover) won 17/24. The per-site share of the direction, floor and engine-order sites is unmeasured; a full canonical-frame build checked on the MapXform panel would answer this.
- The c_gdz (SPAWN_POCKET=0) Diagonal ablation was stopped at 11/24 games (all west wins). TicTacToe was not ablated, because the centroid-sign frame is degenerate there (both team centroids at x=14.5).
- The round-1 cliff's effect on results is only suggestive (permutation p=0.027, but no dose-response). The panel's one-side-only cells, 16 vs 6 (sign test p=0.052), also ran on the fixed map seed, and the field bots' own side dependence is unknown.
- Not explained: why Risk's north advantage (16/18 with HQs on the west edge) disappears with HQs on the east edge (5/12), and what causes the B tilt of older non-pocket builds (48.2%, z=-3.9; reflection maps 44%).
