# Analyst 0: maxwelljones14.MPWorking, 18 games (matches 9911, 9913, 9918, 9924, 9928, 9930)

Written 2026-10-19 12:56 PDT. Our build in all six matches is c_eco3 (submission 192). Code locations cite
`src/c_kx0`, whose switch defaults reproduce c_eco3. We went 6-12 (6/18). The opponent's source was not read; this
report uses only the replays (extracts and per-turn dumps). Nothing in `src/` was changed and no game was run.

**Notation.**
- r² is a squared distance.
- prog is a position's progress toward the enemy, sqrt(d own HQ) / (sqrt(d own) + sqrt(d enemy)). 0 is our HQ and 1 is theirs.
- "us" is vibe23 and "them" is maxwell.
- A **fast loss** is a loss in 600 rounds or fewer. There are 8 of them (Pit, Quiet, Clown, PairedProgramming, Contraction, Diagonal, BatSignal and SoundWave).

**Data.**
- The extract CSVs are in `matches/<m>/extract/`.
- Per-turn dumps (`--sa`) exist for both sides of all 18 games (36 dumps). They were made with
  `research/diagnosis/2026-10-19-top2/scripts/a0_dump.sh` (flock, DUMP_XMX=500m) and are kept in the session scratchpad
  (`.../scratchpad/top2/a0/sa`, path set in `a0_common.py`, override with `A0_SA`).
- Per-turn telemetry codes (`--tele-turns`) are in `.../scratchpad/top2/a0/ext/<m>/tele_turns.csv` (override with `A0_EXT`).
- Every script is in `research/diagnosis/2026-10-19-top2/scripts/` and runs as `python3 -I scripts/a0_<name>.py [args]`.
- Each table below names the script that produced it.

## 0. Verified findings (short)

1. **The opening is the same on both sides.** In all 18 games both sides build 4 launchers and 4 carriers per HQ in
   r1-3. Launchers built by r50 are equal within 2 in 16 of 18 games; the exceptions, Hah and ThirtyFive, are wins in our
   favour (a0_overview `b3`, `bL50`). The games are decided
   by what the units do, not by the build.
2. **Fast losses start with maxwell's launchers on our mana wells, killing our carriers.**
   - In losses, maxwell hit our carriers 319 times by r100, against 121 for us (wins: 53 against 143).
   - 125 of those 319 hits landed within r² 25 of our mana wells (a0_wells).
   - In losses, 25 of our 50 carrier deaths by r150 were at prog < 0.3, near our HQ. In wins there were none (a0_deaths).
3. **Our carriers flee and come back to the same camped well.**
   - 24 of 50 fatal carrier trips in losses had at least 5 flee turns and at least 5 go/collect/wait/explore turns (a0_ctrips).
   - Quiet: 7 of 7 such trips; half of all mana-carrier turns by r100 were flee turns (a0_explore).
   - A home well is never marked "hot". `Carrier.front()` (Carrier.java:498-502) excludes wells within r² `C.HOT_HOME_D2` = 64 of home, and `gather()` drops a well only when it is hot (Carrier.java:340).
4. **On maps where our nearest mana well is outside HQ vision (r² > 34), our economy falls behind.**
   - Median mana collected by r100 is 237 for us against 422 for them (11 games, 3 wins). With the well inside HQ vision it is 622 against 613 (7 games, 3 wins) (a0_econ).
5. **SoundWave: mana carriers explore toward the centre, which is the enemy's doorstep.**
   - Our mana carriers spent 0.76 of their turns in explore (X) state.
   - 133 of those turns were within r² 100 of the enemy HQ at (24,11) (a0_explore).
   - Result: 0 mana by r100 against 449, and 8 carriers dead by r100 against 1 (a0_econ).
   - Code: `Carrier.explore()` sends a mana carrier with no known mana well to the map centre first (Carrier.java:702-710).
6. **First contact is at par, but we lose the exchange.**
   - In 9 of the 12 losses, the first lethal contact had launcher numbers within r² 64 equal or within 1 of each other.
   - In the 40 rounds after it we killed 25 launchers and lost 47. In wins the count was 20 against 27 (a0_first).
   - Quiet: 4 against 4 at r11 with 0 kills against 5 losses. Contraction: 4 against 6 at r52, 0 against 5.
7. **We arrive one at a time.**
   - At contact we have 3.1 launchers together against their 4.1 (medians, r ≤ 150; wins 4.2 against 4.6).
   - We are outnumbered on 0.15 of contact turns against their 0.01 (a0_launchers).
   - Our launchers that died by r200 in losses were alone (no ally within r² 20) at their last row in 53 of 227 deaths. In wins it was 17 of 141 (a0_lastcode).
   - At equal army size the spread is close (alone 0.18 against 0.15, a0_spread par rounds). So most of the gap comes with losing numbers; it does not cause it.
8. **Quiet trace (a0_trace 9928 1 8 26): maxwell's 4 launchers stood still in one block at (8-9,8-10), covering our mana well (13,10).**
   - Our 4 launchers stepped to (12,10) one at a time (r12, r14, r18, r22). Each had at most 2 allies within r² 20 against 4 enemies.
   - Each step-in was chosen while it saw 1 enemy. `Launcher.fight()` computes `superior` and `ahead` from the fighters in vision only (Launcher.java:248-252). Vision is r² 20; an enemy's reach after a move is r² 26.
9. **Blind step-ins are a second-order effect.**
   - In losses, 0.13 of our step-ins entered the reach of more enemy launchers than we saw, against their 0.07.
   - 0.12 of our step-ins entered the reach of 3 or more, against their 0.06. In wins both sides are at 0.02 (a0_stepin).
