# Bytecode accounting and sandbox runtime (Battlecode 2023, engine 3.0.15)

Area: **bytecode-runtime**. Covers the instrumenter (how bytecodes are counted), `MethodCosts.txt`, allowed and banned
classes, exception penalty, overruns and `Clock`, static initialisation, memory, robot output, seeds and robot IDs,
determinism, and the server properties a headless runner can set.

## How this was verified

- **Source tree** (git master `af42086`, 2023-02-05): `/home/terryvanbelle/projects/vibe/reference/battlecode23/engine/src/main/battlecode/`,
  written below as `E/`. Line numbers are 1-based lines in those files.
- **Release jar**: `engine/battlecode23-3.0.15.jar` (sha256 `5d4e42a5…ed72a`, matching `tools/lib.sh:12`), written below
  as `JAR`. `battlecode_version` inside the jar reads `3.0.15`.
- **Source is the same as the jar.** I compiled every `.java` under `E/` with JDK 8u504 against `JAR`, then ran
  `javap -c -p -constants` on all 136 classes from each side and diffed the output (constant-pool indices masked). The
  only difference is in `GameMapIO$Serial.deserialize`: the jar keeps `rounds = 2000` in a local variable (`sipush 2000; istore 7`)
  where my build inlines the constant. That is a compiler artefact with the same behaviour. The three resource lists
  (`MethodCosts.txt`, `AllowedPackages.txt`, `DisallowedClasses.txt`) in `JAR` are byte-identical to the source. So
  wherever this report cites source lines, the jar behaves the same way.
- **Empirical probe.** I ran a throwaway bot (`bcprobe`, written in the session scratchpad, never in the repo) on map
  `maptestsmall` with `JAR`, JDK 8u504, `-Dbc.server.websocket=false`. Its HQ measures `Clock.getBytecodeNum()`
  deltas around single operations (calibrated, flushed with an empty user-method call), forces overruns, and spawns
  carriers that return from `run()`, throw, overflow the stack and call `System.exit`. A second throwaway bot (`bcdead`)
  fails instrumentation on purpose. I also wrote a replay dumper that uses the jar's `battlecode.schema` classes. Facts
  confirmed this way are tagged **[measured]**. The appendix lists the runs.
- Anything not confirmed in code or by measurement is marked **UNVERIFIED**.

---

## 1. How bytecodes are counted (instruction level)

Counting is done at instrumentation time, per method, by `E/instrumenter/bytecode/InstrumentingMethodVisitor.java`
(called from `InstrumentingClassVisitor.visitMethod`, `E/instrumenter/bytecode/InstrumentingClassVisitor.java:77-115`).

1. **Every ordinary JVM instruction costs 1.** This covers field get/put (`InstrumentingMethodVisitor.java:295-299`),
   every zero-operand instruction including arithmetic, array load/store, `arraylength`, `athrow` and returns
   (`:301-303`), `ldc` (`:336-341`), local load/store (`:642-646`), `bipush`/`sipush` (`:648-658`), `iinc` (`:149-151`),
   jumps and switches (`:140-145`), and `new`/`checkcast`/`instanceof` (`:629-640`).
2. **Method invocations cost nothing for the call instruction itself.** `visitMethodInsnNode` never does `bytecodeCtr++`
   for an ordinary call (`:405-525`). The only cost is the `MethodCosts.txt` value, when the callee is listed (`:454-458`).
   A user method therefore costs only its argument pushes plus its own instrumented body. **[measured]**
   `add(1,2)`, a static user method with body `return a+b`, costs 7 in total: 2 pushes + 4 for the body + `istore`.
3. **`invokedynamic` (lambda creation) costs 0** (`:343-403`, no increment).
4. **Labels, frames and line numbers cost 0.** However, every label ends a basic block (`:623-627`). Because `javac`
   emits a label for each source line, the counter is in practice flushed at almost every line.
5. **Array creation is charged per element.** `newarray`/`anewarray` cost `max(1, length)`
   (`:629-640` and `:648-658`; `RobotMonitor.sanitizeArrayIndex`, `E/instrumenter/inject/RobotMonitor.java:192-194`).
   `multianewarray` costs the product of `max(dim,1)` over the given dimensions (`:585-621`; `RobotMonitor.java:208-215`).
   The allocation instruction itself adds nothing on top. The charge is deferred through `incrementBytecodesWithoutInterrupt`
   (`RobotMonitor.java:166-176`) and applied at the next flush. **[measured]** `new int[100]` = 100,
   `new int[0]` = 1, `new int[10][20]` = 200.
6. **Entering an exception handler costs `GameConstants.EXCEPTION_BYTECODE_PENALTY` = 500.** The 500 is attached to the
   handler's label (`InstrumentingMethodVisitor.java:623-627`; `E/common/GameConstants.java:69`; jar `javap`:
   `EXCEPTION_BYTECODE_PENALTY = 500`). See section 5.
7. **The counter is flushed at the end of each basic block**, through `RobotMonitor.incrementBytecodes(n)` (`:681-687`).
   Flush points are labels, jumps, returns, `athrow`, and the following calls: any call to a team class, to an
   `instrumented/…` class, or to a `battlecode/…` class, unless the `MethodCosts.txt` entry sets the third column to `false`
   (`:452-458`, `:522-523`). The robot can only be paused inside `incrementBytecodes` (`RobotMonitor.java:126-153`), so
   the robot is always paused at a basic-block boundary, never mid-block.
8. **A listed method's cost is charged before the method runs.** For an entry whose third column is `true`, the cost is
   added to the block counter and the block is flushed before the call instruction (`:454-458` then `:522-523`; the column is
   named `shouldEndRound` but means "end basic block", `E/instrumenter/bytecode/MethodCostUtil.java:43-52`). So if, for
   example, `senseNearbyRobots` (100) drives the budget to ≤ 0, the robot pauses before the sensing call and makes it in
   the next round.
9. **`hashCode()` and `toString()` on any receiver are rewritten** to `ObjectMethods.hashCode/toString` at a flat cost of
   1 (`:407-428`). This overrides `MethodCosts.txt`: `MapLocation.hashCode` and `MapLocation.toString` (listed at 2) and
   `MapInfo.toString` (listed at 15) actually cost 1. **[measured]** `loc.hashCode()` = 1.
