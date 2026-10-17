# Carrier deaths in lost ranked games (2026-10-16, c_flee1 workflow)

Matches 8190-8237 (submissions 175/176). Written by the c_flee1 diagnosis agent; the judge's implementation spec follows.

## Diagnosis

Our carriers in lost games die mainly because they walk straight back into a raider they just fled. The next biggest cause is the flee step itself, which often heads toward our HQ and through the raiders. Most of these deaths happen at home wells, within r2 34 of our HQ.

**Sample.** 12 lost games from 8 replays (matches 8190-8237, submissions 175/176), deaths by r300 only:
- 8236 g0 Cee, g1 River; 8234 g0 DefaultMap, g2 Turtle; 8235 g1 Quiet (all CyrilSharma)
- 8232 g2 River and 8190 g1 Pakbot (pranayagra)
- 8203 g2 Cornucopia, g5 Hah (georgezhang)
- 8204 g3 DefaultMap, g8 Maze (awesomelemonade)
- 8191 g0 Barcode (GabeG888)

That gives 230 of our carriers killed by launchers by r300, taking 1,806 hits; the opponents lost 95 carriers to 710 hits. Every death is 8 launcher hits (`hp_before` is 10 in 1,567 of 1,593 deaths across all 114 losses), so the real question is why a carrier stays exposed for 8 hits.

**Method.** A one-pass extractor in scratch, built on ReplayDump's classes, gave:
- our BCC state per turn;
- start-of-turn positions for both teams;
- every hit's shooter and target square;
- the map, with vision computed by the cloud rule.

Each hit is charged to the carrier's last decision before it. If the shot landed on its starting square before it moved, that is the previous turn. Opponents' states can't be read, only their positions.

**Mechanisms**

| Mechanism | Share of hits | Share of deaths (main cause) |
|---|---|---|
| RETURN: walks back in right after losing sight of a raider | 40% (722) | 53% (123) |
| INTO: the flee step moves closer to the shooter | 22% (395) | 24% (56) |
| STUCK: fleeing but no move that turn | 12% (217) | 11% (26) |
| AWAY: fled away but was still caught | 11% (193) | 3% (7) |
| FRESH: walked in with no sighting in the last 15 turns | 8% (150) | 3% (7) |
| SEEN: kept working with a launcher in view | 4% (71) | 3% (7) |
| SLOW: fled away while loaded (14 kg or more) | 3% (58) | 2% (4) |

1. **RETURN (flee/return oscillation at home wells).** The carrier was in G, C, W or X, saw no launcher at the start of the turn, but had seen one within 15 turns.
   - When: in 64% of these hits the last sighting was the turn before, and in 93% it was within 3 turns.
   - Where: in 94% the move ended within r2 25 of where it last saw a launcher, and in 73% the shooter was one it had seen. 85% were within r2 34 of our HQ, so the c_well6 hot-well memory (front wells only) never applies.
   - Staying put would have kept it out of the shooter's reach in 58%.
   - Clouds: 28% of these decisions were made standing on a cloud, where vision is r2 4.
   - 78 of 228 deaths show 3 or more one-turn F-G-F, F-C-F or F-W-F flips in their last 30 rounds.
   - Cause in the code: once nothing is visible, `survive()` returns false and `gather()` walks back to the same well. Nothing remembers the threat.
2. **INTO (fled into fire, mostly toward home).** 75% of these hits came on steps toward home. The `moveTo(home)` branch fires when home is farther from the nearest threat than the carrier is, which says nothing about the path. Across INTO and AWAY, 80% had a reachable square out of r2 16 of every visible launcher, yet only 15% ended on one.
3. **STUCK and SLOW (caught slow with cargo).** 68% of stuck hits were on carriers holding 14 kg or more, whose move cooldown is 10 or more. Real cornering is rare: only 17 of 217 had 2 or fewer free neighbouring squares. Separately, 16 deaths (7%) carried cargo while next to our HQ during flee or return turns in their last 15 rounds and never deposited, because `survive()` runs before `deliver()` (159 kg lost).
4. **FRESH (walked in blind)** is only 3% of deaths. It is usually just the first hit before the oscillation starts.
5. **Died at HQ** cuts across all of the above: 71% of deaths were within r2 34 of our HQ and 29% within r2 9. 67% of hits were taken within r2 34 (52% within r2 20). An ally launcher was within r2 20 at 57% of deaths.

**Opponents in the same games**