10. **Clouds: we do not fire at enemies we cannot see; maxwell does.**
    - On in-range turns with the shooter or the target on a cloud, we fired on 0.33 and they fired on 0.86 (r ≤ 200, n 1172 and 1233).
    - On clear turns both fired on 1.00 and 0.99 (a0_cloudfire).
    - The net effect is smaller than the fire rates suggest: launcher hits per cloud turn were 0.28 against 0.34 (all rounds: 0.30 against 0.34).
    - `Launcher.shoot()` attacks only sensed robots (`G.enemies`, Launcher.java:165-182).
    - A cloud was involved in 666 of 699 and 209 of 209 in-range turns in the two r2000 tiebreak losses (TimesUp and Marsh), and in part of the fighting on Contraction, BuildSite and Spots. Clouds do not explain the fast losses on clear maps.
    - Blind fire was tried before and rejected: c_blind1 and c_blind2 hit with 0.2% of their outside-vision shots, about 1% of damage (TRAINING_LOG 2026-10-14 13:23 and 15:19 PDT; LEARNINGS.md:12-19). c_blind2's memory targeting gave outcomes identical to c_blind1 in 100 of 100 cells. maxwell's replays suggest that remembered-position fire can do better (§5.3), so that memory path is worth checking for being inert.
11. **maxwell focus-fires harder.** In losses, its launcher kills had 2.25 distinct attackers in the last 5 rounds,
    38% were by 3 or more attackers, and the median time from first hit to death was 16 rounds. Ours: 1.93, 27% and 31
    rounds. In wins we lead: 2.37, 39% and 27 rounds, against their 2.14, 33% and 22 rounds (a0_focus).
12. **HQ defence is a consequence of losing, not a cause.**
    - Our HQ was pressed (pressure34 ≥ 100 in a 25-round bucket) by r300 in 4 of 12 losses (Quiet r125, PairedProgramming r75, Contraction r175, SoundWave r250) and in 0 of 6 wins (a0_hq).
    - When threatened, our HQ withholds carriers (`!threatened`, HQ.java:93). Quiet spent 0.59 of its HQ turns in that state.

## 1. The 18 games

From a0_overview (sizes, HQs, walk distance between the nearest HQ pair, L and Mn at r100), a0_econ (`mnvis` = least
d² from our HQs to a mana well) and a0_cloudfire (in-range launcher turns with a cloud involved, r ≤ 200). The cloud
share is the cloud tiles divided by the map area (inline `load_map`).

| game | res | end | size | HQs | walk | nearest Mn d² | cloud share | cloud in-range turns us | L r100 us-them | Mn r100 us-them |
|---|---|---|---|---|---|---|---|---|---|---|
| 9918 g1 Pit | L | r379 conquest | 60x30 | 2 | 21 | 49 | 0.031 | 0 | 12-13 | 444-549 |
| 9928 g1 Quiet | L | r413 conquest | 20x20 | 1 | 13 | 45 | 0.035 | 0 | 0-11 | 20-334 |
| 9924 g1 Clown | L | r445 conquest | 21x20 | 2 | 6 | 10 | 0.029 | 0 | 12-16 | 503-577 |
| 9913 g1 PairedProgramming | L | r457 conquest | 45x20 | 3 | 16 | 36 | 0.129 | 0 | 10-10 | 294-504 |
| 9913 g0 Contraction | L | r484 conquest | 60x60 | 2 | 53 | 137 | 0.139 | 68 | 11-19 | 179-422 |
| 9918 g0 Diagonal | L | r489 conquest | 40x40 | 1 | 32 | 164 | 0.013 | 0 | 2-8 | 101-205 |
| 9924 g0 BatSignal | L | r504 conquest | 60x20 | 1 | 53 | 50 | 0.013 | 0 | 6-6 | 319-282 |
| 9928 g2 SoundWave | L | r596 conquest | 40x30 | 2 | 19 | 89 | 0.090 | 4 | 4-11 | 0-449 |
| 9930 g2 Spots | L | r833 conquest | 60x60 | 2 | 49 | 10 | 0.172 | 47 | 19-19 | 498-426 |
| 9928 g0 BuildSite | L | r999 conquest | 50x50 | 2 | 39 | 8 | 0.030 | 109 | 19-17 | 770-638 |
| 9911 g2 TimesUp | L | r2000 tb anchors | 20x30 | 2 | 19 | 53 | 0.237 | 666 | 11-8 | 392-366 |
| 9924 g2 Marsh | L | r2000 tb islands | 60x50 | 1 | 37 | 16 | 0.406 | 209 | 4-4 | 90-183 |
| 9911 g0 Movepls | W | r466 | 45x30 | 2 | 17 | 90 | 0.019 | 0 | 10-15 | 205-439 |
| 9913 g2 Rectangle | W | r490 | 50x30 | 2 | 39 | 32 | 0.064 | 11 | 15-10 | 786-613 |
| 9930 g1 Spiral | W | r532 | 30x30 | 2 | 19 | 8 | 0.044 | 4 | 17-13 | 776-667 |
| 9930 g0 Hah | W | r536 | 50x25 | 2 | 29 | 32 | 0.074 | 0 | 11-13 | 622-659 |
| 9918 g2 ThirtyFive | W | r894 | 48x47 | 3 | 33 | 40 | 0.024 | 54 | 23-17 | 787-561 |
| 9911 g1 SweetDreams | W | r951 | 35x35 | 1 | 20 | 40 | 0.127 | 0 | 5-3 | 237-130 |

All 8 fast losses are on maps with a short rush (walk ≤ 21) or a nearest mana well outside HQ vision (d² > 34). So are
4 of the 6 wins (Movepls, Spiral, ThirtyFive and SweetDreams), so map features alone do not separate wins from losses.

## 2. maxwell's opening and attack pattern

