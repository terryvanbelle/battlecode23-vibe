# Ladder

25353 games (6858 ours, 6 of the stock examplefuncsplayer, 18489 between field bots on the ladder replica), 24627 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 133 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_loose1 | 2103 +- 96 | 5 of 132 | 100 | 79-21 | 92.5% | 43.9% (vs 4) |
| c_rot1 | 2017 +- 90 | 9 of 132 | 100 | 72-28 | 89.9% | 38.3% (vs 7) |
| c_hunt1 | 2005 +- 89 | 11 of 132 | 100 | 71-29 | 89.6% | 38.3% (vs 8) |
| c_di1 | 2005 +- 89 | 12 of 132 | 100 | 71-29 | 89.6% | 38.3% (vs 8) |
| c_gp1 | 1996 +- 58 | 13 of 132 | 205 | 126-79 | 89.3% | 37.1% (vs 8) |
| c_hr1 | 1982 +- 59 | 16 of 132 | 195 | 114-81 | 88.8% | 38.0% (vs 10) |
| c_expl1 | 1971 +- 88 | 18 of 132 | 100 | 68-32 | 88.5% | 37.8% (vs 11) |
| c_adlo2 | 1971 +- 88 | 19 of 132 | 100 | 68-32 | 88.5% | 37.8% (vs 11) |
| c_pack1 | 1960 +- 88 | 20 of 132 | 100 | 67-33 | 88.1% | 36.4% (vs 11) |
| c_isle1 | 1947 +- 48 | 21 of 132 | 303 | 165-138 | 87.6% | 34.6% (vs 11) |
| c_well5 | 1928 +- 87 | 22 of 132 | 100 | 64-36 | 86.9% | 32.3% (vs 11) |
| c_tune1 | 1917 +- 86 | 23 of 132 | 100 | 63-37 | 86.6% | 31.0% (vs 11) |
| c_blind1 | 1917 +- 86 | 24 of 132 | 100 | 63-37 | 86.6% | 31.0% (vs 11) |
| c_blind2 | 1917 +- 86 | 25 of 132 | 100 | 63-37 | 86.6% | 31.0% (vs 11) |
| c_well10 | 1907 +- 86 | 26 of 132 | 100 | 62-38 | 86.2% | 29.8% (vs 11) |
| c_mid1 | 1907 +- 86 | 27 of 132 | 100 | 62-38 | 86.2% | 29.8% (vs 11) |
| c_bc3 | 1896 +- 86 | 29 of 132 | 100 | 61-39 | 85.8% | 30.2% (vs 12) |
| c_spread2 | 1896 +- 86 | 30 of 132 | 100 | 61-39 | 85.8% | 30.2% (vs 12) |
| c_mend3 | 1896 +- 86 | 31 of 132 | 100 | 61-39 | 85.8% | 30.2% (vs 12) |
| c_scout1 | 1886 +- 86 | 32 of 132 | 100 | 60-40 | 85.4% | 29.0% (vs 12) |
| c_well7 | 1886 +- 86 | 33 of 132 | 100 | 60-40 | 85.4% | 29.0% (vs 12) |
| c_thr1 | 1886 +- 86 | 34 of 132 | 100 | 60-40 | 85.4% | 29.0% (vs 12) |
| c_seam1 | 1875 +- 86 | 35 of 132 | 100 | 59-41 | 85.0% | 27.8% (vs 12) |
| c_seam2 | 1875 +- 86 | 36 of 132 | 100 | 59-41 | 85.0% | 27.8% (vs 12) |
| c_cap1 | 1875 +- 86 | 37 of 132 | 100 | 59-41 | 85.0% | 27.8% (vs 12) |
| c_mend2 | 1871 +- 38 | 38 of 132 | 612 | 362-250 | 84.8% | 27.3% (vs 12) |
| c_def3 | 1870 +- 59 | 39 of 132 | 199 | 120-79 | 84.8% | 27.3% (vs 12) |
| c_bc1 | 1870 +- 65 | 40 of 132 | 164 | 97-67 | 84.8% | 27.2% (vs 12) |
| c_well9 | 1865 +- 52 | 41 of 132 | 260 | 138-122 | 84.6% | 26.7% (vs 12) |
| c_siege1 | 1865 +- 86 | 42 of 132 | 100 | 58-42 | 84.6% | 26.7% (vs 12) |
| c_end2 | 1854 +- 85 | 43 of 132 | 100 | 57-43 | 84.2% | 25.5% (vs 12) |
| c_open1 | 1844 +- 85 | 44 of 132 | 100 | 56-44 | 83.8% | 24.5% (vs 12) |
| c_flee3 | 1844 +- 85 | 45 of 132 | 100 | 56-44 | 83.8% | 24.5% (vs 12) |
| c_anc3 | 1841 +- 65 | 46 of 132 | 163 | 88-75 | 83.7% | 24.2% (vs 12) |
| c_aura2 | 1840 +- 48 | 47 of 132 | 314 | 162-152 | 83.6% | 24.1% (vs 12) |
| c_nav5 | 1782 +- 75 | 49 of 132 | 126 | 61-65 | 81.2% | 20.9% (vs 13) |
| c_nav6 | 1767 +- 74 | 51 of 132 | 129 | 58-71 | 80.6% | 21.6% (vs 14) |
| c_nav4 | 1744 +- 56 | 53 of 132 | 221 | 108-113 | 79.6% | 21.5% (vs 15) |
| c_swarm1 | 1663 +- 52 | 58 of 132 | 271 | 128-143 | 76.0% | 21.9% (vs 19) |
| c_line8a | 1621 +- 75 | 62 of 132 | 139 | 47-92 | 74.0% | 22.2% (vs 22) |
| g_iter0 | 1601 +- 52 | 63 of 132 | 456 | 230-226 | 73.0% | 20.6% (vs 22) |
| c_line6 | 1582 +- 91 | 65 of 132 | 100 | 32-68 | 72.1% | 20.5% (vs 23) |
| c_line7m | 1570 +- 92 | 67 of 132 | 100 | 31-69 | 71.5% | 20.8% (vs 24) |
| c_line5 | 1532 +- 94 | 72 of 132 | 100 | 28-72 | 69.6% | 21.9% (vs 28) |
| c_line4 | 1492 +- 97 | 74 of 132 | 100 | 25-75 | 67.6% | 19.8% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_loose1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2173 | 54 | 279 | 189-90 | 22% (c_mend2 2-7*) |
| 2 | awesomelemonade.finalBot | 2150 | 39 | 731 | 555-176 | 40% (c_loose1 4-6*) |
| 3 | IvanGeffner.fortytwo | 2136 | 51 | 315 | 204-111 | 33% (c_gp1 1-2*) |
| 4 | carlguo866.submit26_final | 2122 | 52 | 292 | 180-112 | 0% (c_mend2 0-3*) |
| 5 | **us:c_loose1** | 2103 | 96 | 100 | 79-21 |  |
| 6 | vrangr1.AFinalsBot | 2069 | 37 | 745 | 511-234 | 70% (c_loose1 7-3*) |
| 7 | AnOvercookedFork.quals | 2040 | 48 | 336 | 204-132 | 56% (c_isle1 5-4*) |
| 8 | georgezhang02.FB_ZZZ | 2021 | 45 | 379 | 237-142 | 29% (c_isle1 6-15*) |
| 9 | **us:c_rot1** | 2017 | 90 | 100 | 72-28 |  |
| 10 | pranayagra.finalbotfinaltwo | 2011 | 47 | 348 | 214-134 | 44% (c_isle1 4-5*) |
| 11 | **us:c_hunt1** | 2005 | 89 | 100 | 71-29 |  |
| 12 | **us:c_di1** | 2005 | 89 | 100 | 71-29 |  |
| 13 | **us:c_gp1** | 1996 | 58 | 205 | 126-79 |  |
| 14 | pranayagra.finalbotfinal | 1996 | 33 | 898 | 557-341 | 70% (c_loose1 7-3*) |
| 15 | battlecode-archive.sprintBot | 1985 | 45 | 393 | 232-161 | 49% (c_isle1 18-19) |
| 16 | **us:c_hr1** | 1982 | 59 | 195 | 114-81 |  |
| 17 | jmerle.camel_case_v30_final | 1974 | 33 | 860 | 529-331 | 50% (c_loose1 5-5*) |
| 18 | **us:c_expl1** | 1971 | 88 | 100 | 68-32 |  |
| 19 | **us:c_adlo2** | 1971 | 88 | 100 | 68-32 |  |
| 20 | **us:c_pack1** | 1960 | 88 | 100 | 67-33 |  |
| 21 | **us:c_isle1** | 1947 | 48 | 303 | 165-138 |  |
| 22 | **us:c_well5** | 1928 | 87 | 100 | 64-36 |  |
| 23 | **us:c_tune1** | 1917 | 86 | 100 | 63-37 |  |
| 24 | **us:c_blind1** | 1917 | 86 | 100 | 63-37 |  |
| 25 | **us:c_blind2** | 1917 | 86 | 100 | 63-37 |  |
| 26 | **us:c_well10** | 1907 | 86 | 100 | 62-38 |  |
| 27 | **us:c_mid1** | 1907 | 86 | 100 | 62-38 |  |
| 28 | CyrilSharma.finalBot | 1906 | 41 | 473 | 269-204 | 49% (c_isle1 19-20) |
| 29 | **us:c_bc3** | 1896 | 86 | 100 | 61-39 |  |
| 30 | **us:c_spread2** | 1896 | 86 | 100 | 61-39 |  |
| 31 | **us:c_mend3** | 1896 | 86 | 100 | 61-39 |  |
| 32 | **us:c_scout1** | 1886 | 86 | 100 | 60-40 |  |
| 33 | **us:c_well7** | 1886 | 86 | 100 | 60-40 |  |
| 34 | **us:c_thr1** | 1886 | 86 | 100 | 60-40 |  |
| 35 | **us:c_seam1** | 1875 | 86 | 100 | 59-41 |  |
| 36 | **us:c_seam2** | 1875 | 86 | 100 | 59-41 |  |
| 37 | **us:c_cap1** | 1875 | 86 | 100 | 59-41 |  |
| 38 | **us:c_mend2** | 1871 | 38 | 612 | 362-250 |  |
| 39 | **us:c_def3** | 1870 | 59 | 199 | 120-79 |  |
| 40 | **us:c_bc1** | 1870 | 65 | 164 | 97-67 |  |
| 41 | **us:c_well9** | 1865 | 52 | 260 | 138-122 |  |
| 42 | **us:c_siege1** | 1865 | 86 | 100 | 58-42 |  |
| 43 | **us:c_end2** | 1854 | 85 | 100 | 57-43 |  |
| 44 | **us:c_open1** | 1844 | 85 | 100 | 56-44 |  |
| 45 | **us:c_flee3** | 1844 | 85 | 100 | 56-44 |  |
| 46 | **us:c_anc3** | 1841 | 65 | 163 | 88-75 |  |
| 47 | **us:c_aura2** | 1840 | 48 | 314 | 162-152 |  |
| 48 | ethanlabelle.dev | 1802 | 41 | 449 | 246-203 | 33% (c_isle1 1-2*) |
| 49 | **us:c_nav5** | 1782 | 75 | 126 | 61-65 |  |
| 50 | NotLLeon.v7 | 1781 | 32 | 881 | 406-475 | 90% (c_loose1 9-1*) |
| 51 | **us:c_nav6** | 1767 | 74 | 129 | 58-71 |  |
| 52 | georgezhang02.CB_tuning2 | 1756 | 32 | 890 | 393-497 | 90% (c_loose1 9-1*) |
| 53 | **us:c_nav4** | 1744 | 56 | 221 | 108-113 |  |
| 54 | britacatalin.FinalBot | 1697 | 33 | 840 | 339-501 | 90% (c_loose1 9-1*) |
| 55 | ethanlabelle.v19 | 1682 | 41 | 438 | 217-221 | 83% (c_well9 5-1*) |
| 56 | VarunVejalla.karel | 1679 | 41 | 455 | 233-222 | 67% (c_gp1 2-1*) |
| 57 | GabeG888.v8 | 1672 | 44 | 366 | 204-162 | 67% (c_well9 2-1*) |
| 58 | **us:c_swarm1** | 1663 | 52 | 271 | 128-143 |  |
| 59 | VarunVejalla.ali8 | 1652 | 45 | 355 | 195-160 | 83% (c_mend2 5-1*) |
| 60 | GabeG888.v8o1 | 1652 | 43 | 369 | 208-161 | 33% (c_well9 1-2*) |
| 61 | programjames.fourthbot | 1651 | 43 | 373 | 200-173 | 64% (c_mend2 7-4*) |
| 62 | **us:c_line8a** | 1621 | 75 | 139 | 47-92 |  |
| 63 | **us:g_iter0** | 1601 | 52 | 456 | 230-226 |  |
| 64 | DannyZhang686.pqual2 | 1586 | 42 | 406 | 213-193 | 83% (c_mend2 5-1*) |
| 65 | **us:c_line6** | 1582 | 91 | 100 | 32-68 |  |
| 66 | NicholasKelly15.gopher10 | 1571 | 45 | 345 | 190-155 | 100% (c_anc3 3-0*) |
| 67 | **us:c_line7m** | 1570 | 92 | 100 | 31-69 |  |
| 68 | louishu17.louisv10 | 1565 | 45 | 356 | 189-167 | 100% (c_bc1 3-0*) |
| 69 | SampleProvider.SPAARK | 1560 | 45 | 354 | 186-168 | 33% (c_anc3 1-2*) |
| 70 | louishu17.wouisv8 | 1554 | 44 | 377 | 192-185 | 83% (c_aura2 5-1*) |
| 71 | reeceyang.v5anaconda | 1546 | 34 | 839 | 274-565 | 100% (c_loose1 10-0*) |
| 72 | **us:c_line5** | 1532 | 94 | 100 | 28-72 |  |
| 73 | battlecode-archive.Sprint1 | 1500 | 35 | 813 | 248-565 | 100% (c_loose1 10-0*) |
| 74 | **us:c_line4** | 1492 | 97 | 100 | 25-75 |  |
| 75 | ipince.bobby | 1434 | 46 | 337 | 173-164 | 67% (c_swarm1 2-1*) |
| 76 | SteamBlizzard.newVnewME | 1404 | 42 | 407 | 204-203 | 80% (g_iter0 4-1*) |
| 77 | legobridge.tacoplayer | 1391 | 44 | 397 | 189-208 | 100% (c_mend2 6-0*) |
| 78 | TheK098.qp1_7_sprint_1 | 1388 | 43 | 397 | 219-178 | 100% (c_mend2 6-0*) |
| 79 | polyllc.poly | 1359 | 47 | 335 | 165-170 | 100% (g_iter0 2-0*) |
| 80 | toyat522.bot5a | 1319 | 43 | 406 | 196-210 | 80% (g_iter0 4-1*) |
| 81 | ColtG5.rexv9 | 1314 | 42 | 412 | 203-209 | 100% (g_iter0 2-0*) |
| 82 | elgoldie.head_v5 | 1295 | 42 | 392 | 192-200 | 100% (g_iter0 2-0*) |
| 83 | DukeBas._main | 1290 | 43 | 411 | 222-189 | 100% (c_mend2 6-0*) |
| 84 | beaverbois.USQualifiers | 1279 | 43 | 391 | 209-182 | 50% (g_iter0 1-1*) |
| 85 | Nawlej.PoonPoon | 1221 | 45 | 376 | 183-193 | 100% (g_iter0 2-0*) |
| 86 | kevinli405.maggi3_2 | 1221 | 42 | 429 | 219-210 | 100% (g_iter0 2-0*) |
| 87 | yaonam.PoonPoonv4 | 1198 | 39 | 881 | 253-628 | 90% (c_loose1 9-1*) |
| 88 | BrysonJGalapon.friday | 1184 | 43 | 400 | 209-191 | 100% (g_iter0 2-0*) |
| 89 | nail-e.Barry | 1163 | 43 | 409 | 206-203 | 100% (g_iter0 2-0*) |
| 90 | kevinli405.maggi3 | 1160 | 44 | 414 | 209-205 | 100% (g_iter0 5-0*) |
| 91 | aj-chau.attempt1 | 1149 | 43 | 425 | 221-204 | 100% (g_iter0 5-0*) |
| 92 | prisms-cs-club.prisms10 | 1114 | 44 | 423 | 214-209 | 100% (g_iter0 2-0*) |
| 93 | mama4294.currentPlayer | 1113 | 43 | 428 | 213-215 | 100% (g_iter0 2-0*) |
| 94 | ipince.bobby_v2 | 1084 | 42 | 473 | 235-238 | 67% (c_swarm1 2-1*) |
| 95 | bewuwy.deathbot4 | 988 | 42 | 502 | 248-254 | 100% (g_iter0 2-0*) |
| 96 | JfeMak.realplayer2 | 988 | 43 | 463 | 233-230 | 100% (g_iter0 2-0*) |
| 97 | andrewgopher.gopherbot | 985 | 43 | 474 | 219-255 | 100% (g_iter0 2-0*) |
| 98 | BrysonJGalapon.aloha | 978 | 43 | 491 | 248-243 | 100% (c_swarm1 3-0*) |
| 99 | PSUtblock.sprint_four_player | 936 | 45 | 459 | 220-239 | 100% (g_iter0 2-0*) |
| 100 | SampleProvider.SPAARK_1_12_2023 | 913 | 44 | 505 | 263-242 | 100% (c_swarm1 3-0*) |
| 101 | Nawlej.PoonPoonv3 | 886 | 44 | 494 | 236-258 | 100% (g_iter0 5-0*) |
| 102 | SDainard-PDX.Team_Player | 876 | 45 | 452 | 211-241 | 100% (g_iter0 2-0*) |
| 103 | Juanbri02.matfisplayer1 | 872 | 44 | 490 | 246-244 | 100% (g_iter0 5-0*) |
| 104 | NolanChai.nolan_1 | 869 | 43 | 510 | 250-260 | 100% (g_iter0 2-0*) |
| 105 | andrewgopher.gopherbot1 | 847 | 45 | 465 | 215-250 | 100% (g_iter0 2-0*) |
| 106 | jyorkio.elicompbot | 827 | 45 | 475 | 230-245 | 100% (g_iter0 2-0*) |
| 107 | vontell.regressiongames | 745 | 45 | 502 | 243-259 | 100% (g_iter0 5-0*) |
| 108 | legobridge.kushalplayer | 739 | 47 | 453 | 217-236 | 100% (g_iter0 2-0*) |
| 109 | SteamBlizzard.Block | 675 | 47 | 516 | 240-276 | 100% (g_iter0 5-0*) |
| 110 | Patela171.Battlecode2023_Robot | 672 | 47 | 490 | 227-263 | 100% (g_iter0 2-0*) |
| 111 | ax-95174.MPAction | 641 | 48 | 499 | 225-274 | 100% (c_swarm1 3-0*) |
| 112 | nail-e.Dante | 601 | 48 | 526 | 266-260 | 100% (g_iter0 2-0*) |
| 113 | michael-tyl.hqrewrite | 589 | 49 | 479 | 231-248 | 100% (g_iter0 2-0*) |
| 114 | Chahat08.toph | 589 | 49 | 499 | 232-267 | 100% (g_iter0 2-0*) |
| 115 | JackLee9355.jackPlayer | 588 | 51 | 458 | 203-255 | 100% (g_iter0 2-0*) |
| 116 | mama4294.learningBot | 584 | 49 | 504 | 245-259 | 100% (g_iter0 2-0*) |
| 117 | team-remember-to-hydrate.sprint_1 | 527 | 50 | 511 | 235-276 | 100% (g_iter0 2-0*) |
| 118 | anicolao.submission | 527 | 49 | 546 | 254-292 | 100% (g_iter0 2-0*) |
| 119 | Vinceyou1.Player1 | 411 | 52 | 501 | 228-273 | 100% (g_iter0 2-0*) |
| 120 | toyat522.bot5 | 390 | 52 | 552 | 242-310 | 100% (g_iter0 2-0*) |
| 121 | addiesteward.elicompbot | 389 | 52 | 525 | 233-292 | 100% (g_iter0 5-0*) |
| 122 | michael-tyl.cc_v0_5_0_6 | 389 | 52 | 585 | 278-307 | 100% (g_iter0 2-0*) |
| 123 | Swordman51.AdeptusAstartes2 | 363 | 53 | 527 | 256-271 | 100% (g_iter0 2-0*) |
| 124 | Chahat08.lazarus | 353 | 53 | 543 | 249-294 | 100% (g_iter0 2-0*) |
| 125 | monmouth-college-cs.elicompbot | 321 | 53 | 557 | 245-312 | 100% (g_iter0 2-0*) |
| 126 | anicolao.jumbled | 240 | 57 | 546 | 255-291 | 100% (g_iter0 5-0*) |
| 127 | ShatterXD.SRNNbot | 213 | 58 | 541 | 260-281 | 100% (g_iter0 2-0*) |
| 128 | NotLLeon.player | -29 | 71 | 504 | 238-266 | 100% (g_iter0 2-0*) |
| 129 | CodeClash-ai.mysubmission | -123 | 74 | 526 | 240-286 | 100% (g_iter0 2-0*) |
| 130 | addiesteward.NDeClaw | -136 | 76 | 490 | 220-270 | 100% (g_iter0 5-0*) |
| 131 | Yooncw0223.lec3player | -452 | 87 | 459 | 83-376 | 100% (g_iter0 5-0*) |
| 132 | andrewkbank.First | -521 | 91 | 374 | 55-319 | 100% (g_iter0 2-0*) |
