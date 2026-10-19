# Analyst 3: opening economy against carlguo866.submit26_final and maxwelljones14.MPWorking

Written 2026-10-19, 13:07-13:45 PDT. Scope: 48 replica games (carl matches 9888 9900 9912 9914 9915 9921 9925 9929 9931 10060,
maxwell matches 9911 9913 9918 9924 9928 9930). 9921 g0 repeats 9888 g0 (Frog, same seed and result), so every pooled number uses
47 distinct games: **30 losses (L) and 17 wins (W)**. Wins are the control. Our bot in these games is c_kx0 (= c_eco3).

Sources: the `matches/<id>/` extracts (games, census, timeline, robots, trips, deaths, hq), the per-turn sa dumps and
`tele_turns.csv` under the session scratchpad `top2/` (a0, a1, a2), and the engine map files. Every script is in
`scripts/` with the prefix `a3_`. Run each one with `python3 -I`. Outputs are under the scratchpad `top2/a3/`.

## Verdict

1. **Production is not the problem.** In the first 50 rounds both sides build the same thing. Both sides turn the
   mana they get into launchers equally well: 0.939 vs 0.946 of available Mn through r150. Our HQs have 45 Mn
   unspent on 3 of 7950 HQ turns. By r100 the launcher-built gap in losses is 1 per game (453 vs 483).
2. **Our opening trips are faster.** We are ahead in mana at r30 even in losses: +380 pooled, i.e. +13 per game.
   - First collect: r5 vs r12.
   - First Mn deposit: r43.5 vs r57.
3. **The losses diverge at r31-50.** Enemy launchers reach our home Mn wells and our carriers die or flee:
   - carriers lost r31-50: 19 vs 5; by r100: 105 vs 17, 103 of ours to launchers;
   - our Mn per carrier-round falls from 0.60 to 0.32 while theirs stays at 0.64-0.70.

   About half of the r100 Mn gap is fewer carriers alive (count term -1507 of -3056). The other half is less Mn
   per live carrier (-1549).
4. **Early Ad collection is not a lever.**
   - Our extra Ad by r100 is 650 kg in losses. Mined as Mn instead, that is at most 14-27 launchers over 30 losses,
     i.e. 0.5-0.9 per loss.
   - It was spent on carriers that replaced losses.
   - Per-game Ad is the same in wins and losses: 78 vs 68.5 kg by r100.
   - r(our Ad@100, result) = 0.05.
   - **Estimated flips: 0.** The Ad that Mn-role carriers mine (636 kg in losses) is the hot-well fallback, a symptom
     of enemy launchers on our Mn wells.
5. **Well choice costs games only through the centre-first explore rule** (Carrier.java 704-712), and only where the
   home Mn wells are outside HQ vision and away from the centre:
   - SoundWave: Mn at r100 0 vs 449; first Mn deposit r189.
   - Contraction: centre well at walk 25 instead of a home well at walk 10.

   **Estimated flips: 1 (range 0-2).** Other far-well cases were already ahead in Mn at r100.
6. **Map vs decision.** Maps are symmetric, so walks are identical for both sides. Walk to Mn vs result: r = -0.10.
   Within the same walk stratum (4-6), losses lost 70 carriers vs 5 for the opponent. Enemy launchers reach our main
   Mn well at median r54 in losses vs r71 in wins, with the same enemy walk to it (19.5 vs 20). The economic gap is
   decided by how the early launcher fight goes near our home wells. That is the combat and positioning question for
   the other analysts, not an economy constant.

## 1. HQ builds in rounds 1-50 (`a3_builds.py`)

Per HQ, from robots.csv birth rounds. Banks come from sa_HQ: the bank is read at the start of the HQ's turn, and
round 1 shows 200/200 together with the round-1 builds.

| side | r1 (per HQ) | r2-10 | r11-25 | r26-50 | launchers / carriers by r25 (median) | by r50 | HQ-rounds r3-50 ending with Mn >= 45 (per HQ, median) | mean bank Mn / Ad r3-50 |
|---|---|---|---|---|---|---|---|---|
| L us | LLLL C | r2: CCC | - | r26: L, r46: CC | 8 / 8 | 10.5 / 10 | 1.5 | 26 / 24 |
| L them | LLLL C (carl); maxwell C first | r2: CCC (carl); maxwell r2-3 LLLL + C | carl one L r24 in Frog | r26: L, r46: CC | 8 / 8 | 10 / 10 | 1.0 | 26 / 27 |
| W us | LLLL C | r2: CCC | - | r26: L(L), r46: CC | 8 / 8 | 15 / 10 | 2.5 | 26 / 25 |
| W them | as above | | | | 8 / 8 | 11 / 10 | 1.0 | 26 / 32 |