10. **`debug_*` methods**: a team method whose name starts with `debug_` and returns `void` is handled by the
    `bc.engine.debug-methods` flag (default `false`, `E/server/Config.java:64`). When the flag is false, the call is removed,
    but the argument expressions are still evaluated and charged; only the call is replaced by `pop`s
    (`InstrumentingMethodVisitor.java:486-519`). When the flag is true, the body runs uncharged, because
    `incrementBytecodes` skips counting while `debugLevel > 0` (`:164-166`, `RobotMonitor.java:132-150`).
11. **`synchronized` methods are silently stripped of the flag** (`InstrumentingClassVisitor.java:88`). A `synchronized`
    block (`monitorenter`/`monitorexit`) in player code is an instrumentation error (`InstrumentingMethodVisitor.java:325-332`).

## 2. `MethodCosts.txt` (fixed costs)

File: `E/instrumenter/bytecode/resources/MethodCosts.txt` (identical in `JAR`). Format: `owner/method cost endsBlock`,
parsed in `MethodCostUtil.java:62-70`. The lookup is by name only, so all overloads share a cost. If the exact owner is
not listed, the lookup also checks the owner's interfaces and superclasses (`MethodCostUtil.java:84-110`). Team classes are
never looked up (`InstrumentingMethodVisitor.java:711-718`). A method that is not listed costs 0 for the call. The table
below shows the cost and, after the slash, the "ends block" flag (T/F).

**RobotController** (all T except where marked F):

| Cost | Methods (MethodCosts.txt line) |
| --- | --- |
| 200 | `senseNearbyIslands` (L83) |
| 100 | `senseNearbyRobots` (L85), `senseNearbyMapInfos` (L94), `senseNearbyWells` (L92), `senseNearbyCloudLocations` (L90), `senseNearbyIslandLocations` (L84), `getAllLocationsWithinRadiusSquared` (L46) |
| 75 | `writeSharedArray` (L100) |
| 25 | `senseRobot` (L86) |
| 20 | `senseIsland`, `senseTeamOccupyingIsland`, `senseAnchorPlantedHealth`, `senseAnchor`, `senseCooldownMultiplier`, `senseDestabilizeTurns`, `senseBoostTurns` (L76-82); `getIslandCount` (L52); `getRobotCount` (L58) |
| 15 | `senseRobotAtLocation` (L87) |
| 10 | `canMove` (L32), `canBuildRobot` (L29), `canCollectResource` (L30), `canTransferResource` (L31), `canBuildAnchor`, `canTakeAnchor`, `canPlaceAnchor`, `canReturnAnchor` (L33-36), `canBoost`, `canDestabilize` (L41-42), `canWriteSharedArray` (L43); `getWeight` (L50, F) |
| 5 | `canAttack` (L28), `canSenseLocation`, `canActLocation`, `canSenseRobot`, `canSenseRobotAtLocation` (L37-40), `isLocationOccupied` (L63), `onTheMap` (L73), `sensePassability` (L88), `senseCloud` (L89), `senseWell` (L91), `senseMapInfo` (L93), `getNumAnchors` (L53); `getResourceAmount` (L49, F) |
| 2 | `readSharedArray` (L74) |
| 1 | `getID`, `getHealth`, `getLocation`, `getMapWidth`, `getMapHeight`, `getRoundNum`, `getTeam`, `getType`, `getActionCooldownTurns`, `getMovementCooldownTurns`, `isActionReady`, `isMovementReady`, `isTransformReady`, `adjacentLocation` (L25-65); `getAnchor` (L51, F) |
| 0 | `move` (L68), `attack` (L26), `buildRobot` (L27), `collectResource`, `transferResource` (L66-67), `buildAnchor`, `takeAnchor`, `placeAnchor`, `returnAnchor` (L69-72), `boost`, `destabilize` (L98-99), `resign` (L75), `disintegrate` (L44), `setIndicatorDot`, `setIndicatorLine`, `setIndicatorString` (L95-97) |

**Other `battlecode.common` classes:**

- **`MapLocation`** (L12-24, all F): `add`, `compareTo`, `directionTo`, `distanceSquaredTo`, `equals`, `hashCode`*,
  `isWithinDistanceSquared`, `isAdjacentTo`, `isWithinSensorRadius`, `subtract`, `toString`*, `translate` cost 2 each;
  `valueOf` costs 25. The constructor `new MapLocation(x,y)` is not listed, so it costs 0 beyond `new`, `dup` and the
  argument pushes. **[measured]** 5 in total. The `x` and `y` fields cost 1 each (getfield).
  (*Rewritten to cost 1, see section 1 item 9.)
- **`Direction`** (L4-11): `equals`, `getDeltaX`, `getDeltaY`, `rotateLeft`, `rotateRight`, `opposite`,
  `allDirections`, `cardinalDirections` cost 1. `values()` and `getDirectionOrderNum()` are not listed, so they cost 0.
  **[measured]** `Direction.values()` = 0.
- **`RobotType`** (L101-107) and **`Team`** (L108-109): 1 each. **`WellInfo`** (L110-114): 1, except `getRate` = 2.
  **`MapInfo`** (L115-124): `getMapLocation` = 1, the other getters = 2, `toString` = 15* (really 1).
- **Free (not listed)** (javap of `JAR` against the table): all `RobotInfo` getters (`getID`, `getLocation`, `getTeam`,
  `getType`, `getHealth`, …; the public fields cost 1 via getfield), the `Anchor` getters, `GameActionException.getType`,
  and every enum's `values()`/`valueOf()`.
- **`Clock`** (L1-3): `yield` 0/T, `getBytecodesLeft` 0/F, `getBytecodeNum` 0/F.

**`java.lang` entries** (L125-218): every `Math.*` and `StrictMath.*` method (`abs`, `min`, `max`, `sqrt`, `pow`, `atan2`,
`floor`, `round`, …) costs 1. These `String` methods cost 1: `compareTo`, `compareToIgnoreCase`, `contains`, `contentEquals`,
`endsWith`, `equals`, `equalsIgnoreCase`, `indexOf`, `lastIndexOf`, `regionMatches`, `replace`, `startsWith`.
`StringBuffer`/`StringBuilder` `append`, `delete`, `deleteCharAt`, `indexOf`, `insert`, `lastIndexOf`, `replace` cost 1.
Every other `java.lang` call costs 0. That includes `String.charAt`, `length`, `substring`, `toCharArray`, `valueOf` and
`format`, `Integer.parseInt`/`valueOf`, `Character.*`, and array `clone()`. They cost 0 because `java/lang` is not
instrumented (`E/instrumenter/bytecode/ClassReferenceUtil.java:127-130`) and array owners return no MethodData
(`MethodCostUtil.java:85-86`).