### 2.1 Build order

a0_overview `b3` and the `bL50`/`bL100` columns:

- **r1-3.** Both sides build 4 launchers and 4 carriers per HQ in all 18 games. maxwell sometimes builds a carrier first on an HQ (census `first_builds` on Contraction: `1:C 1:C 1:C 2:L`), but the r3 total is the same.
- **Launchers built by r50.** Equal within 2 in 16 of 18 games. The exceptions are Hah 15/11 and ThirtyFive 22/15, both wins in our favour.
- **Launchers built by r100.** maxwell builds more in 7 of 12 losses, for example Quiet 6/12, SoundWave 12/18 and Contraction 16/19. In 4 of 6 wins we build more. This is the economy gap of §2.3 showing up, not a different build rule.

### 2.2 First launchers and the shape of their army

a0_first gives the first contact (an enemy launcher within r² 20) and the first contact followed by a death within
10 rounds. The near counts are launchers within r² 64 of the contact point.

| game | res | first contact | near us v them | prog | first lethal contact | near | prog | L kills next 40 r us/them |
|---|---|---|---|---|---|---|---|---|
| Pit | L | r6 | 4v4 | 0.33 | r9 | 3v4 | 0.33 | 3/3 |
| Quiet | L | r11 | 4v4 | 0.31 | r11 | 4v4 | 0.31 | 0/5 |
| Clown | L | r2 | 4v4 | 0.65 | r2 | 4v4 | 0.65 | 5/3 |
| PairedProgramming | L | r15 | 7v4 | 0.28 | r20 | 6v5 | 0.28 | 3/5 |
| Contraction | L | r46 | 4v4 | 0.48 | r52 | 4v6 | 0.51 | 0/5 |
| Diagonal | L | r27 | 4v2 | 0.29 | r35 | 4v4 | 0.31 | 0/2 |
| BatSignal | L | r30 | 2v4 | 0.53 | r34 | 4v4 | 0.45 | 2/4 |
| SoundWave | L | r4 | 4v4 | 0.62 | r10 | 4v4 | 0.61 | 2/3 |
| Spots | L | r60 | 2v3 | 0.46 | r76 | 2v4 | 0.47 | 0/4 |
| BuildSite | L | r38 | 3v2 | 0.44 | r40 | 5v2 | 0.49 | 4/3 |
| TimesUp | L | r14 | 3v4 | 0.62 | r22 | 4v4 | 0.48 | 4/6 |
| Marsh | L | r53 | 4v3 | 0.41 | r56 | 4v4 | 0.44 | 2/4 |
| Movepls | W | r8 | 4v2 | 0.31 | r30 | 1v5 | 0.58 | 1/3 |
| Rectangle | W | r13 | 4v3 | 0.46 | r15 | 4v3 | 0.44 | 3/2 |
| Spiral | W | r9 | 5v4 | 0.41 | r9 | 5v4 | 0.41 | 5/5 |
| Hah | W | r30 | 4v8 | 0.58 | r30 | 4v8 | 0.58 | 5/9 |
| ThirtyFive | W | r41 | 6v4 | 0.48 | r41 | 6v4 | 0.48 | 4/7 |
| SweetDreams | W | r29 | 5v5 | 0.45 | r30 | 5v5 | 0.45 | 2/1 |

Pooled over the first lethal contact:

| | we have fewer near | we have more near | launcher kills next 40 rounds, us / them |
|---|---|---|---|
| Losses | 3/12 | 2/12 | 25 / 47 |
| Wins | 2/6 | 3/6 | 20 / 27 |

**Where and when maxwell's launchers arrive.**
- Its first launchers meet ours between r2 and r60. The first contact is at prog 0.28-0.33 (our third of the map) in Pit, Quiet, PairedProgramming and Diagonal, all losses, and in Movepls, a win.
- Its launchers are first within r² 100 of one of our HQs on these rounds (a0_launchers `arrive`):
  - Pit r3: 1 launcher, at most 4.
  - Quiet r10: 1, at most 12.
  - Clown r2: 6, at most 15.
  - PairedProgramming r2: 1, at most 9.
  - SoundWave r3: 4, at most 11.
  - Contraction r126: 1, at most 9.
  - Diagonal r66: 1, at most 4.
- On Clown, Pit, PairedProgramming and SoundWave the HQs are close, so arrival at r2-3 mostly reflects the spawn tiles.

**Army shape.** From a0_launchers (r ≤ 150, medians over games):

| | group at contact us/them | outnumbered share us/them | outnumbering share us/them | still when firing us/them | carrier hits us/them | launcher hits us/them |
|---|---|---|---|---|---|---|
| Losses (12) | 3.1 / 4.1 | 0.15 / 0.01 | 0.63 / 0.90 | 0.35 / 0.53 | 21 / 47 | 132 / 142 |
| Wins (6) | 4.2 / 4.6 | 0.08 / 0.05 | 0.86 / 0.86 | 0.35 / 0.57 | 38 / 13 | 256 / 206 |

maxwell fights as a block that stands still while firing (0.53-0.57 of its attack turns without a move, against our
0.35). In losses it is almost never outnumbered at contact (0.01).

The Quiet trace (`a0_trace.py 9928 1 8 26`) shows the pattern:
- r8-11: its 4 launchers held (8,7), (8,9), (6,8) and (5,6), then settled at (9,8), (9,10), (8,8) and (8,10). Each had 3 allies within r² 20, and they hit our carriers at our mana well (13,10) on r8-11.
- From r12 to r24 the block barely moved and hit our launchers every turn.
- Our 4 launchers came to the step-in tile (12,10) one by one: id 366 at r12 (1 ally against 4), 438 at r14, 717 at r18 and 149 at r22. Our launcher deaths were at r14, r22, r22 and r24 (a0_deaths). Ours killed none of theirs (a0_first: 0/5).

