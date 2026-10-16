# Ladder

21642 games (5205 ours, 6 of the stock examplefuncsplayer, 16431 between field bots on the ladder replica), 21095 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 121 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2007 +- 87 | 12 of 120 | 100 | 64-36 | 87.0% | 33.0% (vs 11) |
| c_blind2 | 1996 +- 87 | 13 of 120 | 100 | 63-37 | 86.6% | 31.7% (vs 11) |
| c_blind1 | 1996 +- 87 | 14 of 120 | 100 | 63-37 | 86.6% | 31.7% (vs 11) |
| c_well10 | 1986 +- 87 | 15 of 120 | 100 | 62-38 | 86.2% | 30.5% (vs 11) |
| c_spread2 | 1975 +- 87 | 17 of 120 | 100 | 61-39 | 85.8% | 31.0% (vs 12) |
| c_mend3 | 1975 +- 87 | 18 of 120 | 100 | 61-39 | 85.8% | 31.0% (vs 12) |
| c_bc3 | 1975 +- 87 | 19 of 120 | 100 | 61-39 | 85.8% | 31.0% (vs 12) |
| c_thr1 | 1965 +- 86 | 20 of 120 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_well7 | 1965 +- 86 | 21 of 120 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_scout1 | 1965 +- 86 | 22 of 120 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_seam2 | 1954 +- 86 | 23 of 120 | 100 | 59-41 | 85.0% | 28.6% (vs 12) |
| c_cap1 | 1954 +- 86 | 24 of 120 | 100 | 59-41 | 85.0% | 28.6% (vs 12) |
| c_seam1 | 1954 +- 86 | 25 of 120 | 100 | 59-41 | 85.0% | 28.6% (vs 12) |
| c_mend2 | 1951 +- 39 | 26 of 120 | 612 | 362-250 | 84.9% | 28.1% (vs 12) |
| c_well9 | 1949 +- 55 | 27 of 120 | 233 | 125-108 | 84.8% | 27.9% (vs 12) |
| c_bc1 | 1949 +- 66 | 28 of 120 | 164 | 97-67 | 84.8% | 27.9% (vs 12) |
| c_def3 | 1946 +- 60 | 29 of 120 | 199 | 120-79 | 84.7% | 27.6% (vs 12) |
| c_siege1 | 1944 +- 86 | 30 of 120 | 100 | 58-42 | 84.6% | 27.4% (vs 12) |
| c_end2 | 1933 +- 86 | 31 of 120 | 100 | 57-43 | 84.2% | 26.3% (vs 12) |
| c_open1 | 1923 +- 86 | 32 of 120 | 100 | 56-44 | 83.8% | 25.2% (vs 12) |
| c_flee3 | 1923 +- 86 | 33 of 120 | 100 | 56-44 | 83.8% | 25.2% (vs 12) |
| c_anc3 | 1919 +- 66 | 34 of 120 | 163 | 88-75 | 83.6% | 24.7% (vs 12) |
| c_aura2 | 1918 +- 49 | 35 of 120 | 314 | 162-152 | 83.6% | 24.7% (vs 12) |
| c_nav5 | 1860 +- 75 | 37 of 120 | 126 | 61-65 | 81.2% | 21.3% (vs 13) |
| c_nav6 | 1844 +- 75 | 40 of 120 | 129 | 58-71 | 80.5% | 23.8% (vs 15) |
| c_nav4 | 1822 +- 57 | 41 of 120 | 221 | 108-113 | 79.6% | 21.8% (vs 15) |
| c_swarm1 | 1744 +- 53 | 46 of 120 | 271 | 128-143 | 76.0% | 22.3% (vs 19) |
| c_line8a | 1700 +- 75 | 50 of 120 | 139 | 47-92 | 73.9% | 22.5% (vs 22) |
| g_iter0 | 1681 +- 53 | 51 of 120 | 456 | 230-226 | 73.0% | 20.9% (vs 22) |
| c_line6 | 1663 +- 92 | 53 of 120 | 100 | 32-68 | 72.2% | 20.8% (vs 23) |
| c_line7m | 1651 +- 92 | 56 of 120 | 100 | 31-69 | 71.6% | 22.2% (vs 25) |
| c_line5 | 1614 +- 95 | 60 of 120 | 100 | 28-72 | 69.7% | 22.0% (vs 28) |
| c_line4 | 1574 +- 98 | 62 of 120 | 100 | 25-75 | 67.7% | 19.8% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_well9), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2253 | 61 | 233 | 163-70 | 22% (c_mend2 2-7*) |
| 2 | awesomelemonade.finalBot | 2226 | 46 | 569 | 444-125 | 20% (c_well9 2-8*) |
| 3 | IvanGeffner.fortytwo | 2222 | 57 | 270 | 182-88 | 13% (c_mend2 3-20*) |
| 4 | carlguo866.submit26_final | 2185 | 57 | 248 | 152-96 | 0% (c_mend2 0-3*) |
| 5 | vrangr1.AFinalsBot | 2162 | 43 | 572 | 421-151 | 20% (c_well9 2-8*) |
| 6 | AnOvercookedFork.quals | 2121 | 54 | 275 | 173-102 | 27% (c_mend2 4-11*) |
| 7 | pranayagra.finalbotfinaltwo | 2081 | 53 | 282 | 176-106 | 33% (c_well9 2-4*) |
| 8 | georgezhang02.FB_ZZZ | 2073 | 52 | 289 | 180-109 | 33% (c_well9 4-8*) |
| 9 | pranayagra.finalbotfinal | 2069 | 38 | 676 | 440-236 | 28% (c_well9 7-18*) |
| 10 | battlecode-archive.sprintBot | 2051 | 53 | 282 | 173-109 | 17% (c_well9 1-5*) |
| 11 | jmerle.camel_case_v30_final | 2044 | 39 | 632 | 409-223 | 44% (c_well9 7-9*) |
| 12 | **us:c_well5** | 2007 | 87 | 100 | 64-36 |  |
| 13 | **us:c_blind2** | 1996 | 87 | 100 | 63-37 |  |
| 14 | **us:c_blind1** | 1996 | 87 | 100 | 63-37 |  |
| 15 | **us:c_well10** | 1986 | 87 | 100 | 62-38 |  |
| 16 | CyrilSharma.finalBot | 1977 | 48 | 362 | 216-146 | 35% (c_well9 11-20) |
| 17 | **us:c_spread2** | 1975 | 87 | 100 | 61-39 |  |
| 18 | **us:c_mend3** | 1975 | 87 | 100 | 61-39 |  |
| 19 | **us:c_bc3** | 1975 | 87 | 100 | 61-39 |  |
| 20 | **us:c_thr1** | 1965 | 86 | 100 | 60-40 |  |
| 21 | **us:c_well7** | 1965 | 86 | 100 | 60-40 |  |
| 22 | **us:c_scout1** | 1965 | 86 | 100 | 60-40 |  |
| 23 | **us:c_seam2** | 1954 | 86 | 100 | 59-41 |  |
| 24 | **us:c_cap1** | 1954 | 86 | 100 | 59-41 |  |
| 25 | **us:c_seam1** | 1954 | 86 | 100 | 59-41 |  |
| 26 | **us:c_mend2** | 1951 | 39 | 612 | 362-250 |  |
| 27 | **us:c_well9** | 1949 | 55 | 233 | 125-108 |  |
| 28 | **us:c_bc1** | 1949 | 66 | 164 | 97-67 |  |
| 29 | **us:c_def3** | 1946 | 60 | 199 | 120-79 |  |
| 30 | **us:c_siege1** | 1944 | 86 | 100 | 58-42 |  |
| 31 | **us:c_end2** | 1933 | 86 | 100 | 57-43 |  |
| 32 | **us:c_open1** | 1923 | 86 | 100 | 56-44 |  |
| 33 | **us:c_flee3** | 1923 | 86 | 100 | 56-44 |  |
| 34 | **us:c_anc3** | 1919 | 66 | 163 | 88-75 |  |
| 35 | **us:c_aura2** | 1918 | 49 | 314 | 162-152 |  |
| 36 | ethanlabelle.dev | 1884 | 44 | 404 | 223-181 | 50% (c_well9 15-15) |
| 37 | **us:c_nav5** | 1860 | 75 | 126 | 61-65 |  |
| 38 | NotLLeon.v7 | 1851 | 36 | 706 | 345-361 | 69% (c_well9 11-5*) |
| 39 | georgezhang02.CB_tuning2 | 1847 | 35 | 715 | 351-364 | 80% (c_well9 8-2*) |
| 40 | **us:c_nav6** | 1844 | 75 | 129 | 58-71 |  |
| 41 | **us:c_nav4** | 1822 | 57 | 221 | 108-113 |  |
| 42 | ethanlabelle.v19 | 1776 | 44 | 395 | 201-194 | 83% (c_well9 5-1*) |
| 43 | britacatalin.FinalBot | 1770 | 36 | 670 | 296-374 | 86% (c_well9 19-3*) |
| 44 | VarunVejalla.karel | 1747 | 44 | 404 | 204-200 | 68% (c_mend2 52-25) |
| 45 | GabeG888.v8 | 1747 | 47 | 323 | 178-145 | 67% (c_well9 2-1*) |
| 46 | **us:c_swarm1** | 1744 | 53 | 271 | 128-143 |  |
| 47 | programjames.fourthbot | 1740 | 47 | 326 | 179-147 | 64% (c_mend2 7-4*) |
| 48 | VarunVejalla.ali8 | 1724 | 48 | 310 | 167-143 | 83% (c_mend2 5-1*) |
| 49 | GabeG888.v8o1 | 1720 | 47 | 321 | 179-142 | 67% (c_aura2 4-2*) |
| 50 | **us:c_line8a** | 1700 | 75 | 139 | 47-92 |  |
| 51 | **us:g_iter0** | 1681 | 53 | 456 | 230-226 |  |
| 52 | DannyZhang686.pqual2 | 1666 | 45 | 360 | 185-175 | 83% (c_mend2 5-1*) |
| 53 | **us:c_line6** | 1663 | 92 | 100 | 32-68 |  |
| 54 | NicholasKelly15.gopher10 | 1658 | 49 | 298 | 162-136 | 100% (c_anc3 3-0*) |
| 55 | louishu17.louisv10 | 1652 | 48 | 309 | 166-143 | 100% (c_bc1 3-0*) |
| 56 | **us:c_line7m** | 1651 | 92 | 100 | 31-69 |  |
| 57 | SampleProvider.SPAARK | 1645 | 48 | 308 | 163-145 | 33% (c_anc3 1-2*) |
| 58 | louishu17.wouisv8 | 1642 | 47 | 330 | 176-154 | 83% (c_aura2 5-1*) |
| 59 | reeceyang.v5anaconda | 1636 | 37 | 674 | 252-422 | 100% (c_well9 10-0*) |
| 60 | **us:c_line5** | 1614 | 95 | 100 | 28-72 |  |
| 61 | battlecode-archive.Sprint1 | 1587 | 38 | 646 | 220-426 | 100% (c_well9 10-0*) |
| 62 | **us:c_line4** | 1574 | 98 | 100 | 25-75 |  |
| 63 | ipince.bobby | 1508 | 50 | 294 | 150-144 | 67% (c_swarm1 2-1*) |
| 64 | SteamBlizzard.newVnewME | 1494 | 45 | 360 | 182-178 | 80% (g_iter0 4-1*) |
| 65 | legobridge.tacoplayer | 1480 | 47 | 354 | 173-181 | 100% (c_mend2 6-0*) |
| 66 | TheK098.qp1_7_sprint_1 | 1456 | 46 | 351 | 192-159 | 100% (c_mend2 6-0*) |
| 67 | polyllc.poly | 1444 | 51 | 292 | 151-141 | 100% (g_iter0 2-0*) |
| 68 | ColtG5.rexv9 | 1401 | 45 | 365 | 182-183 | 100% (g_iter0 2-0*) |
| 69 | toyat522.bot5a | 1391 | 45 | 362 | 167-195 | 80% (g_iter0 4-1*) |
| 70 | elgoldie.head_v5 | 1378 | 45 | 348 | 169-179 | 100% (g_iter0 2-0*) |
| 71 | DukeBas._main | 1365 | 46 | 365 | 199-166 | 100% (c_mend2 6-0*) |
| 72 | beaverbois.USQualifiers | 1348 | 46 | 346 | 182-164 | 50% (g_iter0 1-1*) |
| 73 | kevinli405.maggi3_2 | 1306 | 45 | 385 | 200-185 | 100% (g_iter0 2-0*) |
| 74 | Nawlej.PoonPoon | 1304 | 48 | 330 | 166-164 | 100% (g_iter0 2-0*) |
| 75 | yaonam.PoonPoonv4 | 1274 | 41 | 716 | 222-494 | 90% (c_well9 9-1*) |
| 76 | BrysonJGalapon.friday | 1265 | 45 | 355 | 184-171 | 100% (g_iter0 2-0*) |
| 77 | nail-e.Barry | 1241 | 45 | 364 | 184-180 | 100% (g_iter0 2-0*) |
| 78 | aj-chau.attempt1 | 1235 | 45 | 381 | 200-181 | 100% (g_iter0 5-0*) |
| 79 | kevinli405.maggi3 | 1229 | 46 | 371 | 182-189 | 100% (g_iter0 5-0*) |
| 80 | prisms-cs-club.prisms10 | 1198 | 45 | 380 | 191-189 | 100% (g_iter0 2-0*) |
| 81 | mama4294.currentPlayer | 1189 | 45 | 384 | 192-192 | 100% (g_iter0 2-0*) |
| 82 | ipince.bobby_v2 | 1159 | 44 | 426 | 212-214 | 67% (c_swarm1 2-1*) |
| 83 | bewuwy.deathbot4 | 1075 | 43 | 457 | 225-232 | 100% (g_iter0 2-0*) |
| 84 | andrewgopher.gopherbot | 1064 | 45 | 427 | 202-225 | 100% (g_iter0 2-0*) |
| 85 | JfeMak.realplayer2 | 1061 | 44 | 417 | 203-214 | 100% (g_iter0 2-0*) |
| 86 | BrysonJGalapon.aloha | 1055 | 44 | 449 | 224-225 | 100% (c_swarm1 3-0*) |
| 87 | PSUtblock.sprint_four_player | 1017 | 46 | 412 | 197-215 | 100% (g_iter0 2-0*) |
| 88 | SampleProvider.SPAARK_1_12_2023 | 995 | 45 | 460 | 240-220 | 100% (c_swarm1 3-0*) |
| 89 | Nawlej.PoonPoonv3 | 966 | 45 | 448 | 211-237 | 100% (g_iter0 5-0*) |
| 90 | SDainard-PDX.Team_Player | 955 | 47 | 409 | 191-218 | 100% (g_iter0 2-0*) |
| 91 | Juanbri02.matfisplayer1 | 954 | 45 | 447 | 222-225 | 100% (g_iter0 5-0*) |
| 92 | NolanChai.nolan_1 | 951 | 44 | 465 | 229-236 | 100% (g_iter0 2-0*) |
| 93 | andrewgopher.gopherbot1 | 935 | 46 | 423 | 196-227 | 100% (g_iter0 2-0*) |
| 94 | jyorkio.elicompbot | 909 | 46 | 433 | 212-221 | 100% (g_iter0 2-0*) |
| 95 | vontell.regressiongames | 837 | 46 | 458 | 222-236 | 100% (g_iter0 5-0*) |
| 96 | legobridge.kushalplayer | 814 | 49 | 410 | 188-222 | 100% (g_iter0 2-0*) |
| 97 | SteamBlizzard.Block | 769 | 48 | 469 | 218-251 | 100% (g_iter0 5-0*) |
| 98 | Patela171.Battlecode2023_Robot | 765 | 48 | 446 | 209-237 | 100% (g_iter0 2-0*) |
| 99 | ax-95174.MPAction | 741 | 48 | 453 | 206-247 | 100% (c_swarm1 3-0*) |
| 100 | nail-e.Dante | 694 | 49 | 480 | 240-240 | 100% (g_iter0 2-0*) |
| 101 | Chahat08.toph | 687 | 49 | 456 | 214-242 | 100% (g_iter0 2-0*) |
| 102 | michael-tyl.hqrewrite | 678 | 50 | 432 | 211-221 | 100% (g_iter0 2-0*) |
| 103 | JackLee9355.jackPlayer | 676 | 52 | 415 | 183-232 | 100% (g_iter0 2-0*) |
| 104 | mama4294.learningBot | 665 | 50 | 459 | 224-235 | 100% (g_iter0 2-0*) |
| 105 | anicolao.submission | 623 | 50 | 502 | 234-268 | 100% (g_iter0 2-0*) |
| 106 | team-remember-to-hydrate.sprint_1 | 608 | 51 | 467 | 209-258 | 100% (g_iter0 2-0*) |
| 107 | Vinceyou1.Player1 | 494 | 54 | 455 | 208-247 | 100% (g_iter0 2-0*) |
| 108 | addiesteward.elicompbot | 482 | 53 | 481 | 215-266 | 100% (g_iter0 5-0*) |
| 109 | toyat522.bot5 | 481 | 53 | 508 | 222-286 | 100% (g_iter0 2-0*) |
| 110 | michael-tyl.cc_v0_5_0_6 | 473 | 52 | 538 | 248-290 | 100% (g_iter0 2-0*) |
| 111 | Chahat08.lazarus | 440 | 54 | 496 | 226-270 | 100% (g_iter0 2-0*) |
| 112 | Swordman51.AdeptusAstartes2 | 439 | 55 | 480 | 231-249 | 100% (g_iter0 2-0*) |
| 113 | monmouth-college-cs.elicompbot | 410 | 54 | 516 | 226-290 | 100% (g_iter0 2-0*) |
| 114 | anicolao.jumbled | 325 | 57 | 502 | 228-274 | 100% (g_iter0 5-0*) |
| 115 | ShatterXD.SRNNbot | 310 | 58 | 496 | 240-256 | 100% (g_iter0 2-0*) |
| 116 | NotLLeon.player | 72 | 72 | 467 | 218-249 | 100% (g_iter0 2-0*) |
| 117 | CodeClash-ai.mysubmission | -30 | 76 | 492 | 219-273 | 100% (g_iter0 2-0*) |
| 118 | addiesteward.NDeClaw | -36 | 77 | 454 | 201-253 | 100% (g_iter0 5-0*) |
| 119 | Yooncw0223.lec3player | -352 | 88 | 423 | 73-350 | 100% (g_iter0 5-0*) |
| 120 | andrewkbank.First | -402 | 92 | 337 | 53-284 | 100% (g_iter0 2-0*) |
