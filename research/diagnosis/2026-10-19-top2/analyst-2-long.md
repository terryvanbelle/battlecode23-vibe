# Long and late games against carl and maxwell (Analyst 2)

2026-10-19, 13:40 PDT. Our build was c_eco3 (submission 192). It is `src/c_kx0` with its switch constants at their
defaults, so every code location below is in `src/c_kx0`. Sources:
- extracts `matches/<match>/extract/*.csv` (census, timeline, engagements, deaths, hq, robots, tele_states);
- per-turn `--sa` dumps of both teams, which live outside the repo (paths in the last section);
- our own telemetry (tele_states), which covers our side only.

I read no other team's source code and no 2023 post-mortem. I ran no games, did not edit `src/` and did not commit.
Every number comes from a script in `research/diagnosis/2026-10-19-top2/scripts/a2_*.py`, run with `python3 -I`. The
script is named in brackets. Claims I could not check are marked **unverified**.

Scope: 19 games.
- 10 losses to carlguo866.submit26_final ("Lc"): PipesAndParabolas 9912 g1, RockWall 9912 g2, MassiveL 9914 g0, USA
  9914 g2, KingdomRush 9915 g0, RaceToTheTop 9929 g1, Pillars 9931 g1, IslandHopping 10060 g0, Maze 10060 g1, Rainbow
  9888 g1.
- 5 losses to maxwelljones14.MPWorking ("Lm"): TimesUp 9911 g2, Marsh 9924 g2, BuildSite 9928 g0, Spots 9930 g2,
  BatSignal 9924 g0.
- 4 long wins ("W"): Repetition 9921 g1 and 9925 g1, Forest 9929 g0, SweetDreams 10060 g2.

Windows are r0-299, r300-599, r600-999 and r1000+. Telemetry phases are open ≤ r150, mid r151-600 and late > r600.
"Home/mid/far" is the progress e = d_own / (d_own + d_enemy), measured from each team's nearest HQ: home < 0.35, far
> 0.65.

## Summary

1. **The turn is r300-600, after an even opening.**
   - r0-299, losses: we have as many launchers as they do (12.0 vs 11.6 alive per round) and as much Mn (441 vs 528
     per 100 r, median).
   - r300-599: their army is 2.4 times ours (30.4 vs 12.7). Their Mn income is 2.3 times ours (808 vs 353), they
     build 17.7 launchers per 100 r to our 9.3, and they keep 26.0 carriers alive to our 14.7.
   - The split round (from it on, they lead by 5+ launchers to the end) has a median of r440. It falls in r340-810
     in 10 of 15 losses and at r120-260 in the other 5. [a2_bins, a2_econ, a2_overview]
2. **The losses fall into three types** (game table below):
   - (A) early collapse, split ≤ r260, 5 games: the long tail is only the opponent's slow conquest;
   - (B) midgame economic break after an even start, 6 games;
   - (C) the island race lost with a comparable army, 4 games: KingdomRush, BuildSite, Spots, TimesUp.
3. **Type B: they kill our carriers at home.**
   - r300-599 carrier deaths are 307 ours to 133 theirs. 258 of our 307 die at home (e < 0.35).
   - 0.33 of their kills are carriers; 0.25 of ours are.
   - Their launchers stand in our HQ vision 4 times as often as ours stand in theirs: 1.83 vs 0.47 enemy launchers per
     HQ-round. 48% of our launcher-turns are at home, and our launchers are still outnumbered in 14% of their contact
     turns (theirs 5%). [a2_carriers, a2_kills, a2_bins]
4. **Type C: they take islands earlier and fight on them.**
   - First island: median r330 for them, r465 for us. We never take one in 7 of 15 losses. They placed 12 anchors
     before r400; we cannot, because `C.ANCHOR_START = 400` (C.java:77).
   - r300-599: 13% of their contact turns stand within heal range of their own island (maxwell 19%) against our 3%.
     They heal 788 HP per 100 r to our 187 (4.2×). [a2_islands, a2_anchors, a2_islfight, a2_bins]
   - BuildSite: we led 58 to 29 launchers at r400. Then 42% of our contact turns were next to their islands, 44% of
     theirs were on their own islands, and we lost 99 launchers to their 51 (exchange 0.53) by r600.
