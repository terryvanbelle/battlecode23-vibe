# carlguo866 early collapses: the mechanism (Analyst 1)

2026-10-19, 12:55 PDT. Our build was c_eco3 (sub 192), which is `src/c_kx0` with its switch constants at their defaults. Match 9888 used sub 189 and match 9900 used sub 191. Sources:
- replays `build/top2/replays/<match>.bc23`;
- extracts `matches/<match>/extract/*.csv`;
- per-turn dumps and telemetry, which live outside the repo (paths in the last section).

I read no other team's source code and no 2023 post-mortem. I ran no games, did not edit `src/` and did not commit.

The two Frog games, 9888 g0 and 9921 g0, are the same replay. Every pooled number below counts Frog once: **8 distinct collapse games and 7 early wins**.

## Summary

The opening is identical. The collapse is an **economic squeeze on our home mana well, which our carriers do not recognise as dangerous**. It goes in five steps.

1. **The first exchange.** Carl comes out of the first big fight with more launchers alive (counted 10 rounds after it) in 6 of 8 collapses; we do in 7 of 7 early wins. Our wave arrived split in LightWork and Barcode. TreasureMap and maptestsmall were even 4v4 fights. Sneaky was lost from 11/5.
2. **Carl moves onto our home mana well.** Its launchers park on our home Mn well:
   - The first carl launcher arrives there at r3–39.
   - Before r150, carl has 2728 launcher-turns within r²34 of our home Mn wells against our 1727.
3. **Our carriers keep walking into the camp.** That well is a "home" well by `Carrier.frontGate` (Carrier.java:501–503), so it never turns hot (Carrier.java:215). Our carriers flee and come back:
   - 72 trips, 17 deposits, 34 deaths;
   - 3.9 separate exposures per dead carrier;
   - 80 of 82 carriers lost before r150 were killed by launchers.
4. **Mana stops.** Our collected Mn flatlines once the carriers are gone: 1331 against 2558 at r100. The HQ then withholds new carriers while threatened (HQ.java:93, 507 HQ-turns). Ad piles up (1056 against 520 banked at r200), and launchers come only from passive Mn, one at a time (HQ.java:59/92, LAUNCHER_BATCH=1, ARMY=false).
5. **Reinforcements die alone.** Each new launcher meets the camp 3.8 tiles from our HQ, 9.9 rounds after birth:
   - alone 53%, outnumbered 27%;
   - 71% die within 20 rounds.

   Carl's later launchers: alone 9%, dead within 20 rounds 6%.

**Micro is not the gap.** Hits per 100 contact turns are 51.0 for us and 48.0 for carl. The local numbers are the gap: we are outnumbered on 21% of contact turns and carl on 7%.

**Special cases:**
- **Frog** adds two of our own bugs:
  - The army sieges carl's other HQ while carl raids our upper well, and the guard and recall rules never call it home (Launcher.java:953/966).
  - Four mana-role carriers locked onto an Ad well and mined 380 kg of Ad (Carrier.java:356–373).
- **Jail** is a basics failure: two of seven carriers stood still for 162 and 172 rounds.

The early wins are the mirror image. There, our launchers sit on carl's wells:
- we hit carl's carriers 479 times, against 136 hits on ours;
- carl's HQs withhold and bank Ad (1572 against 630);
- our home-well trips almost all end in deposits (179 of 188).

## 1. The games

Source: `a1_table.py` (built by r100, Mn collected by r100) and `a1_snow.py` (launchers alive and carriers lost, from timeline). Values are us/carl.

