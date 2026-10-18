# Panel losses for c_loose1: verified claims, mechanisms and ranked changes (2026-10-18)

Judged 2026-10-18 at 15:56 PDT. Four lenses (economy, deaths, fights, islands) each made claims. An adversarial pass then recomputed every claim. This file keeps only the claims that held or were adjusted, with the recomputed numbers.

**Data**
- Panel: `gauntlet/20261018-194500-panel-c_loose1/results.csv`, matches 9475-9484, 100 games, 79 won.
- Previous panel: c_isle1, `gauntlet/20261018-044752-panel-c_isle1`, matches 9039-9048, 73 won. It has the same opponents and maps, so each (opponent, map) cell pairs across the two panels.
- Extracts: `matches/<id>/extract/*.csv`.
- Code read: `src/c_loose1/`.

**Groups**
- SL: the 17 losses to the 4 strong bots (awesomelemonade 6, jmerle 5, pranayagra 3, vrangr1 3).
- SW: the 23 wins against those 4 bots.
- WW: the wins against the other 6 bots.
- The fights lens also counts NotLLeon as strong, which gives SL n=18 and SW n=32. Those figures are marked "5 bots".

**The 21 losses**
- 16 are lost on both panels.
- 5 flipped from a win to a loss: awesomelemonade BatSignal, georgezhang02 BatSignal, vrangr1 Hah, yaonam ReverseFunnel and britacatalin Cornucopia.
- By map: BatSignal 4, ReverseFunnel 3, IslandHopping 3, DefaultMap, Cornucopia, Forest, Maze and Hah 2 each, MassiveL 1.

**Scripts**
- The lens scripts are in `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/`, in the folders `econ/`, `deaths/`, `fs/` and `isl/`.
- The judge's spot checks (section 1.7) are `judge/j1.py` to `j3.py` in the same folder.

**What is new or changed since the prior diagnoses**
(2026-10-17-panel-losses-c_hr1, 2026-10-18-launcher-micro-vs-strong, 2026-10-18-structural-designs)
- C.ARMY false helped through the carrier war, not through fights. Over the 40 paired strong-bot games, our carrier deaths by r300 fell 3.83 per game (t -3.6) and the enemy's rose 3.30 (t +2.7). Launcher losses by r300 did not move for either side (34.9 -> 35.2 and 40.6 -> 40.5 over 50 cells, 5 bots).
- The losses are still mostly army collapses, now about 30 rounds later. In 16 of 21 losses the army collapses first (median r300). Only 5 losses are island races.
- c_loose1 gained nothing on the 4-island maps. BatSignal, Hah and ReverseFunnel went 21-9 against 22-8 on c_isle1, and they hold 9 of the 21 losses. All of the +6 came on maps with more islands (58-12 against 51-19).
- New island-side faults on small maps:
  - The first anchor waits for the r400 blind rule (ANCHOR_BLIND_FROM).
  - On ReverseFunnel, anchors pile up and are never placed.
  - The conquest threat rule fires late, because the team undercounts enemy islands.
- No economic lever from this panel is both strong and untested. The economy levers in hand are either already in abl2/abl3 or reach only a small part of the gap.

## 1. Verified claims

### 1.1 The army gap is a mana production gap (SL n=17, SW n=23)
- **The launcher trade is level through r300.** Launchers lost by r300: SL 45.2 ours vs 44.8 theirs. SW 32.1 vs 38.7.
- **Production splits from r100.** Comparing SL with SW:
  - Launchers built per 100 rounds, SL ours/theirs: r100-200 19.5/21.3, r200-300 16.6/23.2, r300-400 13.1/25.5. SW mirrors this: 22.1/14.9, 21.6/13.7, 19.9/13.1.
  - Mana collected per 100 rounds, SL: 626/769, 547/908, 445/1088. Ours falls while theirs rises.
- **The gaps grow from r200.** In SL at r200/r300/r400:
  - Alive-launcher gap: -0.9 / -9.1 / -24.5 (r400 n=16).
  - Build gap: -2.1 / -8.6 / -21.6.
  - By r400 the trade accounts for 2.9 of the 24.5 alive gap (12%). The rest is production.
- **Mana limits production.** The r100-300 mana gap is 504 Mn, which is 11.2 launchers at 45 Mn. The build gap is 8.4 launchers.
- **We do not float mana.** Our bank_Mn is 85-101 at every 50-round mark in SL; at r300 it is 85.6 against their 107.6.
- **The build gap shrank since c_isle1.** On the same 17 opponent-map cells, the r300 build gap is -13.9 on c_isle1 and -8.6 on c_loose1. Over all 40 paired strong-bot games it went from -3.2 to +6.0.

### 1.2 What c_loose1 changed (paired against c_isle1)
Over 40 strong-bot cells (deaths lens; the economy lens gives the same means):

