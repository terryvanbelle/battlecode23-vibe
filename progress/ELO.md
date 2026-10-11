# Ladder

14028 games (2967 ours, 6 of the stock examplefuncsplayer, 11055 between field bots on the ladder replica), 13670 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 106 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2124 +- 90 | 12 of 105 | 100 | 64-36 | 87.1% | 33.6% (vs 11) |
| c_spread2 | 2092 +- 89 | 13 of 105 | 100 | 61-39 | 86.0% | 29.7% (vs 11) |
| c_scout1 | 2082 +- 89 | 14 of 105 | 100 | 60-40 | 85.6% | 28.5% (vs 11) |
| c_def3 | 2064 +- 64 | 16 of 105 | 194 | 117-77 | 84.9% | 28.5% (vs 12) |
| c_bc1 | 2058 +- 79 | 17 of 105 | 122 | 71-51 | 84.6% | 27.8% (vs 12) |
| c_flee3 | 2040 +- 88 | 18 of 105 | 100 | 56-44 | 84.0% | 25.9% (vs 12) |
| c_anc3 | 2034 +- 69 | 19 of 105 | 161 | 87-74 | 83.7% | 25.2% (vs 12) |
| c_aura2 | 2032 +- 53 | 20 of 105 | 311 | 160-151 | 83.6% | 25.0% (vs 12) |
| c_nav5 | 1975 +- 78 | 23 of 105 | 126 | 61-65 | 81.3% | 23.5% (vs 14) |
| c_nav6 | 1960 +- 77 | 25 of 105 | 129 | 58-71 | 80.6% | 24.0% (vs 15) |
| c_nav4 | 1936 +- 59 | 26 of 105 | 221 | 108-113 | 79.6% | 21.8% (vs 15) |
| c_swarm1 | 1856 +- 56 | 30 of 105 | 268 | 126-142 | 76.0% | 20.4% (vs 18) |
| c_line8a | 1813 +- 78 | 35 of 105 | 139 | 47-92 | 73.9% | 22.6% (vs 22) |
| g_iter0 | 1796 +- 55 | 37 of 105 | 455 | 230-225 | 73.1% | 22.4% (vs 23) |
| c_line6 | 1779 +- 94 | 38 of 105 | 100 | 32-68 | 72.2% | 20.9% (vs 23) |
| c_line7m | 1766 +- 95 | 41 of 105 | 100 | 31-69 | 71.6% | 22.2% (vs 25) |
| c_line5 | 1728 +- 97 | 45 of 105 | 100 | 28-72 | 69.7% | 22.1% (vs 28) |
| c_line4 | 1687 +- 100 | 47 of 105 | 100 | 25-75 | 67.6% | 19.9% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_bc1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2364 | 76 | 169 | 122-47 | 0% (g_iter0 0-35) |
| 2 | awesomelemonade.finalBot | 2354 | 64 | 332 | 270-62 | 20% (c_bc1 2-8*) |
| 3 | maxwelljones14.MPWorking | 2341 | 76 | 157 | 108-49 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2304 | 73 | 173 | 116-57 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2287 | 60 | 341 | 265-76 | 30% (c_bc1 3-7*) |
| 6 | AnOvercookedFork.quals | 2222 | 69 | 187 | 119-68 | 22% (c_aura2 4-14*) |
| 7 | pranayagra.finalbotfinaltwo | 2198 | 67 | 200 | 130-70 | 29% (c_aura2 5-12*) |
| 8 | pranayagra.finalbotfinal | 2190 | 52 | 417 | 286-131 | 30% (c_bc1 3-7*) |
| 9 | georgezhang02.FB_ZZZ | 2186 | 67 | 191 | 121-70 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2156 | 69 | 187 | 119-68 | 0% (c_bc1 0-3*) |
| 11 | jmerle.camel_case_v30_final | 2138 | 51 | 401 | 272-129 | 40% (c_bc1 4-6*) |
| 12 | **us:c_well5** | 2124 | 90 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2092 | 89 | 100 | 61-39 |  |
| 14 | **us:c_scout1** | 2082 | 89 | 100 | 60-40 |  |
| 15 | CyrilSharma.finalBot | 2068 | 59 | 247 | 147-100 | 22% (c_aura2 5-18*) |
| 16 | **us:c_def3** | 2064 | 64 | 194 | 117-77 |  |
| 17 | **us:c_bc1** | 2058 | 79 | 122 | 71-51 |  |
| 18 | **us:c_flee3** | 2040 | 88 | 100 | 56-44 |  |
| 19 | **us:c_anc3** | 2034 | 69 | 161 | 87-74 |  |
| 20 | **us:c_aura2** | 2032 | 53 | 311 | 160-151 |  |
| 21 | ethanlabelle.dev | 2012 | 57 | 238 | 140-98 | 67% (c_bc1 2-1*) |
| 22 | NotLLeon.v7 | 1980 | 47 | 414 | 230-184 | 76% (c_bc1 13-4*) |
| 23 | **us:c_nav5** | 1975 | 78 | 126 | 61-65 |  |
| 24 | georgezhang02.CB_tuning2 | 1962 | 48 | 392 | 218-174 | 50% (c_bc1 5-5*) |
| 25 | **us:c_nav6** | 1960 | 77 | 129 | 58-71 |  |
| 26 | **us:c_nav4** | 1936 | 59 | 221 | 108-113 |  |
| 27 | ethanlabelle.v19 | 1914 | 58 | 223 | 129-94 | 44% (c_bc1 4-5*) |
| 28 | britacatalin.FinalBot | 1894 | 47 | 402 | 203-199 | 80% (c_bc1 8-2*) |
| 29 | GabeG888.v8 | 1863 | 56 | 230 | 123-107 | 89% (c_def3 16-2*) |
| 30 | **us:c_swarm1** | 1856 | 56 | 268 | 126-142 |  |
| 31 | programjames.fourthbot | 1836 | 59 | 218 | 118-100 | 100% (c_aura2 3-0*) |
| 32 | GabeG888.v8o1 | 1833 | 57 | 225 | 129-96 | 67% (c_aura2 4-2*) |
| 33 | VarunVejalla.karel | 1830 | 57 | 232 | 127-105 | 33% (c_aura2 1-2*) |
| 34 | VarunVejalla.ali8 | 1829 | 60 | 213 | 118-95 | 50% (c_aura2 3-3*) |
| 35 | **us:c_line8a** | 1813 | 78 | 139 | 47-92 |  |
| 36 | DannyZhang686.pqual2 | 1799 | 56 | 243 | 130-113 | 83% (c_anc3 5-1*) |
| 37 | **us:g_iter0** | 1796 | 55 | 455 | 230-225 |  |
| 38 | **us:c_line6** | 1779 | 94 | 100 | 32-68 |  |
| 39 | NicholasKelly15.gopher10 | 1775 | 61 | 199 | 112-87 | 100% (c_anc3 3-0*) |
| 40 | louishu17.louisv10 | 1772 | 59 | 216 | 119-97 | 100% (c_nav4 6-0*) |
| 41 | **us:c_line7m** | 1766 | 95 | 100 | 31-69 |  |
| 42 | louishu17.wouisv8 | 1752 | 60 | 227 | 123-104 | 83% (c_aura2 5-1*) |
| 43 | SampleProvider.SPAARK | 1751 | 58 | 222 | 125-97 | 33% (c_anc3 1-2*) |
| 44 | reeceyang.v5anaconda | 1748 | 46 | 417 | 174-243 | 90% (c_bc1 9-1*) |
| 45 | **us:c_line5** | 1728 | 97 | 100 | 28-72 |  |
| 46 | battlecode-archive.Sprint1 | 1696 | 48 | 386 | 150-236 | 90% (c_bc1 9-1*) |
| 47 | **us:c_line4** | 1687 | 100 | 100 | 25-75 |  |
| 48 | ipince.bobby | 1650 | 63 | 191 | 105-86 | 67% (c_swarm1 2-1*) |
| 49 | SteamBlizzard.newVnewME | 1597 | 55 | 249 | 127-122 | 80% (g_iter0 4-1*) |
| 50 | legobridge.tacoplayer | 1591 | 58 | 234 | 124-110 | 85% (g_iter0 11-2*) |
| 51 | TheK098.qp1_7_sprint_1 | 1558 | 57 | 236 | 125-111 | 100% (c_swarm1 6-0*) |
| 52 | polyllc.poly | 1542 | 62 | 205 | 103-102 | 100% (g_iter0 2-0*) |
| 53 | toyat522.bot5a | 1520 | 54 | 256 | 131-125 | 80% (g_iter0 4-1*) |
| 54 | elgoldie.head_v5 | 1507 | 54 | 243 | 120-123 | 100% (g_iter0 2-0*) |
| 55 | DukeBas._main | 1495 | 58 | 224 | 119-105 | 100% (g_iter0 2-0*) |
| 56 | ColtG5.rexv9 | 1480 | 55 | 243 | 121-122 | 100% (g_iter0 2-0*) |
| 57 | beaverbois.USQualifiers | 1457 | 55 | 243 | 127-116 | 50% (g_iter0 1-1*) |
| 58 | Nawlej.PoonPoon | 1415 | 57 | 231 | 118-113 | 100% (g_iter0 2-0*) |
| 59 | kevinli405.maggi3_2 | 1410 | 53 | 276 | 138-138 | 100% (g_iter0 2-0*) |
| 60 | BrysonJGalapon.friday | 1375 | 54 | 244 | 126-118 | 100% (g_iter0 2-0*) |
| 61 | yaonam.PoonPoonv4 | 1371 | 49 | 453 | 155-298 | 90% (c_bc1 9-1*) |
| 62 | aj-chau.attempt1 | 1369 | 54 | 253 | 133-120 | 100% (g_iter0 5-0*) |
| 63 | nail-e.Barry | 1366 | 53 | 255 | 129-126 | 100% (g_iter0 2-0*) |
| 64 | kevinli405.maggi3 | 1352 | 56 | 252 | 129-123 | 100% (g_iter0 5-0*) |
| 65 | prisms-cs-club.prisms10 | 1310 | 55 | 249 | 122-127 | 100% (g_iter0 2-0*) |
| 66 | mama4294.currentPlayer | 1290 | 54 | 258 | 126-132 | 100% (g_iter0 2-0*) |
| 67 | ipince.bobby_v2 | 1262 | 53 | 281 | 137-144 | 67% (c_swarm1 2-1*) |
| 68 | bewuwy.deathbot4 | 1195 | 52 | 307 | 150-157 | 100% (g_iter0 2-0*) |
| 69 | andrewgopher.gopherbot | 1191 | 53 | 291 | 142-149 | 100% (g_iter0 2-0*) |
| 70 | JfeMak.realplayer2 | 1181 | 54 | 269 | 132-137 | 100% (g_iter0 2-0*) |
| 71 | BrysonJGalapon.aloha | 1178 | 51 | 299 | 147-152 | 100% (c_swarm1 3-0*) |
| 72 | PSUtblock.sprint_four_player | 1149 | 55 | 280 | 139-141 | 100% (g_iter0 2-0*) |
| 73 | SampleProvider.SPAARK_1_12_2023 | 1115 | 52 | 310 | 151-159 | 100% (c_swarm1 3-0*) |
| 74 | Nawlej.PoonPoonv3 | 1087 | 53 | 304 | 145-159 | 100% (g_iter0 5-0*) |
| 75 | NolanChai.nolan_1 | 1079 | 51 | 326 | 156-170 | 100% (g_iter0 2-0*) |
| 76 | Juanbri02.matfisplayer1 | 1077 | 52 | 309 | 148-161 | 100% (g_iter0 5-0*) |
| 77 | SDainard-PDX.Team_Player | 1074 | 56 | 266 | 130-136 | 100% (g_iter0 2-0*) |
| 78 | andrewgopher.gopherbot1 | 1073 | 54 | 294 | 138-156 | 100% (g_iter0 2-0*) |
| 79 | jyorkio.elicompbot | 1042 | 54 | 286 | 140-146 | 100% (g_iter0 2-0*) |
| 80 | vontell.regressiongames | 979 | 52 | 324 | 157-167 | 100% (g_iter0 5-0*) |
| 81 | legobridge.kushalplayer | 951 | 59 | 256 | 116-140 | 100% (g_iter0 2-0*) |
| 82 | SteamBlizzard.Block | 930 | 55 | 319 | 142-177 | 100% (g_iter0 5-0*) |
| 83 | Patela171.Battlecode2023_Robot | 928 | 56 | 294 | 134-160 | 100% (g_iter0 2-0*) |
| 84 | ax-95174.MPAction | 908 | 56 | 292 | 136-156 | 100% (c_swarm1 3-0*) |
| 85 | JackLee9355.jackPlayer | 860 | 60 | 295 | 133-162 | 100% (g_iter0 2-0*) |
| 86 | Chahat08.toph | 838 | 57 | 298 | 139-159 | 100% (g_iter0 2-0*) |
| 87 | nail-e.Dante | 836 | 56 | 323 | 154-169 | 100% (g_iter0 2-0*) |
| 88 | michael-tyl.hqrewrite | 828 | 58 | 303 | 144-159 | 100% (g_iter0 2-0*) |
| 89 | mama4294.learningBot | 809 | 59 | 298 | 135-163 | 100% (g_iter0 2-0*) |
| 90 | anicolao.submission | 770 | 57 | 348 | 158-190 | 100% (g_iter0 2-0*) |
| 91 | team-remember-to-hydrate.sprint_1 | 715 | 60 | 309 | 136-173 | 100% (g_iter0 2-0*) |
| 92 | Vinceyou1.Player1 | 632 | 63 | 297 | 129-168 | 100% (g_iter0 2-0*) |
| 93 | addiesteward.elicompbot | 619 | 62 | 327 | 144-183 | 100% (g_iter0 5-0*) |
| 94 | toyat522.bot5 | 612 | 62 | 353 | 159-194 | 100% (g_iter0 2-0*) |
| 95 | michael-tyl.cc_v0_5_0_6 | 596 | 61 | 357 | 154-203 | 100% (g_iter0 2-0*) |
| 96 | Chahat08.lazarus | 565 | 64 | 326 | 146-180 | 100% (g_iter0 2-0*) |
| 97 | monmouth-college-cs.elicompbot | 558 | 63 | 350 | 153-197 | 100% (g_iter0 2-0*) |
| 98 | Swordman51.AdeptusAstartes2 | 556 | 64 | 319 | 141-178 | 100% (g_iter0 2-0*) |
| 99 | anicolao.jumbled | 441 | 68 | 340 | 149-191 | 100% (g_iter0 5-0*) |
| 100 | ShatterXD.SRNNbot | 425 | 69 | 307 | 132-175 | 100% (g_iter0 2-0*) |
| 101 | NotLLeon.player | 224 | 84 | 297 | 137-160 | 100% (g_iter0 2-0*) |
| 102 | CodeClash-ai.mysubmission | 170 | 84 | 343 | 147-196 | 100% (g_iter0 2-0*) |
| 103 | addiesteward.NDeClaw | 135 | 89 | 305 | 127-178 | 100% (g_iter0 5-0*) |
| 104 | Yooncw0223.lec3player | -170 | 103 | 290 | 43-247 | 100% (g_iter0 5-0*) |
| 105 | andrewkbank.First | -241 | 111 | 222 | 27-195 | 100% (g_iter0 2-0*) |
