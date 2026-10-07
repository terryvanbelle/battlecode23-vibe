# Battlecode 2023 (Tempest): maps, verified against the engine

Scope: how maps are loaded, what a map may contain, how symmetry is defined and how far it is enforced, the island,
well and HQ rules, and a census of all 103 maps in the release jar.

Sources and abbreviations used in provenance tags:

| Tag | Path |
|---|---|
| `E/` | `/home/terryvanbelle/projects/vibe/reference/battlecode23/engine/src/main/battlecode/` (git master source) |
| `JAR` | `/home/terryvanbelle/projects/vibe/2023/engine/battlecode23-3.0.15.jar`, read with `javap -c -p -constants` (JDK 8u504) |
| `SPEC` | `/home/terryvanbelle/projects/vibe/reference/battlecode23/specs/specs.md.html` (line numbers) |
| `CLIENT/` | `/home/terryvanbelle/projects/vibe/reference/battlecode23/client/visualizer/src/` |
| `SCHEMA` | `/home/terryvanbelle/projects/vibe/reference/battlecode23/schema/battlecode.fbs` |
| `CENSUS:col` | column `col` of `/home/terryvanbelle/projects/vibe/2023/research/rules/mapcensus/maps.tsv` (produced by `MapCensus.java` in the same directory, run through the jar's own loader) |

Jar vs source: every map-relevant member I checked in the jar matches the source: `GameConstants` map constants,
`Server.validateMapOnGuarantees` (string constants, the `2`/`32` HQ bounds, `20`/`60`/`35`/`100` literals),
`MapBuilder.getSymmetricIsland` and its validation strings, `InternalRobot.canSenseLocation`,
`RobotControllerImpl.assertCanBuildRobot`, `LiveMap` sorting by ID, `GameMapIO$Serial` (2000 rounds), and the
`HEADQUARTERS` constructor arguments in `RobotType`. `GameConstants.SPEC_VERSION` is `"3.0.14"` in both (JAR
`battlecode.common.GameConstants`; `E/common/GameConstants.java:13`), although the jar is 3.0.15.

---

## 1. Facts

### 1.1 Loading and file format

1. Map files use the extension `.map23` (`E/world/GameMapIO.java:34`). Built-in maps live in the jar under
   `battlecode/world/resources/` (`GameMapIO.java:39`). The jar contains 103 of them (`unzip -l` of JAR;
   `CENSUS`: 103 rows).
2. The server first looks for `<mapDir>/<name>.map23`, where `mapDir` is `bc.game.map-path` and defaults to `maps`.
   If the file is not there it falls back to the jar resource (`GameMapIO.java:51-63`; `E/server/Config.java:71`).
   The name stored inside the file must equal the file name, or loading fails (`GameMapIO.java:65-69, 88-92`).
3. A map is a flatbuffer `GameMap` holding: name, minCorner, maxCorner, symmetry (int), bodies, randomSeed, and
   per-tile arrays walls[bool], clouds[bool], currents[int], islands[int], resources[int] (`SCHEMA:50-74`).
4. Width is `maxCorner.x - minCorner.x`, height is `maxCorner.y - minCorner.y`, and the origin is `minCorner`
   (`GameMapIO.java:223-225`). All 103 shipped maps have origin (0,0) (`CENSUS:origin`). The run-time validator
   indexes tiles as `x + y*W` and ignores the origin (`E/server/Server.java:213-219`), so only origin (0,0) maps
   validate correctly. `MapBuilder` asserts origin 0 (`E/world/MapBuilder.java:31-33`).
5. The file's `symmetry` int becomes `MapSymmetry.values()[i]`, with 0 = ROTATIONAL, 1 = HORIZONTAL,
   2 = VERTICAL (`GameMapIO.java:226`; `E/world/MapSymmetry.java:6-10`; `SCHEMA:57`). This field is metadata only.
   Nothing in the game logic reads it, and robots cannot see it (section 1.3).
6. The round limit does not come from the map. Every loaded map gets `GameConstants.GAME_MAX_NUMBER_OF_ROUNDS` = 2000
   (`GameMapIO.java:228`; `E/common/GameConstants.java:170`; JAR `GameMapIO$Serial` `sipush 2000`).
7. Only bodies of type HEADQUARTERS are kept from the file. Any other body type is silently dropped
   (`GameMapIO.java:338-356`, comment "ignore robots that are not headquarters, TODO throw error?"). Each kept HQ gets
   an empty inventory and full health (`GameMapIO.java:350-352`).
8. With `teamsReversed`, every HQ's team is flipped at load time, but the HQ IDs and positions stay the same
   (`GameMapIO.java:347-349`). `teamsReversed` alternates between consecutive matches only when
   `bc.server.alternate-order` is true. The default is false (`Server.java:176-181`; `Config.java:53`).
9. `LiveMap` sorts the initial bodies by ID (`E/world/LiveMap.java:151-152`; JAR `LiveMap.<init>` calls
   `Arrays.sort`). `GameWorld` spawns them in that order (`E/world/GameWorld.java:84-90`). Execution order equals spawn
   order (`E/world/ObjectInfo.java:154-161, 95-104`), so **the HQ with the lowest ID in the map file acts first every
   round**. Shipped HQ IDs are small integers (2, 3, 4...), not ≥10000 (`CENSUS:hq_ids_exec_order`). SPEC:94 says the
   same ("unique random IDs no smaller than 10,000, except for your headquarters").
10. The map's `randomSeed` seeds the robot `IDGenerator`, which hands out shuffled blocks of 4096 IDs starting above
    10000 (`GameWorld.java:63`; `E/world/IDGenerator.java:16, 21, 48-53, 73-94`). So the IDs of newly built robots are
    determined by the map. `GameWorld.rand` and `RobotControllerImpl.random` are also seeded from it
    (`GameWorld.java:78`; `E/world/RobotControllerImpl.java:49`), but grep found no other use of them.
11. Validation runs in `Server.runMatch` after the `GameWorld` is built and before round 1, but only when
    `bc.server.validate-maps` is true. That is the default (`Server.java:457-469`; `Config.java:52`). If a map fails,
    the exception goes to `ErrorReporter`, the server enters the ERROR state, and the whole game stops
    (`Server.java:179-186`). The spec changelog notes a Gradle option to turn validation off (SPEC:462).

### 1.2 Coordinates

12. `Direction.NORTH` = (dx 0, dy +1), so y grows to the north and (0,0) is the south-west (bottom-left) corner
    (`E/common/Direction.java:21-53`). This matches SPEC:44. Per-tile arrays are row-major from y = 0:
    `index = x + y*W` (`GameWorld.java:309-321`; `MapBuilder.java:61-63`).
13. Valid coordinates are 0 ≤ x < W and 0 ≤ y < H (`LiveMap.java:255-257` with origin 0;
    `E/common/RobotController.java:30-47`). Map sizes are between 20 and 60 inclusive in each dimension
    (`GameConstants.java:19-29`; `Server.java:246-257`).
14. Currents are stored as indices into `Direction.DIRECTION_ORDER` = {CENTER, WEST, NORTHWEST, NORTH, NORTHEAST,
    EAST, SOUTHEAST, SOUTH, SOUTHWEST}, so 0 means no current (`Direction.java:55`; `GameWorld.java:69-74`).
    Resources are stored as `ResourceType` IDs: 0 none, 1 adamantium, 2 mana, 3 elixir
    (`E/common/ResourceType.java:4-7`). An island value of 0 means no island (`GameWorld.java:96-104`).

### 1.3 Symmetry: definition and enforcement

15. There are three kinds of symmetry (`MapSymmetry.java:6-10`), mapping a tile (x,y) as follows
    (`MapBuilder.java:130-150`; client `CLIENT/mapeditor/forms/symmetry.ts:121-139`):
    - **ROTATIONAL**: (x,y) → (W-1-x, H-1-y), a 180° rotation.
    - **HORIZONTAL**: (x,y) → (x, H-1-y). This mirrors across a *horizontal* line, so **y flips**.
    - **VERTICAL**: (x,y) → (W-1-x, y). This mirrors across a *vertical* line, so **x flips**.
16. Under a symmetry, HQs map to HQs of the other team (`MapBuilder.java:161-164, 381-389, 398-400`; client
    `symmetry.ts:98-100, 148-169`).
17. **Currents are mirrored geometrically.** ROTATIONAL negates (dx,dy), HORIZONTAL negates dy, VERTICAL negates dx
    (client `symmetry.ts:102-113`). The engine's `MapBuilder.getSymmetricCurrent` instead always uses
    `Direction.opposite()` (`MapBuilder.java:176-179, 371`), which is only correct for rotation. The shipped maps use
    the geometric rule: of the 54 reflection-symmetric maps that have currents, 41 do not fit the `opposite()` rule
    (`CENSUS:sym_currents_geometric` vs `sym_currents_opposite`). In the other 13, the currents happen to fit both
    rules, for example because they lie along the mirror axis.
18. **Symmetry is not checked at run time.** `Server.validateMapOnGuarantees` contains no symmetry check
    (`Server.java:244-439`; JAR disassembly of the same method contains no symmetry call or string). The only symmetry
    check is in the development tool `MapBuilder.assertIsValid` (`MapBuilder.java:287-291`). It uses two conventions
    that no shipped map follows: island ID k must mirror to W·H−k (`MapBuilder.java:186-188, 374`), and currents mirror
    to their opposite. As a result, `MapBuilder.assertIsValid` rejects **all 103** shipped maps with "Headquarters,
    walls, clouds, currents, islands and resources must be symmetric" (`CENSUS:builder_assertIsValid`,
    `builder_getSymmetry` = NONE for all). Even with islands removed, 41 maps still fail because of the currents
    convention (`CENSUS:builder_getSymmetry_no_islands`). The shipped maps were evidently made with the client map
    editor, not `MapBuilder`.
