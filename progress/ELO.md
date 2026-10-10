# Ladder

9813 games (2115 ours, 7698 between field bots on the ladder replica), 9714 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_def3 | 2048 +- 57 | 12 of 100 | 185 | 114-71 | 84.7% | 27.1% (vs 11) |
| c_anc3 | 2006 +- 61 | 14 of 100 | 163 | 88-75 | 82.9% | 25.0% (vs 12) |
| c_nav5 | 1946 +- 71 | 17 of 100 | 126 | 61-65 | 80.2% | 23.3% (vs 14) |
| c_nav6 | 1933 +- 71 | 19 of 100 | 129 | 58-71 | 79.5% | 23.9% (vs 15) |
| c_nav4 | 1914 +- 52 | 20 of 100 | 221 | 108-113 | 78.6% | 22.2% (vs 15) |
| c_swarm1 | 1840 +- 48 | 24 of 100 | 271 | 128-143 | 74.9% | 21.3% (vs 18) |
| g_iter0 | 1794 +- 48 | 30 of 100 | 456 | 230-226 | 72.4% | 24.2% (vs 23) |
| c_line8a | 1793 +- 71 | 32 of 100 | 139 | 47-92 | 72.3% | 25.1% (vs 24) |
| c_line6 | 1761 +- 88 | 34 of 100 | 100 | 32-68 | 70.5% | 23.4% (vs 25) |
| c_line7m | 1749 +- 88 | 36 of 100 | 100 | 31-69 | 69.9% | 23.4% (vs 26) |
| c_line5 | 1713 +- 90 | 40 of 100 | 100 | 28-72 | 67.8% | 23.3% (vs 29) |
| c_line4 | 1675 +- 93 | 41 of 100 | 100 | 25-75 | 65.5% | 20.1% (vs 29) |
| examplefuncsplayer | 1244 +- 380 | 66 of 100 | 6 | 0-6 | 38.5% | 12.0% (vs 53) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_def3), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2369 | 77 | 134 | 106-28 | 0% (g_iter0 0-36) |
| 2 | awesomelemonade.finalBot | 2316 | 68 | 235 | 197-38 | 20% (c_def3 2-8*) |
| 3 | maxwelljones14.MPWorking | 2305 | 77 | 118 | 84-34 | 0% (g_iter0 0-5*) |
| 4 | vrangr1.AFinalsBot | 2296 | 67 | 243 | 205-38 | 40% (c_def3 4-6*) |
| 5 | carlguo866.submit26_final | 2268 | 74 | 130 | 91-39 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2230 | 77 | 128 | 90-38 | 0% (c_anc3 0-3*) |
| 7 | pranayagra.finalbotfinaltwo | 2172 | 69 | 151 | 100-51 | 33% (c_anc3 2-4*) |
| 8 | pranayagra.finalbotfinal | 2172 | 51 | 295 | 215-80 | 40% (c_def3 4-6*) |
| 9 | georgezhang02.FB_ZZZ | 2152 | 67 | 149 | 99-50 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2141 | 73 | 145 | 102-43 | 0% (c_def3 0-6*) |
| 11 | jmerle.camel_case_v30_final | 2097 | 50 | 287 | 204-83 | 31% (c_def3 5-11*) |
| 12 | **us:c_def3** | 2048 | 57 | 185 | 114-71 |  |
| 13 | CyrilSharma.finalBot | 2009 | 58 | 194 | 113-81 | 33% (c_def3 3-6*) |
| 14 | **us:c_anc3** | 2006 | 61 | 163 | 88-75 |  |
| 15 | ethanlabelle.dev | 1987 | 60 | 161 | 99-62 | 67% (c_def3 6-3*) |
| 16 | NotLLeon.v7 | 1953 | 44 | 296 | 175-121 | 67% (c_def3 18-9*) |
| 17 | **us:c_nav5** | 1946 | 71 | 126 | 61-65 |  |
| 18 | georgezhang02.CB_tuning2 | 1933 | 46 | 271 | 163-108 | 60% (c_def3 6-4*) |
| 19 | **us:c_nav6** | 1933 | 71 | 129 | 58-71 |  |
| 20 | **us:c_nav4** | 1914 | 52 | 221 | 108-113 |  |
| 21 | britacatalin.FinalBot | 1874 | 45 | 284 | 157-127 | 70% (c_def3 19-8*) |
| 22 | ethanlabelle.v19 | 1866 | 65 | 141 | 84-57 | 100% (c_nav5 3-0*) |
| 23 | GabeG888.v8 | 1845 | 57 | 175 | 93-82 | 87% (c_def3 13-2*) |
| 24 | **us:c_swarm1** | 1840 | 48 | 271 | 128-143 |  |
| 25 | GabeG888.v8o1 | 1828 | 64 | 148 | 90-58 | 100% (c_nav5 3-0*) |
| 26 | programjames.fourthbot | 1817 | 64 | 157 | 89-68 | 17% (c_nav4 1-5*) |
| 27 | DannyZhang686.pqual2 | 1812 | 59 | 181 | 99-82 | 83% (c_anc3 5-1*) |
| 28 | VarunVejalla.ali8 | 1805 | 64 | 155 | 89-66 | 100% (c_def3 6-0*) |
| 29 | VarunVejalla.karel | 1802 | 59 | 176 | 96-80 | 67% (c_nav4 6-3*) |
| 30 | **us:g_iter0** | 1794 | 48 | 456 | 230-226 |  |
| 31 | NicholasKelly15.gopher10 | 1793 | 66 | 142 | 80-62 | 100% (c_anc3 3-0*) |
| 32 | **us:c_line8a** | 1793 | 71 | 139 | 47-92 |  |
| 33 | louishu17.louisv10 | 1763 | 64 | 157 | 91-66 | 100% (c_nav4 6-0*) |
| 34 | **us:c_line6** | 1761 | 88 | 100 | 32-68 |  |
| 35 | louishu17.wouisv8 | 1749 | 61 | 185 | 102-83 | 33% (c_nav4 2-4*) |
| 36 | **us:c_line7m** | 1749 | 88 | 100 | 31-69 |  |
| 37 | SampleProvider.SPAARK | 1729 | 61 | 162 | 90-72 | 33% (c_anc3 1-2*) |
| 38 | reeceyang.v5anaconda | 1728 | 45 | 291 | 132-159 | 90% (c_def3 9-1*) |
| 39 | battlecode-archive.Sprint1 | 1718 | 47 | 265 | 120-145 | 100% (c_def3 10-0*) |
| 40 | **us:c_line5** | 1713 | 90 | 100 | 28-72 |  |
| 41 | **us:c_line4** | 1675 | 93 | 100 | 25-75 |  |
| 42 | ipince.bobby | 1628 | 67 | 142 | 77-65 | 67% (c_swarm1 2-1*) |
| 43 | SteamBlizzard.newVnewME | 1617 | 56 | 195 | 100-95 | 80% (g_iter0 4-1*) |
| 44 | legobridge.tacoplayer | 1616 | 61 | 182 | 99-83 | 85% (g_iter0 11-2*) |
| 45 | polyllc.poly | 1616 | 72 | 142 | 75-67 | 100% (g_iter0 2-0*) |
| 46 | TheK098.qp1_7_sprint_1 | 1586 | 60 | 176 | 95-81 | 100% (c_swarm1 6-0*) |
| 47 | toyat522.bot5a | 1575 | 61 | 167 | 87-80 | 80% (g_iter0 4-1*) |
| 48 | elgoldie.head_v5 | 1557 | 58 | 170 | 85-85 | 100% (g_iter0 2-0*) |
| 49 | DukeBas._main | 1543 | 62 | 170 | 91-79 | 100% (g_iter0 2-0*) |
| 50 | ColtG5.rexv9 | 1537 | 57 | 188 | 96-92 | 100% (g_iter0 2-0*) |
| 51 | beaverbois.USQualifiers | 1495 | 59 | 173 | 90-83 | 50% (g_iter0 1-1*) |
| 52 | kevinli405.maggi3_2 | 1482 | 59 | 184 | 94-90 | 100% (g_iter0 2-0*) |
| 53 | BrysonJGalapon.friday | 1478 | 58 | 168 | 87-81 | 100% (g_iter0 2-0*) |
| 54 | Nawlej.PoonPoon | 1461 | 65 | 157 | 79-78 | 100% (g_iter0 2-0*) |
| 55 | nail-e.Barry | 1442 | 58 | 172 | 88-84 | 100% (g_iter0 2-0*) |
| 56 | yaonam.PoonPoonv4 | 1428 | 50 | 316 | 114-202 | 90% (c_def3 9-1*) |
| 57 | aj-chau.attempt1 | 1425 | 60 | 173 | 91-82 | 100% (g_iter0 5-0*) |
| 58 | kevinli405.maggi3 | 1418 | 60 | 182 | 92-90 | 100% (g_iter0 5-0*) |
| 59 | prisms-cs-club.prisms10 | 1389 | 59 | 182 | 85-97 | 100% (g_iter0 2-0*) |
| 60 | ipince.bobby_v2 | 1358 | 59 | 185 | 92-93 | 67% (c_swarm1 2-1*) |
| 61 | mama4294.currentPlayer | 1356 | 58 | 185 | 92-93 | 100% (g_iter0 2-0*) |
| 62 | andrewgopher.gopherbot | 1303 | 54 | 209 | 101-108 | 100% (g_iter0 2-0*) |
| 63 | BrysonJGalapon.aloha | 1294 | 54 | 199 | 97-102 | 100% (c_swarm1 3-0*) |
| 64 | JfeMak.realplayer2 | 1284 | 60 | 165 | 81-84 | 100% (g_iter0 2-0*) |
| 65 | bewuwy.deathbot4 | 1279 | 51 | 233 | 107-126 | 100% (g_iter0 2-0*) |
| 66 | **us:examplefuncsplayer** | 1244 | 380 | 6 | 0-6 |  |
| 67 | PSUtblock.sprint_four_player | 1242 | 61 | 178 | 91-87 | 100% (g_iter0 2-0*) |
| 68 | SampleProvider.SPAARK_1_12_2023 | 1240 | 52 | 217 | 103-114 | 100% (c_swarm1 3-0*) |
| 69 | SDainard-PDX.Team_Player | 1211 | 60 | 173 | 80-93 | 100% (g_iter0 2-0*) |
| 70 | NolanChai.nolan_1 | 1200 | 54 | 202 | 94-108 | 100% (g_iter0 2-0*) |
| 71 | Juanbri02.matfisplayer1 | 1198 | 54 | 201 | 93-108 | 100% (g_iter0 5-0*) |
| 72 | Nawlej.PoonPoonv3 | 1188 | 52 | 217 | 99-118 | 100% (g_iter0 5-0*) |
| 73 | jyorkio.elicompbot | 1179 | 52 | 207 | 101-106 | 100% (g_iter0 2-0*) |
| 74 | andrewgopher.gopherbot1 | 1176 | 56 | 202 | 93-109 | 100% (g_iter0 2-0*) |
| 75 | vontell.regressiongames | 1120 | 49 | 233 | 110-123 | 100% (g_iter0 5-0*) |
| 76 | SteamBlizzard.Block | 1083 | 51 | 237 | 101-136 | 100% (g_iter0 5-0*) |
| 77 | JackLee9355.jackPlayer | 1081 | 56 | 209 | 90-119 | 100% (g_iter0 2-0*) |
| 78 | ax-95174.MPAction | 1074 | 54 | 196 | 87-109 | 100% (c_swarm1 3-0*) |
| 79 | legobridge.kushalplayer | 1066 | 65 | 160 | 69-91 | 100% (g_iter0 2-0*) |
| 80 | Patela171.Battlecode2023_Robot | 1051 | 54 | 208 | 92-116 | 100% (g_iter0 2-0*) |
| 81 | nail-e.Dante | 1012 | 54 | 212 | 102-110 | 100% (g_iter0 2-0*) |
| 82 | michael-tyl.hqrewrite | 1011 | 54 | 206 | 92-114 | 100% (g_iter0 2-0*) |
| 83 | Chahat08.toph | 999 | 55 | 196 | 85-111 | 100% (g_iter0 2-0*) |
| 84 | anicolao.submission | 977 | 50 | 258 | 118-140 | 100% (g_iter0 2-0*) |
| 85 | mama4294.learningBot | 965 | 56 | 209 | 88-121 | 100% (g_iter0 2-0*) |
| 86 | team-remember-to-hydrate.sprint_1 | 925 | 53 | 224 | 95-129 | 100% (g_iter0 2-0*) |
| 87 | Vinceyou1.Player1 | 828 | 55 | 211 | 87-124 | 100% (g_iter0 2-0*) |
| 88 | addiesteward.elicompbot | 812 | 50 | 252 | 111-141 | 100% (g_iter0 5-0*) |
| 89 | michael-tyl.cc_v0_5_0_6 | 804 | 47 | 280 | 118-162 | 100% (g_iter0 2-0*) |
| 90 | Swordman51.AdeptusAstartes2 | 774 | 50 | 237 | 101-136 | 100% (g_iter0 2-0*) |
| 91 | monmouth-college-cs.elicompbot | 767 | 52 | 246 | 105-141 | 100% (g_iter0 2-0*) |
| 92 | Chahat08.lazarus | 759 | 54 | 218 | 93-125 | 100% (g_iter0 2-0*) |
| 93 | toyat522.bot5 | 753 | 54 | 230 | 94-136 | 100% (g_iter0 2-0*) |
| 94 | anicolao.jumbled | 654 | 52 | 256 | 108-148 | 100% (g_iter0 5-0*) |
| 95 | ShatterXD.SRNNbot | 632 | 57 | 210 | 84-126 | 100% (g_iter0 2-0*) |
| 96 | NotLLeon.player | 450 | 61 | 227 | 92-135 | 100% (g_iter0 2-0*) |
| 97 | CodeClash-ai.mysubmission | 449 | 61 | 232 | 95-137 | 100% (g_iter0 2-0*) |
| 98 | addiesteward.NDeClaw | 414 | 64 | 225 | 90-135 | 100% (g_iter0 5-0*) |
| 99 | Yooncw0223.lec3player | 135 | 75 | 220 | 32-188 | 100% (g_iter0 5-0*) |
| 100 | andrewkbank.First | 65 | 84 | 172 | 21-151 | 100% (g_iter0 2-0*) |
