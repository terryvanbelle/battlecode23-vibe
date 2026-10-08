# Ladder

2854 games (760 ours, 2094 between field bots on the ladder replica), 2842 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| g_iter0 | 1811 +- 47 | 21 of 92 | 447 | 221-226 | 71.8% | 20.0% (vs 20) |
| c_line6 | 1765 +- 88 | 26 of 92 | 100 | 32-68 | 69.0% | 21.5% (vs 24) |
| c_line5 | 1717 +- 91 | 30 of 92 | 100 | 28-72 | 66.1% | 21.3% (vs 27) |
| c_line4 | 1679 +- 93 | 34 of 92 | 100 | 25-75 | 63.6% | 21.2% (vs 30) |
| examplefuncsplayer | 1290 +- 380 | 62 of 92 | 6 | 0-6 | 35.7% | 15.1% (vs 57) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | carlguo866.submit26_final | 2525 | 262 | 46 | 45-1 | 0% (g_iter0 0-2*) |
| 2 | IvanGeffner.fortytwo | 2385 | 118 | 84 | 74-10 | 0% (g_iter0 0-36) |
| 3 | battlecode-archive.sprintBot | 2362 | 272 | 44 | 43-1 | 0% (g_iter0 0-2*) |
| 4 | maxwelljones14.MPWorking | 2330 | 143 | 59 | 50-9 | 0% (g_iter0 0-5*) |
| 5 | awesomelemonade.finalBot | 2301 | 137 | 99 | 91-8 | 0% (g_iter0 0-15*) |
| 6 | vrangr1.AFinalsBot | 2264 | 161 | 90 | 85-5 | 7% (g_iter0 1-14*) |
| 7 | AnOvercookedFork.quals | 2241 | 171 | 47 | 41-6 | 20% (g_iter0 1-4*) |
| 8 | pranayagra.finalbotfinaltwo | 2228 | 116 | 82 | 65-17 | 7% (g_iter0 1-13*) |
| 9 | georgezhang02.FB_ZZZ | 2213 | 152 | 47 | 37-10 | 0% (g_iter0 0-2*) |
| 10 | pranayagra.finalbotfinal | 2187 | 83 | 144 | 110-34 | 13% (g_iter0 6-39) |
| 11 | jmerle.camel_case_v30_final | 2123 | 95 | 114 | 90-24 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2041 | 121 | 59 | 46-13 | 0% (g_iter0 0-2*) |
| 13 | GabeG888.v8o1 | 1970 | 145 | 41 | 29-12 | 0% (g_iter0 0-2*) |
| 14 | georgezhang02.CB_tuning2 | 1969 | 90 | 99 | 74-25 | 7% (g_iter0 1-14*) |
| 15 | CyrilSharma.finalBot | 1956 | 140 | 59 | 37-22 | 0% (g_iter0 0-2*) |
| 16 | NotLLeon.v7 | 1916 | 87 | 89 | 61-28 | 17% (g_iter0 2-10*) |
| 17 | britacatalin.FinalBot | 1899 | 96 | 81 | 59-22 | 42% (g_iter0 5-7*) |
| 18 | GabeG888.v8 | 1835 | 123 | 44 | 28-16 | 50% (g_iter0 1-1*) |
| 19 | VarunVejalla.karel | 1834 | 107 | 68 | 37-31 | 50% (g_iter0 4-4*) |
| 20 | ethanlabelle.v19 | 1824 | 139 | 38 | 24-14 | 50% (g_iter0 1-1*) |
| 21 | **us:g_iter0** | 1811 | 47 | 447 | 221-226 |  |
| 22 | DannyZhang686.pqual2 | 1808 | 104 | 74 | 40-34 | 29% (g_iter0 4-10*) |
| 23 | programjames.fourthbot | 1804 | 147 | 47 | 29-18 | 100% (g_iter0 2-0*) |
| 24 | VarunVejalla.ali8 | 1779 | 134 | 50 | 31-19 | 50% (g_iter0 1-1*) |
| 25 | louishu17.wouisv8 | 1769 | 120 | 66 | 41-25 | 50% (g_iter0 5-5*) |
| 26 | **us:c_line6** | 1765 | 88 | 100 | 32-68 |  |
| 27 | battlecode-archive.Sprint1 | 1733 | 82 | 93 | 53-40 | 58% (g_iter0 7-5*) |
| 28 | SampleProvider.SPAARK | 1721 | 129 | 50 | 34-16 | 100% (g_iter0 2-0*) |
| 29 | louishu17.louisv10 | 1718 | 137 | 41 | 22-19 | 100% (g_iter0 2-0*) |
| 30 | **us:c_line5** | 1717 | 91 | 100 | 28-72 |  |
| 31 | NicholasKelly15.gopher10 | 1714 | 146 | 41 | 26-15 | 100% (g_iter0 2-0*) |
| 32 | reeceyang.v5anaconda | 1708 | 87 | 87 | 49-38 | 58% (g_iter0 7-5*) |
| 33 | polyllc.poly | 1685 | 172 | 44 | 25-19 | 100% (g_iter0 2-0*) |
| 34 | **us:c_line4** | 1679 | 93 | 100 | 25-75 |  |
| 35 | legobridge.tacoplayer | 1661 | 108 | 76 | 39-37 | 85% (g_iter0 11-2*) |
| 36 | ipince.bobby | 1653 | 162 | 26 | 11-15 | 100% (g_iter0 2-0*) |
| 37 | ColtG5.rexv9 | 1644 | 127 | 55 | 27-28 | 100% (g_iter0 2-0*) |
| 38 | SteamBlizzard.newVnewME | 1641 | 119 | 53 | 28-25 | 80% (g_iter0 4-1*) |
| 39 | toyat522.bot5a | 1641 | 131 | 47 | 22-25 | 80% (g_iter0 4-1*) |
| 40 | elgoldie.head_v5 | 1589 | 106 | 59 | 24-35 | 100% (g_iter0 2-0*) |
| 41 | TheK098.qp1_7_sprint_1 | 1581 | 135 | 44 | 22-22 | 100% (g_iter0 2-0*) |
| 42 | beaverbois.USQualifiers | 1559 | 124 | 44 | 20-24 | 50% (g_iter0 1-1*) |
| 43 | BrysonJGalapon.friday | 1558 | 106 | 62 | 37-25 | 100% (g_iter0 2-0*) |
| 44 | DukeBas._main | 1546 | 156 | 38 | 17-21 | 100% (g_iter0 2-0*) |
| 45 | kevinli405.maggi3_2 | 1530 | 141 | 50 | 21-29 | 100% (g_iter0 2-0*) |
| 46 | nail-e.Barry | 1506 | 120 | 47 | 29-18 | 100% (g_iter0 2-0*) |
| 47 | prisms-cs-club.prisms10 | 1481 | 124 | 59 | 28-31 | 100% (g_iter0 2-0*) |
| 48 | kevinli405.maggi3 | 1438 | 121 | 59 | 32-27 | 100% (g_iter0 5-0*) |
| 49 | yaonam.PoonPoonv4 | 1432 | 91 | 108 | 40-68 | 87% (g_iter0 13-2*) |
| 50 | Nawlej.PoonPoon | 1429 | 127 | 47 | 24-23 | 100% (g_iter0 2-0*) |
| 51 | BrysonJGalapon.aloha | 1421 | 120 | 47 | 25-22 | 100% (g_iter0 2-0*) |
| 52 | aj-chau.attempt1 | 1410 | 129 | 50 | 24-26 | 100% (g_iter0 5-0*) |
| 53 | mama4294.currentPlayer | 1373 | 138 | 41 | 19-22 | 100% (g_iter0 2-0*) |
| 54 | andrewgopher.gopherbot | 1369 | 97 | 65 | 35-30 | 100% (g_iter0 2-0*) |
| 55 | bewuwy.deathbot4 | 1360 | 113 | 59 | 22-37 | 100% (g_iter0 2-0*) |
| 56 | JfeMak.realplayer2 | 1336 | 125 | 43 | 22-21 | 100% (g_iter0 2-0*) |
| 57 | NolanChai.nolan_1 | 1315 | 109 | 56 | 20-36 | 100% (g_iter0 2-0*) |
| 58 | PSUtblock.sprint_four_player | 1313 | 183 | 35 | 16-19 | 100% (g_iter0 2-0*) |
| 59 | SampleProvider.SPAARK_1_12_2023 | 1313 | 138 | 35 | 16-19 | 100% (g_iter0 2-0*) |
| 60 | JackLee9355.jackPlayer | 1300 | 125 | 53 | 23-30 | 100% (g_iter0 2-0*) |
| 61 | SDainard-PDX.Team_Player | 1294 | 139 | 44 | 15-29 | 100% (g_iter0 2-0*) |
| 62 | **us:examplefuncsplayer** | 1290 | 380 | 6 | 0-6 |  |
| 63 | jyorkio.elicompbot | 1288 | 125 | 35 | 15-20 | 100% (g_iter0 2-0*) |
| 64 | Nawlej.PoonPoonv3 | 1278 | 121 | 50 | 18-32 | 100% (g_iter0 2-0*) |
| 65 | anicolao.submission | 1272 | 108 | 61 | 25-36 | 100% (g_iter0 2-0*) |
| 66 | ipince.bobby_v2 | 1267 | 132 | 44 | 15-29 | 100% (g_iter0 2-0*) |
| 67 | andrewgopher.gopherbot1 | 1265 | 99 | 74 | 27-47 | 100% (g_iter0 2-0*) |
| 68 | vontell.regressiongames | 1262 | 107 | 53 | 22-31 | 100% (g_iter0 5-0*) |
| 69 | ax-95174.MPAction | 1236 | 132 | 41 | 15-26 | 100% (g_iter0 2-0*) |
| 70 | legobridge.kushalplayer | 1217 | 203 | 26 | 4-22 | 100% (g_iter0 2-0*) |
| 71 | michael-tyl.hqrewrite | 1213 | 117 | 53 | 19-34 | 100% (g_iter0 2-0*) |
| 72 | Chahat08.toph | 1207 | 117 | 53 | 18-35 | 100% (g_iter0 2-0*) |
| 73 | SteamBlizzard.Block | 1194 | 121 | 67 | 17-50 | 100% (g_iter0 5-0*) |
| 74 | Patela171.Battlecode2023_Robot | 1187 | 114 | 62 | 25-37 | 100% (g_iter0 2-0*) |
| 75 | nail-e.Dante | 1185 | 139 | 41 | 24-17 | 100% (g_iter0 2-0*) |
| 76 | Juanbri02.matfisplayer1 | 1142 | 156 | 47 | 16-31 | 100% (g_iter0 2-0*) |
| 77 | team-remember-to-hydrate.sprint_1 | 1072 | 138 | 56 | 12-44 | 100% (g_iter0 2-0*) |
| 78 | addiesteward.elicompbot | 1066 | 137 | 47 | 13-34 | 100% (g_iter0 5-0*) |
| 79 | mama4294.learningBot | 1063 | 160 | 50 | 9-41 | 100% (g_iter0 2-0*) |
| 80 | toyat522.bot5 | 1029 | 170 | 47 | 6-41 | 100% (g_iter0 2-0*) |
| 81 | Swordman51.AdeptusAstartes2 | 1026 | 163 | 40 | 11-29 | 100% (g_iter0 2-0*) |
| 82 | Vinceyou1.Player1 | 1005 | 119 | 59 | 19-40 | 100% (g_iter0 2-0*) |
| 83 | monmouth-college-cs.elicompbot | 943 | 129 | 62 | 16-46 | 100% (g_iter0 2-0*) |
| 84 | Chahat08.lazarus | 914 | 211 | 32 | 4-28 | 100% (g_iter0 2-0*) |
| 85 | michael-tyl.cc_v0_5_0_6 | 914 | 126 | 71 | 19-52 | 100% (g_iter0 2-0*) |
| 86 | ShatterXD.SRNNbot | 895 | 164 | 38 | 8-30 | 100% (g_iter0 2-0*) |
| 87 | CodeClash-ai.mysubmission | 787 | 193 | 49 | 4-45 | 100% (g_iter0 2-0*) |
| 88 | addiesteward.NDeClaw | 731 | 155 | 62 | 11-51 | 100% (g_iter0 5-0*) |
| 89 | andrewkbank.First | 675 | 179 | 38 | 4-34 | 100% (g_iter0 2-0*) |
| 90 | NotLLeon.player | 664 | 259 | 32 | 1-31 | 100% (g_iter0 2-0*) |
| 91 | anicolao.jumbled | 538 | 243 | 47 | 2-45 | 100% (g_iter0 5-0*) |
| 92 | Yooncw0223.lec3player | 499 | 197 | 65 | 3-62 | 100% (g_iter0 5-0*) |