### 2.3 Carrier harassment

From a0_wells (r ≤ 100). A mana well "belongs" to the side whose nearest HQ is nearer by walk distance.

| game | res | their launcher turns at our Mn wells | their carrier hits | of which at our wells | our carrier hits | of which at their wells | their first carrier hit (a0_launchers c1) |
|---|---|---|---|---|---|---|---|
| Quiet | L | 0.57 | 43 | 39 | 0 | 0 | r7 |
| Diagonal | L | 0.33 | 47 | 31 | 27 | 6 | r47 |
| Contraction | L | 0.27 | 17 | 17 | 0 | 0 | r39 |
| BatSignal | L | 0.24 | 0 | 0 | 0 | 0 | - |
| TimesUp | L | 0.25 | 28 | 9 | 35 | 15 | r22 |
| PairedProgramming | L | 0.02 | 54 | 26 | 4 | 0 | r9 |
| SoundWave | L | 0.00 | 66 | 0 | 8 | 0 | r3 |
| Pit | L | 0.05 | 26 | 3 | 2 | 2 | r45 |
| Clown | L | 0.00 | 37 | 0 | 32 | 0 | r2 |
| Losses, sum | | | **319** | **125** | 121 | 32 | |
| Wins, sum | | | 53 | 23 | 143 | 110 | r27-71 in wins |

On SoundWave none of maxwell's 66 carrier hits by r100 were at our wells. Our mana carriers walked to them (§4.2).

### 2.4 Which of our units die first, and where

From a0_deaths. Token is our last telemetry state: F flee, H hold, M march, X explore, V, G and W carrier states.

| game | res | our first 6 deaths (type, round, prog, token) | dead by r150 us C/L | them C/L | our C deaths r ≤ 150 at prog <0.3 / 0.3-0.6 / >0.6 |
|---|---|---|---|---|---|
| Pit | L | L18@0.15F L24@0.15F L31@0.17H C52@0.52F C60@0.67F C66@0.54V | 5/16 | 0/19 | 1/3/1 |
| Quiet | L | L14@0.47H L22@0.29F L22@0.38H L24@0.47H C25@0.29F C28@0.29F | 7/7 | 0/1 | 7/0/0 |
| Clown | L | C5@0.50F C7@0.83F L25@0.50 L29@0.53H C36@0.71F L41@0.56H | 5/18 | 4/20 | 0/2/3 |
| PairedProgramming | L | C11@0.37F C15@0.45F C17@0.44F C22@0.29V L29@0.25M L31@0.43F | 5/20 | 0/19 | 1/4/0 |
| Contraction | L | L61@0.57H L62@0.51H L67@0.53H L70@0.62M C76@0.45 L77@0.40N | 3/11 | 0/2 | 2/1/0 |
| Diagonal | L | L43@0.33F C61@0.25W C64@0.27G L69@0.15H C71@0.18F L81@0.32F | 7/8 | 2/4 | 7/0/0 |
| BatSignal | L | L43@0.49H L51@0.51H L55@0.47H L63@0.45H L82@0.72M L123@0.47H | 0/10 | 0/8 | 0/0/0 |
| SoundWave | L | C15@0.74F L19@0.16H L25@0.26 C31@0.15F C34@0.27X C36@0.05X | 12/13 | 1/10 | 6/0/6 |
| Spots | L | L85@0.36F L101@0.50H L103@0.81M L107@0.37H L121@0.96F L128@0.39M | 0/12 | 4/4 | 0/0/0 |
| BuildSite | L | L63@0.67M L67@0.67M L75@0.74 L81@0.72M L89@0.31H L89@0.33M | 0/15 | 9/20 | 0/0/0 |
| TimesUp | L | L32@0.57H L35@0.50H L35@0.47M L46@0.62N L50@0.50M L52@0.50M | 5/14 | 4/14 | 1/4/0 |
| Marsh | L | L65@0.46F L69@0.46H L74@0.46H L85@0.49M L118@0.30M L124@0.70H | 1/8 | 2/4 | 0/1/0 |
| Movepls | W | C32@0.52V C35@0.54F L39@0.43H L48@0.61M L63@0.84H L74@0.64F | 3/12 | 4/8 | 0/3/0 |
| Rectangle | W | L29@0.51H L35@0.56H L57@0.59F L58@0.74F L69@0.69H L75@0.15M | 0/16 | 3/21 | 0/0/0 |
| Spiral | W | L24@0.46F L31@0.47H L33@0.54F L33@0.47H L45@0.55H L49@0.47H | 0/22 | 3/24 | 0/0/0 |
| Hah | W | L40@0.59F L43@0.59H L44@0.55F L48@0.62F L51@0.62H L59@0.66H | 0/18 | 0/24 | 0/0/0 |
| ThirtyFive | W | C38@0.82F L50@0.52F L53@0.54H L65@0.85F L67@0.64H L75@0.54M | 1/19 | 3/14 | 0/0/1 |
| SweetDreams | W | L39@0.50M L73@0.55H L83@0.70H L91@0.65F L95@0.65F C102@0.65F | 2/9 | 3/8 | 0/1/1 |

Dead by r150 per game:

| | our carriers | our launchers | their carriers | their launchers |
|---|---|---|---|---|
| Losses | 4.2 | 12.7 | 2.2 | 10.4 |
| Wins | 1.0 | 16.0 | 2.7 | 16.5 |

- **Our carriers.** In losses, 25 of our 50 carrier deaths by r150 were at prog < 0.3 and 15 at 0.3-0.6. In wins the split was 0 and 4.
- **Our launchers.** Our first launcher deaths in the fast losses are near home: Pit at prog 0.15-0.17, Diagonal 0.15-0.33, SoundWave 0.16-0.26 and Quiet 0.29-0.47. In wins they are at 0.43-0.62.

