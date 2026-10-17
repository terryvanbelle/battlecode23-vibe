# Panel loss mechanisms for c_hr1: merge, verification, ranking and plans

The two plans to build:
1. **Defend against island conquest (`c_isle1`).** Low risk, about +1.2 games net.
2. **Drop a home well after a second flight (`c_drop1`).** It addresses the cause behind most losses, but it is the riskier change, at about +0.5 to +1 net.

Panel run: `/home/terryvanbelle/projects/vibe/2023/gauntlet/20261017-212413-panel-c_hr1`. `results.csv` shows **72 wins and 28 losses**, not 71/29.

The analysis scripts are in `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag/verify/` (`lib.py`, `a1`–`a4`, `b1`–`b2`, `c1`–`c2`, `d1`–`d2`, `e1`–`e8`, `f1` `.py`). The code read is in `/home/terryvanbelle/projects/vibe/2023/src/c_hr1/`: `Carrier.java`, `Launcher.java`, `HQ.java`, `C.java`, `Comms.java`, `MapMem.java`, `Telemetry.java`.

**How the losses happen** (the timeline data behind the ranking):
- **Carriers die first.** Our carrier deaths by round 200 are 8.9 a game in losses and 2.9 in wins. Carrier builds are nearly the same (21.7 vs 22.5), so the difference is deaths, not production.
- **The deaths are at home.** Our carrier deaths near home before round 300 are 12.57 a game in losses and 3.28 in wins. 22 of 28 losses have 6 or more, against 19 of 72 wins.
- **The armies stay level, then split.** At round 200 both sides have built 39.5 vs 40 launchers. The enemy army reaches twice ours in 25 of 28 losses (median round 280), and in only 1 of 72 wins.
- **Islands come last.** By the time the enemy is one or two islands from conquest, our army is level or ahead in only 2 of 26 losses.

So the losses are mostly settled by carriers dying at home wells before round 300. Islands are the final step.

## 1. Merged mechanisms and the distinct losses each explains

| ID | Merged mechanism | Sources | Distinct losses |
|---|---|---|---|
| A | Carriers flee their home well, come back to it and die there; c_well6's hot-well rule covers front wells only | jmerle "flee-and-return loop" (8824 g2,g4,g5,g6,g8); awesome M1 home-well camp (8826 g1,g3,g4,g5,g7,g8); vrangr "home-well carrier feeding" (8823 g1,g4,g6,g8, 8825g2); pran "unanswered economic war" (8827 g3,g6,g7, 8828 g1,g6, 8832g5) | **22** |
| B | Launchers arrive piecemeal, or dribble out of a camped HQ | jmerle dribble (8824 g2,g4,g6); awesome "piecemeal home defence" and "HQ siege lockout" (8826 g1,g3,g4,g5,g7,g8); vrangr "piecemeal openings" (8823 g1,g4,g6,g8); pran "decisive battle piecemeal" and "spawn-camp lock" (8827 g3,g6,g7,g9, 8828 g1,g6, 8832 g2,g5) | 21 (19 of them also in A) |
| C | The army is away while home is raided | jmerle "home raids unanswered" (8824 g2,g4,g5,g6,g8); awesome "single siege target strands the army" (8826 g3,g7) | 7 (all in A) |
| D | The raid ignores enemy wells far from their HQs | jmerle M3 (8824 g2,g4,g6,g8); vrangr "lead not converted" (8823 g0,g4, 8825g2); part of pran's economic war | 7 |
| E1 | Our launchers almost never contest enemy-held islands | vrangr M2 (8823 g0,g8, 8825g2); pran "island deadlock" (8828g9, 8827g0, 8827g9); jmerle "ReverseFunnel island race" (8824g9) | **7** |
| E2 | One pressured HQ, or trailing on islands, stops anchors team-wide | vrangr M3 (8823 g0,g8, 8825g2); pran M2 part (8828g9, 8827g0, 8827g9) | 6 (all in E1) |
| F | The anchor reserve is gated on the cumulative launchers-built count | jmerle M6 (8824 g2,g4,g6,g8); vrangr M5 (8823g6) | 5 |
| G | Too much Ad mined while short of Mn; the any-type well fallback | jmerle M7 (8824 g2,g5,g6,g8); pran M4 (8832g2) | 5 |
| H | Forest: one home Mn well for 3 HQs, switchWell, carrier cap | jmerle M4 (8824g4); vrangr M6 (8823g4) | 2 |
| I | Blind fire into clouds | jmerle (8824 g2,g4) | 2 |
| J | Crowded wells, low Mn per carrier | pran "well crowding" (8827 g7,g9, 8828g9); jmerle M9 (8824g9) | 4 |
| K | Islands and healing amplify their lead | awesome M5 (6 games) | A consequence, not a cause |

