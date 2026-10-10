# Ladder

8465 games (1916 ours, 6549 between field bots on the ladder replica), 8393 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_anc3 | 2023 +- 64 | 13 of 99 | 151 | 81-70 | 83.4% | 25.9% (vs 12) |
| c_nav5 | 1951 +- 71 | 16 of 99 | 126 | 61-65 | 80.2% | 23.0% (vs 14) |
| c_nav6 | 1938 +- 71 | 18 of 99 | 129 | 58-71 | 79.5% | 23.7% (vs 15) |
| c_nav4 | 1918 +- 52 | 19 of 99 | 221 | 108-113 | 78.6% | 21.9% (vs 15) |
| c_swarm1 | 1844 +- 48 | 23 of 99 | 271 | 128-143 | 74.8% | 21.2% (vs 18) |
| g_iter0 | 1800 +- 48 | 29 of 99 | 456 | 230-226 | 72.4% | 24.3% (vs 23) |
| c_line8a | 1799 +- 71 | 31 of 99 | 139 | 47-92 | 72.4% | 25.3% (vs 24) |
| c_line6 | 1766 +- 88 | 33 of 99 | 100 | 32-68 | 70.5% | 23.4% (vs 25) |
| c_line7m | 1754 +- 88 | 34 of 99 | 100 | 31-69 | 69.8% | 22.4% (vs 25) |
| c_line5 | 1718 +- 91 | 39 of 99 | 100 | 28-72 | 67.7% | 23.3% (vs 29) |
| c_line4 | 1680 +- 93 | 40 of 99 | 100 | 25-75 | 65.5% | 20.1% (vs 29) |
| examplefuncsplayer | 1245 +- 380 | 67 of 99 | 6 | 0-6 | 37.7% | 13.1% (vs 55) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_anc3), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2377 | 84 | 122 | 98-24 | 0% (g_iter0 0-36) |
| 2 | maxwelljones14.MPWorking | 2365 | 90 | 101 | 79-22 | 0% (g_iter0 0-5*) |
| 3 | vrangr1.AFinalsBot | 2337 | 80 | 216 | 192-24 | 10% (c_anc3 1-9*) |
| 4 | awesomelemonade.finalBot | 2325 | 75 | 213 | 182-31 | 20% (c_anc3 2-8*) |
| 5 | carlguo866.submit26_final | 2268 | 82 | 115 | 83-32 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2238 | 87 | 110 | 79-31 | 0% (c_anc3 0-3*) |
| 7 | pranayagra.finalbotfinaltwo | 2193 | 74 | 136 | 93-43 | 33% (c_anc3 2-4*) |
| 8 | pranayagra.finalbotfinal | 2168 | 54 | 273 | 201-72 | 40% (c_anc3 4-6*) |
| 9 | georgezhang02.FB_ZZZ | 2140 | 73 | 131 | 87-44 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2128 | 81 | 127 | 89-38 | 33% (c_anc3 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2097 | 55 | 253 | 185-68 | 38% (c_anc3 5-8*) |
| 12 | CyrilSharma.finalBot | 2026 | 65 | 161 | 99-62 | 42% (c_anc3 5-7*) |
| 13 | **us:c_anc3** | 2023 | 64 | 151 | 81-70 |  |
| 14 | ethanlabelle.dev | 2000 | 68 | 134 | 87-47 | 33% (c_anc3 2-4*) |
| 15 | NotLLeon.v7 | 1959 | 50 | 248 | 154-94 | 69% (c_anc3 11-5*) |
| 16 | **us:c_nav5** | 1951 | 71 | 126 | 61-65 |  |
| 17 | georgezhang02.CB_tuning2 | 1939 | 50 | 237 | 147-90 | 46% (c_anc3 6-7*) |
| 18 | **us:c_nav6** | 1938 | 71 | 129 | 58-71 |  |
| 19 | **us:c_nav4** | 1918 | 52 | 221 | 108-113 |  |
| 20 | britacatalin.FinalBot | 1873 | 48 | 251 | 144-107 | 85% (c_anc3 11-2*) |
| 21 | ethanlabelle.v19 | 1860 | 72 | 120 | 70-50 | 100% (c_nav5 3-0*) |
| 22 | GabeG888.v8 | 1849 | 61 | 148 | 86-62 | 67% (c_nav4 4-2*) |
| 23 | **us:c_swarm1** | 1844 | 48 | 271 | 128-143 |  |
| 24 | GabeG888.v8o1 | 1830 | 69 | 130 | 78-52 | 100% (c_nav5 3-0*) |
| 25 | DannyZhang686.pqual2 | 1819 | 63 | 164 | 92-72 | 100% (c_anc3 3-0*) |
| 26 | programjames.fourthbot | 1811 | 70 | 134 | 75-59 | 17% (c_nav4 1-5*) |
| 27 | VarunVejalla.karel | 1810 | 63 | 158 | 87-71 | 67% (c_nav4 6-3*) |
| 28 | NicholasKelly15.gopher10 | 1810 | 77 | 113 | 68-45 | 78% (c_nav4 7-2*) |
| 29 | **us:g_iter0** | 1800 | 48 | 456 | 230-226 |  |
| 30 | VarunVejalla.ali8 | 1799 | 68 | 137 | 81-56 | 67% (c_swarm1 6-3*) |
| 31 | **us:c_line8a** | 1799 | 71 | 139 | 47-92 |  |
| 32 | louishu17.wouisv8 | 1768 | 68 | 155 | 88-67 | 33% (c_nav4 2-4*) |
| 33 | **us:c_line6** | 1766 | 88 | 100 | 32-68 |  |
| 34 | **us:c_line7m** | 1754 | 88 | 100 | 31-69 |  |
| 35 | louishu17.louisv10 | 1753 | 69 | 139 | 78-61 | 100% (c_nav4 6-0*) |
| 36 | reeceyang.v5anaconda | 1737 | 49 | 251 | 116-135 | 90% (c_anc3 9-1*) |
| 37 | SampleProvider.SPAARK | 1727 | 70 | 130 | 77-53 | 100% (g_iter0 2-0*) |
| 38 | battlecode-archive.Sprint1 | 1727 | 49 | 240 | 113-127 | 100% (c_anc3 10-0*) |
| 39 | **us:c_line5** | 1718 | 91 | 100 | 28-72 |  |
| 40 | **us:c_line4** | 1680 | 93 | 100 | 25-75 |  |
| 41 | ipince.bobby | 1646 | 73 | 125 | 71-54 | 67% (c_swarm1 2-1*) |
| 42 | legobridge.tacoplayer | 1625 | 65 | 167 | 91-76 | 85% (g_iter0 11-2*) |
| 43 | polyllc.poly | 1611 | 76 | 130 | 68-62 | 100% (g_iter0 2-0*) |
| 44 | TheK098.qp1_7_sprint_1 | 1607 | 66 | 152 | 84-68 | 100% (c_swarm1 6-0*) |
| 45 | SteamBlizzard.newVnewME | 1597 | 62 | 162 | 82-80 | 80% (g_iter0 4-1*) |
| 46 | toyat522.bot5a | 1569 | 66 | 146 | 75-71 | 80% (g_iter0 4-1*) |
| 47 | elgoldie.head_v5 | 1567 | 64 | 140 | 69-71 | 100% (g_iter0 2-0*) |
| 48 | DukeBas._main | 1546 | 65 | 155 | 83-72 | 100% (g_iter0 2-0*) |
| 49 | ColtG5.rexv9 | 1545 | 62 | 163 | 81-82 | 100% (g_iter0 2-0*) |
| 50 | BrysonJGalapon.friday | 1480 | 61 | 156 | 80-76 | 100% (g_iter0 2-0*) |
| 51 | beaverbois.USQualifiers | 1480 | 64 | 146 | 73-73 | 50% (g_iter0 1-1*) |
| 52 | kevinli405.maggi3_2 | 1476 | 65 | 160 | 81-79 | 100% (g_iter0 2-0*) |
| 53 | Nawlej.PoonPoon | 1459 | 72 | 134 | 65-69 | 100% (g_iter0 2-0*) |
| 54 | nail-e.Barry | 1457 | 65 | 142 | 75-67 | 100% (g_iter0 2-0*) |
| 55 | aj-chau.attempt1 | 1434 | 66 | 149 | 78-71 | 100% (g_iter0 5-0*) |
| 56 | kevinli405.maggi3 | 1432 | 69 | 149 | 76-73 | 100% (g_iter0 5-0*) |
| 57 | yaonam.PoonPoonv4 | 1420 | 53 | 285 | 99-186 | 90% (c_anc3 9-1*) |
| 58 | prisms-cs-club.prisms10 | 1406 | 66 | 149 | 73-76 | 100% (g_iter0 2-0*) |
| 59 | mama4294.currentPlayer | 1365 | 60 | 170 | 85-85 | 100% (g_iter0 2-0*) |
| 60 | ipince.bobby_v2 | 1363 | 69 | 143 | 70-73 | 67% (c_swarm1 2-1*) |
| 61 | andrewgopher.gopherbot | 1311 | 58 | 185 | 89-96 | 100% (g_iter0 2-0*) |
| 62 | BrysonJGalapon.aloha | 1299 | 60 | 164 | 80-84 | 100% (c_swarm1 3-0*) |
| 63 | JfeMak.realplayer2 | 1293 | 65 | 142 | 72-70 | 100% (g_iter0 2-0*) |
| 64 | bewuwy.deathbot4 | 1284 | 56 | 196 | 88-108 | 100% (g_iter0 2-0*) |
| 65 | PSUtblock.sprint_four_player | 1258 | 70 | 143 | 74-69 | 100% (g_iter0 2-0*) |
| 66 | SampleProvider.SPAARK_1_12_2023 | 1257 | 55 | 196 | 94-102 | 100% (c_swarm1 3-0*) |
| 67 | **us:examplefuncsplayer** | 1245 | 380 | 6 | 0-6 |  |
| 68 | SDainard-PDX.Team_Player | 1227 | 66 | 149 | 69-80 | 100% (g_iter0 2-0*) |
| 69 | Juanbri02.matfisplayer1 | 1221 | 57 | 183 | 85-98 | 100% (g_iter0 5-0*) |
| 70 | NolanChai.nolan_1 | 1214 | 63 | 158 | 74-84 | 100% (g_iter0 2-0*) |
| 71 | Nawlej.PoonPoonv3 | 1205 | 57 | 188 | 85-103 | 100% (g_iter0 5-0*) |
| 72 | andrewgopher.gopherbot1 | 1189 | 62 | 169 | 75-94 | 100% (g_iter0 2-0*) |
| 73 | jyorkio.elicompbot | 1189 | 60 | 159 | 75-84 | 100% (g_iter0 2-0*) |
| 74 | vontell.regressiongames | 1151 | 52 | 209 | 101-108 | 100% (g_iter0 5-0*) |
| 75 | JackLee9355.jackPlayer | 1121 | 60 | 182 | 75-107 | 100% (g_iter0 2-0*) |
| 76 | SteamBlizzard.Block | 1105 | 55 | 207 | 86-121 | 100% (g_iter0 5-0*) |
| 77 | ax-95174.MPAction | 1099 | 61 | 160 | 68-92 | 100% (c_swarm1 3-0*) |
| 78 | legobridge.kushalplayer | 1076 | 71 | 140 | 58-82 | 100% (g_iter0 2-0*) |
| 79 | Patela171.Battlecode2023_Robot | 1063 | 58 | 185 | 81-104 | 100% (g_iter0 2-0*) |
| 80 | michael-tyl.hqrewrite | 1050 | 59 | 176 | 82-94 | 100% (g_iter0 2-0*) |
| 81 | nail-e.Dante | 1030 | 61 | 173 | 81-92 | 100% (g_iter0 2-0*) |
| 82 | Chahat08.toph | 1020 | 61 | 166 | 69-97 | 100% (g_iter0 2-0*) |
| 83 | anicolao.submission | 1000 | 55 | 220 | 96-124 | 100% (g_iter0 2-0*) |
| 84 | mama4294.learningBot | 999 | 64 | 170 | 70-100 | 100% (g_iter0 2-0*) |
| 85 | team-remember-to-hydrate.sprint_1 | 931 | 58 | 197 | 81-116 | 100% (g_iter0 2-0*) |
| 86 | Vinceyou1.Player1 | 851 | 64 | 166 | 66-100 | 100% (g_iter0 2-0*) |
| 87 | addiesteward.elicompbot | 841 | 57 | 201 | 85-116 | 100% (g_iter0 5-0*) |
| 88 | michael-tyl.cc_v0_5_0_6 | 817 | 52 | 234 | 93-141 | 100% (g_iter0 2-0*) |
| 89 | Swordman51.AdeptusAstartes2 | 804 | 55 | 203 | 83-120 | 100% (g_iter0 2-0*) |
| 90 | Chahat08.lazarus | 797 | 59 | 187 | 79-108 | 100% (g_iter0 2-0*) |
| 91 | monmouth-college-cs.elicompbot | 796 | 58 | 202 | 83-119 | 100% (g_iter0 2-0*) |
| 92 | toyat522.bot5 | 781 | 60 | 194 | 77-117 | 100% (g_iter0 2-0*) |
| 93 | anicolao.jumbled | 685 | 54 | 236 | 98-138 | 100% (g_iter0 5-0*) |
| 94 | ShatterXD.SRNNbot | 661 | 65 | 169 | 64-105 | 100% (g_iter0 2-0*) |
| 95 | NotLLeon.player | 503 | 65 | 194 | 76-118 | 100% (g_iter0 2-0*) |
| 96 | CodeClash-ai.mysubmission | 496 | 66 | 199 | 78-121 | 100% (g_iter0 2-0*) |
| 97 | addiesteward.NDeClaw | 476 | 70 | 190 | 72-118 | 100% (g_iter0 5-0*) |
| 98 | Yooncw0223.lec3player | 178 | 93 | 178 | 18-160 | 100% (g_iter0 5-0*) |
| 99 | andrewkbank.First | 153 | 93 | 147 | 17-130 | 100% (g_iter0 2-0*) |