**[measured]** costs from the probe, call only, with argument pushes and stores subtracted:

| Call | Cost |
| --- | --- |
| `readSharedArray` | 2 |
| `writeSharedArray` | 75 |
| `senseNearbyRobots()` | 100 |
| `canMove` | 10 |
| `getLocation` + `distanceSquaredTo` | 1 + 2 |
| `setIndicatorString` | 0 |
| `System.out.println(const)` | 0 (the `getstatic` costs 1) |
| `String.charAt` | 0 |
| `String.indexOf` on a 1,001-character string | 1 |
| `int[1000].clone()` | 0 |
| `System.arraycopy` of 1,000 elements | 1,000 |
| `HashMap.put` on an empty `HashMap<Integer,Integer>` (includes its first-use table allocation) | ≈143 |
| `HashMap.get` | ≈52 |
| `ConcurrentHashMap.put` | 0 |
| `ConcurrentHashMap.get` | 0 |

## 3. Which classes may be used, and which are charged

- **Allowed packages** (`E/instrumenter/bytecode/resources/AllowedPackages.txt:1-26`): `java/io`, `java/lang`,
  `java/lang/invoke`, `java/math`, `java/util`, `java/util/function`, `java/util/regex`, `java/util/stream`, `java/text`,
  `battlecode/common`, and a list of `scala/…` packages. The match is by **exact package**, so subpackages are not
  automatically allowed (`ClassReferenceUtil.java:98-102`). For example, `java/util/concurrent/*` is illegal, apart from
  the 4 classes the engine remaps (below).
- **Disallowed classes** (`DisallowedClasses.txt:1-49`), even inside allowed packages: `java/io/File*`,
  `RandomAccessFile`, `ClassLoader`, `Compiler`, `Process*`, `Runtime`, `SecurityManager`, `Thread`, `ThreadGroup`,
  `ThreadLocal`, `InheritableThreadLocal`, `Calendar`, `Date`, `Formatter`, `GregorianCalendar`, `Locale`, `Properties`,
  `ResourceBundle` and its variants, `TimeZone`, `Timer`, `TimerTask`, `UUID`, `WeakHashMap`, `scala/Symbol`, and a few more.
  Checked in `ClassReferenceUtil.java:174-178`.
- **Banned methods**, rejected at instrumentation (`InstrumentingMethodVisitor.java:535-583`):
  - `Object.wait`, `notify` and `notifyAll`.
  - **Every `java.lang.Class` method except `desiredAssertionStatus`.** **[measured]** `getClass().getName()` is rejected.
  - `PrintStream(String…)` constructors.
  - `String.intern`.
  - These `System` methods: `currentTimeMillis`, `nanoTime`, `gc`, `getProperties`, `getSecurityManager`, `getenv`,
    `load`, `loadLibrary`, `mapLibraryName`, `runFinalization`, `runFinalizersOnExit`, `setProperties`, `setSecurityManager`.
  - Any direct call into `java/lang/invoke/*`.
  - **Method references** (`X::m`) to anything the instrumenter rewrites or charges are also rejected (`:366-393`). This
    covers `hashCode`, `toString`, `new Random()`, `Math.random`, the `String` regex methods, `printStackTrace`,
    `debug_*` methods, and every method listed in `MethodCosts.txt` (for example `MapLocation::distanceSquaredTo`). Use an
    explicit lambda instead.
- **Team package names** may not start with `battlecode.`, `java.`, `com.sun.`, `sun.`, `org.apache.`, `org.objectweb.` or
  `kotlin.` (`E/instrumenter/TeamClassLoaderFactory.java:41-68`). Every class found under the team URL counts as a team
  class and is instrumented (`TeamClassLoaderFactory.java:199-201`, `:438-464`). The entry point must be
  `<package>.RobotPlayer.public static run(RobotController)` (`E/instrumenter/SandboxedRobotPlayer.java:246-264`).
- **What is charged as if it were your code**: classes under `java/util/…` and `java/math/…` (not `java/util/Iterator`,
  `java/util/concurrent/TimeUnit`, `java/util/jar`, `java/util/zip` or `java/util/invoke`), and `scala/…`. These are
  re-read from the running JDK's class library, renamed `instrumented/…`, and instrumented per robot
  (`ClassReferenceUtil.java:104-133`, `TeamClassLoaderFactory.java:465-481`). `java/lang`, `java/io` and `java/text` are
  **not** instrumented, so they cost only their `MethodCosts.txt` entry or 0.
  - Consequence: the bytecode cost of `HashMap`, `ArrayList`, `PriorityQueue` and similar depends on the JDK's `rt.jar`
    that runs the engine. My measurements are for JDK 8u504.
- **Engine replacements** (`ClassReferenceUtil.java:161-172`):
  - `java.lang.System` becomes `inject.System` (section 8).
  - `java.util.concurrent.ConcurrentHashMap` becomes `inject.ConcurrentHashMap`, which extends the real, uninstrumented
    `java.util.Hashtable` (`E/instrumenter/inject/ConcurrentHashMap.java:11`). Because it is loaded by the system loader
    and not instrumented, its operations cost 0. **[measured]** `put` and `get` = 0, against HashMap's ≈143/≈52.
  - `AtomicInteger`, `AtomicLong` and `AtomicReference` become engine stand-ins, which are also free.
  - `sun.misc.Unsafe` becomes `inject.Unsafe`.
- **Regex and `Math.random` are charged.** `String.matches`, `replaceAll`, `replaceFirst` and `split` are redirected
  to the instrumented `InstrumentableFunctions` (`InstrumentingMethodVisitor.java:461-464`), and so are
  `Math.random`/`StrictMath.random` (`:465-468`).
- `String(byte[])` and `getBytes()` are forced to UTF-16 (`:438-445`). `e.printStackTrace()` is redirected to the robot's
  `System.out` and costs 0 (`:477-480`).

## 4. Per-turn limit, overruns, `Clock`

