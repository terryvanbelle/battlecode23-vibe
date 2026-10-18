# Launcher micro vs strong bots: verified findings, mechanisms and ranked changes (src/c_hr1, panel 20261017-212413)

Our per-launcher micro trades as well as the strong bots' does. We lose because more of our ahead or par fights turn into fights where the enemy brings more launchers, and that follows army size, not shot-level micro. The micro levers I found are all small: at best about 1 game in 100 against strong bots. I give the top two as build plans because they target real, measured losses at low risk.

Scope: data are the 10 matches 8823..8832 (100 games, vibe23 always side A). "Strong" means jmerle, awesomelemonade, vrangr1, pranayagra and NotLLeon.

Three extra sources:
- **Per-turn, 7 strong-bot losses:** both sides' per-turn data for the 7 lost case games: (8823,4) Forest, (8824,8) Maze, (8826,5) Hah, (8826,7) MassiveL, (8827,0) BatSignal, (8827,9) ReverseFunnel, (8828,1) Cat.
- **jmerle per-turn set:** 240 games of earlier builds against jmerle (`research/clone/jmerle`).
- **Code:** c_hr1's source.

"R" marks a number I recomputed myself. My scripts are in `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/micro/verify/` (v1.py to v35.py, plus cl_*.txt, bh_*.txt, ours_band.csv and jm_band.csv). No repo files were changed, and no JVM or game was run.

## 1. Merged and verified claims

### Claims that hold

| # | Claim | Numbers I re-checked |
|---|---|---|
| S1 | **Concentration decides fights.** At the same peak-count difference, our launcher exchange in lost games matches won games. | Strong opponents, LvL par and ahead, r0 ≤ 300:<br>• Lost games: n172, engagements won 0.40, launcher exchange (Lexch) 0.94.<br>• Won games: n192, 0.69 and 1.40.<br>• Reweighting by peak difference closes 66% of the gap (89% at r0 ≤ 600).<br>• Lexch lost/won by peak difference: ≤−1: 0.71/0.75; 0: 0.98/0.88; 1: 1.12/1.33; 2: 1.39/1.39; ≥3: 1.49/1.70 (v26). |
| S1a | **Turned fights.** Fights where the enemy's peak count exceeds ours (pdiff ≤ −1) hold our deaths. | • 46 of 172 such fights in lost games (27%), against 18 of 192 in won games (9%).<br>• They hold 400 of our 874 early launcher deaths (46%), at Lexch 0.71.<br>• At death, only 18% of those launchers saw themselves outnumbered (H/F mode with the 'o' flag); in held fights it was 7% (v27). |
| S2 | **Per-shot micro is at parity.** | • First hit, strong par: we hit first 0.35, they hit first 0.36.<br>• Damage per kill: 245 (theirs) / 255 (ours) in lost games, 251/263 in won.<br>• Entering range from a cloud: we hit 0.45 per entry, jmerle 0.41 (jm_band).<br>• In-range hit rate over 240 games: off a cloud 0.95 vs 0.98; on a cloud 0.28 vs 0.26 (cl_*). |
| S3 | **Carriers explain the value gap at home.** | • Strong par-home: carriers lost 93 vs 2, launcher exchange 1.17 (136/159).<br>• Carriers lost before r100: 186 vs 80 in lost games, 110 vs 277 in won games. |
| S4 | **Production diverges from r100, while the launcher trade stays even (about 1.0 in every phase).** | Launchers built, lost games: r200 38.3 vs 43.3; r300 52.4 vs 66.8. Alive at r300: 13.2 vs 27.6. |
| S5 | **Fights we lead and then lose (code lens).** | Lost games, ahead-mid fights: 23 caught up (deaths 185 ours / 170 theirs, exchange 0.71) against 72 that kept the lead (38/58, 2.40). |
| S6 | **Cloud idling, adjusted to MassiveL only.** | • (8826,7,18): 55 of our 89 in-range turns had no hit, all on a cloud; theirs 5 of 63.<br>• Early hits taken on a cloud from an enemy we cannot see: MassiveL 68 ours vs 0 theirs; Forest 30 vs 26; all other case games 0 to 6 (v32).<br>• Panel-wide this is 2.6 vs 2.0 per game (bh_*). |

### Claims adjusted

- **"Enemy reinforces our ahead fights more in lost games."** The relative inflow is the same in lost and won ahead fights: enemy joiners minus ours are +1.74 vs +1.72 (v25).
  - What differs is the starting lead: nA0 − nB0 is 3.49 in lost games vs 5.43 in won.
  - At par the reinforcement race does flip: the enemy out-joins us by 1.28 in lost games, and we out-join them by 1.51 in won games.
