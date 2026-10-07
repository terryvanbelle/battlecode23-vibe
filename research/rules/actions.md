# Battlecode 2023 (Tempest): actions, sensing and the RobotController API, checked against the engine

Area: **actions**. These are all public `RobotController` methods as implemented in `RobotControllerImpl`, with the
legality clauses, cooldowns, sensing radii, cloud rules, the order results come back in, and bytecode costs.

## Provenance conventions

All source paths are relative to
`/home/terryvanbelle/projects/vibe/reference/battlecode23/engine/src/main/battlecode/` (git master af42086, 2023-02-05).

| Abbrev | File |
|---|---|
| RCI | `world/RobotControllerImpl.java` |
| IR  | `world/InternalRobot.java` |
| IC  | `world/robots/InternalCarrier.java` |
| GW  | `world/GameWorld.java` |
| INV | `world/Inventory.java` |
| ISL | `world/Island.java` |
| WELL| `world/Well.java` |
| TI  | `world/TeamInfo.java` |
| OI  | `world/ObjectInfo.java` |
| GC  | `common/GameConstants.java` |
| RT  | `common/RobotType.java` |
| AN  | `common/Anchor.java` |
| ML  | `common/MapLocation.java` |
| MI  | `common/MapInfo.java` |
| RC  | `common/RobotController.java` (the interface javadoc) |
| MC  | `instrumenter/bytecode/resources/MethodCosts.txt` |
| IMV | `instrumenter/bytecode/InstrumentingMethodVisitor.java` |
| SPEC| `/home/terryvanbelle/projects/vibe/reference/battlecode23/specs/specs.md.html` |

### The jar matches the source (checked)

- I compiled `battlecode/common/*.java`, `battlecode/world/*.java` and `battlecode/world/robots/*.java` with JDK 8 javac against
  `battlecode23-3.0.15.jar`. I then diffed `javap -c -p -constants` of every resulting class against the same class in the jar, with
  constant-pool indices removed.
  - **Every class in `battlecode.common` and `battlecode.world` is bytecode-identical.** That includes RobotControllerImpl,
    InternalRobot, robots.InternalCarrier, GameWorld, Inventory, Island, Well, TeamInfo, ObjectInfo, RobotType, GameConstants and MapInfo.
  - The one exception is `GameMapIO$Serial`. Its only difference is the slot order of the local variable `final int rounds = 2000`
    (GameMapIO.java:228), so the behaviour is the same and it is outside this area.
  - Because the bytecode is identical, the source line numbers below also hold for the jar.
- `MethodCosts.txt` inside the jar is byte-identical to the source copy (`diff` printed nothing).
- The jar was built `Sun Feb 05 22:36 UTC 2023` and `battlecode_version` = `3.0.15`. However
  `javap -constants battlecode.common.GameConstants` shows `SPEC_VERSION = "3.0.14"` (GC:13), and the spec header also says 3.0.14.
- Jar RobotType constants, from `javap -c battlecode.common.RobotType` `<clinit>`. Columns are
  BCA, BCM, BCE, actionCD, moveCD, HP, dmg, actionR², visionR², bytecodes:
  - HEADQUARTERS 0,0,0,**2**,-1,1,4,9,34,20000
  - CARRIER 50,0,0,10,0,150,0,9,20,12500
  - LAUNCHER 0,45,0,10,20,200,20,16,20,10000
  - DESTABILIZER 0,0,200,**70**,**25**,300,50,13,20,10000
  - BOOSTER 0,0,150,**140**,25,400,0,-1,20,10000
  - AMPLIFIER 30,15,0,-1,15,120,0,-1,34,10000

  These match RT:21-66.

---

## 1. Cooldown machinery (applies to every action)

1. **Ready test.** An action is allowed iff `actionCooldownTurns < 10`, and a move iff `movementCooldownTurns < 10`
   (IR:223-232, GC:118 `COOLDOWN_LIMIT=10`). No per-turn action counter exists anywhere. Only cooldown limits how often a robot can act.
2. **Decrement.** Both cooldowns drop by 10, floored at 0, at the **start of the robot's own turn** (`processBeginningOfTurn`, IR:425-429;
   GC:121).
3. **Spawn state.** A new robot starts with both cooldowns at 10 (IR:74-75), so they are 0 on its first turn.
   - Robots built this round do **not** run until the next round. `eachDynamicBodyByExecOrder` iterates a snapshot of the exec-order
     list taken before the loop (OI:95-110), and new IDs are appended at the end (OI:161).
4. **Cooldown cost.** Every action adds `(int)Math.round(base * multiplier[tile][team])` (GW:498-500, IR:327-330).
   - For **actions**, `tile` is the robot's current location.
   - For **moves**, the cooldown is added *after* `setLocation`, so the multiplier is the one at the **destination** tile (RCI:659-664, IR:344-347).
5. **Multiplier.** The multiplier starts at 1.0 per (tile, team). Contributions:
   - cloud: +0.2 for both teams (GW:136-143)
   - each own boost: −0.1, capped at 3 stacks (GW:327-339)
   - each enemy destabilize: +0.1, capped at 2 stacks (GW:351-362)
   - own accelerating anchor: −0.15, capped at 1 stack (GW:374-387)

   The value is rounded to 2 decimals after each change. The constants are at GC:140-155.
