# Ladder

24421 games (6442 ours, 6 of the stock examplefuncsplayer, 17973 between field bots on the ladder replica), 23743 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 131 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_isle1 | 2043 +- 91 | 7 of 130 | 100 | 73-27 | 90.4% | 38.0% (vs 6) |
| c_rot1 | 2031 +- 90 | 8 of 130 | 100 | 72-28 | 90.0% | 36.5% (vs 6) |
| c_hunt1 | 2019 +- 90 | 10 of 130 | 100 | 71-29 | 89.6% | 37.0% (vs 7) |
| c_gp1 | 2008 +- 58 | 12 of 130 | 205 | 126-79 | 89.3% | 37.1% (vs 8) |
| c_hr1 | 1994 +- 59 | 15 of 130 | 195 | 114-81 | 88.8% | 38.1% (vs 10) |
| c_expl1 | 1986 +- 88 | 17 of 130 | 100 | 68-32 | 88.5% | 38.1% (vs 11) |
| c_adlo2 | 1986 +- 88 | 18 of 130 | 100 | 68-32 | 88.5% | 38.1% (vs 11) |
| c_pack1 | 1975 +- 88 | 19 of 130 | 100 | 67-33 | 88.2% | 36.7% (vs 11) |
| c_well5 | 1942 +- 87 | 20 of 130 | 100 | 64-36 | 87.0% | 32.6% (vs 11) |
| c_blind1 | 1931 +- 87 | 21 of 130 | 100 | 63-37 | 86.6% | 31.3% (vs 11) |
| c_blind2 | 1931 +- 87 | 22 of 130 | 100 | 63-37 | 86.6% | 31.3% (vs 11) |
| c_tune1 | 1931 +- 87 | 23 of 130 | 100 | 63-37 | 86.6% | 31.3% (vs 11) |
| c_mid1 | 1921 +- 86 | 24 of 130 | 100 | 62-38 | 86.2% | 30.0% (vs 11) |
| c_well10 | 1921 +- 86 | 25 of 130 | 100 | 62-38 | 86.2% | 30.0% (vs 11) |
| c_bc3 | 1910 +- 86 | 26 of 130 | 100 | 61-39 | 85.8% | 28.8% (vs 11) |
| c_spread2 | 1910 +- 86 | 27 of 130 | 100 | 61-39 | 85.8% | 28.8% (vs 11) |
| c_mend3 | 1910 +- 86 | 28 of 130 | 100 | 61-39 | 85.8% | 28.8% (vs 11) |
| c_thr1 | 1900 +- 86 | 30 of 130 | 100 | 60-40 | 85.5% | 29.4% (vs 12) |
| c_well7 | 1900 +- 86 | 31 of 130 | 100 | 60-40 | 85.5% | 29.4% (vs 12) |
| c_scout1 | 1900 +- 86 | 32 of 130 | 100 | 60-40 | 85.5% | 29.4% (vs 12) |
| c_seam1 | 1889 +- 86 | 33 of 130 | 100 | 59-41 | 85.1% | 28.2% (vs 12) |
| c_seam2 | 1889 +- 86 | 34 of 130 | 100 | 59-41 | 85.1% | 28.2% (vs 12) |
| c_cap1 | 1889 +- 86 | 35 of 130 | 100 | 59-41 | 85.1% | 28.2% (vs 12) |
| c_bc1 | 1884 +- 65 | 36 of 130 | 164 | 97-67 | 84.8% | 27.6% (vs 12) |
| c_mend2 | 1883 +- 38 | 37 of 130 | 612 | 362-250 | 84.8% | 27.5% (vs 12) |
| c_def3 | 1883 +- 59 | 38 of 130 | 199 | 120-79 | 84.8% | 27.5% (vs 12) |
| c_siege1 | 1879 +- 86 | 39 of 130 | 100 | 58-42 | 84.7% | 27.0% (vs 12) |
| c_well9 | 1876 +- 52 | 40 of 130 | 260 | 138-122 | 84.5% | 26.7% (vs 12) |
| c_end2 | 1868 +- 86 | 41 of 130 | 100 | 57-43 | 84.2% | 25.9% (vs 12) |
| c_flee3 | 1858 +- 85 | 42 of 130 | 100 | 56-44 | 83.8% | 24.8% (vs 12) |
| c_open1 | 1858 +- 85 | 43 of 130 | 100 | 56-44 | 83.8% | 24.8% (vs 12) |
| c_anc3 | 1854 +- 65 | 44 of 130 | 163 | 88-75 | 83.7% | 24.4% (vs 12) |
| c_aura2 | 1852 +- 48 | 45 of 130 | 314 | 162-152 | 83.6% | 24.2% (vs 12) |
| c_nav5 | 1795 +- 75 | 47 of 130 | 126 | 61-65 | 81.3% | 21.1% (vs 13) |
| c_nav6 | 1780 +- 74 | 49 of 130 | 129 | 58-71 | 80.6% | 21.8% (vs 14) |
| c_nav4 | 1757 +- 56 | 51 of 130 | 221 | 108-113 | 79.7% | 21.7% (vs 15) |
| c_swarm1 | 1677 +- 52 | 56 of 130 | 271 | 128-143 | 76.0% | 22.1% (vs 19) |
| c_line8a | 1634 +- 75 | 60 of 130 | 139 | 47-92 | 74.0% | 22.3% (vs 22) |
| g_iter0 | 1613 +- 52 | 61 of 130 | 456 | 230-226 | 73.0% | 20.6% (vs 22) |
| c_line6 | 1597 +- 91 | 62 of 130 | 100 | 32-68 | 72.2% | 19.3% (vs 22) |
| c_line7m | 1585 +- 92 | 65 of 130 | 100 | 31-69 | 71.6% | 20.9% (vs 24) |
| c_line5 | 1547 +- 94 | 70 of 130 | 100 | 28-72 | 69.7% | 22.0% (vs 28) |
| c_line4 | 1506 +- 98 | 72 of 130 | 100 | 25-75 | 67.7% | 19.8% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_isle1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2187 | 56 | 268 | 183-85 | 22% (c_mend2 2-7*) |
| 2 | awesomelemonade.finalBot | 2163 | 40 | 699 | 535-164 | 30% (c_isle1 3-7*) |
| 3 | IvanGeffner.fortytwo | 2156 | 53 | 303 | 200-103 | 33% (c_gp1 1-2*) |
| 4 | carlguo866.submit26_final | 2123 | 53 | 280 | 169-111 | 0% (c_mend2 0-3*) |
| 5 | vrangr1.AFinalsBot | 2089 | 38 | 713 | 499-214 | 50% (c_isle1 5-5*) |
| 6 | AnOvercookedFork.quals | 2055 | 50 | 316 | 193-123 | 33% (c_hr1 1-2*) |
| 7 | **us:c_isle1** | 2043 | 91 | 100 | 73-27 |  |
| 8 | **us:c_rot1** | 2031 | 90 | 100 | 72-28 |  |
| 9 | georgezhang02.FB_ZZZ | 2026 | 47 | 346 | 216-130 | 38% (c_hr1 8-13*) |
| 10 | **us:c_hunt1** | 2019 | 90 | 100 | 71-29 |  |
| 11 | pranayagra.finalbotfinaltwo | 2016 | 49 | 330 | 200-130 | 42% (c_hr1 5-7*) |
| 12 | **us:c_gp1** | 2008 | 58 | 205 | 126-79 |  |
| 13 | pranayagra.finalbotfinal | 2004 | 34 | 833 | 520-313 | 50% (c_isle1 5-5*) |
| 14 | battlecode-archive.sprintBot | 2003 | 47 | 345 | 209-136 | 42% (c_hr1 10-14*) |
| 15 | **us:c_hr1** | 1994 | 59 | 195 | 114-81 |  |
| 16 | jmerle.camel_case_v30_final | 1988 | 34 | 796 | 499-297 | 40% (c_isle1 4-6*) |
| 17 | **us:c_expl1** | 1986 | 88 | 100 | 68-32 |  |
| 18 | **us:c_adlo2** | 1986 | 88 | 100 | 68-32 |  |
| 19 | **us:c_pack1** | 1975 | 88 | 100 | 67-33 |  |
| 20 | **us:c_well5** | 1942 | 87 | 100 | 64-36 |  |
| 21 | **us:c_blind1** | 1931 | 87 | 100 | 63-37 |  |
| 22 | **us:c_blind2** | 1931 | 87 | 100 | 63-37 |  |
| 23 | **us:c_tune1** | 1931 | 87 | 100 | 63-37 |  |
| 24 | **us:c_mid1** | 1921 | 86 | 100 | 62-38 |  |
| 25 | **us:c_well10** | 1921 | 86 | 100 | 62-38 |  |
| 26 | **us:c_bc3** | 1910 | 86 | 100 | 61-39 |  |
| 27 | **us:c_spread2** | 1910 | 86 | 100 | 61-39 |  |
| 28 | **us:c_mend3** | 1910 | 86 | 100 | 61-39 |  |
| 29 | CyrilSharma.finalBot | 1908 | 44 | 423 | 242-181 | 62% (c_gp1 16-10*) |
| 30 | **us:c_thr1** | 1900 | 86 | 100 | 60-40 |  |
| 31 | **us:c_well7** | 1900 | 86 | 100 | 60-40 |  |
| 32 | **us:c_scout1** | 1900 | 86 | 100 | 60-40 |  |
| 33 | **us:c_seam1** | 1889 | 86 | 100 | 59-41 |  |
| 34 | **us:c_seam2** | 1889 | 86 | 100 | 59-41 |  |
| 35 | **us:c_cap1** | 1889 | 86 | 100 | 59-41 |  |
| 36 | **us:c_bc1** | 1884 | 65 | 164 | 97-67 |  |
| 37 | **us:c_mend2** | 1883 | 38 | 612 | 362-250 |  |
| 38 | **us:c_def3** | 1883 | 59 | 199 | 120-79 |  |
| 39 | **us:c_siege1** | 1879 | 86 | 100 | 58-42 |  |
| 40 | **us:c_well9** | 1876 | 52 | 260 | 138-122 |  |
| 41 | **us:c_end2** | 1868 | 86 | 100 | 57-43 |  |
| 42 | **us:c_flee3** | 1858 | 85 | 100 | 56-44 |  |
| 43 | **us:c_open1** | 1858 | 85 | 100 | 56-44 |  |
| 44 | **us:c_anc3** | 1854 | 65 | 163 | 88-75 |  |
| 45 | **us:c_aura2** | 1852 | 48 | 314 | 162-152 |  |
| 46 | ethanlabelle.dev | 1813 | 41 | 438 | 241-197 | 52% (c_well9 17-16) |
| 47 | **us:c_nav5** | 1795 | 75 | 126 | 61-65 |  |
| 48 | NotLLeon.v7 | 1795 | 33 | 847 | 397-450 | 70% (c_isle1 7-3*) |
| 49 | **us:c_nav6** | 1780 | 74 | 129 | 58-71 |  |
| 50 | georgezhang02.CB_tuning2 | 1770 | 32 | 852 | 383-469 | 100% (c_isle1 10-0*) |
| 51 | **us:c_nav4** | 1757 | 56 | 221 | 108-113 |  |
| 52 | britacatalin.FinalBot | 1712 | 33 | 805 | 333-472 | 90% (c_isle1 9-1*) |
| 53 | ethanlabelle.v19 | 1696 | 42 | 426 | 211-215 | 83% (c_well9 5-1*) |
| 54 | VarunVejalla.karel | 1686 | 41 | 443 | 224-219 | 67% (c_gp1 2-1*) |
| 55 | GabeG888.v8 | 1685 | 44 | 356 | 198-158 | 67% (c_well9 2-1*) |
| 56 | **us:c_swarm1** | 1677 | 52 | 271 | 128-143 |  |
| 57 | programjames.fourthbot | 1670 | 44 | 361 | 197-164 | 64% (c_mend2 7-4*) |
| 58 | GabeG888.v8o1 | 1666 | 44 | 357 | 202-155 | 33% (c_well9 1-2*) |
| 59 | VarunVejalla.ali8 | 1663 | 45 | 345 | 189-156 | 83% (c_mend2 5-1*) |
| 60 | **us:c_line8a** | 1634 | 75 | 139 | 47-92 |  |
| 61 | **us:g_iter0** | 1613 | 52 | 456 | 230-226 |  |
| 62 | **us:c_line6** | 1597 | 91 | 100 | 32-68 |  |
| 63 | DannyZhang686.pqual2 | 1594 | 43 | 394 | 203-191 | 83% (c_mend2 5-1*) |
| 64 | NicholasKelly15.gopher10 | 1589 | 46 | 333 | 183-150 | 100% (c_anc3 3-0*) |
| 65 | **us:c_line7m** | 1585 | 92 | 100 | 31-69 |  |
| 66 | louishu17.louisv10 | 1582 | 45 | 344 | 184-160 | 100% (c_bc1 3-0*) |
| 67 | SampleProvider.SPAARK | 1577 | 46 | 342 | 181-161 | 33% (c_anc3 1-2*) |
| 68 | louishu17.wouisv8 | 1570 | 45 | 365 | 187-178 | 83% (c_aura2 5-1*) |
| 69 | reeceyang.v5anaconda | 1565 | 35 | 807 | 270-537 | 100% (c_isle1 10-0*) |
| 70 | **us:c_line5** | 1547 | 94 | 100 | 28-72 |  |
| 71 | battlecode-archive.Sprint1 | 1511 | 36 | 781 | 239-542 | 100% (c_isle1 10-0*) |
| 72 | **us:c_line4** | 1506 | 98 | 100 | 25-75 |  |
| 73 | ipince.bobby | 1447 | 47 | 327 | 168-159 | 67% (c_swarm1 2-1*) |
| 74 | SteamBlizzard.newVnewME | 1419 | 43 | 396 | 198-198 | 80% (g_iter0 4-1*) |
| 75 | legobridge.tacoplayer | 1400 | 45 | 386 | 184-202 | 100% (c_mend2 6-0*) |
| 76 | TheK098.qp1_7_sprint_1 | 1393 | 44 | 385 | 213-172 | 100% (c_mend2 6-0*) |
| 77 | polyllc.poly | 1377 | 48 | 323 | 162-161 | 100% (g_iter0 2-0*) |
| 78 | ColtG5.rexv9 | 1329 | 43 | 400 | 197-203 | 100% (g_iter0 2-0*) |
| 79 | toyat522.bot5a | 1327 | 43 | 396 | 189-207 | 80% (g_iter0 4-1*) |
| 80 | elgoldie.head_v5 | 1304 | 43 | 382 | 187-195 | 100% (g_iter0 2-0*) |
| 81 | DukeBas._main | 1297 | 44 | 401 | 218-183 | 100% (c_mend2 6-0*) |
| 82 | beaverbois.USQualifiers | 1286 | 44 | 381 | 203-178 | 50% (g_iter0 1-1*) |
| 83 | Nawlej.PoonPoon | 1236 | 46 | 365 | 180-185 | 100% (g_iter0 2-0*) |
| 84 | kevinli405.maggi3_2 | 1227 | 43 | 418 | 213-205 | 100% (g_iter0 2-0*) |
| 85 | yaonam.PoonPoonv4 | 1210 | 39 | 849 | 247-602 | 100% (c_isle1 10-0*) |
| 86 | BrysonJGalapon.friday | 1193 | 44 | 388 | 203-185 | 100% (g_iter0 2-0*) |
| 87 | nail-e.Barry | 1172 | 43 | 397 | 198-199 | 100% (g_iter0 2-0*) |
| 88 | kevinli405.maggi3 | 1166 | 45 | 403 | 201-202 | 100% (g_iter0 5-0*) |
| 89 | aj-chau.attempt1 | 1155 | 44 | 413 | 214-199 | 100% (g_iter0 5-0*) |
| 90 | prisms-cs-club.prisms10 | 1125 | 44 | 411 | 210-201 | 100% (g_iter0 2-0*) |
| 91 | mama4294.currentPlayer | 1119 | 43 | 416 | 207-209 | 100% (g_iter0 2-0*) |
| 92 | ipince.bobby_v2 | 1094 | 43 | 462 | 230-232 | 67% (c_swarm1 2-1*) |
| 93 | JfeMak.realplayer2 | 999 | 43 | 451 | 227-224 | 100% (g_iter0 2-0*) |
| 94 | bewuwy.deathbot4 | 996 | 43 | 490 | 240-250 | 100% (g_iter0 2-0*) |
| 95 | andrewgopher.gopherbot | 995 | 43 | 462 | 215-247 | 100% (g_iter0 2-0*) |
| 96 | BrysonJGalapon.aloha | 988 | 43 | 479 | 244-235 | 100% (c_swarm1 3-0*) |
| 97 | PSUtblock.sprint_four_player | 944 | 45 | 447 | 215-232 | 100% (g_iter0 2-0*) |
| 98 | SampleProvider.SPAARK_1_12_2023 | 922 | 44 | 494 | 255-239 | 100% (c_swarm1 3-0*) |
| 99 | Nawlej.PoonPoonv3 | 894 | 44 | 482 | 230-252 | 100% (g_iter0 5-0*) |
| 100 | SDainard-PDX.Team_Player | 883 | 46 | 441 | 205-236 | 100% (g_iter0 2-0*) |
| 101 | Juanbri02.matfisplayer1 | 879 | 44 | 479 | 238-241 | 100% (g_iter0 5-0*) |
| 102 | NolanChai.nolan_1 | 873 | 44 | 501 | 243-258 | 100% (g_iter0 2-0*) |
| 103 | andrewgopher.gopherbot1 | 854 | 46 | 454 | 208-246 | 100% (g_iter0 2-0*) |
| 104 | jyorkio.elicompbot | 838 | 45 | 466 | 228-238 | 100% (g_iter0 2-0*) |
| 105 | vontell.regressiongames | 758 | 46 | 491 | 239-252 | 100% (g_iter0 5-0*) |
| 106 | legobridge.kushalplayer | 742 | 48 | 441 | 205-236 | 100% (g_iter0 2-0*) |
| 107 | SteamBlizzard.Block | 690 | 48 | 504 | 235-269 | 100% (g_iter0 5-0*) |
| 108 | Patela171.Battlecode2023_Robot | 686 | 48 | 479 | 224-255 | 100% (g_iter0 2-0*) |
| 109 | ax-95174.MPAction | 655 | 48 | 488 | 220-268 | 100% (c_swarm1 3-0*) |
| 110 | nail-e.Dante | 613 | 49 | 514 | 261-253 | 100% (g_iter0 2-0*) |
| 111 | michael-tyl.hqrewrite | 605 | 50 | 467 | 230-237 | 100% (g_iter0 2-0*) |
| 112 | Chahat08.toph | 605 | 49 | 490 | 229-261 | 100% (g_iter0 2-0*) |
| 113 | JackLee9355.jackPlayer | 600 | 51 | 448 | 196-252 | 100% (g_iter0 2-0*) |
| 114 | mama4294.learningBot | 598 | 50 | 493 | 242-251 | 100% (g_iter0 2-0*) |
| 115 | anicolao.submission | 542 | 49 | 537 | 250-287 | 100% (g_iter0 2-0*) |
| 116 | team-remember-to-hydrate.sprint_1 | 534 | 50 | 500 | 226-274 | 100% (g_iter0 2-0*) |
| 117 | Vinceyou1.Player1 | 424 | 53 | 490 | 224-266 | 100% (g_iter0 2-0*) |
| 118 | addiesteward.elicompbot | 404 | 53 | 515 | 229-286 | 100% (g_iter0 5-0*) |
| 119 | toyat522.bot5 | 404 | 52 | 540 | 236-304 | 100% (g_iter0 2-0*) |
| 120 | michael-tyl.cc_v0_5_0_6 | 401 | 52 | 573 | 271-302 | 100% (g_iter0 2-0*) |
| 121 | Swordman51.AdeptusAstartes2 | 371 | 54 | 516 | 248-268 | 100% (g_iter0 2-0*) |
| 122 | Chahat08.lazarus | 367 | 53 | 531 | 247-284 | 100% (g_iter0 2-0*) |
| 123 | monmouth-college-cs.elicompbot | 333 | 54 | 545 | 240-305 | 100% (g_iter0 2-0*) |
| 124 | anicolao.jumbled | 246 | 57 | 534 | 246-288 | 100% (g_iter0 5-0*) |
| 125 | ShatterXD.SRNNbot | 223 | 58 | 530 | 251-279 | 100% (g_iter0 2-0*) |
| 126 | NotLLeon.player | -11 | 71 | 494 | 234-260 | 100% (g_iter0 2-0*) |
| 127 | CodeClash-ai.mysubmission | -111 | 75 | 516 | 233-283 | 100% (g_iter0 2-0*) |
| 128 | addiesteward.NDeClaw | -125 | 76 | 482 | 216-266 | 100% (g_iter0 5-0*) |
| 129 | Yooncw0223.lec3player | -437 | 87 | 451 | 81-370 | 100% (g_iter0 5-0*) |
| 130 | andrewkbank.First | -501 | 91 | 364 | 55-309 | 100% (g_iter0 2-0*) |
