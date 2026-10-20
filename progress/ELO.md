# Ladder

29240 games (8492 ours, 6 of the stock examplefuncsplayer, 20742 between field bots on the ladder replica), 28310 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 141 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_im1 (P) | 2144 +- 106 | 1 of 140 | 100 | 85-15 | 94.6% | - |
| c_fw1 (P) | 2144 +- 106 | 2 of 140 | 100 | 85-15 | 94.6% | - |
| c_ms1 (P) | 2124 +- 64 | 4 of 140 | 198 | 146-52 | 94.1% | 49.6% (vs 1) |
| c_gx1 (P) | 2113 +- 102 | 7 of 140 | 100 | 83-17 | 93.9% | 48.6% (vs 3) |
| c_eco3 | 2081 +- 65 | 9 of 140 | 179 | 116-63 | 93.1% | 44.7% (vs 4) |
| c_sm1 (P) | 2069 +- 98 | 10 of 140 | 100 | 80-20 | 92.8% | 43.2% (vs 4) |
| c_gd1 | 2046 +- 43 | 11 of 140 | 417 | 240-177 | 92.2% | 39.9% (vs 4) |
| c_adp1 | 2046 +- 56 | 12 of 140 | 232 | 139-93 | 92.2% | 39.9% (vs 4) |
| c_loose1 | 2030 +- 51 | 13 of 140 | 278 | 165-113 | 91.7% | 37.7% (vs 4) |
| c_rot1 (P) | 1969 +- 90 | 17 of 140 | 100 | 72-28 | 89.9% | 36.8% (vs 7) |
| c_hunt1 (P) | 1957 +- 90 | 19 of 140 | 100 | 71-29 | 89.5% | 37.0% (vs 8) |
| c_di1 (P) | 1957 +- 90 | 20 of 140 | 100 | 71-29 | 89.5% | 37.0% (vs 8) |
| c_gp1 | 1946 +- 58 | 21 of 140 | 205 | 126-79 | 89.2% | 35.6% (vs 8) |
| c_hr1 | 1934 +- 59 | 24 of 140 | 195 | 114-81 | 88.8% | 37.1% (vs 10) |
| c_adlo2 (P) | 1923 +- 88 | 26 of 140 | 100 | 68-32 | 88.4% | 36.8% (vs 11) |
| c_expl1 (P) | 1923 +- 88 | 27 of 140 | 100 | 68-32 | 88.4% | 36.8% (vs 11) |
| c_pack1 (P) | 1912 +- 88 | 28 of 140 | 100 | 67-33 | 88.0% | 35.4% (vs 11) |
| c_isle1 | 1896 +- 48 | 29 of 140 | 303 | 165-138 | 87.5% | 33.5% (vs 11) |
| c_well5 (P) | 1879 +- 87 | 30 of 140 | 100 | 64-36 | 86.9% | 31.4% (vs 11) |
| c_blind1 (P) | 1868 +- 86 | 31 of 140 | 100 | 63-37 | 86.5% | 30.1% (vs 11) |
| c_blind2 (P) | 1868 +- 86 | 32 of 140 | 100 | 63-37 | 86.5% | 30.1% (vs 11) |
| c_tune1 (P) | 1868 +- 86 | 33 of 140 | 100 | 63-37 | 86.5% | 30.1% (vs 11) |
| c_mid1 (P) | 1857 +- 86 | 34 of 140 | 100 | 62-38 | 86.1% | 28.9% (vs 11) |
| c_well10 (P) | 1857 +- 86 | 35 of 140 | 100 | 62-38 | 86.1% | 28.9% (vs 11) |
| c_mend3 (P) | 1846 +- 86 | 36 of 140 | 100 | 61-39 | 85.7% | 27.7% (vs 11) |
| c_bc3 (P) | 1846 +- 86 | 37 of 140 | 100 | 61-39 | 85.7% | 27.7% (vs 11) |
| c_spread2 (P) | 1846 +- 86 | 38 of 140 | 100 | 61-39 | 85.7% | 27.7% (vs 11) |
| c_scout1 (P) | 1836 +- 86 | 40 of 140 | 100 | 60-40 | 85.3% | 28.4% (vs 12) |
| c_thr1 (P) | 1836 +- 86 | 41 of 140 | 100 | 60-40 | 85.3% | 28.4% (vs 12) |
| c_well7 (P) | 1836 +- 86 | 42 of 140 | 100 | 60-40 | 85.3% | 28.4% (vs 12) |
| c_seam1 (P) | 1825 +- 86 | 43 of 140 | 100 | 59-41 | 84.9% | 27.2% (vs 12) |
| c_seam2 (P) | 1825 +- 86 | 44 of 140 | 100 | 59-41 | 84.9% | 27.2% (vs 12) |
| c_cap1 (P) | 1825 +- 86 | 45 of 140 | 100 | 59-41 | 84.9% | 27.2% (vs 12) |
| c_bc1 | 1819 +- 65 | 46 of 140 | 164 | 97-67 | 84.7% | 26.5% (vs 12) |
| c_def3 | 1819 +- 58 | 47 of 140 | 199 | 120-79 | 84.7% | 26.5% (vs 12) |
| c_mend2 | 1817 +- 37 | 48 of 140 | 612 | 362-250 | 84.6% | 26.3% (vs 12) |
| c_siege1 (P) | 1815 +- 85 | 49 of 140 | 100 | 58-42 | 84.5% | 26.1% (vs 12) |
| c_well9 | 1812 +- 51 | 50 of 140 | 260 | 138-122 | 84.4% | 25.7% (vs 12) |
| c_end2 (P) | 1804 +- 85 | 51 of 140 | 100 | 57-43 | 84.1% | 25.0% (vs 12) |
| c_open1 (P) | 1794 +- 85 | 52 of 140 | 100 | 56-44 | 83.7% | 23.9% (vs 12) |
| c_flee3 (P) | 1794 +- 85 | 53 of 140 | 100 | 56-44 | 83.7% | 23.9% (vs 12) |
| c_anc3 | 1790 +- 65 | 54 of 140 | 163 | 88-75 | 83.6% | 23.5% (vs 12) |
| c_aura2 | 1789 +- 47 | 55 of 140 | 314 | 162-152 | 83.6% | 23.5% (vs 12) |
| c_nav5 | 1731 +- 74 | 57 of 140 | 126 | 61-65 | 81.2% | 20.4% (vs 13) |
| c_nav6 | 1716 +- 74 | 59 of 140 | 129 | 58-71 | 80.5% | 21.2% (vs 14) |
| c_nav4 | 1692 +- 55 | 61 of 140 | 221 | 108-113 | 79.5% | 21.2% (vs 15) |
| c_swarm1 | 1611 +- 51 | 66 of 140 | 271 | 128-143 | 75.9% | 21.9% (vs 19) |
| c_line8a | 1569 +- 74 | 70 of 140 | 139 | 47-92 | 73.9% | 22.3% (vs 22) |
| g_iter0 | 1551 +- 52 | 71 of 140 | 456 | 230-226 | 73.0% | 20.7% (vs 22) |
| c_line6 (P) | 1532 +- 91 | 73 of 140 | 100 | 32-68 | 72.1% | 20.5% (vs 23) |
| c_line7m (P) | 1519 +- 92 | 75 of 140 | 100 | 31-69 | 71.5% | 20.8% (vs 24) |
| c_line5 (P) | 1482 +- 94 | 80 of 140 | 100 | 28-72 | 69.6% | 21.9% (vs 28) |
| c_line4 (P) | 1442 +- 97 | 82 of 140 | 100 | 25-75 | 67.6% | 19.8% (vs 29) |