| match g | map | size, HQs | L built ≤r100 | C built ≤r100 | L alive r30 | r50 | r100 | r150 | C lost ≤r100 | Mn coll r100 |
|---|---|---|---|---|---|---|---|---|---|---|
| 9888 g0 (=9921 g0) | Frog | 39x39, 2 | 14/18 | 15/12 | 8/7 | 7/6 | 8/12 | 1/14 | 5/0 | 148/430 |
| 9888 g2 | TreasureMap | 21x21, 1 | 6/7 | 5/6 | 3/3 | 1/2 | 0/2 | 1/6 | 5/0 | 103/253 |
| 9900 g0 | Jail | 20x30, 1 | 6/8 | 6/5 | 3/1 | 1/1 | 1/3 | 1/8 | 2/0 | 30/181 |
| 9915 g1 | LightWork | 30x30, 2 | 14/20 | 12/12 | 2/9 | 0/8 | 1/13 | 0/22 | 10/0 | 224/508 |
| 9915 g2 | maptestsmall | 20x20, 1 | 9/10 | 6/6 | 1/2 | 3/1 | 0/4 | 0/12 | 6/0 | 153/373 |
| 9929 g2 | Sneaky | 20x20, 3 | 21/20 | 18/18 | 13/14 | 9/8 | 4/6 | 0/8 | 9/0 | 277/351 |
| 9931 g0 | Barcode | 20x20, 2 | 12/13 | 12/12 | 6/9 | 0/6 | 0/8 | 0/13 | 10/0 | 104/190 |
| 9931 g2 | Star | 30x30, 2 | 15/17 | 12/12 | 9/7 | 12/7 | 7/7 | 4/8 | 10/1 | 292/272 |
| **collapse sum** | | | **97/113** | **86/83** | | | | **7/91** | **57/1** | **1331/2558** |
| 9912 g0 | BowAndArrow | 35x25, 2 | 20/10 | 12/5 | 4/4 | 4/1 | 13/0 | 21/0 | 6/5 | 493/0 |
| 9914 g1 | PairedProgramming | 45x20, 3 | 23/21 | 20/18 | 15/12 | 11/9 | 10/5 | 15/4 | 0/5 | 527/173 |
| 9900 g2 | Pizza | 30x30, 2 | 22/15 | 14/11 | 10/8 | 12/5 | 13/2 | 19/4 | 0/3 | 598/347 |
| 9921 g2 | Scatter | 50x30, 2 | 23/21 | 14/13 | 10/10 | 10/3 | 10/7 | 12/7 | 1/0 | 617/577 |
| 9925 g2 | Risk | 20x20, 1 | 10/10 | 7/5 | 4/4 | 3/2 | 4/4 | 6/2 | 0/1 | 252/260 |
| 9925 g0 | Piglets | 60x40, 2 | 16/14 | 12/12 | 10/10 | 10/8 | 7/6 | 12/7 | 2/1 | 274/255 |
| 9900 g1 | Piglets | 60x40, 2 | 16/13 | 12/13 | 10/10 | 9/8 | 7/5 | 11/8 | 0/0 | 375/261 |
| **early-win sum** | | | **130/104** | **78/77** | | | | **96/32** | **9/15** | **3136/1873** |

The sums are added from the rows above. The collapses are mostly small maps (five of eight are 21x21 or smaller), but Risk (20x20) is an early win, so map size alone does not separate the groups.

## 2. Carl's opening: same builds, same timing, more forward

- **Identical builds.** The first builds are identical on every 2-HQ map: `1:L 1:L 1:L 1:L 1:C 1:L 1:L 1:L 1:L 1:C 2:C 2:C` for both sides (`a1_table.py`, column first_builds). On 1-HQ maps both sides build 4 launchers and 4 carriers in rounds 1–2 and add the next launcher at r21–26 (24 and 26 in Jail, 26 in TreasureMap and maptestsmall).
- **No production lead by r100.** Carl has 113 launchers built against our 97, and 83 carriers against our 86. The collapse is not a production lead in the opening.
- **Where it fights: forward, then on our well.**
  - Carl's opening wave makes first contact 9.0 tiles from its own HQ on average, against our 6.4 (`a1_feed.py`, cohort "wave", collapses).
  - Carl's launchers then spend a median 54% of their turns in our half before r150. In early wins that share is 22%. Ours spend 16% in its half (`a1_pos.py`, column enemy_half, medians over games).
- **Timing of the raid.** The first carl launcher within r²34 of our home Mn well (`a1_home.py`):

  | map | first carl launcher at our well |
  |---|---|
  | Frog | r35 |
  | TreasureMap | r7 |
  | LightWork | r39 |
  | maptestsmall | r3 |
  | Sneaky | r23 |
  | Barcode | r26 |
  | Star | r13 |
  | Jail | never: our carriers never got there, see §7 |