5. **Our anchors do not become islands.**
   - Losses: we place 29 of the 79 anchors we build (0.37). They place 95 of 154 (0.62). 15 of our anchors died with
     their carriers against 2 of theirs.
   - Wins: we place 23 of 136 (0.17). In the late phase our carriers spend 23,319 turns holding an anchor with no target
     (state E) and 11,189 returning one (state Y), against 3,538 heading to an island (K).
   - Predicted islands (state Q) got 0 carrier-turns in all 19 games. Cause: Carrier.java:869-871 skips predicted
     islands on the enemy side, and `scoutMove` (Carrier.java:885-896) searches our half only, although the comment at
     Carrier.java:778 says "search the whole map". Both Repetition wins ended on a tiebreak at 4 of the 6 islands
     needed. [a2_cstate, a2_mapisl]
6. **The anchor gate closes when we fall behind on islands.**
   - The gate is HQ.java:68 (`!Comms.anyPressed() && Comms.islThem <= Comms.islUs` before r1500). In TimesUp we held 2
     islands to their 4-5 from r500 to r1400 and placed no anchor between r600 and r1400.
   - The gate expires at r1500 (`ANCHOR_GATE_UNTIL`, C.java:200). From then on we placed 4 anchors and reached 4 islands
     to their 4, and lost the tiebreak on anchors placed, 6 to 12.
   - Rebuilt with true island counts, the gate was closed in 87% of 25-round buckets from r400 in losses and open in 99%
     in wins. That rebuild is approximate: the bot reads `Comms.islThem`, which is **unverified** against the truth.
     [a2_tl, a2_gate]
7. **Under siege we feed launchers to the camp.**
   - 470 of the 2050 launchers we built in losses spawned with 3+ enemy launchers within r² 34 of the HQ (408 of them
     from r600).
   - Their median life was 5 rounds against 70, they made 0.08 kills each against 0.88, and they cost 21,150 Mn.
   - The opponents built 61 of their 2913 that way.
   - Code: HQ.java:59 (`batchOK = threatened || ...`) and HQ.java:92 build one launcher whenever Mn ≥ 45, threat or not.
     HQ.java:93 builds no carrier while threatened (HQ late letter t, threatened, in 0.62 of HQ-turns in losses).
     [a2_spawn, a2_carriers]

## Game table

L = launchers alive (timeline). First island and anchors are us/them. Split = the first 10-round sample from which they
lead by 5+ launchers to the end. [a2_overview, a2_islands, a2_census]

