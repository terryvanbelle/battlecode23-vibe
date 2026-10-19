Findings: launcher FIGHTS against awesomelemonade (AL)

**Scope and method.** Scripts are in `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/fights/`; run each with `python3 -I <script>`. CSV scripts are a1–a11, per-turn scripts sa1–sa7.
- **AL sample:** 9478 plus the 7 ranked c_loose1 matches, 28 unique games (19 losses, 9 wins). Three ranked games repeat an earlier game exactly: 9702g0 = 9478g4, 9702g2 = 9478g9, 9703g1 = 9702g1. I removed them where noted.
- **S4 sample:** jmerle, vrangr1, pranayagra and NotLLeon from the same c_loose1 panel (9476, 9475, 9479, 9480): 40 games on the same 10 maps as 9478.
- **Replay dumps (3 games):** 9478 g8 Maze (AL), 9478 g5 Hah (AL) and 9476 g8 Maze (jmerle), made with `tools/replay-dump.sh <replay> --sa --team A|B --game N --match M --out sa/...`. I also reused existing c_hr1 per-turn dumps in `scratchpad/micro/sa`: 8826 g5 Hah and g7 MassiveL (AL), and 8823g4, 8824g8, 8827g0, 8827g9 and 8828g1 (S4).

**VERIFIED**

1. **"6 of 21 par fights" is an artefact of how fights are clustered.**
   - The 21 dN 0 rows in the 9904 losses are: 3 carrier throws with no launchers, 5 draws with no kill, 6 won and 7 lost. 14 of them never have more than 2 launchers per side.
   - They hold 20 of our 865 launcher deaths (2%). 57% of our deaths sit in engagements lasting 100 rounds or more (DefaultMap's runs r4–316), so dN at the start describes only the first skirmish.
   - Before r300 in AL losses we win the par engagements 21–16, with equal reinforcements (119 vs 119). (a5_eng.py)

2. **A better unit: 10-round windows at equal army size (alive launchers within a ratio of 0.8–1.25).** "Exchange" below is their launcher deaths divided by ours.
   - Before r300 vs AL: exchange 0.89, 95% CI 0.83–0.96 (resampled by game), over 449 windows with deaths 516 ours vs 458 theirs.
   - Before r300 vs S4: exchange 1.19, CI 1.07–1.32, over 455 windows.
   - On the same 10 panel maps only: 0.91 vs 1.19.
   - By S4 bot: jmerle 1.30, vrangr1 1.16, NotLLeon 1.29, pranayagra 1.02.
   - Even in our AL wins the par exchange is only 0.96 (CI 0.82–1.29). We win those games on production: launchers built by r300 61.0 vs 38.8 (n=9). (a1_windows.py, a2_decomp.py)

3. **The fight deficit costs us games against AL, and not against the other strong bots.** The army gap splits into deaths and production:

   | Losses | Round | Alive (ours vs theirs) | Gap from deaths | Gap from production |
   |---|---|---|---|---|
   | AL (n=19) | r200 | 12.2 vs 16.9 | −3.4 | −1.3 |
   | AL (n=19) | r300 | — | −5.9 | −7.0 |
   | S4 (n=12) | r300 | — | +2.5 (in our favour) | −10.8 |

   (a11_r300.py)

4. **Healing does not explain the deficit before r300 (it does after).**
   - AL holds an island in only 19 of 386 early par windows. The exchange is 0.74 in those and 0.91 in the rest, against 1.19 for S4.
   - Only 5–6% of our early par deaths are within r² 4 of an island while AL holds one. After r300 it is 14–17%, which is the known island fortress.
   - Exception, Hah 9478g5: AL healed 2,408 HP before r300. Launcher-on-launcher damage per AL death there is 304, against 215 per our death.
   - (a9_isl.py, a3_deaths.py, sa1.py)

5. **Not their HQ, and not shots from clouds.**
   - 9% of our early par deaths are within r² 34 of AL's HQ (S4: 8%).
   - 14% of our deaths are on clouds (S4: 6%), but the attacker stands on a cloud for only 1% of AL's hits (S4: 5%).
   - AL fires 664–1,778 shots per game that hit nothing on the cloud maps; none land.

6. **First hit and reinforcements.**
   - AL hits first in 139 of 230 decisive fights before r300 in our losses (60%; S4 losses 57%).
   - 29% of AL's first hits come from a launcher that did not move (S4: 17%), and the pair was already in range at the start of the round 33% of the time (S4: 18%).
   - We win only 27% of the fights AL opens (S4: 43%).
   - Reinforcements run 1.14 launchers per engagement in AL's favour (S4 losses: 0.30). This follows the global army: in AL losses we are behind in 33% of early windows (S4: 25%), and when behind the exchange is 0.86 (S4: 1.15).

7. **Our telemetry at death (early par windows).** Compared across AL losses (n=406), S4 losses (n=275) and AL wins (n=110):

   | Our state at death | AL losses | S4 losses | AL wins |
   |---|---|---|---|
   | Marching (M) | 21% | 14% | 8% |
   | "Outnumbered" flag | 20% | 10% | 14% |

   - The objective mix is the same against AL and S4: sighting 50% vs 53%, mid squad 11% vs 14%, siege/raid 35% vs 30%. Objective kind does not single out AL.
   - (a4_codes.py, a10_obj.py)

8. **Main mechanism in the per-turn data: AL steps in to finish wounded launchers.** Early par windows, 4 AL games against 6 S4 games:
   - Hits are equal (1,236 ours vs 1,247 AL's), but kills are 88 vs 118.
   - **Shots without moving:** both sides hit the lowest-HP enemy in range almost every time, and kill with 0.065 vs 0.067 of them.
   - **Shots after moving into range:** AL's land on a launcher at 20 HP or less 0.157 of the time (n=381), ours 0.080 (n=513). It holds in every AL game (0.11–0.17 vs 0.05–0.09). Against S4 the rates are 0.112 vs 0.115.
   - At our rate AL would have about 30 fewer such kills, which is the whole 30-kill gap.
   - Our launchers killed this way had no enemy in range on their last turn 78% of the time, and 24% were marching (S4: 13%).
   - Our launchers at 40 HP or less die within 10 rounds 89% of the time (AL's 73%; S4 83% ours vs 88% theirs).
   - (sa1–sa7.py)

9. **Maze also shows a concentration gap, but it is specific to that map.**
   - Vs AL on Maze (9478g8): we are outnumbered on 22% of our in-range turns vs 8% for AL. At each hit, our local lead is +0.43 launchers against AL's +1.23.
   - Vs jmerle on the same map (9476g8) it reverses: 8% vs 16%, and +2.07 vs +0.66.
   - On Hah we had the local lead (+8.1 vs +4.0) and still lost the kills.

**HYPOTHESES (not verified)**

- **H1, wounded launchers left in reach.** AL picks launchers at 20 HP or less when it steps in. Ours stay within reach on march or sighting objectives, because nothing pulls a wounded launcher back while we own no island. Test: back off launchers at 40 HP or less to more than r² 34 from the nearest enemy, then check that the step-in kill rate drops toward 0.08.
- **H2, AL waits in place.** AL holds still and we walk into range. That fits the first hits from launchers that did not move and our marching deaths.
- **H3, concentration on Maze.** This is a positioning effect specific to the map, not a general cause.

**Caveats**
- The per-turn dumps cover 10 games: c_hr1 for the older ones, c_loose1 for the new ones.
- The timeline's damage counts include hits on carriers, so I only use it for comparisons. The launcher-on-launcher numbers come from the per-turn rows.
- The CIs in item 2 include the 3 repeated games; with them removed the result is 0.90.