Raw rows:
- Ours, every game: r1 `LLLLCLLLLC` for 2 HQs, r2 `CCCCCC`.
- carl in 9888 g0: identical to ours.
- maxwell in 9913 g0: r1 `CCC`, r2 `LLLCLLLLC`, r3 `LCCC`.
- maxwell in 9928 g2: r1 `CCC`, r2 `LLLLCLLLLC`, r3 `CCC`.

Both bots spend the 200/200 start the same way. After that, each builds one launcher per 45 Mn as soon as it has it.
Our medians at r50 are 10.5 launchers in losses vs 15 in wins. The difference comes from more HQs per map (3-4-HQ
maps are 5-3 for us, section 7) and from more early Mn (launchers per HQ in r2-50: 1.87 in losses vs 2.49 in wins),
not from a different build policy. HQ code `p` (too poor to build) is set on 7410 of 7950
of our HQ turns r1-150 in losses (`a3_convert.py 150`), so the HQs are income-bound.

## 2. First trips and trip times (`a3_trips.py`)

The opening carriers are those born in r1-2. "Extra moves" = moves to the first well, minus the BFS walk to the
nearest well of that type from the carrier's HQ. Trip cycles cover deposit trips started by r100.

| group | opening carriers' first well Mn / Ad / none | extra moves per carrier | first collect (median round) | first trip died | first Mn deposit (median round) | Mn deposited r50 / r75 / r100 / r150 (median per game) | cycle / out / fill / back (median rounds) | load |
|---|---|---|---|---|---|---|---|---|
| L us | 0.74 / 0.14 / 0.12 | 1.85 | 5 | 0.20 | 43.5 | 60 / 90 / 120 / 165 | 44 / 4 / 29 / 9 | 30 |
| L them | 0.88 / 0.09 / 0.03 | 1.08 | 12 | 0.10 | 57 | 0 / 120 / 200 / 399 | 57 / 6 / 39 / 9 | 40 |
| W us | 0.89 / 0.10 / 0.01 | 0.79 | 4 | 0.08 | 38 | 90 / 180 / 330 / 720 | 44 / 4 / 29 / 9 | 30 |
| W them | 0.78 / 0.16 / 0.06 | 2.27 | 10.25 | 0.12 | 45.5 | 13 / 100 / 168 / 298 | 55 / 5 / 39 / 10 | 40 |

- **The trip itself is not the problem.** Collection per round over a trip is the same for both sides:
  - us: a 30 kg load in a 44-round cycle, 0.68 kg per round;
  - them: a 40 kg load in a 57-round cycle, 0.70 kg per round.

  `C.CARRIER_RETURN_LOAD = 30` (C.java:126) delivers sooner at the same rate. Flips from changing it: 0.
- **Extra moves are concentrated in a few losses** (extra moves summed over the opening carriers):
  - Contraction 99;
  - Spots 73;
  - MassiveL 50;
  - PipesAndParabolas 44;
  - TimesUp 44;
  - Pit 24;
  - Frog 22.

  Of these, Spots (+72), Pipes (+118) and TimesUp (+26) were still ahead in Mn at r100 (`a3_flip.py`). Section 8
  covers Contraction.
- **12% of our opening carriers in losses never reached a well, vs 3% of theirs.** SoundWave alone has 7 of 8
  (section 8).

## 3. The Mn gap: when it opens (`a3_rate.py`) and what it is made of (`a3_decomp.py`)

Losses (n = 30), 10-round windows, pooled. "C alive" is the mean number of carriers alive. "Mn per C-round" is Mn
collected per carrier-round.

