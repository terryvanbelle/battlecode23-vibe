# Ladder

4810 games (1198 ours, 3612 between field bots on the ladder replica), 4790 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_swarm1 | 1869 +- 60 | 19 of 95 | 188 | 88-100 | 75.3% | 20.7% (vs 18) |
| c_line8a | 1816 +- 73 | 22 of 95 | 139 | 47-92 | 72.4% | 19.5% (vs 20) |
| g_iter0 | 1815 +- 48 | 23 of 95 | 456 | 230-226 | 72.4% | 19.5% (vs 20) |
| c_line6 | 1778 +- 89 | 26 of 95 | 100 | 32-68 | 70.2% | 19.4% (vs 22) |
| c_line7m | 1766 +- 90 | 27 of 95 | 100 | 31-69 | 69.5% | 18.5% (vs 22) |
| c_line5 | 1728 +- 92 | 32 of 95 | 100 | 28-72 | 67.3% | 20.7% (vs 26) |
| c_line4 | 1688 +- 95 | 36 of 95 | 100 | 25-75 | 64.8% | 20.6% (vs 29) |
| examplefuncsplayer | 1270 +- 380 | 65 of 95 | 6 | 0-6 | 36.4% | 14.6% (vs 57) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2410 | 122 | 74 | 63-11 | 0% (g_iter0 0-5*) |
| 2 | IvanGeffner.fortytwo | 2393 | 99 | 99 | 82-17 | 0% (g_iter0 0-36) |
| 3 | carlguo866.submit26_final | 2387 | 133 | 70 | 60-10 | 0% (g_iter0 0-2*) |
| 4 | awesomelemonade.finalBot | 2360 | 107 | 147 | 132-15 | 0% (g_iter0 0-15*) |
| 5 | vrangr1.AFinalsBot | 2293 | 107 | 146 | 134-12 | 7% (g_iter0 1-14*) |
| 6 | pranayagra.finalbotfinaltwo | 2240 | 99 | 97 | 72-25 | 7% (g_iter0 1-13*) |
| 7 | AnOvercookedFork.quals | 2231 | 119 | 77 | 60-17 | 20% (g_iter0 1-4*) |
| 8 | pranayagra.finalbotfinal | 2217 | 73 | 189 | 148-41 | 13% (g_iter0 6-39) |
| 9 | battlecode-archive.sprintBot | 2212 | 143 | 70 | 61-9 | 0% (g_iter0 0-2*) |
| 10 | georgezhang02.FB_ZZZ | 2167 | 108 | 71 | 49-22 | 0% (g_iter0 0-2*) |
| 11 | jmerle.camel_case_v30_final | 2127 | 74 | 171 | 132-39 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2048 | 97 | 82 | 60-22 | 0% (g_iter0 0-2*) |
| 13 | georgezhang02.CB_tuning2 | 1981 | 69 | 150 | 107-43 | 7% (g_iter0 1-14*) |
| 14 | NotLLeon.v7 | 1954 | 70 | 140 | 101-39 | 17% (g_iter0 2-10*) |
| 15 | CyrilSharma.finalBot | 1951 | 110 | 83 | 56-27 | 0% (g_iter0 0-2*) |
| 16 | GabeG888.v8o1 | 1947 | 121 | 62 | 46-16 | 0% (g_iter0 0-2*) |
| 17 | britacatalin.FinalBot | 1918 | 70 | 137 | 94-43 | 42% (g_iter0 5-7*) |
| 18 | ethanlabelle.v19 | 1889 | 99 | 76 | 51-25 | 50% (g_iter0 1-1*) |
| 19 | **us:c_swarm1** | 1869 | 60 | 188 | 88-100 |  |
| 20 | GabeG888.v8 | 1861 | 92 | 77 | 46-31 | 50% (g_iter0 1-1*) |
| 21 | VarunVejalla.karel | 1834 | 91 | 95 | 55-40 | 50% (g_iter0 4-4*) |
| 22 | **us:c_line8a** | 1816 | 73 | 139 | 47-92 |  |
| 23 | **us:g_iter0** | 1815 | 48 | 456 | 230-226 |  |
| 24 | DannyZhang686.pqual2 | 1804 | 86 | 101 | 55-46 | 29% (g_iter0 4-10*) |
| 25 | programjames.fourthbot | 1796 | 99 | 80 | 47-33 | 100% (g_iter0 2-0*) |
| 26 | **us:c_line6** | 1778 | 89 | 100 | 32-68 |  |
| 27 | **us:c_line7m** | 1766 | 90 | 100 | 31-69 |  |
| 28 | NicholasKelly15.gopher10 | 1758 | 107 | 68 | 44-24 | 100% (g_iter0 2-0*) |
| 29 | louishu17.wouisv8 | 1755 | 90 | 104 | 58-46 | 50% (g_iter0 5-5*) |
| 30 | battlecode-archive.Sprint1 | 1736 | 64 | 143 | 74-69 | 58% (g_iter0 7-5*) |
| 31 | louishu17.louisv10 | 1730 | 101 | 80 | 49-31 | 100% (g_iter0 2-0*) |
| 32 | **us:c_line5** | 1728 | 92 | 100 | 28-72 |  |
| 33 | SampleProvider.SPAARK | 1728 | 99 | 76 | 48-28 | 100% (g_iter0 2-0*) |
| 34 | VarunVejalla.ali8 | 1726 | 103 | 77 | 47-30 | 50% (g_iter0 1-1*) |
| 35 | reeceyang.v5anaconda | 1711 | 65 | 147 | 75-72 | 58% (g_iter0 7-5*) |
| 36 | **us:c_line4** | 1688 | 95 | 100 | 25-75 |  |
| 37 | ipince.bobby | 1685 | 119 | 65 | 42-23 | 100% (g_iter0 2-0*) |
| 38 | polyllc.poly | 1650 | 113 | 77 | 43-34 | 100% (g_iter0 2-0*) |
| 39 | legobridge.tacoplayer | 1633 | 92 | 100 | 53-47 | 85% (g_iter0 11-2*) |
| 40 | toyat522.bot5a | 1621 | 93 | 86 | 44-42 | 80% (g_iter0 4-1*) |
| 41 | SteamBlizzard.newVnewME | 1602 | 89 | 92 | 44-48 | 80% (g_iter0 4-1*) |
| 42 | DukeBas._main | 1602 | 98 | 80 | 48-32 | 100% (g_iter0 2-0*) |
| 43 | elgoldie.head_v5 | 1586 | 85 | 89 | 43-46 | 100% (g_iter0 2-0*) |
| 44 | beaverbois.USQualifiers | 1579 | 101 | 71 | 40-31 | 50% (g_iter0 1-1*) |
| 45 | ColtG5.rexv9 | 1567 | 98 | 82 | 39-43 | 100% (g_iter0 2-0*) |
| 46 | TheK098.qp1_7_sprint_1 | 1534 | 107 | 71 | 42-29 | 100% (g_iter0 2-0*) |
| 47 | kevinli405.maggi3_2 | 1533 | 102 | 86 | 46-40 | 100% (g_iter0 2-0*) |
| 48 | BrysonJGalapon.friday | 1523 | 89 | 86 | 45-41 | 100% (g_iter0 2-0*) |
| 49 | nail-e.Barry | 1499 | 93 | 77 | 42-35 | 100% (g_iter0 2-0*) |
| 50 | Nawlej.PoonPoon | 1442 | 99 | 80 | 39-41 | 100% (g_iter0 2-0*) |
| 51 | prisms-cs-club.prisms10 | 1426 | 97 | 83 | 37-46 | 100% (g_iter0 2-0*) |
| 52 | yaonam.PoonPoonv4 | 1405 | 73 | 171 | 56-115 | 87% (g_iter0 13-2*) |
| 53 | aj-chau.attempt1 | 1399 | 113 | 68 | 36-32 | 100% (g_iter0 5-0*) |
| 54 | ipince.bobby_v2 | 1398 | 89 | 92 | 46-46 | 100% (g_iter0 5-0*) |
| 55 | kevinli405.maggi3 | 1396 | 93 | 92 | 45-47 | 100% (g_iter0 5-0*) |
| 56 | mama4294.currentPlayer | 1381 | 102 | 77 | 39-38 | 100% (g_iter0 2-0*) |
| 57 | BrysonJGalapon.aloha | 1361 | 93 | 77 | 39-38 | 100% (g_iter0 2-0*) |
| 58 | bewuwy.deathbot4 | 1340 | 73 | 122 | 51-71 | 100% (g_iter0 2-0*) |
| 59 | andrewgopher.gopherbot | 1329 | 82 | 104 | 45-59 | 100% (g_iter0 2-0*) |
| 60 | PSUtblock.sprint_four_player | 1327 | 109 | 80 | 41-39 | 100% (g_iter0 2-0*) |
| 61 | SampleProvider.SPAARK_1_12_2023 | 1307 | 93 | 80 | 39-41 | 100% (g_iter0 2-0*) |
| 62 | JfeMak.realplayer2 | 1301 | 86 | 85 | 39-46 | 100% (g_iter0 2-0*) |
| 63 | JackLee9355.jackPlayer | 1287 | 82 | 107 | 44-63 | 100% (g_iter0 2-0*) |
| 64 | SDainard-PDX.Team_Player | 1273 | 103 | 77 | 35-42 | 100% (g_iter0 2-0*) |
| 65 | **us:examplefuncsplayer** | 1270 | 380 | 6 | 0-6 |  |
| 66 | jyorkio.elicompbot | 1269 | 96 | 71 | 35-36 | 100% (g_iter0 2-0*) |
| 67 | NolanChai.nolan_1 | 1251 | 91 | 86 | 34-52 | 100% (g_iter0 2-0*) |
| 68 | andrewgopher.gopherbot1 | 1237 | 83 | 107 | 43-64 | 100% (g_iter0 2-0*) |
| 69 | Nawlej.PoonPoonv3 | 1237 | 79 | 109 | 41-68 | 100% (g_iter0 5-0*) |
| 70 | Juanbri02.matfisplayer1 | 1232 | 87 | 95 | 41-54 | 100% (g_iter0 5-0*) |
| 71 | SteamBlizzard.Block | 1205 | 80 | 117 | 42-75 | 100% (g_iter0 5-0*) |
| 72 | vontell.regressiongames | 1181 | 82 | 92 | 39-53 | 100% (g_iter0 5-0*) |
| 73 | legobridge.kushalplayer | 1175 | 102 | 83 | 34-49 | 100% (g_iter0 2-0*) |
| 74 | michael-tyl.hqrewrite | 1170 | 86 | 95 | 42-53 | 100% (g_iter0 2-0*) |
| 75 | anicolao.submission | 1168 | 81 | 105 | 39-66 | 100% (g_iter0 2-0*) |
| 76 | ax-95174.MPAction | 1151 | 95 | 80 | 29-51 | 100% (g_iter0 2-0*) |
| 77 | Chahat08.toph | 1149 | 81 | 100 | 39-61 | 100% (g_iter0 2-0*) |
| 78 | Patela171.Battlecode2023_Robot | 1102 | 86 | 101 | 36-65 | 100% (g_iter0 2-0*) |
| 79 | nail-e.Dante | 1065 | 86 | 95 | 45-50 | 100% (g_iter0 2-0*) |
| 80 | mama4294.learningBot | 1047 | 98 | 95 | 29-66 | 100% (g_iter0 2-0*) |
| 81 | team-remember-to-hydrate.sprint_1 | 1007 | 94 | 92 | 30-62 | 100% (g_iter0 2-0*) |
| 82 | addiesteward.elicompbot | 952 | 82 | 110 | 38-72 | 100% (g_iter0 5-0*) |
| 83 | michael-tyl.cc_v0_5_0_6 | 929 | 79 | 125 | 43-82 | 100% (g_iter0 2-0*) |
| 84 | Vinceyou1.Player1 | 926 | 95 | 89 | 30-59 | 100% (g_iter0 2-0*) |
| 85 | toyat522.bot5 | 902 | 103 | 92 | 28-64 | 100% (g_iter0 2-0*) |
| 86 | Swordman51.AdeptusAstartes2 | 868 | 93 | 88 | 28-60 | 100% (g_iter0 2-0*) |
| 87 | monmouth-college-cs.elicompbot | 848 | 95 | 98 | 30-68 | 100% (g_iter0 2-0*) |
| 88 | Chahat08.lazarus | 838 | 105 | 86 | 28-58 | 100% (g_iter0 2-0*) |
| 89 | ShatterXD.SRNNbot | 765 | 91 | 98 | 34-64 | 100% (g_iter0 2-0*) |
| 90 | anicolao.jumbled | 684 | 86 | 118 | 38-80 | 100% (g_iter0 5-0*) |
| 91 | NotLLeon.player | 638 | 97 | 92 | 26-66 | 100% (g_iter0 2-0*) |
| 92 | CodeClash-ai.mysubmission | 620 | 96 | 103 | 28-75 | 100% (g_iter0 2-0*) |
| 93 | addiesteward.NDeClaw | 595 | 97 | 113 | 33-80 | 100% (g_iter0 5-0*) |
| 94 | andrewkbank.First | 427 | 123 | 77 | 11-66 | 100% (g_iter0 2-0*) |
| 95 | Yooncw0223.lec3player | 310 | 125 | 133 | 8-125 | 100% (g_iter0 5-0*) |
