# Structural designs vs the strong bots: four designs, one judge (2026-10-18)

Workflow wf_9dfbc5a6-daf (designers: economy, doctrine, information, copy; one judge). Data: the c_isle1 panel, matches 9039-9048 extracts. Winner: **c_evac1** (evacuate a raided HQ zone), built from the spec below.

# Ranking
Judged 2026-10-18 at 11:03 PDT. Data: the c_isle1 panel, matches 9039-9048, from matches/<id>/extract/*.csv. Code: src/c_isle1. Group sizes: strong-bot losses SL 23, strong-bot wins SW 17, weak-bot wins WW 56, weak-bot losses 4.

1. WINNER: the ECONOMY design (proposed as "c_raid1"), built as c_evac1 with the copy design's core merged in.
   - Mechanism: an HQ under enemy pressure is flagged "raided" in the shared array.
     - While another HQ is clear, carriers stop mining, delivering and fleeing in that HQ's zone and use the nearest clear HQ instead.
     - The raided HQ stops building carriers but keeps building launchers.
   - The evidence holds against the CSVs:
     - SL carrier deaths by r200 are 9.22 ours vs 3.65 theirs; 195 of 212 happen at prog < 0.4, i.e. on our side.
     - Deaths in scope of the rule: 3.04 per SL game conservative, 4.91 optimistic. The design claimed 3.6-4.8.
     - The flag fires in 15 of 23 SL games.
     - Victims are mostly empty: flee-empty 26, going-to-well-empty 22, throw 9, loaded on the way back only 3 of 67.
     - The cleanest geometry is Maze: raided (21,21); siblings (11,2) and (3,46) have under-used wells (17,9) and (10,39), at concurrency 3.2-4.2 against a max of 6-7.
   - No past attempt moves carriers between HQ zones. The nearest past attempts differ on the axis that matters:
     - c_line8c: danger-aware wells from sightings, not HQ pressure.
     - c_flee2 and c_flee3: hold carriers near home, which idles them.
     - c_di1: drops a well after flights, but stays in the zone.
     - c_well6 and c_well7 (HOT): front wells only; frontGate exempts home wells, and the deaths are at home wells.
     - c_hq1 and c_thr1: more carriers under threat, the opposite move.
   - Expected effect: 1.5-2.9 fewer SL carrier deaths per game by r200, concentrated in the 12 losses on Maze, Cornucopia, Forest, MassiveL and DefaultMap. That is +1.5 to +3 alive carriers at r200 (the gap is 6.9) and +100-200 Mn per SL game by r300 (+2-4 launchers), so +1 to +3 of the 40 strong-bot games.
   - Weak-bot risk: the T25/H25 rule fires in 18 of 56 WW games. Per WW game, in-scope deaths are 0.84, about 17 Mn moves to another zone and about 0.9 carrier births are delayed, so at most 1 weak-bot game is at risk (watch Cornucopia and DefaultMap).
   - Expected net: +1 to +2 panel games.

2. COPY design (c_qhq1): same core as the winner; MERGED into it, not built alone. It ranks below the economy design for three reasons:
   - It leaves the flee target unchanged, and flee-empty is 26 of 67 in-scope deaths. 75% of INTO hits happen on steps toward home (diagnosis 2026-10-16).
   - It leaves delivery unchanged.
   - Its QUIET_SUM 10 threshold fires in 22 of 56 WW games (31 HQs), against 18 (26 HQs) for the economy rule, with about the same SL coverage (2.91-5.09 vs 3.04-4.91 per game). That is more weak-bot exposure for no strong-bot gain.
   Grafted from it:
   - swarmRole reads the safe HQ's Ad flag.
   - Its observation that inbound trips are safe (loaded on the way back: 3 of 67) is why the delivery redirect is bounded rather than total.

3. EYES design (c_eyes1): not rejected, not built now.
   - Its numbers reproduce exactly (15.65 SL carrier deaths per game by r300, 8.87, 12.48).
   - But its causal premise (carriers die because they do not know where enemies are) is not audited:
     - Deaths on a first sighting are 3% of deaths, and the 10-16 diagnosis scored its "warning board" variant lowest.
     - The memory and stand-off family it resembles failed: c_flee1 (screen b 8/20, 6 overruns), c_flee9 (b 8/20); the c_flee6 ablation was neutral (20/40, paired +5 -6).
     - It risks idle carriers, as c_flee3 did (panel net -4).
   - Grafted: its bound for delivering to another HQ, cheb(here, clear) <= 1.5 x cheb(here, raided) + 4.
   - Promote only if an offline replay audit shows it would avoid at least 2.0 SL deaths per game that c_evac1 does not.

4. DOCTRINE design (c_screen1): REJECTED (see rejected).

Expected panel gain minus weak-bot risk: c_evac1 (+1 to +2) > copy alone (+0.5 to +1.5, higher WW exposure) > eyes (unproven; about 0 on the stand-off precedent) > doctrine (negative on precedent).

# Rejected
DOCTRINE design (c_screen1): REJECTED. Its idea: hold launchers as a screen at a point and release them by count, to stop the carriers from being hit piecemeal.

1. It repeats failed attempts without a real difference. "Hold the army at a point, release on a count" is the c_front1 / c_grp1 / c_ward3 family:
   - c_front1: screen FAIL, b 10/20, c -16.
   - c_grp1: screen FAIL, b 7/20.
   - c_ward3: screen FAIL, b 9/20.
   Each of these held launchers back from the fight. The screen differs only in where the hold point sits.
2. It runs against the strongest current result. c_loose1 (C.ARMY false, i.e. less grouping, not more; abl1 cell c_ab03) scores 59/79 on the panel maps, paired net +20, z 3.2. The 09:39 PDT panel analysis concludes that army size, not concentration, is the gap: alive launchers in SL games are 15.3 vs 19.2 at r200 and 13.5 vs 27.6 at r300.
3. Its causal premise was already rejected by diagnosis. research/diagnosis/2026-10-17-panel-losses-c_hr1.md:
   - "B: piecemeal arrival. Rejected as a cause."
   - 328 of 352 home carrier deaths came inside engagements our launchers were already in (median peak 7 vs 7).
   - A trigger on the first flight would fire in nearly every win.
4. Its numbers hold only partly: deaths within r2 36 of the top-3 wells by r200 are 5.57 per SL game against the claimed 5.09; SW 1.47 matches. But a screen does not address deaths that happen while our launchers are already present.

Nothing from it is compatible with the winner.

Notes on the other designs:
- ECONOMY: not rejected, but its package name c_raid1 collides with an existing attempt in progress/ATTEMPTS.md (c_mid1 plus the army raiding enemy mana wells, dropped 19/40 vs 22/40), and test/bot/Raid1Test.java already exists. Built as c_evac1 / Evac1Test.
- ECONOMY: its "WELL source 8" does not fit Telemetry.emitWell's 3-bit source field ((source & 7) << 14 would wrap to 0). Use source 0, which is unused.
- COPY: merged, not rejected.
- EYES: deferred pending the audit described in the ranking, not rejected.

# Verified numbers
All from python over matches/9039-9048/extract/*.csv (games, robots, deaths, hq, trips, timeline). Our side is A in every game.

- Group sizes: SL 23, SW 17, WW 56, weak losses 4.
- "In scope": our carrier deaths within r2 100 of a raided HQ while some sibling HQ is clear.
- Raid rule: hq.csv pressure34 summed per 25-round bucket.

HEADLINES

Our carrier deaths by r200 (ours vs theirs):

| Group | Ours | Theirs |
|---|---|---|
| SL | 9.22 | 3.65 |
| SW | 3.53 | 7.53 |
| WW | 2.79 | 10.82 |

195 of 212 SL deaths happened at prog < 0.4 (our side).

SL per game (ours/theirs):

| Round | Alive carriers | Mn collected | Built carriers | Built launchers | Alive launchers |
|---|---|---|---|---|---|
| r60 | 11.0/11.9 | 261/278 | | | |
| r100 | 12.5/14.4 | 480/543 | 15.3/15.5 | | |
| r200 | 13.0/19.9 | 1012/1319 | 22.2/23.6 | 39.4/43.7 | 15.3/19.2 |
| r300 | 11.9/27.6 | 1433/2288 | | 53.7/67.5 | 13.5/27.6 |

SL death tokens r<=200: F 77, G 66, C 22, V 19, W 15, R 4, X 3.

ECONOMY DESIGN (RAID_SUM 25)

| Version | SL in-scope deaths per game | Design's claim |
|---|---|---|
| Conservative, r200 | 3.04 | 3.6-4.8 |
| Optimistic, r200 | 4.91 | |
| Conservative, r300 | 5.09 | of 15.65 SL deaths per game by r300 |

- Fired in 15/23 SL games (22 HQs) and 18/56 WW games (26 HQs).
- Median d2 from death to the HQ: 13 conservative, 10 optimistic.
- In-scope tokens: F 32, G 22, V 9, R 3, C 2, W 2.
- Load at death: F-empty 26, G-empty 22, V-empty 9, F-loaded 6, R-loaded 3.
- Mn deposited from wells mined in a flagged zone, by r200 (design claimed 44-47 for SL):

| Group | Per game | Of total Mn |
|---|---|---|
| SL | 32.6-37.8 | 772 |
| SW | 17.6-24.7 | 1007 |
| WW | 22.5-26.8 | 1028 |

- Births at a flagged HQ with a clear sibling: SL 1.91-2.74 per game.

COPY DESIGN (QUIET_SUM 10)
- SL in-scope 2.91-5.09 per game (claimed 2.9-4.9: holds). SW 1.65-2.06. WW 0.84-1.14.
- Fired in 22/56 WW games (31 HQs), against 18/56 (26 HQs) for RAID_SUM 25.

THRESHOLD SWEEP (T = sum, H = hold; conservative)

| Rule | SL in-scope deaths/game | SL fired | WW in-scope deaths/game | WW fired | WW Mn relocated/game | WW births blocked/game |
|---|---|---|---|---|---|---|
| T25 H25 (chosen) | 2.91 | 15/23 | 0.84 | 18/56 | 17 | 0.89 |
| T25 H50 | 3.04 | | 0.84 | | | 1.07 |
| T50 H25 | 2.09 | | 0.61 | | | |
| T100 H0 | 1.09 | 9/23 | | | | |

WHERE AND WHEN

- SL in-scope deaths by map: Maze 21 (3 games), Cornucopia 13 (2), Forest 13 (3), MassiveL 12 (2), DefaultMap 11 (2). Zero on BatSignal, Cat, Hah, IslandHopping and ReverseFunnel.
- WW concentration: Cornucopia 19 (6 games), DefaultMap 15 (6).
- Timing, 70 in-scope deaths: 21 within 25 rounds of the HQ's first flag, 10 at 26-50, 39 later.
- Victim age: 10 rounds or less: 4; 11-40: 17; over 40: 46.
- Victim's last well:
  - none: 17;
  - local, within d2 100: 22;
  - local, beyond d2 100: 16 (Maze (12,26) at d2 106; Cornucopia centre at about 290; Forest);
  - another zone: 12, of which DefaultMap accounts for 8 (well (7,21), homeOf (4,26), next to the raided (13,23)).
  - This supports EVAC_WELL_R2 = 144.

Births at a raided HQ (H25):

| Group | Births per game | Dead within 40 rounds (share) | Of those, near that HQ | All births dead within 40 rounds |
|---|---|---|---|---|
| SL | 1.61 | 0.65 (41%) | 0.57 | 11% |
| SW | 1.65 | 0.53 (32%) | | 5% |
| WW | 0.89 | 0.14 (16%) | | 4% |

- Banked Ad at flagged HQ-buckets: median 55 (SL), 40 (SW), 40 (WW). Share at 150 or more: 0.16 (SL), 0.07 (WW). This supports EVAC_AD_RELEASE 150.

GEOMETRY

- Maze: raided (21,21). Sibling (11,2) with well (17,9) at concurrency 3.9-4.2 (max 6-7); sibling (3,46) with well (10,39) at 3.2-3.3 (max 6).
- Forest: pressed (11,48). The only mined Mn well is (8,12) (homeOf (0,0), cheb 48), at concurrency 4.9-7.3 (max 10). (6,30) and (7,30) mine no Mn.
- DefaultMap (7,21): 6.5-6.9 (max 9-10). Hah (14,11): 7.4 (max 10). MassiveL (0,39): 3.7 (max 4).
- Cornucopia 9040 game 2: all three HQs flagged, so the rule falls back to c_isle1 behaviour.

OTHER DESIGNS
- Eyes: 15.65, 8.87 and 12.48 reproduce.
- Doctrine: deaths within r2 36 of the top-3 wells by r200 are 5.57 per SL game (claimed 5.09); SW 1.47 (matches).

CODE FACTS (c_isle1)
- Well choice, flee (survive:226), deliver (245) and spawn (HQ.build:87) all use the nearest or the threatened HQ. None of them considers another HQ.
- frontGate exempts home wells (HOT_HOME_D2 64), so HOT does not cover these deaths.
- AD_FLAGS bits 12-15 are unused, and every writer preserves them.
- emitWell's source field is 3 bits: source 0 is free, and the proposed 8 would wrap.
- No package emits HQ reason 10; LET_HQ index 10 decodes as '?'.
- G.nearest draws the RNG on ties; Carrier.homeOf does not.
- The names c_raid1 and Raid1Test are taken; c_evac1 and Evac1Test are free.
- Past results cited: c_loose1/c_ab03 59/79, paired net +20, z 3.2. Instrument check (TRAINING_LOG 08:41 PDT): screen b of 12 or more means panel net +1.7; 10-11 means -0.3; 9 or less means -2.6.
# c_evac1 implementation spec

c_evac1: implementation spec. Base: src/c_isle1. Arm: C.EVAC (false = c_isle1 exactly).

0. PACKAGE
- cp -r src/c_isle1 src/c_evac1, then change "package c_isle1;" to "package c_evac1;" in every file.
- The name c_raid1 is taken (ATTEMPTS.md; test/bot/Raid1Test.java exists).
- Change only what is below.
- Identity rule: with the raided mask at 0, every new branch is inert, and no new code draws G.rand() or changes the order or number of the existing HQState.nearest calls. G.nearest draws rand() on ties, so every HQState.nearest call stays exactly where it is, and the new logic post-processes its result with RNG-free helpers.

1. C.java: one block, after the c_isle1 constants

```java
/** c_evac1: a raided HQ zone is evacuated. HQ i is raided while its vision held >= RAID_SUM enemy fighter-rounds in
 *  the previous + current PRESS_BUCKET (and RAID_HOLD rounds after); while some other HQ is clear, carriers flee,
 *  deliver (bounded) and choose wells via the nearest clear HQ, and the raided HQ builds no carrier below
 *  EVAC_AD_RELEASE Ad. c_isle1 panel: 3.0-4.9 of 9.2 SL carrier deaths by r200 are in scope. false = c_isle1. */
