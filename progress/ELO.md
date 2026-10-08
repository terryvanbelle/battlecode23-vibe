# Ladder

2677 games (730 ours, 1947 between field bots on the ladder replica), 2668 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| g_iter0 | 1810 +- 50 | 21 of 92 | 418 | 208-210 | 72.1% | 20.7% (vs 20) |
| c_line6 | 1757 +- 88 | 25 of 92 | 100 | 32-68 | 68.9% | 20.6% (vs 23) |
| c_line5 | 1710 +- 90 | 29 of 92 | 100 | 28-72 | 65.8% | 20.5% (vs 26) |
| c_line4 | 1672 +- 93 | 34 of 92 | 100 | 25-75 | 63.3% | 21.5% (vs 30) |
| examplefuncsplayer | 1297 +- 381 | 63 of 92 | 6 | 0-6 | 35.9% | 16.1% (vs 58) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | carlguo866.submit26_final | 2513 | 266 | 35 | 34-1 | 0% (g_iter0 0-2*) |
| 2 | IvanGeffner.fortytwo | 2372 | 122 | 81 | 72-9 | 0% (g_iter0 0-36) |
| 3 | battlecode-archive.sprintBot | 2356 | 273 | 41 | 40-1 | 0% (g_iter0 0-2*) |
| 4 | maxwelljones14.MPWorking | 2337 | 183 | 50 | 45-5 | 0% (g_iter0 0-5*) |
| 5 | awesomelemonade.finalBot | 2289 | 139 | 93 | 85-8 | 0% (g_iter0 0-15*) |
| 6 | AnOvercookedFork.quals | 2271 | 182 | 44 | 39-5 | 0% (g_iter0 0-2*) |
| 7 | vrangr1.AFinalsBot | 2261 | 160 | 90 | 85-5 | 7% (g_iter0 1-14*) |
| 8 | pranayagra.finalbotfinaltwo | 2222 | 121 | 79 | 64-15 | 7% (g_iter0 1-13*) |
| 9 | georgezhang02.FB_ZZZ | 2207 | 154 | 47 | 37-10 | 0% (g_iter0 0-2*) |
| 10 | pranayagra.finalbotfinal | 2177 | 86 | 138 | 107-31 | 13% (g_iter0 6-39) |
| 11 | jmerle.camel_case_v30_final | 2119 | 97 | 111 | 89-22 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2018 | 123 | 56 | 43-13 | 0% (g_iter0 0-2*) |
| 13 | GabeG888.v8o1 | 1963 | 144 | 41 | 29-12 | 0% (g_iter0 0-2*) |
| 14 | georgezhang02.CB_tuning2 | 1951 | 93 | 90 | 66-24 | 8% (g_iter0 1-11*) |
| 15 | CyrilSharma.finalBot | 1934 | 148 | 53 | 31-22 | 0% (g_iter0 0-2*) |
| 16 | NotLLeon.v7 | 1914 | 91 | 78 | 52-26 | 17% (g_iter0 2-10*) |
| 17 | britacatalin.FinalBot | 1893 | 96 | 75 | 53-22 | 42% (g_iter0 5-7*) |
| 18 | GabeG888.v8 | 1825 | 123 | 44 | 28-16 | 50% (g_iter0 1-1*) |
| 19 | programjames.fourthbot | 1819 | 163 | 44 | 28-16 | 100% (g_iter0 2-0*) |
| 20 | ethanlabelle.v19 | 1813 | 139 | 38 | 24-14 | 50% (g_iter0 1-1*) |
| 21 | **us:g_iter0** | 1810 | 50 | 418 | 208-210 |  |
| 22 | DannyZhang686.pqual2 | 1802 | 111 | 68 | 37-31 | 12% (g_iter0 1-7*) |
| 23 | VarunVejalla.karel | 1787 | 124 | 56 | 30-26 | 100% (g_iter0 2-0*) |
| 24 | VarunVejalla.ali8 | 1762 | 148 | 41 | 26-15 | 50% (g_iter0 1-1*) |
| 25 | **us:c_line6** | 1757 | 88 | 100 | 32-68 |  |
| 26 | louishu17.wouisv8 | 1756 | 141 | 52 | 37-15 | 50% (g_iter0 1-1*) |
| 27 | battlecode-archive.Sprint1 | 1722 | 86 | 87 | 49-38 | 58% (g_iter0 7-5*) |
| 28 | louishu17.louisv10 | 1711 | 137 | 38 | 22-16 | 100% (g_iter0 2-0*) |
| 29 | **us:c_line5** | 1710 | 90 | 100 | 28-72 |  |
| 30 | NicholasKelly15.gopher10 | 1707 | 147 | 41 | 26-15 | 100% (g_iter0 2-0*) |
| 31 | SampleProvider.SPAARK | 1705 | 134 | 47 | 32-15 | 100% (g_iter0 2-0*) |
| 32 | reeceyang.v5anaconda | 1702 | 87 | 81 | 43-38 | 58% (g_iter0 7-5*) |
| 33 | ipince.bobby | 1678 | 169 | 23 | 11-12 | 100% (g_iter0 2-0*) |
| 34 | **us:c_line4** | 1672 | 93 | 100 | 25-75 |  |
| 35 | polyllc.poly | 1667 | 177 | 41 | 22-19 | 100% (g_iter0 2-0*) |
| 36 | legobridge.tacoplayer | 1654 | 107 | 76 | 39-37 | 85% (g_iter0 11-2*) |
| 37 | ColtG5.rexv9 | 1654 | 130 | 44 | 27-17 | 100% (g_iter0 2-0*) |
| 38 | toyat522.bot5a | 1644 | 130 | 47 | 22-25 | 80% (g_iter0 4-1*) |
| 39 | SteamBlizzard.newVnewME | 1635 | 118 | 53 | 28-25 | 80% (g_iter0 4-1*) |
| 40 | elgoldie.head_v5 | 1599 | 108 | 56 | 24-32 | 100% (g_iter0 2-0*) |
| 41 | BrysonJGalapon.friday | 1570 | 111 | 59 | 36-23 | 100% (g_iter0 2-0*) |
| 42 | TheK098.qp1_7_sprint_1 | 1570 | 137 | 41 | 19-22 | 100% (g_iter0 2-0*) |
| 43 | beaverbois.USQualifiers | 1554 | 129 | 41 | 18-23 | 50% (g_iter0 1-1*) |
| 44 | DukeBas._main | 1547 | 155 | 38 | 17-21 | 100% (g_iter0 2-0*) |
| 45 | nail-e.Barry | 1518 | 125 | 44 | 28-16 | 100% (g_iter0 2-0*) |
| 46 | prisms-cs-club.prisms10 | 1485 | 124 | 56 | 28-28 | 100% (g_iter0 2-0*) |
| 47 | kevinli405.maggi3_2 | 1470 | 166 | 41 | 13-28 | 100% (g_iter0 2-0*) |
| 48 | kevinli405.maggi3 | 1436 | 121 | 56 | 29-27 | 100% (g_iter0 5-0*) |
| 49 | yaonam.PoonPoonv4 | 1430 | 93 | 102 | 38-64 | 87% (g_iter0 13-2*) |
| 50 | Nawlej.PoonPoon | 1417 | 133 | 41 | 18-23 | 100% (g_iter0 2-0*) |
| 51 | BrysonJGalapon.aloha | 1411 | 125 | 44 | 22-22 | 100% (g_iter0 2-0*) |
| 52 | mama4294.currentPlayer | 1406 | 144 | 38 | 19-19 | 100% (g_iter0 2-0*) |
| 53 | aj-chau.attempt1 | 1392 | 139 | 44 | 19-25 | 100% (g_iter0 5-0*) |
| 54 | andrewgopher.gopherbot | 1384 | 102 | 59 | 34-25 | 100% (g_iter0 2-0*) |
| 55 | bewuwy.deathbot4 | 1365 | 117 | 53 | 21-32 | 100% (g_iter0 2-0*) |
| 56 | JfeMak.realplayer2 | 1337 | 124 | 43 | 22-21 | 100% (g_iter0 2-0*) |
| 57 | PSUtblock.sprint_four_player | 1327 | 181 | 35 | 16-19 | 100% (g_iter0 2-0*) |
| 58 | NolanChai.nolan_1 | 1325 | 109 | 56 | 20-36 | 100% (g_iter0 2-0*) |
| 59 | SampleProvider.SPAARK_1_12_2023 | 1324 | 140 | 32 | 16-16 | 100% (g_iter0 2-0*) |
| 60 | JackLee9355.jackPlayer | 1309 | 122 | 53 | 23-30 | 100% (g_iter0 2-0*) |
| 61 | SDainard-PDX.Team_Player | 1300 | 136 | 44 | 15-29 | 100% (g_iter0 2-0*) |
| 62 | jyorkio.elicompbot | 1299 | 127 | 32 | 15-17 | 100% (g_iter0 2-0*) |
| 63 | **us:examplefuncsplayer** | 1297 | 381 | 6 | 0-6 |  |
| 64 | Nawlej.PoonPoonv3 | 1285 | 121 | 50 | 18-32 | 100% (g_iter0 2-0*) |
| 65 | ipince.bobby_v2 | 1278 | 139 | 38 | 13-25 | 100% (g_iter0 2-0*) |
| 66 | vontell.regressiongames | 1270 | 106 | 53 | 22-31 | 100% (g_iter0 5-0*) |
| 67 | anicolao.submission | 1266 | 111 | 58 | 22-36 | 100% (g_iter0 2-0*) |
| 68 | andrewgopher.gopherbot1 | 1264 | 103 | 68 | 22-46 | 100% (g_iter0 2-0*) |
| 69 | ax-95174.MPAction | 1246 | 132 | 41 | 15-26 | 100% (g_iter0 2-0*) |
| 70 | michael-tyl.hqrewrite | 1236 | 121 | 50 | 18-32 | 100% (g_iter0 2-0*) |
| 71 | SteamBlizzard.Block | 1213 | 123 | 64 | 17-47 | 100% (g_iter0 5-0*) |
| 72 | legobridge.kushalplayer | 1210 | 200 | 26 | 4-22 | 100% (g_iter0 2-0*) |
| 73 | Chahat08.toph | 1201 | 122 | 50 | 16-34 | 100% (g_iter0 2-0*) |
| 74 | Patela171.Battlecode2023_Robot | 1198 | 117 | 59 | 24-35 | 100% (g_iter0 2-0*) |
| 75 | nail-e.Dante | 1197 | 137 | 41 | 24-17 | 100% (g_iter0 2-0*) |
| 76 | Juanbri02.matfisplayer1 | 1152 | 167 | 44 | 15-29 | 100% (g_iter0 2-0*) |
| 77 | team-remember-to-hydrate.sprint_1 | 1101 | 140 | 50 | 12-38 | 100% (g_iter0 2-0*) |
| 78 | addiesteward.elicompbot | 1080 | 141 | 41 | 13-28 | 100% (g_iter0 2-0*) |
| 79 | mama4294.learningBot | 1066 | 164 | 47 | 9-38 | 100% (g_iter0 2-0*) |
| 80 | Swordman51.AdeptusAstartes2 | 1036 | 161 | 40 | 11-29 | 100% (g_iter0 2-0*) |
| 81 | toyat522.bot5 | 1035 | 171 | 44 | 6-38 | 100% (g_iter0 2-0*) |
| 82 | Vinceyou1.Player1 | 1029 | 124 | 53 | 19-34 | 100% (g_iter0 2-0*) |
| 83 | monmouth-college-cs.elicompbot | 986 | 130 | 59 | 15-44 | 100% (g_iter0 2-0*) |
| 84 | Chahat08.lazarus | 961 | 216 | 29 | 4-25 | 100% (g_iter0 2-0*) |
| 85 | michael-tyl.cc_v0_5_0_6 | 924 | 128 | 68 | 16-52 | 100% (g_iter0 2-0*) |
| 86 | ShatterXD.SRNNbot | 901 | 166 | 38 | 8-30 | 100% (g_iter0 2-0*) |
| 87 | addiesteward.NDeClaw | 730 | 163 | 59 | 8-51 | 100% (g_iter0 5-0*) |
| 88 | CodeClash-ai.mysubmission | 703 | 244 | 41 | 2-39 | 100% (g_iter0 2-0*) |
| 89 | NotLLeon.player | 692 | 258 | 29 | 1-28 | 100% (g_iter0 2-0*) |
| 90 | andrewkbank.First | 664 | 182 | 35 | 4-31 | 100% (g_iter0 2-0*) |
| 91 | anicolao.jumbled | 599 | 243 | 44 | 2-42 | 100% (g_iter0 5-0*) |
| 92 | Yooncw0223.lec3player | 563 | 200 | 62 | 3-59 | 100% (g_iter0 5-0*) |