| Measure at r300 | c_isle1 | c_loose1 |
|---|---|---|
| Our carrier deaths | 11.65 | 7.83 |
| Their carrier deaths | 9.85 | 13.15 |
| Our carriers alive | 16.6 | 20.2 |
| Our carriers built | 28.2 | 28.1 |
| Our Mn collected | 1695 | 1971 |
| Their Mn collected | 1921 | 1689 |
| Our launchers built | 57.6 | 63.0 |

- By r150 the significant change is in their carriers: their deaths rose 1.57 (SE 0.52, t +3.0). Ours fell 0.78, which is not significant (t -1.4).
- Over 50 cells (5 bots):
  - Our home carrier losses (prog < 0.4) went 9.5 -> 5.9 (t -4.2).
  - Their carrier losses on their half (prog >= 0.5) went 8.6 -> 11.7.
  - Launchers built: ours 58.2 -> 63.4 (t +4.5), theirs 59.3 -> 55.1 (t -2.7).
- Wins by the r150 carrier-death gap, c_loose1 vs c_isle1:
  - We were 2 or more down: 2/8 vs 1/15.
  - Within 1: 9/20 vs 12/20.
  - They were 2 or more down: 12/12 vs 4/5.
- For predicting the win at r150 (c_loose1, n=40), the carrier-death gap beats the launcher-death gap (AUC 0.80 vs 0.66). But Mn collected (0.87) and army value (0.83) predict as well or better.

### 1.3 Carriers in the losses
- **Carrier deaths by r300 per game:**
  - c_loose1 SL: 11.6 ours vs 7.1 theirs.
  - c_loose1 SW: 5.0 vs 17.6.
  - c_isle1 losses: 15.7 vs 5.5.
- **Last state at death.** In SL: F (flee) 41%, G (going to a well) 31%. In SW: F 52%, G 18%. Spawn kills are 1% of our SL carrier deaths up to r400.
- **Fleeing is the yield sink. Walking is not.** Share of our carrier turns, all maps, mid phase:
  - Flee: SL 6.5% vs SW 0.7%, about 9 times as much (SL 96k turns, SW 237k).
  - Going to a well: SL 17.9% vs SW 18.4%, no difference.
- **The mana gap in r200-300 splits into count and yield.**
  - Carrier count gives 189 Mn per game (52%). Mana per carrier gives 172 (48%). On c_isle1 the split was 70/30.
  - About a third of the yield part is role mix, not lost turns. Mana is 0.75 of our collection against 0.81 of theirs. Total (Ad+Mn) per carrier-round is 0.465 vs 0.531.
- **Carriers alive and yield in r200-300.** Average carriers alive: SL 15.7 ours vs 21.2 theirs (c_isle1: 12.6 vs 24.0). Mn per carrier-round: SL 0.347 vs 0.428. Ours in SW: 0.389.
- **Carriers built in r200-300.** Ours 6.1 in both panels; theirs 9.3 and 9.7.
- **Our HQs are under pressure far more often.**
  - Pressured share of HQ buckets in r101-300: SL 32%, SW 14%.
  - Pressured buckets up to r400: SL ours n=207 building 0.52 carriers per bucket, theirs n=80 building 0.82.
  - Unpressured buckets: SL ours 1.00 (n=429) vs theirs 1.08 (n=556). SW ours 0.92 (n=770) vs theirs 1.22 (n=572).
- **Decomposition of the SL carrier build gap** (7.6 per game): the pressure mix explains 25-47%; the unpressured build rate explains 35%.
- **Under heavy pressure (pressure34 >= 150):**
  - Carriers per bucket: ours 0.02 (n=46, Ad banked 213); theirs 0.31 in SL (n=13, Ad 54) and 0.50 in SW (n=113).
  - Code 't' (carrier withheld under threat), share of SL HQ turns: 11.6% in r200-300 and 24.5% in r300-400. In SW: 4.1% and 1.0%.
- **Carriers born at pressure >= 75 that die within 50 rounds:** theirs 57% in SL (n=21) and 95% in SW (n=79). Ours 64% in SL (n=11).
  - Their SL carriers born under pressure still deposit 59 Mn each. Their SW ones deposit 3 Mn each, ours 8 Mn each.
- **Team Ad at r300:** SL 212.6 ours vs 66.9 theirs. About half of ours sits at besieged HQs (101 vs 111 per game).

### 1.4 Wells, caps and the middle
- **Middle mana wells.** The middle is wells with p 0.4-0.6, where p = distance to our nearest HQ over that plus distance to theirs.
  - Mn per game, SL ours|theirs: r0-100 156|167, r100-200 133|239, r200-300 84|348, r300-400 14|408.
  - SW: 166|120, 227|108, 288|104, 280|32.
- **The middle's share of the r200-300 gap (490 Mn) depends on the definition.**
  - It is 54% with Euclidean distance and 38% with Chebyshev distance.
  - Leaving out wells within r2 64 of any HQ, the far-middle gap is 202 per game (41%).
  - 81% of the far-middle gap (2,779 of 3,434 Mn) comes from the 3 Forest and Cornucopia losses, which already have a Mid site.