| window | us dMn | us C alive | us Mn per C-round | us C lost | them dMn | them C alive | them Mn per C-round | them C lost | cumulative Mn gap |
|---|---|---|---|---|---|---|---|---|---|
| r1-10 | 562 | 3.5 | 0.535 | 2 | 244 | 3.5 | 0.235 | 1 | +318 |
| r11-20 | 1077 | 6.9 | 0.523 | 8 | 908 | 6.9 | 0.439 | 2 | +487 |
| r21-30 | 1189 | 6.6 | 0.597 | 6 | 1296 | 6.9 | 0.625 | 0 | +380 |
| r31-40 | 930 | 6.5 | 0.481 | 12 | 1451 | 6.9 | 0.698 | 2 | -141 |
| r41-50 | 669 | 7.0 | 0.318 | 7 | 1477 | 7.7 | 0.642 | 3 | -949 |
| r51-60 | 867 | 7.5 | 0.386 | 13 | 1350 | 8.6 | 0.524 | 1 | -1432 |
| r61-100 | 3472 | 7.2-7.7 | 0.37-0.41 | 57 | 5096 | 8.6-10.1 | 0.44-0.47 | 8 | -3056 |
| r101-150 | 5006 | 7.7-8.6 | 0.37-0.47 | 64 | 7803 | 10.2-11.9 | 0.46-0.49 | 30 | -5853 |

In wins we lead in every window: +348 at r10, +1098 at r30, +2773 at r100. Both sides dip at r41-50 (us 0.403, them
0.479), which is the return-trip phase of the opening trips.

Decomposition of the collected-Mn gap. The count term is (carrier-rounds us - them) times their Mn per carrier-round.
The rate term is our carrier-rounds times (our Mn per carrier-round - theirs).

| group, rounds | Mn gap | count term (fewer carriers) | rate term (less Mn per carrier) | carrier-rounds us / them | Mn per C-round us / them | Ad per C-round us / them | our Ad beyond their Ad rate |
|---|---|---|---|---|---|---|---|
| L, r1-50 | -949 | -239 | -710 | 9140 / 9565 | 0.484 / 0.562 | 0.078 / 0.054 | 217 kg (31% of the rate term) |
| L, r1-100 | -3056 | -1507 | -1549 | 20220 / 23175 | 0.434 / 0.510 | 0.102 / 0.070 | 650 kg (42%) |
| L, r1-150 | -5853 | -3615 | -2238 | 32375 / 39685 | 0.425 / 0.495 | 0.110 / 0.083 | 875 kg (39%) |
| W, r1-100 | +2773 | +402 | +2371 | 17380 / 16380 | 0.538 / 0.402 | 0.077 / 0.110 | -580 kg |

Reading the decomposition:
- The count term is carrier deaths, not production. We built 335 carriers by r100 vs 324, and lost 105 vs 17
  (section 6).
- In losses, the rate term is partly Ad: the extra Ad is 42% of it at r100. The rest is walking, fleeing and waiting.
- The rate term alone is less than 1 launcher per loss by r100: 1549 / 45 / 30 = 1.1 launchers, of which Ad is 0.48.
- **Collected Mn is not deposited Mn.** HQ-received Mn by r100 is 22549 vs 23705 (gap 1156, `a3_convert.py 100`),
  while the collected gap is 3056. The opponent's 40 kg loads are still in transit at r100, and our dead carriers took
  574 kg of Mn cargo with them (`a3_closs.py`). Only the 574 kg is measured; the in-transit share of the remaining
  ~1900 kg is inferred.

## 4. Mn vs Ad role split (`a3_roles.py 100`)

The sa_C collect actions are joined to our telemetry role bit (carrier code & 1 = Mn role), rounds 1-100.

| group | carriers born with the Ad role | carrier-turns Ad role / Mn role (Ad share) | our Ad: by Ad role / by Mn role / no code | our Ad share of collection | their Ad share | our Ad per game |
|---|---|---|---|---|---|---|
| L (30) | 27 / 335 (0.081) | 2120 / 18300 (0.104) | 2056: 1376 / 636 / 44 | 0.190 | 0.120 (1611 Ad, 11822 Mn) | 68.5 |
| W (17) | 21 / 247 (0.085) | 1300 / 16139 (0.075) | 1332: 913 / 393 / 26 | 0.125 | 0.215 (1802 Ad, 6583 Mn) | 78.4 |

- The Ad-role rule `swarmRole()` (Carrier.java:172-177) assigns the same share in wins and losses: 8.1% vs 8.5% of
  carriers. The rule is `G.id % AD_EARLY_EVERY == 0 && adFlag(nearest HQ)`, with the flag set by HQ.java:116,
  `Ad < AD_NEED && liveCarriers < carrierCap`. Constants: `AD_NEED = 100, AD_EARLY_EVERY = 8, AD_ROLE_FROM = 200,
  AD_LATE_EVERY = 4` (C.java:28).
