# Battlecode 2023 (Tempest): constants, robot types, resources, anchors, wells, cooldowns

Area: **constants-types**. The engine is the source of truth. Release in use: `battlecode23-3.0.15.jar`.

## Provenance conventions

- `ENG/` = `/home/terryvanbelle/projects/vibe/reference/battlecode23/engine/src/main/battlecode/`. The reference repo is at `af42086`, and git tag `3.0.15` points at the same commit (`git tag` → `3.0.15`; `git log 3.0.15..HEAD` is empty).
- `JAR` = `/home/terryvanbelle/projects/vibe/2023/engine/battlecode23-3.0.15.jar`, disassembled with `~/jdk/jdk8u504-b01/bin/javap -c -p -l -constants`.
- `SPEC:n` = line n of `/home/terryvanbelle/projects/vibe/reference/battlecode23/specs/specs.md.html` (spec version 3.0.14).
- **Source and jar agree everywhere I checked.** I compared these in the jar, by opcodes, constants and `LineNumberTable`, against the cited source lines:
  - All `GameConstants` values (`javap -constants`).
  - The `RobotType`, `Anchor` and `ResourceType` enum static initializers (`static {}`).
  - `InternalCarrier.emptyResources/getDamage/attack`.
  - `InternalRobot.<init>/addActionCooldownTurns/getBaseMovementCooldown/addMovementCooldownTurns/addHealth/processBeginningOfTurn/processEndOfRound`.
  - `Well.addAdamantium/addMana/addElixir/getRate`.
  - `Island.placeAnchor/advanceTurn`.
  - `GameWorld.addBoost/addDestabilize/addBoostFromAnchor/removeBoostFromAnchor/getCooldownWithMultiplier/processEndOfRound/inRangeForAmplification`.
  - `RobotControllerImpl.boost/destabilize/move/buildRobot/transferResource/collectResource/attack/assertCanTransferResource/assertCanCollectResource`.
- "Derived" means the claim follows arithmetically from verified code. I computed it with the engine's own expressions: a JDK 8 `strictfp` program that copies `GameWorld`'s multiplier arithmetic, in the scratchpad `cd/CD.java`. I did not check it by running a game.
- Anything not verified in code is marked **UNVERIFIED**.

---

## 1. GameConstants (all 52 fields, values from `javap -constants` on the JAR)

Each value is identical in `ENG/common/GameConstants.java` (line given) and in the JAR. "Used in" lists where the engine reads the constant (from a grep over `ENG/`).

| Constant | Value | Src line | Used in / meaning |
|---|---|---|---|
| SPEC_VERSION | "3.0.14" | 13 | replay header (`server/GameMaker.java:242`). The jar's own version is 3.0.15. |
| MAP_MIN_HEIGHT / MAP_MAX_HEIGHT | 20 / 60 | 20, 23 | map validation (`server/Server.java:246-257`) |
| MAP_MIN_WIDTH / MAP_MAX_WIDTH | 20 / 60 | 26, 29 | same |
| MIN_STARTING_HEADQUARTERS | 1 | 32 | validation compares the total HQ count with `1*2` (`Server.java:273`) |
| MAX_STARTING_HEADQUARTERS | 4 | 35 | validation compares the total HQ count with `4*8` = 32, not 8 (`Server.java:276`; engine bug) |
| MIN_NUMBER_ISLANDS / MAX_NUMBER_ISLANDS | 4 / 35 | 38, 41 | `Server.java:323-328` |
| MAX_ISLAND_AREA | 20 | 44 | `Server.java:333` |
| MAX_DISTANCE_BETWEEN_WELLS | 100 (r²) | 47 | every Ad well has an Mn well within r² 100, and vice versa (`Server.java:387-411`) |
| MIN_NEAREST_AD_DISTANCE | 100 (r²) | 50 | every HQ has an Ad well within r² 100 (`Server.java:345-365`). The name says "min", but it is used as a maximum distance. |
| MAX_MAP_PERCENT_WELLS | 0.04f | 53 | at most `(int)(W*H*0.04)` wells of each initial type (`Server.java:413-419`) |
| INDICATOR_STRING_MAX_LENGTH | 64 | 60 | truncation (`RobotControllerImpl.java:1181`) |
| SHARED_ARRAY_LENGTH | 64 | 63 | `TeamInfo.java:40`, `RobotControllerImpl.java:1114` |
| MAX_SHARED_ARRAY_VALUE | 65535 | 66 | `RobotControllerImpl.java:1119` |
| EXCEPTION_BYTECODE_PENALTY | 500 | 69 | `instrumenter/bytecode/InstrumentingMethodVisitor.java:626` |
| INITIAL_MN_AMOUNT | 200 | 72 | given to **each HQ** at the start of round 1 (`world/GameWorld.java:169-183`) |
| INITIAL_AD_AMOUNT | 200 | 75 | same |
| PASSIVE_AD_INCREASE | 6 | 78 | **per HQ**, every 5 rounds (`world/InternalRobot.java:444-448`). The javadoc's "per turn" is wrong. |
| PASSIVE_MN_INCREASE | 6 | 81 | same |
| PASSIVE_INCREASE_ROUNDS | 5 | 84 | `InternalRobot.java:444` |
| UPGRADE_TO_ELIXIR | 600 | 87 | `world/Well.java:40,50` |
| UPGRADE_WELL_AMOUNT | 1400 | 90 | `Well.java:43,53,61` |
| WIN_PERCENTAGE_OF_ISLANDS_OCCUPIED | 0.75f | 93 | `world/TeamInfo.java:177,191` |
| DISTANCE_SQUARED_FROM_SIGNAL_AMPLIFIER | 20 | 96 | shared-array write range (`GameWorld.java:869-875`) |
| DISTANCE_SQUARED_FROM_ISLAND | 4 | 99 | write range, **and** island healing / accelerating-anchor area (`world/Island.java:133`) |
| DISTANCE_SQUARED_FROM_HEADQUARTER | 9 | 102 | write range (`GameWorld.java:869-877`) |
| CARRIER_DAMAGE_FACTOR | 1.25f | 105 | `world/robots/InternalCarrier.java:49` |
| CARRIER_MOVEMENT_SLOPE | 0.375f | 108 | `InternalRobot.java:334` |
| CARRIER_MOVEMENT_INTERCEPT | 5 | 111 | `InternalRobot.java:334` |
| COOLDOWN_LIMIT | 10 | 118 | a robot can act or move iff its cooldown is **< 10** (`InternalRobot.java:223-232`). Also the starting cooldowns of a new robot (`InternalRobot.java:74-75`). |
| COOLDOWNS_PER_TURN | 10 | 121 | subtracted at the **start of the robot's own turn**, floored at 0 (`InternalRobot.java:425-429`) |
| CURRENT_STRENGTH | 1 | 128 | currents apply every round (`GameWorld.java:708`) |
| CARRIER_CAPACITY | 40 | 131 | carrier inventory cap (`InternalRobot.java:60-61`) |
| ANCHOR_WEIGHT | 40 | 134 | `Inventory.java:135`, `InternalRobot.java:166`, `RobotControllerImpl.java:155` |
| CLOUD_VISION_RADIUS_SQUARED | 4 | 137 | `InternalRobot.java:273-276`, `RobotControllerImpl.java:396-397,428-429` |
| BOOSTER_MULTIPLIER | -0.1d | 140 | `GameWorld.java:334,666` |
| DESTABILIZER_MULTIPLIER | 0.1d | 141 | `GameWorld.java:357,683` |
| ANCHOR_MULTIPLIER | -0.15d | 142 | `GameWorld.java:382,395` |
| CLOUD_MULTIPLIER | 0.2d | 143 | `GameWorld.java:136-143` |
| BOOSTER_RADIUS_SQUARED | 20 | 146 | `GameWorld.java:329` |
| DESTABILIZER_RADIUS_SQUARED | 15 | 147 | `GameWorld.java:353` |
| BOOSTER_DURATION | 10 | 150 | `GameWorld.java:328` |
| DESTABILIZER_DURATION | 5 | 151 | `GameWorld.java:352` |
| MAX_BOOST_STACKS | 3 | 154 | `GameWorld.java:333,665` |
| MAX_DESTABILIZE_STACKS | 2 | 155 | `GameWorld.java:356,682` |
| MAX_ANCHOR_STACKS | 1 | 156 | `GameWorld.java:381,394` |
| WELL_STANDARD_RATE | 1 | 159 | `Well.java:91`, `common/WellInfo.java:75` |
| WELL_ACCELERATED_RATE | 3 | 160 | same |
| GAME_DEFAULT_SEED | 6370 | 167 | **not used anywhere** in `ENG/` |
| GAME_MAX_NUMBER_OF_ROUNDS | 2000 | 170 | `world/GameMapIO.java:228`, `world/MapBuilder.java:205` |