public static final boolean EVAC = true;
public static final int RAID_SUM = 25;             // fighter-rounds (hq.csv pressure34 units); PRESS_SUM is 100
public static final int RAID_HOLD = 25;            // rounds the bit stays on after the last round the sum held
public static final int RAID_SHIFT = 12;           // AD_FLAGS bits 12-15 (free in c_isle1)
public static final int EVAC_WELL_R2 = 144;        // a well is evacuated if its nearest HQ is raided and it is within this
                                                   // (Maze (12,26) at d2 106 is in; Cornucopia central wells at d2 ~290 are out)
public static final int EVAC_DELIVER_SLACK = 4;    // deliver to the clear HQ if cheb <= 1.5 x cheb(raided) + this
public static final int EVAC_MIN_LEFT = 5000;      // bytecodes needed for an evacuation well pick
public static final int EVAC_RETRY = 10;           // rounds without evac drops after nearestEvac found nothing
public static final boolean EVAC_SPAWN = true;     // sub-switch: the raided HQ's carrier gate
public static final int EVAC_AD_RELEASE = 150;     // = AD_BANK_CAP: a raided HQ at >= 150 Ad still builds carriers
```

2. Comms.java
- Schema doc for slot 61: replace "Bits 12-15 stay free (rank 3 uses them)" with: "c_evac1: bit C.RAID_SHIFT+i (12-15) set = HQ i is raided (HQ.swarmEconomy: C.RAID_SUM fighter-rounds); written by that HQ only on change; setAdFlag, setPressed and the probe claim/release keep it".
- Add:

```java
public static void setRaided(int hq, boolean on) throws GameActionException {
    if (hq < 0) return;
    int v = read(AD_FLAGS), b = 1 << (C.RAID_SHIFT + hq), n = on ? v | b : v & ~b;
    if (n != v) put(AD_FLAGS, n);
}
public static int raidMask() throws GameActionException { return read(AD_FLAGS) >>> C.RAID_SHIFT & 15; }
/** Whether some registered HQ (index < n) has its raided bit clear. */
public static boolean clearExists(int mask, int n) { if (n <= 0) return false; int full = (1 << n) - 1; return (mask & full) != full; }
```

- HQ_LOC slots fill in order, so HQState.ourHQs[i] = slot i = HQ.hqIdx. Bits 12-15 are verified free: setAdFlag and setPressed mask single bits, and the probe claim/release at Carrier:333 does `v & ~(1 << (PROBE_SHIFT + idx))`.

3. HQ.java
- New static: `static int raidUntil;`.
- swarmEconomy(): after line 121 (Comms.setPressed):

```java
if (C.EVAC) {
    if (pressPrev + pressAcc >= C.RAID_SUM) raidUntil = G.round + C.RAID_HOLD;
    Comms.setRaided(hqIdx, G.round < raidUntil);
}
```

  - pressPrev carries the previous bucket, so after a bucket of at least 25 the bit stays on through the next bucket and RAID_HOLD more rounds.
  - The real-time rule fires mid-bucket, earlier than my bucket-end simulation. Its coverage sits between the simulated H25 and H50: SL in-scope 2.91-3.04 per game; WW births blocked 0.89-1.07 per game.
- build(): before the for loop (line 70), once per turn:

```java
boolean evacRaid = C.EVAC && C.EVAC_SPAWN && hqIdx >= 0 && G.round < raidUntil
    && Comms.clearExists(Comms.raidMask(), HQState.ourHQs == null ? 0 : HQState.ourHQs.length);