- **The middle swing starts while armies are level.** Launchers alive in SL at r150: 14.4/14.3. At r200: 15.2/16.1.
- **Mid.pick has a site only on Cornucopia and Forest**, because of its `urgent` test. This was already in TRAINING_LOG 2026-10-16 01:15 PDT.
  - On the no-site maps (Hah, Maze, BatSignal), wins mine the middle anyway: SW n=5 428|28 against SL n=7 104|286.
- **In 6 of 6 cell flips between panels, the game we won is the one where we mined more of the middle well.** This is correlational.
- **On BatSignal the cap binds.** BatSignal has 1 HQ and 1 known mana well.
  - Our carriers alive at r150/r250/r350: 7-9 / 10-12 / 10-17, which fits the cap.
  - The cap code 'c' is 0.40-0.55 of HQ turns up to r400 in 14 of 20 games.
  - Ad at r350 against the 4 strong bots: 270-360.
  - vrangr1 runs 16-24 carriers and pranayagra 17-19.
- **pranayagra's BatSignal edge is its middle well, not more carriers.**
  - It mined 346 Mn at (32,6) in r101-300; we mined 0 there in that window.
  - At its home well it gets only +58 Mn over us, with about 45% more carriers.
  - Only vrangr1's +260 Mn at home supports a higher cap.
  - 2 of the 4 BatSignal losses had equal or better economy (awesomelemonade 1804 vs 1650 Mn, georgezhang02 1711 vs 1700).
- **Carriers queue at the home mana wells on ReverseFunnel and Hah, in wins and losses alike.**
  - Waiting carriers per round in r101-300: ReverseFunnel 3.66 (c_isle1 3.95), Hah 3.33 (c_isle1 2.86). For comparison, BatSignal 0.43 and DefaultMap 1.16.
  - The ReverseFunnel home well (2,17) has 7 of 9 tiles in cloud, which caps it at 7.83 kg/round. We get 6.18-7.24 on c_loose1 and 5.86-6.99 on c_isle1.
- **DefaultMap (20,23) is outside the HOT rule.** homeD2 49 is under HOT_HOME_D2 64, and 21% is under HOT_FRONT_PCT 36.
  - In the two DefaultMap losses lost on both panels, trips there went 32 -> 56 and the death rate per trip 0.41 -> 0.46-0.50. Total carrier deaths in those two games fell (48 -> 41), because deaths at (7,21) halved (30 -> 15).
  - The jmerle win on DefaultMap lost 15 carriers there in 40 trips (0.375 per trip), so the well does not separate wins from losses.
- **The Forest site (29,48)** is credited with 21 trips, 18 deaths and 30 kg in the 2 Forest losses on c_loose1 (10/9/0 on c_isle1). The wins have 64/3/1740.
  - By death location, deaths within r2 100 of the site rose only 12 -> 15. All carrier deaths in those 2 games went 42 -> 39.
  - An outnumbered carrier at the site already avoids it itself for 64 rounds (midLeave plus hotLocal). Only the shared hot mark is missing.

### 1.5 Launcher fights and healing
- **Per-launcher fighting is at parity** (5 bots, SL n=18).
  - Damage per kill by r300: 214.8 ours vs 208.1 theirs.
  - Launchers born by r200 (742 ours, 778 theirs): living more than 100 rounds, 0.30 vs 0.30; dead by r300, 0.90 vs 0.89.
  - Hits per launcher built: 10.7 ours vs 6.9 theirs. Their extra hits come from their extra launchers.
  - Focus and kill conversion reverse between SL and SW: focus 0.365/0.504 in SL against 0.541/0.333 in SW.
- **Lone launcher deaths did not rise with ARMY off.**
  - Deaths in engagements where we only ever had 1 launcher (joinA 1), by r300: 2.00 per game (4%) in SL, 1.96 (5%) on c_isle1. The outnumbered bit is set on 15% of SL deaths vs 13% of SW deaths.
- **ARMY off moved where launchers die.** Paired over the 15 cells lost on both panels:
  - Deaths on our half (prog < 0.33): -4.27 per game (SE 1.52).
  - Deep deaths (prog > 0.67): +2.20 (SE 0.91).
- **March-mode deaths with objKind 0 within r2 200 of our HQ** (sighting, recall or guard objectives), per game by r300: SL 5.29, SW 2.04, c_isle1 losses 3.43.
  - These launchers die in large, roughly even fights: peak 10.9 ours vs 11.2 theirs, joinA 1 in only 3%.
  - Over all 40 strong-bot pairs the change is +0.60 (SE 0.47).
- **After r300 the losing side's launchers die outnumbered, and this mirrors in our wins.**
  - Of our post-r300 SL launcher deaths, 60% are in fights entered 2 or more down, and 34% in fights where at most 2 of ours ever joined.
  - The opponents in SW: 65% and 29%.
  - Paired on 16 cells lost on both panels: 24.9 -> 22.1 such fights per game (t -0.74), so not worse.
