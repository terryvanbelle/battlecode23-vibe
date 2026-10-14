# Ladder

19346 games (3941 ours, 6 of the stock examplefuncsplayer, 15399 between field bots on the ladder replica), 18860 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 111 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_blind1 | 2236 +- 219 | 6 of 110 | 10 | 5-5 | 92.1% | 43.6% (vs 5) |
| c_well5 | 2080 +- 88 | 13 of 110 | 100 | 64-36 | 87.1% | 33.6% (vs 11) |
| c_bc3 | 2048 +- 87 | 14 of 110 | 100 | 61-39 | 85.9% | 29.8% (vs 11) |
| c_spread2 | 2048 +- 87 | 15 of 110 | 100 | 61-39 | 85.9% | 29.8% (vs 11) |
| c_well7 | 2038 +- 87 | 17 of 110 | 100 | 60-40 | 85.5% | 30.3% (vs 12) |
| c_scout1 | 2038 +- 87 | 18 of 110 | 100 | 60-40 | 85.5% | 30.3% (vs 12) |
| c_bc1 | 2021 +- 66 | 19 of 110 | 164 | 97-67 | 84.8% | 28.3% (vs 12) |
| c_mend2 | 2019 +- 42 | 20 of 110 | 576 | 344-232 | 84.7% | 28.1% (vs 12) |
| c_def3 | 2018 +- 61 | 21 of 110 | 199 | 120-79 | 84.7% | 28.0% (vs 12) |
| c_end2 | 2007 +- 87 | 22 of 110 | 100 | 57-43 | 84.3% | 26.8% (vs 12) |
| c_flee3 | 1996 +- 87 | 23 of 110 | 100 | 56-44 | 83.9% | 25.7% (vs 12) |
| c_anc3 | 1990 +- 67 | 24 of 110 | 163 | 88-75 | 83.6% | 25.1% (vs 12) |
| c_aura2 | 1990 +- 50 | 25 of 110 | 314 | 162-152 | 83.6% | 25.0% (vs 12) |
| c_nav5 | 1933 +- 76 | 27 of 110 | 126 | 61-65 | 81.2% | 21.7% (vs 13) |
| c_nav6 | 1916 +- 75 | 30 of 110 | 129 | 58-71 | 80.5% | 24.1% (vs 15) |
| c_nav4 | 1895 +- 57 | 31 of 110 | 221 | 108-113 | 79.6% | 22.1% (vs 15) |
| c_swarm1 | 1818 +- 54 | 35 of 110 | 271 | 128-143 | 76.1% | 21.1% (vs 18) |
| c_line8a | 1773 +- 76 | 40 of 110 | 139 | 47-92 | 73.9% | 22.6% (vs 22) |
| g_iter0 | 1755 +- 53 | 41 of 110 | 456 | 230-226 | 73.0% | 21.0% (vs 22) |
| c_line6 | 1738 +- 92 | 44 of 110 | 100 | 32-68 | 72.1% | 22.1% (vs 24) |
| c_line7m | 1725 +- 93 | 46 of 110 | 100 | 31-69 | 71.5% | 22.2% (vs 25) |
| c_line5 | 1688 +- 95 | 50 of 110 | 100 | 28-72 | 69.7% | 22.0% (vs 28) |
| c_line4 | 1647 +- 99 | 52 of 110 | 100 | 25-75 | 67.6% | 19.7% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_mend2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2327 | 65 | 210 | 150-60 | 22% (c_mend2 2-7*) |
| 2 | awesomelemonade.finalBot | 2295 | 53 | 437 | 341-96 | 20% (c_mend2 5-20*) |
| 3 | IvanGeffner.fortytwo | 2288 | 61 | 248 | 169-79 | 13% (c_mend2 3-20*) |
| 4 | carlguo866.submit26_final | 2254 | 62 | 224 | 140-84 | 0% (c_mend2 0-3*) |
| 5 | vrangr1.AFinalsBot | 2243 | 50 | 449 | 336-113 | 36% (c_mend2 8-14*) |
| 6 | **us:c_blind1** | 2236 | 219 | 10 | 5-5 |  |
| 7 | AnOvercookedFork.quals | 2187 | 58 | 252 | 159-93 | 25% (c_mend2 3-9*) |
| 8 | pranayagra.finalbotfinaltwo | 2155 | 58 | 252 | 159-93 | 0% (c_mend2 0-3*) |
| 9 | georgezhang02.FB_ZZZ | 2142 | 57 | 254 | 157-97 | 0% (c_anc3 0-3*) |
| 10 | pranayagra.finalbotfinal | 2140 | 44 | 524 | 343-181 | 32% (c_mend2 7-15*) |
| 11 | battlecode-archive.sprintBot | 2109 | 58 | 248 | 151-97 | 28% (c_mend2 5-13*) |
| 12 | jmerle.camel_case_v30_final | 2106 | 44 | 495 | 324-171 | 40% (c_mend2 4-6*) |
| 13 | **us:c_well5** | 2080 | 88 | 100 | 64-36 |  |
| 14 | **us:c_bc3** | 2048 | 87 | 100 | 61-39 |  |
| 15 | **us:c_spread2** | 2048 | 87 | 100 | 61-39 |  |
| 16 | CyrilSharma.finalBot | 2044 | 52 | 304 | 187-117 | 33% (c_mend2 4-8*) |
| 17 | **us:c_well7** | 2038 | 87 | 100 | 60-40 |  |
| 18 | **us:c_scout1** | 2038 | 87 | 100 | 60-40 |  |
| 19 | **us:c_bc1** | 2021 | 66 | 164 | 97-67 |  |
| 20 | **us:c_mend2** | 2019 | 42 | 576 | 344-232 |  |
| 21 | **us:c_def3** | 2018 | 61 | 199 | 120-79 |  |
| 22 | **us:c_end2** | 2007 | 87 | 100 | 57-43 |  |
| 23 | **us:c_flee3** | 1996 | 87 | 100 | 56-44 |  |
| 24 | **us:c_anc3** | 1990 | 67 | 163 | 88-75 |  |
| 25 | **us:c_aura2** | 1990 | 50 | 314 | 162-152 |  |
| 26 | ethanlabelle.dev | 1948 | 47 | 353 | 198-155 | 64% (c_mend2 23-13) |
| 27 | **us:c_nav5** | 1933 | 76 | 126 | 61-65 |  |
| 28 | NotLLeon.v7 | 1927 | 40 | 567 | 296-271 | 74% (c_mend2 39-14) |
| 29 | georgezhang02.CB_tuning2 | 1921 | 40 | 578 | 302-276 | 59% (c_mend2 47-33) |
| 30 | **us:c_nav6** | 1916 | 75 | 129 | 58-71 |  |
| 31 | **us:c_nav4** | 1895 | 57 | 221 | 108-113 |  |
| 32 | ethanlabelle.v19 | 1854 | 46 | 371 | 193-178 | 77% (c_mend2 53-16) |
| 33 | britacatalin.FinalBot | 1845 | 41 | 521 | 252-269 | 75% (c_mend2 12-4*) |
| 34 | GabeG888.v8 | 1819 | 50 | 300 | 165-135 | 89% (c_def3 16-2*) |
| 35 | **us:c_swarm1** | 1818 | 54 | 271 | 128-143 |  |
| 36 | VarunVejalla.karel | 1818 | 46 | 380 | 192-188 | 68% (c_mend2 52-25) |
| 37 | programjames.fourthbot | 1809 | 50 | 302 | 164-138 | 64% (c_mend2 7-4*) |
| 38 | VarunVejalla.ali8 | 1806 | 51 | 287 | 159-128 | 83% (c_mend2 5-1*) |
| 39 | GabeG888.v8o1 | 1795 | 49 | 297 | 167-130 | 67% (c_aura2 4-2*) |
| 40 | **us:c_line8a** | 1773 | 76 | 139 | 47-92 |  |
| 41 | **us:g_iter0** | 1755 | 53 | 456 | 230-226 |  |
| 42 | NicholasKelly15.gopher10 | 1747 | 52 | 274 | 153-121 | 100% (c_anc3 3-0*) |
| 43 | DannyZhang686.pqual2 | 1744 | 47 | 336 | 174-162 | 83% (c_mend2 5-1*) |
| 44 | **us:c_line6** | 1738 | 92 | 100 | 32-68 |  |
| 45 | louishu17.louisv10 | 1727 | 51 | 285 | 153-132 | 100% (c_bc1 3-0*) |
| 46 | **us:c_line7m** | 1725 | 93 | 100 | 31-69 |  |
| 47 | SampleProvider.SPAARK | 1723 | 51 | 284 | 149-135 | 33% (c_anc3 1-2*) |
| 48 | louishu17.wouisv8 | 1715 | 50 | 306 | 166-140 | 83% (c_aura2 5-1*) |
| 49 | reeceyang.v5anaconda | 1713 | 40 | 541 | 225-316 | 90% (c_mend2 9-1*) |
| 50 | **us:c_line5** | 1688 | 95 | 100 | 28-72 |  |
| 51 | battlecode-archive.Sprint1 | 1667 | 42 | 512 | 199-313 | 96% (c_mend2 24-1*) |
| 52 | **us:c_line4** | 1647 | 99 | 100 | 25-75 |  |
| 53 | ipince.bobby | 1593 | 53 | 271 | 141-130 | 67% (c_swarm1 2-1*) |
| 54 | SteamBlizzard.newVnewME | 1567 | 47 | 336 | 169-167 | 80% (g_iter0 4-1*) |
| 55 | legobridge.tacoplayer | 1563 | 49 | 332 | 167-165 | 100% (c_mend2 6-0*) |
| 56 | TheK098.qp1_7_sprint_1 | 1536 | 48 | 328 | 179-149 | 100% (c_mend2 6-0*) |
| 57 | polyllc.poly | 1509 | 53 | 269 | 137-132 | 100% (g_iter0 2-0*) |
| 58 | ColtG5.rexv9 | 1475 | 47 | 343 | 171-172 | 100% (g_iter0 2-0*) |
| 59 | toyat522.bot5a | 1470 | 47 | 340 | 160-180 | 80% (g_iter0 4-1*) |
| 60 | elgoldie.head_v5 | 1454 | 47 | 324 | 156-168 | 100% (g_iter0 2-0*) |
| 61 | DukeBas._main | 1435 | 48 | 343 | 186-157 | 100% (c_mend2 6-0*) |
| 62 | beaverbois.USQualifiers | 1426 | 48 | 323 | 173-150 | 50% (g_iter0 1-1*) |
| 63 | kevinli405.maggi3_2 | 1384 | 46 | 362 | 189-173 | 100% (g_iter0 2-0*) |
| 64 | Nawlej.PoonPoon | 1370 | 50 | 307 | 155-152 | 100% (g_iter0 2-0*) |
| 65 | yaonam.PoonPoonv4 | 1332 | 43 | 583 | 202-381 | 90% (c_mend2 9-1*) |
| 66 | BrysonJGalapon.friday | 1330 | 46 | 332 | 171-161 | 100% (g_iter0 2-0*) |
| 67 | nail-e.Barry | 1309 | 46 | 341 | 167-174 | 100% (g_iter0 2-0*) |
| 68 | aj-chau.attempt1 | 1305 | 46 | 359 | 188-171 | 100% (g_iter0 5-0*) |
| 69 | kevinli405.maggi3 | 1304 | 48 | 348 | 169-179 | 100% (g_iter0 5-0*) |
| 70 | prisms-cs-club.prisms10 | 1272 | 47 | 357 | 180-177 | 100% (g_iter0 2-0*) |
| 71 | mama4294.currentPlayer | 1258 | 46 | 360 | 180-180 | 100% (g_iter0 2-0*) |
| 72 | ipince.bobby_v2 | 1233 | 45 | 402 | 197-205 | 67% (c_swarm1 2-1*) |
| 73 | bewuwy.deathbot4 | 1147 | 44 | 434 | 213-221 | 100% (g_iter0 2-0*) |
| 74 | JfeMak.realplayer2 | 1139 | 45 | 393 | 196-197 | 100% (g_iter0 2-0*) |
| 75 | andrewgopher.gopherbot | 1135 | 45 | 405 | 190-215 | 100% (g_iter0 2-0*) |
| 76 | BrysonJGalapon.aloha | 1133 | 44 | 426 | 213-213 | 100% (c_swarm1 3-0*) |
| 77 | PSUtblock.sprint_four_player | 1099 | 47 | 389 | 190-199 | 100% (g_iter0 2-0*) |
| 78 | SampleProvider.SPAARK_1_12_2023 | 1059 | 46 | 436 | 222-214 | 100% (c_swarm1 3-0*) |
| 79 | Nawlej.PoonPoonv3 | 1031 | 46 | 424 | 201-223 | 100% (g_iter0 5-0*) |
| 80 | Juanbri02.matfisplayer1 | 1027 | 46 | 423 | 208-215 | 100% (g_iter0 5-0*) |
| 81 | SDainard-PDX.Team_Player | 1022 | 48 | 387 | 182-205 | 100% (g_iter0 2-0*) |
| 82 | NolanChai.nolan_1 | 1022 | 45 | 442 | 217-225 | 100% (g_iter0 2-0*) |
| 83 | andrewgopher.gopherbot1 | 1001 | 47 | 400 | 184-216 | 100% (g_iter0 2-0*) |
| 84 | jyorkio.elicompbot | 985 | 46 | 411 | 201-210 | 100% (g_iter0 2-0*) |
| 85 | vontell.regressiongames | 908 | 46 | 437 | 210-227 | 100% (g_iter0 5-0*) |
| 86 | legobridge.kushalplayer | 888 | 49 | 389 | 180-209 | 100% (g_iter0 2-0*) |
| 87 | Patela171.Battlecode2023_Robot | 844 | 48 | 422 | 195-227 | 100% (g_iter0 2-0*) |
| 88 | SteamBlizzard.Block | 841 | 49 | 445 | 206-239 | 100% (g_iter0 5-0*) |
| 89 | ax-95174.MPAction | 817 | 49 | 430 | 196-234 | 100% (c_swarm1 3-0*) |
| 90 | nail-e.Dante | 781 | 49 | 456 | 228-228 | 100% (g_iter0 2-0*) |
| 91 | Chahat08.toph | 761 | 50 | 433 | 205-228 | 100% (g_iter0 2-0*) |
| 92 | JackLee9355.jackPlayer | 750 | 53 | 392 | 171-221 | 100% (g_iter0 2-0*) |
| 93 | michael-tyl.hqrewrite | 748 | 51 | 408 | 201-207 | 100% (g_iter0 2-0*) |
| 94 | mama4294.learningBot | 738 | 50 | 439 | 209-230 | 100% (g_iter0 2-0*) |
| 95 | anicolao.submission | 698 | 50 | 481 | 227-254 | 100% (g_iter0 2-0*) |
| 96 | team-remember-to-hydrate.sprint_1 | 676 | 51 | 444 | 196-248 | 100% (g_iter0 2-0*) |
| 97 | toyat522.bot5 | 558 | 53 | 487 | 215-272 | 100% (g_iter0 2-0*) |
| 98 | Vinceyou1.Player1 | 558 | 55 | 432 | 199-233 | 100% (g_iter0 2-0*) |
| 99 | addiesteward.elicompbot | 551 | 54 | 460 | 205-255 | 100% (g_iter0 5-0*) |
| 100 | michael-tyl.cc_v0_5_0_6 | 539 | 53 | 515 | 242-273 | 100% (g_iter0 2-0*) |
| 101 | Chahat08.lazarus | 509 | 55 | 474 | 220-254 | 100% (g_iter0 2-0*) |
| 102 | Swordman51.AdeptusAstartes2 | 499 | 55 | 458 | 215-243 | 100% (g_iter0 2-0*) |
| 103 | monmouth-college-cs.elicompbot | 479 | 55 | 494 | 219-275 | 100% (g_iter0 2-0*) |
| 104 | anicolao.jumbled | 377 | 59 | 480 | 215-265 | 100% (g_iter0 5-0*) |
| 105 | ShatterXD.SRNNbot | 370 | 59 | 477 | 226-251 | 100% (g_iter0 2-0*) |
| 106 | NotLLeon.player | 131 | 73 | 448 | 205-243 | 100% (g_iter0 2-0*) |
| 107 | CodeClash-ai.mysubmission | 33 | 76 | 473 | 207-266 | 100% (g_iter0 2-0*) |
| 108 | addiesteward.NDeClaw | 32 | 78 | 433 | 191-242 | 100% (g_iter0 5-0*) |
| 109 | Yooncw0223.lec3player | -290 | 90 | 402 | 67-335 | 100% (g_iter0 5-0*) |
| 110 | andrewkbank.First | -334 | 94 | 316 | 50-266 | 100% (g_iter0 2-0*) |