| | Ours | Theirs |
|---|---|---|
| Carriers dead by r300 | 230/316 | 95/389 |
| Chance of dying once hit | 0.86 | 0.57 |
| Hits taken by carriers that survived | 123 | 215 |
| Carrier turns with an enemy launcher in vision | 9.1% | 3.0% |
| Exposure episodes per carrier | 4.9 | 2.2 |
| Back in view within 10 rounds of leaving it | 73% | 56% |
| Return hits where the sighting was 1 turn earlier | 64% | 15% |
| Dead within 10 rounds of the first hit | 32% | 15% |
| Median r2 to the first shooter's square, 5 rounds after the first hit | 26 | 40 |
| Median r2 to own HQ at the first hit | 32 | 50 |

Their carriers open distance past the launcher's reach and don't come back the next turn. Ours hover at r2 18-29, the edge of vision, which is exactly what a launcher reaches by stepping once and shooting. 60% of their hits came while our launcher was already in their view; we can't see their states.

Caveat: these are losses with the enemy army in our half (3 or more enemy launchers within r2 20 at 45 of 122 RETURN deaths and 44 of 55 INTO deaths). Part of this is a symptom of losing the army fight, but the much lower chance of dying once hit shows carrier behaviour is still a lever.

**Examples**
1. **8236 g1 River, carrier 12513, r184-210 (RETURN, one shooter).** Launcher 11601 parked at (28-30,20-21), 2-3 tiles from our home Ad well; HQ (39,22) is r2 16-65 away. The empty carrier flipped 13 times between (35,22)/(33,23) and (31,22)/(33,21). All 8 hits came from 11601, almost every one on the turn after it walked back in.
2. **8234 g2 Turtle, carrier 13122, r78-121 (RETURN, one shooter, 7 episodes).** Launcher 14055 sat at (0-1,24-27) beside an Ad well about 6 tiles from HQ (6,29) for 40+ rounds. The carrier looped HQ to (3,24) and back every 4-6 rounds, taking 1 hit per visit, with 0-3 of our launchers within r2 20.
3. **8203 g5 Hah, carrier 12477, r193-212 (RETURN through a cloud).** Home Mn well (14,11), HQ (10,7), launchers 10036 and 12063 2-3 tiles from the well. The pattern was collect, get hit, step back to the cloud column x=12 (vision r2 4) where the launchers vanish, step back and collect. It flipped between C and F 9 times, threw its 16 kg at r208, still came back, and died at r212. Six of our launchers were within r2 20 at r193.
4. **8236 g1 River, carrier 10390, r156-159 (INTO toward home).** Hit at (31,24) by 10975 at (33,21). Home (39,22) is r2 37 from the threat versus 13 for the carrier, so it took the `moveTo(home)` branch to (33,22), r2 5 from 10975 and 11601. It took 7 hits in r157-159.
5. **8234 g0 DefaultMap, carrier 10178, r34-47 (SLOW plus no deposit).** Carrying 30 Mn, it fled to HQ (25,18) and sat next to it (r2 1-2) in r38-40 without depositing. At 30 kg its move cooldown is 16, so it could only move about every other turn. It took 8 hits among 5-7 launchers and died with the 30 Mn.

**The single change I expect to save the most carriers: a short threat memory with a stand-off ring, home wells included.**
- In `survive()`, store every visible enemy launcher or destabilizer location and the round (a ring of 4-6 entries).
- For the next ~6 rounds, a carrier in G, C, W, X or R does not end a move within r2 36 of a stored position. That includes collecting on a well inside the ring: it waits at the safest reachable square instead.
- After a second flee from the same well within ~30 rounds, that carrier drops the well for itself only (a home-well version of `hotLocal`, with no shared mark).
- Cost is about 1-2k bytecodes, only while the memory is live; the carrier limit is 12,500.

Expected effect: it targets the 40% of hits and 53% of deaths in RETURN; 119 of 230 deaths had 3 or more such hits. My realistic estimate is 25-35% fewer carrier deaths by r300 in losses, about 3.5-5 of the 14 per game.

How it differs from c_flee3, which was rejected at net -4 (panel 56/100, p 0.22): c_flee3 used a 40-round memory, dropped wells within r2 36 and held carriers near the HQ. The data say about 6 rounds covers 93% of return hits, so the carrier resumes as soon as the raider moves on.

Next in line, in the same function:
- Score the flee step by the largest minimum r2 to all visible and remembered fighters, using home only as a tie-break. This targets the 22% of hits and 24% of deaths in INTO.
- Deposit first when next to an HQ.
- Consider throwing early to lighten a loaded carrier that is being hit.

Files are in `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/flee-diag/`:
- `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/flee-diag/src/replaydump/FleeDiag.java` — the one-pass extractor
- `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/flee-diag/d/<match>_<game>/` — per-game extracted data
- `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/flee-diag/hits.py`, `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/flee-diag/hits.json`, `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/flee-diag/final.py` — hit table and mechanism summary
- `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/flee-diag/surv.py`, `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/flee-diag/after.py` — the opponent comparison
- `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/flee-diag/tl.py` — timeline printer: `python3 -I tl.py <match> <game> <id> <rounds>`