**Who holds the home mana wells?** Launcher-turns within r²34 of each side's home Mn wells, r<150 (`a1_home.py SA 150 34`):

| group | our wells: our L-turns | our wells: carl L-turns | our carriers killed there | carl's wells: our L-turns | carl's wells: carl L-turns | carl carriers killed there |
|---|---|---|---|---|---|---|
| collapse (8) | 1727 | **2728** | **62** | 920 | 1545 | 6 |
| early win (7) | 3001 | 154 | 10 | 1988 | 1271 | 14 |

In collapses, carl spends more launcher-turns on our wells than on its own. 62 of our 82 carrier deaths before r150 (`a1_ckill.py`) happen within r²34 of our home Mn wells.

## 3. The first engagements

**First large engagement.** This is the first engagement with joiners ≥ 8 and r0 < 200 (`a1_first.py`). "L alive after" is counted at r1+10.

| map | rounds | where (prog_us) | start us/carl | L dead us/carl | C dead us/carl | L alive after |
|---|---|---|---|---|---|---|
| Frog | 10–78 | 0.66 | 0/4 | 3/6 | 1/0 | 9/8 |
| TreasureMap | 9–53 | 0.52 | 4/4 | 5/3 | 3/0 | 0/2 |
| Jail | 3–118 | 0.82 | 4/4 | 6/6 | 2/0 | 1/4 |
| LightWork | 3–103 | 0.72 | 4/8 | 13/7 | 10/0 | 1/15 |
| maptestsmall | 3–28 | 0.48 | 4/4 | 4/3 | 0/0 | 1/2 |
| Sneaky | 19–192 | 0.42 | 11/5 | 29/22 | 24/2 | 0/12 |
| Barcode | 7–72 | 0.50 | 4/4 | 12/5 | 5/0 | 0/8 |
| Star | 13–49 | 0.50 | 4/4 | 1/4 | 0/0 | 12/7 |
| *early wins* | | | | | | 4/1, 10/5, 13/3, 10/4, 3/2, 12/7, 11/6 |

- **Collapses:** we come out behind in 6 of 8. Frog and Star are the two we come out ahead in.
- **Early wins:** we come out ahead in 7 of 7.
- **Frog's "1/20" deficit is not from the first fight.** We won that fight (3 of our launchers dead against 6 of carl's). The deficit builds between r100 and r150: launchers alive go from 8/12 to 1/14 (`a1_snow.py`, `a1_alive.py`).

**All engagements before r250, from our side** (`a1_eng.py 250`, 8 distinct games):

| group | eng. | won | lost | carl hit first | we were behind at start | started with 0 of ours | kills us/carl (all types) | carl kills in our half | launchers joining us/carl |
|---|---|---|---|---|---|---|---|---|---|
| collapse | 68 | 15 | 52 | 50 | 43 | 32 | 100/276 | 169 | 196/427 |
| early win | 83 | 61 | 19 | 22 | 11 | 3 | 280/165 | — | 484/261 |

The engagement lists after the first fight show the feeding directly (`a1_eng.py 250 -v`). Each entry gives our and carl's launchers at the start, then the joiners:
- maptestsmall 111–113: 0/7 at the start, then 1/7 joining. 151–158: 0/9, then 1/7. 186–188: 0/14, then 1/9.
- LightWork 176–179: 0/11, then 2/13. 211–214: 0/12, then 2/18.
- Sneaky 211–222: 0/8, then 1/9. 226–230: 0/10, then 1/10. 236–239: 0/12, then 1/9.

## 4. Do we feed launchers in one at a time? Yes

For each launcher born before r200, I took its first turn with an enemy launcher within r²20 (`a1_feed.py SA 200`). The figures are means. "Own" counts the launcher itself plus its allies within r²20. "Wave" means born by r2; "later" means born after r2.