- The higher Ad share in losses comes from **Mn-role carriers mining Ad** (636 kg).

  Losses:

  | map | Ad mined by Mn-role carriers by r100 | other figures by r100 |
  |---|---|---|
  | Frog | 281 kg | 145 Mn |
  | RockWall | 225 kg | 19 Mn, first Mn deposit r252 |
  | Contraction | 88 kg | |
  | RaceToTheTop | 42 kg | |

  In a win, Movepls has 393 kg. The path is the hot-well fallback:
  - `gather()` (Carrier.java:358-360) sets `searchTurns = C.WELL_SEARCH_TURNS` when every known Mn well is hot;
  - in the same call, `++searchTurns > WELL_SEARCH_TURNS` then holds and the carrier takes `nearestCool(home, 0)`
    (Carrier.java:371-374), which is any type, so an Ad well.

  RockWall trace (sa_C, from earlier in this session):
  - Mn collected at (8,6) in r5-7;
  - the carriers fled at r11-13;
  - Ad collected at (6,0) and (7,1) through r70.

  These carriers mine Ad because enemy launchers hold the Mn wells.
- **Upper bound on the launchers lost to Ad.** Our Ad above the opponent's Ad rate is 650 kg by r100 (`a3_decomp.py`).
  Summing only the positive per-game excess gives 1233 kg (`a3_flip.py`). That is 14.4-27.4 launchers over 30 losses,
  i.e. 0.5-0.9 per loss by r100. This ignores two things:
  - the Ad paid for 11 more carriers than the opponent built by r100 (335 vs 324; Ad received 18241 vs 17879);
  - the Mn-role Ad came from carriers that had no cool Mn well to mine.
- Correlations over 47 games (`a3_mapfx.py`):
  - our Ad@100 vs result: 0.05;
  - Ad gap r100 vs result: -0.16;
  - our Ad@100 vs Mn gap r100: -0.20.

## 5. Mana into launchers and HQ idle funds (`a3_convert.py 150`, `a3_convert.py 100`)

For each HQ turn: left = bank - spent (45 per launcher, 15 Mn per amplifier; 50 per carrier, 30 Ad per amplifier, 80
per anchor), received = next bank - left. "Mn available" = the 200 per-HQ stock plus everything received. Conversion =
45 x launchers built / Mn available. Round 1 is included because maxwell builds its first launchers in r2-3.

| group, r1-150 | Mn available | launchers built | conversion | mean left Mn per HQ turn | HQ turns with left Mn >= 45 | left Ad >= 50 | hq.csv idle_funds | carriers built | Ad received | our codes p / t |
|---|---|---|---|---|---|---|---|---|---|---|
| L us | 29367 | 613 | 0.939 | 23.6 | 3 / 7950 | 3.6% | 763 | 422 | 22853 | 7410 / 301 |
| L them | 33360 | 701 | 0.946 | 24.7 | 134 / 7950 | 6.4% | 1005 | 408 | 22405 | |
| W us | 25972 | 547 | 0.948 | 23.3 | 1 / 5850 | 3.4% | 599 | 306 | 16658 | 5509 / 68 |
| W them | 21631 | 448 | 0.932 | 26.7 | 286 / 5850 | 11.5% | 1063 | 300 | 17109 | |

At r100 in losses: Mn available 22549 vs 23705, launchers built 453 vs 483, conversion 0.904 vs 0.917.

What the table shows:
- Our HQs hold less unspent money than the opponent's in both wins and losses.
- The launcher deficit in losses is exactly the Mn-income deficit: 88 launchers = 3993 Mn / 45.
- `LAUNCHER_BATCH = 1` (C.java:99) and `batchOK` (HQ.java:59) do not delay launchers: a launcher was affordable but
  not built on 3 of 7950 turns.
- Under threat, the HQ withholds carriers (HQ.java:93, `!threatened`; code `t`) on 301 turns in losses vs 68 in wins.
  That is a combat-state effect, not a funds effect.

## 6. Carriers lost before r100 (`a3_closs.py 100`)

