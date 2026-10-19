<!-- Workflow diag-awesomelemonade (2026-10-19 07:45-08:10 PDT): three analysts (fights, army, islands) and a synthesis that re-checked their claims. Scripts in scripts/ (paths in the text point to the session scratchpad; the per-turn dumps they read are not kept: regenerate with tools/replay-dump.sh <replay> --sa --team A|B --game N --match M --out sa/...). Analyst reports: analyst-*.md. Changes built: src/c_kx0 (KILL_STEP switch), c_ks1 (1), c_ks2 (2); sweep abl7. -->

# Diagnosis of our losses to awesomelemonade (AL): verified claims, mechanisms and ranked changes

**Summary**
1. Our step-in shots ignore target HP, and AL exploits this. Of our step-in hits on AL launchers, 27% go to a target 40+ HP healthier than one we could have reached instead; AL's figure is 16%. The gap appears in all 4 dumped AL games. Against the 4 other strong bots (S4) it is 15% vs 14%.
2. AL chains kills within a round: 42% of its kills take 2 or more hits in the kill round, against our 24%. Its kill-rate edge sits on tiles that 2 of our launchers can reach, where our parity hold forbids the step.
3. Of the 19 distinct AL losses, 5 diverge early by fight attrition, 6 by early economy and 8 later from level armies. Of those 8, 4 follow AL's first anchor, which is where the "island fortress" starts.
4. Islands and healing are verified but are a second-order lever (about 1–2 flips). From r300, losses end with our HQ pressed half the time and Ad sitting idle.
5. Ranked changes: (1) `KILL_STEP=1`, (2) `KILL_STEP=2`, (3) `ISLE_MARGIN_SMALL=2`, (4) `AD_PRESS_MN`. Only (3) is an existing constant; (1), (2) and (4) are new constants whose default reproduces c_eco3.

Scripts are in `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/v/`; run each with `python3 -I`. I also re-ran `fights/sa6.py`, `fights/sa7.py`, `window.py` and `heal.py`. I made no new replay dumps.

## 1. Checks of the claims the recommendations rest on

**A. AL finishes wounded launchers when it steps in. Held, exactly, and refined.**
- `sa6.py`: in par windows before r300, the share of step-in hits that kill is 0.157 for AL (n=381) against 0.080 for us (n=513). In the S4 games it is 0.112 for them and 0.115 for us.
- New, `stepsel.py`: a step-in hit where a launcher at 20 HP or less was reachable (r² 26 or less) but a healthier one was hit:

  | Period | Ours | AL | S4 games, ours | S4 games, theirs |
  |---|---|---|---|---|
  | r<300 | 0.059 | 0.046 | 0.025 | 0.030 |
  | r≥300 | 0.040 | 0.019 | — | — |

- New: a target 40+ HP weaker was reachable:

  | Period | Ours | AL | S4 games, ours | S4 games, theirs |
  |---|---|---|---|---|
  | r<300 | 0.27 | 0.16 | 0.15 | 0.14 |
  | r≥300 | 0.21 | 0.07 | 0.16 | 0.12 |

- Per game (`stepsel_pg.py`), ours vs AL: 0.25/0.17, 0.24/0.10, 0.32/0.19 and 0.21/0.11, so we are worse in 4 of 4 games. Against S4 we are worse in 5 of 6 games, but by less.
- New, `focus.py` (par, r<300):
  - AL kills that follow a same-round hit by another AL launcher: 25 of AL's 60 step-in kills, against 10 of our 41.
  - Kills needing 2 or more hits in the kill round: AL 42%, ours 24%. Against S4 we are the focusing side: 38% ours vs 28% theirs.
- New, `opp.py`: when the best kill tile has threat 2, AL converts 6 of 16 chances and we convert 4 of 26. At threat 0–1 we match it (6/41 vs 6/48).
- **Rejected: the fights analyst's H1 (pull our wounded launchers back).** Our launchers at 20 HP or less are less exposed than AL's:
  - within r² 16 of an enemy: 12% of turns vs 28% (`opp.py`);
  - open to an enemy that is ready to step in: 25% vs 42%;
  - moving farther away on their next turn: 39% vs 31% (`sa7.py`).

  AL wins by picking targets, not because ours stand exposed.
- Code cause (Launcher.java:296–321): `fight()` scores tiles by can-hit, then threat, then distance. `killShot` is used only for the HQ-aura exception. The parity rule `threat <= 1 && threat <= threat0` never lets a launcher standing on a zero-threat tile step in on an enemy launcher, even when that launcher is a one-shot kill and the only threat.
- The 2026-10-18 micro diagnosis recorded "target choice: no gap". That holds against the pooled strong field, not against AL.