## c_flee1 spec (judge)

**Scores** (1-10, higher is better; "income" and "risk" are scored so that 10 means cheapest and safest)

| | Carriers saved (by death share) | Income cost on safe maps | Implementation risk | Simplicity | Total |
|---|---|---|---|---|---|
| A (memory) | 7 | 5 | 6 | 4 | 22 |
| B (flight) | 8 | 8 | 7 | 7 | **30** |
| C (warning) | 6 | 6 | 4 | 4 | 20 |

Why:
- **B covers the most deaths.** It handles RETURN (53%) with a memory flight and a stand-off. It handles INTO (24%) with the only flee-step scorer that counts several fighters at once. It handles STUCK and SLOW (13%) with lightening and deposit-first. Its weak spot is a raider that stays parked: the cycle stretches to one hit every 6-8 rounds but does not stop.
- **A** is strong on RETURN, and it is the only design that drops a raided home well (110 of 228 deaths came after a second flight). Its INTO filter checks one step at a time and it has nothing for slow, loaded carriers. `dzKeep` plus `standOff` brings back c_flee3's at-home wait (up to 40 rounds), which is what lost c_flee3 its panel.
- **C's board** targets FRESH, which is 3% of deaths. It also adds about 100 bytecodes to every carrier turn, an HQ change, island slots 52-55 reused, and holds during sieges.

**Claims checked against the c_gp1 code**
- Confirmed:
  - `return moved || bd <= 20` is always true when a fighter is in view.
  - `survive()` runs before `deliver()`.
  - `moveTwice` does not re-sense between its two moves.
  - Hot wells are front wells only, and `fledFrom` is only used for the report.
  - `unjam` and `packStep` call `rc.canMove` directly, so neither is filtered.
  - Every Nav path (greedy, sidestep, field descent, wall-following, `moveAway`) goes through `can()`.
  - Island loops stop at min(35, count), and `flushIslands` only flushes ids it has seen, so C's slot claim holds.
  - `getMovementCooldownTurns` exists in the 3.0.15 jar.
  - Cloud move cost is round(base×1.2), with no x.5 cases.
- **Pitfall for B's hook:** `Nav.avoid` is set only by launchers, and `can()` returns at `if (!avoid) return true;`. The danger check must sit between `canMove` and that line.
- **B bugs:**
  - Its `ghostAt` veto blocks outward steps too, which freezes a carrier inside a ring after `fleeMove` fails.
  - Its veto rescans all 6 slots on every `can()` call.
  - `slot()` can overwrite an entry written this round.
  - Its unhurt "bd ≤ 16" throw goes beyond the evidence: the 84% death figure is for carriers already hit.
- **A overstates:** a refused step is treated "like a robot" only when none of dir/a/b is a wall. Otherwise the carrier wall-follows and calls `Field.request`.
- **C is doubtful:** it says the home-well drop "comes free" through crowd patience, but W ticks only at 2 < d ≤ 8 from the well. A carrier held at r2 26 from a launcher 2-3 tiles off the well is mostly beyond r2 8 of it.

---

# FINAL SPEC: c_flee1 = B (scored flight + 4-round memory + stand-off + deposit + lighten), with grafts

Grafts:
- From A: drop the well after a second flight (home wells included, local only, with a far guard and no home wait), a ghost on the carrier's own square when it is hit with nothing in view, and the live list computed once per turn.
- From C: the strictly-outward rule, `unjam` and `packStep` routed through `Nav.can`, and the indicator counters.

Base: copy `src/c_gp1` to `src/c_flee1` and change every file to `package c_flee1;`. With `C.FLEE1 = false` the bot behaves exactly like c_gp1. The new code makes no RNG draws, writes no shared slots and does not touch HQ or Launcher code.

