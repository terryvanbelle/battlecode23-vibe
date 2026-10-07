# Battlecode 2023 (Tempest): round and turn order, win check, tiebreaks, exceptions

Area: **round-order**. The engine is the source of truth. Release in use: `battlecode23-3.0.15.jar` (`battlecode_version` inside the jar = `3.0.15`; `GameConstants.SPEC_VERSION` = `"3.0.14"` in both the source and the jar).

## Provenance conventions

- `ENG/` = `/home/terryvanbelle/projects/vibe/reference/battlecode23/engine/src/main/battlecode/` (git master `af42086`).
- `JAR` = `/home/terryvanbelle/projects/vibe/2023/engine/battlecode23-3.0.15.jar`, disassembled with `~/jdk/jdk8u504-b01/bin/javap -c -p -l -constants`.
- `SPEC:n` = line n of `/home/terryvanbelle/projects/vibe/reference/battlecode23/specs/specs.md.html`.
- **Source and jar match.** For every method cited below I compared the jar's `LineNumberTable` and opcodes with the source. They line up exactly: `GameWorld.runRound`, `updateRobot`, `processEndOfRound`, `checkEndOfMatch`; `Island.placeAnchor`, `advanceTurn`; `TeamInfo.placeAnchor`, `checkWin`; `InternalRobot.processBeginningOfTurn`, `processEndOfTurn`, `processEndOfRound`, `addHealth`; `ObjectInfo.eachRobot`, `eachDynamicBodyByExecOrder`, `spawnRobot`, `destroyRobot`; `RobotControllerImpl.resign`, `disintegrate`; `RobotMonitor.incrementBytecodes`, `reactivate`; `SandboxedRobotPlayer.step`; `InstrumentingMethodVisitor.visitLabelNode`, `addRobotDeathHandler`. `javap -constants battlecode.common.GameConstants` from the jar gives the same values as `ENG/common/GameConstants.java`. Where I cite a source line, the jar has the same code at that line.
- Every fact below was verified in code unless it is marked **UNVERIFIED**. "Derived" means it follows arithmetically from verified code but was not checked by running a game.

---

## 1. One round, step by step (`GameWorld.runRound`)

`ENG/world/GameWorld.java:152-202`. `Server.runMatch` calls `runRound()` repeatedly until it returns `DONE` (`ENG/server/Server.java:492-511`).

0. If `!running` (a winner was set in the previous round), write the match footer and return `DONE`. No more rounds are played (`GameWorld.java:153-163`).
1. **`processBeginningOfRound()`** (`GameWorld.java:506-515`):
   - `currentRound++`. It starts at 0 (`GameWorld.java:62`), so the first round is **1**. `rc.getRoundNum()` returns `currentRound` (`RobotControllerImpl.java:77-79`).
   - For each robot in hash order: `InternalRobot.processBeginningOfRound()` clears the indicator string. Nothing else (`InternalRobot.java:421-423`).
2. `controlProvider.roundStarted()` does nothing (`ENG/world/control/PlayerControlProvider.java:162-163`).
3. **Round 1 only:** every robot (all must be HQs, or a RuntimeException is thrown) gets `+INITIAL_AD_AMOUNT` (200) Ad and `+INITIAL_MN_AMOUNT` (200) Mn. This happens **before any robot's turn** (`GameWorld.java:169-183`; constants at `GameConstants.java:72,75`).
4. **Robot turns, `updateDynamicBodies()`** (`GameWorld.java:204-212`). For each robot in exec order (§2), `updateRobot` (`GameWorld.java:214-225`):
   1. `processBeginningOfTurn()`: `actionCooldownTurns = max(0, acd - 10)` and `movementCooldownTurns = max(0, mcd - 10)`. The bytecode limit is reset to the type's limit (`InternalRobot.java:425-429`; `COOLDOWNS_PER_TURN = 10`, `GameConstants.java:121`).
   2. `runRobot` sets the sandbox bytecode limit and `step()`s the player thread until it yields, runs out of bytecode or dies (`PlayerControlProvider.java:169-178`, `ENG/instrumenter/SandboxedRobotPlayer.java:286-313`).
   3. Bytecodes used are recorded. `processEndOfTurn()` writes bytecodes and the indicator string to the replay and increments `roundsAlive` (`InternalRobot.java:431-437`).
   4. If the player thread has **terminated** (uncaught exception, `run()` returned, `disintegrate()`) and the robot still exists, it is **destroyed now**, at the end of its own turn (`GameWorld.java:222-223`).