| Game | Result | Split | L r300 | L r500 | L r750 | First island | Anchors built/placed us · them | Type: mechanism |
|---|---|---|---|---|---|---|---|---|
| PipesAndParabolas 9912 g1 | Lc conquest r1484 | 640 | 23/15 | 25/23 | 4/42 | 560/620 | 6/4 · 9/7 | B: even to r600; Mn 608 vs 1306/100 r before split; 46 of 157 L built besieged |
| RockWall 9912 g2 | Lc tb islands 0/7 | 460 | 3/6 | 1/6 | 0/16 | 620/520 | 2/2 · 8/7 | B: tiny armies; our Ad share 0.84; Mn 421 vs 2853 all game |
| MassiveL 9914 g0 | Lc conquest r1639 | 120 | 12/26 | 3/63 | 0/144 | none/440 | 0/0 · 12/9 | A: 74 of 131 L built besieged |
| USA 9914 g2 | Lc conquest r1484 | 440 | 17/13 | 6/21 | 2/45 | 460/250 | 8/4 · 7/6 | B: led 19/14 at r400; r300-599 L deaths 42/20 (28 at home), exch 0.64 |
| KingdomRush 9915 g0 | Lc conquest r663 | 650 | 36/29 | 37/55 | end 44/64 | 420/200 | 14/2 · 4/3 | C: 4 islands, 3 needed; 14 anchors, 2 placed, 3 lost; 652 carrier-turns in K |
| RaceToTheTop 9929 g1 | Lc conquest r837 | 410 | 7/7 | 0/15 | - | none/300 | 1/0 · 3/3 | B: our L 0.99 at home r0-599; Mn 435 vs 3812 |
| Pillars 9931 g1 | Lc conquest r704 | 340 | 12/18 | 6/43 | - | none/290 | 5/0 · 3/3 | B: 59 carriers die at home r300-599; L 0.98 at home |
| IslandHopping 10060 g0 | Lc conquest r1654 | 810 | 16/7 | 10/7 | 3/8 | 480/910 | 5/4 · 8/6 | B: we held 2 islands (1030 island-rounds to 0 before split), then Mn 47 vs 390/100 r |
| Maze 10060 g1 | Lc conquest r1613 | 230 | 8/39 | 9/124 | 0/217 | none/280 | 0/0 · 15/6 | A: they build 393 L; HQ wanted an anchor 0 of 1323 mid HQ-turns |
| Rainbow 9888 g1 | Lc tb islands 0/8 | 210 | 5/25 | 0/47 | 0/96 | none/630 | 7/0 · 18/9 | A: 79 of 122 L built besieged; 20 islands, so carl could not conquer |
| TimesUp 9911 g2 | Lm tb anchors 6/12 | 480 | 5/9 | 11/18 | 14/35 | 430/310 | 10/6 · 24/12 | C: islands 2 vs 4-5 r500-1400, 0 placements r600-1400; 4/4 at r2000 |
| Marsh 9924 g2 | Lm tb islands 0/7 | 190 | 1/9 | 0/14 | 0/32 | none/340 | 1/0 · 10/7 | A |
| BuildSite 9928 g0 | Lm conquest r999 | 720 | 44/15 | 26/24 | 35/42 | 440/300 | 10/5 · 15/7 | C: led 58/29 at r400, lost 32 L r400-500 attacking into their islands |
| Spots 9930 g2 | Lm conquest r833 | 520 | 29/27 | 31/32 | 15/44 | 470/330 | 10/2 · 15/7 | C: heal 25 vs 1224 HP/100 r in r300-599; 4 anchors lost with carriers |
| BatSignal 9924 g0 | Lm conquest r504 | 260 | 5/18 | 0/46 | - | none/430 | 0/0 · 3/3 | A |
| Repetition 9921 g1 | W tb islands 4/0 | 200 | 61/54 | 76/50 | 146/31 | 450/none | 41/4 · 2/0 | stuck at 4 of 6 islands; late E 7173, Y 5675, K 0 |
| Repetition 9925 g1 | W tb islands 4/0 | 100 | 66/57 | 67/42 | 123/18 | 480/480 | 43/5 · 2/1 | stuck at 4 of 6; 12 anchors lost; late E 5755, Y 3554, K 101 |
| Forest 9929 g0 | W conquest r1671 | 140 | 55/23 | 95/45 | 85/32 | 420/190 | 41/8 · 1/1 | conquest only at r1671; late E 9393, Y 1777, K 2738 |
| SweetDreams 10060 g2 | W conquest r1372 | 130 | 15/0 | 23/0 | 34/0 | 470/none | 11/6 · 0/0 | opponent had 0 L and 0 C from r300; islands 1 at r500, 4 at r900, 6 at r1372 |

Types: A = early collapse (split ≤ r260); B = midgame economic break after an even start; C = island race lost with
a comparable army.

## 1. Army over time

Per-turn dumps, mean launchers alive per round, and where they stand [a2_bins]:

| Window | Losses: L us/them | home/mid/far us | home/mid/far them | Wins: L us/them | home/mid/far us |
|---|---|---|---|---|---|
| r0-299 | 12.0 / 11.6 | 0.52/0.31/0.17 | 0.39/0.46/0.15 | 29.9 / 22.2 | 0.24/0.68/0.08 |
| r300-599 | 12.7 / 30.4 | 0.48/0.31/0.21 | 0.27/0.42/0.31 | 61.0 / 33.2 | 0.15/0.64/0.21 |
| r600-999 | 7.0 / 66.3 | 0.67/0.29/0.05 | 0.14/0.40/0.47 | 109.5 / 17.7 | 0.11/0.73/0.16 |
| r1000+ | 3.2 / 102.9 | 0.25/0.63/0.12 | 0.14/0.32/0.54 | 317.4 / 4.9 | 0.05/0.84/0.11 |