- **Limits** (last constructor argument of `RobotType`, `E/common/RobotType.java:198-209`):

  | Robot | Limit | Source |
  | --- | --- | --- |
  | HEADQUARTERS | 20,000 | `RobotType.java:21` |
  | CARRIER | 12,500 | `RobotType.java:31` |
  | LAUNCHER | 10,000 | `RobotType.java:40` |
  | DESTABILIZER | 10,000 | `RobotType.java:49` |
  | BOOSTER | 10,000 | `RobotType.java:58` |
  | AMPLIFIER | 10,000 | `RobotType.java:66` |

  The limit is reset every turn (`E/world/InternalRobot.java:428`) and handed to the sandbox before each step
  (`E/world/control/PlayerControlProvider.java:175-176`).
- **Robots run strictly one at a time.** Each robot has its own thread, but the engine blocks until that thread pauses
  (`SandboxedRobotPlayer.java:286-313`, `Pauser` `:153-167`).
- **What happens on an overrun.** At each flush, `bytecodesLeft -= n + pendingArrayCost`. While `bytecodesLeft <= 0`, the
  robot calls `pause()` (`RobotMonitor.java:135-149`). On resume, `reactivate()` sets `bytecodesLeft += limit` if it was
  negative, or `bytecodesLeft = limit` otherwise (`RobotMonitor.java:297-308`). So:
  - **The turn resumes next round exactly where it stopped, in the middle of the code**, with all local state stale.
    **[measured]** A loop started in round 5 was resumed in round 6 and kept counting.
  - **The overshoot is debt taken from the next turn.** If the debt is larger than one turn's limit (a big array, a long
    `arraycopy`), the robot loses **whole extra turns**. **[measured]** An HQ with 19,818 bytecodes left ran
    `new int[50000]` in round 2. It lost round 3 completely, resumed in round 4 with 9,811 left, and the replay recorded
    bytecodes 50,185 / 30,185 / 10,240 for rounds 2, 3 and 4.
  - **Unused bytecodes are never carried forward** (`reactivate`, `RobotMonitor.java:303-307`).
- **`Clock.yield()`** = `RobotMonitor.pause()` (`E/common/Clock.java:24-26`). It costs 0 and flushes the pending block
  first (`MethodCosts.txt:1`). **If that flush itself drives the budget to ≤ 0, the robot pauses inside the flush. Next
  round it resumes, immediately executes the `yield`, and so loses that entire turn.** **[measured]** The HQ spun until 36
  bytecodes were left, ran a ~65-bytecode line, then called `Clock.yield()`. It started in round 9 and printed in round
  11, with round 10 recorded as a 29-bytecode turn. A control run with enough budget went from round 8 to round 9.
- **`Clock.getBytecodesLeft()`** returns the internal counter (`Clock.java:34-36`, `RobotMonitor.java:110-112`).
  **`Clock.getBytecodeNum()`** returns `limit - bytecodesLeft` (`RobotMonitor.java:102-104`). Both cost 0 and **do not
  flush**, so they lag the true value by the current block and by any pending array cost.
  **[measured]** Two reads on the same source line return equal values.
  After an overrun, `getBytecodeNum()` early in the next turn includes the carried debt. `getBytecodeNum()` can exceed the limit.
- **The replay records per-turn usage** as `limit - bytecodesLeft` at pause time (`PlayerControlProvider.java:181-191`,
  `E/world/GameWorld.java:217`, `InternalRobot.java:433`). A turn that overran or was skipped records a value ≥ the
  type's limit. **[measured]** Values seen: 20,029, 12,501, 50,185, 20,000.
- An idle robot running `while(true) Clock.yield();` uses 1 bytecode per turn (the `goto`). **[measured]**

## 5. Exceptions and robot death

- **The 500 penalty is charged when a handler is entered, not when the exception is thrown**
  (`InstrumentingMethodVisitor.java:623-627`). Each `catch` or `finally` handler on the unwinding path costs 500.
  **[measured]**
  - Throw and catch in the same method: 510 in total.
  - Throw in a callee, catch in the caller: 510.
  - Throw through a `finally` and then a `catch`: 1,017.
  - `rc.move` from an HQ, throwing `GameActionException` that is caught: 507.

  An exception that is never caught costs no penalty, but kills the robot (next item).
- **When `run()` ends, the robot is destroyed.** This applies whether `run()` returns, throws an uncaught exception, or
  the bot calls `System.exit` (which throws `RobotDeathException`, `E/instrumenter/inject/System.java:152-153`).
  1. The player thread ends and `terminated = true` (`SandboxedRobotPlayer.java:175-219`).
  2. `GameWorld.updateRobot` then calls `destroyRobot` at the end of that turn (`GameWorld.java:220-223`).
  3. The comment "they're not gonna lose the robot" at `SandboxedRobotPlayer.java:289` is wrong.

  This applies to **HQs** as well. **[measured]** All three carrier cases (return, uncaught `RuntimeException`,
  `System.exit`) left the robot count one lower the next round, and the replay lists them in `diedIDs`. A return from
  `run()` also prints "…froze in round N because it returned from its run() method!"
  (`SandboxedRobotPlayer.java:184-188`). No `DIE_EXCEPTION` action is recorded for these deaths; that action is used only
  when loading fails at spawn (`PlayerControlProvider.java:138-144`, `InternalRobot.java:473-476`).
- **`VirtualMachineError`s cannot be caught by bot code.** Every instrumented method that contains a try/catch gets an
  extra first handler that rethrows `VirtualMachineError` (`InstrumentingMethodVisitor.java:280-293`), and
  `RobotDeathException extends VirtualMachineError` (`E/instrumenter/RobotDeathException.java:10`). So a
  `StackOverflowError` or `OutOfMemoryError` bypasses `catch (Throwable)` and kills the robot. **[measured]** Deep
  recursion inside `try {…} catch (Throwable t)` never reached the catch, and the carrier died.
- **An instrumentation failure is fatal.** It is raised when the offending class is first loaded, for `RobotPlayer` at
  the robot's first turn. It kills that robot and sets `hasError` on the whole team's class factory, so every later class
  load for that team fails with "Team is known to have errors" (`TeamClassLoaderFactory.java:412-414`, `:445-462`).
  **[measured]** With `bcdead`, both HQs died in round 1. The match then ran to round 2000 with no robots on the map and
  was decided by coin flip. A team with zero robots does not lose early.
- Stack traces of uncaught robot exceptions are printed to the **engine's stderr** by `ErrorReporter`, whatever the
  output settings (`SandboxedRobotPlayer.java:191-195`, `E/server/ErrorReporter.java:33-44`).

