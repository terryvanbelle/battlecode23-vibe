# Ladder

17701 games (3877 ours, 6 of the stock examplefuncsplayer, 13818 between field bots on the ladder replica), 17298 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 110 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2089 +- 88 | 12 of 109 | 100 | 64-36 | 87.1% | 33.5% (vs 11) |
| c_spread2 | 2058 +- 88 | 13 of 109 | 100 | 61-39 | 85.9% | 29.7% (vs 11) |
| c_bc3 | 2058 +- 88 | 14 of 109 | 100 | 61-39 | 85.9% | 29.7% (vs 11) |
| c_well7 | 2047 +- 87 | 15 of 109 | 100 | 60-40 | 85.5% | 28.6% (vs 11) |
| c_scout1 | 2047 +- 87 | 16 of 109 | 100 | 60-40 | 85.5% | 28.6% (vs 11) |
| c_bc1 | 2031 +- 67 | 18 of 109 | 164 | 97-67 | 84.9% | 28.5% (vs 12) |
| c_mend2 | 2027 +- 44 | 19 of 109 | 523 | 305-218 | 84.7% | 28.1% (vs 12) |
| c_def3 | 2026 +- 62 | 20 of 109 | 199 | 120-79 | 84.7% | 27.9% (vs 12) |
| c_end2 | 2016 +- 87 | 21 of 109 | 100 | 57-43 | 84.3% | 26.9% (vs 12) |
| c_flee3 | 2006 +- 87 | 22 of 109 | 100 | 56-44 | 83.9% | 25.8% (vs 12) |
| c_anc3 | 2000 +- 67 | 23 of 109 | 163 | 88-75 | 83.6% | 25.1% (vs 12) |
| c_aura2 | 1998 +- 51 | 24 of 109 | 314 | 162-152 | 83.6% | 25.0% (vs 12) |
| c_nav5 | 1941 +- 76 | 26 of 109 | 126 | 61-65 | 81.2% | 21.7% (vs 13) |
| c_nav6 | 1926 +- 76 | 29 of 109 | 129 | 58-71 | 80.5% | 24.1% (vs 15) |
| c_nav4 | 1905 +- 58 | 30 of 109 | 221 | 108-113 | 79.6% | 22.1% (vs 15) |
| c_swarm1 | 1828 +- 54 | 34 of 109 | 271 | 128-143 | 76.1% | 21.1% (vs 18) |
| c_line8a | 1783 +- 76 | 39 of 109 | 139 | 47-92 | 74.0% | 22.8% (vs 22) |
| g_iter0 | 1765 +- 54 | 40 of 109 | 456 | 230-226 | 73.1% | 21.2% (vs 22) |
| c_line6 | 1747 +- 93 | 44 of 109 | 100 | 32-68 | 72.2% | 23.2% (vs 25) |
| c_line7m | 1735 +- 93 | 45 of 109 | 100 | 31-69 | 71.6% | 22.2% (vs 25) |
| c_line5 | 1697 +- 96 | 49 of 109 | 100 | 28-72 | 69.7% | 22.0% (vs 28) |
| c_line4 | 1657 +- 99 | 51 of 109 | 100 | 25-75 | 67.7% | 19.7% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_mend2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2320 | 69 | 186 | 131-55 | 33% (c_mend2 2-4*) |
| 2 | IvanGeffner.fortytwo | 2301 | 64 | 223 | 157-66 | 13% (c_mend2 3-20*) |
| 3 | awesomelemonade.finalBot | 2297 | 55 | 413 | 324-89 | 20% (c_mend2 5-20*) |
| 4 | carlguo866.submit26_final | 2278 | 66 | 199 | 132-67 | 0% (c_mend2 0-3*) |
| 5 | vrangr1.AFinalsBot | 2253 | 52 | 417 | 317-100 | 36% (c_mend2 8-14*) |
| 6 | AnOvercookedFork.quals | 2200 | 62 | 228 | 150-78 | 25% (c_mend2 3-9*) |
| 7 | pranayagra.finalbotfinal | 2158 | 46 | 499 | 335-164 | 32% (c_mend2 7-15*) |
| 8 | pranayagra.finalbotfinaltwo | 2156 | 61 | 228 | 142-86 | 0% (c_mend2 0-3*) |
| 9 | georgezhang02.FB_ZZZ | 2150 | 60 | 233 | 146-87 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2125 | 61 | 228 | 145-83 | 28% (c_mend2 5-13*) |
| 11 | jmerle.camel_case_v30_final | 2111 | 46 | 472 | 312-160 | 40% (c_mend2 4-6*) |
| 12 | **us:c_well5** | 2089 | 88 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2058 | 88 | 100 | 61-39 |  |
| 14 | **us:c_bc3** | 2058 | 88 | 100 | 61-39 |  |
| 15 | **us:c_well7** | 2047 | 87 | 100 | 60-40 |  |
| 16 | **us:c_scout1** | 2047 | 87 | 100 | 60-40 |  |
| 17 | CyrilSharma.finalBot | 2043 | 55 | 271 | 161-110 | 22% (c_aura2 5-18*) |
| 18 | **us:c_bc1** | 2031 | 67 | 164 | 97-67 |  |
| 19 | **us:c_mend2** | 2027 | 44 | 523 | 305-218 |  |
| 20 | **us:c_def3** | 2026 | 62 | 199 | 120-79 |  |
| 21 | **us:c_end2** | 2016 | 87 | 100 | 57-43 |  |
| 22 | **us:c_flee3** | 2006 | 87 | 100 | 56-44 |  |
| 23 | **us:c_anc3** | 2000 | 67 | 163 | 88-75 |  |
| 24 | **us:c_aura2** | 1998 | 51 | 314 | 162-152 |  |
| 25 | ethanlabelle.dev | 1963 | 50 | 311 | 172-139 | 60% (c_mend2 18-12) |
| 26 | **us:c_nav5** | 1941 | 76 | 126 | 61-65 |  |
| 27 | NotLLeon.v7 | 1938 | 41 | 544 | 282-262 | 74% (c_mend2 39-14) |
| 28 | georgezhang02.CB_tuning2 | 1933 | 41 | 542 | 282-260 | 59% (c_mend2 47-33) |
| 29 | **us:c_nav6** | 1926 | 76 | 129 | 58-71 |  |
| 30 | **us:c_nav4** | 1905 | 58 | 221 | 108-113 |  |
| 31 | ethanlabelle.v19 | 1857 | 48 | 342 | 169-173 | 78% (c_mend2 52-15) |
| 32 | britacatalin.FinalBot | 1853 | 42 | 498 | 238-260 | 75% (c_mend2 12-4*) |
| 33 | VarunVejalla.karel | 1831 | 48 | 349 | 179-170 | 66% (c_mend2 49-25) |
| 34 | **us:c_swarm1** | 1828 | 54 | 271 | 128-143 |  |
| 35 | programjames.fourthbot | 1821 | 53 | 266 | 147-119 | 64% (c_mend2 7-4*) |
| 36 | GabeG888.v8 | 1813 | 52 | 272 | 149-123 | 89% (c_def3 16-2*) |
| 37 | VarunVejalla.ali8 | 1808 | 54 | 261 | 147-114 | 83% (c_mend2 5-1*) |
| 38 | GabeG888.v8o1 | 1806 | 52 | 267 | 154-113 | 67% (c_aura2 4-2*) |
| 39 | **us:c_line8a** | 1783 | 76 | 139 | 47-92 |  |
| 40 | **us:g_iter0** | 1765 | 54 | 456 | 230-226 |  |
| 41 | DannyZhang686.pqual2 | 1764 | 51 | 291 | 154-137 | 83% (c_anc3 5-1*) |
| 42 | NicholasKelly15.gopher10 | 1763 | 55 | 244 | 143-101 | 100% (c_anc3 3-0*) |
| 43 | louishu17.louisv10 | 1748 | 53 | 258 | 138-120 | 100% (c_bc1 3-0*) |
| 44 | **us:c_line6** | 1747 | 93 | 100 | 32-68 |  |
| 45 | **us:c_line7m** | 1735 | 93 | 100 | 31-69 |  |
| 46 | SampleProvider.SPAARK | 1728 | 54 | 258 | 139-119 | 33% (c_anc3 1-2*) |
| 47 | louishu17.wouisv8 | 1725 | 53 | 280 | 150-130 | 83% (c_aura2 5-1*) |
| 48 | reeceyang.v5anaconda | 1720 | 42 | 512 | 206-306 | 90% (c_mend2 9-1*) |
| 49 | **us:c_line5** | 1697 | 96 | 100 | 28-72 |  |
| 50 | battlecode-archive.Sprint1 | 1679 | 43 | 476 | 178-298 | 95% (c_mend2 21-1*) |
| 51 | **us:c_line4** | 1657 | 99 | 100 | 25-75 |  |
| 52 | ipince.bobby | 1602 | 57 | 233 | 121-112 | 67% (c_swarm1 2-1*) |
| 53 | legobridge.tacoplayer | 1570 | 52 | 293 | 156-137 | 85% (g_iter0 11-2*) |
| 54 | SteamBlizzard.newVnewME | 1562 | 50 | 299 | 146-153 | 80% (g_iter0 4-1*) |
| 55 | TheK098.qp1_7_sprint_1 | 1544 | 50 | 298 | 172-126 | 100% (c_swarm1 6-0*) |
| 56 | polyllc.poly | 1521 | 57 | 242 | 126-116 | 100% (g_iter0 2-0*) |
| 57 | toyat522.bot5a | 1473 | 49 | 311 | 144-167 | 80% (g_iter0 4-1*) |
| 58 | elgoldie.head_v5 | 1469 | 49 | 291 | 141-150 | 100% (g_iter0 2-0*) |
| 59 | ColtG5.rexv9 | 1459 | 49 | 307 | 149-158 | 100% (g_iter0 2-0*) |
| 60 | DukeBas._main | 1441 | 50 | 308 | 173-135 | 100% (g_iter0 2-0*) |
| 61 | beaverbois.USQualifiers | 1430 | 50 | 290 | 154-136 | 50% (g_iter0 1-1*) |
| 62 | kevinli405.maggi3_2 | 1386 | 48 | 330 | 170-160 | 100% (g_iter0 2-0*) |
| 63 | Nawlej.PoonPoon | 1367 | 53 | 279 | 136-143 | 100% (g_iter0 2-0*) |
| 64 | yaonam.PoonPoonv4 | 1343 | 44 | 553 | 190-363 | 90% (c_mend2 9-1*) |
| 65 | BrysonJGalapon.friday | 1337 | 49 | 295 | 151-144 | 100% (g_iter0 2-0*) |
| 66 | nail-e.Barry | 1322 | 48 | 312 | 156-156 | 100% (g_iter0 2-0*) |
| 67 | aj-chau.attempt1 | 1316 | 49 | 318 | 167-151 | 100% (g_iter0 5-0*) |
| 68 | kevinli405.maggi3 | 1308 | 51 | 312 | 148-164 | 100% (g_iter0 5-0*) |
| 69 | prisms-cs-club.prisms10 | 1280 | 49 | 316 | 158-158 | 100% (g_iter0 2-0*) |
| 70 | mama4294.currentPlayer | 1263 | 48 | 328 | 159-169 | 100% (g_iter0 2-0*) |
| 71 | ipince.bobby_v2 | 1244 | 48 | 350 | 167-183 | 67% (c_swarm1 2-1*) |
| 72 | bewuwy.deathbot4 | 1161 | 46 | 398 | 202-196 | 100% (g_iter0 2-0*) |
| 73 | andrewgopher.gopherbot | 1157 | 47 | 367 | 174-193 | 100% (g_iter0 2-0*) |
| 74 | JfeMak.realplayer2 | 1156 | 47 | 360 | 184-176 | 100% (g_iter0 2-0*) |
| 75 | BrysonJGalapon.aloha | 1145 | 47 | 377 | 194-183 | 100% (c_swarm1 3-0*) |
| 76 | PSUtblock.sprint_four_player | 1112 | 49 | 351 | 167-184 | 100% (g_iter0 2-0*) |
| 77 | SampleProvider.SPAARK_1_12_2023 | 1072 | 47 | 401 | 212-189 | 100% (c_swarm1 3-0*) |
| 78 | NolanChai.nolan_1 | 1041 | 47 | 395 | 193-202 | 100% (g_iter0 2-0*) |
| 79 | Nawlej.PoonPoonv3 | 1039 | 48 | 376 | 171-205 | 100% (g_iter0 5-0*) |
| 80 | Juanbri02.matfisplayer1 | 1039 | 48 | 380 | 187-193 | 100% (g_iter0 5-0*) |
| 81 | SDainard-PDX.Team_Player | 1033 | 50 | 350 | 158-192 | 100% (g_iter0 2-0*) |
| 82 | andrewgopher.gopherbot1 | 1021 | 50 | 357 | 164-193 | 100% (g_iter0 2-0*) |
| 83 | jyorkio.elicompbot | 1003 | 48 | 377 | 186-191 | 100% (g_iter0 2-0*) |
| 84 | vontell.regressiongames | 927 | 48 | 405 | 194-211 | 100% (g_iter0 5-0*) |
| 85 | legobridge.kushalplayer | 917 | 52 | 345 | 162-183 | 100% (g_iter0 2-0*) |
| 86 | Patela171.Battlecode2023_Robot | 871 | 51 | 375 | 171-204 | 100% (g_iter0 2-0*) |
| 87 | SteamBlizzard.Block | 862 | 50 | 399 | 174-225 | 100% (g_iter0 5-0*) |
| 88 | ax-95174.MPAction | 840 | 50 | 394 | 174-220 | 100% (c_swarm1 3-0*) |
| 89 | nail-e.Dante | 807 | 51 | 412 | 214-198 | 100% (g_iter0 2-0*) |
| 90 | Chahat08.toph | 783 | 52 | 396 | 193-203 | 100% (g_iter0 2-0*) |
| 91 | JackLee9355.jackPlayer | 776 | 55 | 362 | 158-204 | 100% (g_iter0 2-0*) |
| 92 | mama4294.learningBot | 761 | 53 | 401 | 194-207 | 100% (g_iter0 2-0*) |
| 93 | michael-tyl.hqrewrite | 754 | 54 | 370 | 174-196 | 100% (g_iter0 2-0*) |
| 94 | anicolao.submission | 715 | 52 | 452 | 216-236 | 100% (g_iter0 2-0*) |
| 95 | team-remember-to-hydrate.sprint_1 | 677 | 55 | 386 | 165-221 | 100% (g_iter0 2-0*) |
| 96 | Vinceyou1.Player1 | 576 | 57 | 397 | 186-211 | 100% (g_iter0 2-0*) |
| 97 | toyat522.bot5 | 571 | 55 | 444 | 188-256 | 100% (g_iter0 2-0*) |
| 98 | addiesteward.elicompbot | 570 | 57 | 415 | 187-228 | 100% (g_iter0 5-0*) |
| 99 | michael-tyl.cc_v0_5_0_6 | 548 | 56 | 461 | 211-250 | 100% (g_iter0 2-0*) |
| 100 | Chahat08.lazarus | 531 | 57 | 429 | 195-234 | 100% (g_iter0 2-0*) |
| 101 | Swordman51.AdeptusAstartes2 | 522 | 58 | 418 | 202-216 | 100% (g_iter0 2-0*) |
| 102 | monmouth-college-cs.elicompbot | 497 | 57 | 449 | 196-253 | 100% (g_iter0 2-0*) |
| 103 | anicolao.jumbled | 407 | 61 | 440 | 201-239 | 100% (g_iter0 5-0*) |
| 104 | ShatterXD.SRNNbot | 393 | 62 | 422 | 201-221 | 100% (g_iter0 2-0*) |
| 105 | NotLLeon.player | 152 | 76 | 405 | 184-221 | 100% (g_iter0 2-0*) |
| 106 | CodeClash-ai.mysubmission | 72 | 79 | 436 | 190-246 | 100% (g_iter0 2-0*) |
| 107 | addiesteward.NDeClaw | 54 | 81 | 395 | 170-225 | 100% (g_iter0 5-0*) |
| 108 | Yooncw0223.lec3player | -249 | 93 | 370 | 62-308 | 100% (g_iter0 5-0*) |
| 109 | andrewkbank.First | -308 | 98 | 285 | 42-243 | 100% (g_iter0 2-0*) |
