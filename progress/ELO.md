# Ladder

3125 games (959 ours, 2166 between field bots on the ladder replica), 3113 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| g_iter0 | 1807 +- 48 | 22 of 94 | 456 | 230-226 | 72.0% | 21.2% (vs 21) |
| c_line8a | 1769 +- 96 | 25 of 94 | 90 | 30-60 | 69.8% | 20.8% (vs 23) |
| c_line6 | 1753 +- 89 | 27 of 94 | 100 | 32-68 | 68.8% | 20.9% (vs 24) |
| c_line7m | 1741 +- 90 | 28 of 94 | 100 | 31-69 | 68.1% | 20.0% (vs 24) |
| c_line5 | 1704 +- 92 | 32 of 94 | 100 | 28-72 | 65.8% | 20.8% (vs 27) |
| c_line4 | 1665 +- 95 | 36 of 94 | 100 | 25-75 | 63.2% | 20.8% (vs 30) |
| examplefuncsplayer | 1281 +- 380 | 66 of 94 | 6 | 0-6 | 35.8% | 16.3% (vs 59) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | carlguo866.submit26_final | 2527 | 263 | 46 | 45-1 | 0% (g_iter0 0-2*) |
| 2 | battlecode-archive.sprintBot | 2391 | 281 | 44 | 43-1 | 0% (g_iter0 0-2*) |
| 3 | IvanGeffner.fortytwo | 2389 | 114 | 87 | 76-11 | 0% (g_iter0 0-36) |
| 4 | maxwelljones14.MPWorking | 2331 | 144 | 59 | 50-9 | 0% (g_iter0 0-5*) |
| 5 | vrangr1.AFinalsBot | 2329 | 158 | 116 | 111-5 | 7% (g_iter0 1-14*) |
| 6 | awesomelemonade.finalBot | 2321 | 134 | 119 | 111-8 | 0% (g_iter0 0-15*) |
| 7 | AnOvercookedFork.quals | 2244 | 173 | 47 | 41-6 | 20% (g_iter0 1-4*) |
| 8 | pranayagra.finalbotfinaltwo | 2232 | 113 | 85 | 66-19 | 7% (g_iter0 1-13*) |
| 9 | georgezhang02.FB_ZZZ | 2220 | 151 | 50 | 40-10 | 0% (g_iter0 0-2*) |
| 10 | pranayagra.finalbotfinal | 2201 | 81 | 164 | 130-34 | 13% (g_iter0 6-39) |
| 11 | jmerle.camel_case_v30_final | 2115 | 87 | 137 | 108-29 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2029 | 121 | 59 | 46-13 | 0% (g_iter0 0-2*) |
| 13 | GabeG888.v8o1 | 1962 | 146 | 41 | 29-12 | 0% (g_iter0 0-2*) |
| 14 | CyrilSharma.finalBot | 1954 | 142 | 59 | 37-22 | 0% (g_iter0 0-2*) |
| 15 | georgezhang02.CB_tuning2 | 1949 | 79 | 119 | 88-31 | 7% (g_iter0 1-14*) |
| 16 | NotLLeon.v7 | 1929 | 80 | 112 | 80-32 | 17% (g_iter0 2-10*) |
| 17 | britacatalin.FinalBot | 1893 | 89 | 91 | 66-25 | 42% (g_iter0 5-7*) |
| 18 | VarunVejalla.karel | 1832 | 106 | 71 | 40-31 | 50% (g_iter0 4-4*) |
| 19 | GabeG888.v8 | 1831 | 118 | 50 | 33-17 | 50% (g_iter0 1-1*) |
| 20 | ethanlabelle.v19 | 1811 | 140 | 38 | 24-14 | 50% (g_iter0 1-1*) |
| 21 | DannyZhang686.pqual2 | 1809 | 104 | 74 | 40-34 | 29% (g_iter0 4-10*) |
| 22 | **us:g_iter0** | 1807 | 48 | 456 | 230-226 |  |
| 23 | programjames.fourthbot | 1801 | 151 | 47 | 29-18 | 100% (g_iter0 2-0*) |
| 24 | VarunVejalla.ali8 | 1770 | 134 | 50 | 31-19 | 50% (g_iter0 1-1*) |
| 25 | **us:c_line8a** | 1769 | 96 | 90 | 30-60 |  |
| 26 | louishu17.wouisv8 | 1756 | 120 | 69 | 41-28 | 50% (g_iter0 5-5*) |
| 27 | **us:c_line6** | 1753 | 89 | 100 | 32-68 |  |
| 28 | **us:c_line7m** | 1741 | 90 | 100 | 31-69 |  |
| 29 | SampleProvider.SPAARK | 1712 | 128 | 50 | 34-16 | 100% (g_iter0 2-0*) |
| 30 | NicholasKelly15.gopher10 | 1708 | 139 | 44 | 28-16 | 100% (g_iter0 2-0*) |
| 31 | louishu17.louisv10 | 1706 | 130 | 44 | 23-21 | 100% (g_iter0 2-0*) |
| 32 | **us:c_line5** | 1704 | 92 | 100 | 28-72 |  |
| 33 | battlecode-archive.Sprint1 | 1699 | 73 | 113 | 59-54 | 58% (g_iter0 7-5*) |
| 34 | reeceyang.v5anaconda | 1677 | 76 | 107 | 55-52 | 58% (g_iter0 7-5*) |
| 35 | polyllc.poly | 1677 | 174 | 44 | 25-19 | 100% (g_iter0 2-0*) |
| 36 | **us:c_line4** | 1665 | 95 | 100 | 25-75 |  |
| 37 | legobridge.tacoplayer | 1660 | 107 | 79 | 42-37 | 85% (g_iter0 11-2*) |
| 38 | ipince.bobby | 1642 | 163 | 26 | 11-15 | 100% (g_iter0 2-0*) |
| 39 | toyat522.bot5a | 1640 | 129 | 50 | 25-25 | 80% (g_iter0 4-1*) |
| 40 | ColtG5.rexv9 | 1629 | 128 | 55 | 27-28 | 100% (g_iter0 2-0*) |
| 41 | SteamBlizzard.newVnewME | 1613 | 115 | 56 | 29-27 | 80% (g_iter0 4-1*) |
| 42 | DukeBas._main | 1591 | 142 | 44 | 23-21 | 100% (g_iter0 2-0*) |
| 43 | elgoldie.head_v5 | 1583 | 105 | 59 | 24-35 | 100% (g_iter0 2-0*) |
| 44 | TheK098.qp1_7_sprint_1 | 1570 | 134 | 44 | 22-22 | 100% (g_iter0 2-0*) |
| 45 | beaverbois.USQualifiers | 1548 | 124 | 44 | 20-24 | 50% (g_iter0 1-1*) |
| 46 | BrysonJGalapon.friday | 1541 | 107 | 62 | 37-25 | 100% (g_iter0 2-0*) |
| 47 | nail-e.Barry | 1512 | 110 | 56 | 34-22 | 100% (g_iter0 2-0*) |
| 48 | kevinli405.maggi3_2 | 1488 | 136 | 53 | 21-32 | 100% (g_iter0 2-0*) |
| 49 | prisms-cs-club.prisms10 | 1475 | 124 | 59 | 28-31 | 100% (g_iter0 2-0*) |
| 50 | kevinli405.maggi3 | 1435 | 121 | 59 | 32-27 | 100% (g_iter0 5-0*) |
| 51 | Nawlej.PoonPoon | 1419 | 128 | 47 | 24-23 | 100% (g_iter0 2-0*) |
| 52 | yaonam.PoonPoonv4 | 1412 | 84 | 131 | 42-89 | 87% (g_iter0 13-2*) |
| 53 | BrysonJGalapon.aloha | 1410 | 121 | 47 | 25-22 | 100% (g_iter0 2-0*) |
| 54 | aj-chau.attempt1 | 1400 | 128 | 50 | 24-26 | 100% (g_iter0 5-0*) |
| 55 | andrewgopher.gopherbot | 1361 | 98 | 65 | 35-30 | 100% (g_iter0 2-0*) |
| 56 | mama4294.currentPlayer | 1360 | 138 | 41 | 19-22 | 100% (g_iter0 2-0*) |
| 57 | bewuwy.deathbot4 | 1341 | 112 | 62 | 22-40 | 100% (g_iter0 2-0*) |
| 58 | JfeMak.realplayer2 | 1327 | 125 | 43 | 22-21 | 100% (g_iter0 2-0*) |
| 59 | PSUtblock.sprint_four_player | 1309 | 184 | 35 | 16-19 | 100% (g_iter0 2-0*) |
| 60 | JackLee9355.jackPlayer | 1300 | 125 | 53 | 23-30 | 100% (g_iter0 2-0*) |
| 61 | Nawlej.PoonPoonv3 | 1297 | 110 | 59 | 23-36 | 100% (g_iter0 5-0*) |
| 62 | ipince.bobby_v2 | 1297 | 122 | 53 | 18-35 | 100% (g_iter0 5-0*) |
| 63 | SampleProvider.SPAARK_1_12_2023 | 1293 | 136 | 38 | 16-22 | 100% (g_iter0 2-0*) |
| 64 | SDainard-PDX.Team_Player | 1291 | 138 | 47 | 18-29 | 100% (g_iter0 2-0*) |
| 65 | jyorkio.elicompbot | 1282 | 124 | 35 | 15-20 | 100% (g_iter0 2-0*) |
| 66 | **us:examplefuncsplayer** | 1281 | 380 | 6 | 0-6 |  |
| 67 | NolanChai.nolan_1 | 1275 | 100 | 65 | 23-42 | 100% (g_iter0 2-0*) |
| 68 | anicolao.submission | 1259 | 104 | 64 | 27-37 | 100% (g_iter0 2-0*) |
| 69 | vontell.regressiongames | 1257 | 107 | 53 | 22-31 | 100% (g_iter0 5-0*) |
| 70 | andrewgopher.gopherbot1 | 1254 | 100 | 74 | 27-47 | 100% (g_iter0 2-0*) |
| 71 | ax-95174.MPAction | 1250 | 126 | 44 | 18-26 | 100% (g_iter0 2-0*) |
| 72 | michael-tyl.hqrewrite | 1205 | 117 | 53 | 19-34 | 100% (g_iter0 2-0*) |
| 73 | SteamBlizzard.Block | 1196 | 117 | 70 | 18-52 | 100% (g_iter0 5-0*) |
| 74 | Patela171.Battlecode2023_Robot | 1177 | 110 | 65 | 26-39 | 100% (g_iter0 2-0*) |
| 75 | Chahat08.toph | 1177 | 113 | 56 | 18-38 | 100% (g_iter0 2-0*) |
| 76 | legobridge.kushalplayer | 1169 | 183 | 35 | 5-30 | 100% (g_iter0 2-0*) |
| 77 | nail-e.Dante | 1142 | 132 | 44 | 24-20 | 100% (g_iter0 2-0*) |
| 78 | Juanbri02.matfisplayer1 | 1140 | 156 | 50 | 16-34 | 100% (g_iter0 5-0*) |
| 79 | addiesteward.elicompbot | 1081 | 130 | 50 | 16-34 | 100% (g_iter0 5-0*) |
| 80 | team-remember-to-hydrate.sprint_1 | 1057 | 138 | 56 | 12-44 | 100% (g_iter0 2-0*) |
| 81 | mama4294.learningBot | 1056 | 161 | 53 | 9-44 | 100% (g_iter0 2-0*) |
| 82 | toyat522.bot5 | 1013 | 170 | 47 | 6-41 | 100% (g_iter0 2-0*) |
| 83 | Vinceyou1.Player1 | 997 | 120 | 59 | 19-40 | 100% (g_iter0 2-0*) |
| 84 | Swordman51.AdeptusAstartes2 | 971 | 144 | 46 | 13-33 | 100% (g_iter0 2-0*) |
| 85 | monmouth-college-cs.elicompbot | 930 | 129 | 62 | 16-46 | 100% (g_iter0 2-0*) |
| 86 | michael-tyl.cc_v0_5_0_6 | 902 | 126 | 71 | 19-52 | 100% (g_iter0 2-0*) |
| 87 | Chahat08.lazarus | 891 | 190 | 35 | 5-30 | 100% (g_iter0 2-0*) |
| 88 | ShatterXD.SRNNbot | 877 | 164 | 38 | 8-30 | 100% (g_iter0 2-0*) |
| 89 | CodeClash-ai.mysubmission | 782 | 194 | 49 | 4-45 | 100% (g_iter0 2-0*) |
| 90 | addiesteward.NDeClaw | 719 | 155 | 62 | 11-51 | 100% (g_iter0 5-0*) |
| 91 | andrewkbank.First | 661 | 178 | 38 | 4-34 | 100% (g_iter0 2-0*) |
| 92 | NotLLeon.player | 639 | 258 | 32 | 1-31 | 100% (g_iter0 2-0*) |
| 93 | anicolao.jumbled | 524 | 243 | 47 | 2-45 | 100% (g_iter0 5-0*) |
| 94 | Yooncw0223.lec3player | 486 | 197 | 68 | 3-65 | 100% (g_iter0 5-0*) |
