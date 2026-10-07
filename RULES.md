# Battlecode 2023 (Tempest): rules digest, checked against the engine

The engine is the truth. This digest is assembled from six area reports and an adversarial re-verification of every
numbered fact in them. Facts the verifier refuted or corrected appear here only in their corrected form, marked
**(corr.)**. Every fact carries provenance. Details, derivations and per-map data live in the area reports.

## 0. Sources, conventions, status

- **Engine of record:** `engine/battlecode23-3.0.15.jar` (`battlecode_version` 3.0.15). `GameConstants.SPEC_VERSION` is
  still `"3.0.14"` in the jar and source (`GC:13`; JAR `javap -constants`). Reference source = git `af42086`
  (2023-02-05) = tag `3.0.15`.
- **Jar = source (corr.).** All 103 `.java` files were rebuilt with JDK 8 javac against the jar, and the 136 classes were
  diffed with `javap -c -p -constants`. 135 are identical. The only difference is in `GameMapIO$Serial.deserialize`, where
  the jar keeps a dead store `sipush 2000; istore 7` of the local `rounds` (`E/world/GameMapIO.java:228`). The behaviour
  is the same. `MethodCosts.txt`, `AllowedPackages.txt` and `DisallowedClasses.txt` are byte-identical (`cmp`). The jar's
  103 bundled `.map23` files are byte-identical to the source copies. Source line numbers below therefore hold for the jar.
- **Project patch:** `engine/patch-src/battlecode/world/LiveMap.java:307-308` makes `getSeed()` return
  `Integer.getInteger("bc.game.seed", seed)`. `tools/lib.sh:21` puts the patch dir ahead of the jar, and `:59` passes
  `GAME_SEED`. The patch changes only spawned-robot IDs (and through them their `Random` streams) and the replay's
  `randomSeed`. HQ IDs, HQ randomness and the coin flip are unaffected [measured] ([BR] §Surprises 14).
- **Path tags:** `E/` = `reference/battlecode23/engine/src/main/battlecode/`. `RCI` = `E/world/RobotControllerImpl.java`,
  `IR` = `E/world/InternalRobot.java`, `IC` = `E/world/robots/InternalCarrier.java`, `GW` = `E/world/GameWorld.java`,
  `ISL` = `E/world/Island.java`, `TI` = `E/world/TeamInfo.java`, `OI` = `E/world/ObjectInfo.java`, `WELL` =
  `E/world/Well.java`, `INV` = `E/world/Inventory.java`, `GC` = `E/common/GameConstants.java`, `RT` =
  `E/common/RobotType.java`, `AN` = `E/common/Anchor.java`, `IMV` = `E/instrumenter/bytecode/InstrumentingMethodVisitor.java`,
  `RM` = `E/instrumenter/inject/RobotMonitor.java`, `SRP` = `E/instrumenter/SandboxedRobotPlayer.java`, `PCP` =
  `E/world/control/PlayerControlProvider.java`, `GM` = `E/server/GameMaker.java`, `SRV` = `E/server/Server.java`, `CFG` =
  `E/server/Config.java`, `MC:n` = line n of `E/instrumenter/bytecode/resources/MethodCosts.txt`, `FBS:n` = line n of
  `reference/battlecode23/schema/battlecode.fbs`, `SPEC:n` = line n of `reference/battlecode23/specs/specs.md.html`,
  `CENSUS:col` = a column of [`research/rules/mapcensus/maps.tsv`](research/rules/mapcensus/maps.tsv). A bare file
  name (`GameMapIO.java`, `LiveMap.java`, `MapBuilder.java`, `TeamClassLoaderFactory.java`, `ClassReferenceUtil.java`,
  `MethodCostUtil.java`, `RoboPrintStream.java`, `AllowedPackages.txt`, …) is unique under `E/` (checked with `find`).
  `symmetry.ts` = `reference/battlecode23/client/visualizer/src/mapeditor/forms/symmetry.ts`; `constants.ts` =
  `reference/battlecode23/client/visualizer/src/constants.ts`.
- **Area reports** (full detail): [RO] [round-order](research/rules/round-order.md), [AC]
  [actions](research/rules/actions.md), [CT] [constants-types](research/rules/constants-types.md), [MP]
  [maps](research/rules/maps.md), [BR] [bytecode-runtime](research/rules/bytecode-runtime.md), [RS]
  [replay-schema](research/rules/replay-schema.md).
- **Markers:** facts are verified in code unless marked. **[measured]** = observed in a run of the 3.0.15 jar on JDK
  8u504. **derived** = arithmetic from verified code (the area reports used strictfp Java replicas of the engine
  expressions). **(corr.)** = corrected by the verifier. **UNVERIFIED** = not confirmed. **No item is DISPUTED.** Every
  extractor/verifier disagreement was settled from code or data. Where the two verifiers contradicted each other (max
  HQ ID 13 vs 19), `CENSUS:hq_ids_exec_order` settled it: 19 (Fractured).

---

## 1. One-screen summary

| Topic | Rule | Provenance |
|---|---|---|
| Board | W, H each 20..60. (0,0) is the bottom-left corner, `NORTH` = +y, tile index `x + y*W`. Tiles are walls, clouds, currents, wells (Ad/Mn), island squares. | `GC:20-29`, `SRV:246-257`, `E/common/Direction.java:21-55`, `GW:309-321` |
| Length | Always 2000 rounds; a map cannot change it. The first round is 1. | `GameMapIO.java:228`, `GC:170`, `GW:62,506-508` |
| Teams | Each team has 1..4 HQs. On shipped maps the counts are always equal. HQs never move, cannot be damaged, each keep their **own** resource stockpile, build robots and anchors, and hit every enemy within r² 9 for 4 at end of round. | `RT:21`, `IR:56-58,373-375,439-448`, `RCI:637-638,681-688`; `CENSUS:hq_A,hq_B` |
| Economy | Each HQ: 200 Ad + 200 Mn at round 1, +6 Ad +6 Mn every 5th round. Carriers mine infinite wells (1 per collect; 3 once the well is upgraded) and carry at most 40 kg. Elixir exists only by converting a well (deposit 600 of the other resource). | `GW:169-183`, `IR:439-448`, `WELL:38-64,90-92`, `GC:72-90,131,159-160` |
| Units | Carrier 50 Ad, Launcher 45 Mn, Amplifier 30 Ad + 15 Mn, Destabilizer 200 Ex, Booster 150 Ex (§2). | `RT:31-66` |
| Islands | 4..35 per map, each 4-connected with ≤ 20 squares. A carrier standing on an island square places an anchor (Standard 80 Ad + 80 Mn, 250 HP; Accelerating 300 Ex, 750 HP, -0.15 cooldown aura). Each round the anchor's health changes by `trunc(100*(own-enemy robots on the island)/area)`. At ≤ 0 the island turns neutral. | `SRV:311-341`, `AN:16,21`, `ISL:75-119` |
| Conquest | Checked **only** when a team places an anchor on an island it did not own: if `(float)currentAnchors/N >= 0.75f` (N = `rc.getIslandCount()`) that team wins. The rest of that round is still played. | `ISL:76,85-87`, `TI:175-194`, `GW:717-720` |
| Round 2000 | Tiebreak, first strict difference wins: islands owned → total anchors ever placed → Ex → Mn → Ad (team totals = HQ stock + carrier cargo of **living** robots) → unseeded coin flip. | `GW:525-648` |
| Other ends | `resign()`: the opponent wins after the round. There is **no elimination rule**: a team with zero robots plays on to round 2000. An engine exception ends the match with no winner (§4, §9). | `RCI:1164-1173`, `GW:194-198,637-648` |
| Turns | Robots act one at a time in **global spawn order** (both teams mixed; initial HQs in ascending map-file ID). A robot may act or move while that cooldown is < 10. Cooldowns drop by 10 at the start of the robot's own turn. | `OI:95-111,154-165`, `LiveMap.java:151-152`, `IR:223-232,425-429` |
| Terrain effects | Cloud: +0.2 cooldown multiplier, vision r² 4. Current: pushes 1 tile at end of every round. Booster: -0.1 (≤ 3 stacks). Destabilize: +0.1 (≤ 2 stacks) plus 50 damage on expiry. Accelerating anchor: -0.15. | `GW:131-143,327-400,659-690,708-710` |
| Comms | Per team, 64 ints of 0..65535. Anyone can read. Writing needs an HQ or amplifier caller, or an own amplifier within r² 20, an own HQ within r² 9, or an own island square within r² 4. | `RCI:1113-1150`, `GW:863-892` |
| Compute | Per turn: HQ 20,000 bytecodes, Carrier 12,500, others 10,000. An overrun pauses the robot mid-code and the overshoot is debt. An uncaught exception or returning from `run()` **destroys** the robot, HQs included. | `RT:21-66`, `RM:126-153,286-308`, `GW:222-223` |

---

## 2. Units

Values are from `RT:21,31,40,49,58,66`. The constructor order is BCA, BCM, BCE, actionCD, moveCD, HP, damage,
actionR², visionR², bytecodes (`RT:198-210`). They are identical in the JAR `RobotType.<clinit>` (e.g. DESTABILIZER
offset 105 `bipush 25`).

| Type | Cost Ad/Mn/Ex | HP | Action CD | Move CD | Damage | Action r² | Vision r² | Bytecodes | Notes |
|---|---|---|---|---|---|---|---|---|---|
| HEADQUARTERS | – | 1 (cannot be damaged) | **2** | -1 (immobile) | 4 to every enemy within r² 9, end of round | 9 | 34 | 20,000 | builds robots and anchors; stockpile unbounded |
| CARRIER | 50/0/0 | 150 | 10 | `floor(0.375f*w)+5` (enum: 0) | throw `floor(1.25f*w)` (enum: 0) | 9 | 20 | 12,500 | capacity 40; w = Ad+Mn+Ex+40×anchors |
| LAUNCHER | 0/45/0 | 200 | 10 | 20 | 20 | 16 | 20 | 10,000 | |
| DESTABILIZER | 0/0/200 | 300 | 70 | **25** (spec: 20) | 50 per expiring entry | 13 | 20 | 10,000 | `canAttack()` false |
| BOOSTER | 0/0/150 | 400 | 140 | 25 | 0 | -1 (boosts its own position) | 20 | 10,000 | |
| AMPLIFIER | 30/15/0 | 120 | -1 (no action) | 15 | 0 | -1 | 34 | 10,000 | lets allies within r² 20 write comms |

- Placeholder fields: `CARRIER.movementCooldown = 0` and `CARRIER.damage = 0` (the real values come from `IR:332-339` and
  `IC:47-50`). Booster and amplifier `actionRadiusSquared = -1`; amplifier `actionCooldown = -1`; HQ `movementCooldown =
  -1`. `canAttack()` is true only for CARRIER and LAUNCHER (`RT:129-132`), so the HQ aura and destabilizer damage do not
  show up there (`RT:21-66`). Only GameMaker and InternalRobot read `RobotType.movementCooldown` (JAR getfield scan).
- Inventory capacity: HQ unbounded (`new Inventory()`, maxCapacity -1), carrier 40, every other type 0 (`IR:55-66`,
  `INV:27-29,142-146`).
- HP is capped at the type maximum. A robot is destroyed the moment its health reaches ≤ 0 (`IR:376-381`).
  `addHealth` returns immediately for HQs, so HQs also ignore healing (`IR:373-375`).
- New robots start with both cooldowns at 10 (`IR:74-75`). They first act in the next round, when both drop to 0
  (`IR:425-427`, `OI:97`).
- Derived squares per radius (lattice count, own square included): r² 2 = 9, 4 = 13, 9 = 29, 13 = 45, **15 = 45** (no
  lattice point has d² 14 or 15), 16 = 49, 20 = 69, 34 = 109 (`GW:462-479`, `E/common/MapLocation.java:119-121`).
- Derived hits to kill. Launcher (20): carrier 8, launcher 10, destabilizer 15, booster 20, amplifier 6. A 50-damage hit
  (full throw or one destabilize expiry): carrier 3, launcher 4, amplifier 3, destabilizer 6, booster 8. HQ aura at 4 per
  round: 38 rounds to kill a carrier, 50 for a launcher.

---

## 3. Economy

### 3.1 HQ stockpiles and income

