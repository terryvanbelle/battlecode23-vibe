# Ladder

10170 games (2121 ours, 8049 between field bots on the ladder replica), 10056 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_def3 | 2050 +- 57 | 12 of 100 | 191 | 118-73 | 84.7% | 27.4% (vs 11) |
| c_anc3 | 2008 +- 61 | 14 of 100 | 163 | 88-75 | 82.9% | 25.2% (vs 12) |
| c_nav5 | 1948 +- 71 | 17 of 100 | 126 | 61-65 | 80.2% | 23.2% (vs 14) |
| c_nav6 | 1934 +- 71 | 18 of 100 | 129 | 58-71 | 79.6% | 22.0% (vs 14) |
| c_nav4 | 1915 +- 52 | 20 of 100 | 221 | 108-113 | 78.7% | 22.1% (vs 15) |
| c_swarm1 | 1841 +- 48 | 24 of 100 | 271 | 128-143 | 74.9% | 21.2% (vs 18) |
| c_line8a | 1794 +- 71 | 30 of 100 | 139 | 47-92 | 72.4% | 24.1% (vs 23) |
| g_iter0 | 1794 +- 48 | 31 of 100 | 456 | 230-226 | 72.4% | 24.1% (vs 23) |
| c_line6 | 1761 +- 88 | 33 of 100 | 100 | 32-68 | 70.5% | 22.2% (vs 24) |
| c_line7m | 1749 +- 88 | 36 of 100 | 100 | 31-69 | 69.9% | 23.4% (vs 26) |
| c_line5 | 1713 +- 91 | 39 of 100 | 100 | 28-72 | 67.8% | 22.3% (vs 28) |
| c_line4 | 1676 +- 93 | 41 of 100 | 100 | 25-75 | 65.5% | 20.1% (vs 29) |
| examplefuncsplayer | 1244 +- 380 | 66 of 100 | 6 | 0-6 | 38.5% | 12.0% (vs 53) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_def3), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2353 | 71 | 146 | 111-35 | 0% (g_iter0 0-36) |
| 2 | awesomelemonade.finalBot | 2331 | 66 | 244 | 205-39 | 20% (c_def3 2-8*) |
| 3 | maxwelljones14.MPWorking | 2307 | 76 | 121 | 86-35 | 0% (g_iter0 0-5*) |
| 4 | vrangr1.AFinalsBot | 2284 | 63 | 252 | 208-44 | 40% (c_def3 4-6*) |
| 5 | carlguo866.submit26_final | 2263 | 70 | 139 | 94-45 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2216 | 75 | 131 | 90-41 | 0% (c_anc3 0-3*) |
| 7 | pranayagra.finalbotfinal | 2176 | 51 | 301 | 218-83 | 40% (c_def3 4-6*) |
| 8 | pranayagra.finalbotfinaltwo | 2168 | 67 | 156 | 102-54 | 33% (c_anc3 2-4*) |
| 9 | georgezhang02.FB_ZZZ | 2163 | 64 | 158 | 105-53 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2146 | 72 | 148 | 104-44 | 0% (c_def3 0-6*) |
| 11 | jmerle.camel_case_v30_final | 2099 | 49 | 289 | 205-84 | 31% (c_def3 5-11*) |
| 12 | **us:c_def3** | 2050 | 57 | 191 | 118-73 |  |
| 13 | CyrilSharma.finalBot | 2011 | 58 | 194 | 113-81 | 33% (c_def3 3-6*) |
| 14 | **us:c_anc3** | 2008 | 61 | 163 | 88-75 |  |
| 15 | ethanlabelle.dev | 2006 | 58 | 173 | 110-63 | 58% (c_def3 7-5*) |
| 16 | NotLLeon.v7 | 1955 | 44 | 302 | 179-123 | 67% (c_def3 18-9*) |
| 17 | **us:c_nav5** | 1948 | 71 | 126 | 61-65 |  |
| 18 | **us:c_nav6** | 1934 | 71 | 129 | 58-71 |  |
| 19 | georgezhang02.CB_tuning2 | 1933 | 46 | 277 | 166-111 | 60% (c_def3 6-4*) |
| 20 | **us:c_nav4** | 1915 | 52 | 221 | 108-113 |  |
| 21 | ethanlabelle.v19 | 1876 | 63 | 150 | 90-60 | 100% (c_nav5 3-0*) |
| 22 | britacatalin.FinalBot | 1873 | 45 | 290 | 159-131 | 70% (c_def3 19-8*) |
| 23 | GabeG888.v8 | 1847 | 56 | 181 | 95-86 | 89% (c_def3 16-2*) |
| 24 | **us:c_swarm1** | 1841 | 48 | 271 | 128-143 |  |
| 25 | programjames.fourthbot | 1822 | 61 | 169 | 95-74 | 17% (c_nav4 1-5*) |
| 26 | GabeG888.v8o1 | 1819 | 61 | 157 | 92-65 | 100% (c_nav5 3-0*) |
| 27 | DannyZhang686.pqual2 | 1807 | 57 | 190 | 104-86 | 83% (c_anc3 5-1*) |
| 28 | VarunVejalla.karel | 1801 | 57 | 185 | 101-84 | 67% (c_nav4 6-3*) |
| 29 | VarunVejalla.ali8 | 1801 | 63 | 161 | 90-71 | 100% (c_def3 6-0*) |
| 30 | **us:c_line8a** | 1794 | 71 | 139 | 47-92 |  |
| 31 | **us:g_iter0** | 1794 | 48 | 456 | 230-226 |  |
| 32 | NicholasKelly15.gopher10 | 1793 | 65 | 145 | 82-63 | 100% (c_anc3 3-0*) |
| 33 | **us:c_line6** | 1761 | 88 | 100 | 32-68 |  |
| 34 | louishu17.louisv10 | 1755 | 61 | 166 | 94-72 | 100% (c_nav4 6-0*) |
| 35 | louishu17.wouisv8 | 1752 | 59 | 191 | 106-85 | 33% (c_nav4 2-4*) |
| 36 | **us:c_line7m** | 1749 | 88 | 100 | 31-69 |  |
| 37 | SampleProvider.SPAARK | 1735 | 59 | 170 | 95-75 | 33% (c_anc3 1-2*) |
| 38 | reeceyang.v5anaconda | 1732 | 44 | 300 | 139-161 | 90% (c_def3 9-1*) |
| 39 | **us:c_line5** | 1713 | 91 | 100 | 28-72 |  |
| 40 | battlecode-archive.Sprint1 | 1713 | 46 | 276 | 123-153 | 100% (c_def3 10-0*) |
| 41 | **us:c_line4** | 1676 | 93 | 100 | 25-75 |  |
| 42 | ipince.bobby | 1623 | 64 | 153 | 83-70 | 67% (c_swarm1 2-1*) |
| 43 | SteamBlizzard.newVnewME | 1622 | 55 | 201 | 103-98 | 80% (g_iter0 4-1*) |
| 44 | legobridge.tacoplayer | 1617 | 59 | 191 | 103-88 | 85% (g_iter0 11-2*) |
| 45 | polyllc.poly | 1609 | 70 | 148 | 76-72 | 100% (g_iter0 2-0*) |
| 46 | TheK098.qp1_7_sprint_1 | 1593 | 58 | 187 | 102-85 | 100% (c_swarm1 6-0*) |
| 47 | toyat522.bot5a | 1570 | 58 | 178 | 91-87 | 80% (g_iter0 4-1*) |
| 48 | elgoldie.head_v5 | 1547 | 57 | 176 | 86-90 | 100% (g_iter0 2-0*) |
| 49 | DukeBas._main | 1542 | 59 | 182 | 98-84 | 100% (g_iter0 2-0*) |
| 50 | ColtG5.rexv9 | 1534 | 55 | 197 | 100-97 | 100% (g_iter0 2-0*) |
| 51 | beaverbois.USQualifiers | 1496 | 59 | 173 | 90-83 | 50% (g_iter0 1-1*) |
| 52 | kevinli405.maggi3_2 | 1482 | 57 | 196 | 100-96 | 100% (g_iter0 2-0*) |
| 53 | Nawlej.PoonPoon | 1479 | 62 | 166 | 86-80 | 100% (g_iter0 2-0*) |
| 54 | BrysonJGalapon.friday | 1478 | 57 | 176 | 91-85 | 100% (g_iter0 2-0*) |
| 55 | nail-e.Barry | 1448 | 57 | 179 | 93-86 | 100% (g_iter0 2-0*) |
| 56 | yaonam.PoonPoonv4 | 1425 | 49 | 324 | 116-208 | 90% (c_def3 9-1*) |
| 57 | kevinli405.maggi3 | 1418 | 58 | 191 | 96-95 | 100% (g_iter0 5-0*) |
| 58 | aj-chau.attempt1 | 1418 | 59 | 178 | 92-86 | 100% (g_iter0 5-0*) |
| 59 | prisms-cs-club.prisms10 | 1393 | 58 | 185 | 88-97 | 100% (g_iter0 2-0*) |
| 60 | mama4294.currentPlayer | 1361 | 57 | 187 | 94-93 | 100% (g_iter0 2-0*) |
| 61 | ipince.bobby_v2 | 1360 | 58 | 188 | 93-95 | 67% (c_swarm1 2-1*) |
| 62 | andrewgopher.gopherbot | 1296 | 53 | 215 | 103-112 | 100% (g_iter0 2-0*) |
| 63 | JfeMak.realplayer2 | 1292 | 59 | 172 | 86-86 | 100% (g_iter0 2-0*) |
| 64 | BrysonJGalapon.aloha | 1292 | 53 | 205 | 100-105 | 100% (c_swarm1 3-0*) |
| 65 | bewuwy.deathbot4 | 1279 | 50 | 241 | 111-130 | 100% (g_iter0 2-0*) |
| 66 | **us:examplefuncsplayer** | 1244 | 380 | 6 | 0-6 |  |
| 67 | PSUtblock.sprint_four_player | 1241 | 59 | 190 | 96-94 | 100% (g_iter0 2-0*) |
| 68 | SampleProvider.SPAARK_1_12_2023 | 1233 | 51 | 229 | 108-121 | 100% (c_swarm1 3-0*) |
| 69 | SDainard-PDX.Team_Player | 1217 | 58 | 185 | 89-96 | 100% (g_iter0 2-0*) |
| 70 | Juanbri02.matfisplayer1 | 1204 | 53 | 207 | 98-109 | 100% (g_iter0 5-0*) |
| 71 | Nawlej.PoonPoonv3 | 1190 | 51 | 226 | 104-122 | 100% (g_iter0 5-0*) |
| 72 | NolanChai.nolan_1 | 1186 | 52 | 214 | 97-117 | 100% (g_iter0 2-0*) |
| 73 | jyorkio.elicompbot | 1183 | 51 | 216 | 106-110 | 100% (g_iter0 2-0*) |
| 74 | andrewgopher.gopherbot1 | 1177 | 54 | 214 | 99-115 | 100% (g_iter0 2-0*) |
| 75 | vontell.regressiongames | 1119 | 48 | 239 | 113-126 | 100% (g_iter0 5-0*) |
| 76 | SteamBlizzard.Block | 1087 | 50 | 246 | 108-138 | 100% (g_iter0 5-0*) |
| 77 | JackLee9355.jackPlayer | 1086 | 55 | 215 | 96-119 | 100% (g_iter0 2-0*) |
| 78 | ax-95174.MPAction | 1078 | 53 | 205 | 94-111 | 100% (c_swarm1 3-0*) |
| 79 | legobridge.kushalplayer | 1066 | 64 | 166 | 72-94 | 100% (g_iter0 2-0*) |
| 80 | Patela171.Battlecode2023_Robot | 1058 | 53 | 216 | 98-118 | 100% (g_iter0 2-0*) |
| 81 | michael-tyl.hqrewrite | 1009 | 53 | 212 | 96-116 | 100% (g_iter0 2-0*) |
| 82 | nail-e.Dante | 996 | 52 | 224 | 103-121 | 100% (g_iter0 2-0*) |
| 83 | Chahat08.toph | 994 | 54 | 205 | 89-116 | 100% (g_iter0 2-0*) |
| 84 | anicolao.submission | 964 | 49 | 266 | 119-147 | 100% (g_iter0 2-0*) |
| 85 | mama4294.learningBot | 962 | 56 | 212 | 91-121 | 100% (g_iter0 2-0*) |
| 86 | team-remember-to-hydrate.sprint_1 | 912 | 52 | 233 | 96-137 | 100% (g_iter0 2-0*) |
| 87 | Vinceyou1.Player1 | 818 | 54 | 220 | 91-129 | 100% (g_iter0 2-0*) |
| 88 | addiesteward.elicompbot | 801 | 50 | 258 | 113-145 | 100% (g_iter0 5-0*) |
| 89 | michael-tyl.cc_v0_5_0_6 | 791 | 46 | 291 | 123-168 | 100% (g_iter0 2-0*) |
| 90 | Swordman51.AdeptusAstartes2 | 762 | 49 | 245 | 105-140 | 100% (g_iter0 2-0*) |
| 91 | Chahat08.lazarus | 760 | 53 | 228 | 102-126 | 100% (g_iter0 2-0*) |
| 92 | monmouth-college-cs.elicompbot | 752 | 51 | 255 | 109-146 | 100% (g_iter0 2-0*) |
| 93 | toyat522.bot5 | 739 | 52 | 242 | 101-141 | 100% (g_iter0 2-0*) |
| 94 | anicolao.jumbled | 633 | 51 | 268 | 110-158 | 100% (g_iter0 5-0*) |
| 95 | ShatterXD.SRNNbot | 617 | 57 | 219 | 90-129 | 100% (g_iter0 2-0*) |
| 96 | NotLLeon.player | 431 | 60 | 234 | 96-138 | 100% (g_iter0 2-0*) |
| 97 | CodeClash-ai.mysubmission | 428 | 60 | 239 | 98-141 | 100% (g_iter0 2-0*) |
| 98 | addiesteward.NDeClaw | 389 | 62 | 237 | 96-141 | 100% (g_iter0 5-0*) |
| 99 | Yooncw0223.lec3player | 114 | 74 | 226 | 33-193 | 100% (g_iter0 5-0*) |
| 100 | andrewkbank.First | 38 | 84 | 177 | 21-156 | 100% (g_iter0 2-0*) |
