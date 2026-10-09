# Ladder

5846 games (1325 ours, 4521 between field bots on the ladder replica), 5815 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_nav4 | 1899 +- 129 | 17 of 96 | 40 | 15-25 | 76.8% | 20.5% (vs 16) |
| c_swarm1 | 1854 +- 48 | 21 of 96 | 271 | 128-143 | 74.5% | 21.6% (vs 19) |
| g_iter0 | 1816 +- 48 | 25 of 96 | 456 | 230-226 | 72.4% | 22.6% (vs 22) |
| c_line8a | 1813 +- 72 | 27 of 96 | 139 | 47-92 | 72.2% | 23.5% (vs 23) |
| c_line6 | 1778 +- 89 | 28 of 96 | 100 | 32-68 | 70.2% | 20.6% (vs 23) |
| c_line7m | 1766 +- 90 | 32 of 96 | 100 | 31-69 | 69.5% | 23.0% (vs 26) |
| c_line5 | 1729 +- 92 | 35 of 96 | 100 | 28-72 | 67.4% | 22.1% (vs 28) |
| c_line4 | 1690 +- 95 | 37 of 96 | 100 | 25-75 | 65.0% | 19.9% (vs 29) |
| examplefuncsplayer | 1266 +- 380 | 64 of 96 | 6 | 0-6 | 37.0% | 13.5% (vs 55) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2416 | 92 | 111 | 92-19 | 0% (g_iter0 0-36) |
| 2 | maxwelljones14.MPWorking | 2384 | 103 | 86 | 69-17 | 0% (g_iter0 0-5*) |
| 3 | awesomelemonade.finalBot | 2363 | 95 | 159 | 139-20 | 0% (g_iter0 0-15*) |
| 4 | carlguo866.submit26_final | 2342 | 108 | 82 | 64-18 | 0% (g_iter0 0-2*) |
| 5 | vrangr1.AFinalsBot | 2334 | 99 | 168 | 153-15 | 7% (g_iter0 1-14*) |
| 6 | AnOvercookedFork.quals | 2275 | 105 | 89 | 70-19 | 20% (g_iter0 1-4*) |
| 7 | pranayagra.finalbotfinaltwo | 2234 | 89 | 109 | 79-30 | 7% (g_iter0 1-13*) |
| 8 | pranayagra.finalbotfinal | 2191 | 68 | 201 | 152-49 | 13% (g_iter0 6-39) |
| 9 | battlecode-archive.sprintBot | 2182 | 120 | 82 | 63-19 | 0% (g_iter0 0-2*) |
| 10 | georgezhang02.FB_ZZZ | 2154 | 91 | 95 | 66-29 | 0% (g_iter0 0-2*) |
| 11 | jmerle.camel_case_v30_final | 2109 | 66 | 196 | 148-48 | 14% (g_iter0 3-18*) |
| 12 | CyrilSharma.finalBot | 2001 | 93 | 101 | 65-36 | 0% (g_iter0 0-2*) |
| 13 | ethanlabelle.dev | 1999 | 81 | 100 | 65-35 | 0% (g_iter0 0-2*) |
| 14 | NotLLeon.v7 | 1978 | 65 | 168 | 116-52 | 17% (g_iter0 2-10*) |
| 15 | georgezhang02.CB_tuning2 | 1972 | 64 | 167 | 115-52 | 7% (g_iter0 1-14*) |
| 16 | GabeG888.v8o1 | 1908 | 98 | 80 | 56-24 | 0% (g_iter0 0-2*) |
| 17 | **us:c_nav4** | 1899 | 129 | 40 | 15-25 |  |
| 18 | britacatalin.FinalBot | 1895 | 64 | 155 | 99-56 | 42% (g_iter0 5-7*) |
| 19 | ethanlabelle.v19 | 1895 | 86 | 90 | 60-30 | 50% (g_iter0 1-1*) |
| 20 | GabeG888.v8 | 1856 | 78 | 98 | 59-39 | 50% (g_iter0 1-1*) |
| 21 | **us:c_swarm1** | 1854 | 48 | 271 | 128-143 |  |
| 22 | NicholasKelly15.gopher10 | 1831 | 96 | 83 | 56-27 | 100% (g_iter0 2-0*) |
| 23 | VarunVejalla.karel | 1829 | 76 | 122 | 70-52 | 50% (g_iter0 4-4*) |
| 24 | DannyZhang686.pqual2 | 1823 | 80 | 116 | 67-49 | 29% (g_iter0 4-10*) |
| 25 | **us:g_iter0** | 1816 | 48 | 456 | 230-226 |  |
| 26 | programjames.fourthbot | 1815 | 83 | 104 | 62-42 | 100% (g_iter0 2-0*) |
| 27 | **us:c_line8a** | 1813 | 72 | 139 | 47-92 |  |
| 28 | **us:c_line6** | 1778 | 89 | 100 | 32-68 |  |
| 29 | louishu17.louisv10 | 1777 | 87 | 98 | 59-39 | 100% (g_iter0 2-0*) |
| 30 | louishu17.wouisv8 | 1770 | 81 | 122 | 73-49 | 50% (g_iter0 5-5*) |
| 31 | VarunVejalla.ali8 | 1767 | 93 | 89 | 55-34 | 50% (g_iter0 1-1*) |
| 32 | **us:c_line7m** | 1766 | 90 | 100 | 31-69 |  |
| 33 | reeceyang.v5anaconda | 1731 | 58 | 175 | 88-87 | 58% (g_iter0 7-5*) |
| 34 | battlecode-archive.Sprint1 | 1731 | 58 | 171 | 84-87 | 58% (g_iter0 7-5*) |
| 35 | **us:c_line5** | 1729 | 92 | 100 | 28-72 |  |
| 36 | SampleProvider.SPAARK | 1723 | 84 | 97 | 58-39 | 100% (g_iter0 2-0*) |
| 37 | **us:c_line4** | 1690 | 95 | 100 | 25-75 |  |
| 38 | ipince.bobby | 1666 | 89 | 95 | 54-41 | 100% (g_iter0 2-0*) |
| 39 | legobridge.tacoplayer | 1655 | 81 | 123 | 71-52 | 85% (g_iter0 11-2*) |
| 40 | polyllc.poly | 1614 | 97 | 95 | 47-48 | 100% (g_iter0 2-0*) |
| 41 | toyat522.bot5a | 1596 | 78 | 113 | 59-54 | 80% (g_iter0 4-1*) |
| 42 | ColtG5.rexv9 | 1590 | 80 | 109 | 57-52 | 100% (g_iter0 2-0*) |
| 43 | SteamBlizzard.newVnewME | 1582 | 77 | 115 | 54-61 | 80% (g_iter0 4-1*) |
| 44 | TheK098.qp1_7_sprint_1 | 1581 | 82 | 107 | 61-46 | 100% (g_iter0 2-0*) |
| 45 | DukeBas._main | 1569 | 88 | 98 | 51-47 | 100% (g_iter0 2-0*) |
| 46 | elgoldie.head_v5 | 1568 | 75 | 107 | 51-56 | 100% (g_iter0 2-0*) |
| 47 | beaverbois.USQualifiers | 1541 | 84 | 95 | 49-46 | 50% (g_iter0 1-1*) |
| 48 | kevinli405.maggi3_2 | 1523 | 85 | 109 | 54-55 | 100% (g_iter0 2-0*) |
| 49 | BrysonJGalapon.friday | 1515 | 78 | 106 | 56-50 | 100% (g_iter0 2-0*) |
| 50 | nail-e.Barry | 1473 | 83 | 94 | 49-45 | 100% (g_iter0 2-0*) |
| 51 | Nawlej.PoonPoon | 1463 | 89 | 95 | 48-47 | 100% (g_iter0 2-0*) |
| 52 | kevinli405.maggi3 | 1422 | 81 | 113 | 60-53 | 100% (g_iter0 5-0*) |
| 53 | yaonam.PoonPoonv4 | 1413 | 63 | 203 | 74-129 | 87% (g_iter0 13-2*) |
| 54 | aj-chau.attempt1 | 1407 | 95 | 89 | 46-43 | 100% (g_iter0 5-0*) |
| 55 | prisms-cs-club.prisms10 | 1407 | 81 | 107 | 47-60 | 100% (g_iter0 2-0*) |
| 56 | ipince.bobby_v2 | 1391 | 79 | 110 | 53-57 | 100% (g_iter0 5-0*) |
| 57 | mama4294.currentPlayer | 1368 | 86 | 101 | 49-52 | 100% (g_iter0 2-0*) |
| 58 | BrysonJGalapon.aloha | 1343 | 78 | 101 | 51-50 | 100% (g_iter0 2-0*) |
| 59 | andrewgopher.gopherbot | 1331 | 72 | 128 | 60-68 | 100% (g_iter0 2-0*) |
| 60 | bewuwy.deathbot4 | 1317 | 68 | 140 | 60-80 | 100% (g_iter0 2-0*) |
| 61 | JfeMak.realplayer2 | 1303 | 78 | 103 | 50-53 | 100% (g_iter0 2-0*) |
| 62 | SampleProvider.SPAARK_1_12_2023 | 1281 | 76 | 110 | 50-60 | 100% (g_iter0 2-0*) |
| 63 | SDainard-PDX.Team_Player | 1275 | 90 | 92 | 43-49 | 100% (g_iter0 2-0*) |
| 64 | **us:examplefuncsplayer** | 1266 | 380 | 6 | 0-6 |  |
| 65 | Juanbri02.matfisplayer1 | 1256 | 76 | 116 | 55-61 | 100% (g_iter0 5-0*) |
| 66 | Nawlej.PoonPoonv3 | 1250 | 69 | 133 | 58-75 | 100% (g_iter0 5-0*) |
| 67 | PSUtblock.sprint_four_player | 1244 | 91 | 101 | 47-54 | 100% (g_iter0 2-0*) |
| 68 | jyorkio.elicompbot | 1234 | 80 | 98 | 44-54 | 100% (g_iter0 2-0*) |
| 69 | andrewgopher.gopherbot1 | 1232 | 78 | 119 | 50-69 | 100% (g_iter0 2-0*) |
| 70 | JackLee9355.jackPlayer | 1231 | 72 | 131 | 54-77 | 100% (g_iter0 2-0*) |
| 71 | NolanChai.nolan_1 | 1229 | 81 | 104 | 44-60 | 100% (g_iter0 2-0*) |
| 72 | SteamBlizzard.Block | 1205 | 71 | 141 | 57-84 | 100% (g_iter0 5-0*) |
| 73 | vontell.regressiongames | 1199 | 70 | 122 | 57-65 | 100% (g_iter0 5-0*) |
| 74 | ax-95174.MPAction | 1119 | 82 | 101 | 36-65 | 100% (g_iter0 2-0*) |
| 75 | Chahat08.toph | 1112 | 74 | 118 | 47-71 | 100% (g_iter0 2-0*) |
| 76 | anicolao.submission | 1097 | 69 | 143 | 58-85 | 100% (g_iter0 2-0*) |
| 77 | legobridge.kushalplayer | 1093 | 93 | 98 | 35-63 | 100% (g_iter0 2-0*) |
| 78 | michael-tyl.hqrewrite | 1091 | 72 | 125 | 52-73 | 100% (g_iter0 2-0*) |
| 79 | mama4294.learningBot | 1089 | 79 | 121 | 49-72 | 100% (g_iter0 2-0*) |
| 80 | Patela171.Battlecode2023_Robot | 1088 | 74 | 125 | 49-76 | 100% (g_iter0 2-0*) |
| 81 | nail-e.Dante | 1086 | 76 | 116 | 57-59 | 100% (g_iter0 2-0*) |
| 82 | team-remember-to-hydrate.sprint_1 | 975 | 77 | 125 | 44-81 | 100% (g_iter0 2-0*) |
| 83 | Vinceyou1.Player1 | 933 | 82 | 110 | 39-71 | 100% (g_iter0 2-0*) |
| 84 | addiesteward.elicompbot | 905 | 71 | 139 | 54-85 | 100% (g_iter0 5-0*) |
| 85 | michael-tyl.cc_v0_5_0_6 | 895 | 70 | 152 | 55-97 | 100% (g_iter0 2-0*) |
| 86 | monmouth-college-cs.elicompbot | 888 | 77 | 128 | 48-80 | 100% (g_iter0 2-0*) |
| 87 | toyat522.bot5 | 861 | 85 | 118 | 40-78 | 100% (g_iter0 2-0*) |
| 88 | Swordman51.AdeptusAstartes2 | 845 | 71 | 130 | 50-80 | 100% (g_iter0 2-0*) |
| 89 | Chahat08.lazarus | 781 | 86 | 109 | 36-73 | 100% (g_iter0 2-0*) |
| 90 | ShatterXD.SRNNbot | 721 | 83 | 115 | 38-77 | 100% (g_iter0 2-0*) |
| 91 | anicolao.jumbled | 701 | 71 | 154 | 58-96 | 100% (g_iter0 5-0*) |
| 92 | CodeClash-ai.mysubmission | 611 | 83 | 130 | 45-85 | 100% (g_iter0 2-0*) |
| 93 | NotLLeon.player | 587 | 82 | 128 | 45-83 | 100% (g_iter0 2-0*) |
| 94 | addiesteward.NDeClaw | 549 | 82 | 145 | 49-96 | 100% (g_iter0 5-0*) |
| 95 | andrewkbank.First | 279 | 111 | 104 | 12-92 | 100% (g_iter0 2-0*) |
| 96 | Yooncw0223.lec3player | 259 | 113 | 147 | 11-136 | 100% (g_iter0 5-0*) |
