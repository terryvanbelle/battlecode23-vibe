Findings: awesomelemonade (AL), islands and healing lens

**Data.** "Loss instances" means 25 games: AL anchored in each and we lost. They come from 9478 (c_loose1), 9904 (c_eco3) and the ranked matches. Three ranked games were dropped because they replay panel games exactly: 9702 g0 and g2, and 9703 g1. Island squares come from the engine jar's maps. I ran replaydump --islands on 3 games only: 9904 g0 BatSignal, g5 Hah and g7 MassiveL. Every number below comes from a script in /tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/ (t1, heal, window, fort, zonewin, drain, obj .py; islands.csv; isl_9904_{0,5,7}.txt).

**Verified**

1. **AL anchors early, and always before us when we lose (t1.py, heal.py).**
   - On the c_eco3 panel, AL's first anchor came at r164–366 (median r287, n=7). Ours came at r437–508 (n=6). We never anchored on DefaultMap, Forest, Hah or Maze.
   - AL anchored first in 7 of the 7 games where it anchored, and we lost 6 of them.
   - Across the 25 loss instances, AL anchored first in 20 and by r300 in 12. The other strong bots anchored by r300 in 0 of our 22 losses to them.
   - In 9 of our 13 wins over AL, AL never anchored.
   - c_eco3's ANCHOR_START 400 changed none of our anchor times in losses against c_loose1: BatSignal r487 and MassiveL r499 in both builds. It only moved anchor times in wins (Cat, Cornucopia, IslandHopping: r287–298 became r437–452), plus Forest (r287 became no anchor at all).

2. **Where AL anchors.** In all 3 replay dumps, its first island is the one nearest its HQ:
   - BatSignal island 4, 14.6 tiles from its HQ.
   - Hah island 2, 7.2 tiles.
   - MassiveL island 2, 2.0 tiles.
   - Using the same nearest-island rule, the first island in the level losses sits 2.0–14.6 tiles from its HQ (median 5.8). In the 3 wins where it anchored, it sat 10.6–21.6 tiles away.
   - On Hah (9904), AL's second island at r322 is island 1, **7.2 tiles from our HQ**. It held that island until the game ended at r501 and was never drained.

3. **The fortress effect is real and specific to AL (window.py).** I took games where armies were level when AL anchored (our launchers at least 0.8 of theirs). That is n=7 loss instances on 5 maps: BatSignal, Hah, MassiveL, Cave, PipesAndParabolas. I compared the 150 rounds before AL's first anchor with the 150 rounds after.
   - Our damage per kill went from 197 to 289. Theirs went from 216 to 204.
   - Kills went from 146 vs 130 to 146 vs 217 (ours vs theirs).
   - Level losses to the other strong bots (n=5): ours went from 199 to 201, so no change. AL games we won (n=4): ours went from 197 to 211.

4. **Healing, over whole games (heal.py).**
   - In our losses, AL heals 27.4% of the damage we deal (n=25). In our wins over AL it is 2.2% (n=13). For the other strong bots in our losses it is 9.9% (n=22).
   - Our damage per kill in losses to AL is 325, against 216 in losses to other strong bots. Removing 27.4% healing gives 325 × 0.726 = 236, which closes most of that gap.
   - AL does not heal faster per island-round in losses: 3.48 vs our 5.40. The gap is island holding: 1,972 vs 237 island-rounds per loss.
   - AL uses only standard anchors (it collects no elixir), so each anchor has 250 HP and heals +4 per round.

5. **We do not lose the exchange at AL's island (zonewin.py, fort.py).** Level losses, in the 150 rounds after AL's first anchor:
   - 42 of our 191 launcher deaths (22%) were within r² 36 of that island. The launcher exchange there was 42:38. Elsewhere it was 149:96, which is worse for us.
   - Our deaths had a mean prog of 0.32–0.57, meaning our own half to the middle.
   - Across all 25 losses after AL's first anchor, 50 of 1,100 engagements started within r² 25 of its island. 34 of those 50 started with us behind; only 5 were at par (3 vs 4 launchers, kills 2:2).
   - The one exception is BatSignal, a corridor map with island 4 in the lane: one long fight there cost us 501 damage per kill against its 222.

6. **We never drain its islands (drain.py and the 3 dumps).**
   - In the 25 losses, AL lost 0 islands while we lost 22. The dumps show no AL island ever turned neutral, while our islands did, 3 times.
   - In all 4 wins where AL anchored, we drained it (8 islands in total), but only 1 drain came within 150 rounds of its first anchor (Rectangle, r300).
   - Other strong bots: we drained their islands in 16 of 17 wins and 2 of 22 losses. Draining follows army control, so this is correlation, not cause.

7. **Our launchers rarely aim at enemy islands, against any strong bot (obj.py).**
   - Turns with the enemy-island objective per enemy island-round: 0.12 in AL losses vs 4.32 in AL wins. Other strong bots: 0.12 in losses vs 31.4 in wins.
   - 16 of the 25 AL losses had zero such turns. This confirms the prior "no contest in losses" finding on c_eco3 and ranked play.

**Hypothesis, not verified.** AL's wounded launchers probably walk back to the island near its HQ, heal, and return. That would explain why our damage per kill rises without the fighting moving to the island. Testing it needs per-robot HP and positions from replays, which is beyond the 3-dump budget.

**Counterfactuals (all hypotheses; upper bounds).**

Base: 17 of the 25 loss instances were already behind when AL first anchored (our launchers under 0.8 of theirs, for example Forest 14/40, Maze 14/41, Turtle 1/48, Grievance 0/151). Islands cannot flip those; the army collapsed first. Only the 8 level instances (5 maps) are in play.

- **(a) Never engage within AL's healing range at par: about 0 flips, at most 1 (BatSignal).** Fights there are rare (5 at par) and they are not where we lose the exchange.
- **(b) Drain its first island early: about 1–2 flips.**
  - Each drain needs a lead of several launchers on the island (example: area 13 drains in 11 rounds with a 3-robot lead, 36 rounds with 1).
  - Candidates:
    - BatSignal: about 110 level rounds after r276, island 14.6 tiles from its HQ.
    - Hah: we led 14–15 vs 9–10 for about 70 rounds after r170, island 7.2 tiles from its HQ. The second island, 7.2 tiles from our HQ, also went undrained for 179 rounds.
    - PipesAndParabolas: 20–50 level rounds.
  - On MassiveL and Cave the island is 2 tiles from AL's HQ, so draining it means a siege.
- **(c) Anchor our own island earlier: 0–1 flips (BatSignal).**
  - Cave is the counterexample: we anchored at r284, held 2–3 islands against its 2–3 over r360–480, healed 15,536 against its 14,259, and still lost the army.
  - We anchored first in 5 losses (both Forests, Piglets, Crossword, Pathfind, Grievance) and lost all 5, already behind each time.
  - The only paired evidence is BatSignal on c_hr1/c_isle1: our anchor at r354 beat AL's r392 and we won. AL now anchors there at r276, which c_eco3 cannot reach with ANCHOR_START 400 and blind anchors from r400.
  - On Hah, AL anchors at r164, and holding 1 of 4 islands does not block conquest (3 of 4 is 75%).

**Net.** About 1–3 of the 25 loss instances (4–12%) plausibly flip, concentrated on BatSignal and Hah. The main lever against AL is still army parity through r300; the island fortress mostly turns a level army into a loss on the small maps.