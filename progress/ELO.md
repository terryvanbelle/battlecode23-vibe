# Ladder

27922 games (7750 ours, 6 of the stock examplefuncsplayer, 20166 between field bots on the ladder replica), 27060 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 138 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_gd1 | 2176 +- 108 | 1 of 137 | 100 | 86-14 | 95.0% | - |
| c_gx1 | 2168 +- 122 | 2 of 137 | 90 | 80-10 | 94.8% | - |
| c_eco3 | 2090 +- 65 | 7 of 137 | 179 | 116-63 | 93.0% | 45.1% (vs 4) |
| c_sm1 | 2085 +- 97 | 8 of 137 | 100 | 80-20 | 92.8% | 44.4% (vs 4) |
| c_adp1 | 2055 +- 56 | 9 of 137 | 232 | 139-93 | 92.0% | 40.2% (vs 4) |
| c_loose1 | 2039 +- 51 | 10 of 137 | 278 | 165-113 | 91.5% | 38.0% (vs 4) |
| c_rot1 | 1985 +- 90 | 14 of 137 | 100 | 72-28 | 89.9% | 37.5% (vs 7) |
| c_di1 | 1973 +- 89 | 15 of 137 | 100 | 71-29 | 89.5% | 36.0% (vs 7) |
| c_hunt1 | 1973 +- 89 | 16 of 137 | 100 | 71-29 | 89.5% | 36.0% (vs 7) |
| c_gp1 | 1963 +- 58 | 18 of 137 | 205 | 126-79 | 89.2% | 36.5% (vs 8) |
| c_hr1 | 1950 +- 59 | 21 of 137 | 195 | 114-81 | 88.8% | 37.6% (vs 10) |
| c_adlo2 | 1939 +- 88 | 23 of 137 | 100 | 68-32 | 88.4% | 37.3% (vs 11) |
| c_expl1 | 1939 +- 88 | 24 of 137 | 100 | 68-32 | 88.4% | 37.3% (vs 11) |
| c_pack1 | 1928 +- 88 | 25 of 137 | 100 | 67-33 | 88.0% | 35.9% (vs 11) |
| c_isle1 | 1914 +- 48 | 26 of 137 | 303 | 165-138 | 87.6% | 34.1% (vs 11) |
| c_well5 | 1896 +- 87 | 27 of 137 | 100 | 64-36 | 86.9% | 31.9% (vs 11) |
| c_tune1 | 1885 +- 86 | 28 of 137 | 100 | 63-37 | 86.5% | 30.6% (vs 11) |
| c_blind1 | 1885 +- 86 | 29 of 137 | 100 | 63-37 | 86.5% | 30.6% (vs 11) |
| c_blind2 | 1885 +- 86 | 30 of 137 | 100 | 63-37 | 86.5% | 30.6% (vs 11) |
| c_mid1 | 1874 +- 86 | 31 of 137 | 100 | 62-38 | 86.1% | 29.3% (vs 11) |
| c_well10 | 1874 +- 86 | 32 of 137 | 100 | 62-38 | 86.1% | 29.3% (vs 11) |
| c_bc3 | 1863 +- 86 | 34 of 137 | 100 | 61-39 | 85.7% | 29.9% (vs 12) |
| c_spread2 | 1863 +- 86 | 35 of 137 | 100 | 61-39 | 85.7% | 29.9% (vs 12) |
| c_mend3 | 1863 +- 86 | 36 of 137 | 100 | 61-39 | 85.7% | 29.9% (vs 12) |
| c_thr1 | 1853 +- 86 | 37 of 137 | 100 | 60-40 | 85.3% | 28.7% (vs 12) |
| c_scout1 | 1853 +- 86 | 38 of 137 | 100 | 60-40 | 85.3% | 28.7% (vs 12) |
| c_well7 | 1853 +- 86 | 39 of 137 | 100 | 60-40 | 85.3% | 28.7% (vs 12) |
| c_seam1 | 1842 +- 86 | 40 of 137 | 100 | 59-41 | 84.9% | 27.5% (vs 12) |
| c_seam2 | 1842 +- 86 | 41 of 137 | 100 | 59-41 | 84.9% | 27.5% (vs 12) |
| c_cap1 | 1842 +- 86 | 42 of 137 | 100 | 59-41 | 84.9% | 27.5% (vs 12) |
| c_def3 | 1837 +- 59 | 43 of 137 | 199 | 120-79 | 84.7% | 26.9% (vs 12) |
| c_bc1 | 1836 +- 65 | 44 of 137 | 164 | 97-67 | 84.7% | 26.9% (vs 12) |
| c_mend2 | 1836 +- 37 | 45 of 137 | 612 | 362-250 | 84.7% | 26.8% (vs 12) |
| c_siege1 | 1832 +- 85 | 46 of 137 | 100 | 58-42 | 84.5% | 26.4% (vs 12) |
| c_well9 | 1830 +- 51 | 47 of 137 | 260 | 138-122 | 84.5% | 26.1% (vs 12) |
| c_end2 | 1821 +- 85 | 48 of 137 | 100 | 57-43 | 84.1% | 25.3% (vs 12) |
| c_flee3 | 1811 +- 85 | 49 of 137 | 100 | 56-44 | 83.7% | 24.2% (vs 12) |
| c_open1 | 1811 +- 85 | 50 of 137 | 100 | 56-44 | 83.7% | 24.2% (vs 12) |
| c_anc3 | 1807 +- 65 | 51 of 137 | 163 | 88-75 | 83.6% | 23.8% (vs 12) |
| c_aura2 | 1806 +- 47 | 52 of 137 | 314 | 162-152 | 83.5% | 23.7% (vs 12) |
| c_nav5 | 1749 +- 74 | 54 of 137 | 126 | 61-65 | 81.2% | 20.7% (vs 13) |
| c_nav6 | 1734 +- 74 | 56 of 137 | 129 | 58-71 | 80.5% | 21.5% (vs 14) |
| c_nav4 | 1711 +- 56 | 58 of 137 | 221 | 108-113 | 79.6% | 21.5% (vs 15) |
| c_swarm1 | 1630 +- 52 | 63 of 137 | 271 | 128-143 | 75.9% | 22.0% (vs 19) |
| c_line8a | 1587 +- 74 | 67 of 137 | 139 | 47-92 | 73.9% | 22.3% (vs 22) |
| g_iter0 | 1569 +- 52 | 68 of 137 | 456 | 230-226 | 73.0% | 20.8% (vs 22) |
| c_line6 | 1549 +- 91 | 70 of 137 | 100 | 32-68 | 72.0% | 20.5% (vs 23) |
| c_line7m | 1537 +- 92 | 73 of 137 | 100 | 31-69 | 71.4% | 21.9% (vs 25) |
| c_line5 | 1499 +- 94 | 77 of 137 | 100 | 28-72 | 69.6% | 21.9% (vs 28) |
| c_line4 | 1459 +- 97 | 79 of 137 | 100 | 25-75 | 67.5% | 19.7% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_gd1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | **us:c_gd1** | 2176 | 108 | 100 | 86-14 |  |
| 2 | **us:c_gx1** | 2168 | 122 | 90 | 80-10 |  |
| 3 | maxwelljones14.MPWorking | 2143 | 49 | 340 | 223-117 | 44% (c_adp1 4-5*) |
| 4 | awesomelemonade.finalBot | 2131 | 36 | 859 | 635-224 | 50% (c_gd1 5-5*) |
| 5 | carlguo866.submit26_final | 2112 | 45 | 423 | 261-162 | 30% (c_adp1 9-21) |
| 6 | IvanGeffner.fortytwo | 2111 | 46 | 393 | 248-145 | 29% (c_adp1 9-22) |
| 7 | **us:c_eco3** | 2090 | 65 | 179 | 116-63 |  |
| 8 | **us:c_sm1** | 2085 | 97 | 100 | 80-20 |  |
| 9 | **us:c_adp1** | 2055 | 56 | 232 | 139-93 |  |
| 10 | **us:c_loose1** | 2039 | 51 | 278 | 165-113 |  |
| 11 | vrangr1.AFinalsBot | 2034 | 34 | 851 | 556-295 | 70% (c_gd1 7-3*) |
| 12 | AnOvercookedFork.quals | 2012 | 45 | 388 | 231-157 | 50% (c_loose1 9-9*) |
| 13 | georgezhang02.FB_ZZZ | 1989 | 43 | 423 | 259-164 | 67% (c_adp1 2-1*) |
| 14 | **us:c_rot1** | 1985 | 90 | 100 | 72-28 |  |
| 15 | **us:c_di1** | 1973 | 89 | 100 | 71-29 |  |
| 16 | **us:c_hunt1** | 1973 | 89 | 100 | 71-29 |  |
| 17 | pranayagra.finalbotfinaltwo | 1973 | 44 | 403 | 236-167 | 80% (c_adp1 12-3*) |
| 18 | **us:c_gp1** | 1963 | 58 | 205 | 126-79 |  |
| 19 | battlecode-archive.sprintBot | 1960 | 42 | 436 | 254-182 | 56% (c_loose1 5-4*) |
| 20 | pranayagra.finalbotfinal | 1957 | 31 | 1011 | 595-416 | 90% (c_gd1 9-1*) |
| 21 | **us:c_hr1** | 1950 | 59 | 195 | 114-81 |  |
| 22 | jmerle.camel_case_v30_final | 1946 | 32 | 952 | 572-380 | 80% (c_gd1 8-2*) |
| 23 | **us:c_adlo2** | 1939 | 88 | 100 | 68-32 |  |
| 24 | **us:c_expl1** | 1939 | 88 | 100 | 68-32 |  |
| 25 | **us:c_pack1** | 1928 | 88 | 100 | 67-33 |  |
| 26 | **us:c_isle1** | 1914 | 48 | 303 | 165-138 |  |
| 27 | **us:c_well5** | 1896 | 87 | 100 | 64-36 |  |
| 28 | **us:c_tune1** | 1885 | 86 | 100 | 63-37 |  |
| 29 | **us:c_blind1** | 1885 | 86 | 100 | 63-37 |  |
| 30 | **us:c_blind2** | 1885 | 86 | 100 | 63-37 |  |
| 31 | **us:c_mid1** | 1874 | 86 | 100 | 62-38 |  |
| 32 | **us:c_well10** | 1874 | 86 | 100 | 62-38 |  |
| 33 | CyrilSharma.finalBot | 1868 | 39 | 524 | 291-233 | 67% (c_loose1 6-3*) |
| 34 | **us:c_bc3** | 1863 | 86 | 100 | 61-39 |  |
| 35 | **us:c_spread2** | 1863 | 86 | 100 | 61-39 |  |
| 36 | **us:c_mend3** | 1863 | 86 | 100 | 61-39 |  |
| 37 | **us:c_thr1** | 1853 | 86 | 100 | 60-40 |  |
| 38 | **us:c_scout1** | 1853 | 86 | 100 | 60-40 |  |
| 39 | **us:c_well7** | 1853 | 86 | 100 | 60-40 |  |
| 40 | **us:c_seam1** | 1842 | 86 | 100 | 59-41 |  |
| 41 | **us:c_seam2** | 1842 | 86 | 100 | 59-41 |  |
| 42 | **us:c_cap1** | 1842 | 86 | 100 | 59-41 |  |
| 43 | **us:c_def3** | 1837 | 59 | 199 | 120-79 |  |
| 44 | **us:c_bc1** | 1836 | 65 | 164 | 97-67 |  |
| 45 | **us:c_mend2** | 1836 | 37 | 612 | 362-250 |  |
| 46 | **us:c_siege1** | 1832 | 85 | 100 | 58-42 |  |
| 47 | **us:c_well9** | 1830 | 51 | 260 | 138-122 |  |
| 48 | **us:c_end2** | 1821 | 85 | 100 | 57-43 |  |
| 49 | **us:c_flee3** | 1811 | 85 | 100 | 56-44 |  |
| 50 | **us:c_open1** | 1811 | 85 | 100 | 56-44 |  |
| 51 | **us:c_anc3** | 1807 | 65 | 163 | 88-75 |  |
| 52 | **us:c_aura2** | 1806 | 47 | 314 | 162-152 |  |
| 53 | ethanlabelle.dev | 1762 | 39 | 487 | 262-225 | 33% (c_isle1 1-2*) |
| 54 | **us:c_nav5** | 1749 | 74 | 126 | 61-65 |  |
| 55 | NotLLeon.v7 | 1748 | 30 | 967 | 430-537 | 90% (c_gd1 9-1*) |
| 56 | **us:c_nav6** | 1734 | 74 | 129 | 58-71 |  |
| 57 | georgezhang02.CB_tuning2 | 1718 | 30 | 981 | 416-565 | 100% (c_gd1 10-0*) |
| 58 | **us:c_nav4** | 1711 | 56 | 221 | 108-113 |  |
| 59 | britacatalin.FinalBot | 1663 | 31 | 925 | 361-564 | 90% (c_gd1 9-1*) |
| 60 | ethanlabelle.v19 | 1647 | 39 | 474 | 236-238 | 83% (c_well9 5-1*) |
| 61 | GabeG888.v8 | 1641 | 41 | 402 | 223-179 | 67% (c_well9 2-1*) |
| 62 | VarunVejalla.karel | 1636 | 39 | 492 | 244-248 | 67% (c_gp1 2-1*) |
| 63 | **us:c_swarm1** | 1630 | 52 | 271 | 128-143 |  |
| 64 | GabeG888.v8o1 | 1627 | 41 | 403 | 228-175 | 33% (c_well9 1-2*) |
| 65 | VarunVejalla.ali8 | 1616 | 42 | 390 | 209-181 | 83% (c_mend2 5-1*) |
| 66 | programjames.fourthbot | 1614 | 41 | 411 | 221-190 | 64% (c_mend2 7-4*) |
| 67 | **us:c_line8a** | 1587 | 74 | 139 | 47-92 |  |
| 68 | **us:g_iter0** | 1569 | 52 | 456 | 230-226 |  |
| 69 | DannyZhang686.pqual2 | 1558 | 40 | 440 | 227-213 | 83% (c_mend2 5-1*) |
| 70 | **us:c_line6** | 1549 | 91 | 100 | 32-68 |  |
| 71 | louishu17.wouisv8 | 1541 | 42 | 414 | 216-198 | 83% (c_aura2 5-1*) |
| 72 | NicholasKelly15.gopher10 | 1538 | 42 | 380 | 207-173 | 100% (c_anc3 3-0*) |
| 73 | **us:c_line7m** | 1537 | 92 | 100 | 31-69 |  |
| 74 | louishu17.louisv10 | 1535 | 42 | 388 | 204-184 | 100% (c_bc1 3-0*) |
| 75 | SampleProvider.SPAARK | 1529 | 42 | 393 | 207-186 | 33% (c_anc3 1-2*) |
| 76 | reeceyang.v5anaconda | 1511 | 32 | 930 | 297-633 | 100% (c_gd1 10-0*) |
| 77 | **us:c_line5** | 1499 | 94 | 100 | 28-72 |  |
| 78 | battlecode-archive.Sprint1 | 1468 | 34 | 897 | 268-629 | 100% (c_gd1 10-0*) |
| 79 | **us:c_line4** | 1459 | 97 | 100 | 25-75 |  |
| 80 | ipince.bobby | 1402 | 43 | 377 | 189-188 | 67% (c_swarm1 2-1*) |
| 81 | SteamBlizzard.newVnewME | 1372 | 40 | 440 | 224-216 | 80% (g_iter0 4-1*) |
| 82 | TheK098.qp1_7_sprint_1 | 1360 | 41 | 433 | 236-197 | 100% (c_mend2 6-0*) |
| 83 | legobridge.tacoplayer | 1357 | 42 | 432 | 208-224 | 100% (c_mend2 6-0*) |
| 84 | polyllc.poly | 1330 | 45 | 370 | 182-188 | 100% (g_iter0 2-0*) |
| 85 | toyat522.bot5a | 1300 | 41 | 441 | 219-222 | 80% (g_iter0 4-1*) |
| 86 | ColtG5.rexv9 | 1280 | 41 | 449 | 224-225 | 100% (g_iter0 2-0*) |
| 87 | DukeBas._main | 1264 | 42 | 447 | 242-205 | 100% (c_mend2 6-0*) |
| 88 | elgoldie.head_v5 | 1263 | 41 | 427 | 210-217 | 100% (g_iter0 2-0*) |
| 89 | beaverbois.USQualifiers | 1246 | 42 | 426 | 226-200 | 50% (g_iter0 1-1*) |
| 90 | Nawlej.PoonPoon | 1186 | 43 | 413 | 201-212 | 100% (g_iter0 2-0*) |
| 91 | kevinli405.maggi3_2 | 1180 | 41 | 466 | 232-234 | 100% (g_iter0 2-0*) |
| 92 | yaonam.PoonPoonv4 | 1171 | 38 | 973 | 281-692 | 90% (c_gd1 9-1*) |
| 93 | BrysonJGalapon.friday | 1154 | 41 | 442 | 232-210 | 100% (g_iter0 2-0*) |
| 94 | nail-e.Barry | 1135 | 41 | 449 | 228-221 | 100% (g_iter0 2-0*) |
| 95 | kevinli405.maggi3 | 1122 | 42 | 455 | 222-233 | 100% (g_iter0 5-0*) |
| 96 | aj-chau.attempt1 | 1114 | 41 | 462 | 238-224 | 100% (g_iter0 5-0*) |
| 97 | mama4294.currentPlayer | 1089 | 41 | 465 | 231-234 | 100% (g_iter0 2-0*) |
| 98 | prisms-cs-club.prisms10 | 1080 | 42 | 464 | 231-233 | 100% (g_iter0 2-0*) |
| 99 | ipince.bobby_v2 | 1057 | 41 | 512 | 252-260 | 67% (c_swarm1 2-1*) |
| 100 | JfeMak.realplayer2 | 966 | 42 | 497 | 253-244 | 100% (g_iter0 2-0*) |
| 101 | andrewgopher.gopherbot | 961 | 41 | 516 | 242-274 | 100% (g_iter0 2-0*) |
| 102 | bewuwy.deathbot4 | 958 | 41 | 539 | 264-275 | 100% (g_iter0 2-0*) |
| 103 | BrysonJGalapon.aloha | 956 | 41 | 525 | 268-257 | 100% (c_swarm1 3-0*) |
| 104 | PSUtblock.sprint_four_player | 919 | 43 | 504 | 242-262 | 100% (g_iter0 2-0*) |
| 105 | SampleProvider.SPAARK_1_12_2023 | 881 | 43 | 543 | 283-260 | 100% (c_swarm1 3-0*) |
| 106 | Nawlej.PoonPoonv3 | 857 | 43 | 528 | 253-275 | 100% (g_iter0 5-0*) |
| 107 | SDainard-PDX.Team_Player | 854 | 44 | 484 | 230-254 | 100% (g_iter0 2-0*) |
| 108 | NolanChai.nolan_1 | 840 | 42 | 549 | 267-282 | 100% (g_iter0 2-0*) |
| 109 | Juanbri02.matfisplayer1 | 836 | 43 | 529 | 264-265 | 100% (g_iter0 5-0*) |
| 110 | andrewgopher.gopherbot1 | 815 | 44 | 502 | 233-269 | 100% (g_iter0 2-0*) |
| 111 | jyorkio.elicompbot | 791 | 44 | 510 | 246-264 | 100% (g_iter0 2-0*) |
| 112 | vontell.regressiongames | 712 | 44 | 538 | 260-278 | 100% (g_iter0 5-0*) |
| 113 | legobridge.kushalplayer | 708 | 46 | 488 | 235-253 | 100% (g_iter0 2-0*) |
| 114 | SteamBlizzard.Block | 642 | 46 | 554 | 260-294 | 100% (g_iter0 5-0*) |
| 115 | Patela171.Battlecode2023_Robot | 626 | 46 | 528 | 244-284 | 100% (g_iter0 2-0*) |
| 116 | ax-95174.MPAction | 605 | 47 | 532 | 241-291 | 100% (c_swarm1 3-0*) |
| 117 | nail-e.Dante | 572 | 47 | 561 | 285-276 | 100% (g_iter0 2-0*) |
| 118 | Chahat08.toph | 565 | 47 | 536 | 252-284 | 100% (g_iter0 2-0*) |
| 119 | JackLee9355.jackPlayer | 553 | 49 | 497 | 222-275 | 100% (g_iter0 2-0*) |
| 120 | michael-tyl.hqrewrite | 552 | 48 | 515 | 247-268 | 100% (g_iter0 2-0*) |
| 121 | mama4294.learningBot | 551 | 48 | 545 | 265-280 | 100% (g_iter0 2-0*) |
| 122 | team-remember-to-hydrate.sprint_1 | 505 | 48 | 549 | 252-297 | 100% (g_iter0 2-0*) |
| 123 | anicolao.submission | 495 | 48 | 576 | 270-306 | 100% (g_iter0 2-0*) |
| 124 | Vinceyou1.Player1 | 389 | 51 | 538 | 249-289 | 100% (g_iter0 2-0*) |
| 125 | michael-tyl.cc_v0_5_0_6 | 366 | 50 | 623 | 297-326 | 100% (g_iter0 2-0*) |
| 126 | addiesteward.elicompbot | 359 | 51 | 559 | 248-311 | 100% (g_iter0 5-0*) |
| 127 | toyat522.bot5 | 353 | 51 | 593 | 260-333 | 100% (g_iter0 2-0*) |
| 128 | Swordman51.AdeptusAstartes2 | 344 | 52 | 559 | 274-285 | 100% (g_iter0 2-0*) |
| 129 | Chahat08.lazarus | 322 | 52 | 575 | 262-313 | 100% (g_iter0 2-0*) |
| 130 | monmouth-college-cs.elicompbot | 298 | 52 | 599 | 268-331 | 100% (g_iter0 2-0*) |
| 131 | anicolao.jumbled | 220 | 55 | 583 | 273-310 | 100% (g_iter0 5-0*) |
| 132 | ShatterXD.SRNNbot | 181 | 56 | 579 | 278-301 | 100% (g_iter0 2-0*) |
| 133 | NotLLeon.player | -63 | 70 | 535 | 254-281 | 100% (g_iter0 2-0*) |
| 134 | CodeClash-ai.mysubmission | -149 | 73 | 561 | 262-299 | 100% (g_iter0 2-0*) |
| 135 | addiesteward.NDeClaw | -167 | 75 | 518 | 237-281 | 100% (g_iter0 5-0*) |
| 136 | Yooncw0223.lec3player | -479 | 85 | 483 | 89-394 | 100% (g_iter0 5-0*) |
| 137 | andrewkbank.First | -552 | 88 | 408 | 59-349 | 100% (g_iter0 2-0*) |