19. Even so, every shipped map is symmetric in the geometric sense across walls, clouds, currents (geometric),
    wells (type and position), islands (as a set of tile groups; IDs may differ) and HQs (team-swapped):
    ROTATIONAL 44, VERTICAL 42, HORIZONTAL 16, and one map (Cornucopia) is both ROTATIONAL and HORIZONTAL. No map is
    asymmetric (`CENSUS:sym_all`).
20. The symmetry stored in the file is wrong for one map. **FourNations** says ROTATIONAL, but its wells are only
    consistent with VERTICAL: well positions are symmetric under all three kinds, but rotation swaps adamantium and
    mana (`CENSUS:declared_sym_consistent`, `sym_wells`; direct dump: AD at (8,3) rotates to (36,41), which is a MN
    well).
21. Robots cannot read the symmetry. `RobotController` exposes only `getMapWidth`, `getMapHeight` and
    `getIslandCount` as global map facts (`E/common/RobotController.java:37, 47, 56`;
    `E/world/RobotControllerImpl.java:82-94`). A bot has to work out the symmetry from what it senses.
22. Island IDs are arbitrary labels. On every shipped map they are exactly 1..N (`CENSUS:island_ids_1_to_N` true for
    103/103), but the validator does not require this (`Server.java:311-341`). Mirrored islands follow no fixed ID
    rule: only 5 of 103 maps use id ↔ N+1−id, and IDs follow no consistent scan order (scratch analysis with
    IslMap/IslOrd against the jar loader). SPEC changelog: "islandIDs no longer clue you in on where other islands are"
    (SPEC:464).

### 1.4 What the run-time validator enforces (`Server.validateMapOnGuarantees`, `Server.java:244-439`)

23. Width and height must each be between 20 and 60 inclusive (`Server.java:246-257`).
24. Every initial body must be an HQ, and no two may share a tile (`Server.java:259-270`).
25. There must be **at least 2 and at most 32 HQs in total**: `MIN_STARTING_HEADQUARTERS*2` and
    `MAX_STARTING_HEADQUARTERS*8` (`Server.java:272-278`; JAR offsets 192 `iconst_2` and 229 `bipush 32`). The number
    per team and the balance between teams are **not** checked. `GameConstants` documents 1..4 *per team*
    (`GameConstants.java:31-35`).
26. A wall tile may not hold a cloud, a well, an island tile, a current or an HQ (`Server.java:281-293`).
27. A tile may not hold both a cloud and a current (`Server.java:295-296`), a well and an HQ (`Server.java:299-300`),
    a well and a current (`Server.java:303-304`), or a current and an HQ (`Server.java:307-308`).
28. There must be 4 to 35 islands, counted as distinct nonzero IDs (`Server.java:312-328`;
    `GameConstants.java:37-41`). Each island has at most 20 tiles (`Server.java:333-335`; `GameConstants.java:44`).
    Each island must be **4-connected**: the flood fill uses `Direction.cardinalDirections()`
    (`Server.java:230-242, 329-341`).
29. Every HQ must have an adamantium well with dist² ≤ `MIN_NEAREST_AD_DISTANCE` = 100 (`Server.java:344-365`;
    `GameConstants.java:49-50`). The comparison is inclusive, `distanceSquaredTo <= r²`
    (`E/common/MapLocation.java:119-121`; `GameWorld.java:462-479`). Despite its name, this constant is a *maximum*.
30. Only resource types 0, 1 and 2 are allowed. A map cannot start with elixir wells (`Server.java:368-385`).
31. Every adamantium well needs a mana well with dist² ≤ 100, and every mana well needs an adamantium well with
    dist² ≤ 100 (`Server.java:387-411`; `GameConstants.java:47`).
32. For each type, the number of wells must be ≤ `(int)(W*H*0.04f)` (`Server.java:413-419`;
    `GameConstants.java:53`).
33. Every current must point to a tile that is on the map, is not a wall, and is not the destination of any other
    current (`Server.java:422-438`).
34. **Not checked at run time:** symmetry; HQ count per team; an HQ on a cloud or island; a well on an island or
    cloud; a current pointing into an HQ, well or island; whether wells, islands or the enemy can be reached; how far
    apart HQs are; a mana well near each HQ; whether island IDs are contiguous; origin = (0,0). (These are absences in
    `Server.java:244-439`.)

### 1.5 `MapBuilder.assertIsValid`, a development tool, not used at run time (`MapBuilder.java:224-337`)

