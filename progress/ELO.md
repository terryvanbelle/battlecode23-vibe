# Ladder

11390 games (2408 ours, 6 of the stock examplefuncsplayer, 8976 between field bots on the ladder replica), 11158 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 102 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_def3 | 2098 +- 65 | 12 of 101 | 194 | 117-77 | 84.9% | 25.6% (vs 11) |
| c_aura2 | 2077 +- 67 | 14 of 101 | 182 | 98-84 | 84.1% | 25.7% (vs 12) |
| c_flee3 | 2075 +- 90 | 15 of 101 | 100 | 56-44 | 84.0% | 25.5% (vs 12) |
| c_anc3 | 2068 +- 71 | 16 of 101 | 161 | 87-74 | 83.7% | 24.8% (vs 12) |
| c_nav5 | 2007 +- 79 | 19 of 101 | 126 | 61-65 | 81.2% | 22.9% (vs 14) |
| c_nav6 | 1994 +- 79 | 21 of 101 | 129 | 58-71 | 80.7% | 23.6% (vs 15) |
| c_nav4 | 1967 +- 61 | 22 of 101 | 221 | 108-113 | 79.5% | 21.2% (vs 15) |
| c_swarm1 | 1887 +- 57 | 26 of 101 | 268 | 126-142 | 75.9% | 20.1% (vs 18) |
| c_line8a | 1847 +- 79 | 31 of 101 | 139 | 47-92 | 74.0% | 22.8% (vs 22) |
| g_iter0 | 1831 +- 56 | 33 of 101 | 455 | 230-225 | 73.2% | 22.7% (vs 23) |
| c_line6 | 1813 +- 95 | 35 of 101 | 100 | 32-68 | 72.3% | 22.3% (vs 24) |
| c_line7m | 1801 +- 95 | 36 of 101 | 100 | 31-69 | 71.7% | 21.3% (vs 24) |
| c_line5 | 1763 +- 98 | 41 of 101 | 100 | 28-72 | 69.8% | 22.4% (vs 28) |
| c_line4 | 1722 +- 101 | 43 of 101 | 100 | 25-75 | 67.7% | 20.1% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_aura2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2420 | 83 | 151 | 113-38 | 0% (g_iter0 0-35) |
| 2 | awesomelemonade.finalBot | 2401 | 75 | 273 | 227-46 | 20% (c_aura2 2-8*) |
| 3 | maxwelljones14.MPWorking | 2389 | 85 | 134 | 95-39 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2339 | 82 | 145 | 99-46 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2333 | 69 | 278 | 225-53 | 40% (c_aura2 4-6*) |
| 6 | AnOvercookedFork.quals | 2283 | 81 | 146 | 99-47 | 17% (c_aura2 1-5*) |
| 7 | pranayagra.finalbotfinaltwo | 2244 | 75 | 170 | 113-57 | 33% (c_aura2 3-6*) |
| 8 | pranayagra.finalbotfinal | 2230 | 59 | 335 | 236-99 | 40% (c_aura2 4-6*) |
| 9 | georgezhang02.FB_ZZZ | 2227 | 74 | 165 | 108-57 | 0% (c_anc3 0-3*) |
| 10 | battlecode-archive.sprintBot | 2191 | 77 | 158 | 106-52 | 33% (c_aura2 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2164 | 57 | 322 | 227-95 | 29% (c_aura2 6-15*) |
| 12 | **us:c_def3** | 2098 | 65 | 194 | 117-77 |  |
| 13 | CyrilSharma.finalBot | 2079 | 65 | 213 | 124-89 | 33% (c_aura2 2-4*) |
| 14 | **us:c_aura2** | 2077 | 67 | 182 | 98-84 |  |
| 15 | **us:c_flee3** | 2075 | 90 | 100 | 56-44 |  |
| 16 | **us:c_anc3** | 2068 | 71 | 161 | 87-74 |  |
| 17 | ethanlabelle.dev | 2064 | 64 | 195 | 120-75 | 50% (c_aura2 9-9*) |
| 18 | NotLLeon.v7 | 2009 | 53 | 329 | 192-137 | 60% (c_aura2 6-4*) |
| 19 | **us:c_nav5** | 2007 | 79 | 126 | 61-65 |  |
| 20 | georgezhang02.CB_tuning2 | 1996 | 53 | 315 | 187-128 | 56% (c_aura2 9-7*) |
| 21 | **us:c_nav6** | 1994 | 79 | 129 | 58-71 |  |
| 22 | **us:c_nav4** | 1967 | 61 | 221 | 108-113 |  |
| 23 | ethanlabelle.v19 | 1934 | 64 | 186 | 105-81 | 58% (c_aura2 7-5*) |
| 24 | britacatalin.FinalBot | 1926 | 52 | 321 | 171-150 | 80% (c_aura2 12-3*) |
| 25 | GabeG888.v8 | 1902 | 62 | 197 | 107-90 | 89% (c_def3 16-2*) |
| 26 | **us:c_swarm1** | 1887 | 57 | 268 | 126-142 |  |
| 27 | programjames.fourthbot | 1859 | 66 | 181 | 99-82 | 100% (c_aura2 3-0*) |
| 28 | GabeG888.v8o1 | 1855 | 64 | 180 | 104-76 | 100% (c_nav5 3-0*) |
| 29 | VarunVejalla.ali8 | 1852 | 67 | 178 | 100-78 | 100% (c_def3 8-0*) |
| 30 | DannyZhang686.pqual2 | 1847 | 62 | 205 | 113-92 | 83% (c_anc3 5-1*) |
| 31 | **us:c_line8a** | 1847 | 79 | 139 | 47-92 |  |
| 32 | VarunVejalla.karel | 1841 | 64 | 191 | 104-87 | 67% (c_nav4 6-3*) |
| 33 | **us:g_iter0** | 1831 | 56 | 455 | 230-225 |  |
| 34 | NicholasKelly15.gopher10 | 1820 | 70 | 157 | 88-69 | 100% (c_anc3 3-0*) |
| 35 | **us:c_line6** | 1813 | 95 | 100 | 32-68 |  |
| 36 | **us:c_line7m** | 1801 | 95 | 100 | 31-69 |  |
| 37 | louishu17.wouisv8 | 1798 | 65 | 201 | 113-88 | 67% (c_aura2 2-1*) |
| 38 | louishu17.louisv10 | 1780 | 65 | 180 | 99-81 | 100% (c_nav4 6-0*) |
| 39 | SampleProvider.SPAARK | 1777 | 64 | 185 | 105-80 | 33% (c_anc3 1-2*) |
| 40 | reeceyang.v5anaconda | 1774 | 52 | 325 | 144-181 | 80% (c_aura2 8-2*) |
| 41 | **us:c_line5** | 1763 | 98 | 100 | 28-72 |  |
| 42 | battlecode-archive.Sprint1 | 1745 | 52 | 310 | 133-177 | 100% (c_aura2 10-0*) |
| 43 | **us:c_line4** | 1722 | 101 | 100 | 25-75 |  |
| 44 | ipince.bobby | 1645 | 70 | 158 | 87-71 | 67% (c_swarm1 2-1*) |
| 45 | polyllc.poly | 1623 | 71 | 167 | 87-80 | 100% (g_iter0 2-0*) |
| 46 | SteamBlizzard.newVnewME | 1623 | 59 | 216 | 107-109 | 80% (g_iter0 4-1*) |
| 47 | legobridge.tacoplayer | 1615 | 63 | 202 | 108-94 | 85% (g_iter0 11-2*) |
| 48 | TheK098.qp1_7_sprint_1 | 1590 | 63 | 197 | 107-90 | 100% (c_swarm1 6-0*) |
| 49 | toyat522.bot5a | 1547 | 59 | 210 | 105-105 | 80% (g_iter0 4-1*) |
| 50 | elgoldie.head_v5 | 1541 | 58 | 210 | 106-104 | 100% (g_iter0 2-0*) |
| 51 | DukeBas._main | 1524 | 62 | 197 | 104-93 | 100% (g_iter0 2-0*) |
| 52 | ColtG5.rexv9 | 1515 | 59 | 216 | 110-106 | 100% (g_iter0 2-0*) |
| 53 | beaverbois.USQualifiers | 1468 | 61 | 201 | 103-98 | 50% (g_iter0 1-1*) |
| 54 | kevinli405.maggi3_2 | 1457 | 60 | 213 | 108-105 | 100% (g_iter0 2-0*) |
| 55 | BrysonJGalapon.friday | 1431 | 61 | 185 | 94-91 | 100% (g_iter0 2-0*) |
| 56 | Nawlej.PoonPoon | 1429 | 63 | 192 | 94-98 | 100% (g_iter0 2-0*) |
| 57 | nail-e.Barry | 1406 | 58 | 214 | 110-104 | 100% (g_iter0 2-0*) |
| 58 | yaonam.PoonPoonv4 | 1404 | 53 | 366 | 129-237 | 90% (c_aura2 9-1*) |
| 59 | kevinli405.maggi3 | 1392 | 59 | 225 | 117-108 | 100% (g_iter0 5-0*) |
| 60 | aj-chau.attempt1 | 1386 | 63 | 190 | 99-91 | 100% (g_iter0 5-0*) |
| 61 | prisms-cs-club.prisms10 | 1346 | 62 | 199 | 95-104 | 100% (g_iter0 2-0*) |
| 62 | ipince.bobby_v2 | 1311 | 61 | 211 | 103-108 | 67% (c_swarm1 2-1*) |
| 63 | mama4294.currentPlayer | 1310 | 59 | 220 | 107-113 | 100% (g_iter0 2-0*) |
| 64 | andrewgopher.gopherbot | 1228 | 57 | 244 | 118-126 | 100% (g_iter0 2-0*) |
| 65 | bewuwy.deathbot4 | 1227 | 55 | 263 | 127-136 | 100% (g_iter0 2-0*) |
| 66 | BrysonJGalapon.aloha | 1224 | 56 | 242 | 121-121 | 100% (c_swarm1 3-0*) |
| 67 | JfeMak.realplayer2 | 1210 | 62 | 196 | 94-102 | 100% (g_iter0 2-0*) |
| 68 | PSUtblock.sprint_four_player | 1183 | 64 | 203 | 103-100 | 100% (g_iter0 2-0*) |
| 69 | SampleProvider.SPAARK_1_12_2023 | 1155 | 57 | 250 | 119-131 | 100% (c_swarm1 3-0*) |
| 70 | NolanChai.nolan_1 | 1125 | 57 | 248 | 121-127 | 100% (g_iter0 2-0*) |
| 71 | Nawlej.PoonPoonv3 | 1125 | 57 | 252 | 121-131 | 100% (g_iter0 5-0*) |
| 72 | Juanbri02.matfisplayer1 | 1124 | 58 | 242 | 114-128 | 100% (g_iter0 5-0*) |
| 73 | SDainard-PDX.Team_Player | 1119 | 60 | 227 | 106-121 | 100% (g_iter0 2-0*) |
| 74 | andrewgopher.gopherbot1 | 1104 | 59 | 240 | 110-130 | 100% (g_iter0 2-0*) |
| 75 | jyorkio.elicompbot | 1097 | 58 | 231 | 111-120 | 100% (g_iter0 2-0*) |
| 76 | vontell.regressiongames | 1029 | 57 | 260 | 124-136 | 100% (g_iter0 5-0*) |
| 77 | SteamBlizzard.Block | 993 | 59 | 267 | 119-148 | 100% (g_iter0 5-0*) |
| 78 | legobridge.kushalplayer | 983 | 67 | 197 | 87-110 | 100% (g_iter0 2-0*) |
| 79 | ax-95174.MPAction | 978 | 61 | 230 | 107-123 | 100% (c_swarm1 3-0*) |
| 80 | JackLee9355.jackPlayer | 972 | 64 | 238 | 107-131 | 100% (g_iter0 2-0*) |
| 81 | Patela171.Battlecode2023_Robot | 959 | 62 | 234 | 105-129 | 100% (g_iter0 2-0*) |
| 82 | michael-tyl.hqrewrite | 909 | 64 | 227 | 107-120 | 100% (g_iter0 2-0*) |
| 83 | Chahat08.toph | 890 | 63 | 236 | 105-131 | 100% (g_iter0 2-0*) |
| 84 | nail-e.Dante | 887 | 61 | 253 | 118-135 | 100% (g_iter0 2-0*) |
| 85 | mama4294.learningBot | 861 | 65 | 233 | 103-130 | 100% (g_iter0 2-0*) |
| 86 | anicolao.submission | 834 | 62 | 286 | 127-159 | 100% (g_iter0 2-0*) |
| 87 | team-remember-to-hydrate.sprint_1 | 775 | 65 | 249 | 103-146 | 100% (g_iter0 2-0*) |
| 88 | Vinceyou1.Player1 | 706 | 66 | 253 | 110-143 | 100% (g_iter0 2-0*) |
| 89 | addiesteward.elicompbot | 672 | 67 | 274 | 120-154 | 100% (g_iter0 5-0*) |
| 90 | michael-tyl.cc_v0_5_0_6 | 652 | 65 | 317 | 136-181 | 100% (g_iter0 2-0*) |
| 91 | toyat522.bot5 | 623 | 69 | 274 | 118-156 | 100% (g_iter0 2-0*) |
| 92 | Chahat08.lazarus | 622 | 69 | 268 | 118-150 | 100% (g_iter0 2-0*) |
| 93 | Swordman51.AdeptusAstartes2 | 615 | 69 | 263 | 113-150 | 100% (g_iter0 2-0*) |
| 94 | monmouth-college-cs.elicompbot | 604 | 67 | 291 | 124-167 | 100% (g_iter0 2-0*) |
| 95 | anicolao.jumbled | 479 | 74 | 284 | 120-164 | 100% (g_iter0 5-0*) |
| 96 | ShatterXD.SRNNbot | 466 | 77 | 234 | 98-136 | 100% (g_iter0 2-0*) |
| 97 | NotLLeon.player | 273 | 90 | 243 | 104-139 | 100% (g_iter0 2-0*) |
| 98 | CodeClash-ai.mysubmission | 252 | 89 | 280 | 120-160 | 100% (g_iter0 2-0*) |
| 99 | addiesteward.NDeClaw | 213 | 95 | 253 | 102-151 | 100% (g_iter0 5-0*) |
| 100 | Yooncw0223.lec3player | -86 | 110 | 248 | 36-212 | 100% (g_iter0 5-0*) |
| 101 | andrewkbank.First | -166 | 119 | 190 | 22-168 | 100% (g_iter0 2-0*) |