## 6. Static initialisation and per-robot isolation

- **Each robot gets its own class loader** (`PlayerControlProvider.java:133` → `TeamClassLoaderFactory.java:159-161`,
  `:360-493`). Team classes, instrumented `java.util` copies, `RobotMonitor`, `inject.System`, `ObjectMethods`,
  `InstrumentableFunctions` and `Clock` are all defined separately per robot
  (`alwaysRedefine`, `TeamClassLoaderFactory.java:82-88`). So **static fields are per robot**. All robots share one JVM;
  they are not separate JVMs.
- **Static initialisers are charged to the robot that triggers them, on the turn they run.**
  - `RobotPlayer`'s `<clinit>` runs inside the robot's first turn, before `run()` (`SandboxedRobotPlayer.java:236-246`).
  - A helper class's `<clinit>` runs, and is charged, when the class is first touched.
  - **[measured]** `static int[] BIG = new int[3000]` cost 3,003 at entry for every robot, HQ and each carrier alike.
    A lazily touched class holding `static int[2000]` cost 2,006 on first touch and 3 afterwards.
- Implication: a large static lookup table is paid again by **every** newly built robot. An `int[]` literal costs about
  5 bytecodes per element: `newarray` length + `dup` + index push + value push + `iastore`, derived from section 1. A
  `String` constant costs 1 to load (`ldc`) and 0 per `charAt`. UNVERIFIED by measurement; follows from the counted rules.

## 7. Memory

- **The engine enforces no per-robot memory limit.** I found no heap accounting anywhere in `E/` (grep for
  memory/heap/Xmx/OutOfMemory finds nothing). All robots share the engine JVM's `-Xmx`.
  - Only allocation **cost** is limited: arrays cost one bytecode per element (section 1).
  - `new` of an object costs 1 regardless of its size.
  - `StringBuilder.append` costs 1 regardless of length.
- An `OutOfMemoryError` raised in bot code cannot be caught (section 5). Whether it would hit another robot's thread or
  the engine instead is UNVERIFIED.
- The spec's "8 Mb heap" rule is not implemented in the engine. Whether tournament infrastructure enforces it is
  UNVERIFIED.

## 8. `System`, output, indicator strings, replay contents

- **`System` is replaced** by `inject.System`, defined per robot:
  - `out` and `err` are the same robot stream (`E/instrumenter/inject/System.java:37,42`).
  - `in` returns EOF.
  - `setIn`, `setOut` and `setErr` throw (`:102-112`).
  - `console()` and `inheritedChannel()` return null.
  - `lineSeparator()` returns `"\n"`.
  - `arraycopy` costs `length` (`:126-130`). **[measured]**
  - `identityHashCode` uses the deterministic per-robot counter (`:132`).
  - `getProperty` and `setProperty` work on a per-robot `Properties`. It holds fake `java.*`/`os.*`/`user.*` values set to
    `"who knows?"` (`:55-69`) plus **copies of every config key that starts with `bc.testing`** (`:73-78`).
  - `exit()` throws `RobotDeathException`, so the robot dies (`:152-153`).
  - **[measured]** `-Dbc.testing.foo=bar` is readable as `System.getProperty("bc.testing.foo")`, and
    `java.version` reads `"who knows?"`.
- **Printing costs no bytecodes beyond building its arguments.** `PrintStream` is uninstrumented `java/io`.
  **[measured]** `System.out.println(constant)` = 2 (`getstatic` + `ldc`). String concatenation costs `new` + `dup` + 1 per
  `append` + 1 for `toString()`.
- **Where output goes.** Each line is prefixed `[A:CARRIER#10869@3] ` (`E/instrumenter/stream/RoboPrintStream.java:246-250`).
  - It is copied to the engine's stdout only if `bc.server.robot-player-to-system-out` is true (default `true`,
    `E/server/Config.java:38`; `RoboPrintStream.java:89-93`).
  - It is fully suppressed for a team when `bc.engine.silence-a` / `-b` is set (`SandboxedRobotPlayer.java:396-404`).
- **Robot output is not stored in the replay.** The per-match log buffer is flushed and reset every round, with the line
  that would save it commented out: `// byte[] logs = this.logger.toByteArray(); this.logger.reset();`
  (`E/server/GameMaker.java:509-514`). The schema's `Round` table has no logs field ("logs have been replaced with
  indicator strings", `schema/battlecode.fbs:320`).
  - Consequently `bc.server.robot-player-replay-file-per-team-limit-bytes` (default −1, `Config.java:43`) only limits the
    discarded buffer (`E/instrumenter/stream/LimitedPrintStream.java`). It never limits stdout.
- **Indicator strings are what reaches the replay.**
  - `setIndicatorString`, `setIndicatorDot` and `setIndicatorLine` cost 0 (`MethodCosts.txt:95-97`).
  - Strings are truncated to `INDICATOR_STRING_MAX_LENGTH` = 64 (`E/world/RobotControllerImpl.java:1180-1185`,
    `GameConstants.java:60`).
  - Only the last string set in a turn is kept (reset each round, `InternalRobot.java:421-423`, recorded at end of turn
    `:435`).
  - All indicators are dropped from the replay if `bc.engine.show-indicators=false` (`GameMaker.java:670-698`).
- **The replay header reports spec version `3.0.14`** (`GameConstants.SPEC_VERSION`, `GameConstants.java:13`; written at
  `GameMaker.java:242`), even though the jar is 3.0.15. **[measured]** In the dumped replay.

## 9. Seeds, robot IDs, randomness, determinism

- **The official engine has no seed property.** The only seed is the map file's `randomSeed` field
  (`E/world/GameMapIO.java:227` → `LiveMap.getSeed()`, `E/world/LiveMap.java:307-308`).
  - `GameConstants.GAME_DEFAULT_SEED = 6370` (`GameConstants.java:167`) is not used anywhere in the engine.
  - Official map seeds range from 5 to 988 (all 103 built-in maps dumped).
  - This project's `-Dbc.game.seed` comes from its own patched `LiveMap.class` (`engine/patch-src/battlecode/world/LiveMap.java:308`,
    `tools/get-engine.sh`), not from the official engine.
