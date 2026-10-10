# Ladder

12565 games (2686 ours, 6 of the stock examplefuncsplayer, 9873 between field bots on the ladder replica), 12285 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 104 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2138 +- 91 | 12 of 103 | 100 | 64-36 | 87.1% | 32.6% (vs 11) |
| c_spread2 | 2106 +- 90 | 13 of 103 | 100 | 61-39 | 86.0% | 28.8% (vs 11) |
| c_def3 | 2076 +- 65 | 14 of 103 | 194 | 117-77 | 84.8% | 25.5% (vs 11) |
| c_aura2 | 2067 +- 58 | 15 of 103 | 258 | 135-123 | 84.5% | 24.5% (vs 11) |
| c_flee3 | 2054 +- 89 | 17 of 103 | 100 | 56-44 | 84.0% | 25.3% (vs 12) |
| c_anc3 | 2047 +- 70 | 18 of 103 | 161 | 87-74 | 83.7% | 24.6% (vs 12) |
| c_nav5 | 1987 +- 78 | 21 of 103 | 126 | 61-65 | 81.3% | 23.0% (vs 14) |
| c_nav6 | 1974 +- 78 | 23 of 103 | 129 | 58-71 | 80.7% | 23.6% (vs 15) |
| c_nav4 | 1946 +- 60 | 24 of 103 | 221 | 108-113 | 79.5% | 21.1% (vs 15) |
| c_swarm1 | 1867 +- 57 | 28 of 103 | 268 | 126-142 | 75.9% | 20.3% (vs 18) |
| c_line8a | 1825 +- 78 | 33 of 103 | 139 | 47-92 | 73.9% | 22.7% (vs 22) |
| g_iter0 | 1810 +- 55 | 34 of 103 | 455 | 230-225 | 73.1% | 21.4% (vs 22) |
| c_line6 | 1793 +- 94 | 36 of 103 | 100 | 32-68 | 72.3% | 21.2% (vs 23) |
| c_line7m | 1780 +- 95 | 37 of 103 | 100 | 31-69 | 71.7% | 20.2% (vs 23) |
| c_line5 | 1742 +- 97 | 43 of 103 | 100 | 28-72 | 69.8% | 22.6% (vs 28) |
| c_line4 | 1702 +- 100 | 45 of 103 | 100 | 25-75 | 67.7% | 20.3% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_aura2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2400 | 81 | 157 | 117-40 | 0% (g_iter0 0-35) |
| 2 | awesomelemonade.finalBot | 2378 | 70 | 298 | 246-52 | 20% (c_aura2 2-8*) |
| 3 | maxwelljones14.MPWorking | 2366 | 81 | 146 | 102-44 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2313 | 77 | 159 | 106-53 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2300 | 64 | 310 | 243-67 | 40% (c_aura2 4-6*) |
| 6 | AnOvercookedFork.quals | 2268 | 75 | 167 | 112-55 | 20% (c_aura2 3-12*) |
| 7 | pranayagra.finalbotfinaltwo | 2224 | 70 | 190 | 125-65 | 29% (c_aura2 5-12*) |
| 8 | georgezhang02.FB_ZZZ | 2209 | 70 | 179 | 116-63 | 0% (c_anc3 0-3*) |
| 9 | pranayagra.finalbotfinal | 2202 | 54 | 382 | 263-119 | 36% (c_aura2 9-16*) |
| 10 | battlecode-archive.sprintBot | 2182 | 73 | 172 | 115-57 | 33% (c_aura2 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2147 | 53 | 368 | 251-117 | 34% (c_aura2 10-19*) |
| 12 | **us:c_well5** | 2138 | 91 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2106 | 90 | 100 | 61-39 |  |
| 14 | **us:c_def3** | 2076 | 65 | 194 | 117-77 |  |
| 15 | **us:c_aura2** | 2067 | 58 | 258 | 135-123 |  |
| 16 | CyrilSharma.finalBot | 2066 | 62 | 228 | 132-96 | 33% (c_aura2 4-8*) |
| 17 | **us:c_flee3** | 2054 | 89 | 100 | 56-44 |  |
| 18 | **us:c_anc3** | 2047 | 70 | 161 | 87-74 |  |
| 19 | ethanlabelle.dev | 2024 | 60 | 215 | 126-89 | 52% (c_aura2 11-10*) |
| 20 | NotLLeon.v7 | 1994 | 50 | 366 | 210-156 | 63% (c_aura2 12-7*) |
| 21 | **us:c_nav5** | 1987 | 78 | 126 | 61-65 |  |
| 22 | georgezhang02.CB_tuning2 | 1981 | 50 | 352 | 202-150 | 61% (c_aura2 17-11*) |
| 23 | **us:c_nav6** | 1974 | 78 | 129 | 58-71 |  |
| 24 | **us:c_nav4** | 1946 | 60 | 221 | 108-113 |  |
| 25 | ethanlabelle.v19 | 1905 | 61 | 200 | 112-88 | 67% (c_aura2 10-5*) |
| 26 | britacatalin.FinalBot | 1903 | 49 | 361 | 186-175 | 80% (c_aura2 12-3*) |
| 27 | GabeG888.v8 | 1868 | 59 | 213 | 112-101 | 89% (c_def3 16-2*) |
| 28 | **us:c_swarm1** | 1867 | 57 | 268 | 126-142 |  |
| 29 | programjames.fourthbot | 1849 | 62 | 201 | 111-90 | 100% (c_aura2 3-0*) |
| 30 | GabeG888.v8o1 | 1840 | 60 | 201 | 117-84 | 100% (c_nav5 3-0*) |
| 31 | VarunVejalla.ali8 | 1838 | 64 | 187 | 107-80 | 100% (c_def3 8-0*) |
| 32 | VarunVejalla.karel | 1831 | 59 | 217 | 120-97 | 67% (c_nav4 6-3*) |
| 33 | **us:c_line8a** | 1825 | 78 | 139 | 47-92 |  |
| 34 | **us:g_iter0** | 1810 | 55 | 455 | 230-225 |  |
| 35 | DannyZhang686.pqual2 | 1810 | 58 | 226 | 120-106 | 83% (c_anc3 5-1*) |
| 36 | **us:c_line6** | 1793 | 94 | 100 | 32-68 |  |
| 37 | **us:c_line7m** | 1780 | 95 | 100 | 31-69 |  |
| 38 | louishu17.louisv10 | 1774 | 62 | 197 | 110-87 | 100% (c_nav4 6-0*) |
| 39 | NicholasKelly15.gopher10 | 1774 | 65 | 178 | 98-80 | 100% (c_anc3 3-0*) |
| 40 | SampleProvider.SPAARK | 1760 | 61 | 202 | 113-89 | 33% (c_anc3 1-2*) |
| 41 | louishu17.wouisv8 | 1759 | 62 | 213 | 113-100 | 83% (c_aura2 5-1*) |
| 42 | reeceyang.v5anaconda | 1756 | 49 | 371 | 158-213 | 80% (c_aura2 8-2*) |
| 43 | **us:c_line5** | 1742 | 97 | 100 | 28-72 |  |
| 44 | battlecode-archive.Sprint1 | 1716 | 50 | 345 | 139-206 | 100% (c_aura2 10-0*) |
| 45 | **us:c_line4** | 1702 | 100 | 100 | 25-75 |  |
| 46 | ipince.bobby | 1654 | 66 | 170 | 97-73 | 67% (c_swarm1 2-1*) |
| 47 | SteamBlizzard.newVnewME | 1607 | 57 | 231 | 116-115 | 80% (g_iter0 4-1*) |
| 48 | legobridge.tacoplayer | 1606 | 60 | 220 | 117-103 | 85% (g_iter0 11-2*) |
| 49 | TheK098.qp1_7_sprint_1 | 1582 | 59 | 215 | 118-97 | 100% (c_swarm1 6-0*) |
| 50 | polyllc.poly | 1565 | 65 | 188 | 93-95 | 100% (g_iter0 2-0*) |
| 51 | toyat522.bot5a | 1533 | 57 | 224 | 113-111 | 80% (g_iter0 4-1*) |
| 52 | elgoldie.head_v5 | 1528 | 56 | 228 | 114-114 | 100% (g_iter0 2-0*) |
| 53 | DukeBas._main | 1507 | 60 | 209 | 111-98 | 100% (g_iter0 2-0*) |
| 54 | ColtG5.rexv9 | 1499 | 56 | 230 | 117-113 | 100% (g_iter0 2-0*) |
| 55 | beaverbois.USQualifiers | 1469 | 58 | 218 | 115-103 | 50% (g_iter0 1-1*) |
| 56 | kevinli405.maggi3_2 | 1438 | 56 | 246 | 123-123 | 100% (g_iter0 2-0*) |
| 57 | Nawlej.PoonPoon | 1422 | 59 | 215 | 108-107 | 100% (g_iter0 2-0*) |
| 58 | BrysonJGalapon.friday | 1402 | 58 | 205 | 104-101 | 100% (g_iter0 2-0*) |
| 59 | nail-e.Barry | 1397 | 56 | 231 | 118-113 | 100% (g_iter0 2-0*) |
| 60 | yaonam.PoonPoonv4 | 1393 | 51 | 401 | 138-263 | 90% (c_aura2 9-1*) |
| 61 | aj-chau.attempt1 | 1374 | 59 | 213 | 112-101 | 100% (g_iter0 5-0*) |
| 62 | kevinli405.maggi3 | 1370 | 57 | 237 | 121-116 | 100% (g_iter0 5-0*) |
| 63 | prisms-cs-club.prisms10 | 1327 | 59 | 219 | 105-114 | 100% (g_iter0 2-0*) |
| 64 | mama4294.currentPlayer | 1305 | 56 | 238 | 117-121 | 100% (g_iter0 2-0*) |
| 65 | ipince.bobby_v2 | 1279 | 57 | 241 | 116-125 | 67% (c_swarm1 2-1*) |
| 66 | andrewgopher.gopherbot | 1216 | 56 | 259 | 128-131 | 100% (g_iter0 2-0*) |
| 67 | bewuwy.deathbot4 | 1212 | 53 | 289 | 139-150 | 100% (g_iter0 2-0*) |
| 68 | BrysonJGalapon.aloha | 1204 | 54 | 261 | 129-132 | 100% (c_swarm1 3-0*) |
| 69 | JfeMak.realplayer2 | 1195 | 58 | 225 | 108-117 | 100% (g_iter0 2-0*) |
| 70 | PSUtblock.sprint_four_player | 1176 | 59 | 238 | 121-117 | 100% (g_iter0 2-0*) |
| 71 | SampleProvider.SPAARK_1_12_2023 | 1140 | 55 | 267 | 128-139 | 100% (c_swarm1 3-0*) |
| 72 | Nawlej.PoonPoonv3 | 1125 | 55 | 274 | 134-140 | 100% (g_iter0 5-0*) |
| 73 | NolanChai.nolan_1 | 1110 | 54 | 288 | 139-149 | 100% (g_iter0 2-0*) |
| 74 | Juanbri02.matfisplayer1 | 1107 | 55 | 266 | 125-141 | 100% (g_iter0 5-0*) |
| 75 | SDainard-PDX.Team_Player | 1100 | 57 | 248 | 118-130 | 100% (g_iter0 2-0*) |
| 76 | andrewgopher.gopherbot1 | 1097 | 56 | 265 | 123-142 | 100% (g_iter0 2-0*) |
| 77 | jyorkio.elicompbot | 1076 | 56 | 251 | 121-130 | 100% (g_iter0 2-0*) |
| 78 | vontell.regressiongames | 1021 | 54 | 286 | 138-148 | 100% (g_iter0 5-0*) |
| 79 | legobridge.kushalplayer | 974 | 63 | 220 | 99-121 | 100% (g_iter0 2-0*) |
| 80 | SteamBlizzard.Block | 970 | 57 | 294 | 132-162 | 100% (g_iter0 5-0*) |
| 81 | Patela171.Battlecode2023_Robot | 967 | 58 | 272 | 126-146 | 100% (g_iter0 2-0*) |
| 82 | ax-95174.MPAction | 960 | 59 | 253 | 118-135 | 100% (c_swarm1 3-0*) |
| 83 | JackLee9355.jackPlayer | 936 | 62 | 255 | 113-142 | 100% (g_iter0 2-0*) |
| 84 | michael-tyl.hqrewrite | 881 | 60 | 259 | 121-138 | 100% (g_iter0 2-0*) |
| 85 | nail-e.Dante | 876 | 59 | 283 | 137-146 | 100% (g_iter0 2-0*) |
| 86 | Chahat08.toph | 874 | 60 | 265 | 120-145 | 100% (g_iter0 2-0*) |
| 87 | mama4294.learningBot | 838 | 62 | 265 | 115-150 | 100% (g_iter0 2-0*) |
| 88 | anicolao.submission | 821 | 59 | 310 | 140-170 | 100% (g_iter0 2-0*) |
| 89 | team-remember-to-hydrate.sprint_1 | 747 | 63 | 273 | 116-157 | 100% (g_iter0 2-0*) |
| 90 | Vinceyou1.Player1 | 685 | 65 | 268 | 114-154 | 100% (g_iter0 2-0*) |
| 91 | addiesteward.elicompbot | 659 | 65 | 287 | 127-160 | 100% (g_iter0 5-0*) |
| 92 | michael-tyl.cc_v0_5_0_6 | 627 | 63 | 337 | 144-193 | 100% (g_iter0 2-0*) |
| 93 | toyat522.bot5 | 618 | 66 | 307 | 136-171 | 100% (g_iter0 2-0*) |
| 94 | Chahat08.lazarus | 599 | 67 | 281 | 122-159 | 100% (g_iter0 2-0*) |
| 95 | monmouth-college-cs.elicompbot | 591 | 65 | 312 | 137-175 | 100% (g_iter0 2-0*) |
| 96 | Swordman51.AdeptusAstartes2 | 586 | 67 | 284 | 122-162 | 100% (g_iter0 2-0*) |
| 97 | anicolao.jumbled | 474 | 71 | 307 | 136-171 | 100% (g_iter0 5-0*) |
| 98 | ShatterXD.SRNNbot | 462 | 72 | 276 | 118-158 | 100% (g_iter0 2-0*) |
| 99 | NotLLeon.player | 254 | 87 | 269 | 120-149 | 100% (g_iter0 2-0*) |
| 100 | CodeClash-ai.mysubmission | 229 | 86 | 302 | 129-173 | 100% (g_iter0 2-0*) |
| 101 | addiesteward.NDeClaw | 180 | 92 | 273 | 110-163 | 100% (g_iter0 5-0*) |
| 102 | Yooncw0223.lec3player | -120 | 108 | 264 | 38-226 | 100% (g_iter0 5-0*) |
| 103 | andrewkbank.First | -199 | 117 | 200 | 23-177 | 100% (g_iter0 2-0*) |