35. Compared with the server validator, it checks the HQ count per team (team A only, 1..4,
    `MapBuilder.java:242-254`). It requires symmetry, using the conventions in fact 18 (`MapBuilder.java:287-291`). It
    requires an adamantium well within each team's **HQ vision radius (34)** rather than within 100
    (`MapBuilder.java:293-318`). It also computes `hasVisibleMana` but never tests it (`MapBuilder.java:295, 311-318`).
    It does **not** check island count, island size or connectivity, the adamantium-mana distance, or the 4% cap. Only
    `MapBuilder.saveMap` calls it (`MapBuilder.java:214-219`). The repository has a single builder-generated map,
    `maptestsmall` (`E/world/maps/MapTestSmall.java:26, 44-104`). Its island-growing loop throws away the result of
    `nextLoc.add(...)`, so every island in it is one tile (`MapTestSmall.java:63, 93`; `CENSUS`: maptestsmall
    island_max 1).

### 1.6 Islands at run time

36. Islands are built from the map's island IDs as given (`GameWorld.java:93-108`). `senseIsland` returns that ID, or
    −1 off-island (`RobotControllerImpl.java:306-310`). `getIslandCount()` returns the number of distinct islands
    (`RobotControllerImpl.java:92-94`), so a robot knows N on its first turn.
37. A team wins by conquest the moment `currentAnchorsPlaced / N ≥ 0.75f` (`E/world/TeamInfo.java:188-194, 175-182`;
    `GameConstants.java:93`). The number of anchors needed is the smallest k with k/N ≥ 0.75: 3 of 4, 6 of 8, 27 of 35
    (`CENSUS:islands_needed_to_win`).
38. Each round an anchor's health changes by `floor(100*(own occupants − enemy occupants)/area)`
    (`E/world/Island.java:94-103`), so on small islands each robot moves the health a lot. The heal and boost area is
    every tile within dist² 4 of any island tile (`Island.java:129-137`; `GameConstants.java:99`).
39. Distinct islands never touch orthogonally on any shipped map, but they do touch **diagonally** on Flower,
    Spiderweb, ThirtyFive and maptestsmall (`CENSUS:distinct_islands_touch_diag`). An 8-connected flood fill would merge
    them; the engine uses IDs and 4-connectivity.
40. Islands can sit under clouds (USA: all 124 island tiles; Lines, Sakura: all) and currents (Spiderweb: all 318
    island tiles) (`CENSUS:cloud_on_island`, `current_on_island`). No shipped map puts an HQ or a well on an island
    (`CENSUS:hq_on_island`, `well_on_island` = 0), although the validator would allow it.

### 1.7 Wells at run time

41. A `Well` is created for every tile with a nonzero resource (`GameWorld.java:113-122`). A carrier may collect only
    from a well within Chebyshev distance 1, including the well's own tile (`RobotControllerImpl.java:938-941`;
    `MapLocation.java:129-132`).
42. Wells can be on cloud tiles (24 maps, 107 wells; Repetition has 16) (`CENSUS:well_on_cloud`). A well on a cloud can only be
    sensed from dist² ≤ 4 (`E/world/InternalRobot.java:271-277`; `RobotControllerImpl.java:484-502`).

### 1.8 HQs at run time

43. HQ action radius² is 9 and vision radius² is 34 (`E/common/RobotType.java:21`; JAR `RobotType.<clinit>`
    `bipush 9`, `bipush 34`).
44. **An HQ standing on a cloud has vision radius² 4** (`InternalRobot.java:271-277`;
    `GameConstants.java:137`), and any cloud tile is only sensable within dist² 4.
45. **Building a robot requires sensing the target tile.** `assertCanBuildRobot` calls `isLocationOccupied` and
    `sensePassability`, both of which call `assertCanSenseLocation` (`RobotControllerImpl.java:670-697, 217-219,
    300-303, 180-188`; JAR `assertCanBuildRobot` invokes both). So an HQ on a cloud can only spawn within dist² 4, and
    no HQ can spawn onto a cloud tile at dist² 5..9. The fewest spawnable tiles for any HQ on any shipped map is 5
    (Rewind, Repetition), and the most is 28 (`CENSUS:min_spawn_tiles_per_hq`).
46. Four currents point into an HQ tile, two each on BowAndArrow and Rewind (`CENSUS:currents_into_hq`; direct dump:
    BowAndArrow (8,7) NORTHEAST → HQ at (9,8)). The validator allows this. `applyCurrents` blocks any robot whose
    destination already holds a robot that does not move, HQs included (`GameWorld.java:736-782`), so a robot on such
    a current is never moved.

### 1.9 Terrain mechanics that depend on the map (cited for context; other reports own the details)

47. Currents are applied at the end of every round (`CURRENT_STRENGTH` = 1, and `currentRound % 1 == 0`)
    (`GameConstants.java:128`; `GameWorld.java:707-710`). Clouds add +0.2 to both teams' cooldown multiplier on their
    tile (`GameWorld.java:136-143`; `GameConstants.java:143`).

---

## 2. Map census

**Program:** `/home/terryvanbelle/projects/vibe/2023/research/rules/mapcensus/MapCensus.java`. Rebuild and run with
`/home/terryvanbelle/projects/vibe/2023/research/rules/mapcensus/run.sh` (javac against the jar, `java -Xmx300m`).
It writes `/home/terryvanbelle/projects/vibe/2023/research/rules/mapcensus/maps.tsv`: 103 rows and 67 columns.
Tournament labels come from the client's `SERVER_MAPS` table (`CLIENT/constants.ts:147-262`). The engine itself
records no tournament.

What it does for each map:
- Lists the maps with `GameMapIO.getAvailableMaps(null)` and loads each with `GameMapIO.loadMapAsResource`, the
  engine's own loader.
- Calls the private `Server.validateMapOnGuarantees` by reflection. **All 103 pass** (`server_validator`).
- Copies the map into a `MapBuilder`, then runs `MapBuilder.getSymmetry` (by reflection) and
  `MapBuilder.assertIsValid`. All 103 fail, as explained in fact 18.
- Runs its own geometric symmetry test on each feature separately (walls, clouds, currents, wells, islands, HQs) and
  on all of them together (`sym_all`).
- Measures distances: dist², Chebyshev distance, and king-move BFS steps between the closest opposing HQs, with walls
  and HQs blocking. A path exists on all 103 maps.
- Records wells by type, island count and area, terrain percentages, overlaps, and spawnable tiles per HQ.
- Checks reachability from each team's spawn tiles (king moves; walls and HQs block).
- Models what a team knows on round 1 (`deduce()`): all its own HQ positions (HQs can write to the shared array,
  SPEC:148), plus everything its HQs can sense under the engine's cloud rule, plus the cloud bits that
  `senseNearbyCloudLocations` reveals within 34 (`RobotControllerImpl.java:421-443`). It then lists which symmetries
  remain possible. This is a modelling assumption, not an engine guarantee. As a sanity check, the true symmetry is
  never eliminated.

---

## 3. Corpus distribution (103 maps)

**By tournament** (client labels): Default 9, Sprint 1 23, Sprint 2 25, International Qualifying 15, US Qualifying
15, HS/Newbie 16. The client enum has a `FINAL` category, but **no map in the jar carries that label**, so the
final-tournament maps are absent (`CLIENT/constants.ts:147-156`). Turtle, Dreamy, Forest, PairedProgramming and
Rewind are labelled DEFAULT, although the table lists them between the Sprint 1 and Sprint 2 maps
(`CLIENT/constants.ts:186-190`).

**Size.**
- Width ranges from 20 to 60 (median 40). Height ranges from 20 to 60 (median 30).
- Area ranges from 400 to 3600 (median 1200, mean 1389). By area: ≤625: 21 maps; 626–1225: 41; 1226–2025: 23;
  >2025: 18.