## 1. C.java (new block at the end)
```java
/** c_flee1: carrier flight. 4-round memory of enemy fighters; flight continues while within r2 FLEE1_STAND of a
 *  sighting; no other move ends within FLEE1_STAND of one unless strictly outward; the flee step is scored over every
 *  visible and remembered fighter; deposit first next to an HQ; a hit carrier with 14 kg or more throws its load;
 *  after a second flight from the same well within FLEE1_REPEAT rounds the carrier drops the well (home wells
 *  included) for FLEE1_AVOID rounds unless the alternative is far. */
public static final boolean FLEE1 = true;
public static final boolean FLEE1_MOVE = true, FLEE1_MEMORY = true, FLEE1_BANK = true, FLEE1_LIGHTEN = true, FLEE1_DROP = true;
public static final int FLEE1_MEM = 4;          // rounds a sighting stays live (93% of return hits within 3 turns)
public static final int FLEE1_N = 6;            // memory slots (at most FLEE1_N fighters stored per turn)
public static final int FLEE1_STAND = 36;       // r2: THREAT_R2 26 plus one launcher step
public static final int FLEE1_NEAR_R2 = 80;     // live list radius: >= (sqrt(STAND) + 2*sqrt(2))^2 = 77.9
public static final int FLEE1_MERGE_R2 = 4;     // the same fighter one step later
public static final int FLEE1_LIGHT_W = 14;     // at 14 kg a carrier makes 1 move a turn or fewer
public static final int FLEE1_HURT = 10;        // rounds since the last HP loss that count as "being shot"
public static final int FLEE1_WELL_R2 = 64, FLEE1_REPEAT = 30, FLEE1_AVOID = 40, FLEE1_ALT_D2 = 100;
public static final int FLEE1_MIN_LEFT = 2500;  // fleeMove stops scoring below this many bytecodes left
public static final int FLEE1_GUARD = 3000;     // no two-step expansion below this many left
public static final int FLEE1_NAV_GUARD = 1500; // Nav.can stand-off filter off below this many left
```

## 2. Nav.java
New fields: `static boolean danger; static final int[] ringX = new int[C.FLEE1_N], ringY = new int[C.FLEE1_N]; static int ringN; public static int ringBlocks;`

```java
/** c_flee1 (pure): the step (hx,hy)->(nx,ny) ends within r2 C.FLEE1_STAND of one of the n points and is not strictly
 *  farther from it (inward and sideways steps are refused, outward ones allowed). */
static boolean ringBlocks(int hx, int hy, int nx, int ny, int[] lx, int[] ly, int n) {
    for (int k = n; --k >= 0; ) {
        int ax = nx - lx[k], ay = ny - ly[k], dn = ax * ax + ay * ay;
        if (dn <= C.FLEE1_STAND) { int bx = hx - lx[k], by = hy - ly[k]; if (dn <= bx * bx + by * by) return true; }
    }
    return false;
}
```
In `can(d)`, immediately after `if (!G.rc.canMove(d)) return false;` and **before** `if (!avoid) return true;`:
```java
if (danger && ringN > 0 && Clock.getBytecodesLeft() > C.FLEE1_NAV_GUARD) {
    MapLocation h = G.rc.getLocation();
    if (ringBlocks(h.x, h.y, h.x + d.dx, h.y + d.dy, ringX, ringY, ringN)) { ringBlocks++; return false; }
}
```
`danger` is only ever set by carriers, so launchers pay one boolean test per call.

## 3. Carrier.java

New fields:
```java
static final int[] gx = new int[C.FLEE1_N], gy = new int[C.FLEE1_N], gr = new int[C.FLEE1_N];  // gr 0 = empty
static final int[] tx = new int[8], ty = new int[8];                                          // fleeMove threats
static int memUntil = -1, lastHp = 150, hurtRound = -100;
static MapLocation fWell, badAt; static int fWellRound = -1000, fRole, badUntil, badD2; static boolean badKeep;
public static int memFlights, lightens, drops;   // diagnostics
static final ResourceType[] DEPOSIT = {ResourceType.ADAMANTIUM, ResourceType.MANA, ResourceType.ELIXIR};
```

**run()**
- Add `Nav.danger = false;` as the first statement.
- After `reportEnemies();` add `if (C.FLEE1) memTurn();`.

**memTurn / remember / memAdd**
```java
static void memTurn() throws GameActionException {
    int hp = G.rc.getHealth();
    if (hp < lastHp) {
        hurtRound = G.round;
        if (C.FLEE1_MEMORY && G.nEnemyFighters == 0) memAdd(G.here.x, G.here.y);   // shooter unseen (cloud, r2 4)
    }
    lastHp = hp;
    if (C.FLEE1_MEMORY && G.nEnemyFighters > 0) remember();
    Nav.ringN = !C.FLEE1_MEMORY || G.round > memUntil ? 0
        : liveNear(gx, gy, gr, G.round - C.FLEE1_MEM, G.here.x, G.here.y, C.FLEE1_NEAR_R2, Nav.ringX, Nav.ringY);
}
static void remember() {
    for (int i = G.enemies.length, m = 0; --i >= 0 && m < C.FLEE1_N; ) {
        RobotInfo e = G.enemies[i];
        if (e.type != RobotType.LAUNCHER && e.type != RobotType.DESTABILIZER) continue;
        m++;
        if (!memAdd(e.location.x, e.location.y)) break;
    }
}
static boolean memAdd(int x, int y) {
    int k = slot(gx, gy, gr, x, y, G.round);
    if (k < 0) return false;
    gx[k] = x; gy[k] = y; gr[k] = G.round; memUntil = G.round + C.FLEE1_MEM;
    return true;
}
```

