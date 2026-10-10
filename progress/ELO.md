# Ladder

11780 games (2417 ours, 6 of the stock examplefuncsplayer, 9357 between field bots on the ladder replica), 11528 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 102 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_def3 | 2098 +- 65 | 12 of 101 | 194 | 117-77 | 84.8% | 25.3% (vs 11) |
| c_aura2 | 2089 +- 66 | 13 of 101 | 191 | 107-84 | 84.5% | 24.4% (vs 11) |
| c_flee3 | 2075 +- 90 | 15 of 101 | 100 | 56-44 | 84.0% | 25.2% (vs 12) |
| c_anc3 | 2068 +- 71 | 16 of 101 | 161 | 87-74 | 83.7% | 24.5% (vs 12) |
| c_nav5 | 2007 +- 79 | 19 of 101 | 126 | 61-65 | 81.2% | 22.7% (vs 14) |
| c_nav6 | 1995 +- 79 | 20 of 101 | 129 | 58-71 | 80.7% | 21.6% (vs 14) |
| c_nav4 | 1966 +- 61 | 22 of 101 | 221 | 108-113 | 79.5% | 20.9% (vs 15) |
| c_swarm1 | 1888 +- 57 | 26 of 101 | 268 | 126-142 | 75.9% | 20.1% (vs 18) |
| c_line8a | 1846 +- 79 | 30 of 101 | 139 | 47-92 | 73.9% | 21.3% (vs 21) |
| g_iter0 | 1830 +- 56 | 33 of 101 | 455 | 230-225 | 73.2% | 22.6% (vs 23) |
| c_line6 | 1812 +- 95 | 34 of 101 | 100 | 32-68 | 72.3% | 21.1% (vs 23) |
| c_line7m | 1800 +- 95 | 36 of 101 | 100 | 31-69 | 71.7% | 21.3% (vs 24) |
| c_line5 | 1762 +- 98 | 41 of 101 | 100 | 28-72 | 69.8% | 22.5% (vs 28) |
| c_line4 | 1721 +- 101 | 43 of 101 | 100 | 25-75 | 67.7% | 20.2% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_aura2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2425 | 82 | 157 | 117-40 | 0% (g_iter0 0-35) |
| 2 | awesomelemonade.finalBot | 2403 | 74 | 278 | 230-48 | 20% (c_aura2 2-8*) |
| 3 | maxwelljones14.MPWorking | 2391 | 83 | 143 | 100-43 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2338 | 79 | 153 | 102-51 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2335 | 68 | 290 | 231-59 | 40% (c_aura2 4-6*) |
| 6 | AnOvercookedFork.quals | 2288 | 79 | 152 | 102-50 | 17% (c_aura2 1-5*) |
| 7 | pranayagra.finalbotfinaltwo | 2250 | 74 | 177 | 117-60 | 33% (c_aura2 3-6*) |
| 8 | georgezhang02.FB_ZZZ | 2235 | 72 | 174 | 114-60 | 0% (c_anc3 0-3*) |
| 9 | pranayagra.finalbotfinal | 2226 | 58 | 345 | 240-105 | 40% (c_aura2 4-6*) |
| 10 | battlecode-archive.sprintBot | 2197 | 74 | 170 | 113-57 | 33% (c_aura2 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2167 | 56 | 334 | 232-102 | 29% (c_aura2 6-15*) |
| 12 | **us:c_def3** | 2098 | 65 | 194 | 117-77 |  |
| 13 | **us:c_aura2** | 2089 | 66 | 191 | 107-84 |  |
| 14 | CyrilSharma.finalBot | 2080 | 64 | 216 | 125-91 | 33% (c_aura2 2-4*) |
| 15 | **us:c_flee3** | 2075 | 90 | 100 | 56-44 |  |
| 16 | **us:c_anc3** | 2068 | 71 | 161 | 87-74 |  |
| 17 | ethanlabelle.dev | 2063 | 63 | 203 | 124-79 | 50% (c_aura2 9-9*) |
| 18 | NotLLeon.v7 | 2013 | 52 | 337 | 199-138 | 60% (c_aura2 6-4*) |
| 19 | **us:c_nav5** | 2007 | 79 | 126 | 61-65 |  |
| 20 | **us:c_nav6** | 1995 | 79 | 129 | 58-71 |  |
| 21 | georgezhang02.CB_tuning2 | 1994 | 53 | 320 | 188-132 | 63% (c_aura2 12-7*) |
| 22 | **us:c_nav4** | 1966 | 61 | 221 | 108-113 |  |
| 23 | ethanlabelle.v19 | 1929 | 64 | 189 | 105-84 | 67% (c_aura2 10-5*) |
| 24 | britacatalin.FinalBot | 1921 | 51 | 332 | 175-157 | 80% (c_aura2 12-3*) |
| 25 | GabeG888.v8 | 1896 | 60 | 208 | 111-97 | 89% (c_def3 16-2*) |
| 26 | **us:c_swarm1** | 1888 | 57 | 268 | 126-142 |  |
| 27 | programjames.fourthbot | 1866 | 64 | 192 | 105-87 | 100% (c_aura2 3-0*) |
| 28 | VarunVejalla.ali8 | 1860 | 65 | 187 | 107-80 | 100% (c_def3 8-0*) |
| 29 | GabeG888.v8o1 | 1859 | 63 | 189 | 109-80 | 100% (c_nav5 3-0*) |
| 30 | **us:c_line8a** | 1846 | 79 | 139 | 47-92 |  |
| 31 | VarunVejalla.karel | 1843 | 62 | 200 | 109-91 | 67% (c_nav4 6-3*) |
| 32 | DannyZhang686.pqual2 | 1836 | 61 | 211 | 114-97 | 83% (c_anc3 5-1*) |
| 33 | **us:g_iter0** | 1830 | 56 | 455 | 230-225 |  |
| 34 | **us:c_line6** | 1812 | 95 | 100 | 32-68 |  |
| 35 | NicholasKelly15.gopher10 | 1805 | 67 | 169 | 94-75 | 100% (c_anc3 3-0*) |
| 36 | **us:c_line7m** | 1800 | 95 | 100 | 31-69 |  |
| 37 | louishu17.wouisv8 | 1787 | 63 | 210 | 113-97 | 83% (c_aura2 5-1*) |
| 38 | louishu17.louisv10 | 1784 | 63 | 192 | 106-86 | 100% (c_nav4 6-0*) |
| 39 | SampleProvider.SPAARK | 1777 | 63 | 191 | 108-83 | 33% (c_anc3 1-2*) |
| 40 | reeceyang.v5anaconda | 1773 | 51 | 334 | 148-186 | 80% (c_aura2 8-2*) |
| 41 | **us:c_line5** | 1762 | 98 | 100 | 28-72 |  |
| 42 | battlecode-archive.Sprint1 | 1745 | 52 | 316 | 136-180 | 100% (c_aura2 10-0*) |
| 43 | **us:c_line4** | 1721 | 101 | 100 | 25-75 |  |
| 44 | ipince.bobby | 1673 | 67 | 170 | 97-73 | 67% (c_swarm1 2-1*) |
| 45 | legobridge.tacoplayer | 1625 | 61 | 214 | 116-98 | 85% (g_iter0 11-2*) |
| 46 | SteamBlizzard.newVnewME | 1625 | 59 | 219 | 108-111 | 80% (g_iter0 4-1*) |
| 47 | TheK098.qp1_7_sprint_1 | 1604 | 61 | 206 | 115-91 | 100% (c_swarm1 6-0*) |
| 48 | polyllc.poly | 1595 | 68 | 176 | 87-89 | 100% (g_iter0 2-0*) |
| 49 | toyat522.bot5a | 1550 | 59 | 215 | 108-107 | 80% (g_iter0 4-1*) |
| 50 | elgoldie.head_v5 | 1534 | 57 | 219 | 107-112 | 100% (g_iter0 2-0*) |
| 51 | DukeBas._main | 1522 | 60 | 209 | 111-98 | 100% (g_iter0 2-0*) |
| 52 | ColtG5.rexv9 | 1511 | 57 | 227 | 114-113 | 100% (g_iter0 2-0*) |
| 53 | beaverbois.USQualifiers | 1481 | 59 | 210 | 111-99 | 50% (g_iter0 1-1*) |
| 54 | kevinli405.maggi3_2 | 1460 | 59 | 225 | 113-112 | 100% (g_iter0 2-0*) |
| 55 | Nawlej.PoonPoon | 1436 | 61 | 204 | 103-101 | 100% (g_iter0 2-0*) |
| 56 | BrysonJGalapon.friday | 1431 | 60 | 193 | 99-94 | 100% (g_iter0 2-0*) |
| 57 | nail-e.Barry | 1405 | 57 | 219 | 112-107 | 100% (g_iter0 2-0*) |
| 58 | yaonam.PoonPoonv4 | 1404 | 52 | 375 | 133-242 | 90% (c_aura2 9-1*) |
| 59 | kevinli405.maggi3 | 1390 | 58 | 231 | 120-111 | 100% (g_iter0 5-0*) |
| 60 | aj-chau.attempt1 | 1379 | 62 | 198 | 101-97 | 100% (g_iter0 5-0*) |
| 61 | prisms-cs-club.prisms10 | 1332 | 60 | 210 | 97-113 | 100% (g_iter0 2-0*) |
| 62 | ipince.bobby_v2 | 1310 | 61 | 211 | 103-108 | 67% (c_swarm1 2-1*) |
| 63 | mama4294.currentPlayer | 1307 | 58 | 226 | 110-116 | 100% (g_iter0 2-0*) |
| 64 | andrewgopher.gopherbot | 1224 | 57 | 250 | 121-129 | 100% (g_iter0 2-0*) |
| 65 | bewuwy.deathbot4 | 1223 | 54 | 275 | 131-144 | 100% (g_iter0 2-0*) |
| 66 | JfeMak.realplayer2 | 1222 | 60 | 205 | 102-103 | 100% (g_iter0 2-0*) |
| 67 | BrysonJGalapon.aloha | 1219 | 55 | 248 | 123-125 | 100% (c_swarm1 3-0*) |
| 68 | PSUtblock.sprint_four_player | 1173 | 62 | 215 | 106-109 | 100% (g_iter0 2-0*) |
| 69 | SampleProvider.SPAARK_1_12_2023 | 1156 | 56 | 258 | 125-133 | 100% (c_swarm1 3-0*) |
| 70 | Nawlej.PoonPoonv3 | 1135 | 56 | 260 | 127-133 | 100% (g_iter0 5-0*) |
| 71 | Juanbri02.matfisplayer1 | 1126 | 57 | 247 | 118-129 | 100% (g_iter0 5-0*) |
| 72 | NolanChai.nolan_1 | 1126 | 56 | 256 | 124-132 | 100% (g_iter0 2-0*) |
| 73 | SDainard-PDX.Team_Player | 1118 | 59 | 233 | 110-123 | 100% (g_iter0 2-0*) |
| 74 | andrewgopher.gopherbot1 | 1105 | 58 | 248 | 115-133 | 100% (g_iter0 2-0*) |
| 75 | jyorkio.elicompbot | 1087 | 57 | 240 | 113-127 | 100% (g_iter0 2-0*) |
| 76 | vontell.regressiongames | 1034 | 56 | 271 | 131-140 | 100% (g_iter0 5-0*) |
| 77 | SteamBlizzard.Block | 988 | 59 | 273 | 120-153 | 100% (g_iter0 5-0*) |
| 78 | legobridge.kushalplayer | 986 | 65 | 203 | 89-114 | 100% (g_iter0 2-0*) |
| 79 | ax-95174.MPAction | 977 | 61 | 236 | 108-128 | 100% (c_swarm1 3-0*) |
| 80 | Patela171.Battlecode2023_Robot | 975 | 60 | 246 | 113-133 | 100% (g_iter0 2-0*) |
| 81 | JackLee9355.jackPlayer | 959 | 62 | 247 | 109-138 | 100% (g_iter0 2-0*) |
| 82 | michael-tyl.hqrewrite | 908 | 62 | 238 | 111-127 | 100% (g_iter0 2-0*) |
| 83 | Chahat08.toph | 897 | 61 | 248 | 114-134 | 100% (g_iter0 2-0*) |
| 84 | nail-e.Dante | 894 | 60 | 262 | 125-137 | 100% (g_iter0 2-0*) |
| 85 | mama4294.learningBot | 870 | 64 | 244 | 109-135 | 100% (g_iter0 2-0*) |
| 86 | anicolao.submission | 841 | 61 | 292 | 132-160 | 100% (g_iter0 2-0*) |
| 87 | team-remember-to-hydrate.sprint_1 | 775 | 64 | 258 | 109-149 | 100% (g_iter0 2-0*) |
| 88 | Vinceyou1.Player1 | 705 | 66 | 256 | 110-146 | 100% (g_iter0 2-0*) |
| 89 | addiesteward.elicompbot | 675 | 66 | 282 | 124-158 | 100% (g_iter0 5-0*) |
| 90 | michael-tyl.cc_v0_5_0_6 | 649 | 64 | 329 | 141-188 | 100% (g_iter0 2-0*) |
| 91 | toyat522.bot5 | 629 | 68 | 282 | 123-159 | 100% (g_iter0 2-0*) |
| 92 | Chahat08.lazarus | 616 | 68 | 276 | 118-158 | 100% (g_iter0 2-0*) |
| 93 | Swordman51.AdeptusAstartes2 | 607 | 68 | 272 | 115-157 | 100% (g_iter0 2-0*) |
| 94 | monmouth-college-cs.elicompbot | 603 | 67 | 296 | 126-170 | 100% (g_iter0 2-0*) |
| 95 | anicolao.jumbled | 488 | 72 | 293 | 128-165 | 100% (g_iter0 5-0*) |
| 96 | ShatterXD.SRNNbot | 482 | 75 | 245 | 105-140 | 100% (g_iter0 2-0*) |
| 97 | NotLLeon.player | 274 | 89 | 253 | 110-143 | 100% (g_iter0 2-0*) |
| 98 | CodeClash-ai.mysubmission | 247 | 88 | 286 | 122-164 | 100% (g_iter0 2-0*) |
| 99 | addiesteward.NDeClaw | 214 | 93 | 264 | 109-155 | 100% (g_iter0 5-0*) |
| 100 | Yooncw0223.lec3player | -95 | 110 | 253 | 37-216 | 100% (g_iter0 5-0*) |
| 101 | andrewkbank.First | -175 | 118 | 200 | 23-177 | 100% (g_iter0 2-0*) |
