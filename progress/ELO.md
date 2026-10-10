# Ladder

10542 games (2280 ours, 8262 between field bots on the ladder replica), 10421 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_aura2 | 2073 +- 108 | 12 of 102 | 50 | 28-22 | 86.3% | 32.1% (vs 11) |
| c_def3 | 2022 +- 55 | 13 of 102 | 199 | 120-79 | 84.2% | 26.3% (vs 11) |
| c_flee3 | 1997 +- 82 | 14 of 102 | 100 | 56-44 | 83.1% | 23.7% (vs 11) |
| c_anc3 | 1992 +- 61 | 16 of 102 | 163 | 88-75 | 82.9% | 25.4% (vs 12) |
| c_nav5 | 1932 +- 71 | 19 of 102 | 126 | 61-65 | 80.2% | 23.4% (vs 14) |
| c_nav6 | 1919 +- 71 | 21 of 102 | 129 | 58-71 | 79.5% | 23.9% (vs 15) |
| c_nav4 | 1900 +- 52 | 22 of 102 | 221 | 108-113 | 78.6% | 22.2% (vs 15) |
| c_swarm1 | 1827 +- 48 | 26 of 102 | 271 | 128-143 | 74.9% | 21.3% (vs 18) |
| c_line8a | 1780 +- 71 | 33 of 102 | 139 | 47-92 | 72.4% | 25.1% (vs 24) |
| g_iter0 | 1779 +- 48 | 34 of 102 | 456 | 230-226 | 72.4% | 25.1% (vs 24) |
| c_line6 | 1746 +- 88 | 35 of 102 | 100 | 32-68 | 70.5% | 22.2% (vs 24) |
| c_line7m | 1734 +- 88 | 38 of 102 | 100 | 31-69 | 69.8% | 23.3% (vs 26) |
| c_line5 | 1698 +- 91 | 41 of 102 | 100 | 28-72 | 67.7% | 22.2% (vs 28) |
| c_line4 | 1660 +- 93 | 43 of 102 | 100 | 25-75 | 65.5% | 20.0% (vs 29) |
| examplefuncsplayer | 1228 +- 380 | 69 of 102 | 6 | 0-6 | 38.4% | 12.6% (vs 54) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_def3), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2337 | 71 | 146 | 111-35 | 0% (g_iter0 0-36) |
| 2 | awesomelemonade.finalBot | 2319 | 64 | 257 | 216-41 | 20% (c_def3 2-8*) |
| 3 | maxwelljones14.MPWorking | 2300 | 73 | 130 | 93-37 | 0% (g_iter0 0-5*) |
| 4 | vrangr1.AFinalsBot | 2248 | 58 | 275 | 222-53 | 40% (c_def3 4-6*) |
| 5 | carlguo866.submit26_final | 2245 | 70 | 139 | 94-45 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2193 | 72 | 137 | 93-44 | 0% (c_anc3 0-3*) |
| 7 | pranayagra.finalbotfinaltwo | 2162 | 66 | 159 | 105-54 | 33% (c_anc3 2-4*) |
| 8 | pranayagra.finalbotfinal | 2157 | 47 | 333 | 236-97 | 31% (c_def3 4-9*) |
| 9 | georgezhang02.FB_ZZZ | 2146 | 63 | 161 | 106-55 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2118 | 69 | 153 | 105-48 | 0% (c_def3 0-6*) |
| 11 | jmerle.camel_case_v30_final | 2088 | 47 | 311 | 219-92 | 31% (c_def3 5-11*) |
| 12 | **us:c_aura2** | 2073 | 108 | 50 | 28-22 |  |
| 13 | **us:c_def3** | 2022 | 55 | 199 | 120-79 |  |
| 14 | **us:c_flee3** | 1997 | 82 | 100 | 56-44 |  |
| 15 | CyrilSharma.finalBot | 1995 | 58 | 194 | 113-81 | 33% (c_def3 3-6*) |
| 16 | **us:c_anc3** | 1992 | 61 | 163 | 88-75 |  |
| 17 | ethanlabelle.dev | 1988 | 58 | 176 | 110-66 | 58% (c_def3 7-5*) |
| 18 | NotLLeon.v7 | 1941 | 42 | 327 | 191-136 | 67% (c_def3 18-9*) |
| 19 | **us:c_nav5** | 1932 | 71 | 126 | 61-65 |  |
| 20 | georgezhang02.CB_tuning2 | 1921 | 44 | 292 | 174-118 | 60% (c_def3 6-4*) |
| 21 | **us:c_nav6** | 1919 | 71 | 129 | 58-71 |  |
| 22 | **us:c_nav4** | 1900 | 52 | 221 | 108-113 |  |
| 23 | ethanlabelle.v19 | 1865 | 62 | 153 | 92-61 | 100% (c_nav5 3-0*) |
| 24 | britacatalin.FinalBot | 1863 | 43 | 312 | 170-142 | 63% (c_def3 19-11) |
| 25 | GabeG888.v8 | 1830 | 54 | 190 | 100-90 | 89% (c_def3 16-2*) |
| 26 | **us:c_swarm1** | 1827 | 48 | 271 | 128-143 |  |
| 27 | programjames.fourthbot | 1806 | 60 | 172 | 96-76 | 17% (c_nav4 1-5*) |
| 28 | GabeG888.v8o1 | 1802 | 60 | 163 | 94-69 | 100% (c_nav5 3-0*) |
| 29 | VarunVejalla.ali8 | 1796 | 61 | 169 | 95-74 | 100% (c_def3 8-0*) |
| 30 | VarunVejalla.karel | 1794 | 57 | 188 | 104-84 | 67% (c_nav4 6-3*) |
| 31 | DannyZhang686.pqual2 | 1786 | 56 | 193 | 104-89 | 83% (c_anc3 5-1*) |
| 32 | NicholasKelly15.gopher10 | 1780 | 64 | 151 | 87-64 | 100% (c_anc3 3-0*) |
| 33 | **us:c_line8a** | 1780 | 71 | 139 | 47-92 |  |
| 34 | **us:g_iter0** | 1779 | 48 | 456 | 230-226 |  |
| 35 | **us:c_line6** | 1746 | 88 | 100 | 32-68 |  |
| 36 | louishu17.louisv10 | 1740 | 61 | 166 | 94-72 | 100% (c_nav4 6-0*) |
| 37 | louishu17.wouisv8 | 1739 | 59 | 193 | 108-85 | 33% (c_nav4 2-4*) |
| 38 | **us:c_line7m** | 1734 | 88 | 100 | 31-69 |  |
| 39 | SampleProvider.SPAARK | 1720 | 59 | 170 | 95-75 | 33% (c_anc3 1-2*) |
| 40 | reeceyang.v5anaconda | 1717 | 44 | 313 | 141-172 | 90% (c_def3 9-1*) |
| 41 | **us:c_line5** | 1698 | 91 | 100 | 28-72 |  |
| 42 | battlecode-archive.Sprint1 | 1693 | 45 | 299 | 126-173 | 100% (c_def3 10-0*) |
| 43 | **us:c_line4** | 1660 | 93 | 100 | 25-75 |  |
| 44 | ipince.bobby | 1608 | 64 | 153 | 83-70 | 67% (c_swarm1 2-1*) |
| 45 | SteamBlizzard.newVnewME | 1608 | 55 | 201 | 103-98 | 80% (g_iter0 4-1*) |
| 46 | legobridge.tacoplayer | 1602 | 59 | 191 | 103-88 | 85% (g_iter0 11-2*) |
| 47 | polyllc.poly | 1596 | 68 | 154 | 79-75 | 100% (g_iter0 2-0*) |
| 48 | TheK098.qp1_7_sprint_1 | 1583 | 57 | 190 | 105-85 | 100% (c_swarm1 6-0*) |
| 49 | toyat522.bot5a | 1555 | 57 | 184 | 93-91 | 80% (g_iter0 4-1*) |
| 50 | elgoldie.head_v5 | 1532 | 56 | 182 | 90-92 | 100% (g_iter0 2-0*) |
| 51 | DukeBas._main | 1524 | 58 | 185 | 99-86 | 100% (g_iter0 2-0*) |
| 52 | ColtG5.rexv9 | 1518 | 55 | 200 | 101-99 | 100% (g_iter0 2-0*) |
| 53 | beaverbois.USQualifiers | 1477 | 58 | 181 | 91-90 | 50% (g_iter0 1-1*) |
| 54 | kevinli405.maggi3_2 | 1466 | 56 | 199 | 101-98 | 100% (g_iter0 2-0*) |
| 55 | Nawlej.PoonPoon | 1455 | 60 | 178 | 89-89 | 100% (g_iter0 2-0*) |
| 56 | BrysonJGalapon.friday | 1454 | 55 | 182 | 93-89 | 100% (g_iter0 2-0*) |
| 57 | nail-e.Barry | 1434 | 55 | 188 | 98-90 | 100% (g_iter0 2-0*) |
| 58 | kevinli405.maggi3 | 1411 | 57 | 197 | 101-96 | 100% (g_iter0 5-0*) |
| 59 | aj-chau.attempt1 | 1408 | 57 | 187 | 97-90 | 100% (g_iter0 5-0*) |
| 60 | yaonam.PoonPoonv4 | 1408 | 49 | 337 | 117-220 | 90% (c_def3 9-1*) |
| 61 | prisms-cs-club.prisms10 | 1380 | 56 | 197 | 95-102 | 100% (g_iter0 2-0*) |
| 62 | mama4294.currentPlayer | 1354 | 55 | 199 | 100-99 | 100% (g_iter0 2-0*) |
| 63 | ipince.bobby_v2 | 1350 | 57 | 194 | 96-98 | 67% (c_swarm1 2-1*) |
| 64 | JfeMak.realplayer2 | 1280 | 58 | 177 | 88-89 | 100% (g_iter0 2-0*) |
| 65 | andrewgopher.gopherbot | 1279 | 51 | 227 | 108-119 | 100% (g_iter0 2-0*) |
| 66 | BrysonJGalapon.aloha | 1275 | 51 | 216 | 105-111 | 100% (c_swarm1 3-0*) |
| 67 | bewuwy.deathbot4 | 1266 | 49 | 250 | 116-134 | 100% (g_iter0 2-0*) |
| 68 | PSUtblock.sprint_four_player | 1239 | 58 | 193 | 99-94 | 100% (g_iter0 2-0*) |
| 69 | **us:examplefuncsplayer** | 1228 | 380 | 6 | 0-6 |  |
| 70 | SampleProvider.SPAARK_1_12_2023 | 1220 | 50 | 235 | 111-124 | 100% (c_swarm1 3-0*) |
| 71 | Juanbri02.matfisplayer1 | 1205 | 52 | 219 | 107-112 | 100% (g_iter0 5-0*) |
| 72 | SDainard-PDX.Team_Player | 1205 | 56 | 191 | 92-99 | 100% (g_iter0 2-0*) |
| 73 | Nawlej.PoonPoonv3 | 1180 | 50 | 229 | 106-123 | 100% (g_iter0 5-0*) |
| 74 | NolanChai.nolan_1 | 1174 | 52 | 217 | 99-118 | 100% (g_iter0 2-0*) |
| 75 | jyorkio.elicompbot | 1171 | 50 | 219 | 107-112 | 100% (g_iter0 2-0*) |
| 76 | andrewgopher.gopherbot1 | 1165 | 54 | 214 | 99-115 | 100% (g_iter0 2-0*) |
| 77 | vontell.regressiongames | 1102 | 48 | 245 | 115-130 | 100% (g_iter0 5-0*) |
| 78 | SteamBlizzard.Block | 1067 | 50 | 249 | 108-141 | 100% (g_iter0 5-0*) |
| 79 | ax-95174.MPAction | 1062 | 52 | 214 | 98-116 | 100% (c_swarm1 3-0*) |
| 80 | JackLee9355.jackPlayer | 1061 | 55 | 221 | 98-123 | 100% (g_iter0 2-0*) |
| 81 | legobridge.kushalplayer | 1058 | 61 | 175 | 76-99 | 100% (g_iter0 2-0*) |
| 82 | Patela171.Battlecode2023_Robot | 1045 | 53 | 216 | 98-118 | 100% (g_iter0 2-0*) |
| 83 | michael-tyl.hqrewrite | 1000 | 53 | 218 | 102-116 | 100% (g_iter0 2-0*) |
| 84 | nail-e.Dante | 983 | 52 | 224 | 103-121 | 100% (g_iter0 2-0*) |
| 85 | Chahat08.toph | 979 | 53 | 211 | 91-120 | 100% (g_iter0 2-0*) |
| 86 | mama4294.learningBot | 961 | 54 | 221 | 98-123 | 100% (g_iter0 2-0*) |
| 87 | anicolao.submission | 950 | 49 | 269 | 121-148 | 100% (g_iter0 2-0*) |
| 88 | team-remember-to-hydrate.sprint_1 | 892 | 52 | 239 | 98-141 | 100% (g_iter0 2-0*) |
| 89 | Vinceyou1.Player1 | 811 | 53 | 226 | 94-132 | 100% (g_iter0 2-0*) |
| 90 | addiesteward.elicompbot | 786 | 49 | 261 | 113-148 | 100% (g_iter0 5-0*) |
| 91 | michael-tyl.cc_v0_5_0_6 | 777 | 46 | 294 | 124-170 | 100% (g_iter0 2-0*) |
| 92 | Swordman51.AdeptusAstartes2 | 751 | 49 | 251 | 108-143 | 100% (g_iter0 2-0*) |
| 93 | Chahat08.lazarus | 744 | 52 | 237 | 103-134 | 100% (g_iter0 2-0*) |
| 94 | monmouth-college-cs.elicompbot | 744 | 50 | 261 | 113-148 | 100% (g_iter0 2-0*) |
| 95 | toyat522.bot5 | 727 | 52 | 242 | 101-141 | 100% (g_iter0 2-0*) |
| 96 | anicolao.jumbled | 620 | 51 | 268 | 110-158 | 100% (g_iter0 5-0*) |
| 97 | ShatterXD.SRNNbot | 604 | 57 | 219 | 90-129 | 100% (g_iter0 2-0*) |
| 98 | NotLLeon.player | 420 | 60 | 234 | 96-138 | 100% (g_iter0 2-0*) |
| 99 | CodeClash-ai.mysubmission | 411 | 58 | 246 | 102-144 | 100% (g_iter0 2-0*) |
| 100 | addiesteward.NDeClaw | 382 | 61 | 240 | 98-142 | 100% (g_iter0 5-0*) |
| 101 | Yooncw0223.lec3player | 112 | 73 | 229 | 36-193 | 100% (g_iter0 5-0*) |
| 102 | andrewkbank.First | 25 | 82 | 184 | 22-162 | 100% (g_iter0 2-0*) |