- **Healing follows island control.**
  - Healed as a share of damage taken: SL them 19.9%, us 3.9%. SW us 17.7%, them 2.9%.
  - There is little healing before r300 (an estimated 39 vs 163 HP in SL).
- **awesomelemonade and pranayagra heal more per island-round at equal island holding.** Pooled over each opponent's 10 games, ours vs theirs:
  - awesomelemonade 2.32 vs 4.98 (island-rounds 11,183 vs 10,493).
  - pranayagra 1.02 vs 5.27.
  - vrangr1 2.35 vs 3.47.
  - jmerle 2.36 vs 2.24.
- **awesomelemonade's island fortress.** In 9478 g0, g5 and g7 the armies were level or we led at its first island (11/9, 15/9, 24/25).
  - In the 150 rounds after, our damage per kill rose to 308 against its 198, and kills went 19.0 vs 32.3.
  - It healed 7,945, 3,860 and 5,001; we healed 1,144, 0 and 252.
  - Over the 6 losses to it, our damage per kill is 340 while it holds an island and 211 otherwise.
  - When it anchored first at level armies we went 1-3. g9 ReverseFunnel was won.

### 1.6 Islands and anchors
- **16 of 21 losses collapse on army first.** A collapse is 3 samples with enemy alive_L >= max(10, 2x ours), counted from r100.
  - Median collapse r300. The enemy leads on islands a median 150 rounds later. The game ends a median 422 rounds after the collapse.
  - Without the r100 cutoff the split is 17/4, not 16/5. c_isle1 was 19/8.
  - In wins, 2 of 79 collapsed and 4 of 79 ever trailed on islands.
- **The first anchor on small maps waits for the r400 blind rule.**
  - The first anchor build lands in r376-425 in 12 of 19 games on BatSignal (6/9) and ReverseFunnel (6/10). On the other 8 maps, the first build is by r300 in 68 of 74 games.
  - In the 6 BatSignal blind games, the HQ held a median 190-255 idle Ad on the cap code 'c' (69-100% of turns), while banking only 20-80 Mn.
  - Once built, blind anchors are placed fast on BatSignal: median 12.5 rounds (n=12). ReverseFunnel takes a median 81 rounds (n=10).
- **Blind vs located first anchor, pooled with c_isle1:** blind 15W-9L (n=24), located 13W-2L (n=15).
  - Against the 6 weaker bots both are 10-2. The whole gap is the 4 strong bots: blind 5-7, located 3-0.
- **The paired flip, awesomelemonade BatSignal:**
  - c_isle1 placed at r354, before the enemy's r392, and won at r466.
  - On c_loose1 the enemy anchored at r276 with armies at 11 vs 10. Our blind anchor landed at r487 and we lost.
- **The ReverseFunnel anchor sink:**
  - 9480g9 (NotLLeon): 23 anchors built, 0 placed, 7 couriers killed at prog 0.19-0.33. That is 1,840 Mn, 34% of our Mn, about 41 launchers. The enemy sat one island short of conquest for 337 rounds.
  - 9483g9 (yaonam): 25 built, 1 placed, 12 couriers killed, 28% of Mn. Under the collapse rule above this game is collapse-first.
  - ReverseFunnel wins (n=7): 3-11 built, 3-6 placed, at most 2 courier deaths, 8-16% of Mn.
- **The island gate leaks on small maps because we undercount enemy islands.**
  - In losses, 33 of 116 anchors were built while truly behind on islands with no HQ pressed; 31 of the 33 are on 4-island maps.
  - Given a truly-behind, unpressed bucket, the gate was open in 63 of 119 in losses and 18 of 54 in wins.
- **Launchers do not contest enemy islands in losses.** Launcher turns aimed at an enemy island: 0 in 16 of 21 losses, although the enemy held islands in all 21. In wins where the enemy held islands, 12 of 13 had such turns. 12 of the 16 zero-turn losses are collapse-first.
- **The line-66 anchor veto.**
  - Its islThem half does not suppress anchor building. Anchor activity in unpressed buckets: 0.51 when they lead on islands, 0.45 at 0-0, 0.74 when we hold one.
  - Its anyPressed half does bind. In the awesomelemonade DefaultMap and Maze losses, one HQ was pressed all game and no anchor was ever wanted.
- **Placement in SL.** We built 4.9 anchors per game and placed 1.3. 4 of the 7 SL games with no placement built no anchor at all.
- **9484g2 (britacatalin Cornucopia), the island-tiebreak loss:**
  - We built 0 anchors in 2,000 rounds.
  - One HQ was pressed from r250 (121-182). That closed the gate team-wide, and that HQ banked 300-450 Ad.
  - The game was an army wipe: 0 robots from r600.

