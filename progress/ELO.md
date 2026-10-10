# Ladder

8792 games (1922 ours, 6870 between field bots on the ladder replica), 8716 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_anc3 | 2011 +- 63 | 13 of 99 | 157 | 84-73 | 82.8% | 24.7% (vs 12) |
| c_nav5 | 1950 +- 71 | 16 of 99 | 126 | 61-65 | 80.1% | 23.0% (vs 14) |
| c_nav6 | 1938 +- 71 | 18 of 99 | 129 | 58-71 | 79.5% | 23.7% (vs 15) |
| c_nav4 | 1918 +- 52 | 19 of 99 | 221 | 108-113 | 78.5% | 21.9% (vs 15) |
| c_swarm1 | 1844 +- 48 | 23 of 99 | 271 | 128-143 | 74.8% | 21.3% (vs 18) |
| g_iter0 | 1801 +- 48 | 30 of 99 | 456 | 230-226 | 72.4% | 25.4% (vs 24) |
| c_line8a | 1799 +- 71 | 31 of 99 | 139 | 47-92 | 72.3% | 25.2% (vs 24) |
| c_line6 | 1766 +- 88 | 32 of 99 | 100 | 32-68 | 70.5% | 22.3% (vs 24) |
| c_line7m | 1754 +- 88 | 35 of 99 | 100 | 31-69 | 69.8% | 23.5% (vs 26) |
| c_line5 | 1718 +- 90 | 39 of 99 | 100 | 28-72 | 67.7% | 23.3% (vs 29) |
| c_line4 | 1680 +- 93 | 40 of 99 | 100 | 25-75 | 65.5% | 20.1% (vs 29) |
| examplefuncsplayer | 1243 +- 380 | 67 of 99 | 6 | 0-6 | 37.7% | 13.1% (vs 55) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_anc3), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2387 | 78 | 134 | 106-28 | 0% (g_iter0 0-36) |
| 2 | maxwelljones14.MPWorking | 2357 | 85 | 107 | 81-26 | 0% (g_iter0 0-5*) |
| 3 | awesomelemonade.finalBot | 2331 | 71 | 225 | 189-36 | 20% (c_anc3 2-8*) |
| 4 | vrangr1.AFinalsBot | 2311 | 74 | 222 | 192-30 | 10% (c_anc3 1-9*) |
| 5 | carlguo866.submit26_final | 2277 | 79 | 121 | 86-35 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2250 | 82 | 119 | 85-34 | 0% (c_anc3 0-3*) |
| 7 | pranayagra.finalbotfinaltwo | 2195 | 72 | 142 | 96-46 | 33% (c_anc3 2-4*) |
| 8 | pranayagra.finalbotfinal | 2174 | 54 | 279 | 205-74 | 40% (c_anc3 4-6*) |
| 9 | georgezhang02.FB_ZZZ | 2154 | 70 | 140 | 93-47 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2124 | 78 | 133 | 92-41 | 33% (c_anc3 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2090 | 53 | 259 | 187-72 | 38% (c_anc3 5-8*) |
| 12 | CyrilSharma.finalBot | 2016 | 63 | 170 | 102-68 | 42% (c_anc3 5-7*) |
| 13 | **us:c_anc3** | 2011 | 63 | 157 | 84-73 |  |
| 14 | ethanlabelle.dev | 1990 | 65 | 143 | 90-53 | 33% (c_anc3 2-4*) |
| 15 | NotLLeon.v7 | 1963 | 49 | 257 | 160-97 | 69% (c_anc3 11-5*) |
| 16 | **us:c_nav5** | 1950 | 71 | 126 | 61-65 |  |
| 17 | georgezhang02.CB_tuning2 | 1938 | 49 | 246 | 151-95 | 46% (c_anc3 6-7*) |
| 18 | **us:c_nav6** | 1938 | 71 | 129 | 58-71 |  |
| 19 | **us:c_nav4** | 1918 | 52 | 221 | 108-113 |  |
| 20 | britacatalin.FinalBot | 1875 | 47 | 254 | 147-107 | 85% (c_anc3 11-2*) |
| 21 | ethanlabelle.v19 | 1862 | 69 | 129 | 76-53 | 100% (c_nav5 3-0*) |
| 22 | GabeG888.v8 | 1850 | 61 | 148 | 86-62 | 67% (c_nav4 4-2*) |
| 23 | **us:c_swarm1** | 1844 | 48 | 271 | 128-143 |  |
| 24 | GabeG888.v8o1 | 1828 | 67 | 136 | 82-54 | 100% (c_nav5 3-0*) |
| 25 | DannyZhang686.pqual2 | 1821 | 60 | 173 | 96-77 | 83% (c_anc3 5-1*) |
| 26 | programjames.fourthbot | 1812 | 70 | 134 | 75-59 | 17% (c_nav4 1-5*) |
| 27 | VarunVejalla.karel | 1811 | 62 | 164 | 90-74 | 67% (c_nav4 6-3*) |
| 28 | NicholasKelly15.gopher10 | 1807 | 75 | 116 | 69-47 | 78% (c_nav4 7-2*) |
| 29 | VarunVejalla.ali8 | 1803 | 66 | 143 | 85-58 | 67% (c_swarm1 6-3*) |
| 30 | **us:g_iter0** | 1801 | 48 | 456 | 230-226 |  |
| 31 | **us:c_line8a** | 1799 | 71 | 139 | 47-92 |  |
| 32 | **us:c_line6** | 1766 | 88 | 100 | 32-68 |  |
| 33 | louishu17.louisv10 | 1764 | 67 | 145 | 83-62 | 100% (c_nav4 6-0*) |
| 34 | louishu17.wouisv8 | 1763 | 65 | 164 | 91-73 | 33% (c_nav4 2-4*) |
| 35 | **us:c_line7m** | 1754 | 88 | 100 | 31-69 |  |
| 36 | SampleProvider.SPAARK | 1738 | 67 | 142 | 82-60 | 33% (c_anc3 1-2*) |
| 37 | reeceyang.v5anaconda | 1737 | 47 | 263 | 122-141 | 90% (c_anc3 9-1*) |
| 38 | battlecode-archive.Sprint1 | 1726 | 49 | 243 | 114-129 | 100% (c_anc3 10-0*) |
| 39 | **us:c_line5** | 1718 | 90 | 100 | 28-72 |  |
| 40 | **us:c_line4** | 1680 | 93 | 100 | 25-75 |  |
| 41 | ipince.bobby | 1629 | 70 | 134 | 73-61 | 67% (c_swarm1 2-1*) |
| 42 | legobridge.tacoplayer | 1625 | 63 | 173 | 94-79 | 85% (g_iter0 11-2*) |
| 43 | polyllc.poly | 1620 | 73 | 139 | 73-66 | 100% (g_iter0 2-0*) |
| 44 | SteamBlizzard.newVnewME | 1604 | 60 | 171 | 86-85 | 80% (g_iter0 4-1*) |
| 45 | TheK098.qp1_7_sprint_1 | 1598 | 63 | 164 | 89-75 | 100% (c_swarm1 6-0*) |
| 46 | elgoldie.head_v5 | 1580 | 62 | 149 | 77-72 | 100% (g_iter0 2-0*) |
| 47 | toyat522.bot5a | 1577 | 63 | 155 | 81-74 | 80% (g_iter0 4-1*) |
| 48 | DukeBas._main | 1554 | 63 | 162 | 87-75 | 100% (g_iter0 2-0*) |
| 49 | ColtG5.rexv9 | 1540 | 60 | 170 | 83-87 | 100% (g_iter0 2-0*) |
| 50 | beaverbois.USQualifiers | 1488 | 62 | 155 | 81-74 | 50% (g_iter0 1-1*) |
| 51 | kevinli405.maggi3_2 | 1486 | 62 | 172 | 88-84 | 100% (g_iter0 2-0*) |
| 52 | BrysonJGalapon.friday | 1477 | 59 | 162 | 83-79 | 100% (g_iter0 2-0*) |
| 53 | nail-e.Barry | 1461 | 63 | 148 | 78-70 | 100% (g_iter0 2-0*) |
| 54 | Nawlej.PoonPoon | 1443 | 69 | 143 | 67-76 | 100% (g_iter0 2-0*) |
| 55 | aj-chau.attempt1 | 1439 | 65 | 152 | 81-71 | 100% (g_iter0 5-0*) |
| 56 | kevinli405.maggi3 | 1427 | 67 | 158 | 81-77 | 100% (g_iter0 5-0*) |
| 57 | yaonam.PoonPoonv4 | 1425 | 51 | 297 | 108-189 | 90% (c_anc3 9-1*) |
| 58 | prisms-cs-club.prisms10 | 1402 | 64 | 158 | 75-83 | 100% (g_iter0 2-0*) |
| 59 | mama4294.currentPlayer | 1369 | 59 | 176 | 89-87 | 100% (g_iter0 2-0*) |
| 60 | ipince.bobby_v2 | 1358 | 66 | 152 | 74-78 | 67% (c_swarm1 2-1*) |
| 61 | BrysonJGalapon.aloha | 1308 | 58 | 170 | 85-85 | 100% (c_swarm1 3-0*) |
| 62 | andrewgopher.gopherbot | 1301 | 56 | 194 | 90-104 | 100% (g_iter0 2-0*) |
| 63 | JfeMak.realplayer2 | 1298 | 63 | 148 | 75-73 | 100% (g_iter0 2-0*) |
| 64 | bewuwy.deathbot4 | 1289 | 54 | 208 | 95-113 | 100% (g_iter0 2-0*) |
| 65 | SampleProvider.SPAARK_1_12_2023 | 1250 | 54 | 205 | 96-109 | 100% (c_swarm1 3-0*) |
| 66 | PSUtblock.sprint_four_player | 1245 | 67 | 155 | 76-79 | 100% (g_iter0 2-0*) |
| 67 | **us:examplefuncsplayer** | 1243 | 380 | 6 | 0-6 |  |
| 68 | SDainard-PDX.Team_Player | 1234 | 65 | 152 | 72-80 | 100% (g_iter0 2-0*) |
| 69 | NolanChai.nolan_1 | 1219 | 62 | 161 | 77-84 | 100% (g_iter0 2-0*) |
| 70 | Nawlej.PoonPoonv3 | 1212 | 55 | 194 | 90-104 | 100% (g_iter0 5-0*) |
| 71 | Juanbri02.matfisplayer1 | 1207 | 56 | 189 | 85-104 | 100% (g_iter0 5-0*) |
| 72 | jyorkio.elicompbot | 1183 | 60 | 162 | 76-86 | 100% (g_iter0 2-0*) |
| 73 | andrewgopher.gopherbot1 | 1175 | 61 | 175 | 76-99 | 100% (g_iter0 2-0*) |
| 74 | vontell.regressiongames | 1145 | 51 | 212 | 101-111 | 100% (g_iter0 5-0*) |
| 75 | JackLee9355.jackPlayer | 1116 | 58 | 194 | 83-111 | 100% (g_iter0 2-0*) |
| 76 | SteamBlizzard.Block | 1110 | 54 | 216 | 93-123 | 100% (g_iter0 5-0*) |
| 77 | ax-95174.MPAction | 1101 | 59 | 172 | 76-96 | 100% (c_swarm1 3-0*) |
| 78 | Patela171.Battlecode2023_Robot | 1074 | 57 | 194 | 88-106 | 100% (g_iter0 2-0*) |
| 79 | legobridge.kushalplayer | 1071 | 69 | 146 | 61-85 | 100% (g_iter0 2-0*) |
| 80 | michael-tyl.hqrewrite | 1044 | 58 | 182 | 84-98 | 100% (g_iter0 2-0*) |
| 81 | nail-e.Dante | 1021 | 59 | 182 | 84-98 | 100% (g_iter0 2-0*) |
| 82 | Chahat08.toph | 1018 | 60 | 172 | 73-99 | 100% (g_iter0 2-0*) |
| 83 | anicolao.submission | 993 | 54 | 223 | 96-127 | 100% (g_iter0 2-0*) |
| 84 | mama4294.learningBot | 987 | 62 | 176 | 71-105 | 100% (g_iter0 2-0*) |
| 85 | team-remember-to-hydrate.sprint_1 | 926 | 57 | 203 | 83-120 | 100% (g_iter0 2-0*) |
| 86 | Vinceyou1.Player1 | 851 | 62 | 172 | 69-103 | 100% (g_iter0 2-0*) |
| 87 | addiesteward.elicompbot | 840 | 56 | 207 | 88-119 | 100% (g_iter0 5-0*) |
| 88 | michael-tyl.cc_v0_5_0_6 | 819 | 51 | 246 | 102-144 | 100% (g_iter0 2-0*) |
| 89 | Swordman51.AdeptusAstartes2 | 793 | 54 | 209 | 85-124 | 100% (g_iter0 2-0*) |
| 90 | monmouth-college-cs.elicompbot | 792 | 57 | 208 | 85-123 | 100% (g_iter0 2-0*) |
| 91 | Chahat08.lazarus | 780 | 58 | 193 | 79-114 | 100% (g_iter0 2-0*) |
| 92 | toyat522.bot5 | 779 | 59 | 200 | 81-119 | 100% (g_iter0 2-0*) |
| 93 | anicolao.jumbled | 680 | 53 | 241 | 100-141 | 100% (g_iter0 5-0*) |
| 94 | ShatterXD.SRNNbot | 662 | 62 | 180 | 70-110 | 100% (g_iter0 2-0*) |
| 95 | NotLLeon.player | 504 | 64 | 200 | 82-118 | 100% (g_iter0 2-0*) |
| 96 | CodeClash-ai.mysubmission | 485 | 64 | 207 | 82-125 | 100% (g_iter0 2-0*) |
| 97 | addiesteward.NDeClaw | 458 | 68 | 201 | 78-123 | 100% (g_iter0 5-0*) |
| 98 | Yooncw0223.lec3player | 153 | 92 | 187 | 18-169 | 100% (g_iter0 5-0*) |
| 99 | andrewkbank.First | 148 | 91 | 150 | 18-132 | 100% (g_iter0 2-0*) |