- **Robot IDs**:
  - **HQ IDs come from the map file** (`GameMapIO.java:343`, `GameWorld.java:84-90`). In the 103 official maps they
    are small integers from 2 to 19, and the initial bodies are sorted by ID (`LiveMap.java:105`).
  - **Every spawned robot** gets the next ID from `IDGenerator(mapSeed)` (`GameWorld.java:63`, `:806-809`). IDs are
    handed out in blocks of 4,096 consecutive integers starting at 10,001, each block Fisher–Yates shuffled with
    `java.util.Random(mapSeed)` (`E/world/IDGenerator.java:16-21`, `:48-53`, `:73-94`).
  - So the first 4,096 spawned robots have IDs in [10001, 14096], which fit in 14 bits. **[measured]** 10869, 13497,
    11039, 14071 on `maptestsmall`.
- **Bot-side randomness is seeded with the robot's ID** (`PlayerControlProvider.java:129-136` passes `robot.getID()` as the
  seed; `RobotMonitor.java:51-64`, `:249-251`).
  - `new Random()` is rewritten to `new Random(robotID)` (`InstrumentingMethodVisitor.java:430-436`).
  - `Math.random()` draws from a lazily created per-robot `Random(robotID)` (`E/instrumenter/inject/InstrumentableFunctions.java:17-25`).
  - **[measured]** HQ #3: `new Random().nextInt()` equals `new Random(3).nextInt()`, and `Math.random()` equals
    `new Random(3).nextDouble()`.
  - Consequence: on a given map, every robot's random stream is fixed, and an HQ's stream is the same on any map where it
    has the same map-file ID.
- **Identity hash codes are deterministic.** `Object.hashCode()`/`System.identityHashCode` return a per-robot counter
  0, 1, 2, … (`E/instrumenter/inject/ObjectMethods.java:34`, `:78-85`). **[measured]** The first two `new Object()`
  hashes were 0 and 1. So iteration order of `HashMap`/`HashSet` with identity-hashed keys is reproducible.
  - Exception: `ConcurrentHashMap` is the uninstrumented `Hashtable`, which calls the real native `hashCode` on keys that
    do not override it, so its order is UNVERIFIED and probably non-deterministic.
- **The engine's own randomness**:
  - `GameWorld.rand` (`GameWorld.java:52,78`) and the static `RobotControllerImpl.random` (`RobotControllerImpl.java:37,49`)
    are seeded from the map but **never used**.
  - The **final tiebreak** ("a uniformly random team") is `Math.random() < 0.5`, in uninstrumented engine code, **unseeded**
    (`GameWorld.java:626-628`, reached from `checkEndOfMatch` `:637-648`).
  - **[measured]** 7 identical dead-vs-dead games gave A, B, B, A, A, A, B.
- **Is a game deterministic?** It is, given the same map file, the same class files for each side, the same side
  assignment, the same config (notably `bc.engine.debug-methods`, which changes counting, and any `bc.testing.*` values the
  bots read), and the same JDK class library (it sets the cost of `java.util`), **with two exceptions**:
  1. the final coin flip;
  2. JVM-dependent errors. **[measured]** `StackOverflowError` depth varies between runs (the same game killed the
     recursing carrier in round 10 in one run and round 9 in the other).

  Two identical probe runs produced replays identical in every round not touched by the stack overflow.
  `bc.engine.enable-profiler` does not change counts: its hooks are inserted after counting
  (`InstrumentingMethodVisitor.java:159-162`, `:218-232`); this is code-verified only.

## 10. Server and config properties (headless runner)

Config sources, in order (`E/server/Config.java:105-172`):

1. Built-in defaults (`:31-72`).
2. Every JVM system property starting with `bc.` or `drw.` (`:110-120`).
3. A config file, which **overrides** the `-D` values: `-c <file>`, or **`bc.conf` in the working directory if `-c` is
   absent** (`:145-162`). `-c=-` loads no file (as the official gradle task and `tools/lib.sh:60` do).
4. `-h` sets `bc.server.mode=headless`, `-s` sets it to `tcp`, and `-n` sets `bc.dialog.skip` (`:164-171`).

`getInt` defaults to 0 and `getBoolean` to false for missing keys (`:201-210`).

| Key | Default | Effect (provenance) |
| --- | --- | --- |
| `bc.server.mode` | unset → headless | Only `HEADLESS` runs; any other value prints "invalid bc.server.mode" and exits 64 (`Main.java:97-123`). |
| `bc.game.team-a` / `-b` | `team000` | Team names; required (`Main.java:14-18`, `:33-37`). |
| `bc.game.team-a.url` / `-b.url` | none | **Required**: a directory or jar of class files. Every class in it is a team class (`Main.java:19-25`, `:38-44`; `TeamClassLoaderFactory.java:125-153`). |
| `bc.game.team-a.package` / `-b.package` | = team name | Package whose `RobotPlayer` is loaded (`Main.java:26-31`, `:45-50`). |
| `bc.game.maps` | `glass` | Comma-separated; one match per map, all in one replay (`Main.java:52-57`; `Server.java:177-206`). |
| `bc.game.map-path` | `maps` | Directory searched first, then the maps built into the jar (`Server.java:457`; `GameMapIO.java:51-63`). The official gradle task passes `bc.server.map-path`, which nothing reads. |
| `bc.game.best-of-three` | false | Stop after 2 wins, only if exactly 3 maps (`Main.java:72`, `Server.java:201-205`). |
| `bc.server.save-file` | `match.rms` | Replay path, gzip flatbuffer (`Main.java:59-65`, `Server.java:209`). |
| `bc.server.alternate-order` | false | Swap the sides' HQ ownership on every other map (`Server.java:170`, `:181`; `GameMapIO.java:347-349`). The overall winner is `aWins >= bWins ? A : B`, so **ties go to A** (`Server.java:207`). |
| `bc.server.validate-maps` | true | Map-guarantee checks before each match (`Server.java:169`, `:466-469`). |
| `bc.server.websocket` | **true** | Starts a websocket server on `bc.server.port` (6175) that **keeps every event in memory** for late clients (`Server.java:131-137`; `NetServer.java:132-139`). **[measured]** If the port is taken, a `NullPointerException` hits the websocket thread but the match still runs and writes its replay. A headless runner should pass `-Dbc.server.websocket=false`. |
| `bc.server.port`, `bc.server.wait-for-client` | 6175, false | Websocket only; wait-for-client blocks until a client connects (`NetServer.java:68-87`). |
| `bc.server.robot-player-to-system-out` | true | Copy robot prints to stdout (section 8). |
| `bc.server.robot-player-replay-file-per-team-limit-bytes` | −1 | Limits only the discarded log buffer, so it has no visible effect (section 8). |
| `bc.server.debug` | false | `[server:debug]` messages (`Server.java:682-686`). |
| `bc.engine.silence-a` / `-b` | false | Discard that team's prints (`SandboxedRobotPlayer.java:396-404`). |
| `bc.engine.debug-methods` | false | `debug_*` handling, section 1 item 10 (`TeamClassLoaderFactory.java:457`). |
| `bc.engine.enable-profiler` | false | Per-method bytecode profiles, written to the match footer (`Server.java:166`; `GameWorld.java:154-161`). |
| `bc.engine.show-indicators` | true | Include indicator strings, dots and lines in the replay (`Server.java:160`; `GameMaker.java:670-698`). |
| `bc.testing.*` | none | Visible to bots through `System.getProperty` (section 8). |