| group | side | cohort | launchers with a contact | own | enemy | alone | outnumbered | died ≤20 rounds after | age at contact | tiles from own HQ | ≤8 tiles |
|---|---|---|---|---|---|---|---|---|---|---|---|
| collapse | us | wave | 54 | 5.33 | 1.54 | 0.00 | 0.02 | 0.54 | 16.9 | 6.4 | 0.81 |
| collapse | us | **later** | 86 | **2.21** | 1.86 | **0.53** | **0.27** | **0.71** | **9.9** | **3.8** | **0.91** |
| collapse | carl | wave | 52 | 4.88 | 1.58 | 0.02 | 0.00 | 0.46 | 19.4 | 9.0 | 0.52 |
| collapse | carl | later | 124 | 4.60 | 1.23 | 0.09 | 0.05 | 0.06 | 24.2 | 9.8 | 0.35 |
| early win | us | later | 110 | 4.40 | 1.19 | 0.15 | 0.03 | 0.19 | 23.2 | 8.8 | 0.50 |
| early win | carl | later | 99 | 2.86 | 1.31 | 0.17 | 0.04 | 0.37 | 14.7 | 7.8 | 0.78 |

- **Our reinforcements in collapses meet the enemy at our door.** First contact is 3.8 tiles from our HQ, 9.9 rounds after birth, and the launcher is alone half the time.
- **Carl's reinforcements arrive grouped.** At first contact they average 4.6 launchers of their own.
- **Launcher deaths agree** (`a1_lage.py`, r<200):
  - Ours: 138 dead in collapses, median age 26, 84 dead at age ≤30, 91 within 8 tiles of our HQ.
  - Carl's: 96 dead, median age 48.5, 24 at age ≤30.

## 5. Do our carriers die to its launchers? Yes, at our own well, again and again

**Who kills them** (`a1_ckill.py 150`, r<150):

| group | side | carriers dead | killed by launchers | cargo lost | mean age |
|---|---|---|---|---|---|
| collapse | us | **82** | 80 (2 by HQ aura) | 437 kg | 51.1 |
| collapse | carl | 6 | 6 | 0 | 94.2 |
| early win | us | 12 | 7 | 69 kg | 82.2 |
| early win | carl | 43 | 43 | 81 kg | 89.6 |

**Where they die** (`a1_cdeath.py`, r<200):
- 94 of our 108 dead carriers died within 8 tiles of our HQ. Carl lost 8.
- The state at death was F (fleeing) for 49, G (walking to a well) for 16, C (collecting) for 13 and V for 13.

**Exposure** (`a1_cexp.py SA TT 150`). An exposed turn is a carrier-turn that starts with an enemy launcher within r²20.

| group | side | carrier-turns | exposed | share | dead | separate exposures per dead carrier |
|---|---|---|---|---|---|---|
| collapse | us | 5668 | 1821 | **0.32** | 82 | **3.9** |
| collapse | carl | 10523 | 778 | 0.07 | 6 | 7.0 |
| early win | us | 10815 | 455 | 0.04 | 12 | 5.3 |
| early win | carl | 8246 | 894 | 0.11 | 43 | 6.3 |

Our exposed turns in collapses, by telemetry state:

| state | turns |
|---|---|
| F (flee) | 792 |
| C (collect) | 471 |
| W (wait at a crowded well) | 181 |
| G (walk to the well) | 167 |
| R (return) | 101 |

A dead carrier had been exposed 3.9 separate times on average. The carrier flees, the threat leaves its vision, and it walks back to the same well.

**Why the carrier walks back** (`a1_front.py 150`). `frontGate` (Carrier.java:501–503) is evaluated on each of our Mn wells with a first collect before r150, using the true HQs:

| map | well | homeD2 | enemyD2 | gate | trips | deposits | deaths | our C deaths within r²34 |
|---|---|---|---|---|---|---|---|---|
| Frog | (19,6) | 90 | 90 | front | 9 | 4 | 2 | 2 |
| Frog | (26,24) | 101 | 481 | home | 4 | 3 | 1 | 1 |
| TreasureMap | (12,11) | 37 | 101 | home | 7 | **0** | 3 | 6 |
| Jail | (8,21) | 25 | 52 | home | 1 | 0 | 1 | 4 |
| LightWork | (6,16) | 64 | 250 | home | 8 | 2 | 3 | 6 |
| maptestsmall | (13,7) | 50 | 68 | home | 9 | 4 | 5 | 5 |
| Sneaky | (8,19) | 49 | 445 | home | 24 | 3 | 10 | 19 |
| Barcode | (10,4) | 25 | 169 | home | 6 | **0** | 4 | 14 |
| Star | (11,9) | 74 | 221 | home | 10 | 4 | 6 | 4 |
| **collapse, 9 home wells** | | | | | **72** | **17** | **34** | 59 |
| **early win, 9 home wells** | | | | | **188** | **179** | **6** | 16 |