Pure helpers (unit-tested):
```java
/** pure: the slot of a stored sighting within r2 FLEE1_MERGE_R2 not written this round (the same fighter, moved), else
 *  the oldest slot not written this round (empty first); -1 when every slot was written this round. */
static int slot(int[] gx, int[] gy, int[] gr, int x, int y, int r) {
    int k = -1, old = r;
    for (int j = gr.length; --j >= 0; ) {
        if (gr[j] == r) continue;
        int dx = gx[j] - x, dy = gy[j] - y;
        if (gr[j] > 0 && dx * dx + dy * dy <= C.FLEE1_MERGE_R2) return j;
        if (gr[j] < old) { old = gr[j]; k = j; }
    }
    return k;
}
/** pure: copies the entries seen at rounds >= r0 (gr > 0) within r2 near of (x,y) into (lx,ly); returns the count. */
static int liveNear(int[] gx, int[] gy, int[] gr, int r0, int x, int y, int near, int[] lx, int[] ly) {
    int n = 0;
    for (int j = gr.length; --j >= 0; ) {
        if (gr[j] <= 0 || gr[j] < r0) continue;
        int dx = gx[j] - x, dy = gy[j] - y;
        if (dx * dx + dy * dy <= near) { lx[n] = gx[j]; ly[n++] = gy[j]; }
    }
    return n;
}
/** pure: index of the point nearest (x,y) within r2 FLEE1_STAND, or -1. */
static int ghostAt(int x, int y, int[] lx, int[] ly, int n) {
    int bd = C.FLEE1_STAND + 1, b = -1;
    for (int k = n; --k >= 0; ) { int dx = x - lx[k], dy = y - ly[k], d = dx * dx + dy * dy; if (d < bd) { bd = d; b = k; } }
    return b;
}
/** pure, larger is safer: fewer shots (4 per fighter within r2 16, 2 within THREAT_R2, 1 within FLEE1_STAND), then the
 *  larger least r2 to a fighter (capped at STAND+1), then nearer (hx,hy). n <= 8. */
static int fleeScore(int x, int y, int[] tx, int[] ty, int n, int hx, int hy) {
    int danger = 0, mn = C.FLEE1_STAND + 1;
    for (int j = n; --j >= 0; ) {
        int dx = x - tx[j], dy = y - ty[j], d = dx * dx + dy * dy;
        if (d <= C.FLEE1_STAND) { danger += d <= 16 ? 4 : d <= C.THREAT_R2 ? 2 : 1; if (d < mn) mn = d; }
    }
    int dh = (x - hx) * (x - hx) + (y - hy) * (y - hy);
    return ((64 - danger) << 20) + (mn << 13) + 8191 - (dh < 8191 ? dh : 8191);
}
static int moveCost(int w, boolean cloud) { int b = (int) (0.375f * w) + 5; return cloud ? (b * 12 + 5) / 10 : b; }
static boolean shouldLighten(int w, int anchors, int bd, int round, int hurt) {
    return w >= C.FLEE1_LIGHT_W && anchors == 0 && bd <= C.THREAT_R2 && round - hurt <= C.FLEE1_HURT;
}
/** pure: an alternative at r2 altD2 from our nearest HQ is too far to replace a raided well at r2 raidD2. */
static boolean farAlt(int altD2, int raidD2) { return altD2 > Math.max(C.FLEE1_ALT_D2, 4 * Math.min(raidD2, 10000)); }
```

