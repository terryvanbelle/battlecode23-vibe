# Ladder

874 games (325 ours, 549 between field bots on the ladder replica), 874 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| g_iter0 | 1782 +- 52 | 18 of 89 | 319 | 178-141 | 72.6% | 19.5% (vs 17) |
| examplefuncsplayer | 1303 +- 377 | 67 of 89 | 6 | 0-6 | 32.3% | 20.0% (vs 65) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2207 | 168 | 41 | 37-4 | 0% (g_iter0 0-20*) |
| 2 | ethanlabelle.dev | 2204 | 365 | 14 | 14-0 | 0% (g_iter0 0-2*) |
| 3 | georgezhang02.FB_ZZZ | 2195 | 366 | 11 | 11-0 | 0% (g_iter0 0-2*) |
| 4 | awesomelemonade.finalBot | 2151 | 253 | 27 | 26-1 | 0% (g_iter0 0-12*) |
| 5 | vrangr1.AFinalsBot | 2128 | 255 | 24 | 23-1 | 7% (g_iter0 1-14*) |
| 6 | carlguo866.submit26_final | 2127 | 355 | 17 | 17-0 | 0% (g_iter0 0-2*) |
| 7 | CyrilSharma.finalBot | 2102 | 293 | 17 | 16-1 | 0% (g_iter0 0-2*) |
| 8 | pranayagra.finalbotfinal | 2065 | 134 | 51 | 42-9 | 19% (g_iter0 4-17*) |
| 9 | battlecode-archive.sprintBot | 2021 | 364 | 11 | 11-0 | 0% (g_iter0 0-2*) |
| 10 | jmerle.camel_case_v30_final | 2012 | 188 | 27 | 24-3 | 8% (g_iter0 1-11*) |
| 11 | GabeG888.v8o1 | 2001 | 229 | 14 | 9-5 | 0% (g_iter0 0-2*) |
| 12 | pranayagra.finalbotfinaltwo | 1979 | 206 | 29 | 24-5 | 0% (g_iter0 0-2*) |
| 13 | maxwelljones14.MPWorking | 1973 | 370 | 11 | 11-0 | 0% (g_iter0 0-2*) |
| 14 | NotLLeon.v7 | 1948 | 178 | 18 | 14-4 | 17% (g_iter0 2-10*) |
| 15 | georgezhang02.CB_tuning2 | 1942 | 171 | 27 | 19-8 | 8% (g_iter0 1-11*) |
| 16 | AnOvercookedFork.quals | 1940 | 379 | 8 | 8-0 | 0% (g_iter0 0-2*) |
| 17 | britacatalin.FinalBot | 1821 | 168 | 18 | 12-6 | 42% (g_iter0 5-7*) |
| 18 | **us:g_iter0** | 1782 | 52 | 319 | 178-141 |  |
| 19 | GabeG888.v8 | 1778 | 207 | 14 | 8-6 | 50% (g_iter0 1-1*) |
| 20 | battlecode-archive.Sprint1 | 1764 | 153 | 36 | 21-15 | 58% (g_iter0 7-5*) |
| 21 | ethanlabelle.v19 | 1750 | 236 | 8 | 5-3 | 50% (g_iter0 1-1*) |
| 22 | DannyZhang686.pqual2 | 1741 | 160 | 32 | 18-14 | 0% (g_iter0 0-2*) |
| 23 | reeceyang.v5anaconda | 1732 | 159 | 24 | 12-12 | 58% (g_iter0 7-5*) |
| 24 | SampleProvider.SPAARK | 1725 | 222 | 17 | 12-5 | 100% (g_iter0 2-0*) |
| 25 | toyat522.bot5a | 1707 | 207 | 14 | 8-6 | 80% (g_iter0 4-1*) |
| 26 | polyllc.poly | 1705 | 203 | 20 | 10-10 | 100% (g_iter0 2-0*) |
| 27 | VarunVejalla.karel | 1649 | 211 | 14 | 6-8 | 100% (g_iter0 2-0*) |
| 28 | VarunVejalla.ali8 | 1644 | 204 | 17 | 11-6 | 50% (g_iter0 1-1*) |
| 29 | TheK098.qp1_7_sprint_1 | 1626 | 206 | 17 | 11-6 | 100% (g_iter0 2-0*) |
| 30 | BrysonJGalapon.friday | 1610 | 210 | 11 | 7-4 | 100% (g_iter0 2-0*) |
| 31 | legobridge.tacoplayer | 1602 | 164 | 26 | 11-15 | 100% (g_iter0 2-0*) |
| 32 | ColtG5.rexv9 | 1591 | 239 | 11 | 5-6 | 100% (g_iter0 2-0*) |
| 33 | DukeBas._main | 1564 | 215 | 14 | 10-4 | 100% (g_iter0 2-0*) |
| 34 | beaverbois.USQualifiers | 1560 | 186 | 20 | 9-11 | 50% (g_iter0 1-1*) |
| 35 | ipince.bobby | 1553 | 244 | 11 | 3-8 | 100% (g_iter0 2-0*) |
| 36 | bewuwy.deathbot4 | 1551 | 181 | 20 | 9-11 | 100% (g_iter0 2-0*) |
| 37 | andrewgopher.gopherbot1 | 1551 | 221 | 11 | 6-5 | 100% (g_iter0 2-0*) |
| 38 | NicholasKelly15.gopher10 | 1546 | 298 | 8 | 6-2 | 100% (g_iter0 2-0*) |
| 39 | louishu17.wouisv8 | 1542 | 274 | 8 | 3-5 | 50% (g_iter0 1-1*) |
| 40 | louishu17.louisv10 | 1539 | 209 | 17 | 7-10 | 100% (g_iter0 2-0*) |
| 41 | programjames.fourthbot | 1510 | 323 | 5 | 3-2 | 100% (g_iter0 2-0*) |
| 42 | SteamBlizzard.newVnewME | 1491 | 170 | 23 | 8-15 | 80% (g_iter0 4-1*) |
| 43 | yaonam.PoonPoonv4 | 1488 | 174 | 27 | 6-21 | 87% (g_iter0 13-2*) |
| 44 | andrewgopher.gopherbot | 1485 | 186 | 17 | 10-7 | 100% (g_iter0 2-0*) |
| 45 | kevinli405.maggi3_2 | 1484 | 202 | 17 | 9-8 | 100% (g_iter0 2-0*) |
| 46 | BrysonJGalapon.aloha | 1449 | 224 | 11 | 5-6 | 100% (g_iter0 2-0*) |
| 47 | NolanChai.nolan_1 | 1443 | 178 | 20 | 9-11 | 100% (g_iter0 2-0*) |
| 48 | vontell.regressiongames | 1434 | 186 | 17 | 9-8 | 100% (g_iter0 5-0*) |
| 49 | Swordman51.AdeptusAstartes2 | 1421 | 415 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 50 | Nawlej.PoonPoonv3 | 1409 | 407 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 51 | kevinli405.maggi3 | 1406 | 227 | 11 | 5-6 | 100% (g_iter0 2-0*) |
| 52 | SDainard-PDX.Team_Player | 1401 | 183 | 20 | 8-12 | 100% (g_iter0 2-0*) |
| 53 | JackLee9355.jackPlayer | 1399 | 168 | 20 | 6-14 | 100% (g_iter0 2-0*) |
| 54 | aj-chau.attempt1 | 1378 | 225 | 14 | 7-7 | 100% (g_iter0 5-0*) |
| 55 | prisms-cs-club.prisms10 | 1368 | 286 | 17 | 3-14 | 100% (g_iter0 2-0*) |
| 56 | anicolao.submission | 1364 | 180 | 20 | 8-12 | 100% (g_iter0 2-0*) |
| 57 | nail-e.Dante | 1353 | 198 | 17 | 9-8 | 100% (g_iter0 2-0*) |
| 58 | elgoldie.head_v5 | 1352 | 382 | 11 | 0-11 | 100% (g_iter0 2-0*) |
| 59 | ipince.bobby_v2 | 1352 | 204 | 11 | 4-7 | 100% (g_iter0 2-0*) |
| 60 | mama4294.learningBot | 1343 | 274 | 8 | 1-7 | 100% (g_iter0 2-0*) |
| 61 | Juanbri02.matfisplayer1 | 1340 | 381 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 62 | SteamBlizzard.Block | 1339 | 140 | 32 | 8-24 | 100% (g_iter0 2-0*) |
| 63 | michael-tyl.hqrewrite | 1321 | 152 | 29 | 11-18 | 100% (g_iter0 2-0*) |
| 64 | mama4294.currentPlayer | 1319 | 245 | 11 | 2-9 | 100% (g_iter0 2-0*) |
| 65 | jyorkio.elicompbot | 1318 | 305 | 5 | 1-4 | 100% (g_iter0 2-0*) |
| 66 | PSUtblock.sprint_four_player | 1303 | 238 | 14 | 4-10 | 100% (g_iter0 2-0*) |
| 67 | **us:examplefuncsplayer** | 1303 | 377 | 6 | 0-6 |  |
| 68 | ax-95174.MPAction | 1299 | 222 | 17 | 5-12 | 100% (g_iter0 2-0*) |
| 69 | nail-e.Barry | 1296 | 236 | 11 | 4-7 | 100% (g_iter0 2-0*) |
| 70 | ShatterXD.SRNNbot | 1295 | 272 | 14 | 3-11 | 100% (g_iter0 2-0*) |
| 71 | addiesteward.elicompbot | 1279 | 241 | 11 | 2-9 | 100% (g_iter0 2-0*) |
| 72 | SampleProvider.SPAARK_1_12_2023 | 1267 | 374 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 73 | Patela171.Battlecode2023_Robot | 1249 | 197 | 20 | 5-15 | 100% (g_iter0 2-0*) |
| 74 | team-remember-to-hydrate.sprint_1 | 1235 | 238 | 17 | 3-14 | 100% (g_iter0 2-0*) |
| 75 | toyat522.bot5 | 1232 | 205 | 20 | 3-17 | 100% (g_iter0 2-0*) |
| 76 | legobridge.kushalplayer | 1231 | 374 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 77 | JfeMak.realplayer2 | 1226 | 249 | 14 | 3-11 | 100% (g_iter0 2-0*) |
| 78 | Chahat08.toph | 1192 | 277 | 14 | 1-13 | 100% (g_iter0 2-0*) |
| 79 | Nawlej.PoonPoon | 1170 | 362 | 8 | 0-8 | 100% (g_iter0 2-0*) |
| 80 | michael-tyl.cc_v0_5_0_6 | 1155 | 248 | 14 | 3-11 | 100% (g_iter0 2-0*) |
| 81 | Vinceyou1.Player1 | 1148 | 226 | 20 | 4-16 | 100% (g_iter0 2-0*) |
| 82 | CodeClash-ai.mysubmission | 1115 | 356 | 11 | 0-11 | 100% (g_iter0 2-0*) |
| 83 | Chahat08.lazarus | 1062 | 388 | 8 | 0-8 | 100% (g_iter0 2-0*) |
| 84 | monmouth-college-cs.elicompbot | 1024 | 214 | 23 | 2-21 | 100% (g_iter0 2-0*) |
| 85 | addiesteward.NDeClaw | 1024 | 225 | 20 | 5-15 | 100% (g_iter0 2-0*) |
| 86 | NotLLeon.player | 1022 | 366 | 8 | 0-8 | 100% (g_iter0 2-0*) |
| 87 | andrewkbank.First | 987 | 361 | 11 | 0-11 | 100% (g_iter0 2-0*) |
| 88 | anicolao.jumbled | 942 | 375 | 11 | 0-11 | 100% (g_iter0 2-0*) |
| 89 | Yooncw0223.lec3player | 822 | 269 | 17 | 1-16 | 100% (g_iter0 2-0*) |