| group | carriers lost | within d2 64 of own HQ | own-side progress < 0.3 / 0.3-0.5 / >= 0.5 | working a home / front well | Mn / Ad well | no well yet | died within r2 20 of its well | Mn cargo lost | first death (median round) | causes | our last telemetry state |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L us | 105 | 76 | 59 / 31 / 15 | 48 / 20 | 66 / 2 | 37 | 43 | 574 | 43.5 | launcher 103, HQ aura 2 | F 47, G 22, V 9, X 8, W 8, C 8 |
| L them | 17 | 10 | 8 / 6 / 3 | 8 / 6 | 8 / 6 | 3 | 10 | 2 | 58 | launcher 16, self 1 | |
| W us | 18 | 11 | 5 / 7 / 6 | 11 / 4 | 13 / 2 | 3 | 6 | 78 | 62 | launcher 13, HQ aura 5 | G 5, F 5, C 4 |
| W them | 31 | 27 | 23 / 6 / 2 | 17 / 7 | 19 / 5 | 7 | 15 | 64 | 63 | launcher 31 | |

In losses, our carriers die on our own half (59 of 105 at progress < 0.3), at Mn wells, and while fleeing (F 47).
37 of them had not yet reached a well. The mirror holds in wins: the opponent loses 31 carriers on its own half. The
carrier war is decided by whose launchers reach the other side's home Mn wells first (section 7). The losses start
early: 8 vs 2 in r11-20 and 16 vs 3 by r30 (`a3_rate.py`).

## 7. Map effects vs decision effects (`a3_mapfx.py`, `a3_arrive.py`, `a3_hqfirst.py`)

All maps are symmetric, so the BFS walk from each HQ to its nearest Mn well is the same for both sides (`a3_overview.py`
mapfeat, per HQ). A map can only matter through how play unfolds on it.

| stratum | n | W-L | median Mn gap r30 | median Mn gap r100 | carriers lost r100 us / them |
|---|---|---|---|---|---|
| walk to Mn <= 3 | 11 | 5-6 | 3 | -8 | 11 / 15 |
| walk 4-6 | 18 | 5-13 | 16 | -56 | 72 / 14 |
| walk 7-9 | 12 | 6-6 | 38 | -52 | 32 / 16 |
| walk >= 10 | 6 | 1-5 | 64 | -16 | 8 / 3 |
| area <= 900 | 20 | 5-15 | 14 | -76 | 76 / 27 |
| area > 1800 | 12 | 6-6 | 74 | 116 | 17 / 8 |
| 1 HQ | 13 | 3-10 | 16 | -93 | 25 / 8 |
| 3-4 HQs | 8 | 5-3 | 112 | 267 | 27 / 9 |
| vs carl | 29 | 11-18 | 35 | -8 | 87 / 26 |
| vs maxwell | 18 | 6-12 | 10 | -56 | 36 / 22 |

Within a stratum, wins and losses have the same walk but different carrier losses:

| walk | W: median Mn gap r100 | W: C lost us / them | L: median Mn gap r100 | L: C lost us / them |
|---|---|---|---|---|
| 4-6 | +141 | 2 / 9 | -105 | 70 / 5 |
| 7-9 | +211 | 9 / 12 | -157 | 23 / 4 |

Same map, different result: on PairedProgramming we won against carl (Mn100 527/173, carriers lost 0/5) and lost
against maxwell (Mn100 294/504, carriers lost 5/0).

Pearson r over 47 games, with the result (1 = win):

| variable | r with the result |
|---|---|
| Mn gap r100 | 0.65 |
| carrier-loss difference r100 | 0.50 |
| Mn gap r30 | 0.45 |
| area | 0.19 |
| our Ad@100 | 0.05 |
| walk to Mn | -0.10 |
| Ad gap r100 | -0.16 |

Mn gap r100 vs carrier-loss difference: 0.49. Vs walk: -0.03.

**Enemy launchers on our main Mn well** (`a3_arrive.py`). The main well is the Mn well with the most collects among
trips started by r60. Arrival = the first enemy launcher within r2 20 of it.

| | L (30) | W (17) |
|---|---|---|
| enemy reaches our well, median round | r54 (never in 8) | r71 (never in 9) |
| we reach theirs, median round | r58 (never in 22) | r78 (never in 8) |
| enemy arrives first | 18 / 30 | 4 / 17 |
| enemy walk to our well / ours to theirs (median) | 19.5 / 22.5 | 20 / 23.5 |