**B. Army decomposition. Both analysts reproduce exactly; their samples explain the disagreement (`decomp.py`).** Alive gap = production gap + deaths gap.

| Group | Round | Alive gap | Production | Deaths |
|---|---|---|---|---|
| c_eco3 AL losses (n=6) | r200 | −2.5 | −0.3 | −2.2 |
| c_eco3 AL losses (n=6) | r300 | −10.7 | −2.3 | −8.3 |
| c_loose1 panel + ranked AL losses (n=19) | r200 | −4.7 | −1.3 | −3.4 |
| c_loose1 panel + ranked AL losses (n=19) | r250 | −6.6 | −3.3 | −3.3 |
| c_loose1 panel + ranked AL losses (n=19) | r300 | −12.9 | −7.0 | −5.9 |
| S4 losses on c_eco3 (n=10) | r300 | — | −9.8 | +3.5 |

So the deaths gap leads against AL through r250. The "78% attrition" figure holds only for n=6. Against S4 the deaths gap is in our favour at every round.

**C. Island fortress. Held (`window.py`, `heal.py`).**
- Our damage per kill went from 197 before AL's first anchor to 289 after, at level armies (n=7). In level losses to S4 it went from 199 to 201 (n=5).
- AL heals 27.4% of the damage it receives in our losses (n=25), against 9.9% for S4 (n=22).
- AL anchored first in 20 of 25 losses and by r300 in 12; S4 anchored by r300 in 0 of 22.

**D. Late-game HQ starvation. Held and extended (`hqcodes.py`, `press.py`, `adshare.py`).**
- In AL losses, r300–700, the HQ build loop stops on code `t` in 57% of HQ turns: Mn is under 45, Ad is available, and the carrier is held back because the HQ is threatened. The mean bank is 185 Ad. In AL wins it is 2% and 79 Ad; in S4 losses 28%.
- Our HQ is "pressed" (pressure34 ≥ 100) in 51% of r200–700 HQ rows in AL losses, and in 1% of rows in wins against every group.
- Ad share of what we collect in r300–600: 0.36 in AL losses vs AL's 0.21; 0.19 in our wins.

## 2. Mechanisms, in order of games explained

Basis: 19 distinct AL losses, the 6 on the c_eco3 panel plus 13 distinct ranked c_loose1 games (`pergame.py`, `late.py`, `late2.py`).

1. **We convert fight damage into kills worse than AL does (HP-blind step-ins, no same-round chains).**
   - It is the primary cause in the 5 attrition-led losses: DefaultMap (deaths −7 at r200), Maze (−9 at r250), Hah, Piglets 9509 (−8) and Crossword (−5).
   - It also feeds the late losing exchanges in the level games. Our deaths vs theirs per 100 rounds: BatSignal r400–500 19/4, Pipes r600–700 24/9, Cave r700–800 28/9.
   - Upper bound: 13 of 19 games.
2. **Lost from level armies at r250 (8 games).**
   - AL anchored first while armies were level, which is the fortress: BatSignal, MassiveL, Cave, PipesAndParabolas, plus Hah from group 1.
   - In the other 4 the late army and production collapse came before any AL island: Piglets 9514, Lines, Pathfind, Grievance.
   - From r300 AL's Mn per 100 rounds climbs from 575 to 796, while ours stays at 440–500 and then falls (n=7).
3. **Early economy (6 games).**
   - Forest twice (Mn behind from r50).
   - Carrier wipes by r150: ArtistRendition, Turtle, Grapes (10–12 carriers lost each).
   - PairedProgramming.
   - The same production pattern loses to S4, so it is not specific to AL. c_mid3 (already in flight) targets it.
4. **Starved HQ under siege** (pressed 51% of the time, `t` 57%, Ad idle). This follows from groups 1 and 2 rather than causing them, but it speeds the end of the level games.

## 3. Ranked changes

**1. `KILL_STEP = 1`** (new `int` in C.java; 0 = c_eco3). All edits are in `fight()` in src/c_eco3/Launcher.java:
- **Line 297:** declare a per-tile `boolean killF` with no initializer. Assign it only inside `C.KILL_STEP > 0` guards, so that KILL_STEP=0 compiles to classes byte-identical to c_eco3. Check with a `javap -c -p` diff.
- **Line 302 (`case 1`):** set `killF = true` when `dd <= 16 && kill[i]`.
- **After the enemy loop (before line 306):** add `if (C.KILL_STEP > 0 && ready && killF) threat--;`. The launcher we kill cannot answer, so the parity test at 320 and both scores use the discounted threat.
- **Line 315 (ahead branch) and line 321 (parity firing score):** add `+5_000` when `killF`. This sits below one threat (10,000) and above the edge-of-range term (at most 1,000).
- Mending and the not-ready scoring are unchanged.