```

  Factor it as `static boolean evacBlocks(boolean evacRaid, int ad) { return evacRaid && ad < C.EVAC_AD_RELEASE; }` so the test can call it.
  - Line 87, the carrier branch: `if (!threatened && !evacBlocks(evacRaid, ad) && ad - resAd >= 50 && room && tryBuild(RobotType.CARRIER)) {...}`
  - Line 86 (launchers) is unchanged.
  - After line 88 (reason = hqReason(...)): `if (C.EVAC && reason == 9 && evacBlocks(evacRaid, ad) && !threatened && ad - resAd >= 50 && room) reason = 10;`
  - HQs act before carriers each round, so the bit is fresh for carriers. Between HQs it lags at most one round.
- Telemetry decoder (a tool change; run unit tests after it):
  - tools/replaydump/ReplayDump.java:682: LET_HQ ".bgpwcastx?????!" becomes ".bgpwcastxr????!" (index 10 = 'r', "carrier held back: zone raided").
  - Verified: no src/*/Telemetry.java returns 10.
  - Add the code to docs/TELEMETRY.md's HQ reason table.
  - Do not add anything to G.note.
  - When the flag fired is recomputed offline from hq.csv pressure34 with the same rule (my scratch scripts used it).

4. Carrier.java
- New statics:

```java
static boolean evac; static int evacMask, evacFallUntil; static MapLocation evacHome;
public static int evacPicks, evacFlees, evacDelivers;   // diagnostics
```

- run(): immediately after the censusTick line (before `if (role == 0)`, so pickRole/swarmRole sees it):

```java
evac = false;
if (C.EVAC) { evacMask = Comms.raidMask(); if (evacMask != 0) evac = Comms.clearExists(evacMask, HQState.ourHQs == null ? 0 : HQState.ourHQs.length); }
if (!evac) evacHome = null;
```

- Helpers (no RNG, no allocation):

```java
static int hqIdxOf(MapLocation h) { MapLocation[] a = HQState.ourHQs; if (a == null || h == null) return -1;
    for (int i = 0; i < a.length; i++) if (a[i].equals(h)) return i; return -1; }