### 1.7 Judge spot-checks (not lens-verified; scripts judge/j1.py to j3.py)
**A dead anchor reserve.** Code 'a' means the 80 Ad + 80 Mn anchor reserve made the next unit unaffordable. The check counts HQ buckets (r275-1500) with 'a' on 12 or more of 25 turns and no anchor built in that bucket or the next:
- Per game: SL 3.71, SW 1.39, WW 1.02.
- 46 of the 63 SL buckets come from three jmerle losses: IslandHopping 27 (14 in a row), Forest 11 and Cornucopia 8.
- In jmerle IslandHopping, from r275 to r700, both of our HQs held 90-150 Ad and 20-65 Mn. The reserve blocked carriers there (the Ad path in Telemetry.hqReason), while the Mn half of the anchor never arrived.
- In 30 of the 63 SL buckets, Mn was under 45 and Ad at least 50, so the blocked unit was a carrier.
- Those buckets built 0.59 carriers and 0.65 launchers per bucket. Unpressured buckets without the reserve built 0.84 and 2.31. Low income confounds this comparison.

**Unplaced anchors by map size.** Per game, unplaced anchors (built minus placed):
- Small maps (5 islands or fewer): weak-bot losses 16.7 (n=3), weak-bot wins 0.7 (n=15), SL 2.5 (n=6), SW 2.7 (n=6).
- Big maps: weak-bot wins 9.2 (n=41), SW 11.3 (n=17).
- So a cap on unplaced anchors is safe only on small maps.

## 2. Rejected claims (one line each)
- "The army gap is entirely mana": by r400 the launcher trade is 12% of the alive gap (2.9 of 24.5).
- "Code 'p' on 84% of turns shows only mana binds": wins have 80-81%, and 'p' means both Mn < 45 and Ad < 50.
- "bank_Mn is 86-101 in every group": SW r400 is 116.
- "Middle-band engagements 4.2 vs 8.7": recomputed 3.5 vs 6.5, and 2.1 vs 2.5 on the no-site maps.
- "Dropping `urgent` reaches about half the mana edge": it reaches about 8% (38.5 Mn per SL game in r200-300).
- "Carrier flee/walk shares F 8.4/0.8 and G 20.9/16.6": these hold only on a 5-map subset; over all maps G is 17.9 vs 18.4.
- "Unpressured HQs build carriers as fast as the strong bots'": true only in SL. Over 40 strong-bot games it is about 0.95 vs 1.15.
- "Withholding carriers under siege is right": the strong bots' under-siege carriers in their wins deposit 59 Mn each (n=21).
- "WW die-rates show what strong bots do": WW are weak bots.
- "BatSignal Mn per carrier-round 0.683 vs 0.670": recomputed 0.557 vs 0.573.
- "We never touch (32,6)": true only in r101-300; over whole games we mine it in 3 of 20.
- "The ReverseFunnel cycle is 82 vs 68 rounds": at r101-300 it is 67.8 vs 58.0, and the SL group was one game.
- "Hah waits 13.1 vs 8.4 per trip separate losses": c_isle1 shows 6.5 vs 6.1.
- "Near-HQ carrier deaths separate losses": 53% in losses vs 56% in wins.
- "Our early carrier deaths fell": by r150 the fall is not significant (t -1.4).
- "Deaths at DefaultMap (20,23) doubled": trips doubled; the rate went 0.41 -> 0.46, and total deaths in those games fell.
- "Home-well deaths 10.0 -> 5.47 per game": recomputed 7.61 -> 5.24.
- "HOT eligibility protects carriers": HOT-covered wells die at 0.275 per trip in losses, about the same as 0.337 for uncovered wells.
- "Forest site deaths more than doubled (8 -> 18)": by death location, 12 -> 15.
- "The opponent's Forest twin gave 111 trips, 0 deaths, 1706 kg": recomputed 71/0/654.
- "Squad deaths near the site went 93 -> 70": recomputed 77 -> 57 by r300.
- "Guard and recall launchers now go alone": 3% are alone (4% on c_isle1), in fights of 10.9 vs 11.2.
- "A camped HQ dribbles 1 launcher per 50 rounds": it is 1 per 31-38.
- "The turn comes about r290": census turn_round has a median of r155. r280 is when the enemy army first doubles ours.
- "The healing gap closed except pranayagra and vrangr1": awesomelemonade heals 2.1x our rate pooled.
- "c_loose1 lowered our heal rate": the drop depends on the threshold and is not significant.
- "The island race decides level games (11/15 vs 4/13)": the placed-first group led about 3:1 in launchers. In strictly level games it was 0/3 vs 2/8.
- "The line-66 veto never binds": its anyPressed half binds.
- "Most post-r300 deaths are lone arrivals": about a third are; 60% are fights entered 2 or more down.
- "Behind fights fell 23.5 -> 19.9": that compares different games. Paired it is 24.9 -> 22.1 (t -0.74).
- "Waiting for the blind anchor costs games (15-9 vs 13-2)": this is an opponent effect. Against the weaker bots both are 10-2.
- "ReverseFunnel losses at army parity": parity holds only on army value counting carriers. The launcher ratio was 0.72, and yaonam was collapse-first.
- "c_isle1's NotLLeon ReverseFunnel loss shows the same sink": it put 13.4% of Mn into anchors, inside the win range.
- "Enemy island time rose on 4-island maps": paired it is 8 up and 7 down. Two BatSignal games give 1,207 of the 1,470.
- "Gate-closed buckets never come from pressure alone": false on c_isle1.
- "Anchors built while behind, 28% vs 0.9%": mostly a denominator effect. Given a behind bucket it is 33/119 vs 9/54.

