# Ladder

15402 games (3348 ours, 6 of the stock examplefuncsplayer, 12048 between field bots on the ladder replica), 14966 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 109 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2104 +- 89 | 12 of 108 | 100 | 64-36 | 87.2% | 33.9% (vs 11) |
| c_spread2 | 2073 +- 88 | 13 of 108 | 100 | 61-39 | 86.1% | 30.1% (vs 11) |
| c_scout1 | 2062 +- 88 | 14 of 108 | 100 | 60-40 | 85.7% | 28.9% (vs 11) |
| c_well7 | 2062 +- 88 | 15 of 108 | 100 | 60-40 | 85.7% | 28.9% (vs 11) |
| c_mend2 | 2054 +- 74 | 16 of 108 | 138 | 86-52 | 85.4% | 28.1% (vs 11) |
| c_bc1 | 2046 +- 68 | 18 of 108 | 163 | 96-67 | 85.0% | 29.0% (vs 12) |
| c_def3 | 2043 +- 63 | 19 of 108 | 194 | 117-77 | 84.9% | 28.7% (vs 12) |
| c_end2 | 2031 +- 88 | 20 of 108 | 100 | 57-43 | 84.5% | 27.4% (vs 12) |
| c_flee3 | 2021 +- 88 | 21 of 108 | 100 | 56-44 | 84.0% | 26.2% (vs 12) |
| c_anc3 | 2013 +- 68 | 22 of 108 | 161 | 87-74 | 83.7% | 25.4% (vs 12) |
| c_aura2 | 2012 +- 52 | 23 of 108 | 311 | 160-151 | 83.7% | 25.4% (vs 12) |
| c_nav5 | 1955 +- 77 | 26 of 108 | 126 | 61-65 | 81.4% | 23.8% (vs 14) |
| c_nav6 | 1940 +- 77 | 28 of 108 | 129 | 58-71 | 80.7% | 24.1% (vs 15) |
| c_nav4 | 1916 +- 59 | 29 of 108 | 221 | 108-113 | 79.7% | 22.0% (vs 15) |
| c_swarm1 | 1838 +- 55 | 33 of 108 | 268 | 126-142 | 76.1% | 20.7% (vs 18) |
| c_line8a | 1796 +- 77 | 38 of 108 | 139 | 47-92 | 74.1% | 22.8% (vs 22) |
| g_iter0 | 1775 +- 54 | 39 of 108 | 455 | 230-225 | 73.1% | 21.0% (vs 22) |
| c_line6 | 1761 +- 93 | 41 of 108 | 100 | 32-68 | 72.5% | 21.2% (vs 23) |
| c_line7m | 1749 +- 94 | 44 of 108 | 100 | 31-69 | 71.9% | 22.5% (vs 25) |
| c_line5 | 1711 +- 96 | 48 of 108 | 100 | 28-72 | 70.0% | 22.4% (vs 28) |
| c_line4 | 1670 +- 99 | 50 of 108 | 100 | 25-75 | 68.0% | 20.1% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_mend2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2327 | 73 | 168 | 118-50 | 0% (g_iter0 0-5*) |
| 2 | awesomelemonade.finalBot | 2324 | 59 | 374 | 300-74 | 20% (c_mend2 2-8*) |
| 3 | IvanGeffner.fortytwo | 2321 | 71 | 180 | 124-56 | 0% (g_iter0 0-35) |
| 4 | carlguo866.submit26_final | 2290 | 70 | 185 | 124-61 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2268 | 56 | 383 | 295-88 | 40% (c_mend2 4-6*) |
| 6 | AnOvercookedFork.quals | 2206 | 66 | 202 | 131-71 | 33% (c_bc1 1-2*) |
| 7 | pranayagra.finalbotfinaltwo | 2175 | 65 | 209 | 135-74 | 29% (c_aura2 5-12*) |
| 8 | pranayagra.finalbotfinal | 2167 | 48 | 461 | 311-150 | 30% (c_mend2 3-7*) |
| 9 | georgezhang02.FB_ZZZ | 2153 | 64 | 204 | 124-80 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2131 | 66 | 201 | 127-74 | 22% (c_bc1 2-7*) |
| 11 | jmerle.camel_case_v30_final | 2120 | 48 | 441 | 295-146 | 40% (c_mend2 4-6*) |
| 12 | **us:c_well5** | 2104 | 89 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2073 | 88 | 100 | 61-39 |  |
| 14 | **us:c_scout1** | 2062 | 88 | 100 | 60-40 |  |
| 15 | **us:c_well7** | 2062 | 88 | 100 | 60-40 |  |
| 16 | **us:c_mend2** | 2054 | 74 | 138 | 86-52 |  |
| 17 | CyrilSharma.finalBot | 2047 | 57 | 257 | 151-106 | 22% (c_aura2 5-18*) |
| 18 | **us:c_bc1** | 2046 | 68 | 163 | 96-67 |  |
| 19 | **us:c_def3** | 2043 | 63 | 194 | 117-77 |  |
| 20 | **us:c_end2** | 2031 | 88 | 100 | 57-43 |  |
| 21 | **us:c_flee3** | 2021 | 88 | 100 | 56-44 |  |
| 22 | **us:c_anc3** | 2013 | 68 | 161 | 87-74 |  |
| 23 | **us:c_aura2** | 2012 | 52 | 311 | 160-151 |  |
| 24 | ethanlabelle.dev | 1991 | 55 | 259 | 149-110 | 53% (c_bc1 8-7*) |
| 25 | NotLLeon.v7 | 1957 | 44 | 476 | 252-224 | 72% (c_mend2 13-5*) |
| 26 | **us:c_nav5** | 1955 | 77 | 126 | 61-65 |  |
| 27 | georgezhang02.CB_tuning2 | 1949 | 45 | 443 | 242-201 | 53% (c_mend2 10-9*) |
| 28 | **us:c_nav6** | 1940 | 77 | 129 | 58-71 |  |
| 29 | **us:c_nav4** | 1916 | 59 | 221 | 108-113 |  |
| 30 | ethanlabelle.v19 | 1888 | 55 | 252 | 137-115 | 92% (c_mend2 11-1*) |
| 31 | britacatalin.FinalBot | 1870 | 45 | 444 | 215-229 | 80% (c_mend2 8-2*) |
| 32 | GabeG888.v8 | 1838 | 55 | 242 | 130-112 | 89% (c_def3 16-2*) |
| 33 | **us:c_swarm1** | 1838 | 55 | 268 | 126-142 |  |
| 34 | VarunVejalla.karel | 1820 | 55 | 253 | 137-116 | 44% (c_mend2 4-5*) |
| 35 | programjames.fourthbot | 1819 | 57 | 233 | 129-104 | 100% (c_aura2 3-0*) |
| 36 | GabeG888.v8o1 | 1815 | 55 | 243 | 139-104 | 67% (c_aura2 4-2*) |
| 37 | VarunVejalla.ali8 | 1812 | 58 | 227 | 127-100 | 50% (c_aura2 3-3*) |
| 38 | **us:c_line8a** | 1796 | 77 | 139 | 47-92 |  |
| 39 | **us:g_iter0** | 1775 | 54 | 455 | 230-225 |  |
| 40 | DannyZhang686.pqual2 | 1773 | 54 | 266 | 143-123 | 83% (c_anc3 5-1*) |
| 41 | **us:c_line6** | 1761 | 93 | 100 | 32-68 |  |
| 42 | NicholasKelly15.gopher10 | 1754 | 59 | 213 | 119-94 | 100% (c_anc3 3-0*) |
| 43 | louishu17.louisv10 | 1750 | 57 | 231 | 125-106 | 100% (c_bc1 3-0*) |
| 44 | **us:c_line7m** | 1749 | 94 | 100 | 31-69 |  |
| 45 | reeceyang.v5anaconda | 1734 | 44 | 470 | 193-277 | 90% (c_mend2 9-1*) |
| 46 | louishu17.wouisv8 | 1734 | 56 | 254 | 138-116 | 83% (c_aura2 5-1*) |
| 47 | SampleProvider.SPAARK | 1725 | 56 | 234 | 129-105 | 33% (c_anc3 1-2*) |
| 48 | **us:c_line5** | 1711 | 96 | 100 | 28-72 |  |
| 49 | battlecode-archive.Sprint1 | 1686 | 46 | 431 | 167-264 | 90% (c_mend2 9-1*) |
| 50 | **us:c_line4** | 1670 | 99 | 100 | 25-75 |  |
| 51 | ipince.bobby | 1617 | 59 | 220 | 117-103 | 67% (c_swarm1 2-1*) |
| 52 | SteamBlizzard.newVnewME | 1570 | 53 | 267 | 136-131 | 80% (g_iter0 4-1*) |
| 53 | legobridge.tacoplayer | 1564 | 56 | 253 | 133-120 | 85% (g_iter0 11-2*) |
| 54 | TheK098.qp1_7_sprint_1 | 1542 | 55 | 254 | 138-116 | 100% (c_swarm1 6-0*) |
| 55 | polyllc.poly | 1530 | 60 | 223 | 115-108 | 100% (g_iter0 2-0*) |
| 56 | toyat522.bot5a | 1479 | 52 | 276 | 136-140 | 80% (g_iter0 4-1*) |
| 57 | elgoldie.head_v5 | 1479 | 52 | 258 | 128-130 | 100% (g_iter0 2-0*) |
| 58 | DukeBas._main | 1465 | 55 | 244 | 129-115 | 100% (g_iter0 2-0*) |
| 59 | ColtG5.rexv9 | 1464 | 53 | 262 | 133-129 | 100% (g_iter0 2-0*) |
| 60 | beaverbois.USQualifiers | 1429 | 53 | 263 | 138-125 | 50% (g_iter0 1-1*) |
| 61 | kevinli405.maggi3_2 | 1388 | 50 | 306 | 154-152 | 100% (g_iter0 2-0*) |
| 62 | Nawlej.PoonPoon | 1384 | 55 | 254 | 123-131 | 100% (g_iter0 2-0*) |
| 63 | yaonam.PoonPoonv4 | 1354 | 47 | 504 | 172-332 | 90% (c_mend2 9-1*) |
| 64 | BrysonJGalapon.friday | 1353 | 52 | 260 | 134-126 | 100% (g_iter0 2-0*) |
| 65 | nail-e.Barry | 1329 | 51 | 281 | 140-141 | 100% (g_iter0 2-0*) |
| 66 | aj-chau.attempt1 | 1325 | 52 | 277 | 142-135 | 100% (g_iter0 5-0*) |
| 67 | kevinli405.maggi3 | 1316 | 53 | 275 | 139-136 | 100% (g_iter0 5-0*) |
| 68 | prisms-cs-club.prisms10 | 1278 | 54 | 263 | 129-134 | 100% (g_iter0 2-0*) |
| 69 | mama4294.currentPlayer | 1264 | 52 | 285 | 141-144 | 100% (g_iter0 2-0*) |
| 70 | ipince.bobby_v2 | 1249 | 51 | 313 | 157-156 | 67% (c_swarm1 2-1*) |
| 71 | bewuwy.deathbot4 | 1156 | 50 | 334 | 159-175 | 100% (g_iter0 2-0*) |
| 72 | JfeMak.realplayer2 | 1155 | 52 | 293 | 143-150 | 100% (g_iter0 2-0*) |
| 73 | BrysonJGalapon.aloha | 1151 | 50 | 328 | 163-165 | 100% (c_swarm1 3-0*) |
| 74 | andrewgopher.gopherbot | 1150 | 51 | 313 | 151-162 | 100% (g_iter0 2-0*) |
| 75 | PSUtblock.sprint_four_player | 1111 | 53 | 304 | 150-154 | 100% (g_iter0 2-0*) |
| 76 | SampleProvider.SPAARK_1_12_2023 | 1074 | 51 | 332 | 160-172 | 100% (c_swarm1 3-0*) |
| 77 | Nawlej.PoonPoonv3 | 1050 | 51 | 326 | 157-169 | 100% (g_iter0 5-0*) |
| 78 | SDainard-PDX.Team_Player | 1047 | 54 | 294 | 145-149 | 100% (g_iter0 2-0*) |
| 79 | NolanChai.nolan_1 | 1041 | 50 | 350 | 168-182 | 100% (g_iter0 2-0*) |
| 80 | Juanbri02.matfisplayer1 | 1037 | 51 | 332 | 157-175 | 100% (g_iter0 5-0*) |
| 81 | andrewgopher.gopherbot1 | 1033 | 53 | 309 | 143-166 | 100% (g_iter0 2-0*) |
| 82 | jyorkio.elicompbot | 1012 | 52 | 320 | 157-163 | 100% (g_iter0 2-0*) |
| 83 | vontell.regressiongames | 942 | 51 | 346 | 169-177 | 100% (g_iter0 5-0*) |
| 84 | legobridge.kushalplayer | 920 | 56 | 289 | 133-156 | 100% (g_iter0 2-0*) |
| 85 | SteamBlizzard.Block | 895 | 54 | 350 | 160-190 | 100% (g_iter0 5-0*) |
| 86 | Patela171.Battlecode2023_Robot | 892 | 55 | 320 | 148-172 | 100% (g_iter0 2-0*) |
| 87 | ax-95174.MPAction | 868 | 55 | 324 | 155-169 | 100% (c_swarm1 3-0*) |
| 88 | JackLee9355.jackPlayer | 804 | 58 | 319 | 144-175 | 100% (g_iter0 2-0*) |
| 89 | nail-e.Dante | 794 | 55 | 347 | 167-180 | 100% (g_iter0 2-0*) |
| 90 | Chahat08.toph | 794 | 55 | 338 | 158-180 | 100% (g_iter0 2-0*) |
| 91 | michael-tyl.hqrewrite | 776 | 56 | 331 | 156-175 | 100% (g_iter0 2-0*) |
| 92 | mama4294.learningBot | 766 | 57 | 331 | 149-182 | 100% (g_iter0 2-0*) |
| 93 | anicolao.submission | 719 | 56 | 378 | 172-206 | 100% (g_iter0 2-0*) |
| 94 | team-remember-to-hydrate.sprint_1 | 676 | 59 | 332 | 146-186 | 100% (g_iter0 2-0*) |
| 95 | toyat522.bot5 | 588 | 60 | 379 | 173-206 | 100% (g_iter0 2-0*) |
| 96 | Vinceyou1.Player1 | 583 | 61 | 327 | 145-182 | 100% (g_iter0 2-0*) |
| 97 | addiesteward.elicompbot | 579 | 60 | 362 | 163-199 | 100% (g_iter0 5-0*) |
| 98 | michael-tyl.cc_v0_5_0_6 | 559 | 60 | 396 | 175-221 | 100% (g_iter0 2-0*) |
| 99 | Chahat08.lazarus | 533 | 62 | 360 | 163-197 | 100% (g_iter0 2-0*) |
| 100 | Swordman51.AdeptusAstartes2 | 525 | 62 | 339 | 152-187 | 100% (g_iter0 2-0*) |
| 101 | monmouth-college-cs.elicompbot | 518 | 61 | 375 | 165-210 | 100% (g_iter0 2-0*) |
| 102 | anicolao.jumbled | 411 | 65 | 377 | 168-209 | 100% (g_iter0 5-0*) |
| 103 | ShatterXD.SRNNbot | 383 | 68 | 340 | 148-192 | 100% (g_iter0 2-0*) |
| 104 | NotLLeon.player | 183 | 82 | 320 | 146-174 | 100% (g_iter0 2-0*) |
| 105 | CodeClash-ai.mysubmission | 111 | 83 | 362 | 152-210 | 100% (g_iter0 2-0*) |
| 106 | addiesteward.NDeClaw | 90 | 87 | 327 | 138-189 | 100% (g_iter0 5-0*) |
| 107 | Yooncw0223.lec3player | -225 | 101 | 307 | 46-261 | 100% (g_iter0 5-0*) |
| 108 | andrewkbank.First | -279 | 107 | 236 | 32-204 | 100% (g_iter0 2-0*) |
