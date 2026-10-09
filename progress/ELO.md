# Ladder

7374 games (1620 ours, 5754 between field bots on the ladder replica), 7313 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_nav5 | 1964 +- 77 | 15 of 97 | 111 | 56-55 | 80.0% | 22.2% (vs 14) |
| c_nav4 | 1937 +- 52 | 17 of 97 | 221 | 108-113 | 78.7% | 21.8% (vs 15) |
| c_swarm1 | 1858 +- 48 | 21 of 97 | 271 | 128-143 | 74.7% | 20.6% (vs 18) |
| g_iter0 | 1813 +- 48 | 27 of 97 | 456 | 230-226 | 72.3% | 23.6% (vs 23) |
| c_line8a | 1812 +- 72 | 28 of 97 | 139 | 47-92 | 72.3% | 23.5% (vs 23) |
| c_line6 | 1778 +- 88 | 31 of 97 | 100 | 32-68 | 70.4% | 22.9% (vs 25) |
| c_line7m | 1766 +- 89 | 33 of 97 | 100 | 31-69 | 69.7% | 23.0% (vs 26) |
| c_line5 | 1730 +- 91 | 36 of 97 | 100 | 28-72 | 67.6% | 22.0% (vs 28) |
| c_line4 | 1692 +- 94 | 38 of 97 | 100 | 25-75 | 65.3% | 19.8% (vs 29) |
| examplefuncsplayer | 1262 +- 380 | 64 of 97 | 6 | 0-6 | 37.8% | 12.9% (vs 54) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_nav5), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2400 | 87 | 117 | 95-22 | 0% (g_iter0 0-36) |
| 2 | maxwelljones14.MPWorking | 2387 | 90 | 101 | 79-22 | 0% (g_iter0 0-5*) |
| 3 | vrangr1.AFinalsBot | 2343 | 87 | 190 | 169-21 | 0% (c_nav5 0-10*) |
| 4 | awesomelemonade.finalBot | 2340 | 80 | 191 | 163-28 | 10% (c_nav5 1-9*) |
| 5 | carlguo866.submit26_final | 2295 | 91 | 100 | 74-26 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2267 | 92 | 101 | 74-27 | 17% (c_swarm1 1-5*) |
| 7 | pranayagra.finalbotfinaltwo | 2229 | 79 | 127 | 89-38 | 7% (g_iter0 1-13*) |
| 8 | pranayagra.finalbotfinal | 2182 | 60 | 238 | 178-60 | 30% (c_nav5 3-7*) |
| 9 | georgezhang02.FB_ZZZ | 2162 | 82 | 110 | 75-35 | 0% (c_nav4 0-3*) |
| 10 | battlecode-archive.sprintBot | 2161 | 88 | 115 | 82-33 | 17% (c_nav4 2-10*) |
| 11 | jmerle.camel_case_v30_final | 2107 | 60 | 224 | 166-58 | 30% (c_nav5 3-7*) |
| 12 | CyrilSharma.finalBot | 2048 | 75 | 134 | 85-49 | 44% (c_nav4 4-5*) |
| 13 | ethanlabelle.dev | 2014 | 72 | 122 | 80-42 | 67% (c_nav4 2-1*) |
| 14 | NotLLeon.v7 | 1981 | 57 | 205 | 135-70 | 50% (c_nav5 5-5*) |
| 15 | **us:c_nav5** | 1964 | 77 | 111 | 56-55 |  |
| 16 | georgezhang02.CB_tuning2 | 1949 | 53 | 214 | 136-78 | 58% (c_nav5 7-5*) |
| 17 | **us:c_nav4** | 1937 | 52 | 221 | 108-113 |  |
| 18 | ethanlabelle.v19 | 1896 | 74 | 114 | 70-44 | 100% (c_nav5 3-0*) |
| 19 | britacatalin.FinalBot | 1886 | 52 | 216 | 129-87 | 62% (c_nav5 8-5*) |
| 20 | GabeG888.v8o1 | 1873 | 76 | 112 | 70-42 | 100% (c_nav5 3-0*) |
| 21 | **us:c_swarm1** | 1858 | 48 | 271 | 128-143 |  |
| 22 | GabeG888.v8 | 1853 | 66 | 130 | 75-55 | 67% (c_nav4 4-2*) |
| 23 | NicholasKelly15.gopher10 | 1838 | 82 | 104 | 65-39 | 78% (c_nav4 7-2*) |
| 24 | programjames.fourthbot | 1834 | 76 | 122 | 70-52 | 17% (c_nav4 1-5*) |
| 25 | VarunVejalla.karel | 1829 | 66 | 149 | 83-66 | 67% (c_nav4 6-3*) |
| 26 | DannyZhang686.pqual2 | 1823 | 72 | 134 | 76-58 | 67% (c_nav4 2-1*) |
| 27 | **us:g_iter0** | 1813 | 48 | 456 | 230-226 |  |
| 28 | **us:c_line8a** | 1812 | 72 | 139 | 47-92 |  |
| 29 | VarunVejalla.ali8 | 1788 | 81 | 107 | 64-43 | 67% (c_swarm1 6-3*) |
| 30 | louishu17.wouisv8 | 1783 | 71 | 146 | 82-64 | 33% (c_nav4 2-4*) |
| 31 | **us:c_line6** | 1778 | 88 | 100 | 32-68 |  |
| 32 | louishu17.louisv10 | 1771 | 72 | 130 | 73-57 | 100% (c_nav4 6-0*) |
| 33 | **us:c_line7m** | 1766 | 89 | 100 | 31-69 |  |
| 34 | reeceyang.v5anaconda | 1749 | 51 | 225 | 108-117 | 70% (c_nav5 7-3*) |
| 35 | battlecode-archive.Sprint1 | 1735 | 53 | 205 | 100-105 | 70% (c_nav5 7-3*) |
| 36 | **us:c_line5** | 1730 | 91 | 100 | 28-72 |  |
| 37 | SampleProvider.SPAARK | 1727 | 72 | 124 | 73-51 | 100% (g_iter0 2-0*) |
| 38 | **us:c_line4** | 1692 | 94 | 100 | 25-75 |  |
| 39 | ipince.bobby | 1649 | 75 | 122 | 68-54 | 67% (c_swarm1 2-1*) |
| 40 | legobridge.tacoplayer | 1624 | 69 | 152 | 80-72 | 85% (g_iter0 11-2*) |
| 41 | TheK098.qp1_7_sprint_1 | 1617 | 71 | 134 | 77-57 | 100% (c_swarm1 6-0*) |
| 42 | polyllc.poly | 1609 | 82 | 118 | 61-57 | 100% (g_iter0 2-0*) |
| 43 | SteamBlizzard.newVnewME | 1607 | 66 | 147 | 76-71 | 80% (g_iter0 4-1*) |
| 44 | toyat522.bot5a | 1589 | 71 | 131 | 68-63 | 80% (g_iter0 4-1*) |
| 45 | elgoldie.head_v5 | 1580 | 70 | 122 | 61-61 | 100% (g_iter0 2-0*) |
| 46 | ColtG5.rexv9 | 1563 | 68 | 142 | 72-70 | 100% (g_iter0 2-0*) |
| 47 | DukeBas._main | 1552 | 75 | 125 | 67-58 | 100% (g_iter0 2-0*) |
| 48 | BrysonJGalapon.friday | 1509 | 65 | 138 | 73-65 | 100% (g_iter0 2-0*) |
| 49 | beaverbois.USQualifiers | 1505 | 68 | 134 | 68-66 | 50% (g_iter0 1-1*) |
| 50 | kevinli405.maggi3_2 | 1495 | 70 | 145 | 72-73 | 100% (g_iter0 2-0*) |
| 51 | Nawlej.PoonPoon | 1475 | 76 | 122 | 59-63 | 100% (g_iter0 2-0*) |
| 52 | nail-e.Barry | 1465 | 69 | 127 | 68-59 | 100% (g_iter0 2-0*) |
| 53 | kevinli405.maggi3 | 1462 | 72 | 140 | 74-66 | 100% (g_iter0 5-0*) |
| 54 | yaonam.PoonPoonv4 | 1431 | 56 | 250 | 91-159 | 90% (c_nav5 9-1*) |
| 55 | aj-chau.attempt1 | 1411 | 77 | 119 | 59-60 | 100% (g_iter0 5-0*) |
| 56 | prisms-cs-club.prisms10 | 1407 | 68 | 140 | 68-72 | 100% (g_iter0 2-0*) |
| 57 | ipince.bobby_v2 | 1372 | 73 | 128 | 60-68 | 67% (c_swarm1 2-1*) |
| 58 | mama4294.currentPlayer | 1354 | 68 | 143 | 67-76 | 100% (g_iter0 2-0*) |
| 59 | andrewgopher.gopherbot | 1323 | 61 | 167 | 79-88 | 100% (g_iter0 2-0*) |
| 60 | BrysonJGalapon.aloha | 1316 | 68 | 131 | 63-68 | 100% (c_swarm1 3-0*) |
| 61 | bewuwy.deathbot4 | 1300 | 59 | 180 | 81-99 | 100% (g_iter0 2-0*) |
| 62 | JfeMak.realplayer2 | 1291 | 69 | 127 | 62-65 | 100% (g_iter0 2-0*) |
| 63 | SampleProvider.SPAARK_1_12_2023 | 1271 | 63 | 154 | 75-79 | 100% (c_swarm1 3-0*) |
| 64 | **us:examplefuncsplayer** | 1262 | 380 | 6 | 0-6 |  |
| 65 | SDainard-PDX.Team_Player | 1255 | 75 | 121 | 57-64 | 100% (g_iter0 2-0*) |
| 66 | NolanChai.nolan_1 | 1239 | 66 | 143 | 68-75 | 100% (g_iter0 2-0*) |
| 67 | PSUtblock.sprint_four_player | 1238 | 76 | 128 | 62-66 | 100% (g_iter0 2-0*) |
| 68 | Juanbri02.matfisplayer1 | 1233 | 65 | 147 | 68-79 | 100% (g_iter0 5-0*) |
| 69 | Nawlej.PoonPoonv3 | 1225 | 61 | 162 | 70-92 | 100% (g_iter0 5-0*) |
| 70 | andrewgopher.gopherbot1 | 1215 | 68 | 148 | 64-84 | 100% (g_iter0 2-0*) |
| 71 | jyorkio.elicompbot | 1211 | 68 | 129 | 60-69 | 100% (g_iter0 2-0*) |
| 72 | vontell.regressiongames | 1169 | 60 | 162 | 76-86 | 100% (g_iter0 5-0*) |
| 73 | JackLee9355.jackPlayer | 1166 | 65 | 158 | 65-93 | 100% (g_iter0 2-0*) |
| 74 | ax-95174.MPAction | 1150 | 68 | 133 | 60-73 | 100% (c_swarm1 3-0*) |
| 75 | SteamBlizzard.Block | 1140 | 64 | 168 | 66-102 | 100% (g_iter0 5-0*) |
| 76 | legobridge.kushalplayer | 1089 | 79 | 119 | 47-72 | 100% (g_iter0 2-0*) |
| 77 | michael-tyl.hqrewrite | 1070 | 64 | 155 | 70-85 | 100% (g_iter0 2-0*) |
| 78 | Patela171.Battlecode2023_Robot | 1066 | 69 | 143 | 59-84 | 100% (g_iter0 2-0*) |
| 79 | anicolao.submission | 1057 | 60 | 182 | 78-104 | 100% (g_iter0 2-0*) |
| 80 | nail-e.Dante | 1050 | 66 | 152 | 68-84 | 100% (g_iter0 2-0*) |
| 81 | Chahat08.toph | 1050 | 66 | 145 | 58-87 | 100% (g_iter0 2-0*) |
| 82 | mama4294.learningBot | 1050 | 70 | 147 | 60-87 | 100% (g_iter0 2-0*) |
| 83 | team-remember-to-hydrate.sprint_1 | 945 | 64 | 164 | 66-98 | 100% (g_iter0 2-0*) |
| 84 | addiesteward.elicompbot | 870 | 63 | 171 | 72-99 | 100% (g_iter0 5-0*) |
| 85 | Vinceyou1.Player1 | 863 | 67 | 151 | 56-95 | 100% (g_iter0 2-0*) |
| 86 | michael-tyl.cc_v0_5_0_6 | 863 | 56 | 208 | 82-126 | 100% (g_iter0 2-0*) |
| 87 | Swordman51.AdeptusAstartes2 | 844 | 61 | 170 | 69-101 | 100% (g_iter0 2-0*) |
| 88 | monmouth-college-cs.elicompbot | 824 | 62 | 185 | 75-110 | 100% (g_iter0 2-0*) |
| 89 | toyat522.bot5 | 808 | 70 | 153 | 56-97 | 100% (g_iter0 2-0*) |
| 90 | Chahat08.lazarus | 801 | 67 | 155 | 62-93 | 100% (g_iter0 2-0*) |
| 91 | anicolao.jumbled | 716 | 58 | 210 | 84-126 | 100% (g_iter0 5-0*) |
| 92 | ShatterXD.SRNNbot | 707 | 71 | 146 | 57-89 | 100% (g_iter0 2-0*) |
| 93 | NotLLeon.player | 539 | 69 | 172 | 65-107 | 100% (g_iter0 2-0*) |
| 94 | CodeClash-ai.mysubmission | 533 | 70 | 181 | 71-110 | 100% (g_iter0 2-0*) |
| 95 | addiesteward.NDeClaw | 512 | 74 | 172 | 61-111 | 100% (g_iter0 5-0*) |
| 96 | andrewkbank.First | 207 | 100 | 128 | 15-113 | 100% (g_iter0 2-0*) |
| 97 | Yooncw0223.lec3player | 195 | 102 | 169 | 14-155 | 100% (g_iter0 5-0*) |