- Shape: 52 maps are square, 47 are wider than tall, and only 4 are taller than wide.
- The most common sizes are 30×30 (12), 20×20 (8), 40×30 (8), 40×40 (7), 60×60 (6) and 45×45 (5).
- 29 maps have an odd width and 26 an odd height, which gives them a self-mirrored centre line or centre tile.

**Symmetry** (geometric, all features): ROT 44, VERT 42, HORI 16, ROT+HORI 1 (Cornucopia). By shape: square maps are
mostly ROT (29) or VERT (18), and wide maps mostly VERT (21), ROT (15) or HORI (11).

| Tournament | n | ROT / HORI / VERT | HQs per team: 1 / 2 / 3 / 4 | median area | median islands | median closest opposing-HQ d² | median BFS steps | median % wall / cloud / current |
|---|---|---|---|---|---|---|---|---|
| Default | 9 | 6 / 0 / 3 | 1 / 5 / 2 / 1 | 900 | 6 | 162 | 16 | 5.8 / 5.3 / 3.1 |
| Sprint 1 | 23 | 11 / 2 / 10 | 6 / 17 / 0 / 0 | 1250 | 4 | 361 | 21 | 9.9 / 2.1 / 5.0 |
| Sprint 2 | 25 | 10 / 3 / 13 (Cornucopia counted as ROT and HORI) | 9 / 14 / 2 / 0 | 900 | 5 | 482 | 21 | 15.3 / 5.3 / 2.2 |
| Intl Qual | 15 | 6 / 3 / 6 | 4 / 8 / 2 / 1 | 1200 | 8 | 361 | 29 | 22.0 / 13.9 / 3.3 |
| US Qual | 15 | 6 / 3 / 6 | 3 / 11 / 1 / 0 | 1200 | 8 | 648 | 31 | 17.6 / 11.0 / 4.0 |
| HS/Newbie | 16 | 6 / 6 / 4 | 3 / 11 / 1 / 1 | 1180 | 8 | 577 | 27 | 15.7 / 14.3 / 3.2 |

Later tournaments have more walls and clouds, more islands, and HQs further apart.

**HQs.**
- Every map gives both teams the same number of HQs: 1 per team on 26 maps, 2 on 66, 3 on 8 (Cornucopia, DefaultMap,
  LookingGlass, Maze, PairedProgramming, River, Sneaky, ThirtyFive) and 4 on 3 (Forest, Fractured, Repetition).
- In the map file's own team order, the lowest-ID HQ belongs to team B on 59 maps and team A on 44
  (`hq_ids_exec_order`).
- 11 maps place HQs on clouds (32 HQs in all); on River all 6 do (`hq_on_cloud`). 17 maps place HQs on the map edge
  (`hq_on_edge`).

**Distance between the closest opposing HQs.**
- dist² ranges from 4 to 3481 (median 441, about 21 tiles). Chebyshev distance ranges from 2 to 59 (median 20). BFS
  path length ranges from 2 to 62 steps (median 25).
- 13 maps have dist² ≤ 100, and 47 have dist² ≤ 400.
- The closest are BowAndArrow (d² 4: HQs at (15,11) and (15,13)), Squares (d² 10), Sine (34), Clown (36) and
  Repetition (36, but 30 BFS steps).
- The BFS/Chebyshev ratio has a median of 1.0, but reaches 6.4 on Potions, a maze.

**Wells.**
- Adamantium wells per map range from 2 to 16 (median 4), and so do mana wells (median 4). There are never any elixir
  wells.
- For the worst-placed HQ on each map, the nearest adamantium well is at dist² 8–100 (median 45). On 11 maps it is
  exactly 100, the inclusive limit (ArtistRendition, BattleSuns, Crossword, DefaultMap, Forest, IslandHopping,
  IslandHoppingTwo, LookingGlass, Pakbot, Spiderweb, Target).
- For the worst-placed HQ, the nearest mana well is at dist² 8–328 (median 73). On 37 maps some HQ has no mana well
  within 100 (worst: Forest, 328).
- On 38 maps no HQ can see an adamantium well at spawn (dist² ≤ 34). On 62 maps no HQ can see a mana well at spawn.

**Islands.**
- 4–35 per map (median 6). The distribution: 4 islands on 44 maps, 5 on 6, 6 on 8, 7 on 2, 8 on 31, 9 on 3, 10 on 1,
  12 on 3, 14 on 1, 16 on 2, 20 on 1, 35 on 1 (ThirtyFive).
- Anchors needed to win: 3 on 44 maps and 6 on 33; the maximum is 27.
- Total island area per map ranges from 6 to 318 (median 53). Single islands range from 1 tile (HideAndSeek, RockWall,
  maptestsmall) to 20 tiles.

**Terrain.**
- Walls: 1.1%–71.5% of tiles (median 14.1). Nine maps are ≥40% wall (BuildSite 71.2, ThirtyFive 71.5, IslandHoppingTwo
  58.9, Tightrope 58.0, Crossword 57.6, Fractured 47.8, BattleSuns 43.8, TimesUp 42.7, Target 42.4).
- Clouds: 0%–54.5% (median 7.1; Spin 54.5, USA 51.5, Checkmate2 49.0, Marsh 40.6, Sneaky 37.0).
- Currents: 0%–18.4% (median 3.3; Spiderweb 18.4, ReverseFunnel 18.0).
- 8 maps have no currents and 6 have no clouds. On 85 maps some current flows into another current, forming chains
  (`currents_into_current`).

**Reachability.**
- Every well and every island is reachable by both teams on all 103 maps.
- 14 maps contain pockets that no team can reach (Cat has 814 such tiles; Spiderweb 134; BatSignal 86).
- Three maps have tiles that only one team can reach: PipesAndParabolas (108), ThirtyFive (12) and Jail (4).

**Deducing the symmetry at the start.**
- Own HQ positions alone rule out a symmetry on only 19 maps; on 84 maps all three remain possible
  (`syms_left_ownHQs_*`).
- After round-1 HQ vision, the symmetry is fully determined on 10 maps (BowAndArrow, Clown, DefaultMap, Fractured,
  Jail, Maze, Repetition, Sine, Squares, maptestsmall). Two candidates remain on 65 maps and all three on 28
  (`syms_left_round1_*`). Both teams always reach the same conclusion.
- Using walls alone, the symmetry is ambiguous on 10 maps (`sym_walls_only`).

---

## 4. Per-map table

Columns:
- *Symmetry*: geometric, all features.
- *HQ/team*: HQs per team.
- *Islands (area; to win)*: number of islands, total island tiles, and anchors needed to win.
- *Opp. HQ d² / BFS steps*: closest opposing HQ pair.
- *Min spawn tiles*: the fewest tiles any HQ can build onto.
- *Syms left after round-1 vision*: the result of the knowledge model described in section 2.

The full 67-column data is in `maps.tsv`.