A home well cannot turn hot. The hot marking in `survive()` requires `front(well)` (Carrier.java:215). `gather()` drops a well only if it is hot (Carrier.java:340). So nothing in the carrier stops it from going back to a home well that carl's launchers are holding.

Carl's carriers at the mirrored wells (`a1_wells.py 150`):

| map | well | trips | deposits | deaths |
|---|---|---|---|---|
| Frog | (12,24) | 24 | 24 | 0 |
| LightWork | (23,16) | 18 | 18 | 0 |
| maptestsmall | (9,0) | 15 | 15 | 0 |
| Barcode | (9,15) | 8 | 8 | 0 |
| Star | (18,9) | 16 | 16 | 0 |

## 6. Why our Mn falls behind

1. **The carriers die before they deliver** (§5). The collapse sum of collected Mn at r100 is 1331 against 2558. Our carriers alive collapse before our launchers do (`a1_alive.py`). Carriers alive at r100, us/carl:
   - TreasureMap 0/6, LightWork 2/12, maptestsmall 0/6, Barcode 2/12, Star 2/11;
   - Sneaky 9/18 at r100, then 1/16 at r125.

   Our collected Mn then stops for good:

   | map | our Mn collected stays at | from |
   |---|---|---|
   | TreasureMap | 103 | r100 |
   | Jail | 30 | r50 |
   | maptestsmall | 153 | r100 |
   | Barcode | 104 | r100 |
   | LightWork | 293 | r150 |
   | Sneaky | 334 | r175 |
   | Star | 351 | r200 |

   Carl's goes on climbing, to 470–1820 at r250.
2. **The HQ stops replacing carriers while threatened.** `inDanger()` (HQ.java:153–161) is true when enemy fighters outnumber ours and one is within r²20 of the HQ. Then HQ.java:93 builds no carrier. `a1_hq.py 200` gives:
   - **t (a carrier withheld under threat) on 507 HQ-turns** in collapses, 43 in early wins;
   - carriers built r26–200: 55 for us, 56 for carl, so replacement keeps pace only in count;
   - **Ad banked at r200: 1056 for us, 520 for carl.** In early wins carl banks 1572 against our 630.
3. **Launchers then come from passive income alone.** Passive income is 1.2 Mn per round per HQ (RULES.md:108). That is one 45-Mn launcher about every 37 rounds per HQ, and a threatened HQ builds it at once (HQ.java:59 `batchOK = threatened || ...`, HQ.java:92). Launchers built r26–200 (`a1_hq.py`):
   - collapses: 85 for us, 167 for carl;
   - early wins: 190 for us, 108 for carl.
4. **Frog only: mana carriers mined Ad** (`a1_role.py`, `a1_frogad.py`).
   - Before r150, 5 mana-role carriers collected 469 kg of Ad. All 14 mana-role carriers together collected 301 kg of Mn.
   - Four of them have telemetry at their first Ad collect. Their role bit was mana at birth and never changed:

     | carrier | born | first Ad collect | explore turns before it | Ad collected | Mn collected |
     |---|---|---|---|---|---|
     | 10332 | r46 | r47 | 0 | 90 | 0 |
     | 10343 | r2 | r26 | 17 | 109 | 0–2 |
     | 11103 | r1 | r49 | 34 | 90 | 0–2 |
     | 11189 | r2 | r44 | 35 | 91 | 0–2 |

   - All four mined at the Ad well (26,6), 3.6 tiles from our HQ (28,9).
   - A mana carrier can reach a well of any type before 60 search turns only by the cool branch: Carrier.java:356–360 sets `searchTurns = C.WELL_SEARCH_TURNS` when `nearestCool(home, role)` is null, then :373 takes `nearestCool(home, 0)`. Carrier 10332 took the Ad well the turn after birth, so this branch ran.
   - The Ad well is a home well (homeD2 13), so :340 never drops it. No other game in either group shows a mana-role carrier on Ad.