No code reads `bc.game.state`, `bc.server.throttle*`, `bc.server.transcribe-*`, `bc.server.output-xml`,
`bc.engine.silence-c/-d`, `match.zombie-armageddon` or `bc.dialog.skip` (they appear only in `Config.java`; grep of `E/`).
There is no `bc.game.seed`, round-limit or bytecode-limit property in the official engine. The round limit is
hard-wired to `GAME_MAX_NUMBER_OF_ROUNDS = 2000` (`GameMapIO.java:228`, `GameConstants.java:170`).

---

## Spec disagreements

Spec = `reference/battlecode23/specs/specs.md.html`; the engine is authoritative.

1. **"Unhandled exceptions may paralyze your robot"** (spec l.249). The engine **destroys** the robot (HQs included) at
   the end of the turn in which `run()` ends for any reason (`GameWorld.java:220-223`). **[measured]**
2. **"Throwing any Exceptions cause a bytecode penalty of 500"** (spec l.249). The penalty is per handler entered: it is
   charged on catch or finally, not on throw (`InstrumentingMethodVisitor.java:623-627`). Through a `finally` the cost is
   1,000. An uncaught throw costs no penalty but kills the robot. **[measured]**
3. **"…they are run in separate JVMs"** (spec l.96). All robots share one JVM, each with its own class loader
   (`TeamClassLoaderFactory.java:360-493`). The conclusion (no shared statics) holds.
4. **"…resumed at exactly that point next turn"** (spec l.218). The robot pauses only at a basic-block boundary, after
   the limit is crossed, and the overshoot is repaid out of later turns. A debt larger than one limit skips whole turns, and
   an overrun just before `Clock.yield()` loses the next turn entirely (`RobotMonitor.java:126-153`, `:297-308`). **[measured]**
5. **"re-running the same match between the same bots produces exactly the same results"** (spec l.216). This is false
   in two cases: the final coin flip is unseeded `Math.random()` (`GameWorld.java:627`), and `StackOverflowError` depth
   varies between runs. **[measured]**
6. **"If a robot uses more than 8 Mb of heap space … the robot may explode"** (spec l.269). The engine has no memory
   enforcement at all. UNVERIFIED whether tournament infrastructure adds one.
7. **"Class.forName … not allowed"** (spec l.263). Understated: **every** `java.lang.Class` method except
   `desiredAssertionStatus` is banned, for example `getClass().getName()` (`InstrumentingMethodVisitor.java:542-548`).
   Also banned and not mentioned in the spec: `synchronized`, any `java/lang/invoke` call, `System.currentTimeMillis`,
   `nanoTime` and the rest of section 3's list, and method references to charged methods. **[measured]** for `Class`.
8. **"java.lang.System only supports out, arraycopy, and getProperty … only … names beginning with bc.testing."**
   (spec l.263). The engine also provides `err`, `in`, `identityHashCode`, `lineSeparator`, `setProperty`,
   `clearProperty` and `exit` (which kills the robot). `getProperty` also returns fake `java.*`/`os.*` values
   (`"who knows?"`) (`inject/System.java:55-153`).
9. **"Classes in java.util … are bytecode counted as if they were your own code"** (spec l.273).
   `java.util.concurrent.ConcurrentHashMap` and `AtomicInteger`/`AtomicLong`/`AtomicReference` are swapped for **uncounted**
   engine classes (`ClassReferenceUtil.java:163-170`). **[measured]** `ConcurrentHashMap.put`/`get` = 0.
10. **"these instructions have a bytecode cost equal to the total length of the instantiated array"** (spec l.286).
    Zero-length arrays cost 1, and each multi-array dimension counts as at least 1 (`RobotMonitor.java:192-215`).
    **[measured]** `new int[0]` = 1. Minor.
11. **"Methods not listed are free" / the costs in MethodCosts.txt** (spec l.282). `MapLocation.hashCode`, `MapLocation.toString`
    and `MapInfo.toString` are listed at 2, 2 and 15 but cost 1, because every `hashCode()`/`toString()` call is rewritten
    first (`InstrumentingMethodVisitor.java:407-428`). **[measured]** for `hashCode`. Minor.
12. **"read from the shared array … for standard Java bytecode costs"** (spec l.184). `readSharedArray` has a fixed cost of
    2 (`MethodCosts.txt:74`). **[measured]** Minor or ambiguous wording.
13. **`Clock.getBytecodeNum()` = "how many bytecodes have been executed during the current round"** (spec l.243).
    It is `limit - bytecodesLeft`: it includes debt carried from an overrun and excludes the current unflushed basic block
    (`RobotMonitor.java:102-104`). **[measured]** Minor.
14. The official `build.gradle:58` headless task passes `-Dbc.server.map-path=maps`, a key the engine never reads; the
    engine reads `bc.game.map-path` (`Server.java:457`). This is a tooling disagreement, not a spec one.

No disagreement: the per-type bytecode limits (spec l.204/220-225), `writeSharedArray` at 75, `System.arraycopy` costing 1
per element, the `Clock.yield()` semantics in the normal case, and "unique random IDs no smaller than 10,000, except for
your headquarters" (spec l.94; IDs start at 10,001).

## Surprises: mechanics a bot designer could easily get wrong

1. **Running out of bytecodes right before `Clock.yield()` costs a whole extra turn.** The flush before the yield pauses
   the robot; next round it wakes up and yields at once. Keep a safety margin, and do not spin until
   `getBytecodesLeft()` is almost 0. **[measured]**
