# Ladder

7750 games (1744 ours, 6006 between field bots on the ladder replica), 7688 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_nav5 | 1958 +- 71 | 15 of 98 | 126 | 61-65 | 80.1% | 22.9% (vs 14) |
| c_nav6 | 1946 +- 78 | 16 of 98 | 109 | 51-58 | 79.5% | 21.7% (vs 14) |
| c_nav4 | 1927 +- 52 | 18 of 98 | 221 | 108-113 | 78.7% | 22.0% (vs 15) |
| c_swarm1 | 1851 +- 48 | 22 of 98 | 271 | 128-143 | 74.8% | 21.1% (vs 18) |
| g_iter0 | 1806 +- 48 | 28 of 98 | 456 | 230-226 | 72.4% | 24.0% (vs 23) |
| c_line8a | 1805 +- 71 | 29 of 98 | 139 | 47-92 | 72.3% | 23.9% (vs 23) |
| c_line6 | 1772 +- 88 | 32 of 98 | 100 | 32-68 | 70.5% | 23.3% (vs 25) |
| c_line7m | 1761 +- 88 | 34 of 98 | 100 | 31-69 | 69.8% | 23.4% (vs 26) |
| c_line5 | 1725 +- 91 | 38 of 98 | 100 | 28-72 | 67.7% | 23.2% (vs 29) |
| c_line4 | 1687 +- 93 | 39 of 98 | 100 | 25-75 | 65.5% | 20.0% (vs 29) |
| examplefuncsplayer | 1255 +- 380 | 65 of 98 | 6 | 0-6 | 37.8% | 12.8% (vs 54) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_nav6), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2388 | 84 | 122 | 98-24 | 0% (g_iter0 0-36) |
| 2 | maxwelljones14.MPWorking | 2377 | 90 | 101 | 79-22 | 0% (g_iter0 0-5*) |
| 3 | awesomelemonade.finalBot | 2340 | 78 | 203 | 174-29 | 10% (c_nav6 1-9*) |
| 4 | vrangr1.AFinalsBot | 2339 | 84 | 203 | 181-22 | 0% (c_nav6 0-10*) |
| 5 | carlguo866.submit26_final | 2292 | 88 | 106 | 79-27 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2247 | 90 | 104 | 74-30 | 17% (c_swarm1 1-5*) |
| 7 | pranayagra.finalbotfinaltwo | 2218 | 79 | 127 | 89-38 | 7% (g_iter0 1-13*) |
| 8 | pranayagra.finalbotfinal | 2170 | 56 | 257 | 190-67 | 30% (c_nav6 3-7*) |
| 9 | georgezhang02.FB_ZZZ | 2141 | 75 | 125 | 83-42 | 33% (c_nav6 2-4*) |
| 10 | battlecode-archive.sprintBot | 2129 | 84 | 121 | 84-37 | 67% (c_nav5 2-1*) |
| 11 | jmerle.camel_case_v30_final | 2103 | 57 | 240 | 177-63 | 30% (c_nav6 3-7*) |
| 12 | CyrilSharma.finalBot | 2039 | 71 | 143 | 90-53 | 50% (c_nav5 3-3*) |
| 13 | ethanlabelle.dev | 1999 | 70 | 128 | 83-45 | 100% (c_nav6 3-0*) |
| 14 | NotLLeon.v7 | 1973 | 54 | 218 | 141-77 | 50% (c_nav6 5-5*) |
| 15 | **us:c_nav5** | 1958 | 71 | 126 | 61-65 |  |
| 16 | **us:c_nav6** | 1946 | 78 | 109 | 51-58 |  |
| 17 | georgezhang02.CB_tuning2 | 1937 | 52 | 224 | 140-84 | 60% (c_nav6 6-4*) |
| 18 | **us:c_nav4** | 1927 | 52 | 221 | 108-113 |  |
| 19 | ethanlabelle.v19 | 1879 | 73 | 117 | 70-47 | 100% (c_nav5 3-0*) |
| 20 | britacatalin.FinalBot | 1878 | 51 | 226 | 133-93 | 60% (c_nav6 6-4*) |
| 21 | GabeG888.v8o1 | 1853 | 73 | 118 | 72-46 | 100% (c_nav5 3-0*) |
| 22 | **us:c_swarm1** | 1851 | 48 | 271 | 128-143 |  |
| 23 | GabeG888.v8 | 1844 | 66 | 130 | 75-55 | 67% (c_nav4 4-2*) |
| 24 | NicholasKelly15.gopher10 | 1831 | 82 | 104 | 65-39 | 78% (c_nav4 7-2*) |
| 25 | programjames.fourthbot | 1827 | 76 | 122 | 70-52 | 17% (c_nav4 1-5*) |
| 26 | VarunVejalla.karel | 1819 | 65 | 152 | 84-68 | 67% (c_nav4 6-3*) |
| 27 | DannyZhang686.pqual2 | 1816 | 68 | 143 | 81-62 | 67% (c_nav4 2-1*) |
| 28 | **us:g_iter0** | 1806 | 48 | 456 | 230-226 |  |
| 29 | **us:c_line8a** | 1805 | 71 | 139 | 47-92 |  |
| 30 | VarunVejalla.ali8 | 1789 | 78 | 113 | 68-45 | 67% (c_swarm1 6-3*) |
| 31 | louishu17.wouisv8 | 1773 | 70 | 149 | 83-66 | 33% (c_nav4 2-4*) |
| 32 | **us:c_line6** | 1772 | 88 | 100 | 32-68 |  |
| 33 | louishu17.louisv10 | 1771 | 71 | 133 | 76-57 | 100% (c_nav4 6-0*) |
| 34 | **us:c_line7m** | 1761 | 88 | 100 | 31-69 |  |
| 35 | reeceyang.v5anaconda | 1747 | 49 | 241 | 115-126 | 70% (c_nav6 7-3*) |
| 36 | battlecode-archive.Sprint1 | 1736 | 51 | 221 | 108-113 | 60% (c_nav6 6-4*) |
| 37 | SampleProvider.SPAARK | 1735 | 70 | 130 | 77-53 | 100% (g_iter0 2-0*) |
| 38 | **us:c_line5** | 1725 | 91 | 100 | 28-72 |  |
| 39 | **us:c_line4** | 1687 | 93 | 100 | 25-75 |  |
| 40 | ipince.bobby | 1644 | 75 | 122 | 68-54 | 67% (c_swarm1 2-1*) |
| 41 | legobridge.tacoplayer | 1618 | 67 | 158 | 84-74 | 85% (g_iter0 11-2*) |
| 42 | TheK098.qp1_7_sprint_1 | 1617 | 70 | 137 | 79-58 | 100% (c_swarm1 6-0*) |
| 43 | polyllc.poly | 1605 | 82 | 118 | 61-57 | 100% (g_iter0 2-0*) |
| 44 | SteamBlizzard.newVnewME | 1596 | 65 | 150 | 76-74 | 80% (g_iter0 4-1*) |
| 45 | toyat522.bot5a | 1583 | 71 | 131 | 68-63 | 80% (g_iter0 4-1*) |
| 46 | elgoldie.head_v5 | 1574 | 70 | 122 | 61-61 | 100% (g_iter0 2-0*) |
| 47 | ColtG5.rexv9 | 1557 | 68 | 142 | 72-70 | 100% (g_iter0 2-0*) |
| 48 | DukeBas._main | 1554 | 70 | 140 | 75-65 | 100% (g_iter0 2-0*) |
| 49 | BrysonJGalapon.friday | 1496 | 64 | 144 | 75-69 | 100% (g_iter0 2-0*) |
| 50 | beaverbois.USQualifiers | 1489 | 66 | 140 | 70-70 | 50% (g_iter0 1-1*) |
| 51 | kevinli405.maggi3_2 | 1479 | 68 | 151 | 74-77 | 100% (g_iter0 2-0*) |
| 52 | Nawlej.PoonPoon | 1465 | 75 | 125 | 61-64 | 100% (g_iter0 2-0*) |
| 53 | nail-e.Barry | 1465 | 68 | 130 | 70-60 | 100% (g_iter0 2-0*) |
| 54 | kevinli405.maggi3 | 1451 | 70 | 146 | 76-70 | 100% (g_iter0 5-0*) |
| 55 | aj-chau.attempt1 | 1431 | 71 | 134 | 70-64 | 100% (g_iter0 5-0*) |
| 56 | yaonam.PoonPoonv4 | 1428 | 54 | 269 | 96-173 | 90% (c_nav6 9-1*) |
| 57 | prisms-cs-club.prisms10 | 1402 | 68 | 140 | 68-72 | 100% (g_iter0 2-0*) |
| 58 | ipince.bobby_v2 | 1368 | 69 | 140 | 68-72 | 67% (c_swarm1 2-1*) |
| 59 | mama4294.currentPlayer | 1358 | 66 | 149 | 71-78 | 100% (g_iter0 2-0*) |
| 60 | andrewgopher.gopherbot | 1317 | 59 | 176 | 85-91 | 100% (g_iter0 2-0*) |
| 61 | BrysonJGalapon.aloha | 1301 | 67 | 134 | 63-71 | 100% (c_swarm1 3-0*) |
| 62 | bewuwy.deathbot4 | 1293 | 58 | 183 | 82-101 | 100% (g_iter0 2-0*) |
| 63 | JfeMak.realplayer2 | 1283 | 68 | 130 | 63-67 | 100% (g_iter0 2-0*) |
| 64 | PSUtblock.sprint_four_player | 1255 | 73 | 134 | 68-66 | 100% (g_iter0 2-0*) |
| 65 | **us:examplefuncsplayer** | 1255 | 380 | 6 | 0-6 |  |
| 66 | SampleProvider.SPAARK_1_12_2023 | 1254 | 61 | 163 | 76-87 | 100% (c_swarm1 3-0*) |
| 67 | SDainard-PDX.Team_Player | 1252 | 73 | 127 | 61-66 | 100% (g_iter0 2-0*) |
| 68 | Juanbri02.matfisplayer1 | 1236 | 63 | 156 | 74-82 | 100% (g_iter0 5-0*) |
| 69 | NolanChai.nolan_1 | 1225 | 65 | 149 | 70-79 | 100% (g_iter0 2-0*) |
| 70 | Nawlej.PoonPoonv3 | 1210 | 59 | 174 | 76-98 | 100% (g_iter0 5-0*) |
| 71 | andrewgopher.gopherbot1 | 1196 | 67 | 151 | 64-87 | 100% (g_iter0 2-0*) |
| 72 | jyorkio.elicompbot | 1193 | 67 | 135 | 62-73 | 100% (g_iter0 2-0*) |
| 73 | vontell.regressiongames | 1163 | 57 | 177 | 85-92 | 100% (g_iter0 5-0*) |
| 74 | JackLee9355.jackPlayer | 1161 | 64 | 164 | 70-94 | 100% (g_iter0 2-0*) |
| 75 | ax-95174.MPAction | 1133 | 65 | 145 | 64-81 | 100% (c_swarm1 3-0*) |
| 76 | SteamBlizzard.Block | 1120 | 60 | 183 | 73-110 | 100% (g_iter0 5-0*) |
| 77 | legobridge.kushalplayer | 1090 | 75 | 128 | 53-75 | 100% (g_iter0 2-0*) |
| 78 | Patela171.Battlecode2023_Robot | 1070 | 63 | 164 | 70-94 | 100% (g_iter0 2-0*) |
| 79 | michael-tyl.hqrewrite | 1057 | 63 | 161 | 72-89 | 100% (g_iter0 2-0*) |
| 80 | Chahat08.toph | 1049 | 64 | 154 | 66-88 | 100% (g_iter0 2-0*) |
| 81 | anicolao.submission | 1047 | 59 | 188 | 82-106 | 100% (g_iter0 2-0*) |
| 82 | nail-e.Dante | 1028 | 64 | 158 | 69-89 | 100% (g_iter0 2-0*) |
| 83 | mama4294.learningBot | 1016 | 67 | 156 | 61-95 | 100% (g_iter0 2-0*) |
| 84 | team-remember-to-hydrate.sprint_1 | 924 | 63 | 173 | 69-104 | 100% (g_iter0 2-0*) |
| 85 | Vinceyou1.Player1 | 856 | 66 | 157 | 61-96 | 100% (g_iter0 2-0*) |
| 86 | michael-tyl.cc_v0_5_0_6 | 849 | 56 | 211 | 85-126 | 100% (g_iter0 2-0*) |
| 87 | addiesteward.elicompbot | 845 | 62 | 177 | 72-105 | 100% (g_iter0 5-0*) |
| 88 | Swordman51.AdeptusAstartes2 | 818 | 57 | 191 | 80-111 | 100% (g_iter0 2-0*) |
| 89 | monmouth-college-cs.elicompbot | 806 | 62 | 185 | 75-110 | 100% (g_iter0 2-0*) |
| 90 | Chahat08.lazarus | 785 | 66 | 161 | 65-96 | 100% (g_iter0 2-0*) |
| 91 | toyat522.bot5 | 778 | 65 | 171 | 64-107 | 100% (g_iter0 2-0*) |
| 92 | anicolao.jumbled | 695 | 57 | 216 | 86-130 | 100% (g_iter0 5-0*) |
| 93 | ShatterXD.SRNNbot | 678 | 71 | 149 | 57-92 | 100% (g_iter0 2-0*) |
| 94 | CodeClash-ai.mysubmission | 519 | 68 | 190 | 77-113 | 100% (g_iter0 2-0*) |
| 95 | NotLLeon.player | 510 | 68 | 178 | 68-110 | 100% (g_iter0 2-0*) |
| 96 | addiesteward.NDeClaw | 491 | 72 | 181 | 67-114 | 100% (g_iter0 5-0*) |
| 97 | Yooncw0223.lec3player | 175 | 99 | 175 | 15-160 | 100% (g_iter0 5-0*) |
| 98 | andrewkbank.First | 174 | 99 | 134 | 15-119 | 100% (g_iter0 2-0*) |