- In losses, our army never leaves home. 52% of our launcher-turns are at home in r0-299, the same share as in r300-599,
  and the share rises to 67% in r600-999. The winning opponent is home in 39% and then 27%.
- In wins our army sits mid-map: 64-84% mid, 3-7% in the siege ring (r² 16-34 of their HQ).
- The opponent's late army is far forward: 0.54 far in r1000+, 12% of turns in the ring around our HQ. They besiege;
  we hold the middle.

Flows, median per game [a2_econ]:

| Window | Mn/100 r us/them | built L/100 r | alive C | alive L | Ad share of collection | bank Ad |
|---|---|---|---|---|---|---|
| Losses r0-299 | 441/528 | 15.7/14.7 | 10.6/11.7 | 11.1/9.5 | 0.21/0.19 | 60/63 |
| Losses r300-599 | 353/808 | 9.3/17.7 | 14.7/26.0 | 9.6/25.4 | 0.31/0.30 | 85/73 |
| Losses r600-999 | 31/782 | 5.7/17.0 | 1.6/37.1 | 1.1/56.2 | 0.42/0.27 | 177/86 |
| Wins r300-599 | 1362/666 | 34.3/23.7 | 58.0/49.6 | 72.3/41.3 | 0.30/0.55 | 248/329 |

- The Mn gap opens in r300-599: 353 vs 808. It follows the carrier gap (14.7 vs 26.0 alive), not the Ad share, which
  is the same for both sides (0.31 vs 0.30).
- Once we are losing (r600-999), our collection tilts to Ad (0.42 vs 0.27) and Ad piles up in the bank (177 vs 86).
- RockWall is the extreme: Ad share 0.84 and 0.81 in r0-299 and r300-599, and 421 Mn collected all game against their
  2853.

## 2. Engagement exchange

Engagements are counted from the extract. "exch" is their value lost over ours; "behind by 2+" is engagements won /
engagements fought 2+ launchers behind. [a2_eng]

| Window | Losses won/lost | behind by 2+: won / fought | exch | our L deaths (home) | their L deaths | Wins exch |
|---|---|---|---|---|---|---|
| r0-299 | 144/101 | 6/46 | 0.72 | 474 (167) | 443 | 1.34 |
| r300-599 | 99/144 | 2/94 | 0.56 | 641 (277) | 407 | 1.88 |
| r600-999 | 24/228 | 3/197 | 0.21 | 440 (240) | 277 | 3.03 |
| r1000+ | 22/329 | 1/312 | 0.17 | 389 (275) | 256 | 3.70 |

- Our exchange is already 0.72 in r0-299 while the numbers are level. In the long even games it falls from r0-299 to
  r300-599:

  | Game | r0-299 | r300-599 |
  |---|---|---|
  | PipesAndParabolas | 1.10 | 0.78 |
  | USA | 1.25 | 0.64 |
  | BuildSite | 1.34 | 0.53 |
  | Spots | 0.89 | 0.72 |
  | TimesUp | 0.67 | 0.56 |

  KingdomRush (0.97 → 1.46) and IslandHopping (1.13 → 1.08 → 1.24 in r600-999) are the exceptions: there the fight
  was even and the game turned on islands and on the economy.
- Once outnumbered, we win almost nothing: 2 of the 94 r300-599 engagements fought 2+ launchers behind (6 of 46 in r0-299).
- Contact quality from the per-turn dumps, r300-599 losses:
  - we are outnumbered (enemy within r² 20 > allies + 1) in 14% of contact turns, they in 5%;
  - we are alone in 14%, they in 7%;
  - mean HP at contact is 131 for us against 139; in r600-999 it is 130 against 150 (their healing). [a2_bins,
    a2_islfight]

## 3. Carriers and the economy

[a2_carriers, a2_kills]

