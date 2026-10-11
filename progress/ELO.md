# Ladder

13630 games (2863 ours, 6 of the stock examplefuncsplayer, 10761 between field bots on the ladder replica), 13291 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 106 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2124 +- 90 | 12 of 105 | 100 | 64-36 | 87.2% | 33.5% (vs 11) |
| c_bc1 | 2097 +- 168 | 13 of 105 | 20 | 7-13 | 86.2% | 30.2% (vs 11) |
| c_spread2 | 2092 +- 89 | 14 of 105 | 100 | 61-39 | 86.0% | 29.7% (vs 11) |
| c_scout1 | 2082 +- 89 | 15 of 105 | 100 | 60-40 | 85.6% | 28.5% (vs 11) |
| c_def3 | 2063 +- 64 | 17 of 105 | 194 | 117-77 | 84.9% | 28.3% (vs 12) |
| c_flee3 | 2040 +- 89 | 18 of 105 | 100 | 56-44 | 84.0% | 25.8% (vs 12) |
| c_anc3 | 2033 +- 69 | 19 of 105 | 161 | 87-74 | 83.7% | 25.1% (vs 12) |
| c_aura2 | 2030 +- 53 | 20 of 105 | 311 | 160-151 | 83.6% | 24.9% (vs 12) |
| c_nav5 | 1974 +- 78 | 23 of 105 | 126 | 61-65 | 81.3% | 23.4% (vs 14) |
| c_nav6 | 1960 +- 77 | 24 of 105 | 129 | 58-71 | 80.7% | 22.1% (vs 14) |
| c_nav4 | 1934 +- 60 | 26 of 105 | 221 | 108-113 | 79.6% | 21.7% (vs 15) |
| c_swarm1 | 1854 +- 56 | 30 of 105 | 268 | 126-142 | 75.9% | 20.4% (vs 18) |
| c_line8a | 1812 +- 78 | 35 of 105 | 139 | 47-92 | 73.9% | 22.7% (vs 22) |
| g_iter0 | 1795 +- 55 | 37 of 105 | 455 | 230-225 | 73.1% | 22.5% (vs 23) |
| c_line6 | 1778 +- 94 | 38 of 105 | 100 | 32-68 | 72.3% | 21.1% (vs 23) |
| c_line7m | 1765 +- 95 | 41 of 105 | 100 | 31-69 | 71.6% | 22.4% (vs 25) |
| c_line5 | 1727 +- 97 | 45 of 105 | 100 | 28-72 | 69.7% | 22.3% (vs 28) |
| c_line4 | 1686 +- 100 | 47 of 105 | 100 | 25-75 | 67.6% | 20.0% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_aura2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2365 | 76 | 169 | 122-47 | 0% (g_iter0 0-35) |
| 2 | awesomelemonade.finalBot | 2357 | 66 | 319 | 260-59 | 20% (c_aura2 2-8*) |
| 3 | maxwelljones14.MPWorking | 2342 | 77 | 157 | 108-49 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2305 | 73 | 173 | 116-57 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2288 | 60 | 341 | 265-76 | 40% (c_aura2 4-6*) |
| 6 | AnOvercookedFork.quals | 2229 | 70 | 184 | 118-66 | 22% (c_aura2 4-14*) |
| 7 | pranayagra.finalbotfinaltwo | 2198 | 67 | 200 | 130-70 | 29% (c_aura2 5-12*) |
| 8 | pranayagra.finalbotfinal | 2188 | 52 | 404 | 278-126 | 36% (c_aura2 9-16*) |
| 9 | georgezhang02.FB_ZZZ | 2186 | 67 | 191 | 121-70 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2150 | 70 | 184 | 116-68 | 33% (c_aura2 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2138 | 51 | 401 | 272-129 | 32% (c_aura2 10-21) |
| 12 | **us:c_well5** | 2124 | 90 | 100 | 64-36 |  |
| 13 | **us:c_bc1** | 2097 | 168 | 20 | 7-13 |  |
| 14 | **us:c_spread2** | 2092 | 89 | 100 | 61-39 |  |
| 15 | **us:c_scout1** | 2082 | 89 | 100 | 60-40 |  |
| 16 | CyrilSharma.finalBot | 2066 | 59 | 247 | 147-100 | 22% (c_aura2 5-18*) |
| 17 | **us:c_def3** | 2063 | 64 | 194 | 117-77 |  |
| 18 | **us:c_flee3** | 2040 | 89 | 100 | 56-44 |  |
| 19 | **us:c_anc3** | 2033 | 69 | 161 | 87-74 |  |
| 20 | **us:c_aura2** | 2030 | 53 | 311 | 160-151 |  |
| 21 | ethanlabelle.dev | 2007 | 58 | 229 | 136-93 | 54% (c_aura2 13-11*) |
| 22 | NotLLeon.v7 | 1983 | 48 | 394 | 224-170 | 68% (c_aura2 17-8*) |
| 23 | **us:c_nav5** | 1974 | 78 | 126 | 61-65 |  |
| 24 | **us:c_nav6** | 1960 | 77 | 129 | 58-71 |  |
| 25 | georgezhang02.CB_tuning2 | 1958 | 48 | 382 | 213-169 | 62% (c_aura2 21-13) |
| 26 | **us:c_nav4** | 1934 | 60 | 221 | 108-113 |  |
| 27 | ethanlabelle.v19 | 1902 | 59 | 214 | 124-90 | 67% (c_aura2 10-5*) |
| 28 | britacatalin.FinalBot | 1893 | 47 | 392 | 201-191 | 73% (c_aura2 16-6*) |
| 29 | GabeG888.v8 | 1859 | 57 | 227 | 121-106 | 89% (c_def3 16-2*) |
| 30 | **us:c_swarm1** | 1854 | 56 | 268 | 126-142 |  |
| 31 | programjames.fourthbot | 1833 | 59 | 218 | 118-100 | 100% (c_aura2 3-0*) |
| 32 | VarunVejalla.karel | 1828 | 57 | 232 | 127-105 | 33% (c_aura2 1-2*) |
| 33 | GabeG888.v8o1 | 1826 | 57 | 222 | 126-96 | 67% (c_aura2 4-2*) |
| 34 | VarunVejalla.ali8 | 1822 | 61 | 207 | 114-93 | 50% (c_aura2 3-3*) |
| 35 | **us:c_line8a** | 1812 | 78 | 139 | 47-92 |  |
| 36 | DannyZhang686.pqual2 | 1800 | 57 | 237 | 127-110 | 83% (c_anc3 5-1*) |
| 37 | **us:g_iter0** | 1795 | 55 | 455 | 230-225 |  |
| 38 | **us:c_line6** | 1778 | 94 | 100 | 32-68 |  |
| 39 | louishu17.louisv10 | 1769 | 59 | 216 | 119-97 | 100% (c_nav4 6-0*) |
| 40 | NicholasKelly15.gopher10 | 1769 | 62 | 196 | 109-87 | 100% (c_anc3 3-0*) |
| 41 | **us:c_line7m** | 1765 | 95 | 100 | 31-69 |  |
| 42 | louishu17.wouisv8 | 1752 | 60 | 224 | 122-102 | 83% (c_aura2 5-1*) |
| 43 | SampleProvider.SPAARK | 1749 | 58 | 222 | 125-97 | 33% (c_anc3 1-2*) |
| 44 | reeceyang.v5anaconda | 1748 | 47 | 401 | 171-230 | 80% (c_aura2 8-2*) |
| 45 | **us:c_line5** | 1727 | 97 | 100 | 28-72 |  |
| 46 | battlecode-archive.Sprint1 | 1693 | 49 | 367 | 141-226 | 100% (c_aura2 10-0*) |
| 47 | **us:c_line4** | 1686 | 100 | 100 | 25-75 |  |
| 48 | ipince.bobby | 1643 | 63 | 188 | 102-86 | 67% (c_swarm1 2-1*) |
| 49 | SteamBlizzard.newVnewME | 1596 | 55 | 249 | 127-122 | 80% (g_iter0 4-1*) |
| 50 | legobridge.tacoplayer | 1588 | 59 | 231 | 121-110 | 85% (g_iter0 11-2*) |
| 51 | TheK098.qp1_7_sprint_1 | 1562 | 57 | 230 | 122-108 | 100% (c_swarm1 6-0*) |
| 52 | polyllc.poly | 1547 | 63 | 199 | 101-98 | 100% (g_iter0 2-0*) |
| 53 | toyat522.bot5a | 1521 | 54 | 247 | 128-119 | 80% (g_iter0 4-1*) |
| 54 | elgoldie.head_v5 | 1504 | 54 | 240 | 118-122 | 100% (g_iter0 2-0*) |
| 55 | DukeBas._main | 1496 | 58 | 221 | 119-102 | 100% (g_iter0 2-0*) |
| 56 | ColtG5.rexv9 | 1480 | 55 | 243 | 121-122 | 100% (g_iter0 2-0*) |
| 57 | beaverbois.USQualifiers | 1451 | 56 | 234 | 121-113 | 50% (g_iter0 1-1*) |
| 58 | Nawlej.PoonPoon | 1420 | 58 | 228 | 118-110 | 100% (g_iter0 2-0*) |
| 59 | kevinli405.maggi3_2 | 1408 | 53 | 270 | 133-137 | 100% (g_iter0 2-0*) |
| 60 | BrysonJGalapon.friday | 1377 | 55 | 229 | 116-113 | 100% (g_iter0 2-0*) |
| 61 | yaonam.PoonPoonv4 | 1370 | 49 | 434 | 150-284 | 90% (c_aura2 9-1*) |
| 62 | nail-e.Barry | 1365 | 54 | 246 | 122-124 | 100% (g_iter0 2-0*) |
| 63 | aj-chau.attempt1 | 1364 | 56 | 242 | 126-116 | 100% (g_iter0 5-0*) |
| 64 | kevinli405.maggi3 | 1355 | 56 | 249 | 129-120 | 100% (g_iter0 5-0*) |
| 65 | prisms-cs-club.prisms10 | 1313 | 56 | 240 | 119-121 | 100% (g_iter0 2-0*) |
| 66 | mama4294.currentPlayer | 1293 | 55 | 252 | 124-128 | 100% (g_iter0 2-0*) |
| 67 | ipince.bobby_v2 | 1262 | 54 | 269 | 132-137 | 67% (c_swarm1 2-1*) |
| 68 | bewuwy.deathbot4 | 1198 | 52 | 307 | 150-157 | 100% (g_iter0 2-0*) |
| 69 | andrewgopher.gopherbot | 1191 | 53 | 286 | 138-148 | 100% (g_iter0 2-0*) |
| 70 | JfeMak.realplayer2 | 1185 | 55 | 254 | 127-127 | 100% (g_iter0 2-0*) |
| 71 | BrysonJGalapon.aloha | 1179 | 53 | 284 | 141-143 | 100% (c_swarm1 3-0*) |
| 72 | PSUtblock.sprint_four_player | 1162 | 56 | 262 | 134-128 | 100% (g_iter0 2-0*) |
| 73 | SampleProvider.SPAARK_1_12_2023 | 1111 | 53 | 301 | 143-158 | 100% (c_swarm1 3-0*) |
| 74 | Nawlej.PoonPoonv3 | 1097 | 53 | 298 | 144-154 | 100% (g_iter0 5-0*) |
| 75 | NolanChai.nolan_1 | 1085 | 52 | 318 | 153-165 | 100% (g_iter0 2-0*) |
| 76 | Juanbri02.matfisplayer1 | 1084 | 54 | 289 | 138-151 | 100% (g_iter0 5-0*) |
| 77 | andrewgopher.gopherbot1 | 1079 | 54 | 294 | 138-156 | 100% (g_iter0 2-0*) |
| 78 | SDainard-PDX.Team_Player | 1074 | 56 | 260 | 125-135 | 100% (g_iter0 2-0*) |
| 79 | jyorkio.elicompbot | 1042 | 55 | 275 | 132-143 | 100% (g_iter0 2-0*) |
| 80 | vontell.regressiongames | 987 | 53 | 306 | 147-159 | 100% (g_iter0 5-0*) |
| 81 | legobridge.kushalplayer | 959 | 60 | 247 | 113-134 | 100% (g_iter0 2-0*) |
| 82 | Patela171.Battlecode2023_Robot | 939 | 56 | 289 | 133-156 | 100% (g_iter0 2-0*) |
| 83 | SteamBlizzard.Block | 938 | 56 | 310 | 139-171 | 100% (g_iter0 5-0*) |
| 84 | ax-95174.MPAction | 915 | 57 | 287 | 132-155 | 100% (c_swarm1 3-0*) |
| 85 | JackLee9355.jackPlayer | 871 | 60 | 280 | 122-158 | 100% (g_iter0 2-0*) |
| 86 | Chahat08.toph | 845 | 58 | 289 | 134-155 | 100% (g_iter0 2-0*) |
| 87 | nail-e.Dante | 844 | 56 | 321 | 154-167 | 100% (g_iter0 2-0*) |
| 88 | michael-tyl.hqrewrite | 840 | 58 | 295 | 139-156 | 100% (g_iter0 2-0*) |
| 89 | mama4294.learningBot | 815 | 60 | 283 | 127-156 | 100% (g_iter0 2-0*) |
| 90 | anicolao.submission | 786 | 58 | 340 | 156-184 | 100% (g_iter0 2-0*) |
| 91 | team-remember-to-hydrate.sprint_1 | 717 | 62 | 295 | 128-167 | 100% (g_iter0 2-0*) |
| 92 | Vinceyou1.Player1 | 643 | 63 | 288 | 124-164 | 100% (g_iter0 2-0*) |
| 93 | addiesteward.elicompbot | 621 | 63 | 311 | 134-177 | 100% (g_iter0 5-0*) |
| 94 | toyat522.bot5 | 615 | 63 | 336 | 154-182 | 100% (g_iter0 2-0*) |
| 95 | michael-tyl.cc_v0_5_0_6 | 603 | 62 | 355 | 153-202 | 100% (g_iter0 2-0*) |
| 96 | Chahat08.lazarus | 573 | 65 | 311 | 140-171 | 100% (g_iter0 2-0*) |
| 97 | monmouth-college-cs.elicompbot | 567 | 63 | 341 | 152-189 | 100% (g_iter0 2-0*) |
| 98 | Swordman51.AdeptusAstartes2 | 561 | 65 | 310 | 136-174 | 100% (g_iter0 2-0*) |
| 99 | anicolao.jumbled | 444 | 69 | 330 | 144-186 | 100% (g_iter0 5-0*) |
| 100 | ShatterXD.SRNNbot | 436 | 70 | 297 | 129-168 | 100% (g_iter0 2-0*) |
| 101 | NotLLeon.player | 228 | 85 | 289 | 130-159 | 100% (g_iter0 2-0*) |
| 102 | CodeClash-ai.mysubmission | 180 | 85 | 331 | 141-190 | 100% (g_iter0 2-0*) |
| 103 | addiesteward.NDeClaw | 152 | 89 | 294 | 122-172 | 100% (g_iter0 5-0*) |
| 104 | Yooncw0223.lec3player | -160 | 104 | 284 | 41-243 | 100% (g_iter0 5-0*) |
| 105 | andrewkbank.First | -227 | 113 | 214 | 26-188 | 100% (g_iter0 2-0*) |