| Fact | Provenance |
|---|---|
| **Stockpiles are per HQ.** `buildRobot`/`buildAnchor` check and charge only the calling HQ's inventory. `rc.getResourceAmount` on an HQ returns that HQ's stock. No API returns the team total. | `IR:56-58,114-116`, `RCI:130-133,681-688,712-716,727-734,750-754` |
| Round 1, before any turn: each HQ gets +200 Ad and +200 Mn (k HQs = 200k of each per team). | `GW:169-183`, `GC:72,75` |
| End of every round with `round % 5 == 0` (5, 10, ..., 2000): **each HQ** gets +6 Ad and +6 Mn. That is 1.2/round/HQ, or 2400 of each per HQ per game (derived). The GameConstants javadoc says "per turn", which is wrong. | `IR:439-448`, `GC:77-84`; JAR `iconst_5 irem … bipush 6` |
| Moving stock between your HQs needs a carrier: withdraw with `transferResource(hq, r, -n)`, then deposit. | `RCI:881-894` |
| Derived turn 1 per HQ: 200 Ad = 4 carriers, 200 Mn = 4 launchers, at most 5 builds in the turn (cooldown 2). | `RT:21,31,40` |

### 3.2 Wells

| Fact | Provenance |
|---|---|
| Wells are infinite. Collecting never decrements anything. Any number of carriers can use one well, but at most 9 at a time (the well square plus its 8 neighbours, one robot per square) (corr.). | `RCI:961-973`, `E/common/MapLocation.java:129-133` |
| Rate per collect action: 1, or 3 once upgraded (`isUpgraded ? 3 : 1`). | `WELL:90-92`, `GC:159-160` |
| Maps start with Ad and Mn wells only. A map with an Ex well fails validation. | `SRV:368-385`, `GW:114-122` |
| Resources a carrier **deposits** into a well add to a permanent cumulative per-resource total (they leave the team totals). Thresholds below are checked at deposit time against the well's current type. | `WELL:38-80`, `RCI:912-913` |

| Well now | Deposited | Cumulative condition | Effect |
|---|---|---|---|
| ADAMANTIUM | Mana | Mn ≥ 600 | becomes ELIXIR (`WELL:50-52`) |
| MANA | Adamantium | Ad ≥ 600 | becomes ELIXIR (`WELL:40-42`) |
| ADAMANTIUM / MANA / ELIXIR | its own type | ≥ 1400 | upgraded, rate 3 (`WELL:43-45,53-55,61-63`) |
| ELIXIR | Ad or Mn | — | stored, wasted |

- The upgrade flag is never cleared. An upgraded Ad/Mn well that later converts becomes an **upgraded elixir well**
  (`WELL:16,43-52`). Collection yields the well's **current** type (`RCI:965`).

### 3.3 Carriers: weight, speed, collection rate

- Weight `w = Ad + Mn + Ex + 40×anchors` (`INV:134-137`, `RCI:151-156`). Base move cooldown `(int)floor(0.375f*w) + 5`
  uses the weight **at the moment of the move** (`IR:332-339`). Derived:

| w | 0-2 | 3-5 | 6-7 | 8-10 | 11-13 | 14-15 | 16-18 | 19-21 | 22-23 | 24-26 | 27-29 | 30-31 | 32-34 | 35-37 | 38-39 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base move CD | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |

  At m = 1: an empty carrier makes 2 moves/turn. At w ≤ 13 a second move is possible whenever the turn starts low enough.
  At w 14-15 it makes exactly 1 move/turn. At w = 40, or while holding an anchor, it moves once per 2 turns. With
  multipliers (corr., derived from `GW:498-500`): an empty carrier costs round(5m) per move. m 0.70/0.75/0.80/0.85 → 4 (up
  to 3 moves/turn). m 0.55/0.65 → 3 (up to 4). m 0.9-1.4 → 5-7 (2 moves/turn). Each move uses the **destination**
  square's m.
- Collections per turn (corr., derived). Cost = round(10m) with m at the carrier's square. m = 1.0 or 0.95 → 10 (1 per
  turn). m = 0.9 or 0.85 → 9: 2 collections only in a turn that starts at cooldown 0; sustained 10 per 9 turns. m = 0.8
  → 8: 5 per 4 turns. m = 0.7 → 7: 10 per 7. Cloud (1.2) → 12: 5 per 6 turns. In general the sustained rate is 10/cost
  per turn (`IR:223-232,327-330,425-427`).
- Filling 40 kg: 40 collects at a standard well, 14 at an upgraded one (13×3 + 1) (derived).

### 3.4 Transfers and anchors (carrier side; legality in §5)

- `transferResource(loc, type, amount)`. A positive amount deposits into **any** adjacent HQ (the enemy's too: the
  resources become theirs) or well. A negative amount withdraws, from an **own** HQ only. The whole amount of one type
  moves in one action. Amount 0 throws (`RCI:862-923`).
- `takeAnchor` needs a **completely empty** carrier (anchor weight 40 = capacity) (`IR:165-167`). There is **no
  `transferAnchor`** (JAR javap of `RobotController`; `RCI:1014-1107`).
- A throw (`attack` by a carrier) **always destroys the whole inventory**, resources and anchors, even on a miss or when
  aimed at an ally or HQ (`IC:35-45,62-73`).

### 3.5 Team totals (used by the tiebreak and the replay)

- `TeamInfo` Ad/Mn/Ex = Σ inventories of **living** robots (HQs plus carriers). Every `addResourceAmount` updates both
  the robot and the team (`IR:141-145`, `TI:148-164`).
- These reduce the totals: a robot dying (its inventory is subtracted, `GW:828-830`); a throw (`IC:35-40`); a deposit into
  a well (`RCI:912-921`); a deposit into an enemy HQ (the enemy gains it). Anchors are **not** part of any total: held
  anchors simply vanish when thrown or when the carrier dies (corr.; `TI:18-23,148-164`, `IC:41-44`).
- Enemy inventories are readable: `RobotInfo.getResourceAmount/getNumAnchors/getTotalAnchors` on a sensed enemy HQ or
  carrier (`E/common/RobotInfo.java:94-115`, `IR:197-214`).

---

## 4. Round and turn order

### 4.1 `GameWorld.runRound` (`GW:152-202`)

0. If a winner was set last round, write the MatchFooter and return DONE (`GW:153-163`).
1. `currentRound++` (it starts at 0, so the first round is 1). Every robot's indicator string is cleared (`GW:506-515`,
   `IR:421-423`).
2. **Round 1 only:** every HQ gets +200 Ad and +200 Mn, before any turn (`GW:169-183`).
3. **Turns** (`GW:204-225`), in exec order (§4.2). For each robot: (a) `actionCD = max(0, acd-10)`,
   `moveCD = max(0, mcd-10)`, and the bytecode limit is reset (`IR:425-429`); (b) the player thread runs until it
   yields, runs out of bytecodes or dies (`PCP:169-178`); (c) bytecodes used and the indicator string are recorded
   (`IR:431-437`); (d) if the thread has **terminated** (uncaught exception, `run()` returned, `disintegrate()`,
   `System.exit`), the robot is destroyed **now**. This includes HQs (`GW:222-223`).
4. **End of round** (`GW:650-721`), in this order:
   1. **Islands** (`GW:653-656`, `ISL:90-119`). For every owned island: change anchor health, turn the island neutral if
      health ≤ 0, otherwise heal own robots within r² 4 (§8). The ownership/health record is written.
   2. **Boost/destabilize expiry** (`GW:659-690`): entries with `lastRound <= round+1` are removed. Each expiring
      **destabilize** entry deals 50 to the target-team robot on that square (§5.4).
   3. **Per robot, in hash order** (`GW:692-696`, `OI:81-84`): each HQ deals 4 to every enemy within r² 9, **then** that
      HQ gets its income if `round % 5 == 0` (`IR:439-451`).
   4. Wells and team deltas are written to the replay (`GW:698-705`).
   5. **Currents** every round (`CURRENT_STRENGTH = 1`; `GW:708-710`, `GC:128`). See §6.4.
   6. Every robot's position is written (`GW:712-715`).
   7. `checkEndOfMatch`: tiebreak only if `round >= 2000` and no winner yet (`GW:630-648,717`).
   8. If a winner is set, `running = false` (`GW:719-720`).
5. Any engine exception inside the round is caught. The round returns DONE with **no winner**, and that round and the
   footer are not written (`GW:194-198`). The server then hits an NPE in `Server.getWinnerString` (`SRV:513,584-588`),
   writes no replay, and exits 64 [measured, poisoned-team case, §9.6] (corr.: was UNVERIFIED in [RO]).

### 4.2 Execution order

- Turns run in **spawn order across both teams** (a `TIntArrayList` of IDs, appended on spawn and removed by value on
  death). There is no team alternation, ID sort or per-round reshuffle. `InternalRobot.compareTo` exists but is never
  used (`OI:95-111,154-165,179-189`; `IR:8-12,498-503`; grep for sort/compareTo).
- The list is **snapshotted** before the turn loop (`OI:97`). A robot built in round r is not in the snapshot and first
  acts in r+1, after every robot older than it. A robot killed earlier in the round is skipped (`OI:99-109`).