| Map | Tournament | W×H | Symmetry | HQ/team | AD/MN wells | Islands (area; to win) | % wall / cloud / current | Opp. HQ d² / BFS steps | Min spawn tiles | Syms left after round-1 vision |
|---|---|---|---|---|---|---|---|---|---|---|
| AbsoluteW | US Qual | 40×40 | VERT | 1 | 6/6 | 8 (104; 6) | 13.3 / 11.0 / 9.3 | 841 / 29 | 28 | ROT+HORI+VERT |
| AllElements | Default | 30×30 | ROT | 2 | 6/6 | 6 (36; 5) | 4.4 / 2.4 / 2.9 | 436 / 19 | 27 | ROT+HORI |
| ArtistRendition | Sprint 1 | 40×40 | ROT | 2 | 6/8 | 4 (56; 3) | 9.0 / 0.0 / 7.0 | 900 / 30 | 24 | ROT+HORI |
| Barcode | Intl Qual | 20×20 | ROT | 2 | 2/2 | 7 (58; 6) | 31.5 / 28.0 / 3.0 | 226 / 15 | 8 | ROT+HORI |
| BatSignal | Sprint 1 | 60×20 | VERT | 1 | 4/4 | 4 (50; 3) | 19.5 / 1.3 / 6.2 | 2809 / 53 | 27 | ROT+VERT |
| BattleSuns | Sprint 2 | 50×50 | ROT | 2 | 10/12 | 8 (40; 6) | 43.8 / 18.3 / 0.0 | 1525 / 39 | 11 | ROT+HORI |
| BowAndArrow | Sprint 1 | 35×25 | HORI | 2 | 3/4 | 4 (60; 3) | 2.1 / 4.6 / 8.8 | 4 / 2 | 27 | HORI |
| Buggy | US Qual | 50×40 | HORI | 2 | 6/6 | 8 (110; 6) | 8.8 / 14.2 / 4.2 | 529 / 35 | 15 | ROT+HORI |
| BuildSite | HS/Newbie | 50×50 | ROT | 2 | 6/6 | 8 (140; 6) | 71.2 / 3.0 / 0.0 | 1521 / 39 | 28 | ROT+VERT |
| Cat | Sprint 1 | 50×50 | VERT | 2 | 4/2 | 6 (24; 5) | 16.6 / 0.8 / 0.6 | 441 / 21 | 28 | ROT+VERT |
| Cave | US Qual | 30×20 | ROT | 2 | 4/4 | 8 (104; 6) | 22.0 / 5.7 / 8.0 | 425 / 25 | 13 | ROT+VERT |
| Cee | US Qual | 40×30 | HORI | 2 | 6/6 | 8 (118; 6) | 26.0 / 11.5 / 2.5 | 361 / 25 | 13 | ROT+HORI |
| Checkmate2 | Sprint 2 | 21×21 | ROT | 2 | 2/4 | 8 (72; 6) | 18.4 / 49.0 / 15.4 | 324 / 18 | 10 | ROT+HORI |
| Clown | Sprint 1 | 21×20 | VERT | 2 | 4/3 | 4 (31; 3) | 15.0 / 2.9 / 7.1 | 36 / 6 | 13 | VERT |
| Contraction | Intl Qual | 60×60 | HORI | 2 | 6/6 | 8 (84; 6) | 36.8 / 13.9 / 3.4 | 2809 / 53 | 11 | ROT+HORI |
| Cornucopia | Sprint 2 | 59×59 | ROT+HORI | 3 | 6/6 | 9 (110; 7) | 1.1 / 1.5 / 2.1 | 482 / 19 | 28 | ROT+HORI |
| Crossword | Sprint 2 | 45×45 | ROT | 2 | 6/6 | 4 (46; 3) | 57.6 / 5.3 / 2.3 | 2384 / 51 | 12 | ROT+HORI+VERT |
| CrownJewels | HS/Newbie | 30×30 | VERT | 1 | 4/2 | 4 (46; 3) | 14.0 / 15.6 / 0.0 | 729 / 27 | 22 | ROT+VERT |
| Cube | Sprint 2 | 30×30 | VERT | 2 | 8/4 | 8 (16; 6) | 13.1 / 0.0 / 1.8 | 625 / 25 | 26 | ROT+VERT |
| DefaultMap | Default | 32×32 | ROT | 3 | 4/4 | 6 (40; 5) | 2.7 / 4.1 / 3.1 | 149 / 10 | 27 | ROT |
| Diagonal | Sprint 1 | 40×40 | ROT | 1 | 4/4 | 4 (50; 3) | 4.3 / 1.3 / 4.6 | 1922 / 32 | 28 | ROT+HORI+VERT |
| Divergence | Sprint 2 | 40×20 | VERT | 1 | 4/4 | 4 (36; 3) | 30.3 / 7.0 / 9.3 | 1089 / 33 | 22 | ROT+VERT |
| Dreamy | Default | 30×30 | ROT | 2 | 4/4 | 5 (24; 4) | 19.8 / 11.6 / 2.2 | 482 / 19 | 13 | ROT+HORI+VERT |
| Elephant | HS/Newbie | 40×30 | ROT | 2 | 4/4 | 4 (62; 3) | 22.0 / 20.7 / 5.8 | 1530 / 37 | 10 | ROT+VERT |
| ExtremelyMid | HS/Newbie | 40×29 | HORI | 2 | 6/5 | 8 (112; 6) | 9.3 / 12.6 / 10.4 | 400 / 22 | 21 | HORI+VERT |
| Eyelands | Sprint 1 | 50×30 | VERT | 2 | 8/6 | 4 (76; 3) | 10.3 / 0.5 / 5.5 | 361 / 19 | 27 | HORI+VERT |
| FishCake | HS/Newbie | 37×20 | ROT | 1 | 2/2 | 4 (66; 3) | 14.1 / 24.9 / 3.5 | 577 / 27 | 20 | ROT+VERT |
| Flower | Intl Qual | 35×35 | ROT | 2 | 4/6 | 4 (30; 3) | 1.8 / 20.7 / 3.9 | 850 / 28 | 12 | ROT+HORI+VERT |
| Forest | Default | 60×60 | VERT | 4 | 6/4 | 7 (128; 6) | 5.8 / 27.1 / 3.3 | 1369 / 37 | 9 | ROT+VERT |
| FourNations | Sprint 2 | 45×45 | VERT (file says ROTATIONAL) | 2 | 4/4 | 5 (53; 4) | 4.3 / 7.9 / 13.4 | 1444 / 38 | 27 | ROT+VERT |
| Fractured | HS/Newbie | 60×60 | ROT | 4 | 8/8 | 4 (76; 3) | 47.8 / 11.2 / 0.7 | 74 / 27 | 12 | ROT |
| Frog | Sprint 1 | 39×39 | VERT | 2 | 4/3 | 4 (30; 3) | 17.1 / 2.4 / 2.4 | 324 / 18 | 26 | ROT+VERT |
| Grapes | Intl Qual | 30×30 | VERT | 2 | 4/2 | 8 (70; 6) | 10.2 / 15.3 / 0.2 | 225 / 15 | 19 | ROT+VERT |
| Grievance | Sprint 1 | 60×60 | ROT | 2 | 12/12 | 5 (90; 4) | 7.9 / 0.0 / 4.2 | 3481 / 59 | 10 | ROT+VERT |
| Hah | Sprint 1 | 50×25 | VERT | 2 | 4/4 | 4 (48; 3) | 1.1 / 7.4 / 4.6 | 841 / 29 | 24 | ROT+VERT |
| Heart | US Qual | 50×30 | VERT | 2 | 6/6 | 8 (118; 6) | 5.9 / 24.1 / 7.9 | 841 / 31 | 17 | ROT+VERT |
| HideAndSeek | Sprint 2 | 37×31 | ROT | 2 | 4/4 | 16 (70; 12) | 5.9 / 10.7 / 6.8 | 980 / 28 | 11 | ROT+HORI+VERT |
| HotAirBalloon | US Qual | 40×30 | ROT | 2 | 4/4 | 8 (102; 6) | 10.2 / 24.3 / 4.0 | 1154 / 35 | 13 | ROT+HORI+VERT |
| IslandHopping | Intl Qual | 60×30 | VERT | 2 | 4/4 | 8 (124; 6) | 6.2 / 1.3 / 3.9 | 841 / 29 | 28 | ROT+VERT |
| IslandHoppingTwo | US Qual | 59×55 | ROT | 2 | 8/12 | 12 (204; 9) | 58.9 / 2.8 / 1.2 | 1780 / 62 | 28 | ROT+VERT |
| Jail | Sprint 1 | 20×30 | VERT | 1 | 4/4 | 4 (38; 3) | 9.3 / 0.0 / 10.7 | 81 / 13 | 17 | VERT |
| KingdomRush | Sprint 1 | 45×24 | ROT | 2 | 6/6 | 4 (48; 3) | 10.0 / 1.9 / 2.2 | 1296 / 36 | 26 | ROT+VERT |
| Lantern | Sprint 2 | 20×20 | VERT | 1 | 2/2 | 4 (24; 3) | 11.5 / 12.5 / 3.0 | 289 / 17 | 22 | ROT+HORI+VERT |
| LightWork | US Qual | 30×30 | VERT | 2 | 4/4 | 8 (44; 6) | 15.1 / 4.2 / 12.7 | 81 / 17 | 18 | ROT+HORI+VERT |
| Lines | Sprint 2 | 40×40 | VERT | 2 | 4/2 | 4 (58; 3) | 19.1 / 19.3 / 1.4 | 1225 / 37 | 21 | ROT+HORI+VERT |
| LookingGlass | HS/Newbie | 45×30 | VERT | 3 | 6/8 | 8 (90; 6) | 15.9 / 7.1 / 4.7 | 144 / 36 | 26 | ROT+VERT |
| Marsh | Intl Qual | 60×50 | ROT | 1 | 8/8 | 10 (118; 8) | 28.0 / 40.6 / 0.0 | 1450 / 37 | 12 | ROT+HORI+VERT |
| MassiveL | US Qual | 40×40 | ROT | 2 | 6/6 | 12 (132; 9) | 17.6 / 10.5 / 2.3 | 909 / 30 | 23 | ROT+VERT |
| Maze | Sprint 2 | 50×50 | ROT | 3 | 8/10 | 8 (64; 6) | 29.4 / 0.0 / 3.8 | 98 / 13 | 24 | ROT |
| Minefield | Sprint 1 | 60×20 | HORI | 1 | 2/2 | 9 (72; 7) | 15.8 / 19.0 / 5.7 | 121 / 13 | 25 | ROT+HORI+VERT |
| MoonPhases | HS/Newbie | 27×25 | ROT | 2 | 2/4 | 8 (86; 6) | 10.7 / 5.3 / 1.2 | 576 / 24 | 22 | ROT+VERT |
| Movepls | Sprint 1 | 45×30 | ROT | 2 | 4/4 | 4 (30; 3) | 8.1 / 1.9 / 7.0 | 298 / 17 | 23 | ROT+HORI |
| Orbit | Sprint 1 | 25×25 | ROT | 2 | 4/2 | 8 (50; 6) | 14.2 / 0.0 / 4.2 | 256 / 16 | 22 | ROT+VERT |
| PairedProgramming | Default | 45×20 | VERT | 3 | 4/2 | 5 (26; 4) | 10.7 / 12.9 / 4.0 | 144 / 16 | 11 | ROT+VERT |
| Pakbot | Sprint 2 | 30×30 | VERT | 2 | 2/2 | 4 (18; 3) | 31.6 / 4.4 / 1.6 | 289 / 17 | 19 | ROT+VERT |
| Pathfind | Sprint 1 | 45×45 | ROT | 2 | 4/4 | 4 (48; 3) | 13.5 / 2.1 / 8.7 | 68 / 36 | 24 | ROT+VERT |
| Piglets | Sprint 2 | 60×40 | VERT | 2 | 4/4 | 8 (40; 6) | 15.3 / 0.9 / 0.9 | 1521 / 39 | 22 | ROT+VERT |
| Pillars | HS/Newbie | 35×21 | VERT | 2 | 2/2 | 4 (76; 3) | 32.7 / 16.7 / 2.2 | 1024 / 38 | 20 | ROT+VERT |
| PipesAndParabolas | HS/Newbie | 55×45 | HORI | 2 | 6/7 | 8 (149; 6) | 21.2 / 13.4 / 1.5 | 400 / 20 | 23 | HORI+VERT |
| Pit | Sprint 1 | 60×30 | VERT | 2 | 6/4 | 4 (42; 3) | 9.2 / 3.1 / 3.3 | 169 / 21 | 16 | ROT+HORI+VERT |
| Pizza | Sprint 1 | 30×30 | VERT | 2 | 2/4 | 4 (12; 3) | 7.6 / 2.2 / 0.0 | 361 / 19 | 22 | ROT+VERT |
| Potions | US Qual | 40×30 | HORI | 1 | 4/2 | 4 (64; 3) | 29.8 / 1.3 / 2.7 | 49 / 45 | 9 | ROT+HORI+VERT |
| Quiet | Sprint 1 | 20×20 | ROT | 1 | 4/2 | 4 (8; 3) | 11.5 / 3.5 / 5.0 | 338 / 13 | 22 | ROT+HORI+VERT |
| RaceToTheTop | Intl Qual | 31×20 | VERT | 1 | 2/2 | 4 (28; 3) | 39.8 / 16.1 / 12.3 | 900 / 32 | 10 | ROT+HORI+VERT |
| Rainbow | US Qual | 40×30 | VERT | 2 | 4/4 | 20 (112; 15) | 22.3 / 13.0 / 3.0 | 625 / 35 | 10 | ROT+VERT |
| Rectangle | Sprint 1 | 50×30 | ROT | 2 | 6/6 | 4 (44; 3) | 8.0 / 6.4 / 5.3 | 1521 / 39 | 27 | ROT+VERT |
| Repetition | Intl Qual | 55×55 | HORI | 4 | 16/16 | 8 (92; 6) | 24.3 / 12.0 / 2.1 | 36 / 30 | 5 | HORI |
| Resign | US Qual | 30×20 | VERT | 2 | 4/4 | 4 (58; 3) | 16.0 / 14.7 / 5.3 | 225 / 15 | 21 | HORI+VERT |
| ReverseFunnel | HS/Newbie | 40×20 | HORI | 2 | 4/4 | 4 (54; 3) | 8.5 / 9.0 / 18.0 | 121 / 13 | 6 | ROT+HORI+VERT |
| Rewind | Default | 30×30 | ROT | 2 | 4/4 | 6 (34; 5) | 12.2 / 20.7 / 4.7 | 117 / 9 | 5 | ROT+HORI+VERT |
| Risk | Sprint 2 | 20×20 | HORI | 1 | 4/4 | 4 (34; 3) | 19.0 / 18.0 / 7.0 | 225 / 15 | 22 | ROT+HORI+VERT |
| River | Intl Qual | 40×30 | ROT | 3 | 4/4 | 4 (16; 3) | 10.7 / 28.2 / 7.7 | 61 / 15 | 7 | ROT+HORI+VERT |
| RockWall | Intl Qual | 20×30 | VERT | 1 | 2/2 | 14 (42; 11) | 17.7 / 2.0 / 3.3 | 361 / 59 | 10 | ROT+HORI+VERT |
| Sakura | Intl Qual | 45×45 | VERT | 2 | 8/8 | 9 (78; 7) | 22.0 / 3.9 / 5.1 | 1296 / 36 | 24 | ROT+VERT |
| Scatter | Sprint 1 | 50×30 | ROT | 2 | 6/4 | 8 (70; 6) | 8.0 / 1.5 / 2.4 | 157 / 12 | 26 | ROT+VERT |
| Sine | Sprint 2 | 40×20 | ROT | 2 | 4/4 | 6 (38; 5) | 9.0 / 4.3 / 2.8 | 34 / 12 | 18 | ROT |
| SmallElements | Default | 20×20 | ROT | 2 | 4/6 | 4 (24; 3) | 4.0 / 4.0 / 5.5 | 121 / 11 | 26 | ROT+HORI |
| Sneaky | US Qual | 20×20 | ROT | 3 | 2/2 | 4 (24; 3) | 6.0 / 37.0 / 12.0 | 648 / 19 | 8 | ROT+HORI+VERT |
| Snowflake | Sprint 2 | 31×30 | VERT | 2 | 4/4 | 6 (24; 5) | 11.4 / 2.4 / 1.3 | 576 / 24 | 28 | ROT+VERT |
| SomethingFishy | Sprint 2 | 40×30 | VERT | 1 | 2/2 | 5 (52; 4) | 20.8 / 1.7 / 0.8 | 961 / 31 | 23 | ROT+VERT |
| SoundWave | Intl Qual | 40×30 | HORI | 2 | 4/4 | 8 (66; 6) | 20.3 / 9.0 / 2.0 | 49 / 19 | 13 | ROT+HORI |
| Spiderweb | HS/Newbie | 45×45 | ROT | 2 | 6/6 | 16 (318; 12) | 4.4 / 15.1 / 18.4 | 1396 / 36 | 28 | ROT+HORI+VERT |
| Spin | Sprint 2 | 20×20 | ROT | 1 | 2/2 | 4 (20; 3) | 4.5 / 54.5 / 12.5 | 394 / 17 | 13 | ROT+HORI+VERT |
| Spiral | Sprint 2 | 30×30 | ROT | 2 | 4/4 | 4 (78; 3) | 13.1 / 4.4 / 2.2 | 370 / 19 | 25 | ROT+VERT |
| Spots | HS/Newbie | 60×60 | HORI | 2 | 8/8 | 8 (142; 6) | 14.7 / 17.2 / 4.9 | 2401 / 49 | 14 | ROT+HORI |
| Squares | Sprint 2 | 40×40 | ROT | 1 | 2/2 | 4 (28; 3) | 21.0 / 0.9 / 1.0 | 10 / 3 | 22 | ROT |
| Star | Sprint 2 | 30×30 | VERT | 2 | 4/4 | 5 (16; 4) | 7.6 / 4.2 / 2.2 | 441 / 21 | 25 | HORI+VERT |
| Sun | Sprint 1 | 25×25 | ROT | 1 | 4/3 | 4 (22; 3) | 9.9 / 2.6 / 7.4 | 800 / 23 | 25 | ROT+HORI+VERT |
| Sus | Sprint 2 | 40×20 | VERT | 1 | 2/2 | 4 (16; 3) | 15.5 / 2.8 / 1.5 | 961 / 31 | 22 | ROT+HORI+VERT |
| SweetDreams | Sprint 2 | 35×35 | VERT | 1 | 4/4 | 8 (54; 6) | 12.1 / 12.7 / 2.6 | 400 / 20 | 26 | ROT+HORI+VERT |
| Swooshy | HS/Newbie | 50×41 | HORI | 2 | 6/4 | 8 (108; 6) | 21.2 / 13.2 / 2.8 | 676 / 40 | 28 | ROT+HORI |
| Tacocat | Sprint 1 | 60×20 | VERT | 2 | 4/4 | 8 (22; 6) | 13.2 / 5.0 / 2.5 | 729 / 27 | 27 | ROT+VERT |
| Target | US Qual | 60×60 | ROT | 2 | 4/4 | 12 (154; 9) | 42.4 / 7.8 / 2.6 | 3481 / 59 | 10 | ROT+HORI |
| ThirtyFive | Intl Qual | 48×47 | ROT | 3 | 6/6 | 35 (232; 27) | 71.5 / 2.4 / 3.0 | 1289 / 33 | 15 | ROT+VERT |
| TicTacToe | Sprint 2 | 30×30 | VERT | 2 | 8/8 | 4 (36; 3) | 16.2 / 6.9 / 4.7 | 324 / 19 | 20 | HORI+VERT |
| Tightrope | US Qual | 50×20 | VERT | 1 | 2/2 | 4 (32; 3) | 58.0 / 8.0 / 1.8 | 2401 / 49 | 14 | ROT+VERT |
| TimesUp | Intl Qual | 20×30 | VERT | 2 | 4/4 | 8 (60; 6) | 42.7 / 23.7 / 2.7 | 361 / 19 | 7 | ROT+VERT |
| TreasureMap | Intl Qual | 21×21 | ROT | 1 | 2/2 | 4 (12; 3) | 7.5 / 8.2 / 9.1 | 256 / 16 | 27 | ROT+VERT |
| Turtle | Default | 40×40 | VERT | 2 | 4/2 | 6 (52; 5) | 15.3 / 5.3 / 1.8 | 533 / 23 | 19 | HORI+VERT |
| USA | Sprint 2 | 20×31 | HORI | 1 | 2/2 | 8 (124; 6) | 2.7 / 51.5 / 0.0 | 484 / 28 | 12 | ROT+HORI+VERT |
| VeryReasonable | HS/Newbie | 26×20 | VERT | 1 | 4/4 | 4 (48; 3) | 15.4 / 28.1 / 4.6 | 441 / 21 | 27 | ROT+VERT |
| Zig | HS/Newbie | 29×25 | HORI | 2 | 6/5 | 8 (85; 6) | 19.6 / 27.4 / 0.0 | 144 / 22 | 17 | HORI+VERT |
| maptestsmall | Default | 20×20 | ROT | 1 | 10/10 | 6 (6; 5) | 3.5 / 0.5 / 0.0 | 162 / 9 | 26 | ROT |

