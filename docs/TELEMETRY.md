# TELEMETRY.md: getting the most information from every game

Design v1, 2026-10-08. Origin: owner prompts 11 and 13. Ladder play goes through our private galaxy replica, which
gives our team about 50 games an hour, so every replay has to count. This document is the contract for three parts
built in parallel on disjoint files:

- **A**: bot telemetry in `src/bot`
- **B**: extraction in `tools/replaydump/ReplayDump.java`
- **C**: match reports in Python

§1 is the single source of truth for everything two parts share. When this document and a survey disagree, this
document wins. When this document and the engine disagree, the engine wins: fix the document, and note the change in
§9.

---

## 0. What reaches a replay

The replica runs every match with `-Dbc.engine.show-indicators=false` (`tools/replica/worker.py` `match_command`, the
same as the real galaxy). With that flag set, the engine drops every indicator string, dot and line before writing the
replay.

Two kinds of data survive:

- the public game state: spawns, actions, positions, deaths, HP and inventory deltas, team totals and island owners;
- every robot's per-turn `bytecodesUsed`.

Facts measured by the 2026-10-08 probe on engine 3.0.15:

- **Outcomes:** indicators on or off give identical game states (the state hash matched over 400 rounds).
- **Dots and lines:**
  - The calls cost 0 bytecodes. Only argument pushes count: a dot is about 8 to 13 bytecodes in total.
  - There is no count cap. All five ints (x, y, r, g, b) are stored exactly.
  - Dots are recorded in the round the call runs.
- **Strings:**
  - Strings are cut to 64 UTF-16 units. Only the last string of the turn is kept.
  - A lone surrogate crashes the engine, and no game in the match is saved.
- **`bytecodesUsed`:** this is `limit - bytecodesLeft` at the pause. A value of at least the limit means an overrun.

So information leaves the bot through three channels. Replay-only extractors cover both teams on top of them:

| Channel | Carries | Reaches replica replays as configured | Cost to the bot |
|---|---|---|---|
| **BCC**, the bytecode channel (A.3) | One 6-bit state code per robot-turn | **Yes** | About 48 bytecodes per turn on average |
| **Indicator string v2** (A.5) | Human-readable state, the same 6-bit code, and the health counters | Only for local games of our own builds (shadow re-runs, C.7, are not used: rule 10) | About 60 per turn, as today |
| **Data dots** (A.6) | Events, fight turns, periodic counters, HQ and comms snapshots | Same as strings | About 10 to 40 per record |
| **Replay extractors** (B) | Engagements, death causes, timelines, HQ pressure and the rest, for both teams | **Yes** | 0 |

Design rule: the bot cannot tell whether indicators are on. **Telemetry always runs the same code**, so a replica game
and its shadow re-run consume identical bytecodes and play identically.

---

## 1. Shared constants and encodings (A, B and C all depend on these)

| Name | Value | Meaning |
|---|---|---|
| `MAGIC` | `0x7E1E0001` (2115895297) | HDR record word a: magic `0x7E1E` plus `VERSION` 1 |
| `DOT_X(kind)` | `-2 - kind` | A data dot is `rc.setIndicatorDot(new MapLocation(-2 - kind, a), b, c, d)`. In the replay, x = −2 − kind, y = a, red = b, green = c, blue = d. Dots with x ≥ 0 are not telemetry. |
| `loc12(l)` | `G.enc(l)` = `x*64 + y + 1`; 0 = none/null | 12-bit location. Decode: `x = (v-1)/64`, `y = (v-1)%64`. |
| type numbers | 0 HQ, 1 CARRIER, 2 LAUNCHER, 3 AMPLIFIER, 4 DESTABILIZER, 5 BOOSTER | The replay schema's body-type order, not `RobotType.ordinal()`. Letters H C L A D B. |
| `ALPHA` | `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_` | Code `c` (0..63) is the character `ALPHA[c]` |
| `SYNC_CODE` | 42 (`ALPHA[42]` = `g`) | BCC sync code |
| sync rounds | `round % 50 == 25` | Every telemetry robot pads to `SYNC_CODE` on these rounds |
| `BCC_GUARD` | 300 | The pad runs only if `Clock.getBytecodesLeft() >= 300`. The decoder trusts a turn only if `used <= limit - 300`. |
| limits | HQ 20000, C 12500, L/A/D/B 10000 | Prefer `bodyTypeMetadata.bytecodeLimit` from the replay header |
| `sat(v, w)` | clamp to `[0, 2^w - 1]` | Every packed field is saturated, unless marked *signed* |
| `f@k:w` | field f at bit offset k, width w | Unsigned. Decoders must use `(v >>> k) & mask` on the 32-bit int. |
| unit value | C 50, L 45, A 45, D 200, B 150 | Resource cost, used by every value statistic |

### 1.1 BCC code tables

Each type has 64 codes. The **letter** of a code is the first character of the indicator string. Codes listed as
invalid never occur, and a decoder that sees one counts it as a decode error.

**CARRIER**: `code = state << 1 | (role == 2 ? 1 : 0)`. The role is 1 for Ad and 2 for Mn. States 0..15 are listed
below. Codes 32..63 are invalid.

| state | letter | meaning this turn |
|---|---|---|
| 0 | `!` | Exception, or the turn ended before a state was set |
| 1 | `G` | Going to a well |
| 2 | `C` | Collected at the well |
| 3 | `W` | Waiting near a crowded well |
| 4 | `S` | Switched well (crowd patience ran out this turn) |
| 5 | `X` | Exploring: no well known |
| 6 | `R` | Returning loaded |
| 7 | `D` | Deposited this turn |
| 8 | `F` | Fleeing armed enemies |
| 9 | `V` | Threw its load this turn (cornered) |
| 10 | `T` | Took an anchor at an HQ this turn |
| 11 | `K` | Carrying an anchor to a known island |
| 12 | `Q` | Carrying an anchor to a predicted island (a mirror image) |
| 13 | `E` | Carrying an anchor with no target (exploring) |
| 14 | `Y` | Carrying an anchor home after the timeout |
| 15 | `P` | Placed an anchor this turn |

**LAUNCHER**: `code = mode | objKind << 3 | outnumbered << 5`. All 64 codes are valid.

- `mode`:

  | value | letter | meaning |
  |---|---|---|
  | 0 | `N` | Nothing to do: movement not ready and no hittable enemy |
  | 1 | `F` | Fight: movement ready and an enemy is hittable (`fight()` scored the tiles) |
  | 2 | `H` | Hold: an enemy is hittable, movement not ready (shoots only) |
  | 3 | `M` | March toward the objective |
  | 4 | `S` | Stand: no objective, on the target island, or holding short of enemy HQ fire |
  | 5 | `G` | Regroup (`C.ARMY`) |
  | 6 | `W` | Follow the leader (`C.ARMY`) |
  | 7 | `!` | Exception or unset |

- `objKind` is the last objective chosen by `pickObjective`, kept through fight turns. It starts at 3:

  | value | objective |
  |---|---|
  | 0 | Enemy sighting from comms |
  | 1 | Enemy-held island |
  | 2 | Predicted enemy HQ |
  | 3 | Map centre, or none |

- `outnumbered` = `G.nEnemyFighters > G.nAllyFighters + 1`.

**HQ**: `code = reason | threatened << 4 | wantAnchor << 5`. Reasons 10 to 14 are invalid.

- `reason` (letter, then meaning):

  | value | letter | meaning |
  |---|---|---|
  | 0 | `.` | Spent: the build loop ran until the HQ was not action-ready |
  | 1 | `b` | Bytecode guard |
  | 2 | `g` | Six-iteration guard |
  | 3 | `p` | Poor: nothing affordable |
  | 4 | `w` | Batch wait: a launcher is affordable but `batchOK` is false |
  | 5 | `c` | Carrier cap: Ad for a carrier, but `carrierRoom()` is false |
  | 6 | `a` | Anchor reserve: the reserve made the next unit unaffordable |
  | 7 | `s` | No free spawn tile for an affordable unit |
  | 8 | `t` | Threatened: a carrier or amplifier is affordable but withheld under threat |
  | 9 | `x` | Other |
  | 15 | `!` | Exception or unset |

- `threatened` = `G.nEnemyFighters > 0`.
- `wantAnchor` is the last iteration's `wantAnchor`.

**AMPLIFIER**: `code = mode | min(n, 14) << 2`. Code 63 = `!` (exception or unset).

- `mode`: 0 `F` backs away from a fighter; 1 `C` goes to the centroid of visible launchers; 2 `S` goes toward the
  point between home and a sighting; 3 `H` goes home, or has nothing to do.
- `n` = own launchers in vision.

**DESTABILIZER, BOOSTER**: code 0 = `O` (normal), 1 = `!`, and the rest are invalid.

---

## 2. Part A: bot telemetry (`src/bot`)

### A.1 Files and switches

- **New file `src/bot/Telemetry.java`.** All encoding and emission lives here. It holds only statics: no per-turn
  allocation, no `G.rand()` calls, no shared-array writes, and no writes to any field that decision code reads.
- **`C.java` additions:**
  ```java
  /** Telemetry (docs/TELEMETRY.md): data dots and the bytecode channel. The v2 indicator string is always on. */
  public static final boolean TELEMETRY = true;
  /** Bytecode-channel constant, calibrated per A.3; recalibrate whenever Telemetry.pad() or its call site changes. */
  public static final int PADK = 0;        // set by calibration
  /** Free 16-bit build tag reported in HDR (0 = working line). */
  public static final int TELE_BUILD = 0;
  ```
  `TELEMETRY = false` removes the dots and the BCC pad, and nothing else. Guard hook call sites with
  `if (C.TELEMETRY)` so that javac drops them.
- **Hooks are added to:**
  - `RobotPlayer.java`
  - `Carrier.java`, `Launcher.java`, `HQ.java`, `Amplifier.java`, `Other.java`
  - `Nav.java` (BUG)
  - `MapMem.java` (SYM, plus the `maxPending` and `maxUnreported` trackers)
  - `Comms.java` (`writes`, `refusedWrites`, and `lastAge` from `nearestEnemy`)

  Every hook is one call or a few static stores. Hooks never change control flow.
- **Tests go in `test/bot/BotTest.java`.** A owns that file.