static boolean raided(MapLocation h) { int i = hqIdxOf(h); return i >= 0 && (evacMask >> i & 1) != 0; }
/** n if evac is off or n is not raided; else the clear HQ nearest to `from`, first in HQ order on a tie; n if none. */
static MapLocation safeFrom(MapLocation n, MapLocation from) {
    if (!evac || n == null || !raided(n)) return n;
    MapLocation[] a = HQState.ourHQs; MapLocation best = null; int bd = Integer.MAX_VALUE;
    for (int i = 0; i < a.length; i++) if ((evacMask >> i & 1) == 0) { int d = from.distanceSquaredTo(a[i]); if (d < bd) { bd = d; best = a[i]; } }
    return best != null ? best : n;
}
/** l is in a raided zone: within EVAC_WELL_R2 of a raided HQ that is l's nearest HQ, and not the Mid site/twin. */
static boolean evacuated(MapLocation l) throws GameActionException {
    if (!evac || l == null) return false;
    MapLocation[] a = HQState.ourHQs;
    for (int i = 0; i < a.length; i++)
        if ((evacMask >> i & 1) != 0 && l.distanceSquaredTo(a[i]) <= C.EVAC_WELL_R2) {   // cheap reject first
            MapLocation h = homeOf(l);
            return h != null && raided(h) && !(C.MID && Mid.isSite(l));
        }
    return false;
}
```

- nearestEvac(from, t): a copy of nearestCool (lines 575-597) whose acceptance tests become:
  - shared loop: `if (d < bd && !hotLocal(l) && !evacuated(l))` (keep the `c >= 0x4000` skip);
  - seen loop: `if (d < bd && !hot(l) && !evacuated(l))`.
  - Same Comms.lastWellType / lastWellCount telemetry.
  - The checks stay lazy: they run only when d < bd.
- evacRepick(t):

```java
static void evacRepick(int t) throws GameActionException {
    if (!evac || well == null || G.round < evacFallUntil || !evacuated(well) || Clock.getBytecodesLeft() < C.EVAC_MIN_LEFT) return;
    MapLocation k = nearestEvac(safeFrom(homeOf(G.here), G.here), t);
    if (k == null) { evacFallUntil = G.round + C.EVAC_RETRY; return; }   // nothing else known: c_isle1's pick stands
    well = k; evacPicks++;
    if (C.TELEMETRY) wellHook(0, Comms.lastWellType);                    // WELL source 0 = evacuation pick (3-bit field)
}
```

  - homeOf(G.here) is the no-RNG nearest HQ. If it is clear, safeFrom returns it.
- survive(), line 226:

```java
MapLocation home = HQState.nearest(G.here);
if (evac) { MapLocation s = safeFrom(home, G.here); if (s != home) { home = s; evacFlees++; } }
```

  - The existing rule then moves toward home only if home is farther from the threat than here, else it calls moveAway.
  - emitFlee's home field records the safe HQ.
- deliver(), line 245: factor into `static MapLocation deliverHome()` (testable):

```java
MapLocation home = HQState.nearest(G.here);               // RNG draw kept
if (!evac || home == null) return home;
if (evacHome != null && !raided(evacHome)) return evacHome;   // sticky for this trip
evacHome = null;
if (!raided(home)) return home;
MapLocation s = safeFrom(home, G.here);
if (s != home && G.cheb(G.here, s) <= G.cheb(G.here, home) * 3 / 2 + C.EVAC_DELIVER_SLACK) { evacHome = s; evacDelivers++; return s; }
return home;
```

  - deliver() then uses `MapLocation home = deliverHome();`.
  - Set `evacHome = null;` where `returning = false;` is set after the deposit (line 257).
  - The c_well3 re-pick (lines 283-287) and Telemetry.trip use this home unchanged.
- swarmRole(), line 174: keep the RNG draw conditional on the id test, exactly as now:

```java
if (G.id % C.AD_EARLY_EVERY == 0) { MapLocation h = HQState.nearest(G.here); if (evac) h = safeFrom(h, G.here);
    if (Comms.adFlag(Comms.hqIndex(h))) return 1; }
