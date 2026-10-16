# Ladder

22591 games (5638 ours, 6 of the stock examplefuncsplayer, 16947 between field bots on the ladder replica), 22005 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 125 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_gp1 | 2044 +- 86 | 9 of 124 | 106 | 73-33 | 89.3% | 37.2% (vs 8) |
| c_pack1 | 2010 +- 88 | 13 of 124 | 100 | 67-33 | 88.1% | 36.9% (vs 11) |
| c_well5 | 1978 +- 87 | 14 of 124 | 100 | 64-36 | 87.0% | 32.9% (vs 11) |
| c_blind1 | 1968 +- 87 | 15 of 124 | 100 | 63-37 | 86.6% | 31.6% (vs 11) |
| c_tune1 | 1968 +- 87 | 16 of 124 | 100 | 63-37 | 86.6% | 31.6% (vs 11) |
| c_blind2 | 1968 +- 87 | 17 of 124 | 100 | 63-37 | 86.6% | 31.6% (vs 11) |
| c_well10 | 1957 +- 86 | 18 of 124 | 100 | 62-38 | 86.2% | 30.3% (vs 11) |
| c_mid1 | 1957 +- 86 | 19 of 124 | 100 | 62-38 | 86.2% | 30.3% (vs 11) |
| c_mend3 | 1946 +- 86 | 20 of 124 | 100 | 61-39 | 85.8% | 29.1% (vs 11) |
| c_spread2 | 1946 +- 86 | 21 of 124 | 100 | 61-39 | 85.8% | 29.1% (vs 11) |
| c_bc3 | 1946 +- 86 | 22 of 124 | 100 | 61-39 | 85.8% | 29.1% (vs 11) |
| c_thr1 | 1936 +- 86 | 24 of 124 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_well7 | 1936 +- 86 | 25 of 124 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_scout1 | 1936 +- 86 | 26 of 124 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_seam1 | 1926 +- 86 | 27 of 124 | 100 | 59-41 | 85.0% | 28.5% (vs 12) |
| c_cap1 | 1926 +- 86 | 28 of 124 | 100 | 59-41 | 85.0% | 28.5% (vs 12) |
| c_seam2 | 1926 +- 86 | 29 of 124 | 100 | 59-41 | 85.0% | 28.5% (vs 12) |
| c_mend2 | 1921 +- 39 | 30 of 124 | 612 | 362-250 | 84.8% | 28.0% (vs 12) |
| c_bc1 | 1921 +- 65 | 31 of 124 | 164 | 97-67 | 84.8% | 27.9% (vs 12) |
| c_def3 | 1918 +- 59 | 32 of 124 | 199 | 120-79 | 84.7% | 27.7% (vs 12) |
| c_siege1 | 1915 +- 86 | 33 of 124 | 100 | 58-42 | 84.6% | 27.4% (vs 12) |
| c_well9 | 1911 +- 52 | 34 of 124 | 260 | 138-122 | 84.5% | 27.0% (vs 12) |
| c_end2 | 1905 +- 86 | 35 of 124 | 100 | 57-43 | 84.2% | 26.2% (vs 12) |
| c_flee3 | 1894 +- 85 | 36 of 124 | 100 | 56-44 | 83.8% | 25.1% (vs 12) |
| c_open1 | 1894 +- 85 | 37 of 124 | 100 | 56-44 | 83.8% | 25.1% (vs 12) |
| c_anc3 | 1890 +- 65 | 38 of 124 | 163 | 88-75 | 83.6% | 24.7% (vs 12) |
| c_aura2 | 1889 +- 48 | 39 of 124 | 314 | 162-152 | 83.6% | 24.6% (vs 12) |
| c_nav5 | 1831 +- 75 | 41 of 124 | 126 | 61-65 | 81.2% | 21.3% (vs 13) |
| c_nav6 | 1816 +- 74 | 43 of 124 | 129 | 58-71 | 80.5% | 21.9% (vs 14) |
| c_nav4 | 1795 +- 56 | 45 of 124 | 221 | 108-113 | 79.6% | 21.9% (vs 15) |
| c_swarm1 | 1716 +- 52 | 50 of 124 | 271 | 128-143 | 76.0% | 22.3% (vs 19) |
| c_line8a | 1672 +- 75 | 54 of 124 | 139 | 47-92 | 73.9% | 22.5% (vs 22) |
| g_iter0 | 1653 +- 52 | 55 of 124 | 456 | 230-226 | 73.0% | 20.8% (vs 22) |
| c_line6 | 1636 +- 91 | 56 of 124 | 100 | 32-68 | 72.1% | 19.5% (vs 22) |
| c_line7m | 1624 +- 92 | 61 of 124 | 100 | 31-69 | 71.5% | 23.3% (vs 26) |
| c_line5 | 1586 +- 94 | 64 of 124 | 100 | 28-72 | 69.7% | 22.0% (vs 28) |
| c_line4 | 1546 +- 97 | 66 of 124 | 100 | 25-75 | 67.6% | 19.8% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_gp1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2221 | 59 | 245 | 169-76 | 22% (c_mend2 2-7*) |
| 2 | IvanGeffner.fortytwo | 2196 | 55 | 281 | 189-92 | 13% (c_mend2 3-20*) |
| 3 | awesomelemonade.finalBot | 2195 | 43 | 618 | 478-140 | 30% (c_gp1 3-7*) |
| 4 | carlguo866.submit26_final | 2158 | 56 | 258 | 158-100 | 0% (c_mend2 0-3*) |
| 5 | vrangr1.AFinalsBot | 2131 | 41 | 623 | 452-171 | 50% (c_gp1 5-5*) |
| 6 | AnOvercookedFork.quals | 2093 | 53 | 287 | 178-109 | 27% (c_mend2 4-11*) |
| 7 | pranayagra.finalbotfinaltwo | 2057 | 52 | 297 | 186-111 | 33% (c_gp1 1-2*) |
| 8 | georgezhang02.FB_ZZZ | 2051 | 51 | 299 | 188-111 | 33% (c_well9 4-8*) |
| 9 | **us:c_gp1** | 2044 | 86 | 106 | 73-33 |  |
| 10 | pranayagra.finalbotfinal | 2040 | 37 | 729 | 469-260 | 38% (c_gp1 5-8*) |
| 11 | battlecode-archive.sprintBot | 2025 | 52 | 290 | 178-112 | 17% (c_well9 1-5*) |
| 12 | jmerle.camel_case_v30_final | 2014 | 37 | 682 | 434-248 | 40% (c_gp1 4-6*) |
| 13 | **us:c_pack1** | 2010 | 88 | 100 | 67-33 |  |
| 14 | **us:c_well5** | 1978 | 87 | 100 | 64-36 |  |
| 15 | **us:c_blind1** | 1968 | 87 | 100 | 63-37 |  |
| 16 | **us:c_tune1** | 1968 | 87 | 100 | 63-37 |  |
| 17 | **us:c_blind2** | 1968 | 87 | 100 | 63-37 |  |
| 18 | **us:c_well10** | 1957 | 86 | 100 | 62-38 |  |
| 19 | **us:c_mid1** | 1957 | 86 | 100 | 62-38 |  |
| 20 | **us:c_mend3** | 1946 | 86 | 100 | 61-39 |  |
| 21 | **us:c_spread2** | 1946 | 86 | 100 | 61-39 |  |
| 22 | **us:c_bc3** | 1946 | 86 | 100 | 61-39 |  |
| 23 | CyrilSharma.finalBot | 1941 | 46 | 377 | 220-157 | 35% (c_well9 12-22) |
| 24 | **us:c_thr1** | 1936 | 86 | 100 | 60-40 |  |
| 25 | **us:c_well7** | 1936 | 86 | 100 | 60-40 |  |
| 26 | **us:c_scout1** | 1936 | 86 | 100 | 60-40 |  |
| 27 | **us:c_seam1** | 1926 | 86 | 100 | 59-41 |  |
| 28 | **us:c_cap1** | 1926 | 86 | 100 | 59-41 |  |
| 29 | **us:c_seam2** | 1926 | 86 | 100 | 59-41 |  |
| 30 | **us:c_mend2** | 1921 | 39 | 612 | 362-250 |  |
| 31 | **us:c_bc1** | 1921 | 65 | 164 | 97-67 |  |
| 32 | **us:c_def3** | 1918 | 59 | 199 | 120-79 |  |
| 33 | **us:c_siege1** | 1915 | 86 | 100 | 58-42 |  |
| 34 | **us:c_well9** | 1911 | 52 | 260 | 138-122 |  |
| 35 | **us:c_end2** | 1905 | 86 | 100 | 57-43 |  |
| 36 | **us:c_flee3** | 1894 | 85 | 100 | 56-44 |  |
| 37 | **us:c_open1** | 1894 | 85 | 100 | 56-44 |  |
| 38 | **us:c_anc3** | 1890 | 65 | 163 | 88-75 |  |
| 39 | **us:c_aura2** | 1889 | 48 | 314 | 162-152 |  |
| 40 | ethanlabelle.dev | 1855 | 43 | 416 | 230-186 | 52% (c_well9 17-16) |
| 41 | **us:c_nav5** | 1831 | 75 | 126 | 61-65 |  |
| 42 | NotLLeon.v7 | 1828 | 34 | 761 | 368-393 | 70% (c_gp1 7-3*) |
| 43 | **us:c_nav6** | 1816 | 74 | 129 | 58-71 |  |
| 44 | georgezhang02.CB_tuning2 | 1812 | 34 | 770 | 363-407 | 100% (c_gp1 10-0*) |
| 45 | **us:c_nav4** | 1795 | 56 | 221 | 108-113 |  |
| 46 | britacatalin.FinalBot | 1746 | 35 | 721 | 312-409 | 80% (c_gp1 8-2*) |
| 47 | ethanlabelle.v19 | 1743 | 43 | 406 | 205-201 | 83% (c_well9 5-1*) |
| 48 | GabeG888.v8 | 1724 | 46 | 333 | 185-148 | 67% (c_well9 2-1*) |
| 49 | VarunVejalla.karel | 1722 | 43 | 419 | 213-206 | 100% (c_well9 3-0*) |
| 50 | **us:c_swarm1** | 1716 | 52 | 271 | 128-143 |  |
| 51 | programjames.fourthbot | 1711 | 46 | 337 | 184-153 | 64% (c_mend2 7-4*) |
| 52 | GabeG888.v8o1 | 1698 | 46 | 333 | 185-148 | 33% (c_well9 1-2*) |
| 53 | VarunVejalla.ali8 | 1695 | 47 | 321 | 171-150 | 83% (c_mend2 5-1*) |
| 54 | **us:c_line8a** | 1672 | 75 | 139 | 47-92 |  |
| 55 | **us:g_iter0** | 1653 | 52 | 456 | 230-226 |  |
| 56 | **us:c_line6** | 1636 | 91 | 100 | 32-68 |  |
| 57 | NicholasKelly15.gopher10 | 1633 | 48 | 310 | 171-139 | 100% (c_anc3 3-0*) |
| 58 | DannyZhang686.pqual2 | 1630 | 44 | 372 | 188-184 | 83% (c_mend2 5-1*) |
| 59 | louishu17.louisv10 | 1625 | 47 | 321 | 173-148 | 100% (c_bc1 3-0*) |
| 60 | SampleProvider.SPAARK | 1624 | 47 | 320 | 172-148 | 33% (c_anc3 1-2*) |
| 61 | **us:c_line7m** | 1624 | 92 | 100 | 31-69 |  |
| 62 | louishu17.wouisv8 | 1616 | 46 | 342 | 181-161 | 83% (c_aura2 5-1*) |
| 63 | reeceyang.v5anaconda | 1610 | 36 | 725 | 263-462 | 100% (c_gp1 10-0*) |
| 64 | **us:c_line5** | 1586 | 94 | 100 | 28-72 |  |
| 65 | battlecode-archive.Sprint1 | 1555 | 37 | 698 | 228-470 | 100% (c_gp1 10-0*) |
| 66 | **us:c_line4** | 1546 | 97 | 100 | 25-75 |  |
| 67 | ipince.bobby | 1485 | 49 | 305 | 157-148 | 67% (c_swarm1 2-1*) |
| 68 | SteamBlizzard.newVnewME | 1467 | 44 | 372 | 190-182 | 80% (g_iter0 4-1*) |
| 69 | legobridge.tacoplayer | 1446 | 46 | 366 | 175-191 | 100% (c_mend2 6-0*) |
| 70 | TheK098.qp1_7_sprint_1 | 1426 | 45 | 363 | 196-167 | 100% (c_mend2 6-0*) |
| 71 | polyllc.poly | 1413 | 50 | 303 | 153-150 | 100% (g_iter0 2-0*) |
| 72 | ColtG5.rexv9 | 1377 | 44 | 376 | 187-189 | 100% (g_iter0 2-0*) |
| 73 | toyat522.bot5a | 1371 | 45 | 372 | 177-195 | 80% (g_iter0 4-1*) |
| 74 | elgoldie.head_v5 | 1350 | 44 | 360 | 176-184 | 100% (g_iter0 2-0*) |
| 75 | DukeBas._main | 1342 | 45 | 377 | 207-170 | 100% (c_mend2 6-0*) |
| 76 | beaverbois.USQualifiers | 1319 | 45 | 358 | 187-171 | 50% (g_iter0 1-1*) |
| 77 | Nawlej.PoonPoon | 1281 | 47 | 342 | 172-170 | 100% (g_iter0 2-0*) |
| 78 | kevinli405.maggi3_2 | 1274 | 44 | 397 | 203-194 | 100% (g_iter0 2-0*) |
| 79 | yaonam.PoonPoonv4 | 1252 | 40 | 767 | 234-533 | 100% (c_gp1 10-0*) |
| 80 | BrysonJGalapon.friday | 1237 | 44 | 366 | 191-175 | 100% (g_iter0 2-0*) |
| 81 | nail-e.Barry | 1212 | 44 | 374 | 188-186 | 100% (g_iter0 2-0*) |
| 82 | aj-chau.attempt1 | 1204 | 44 | 392 | 204-188 | 100% (g_iter0 5-0*) |
| 83 | kevinli405.maggi3 | 1200 | 46 | 381 | 185-196 | 100% (g_iter0 5-0*) |
| 84 | prisms-cs-club.prisms10 | 1171 | 45 | 392 | 201-191 | 100% (g_iter0 2-0*) |
| 85 | mama4294.currentPlayer | 1159 | 44 | 393 | 195-198 | 100% (g_iter0 2-0*) |
| 86 | ipince.bobby_v2 | 1135 | 43 | 438 | 217-221 | 67% (c_swarm1 2-1*) |
| 87 | bewuwy.deathbot4 | 1046 | 43 | 467 | 230-237 | 100% (g_iter0 2-0*) |
| 88 | JfeMak.realplayer2 | 1042 | 44 | 429 | 213-216 | 100% (g_iter0 2-0*) |
| 89 | andrewgopher.gopherbot | 1036 | 44 | 438 | 205-233 | 100% (g_iter0 2-0*) |
| 90 | BrysonJGalapon.aloha | 1029 | 43 | 459 | 230-229 | 100% (c_swarm1 3-0*) |
| 91 | PSUtblock.sprint_four_player | 994 | 46 | 423 | 206-217 | 100% (g_iter0 2-0*) |
| 92 | SampleProvider.SPAARK_1_12_2023 | 965 | 45 | 472 | 242-230 | 100% (c_swarm1 3-0*) |
| 93 | Nawlej.PoonPoonv3 | 942 | 45 | 460 | 220-240 | 100% (g_iter0 5-0*) |
| 94 | SDainard-PDX.Team_Player | 929 | 46 | 419 | 195-224 | 100% (g_iter0 2-0*) |
| 95 | Juanbri02.matfisplayer1 | 928 | 45 | 459 | 226-233 | 100% (g_iter0 5-0*) |
| 96 | NolanChai.nolan_1 | 921 | 44 | 477 | 234-243 | 100% (g_iter0 2-0*) |
| 97 | andrewgopher.gopherbot1 | 907 | 46 | 434 | 199-235 | 100% (g_iter0 2-0*) |
| 98 | jyorkio.elicompbot | 884 | 45 | 445 | 217-228 | 100% (g_iter0 2-0*) |
| 99 | vontell.regressiongames | 810 | 46 | 470 | 230-240 | 100% (g_iter0 5-0*) |
| 100 | legobridge.kushalplayer | 790 | 48 | 421 | 194-227 | 100% (g_iter0 2-0*) |
| 101 | SteamBlizzard.Block | 742 | 48 | 481 | 224-257 | 100% (g_iter0 5-0*) |
| 102 | Patela171.Battlecode2023_Robot | 735 | 48 | 457 | 214-243 | 100% (g_iter0 2-0*) |
| 103 | ax-95174.MPAction | 709 | 48 | 465 | 208-257 | 100% (c_swarm1 3-0*) |
| 104 | nail-e.Dante | 662 | 49 | 490 | 245-245 | 100% (g_iter0 2-0*) |
| 105 | Chahat08.toph | 654 | 49 | 467 | 216-251 | 100% (g_iter0 2-0*) |
| 106 | michael-tyl.hqrewrite | 651 | 50 | 443 | 216-227 | 100% (g_iter0 2-0*) |
| 107 | JackLee9355.jackPlayer | 646 | 52 | 425 | 187-238 | 100% (g_iter0 2-0*) |
| 108 | mama4294.learningBot | 640 | 50 | 471 | 231-240 | 100% (g_iter0 2-0*) |
| 109 | anicolao.submission | 595 | 50 | 514 | 241-273 | 100% (g_iter0 2-0*) |
| 110 | team-remember-to-hydrate.sprint_1 | 584 | 51 | 477 | 217-260 | 100% (g_iter0 2-0*) |
| 111 | Vinceyou1.Player1 | 470 | 53 | 467 | 215-252 | 100% (g_iter0 2-0*) |
| 112 | addiesteward.elicompbot | 453 | 53 | 491 | 218-273 | 100% (g_iter0 5-0*) |
| 113 | toyat522.bot5 | 451 | 53 | 517 | 225-292 | 100% (g_iter0 2-0*) |
| 114 | michael-tyl.cc_v0_5_0_6 | 447 | 52 | 550 | 256-294 | 100% (g_iter0 2-0*) |
| 115 | Chahat08.lazarus | 414 | 54 | 508 | 234-274 | 100% (g_iter0 2-0*) |
| 116 | Swordman51.AdeptusAstartes2 | 411 | 54 | 492 | 238-254 | 100% (g_iter0 2-0*) |
| 117 | monmouth-college-cs.elicompbot | 381 | 54 | 528 | 233-295 | 100% (g_iter0 2-0*) |
| 118 | anicolao.jumbled | 295 | 57 | 514 | 237-277 | 100% (g_iter0 5-0*) |
| 119 | ShatterXD.SRNNbot | 277 | 58 | 508 | 242-266 | 100% (g_iter0 2-0*) |
| 120 | NotLLeon.player | 40 | 72 | 477 | 224-253 | 100% (g_iter0 2-0*) |
| 121 | CodeClash-ai.mysubmission | -64 | 75 | 500 | 222-278 | 100% (g_iter0 2-0*) |
| 122 | addiesteward.NDeClaw | -75 | 77 | 465 | 205-260 | 100% (g_iter0 5-0*) |
| 123 | Yooncw0223.lec3player | -382 | 88 | 433 | 77-356 | 100% (g_iter0 5-0*) |
| 124 | andrewkbank.First | -439 | 92 | 346 | 54-292 | 100% (g_iter0 2-0*) |