## 3. Mechanisms: why we still lose to the strong bots

1. **The biggest mechanism is the mana gap from r100 to r300, with an even launcher trade.** It decides 16 of the 21 losses as army collapses (median r300); islands only finish them.
   - In r200-300 the strong bots collect 908 Mn per 100 rounds against our 547.
   - **Where the gap comes from.** The middle wells give 38-54% of it, depending on the distance metric; most of the far-middle part is on Forest and Cornucopia. The rest splits about evenly between fewer live carriers (52%) and less Mn per carrier (48%). About a third of the per-carrier part is Ad mining while Ad floats (team Ad 213 vs 67 at r300). Much of the rest is fleeing: F is 6.5% of our carrier turns in SL against 0.7% in SW.
   - **Why we have fewer live carriers.** Our HQs are pressured in 32% of SL buckets against 14% in SW, and they stop building carriers there.
   - **What c_loose1 fixed.** It cut our carrier deaths and raised theirs. In the losses it did not change who holds the middle, and no tested lever has.
2. **Small maps lose the island race.** BatSignal, Hah and ReverseFunnel hold 9 of the 21 losses, and c_loose1 gained nothing there.
   - Our first anchor waits for r400 when no neutral island is located (12 of 19 games).
   - The team undercounts enemy islands. So the anchor gate leaks, and ISLE_THREAT, which needs 2 seen enemy islands on a 4-island map, stays silent.
   - On ReverseFunnel, couriers lose or hold anchors, and new ones keep coming: 23-25 built in the 2 sink losses.
   - awesomelemonade turns an early island into a healing fortress. At level armies, our damage per kill goes 201 -> 308.
3. **Fights, cohesion and spawn camping follow army size.** They are not causes before r300.
   - Per-launcher micro is at parity.
   - Lone deaths did not rise with ARMY off.
   - Spawn kills are 0.43 launchers and 0.10 carriers per loss before r300. 65% of all spawn kills come from 2 late games.
4. **jmerle loses us anchors and carriers through a dead reserve** (judge spot-check, n=3 games). Our HQs reserve Ad for an anchor whose Mn never arrives. On IslandHopping this blocked carriers for about 400 rounds while 90-150 Ad sat idle.

## 4. Ranked buildable changes

Every change below is either a one-knob `tools/param.py` cell on c_loose1, or a new constant whose default reproduces c_loose1 exactly, so it becomes a one-knob cell. Screen each cell on the BatSignal, Hah and ReverseFunnel panel cells first, then on the rest.

### 1. Blind anchors from r250: `ANCHOR_BLIND_FROM=250`
- **Change:** `src/c_loose1/C.java` ANCHOR_BLIND_FROM 400 -> 250 (= ANCHOR_START). It is read in `HQ.java` build(), in `anchorAllowed` (line 67).
  - The gate, ANCHOR_BLIND_PERIOD 150 and the courier's own search stay unchanged.
  - Test: `tools/param.py make c_loose1 <new> ANCHOR_BLIND_FROM=250`. The param constraint ANCHOR_START <= ANCHOR_BLIND_FROM holds.
- **Expected effect:**
  - It moves our first anchor from about r400 to about r250-260 in the 12 small-map games where it waits today.
  - On BatSignal the blind courier places in a median 12.5 rounds. That puts our anchor before awesomelemonade's r276 there; the paired c_isle1 win came from anchoring first.
  - Plausible gain: 1 or 2 games (awesomelemonade BatSignal, perhaps jmerle ReverseFunnel, where the enemy anchored at r287 and our median placement lag is 81).
  - On the other 8 maps (Hah included), 68 of 74 games already anchor by r300 on a located island, so they change little.
- **Evidence and limits:** The mechanism is confirmed. The blind-vs-located outcome split is an opponent effect, so the gain rests on the few strong-bot games.
- **Risk:**
  - Each anchor costs 80 Mn, about 1.8 launchers, in the phase where mana binds (HQ Mn 20-80 in r275-400).
  - On ReverseFunnel, earlier blind anchors may feed the anchor sink. Run it with change 3, or read its ReverseFunnel cells for courier deaths.
  - On big maps, blind anchors also start at r250 once no located neutral island remains. If those cells lose, gate the change on `rc.getIslandCount() <= 5`.