- **Initial HQs** spawn in ascending **map-file ID** order (`LiveMap.java:151-152`, `GW:84-90`, `GameMapIO.java:343`),
  so the lowest-ID HQ acts first every round. On the 103 shipped maps, **team B moves first on 59 and team A on 44**
  (`CENSUS:hq_ids_exec_order`; re-derived by the verifier). IDs do not always alternate by team: Repetition is `A2 B3 B4 A5
  B6 A7 A8 B9`, and BowAndArrow and FourNations are `B2 A3 A4 B5`. Shipped HQ IDs range from 2 to **19** (Fractured; the
  verifier's "2..13" was wrong, `CENSUS:hq_ids_exec_order`).
- `bc.server.alternate-order` (default false, `CFG:53`) **(corr.)**: in a multi-map game, `teamsReversed` flips after
  each match (match 1 normal, match 2 reversed, match 3 normal, …). A reversal swaps the team of every map body, which
  also swaps which team holds the low IDs and moves first (`SRV:170,176,180-181`, `GameMapIO.java:347-349`; SPEC:442).
- A robot built mid-round is already exposed **in its spawn round** to island occupancy counting, destabilize damage,
  HQ damage and currents (`GW:788-804`, `ISL:95-101`, `GW:677-680`, `IR:441-443`, `GW:739`).
- Turns are sequential. A robot sees every change made by robots earlier in the round: moves, deaths, shared-array
  writes, anchors, boosts (`TI:211-213`).

### 4.3 Timers

- **Boost** cast in round R: `lastRound = R+10`. It is active immediately and removed at the end of round **R+9**
  (`GW:327-339,663`).
- **Destabilize** cast in round R: `lastRound = R+5`. The multiplier is applied immediately. **No damage at cast.** It
  is removed, and its 50 damage dealt, at the end of round **R+4** (`GW:351-362,672-688`, `RCI:842-848`).
- `MapInfo.get*TurnsLeft` = oldest entry's `lastRound - round`: 10..1 for a boost, 5..1 for a destabilize. 1 means it
  expires at the end of this round (`RCI:517-520`).
- Accelerating-anchor aura: added at placement. It is removed only when an ACCELERATING anchor is destroyed in
  `advanceTurn` (`ISL:79-83,104-112`; bug in §8).

---

## 5. Actions and their legality

### 5.1 Cooldown machinery (all actions)

- Ready iff `cooldown < 10` (`COOLDOWN_LIMIT`). There is no per-turn action counter (`IR:223-232`, `GC:118`).
- At the start of the robot's own turn, `cd = max(0, cd-10)`. Idle time is never banked (`IR:425-427`, `GC:121`).
- Each action adds `(int)Math.round(base * m)`. Each move adds `round(baseMove * m)` (`GW:498-500`, `IR:327-347`).
  - Actions use m at the robot's **current** square.
  - Moves use m at the **destination**: `move()` calls `setLocation` and then adds the cooldown (`RCI:659-664`).
  - `boost()` and `placeAnchor()` apply their own effect **before** charging their cooldown, so they see it
    (`RCI:813-819,1002-1012`).
- **Multiplier** per (square, team): `1.0 + 0.2·cloud − 0.1·min(boosts,3) + 0.1·min(destabs,2) − 0.15·min(accelAnchor,1)`,
  rounded to 2 decimals after every change (`GW:131-143,327-400`, `GC:140-156`). Cloud applies to both teams. Boost
  applies to the booster's team within r² 20 of the booster. Destabilize applies to the **opponent** within r² 15 of the
  target. The anchor applies to its owner within r² 4 of any island square. The range is **0.55 to 1.40**. Read it with
  `senseMapInfo(loc).getCooldownMultiplier(team)` (`RCI:504-524`).
- Stack caps limit **only the multiplier**. Extra entries are still stored and take over as older ones expire
  (`GW:333-337,356-360,665-669,682-685`).
- Derived actions per turn from a per-action cost c: the most in one turn is ceil(10/c) starting from cooldown 0 (c=1:
  10, 2: 5, 3: 4, 4: 3, 5-9: 2, ≥ 10: 1). The sustained rate is 10/c.

**Cost after the multiplier** (derived with the engine arithmetic; Math.round rounds half up):

| m | example | HQ 2 | 5 | 10 | 15 | 20 | 25 | 70 | 140 |
|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 3 boosts + accel anchor | 1 | 3 | 6 | 8 | 11 | 14 | 39 | 77 |
| 0.65 | 2 boosts + anchor | 1 | 3 | 7 | 10 | 13 | 16 | 46 | 91 |
| 0.70 | 3 boosts | 1 | 4 | 7 | 11 | 14 | 18 | 49 | 98 |
| 0.75 | boost + anchor | 2 | 4 | 8 | 11 | 15 | 19 | 53 | 105 |
| 0.80 | 2 boosts | 2 | 4 | 8 | 12 | 16 | 20 | 56 | 112 |
| 0.85 | accel anchor | 2 | 4 | 9 | 13 | 17 | 21 | 60 | 119 |
| 0.90 | 1 boost | 2 | 5 | 9 | 14 | 18 | 23 | 63 | 126 |
| 0.95 | anchor + destab | 2 | 5 | 10 | 14 | 19 | 24 | 67 | 133 |
| 1.00 | none | 2 | 5 | 10 | 15 | 20 | 25 | 70 | 140 |
| 1.05 | cloud + anchor | 2 | 5 | 11 | 16 | 21 | 26 | 74 | 147 |
| 1.10 | 1 destab | 2 | 6 | 11 | 17 | 22 | 28 | 77 | 154 |
| 1.15 | cloud + destab + anchor | 2 | 6 | 12 | 17 | 23 | 29 | 81 | 161 |
| 1.20 | cloud; 2 destabs | 2 | 6 | 12 | 18 | 24 | 30 | 84 | 168 |
| 1.25 | cloud + 2 destabs + anchor | 3 | 6 | 13 | 19 | 25 | 31 | 88 | 175 |
| 1.30 | cloud + 1 destab | 3 | 7 | 13 | 20 | 26 | 33 | 91 | 182 |
| 1.40 | cloud + 2 destabs | 3 | 7 | 14 | 21 | 28 | 35 | 98 | 196 |

- HQ (corr.): 5 builds/anchors per turn only for m 0.75-1.20. At m ≤ 0.70 the cost is 1, giving **10 per turn**. At m ≥
  1.25 the cost is 3: up to 4 in a turn, in a 4,3,3 pattern (10 per 3 turns). The m ≥ 1.25 case needs an HQ on a cloud,
  which 11 shipped maps have (`CENSUS:hq_on_cloud`). A single boost does **not** speed up HQ builds (2×0.9 = 1.8 → 2).
  Builds are also limited by resources and by free, sensable spawn squares.

### 5.2 Per-method legality (checks in engine order; a failed `assert` throws `GameActionException` before any state change and costs no cooldown, `RCI:659-664,708-719,1002-1012`)

"Act-loc" = `dist² ≤ caller's actionR²` (else OUT_OF_RANGE), then on the map (`RCI:190-198`). It needs **no vision**.

| Method | Caller | Legality, in order | Effect | CD | BC can/do |
|---|---|---|---|---|---|
| `move(dir)` | non-HQ | dir≠null; move-ready; not HQ; target on map; not occupied (via sensing, but adjacent squares are always within r² 4); passable | `setLocation`, then move CD at the destination. `move(CENTER)` is illegal (own square occupied). Wells, islands and currents are enterable. | base×m(dest) | 10 (MC:32) / 0 (MC:68) — `RCI:633-664` |
| `buildRobot(type, loc)` | HQ | type≠null; act-loc r² 9; ready; HQ; type≠HQ; **this HQ** holds ≥ cost of each of Ad/Mn/Ex; not occupied **and** passable, both of which need `loc` **sensable** (cloud rule, §6) | deduct from this HQ and team; spawn now (CD 10/10; acts next round) | HQ's own 2×m | 10 (MC:29) / 0 (MC:27) — `RCI:670-719`, `GW:788-809` |
| `buildAnchor(a)` | HQ | a≠null; ready; HQ; HQ holds the cost | anchor into the HQ inventory | 2×m | 10 (MC:33) / 0 (MC:69) — `RCI:721-757` |
| `attack(loc)` | Carrier, Launcher | loc≠null; act-loc (carrier 9, launcher 16); ready; `canAttack`; carrier weight > 0 | CD first, then damage. **Launcher:** 20 to an enemy non-HQ on loc. **Carrier:** `floor(1.25f·w)` (≤ 50, an anchor alone = 50) to an enemy non-HQ, then **empties the whole inventory, always**. Empty square, ally or HQ targets are legal and deal 0. | 10×m | 5 (MC:28) / 0 (MC:26) — `RCI:763-791`, `IR:404-414`, `IC:35-73` |
| `boost()` | Booster | ready; BOOSTER | boost entry on every square within r² 20 of **itself** (own team, `lastRound = R+10`), then CD with the boost included (140→126) | 140×m | 10 (MC:41) / 0 (MC:98) — `RCI:797-819`, `GW:327-339` |
| `destabilize(loc)` | Destabilizer | loc≠null; act-loc r² 13 (no vision); ready; DESTABILIZER | opponent entry on every square within r² 15 of loc (`lastRound = R+5`); no damage now | 70×m | 10 (MC:42) / 0 (MC:99) — `RCI:825-848`, `GW:351-362` |
| `collectResource(loc, amt)` | Carrier | loc≠null; act-loc r² 9; ready; amt ≥ -1; CARRIER; loc is a well; adjacent (Chebyshev ≤ 1, **own square included**); amt (-1 → rate) ≤ rate; w + amt ≤ 40 | +amt of the well's current type to the carrier and team | 10×m | 10 (MC:30) / 0 (MC:66) — `RCI:925-973` |
| `transferResource(loc, t, amt)` | Carrier | non-null; act-loc 9; ready; CARRIER; amt ≠ 0; if amt > 0 holds amt; adjacent; if amt < 0: `canAdd(-amt)`, loc is an HQ, **own team**, HQ holds -amt; loc is a well or HQ | amt into the target, -amt from the carrier. **No team check on deposit.** | 10×m | 10 (MC:31) / 0 (MC:67) — `RCI:862-923` |
| `takeAnchor(loc, a)` | Carrier | non-null; act-loc 9; ready; CARRIER; HQ at loc; own team; adjacent; HQ holds ≥ 1 of type a; carrier **empty** | HQ → carrier | 10×m | 10 (MC:34) / 0 (MC:70) — `RCI:1014-1062` |
| `returnAnchor(loc)` | Carrier | non-null; act-loc 9; ready; CARRIER; HQ at loc; own team; adjacent; holds an anchor | carrier → HQ (STANDARD first if both are held) | 10×m | 10 (MC:36) / 0 (MC:72) — `RCI:1064-1107`, `IR:155-163` |
| `placeAnchor()` | Carrier | ready; CARRIER; **own square** is an island square; holds an anchor; island not anchored by the enemy (neutral or own is fine) | §8.2; CD computed after a new accelerating aura is in place | 10×m | 10 (MC:35) / 0 (MC:71) — `RCI:975-1012`, `ISL:60-88` |
| `writeSharedArray(i, v)` | any in range | 0 ≤ i < 64; 0 ≤ v ≤ 65535; in amplification range (§7) | immediate write | none | 10 (MC:43) / **75** (MC:100) — `RCI:1130-1150` |
| `readSharedArray(i)` | any | 0 ≤ i < 64 | – | none | **2** (MC:74) — `RCI:1113-1128` |
| `disintegrate()` | any | – | throws `RobotDeathException`; destroyed at the end of this turn | – | 0 (MC:44) — `RCI:1158-1161` |
| `resign()` | any | – | destroys **every** own robot now, including HQs and itself, then `setWinner(opponent, RESIGNATION)` | – | 0 (MC:75) — `RCI:1164-1173` |
| `setIndicatorString(s)` | any | s≠null (null → NPE) | truncated to 64 chars; reset every round; last value per turn kept | – | 0 (MC:97) — `RCI:1179-1185` |
| `setIndicatorDot/Line` | any | location non-null only | appended per call; no cap; no on-map check | – | 0 (MC:95-96) — `RCI:1187-1198` |

Notes:
- `collectResource(loc, -1)` means **exactly the rate**. It fails if fewer than `rate` kg of space are left, so use
  `min(rate, 40-w)` at an upgraded well. Amount 0 is **legal**: it burns the cooldown and collects nothing. By contrast,
  `transferResource` with amount 0 throws (`RCI:871-873,925-950`).
- Spawn squares are the 28 with 1 ≤ d² ≤ 9 that are on the map, passable, unoccupied and sensable. Wells, islands and
  current squares are valid. An HQ on a cloud, or a target square that is a cloud, needs d² ≤ 4 (`RCI:689-696`,
  `IR:271-277`). The fewest spawnable squares for any HQ on a shipped map is 5 (Rewind, Repetition)
  (`CENSUS:min_spawn_tiles_per_hq`).
- Booster cadence (corr., derived): with nothing else on its square, a stationary booster pays 126 and can re-boost
  after gaps of **12, 13, 12, 13, 13** turns, averaging 12.6, because leftover cooldown carries over. A boost covers the
  cast round plus 9 more, so a lone booster leaves 2-3 rounds uncovered per cycle (`RCI:813-819`, `GW:328,663`).
- Destabilizer cadence: cooldown 70 means it acts every 7th turn at m = 1. Its own destabilize does not slow it
  (`RCI:843-848`).

### 5.3 Query methods (no sensing)

| Method | Returns | BC (MC) | Provenance |
|---|---|---|---|
| `getRoundNum`, `getMapWidth/Height`, `getID`, `getTeam`, `getType`, `getLocation`, `getHealth`, `isActionReady`, `isMovementReady`, `get*CooldownTurns` | own values | 1 | `RCI:77-128,597-627` |
| `getIslandCount` | number of distinct islands N | 20 (MC:52) | `RCI:92-94`, `GW:895-897` |
| `getRobotCount` | own robots, HQs included | 20 (MC:58) | `RCI:97`, `OI:127` |
| `getResourceAmount(r)` | **own** inventory | 5 (MC:49, F) | `RCI:130-133` |
| `getAnchor()` | STANDARD if held, else ACCELERATING, else null; throws for non-carriers | 1 (MC:51, F) | `RCI:135-141` |
| `getNumAnchors(a)` | null → total | 5 (MC:53) | `RCI:143-149` |
| `getWeight()` | resources + 40 per anchor | 10 (MC:50, F) | `RCI:151-156` |
| `onTheMap(loc)` | bounds only | 5 (MC:73) | `RCI:172-178` |
| `canActLocation(loc)` | d² ≤ actionR² and on map; always false for booster/amplifier | 5 (MC:38) | `RCI:208-214` |
| `adjacentLocation(dir)` | no checks | 1 (MC:25) | `RCI:572-575` |

### 5.4 Combat damage summary

- Launcher: 20 per attack, r² 16, one attack per turn at m = 1. It can hit squares it cannot sense (`RT:40`, `RCI:763-791`).
- Carrier throw: `floor(1.25f·w)` (w=40 → 50, 20 → 25, 8 → 10, 1 → 1). It needs only w > 0 (`IC:47-50`, `RCI:770-775`).
- Destabilize: 50 at the end of round cast+4 to **each** target-team robot standing in the r² 15 area **then**. One
  50 per expiring entry, with **no cap**: 3 overlapping casts deal 150 (`GW:672-688`).
- HQ: 4 per round to every enemy within r² 9 at end of round. Several HQs stack. It reads end-of-round positions, so a
  robot can step in, act and step out without damage (`IR:439-443`).
- HQs take no damage from anything (`IR:373-375`). A kill is immediate, mid-turn. The victim's inventory leaves its team
  totals (`IR:379-380`, `GW:815-832`).

---

## 6. Sensing, vision, clouds, currents

### 6.1 Vision rule (`IR:262-277`, `GC:137`)

`canSenseLocation(loc)`: r² = the type's vision (HQ/amplifier 34, others 20). It becomes **4 if the target square OR the
robot's own square is a cloud**. Then `dist² ≤ r²`. `assertCanSenseLocation` also requires the square to be on the map
(`RCI:180-188`). This rule governs `canSenseLocation`, `isLocationOccupied`, `senseRobotAtLocation`,
`canSenseRobot`/`senseRobot`, `sensePassability`, `senseIsland`, `senseNearbyRobots/Wells/MapInfos`,
`senseNearbyIslands`, `senseNearbyIslandLocations`, the island-ownership queries, `senseWell`, `senseMapInfo`,
`getAllLocationsWithinRadiusSquared` and the spawn checks (corr.; `RCI:216-310,353,360-390,446-451,492,527-531,563,583,689-696`).

**Exceptions (corr.):** `senseCloud(loc)` and `senseNearbyCloudLocations` shrink to 4 **only when the caller stands on
a cloud**. From outside a cloud they reveal cloud squares out to full vision. `senseCloud` has **no on-map check** and
throws CANT_DO_THAT, not CANT_SENSE_THAT. `senseNearbyCloudLocations` is **not** filtered by `canSenseLocation`
(`RCI:392-443`).

### 6.2 Sensing methods

| Method | Rules / result | BC (MC) | Provenance |
|---|---|---|---|
| `senseNearbyRobots()`, `(r)`, `(r, team)`, `(center, r, team)` | Squares within `min(r, typeVision)` of center, each also passing `canSenseLocation` from the real position. Excludes self; includes HQs. `team == null` means all. | 100 (MC:85) | `RCI:256-297` |
| `senseRobotAtLocation(loc)` / `canSenseRobotAtLocation` | throws if not sensable / null if empty; can = false on exception | 15 (MC:87) / 5 (MC:40) | `RCI:222-234` |
| `senseRobot(id)` / `canSenseRobot(id)` | the robot exists and its square is sensable | 25 (MC:86) / 5 (MC:39) | `RCI:236-248` |
| `isLocationOccupied(loc)` | throws if not sensable; true for any robot, self included | 5 (MC:63) | `RCI:216-220` |
| `sensePassability(loc)` | `!wall`; throws if not sensable | 5 (MC:88) | `RCI:299-303` |
| `senseIsland(loc)` | island ID, or **-1** | 20 (MC:76) | `RCI:305-310` |
| `senseNearbyIslands()` | IDs of islands with ≥ 1 sensable square. **No radius argument.** **HashSet order** (not sorted). | **200** (MC:83) | `RCI:312-326` |
| `senseNearbyIslandLocations([center,] [r,] id)` | Invalid ID → throws. A valid ID that is out of sight → **empty array** (the javadoc says throw). **Row-major** order (y, then x). | 100 (MC:84) | `RCI:328-358` |
| `senseTeamOccupyingIsland / senseAnchor / senseAnchorPlantedHealth (id)` | Throw unless ≥ 1 square of the island is sensable. Unowned → NEUTRAL / null / **0** (the javadoc says -1). | 20 each (MC:77-79) | `RCI:360-390`, `ISL:26-28,109-111` |
| `senseCloud(loc)` | see §6.1 exceptions | 5 (MC:89) | `RCI:392-403` |
| `senseNearbyCloudLocations(...)` | cloud squares within `min(r, vision)` of center and within (4 if on a cloud, else vision) of self | 100 (MC:90) | `RCI:405-443` |
| `senseWell(loc)` / `senseNearbyWells(...[, type])` | well or null / wells passing the vision rule, optionally of the current type | 5 (MC:91) / 100 (MC:92) | `RCI:445-502` |
| `senseMapInfo(loc)` / `senseNearbyMapInfos(...)` | cloud, passable, per-team multiplier, current, boost/destab counts and turns left. The nearby version **drops cloud squares beyond r² 4**. | 5 (MC:93) / 100 (MC:94) | `RCI:504-570` |
| `getAllLocationsWithinRadiusSquared(center, r)` | squares passing `canSenseLocation`; accepts -1 | 100 (MC:46) | `RCI:577-585` |

- Radius argument: `-1` means the type's **full** vision (not cloud-reduced). Below -1 throws CANT_DO_THAT; the no-arg
  overloads catch it and return an empty array. Otherwise the radius is `min(r, typeVision)` around center
  (`RCI:250-254`).
- **Result order:** `senseNearbyRobots/Wells/MapInfos/CloudLocations` and `getAllLocationsWithinRadiusSquared` come out in
  **column-major** order (x ascending, then y ascending), **not** by distance (`GW:462-479`). `senseNearbyIslands` is
  HashSet order. `senseNearbyIslandLocations` is row-major (`GW:96-108`).
- `MapInfo.getNumDestabilizers(myTeam)` counts the enemy destabilizes affecting **me** (stored under the victim's index,
  `GW:355`). Passing `Team.NEUTRAL` to a per-team getter throws (`E/common/MapInfo.java:43-47`).

### 6.3 Clouds

- Clouds are static. +0.2 is added to both teams' multiplier at construction (`GW:136-143`).
- A robot on a cloud sees only r² 4. A robot on a cloud is invisible beyond r² 4. A well on a cloud is visible only
  within r² 4 (`IR:271-277`).
- An HQ on a cloud can spawn only within d² 4. No HQ can spawn onto a cloud square at d² 5-9 (`RCI:689-696`). 11 shipped
  maps put HQs on clouds (32 HQs; all 6 on River), and 24 maps put wells on clouds (107 wells)
  (`CENSUS:hq_on_cloud,well_on_cloud`).
- Launcher attacks and destabilize targets need no vision, so they can hit clouded squares (`RCI:190-198`).

### 6.4 Currents (`GW:723-782`)

- Applied once per round at **end of round**, after islands, destabilize damage, HQ damage and income, and before the
  position record and the win check (`GW:705-720`).
- Each robot forecasts `loc + current` (CENTER = stay). A robot is blocked if its destination is impassable or off the
  map, or if **more than one robot forecasts that square**. A stationary robot, HQs included, forecasts its own square.
  Blocking propagates back along chains (`addToNotMoving`). Swaps and cycles are not blocked (`GW:736-761`).
- A current move adds **no cooldown**, ignores cooldowns, and applies to both teams (`IR:317-321`).
- The validator guarantees that currents point on-map, not into walls, and to unique destinations (`SRV:422-438`). A
  current **into an HQ** is legal (BowAndArrow, Rewind), and a robot on it never moves (`CENSUS:currents_into_hq`).

---

## 7. Communication

| Fact | Provenance |
|---|---|
| One array per team: 64 ints of 0..65535. It is initialised once and **never reset**. | `TI:40,98-100,211-213`, `GC:63,66` |
| Any robot can read from anywhere: `readSharedArray` costs 2. | `RCI:1113-1128`, `MC:74` |
| A write is allowed iff any of: the caller is an **HQ or amplifier** (no position check); an own **amplifier within d² ≤ 20**; an own **HQ within d² ≤ 9**; a square of an island **currently owned by the caller's team** within d² ≤ 4. These are geometric distances; clouds do not matter. | `GW:863-892`, `ISL:121-127`, `GC:96,99,102` |
| A write is visible **immediately**: robots later in this round's exec order see it, earlier robots see it next round. There is no cooldown and no per-turn limit. A write costs **75** bytecodes and `canWriteSharedArray` costs 10. | `TI:211-213`, `MC:43,100` |
| The shared array is **not** recorded in the replay. | `RCI:1147-1150` |

---

## 8. Islands, anchors, win condition, tiebreaks

### 8.1 Anchors

| Anchor | Cost | Max = initial HP | Heal/round (own robots within r² 4 of any island square) | Aura |
|---|---|---|---|---|
| STANDARD | 80 Ad + 80 Mn | 250 | +4 | none |
| ACCELERATING | 300 Ex | 750 | +6 | −0.15 for the owner within r² 4, max 1 stack |

`AN:16,21,80-89` (constructor order manaCost, adamantiumCost, elixirCost); JAR `Anchor.<clinit>`. `Anchor.unitsAffected`
and `accelerationFactor` are **never read**. The real values come from `GC:99,142` (`ISL:133`, `GW:374-400`).
`healingFrequency` = 1, so healing happens every round (`ISL:116`).

### 8.2 Island lifecycle

- Islands are made from the map's nonzero IDs. N = number of distinct IDs = `getIslandCount()` (`GW:93-108,895-897`).
- `placeAnchor` sets the owner, the anchor type and health = full. It adds the accelerating aura only when an
  ACCELERATING anchor replaces a non-accelerating one. It calls `TeamInfo.placeAnchor` **only if the placing team did
  not already own the island** (`ISL:75-88`).
- **Each round** (end of round, step 1, `GW:653-656`), for each owned island (`ISL:90-119`):
  1. `diff = (100*(own − enemy robots on the island's squares))/area`. This is Java int division, **truncating toward
     zero** (corr.: not floor; 1 enemy on 3 squares = −33). Every robot type counts.
  2. `health = min(max, health + diff)`. An unoccupied anchor never changes.
  3. If health ≤ 0: the island turns neutral, `currentAnchorsPlaced--`, and the accelerating aura is removed if that
     anchor was ACCELERATING. The island does not heal that round.
  4. Otherwise heal own robots within r² 4 of any island square, capped at max HP. A robot near several owned islands is
     healed once per island.
- Robots are counted **before** the same round's destabilize and HQ deaths and before currents (`GW:653-710`).
- Derived time to neutralise (STANDARD / ACCELERATING) with k unopposed enemies: area 20, k=1 (−5/round): 50 / 150
  rounds. Area 4, k=1 (−25): 10 / 30. Area 1, k=1 (−100): 3 / 8. Full occupancy on any area: 3 / 8 rounds. One defender
  cancels one attacker.
- **Engine bug** (code-derived, not run-tested): placing a STANDARD anchor over your own ACCELERATING one never
  removes the −0.15 aura. It persists for that team around the island for the rest of the game, even after the island is
  lost (`ISL:79-83,104-112`; `removeBoostFromAnchor` is called only at `ISL:107`).

### 8.3 Conquest

- Checked **only** inside `TeamInfo.placeAnchor`, i.e. on placement onto an island the team did not own:
  `totalAnchorsPlaced++`, `currentAnchorsPlaced++`, then if `(float)current/N >= 0.75f` → `checkWin` →
  `setWinner(team, CONQUEST)` (`TI:166-194`, `GC:93`). Losing islands never triggers a win, and there is no per-round
  re-check.
- Threshold k = ceil(0.75·N): N 4→3, 5→4, 6→5, 7→6, 8→6, 9→7, 10→8, 12→9, 14→11, 16→12, 20→15, 35→27 (derived;
  `CENSUS:islands_needed_to_win`).
- The winner is recorded mid-turn, but **every remaining robot still takes its turn and the full end of round runs**.
  The match ends after that round (`GW:204-212,717-720`). `setWinner` overwrites (`GameStats.java:19-21`), so a later
  `resign()` in the same round replaces the result. If both teams resign in one round, the last resigner loses.

### 8.4 Tiebreak at the end of round 2000 (`GW:637-648`)

Round 2000 is played in full, including decay, HQ damage and currents (`GW:630-632,717`). The first strict difference
wins:

| # | Criterion | DominationFactor | Provenance |
|---|---|---|---|
| 1 | islands owned now (after round 2000's decay) | MORE_SKY_ISLANDS | `GW:525-544` |
| 2 | `totalAnchorsPlaced`: placements on islands not owned at the time. Recaptures count again; re-anchoring your own island counts 0; it never decrements. | MORE_REALITY_ANCHORS | `GW:549-561`, `TI:189,200-202` |
| 3 | elixir team total | MORE_ELIXIR_NET_WORTH | `GW:566-581` |
| 4 | mana team total | MORE_MANA_NET_WORTH | `GW:586-601` |
| 5 | adamantium team total | MORE_ADAMANTIUM_NET_WORTH | `GW:606-621` |
| 6 | `Math.random() < 0.5 ? A : B`, **unseeded**: reruns can flip it [measured: 7 dead-vs-dead games gave A,B,B,A,A,A,B] | WON_BY_DUBIOUS_REASONS | `GW:626-628` |

Team totals: §3.5. The win reason is not stored in the replay (§11).

---

## 9. Bytecode costs and runtime limits

### 9.1 Counting rules (`IMV`)

| Item | Cost | Provenance |
|---|---|---|
| Every ordinary JVM instruction (field, arithmetic, array load/store, local load/store, ldc, push, iinc, jump, switch, new, checkcast, instanceof, return, athrow) | 1 | `IMV:104-153,295-341,629-658` |
| Call instruction | 0, plus the MethodCosts entry if listed. A user method costs its argument pushes plus its body [measured: `add(1,2)` = 7 including the store]. | `IMV:405-525,454-458` |
| `invokedynamic`, labels, frames, line numbers | 0 | `IMV:343-403` |
| `newarray`/`anewarray` | `max(1, length)`; `multianewarray` = product of `max(dim,1)` [measured: int[100] = 100, int[0] = 1, int[10][20] = 200] | `IMV:585-640`, `RM:166-176,192-215` |
| `System.arraycopy` | its length; array `clone()` = 0 | `E/instrumenter/inject/System.java:126-130`, `MethodCostUtil.java:85-86` |
| Any non-static `hashCode()`/`toString()` call | **1**, rewritten to `ObjectMethods` **before** the MethodCosts lookup, so `MapLocation.hashCode/toString` (listed 2) and `MapInfo.toString` (listed 15) cost 1 [measured] (corr.) | `IMV:405-428` |
| Entering an exception handler (catch, or finally on the exceptional path) | **+500 per handler**, charged on entry, not on throw [measured: throw+catch 510; through finally then catch 1017; caught GameActionException ≈507] | `IMV:180-186,623-627`, `GC:69` |
| `new Random()` | rewritten to `new Random(robotID)`; its constructor body is charged | `IMV:430-436` |
| `MONITORENTER/EXIT` (synchronized **blocks**) | illegal. Synchronized **methods** are allowed: the flag is silently stripped (corr.). | `IMV:325-332`, `InstrumentingClassVisitor.java:84-88` |

- The counter flushes at the end of each basic block, through `RobotMonitor.incrementBytecodes` (`IMV:681-687`). Javac
  emits a label per line, so in practice it flushes almost every line. A robot can pause **only** at a flush.
- **Flush before a call (corr.):** a MethodCosts entry whose third column is `true` is charged and flushed **before**
  the call runs, so if it exhausts the budget the robot pauses before the call and makes the call next round. Entries
  marked `false` (`getResourceAmount`, `getWeight`, `getAnchor`, and every MapLocation, Direction and Math entry) are
  charged at the next block end, i.e. after the call (`IMV:452-458,522-523`, `MethodCostUtil.java:45-52`, `MC:49-51`).

### 9.2 MethodCosts (`MC`; lookup by owner/name, all overloads share a cost, supertypes searched; unlisted = 0)

| Cost | RobotController methods |
|---|---|
| 200 | `senseNearbyIslands` (MC:83) |
| 100 | `senseNearbyRobots`, `senseNearbyMapInfos`, `senseNearbyWells`, `senseNearbyCloudLocations`, `senseNearbyIslandLocations`, `getAllLocationsWithinRadiusSquared` (MC:46,84-85,90,92,94) |
| 75 | `writeSharedArray` (MC:100) |
| 25 | `senseRobot` (MC:86) |
| 20 | `senseIsland`, `senseTeamOccupyingIsland`, `senseAnchorPlantedHealth`, `senseAnchor`, `getIslandCount`, `getRobotCount` (MC:52,58,76-79) |
| 15 | `senseRobotAtLocation` (MC:87) |
| 10 | `canMove`, `canBuildRobot`, `canCollectResource`, `canTransferResource`, `canBuildAnchor`, `canTakeAnchor`, `canPlaceAnchor`, `canReturnAnchor`, `canBoost`, `canDestabilize`, `canWriteSharedArray`; `getWeight` (F) (MC:29-36,41-43,50) |
| 5 | `canAttack`, `canSenseLocation`, `canActLocation`, `canSenseRobot`, `canSenseRobotAtLocation`, `isLocationOccupied`, `onTheMap`, `sensePassability`, `senseCloud`, `senseWell`, `senseMapInfo`, `getNumAnchors`; `getResourceAmount` (F) (corr.; MC:28,37-40,49,53,63,73,88-89,91,93) |
| 2 | `readSharedArray` (MC:74) |
| 1 | simple getters (`getID`, `getLocation`, `getRoundNum`, `getType`, `isActionReady`, …), `adjacentLocation`; `getAnchor` (F) (MC:25-65) |
| 0 | every action (`move`, `attack`, `buildRobot`, `collectResource`, `transferResource`, `buildAnchor`, `takeAnchor`, `placeAnchor`, `returnAnchor`, `boost`, `destabilize`), `resign`, `disintegrate`, `setIndicator*` (MC:26-27,44,66-72,75,95-99) |

- Dead entries (no such method in 3.0.15): `senseCooldownMultiplier`, `senseDestabilizeTurns`, `senseBoostTurns`,
  `isTransformReady`, `MapLocation.isWithinSensorRadius` (JAR javap; corr.).
- `MapLocation` methods cost 2 each (`valueOf` 25; `hashCode`/`toString` really 1); `new MapLocation(x,y)` = 0 plus pushes
  [measured 5 total] (MC:12-24). `Direction` listed methods cost 1; `values()` costs 0 (MC:4-11). `RobotType` and `Team`
  cost 1. `WellInfo` costs 1 (`getRate` 2). `MapInfo` getters cost 2 (`getMapLocation` 1) (MC:101-124). `RobotInfo`
  getters, `Anchor` getters and enum `values()` are free. `Clock.yield`/`getBytecodesLeft`/`getBytecodeNum` cost 0.
- `java.lang` (uninstrumented): **only the listed** `Math`/`StrictMath` methods cost 1 (`abs`, `min`, `max`, `sqrt`,
  `floor`, `round`, …). Unlisted ones (`floorMod`, `floorDiv`, `addExact`, `toRadians`) cost 0 [measured] (corr.). Listed
  `String` methods (`equals`, `indexOf`, `contains`, `startsWith`, …) and `StringBuilder.append/insert/…` cost 1.
  `String.charAt`, `length`, `substring`, `Integer.parseInt` and boxing cost 0. `Math.random`, `StrictMath.random`, and
  `String.matches/replaceAll/replaceFirst/split` are redirected to instrumented code and charged (`MC:125-218`,
  `IMV:460-468`).

### 9.3 Libraries

- Allowed packages, **exact match only, no subpackages**: `java/io`, `java/lang`, `java/lang/invoke`, `java/math`,
  `java/util`, `java/util/function`, `java/util/regex`, `java/util/stream`, `java/text`, `battlecode/common`, some
  `scala/…` (`AllowedPackages.txt:1-26`, `ClassReferenceUtil.java:98-102`). All of `java.util.concurrent`, `java.lang.reflect`
  and `java.nio` are illegal, apart from 4 swapped classes [measured: `ConcurrentHashMap.keySet()` → illegal
  `ConcurrentHashMap$KeySetView`] (corr.).
- Disallowed classes even inside allowed packages: `File*`, `Thread*`, `Runtime`, `ClassLoader`, `Process*`, `Date`,
  `Calendar`, `Locale`, `Properties`, `Timer`, `UUID`, `WeakHashMap`, … (`DisallowedClasses.txt:1-49`).
- Banned calls: `wait`/`notify`/`notifyAll`; **every** `java.lang.Class` method except `desiredAssertionStatus`
  [measured: `getClass().getName()`]; `String.intern`; `PrintStream(String…)`; `System.currentTimeMillis`, `nanoTime`,
  `gc`, `getenv`, `getProperties`, `getSecurityManager`, `load`, `loadLibrary`, `mapLibraryName`, `runFinalization`,
  `runFinalizersOnExit`, `setProperties`, `setSecurityManager`; any `java/lang/invoke` call; **method references** to
  anything rewritten or charged (e.g. `MapLocation::distanceSquaredTo`, `Math::random`) (`IMV:366-393,535-583`).
- **Charged as your code:** `java/util/**` and `java/math/**` are re-read from the **running JDK** and instrumented per
  robot, except `java/util/invoke`, `jar`, `zip`, `Iterator` and `concurrent/TimeUnit`; scala and kotlin (except
  `Intrinsics`) likewise (corr.; `ClassReferenceUtil.java:104-133`, `TeamClassLoaderFactory.java:465-481`). Costs
  therefore depend on the JDK build. JDK 8u504 measurements: `HashMap.get` ≈52; `put` on an existing key ≈68; `put` of a
  new key without resize ≈91; first `put` into an empty `HashMap` ≈143 (extractor measurement, includes the table
  allocation; not reproduced by the verifier, UNVERIFIED as a general cost).
- **Free swaps:** `ConcurrentHashMap` becomes `inject.ConcurrentHashMap`, which extends the real uninstrumented
  `Hashtable`. `AtomicInteger/Long/Reference` become engine stand-ins. All their operations cost 0 [measured: CHM put/get
  = 0] (`ClassReferenceUtil.java:159-178`, `E/instrumenter/inject/ConcurrentHashMap.java:11`). Their iteration order
  over identity-hashed or enum keys is **non-deterministic** [measured: 3 orders in 3 identical runs].

### 9.4 Limits, overruns, `Clock`

- Limit per turn: HQ 20,000, Carrier 12,500, Launcher/Destabilizer/Booster/Amplifier 10,000. It is reset every turn
  (`RT:21-66`, `IR:428`, `PCP:175-176`).
- Robots run strictly one at a time, each on its own thread (`SRP:153-167,286-313`).
- **Overrun:** at a flush, `bytecodesLeft -= n`. While `bytecodesLeft <= 0` the robot pauses **in place**. On resume,
  `reactivate()` sets `bytecodesLeft += limit` if it was negative (debt), otherwise `= limit` (`RM:126-153,286-308`).
  - The robot resumes at the same instruction next round with its locals intact. Values it cached before the pause are
    a round old; any `rc` call after resuming reads the current world (corr.).
  - With debt D ≥ limit L, the robot pauses again and **loses whole turns**. If `L − D` reaches exactly 0, the next turn
    gets the full limit (corr.: the boundary is ≥, not >) [measured: `new int[50000]` on an HQ with 19,818 left in round
    2 → round 3 lost → resumed in round 4 with 9,811 left].
  - Cooldowns keep decrementing during lost turns (`processBeginningOfTurn` still runs, `GW:214-216`).
- `Clock.yield()` = `pause()` (0 bytecodes). Unused bytecodes never carry over (`E/common/Clock.java:24-26`). **Trap:** it
  flushes the pending block first. If that flush drives the budget to ≤ 0, the robot pauses inside the flush, wakes
  next round, and yields at once, **losing that entire turn** [measured].
- `Clock.getBytecodesLeft()` and `getBytecodeNum()` (= limit − left, debt included) cost 0 and **do not flush**, so they
  lag by the current block and any pending array cost (`MC:2-3`, `RM:102-112`).
- An idle `while(true) Clock.yield();` costs 1 per turn (the `goto`) [measured].

### 9.5 Death and exceptions

- Returning from `run()`, an uncaught exception, `disintegrate()` or `System.exit` ends the thread (`terminated = true`).
  `GameWorld` destroys the robot at the end of that turn, **HQs included**, and its stockpile leaves the totals
  (`SRP:175-219`, `GW:222-223,815-832`, `E/instrumenter/inject/System.java:152-154`) [measured: HQs 2, 4 and 5 died in
  round 1].
- **Death cannot be caught.** `RobotDeathException extends VirtualMachineError`. Every method with a try/catch gets a
  first handler `catch (VirtualMachineError) { throw; }`, so even `catch (Throwable)` cannot swallow death,
  `StackOverflowError` or `OutOfMemoryError` (`E/instrumenter/RobotDeathException.java:10`, `IMV:157-169,279-293`)
  [measured: a StackOverflowError inside `try/catch(Throwable)` killed the robot].
- `resign()` marks the caller's thread to die. The thread throws at its next instrumented block (`SRP:319-341`,
  `RM:127-130`).

### 9.6 Illegal code: instrumentation failure (corr.)

- Instrumentation runs when a class is **first loaded** (lazily). `InstrumentationException` is a RuntimeException thrown
  at the use site. For `RobotPlayer` that is the robot's first turn, and the robot dies. For a class first touched
  mid-game, a bot `catch (Exception)` can catch it and the robot survives, if the handler needs no new class [measured
  probe4].
- The first failure sets `hasError` on the team's loader factory ("Team is known to have errors"). Every later class
  load for that team throws, engine classes included. New spawns die immediately (`die_exception`)
  (`TeamClassLoaderFactory.java:412-414,445-462`, `PCP:129-144`).
- If every robot of the team dies in round 1, the game runs to round 2000 and ends in a coin flip [measured]. If one
  survives, then on JDK 8, around that robot's 16th turn, reflection inflation loads a class through its loader. The
  engine thread throws, `runRound` returns DONE with no winner, `Server.getWinnerString` NPEs, **no replay is written**,
  and the process exits 64 [measured probe3/probe4]. The factory is created once per game, so the poisoning carries into
  later maps of a multi-map run (`SRV:167,513,588`, `GW:194-197`).

### 9.7 Isolation, statics, memory, output

- Each robot has its **own class loader** in one shared JVM, so statics are per robot. A static initialiser is charged to
  the robot's first turn, or to the turn a class is first touched [measured: `static int[3000]` = 3,003 on every robot's
  first turn] (`PCP:129-136`, `TeamClassLoaderFactory.java:82-88,360-493`, `SRP:236-268`). Derived: an `int[]` literal
  costs about 5 per element (UNVERIFIED by measurement).