## 2. Code verification and CSV spot-checks

### A: home-well feeding. Verified; one sub-claim rejected

**Code:**
- `survive()` (Carrier 191–241) flees but keeps `well`.
- The hot-well mark at line 213 requires `front(well)`, and so do `hotLocal()` (559) and `markHot()`.
- `frontGate()` (499–501: farther than r² 64 from home and at least 36% of the enemy distance squared) excludes every home well.
- So a carrier goes straight back to a raided home well. `gather()` at 337 drops only wells that `hot()` reports.

**Rejected sub-claim (vrangr):** "removing `front()` at 212–213 is enough." It is not. `hotLocal()` and `markHot()` still filter by `front()`, so the home well is never treated as hot, and the cool path measured from home picks the same well. The change does nothing on its own.

**Spot-checks:**
- Loss deaths with a known well before round 300: 152 at home wells, 31 at front wells.
- The same home wells keep killing carriers in losses and none in wins:

  | Map and well | Deaths in losses | Deaths in wins |
  |---|---|---|
  | Cat (20,32) | 10–11 | 0 |
  | Hah (14,11) | 8–16 | 0 |
  | DefaultMap (7,21) | 11 | 0 |

- Our launchers were there. In losses, 328 of 352 home carrier deaths before round 300 happened inside an engagement our launchers were in (median peak 7 vs 7). The carriers walk back into an even fight that is still going on; the army is not absent.
- Carriers fled before dying in both outcomes (91% of losses, 93% of wins). A trigger on the first flight would therefore fire in nearly every win; the trigger has to be a repeat flight.

### B: piecemeal arrival. Rejected as a cause

**Code:**
- pran's "a sighting objective skips regroup" is contradicted: `march()` calls `regroup()` at line 399 for sighting objectives, and exempts only launchers within r² 20 of home.
- "A threatened HQ bypasses batching" does nothing, because `LAUNCHER_BATCH` is 1.

**Data:**
- Engagements in losses show equal peak and join shares (0.46 / 0.46).
- Launcher deaths before round 300 are even (38.7 vs 39.5), and launchers built by round 200 are 39.5 vs 40.
- The army gap opens only after the carrier deaths diverge, so B is an effect of A.

**History:** c_batch1 and c_grp1 both failed.

### C: army away from home. Code verified; rejected in aggregate, true only in specific games

**Code:**
- The alarm is raised from HQ vision only.
- Recall requires the HQ to be within r² 225 and nearer than the siege target.
- Guard covers r² 400 and stops at round 600.

**Data:**
- In losses, 57% of our launcher deaths are at home (22.1 a game).
- Home carrier deaths happen with our launchers present (see A).

**Confirmed only for 8824g6:** engagement 17 (rounds 207–252 at (20,12)) started with 0 of our launchers against 3 of theirs and went 2 kills to 11. Meanwhile 4–5 of our launchers were around the enemy HQ at (39–40,3–4), killing about 1 at a time.

### D: raid ignores far wells. Code verified; does not separate wins from losses

- **Code:** `addPred` (line 600) filters predicted wells by `RAID_R2`.
- **Data:** wins on Forest, IslandHopping and Cornucopia show the same far-well mining by the enemy. Cornucopia's ring wells are equidistant from both sides, so a nearest-HQ rule would also miss them.
- **History:** c_raid1 inconclusive; c_hunt1 net 0.

### E1: enemy islands not contested. Code verified; survives

**Code:**
- `pickObjective()` order: sighting (845) before recall (850), guard (872), site (886), enemy islands (887–910), then raid and ring. Any shared sighting within r² 64 wins over an enemy-held island.
- Gap in what we know (code-inferred, not seen in telemetry):
  - Island slots are written only by robots that can write to the shared array.
  - A launcher trusts its own record for only 10 rounds.
  - `flushIslands()` (MapMem 173) lets an observation older than 8 rounds fill only an **empty** slot, so a stale "neutral" slot never becomes "theirs".
