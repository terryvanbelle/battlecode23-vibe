# Ladder

9489 games (2082 ours, 7407 between field bots on the ladder replica), 9395 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_def3 | 2061 +- 65 | 12 of 100 | 152 | 98-54 | 85.3% | 29.1% (vs 11) |
| c_anc3 | 2005 +- 61 | 13 of 100 | 163 | 88-75 | 82.9% | 23.2% (vs 11) |
| c_nav5 | 1945 +- 71 | 17 of 100 | 126 | 61-65 | 80.2% | 23.4% (vs 14) |
| c_nav6 | 1932 +- 71 | 19 of 100 | 129 | 58-71 | 79.6% | 24.0% (vs 15) |
| c_nav4 | 1911 +- 52 | 20 of 100 | 221 | 108-113 | 78.6% | 22.1% (vs 15) |
| c_swarm1 | 1838 +- 48 | 24 of 100 | 271 | 128-143 | 74.8% | 21.3% (vs 18) |
| c_line8a | 1793 +- 71 | 31 of 100 | 139 | 47-92 | 72.4% | 25.4% (vs 24) |
| g_iter0 | 1793 +- 48 | 32 of 100 | 456 | 230-226 | 72.4% | 25.4% (vs 24) |
| c_line6 | 1761 +- 88 | 33 of 100 | 100 | 32-68 | 70.6% | 22.5% (vs 24) |
| c_line7m | 1749 +- 88 | 36 of 100 | 100 | 31-69 | 69.9% | 23.7% (vs 26) |
| c_line5 | 1713 +- 90 | 40 of 100 | 100 | 28-72 | 67.8% | 23.4% (vs 29) |
| c_line4 | 1676 +- 93 | 41 of 100 | 100 | 25-75 | 65.6% | 20.2% (vs 29) |
| examplefuncsplayer | 1243 +- 380 | 66 of 100 | 6 | 0-6 | 38.4% | 12.0% (vs 53) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_def3), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2368 | 77 | 134 | 106-28 | 0% (g_iter0 0-36) |
| 2 | awesomelemonade.finalBot | 2315 | 68 | 235 | 197-38 | 20% (c_def3 2-8*) |
| 3 | maxwelljones14.MPWorking | 2312 | 80 | 113 | 82-31 | 0% (g_iter0 0-5*) |
| 4 | vrangr1.AFinalsBot | 2288 | 67 | 241 | 203-38 | 40% (c_def3 4-6*) |
| 5 | carlguo866.submit26_final | 2262 | 76 | 127 | 89-38 | 67% (c_nav4 2-1*) |
| 6 | AnOvercookedFork.quals | 2233 | 80 | 122 | 87-35 | 0% (c_anc3 0-3*) |
| 7 | pranayagra.finalbotfinaltwo | 2173 | 69 | 148 | 98-50 | 33% (c_anc3 2-4*) |
| 8 | pranayagra.finalbotfinal | 2170 | 52 | 292 | 214-78 | 40% (c_def3 4-6*) |
| 9 | georgezhang02.FB_ZZZ | 2149 | 67 | 146 | 97-49 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2111 | 76 | 136 | 93-43 | 33% (c_anc3 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2094 | 51 | 275 | 197-78 | 30% (c_def3 3-7*) |
| 12 | **us:c_def3** | 2061 | 65 | 152 | 98-54 |  |
| 13 | **us:c_anc3** | 2005 | 61 | 163 | 88-75 |  |
| 14 | CyrilSharma.finalBot | 2002 | 62 | 173 | 103-70 | 42% (c_anc3 5-7*) |
| 15 | ethanlabelle.dev | 1994 | 61 | 158 | 99-59 | 50% (c_def3 3-3*) |
| 16 | NotLLeon.v7 | 1959 | 45 | 290 | 174-116 | 62% (c_def3 15-9*) |
| 17 | **us:c_nav5** | 1945 | 71 | 126 | 61-65 |  |
| 18 | georgezhang02.CB_tuning2 | 1937 | 47 | 268 | 162-106 | 60% (c_def3 6-4*) |
| 19 | **us:c_nav6** | 1932 | 71 | 129 | 58-71 |  |
| 20 | **us:c_nav4** | 1911 | 52 | 221 | 108-113 |  |
| 21 | britacatalin.FinalBot | 1873 | 45 | 281 | 156-125 | 71% (c_def3 17-7*) |
| 22 | ethanlabelle.v19 | 1860 | 66 | 138 | 82-56 | 100% (c_nav5 3-0*) |
| 23 | GabeG888.v8 | 1844 | 57 | 172 | 92-80 | 87% (c_def3 13-2*) |
| 24 | **us:c_swarm1** | 1838 | 48 | 271 | 128-143 |  |
| 25 | GabeG888.v8o1 | 1820 | 64 | 145 | 87-58 | 100% (c_nav5 3-0*) |
| 26 | programjames.fourthbot | 1804 | 65 | 152 | 85-67 | 17% (c_nav4 1-5*) |
| 27 | DannyZhang686.pqual2 | 1804 | 59 | 178 | 96-82 | 83% (c_anc3 5-1*) |
| 28 | VarunVejalla.ali8 | 1802 | 65 | 149 | 88-61 | 100% (c_def3 3-0*) |
| 29 | VarunVejalla.karel | 1802 | 60 | 170 | 93-77 | 67% (c_nav4 6-3*) |
| 30 | NicholasKelly15.gopher10 | 1798 | 69 | 133 | 76-57 | 100% (c_anc3 3-0*) |
| 31 | **us:c_line8a** | 1793 | 71 | 139 | 47-92 |  |
| 32 | **us:g_iter0** | 1793 | 48 | 456 | 230-226 |  |
| 33 | **us:c_line6** | 1761 | 88 | 100 | 32-68 |  |
| 34 | louishu17.louisv10 | 1756 | 65 | 151 | 86-65 | 100% (c_nav4 6-0*) |
| 35 | louishu17.wouisv8 | 1754 | 63 | 173 | 95-78 | 33% (c_nav4 2-4*) |
| 36 | **us:c_line7m** | 1749 | 88 | 100 | 31-69 |  |
| 37 | SampleProvider.SPAARK | 1744 | 63 | 154 | 89-65 | 33% (c_anc3 1-2*) |
| 38 | reeceyang.v5anaconda | 1725 | 46 | 285 | 128-157 | 90% (c_def3 9-1*) |
| 39 | battlecode-archive.Sprint1 | 1717 | 47 | 262 | 118-144 | 100% (c_def3 10-0*) |
| 40 | **us:c_line5** | 1713 | 90 | 100 | 28-72 |  |
| 41 | **us:c_line4** | 1676 | 93 | 100 | 25-75 |  |
| 42 | ipince.bobby | 1627 | 67 | 142 | 77-65 | 67% (c_swarm1 2-1*) |
| 43 | polyllc.poly | 1611 | 73 | 139 | 73-66 | 100% (g_iter0 2-0*) |
| 44 | legobridge.tacoplayer | 1610 | 62 | 176 | 94-82 | 85% (g_iter0 11-2*) |
| 45 | SteamBlizzard.newVnewME | 1610 | 59 | 180 | 94-86 | 80% (g_iter0 4-1*) |
| 46 | TheK098.qp1_7_sprint_1 | 1585 | 60 | 176 | 95-81 | 100% (c_swarm1 6-0*) |
| 47 | toyat522.bot5a | 1578 | 61 | 164 | 86-78 | 80% (g_iter0 4-1*) |
| 48 | elgoldie.head_v5 | 1569 | 60 | 158 | 80-78 | 100% (g_iter0 2-0*) |
| 49 | DukeBas._main | 1542 | 62 | 167 | 89-78 | 100% (g_iter0 2-0*) |
| 50 | ColtG5.rexv9 | 1531 | 58 | 179 | 88-91 | 100% (g_iter0 2-0*) |
| 51 | beaverbois.USQualifiers | 1487 | 61 | 161 | 86-75 | 50% (g_iter0 1-1*) |
| 52 | kevinli405.maggi3_2 | 1481 | 61 | 178 | 91-87 | 100% (g_iter0 2-0*) |
| 53 | BrysonJGalapon.friday | 1478 | 58 | 168 | 87-81 | 100% (g_iter0 2-0*) |
| 54 | Nawlej.PoonPoon | 1452 | 66 | 151 | 74-77 | 100% (g_iter0 2-0*) |
| 55 | nail-e.Barry | 1449 | 60 | 160 | 82-78 | 100% (g_iter0 2-0*) |
| 56 | yaonam.PoonPoonv4 | 1429 | 51 | 310 | 112-198 | 90% (c_def3 9-1*) |
| 57 | kevinli405.maggi3 | 1420 | 63 | 173 | 88-85 | 100% (g_iter0 5-0*) |
| 58 | aj-chau.attempt1 | 1418 | 64 | 158 | 82-76 | 100% (g_iter0 5-0*) |
| 59 | prisms-cs-club.prisms10 | 1403 | 61 | 170 | 82-88 | 100% (g_iter0 2-0*) |
| 60 | mama4294.currentPlayer | 1361 | 59 | 179 | 90-89 | 100% (g_iter0 2-0*) |
| 61 | ipince.bobby_v2 | 1344 | 63 | 167 | 82-85 | 67% (c_swarm1 2-1*) |
| 62 | andrewgopher.gopherbot | 1305 | 55 | 203 | 98-105 | 100% (g_iter0 2-0*) |
| 63 | BrysonJGalapon.aloha | 1304 | 56 | 187 | 94-93 | 100% (c_swarm1 3-0*) |
| 64 | JfeMak.realplayer2 | 1289 | 61 | 162 | 80-82 | 100% (g_iter0 2-0*) |
| 65 | bewuwy.deathbot4 | 1282 | 51 | 230 | 106-124 | 100% (g_iter0 2-0*) |
| 66 | **us:examplefuncsplayer** | 1243 | 380 | 6 | 0-6 |  |
| 67 | SampleProvider.SPAARK_1_12_2023 | 1240 | 54 | 208 | 97-111 | 100% (c_swarm1 3-0*) |
| 68 | PSUtblock.sprint_four_player | 1237 | 64 | 166 | 83-83 | 100% (g_iter0 2-0*) |
| 69 | SDainard-PDX.Team_Player | 1221 | 60 | 170 | 80-90 | 100% (g_iter0 2-0*) |
| 70 | NolanChai.nolan_1 | 1209 | 57 | 184 | 87-97 | 100% (g_iter0 2-0*) |
| 71 | Juanbri02.matfisplayer1 | 1203 | 55 | 198 | 92-106 | 100% (g_iter0 5-0*) |
| 72 | Nawlej.PoonPoonv3 | 1199 | 54 | 205 | 94-111 | 100% (g_iter0 5-0*) |
| 73 | jyorkio.elicompbot | 1171 | 55 | 192 | 91-101 | 100% (g_iter0 2-0*) |
| 74 | andrewgopher.gopherbot1 | 1168 | 59 | 187 | 84-103 | 100% (g_iter0 2-0*) |
| 75 | vontell.regressiongames | 1130 | 49 | 227 | 109-118 | 100% (g_iter0 5-0*) |
| 76 | SteamBlizzard.Block | 1086 | 52 | 231 | 99-132 | 100% (g_iter0 5-0*) |
| 77 | JackLee9355.jackPlayer | 1081 | 56 | 206 | 87-119 | 100% (g_iter0 2-0*) |
| 78 | ax-95174.MPAction | 1081 | 55 | 193 | 86-107 | 100% (c_swarm1 3-0*) |
| 79 | legobridge.kushalplayer | 1067 | 65 | 160 | 69-91 | 100% (g_iter0 2-0*) |
| 80 | Patela171.Battlecode2023_Robot | 1054 | 55 | 202 | 90-112 | 100% (g_iter0 2-0*) |
| 81 | michael-tyl.hqrewrite | 1019 | 55 | 200 | 89-111 | 100% (g_iter0 2-0*) |
| 82 | nail-e.Dante | 1010 | 54 | 209 | 99-110 | 100% (g_iter0 2-0*) |
| 83 | Chahat08.toph | 1004 | 56 | 193 | 84-109 | 100% (g_iter0 2-0*) |
| 84 | anicolao.submission | 979 | 51 | 243 | 108-135 | 100% (g_iter0 2-0*) |
| 85 | mama4294.learningBot | 965 | 59 | 194 | 80-114 | 100% (g_iter0 2-0*) |
| 86 | team-remember-to-hydrate.sprint_1 | 914 | 55 | 212 | 87-125 | 100% (g_iter0 2-0*) |
| 87 | Vinceyou1.Player1 | 833 | 58 | 191 | 79-112 | 100% (g_iter0 2-0*) |
| 88 | addiesteward.elicompbot | 812 | 52 | 240 | 105-135 | 100% (g_iter0 5-0*) |
| 89 | michael-tyl.cc_v0_5_0_6 | 810 | 48 | 269 | 113-156 | 100% (g_iter0 2-0*) |
| 90 | Swordman51.AdeptusAstartes2 | 779 | 52 | 226 | 96-130 | 100% (g_iter0 2-0*) |
| 91 | monmouth-college-cs.elicompbot | 773 | 53 | 238 | 101-137 | 100% (g_iter0 2-0*) |
| 92 | toyat522.bot5 | 769 | 55 | 224 | 94-130 | 100% (g_iter0 2-0*) |
| 93 | Chahat08.lazarus | 768 | 54 | 216 | 93-123 | 100% (g_iter0 2-0*) |
| 94 | anicolao.jumbled | 659 | 52 | 254 | 107-147 | 100% (g_iter0 5-0*) |
| 95 | ShatterXD.SRNNbot | 635 | 58 | 207 | 81-126 | 100% (g_iter0 2-0*) |
| 96 | NotLLeon.player | 461 | 61 | 221 | 89-132 | 100% (g_iter0 2-0*) |
| 97 | CodeClash-ai.mysubmission | 456 | 61 | 229 | 92-137 | 100% (g_iter0 2-0*) |
| 98 | addiesteward.NDeClaw | 425 | 64 | 219 | 85-134 | 100% (g_iter0 5-0*) |
| 99 | Yooncw0223.lec3player | 148 | 79 | 208 | 29-179 | 100% (g_iter0 5-0*) |
| 100 | andrewkbank.First | 82 | 86 | 166 | 20-146 | 100% (g_iter0 2-0*) |