---

## 5. Spec disagreements

1. **Symmetry guarantee (SPEC:46, "it is guaranteed that the world is symmetric either by rotation or
   reflection").** The engine does not enforce it at run time: no symmetry check exists in `Server.java:244-439`. The
   only enforcing code, `MapBuilder.assertIsValid` (`MapBuilder.java:287-291`), uses island-ID and current conventions
   that reject all 103 shipped maps. In practice all shipped maps are geometrically symmetric (`CENSUS:sym_all`). A
   custom map that breaks symmetry would run.
2. **"Each team has 1-4 fixed headquarters" (SPEC:70; `GameConstants.java:31-35` "per team").** The run-time check is
   on the total, 2 ≤ total ≤ 32 (`Server.java:272-278`, using `MAX_STARTING_HEADQUARTERS * 8`, which looks like a bug
   for `* 2`). It checks neither the per-team count nor the balance. The shipped maps comply (1–4 each, always equal).
3. **"Islands appear as groups of connected squares" (SPEC:66).** The engine requires 4-connectivity
   (`Server.java:230-242`). Distinct islands may touch diagonally, and do on 4 maps. The spec does not say which kind of
   connectivity it means.
4. **The stored symmetry field does not always match the map.** FourNations is stored as ROTATIONAL but is only
   VERTICAL-consistent (fact 20). The spec does not describe the field; this is a data error, flagged for completeness.
5. **The adamantium guarantee differs between the two engine validators.** SPEC:78 and the run-time validator say
   "within 100 units" (`Server.java:344-365`). `MapBuilder.assertIsValid` requires one *within HQ vision (34)*
   (`MapBuilder.java:293-318`). The constant's Javadoc calls it "The minimum distance from a headquarter to the nearest
   adamantium well" (`GameConstants.java:49`), but the code uses it as a maximum. The run-time behaviour, a maximum of
   100, governs, and 38 maps give no HQ an adamantium well inside vision.
6. **Where the origin is.** SPEC:44 says (0,0) is the bottom-left, which agrees with `Direction.NORTH` = +y. The
   `LiveMap.getOrigin` Javadoc says "upper left corner" (`LiveMap.java:311-318`). This is only a comment; the
   behaviour follows the spec.
7. **Constraints the spec leaves out (omissions, not contradictions).** The engine also forbids clouds on walls
   (`Server.java:283-284`) and currents that point off the map or into a wall (`Server.java:430-433`). SPEC:58 states
   only the unique-destination rule. The spec does not mention that HQs may sit on clouds, which is allowed and
   happens on 11 maps, or that wells may sit on clouds (allowed, 24 maps). Both have large sensing and spawning
   consequences (facts 44–45).
8. **"Each headquarter will have at least one adamantium well located within 100 units" (SPEC:78).** Consistent
   (inclusive). **"All maps are guaranteed to have at least one adamantium well and one mana well."** Consistent: it
   follows from `Server.java:344-411`. **"Wells of a specific type cannot constitute more than 4%"** (SPEC:82):
   consistent, enforced as count ≤ `(int)(W*H*0.04f)`. **4–35 islands of at most 20 tiles** (SPEC:68): consistent.
   **Map size 20–60** (SPEC:44): consistent. **No current on an HQ, and no current, HQ or wall on a well**
   (SPEC:70, 72): consistent.

---

## 6. Surprises: mechanics a bot designer could easily get wrong

1. **HORIZONTAL means y flips and VERTICAL means x flips.** The names refer to the mirror line, not the direction
   tiles move (`MapBuilder.java:130-150`). VERTICAL maps are mostly wide (left half against right half).
2. **Mirror currents geometrically, not with `opposite()`.** Under a reflection the mirrored current is reflected
   (for example, NE becomes SE under HORIZONTAL), not reversed. The engine's own `MapBuilder` gets this wrong
   (fact 17). Predicting enemy-side currents with `opposite()` is wrong on 41 of 54 reflection maps that have
   currents.
3. **The engine will not tell you the symmetry, and your HQs usually cannot work it out on round 1.** Own HQ
   positions settle it on 0 maps. HQ vision settles it on only 10/103 maps and leaves all three possible on 28. Plan
   to keep scouting and to rule out candidates, not to guess once.
4. **Island IDs say nothing about the mirrored island.** IDs are 1..N on shipped maps, but there is no mirror rule
   (only 5/103 maps use id↔N+1−id).
5. **Well types can break a symmetry that positions satisfy.** On FourNations, rotation maps each well position onto
   a well but swaps adamantium and mana; only VERTICAL is right. Check well type, not just position, when ruling out
   symmetries. Cornucopia is genuinely both ROT and HORI, so a bot must handle a tie.
6. **An HQ on a cloud is nearly blind and cramped:** vision radius² 4, and spawning only within dist² 4. Cloud tiles
   at dist² 5–9 can never be spawn targets for any HQ. This affects 11 maps; on River all six HQs sit on clouds.
   `canBuildRobot` simply returns false for those tiles.
7. **Which team moves first is set by the map.** The lowest map-file HQ ID acts first: team B on 59/103 maps, team A
   on 44. With alternate-order, the same IDs change hands. HQ IDs are small integers, not ≥10000.
8. **Opposing HQs can start almost touching:** BowAndArrow d² 4 (each inside the other's action radius 9), Squares
   d² 10, and 13 maps with d² ≤ 100. Spawn-tile safety and HQ damage matter from round 1.
9. **The adamantium guarantee is d² ≤ 100, not "visible".** On 38 maps no HQ sees an adamantium well at spawn. There
   is **no mana guarantee near HQs at all**: on 37 maps some HQ's nearest mana well is beyond d² 100 (Forest: 328),
   and on 62 maps no HQ sees mana at spawn.
10. **The conquest threshold is ceil(0.75·N) anchors placed at the same time,** using `getIslandCount()`. Most maps
    need 3 (N = 4) or 6 (N = 8); ThirtyFive needs 27.
11. **Islands can be fully covered by currents or clouds** (Spiderweb: every island tile is a current; USA, Lines,
    Sakura: every island tile is a cloud). Currents push occupants off islands at the end of every round, which
    matters because anchor health depends on occupancy.
12. **Small islands change hands fast.** Health changes by `floor(100*(own−enemy)/area)` per round, so one robot on a
    1-tile island moves it by ±100 a round (HideAndSeek, RockWall).
13. **Two islands can touch diagonally** (Flower, Spiderweb, ThirtyFive). Identify islands by `senseIsland` ID, not
    by 8-connected flood fill.
14. **Pathing:** 14 maps have sealed pockets (Cat: 814 unreachable tiles), and PipesAndParabolas has 108 tiles only
    one team can reach. Explorers should not chase those. Every well and island is reachable on the shipped maps, but
    the engine does not guarantee it.
15. **A current pointing into an HQ is legal** (BowAndArrow, Rewind). A robot on that tile is never moved.
16. **Maps never change game length.** It is always 2000 rounds, whatever the map.
17. **Validation is a server option.** Custom or local test maps can break every guarantee if
    `bc.server.validate-maps=false`, and the symmetry guarantee is never checked even when it is true.

---

## 7. UNVERIFIED / caveats

- **Tournament labels** come from the client (`CLIENT/constants.ts:158-261`), not the engine. Whether each map was
  actually played in that tournament is UNVERIFIED. No FINAL maps are in the jar.
- **Server settings for official matches** (validate-maps, alternate-order) are UNVERIFIED. Only the defaults were
  checked (`Config.java:52-53`).
- **The round-1 symmetry model** assumes every HQ learns all its own team's HQ locations through the shared array on
  round 1, and it treats island tiles by presence only. It is an analysis model, not an engine fact.
- **Reachability** treats walls and HQs as blocking and ignores currents (which only move a robot to an adjacent
  non-wall tile, so they add no connectivity) and the movement cooldown from clouds. Spawn tiles follow fact 45.