5. **Jail only: stuck carriers** (`a1_stuck.py 200 50`).
   - Carriers 12472 and 12883 (born r2 at (4,19) and (5,19)) stood still for 162 and 172 consecutive rounds, in state G for 149 and 155 turns. Launchers killed them at r165 and r175.
   - The one carrier that reached (8,21) collected 30, then spent 145 turns in R and died at r192 (trips.csv).
   - Carl never stood on our Jail well (0 launcher-turns, `a1_home.py`). This is a navigation failure on our side, not carl's play.

## 7. Micro: equal shooting, unequal numbers

Contact turns before r150, pooled (`a1_micro.py SA 150`):

| group | side | contact turns | outnumbered | alone | ahead by ≥2 | L hits per 100 contact turns | fire→move | move→fire | moves away | lethal hits on L | hits on carriers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| collapse | us | 1652 | 0.21 | 0.21 | 0.40 | **51.0** | 139 | 164 | 345/700 | 77 | 153 |
| collapse | carl | 2292 | 0.07 | 0.11 | 0.64 | **48.0** | 230 | 140 | 589/1000 | 109 | **692** |
| early win | us | 1492 | 0.04 | 0.14 | 0.63 | 64.7 | 253 | 316 | 351/679 | 110 | 479 |
| early win | carl | 1526 | 0.05 | 0.14 | 0.49 | 61.8 | 363 | 183 | 579/788 | 84 | 136 |

- **The per-launcher hit rate is the same.** The parity hold (Launcher.java:339) and the `ahead` test (Launcher.java:252) are not what separates the groups.
- **Carl kites more.** It fires and then moves away more often: 230 fire→move against our 139, and 59% of its contact moves go away against our 49%. This is a secondary difference.
- **Our waves arrive split** (`a1_pos.py`, mean group size at contact, us/carl):

  | game | group at contact | alone | outnumbered |
  |---|---|---|---|
  | Barcode | 1.98/3.35 | 0.46/0.03 | 0.46/0.02 |
  | LightWork | 2.17/6.51 | 0.38/0.00 | — |

## 8. Mechanism per game

| game | when launchers diverge (L alive) | main mechanism | key numbers (script) |
|---|---|---|---|
| Frog | r100–150 (8/12 to 1/14) | The army sieges carl's lower HQ (10,9) while carl's 4–7 launchers raid our upper well (26,24). Four mana carriers are locked on Ad. | Our centroid (17,8)–(17,10) r61–90 at prog 0.67–0.71; carl's (22,23) r61–70 (`a1_traj.py`). Raids r42–87 at prog_us 0.24–0.41, 0–1 of ours against 3–4 of carl's, first hit on a carrier. Siege fight r96–178: start 2/6, kills 8/28 (`a1_eng.py -v`). Mana-role Ad 469 kg (`a1_role.py`). |
| TreasureMap | r30–50 (3/3 to 1/2) | Even 4v4 mid fight lost. Carl's 1–3 survivors (r31–100), then 6–7 (r111–160), sit in our half at median prog 0.56–0.82, around our well (12,11). | Dead L 5/3 (`a1_first.py`). Well: 7 trips, 0 deposits (`a1_front.py`). Our carriers alive 0 at r100 (`a1_alive.py`). |
| Jail | r100–150 (1/3 to 1/8) | Basics: stuck carriers, Mn 30 total. Our wave went to carl's HQ (first fight at prog_us 0.82: 4/4, kills 6/6, lost). | `a1_stuck.py`; `a1_eng.py -v` |
| LightWork | r1–30 (2/9 at r30) | Carl's 8 launchers move as one group (median 7.5) against our two groups of 4. Carl is in our half 68% of the time. | Outnumbered 0.41 (`a1_micro.py`). First fight start 4/8, dead L 13/7, our carriers 10/0 (`a1_first.py`). |
| maptestsmall | r75–100 (3/4 to 0/4) | Our 4 advance to median prog 0.42–0.58 (r1–30) against carl's 4, which hold at prog 0.14–0.26 near its HQ (r1–40). Carl pushes onto our well from r81–90 (prog 0.55–0.79). | First fight 4/3 dead L. Well (13,7): 9 trips, 5 deaths. First carl launcher at our well r3 (`a1_traj.py`, `a1_front.py`, `a1_home.py`). |
| Sneaky | r100–150 (4/6 to 0/8) | 12v12 waves (3 HQs). One running fight r19–192 that we start at 11/5 and lose. Carl's median launcher sits in our half (prog 0.50–0.77) from r21 to r180. | Dead L 29/22, dead C 24/2 (`a1_first.py`). Well (8,19): 24 trips, 3 deposits, 10 deaths, 19 carrier deaths nearby (`a1_front.py`). |
| Barcode | r30–50 (6/9 to 0/6) | Split wave lost 12/5. Carl's 6–14 launchers centre on x 9–11, y 5–7, 1–3 tiles from our well (10,4), from r41 to r160. | `a1_first.py`, `a1_traj.py`. Well: 6 trips, 0 deposits, 14 carrier deaths nearby (`a1_front.py`). |
| Star | r125–250 (8/6 to 0/23) | First fight won (dead L 1/4). Carl's raiders were at our well (11,9) from r13 and killed carriers: alive 2/11 at r100. Mid fight r38–204 lost (joins 20/22, kills 15/31). | Mn was even at r100 (292/272) and flat from r200 (`a1_alive.py`, `a1_eng.py -v`). |

