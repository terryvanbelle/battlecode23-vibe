# Ladder

3285 games (990 ours, 2295 between field bots on the ladder replica), 3273 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| g_iter0 | 1810 +- 48 | 20 of 94 | 456 | 230-226 | 72.2% | 18.5% (vs 19) |
| c_line8a | 1801 +- 80 | 22 of 94 | 121 | 41-80 | 71.6% | 19.4% (vs 20) |
| c_line6 | 1762 +- 90 | 26 of 94 | 100 | 32-68 | 69.4% | 20.5% (vs 23) |
| c_line7m | 1750 +- 90 | 28 of 94 | 100 | 31-69 | 68.6% | 20.9% (vs 24) |
| c_line5 | 1712 +- 92 | 31 of 94 | 100 | 28-72 | 66.3% | 20.4% (vs 26) |
| c_line4 | 1673 +- 95 | 37 of 94 | 100 | 25-75 | 63.7% | 22.3% (vs 31) |
| examplefuncsplayer | 1283 +- 380 | 65 of 94 | 6 | 0-6 | 36.1% | 15.9% (vs 58) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | carlguo866.submit26_final | 2534 | 262 | 49 | 48-1 | 0% (g_iter0 0-2*) |
| 2 | battlecode-archive.sprintBot | 2398 | 282 | 44 | 43-1 | 0% (g_iter0 0-2*) |
| 3 | IvanGeffner.fortytwo | 2394 | 114 | 87 | 76-11 | 0% (g_iter0 0-36) |
| 4 | vrangr1.AFinalsBot | 2338 | 158 | 116 | 111-5 | 7% (g_iter0 1-14*) |
| 5 | maxwelljones14.MPWorking | 2335 | 144 | 62 | 53-9 | 0% (g_iter0 0-5*) |
| 6 | awesomelemonade.finalBot | 2331 | 133 | 122 | 114-8 | 0% (g_iter0 0-15*) |
| 7 | AnOvercookedFork.quals | 2250 | 172 | 53 | 47-6 | 20% (g_iter0 1-4*) |
| 8 | pranayagra.finalbotfinaltwo | 2238 | 113 | 85 | 66-19 | 7% (g_iter0 1-13*) |
| 9 | georgezhang02.FB_ZZZ | 2221 | 153 | 50 | 40-10 | 0% (g_iter0 0-2*) |
| 10 | pranayagra.finalbotfinal | 2207 | 81 | 164 | 130-34 | 13% (g_iter0 6-39) |
| 11 | jmerle.camel_case_v30_final | 2126 | 86 | 140 | 111-29 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2000 | 115 | 62 | 47-15 | 0% (g_iter0 0-2*) |
| 13 | GabeG888.v8o1 | 1960 | 145 | 44 | 32-12 | 0% (g_iter0 0-2*) |
| 14 | georgezhang02.CB_tuning2 | 1954 | 79 | 119 | 88-31 | 7% (g_iter0 1-14*) |
| 15 | CyrilSharma.finalBot | 1950 | 142 | 59 | 37-22 | 0% (g_iter0 0-2*) |
| 16 | NotLLeon.v7 | 1936 | 80 | 112 | 80-32 | 17% (g_iter0 2-10*) |
| 17 | britacatalin.FinalBot | 1908 | 83 | 107 | 79-28 | 42% (g_iter0 5-7*) |
| 18 | GabeG888.v8 | 1826 | 117 | 50 | 33-17 | 50% (g_iter0 1-1*) |
| 19 | VarunVejalla.karel | 1813 | 99 | 77 | 42-35 | 50% (g_iter0 4-4*) |
| 20 | **us:g_iter0** | 1810 | 48 | 456 | 230-226 |  |
| 21 | programjames.fourthbot | 1805 | 142 | 50 | 31-19 | 100% (g_iter0 2-0*) |
| 22 | **us:c_line8a** | 1801 | 80 | 121 | 41-80 |  |
| 23 | DannyZhang686.pqual2 | 1801 | 102 | 77 | 41-36 | 29% (g_iter0 4-10*) |
| 24 | ethanlabelle.v19 | 1782 | 137 | 41 | 26-15 | 50% (g_iter0 1-1*) |
| 25 | VarunVejalla.ali8 | 1768 | 132 | 53 | 34-19 | 50% (g_iter0 1-1*) |
| 26 | **us:c_line6** | 1762 | 90 | 100 | 32-68 |  |
| 27 | louishu17.wouisv8 | 1754 | 119 | 72 | 41-31 | 50% (g_iter0 5-5*) |
| 28 | **us:c_line7m** | 1750 | 90 | 100 | 31-69 |  |
| 29 | SampleProvider.SPAARK | 1719 | 127 | 53 | 37-16 | 100% (g_iter0 2-0*) |
| 30 | NicholasKelly15.gopher10 | 1718 | 137 | 47 | 31-16 | 100% (g_iter0 2-0*) |
| 31 | **us:c_line5** | 1712 | 92 | 100 | 28-72 |  |
| 32 | battlecode-archive.Sprint1 | 1704 | 73 | 113 | 59-54 | 58% (g_iter0 7-5*) |
| 33 | louishu17.louisv10 | 1692 | 127 | 50 | 28-22 | 100% (g_iter0 2-0*) |
| 34 | polyllc.poly | 1688 | 172 | 47 | 28-19 | 100% (g_iter0 2-0*) |
| 35 | reeceyang.v5anaconda | 1686 | 75 | 113 | 59-54 | 58% (g_iter0 7-5*) |
| 36 | ipince.bobby | 1682 | 152 | 29 | 14-15 | 100% (g_iter0 2-0*) |
| 37 | **us:c_line4** | 1673 | 95 | 100 | 25-75 |  |
| 38 | legobridge.tacoplayer | 1661 | 107 | 79 | 42-37 | 85% (g_iter0 11-2*) |
| 39 | toyat522.bot5a | 1654 | 127 | 53 | 28-25 | 80% (g_iter0 4-1*) |
| 40 | ColtG5.rexv9 | 1630 | 128 | 55 | 27-28 | 100% (g_iter0 2-0*) |
| 41 | SteamBlizzard.newVnewME | 1602 | 113 | 59 | 29-30 | 80% (g_iter0 4-1*) |
| 42 | TheK098.qp1_7_sprint_1 | 1578 | 129 | 47 | 25-22 | 100% (g_iter0 2-0*) |
| 43 | elgoldie.head_v5 | 1578 | 102 | 62 | 26-36 | 100% (g_iter0 2-0*) |
| 44 | DukeBas._main | 1564 | 134 | 47 | 23-24 | 100% (g_iter0 2-0*) |
| 45 | beaverbois.USQualifiers | 1550 | 123 | 47 | 23-24 | 50% (g_iter0 1-1*) |
| 46 | BrysonJGalapon.friday | 1545 | 107 | 65 | 37-28 | 100% (g_iter0 2-0*) |
| 47 | nail-e.Barry | 1512 | 110 | 56 | 34-22 | 100% (g_iter0 2-0*) |
| 48 | kevinli405.maggi3_2 | 1487 | 135 | 56 | 24-32 | 100% (g_iter0 2-0*) |
| 49 | prisms-cs-club.prisms10 | 1472 | 124 | 59 | 28-31 | 100% (g_iter0 2-0*) |
| 50 | Nawlej.PoonPoon | 1444 | 118 | 53 | 28-25 | 100% (g_iter0 2-0*) |
| 51 | kevinli405.maggi3 | 1434 | 121 | 59 | 32-27 | 100% (g_iter0 5-0*) |
| 52 | yaonam.PoonPoonv4 | 1418 | 85 | 131 | 42-89 | 87% (g_iter0 13-2*) |
| 53 | aj-chau.attempt1 | 1390 | 128 | 50 | 24-26 | 100% (g_iter0 5-0*) |
| 54 | BrysonJGalapon.aloha | 1373 | 116 | 50 | 25-25 | 100% (g_iter0 2-0*) |
| 55 | andrewgopher.gopherbot | 1361 | 98 | 68 | 35-33 | 100% (g_iter0 2-0*) |
| 56 | mama4294.currentPlayer | 1357 | 140 | 41 | 19-22 | 100% (g_iter0 2-0*) |
| 57 | bewuwy.deathbot4 | 1341 | 102 | 74 | 26-48 | 100% (g_iter0 2-0*) |
| 58 | ipince.bobby_v2 | 1322 | 116 | 56 | 21-35 | 100% (g_iter0 5-0*) |
| 59 | SDainard-PDX.Team_Player | 1306 | 135 | 50 | 21-29 | 100% (g_iter0 2-0*) |
| 60 | Nawlej.PoonPoonv3 | 1304 | 106 | 62 | 25-37 | 100% (g_iter0 5-0*) |
| 61 | JfeMak.realplayer2 | 1303 | 110 | 52 | 25-27 | 100% (g_iter0 2-0*) |
| 62 | PSUtblock.sprint_four_player | 1303 | 187 | 35 | 16-19 | 100% (g_iter0 2-0*) |
| 63 | JackLee9355.jackPlayer | 1296 | 113 | 62 | 26-36 | 100% (g_iter0 2-0*) |
| 64 | jyorkio.elicompbot | 1284 | 120 | 44 | 21-23 | 100% (g_iter0 2-0*) |
| 65 | **us:examplefuncsplayer** | 1283 | 380 | 6 | 0-6 |  |
| 66 | NolanChai.nolan_1 | 1279 | 100 | 65 | 23-42 | 100% (g_iter0 2-0*) |
| 67 | SampleProvider.SPAARK_1_12_2023 | 1279 | 125 | 50 | 21-29 | 100% (g_iter0 2-0*) |
| 68 | andrewgopher.gopherbot1 | 1255 | 97 | 80 | 29-51 | 100% (g_iter0 2-0*) |
| 69 | vontell.regressiongames | 1249 | 106 | 56 | 22-34 | 100% (g_iter0 5-0*) |
| 70 | anicolao.submission | 1246 | 102 | 67 | 28-39 | 100% (g_iter0 2-0*) |
| 71 | ax-95174.MPAction | 1237 | 119 | 53 | 22-31 | 100% (g_iter0 2-0*) |
| 72 | michael-tyl.hqrewrite | 1206 | 114 | 59 | 22-37 | 100% (g_iter0 2-0*) |
| 73 | SteamBlizzard.Block | 1199 | 113 | 76 | 21-55 | 100% (g_iter0 5-0*) |
| 74 | legobridge.kushalplayer | 1181 | 172 | 38 | 8-30 | 100% (g_iter0 2-0*) |
| 75 | Patela171.Battlecode2023_Robot | 1177 | 110 | 65 | 26-39 | 100% (g_iter0 2-0*) |
| 76 | Chahat08.toph | 1169 | 109 | 59 | 19-40 | 100% (g_iter0 2-0*) |
| 77 | Juanbri02.matfisplayer1 | 1143 | 155 | 50 | 16-34 | 100% (g_iter0 5-0*) |
| 78 | nail-e.Dante | 1136 | 128 | 47 | 26-21 | 100% (g_iter0 2-0*) |
| 79 | mama4294.learningBot | 1062 | 158 | 56 | 12-44 | 100% (g_iter0 2-0*) |
| 80 | addiesteward.elicompbot | 1062 | 132 | 53 | 16-37 | 100% (g_iter0 5-0*) |
| 81 | team-remember-to-hydrate.sprint_1 | 1048 | 133 | 59 | 13-46 | 100% (g_iter0 2-0*) |
| 82 | toyat522.bot5 | 1036 | 156 | 50 | 9-41 | 100% (g_iter0 2-0*) |
| 83 | Vinceyou1.Player1 | 982 | 123 | 59 | 19-40 | 100% (g_iter0 2-0*) |
| 84 | Swordman51.AdeptusAstartes2 | 947 | 141 | 49 | 13-36 | 100% (g_iter0 2-0*) |
| 85 | monmouth-college-cs.elicompbot | 928 | 127 | 65 | 17-48 | 100% (g_iter0 2-0*) |
| 86 | michael-tyl.cc_v0_5_0_6 | 900 | 119 | 74 | 19-55 | 100% (g_iter0 2-0*) |
| 87 | Chahat08.lazarus | 854 | 185 | 41 | 5-36 | 100% (g_iter0 2-0*) |
| 88 | ShatterXD.SRNNbot | 813 | 150 | 47 | 10-37 | 100% (g_iter0 2-0*) |
| 89 | addiesteward.NDeClaw | 692 | 155 | 68 | 11-57 | 100% (g_iter0 5-0*) |
| 90 | CodeClash-ai.mysubmission | 692 | 175 | 58 | 7-51 | 100% (g_iter0 2-0*) |
| 91 | anicolao.jumbled | 650 | 169 | 53 | 6-47 | 100% (g_iter0 5-0*) |
| 92 | NotLLeon.player | 624 | 259 | 32 | 1-31 | 100% (g_iter0 2-0*) |
| 93 | andrewkbank.First | 617 | 180 | 38 | 4-34 | 100% (g_iter0 2-0*) |
| 94 | Yooncw0223.lec3player | 459 | 188 | 77 | 3-74 | 100% (g_iter0 5-0*) |
