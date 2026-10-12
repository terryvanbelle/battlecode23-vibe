# Ladder

15708 games (3390 ours, 6 of the stock examplefuncsplayer, 12312 between field bots on the ladder replica), 15421 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 109 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2103 +- 89 | 12 of 108 | 100 | 64-36 | 87.2% | 33.7% (vs 11) |
| c_spread2 | 2071 +- 88 | 13 of 108 | 100 | 61-39 | 86.0% | 29.9% (vs 11) |
| c_scout1 | 2061 +- 88 | 14 of 108 | 100 | 60-40 | 85.6% | 28.7% (vs 11) |
| c_well7 | 2061 +- 88 | 15 of 108 | 100 | 60-40 | 85.6% | 28.7% (vs 11) |
| c_mend2 | 2054 +- 66 | 16 of 108 | 178 | 114-64 | 85.4% | 27.9% (vs 11) |
| c_bc1 | 2046 +- 68 | 17 of 108 | 164 | 97-67 | 85.1% | 27.1% (vs 11) |
| c_def3 | 2039 +- 62 | 19 of 108 | 199 | 120-79 | 84.8% | 28.2% (vs 12) |
| c_end2 | 2030 +- 88 | 20 of 108 | 100 | 57-43 | 84.4% | 27.2% (vs 12) |
| c_flee3 | 2019 +- 88 | 21 of 108 | 100 | 56-44 | 84.0% | 26.1% (vs 12) |
| c_anc3 | 2012 +- 68 | 22 of 108 | 163 | 88-75 | 83.7% | 25.3% (vs 12) |
| c_aura2 | 2011 +- 52 | 23 of 108 | 314 | 162-152 | 83.7% | 25.2% (vs 12) |
| c_nav5 | 1954 +- 77 | 26 of 108 | 126 | 61-65 | 81.3% | 23.7% (vs 14) |
| c_nav6 | 1938 +- 76 | 28 of 108 | 129 | 58-71 | 80.7% | 24.1% (vs 15) |
| c_nav4 | 1916 +- 59 | 29 of 108 | 221 | 108-113 | 79.7% | 22.0% (vs 15) |
| c_swarm1 | 1838 +- 55 | 32 of 108 | 271 | 128-143 | 76.1% | 19.2% (vs 17) |
| c_line8a | 1795 +- 77 | 38 of 108 | 139 | 47-92 | 74.1% | 22.9% (vs 22) |
| g_iter0 | 1775 +- 54 | 40 of 108 | 456 | 230-226 | 73.1% | 22.4% (vs 23) |
| c_line6 | 1760 +- 93 | 41 of 108 | 100 | 32-68 | 72.4% | 21.2% (vs 23) |
| c_line7m | 1748 +- 94 | 44 of 108 | 100 | 31-69 | 71.8% | 22.5% (vs 25) |
| c_line5 | 1710 +- 96 | 48 of 108 | 100 | 28-72 | 69.9% | 22.3% (vs 28) |
| c_line4 | 1669 +- 99 | 50 of 108 | 100 | 25-75 | 67.9% | 20.0% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_mend2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2324 | 73 | 171 | 119-52 | 0% (g_iter0 0-5*) |
| 2 | awesomelemonade.finalBot | 2321 | 59 | 376 | 300-76 | 20% (c_mend2 2-8*) |
| 3 | IvanGeffner.fortytwo | 2318 | 71 | 182 | 125-57 | 0% (g_iter0 0-36) |
| 4 | carlguo866.submit26_final | 2295 | 69 | 187 | 126-61 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2272 | 56 | 386 | 298-88 | 40% (c_mend2 4-6*) |
| 6 | AnOvercookedFork.quals | 2209 | 66 | 205 | 134-71 | 33% (c_bc1 1-2*) |
| 7 | pranayagra.finalbotfinaltwo | 2174 | 64 | 213 | 137-76 | 29% (c_aura2 5-12*) |
| 8 | pranayagra.finalbotfinal | 2169 | 48 | 463 | 313-150 | 30% (c_mend2 3-7*) |
| 9 | georgezhang02.FB_ZZZ | 2154 | 63 | 206 | 125-81 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2133 | 66 | 202 | 128-74 | 22% (c_bc1 2-7*) |
| 11 | jmerle.camel_case_v30_final | 2119 | 48 | 446 | 298-148 | 40% (c_mend2 4-6*) |
| 12 | **us:c_well5** | 2103 | 89 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2071 | 88 | 100 | 61-39 |  |
| 14 | **us:c_scout1** | 2061 | 88 | 100 | 60-40 |  |
| 15 | **us:c_well7** | 2061 | 88 | 100 | 60-40 |  |
| 16 | **us:c_mend2** | 2054 | 66 | 178 | 114-64 |  |
| 17 | **us:c_bc1** | 2046 | 68 | 164 | 97-67 |  |
| 18 | CyrilSharma.finalBot | 2045 | 57 | 260 | 152-108 | 22% (c_aura2 5-18*) |
| 19 | **us:c_def3** | 2039 | 62 | 199 | 120-79 |  |
| 20 | **us:c_end2** | 2030 | 88 | 100 | 57-43 |  |
| 21 | **us:c_flee3** | 2019 | 88 | 100 | 56-44 |  |
| 22 | **us:c_anc3** | 2012 | 68 | 163 | 88-75 |  |
| 23 | **us:c_aura2** | 2011 | 52 | 314 | 162-152 |  |
| 24 | ethanlabelle.dev | 1989 | 54 | 269 | 154-115 | 50% (c_mend2 3-3*) |
| 25 | NotLLeon.v7 | 1955 | 44 | 490 | 256-234 | 70% (c_mend2 19-8*) |
| 26 | **us:c_nav5** | 1954 | 77 | 126 | 61-65 |  |
| 27 | georgezhang02.CB_tuning2 | 1944 | 45 | 457 | 247-210 | 58% (c_mend2 15-11*) |
| 28 | **us:c_nav6** | 1938 | 76 | 129 | 58-71 |  |
| 29 | **us:c_nav4** | 1916 | 59 | 221 | 108-113 |  |
| 30 | ethanlabelle.v19 | 1879 | 54 | 263 | 139-124 | 94% (c_mend2 17-1*) |
| 31 | britacatalin.FinalBot | 1865 | 44 | 462 | 222-240 | 80% (c_mend2 8-2*) |
| 32 | **us:c_swarm1** | 1838 | 55 | 271 | 128-143 |  |
| 33 | GabeG888.v8 | 1833 | 54 | 249 | 133-116 | 89% (c_def3 16-2*) |
| 34 | VarunVejalla.karel | 1823 | 54 | 265 | 141-124 | 56% (c_mend2 10-8*) |
| 35 | GabeG888.v8o1 | 1820 | 54 | 246 | 142-104 | 67% (c_aura2 4-2*) |
| 36 | programjames.fourthbot | 1819 | 57 | 237 | 130-107 | 67% (c_mend2 2-1*) |
| 37 | VarunVejalla.ali8 | 1808 | 57 | 235 | 130-105 | 50% (c_aura2 3-3*) |
| 38 | **us:c_line8a** | 1795 | 77 | 139 | 47-92 |  |
| 39 | DannyZhang686.pqual2 | 1778 | 53 | 273 | 148-125 | 83% (c_anc3 5-1*) |
| 40 | **us:g_iter0** | 1775 | 54 | 456 | 230-226 |  |
| 41 | **us:c_line6** | 1760 | 93 | 100 | 32-68 |  |
| 42 | louishu17.louisv10 | 1757 | 56 | 237 | 129-108 | 100% (c_bc1 3-0*) |
| 43 | NicholasKelly15.gopher10 | 1753 | 59 | 214 | 119-95 | 100% (c_anc3 3-0*) |
| 44 | **us:c_line7m** | 1748 | 94 | 100 | 31-69 |  |
| 45 | louishu17.wouisv8 | 1738 | 56 | 257 | 140-117 | 83% (c_aura2 5-1*) |
| 46 | reeceyang.v5anaconda | 1733 | 44 | 477 | 195-282 | 90% (c_mend2 9-1*) |
| 47 | SampleProvider.SPAARK | 1727 | 56 | 234 | 129-105 | 33% (c_anc3 1-2*) |
| 48 | **us:c_line5** | 1710 | 96 | 100 | 28-72 |  |
| 49 | battlecode-archive.Sprint1 | 1689 | 45 | 436 | 169-267 | 90% (c_mend2 9-1*) |
| 50 | **us:c_line4** | 1669 | 99 | 100 | 25-75 |  |
| 51 | ipince.bobby | 1615 | 58 | 221 | 117-104 | 67% (c_swarm1 2-1*) |
| 52 | SteamBlizzard.newVnewME | 1571 | 53 | 269 | 137-132 | 80% (g_iter0 4-1*) |
| 53 | legobridge.tacoplayer | 1568 | 55 | 261 | 138-123 | 85% (g_iter0 11-2*) |
| 54 | TheK098.qp1_7_sprint_1 | 1545 | 54 | 262 | 143-119 | 100% (c_swarm1 6-0*) |
| 55 | polyllc.poly | 1535 | 59 | 224 | 116-108 | 100% (g_iter0 2-0*) |
| 56 | toyat522.bot5a | 1483 | 51 | 281 | 141-140 | 80% (g_iter0 4-1*) |
| 57 | elgoldie.head_v5 | 1477 | 51 | 268 | 133-135 | 100% (g_iter0 2-0*) |
| 58 | ColtG5.rexv9 | 1464 | 52 | 274 | 139-135 | 100% (g_iter0 2-0*) |
| 59 | DukeBas._main | 1460 | 55 | 251 | 132-119 | 100% (g_iter0 2-0*) |
| 60 | beaverbois.USQualifiers | 1430 | 53 | 267 | 140-127 | 50% (g_iter0 1-1*) |
| 61 | kevinli405.maggi3_2 | 1392 | 50 | 313 | 158-155 | 100% (g_iter0 2-0*) |
| 62 | Nawlej.PoonPoon | 1389 | 55 | 258 | 127-131 | 100% (g_iter0 2-0*) |
| 63 | yaonam.PoonPoonv4 | 1356 | 46 | 512 | 176-336 | 90% (c_mend2 9-1*) |
| 64 | BrysonJGalapon.friday | 1354 | 52 | 264 | 136-128 | 100% (g_iter0 2-0*) |
| 65 | nail-e.Barry | 1329 | 51 | 288 | 145-143 | 100% (g_iter0 2-0*) |
| 66 | aj-chau.attempt1 | 1322 | 52 | 281 | 144-137 | 100% (g_iter0 5-0*) |
| 67 | kevinli405.maggi3 | 1317 | 52 | 285 | 145-140 | 100% (g_iter0 5-0*) |
| 68 | prisms-cs-club.prisms10 | 1278 | 53 | 270 | 132-138 | 100% (g_iter0 2-0*) |
| 69 | mama4294.currentPlayer | 1265 | 52 | 286 | 142-144 | 100% (g_iter0 2-0*) |
| 70 | ipince.bobby_v2 | 1244 | 50 | 318 | 157-161 | 67% (c_swarm1 2-1*) |
| 71 | bewuwy.deathbot4 | 1156 | 49 | 346 | 165-181 | 100% (g_iter0 2-0*) |
| 72 | JfeMak.realplayer2 | 1153 | 51 | 309 | 151-158 | 100% (g_iter0 2-0*) |
| 73 | andrewgopher.gopherbot | 1150 | 51 | 325 | 158-167 | 100% (g_iter0 2-0*) |
| 74 | BrysonJGalapon.aloha | 1149 | 49 | 342 | 168-174 | 100% (c_swarm1 3-0*) |
| 75 | PSUtblock.sprint_four_player | 1113 | 52 | 317 | 158-159 | 100% (g_iter0 2-0*) |
| 76 | SampleProvider.SPAARK_1_12_2023 | 1066 | 50 | 343 | 163-180 | 100% (c_swarm1 3-0*) |
| 77 | NolanChai.nolan_1 | 1046 | 49 | 361 | 177-184 | 100% (g_iter0 2-0*) |
| 78 | SDainard-PDX.Team_Player | 1044 | 53 | 306 | 150-156 | 100% (g_iter0 2-0*) |
| 79 | Nawlej.PoonPoonv3 | 1044 | 51 | 337 | 160-177 | 100% (g_iter0 5-0*) |
| 80 | Juanbri02.matfisplayer1 | 1040 | 50 | 344 | 167-177 | 100% (g_iter0 5-0*) |
| 81 | andrewgopher.gopherbot1 | 1031 | 53 | 315 | 146-169 | 100% (g_iter0 2-0*) |
| 82 | jyorkio.elicompbot | 1006 | 51 | 331 | 160-171 | 100% (g_iter0 2-0*) |
| 83 | vontell.regressiongames | 939 | 51 | 361 | 178-183 | 100% (g_iter0 5-0*) |
| 84 | legobridge.kushalplayer | 920 | 55 | 298 | 138-160 | 100% (g_iter0 2-0*) |
| 85 | SteamBlizzard.Block | 890 | 53 | 357 | 163-194 | 100% (g_iter0 5-0*) |
| 86 | Patela171.Battlecode2023_Robot | 881 | 54 | 339 | 157-182 | 100% (g_iter0 2-0*) |
| 87 | ax-95174.MPAction | 851 | 53 | 351 | 164-187 | 100% (c_swarm1 3-0*) |
| 88 | nail-e.Dante | 798 | 54 | 365 | 178-187 | 100% (g_iter0 2-0*) |
| 89 | JackLee9355.jackPlayer | 793 | 58 | 327 | 146-181 | 100% (g_iter0 2-0*) |
| 90 | Chahat08.toph | 789 | 55 | 352 | 165-187 | 100% (g_iter0 2-0*) |
| 91 | michael-tyl.hqrewrite | 765 | 55 | 347 | 162-185 | 100% (g_iter0 2-0*) |
| 92 | mama4294.learningBot | 764 | 55 | 364 | 167-197 | 100% (g_iter0 2-0*) |
| 93 | anicolao.submission | 719 | 55 | 391 | 180-211 | 100% (g_iter0 2-0*) |
| 94 | team-remember-to-hydrate.sprint_1 | 680 | 58 | 341 | 152-189 | 100% (g_iter0 2-0*) |
| 95 | toyat522.bot5 | 591 | 58 | 396 | 178-218 | 100% (g_iter0 2-0*) |
| 96 | addiesteward.elicompbot | 580 | 59 | 378 | 169-209 | 100% (g_iter0 5-0*) |
| 97 | Vinceyou1.Player1 | 578 | 60 | 338 | 148-190 | 100% (g_iter0 2-0*) |
| 98 | michael-tyl.cc_v0_5_0_6 | 561 | 58 | 418 | 186-232 | 100% (g_iter0 2-0*) |
| 99 | Chahat08.lazarus | 541 | 60 | 379 | 176-203 | 100% (g_iter0 2-0*) |
| 100 | Swordman51.AdeptusAstartes2 | 532 | 61 | 360 | 163-197 | 100% (g_iter0 2-0*) |
| 101 | monmouth-college-cs.elicompbot | 527 | 60 | 393 | 177-216 | 100% (g_iter0 2-0*) |
| 102 | anicolao.jumbled | 414 | 64 | 388 | 173-215 | 100% (g_iter0 5-0*) |
| 103 | ShatterXD.SRNNbot | 391 | 66 | 356 | 159-197 | 100% (g_iter0 2-0*) |
| 104 | NotLLeon.player | 184 | 80 | 343 | 161-182 | 100% (g_iter0 2-0*) |
| 105 | CodeClash-ai.mysubmission | 103 | 82 | 384 | 164-220 | 100% (g_iter0 2-0*) |
| 106 | addiesteward.NDeClaw | 85 | 85 | 348 | 148-200 | 100% (g_iter0 5-0*) |
| 107 | Yooncw0223.lec3player | -229 | 99 | 327 | 48-279 | 100% (g_iter0 5-0*) |
| 108 | andrewkbank.First | -273 | 104 | 248 | 35-213 | 100% (g_iter0 2-0*) |