Suggested API (signatures are A's choice; the behaviour is fixed by this section):
```java
public final class Telemetry {
  public static int code, phase, t1;                 // this turn's 6-bit code; phase 1..5; bytecodes after shared start
  static void startTurn(int r0);                     // phase=1, code=EXC code of the type, HDR on the first turn
  static void exc(int site, Exception e, int r0);    // EXC record + code = EXC code of the type
  static void nearMiss(int work, int r0);            // NM record
  static void endTurn(int r0);                       // phase=3: trip state counts; due CNT/CNTT/CNTM, HQS, COMMS
  static void overrun(int r0, int work);             // OVR record
  static void indicator();                           // builds and sets the v2 string (phase=5)
  static void pad();                                 // BCC; the LAST call before Clock.yield()
  static int carrierCode(int state, int role); static int launcherCode(int mode, int obj, boolean out);
  static int hqCode(int reason, boolean threat, boolean wantAnchor); static int ampCode(int mode, int n);
  static void dot(int kind, int a, int b, int c, int d);   // G.rc == null (BotTest) -> TEST_SINK
  static int loc12(MapLocation l); static int sat(int v, int bits);
  // one packer per record kind, e.g. static int[] packTrip(...) or packTripA(...)..D(...), pure and unit-tested
}
```

### A.2 Turn loop (exact order in `RobotPlayer.run`)

```java
while (true) {
    int r0 = rc.getRoundNum();
    Telemetry.startTurn(r0);                                   // phase 1; HDR on the first turn; cannot throw
    try {
        G.startTurn(); Comms.startTurn(); HQState.refresh();
        Telemetry.t1 = Clock.getBytecodeNum(); Telemetry.phase = 2;
        switch (G.type) { ... }                                // unit code sets Telemetry.code at every exit
    } catch (GameActionException e) { G.exceptions++; Telemetry.exc(1, e, r0); ... }
      catch (Exception e)           { G.exceptions++; Telemetry.exc(2, e, r0); ... }
    int work = Clock.getBytecodeNum();
    if (rc.getRoundNum() == r0) { /* maxBc, near miss as today */ ...; if (near) Telemetry.nearMiss(work, r0); }
    Telemetry.endTurn(r0);                                     // phase 3, guarded, try/catch inside (A.8)
    try { if (rc.getRoundNum() == r0) { Telemetry.phase = 4; /* fill + flushIslands as today */ } }
    catch (Exception e) { G.exceptions++; Telemetry.exc(3, e, r0); ... }
    if (rc.getRoundNum() != r0) { G.overruns++; Telemetry.overrun(r0, work); }
    Telemetry.indicator();                                     // replaces the inline setIndicatorString
    Telemetry.pad();                                           // must be the last statement before yield
    Clock.yield();
}
```

The reasons for this order:

- The near-miss measure (`work`) still excludes telemetry's end-of-turn records and the fill. So the bot's `nm`
  counter keeps its meaning.
- Records are written before the fill, and the fill still stops at a 12% reserve. A filled turn therefore still ends
  near 88% of the limit, plus the string and the pad (at most about 1.5%). Replay-side near misses (at least 90%)
  keep their meaning.
- The pad comes after everything else, so its constant overhead is fixed.
- `Clock.yield()` must stay the only yield in the bot (it is today: `RobotPlayer.java:61`).

### A.3 BCC: the bytecode channel

**`pad()`** follows the probe's verified implementation, in
`scratchpad/telemetry-probe/src/telemetryprobe/RobotPlayer.java` `pad()`:

```java
static void pad() {
    if (!C.TELEMETRY || Clock.getBytecodesLeft() < 300) return;            // BCC_GUARD
    int c = G.rc.getRoundNum() % 50 == 25 ? 42 : code;                     // sync rounds pad to SYNC_CODE
    int now = Clock.getBytecodeNum();
    int n = (c - now - C.PADK) & 63;
    int s = 0;
    switch (n) {                                                            // fall-through: costs exactly n
        case 63: s++; case 62: s++; ... case 1: s++; case 0:
    }
}
```

- **The recorded value.** With `PADK` calibrated, `bytecodesUsed ≡ c (mod 64)`. The cost is 17 + n plus the call,
  which is about 48 on average and at most about 90.
- **Robustness.** Overrun turns (used ≥ limit) and guarded turns (used > limit − 300) carry no code, and the decoder
  drops them.
- **Calibration.** `PADK` covers the constant overhead from the `getBytecodeNum()` read to the pause. Calibrate it on
  the same JDK that compiles for the replica: the driver and the VM both use `~/jdk/jdk8u504-b01`.
  1. Set `PADK = 0`.
  2. Run one game: `bot` vs `examplefuncsplayer`, maptestsmall, `GAME_SEED=1`, indicators on. Use the driver, one
     game at a time.
  3. For our robots' non-sync turns with `used <= limit - 300`, take the histogram of
     `(used - ALPHA.indexOf(str.charAt(1))) & 63`. One residue m should hold at least 99.9% of the turns.
  4. Set `PADK = m`. Changing the constant does not change the cost: `iconst` and `bipush` both cost 1.
  5. Re-run and check that the residue is 0.

  Before B's `--tele` exists, adapt the probe reader (`scratchpad/telemetry-probe/reader/TeleRead.java`) in scratch;
  do not commit it.
- **Self-calibration in the decoder.** Each robot alive in a sync round pads to 42. The decoder finds the offset k*
  that maximises the count of sync turns with `(used - k) & 63 == 42`. That detects telemetry teams, and it keeps the
  decode correct even if `PADK` drifts (B.3).

### A.4 Setting `Telemetry.code` (one assignment per exit path)

- `Telemetry.startTurn` sets the type's `!` code: carrier 0, launcher 7, HQ 15, amplifier 63, other 1. `exc()` sets it
  again. Every normal exit of a unit's `run()` must assign the real code. So a `!` on a replica replay means an
  exception, or a path that missed its assignment (a bug either way). B counts these turns as `tele_exc_turns`.
- **Carrier:**
  - `state` follows the existing state char, with the new letters S, V, Q, E, Y and P:
    - `S`: `switchWell()` ran this turn.
    - `V`: `survive()` threw.
    - `K` splits by `deliverAnchor` outcome: `K` known island, `Q` predicted island (`anchorIsland < 0`), `E` no
      target (`explore()`), `Y` timeout branch, `P` `tryPlace()` succeeded.
  - `role` is read at the end of the turn, after any change at a deposit.
  - Set the code in `note()`.
- **Launcher:**
  - `mode`:
    - `F`: movement was ready and `hasHittableEnemies()`.
    - `H`: movement not ready and an enemy hittable.
    - `N`: movement not ready and nothing hittable.
    - `march()`: `S` for each early `return` that holds (objective null, on the island, short of HQ fire); `G` or `W`
      from `regroup()` (regroup vs follow branch); otherwise `M`.
  - `objKind` comes from `pickObjective()` (static; starts at 3).
  - `outnumbered` uses this turn's vision counts.
- **HQ:** reasons are assigned by the precedence below, on the iteration on which `build()` stopped. `tileFail` means
  a `tryBuild` returned false on that iteration.
  ```
  loop condition failed on !isActionReady()                 -> 0 '.'
  loop condition failed on getBytecodesLeft() <= 7000       -> 1 'b'
  loop ended at guard == 6                                  -> 2 'g'
  otherwise (break), with that iteration's ad, mn, resAd, resMn, room, batchOK, threatened, wantAnchor:
    tileFail                                                -> 7 's'
    wantAnchor && ((batchOK && mn >= 45 && mn - 80 < 45)
                   || (!threatened && room && ad >= 50 && ad - 80 < 50))   -> 6 'a'
    mn - resMn >= 45 && !batchOK                            -> 4 'w'
    ad - resAd >= 50 && !threatened && !room                -> 5 'c'
    (ad - resAd >= 50 || (ad - resAd >= 30 && mn - resMn >= 15)) && threatened -> 8 't'
    mn - resMn < 45 && ad - resAd < 50                      -> 3 'p'
    else                                                    -> 9 'x'
  ```
  Implement this as a pure static function `hqReason(...)` so that BotTest can table-test it.
- **Amplifier:** `mode` comes from the branch taken, and `n` is the existing launcher count.

### A.5 Indicator string v2 (every turn; replaces the inline string in `RobotPlayer`)

```
<letter><ALPHA[code]><rest>|ov=<int>,ex=<int>,nm=<int>,sm=<int>,sd=<int>,wh=<int>,bf=<int><extra>
```

- **`letter`** is the letter of `code` (§1.1). The first character is still the state token that
  `ReplayDump --states` and the census column `states_C` read.
- **`ALPHA[code]`** is the exact 6-bit code. The decoder cross-checks it against the BCC.
- **`rest`**: ASCII `[0-9A-Za-z-]` only, at most 14 characters, never `| , = < > &`. By type:

  | Type | `rest` |
  |---|---|
  | Carrier | role digit, plus `k<anchorIsland>` while `anchorTarget != null` (today's note without its first character) |
  | Launcher | `objKind` digit |
  | HQ | `C<n>L<n>A<n>K<n>`, as today |
  | Amplifier | `n` |
  | Other | empty |

- **The counters after `|` are unchanged**: the same keys in the same order. `extra` is unchanged: launcher
  `,pn=..,ua=..` plus `,rg=..,fo=..` when `C.ARMY`.
- **Length:** if the string is longer than 64 characters, cut it at `s.lastIndexOf(',', 64)`. Only whole trailing
  fields are dropped, never part of a number. That fixes today's silent `fo` corruption. Every counter is also in the
  CNT records.
- **ASCII only.** That is what guards against the lone-surrogate engine crash.

Changes from today, documented for every reader:

| Type | Old first character | New first character |
|---|---|---|
| Carrier | `G C W R D F X K T` | The same letters. `K` now means known island only. `S`, `V`, `Q`, `E`, `Y`, `P` and `!` are new. |
| Launcher | Always `L` | Mode letter |
| HQ | Always `C` | Reason letter |
| Amplifier | Always `A` | Mode letter |
| Other | `|` (empty note) | `O` |

In addition, character 1 is now the code character for every type. For carriers it used to be the role digit, which
no tool parsed.

### A.6 Data dot records

Each record is `dot(kind, a, b, c, d)`, which means `rc.setIndicatorDot(new MapLocation(-2 - kind, a), b, c, d)`. The
JSON names in this table are the interface to B (`tele_events.jsonl`) and to C. Unknown kinds must be tolerated.
Kinds 17 to 23 are reserved.

| kind | name | emitter, when | a | b | c | d | JSON fields (B) |
|---|---|---|---|---|---|---|---|
| 0 | HDR | all, first turn | `MAGIC` | type@0:8, spawn_round@8:16 | spawn(loc12)@0:12, roles@12:2, micro@14:1, army@15:1, spawn_safety@16:1, launcher_batch@17:3 | padk@0:8, sync@8:8, build@16:16 | version, type, spawn_round, spawn, roles, micro, army, spawn_safety, launcher_batch, padk, sync, build |
| 1 | EXC | all, in each catch | site@0:4 (1 main GAE, 2 main other, 3 end of turn), gae_type@4:8 (`getType().ordinal()+1`; 0 = not a GAE), phase@12:4, code@16:6 | r0 | round_now | exc_class: 0 GAE, 1 NPE, 2 AIOOBE, 3 Arithmetic, 4 ClassCast, 5 NegativeArraySize, 6 IllegalArgument, 7 IllegalState, 15 other (by `instanceof`) | site, gae_type, phase, code, token, r0, round_now, exc_class |
| 2 | NM | all, near miss | work@0:16, t1@16:16 | code@0:6, enemy_fighters@8:8, ally_fighters@16:8, nearby@24:8 | pending_tiles@0:16, enemies@16:8 | r0 | work, t1, code, token, enemy_fighters, ally_fighters, nearby, pending_tiles, enemies, r0 |
| 3 | OVR | all, round changed during the turn | r0 | round_now | code@0:6, phase@8:4 | work | r0, round_now, code, token, phase, work |
| 4 | CNT | all, periodic (A.7) | ov@0:16, ex@16:16 | nm@0:16, max_bc@16:16 | wall_hits@0:16, stall_flips@16:16 | edge_flips@0:16, budget_flips@16:16 | the names shown |
| 5 | CNTT | carrier, launcher and HQ only, with CNT | 16-bit pairs, see below | | | | the names below |
| 6 | CNTM | all, with CNT | cand@0:3, decided_round+1@4:12 (0 = undecided), sym_conflicts@16:16 | writes@0:16, refused_writes@16:16 | max_pending@0:16, seen_wells@16:8, max_unreported@24:8 | tele_max_cost@0:16, tele_errors@16:8, tele_deferrals@24:8 | cand, decided_round (−1 = undecided), sym_conflicts, writes, refused_writes, max_pending, seen_wells, max_unreported, tele_max_cost, tele_errors, tele_deferrals |
| 7 | SYM | all, each change of `MapMem.cand` and each ignored conflict | eliminated@0:3 (1 ROT, 2 FLIP_X, 4 FLIP_Y), evidence@4:3 (1 tile, 2 well, 3 hq_seen, 4 hq_absent, 5 comms), cand_after@8:3, conflict@12:1 | at(loc12), 0 for comms | r0 | sym_conflicts | eliminated, evidence, cand_after, conflict, at, r0, sym_conflicts |
| 8 | ROLE | carrier, first `pickRole` (reason 0) and each change at a deposit (reason 1) | old@0:4, new@4:4, reason@8:4 | hq_ad (*signed*, −1 = not read) | hq_mn (*signed*) | hq(loc12)@0:12, trips@12:16 | old, new, reason (`spawn` or `hq_stock`), hq_ad, hq_mn, hq, trips |
| 9 | WELL | carrier, `well` set to a new non-null tile | well(loc12)@0:12, well_type@12:2 (1 Ad, 2 Mn, 3 Ex, 0 unknown), source@14:3 (1 shared, 2 seen, 3 any_shared, 4 any_seen, 5 crowd_switch), role@17:2 | d2 (carrier to well) | shared_wells@0:8, seen_wells@8:8, search_turns@16:16 | crowd_turns@0:8, prev_well(loc12)@8:12 | well, well_type, source, role, d2, shared_wells, seen_wells, search_turns, crowd_turns, prev_well |
| 10 | TRIP | carrier, at a deposit that empties it | well(loc12)@0:12, well_type@12:2, role@14:2, load@16:8, hq@24:2 (index in `HQState.ourHQs`) | t_start@0:16, t_first_collect@16:16 (0 = none) | t_last_collect@0:16, t_deposit@16:16 | wait@0:8, explore@8:8, flee@16:8, collect@24:8 (turns this trip in W or S, X, F or V, and C) | well, well_type, role, load, hq, t_start, t_first_collect, t_last_collect, t_deposit, wait, explore, flee, collect |
| 11 | FLEE | carrier, F or V after a turn that was neither, or any throw | threat_d2@0:8, enemy_fighters@8:8, hp@16:8, threw@24:1, moved@25:1 | threat(loc12)@0:12, weight@12:8 | home(loc12) | r0 | threat_d2, enemy_fighters, hp, threw, moved, threat, weight, home, r0 |
| 12 | ANCH | carrier, anchor events | event@0:4 (1 target, 2 rejected, 3 retarget, 4 timeout, 5 returned, 6 placed, 7 took), island@4:8 (255 predicted, 0 none), source@12:2 (0 n/a, 1 seen, 2 shared, 3 predicted), enemy_side@14:1 | target(loc12)@0:12, anchor_turns@12:12 | d2@0:16 | r0 | event, island (−1 predicted), source, enemy_side, target, anchor_turns, d2, r0 |
| 13 | OBJ | launcher, on a kind change, or a move of the objective by more than d² 8 from the last one emitted (kinds 4 to 7: kind change only) | obj_kind@0:4 (0 sighting, 1 enemy_island, 2 enemy_hq, 3 centre, 4 regroup_ally, 5 regroup_home, 6 follow, 7 home_defence), sighting_age@4:4 (stamps, 15 = n/a), ally_launchers@8:8, enemy_fighters@16:8, island@24:8 | objective(loc12) | at(loc12) | r0 | obj_kind, sighting_age, ally_launchers, enemy_fighters, island, objective, at, r0 |
| 14 | FIGHT | launcher, every turn `fight()` runs | ready@0, superior@1, outnumbered@2, any_can_hit@3, moved@4, dir@5:4 (index in `G.DIRS9`), guard_break@9, micro@10, shots_before@12:2, shots_after@14:2, enemy_fighters@16:8, ally_fighters@24:8 | chosen tile: threat@0:8, can_hit@8:1, min_d2@16:8 (255 = no fighter), pinned@24:8 | stay (CENTER) tile: stay_threat@0:8, stay_can_hit@8:1, stay_min_d2@16:8, tiles@24:4 (tiles scored; 0 = CENTER not scored) | hp@0:8, enemies@8:8, target@16:16 (id of the first robot shot this turn, 0 = none) | ready, superior, outnumbered, any_can_hit, moved, dir (name), guard_break, micro, shots_before, shots_after, enemy_fighters, ally_fighters, threat, can_hit, min_d2, pinned, stay_threat, stay_can_hit, stay_min_d2, tiles, hp, enemies, target |
| 15 | HQS | HQ, every 25 rounds | ad@0:16, mn@16:16 | ex@0:16, robots@16:16 (`getRobotCount`) | carriers_built@0:8, launchers_built@8:8, amps_built@16:8, anchors_built@24:8 | shared_wells@0:8, carrier_cap@8:8, float_rounds@16:16 | the names shown |
| 16 | BUG | mobile units, when a wall-following episode ends | moves@0:16, flips@16:8, reason@24:4 (1 closer, 2 new_target, 3 budget) | target(loc12)@0:12, start(loc12)@12:12 | start_round@0:16, r0@16:16 | start_d2@0:16, exit_d2@16:16 | moves, flips, reason, target, start, start_round, r0, start_d2, exit_d2 |
| 24+j | COMMS | the HQ in `Comms.HQ_LOC` slot 0, with HQS; j = 0..7 | slot 8j@0:16, 8j+1@16:16 | 8j+2, 8j+3 | 8j+4, 8j+5 | 8j+6, 8j+7 | B merges the 8 chunks of one (round, id) into `{"kind":"COMMS","slots":[64 ints]}`; a missing chunk gives `null` slots |

**CNTT pairs** run in the order a.lo, a.hi, b.lo, b.hi, c.lo, c.hi, d.lo, d.hi:

| Type | Fields | Note |
|---|---|---|
| Carrier | `trips, fled, throws, anchors_placed, anchors_returned, crowd_switches, wait_turns, explore_turns` | |
| Launcher | `shots, stepped_in, kited, pinned_seen, unsafe_avoided, regroups, follows, guard_breaks` | |
| HQ | `carriers_built, launchers_built, amps_built, anchors_built, float_rounds, 0, 0, 0` | |

New counters are added by A where the event happens: `crowd_switches`, `wait_turns`, `explore_turns`,
`guard_breaks`, `Comms.writes`, `Comms.refusedWrites`, `maxPending` (`pendingTiles()` after the fill) and
`maxUnreported`.

**Locations** decode to `[x, y]`, or `null` when the value is 0. **`token`** in JSON is the code's letter.

No on-map dots or lines are drawn in v1. They are reserved for hand debugging, and B ignores any dot or line with
x ≥ 0.

### A.7 Cadence, volume, and the bytecode budget

**Periodic records:**

- **CNT, CNTT and CNTM** are due when `round >= nextCnt`. Start at `nextCnt = spawnRound + 1 + id % 50`, then add 50
  after each emission.
- **HQS and COMMS** are due at `round >= nextHqs`. Start at 25, then add 25.
- **Deferral.** In `endTurn`, a due record is deferred if `Clock.getBytecodesLeft() < limit*12/100 + R`, where R is
  1,500 for HQs and 400 for the others. Deferral counts in `tele_deferrals`. Nothing is dropped; the record goes out
  late, stamped with its round.

**Volume:**

- A 2,000-round game produces roughly 20,000 to 30,000 dots per team: about 6,000 CNT, 5,000 to 10,000 FIGHT, about
  5,000 events and about 1,000 HQ records. That is roughly 50 to 200 KB gzip.
- This is within the probe's guideline of 50,000 data dots per game.
- It matters only where indicators are on.

**Bytecode budget**, per robot-turn: telemetry's total including hooks. Every cap is checked by test A-9.

| type | every turn (string + pad + bookkeeping) | per event | periodic | hard cap on any turn |
|---|---|---|---|---|
| HQ | ≤ 200 | ≤ 40 | HQS ≤ 60; COMMS ≤ 800 (first HQ, 1 turn in 25); CNT×3 ≤ 120 (1 in 50) | 1,300 |
| Carrier | ≤ 200 | ≤ 40 (ROLE, WELL, TRIP, FLEE, ANCH, BUG, SYM) | CNT×3 ≤ 120 | 450 |
| Launcher | ≤ 200 | FIGHT ≤ 60 (including the stay-tile stores in the scoring loop); OBJ, BUG, SYM ≤ 40 | CNT×3 ≤ 120 | 450 |
| Amplifier, other | ≤ 180 | ≤ 40 | CNT + CNTM ≤ 80 | 350 |

The pad itself averages about 50 and is at most about 90. `tele_max_cost` measures `endTurn` plus `indicator`, from
entry to exit; the pad is bounded by construction.

### A.8 Safety rules (all mandatory)

1. **No exceptions:**
   - `loc12(null)` returns 0.
   - Every array index is bounded and no packer divides.
   - `endTurn` and `indicator` bodies are wrapped in `try { } catch (Exception e) { teleErrors++; }`. Telemetry
     errors never count in `G.exceptions`, so the basics `ex` bar keeps its meaning.
   - Hooks need no try: they are exception-free by construction.
2. **No overruns.** Periodic records are deferred under the reserve; the pad is skipped under `BCC_GUARD`; hooks cost
   at most about 40 each. The existing guards stay as they are: fight at 2,000 left, the HQ at 4,000, chooseIsland at
   3,000.
3. **No change to decisions** except through the bytecodes consumed:
   - No `G.rand()` calls.
   - No shared-array writes.
   - No writes to state that decisions read.
   - The fill reserve is unchanged.
4. **Determinism.** The same code runs whatever the indicator flag. Nothing reads system properties other than the
   existing `bc.testing.debug`.
5. **Fairness in paired tests.** Telemetry costs bytecodes, so both arms of every paired comparison must carry the
   same `Telemetry.java` and the same `C.TELEMETRY`. The first comparison against g_iter0 needs a control rebuilt
   with telemetry (§8).

### A.9 Golden vectors (A's packers and B's `--decode-record` must agree exactly)

| record | inputs | a | b | c | d |
|---|---|---|---|---|---|
| HDR | carrier, spawn_round 37, spawn (12,7), roles 2, micro 0, army 0, spawn_safety 1, launcher_batch 3, padk 16, sync 42, build 0 | 2115895297 | 9473 | 467720 | 10768 |
| ROLE | old 2, new 1, reason 1, hq_ad 30, hq_mn 420, hq (5,5), trips 4 | 274 | 30 | 420 | 16710 |
| WELL | well (20,33), well_type 2, source 2 (seen), role 2, d2 45, shared_wells 5, seen_wells 7, search_turns 0, crowd_turns 0, prev_well none | 304418 | 45 | 1797 | 0 |
| TRIP | well (20,33), well_type 2, role 2, load 40, hq 1, t_start 180, t_first_collect 195, t_last_collect 215, t_deposit 231, wait 3, explore 0, flee 1, collect 20 | 19440930 | 12779700 | 15139031 | 335609859 |
| FIGHT | ready 1, superior 0, outnumbered 1, any_can_hit 1, moved 1, dir 3 (EAST), guard_break 0, micro 0, shots_before 0, shots_after 1, enemy_fighters 3, ally_fighters 1; chosen threat 1, can_hit 1, min_d2 13, pinned 0; stay threat 2, can_hit 1, min_d2 9, tiles 9; hp 140, enemies 4, target 10234 | 16990333 | 852225 | 151585026 | 670696588 |

Code and string examples:

| Example | Code | Character | String |
|---|---|---|---|
| Carrier `C`, Mn | 5 | `5` | `C52\|ov=0,ex=0,nm=0,sm=1,sd=88,wh=3,bf=0` |
| Launcher `F`, sighting, outnumbered | 33 | `X` | `FX0\|...` |
| HQ `w`, wantAnchor | 36 | `a` | `waC3L5A0K0\|...` |
| Sync | 42 | `g` | |

BCC example: offset 0, used 7173. 7173 mod 64 = 5, which decodes as carrier code 5.

### A.10 Test plan A

Unit tests go in `test/bot/BotTest.java` (pure logic, no engine). When `G.rc == null`, `Telemetry.dot` appends to an
int ring `TEST_SINK`.

1. **Code tables.** For each type and every code 0..63: the letter (§1.1), validity, and `ALPHA[code]`.
   `carrierCode`, `launcherCode`, `hqCode` and `ampCode` round-trip their fields.
2. **Golden vectors (A.9).** Every packer output equals the table exactly. Saturation: for example, load 300 packs as
   255, and a negative input packs as 0.
3. **Indicator builder.** Every combination of type with extreme counters (5-digit values, launcher with `C.ARMY`) must:
   - give at most 64 characters;
   - contain only characters 0x20..0x7E, with none of `< > &`;
   - start with letter then code character;
   - drop only whole trailing fields;
   - contain `|ov=`.
4. **`hqReason`.** A precedence table: at least one case per reason, plus overlapping cases that check the order.
5. **Emitters through `TEST_SINK`.** Each emitter writes its kind with `x = -2 - kind` and the packed words. `loc12(null)`
   gives 0. No emitter throws on null or empty inputs.

Game checks are run by A, one game at a time on the driver, `bot` against `examplefuncsplayer` only:

6. **Calibration (A.3).** Residue 0 on at least 99.9% of decodable non-sync turns. Sync turns hold 42 on at least 99%.
7. **Basics on the calibration game:** 0 overruns, `ex=0`, `nm=0`, and no `!` codes.
8. **Fixtures**, produced only after calibration. Both must be at most 1.5 MB, otherwise use SmallElements:
   - `test/fixtures/tele-example-maptestsmall.bc23` (indicators on);
   - `test/fixtures/tele-example-maptestsmall-indoff.bc23` (the same game with `-Dbc.engine.show-indicators=false`
     passed after `run_game`'s own flag; the last `-D` wins).

   Both are `bot` (team A) vs `examplefuncsplayer`, maptestsmall, `GAME_SEED=1`.
9. **Cost check** on the same game with `C.TELEMETRY` true and false:
   - the per-type mean bytecode difference is within the every-turn budget;
   - `tele_max_cost` (CNTM) is within the hard cap;
   - there are 0 overruns either way.

   Report the numbers in the commit message for the orchestrator. The paired win-rate cost runs on the VM (§8), not
   here.

---

## 3. Part B: extraction (`tools/replaydump/ReplayDump.java`)

### B.1 CLI

Existing modes and their output are unchanged. `--census` changes only by the appended columns (B.5).
`ReplayDump.java` stays a single source file, because `tools/replay-dump.sh` compiles that one file.

| flag | output |
|---|---|
| `--extract DIR [--match ID] [--games all\|i,j] [--tele-turns]` | **One pass over the file.** Decompress once, then build and run each selected game's model in turn and write the files of B.4 into DIR (creating it). Without `--match`, ID is the leading digits of the file name, else 0. stdout gets one line per game: `<game> <map> <rounds> <winner A\|B\|-> <win_reason> tele_A=<s> tele_B=<s>`. |
| `--tele [--game N]` | Human telemetry check for one game (format in B.3). |
| `--fingerprint` | One line per game: `<game> <map> <rounds> <state_sha1> <bytecode_sha1>`. |
| `--decode-record KIND A B C D [--type T]` | Prints the JSON that `tele_events.jsonl` would hold for that record, without the common keys. T is a type letter, needed for CNTT. |

**Fingerprint definition.** SHA-1 over decimal text with `,` between values and `\n` after each round. Each round
writes these items in the order shown:

- `roundID`;
- each spawned body as `id,team,type,x,y`;
- each action as `id,action,target`;
- each moved robot as `id,x,y`;
- each `diedIDs` entry;
- each team change as `team,ad,mn,ex`;
- each island as `id,owner`.

`bytecode_sha1` covers `round,id,used`. Indicator strings, dots and lines are excluded.

**Performance:** 10 s or less per 2,000-round game on the driver (2 vCPU) with `DUMP_XMX=1g`. Bucket robots per round
and never loop over shots × robots. There is a test bound of 60 s.

### B.2 Shared definitions (one model per game; every extractor reads it in the same pass)

**Positions:**

- `pre` is the position at the end of round r−1; `post` is the position at the end of round r, both after currents.
- A robot that dies in round r has no `post`; use `pre`.
- The flag `cur` is set when the tile at `pre` has a current and `post == pre + dir`.

**Turn order:** a robot's index in round r's `bytecodeIDs`.

**HP:** `bodyTypeMetadata.health` plus the sum of CHANGE_HEALTH, capped at the maximum. A lethal hit emits no
CHANGE_HEALTH.

**Inventories:** the sum of CHANGE_* per robot (HQs per HQ). On THROW_ATTACK, zero the thrower (cargo and anchors).

**Damage attribution** for a victim v in round r:

- `hits(v)` = LAUNCH_ATTACK and THROW_ATTACK actions with target v.
- `neg(v)` = negative CHANGE_HEALTH entries on v.
- When v died in round r and `hits > neg`, the **last hit in action order** was lethal and dealt v's remaining HP.
- Every non-lethal hit is paired in action order with its CHANGE_HEALTH entry.
- Negative entries not paired with a hit are end-of-round damage:
  - `hq_aura` if v was within r² 9 of a living enemy HQ at `pre` or `post`;
  - otherwise `destab` if an enemy DESTABILIZE at round r−4 had its centre within r² 15 of v;
  - otherwise `other`.

**Death cause.** Apply the first rule that matches:

1. `resign`: every robot of v's side died in r, the game ended in r, and that side lost.
2. `launcher` or `throw`: by the type of the lethal hit.
3. `destab`: an enemy DESTABILIZE at r−4 within r² 15.
4. `hq_aura`: within r² 9 of an enemy HQ at `pre`.
5. `self`: an uncaught exception, or `run()` returned. HQs die only this way or by resigning.

**prog(tile):** an 8-connected BFS over non-wall tiles from each side's HQs gives dA and dB. `prog = dA/(dA+dB)`,
with 0 at A's HQs. Blank when the tile is unreachable.

**reach1(p, q):** `max(|dx|-1,0)^2 + max(|dy|-1,0)^2 <= 16`, meaning p can fire on q after one step.

**Team totals for tiebreaks:** HQ stocks plus living carriers' cargo (RULES §3.5). Track `totalAnchorsPlaced`:
PLACE_ANCHOR onto an island the team did not own at that moment.

### B.3 Telemetry decoding (both sides, independently)

1. **Dots.** Robot i is a dot-telemetry robot if its first record of kind 0 has `a == MAGIC`. Only dots of such
   robots with x ≤ −2 are decoded. The kind is `-2 - x`. Decoding is table-driven from A.6. Unknown kinds go to
   `tele_unknown_kinds`. COMMS chunks are merged.
2. **BCC detection and offset.** For one side, take the sync-round turns (`round % 50 == 25`) with
   `used <= limit - 300`. For each k in 0..63, let `S(k) = #{(used - k) & 63 == 42}`. Then `k* = argmax`.
   - The side is a BCC side when `N_sync >= 10` and `S(k*)/N_sync >= 0.9`.
   - Report `tele_offset = k*` (expected 0) and `tele_sync = S(k*)/N_sync`.
3. **Per robot-turn code**, only on a side detected by step 1 or 2:
   - `code_bcc = (used - k*) & 63` on decodable non-sync turns.
   - `code_str = ALPHA.indexOf(str.charAt(1))` when the string is at least 2 characters long. If `str.charAt(0)`
     is not the code's letter, count `str_letter_mismatch`.
   - The best code is `code_bcc`, else `code_str`, else none.
   - Agreement is measured over turns that have both: `tele_agree = equal / both`.
   - A code outside the type's valid set counts as `tele_invalid`.
4. **Status per side:** `both` (dots and BCC), `dots`, `bcc` or `none`.

Strings from older builds have no HDR and no sync, so they are never decoded as codes.

`--tele` prints, per game:

```
game 0 map maptestsmall rounds 339
side A team bot tele=both offset=0 sync=40/40 (1.000) agree=12873/12880 (0.9995) valid=0.998 invalid=0 exc_turns=0 dots=4123 unknown_kinds=0 letter_mismatch=0
side A records HDR=88 CNT=120 CNTT=96 CNTM=120 ROLE=31 WELL=40 TRIP=55 FLEE=3 OBJ=60 FIGHT=210 HQS=26 ...
side A CARRIER G=0.31 C=0.25 R=0.20 ...      (letter shares >= 1%, as in --states)
side B team examplefuncsplayer tele=none
```

### B.4 Output files of `--extract DIR` (header first, comma-separated, no commas inside fields)

Lists inside a field use `;` or spaces. `side` is A or B, the replay label. C maps it to us and them.

**`games.csv`**: one row per game and side (E12 and telemetry status).

```
match,game,map,width,height,symmetry,islands,rounds,side,team,won,win_reason,tb_margin,vtb500,vtb1000,vtb1500,tele,tele_offset,tele_sync_n,tele_sync,tele_agree_n,tele_agree,tele_valid,tele_invalid,tele_exc_turns,tele_dots,tele_unknown_kinds
```

- `win_reason` is one of:
  - `conquest`: the winner placed an anchor in the final round and held at least ceil(0.75·N) islands after it;
  - `resign`;
  - `tb_islands`, `tb_anchors`, `tb_ex`, `tb_mn`, `tb_ad`: at 2,000 rounds, the first strictly differing criterion of
    RULES §8.4, recomputed. It must agree with the recorded winner, otherwise the reason is `other`;
  - `coin`: everything equal;
  - `other`.
- `tb_margin` is the winner minus loser on the deciding criterion; it is blank for conquest and resign.
- `vtbR` is the side that would win the tiebreak if the game ended after round R; blank if the game ended earlier.

**`census.csv`**: `match,game,` followed by the full `--census` header. For each game, the row from `game` onward must
be **byte-identical** to `--census --no-header --game N`. C relies on this to drop the per-game census calls (C.2).

**`deaths.csv`** (E2): one row per `diedIDs` entry.

```
match,game,round,id,side,type,age,x,y,prog,cause,killer_id,killer_type,hp_before,cargo_Ad,cargo_Mn,cargo_Ex,anchors,spawn_kill,eng,last_code,last_token
```

- `cause` is one of launcher, throw, destab, hq_aura, resign, self.
- `killer_*` is filled only for launcher and throw.
- `spawn_kill` = age ≤ 5.
- `eng` is the engagement id, or blank.
- `last_code` and `last_token` are the best code and letter of the victim's last turn (telemetry sides only).

**`engagements.csv`** (E1).

```
match,game,eng,r0,r1,dur,x0,y0,prog0,nA0,nB0,hpA0,hpB0,peakA,peakB,joinA,joinB,first_hit,dmg_by_A,dmg_by_B,kills_by_A,kills_by_B,val_lost_A,val_lost_B,aura_dmg_A,aura_dmg_B,surv_A,surv_B,held,result,codes_A,codes_B
```

How engagements are built:

- Each round, the **nodes** are launchers and destabilizers alive at the start of the round or dying in it, plus
  carriers that threw this round.
- **Edges** join opposing nodes with `reach1(pre, pre)`. Every hit adds an attacker→victim edge, and the victim joins
  the nodes.
- A component with both sides in it is a **fight cell**.
- A cell joins every engagement that any of its members belonged to within the last 3 rounds. Engagements merge with
  union-find, and the merged one keeps the **earliest** `r0` and its start numbers.
- An engagement ends when none of its members has been in a cell for 3 rounds.

Column meanings:

- `nA0`, `hpA0`: side A's live launchers within r² 36 of the first cell's centroid at r0, and their summed HP.
- `peakA`: the most of side A's launchers in the engagement's cells in any one round.
- `joinA`: distinct side-A launchers that were ever in one of its cells.
- `first_hit`: the side of the first launcher or throw hit.
- `dmg_by_A`: HP removed from B's robots by A's hits, with lethal hits counted at the victim's remaining HP.
- `kills_by_A`: B robots killed by A's hits.
- `val_lost_A`: §1 value of A's robots that died in the engagement's cells, any cause.
- `aura_dmg_A`: HQ aura damage taken by A's robots in the cells.
- `surv_A`: A's participating launchers still alive at r1.
- `held`: the side with more live launchers within r² 36 of the last centroid at r1 + 5, or `-`.
- `result`: the side with the larger `val_lost_other - val_lost_own`. A tie goes to more damage dealt, otherwise
  `draw`.
- `codes_A`: telemetry sides only. Counts of the side's launcher-turn codes in the cells, written
  `<letter>[o]=<n>;...`, where `o` marks the outnumbered flag. For example `F=12;Fo=7;H=20;Ho=3;M=2`.

**`timeline.csv`** (E3): every 10 rounds and at the final round, per side.

```
match,game,round,side,alive_C,alive_L,alive_A,alive_D,alive_B,built_C,built_L,built_A,coll_Ad,coll_Mn,coll_Ex,bank_Ad,bank_Mn,bank_Ex,carried_Ad,carried_Mn,carried_Ex,army_value,value_lost,dmg_dealt,kills,islands,anchors_placed,in_contact
```

- `bank` is HQ stock summed over the side's HQs. `carried` is carriers' cargo.
- `army_value` is the value of living non-HQ robots.
- `value_lost`, `dmg_dealt` and `kills` are cumulative, using the hit attribution of B.2.
- `in_contact` counts the side's launchers in a fight cell that round.

**`hq.csv`** (E11 and the HQ codes): per HQ per 25-round bucket. The row's `round` is the bucket's last round.

```
match,game,round,side,hq_id,x,y,bank_Ad,bank_Mn,bank_Ex,built_C,built_L,built_A,built_K,pressure34,pressure9,idle_funds,codes
```

- `pressure34` and `pressure9`: enemy launcher-rounds within r² 34 and r² 9.
- `idle_funds`: rounds in which this HQ ended with at least 45 Mn or at least 50 Ad, built nothing, and had at least
  one free passable tile within r² 9.
- `codes`: telemetry sides only, as `<reason letter>=<n>;...`.

**`robots.csv`**: one row per robot.

```
match,game,id,side,type,born,died,cause,x_born,y_born,turns,max_still,still_r0,bc_max,bc_over,bc_near,codes
```

- `max_still` is the longest run of rounds alive without a position change. `still_r0` is the round that run started.
- `codes` (telemetry sides only) gives the top 4 letters, as `G=40;C=30;R=20;D=10`.

**`tele_states.csv`**: telemetry sides only.

```
match,game,side,type,phase,code,letter,detail,turns,share,src_bcc,src_str
```

- `phase` is one of `all`, `open` (r ≤ 150), `mid` (151–600) or `late` (> 600).
- `detail` decomposes the code: `role=Mn`, `obj=sighting;out=1`, `threat=1;anchor=0` or `n=3`.
- `src_*` counts which channel supplied each code.

**`tele_events.jsonl`**: one JSON object per decoded record. The common keys are
`"match","game","round","id","side","type","kind"`, where `round` is the replay round in which the dot was recorded,
followed by the A.6 fields. For example:

```
{"match":123,"game":0,"round":231,"id":10452,"side":"A","type":"C","kind":"TRIP","well":[20,33],"well_type":2,"role":2,"load":40,"hq":1,"t_start":180,"t_first_collect":195,"t_last_collect":215,"t_deposit":231,"wait":3,"explore":0,"flee":1,"collect":20}
```

The file is written only when some side has dots.

**`tele_turns.csv`** is written only with `--tele-turns`:
`match,game,round,id,side,type,used,code_bcc,code_str,sync`.

**Tier 2 file `trips.csv`** (E6): one row per carrier trip, both sides, replay-derived. A trip runs from a deposit at
one of the side's own HQs, or from spawn, to the next deposit, death, throw, anchor pickup, or the end of the game.

```
match,game,side,carrier,t0,first_collect,last_collect,t_end,well_x,well_y,well_type,collects,load,wait_rounds,outcome,codes
```

- `wait_rounds` counts rounds spent within r² 8 of the well without collecting.
- `outcome` is one of deposit, death, throw, anchor or end.
- `codes` (telemetry sides only) gives the letter counts during the trip.

### B.5 How census.csv grows

Existing columns keep their order and meaning. Known legacy definitions stay documented in the header comment:

- `dmg` credits all negative CHANGE_HEALTH, HQ aura included, to the other team, and leaves out lethal damage.
- `kills` counts any death that had a hit in the same round.

New tools should use `dmg_hits` and `kills_hits`. New columns are **appended**, in this exact order. Tier 1 comes
first; Tier 2 columns are appended after the Tier 1 columns when they are built. Every value is for the row's team.

**Tier 1** (34 columns):

```
win_reason,tele,tele_offset,tele_agree,tele_exc_turns,tstates_C,tstates_L,tstates_HQ,tstates_A,tele_carrier_mn,tele_L_out,
deaths_launcher,deaths_throw,deaths_destab,deaths_aura,deaths_self,deaths_resign,value_lost,cargo_lost_Ad,cargo_lost_Mn,
anchors_lost,spawn_kills,dmg_hits,kills_hits,dmg_aura,kills_aura,eng_n,eng_won,eng_lost,eng_n_par,eng_won_par,
eng_n_ahead,eng_won_ahead,eng_n_behind,eng_won_behind,exch_ratio,first_hit_rate,turn_round,lock_round,onset_L,onset_Mn,
onset_value,onset_islands,idle_funds
```

(The line breaks are only for display: one header line, no spaces.)

**Telemetry columns:**

- `tstates_*` give letter shares of at least 1% in the `states_C` format (`G=0.31 C=0.25`), from the best code. They
  are blank for non-telemetry sides.
- `tele_carrier_mn` is the share of carrier turns with the Mn role.
- `tele_L_out` is the share of F and H launcher turns with the outnumbered flag.

**Engagement columns:**

- ΔN = this team's `n0` minus the other team's `n0`. Parity means ΔN = 0, ahead means ΔN ≥ 2, behind means ΔN ≤ −2.
- `exch_ratio` = value destroyed / value lost over all engagements, blank when the value lost is 0.

**Game-level columns** (E3), the same in both rows:

- `turn_round` is the earliest sample from which the army-value lead always favours the eventual winner.
- `lock_round` is the earliest sample from which `(Vw - Vl)/max(Vw, Vl, 1) >= 0.33` always holds.
- `onset_M` is the earliest sample from which the side strictly leading in M is the winner at every later sample. M is
  alive launchers, cumulative Mn collected, cumulative value destroyed, or islands held.
- Each is blank if it never happens.

**Tier 2** (appended after the Tier 1 columns):

```
kite_stand_fire,kite_fire_retreat,kite_stepin_fire,kite_fire_ambiguous,kite_advance,kite_retreat,kite_hold,exposed_end,
alone20,group_p50,trip_cycle_p50,partial_loads,carriers_per_well,blind_rate,focus,kill_conv,first_builds
```

**`kite_*`** (E7) are shares over this team's launcher turns in a fight cell.

The target of a miss is decoded from the action; the target of a hit is the victim's `post` if the victim acted
earlier in turn order, else its `pre`. The classes, by whether the launcher fired and whether it moved (ignoring
current pushes):

| Fired | Moved | Class |
|---|---|---|
| Yes | No | `stand_fire` |
| Yes | Yes | `fire_retreat` if the target was in r² 16 from `pre` only |
| Yes | Yes | `stepin_fire` if it was in r² 16 from `post` only |
| Yes | Yes | `fire_ambiguous` if it was in range from both |
| No | Yes | `advance` or `retreat`, by the sign of Δd² to the nearest enemy launcher |
| No | No | `hold` |

**Other Tier 2 columns:**

- `exposed_end`: the share of contact turns that end within r² 16 of a live enemy launcher.
- `alone20`: contact launcher-turns with no own launcher within r² 20.
- `group_p50`: the median size of own-launcher components (r² 20) among contact launchers.
- `trip_cycle_p50`: the median of `t_end - t0` over deposit trips.
- `partial_loads`: the share of deposits under 40.
- `carriers_per_well`: the median number of carriers within r² 2 of a used well, counted while a carrier of this team
  is there.
- `blind_rate`: the share of shots that hit nothing.
- `focus`: the share of hits whose victim took 2 or more hits that round.
- `kill_conv`: the share of victims hit that died within 3 rounds.
- `first_builds`: the side's first 12 builds as `r:T` joined by spaces.

Tier 3, not now: E9 map control, E10 `islands.csv`, E13 vision, E14 raids, E15 retreat and heal, E16 special units,
E17 terrain, E18 compute. Add them later as appended columns or new files under the same rules.

### B.6 Tiers for B

| Tier | Contents |
|---|---|
| **Tier 1** | `--extract` (one pass), `games.csv`, `census.csv` plus the Tier 1 columns, `deaths.csv`, `engagements.csv`, `timeline.csv`, `hq.csv`, `robots.csv`, `tele_states.csv`, `tele_events.jsonl`, `--tele`, `--fingerprint`, `--decode-record` |
| **Tier 2** | `trips.csv` and the Tier 2 census columns |

The decoder must handle every A.6 kind from the start, even those A builds in its Tier 2 (SYM, BUG, COMMS).

### B.7 Test plan B (in `tools/test_tools.py`, as new test classes; existing classes must keep passing unchanged)

1. **Regression:**
   - Summary, `--bytecode`, `--games` and the existing census columns are byte-identical on both current fixtures.
   - The new census header starts with the old header.
   - Each row's field count equals the header's.
2. **`--extract` on `two-games.bc23`** (g_iter0 vs examplefuncsplayer):
   - Every Tier 1 file exists with exactly the headers above.
   - `games.csv` has 4 rows.
   - `census.csv` rows equal the per-game `--census --no-header --game N` lines with the `match,game,` prefix.
   - `tele` is `none` on both sides (g_iter0 strings carry no HDR and no sync).
3. **Identities on `example-mirror-maptestsmall.bc23`:**
   - Deaths by cause add up to the summary's died counts per side.
   - Side B's deaths split into 86 hit kills and 10 `hq_aura` (pinned in the existing ReplayDumpTest docstring).
   - Engagement `dmg_by_*` ≤ the census `dmg_hits`.
   - Reconstructed HP is never above the maximum.
   - (Tier 2) Trip collects add up to `coll_*`.
4. **Golden vectors:** `--decode-record` gives the exact JSON for every A.9 row, plus an unknown kind (`{"kind":"K20"}`).
5. **`--fingerprint`:** stable across two runs, and different for the two games of `two-games.bc23`.
6. **Integration** (enabled when A's fixtures land):
   - On `tele-example-maptestsmall.bc23`, side A shows `tele=both`, offset 0, sync ≥ 0.99, agree ≥ 0.999,
     `unknown_kinds=0` and `letter_mismatch=0`. Side B shows `none`.
   - On the `-indoff` fixture, side A shows `tele=bcc`.
   - **The state fingerprints of the two fixtures are equal.**
   - **For at least 99.9% of decodable turns, the indoff game's BCC code equals the string code recorded in the
     indicators-on game.** This is the end-to-end proof that a replica-style replay carries our codes.
   - Until the fixtures exist, these tests `skipTest` with the fixture path. The merge step (§8) removes the skip.
7. **Speed:** `--extract` on the mirror fixture finishes in under 60 s.

---

## 4. Part C: match reports (Python, standard library only)

### C.1 `tools/match_report.py`

```
tools/match_report.py match <replay.bc23> (--match-json FILE | --match-id ID) [--shadow REPLAY] [--force]
tools/match_report.py sweep [--pages N] [--max N]        # our recent finished matches not yet reported
tools/match_report.py file <replay.bc23> --us A|B --label NAME   # any local replay; report to matches/local/NAME.md
tools/match_report.py field [--max N] [--since ID]       # Tier 2: a sample of field-vs-field matches
```

**`match`:**

1. Load the match JSON from the API. It needs the participants with `player_index`, `teamname`, `team` and
   `submission`, plus `alternate_order`, `is_ranked`, `created` and `maps`.
2. Run `bash tools/replay-dump.sh <replay> --extract matches/<id>/extract --match <id>`, with a 1,800 s timeout.
3. Write `research/matches/<id>.md` (C.3).
4. Append one line to `progress/telemetry.jsonl` (C.4).
5. Be idempotent. If that match id already has a line with the same `v`, do nothing unless `--force`. With `--force`,
   append a new line with `"supersedes": true`; readers take the last line per match.

**Which side is ours:** the side whose `teamname` is `vibe23` (env `CONTEST_TEAM`). `side` = A when `player_index` is
0. Game i is reversed when `alternate_order` is set and i is odd, as in `contest.run_rows`.

**`sweep`** is for ranked ladder matches and autoscrims, which nothing downloads today:

1. List our matches with `contest.matches(team_id, pages)` (import `contest.py` with `importlib`, as `test_tools`
   does).
2. For every status `OK!` match without a line in `progress/telemetry.jsonl`, download it into
   `matches/<id>/<id>.bc23` with `contest.download` and run `match`.
3. Process at most `--max` matches (default 30) in one run.
4. Before downloading, require at least 2 GB of free disk on the driver; otherwise refuse.

The orchestrator adds `sweep` to every check-in.

**Disk.** Extract directories are kept, since they are small. Replays under `matches/` are deleted after 14 days,
except for losses and anomaly matches, which are kept 30 days.

### C.2 Hook in `tools/contest.py` (the only change to that file)

- **`report_hook(match, replay_path, team_id)`:**
  - Writes `match` to a temporary JSON file.
  - Runs `match_report.py match <replay> --match-json <tmp>` as a subprocess, with a 1,800 s timeout.
  - Never raises: on failure it prints one line, `report: match <id> failed: <reason>`.
  - Skipped when env `NO_MATCH_REPORT=1`.
- **Call sites:**
  - The `fetch` command: after each `download` returns a path.
  - `block()`: right after `download(m, ...)` returns `rep`.
- **`census_of(replay, game_rows)`:** when `matches/<id>/extract/census.csv` exists, take each game's row from it.
  Strip the leading `match,game,` fields and keep the existing `cell_*` prefix logic. Otherwise fall back to the
  current per-game `--census` calls. B guarantees the lines are identical, so this saves 3 to 10 extra ReplayDump runs
  per match on the 2-vCPU driver.
- **No other behaviour of `contest.py` changes.** Its existing tests in `test_tools.py` must pass untouched.

### C.3 The report: `research/matches/<id>.md` (at most 8 KB; if over, shorten the per-game narratives first)

The report is built from the extract files and the match JSON. Every number is computed; nothing is free text from
memory. Template:

```
# Match <id>: vibe23 (sub <n>) vs <opponent> - <ourWins>-<theirWins>   (<ranked|unranked>, <created UTC>)
Telemetry: us <none|bcc|dots|both> (sync <s>, agree <a>, offset <k>, exc turns <e>)  |  replay <path>  |  extract matches/<id>/extract
| game | map | side | result | rounds | reason | turn/lock | Mn@100 us/them | L@100 | L@250 | eng won/lost (par, ahead, behind) | exch | our deaths (L hit/aura/other) | anomalies |

## Game <i>: <map>, <win|loss> r<rounds> (<win_reason>)
What happened: <2-4 generated sentences: result and reason; economy at r100 (Mn, Ad, carriers); launchers at r100/r250;
first contact round; where value was lost (largest death cause); islands at the end>.
Turning point: turn r<turn_round>, lock r<lock_round>; onset L r.., Mn r.., value r.., islands r..; the engagement with
the largest value swing in [turn_round-50, turn_round+10]: r0-r1 at prog p, us n0 vs them n0, result, exchange.
Economy and army: table at r50/100/150/250/500/1000/end, us/them: alive_C, alive_L, coll_Mn, coll_Ad, bank_Mn, army_value, islands.
Engagements: top 5 by |value swing| (r0-r1, prog0, n us/them, first hit, damage us/them, kills, result, our codes);
our record by ΔN bucket (behind / -1 / par / +1 / ahead).
Our decisions vs outcomes (telemetry sides only):
  BCC/strings: carrier letters by phase (open/mid/late) and Mn-role share; HQ reasons (p w c a s t) with idle_funds
  rounds and bank_Mn at those times; launcher modes overall vs inside engagements, outnumbered share at contact.
  Dots (local or shadow): trips n, cycle p50, wait/explore per trip, well sources; role changes with HQ reads; OBJ by
  kind; FIGHT: share of turns choosing a tile with more threat than staying, step-ins while outnumbered; BUG p90 moves;
  symmetry decided round; COMMS fill (non-zero slots) at r100/r500.
Deaths: by cause and type (us/them), spawn kills, cargo lost, anchors lost.
Anomalies: (list below, or "none").
```

**Anomalies** are listed for our side, or for either side if marked:

| Anomaly | Trigger | Source |
|---|---|---|
| `overruns:<n>` | — | census `over` |
| `near:<n>` | — | census `near` |
| `exc:<n>` | `tele_exc_turns` + `ex` + `self` deaths > 0 | census and `deaths.csv` |
| `bcc_disagree:<x>` | `1 - tele_agree > 0.001` | census |
| `tele_missing` | our side shows `none` | census |
| `stall:<type>#<id>@r<a>-r<b>` | `max_still` ≥ 30 for a carrier or launcher, outside any engagement | `robots.csv` |
| `float:Mn<min>@r<a>-r<b>` | `bank_Mn` ≥ 500 for ≥ 10 consecutive samples | `timeline.csv` |
| `idle_hq:<share>` | `idle_funds` / HQ-rounds > 0.2 | census |
| `unknown_kinds:<n>` | — | `games.csv` |
| `letter_mismatch` | — | `--tele` |
| `opp_exc:<n>` | `self` deaths of the opponent | `deaths.csv` (them) |

### C.4 `progress/telemetry.jsonl` (one line per match, append-only; schema `v` = 1)

```
{"v":1,"match":123,"reported_at":"2026-10-08T19:20:00Z","created":"...","ranked":true,"status":"OK!",
 "us":"vibe23","submission":24,"opponent":"teamX","our_label":"A","score":[2,1],
 "replay":"matches/123/123.bc23","extract":"matches/123/extract","report":"research/matches/123.md",
 "shadow":null,                                   // or {"replay":..., "verified_games":[0,2], "mismatch_games":[1]}
 "games":[GAME, ...]}
GAME = {"game":0,"map":"Forest","rev":false,"side":"A","result":"win|loss|unknown","rounds":1234,
 "win_reason":"tb_islands","turn_round":180,"lock_round":250,"onset":{"L":40,"Mn":100,"value":200,"islands":800},
 "us":SIDE,"them":SIDE,
 "tele":{"status":"bcc","offset":0,"sync":0.998,"agree":null,"exc_turns":0,
         "states":{"C":{"G":0.31,"C":0.25},"L":{"F":0.1},"HQ":{"p":0.4},"A":{}},
         "states_by_phase":{"open":{"C":{...},"L":{...},"HQ":{...}},"mid":{...},"late":{...}},
         "carrier_mn":0.8,"launcher_out":0.12,
         "eng_codes":{"F":12,"Fo":7,"H":20,"Ho":3},
         "events":{"TRIP":120,"FIGHT":300},
         "trip":{"n":120,"cycle_p50":38,"wait_mean":2.1,"explore_mean":0.4}|null,
         "fight":{"n":300,"riskier_than_stay":0.21,"stepin_outnumbered":0.08}|null},
 "anomalies":["overruns:3","stall:L#10234@r300-r380"]}
SIDE = {"team":"vibe23","built":{"C":..,"L":..,"A":..},"died":{"C":..,"L":..},"coll":{"Ad":..,"Mn":..,"Ex":..},
 "at":{"50":{"C":..,"L":..,"Mn":..,"Ad":..,"value":..},"100":{...},"150":{...},"250":{...},"500":{...}},
 "deaths_by_cause":{"launcher":..,"throw":..,"destab":..,"hq_aura":..,"self":..,"resign":..},
 "value_lost":..,"dmg_hits":..,"kills_hits":..,"spawn_kills":..,"cargo_lost_Mn":..,
 "eng":{"n":..,"won":..,"lost":..,"n_par":..,"won_par":..,"n_ahead":..,"won_ahead":..,"n_behind":..,"won_behind":..,
        "exch":..,"first_hit":..,"by_dn":{"-3":[n,won],...,"3":[n,won]}},
 "idle_funds":..,"overruns":..,"near":..,"islands_end":..,"anchors_placed":..,
 "kite":{...}|null,"alone20":..|null,"first_builds":"..."|null}
```

`at.R` is omitted when the game ended before R. `by_dn` buckets ΔN at the start, clamped to −3..3. A `field` line
(Tier 2) goes to `progress/field.jsonl` in the same GAME format, with `"us":null` and sides keyed by team name.

### C.5 `tools/telemetry_query.py`: aggregate answers across matches

```
tools/telemetry_query.py <question> [--since YYYY-MM-DD | --last N] [--opponent NAME] [--submission ID] [--map M]
                         [--ranked | --unranked] [--by opponent|map|submission|phase] [--csv] [--deep]
```

The tool reads `progress/telemetry.jsonl`, keeping the last line per match. `--deep` also reads
`matches/<id>/extract/*.csv` where present, which gives timelines and per-engagement rows. Output is aligned text, or
CSV with `--csv`: means with SE and n games for every row. The questions follow the ranked information needs:

| question | answers (need #) | main sources |
|---|---|---|
| `econ` | Why our mana arrives late (1): Mn and Ad at r50/100/250 us vs them; carriers built and alive; carrier letter shares by phase; Mn-role share; trips and cycle times when dots exist | `at`, `tele.states_by_phase`, `tele.trip` |
| `fights` | Why we lose launcher fights (2): engagement win rate by ΔN (−3..+3), us vs opponents; exchange; first-hit rate; our mode shares inside engagements; outnumbered share at contact; kite classes (Tier 2) | `eng.by_dn`, `tele.eng_codes`, `kite` |
| `hq` | What the HQ waited for (3): reason shares, idle_funds per game, float anomalies | `tele.states.HQ`, `idle_funds` |
| `opening` | Opening timeline (4): alive L and C us/them at r50/100/150, first builds, onset rounds | `at`, `first_builds`, `onset` |
| `deaths` | Our deaths (7): by cause and type, value lost, spawn kills, cargo lost | `deaths_by_cause` etc. |
| `turning` | Earliest predictive round: distributions of turn and lock rounds. For R in 50..500 step 50, how often the leader at R in L, Mn, value and islands wins (with `--deep`, from `timeline.csv`) | `onset`, `timeline.csv` |
| `basics` | Basics bar on replica games (11, 14): overruns, near, exception turns, BCC agreement and telemetry presence per submission | `us.*`, `tele.*` |
| `losses` | Our losses, each with its report link and the largest negative us-minus-them delta among Mn@100, L@250, eng won share and value lost | everything |
| `anomalies` | Matches with anomalies, by kind | `anomalies` |
| `field` (Tier 2) | Field behaviour rates (5): per team means of the census features, and a two-group contrast. The groups are bots that beat us against bots we beat; keep only the rates where we differ from the first group and match the second | `progress/field.jsonl` |

### C.6 Guards in `tools/basics.py` and `tools/delivery.py` (C owns these small edits)

Replica rows carry no counters. Today they read as passes for exceptions, near misses and symmetry. The new rules:

- **`basics.py`:** for rows whose `tele` column is `none` or `bcc` (strings absent):
  - Exceptions use `tele_exc_turns`. When `tele` = `none`, report `n/a` instead of PASS.
  - Near misses use the replay-side `near`.
  - Both symmetry bars report `n/a (no strings)`.
  - Rows without a `tele` column (old runs) behave as today.
- **`delivery.py --fire`:** print `n/a (no counters in N games)` when a counter is absent from every candidate row,
  instead of reading 0.

### C.7 Shadow re-runs (`tools/shadow.py`, Tier 2): full telemetry for replica games at no quota cost

> **Not used, and `tools/shadow.py` is not built** (decided 2026-10-08). A shadow re-run plays the other team's bot on
> our own machine, which a contestant cannot do: CLAUDE.md rule 10 allows local games only between our own builds.
> Replica games carry the bytecode channel and the replay-only extractors; dots and strings are for local games of
> our own builds. The section is kept as the record of the design.

Games are deterministic: the indicator flag does not change play, and identical code on an identical cell replays
identically. Re-running one of our replica matches on the VM with indicators on therefore recovers every string and
dot.

```
tools/shadow.py run <match id> [--games all|i,j]    # one shadow run
tools/shadow.py pending [--max-per-hour 6]           # losses first, then anomaly matches, then the rest
```

**`run` steps:**

1. On `battlecode-dev` (`tools/vm.sh`), take one slot of the gauntlet semaphore (`/tmp/bc23-game-slots`). Never more
   than one shadow engine at a time.
2. Copy both participants' compiled `binary.zip`. Their path is
   `storage/bc23-replica-secure/episode/bc23/submission/<submission id>/binary.zip` under `/srv/bc23-galaxy/`, with
   group-read access as the galaxy's own tools have it, or the same path through the site gate.
3. Run `tools/replica/worker.py` `match_command` with identical arguments: the same names, packages, maps (or only the
   selected games, with team order swapped for reversed games) and the same alternate order. The only change is
   `-Dbc.engine.show-indicators=true`, plus a different save file.
4. Bring the replay back to `matches/<id>/shadow.bc23`.
5. Compare `--fingerprint` per game with the replica replay. Use only games whose `state_sha1` matches. If
   `bytecode_sha1` differs, keep the game but add a warning.
6. Re-run `match_report.py match ... --shadow`, which fills the dot sections and `"shadow"` in the JSON line.

**Rules:**

- Nothing in `/srv/bc23-galaxy`, the galaxy database or saturn is modified.
- Shadow runs never use replica quota, and they share the VM with gauntlet slots.
- The default budget is 6 shadow games an hour. Before each run, check that the VM has at least 2 GB of free disk.

### C.8 Test plan C (new `tools/test_match_report.py`; C adds its one line to `tools/unit-tests.sh`)

1. **`match` on `two-games.bc23`** with a synthetic match JSON (vibe23 = player 1, alternate order):
   - the report exists, has both game sections, the summary table, and an "Anomalies" line per game;
   - it is at most 8 KB;
   - the JSON line parses and has every C.4 key;
   - `side`, `rev` and `result` match `contest.run_rows` for the same JSON;
   - a second run appends nothing.
2. **Robustness:** with `tele_events.jsonl` and the Tier 2 columns removed from a copy of the extract, the report
   still renders, and its telemetry sections say "not available".
3. **Hook:**
   - with `subprocess.run` monkeypatched, `report_hook` is called from the fetch path, and a raising subprocess does
     not raise;
   - `NO_MATCH_REPORT=1` skips the hook;
   - `census_of` reads the extract's `census.csv` when present (temp directory) and falls back otherwise;
   - the output is identical either way.
4. **`telemetry_query`** on a synthetic 3-match JSONL: exact expected numbers for `econ`, `fights` (the ΔN table),
   `deaths` and `basics`; the `--csv` output parses; filtering by `--opponent` and `--last` works.
5. **Guards:** `basics.py` on a synthetic census with `tele=bcc` reports `n/a` for symmetry and uses `tele_exc_turns`.
   Old-format rows are unchanged.
6. **Integration** (enabled at merge): `file` on the tele fixture with `--us A` shows non-empty carrier, launcher and
   HQ state shares, a trips line and FIGHT stats. On the indoff fixture, it shows state shares and "not available"
   for the dot sections.
7. **Shadow (Tier 2):** a unit test of fingerprint comparison and game selection, using stubbed VM calls. No VM in
   unit tests.

---

## 5. Interfaces and file ownership

| part | owns (writes) | consumes |
|---|---|---|
| A | `src/bot/*.java` (Telemetry.java new; RobotPlayer, C, G, Carrier, Launcher, HQ, Amplifier, Other, Nav, MapMem, Comms hooks), `test/bot/BotTest.java`, `test/fixtures/tele-*.bc23` | §1, A.* |
| B | `tools/replaydump/ReplayDump.java`, new test classes in `tools/test_tools.py` | §1, A.5, A.6, A.9 |
| C | `tools/match_report.py`, `tools/telemetry_query.py`, `tools/shadow.py`, `tools/test_match_report.py`, `tools/contest.py` (hook and `census_of` only), `tools/basics.py`, `tools/delivery.py` (guards only), one line in `tools/unit-tests.sh`; generated `research/matches/*.md`, `progress/telemetry.jsonl`, `progress/field.jsonl` | B.1, B.4, B.5 |

**Contracts between the parts:**

- **A → B:**
  - record kinds, bit layouts and JSON names (A.6);
  - code tables, `ALPHA`, `MAGIC`, sync and guard (§1);
  - string v2 (A.5);
  - golden vectors (A.9).
- **B → C:**
  - CLI flags (B.1);
  - file names and headers (B.4);
  - census column names (B.5);
  - JSON names (A.6).

  C reads every CSV with `csv.DictReader` by name and tolerates missing columns and files.
- **Shared rules:** CSV fields never contain commas. Strings are ASCII. `side` is A or B, the replay label.

---

## 6. Coverage: ranked information needs and where each is answered

| # | need | replica game as configured (BCC + replay) | plus dots (local, shadow, or flag on) |
|---|---|---|---|
| 1 | Why mana arrives late | Carrier states and Mn role per turn; trips, wells and crowding (Tier 2 `trips.csv`); timeline | ROLE with HQ reads, WELL sources, TRIP wait and explore |
| 2 | Why we lose launcher fights | Engagements with ΔN, exchange, first hit; our mode and outnumbered codes inside them; kite classes (Tier 2) | FIGHT: the chosen tile against staying, pinned count, guard breaks |
| 3 | What the HQ waited for | HQ reason code every turn; `hq.csv` idle funds and pressure | HQS snapshots (carrier cap, wells) |
| 4 | Opening timeline | `timeline.csv`, `first_builds`, onsets | — |
| 5 | Field behaviour rates | Census rows for both teams; field matches (C Tier 2) | — |
| 6 | Launcher objectives and groups | objKind per turn; group size (Tier 2) | OBJ with sighting age, allies and enemies |
| 7 | Our deaths | `deaths.csv` with cause, killer and last code | — |
| 8 | Map control, islands | Win reason, islands in the timeline (E9 and E10 are Tier 3) | ANCH events |
| 9 | Why anchors are not placed | Carrier states K, Q, E, Y, P | ANCH with reasons |
| 10 | Movement stalls | `robots.csv` `max_still` | BUG episodes, Nav counters |
| 11 | Bytecode headroom | Overruns and near misses from bytecodes | NM with context, t1, `max_bc`, `tele_max_cost` |
| 12 | Symmetry | n/a | SYM events, `cand` and `decided_round` |
| 13 | Shared-array use | n/a | COMMS snapshots, writes and refused writes |
| 14 | Exceptions | `!` codes (`tele_exc_turns`), `self` deaths | EXC with site, phase, class |
| 15 | Spawn safety | Spawn kills, `pressure9` | — |

---

## 7. Volume, disk, and the owner decision

- **Replica as-is.** The BCC changes bytecode values, not replay size. Replica disk use is unchanged.
- **Local and shadow games.** Dots add roughly 50 to 200 KB gzip per 2,000-round game, about 0.5 to 2 MB per
  10-game match.
- **Analysis outputs.** Each match's extract is under 5 MB, in `matches/` (gitignored). Each report is at most 8 KB in
  `research/matches/`, which is committed: about 120 to 400 reports a day, or 1 to 3 MB a day.
- **Declined.** A runner change could enable `show-indicators=true` for matches that include vibe23 (galaxy's saturn
  passes `-PshowIndicators=false`, so the contest never has indicators). That would put dots and strings into every replica replay of ours, with no shadow compute, and the
  measurements say outcomes would not change. The price:
  - replays about 50% larger;
  - the flag would also record opponents' strings, and a lone surrogate from an opponent would crash that match. An
    engine patch that sanitises strings would remove that risk.

  The orchestrator brings the measured facts to the owner. The bot needs no change for either answer.

---

## 8. Merge order and rollout

1. **Start in parallel.** B and C build against the existing fixtures and the synthetic inputs above. A builds the
   telemetry, calibrates `PADK`, and produces the two `tele-*` fixtures (A.10 item 8).
2. **Merge A, then B, then C**, and run `tools/unit-tests.sh` after each. At the merge, un-skip B.7 item 6 and C.8
   item 6. The suite must pass with 0 skips.
3. **Cost and identity on the VM** (orchestrator): the working line with `C.TELEMETRY` true against false, on the
   174 calibration cells.
   - Expected: 0 overruns and 0 exceptions on both; win rates within noise. Decisions differ only through bytecodes,
     so a small number of discordant pairs is expected.
   - Record the result in `TRAINING_LOG.md`.
   - From then on, every paired gate's control must carry telemetry too: build `c_tele0` = incumbent plus
     `Telemetry.java`.
4. **No submission happens in this work.** Our team's active replica submission is unchanged. The first telemetry
   build is submitted later by the main session, as HANDOFF plans. Until then, our replica replays show `tele=none`
   and the reports carry the replay-only sections.
5. **Before the first submission:** check that `--tele` on a VM-compiled local game reports offset 0. The replica
   compiles on the VM with the same JDK.

---

## 9. Risks and open points

- **PADK depends on the compiler.** If a JDK change moves the overhead, the decoder's sync-based offset (B.3) still
  decodes, and `tele_offset != 0` is reported as an anomaly. Recalibrate A.3 when it happens.
- **Collision of the sync code.** For a non-telemetry team the chance per sync turn is 1/64, so the 0.9 detection
  threshold over at least 10 turns cannot be reached by chance.
- **Robot IDs above 65535** would saturate FIGHT `target`. bc23 ids are far below that, but check it in the
  calibration game.
- **The HQ reason precedence** (A.4) describes a loop that may change. Whoever changes `HQ.build()` must update
  `hqReason` and its test in the same commit.
- **Survey numbers** (bytecode costs, sizes) come from the probe of 2026-10-08. Re-measure after any engine change.
