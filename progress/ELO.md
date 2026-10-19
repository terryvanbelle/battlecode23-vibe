# Ladder

26387 games (7244 ours, 6 of the stock examplefuncsplayer, 19137 between field bots on the ladder replica), 25606 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 135 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_eco3 | 2131 +- 100 | 3 of 134 | 100 | 82-18 | 93.5% | 47.2% (vs 2) |
| c_sm1 | 2103 +- 97 | 6 of 134 | 100 | 80-20 | 92.8% | 45.5% (vs 4) |
| c_loose1 | 2053 +- 52 | 7 of 134 | 278 | 165-113 | 91.5% | 38.7% (vs 4) |
| c_rot1 | 2003 +- 90 | 11 of 134 | 100 | 72-28 | 89.9% | 38.2% (vs 7) |
| c_di1 | 1991 +- 89 | 13 of 134 | 100 | 71-29 | 89.5% | 38.2% (vs 8) |
| c_hunt1 | 1991 +- 89 | 14 of 134 | 100 | 71-29 | 89.5% | 38.2% (vs 8) |
| c_gp1 | 1983 +- 58 | 15 of 134 | 205 | 126-79 | 89.3% | 37.1% (vs 8) |
| c_hr1 | 1969 +- 59 | 18 of 134 | 195 | 114-81 | 88.8% | 38.0% (vs 10) |
| c_expl1 | 1958 +- 88 | 20 of 134 | 100 | 68-32 | 88.4% | 37.6% (vs 11) |
| c_adlo2 | 1958 +- 88 | 21 of 134 | 100 | 68-32 | 88.4% | 37.6% (vs 11) |
| c_pack1 | 1947 +- 88 | 22 of 134 | 100 | 67-33 | 88.0% | 36.2% (vs 11) |
| c_isle1 | 1934 +- 48 | 23 of 134 | 303 | 165-138 | 87.6% | 34.6% (vs 11) |
| c_well5 | 1914 +- 87 | 24 of 134 | 100 | 64-36 | 86.9% | 32.1% (vs 11) |
| c_blind1 | 1903 +- 86 | 25 of 134 | 100 | 63-37 | 86.5% | 30.9% (vs 11) |
| c_blind2 | 1903 +- 86 | 26 of 134 | 100 | 63-37 | 86.5% | 30.9% (vs 11) |
| c_tune1 | 1903 +- 86 | 27 of 134 | 100 | 63-37 | 86.5% | 30.9% (vs 11) |
| c_well10 | 1893 +- 86 | 29 of 134 | 100 | 62-38 | 86.1% | 31.3% (vs 12) |
| c_mid1 | 1893 +- 86 | 30 of 134 | 100 | 62-38 | 86.1% | 31.3% (vs 12) |
| c_bc3 | 1882 +- 86 | 31 of 134 | 100 | 61-39 | 85.7% | 30.0% (vs 12) |
| c_mend3 | 1882 +- 86 | 32 of 134 | 100 | 61-39 | 85.7% | 30.0% (vs 12) |
| c_spread2 | 1882 +- 86 | 33 of 134 | 100 | 61-39 | 85.7% | 30.0% (vs 12) |
| c_thr1 | 1872 +- 86 | 34 of 134 | 100 | 60-40 | 85.3% | 28.8% (vs 12) |
| c_scout1 | 1872 +- 86 | 35 of 134 | 100 | 60-40 | 85.3% | 28.8% (vs 12) |
| c_well7 | 1872 +- 86 | 36 of 134 | 100 | 60-40 | 85.3% | 28.8% (vs 12) |
| c_seam2 | 1861 +- 86 | 37 of 134 | 100 | 59-41 | 84.9% | 27.7% (vs 12) |
| c_cap1 | 1861 +- 86 | 38 of 134 | 100 | 59-41 | 84.9% | 27.7% (vs 12) |
| c_seam1 | 1861 +- 86 | 39 of 134 | 100 | 59-41 | 84.9% | 27.7% (vs 12) |
| c_def3 | 1857 +- 59 | 40 of 134 | 199 | 120-79 | 84.8% | 27.2% (vs 12) |
| c_mend2 | 1856 +- 38 | 41 of 134 | 612 | 362-250 | 84.8% | 27.2% (vs 12) |
| c_bc1 | 1856 +- 65 | 42 of 134 | 164 | 97-67 | 84.7% | 27.1% (vs 12) |
| c_well9 | 1851 +- 51 | 43 of 134 | 260 | 138-122 | 84.5% | 26.6% (vs 12) |
| c_siege1 | 1851 +- 85 | 44 of 134 | 100 | 58-42 | 84.5% | 26.5% (vs 12) |
| c_end2 | 1840 +- 85 | 45 of 134 | 100 | 57-43 | 84.1% | 25.4% (vs 12) |
| c_flee3 | 1830 +- 85 | 46 of 134 | 100 | 56-44 | 83.7% | 24.3% (vs 12) |
| c_open1 | 1830 +- 85 | 47 of 134 | 100 | 56-44 | 83.7% | 24.3% (vs 12) |
| c_anc3 | 1828 +- 65 | 48 of 134 | 163 | 88-75 | 83.6% | 24.1% (vs 12) |
| c_aura2 | 1826 +- 47 | 49 of 134 | 314 | 162-152 | 83.6% | 24.0% (vs 12) |
| c_nav5 | 1768 +- 75 | 51 of 134 | 126 | 61-65 | 81.2% | 20.8% (vs 13) |
| c_nav6 | 1753 +- 74 | 53 of 134 | 129 | 58-71 | 80.6% | 21.5% (vs 14) |
| c_nav4 | 1731 +- 56 | 55 of 134 | 221 | 108-113 | 79.6% | 21.5% (vs 15) |
| c_swarm1 | 1649 +- 52 | 60 of 134 | 271 | 128-143 | 75.9% | 21.9% (vs 19) |
| c_line8a | 1607 +- 75 | 64 of 134 | 139 | 47-92 | 73.9% | 22.3% (vs 22) |
| g_iter0 | 1588 +- 52 | 65 of 134 | 456 | 230-226 | 73.0% | 20.7% (vs 22) |
| c_line6 | 1568 +- 91 | 67 of 134 | 100 | 32-68 | 72.0% | 20.5% (vs 23) |
| c_line7m | 1556 +- 92 | 70 of 134 | 100 | 31-69 | 71.4% | 21.9% (vs 25) |
| c_line5 | 1518 +- 94 | 74 of 134 | 100 | 28-72 | 69.6% | 21.8% (vs 28) |
| c_line4 | 1478 +- 97 | 76 of 134 | 100 | 25-75 | 67.5% | 19.7% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_eco3), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2156 | 52 | 293 | 196-97 | 33% (c_loose1 2-4*) |
| 2 | awesomelemonade.finalBot | 2144 | 38 | 781 | 589-192 | 40% (c_eco3 4-6*) |
| 3 | **us:c_eco3** | 2131 | 100 | 100 | 82-18 |  |
| 4 | IvanGeffner.fortytwo | 2121 | 50 | 329 | 211-118 | 33% (c_loose1 2-4*) |
| 5 | carlguo866.submit26_final | 2114 | 48 | 349 | 215-134 | 40% (c_loose1 20-30) |
| 6 | **us:c_sm1** | 2103 | 97 | 100 | 80-20 |  |
| 7 | **us:c_loose1** | 2053 | 52 | 278 | 165-113 |  |
| 8 | vrangr1.AFinalsBot | 2050 | 35 | 783 | 525-258 | 70% (c_eco3 7-3*) |
| 9 | AnOvercookedFork.quals | 2024 | 46 | 364 | 216-148 | 50% (c_loose1 9-9*) |
| 10 | georgezhang02.FB_ZZZ | 2009 | 44 | 400 | 248-152 | 56% (c_loose1 5-4*) |
| 11 | **us:c_rot1** | 2003 | 90 | 100 | 72-28 |  |
| 12 | pranayagra.finalbotfinaltwo | 2000 | 46 | 368 | 225-143 | 67% (c_loose1 6-3*) |
| 13 | **us:c_di1** | 1991 | 89 | 100 | 71-29 |  |
| 14 | **us:c_hunt1** | 1991 | 89 | 100 | 71-29 |  |
| 15 | **us:c_gp1** | 1983 | 58 | 205 | 126-79 |  |
| 16 | pranayagra.finalbotfinal | 1979 | 32 | 960 | 578-382 | 80% (c_eco3 8-2*) |
| 17 | battlecode-archive.sprintBot | 1978 | 43 | 416 | 245-171 | 56% (c_loose1 5-4*) |
| 18 | **us:c_hr1** | 1969 | 59 | 195 | 114-81 |  |
| 19 | jmerle.camel_case_v30_final | 1961 | 33 | 896 | 546-350 | 60% (c_eco3 6-4*) |
| 20 | **us:c_expl1** | 1958 | 88 | 100 | 68-32 |  |
| 21 | **us:c_adlo2** | 1958 | 88 | 100 | 68-32 |  |
| 22 | **us:c_pack1** | 1947 | 88 | 100 | 67-33 |  |
| 23 | **us:c_isle1** | 1934 | 48 | 303 | 165-138 |  |
| 24 | **us:c_well5** | 1914 | 87 | 100 | 64-36 |  |
| 25 | **us:c_blind1** | 1903 | 86 | 100 | 63-37 |  |
| 26 | **us:c_blind2** | 1903 | 86 | 100 | 63-37 |  |
| 27 | **us:c_tune1** | 1903 | 86 | 100 | 63-37 |  |
| 28 | CyrilSharma.finalBot | 1894 | 40 | 500 | 280-220 | 67% (c_loose1 6-3*) |
| 29 | **us:c_well10** | 1893 | 86 | 100 | 62-38 |  |
| 30 | **us:c_mid1** | 1893 | 86 | 100 | 62-38 |  |
| 31 | **us:c_bc3** | 1882 | 86 | 100 | 61-39 |  |
| 32 | **us:c_mend3** | 1882 | 86 | 100 | 61-39 |  |
| 33 | **us:c_spread2** | 1882 | 86 | 100 | 61-39 |  |
| 34 | **us:c_thr1** | 1872 | 86 | 100 | 60-40 |  |
| 35 | **us:c_scout1** | 1872 | 86 | 100 | 60-40 |  |
| 36 | **us:c_well7** | 1872 | 86 | 100 | 60-40 |  |
| 37 | **us:c_seam2** | 1861 | 86 | 100 | 59-41 |  |
| 38 | **us:c_cap1** | 1861 | 86 | 100 | 59-41 |  |
| 39 | **us:c_seam1** | 1861 | 86 | 100 | 59-41 |  |
| 40 | **us:c_def3** | 1857 | 59 | 199 | 120-79 |  |
| 41 | **us:c_mend2** | 1856 | 38 | 612 | 362-250 |  |
| 42 | **us:c_bc1** | 1856 | 65 | 164 | 97-67 |  |
| 43 | **us:c_well9** | 1851 | 51 | 260 | 138-122 |  |
| 44 | **us:c_siege1** | 1851 | 85 | 100 | 58-42 |  |
| 45 | **us:c_end2** | 1840 | 85 | 100 | 57-43 |  |
| 46 | **us:c_flee3** | 1830 | 85 | 100 | 56-44 |  |
| 47 | **us:c_open1** | 1830 | 85 | 100 | 56-44 |  |
| 48 | **us:c_anc3** | 1828 | 65 | 163 | 88-75 |  |
| 49 | **us:c_aura2** | 1826 | 47 | 314 | 162-152 |  |
| 50 | ethanlabelle.dev | 1784 | 40 | 465 | 252-213 | 33% (c_isle1 1-2*) |
| 51 | **us:c_nav5** | 1768 | 75 | 126 | 61-65 |  |
| 52 | NotLLeon.v7 | 1768 | 31 | 914 | 417-497 | 90% (c_eco3 9-1*) |
| 53 | **us:c_nav6** | 1753 | 74 | 129 | 58-71 |  |
| 54 | georgezhang02.CB_tuning2 | 1741 | 31 | 928 | 405-523 | 100% (c_eco3 10-0*) |
| 55 | **us:c_nav4** | 1731 | 56 | 221 | 108-113 |  |
| 56 | britacatalin.FinalBot | 1683 | 32 | 872 | 345-527 | 90% (c_eco3 9-1*) |
| 57 | ethanlabelle.v19 | 1666 | 40 | 453 | 223-230 | 83% (c_well9 5-1*) |
| 58 | VarunVejalla.karel | 1666 | 40 | 469 | 238-231 | 67% (c_gp1 2-1*) |
| 59 | GabeG888.v8 | 1662 | 43 | 380 | 212-168 | 67% (c_well9 2-1*) |
| 60 | **us:c_swarm1** | 1649 | 52 | 271 | 128-143 |  |
| 61 | VarunVejalla.ali8 | 1641 | 44 | 367 | 201-166 | 83% (c_mend2 5-1*) |
| 62 | GabeG888.v8o1 | 1639 | 42 | 380 | 215-165 | 33% (c_well9 1-2*) |
| 63 | programjames.fourthbot | 1626 | 43 | 387 | 202-185 | 64% (c_mend2 7-4*) |
| 64 | **us:c_line8a** | 1607 | 75 | 139 | 47-92 |  |
| 65 | **us:g_iter0** | 1588 | 52 | 456 | 230-226 |  |
| 66 | DannyZhang686.pqual2 | 1575 | 41 | 417 | 218-199 | 83% (c_mend2 5-1*) |
| 67 | **us:c_line6** | 1568 | 91 | 100 | 32-68 |  |
| 68 | NicholasKelly15.gopher10 | 1560 | 44 | 359 | 198-161 | 100% (c_anc3 3-0*) |
| 69 | louishu17.louisv10 | 1557 | 44 | 367 | 196-171 | 100% (c_bc1 3-0*) |
| 70 | **us:c_line7m** | 1556 | 92 | 100 | 31-69 |  |
| 71 | SampleProvider.SPAARK | 1552 | 43 | 372 | 198-174 | 33% (c_anc3 1-2*) |
| 72 | louishu17.wouisv8 | 1552 | 43 | 391 | 203-188 | 83% (c_aura2 5-1*) |
| 73 | reeceyang.v5anaconda | 1531 | 33 | 877 | 283-594 | 100% (c_eco3 10-0*) |
| 74 | **us:c_line5** | 1518 | 94 | 100 | 28-72 |  |
| 75 | battlecode-archive.Sprint1 | 1486 | 35 | 845 | 254-591 | 100% (c_eco3 10-0*) |
| 76 | **us:c_line4** | 1478 | 97 | 100 | 25-75 |  |
| 77 | ipince.bobby | 1426 | 45 | 355 | 181-174 | 67% (c_swarm1 2-1*) |
| 78 | SteamBlizzard.newVnewME | 1395 | 42 | 418 | 214-204 | 80% (g_iter0 4-1*) |
| 79 | TheK098.qp1_7_sprint_1 | 1377 | 42 | 412 | 228-184 | 100% (c_mend2 6-0*) |
| 80 | legobridge.tacoplayer | 1374 | 43 | 408 | 191-217 | 100% (c_mend2 6-0*) |
| 81 | polyllc.poly | 1348 | 46 | 349 | 173-176 | 100% (g_iter0 2-0*) |
| 82 | toyat522.bot5a | 1308 | 42 | 421 | 203-218 | 80% (g_iter0 4-1*) |
| 83 | ColtG5.rexv9 | 1301 | 42 | 427 | 214-213 | 100% (g_iter0 2-0*) |
| 84 | DukeBas._main | 1279 | 43 | 423 | 230-193 | 100% (c_mend2 6-0*) |
| 85 | elgoldie.head_v5 | 1277 | 42 | 404 | 196-208 | 100% (g_iter0 2-0*) |
| 86 | beaverbois.USQualifiers | 1265 | 43 | 402 | 213-189 | 50% (g_iter0 1-1*) |
| 87 | kevinli405.maggi3_2 | 1208 | 42 | 443 | 225-218 | 100% (g_iter0 2-0*) |
| 88 | Nawlej.PoonPoon | 1206 | 44 | 391 | 191-200 | 100% (g_iter0 2-0*) |
| 89 | yaonam.PoonPoonv4 | 1186 | 38 | 919 | 262-657 | 90% (c_eco3 9-1*) |
| 90 | BrysonJGalapon.friday | 1169 | 42 | 418 | 219-199 | 100% (g_iter0 2-0*) |
| 91 | nail-e.Barry | 1154 | 42 | 426 | 217-209 | 100% (g_iter0 2-0*) |
| 92 | kevinli405.maggi3 | 1149 | 43 | 431 | 215-216 | 100% (g_iter0 5-0*) |
| 93 | aj-chau.attempt1 | 1135 | 42 | 440 | 226-214 | 100% (g_iter0 5-0*) |
| 94 | mama4294.currentPlayer | 1105 | 42 | 442 | 219-223 | 100% (g_iter0 2-0*) |
| 95 | prisms-cs-club.prisms10 | 1100 | 43 | 441 | 222-219 | 100% (g_iter0 2-0*) |
| 96 | ipince.bobby_v2 | 1076 | 42 | 488 | 243-245 | 67% (c_swarm1 2-1*) |
| 97 | JfeMak.realplayer2 | 978 | 43 | 476 | 240-236 | 100% (g_iter0 2-0*) |
| 98 | andrewgopher.gopherbot | 977 | 42 | 494 | 230-264 | 100% (g_iter0 2-0*) |
| 99 | bewuwy.deathbot4 | 975 | 42 | 520 | 254-266 | 100% (g_iter0 2-0*) |
| 100 | BrysonJGalapon.aloha | 969 | 42 | 503 | 256-247 | 100% (c_swarm1 3-0*) |
| 101 | PSUtblock.sprint_four_player | 929 | 44 | 480 | 230-250 | 100% (g_iter0 2-0*) |
| 102 | SampleProvider.SPAARK_1_12_2023 | 900 | 43 | 519 | 269-250 | 100% (c_swarm1 3-0*) |
| 103 | Nawlej.PoonPoonv3 | 873 | 43 | 505 | 241-264 | 100% (g_iter0 5-0*) |
| 104 | SDainard-PDX.Team_Player | 871 | 45 | 463 | 222-241 | 100% (g_iter0 2-0*) |
| 105 | NolanChai.nolan_1 | 858 | 43 | 528 | 257-271 | 100% (g_iter0 2-0*) |
| 106 | Juanbri02.matfisplayer1 | 856 | 44 | 508 | 253-255 | 100% (g_iter0 5-0*) |
| 107 | andrewgopher.gopherbot1 | 834 | 45 | 481 | 223-258 | 100% (g_iter0 2-0*) |
| 108 | jyorkio.elicompbot | 817 | 44 | 489 | 240-249 | 100% (g_iter0 2-0*) |
| 109 | vontell.regressiongames | 732 | 45 | 516 | 250-266 | 100% (g_iter0 5-0*) |
| 110 | legobridge.kushalplayer | 724 | 47 | 467 | 223-244 | 100% (g_iter0 2-0*) |
| 111 | SteamBlizzard.Block | 659 | 47 | 533 | 246-287 | 100% (g_iter0 5-0*) |
| 112 | Patela171.Battlecode2023_Robot | 654 | 47 | 504 | 233-271 | 100% (g_iter0 2-0*) |
| 113 | ax-95174.MPAction | 625 | 47 | 510 | 229-281 | 100% (c_swarm1 3-0*) |
| 114 | nail-e.Dante | 592 | 48 | 538 | 276-262 | 100% (g_iter0 2-0*) |
| 115 | Chahat08.toph | 578 | 48 | 514 | 240-274 | 100% (g_iter0 2-0*) |
| 116 | JackLee9355.jackPlayer | 573 | 50 | 473 | 209-264 | 100% (g_iter0 2-0*) |
| 117 | mama4294.learningBot | 571 | 49 | 524 | 254-270 | 100% (g_iter0 2-0*) |
| 118 | michael-tyl.hqrewrite | 570 | 49 | 494 | 237-257 | 100% (g_iter0 2-0*) |
| 119 | team-remember-to-hydrate.sprint_1 | 522 | 49 | 527 | 244-283 | 100% (g_iter0 2-0*) |
| 120 | anicolao.submission | 510 | 49 | 555 | 255-300 | 100% (g_iter0 2-0*) |
| 121 | Vinceyou1.Player1 | 410 | 52 | 515 | 239-276 | 100% (g_iter0 2-0*) |
| 122 | michael-tyl.cc_v0_5_0_6 | 382 | 51 | 601 | 286-315 | 100% (g_iter0 2-0*) |
| 123 | addiesteward.elicompbot | 376 | 52 | 536 | 236-300 | 100% (g_iter0 5-0*) |
| 124 | toyat522.bot5 | 373 | 51 | 570 | 247-323 | 100% (g_iter0 2-0*) |
| 125 | Swordman51.AdeptusAstartes2 | 358 | 53 | 536 | 264-272 | 100% (g_iter0 2-0*) |
| 126 | Chahat08.lazarus | 341 | 53 | 551 | 252-299 | 100% (g_iter0 2-0*) |
| 127 | monmouth-college-cs.elicompbot | 313 | 53 | 575 | 257-318 | 100% (g_iter0 2-0*) |
| 128 | anicolao.jumbled | 233 | 56 | 559 | 261-298 | 100% (g_iter0 5-0*) |
| 129 | ShatterXD.SRNNbot | 203 | 57 | 557 | 271-286 | 100% (g_iter0 2-0*) |
| 130 | NotLLeon.player | -42 | 71 | 513 | 243-270 | 100% (g_iter0 2-0*) |
| 131 | CodeClash-ai.mysubmission | -135 | 74 | 541 | 248-293 | 100% (g_iter0 2-0*) |
| 132 | addiesteward.NDeClaw | -151 | 76 | 500 | 225-275 | 100% (g_iter0 5-0*) |
| 133 | Yooncw0223.lec3player | -464 | 86 | 469 | 85-384 | 100% (g_iter0 5-0*) |
| 134 | andrewkbank.First | -533 | 90 | 387 | 57-330 | 100% (g_iter0 2-0*) |
