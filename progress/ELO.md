# Ladder

3835 games (1111 ours, 2724 between field bots on the ladder replica), 3823 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_swarm1 | 1845 +- 85 | 20 of 95 | 103 | 42-61 | 74.2% | 20.7% (vs 19) |
| g_iter0 | 1806 +- 48 | 21 of 95 | 456 | 230-226 | 72.1% | 17.7% (vs 19) |
| c_line8a | 1799 +- 73 | 23 of 95 | 139 | 47-92 | 71.7% | 18.8% (vs 20) |
| c_line6 | 1762 +- 89 | 27 of 95 | 100 | 32-68 | 69.5% | 20.3% (vs 23) |
| c_line7m | 1750 +- 90 | 29 of 95 | 100 | 31-69 | 68.8% | 20.6% (vs 24) |
| c_line5 | 1713 +- 92 | 33 of 95 | 100 | 28-72 | 66.5% | 21.2% (vs 27) |
| c_line4 | 1674 +- 95 | 37 of 95 | 100 | 25-75 | 64.1% | 21.1% (vs 30) |
| examplefuncsplayer | 1286 +- 380 | 65 of 95 | 6 | 0-6 | 37.0% | 15.7% (vs 57) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | carlguo866.submit26_final | 2396 | 156 | 61 | 55-6 | 0% (g_iter0 0-2*) |
| 2 | battlecode-archive.sprintBot | 2387 | 272 | 59 | 58-1 | 0% (g_iter0 0-2*) |
| 3 | IvanGeffner.fortytwo | 2382 | 108 | 90 | 77-13 | 0% (g_iter0 0-36) |
| 4 | awesomelemonade.finalBot | 2372 | 124 | 138 | 128-10 | 0% (g_iter0 0-15*) |
| 5 | maxwelljones14.MPWorking | 2310 | 131 | 65 | 54-11 | 0% (g_iter0 0-5*) |
| 6 | vrangr1.AFinalsBot | 2291 | 130 | 129 | 121-8 | 7% (g_iter0 1-14*) |
| 7 | AnOvercookedFork.quals | 2265 | 157 | 59 | 51-8 | 20% (g_iter0 1-4*) |
| 8 | pranayagra.finalbotfinaltwo | 2221 | 112 | 85 | 66-19 | 7% (g_iter0 1-13*) |
| 9 | pranayagra.finalbotfinal | 2206 | 78 | 177 | 141-36 | 13% (g_iter0 6-39) |
| 10 | georgezhang02.FB_ZZZ | 2182 | 126 | 59 | 44-15 | 0% (g_iter0 0-2*) |
| 11 | jmerle.camel_case_v30_final | 2119 | 82 | 150 | 119-31 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2007 | 110 | 65 | 49-16 | 0% (g_iter0 0-2*) |
| 13 | GabeG888.v8o1 | 1992 | 141 | 53 | 41-12 | 0% (g_iter0 0-2*) |
| 14 | georgezhang02.CB_tuning2 | 1960 | 73 | 135 | 98-37 | 7% (g_iter0 1-14*) |
| 15 | CyrilSharma.finalBot | 1948 | 130 | 65 | 42-23 | 0% (g_iter0 0-2*) |
| 16 | NotLLeon.v7 | 1935 | 74 | 125 | 89-36 | 17% (g_iter0 2-10*) |
| 17 | britacatalin.FinalBot | 1897 | 76 | 120 | 86-34 | 42% (g_iter0 5-7*) |
| 18 | GabeG888.v8 | 1866 | 106 | 62 | 41-21 | 50% (g_iter0 1-1*) |
| 19 | ethanlabelle.v19 | 1858 | 123 | 56 | 41-15 | 50% (g_iter0 1-1*) |
| 20 | **us:c_swarm1** | 1845 | 85 | 103 | 42-61 |  |
| 21 | **us:g_iter0** | 1806 | 48 | 456 | 230-226 |  |
| 22 | VarunVejalla.karel | 1802 | 96 | 80 | 43-37 | 50% (g_iter0 4-4*) |
| 23 | **us:c_line8a** | 1799 | 73 | 139 | 47-92 |  |
| 24 | programjames.fourthbot | 1782 | 128 | 59 | 35-24 | 100% (g_iter0 2-0*) |
| 25 | DannyZhang686.pqual2 | 1780 | 98 | 80 | 41-39 | 29% (g_iter0 4-10*) |
| 26 | louishu17.wouisv8 | 1771 | 111 | 78 | 44-34 | 50% (g_iter0 5-5*) |
| 27 | **us:c_line6** | 1762 | 89 | 100 | 32-68 |  |
| 28 | VarunVejalla.ali8 | 1756 | 120 | 59 | 37-22 | 50% (g_iter0 1-1*) |
| 29 | **us:c_line7m** | 1750 | 90 | 100 | 31-69 |  |
| 30 | NicholasKelly15.gopher10 | 1740 | 131 | 53 | 35-18 | 100% (g_iter0 2-0*) |
| 31 | SampleProvider.SPAARK | 1720 | 119 | 59 | 40-19 | 100% (g_iter0 2-0*) |
| 32 | battlecode-archive.Sprint1 | 1715 | 68 | 129 | 67-62 | 58% (g_iter0 7-5*) |
| 33 | **us:c_line5** | 1713 | 92 | 100 | 28-72 |  |
| 34 | louishu17.louisv10 | 1709 | 119 | 62 | 39-23 | 100% (g_iter0 2-0*) |
| 35 | reeceyang.v5anaconda | 1695 | 67 | 135 | 68-67 | 58% (g_iter0 7-5*) |
| 36 | ipince.bobby | 1675 | 141 | 50 | 33-17 | 100% (g_iter0 2-0*) |
| 37 | **us:c_line4** | 1674 | 95 | 100 | 25-75 |  |
| 38 | legobridge.tacoplayer | 1643 | 105 | 82 | 44-38 | 85% (g_iter0 11-2*) |
| 39 | polyllc.poly | 1618 | 143 | 59 | 31-28 | 100% (g_iter0 2-0*) |
| 40 | ColtG5.rexv9 | 1615 | 119 | 61 | 29-32 | 100% (g_iter0 2-0*) |
| 41 | toyat522.bot5a | 1608 | 111 | 65 | 34-31 | 80% (g_iter0 4-1*) |
| 42 | elgoldie.head_v5 | 1595 | 98 | 68 | 32-36 | 100% (g_iter0 2-0*) |
| 43 | DukeBas._main | 1593 | 113 | 65 | 38-27 | 100% (g_iter0 2-0*) |
| 44 | SteamBlizzard.newVnewME | 1590 | 104 | 68 | 33-35 | 80% (g_iter0 4-1*) |
| 45 | beaverbois.USQualifiers | 1566 | 117 | 56 | 31-25 | 50% (g_iter0 1-1*) |
| 46 | BrysonJGalapon.friday | 1551 | 101 | 71 | 40-31 | 100% (g_iter0 2-0*) |
| 47 | TheK098.qp1_7_sprint_1 | 1532 | 120 | 56 | 30-26 | 100% (g_iter0 2-0*) |
| 48 | nail-e.Barry | 1511 | 108 | 59 | 34-25 | 100% (g_iter0 2-0*) |
| 49 | kevinli405.maggi3_2 | 1506 | 117 | 71 | 36-35 | 100% (g_iter0 2-0*) |
| 50 | Nawlej.PoonPoon | 1466 | 111 | 62 | 33-29 | 100% (g_iter0 2-0*) |
| 51 | prisms-cs-club.prisms10 | 1444 | 114 | 65 | 31-34 | 100% (g_iter0 2-0*) |
| 52 | yaonam.PoonPoonv4 | 1409 | 83 | 144 | 43-101 | 87% (g_iter0 13-2*) |
| 53 | kevinli405.maggi3 | 1404 | 113 | 68 | 33-35 | 100% (g_iter0 5-0*) |
| 54 | aj-chau.attempt1 | 1394 | 118 | 59 | 28-31 | 100% (g_iter0 5-0*) |
| 55 | ipince.bobby_v2 | 1383 | 100 | 74 | 33-41 | 100% (g_iter0 5-0*) |
| 56 | BrysonJGalapon.aloha | 1350 | 104 | 62 | 31-31 | 100% (g_iter0 2-0*) |
| 57 | andrewgopher.gopherbot | 1332 | 97 | 77 | 35-42 | 100% (g_iter0 2-0*) |
| 58 | bewuwy.deathbot4 | 1331 | 95 | 83 | 31-52 | 100% (g_iter0 2-0*) |
| 59 | mama4294.currentPlayer | 1327 | 130 | 56 | 28-28 | 100% (g_iter0 2-0*) |
| 60 | PSUtblock.sprint_four_player | 1321 | 155 | 53 | 33-20 | 100% (g_iter0 2-0*) |
| 61 | JackLee9355.jackPlayer | 1309 | 101 | 77 | 32-45 | 100% (g_iter0 2-0*) |
| 62 | SDainard-PDX.Team_Player | 1298 | 135 | 53 | 24-29 | 100% (g_iter0 2-0*) |
| 63 | JfeMak.realplayer2 | 1297 | 108 | 55 | 27-28 | 100% (g_iter0 2-0*) |
| 64 | jyorkio.elicompbot | 1292 | 117 | 47 | 24-23 | 100% (g_iter0 2-0*) |
| 65 | **us:examplefuncsplayer** | 1286 | 380 | 6 | 0-6 |  |
| 66 | Nawlej.PoonPoonv3 | 1279 | 90 | 83 | 30-53 | 100% (g_iter0 5-0*) |
| 67 | SampleProvider.SPAARK_1_12_2023 | 1278 | 115 | 56 | 24-32 | 100% (g_iter0 2-0*) |
| 68 | NolanChai.nolan_1 | 1260 | 97 | 74 | 27-47 | 100% (g_iter0 2-0*) |
| 69 | andrewgopher.gopherbot1 | 1253 | 95 | 83 | 32-51 | 100% (g_iter0 2-0*) |
| 70 | Juanbri02.matfisplayer1 | 1241 | 120 | 62 | 25-37 | 100% (g_iter0 5-0*) |
| 71 | vontell.regressiongames | 1217 | 97 | 65 | 25-40 | 100% (g_iter0 5-0*) |
| 72 | SteamBlizzard.Block | 1202 | 92 | 97 | 29-68 | 100% (g_iter0 5-0*) |
| 73 | michael-tyl.hqrewrite | 1189 | 108 | 65 | 26-39 | 100% (g_iter0 2-0*) |
| 74 | anicolao.submission | 1176 | 93 | 85 | 30-55 | 100% (g_iter0 2-0*) |
| 75 | ax-95174.MPAction | 1168 | 113 | 59 | 22-37 | 100% (g_iter0 2-0*) |
| 76 | Patela171.Battlecode2023_Robot | 1158 | 108 | 71 | 26-45 | 100% (g_iter0 2-0*) |
| 77 | Chahat08.toph | 1138 | 102 | 68 | 21-47 | 100% (g_iter0 2-0*) |
| 78 | mama4294.learningBot | 1115 | 136 | 65 | 19-46 | 100% (g_iter0 2-0*) |
| 79 | nail-e.Dante | 1095 | 109 | 62 | 32-30 | 100% (g_iter0 2-0*) |
| 80 | legobridge.kushalplayer | 1078 | 147 | 59 | 17-42 | 100% (g_iter0 2-0*) |
| 81 | toyat522.bot5 | 1030 | 132 | 62 | 19-43 | 100% (g_iter0 2-0*) |
| 82 | team-remember-to-hydrate.sprint_1 | 1024 | 110 | 74 | 21-53 | 100% (g_iter0 2-0*) |
| 83 | addiesteward.elicompbot | 1000 | 106 | 74 | 24-50 | 100% (g_iter0 5-0*) |
| 84 | Vinceyou1.Player1 | 962 | 115 | 65 | 21-44 | 100% (g_iter0 2-0*) |
| 85 | monmouth-college-cs.elicompbot | 927 | 114 | 74 | 20-54 | 100% (g_iter0 2-0*) |
| 86 | michael-tyl.cc_v0_5_0_6 | 906 | 103 | 89 | 24-65 | 100% (g_iter0 2-0*) |
| 87 | Swordman51.AdeptusAstartes2 | 882 | 119 | 64 | 17-47 | 100% (g_iter0 2-0*) |
| 88 | Chahat08.lazarus | 853 | 125 | 71 | 20-51 | 100% (g_iter0 2-0*) |
| 89 | ShatterXD.SRNNbot | 794 | 122 | 65 | 18-47 | 100% (g_iter0 2-0*) |
| 90 | addiesteward.NDeClaw | 713 | 138 | 77 | 16-61 | 100% (g_iter0 5-0*) |
| 91 | CodeClash-ai.mysubmission | 637 | 131 | 73 | 14-59 | 100% (g_iter0 2-0*) |
| 92 | anicolao.jumbled | 604 | 115 | 86 | 17-69 | 100% (g_iter0 5-0*) |
| 93 | andrewkbank.First | 584 | 177 | 47 | 4-43 | 100% (g_iter0 2-0*) |
| 94 | NotLLeon.player | 558 | 227 | 47 | 2-45 | 100% (g_iter0 2-0*) |
| 95 | Yooncw0223.lec3player | 400 | 152 | 107 | 5-102 | 100% (g_iter0 5-0*) |