| Window (losses) | Carrier deaths us/them | ours at home | Mn cargo lost us/them | carrier share of their kills / ours |
|---|---|---|---|---|
| r0-299 | 118/63 | 98 | 438/347 | 0.20 / 0.13 |
| r300-599 | 307/133 | 258 | 1274/366 | 0.33 / 0.25 |
| r600-999 | 302/58 | 242 | 873/95 | 0.41 / 0.17 |
| r1000+ | 216/54 | 146 | 76/200 | 0.36 / 0.20 |

- In wins the picture reverses: carrier deaths in r600-999 are 51 ours to 371 theirs, and 0.53 of our kills are
  carriers.
- **Midgame raids.** Both opponents kill our carriers at our home wells. Analyst 1 found the same mechanism in carl's
  early collapses (Carrier.frontGate, Carrier.java:501-503).
- HQ telemetry letters in losses:
  - mid phase: p (poor) 0.67, t (threatened, no carrier) 0.13, c (carrier cap) 0.11, a (anchor reserve) 0.09;
  - late phase: t 0.62. HQ.java:93 builds carriers only `!threatened`, so the economy cannot restart under a siege.
  - Wins, late phase: c (cap) 0.82.

## 4. Islands, anchors and healing

[a2_islands, a2_anchors, a2_bins, a2_islfight, a2_cstate]

| Losses | Us | Them |
|---|---|---|
| Median first island | r465 (none in 7 of 15) | r330 (all 15) |
| Their first island before the split | - | 8 of 15 |
| Anchors built / placed / lost with carrier | 79 / 29 / 15 | 154 / 95 / 2 |
| Placements before r400 | 0 | 12 |
| Placements while pressed or behind on islands | 15 of 29 (0.52) | 6 of 95 (0.06) |
| Launcher heal, HP per 100 r, r300-599 / r600-999 | 187 / 359 | 788 / 870 |
| Launcher-turns within r² 4 of an own island, r300-599 | 0.07 | 0.15 |
| Contact turns on own island, r300-599 (carl / maxwell) | 0.03 (0.03 / 0.04) | 0.13 (0.09 / 0.19) |
| Our contact turns within r² 16 of an enemy island, r300-599 (carl / maxwell) | 0.09 (0.03 / 0.21) | - |

- **Whole-game healing** (census): carl losses 13,932 HP ours against 121,921 theirs. That is about 610 launchers'
  worth of HP at 200 each, against the 2,018 launchers carl built. Maxwell losses: 27,925 against 53,904.
- **We healed 0** in 5 of 10 carl losses and 2 of 5 maxwell losses.
- **BuildSite**, r300-599: 44% of maxwell's contact turns were on its own islands, and 42% of ours were within r² 16 of
  their islands. We lost 99 launchers to their 51 while ahead although we won 11 of the 13 engagements fought 2+ ahead (value lost 11,930 vs 6,350). r600-999:
  their islands 4.5 on average against our 2.4. Conquest r999 with 45 launchers against 91.
- **Spots**: heal 25 vs 1224 HP per 100 r in r300-599, and 0.00 of our contact turns on our own islands.
- **USA**: 21% of carl's contact turns in r300-599 on its own islands (37% in r600-999).
- **Code: mending.** Our launchers heal only through mending (Launcher.java:80-108). Mending starts at HP ≤ 80
  (`MEND_HP`, C.java:250), on our own islands, from r400 (`mendDue`, Launcher.java:106-108).
- **Code: fight placement.** No fight placement that prefers our own islands was found in `fight()`
  (Launcher.java:245-376). **Unverified**: I did not read every line of it for this.

## 5. The anchor gate

[a2_gate, a2_tl]

HQ.java:68:
`gate = G.round >= C.ANCHOR_GATE_UNTIL || (!Comms.anyPressed() && Comms.islThem <= Comms.islUs)`, with
`ANCHOR_GATE_UNTIL = 1500` (C.java:200).

Rebuilt from true counts over the 25-round buckets from r400 to min(end, 1500):

| | Buckets | Pressed only | Deficit only | Both | Open |
|---|---|---|---|---|---|
| Losses | 485 | 0.05 | 0.22 | 0.60 | 0.13 |
| Wins | 171 | 0.00 | 0.01 | 0.00 | 0.99 |