- **No per-robot memory limit** exists in the engine (grep finds no heap accounting). The spec's 8 MB rule is not
  implemented; tournament enforcement is UNVERIFIED (SPEC:269).
- `System` is replaced per robot by `inject.System`. `out` = `err` = the robot stream. `in` gives EOF. `exit` kills the
  robot. `identityHashCode` uses a per-robot counter. `getProperty`/`setProperty`/`clearProperty` work on a per-robot
  copy. **15 fixed keys** (`java.version`, `java.vendor`, `java.vendor.url`, `java.home`, `java.class.version`,
  `java.class.path`, `os.name`, `os.arch`, `os.version`, `file.separator`, `path.separator`, `line.separator`,
  `user.name`, `user.home`, `user.dir`) return `"who knows?"`. Explicitly set config keys starting with `bc.testing` are
  copied in. Any other key returns null (corr.; `E/instrumenter/inject/System.java:37-79,102-154`) [measured:
  `bc.testing.foo=bar`, `java.vm.name=null`].
- Printing costs only its argument building: `getstatic System.out` 1, `println` 0, each `StringBuilder.append` 1, the
  final `toString` 1. An overridden `toString` is charged (`RoboPrintStream.java:30-35,83-93`).
- Robot `System.out` goes to engine stdout only when `bc.server.robot-player-to-system-out=true` (the default), and never
  for a team silenced by `bc.engine.silence-a/-b`. It is **never** stored in the replay (`GM:505-514`, `CFG:38`,
  `SRP:396-414`). Uncaught-exception stack traces go to engine stderr (`E/server/ErrorReporter.java:33-44`).

