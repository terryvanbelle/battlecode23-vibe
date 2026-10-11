# Ladder

12937 games (2731 ours, 6 of the stock examplefuncsplayer, 10200 between field bots on the ladder replica), 12629 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 104 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_well5 | 2138 +- 91 | 12 of 103 | 100 | 64-36 | 87.1% | 32.8% (vs 11) |
| c_spread2 | 2106 +- 90 | 13 of 103 | 100 | 61-39 | 86.0% | 29.1% (vs 11) |
| c_def3 | 2076 +- 64 | 14 of 103 | 194 | 117-77 | 84.9% | 25.8% (vs 11) |
| c_flee3 | 2053 +- 89 | 16 of 103 | 100 | 56-44 | 84.0% | 25.4% (vs 12) |
| c_aura2 | 2047 +- 54 | 17 of 103 | 299 | 155-144 | 83.7% | 24.8% (vs 12) |
| c_anc3 | 2046 +- 70 | 18 of 103 | 161 | 87-74 | 83.7% | 24.7% (vs 12) |
| c_nav5 | 1987 +- 78 | 21 of 103 | 126 | 61-65 | 81.3% | 23.2% (vs 14) |
| c_nav6 | 1974 +- 78 | 23 of 103 | 129 | 58-71 | 80.7% | 23.8% (vs 15) |
| c_nav4 | 1946 +- 60 | 24 of 103 | 221 | 108-113 | 79.5% | 21.3% (vs 15) |
| c_swarm1 | 1867 +- 56 | 28 of 103 | 268 | 126-142 | 75.9% | 20.3% (vs 18) |
| c_line8a | 1825 +- 78 | 33 of 103 | 139 | 47-92 | 73.9% | 22.6% (vs 22) |
| g_iter0 | 1809 +- 55 | 34 of 103 | 455 | 230-225 | 73.1% | 21.3% (vs 22) |
| c_line6 | 1792 +- 94 | 36 of 103 | 100 | 32-68 | 72.3% | 21.2% (vs 23) |
| c_line7m | 1780 +- 95 | 37 of 103 | 100 | 31-69 | 71.7% | 20.2% (vs 23) |
| c_line5 | 1742 +- 97 | 43 of 103 | 100 | 28-72 | 69.8% | 22.7% (vs 28) |
| c_line4 | 1701 +- 100 | 45 of 103 | 100 | 25-75 | 67.7% | 20.4% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_aura2), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | IvanGeffner.fortytwo | 2388 | 78 | 163 | 119-44 | 0% (g_iter0 0-35) |
| 2 | awesomelemonade.finalBot | 2377 | 69 | 301 | 248-53 | 20% (c_aura2 2-8*) |
| 3 | maxwelljones14.MPWorking | 2362 | 80 | 146 | 102-44 | 0% (g_iter0 0-5*) |
| 4 | carlguo866.submit26_final | 2312 | 76 | 162 | 108-54 | 67% (c_nav4 2-1*) |
| 5 | vrangr1.AFinalsBot | 2301 | 63 | 313 | 245-68 | 40% (c_aura2 4-6*) |
| 6 | AnOvercookedFork.quals | 2263 | 74 | 170 | 113-57 | 20% (c_aura2 3-12*) |
| 7 | pranayagra.finalbotfinaltwo | 2218 | 69 | 193 | 127-66 | 29% (c_aura2 5-12*) |
| 8 | georgezhang02.FB_ZZZ | 2208 | 70 | 179 | 116-63 | 0% (c_anc3 0-3*) |
| 9 | pranayagra.finalbotfinal | 2199 | 54 | 382 | 263-119 | 36% (c_aura2 9-16*) |
| 10 | battlecode-archive.sprintBot | 2181 | 73 | 172 | 115-57 | 33% (c_aura2 1-2*) |
| 11 | jmerle.camel_case_v30_final | 2146 | 53 | 370 | 253-117 | 32% (c_aura2 10-21) |
| 12 | **us:c_well5** | 2138 | 91 | 100 | 64-36 |  |
| 13 | **us:c_spread2** | 2106 | 90 | 100 | 61-39 |  |
| 14 | **us:c_def3** | 2076 | 64 | 194 | 117-77 |  |
| 15 | CyrilSharma.finalBot | 2074 | 61 | 238 | 140-98 | 25% (c_aura2 5-15*) |
| 16 | **us:c_flee3** | 2053 | 89 | 100 | 56-44 |  |
| 17 | **us:c_aura2** | 2047 | 54 | 299 | 155-144 |  |
| 18 | **us:c_anc3** | 2046 | 70 | 161 | 87-74 |  |
| 19 | ethanlabelle.dev | 2018 | 60 | 220 | 128-92 | 54% (c_aura2 13-11*) |
| 20 | NotLLeon.v7 | 1995 | 50 | 375 | 215-160 | 64% (c_aura2 14-8*) |
| 21 | **us:c_nav5** | 1987 | 78 | 126 | 61-65 |  |
| 22 | georgezhang02.CB_tuning2 | 1978 | 50 | 360 | 205-155 | 62% (c_aura2 21-13) |
| 23 | **us:c_nav6** | 1974 | 78 | 129 | 58-71 |  |
| 24 | **us:c_nav4** | 1946 | 60 | 221 | 108-113 |  |
| 25 | ethanlabelle.v19 | 1906 | 60 | 208 | 118-90 | 67% (c_aura2 10-5*) |
| 26 | britacatalin.FinalBot | 1906 | 49 | 373 | 193-180 | 73% (c_aura2 16-6*) |
| 27 | GabeG888.v8 | 1868 | 58 | 216 | 114-102 | 89% (c_def3 16-2*) |
| 28 | **us:c_swarm1** | 1867 | 56 | 268 | 126-142 |  |
| 29 | programjames.fourthbot | 1846 | 61 | 207 | 113-94 | 100% (c_aura2 3-0*) |
| 30 | VarunVejalla.ali8 | 1843 | 63 | 198 | 111-87 | 50% (c_aura2 3-3*) |
| 31 | GabeG888.v8o1 | 1841 | 60 | 207 | 119-88 | 67% (c_aura2 4-2*) |
| 32 | VarunVejalla.karel | 1831 | 59 | 217 | 120-97 | 67% (c_nav4 6-3*) |
| 33 | **us:c_line8a** | 1825 | 78 | 139 | 47-92 |  |
| 34 | **us:g_iter0** | 1809 | 55 | 455 | 230-225 |  |
| 35 | DannyZhang686.pqual2 | 1809 | 58 | 226 | 120-106 | 83% (c_anc3 5-1*) |
| 36 | **us:c_line6** | 1792 | 94 | 100 | 32-68 |  |
| 37 | **us:c_line7m** | 1780 | 95 | 100 | 31-69 |  |
| 38 | NicholasKelly15.gopher10 | 1773 | 64 | 184 | 102-82 | 100% (c_anc3 3-0*) |
| 39 | louishu17.louisv10 | 1771 | 61 | 205 | 114-91 | 100% (c_nav4 6-0*) |
| 40 | louishu17.wouisv8 | 1759 | 62 | 213 | 113-100 | 83% (c_aura2 5-1*) |
| 41 | reeceyang.v5anaconda | 1756 | 48 | 380 | 163-217 | 80% (c_aura2 8-2*) |
| 42 | SampleProvider.SPAARK | 1749 | 59 | 210 | 114-96 | 33% (c_anc3 1-2*) |
| 43 | **us:c_line5** | 1742 | 97 | 100 | 28-72 |  |
| 44 | battlecode-archive.Sprint1 | 1716 | 50 | 345 | 139-206 | 100% (c_aura2 10-0*) |
| 45 | **us:c_line4** | 1701 | 100 | 100 | 25-75 |  |
| 46 | ipince.bobby | 1659 | 65 | 176 | 100-76 | 67% (c_swarm1 2-1*) |
| 47 | legobridge.tacoplayer | 1609 | 60 | 223 | 119-104 | 85% (g_iter0 11-2*) |
| 48 | SteamBlizzard.newVnewME | 1609 | 56 | 237 | 120-117 | 80% (g_iter0 4-1*) |
| 49 | TheK098.qp1_7_sprint_1 | 1587 | 58 | 221 | 121-100 | 100% (c_swarm1 6-0*) |
| 50 | polyllc.poly | 1557 | 65 | 190 | 93-97 | 100% (g_iter0 2-0*) |
| 51 | toyat522.bot5a | 1534 | 56 | 230 | 117-113 | 80% (g_iter0 4-1*) |
| 52 | elgoldie.head_v5 | 1528 | 55 | 228 | 114-114 | 100% (g_iter0 2-0*) |
| 53 | DukeBas._main | 1507 | 60 | 209 | 111-98 | 100% (g_iter0 2-0*) |
| 54 | ColtG5.rexv9 | 1501 | 56 | 230 | 117-113 | 100% (g_iter0 2-0*) |
| 55 | beaverbois.USQualifiers | 1469 | 58 | 221 | 115-106 | 50% (g_iter0 1-1*) |
| 56 | kevinli405.maggi3_2 | 1432 | 55 | 251 | 124-127 | 100% (g_iter0 2-0*) |
| 57 | Nawlej.PoonPoon | 1429 | 59 | 220 | 111-109 | 100% (g_iter0 2-0*) |
| 58 | BrysonJGalapon.friday | 1406 | 57 | 214 | 110-104 | 100% (g_iter0 2-0*) |
| 59 | nail-e.Barry | 1399 | 55 | 231 | 118-113 | 100% (g_iter0 2-0*) |
| 60 | yaonam.PoonPoonv4 | 1392 | 50 | 412 | 143-269 | 90% (c_aura2 9-1*) |
| 61 | aj-chau.attempt1 | 1386 | 57 | 228 | 121-107 | 100% (g_iter0 5-0*) |
| 62 | kevinli405.maggi3 | 1373 | 57 | 243 | 125-118 | 100% (g_iter0 5-0*) |
| 63 | prisms-cs-club.prisms10 | 1326 | 58 | 228 | 109-119 | 100% (g_iter0 2-0*) |
| 64 | mama4294.currentPlayer | 1312 | 56 | 241 | 120-121 | 100% (g_iter0 2-0*) |
| 65 | ipince.bobby_v2 | 1278 | 56 | 255 | 125-130 | 67% (c_swarm1 2-1*) |
| 66 | andrewgopher.gopherbot | 1213 | 54 | 271 | 132-139 | 100% (g_iter0 2-0*) |
| 67 | bewuwy.deathbot4 | 1212 | 52 | 295 | 143-152 | 100% (g_iter0 2-0*) |
| 68 | JfeMak.realplayer2 | 1208 | 56 | 245 | 123-122 | 100% (g_iter0 2-0*) |
| 69 | BrysonJGalapon.aloha | 1202 | 53 | 272 | 134-138 | 100% (c_swarm1 3-0*) |
| 70 | PSUtblock.sprint_four_player | 1176 | 57 | 250 | 126-124 | 100% (g_iter0 2-0*) |
| 71 | SampleProvider.SPAARK_1_12_2023 | 1138 | 55 | 270 | 130-140 | 100% (c_swarm1 3-0*) |
| 72 | Nawlej.PoonPoonv3 | 1124 | 54 | 280 | 137-143 | 100% (g_iter0 5-0*) |
| 73 | NolanChai.nolan_1 | 1108 | 53 | 303 | 146-157 | 100% (g_iter0 2-0*) |
| 74 | Juanbri02.matfisplayer1 | 1106 | 55 | 274 | 130-144 | 100% (g_iter0 5-0*) |
| 75 | SDainard-PDX.Team_Player | 1095 | 57 | 254 | 121-133 | 100% (g_iter0 2-0*) |
| 76 | andrewgopher.gopherbot1 | 1091 | 56 | 271 | 124-147 | 100% (g_iter0 2-0*) |
| 77 | jyorkio.elicompbot | 1065 | 56 | 260 | 124-136 | 100% (g_iter0 2-0*) |
| 78 | vontell.regressiongames | 1015 | 54 | 290 | 140-150 | 100% (g_iter0 5-0*) |
| 79 | legobridge.kushalplayer | 977 | 61 | 235 | 106-129 | 100% (g_iter0 2-0*) |
| 80 | SteamBlizzard.Block | 966 | 56 | 299 | 135-164 | 100% (g_iter0 5-0*) |
| 81 | Patela171.Battlecode2023_Robot | 963 | 57 | 278 | 129-149 | 100% (g_iter0 2-0*) |
| 82 | ax-95174.MPAction | 950 | 58 | 265 | 123-142 | 100% (c_swarm1 3-0*) |
| 83 | JackLee9355.jackPlayer | 916 | 61 | 272 | 122-150 | 100% (g_iter0 2-0*) |
| 84 | Chahat08.toph | 874 | 59 | 274 | 127-147 | 100% (g_iter0 2-0*) |
| 85 | michael-tyl.hqrewrite | 871 | 60 | 270 | 126-144 | 100% (g_iter0 2-0*) |
| 86 | nail-e.Dante | 867 | 57 | 302 | 144-158 | 100% (g_iter0 2-0*) |
| 87 | mama4294.learningBot | 835 | 61 | 274 | 122-152 | 100% (g_iter0 2-0*) |
| 88 | anicolao.submission | 813 | 59 | 322 | 146-176 | 100% (g_iter0 2-0*) |
| 89 | team-remember-to-hydrate.sprint_1 | 735 | 63 | 284 | 121-163 | 100% (g_iter0 2-0*) |
| 90 | Vinceyou1.Player1 | 667 | 64 | 278 | 117-161 | 100% (g_iter0 2-0*) |
| 91 | addiesteward.elicompbot | 646 | 64 | 299 | 130-169 | 100% (g_iter0 5-0*) |
| 92 | toyat522.bot5 | 620 | 64 | 318 | 143-175 | 100% (g_iter0 2-0*) |
| 93 | michael-tyl.cc_v0_5_0_6 | 619 | 63 | 340 | 145-195 | 100% (g_iter0 2-0*) |
| 94 | Chahat08.lazarus | 590 | 66 | 299 | 131-168 | 100% (g_iter0 2-0*) |
| 95 | monmouth-college-cs.elicompbot | 586 | 64 | 331 | 144-187 | 100% (g_iter0 2-0*) |
| 96 | Swordman51.AdeptusAstartes2 | 580 | 66 | 299 | 131-168 | 100% (g_iter0 2-0*) |
| 97 | anicolao.jumbled | 475 | 70 | 317 | 141-176 | 100% (g_iter0 5-0*) |
| 98 | ShatterXD.SRNNbot | 464 | 71 | 287 | 126-161 | 100% (g_iter0 2-0*) |
| 99 | NotLLeon.player | 249 | 86 | 279 | 123-156 | 100% (g_iter0 2-0*) |
| 100 | CodeClash-ai.mysubmission | 219 | 85 | 319 | 141-178 | 100% (g_iter0 2-0*) |
| 101 | addiesteward.NDeClaw | 176 | 91 | 279 | 113-166 | 100% (g_iter0 5-0*) |
| 102 | Yooncw0223.lec3player | -122 | 105 | 278 | 40-238 | 100% (g_iter0 5-0*) |
| 103 | andrewkbank.First | -198 | 114 | 206 | 24-182 | 100% (g_iter0 2-0*) |
