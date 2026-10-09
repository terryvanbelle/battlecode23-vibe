# Ladder

6251 games (1421 ours, 4830 between field bots on the ladder replica), 6212 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_nav4 | 1970 +- 69 | 15 of 96 | 136 | 65-71 | 80.1% | 22.4% (vs 14) |
| c_swarm1 | 1861 +- 48 | 21 of 96 | 271 | 128-143 | 74.7% | 21.7% (vs 19) |
| c_line8a | 1818 +- 72 | 26 of 96 | 139 | 47-92 | 72.4% | 23.7% (vs 23) |
| g_iter0 | 1818 +- 48 | 27 of 96 | 456 | 230-226 | 72.4% | 23.7% (vs 23) |
| c_line6 | 1784 +- 89 | 29 of 96 | 100 | 32-68 | 70.5% | 21.9% (vs 24) |
| c_line7m | 1772 +- 89 | 31 of 96 | 100 | 31-69 | 69.8% | 22.1% (vs 25) |
| c_line5 | 1735 +- 92 | 35 of 96 | 100 | 28-72 | 67.7% | 22.2% (vs 28) |
| c_line4 | 1696 +- 95 | 37 of 96 | 100 | 25-75 | 65.4% | 20.0% (vs 29) |
| examplefuncsplayer | 1254 +- 380 | 64 of 96 | 6 | 0-6 | 36.4% | 12.8% (vs 55) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2419 | 92 | 111 | 92-19 | 0% (g_iter0 0-36) |
| 2 | maxwelljones14.MPWorking | 2388 | 100 | 89 | 71-18 | 0% (g_iter0 0-5*) |
| 3 | awesomelemonade.finalBot | 2367 | 92 | 169 | 148-21 | 0% (g_iter0 0-15*) |
| 4 | carlguo866.submit26_final | 2346 | 108 | 82 | 64-18 | 0% (g_iter0 0-2*) |
| 5 | vrangr1.AFinalsBot | 2345 | 99 | 168 | 153-15 | 7% (g_iter0 1-14*) |
| 6 | AnOvercookedFork.quals | 2279 | 102 | 92 | 71-21 | 20% (g_iter0 1-4*) |
| 7 | pranayagra.finalbotfinaltwo | 2237 | 89 | 109 | 79-30 | 7% (g_iter0 1-13*) |
| 8 | battlecode-archive.sprintBot | 2195 | 113 | 88 | 68-20 | 0% (g_iter0 0-2*) |
| 9 | pranayagra.finalbotfinal | 2186 | 63 | 220 | 165-55 | 13% (g_iter0 6-39) |
| 10 | georgezhang02.FB_ZZZ | 2167 | 90 | 98 | 69-29 | 0% (g_iter0 0-2*) |
| 11 | jmerle.camel_case_v30_final | 2122 | 64 | 202 | 152-50 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2012 | 80 | 102 | 67-35 | 0% (g_iter0 0-2*) |
| 13 | CyrilSharma.finalBot | 1997 | 91 | 104 | 66-38 | 0% (g_iter0 0-2*) |
| 14 | NotLLeon.v7 | 1984 | 62 | 177 | 120-57 | 17% (g_iter0 2-10*) |
| 15 | **us:c_nav4** | 1970 | 69 | 136 | 65-71 |  |
| 16 | georgezhang02.CB_tuning2 | 1966 | 59 | 185 | 123-62 | 7% (g_iter0 1-14*) |
| 17 | GabeG888.v8o1 | 1907 | 94 | 85 | 59-26 | 0% (g_iter0 0-2*) |
| 18 | ethanlabelle.v19 | 1906 | 86 | 93 | 61-32 | 50% (g_iter0 1-1*) |
| 19 | britacatalin.FinalBot | 1902 | 60 | 174 | 110-64 | 42% (g_iter0 5-7*) |
| 20 | GabeG888.v8 | 1865 | 75 | 107 | 64-43 | 50% (g_iter0 1-1*) |
| 21 | **us:c_swarm1** | 1861 | 48 | 271 | 128-143 |  |
| 22 | VarunVejalla.karel | 1835 | 76 | 122 | 70-52 | 50% (g_iter0 4-4*) |
| 23 | NicholasKelly15.gopher10 | 1822 | 91 | 89 | 57-32 | 100% (g_iter0 2-0*) |
| 24 | DannyZhang686.pqual2 | 1820 | 78 | 119 | 68-51 | 29% (g_iter0 4-10*) |
| 25 | programjames.fourthbot | 1819 | 83 | 104 | 62-42 | 100% (g_iter0 2-0*) |
| 26 | **us:c_line8a** | 1818 | 72 | 139 | 47-92 |  |
| 27 | **us:g_iter0** | 1818 | 48 | 456 | 230-226 |  |
| 28 | VarunVejalla.ali8 | 1798 | 87 | 98 | 61-37 | 50% (g_iter0 1-1*) |
| 29 | **us:c_line6** | 1784 | 89 | 100 | 32-68 |  |
| 30 | louishu17.louisv10 | 1775 | 81 | 109 | 63-46 | 100% (g_iter0 2-0*) |
| 31 | **us:c_line7m** | 1772 | 89 | 100 | 31-69 |  |
| 32 | louishu17.wouisv8 | 1771 | 81 | 122 | 73-49 | 50% (g_iter0 5-5*) |
| 33 | reeceyang.v5anaconda | 1744 | 56 | 191 | 95-96 | 58% (g_iter0 7-5*) |
| 34 | battlecode-archive.Sprint1 | 1739 | 57 | 177 | 88-89 | 58% (g_iter0 7-5*) |
| 35 | **us:c_line5** | 1735 | 92 | 100 | 28-72 |  |
| 36 | SampleProvider.SPAARK | 1713 | 79 | 106 | 61-45 | 100% (g_iter0 2-0*) |
| 37 | **us:c_line4** | 1696 | 95 | 100 | 25-75 |  |
| 38 | ipince.bobby | 1666 | 88 | 98 | 56-42 | 100% (g_iter0 2-0*) |
| 39 | legobridge.tacoplayer | 1643 | 76 | 134 | 74-60 | 85% (g_iter0 11-2*) |
| 40 | polyllc.poly | 1617 | 91 | 103 | 53-50 | 100% (g_iter0 2-0*) |
| 41 | toyat522.bot5a | 1596 | 78 | 113 | 59-54 | 80% (g_iter0 4-1*) |
| 42 | SteamBlizzard.newVnewME | 1588 | 72 | 129 | 63-66 | 80% (g_iter0 4-1*) |
| 43 | TheK098.qp1_7_sprint_1 | 1581 | 81 | 110 | 62-48 | 100% (g_iter0 2-0*) |
| 44 | elgoldie.head_v5 | 1579 | 74 | 110 | 54-56 | 100% (g_iter0 2-0*) |
| 45 | ColtG5.rexv9 | 1572 | 75 | 121 | 60-61 | 100% (g_iter0 2-0*) |
| 46 | DukeBas._main | 1565 | 85 | 104 | 55-49 | 100% (g_iter0 2-0*) |
| 47 | beaverbois.USQualifiers | 1527 | 79 | 104 | 53-51 | 50% (g_iter0 1-1*) |
| 48 | kevinli405.maggi3_2 | 1517 | 81 | 118 | 59-59 | 100% (g_iter0 2-0*) |
| 49 | BrysonJGalapon.friday | 1495 | 71 | 120 | 61-59 | 100% (g_iter0 2-0*) |
| 50 | Nawlej.PoonPoon | 1487 | 84 | 104 | 54-50 | 100% (g_iter0 2-0*) |
| 51 | nail-e.Barry | 1463 | 79 | 103 | 54-49 | 100% (g_iter0 2-0*) |
| 52 | kevinli405.maggi3 | 1444 | 77 | 125 | 66-59 | 100% (g_iter0 5-0*) |
| 53 | yaonam.PoonPoonv4 | 1421 | 60 | 222 | 79-143 | 87% (g_iter0 13-2*) |
| 54 | aj-chau.attempt1 | 1418 | 86 | 101 | 52-49 | 100% (g_iter0 5-0*) |
| 55 | prisms-cs-club.prisms10 | 1394 | 74 | 122 | 54-68 | 100% (g_iter0 2-0*) |
| 56 | ipince.bobby_v2 | 1390 | 78 | 113 | 55-58 | 100% (g_iter0 5-0*) |
| 57 | mama4294.currentPlayer | 1372 | 80 | 110 | 54-56 | 100% (g_iter0 2-0*) |
| 58 | andrewgopher.gopherbot | 1342 | 68 | 140 | 68-72 | 100% (g_iter0 2-0*) |
| 59 | BrysonJGalapon.aloha | 1338 | 77 | 104 | 52-52 | 100% (g_iter0 2-0*) |
| 60 | bewuwy.deathbot4 | 1314 | 66 | 149 | 65-84 | 100% (g_iter0 2-0*) |
| 61 | JfeMak.realplayer2 | 1300 | 78 | 103 | 50-53 | 100% (g_iter0 2-0*) |
| 62 | SampleProvider.SPAARK_1_12_2023 | 1284 | 70 | 127 | 58-69 | 100% (g_iter0 2-0*) |
| 63 | SDainard-PDX.Team_Player | 1278 | 87 | 98 | 46-52 | 100% (g_iter0 2-0*) |
| 64 | **us:examplefuncsplayer** | 1254 | 380 | 6 | 0-6 |  |
| 65 | Nawlej.PoonPoonv3 | 1245 | 69 | 136 | 59-77 | 100% (g_iter0 5-0*) |
| 66 | PSUtblock.sprint_four_player | 1243 | 87 | 107 | 51-56 | 100% (g_iter0 2-0*) |
| 67 | Juanbri02.matfisplayer1 | 1238 | 74 | 122 | 55-67 | 100% (g_iter0 5-0*) |
| 68 | NolanChai.nolan_1 | 1232 | 78 | 113 | 51-62 | 100% (g_iter0 2-0*) |
| 69 | andrewgopher.gopherbot1 | 1224 | 74 | 128 | 54-74 | 100% (g_iter0 2-0*) |
| 70 | JackLee9355.jackPlayer | 1218 | 70 | 137 | 57-80 | 100% (g_iter0 2-0*) |
| 71 | jyorkio.elicompbot | 1217 | 75 | 110 | 49-61 | 100% (g_iter0 2-0*) |
| 72 | vontell.regressiongames | 1199 | 66 | 133 | 63-70 | 100% (g_iter0 5-0*) |
| 73 | SteamBlizzard.Block | 1184 | 68 | 150 | 59-91 | 100% (g_iter0 5-0*) |
| 74 | ax-95174.MPAction | 1133 | 79 | 107 | 42-65 | 100% (g_iter0 2-0*) |
| 75 | Chahat08.toph | 1103 | 72 | 124 | 51-73 | 100% (g_iter0 2-0*) |
| 76 | anicolao.submission | 1091 | 65 | 158 | 66-92 | 100% (g_iter0 2-0*) |
| 77 | legobridge.kushalplayer | 1087 | 88 | 104 | 38-66 | 100% (g_iter0 2-0*) |
| 78 | nail-e.Dante | 1081 | 72 | 128 | 61-67 | 100% (g_iter0 2-0*) |
| 79 | mama4294.learningBot | 1081 | 78 | 124 | 50-74 | 100% (g_iter0 2-0*) |
| 80 | Patela171.Battlecode2023_Robot | 1080 | 70 | 137 | 55-82 | 100% (g_iter0 2-0*) |
| 81 | michael-tyl.hqrewrite | 1076 | 71 | 128 | 52-76 | 100% (g_iter0 2-0*) |
| 82 | team-remember-to-hydrate.sprint_1 | 942 | 74 | 136 | 48-88 | 100% (g_iter0 2-0*) |
| 83 | Vinceyou1.Player1 | 933 | 77 | 121 | 45-76 | 100% (g_iter0 2-0*) |
| 84 | addiesteward.elicompbot | 902 | 70 | 142 | 56-86 | 100% (g_iter0 5-0*) |
| 85 | michael-tyl.cc_v0_5_0_6 | 887 | 66 | 164 | 62-102 | 100% (g_iter0 2-0*) |
| 86 | monmouth-college-cs.elicompbot | 864 | 72 | 142 | 51-91 | 100% (g_iter0 2-0*) |
| 87 | toyat522.bot5 | 859 | 80 | 127 | 46-81 | 100% (g_iter0 2-0*) |
| 88 | Swordman51.AdeptusAstartes2 | 837 | 67 | 146 | 56-90 | 100% (g_iter0 2-0*) |
| 89 | Chahat08.lazarus | 795 | 77 | 126 | 48-78 | 100% (g_iter0 2-0*) |
| 90 | ShatterXD.SRNNbot | 719 | 80 | 121 | 42-79 | 100% (g_iter0 2-0*) |
| 91 | anicolao.jumbled | 703 | 66 | 172 | 66-106 | 100% (g_iter0 5-0*) |
| 92 | NotLLeon.player | 591 | 77 | 140 | 51-89 | 100% (g_iter0 2-0*) |
| 93 | CodeClash-ai.mysubmission | 557 | 77 | 148 | 49-99 | 100% (g_iter0 2-0*) |
| 94 | addiesteward.NDeClaw | 542 | 81 | 148 | 52-96 | 100% (g_iter0 5-0*) |
| 95 | andrewkbank.First | 277 | 107 | 107 | 13-94 | 100% (g_iter0 2-0*) |
| 96 | Yooncw0223.lec3player | 250 | 108 | 153 | 12-141 | 100% (g_iter0 5-0*) |
