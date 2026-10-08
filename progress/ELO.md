# Ladder

3523 games (1108 ours, 2415 between field bots on the ladder replica), 3511 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_swarm1 | 1849 +- 86 | 19 of 95 | 100 | 40-60 | 74.6% | 19.9% (vs 18) |
| g_iter0 | 1803 +- 48 | 20 of 95 | 456 | 230-226 | 72.1% | 16.6% (vs 18) |
| c_line8a | 1795 +- 73 | 22 of 95 | 139 | 47-92 | 71.6% | 17.7% (vs 19) |
| c_line6 | 1758 +- 89 | 27 of 95 | 100 | 32-68 | 69.4% | 20.7% (vs 23) |
| c_line7m | 1746 +- 90 | 29 of 95 | 100 | 31-69 | 68.7% | 20.9% (vs 24) |
| c_line5 | 1708 +- 92 | 32 of 95 | 100 | 28-72 | 66.4% | 20.5% (vs 26) |
| c_line4 | 1669 +- 95 | 38 of 95 | 100 | 25-75 | 63.9% | 22.4% (vs 31) |
| examplefuncsplayer | 1291 +- 380 | 65 of 95 | 6 | 0-6 | 37.2% | 16.1% (vs 57) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | carlguo866.submit26_final | 2435 | 221 | 52 | 50-2 | 0% (g_iter0 0-2*) |
| 2 | IvanGeffner.fortytwo | 2382 | 114 | 87 | 76-11 | 0% (g_iter0 0-36) |
| 3 | battlecode-archive.sprintBot | 2380 | 281 | 47 | 46-1 | 0% (g_iter0 0-2*) |
| 4 | awesomelemonade.finalBot | 2336 | 131 | 132 | 124-8 | 0% (g_iter0 0-15*) |
| 5 | vrangr1.AFinalsBot | 2316 | 145 | 126 | 120-6 | 7% (g_iter0 1-14*) |
| 6 | maxwelljones14.MPWorking | 2314 | 140 | 62 | 53-9 | 0% (g_iter0 0-5*) |
| 7 | AnOvercookedFork.quals | 2240 | 172 | 53 | 47-6 | 20% (g_iter0 1-4*) |
| 8 | pranayagra.finalbotfinaltwo | 2221 | 112 | 85 | 66-19 | 7% (g_iter0 1-13*) |
| 9 | pranayagra.finalbotfinal | 2191 | 78 | 174 | 138-36 | 13% (g_iter0 6-39) |
| 10 | georgezhang02.FB_ZZZ | 2188 | 143 | 53 | 42-11 | 0% (g_iter0 0-2*) |
| 11 | jmerle.camel_case_v30_final | 2115 | 82 | 150 | 119-31 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 1996 | 111 | 65 | 49-16 | 0% (g_iter0 0-2*) |
| 13 | GabeG888.v8o1 | 1970 | 144 | 44 | 32-12 | 0% (g_iter0 0-2*) |
| 14 | georgezhang02.CB_tuning2 | 1960 | 74 | 132 | 98-34 | 7% (g_iter0 1-14*) |
| 15 | CyrilSharma.finalBot | 1952 | 135 | 62 | 40-22 | 0% (g_iter0 0-2*) |
| 16 | NotLLeon.v7 | 1930 | 75 | 122 | 86-36 | 17% (g_iter0 2-10*) |
| 17 | britacatalin.FinalBot | 1889 | 76 | 117 | 83-34 | 42% (g_iter0 5-7*) |
| 18 | GabeG888.v8 | 1853 | 110 | 59 | 39-20 | 50% (g_iter0 1-1*) |
| 19 | **us:c_swarm1** | 1849 | 86 | 100 | 40-60 |  |
| 20 | **us:g_iter0** | 1803 | 48 | 456 | 230-226 |  |
| 21 | VarunVejalla.karel | 1801 | 96 | 80 | 43-37 | 50% (g_iter0 4-4*) |
| 22 | **us:c_line8a** | 1795 | 73 | 139 | 47-92 |  |
| 23 | ethanlabelle.v19 | 1794 | 132 | 50 | 35-15 | 50% (g_iter0 1-1*) |
| 24 | DannyZhang686.pqual2 | 1793 | 101 | 77 | 41-36 | 29% (g_iter0 4-10*) |
| 25 | programjames.fourthbot | 1771 | 132 | 53 | 32-21 | 100% (g_iter0 2-0*) |
| 26 | louishu17.wouisv8 | 1764 | 114 | 75 | 43-32 | 50% (g_iter0 5-5*) |
| 27 | **us:c_line6** | 1758 | 89 | 100 | 32-68 |  |
| 28 | VarunVejalla.ali8 | 1757 | 131 | 53 | 34-19 | 50% (g_iter0 1-1*) |
| 29 | **us:c_line7m** | 1746 | 90 | 100 | 31-69 |  |
| 30 | NicholasKelly15.gopher10 | 1718 | 137 | 47 | 31-16 | 100% (g_iter0 2-0*) |
| 31 | battlecode-archive.Sprint1 | 1713 | 69 | 123 | 64-59 | 58% (g_iter0 7-5*) |
| 32 | **us:c_line5** | 1708 | 92 | 100 | 28-72 |  |
| 33 | SampleProvider.SPAARK | 1697 | 123 | 56 | 37-19 | 100% (g_iter0 2-0*) |
| 34 | louishu17.louisv10 | 1688 | 127 | 53 | 31-22 | 100% (g_iter0 2-0*) |
| 35 | polyllc.poly | 1685 | 169 | 50 | 31-19 | 100% (g_iter0 2-0*) |
| 36 | ipince.bobby | 1685 | 152 | 32 | 17-15 | 100% (g_iter0 2-0*) |
| 37 | reeceyang.v5anaconda | 1682 | 70 | 126 | 63-63 | 58% (g_iter0 7-5*) |
| 38 | **us:c_line4** | 1669 | 95 | 100 | 25-75 |  |
| 39 | legobridge.tacoplayer | 1653 | 107 | 79 | 42-37 | 85% (g_iter0 11-2*) |
| 40 | toyat522.bot5a | 1644 | 126 | 53 | 28-25 | 80% (g_iter0 4-1*) |
| 41 | ColtG5.rexv9 | 1632 | 128 | 55 | 27-28 | 100% (g_iter0 2-0*) |
| 42 | SteamBlizzard.newVnewME | 1586 | 110 | 62 | 29-33 | 80% (g_iter0 4-1*) |
| 43 | DukeBas._main | 1576 | 123 | 56 | 31-25 | 100% (g_iter0 2-0*) |
| 44 | elgoldie.head_v5 | 1574 | 102 | 62 | 26-36 | 100% (g_iter0 2-0*) |
| 45 | BrysonJGalapon.friday | 1561 | 104 | 68 | 40-28 | 100% (g_iter0 2-0*) |
| 46 | beaverbois.USQualifiers | 1553 | 122 | 53 | 29-24 | 50% (g_iter0 1-1*) |
| 47 | TheK098.qp1_7_sprint_1 | 1544 | 127 | 50 | 26-24 | 100% (g_iter0 2-0*) |
| 48 | nail-e.Barry | 1503 | 107 | 59 | 34-25 | 100% (g_iter0 2-0*) |
| 49 | kevinli405.maggi3_2 | 1477 | 129 | 62 | 28-34 | 100% (g_iter0 2-0*) |
| 50 | prisms-cs-club.prisms10 | 1463 | 123 | 59 | 28-31 | 100% (g_iter0 2-0*) |
| 51 | Nawlej.PoonPoon | 1451 | 116 | 56 | 31-25 | 100% (g_iter0 2-0*) |
| 52 | yaonam.PoonPoonv4 | 1416 | 83 | 141 | 43-98 | 87% (g_iter0 13-2*) |
| 53 | kevinli405.maggi3 | 1400 | 117 | 62 | 32-30 | 100% (g_iter0 5-0*) |
| 54 | aj-chau.attempt1 | 1383 | 130 | 50 | 24-26 | 100% (g_iter0 5-0*) |
| 55 | BrysonJGalapon.aloha | 1364 | 113 | 53 | 27-26 | 100% (g_iter0 2-0*) |
| 56 | PSUtblock.sprint_four_player | 1351 | 162 | 44 | 25-19 | 100% (g_iter0 2-0*) |
| 57 | andrewgopher.gopherbot | 1350 | 99 | 68 | 35-33 | 100% (g_iter0 2-0*) |
| 58 | mama4294.currentPlayer | 1341 | 132 | 47 | 22-25 | 100% (g_iter0 2-0*) |
| 59 | bewuwy.deathbot4 | 1334 | 100 | 77 | 28-49 | 100% (g_iter0 2-0*) |
| 60 | ipince.bobby_v2 | 1321 | 115 | 56 | 21-35 | 100% (g_iter0 5-0*) |
| 61 | SampleProvider.SPAARK_1_12_2023 | 1300 | 119 | 53 | 24-29 | 100% (g_iter0 2-0*) |
| 62 | JackLee9355.jackPlayer | 1296 | 109 | 68 | 28-40 | 100% (g_iter0 2-0*) |
| 63 | SDainard-PDX.Team_Player | 1296 | 137 | 50 | 21-29 | 100% (g_iter0 2-0*) |
| 64 | JfeMak.realplayer2 | 1292 | 111 | 52 | 25-27 | 100% (g_iter0 2-0*) |
| 65 | **us:examplefuncsplayer** | 1291 | 380 | 6 | 0-6 |  |
| 66 | Nawlej.PoonPoonv3 | 1289 | 99 | 68 | 27-41 | 100% (g_iter0 5-0*) |
| 67 | jyorkio.elicompbot | 1276 | 119 | 44 | 21-23 | 100% (g_iter0 2-0*) |
| 68 | NolanChai.nolan_1 | 1271 | 101 | 65 | 23-42 | 100% (g_iter0 2-0*) |
| 69 | andrewgopher.gopherbot1 | 1244 | 97 | 80 | 29-51 | 100% (g_iter0 2-0*) |
| 70 | ax-95174.MPAction | 1224 | 120 | 53 | 22-31 | 100% (g_iter0 2-0*) |
| 71 | anicolao.submission | 1219 | 99 | 73 | 28-45 | 100% (g_iter0 2-0*) |
| 72 | vontell.regressiongames | 1219 | 103 | 59 | 22-37 | 100% (g_iter0 5-0*) |
| 73 | Juanbri02.matfisplayer1 | 1216 | 136 | 56 | 21-35 | 100% (g_iter0 5-0*) |
| 74 | SteamBlizzard.Block | 1194 | 109 | 82 | 22-60 | 100% (g_iter0 5-0*) |
| 75 | michael-tyl.hqrewrite | 1192 | 111 | 62 | 24-38 | 100% (g_iter0 2-0*) |
| 76 | Patela171.Battlecode2023_Robot | 1163 | 110 | 68 | 26-42 | 100% (g_iter0 2-0*) |
| 77 | Chahat08.toph | 1157 | 109 | 62 | 19-43 | 100% (g_iter0 2-0*) |
| 78 | legobridge.kushalplayer | 1116 | 159 | 47 | 11-36 | 100% (g_iter0 2-0*) |
| 79 | nail-e.Dante | 1114 | 117 | 56 | 30-26 | 100% (g_iter0 2-0*) |
| 80 | mama4294.learningBot | 1063 | 154 | 59 | 15-44 | 100% (g_iter0 2-0*) |
| 81 | addiesteward.elicompbot | 1031 | 121 | 62 | 18-44 | 100% (g_iter0 5-0*) |
| 82 | team-remember-to-hydrate.sprint_1 | 1031 | 127 | 62 | 14-48 | 100% (g_iter0 2-0*) |
| 83 | toyat522.bot5 | 1019 | 148 | 53 | 11-42 | 100% (g_iter0 2-0*) |
| 84 | Vinceyou1.Player1 | 970 | 114 | 65 | 21-44 | 100% (g_iter0 2-0*) |
| 85 | monmouth-college-cs.elicompbot | 913 | 128 | 65 | 17-48 | 100% (g_iter0 2-0*) |
| 86 | Swordman51.AdeptusAstartes2 | 905 | 132 | 55 | 14-41 | 100% (g_iter0 2-0*) |
| 87 | michael-tyl.cc_v0_5_0_6 | 899 | 114 | 77 | 20-57 | 100% (g_iter0 2-0*) |
| 88 | Chahat08.lazarus | 842 | 170 | 44 | 6-38 | 100% (g_iter0 2-0*) |
| 89 | ShatterXD.SRNNbot | 831 | 134 | 53 | 15-38 | 100% (g_iter0 2-0*) |
| 90 | anicolao.jumbled | 676 | 147 | 59 | 11-48 | 100% (g_iter0 5-0*) |
| 91 | addiesteward.NDeClaw | 661 | 159 | 71 | 11-60 | 100% (g_iter0 5-0*) |
| 92 | CodeClash-ai.mysubmission | 660 | 163 | 61 | 8-53 | 100% (g_iter0 2-0*) |
| 93 | NotLLeon.player | 607 | 260 | 35 | 1-34 | 100% (g_iter0 2-0*) |
| 94 | andrewkbank.First | 600 | 180 | 44 | 4-40 | 100% (g_iter0 2-0*) |
| 95 | Yooncw0223.lec3player | 398 | 185 | 89 | 3-86 | 100% (g_iter0 5-0*) |