## 9. Comparison with the early wins

The early wins run the same machine in reverse:
- We come out of the first fight ahead (7 of 7).
- Our launchers then stand on carl's wells: 1988 launcher-turns there against carl's 1271.
- We hit carl's carriers 479 times; carl hits ours 136 times.
- Carl's HQs carry the pressure: pressure34 sum 6667 on carl's HQs against 724 on ours (`a1_hq.py`).
- Carl banks Ad: 1572 against our 630.
- Our home wells stay clean: carl has 154 launcher-turns there, and our trips end in deposits 179 of 188 times.

Two things favour carl in this symmetric race:
1. Its waves meet ours bigger and earlier, in the middle or in our half.
2. Its carriers survive carl-side exposure better than ours. Dead carriers per exposed turn:
   - carl in collapses: 6 per 778;
   - us in collapses: 82 per 1821;
   - carl in early wins: 43 per 894.

   I did not establish why. Unverified candidates: carl's carriers flee earlier, or our launchers' target priority sends them after launchers first (Launcher.java:155–163).

## 10. Code ties (src/c_kx0)

| # | mechanism | code | evidence |
|---|---|---|---|
| 1 | Carriers return to a camped home well | Carrier.java:215: the hot mark needs `front(well)`. Carrier.java:501–503: `frontGate` (homeD2 > `HOT_HOME_D2`=64, C.java:345, and ≥ `HOT_FRONT_PCT`=36% of enemyD2, C.java:346). Carrier.java:340: drop only if hot. `survive()` at Carrier.java:192–243 flees home and forgets nothing. | 9 collapse home wells: 72 trips, 17 deposits, 34 deaths. 3.9 exposures per dead carrier. |
| 2 | No carrier replacement while threatened; Ad idles | HQ.java:93 (`!threatened`); HQ.java:153–161 `inDanger` (`HQ_DANGER_R2`=20, C.java:96) | t on 507 HQ-turns. Ad bank 1056/520 at r200. |
| 3 | Reinforcements leave alone, straight into the camp | HQ.java:59 and :92 (threatened ⇒ `batchOK`; a launcher whenever Mn ≥ 45). C.java:99 `LAUNCHER_BATCH=1`. C.java:112 `ARMY=false`, so Launcher.java:425 skips `regroup()`. HQ.java:195–217 spawns on the tile nearest the enemy HQ. | Later launchers: alone 53%, outnumbered 27%, dead within 20 rounds 71%, first contact 3.8 tiles from HQ. |
| 4 | The army does not come home | Launcher.java:1009 `siegeTarget` (the enemy HQ nearest our centroid, Launcher.java:448–471). Recall at Launcher.java:953 and guard at Launcher.java:966 both need the home threat nearer than the siege target, and recall needs it within `RECALL_R2`=225 (C.java:70). | Frog, from the army centroid (17,8): siege target (10,9) d² 50, carl group (22,23) d² 250, our upper HQ (36,23) d² 586. So neither rule fires. |
| 5 | Mana carriers locked on an Ad well | Carrier.java:356–360 (all known Mn wells hot ⇒ `searchTurns=60`), :373 `nearestCool(home, 0)`, :340 (a home Ad well is never dropped) | Frog: 4 carriers, 380 kg of Ad, 0–2 kg of Mn each. |
| 6 | Stuck carriers | navigation (not located) | Jail: max_still 162 and 172 in state G. |
| 7 | Not a cause: per-shot micro | Launcher.java:252, :339 | 51.0 vs 48.0 hits per 100 contact turns. |