- **Prior attempts:**
  - c_anc3 (ACCEPTED) set the r400 blind rule after untargeted anchors were lost.
  - c_scout1 (REJECTED, net -2) tried earlier anchors on few-island maps through a claimed scout carrier. This change takes no carrier off mining.
  - c_swarm3 (anchors from r150, dropped h2h) predates the c_anc3 gate.
  - The abl3 cell c_ec09 (ANCHOR_START 400) leaves these 12 games unchanged, so the earlier direction is untested.

### 2. Conquest threat at the enemy's first island on small maps: `ISLE_MARGIN_SMALL=2`
- **Change:** `src/c_loose1/C.java` ISLE_MARGIN_SMALL 1 -> 2. It is used by `Launcher.conquestThreat()` (line 842).
  - On 4-island maps conquestNeed(4) = 3, so the threat fires at 1 enemy island instead of 2. On 5-island maps it fires at 2 instead of 3. Maps with ISLE_LARGE_N (6) or more islands do not change.
  - Test: `tools/param.py make c_loose1 <new> ISLE_MARGIN_SMALL=2`.
- **Expected effect:**
  - Even-id launchers go for the enemy's first island before it becomes a healing fortress.
  - It also works around the undercount, since one seen enemy island is now enough.
  - Targets: when the enemy anchored first, we went 3-11 (n=14). awesomelemonade's fortress decided 3 level games (BatSignal, Hah; MassiveL has 12 islands and is unaffected).
  - 30 panel games change (BatSignal, Hah, ReverseFunnel, all opponents). Plausible net 0 to +2.
- **Risk:**
  - It sends half the marching army to an island the enemy heals on. That is the fights lens's "feeding a healing siege".
  - It may pull launchers off home defence in collapse-first games.
  - 9478g9 ReverseFunnel was won without it, although awesomelemonade anchored first.
  - Read the abl2 cell c_lb08 (ISLE_THREAT=false) first: if the threat rule is worth nothing at margin 1, a lower bar is unlikely to help.
- **Prior attempts:**
  - c_isle1 (ACCEPTED) is this rule at margin 1.
  - c_end1/c_end2 (REJECTED, panel) sent a fixed share to islands from r1700. This change fires at any round, only under a threat.
  - A follow-on if it helps: the islands lens's lever in `Launcher.islandScan()`, which counts located islands that are not ours as theirs from r400 on small maps.

### 3. Cap unplaced anchors on small maps: new `C.ANCHOR_SLACK`
- **Change:** `src/c_loose1/HQ.java` build(), in the `wantAnchor` condition (line 72). Add:
  `&& (rc.getIslandCount() > 5 || anchorsBuilt - Comms.islUs < C.ANCHOR_SLACK)`
  - New constant in `C.java`: `ANCHOR_SLACK = 99`. This default is the identity.
  - Test: `tools/param.py make c_loose1 <new> ANCHOR_SLACK=3`.
  - The count is per HQ against team islands, so on multi-HQ maps the team can hold up to 3 unplaced anchors per HQ.
- **Expected effect:**
  - It stops the ReverseFunnel sink: 23 built and 0 placed (34% of Mn) against NotLLeon, 25 built and 1 placed (28%) against yaonam.
  - ReverseFunnel wins put 8-16% of Mn into anchors.
  - Plausible gain: 1 game (NotLLeon; the yaonam game collapsed on army first). It lowers the cost of change 1 on ReverseFunnel.
- **Risk:**
  - Low on small maps: wins there leave 0.7 (weak bots) and 2.7 (SW) anchors unplaced per game.
  - Big maps are excluded, because their wins leave 9.2-11.3 unplaced per game and an uncapped count there is part of how they win.
  - islUs drops when we lose an island, which loosens the cap at the right time.
- **Prior attempts:**
  - None has capped outstanding anchors.
  - c_line8a (ACCEPTED: anchors only for located neutral islands) and c_anc3 (ACCEPTED: the gate) restrict when anchors start.
  - c_ab06 (ANCHOR_FLEE off) was neutral.
  - A global ANCHOR_PERIOD or ANCHOR_TIMEOUT change would also hit the big-map wins, so it is not proposed.

### 4. Release a dead anchor reserve: new `C.ANCHOR_RESERVE_MAX`
- **Change:** `src/c_loose1/HQ.java` build(), where `resAd`/`resMn` are set (line 82).
  - Track the first round of the current wantAnchor stretch. After `C.ANCHOR_RESERVE_MAX` rounds with no anchor built, set the reserve to 0. The HQ still builds the anchor the moment both 80 Ad and 80 Mn are in hand.
  - Default 2000, the identity. Test: `ANCHOR_RESERVE_MAX=50`.
- **Expected effect:**
  - Carriers resume while Ad idles under a reserve whose Mn never arrives.
  - This targets 3 of the 5 jmerle losses (dead-reserve buckets: IslandHopping 27, Forest 11, Cornucopia 8).
  - The size of the gain is unknown. The evidence is the judge spot-check only (SL 3.71 vs SW 1.39 such buckets per game), and low income confounds it.
- **Risk:**
  - Fewer anchors complete on maps where the reserve does eventually fill.
  - Read the jmerle cells of c_ec09 and c_ec10 first, since both shorten the reserve window.
