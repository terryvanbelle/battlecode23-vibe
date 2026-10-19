**Army trajectory vs awesomelemonade: the gap is attrition first, production second**

All numbers come from timeline, hq, deaths and games.csv. The scripts are in `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/diag-al/` (agg.py, onset.py, front.py, eff.py, eff2.py, cdeath.py, fights.py, traj.py). "Lost" means built_L minus alive_L. Each gap reads ours minus theirs: built gap minus lost gap.

Groups:
- **AL-P**: the 6 losses in 9904. 9478 replicates them within 1 launcher.
- **AL-W**: the 4 wins in 9904.
- **AL-R**: ranked c_loose1, 15 losses and 6 wins. Grievance appears in both 9702 and 9703. Forest and ReverseFunnel in 9702 nearly match 9904.
- **S3**: jmerle, vrangr1 and pranayagra on c_eco3 (9901, 9902, 9905), 9 losses and 21 wins.

**Verified**

1. **Against awesomelemonade the launcher gap comes mostly from attrition until r300. Against the other strong bots it comes from production.** (agg.py)
   - AL-P alive gap:
     - r200: -2.5 = -0.3 built, +2.2 lost.
     - r250: -5.3 = -1.3, +4.0.
     - r300: -10.7 = -2.3, +8.3 (78% attrition).
     - r400: -30.0 = -13.0, +17.0.
   - AL-R: r250 -7.1 = -3.5, +3.5; r300 -13.1 = -7.9, +5.1.
   - S3 losses: r300 -7.1 = -10.7 built, -3.6 lost. There we lose fewer launchers than they do.
   - Per game, taking the onset as the first round the gap reaches 5 (onset.py):
     - Against awesomelemonade: 15 attrition-led, 5 production-led (n=20, median onset r155). The production-led ones are Forest (twice, with Mn behind from r50, 116 vs 266), Maze and Piglets 9514 (both near ties).
     - Against S3: 3 attrition-led, 5 production-led (n=8, median r220).
   - The three examples you named, at r250:
     - DefaultMap: -11 = -4 built, +7 lost.
     - Maze: -13 = -4, +9.
     - Forest: -10 = -10, 0.

2. **When it opens.**
   - Launchers lost per 50 rounds in AL-P, ours vs theirs: level to r150 (9.3/8.2, 9.2/10.5). After that we lose 2 to 4 more per window: 10.5/8.2, 10.7/8.8, 11.7/7.3, then 21.5/12.8 in r300-400.
   - Builds per 50 rounds stay level up to r300: ours 9.8-11.3, theirs 10.0-12.2. The build gap appears only in r300-400, at 16.8 vs 27.5.

3. **Mn is a lagging, second-stage cause.**
   - Mn collected is level at r100 (530/548). After that our rate runs 19-37% lower: 316/390, 336/387, 335/431 and 312/498 per 50 rounds.
   - By r300 awesomelemonade has collected 424 more Mn but has built only 2.3 more launchers (104 Mn), and holds 67 more Mn in the bank. The surplus turns into launchers in r300-400.
   - The r250-300 Mn gap splits into 47% fewer carriers (17.1 vs 20.7 alive) and 53% less Mn per carrier-round (0.365 vs 0.480). Part of the second is Ad mining: Ad is 22% of what our carriers collect vs 11% of theirs.

4. **The front sits in our third from r100, about 150 rounds earlier than against the other bots.** (front.py; prog converted to our frame)
   - Share of launcher deaths at prog<0.33 in r100-150:
     - AL-P: 52% (118 deaths, median 0.32).
     - AL-R: 54% (189 deaths, median 0.30).
     - Our wins: 23% (AL-W) and 16% (ranked wins).
     - S3 losses: 21% (median 0.46). Those only reach 37% by r250-300.
   - It depends on the map:
     - Forest: 0.14-0.28 throughout.
     - Hah: 0.24 in r100-150.
     - MassiveL: about 0.25 from r150.
     - Maze: 0.28 then 0.23, from r200.
   - DefaultMap is the exception (0.60-0.65): there we lose the fights in its half.

5. **HQ pressure, idle Ad and carriers.**
   - Our HQs are pressured (enemies within r² 34) in 27-37% of 25-round buckets during r100-300, against 13-23% for its HQs.
   - HQ code `t` (threatened: Ad was there for a carrier but it was held back) covers 15-24% of HQ turns (17-28% in ranked). Against S3 losses it is 4-7%.
   - We float Ad: 152 and 213 at r200 and r300 vs its 81 and 71 (ranked: 135 and 221 vs 89 and 66). In our wins it is 72-128.
   - Even so, we build as many carriers as awesomelemonade (3.2-3.7 per 50 rounds each side). At r300 we have 16.7 carriers alive to its 21.7; 72% of that gap is carrier deaths (12.2 vs 8.6 lost; 3.7 vs 1.3 in r250-300).
   - 89% of our carriers lost by r150 die in our own third (4.0 of 4.5 per game); against S3 it is 62%.

6. **Per-launcher output is level. Turning damage into kills is not.** (eff.py, eff2.py)
   - Damage per launcher-round: 2.95/2.96 in r100-200 and 2.92/2.60 in r200-300.
   - Damage per kill in r200-300: 222 ours vs 192 theirs.
   - Hah, after its r164 anchor: 377 and 359 vs 193 and 199. This is the fortress effect from the earlier diagnosis.
   - DefaultMap r150-200: 213 vs 172, before its first anchor at r233.

7. **Our wins against it are production wins.**
   - Mn at r100: 526/343 (panel) and 562/424 (ranked).
   - By r250: built +8.2, lost -3.8.
   - Its carriers die: ranked wins, r100-150, 5.0 per game vs our 0.3. The front sits in its half (median 0.68).

8. **Amplifiers play no part.** Neither side has any alive in any awesomelemonade window. S3 keeps 0.6-1.6 alive.

9. **Three ranked losses are early carrier wipes:** Turtle (9511), Grapes (9701) and ArtistRendition (9509).
   - 11-12 of our carriers die by r150 (mean round 68-92).
   - 9-12 of those deaths are in our own third.
   - On Turtle we collected 0 Mn by r300.

**Hypotheses (not verified)**

- **H1. Its first push pins the fight in our third from r100-150.** Our launchers would then join one at a time and trade worse, and our home miners would lose working cycles, which is the Mn-per-carrier gap. To test: compare joinA vs joinB and nA0 vs nB0 in engagements at prog<0.33 in r100-200, or replaydump 9904 g3 and g8.
- **H2. The `t` rule leaves about 100-150 Ad idle.** A threatened HQ that cannot afford a launcher may build nothing at all. To test: count `t` turns with Mn<45. A fix would let it build a carrier anyway.
- **H3. The other ~250 Mn of its r300 surplus went into anchors (80 Mn each) and cargo.** Anchors built per round are not in timeline.csv, so I could not check this.

**Bottom line:** against awesomelemonade the gap is attrition first, from about r150. Fights move into our third early, and from r200 its island healing lowers our kill rate. Production follows from r300, when the Mn gap that started at r100 turns into launchers. Against jmerle, vrangr1 and pranayagra it is production from the start.