- Conquest is checked only when an anchor is placed, at `anchors/N >= 0.75` (`RULES.md:57`). An enemy one island short wins with its next placement.

**Spot-checks:**
- Launcher turns spent on an enemy-island objective, relative to the rounds the enemy held islands: median 0.00 in losses (28 games), 2.65 in wins (17 games).
- At the conquest threshold (one island short, or two on maps with 6 or more islands):
  - 8823g0 had our launchers 26 vs 15 and only 18 island-objective turns.
  - 8828g9 had 27 vs 26 and 0 island-objective turns over 320 rounds under threat.
- Same check across all games: our army was level or ahead in only 2 of 26 losses. Marginal cases: 8826g5 (18 vs 20), 8827g0 (9 vs 13), 8824g9 (17 vs 29).
- **Risk check:** the enemy reached one island short of conquest in 0 of 72 wins. On maps with 6 or more islands, two short also occurs in 0 wins. The 4 wins that reach two short are all 4-island maps, where that means 1 island.
- Warning before the game ends: median 94 rounds at one short, 182 at two short.

### E2: team-wide anchor veto. Verified; small

- **Code:** `HQ.java:66`: `!Comms.anyPressed() && Comms.islThem <= Comms.islUs`.
- **Maze 8823g8:** no anchor on any of the 1383 HQ turns. Only HQ (21,21) was pressed (pressure 72–292). The other two HQs were at pressure 0 with 290 and 210 Ad at round 350.
- **But** at the threat in that game we had 13 launchers against 42, so anchors would not have saved it.
- **History:** c_anc3 found that anchors built under pressure were the ones lost.

### F: anchor reserve. Verified; does not separate

- **Code:** the reserve is gated on the cumulative launchers-built count.
- **Data:** HQ turns before round 600 in anchor reserve are 0.070 in losses and 0.120 in wins. Only jmerle's games run high (8824g4 0.183, g6 0.174, g8 0.155).

### G: Ad over-mining. Verified; low

- **Data:** the Ad/Mn collection ratio at round 300 is equal (0.20 vs 0.21). Banked Ad at round 300 is 193 vs 110.
- **Specific games:** 8824g5 mined 543 Ad against their 74, and 8832g2 mined 1214 against their 97.

### H: Forest. Verified; one map

- At round 300 we had 22 carriers vs 40 in 8823g4, and 14 vs 52 in 8824g4.
- c_adlo2 was rejected.

### I: blind fire. Rejected

- c_blind1 measured about +96 damage a game, t = 0.07.
- `LEARNINGS.md` puts blind fire at about 1%.

### J: crowding. Low

- Mn per carrier at round 300 on ReverseFunnel: 8828g9 70 vs 99; 8827g9 68 vs 79.
- c_eco1 and c_eco2 both lost.

### K: amplification

A consequence of the earlier collapse, not a cause.

## 3. Ranking: expected gain against the risk to our 72 wins

| Rank | Mechanism | Plausible flips | Confidence | Gain | Risk to wins | Net |
|---|---|---|---|---|---|---|
| 1 | **E1** island conquest threat | 2 strong + 3 marginal (about 2.9 weighted) | 0.5 | +1.4 | About 0. The trigger fires in 0/72 wins on true island counts; only the stale-"theirs" sub-switch can act in wins | **about +1.2**, low variance |
| 2 | **A** home-well drop after a second flight | About 5 of the 22 | 0.3 | +1.5 | 19 wins have 6+ home carrier deaths and are exposed. c_flee3 (hold near home) lost 4 net on the panel | **+0.5 to +1**, the largest lever but high variance |
| 3 | C, game-specific | 2–3 | 0.3 | +0.7 | Larger recall or guard radii pull the army off sieges in wins | +0.3 |
| 4 | E2 | About 1 | 0.3 | +0.3 | c_anc3 history | +0.1 |
| 5 | G, F, J, H, D | 1 or fewer each | ≤0.3 | ≤0.3 | Their history candidates lost or held | ≤ +0.2 |
| — | B, I, K | Rejected | | | | |

## 4a. Plan 1: `c_isle1` = c_hr1 + `C.ISLE_THREAT`

