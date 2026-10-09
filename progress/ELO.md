# Ladder

7095 games (1614 ours, 5481 between field bots on the ladder replica), 7041 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_nav5 | 1949 +- 79 | 15 of 97 | 106 | 52-54 | 79.4% | 21.3% (vs 14) |
| c_nav4 | 1934 +- 52 | 17 of 97 | 221 | 108-113 | 78.7% | 22.0% (vs 15) |
| c_swarm1 | 1856 +- 48 | 21 of 97 | 271 | 128-143 | 74.7% | 20.8% (vs 18) |
| g_iter0 | 1811 +- 48 | 27 of 97 | 456 | 230-226 | 72.3% | 23.8% (vs 23) |
| c_line8a | 1807 +- 71 | 28 of 97 | 139 | 47-92 | 72.1% | 23.5% (vs 23) |
| c_line6 | 1774 +- 88 | 31 of 97 | 100 | 32-68 | 70.2% | 22.8% (vs 25) |
| c_line7m | 1762 +- 88 | 33 of 97 | 100 | 31-69 | 69.5% | 22.8% (vs 26) |
| c_line5 | 1726 +- 91 | 36 of 97 | 100 | 28-72 | 67.4% | 21.8% (vs 28) |
| c_line4 | 1688 +- 94 | 38 of 97 | 100 | 25-75 | 65.2% | 19.7% (vs 29) |
| examplefuncsplayer | 1263 +- 380 | 65 of 97 | 6 | 0-6 | 37.7% | 13.6% (vs 55) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_nav5), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2403 | 90 | 114 | 94-20 | 0% (g_iter0 0-36) |
| 2 | maxwelljones14.MPWorking | 2374 | 97 | 92 | 73-19 | 0% (g_iter0 0-5*) |
| 3 | vrangr1.AFinalsBot | 2339 | 94 | 181 | 164-17 | 0% (c_nav5 0-10*) |
| 4 | awesomelemonade.finalBot | 2332 | 83 | 185 | 159-26 | 10% (c_nav5 1-9*) |
| 5 | carlguo866.submit26_final | 2294 | 94 | 97 | 73-24 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2268 | 100 | 92 | 71-21 | 17% (c_swarm1 1-5*) |
| 7 | pranayagra.finalbotfinaltwo | 2236 | 85 | 115 | 83-32 | 7% (g_iter0 1-13*) |
| 8 | pranayagra.finalbotfinal | 2180 | 61 | 235 | 176-59 | 30% (c_nav5 3-7*) |
| 9 | georgezhang02.FB_ZZZ | 2161 | 84 | 107 | 74-33 | 0% (c_nav4 0-3*) |
| 10 | battlecode-archive.sprintBot | 2149 | 92 | 109 | 78-31 | 17% (c_nav4 2-10*) |
| 11 | jmerle.camel_case_v30_final | 2106 | 61 | 218 | 162-56 | 30% (c_nav5 3-7*) |
| 12 | CyrilSharma.finalBot | 2042 | 79 | 125 | 82-43 | 44% (c_nav4 4-5*) |
| 13 | ethanlabelle.dev | 2001 | 74 | 116 | 76-40 | 67% (c_nav4 2-1*) |
| 14 | NotLLeon.v7 | 1976 | 58 | 196 | 129-67 | 50% (c_nav5 5-5*) |
| 15 | **us:c_nav5** | 1949 | 79 | 106 | 52-54 |  |
| 16 | georgezhang02.CB_tuning2 | 1940 | 54 | 207 | 131-76 | 60% (c_nav5 6-4*) |
| 17 | **us:c_nav4** | 1934 | 52 | 221 | 108-113 |  |
| 18 | ethanlabelle.v19 | 1901 | 77 | 108 | 68-40 | 56% (c_nav4 5-4*) |
| 19 | britacatalin.FinalBot | 1881 | 52 | 214 | 128-86 | 62% (c_nav5 8-5*) |
| 20 | GabeG888.v8o1 | 1879 | 80 | 103 | 66-37 | 100% (c_nav5 3-0*) |
| 21 | **us:c_swarm1** | 1856 | 48 | 271 | 128-143 |  |
| 22 | GabeG888.v8 | 1847 | 68 | 124 | 71-53 | 67% (c_nav4 4-2*) |
| 23 | programjames.fourthbot | 1839 | 78 | 116 | 68-48 | 17% (c_nav4 1-5*) |
| 24 | NicholasKelly15.gopher10 | 1832 | 85 | 98 | 62-36 | 78% (c_nav4 7-2*) |
| 25 | VarunVejalla.karel | 1822 | 67 | 146 | 81-65 | 67% (c_nav4 6-3*) |
| 26 | DannyZhang686.pqual2 | 1816 | 74 | 128 | 72-56 | 67% (c_nav4 2-1*) |
| 27 | **us:g_iter0** | 1811 | 48 | 456 | 230-226 |  |
| 28 | **us:c_line8a** | 1807 | 71 | 139 | 47-92 |  |
| 29 | louishu17.wouisv8 | 1794 | 75 | 134 | 80-54 | 33% (c_nav4 2-4*) |
| 30 | VarunVejalla.ali8 | 1789 | 83 | 104 | 63-41 | 67% (c_swarm1 6-3*) |
| 31 | **us:c_line6** | 1774 | 88 | 100 | 32-68 |  |
| 32 | louishu17.louisv10 | 1773 | 75 | 121 | 69-52 | 100% (c_nav4 6-0*) |
| 33 | **us:c_line7m** | 1762 | 88 | 100 | 31-69 |  |
| 34 | reeceyang.v5anaconda | 1748 | 52 | 219 | 106-113 | 70% (c_nav5 7-3*) |
| 35 | battlecode-archive.Sprint1 | 1733 | 53 | 202 | 99-103 | 70% (c_nav5 7-3*) |
| 36 | **us:c_line5** | 1726 | 91 | 100 | 28-72 |  |
| 37 | SampleProvider.SPAARK | 1717 | 74 | 118 | 68-50 | 100% (g_iter0 2-0*) |
| 38 | **us:c_line4** | 1688 | 94 | 100 | 25-75 |  |
| 39 | ipince.bobby | 1657 | 79 | 113 | 64-49 | 67% (c_swarm1 2-1*) |
| 40 | legobridge.tacoplayer | 1633 | 71 | 146 | 79-67 | 85% (g_iter0 11-2*) |
| 41 | TheK098.qp1_7_sprint_1 | 1610 | 75 | 125 | 72-53 | 100% (c_swarm1 6-0*) |
| 42 | polyllc.poly | 1609 | 85 | 112 | 58-54 | 100% (g_iter0 2-0*) |
| 43 | SteamBlizzard.newVnewME | 1596 | 68 | 141 | 71-70 | 80% (g_iter0 4-1*) |
| 44 | elgoldie.head_v5 | 1578 | 73 | 113 | 56-57 | 100% (g_iter0 2-0*) |
| 45 | toyat522.bot5a | 1578 | 73 | 125 | 63-62 | 80% (g_iter0 4-1*) |
| 46 | ColtG5.rexv9 | 1557 | 72 | 130 | 63-67 | 100% (g_iter0 2-0*) |
| 47 | DukeBas._main | 1556 | 78 | 119 | 64-55 | 100% (g_iter0 2-0*) |
| 48 | beaverbois.USQualifiers | 1510 | 70 | 128 | 65-63 | 50% (g_iter0 1-1*) |
| 49 | BrysonJGalapon.friday | 1509 | 65 | 138 | 73-65 | 100% (g_iter0 2-0*) |
| 50 | kevinli405.maggi3_2 | 1509 | 73 | 136 | 69-67 | 100% (g_iter0 2-0*) |
| 51 | Nawlej.PoonPoon | 1497 | 82 | 110 | 57-53 | 100% (g_iter0 2-0*) |
| 52 | nail-e.Barry | 1455 | 72 | 118 | 62-56 | 100% (g_iter0 2-0*) |
| 53 | kevinli405.maggi3 | 1450 | 74 | 134 | 70-64 | 100% (g_iter0 5-0*) |
| 54 | yaonam.PoonPoonv4 | 1427 | 58 | 241 | 87-154 | 90% (c_nav5 9-1*) |
| 55 | aj-chau.attempt1 | 1411 | 80 | 113 | 57-56 | 100% (g_iter0 5-0*) |
| 56 | prisms-cs-club.prisms10 | 1400 | 69 | 137 | 65-72 | 100% (g_iter0 2-0*) |
| 57 | ipince.bobby_v2 | 1381 | 75 | 122 | 58-64 | 67% (c_swarm1 2-1*) |
| 58 | mama4294.currentPlayer | 1364 | 69 | 137 | 66-71 | 100% (g_iter0 2-0*) |
| 59 | BrysonJGalapon.aloha | 1329 | 70 | 125 | 62-63 | 100% (c_swarm1 3-0*) |
| 60 | andrewgopher.gopherbot | 1325 | 63 | 161 | 76-85 | 100% (g_iter0 2-0*) |
| 61 | bewuwy.deathbot4 | 1298 | 60 | 174 | 77-97 | 100% (g_iter0 2-0*) |
| 62 | JfeMak.realplayer2 | 1285 | 70 | 124 | 59-65 | 100% (g_iter0 2-0*) |
| 63 | SDainard-PDX.Team_Player | 1263 | 79 | 112 | 53-59 | 100% (g_iter0 2-0*) |
| 64 | SampleProvider.SPAARK_1_12_2023 | 1263 | 64 | 148 | 69-79 | 100% (c_swarm1 3-0*) |
| 65 | **us:examplefuncsplayer** | 1263 | 380 | 6 | 0-6 |  |
| 66 | NolanChai.nolan_1 | 1236 | 67 | 140 | 66-74 | 100% (g_iter0 2-0*) |
| 67 | PSUtblock.sprint_four_player | 1235 | 77 | 125 | 60-65 | 100% (g_iter0 2-0*) |
| 68 | Juanbri02.matfisplayer1 | 1234 | 68 | 139 | 64-75 | 100% (g_iter0 5-0*) |
| 69 | Nawlej.PoonPoonv3 | 1234 | 62 | 159 | 70-89 | 100% (g_iter0 5-0*) |
| 70 | jyorkio.elicompbot | 1213 | 70 | 124 | 58-66 | 100% (g_iter0 2-0*) |
| 71 | andrewgopher.gopherbot1 | 1208 | 69 | 142 | 60-82 | 100% (g_iter0 2-0*) |
| 72 | JackLee9355.jackPlayer | 1183 | 66 | 155 | 65-90 | 100% (g_iter0 2-0*) |
| 73 | vontell.regressiongames | 1178 | 61 | 153 | 72-81 | 100% (g_iter0 5-0*) |
| 74 | ax-95174.MPAction | 1163 | 69 | 130 | 60-70 | 100% (c_swarm1 3-0*) |
| 75 | SteamBlizzard.Block | 1148 | 66 | 159 | 61-98 | 100% (g_iter0 5-0*) |
| 76 | legobridge.kushalplayer | 1084 | 83 | 113 | 44-69 | 100% (g_iter0 2-0*) |
| 77 | Patela171.Battlecode2023_Robot | 1067 | 69 | 143 | 59-84 | 100% (g_iter0 2-0*) |
| 78 | Chahat08.toph | 1064 | 68 | 139 | 57-82 | 100% (g_iter0 2-0*) |
| 79 | nail-e.Dante | 1063 | 67 | 146 | 68-78 | 100% (g_iter0 2-0*) |
| 80 | michael-tyl.hqrewrite | 1061 | 67 | 146 | 64-82 | 100% (g_iter0 2-0*) |
| 81 | anicolao.submission | 1054 | 61 | 179 | 75-104 | 100% (g_iter0 2-0*) |
| 82 | mama4294.learningBot | 1036 | 72 | 141 | 55-86 | 100% (g_iter0 2-0*) |
| 83 | team-remember-to-hydrate.sprint_1 | 942 | 65 | 162 | 64-98 | 100% (g_iter0 2-0*) |
| 84 | Vinceyou1.Player1 | 873 | 70 | 142 | 52-90 | 100% (g_iter0 2-0*) |
| 85 | michael-tyl.cc_v0_5_0_6 | 868 | 58 | 200 | 79-121 | 100% (g_iter0 2-0*) |
| 86 | addiesteward.elicompbot | 866 | 65 | 162 | 66-96 | 100% (g_iter0 5-0*) |
| 87 | Swordman51.AdeptusAstartes2 | 844 | 61 | 170 | 69-101 | 100% (g_iter0 2-0*) |
| 88 | monmouth-college-cs.elicompbot | 832 | 63 | 180 | 75-105 | 100% (g_iter0 2-0*) |
| 89 | toyat522.bot5 | 814 | 71 | 148 | 53-95 | 100% (g_iter0 2-0*) |
| 90 | Chahat08.lazarus | 801 | 68 | 153 | 61-92 | 100% (g_iter0 2-0*) |
| 91 | ShatterXD.SRNNbot | 706 | 73 | 137 | 51-86 | 100% (g_iter0 2-0*) |
| 92 | anicolao.jumbled | 701 | 59 | 205 | 79-126 | 100% (g_iter0 5-0*) |
| 93 | NotLLeon.player | 555 | 72 | 161 | 61-100 | 100% (g_iter0 2-0*) |
| 94 | CodeClash-ai.mysubmission | 534 | 72 | 169 | 63-106 | 100% (g_iter0 2-0*) |
| 95 | addiesteward.NDeClaw | 510 | 74 | 170 | 59-111 | 100% (g_iter0 5-0*) |
| 96 | andrewkbank.First | 224 | 101 | 122 | 15-107 | 100% (g_iter0 2-0*) |
| 97 | Yooncw0223.lec3player | 211 | 102 | 163 | 14-149 | 100% (g_iter0 5-0*) |