| enemy arrival on our main Mn well | n | W-L | our carriers lost r100 | median Mn gap r100 |
|---|---|---|---|---|
| r0-40 | 10 | 2-8 | 54 | -215 |
| r41-80 | 10 | 3-7 | 29 | -65 |
| r81-300 | 10 | 3-7 | 13 | +16 |
| never | 17 | 9-8 | 27 | |

**Per HQ: is the nearest Mn well inside HQ vision (r2 <= 34)?**

| nearest Mn well | group | HQs | first carrier Mn at the HQ (median round) | HQs with no carrier Mn by r100 | carrier Mn per HQ r50 / r100 / r150 |
|---|---|---|---|---|---|
| in vision | L us | 10 | 33 | 2 | 78 / 219 / 357 |
| in vision | L them | 10 | 44 | 0 | 85 / 252 / 437 |
| out of vision | L us | 43 | 52 | 15 | 25 / 79 / 132 |
| out of vision | L them | 43 | 64 | 7 | 4 / 98 / 206 |
| out of vision | W us | 31 | 46 | 8 | 40 / 122 / 207 |
| out of vision | W them | 31 | 70 | 9 | 6 / 67 / 133 |

"No carrier Mn" can also mean the carriers delivered to another of our HQs. 15 of 43 is therefore an upper bound on
starved HQs; it is unverified per HQ.

Conclusion:
- Geometry sets the stage. Small maps (5-15) and one-HQ maps (3-10) are bad for us.
- On the same geometry, the decision is the early launcher contest at the home Mn wells:
  - when enemy launchers arrive by r40 we are 2-8;
  - our carriers are fast to the wells, but once launchers arrive they die or flee there.

## 8. Well-choice decision cases

**SoundWave, 9928 g2, a loss** (`a3_trips.py`, `a3_roles.py`, plus the sa_C positions and telemetry printed in this
session):
- Our HQs are at (7,25) and (24,18). Their nearest Mn wells, (16,29) and (32,23), are at walk 8 and 7, d2 97 and 89:
  outside HQ vision 34 and outside carrier vision 20 at spawn.
- With no Mn well known, the carriers follow the centre-first explore (Carrier.java:704-712) toward (20,15):
  - carrier 10091 went (10,28) -> (18,20) -> (27,18);
  - carrier 10975 went (21,19) -> (6,25) -> (2,15) -> (6,4), next to the enemy HQ at (7,4).
- The telemetry runs X (explore) for 10-50 rounds, then F (flee).
- Outcome:
  - opening carriers' first well: 0 Mn, 1 Ad, 7 none;
  - first Mn deposit r189 vs the opponent's r64;
  - Mn by r100: 0 vs 449; launchers built by r100: 12 vs 18; carriers lost r100: 8 vs 1;
  - conquest at r596.

**Contraction, 9913 g0, a loss.**
- HQ (8,3) has a Mn well at (19,7): walk 10, d2 137, outside vision. The opening carriers took the centre wells
  (27,29)/(27,30) at walk 25: extra moves 99, first Mn deposit r85 vs r72.
- Enemy launchers reached (27,29) at r40. Mn gap r100: -243. Launchers alive r100: 11 vs 19. Conquest at r484.

**Shared-list far wells** (MassiveL, PipesAndParabolas, TimesUp, Spots: +44 to +73 extra moves). The opening carriers
took another HQ's well from the Comms list. Mn gap at r100: -128, +118, +26, +72. Three of the four were ahead in Mn
at r100 anyway, and all four games ran 833-2000 rounds.

## 9. Constants, code lines, and estimated flips