- **"Blind entries into range."** On clouds our launchers enter range without firing more often (0.149 of band turns vs jmerle 0.028). It is not a hit gap: 213 of jmerle's 400 entry shots hit nothing, and entry hit rates are 0.45 vs 0.41.

### Claims rejected

- **"Kite to r2 > 26."** One step from r2 ≤ 16 reaches at most r2 26; the measured kite distance is 17-26.
- **Fire-share gap.** It disappears off clouds (94% vs 93%).
- **Maze as a numbers-neutral control.** It is not neutral: launchers in the box were 2.1 vs 7.1.
- **Kill conversion from the 7 hand-picked fights** (360 vs 395 launcher hits, 22 vs 43 deaths). Those fights were chosen by outcome; panel-wide damage per kill is equal (S2).
- **"They converge via comms."** jmerle and awesomelemonade build 0 amplifiers. We are in write range on only 10 of 464 F/H turns. A launcher just outside vision (r2 21-34) of an enemy fighting an ally moves closer 0.29 vs 0.28 and into vision 0.20 vs 0.21 (n 1500 vs 1329, v30).
- **Support gap.** With a damaged ally within r2 20 and no enemy in vision: ours stay 0.53, closer 0.29, farther 0.16; theirs 0.60, 0.27, 0.10 (n 502 / 524, v24).
- **Wounded-behaviour gap.** The lens's own numbers are similar: closer/farther 38%/59% ours vs 34%/64% theirs.
- **"jmerle blind fire is worth about 570 damage a game."**
  - From a cloud in the 17-20 band, jmerle fired 974 shots for 16 hits (2%).
  - Its in-range cloud hit rate (0.26) is no better than ours (0.28).
- **Step-in onto our just-moved launcher.** It happened 43 of 129 times, not 109 as the lens said. Engagement win rate is 0.74 vs 0.75, so it does not predict the result.

## 2. Mechanisms

1. **Fight selection and concentration (the dominant cause).** Strong bots do not out-trade us launcher for launcher.
   - More of our ahead or par fights turn: 27% vs 9%, holding 46% of our early deaths.
   - At par, the side with more launchers nearby wins the reinforcement race.
   - Ahead fights in lost games start with smaller leads.
   - This follows army size (S4) and positions. It is not a response gap: launchers outside vision react the same on both sides.
2. **Strong bots erase our edge over weak bots.** At equal peak difference, strong bots hold us to Lexch 0.88-0.98 at pdiff 0 and 1.12-1.39 at pdiff 1-2. Weak bots give up 1.19 and 1.59-1.71.
3. **Carrier losses at home** carry the value deficit in par-home fights (S3).
4. **Clouds, map by map.** On MassiveL we fight from clouds and get hit by enemies we cannot see (68 vs 0). jmerle and awesomelemonade spend zero in-range turns on clouds there. Forest is the opposite: jmerle spends 42% of in-range turns on clouds, and our off-cloud hit rate there drops to 0.80.
5. **A residual state-level loss.** Our 'ahead' test counts only fighters in vision. With a 4-round memory emulated (v33/v34):
   - Step-ins the memory would flip die within 4 rounds 0.44 of the time (n48, net −11.2 HP), against 0.18 for step-ins it keeps (n520).
   - Standing in range in flip states dies 0.37, against 0.19.
   - The strong side does no better in these states (step-in net −22.3), so fixing this goes past parity rather than copying them.
   - Only 7% of vision-ahead turns flip with a 2-round memory; 34% of those flips come from false ghosts (v35).

## 3. Ranked micro changes

| Rank | Change | Expected effect vs strong | Risk to our wins vs weak bots | Resembles | How it differs |
|---|---|---|---|---|---|
| 1 | **GHOST:** 'ahead' also subtracts fighters this launcher saw in the last 2 rounds within r2 26 that it cannot sense now | Small: about 4-7 step-ins per lost strong game by r300 are converted; upper bound about 1.8 deaths saved; realistically +0-1 game/100 | Moderate. 34% of flips come from false ghosts, and it may cost chases of weak bots that retreat. Nothing changes when memory holds no vanished fighter. | AHEAD_MIN knob (0/1/2 raced .469/.625/.635; 3 never finished); c_sim1 (HP sim plus standing, h2h 5/20); c_micro1 | No threshold or HP model. It changes only ready step-in decisions: the not-ready scoring is identical in both branches of fight(), and shoot() runs first. |
| 2 | **UHIT:** after a hit with no enemy fighter sensed, leave the cloud, then fire at the freshest remembered tile | Small panel-wide (2.6 events/game); larger on MassiveL (68 vs 0) | Very low: triggers only on that state | c_cloud1/c_cld2 (screen FAIL 9-11, self-play); c_blind2 (inert); arch_jm DEBT 13 (ablation null) | The trigger is an actual HP loss, and the main action is a move (none of those moved). The shot rule is cd + cost < 20, so the next turn stays ready; c_blind2's DEBT 0 forbade every shot from a cloud. No scan. |
| 3 | Cloud-aware fight() scoring | Unclear: helps MassiveL, probably hurts Forest | Medium | none | Test only after UHIT |
| 4 | AHEAD_MIN 3 | Blunt version of #1 | High (hits every fight) | knob race | — |
| 5 | Count only allies that can hit or reach in 'ahead' | Not measured | Medium | c_sim1 | — |

