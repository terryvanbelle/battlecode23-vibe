# Ladder

27081 games (7425 ours, 6 of the stock examplefuncsplayer, 19650 between field bots on the ladder replica), 26253 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 136 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_adp1 | 2139 +- 102 | 3 of 135 | 100 | 83-17 | 93.9% | 49.0% (vs 2) |
| c_eco3 | 2098 +- 65 | 6 of 135 | 179 | 116-63 | 92.8% | 45.5% (vs 4) |
| c_sm1 | 2096 +- 97 | 7 of 135 | 100 | 80-20 | 92.8% | 45.3% (vs 4) |
| c_loose1 | 2049 +- 52 | 8 of 135 | 278 | 165-113 | 91.5% | 38.7% (vs 4) |
| c_rot1 | 1996 +- 90 | 13 of 135 | 100 | 72-28 | 89.9% | 39.4% (vs 8) |
| c_di1 | 1985 +- 89 | 14 of 135 | 100 | 71-29 | 89.5% | 37.9% (vs 8) |
| c_hunt1 | 1985 +- 89 | 15 of 135 | 100 | 71-29 | 89.5% | 37.9% (vs 8) |
| c_gp1 | 1977 +- 58 | 16 of 135 | 205 | 126-79 | 89.3% | 36.8% (vs 8) |
| c_hr1 | 1963 +- 59 | 19 of 135 | 195 | 114-81 | 88.8% | 37.8% (vs 10) |
| c_expl1 | 1951 +- 88 | 21 of 135 | 100 | 68-32 | 88.4% | 37.4% (vs 11) |
| c_adlo2 | 1951 +- 88 | 22 of 135 | 100 | 68-32 | 88.4% | 37.4% (vs 11) |
| c_pack1 | 1940 +- 88 | 23 of 135 | 100 | 67-33 | 88.0% | 36.0% (vs 11) |
| c_isle1 | 1928 +- 48 | 24 of 135 | 303 | 165-138 | 87.6% | 34.5% (vs 11) |
| c_well5 | 1907 +- 87 | 25 of 135 | 100 | 64-36 | 86.9% | 31.9% (vs 11) |
| c_blind2 | 1896 +- 86 | 26 of 135 | 100 | 63-37 | 86.5% | 30.6% (vs 11) |
| c_tune1 | 1896 +- 86 | 27 of 135 | 100 | 63-37 | 86.5% | 30.6% (vs 11) |
| c_blind1 | 1896 +- 86 | 28 of 135 | 100 | 63-37 | 86.5% | 30.6% (vs 11) |
| c_mid1 | 1886 +- 86 | 30 of 135 | 100 | 62-38 | 86.1% | 31.0% (vs 12) |
| c_well10 | 1886 +- 86 | 31 of 135 | 100 | 62-38 | 86.1% | 31.0% (vs 12) |
| c_spread2 | 1875 +- 86 | 32 of 135 | 100 | 61-39 | 85.7% | 29.8% (vs 12) |
| c_bc3 | 1875 +- 86 | 33 of 135 | 100 | 61-39 | 85.7% | 29.8% (vs 12) |
| c_mend3 | 1875 +- 86 | 34 of 135 | 100 | 61-39 | 85.7% | 29.8% (vs 12) |
| c_well7 | 1865 +- 86 | 35 of 135 | 100 | 60-40 | 85.3% | 28.6% (vs 12) |
| c_scout1 | 1865 +- 86 | 36 of 135 | 100 | 60-40 | 85.3% | 28.6% (vs 12) |
| c_thr1 | 1865 +- 86 | 37 of 135 | 100 | 60-40 | 85.3% | 28.6% (vs 12) |
| c_seam2 | 1854 +- 86 | 38 of 135 | 100 | 59-41 | 84.9% | 27.4% (vs 12) |
| c_seam1 | 1854 +- 86 | 39 of 135 | 100 | 59-41 | 84.9% | 27.4% (vs 12) |
| c_cap1 | 1854 +- 86 | 40 of 135 | 100 | 59-41 | 84.9% | 27.4% (vs 12) |
| c_def3 | 1849 +- 59 | 41 of 135 | 199 | 120-79 | 84.7% | 26.9% (vs 12) |
| c_mend2 | 1849 +- 37 | 42 of 135 | 612 | 362-250 | 84.7% | 26.9% (vs 12) |
| c_bc1 | 1849 +- 65 | 43 of 135 | 164 | 97-67 | 84.7% | 26.8% (vs 12) |
| c_well9 | 1844 +- 51 | 44 of 135 | 260 | 138-122 | 84.5% | 26.3% (vs 12) |
| c_siege1 | 1843 +- 85 | 45 of 135 | 100 | 58-42 | 84.5% | 26.3% (vs 12) |
| c_end2 | 1833 +- 85 | 46 of 135 | 100 | 57-43 | 84.1% | 25.2% (vs 12) |
| c_flee3 | 1823 +- 85 | 47 of 135 | 100 | 56-44 | 83.7% | 24.1% (vs 12) |
| c_open1 | 1823 +- 85 | 48 of 135 | 100 | 56-44 | 83.7% | 24.1% (vs 12) |
| c_anc3 | 1821 +- 65 | 49 of 135 | 163 | 88-75 | 83.6% | 23.9% (vs 12) |
| c_aura2 | 1820 +- 47 | 50 of 135 | 314 | 162-152 | 83.6% | 23.8% (vs 12) |
| c_nav5 | 1761 +- 75 | 52 of 135 | 126 | 61-65 | 81.2% | 20.7% (vs 13) |
| c_nav6 | 1746 +- 74 | 54 of 135 | 129 | 58-71 | 80.5% | 21.4% (vs 14) |
| c_nav4 | 1724 +- 56 | 56 of 135 | 221 | 108-113 | 79.6% | 21.5% (vs 15) |
| c_swarm1 | 1643 +- 52 | 61 of 135 | 271 | 128-143 | 75.9% | 22.0% (vs 19) |
| c_line8a | 1600 +- 74 | 65 of 135 | 139 | 47-92 | 73.9% | 22.3% (vs 22) |
| g_iter0 | 1582 +- 52 | 66 of 135 | 456 | 230-226 | 73.0% | 20.7% (vs 22) |
| c_line6 | 1561 +- 91 | 68 of 135 | 100 | 32-68 | 72.0% | 20.4% (vs 23) |
| c_line7m | 1549 +- 92 | 72 of 135 | 100 | 31-69 | 71.4% | 22.9% (vs 26) |
| c_line5 | 1511 +- 94 | 75 of 135 | 100 | 28-72 | 69.5% | 21.7% (vs 28) |
| c_line4 | 1471 +- 97 | 77 of 135 | 100 | 25-75 | 67.4% | 19.6% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_adp1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2152 | 50 | 321 | 212-109 | 35% (c_eco3 7-13*) |
| 2 | awesomelemonade.finalBot | 2140 | 37 | 818 | 611-207 | 40% (c_adp1 4-6*) |
| 3 | **us:c_adp1** | 2139 | 102 | 100 | 83-17 |  |
| 4 | carlguo866.submit26_final | 2115 | 46 | 381 | 234-147 | 38% (c_eco3 9-15*) |
| 5 | IvanGeffner.fortytwo | 2111 | 48 | 352 | 221-131 | 73% (c_eco3 11-4*) |
| 6 | **us:c_eco3** | 2098 | 65 | 179 | 116-63 |  |
| 7 | **us:c_sm1** | 2096 | 97 | 100 | 80-20 |  |
| 8 | **us:c_loose1** | 2049 | 52 | 278 | 165-113 |  |
| 9 | vrangr1.AFinalsBot | 2045 | 35 | 805 | 536-269 | 70% (c_adp1 7-3*) |
| 10 | AnOvercookedFork.quals | 2023 | 45 | 376 | 226-150 | 50% (c_loose1 9-9*) |
| 11 | georgezhang02.FB_ZZZ | 2003 | 43 | 412 | 254-158 | 56% (c_loose1 5-4*) |
| 12 | pranayagra.finalbotfinaltwo | 1997 | 45 | 379 | 231-148 | 67% (c_loose1 6-3*) |
| 13 | **us:c_rot1** | 1996 | 90 | 100 | 72-28 |  |
| 14 | **us:c_di1** | 1985 | 89 | 100 | 71-29 |  |
| 15 | **us:c_hunt1** | 1985 | 89 | 100 | 71-29 |  |
| 16 | **us:c_gp1** | 1977 | 58 | 205 | 126-79 |  |
| 17 | battlecode-archive.sprintBot | 1972 | 43 | 425 | 248-177 | 56% (c_loose1 5-4*) |
| 18 | pranayagra.finalbotfinal | 1971 | 32 | 979 | 583-396 | 80% (c_adp1 8-2*) |
| 19 | **us:c_hr1** | 1963 | 59 | 195 | 114-81 |  |
| 20 | jmerle.camel_case_v30_final | 1957 | 32 | 917 | 558-359 | 60% (c_adp1 6-4*) |
| 21 | **us:c_expl1** | 1951 | 88 | 100 | 68-32 |  |
| 22 | **us:c_adlo2** | 1951 | 88 | 100 | 68-32 |  |
| 23 | **us:c_pack1** | 1940 | 88 | 100 | 67-33 |  |
| 24 | **us:c_isle1** | 1928 | 48 | 303 | 165-138 |  |
| 25 | **us:c_well5** | 1907 | 87 | 100 | 64-36 |  |
| 26 | **us:c_blind2** | 1896 | 86 | 100 | 63-37 |  |
| 27 | **us:c_tune1** | 1896 | 86 | 100 | 63-37 |  |
| 28 | **us:c_blind1** | 1896 | 86 | 100 | 63-37 |  |
| 29 | CyrilSharma.finalBot | 1888 | 40 | 512 | 287-225 | 67% (c_loose1 6-3*) |
| 30 | **us:c_mid1** | 1886 | 86 | 100 | 62-38 |  |
| 31 | **us:c_well10** | 1886 | 86 | 100 | 62-38 |  |
| 32 | **us:c_spread2** | 1875 | 86 | 100 | 61-39 |  |
| 33 | **us:c_bc3** | 1875 | 86 | 100 | 61-39 |  |
| 34 | **us:c_mend3** | 1875 | 86 | 100 | 61-39 |  |
| 35 | **us:c_well7** | 1865 | 86 | 100 | 60-40 |  |
| 36 | **us:c_scout1** | 1865 | 86 | 100 | 60-40 |  |
| 37 | **us:c_thr1** | 1865 | 86 | 100 | 60-40 |  |
| 38 | **us:c_seam2** | 1854 | 86 | 100 | 59-41 |  |
| 39 | **us:c_seam1** | 1854 | 86 | 100 | 59-41 |  |
| 40 | **us:c_cap1** | 1854 | 86 | 100 | 59-41 |  |
| 41 | **us:c_def3** | 1849 | 59 | 199 | 120-79 |  |
| 42 | **us:c_mend2** | 1849 | 37 | 612 | 362-250 |  |
| 43 | **us:c_bc1** | 1849 | 65 | 164 | 97-67 |  |
| 44 | **us:c_well9** | 1844 | 51 | 260 | 138-122 |  |
| 45 | **us:c_siege1** | 1843 | 85 | 100 | 58-42 |  |
| 46 | **us:c_end2** | 1833 | 85 | 100 | 57-43 |  |
| 47 | **us:c_flee3** | 1823 | 85 | 100 | 56-44 |  |
| 48 | **us:c_open1** | 1823 | 85 | 100 | 56-44 |  |
| 49 | **us:c_anc3** | 1821 | 65 | 163 | 88-75 |  |
| 50 | **us:c_aura2** | 1820 | 47 | 314 | 162-152 |  |
| 51 | ethanlabelle.dev | 1776 | 39 | 475 | 256-219 | 33% (c_isle1 1-2*) |
| 52 | **us:c_nav5** | 1761 | 75 | 126 | 61-65 |  |
| 53 | NotLLeon.v7 | 1759 | 31 | 935 | 421-514 | 90% (c_adp1 9-1*) |
| 54 | **us:c_nav6** | 1746 | 74 | 129 | 58-71 |  |
| 55 | georgezhang02.CB_tuning2 | 1732 | 31 | 949 | 407-542 | 100% (c_adp1 10-0*) |
| 56 | **us:c_nav4** | 1724 | 56 | 221 | 108-113 |  |
| 57 | britacatalin.FinalBot | 1673 | 32 | 894 | 351-543 | 100% (c_adp1 10-0*) |
| 58 | ethanlabelle.v19 | 1661 | 40 | 463 | 230-233 | 83% (c_well9 5-1*) |
| 59 | VarunVejalla.karel | 1655 | 39 | 481 | 242-239 | 67% (c_gp1 2-1*) |
| 60 | GabeG888.v8 | 1652 | 42 | 391 | 216-175 | 67% (c_well9 2-1*) |
| 61 | **us:c_swarm1** | 1643 | 52 | 271 | 128-143 |  |
| 62 | GabeG888.v8o1 | 1635 | 42 | 391 | 222-169 | 33% (c_well9 1-2*) |
| 63 | VarunVejalla.ali8 | 1634 | 43 | 379 | 206-173 | 83% (c_mend2 5-1*) |
| 64 | programjames.fourthbot | 1622 | 42 | 399 | 212-187 | 64% (c_mend2 7-4*) |
| 65 | **us:c_line8a** | 1600 | 74 | 139 | 47-92 |  |
| 66 | **us:g_iter0** | 1582 | 52 | 456 | 230-226 |  |
| 67 | DannyZhang686.pqual2 | 1574 | 41 | 428 | 225-203 | 83% (c_mend2 5-1*) |
| 68 | **us:c_line6** | 1561 | 91 | 100 | 32-68 |  |
| 69 | louishu17.wouisv8 | 1553 | 42 | 402 | 211-191 | 83% (c_aura2 5-1*) |
| 70 | louishu17.louisv10 | 1553 | 43 | 377 | 202-175 | 100% (c_bc1 3-0*) |
| 71 | NicholasKelly15.gopher10 | 1549 | 43 | 368 | 201-167 | 100% (c_anc3 3-0*) |
| 72 | **us:c_line7m** | 1549 | 92 | 100 | 31-69 |  |
| 73 | SampleProvider.SPAARK | 1542 | 43 | 382 | 200-182 | 33% (c_anc3 1-2*) |
| 74 | reeceyang.v5anaconda | 1523 | 33 | 898 | 289-609 | 100% (c_adp1 10-0*) |
| 75 | **us:c_line5** | 1511 | 94 | 100 | 28-72 |  |
| 76 | battlecode-archive.Sprint1 | 1480 | 34 | 866 | 261-605 | 100% (c_adp1 10-0*) |
| 77 | **us:c_line4** | 1471 | 97 | 100 | 25-75 |  |
| 78 | ipince.bobby | 1420 | 44 | 365 | 185-180 | 67% (c_swarm1 2-1*) |
| 79 | SteamBlizzard.newVnewME | 1386 | 41 | 428 | 216-212 | 80% (g_iter0 4-1*) |
| 80 | TheK098.qp1_7_sprint_1 | 1373 | 42 | 423 | 232-191 | 100% (c_mend2 6-0*) |
| 81 | legobridge.tacoplayer | 1370 | 42 | 420 | 200-220 | 100% (c_mend2 6-0*) |
| 82 | polyllc.poly | 1346 | 45 | 358 | 179-179 | 100% (g_iter0 2-0*) |
| 83 | toyat522.bot5a | 1306 | 41 | 432 | 211-221 | 80% (g_iter0 4-1*) |
| 84 | ColtG5.rexv9 | 1294 | 41 | 437 | 218-219 | 100% (g_iter0 2-0*) |
| 85 | elgoldie.head_v5 | 1278 | 41 | 416 | 206-210 | 100% (g_iter0 2-0*) |
| 86 | DukeBas._main | 1276 | 42 | 435 | 237-198 | 100% (c_mend2 6-0*) |
| 87 | beaverbois.USQualifiers | 1257 | 42 | 414 | 219-195 | 50% (g_iter0 1-1*) |
| 88 | Nawlej.PoonPoon | 1205 | 44 | 403 | 200-203 | 100% (g_iter0 2-0*) |
| 89 | kevinli405.maggi3_2 | 1196 | 41 | 454 | 225-229 | 100% (g_iter0 2-0*) |
| 90 | yaonam.PoonPoonv4 | 1178 | 38 | 941 | 270-671 | 90% (c_adp1 9-1*) |
| 91 | BrysonJGalapon.friday | 1165 | 42 | 430 | 227-203 | 100% (g_iter0 2-0*) |
| 92 | nail-e.Barry | 1144 | 42 | 437 | 222-215 | 100% (g_iter0 2-0*) |
| 93 | kevinli405.maggi3 | 1139 | 43 | 443 | 218-225 | 100% (g_iter0 5-0*) |
| 94 | aj-chau.attempt1 | 1124 | 42 | 451 | 231-220 | 100% (g_iter0 5-0*) |
| 95 | mama4294.currentPlayer | 1098 | 42 | 454 | 225-229 | 100% (g_iter0 2-0*) |
| 96 | prisms-cs-club.prisms10 | 1092 | 42 | 452 | 226-226 | 100% (g_iter0 2-0*) |
| 97 | ipince.bobby_v2 | 1068 | 41 | 500 | 246-254 | 67% (c_swarm1 2-1*) |
| 98 | JfeMak.realplayer2 | 975 | 42 | 486 | 246-240 | 100% (g_iter0 2-0*) |
| 99 | andrewgopher.gopherbot | 973 | 42 | 506 | 239-267 | 100% (g_iter0 2-0*) |
| 100 | bewuwy.deathbot4 | 973 | 41 | 529 | 262-267 | 100% (g_iter0 2-0*) |
| 101 | BrysonJGalapon.aloha | 963 | 42 | 514 | 259-255 | 100% (c_swarm1 3-0*) |
| 102 | PSUtblock.sprint_four_player | 926 | 43 | 492 | 236-256 | 100% (g_iter0 2-0*) |
| 103 | SampleProvider.SPAARK_1_12_2023 | 887 | 43 | 531 | 271-260 | 100% (c_swarm1 3-0*) |
| 104 | Nawlej.PoonPoonv3 | 870 | 43 | 516 | 248-268 | 100% (g_iter0 5-0*) |
| 105 | SDainard-PDX.Team_Player | 863 | 44 | 474 | 224-250 | 100% (g_iter0 2-0*) |
| 106 | NolanChai.nolan_1 | 853 | 42 | 538 | 262-276 | 100% (g_iter0 2-0*) |
| 107 | Juanbri02.matfisplayer1 | 849 | 43 | 519 | 260-259 | 100% (g_iter0 5-0*) |
| 108 | andrewgopher.gopherbot1 | 828 | 44 | 492 | 230-262 | 100% (g_iter0 2-0*) |
| 109 | jyorkio.elicompbot | 810 | 44 | 500 | 245-255 | 100% (g_iter0 2-0*) |
| 110 | vontell.regressiongames | 723 | 45 | 527 | 255-272 | 100% (g_iter0 5-0*) |
| 111 | legobridge.kushalplayer | 717 | 47 | 478 | 229-249 | 100% (g_iter0 2-0*) |
| 112 | SteamBlizzard.Block | 653 | 46 | 544 | 253-291 | 100% (g_iter0 5-0*) |
| 113 | Patela171.Battlecode2023_Robot | 640 | 47 | 516 | 236-280 | 100% (g_iter0 2-0*) |
| 114 | ax-95174.MPAction | 616 | 47 | 520 | 233-287 | 100% (c_swarm1 3-0*) |
| 115 | nail-e.Dante | 587 | 47 | 550 | 282-268 | 100% (g_iter0 2-0*) |
| 116 | Chahat08.toph | 574 | 48 | 524 | 247-277 | 100% (g_iter0 2-0*) |
| 117 | JackLee9355.jackPlayer | 565 | 50 | 485 | 216-269 | 100% (g_iter0 2-0*) |
| 118 | michael-tyl.hqrewrite | 564 | 49 | 505 | 243-262 | 100% (g_iter0 2-0*) |
| 119 | mama4294.learningBot | 563 | 48 | 534 | 260-274 | 100% (g_iter0 2-0*) |
| 120 | team-remember-to-hydrate.sprint_1 | 514 | 49 | 537 | 246-291 | 100% (g_iter0 2-0*) |
| 121 | anicolao.submission | 504 | 49 | 564 | 261-303 | 100% (g_iter0 2-0*) |
| 122 | Vinceyou1.Player1 | 397 | 51 | 526 | 239-287 | 100% (g_iter0 2-0*) |
| 123 | michael-tyl.cc_v0_5_0_6 | 375 | 51 | 611 | 289-322 | 100% (g_iter0 2-0*) |
| 124 | addiesteward.elicompbot | 371 | 52 | 548 | 244-304 | 100% (g_iter0 5-0*) |
| 125 | toyat522.bot5 | 366 | 51 | 581 | 253-328 | 100% (g_iter0 2-0*) |
| 126 | Swordman51.AdeptusAstartes2 | 357 | 53 | 548 | 272-276 | 100% (g_iter0 2-0*) |
| 127 | Chahat08.lazarus | 333 | 52 | 563 | 256-307 | 100% (g_iter0 2-0*) |
| 128 | monmouth-college-cs.elicompbot | 309 | 52 | 587 | 265-322 | 100% (g_iter0 2-0*) |
| 129 | anicolao.jumbled | 231 | 55 | 571 | 268-303 | 100% (g_iter0 5-0*) |
| 130 | ShatterXD.SRNNbot | 196 | 57 | 567 | 274-293 | 100% (g_iter0 2-0*) |
| 131 | NotLLeon.player | -49 | 70 | 524 | 248-276 | 100% (g_iter0 2-0*) |
| 132 | CodeClash-ai.mysubmission | -136 | 73 | 551 | 255-296 | 100% (g_iter0 2-0*) |
| 133 | addiesteward.NDeClaw | -153 | 75 | 509 | 231-278 | 100% (g_iter0 5-0*) |
| 134 | Yooncw0223.lec3player | -465 | 85 | 475 | 86-389 | 100% (g_iter0 5-0*) |
| 135 | andrewkbank.First | -530 | 89 | 396 | 59-337 | 100% (g_iter0 2-0*) |