- **Prior attempts:** none changed the reserve itself. c_mana1 and c_adlo2 changed Ad mining, not the reserve.

### 5. Mid site without the `urgent` test: new `C.MID_URGENT`
- **Change:** `src/c_loose1/Mid.java` pick(), line 78. Change `!urgent ||` to `(C.MID_URGENT && !urgent) ||`.
  - New constant `MID_URGENT = true`, the identity. Test: `MID_URGENT=false`.
  - The id%3 squad then also holds the in-band mana well on Hah, BatSignal, Maze, MassiveL and ReverseFunnel.
- **Expected effect:** small. It reaches at most 38.5 Mn per SL game in r200-300 (8% of the gap). On the no-site maps, wins already mine the middle without a site.
- **Risk:**
  - The Cornucopia site moves from (26,34) to (26,24), on a map we win 3 of 4 against strong bots.
  - A third of the launchers leave on more maps.
  - Build it only if the abl2 cell c_lb05 (MID=false) shows that the Mid squad earns its keep.
- **Prior attempts:** c_mid1 (REJECTED alone) introduced the squad; c_gp1 (ACCEPTED) kept it with home-well defence and packing. This change widens the site rule only.

### 6. Hot marks for near-home contested wells: `HOT_HOME_D2=48 HOT_FRONT_PCT=20`
- **Change:** `src/c_loose1/C.java` HOT_HOME_D2 64 -> 48 and HOT_FRONT_PCT 36 -> 20. Both are used by `Carrier.frontGate()`.
  - Two param.py knobs, in one cell.
  - Newly eligible wells: DefaultMap (20,23) and (22,27); Maze (3,34), (10,39) and (22,14).
- **Expected effect:** low.
  - Wells that HOT already covers die at 0.275 per trip in losses, about the same as the uncovered class (0.337).
  - (20,23) kills as many carriers in a jmerle win as in the losses.
- **Risk:** the newly covered wells carry 557 trips and 15,600 kg in weak-bot wins (Maze (10,39) most of all).
  - Build it only if the abl2 cell c_lb04 (HOT=false) loses. If HOT=false is neutral, widening HOT will not help.
- **Prior attempts:**
  - c_well6/c_well7 (REJECTED) introduced hot wells.
  - c_well10 (HOT off, REJECTED).
  - c_di1 (well drop after two flights, REJECTED net -2) is a per-carrier version.

### Not proposed, and why
- **Higher BatSignal carrier cap** (count the symmetric image of each known well when there is one HQ): c_ec02 (CAP_PER_MN_WELL=12) and c_ec03 (CAP_MIN_PER_HQ=9) already raise BatSignal's cap. Read their BatSignal cells. pranayagra's edge there is its middle well.
- **Sending crowd-timeout carriers to the middle well:** it repeats c_seam1/c_seam2 (REJECTED, panel). The existing well switch already reaches Hah (21,14), and the home-well rate falls in losses, which points to harassment.
- **A shared hot mark at the Forest site:** n=2. Carriers already avoid the site for 64 rounds themselves. Wait for c_lb05.
- **Regroup for objKind-0 marches:** the "go alone" mechanism is refuted (3% lone). regroup() also skips recalled launchers. Cohesion is being settled by c_lb11/c_lb12.
- **Launcher micro, retreat-when-alone, healing work in general:** parity holds. Anything on healing should target awesomelemonade or pranayagra only.
- **Carriers under siege:** repeats c_thr1 (REJECTED, net -1) and c_hq1 (REJECTED, screen). The opponent data are mixed (59 Mn per carrier in their wins, 3 in their losses).
- **Relaxing the line-66 gate, or an Ad delivery redirect from a camped HQ:** one game (9484g2), which was an army wipe. c_evac2 failed (net -3).
- **Less Ad mining:** c_ec05, c_ec07 and c_ec08 (abl3) cover it. If c_ec08 (AD_LATE_EVERY=6) helps, try AD_BANK_CAP=100 next. c_mana1 (net -7) and c_adlo2 (REJECTED) are the precedents.

### Reading the running sweeps against this diagnosis
- **c_lb04** (HOT=false) gates change 6. **c_lb05** (MID=false) gates change 5. **c_lb08** (ISLE_THREAT=false) informs change 2.
- **c_lb11/c_lb12** (ARMY on, GROUP_MIN 2/3) settle cohesion.
- **c_ec09** (ANCHOR_START 400) and **c_ec10** (ANCHOR_MIN_LAUNCHERS 20): judge their BatSignal, Hah and ReverseFunnel cells apart from the rest. Both make our first anchor later on the maps where it is already late.
- **c_ec02/c_ec03:** read the BatSignal cells for the one-HQ cap.
- **Gap:** IslandHopping has 3 losses (pranayagra, jmerle, vrangr1), all lost on both panels, and no lens studied it. The jmerle game is the dead-reserve case in section 1.7.
