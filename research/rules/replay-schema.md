# Battlecode 2023 (Tempest): the replay file (.bc23), engine-verified

Area: **replay-schema**. The engine is the source of truth. Release in use: `battlecode23-3.0.15.jar`.

## Provenance conventions

- `ENG/` = `/home/terryvanbelle/projects/vibe/reference/battlecode23/engine/src/main/battlecode/` (git master).
- `FBS:n` = line n of `/home/terryvanbelle/projects/vibe/reference/battlecode23/schema/battlecode.fbs`.
- `SREADME:n` = line n of `/home/terryvanbelle/projects/vibe/reference/battlecode23/schema/README.md`.
- `SPEC:n` = line n of `/home/terryvanbelle/projects/vibe/reference/battlecode23/specs/specs.md.html`.
- `JAR` = `/home/terryvanbelle/projects/vibe/2023/engine/battlecode23-3.0.15.jar`, disassembled with
  `~/jdk/jdk8u504-b01/bin/javap -c -p -constants`.
- `READER` = `/home/terryvanbelle/projects/vibe/2023/research/rules/replay/ReplayReader.java` (my reader) and
  `OUT` = its output on `matches/test1.bc23`, saved at `research/rules/replay/output.txt`.
- **Source and jar match for everything cited here.** I checked these in the jar:
  - `GameMaker$MatchMaker`: the method list, the `makeMatchHeader` → `clearData` order, the `makeRound` logger reset,
    and the `addIndicatorString` `showIndicators` guard.
  - `GameMaker.toBytes`: GZIP.
  - `GameWorld`: constructor order (`spawnRobot` before `makeMatchHeader`), and the call sequences of
    `processEndOfRound` and `runRound`.
  - `RobotControllerImpl`: the action byte constants and target arithmetic of `buildRobot`, `buildAnchor`, `boost`,
    `destabilize`, `transferResource`, `collectResource`, `placeAnchor`, `takeAnchor` and `returnAnchor`.
  - `InternalCarrier.emptyResources`: it makes no `addAction` call.
  - `InternalRobot.addHealth` and `processEndOfTurn`.
  - The `battlecode.schema.Action`, `BodyType` and `Event` constants.
  - `GameConstants.SPEC_VERSION` and the `PASSIVE_*` constants.
  - The `Config` default `bc.engine.show-indicators=true`.

  Where I cite a source line, the jar has the same code.
- **[measured]** means I observed it by decoding `test1.bc23` with the reader. Anything I did not verify in code or
  data is marked **UNVERIFIED**.

The test replay `test1.bc23` is examplefuncsplayer against itself on `maptestsmall` (20x20). It ran the full 2000
rounds and team A (id 1) won (`OUT` lines 3-16, 76-77).

---

## 1. Container

1. **The file is GZIP-compressed.** `GameMaker.toBytes()` builds one FlatBuffer, finishes it with a `GameWrapper` root,
   takes `sizedByteArray()` and pipes it through `java.util.zip.GZIPOutputStream` (`ENG/server/GameMaker.java:160-190`).
   `writeGame` writes those bytes as they are (`GameMaker.java:197-207`). **[measured]** `file test1.bc23` reports "gzip
   compressed data, original size 7025880". The file is 821,251 bytes on disk and 7,025,880 bytes gunzipped (`OUT`:1),
   about 3.5 KB per round with up to 67 robots.
2. **The whole game is held in memory until the end.** Every event goes into the same `fileBuilder`. The file is
   written once, after the last match of the game (`GameMaker.java:63, 214-228`; `ENG/server/Server.java:208-209`).
   A crashed or killed engine leaves no replay. **UNVERIFIED** (by experiment) for a killed JVM, but it follows from
   the code.
3. **The file name and extension come from `bc.server.save-file`** (`ENG/server/Main.java:59-65`). The default is
   `match.rms` (`ENG/server/Config.java:45`). The `.bc23` extension is a convention. Our runner passes it in
   `tools/lib.sh` `run_game`.
4. **The root table is `GameWrapper`**, with `events: [EventWrapper]`, `matchHeaders: [int]` and `matchFooters: [int]`
   (`FBS:344-351`). The two int vectors hold indices into `events` (`GameMaker.java:451, 502`). **[measured]** test1
   has 2004 events, `matchHeaders=[1]` and `matchFooters=[2002]` (`OUT`:2).
5. **`EventWrapper` is a union wrapper.** Its `eType()` is a `battlecode.schema.Event` byte: NONE=0, GameHeader=1,
   MatchHeader=2, Round=3, MatchFooter=4, GameFooter=5. `e(Table)` fills the table you pass in (`FBS:186-198, 334-336`;
   JAR `battlecode.schema.Event` constants).
6. **Event order.** GameHeader comes first. Each match then has MatchHeader, Round × N and MatchFooter. GameFooter
   comes last. The state machine enforces this order (`GameMaker.java:38-55, 139-152, 237-239, 315-316, 441-442,
   456-457, 505-506`). One file can hold **several matches**, one per map in `bc.game.maps`
   (`Server.java:177-206`).
7. **Every round is written, and none is skipped.** `GameWorld.runRound()` always ends with
   `matchMaker.makeRound(currentRound)` after a successful round (`ENG/world/GameWorld.java:199-201`). **[measured]**
   `roundID` runs 1..2000 with no gaps (`OUT` check "roundID increments by 1": 0 violations).