```

- gather():
  - (a) After line 338: `if (evac && well != null && G.round >= evacFallUntil && G.here.distanceSquaredTo(well) > 2 && evacuated(well)) well = null;` A carrier already at its well keeps collecting: only 2 of 67 in-scope deaths were collecting.
  - (b) Line 347, probe: add `&& !(evac && !probeInit && raided(homeOf(G.here)))` before probeTurn(). This only blocks starting a probe from a raided zone. A started probe runs as in c_isle1, so its claim/release stays consistent. probeDone is not set, so it can probe after the raid (PROBE_UNTIL 200).
  - (c) At the end of the `if (well == null) {...}` block (after line 367): `if (C.EVAC) evacRepick(role);`
  - (d) At the end of the search-fallback block (after line 378): `if (C.EVAC) evacRepick(0);`
  - c_isle1's own pick, with its wellHook (sources 1, 2, 6), runs first. The repick replaces it only when it is evacuated, so carriers in clear zones keep c_isle1's choice. A replacement emits a second WELL record, source 0.
- switchWell(), lines 662-689: in both loops change `if (d < bd)` to `if (d < bd && !(evac && evacuated(l)))`. If everything is evacuated, c_isle1's no-best branch runs.
- explore(), line 712: `MapLocation home = HQState.nearest(G.here); if (evac) home = safeFrom(home, G.here);` The G.rand draws that follow are unchanged.
- Unchanged:
  - anchor courier paths (lines 80, 298 takeAnchor, 741 deliverAnchor timeout), scoutTurn (924), probeStart (1035), unjam;
  - Launcher, Comms enemy and ALARM/RECALL, GUARD, MID, HOT marking, PACK;
  - the HQ launcher, anchor and amplifier logic.

5. BYTECODE GUARDS
- Calm (mask 0): per carrier turn 1 shared read (2) plus about 10. Per HQ turn 1 read in swarmEconomy and 1 in build; the write (75) happens only on change.
- Under a raid, per carrier turn:
  - survive: safeFrom, about 60 (4 HQs);
  - deliver: about 100;
  - the gather drop check: about 40 (the reject path loops only over raided HQs).
- Pick turns: nearestEvac costs about 16x70 + 32x32 (as nearestCool), plus evacuated() on accepted candidates, about 100 each: at most about 3,500 on top of c_isle1's pick (about 1,500). It is guarded by EVAC_MIN_LEFT 5000 against the carrier's 12,500. If the budget is short, the c_isle1 pick stands that turn and the drop and repick are retried next turn.
- switchWell's checks are lazy (only when d < bd), with no allocation.
- The HQ build loop's existing `Clock.getBytecodesLeft() > 7000` guard is unchanged.
- Acceptance: zero bytecode overruns and zero exceptions in the h2h (Telemetry), especially on Cornucopia and MassiveL (most wells and carriers).

6. UNIT TESTS: test/bot/Evac1Test.java (package c_evac1)
Proxy RobotController over shared[64] as in Isle1Test, check() counter, System.exit(1) on failure. Set statics with set(), and the bytecode budget with budget().
- T1 bit preservation:
  - Start with AD_FLAGS = 0x0F73.
  - setRaided(2, true) gives 0x4F73. setAdFlag(1, false), setPressed(3, true), the probe claim of bit 10 and its release all keep bit 14. raidMask() == 4.
  - setRaided(2, true) a second time makes no write (count writeSharedArray calls).
  - setRaided(2, false) restores the other bits.
- T2 flag timing (HQ statics; G.round and G.nEnemyFighters set per round; hqIdx 0; call swarmEconomy, or only its pressure part, each round):
  - 0 fighters r1-30, then 2 per round from r31 to r43, then 0. Expect the bit off at r42 (sum 24), on at r43 (26), still on at r74 (pressPrev 26) and r98, off at r99 (raidUntil 74 + 25).
- T3 build gate (evacBlocks):
  - Two HQs; HQ 0 raided, HQ 1 clear: evacRaid true, so ad 120 blocks and ad 150 releases.
  - Both raided: clearExists false, so evacRaid false.
  - One HQ: n = 1, mask 1, so false.
  - The reason override gives 10 only when the base reason is 9. If the proxy can drive build(), also check that a launcher is still built with mn 45.
- T4 safeFrom, with HQs (0,0), (20,0), (40,0), (0,40):
  - mask 0001 from (5,0) gives (20,0); mask 0011 gives (40,0).
  - Tie: mask 0001 from (10,20) puts (20,0) and (0,40) at d2 500 each, so the first in order, (20,0), wins.
  - mask 1111 returns n. Mask 0 (evac false) returns n. A clear n returns n.
  - G.rng is unchanged across all calls.
- T5 evacuated:
  - HQs A (5,5) raided, B (40,40) clear: well (10,10) true; (15,15) (d2 200) false.
  - Mid site placed at (10,10) through the slot Mid.site() reads: false.
  - HQs (5,5) raided and (14,14) clear: well (11,11) is within 144 of (5,5), but homeOf is (14,14), so false.
  - Mask 0: false.
- T6 nearestEvac:
  - Shared mana wells (8,8) and (36,36), seen well (30,30), base (40,40), (5,5) raided: returns (36,36).
  - (36,36) marked hot (c | 0x4000): returns (30,30).
  - Only (8,8) known: returns null.
- T7 deliverHome:
  - here (10,10), raided (5,5) at cheb 5, clear (20,10) at cheb 10: 10 <= 5*3/2 + 4 = 11, so redirect.
  - Clear at (22,10), cheb 12: no redirect.
  - Sticky: a second call after moving one step returns evacHome. It resets when evacHome's bit sets and when returning goes false.
  - The HQState.nearest draw count is unchanged (compare G.rng with a c_isle1-style call).
- T8 switchWell: the current well and an evacuated alternative nearer than a clear one: picks the clear one. Only evacuated alternatives (role 2): well becomes null, as in c_isle1.
- T9 evacRepick:
  - The c_isle1 pick evacuated, alternative known: well replaced, evacPicks 1, source-0 record.
  - No alternative: well kept, evacFallUntil = round + 10, and the gather drop is skipped until then.
  - budget(4000): no change.
- T10 identity with mask 0: evac false; safeFrom, evacuated, deliverHome, evacRepick and the switchWell filter are all no-ops, and G.rng is unchanged.
Then run tools/unit-tests.sh. It globs test/bot/*Test and compiles all src packages, and it covers the ReplayDump LET_HQ change.

7. LOCAL MEASUREMENT PLAN
Volume runs go on battlecode-dev only, queued after abl1 and the c_loose1 screen. The driver runs at most one diagnostic game at a time. Never use battlecode-dev2.
- (a) Identity: build c_evac0 (= c_evac1 with EVAC false). It must reproduce c_isle1's games exactly on the panel maps at the 4 abl1 seeds (919953836, 840799072, 215706231, 353760905): same winners, rounds and per-team counts, like c_ab00.
- (b) Driver diagnostic, one game at a time: Maze vs arch_jm at seed 919953836, c_evac1 then c_isle1. Compare:
  - the first raided round at (21,21) (recomputed from hq.csv pressure34);
  - WELL source-0 picks and HQ reason 'r' counts;
  - in-scope carrier deaths by r200 (within r2 100 of a raided HQ while a sibling is clear);
  - alive carriers and collected Mn at r200 and r300;
  - zero overruns and exceptions.
  If nothing fires, use DefaultMap vs arch_swarm.
- (c) h2h vs c_isle1, VM: all maps, both sides, map seeds, 206 games. Then the 10 panel maps x both sides x the 4 abl1 seeds (80 games), paired cell by cell with the c_ab00 baseline games.
- (d) Mechanism study, VM: arch_jm and arch_swarm on the 5 trigger maps (Maze, Cornucopia, Forest, MassiveL, DefaultMap) x both sides x 4 seeds, paired with c_isle1. Include the c_evac1 ablation with EVAC_SPAWN false.
- (e) tools/screen.py, then the unranked panel only through tools/ladder_policy.py trial-start (docs/LADDER_STRATEGY.md).
- (f) If c_loose1 is accepted first, rebase as c_evac2 = c_loose1 + EVAC. The arms are orthogonal: ARMY touches launchers only.

KILL / ACCEPT
1. Mechanism (d): the flag fires in at least 25% of trigger-map cells; in-scope deaths fall at least 40% in fired cells; alive carriers at r200 rise by at least 1.0; coll_Mn at r200 does not fall. Otherwise the mechanism failed.
2. h2h (c): the signal over 206 games is at least 0, and the 10 panel maps are at least 50% (at least 40/80 at the fixed seeds). Watch Cornucopia and DefaultMap, the WW concentration of in-scope deaths: 19 over 6 games and 15 over 6.
3. Screen b: 9/20 or below kills; 10 needs a roster gain; 11 or more passes. The instrument check says b of 12 or more means panel +1.7.
4. Panel: net 0 or below rejects; the strong-bot cells must beat c_isle1's 17/40; weak-bot cells may lose at most 1.
5. Deaths down but outcomes flat: park it, do not tune it.
Record the attempt row in progress/ATTEMPTS.md and the TRAINING_LOG entry (times in PDT).

RISKS TO WATCH
- Launchers still spawn at the raided HQ, which is intended.
- Crowded sibling wells: DefaultMap (7,21) runs at concurrency 6.5-6.9 (max 9-10); Hah (14,11) at 7.4 (max 10); MassiveL (0,39) at 3.7 (max 4). switchWell and unjam still apply.
- Flag flicker between close HQs: DefaultMap's are 9 apart, and the sticky evacHome helps.
- Enemies following carriers into the clear zone.
- Forest's long walk to (8,12) at cheb 48 from (0,0), at concurrency 4.9-7.3.
- Stranded Ad at the raided HQ, bounded by EVAC_AD_RELEASE (median bank 55 at flagged SL buckets; 16% at 150 or more).