### 9.8 IDs, randomness, determinism

- HQ IDs come from the map file (2..19 on shipped maps). Spawned robots draw from `IDGenerator(mapSeed)`: blocks of 4096
  starting at 10001, each block Fisher-Yates shuffled. The first 4096 spawns fall in [10001, 14096], which fits in 14
  bits. **Both teams share one generator**, so a team's IDs depend on the opponent's spawn timing (`E/world/IDGenerator.java:16,21,48-53,73-94`,
  `GW:63,806-809`). Map seeds range from 5 to 988 (`CENSUS:seed`). `GAME_DEFAULT_SEED = 6370` is unused (`GC:167`).
- `new Random()` → `Random(robotID)`. `Math.random()` uses a per-robot `Random(robotID)` [measured: HQ 3's
  `new Random().nextInt()` == `new Random(3).nextInt()`] (`RM:51-64,249-251`,
  `E/instrumenter/inject/InstrumentableFunctions.java:17-25`). HQ streams depend only on the map-file ID. A spawned
  robot's stream depends on both teams' spawn sequence (corr.).
- Identity `hashCode` is a per-robot counter 0, 1, 2, … **only at instrumented call sites**. Uninstrumented JDK code
  reaches the real JVM hash [measured: `"" + new Object()` → `java.lang.Object@36327ec0` while `new Object().toString()`
  → `object0`] (corr.; `E/instrumenter/inject/ObjectMethods.java:34,42-54,78-89`).
