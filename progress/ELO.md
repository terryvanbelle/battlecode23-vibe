# Ladder

14382 games (2997 ours, 6 of the stock examplefuncsplayer, 11379 between field bots on the ladder replica), 13991 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 106 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2127 +- 90 | 12 of 105 | 100 | 64-36 | 87.2% | 33.6% (vs 11) |
| c_spread2 | 2095 +- 89 | 13 of 105 | 100 | 61-39 | 86.0% | 29.8% (vs 11) |
| c_scout1 | 2085 +- 89 | 14 of 105 | 100 | 60-40 | 85.6% | 28.6% (vs 11) |
| c_def3 | 2066 +- 64 | 16 of 105 | 194 | 117-77 | 84.9% | 28.5% (vs 12) |
| c_bc1 | 2063 +- 71 | 17 of 105 | 151 | 87-64 | 84.8% | 28.1% (vs 12) |
| c_flee3 | 2043 +- 88 | 18 of 105 | 100 | 56-44 | 84.0% | 26.0% (vs 12) |
| c_anc3 | 2036 +- 69 | 19 of 105 | 161 | 87-74 | 83.7% | 25.2% (vs 12) |
| c_aura2 | 2035 +- 53 | 20 of 105 | 311 | 160-151 | 83.7% | 25.1% (vs 12) |
| c_nav5 | 1978 +- 78 | 23 of 105 | 126 | 61-65 | 81.3% | 23.6% (vs 14) |
| c_nav6 | 1962 +- 77 | 25 of 105 | 129 | 58-71 | 80.7% | 24.0% (vs 15) |
| c_nav4 | 1939 +- 59 | 26 of 105 | 221 | 108-113 | 79.6% | 21.8% (vs 15) |
| c_swarm1 | 1859 +- 56 | 30 of 105 | 268 | 126-142 | 76.0% | 20.4% (vs 18) |
| c_line8a | 1816 +- 78 | 35 of 105 | 139 | 47-92 | 74.0% | 22.6% (vs 22) |
| g_iter0 | 1798 +- 55 | 36 of 105 | 455 | 230-225 | 73.1% | 21.1% (vs 22) |
| c_line6 | 1782 +- 94 | 38 of 105 | 100 | 32-68 | 72.3% | 21.0% (vs 23) |
| c_line7m | 1769 +- 95 | 41 of 105 | 100 | 31-69 | 71.7% | 22.3% (vs 25) |
| c_line5 | 1731 +- 97 | 45 of 105 | 100 | 28-72 | 69.8% | 22.2% (vs 28) |
| c_line4 | 1690 +- 100 | 47 of 105 | 100 | 25-75 | 67.7% | 19.9% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_bc1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2366 | 76 | 169 | 122-47 | 0% (g_iter0 0-35) |
| 2 | awesomelemonade.finalBot | 2357 | 64 | 332 | 270-62 | 20% (c_bc1 2-8*) |
| 3 | maxwelljones14.MPWorking | 2343 | 76 | 157 | 108-49 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2307 | 73 | 173 | 116-57 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2289 | 60 | 341 | 265-76 | 30% (c_bc1 3-7*) |
| 6 | AnOvercookedFork.quals | 2224 | 69 | 190 | 121-69 | 33% (c_bc1 1-2*) |
| 7 | pranayagra.finalbotfinaltwo | 2200 | 67 | 202 | 131-71 | 29% (c_aura2 5-12*) |
| 8 | pranayagra.finalbotfinal | 2192 | 51 | 417 | 286-131 | 30% (c_bc1 3-7*) |
| 9 | georgezhang02.FB_ZZZ | 2188 | 66 | 191 | 121-70 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2159 | 69 | 190 | 121-69 | 17% (c_bc1 1-5*) |
| 11 | jmerle.camel_case_v30_final | 2143 | 51 | 405 | 275-130 | 40% (c_bc1 4-6*) |
| 12 | **us:c_well5** | 2127 | 90 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2095 | 89 | 100 | 61-39 |  |
| 14 | **us:c_scout1** | 2085 | 89 | 100 | 60-40 |  |
| 15 | CyrilSharma.finalBot | 2068 | 59 | 249 | 147-102 | 22% (c_aura2 5-18*) |
| 16 | **us:c_def3** | 2066 | 64 | 194 | 117-77 |  |
| 17 | **us:c_bc1** | 2063 | 71 | 151 | 87-64 |  |
| 18 | **us:c_flee3** | 2043 | 88 | 100 | 56-44 |  |
| 19 | **us:c_anc3** | 2036 | 69 | 161 | 87-74 |  |
| 20 | **us:c_aura2** | 2035 | 53 | 311 | 160-151 |  |
| 21 | ethanlabelle.dev | 2017 | 56 | 250 | 146-104 | 53% (c_bc1 8-7*) |
| 22 | NotLLeon.v7 | 1980 | 47 | 424 | 233-191 | 76% (c_bc1 19-6*) |
| 23 | **us:c_nav5** | 1978 | 78 | 126 | 61-65 |  |
| 24 | georgezhang02.CB_tuning2 | 1968 | 48 | 395 | 221-174 | 50% (c_bc1 5-5*) |
| 25 | **us:c_nav6** | 1962 | 77 | 129 | 58-71 |  |
| 26 | **us:c_nav4** | 1939 | 59 | 221 | 108-113 |  |
| 27 | ethanlabelle.v19 | 1917 | 58 | 228 | 131-97 | 50% (c_bc1 6-6*) |
| 28 | britacatalin.FinalBot | 1894 | 47 | 405 | 203-202 | 80% (c_bc1 8-2*) |
| 29 | GabeG888.v8 | 1865 | 56 | 230 | 123-107 | 89% (c_def3 16-2*) |
| 30 | **us:c_swarm1** | 1859 | 56 | 268 | 126-142 |  |
| 31 | GabeG888.v8o1 | 1836 | 57 | 225 | 129-96 | 67% (c_aura2 4-2*) |
| 32 | programjames.fourthbot | 1835 | 59 | 221 | 119-102 | 100% (c_aura2 3-0*) |
| 33 | VarunVejalla.ali8 | 1833 | 59 | 219 | 122-97 | 50% (c_aura2 3-3*) |
| 34 | VarunVejalla.karel | 1832 | 57 | 232 | 127-105 | 33% (c_aura2 1-2*) |
| 35 | **us:c_line8a** | 1816 | 78 | 139 | 47-92 |  |
| 36 | **us:g_iter0** | 1798 | 55 | 455 | 230-225 |  |
| 37 | DannyZhang686.pqual2 | 1798 | 55 | 252 | 135-117 | 83% (c_anc3 5-1*) |
| 38 | **us:c_line6** | 1782 | 94 | 100 | 32-68 |  |
| 39 | NicholasKelly15.gopher10 | 1776 | 60 | 205 | 115-90 | 100% (c_anc3 3-0*) |
| 40 | louishu17.louisv10 | 1774 | 59 | 216 | 119-97 | 100% (c_nav4 6-0*) |
| 41 | **us:c_line7m** | 1769 | 95 | 100 | 31-69 |  |
| 42 | louishu17.wouisv8 | 1757 | 58 | 239 | 130-109 | 83% (c_aura2 5-1*) |
| 43 | reeceyang.v5anaconda | 1754 | 46 | 429 | 183-246 | 90% (c_bc1 9-1*) |
| 44 | SampleProvider.SPAARK | 1752 | 58 | 222 | 125-97 | 33% (c_anc3 1-2*) |
| 45 | **us:c_line5** | 1731 | 97 | 100 | 28-72 |  |
| 46 | battlecode-archive.Sprint1 | 1701 | 48 | 389 | 153-236 | 90% (c_bc1 9-1*) |
| 47 | **us:c_line4** | 1690 | 100 | 100 | 25-75 |  |
| 48 | ipince.bobby | 1652 | 61 | 200 | 108-92 | 67% (c_swarm1 2-1*) |
| 49 | legobridge.tacoplayer | 1595 | 57 | 242 | 129-113 | 85% (g_iter0 11-2*) |
| 50 | SteamBlizzard.newVnewME | 1589 | 54 | 258 | 129-129 | 80% (g_iter0 4-1*) |
| 51 | TheK098.qp1_7_sprint_1 | 1565 | 56 | 242 | 131-111 | 100% (c_swarm1 6-0*) |
| 52 | polyllc.poly | 1559 | 61 | 214 | 112-102 | 100% (g_iter0 2-0*) |
| 53 | toyat522.bot5a | 1511 | 53 | 265 | 132-133 | 80% (g_iter0 4-1*) |
| 54 | elgoldie.head_v5 | 1504 | 54 | 246 | 121-125 | 100% (g_iter0 2-0*) |
| 55 | DukeBas._main | 1491 | 57 | 229 | 121-108 | 100% (g_iter0 2-0*) |
| 56 | ColtG5.rexv9 | 1488 | 54 | 256 | 129-127 | 100% (g_iter0 2-0*) |
| 57 | beaverbois.USQualifiers | 1454 | 54 | 254 | 131-123 | 50% (g_iter0 1-1*) |
| 58 | Nawlej.PoonPoon | 1421 | 56 | 239 | 123-116 | 100% (g_iter0 2-0*) |
| 59 | kevinli405.maggi3_2 | 1409 | 52 | 282 | 141-141 | 100% (g_iter0 2-0*) |
| 60 | BrysonJGalapon.friday | 1371 | 53 | 249 | 127-122 | 100% (g_iter0 2-0*) |
| 61 | yaonam.PoonPoonv4 | 1370 | 48 | 459 | 159-300 | 90% (c_bc1 9-1*) |
| 62 | nail-e.Barry | 1366 | 53 | 262 | 134-128 | 100% (g_iter0 2-0*) |
| 63 | aj-chau.attempt1 | 1357 | 54 | 262 | 134-128 | 100% (g_iter0 5-0*) |
| 64 | kevinli405.maggi3 | 1342 | 55 | 261 | 131-130 | 100% (g_iter0 5-0*) |
| 65 | prisms-cs-club.prisms10 | 1306 | 55 | 254 | 123-131 | 100% (g_iter0 2-0*) |
| 66 | mama4294.currentPlayer | 1289 | 53 | 270 | 134-136 | 100% (g_iter0 2-0*) |
| 67 | ipince.bobby_v2 | 1268 | 52 | 293 | 146-147 | 67% (c_swarm1 2-1*) |
| 68 | bewuwy.deathbot4 | 1189 | 51 | 314 | 152-162 | 100% (g_iter0 2-0*) |
| 69 | JfeMak.realplayer2 | 1187 | 53 | 278 | 139-139 | 100% (g_iter0 2-0*) |
| 70 | andrewgopher.gopherbot | 1187 | 52 | 299 | 146-153 | 100% (g_iter0 2-0*) |
| 71 | BrysonJGalapon.aloha | 1179 | 51 | 305 | 152-153 | 100% (c_swarm1 3-0*) |
| 72 | PSUtblock.sprint_four_player | 1144 | 54 | 290 | 145-145 | 100% (g_iter0 2-0*) |
| 73 | SampleProvider.SPAARK_1_12_2023 | 1106 | 51 | 320 | 154-166 | 100% (c_swarm1 3-0*) |
| 74 | Nawlej.PoonPoonv3 | 1080 | 52 | 315 | 150-165 | 100% (g_iter0 5-0*) |
| 75 | SDainard-PDX.Team_Player | 1073 | 55 | 282 | 138-144 | 100% (g_iter0 2-0*) |
| 76 | NolanChai.nolan_1 | 1072 | 51 | 332 | 158-174 | 100% (g_iter0 2-0*) |
| 77 | Juanbri02.matfisplayer1 | 1067 | 52 | 320 | 152-168 | 100% (g_iter0 5-0*) |
| 78 | andrewgopher.gopherbot1 | 1064 | 54 | 300 | 138-162 | 100% (g_iter0 2-0*) |
| 79 | jyorkio.elicompbot | 1040 | 53 | 298 | 147-151 | 100% (g_iter0 2-0*) |
| 80 | vontell.regressiongames | 976 | 52 | 334 | 164-170 | 100% (g_iter0 5-0*) |
| 81 | legobridge.kushalplayer | 949 | 58 | 272 | 125-147 | 100% (g_iter0 2-0*) |
| 82 | Patela171.Battlecode2023_Robot | 925 | 55 | 303 | 140-163 | 100% (g_iter0 2-0*) |
| 83 | SteamBlizzard.Block | 921 | 54 | 333 | 149-184 | 100% (g_iter0 5-0*) |
| 84 | ax-95174.MPAction | 898 | 56 | 297 | 139-158 | 100% (c_swarm1 3-0*) |
| 85 | JackLee9355.jackPlayer | 846 | 59 | 298 | 133-165 | 100% (g_iter0 2-0*) |
| 86 | Chahat08.toph | 827 | 57 | 309 | 143-166 | 100% (g_iter0 2-0*) |
| 87 | nail-e.Dante | 823 | 56 | 329 | 155-174 | 100% (g_iter0 2-0*) |
| 88 | michael-tyl.hqrewrite | 813 | 57 | 309 | 145-164 | 100% (g_iter0 2-0*) |
| 89 | mama4294.learningBot | 805 | 58 | 310 | 141-169 | 100% (g_iter0 2-0*) |
| 90 | anicolao.submission | 759 | 57 | 359 | 164-195 | 100% (g_iter0 2-0*) |
| 91 | team-remember-to-hydrate.sprint_1 | 710 | 60 | 315 | 139-176 | 100% (g_iter0 2-0*) |
| 92 | Vinceyou1.Player1 | 625 | 62 | 304 | 133-171 | 100% (g_iter0 2-0*) |
| 93 | addiesteward.elicompbot | 610 | 62 | 332 | 145-187 | 100% (g_iter0 5-0*) |
| 94 | toyat522.bot5 | 606 | 61 | 353 | 159-194 | 100% (g_iter0 2-0*) |
| 95 | michael-tyl.cc_v0_5_0_6 | 586 | 61 | 367 | 159-208 | 100% (g_iter0 2-0*) |
| 96 | Chahat08.lazarus | 563 | 63 | 338 | 152-186 | 100% (g_iter0 2-0*) |
| 97 | Swordman51.AdeptusAstartes2 | 554 | 63 | 327 | 146-181 | 100% (g_iter0 2-0*) |
| 98 | monmouth-college-cs.elicompbot | 553 | 62 | 359 | 158-201 | 100% (g_iter0 2-0*) |
| 99 | anicolao.jumbled | 434 | 67 | 352 | 157-195 | 100% (g_iter0 5-0*) |
| 100 | ShatterXD.SRNNbot | 423 | 69 | 315 | 140-175 | 100% (g_iter0 2-0*) |
| 101 | NotLLeon.player | 218 | 82 | 314 | 143-171 | 100% (g_iter0 2-0*) |
| 102 | CodeClash-ai.mysubmission | 147 | 83 | 358 | 149-209 | 100% (g_iter0 2-0*) |
| 103 | addiesteward.NDeClaw | 132 | 87 | 316 | 135-181 | 100% (g_iter0 5-0*) |
| 104 | Yooncw0223.lec3player | -186 | 102 | 301 | 46-255 | 100% (g_iter0 5-0*) |
| 105 | andrewkbank.First | -244 | 109 | 230 | 31-199 | 100% (g_iter0 2-0*) |