**Files:**
- Copy `src/c_hr1` to `src/c_isle1` and rename the package.
- Edit `C.java`, `Launcher.java` and `MapMem.java`.
- Add `test/bot/Isle1Test.java`.

**C.java:**
```java
/** c_isle1: when the enemy is ISLE_MARGIN islands short of conquest, even-id launchers in march take the nearest
 *  enemy-held island before any sighting. Arm switch: false = c_hr1. */
public static final boolean ISLE_THREAT = true;
/** Sub-switch: an owner-2 sighting up to ISLE_STICKY_AGE rounds old may overwrite an owner-0 slot (never owner 1). */
public static final boolean ISLE_STICKY = true;
public static final int ISLE_STICKY_AGE = 60, ISLE_MEM = 150, ISLE_RECHECK = 5;
public static final int ISLE_MARGIN_SMALL = 1, ISLE_MARGIN_LARGE = 2, ISLE_LARGE_N = 6;
```

**Pure functions (Launcher), the unit-tested part:**
```java
static int conquestNeed(int n) { return (3 * n + 3) / 4; }        // ceil(0.75n): 4->3 6->5 7->6 8->6 9->7 12->9
static boolean conquestThreat(int them, int n) {
    if (n <= 0 || them <= 0) return false;
    return them >= Math.max(1, conquestNeed(n) - (n >= C.ISLE_LARGE_N ? C.ISLE_MARGIN_LARGE : C.ISLE_MARGIN_SMALL));
}
static boolean isleFirst(boolean threat, int id) { return threat && (id & 1) == 0; }
/** Theirs for the threat: pickObjective's rule, or our own owner-2 record within ISLE_MEM over a neutral slot. */
static boolean theirsFor(int shared, int own, int seen, int round) {
    int rule = seen > 0 && (round - seen <= 10 || shared == 0) ? own : shared >>> 12;
    return rule == 2 || (own == 2 && seen > 0 && round - seen <= C.ISLE_MEM && (shared >>> 12) == 0);
}
```
`MapMem` gets `static boolean mayWrite(int age, int slot, int owner)`. It returns c_hr1's rule (`age <= 60 && (age <= ISLAND_FRESH || slot == 0)`), and also true when `ISLE_STICKY && owner == 2 && age <= ISLE_STICKY_AGE && slot != 0 && (slot >>> 12) == 0`. `flushIslands` line 173 becomes `if (!mayWrite(age, Comms.read(ISLANDS + id), islandOwner[id])) continue;`.

**Launcher changes:**
- **New fields:** `isleCheck = -1000`, `isleThreat`, `isleBest`, `isleBestId`.
- **New `islandScan()`:** the same loop as lines 891–908, with the `ISLAND_LOOP_GUARD` bytecode guard. It counts `theirsFor` and keeps the nearest island where it holds, then sets `isleThreat = conquestThreat(count, islandCount)`.
- **In `pickObjective()`, after `midSite = site;` and before the sighting at line 845:**
  1. Invalidate the cached target when `MapMem.islandSeen[isleBestId] == G.round && islandOwner[isleBestId] != 2`.
  2. Rescan when `G.round >= isleCheck`.
  3. `if (C.ISLE_THREAT && isleFirst(isleThreat, G.id) && isleBest != null) { objKind = 1; objIsland = isleBestId; return isleBest; }`

  Arrival already uses the free-square logic at `march` 386–397, so the launchers stand on the island and wear its anchor down.

**Invariants (asserted in `Isle1Test`):**
1. With `ISLE_THREAT` false the bot behaves exactly as c_hr1: no RNG draw and no shared write.
2. `conquestThreat` is false when `them == 0` and monotone in `them`. Thresholds: n=4 → 2, 6 → 3, 7 → 4, 8 → 4, 9 → 5, 12 → 7, 35 → 25.
3. Only even-id launchers in `march` (no enemy in vision) are diverted. `fight()`, odd ids and menders are unchanged.
4. `mayWrite` equals c_hr1's rule for every case with owner 0 or 1. Enumerate age 0..70 × slot owner {empty, 0, 1, 2} × owner {0, 1, 2}. The sticky write never overwrites an owner-1 slot.
5. `islandScan` runs at most once every 5 rounds per launcher (about 1.4k bytecodes) and must show 0 overruns.

**Known side effect:** sticky "theirs" raises `islThem`, which can close the HQ anchor gate (E2). Run the ablation `c_isle2` (`ISLE_STICKY` false).