5. `controlProvider.roundEnded()` does nothing (`PlayerControlProvider.java:165-166`).
6. **`processEndOfRound()`** (`GameWorld.java:650-721`), in this exact order:
   1. **Islands** (`GameWorld.java:653-656`). For each island, `Island.advanceTurn()` (`ENG/world/Island.java:90-119`) runs only on islands that are not neutral:
      - **Anchor health change:** `diff = (100*(ownRobotsOnIsland - enemyRobotsOnIsland)) / islandArea`. This is Java integer division, which truncates toward zero. Robots of any type on the island's own squares count. `health = min(maxHealth, health + diff)` (`Island.java:94-103`).
      - If `health <= 0`, the island becomes NEUTRAL and the team's current-anchor count is decremented. If the anchor was ACCELERATING, its cooldown boost is removed (`Island.java:104-112`).
      - **Healing:** each robot of the owning team on any square within r² ≤ 4 of any island square gets `+healingAmount` (STANDARD 4, ACCELERATING 6) when `round % healingFrequency == 0`. The frequency is 1 for both, so healing happens every round. Health is capped at max (`Island.java:113-118`, `Anchor.java:16,21`, `InternalRobot.java:378`). An island that was neutralised in this same step has `anchorPlanted == null`, so `getLocsAffected()` is empty and it heals no one (`Island.java:129-137`).
   2. **Boost and destabilize expiry** (`GameWorld.java:659-690`). For every map square and both teams, entries with `lastRound <= currentRound + 1` are removed and the cooldown multiplier is updated. Each **destabilize** entry that expires deals `RobotType.DESTABILIZER.damage` (50) to the robot of the affected team standing on that square at that moment (`GameWorld.java:676-680`).
   3. **Per-robot end of round**, in hash order (`GameWorld.java:692-696` → `InternalRobot.processEndOfRound`, `InternalRobot.java:439-451`). For HQs only:
      - **HQ damage:** every enemy robot within r² ≤ 9 (HQ action radius) loses `HEADQUARTERS.damage` = 4 (`RobotType.java:21`).
      - **Passive income:** if `round % 5 == 0`, `+6` Ad and `+6` Mn to *that HQ* (`GameConstants.java:78-84`).
   4. Wells and team resource deltas are written to the replay. `TeamInfo.processEndOfRound()` only snapshots counters for those deltas (`GameWorld.java:698-705`, `TeamInfo.java:227-234`).
   5. **Currents:** if `round % CURRENT_STRENGTH == 0`, `applyCurrents()` runs. `CURRENT_STRENGTH = 1`, so this is every round (`GameWorld.java:708-710`, `GameConstants.java:128`). See §6.
   6. Robot positions are written to the replay (`GameWorld.java:712-715`).
   7. **`checkEndOfMatch()`** runs tiebreaks only if `currentRound >= 2000` and no winner has been set yet (`GameWorld.java:637-648`).
   8. If any winner is set, `running = false`, and the next `runRound()` returns `DONE` (`GameWorld.java:719-720`).
7. If the match is over, `controlProvider.matchEnded()` terminates all sandboxes (`GameWorld.java:190-192`).
8. Any `Exception` thrown by engine code during steps 1-7 is caught. The round returns `DONE` **without setting a winner** (`GameWorld.java:194-198`). What `Server` does with a null winner (`switch (winner)` at `Server.java:188`) was not run-tested. **UNVERIFIED** (probably a NullPointerException that puts the server into ERROR).

## 2. Turn order