Not worth building, since there is no measured gap: cloud scan (c_blind1); support move; amplifier relay (c_amp2/3); pressing when outnumbered (c_swarm4a/b); the STAND/HOLD_THREAT knobs; target choice and overkill; tempo or first hit; pre-r250 wounded rotation.

The larger levers are outside launcher micro: production after r100, carrier defence at home, and army size.

## 4. Implementation plans

Base: the incumbent c_isle1 (submission 186). Its run, shoot, track, fight, march and regroup are identical to c_hr1's, so the line numbers below (c_hr1 Launcher.java) carry over. Use new build directories (for example `src/c_ghost1`, `src/c_uhit1`) or one build with both switches, screening each arm alone.

### Shared fighter memory (both arms)

- **Port:** `memReset`, `remember`, `memForget`, `memBlocked`, `memPick` and `memTile` from `/home/terryvanbelle/projects/vibe/2023/src/c_blind2/Launcher.java` lines 150-247, renaming BLIND_MEM_* to MEM_*.
- **Constants:**
  - `C.MEM_N = 8` (a power of two from 2 to 16).
  - In Launcher: `static final boolean MEM = C.GHOST || C.UHIT;` With both switches false, javac removes every call and the bytecode path is c_hr1's.
- **Hooks:**
  - track(), line 221, before `ids[n] = e.ID;`: `if (MEM) remember(e, G.round);`
  - shoot(), line 176, after `rc.attack(best.location);`: `if (MEM && best.health <= 20) memForget(best.ID);`
- **Cost:** c_blind2 measured 37-53 bytecodes per fighter, so at most about 650 per turn at TRACK_MAX 12. It runs only under track()'s existing 6000-bytecode guard, and calm turns pay nothing.
- **Tests:** port the memory cases from `test/bot/Blind2Test.java` (Proxy RobotController, checks run from main).

### Plan 1: GHOST

**C.java**
```java
/** c_ghost1: fight()'s 'ahead' also subtracts up to GHOST_MAX enemy fighters this launcher saw at most GHOST_AGE rounds
 *  ago whose last tile is within r2 GHOST_R2 and which it cannot sense now. false = c_hr1. */
public static final boolean GHOST = false;
public static final int GHOST_AGE = 2, GHOST_R2 = 26, GHOST_MAX = 2, GHOST_MIN_LEFT = 3500;
```

**Launcher.fight()** (lines 250-251): move `MapLocation here = rc.getLocation();` above the `ahead` line, then:
```java
int lead = G.nAllyFighters + 1 - G.nEnemyFighters;
if (C.GHOST && lead >= 2 && G.round - memLast <= C.GHOST_AGE && Clock.getBytecodesLeft() >= C.GHOST_MIN_LEFT) {
    int cand = ghostCandidates(G.round, here);
    int g = ghostCount(cand, ghostSensed(rc, cand), C.GHOST_MAX);
    if (lead - g < 2) ghostFlips++;
    lead -= g;
}
boolean ahead = lead >= 2;
```

**Functions**
- `static int ghostCandidates(int now, MapLocation here)` (pure): the bit mask of slots s with `now - memRound[s] <= GHOST_AGE` and `here.distanceSquaredTo(memLoc[s]) <= GHOST_R2`.
- `static int ghostSensed(RobotController rc, int cand)` (RC part): the bits of `cand` where `rc.canSenseRobot(memId[s])` is true.
- `static int ghostCount(int cand, int sensed, int max)` (pure): `Math.min(max, Integer.bitCount(cand & ~sensed))`.
- `static boolean aheadLead(int nAlly, int nEnemy, int ghosts)` (pure): `nAlly + 1 - nEnemy - ghosts >= 2`.

**Invariants, to test in Ghost1Test.main**
1. An empty memory gives a candidate mask of 0.
2. The age boundary counts at AGE and not at AGE+1.
3. The r2 boundary counts at 26 and not at 27.
4. `0 <= ghostCount <= max`.
5. Sensed slots never count, and the count never rises as sensed bits are added.
6. With 0 ghosts, aheadLead equals c_hr1's expression for every nAlly and nEnemy in 0..20.
7. A Proxy RC check that a slot killed through shoot() is forgotten.