Bot code compiled against these `static final` primitives gets the values inlined by javac.

---

## 2. RobotType

Constructor argument order: BCA, BCM, BCE, actionCooldown, movementCooldown, health, damage, actionRadiusSquared, visionRadiusSquared, bytecodeLimit (`ENG/common/RobotType.java:198-210`). Values are from `RobotType.java:21-66`. They are identical in the JAR's `static {}` (e.g. DESTABILIZER: `sipush 200, bipush 70, bipush 25, sipush 300, bipush 50, bipush 13, bipush 20, sipush 10000`).

| Type | Ad | Mn | Ex | Action CD | Move CD | HP | Damage | Action r² | Vision r² | Bytecodes |
|---|---|---|---|---|---|---|---|---|---|---|
| HEADQUARTERS | 0 | 0 | 0 | **2** | -1 | 1 (unkillable) | 4 (passive, end of round) | 9 | 34 | 20000 |
| CARRIER | **50** | 0 | 0 | 10 | 0 in the table; real value `floor(0.375*w)+5` | 150 | 0 in the table; real value `floor(1.25*w)` | 9 | 20 | 12500 |
| LAUNCHER | 0 | **45** | 0 | 10 | 20 | 200 | 20 | 16 | 20 | 10000 |
| DESTABILIZER | 0 | 0 | **200** | 70 | **25** | 300 | 50 (at expiry) | 13 | 20 | 10000 |
| BOOSTER | 0 | 0 | **150** | 140 | 25 | 400 | 0 | -1 (boost is centred on self) | 20 | 10000 |
| AMPLIFIER | **30** | **15** | 0 | -1 (has no action) | 15 | 120 | 0 | -1 | 34 | 10000 |

More facts about types:

- `canAttack()` is true only for CARRIER and LAUNCHER (`RobotType.java:129-132`). Destabilizers use `destabilize()`. The HQ's damage is passive.
- Only CARRIER can extract or place anchors (`RobotType.java:140-152`). Only HQ can build robots and anchors (`RobotControllerImpl.java:675-680,724-726`). A HQ cannot be built (`RobotControllerImpl.java:678-679`).
- **HQs cannot be damaged.** `addHealth` returns immediately for HEADQUARTERS (`InternalRobot.java:373-375`). Launcher and carrier attacks on a HQ do nothing (`InternalRobot.java:406`, `InternalCarrier.java:64`). HQs cannot move (`RobotControllerImpl.java:637-638`).
- Health is capped at the type maximum, and a robot is destroyed as soon as health ≤ 0 (`InternalRobot.java:376-381`).
- Inventory capacity: HQ has no cap (`Inventory()` with maxCapacity -1). Carrier holds 40. Every other type has capacity 0 (`InternalRobot.java:55-66`).
- New robots start with action and movement cooldown = 10. At the start of their first turn both drop to 0 (`InternalRobot.java:74-75,425-427`).
- The bytecode limit is reset to `type.bytecodeLimit` at the start of every turn (`InternalRobot.java:428`).
- Spawning: `buildRobot` needs the target within the HQ's action r² 9 (`assertCanActLocation`), the target **sensable** (`isLocationOccupied` → `assertCanSenseLocation`, so clouds cut this to r² 4), unoccupied and passable, and the **building HQ's own** stock to cover every cost (`RobotControllerImpl.java:670-697`). It adds the HQ's action cooldown and deducts costs from that HQ (`RobotControllerImpl.java:708-719`).
- The replay header writes these raw RobotType fields, including CARRIER movementCooldown 0 and damage 0 (`server/GameMaker.java:282-302`).
- Number of squares in each radius (derived, lattice count): r²2 = 9, r²4 = 13, r²9 = 29, r²13 = 45, **r²15 = 45** (no lattice point has d² = 14 or 15), r²16 = 49, r²20 = 69, r²34 = 109.
- Hits to kill (derived):
  - Launcher (20 damage): carrier 8, launcher 10, destabilizer 15, booster 20, amplifier 6.
  - 50-damage hit (full carrier throw or one destabilize expiry): carrier 3, launcher 4, amplifier 3, destabilizer 6, booster 8.
  - HQ aura (4 per round): a launcher sitting in range dies in 50 rounds.

---

## 3. ResourceType

- `NO_RESOURCE(0)`, `ADAMANTIUM(1)`, `MANA(2)`, `ELIXIR(3)`. The field is `resourceID` (`ENG/common/ResourceType.java:4-7`; JAR `static {}` same).
- The map file's resource array indexes `ResourceType.values()`. Initial maps may contain only Ad and Mn wells (`GameWorld.java:114-122`; `Server.java:373-384` throws on anything else).

---

## 4. Anchor

Constructor order: totalHealth, unitsAffected, accelerationFactor, healingFrequency, healingAmount, **manaCost, adamantiumCost**, elixirCost (`ENG/common/Anchor.java:80-89`). Values are from `Anchor.java:16,21`. JAR `static {}`: STANDARD `250,0,0.0f,1,4,80,80,0`; ACCELERATING `750,4,-0.15f,1,6,0,0,300`.

| Anchor | Cost | Max / initial health | Heal per round | Cooldown effect |
|---|---|---|---|---|
| STANDARD | 80 Ad + 80 Mn | 250 | +4 | none |
| ACCELERATING | 300 Ex | 750 | +6 | −0.15 on the owner's multiplier, 1 stack max |

- `unitsAffected` (0/4) and `accelerationFactor` (0.0/−0.15) are **never read by the engine**. The real values come from `GameConstants.DISTANCE_SQUARED_FROM_ISLAND` (4) and `ANCHOR_MULTIPLIER` (−0.15) (`Island.java:133`, `GameWorld.java:374-400`). `healingFrequency` = 1 is read (`Island.java:116`), so healing happens every round.
- Anchor weight is 40 = carrier capacity. `takeAnchor` needs `canAdd(40)`, so the carrier must be **completely empty** (`InternalRobot.java:165-167`, `RobotControllerImpl.java:1040-1043`).
- Building an anchor: HQ only. It costs the HQ's action cooldown (2) and is paid from that HQ's stock (`RobotControllerImpl.java:721-757`). The anchor goes into the HQ's inventory. A carrier takes it with `takeAnchor(hqLoc, type)`: adjacent, same team, HQ has one, carrier empty (`RobotControllerImpl.java:1014-1062`). `returnAnchor` gives it back (`RobotControllerImpl.java:1064-1107`). There is **no** `transferAnchor`.
- `placeAnchor()`: the carrier must **stand on** an island square and hold an anchor. If it somehow held both types, STANDARD is placed first (`InternalRobot.java:155-163`). The island must be neutral or already owned by the carrier's team (`RobotControllerImpl.java:975-1012`, `Island.java:60-66`).

---

## 5. Wells

- Wells are infinite. Collecting never depletes a well (`RobotControllerImpl.java:961-973` only adds to the carrier).
- A well's **type and upgrade state change only when carriers transfer resources into it.** Each well keeps a cumulative inventory per resource, which only grows (`Well.java:10,38-64`; `Inventory.addX` only adds).

| Well currently | Resource thrown in | Condition (cumulative in the well) | Effect |
|---|---|---|---|
| ADAMANTIUM | Mana | Mn ≥ 600 | becomes **ELIXIR** (`Well.java:50-52`) |
| MANA | Adamantium | Ad ≥ 600 | becomes **ELIXIR** (`Well.java:40-42`) |
| ADAMANTIUM | Adamantium | Ad ≥ 1400 | upgraded, rate 1 → 3 (`Well.java:43-45`) |
| MANA | Mana | Mn ≥ 1400 | upgraded (`Well.java:53-55`) |
| ELIXIR | Elixir | Ex ≥ 1400 | upgraded (`Well.java:61-63`) |
| any | anything else | — | stored, no effect |

