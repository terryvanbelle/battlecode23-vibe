# Ladder

5380 games (1276 ours, 4104 between field bots on the ladder replica), 5352 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_swarm1 | 1857 +- 49 | 20 of 95 | 262 | 123-139 | 74.5% | 21.5% (vs 19) |
| g_iter0 | 1817 +- 48 | 21 of 95 | 456 | 230-226 | 72.4% | 18.3% (vs 19) |
| c_line8a | 1817 +- 72 | 22 of 95 | 139 | 47-92 | 72.3% | 18.3% (vs 19) |
| c_line6 | 1786 +- 89 | 26 of 95 | 100 | 32-68 | 70.6% | 20.1% (vs 22) |
| c_line7m | 1774 +- 89 | 29 of 95 | 100 | 31-69 | 69.9% | 21.7% (vs 24) |
| c_line5 | 1737 +- 92 | 31 of 95 | 100 | 28-72 | 67.7% | 20.0% (vs 25) |
| c_line4 | 1698 +- 95 | 36 of 95 | 100 | 25-75 | 65.3% | 21.0% (vs 29) |
| examplefuncsplayer | 1267 +- 380 | 63 of 95 | 6 | 0-6 | 36.5% | 13.3% (vs 55) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2398 | 117 | 77 | 65-12 | 0% (g_iter0 0-5*) |
| 2 | IvanGeffner.fortytwo | 2396 | 94 | 105 | 86-19 | 0% (g_iter0 0-36) |
| 3 | carlguo866.submit26_final | 2371 | 125 | 73 | 61-12 | 0% (g_iter0 0-2*) |
| 4 | awesomelemonade.finalBot | 2350 | 102 | 150 | 133-17 | 0% (g_iter0 0-15*) |
| 5 | vrangr1.AFinalsBot | 2291 | 106 | 146 | 134-12 | 7% (g_iter0 1-14*) |
| 6 | pranayagra.finalbotfinaltwo | 2234 | 98 | 97 | 72-25 | 7% (g_iter0 1-13*) |
| 7 | AnOvercookedFork.quals | 2228 | 117 | 77 | 60-17 | 20% (g_iter0 1-4*) |
| 8 | battlecode-archive.sprintBot | 2215 | 136 | 73 | 62-11 | 0% (g_iter0 0-2*) |
| 9 | pranayagra.finalbotfinal | 2214 | 73 | 189 | 148-41 | 13% (g_iter0 6-39) |
| 10 | georgezhang02.FB_ZZZ | 2133 | 99 | 83 | 57-26 | 0% (g_iter0 0-2*) |
| 11 | jmerle.camel_case_v30_final | 2111 | 69 | 180 | 136-44 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2018 | 88 | 91 | 63-28 | 0% (g_iter0 0-2*) |
| 13 | CyrilSharma.finalBot | 1997 | 100 | 92 | 62-30 | 0% (g_iter0 0-2*) |
| 14 | NotLLeon.v7 | 1979 | 70 | 146 | 107-39 | 17% (g_iter0 2-10*) |
| 15 | georgezhang02.CB_tuning2 | 1976 | 66 | 158 | 111-47 | 7% (g_iter0 1-14*) |
| 16 | GabeG888.v8o1 | 1926 | 108 | 71 | 51-20 | 0% (g_iter0 0-2*) |
| 17 | britacatalin.FinalBot | 1921 | 68 | 143 | 98-45 | 42% (g_iter0 5-7*) |
| 18 | ethanlabelle.v19 | 1883 | 96 | 78 | 52-26 | 50% (g_iter0 1-1*) |
| 19 | GabeG888.v8 | 1862 | 83 | 89 | 54-35 | 50% (g_iter0 1-1*) |
| 20 | **us:c_swarm1** | 1857 | 49 | 262 | 123-139 |  |
| 21 | **us:g_iter0** | 1817 | 48 | 456 | 230-226 |  |
| 22 | **us:c_line8a** | 1817 | 72 | 139 | 47-92 |  |
| 23 | DannyZhang686.pqual2 | 1815 | 84 | 104 | 57-47 | 29% (g_iter0 4-10*) |
| 24 | VarunVejalla.karel | 1815 | 79 | 113 | 62-51 | 50% (g_iter0 4-4*) |
| 25 | programjames.fourthbot | 1807 | 84 | 101 | 59-42 | 100% (g_iter0 2-0*) |
| 26 | **us:c_line6** | 1786 | 89 | 100 | 32-68 |  |
| 27 | NicholasKelly15.gopher10 | 1784 | 105 | 71 | 47-24 | 100% (g_iter0 2-0*) |
| 28 | louishu17.louisv10 | 1776 | 96 | 86 | 54-32 | 100% (g_iter0 2-0*) |
| 29 | **us:c_line7m** | 1774 | 89 | 100 | 31-69 |  |
| 30 | battlecode-archive.Sprint1 | 1746 | 61 | 155 | 80-75 | 58% (g_iter0 7-5*) |
| 31 | **us:c_line5** | 1737 | 92 | 100 | 28-72 |  |
| 32 | reeceyang.v5anaconda | 1737 | 61 | 163 | 84-79 | 58% (g_iter0 7-5*) |
| 33 | louishu17.wouisv8 | 1737 | 86 | 110 | 61-49 | 50% (g_iter0 5-5*) |
| 34 | VarunVejalla.ali8 | 1736 | 101 | 80 | 49-31 | 50% (g_iter0 1-1*) |
| 35 | SampleProvider.SPAARK | 1716 | 90 | 88 | 52-36 | 100% (g_iter0 2-0*) |
| 36 | **us:c_line4** | 1698 | 95 | 100 | 25-75 |  |
| 37 | ipince.bobby | 1683 | 98 | 83 | 51-32 | 100% (g_iter0 2-0*) |
| 38 | polyllc.poly | 1658 | 105 | 86 | 47-39 | 100% (g_iter0 2-0*) |
| 39 | legobridge.tacoplayer | 1653 | 85 | 112 | 62-50 | 85% (g_iter0 11-2*) |
| 40 | SteamBlizzard.newVnewME | 1611 | 82 | 103 | 51-52 | 80% (g_iter0 4-1*) |
| 41 | DukeBas._main | 1603 | 92 | 89 | 51-38 | 100% (g_iter0 2-0*) |
| 42 | toyat522.bot5a | 1596 | 82 | 104 | 53-51 | 80% (g_iter0 4-1*) |
| 43 | elgoldie.head_v5 | 1583 | 81 | 95 | 45-50 | 100% (g_iter0 2-0*) |
| 44 | ColtG5.rexv9 | 1578 | 87 | 97 | 49-48 | 100% (g_iter0 2-0*) |
| 45 | TheK098.qp1_7_sprint_1 | 1565 | 89 | 95 | 54-41 | 100% (g_iter0 2-0*) |
| 46 | beaverbois.USQualifiers | 1555 | 91 | 83 | 45-38 | 50% (g_iter0 1-1*) |
| 47 | kevinli405.maggi3_2 | 1539 | 91 | 98 | 51-47 | 100% (g_iter0 2-0*) |
| 48 | BrysonJGalapon.friday | 1518 | 82 | 97 | 51-46 | 100% (g_iter0 2-0*) |
| 49 | nail-e.Barry | 1487 | 91 | 82 | 45-37 | 100% (g_iter0 2-0*) |
| 50 | Nawlej.PoonPoon | 1477 | 92 | 89 | 45-44 | 100% (g_iter0 2-0*) |
| 51 | prisms-cs-club.prisms10 | 1425 | 86 | 98 | 44-54 | 100% (g_iter0 2-0*) |
| 52 | yaonam.PoonPoonv4 | 1420 | 64 | 197 | 71-126 | 87% (g_iter0 13-2*) |
| 53 | aj-chau.attempt1 | 1418 | 104 | 77 | 42-35 | 100% (g_iter0 5-0*) |
| 54 | mama4294.currentPlayer | 1383 | 92 | 92 | 46-46 | 100% (g_iter0 2-0*) |
| 55 | ipince.bobby_v2 | 1382 | 84 | 101 | 48-53 | 100% (g_iter0 5-0*) |
| 56 | kevinli405.maggi3 | 1381 | 87 | 101 | 48-53 | 100% (g_iter0 5-0*) |
| 57 | BrysonJGalapon.aloha | 1352 | 83 | 92 | 46-46 | 100% (g_iter0 2-0*) |
| 58 | bewuwy.deathbot4 | 1342 | 70 | 134 | 59-75 | 100% (g_iter0 2-0*) |
| 59 | andrewgopher.gopherbot | 1326 | 77 | 116 | 51-65 | 100% (g_iter0 2-0*) |
| 60 | JfeMak.realplayer2 | 1319 | 82 | 94 | 45-49 | 100% (g_iter0 2-0*) |
| 61 | SampleProvider.SPAARK_1_12_2023 | 1297 | 79 | 104 | 49-55 | 100% (g_iter0 2-0*) |
| 62 | SDainard-PDX.Team_Player | 1269 | 98 | 83 | 38-45 | 100% (g_iter0 2-0*) |
| 63 | **us:examplefuncsplayer** | 1267 | 380 | 6 | 0-6 |  |
| 64 | PSUtblock.sprint_four_player | 1265 | 97 | 92 | 43-49 | 100% (g_iter0 2-0*) |
| 65 | jyorkio.elicompbot | 1259 | 82 | 92 | 44-48 | 100% (g_iter0 2-0*) |
| 66 | Nawlej.PoonPoonv3 | 1251 | 72 | 124 | 52-72 | 100% (g_iter0 5-0*) |
| 67 | JackLee9355.jackPlayer | 1249 | 75 | 122 | 49-73 | 100% (g_iter0 2-0*) |
| 68 | andrewgopher.gopherbot1 | 1247 | 82 | 110 | 46-64 | 100% (g_iter0 2-0*) |
| 69 | NolanChai.nolan_1 | 1241 | 86 | 95 | 40-55 | 100% (g_iter0 2-0*) |
| 70 | Juanbri02.matfisplayer1 | 1231 | 82 | 104 | 45-59 | 100% (g_iter0 5-0*) |
| 71 | SteamBlizzard.Block | 1207 | 75 | 129 | 49-80 | 100% (g_iter0 5-0*) |
| 72 | vontell.regressiongames | 1190 | 73 | 110 | 48-62 | 100% (g_iter0 5-0*) |
| 73 | ax-95174.MPAction | 1155 | 86 | 92 | 36-56 | 100% (g_iter0 2-0*) |
| 74 | legobridge.kushalplayer | 1143 | 98 | 89 | 35-54 | 100% (g_iter0 2-0*) |
| 75 | Chahat08.toph | 1140 | 75 | 112 | 45-67 | 100% (g_iter0 2-0*) |
| 76 | michael-tyl.hqrewrite | 1119 | 74 | 119 | 50-69 | 100% (g_iter0 2-0*) |
| 77 | anicolao.submission | 1118 | 71 | 135 | 53-82 | 100% (g_iter0 2-0*) |
| 78 | Patela171.Battlecode2023_Robot | 1106 | 79 | 113 | 43-70 | 100% (g_iter0 2-0*) |
| 79 | nail-e.Dante | 1073 | 82 | 104 | 49-55 | 100% (g_iter0 2-0*) |
| 80 | mama4294.learningBot | 1063 | 86 | 110 | 38-72 | 100% (g_iter0 2-0*) |
| 81 | team-remember-to-hydrate.sprint_1 | 999 | 82 | 113 | 39-74 | 100% (g_iter0 2-0*) |
| 82 | Vinceyou1.Player1 | 954 | 87 | 98 | 37-61 | 100% (g_iter0 2-0*) |
| 83 | addiesteward.elicompbot | 926 | 74 | 130 | 49-81 | 100% (g_iter0 5-0*) |
| 84 | michael-tyl.cc_v0_5_0_6 | 906 | 71 | 146 | 51-95 | 100% (g_iter0 2-0*) |
| 85 | toyat522.bot5 | 901 | 91 | 107 | 35-72 | 100% (g_iter0 2-0*) |
| 86 | monmouth-college-cs.elicompbot | 888 | 82 | 116 | 42-74 | 100% (g_iter0 2-0*) |
| 87 | Swordman51.AdeptusAstartes2 | 847 | 74 | 124 | 45-79 | 100% (g_iter0 2-0*) |
| 88 | Chahat08.lazarus | 831 | 90 | 101 | 36-65 | 100% (g_iter0 2-0*) |
| 89 | ShatterXD.SRNNbot | 755 | 87 | 106 | 38-68 | 100% (g_iter0 2-0*) |
| 90 | anicolao.jumbled | 695 | 73 | 148 | 54-94 | 100% (g_iter0 5-0*) |
| 91 | NotLLeon.player | 620 | 87 | 116 | 39-77 | 100% (g_iter0 2-0*) |
| 92 | CodeClash-ai.mysubmission | 604 | 87 | 121 | 36-85 | 100% (g_iter0 2-0*) |
| 93 | addiesteward.NDeClaw | 565 | 86 | 136 | 44-92 | 100% (g_iter0 5-0*) |
| 94 | andrewkbank.First | 308 | 117 | 95 | 11-84 | 100% (g_iter0 2-0*) |
| 95 | Yooncw0223.lec3player | 292 | 114 | 141 | 11-130 | 100% (g_iter0 5-0*) |
