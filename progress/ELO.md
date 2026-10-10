# Ladder

9117 games (2028 ours, 7089 between field bots on the ladder replica), 9034 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_def3 | 2050 +- 83 | 12 of 100 | 100 | 60-40 | 84.9% | 28.1% (vs 11) |
| c_anc3 | 2002 +- 61 | 13 of 100 | 163 | 88-75 | 82.9% | 23.1% (vs 11) |
| c_nav5 | 1942 +- 71 | 17 of 100 | 126 | 61-65 | 80.1% | 23.4% (vs 14) |
| c_nav6 | 1929 +- 71 | 19 of 100 | 129 | 58-71 | 79.5% | 24.1% (vs 15) |
| c_nav4 | 1909 +- 52 | 20 of 100 | 221 | 108-113 | 78.6% | 22.3% (vs 15) |
| c_swarm1 | 1836 +- 48 | 24 of 100 | 271 | 128-143 | 74.8% | 21.4% (vs 18) |
| g_iter0 | 1792 +- 48 | 31 of 100 | 456 | 230-226 | 72.4% | 25.4% (vs 24) |
| c_line8a | 1791 +- 71 | 32 of 100 | 139 | 47-92 | 72.3% | 25.3% (vs 24) |
| c_line6 | 1758 +- 88 | 33 of 100 | 100 | 32-68 | 70.5% | 22.4% (vs 24) |
| c_line7m | 1746 +- 88 | 36 of 100 | 100 | 31-69 | 69.8% | 23.5% (vs 26) |
| c_line5 | 1711 +- 90 | 40 of 100 | 100 | 28-72 | 67.7% | 23.3% (vs 29) |
| c_line4 | 1673 +- 93 | 41 of 100 | 100 | 25-75 | 65.4% | 20.1% (vs 29) |
| examplefuncsplayer | 1239 +- 380 | 67 of 100 | 6 | 0-6 | 37.9% | 12.5% (vs 54) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_anc3), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2366 | 77 | 134 | 106-28 | 0% (g_iter0 0-36) |
| 2 | awesomelemonade.finalBot | 2312 | 68 | 235 | 197-38 | 20% (c_anc3 2-8*) |
| 3 | maxwelljones14.MPWorking | 2310 | 80 | 113 | 82-31 | 0% (g_iter0 0-5*) |
| 4 | vrangr1.AFinalsBot | 2285 | 67 | 241 | 203-38 | 10% (c_anc3 1-9*) |
| 5 | carlguo866.submit26_final | 2260 | 76 | 127 | 89-38 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2230 | 80 | 122 | 87-35 | 0% (c_anc3 0-3*) |
| 7 | pranayagra.finalbotfinaltwo | 2175 | 70 | 145 | 97-48 | 33% (c_anc3 2-4*) |
| 8 | pranayagra.finalbotfinal | 2168 | 52 | 292 | 214-78 | 40% (c_anc3 4-6*) |
| 9 | georgezhang02.FB_ZZZ | 2142 | 68 | 143 | 95-48 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2108 | 76 | 136 | 93-43 | 33% (c_anc3 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2090 | 51 | 275 | 197-78 | 38% (c_anc3 5-8*) |
| 12 | **us:c_def3** | 2050 | 83 | 100 | 60-40 |  |
| 13 | **us:c_anc3** | 2002 | 61 | 163 | 88-75 |  |
| 14 | CyrilSharma.finalBot | 2000 | 62 | 173 | 103-70 | 42% (c_anc3 5-7*) |
| 15 | ethanlabelle.dev | 1983 | 63 | 149 | 93-56 | 33% (c_anc3 3-6*) |
| 16 | NotLLeon.v7 | 1961 | 47 | 270 | 167-103 | 69% (c_anc3 11-5*) |
| 17 | **us:c_nav5** | 1942 | 71 | 126 | 61-65 |  |
| 18 | georgezhang02.CB_tuning2 | 1930 | 47 | 259 | 156-103 | 46% (c_anc3 6-7*) |
| 19 | **us:c_nav6** | 1929 | 71 | 129 | 58-71 |  |
| 20 | **us:c_nav4** | 1909 | 52 | 221 | 108-113 |  |
| 21 | britacatalin.FinalBot | 1866 | 46 | 267 | 151-116 | 85% (c_anc3 11-2*) |
| 22 | ethanlabelle.v19 | 1856 | 68 | 132 | 78-54 | 100% (c_nav5 3-0*) |
| 23 | GabeG888.v8 | 1854 | 60 | 154 | 90-64 | 67% (c_nav4 4-2*) |
| 24 | **us:c_swarm1** | 1836 | 48 | 271 | 128-143 |  |
| 25 | GabeG888.v8o1 | 1823 | 66 | 139 | 84-55 | 100% (c_nav5 3-0*) |
| 26 | DannyZhang686.pqual2 | 1814 | 60 | 173 | 96-77 | 83% (c_anc3 5-1*) |
| 27 | VarunVejalla.ali8 | 1806 | 65 | 146 | 88-58 | 67% (c_swarm1 6-3*) |
| 28 | VarunVejalla.karel | 1802 | 60 | 170 | 93-77 | 67% (c_nav4 6-3*) |
| 29 | programjames.fourthbot | 1800 | 65 | 149 | 82-67 | 17% (c_nav4 1-5*) |
| 30 | NicholasKelly15.gopher10 | 1793 | 73 | 122 | 70-52 | 100% (c_anc3 3-0*) |
| 31 | **us:g_iter0** | 1792 | 48 | 456 | 230-226 |  |
| 32 | **us:c_line8a** | 1791 | 71 | 139 | 47-92 |  |
| 33 | **us:c_line6** | 1758 | 88 | 100 | 32-68 |  |
| 34 | louishu17.louisv10 | 1755 | 65 | 151 | 86-65 | 100% (c_nav4 6-0*) |
| 35 | louishu17.wouisv8 | 1751 | 64 | 167 | 92-75 | 33% (c_nav4 2-4*) |
| 36 | **us:c_line7m** | 1746 | 88 | 100 | 31-69 |  |
| 37 | SampleProvider.SPAARK | 1730 | 66 | 142 | 82-60 | 33% (c_anc3 1-2*) |
| 38 | reeceyang.v5anaconda | 1727 | 47 | 276 | 124-152 | 90% (c_anc3 9-1*) |
| 39 | battlecode-archive.Sprint1 | 1716 | 47 | 262 | 118-144 | 100% (c_anc3 10-0*) |
| 40 | **us:c_line5** | 1711 | 90 | 100 | 28-72 |  |
| 41 | **us:c_line4** | 1673 | 93 | 100 | 25-75 |  |
| 42 | ipince.bobby | 1623 | 69 | 137 | 74-63 | 67% (c_swarm1 2-1*) |
| 43 | legobridge.tacoplayer | 1617 | 63 | 173 | 94-79 | 85% (g_iter0 11-2*) |
| 44 | polyllc.poly | 1612 | 73 | 139 | 73-66 | 100% (g_iter0 2-0*) |
| 45 | SteamBlizzard.newVnewME | 1597 | 60 | 171 | 86-85 | 80% (g_iter0 4-1*) |
| 46 | TheK098.qp1_7_sprint_1 | 1588 | 62 | 167 | 90-77 | 100% (c_swarm1 6-0*) |
| 47 | elgoldie.head_v5 | 1574 | 62 | 149 | 77-72 | 100% (g_iter0 2-0*) |
| 48 | toyat522.bot5a | 1574 | 63 | 158 | 83-75 | 80% (g_iter0 4-1*) |
| 49 | DukeBas._main | 1547 | 63 | 162 | 87-75 | 100% (g_iter0 2-0*) |
| 50 | ColtG5.rexv9 | 1534 | 59 | 173 | 85-88 | 100% (g_iter0 2-0*) |
| 51 | beaverbois.USQualifiers | 1487 | 61 | 161 | 86-75 | 50% (g_iter0 1-1*) |
| 52 | kevinli405.maggi3_2 | 1480 | 62 | 172 | 88-84 | 100% (g_iter0 2-0*) |
| 53 | BrysonJGalapon.friday | 1470 | 59 | 165 | 84-81 | 100% (g_iter0 2-0*) |
| 54 | nail-e.Barry | 1453 | 63 | 151 | 79-72 | 100% (g_iter0 2-0*) |
| 55 | Nawlej.PoonPoon | 1448 | 67 | 149 | 72-77 | 100% (g_iter0 2-0*) |
| 56 | kevinli405.maggi3 | 1428 | 66 | 161 | 84-77 | 100% (g_iter0 5-0*) |
| 57 | yaonam.PoonPoonv4 | 1422 | 51 | 307 | 109-198 | 90% (c_anc3 9-1*) |
| 58 | aj-chau.attempt1 | 1419 | 64 | 158 | 82-76 | 100% (g_iter0 5-0*) |
| 59 | prisms-cs-club.prisms10 | 1401 | 63 | 161 | 78-83 | 100% (g_iter0 2-0*) |
| 60 | mama4294.currentPlayer | 1363 | 59 | 176 | 89-87 | 100% (g_iter0 2-0*) |
| 61 | ipince.bobby_v2 | 1343 | 65 | 155 | 74-81 | 67% (c_swarm1 2-1*) |
| 62 | BrysonJGalapon.aloha | 1302 | 57 | 179 | 89-90 | 100% (c_swarm1 3-0*) |
| 63 | andrewgopher.gopherbot | 1300 | 56 | 197 | 93-104 | 100% (g_iter0 2-0*) |
| 64 | JfeMak.realplayer2 | 1298 | 63 | 151 | 77-74 | 100% (g_iter0 2-0*) |
| 65 | bewuwy.deathbot4 | 1280 | 53 | 216 | 98-118 | 100% (g_iter0 2-0*) |
| 66 | SampleProvider.SPAARK_1_12_2023 | 1243 | 54 | 205 | 96-109 | 100% (c_swarm1 3-0*) |
| 67 | **us:examplefuncsplayer** | 1239 | 380 | 6 | 0-6 |  |
| 68 | PSUtblock.sprint_four_player | 1238 | 67 | 157 | 77-80 | 100% (g_iter0 2-0*) |
| 69 | SDainard-PDX.Team_Player | 1234 | 63 | 158 | 77-81 | 100% (g_iter0 2-0*) |
| 70 | NolanChai.nolan_1 | 1204 | 60 | 172 | 81-91 | 100% (g_iter0 2-0*) |
| 71 | Juanbri02.matfisplayer1 | 1203 | 56 | 192 | 88-104 | 100% (g_iter0 5-0*) |
| 72 | Nawlej.PoonPoonv3 | 1198 | 55 | 199 | 91-108 | 100% (g_iter0 5-0*) |
| 73 | jyorkio.elicompbot | 1173 | 57 | 177 | 84-93 | 100% (g_iter0 2-0*) |
| 74 | andrewgopher.gopherbot1 | 1172 | 60 | 181 | 81-100 | 100% (g_iter0 2-0*) |
| 75 | vontell.regressiongames | 1126 | 51 | 218 | 101-117 | 100% (g_iter0 5-0*) |
| 76 | JackLee9355.jackPlayer | 1096 | 58 | 197 | 83-114 | 100% (g_iter0 2-0*) |
| 77 | ax-95174.MPAction | 1091 | 59 | 172 | 76-96 | 100% (c_swarm1 3-0*) |
| 78 | SteamBlizzard.Block | 1090 | 53 | 222 | 94-128 | 100% (g_iter0 5-0*) |
| 79 | legobridge.kushalplayer | 1072 | 65 | 157 | 68-89 | 100% (g_iter0 2-0*) |
| 80 | Patela171.Battlecode2023_Robot | 1063 | 56 | 199 | 90-109 | 100% (g_iter0 2-0*) |
| 81 | michael-tyl.hqrewrite | 1033 | 56 | 191 | 87-104 | 100% (g_iter0 2-0*) |
| 82 | Chahat08.toph | 1015 | 58 | 181 | 79-102 | 100% (g_iter0 2-0*) |
| 83 | nail-e.Dante | 1013 | 56 | 197 | 93-104 | 100% (g_iter0 2-0*) |
| 84 | anicolao.submission | 983 | 53 | 231 | 101-130 | 100% (g_iter0 2-0*) |
| 85 | mama4294.learningBot | 978 | 61 | 182 | 74-108 | 100% (g_iter0 2-0*) |
| 86 | team-remember-to-hydrate.sprint_1 | 921 | 55 | 212 | 87-125 | 100% (g_iter0 2-0*) |
| 87 | Vinceyou1.Player1 | 835 | 61 | 177 | 70-107 | 100% (g_iter0 2-0*) |
| 88 | addiesteward.elicompbot | 823 | 54 | 216 | 90-126 | 100% (g_iter0 5-0*) |
| 89 | michael-tyl.cc_v0_5_0_6 | 814 | 50 | 249 | 105-144 | 100% (g_iter0 2-0*) |
| 90 | monmouth-college-cs.elicompbot | 786 | 56 | 214 | 88-126 | 100% (g_iter0 2-0*) |
| 91 | Swordman51.AdeptusAstartes2 | 781 | 52 | 221 | 92-129 | 100% (g_iter0 2-0*) |
| 92 | toyat522.bot5 | 770 | 59 | 200 | 81-119 | 100% (g_iter0 2-0*) |
| 93 | Chahat08.lazarus | 769 | 56 | 205 | 85-120 | 100% (g_iter0 2-0*) |
| 94 | anicolao.jumbled | 668 | 52 | 250 | 105-145 | 100% (g_iter0 5-0*) |
| 95 | ShatterXD.SRNNbot | 661 | 60 | 189 | 77-112 | 100% (g_iter0 2-0*) |
| 96 | NotLLeon.player | 489 | 62 | 212 | 86-126 | 100% (g_iter0 2-0*) |
| 97 | CodeClash-ai.mysubmission | 476 | 62 | 218 | 88-130 | 100% (g_iter0 2-0*) |
| 98 | addiesteward.NDeClaw | 444 | 68 | 202 | 78-124 | 100% (g_iter0 5-0*) |
| 99 | Yooncw0223.lec3player | 152 | 87 | 194 | 21-173 | 100% (g_iter0 5-0*) |
| 100 | andrewkbank.First | 138 | 87 | 158 | 20-138 | 100% (g_iter0 2-0*) |
