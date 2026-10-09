# Ladder

4690 games (1183 ours, 3507 between field bots on the ladder replica), 4672 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_swarm1 | 1865 +- 63 | 19 of 95 | 174 | 78-96 | 75.1% | 20.6% (vs 18) |
| g_iter0 | 1817 +- 48 | 23 of 95 | 456 | 230-226 | 72.5% | 21.1% (vs 21) |
| c_line8a | 1815 +- 73 | 24 of 95 | 139 | 47-92 | 72.4% | 21.0% (vs 21) |
| c_line6 | 1775 +- 89 | 26 of 95 | 100 | 32-68 | 70.1% | 19.3% (vs 22) |
| c_line7m | 1763 +- 90 | 28 of 95 | 100 | 31-69 | 69.4% | 19.7% (vs 23) |
| c_line5 | 1726 +- 92 | 32 of 95 | 100 | 28-72 | 67.2% | 20.6% (vs 26) |
| c_line4 | 1686 +- 95 | 36 of 95 | 100 | 25-75 | 64.7% | 20.6% (vs 29) |
| examplefuncsplayer | 1270 +- 380 | 66 of 95 | 6 | 0-6 | 36.3% | 15.2% (vs 58) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2408 | 122 | 74 | 63-11 | 0% (g_iter0 0-5*) |
| 2 | IvanGeffner.fortytwo | 2391 | 98 | 99 | 82-17 | 0% (g_iter0 0-36) |
| 3 | carlguo866.submit26_final | 2382 | 134 | 67 | 57-10 | 0% (g_iter0 0-2*) |
| 4 | awesomelemonade.finalBot | 2359 | 107 | 147 | 132-15 | 0% (g_iter0 0-15*) |
| 5 | vrangr1.AFinalsBot | 2314 | 115 | 143 | 133-10 | 7% (g_iter0 1-14*) |
| 6 | pranayagra.finalbotfinaltwo | 2238 | 98 | 97 | 72-25 | 7% (g_iter0 1-13*) |
| 7 | AnOvercookedFork.quals | 2229 | 119 | 77 | 60-17 | 20% (g_iter0 1-4*) |
| 8 | battlecode-archive.sprintBot | 2216 | 144 | 70 | 61-9 | 0% (g_iter0 0-2*) |
| 9 | pranayagra.finalbotfinal | 2216 | 73 | 189 | 148-41 | 13% (g_iter0 6-39) |
| 10 | georgezhang02.FB_ZZZ | 2166 | 109 | 71 | 49-22 | 0% (g_iter0 0-2*) |
| 11 | jmerle.camel_case_v30_final | 2117 | 74 | 168 | 130-38 | 14% (g_iter0 3-18*) |
| 12 | ethanlabelle.dev | 2045 | 97 | 82 | 60-22 | 0% (g_iter0 0-2*) |
| 13 | georgezhang02.CB_tuning2 | 1979 | 69 | 150 | 107-43 | 7% (g_iter0 1-14*) |
| 14 | NotLLeon.v7 | 1954 | 71 | 140 | 101-39 | 17% (g_iter0 2-10*) |
| 15 | GabeG888.v8o1 | 1944 | 121 | 62 | 46-16 | 0% (g_iter0 0-2*) |
| 16 | CyrilSharma.finalBot | 1932 | 113 | 80 | 53-27 | 0% (g_iter0 0-2*) |
| 17 | britacatalin.FinalBot | 1917 | 70 | 137 | 94-43 | 42% (g_iter0 5-7*) |
| 18 | ethanlabelle.v19 | 1890 | 99 | 76 | 51-25 | 50% (g_iter0 1-1*) |
| 19 | **us:c_swarm1** | 1865 | 63 | 174 | 78-96 |  |
| 20 | GabeG888.v8 | 1860 | 92 | 77 | 46-31 | 50% (g_iter0 1-1*) |
| 21 | VarunVejalla.karel | 1836 | 92 | 92 | 55-37 | 50% (g_iter0 4-4*) |
| 22 | DannyZhang686.pqual2 | 1830 | 91 | 95 | 55-40 | 29% (g_iter0 4-10*) |
| 23 | **us:g_iter0** | 1817 | 48 | 456 | 230-226 |  |
| 24 | **us:c_line8a** | 1815 | 73 | 139 | 47-92 |  |
| 25 | programjames.fourthbot | 1792 | 99 | 80 | 47-33 | 100% (g_iter0 2-0*) |
| 26 | **us:c_line6** | 1775 | 89 | 100 | 32-68 |  |
| 27 | louishu17.wouisv8 | 1764 | 91 | 102 | 58-44 | 50% (g_iter0 5-5*) |
| 28 | **us:c_line7m** | 1763 | 90 | 100 | 31-69 |  |
| 29 | NicholasKelly15.gopher10 | 1752 | 107 | 68 | 44-24 | 100% (g_iter0 2-0*) |
| 30 | battlecode-archive.Sprint1 | 1735 | 64 | 143 | 74-69 | 58% (g_iter0 7-5*) |
| 31 | louishu17.louisv10 | 1726 | 100 | 80 | 49-31 | 100% (g_iter0 2-0*) |
| 32 | **us:c_line5** | 1726 | 92 | 100 | 28-72 |  |
| 33 | VarunVejalla.ali8 | 1722 | 110 | 71 | 45-26 | 50% (g_iter0 1-1*) |
| 34 | SampleProvider.SPAARK | 1707 | 101 | 73 | 45-28 | 100% (g_iter0 2-0*) |
| 35 | reeceyang.v5anaconda | 1701 | 66 | 144 | 73-71 | 58% (g_iter0 7-5*) |
| 36 | **us:c_line4** | 1686 | 95 | 100 | 25-75 |  |
| 37 | ipince.bobby | 1681 | 119 | 65 | 42-23 | 100% (g_iter0 2-0*) |
| 38 | legobridge.tacoplayer | 1659 | 98 | 94 | 52-42 | 85% (g_iter0 11-2*) |
| 39 | polyllc.poly | 1654 | 113 | 77 | 43-34 | 100% (g_iter0 2-0*) |
| 40 | toyat522.bot5a | 1611 | 95 | 83 | 42-41 | 80% (g_iter0 4-1*) |
| 41 | DukeBas._main | 1601 | 98 | 80 | 48-32 | 100% (g_iter0 2-0*) |
| 42 | SteamBlizzard.newVnewME | 1593 | 91 | 89 | 42-47 | 80% (g_iter0 4-1*) |
| 43 | beaverbois.USQualifiers | 1581 | 101 | 71 | 40-31 | 50% (g_iter0 1-1*) |
| 44 | elgoldie.head_v5 | 1577 | 89 | 83 | 39-44 | 100% (g_iter0 2-0*) |
| 45 | ColtG5.rexv9 | 1569 | 100 | 79 | 37-42 | 100% (g_iter0 2-0*) |
| 46 | TheK098.qp1_7_sprint_1 | 1547 | 113 | 65 | 38-27 | 100% (g_iter0 2-0*) |
| 47 | kevinli405.maggi3_2 | 1538 | 101 | 86 | 46-40 | 100% (g_iter0 2-0*) |
| 48 | BrysonJGalapon.friday | 1523 | 89 | 86 | 45-41 | 100% (g_iter0 2-0*) |
| 49 | nail-e.Barry | 1497 | 93 | 77 | 42-35 | 100% (g_iter0 2-0*) |
| 50 | Nawlej.PoonPoon | 1428 | 101 | 77 | 36-41 | 100% (g_iter0 2-0*) |
| 51 | prisms-cs-club.prisms10 | 1421 | 100 | 80 | 36-44 | 100% (g_iter0 2-0*) |
| 52 | yaonam.PoonPoonv4 | 1411 | 73 | 168 | 56-112 | 87% (g_iter0 13-2*) |
| 53 | ipince.bobby_v2 | 1403 | 88 | 92 | 46-46 | 100% (g_iter0 5-0*) |
| 54 | aj-chau.attempt1 | 1400 | 113 | 68 | 36-32 | 100% (g_iter0 5-0*) |
| 55 | kevinli405.maggi3 | 1398 | 93 | 92 | 45-47 | 100% (g_iter0 5-0*) |
| 56 | mama4294.currentPlayer | 1364 | 106 | 74 | 36-38 | 100% (g_iter0 2-0*) |
| 57 | PSUtblock.sprint_four_player | 1346 | 117 | 74 | 39-35 | 100% (g_iter0 2-0*) |
| 58 | andrewgopher.gopherbot | 1339 | 84 | 101 | 45-56 | 100% (g_iter0 2-0*) |
| 59 | BrysonJGalapon.aloha | 1337 | 98 | 71 | 35-36 | 100% (g_iter0 2-0*) |
| 60 | bewuwy.deathbot4 | 1328 | 75 | 119 | 48-71 | 100% (g_iter0 2-0*) |
| 61 | JackLee9355.jackPlayer | 1306 | 85 | 101 | 43-58 | 100% (g_iter0 2-0*) |
| 62 | JfeMak.realplayer2 | 1301 | 92 | 76 | 35-41 | 100% (g_iter0 2-0*) |
| 63 | SDainard-PDX.Team_Player | 1297 | 106 | 74 | 35-39 | 100% (g_iter0 2-0*) |
| 64 | SampleProvider.SPAARK_1_12_2023 | 1286 | 96 | 77 | 36-41 | 100% (g_iter0 2-0*) |
| 65 | jyorkio.elicompbot | 1286 | 99 | 68 | 34-34 | 100% (g_iter0 2-0*) |
| 66 | **us:examplefuncsplayer** | 1270 | 380 | 6 | 0-6 |  |
| 67 | NolanChai.nolan_1 | 1251 | 91 | 86 | 34-52 | 100% (g_iter0 2-0*) |
| 68 | Nawlej.PoonPoonv3 | 1249 | 81 | 104 | 39-65 | 100% (g_iter0 5-0*) |
| 69 | andrewgopher.gopherbot1 | 1244 | 87 | 101 | 41-60 | 100% (g_iter0 2-0*) |
| 70 | Juanbri02.matfisplayer1 | 1233 | 87 | 95 | 41-54 | 100% (g_iter0 5-0*) |
| 71 | SteamBlizzard.Block | 1194 | 82 | 114 | 39-75 | 100% (g_iter0 5-0*) |
| 72 | vontell.regressiongames | 1177 | 83 | 89 | 36-53 | 100% (g_iter0 5-0*) |
| 73 | legobridge.kushalplayer | 1177 | 103 | 83 | 34-49 | 100% (g_iter0 2-0*) |
| 74 | ax-95174.MPAction | 1173 | 100 | 74 | 27-47 | 100% (g_iter0 2-0*) |
| 75 | michael-tyl.hqrewrite | 1171 | 85 | 95 | 42-53 | 100% (g_iter0 2-0*) |
| 76 | anicolao.submission | 1165 | 80 | 105 | 39-66 | 100% (g_iter0 2-0*) |
| 77 | Chahat08.toph | 1150 | 85 | 92 | 36-56 | 100% (g_iter0 2-0*) |
| 78 | Patela171.Battlecode2023_Robot | 1089 | 90 | 95 | 32-63 | 100% (g_iter0 2-0*) |
| 79 | mama4294.learningBot | 1048 | 98 | 95 | 29-66 | 100% (g_iter0 2-0*) |
| 80 | nail-e.Dante | 1048 | 90 | 89 | 39-50 | 100% (g_iter0 2-0*) |
| 81 | team-remember-to-hydrate.sprint_1 | 1008 | 94 | 92 | 30-62 | 100% (g_iter0 2-0*) |
| 82 | addiesteward.elicompbot | 960 | 85 | 104 | 34-70 | 100% (g_iter0 5-0*) |
| 83 | Vinceyou1.Player1 | 949 | 98 | 83 | 30-53 | 100% (g_iter0 2-0*) |
| 84 | michael-tyl.cc_v0_5_0_6 | 939 | 82 | 119 | 41-78 | 100% (g_iter0 2-0*) |
| 85 | toyat522.bot5 | 889 | 108 | 86 | 23-63 | 100% (g_iter0 2-0*) |
| 86 | Swordman51.AdeptusAstartes2 | 875 | 95 | 85 | 27-58 | 100% (g_iter0 2-0*) |
| 87 | monmouth-college-cs.elicompbot | 853 | 94 | 98 | 30-68 | 100% (g_iter0 2-0*) |
| 88 | Chahat08.lazarus | 846 | 107 | 83 | 26-57 | 100% (g_iter0 2-0*) |
| 89 | ShatterXD.SRNNbot | 769 | 90 | 98 | 34-64 | 100% (g_iter0 2-0*) |
| 90 | anicolao.jumbled | 694 | 86 | 118 | 38-80 | 100% (g_iter0 5-0*) |
| 91 | CodeClash-ai.mysubmission | 638 | 98 | 100 | 27-73 | 100% (g_iter0 2-0*) |
| 92 | NotLLeon.player | 631 | 107 | 80 | 20-60 | 100% (g_iter0 2-0*) |
| 93 | addiesteward.NDeClaw | 605 | 99 | 107 | 30-77 | 100% (g_iter0 5-0*) |
| 94 | andrewkbank.First | 454 | 131 | 71 | 9-62 | 100% (g_iter0 2-0*) |
| 95 | Yooncw0223.lec3player | 334 | 131 | 127 | 7-120 | 100% (g_iter0 5-0*) |