### 2.5 Focus fire

From a0_focus: launcher kills by r200, credited from the killer side's per-turn attack rows.

| games | killer | kills | attackers in the kill round | attackers in the last 5 rounds | killed by 3+ in last 5 | median rounds from first hit to death |
|---|---|---|---|---|---|---|
| losses | us | 188 | 1.28 | 1.93 | 0.27 | 31 |
| losses | them | 226 | 1.35 | 2.25 | 0.38 | 16 |
| wins | us | 163 | 1.42 | 2.37 | 0.39 | 27 |
| wins | them | 141 | 1.28 | 2.14 | 0.33 | 22 |

### 2.6 Pressure on our HQ

From a0_hq (r ≤ 300, 25-round buckets).
- **Pressed by r300** (pressure34 = enemy fighter-rounds within r² 34 of the HQ, at least 100 in one bucket): 4 of 12 losses (Quiet r125, PairedProgramming r75, Contraction r175, SoundWave r250) and 0 of 6 wins.
- **Mean pressure34 summed over r ≤ 300:**

  | | on our HQs | on theirs |
  |---|---|---|
  | Losses | 280 | 146 |
  | Wins | 45 | 747 |

- **Share of our HQ turns stopped as threatened** (carrier withheld): 0.08 in losses and 0.01 in wins. Quiet 0.59, SoundWave 0.18.
- **Launchers built by r300**, us/them: Quiet 12/35, Diagonal 14/28, SoundWave 30/51, Contraction 39/61 and Pit 42/64. In wins: Rectangle 85/65, Spiral 89/71, Hah 69/50 and ThirtyFive 90/61.

## 3. What differs between our wins and losses

| feature | losses (12) | wins (6) | source |
|---|---|---|---|
| our build r1-3 | 4L+4C per HQ | 4L+4C per HQ | a0_overview b3 |
| nearest Mn well outside HQ vision (d² > 34) | 8 of 12 | 3 of 6 | a0_econ mnvis |
| median Mn collected by r100, us / them (all 18 games, split by well visibility) | outside vision: 237 / 422 (11 games, 3 W) | inside vision: 622 / 613 (7 games, 3 W) | a0_econ |
| their carrier hits by r100 (sum) / at our wells | 319 / 125 | 53 / 23 | a0_wells |
| our carriers dead by r150 per game | 4.2 | 1.0 | a0_deaths |
| launchers together at contact (median group) us / them | 3.1 / 4.1 | 4.2 / 4.6 | a0_launchers |
| contact turns outnumbered, us / them | 0.15 / 0.01 | 0.08 / 0.05 | a0_launchers |
| launcher kills in 40 rounds after first lethal contact us / them | 25 / 47 | 20 / 27 | a0_first |
| engagements r ≤ 200: kills us / them; their peak > ours / ours > theirs | 373 / 562; 53 / 13 of 95 | 527 / 357; 13 / 15 of 36 | a0_engage |
| engagements at prog < 0.4 (our side): n, kills us / them | 30, 31 / 66 | 9, 82 / 39 | a0_engage |
| in-range turns with no shot, us / them | 0.32 / 0.07 | 0.04 / 0.02 | a0_fire |
| outnumbered while in range, us / them | 0.20 / 0.08 | 0.10 / 0.06 | a0_fire |
| launcher hits per contact turn, us / them | 0.50 / 0.48 | 0.62 / 0.55 | a0_fire |
| our dying launchers alone at last row | 53 / 227 | 17 / 141 | a0_lastcode |
| our dying launchers with objective sighting / recall / guard | 93 / 228 (0.41) | 36 / 141 (0.26) | a0_lastcode |
| our launcher turns with objective sighting / recall / guard (all turns r ≤ 200) | 0.28 | 0.22 | a0_objmix |
| our HQ pressed by r300 | 4 / 12 | 0 / 6 | a0_hq |

**Not different.**
- Our build order.
- The overall objective mix (0.28 against 0.22).
- Hits per contact turn on clear terrain: both sides fire on about 1.00 of their clear in-range turns (a0_cloudfire).
- Edge step-in hit rate: in losses we hit on 0.29 of edge turns against their 0.23 (a0_fire).

**The spread is mostly a consequence of losing numbers.** Over par rounds (both sides have 4+ launchers and their counts differ by at most 1), we were alone (no ally within r² 20) on 0.18 of turns against their 0.15 in losses, and 0.08 against 0.06 in wins (a0_spread). Three losses keep a clear gap at par:

| game | alone us/them | group us/them |
|---|---|---|
| Marsh | 0.37 / 0.16 | 2.7 / 3.8 |
| SoundWave | 0.21 / 0.05 | 2.8 / 5.0 |
| BatSignal | 0.26 / 0.18 | 2.5 / 3.7 |

## 4. Mechanisms, per fast loss

### 4.1 Quiet (r413; 20x20, 1 HQ; our mana well (13,10) at d² 45 from our HQ (16,16))
- **The block.** maxwell's 4 launchers form a static block at (8-9,8-10). It hits our carriers at (13,10) from r7. Their launchers spend 0.57 of their turns at our well; 39 of their 43 carrier hits are there (a0_wells).
- **Our launchers.** They step in one by one (§2.2 trace), kill 0 and lose 5 in 40 rounds (a0_first), and are 0 alive at r50 (a0_traj). They were alone on 0.94 of their turns r20-200 (a0_spread).
- **Our carriers.** Half of our mana-carrier turns by r100 were flee turns (a0_explore). All 7 fatal trips were flee-and-return (a0_ctrips). We collected 20 Mn by r100 against 334 (a0_econ).
- **The end.** The HQ was threatened on 0.59 of its turns, so it withheld carriers. We built 12 launchers by r300 against 35 (a0_hq).

