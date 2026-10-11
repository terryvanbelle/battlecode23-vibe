# Ladder

14769 games (3009 ours, 6 of the stock examplefuncsplayer, 11754 between field bots on the ladder replica), 14353 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 106 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2134 +- 90 | 12 of 105 | 100 | 64-36 | 87.2% | 33.5% (vs 11) |
| c_spread2 | 2102 +- 89 | 13 of 105 | 100 | 61-39 | 86.1% | 29.7% (vs 11) |
| c_scout1 | 2091 +- 89 | 14 of 105 | 100 | 60-40 | 85.7% | 28.5% (vs 11) |
| c_bc1 | 2075 +- 69 | 16 of 105 | 163 | 96-67 | 85.1% | 28.7% (vs 12) |
| c_def3 | 2071 +- 64 | 17 of 105 | 194 | 117-77 | 84.9% | 28.3% (vs 12) |
| c_flee3 | 2049 +- 88 | 18 of 105 | 100 | 56-44 | 84.1% | 25.9% (vs 12) |
| c_anc3 | 2042 +- 69 | 19 of 105 | 161 | 87-74 | 83.8% | 25.1% (vs 12) |
| c_aura2 | 2040 +- 53 | 20 of 105 | 311 | 160-151 | 83.7% | 25.0% (vs 12) |
| c_nav5 | 1983 +- 78 | 23 of 105 | 126 | 61-65 | 81.4% | 23.5% (vs 14) |
| c_nav6 | 1968 +- 77 | 25 of 105 | 129 | 58-71 | 80.8% | 23.9% (vs 15) |
| c_nav4 | 1944 +- 59 | 26 of 105 | 221 | 108-113 | 79.7% | 21.7% (vs 15) |
| c_swarm1 | 1864 +- 56 | 29 of 105 | 268 | 126-142 | 76.1% | 18.7% (vs 17) |
| c_line8a | 1821 +- 78 | 35 of 105 | 139 | 47-92 | 74.1% | 22.6% (vs 22) |
| g_iter0 | 1801 +- 55 | 36 of 105 | 455 | 230-225 | 73.1% | 20.9% (vs 22) |
| c_line6 | 1787 +- 94 | 38 of 105 | 100 | 32-68 | 72.5% | 21.1% (vs 23) |
| c_line7m | 1775 +- 95 | 40 of 105 | 100 | 31-69 | 71.9% | 21.3% (vs 24) |
| c_line5 | 1737 +- 97 | 45 of 105 | 100 | 28-72 | 70.0% | 22.3% (vs 28) |
| c_line4 | 1696 +- 100 | 47 of 105 | 100 | 25-75 | 68.0% | 20.0% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_bc1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2360 | 74 | 168 | 118-50 | 0% (g_iter0 0-5*) |
| 2 | awesomelemonade.finalBot | 2359 | 63 | 344 | 276-68 | 20% (c_bc1 2-8*) |
| 3 | IvanGeffner.fortytwo | 2353 | 73 | 180 | 124-56 | 0% (g_iter0 0-35) |
| 4 | carlguo866.submit26_final | 2323 | 71 | 185 | 124-61 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2306 | 60 | 350 | 272-78 | 30% (c_bc1 3-7*) |
| 6 | AnOvercookedFork.quals | 2238 | 67 | 202 | 131-71 | 33% (c_bc1 1-2*) |
| 7 | pranayagra.finalbotfinaltwo | 2206 | 66 | 209 | 135-74 | 29% (c_aura2 5-12*) |
| 8 | pranayagra.finalbotfinal | 2195 | 51 | 426 | 288-138 | 30% (c_bc1 3-7*) |
| 9 | georgezhang02.FB_ZZZ | 2188 | 65 | 202 | 124-78 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2164 | 67 | 199 | 126-73 | 22% (c_bc1 2-7*) |
| 11 | jmerle.camel_case_v30_final | 2151 | 50 | 411 | 278-133 | 40% (c_bc1 4-6*) |
| 12 | **us:c_well5** | 2134 | 90 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2102 | 89 | 100 | 61-39 |  |
| 14 | **us:c_scout1** | 2091 | 89 | 100 | 60-40 |  |
| 15 | CyrilSharma.finalBot | 2076 | 58 | 257 | 151-106 | 22% (c_aura2 5-18*) |
| 16 | **us:c_bc1** | 2075 | 69 | 163 | 96-67 |  |
| 17 | **us:c_def3** | 2071 | 64 | 194 | 117-77 |  |
| 18 | **us:c_flee3** | 2049 | 88 | 100 | 56-44 |  |
| 19 | **us:c_anc3** | 2042 | 69 | 161 | 87-74 |  |
| 20 | **us:c_aura2** | 2040 | 53 | 311 | 160-151 |  |
| 21 | ethanlabelle.dev | 2019 | 55 | 259 | 149-110 | 53% (c_bc1 8-7*) |
| 22 | NotLLeon.v7 | 1986 | 46 | 436 | 238-198 | 76% (c_bc1 19-6*) |
| 23 | **us:c_nav5** | 1983 | 78 | 126 | 61-65 |  |
| 24 | georgezhang02.CB_tuning2 | 1970 | 47 | 401 | 223-178 | 54% (c_bc1 7-6*) |
| 25 | **us:c_nav6** | 1968 | 77 | 129 | 58-71 |  |
| 26 | **us:c_nav4** | 1944 | 59 | 221 | 108-113 |  |
| 27 | ethanlabelle.v19 | 1923 | 57 | 240 | 136-104 | 50% (c_bc1 6-6*) |
| 28 | britacatalin.FinalBot | 1899 | 46 | 414 | 208-206 | 85% (c_bc1 11-2*) |
| 29 | **us:c_swarm1** | 1864 | 56 | 268 | 126-142 |  |
| 30 | GabeG888.v8 | 1864 | 55 | 242 | 130-112 | 89% (c_def3 16-2*) |
| 31 | programjames.fourthbot | 1846 | 58 | 230 | 127-103 | 100% (c_aura2 3-0*) |
| 32 | VarunVejalla.ali8 | 1838 | 58 | 227 | 127-100 | 50% (c_aura2 3-3*) |
| 33 | GabeG888.v8o1 | 1837 | 56 | 231 | 132-99 | 67% (c_aura2 4-2*) |
| 34 | VarunVejalla.karel | 1835 | 56 | 244 | 132-112 | 33% (c_aura2 1-2*) |
| 35 | **us:c_line8a** | 1821 | 78 | 139 | 47-92 |  |
| 36 | **us:g_iter0** | 1801 | 55 | 455 | 230-225 |  |
| 37 | DannyZhang686.pqual2 | 1801 | 55 | 260 | 141-119 | 83% (c_anc3 5-1*) |
| 38 | **us:c_line6** | 1787 | 94 | 100 | 32-68 |  |
| 39 | NicholasKelly15.gopher10 | 1781 | 60 | 210 | 118-92 | 100% (c_anc3 3-0*) |
| 40 | **us:c_line7m** | 1775 | 95 | 100 | 31-69 |  |
| 41 | louishu17.louisv10 | 1772 | 58 | 228 | 122-106 | 100% (c_bc1 3-0*) |
| 42 | reeceyang.v5anaconda | 1760 | 45 | 440 | 189-251 | 90% (c_bc1 9-1*) |
| 43 | louishu17.wouisv8 | 1758 | 58 | 245 | 132-113 | 83% (c_aura2 5-1*) |
| 44 | SampleProvider.SPAARK | 1752 | 57 | 231 | 128-103 | 33% (c_anc3 1-2*) |
| 45 | **us:c_line5** | 1737 | 97 | 100 | 28-72 |  |
| 46 | battlecode-archive.Sprint1 | 1706 | 47 | 392 | 156-236 | 90% (c_bc1 9-1*) |
| 47 | **us:c_line4** | 1696 | 100 | 100 | 25-75 |  |
| 48 | ipince.bobby | 1644 | 60 | 208 | 111-97 | 67% (c_swarm1 2-1*) |
| 49 | SteamBlizzard.newVnewME | 1596 | 53 | 264 | 134-130 | 80% (g_iter0 4-1*) |
| 50 | legobridge.tacoplayer | 1591 | 57 | 247 | 130-117 | 85% (g_iter0 11-2*) |
| 51 | TheK098.qp1_7_sprint_1 | 1569 | 55 | 251 | 138-113 | 100% (c_swarm1 6-0*) |
| 52 | polyllc.poly | 1555 | 60 | 223 | 115-108 | 100% (g_iter0 2-0*) |
| 53 | toyat522.bot5a | 1506 | 52 | 271 | 134-137 | 80% (g_iter0 4-1*) |
| 54 | elgoldie.head_v5 | 1504 | 53 | 255 | 126-129 | 100% (g_iter0 2-0*) |
| 55 | DukeBas._main | 1490 | 56 | 238 | 126-112 | 100% (g_iter0 2-0*) |
| 56 | ColtG5.rexv9 | 1489 | 53 | 259 | 131-128 | 100% (g_iter0 2-0*) |
| 57 | beaverbois.USQualifiers | 1454 | 53 | 263 | 138-125 | 50% (g_iter0 1-1*) |
| 58 | Nawlej.PoonPoon | 1415 | 56 | 251 | 123-128 | 100% (g_iter0 2-0*) |
| 59 | kevinli405.maggi3_2 | 1408 | 52 | 291 | 145-146 | 100% (g_iter0 2-0*) |
| 60 | BrysonJGalapon.friday | 1373 | 53 | 254 | 130-124 | 100% (g_iter0 2-0*) |
| 61 | yaonam.PoonPoonv4 | 1372 | 48 | 471 | 168-303 | 90% (c_bc1 9-1*) |
| 62 | nail-e.Barry | 1358 | 52 | 270 | 135-135 | 100% (g_iter0 2-0*) |
| 63 | aj-chau.attempt1 | 1353 | 53 | 274 | 142-132 | 100% (g_iter0 5-0*) |
| 64 | kevinli405.maggi3 | 1346 | 54 | 267 | 136-131 | 100% (g_iter0 5-0*) |
| 65 | prisms-cs-club.prisms10 | 1303 | 54 | 263 | 129-134 | 100% (g_iter0 2-0*) |
| 66 | mama4294.currentPlayer | 1292 | 53 | 276 | 140-136 | 100% (g_iter0 2-0*) |
| 67 | ipince.bobby_v2 | 1263 | 51 | 305 | 150-155 | 67% (c_swarm1 2-1*) |
| 68 | bewuwy.deathbot4 | 1180 | 50 | 323 | 154-169 | 100% (g_iter0 2-0*) |
| 69 | andrewgopher.gopherbot | 1179 | 52 | 308 | 150-158 | 100% (g_iter0 2-0*) |
| 70 | JfeMak.realplayer2 | 1177 | 52 | 290 | 141-149 | 100% (g_iter0 2-0*) |
| 71 | BrysonJGalapon.aloha | 1172 | 50 | 314 | 155-159 | 100% (c_swarm1 3-0*) |
| 72 | PSUtblock.sprint_four_player | 1136 | 53 | 299 | 147-152 | 100% (g_iter0 2-0*) |
| 73 | SampleProvider.SPAARK_1_12_2023 | 1096 | 51 | 329 | 157-172 | 100% (c_swarm1 3-0*) |
| 74 | Nawlej.PoonPoonv3 | 1074 | 52 | 319 | 153-166 | 100% (g_iter0 5-0*) |
| 75 | NolanChai.nolan_1 | 1070 | 50 | 339 | 164-175 | 100% (g_iter0 2-0*) |
| 76 | SDainard-PDX.Team_Player | 1067 | 54 | 288 | 141-147 | 100% (g_iter0 2-0*) |
| 77 | Juanbri02.matfisplayer1 | 1061 | 51 | 324 | 155-169 | 100% (g_iter0 5-0*) |
| 78 | andrewgopher.gopherbot1 | 1055 | 53 | 306 | 140-166 | 100% (g_iter0 2-0*) |
| 79 | jyorkio.elicompbot | 1035 | 52 | 309 | 152-157 | 100% (g_iter0 2-0*) |
| 80 | vontell.regressiongames | 968 | 51 | 343 | 168-175 | 100% (g_iter0 5-0*) |
| 81 | legobridge.kushalplayer | 945 | 57 | 281 | 130-151 | 100% (g_iter0 2-0*) |
| 82 | Patela171.Battlecode2023_Robot | 917 | 55 | 312 | 144-168 | 100% (g_iter0 2-0*) |
| 83 | SteamBlizzard.Block | 916 | 54 | 342 | 155-187 | 100% (g_iter0 5-0*) |
| 84 | ax-95174.MPAction | 887 | 56 | 304 | 142-162 | 100% (c_swarm1 3-0*) |
| 85 | JackLee9355.jackPlayer | 836 | 59 | 310 | 141-169 | 100% (g_iter0 2-0*) |
| 86 | nail-e.Dante | 820 | 55 | 341 | 165-176 | 100% (g_iter0 2-0*) |
| 87 | Chahat08.toph | 817 | 56 | 315 | 146-169 | 100% (g_iter0 2-0*) |
| 88 | michael-tyl.hqrewrite | 800 | 57 | 317 | 147-170 | 100% (g_iter0 2-0*) |
| 89 | mama4294.learningBot | 794 | 58 | 319 | 144-175 | 100% (g_iter0 2-0*) |
| 90 | anicolao.submission | 749 | 56 | 367 | 167-200 | 100% (g_iter0 2-0*) |
| 91 | team-remember-to-hydrate.sprint_1 | 703 | 59 | 327 | 143-184 | 100% (g_iter0 2-0*) |
| 92 | toyat522.bot5 | 608 | 61 | 363 | 166-197 | 100% (g_iter0 2-0*) |
| 93 | Vinceyou1.Player1 | 607 | 62 | 310 | 133-177 | 100% (g_iter0 2-0*) |
| 94 | addiesteward.elicompbot | 600 | 61 | 338 | 147-191 | 100% (g_iter0 5-0*) |
| 95 | michael-tyl.cc_v0_5_0_6 | 584 | 60 | 378 | 164-214 | 100% (g_iter0 2-0*) |
| 96 | Chahat08.lazarus | 555 | 62 | 343 | 152-191 | 100% (g_iter0 2-0*) |
| 97 | Swordman51.AdeptusAstartes2 | 550 | 63 | 333 | 149-184 | 100% (g_iter0 2-0*) |
| 98 | monmouth-college-cs.elicompbot | 549 | 62 | 363 | 160-203 | 100% (g_iter0 2-0*) |
| 99 | anicolao.jumbled | 440 | 66 | 357 | 162-195 | 100% (g_iter0 5-0*) |
| 100 | ShatterXD.SRNNbot | 422 | 68 | 322 | 147-175 | 100% (g_iter0 2-0*) |
| 101 | NotLLeon.player | 216 | 82 | 315 | 144-171 | 100% (g_iter0 2-0*) |
| 102 | CodeClash-ai.mysubmission | 143 | 83 | 361 | 151-210 | 100% (g_iter0 2-0*) |
| 103 | addiesteward.NDeClaw | 126 | 87 | 322 | 137-185 | 100% (g_iter0 5-0*) |
| 104 | Yooncw0223.lec3player | -192 | 102 | 304 | 46-258 | 100% (g_iter0 5-0*) |
| 105 | andrewkbank.First | -252 | 108 | 234 | 31-203 | 100% (g_iter0 2-0*) |