**Gates:**
- VM head-to-head against c_hr1 on the panel maps, both sides.
- Island-objective turns rise in games that reach the threshold.
- Wins that never reach the threshold stay identical with `c_isle2`.

## 4b. Plan 2: `c_drop1` = c_hr1 + `C.DROP`

This ports c_flee4's `FLEE1_DROP` alone, without the flight scoring, memory, deposit-near-HQ or lighten parts. c_flee3's failure was holding carriers near home; this has no hold.

**Files:**
- Copy to `src/c_drop1`.
- Edit `C.java` and `Carrier.java`.
- Add `test/bot/Drop1Test.java`.

**C.java:**
```java
/** c_drop1: a second flight from the same well (fighter within r2 DROP_WELL_R2 of it) within DROP_REPEAT rounds drops
 *  it, home wells included, for DROP_AVOID rounds unless the alternative is far. Local only, no hold. Arm switch: false = c_hr1. */
public static final boolean DROP = true;
public static final int DROP_WELL_R2 = 64, DROP_REPEAT = 30, DROP_AVOID = 40, DROP_ALT_D2 = 100;
```

**Pure functions (Carrier):**
```java
static boolean dropHit(boolean contFlight, int threatWellD2, boolean sameWell, int sinceLast) {
    return !contFlight && threatWellD2 <= C.DROP_WELL_R2 && sameWell && sinceLast <= C.DROP_REPEAT;
}
static boolean farAlt(int altD2, int raidD2) { return altD2 > Math.max(C.DROP_ALT_D2, 4 * Math.min(raidD2, 10000)); }
static boolean backToRaided(boolean noRoleAlt, int altD2, int raidD2) { return noRoleAlt || farAlt(altD2, raidD2); }
```

**Carrier changes:**
- **New fields:** `fWell`, `badAt`, `fWellRound = -1000`, `fRole`, `fType`, `badUntil`, `badD2`, `badKeep`, `drops`.
- **`noteFlight(t)`:** taken from `src/c_flee4/Carrier.java:555–567`, with `dropHit` as its test and `prevState` F or V as `contFlight`.
- **`survive()`:** call `noteFlight` after the hot-well block (after line 217), guarded by `C.DROP && !(C.MID && well != null && Mid.isSite(well))`.
- **`hotLocal()`:** before line 559, add `if (C.DROP && G.round < badUntil && !badKeep && l.distanceSquaredTo(badAt) <= C.DROP_WELL_R2) return true;`.
- **`anyHot()`:** add `|| (C.DROP && G.round < badUntil && !badKeep)`.
- **`gather()`:**
  - Add `boolean anyType = false;`.
  - Set it to true when the `++searchTurns > WELL_SEARCH_TURNS` any-type branch picks a well.
  - Before `if (well == null) { state = 'X'; ...}`, insert c_flee4's block from lines 713–717 (`backToRaided` sets `well = fWell` and `badKeep = true`).

**Invariants (asserted in `Drop1Test`; reuse Flee4Test section 13's `backToRaided` cases):**
1. With `DROP` false the bot behaves exactly as c_hr1.
2. No shared-array write, no hot mark, and front-well hot handling is unchanged.
3. The drop never strands a carrier. With no near alternative of its role it goes back to the raided well; it never explores and never waits.
4. The drop expires after `DROP_AVOID` rounds, or earlier when `badKeep` is set.
5. Wells of c_mid1's contested central site are excluded.
6. Only the first turn of a flight counts toward the drop.

**Gates (on the VM):**
- Head-to-head against c_hr1 on the panel maps, both sides, plus all maps.
- Home carrier deaths before round 300 down by at least 25%.
- Mn at round 300 not more than 5% below c_hr1. That is c_flee1's failure: fewer deaths, less mid-game mining.
- Then the screen, and `ladder_policy trial-start`.

## Caveats

- Engagement peak and join shares are endogenous.
- The extract has no per-round positions.
- E1's knowledge gap is inferred from the code; there is no telemetry of `Comms.islThem`.
- The threat thresholds use the engine's true island counts sampled every 10 rounds; the bot's own counts lag.
- The c_flee4 DROP ablation (`FLEE1_DROP` off scored 18/40 against the base 21, paired +1 −4) is within noise. It was never trialled alone against the field.
