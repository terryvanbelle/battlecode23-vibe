# Ladder

11390 games (2414 ours, 8976 between field bots on the ladder replica), 11243 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_def3 | 2027 +- 55 | 12 of 102 | 199 | 120-79 | 84.2% | 26.4% (vs 11) |
| c_aura2 | 2006 +- 57 | 14 of 102 | 182 | 98-84 | 83.3% | 26.3% (vs 12) |
| c_flee3 | 2002 +- 82 | 15 of 102 | 100 | 56-44 | 83.2% | 25.9% (vs 12) |
| c_anc3 | 1998 +- 61 | 16 of 102 | 163 | 88-75 | 83.0% | 25.5% (vs 12) |
| c_nav5 | 1938 +- 71 | 19 of 102 | 126 | 61-65 | 80.3% | 23.4% (vs 14) |
| c_nav6 | 1924 +- 71 | 21 of 102 | 129 | 58-71 | 79.6% | 23.9% (vs 15) |
| c_nav4 | 1904 +- 52 | 22 of 102 | 221 | 108-113 | 78.7% | 22.1% (vs 15) |
| c_swarm1 | 1832 +- 48 | 26 of 102 | 271 | 128-143 | 75.0% | 21.2% (vs 18) |
| c_line8a | 1785 +- 71 | 32 of 102 | 139 | 47-92 | 72.5% | 24.0% (vs 23) |
| g_iter0 | 1783 +- 48 | 33 of 102 | 456 | 230-226 | 72.4% | 23.9% (vs 23) |
| c_line6 | 1751 +- 88 | 36 of 102 | 100 | 32-68 | 70.6% | 23.3% (vs 25) |
| c_line7m | 1739 +- 88 | 38 of 102 | 100 | 31-69 | 70.0% | 23.3% (vs 26) |
| c_line5 | 1703 +- 91 | 41 of 102 | 100 | 28-72 | 67.9% | 22.2% (vs 28) |
| c_line4 | 1665 +- 93 | 43 of 102 | 100 | 25-75 | 65.7% | 20.0% (vs 29) |
| examplefuncsplayer | 1224 +- 380 | 69 of 102 | 6 | 0-6 | 38.3% | 12.5% (vs 54) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_aura2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2336 | 69 | 152 | 114-38 | 0% (g_iter0 0-36) |
| 2 | awesomelemonade.finalBot | 2320 | 61 | 273 | 227-46 | 20% (c_aura2 2-8*) |
| 3 | maxwelljones14.MPWorking | 2300 | 71 | 135 | 95-40 | 0% (g_iter0 0-5*) |
| 4 | vrangr1.AFinalsBot | 2260 | 58 | 280 | 227-53 | 40% (c_aura2 4-6*) |
| 5 | carlguo866.submit26_final | 2256 | 69 | 145 | 99-46 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2201 | 70 | 146 | 99-47 | 17% (c_aura2 1-5*) |
| 7 | pranayagra.finalbotfinaltwo | 2163 | 63 | 171 | 113-58 | 33% (c_aura2 3-6*) |
| 8 | pranayagra.finalbotfinal | 2158 | 47 | 336 | 237-99 | 40% (c_aura2 4-6*) |
| 9 | georgezhang02.FB_ZZZ | 2150 | 62 | 167 | 109-58 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2117 | 67 | 159 | 107-52 | 33% (c_aura2 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2094 | 46 | 325 | 229-96 | 29% (c_aura2 6-15*) |
| 12 | **us:c_def3** | 2027 | 55 | 199 | 120-79 |  |
| 13 | CyrilSharma.finalBot | 2009 | 54 | 215 | 125-90 | 33% (c_aura2 2-4*) |
| 14 | **us:c_aura2** | 2006 | 57 | 182 | 98-84 |  |
| 15 | **us:c_flee3** | 2002 | 82 | 100 | 56-44 |  |
| 16 | **us:c_anc3** | 1998 | 61 | 163 | 88-75 |  |
| 17 | ethanlabelle.dev | 1991 | 54 | 197 | 120-77 | 50% (c_aura2 9-9*) |
| 18 | NotLLeon.v7 | 1945 | 42 | 330 | 193-137 | 60% (c_aura2 6-4*) |
| 19 | **us:c_nav5** | 1938 | 71 | 126 | 61-65 |  |
| 20 | georgezhang02.CB_tuning2 | 1931 | 42 | 316 | 187-129 | 56% (c_aura2 9-7*) |
| 21 | **us:c_nav6** | 1924 | 71 | 129 | 58-71 |  |
| 22 | **us:c_nav4** | 1904 | 52 | 221 | 108-113 |  |
| 23 | ethanlabelle.v19 | 1874 | 56 | 186 | 105-81 | 58% (c_aura2 7-5*) |
| 24 | britacatalin.FinalBot | 1864 | 42 | 327 | 173-154 | 80% (c_aura2 12-3*) |
| 25 | GabeG888.v8 | 1843 | 53 | 198 | 107-91 | 89% (c_def3 16-2*) |
| 26 | **us:c_swarm1** | 1832 | 48 | 271 | 128-143 |  |
| 27 | programjames.fourthbot | 1808 | 58 | 181 | 99-82 | 100% (c_aura2 3-0*) |
| 28 | GabeG888.v8o1 | 1805 | 57 | 180 | 104-76 | 100% (c_nav5 3-0*) |
| 29 | VarunVejalla.ali8 | 1799 | 59 | 178 | 100-78 | 100% (c_def3 8-0*) |
| 30 | DannyZhang686.pqual2 | 1799 | 54 | 205 | 113-92 | 83% (c_anc3 5-1*) |
| 31 | VarunVejalla.karel | 1791 | 56 | 191 | 104-87 | 67% (c_nav4 6-3*) |
| 32 | **us:c_line8a** | 1785 | 71 | 139 | 47-92 |  |
| 33 | **us:g_iter0** | 1783 | 48 | 456 | 230-226 |  |
| 34 | NicholasKelly15.gopher10 | 1773 | 62 | 157 | 88-69 | 100% (c_anc3 3-0*) |
| 35 | louishu17.wouisv8 | 1754 | 58 | 201 | 113-88 | 67% (c_aura2 2-1*) |
| 36 | **us:c_line6** | 1751 | 88 | 100 | 32-68 |  |
| 37 | louishu17.louisv10 | 1739 | 58 | 181 | 100-81 | 100% (c_nav4 6-0*) |
| 38 | **us:c_line7m** | 1739 | 88 | 100 | 31-69 |  |
| 39 | SampleProvider.SPAARK | 1736 | 57 | 185 | 105-80 | 33% (c_anc3 1-2*) |
| 40 | reeceyang.v5anaconda | 1721 | 43 | 326 | 144-182 | 80% (c_aura2 8-2*) |
| 41 | **us:c_line5** | 1703 | 91 | 100 | 28-72 |  |
| 42 | battlecode-archive.Sprint1 | 1697 | 44 | 310 | 133-177 | 100% (c_aura2 10-0*) |
| 43 | **us:c_line4** | 1665 | 93 | 100 | 25-75 |  |
| 44 | ipince.bobby | 1618 | 63 | 159 | 87-72 | 67% (c_swarm1 2-1*) |
| 45 | polyllc.poly | 1610 | 64 | 168 | 88-80 | 100% (g_iter0 2-0*) |
| 46 | legobridge.tacoplayer | 1603 | 57 | 203 | 109-94 | 85% (g_iter0 11-2*) |
| 47 | SteamBlizzard.newVnewME | 1601 | 53 | 218 | 108-110 | 80% (g_iter0 4-1*) |
| 48 | TheK098.qp1_7_sprint_1 | 1574 | 56 | 199 | 107-92 | 100% (c_swarm1 6-0*) |
| 49 | toyat522.bot5a | 1546 | 53 | 211 | 106-105 | 80% (g_iter0 4-1*) |
| 50 | elgoldie.head_v5 | 1543 | 52 | 211 | 107-104 | 100% (g_iter0 2-0*) |
| 51 | DukeBas._main | 1525 | 56 | 197 | 104-93 | 100% (g_iter0 2-0*) |
| 52 | ColtG5.rexv9 | 1519 | 52 | 218 | 111-107 | 100% (g_iter0 2-0*) |
| 53 | beaverbois.USQualifiers | 1479 | 54 | 205 | 105-100 | 50% (g_iter0 1-1*) |
| 54 | kevinli405.maggi3_2 | 1470 | 54 | 214 | 109-105 | 100% (g_iter0 2-0*) |
| 55 | BrysonJGalapon.friday | 1447 | 54 | 188 | 95-93 | 100% (g_iter0 2-0*) |
| 56 | Nawlej.PoonPoon | 1445 | 57 | 193 | 95-98 | 100% (g_iter0 2-0*) |
| 57 | nail-e.Barry | 1426 | 51 | 214 | 110-104 | 100% (g_iter0 2-0*) |
| 58 | yaonam.PoonPoonv4 | 1414 | 46 | 367 | 130-237 | 90% (c_aura2 9-1*) |
| 59 | kevinli405.maggi3 | 1411 | 53 | 226 | 117-109 | 100% (g_iter0 5-0*) |
| 60 | aj-chau.attempt1 | 1408 | 57 | 190 | 99-91 | 100% (g_iter0 5-0*) |
| 61 | prisms-cs-club.prisms10 | 1378 | 55 | 203 | 98-105 | 100% (g_iter0 2-0*) |
| 62 | ipince.bobby_v2 | 1343 | 54 | 212 | 103-109 | 67% (c_swarm1 2-1*) |
| 63 | mama4294.currentPlayer | 1342 | 52 | 221 | 108-113 | 100% (g_iter0 2-0*) |
| 64 | andrewgopher.gopherbot | 1276 | 49 | 245 | 119-126 | 100% (g_iter0 2-0*) |
| 65 | BrysonJGalapon.aloha | 1271 | 48 | 243 | 121-122 | 100% (c_swarm1 3-0*) |
| 66 | bewuwy.deathbot4 | 1270 | 47 | 267 | 127-140 | 100% (g_iter0 2-0*) |
| 67 | JfeMak.realplayer2 | 1262 | 54 | 198 | 96-102 | 100% (g_iter0 2-0*) |
| 68 | PSUtblock.sprint_four_player | 1240 | 56 | 205 | 105-100 | 100% (g_iter0 2-0*) |
| 69 | **us:examplefuncsplayer** | 1224 | 380 | 6 | 0-6 |  |
| 70 | SampleProvider.SPAARK_1_12_2023 | 1212 | 48 | 250 | 119-131 | 100% (c_swarm1 3-0*) |
| 71 | NolanChai.nolan_1 | 1188 | 48 | 250 | 122-128 | 100% (g_iter0 2-0*) |
| 72 | Juanbri02.matfisplayer1 | 1186 | 49 | 243 | 115-128 | 100% (g_iter0 5-0*) |
| 73 | Nawlej.PoonPoonv3 | 1184 | 47 | 256 | 121-135 | 100% (g_iter0 5-0*) |
| 74 | SDainard-PDX.Team_Player | 1181 | 51 | 227 | 106-121 | 100% (g_iter0 2-0*) |
| 75 | andrewgopher.gopherbot1 | 1170 | 50 | 241 | 111-130 | 100% (g_iter0 2-0*) |
| 76 | jyorkio.elicompbot | 1161 | 49 | 231 | 111-120 | 100% (g_iter0 2-0*) |
| 77 | vontell.regressiongames | 1104 | 45 | 266 | 128-138 | 100% (g_iter0 5-0*) |
| 78 | SteamBlizzard.Block | 1073 | 48 | 268 | 120-148 | 100% (g_iter0 5-0*) |
| 79 | legobridge.kushalplayer | 1061 | 57 | 197 | 87-110 | 100% (g_iter0 2-0*) |
| 80 | ax-95174.MPAction | 1055 | 50 | 232 | 107-125 | 100% (c_swarm1 3-0*) |
| 81 | JackLee9355.jackPlayer | 1053 | 52 | 238 | 107-131 | 100% (g_iter0 2-0*) |
| 82 | Patela171.Battlecode2023_Robot | 1044 | 51 | 236 | 107-129 | 100% (g_iter0 2-0*) |
| 83 | michael-tyl.hqrewrite | 997 | 51 | 228 | 107-121 | 100% (g_iter0 2-0*) |
| 84 | nail-e.Dante | 977 | 49 | 254 | 119-135 | 100% (g_iter0 2-0*) |
| 85 | Chahat08.toph | 976 | 50 | 238 | 105-133 | 100% (g_iter0 2-0*) |
| 86 | mama4294.learningBot | 947 | 52 | 236 | 103-133 | 100% (g_iter0 2-0*) |
| 87 | anicolao.submission | 931 | 47 | 290 | 130-160 | 100% (g_iter0 2-0*) |
| 88 | team-remember-to-hydrate.sprint_1 | 872 | 51 | 250 | 103-147 | 100% (g_iter0 2-0*) |
| 89 | Vinceyou1.Player1 | 813 | 49 | 256 | 111-145 | 100% (g_iter0 2-0*) |
| 90 | addiesteward.elicompbot | 781 | 48 | 278 | 122-156 | 100% (g_iter0 5-0*) |
| 91 | michael-tyl.cc_v0_5_0_6 | 767 | 44 | 321 | 139-182 | 100% (g_iter0 2-0*) |
| 92 | Chahat08.lazarus | 738 | 48 | 272 | 121-151 | 100% (g_iter0 2-0*) |
| 93 | toyat522.bot5 | 738 | 49 | 274 | 118-156 | 100% (g_iter0 2-0*) |
| 94 | Swordman51.AdeptusAstartes2 | 729 | 47 | 268 | 115-153 | 100% (g_iter0 2-0*) |
| 95 | monmouth-college-cs.elicompbot | 721 | 47 | 293 | 126-167 | 100% (g_iter0 2-0*) |
| 96 | anicolao.jumbled | 601 | 49 | 290 | 122-168 | 100% (g_iter0 5-0*) |
| 97 | ShatterXD.SRNNbot | 594 | 54 | 238 | 101-137 | 100% (g_iter0 2-0*) |
| 98 | NotLLeon.player | 407 | 59 | 247 | 105-142 | 100% (g_iter0 2-0*) |
| 99 | CodeClash-ai.mysubmission | 392 | 55 | 290 | 128-162 | 100% (g_iter0 2-0*) |
| 100 | addiesteward.NDeClaw | 351 | 60 | 259 | 105-154 | 100% (g_iter0 5-0*) |
| 101 | Yooncw0223.lec3player | 61 | 70 | 256 | 37-219 | 100% (g_iter0 5-0*) |
| 102 | andrewkbank.First | -17 | 82 | 193 | 22-171 | 100% (g_iter0 2-0*) |