2. **An overrun resumes mid-code next round with stale state.** A check-then-act split across the boundary (for example
   `canAttack`, then the flush before `attack`) can act on a world that has changed. If the act then throws uncaught, the
   robot dies. Every `RobotController` call ends a basic block, so each one is a possible pause point.
3. **Big allocations freeze robots for several turns.** Each element costs 1 bytecode and the debt carries over, so
   `new int[50000]` on an HQ loses a full turn **[measured]**, and on a launcher about 5 turns (derived). Allocate large
   arrays once, never per turn.
4. **Static initialisers are paid by every robot**, on its first turn (or on first touch of the class). A 3,000-element
   static array costs every new carrier 3,003 of its 12,500 first-turn budget. **[measured]**
5. **An uncaught exception, returning from `run()`, or `System.exit` destroys the robot, including HQs.** Wrap the whole
   turn in `try/catch (Exception)` inside the loop. Note that `StackOverflowError`/`OutOfMemoryError` cannot be caught at
   all. **[measured]**
6. **A single illegal API use anywhere in the team's code kills robots at class-load time and poisons the whole team**
   ("Team is known to have errors"). Examples are `getClass().getName()`, `synchronized`, `System.nanoTime`, and
   `MapLocation::distanceSquaredTo` as a method reference. It compiles fine. **[measured]**: both HQs died in round 1.
   The game still runs to round 2000, so a broken build can look like a long, quiet game.
7. **Each exception handler entered costs 500, and `finally` counts as one.** A `canX` check (5-10) is far cheaper than
   a caught `GameActionException` (≈507). **[measured]**
8. **`java.util` is charged as user code and is expensive.** `HashMap.put` ≈143 and `get` ≈52 **[measured]**, against
   an array access of ≈3. In contrast, `String` methods (`charAt` 0, `indexOf` 1), array `clone()` (0), `Math.*` (1) and
   all `java.lang` boxing and parsing are nearly free. `ConcurrentHashMap` is free **[measured]**, but its iteration order
   may be non-deterministic for identity-hashed keys (UNVERIFIED).
9. **Method calls are free.** Only the argument pushes and the callee body are charged **[measured]**, so manual
   inlining saves only those pushes and the callee's load/return instructions.
10. **`Clock.getBytecodesLeft()`/`getBytecodeNum()` do not flush.** They lag by the current block and any pending array
    cost. Within one line, two reads are identical. **[measured]**
11. **`System.out` output is not in the replay.** It appears only on stdout, and only with
    `bc.server.robot-player-to-system-out=true`. For anything that must be visible in a replay, use
    `setIndicatorString` (free, ≤ 64 chars, last one per turn) or indicator dots and lines.
12. **`debug_*` methods are removed when debug methods are disabled, but their argument expressions still run and are
    charged.** When debug methods are enabled, the bodies are free, which changes behaviour between debug and normal runs.
13. **Randomness is fixed per robot ID.** `new Random()` and `Math.random()` are seeded with the robot ID; HQ IDs (2-19)
    come from the map file and other IDs from the map seed. The same game on the same map replays identically: you get
    no variety from re-running, and HQs with equal IDs on different maps draw the same numbers. **[measured]**
14. **This project's seed patch does less than its comment claims.** `tools/get-engine.sh:6-7` says robot IDs, "every
    sandboxed Random and the final coin flip derive from the map seed". In the engine, HQ IDs and therefore HQ randomness
    come from the map file, unaffected by the seed; the coin flip is unseeded `Math.random()`, unaffected and
    non-reproducible. **[measured]** With `-Dbc.game.seed=12345`, HQ IDs (2, 3) and their `Random` outputs were identical
    to the unpatched run, carrier IDs changed (10247, 11850, …), and the replay's map seed became 12345. The patch only
    changes spawned robots' IDs, and through those, their random streams.
15. **A `bc.conf` in the engine's working directory silently overrides `-D` flags** unless `-c=-` (or `-c <file>`) is
    given (`Config.java:145-162`). `tools/lib.sh:60` already passes `-c=-`.
16. **`bc.server.websocket` defaults to true.** Every headless game binds port 6175 and buffers all events in memory. Pass
    `-Dbc.server.websocket=false` for batch runs (`tools/lib.sh` does not). **[measured]** A port conflict is
    non-fatal. Separately, `bc.server.robot-player-replay-file-per-team-limit-bytes`, which `tools/lib.sh:54` sets to
    4,000,000, does nothing visible.
17. **Replay `bytecodesUsed` ≥ the type's limit marks an overrun or a skipped turn.** This is a reliable signal for an
    overrun auditor reading replays. **[measured]**
18. **The replay header says spec `3.0.14` even with the 3.0.15 jar** (`GameConstants.java:13`). Do not version-match on it.
19. **The cost of `java.util` depends on the JDK that runs the engine.** It instruments the JDK's own `rt.jar` classes at
    runtime. Benchmark on the same JDK build used for evaluation. The tournament JDK version is UNVERIFIED. ASM in the jar
    dates from 2015 (5.x), so a Java 9+ runtime would probably fail to instrument `java.util` (UNVERIFIED).

---

## Appendix: empirical runs (session scratchpad, all with `JAR` and JDK 8u504)

Common settings: map `maptestsmall` (seed 919, HQs B#2 and A#3), `-Dbc.server.websocket=false` unless noted,
`-Dbc.testing.foo=bar`.

- `run0`: `bcprobe` with an illegal `getClass().getName()` in one method. Instrumentation failure at the first turn
  killed both HQs; the game went to round 2000 and was decided by coin flip.
- `run2`, `run3`: two identical `bcprobe` games.
  - The cost measurements in sections 1-4 and 8 come from these runs.
  - The replays were identical except rounds 9-10 (SOE-dying carrier: died in R10 in run2, in R9 in run3). Robot
    stack-trace interleaving on stderr also differed.
- `dead1-6`: `bcdead` vs `bcdead`, identical. Winners B, B, A, A, A, B (coin flip; plus `run0`: A).
- `seed1`: `bcprobe` with the project patch on the classpath and `-Dbc.game.seed=12345`. HQ IDs and HQ random values were
  unchanged; carrier IDs changed.
- `ws`: `bcprobe` with websocket on and port 6175 already bound. NPE in `WebsocketSelector`; the match completed and the
  replay was written.
