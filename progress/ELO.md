# Ladder

12140 games (2570 ours, 6 of the stock examplefuncsplayer, 9564 between field bots on the ladder replica), 11878 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 104 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2139 +- 91 | 12 of 103 | 100 | 64-36 | 87.1% | 32.6% (vs 11) |
| c_spread2 | 2108 +- 169 | 13 of 103 | 20 | 7-13 | 86.0% | 29.0% (vs 11) |
| c_def3 | 2077 +- 65 | 14 of 103 | 194 | 117-77 | 84.8% | 25.6% (vs 11) |
| c_aura2 | 2077 +- 62 | 15 of 103 | 223 | 120-103 | 84.8% | 25.6% (vs 11) |
| c_flee3 | 2054 +- 89 | 17 of 103 | 100 | 56-44 | 84.0% | 25.4% (vs 12) |
| c_anc3 | 2048 +- 70 | 18 of 103 | 161 | 87-74 | 83.7% | 24.7% (vs 12) |
| c_nav5 | 1988 +- 78 | 21 of 103 | 126 | 61-65 | 81.3% | 23.0% (vs 14) |
| c_nav6 | 1975 +- 78 | 23 of 103 | 129 | 58-71 | 80.7% | 23.7% (vs 15) |
| c_nav4 | 1947 +- 60 | 24 of 103 | 221 | 108-113 | 79.5% | 21.1% (vs 15) |
| c_swarm1 | 1868 +- 57 | 28 of 103 | 268 | 126-142 | 75.9% | 20.2% (vs 18) |
| c_line8a | 1826 +- 78 | 32 of 103 | 139 | 47-92 | 73.9% | 21.4% (vs 21) |
| g_iter0 | 1811 +- 55 | 35 of 103 | 455 | 230-225 | 73.1% | 22.7% (vs 23) |
| c_line6 | 1794 +- 94 | 36 of 103 | 100 | 32-68 | 72.3% | 21.3% (vs 23) |
| c_line7m | 1782 +- 95 | 37 of 103 | 100 | 31-69 | 71.7% | 20.3% (vs 23) |
| c_line5 | 1744 +- 97 | 43 of 103 | 100 | 28-72 | 69.8% | 22.7% (vs 28) |
| c_line4 | 1703 +- 100 | 45 of 103 | 100 | 25-75 | 67.7% | 20.4% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_aura2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2399 | 81 | 157 | 117-40 | 0% (g_iter0 0-35) |
| 2 | awesomelemonade.finalBot | 2379 | 71 | 288 | 238-50 | 20% (c_aura2 2-8*) |
| 3 | maxwelljones14.MPWorking | 2366 | 81 | 146 | 102-44 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2309 | 78 | 156 | 103-53 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2301 | 64 | 310 | 243-67 | 40% (c_aura2 4-6*) |
| 6 | AnOvercookedFork.quals | 2267 | 77 | 161 | 107-54 | 22% (c_aura2 2-7*) |
| 7 | pranayagra.finalbotfinaltwo | 2229 | 71 | 185 | 123-62 | 29% (c_aura2 5-12*) |
| 8 | georgezhang02.FB_ZZZ | 2208 | 71 | 176 | 114-62 | 0% (c_anc3 0-3*) |
| 9 | pranayagra.finalbotfinal | 2199 | 55 | 367 | 252-115 | 41% (c_aura2 9-13*) |
| 10 | battlecode-archive.sprintBot | 2182 | 73 | 172 | 115-57 | 33% (c_aura2 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2148 | 54 | 360 | 247-113 | 33% (c_aura2 9-18*) |
| 12 | **us:c_well5** | 2139 | 91 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2108 | 169 | 20 | 7-13 |  |
| 14 | **us:c_def3** | 2077 | 65 | 194 | 117-77 |  |
| 15 | **us:c_aura2** | 2077 | 62 | 223 | 120-103 |  |
| 16 | CyrilSharma.finalBot | 2066 | 63 | 219 | 128-91 | 33% (c_aura2 2-4*) |
| 17 | **us:c_flee3** | 2054 | 89 | 100 | 56-44 |  |
| 18 | **us:c_anc3** | 2048 | 70 | 161 | 87-74 |  |
| 19 | ethanlabelle.dev | 2030 | 61 | 212 | 125-87 | 52% (c_aura2 11-10*) |
| 20 | NotLLeon.v7 | 1995 | 51 | 347 | 203-144 | 60% (c_aura2 6-4*) |
| 21 | **us:c_nav5** | 1988 | 78 | 126 | 61-65 |  |
| 22 | georgezhang02.CB_tuning2 | 1979 | 52 | 333 | 194-139 | 63% (c_aura2 12-7*) |
| 23 | **us:c_nav6** | 1975 | 78 | 129 | 58-71 |  |
| 24 | **us:c_nav4** | 1947 | 60 | 221 | 108-113 |  |
| 25 | ethanlabelle.v19 | 1911 | 62 | 194 | 109-85 | 67% (c_aura2 10-5*) |
| 26 | britacatalin.FinalBot | 1904 | 50 | 348 | 182-166 | 80% (c_aura2 12-3*) |
| 27 | GabeG888.v8 | 1874 | 59 | 211 | 112-99 | 89% (c_def3 16-2*) |
| 28 | **us:c_swarm1** | 1868 | 57 | 268 | 126-142 |  |
| 29 | programjames.fourthbot | 1846 | 64 | 192 | 105-87 | 100% (c_aura2 3-0*) |
| 30 | VarunVejalla.ali8 | 1839 | 65 | 187 | 107-80 | 100% (c_def3 8-0*) |
| 31 | GabeG888.v8o1 | 1834 | 61 | 195 | 111-84 | 100% (c_nav5 3-0*) |
| 32 | **us:c_line8a** | 1826 | 78 | 139 | 47-92 |  |
| 33 | VarunVejalla.karel | 1826 | 60 | 209 | 114-95 | 67% (c_nav4 6-3*) |
| 34 | DannyZhang686.pqual2 | 1815 | 59 | 220 | 118-102 | 83% (c_anc3 5-1*) |
| 35 | **us:g_iter0** | 1811 | 55 | 455 | 230-225 |  |
| 36 | **us:c_line6** | 1794 | 94 | 100 | 32-68 |  |
| 37 | **us:c_line7m** | 1782 | 95 | 100 | 31-69 |  |
| 38 | NicholasKelly15.gopher10 | 1779 | 66 | 172 | 95-77 | 100% (c_anc3 3-0*) |
| 39 | louishu17.louisv10 | 1766 | 63 | 194 | 107-87 | 100% (c_nav4 6-0*) |
| 40 | SampleProvider.SPAARK | 1761 | 61 | 197 | 111-86 | 33% (c_anc3 1-2*) |
| 41 | louishu17.wouisv8 | 1760 | 63 | 213 | 113-100 | 83% (c_aura2 5-1*) |
| 42 | reeceyang.v5anaconda | 1759 | 50 | 356 | 156-200 | 80% (c_aura2 8-2*) |
| 43 | **us:c_line5** | 1744 | 97 | 100 | 28-72 |  |
| 44 | battlecode-archive.Sprint1 | 1723 | 50 | 332 | 139-193 | 100% (c_aura2 10-0*) |
| 45 | **us:c_line4** | 1703 | 100 | 100 | 25-75 |  |
| 46 | ipince.bobby | 1655 | 66 | 170 | 97-73 | 67% (c_swarm1 2-1*) |
| 47 | legobridge.tacoplayer | 1608 | 61 | 214 | 116-98 | 85% (g_iter0 11-2*) |
| 48 | SteamBlizzard.newVnewME | 1607 | 58 | 225 | 112-113 | 80% (g_iter0 4-1*) |
| 49 | TheK098.qp1_7_sprint_1 | 1592 | 60 | 212 | 118-94 | 100% (c_swarm1 6-0*) |
| 50 | polyllc.poly | 1577 | 67 | 182 | 91-91 | 100% (g_iter0 2-0*) |
| 51 | toyat522.bot5a | 1533 | 58 | 221 | 111-110 | 80% (g_iter0 4-1*) |
| 52 | elgoldie.head_v5 | 1518 | 57 | 219 | 107-112 | 100% (g_iter0 2-0*) |
| 53 | DukeBas._main | 1506 | 60 | 209 | 111-98 | 100% (g_iter0 2-0*) |
| 54 | ColtG5.rexv9 | 1499 | 57 | 230 | 117-113 | 100% (g_iter0 2-0*) |
| 55 | beaverbois.USQualifiers | 1464 | 59 | 210 | 111-99 | 50% (g_iter0 1-1*) |
| 56 | kevinli405.maggi3_2 | 1441 | 57 | 237 | 117-120 | 100% (g_iter0 2-0*) |
| 57 | Nawlej.PoonPoon | 1418 | 61 | 204 | 103-101 | 100% (g_iter0 2-0*) |
| 58 | BrysonJGalapon.friday | 1405 | 59 | 202 | 103-99 | 100% (g_iter0 2-0*) |
| 59 | nail-e.Barry | 1393 | 56 | 225 | 115-110 | 100% (g_iter0 2-0*) |
| 60 | yaonam.PoonPoonv4 | 1390 | 52 | 385 | 134-251 | 90% (c_aura2 9-1*) |
| 61 | kevinli405.maggi3 | 1370 | 58 | 234 | 120-114 | 100% (g_iter0 5-0*) |
| 62 | aj-chau.attempt1 | 1366 | 61 | 204 | 105-99 | 100% (g_iter0 5-0*) |
| 63 | prisms-cs-club.prisms10 | 1320 | 59 | 216 | 102-114 | 100% (g_iter0 2-0*) |
| 64 | mama4294.currentPlayer | 1300 | 57 | 232 | 114-118 | 100% (g_iter0 2-0*) |
| 65 | ipince.bobby_v2 | 1291 | 60 | 220 | 107-113 | 67% (c_swarm1 2-1*) |
| 66 | andrewgopher.gopherbot | 1215 | 56 | 259 | 128-131 | 100% (g_iter0 2-0*) |
| 67 | bewuwy.deathbot4 | 1209 | 54 | 275 | 131-144 | 100% (g_iter0 2-0*) |
| 68 | JfeMak.realplayer2 | 1205 | 60 | 208 | 103-105 | 100% (g_iter0 2-0*) |
| 69 | BrysonJGalapon.aloha | 1204 | 55 | 251 | 124-127 | 100% (c_swarm1 3-0*) |
| 70 | PSUtblock.sprint_four_player | 1162 | 62 | 218 | 109-109 | 100% (g_iter0 2-0*) |
| 71 | SampleProvider.SPAARK_1_12_2023 | 1141 | 56 | 258 | 125-133 | 100% (c_swarm1 3-0*) |
| 72 | Nawlej.PoonPoonv3 | 1117 | 56 | 266 | 128-138 | 100% (g_iter0 5-0*) |
| 73 | Juanbri02.matfisplayer1 | 1111 | 56 | 257 | 123-134 | 100% (g_iter0 5-0*) |
| 74 | NolanChai.nolan_1 | 1110 | 56 | 262 | 126-136 | 100% (g_iter0 2-0*) |
| 75 | SDainard-PDX.Team_Player | 1106 | 59 | 236 | 113-123 | 100% (g_iter0 2-0*) |
| 76 | andrewgopher.gopherbot1 | 1087 | 58 | 251 | 116-135 | 100% (g_iter0 2-0*) |
| 77 | jyorkio.elicompbot | 1074 | 57 | 246 | 118-128 | 100% (g_iter0 2-0*) |
| 78 | vontell.regressiongames | 1019 | 55 | 278 | 135-143 | 100% (g_iter0 5-0*) |
| 79 | SteamBlizzard.Block | 965 | 58 | 276 | 120-156 | 100% (g_iter0 5-0*) |
| 80 | legobridge.kushalplayer | 963 | 64 | 212 | 93-119 | 100% (g_iter0 2-0*) |
| 81 | ax-95174.MPAction | 961 | 60 | 243 | 113-130 | 100% (c_swarm1 3-0*) |
| 82 | Patela171.Battlecode2023_Robot | 954 | 59 | 260 | 118-142 | 100% (g_iter0 2-0*) |
| 83 | JackLee9355.jackPlayer | 933 | 62 | 252 | 110-142 | 100% (g_iter0 2-0*) |
| 84 | michael-tyl.hqrewrite | 889 | 62 | 247 | 116-131 | 100% (g_iter0 2-0*) |
| 85 | Chahat08.toph | 879 | 61 | 254 | 117-137 | 100% (g_iter0 2-0*) |
| 86 | nail-e.Dante | 869 | 60 | 268 | 126-142 | 100% (g_iter0 2-0*) |
| 87 | mama4294.learningBot | 851 | 64 | 244 | 109-135 | 100% (g_iter0 2-0*) |
| 88 | anicolao.submission | 824 | 60 | 301 | 136-165 | 100% (g_iter0 2-0*) |
| 89 | team-remember-to-hydrate.sprint_1 | 754 | 64 | 264 | 112-152 | 100% (g_iter0 2-0*) |
| 90 | Vinceyou1.Player1 | 686 | 66 | 256 | 110-146 | 100% (g_iter0 2-0*) |
| 91 | addiesteward.elicompbot | 656 | 66 | 284 | 125-159 | 100% (g_iter0 5-0*) |
| 92 | michael-tyl.cc_v0_5_0_6 | 628 | 64 | 331 | 141-190 | 100% (g_iter0 2-0*) |
| 93 | toyat522.bot5 | 610 | 67 | 293 | 130-163 | 100% (g_iter0 2-0*) |
| 94 | Chahat08.lazarus | 600 | 68 | 278 | 120-158 | 100% (g_iter0 2-0*) |
| 95 | monmouth-college-cs.elicompbot | 591 | 66 | 304 | 133-171 | 100% (g_iter0 2-0*) |
| 96 | Swordman51.AdeptusAstartes2 | 584 | 67 | 278 | 117-161 | 100% (g_iter0 2-0*) |
| 97 | anicolao.jumbled | 475 | 72 | 304 | 135-169 | 100% (g_iter0 5-0*) |
| 98 | ShatterXD.SRNNbot | 461 | 74 | 263 | 113-150 | 100% (g_iter0 2-0*) |
| 99 | NotLLeon.player | 255 | 88 | 262 | 115-147 | 100% (g_iter0 2-0*) |
| 100 | CodeClash-ai.mysubmission | 223 | 88 | 289 | 122-167 | 100% (g_iter0 2-0*) |
| 101 | addiesteward.NDeClaw | 185 | 93 | 270 | 110-160 | 100% (g_iter0 5-0*) |
| 102 | Yooncw0223.lec3player | -121 | 110 | 256 | 37-219 | 100% (g_iter0 5-0*) |
| 103 | andrewkbank.First | -200 | 118 | 200 | 23-177 | 100% (g_iter0 2-0*) |