- **The upgrade flag is never cleared.** An Ad or Mn well upgraded first and then converted becomes an **upgraded elixir well** (rate 3) at once (`Well.java:16,43-45,50-52`: the type changes, `isUpgraded` stays true). Elixir wells cannot convert further.
- Conversion and upgrade checks run only inside `addAdamantium` / `addMana` / `addElixir`, at transfer time (`Well.java:66-80`).
- Rate: `isUpgraded ? 3 : 1` (`Well.java:90-92`, JAR `iconst_3 / iconst_1`). This is per **collect action**, per carrier. There is no per-well or per-round cap: any number of carriers can collect, from the 8 neighbours or the well square itself.
- `collectResource(loc, amount)` (`RobotControllerImpl.java:925-973`):
  - Carrier only, action-ready.
  - `loc` must be within action r² 9 **and** `isAdjacentTo`. Adjacency includes the carrier's own square (`common/MapLocation.java:129-133`).
  - `amount == -1` means "the rate". `amount < -1` throws. `0 ≤ amount ≤ rate` is allowed, so `amount = 0` is legal and wastes a cooldown.
  - It throws if `weight + amount > 40`. **`-1` on an upgraded well fails once fewer than 3 kg of space remain**, so pass an explicit `min(rate, 40-weight)`.
  - The resource type is read from the well when you collect, so a converted well yields elixir.
- `transferResource(loc, type, amount)` (`RobotControllerImpl.java:862-923`):
  - Carrier only, action-ready, `loc` adjacent (or own square) and within r² 9, `amount != 0`.
  - `amount > 0` deposits into a **well or a HQ of either team**. There is **no team check on deposit** (`RobotControllerImpl.java:874-897`).
  - `amount < 0` withdraws, and only from an **own-team HQ** with enough stock and capacity (`RobotControllerImpl.java:881-894`).
  - Resources given to a well leave the team's totals (`InternalRobot.addResourceAmount` → `TeamInfo.addResource` with a negative amount; the well's inventory is not team-owned).
- Cost of the economy (derived): a carrier collects 1 kg per collect, which is 1 kg/turn with action cooldown 10. Filling 40 kg takes 40 turns at a standard well and 14 collects at an upgraded one (13×3 + 1). Upgrading a well takes 1400 kg of its own resource. Converting takes 600 kg of the opposite one.
- Map guarantees: listed in §1 (MIN_NEAREST_AD_DISTANCE, MAX_DISTANCE_BETWEEN_WELLS, MAX_MAP_PERCENT_WELLS). Wells are never on walls, HQs or currents (`Server.java:285-304`).

---

## 6. Carriers: weight, movement cooldown, throw attack