| change | code | games touched | evidence | estimated flips (of 30 losses) |
|---|---|---|---|---|
| Less early Ad: raise AD_EARLY_EVERY, lower AD_NEED | C.java:28; Carrier.java:172-177; HQ.java:115-116 | all | Ad-role carriers 8.1% L vs 8.5% W; Ad per game 68.5 L vs 78 W; r(Ad@100, result) = 0.05; at most 0.5-0.9 launchers per loss by r100, and that Ad paid for carriers | **0** |
| Mn-role hot fallback to any well, which becomes an Ad well | Carrier.java:358-360 and 371-374 (`nearestCool(home, 0)`); HOT_HOME_D2 = 64, HOT_FRONT_PCT = 36 (C.java:345-346); WELL_SEARCH_TURNS = 60 (C.java:138) | Frog, RockWall, Contraction, RaceToTheTop (636 kg); a win: Movepls (393 kg) | these carriers have no cool Mn well (enemy launchers there); the alternative is idling or dying | **0** |
| Centre-first explore for Mn carriers with no known Mn well | Carrier.java:704-712 (`centreTried`); WELL_SEARCH_TURNS (C.java:138) | SoundWave, Contraction | home Mn wells at walk 7-10 skipped; Mn r100 0 vs 449 and 179 vs 422 | **1 (0-2)**: SoundWave is the only loss where the economy hole at r100 (10 launchers) is clearly opening-made; its HQs are 7 tiles apart, so combat may decide it anyway |
| Shared-list far wells | Carrier.java:362-368 (`Comms.nearestWell(G.here, role)`) | MassiveL, Pipes, TimesUp, Spots | 3 of 4 ahead in Mn at r100 | 0 |
| Load size | CARRIER_RETURN_LOAD = 30 (C.java:126) | all | 0.68 vs 0.70 kg per round | 0 |
| Build order and batching | LAUNCHER_BATCH = 1 (C.java:99); HQ.java:59, 92-93 | all | builds identical r1-50; 3 idle-Mn turns in 7950 | 0 |

Per loss (`a3_flip.py`), the launchers built by r100 differ by a median of 1 (sum 453 vs 483):
- 12 of 30 losses had built as many launchers as the opponent by r100, or more, and lost anyway.
- 4 more losses have a gap the Ad bound could close, but the launchers-alive gap there is combat:

  | map | launchers built r100 us / them | Ad bound (launchers) | alive at r100 us / them |
  |---|---|---|---|
  | Frog | 14 / 18 | 4.2 | 8 / 12 |
  | PairedProgramming | 20 / 22 | 3.3 | 10 / 10 |
  | RaceToTheTop | 9 / 10 | 1.8 | 7 / 6 |
  | USA | 11 / 12 | 1.3 | 6 / 9 |

  Launchers lost by r100: 213 vs 192 in total.

The economy lever that matters is the **count term**: carrier-rounds 20220 vs 23175 by r100, from 105 vs 17 carriers
lost. That is carrier survival at the home Mn wells once enemy launchers arrive. No economy constant fixes it:
- carriers flee (F 47 of 105 deaths) and still die;
- HQ_DANGER_R2 = 20 and HQ_THREAT = 1 (C.java:95-96) only withhold new carriers.

## 10. Caveats and unverified points

- How the ~1900 kg difference between the collected and deposited Mn gaps at r100 splits between in-transit cargo and
  anything else is inferred; only the 574 kg of cargo lost is measured.
- "HQs with no carrier Mn by r100" counts deposits per HQ. Carriers that deliver to a sibling HQ make this an
  overcount of starved HQs.
- The flip estimates are judgement on the measured gaps. They are not verified by games; this task forbids running
  them.
- The trace that the SoundWave carriers followed the centre-first branch is inferred from positions and the X state.
  It is consistent with Carrier.java:708-711, but the branch itself was not instrumented.
- Carrier-rounds use 10-round samples of timeline alive_C (trapezoid rule). They are approximate to a few percent.
- The opponents' source was not read. Every statement about them comes from replay dumps.

## Reproduce

```
cd research/diagnosis/2026-10-19-top2/scripts
python3 -I a3_overview.py           # per-game map features and economy, pooled medians
python3 -I a3_builds.py             # section 1
python3 -I a3_trips.py [-v]         # section 2
python3 -I a3_rate.py               # section 3 windows
python3 -I a3_decomp.py 50|100|150  # section 3 decomposition
python3 -I a3_roles.py 100          # section 4 (about 2 min)
python3 -I a3_convert.py 150|100    # section 5
python3 -I a3_closs.py 100 [-v]     # section 6
python3 -I a3_mapfx.py              # section 7 strata, pairs, correlations
python3 -I a3_arrive.py             # section 7 enemy arrival
python3 -I a3_hqfirst.py [-v]       # section 7 per HQ
python3 -I a3_flip.py               # section 9 per-loss table (a few minutes)
```

The inputs are the scratchpad dumps `top2/a0/{sa,ext}` (maxwell), `top2/a1/{sa300,tt}` (carl) and `top2/a2/sa` (10060),
made with `tools/replay-dump.sh` under the dump lock, plus `matches/<id>/*.csv`. The paths are in `scripts/a3_common.py`.
