# Ladder

20975 games (5054 ours, 6 of the stock examplefuncsplayer, 15915 between field bots on the ladder replica), 20465 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 120 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2013 +- 87 | 12 of 119 | 100 | 64-36 | 87.0% | 33.1% (vs 11) |
| c_blind1 | 2002 +- 87 | 13 of 119 | 100 | 63-37 | 86.6% | 31.8% (vs 11) |
| c_blind2 | 2002 +- 87 | 14 of 119 | 100 | 63-37 | 86.6% | 31.8% (vs 11) |
| c_mend3 | 1981 +- 87 | 15 of 119 | 100 | 61-39 | 85.8% | 29.3% (vs 11) |
| c_spread2 | 1981 +- 87 | 16 of 119 | 100 | 61-39 | 85.8% | 29.3% (vs 11) |
| c_bc3 | 1981 +- 87 | 17 of 119 | 100 | 61-39 | 85.8% | 29.3% (vs 11) |
| c_thr1 | 1971 +- 86 | 19 of 119 | 100 | 60-40 | 85.4% | 29.8% (vs 12) |
| c_scout1 | 1971 +- 86 | 20 of 119 | 100 | 60-40 | 85.4% | 29.8% (vs 12) |
| c_well7 | 1971 +- 86 | 21 of 119 | 100 | 60-40 | 85.4% | 29.8% (vs 12) |
| c_well9 | 1969 +- 61 | 22 of 119 | 186 | 99-87 | 85.4% | 29.6% (vs 12) |
| c_cap1 | 1960 +- 86 | 23 of 119 | 100 | 59-41 | 85.0% | 28.6% (vs 12) |
| c_seam1 | 1960 +- 86 | 24 of 119 | 100 | 59-41 | 85.0% | 28.6% (vs 12) |
| c_seam2 | 1960 +- 86 | 25 of 119 | 100 | 59-41 | 85.0% | 28.6% (vs 12) |
| c_mend2 | 1956 +- 40 | 26 of 119 | 612 | 362-250 | 84.9% | 28.2% (vs 12) |
| c_bc1 | 1955 +- 66 | 27 of 119 | 164 | 97-67 | 84.8% | 28.0% (vs 12) |
| c_def3 | 1952 +- 60 | 28 of 119 | 199 | 120-79 | 84.7% | 27.7% (vs 12) |
| c_siege1 | 1950 +- 86 | 29 of 119 | 100 | 58-42 | 84.6% | 27.5% (vs 12) |
| c_end2 | 1939 +- 86 | 30 of 119 | 100 | 57-43 | 84.2% | 26.4% (vs 12) |
| c_open1 | 1929 +- 86 | 31 of 119 | 100 | 56-44 | 83.8% | 25.3% (vs 12) |
| c_flee3 | 1929 +- 86 | 32 of 119 | 100 | 56-44 | 83.8% | 25.3% (vs 12) |
| c_anc3 | 1925 +- 66 | 33 of 119 | 163 | 88-75 | 83.6% | 24.8% (vs 12) |
| c_aura2 | 1924 +- 49 | 34 of 119 | 314 | 162-152 | 83.6% | 24.8% (vs 12) |
| c_nav5 | 1866 +- 75 | 36 of 119 | 126 | 61-65 | 81.2% | 21.4% (vs 13) |
| c_nav6 | 1850 +- 75 | 39 of 119 | 129 | 58-71 | 80.5% | 23.9% (vs 15) |
| c_nav4 | 1828 +- 57 | 40 of 119 | 221 | 108-113 | 79.6% | 21.9% (vs 15) |
| c_swarm1 | 1750 +- 53 | 44 of 119 | 271 | 128-143 | 76.0% | 20.9% (vs 18) |
| c_line8a | 1705 +- 75 | 49 of 119 | 139 | 47-92 | 73.9% | 22.4% (vs 22) |
| g_iter0 | 1688 +- 53 | 50 of 119 | 456 | 230-226 | 73.0% | 21.0% (vs 22) |
| c_line6 | 1670 +- 92 | 53 of 119 | 100 | 32-68 | 72.1% | 22.0% (vs 24) |
| c_line7m | 1658 +- 92 | 54 of 119 | 100 | 31-69 | 71.5% | 21.0% (vs 24) |
| c_line5 | 1620 +- 95 | 59 of 119 | 100 | 28-72 | 69.6% | 22.0% (vs 28) |
| c_line4 | 1580 +- 98 | 61 of 119 | 100 | 25-75 | 67.6% | 19.8% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_well9), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2253 | 62 | 222 | 155-67 | 22% (c_mend2 2-7*) |
| 2 | IvanGeffner.fortytwo | 2230 | 58 | 260 | 178-82 | 13% (c_mend2 3-20*) |
| 3 | awesomelemonade.finalBot | 2228 | 47 | 549 | 429-120 | 20% (c_well9 2-8*) |
| 4 | carlguo866.submit26_final | 2181 | 59 | 236 | 144-92 | 0% (c_mend2 0-3*) |
| 5 | vrangr1.AFinalsBot | 2166 | 44 | 551 | 407-144 | 20% (c_well9 2-8*) |
| 6 | AnOvercookedFork.quals | 2125 | 56 | 263 | 166-97 | 27% (c_mend2 4-11*) |
| 7 | pranayagra.finalbotfinaltwo | 2093 | 55 | 270 | 171-99 | 33% (c_well9 2-4*) |
| 8 | georgezhang02.FB_ZZZ | 2082 | 53 | 278 | 175-103 | 33% (c_well9 4-8*) |
| 9 | pranayagra.finalbotfinal | 2075 | 39 | 656 | 427-229 | 28% (c_well9 7-18*) |
| 10 | battlecode-archive.sprintBot | 2057 | 54 | 271 | 168-103 | 17% (c_well9 1-5*) |
| 11 | jmerle.camel_case_v30_final | 2050 | 39 | 612 | 399-213 | 44% (c_well9 7-9*) |
| 12 | **us:c_well5** | 2013 | 87 | 100 | 64-36 |  |
| 13 | **us:c_blind1** | 2002 | 87 | 100 | 63-37 |  |
| 14 | **us:c_blind2** | 2002 | 87 | 100 | 63-37 |  |
| 15 | **us:c_mend3** | 1981 | 87 | 100 | 61-39 |  |
| 16 | **us:c_spread2** | 1981 | 87 | 100 | 61-39 |  |
| 17 | **us:c_bc3** | 1981 | 87 | 100 | 61-39 |  |
| 18 | CyrilSharma.finalBot | 1980 | 49 | 340 | 206-134 | 48% (c_well9 10-11*) |
| 19 | **us:c_thr1** | 1971 | 86 | 100 | 60-40 |  |
| 20 | **us:c_scout1** | 1971 | 86 | 100 | 60-40 |  |
| 21 | **us:c_well7** | 1971 | 86 | 100 | 60-40 |  |
| 22 | **us:c_well9** | 1969 | 61 | 186 | 99-87 |  |
| 23 | **us:c_cap1** | 1960 | 86 | 100 | 59-41 |  |
| 24 | **us:c_seam1** | 1960 | 86 | 100 | 59-41 |  |
| 25 | **us:c_seam2** | 1960 | 86 | 100 | 59-41 |  |
| 26 | **us:c_mend2** | 1956 | 40 | 612 | 362-250 |  |
| 27 | **us:c_bc1** | 1955 | 66 | 164 | 97-67 |  |
| 28 | **us:c_def3** | 1952 | 60 | 199 | 120-79 |  |
| 29 | **us:c_siege1** | 1950 | 86 | 100 | 58-42 |  |
| 30 | **us:c_end2** | 1939 | 86 | 100 | 57-43 |  |
| 31 | **us:c_open1** | 1929 | 86 | 100 | 56-44 |  |
| 32 | **us:c_flee3** | 1929 | 86 | 100 | 56-44 |  |
| 33 | **us:c_anc3** | 1925 | 66 | 163 | 88-75 |  |
| 34 | **us:c_aura2** | 1924 | 49 | 314 | 162-152 |  |
| 35 | ethanlabelle.dev | 1886 | 45 | 379 | 210-169 | 57% (c_well9 8-6*) |
| 36 | **us:c_nav5** | 1866 | 75 | 126 | 61-65 |  |
| 37 | NotLLeon.v7 | 1859 | 36 | 682 | 337-345 | 60% (c_well9 6-4*) |
| 38 | georgezhang02.CB_tuning2 | 1853 | 36 | 693 | 341-352 | 80% (c_well9 8-2*) |
| 39 | **us:c_nav6** | 1850 | 75 | 129 | 58-71 |  |
| 40 | **us:c_nav4** | 1828 | 57 | 221 | 108-113 |  |
| 41 | ethanlabelle.v19 | 1785 | 45 | 381 | 198-183 | 77% (c_mend2 53-16) |
| 42 | britacatalin.FinalBot | 1777 | 37 | 642 | 286-356 | 81% (c_well9 13-3*) |
| 43 | GabeG888.v8 | 1752 | 48 | 311 | 172-139 | 89% (c_def3 16-2*) |
| 44 | **us:c_swarm1** | 1750 | 53 | 271 | 128-143 |  |
| 45 | VarunVejalla.karel | 1747 | 45 | 392 | 194-198 | 68% (c_mend2 52-25) |
| 46 | programjames.fourthbot | 1746 | 48 | 314 | 173-141 | 64% (c_mend2 7-4*) |
| 47 | VarunVejalla.ali8 | 1736 | 49 | 298 | 163-135 | 83% (c_mend2 5-1*) |
| 48 | GabeG888.v8o1 | 1727 | 48 | 309 | 173-136 | 67% (c_aura2 4-2*) |
| 49 | **us:c_line8a** | 1705 | 75 | 139 | 47-92 |  |
| 50 | **us:g_iter0** | 1688 | 53 | 456 | 230-226 |  |
| 51 | DannyZhang686.pqual2 | 1678 | 46 | 348 | 181-167 | 83% (c_mend2 5-1*) |
| 52 | NicholasKelly15.gopher10 | 1674 | 50 | 286 | 157-129 | 100% (c_anc3 3-0*) |
| 53 | **us:c_line6** | 1670 | 92 | 100 | 32-68 |  |
| 54 | **us:c_line7m** | 1658 | 92 | 100 | 31-69 |  |
| 55 | SampleProvider.SPAARK | 1657 | 50 | 296 | 159-137 | 33% (c_anc3 1-2*) |
| 56 | louishu17.louisv10 | 1653 | 49 | 297 | 157-140 | 100% (c_bc1 3-0*) |
| 57 | louishu17.wouisv8 | 1647 | 49 | 318 | 170-148 | 83% (c_aura2 5-1*) |
| 58 | reeceyang.v5anaconda | 1642 | 37 | 652 | 245-407 | 100% (c_well9 10-0*) |
| 59 | **us:c_line5** | 1620 | 95 | 100 | 28-72 |  |
| 60 | battlecode-archive.Sprint1 | 1590 | 39 | 624 | 211-413 | 100% (c_well9 10-0*) |
| 61 | **us:c_line4** | 1580 | 98 | 100 | 25-75 |  |
| 62 | ipince.bobby | 1521 | 51 | 282 | 145-137 | 67% (c_swarm1 2-1*) |
| 63 | SteamBlizzard.newVnewME | 1500 | 46 | 348 | 177-171 | 80% (g_iter0 4-1*) |
| 64 | legobridge.tacoplayer | 1492 | 48 | 343 | 170-173 | 100% (c_mend2 6-0*) |
| 65 | TheK098.qp1_7_sprint_1 | 1462 | 47 | 339 | 183-156 | 100% (c_mend2 6-0*) |
| 66 | polyllc.poly | 1439 | 52 | 280 | 141-139 | 100% (g_iter0 2-0*) |
| 67 | ColtG5.rexv9 | 1410 | 45 | 354 | 177-177 | 100% (g_iter0 2-0*) |
| 68 | toyat522.bot5a | 1403 | 46 | 351 | 164-187 | 80% (g_iter0 4-1*) |
| 69 | elgoldie.head_v5 | 1383 | 46 | 336 | 162-174 | 100% (g_iter0 2-0*) |
| 70 | DukeBas._main | 1366 | 47 | 353 | 190-163 | 100% (c_mend2 6-0*) |
| 71 | beaverbois.USQualifiers | 1356 | 47 | 334 | 174-160 | 50% (g_iter0 1-1*) |
| 72 | kevinli405.maggi3_2 | 1316 | 45 | 374 | 194-180 | 100% (g_iter0 2-0*) |
| 73 | Nawlej.PoonPoon | 1312 | 49 | 319 | 163-156 | 100% (g_iter0 2-0*) |
| 74 | yaonam.PoonPoonv4 | 1284 | 41 | 694 | 219-475 | 90% (c_well9 9-1*) |
| 75 | BrysonJGalapon.friday | 1269 | 46 | 343 | 178-165 | 100% (g_iter0 2-0*) |
| 76 | nail-e.Barry | 1244 | 46 | 352 | 173-179 | 100% (g_iter0 2-0*) |
| 77 | aj-chau.attempt1 | 1242 | 46 | 369 | 193-176 | 100% (g_iter0 5-0*) |
| 78 | kevinli405.maggi3 | 1237 | 47 | 360 | 177-183 | 100% (g_iter0 5-0*) |
| 79 | prisms-cs-club.prisms10 | 1206 | 46 | 368 | 183-185 | 100% (g_iter0 2-0*) |
| 80 | mama4294.currentPlayer | 1198 | 45 | 372 | 187-185 | 100% (g_iter0 2-0*) |
| 81 | ipince.bobby_v2 | 1163 | 44 | 414 | 202-212 | 67% (c_swarm1 2-1*) |
| 82 | bewuwy.deathbot4 | 1085 | 44 | 445 | 220-225 | 100% (g_iter0 2-0*) |
| 83 | andrewgopher.gopherbot | 1075 | 45 | 416 | 197-219 | 100% (g_iter0 2-0*) |
| 84 | JfeMak.realplayer2 | 1071 | 45 | 405 | 196-209 | 100% (g_iter0 2-0*) |
| 85 | BrysonJGalapon.aloha | 1067 | 44 | 438 | 219-219 | 100% (c_swarm1 3-0*) |
| 86 | PSUtblock.sprint_four_player | 1031 | 47 | 401 | 193-208 | 100% (g_iter0 2-0*) |
| 87 | SampleProvider.SPAARK_1_12_2023 | 1003 | 45 | 448 | 234-214 | 100% (c_swarm1 3-0*) |
| 88 | Nawlej.PoonPoonv3 | 976 | 45 | 436 | 209-227 | 100% (g_iter0 5-0*) |
| 89 | SDainard-PDX.Team_Player | 968 | 47 | 398 | 189-209 | 100% (g_iter0 2-0*) |
| 90 | NolanChai.nolan_1 | 961 | 45 | 454 | 225-229 | 100% (g_iter0 2-0*) |
| 91 | Juanbri02.matfisplayer1 | 961 | 45 | 435 | 212-223 | 100% (g_iter0 5-0*) |
| 92 | andrewgopher.gopherbot1 | 945 | 47 | 412 | 192-220 | 100% (g_iter0 2-0*) |
| 93 | jyorkio.elicompbot | 920 | 46 | 422 | 206-216 | 100% (g_iter0 2-0*) |
| 94 | vontell.regressiongames | 850 | 46 | 449 | 221-228 | 100% (g_iter0 5-0*) |
| 95 | legobridge.kushalplayer | 821 | 49 | 401 | 181-220 | 100% (g_iter0 2-0*) |
| 96 | SteamBlizzard.Block | 776 | 49 | 457 | 209-248 | 100% (g_iter0 5-0*) |
| 97 | Patela171.Battlecode2023_Robot | 775 | 49 | 434 | 199-235 | 100% (g_iter0 2-0*) |
| 98 | ax-95174.MPAction | 753 | 49 | 442 | 200-242 | 100% (c_swarm1 3-0*) |
| 99 | nail-e.Dante | 710 | 49 | 468 | 233-235 | 100% (g_iter0 2-0*) |
| 100 | Chahat08.toph | 698 | 50 | 445 | 208-237 | 100% (g_iter0 2-0*) |
| 101 | michael-tyl.hqrewrite | 691 | 51 | 420 | 209-211 | 100% (g_iter0 2-0*) |
| 102 | JackLee9355.jackPlayer | 685 | 52 | 404 | 175-229 | 100% (g_iter0 2-0*) |
| 103 | mama4294.learningBot | 674 | 51 | 450 | 216-234 | 100% (g_iter0 2-0*) |
| 104 | anicolao.submission | 638 | 50 | 492 | 231-261 | 100% (g_iter0 2-0*) |
| 105 | team-remember-to-hydrate.sprint_1 | 619 | 51 | 456 | 205-251 | 100% (g_iter0 2-0*) |
| 106 | Vinceyou1.Player1 | 508 | 54 | 443 | 207-236 | 100% (g_iter0 2-0*) |
| 107 | toyat522.bot5 | 497 | 53 | 499 | 220-279 | 100% (g_iter0 2-0*) |
| 108 | addiesteward.elicompbot | 492 | 54 | 472 | 209-263 | 100% (g_iter0 5-0*) |
| 109 | michael-tyl.cc_v0_5_0_6 | 483 | 53 | 526 | 245-281 | 100% (g_iter0 2-0*) |
| 110 | Chahat08.lazarus | 453 | 54 | 484 | 224-260 | 100% (g_iter0 2-0*) |
| 111 | Swordman51.AdeptusAstartes2 | 446 | 55 | 470 | 223-247 | 100% (g_iter0 2-0*) |
| 112 | monmouth-college-cs.elicompbot | 424 | 54 | 505 | 224-281 | 100% (g_iter0 2-0*) |
| 113 | anicolao.jumbled | 330 | 58 | 491 | 222-269 | 100% (g_iter0 5-0*) |
| 114 | ShatterXD.SRNNbot | 316 | 59 | 487 | 231-256 | 100% (g_iter0 2-0*) |
| 115 | NotLLeon.player | 79 | 72 | 458 | 211-247 | 100% (g_iter0 2-0*) |
| 116 | CodeClash-ai.mysubmission | -15 | 76 | 483 | 215-268 | 100% (g_iter0 2-0*) |
| 117 | addiesteward.NDeClaw | -22 | 78 | 444 | 197-247 | 100% (g_iter0 5-0*) |
| 118 | Yooncw0223.lec3player | -342 | 89 | 412 | 70-342 | 100% (g_iter0 5-0*) |
| 119 | andrewkbank.First | -391 | 93 | 327 | 51-276 | 100% (g_iter0 2-0*) |
