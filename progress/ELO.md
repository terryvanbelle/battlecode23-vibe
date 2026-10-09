# Ladder

6638 games (1484 ours, 5154 between field bots on the ladder replica), 6591 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_nav4 | 1924 +- 55 | 16 of 96 | 199 | 96-103 | 77.9% | 20.4% (vs 15) |
| c_swarm1 | 1863 +- 48 | 20 of 96 | 271 | 128-143 | 74.8% | 20.6% (vs 18) |
| g_iter0 | 1819 +- 48 | 26 of 96 | 456 | 230-226 | 72.4% | 23.8% (vs 23) |
| c_line8a | 1816 +- 72 | 27 of 96 | 139 | 47-92 | 72.2% | 23.6% (vs 23) |
| c_line6 | 1782 +- 88 | 30 of 96 | 100 | 32-68 | 70.3% | 22.8% (vs 25) |
| c_line7m | 1770 +- 89 | 31 of 96 | 100 | 31-69 | 69.6% | 21.8% (vs 25) |
| c_line5 | 1733 +- 91 | 34 of 96 | 100 | 28-72 | 67.5% | 20.9% (vs 27) |
| c_line4 | 1695 +- 94 | 37 of 96 | 100 | 25-75 | 65.2% | 19.8% (vs 29) |
| examplefuncsplayer | 1256 +- 380 | 64 of 96 | 6 | 0-6 | 36.7% | 12.9% (vs 55) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2409 | 92 | 111 | 92-19 | 0% (g_iter0 0-36) |
| 2 | maxwelljones14.MPWorking | 2377 | 100 | 89 | 71-18 | 0% (g_iter0 0-5*) |
| 3 | awesomelemonade.finalBot | 2355 | 91 | 169 | 148-21 | 0% (g_iter0 0-15*) |
| 4 | vrangr1.AFinalsBot | 2336 | 98 | 168 | 153-15 | 7% (g_iter0 1-14*) |
| 5 | carlguo866.submit26_final | 2314 | 104 | 85 | 65-20 | 0% (g_iter0 0-2*) |
| 6 | AnOvercookedFork.quals | 2276 | 101 | 92 | 71-21 | 20% (g_iter0 1-4*) |
| 7 | pranayagra.finalbotfinaltwo | 2233 | 87 | 112 | 81-31 | 7% (g_iter0 1-13*) |
| 8 | pranayagra.finalbotfinal | 2184 | 63 | 222 | 167-55 | 13% (g_iter0 6-39) |
| 9 | georgezhang02.FB_ZZZ | 2176 | 86 | 104 | 73-31 | 0% (g_iter0 0-2*) |
| 10 | battlecode-archive.sprintBot | 2156 | 105 | 94 | 70-24 | 0% (g_iter0 0-2*) |
| 11 | jmerle.camel_case_v30_final | 2116 | 64 | 202 | 152-50 | 14% (g_iter0 3-18*) |
| 12 | CyrilSharma.finalBot | 2023 | 88 | 110 | 71-39 | 0% (g_iter0 0-2*) |
| 13 | ethanlabelle.dev | 2010 | 76 | 110 | 72-38 | 0% (g_iter0 0-2*) |
| 14 | NotLLeon.v7 | 1984 | 60 | 185 | 124-61 | 17% (g_iter0 2-10*) |
| 15 | georgezhang02.CB_tuning2 | 1966 | 59 | 188 | 126-62 | 7% (g_iter0 1-14*) |
| 16 | **us:c_nav4** | 1924 | 55 | 199 | 96-103 |  |
| 17 | GabeG888.v8o1 | 1909 | 85 | 97 | 66-31 | 0% (g_iter0 0-2*) |
| 18 | ethanlabelle.v19 | 1902 | 80 | 102 | 65-37 | 50% (g_iter0 1-1*) |
| 19 | britacatalin.FinalBot | 1888 | 56 | 195 | 120-75 | 42% (g_iter0 5-7*) |
| 20 | **us:c_swarm1** | 1863 | 48 | 271 | 128-143 |  |
| 21 | GabeG888.v8 | 1856 | 71 | 115 | 66-49 | 50% (g_iter0 1-1*) |
| 22 | programjames.fourthbot | 1846 | 80 | 110 | 67-43 | 100% (g_iter0 2-0*) |
| 23 | VarunVejalla.karel | 1828 | 69 | 140 | 78-62 | 50% (g_iter0 4-4*) |
| 24 | DannyZhang686.pqual2 | 1825 | 75 | 125 | 71-54 | 29% (g_iter0 4-10*) |
| 25 | NicholasKelly15.gopher10 | 1819 | 88 | 92 | 58-34 | 100% (g_iter0 2-0*) |
| 26 | **us:g_iter0** | 1819 | 48 | 456 | 230-226 |  |
| 27 | **us:c_line8a** | 1816 | 72 | 139 | 47-92 |  |
| 28 | louishu17.wouisv8 | 1801 | 76 | 134 | 80-54 | 50% (g_iter0 5-5*) |
| 29 | VarunVejalla.ali8 | 1789 | 85 | 101 | 61-40 | 50% (g_iter0 1-1*) |
| 30 | **us:c_line6** | 1782 | 88 | 100 | 32-68 |  |
| 31 | **us:c_line7m** | 1770 | 89 | 100 | 31-69 |  |
| 32 | louishu17.louisv10 | 1767 | 78 | 115 | 64-51 | 100% (g_iter0 2-0*) |
| 33 | reeceyang.v5anaconda | 1755 | 54 | 203 | 102-101 | 58% (g_iter0 7-5*) |
| 34 | **us:c_line5** | 1733 | 91 | 100 | 28-72 |  |
| 35 | battlecode-archive.Sprint1 | 1731 | 56 | 186 | 91-95 | 58% (g_iter0 7-5*) |
| 36 | SampleProvider.SPAARK | 1727 | 78 | 109 | 64-45 | 100% (g_iter0 2-0*) |
| 37 | **us:c_line4** | 1695 | 94 | 100 | 25-75 |  |
| 38 | ipince.bobby | 1659 | 82 | 107 | 60-47 | 100% (g_iter0 2-0*) |
| 39 | legobridge.tacoplayer | 1647 | 74 | 137 | 76-61 | 85% (g_iter0 11-2*) |
| 40 | polyllc.poly | 1619 | 92 | 103 | 53-50 | 100% (g_iter0 2-0*) |
| 41 | TheK098.qp1_7_sprint_1 | 1607 | 76 | 122 | 69-53 | 100% (g_iter0 2-0*) |
| 42 | SteamBlizzard.newVnewME | 1593 | 71 | 132 | 65-67 | 80% (g_iter0 4-1*) |
| 43 | toyat522.bot5a | 1591 | 75 | 119 | 61-58 | 80% (g_iter0 4-1*) |
| 44 | elgoldie.head_v5 | 1580 | 74 | 110 | 54-56 | 100% (g_iter0 2-0*) |
| 45 | ColtG5.rexv9 | 1565 | 73 | 127 | 62-65 | 100% (g_iter0 2-0*) |
| 46 | DukeBas._main | 1559 | 80 | 113 | 60-53 | 100% (g_iter0 2-0*) |
| 47 | beaverbois.USQualifiers | 1525 | 73 | 119 | 62-57 | 50% (g_iter0 1-1*) |
| 48 | kevinli405.maggi3_2 | 1525 | 77 | 127 | 65-62 | 100% (g_iter0 2-0*) |
| 49 | Nawlej.PoonPoon | 1505 | 82 | 107 | 57-50 | 100% (g_iter0 2-0*) |
| 50 | BrysonJGalapon.friday | 1498 | 71 | 120 | 61-59 | 100% (g_iter0 2-0*) |
| 51 | nail-e.Barry | 1463 | 76 | 109 | 57-52 | 100% (g_iter0 2-0*) |
| 52 | kevinli405.maggi3 | 1444 | 77 | 125 | 66-59 | 100% (g_iter0 5-0*) |
| 53 | yaonam.PoonPoonv4 | 1427 | 59 | 225 | 82-143 | 87% (g_iter0 13-2*) |
| 54 | aj-chau.attempt1 | 1416 | 83 | 107 | 55-52 | 100% (g_iter0 5-0*) |
| 55 | ipince.bobby_v2 | 1390 | 76 | 119 | 57-62 | 100% (g_iter0 5-0*) |
| 56 | mama4294.currentPlayer | 1383 | 75 | 122 | 61-61 | 100% (g_iter0 2-0*) |
| 57 | prisms-cs-club.prisms10 | 1382 | 73 | 125 | 54-71 | 100% (g_iter0 2-0*) |
| 58 | BrysonJGalapon.aloha | 1347 | 75 | 110 | 57-53 | 100% (g_iter0 2-0*) |
| 59 | andrewgopher.gopherbot | 1339 | 67 | 146 | 69-77 | 100% (g_iter0 2-0*) |
| 60 | bewuwy.deathbot4 | 1302 | 62 | 165 | 72-93 | 100% (g_iter0 2-0*) |
| 61 | JfeMak.realplayer2 | 1298 | 73 | 115 | 55-60 | 100% (g_iter0 2-0*) |
| 62 | SampleProvider.SPAARK_1_12_2023 | 1276 | 67 | 136 | 63-73 | 100% (g_iter0 2-0*) |
| 63 | SDainard-PDX.Team_Player | 1267 | 86 | 100 | 46-54 | 100% (g_iter0 2-0*) |
| 64 | **us:examplefuncsplayer** | 1256 | 380 | 6 | 0-6 |  |
| 65 | PSUtblock.sprint_four_player | 1254 | 80 | 119 | 58-61 | 100% (g_iter0 2-0*) |
| 66 | NolanChai.nolan_1 | 1246 | 70 | 131 | 62-69 | 100% (g_iter0 2-0*) |
| 67 | Juanbri02.matfisplayer1 | 1243 | 68 | 137 | 63-74 | 100% (g_iter0 5-0*) |
| 68 | Nawlej.PoonPoonv3 | 1239 | 66 | 145 | 63-82 | 100% (g_iter0 5-0*) |
| 69 | jyorkio.elicompbot | 1219 | 74 | 113 | 51-62 | 100% (g_iter0 2-0*) |
| 70 | andrewgopher.gopherbot1 | 1219 | 71 | 137 | 58-79 | 100% (g_iter0 2-0*) |
| 71 | JackLee9355.jackPlayer | 1202 | 68 | 146 | 60-86 | 100% (g_iter0 2-0*) |
| 72 | vontell.regressiongames | 1182 | 62 | 150 | 69-81 | 100% (g_iter0 5-0*) |
| 73 | SteamBlizzard.Block | 1162 | 66 | 159 | 61-98 | 100% (g_iter0 5-0*) |
| 74 | ax-95174.MPAction | 1153 | 75 | 113 | 48-65 | 100% (g_iter0 2-0*) |
| 75 | nail-e.Dante | 1092 | 69 | 137 | 67-70 | 100% (g_iter0 2-0*) |
| 76 | legobridge.kushalplayer | 1092 | 86 | 107 | 41-66 | 100% (g_iter0 2-0*) |
| 77 | Chahat08.toph | 1090 | 70 | 130 | 54-76 | 100% (g_iter0 2-0*) |
| 78 | anicolao.submission | 1082 | 64 | 164 | 69-95 | 100% (g_iter0 2-0*) |
| 79 | Patela171.Battlecode2023_Robot | 1073 | 71 | 137 | 55-82 | 100% (g_iter0 2-0*) |
| 80 | michael-tyl.hqrewrite | 1072 | 69 | 137 | 59-78 | 100% (g_iter0 2-0*) |
| 81 | mama4294.learningBot | 1058 | 75 | 133 | 53-80 | 100% (g_iter0 2-0*) |
| 82 | team-remember-to-hydrate.sprint_1 | 946 | 68 | 153 | 58-95 | 100% (g_iter0 2-0*) |
| 83 | Vinceyou1.Player1 | 895 | 72 | 136 | 49-87 | 100% (g_iter0 2-0*) |
| 84 | michael-tyl.cc_v0_5_0_6 | 893 | 60 | 185 | 73-112 | 100% (g_iter0 2-0*) |
| 85 | addiesteward.elicompbot | 885 | 67 | 153 | 60-93 | 100% (g_iter0 5-0*) |
| 86 | Swordman51.AdeptusAstartes2 | 863 | 63 | 158 | 66-92 | 100% (g_iter0 2-0*) |
| 87 | monmouth-college-cs.elicompbot | 843 | 68 | 159 | 60-99 | 100% (g_iter0 2-0*) |
| 88 | toyat522.bot5 | 818 | 75 | 139 | 48-91 | 100% (g_iter0 2-0*) |
| 89 | Chahat08.lazarus | 798 | 73 | 138 | 53-85 | 100% (g_iter0 2-0*) |
| 90 | anicolao.jumbled | 718 | 63 | 184 | 73-111 | 100% (g_iter0 5-0*) |
| 91 | ShatterXD.SRNNbot | 715 | 76 | 131 | 47-84 | 100% (g_iter0 2-0*) |
| 92 | NotLLeon.player | 578 | 72 | 158 | 61-97 | 100% (g_iter0 2-0*) |
| 93 | CodeClash-ai.mysubmission | 554 | 72 | 169 | 63-106 | 100% (g_iter0 2-0*) |
| 94 | addiesteward.NDeClaw | 538 | 75 | 163 | 58-105 | 100% (g_iter0 5-0*) |
| 95 | andrewkbank.First | 254 | 103 | 119 | 14-105 | 100% (g_iter0 2-0*) |
| 96 | Yooncw0223.lec3player | 228 | 108 | 159 | 12-147 | 100% (g_iter0 5-0*) |
