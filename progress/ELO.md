# Ladder

22285 games (5332 ours, 6 of the stock examplefuncsplayer, 16947 between field bots on the ladder replica), 21699 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 122 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2000 +- 87 | 12 of 121 | 100 | 64-36 | 87.0% | 32.8% (vs 11) |
| c_blind2 | 1989 +- 87 | 13 of 121 | 100 | 63-37 | 86.6% | 31.5% (vs 11) |
| c_blind1 | 1989 +- 87 | 14 of 121 | 100 | 63-37 | 86.6% | 31.5% (vs 11) |
| c_mid1 | 1979 +- 87 | 15 of 121 | 100 | 62-38 | 86.2% | 30.3% (vs 11) |
| c_well10 | 1979 +- 87 | 16 of 121 | 100 | 62-38 | 86.2% | 30.3% (vs 11) |
| c_mend3 | 1968 +- 86 | 17 of 121 | 100 | 61-39 | 85.8% | 29.1% (vs 11) |
| c_bc3 | 1968 +- 86 | 18 of 121 | 100 | 61-39 | 85.8% | 29.1% (vs 11) |
| c_spread2 | 1968 +- 86 | 19 of 121 | 100 | 61-39 | 85.8% | 29.1% (vs 11) |
| c_thr1 | 1958 +- 86 | 21 of 121 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_well7 | 1958 +- 86 | 22 of 121 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_scout1 | 1958 +- 86 | 23 of 121 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_seam2 | 1947 +- 86 | 24 of 121 | 100 | 59-41 | 85.0% | 28.5% (vs 12) |
| c_seam1 | 1947 +- 86 | 25 of 121 | 100 | 59-41 | 85.0% | 28.5% (vs 12) |
| c_cap1 | 1947 +- 86 | 26 of 121 | 100 | 59-41 | 85.0% | 28.5% (vs 12) |
| c_mend2 | 1943 +- 39 | 27 of 121 | 612 | 362-250 | 84.9% | 28.0% (vs 12) |
| c_bc1 | 1942 +- 65 | 28 of 121 | 164 | 97-67 | 84.8% | 27.8% (vs 12) |
| c_def3 | 1940 +- 60 | 29 of 121 | 199 | 120-79 | 84.7% | 27.6% (vs 12) |
| c_siege1 | 1937 +- 86 | 30 of 121 | 100 | 58-42 | 84.6% | 27.3% (vs 12) |
| c_well9 | 1933 +- 52 | 31 of 121 | 260 | 138-122 | 84.5% | 26.9% (vs 12) |
| c_end2 | 1927 +- 86 | 32 of 121 | 100 | 57-43 | 84.2% | 26.2% (vs 12) |
| c_flee3 | 1916 +- 86 | 33 of 121 | 100 | 56-44 | 83.8% | 25.1% (vs 12) |
| c_open1 | 1916 +- 86 | 34 of 121 | 100 | 56-44 | 83.8% | 25.1% (vs 12) |
| c_anc3 | 1911 +- 66 | 35 of 121 | 163 | 88-75 | 83.6% | 24.6% (vs 12) |
| c_aura2 | 1911 +- 49 | 36 of 121 | 314 | 162-152 | 83.6% | 24.5% (vs 12) |
| c_nav5 | 1853 +- 75 | 38 of 121 | 126 | 61-65 | 81.2% | 21.2% (vs 13) |
| c_nav6 | 1837 +- 75 | 40 of 121 | 129 | 58-71 | 80.5% | 21.9% (vs 14) |
| c_nav4 | 1816 +- 56 | 42 of 121 | 221 | 108-113 | 79.6% | 21.8% (vs 15) |
| c_swarm1 | 1737 +- 53 | 47 of 121 | 271 | 128-143 | 76.0% | 22.3% (vs 19) |
| c_line8a | 1694 +- 75 | 51 of 121 | 139 | 47-92 | 74.0% | 22.5% (vs 22) |
| g_iter0 | 1674 +- 52 | 52 of 121 | 456 | 230-226 | 73.0% | 20.8% (vs 22) |
| c_line6 | 1657 +- 91 | 53 of 121 | 100 | 32-68 | 72.2% | 19.5% (vs 22) |
| c_line7m | 1645 +- 92 | 58 of 121 | 100 | 31-69 | 71.6% | 23.3% (vs 26) |
| c_line5 | 1607 +- 95 | 61 of 121 | 100 | 28-72 | 69.7% | 22.0% (vs 28) |
| c_line4 | 1567 +- 98 | 63 of 121 | 100 | 25-75 | 67.7% | 19.8% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_well9), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2244 | 59 | 245 | 169-76 | 22% (c_mend2 2-7*) |
| 2 | IvanGeffner.fortytwo | 2219 | 56 | 281 | 189-92 | 13% (c_mend2 3-20*) |
| 3 | awesomelemonade.finalBot | 2218 | 45 | 588 | 456-132 | 20% (c_well9 2-8*) |
| 4 | carlguo866.submit26_final | 2181 | 56 | 258 | 158-100 | 0% (c_mend2 0-3*) |
| 5 | vrangr1.AFinalsBot | 2155 | 42 | 593 | 433-160 | 20% (c_well9 2-8*) |
| 6 | AnOvercookedFork.quals | 2115 | 53 | 287 | 178-109 | 27% (c_mend2 4-11*) |
| 7 | pranayagra.finalbotfinaltwo | 2078 | 52 | 294 | 184-110 | 33% (c_well9 3-6*) |
| 8 | georgezhang02.FB_ZZZ | 2073 | 51 | 299 | 188-111 | 33% (c_well9 4-8*) |
| 9 | pranayagra.finalbotfinal | 2064 | 38 | 696 | 453-243 | 29% (c_well9 8-20*) |
| 10 | battlecode-archive.sprintBot | 2047 | 52 | 290 | 178-112 | 17% (c_well9 1-5*) |
| 11 | jmerle.camel_case_v30_final | 2035 | 38 | 652 | 418-234 | 44% (c_well9 7-9*) |
| 12 | **us:c_well5** | 2000 | 87 | 100 | 64-36 |  |
| 13 | **us:c_blind2** | 1989 | 87 | 100 | 63-37 |  |
| 14 | **us:c_blind1** | 1989 | 87 | 100 | 63-37 |  |
| 15 | **us:c_mid1** | 1979 | 87 | 100 | 62-38 |  |
| 16 | **us:c_well10** | 1979 | 87 | 100 | 62-38 |  |
| 17 | **us:c_mend3** | 1968 | 86 | 100 | 61-39 |  |
| 18 | **us:c_bc3** | 1968 | 86 | 100 | 61-39 |  |
| 19 | **us:c_spread2** | 1968 | 86 | 100 | 61-39 |  |
| 20 | CyrilSharma.finalBot | 1963 | 46 | 377 | 220-157 | 35% (c_well9 12-22) |
| 21 | **us:c_thr1** | 1958 | 86 | 100 | 60-40 |  |
| 22 | **us:c_well7** | 1958 | 86 | 100 | 60-40 |  |
| 23 | **us:c_scout1** | 1958 | 86 | 100 | 60-40 |  |
| 24 | **us:c_seam2** | 1947 | 86 | 100 | 59-41 |  |
| 25 | **us:c_seam1** | 1947 | 86 | 100 | 59-41 |  |
| 26 | **us:c_cap1** | 1947 | 86 | 100 | 59-41 |  |
| 27 | **us:c_mend2** | 1943 | 39 | 612 | 362-250 |  |
| 28 | **us:c_bc1** | 1942 | 65 | 164 | 97-67 |  |
| 29 | **us:c_def3** | 1940 | 60 | 199 | 120-79 |  |
| 30 | **us:c_siege1** | 1937 | 86 | 100 | 58-42 |  |
| 31 | **us:c_well9** | 1933 | 52 | 260 | 138-122 |  |
| 32 | **us:c_end2** | 1927 | 86 | 100 | 57-43 |  |
| 33 | **us:c_flee3** | 1916 | 86 | 100 | 56-44 |  |
| 34 | **us:c_open1** | 1916 | 86 | 100 | 56-44 |  |
| 35 | **us:c_anc3** | 1911 | 66 | 163 | 88-75 |  |
| 36 | **us:c_aura2** | 1911 | 49 | 314 | 162-152 |  |
| 37 | ethanlabelle.dev | 1876 | 43 | 416 | 230-186 | 52% (c_well9 17-16) |
| 38 | **us:c_nav5** | 1853 | 75 | 126 | 61-65 |  |
| 39 | NotLLeon.v7 | 1846 | 35 | 731 | 357-374 | 58% (c_well9 11-8*) |
| 40 | **us:c_nav6** | 1837 | 75 | 129 | 58-71 |  |
| 41 | georgezhang02.CB_tuning2 | 1835 | 35 | 740 | 357-383 | 75% (c_well9 12-4*) |
| 42 | **us:c_nav4** | 1816 | 56 | 221 | 108-113 |  |
| 43 | britacatalin.FinalBot | 1766 | 35 | 691 | 306-385 | 86% (c_well9 19-3*) |
| 44 | ethanlabelle.v19 | 1764 | 44 | 406 | 205-201 | 83% (c_well9 5-1*) |
| 45 | GabeG888.v8 | 1745 | 46 | 333 | 185-148 | 67% (c_well9 2-1*) |
| 46 | VarunVejalla.karel | 1744 | 43 | 419 | 213-206 | 100% (c_well9 3-0*) |
| 47 | **us:c_swarm1** | 1737 | 53 | 271 | 128-143 |  |
| 48 | programjames.fourthbot | 1732 | 46 | 337 | 184-153 | 64% (c_mend2 7-4*) |
| 49 | GabeG888.v8o1 | 1719 | 46 | 333 | 185-148 | 33% (c_well9 1-2*) |
| 50 | VarunVejalla.ali8 | 1716 | 47 | 321 | 171-150 | 83% (c_mend2 5-1*) |
| 51 | **us:c_line8a** | 1694 | 75 | 139 | 47-92 |  |
| 52 | **us:g_iter0** | 1674 | 52 | 456 | 230-226 |  |
| 53 | **us:c_line6** | 1657 | 91 | 100 | 32-68 |  |
| 54 | NicholasKelly15.gopher10 | 1654 | 48 | 310 | 171-139 | 100% (c_anc3 3-0*) |
| 55 | DannyZhang686.pqual2 | 1651 | 44 | 372 | 188-184 | 83% (c_mend2 5-1*) |
| 56 | louishu17.louisv10 | 1646 | 47 | 321 | 173-148 | 100% (c_bc1 3-0*) |
| 57 | SampleProvider.SPAARK | 1645 | 47 | 320 | 172-148 | 33% (c_anc3 1-2*) |
| 58 | **us:c_line7m** | 1645 | 92 | 100 | 31-69 |  |
| 59 | louishu17.wouisv8 | 1637 | 47 | 342 | 181-161 | 83% (c_aura2 5-1*) |
| 60 | reeceyang.v5anaconda | 1632 | 36 | 695 | 261-434 | 100% (c_well9 10-0*) |
| 61 | **us:c_line5** | 1607 | 95 | 100 | 28-72 |  |
| 62 | battlecode-archive.Sprint1 | 1578 | 38 | 668 | 227-441 | 100% (c_well9 10-0*) |
| 63 | **us:c_line4** | 1567 | 98 | 100 | 25-75 |  |
| 64 | ipince.bobby | 1506 | 49 | 305 | 157-148 | 67% (c_swarm1 2-1*) |
| 65 | SteamBlizzard.newVnewME | 1487 | 44 | 372 | 190-182 | 80% (g_iter0 4-1*) |
| 66 | legobridge.tacoplayer | 1466 | 46 | 366 | 175-191 | 100% (c_mend2 6-0*) |
| 67 | TheK098.qp1_7_sprint_1 | 1446 | 45 | 363 | 196-167 | 100% (c_mend2 6-0*) |
| 68 | polyllc.poly | 1433 | 50 | 303 | 153-150 | 100% (g_iter0 2-0*) |
| 69 | ColtG5.rexv9 | 1397 | 44 | 376 | 187-189 | 100% (g_iter0 2-0*) |
| 70 | toyat522.bot5a | 1391 | 45 | 372 | 177-195 | 80% (g_iter0 4-1*) |
| 71 | elgoldie.head_v5 | 1370 | 44 | 360 | 176-184 | 100% (g_iter0 2-0*) |
| 72 | DukeBas._main | 1362 | 45 | 377 | 207-170 | 100% (c_mend2 6-0*) |
| 73 | beaverbois.USQualifiers | 1339 | 45 | 358 | 187-171 | 50% (g_iter0 1-1*) |
| 74 | Nawlej.PoonPoon | 1300 | 47 | 342 | 172-170 | 100% (g_iter0 2-0*) |
| 75 | kevinli405.maggi3_2 | 1293 | 44 | 397 | 203-194 | 100% (g_iter0 2-0*) |
| 76 | yaonam.PoonPoonv4 | 1269 | 40 | 737 | 232-505 | 90% (c_well9 9-1*) |
| 77 | BrysonJGalapon.friday | 1256 | 44 | 366 | 191-175 | 100% (g_iter0 2-0*) |
| 78 | nail-e.Barry | 1231 | 44 | 374 | 188-186 | 100% (g_iter0 2-0*) |
| 79 | aj-chau.attempt1 | 1223 | 44 | 392 | 204-188 | 100% (g_iter0 5-0*) |
| 80 | kevinli405.maggi3 | 1219 | 46 | 381 | 185-196 | 100% (g_iter0 5-0*) |
| 81 | prisms-cs-club.prisms10 | 1190 | 45 | 392 | 201-191 | 100% (g_iter0 2-0*) |
| 82 | mama4294.currentPlayer | 1178 | 44 | 393 | 195-198 | 100% (g_iter0 2-0*) |
| 83 | ipince.bobby_v2 | 1154 | 43 | 438 | 217-221 | 67% (c_swarm1 2-1*) |
| 84 | bewuwy.deathbot4 | 1065 | 43 | 467 | 230-237 | 100% (g_iter0 2-0*) |
| 85 | JfeMak.realplayer2 | 1061 | 44 | 429 | 213-216 | 100% (g_iter0 2-0*) |
| 86 | andrewgopher.gopherbot | 1055 | 44 | 438 | 205-233 | 100% (g_iter0 2-0*) |
| 87 | BrysonJGalapon.aloha | 1048 | 43 | 459 | 230-229 | 100% (c_swarm1 3-0*) |
| 88 | PSUtblock.sprint_four_player | 1013 | 46 | 423 | 206-217 | 100% (g_iter0 2-0*) |
| 89 | SampleProvider.SPAARK_1_12_2023 | 984 | 44 | 472 | 242-230 | 100% (c_swarm1 3-0*) |
| 90 | Nawlej.PoonPoonv3 | 961 | 45 | 460 | 220-240 | 100% (g_iter0 5-0*) |
| 91 | SDainard-PDX.Team_Player | 948 | 46 | 419 | 195-224 | 100% (g_iter0 2-0*) |
| 92 | Juanbri02.matfisplayer1 | 947 | 45 | 459 | 226-233 | 100% (g_iter0 5-0*) |
| 93 | NolanChai.nolan_1 | 940 | 44 | 477 | 234-243 | 100% (g_iter0 2-0*) |
| 94 | andrewgopher.gopherbot1 | 926 | 46 | 434 | 199-235 | 100% (g_iter0 2-0*) |
| 95 | jyorkio.elicompbot | 903 | 45 | 445 | 217-228 | 100% (g_iter0 2-0*) |
| 96 | vontell.regressiongames | 829 | 46 | 470 | 230-240 | 100% (g_iter0 5-0*) |
| 97 | legobridge.kushalplayer | 809 | 48 | 421 | 194-227 | 100% (g_iter0 2-0*) |
| 98 | SteamBlizzard.Block | 761 | 48 | 481 | 224-257 | 100% (g_iter0 5-0*) |
| 99 | Patela171.Battlecode2023_Robot | 754 | 48 | 457 | 214-243 | 100% (g_iter0 2-0*) |
| 100 | ax-95174.MPAction | 728 | 48 | 465 | 208-257 | 100% (c_swarm1 3-0*) |
| 101 | nail-e.Dante | 681 | 49 | 490 | 245-245 | 100% (g_iter0 2-0*) |
| 102 | Chahat08.toph | 673 | 49 | 467 | 216-251 | 100% (g_iter0 2-0*) |
| 103 | michael-tyl.hqrewrite | 670 | 50 | 443 | 216-227 | 100% (g_iter0 2-0*) |
| 104 | JackLee9355.jackPlayer | 665 | 51 | 425 | 187-238 | 100% (g_iter0 2-0*) |
| 105 | mama4294.learningBot | 660 | 50 | 471 | 231-240 | 100% (g_iter0 2-0*) |
| 106 | anicolao.submission | 614 | 50 | 514 | 241-273 | 100% (g_iter0 2-0*) |
| 107 | team-remember-to-hydrate.sprint_1 | 603 | 50 | 477 | 217-260 | 100% (g_iter0 2-0*) |
| 108 | Vinceyou1.Player1 | 489 | 53 | 467 | 215-252 | 100% (g_iter0 2-0*) |
| 109 | addiesteward.elicompbot | 472 | 53 | 491 | 218-273 | 100% (g_iter0 5-0*) |
| 110 | toyat522.bot5 | 470 | 52 | 517 | 225-292 | 100% (g_iter0 2-0*) |
| 111 | michael-tyl.cc_v0_5_0_6 | 466 | 52 | 550 | 256-294 | 100% (g_iter0 2-0*) |
| 112 | Chahat08.lazarus | 433 | 53 | 508 | 234-274 | 100% (g_iter0 2-0*) |
| 113 | Swordman51.AdeptusAstartes2 | 430 | 54 | 492 | 238-254 | 100% (g_iter0 2-0*) |
| 114 | monmouth-college-cs.elicompbot | 400 | 54 | 528 | 233-295 | 100% (g_iter0 2-0*) |
| 115 | anicolao.jumbled | 314 | 57 | 514 | 237-277 | 100% (g_iter0 5-0*) |
| 116 | ShatterXD.SRNNbot | 296 | 58 | 508 | 242-266 | 100% (g_iter0 2-0*) |
| 117 | NotLLeon.player | 59 | 71 | 477 | 224-253 | 100% (g_iter0 2-0*) |
| 118 | CodeClash-ai.mysubmission | -45 | 75 | 500 | 222-278 | 100% (g_iter0 2-0*) |
| 119 | addiesteward.NDeClaw | -56 | 77 | 465 | 205-260 | 100% (g_iter0 5-0*) |
| 120 | Yooncw0223.lec3player | -363 | 88 | 433 | 77-356 | 100% (g_iter0 5-0*) |
| 121 | andrewkbank.First | -420 | 92 | 346 | 54-292 | 100% (g_iter0 2-0*) |