- **Determinism** (corr.): a game is reproducible given the same map, classes, sides, config and JDK, **except** for the
  unseeded final coin flip, StackOverflowError depth (it varies between runs [measured]), real identity hashes leaking
  into bot-visible values (string concatenation of a default `toString`, ConcurrentHashMap/Hashtable order), and the
  JDK-8 poisoned-team crash. `GameWorld.rand` and `RobotControllerImpl.random` are assigned but never read (`GW:52,78`,
  `RCI:37,49`).

### 9.9 Headless properties (`CFG:31-72,105-172`)

| Key | Default | Effect |
|---|---|---|
| `bc.game.team-a/-b`, `.url` (required), `.package` | – | team name, class dir/jar, package of `RobotPlayer` (`E/server/Main.java:14-50`) |
| `bc.game.maps`, `bc.game.map-path` | `glass`, `maps` | one match per map, all in one replay; the dir is searched before the jar resources (`GameMapIO.java:51-63`; the gradle task's `bc.server.map-path` is never read) |
| `bc.server.save-file` | `match.rms` | replay path (gzip flatbuffer) |
| `bc.server.alternate-order` | false | flip the teams after each match (§4.2). GameFooter winner = A if aWins ≥ bWins (ties → A) (`SRV:207`) |
| `bc.game.best-of-three` | false | stop at 2 wins, only with exactly 3 maps |
| `bc.server.validate-maps` | true | map guarantees; a failure puts the server in ERROR and stops the game (`SRV:169,177-186,464-469`) |
| `bc.server.websocket` | **true** | port 6175, buffers every event; a busy port gives an NPE but the match still writes its replay [measured]. Pass `false` for batch runs. |
| `bc.server.robot-player-to-system-out` | true | robot prints to stdout |
| `bc.engine.silence-a/-b` | false | drop that team's prints |
| `bc.engine.debug-methods` | false | `debug_*` void methods removed (arguments still run and charged); true → bodies run **uncharged** (`IMV:164-166,234-277,486-519`) |
| `bc.engine.enable-profiler` | false | profiler data in the MatchFooter; counts unchanged |
| `bc.engine.show-indicators` | true | indicator strings/dots/lines in the replay (`GM:669-701`) |
| `bc.testing.*` | – | readable by bots via `System.getProperty` |

A `bc.conf` in the working directory **overrides** `-D` flags unless `-c=-` is passed (`CFG:145-162`; `tools/lib.sh:60`
passes it). There is no official seed, round-limit or bytecode-limit property.

---

## 10. Map corpus census and symmetry

**Data:** [`research/rules/mapcensus/maps.tsv`](research/rules/mapcensus/maps.tsv) (103 rows × 67 columns). It was
produced by `research/rules/mapcensus/MapCensus.java` through the jar's own `GameMapIO` loader. Rebuild with
`research/rules/mapcensus/run.sh`. The per-map table is in [MP] §4.

### 10.1 Map rules enforced at run time (`SRV:244-439`, only if `bc.server.validate-maps`)

| Rule | Provenance |
|---|---|
| W and H each 20..60 | `SRV:246-257` |
| Bodies are HQs, one per square. **Total** HQs 2..32 (`MIN*2`, `MAX*8`); the per-team count and balance are **not** checked. | `SRV:259-278`; JAR `iconst_2`/`bipush 32` |
| A wall square holds no cloud, well, island, current or HQ. No cloud+current, well+HQ, well+current or current+HQ on one square. | `SRV:280-309` |
| 4..35 islands (distinct nonzero IDs), each ≤ 20 squares and **4-connected** | `SRV:230-242,311-341` |
| Every HQ has an Ad well within d² ≤ 100 (`MIN_NEAREST_AD_DISTANCE`, a *maximum* despite its name). Every Ad well has a Mn well within d² ≤ 100 and vice versa. | `SRV:344-411`, `GC:47-50` |
| No initial Ex wells. Wells per type ≤ `(int)(W*H*0.04f)`. | `SRV:368-419` |
| Each current points on-map, not into a wall, to a destination no other current uses | `SRV:422-438` |
| **Not checked:** symmetry; HQs per team; HQ or well on a cloud or island; a current into an HQ; reachability; HQ distance; mana near an HQ; contiguous island IDs; origin (0,0) | absences in `SRV:244-439` |

- Only HEADQUARTERS bodies are kept from a map file; others are silently dropped. Every map gets 2000 rounds
  (`GameMapIO.java:223-228,338-356`).
- Map encoding: currents index `DIRECTION_ORDER = {CENTER, W, NW, N, NE, E, SE, S, SW}`; resources 0 none / 1 Ad / 2
  Mn / 3 Ex; island 0 = none (`Direction.java:55`, `GW:69-122`).

### 10.2 Symmetry

- Transforms (`MapBuilder.java:130-150`; client `symmetry.ts:121-139`): **ROTATIONAL** (x,y)→(W−1−x, H−1−y).
  **HORIZONTAL** (x,y)→(x, H−1−y), so **y flips**. **VERTICAL** (x,y)→(W−1−x, y), so **x flips**. HQs map to HQs of the
  other team.
- **Currents mirror geometrically:** ROT negates (dx,dy), HORI negates dy, VERT negates dx (`symmetry.ts:102-113`).
  `MapBuilder.getSymmetricCurrent` uses `opposite()`, which is wrong for reflections. 41 of the 54 reflection maps with
  currents do not fit `opposite()` (`MapBuilder.java:176-179,371`; `CENSUS:sym_currents_geometric,sym_currents_opposite`).
- Symmetry is **never checked at run time** (SPEC:46 promises it). `MapBuilder.assertIsValid` (dev tool) rejects all
  103 shipped maps, because its island-ID rule `k → W·H−k` never holds. With islands removed it still rejects 62: 41 fail
  symmetry (40 on the `opposite()` currents rule; FourNations on wells) and 21 fail "Teams must have at least one
  adamantium well visible" (corr.; `MapBuilder.java:186-188,287-318,365-377`).
- **All 103 shipped maps are geometrically symmetric** across walls, clouds, currents, wells (type and position),
  islands (as square groups) and HQs: ROT-only 44, VERT 42, HORI-only 16, Cornucopia both ROT and HORI
  (`CENSUS:sym_all`).
- **FourNations** declares ROTATIONAL but is only VERTICAL-consistent: rotation swaps Ad and Mn wells. Check well
  **type**, not just position (`CENSUS:declared_sym_consistent`).
- Robots **cannot read** the symmetry. Global facts available are only `getMapWidth`, `getMapHeight` and
  `getIslandCount` (`E/common/RobotController.java:37,47,56`). Own HQ positions alone **never** settle it (0/103; they rule
  one out on 19, leave all three on 84). Round-1 HQ vision (modelled) settles it on 10, leaves two on 65 and three on 28
  (`CENSUS:syms_left_*`; the model is an analysis assumption, [MP] §2).
- Island IDs are 1..N on every shipped map, but this is not validated, and mirrored islands follow no ID rule (only 5/103
  use id ↔ N+1−id) (`CENSUS:island_ids_1_to_N`; SPEC:464).

### 10.3 Corpus distribution (103 maps)

| Dimension | Values (`CENSUS` columns) |
|---|---|
| Tournaments (client labels; no FINAL maps in the jar) | Default 9, Sprint 1 23, Sprint 2 25, Intl Qual 15, US Qual 15, HS/Newbie 16 (`client/visualizer/src/constants.ts:147-261`) |
| Size | W and H 20..60 (medians 40 and 30). Area 400..3600 (median 1200). 52 square, 47 wide, 4 tall. |
| HQs per team | 1: 26 maps; 2: 66; 3: 8; 4: 3 (Forest, Fractured, Repetition); always balanced |
| First mover | team B 59, team A 44 (`hq_ids_exec_order`) |
| Islands (N) | 4: 44 maps; 5: 6; 6: 8; 7: 2; 8: 31; 9: 3; 10: 1; 12: 3; 14: 1; 16: 2; 20: 1; 35: 1. Anchors to win: 3 on 44 maps, 6 on 33, max 27 (ThirtyFive). |
| Islands, other | 1-square islands on HideAndSeek, RockWall and maptestsmall. Diagonally touching distinct islands on Flower, Spiderweb, ThirtyFive and maptestsmall. Fully-current islands: all 16 on Spiderweb (every path leaves the island within ≤ 8 current steps), Barcode #5, Cornucopia #2 and #9. Every island fully cloud on USA, Lines and Sakura. HQs and wells are never on islands. |
| Wells | Ad 2..16 (median 4), Mn 2..16 (median 4), never Ex. Worst HQ's nearest Ad: d² 8..100 (exactly 100 on 11 maps). Worst HQ's nearest Mn: d² 8..**328** (Forest, Fractured). **37 maps** have an HQ with no Mn within d² 100. |
| Wells visible at spawn | Under the real cloud rule, no HQ senses Mn on **67** maps and no HQ senses Ad on **45** (corr.; raw d² ≤ 34 counts in the TSV, `hqs_with_*_in_vision34`, are 62 and 38) |
| Opposing HQs | d² 4..3481 (median 441); BFS 2..62 steps (median 25). BowAndArrow d² 4 (each inside the other's r² 9), Squares 10; 13 maps ≤ 100. |
| Terrain | Walls 1.1-71.5% (median 14.1). Clouds 0-54.5% (median 7.1). Currents 0-18.4% (median 3.3). HQs on clouds: 11 maps. Wells on clouds: 24. Currents into an HQ: BowAndArrow, Rewind. |
| Reachability (not validated) | Every well and island is reachable by both teams. 14 maps have sealed pockets (Cat 814 squares). Tiles only one team can reach: PipesAndParabolas 108, ThirtyFive 12, Jail 4. |

---

## 11. Replay format (`.bc23`) and how to read it

### 11.1 Container and events

- The file is **GZIP** around one FlatBuffer with root `GameWrapper{events:[EventWrapper], matchHeaders:[int],
  matchFooters:[int]}`. The int vectors are indices into `events` (`GM:160-190,451,502`; `FBS:344-351`) [measured: test1
  821,251 bytes gz, 7,025,880 raw, 2004 events].
- Event bytes: GameHeader 1, MatchHeader 2, Round 3, MatchFooter 4, GameFooter 5. The order is GameHeader, then (per
  map) MatchHeader, Round×N, MatchFooter, then GameFooter. **Robot IDs restart each match**, so reset state at every
  MatchHeader (`GM:38-55,237-239,441-457`; `SRV:177-209,464`).
- Every round is written, the deciding round included. `MatchFooter.totalRounds` = last `roundID`. The whole game is
  held in memory and written once at the end, so a killed engine leaves no file (`GW:152-202`, `GM:214-228`; the killed-JVM
  case is UNVERIFIED by experiment).
- Reading needs only the engine jar: `battlecode.schema.*` (21 classes) plus `com.google.flatbuffers.*`. Use
  `GameWrapper.getRootAsGameWrapper(ByteBuffer.wrap(gunzipped))`, `gw.events(ew, i)`, `ew.eType()`,
  `(Round) ew.e(new Round())`, `Action.name(b)`, `BodyType.name(b)`. Working reader:
  `research/rules/replay/ReplayReader.java` (`run.sh [file] [rounds]`; 18 consistency checks, all at 0 violations on
  `matches/test1.bc23`).

### 11.2 Headers and footers

- **GameHeader:** `specVersion "3.0.14"`. Team A teamID 1, B 2 (NEUTRAL 0) in every team field. `bodyTypeMetadata` holds
  raw RobotType fields (carrier move 0, HQ health 1, -1 sentinels, destabilizer move 25). `constants` holds
  increasePeriod 5 and Ad/Mn increase 6/6; the writer swaps the two, which is harmless while both are 6 (`GM:237-303`;
  `E/util/TeamMapping.java:14-20`).
- **MatchHeader.map:** `minCorner` = origin; `maxCorner` is **exclusive** (W = max.x − min.x). Per-square arrays are
  indexed `x + y*W` (§10.1 encodings). `symmetry` 0 ROT / 1 HORI / 2 VERT. `randomSeed` = the effective seed (our patch
  may override it). `bodies` = the initial HQs **only**: they never appear in round 1's `spawnedBodies`, because
  `clearData()` runs after their spawn (`GameMapIO.java:262-332`, `GW:84-111`, `GM:441-454,716-760`). `maxRounds` = 2000.
- **MatchFooter:** `winner` (1/2), `totalRounds`, and `profilerFiles` (always written, empty unless profiling)
  (`GM:456-503`). **GameFooter:** `winner` = A if aWins ≥ bWins (`SRV:207-208`).
- **The win reason is not stored** (corr.). `totalRounds < 2000` means CONQUEST (decided mid-turn by a placement) or
  RESIGNATION. Otherwise apply §8.4 to the final state. Criterion 2 (`totalAnchorsPlaced`) must be rebuilt from the
  **whole match's** PLACE_ANCHOR history (count placements onto islands the team did not own then). If every criterion
  ties, the result was the coin flip (`SRV:584-639`, `GW:525-648`).

### 11.3 Round fields

| Field(s) | Meaning | Provenance |
|---|---|---|
| `roundID` | 1-based, no gaps | `GM:614` |
| `teamIDs`, `team{Ad,Mn,Ex}Changes` | **this round's delta** of team totals (A then B). Cumulative sum = Σ living inventories. | `TI:215-234`, `GW:703-705` |
| `movedIDs`, `movedLocs` | **every living robot, every round**, end-of-round position **after currents**, hash order. Not "robots that moved". | `GW:707-715`, `OI:81-84` |
| `spawnedBodies` | robots built this round, each paired with a SPAWN_UNIT action | `GW:788-804`, `GM:708-714` |
| `diedIDs` | every removal (killed, self-terminated, resigned); no cause recorded | `GW:815-832` |
| `actionIDs`, `actions`, `actionTargets` | parallel arrays (§11.4) | `GM:641-645` |
| `islandIDs`, `islandOwnership` (0/1/2), `islandTurnoverTurns` | every island every round, after decay. `islandTurnoverTurns` is actually **anchor health** (0 when neutral). | `GW:653-656`, `GM:656-660`, `ISL:35-58` |
| `resourceWellLocs`, `resourceID`, `wellAccelerationID`, `well{Ad,Mn,Ex}Values` | every well every round, ascending location index. `resourceID` = current type. Acceleration 1 = upgraded. Values = cumulative **deposits** (they never decrease). | `GW:698-702`, `GM:647-654`, `WELL:38-96` |
| `bytecodeIDs`, `bytecodesUsed` | one entry per robot that took a turn; `limit − bytecodesLeft` at the pause. **≥ the type's limit means an overrun or skipped turn.** Robots built this round have none. | `GW:214-218`, `PCP:181-191`, `RM:102-104` |
| `indicatorString*`, `indicatorDot*`, `indicatorLine*` | a string for every robot that took a turn, even `""` (reset each round, ≤ 64 chars). Dots and lines one per call, uncapped. All dropped if `show-indicators=false`. | `IR:421-437`, `RCI:1180-1198`, `GM:669-701` |

**Entry order** within a round is chronological (corr.): round-1 HQ grants (exec order), then robot turns (exec order),
then end of round: islands (with healing), destabilize ticks, then per HQ **in hash order** that HQ's damage followed by
its own income. Boost expiry and currents emit nothing (`GW:152-202,650-721`, `IR:439-451`) [measured test1 r5/r10:
income HQ 3 then HQ 2, while turns ran 2 then 3].

### 11.4 Actions

| Action (byte) | Actor ID | Target |
|---|---|---|
| LAUNCH_ATTACK (0), THROW_ATTACK (1) | attacker | victim ID if damage was dealt (lethal too), else `-(x+y*W)-1` (empty, ally, any HQ). A throw empties the carrier with **no CHANGE_\*** entry. (`IR:404-414`, `IC:62-73`) |
| SPAWN_UNIT (2) | HQ | new robot ID (`RCI:717-718`) |
| PICK_UP_RESOURCE (3) | carrier | well location index; the amount is in the paired CHANGE_\* (`RCI:972`) |
| PLACE_RESOURCE (4) | carrier | HQ/well location index, **also for withdrawals** (the sign is in CHANGE_\*) (`RCI:922`) |
| DESTABILIZE (5) | destabilizer | centre location index (`RCI:843-848`) |
| DESTABILIZE_DAMAGE (6) | **never emitted** | – |
| BOOST (7) | booster | its own location index (`RCI:813-819`) |
| BUILD_ANCHOR (8) | HQ | 0 STANDARD, 1 ACCELERATING (`AN:76-78`) |
| PICK_UP_ANCHOR (9) | carrier | take: `hqID*2 + type`; **return: `-(hqID*2+type)-1`** (`RCI:1055-1062,1099-1107`) |
| PLACE_ANCHOR (10) | carrier | island ID; **type not recorded** (STANDARD first if both held) (`RCI:1002-1012`) |
| CHANGE_HEALTH (11) | **the victim/healed robot** | delta after capping. Not emitted for a lethal hit or a zero change. For a non-lethal hit it comes **before** the attacker's entry. (`IR:372-384,404-414`) |
| CHANGE_ADAMANTIUM/MANA/ELIXIR (12/13/14) | robot whose inventory changed | delta, **emitted even when 0** (build costs, death zeroing). A death emits all three, keyed by the dying robot, just before `diedIDs` (`IR:123-145`, `GW:825-831`). |
| DIE_EXCEPTION (15) | robot | -1. Emitted **only** when the sandbox cannot be created at spawn; erased for initial HQs by `clearData` (`PCP:122-146`, `IR:473-476`) |

- Reconstruct inventories by summing CHANGE_\* per robot and **zeroing the thrower on THROW_ATTACK** [measured: the
  team-total identity holds in all 2000 rounds]. Health = `bodyTypeMetadata.health` + Σ CHANGE_HEALTH (UNVERIFIED as a
  run check). Kill credit: use the attacker's entry naming the victim plus `diedIDs`. HQ damage, destabilize ticks and
  anchor heals have **no actor entry** [measured: of 139 deaths in test1, 119 were attributed through an attack entry
  and 20 had no attack trace and sat near an enemy HQ].
- A self-terminated robot (exception, return, `disintegrate`) has no special action. Its last turn's bytecode and
  indicator entries are written, then the three CHANGE_\* zeroing entries, then `diedIDs` (corr.; `GW:214-224,828-831`).
- **Not in the replay:** robot stdout, the shared array, the win reason, cooldowns, carried anchors, the planted anchor
  type, boost/destabilize coverage, and intra-round positions (`GM:505-514,584-616`; `FBS:236-320`).
- test1 (examplefuncsplayer mirror, maptestsmall): A won the tiebreak on **mana 420 vs 17**, although both HQs held
  exactly 40 Ad / 10 Mn. Team A's carriers held 410 Mn. The first two built IDs were 10869 (B launcher, round 8) and 13497
  (A launcher, round 8) (corr.) [measured, `research/rules/replay/output.txt`].

---

## 12. Spec disagreements (the engine wins every one)

| # | Spec says | Engine does | Provenance |
|---|---|---|---|
| 1 | Destabilizer move cooldown 20 (SPEC:199) | **25** (also in the replay header) | `RT:49`; JAR `bipush 25` |
| 2 | `transferAnchor()` (SPEC:178) | does not exist; `takeAnchor`/`returnAnchor`/`placeAnchor` | JAR javap `RobotController` |
| 3 | "Throwing m kg of resource … ⌊5m/4⌋; thrown resources fall into the void" (SPEC:110) | m = **total weight incl. anchors (40 each)**; **everything** is thrown, anchors destroyed, even on a miss or at an ally/HQ; m cannot be chosen | `IC:35-73`, `INV:134-137` |
| 4 | Destabilize "stacks up to 2 (max 2 destabilizers can impact a square)… lasts 5 turns, after which damage is dealt" (SPEC:122) | only the slowdown caps at 2; **every** entry deals 50; damage at the end of round cast+4 to whoever stands there | `GW:351-362,672-688` |
| 5 | Boost "for the next 10 turns" (SPEC:126) | cast round + 9 more (removed at the end of R+9) | `GW:328,663` |
| 6 | "After every turn, cooldowns of all robots are decremented by 10" (SPEC:187) | at the **start of each robot's own turn**, floored at 0; new robots show 10 until then | `IR:425-429` |
| 7 | Currents move robots "at the end of the turn" (SPEC:58) | once per **round**, after all turns and end-of-round damage | `GW:708-710` |
| 8 | Anchor health changes "at the end of each turn" by % occupancy (SPEC:136) | once per **round**, `trunc(100*(own−enemy)/area)` | `ISL:90-103`, `GW:653-656` |
| 9 | "Immediately wins" / "instantly win" (SPEC:66,160) | winner recorded mid-turn, but the round finishes first | `GW:717-720` |
| 10 | HQs "cannot be … destroyed" (SPEC:70,102) | cannot be damaged, but are destroyed by an uncaught exception, return from `run()`, `disintegrate`, `System.exit` or resign | `GW:222-223`, `RCI:1158-1173` |
| 11 | "Unhandled exceptions may paralyze your robot" (SPEC:249) | they **destroy** it at the end of the turn [measured] | `SRP:175-219`, `GW:222-223` |
| 12 | "Throwing any Exceptions cause a penalty of 500" (SPEC:249) | 500 per **handler entered** (catch or finally); an uncaught throw costs 0 but kills | `IMV:623-627` |
| 13 | "Re-running the same match … exactly the same results" (SPEC:216) | unseeded coin flip, StackOverflow depth, leaked identity hashes, CHM order | §9.8 |
| 14 | Robots "run in separate JVMs" (SPEC:96) | one JVM, one class loader per robot (statics are still per robot) | `TeamClassLoaderFactory.java:360-493` |
| 15 | Overrun "resumed at exactly that point next turn" (SPEC:218) | pauses at a block boundary after crossing the limit; overshoot is debt; debt ≥ limit loses turns; an overrun just before `yield` loses a turn | `RM:126-153,286-308` |
| 16 | 8 MB heap per robot (SPEC:269) | no memory limit in the engine | grep of `E/` |
| 17 | Only `Class.forName`, wait/notify, `String.intern` banned; `System` supports only out, arraycopy, getProperty for `bc.testing.` names (SPEC:263) | every `Class` method but `desiredAssertionStatus`, synchronized blocks, `java/lang/invoke`, many `System` methods and method refs are banned; `System` also gives err, in, exit, identityHashCode, setProperty; 15 fake keys return "who knows?" | `IMV:325-332,366-393,535-583`, `E/instrumenter/inject/System.java:52-154` |
| 18 | `java.util`, `java.math`, scala "and their subpackages" are counted (SPEC:273) | packages match exactly (`java.util.concurrent` is illegal); `ConcurrentHashMap` and `Atomic*` are swapped for **free** classes; `java/util/jar`, `zip`, `Iterator`, `TimeUnit` are uninstrumented | `ClassReferenceUtil.java:98-178` |
| 19 | Array creation costs the total array length (SPEC:286) | `max(1,len)`; each multi-dim factor ≥ 1 (`new int[0]` = 1) | `RM:192-215` |
| 20 | Costs as listed in MethodCosts.txt (SPEC:282) | `hashCode`/`toString` are rewritten first → 1 (MapLocation 2→1, MapInfo.toString 15→1) | `IMV:405-428` |
| 21 | `readSharedArray` "for standard Java bytecode costs" (SPEC:184) | flat **2** | `MC:74` |
| 22 | `getBytecodeNum` = bytecodes executed this round (SPEC:243) | `limit − left`: includes carried debt, excludes the unflushed block | `RM:102-104` |
| 23 | World "guaranteed symmetric" (SPEC:46) | never checked at run time (all shipped maps are symmetric) | `SRV:244-439` |
| 24 | Each team has 1-4 HQs (SPEC:70) | validator checks total 2..32 only | `SRV:272-278` |
| 25 | Islands are "groups of connected squares" (SPEC:66) | 4-connected; distinct islands may touch diagonally | `SRV:230-242` |
| 26 | Clouds obscure squares beyond r² 4 (SPEC:60,156) | true for every vision-ruled method, but `senseCloud`/`senseNearbyCloudLocations` see cloud squares at full vision unless the caller is on a cloud | `RCI:392-443` |
| 27 | Cloud slows robots "within" it (SPEC:60) | moves use the **destination** square, actions the current square | `RCI:659-664` |
| 28 | Carriers deposit at headquarters (SPEC:102) | deposits accepted at **either team's** HQ | `RCI:874-897` |
| 29 | Override an own anchor with any type (SPEC:140) | STANDARD over ACCELERATING leaves a permanent −0.15 aura (bug) | `ISL:79-83,104-112` |
| 30 | Upgrade and conversion described separately (SPEC:80) | the upgrade survives conversion (upgraded elixir well); omission | `WELL:40-55` |
| 31 | Tiebreak 2 counts anchors placed "throughout the round" (SPEC:165) | throughout the **game** (`totalAnchorsPlaced`); wording slip | `TI:189` |
| 32 | Turn order unspecified (SPEC:218) | spawn order, initial HQs by map-file ID; omission | `OI:95-111` |
| 33 | Winds "cannot pass through impassable squares" (SPEC:56) | also forbids off-map current destinations and clouds on walls explicitly; HQs/wells on clouds allowed (11/24 maps); omission | `SRV:280-309,422-438` |
| 34 | Spec version 3.0.14 | release jar 3.0.15 (rules identical) | `GC:13` |

**Javadoc / schema-doc disagreements** (not spec): `senseAnchorPlantedHealth` "-1 if no anchor" → returns 0;
`collectResource(-1)` "collect max possible" → exactly the rate, failing if it doesn't fit; `transferResource` "limited by
capacity" → throws, no clamp; `canBuildRobot` omits passability and sensability; `senseNearby*` "no particular order" →
column-major; `senseNearbyIslandLocations` should throw for an unseen island → returns empty; `GameConstants.PASSIVE_*`
"per turn" → every 5 rounds; `MIN_NEAREST_AD_DISTANCE` "minimum" → maximum; `LiveMap.getOrigin` "upper left" → bottom left
(`RCI:374-381,925-950,881-884,689-696`, `GW:462-479`, `RCI:339-358`, `GC:49,77-80`, `LiveMap.java:311-318`). Schema
(`FBS`): `movedIDs` "bodies that moved" → all robots (`FBS:260-263`); `islandTurnoverTurns` "turns occupied" → anchor
health (`FBS:281-282`); attack target "direction" → victim ID or `-(loc)-1` (`FBS:83-86`); `indicatorStringIDs` "robots
who changed" → every robot that took a turn (`FBS:299-302`); "a round may be skipped" → never (`FBS:191-193`); "one
MatchFooter per simulation step" → per match (`FBS:195`); PICK_UP_ANCHOR omits the negative return form (`FBS:101`);
DESTABILIZE_DAMAGE documented but never emitted (`FBS:95-96`); DIE_EXCEPTION "uncaught exception" → only on spawn
failure (`FBS:113-115`); `resourceWellLocs` "wells being given resources" → all wells (`FBS:286`); `maxCorner` "top
corner" → exclusive bound (`FBS:55-56`); README "`.bc22`" → `bc.server.save-file` decides (`schema/README.md:7`).

---

## 13. Surprises: easy-to-get-wrong mechanics

1. **Resources are per HQ.** An HQ can only spend its own stock. Your HQ cannot see the team total that decides the
   tiebreak, which includes carrier cargo (§3.1, §3.5).
2. **HQ action cooldown is 2.** That means 5 builds/anchors per turn from turn 1, and 10 at m ≤ 0.70 (§5.1).
3. **An uncaught exception, returning from `run()`, `disintegrate()` or `System.exit` deletes the robot, HQs included,**
   and the stockpile goes with it. `catch (Throwable)` cannot stop death, StackOverflowError or OOM (§9.5).
4. **A single banned API use poisons the whole team** at class load: robots die, spawns die, and on JDK 8 a surviving
   robot can crash the engine with no replay (§9.6). Calling `getClass().getName()` or using a method ref to
   `MapLocation::distanceSquaredTo` both compile fine.
5. **An overrun just before `Clock.yield()` loses a whole turn.** A large allocation is debt that skips turns. A resumed
   turn is in a new round with stale cached values (§9.4).
6. **Turn order is global spawn order.** New robots act next round, after everyone older, but they are hit by HQ damage,
   destabilize damage, currents and island counting in their spawn round (§4.2).
7. **End-of-round effects read end-of-round positions.** You can step into enemy HQ range, act and step out unharmed.
   Currents push **after** damage and island counting (§4.1).
8. **Destabilize deals nothing on cast.** It deals 50 at the end of round cast+4 to whoever stands there, uncapped per
   stack. Dodge by leaving the r² 15 area (§5.4).
9. **Carrier throw = lose everything,** anchors included, even when it misses. Never "test-throw" (§5.2).
10. **Depositing into an enemy HQ is legal** and gifts it the resources. Check the team (§3.4).
11. **`collectResource(loc, -1)` fails near capacity at an upgraded well.** Amount 0 "succeeds" and wastes the action
    (§5.2).
12. **`takeAnchor` needs a completely empty carrier.** A carrier with an anchor moves once every 2 turns (§3.3).
13. **Moves use the destination square's multiplier;** actions use the current square's (§5.1).
14. **Any cost ≤ 9 allows a second action in the turn.** That covers a boost or accelerating anchor (cd 9) and an
    empty carrier moving (cd 5). Loop on `isActionReady()`/`isMovementReady()` (§5.1).
15. **Conquest is checked only on placement,** needs ceil(0.75N) islands held at once, and the round still finishes
    (§8.3).
16. **The anchors-placed tiebreak counts recaptures;** re-anchoring your own island counts 0 (§8.4).
17. **Island health moves only with net occupancy of the island's own squares, truncated.** One robot on a 1-square
    island swings it by 100 per round. An unoccupied anchor never decays (§8.2).
18. **Spawning needs the target square sensable.** An HQ on a cloud (11 maps) can only spawn within d² 4 (§6.3).
19. **Clouds hide robots beyond r² 4,** but `senseNearbyCloudLocations` maps cloud squares at full range, and
    `senseNearbyMapInfos` silently drops them (§6.1).
20. **Sensing results are column-major, not nearest-first.** `senseNearbyIslands` is HashSet order and costs 200
    (§6.2).
21. **HORIZONTAL symmetry flips y; VERTICAL flips x.** Mirror currents geometrically, not with `opposite()`. Check well
    type (FourNations). Cornucopia is both ROT and HORI (§10.2).
22. **The symmetry is not given,** and round-1 vision settles it on only 10/103 maps (§10.2).
23. **There is no mana guarantee near HQs.** On 67 maps no HQ can sense mana at spawn (§10.3).
24. **Opposing HQs can start 2 squares apart** (BowAndArrow d² 4) (§10.3).
25. **Shared-array writes are immediate** for robots later in the same round. They cost 75 and need range (§7).
26. **`java.util` is charged per JDK instruction** (`HashMap.get` ≈52). `ConcurrentHashMap` is free but has a
    non-deterministic order. `String.charAt` and most `java.lang` calls are free (§9.3).
27. **Static initialisers are paid by every new robot** on its first turn (§9.7).
28. **The STANDARD-over-ACCELERATING anchor bug** leaves a permanent −0.15 aura (§8.2).
29. **The final tiebreak is a non-reproducible coin flip,** and `bc.game.seed` does not seed it (§8.4, §0).
30. **Replay `movedIDs` is every robot, `islandTurnoverTurns` is anchor health, and the win reason is absent** (§11).

---

## Appendix: UNVERIFIED items

- Tournament enforcement of the 8 MB heap rule, and the JDK version used by the official tournament (`java.util` costs
  depend on it; a Java 9+ runtime may fail to instrument with the jar's 2015-era ASM) ([BR] §7, Surprises 19).
- A first `HashMap.put` costing ≈143 as a general figure (§9.3).
- Bytecode cost of an `int[]` literal (~5 per element) (§9.7).
- Health reconstruction from CHANGE_HEALTH; attributing the 20 trace-less deaths in test1 to HQ damage; a killed JVM
  leaving no replay (§11).
- The STANDARD-over-ACCELERATING aura bug (§8.2) and the alternate-order and 75%-in-same-round edge cases are code-derived,
  not run-tested.
- Tournament labels of maps (from the client table) and official server settings (validate-maps, alternate-order)
  ([MP] §7).
- The round-1 symmetry model is an analysis model, not an engine fact ([MP] §2).
