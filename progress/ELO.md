# Ladder

8114 games (1874 ours, 6240 between field bots on the ladder replica), 8047 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_anc3 | 2040 +- 79 | 12 of 99 | 109 | 64-45 | 84.1% | 25.3% (vs 11) |
| c_nav5 | 1953 +- 71 | 16 of 99 | 126 | 61-65 | 80.2% | 23.0% (vs 14) |
| c_nav6 | 1940 +- 71 | 17 of 99 | 129 | 58-71 | 79.6% | 21.8% (vs 14) |
| c_nav4 | 1921 +- 52 | 19 of 99 | 221 | 108-113 | 78.7% | 22.0% (vs 15) |
| c_swarm1 | 1844 +- 48 | 22 of 99 | 271 | 128-143 | 74.8% | 19.4% (vs 17) |
| c_line8a | 1800 +- 71 | 29 of 99 | 139 | 47-92 | 72.5% | 24.2% (vs 23) |
| g_iter0 | 1800 +- 48 | 30 of 99 | 456 | 230-226 | 72.5% | 24.2% (vs 23) |
| c_line6 | 1768 +- 88 | 33 of 99 | 100 | 32-68 | 70.6% | 23.6% (vs 25) |
| c_line7m | 1756 +- 88 | 34 of 99 | 100 | 31-69 | 70.0% | 22.6% (vs 25) |
| c_line5 | 1720 +- 91 | 39 of 99 | 100 | 28-72 | 67.9% | 23.5% (vs 29) |
| c_line4 | 1682 +- 93 | 40 of 99 | 100 | 25-75 | 65.6% | 20.3% (vs 29) |
| examplefuncsplayer | 1248 +- 380 | 66 of 99 | 6 | 0-6 | 38.0% | 12.7% (vs 54) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_anc3), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2380 | 84 | 122 | 98-24 | 0% (g_iter0 0-36) |
| 2 | maxwelljones14.MPWorking | 2369 | 90 | 101 | 79-22 | 0% (g_iter0 0-5*) |
| 3 | vrangr1.AFinalsBot | 2338 | 81 | 213 | 190-23 | 10% (c_anc3 1-9*) |
| 4 | awesomelemonade.finalBot | 2329 | 75 | 213 | 182-31 | 20% (c_anc3 2-8*) |
| 5 | carlguo866.submit26_final | 2283 | 88 | 106 | 79-27 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2233 | 89 | 107 | 76-31 | 33% (c_nav6 1-2*) |
| 7 | pranayagra.finalbotfinaltwo | 2210 | 78 | 127 | 89-38 | 7% (g_iter0 1-13*) |
| 8 | pranayagra.finalbotfinal | 2160 | 55 | 267 | 196-71 | 40% (c_anc3 4-6*) |
| 9 | georgezhang02.FB_ZZZ | 2133 | 75 | 125 | 83-42 | 33% (c_nav6 2-4*) |
| 10 | battlecode-archive.sprintBot | 2129 | 83 | 124 | 87-37 | 0% (c_nav6 0-3*) |
| 11 | jmerle.camel_case_v30_final | 2098 | 55 | 250 | 183-67 | 40% (c_anc3 4-6*) |
| 12 | **us:c_anc3** | 2040 | 79 | 109 | 64-45 |  |
| 13 | CyrilSharma.finalBot | 2024 | 68 | 152 | 94-58 | 33% (c_anc3 1-2*) |
| 14 | ethanlabelle.dev | 1992 | 70 | 128 | 83-45 | 100% (c_nav6 3-0*) |
| 15 | NotLLeon.v7 | 1977 | 52 | 236 | 152-84 | 50% (c_anc3 5-5*) |
| 16 | **us:c_nav5** | 1953 | 71 | 126 | 61-65 |  |
| 17 | **us:c_nav6** | 1940 | 71 | 129 | 58-71 |  |
| 18 | georgezhang02.CB_tuning2 | 1937 | 50 | 234 | 145-89 | 50% (c_anc3 5-5*) |
| 19 | **us:c_nav4** | 1921 | 52 | 221 | 108-113 |  |
| 20 | britacatalin.FinalBot | 1873 | 49 | 245 | 140-105 | 85% (c_anc3 11-2*) |
| 21 | ethanlabelle.v19 | 1872 | 73 | 117 | 70-47 | 100% (c_nav5 3-0*) |
| 22 | **us:c_swarm1** | 1844 | 48 | 271 | 128-143 |  |
| 23 | GabeG888.v8o1 | 1839 | 71 | 121 | 73-48 | 100% (c_nav5 3-0*) |
| 24 | GabeG888.v8 | 1838 | 63 | 139 | 80-59 | 67% (c_nav4 4-2*) |
| 25 | DannyZhang686.pqual2 | 1820 | 64 | 158 | 90-68 | 100% (c_anc3 3-0*) |
| 26 | VarunVejalla.karel | 1811 | 64 | 155 | 86-69 | 67% (c_nav4 6-3*) |
| 27 | NicholasKelly15.gopher10 | 1810 | 80 | 107 | 65-42 | 78% (c_nav4 7-2*) |
| 28 | programjames.fourthbot | 1806 | 72 | 131 | 73-58 | 17% (c_nav4 1-5*) |
| 29 | **us:c_line8a** | 1800 | 71 | 139 | 47-92 |  |
| 30 | **us:g_iter0** | 1800 | 48 | 456 | 230-226 |  |
| 31 | VarunVejalla.ali8 | 1783 | 71 | 128 | 75-53 | 67% (c_swarm1 6-3*) |
| 32 | louishu17.wouisv8 | 1770 | 68 | 155 | 88-67 | 33% (c_nav4 2-4*) |
| 33 | **us:c_line6** | 1768 | 88 | 100 | 32-68 |  |
| 34 | **us:c_line7m** | 1756 | 88 | 100 | 31-69 |  |
| 35 | louishu17.louisv10 | 1753 | 70 | 136 | 76-60 | 100% (c_nav4 6-0*) |
| 36 | reeceyang.v5anaconda | 1738 | 49 | 251 | 116-135 | 90% (c_anc3 9-1*) |
| 37 | battlecode-archive.Sprint1 | 1728 | 49 | 240 | 113-127 | 100% (c_anc3 10-0*) |
| 38 | SampleProvider.SPAARK | 1726 | 70 | 130 | 77-53 | 100% (g_iter0 2-0*) |
| 39 | **us:c_line5** | 1720 | 91 | 100 | 28-72 |  |
| 40 | **us:c_line4** | 1682 | 93 | 100 | 25-75 |  |
| 41 | ipince.bobby | 1645 | 73 | 125 | 71-54 | 67% (c_swarm1 2-1*) |
| 42 | legobridge.tacoplayer | 1612 | 67 | 158 | 84-74 | 85% (g_iter0 11-2*) |
| 43 | TheK098.qp1_7_sprint_1 | 1608 | 68 | 146 | 82-64 | 100% (c_swarm1 6-0*) |
| 44 | SteamBlizzard.newVnewME | 1598 | 64 | 156 | 80-76 | 80% (g_iter0 4-1*) |
| 45 | polyllc.poly | 1597 | 82 | 118 | 61-57 | 100% (g_iter0 2-0*) |
| 46 | toyat522.bot5a | 1567 | 70 | 134 | 68-66 | 80% (g_iter0 4-1*) |
| 47 | elgoldie.head_v5 | 1566 | 69 | 125 | 61-64 | 100% (g_iter0 2-0*) |
| 48 | ColtG5.rexv9 | 1556 | 64 | 154 | 79-75 | 100% (g_iter0 2-0*) |
| 49 | DukeBas._main | 1544 | 69 | 143 | 76-67 | 100% (g_iter0 2-0*) |
| 50 | BrysonJGalapon.friday | 1486 | 63 | 147 | 76-71 | 100% (g_iter0 2-0*) |
| 51 | beaverbois.USQualifiers | 1482 | 65 | 143 | 72-71 | 50% (g_iter0 1-1*) |
| 52 | kevinli405.maggi3_2 | 1466 | 67 | 154 | 75-79 | 100% (g_iter0 2-0*) |
| 53 | Nawlej.PoonPoon | 1462 | 74 | 128 | 63-65 | 100% (g_iter0 2-0*) |
| 54 | nail-e.Barry | 1459 | 68 | 130 | 70-60 | 100% (g_iter0 2-0*) |
| 55 | kevinli405.maggi3 | 1433 | 69 | 149 | 76-73 | 100% (g_iter0 5-0*) |
| 56 | aj-chau.attempt1 | 1430 | 69 | 140 | 73-67 | 100% (g_iter0 5-0*) |
| 57 | yaonam.PoonPoonv4 | 1425 | 54 | 279 | 97-182 | 90% (c_anc3 9-1*) |
| 58 | prisms-cs-club.prisms10 | 1395 | 69 | 140 | 68-72 | 100% (g_iter0 2-0*) |
| 59 | ipince.bobby_v2 | 1365 | 68 | 143 | 70-73 | 67% (c_swarm1 2-1*) |
| 60 | mama4294.currentPlayer | 1361 | 63 | 158 | 78-80 | 100% (g_iter0 2-0*) |
| 61 | andrewgopher.gopherbot | 1314 | 58 | 182 | 89-93 | 100% (g_iter0 2-0*) |
| 62 | BrysonJGalapon.aloha | 1308 | 62 | 155 | 77-78 | 100% (c_swarm1 3-0*) |
| 63 | bewuwy.deathbot4 | 1280 | 57 | 192 | 85-107 | 100% (g_iter0 2-0*) |
| 64 | JfeMak.realplayer2 | 1277 | 69 | 130 | 63-67 | 100% (g_iter0 2-0*) |
| 65 | PSUtblock.sprint_four_player | 1267 | 71 | 140 | 74-66 | 100% (g_iter0 2-0*) |
| 66 | **us:examplefuncsplayer** | 1248 | 380 | 6 | 0-6 |  |
| 67 | SampleProvider.SPAARK_1_12_2023 | 1248 | 58 | 181 | 85-96 | 100% (c_swarm1 3-0*) |
| 68 | SDainard-PDX.Team_Player | 1241 | 71 | 133 | 64-69 | 100% (g_iter0 2-0*) |
| 69 | Juanbri02.matfisplayer1 | 1228 | 60 | 168 | 79-89 | 100% (g_iter0 5-0*) |
| 70 | NolanChai.nolan_1 | 1210 | 64 | 152 | 70-82 | 100% (g_iter0 2-0*) |
| 71 | Nawlej.PoonPoonv3 | 1199 | 58 | 180 | 79-101 | 100% (g_iter0 5-0*) |
| 72 | jyorkio.elicompbot | 1199 | 64 | 144 | 69-75 | 100% (g_iter0 2-0*) |
| 73 | andrewgopher.gopherbot1 | 1184 | 65 | 157 | 67-90 | 100% (g_iter0 2-0*) |
| 74 | JackLee9355.jackPlayer | 1140 | 62 | 173 | 73-100 | 100% (g_iter0 2-0*) |
| 75 | vontell.regressiongames | 1140 | 54 | 195 | 90-105 | 100% (g_iter0 5-0*) |
| 76 | SteamBlizzard.Block | 1113 | 60 | 186 | 76-110 | 100% (g_iter0 5-0*) |
| 77 | ax-95174.MPAction | 1104 | 64 | 151 | 64-87 | 100% (c_swarm1 3-0*) |
| 78 | legobridge.kushalplayer | 1072 | 75 | 131 | 53-78 | 100% (g_iter0 2-0*) |
| 79 | Patela171.Battlecode2023_Robot | 1064 | 62 | 167 | 73-94 | 100% (g_iter0 2-0*) |
| 80 | michael-tyl.hqrewrite | 1046 | 60 | 173 | 79-94 | 100% (g_iter0 2-0*) |
| 81 | Chahat08.toph | 1040 | 63 | 157 | 68-89 | 100% (g_iter0 2-0*) |
| 82 | anicolao.submission | 1022 | 58 | 197 | 84-113 | 100% (g_iter0 2-0*) |
| 83 | nail-e.Dante | 1020 | 62 | 170 | 78-92 | 100% (g_iter0 2-0*) |
| 84 | mama4294.learningBot | 996 | 66 | 161 | 63-98 | 100% (g_iter0 2-0*) |
| 85 | team-remember-to-hydrate.sprint_1 | 931 | 60 | 185 | 77-108 | 100% (g_iter0 2-0*) |
| 86 | Vinceyou1.Player1 | 840 | 65 | 163 | 64-99 | 100% (g_iter0 2-0*) |
| 87 | michael-tyl.cc_v0_5_0_6 | 832 | 55 | 219 | 89-130 | 100% (g_iter0 2-0*) |
| 88 | addiesteward.elicompbot | 827 | 60 | 186 | 77-109 | 100% (g_iter0 5-0*) |
| 89 | Swordman51.AdeptusAstartes2 | 800 | 56 | 197 | 82-115 | 100% (g_iter0 2-0*) |
| 90 | monmouth-college-cs.elicompbot | 796 | 62 | 188 | 78-110 | 100% (g_iter0 2-0*) |
| 91 | Chahat08.lazarus | 784 | 62 | 175 | 73-102 | 100% (g_iter0 2-0*) |
| 92 | toyat522.bot5 | 764 | 63 | 182 | 69-113 | 100% (g_iter0 2-0*) |
| 93 | anicolao.jumbled | 671 | 56 | 224 | 89-135 | 100% (g_iter0 5-0*) |
| 94 | ShatterXD.SRNNbot | 655 | 66 | 166 | 63-103 | 100% (g_iter0 2-0*) |
| 95 | NotLLeon.player | 494 | 66 | 186 | 73-113 | 100% (g_iter0 2-0*) |
| 96 | CodeClash-ai.mysubmission | 485 | 67 | 196 | 77-119 | 100% (g_iter0 2-0*) |
| 97 | addiesteward.NDeClaw | 471 | 71 | 187 | 70-117 | 100% (g_iter0 5-0*) |
| 98 | Yooncw0223.lec3player | 168 | 94 | 178 | 18-160 | 100% (g_iter0 5-0*) |
| 99 | andrewkbank.First | 140 | 96 | 142 | 16-126 | 100% (g_iter0 2-0*) |