- **TimesUp** (deficit only 17, both 25, open 2 of 44 buckets).
  - Islands were 2 against 4-5 from r600 to r1400, and our anchors placed stayed at 2 through r1400.
  - After the gate expired at r1500: anchors 3 (r1500), 4 (r1600), 5 (r1900), 6 (r2000); islands 4/4 at r2000.
  - The loss came on the second tiebreak, anchors placed 6 to 12.
  - **Unverified**: that the gate, rather than Mn, held anchors back in r600-1400. Our bank Mn was 50-125 in that
    stretch, and an anchor costs 80 Ad + 80 Mn. The HQ telemetry shows want-anchor on 94 of 882 mid and 154 of 2744 late
    HQ-turns.
- **Spots**: the rebuild says the gate was closed in all 18 buckets, yet we built 10 anchors. So the counts the bot reads differ from the truth
  (most likely `Comms.islThem` undercounts enemy islands).
  - Launchers far from home cannot write comms. The comment at Launcher.java:988 says so, and RULES §7 sets the write
    rule: an amplifier within r² 20, an HQ within r² 9, or an own island within r² 4.
  - The gate therefore depends on what our side manages to report. **Unverified**: Comms.islThem against the truth
    was not dumped.

## 6. Anchors that never land: the wins

[a2_cstate, a2_mapisl, a2_tl]

| Phase | T (take) | K (to located island) | Q (to predicted island) | E (no target) | Y (returning) | P (place) |
|---|---|---|---|---|---|---|
| Losses, mid | 40 | 1000 | 0 | 69 | 20 | 17 |
| Losses, late | 36 | 1365 | 0 | 505 | 206 | 11 |
| Wins, mid | 22 | 410 | 0 | 782 | 0 | 10 |
| Wins, late | 201 | 3538 | 0 | 23,319 | 11,189 | 13 |

- In 4 wins we built 136 anchors and placed 23. Repetition (both games) stalled at 4 islands of the 6 needed
  (N = 8) and won only on the tiebreak.
- The 4 islands we never held in 9921 g1 sit at e = 0.51-0.53, just past the midline (a2_mapisl 9921 1).
- SweetDreams: the opponent had 0 launchers and 0 carriers alive from r300, yet we held 1 island at r500, 4 at r900
  and reached the 6th only at r1372.
- Code path:
  - `chooseIsland` (Carrier.java:835-876) gives a located enemy-side island a penalty `d * 4 + 400` (line 847).
  - It skips every predicted island on the enemy side (line 871). Q, the predicted-target state, ran 0 turns in all
    19 games.
  - With no target, the carrier enters state E (line 778) and calls `scoutMove` (lines 885-896). That picks random
    tiles only where `!enemySide(t, ehq)`, although the comment at line 778 says "search the whole map, not home".
  - After `C.ANCHOR_TIMEOUT = 150` turns (C.java:91; Carrier.java:739) the carrier returns the anchor (state Y).
- Our winning launchers do not help. Late objective mix in wins: enemy HQ 0.97, enemy island 0.01. The enemy-island
  objective comes after sightings, recall, guard and the mid site (Launcher.java:975-998). [a2_lobj]
- **Value for the ladder is limited.** A tiebreak win is still a win. The cost shows in games like TimesUp (lost
  6/12 on anchors placed with islands tied 4/4) and in long games that give the opponent time.

## 7. Amplifiers

[robots.csv via inline python, a2_census]

- Carl builds 1-4 amplifiers per game in 10 of 10 losses. The first comes at r301-921 (median about r350, r301 in 3
  games), and a lost one is rebuilt at once (9912 g1 dies r605, new r625).
- Maxwell builds 0 and still beats us. We build 0: HQ.java:90 says "no amplifiers", `C.LAUNCHERS_PER_AMP` (C.java:122)
  is never read, and `Amplifier.java` is reachable only if an amplifier exists.
- Amplifiers are not what wins the midgame (maxwell has none). Their value to us would be in comms: far islands and
  sightings that our forward launchers cannot report (§5).

## 8. HQ defence and siege

[a2_spawn, a2_bins, a2_eng]