8. **The last round is written, then the footer.** The round in which a winner is set is still written. The *next*
   `runRound()` call writes the MatchFooter and plays no round (`GameWorld.java:152-163, 188-201`). The footer's
   `totalRounds` = `currentRound` = the last `roundID` (**[measured]**, `OUT` check).
9. **Exception path.** If `runRound` catches an engine exception, it returns DONE without writing that round or a
   footer (`GameWorld.java:194-198`). The GameMaker state check would then throw at the next MatchHeader or GameFooter
   (`GameMaker.java:139-152`). **UNVERIFIED** at runtime. This is an engine-bug path, not a player-bug path.

## 2. GameHeader (one per file)

Written by `GameMaker.makeGameHeader()` (`GameMaker.java:237-280`).

10. **`specVersion` = `GameConstants.SPEC_VERSION` = `"3.0.14"`**, even in the 3.0.15 jar (`GameMaker.java:242`;
    `ENG/common/GameConstants.java:13`; JAR `javap -constants`). **[measured]** `OUT`:3.
11. **`teams`** has two `TeamData` entries: (name, packageName, teamID). Team A has teamID **1** and team B has
    teamID **2** (`GameMaker.java:244-262`; `ENG/util/TeamMapping.java:16-18`: NEUTRAL=0, A=1, B=2). The same mapping
    is used for every team field in the file, including island ownership (§5).
12. **`bodyTypeMetadata`** has one entry per `RobotType`, copied straight from the enum: build costs Ad/Mn/Ex, action
    and movement cooldown, health, action and vision radius², bytecode limit (`GameMaker.java:282-303`). **[measured]**
    `OUT`:6-11. These are raw enum fields, not effective game values:
    - CARRIER `movementCooldown` = 0. The real value is computed from weight (`ENG/world/InternalRobot.java:332-339`).
    - HEADQUARTERS health = 1 (`ENG/common/RobotType.java:21`), but HQs cannot be damaged (`InternalRobot.java:373-375`).
    - -1 is a "not applicable" sentinel (HQ move, BOOSTER/AMPLIFIER action radius, AMPLIFIER action cooldown).
    - DESTABILIZER `movementCooldown` = **25** (`RobotType.java:49`). See Spec disagreements.
13. **`constants`** holds increasePeriod=5, AdAdditiveIncrease=6 and MnAdditiveIncrease=6. The writer **swaps** the two
    increase constants: `addMnAdditiveIncrease(PASSIVE_AD_INCREASE)` and `addAdAdditiveIncrease(PASSIVE_MN_INCREASE)`
    (`GameMaker.java:266-268`). Both are 6 (JAR `GameConstants`: `PASSIVE_AD_INCREASE = 6`, `PASSIVE_MN_INCREASE = 6`),
    so the swap is harmless in 3.0.15. **[measured]** `OUT`:12.

## 3. MatchHeader and GameMap (one per match)

Written by `MatchMaker.makeMatchHeader(LiveMap)`, which calls `GameMapIO.Serial.serialize`
(`GameMaker.java:441-454`; `ENG/world/GameMapIO.java:262-332`).

14. **`maxRounds` = `gameMap.getRounds()`**. For maps loaded from file this is always `GAME_MAX_NUMBER_OF_ROUNDS` = 2000
    (`GameMapIO.java:228`). **[measured]** `OUT`:13.
15. **Map geometry.** `minCorner` = origin. **`maxCorner` = origin + (width, height), which is exclusive**
    (`GameMapIO.java:320-322`), so `width = maxCorner.x - minCorner.x` (`GameMapIO.java:223-224`). **[measured]** test1
    has min=(0,0) and max=(20,20), so it is 20x20 (`OUT`:13).
16. **Per-tile arrays** (`walls: [bool]`, `clouds: [bool]`, `currents: [int]`, `islands: [int]`, `resources: [int]`)
    have length width·height and are **indexed `x + y*width`** (`GameMapIO.java:284-290`; the engine's
    `locationToIndex` is `x - origin.x + (y - origin.y)*width`, `GameWorld.java:309-311`). Encodings:
    - `currents[i]` is an index into `Direction.DIRECTION_ORDER = {CENTER, WEST, NORTHWEST, NORTH, NORTHEAST, EAST,
      SOUTHEAST, SOUTH, SOUTHWEST}` (`ENG/common/Direction.java:55`; used at `GameWorld.java:72-74`).
    - `islands[i]`: 0 = no island, otherwise the island ID (`GameWorld.java:96-104`).
    - `resources[i]` is the **initial** well type: 0 none, 1 Ad, 2 Mn, 3 Ex (`ENG/common/ResourceType.java:4-7`;
      `GameWorld.java:114-122`).
    - `symmetry` is the `MapSymmetry` ordinal: 0 ROTATIONAL, 1 HORIZONTAL, 2 VERTICAL (`ENG/world/MapSymmetry.java:6-10`).