(P) = panel-only: at least 90% of the build's games come from fixed panel runs (gauntlet/*-panel*), so its rating is biased high (about +34 on average, up to +82, in a refit of panel-v1 games only; panel review 2026-10-20); its rank is not a standing.

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_gd1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | **us:c_im1** (P) | 2144 | 106 | 100 | 85-15 |  |
| 2 | **us:c_fw1** (P) | 2144 | 106 | 100 | 85-15 |  |
| 3 | awesomelemonade.finalBot | 2127 | 35 | 957 | 698-259 | 32% (c_gd1 15-32) |
| 4 | **us:c_ms1** (P) | 2124 | 64 | 198 | 146-52 |  |
| 5 | carlguo866.submit26_final | 2123 | 42 | 496 | 316-180 | 25% (c_gd1 13-39) |
| 6 | maxwelljones14.MPWorking | 2117 | 45 | 392 | 245-147 | 55% (c_gd1 17-14) |
| 7 | **us:c_gx1** (P) | 2113 | 102 | 100 | 83-17 |  |
| 8 | IvanGeffner.fortytwo | 2101 | 43 | 453 | 282-171 | 36% (c_gd1 14-25) |
| 9 | **us:c_eco3** | 2081 | 65 | 179 | 116-63 |  |
| 10 | **us:c_sm1** (P) | 2069 | 98 | 100 | 80-20 |  |
| 11 | **us:c_gd1** | 2046 | 43 | 417 | 240-177 |  |
| 12 | **us:c_adp1** | 2046 | 56 | 232 | 139-93 |  |
| 13 | **us:c_loose1** | 2030 | 51 | 278 | 165-113 |  |
| 14 | vrangr1.AFinalsBot | 2014 | 33 | 923 | 580-343 | 65% (c_gd1 22-12) |
| 15 | AnOvercookedFork.quals | 2004 | 42 | 436 | 255-181 | 50% (c_gd1 13-13*) |
| 16 | pranayagra.finalbotfinaltwo | 1969 | 42 | 450 | 263-187 | 50% (c_gd1 13-13*) |
| 17 | **us:c_rot1** (P) | 1969 | 90 | 100 | 72-28 |  |
| 18 | georgezhang02.FB_ZZZ | 1967 | 41 | 465 | 275-190 | 70% (c_gd1 14-6*) |
| 19 | **us:c_hunt1** (P) | 1957 | 90 | 100 | 71-29 |  |
| 20 | **us:c_di1** (P) | 1957 | 90 | 100 | 71-29 |  |
| 21 | **us:c_gp1** | 1946 | 58 | 205 | 126-79 |  |
| 22 | battlecode-archive.sprintBot | 1940 | 42 | 445 | 255-190 | 83% (c_gd1 5-1*) |
| 23 | pranayagra.finalbotfinal | 1936 | 30 | 1055 | 603-452 | 85% (c_gd1 11-2*) |
| 24 | **us:c_hr1** | 1934 | 59 | 195 | 114-81 |  |
| 25 | jmerle.camel_case_v30_final | 1933 | 31 | 1030 | 601-429 | 60% (c_gd1 26-17) |
| 26 | **us:c_adlo2** (P) | 1923 | 88 | 100 | 68-32 |  |
| 27 | **us:c_expl1** (P) | 1923 | 88 | 100 | 68-32 |  |
| 28 | **us:c_pack1** (P) | 1912 | 88 | 100 | 67-33 |  |
| 29 | **us:c_isle1** | 1896 | 48 | 303 | 165-138 |  |
| 30 | **us:c_well5** (P) | 1879 | 87 | 100 | 64-36 |  |
| 31 | **us:c_blind1** (P) | 1868 | 86 | 100 | 63-37 |  |
| 32 | **us:c_blind2** (P) | 1868 | 86 | 100 | 63-37 |  |
| 33 | **us:c_tune1** (P) | 1868 | 86 | 100 | 63-37 |  |
| 34 | **us:c_mid1** (P) | 1857 | 86 | 100 | 62-38 |  |
| 35 | **us:c_well10** (P) | 1857 | 86 | 100 | 62-38 |  |
| 36 | **us:c_mend3** (P) | 1846 | 86 | 100 | 61-39 |  |
| 37 | **us:c_bc3** (P) | 1846 | 86 | 100 | 61-39 |  |
| 38 | **us:c_spread2** (P) | 1846 | 86 | 100 | 61-39 |  |
| 39 | CyrilSharma.finalBot | 1844 | 38 | 565 | 299-266 | 100% (c_gd1 20-0*) |
| 40 | **us:c_scout1** (P) | 1836 | 86 | 100 | 60-40 |  |
| 41 | **us:c_thr1** (P) | 1836 | 86 | 100 | 60-40 |  |
| 42 | **us:c_well7** (P) | 1836 | 86 | 100 | 60-40 |  |
| 43 | **us:c_seam1** (P) | 1825 | 86 | 100 | 59-41 |  |
| 44 | **us:c_seam2** (P) | 1825 | 86 | 100 | 59-41 |  |
| 45 | **us:c_cap1** (P) | 1825 | 86 | 100 | 59-41 |  |
| 46 | **us:c_bc1** | 1819 | 65 | 164 | 97-67 |  |
| 47 | **us:c_def3** | 1819 | 58 | 199 | 120-79 |  |
| 48 | **us:c_mend2** | 1817 | 37 | 612 | 362-250 |  |
| 49 | **us:c_siege1** (P) | 1815 | 85 | 100 | 58-42 |  |
| 50 | **us:c_well9** | 1812 | 51 | 260 | 138-122 |  |
| 51 | **us:c_end2** (P) | 1804 | 85 | 100 | 57-43 |  |
| 52 | **us:c_open1** (P) | 1794 | 85 | 100 | 56-44 |  |
| 53 | **us:c_flee3** (P) | 1794 | 85 | 100 | 56-44 |  |
| 54 | **us:c_anc3** | 1790 | 65 | 163 | 88-75 |  |
| 55 | **us:c_aura2** | 1789 | 47 | 314 | 162-152 |  |
| 56 | ethanlabelle.dev | 1747 | 38 | 497 | 271-226 | 33% (c_isle1 1-2*) |
| 57 | **us:c_nav5** | 1731 | 74 | 126 | 61-65 |  |
| 58 | NotLLeon.v7 | 1728 | 30 | 1010 | 436-574 | 90% (c_gd1 9-1*) |
| 59 | **us:c_nav6** | 1716 | 74 | 129 | 58-71 |  |
| 60 | georgezhang02.CB_tuning2 | 1698 | 30 | 1022 | 423-599 | 100% (c_gd1 10-0*) |
| 61 | **us:c_nav4** | 1692 | 55 | 221 | 108-113 |  |
| 62 | britacatalin.FinalBot | 1646 | 31 | 965 | 368-597 | 90% (c_gd1 9-1*) |
| 63 | ethanlabelle.v19 | 1628 | 39 | 485 | 241-244 | 83% (c_well9 5-1*) |
| 64 | GabeG888.v8 | 1619 | 41 | 413 | 227-186 | 67% (c_well9 2-1*) |
| 65 | VarunVejalla.karel | 1613 | 38 | 503 | 250-253 | 67% (c_gp1 2-1*) |
| 66 | **us:c_swarm1** | 1611 | 51 | 271 | 128-143 |  |
| 67 | GabeG888.v8o1 | 1610 | 41 | 418 | 233-185 | 33% (c_well9 1-2*) |
| 68 | VarunVejalla.ali8 | 1604 | 42 | 402 | 220-182 | 83% (c_mend2 5-1*) |
| 69 | programjames.fourthbot | 1588 | 41 | 421 | 222-199 | 64% (c_mend2 7-4*) |
| 70 | **us:c_line8a** | 1569 | 74 | 139 | 47-92 |  |
| 71 | **us:g_iter0** | 1551 | 52 | 456 | 230-226 |  |
| 72 | DannyZhang686.pqual2 | 1539 | 40 | 449 | 231-218 | 83% (c_mend2 5-1*) |
| 73 | **us:c_line6** (P) | 1532 | 91 | 100 | 32-68 |  |
| 74 | louishu17.wouisv8 | 1521 | 41 | 426 | 220-206 | 83% (c_aura2 5-1*) |
| 75 | **us:c_line7m** (P) | 1519 | 92 | 100 | 31-69 |  |
| 76 | NicholasKelly15.gopher10 | 1518 | 42 | 390 | 211-179 | 100% (c_anc3 3-0*) |
| 77 | louishu17.louisv10 | 1513 | 42 | 400 | 210-190 | 100% (c_bc1 3-0*) |
| 78 | SampleProvider.SPAARK | 1508 | 41 | 407 | 213-194 | 33% (c_anc3 1-2*) |
| 79 | reeceyang.v5anaconda | 1495 | 32 | 972 | 307-665 | 100% (c_gd1 10-0*) |
| 80 | **us:c_line5** (P) | 1482 | 94 | 100 | 28-72 |  |
| 81 | battlecode-archive.Sprint1 | 1451 | 33 | 939 | 276-663 | 100% (c_gd1 10-0*) |
| 82 | **us:c_line4** (P) | 1442 | 97 | 100 | 25-75 |  |
| 83 | ipince.bobby | 1380 | 43 | 388 | 194-194 | 67% (c_swarm1 2-1*) |
| 84 | SteamBlizzard.newVnewME | 1355 | 40 | 451 | 231-220 | 80% (g_iter0 4-1*) |
| 85 | TheK098.qp1_7_sprint_1 | 1343 | 41 | 444 | 243-201 | 100% (c_mend2 6-0*) |
| 86 | legobridge.tacoplayer | 1338 | 41 | 444 | 212-232 | 100% (c_mend2 6-0*) |
| 87 | polyllc.poly | 1312 | 44 | 386 | 190-196 | 100% (g_iter0 2-0*) |
| 88 | toyat522.bot5a | 1277 | 41 | 453 | 220-233 | 80% (g_iter0 4-1*) |
| 89 | ColtG5.rexv9 | 1266 | 40 | 467 | 237-230 | 100% (g_iter0 2-0*) |
| 90 | DukeBas._main | 1245 | 41 | 461 | 249-212 | 100% (c_mend2 6-0*) |
| 91 | elgoldie.head_v5 | 1245 | 40 | 437 | 214-223 | 100% (g_iter0 2-0*) |
| 92 | beaverbois.USQualifiers | 1228 | 41 | 444 | 236-208 | 50% (g_iter0 1-1*) |
| 93 | Nawlej.PoonPoon | 1169 | 43 | 425 | 209-216 | 100% (g_iter0 2-0*) |
| 94 | kevinli405.maggi3_2 | 1163 | 41 | 478 | 242-236 | 100% (g_iter0 2-0*) |
| 95 | yaonam.PoonPoonv4 | 1150 | 37 | 1014 | 285-729 | 90% (c_gd1 9-1*) |
| 96 | BrysonJGalapon.friday | 1134 | 41 | 454 | 238-216 | 100% (g_iter0 2-0*) |
| 97 | nail-e.Barry | 1118 | 41 | 460 | 236-224 | 100% (g_iter0 2-0*) |
| 98 | kevinli405.maggi3 | 1103 | 42 | 472 | 234-238 | 100% (g_iter0 5-0*) |
| 99 | aj-chau.attempt1 | 1097 | 41 | 477 | 248-229 | 100% (g_iter0 5-0*) |
| 100 | mama4294.currentPlayer | 1067 | 41 | 480 | 238-242 | 100% (g_iter0 2-0*) |
| 101 | prisms-cs-club.prisms10 | 1058 | 41 | 481 | 239-242 | 100% (g_iter0 2-0*) |
| 102 | ipince.bobby_v2 | 1032 | 41 | 523 | 256-267 | 67% (c_swarm1 2-1*) |
| 103 | JfeMak.realplayer2 | 944 | 41 | 511 | 259-252 | 100% (g_iter0 2-0*) |
| 104 | andrewgopher.gopherbot | 939 | 41 | 530 | 249-281 | 100% (g_iter0 2-0*) |
| 105 | bewuwy.deathbot4 | 934 | 41 | 549 | 269-280 | 100% (g_iter0 2-0*) |
| 106 | BrysonJGalapon.aloha | 928 | 41 | 540 | 269-271 | 100% (c_swarm1 3-0*) |
| 107 | PSUtblock.sprint_four_player | 895 | 42 | 520 | 248-272 | 100% (g_iter0 2-0*) |
| 108 | SampleProvider.SPAARK_1_12_2023 | 854 | 43 | 553 | 287-266 | 100% (c_swarm1 3-0*) |
| 109 | Nawlej.PoonPoonv3 | 831 | 43 | 540 | 260-280 | 100% (g_iter0 5-0*) |
| 110 | SDainard-PDX.Team_Player | 831 | 44 | 502 | 239-263 | 100% (g_iter0 2-0*) |
| 111 | NolanChai.nolan_1 | 814 | 42 | 563 | 274-289 | 100% (g_iter0 2-0*) |
| 112 | Juanbri02.matfisplayer1 | 810 | 43 | 541 | 268-273 | 100% (g_iter0 5-0*) |
| 113 | andrewgopher.gopherbot1 | 792 | 44 | 520 | 245-275 | 100% (g_iter0 2-0*) |
| 114 | jyorkio.elicompbot | 768 | 44 | 521 | 255-266 | 100% (g_iter0 2-0*) |
| 115 | vontell.regressiongames | 685 | 44 | 549 | 265-284 | 100% (g_iter0 5-0*) |
| 116 | legobridge.kushalplayer | 683 | 46 | 505 | 243-262 | 100% (g_iter0 2-0*) |
| 117 | SteamBlizzard.Block | 610 | 46 | 568 | 262-306 | 100% (g_iter0 5-0*) |
| 118 | Patela171.Battlecode2023_Robot | 600 | 46 | 536 | 250-286 | 100% (g_iter0 2-0*) |
| 119 | ax-95174.MPAction | 577 | 47 | 544 | 247-297 | 100% (c_swarm1 3-0*) |
| 120 | nail-e.Dante | 543 | 47 | 573 | 290-283 | 100% (g_iter0 2-0*) |
| 121 | Chahat08.toph | 535 | 47 | 551 | 257-294 | 100% (g_iter0 2-0*) |
| 122 | michael-tyl.hqrewrite | 525 | 48 | 527 | 254-273 | 100% (g_iter0 2-0*) |
| 123 | mama4294.learningBot | 524 | 48 | 557 | 273-284 | 100% (g_iter0 2-0*) |
| 124 | JackLee9355.jackPlayer | 522 | 49 | 509 | 227-282 | 100% (g_iter0 2-0*) |
| 125 | team-remember-to-hydrate.sprint_1 | 480 | 48 | 564 | 260-304 | 100% (g_iter0 2-0*) |
| 126 | anicolao.submission | 467 | 48 | 588 | 274-314 | 100% (g_iter0 2-0*) |
| 127 | Vinceyou1.Player1 | 363 | 51 | 550 | 254-296 | 100% (g_iter0 2-0*) |
| 128 | michael-tyl.cc_v0_5_0_6 | 342 | 50 | 634 | 302-332 | 100% (g_iter0 2-0*) |
| 129 | addiesteward.elicompbot | 332 | 51 | 570 | 253-317 | 100% (g_iter0 5-0*) |
| 130 | toyat522.bot5 | 324 | 51 | 607 | 267-340 | 100% (g_iter0 2-0*) |
| 131 | Swordman51.AdeptusAstartes2 | 324 | 52 | 572 | 282-290 | 100% (g_iter0 2-0*) |
| 132 | Chahat08.lazarus | 293 | 52 | 584 | 265-319 | 100% (g_iter0 2-0*) |
| 133 | monmouth-college-cs.elicompbot | 275 | 52 | 613 | 277-336 | 100% (g_iter0 2-0*) |
| 134 | anicolao.jumbled | 200 | 55 | 598 | 282-316 | 100% (g_iter0 5-0*) |
| 135 | ShatterXD.SRNNbot | 153 | 56 | 594 | 283-311 | 100% (g_iter0 2-0*) |
| 136 | NotLLeon.player | -90 | 70 | 541 | 258-283 | 100% (g_iter0 2-0*) |
| 137 | CodeClash-ai.mysubmission | -175 | 73 | 569 | 269-300 | 100% (g_iter0 2-0*) |
| 138 | addiesteward.NDeClaw | -193 | 75 | 525 | 241-284 | 100% (g_iter0 5-0*) |
| 139 | Yooncw0223.lec3player | -506 | 85 | 491 | 91-400 | 100% (g_iter0 5-0*) |
| 140 | andrewkbank.First | -581 | 88 | 419 | 60-359 | 100% (g_iter0 2-0*) |
