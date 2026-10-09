# Ladder

5008 games (1231 ours, 3777 between field bots on the ladder replica), 4986 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_swarm1 | 1865 +- 55 | 19 of 95 | 219 | 102-117 | 75.1% | 20.8% (vs 18) |
| g_iter0 | 1816 +- 48 | 22 of 95 | 456 | 230-226 | 72.5% | 20.0% (vs 20) |
| c_line8a | 1815 +- 73 | 23 of 95 | 139 | 47-92 | 72.4% | 19.9% (vs 20) |
| c_line6 | 1780 +- 89 | 26 of 95 | 100 | 32-68 | 70.4% | 19.8% (vs 22) |
| c_line7m | 1768 +- 90 | 28 of 95 | 100 | 31-69 | 69.7% | 20.2% (vs 23) |
| c_line5 | 1731 +- 92 | 32 of 95 | 100 | 28-72 | 67.5% | 20.9% (vs 26) |
| c_line4 | 1691 +- 95 | 36 of 95 | 100 | 25-75 | 65.0% | 20.9% (vs 29) |
| examplefuncsplayer | 1268 +- 380 | 66 of 95 | 6 | 0-6 | 36.3% | 15.1% (vs 58) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2405 | 122 | 74 | 63-11 | 0% (g_iter0 0-5*) |
| 2 | IvanGeffner.fortytwo | 2389 | 99 | 99 | 82-17 | 0% (g_iter0 0-36) |
| 3 | carlguo866.submit26_final | 2383 | 133 | 70 | 60-10 | 0% (g_iter0 0-2*) |
| 4 | awesomelemonade.finalBot | 2357 | 107 | 147 | 132-15 | 0% (g_iter0 0-15*) |
| 5 | vrangr1.AFinalsBot | 2292 | 106 | 146 | 134-12 | 7% (g_iter0 1-14*) |
| 6 | pranayagra.finalbotfinaltwo | 2236 | 98 | 97 | 72-25 | 7% (g_iter0 1-13*) |
| 7 | AnOvercookedFork.quals | 2229 | 118 | 77 | 60-17 | 20% (g_iter0 1-4*) |
| 8 | pranayagra.finalbotfinal | 2213 | 73 | 189 | 148-41 | 13% (g_iter0 6-39) |
| 9 | battlecode-archive.sprintBot | 2210 | 142 | 70 | 61-9 | 0% (g_iter0 0-2*) |
| 10 | georgezhang02.FB_ZZZ | 2146 | 104 | 77 | 53-24 | 0% (g_iter0 0-2*) |
| 11 | jmerle.camel_case_v30_final | 2125 | 74 | 171 | 132-39 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2011 | 90 | 88 | 61-27 | 0% (g_iter0 0-2*) |
| 13 | georgezhang02.CB_tuning2 | 1977 | 69 | 150 | 107-43 | 7% (g_iter0 1-14*) |
| 14 | NotLLeon.v7 | 1975 | 70 | 146 | 107-39 | 17% (g_iter0 2-10*) |
| 15 | CyrilSharma.finalBot | 1961 | 106 | 86 | 58-28 | 0% (g_iter0 0-2*) |
| 16 | GabeG888.v8o1 | 1924 | 116 | 65 | 48-17 | 0% (g_iter0 0-2*) |
| 17 | britacatalin.FinalBot | 1917 | 70 | 137 | 94-43 | 42% (g_iter0 5-7*) |
| 18 | ethanlabelle.v19 | 1882 | 96 | 78 | 52-26 | 50% (g_iter0 1-1*) |
| 19 | **us:c_swarm1** | 1865 | 55 | 219 | 102-117 |  |
| 20 | GabeG888.v8 | 1847 | 89 | 80 | 47-33 | 50% (g_iter0 1-1*) |
| 21 | VarunVejalla.karel | 1832 | 85 | 104 | 59-45 | 50% (g_iter0 4-4*) |
| 22 | **us:g_iter0** | 1816 | 48 | 456 | 230-226 |  |
| 23 | **us:c_line8a** | 1815 | 73 | 139 | 47-92 |  |
| 24 | DannyZhang686.pqual2 | 1812 | 84 | 104 | 57-47 | 29% (g_iter0 4-10*) |
| 25 | programjames.fourthbot | 1808 | 92 | 89 | 52-37 | 100% (g_iter0 2-0*) |
| 26 | **us:c_line6** | 1780 | 89 | 100 | 32-68 |  |
| 27 | NicholasKelly15.gopher10 | 1775 | 104 | 71 | 47-24 | 100% (g_iter0 2-0*) |
| 28 | **us:c_line7m** | 1768 | 90 | 100 | 31-69 |  |
| 29 | louishu17.wouisv8 | 1753 | 90 | 104 | 58-46 | 50% (g_iter0 5-5*) |
| 30 | louishu17.louisv10 | 1742 | 98 | 83 | 51-32 | 100% (g_iter0 2-0*) |
| 31 | battlecode-archive.Sprint1 | 1738 | 63 | 149 | 77-72 | 58% (g_iter0 7-5*) |
| 32 | **us:c_line5** | 1731 | 92 | 100 | 28-72 |  |
| 33 | VarunVejalla.ali8 | 1722 | 103 | 77 | 47-30 | 50% (g_iter0 1-1*) |
| 34 | reeceyang.v5anaconda | 1713 | 65 | 149 | 76-73 | 58% (g_iter0 7-5*) |
| 35 | SampleProvider.SPAARK | 1707 | 93 | 82 | 50-32 | 100% (g_iter0 2-0*) |
| 36 | **us:c_line4** | 1691 | 95 | 100 | 25-75 |  |
| 37 | ipince.bobby | 1659 | 103 | 77 | 46-31 | 100% (g_iter0 2-0*) |
| 38 | polyllc.poly | 1652 | 114 | 77 | 43-34 | 100% (g_iter0 2-0*) |
| 39 | legobridge.tacoplayer | 1650 | 88 | 106 | 58-48 | 85% (g_iter0 11-2*) |
| 40 | DukeBas._main | 1610 | 96 | 83 | 50-33 | 100% (g_iter0 2-0*) |
| 41 | toyat522.bot5a | 1599 | 88 | 92 | 45-47 | 80% (g_iter0 4-1*) |
| 42 | SteamBlizzard.newVnewME | 1588 | 87 | 95 | 44-51 | 80% (g_iter0 4-1*) |
| 43 | elgoldie.head_v5 | 1585 | 83 | 92 | 44-48 | 100% (g_iter0 2-0*) |
| 44 | beaverbois.USQualifiers | 1570 | 93 | 80 | 45-35 | 50% (g_iter0 1-1*) |
| 45 | ColtG5.rexv9 | 1569 | 93 | 88 | 43-45 | 100% (g_iter0 2-0*) |
| 46 | TheK098.qp1_7_sprint_1 | 1566 | 96 | 83 | 51-32 | 100% (g_iter0 2-0*) |
| 47 | kevinli405.maggi3_2 | 1533 | 99 | 89 | 47-42 | 100% (g_iter0 2-0*) |
| 48 | BrysonJGalapon.friday | 1519 | 87 | 89 | 46-43 | 100% (g_iter0 2-0*) |
| 49 | nail-e.Barry | 1501 | 92 | 80 | 45-35 | 100% (g_iter0 2-0*) |
| 50 | Nawlej.PoonPoon | 1457 | 97 | 83 | 41-42 | 100% (g_iter0 2-0*) |
| 51 | prisms-cs-club.prisms10 | 1440 | 95 | 86 | 40-46 | 100% (g_iter0 2-0*) |
| 52 | aj-chau.attempt1 | 1419 | 103 | 77 | 42-35 | 100% (g_iter0 5-0*) |
| 53 | yaonam.PoonPoonv4 | 1409 | 70 | 177 | 60-117 | 87% (g_iter0 13-2*) |
| 54 | ipince.bobby_v2 | 1403 | 85 | 98 | 48-50 | 100% (g_iter0 5-0*) |
| 55 | kevinli405.maggi3 | 1386 | 89 | 98 | 47-51 | 100% (g_iter0 5-0*) |
| 56 | mama4294.currentPlayer | 1374 | 100 | 80 | 40-40 | 100% (g_iter0 2-0*) |
| 57 | BrysonJGalapon.aloha | 1362 | 93 | 77 | 39-38 | 100% (g_iter0 2-0*) |
| 58 | andrewgopher.gopherbot | 1339 | 81 | 107 | 48-59 | 100% (g_iter0 2-0*) |
| 59 | bewuwy.deathbot4 | 1331 | 73 | 125 | 51-74 | 100% (g_iter0 2-0*) |
| 60 | PSUtblock.sprint_four_player | 1306 | 106 | 83 | 41-42 | 100% (g_iter0 2-0*) |
| 61 | JfeMak.realplayer2 | 1301 | 86 | 85 | 39-46 | 100% (g_iter0 2-0*) |
| 62 | SampleProvider.SPAARK_1_12_2023 | 1297 | 89 | 86 | 40-46 | 100% (g_iter0 2-0*) |
| 63 | JackLee9355.jackPlayer | 1286 | 82 | 107 | 44-63 | 100% (g_iter0 2-0*) |
| 64 | SDainard-PDX.Team_Player | 1274 | 103 | 77 | 35-42 | 100% (g_iter0 2-0*) |
| 65 | jyorkio.elicompbot | 1270 | 91 | 77 | 37-40 | 100% (g_iter0 2-0*) |
| 66 | **us:examplefuncsplayer** | 1268 | 380 | 6 | 0-6 |  |
| 67 | NolanChai.nolan_1 | 1249 | 88 | 89 | 36-53 | 100% (g_iter0 2-0*) |
| 68 | Nawlej.PoonPoonv3 | 1247 | 76 | 115 | 46-69 | 100% (g_iter0 5-0*) |
| 69 | Juanbri02.matfisplayer1 | 1240 | 83 | 101 | 44-57 | 100% (g_iter0 5-0*) |
| 70 | andrewgopher.gopherbot1 | 1239 | 83 | 107 | 43-64 | 100% (g_iter0 2-0*) |
| 71 | SteamBlizzard.Block | 1202 | 81 | 117 | 42-75 | 100% (g_iter0 5-0*) |
| 72 | vontell.regressiongames | 1186 | 76 | 104 | 45-59 | 100% (g_iter0 5-0*) |
| 73 | legobridge.kushalplayer | 1168 | 103 | 83 | 34-49 | 100% (g_iter0 2-0*) |
| 74 | ax-95174.MPAction | 1153 | 95 | 80 | 29-51 | 100% (g_iter0 2-0*) |
| 75 | anicolao.submission | 1145 | 77 | 114 | 42-72 | 100% (g_iter0 2-0*) |
| 76 | Chahat08.toph | 1143 | 79 | 103 | 41-62 | 100% (g_iter0 2-0*) |
| 77 | michael-tyl.hqrewrite | 1132 | 81 | 104 | 43-61 | 100% (g_iter0 2-0*) |
| 78 | Patela171.Battlecode2023_Robot | 1107 | 81 | 110 | 41-69 | 100% (g_iter0 2-0*) |
| 79 | nail-e.Dante | 1084 | 85 | 98 | 48-50 | 100% (g_iter0 2-0*) |
| 80 | mama4294.learningBot | 1074 | 90 | 104 | 36-68 | 100% (g_iter0 2-0*) |
| 81 | team-remember-to-hydrate.sprint_1 | 1024 | 86 | 104 | 36-68 | 100% (g_iter0 2-0*) |
| 82 | Vinceyou1.Player1 | 958 | 87 | 98 | 37-61 | 100% (g_iter0 2-0*) |
| 83 | addiesteward.elicompbot | 929 | 77 | 122 | 43-79 | 100% (g_iter0 5-0*) |
| 84 | michael-tyl.cc_v0_5_0_6 | 915 | 77 | 131 | 44-87 | 100% (g_iter0 2-0*) |
| 85 | toyat522.bot5 | 896 | 99 | 98 | 31-67 | 100% (g_iter0 2-0*) |
| 86 | Swordman51.AdeptusAstartes2 | 854 | 88 | 97 | 33-64 | 100% (g_iter0 2-0*) |
| 87 | monmouth-college-cs.elicompbot | 851 | 92 | 101 | 32-69 | 100% (g_iter0 2-0*) |
| 88 | Chahat08.lazarus | 822 | 101 | 89 | 29-60 | 100% (g_iter0 2-0*) |
| 89 | ShatterXD.SRNNbot | 749 | 90 | 101 | 35-66 | 100% (g_iter0 2-0*) |
| 90 | anicolao.jumbled | 688 | 82 | 124 | 41-83 | 100% (g_iter0 5-0*) |
| 91 | NotLLeon.player | 630 | 92 | 104 | 32-72 | 100% (g_iter0 2-0*) |
| 92 | CodeClash-ai.mysubmission | 623 | 95 | 106 | 31-75 | 100% (g_iter0 2-0*) |
| 93 | addiesteward.NDeClaw | 593 | 97 | 116 | 34-82 | 100% (g_iter0 5-0*) |
| 94 | andrewkbank.First | 380 | 119 | 86 | 11-75 | 100% (g_iter0 2-0*) |
| 95 | Yooncw0223.lec3player | 300 | 126 | 133 | 8-125 | 100% (g_iter0 5-0*) |