Expected results:
- In new sa dumps against AL (`stepsel.py`): the reachable-kill-missed share falls from 0.06 to 0.03 or less, and the step-in kill share rises from 0.08 to 0.12 or more.
- `focus.py`: same-round chain kills rise from about 10 to about 20 per 4 games.
- `opp.py`: conversion at threat-2 kill tiles rises from 0.15 to about 0.35.
- `decomp.py`: the deaths gap at r250 in AL losses (−4.0) moves toward 0.

Games to flip: 9904 g3 DefaultMap and g8 Maze; in ranked play, Piglets 9509 and Crossword. Expect +1 to +2 on the panel.

Risk:
- A launcher at par can now step onto a tile that 2 enemies reach. The kill flag uses health sensed this turn, so the error rate is small.
- Wins against S4 and the weaker bots are production wins, with a par exchange of 1.19, so the risk to them is low.
- The broader HP-simulation micro c_sim1 failed head-to-head, 5/20. This change is much narrower.
- Unlike the island levers, this is micro against our own HP-blind targeting, so a local head-to-head against c_eco3 means something here.

**2. `KILL_STEP = 2`:** change 1 plus focus on the lowest-HP enemy.
- **Line 269:** also store `eh[n] = e.health`, into an array allocated only under the guard.
- **Per tile:** compute `minHpF`, the lowest HP of an enemy fighter within r² 16 of the tile.
- **Firing tiles:** add `(200 - minHpF) * 20` (at most 3,980). The total of kill bonus, focus and edge term stays under 10,000, so threat still dominates.

Expected results: the "40+ weaker reachable" share falls from 0.27 to 0.16 or less against AL and from 0.15 to about 0.10 against S4; the mean HP of our step-in targets falls from 115 to about 105.

Flips: the same games as change 1, plus small gains against S4, where the 2-hit focus gap still exists.

Risk: preferring focus over edge-of-range puts launchers one tile deeper in a fight. Bytecode: one int array plus 2 operations per fighter per tile, covered by `FIGHT_GUARD`.

**3. `ISLE_MARGIN_SMALL=2`** (one-knob cell on c_ex0).
- Effect: on 4-island maps, even-id launchers start draining after the enemy's first island instead of its second; on 5-island maps after the second.
- Scope: on the c_eco3 panel this moves the trigger earlier in 10 of 30 games on 4-island maps (`isle4.py`). It does not touch the large-map fortresses (MassiveL, Cave, Pipes).
- Expected results: `obj.py` enemy-island turns go above 0 in Hah and BatSignal; `drain.py` shows AL losing an island before r400; `window.py` damage per kill after AL's anchor falls from 289 toward 200.
- Flips:
  - 9904 g5 Hah: AL's island arrives at r170 while we lead 14/10, 160 rounds before its second island.
  - 9904 g0 BatSignal: r280 at 11/9, 220 rounds earlier.
  - Possibly 9901 g5.
- Risk: wins where the trigger now fires at par or behind: 9904 g9 ReverseFunnel (AL, 18/18 at r290) and 9902 g9 (jmerle, 20/26). Expected net 0 to +2.

**4. `AD_PRESS_MN`** (new `boolean`, default false).
- **Carrier.java:173:** the late Ad role becomes `G.round >= C.AD_ROLE_FROM && G.id % C.AD_LATE_EVERY == 0 && !(C.AD_PRESS_MN && Comms.pressed(Comms.hqIndex(HQState.nearest(G.here))))`.
- **Comms.java:** add `pressed(hq)`, which reads bit `PRESS_SHIFT + hq` of `AD_FLAGS`.
- Reason: Mn buys launchers even when the HQ is threatened; Ad does not.
- Expected results: `hq.csv` Ad bank in AL losses r300–700 falls from 185 to 100 or less; the Ad share in `adshare.py` falls from 0.36 to 0.25 or less; about +100–200 Mn per game over r300–600.
- Flips: none on its own. It may keep the 4 level fortress games level for longer.
- Risk: our HQ is pressed in 1% of rows in wins, so the risk to wins is close to zero.

The panel decides all four; self-play can only screen changes 1 and 2.

**Caveats:**
- The per-turn evidence comes from 4 AL games (2 on c_loose1, 2 on c_hr1) and 6 S4 games.
- Reachability ignores walls.
- An alternative target's HP is read at the start of its own turn, so damage taken earlier in the same round is missed in either direction. This error is the same for both sides.
- The 9904 and 9478 games are largely identical, so the effective sample is smaller than the counts suggest.