**fleeMove** (stay, one step or two steps, with per-iteration bytecode guards)
```java
static boolean fleeMove(MapLocation home) throws GameActionException {
    RobotController rc = G.rc;
    if (!rc.isMovementReady()) return false;
    int n = 0, r0 = G.round - C.FLEE1_MEM;
    for (int i = G.enemies.length; --i >= 0 && n < 8; ) {
        RobotInfo e = G.enemies[i];
        if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) { tx[n] = e.location.x; ty[n++] = e.location.y; }
    }
    for (int j = C.FLEE1_N; --j >= 0 && n < 8; )        // this round's entries repeat visible ones, except a cloud ghost
        if (gr[j] > 0 && gr[j] >= r0 && (gr[j] != G.round || G.nEnemyFighters == 0)) { tx[n] = gx[j]; ty[n++] = gy[j]; }
    if (n == 0) return false;
    MapLocation here = rc.getLocation();
    int hx = home == null ? here.x : home.x, hy = home == null ? here.y : home.y;
    int w = rc.getWeight(), cd = rc.getMovementCooldownTurns();
    boolean two = cd + moveCost(w, false) < 10;
    int best = scoreAt(here.x, here.y, n, hx, hy);
    Direction b1 = null, b2 = null;
    for (int i = 8; --i >= 0; ) {
        int left = Clock.getBytecodesLeft();
        if (left < C.FLEE1_MIN_LEFT) break;
        if (left < C.FLEE1_GUARD) two = false;
        Direction d = G.DIRS[i];
        if (!rc.canMove(d)) continue;
        int ax = here.x + d.dx, ay = here.y + d.dy, s = scoreAt(ax, ay, n, hx, hy);
        if (s > best) { best = s; b1 = d; b2 = null; }
        if (!two || cd + moveCost(w, MapMem.cloud(ax, ay)) >= 10) continue;
        for (int k = 3; --k >= 0; ) {
            Direction e = k == 2 ? d : k == 1 ? d.rotateLeft() : d.rotateRight();
            int cx = ax + e.dx, cy = ay + e.dy;
            if (!G.onMap(cx, cy) || MapMem.isWall(cx, cy) || rc.canSenseRobotAtLocation(new MapLocation(cx, cy))) continue;
            s = scoreAt(cx, cy, n, hx, hy);
            if (s > best) { best = s; b1 = d; b2 = e; }
        }
    }
    if (b1 == null) return false;
    rc.move(b1);                                    // canMove(b1) checked this turn, nothing changed since
    if (b2 != null && rc.canMove(b2)) rc.move(b2);
    G.here = rc.getLocation();
    return true;
}
static int scoreAt(int x, int y, int n, int hx, int hy) {     // (x,y) on the map by construction
    Direction c = MapMem.current(x, y);
    if (c != Direction.CENTER && G.onMap(x + c.dx, y + c.dy) && !MapMem.isWall(x + c.dx, y + c.dy)) { x += c.dx; y += c.dy; }
    return fleeScore(x, y, tx, ty, n, hx, hy);
}
```

**bank / lighten**: as in B, with these guards:
- `bank` returns false when home is null, weight is 0, the carrier holds an anchor, the action is not ready, or home is farther than r2 2. On weight 0 it applies deliver's trip accounting: `returning = false`, `trips++`, `Telemetry.trip`.
- `lighten` aims at the threat if `canAttack`. Otherwise it aims at `G.here.add(G.here.directionTo(t))` if `canAttack`. Then `throwsMade++; lightens++; returning = false;`.

**survive()** (changes only)
```java
if (G.nEnemyFighters == 0) return C.FLEE1 && C.FLEE1_MEMORY && ghostFlee();
... threat selection and c_guard1 unchanged ...
boolean site = C.MID && well != null && G.here.distanceSquaredTo(well) <= C.MID_AREA_R2 && Mid.isSite(well);
if (site) { /* c_mid1's two lines unchanged */ }
if (C.FLEE1 && C.FLEE1_DROP && !site) noteFlight(threat.location);
... c_well6 hot block unchanged ...
int w = rc.getWeight(), w0 = w;                     // w0 goes to emitFlee as before
boolean threw = false;
MapLocation home = HQState.nearest(G.here);         // moved above the throw: the same single RNG draw
if (C.FLEE1 && C.FLEE1_BANK && bank(home)) w = rc.getWeight();
if (C.FLEE1 && C.FLEE1_LIGHTEN && shouldLighten(w, rc.getNumAnchors(null), bd, G.round, hurtRound)
    && lighten(threat.location)) { threw = true; w = 0; }
if (!threw && w >= 8 && bd <= 9 && rc.getHealth() <= 60 && rc.canAttack(threat.location)) { /* old throw */ }
boolean moved;
if (C.FLEE1 && C.FLEE1_MOVE && Clock.getBytecodesLeft() > C.FLEE1_MIN_LEFT + 500) {
    moved = fleeMove(home);
    if (moved && C.FLEE1_BANK && !threw) bank(home);
} else { /* c_gp1 lines 227-235 verbatim */ }
// telemetry (emitFlee with w0) and `return moved || bd <= 20` unchanged
```