### 4.2 SoundWave (r596; 40x30; our HQs (7,25) and (24,18), theirs (7,4) and (24,11); our Mn wells (32,23) and (16,29))
- **Exploring into the enemy.** Our nearest mana well, at d² 89, is outside HQ vision. Our mana carriers spent 0.76 of their turns by r100 exploring (X). Their median explore position was at prog 0.32, and 133 explore turns were within r² 100 of the enemy HQ (24,11) (a0_explore).
- **Why there.** The map centre (20,15) is d² 32 from that HQ. `Carrier.explore()` (Carrier.java:702-710) sends a mana carrier with no known mana well to the centre first.
- **Result.** 0 Mn by r100 against 449. 8 of our carriers dead by r100 against 1 (a0_econ), and 12 by r150 (a0_deaths). Fatal trips averaged 20.4 explore turns, and 10 of 12 had 10 or more (a0_ctrips).

### 4.3 Diagonal (r489; 40x40, 1 HQ (35,35); nearest Mn well (27,25) at d² 164)
- **The camp.** maxwell spends 0.33 of its launcher turns at our wells; 31 of its 47 carrier hits by r100 are there (a0_wells).
- **Our carriers.** 7 die by r150, all at prog < 0.3 (a0_deaths); 5 of the 7 fatal trips were flee-and-return (a0_ctrips). Mana by r100: 101 against 205.
- **Our launchers.** Launchers at r100: 2 against 8 (a0_traj). Over the par rounds our group averaged 2.8 against 3.7 (a0_spread).

### 4.4 Contraction (r484; 60x60, clouds 0.139; nearest Mn well at d² 137)
- **Contact.** First lethal contact at r52: 4 against 6 near, at prog 0.51. Kills 0 against 5 (a0_first). Launchers at r80: 7 against 16 (a0_traj).
- **Our launchers.**
  - They carried objective hq/site on 0.98 of their turns (a0_objmix) and were outnumbered on 0.26 of their contact turns (a0_launchers).
  - 0.20 of our step-ins went into the reach of 3 or more enemy launchers, against their 0.08 (a0_stepin).
  - On cloud in-range turns we fired 0.40, against their 0.91 (a0_cloudfire).
- **Pressure.** Our HQ was pressed from r175 (a0_hq).

### 4.5 PairedProgramming (r457; 45x20, 3 HQs)
- **Carriers.** Our first 4 deaths were carriers (r11-22, prog 0.29-0.45, a0_deaths). maxwell hit our carriers 54 times by r100, 26 of them at our wells. We hit theirs 4 times (a0_wells).
- **Launchers.** First lethal contact at r20, 6 against 5 near, kills 3 against 5. Launchers at r200: 5 against 20 (a0_traj). Our HQ was pressed from r75 (pressure 554 against 1, a0_hq).

### 4.6 Pit (r379; 60x30, 2 HQs)
- **Our carriers die out.** Launchers stayed level through r150 (10-10). Our carrier count fell from 9 at r100 to 5 at r200, while theirs grew from 12 to 21. Mana was 859 against 1435 at r200 (a0_traj).
- **Ad.** We collected 12 Ad by r100 against 93 (a0_overview). Launchers built by r300: 42 against 64 (a0_hq).
- **Launchers.** Our first 3 launcher deaths were at prog 0.15-0.17 (a0_deaths).
- **Not established.** We did not isolate why our carriers did not recover. This needs an Ad-role and carrier-build trace beyond r100.

### 4.7 Clown (r445; 21x20; walk 6) and BatSignal (r504; 60x20)
- **Clown.** The armies were level until r200: L 12-16 and C 10-12 (a0_traj). The first contact was at r2 and went 5 against 3 in our favour (a0_first).
- **BatSignal.** The armies were level until r250: 11-12 (a0_traj). Our launchers had no sighting objective at all (objective hq/site on 1.00 of turns, a0_objmix). Over the par rounds they were alone on 0.26 of turns against 0.18 (a0_spread). Our first 4 launcher deaths were at prog 0.45-0.51 in mode H, holding (a0_deaths).
- **Not established.** Neither loss has an isolated opening cause. Both were decided after r250, outside this window.

### 4.8 Late losses
- **BuildSite (lost r999 by conquest).** We led on launchers 36-17 at r250 (a0_traj) and pressed their HQ (pressure 1185 against 0 by r300, a0_hq), but did not convert. Cloud in-range turns: we fired on 0.36, they fired on 0.97.
- **Spots (r833).** Cloud turns: 0.60 against 0.92.
- **TimesUp and Marsh (r2000 tiebreaks).** Most of the in-range turns had a cloud involved (666 of 699 and 209 of 209), and we fired on 0.29 and 0.34 of them, against 0.82 and 0.85 (a0_cloudfire).
- **Not analysed.** We did not analyse why these games were lost on islands. Only the cloud-fire gap is measured.

## 5. Our decisions that cause the losses (code paths in src/c_kx0), ranked

### 5.1 Carriers keep working a home mana well that enemy launchers camp (fast losses: Quiet, Diagonal, PairedProgramming, Contraction)

**Code.**
- `Carrier.survive()` (Carrier.java:192-250) flees from the threat. It throws its cargo only at hp ≤ 60 (line 222).
- `gather()` gives up a well only if it is hot (`if (C.HOT && well != null && hot(well)) well = null;`, line 340).
- `front()` (lines 498-502: `homeD2 > C.HOT_HOME_D2 && 100L * homeD2 >= C.HOT_FRONT_PCT * enemyD2`) never lets a well within r² 64 of home, or less than 36% of the way to the enemy, become hot.
- So a camped home well stays the carrier's target, and the carrier loops flee, return, flee until it dies.

