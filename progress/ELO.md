# Ladder

15131 games (3299 ours, 6 of the stock examplefuncsplayer, 11826 between field bots on the ladder replica), 14711 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 109 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2104 +- 89 | 12 of 108 | 100 | 64-36 | 87.2% | 33.8% (vs 11) |
| c_spread2 | 2072 +- 88 | 13 of 108 | 100 | 61-39 | 86.0% | 30.0% (vs 11) |
| c_mend2 | 2072 +- 88 | 14 of 108 | 100 | 61-39 | 86.0% | 30.0% (vs 11) |
| c_scout1 | 2061 +- 88 | 15 of 108 | 100 | 60-40 | 85.6% | 28.8% (vs 11) |
| c_well7 | 2061 +- 88 | 16 of 108 | 100 | 60-40 | 85.6% | 28.8% (vs 11) |
| c_bc1 | 2046 +- 68 | 18 of 108 | 163 | 96-67 | 85.1% | 29.0% (vs 12) |
| c_def3 | 2042 +- 63 | 19 of 108 | 194 | 117-77 | 84.9% | 28.6% (vs 12) |
| c_end2 | 2020 +- 93 | 20 of 108 | 90 | 49-41 | 84.0% | 26.1% (vs 12) |
| c_flee3 | 2020 +- 88 | 21 of 108 | 100 | 56-44 | 84.0% | 26.1% (vs 12) |
| c_anc3 | 2013 +- 68 | 22 of 108 | 161 | 87-74 | 83.7% | 25.3% (vs 12) |
| c_aura2 | 2012 +- 52 | 23 of 108 | 311 | 160-151 | 83.7% | 25.2% (vs 12) |
| c_nav5 | 1955 +- 77 | 26 of 108 | 126 | 61-65 | 81.4% | 23.7% (vs 14) |
| c_nav6 | 1939 +- 77 | 28 of 108 | 129 | 58-71 | 80.7% | 24.1% (vs 15) |
| c_nav4 | 1916 +- 59 | 29 of 108 | 221 | 108-113 | 79.7% | 21.9% (vs 15) |
| c_swarm1 | 1837 +- 55 | 33 of 108 | 268 | 126-142 | 76.1% | 20.6% (vs 18) |
| c_line8a | 1794 +- 77 | 38 of 108 | 139 | 47-92 | 74.1% | 22.7% (vs 22) |
| g_iter0 | 1774 +- 54 | 39 of 108 | 455 | 230-225 | 73.1% | 21.0% (vs 22) |
| c_line6 | 1760 +- 93 | 41 of 108 | 100 | 32-68 | 72.5% | 21.2% (vs 23) |
| c_line7m | 1748 +- 94 | 43 of 108 | 100 | 31-69 | 71.9% | 21.4% (vs 24) |
| c_line5 | 1710 +- 96 | 48 of 108 | 100 | 28-72 | 70.0% | 22.4% (vs 28) |
| c_line4 | 1669 +- 99 | 50 of 108 | 100 | 25-75 | 67.9% | 20.1% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_mend2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2327 | 73 | 168 | 118-50 | 0% (g_iter0 0-5*) |
| 2 | awesomelemonade.finalBot | 2324 | 59 | 374 | 300-74 | 20% (c_mend2 2-8*) |
| 3 | IvanGeffner.fortytwo | 2321 | 72 | 180 | 124-56 | 0% (g_iter0 0-35) |
| 4 | carlguo866.submit26_final | 2290 | 70 | 185 | 124-61 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2268 | 56 | 383 | 295-88 | 40% (c_mend2 4-6*) |
| 6 | AnOvercookedFork.quals | 2207 | 66 | 202 | 131-71 | 33% (c_bc1 1-2*) |
| 7 | pranayagra.finalbotfinaltwo | 2175 | 65 | 209 | 135-74 | 29% (c_aura2 5-12*) |
| 8 | pranayagra.finalbotfinal | 2165 | 49 | 459 | 309-150 | 30% (c_mend2 3-7*) |
| 9 | georgezhang02.FB_ZZZ | 2158 | 64 | 202 | 124-78 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2134 | 66 | 199 | 126-73 | 22% (c_bc1 2-7*) |
| 11 | jmerle.camel_case_v30_final | 2120 | 48 | 441 | 295-146 | 40% (c_mend2 4-6*) |
| 12 | **us:c_well5** | 2104 | 89 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2072 | 88 | 100 | 61-39 |  |
| 14 | **us:c_mend2** | 2072 | 88 | 100 | 61-39 |  |
| 15 | **us:c_scout1** | 2061 | 88 | 100 | 60-40 |  |
| 16 | **us:c_well7** | 2061 | 88 | 100 | 60-40 |  |
| 17 | CyrilSharma.finalBot | 2047 | 58 | 257 | 151-106 | 22% (c_aura2 5-18*) |
| 18 | **us:c_bc1** | 2046 | 68 | 163 | 96-67 |  |
| 19 | **us:c_def3** | 2042 | 63 | 194 | 117-77 |  |
| 20 | **us:c_end2** | 2020 | 93 | 90 | 49-41 |  |
| 21 | **us:c_flee3** | 2020 | 88 | 100 | 56-44 |  |
| 22 | **us:c_anc3** | 2013 | 68 | 161 | 87-74 |  |
| 23 | **us:c_aura2** | 2012 | 52 | 311 | 160-151 |  |
| 24 | ethanlabelle.dev | 1990 | 55 | 259 | 149-110 | 53% (c_bc1 8-7*) |
| 25 | NotLLeon.v7 | 1957 | 45 | 466 | 249-217 | 70% (c_mend2 7-3*) |
| 26 | **us:c_nav5** | 1955 | 77 | 126 | 61-65 |  |
| 27 | georgezhang02.CB_tuning2 | 1945 | 45 | 434 | 237-197 | 60% (c_mend2 6-4*) |
| 28 | **us:c_nav6** | 1939 | 77 | 129 | 58-71 |  |
| 29 | **us:c_nav4** | 1916 | 59 | 221 | 108-113 |  |
| 30 | ethanlabelle.v19 | 1896 | 56 | 240 | 136-104 | 50% (c_bc1 6-6*) |
| 31 | britacatalin.FinalBot | 1872 | 45 | 434 | 213-221 | 80% (c_mend2 8-2*) |
| 32 | GabeG888.v8 | 1837 | 55 | 242 | 130-112 | 89% (c_def3 16-2*) |
| 33 | **us:c_swarm1** | 1837 | 55 | 268 | 126-142 |  |
| 34 | programjames.fourthbot | 1818 | 57 | 233 | 129-104 | 100% (c_aura2 3-0*) |
| 35 | VarunVejalla.ali8 | 1811 | 58 | 227 | 127-100 | 50% (c_aura2 3-3*) |
| 36 | GabeG888.v8o1 | 1811 | 55 | 237 | 135-102 | 67% (c_aura2 4-2*) |
| 37 | VarunVejalla.karel | 1808 | 56 | 244 | 132-112 | 33% (c_aura2 1-2*) |
| 38 | **us:c_line8a** | 1794 | 77 | 139 | 47-92 |  |
| 39 | **us:g_iter0** | 1774 | 54 | 455 | 230-225 |  |
| 40 | DannyZhang686.pqual2 | 1774 | 54 | 260 | 141-119 | 83% (c_anc3 5-1*) |
| 41 | **us:c_line6** | 1760 | 93 | 100 | 32-68 |  |
| 42 | NicholasKelly15.gopher10 | 1753 | 59 | 213 | 119-94 | 100% (c_anc3 3-0*) |
| 43 | **us:c_line7m** | 1748 | 94 | 100 | 31-69 |  |
| 44 | louishu17.louisv10 | 1745 | 57 | 228 | 122-106 | 100% (c_bc1 3-0*) |
| 45 | louishu17.wouisv8 | 1733 | 57 | 248 | 134-114 | 83% (c_aura2 5-1*) |
| 46 | reeceyang.v5anaconda | 1733 | 44 | 470 | 193-277 | 90% (c_mend2 9-1*) |
| 47 | SampleProvider.SPAARK | 1724 | 56 | 234 | 129-105 | 33% (c_anc3 1-2*) |
| 48 | **us:c_line5** | 1710 | 96 | 100 | 28-72 |  |
| 49 | battlecode-archive.Sprint1 | 1683 | 46 | 428 | 165-263 | 90% (c_mend2 9-1*) |
| 50 | **us:c_line4** | 1669 | 99 | 100 | 25-75 |  |
| 51 | ipince.bobby | 1619 | 60 | 211 | 112-99 | 67% (c_swarm1 2-1*) |
| 52 | SteamBlizzard.newVnewME | 1570 | 53 | 267 | 136-131 | 80% (g_iter0 4-1*) |
| 53 | legobridge.tacoplayer | 1561 | 56 | 250 | 130-120 | 85% (g_iter0 11-2*) |
| 54 | TheK098.qp1_7_sprint_1 | 1544 | 55 | 251 | 138-113 | 100% (c_swarm1 6-0*) |
| 55 | polyllc.poly | 1530 | 59 | 223 | 115-108 | 100% (g_iter0 2-0*) |
| 56 | toyat522.bot5a | 1480 | 52 | 276 | 136-140 | 80% (g_iter0 4-1*) |
| 57 | elgoldie.head_v5 | 1479 | 52 | 258 | 128-130 | 100% (g_iter0 2-0*) |
| 58 | DukeBas._main | 1465 | 56 | 241 | 128-113 | 100% (g_iter0 2-0*) |
| 59 | ColtG5.rexv9 | 1464 | 53 | 259 | 131-128 | 100% (g_iter0 2-0*) |
| 60 | beaverbois.USQualifiers | 1430 | 53 | 263 | 138-125 | 50% (g_iter0 1-1*) |
| 61 | Nawlej.PoonPoon | 1391 | 56 | 251 | 123-128 | 100% (g_iter0 2-0*) |
| 62 | kevinli405.maggi3_2 | 1385 | 51 | 294 | 146-148 | 100% (g_iter0 2-0*) |
| 63 | yaonam.PoonPoonv4 | 1355 | 47 | 501 | 171-330 | 90% (c_mend2 9-1*) |
| 64 | BrysonJGalapon.friday | 1349 | 53 | 257 | 131-126 | 100% (g_iter0 2-0*) |
| 65 | nail-e.Barry | 1334 | 52 | 273 | 136-137 | 100% (g_iter0 2-0*) |
| 66 | aj-chau.attempt1 | 1329 | 53 | 274 | 142-132 | 100% (g_iter0 5-0*) |
| 67 | kevinli405.maggi3 | 1319 | 54 | 270 | 137-133 | 100% (g_iter0 5-0*) |
| 68 | prisms-cs-club.prisms10 | 1280 | 54 | 263 | 129-134 | 100% (g_iter0 2-0*) |
| 69 | mama4294.currentPlayer | 1269 | 53 | 276 | 140-136 | 100% (g_iter0 2-0*) |
| 70 | ipince.bobby_v2 | 1240 | 51 | 305 | 150-155 | 67% (c_swarm1 2-1*) |
| 71 | bewuwy.deathbot4 | 1160 | 50 | 328 | 157-171 | 100% (g_iter0 2-0*) |
| 72 | JfeMak.realplayer2 | 1154 | 52 | 290 | 141-149 | 100% (g_iter0 2-0*) |
| 73 | andrewgopher.gopherbot | 1153 | 52 | 311 | 150-161 | 100% (g_iter0 2-0*) |
| 74 | BrysonJGalapon.aloha | 1153 | 50 | 317 | 157-160 | 100% (c_swarm1 3-0*) |
| 75 | PSUtblock.sprint_four_player | 1114 | 53 | 299 | 147-152 | 100% (g_iter0 2-0*) |
| 76 | SampleProvider.SPAARK_1_12_2023 | 1073 | 51 | 329 | 157-172 | 100% (c_swarm1 3-0*) |
| 77 | Nawlej.PoonPoonv3 | 1050 | 52 | 321 | 154-167 | 100% (g_iter0 5-0*) |
| 78 | NolanChai.nolan_1 | 1047 | 51 | 339 | 164-175 | 100% (g_iter0 2-0*) |
| 79 | SDainard-PDX.Team_Player | 1045 | 54 | 288 | 141-147 | 100% (g_iter0 2-0*) |
| 80 | Juanbri02.matfisplayer1 | 1039 | 51 | 324 | 155-169 | 100% (g_iter0 5-0*) |
| 81 | andrewgopher.gopherbot1 | 1033 | 53 | 306 | 140-166 | 100% (g_iter0 2-0*) |
| 82 | jyorkio.elicompbot | 1013 | 52 | 309 | 152-157 | 100% (g_iter0 2-0*) |
| 83 | vontell.regressiongames | 945 | 52 | 343 | 168-175 | 100% (g_iter0 5-0*) |
| 84 | legobridge.kushalplayer | 923 | 57 | 281 | 130-151 | 100% (g_iter0 2-0*) |
| 85 | SteamBlizzard.Block | 896 | 54 | 345 | 158-187 | 100% (g_iter0 5-0*) |
| 86 | Patela171.Battlecode2023_Robot | 896 | 55 | 314 | 145-169 | 100% (g_iter0 2-0*) |
| 87 | ax-95174.MPAction | 868 | 56 | 307 | 145-162 | 100% (c_swarm1 3-0*) |
| 88 | JackLee9355.jackPlayer | 813 | 59 | 310 | 141-169 | 100% (g_iter0 2-0*) |
| 89 | nail-e.Dante | 797 | 55 | 341 | 165-176 | 100% (g_iter0 2-0*) |
| 90 | Chahat08.toph | 789 | 56 | 324 | 148-176 | 100% (g_iter0 2-0*) |
| 91 | michael-tyl.hqrewrite | 777 | 57 | 317 | 147-170 | 100% (g_iter0 2-0*) |
| 92 | mama4294.learningBot | 773 | 58 | 322 | 147-175 | 100% (g_iter0 2-0*) |
| 93 | anicolao.submission | 725 | 57 | 373 | 170-203 | 100% (g_iter0 2-0*) |
| 94 | team-remember-to-hydrate.sprint_1 | 679 | 59 | 327 | 143-184 | 100% (g_iter0 2-0*) |
| 95 | Vinceyou1.Player1 | 583 | 62 | 310 | 133-177 | 100% (g_iter0 2-0*) |
| 96 | toyat522.bot5 | 581 | 61 | 366 | 166-200 | 100% (g_iter0 2-0*) |
| 97 | addiesteward.elicompbot | 577 | 61 | 341 | 150-191 | 100% (g_iter0 5-0*) |
| 98 | michael-tyl.cc_v0_5_0_6 | 561 | 60 | 381 | 167-214 | 100% (g_iter0 2-0*) |
| 99 | Chahat08.lazarus | 532 | 62 | 349 | 156-193 | 100% (g_iter0 2-0*) |
| 100 | monmouth-college-cs.elicompbot | 526 | 62 | 366 | 163-203 | 100% (g_iter0 2-0*) |
| 101 | Swordman51.AdeptusAstartes2 | 525 | 63 | 333 | 149-184 | 100% (g_iter0 2-0*) |
| 102 | anicolao.jumbled | 411 | 67 | 360 | 162-198 | 100% (g_iter0 5-0*) |
| 103 | ShatterXD.SRNNbot | 390 | 68 | 328 | 147-181 | 100% (g_iter0 2-0*) |
| 104 | NotLLeon.player | 187 | 82 | 315 | 144-171 | 100% (g_iter0 2-0*) |
| 105 | CodeClash-ai.mysubmission | 114 | 83 | 362 | 152-210 | 100% (g_iter0 2-0*) |
| 106 | addiesteward.NDeClaw | 96 | 87 | 325 | 137-188 | 100% (g_iter0 5-0*) |
| 107 | Yooncw0223.lec3player | -222 | 102 | 305 | 46-259 | 100% (g_iter0 5-0*) |
| 108 | andrewkbank.First | -281 | 108 | 234 | 31-203 | 100% (g_iter0 2-0*) |