**ghostFlee** (flight continues after losing sight)
```java
static boolean ghostFlee() throws GameActionException {
    if (Nav.ringN == 0) return false;
    if (C.MID && G.nAllyFighters > 0 && well != null && G.here.distanceSquaredTo(well) <= C.MID_AREA_R2 && Mid.isSite(well)) return false;
    Nav.danger = true;                                    // every later move this turn keeps the stand-off
    int g = ghostAt(G.here.x, G.here.y, Nav.ringX, Nav.ringY, Nav.ringN);
    if (g < 0) return false;                              // outside every ring: work, never step in
    MapLocation home = homeOf(G.here), gl = new MapLocation(Nav.ringX[g], Nav.ringY[g]);   // no RNG
    if (C.FLEE1_BANK) bank(home);
    boolean moved = C.FLEE1_MOVE && Clock.getBytecodesLeft() > C.FLEE1_MIN_LEFT + 500 ? fleeMove(home) : Nav.moveAway(gl);
    if (!moved) return false;                             // collect or deposit as usual; the veto still holds
    if (C.FLEE1_BANK) bank(home);
    fled++; memFlights++;
    if (C.TELEMETRY && prevState != 'F' && prevState != 'V')
        Telemetry.emitFlee(G.here.distanceSquaredTo(gl), 0, G.rc.getHealth(), false, true, Telemetry.loc12(gl),
            G.rc.getWeight(), Telemetry.loc12(home), G.round);    // ef 0 = a flight from memory
    return true;
}
```

**Second-flight drop (graft from A)**
```java
static void noteFlight(MapLocation t) throws GameActionException {
    if (well == null || prevState == 'F' || prevState == 'V' || well.distanceSquaredTo(t) > C.FLEE1_WELL_R2) return;
    if (well.equals(fWell) && G.round - fWellRound <= C.FLEE1_REPEAT) {
        badAt = t; badUntil = G.round + C.FLEE1_AVOID; badKeep = false; badD2 = minD2(well, HQState.ourHQs); drops++;
    }
    fWell = well; fWellRound = G.round; fRole = role;
}
```
- `hotLocal(l)`, after the c_mid1 line:
  `if (C.FLEE1 && G.round < badUntil && !badKeep && l.distanceSquaredTo(badAt) <= C.FLEE1_WELL_R2) return true;`
- `anyHot()`, first line:
  `if (G.round < hotUntil || (C.FLEE1 && G.round < badUntil && !badKeep)) return true;`
- `gather()`, after both well-pick blocks and before `if (well == null) { state = 'X'; ...`:
  ```java
  if (C.FLEE1 && G.round < badUntil && !badKeep && fWell != null && role == fRole
      && (well == null || farAlt(minD2(well, HQState.ourHQs), badD2))) { well = fWell; badKeep = true; }
  ```
  When there is no near alternative, the carrier keeps the raided well. There is no home wait; the memory and the stand-off guard it.

**Other edits**
- `unjam()`: `G.rc.canMove(d)` becomes `Nav.can(d)`. While a ring is live this filters the random step instead of turning unjam off.
- `packStep()`: `rc.canMove(dir)` becomes `Nav.can(dir)`.
- `moveTwice(t)`: before each `Nav.moveTo(t)` add the hold below. It holds rather than wall-following around a ring.
  ```java
  if (Nav.danger && Nav.ringN > 0) {
      MapLocation s = G.rc.getLocation();
      Direction d = s.directionTo(t);
      if (d != Direction.CENTER && Nav.ringBlocks(s.x, s.y, s.x + d.dx, s.y + d.dy, Nav.ringX, Nav.ringY, Nav.ringN)) return;
  }
  ```
- `note()`: when `C.FLEE1` and a counter changed (use a dirty flag, so the string is not rebuilt every turn), set
  `G.extra = ",mf=" + memFlights + ",rb=" + Nav.ringBlocks + ",lt=" + lightens + ",dw=" + drops;`. Keep the indicator under 64 characters.
- docs/TELEMETRY.md: a FLEE record with `enemy_fighters = 0` is a flight from memory. No state letters change.

## 4. Bytecodes (carrier limit 12,500; estimates, to be checked with near misses)

| Turn | Added cost |
|---|---|
| No sighting in the last 4 rounds, no hit | about 20: `getHealth`, two compares, `ringN = 0`, one `danger` test per `can()` |
| `memTurn` with fighters in view | at most 6 × ~100 (`remember`) + ~120 (`liveNear`) |
| `fleeMove` with n threats | about 650 + 200n for one step; about 2.3k + 800n for two steps |
| `Nav.can` filter while a ring is live | about 25 per live point per call |
| Drop | one `nearestCool` (~2.2k) on the first gather turn after a second flight |

- The loop checks bytecodes left on every iteration: below 3,000 it stops expanding second steps, below 2,500 it stops scoring. So `fleeMove` always leaves at least about 2,200, which keeps the turn's work under 10.3k and below the 11,250 near-miss bar.
- If fewer than 3,000 are left at entry, the c_gp1 flight runs instead.
- The Nav filter switches off below 1,500 left.
- New code adds no map loops, no sensing calls (the only call is `canSenseRobotAtLocation`, 5 bytecodes) and no shared writes.