17. **`randomSeed` = `gameMap.getSeed()`** (`GameMapIO.java:264, 325`). With our engine patch
    (`2023/engine/patch-src/battlecode/world/LiveMap.java:308`, `Integer.getInteger("bc.game.seed", seed)`), the
    replay records the **overridden** seed whenever `GAME_SEED` is set. The seed also drives robot ID assignment (#43).
18. **`bodies` (a SpawnedBodyTable) holds the initial HQs, and only there.** The constructor of `GameWorld` spawns the
    map's HQs with `spawnRobot`, which calls `matchMaker.addSpawnedRobot` (`GameWorld.java:84-90, 802`). Then
    `makeMatchHeader` calls `clearData()`, which **discards** those spawn records (`GameWorld.java:111`;
    `GameMaker.java:453, 716-760`). **[measured]** Round 1 has `spawned=0`. The two HQs are listed only under the
    MatchHeader (`OUT`:15-16, 24). Initial HQ IDs come from the map file and are small (2 and 3 in test1). Only HQs
    are kept from a map's bodies (`GameMapIO.java:338-356`).
19. **With `bc.server.alternate-order=true`**, teams are swapped at map load, so the header's bodies already show the
    swapped teams (`GameMapIO.java:347-349`; `Server.java:180-181`). The default is false (`Config.java:53`).

## 4. Round: what is recorded, and when

Every field of every Round is filled from the `MatchMaker` buffers. These buffers are appended to while the round
runs and cleared after each `makeRound` (`GameMaker.java:505-622, 716-760`). Arrays inside a Round are in
**chronological append order**:

1. Round-1 HQ grants.
2. Robot turns, in execution order.
3. End-of-round effects (`GameWorld.java:152-202, 650-721`).

| Field(s) | Written by | Content and semantics |
|---|---|---|
| `roundID` | `makeRound(currentRound)` (`GameMaker.java:614`) | 1-based. Round 0 is the MatchHeader state (`FBS:322-325`). |
| `teamIDs`, `teamAdChanges`, `teamMnChanges`, `teamExChanges` | `processEndOfRound` → `addTeamInfo` for A, then B (`GameWorld.java:703-704`; `GameMaker.java:662-667`) | **This round's change** in the team totals (`ENG/world/TeamInfo.java:215-234`). It is a delta, not a stock. The totals are the **sum of all living robots' inventories, HQs and carriers** (#22). |
| `movedIDs`, `movedLocs` | `processEndOfRound` loops **every living robot** (`GameWorld.java:712-715`) | **The end-of-round position of every robot, every round**, after currents (`GameWorld.java:707-710`). It is not "robots that moved". The order is hash order (`ENG/world/ObjectInfo.java:81-84`). |
| `spawnedBodies` (robotIDs, teamIDs, types, locs) | `GameWorld.spawnRobot` → `addSpawnedRobot` (`GameWorld.java:788-804`; `GameMaker.java:708-714`) | Robots built this round, at their build location. Each one also has a `SPAWN_UNIT` action from the HQ. |
| `diedIDs` | `GameWorld.destroyRobot` → `addDied` (`GameWorld.java:815-832`) | Every removal: killed, self-terminated, or resigned. **The cause is not recorded.** |
| `actionIDs`, `actions`, `actionTargets` | see §5 | Parallel arrays, one entry per event. IDs may repeat. |
| `islandIDs`, `islandOwnership`, `islandTurnoverTurns` | `processEndOfRound` → `island.advanceTurn()` then `addIslandInfo`, for **every island, every round** (`GameWorld.java:653-656`; `GameMaker.java:656-660`) | Ownership is `Island.getTeamInt()`: 0 neutral, 1 A, 2 B (`ENG/world/Island.java:35-46`). **`islandTurnoverTurns` is `Island.getHealth()` = the anchor's health** (`Island.java:56-58`). It is 0 when neutral, at most 250 (STANDARD) or 750 (ACCELERATING) (`ENG/common/Anchor.java:16, 21`; `Island.java:84, 103`). Recorded after this round's anchor decay or regeneration. |
| `resourceWellLocs`, `resourceID`, `wellAccelerationID`, `wellAdamantiumValues`, `wellManaValues`, `wellElixirValues` | `processEndOfRound` → `addWell` for **every well, every round**, in ascending location index (`GameWorld.java:698-702`; `GameMaker.java:647-654`) | `resourceWellLocs` = `x + y*width`. `resourceID` = the **current** type (1/2/3). A Mn or Ad well turns into Elixir once enough of the other resource is deposited (`ENG/world/Well.java:38-57`). `wellAccelerationID` = 1 once upgraded (`Well.java:43-45, 53-55, 61-63, 94-96`). The `well*Values` are the amounts **deposited into** the well by `transferResource`. Mining never decrements them (`ENG/world/RobotControllerImpl.java:961-973` does not touch the well's inventory), so they only grow. |
| `indicatorStringIDs`, `indicatorStrings` | `InternalRobot.processEndOfTurn` → `addIndicatorString` for **every robot that took a turn** (`InternalRobot.java:431-437`) | The string is reset to `""` at the start of every round (`InternalRobot.java:421-423`) and truncated to 64 chars (`RobotControllerImpl.java:1180-1185`; JAR `INDICATOR_STRING_MAX_LENGTH = 64`). Empty strings are recorded too. Dropped if `showIndicators` is false (`GameMaker.java:669-675`). |
| `indicatorDotIDs`, `indicatorDotLocs`, `indicatorDotRGBs` | `rc.setIndicatorDot` → `addIndicatorDot`, one entry **per call** (`RobotControllerImpl.java:1187-1191`; `GameMaker.java:677-687`) | No count cap and no colour or location validation, apart from a null check. |
| `indicatorLineIDs`, `indicatorLineStartLocs`, `indicatorLineEndLocs`, `indicatorLineRGBs` | `rc.setIndicatorLine` → `addIndicatorLine`, per call (`RobotControllerImpl.java:1193-1198`; `GameMaker.java:689-701`) | Same as dots. |
| `bytecodeIDs`, `bytecodesUsed` | `processEndOfTurn` → `addBytecodes` (`InternalRobot.java:433`), with the value from `GameWorld.updateRobot` (`GameWorld.java:217`) | One entry per robot that took a turn. The value is `RobotMonitor.getBytecodeNum()` = `limit - bytecodesLeft` at pause time (`PlayerControlProvider.java:181-191`; `ENG/instrumenter/inject/RobotMonitor.java:102-104`). **`bytecodesUsed >= limit` means the turn was cut off (an overrun).** A turn that ends in `Clock.yield()` pauses with `bytecodesLeft > 0` (`ENG/common/Clock.java:24-26`; `RobotMonitor.java:126-150`). |

Facts behind the table:

20. **Robots built this round take no turn this round.** The exec order is snapshotted before the loop
    (`ObjectInfo.java:95-110`), so a robot built mid-round has no `bytecodeIDs` or `indicatorStrings` entry until the
    next round. It does appear in that round's `movedIDs`. **[measured]** 0 violations of "robot spawned this round is
    absent from bytecodeIDs". `indicatorStringsLength == bytecodeIDsLength` in all 2000 rounds.
21. **[measured] Positions.** `movedIDsLength` equals the number of living robots in every one of 2000 rounds (`OUT`
    check "movedIDs == all living robots"). The robot table can be rebuilt from MatchHeader bodies plus
    spawned/died/moved alone.
22. **Team totals include carried cargo.** `InternalRobot.addResourceAmount` updates **both** the robot's inventory and
    `TeamInfo` (`InternalRobot.java:141-145`). `destroyRobot` subtracts a dying robot's whole inventory
    (`GameWorld.java:828-830`). A carrier's throw empties it through `TeamInfo.addResource`
    (`ENG/world/robots/InternalCarrier.java:35-45`). So the team total = Σ inventories of living robots of that team.
    **[measured]** The cumulative sum of `teamXxChanges` equals Σ reconstructed inventories, for both teams, in all
    2000 rounds (`OUT` check "team totals == sum of living robots' inventories").
23. **The rc API reports per-HQ resources, not the team total.** `rc.getResourceAmount` returns `this.robot.getResource`
    (`RobotControllerImpl.java:131-133`). The team total in the replay differs from what any HQ can see.
    **[measured]** At round 2000, team A total Mn = 420, but its HQ holds 10 and carriers hold 410 (`OUT`:65).
24. **Indicator strings take up space.** **[measured]** test1 has 31,592 empty and 64,281 non-empty indicator
    entries.

## 5. Actions: who emits them, the actor ID, the target encoding

`MatchMaker.addAction(userID, action, target)` appends to the three parallel arrays (`GameMaker.java:641-645`).
`battlecode.schema.Action` byte values come from the JAR (`javap -constants`).

| Action (byte) | Emitted at | `actionIDs[i]` is | `actionTargets[i]` |
|---|---|---|---|
| LAUNCH_ATTACK (0) | `InternalRobot.attack` (`InternalRobot.java:404-414`) | the launcher | **the victim's robot ID** when damage was dealt; otherwise **`-(x + y*width) - 1`** (empty tile, ally, or any HQ; the attack "succeeds" with no damage) |
| THROW_ATTACK (1) | `InternalCarrier.attack` (`InternalCarrier.java:62-73`) | the carrier | same encoding as LAUNCH_ATTACK. Then **the whole inventory (resources and anchors) is emptied with no CHANGE_* action** (`InternalCarrier.java:35-45, 72`) |
| SPAWN_UNIT (2) | `buildRobot` (`RobotControllerImpl.java:708-719`) | the HQ | the new robot's ID. **[measured]** always present in the same round's `spawnedBodies` |
| PICK_UP_RESOURCE (3) | `collectResource` (`RobotControllerImpl.java:961-973`) | the carrier | well location `x + y*width`. **The amount is not here** but in the paired CHANGE_* entry |
| PLACE_RESOURCE (4) | `transferResource` (`RobotControllerImpl.java:909-923`) | the carrier | location of the HQ or well. **A negative amount (taking from an HQ) is also recorded as PLACE_RESOURCE**; the sign shows only in the CHANGE_* entries |
| DESTABILIZE (5) | `destabilize` (`RobotControllerImpl.java:843-848`) | the destabilizer | centre location index |
| DESTABILIZE_DAMAGE (6) | **never emitted.** No call site outside `schema/` (grep of `ENG/`) | – | – |
| BOOST (7) | `boost` (`RobotControllerImpl.java:813-819`) | the booster | the booster's own location index |
| BUILD_ANCHOR (8) | `buildAnchor` (`RobotControllerImpl.java:746-757`) | the HQ | 0 = STANDARD, 1 = ACCELERATING (`Anchor.java:76-78`) |
| PICK_UP_ANCHOR (9) | `takeAnchor` (`RobotControllerImpl.java:1055-1062`) **and `returnAnchor`** (`RobotControllerImpl.java:1099-1107`) | the carrier | take: `hqID*2 + type`. **Return: `-(hqID*2 + type) - 1`** |
| PLACE_ANCHOR (10) | `placeAnchor` (`RobotControllerImpl.java:1002-1012`) | the carrier | **the island ID only. The anchor type is not recorded** (the carrier places STANDARD first if it holds both, `InternalRobot.java:155-163`) |
| CHANGE_HEALTH (11) | `InternalRobot.addHealth` (`InternalRobot.java:372-384`) | **the robot whose health changed (the victim or the healed robot), not the attacker** | the delta (after capping at max health). **Not emitted when the change is lethal** (the robot is destroyed instead), and not emitted for a delta of 0 |
| CHANGE_ADAMANTIUM / CHANGE_MANA / CHANGE_ELIXIR (12/13/14) | `InternalRobot.addResourceAmount` → `addResourceChangeAction` (`InternalRobot.java:123-145`) | **the robot whose inventory changed** (HQ or carrier) | the delta. **Emitted even when it is 0** |
| DIE_EXCEPTION (15) | `InternalRobot.die_exception` (`InternalRobot.java:473-476`), called **only when the player sandbox cannot be created at spawn** (`ENG/world/control/PlayerControlProvider.java:122-145`) | the robot | -1 |

Facts behind the table:

25. **Inventory reconstruction recipe:** start every robot at 0 and add its CHANGE_* deltas. **On THROW_ATTACK, zero
    the thrower.** **[measured]** With this rule, every dying robot is at exactly 0 when it appears in `diedIDs`, and
    the team-total identity of #22 holds in every round (`OUT` checks).
26. **Sources of CHANGE_* entries:**
    - Round-1 grant: +200 Ad and +200 Mn on each HQ, before any turn (`GameWorld.java:169-183`).
    - Build costs: one entry per resource type, including 0-cost types (`RobotControllerImpl.java:712-716, 750-754`).
    - Mining, transfers (both the carrier and the HQ get entries), and death (`GameWorld.java:828-830`).
    - Passive income: **+6 Ad and +6 Mn on each HQ** every 5 rounds (`InternalRobot.java:439-449`), so income scales
      with the number of HQs.

    **[measured]** 720 zero-delta CHANGE_* entries in test1. Round 1 shows +200 then -80 Ad, +200 then -80 Mn, and
    0 Ex per HQ for its STANDARD anchor (`OUT`:21-23, 80-84).
27. **Damage with no attacker action:** HQ end-of-round damage (4 per round to every enemy within r² ≤ 9,
    `InternalRobot.java:440-443`; `RobotType.java:21`), destabilizer ticks (`GameWorld.java:672-688`) and anchor
    healing (`Island.java:113-118`). These appear only as CHANGE_HEALTH on the affected robot, or only in `diedIDs`
    when lethal. **[measured]** Of 139 deaths in test1, 119 have one more robot-target hit than negative CHANGE_HEALTH
    entries in their death round (the lethal hit leaves no CHANGE_HEALTH). The other 20 have none of either and were
    all within one step of r² ≤ 9 of an enemy HQ, so they were killed by HQ damage. Calling it HQ damage is an
    inference from position, consistent with the code.
28. **Health is reconstructable** as `bodyTypeMetadata.health` + Σ CHANGE_HEALTH. Death is read from `diedIDs`, not
    from health reaching 0. **UNVERIFIED** as a run-time check (the reader does not track health).
29. **Self-termination leaves no action.** A robot whose `run()` throws, returns, or calls `disintegrate()` is
    terminated, then destroyed at the end of its own turn (`ENG/instrumenter/SandboxedRobotPlayer.java:180-206`;
    `PlayerControlProvider.java:194-201`; `GameWorld.java:222-223`). It appears only in `diedIDs` (its turn's bytecode
    and indicator entries are still written first, `GameWorld.java:217-218`). `resign()` destroys every robot of the
    team, so all appear in `diedIDs` (`RobotControllerImpl.java:1164-1173`).

## 6. Footers

30. **MatchFooter** holds `winner` (TeamMapping byte), `totalRounds` and `profilerFiles` (`GameMaker.java:456-503`).
    `profilerFiles` has entries only when `bc.engine.enable-profiler=true`: one ProfilerFile per team, A then B, each
    with method-name `frames` and one `ProfilerProfile` per robot (`GameWorld.java:154-161`; `GameMaker.java:460-496`;
    the default is false, `Config.java:65`). **[measured]** test1 has `winner=1`, `totalRounds=2000` and
    `profilerFiles=0` (`OUT`:76).
31. **GameFooter** holds `winner` = A if `aWins >= bWins`, otherwise B (`Server.java:207-208`). **A tie in match wins
    goes to A.** This only matters for files with several maps.
32. **The reason for the win (`DominationFactor`) is not stored anywhere in the file.** It is only printed to stdout
    (`Server.java:584-620+`). You can derive it:
    - `totalRounds < 2000` means conquest or resignation.
    - Otherwise apply the tiebreak chain (`GameWorld.java:637-647`) to the last Round: islands owned, then anchors
      placed (count PLACE_ANCHOR on islands the team did not already own, `Island.java:76, 85-87`), then the team
      totals of Ex, Mn and Ad.
    - **[measured]** test1: islands 0-0, anchors placed 0-0, Ex 0-0, **Mn 420 vs 17**, so A won on mana (`OUT`:65-66).
      **Both HQs held exactly 40 Ad and 10 Mn. The game was decided by carrier-held mana.**

## 7. What is NOT in the replay

33. **Robot `System.out` output.** It goes into `MatchMaker.logger`, which `makeRound` resets each round without
    writing it. The write is commented out (`GameMaker.java:508-514`; JAR `makeRound` bytecode 10-36 shows
    `flush` then `reset`). The schema comment says "logs have been replaced with indicator strings" (`FBS:320`).
34. **The shared array.** `writeSharedArray` makes no MatchMaker call (`RobotControllerImpl.java:1147-1150`).
35. **Absolute health, cooldowns, carrier weight, held anchors, boost/destabilize coverage and expiry, active cooldown
    multipliers, and the anchor type planted on an island.** Some of these are inferable: anchors from
    BUILD/PICK_UP/PLACE actions, zones from the action's centre plus `GameConstants` radii and durations.
36. **Movement within a round.** Only end-of-round positions are stored (#21). A robot that moves twice in one turn,
    or is pushed by a current, shows only its final tile. Current pushes have no action.
37. **The win reason** (#32) and **map validation** results.

## 8. Reading it: generated classes and the API that worked

38. **Everything needed is inside the engine jar.** `battlecode/schema/*.class` has 21 classes (Action, BodyType,
    BodyTypeMetadata, Constants, Event, EventWrapper, GameFooter, GameHeader, GameMap, GameWrapper, MatchFooter,
    MatchHeader, ProfilerEvent, ProfilerFile, ProfilerProfile, RGBTable, Round, SpawnedBodyTable, TeamData, Vec,
    VecTable). The `com/google/flatbuffers/*` runtime is there too (`unzip -l` of JAR). The classpath is just the jar.
    Generated sources: `ENG/schema/*.java`, identical to `schema/java/battlecode/schema/*.java` (`diff -q Round.java`
    is empty).
39. **Exact calls used in `READER`**, all of which worked on the 3.0.15 jar under JDK 8:

```java
// gunzip (java.util.zip) -> one flatbuffer
byte[] raw = readAll(new GZIPInputStream(new FileInputStream(path)));            // READER:41-49
GameWrapper gw = GameWrapper.getRootAsGameWrapper(ByteBuffer.wrap(raw));         // READER:66
gw.eventsLength(); gw.matchHeaders(j); gw.matchFooters(j);
EventWrapper ew = new EventWrapper();
for (int i = 0; i < gw.eventsLength(); i++) {
    gw.events(ew, i);                                                            // READER:75
    switch (ew.eType()) {                                                        // byte, battlecode.schema.Event.*
    case Event.GameHeader:  GameHeader gh = (GameHeader) ew.e(new GameHeader());  // specVersion(), teams(k).teamID()/name()/packageName(),
                            // bodyTypeMetadata(k).type()/health()/bytecodeLimit()/..., constants().increasePeriod()
    case Event.MatchHeader: MatchHeader mh = (MatchHeader) ew.e(new MatchHeader()); GameMap m = mh.map();
                            // m.minCorner().x(), m.maxCorner().x(), m.walls(i), m.islands(i), m.resources(i), m.currents(i),
                            // m.bodies().robotIDs(k)/teamIDs(k)/types(k), m.bodies().locs().xs(k)/ys(k), mh.maxRounds()
    case Event.Round:       Round r = (Round) ew.e(new Round());                 // READER:133
                            // r.roundID(); r.spawnedBodies().robotIDs(k)/teamIDs(k)/types(k)/locs().xs(k)
                            // r.diedIDs(k); r.movedIDs(k); r.movedLocs().xs(k)/ys(k)
                            // r.actionIDs(k), r.actions(k) (byte), r.actionTargets(k)
                            // r.teamIDs(k), r.teamAdChanges(k), r.teamMnChanges(k), r.teamExChanges(k)
                            // r.islandIDs(k), r.islandOwnership(k), r.islandTurnoverTurns(k)
                            // r.resourceWellLocs(k), r.resourceID(k), r.wellAccelerationID(k), r.wellAdamantiumValues(k)...
                            // r.bytecodeIDs(k), r.bytecodesUsed(k); r.indicatorStringIDs(k), r.indicatorStrings(k)
                            // r.indicatorDotIDs(k), r.indicatorDotLocs().xs(k), r.indicatorDotRGBs().red(k) ...
                            // every vector has a matching xxxLength()
    case Event.MatchFooter: MatchFooter mf = (MatchFooter) ew.e(new MatchFooter()); // winner(), totalRounds(), profilerFilesLength()
    case Event.GameFooter:  GameFooter gf = (GameFooter) ew.e(new GameFooter());    // winner()
    }
}
BodyType.name(int); Action.name(int);   // enum names from the generated classes
```

    Build and run with `research/rules/replay/run.sh [file] [rounds]`. It does `javac -source 8 -target 8 -cp JAR` and
    then `java -cp classes:JAR ReplayReader`. It runs in about 19 s wall on the loaded driver, 7 s CPU. The reader
    resets its state at each MatchHeader, because robot IDs restart in every match (#43).
40. **[measured] Output for rounds 1, 100, 500 and 2000 of test1** (`OUT`:18-75; counts are at end of round):

| Round | Team A robots (HQ/Car/Lau) | Team B robots (HQ/Car/Lau) | Team A Ad/Mn/Ex total (HQ + carried) | Team B Ad/Mn/Ex total | Actions this round |
|---|---|---|---|---|---|
| 1 | 1/0/0 | 1/0/0 | 120/120/0 (120/120 + 0/0) | 120/120/0 | BUILD_ANCHOR 1+1, CHANGE_AD 2+2, CHANGE_MN 2+2, CHANGE_EX 1+1 |
| 100 | 1/3/3 | 1/3/3 | 26/25/0 (10/25 + 16/0) | 36/55/0 (10/25 + 26/30) | LAUNCH_ATTACK 3+2, PICK_UP_RESOURCE 1+0, CHANGE_AD 2+1, CHANGE_MN 1+1 |
| 500 | 1/8/13 | 1/7/10 | 95/22/0 (40/10 + 55/12) | 139/74/0 (40/10 + 99/64) | LAUNCH_ATTACK 12+10, PICK_UP_RESOURCE 1+3, CHANGE_AD 1+3, CHANGE_MN 2+2, CHANGE_HEALTH 0+1 |
| 2000 | 1/31/28 | 1/1/5 | 441/420/0 (40/10 + 401/410) | 46/17/0 (40/10 + 6/7) | LAUNCH_ATTACK 28+5, PICK_UP_RESOURCE 7+0, CHANGE_AD 4+1, CHANGE_MN 5+1 |

    No amplifiers, destabilizers or boosters were built. Six islands were neutral throughout. There were 20 wells
    (10 Ad, 10 Mn), none upgraded. Whole-match action totals: LAUNCH_ATTACK 50,553; PICK_UP_RESOURCE 9,634;
    CHANGE_AD 6,520; CHANGE_MN 5,412; CHANGE_HEALTH 1,776; CHANGE_EX 347; THROW_ATTACK 320; SPAWN_UNIT 204;
    BUILD_ANCHOR 4; no PLACE_ANCHOR, PLACE_RESOURCE, PICK_UP_ANCHOR, BOOST, DESTABILIZE or DIE_EXCEPTION (`OUT`:90-105).
    examplefuncsplayer never transfers resources, which is why PLACE_RESOURCE is absent. All 18 consistency checks
    pass with 0 violations (`OUT`:107-125).

## 9. Run-time configuration that changes the file

41. **`bc.engine.show-indicators`** (default **true**, `Config.java:66`; read at `Server.java:160`). When false,
    indicator strings, dots and lines are all omitted. Bytecodes are still recorded. Our `run_game` passes `true`.
42. **`bc.server.websocket`** (default **true**, `Config.java:33`). When on, every event is built a second time into a
    `packetBuilder` and sent over a websocket on port 6175 (`GameMaker.java:113-121, 219-227`; `Server.java:131-137`).
    This does not change the file. Our `run_game` does not turn it off. A sibling report, `bytecode-runtime.md` §9,
    measured that a busy port gives an NPE but the match still writes its replay. I did not re-verify that here.
43. **Robot IDs.** Built robots get IDs ≥ 10001 drawn from shuffled blocks of 4096, seeded by the map seed
    (`ENG/world/IDGenerator.java:16-21, 48-53, 73-90`; `GameWorld.java:63`). Initial HQs keep their map-file IDs. IDs
    restart in every match (a new `GameWorld` per match, `Server.java:464`). **[measured]** First built IDs in test1:
    10869, 11039, …

---

## Spec disagreements

The game spec (`specs.md.html`) says almost nothing about the replay. Its only pointers are "Debugging" (`SPEC:237-239`)
and the bytecode text. Most disagreements are with the schema's own documentation (`battlecode.fbs` comments and the
schema README), which is the de facto replay spec. The engine wins every case.

1. **`movedIDs` "The IDs of bodies that moved"** (`FBS:260-263`). The engine lists **every living robot** every round
   (`GameWorld.java:712-715`; [measured]).
2. **`islandTurnoverTurns` "The number of turns the opposing team has been occupying each island"** (`FBS:281-282`).
   The engine writes the **anchor health** (`GameMaker.java:658`; `Island.java:56-58`).
3. **LAUNCH_ATTACK and THROW_ATTACK "Target: ID for direction in which attack occurs"** (`FBS:83-86`). The engine
   writes the **victim robot ID**, or `-(locIndex)-1` when no damage is dealt (`InternalRobot.java:406-413`;
   `InternalCarrier.java:64-71`; [measured]).
4. **`indicatorStringIDs` "robots who changed their indicator strings"** (`FBS:299-302`). The engine writes one entry
   for **every robot that took a turn**, including `""` (`InternalRobot.java:431-437`; [measured]: 31,592 empty
   entries).
5. **"A round may be skipped if nothing happens during its time"** (`FBS:191-193`). The engine writes every round
   (`GameWorld.java:199-201`; [measured] contiguous 1..2000).
6. **"There should be one MatchFooter at the end of each simulation step"** (`FBS:195`). There is one per **match**
   (`GameWorld.java:153-162`).
7. **PICK_UP_ANCHOR "Target: (Robot id picked up from)*2 + (ANCHOR type)"** (`FBS:101`). The doc leaves out the
   **negative form for `returnAnchor`**: `-(hqID*2 + type) - 1` (`RobotControllerImpl.java:1106`).
8. **DESTABILIZE_DAMAGE** is documented (`FBS:95-96`) but **never emitted**. Destabilize ticks show up as CHANGE_HEALTH
   (`GameWorld.java:676-680`; `InternalRobot.java:382`).
9. **DIE_EXCEPTION "Dies due to an uncaught exception"** (`FBS:113-115`). It is emitted **only when the sandbox fails
   at spawn** (`PlayerControlProvider.java:139-144`). A real uncaught exception in `run()` gives only a `diedIDs`
   entry (`SandboxedRobotPlayer.java:191-206`; `GameWorld.java:222-223`). Relatedly, the spec says "Unhandled
   exceptions may paralyze your robot" (`SPEC:249`). In the engine, an exception escaping `run()` **destroys** the
   robot.
10. **`resourceWellLocs` "The locations of the resources wells being given resources"** (`FBS:286`). **All** wells are
    listed every round (`GameWorld.java:698-702`; [measured]: 20 of 20 in every round).
11. **Schema README "A match file has the extension `.bc22`"** (`SREADME:7`). The engine uses whatever
    `bc.server.save-file` says (`Main.java:59-65`). The README's "compressed with GZIP" is correct.
12. **`maxCorner` "The top corner of the map"** (`FBS:55-56`). It is **exclusive** (origin + width/height,
    `GameMapIO.java:321-322`).
13. **Writer-side swap of `Constants`.** `AdAdditiveIncrease` is written with `PASSIVE_MN_INCREASE` and vice versa
    (`GameMaker.java:267-268`). The values are equal (6), so the swap has no effect today.
14. **DESTABILIZER movement cooldown.** The spec table says 20 (`SPEC:194, 199`). The engine says **25**
    (`RobotType.java:49`), and the replay header records 25 ([measured] `OUT`:9).
15. **`GameHeader.specVersion` is "3.0.14" in the 3.0.15 release** (`GameConstants.java:13`; [measured]). This is a
    version-label mismatch rather than a rule disagreement.

## Surprises: mechanics a bot designer could easily get wrong

1. **Cargo counts for the tiebreak and in the replay's team totals, but your HQ cannot see it.** Team totals = HQs +
   carriers (#22). `rc.getResourceAmount` on an HQ shows only that HQ's stock (#23). test1 was decided 420 vs 17 Mn
   while both HQs held exactly 10 Mn (#32). Each of these lowers the tiebreak total:
   - a carrier dying with cargo (`GameWorld.java:828-830`);
   - a carrier throwing (`InternalCarrier.java:35-45`);
   - depositing into a well (`RobotControllerImpl.java:912-913, 921`).
2. **A throw empties the whole inventory, anchors included, whatever the target.** Even a no-damage throw at an empty
   tile, an ally or an HQ does this (`InternalCarrier.java:62-73`). In the replay this has no CHANGE_* trace.
3. **Attacks on empty tiles, allies or HQs "succeed".** They cost the cooldown and deal no damage
   (`InternalRobot.java:404-409`). The replay marks them with a negative target, so wasted attacks in our own games
   can be counted.
4. **A lethal hit has no CHANGE_HEALTH, and HQ or destabilizer damage has no attacker action** (#27). Credit kills
   from `diedIDs` together with the same round's attack targets, not from CHANGE_HEALTH alone.
5. **Positions are end-of-round only, and they are after currents** (#21, #36). Do not read `movedIDs` as "robots that
   moved". Diff positions to find movers.
6. **Newly built robots do not act in their build round** (#20). They appear in `movedIDs` but not in `bytecodeIDs`.
7. **Indicator strings reset to `""` every round.** Set them every turn or they are blank. Robot `System.out` is not in
   the replay at all (#33). For post-game diagnostics, use indicator strings, dots and lines, or capture stdout.
8. **Overruns can be read from the replay:** `bytecodesUsed >= bodyTypeMetadata.bytecodeLimit` (#20 table row).
   **[measured]** 0 overruns for examplefuncsplayer in test1.
9. **Wells never deplete.** The per-round `well*Values` are deposits, used for upgrades and elixir conversion. They are
   not stock left to mine (`RobotControllerImpl.java:961-973`; `Well.java:38-64`).
10. **Passive income is per HQ.** +6 Ad and +6 Mn per HQ every 5 rounds, applied to each HQ's own inventory
    (`InternalRobot.java:439-449`).
11. **The island anchor type and the win reason are not recorded.** Infer the anchor type by tracking each carrier's
    PICK_UP_ANCHOR types; if a carrier holds both, STANDARD is placed first (`InternalRobot.java:155-163`). Derive the
    win reason with the tiebreak chain (#32).
12. **Robot IDs carry no team or type information and are seed-dependent** (#43). Look the team and type up in
    `spawnedBodies` or MatchHeader `bodies`. Never infer them from the ID.

## UNVERIFIED items (collected)

- That a killed JVM leaves no replay file (#2). This is inferred from the write-at-end code. I did not test it.
- The engine-exception path in `runRound` that skips the round and footer (#9). This is read from the code only.
- That health can be reconstructed exactly as metadata health + Σ CHANGE_HEALTH (#28). The reader does not check it.
- That the 20 deaths with no attack-action trace were caused by HQ damage (#27). The positions are consistent with it,
  and no direct cause is recorded.
- The websocket busy-port behaviour (#42). This is taken from the sibling report and was not re-measured here.