- Turns run in **spawn (creation) order**, which is global and covers both teams. There is no alternation by team, no sorting by ID, and no reshuffle per round. `ObjectInfo.eachDynamicBodyByExecOrder` iterates a `TIntArrayList` of IDs (`ENG/world/ObjectInfo.java:95-111`). `spawnRobot` appends to the end of it (`ObjectInfo.java:161`). `destroyRobot` removes the ID by value (`ObjectInfo.java:187`; the jar's trove4j has `TIntArrayList.remove(int)` = remove-by-value and `removeAt(int)` = by index).
- The list is **snapshotted** at the start of the turn loop (`spawnOrderArray = dynamicBodyExecOrder.toArray()`, `ObjectInfo.java:97`). Robots destroyed earlier in the round are skipped (`existsRobot` check, `ObjectInfo.java:101-109`). Robots **built during round r are not in the snapshot**, so their **first turn is in round r+1**, at the end of the order, after every robot that existed before them.
- **Initial HQs** go first, in **ascending map-file robot ID** order. `LiveMap` sorts initial bodies by ID (`ENG/world/LiveMap.java:151-152`), and `GameWorld` spawns them in that order (`GameWorld.java:84-90`). Their IDs come from the map file and are not random (`GameMapIO.java:343`).
  - Derived: I ran a small loader that uses the jar's `GameMapIO`/`LiveMap` (`scratchpad/roundorder/MapOrder.java`) over the 103 maps in `ENG/world/resources/`. The team whose HQ moves first depends on the map: **Team A first on 44 maps, Team B first on 59**. HQs usually alternate (e.g. `B2 A3 B4 A5`), but not always: Repetition is `A2 B3 B4 A5 B6 A7 A8 B9`, BowAndArrow is `B2 A3 A4 B5`, FourNations is `B2 A3 A4 B5`.
  - With `bc.server.alternate-order=true` (default `false`, `Server.java:170,181`, `Config.java:53`), `teamsReversed` swaps the team of every initial body, not the ID order (`GameMapIO.java:347-349`). That flips which team moves first.
- `InternalRobot` implements `Comparable` (`roundsAlive`, then ID; class comment "priority to later creation", `InternalRobot.java:8-11,499-503`). **Nothing in the engine sorts robots with it** (grep of `world/` and `server/` for sort/compareTo/PriorityQueue/TreeSet). The comment is dead.
- `eachRobot` (start-of-round, end-of-round HQ damage and income, resign) iterates a `TIntObjectHashMap`, so the order is effectively random (`ObjectInfo.java:73-84`). It does not change outcomes for HQ damage or income, because those effects are additive and deaths are final.
- Turns are sequential, so a robot sees every change made by robots earlier in the same round: moves, deaths, shared-array writes (`TeamInfo.writeSharedArray` writes straight to the array, `TeamInfo.java:211-213`), anchors and boosts.
- Built robot IDs come from `IDGenerator`, seeded with the map seed. Blocks of 4096 IDs are shuffled, and the first block is 10001..14096 (`IDGenerator.java:21,48-53,73-94`). The ID says nothing about turn order.

## 3. Cooldown timing

- New robots start with `actionCooldownTurns = movementCooldownTurns = COOLDOWN_LIMIT = 10` (`InternalRobot.java:74-75`, `GameConstants.java:118`). The first `processBeginningOfTurn` sets both to 0, so **a new robot can move and act on its first turn** (round r+1).
- A robot can act or move while the cooldown is `< 10` (`InternalRobot.java:223-232`). Each action adds `round(base * multiplier)` (`GameWorld.java:498-500`, `InternalRobot.java:327-347`). The decrement is `-10` with a floor of 0 at the start of each of the robot's own turns. Cooldown cannot be banked (`InternalRobot.java:426-427`).
  - Derived consequence: several actions fit in one turn while the accumulated cooldown stays below 10. Examples: an HQ (action cooldown 2, `RobotType.java:21`) gets 5 builds or anchors per turn at multiplier 1.0 (0→2→4→6→8→10). An empty carrier (move cooldown `floor(0.375*0)+5 = 5`, `InternalRobot.java:332-339`) gets 2 moves per turn. The sustained rate is `10/cost` per turn.
- **Movement cooldown uses the multiplier at the destination.** `move()` calls `setLocation(next)` and then `addMovementCooldownTurns()`, which reads `this.location` (`RobotControllerImpl.java:659-664`, `InternalRobot.java:344-347`). Action cooldown uses the robot's current square (`InternalRobot.java:327-330`). `buildRobot` charges the HQ's cooldown before spawning (`RobotControllerImpl.java:708-719`).
- Multiplier per (square, team) = `1.0 + 0.2*cloud - 0.1*min(boosts,3) + 0.1*min(destabs,2) - 0.15*min(accelAnchors,1)`, rounded to 2 decimals after each change (`GameWorld.java:131-143,327-400`, `GameConstants.java:140-156`). Clouds are static. Their +0.2 is baked in at construction, and there is no per-round cloud processing (`GameWorld.java:136-143`). Cloud vision (r² 4) is checked at sense time (`InternalRobot.java:271-277`).

## 4. Boost, destabilize and anchor-boost timers

- `boost()` cast in round r: `lastRound = r + 10`, applied immediately to own-team squares within r² ≤ 20 (`GameWorld.java:327-339`, `RobotControllerImpl.java:813-819`). It is removed at the end of the round where `r+10 <= round+1`, i.e. **end of round r+9**. It is active from the cast through round r+9. Robots that acted before the booster in round r get 9 boosted turns.
- `destabilize(loc)` cast in round r: `lastRound = r + 5`, stored under the **opponent's** team index, applied immediately to enemy-team squares within r² ≤ 15 of `loc` (`GameWorld.java:351-362`, `RobotControllerImpl.java:843-848`). There is **no damage at cast time**. At the **end of round r+4** the entry expires and deals 50 damage to the enemy robot standing on each affected square *at that moment* (`GameWorld.java:672-688`).
- Stack caps (boost 3, destabilize 2, accel-anchor 1) limit **only the multiplier**. Extra entries are still stored, and they take over the multiplier as older ones expire. Removal subtracts only while `size <= MAX` (`GameWorld.java:333-337,356-360,665-669,682-685`). **Destabilize damage is not capped**: every expiring entry deals 50, including a 3rd, 4th and so on (`GameWorld.java:673-687`).
- `MapInfo` `turnsLeft` = `oldest lastRound - currentRound` (`RobotControllerImpl.java:517-520`). That is 10..1 for a boost and 5..1 for a destabilize. `turnsLeft == 1` means "expires (and destabilize damage lands) at the end of this round".
- An accelerating anchor's -0.15 is applied **at placement time** (`Island.java:79-82` → `GameWorld.java:374-387`). It is removed only in `advanceTurn` when an ACCELERATING anchor's health reaches 0 or below (`Island.java:106-108`).

## 5. Anchor and island bookkeeping that the win check depends on

- `placeAnchor` (`Island.java:75-88`): sets owner, anchor type and health = full. It calls `TeamInfo.placeAnchor(team)` **only if the island was not already owned by the placing team** (`Island.java:76,85-87`). You cannot place on an island owned by the enemy while their anchor stands (`Island.java:60-66`).
- `TeamInfo.placeAnchor`: `totalAnchorsPlaced++` (tiebreak counter) and `currentAnchorsPlaced++`. Then if `(float)currentAnchorsPlaced / numIslands >= 0.75f`, it calls `checkWin`. `checkWin` re-counts owned islands, and the result is `setWinner(team)` with `DominationFactor.CONQUEST` (`TeamInfo.java:166-194`, `GameConstants.java:93`).
- `removeAnchor` decrements only `currentAnchorsPlaced`. `totalAnchorsPlaced` never decreases (`TeamInfo.java:200-202`).
- `numIslands` = number of distinct non-zero island IDs in the map (`GameWorld.java:93-108,895-897`). It is the same value as `rc.getIslandCount()` (`RobotControllerImpl.java:92-94`).

## 6. Currents (`GameWorld.applyCurrents`, `GameWorld.java:723-782`)

- Applied every round at the **end of the round**, after island updates, destabilize damage, HQ damage and income, and **before** the win/tiebreak check (§1 step 6.5).
- Every robot forecasts a destination: its own square plus the current there (CENTER = stays put). A robot does not move if its destination is impassable or off-map, or if **more than one robot forecasts that square**. A stationary robot forecasts its own square, so a robot pushed onto an occupied, non-moving square is blocked. Blocking propagates back along chains (`addToNotMoving`, `GameWorld.java:723-734,747-761`). Cycles and swaps are not blocked.
- Being moved by a current adds **no cooldown** and goes through `setLocationForCurrents` (`InternalRobot.java:317-321`). It works on both teams and ignores cooldowns.
- Map validation (on by default, `Config.java:52`) guarantees that currents never point off-map or into walls and that no two currents end on the same square (`Server.java:422-437`).

## 7. Win check (75% of islands)

- Checked **only at the moment an anchor is placed** on an island the placing team did not already own (§5). There is no per-round re-check, and losing islands can never trigger a win for the other side.
- Threshold: `(float)k / N >= 0.75f`, so **k = ceil(0.75·N)**. For N = 4,5,6,7,8,9,10,12,16,20,35 that is k = 3,4,5,6,6,7,8,9,12,15,27 (derived from `TeamInfo.java:191`; also printed per map by the loader in §2). Float rounding cannot matter for N ≤ 35.
- The winner is set **mid-turn**, but the game does **not** stop there. Every remaining robot in the round still takes its turn, the full end-of-round processing runs, and only then does `running = false` (`GameWorld.java:719-720`). The game's last round is the round in which the anchor was placed.
- `setWinner` overwrites unconditionally (`GameStats.java:19-21` via `TeamInfo.java:180-181`, `GameWorld.java:517-520`). A later `resign()` in the same round therefore replaces a CONQUEST result. Both teams cannot reach 75% in one round, because islands are exclusive and only end-of-round decay frees one.

## 8. Round-2000 tiebreak chain

- The map's `rounds` is always `GAME_MAX_NUMBER_OF_ROUNDS = 2000`; map files cannot change it (`GameMapIO.java:228`, `GameConstants.java:170`). `timeLimitReached()` is `currentRound >= 2000` (`GameWorld.java:630-632`). It is evaluated at the very end of round 2000, so **round 2000 is played in full**, including island decay, HQ damage and currents.
- Order, stopping at the first strict inequality (`GameWorld.java:637-648`):
  1. **More islands owned** right now. Ownership is read *after* round 2000's anchor-health update (`GameWorld.java:525-544`). → `MORE_SKY_ISLANDS`
  2. **More `totalAnchorsPlaced`**: placements on islands you did not own at the time. Re-capturing an island counts again. Overriding your own anchor does not count (`GameWorld.java:549-561`, `Island.java:85-87`). → `MORE_REALITY_ANCHORS`
  3. **More elixir** in `TeamInfo.elixirCounts` (`GameWorld.java:566-581`). → `MORE_ELIXIR_NET_WORTH`
  4. **More mana** (`GameWorld.java:586-601`). → `MORE_MANA_NET_WORTH`
  5. **More adamantium** (`GameWorld.java:606-621`). → `MORE_ADAMANTIUM_NET_WORTH`
  6. **`Math.random() < 0.5 ? A : B`** (`GameWorld.java:626-628`). → `WON_BY_DUBIOUS_REASONS`
- `TeamInfo` resource counters = the sum of every *living* robot's inventory: HQ stockpiles plus carrier cargo. Every `InternalRobot.addResourceAmount` updates both the robot inventory and `TeamInfo` (`InternalRobot.java:141-145`). A destroyed robot's inventory is subtracted (`GameWorld.java:828-830`). A carrier throw-attack subtracts its cargo (`ENG/world/robots/InternalCarrier.java:35-45`). Resources deposited into wells leave the count (`RobotControllerImpl.java:912-921`). Anchors, held or planted, have no resource value.

## 9. Resign

- `rc.resign()` (`RobotControllerImpl.java:1164-1173`): destroys **every robot of the caller's team**, including HQs and the caller itself, via `eachRobot` → `destroyRobot`. It then sets `winner = opponent` with `DominationFactor.RESIGNATION`.
- The game still finishes the **current round**: later robots in the snapshot (only the opponent's survive) take their turns, end-of-round processing runs, and then `running = false`.
- The resigning robot's own thread is not killed immediately. `terminate()` while running only sets `shouldDie` (`SandboxedRobotPlayer.java:324-341`). The thread throws `RobotDeathException` at its next instrumented basic block (`RobotMonitor.java:127-130`).
- If both teams resign in the same round, the **last** `resign()` call decides the result, because `setWinner` overwrites.
- The spec has no resign section. Only the changelog says "Resigning now means the other player wins automatically" (SPEC:508, changelog v1.1.0). The javadoc says "Causes your team to lose the game" (`ENG/common/RobotController.java:1064-1069`).
- No other early end exists. A team with zero robots, or zero HQs after crashes, plays on until round 2000 (`checkEndOfMatch` is the only per-round end check, `GameWorld.java:637-648`).

## 10. Exceptions, bytecode overrun, death

- **Bytecode accounting:** `RobotMonitor.incrementBytecodes` is injected at the end of each basic block. When `bytecodesLeft <= 0`, the thread `pause()`s **in place**, mid-method (`ENG/instrumenter/inject/RobotMonitor.java:126-153`). The limit is checked per basic block, so a block can overshoot.
- **Resume:** on the next `step()`, `reactivate()` runs. If `bytecodesLeft < 0`, the debt carries over: `bytecodesLeft += limit`. Otherwise `bytecodesLeft = limit` (`RobotMonitor.java:297-308`). The `while (bytecodesLeft <= 0) pause();` loop (`RobotMonitor.java:147-149`) means a debt larger than one limit **skips whole turns**. The engine still runs `processBeginningOfTurn` for those turns, so cooldowns keep decrementing.
- **State kept across an overrun:** the whole Java stack and locals are kept, and the code continues at the exact instruction. The world, however, has moved on a full round: currents applied, HP changed, other robots moved, cooldowns decremented, `getRoundNum()` advanced. Any cached sensing is stale. The game keeps nothing like a "turn state". Actions taken before the cutoff stand, and actions after it happen in the new round.
- **`Clock.yield()`** = `RobotMonitor.pause()` (`ENG/common/Clock.java:24-26`). Unused bytecodes are **not** carried over: on resume `bytecodesLeft = limit` when it is ≥ 0.
- **Failed actions:** `rc` action methods run all `assert*` checks before mutating anything (e.g. `move` at `RobotControllerImpl.java:659-664`, `buildRobot` at `708-719`, `placeAnchor` at `1002-1012`). A thrown `GameActionException` leaves no side effects and costs no cooldown.
- **Exception penalty:** the instrumenter adds `EXCEPTION_BYTECODE_PENALTY = 500` to the basic block that starts at **each exception-handler label in player code**. You pay it when control *enters* a catch handler (or a finally block's exceptional path), not when the exception is thrown (`ENG/instrumenter/bytecode/InstrumentingMethodVisitor.java:623-627`, `GameConstants.java:69`; jar has `sipush 500` at line 626).
- **Uncaught exception, or returning from `run()`:** the player thread ends and `terminated = true` (`SandboxedRobotPlayer.java:175-219`; the "froze ... returned from its run() method" message is at 184-188). `GameWorld.updateRobot` then **destroys the robot at the end of that turn** (`GameWorld.java:222-223`). **This includes HQs.** The `step()` comment "not gonna lose the robot" at `SandboxedRobotPlayer.java:288-292` is misleading, because `GameWorld` destroys the robot anyway.
- **`disintegrate()`** throws `RobotDeathException` (`RobotControllerImpl.java:1159-1161`). Death is processed the same way, at the end of the turn. **HQs can disintegrate.**
- **Death cannot be caught:** `RobotDeathException extends VirtualMachineError` (`ENG/instrumenter/RobotDeathException.java:10`). The instrumenter puts a highest-priority `catch (VirtualMachineError) { throw; }` around every method that has a try/catch (`InstrumentingMethodVisitor.java:280-293`). As a result, `catch (Throwable)` cannot swallow death. The same applies to StackOverflowError and OutOfMemoryError, which are also VirtualMachineErrors.
- **Mid-round deaths** (launcher hit, carrier throw, etc.) are immediate (`InternalRobot.java:379-380`). A dead robot that has not yet moved this round is skipped (`ObjectInfo.java:101-109`). **HQs ignore all damage** (`InternalRobot.java:373-375`).

---

## Spec disagreements

1. **Currents timing.** SPEC:58 says "forced to move ... at the end of the turn, applied after existing robot movement." The engine applies all currents once at the **end of the round**, after all turns, after island update, destabilize damage, HQ damage and income (`GameWorld.java:708-710`). There is no per-turn current.
2. **Anchor health timing.** SPEC:136 says "At the end of each turn each anchor's health will change". The engine does it once per **round** in `processEndOfRound` (`GameWorld.java:653-656`). The formula is `(100*(own-enemy))/area`, integer-truncated toward zero (`Island.java:102`).
3. **Cooldown decrement timing.** SPEC:187 says "After every turn, the movement and action cooldowns of all robots are decremented by 10." The engine decrements each robot's cooldowns at the **start of that robot's own turn**, floored at 0 (`InternalRobot.java:425-429`). A robot can't observe the difference itself, but a robot spawned in round r has cooldown 10, not 0, until its own first turn in r+1.
4. **"Instantly win".** SPEC:66 and SPEC:160 say "instantly win" and "immediately wins". The engine records the winner at once, but **the rest of the round is still played** before the game stops (`GameWorld.java:717-720`).
5. **HQs "cannot be destroyed".** SPEC:70 and SPEC:102 say they cannot. In the engine, damage cannot destroy them (`InternalRobot.java:373-375`), but an HQ **is destroyed** if its code throws an uncaught exception, returns from `run()`, calls `disintegrate()`, or its team resigns (`GameWorld.java:222-223`, `RobotControllerImpl.java:1159-1173`).
6. **"Unhandled exceptions may paralyze your robot".** SPEC:249 says this. In the engine, an unhandled exception **destroys** the robot at the end of that turn (`SandboxedRobotPlayer.java:191-206` + `GameWorld.java:222-223`).
7. **"Throwing any Exceptions cause a bytecode penalty of 500".** SPEC:249 says this. The engine charges 500 when entering an exception **handler** in player code (`InstrumentingMethodVisitor.java:623-627`). An exception that nobody catches costs nothing, but the robot dies. Each handler an exception passes through (catch or finally) costs 500.
8. **Destabilize stacking.** SPEC:122 says "can stack up to 2 times (a max of 2 total destabilizers can impact a square)". The engine caps only the cooldown multiplier at 2. **Every** destabilize on a square deals its 50 damage on expiry, with no cap (`GameWorld.java:673-687`). The spec's "lasts for 5 turns, after which damage is dealt" means damage at the end of round cast+4 (§4).
9. **Determinism.** SPEC:216 says "re-running the same match ... produces exactly the same results". The final tiebreak uses unseeded `Math.random()` (`GameWorld.java:627`), so a game that reaches step 6 can have a different winner on each run.
10. **Tiebreak wording.** SPEC:165 says "anchors placed in total throughout the round". The engine counts the whole **game** (`totalAnchorsPlaced`, never decremented). This is a wording slip, not a behavioural conflict.
11. **Turn order.** SPEC:218 says "Every round each robot sequentially takes its turn" and does not specify the order. The engine uses **spawn order**, with initial HQs by ascending map ID. Mixed-team order is decided by the map file. New robots act from the next round (§2). This is an omission, not a contradiction.
12. **Island healing order.** SPEC:138 says allies are "healed every round, at the end of the round". This matches, but the engine heals **before** destabilize damage and HQ damage in the same end-of-round (`GameWorld.java:653-696`). A full-HP robot therefore gets no protection from healing against HQ damage in that round. Not contradicted by the spec, but not stated either.

No disagreement found for: the 75% threshold (`>= 0.75f`), the order of tiebreaks 1-6, HQ damage 4 at end of round within r² 9, passive income 6/6 every 5 rounds per HQ, initial 200/200 per HQ, the bytecode-overrun "resume at exactly that point" behaviour, HQ bytecode limits.

---

## Surprises: mechanics a bot designer could easily get wrong

1. **The game does not stop the moment you hit 75%.** Every robot after your carrier in the exec order still plays round r, and only then does the match end. Nothing they do can undo it, except a resign by your own team.
2. **Turn order is spawn order across both teams.** It is not "Team A then Team B", and a new robot always moves after everything that already existed. Which team's HQs move first depends on the map: B first on 59 of 103 bundled maps, A on 44. Bots built in round r cannot act until round r+1, but they are already exposed in round r to HQ damage, destabilize expiry, island occupancy counting and currents.
3. **Everything at end of round reads positions after all turns.** That covers HQ damage (r² 9), destabilize damage, island occupancy and decay, and island healing. You can step into enemy HQ range, act, and step out in the same turn without taking damage. Currents move robots **after** these checks, so a robot on a current is damaged or counted where it stood, then displaced.
4. **Destabilize deals no damage when cast.** It deals 50 at the end of round cast+4 to whoever of the target team is standing on each affected square then. Its damage is uncapped by the 2-stack limit, so N destabilizes means N×50.
5. **Movement cooldown uses the destination square's multiplier.** Stepping into a cloud costs +20% on that move. Stepping out of a cloud onto a boosted square gets the boost.
6. **Cooldowns chain within a turn.** You may act while the cooldown is < 10, the turn start subtracts 10, and nothing is banked. An HQ can do up to 5 builds or anchors per turn. An empty carrier makes 2 moves per turn. Multipliers below 1.0 can push other units under 10 per action.
7. **An uncaught exception, or returning from `run()`, permanently deletes the robot, HQs included.** You lose that HQ's whole stockpile, which also drops your tiebreak totals. `catch (Throwable)` around the main loop is mandatory. Even so, death (VirtualMachineError, including StackOverflowError) cannot be caught.
8. **Bytecode overrun resumes mid-code in the next round with stale data, and the overshoot is a debt.** A huge overshoot skips whole turns. Unused bytecodes are not carried over on `Clock.yield()`. Check `rc.getRoundNum()` around expensive sections.
9. **The anchor-placement tiebreak counts recaptures.** An island lost and recaptured adds +1 again. Re-anchoring your own island to refresh health adds 0.
10. **Resource tiebreaks count carrier cargo and HQ stockpiles of living robots only.** Dumping resources into wells, throwing them, or losing a loaded carrier reduces them. Anchors are worth 0.
11. **The final tiebreak is non-deterministic** (`Math.random()`). A rerun of the same game can flip the result.
12. **Island decay uses integer percent per round.** One enemy on an area-20 island costs 5 health per round (50 rounds to kill a standard anchor). On an area-1 island it costs 100 per round. 20 enemies on an area-20 island kill a standard anchor (250) in 3 rounds and an accelerating anchor (750) in 8. Own robots on the island offset this one for one, and health never exceeds max. Robots are counted before the same round's HQ or destabilize deaths.
13. **Win check fires only on placement.** If the enemy's anchor dies at end of round r, you can place there from round r+1, and the win triggers on that placement.
14. **Engine bug, derived from code and not run-tested: overwriting your own ACCELERATING anchor with a STANDARD one never removes the -0.15 cooldown boost** (`Island.java:79-83` adds the boost only when switching *to* ACCELERATING; `Island.java:106-108` removes it only if the planted anchor is ACCELERATING). The boost then persists for that team around the island for the rest of the game, even after the island is lost.
15. **`resign()` deletes all your robots immediately but still lets the opponent finish the round.** If both teams resign in one round, the last resigner loses.
16. **Shared-array writes are visible within the same round** to any robot later in the exec order. Earlier robots see them next round.
17. **Passive income goes to each HQ separately** (+6 Ad/+6 Mn each at the end of rounds 5, 10, …, 2000). Initial 200/200 goes to *each* HQ at round 1, before the first turn.

### Notes on what was not verified

- How `Server` handles a match that ends with a null winner after an engine exception (§1 step 8): **UNVERIFIED**.
- The surprise #14 bug is derived from code and was not reproduced in a running game.
- The map-order counts come from `ENG/world/resources/*.map23` (git master) loaded with the jar's classes. Whether the jar bundles byte-identical map files is **UNVERIFIED**.