6. **Carrier base movement cooldown** = `floor(0.375f*weight) + 5` (IR:332-339, GC:108-111), where weight is the inventory weight at the
   moment of the move. Other types use `RobotType.movementCooldown`.
   - Table: w 0-2→5, 3-5→6, 6-7→7, 8-10→8, 11-13→9, 14-15→10, 16-18→11, 19-21→12, 22-23→13, 24-26→14, 27-29→15, 30-31→16,
     32-34→17, 35-37→18, 38-39→19, 40→20.
   - Consequence: a carrier with weight ≤ 13 can make **2 moves in one turn** from cooldown 0, because the first move leaves it at ≤ 9 < 10.
     At weight ≤ 2 it sustains 2 tiles/turn. At weight 14-15 it makes exactly 1 move/turn. At weight 40 it makes 1 move per 2 turns.
7. **Worked numbers at base multiplier 1.0:**
   - Carrier action 10, so 1 action/turn.
   - Launcher: attack 10 (1/turn), move 20 (1 per 2 turns).
   - HQ action 2, so **5 builds/anchors per turn** (0→2→4→6→8→10).
   - Destabilizer action 70: next action 7 turns later.
   - Booster action 140, but it is computed *after* its own boost is applied, so 126. Next boost comes 12 turns later (RCI:813-819 orders
     `addBoost` before `addActionCooldownTurns`).
8. **With multipliers below 1, a robot can act twice in a turn.** Example: a carrier under one boost has action cost round(10·0.9) = 9,
   so 0→9 still leaves it ready and it acts again (→18). This is how a carrier can collect or transfer twice per turn.
   - Three boosts: round(10·0.7) = 7.
   - Three boosts plus an anchor: round(10·0.55) = 6.
   - Cloud: round(10·1.2) = 12, so a carrier inside a cloud acts on 5 of every 6 turns.

## 2. Movement

### `move(Direction dir)` / `canMove(dir)`

Legality checks are made in this order (RCI:633-648):

1. `dir != null`, otherwise NullPointerException.
2. Movement ready (cooldown < 10), otherwise `IS_NOT_READY`.
3. Not a HEADQUARTERS, otherwise `CANT_DO_THAT`.
4. `adjacentLocation(dir)` is on the map, otherwise `OUT_OF_RANGE`.
5. Not occupied, otherwise `CANT_MOVE_THERE`. This goes through `isLocationOccupied`, which requires sensing the tile; adjacent tiles
   are always within r² 2 ≤ 4, so this never fails because of clouds.
6. Passable (not a wall), otherwise `CANT_MOVE_THERE`.

Effects and notes:
- `move(Direction.CENTER)` is illegal: the target is the robot's own tile, which is occupied by itself.
- Wells, islands and current tiles are all enterable. Only walls and robots block, and HQs block because they occupy their tile.
- Effect: the location changes immediately, then the movement cooldown is added using the destination multiplier (RCI:659-664).
- Bytecode: `canMove` 10, `move` 0 (MC:32, MC:68).

## 3. Building (HQ only)

### `buildRobot(RobotType type, MapLocation loc)` / `canBuildRobot`

Legality checks are made in this order (RCI:670-697):

1. `type != null`.
2. `assertCanActLocation(loc)`: `dist²(HQ, loc) ≤ 9`, otherwise `OUT_OF_RANGE`; then on the map, otherwise `CANT_SENSE_THAT` (RCI:190-198, IR:246-248).
3. Action ready.
4. The caller is a HEADQUARTERS.
5. `type != HEADQUARTERS`.
6. For each of AD, MN and EX, **this HQ's own inventory** holds at least `type.getBuildCost(r)`, otherwise `NOT_ENOUGH_RESOURCE`
   (RCI:681-688, RCI:131-133).
7. Not occupied. This uses `isLocationOccupied`, so the tile **must be sensable**.
8. `sensePassability(loc)` is true. This also requires sensing.