| Losses, r1000+ | Us | Them |
|---|---|---|
| Enemy launchers in HQ vision, per HQ-round | 12.49 | 0.13 |
| HQ-rounds with 3+ enemy launchers in vision | 0.86 | 0.02 |
| Our launcher deaths at home (of 389) | 275 | - |
| Of those, within 10 rounds of spawn | 160 | - |

- **Besieged spawns.** 470 of our 2050 launchers in losses were built besieged (3+ enemy launchers within r² 34). 322
  of them died within 10 rounds. Their median life was 5 rounds against 70 for the rest, and they made 0.08 kills each
  against 0.88, for 21,150 Mn.
  - MassiveL: 74 of 131.
  - Rainbow: 79 of 122.
  - Maze: 82 of 229.
- **Opponents under our siege**, in wins: 159 of their 1152 launchers built besieged. In our losses: 61 of 2913.
- **Code:**
  - `batchOK = threatened || G.round <= 2 || mnStart >= 45 * C.LAUNCHER_BATCH` (HQ.java:59), with `LAUNCHER_BATCH = 1`
    (C.java:99).
  - HQ.java:92 then builds a launcher whenever Mn ≥ 45, so a besieged HQ releases launchers one at a time into the
    camp.
  - **Unverified**: whether an HQ can place 3-4 launchers in one turn while besieged (blocked spawn tiles). The build
    loop allows up to 6 builds a turn (HQ.java:72), and round 1 builds "LLLL C".

## 9. What the opponents do in the midgame that we do not

1. **Keep more carriers alive** and protect them: 26.0 vs 14.7 alive in r300-599, 133 vs 307 carrier deaths. Their
   income is 808 Mn per 100 r to our 353. [a2_econ, a2_carriers]
2. **Raid our home wells.** In r300-599 their launchers are in our HQ vision at 1.83 per HQ-round against our 0.47 at
   theirs, and 0.33 of their kills are carriers. [a2_bins, a2_kills]
3. **Take islands before r400 and hold them as fighting ground.**
   - First island r330 against our r465, and 12 placements before r400.
   - 13% of their contact turns on their own islands (maxwell 19%, BuildSite 44%) against our 3%.
   - Heal 4.2× ours. [a2_islands, a2_anchors, a2_islfight]
4. **Place anchors only from a safe position.** 6 of their 95 placements came while pressed or behind on islands. They
   lost 2 anchors with carriers; we lost 15. [a2_anchors, a2_cstate]
5. **Carl only**: keeps an amplifier alive from about r350 that travels with its army, and several of them die to our
   HQ aura. [robots.csv]

## 10. Code paths that lose these games

| # | Location | What it does | Evidence |
|---|---|---|---|
| 1 | HQ.java:59, :92; C.java:99 | Builds one launcher whenever Mn ≥ 45, also while besieged | 470 besieged launchers, median life 5, 0.08 kills, 21,150 Mn |
| 2 | HQ.java:93 | No carrier while threatened | late letter t 0.62 in losses; alive C 1.6 vs 37.1 r600-999 |
| 3 | HQ.java:68; C.java:200 | Anchor gate closed while behind on islands or pressed, until r1500 | TimesUp: 0 placements r600-1400, then +4 and 4/4 islands after r1500; rebuild closed 0.87 in losses |
| 4 | C.java:77, :79 (ANCHOR_START 400, ANCHOR_MIN_LAUNCHERS 20) | No anchor before r400 | they place 12 before r400; first island r330 vs r465 |
| 5 | Carrier.java:847, :869-871, :778, :885-896 | Enemy-side islands penalised or skipped; no-target carriers search our half only | Q 0 turns in 19 games; wins: E 23,319 + Y 11,189 vs K 3,538 late; 23 of 136 anchors placed |
| 6 | Launcher.java:975-998 (pickObjective) | Enemy islands only after sighting/recall/guard/mid; owner from stale comms | late island objective 0.00-0.11 in carl losses, 0.01 in wins |
| 7 | Launcher.java:106-108 (mendDue), C.java:250 | Heal only at HP ≤ 80, own islands, from r400 | heal 187 vs 788 HP per 100 r (r300-599); contact on own island 0.03 vs 0.13 |
| 8 | HQ.java:90; C.java:122 (unused) | No amplifiers, so far launchers cannot write comms | island knowledge stale; Spots gate rebuild contradicts the 10 anchors built (unverified link) |