**Evidence.**
- 24 of 50 fatal carrier trips in losses were flee-and-return, against 3 of 6 in wins (a0_ctrips).
- 25 of 50 carrier deaths were at prog < 0.3 in losses, against 0 in wins (a0_deaths).
- Their carrier hits at our wells: 125 in losses against 23 in wins (a0_wells).

**Prior attempts** (TRAINING_LOG, grep):
- An earlier census of ranked games already found carrier deaths at home wells (prog quartiles 0.10/0.20/0.31) and noted that c_well6's hot memory covers front wells only (TRAINING_LOG.md:2017-2020).
- The flee redesigns c_flee1 and c_flee9 gained locally over all 103 maps (114/206 and 116/206 against c_gp1). Both failed the panel-map screen at 8/20 (TRAINING_LOG.md:2063-2068, 2147).
- The abl4 arm `HOT_HOME_D2 48 + HOT_FRONT_PCT 20` scored net 0 (TRAINING_LOG.md:2341). It loosens `front()`, but home wells still never turn hot.
- Abandoning a camped home well has not been tried as such.

**Suggested changes** (not run):
- Mark any well hot, home wells included, after an enemy launcher has been seen within r² 20 of it on, for example, 3 of the last 5 turns.
- While every mana well of the role is hot, hold mana carriers at the HQ, or switch them to Ad, instead of sending them back.
- The HQ could also skip carrier builds while its nearest mana well is hot, saving Ad for later.

### 5.2 Launchers that commit on a partial view, one at a time (Quiet, Contraction, the exchange after first contact)

**Code.**
- `Launcher.fight()` (Launcher.java:248-252) sets `superior = G.nAllyFighters + 1 > G.nEnemyFighters` and `ahead = ... >= 2` from the robots in vision (r² 20).
- When ahead, the base scoring steps in to fire. Vision misses enemies that can reach the new tile (r² 26 after a move) and allies that do not see the enemy and will not follow.
- With `C.ARMY = false` (C.java; checked in `march()` at Launcher.java:425) there is no forming or regrouping before contact.
- Sighting objectives (`SIGHTING_R2` 64 at line 934, recall `RECALL_R2` 225 at lines 935-956, guard `GUARD_R2` 400 at lines 958-968) send each launcher to the fight as it becomes free.

**Evidence.**
- The Quiet trace (§2.2): 4 step-ins into a static 4-block, each while seeing 1 enemy, 0 kills.
- Blind step-ins in losses, us against them: 0.13 against 0.07. Step-ins into the reach of 3 or more: 0.12 against 0.06. In wins both sides are at 0.02 (a0_stepin).
- Our dying launchers in losses were alone on 53 of 227 deaths against 17 of 141 in wins, and had a sighting, recall or guard objective in 41% of deaths against 26% (a0_lastcode).
- That objective's share of all turns is 0.28 against 0.22 (a0_objmix), so launchers on it die out of proportion in losses (0.41/0.28 against 0.26/0.22).
- After the first lethal contact we killed 25 launchers and lost 47 (a0_first).

**Caveat.** Cohesion as such is a known negative on our panel: `C.ARMY` on scored -23 with GROUP_MIN 2 and -18 with GROUP_MIN 3, and off scored +20 (ARMY off: LEARNINGS.md:118-122; GROUP_MIN arms: TRAINING_LOG, c_loose1 entries). The cue here is narrower: a launcher that would step in should not count allies that cannot see the target, and should not step into a tile inside the reach of an unseen block.

**Suggested changes** (not run):
- Count only allies that can hit or reach the target tile when deciding `ahead`.
- Assume at least the enemy count of the last shared sighting near the target.
- When an enemy stands still at the edge of vision and our side is not ahead by 2 among launchers that can hit, hold for one turn instead of stepping in.

### 5.3 No fire at enemies on clouds (TimesUp, Marsh, Spots, BuildSite, Contraction)

**Code.**
- `Launcher.shoot()` (Launcher.java:165-182) loops over `G.enemies` (sensed robots) only.
- `run()` (Launcher.java:57-59) enters `fight()` only when `hasHittableEnemies()` (line 139). Otherwise it marches.
- `track()` (line 198) remembers the enemy fighters, but only for telemetry.
- An enemy on a cloud is invisible beyond r² 4, and a launcher on a cloud sees only r² 4. Attacks need no vision (RULES.md §6.3, line 400, and the act-location rule at line 284).

**Evidence.** In-range turns with a cloud involved (a0_cloudfire):

| range | turns, us / them | fired | hit anything | hit a launcher |
|---|---|---|---|---|
| r ≤ 200 | 1172 / 1233 | 0.33 / 0.86 | 0.33 / 0.39 | 0.28 / 0.34 |
| all rounds | 9442 / 10779 | 0.33 / 0.86 | 0.33 / 0.41 | 0.30 / 0.34 |

On clear turns both sides fire on about 1.00. In losses, the share of in-range turns with no shot is 0.32 for us against 0.07 for them (a0_fire). TimesUp: 0.68 against 0.17. Marsh: 0.66 against 0.15.

**Prior attempt.** c_blind1 shot unseen cloud tiles by a rotating index. c_blind2 added memory targeting, the last-seen tiles of enemy fighters. Both were rejected on 2026-10-14: about 20-24 outside-vision hits a game from 10,551-11,260 shots (0.2%), no measurable effect, and c_blind2 identical to c_blind1 in 100 of 100 panel cells (TRAINING_LOG 2026-10-14 13:23 and 15:19 PDT).

