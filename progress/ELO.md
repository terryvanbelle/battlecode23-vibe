# Ladder

13315 games (2740 ours, 6 of the stock examplefuncsplayer, 10569 between field bots on the ladder replica), 12987 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 104 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2139 +- 91 | 12 of 103 | 100 | 64-36 | 87.2% | 33.1% (vs 11) |
| c_spread2 | 2107 +- 90 | 13 of 103 | 100 | 61-39 | 86.0% | 29.3% (vs 11) |
| c_def3 | 2077 +- 64 | 15 of 103 | 194 | 117-77 | 84.9% | 27.9% (vs 12) |
| c_flee3 | 2055 +- 89 | 16 of 103 | 100 | 56-44 | 84.0% | 25.5% (vs 12) |
| c_anc3 | 2048 +- 70 | 17 of 103 | 161 | 87-74 | 83.7% | 24.8% (vs 12) |
| c_aura2 | 2044 +- 54 | 18 of 103 | 308 | 159-149 | 83.6% | 24.5% (vs 12) |
| c_nav5 | 1989 +- 78 | 21 of 103 | 126 | 61-65 | 81.3% | 23.3% (vs 14) |
| c_nav6 | 1975 +- 78 | 23 of 103 | 129 | 58-71 | 80.7% | 23.8% (vs 15) |
| c_nav4 | 1949 +- 60 | 24 of 103 | 221 | 108-113 | 79.6% | 21.5% (vs 15) |
| c_swarm1 | 1869 +- 56 | 27 of 103 | 268 | 126-142 | 75.9% | 18.6% (vs 17) |
| c_line8a | 1826 +- 78 | 33 of 103 | 139 | 47-92 | 73.9% | 22.6% (vs 22) |
| g_iter0 | 1810 +- 55 | 34 of 103 | 455 | 230-225 | 73.1% | 21.3% (vs 22) |
| c_line6 | 1793 +- 94 | 36 of 103 | 100 | 32-68 | 72.2% | 21.1% (vs 23) |
| c_line7m | 1780 +- 95 | 38 of 103 | 100 | 31-69 | 71.6% | 21.3% (vs 24) |
| c_line5 | 1742 +- 97 | 43 of 103 | 100 | 28-72 | 69.7% | 22.4% (vs 28) |
| c_line4 | 1701 +- 100 | 45 of 103 | 100 | 25-75 | 67.6% | 20.1% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_aura2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2382 | 77 | 169 | 122-47 | 0% (g_iter0 0-35) |
| 2 | awesomelemonade.finalBot | 2374 | 68 | 309 | 252-57 | 20% (c_aura2 2-8*) |
| 3 | maxwelljones14.MPWorking | 2360 | 77 | 157 | 108-49 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2319 | 74 | 170 | 113-57 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2309 | 63 | 321 | 251-70 | 40% (c_aura2 4-6*) |
| 6 | AnOvercookedFork.quals | 2247 | 71 | 181 | 116-65 | 20% (c_aura2 3-12*) |
| 7 | pranayagra.finalbotfinaltwo | 2215 | 68 | 200 | 130-70 | 29% (c_aura2 5-12*) |
| 8 | georgezhang02.FB_ZZZ | 2210 | 68 | 188 | 121-67 | 0% (c_anc3 0-3*) |
| 9 | pranayagra.finalbotfinal | 2201 | 54 | 391 | 269-122 | 36% (c_aura2 9-16*) |
| 10 | battlecode-archive.sprintBot | 2180 | 72 | 178 | 116-62 | 33% (c_aura2 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2149 | 53 | 378 | 257-121 | 32% (c_aura2 10-21) |
| 12 | **us:c_well5** | 2139 | 91 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2107 | 90 | 100 | 61-39 |  |
| 14 | CyrilSharma.finalBot | 2080 | 60 | 244 | 144-100 | 22% (c_aura2 5-18*) |
| 15 | **us:c_def3** | 2077 | 64 | 194 | 117-77 |  |
| 16 | **us:c_flee3** | 2055 | 89 | 100 | 56-44 |  |
| 17 | **us:c_anc3** | 2048 | 70 | 161 | 87-74 |  |
| 18 | **us:c_aura2** | 2044 | 54 | 308 | 159-149 |  |
| 19 | ethanlabelle.dev | 2022 | 59 | 229 | 136-93 | 54% (c_aura2 13-11*) |
| 20 | NotLLeon.v7 | 1994 | 49 | 384 | 219-165 | 68% (c_aura2 17-8*) |
| 21 | **us:c_nav5** | 1989 | 78 | 126 | 61-65 |  |
| 22 | georgezhang02.CB_tuning2 | 1975 | 49 | 369 | 209-160 | 62% (c_aura2 21-13) |
| 23 | **us:c_nav6** | 1975 | 78 | 129 | 58-71 |  |
| 24 | **us:c_nav4** | 1949 | 60 | 221 | 108-113 |  |
| 25 | ethanlabelle.v19 | 1916 | 59 | 214 | 124-90 | 67% (c_aura2 10-5*) |
| 26 | britacatalin.FinalBot | 1909 | 48 | 382 | 199-183 | 73% (c_aura2 16-6*) |
| 27 | **us:c_swarm1** | 1869 | 56 | 268 | 126-142 |  |
| 28 | GabeG888.v8 | 1868 | 57 | 224 | 118-106 | 89% (c_def3 16-2*) |
| 29 | programjames.fourthbot | 1847 | 60 | 215 | 116-99 | 100% (c_aura2 3-0*) |
| 30 | GabeG888.v8o1 | 1846 | 58 | 216 | 125-91 | 67% (c_aura2 4-2*) |
| 31 | VarunVejalla.karel | 1841 | 58 | 226 | 125-101 | 33% (c_aura2 1-2*) |
| 32 | VarunVejalla.ali8 | 1835 | 62 | 204 | 112-92 | 50% (c_aura2 3-3*) |
| 33 | **us:c_line8a** | 1826 | 78 | 139 | 47-92 |  |
| 34 | **us:g_iter0** | 1810 | 55 | 455 | 230-225 |  |
| 35 | DannyZhang686.pqual2 | 1810 | 57 | 234 | 124-110 | 83% (c_anc3 5-1*) |
| 36 | **us:c_line6** | 1793 | 94 | 100 | 32-68 |  |
| 37 | NicholasKelly15.gopher10 | 1784 | 62 | 196 | 109-87 | 100% (c_anc3 3-0*) |
| 38 | **us:c_line7m** | 1780 | 95 | 100 | 31-69 |  |
| 39 | louishu17.louisv10 | 1778 | 60 | 213 | 117-96 | 100% (c_nav4 6-0*) |
| 40 | reeceyang.v5anaconda | 1761 | 48 | 385 | 167-218 | 80% (c_aura2 8-2*) |
| 41 | louishu17.wouisv8 | 1761 | 61 | 218 | 116-102 | 83% (c_aura2 5-1*) |
| 42 | SampleProvider.SPAARK | 1758 | 59 | 216 | 119-97 | 33% (c_anc3 1-2*) |
| 43 | **us:c_line5** | 1742 | 97 | 100 | 28-72 |  |
| 44 | battlecode-archive.Sprint1 | 1710 | 49 | 354 | 140-214 | 100% (c_aura2 10-0*) |
| 45 | **us:c_line4** | 1701 | 100 | 100 | 25-75 |  |
| 46 | ipince.bobby | 1660 | 63 | 188 | 102-86 | 67% (c_swarm1 2-1*) |
| 47 | SteamBlizzard.newVnewME | 1611 | 55 | 246 | 125-121 | 80% (g_iter0 4-1*) |
| 48 | legobridge.tacoplayer | 1608 | 59 | 228 | 121-107 | 85% (g_iter0 11-2*) |
| 49 | TheK098.qp1_7_sprint_1 | 1585 | 58 | 226 | 122-104 | 100% (c_swarm1 6-0*) |
| 50 | polyllc.poly | 1560 | 64 | 196 | 98-98 | 100% (g_iter0 2-0*) |
| 51 | toyat522.bot5a | 1537 | 55 | 242 | 125-117 | 80% (g_iter0 4-1*) |
| 52 | elgoldie.head_v5 | 1523 | 54 | 237 | 118-119 | 100% (g_iter0 2-0*) |
| 53 | DukeBas._main | 1513 | 58 | 221 | 119-102 | 100% (g_iter0 2-0*) |
| 54 | ColtG5.rexv9 | 1498 | 55 | 239 | 120-119 | 100% (g_iter0 2-0*) |
| 55 | beaverbois.USQualifiers | 1473 | 56 | 232 | 121-111 | 50% (g_iter0 1-1*) |
| 56 | Nawlej.PoonPoon | 1434 | 58 | 225 | 115-110 | 100% (g_iter0 2-0*) |
| 57 | kevinli405.maggi3_2 | 1431 | 54 | 262 | 129-133 | 100% (g_iter0 2-0*) |
| 58 | BrysonJGalapon.friday | 1407 | 56 | 220 | 115-105 | 100% (g_iter0 2-0*) |
| 59 | nail-e.Barry | 1388 | 54 | 240 | 120-120 | 100% (g_iter0 2-0*) |
| 60 | yaonam.PoonPoonv4 | 1384 | 50 | 418 | 144-274 | 90% (c_aura2 9-1*) |
| 61 | aj-chau.attempt1 | 1379 | 56 | 240 | 124-116 | 100% (g_iter0 5-0*) |
| 62 | kevinli405.maggi3 | 1368 | 56 | 246 | 126-120 | 100% (g_iter0 5-0*) |
| 63 | prisms-cs-club.prisms10 | 1331 | 56 | 240 | 119-121 | 100% (g_iter0 2-0*) |
| 64 | mama4294.currentPlayer | 1311 | 55 | 252 | 124-128 | 100% (g_iter0 2-0*) |
| 65 | ipince.bobby_v2 | 1282 | 55 | 264 | 130-134 | 67% (c_swarm1 2-1*) |
| 66 | bewuwy.deathbot4 | 1215 | 52 | 304 | 149-155 | 100% (g_iter0 2-0*) |
| 67 | andrewgopher.gopherbot | 1212 | 54 | 277 | 134-143 | 100% (g_iter0 2-0*) |
| 68 | JfeMak.realplayer2 | 1202 | 55 | 251 | 125-126 | 100% (g_iter0 2-0*) |
| 69 | BrysonJGalapon.aloha | 1199 | 53 | 281 | 140-141 | 100% (c_swarm1 3-0*) |
| 70 | PSUtblock.sprint_four_player | 1172 | 57 | 256 | 128-128 | 100% (g_iter0 2-0*) |
| 71 | SampleProvider.SPAARK_1_12_2023 | 1141 | 54 | 282 | 138-144 | 100% (c_swarm1 3-0*) |
| 72 | Nawlej.PoonPoonv3 | 1117 | 53 | 292 | 141-151 | 100% (g_iter0 5-0*) |
| 73 | Juanbri02.matfisplayer1 | 1109 | 54 | 283 | 137-146 | 100% (g_iter0 5-0*) |
| 74 | NolanChai.nolan_1 | 1100 | 52 | 309 | 147-162 | 100% (g_iter0 2-0*) |
| 75 | andrewgopher.gopherbot1 | 1091 | 55 | 282 | 130-152 | 100% (g_iter0 2-0*) |
| 76 | SDainard-PDX.Team_Player | 1090 | 57 | 257 | 122-135 | 100% (g_iter0 2-0*) |
| 77 | jyorkio.elicompbot | 1063 | 55 | 269 | 129-140 | 100% (g_iter0 2-0*) |
| 78 | vontell.regressiongames | 1010 | 54 | 293 | 141-152 | 100% (g_iter0 5-0*) |
| 79 | legobridge.kushalplayer | 981 | 60 | 244 | 112-132 | 100% (g_iter0 2-0*) |
| 80 | Patela171.Battlecode2023_Robot | 960 | 56 | 287 | 132-155 | 100% (g_iter0 2-0*) |
| 81 | SteamBlizzard.Block | 956 | 56 | 307 | 136-171 | 100% (g_iter0 5-0*) |
| 82 | ax-95174.MPAction | 944 | 57 | 273 | 127-146 | 100% (c_swarm1 3-0*) |
| 83 | JackLee9355.jackPlayer | 898 | 60 | 277 | 122-155 | 100% (g_iter0 2-0*) |
| 84 | nail-e.Dante | 868 | 56 | 313 | 151-162 | 100% (g_iter0 2-0*) |
| 85 | Chahat08.toph | 864 | 58 | 283 | 129-154 | 100% (g_iter0 2-0*) |
| 86 | michael-tyl.hqrewrite | 863 | 59 | 279 | 129-150 | 100% (g_iter0 2-0*) |
| 87 | mama4294.learningBot | 837 | 60 | 283 | 127-156 | 100% (g_iter0 2-0*) |
| 88 | anicolao.submission | 811 | 58 | 331 | 153-178 | 100% (g_iter0 2-0*) |
| 89 | team-remember-to-hydrate.sprint_1 | 736 | 62 | 292 | 126-166 | 100% (g_iter0 2-0*) |
| 90 | Vinceyou1.Player1 | 664 | 63 | 283 | 119-164 | 100% (g_iter0 2-0*) |
| 91 | addiesteward.elicompbot | 645 | 63 | 308 | 133-175 | 100% (g_iter0 5-0*) |
| 92 | toyat522.bot5 | 632 | 63 | 330 | 151-179 | 100% (g_iter0 2-0*) |
| 93 | michael-tyl.cc_v0_5_0_6 | 627 | 62 | 349 | 153-196 | 100% (g_iter0 2-0*) |
| 94 | Chahat08.lazarus | 595 | 65 | 311 | 140-171 | 100% (g_iter0 2-0*) |
| 95 | monmouth-college-cs.elicompbot | 589 | 63 | 341 | 152-189 | 100% (g_iter0 2-0*) |
| 96 | Swordman51.AdeptusAstartes2 | 579 | 65 | 305 | 132-173 | 100% (g_iter0 2-0*) |
| 97 | anicolao.jumbled | 470 | 69 | 325 | 142-183 | 100% (g_iter0 5-0*) |
| 98 | ShatterXD.SRNNbot | 458 | 70 | 292 | 126-166 | 100% (g_iter0 2-0*) |
| 99 | NotLLeon.player | 246 | 85 | 286 | 127-159 | 100% (g_iter0 2-0*) |
| 100 | CodeClash-ai.mysubmission | 213 | 85 | 322 | 141-181 | 100% (g_iter0 2-0*) |
| 101 | addiesteward.NDeClaw | 171 | 91 | 285 | 118-167 | 100% (g_iter0 5-0*) |
| 102 | Yooncw0223.lec3player | -136 | 104 | 284 | 41-243 | 100% (g_iter0 5-0*) |
| 103 | andrewkbank.First | -204 | 113 | 214 | 26-188 | 100% (g_iter0 2-0*) |