## 11. Candidate changes (hypotheses, none tested)

These are ranked by expected effect on long and late losses. Each needs a local A/B against c_eco3.

1. **Siege spawn discipline (HQ.java:59/92).** When 3+ enemy launchers are within r² 34 and our nearby launchers are
   fewer, bank Mn and release launchers in batches of 3-4 in one turn. Also allow carriers while threatened if the spawn
   tile faces away from the enemy. Targets type A and B tails (470 launchers, 21,150 Mn).
2. **Drop the deficit clause from the anchor gate (HQ.java:68).** Keep the pressed clause and require a located neutral
   island on our half. Targets type C (TimesUp, Spots, BuildSite). Risk: the C.java:197-199 comment records that anchors
   built under pressure were lost (9.5 of 12.4 a game), which is why the gate exists.
3. **Earlier first anchor.** ANCHOR_START 400 → about 300, gated on a located neutral island on our half and not
   pressed. Targets type C: they place 12 before r400.
4. **Fight from our islands.** Raise MEND_HP and prefer engagements within r² 4 of our own islands, and do not chase into
   theirs (BuildSite). Targets type C.
5. **Anchor conversion (Carrier.java:871, 885-896).** Allow predicted enemy-side islands when no enemy launcher has been
   sighted near them, and let E-state carriers search the whole map or follow the army. This turns tiebreak wins into
   conquests and helps TimesUp-like anchor tiebreaks. The direct win-rate gain is small.
6. **One amplifier with the army from about r350**, so forward sightings and enemy islands reach comms. Maxwell shows it
   is not required.

## Unverified

- Comms.islThem against the true enemy island count. The gate rebuild uses true counts; Spots built 10 anchors through
  a gate the rebuild calls closed.
- Whether Mn or the gate held anchors back in TimesUp r600-1400.
- Whether a besieged HQ can actually place several launchers in one turn.
- Whether `fight()` has any own-island preference (not read line by line).
- The hp-ratio column of a2_islfight is weighted by launcher-turns and is >1 for both teams. I do not use it.

## Scripts, commands and data

All scripts are in `research/diagnosis/2026-10-19-top2/scripts/`, run from the repo root with `python3 -I`. Outputs
are saved in `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/top2/a2/out/`
(`r_<script>.txt`, `eng_pg.txt`, `sa_bins.csv`, `r_islfight.txt`, `r_cstate.txt`).

| Script | Produces |
|---|---|
| a2_common.py | loaders, game lists, dump paths |
| a2_overview.py | per-game L/C trajectory, split round |
| a2_census.py | census both teams (anchors, healed, built) |
| a2_econ.py | median flows per window |
| a2_eng.py [--per-game] | engagements, exchange, L deaths by place |
| a2_carriers.py | carrier deaths, cargo, HQ letters |
| a2_kills.py | kill composition |
| a2_islands.py | first islands, island means, placements per window |
| a2_anchors.py [--list] | placement context (pressed, behind, far half) |
| a2_gate.py | anchor gate rebuild, want-anchor HQ-turns |
| a2_spawn.py | besieged spawns |
| a2_lobj.py [--per-game] | our launcher objectives (telemetry) |
| a2_cstate.py | carrier anchor states, anchors built/placed/lost |
| a2_mapisl.py MATCH GAME | island positions in e |
| a2_tl.py MATCH GAME [STEP FROM] | timeline rows (TimesUp, SweetDreams) |
| a2_sa.py [match...] | streams per-turn dumps into sa_bins.csv |
| a2_bins.py [--per-game] | phase summary of sa_bins |
| a2_islfight.py [--wins] [--per-game] | contact turns relative to islands |
| a2_dump.sh | flocked dumps of 10060, both teams |

Per-turn dumps (scratchpad `top2/`):
- carl matches: `a1/sa/<match><side>/`;
- maxwell games: `a0/sa/<match>g<game><side>/`;
- match 10060: `a2/sa/10060g<game><side>/`, made with
  `flock .../scratchpad/dump.lock env DUMP_XMX=500m tools/replay-dump.sh ... --sa`.