**What maxwell's replays add.**
- On cloud turns maxwell fires 0.53 more often than we do (0.86 against 0.33) and hits 0.08 more often (0.41 against 0.33).
- If its visible-target shots match ours, its extra shots hit about 15% of the time (0.08 / 0.53). This is an estimate, not verified per shot: it is far above c_blind's 0.2%.
- The identical outcomes suggest c_blind2's memory path rarely fired, possibly because of the cloud cooldown multiplier noted in TRAINING_LOG 2026-10-14 10:02 PDT (`C.BLIND_MEM_DEBT 0`).

**Suggested change** (not run): first check whether c_blind2's memory shots fired at all. If they did not, retry fire at the last-seen tile of an enemy launcher seen within r² 16 in the last 1-2 rounds. The expected gain is about 0.04-0.06 launcher hits per cloud turn (0.30-0.34 against 0.28-0.34 above). It matters on cloud-heavy maps (2 of our 12 losses went to tiebreak there), not in the fast losses.

### 5.4 Mana carriers exploring toward the map centre (SoundWave)

**Code.** `Carrier.explore()`, `centreTried` (Carrier.java:702-710): a mana-role carrier with no known mana well walks to `(W/2, H/2)` first.

**Evidence.** On SoundWave (§4.2): 0.76 explore share, 133 explore turns within r² 100 of the enemy HQ (a0_explore), 0 Mn by r100 and 12 carriers dead by r150. In the other 17 games the explore share is 0.24 or less (a0_explore).

**Prior attempt.** The econ-weak-maps diagnosis named SoundWave's centre-first leg "into walls or the enemy half" (TRAINING_LOG.md:2110-2111).
- c_expl1 (frontier exploration) won SoundWave on both sides in local play and went +7 over 206 games against c_gp1.
- On the panel it scored 68 against c_gp1's 71 and was rejected, because "the panel's maps and opponents barely exercise blind search" (TRAINING_LOG.md:2115, 2134-2136).
- maxwell's replica map pool does exercise it (SoundWave here), which argues for a narrow switch rather than a rewrite.

**Suggested change** (not run): skip centre-first when the centre is within r² 100 of a known or predicted enemy HQ, using the symmetry candidates. Search the half of the map on our side instead.

### 5.5 HQ withholds carriers when threatened (consequence, low priority)

**Code.** `HQ.build()` (HQ.java:93) builds a carrier only `if (!threatened && ...)`. `threatened` comes from `inDanger()` (HQ.java:153-161) when `C.HQ_THREAT` is not 0.

**Evidence.** Threatened share: Quiet 0.59 and SoundWave 0.18, against 0.01 across the wins (a0_hq). It follows from the losses in §5.1 and §5.2 rather than starting them.

## 6. Caveats and unverified points

- **Coverage.** These are 18 games against one opponent, on the replica ladder. maxwell's code is unknown, so "its block holds still" and "it fires blind" describe its replays, not its rules.
- **How maxwell's cloud shots hit is unverified.** They hit on 0.41 of cloud in-range turns against our 0.33. We did not check whether it targets remembered positions. The 15% hit rate of its unseen shots is derived on the assumption that its visible shots match ours.
- **a0_stepin is approximate.** It uses the other side's start-of-turn positions in the same round, which can be one move stale because robots act in id order.
- **The objective codes are this turn's code** (Telemetry.launcherCode). The replica replays carry no indicator dots, so the finer OBJ kinds (recall 7, guard, site 8) cannot be split out. "Sighting" means objective kind 0: sighting, recall or guard.
- **The Pit carrier collapse after r100**, Clown and BatSignal after r250, and the island tiebreaks in TimesUp and Marsh are not explained here.
- **None of the suggested changes has been run.** Each needs a local A/B on the panel. §5.2 in particular touches the micro that the panel tuned (ARMY off +20, MICRO2 parity hold).

## 7. Reproduce

All scripts are in `research/diagnosis/2026-10-19-top2/scripts/`. Rebuild the dumps first: `a0_dump.sh` (36 `--sa` dumps, about 3.5 minutes, flock'd). Telemetry codes come from `tools/replay-dump.sh ... --tele-turns` into `scratchpad/top2/a0/ext/<m>/`.

| script | args used here | what it measures |
|---|---|---|
| a0_overview.py | | per-game builds, alive counts, resources, first HQ pressure |
| a0_traj.py | | L / C / Mn at r30-r250 |
| a0_econ.py | | mana well visibility, first mana, idle carriers, carrier deaths by r100 |
| a0_launchers.py | 150 | group, outnumbered, still-firing, carrier and launcher hits, arrival |
| a0_wells.py | 100 | launchers at the other side's mana wells, carrier hits there |
| a0_deaths.py | | first deaths, deaths by r150, carrier death prog bands |
| a0_engage.py | 200 | engagements (extract) by starting balance |
| a0_first.py | | first and first lethal contact, kills in the next 40 rounds |
| a0_fire.py | 200 | fire discipline in range and at the edge |
| a0_cloudfire.py | 200 and 2000 | fire, hit and launcher hit on cloud and clear in-range turns |
| a0_lastcode.py | 200 | last telemetry code and local counts of our dying launchers |
| a0_objmix.py | 200 | our launchers' objective and mode mix per turn |
| a0_hq.py | 300 | HQ stop codes, pressure, builds |
| a0_focus.py | 200 | attackers per kill, time to kill |
| a0_spread.py | 20 200 | alone share, group size, par-round comparison |
| a0_stepin.py | 200 | step-ins into unseen reach |
| a0_ctrips.py | 150 | our carriers' fatal trips (flee and return, explore) |
| a0_explore.py | 100 | mana-role carriers' explore and flee shares, explore near the enemy HQ |
| a0_trace.py | 9928 1 8 26 | per-round launcher trace (Quiet first contact) |