- `weight = Ad + Mn + Ex + 40 × (number of anchors held)` (`Inventory.java:134-137`; same formula in `RobotControllerImpl.getWeight`, `RobotControllerImpl.java:151-156`).
- **Base movement cooldown = `(int)Math.floor(0.375f * weight) + 5`** (`InternalRobot.java:332-339`; JAR `ldc 0.375f, i2f, fmul, f2d, Math.floor, d2i, iconst_5, iadd`). The weight is the carrier's weight **at the moment of the move** (before it moves). Then the multiplier is applied (§8).

  | weight | 0-2 | 3-5 | 6-7 | 8-10 | 11-13 | 14-15 | 16-18 | 19-21 | 22-23 | 24-26 | 27-29 | 30-31 | 32-34 | 35-37 | 38-39 | 40 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | move CD | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |

  (derived, computed with the engine's float expression). An empty carrier moves **twice per turn**: 0 → 5 → 10. A carrier with weight ≤ 13 still gets a second move whenever its cooldown starts the turn below 10 − cd. A full carrier, or one holding an anchor, moves once every 2 turns (CD 20).
- `RobotType.CARRIER.movementCooldown` is **0** and is not used for carriers (`InternalRobot.java:333-337`).
- Throw attack (`attack(loc)` from a carrier):
  - Requirements: target within r² 9 (not necessarily sensable), action-ready, **weight > 0**. Weight can be resources or a held anchor (`RobotControllerImpl.java:763-776`).
  - Damage = `(int)Math.floor(1.25f * weight)` (`InternalCarrier.java:47-50`; JAR `ldc 1.25f … Math.floor`). So 40 kg → 50, 39 → 48, 20 → 25, 8 → 10, 1 → 1, 4 → 5. An anchor alone gives 50.
  - Damage is dealt only if the target square holds an **enemy non-HQ** robot (`InternalCarrier.java:62-71`).
  - **The whole inventory is destroyed in every case**: hit, miss, empty square, friendly target or HQ target. That includes every resource **and any held anchors** (`InternalCarrier.java:35-45,72`). The team totals drop by the thrown amounts (`InternalCarrier.java:39`).
  - Cooldown: the carrier's action cooldown 10 × the multiplier at its square (`RobotControllerImpl.java:786-791`).
- `RobotType.CARRIER.damage` is **0** in the enum. The real damage comes only from `InternalCarrier.getDamage`.
- Carriers are built as `InternalCarrier` (`GameWorld.java:788-797`). Every other type is a plain `InternalRobot`. Its `attack` uses `type.damage`, so a LAUNCHER does 20 (`InternalRobot.java:390-414`).

---

## 7. Headquarters: stockpiles, starting resources, passive income, aura

- **Stockpiles are per HQ, not per team.** Every HQ has its own unbounded `Inventory` (`InternalRobot.java:56-58`). `rc.getResourceAmount` returns that HQ's own stock (`RobotControllerImpl.java:130-133` → `InternalRobot.getResource`). `buildRobot` and `buildAnchor` check and charge only the calling HQ (`RobotControllerImpl.java:681-688,712-716,727-734,750-754`). Moving stock between HQs needs carriers (withdraw with a negative transfer, then deposit).
- **Starting resources: 200 Ad + 200 Mn in each HQ.** They are added at the start of round 1, before any turn (`GameWorld.java:169-183`). A team with k HQs starts with 200k of each, split across its HQs.
- **Passive income: +6 Ad and +6 Mn to each HQ** at the end of every round where `round % 5 == 0`, i.e. rounds 5, 10, …, 2000 (`InternalRobot.java:439-448`; JAR `iconst_5 irem … bipush 6`). That is 1.2 Ad and 1.2 Mn per round per HQ, and 2400 of each per HQ over a 2000-round game (derived).
- **HQ aura:** at the end of every round, every enemy robot within r² 9 of each HQ loses 4 HP. This runs before the income step in the same loop (`InternalRobot.java:440-443`). Several HQs stack.
- HQ build rate: action cooldown 2 at multiplier 1.0. Starting a turn at 0, the HQ can act at 0, 2, 4, 6, 8, so **5 builds/anchors per turn**. With multiplier ≤ 0.70 the cooldown rounds to 1, giving 10 per turn. With ≥ 1.25 it rounds to 3, giving 4, 3, 3 builds and then repeating, an average of 10/3 per turn (derived from §8). Turn-1 budget per HQ (derived): 200 Ad covers 4 carriers, 200 Mn covers 4 launchers, and at most 5 units fit in the turn.
- Team totals (`TeamInfo` Ad/Mn/Ex) add up every robot's inventory: HQs and carriers. They change on every `addResourceAmount` (`InternalRobot.java:141-145`, `TeamInfo.java:148-164`). When a robot dies its inventory is removed from the totals (`GameWorld.java:828-830`). These totals are what the tiebreak uses (`GameWorld.java:566-621`).
- A sensed enemy robot's inventory is readable: `RobotInfo.getResourceAmount/getNumAnchors/getTotalAnchors` (`common/RobotInfo.java:94-113`, built from `inventory.copy()` at `InternalRobot.java:212`). Sensing an enemy HQ shows its stockpile and stored anchors. Sensing an enemy carrier shows its load and whether it carries an anchor.

---

## 8. Cooldowns and the cooldown multiplier

### 8.1 Basics
- A robot can act iff `actionCooldownTurns < 10`, and move iff `movementCooldownTurns < 10` (`InternalRobot.java:223-232`).
- At the start of each of the robot's own turns both cooldowns become `max(0, cd − 10)` (`InternalRobot.java:425-427`). There is no banking below 0.
- Each action adds `round(base × multiplier)` to the action cooldown (`InternalRobot.java:327-330`). Each move adds `round(baseMove × multiplier)` to the movement cooldown (`InternalRobot.java:344-347`).
- Long-run rate (derived): a cooldown of c gives 10/c actions per turn. For c < 10 a robot can act more than once in a turn: c = 9 gives 2 actions on some turns, c = 5 gives 2 every turn, c = 2 gives 5. For c > 10 it acts on fewer than every turn: c = 12 gives 5 actions per 6 turns.
- **The action multiplier is read at the robot's current square.** **The move multiplier is read at the destination square**: `move()` calls `setLocation(next)` and then `addMovementCooldownTurns()`, which reads `this.location` (`RobotControllerImpl.java:659-664`, `InternalRobot.java:344-346`).
- `boost()` calls `addBoost` **before** adding its own cooldown, so a booster's cooldown already includes its own new boost: 140 × 0.9 = **126** (`RobotControllerImpl.java:813-819`). `destabilize()` changes only the opponent's multiplier, so it doesn't affect its own cooldown (`RobotControllerImpl.java:843-848`).

### 8.2 Multiplier: per square, per team, additive, rounded
- `cooldownMultipliers[square][team]` (a double) starts at 1.0 (`GameWorld.java:131-135`).
- Cloud: +0.2 for **both** teams, set once at construction (`GameWorld.java:136-143`).
- Boost: −0.1 for the booster's **own** team on every square within r² 20 of the **booster's location**. A new entry changes the multiplier only while fewer than 3 boosts are active on that square for that team, so the stack is capped at 3 (`GameWorld.java:327-339`).
- Destabilize: +0.1 to the **opponent's** multiplier on every square within r² 15 of the target. The target must be within the destabilizer's action r² 13. Capped at 2 stacks (`GameWorld.java:351-362`; `RobotControllerImpl.java:825-848`).
- Accelerating anchor: −0.15 for the owner on every square within r² 4 of any island square. Capped at 1 stack (`GameWorld.java:374-387`, `Island.java:129-137`).
- **Every add and remove is followed by `Math.round(m*100)/100.0`**, i.e. the value is rounded to 2 decimals (`GameWorld.java:140-141,335,358,383,396,667,684`; JAR `ldc2_w 100.0d … Math.round(D)J … l2d … ddiv`). So the multiplier is always the double nearest to `1 + 0.2·cloud − 0.1·min(boosts,3) + 0.1·min(destabs,2) − 0.15·min(anchors,1)`. I checked that the order of updates never changes the result (derived; all permutations tested).
- The final cooldown is `(int)Math.round(base * m)`. `Math.round` rounds half up, so x.5 goes up (`GameWorld.java:498-500`; JAR `i2d … dmul … Math.round(D)J … l2i`).
- Range of m: **0.55** (3 boosts + accelerating anchor, no cloud) to **1.40** (cloud + 2 destabilizes).
- `rc.senseMapInfo(loc).getCooldownMultiplier(team)` returns this exact double. It also gives active boost/destabilize counts and "turns left" (`RobotControllerImpl.java:504-524`).

### 8.3 Exact cooldown after the multiplier (derived with the engine's arithmetic)

Columns are base cooldowns. Rows are every reachable multiplier, with an example source.

| m | example source | 2 (HQ) | 5 | 10 (carrier/launcher action) | 15 (amp move) | 20 (launcher move, full carrier) | 25 (destab/booster move) | 70 (destab action) | 140 (booster action) |
|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 3 boosts + accel anchor | 1 | 3 | 6 | 8 | 11 | 14 | 39 | 77 |
| 0.65 | 2 boosts + anchor | 1 | 3 | 7 | 10 | 13 | 16 | 46 | 91 |
| 0.70 | 3 boosts | 1 | 4 | 7 | 11 | 14 | 18 | 49 | 98 |
| 0.75 | 1 boost + anchor; cloud + 3 boosts + anchor | 2 | 4 | 8 | 11 | 15 | 19 | 53 | 105 |
| 0.80 | 2 boosts | 2 | 4 | 8 | 12 | 16 | 20 | 56 | 112 |
| 0.85 | accel anchor | 2 | 4 | **9** | 13 | 17 | 21 | 60 | 119 |
| 0.90 | 1 boost | 2 | 5 | **9** | 14 | 18 | 23 | 63 | 126 |
| 0.95 | anchor + destab; cloud + boost + anchor | 2 | 5 | 10 | 14 | 19 | 24 | 67 | 133 |
| 1.00 | nothing | 2 | 5 | 10 | 15 | 20 | 25 | 70 | 140 |
| 1.05 | cloud + anchor; 2 destabs + anchor | 2 | 5 | 11 | 16 | 21 | 26 | 74 | 147 |
| 1.10 | 1 destab; cloud + 1 boost | 2 | 6 | 11 | 17 | 22 | 28 | 77 | 154 |
| 1.15 | cloud + destab + anchor | 2 | 6 | 12 | 17 | 23 | 29 | 81 | 161 |
| 1.20 | cloud; 2 destabs | 2 | 6 | 12 | 18 | 24 | 30 | 84 | 168 |
| 1.25 | cloud + 2 destabs + anchor | 3 | 6 | 13 | 19 | 25 | 31 | 88 | 175 |
| 1.30 | cloud + 1 destab | 3 | 7 | 13 | 20 | 26 | 33 | 91 | 182 |
| 1.40 | cloud + 2 destabs | 3 | 7 | 14 | 21 | 28 | 35 | 98 | 196 |

Notes (derived):
- A single boost or an accelerating anchor turns the 10-cooldown actions (launcher attack, carrier collect/transfer/throw) into **9**, so the robot occasionally gets **two actions in one turn**.
- One boost does **not** speed up HQ builds (2 × 0.9 = 1.8 → 2). It takes m ≤ 0.70 to reach 1.
- A cloud alone makes launcher attacks 12 (5 attacks per 6 turns) and launcher moves 24.

### 8.4 Duration and expiry of boosts and destabilizes

At the end of every round, after islands are processed, each entry with `lastRound ≤ currentRound + 1` is removed. The multiplier is reverted only if the list had ≤ cap entries before the removal, so the effect always equals `min(count, cap)` (`GameWorld.java:658-690`).

- **Boost** applied in round R: `lastRound = R + 10` (`GameWorld.java:328`). It is removed at the end of round **R+9**. It is active for the rest of round R and all of rounds R+1…R+9: 9 full rounds plus part of R.
- **Destabilize** applied in round R: `lastRound = R + 5` (`GameWorld.java:352`). It expires at the end of round **R+4**.
  - **When it expires** it deals `DESTABILIZER.damage` = 50 to the opposing-team robot standing on each affected square **at that moment** (`GameWorld.java:674-680`). Robots that walked out take nothing. Robots that walked in take the full 50.
  - Damage is dealt **for every entry**, with no cap. Three overlapping destabilizes deal 150, even though the slowdown stops at 2 stacks.
- Uptime (derived):
  - Destabilizer: action cooldown 70, so it can act every 7th turn. One destabilizer keeps an area slowed about 5 rounds out of 7, with one 50-damage burst per 7 turns.
  - Booster: self-boosted cooldown 126, so it can boost every 12th turn while a boost lasts 10 rounds. One booster covers 10 of every 12 rounds.
- `MapInfo` "turns left" = oldest entry's `lastRound − roundNum`. It reads 10 right after a boost and 5 right after a destabilize (`RobotControllerImpl.java:517-520`).
- The boosted area is fixed where the booster stood and does not move with it. The effect belongs to squares, not robots.

---

## 9. Islands and anchor health, round by round

All of this happens in `Island.advanceTurn()`. It runs once per round for every non-neutral island, at the start of `processEndOfRound` (`GameWorld.java:653-656`, `Island.java:90-119`).

1. Count robots of each team standing on the island's own squares. Every robot type counts (`Island.java:94-101`).
2. `diff = (100 * (own − enemy)) / area`, using Java `int` division, which **truncates toward zero** (`Island.java:102`, JAR `bipush 100 … imul … idiv`).
3. `health = min(maxHealth, health + diff)` (`Island.java:103`). Nothing decays on its own: an empty island keeps its health.
4. If `health ≤ 0`, the island turns NEUTRAL, the anchor is removed, and the owner's `currentAnchorsPlaced` is decremented. If the anchor was ACCELERATING, its −0.15 is removed (`Island.java:104-112`).
5. Healing (only if the island is still owned): every robot of the owning team within r² 4 of any island square gets +4 (STANDARD) or +6 (ACCELERATING), capped at max HP (`Island.java:113-118`). Robots near several owned islands are healed once per island.

Placing an anchor (`Island.java:75-88`) sets `health = toPlace.totalHealth` (250 or 750), even when re-anchoring your own island. `TeamInfo.placeAnchor` runs only if the island was not already yours. It increments both total and current anchor counts and can end the game at once when `current / islands ≥ 0.75` (`TeamInfo.java:188-194`).

Time to neutralise with k enemy robots and no defenders (derived; 250 for STANDARD, 750 for ACCELERATING):

| island area | k = 1 | k = 2 | k = area |
|---|---|---|---|
| 1 | −100/round: 3 / 8 rounds | – | 3 / 8 |
| 4 | −25: 10 / 30 | −50: 5 / 15 | 3 / 8 |
| 5 | −20: 13 / 38 | −40: 7 / 19 | 3 / 8 |
| 9 | −11: 23 / 69 | −22: 12 / 35 | 3 / 8 |
| 10 | −10: 25 / 75 | −20: 13 / 38 | 3 / 8 |
| 15 | −6: 42 / 125 | −13: 20 / 58 | 3 / 8 |
| 20 | −5: 50 / 150 | −10: 25 / 75 | 3 / 8 |

One defender cancels one attacker in the count. Truncation means a 1-robot advantage on a big island can be worth as little as 5/round.

---

## 10. Spec disagreements (engine wins)

1. **Destabilizer move cooldown.** SPEC:199 gives 20. The engine has **25** (`RobotType.java:49`; JAR `RobotType.<clinit>` offset 105 `bipush 25`).
2. **Destabilize damage stacking.** SPEC:122 says the effect "can stack up to 2 times (a max of 2 total destabilizers can impact a square)". Only the slowdown is capped at 2. **Every** destabilize deals its 50 damage at expiry (`GameWorld.java:673-687`). The damage also hits whoever is on the square at expiry, not at cast (SPEC:122 implies "enemies in the affected area", which is consistent but easy to misread).
3. **Anchor health timing and rounding.** SPEC:136 says health changes "At the end of each turn" by "% occupied by placing team − % occupied by opponent". The engine updates once per **round**, using `trunc(100*(own−enemy)/area)` (`Island.java:102-103`, `GameWorld.java:653-656`). The spec never mentions the truncation.
4. **Overriding an accelerating anchor with a standard one** (SPEC:140: "The same anchor type does not need to be used to override"). The engine adds the −15% boost when an ACCELERATING anchor replaces a non-accelerating one (`Island.java:79-82`). It never removes the boost when a STANDARD anchor replaces an ACCELERATING one. Removal happens only on neutralisation, and only if the current anchor is ACCELERATING (`Island.java:106-108`). Result: re-anchoring an accelerating island with a standard anchor leaves its −0.15 aura in place for the **rest of the game**, even after the island is lost. This is an engine bug.
5. **Cooldown decrement timing.** SPEC:187 says "After every turn … decremented by 10". The engine decrements at the **start** of each robot's own turn, floored at 0 (`InternalRobot.java:425-427`). A newly built robot shows cooldown 10 until its first turn.
6. **Carrier throw destroys anchors too.** SPEC:110 says "The thrown resources fall into the void" and does not mention anchors (the 3.0.2 changelog, SPEC:315, only says carriers can attack with a held anchor). The engine discards **all** resources **and all held anchors** on every throw, including misses and throws at allies or HQs (`InternalCarrier.java:35-45,62-73`).
7. **`transferAnchor()` does not exist.** SPEC:178 names it. The API has `takeAnchor`, `returnAnchor` and `placeAnchor` (`RobotControllerImpl.java:1014-1107`, `975-1012`).
8. **Deposits are not team-checked.** SPEC:102 says carriers "deposit … resources" at headquarters, implying your own. `transferResource` with a positive amount accepts **any** HQ, enemy included. Only withdrawals check the team (`RobotControllerImpl.java:874-897`).
9. **Upgraded-then-converted wells.** SPEC:80 describes upgrade and conversion separately. In the engine the upgrade flag survives conversion, so a well upgraded (1400 own) and then converted (600 opposite) is an elixir well at rate 3 (`Well.java:40-55`). This is an omission rather than a contradiction.
10. **Boost duration wording.** SPEC:126 says "for the next 10 turns". The engine counts the casting round as the first of 10 and expires the boost at the end of round R+9 (`GameWorld.java:328,663`). Destabilize likewise: "5 turns" means rounds R…R+4 (`GameWorld.java:352,674`).
11. **HQ count guarantee.** SPEC:70 says 1-4 HQs per team. The validator only rejects totals outside 2…32 (`Server.java:273-278`: `MAX_STARTING_HEADQUARTERS * 8`) and never checks the per-team split. In-game behaviour does not depend on this. It only weakens the guarantee for custom maps.
12. **Cloud penalty on moves.** SPEC:60 says robots "within" clouds get +20% on movement and action cooldowns. For moves the engine uses the **destination** square (`RobotControllerImpl.java:662-663`, `InternalRobot.java:345`): moving *into* a cloud pays the penalty, moving *out* of one does not. Actions use the current square. The spec is ambiguous here; it is not a contradiction.
13. **Javadoc, not spec:** `GameConstants.PASSIVE_AD_INCREASE/PASSIVE_MN_INCREASE` say "per turn" (`GameConstants.java:77,80`). The engine pays them every 5 rounds (`InternalRobot.java:444`), which matches SPEC:84.

Checked and in agreement with the spec:
- Every other cell of the SPEC:195-204 table: costs, HQ and carrier action cooldowns, the launcher/booster/amplifier move cooldowns, health, attack values, action radii, vision radii, bytecode limits.
- Carrier move formula `floor(5+3m/8)` (SPEC:106) and throw damage `floor(5m/4)` (SPEC:110).
- 200/200 starting resources per HQ and 6/6 every 5 rounds (SPEC:84).
- Well rates 1 and 3; thresholds 600 and 1400 (SPEC:80).
- Anchor costs, health, healing 4/6 every round within 4 units, accelerating −15% within 4 units with no self-stacking (SPEC:134-138).
- Cloud +20% and vision r² 4 (SPEC:60, 156). Destabilize +10% within 15 units of a target within 13 (SPEC:122). Boost −10% within 20 units, 3 stacks (SPEC:126).
- Comms ranges 20/4/9 (SPEC:148). writeSharedArray costs 75 bytecodes (SPEC:184, `instrumenter/bytecode/resources/MethodCosts.txt:100`).
- The 75% win threshold (SPEC:66).

---

## 11. Surprises: mechanics a bot designer could easily get wrong

1. **Resources are per HQ.** A HQ can only spend what is in its own inventory. Carriers must deliver to the HQ that will build, or ferry stock between HQs (`RobotControllerImpl.java:681-688`).
2. **HQ action cooldown is 2, not 10.** A HQ can build up to 5 units or anchors in one turn, from turn 1 (`RobotType.java:21`, `InternalRobot.java:74-75`).
3. **An empty carrier moves twice per turn** (cd 5). Each extra kg slows it. At 14+ kg it needs at least a full turn per move. At 40 kg, or holding an anchor, it moves every other turn (`InternalRobot.java:332-339`).
4. **The move multiplier comes from the destination square.** Stepping into a cloud costs +20% on that move. Stepping out is free. A boost zone speeds up moves that *end* inside it (`RobotControllerImpl.java:662-663`).
5. **A single boost or accelerating anchor gives 10-cooldown units occasional double actions** (cd 9). Code that assumes "one attack per turn" misses free shots (`GameWorld.java:498-500`; §8.3).
6. **Rounding is half-up after the multiply.** HQ builds only speed up at m ≤ 0.70. Destabilizing a HQ only slows its builds if a cloud is also there (2 × 1.2 = 2.4 → 2; 2 × 1.3 = 2.6 → 3).
7. **A carrier throw empties the carrier even on a miss or on an ally/HQ**, and destroys a carried anchor (80 Ad + 80 Mn, or 300 Ex) (`InternalCarrier.java:72`). Never "test-throw".
8. **Throw damage uses total weight, anchors included**: an anchor alone hits for 50. The carrier only needs weight > 0 to attack (`RobotControllerImpl.java:770-775`).
9. **`collectResource(loc, -1)` throws on an upgraded well when fewer than 3 kg of space remain.** Pass `min(rate, 40 − weight)` (`RobotControllerImpl.java:942-949`).
10. **`takeAnchor` needs a completely empty carrier**, because the anchor weighs 40 = capacity (`InternalRobot.java:165-167`).
11. **Depositing into an *enemy* HQ is legal** and hands them the resources (`RobotControllerImpl.java:874-897`). Check the HQ's team before `transferResource` with a positive amount.
12. **Well conversion is cumulative and permanent.** Even small deliveries of the opposite resource count toward the 600-kg conversion, e.g. a carrier that empties every resource type it holds into the well. Once converted, the well never yields its original resource again. An upgraded well that converts stays upgraded (`Well.java:38-64`).
13. **Destabilize damage lands 4 rounds later, at the end of round R+4.** It hits the enemies standing in the area *then* (dodgeable), and it **stacks without cap** (`GameWorld.java:674-680`). The slowdown, by contrast, caps at 2.
14. **Boosters boost themselves first.** Their cooldown becomes 126, and a boost lasts the casting round plus 9 more (`RobotControllerImpl.java:816-818`, `GameWorld.java:328`).
15. **Anchor health only moves with net occupancy of the island's own squares, truncated** (`Island.java:102`). One defender on the island cancels one attacker. A lone attacker on a 20-square island needs 50 rounds against a standard anchor. Nothing heals or damages an unoccupied anchor.
16. **The accelerating-anchor aura can leak.** Overwriting your accelerating anchor with a standard one leaves a permanent −15% on the area for your team (`Island.java:79-83,106-108`). Harmless to you, but surprising when reading `MapInfo` multipliers.
17. **HQs cannot be damaged at all** (`InternalRobot.java:373-375`). `RobotType.HEADQUARTERS.health` is 1. Don't use it for "low HP" logic.
18. **Several RobotType fields are placeholders:**
    - `CARRIER.movementCooldown = 0` and `CARRIER.damage = 0`.
    - `BOOSTER.actionRadiusSquared = -1`, `AMPLIFIER.actionRadiusSquared = -1`, `AMPLIFIER.actionCooldown = -1`.
    - `HEADQUARTERS.movementCooldown = -1`.
    - `canAttack()` is false for HEADQUARTERS (which has a 4-damage r² 9 aura) and for DESTABILIZER.

    Threat models built from these fields under-count danger (`RobotType.java:21-66,129-132`).
19. **Robots in clouds can't be seen beyond r² 4, and a robot in a cloud sees only r² 4** (`InternalRobot.java:271-277`). But `senseCloud` and `senseNearbyCloudLocations` use full vision unless *you* are in a cloud, so cloud squares are visible from afar (`RobotControllerImpl.java:393-443`). HQ spawn squares in a cloud farther than r² 4 can't be built on, because spawning requires sensing (`RobotControllerImpl.java:689-696`).
20. **Enemy inventories are visible**: `RobotInfo.getResourceAmount/getTotalAnchors` work on enemy HQs and carriers (`RobotInfo.java:94-113`). You can see an enemy carrier holding an anchor, and an enemy HQ's stockpile.
21. **Unused idle time is lost.** Cooldowns floor at 0 and are only reduced on your own turn (`InternalRobot.java:425-427`). Being idle never stores up extra actions.
22. **Collection is per carrier with no per-well cap** (`RobotControllerImpl.java:925-973`). Up to 9 carriers (the 8 neighbours plus the well square) can all mine one well each turn.
23. **Destabilizer action r² 13 and destabilize area r² 15 both cover exactly 45 squares.** No lattice offset has d² of 14 or 15 (derived).

---

## 12. Unverified

- **UNVERIFIED:** whether any shipped map actually puts a HQ on a cloud or next to an island. That would make the HQ-on-cloud cooldown cases in §8.3 or HQ anchor healing reachable. It is a question about the map data, not engine code.
- **UNVERIFIED:** the bytecode costs of the API methods named here, apart from `writeSharedArray` (75, checked in `MethodCosts.txt:100`). They belong to another research area.