**Telemetry:** append `",gf=" + ghostFlips` to G.extra.

**Bytecodes:** about 300 at most, only on fight() turns where vision says ahead and the memory is fresh: 8 slots × about 25, plus at most 8 canSenseRobot calls. Zero otherwise.

**What to measure on the panel**
- Flips per game.
- Strong par and ahead Lexch at r0 ≤ 300 (baseline 0.94 lost / 1.40 won).
- The share of fights that turn (27% / 9%).
- Deaths within 4 rounds of a step-in.
- **Guard:** weak-bot ahead-mid exchange must stay at 2.3 or more (baseline 2.55).

### Plan 2: UHIT

**C.java**
```java
/** c_uhit1: HP fell since the previous own turn while no enemy fighter is sensed: on a cloud step to the best non-cloud
 *  neighbour (UHIT_EXIT), then fire at the freshest remembered fighter tile not sensable now if the shot keeps the next
 *  turn ready (UHIT_SHOT). false = c_hr1. */
public static final boolean UHIT = false, UHIT_EXIT = true, UHIT_SHOT = true;
public static final int UHIT_AGE = 4, UHIT_MIN_LEFT = 3000;
```

**Launcher.run() changes**
- New fields: `static int lastHp = 200, lastHpRound = -10, uhitExits, uhitShots;`
- After `shoot();` (line 52):
  ```java
  boolean uhit = false;
  if (C.UHIT) { int hp = rc.getHealth(); uhit = unseenHit(hp, lastHp, lastHpRound, G.round, G.nEnemyFighters); lastHp = hp; lastHpRound = G.round; }
  ```
- The movement block (line 54) becomes:
  `if (uhit && C.UHIT_EXIT && Clock.getBytecodesLeft() >= C.UHIT_MIN_LEFT && cloudExit()) { mode = 1; uhitExits++; } else if (hasHittableEnemies()) ... else march();`
  The existing re-sense and shoot at line 60 then fires at anything visible from the open tile.
- After line 60:
  `if (C.UHIT && C.UHIT_SHOT && uhit && rc.isActionReady() && Clock.getBytecodesLeft() >= C.UHIT_MIN_LEFT) uhitShot();`

**cloudExit()**
1. Return false unless our own tile is a cloud (`rc.senseCloud(G.here)`).
2. For the 8 neighbours, build:
   - a movable mask from `rc.canMove`;
   - a cloud mask from `rc.senseCloud(loc)` (always sensable at r2 ≤ 2);
   - `threat[k]`: remembered fighters within UHIT_AGE whose tile is within r2 26 of the neighbour;
   - `home[k]`: distance² to `HQState.nearest(here)`.
3. Call `exitPick`. If it returns k ≥ 0, move and return true.

**uhitShot()**
1. Read `cd = rc.getActionCooldownTurns()` and `cost = round(10 × senseMapInfo(here).getCooldownMultiplier(G.us))`.
2. If `shotKeepsNextTurn(cd, cost)`: call memBlocked and memPick (age UHIT_AGE); if a candidate is found, `rc.attack(memTile(code))` and count `uhitShots++`.

**Pure functions and invariants**
- `unseenHit(hp, lastHp, lastRound, round, nEnemyFighters)` returns `hp < lastHp && round - lastRound <= 2 && nEnemyFighters == 0`.
  - False on the first turn.
  - False when HP is unchanged or rose (island healing).
  - False when any fighter is sensed.
- `exitPick(int movable, int cloud, int[] threat, int[] home)` returns −1 if and only if `(movable & ~cloud) == 0`.
  - Otherwise it returns the index in that set with the fewest threats, then the smallest home distance, then the lowest index (no RNG).
  - It never returns an index that cannot move or is a cloud.
- `shotKeepsNextTurn(cd, cost)` returns `cd < 10 && cd + cost < 20`, which implies `cd + cost - 10 < 10` (the next turn starts ready).
  - Test it exhaustively over cd 0..9 and cost 6..14.

**Bytecodes**
- About 15 a turn for the trigger.
- About 900 at most for the exit, only on unseen-hit turns on a cloud.
- At most about 1,400 for the return shot (c_blind2's reviewed cap).
- Everything sits behind the UHIT_MIN_LEFT 3000 guard.

**What to measure on the panel**
- Hits taken on a cloud from enemies we cannot see, and what happens in the next 4 rounds. Baseline (8826,7): 68 vs 0; we stay 61% of the time, lose 36.3 HP and deal 11.4 per event.
- The MassiveL and Forest cells.
- Idle in-range turns on clouds.
