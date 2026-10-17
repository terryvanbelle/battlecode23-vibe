# Ladder

23706 games (6240 ours, 6 of the stock examplefuncsplayer, 17460 between field bots on the ladder replica), 23074 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 130 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_rot1 | 2036 +- 90 | 7 of 129 | 100 | 72-28 | 90.0% | 36.4% (vs 6) |
| c_hr1 | 2036 +- 90 | 8 of 129 | 100 | 72-28 | 90.0% | 36.4% (vs 6) |
| c_hunt1 | 2025 +- 90 | 10 of 129 | 100 | 71-29 | 89.7% | 37.0% (vs 7) |
| c_gp1 | 2011 +- 59 | 12 of 129 | 205 | 126-79 | 89.2% | 36.9% (vs 8) |
| c_expl1 | 1991 +- 88 | 16 of 129 | 100 | 68-32 | 88.5% | 38.3% (vs 11) |
| c_adlo2 | 1991 +- 88 | 17 of 129 | 100 | 68-32 | 88.5% | 38.3% (vs 11) |
| c_pack1 | 1980 +- 88 | 18 of 129 | 100 | 67-33 | 88.2% | 36.9% (vs 11) |
| c_well5 | 1948 +- 87 | 19 of 129 | 100 | 64-36 | 87.0% | 32.8% (vs 11) |
| c_tune1 | 1937 +- 87 | 20 of 129 | 100 | 63-37 | 86.6% | 31.5% (vs 11) |
| c_blind2 | 1937 +- 87 | 21 of 129 | 100 | 63-37 | 86.6% | 31.5% (vs 11) |
| c_blind1 | 1937 +- 87 | 22 of 129 | 100 | 63-37 | 86.6% | 31.5% (vs 11) |
| c_mid1 | 1926 +- 86 | 23 of 129 | 100 | 62-38 | 86.2% | 30.2% (vs 11) |
| c_well10 | 1926 +- 86 | 24 of 129 | 100 | 62-38 | 86.2% | 30.2% (vs 11) |
| c_mend3 | 1916 +- 86 | 25 of 129 | 100 | 61-39 | 85.9% | 29.0% (vs 11) |
| c_spread2 | 1916 +- 86 | 26 of 129 | 100 | 61-39 | 85.9% | 29.0% (vs 11) |
| c_bc3 | 1916 +- 86 | 27 of 129 | 100 | 61-39 | 85.9% | 29.0% (vs 11) |
| c_well7 | 1905 +- 86 | 29 of 129 | 100 | 60-40 | 85.5% | 29.6% (vs 12) |
| c_scout1 | 1905 +- 86 | 30 of 129 | 100 | 60-40 | 85.5% | 29.6% (vs 12) |
| c_thr1 | 1905 +- 86 | 31 of 129 | 100 | 60-40 | 85.5% | 29.6% (vs 12) |
| c_seam1 | 1895 +- 86 | 32 of 129 | 100 | 59-41 | 85.1% | 28.4% (vs 12) |
| c_cap1 | 1895 +- 86 | 33 of 129 | 100 | 59-41 | 85.1% | 28.4% (vs 12) |
| c_seam2 | 1895 +- 86 | 34 of 129 | 100 | 59-41 | 85.1% | 28.4% (vs 12) |
| c_bc1 | 1889 +- 65 | 35 of 129 | 164 | 97-67 | 84.9% | 27.8% (vs 12) |
| c_mend2 | 1888 +- 38 | 36 of 129 | 612 | 362-250 | 84.8% | 27.7% (vs 12) |
| c_def3 | 1888 +- 59 | 37 of 129 | 199 | 120-79 | 84.8% | 27.6% (vs 12) |
| c_siege1 | 1884 +- 86 | 38 of 129 | 100 | 58-42 | 84.7% | 27.2% (vs 12) |
| c_well9 | 1881 +- 52 | 39 of 129 | 260 | 138-122 | 84.5% | 26.8% (vs 12) |
| c_end2 | 1874 +- 86 | 40 of 129 | 100 | 57-43 | 84.3% | 26.1% (vs 12) |
| c_open1 | 1863 +- 85 | 41 of 129 | 100 | 56-44 | 83.8% | 25.0% (vs 12) |
| c_flee3 | 1863 +- 85 | 42 of 129 | 100 | 56-44 | 83.8% | 25.0% (vs 12) |
| c_anc3 | 1859 +- 65 | 43 of 129 | 163 | 88-75 | 83.7% | 24.5% (vs 12) |
| c_aura2 | 1858 +- 48 | 44 of 129 | 314 | 162-152 | 83.6% | 24.5% (vs 12) |
| c_nav5 | 1801 +- 75 | 46 of 129 | 126 | 61-65 | 81.3% | 21.2% (vs 13) |
| c_nav6 | 1785 +- 74 | 48 of 129 | 129 | 58-71 | 80.6% | 21.9% (vs 14) |
| c_nav4 | 1763 +- 56 | 50 of 129 | 221 | 108-113 | 79.6% | 21.8% (vs 15) |
| c_swarm1 | 1683 +- 52 | 55 of 129 | 271 | 128-143 | 76.0% | 22.2% (vs 19) |
| c_line8a | 1640 +- 75 | 59 of 129 | 139 | 47-92 | 74.0% | 22.4% (vs 22) |
| g_iter0 | 1619 +- 52 | 60 of 129 | 456 | 230-226 | 73.0% | 20.7% (vs 22) |
| c_line6 | 1603 +- 91 | 61 of 129 | 100 | 32-68 | 72.2% | 19.4% (vs 22) |
| c_line7m | 1591 +- 92 | 64 of 129 | 100 | 31-69 | 71.6% | 21.1% (vs 24) |
| c_line5 | 1553 +- 94 | 69 of 129 | 100 | 28-72 | 69.7% | 22.0% (vs 28) |
| c_line4 | 1513 +- 97 | 71 of 129 | 100 | 25-75 | 67.7% | 19.9% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_hr1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2196 | 57 | 257 | 178-79 | 22% (c_mend2 2-7*) |
| 2 | awesomelemonade.finalBot | 2170 | 41 | 679 | 523-156 | 40% (c_hr1 4-6*) |
| 3 | IvanGeffner.fortytwo | 2157 | 53 | 292 | 192-100 | 33% (c_gp1 1-2*) |
| 4 | carlguo866.submit26_final | 2127 | 54 | 270 | 164-106 | 0% (c_mend2 0-3*) |
| 5 | vrangr1.AFinalsBot | 2094 | 38 | 688 | 486-202 | 50% (c_hr1 5-5*) |
| 6 | AnOvercookedFork.quals | 2065 | 51 | 301 | 187-114 | 17% (c_gp1 1-5*) |
| 7 | **us:c_rot1** | 2036 | 90 | 100 | 72-28 |  |
| 8 | **us:c_hr1** | 2036 | 90 | 100 | 72-28 |  |
| 9 | pranayagra.finalbotfinaltwo | 2025 | 50 | 311 | 192-119 | 50% (c_gp1 4-4*) |
| 10 | **us:c_hunt1** | 2025 | 90 | 100 | 71-29 |  |
| 11 | georgezhang02.FB_ZZZ | 2024 | 49 | 316 | 199-117 | 50% (c_gp1 3-3*) |
| 12 | **us:c_gp1** | 2011 | 59 | 205 | 126-79 |  |
| 13 | pranayagra.finalbotfinal | 2007 | 35 | 799 | 501-298 | 50% (c_hr1 5-5*) |
| 14 | battlecode-archive.sprintBot | 1994 | 50 | 312 | 188-124 | 53% (c_gp1 8-7*) |
| 15 | jmerle.camel_case_v30_final | 1993 | 35 | 759 | 480-279 | 40% (c_hr1 4-6*) |
| 16 | **us:c_expl1** | 1991 | 88 | 100 | 68-32 |  |
| 17 | **us:c_adlo2** | 1991 | 88 | 100 | 68-32 |  |
| 18 | **us:c_pack1** | 1980 | 88 | 100 | 67-33 |  |
| 19 | **us:c_well5** | 1948 | 87 | 100 | 64-36 |  |
| 20 | **us:c_tune1** | 1937 | 87 | 100 | 63-37 |  |
| 21 | **us:c_blind2** | 1937 | 87 | 100 | 63-37 |  |
| 22 | **us:c_blind1** | 1937 | 87 | 100 | 63-37 |  |
| 23 | **us:c_mid1** | 1926 | 86 | 100 | 62-38 |  |
| 24 | **us:c_well10** | 1926 | 86 | 100 | 62-38 |  |
| 25 | **us:c_mend3** | 1916 | 86 | 100 | 61-39 |  |
| 26 | **us:c_spread2** | 1916 | 86 | 100 | 61-39 |  |
| 27 | **us:c_bc3** | 1916 | 86 | 100 | 61-39 |  |
| 28 | CyrilSharma.finalBot | 1912 | 44 | 414 | 237-177 | 62% (c_gp1 16-10*) |
| 29 | **us:c_well7** | 1905 | 86 | 100 | 60-40 |  |
| 30 | **us:c_scout1** | 1905 | 86 | 100 | 60-40 |  |
| 31 | **us:c_thr1** | 1905 | 86 | 100 | 60-40 |  |
| 32 | **us:c_seam1** | 1895 | 86 | 100 | 59-41 |  |
| 33 | **us:c_cap1** | 1895 | 86 | 100 | 59-41 |  |
| 34 | **us:c_seam2** | 1895 | 86 | 100 | 59-41 |  |
| 35 | **us:c_bc1** | 1889 | 65 | 164 | 97-67 |  |
| 36 | **us:c_mend2** | 1888 | 38 | 612 | 362-250 |  |
| 37 | **us:c_def3** | 1888 | 59 | 199 | 120-79 |  |
| 38 | **us:c_siege1** | 1884 | 86 | 100 | 58-42 |  |
| 39 | **us:c_well9** | 1881 | 52 | 260 | 138-122 |  |
| 40 | **us:c_end2** | 1874 | 86 | 100 | 57-43 |  |
| 41 | **us:c_open1** | 1863 | 85 | 100 | 56-44 |  |
| 42 | **us:c_flee3** | 1863 | 85 | 100 | 56-44 |  |
| 43 | **us:c_anc3** | 1859 | 65 | 163 | 88-75 |  |
| 44 | **us:c_aura2** | 1858 | 48 | 314 | 162-152 |  |
| 45 | ethanlabelle.dev | 1821 | 42 | 427 | 235-192 | 52% (c_well9 17-16) |
| 46 | **us:c_nav5** | 1801 | 75 | 126 | 61-65 |  |
| 47 | NotLLeon.v7 | 1800 | 33 | 826 | 389-437 | 70% (c_hr1 7-3*) |
| 48 | **us:c_nav6** | 1785 | 74 | 129 | 58-71 |  |
| 49 | georgezhang02.CB_tuning2 | 1775 | 33 | 832 | 376-456 | 90% (c_hr1 9-1*) |
| 50 | **us:c_nav4** | 1763 | 56 | 221 | 108-113 |  |
| 51 | britacatalin.FinalBot | 1717 | 34 | 783 | 327-456 | 80% (c_hr1 8-2*) |
| 52 | ethanlabelle.v19 | 1708 | 42 | 417 | 210-207 | 83% (c_well9 5-1*) |
| 53 | GabeG888.v8 | 1688 | 45 | 344 | 190-154 | 67% (c_well9 2-1*) |
| 54 | VarunVejalla.karel | 1687 | 42 | 433 | 216-217 | 67% (c_gp1 2-1*) |
| 55 | **us:c_swarm1** | 1683 | 52 | 271 | 128-143 |  |
| 56 | programjames.fourthbot | 1677 | 45 | 349 | 189-160 | 64% (c_mend2 7-4*) |
| 57 | GabeG888.v8o1 | 1669 | 45 | 345 | 195-150 | 33% (c_well9 1-2*) |
| 58 | VarunVejalla.ali8 | 1661 | 46 | 333 | 178-155 | 83% (c_mend2 5-1*) |
| 59 | **us:c_line8a** | 1640 | 75 | 139 | 47-92 |  |
| 60 | **us:g_iter0** | 1619 | 52 | 456 | 230-226 |  |
| 61 | **us:c_line6** | 1603 | 91 | 100 | 32-68 |  |
| 62 | DannyZhang686.pqual2 | 1599 | 43 | 382 | 196-186 | 83% (c_mend2 5-1*) |
| 63 | NicholasKelly15.gopher10 | 1596 | 46 | 322 | 176-146 | 100% (c_anc3 3-0*) |
| 64 | **us:c_line7m** | 1591 | 92 | 100 | 31-69 |  |
| 65 | louishu17.louisv10 | 1590 | 46 | 333 | 178-155 | 100% (c_bc1 3-0*) |
| 66 | SampleProvider.SPAARK | 1587 | 46 | 331 | 176-155 | 33% (c_anc3 1-2*) |
| 67 | louishu17.wouisv8 | 1584 | 45 | 354 | 186-168 | 83% (c_aura2 5-1*) |
| 68 | reeceyang.v5anaconda | 1575 | 35 | 786 | 269-517 | 100% (c_hr1 10-0*) |
| 69 | **us:c_line5** | 1553 | 94 | 100 | 28-72 |  |
| 70 | battlecode-archive.Sprint1 | 1519 | 36 | 759 | 233-526 | 100% (c_hr1 10-0*) |
| 71 | **us:c_line4** | 1513 | 97 | 100 | 25-75 |  |
| 72 | ipince.bobby | 1451 | 48 | 315 | 162-153 | 67% (c_swarm1 2-1*) |
| 73 | SteamBlizzard.newVnewME | 1428 | 43 | 384 | 194-190 | 80% (g_iter0 4-1*) |
| 74 | legobridge.tacoplayer | 1411 | 45 | 374 | 179-195 | 100% (c_mend2 6-0*) |
| 75 | TheK098.qp1_7_sprint_1 | 1394 | 45 | 373 | 203-170 | 100% (c_mend2 6-0*) |
| 76 | polyllc.poly | 1385 | 49 | 312 | 160-152 | 100% (g_iter0 2-0*) |
| 77 | ColtG5.rexv9 | 1339 | 43 | 388 | 190-198 | 100% (g_iter0 2-0*) |
| 78 | toyat522.bot5a | 1336 | 44 | 384 | 184-200 | 80% (g_iter0 4-1*) |
| 79 | elgoldie.head_v5 | 1311 | 44 | 371 | 180-191 | 100% (g_iter0 2-0*) |
| 80 | DukeBas._main | 1306 | 45 | 389 | 213-176 | 100% (c_mend2 6-0*) |
| 81 | beaverbois.USQualifiers | 1289 | 45 | 369 | 195-174 | 50% (g_iter0 1-1*) |
| 82 | Nawlej.PoonPoon | 1247 | 46 | 353 | 177-176 | 100% (g_iter0 2-0*) |
| 83 | kevinli405.maggi3_2 | 1237 | 44 | 407 | 208-199 | 100% (g_iter0 2-0*) |
| 84 | yaonam.PoonPoonv4 | 1218 | 40 | 827 | 240-587 | 100% (c_hr1 10-0*) |
| 85 | BrysonJGalapon.friday | 1198 | 44 | 376 | 194-182 | 100% (g_iter0 2-0*) |
| 86 | nail-e.Barry | 1179 | 44 | 385 | 193-192 | 100% (g_iter0 2-0*) |
| 87 | kevinli405.maggi3 | 1167 | 45 | 392 | 193-199 | 100% (g_iter0 5-0*) |
| 88 | aj-chau.attempt1 | 1166 | 44 | 403 | 210-193 | 100% (g_iter0 5-0*) |
| 89 | prisms-cs-club.prisms10 | 1133 | 45 | 401 | 205-196 | 100% (g_iter0 2-0*) |
| 90 | mama4294.currentPlayer | 1122 | 44 | 404 | 199-205 | 100% (g_iter0 2-0*) |
| 91 | ipince.bobby_v2 | 1106 | 43 | 450 | 229-221 | 67% (c_swarm1 2-1*) |
| 92 | andrewgopher.gopherbot | 1004 | 44 | 450 | 212-238 | 100% (g_iter0 2-0*) |
| 93 | JfeMak.realplayer2 | 1002 | 44 | 440 | 218-222 | 100% (g_iter0 2-0*) |
| 94 | bewuwy.deathbot4 | 1001 | 43 | 478 | 230-248 | 100% (g_iter0 2-0*) |
| 95 | BrysonJGalapon.aloha | 995 | 43 | 470 | 239-231 | 100% (c_swarm1 3-0*) |
| 96 | PSUtblock.sprint_four_player | 957 | 46 | 435 | 212-223 | 100% (g_iter0 2-0*) |
| 97 | SampleProvider.SPAARK_1_12_2023 | 933 | 45 | 483 | 251-232 | 100% (c_swarm1 3-0*) |
| 98 | Nawlej.PoonPoonv3 | 900 | 45 | 471 | 222-249 | 100% (g_iter0 5-0*) |
| 99 | SDainard-PDX.Team_Player | 892 | 46 | 429 | 200-229 | 100% (g_iter0 2-0*) |
| 100 | Juanbri02.matfisplayer1 | 889 | 45 | 470 | 233-237 | 100% (g_iter0 5-0*) |
| 101 | NolanChai.nolan_1 | 882 | 44 | 489 | 238-251 | 100% (g_iter0 2-0*) |
| 102 | andrewgopher.gopherbot1 | 860 | 46 | 444 | 199-245 | 100% (g_iter0 2-0*) |
| 103 | jyorkio.elicompbot | 847 | 45 | 455 | 222-233 | 100% (g_iter0 2-0*) |
| 104 | vontell.regressiongames | 772 | 46 | 481 | 236-245 | 100% (g_iter0 5-0*) |
| 105 | legobridge.kushalplayer | 752 | 48 | 431 | 199-232 | 100% (g_iter0 2-0*) |
| 106 | SteamBlizzard.Block | 701 | 48 | 492 | 226-266 | 100% (g_iter0 5-0*) |
| 107 | Patela171.Battlecode2023_Robot | 699 | 48 | 467 | 220-247 | 100% (g_iter0 2-0*) |
| 108 | ax-95174.MPAction | 667 | 48 | 477 | 213-264 | 100% (c_swarm1 3-0*) |
| 109 | nail-e.Dante | 622 | 49 | 502 | 251-251 | 100% (g_iter0 2-0*) |
| 110 | Chahat08.toph | 615 | 49 | 478 | 220-258 | 100% (g_iter0 2-0*) |
| 111 | michael-tyl.hqrewrite | 613 | 50 | 455 | 221-234 | 100% (g_iter0 2-0*) |
| 112 | mama4294.learningBot | 612 | 50 | 482 | 241-241 | 100% (g_iter0 2-0*) |
| 113 | JackLee9355.jackPlayer | 612 | 51 | 436 | 192-244 | 100% (g_iter0 2-0*) |
| 114 | anicolao.submission | 559 | 50 | 525 | 247-278 | 100% (g_iter0 2-0*) |
| 115 | team-remember-to-hydrate.sprint_1 | 549 | 50 | 488 | 222-266 | 100% (g_iter0 2-0*) |
| 116 | Vinceyou1.Player1 | 439 | 53 | 479 | 221-258 | 100% (g_iter0 2-0*) |
| 117 | addiesteward.elicompbot | 422 | 53 | 503 | 226-277 | 100% (g_iter0 5-0*) |
| 118 | toyat522.bot5 | 417 | 53 | 529 | 230-299 | 100% (g_iter0 2-0*) |
| 119 | michael-tyl.cc_v0_5_0_6 | 415 | 52 | 561 | 263-298 | 100% (g_iter0 2-0*) |
| 120 | Swordman51.AdeptusAstartes2 | 386 | 54 | 504 | 246-258 | 100% (g_iter0 2-0*) |
| 121 | Chahat08.lazarus | 381 | 54 | 520 | 240-280 | 100% (g_iter0 2-0*) |
| 122 | monmouth-college-cs.elicompbot | 347 | 54 | 537 | 236-301 | 100% (g_iter0 2-0*) |
| 123 | anicolao.jumbled | 260 | 57 | 524 | 240-284 | 100% (g_iter0 5-0*) |
| 124 | ShatterXD.SRNNbot | 243 | 58 | 519 | 249-270 | 100% (g_iter0 2-0*) |
| 125 | NotLLeon.player | 7 | 71 | 487 | 229-258 | 100% (g_iter0 2-0*) |
| 126 | CodeClash-ai.mysubmission | -93 | 75 | 508 | 228-280 | 100% (g_iter0 2-0*) |
| 127 | addiesteward.NDeClaw | -104 | 77 | 476 | 212-264 | 100% (g_iter0 5-0*) |
| 128 | Yooncw0223.lec3player | -416 | 87 | 442 | 78-364 | 100% (g_iter0 5-0*) |
| 129 | andrewkbank.First | -473 | 91 | 355 | 55-300 | 100% (g_iter0 2-0*) |
