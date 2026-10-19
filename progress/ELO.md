# Ladder

25581 games (6954 ours, 6 of the stock examplefuncsplayer, 18621 between field bots on the ladder replica), 24848 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 133 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_loose1 | 2070 +- 61 | 5 of 132 | 196 | 129-67 | 91.5% | 39.0% (vs 4) |
| c_rot1 | 2017 +- 90 | 9 of 132 | 100 | 72-28 | 89.9% | 38.0% (vs 7) |
| c_hunt1 | 2006 +- 90 | 11 of 132 | 100 | 71-29 | 89.6% | 38.1% (vs 8) |
| c_di1 | 2006 +- 90 | 12 of 132 | 100 | 71-29 | 89.6% | 38.1% (vs 8) |
| c_gp1 | 1997 +- 58 | 13 of 132 | 205 | 126-79 | 89.3% | 36.9% (vs 8) |
| c_hr1 | 1983 +- 59 | 16 of 132 | 195 | 114-81 | 88.8% | 37.8% (vs 10) |
| c_expl1 | 1972 +- 88 | 18 of 132 | 100 | 68-32 | 88.4% | 37.6% (vs 11) |
| c_adlo2 | 1972 +- 88 | 19 of 132 | 100 | 68-32 | 88.4% | 37.6% (vs 11) |
| c_pack1 | 1961 +- 88 | 20 of 132 | 100 | 67-33 | 88.1% | 36.2% (vs 11) |
| c_isle1 | 1948 +- 48 | 21 of 132 | 303 | 165-138 | 87.6% | 34.5% (vs 11) |
| c_well5 | 1928 +- 87 | 22 of 132 | 100 | 64-36 | 86.9% | 32.1% (vs 11) |
| c_tune1 | 1918 +- 86 | 23 of 132 | 100 | 63-37 | 86.5% | 30.9% (vs 11) |
| c_blind1 | 1918 +- 86 | 24 of 132 | 100 | 63-37 | 86.5% | 30.9% (vs 11) |
| c_blind2 | 1918 +- 86 | 25 of 132 | 100 | 63-37 | 86.5% | 30.9% (vs 11) |
| c_well10 | 1907 +- 86 | 27 of 132 | 100 | 62-38 | 86.1% | 31.3% (vs 12) |
| c_mid1 | 1907 +- 86 | 28 of 132 | 100 | 62-38 | 86.1% | 31.3% (vs 12) |
| c_mend3 | 1896 +- 86 | 29 of 132 | 100 | 61-39 | 85.8% | 30.1% (vs 12) |
| c_spread2 | 1896 +- 86 | 30 of 132 | 100 | 61-39 | 85.8% | 30.1% (vs 12) |
| c_bc3 | 1896 +- 86 | 31 of 132 | 100 | 61-39 | 85.8% | 30.1% (vs 12) |
| c_scout1 | 1886 +- 86 | 32 of 132 | 100 | 60-40 | 85.4% | 28.8% (vs 12) |
| c_thr1 | 1886 +- 86 | 33 of 132 | 100 | 60-40 | 85.4% | 28.8% (vs 12) |
| c_well7 | 1886 +- 86 | 34 of 132 | 100 | 60-40 | 85.4% | 28.8% (vs 12) |
| c_cap1 | 1875 +- 86 | 35 of 132 | 100 | 59-41 | 85.0% | 27.7% (vs 12) |
| c_seam1 | 1875 +- 86 | 36 of 132 | 100 | 59-41 | 85.0% | 27.7% (vs 12) |
| c_seam2 | 1875 +- 86 | 37 of 132 | 100 | 59-41 | 85.0% | 27.7% (vs 12) |
| c_mend2 | 1871 +- 38 | 38 of 132 | 612 | 362-250 | 84.8% | 27.2% (vs 12) |
| c_def3 | 1870 +- 59 | 39 of 132 | 199 | 120-79 | 84.8% | 27.1% (vs 12) |
| c_bc1 | 1870 +- 65 | 40 of 132 | 164 | 97-67 | 84.8% | 27.1% (vs 12) |
| c_well9 | 1865 +- 52 | 41 of 132 | 260 | 138-122 | 84.6% | 26.6% (vs 12) |
| c_siege1 | 1865 +- 86 | 42 of 132 | 100 | 58-42 | 84.6% | 26.5% (vs 12) |
| c_end2 | 1854 +- 85 | 43 of 132 | 100 | 57-43 | 84.2% | 25.4% (vs 12) |
| c_open1 | 1844 +- 85 | 44 of 132 | 100 | 56-44 | 83.7% | 24.3% (vs 12) |
| c_flee3 | 1844 +- 85 | 45 of 132 | 100 | 56-44 | 83.7% | 24.3% (vs 12) |
| c_anc3 | 1841 +- 65 | 46 of 132 | 163 | 88-75 | 83.6% | 24.1% (vs 12) |
| c_aura2 | 1841 +- 48 | 47 of 132 | 314 | 162-152 | 83.6% | 24.0% (vs 12) |
| c_nav5 | 1782 +- 75 | 49 of 132 | 126 | 61-65 | 81.2% | 20.8% (vs 13) |
| c_nav6 | 1767 +- 74 | 51 of 132 | 129 | 58-71 | 80.6% | 21.5% (vs 14) |
| c_nav4 | 1744 +- 56 | 53 of 132 | 221 | 108-113 | 79.6% | 21.5% (vs 15) |
| c_swarm1 | 1663 +- 52 | 58 of 132 | 271 | 128-143 | 76.0% | 21.9% (vs 19) |
| c_line8a | 1621 +- 75 | 62 of 132 | 139 | 47-92 | 74.0% | 22.2% (vs 22) |
| g_iter0 | 1601 +- 52 | 63 of 132 | 456 | 230-226 | 73.0% | 20.6% (vs 22) |
| c_line6 | 1583 +- 91 | 65 of 132 | 100 | 32-68 | 72.1% | 20.4% (vs 23) |
| c_line7m | 1570 +- 92 | 66 of 132 | 100 | 31-69 | 71.5% | 19.5% (vs 23) |
| c_line5 | 1532 +- 94 | 72 of 132 | 100 | 28-72 | 69.6% | 21.9% (vs 28) |
| c_line4 | 1492 +- 97 | 74 of 132 | 100 | 25-75 | 67.6% | 19.8% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_loose1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2173 | 54 | 282 | 190-92 | 67% (c_loose1 2-1*) |
| 2 | awesomelemonade.finalBot | 2154 | 39 | 740 | 563-177 | 26% (c_loose1 5-14*) |
| 3 | IvanGeffner.fortytwo | 2138 | 51 | 315 | 204-111 | 33% (c_gp1 1-2*) |
| 4 | carlguo866.submit26_final | 2127 | 51 | 307 | 190-117 | 33% (c_loose1 5-10*) |
| 5 | **us:c_loose1** | 2070 | 61 | 196 | 129-67 |  |
| 6 | vrangr1.AFinalsBot | 2070 | 36 | 748 | 513-235 | 62% (c_loose1 8-5*) |
| 7 | AnOvercookedFork.quals | 2044 | 47 | 345 | 210-135 | 50% (c_loose1 3-3*) |
| 8 | georgezhang02.FB_ZZZ | 2022 | 45 | 388 | 241-147 | 56% (c_loose1 5-4*) |
| 9 | **us:c_rot1** | 2017 | 90 | 100 | 72-28 |  |
| 10 | pranayagra.finalbotfinaltwo | 2010 | 47 | 357 | 217-140 | 67% (c_loose1 6-3*) |
| 11 | **us:c_hunt1** | 2006 | 90 | 100 | 71-29 |  |
| 12 | **us:c_di1** | 2006 | 90 | 100 | 71-29 |  |
| 13 | **us:c_gp1** | 1997 | 58 | 205 | 126-79 |  |
| 14 | pranayagra.finalbotfinal | 1995 | 33 | 919 | 564-355 | 68% (c_loose1 21-10) |
| 15 | battlecode-archive.sprintBot | 1988 | 44 | 405 | 238-167 | 56% (c_loose1 5-4*) |
| 16 | **us:c_hr1** | 1983 | 59 | 195 | 114-81 |  |
| 17 | jmerle.camel_case_v30_final | 1973 | 33 | 866 | 531-335 | 54% (c_loose1 7-6*) |
| 18 | **us:c_expl1** | 1972 | 88 | 100 | 68-32 |  |
| 19 | **us:c_adlo2** | 1972 | 88 | 100 | 68-32 |  |
| 20 | **us:c_pack1** | 1961 | 88 | 100 | 67-33 |  |
| 21 | **us:c_isle1** | 1948 | 48 | 303 | 165-138 |  |
| 22 | **us:c_well5** | 1928 | 87 | 100 | 64-36 |  |
| 23 | **us:c_tune1** | 1918 | 86 | 100 | 63-37 |  |
| 24 | **us:c_blind1** | 1918 | 86 | 100 | 63-37 |  |
| 25 | **us:c_blind2** | 1918 | 86 | 100 | 63-37 |  |
| 26 | CyrilSharma.finalBot | 1908 | 41 | 488 | 275-213 | 67% (c_loose1 6-3*) |
| 27 | **us:c_well10** | 1907 | 86 | 100 | 62-38 |  |
| 28 | **us:c_mid1** | 1907 | 86 | 100 | 62-38 |  |
| 29 | **us:c_mend3** | 1896 | 86 | 100 | 61-39 |  |
| 30 | **us:c_spread2** | 1896 | 86 | 100 | 61-39 |  |
| 31 | **us:c_bc3** | 1896 | 86 | 100 | 61-39 |  |
| 32 | **us:c_scout1** | 1886 | 86 | 100 | 60-40 |  |
| 33 | **us:c_thr1** | 1886 | 86 | 100 | 60-40 |  |
| 34 | **us:c_well7** | 1886 | 86 | 100 | 60-40 |  |
| 35 | **us:c_cap1** | 1875 | 86 | 100 | 59-41 |  |
| 36 | **us:c_seam1** | 1875 | 86 | 100 | 59-41 |  |
| 37 | **us:c_seam2** | 1875 | 86 | 100 | 59-41 |  |
| 38 | **us:c_mend2** | 1871 | 38 | 612 | 362-250 |  |
| 39 | **us:c_def3** | 1870 | 59 | 199 | 120-79 |  |
| 40 | **us:c_bc1** | 1870 | 65 | 164 | 97-67 |  |
| 41 | **us:c_well9** | 1865 | 52 | 260 | 138-122 |  |
| 42 | **us:c_siege1** | 1865 | 86 | 100 | 58-42 |  |
| 43 | **us:c_end2** | 1854 | 85 | 100 | 57-43 |  |
| 44 | **us:c_open1** | 1844 | 85 | 100 | 56-44 |  |
| 45 | **us:c_flee3** | 1844 | 85 | 100 | 56-44 |  |
| 46 | **us:c_anc3** | 1841 | 65 | 163 | 88-75 |  |
| 47 | **us:c_aura2** | 1841 | 48 | 314 | 162-152 |  |
| 48 | ethanlabelle.dev | 1801 | 40 | 455 | 248-207 | 33% (c_isle1 1-2*) |
| 49 | **us:c_nav5** | 1782 | 75 | 126 | 61-65 |  |
| 50 | NotLLeon.v7 | 1780 | 32 | 883 | 407-476 | 90% (c_loose1 9-1*) |
| 51 | **us:c_nav6** | 1767 | 74 | 129 | 58-71 |  |
| 52 | georgezhang02.CB_tuning2 | 1755 | 32 | 896 | 395-501 | 90% (c_loose1 9-1*) |
| 53 | **us:c_nav4** | 1744 | 56 | 221 | 108-113 |  |
| 54 | britacatalin.FinalBot | 1697 | 33 | 840 | 339-501 | 90% (c_loose1 9-1*) |
| 55 | ethanlabelle.v19 | 1684 | 41 | 441 | 219-222 | 83% (c_well9 5-1*) |
| 56 | VarunVejalla.karel | 1680 | 41 | 457 | 234-223 | 67% (c_gp1 2-1*) |
| 57 | GabeG888.v8 | 1674 | 43 | 368 | 206-162 | 67% (c_well9 2-1*) |
| 58 | **us:c_swarm1** | 1663 | 52 | 271 | 128-143 |  |
| 59 | VarunVejalla.ali8 | 1653 | 45 | 355 | 195-160 | 83% (c_mend2 5-1*) |
| 60 | GabeG888.v8o1 | 1652 | 43 | 369 | 208-161 | 33% (c_well9 1-2*) |
| 61 | programjames.fourthbot | 1649 | 43 | 375 | 200-175 | 64% (c_mend2 7-4*) |
| 62 | **us:c_line8a** | 1621 | 75 | 139 | 47-92 |  |
| 63 | **us:g_iter0** | 1601 | 52 | 456 | 230-226 |  |
| 64 | DannyZhang686.pqual2 | 1586 | 42 | 406 | 213-193 | 83% (c_mend2 5-1*) |
| 65 | **us:c_line6** | 1583 | 91 | 100 | 32-68 |  |
| 66 | **us:c_line7m** | 1570 | 92 | 100 | 31-69 |  |
| 67 | NicholasKelly15.gopher10 | 1570 | 45 | 348 | 191-157 | 100% (c_anc3 3-0*) |
| 68 | louishu17.louisv10 | 1565 | 45 | 356 | 189-167 | 100% (c_bc1 3-0*) |
| 69 | louishu17.wouisv8 | 1558 | 44 | 380 | 195-185 | 83% (c_aura2 5-1*) |
| 70 | SampleProvider.SPAARK | 1557 | 44 | 360 | 188-172 | 33% (c_anc3 1-2*) |
| 71 | reeceyang.v5anaconda | 1547 | 34 | 845 | 278-567 | 100% (c_loose1 10-0*) |
| 72 | **us:c_line5** | 1532 | 94 | 100 | 28-72 |  |
| 73 | battlecode-archive.Sprint1 | 1500 | 35 | 813 | 248-565 | 100% (c_loose1 10-0*) |
| 74 | **us:c_line4** | 1492 | 97 | 100 | 25-75 |  |
| 75 | ipince.bobby | 1437 | 46 | 343 | 177-166 | 67% (c_swarm1 2-1*) |
| 76 | SteamBlizzard.newVnewME | 1404 | 42 | 407 | 204-203 | 80% (g_iter0 4-1*) |
| 77 | legobridge.tacoplayer | 1390 | 44 | 397 | 189-208 | 100% (c_mend2 6-0*) |
| 78 | TheK098.qp1_7_sprint_1 | 1385 | 43 | 400 | 219-181 | 100% (c_mend2 6-0*) |
| 79 | polyllc.poly | 1361 | 47 | 338 | 168-170 | 100% (g_iter0 2-0*) |
| 80 | toyat522.bot5a | 1320 | 43 | 409 | 197-212 | 80% (g_iter0 4-1*) |
| 81 | ColtG5.rexv9 | 1314 | 42 | 415 | 205-210 | 100% (g_iter0 2-0*) |
| 82 | elgoldie.head_v5 | 1294 | 42 | 392 | 192-200 | 100% (g_iter0 2-0*) |
| 83 | DukeBas._main | 1290 | 43 | 411 | 222-189 | 100% (c_mend2 6-0*) |
| 84 | beaverbois.USQualifiers | 1278 | 43 | 391 | 209-182 | 50% (g_iter0 1-1*) |
| 85 | kevinli405.maggi3_2 | 1220 | 42 | 431 | 220-211 | 100% (g_iter0 2-0*) |
| 86 | Nawlej.PoonPoon | 1219 | 45 | 379 | 184-195 | 100% (g_iter0 2-0*) |
| 87 | yaonam.PoonPoonv4 | 1199 | 39 | 889 | 258-631 | 90% (c_loose1 9-1*) |
| 88 | BrysonJGalapon.friday | 1180 | 43 | 406 | 210-196 | 100% (g_iter0 2-0*) |
| 89 | nail-e.Barry | 1164 | 43 | 414 | 209-205 | 100% (g_iter0 2-0*) |
| 90 | kevinli405.maggi3 | 1159 | 44 | 419 | 210-209 | 100% (g_iter0 5-0*) |
| 91 | aj-chau.attempt1 | 1149 | 43 | 428 | 222-206 | 100% (g_iter0 5-0*) |
| 92 | mama4294.currentPlayer | 1116 | 43 | 431 | 216-215 | 100% (g_iter0 2-0*) |
| 93 | prisms-cs-club.prisms10 | 1111 | 43 | 429 | 216-213 | 100% (g_iter0 2-0*) |
| 94 | ipince.bobby_v2 | 1084 | 42 | 476 | 237-239 | 67% (c_swarm1 2-1*) |
| 95 | JfeMak.realplayer2 | 989 | 43 | 466 | 236-230 | 100% (g_iter0 2-0*) |
| 96 | bewuwy.deathbot4 | 989 | 42 | 508 | 251-257 | 100% (g_iter0 2-0*) |
| 97 | andrewgopher.gopherbot | 987 | 43 | 483 | 226-257 | 100% (g_iter0 2-0*) |
| 98 | BrysonJGalapon.aloha | 978 | 42 | 494 | 249-245 | 100% (c_swarm1 3-0*) |
| 99 | PSUtblock.sprint_four_player | 938 | 44 | 468 | 226-242 | 100% (g_iter0 2-0*) |
| 100 | SampleProvider.SPAARK_1_12_2023 | 912 | 44 | 508 | 264-244 | 100% (c_swarm1 3-0*) |
| 101 | Nawlej.PoonPoonv3 | 885 | 44 | 494 | 236-258 | 100% (g_iter0 5-0*) |
| 102 | SDainard-PDX.Team_Player | 875 | 45 | 452 | 211-241 | 100% (g_iter0 2-0*) |
| 103 | Juanbri02.matfisplayer1 | 867 | 44 | 496 | 247-249 | 100% (g_iter0 5-0*) |
| 104 | NolanChai.nolan_1 | 866 | 43 | 516 | 250-266 | 100% (g_iter0 2-0*) |
| 105 | andrewgopher.gopherbot1 | 847 | 45 | 471 | 220-251 | 100% (g_iter0 2-0*) |
| 106 | jyorkio.elicompbot | 825 | 45 | 478 | 231-247 | 100% (g_iter0 2-0*) |
| 107 | vontell.regressiongames | 746 | 45 | 505 | 245-260 | 100% (g_iter0 5-0*) |
| 108 | legobridge.kushalplayer | 736 | 47 | 456 | 218-238 | 100% (g_iter0 2-0*) |
| 109 | SteamBlizzard.Block | 674 | 47 | 522 | 244-278 | 100% (g_iter0 5-0*) |
| 110 | Patela171.Battlecode2023_Robot | 670 | 47 | 493 | 228-265 | 100% (g_iter0 2-0*) |
| 111 | ax-95174.MPAction | 641 | 48 | 499 | 225-274 | 100% (c_swarm1 3-0*) |
| 112 | nail-e.Dante | 600 | 48 | 526 | 266-260 | 100% (g_iter0 2-0*) |
| 113 | Chahat08.toph | 589 | 48 | 502 | 235-267 | 100% (g_iter0 2-0*) |
| 114 | JackLee9355.jackPlayer | 589 | 50 | 461 | 205-256 | 100% (g_iter0 2-0*) |
| 115 | michael-tyl.hqrewrite | 586 | 49 | 482 | 231-251 | 100% (g_iter0 2-0*) |
| 116 | mama4294.learningBot | 585 | 49 | 513 | 250-263 | 100% (g_iter0 2-0*) |
| 117 | team-remember-to-hydrate.sprint_1 | 529 | 50 | 517 | 237-280 | 100% (g_iter0 2-0*) |
| 118 | anicolao.submission | 527 | 49 | 546 | 254-292 | 100% (g_iter0 2-0*) |
| 119 | Vinceyou1.Player1 | 412 | 52 | 504 | 230-274 | 100% (g_iter0 2-0*) |
| 120 | addiesteward.elicompbot | 389 | 52 | 525 | 233-292 | 100% (g_iter0 5-0*) |
| 121 | michael-tyl.cc_v0_5_0_6 | 389 | 51 | 591 | 281-310 | 100% (g_iter0 2-0*) |
| 122 | toyat522.bot5 | 388 | 52 | 558 | 243-315 | 100% (g_iter0 2-0*) |
| 123 | Swordman51.AdeptusAstartes2 | 363 | 53 | 527 | 256-271 | 100% (g_iter0 2-0*) |
| 124 | Chahat08.lazarus | 353 | 53 | 543 | 249-294 | 100% (g_iter0 2-0*) |
| 125 | monmouth-college-cs.elicompbot | 319 | 53 | 563 | 248-315 | 100% (g_iter0 2-0*) |
| 126 | anicolao.jumbled | 241 | 56 | 549 | 257-292 | 100% (g_iter0 5-0*) |
| 127 | ShatterXD.SRNNbot | 213 | 57 | 546 | 263-283 | 100% (g_iter0 2-0*) |
| 128 | NotLLeon.player | -29 | 71 | 504 | 238-266 | 100% (g_iter0 2-0*) |
| 129 | CodeClash-ai.mysubmission | -123 | 74 | 531 | 243-288 | 100% (g_iter0 2-0*) |
| 130 | addiesteward.NDeClaw | -139 | 76 | 491 | 220-271 | 100% (g_iter0 5-0*) |
| 131 | Yooncw0223.lec3player | -451 | 87 | 459 | 83-376 | 100% (g_iter0 5-0*) |
| 132 | andrewkbank.First | -519 | 90 | 378 | 56-322 | 100% (g_iter0 2-0*) |