Notes:
- **Spawn tiles are the 28 tiles with 1 ≤ dist² ≤ 9 from the HQ** (the HQ's own tile is occupied). Each must be on the map, not a wall,
  unoccupied and sensable.
- Because of the cloud rule, a spawn tile that is a cloud, or any tile when the HQ itself is on a cloud, must be within dist² ≤ 4.
  Otherwise `isLocationOccupied` throws `CANT_SENSE_THAT` (IR:271-277).
- Spawning onto wells, island tiles and current tiles is allowed.
- Effect (RCI:707-719):
  1. Adds the HQ action cooldown: `getType().actionCooldown` = **2**, the building HQ's own value, not the built type's (RT:21).
  2. Deducts the cost from **this HQ's** inventory and from the team totals (IR:141-145).
  3. Spawns immediately. Carriers are created as `InternalCarrier` (GW:788-809).
- Costs: carrier 50 AD; launcher 45 MN; destabilizer 200 EX; booster 150 EX; amplifier 30 AD + 15 MN (RT:31-66).
- Bytecode: `canBuildRobot` 10, `buildRobot` 0 (MC:29, MC:27).

### `buildAnchor(Anchor anchor)` / `canBuildAnchor`

- Legality (RCI:721-735), in order:
  1. `anchor != null`.
  2. Action ready.
  3. The caller is a HQ.
  4. For each resource, the HQ inventory holds at least the anchor cost. There is no location argument.
- Costs (AN:16,21; constructor order is `manaCost, adamantiumCost, elixirCost` at AN:80):
  - STANDARD: 80 MN + 80 AD.
  - ACCELERATING: 300 EX.
- Effect: adds an action cooldown of 2 (HQ), deducts the resources, and adds the anchor to the HQ's inventory (RCI:746-757).
  The HQ inventory has no capacity limit (`new Inventory()` with maxCapacity −1, IR:56-58, INV:27-29, INV:142-146).
- Bytecode: `canBuildAnchor` 10, `buildAnchor` 0 (MC:33, MC:69).

## 4. Attacking

### `attack(MapLocation loc)` / `canAttack(loc)`

Legality checks are made in this order (RCI:763-776):

1. `loc != null`.
2. `dist² ≤ actionRadiusSquared` (launcher 16, carrier 9), otherwise `OUT_OF_RANGE`; then on the map.
3. Action ready.
4. `getType().canAttack()`, which is true only for CARRIER and LAUNCHER (RT:129-132).
5. For a carrier, `getWeight() > 0` (resources plus 40 per anchor).

General notes:
- **No vision requirement.** The target may be an unsensable clouded tile.
- Attacking an empty tile, a friendly robot or **any HQ is legal**: it consumes the cooldown and does no damage (IR:404-414, IC:62-73).
- Effect: the action cooldown (10 for both types) is added *before* the damage is resolved (RCI:787-791).

**Launcher** (IR:404-414):
- Deals `RobotType.LAUNCHER.damage` = 20 to the robot on `loc` if it is an enemy and not a HQ.
- `addHealth` ignores HQs (IR:373-375).
- If health drops to ≤ 0, `destroyRobot` runs immediately (IR:379-380). The target's resources are subtracted from its team totals
  (GW:828-830).

**Carrier throw** (IC:35-73):
- `damage = (int)Math.floor(1.25f * weight)` with `weight = 40*anchors + AD + MN + EX` (IC:47-50, INV:134-137). The maximum is 50.
- **The whole inventory is thrown.** All resources *and all anchors* are removed from the carrier and from the team totals
  (IC:35-45, IC:72). This happens **even when the target is empty, friendly or a HQ** (IC:72 is outside the if/else).
- A carrier holding an anchor throws it (50 damage) and the anchor is destroyed.
- You cannot choose how much to throw.

Bytecode: `canAttack` 5, `attack` 0 (MC:28, MC:26).

## 5. Booster and destabilizer

### `boost()` / `canBoost()`

- Legality (RCI:797-802): action ready, and the caller is a BOOSTER. There is no location argument, no action-radius check
  (booster actionR² = −1), and no vision check.
- Effect (RCI:813-819, GW:327-339):
  1. Every tile within **r² 20 of the booster's current location** gets an entry with `lastRound = round+10`.
  2. The own team's multiplier drops by 0.1 if the tile had fewer than 3 entries.
  3. The booster's action cooldown (140) is then added **with the new boost already in effect**.
- Expiry: at the end of round R, entries with `lastRound ≤ R+1` are removed. A boost cast in round R is therefore active from that
  moment through the end of round R+9 (GW:659-671).
- Bytecode: `canBoost` 10, `boost` 0 (MC:41, MC:98).

### `destabilize(MapLocation loc)` / `canDestabilize(loc)`

- Legality (RCI:825-832):
  1. `loc != null`.
  2. `dist² ≤ 13`, then on the map.
  3. Action ready.
  4. The caller is a DESTABILIZER.

  There is no vision requirement and no requirement that an enemy be present.
- Effect (GW:351-362):
  1. Every tile within **r² 15 of `loc`** gets an entry in the *opponent's* destabilize list with `lastRound = round+5`.
  2. The opponent's multiplier rises by 0.1 if the tile had fewer than 2 entries.
  3. Then an action cooldown of 70 is added (RCI:843-848).
- Damage (GW:672-688): at the **end of round R+4** (when `lastRound ≤ R+1`), **each expiring entry** deals 50 to whatever robot of the
  affected team stands on that tile *at that moment*.
  - Damage is **not** capped at 2 stacks. Three destabilizes on one tile deal 150. Only the multiplier is capped.
  - HQs are immune (IR:373-375).
- Bytecode: `canDestabilize` 10, `destabilize` 0 (MC:42, MC:99).

## 6. Carrier resource actions

### `collectResource(MapLocation loc, int amount)` / `canCollectResource`

Legality checks are made in this order (RCI:925-950):

1. `loc != null`.
2. dist² ≤ 9 and on the map.
3. Action ready.
4. `amount ≥ -1` (anything below −1 gives `CANT_DO_THAT`).
5. The caller is a CARRIER.
6. `loc` is a well (GW:852-857).
7. `isAdjacentTo(loc)`. This includes **standing on the well** (dx, dy ≤ 1, ML:129-133).
8. `amount = (amount == -1 ? well.getRate() : amount)`, and `amount ≤ rate`.
9. `inventory.canAdd(amount)`, meaning weight + amount ≤ 40 (INV:142-146).

Semantics:
- **`-1` means exactly `rate`** (1, or 3 if the well is upgraded; WELL:90-92, GC:159-160). It is **not** "as much as fits".
  A carrier at weight 39 at an upgraded well fails with `-1` and must pass `1`. The javadoc's "-1 to collect max possible" is misleading.
- `amount == 0` is **legal**: it burns a full action cooldown and collects nothing.
- The collected type is the well's *current* type, which may have converted to ELIXIR (RCI:965).
- Wells are infinite and unaffected by collection. There is no per-well limit on the number of carriers or collections per round.
- Effect: adds an action cooldown of 10 (×multiplier) and adds the amount to the carrier's inventory and the team totals (RCI:961-973).
- **Collections per turn:** one at multiplier 1.0. Two or more are possible when the multiplier is below 1 (§1.8).
- Bytecode: `canCollectResource` 10, `collectResource` 0 (MC:30, MC:66).

### `transferResource(MapLocation loc, ResourceType rType, int amount)` / `canTransferResource`

Legality checks are made in this order (RCI:862-898):

1. `loc != null` and `rType != null`.
2. dist² ≤ 9 and on the map.
3. Action ready.
4. The caller is a CARRIER.
5. `amount != 0`.
6. If `amount > 0`: the carrier holds at least `amount` of `rType`.
7. `isAdjacentTo(loc)`.
8. If `amount < 0`, which **withdraws from a HQ**:
   - `canAdd(-amount)`.
   - `loc` is a HQ.
   - The HQ is the carrier's **own team**.
   - The HQ holds at least `-amount`.
9. `loc` is a well or a HQ.

Effect (RCI:908-923):
- Adds an action cooldown of 10 (×multiplier).
- Moves `amount` into the well or HQ inventory and `-amount` into the carrier's.
- A whole stack of any size moves in **one action**. Two resource types need two actions.

Notes:
- **Positive transfers have no team check.** A carrier can deposit into the **enemy HQ**, and the resources become the enemy's
  (IR:141-145 credits the HQ's team).
- Negative transfers let carriers move resources **between your own HQs**, whose stockpiles are otherwise separate.
- Transfers to a well ("throwing in") are cumulative and permanent in the well's inventory (WELL:38-64):
  - MN well: ≥ 600 AD turns it into ELIXIR; ≥ 1400 MN upgrades it to rate 3.
  - AD well: ≥ 600 MN turns it into ELIXIR; ≥ 1400 AD upgrades it.
  - ELIXIR well: ≥ 1400 EX upgrades it. AD or MN thrown into an elixir well is wasted.
  - `isUpgraded` survives the conversion to elixir.
  - Thrown resources leave the team totals.
- Bytecode: `canTransferResource` 10, `transferResource` 0 (MC:31, MC:67).

## 7. Anchor actions (carrier side)

The API has **no `transferAnchor`**. The SPEC "Actions and Cooldowns" section names `transferAnchor()`, but no such method exists in
the interface (javap of `battlecode.common.RobotController` in the jar). Anchors move only through `takeAnchor`, `returnAnchor` and
`placeAnchor`.

### `takeAnchor(MapLocation loc, Anchor anchor)` / `canTakeAnchor`

- Legality (RCI:1014-1044), in order:
  1. `loc != null` and `anchor != null`.
  2. dist² ≤ 9 and on the map.
  3. Action ready.
  4. The caller is a CARRIER.
  5. `loc` is a HQ.
  6. The HQ is on the same team.
  7. Adjacent.
  8. The HQ holds at least 1 anchor of **that type**.
  9. `canAddAnchor()`, i.e. weight + 40 ≤ 40, so **the carrier must be completely empty** (IR:165-167).
- Effect: the HQ loses the anchor, the carrier gains it, and an action cooldown of 10 is added (RCI:1055-1062).
- Bytecode: `canTakeAnchor` 10, `takeAnchor` 0 (MC:34, MC:70).

### `returnAnchor(MapLocation loc)` / `canReturnAnchor`

- Legality (RCI:1064-1087):
  1. `loc != null`.
  2. dist² ≤ 9 and on the map.
  3. Ready.
  4. CARRIER.
  5. HQ at `loc`.
  6. Same team.
  7. Adjacent.
  8. Holding an anchor.
- Effect: moves the held anchor (STANDARD preferred if somehow both are held, IR:155-163) to the HQ, and adds an action cooldown of 10
  (RCI:1099-1107).
- Bytecode: `canReturnAnchor` 10, `returnAnchor` 0 (MC:36, MC:72).

### `placeAnchor()` / `canPlaceAnchor()`

- Legality (RCI:975-991):
  1. Action ready.
  2. The caller is a CARRIER.
  3. **Its own tile** is an island tile.
  4. It holds an anchor.
  5. `island.canPlaceAnchor(team)`: fails only if the island has an anchor **and** is owned by the other team (ISL:60-66).
- Effect (ISL:75-88, RCI:1002-1012):
  1. `teamOwning = team`.
  2. If the island did not already hold an ACCELERATING anchor and the new one is ACCELERATING, `addBoostFromAnchor` applies −0.15 to
     every tile within r² 4 of any island tile.
  3. `anchorPlanted = new`, health = full (250 or 750).
  4. The team's "anchors placed" counter increments **only if the team did not already own the island**.
  5. The carrier loses the anchor.
  6. An action cooldown of 10 is added, computed *after* the new anchor's boost is in place.
- Re-anchoring your own island is legal: it resets health and lets you upgrade STANDARD to ACCELERATING.
- Bytecode: `canPlaceAnchor` 10, `placeAnchor` 0 (MC:35, MC:71).

## 8. Communication

- `readSharedArray(i)`: requires `0 ≤ i < 64`, otherwise `CANT_DO_THAT` (RCI:1113-1128). Any robot can read from anywhere. Bytecode 2 (MC:74).
- `writeSharedArray(i, v)` / `canWriteSharedArray(i, v)` (RCI:1130-1150), checked in order:
  1. `0 ≤ i < 64`.
  2. `0 ≤ v ≤ 65535` (GC:63-66).
  3. `gameWorld.inRangeForAmplification(robot)` (GW:863-892). This is true iff **any** of:
     - the writer is a HQ or an AMPLIFIER (no position check at all);
     - an own-team AMPLIFIER is within dist² ≤ 20;
     - an own-team HQ is within dist² ≤ 9;
     - an island **currently owned by the writer's team** (`island.getTeam()==team`) has some tile within dist² ≤ 4.

  The distances are true geometric distances. Clouds and vision do not matter.
- The write is applied **immediately** to the team array (TI:211-213). Robots later in the same round read the new value. There is no
  per-round reset (TI:40, only initialised once).
- There is no limit on writes per turn and no cooldown cost.
- Bytecode: `writeSharedArray` **75**, `canWriteSharedArray` 10 (MC:100, MC:43).

## 9. Other actions

- `disintegrate()` throws `RobotDeathException` (RCI:1158-1161), which **extends `VirtualMachineError`**
  (instrumenter/RobotDeathException.java:10), so `catch (Exception e)` will not stop it.
  - The sandbox sets `terminated` (instrumenter/SandboxedRobotPlayer.java:202-206).
  - `GameWorld.updateRobot` then destroys the robot right after its turn (GW:220-223).
  - `destroyRobot` subtracts its resources from the team totals (GW:828-830). Held anchors vanish.
  - Bytecode 0 (MC:44).
- `resign()` destroys every robot of the caller's team, then `setWinner(opponent, RESIGNATION)` (RCI:1163-1173). Bytecode 0 (MC:75).
- `setIndicatorString(s)`: truncated to 64 chars (RCI:1179-1185, GC:60). A **null string throws NullPointerException** (`string.length()`).
  - The string is reset to "" at the start of each round (IR:421-423) and recorded at the end of the robot's turn (IR:431-437).
  - Bytecode 0 (MC:97).
- `setIndicatorDot(loc, r, g, b)` and `setIndicatorLine(a, b, r, g, b)`: these only null-check their locations (RCI:1187-1198).
  - There is no count limit and no on-map check, and nothing is recorded when indicators are disabled (server/GameMaker.java:677-701).
  - Bytecode 0 (MC:95-96).

## 10. Sensing

### Vision rule (`InternalRobot.canSenseLocation`, IR:271-277)

- `r²` = the type's vision radius (HQ 34, Amplifier 34, all others 20).
- **If the target tile is a cloud OR the robot's own tile is a cloud, `r²` = 4** (GC:137).
- The test is then `dist²(robot, target) ≤ r²`.
- `assertCanSenseLocation` also requires the location to be on the map, otherwise `CANT_SENSE_THAT` (RCI:180-188).

### Result order

Every "nearby" method that scans an area uses `GameWorld.getAllLocationsWithinRadiusSquaredWithoutMap` (GW:462-479). It scans
**x from low to high (outer loop) and, within each x, y from low to high (inner loop)**, over a bounding box clipped to the map.
- Results are therefore in column-major order from the south-west. They are **not sorted by distance** and are deterministic.
- The RC javadoc says "no particular order".

### Radius argument (all `senseNearby*` overloads that take one)

- `-1` means the vision radius. Values below −1 throw `CANT_DO_THAT` (RCI:250-254).
- Otherwise the radius used is `min(r, visionRadiusSquared)` *around `center`*, which defaults to the robot's own location.
- Each result is *also* filtered by `canSenseLocation` from the robot's real position, so a `center` far away cannot extend vision.

### Method table

| Method | Rules / returns | Provenance | Bytecode (MC) |
|---|---|---|---|
| `onTheMap(loc)` | Map bounds only. No vision check, no exception except NPE. | RCI:172-178 | 5 (MC:73) |
| `canSenseLocation(loc)` | On map + vision rule. | RCI:200-206 | 5 (MC:37) |
| `canActLocation(loc)` | `dist² ≤ actionR²` and on map. Always false for Booster/Amplifier (actionR² −1). | RCI:208-214, IR:246-248 | 5 (MC:38) |
| `isLocationOccupied(loc)` | Throws if not sensable. Otherwise true if any robot (incl. HQ, incl. self) is there. | RCI:216-220 | 5 (MC:63) |
| `canSenseRobotAtLocation(loc)` | `isLocationOccupied`, with false on exception. | RCI:222-227 | 5 (MC:40) |
| `senseRobotAtLocation(loc)` | Throws if not sensable. Returns `null` if empty. | RCI:229-234 | 15 (MC:87) |
| `canSenseRobot(id)` | The robot exists and its tile passes `canSenseLocation`. | RCI:236-240 | 5 (MC:39) |
| `senseRobot(id)` | Throws `CANT_SENSE_THAT` if `!canSenseRobot`. | RCI:242-248 | 25 (MC:86) |
| `senseNearbyRobots()`, `(r)`, `(r, team)`, `(center, r, team)` | Excludes self. `team == null` means all teams. Includes HQs. Filters by vision and cloud. Column-major order. No-arg version never throws. | RCI:256-297, GW:427-435 | 100 for every overload (MC:85) |
| `sensePassability(loc)` | Throws if not sensable. `!wall`. | RCI:299-303 | 5 (MC:88) |
| `senseIsland(loc)` | Throws if not sensable. Island ID, or **−1** if none. | RCI:305-310 | 20 (MC:76) |
| `senseNearbyIslands()` | IDs of islands with ≥ 1 sensable tile within vision. Duplicates are removed through a `HashSet<Integer>`, so the order is **HashSet bucket order** (id mod table size), **not sorted**: with a 16-bucket table, IDs ≥ 16 can come before smaller IDs. | RCI:312-326, GW:437-443 | **200** (MC:83) |
| `senseNearbyIslandLocations(idx)`, `(r, idx)`, `(center, r, idx)` | Throws `CANT_SENSE_THAT` if `idx` is not a valid island ID. Returns that island's tiles that pass `canSenseLocation` and lie within the radius of `center`. **Order: island tile order, i.e. ascending `x + y*width` (row-major: y, then x)**, a different order from every other method. May return an empty array with no exception. | RCI:328-358, GW:94-108 | 100 (MC:84) |
| `senseTeamOccupyingIsland(id)` | Throws unless the island exists and ≥ 1 of its tiles is sensable. Returns `Team.NEUTRAL` if unowned. | RCI:364-372, ISL:26 | 20 (MC:77) |
| `senseAnchorPlantedHealth(id)` | Same check. Returns `anchorHealth`, which is **0** when there is no anchor (the javadoc says −1). | RCI:374-381, ISL:28,111 | 20 (MC:78) |
| `senseAnchor(id)` | Same check. Returns `null` if none. | RCI:383-390 | 20 (MC:79) |
| `senseCloud(loc)` | Radius = 4 if **own** tile is a cloud, else vision. **Ignores whether the target is a cloud.** Throws `CANT_DO_THAT` (not CANT_SENSE_THAT) if too far. **No on-map check.** | RCI:392-403 | 5 (MC:89) |
| `senseNearbyCloudLocations()`, `(r)`, `(center, r)` | Cloud tiles within `min(r, vision)` of center **and** within (4 if own tile is a cloud, else vision) of self. **No target-cloud reduction**, so from outside a cloud you see cloud tiles out to full vision. Column-major order. | RCI:405-443 | 100 (MC:90) |
| `senseWell(loc)` | Throws if not sensable. `null` if no well. | RCI:445-451 | 5 (MC:91) |
| `senseNearbyWells()`, `(r)`, `(center, r)`, `(type)`, `(r, type)`, `(center, r, type)` | Wells passing `canSenseLocation`, optionally filtered by current resource type. Column-major order. | RCI:453-502, GW:445-451 | 100 (MC:92) |
| `senseMapInfo(loc)` | Throws if not sensable. Fields: cloud, passable, per-team multiplier, current, per-team boost/destabilize counts and turns left. | RCI:504-531 | 5 (MC:93) |
| `senseNearbyMapInfos()`, `(r)`, `(center)`, `(center, r)` | Every sensable tile in range. Column-major order. **Distant cloud tiles are omitted.** | RCI:533-570 | 100 (MC:94) |
| `adjacentLocation(dir)` | `getLocation().add(dir)`. No checks. | RCI:572-575 | 1 (MC:25) |
| `getAllLocationsWithinRadiusSquared(center, r)` | Accepts −1. Tiles within `min(r, vision)` of center **that pass `canSenseLocation`**. Column-major order. | RCI:577-585 | 100 (MC:46) |

### MapInfo semantics (RCI:504-524, MI:82-163)

- `getCooldownMultiplier(team)` is the full multiplier (cloud, boosts, destabilize and anchor combined) for that team on that tile.
- `getNumDestabilizers(team)` counts destabilizes **affecting** `team`. The engine stores them under the victim's index (GW:355), so
  `getNumDestabilizers(myTeam)` is the number of enemy destabilizes hurting me.
- `get*TurnsLeft(team)` = `lastRound − currentRound` of the **oldest** entry, or −1 if there is none.
  - A fresh boost reads 10 and a fresh destabilize reads 5.
  - It reads 1 in the round at whose end it expires.
- Passing `Team.NEUTRAL` to any per-team getter throws `CANT_DO_THAT` (MI:43-47).

### Query methods (no sensing)

| Method | Returns | Provenance | Bytecode |
|---|---|---|---|
| `getRoundNum()` | Current round | RCI:77 | 1 |
| `getMapWidth()` / `getMapHeight()` | Map dimensions | RCI:82-89 | 1 / 1 |
| `getIslandCount()` | Number of islands | RCI:92 | 20 |
| `getRobotCount()` | Team robots, HQs included | RCI:97, OI:127 | 20 |
| `getID()` / `getTeam()` / `getType()` / `getLocation()` / `getHealth()` | Own unit fields | RCI:105-128 | 1 each |
| `getResourceAmount(r)` | Own inventory amount | RCI:130 | 5 |
| `getAnchor()` | Throws `CANT_DO_THAT` for non-carriers. STANDARD if holding one, else ACCELERATING, else null. | RCI:135-141 | 1 |
| `getNumAnchors(a)` | `null` gives the total | RCI:143-149 | 5 |
| `getWeight()` | Resources + 40 per anchor | RCI:151-156 | 10 |
| `isActionReady()` / `isMovementReady()` | Readiness | RCI:597-622 | 1 |
| `get*CooldownTurns()` | Current cooldown | RCI:606-627 | 1 |

`RobotInfo` exposes the **enemy's inventory**: `getResourceAmount`, `getNumAnchors` and `getTotalAnchors`
(common/RobotInfo.java:94-116). These are not in MC, so they cost nothing beyond the invoke.

### Bytecode rules

- A method listed in MC costs its fixed amount on top of the normal instruction count. Every overload shares the per-name cost
  (MethodCostUtil.java:84-110, IMV:454-458).
- Every `RobotController` method appears in MC. Four MC entries are stale and have no matching method: `isTransformReady`,
  `senseCooldownMultiplier`, `senseDestabilizeTurns` and `senseBoostTurns`.
- **Every exception handler a player's code enters costs 500 bytecodes** (IMV:623-627, GC:69).
  - `can*` methods catch internally inside uninstrumented engine code, so they carry no penalty.
  - Calling an action and catching `GameActionException` costs 500 on failure.

---

## Spec disagreements

The engine wins in each case.

1. **Destabilizer movement cooldown.** SPEC table "Cooldown / move" lists Destabilizer 20. The engine has **25** (RT:49; jar `<clinit>` `bipush 25`).
2. **`transferAnchor()` does not exist.** SPEC "Actions and Cooldowns" › Transferring names it. The real methods are `takeAnchor`,
   `returnAnchor` and `placeAnchor` (RC interface via javap).
3. **Carrier throw amount.**
   - SPEC: "When throwing m kg of resource, the damage dealt is ⌊5m/4⌋. The thrown resources fall into the void."
   - Engine: m is the **total weight, anchors included** (40 each). The carrier **always throws everything** and cannot choose m.
     Anchors are destroyed too. Resources are lost even when the target is empty, friendly or a HQ (IC:35-73).
4. **Destabilizer stacking.**
   - SPEC: "can stack up to 2 times (a max of 2 total destabilizers can impact a square)."
   - Engine: only the **multiplier** is capped at 2. Every destabilize entry still deals 50 damage when it expires (GW:672-688).
5. **Cloud sensing exceptions.**
   - SPEC: "Clouds obscure squares from the default vision radius… obscured vision of 4 units."
   - Engine: this holds for every sense method that uses `canSenseLocation`. However `senseCloud` and `senseNearbyCloudLocations`
     shrink the radius only when the **sensing robot** is in a cloud. From outside, you can find cloud tiles out to full vision
     (RCI:392-443).
6. **When cooldowns decrement.**
   - SPEC: "After every turn, the movement and action cooldowns of all robots are decremented by 10."
   - Engine: at the **start** of each robot's own turn, floored at 0 (IR:425-429). New robots start at 10, so they are 0 on their first turn.
7. **readSharedArray cost.** SPEC: "for standard Java bytecode costs". Engine: a fixed **2** (MC:74).
8. **senseAnchorPlantedHealth with no anchor.** RC javadoc: "-1 if there is no anchor". Engine returns **0** (RCI:374-381, ISL:28, ISL:111).
9. **collectResource(-1).** RC javadoc: "-1 to collect max possible". Engine: −1 means exactly the well rate, and it **fails** if that
   does not fit (RCI:942-949).
10. **transferResource capacity.** RC javadoc: "Transferred material is limited by carrier capacity". Engine: no clamping; it throws
    if `-amount` does not fit (RCI:881-884).
11. **canBuildRobot conditions.** The RC javadoc omits the passability check and the requirement that the spawn tile be **sensable**
    (cloud rule) (RCI:689-696).
12. **senseNearby\* order.** RC javadoc: "returned in no particular order". Engine: deterministic column-major (x, then y) order.
    `senseNearbyIslandLocations` uses row-major order and `senseNearbyIslands` uses HashSet order (GW:462-479, GW:94-108, RCI:315-325).
13. **Version.** The spec header and `GameConstants.SPEC_VERSION` say 3.0.14, while the jar is 3.0.15. The rules are identical as far
    as this area goes (the bytecode diff above).
14. **Depositing into HQs.**
    - SPEC: "carriers can deposit and receive resources… [at] headquarters".
    - Engine: deposits (positive amount) are allowed into **either team's** HQ (RCI:874-897). Only withdrawals require your own team.
15. **Reanchoring with a different type.**
    - SPEC: "Teams can place an anchor on top of an island they already control… The same anchor type does not need to be used."
    - Engine: replacing ACCELERATING with STANDARD leaves the −15 % accelerating multiplier in place **permanently**, even after the
      island is later lost. `removeBoostFromAnchor` only runs if the anchor at the time of loss is ACCELERATING (ISL:79-83, ISL:104-108).

---

## Surprises: mechanics a bot designer could easily get wrong

1. **The HQ can build 5 units, or anchors, per turn.** Its action cooldown is 2, not 10 (RT:21), and resources are the only other limit.
2. **New robots do not act in the round they are built** (OI:95-110). They act on their first turn with cooldown 0.
3. **The spawn tile must be sensable.** In or next to clouds, the HQ can only spawn within dist² 4 (RCI:689-696, IR:271-277).
4. **Resources are per HQ.** `buildRobot` and `buildAnchor` spend only the calling HQ's own stock (RCI:684, RCI:715).
   - Carriers can withdraw from one HQ (`transferResource(hq, r, -n)`) to move stock between HQs (RCI:881-894).
5. **Depositing next to an enemy HQ gifts it resources.** Check the team before calling `transferResource` with a positive amount (RCI:874-897).
6. **Carrier throw = lose everything.** Even a miss, or a "throw" at an empty tile, wipes the whole inventory, including an anchor.
   - Maximum damage is 50 (weight 40).
   - A carrier with one unit of resource can still "attack": ⌊1.25⌋ = 1 damage.
7. **`collectResource(loc, -1)` fails near capacity.** At an upgraded well (rate 3) with weight 38 or 39, pass the remaining capacity
   explicitly. `collectResource(loc, 0)` "succeeds" and wastes the action.
8. **A carrier can collect from the well tile it stands on** (adjacency includes distance 0, ML:129-133).
   - Any number of carriers can share a well. Wells never deplete.
9. **Multiple actions or moves in one turn happen whenever a cooldown increment is ≤ 9:**
   - carrier moves at weight ≤ 13;
   - boosted carrier actions (round(10·0.9) = 9);
   - boosted launcher attacks.

   Always loop on `isActionReady()` / `isMovementReady()` instead of assuming one action per turn.
10. **Movement cooldown uses the multiplier of the tile you move *into*.**
    - Stepping into a cloud costs 1.2×; stepping out costs 1×.
    - Carrier movement cooldown uses the weight at the moment of moving, so collect *after* moving to save movement cooldown.
11. **Action cooldown multipliers are evaluated at the time of the action:**
    - The booster's own cooldown includes the boost it just cast (140 → 126).
    - `placeAnchor` with an ACCELERATING anchor computes the carrier's cooldown with the new −0.15 already applied.
12. **Launcher and destabilizer targets need no vision.** You can attack or destabilize clouded tiles you cannot see.
    - Attacking empty tiles, allies or HQs is legal and silent (no damage).
    - **HQs cannot be damaged at all** (IR:373-375).
13. **Destabilize damage lands at the end of round cast+4.** It hits whoever stands on each tile at that moment, once per stacked
    entry, so 3 casts deal 150. A unit that steps out of the r² 15 area before expiry takes nothing.
14. **Booster has no target.** It boosts r² 20 around its own position. The boost stays where it was cast and lasts through round cast+9.
15. **Sensing in clouds:**
    - A robot on a cloud tile sees everything only within r² 4.
    - Robots standing in clouds are invisible beyond r² 4.
    - `senseNearbyMapInfos` silently drops distant cloud tiles.
    - Use `senseNearbyCloudLocations()` to map clouds at full range.
    - `senseCloud` has no on-map check and throws `CANT_DO_THAT`.
16. **Result orders:**
    - `senseNearbyRobots`, wells, map infos, clouds and `getAllLocationsWithinRadiusSquared` are column-major (x, then y), not nearest-first.
    - `senseNearbyIslands()` is HashSet order.
    - `senseNearbyIslandLocations` is row-major (y, then x).
17. **`senseNearbyIslandLocations(idx)` throws for an invalid ID but returns an empty array for a valid, unseen island.**
    `senseTeamOccupyingIsland`, `senseAnchor` and `senseAnchorPlantedHealth` throw unless at least one tile of the island is sensable.
18. **Unowned islands:** `senseTeamOccupyingIsland` returns `Team.NEUTRAL` and `senseAnchorPlantedHealth` returns 0, not −1.
19. **`takeAnchor` needs a completely empty carrier.** Drop all resources first (IR:165-167).
20. **Shared array:**
    - Writes are visible immediately to robots that act later in the same round.
    - HQs and amplifiers can always write.
    - Others need an own amplifier within r² 20, an own HQ within r² 9, or an own-owned island tile within r² 4.
    - Writes cost 75 bytecodes each. Reads cost 2.
21. **`disintegrate()` cannot be caught** by `catch (Exception)`, because it is a VirtualMachineError.
    Disintegrating a HQ throws away its whole stockpile (GW:828-830).
22. **`setIndicatorString(null)` throws a NullPointerException**, and so does any other null argument to an action.
    Indicators reset every round.
23. **Each caught exception costs 500 bytecodes.** Prefer `canX()` (5–10 bytecodes) to try/catch around `X()`.
24. **Placing a STANDARD anchor on your own ACCELERATING island** leaves a permanent −15 % own-team cooldown aura there.
    This is an engine quirk (ISL:75-88, ISL:104-108, GW:374-400). Placing on your own island never increments the "anchors placed"
    tiebreak counter.
25. **Wells are cumulative and permanent:**
    - Converting a well to elixir keeps its upgraded flag.
    - Throwing AD or MN into an elixir well wastes it.
    - Thrown resources leave the team totals, which affects the tiebreaks (WELL:38-64).

## Not verified in code (UNVERIFIED)

- I did not run any match. All behaviour here comes from reading the source, plus bytecode identity with the jar.
- I did not check how the client or replay renders the actions.
- I did not check whether map generation guarantees that wells or HQs are never on clouds. That affects how often the spawn-tile
  cloud rule matters, and it belongs to the map area.