## 5. Exception and off-map safety
- `rc.move(b1)` follows `canMove(b1)` in the same turn; `b2` is checked with `canMove`.
- `MapMem.cloud(ax, ay)` only runs after `canMove(d)`, so the square is on the map.
- `isWall(cx, cy)` only runs after `G.onMap`; `scoreAt` checks `onMap` before reading the pushed square.
- `attack` follows `canAttack`, and the aim square lies between two on-map squares.
- Transfers follow `canTransferResource`.
- Nulls: `home` null is handled; `badAt` is only read while `badUntil > round`; `fWell` is checked for null.
- `minD2` returns MAX when there is no HQ; it is capped at 10,000 before ×4.
- Empty slots (`gr == 0`) are never live, which matters for rounds up to `FLEE1_MEM`.

## 6. test/bot/Flee1Test.java (package c_flee1, `main()` with `check(cond, msg)`, `System.exit(1)` on a failure, as in Gp1Test)
1. **Knobs:**
   - `C.FLEE1` is on.
   - `FLEE1_STAND >= C.THREAT_R2`.
   - `FLEE1_NEAR_R2 >= 78`.
   - `FLEE1_N <= 8`.
   - `8*4 < 64`, and `(FLEE1_STAND+1) < 128`, so the score packing cannot overflow.
   - `FLEE1_MIN_LEFT < FLEE1_GUARD`.
2. **`fleeScore`, River r157 (8236 g1, carrier 10390):** carrier (31,24), threat (33,21), home (39,22). Assert score(29,26) > score(31,24) > score(33,22). (33,22) is c_gp1's actual choice, r2 1 from the shooter.
3. **`fleeScore` danger order:** a square at r2 10 (in reach) < one at r2 20 < one at r2 30 < one at r2 40 (clear), same home distance.
4. **`fleeScore` two fighters vs one:** a square within r2 16 of two fighters but nearer home ranks below a square within r2 16 of one.
5. **`fleeScore` ties:**
   - equal danger, the larger least r2 wins even when it is farther from home;
   - among clear squares, the one nearer home wins.
6. **`slot`:**
   - a fighter that moved 1 tile (r2 ≤ 4) reuses its slot;
   - two fighters seen in the same round within r2 4 take two slots;
   - an empty slot is used before the oldest live one;
   - a full ring replaces the oldest;
   - it returns -1 when all slots were written this round;
   - an empty slot at (0,0) does not merge with a fighter at (1,1) that is already stored elsewhere.
7. **`liveNear`:**
   - age `FLEE1_MEM` is included and `FLEE1_MEM + 1` excluded;
   - `gr = 0` is never live at round 3, where r0 = -1;
   - entries beyond `FLEE1_NEAR_R2` are excluded;
   - the count is right.
8. **`Nav.ringBlocks`** with the point at (10,10):
   - an inward step (13,10)→(12,10) is blocked;
   - an outward step (12,10)→(13,10) is allowed;
   - a sideways step at equal r2 inside the ring is blocked;
   - a step ending at r2 37+ is allowed;
   - n = 0 never blocks.
9. **`ghostAt`:** returns the nearest index within r2 36, and -1 at r2 37.
10. **`moveCost`:** (0,F)=5, (13,F)=9, (14,F)=10, (30,F)=16, (40,F)=20, (0,T)=6, (30,T)=19.
11. **`shouldLighten`:**
    - false at 13 kg, with an anchor, at bd 27, or 11 rounds after a hit;
    - true at 14 kg, bd 26, hit 10 rounds earlier.
12. **`farAlt`:**
    - raided well at r2 25: an alternative at 90 is near, at 120 is far (bar 100);
    - raided at 400: bar 1,600;
    - raided at `Integer.MAX_VALUE`: bar 40,000, with no overflow.

## 7. Evaluation (screen vs c_gp1, then `trial-start`)
Judge on:
- carrier deaths by r300 in losses (now 14.0);
- one-turn F-G-F, F-C-F and F-W-F flips per death;
- first collections and deposits per carrier (LEARNINGS: a veto can turn a short cycle into a longer one that collects nothing);
- Mn and Ad by r300 in wins (must stay within -2%);
- `mf`, `rb`, `lt` and `dw` from the indicator;
- near misses, and zero exceptions and overruns.

Screen opponents: the c_gp1 mirror, arch_swarm (siege), horde and blob. If the result is neutral, A/B the sub-knobs `FLEE1_DROP` and `FLEE1_LIGHTEN` first.

**Expected:** carrier deaths by r300 in lost games from 14.0 to about 9.5 (range 8.5-11); in won games from 3.8 to about 3.2. With no sighting the cost is zero; in wins, under 2% of carrier work turns.

**Known gaps:**
- Edges and dead ends get no penalty in `fleeScore`.
- No enemy HQ aura term.
- A drop may send a carrier to an off-type well until the deposit re-pick.
- Couriers get the scored flight but not the memory flight.
