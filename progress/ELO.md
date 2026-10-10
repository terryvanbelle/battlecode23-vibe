# Ladder

10976 games (2369 ours, 8607 between field bots on the ladder replica), 10841 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_aura2 | 2045 +- 67 | 12 of 102 | 138 | 78-60 | 85.1% | 28.6% (vs 11) |
| c_def3 | 2023 +- 55 | 13 of 102 | 199 | 120-79 | 84.2% | 26.2% (vs 11) |
| c_flee3 | 1998 +- 82 | 15 of 102 | 100 | 56-44 | 83.2% | 25.8% (vs 12) |
| c_anc3 | 1993 +- 61 | 16 of 102 | 163 | 88-75 | 82.9% | 25.3% (vs 12) |
| c_nav5 | 1933 +- 71 | 19 of 102 | 126 | 61-65 | 80.2% | 23.3% (vs 14) |
| c_nav6 | 1919 +- 71 | 21 of 102 | 129 | 58-71 | 79.6% | 23.9% (vs 15) |
| c_nav4 | 1900 +- 52 | 22 of 102 | 221 | 108-113 | 78.6% | 22.1% (vs 15) |
| c_swarm1 | 1827 +- 48 | 26 of 102 | 271 | 128-143 | 74.9% | 21.2% (vs 18) |
| c_line8a | 1781 +- 71 | 32 of 102 | 139 | 47-92 | 72.4% | 24.2% (vs 23) |
| g_iter0 | 1780 +- 48 | 33 of 102 | 456 | 230-226 | 72.4% | 24.1% (vs 23) |
| c_line6 | 1747 +- 88 | 35 of 102 | 100 | 32-68 | 70.5% | 22.3% (vs 24) |
| c_line7m | 1735 +- 88 | 37 of 102 | 100 | 31-69 | 69.9% | 22.4% (vs 25) |
| c_line5 | 1700 +- 90 | 41 of 102 | 100 | 28-72 | 67.8% | 22.3% (vs 28) |
| c_line4 | 1662 +- 93 | 43 of 102 | 100 | 25-75 | 65.6% | 20.1% (vs 29) |
| examplefuncsplayer | 1228 +- 380 | 69 of 102 | 6 | 0-6 | 38.5% | 12.6% (vs 54) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_aura2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2340 | 71 | 146 | 111-35 | 0% (g_iter0 0-36) |
| 2 | awesomelemonade.finalBot | 2320 | 63 | 267 | 224-43 | 20% (c_aura2 2-8*) |
| 3 | maxwelljones14.MPWorking | 2303 | 73 | 130 | 93-37 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2254 | 70 | 142 | 97-45 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2253 | 58 | 278 | 225-53 | 40% (c_aura2 4-6*) |
| 6 | AnOvercookedFork.quals | 2200 | 71 | 143 | 98-45 | 17% (c_aura2 1-5*) |
| 7 | pranayagra.finalbotfinaltwo | 2163 | 64 | 168 | 111-57 | 33% (c_aura2 3-6*) |
| 8 | pranayagra.finalbotfinal | 2157 | 47 | 333 | 236-97 | 40% (c_aura2 4-6*) |
| 9 | georgezhang02.FB_ZZZ | 2141 | 62 | 164 | 106-58 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2113 | 68 | 156 | 105-51 | 0% (c_def3 0-6*) |
| 11 | jmerle.camel_case_v30_final | 2090 | 46 | 322 | 226-96 | 33% (c_aura2 6-12*) |
| 12 | **us:c_aura2** | 2045 | 67 | 138 | 78-60 |  |
| 13 | **us:c_def3** | 2023 | 55 | 199 | 120-79 |  |
| 14 | CyrilSharma.finalBot | 1999 | 57 | 197 | 115-82 | 33% (c_def3 3-6*) |
| 15 | **us:c_flee3** | 1998 | 82 | 100 | 56-44 |  |
| 16 | **us:c_anc3** | 1993 | 61 | 163 | 88-75 |  |
| 17 | ethanlabelle.dev | 1988 | 56 | 188 | 115-73 | 58% (c_aura2 7-5*) |
| 18 | NotLLeon.v7 | 1941 | 42 | 327 | 191-136 | 60% (c_aura2 6-4*) |
| 19 | **us:c_nav5** | 1933 | 71 | 126 | 61-65 |  |
| 20 | georgezhang02.CB_tuning2 | 1922 | 43 | 305 | 179-126 | 70% (c_aura2 7-3*) |
| 21 | **us:c_nav6** | 1919 | 71 | 129 | 58-71 |  |
| 22 | **us:c_nav4** | 1900 | 52 | 221 | 108-113 |  |
| 23 | ethanlabelle.v19 | 1866 | 60 | 162 | 96-66 | 100% (c_aura2 3-0*) |
| 24 | britacatalin.FinalBot | 1862 | 42 | 322 | 172-150 | 80% (c_aura2 8-2*) |
| 25 | GabeG888.v8 | 1834 | 54 | 192 | 102-90 | 89% (c_def3 16-2*) |
| 26 | **us:c_swarm1** | 1827 | 48 | 271 | 128-143 |  |
| 27 | programjames.fourthbot | 1799 | 59 | 175 | 96-79 | 17% (c_nav4 1-5*) |
| 28 | VarunVejalla.ali8 | 1798 | 60 | 172 | 97-75 | 100% (c_def3 8-0*) |
| 29 | GabeG888.v8o1 | 1794 | 58 | 171 | 97-74 | 100% (c_nav5 3-0*) |
| 30 | VarunVejalla.karel | 1794 | 57 | 188 | 104-84 | 67% (c_nav4 6-3*) |
| 31 | DannyZhang686.pqual2 | 1785 | 55 | 199 | 107-92 | 83% (c_anc3 5-1*) |
| 32 | **us:c_line8a** | 1781 | 71 | 139 | 47-92 |  |
| 33 | **us:g_iter0** | 1780 | 48 | 456 | 230-226 |  |
| 34 | NicholasKelly15.gopher10 | 1776 | 63 | 154 | 88-66 | 100% (c_anc3 3-0*) |
| 35 | **us:c_line6** | 1747 | 88 | 100 | 32-68 |  |
| 36 | louishu17.wouisv8 | 1747 | 58 | 196 | 111-85 | 33% (c_nav4 2-4*) |
| 37 | **us:c_line7m** | 1735 | 88 | 100 | 31-69 |  |
| 38 | louishu17.louisv10 | 1731 | 60 | 172 | 95-77 | 100% (c_nav4 6-0*) |
| 39 | SampleProvider.SPAARK | 1725 | 58 | 176 | 99-77 | 33% (c_anc3 1-2*) |
| 40 | reeceyang.v5anaconda | 1718 | 43 | 323 | 143-180 | 80% (c_aura2 8-2*) |
| 41 | **us:c_line5** | 1700 | 90 | 100 | 28-72 |  |
| 42 | battlecode-archive.Sprint1 | 1694 | 45 | 299 | 126-173 | 100% (c_aura2 10-0*) |
| 43 | **us:c_line4** | 1662 | 93 | 100 | 25-75 |  |
| 44 | ipince.bobby | 1610 | 64 | 156 | 84-72 | 67% (c_swarm1 2-1*) |
| 45 | SteamBlizzard.newVnewME | 1608 | 54 | 207 | 106-101 | 80% (g_iter0 4-1*) |
| 46 | polyllc.poly | 1606 | 65 | 162 | 85-77 | 100% (g_iter0 2-0*) |
| 47 | legobridge.tacoplayer | 1605 | 57 | 200 | 108-92 | 85% (g_iter0 11-2*) |
| 48 | TheK098.qp1_7_sprint_1 | 1581 | 57 | 193 | 106-87 | 100% (c_swarm1 6-0*) |
| 49 | toyat522.bot5a | 1543 | 55 | 196 | 97-99 | 80% (g_iter0 4-1*) |
| 50 | elgoldie.head_v5 | 1540 | 53 | 199 | 101-98 | 100% (g_iter0 2-0*) |
| 51 | DukeBas._main | 1529 | 56 | 194 | 104-90 | 100% (g_iter0 2-0*) |
| 52 | ColtG5.rexv9 | 1525 | 53 | 212 | 109-103 | 100% (g_iter0 2-0*) |
| 53 | beaverbois.USQualifiers | 1479 | 56 | 193 | 98-95 | 50% (g_iter0 1-1*) |
| 54 | kevinli405.maggi3_2 | 1469 | 55 | 205 | 104-101 | 100% (g_iter0 2-0*) |
| 55 | Nawlej.PoonPoon | 1457 | 58 | 184 | 92-92 | 100% (g_iter0 2-0*) |
| 56 | BrysonJGalapon.friday | 1454 | 55 | 182 | 93-89 | 100% (g_iter0 2-0*) |
| 57 | nail-e.Barry | 1428 | 53 | 202 | 104-98 | 100% (g_iter0 2-0*) |
| 58 | yaonam.PoonPoonv4 | 1414 | 47 | 358 | 125-233 | 90% (c_aura2 9-1*) |
| 59 | aj-chau.attempt1 | 1411 | 57 | 190 | 99-91 | 100% (g_iter0 5-0*) |
| 60 | kevinli405.maggi3 | 1403 | 55 | 211 | 106-105 | 100% (g_iter0 5-0*) |
| 61 | prisms-cs-club.prisms10 | 1380 | 56 | 197 | 95-102 | 100% (g_iter0 2-0*) |
| 62 | mama4294.currentPlayer | 1352 | 53 | 210 | 105-105 | 100% (g_iter0 2-0*) |
| 63 | ipince.bobby_v2 | 1349 | 57 | 194 | 96-98 | 67% (c_swarm1 2-1*) |
| 64 | JfeMak.realplayer2 | 1278 | 57 | 180 | 89-91 | 100% (g_iter0 2-0*) |
| 65 | andrewgopher.gopherbot | 1275 | 51 | 230 | 109-121 | 100% (g_iter0 2-0*) |
| 66 | BrysonJGalapon.aloha | 1275 | 50 | 228 | 112-116 | 100% (c_swarm1 3-0*) |
| 67 | bewuwy.deathbot4 | 1265 | 49 | 250 | 116-134 | 100% (g_iter0 2-0*) |
| 68 | PSUtblock.sprint_four_player | 1240 | 57 | 202 | 103-99 | 100% (g_iter0 2-0*) |
| 69 | **us:examplefuncsplayer** | 1228 | 380 | 6 | 0-6 |  |
| 70 | SampleProvider.SPAARK_1_12_2023 | 1218 | 50 | 235 | 111-124 | 100% (c_swarm1 3-0*) |
| 71 | SDainard-PDX.Team_Player | 1200 | 53 | 209 | 100-109 | 100% (g_iter0 2-0*) |
| 72 | Juanbri02.matfisplayer1 | 1198 | 50 | 228 | 110-118 | 100% (g_iter0 5-0*) |
| 73 | Nawlej.PoonPoonv3 | 1178 | 49 | 241 | 111-130 | 100% (g_iter0 5-0*) |
| 74 | NolanChai.nolan_1 | 1175 | 50 | 232 | 110-122 | 100% (g_iter0 2-0*) |
| 75 | jyorkio.elicompbot | 1170 | 51 | 219 | 107-112 | 100% (g_iter0 2-0*) |
| 76 | andrewgopher.gopherbot1 | 1169 | 52 | 226 | 105-121 | 100% (g_iter0 2-0*) |
| 77 | vontell.regressiongames | 1106 | 46 | 263 | 127-136 | 100% (g_iter0 5-0*) |
| 78 | SteamBlizzard.Block | 1069 | 49 | 259 | 115-144 | 100% (g_iter0 5-0*) |
| 79 | legobridge.kushalplayer | 1064 | 59 | 185 | 82-103 | 100% (g_iter0 2-0*) |
| 80 | ax-95174.MPAction | 1053 | 52 | 217 | 98-119 | 100% (c_swarm1 3-0*) |
| 81 | Patela171.Battlecode2023_Robot | 1047 | 51 | 231 | 105-126 | 100% (g_iter0 2-0*) |
| 82 | JackLee9355.jackPlayer | 1045 | 53 | 233 | 102-131 | 100% (g_iter0 2-0*) |
| 83 | michael-tyl.hqrewrite | 1001 | 52 | 223 | 105-118 | 100% (g_iter0 2-0*) |
| 84 | nail-e.Dante | 985 | 50 | 239 | 113-126 | 100% (g_iter0 2-0*) |
| 85 | Chahat08.toph | 979 | 52 | 223 | 99-124 | 100% (g_iter0 2-0*) |
| 86 | mama4294.learningBot | 948 | 53 | 233 | 100-133 | 100% (g_iter0 2-0*) |
| 87 | anicolao.submission | 938 | 48 | 276 | 123-153 | 100% (g_iter0 2-0*) |
| 88 | team-remember-to-hydrate.sprint_1 | 876 | 51 | 247 | 101-146 | 100% (g_iter0 2-0*) |
| 89 | Vinceyou1.Player1 | 813 | 51 | 241 | 102-139 | 100% (g_iter0 2-0*) |
| 90 | addiesteward.elicompbot | 792 | 49 | 269 | 120-149 | 100% (g_iter0 5-0*) |
| 91 | michael-tyl.cc_v0_5_0_6 | 770 | 44 | 315 | 135-180 | 100% (g_iter0 2-0*) |
| 92 | toyat522.bot5 | 741 | 50 | 262 | 113-149 | 100% (g_iter0 2-0*) |
| 93 | Chahat08.lazarus | 739 | 49 | 260 | 115-145 | 100% (g_iter0 2-0*) |
| 94 | monmouth-college-cs.elicompbot | 734 | 49 | 272 | 116-156 | 100% (g_iter0 2-0*) |
| 95 | Swordman51.AdeptusAstartes2 | 734 | 47 | 266 | 113-153 | 100% (g_iter0 2-0*) |
| 96 | anicolao.jumbled | 611 | 49 | 284 | 120-164 | 100% (g_iter0 5-0*) |
| 97 | ShatterXD.SRNNbot | 601 | 54 | 238 | 101-137 | 100% (g_iter0 2-0*) |
| 98 | NotLLeon.player | 411 | 59 | 245 | 103-142 | 100% (g_iter0 2-0*) |
| 99 | CodeClash-ai.mysubmission | 395 | 57 | 267 | 114-153 | 100% (g_iter0 2-0*) |
| 100 | addiesteward.NDeClaw | 364 | 60 | 257 | 105-152 | 100% (g_iter0 5-0*) |
| 101 | Yooncw0223.lec3player | 80 | 71 | 247 | 37-210 | 100% (g_iter0 5-0*) |
| 102 | andrewkbank.First | -3 | 82 | 190 | 22-168 | 100% (g_iter0 2-0*) |