## 11. Unverified or inferred

- **Frog guard and recall.** That neither fired comes from the inequality at Launcher.java:953/966 applied to launcher centroids from the replay. The sighting slots are in the shared array, which the replay does not record (RULES.md:423). There is no debug log (`--logs` returns nothing on the replica).
- **Frog Ad lock.** Why `nearestCool(home, Mn)` returned null (which wells were hot, or whether (26,24) was in the shared list) is inferred, not observed. The branch itself is fixed by the timing: carrier 10332 had 0 explore turns.
- **Jail.** The navigation cause of the two stuck carriers was not located. I did not inspect Nav or the map walls.
- **Split waves.** That they come from the per-HQ spawn tile plus `ARMY=false` is inferred. The observed facts are the group sizes at contact (LightWork 2.17/6.51, Barcode 1.98/3.35).
- **Why carl's carriers survive exposure better** is not established (§9).
- **Fixes.** None was tested; no games were run. The levers the code ties point at:
  1. let a home well turn hot, or mark it after a death there;
  2. hold new launchers at the HQ until a pair or more is formed when the HQ is threatened or outnumbered;
  3. let the guard/recall rule override the siege when our carriers are dying at home;
  4. let a mana-role carrier re-check for a mana well while it holds an Ad well.

## 12. Scripts, data and commands

Scripts are in `research/diagnosis/2026-10-19-top2/scripts/`. Run each with `python3 -I`, from the repo root. The scripts are:

| script | arguments |
|---|---|
| `a1_common.py` | (shared loaders) |
| `a1_table.py` | |
| `a1_snow.py` | |
| `a1_alive.py` | 250 |
| `a1_first.py` | |
| `a1_eng.py` | 250 [-v] |
| `a1_feed.py` | SA 200 |
| `a1_lage.py` | |
| `a1_cdeath.py` | |
| `a1_ckill.py` | 150 |
| `a1_cexp.py` | SA TT 150 |
| `a1_front.py` | 150 |
| `a1_wells.py` | 150 |
| `a1_home.py` | SA 150 34 |
| `a1_pos.py` | SA 150 |
| `a1_traj.py` | SA m g 160 10 |
| `a1_micro.py` | SA 150 |
| `a1_hq.py` | 200 |
| `a1_role.py` | TT SA 150 m:g,... |
| `a1_frogad.py` | TT SA 150 |
| `a1_stuck.py` | 200 50 |
| `a1_split.sh` | SA_RAW SA 300 |

- **SA** is `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/top2/a1/sa300`. It holds the per-turn `--sa` rows split per game, rounds < 300.
- **TT** is `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/top2/a1/tt`. It holds `--extract --tele-turns`.
- **Outputs** are saved in `.../scratchpad/top2/a1/out/*.txt`.

The dumps ran one at a time under the shared lock. For each match m and team t:
```
flock .../scratchpad/dump.lock env DUMP_XMX=500m tools/replay-dump.sh build/top2/replays/$m.bc23 --sa --team $t --games all --match $m --out .../top2/a1/sa/$m$t
flock .../scratchpad/dump.lock env DUMP_XMX=500m tools/replay-dump.sh build/top2/replays/$m.bc23 --extract .../top2/a1/tt/$m --match $m --games all --tele-turns
research/diagnosis/2026-10-19-top2/scripts/a1_split.sh .../top2/a1/sa .../top2/a1/sa300 300
```
