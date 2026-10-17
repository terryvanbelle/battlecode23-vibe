# Ladder

22757 games (5804 ours, 6 of the stock examplefuncsplayer, 16947 between field bots on the ladder replica), 22168 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%, relative to the mean rating of all 126 players; field score = expected score against every rated ladder bot (87 of 87), one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| c_gp1 | 2040 +- 65 | 9 of 125 | 169 | 111-58 | 89.3% | 37.6% (vs 8) |
| c_adlo2 | 2015 +- 88 | 12 of 125 | 100 | 68-32 | 88.5% | 37.2% (vs 10) |
| c_pack1 | 2004 +- 88 | 14 of 125 | 100 | 67-33 | 88.1% | 37.0% (vs 11) |
| c_well5 | 1971 +- 87 | 15 of 125 | 100 | 64-36 | 87.0% | 32.9% (vs 11) |
| c_blind2 | 1961 +- 87 | 16 of 125 | 100 | 63-37 | 86.6% | 31.6% (vs 11) |
| c_tune1 | 1961 +- 87 | 17 of 125 | 100 | 63-37 | 86.6% | 31.6% (vs 11) |
| c_blind1 | 1961 +- 87 | 18 of 125 | 100 | 63-37 | 86.6% | 31.6% (vs 11) |
| c_mid1 | 1950 +- 86 | 19 of 125 | 100 | 62-38 | 86.2% | 30.3% (vs 11) |
| c_well10 | 1950 +- 86 | 20 of 125 | 100 | 62-38 | 86.2% | 30.3% (vs 11) |
| c_mend3 | 1940 +- 86 | 21 of 125 | 100 | 61-39 | 85.8% | 29.1% (vs 11) |
| c_bc3 | 1940 +- 86 | 22 of 125 | 100 | 61-39 | 85.8% | 29.1% (vs 11) |
| c_spread2 | 1940 +- 86 | 23 of 125 | 100 | 61-39 | 85.8% | 29.1% (vs 11) |
| c_scout1 | 1929 +- 86 | 25 of 125 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_thr1 | 1929 +- 86 | 26 of 125 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_well7 | 1929 +- 86 | 27 of 125 | 100 | 60-40 | 85.4% | 29.7% (vs 12) |
| c_seam1 | 1919 +- 86 | 28 of 125 | 100 | 59-41 | 85.0% | 28.5% (vs 12) |
| c_cap1 | 1919 +- 86 | 29 of 125 | 100 | 59-41 | 85.0% | 28.5% (vs 12) |
| c_seam2 | 1919 +- 86 | 30 of 125 | 100 | 59-41 | 85.0% | 28.5% (vs 12) |
| c_mend2 | 1915 +- 39 | 31 of 125 | 612 | 362-250 | 84.9% | 28.0% (vs 12) |
| c_bc1 | 1914 +- 65 | 32 of 125 | 164 | 97-67 | 84.8% | 28.0% (vs 12) |
| c_def3 | 1912 +- 59 | 33 of 125 | 199 | 120-79 | 84.7% | 27.7% (vs 12) |
| c_siege1 | 1908 +- 86 | 34 of 125 | 100 | 58-42 | 84.6% | 27.3% (vs 12) |
| c_well9 | 1905 +- 52 | 35 of 125 | 260 | 138-122 | 84.5% | 27.0% (vs 12) |
| c_end2 | 1898 +- 86 | 36 of 125 | 100 | 57-43 | 84.2% | 26.2% (vs 12) |
| c_flee3 | 1888 +- 85 | 37 of 125 | 100 | 56-44 | 83.8% | 25.1% (vs 12) |
| c_open1 | 1888 +- 85 | 38 of 125 | 100 | 56-44 | 83.8% | 25.1% (vs 12) |
| c_anc3 | 1883 +- 65 | 39 of 125 | 163 | 88-75 | 83.6% | 24.7% (vs 12) |
| c_aura2 | 1883 +- 48 | 40 of 125 | 314 | 162-152 | 83.6% | 24.6% (vs 12) |
| c_nav5 | 1825 +- 75 | 42 of 125 | 126 | 61-65 | 81.2% | 21.3% (vs 13) |
| c_nav6 | 1810 +- 74 | 44 of 125 | 129 | 58-71 | 80.5% | 21.9% (vs 14) |
| c_nav4 | 1788 +- 56 | 46 of 125 | 221 | 108-113 | 79.6% | 21.9% (vs 15) |
| c_swarm1 | 1709 +- 52 | 51 of 125 | 271 | 128-143 | 76.0% | 22.3% (vs 19) |
| c_line8a | 1666 +- 75 | 55 of 125 | 139 | 47-92 | 73.9% | 22.4% (vs 22) |
| g_iter0 | 1646 +- 52 | 56 of 125 | 456 | 230-226 | 73.0% | 20.8% (vs 22) |
| c_line6 | 1629 +- 91 | 57 of 125 | 100 | 32-68 | 72.1% | 19.4% (vs 22) |
| c_line7m | 1617 +- 92 | 62 of 125 | 100 | 31-69 | 71.5% | 23.2% (vs 26) |
| c_line5 | 1579 +- 94 | 65 of 125 | 100 | 28-72 | 69.7% | 22.0% (vs 28) |
| c_line4 | 1539 +- 97 | 67 of 125 | 100 | 25-75 | 67.6% | 19.8% (vs 29) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (c_gp1), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | maxwelljones14.MPWorking | 2214 | 58 | 245 | 169-76 | 22% (c_mend2 2-7*) |
| 2 | awesomelemonade.finalBot | 2190 | 43 | 628 | 486-142 | 30% (c_gp1 3-7*) |
| 3 | IvanGeffner.fortytwo | 2189 | 55 | 281 | 189-92 | 13% (c_mend2 3-20*) |
| 4 | carlguo866.submit26_final | 2152 | 56 | 258 | 158-100 | 0% (c_mend2 0-3*) |
| 5 | vrangr1.AFinalsBot | 2122 | 40 | 633 | 457-176 | 50% (c_gp1 5-5*) |
| 6 | AnOvercookedFork.quals | 2086 | 53 | 287 | 178-109 | 27% (c_mend2 4-11*) |
| 7 | pranayagra.finalbotfinaltwo | 2049 | 51 | 302 | 188-114 | 50% (c_gp1 4-4*) |
| 8 | georgezhang02.FB_ZZZ | 2044 | 50 | 305 | 191-114 | 50% (c_gp1 3-3*) |
| 9 | **us:c_gp1** | 2040 | 65 | 169 | 111-58 |  |
| 10 | pranayagra.finalbotfinal | 2031 | 36 | 744 | 475-269 | 56% (c_gp1 10-8*) |
| 11 | battlecode-archive.sprintBot | 2019 | 51 | 296 | 181-115 | 50% (c_gp1 3-3*) |
| 12 | **us:c_adlo2** | 2015 | 88 | 100 | 68-32 |  |
| 13 | jmerle.camel_case_v30_final | 2010 | 37 | 701 | 445-256 | 42% (c_gp1 8-11*) |
| 14 | **us:c_pack1** | 2004 | 88 | 100 | 67-33 |  |
| 15 | **us:c_well5** | 1971 | 87 | 100 | 64-36 |  |
| 16 | **us:c_blind2** | 1961 | 87 | 100 | 63-37 |  |
| 17 | **us:c_tune1** | 1961 | 87 | 100 | 63-37 |  |
| 18 | **us:c_blind1** | 1961 | 87 | 100 | 63-37 |  |
| 19 | **us:c_mid1** | 1950 | 86 | 100 | 62-38 |  |
| 20 | **us:c_well10** | 1950 | 86 | 100 | 62-38 |  |
| 21 | **us:c_mend3** | 1940 | 86 | 100 | 61-39 |  |
| 22 | **us:c_bc3** | 1940 | 86 | 100 | 61-39 |  |
| 23 | **us:c_spread2** | 1940 | 86 | 100 | 61-39 |  |
| 24 | CyrilSharma.finalBot | 1937 | 45 | 403 | 230-173 | 62% (c_gp1 16-10*) |
| 25 | **us:c_scout1** | 1929 | 86 | 100 | 60-40 |  |
| 26 | **us:c_thr1** | 1929 | 86 | 100 | 60-40 |  |
| 27 | **us:c_well7** | 1929 | 86 | 100 | 60-40 |  |
| 28 | **us:c_seam1** | 1919 | 86 | 100 | 59-41 |  |
| 29 | **us:c_cap1** | 1919 | 86 | 100 | 59-41 |  |
| 30 | **us:c_seam2** | 1919 | 86 | 100 | 59-41 |  |
| 31 | **us:c_mend2** | 1915 | 39 | 612 | 362-250 |  |
| 32 | **us:c_bc1** | 1914 | 65 | 164 | 97-67 |  |
| 33 | **us:c_def3** | 1912 | 59 | 199 | 120-79 |  |
| 34 | **us:c_siege1** | 1908 | 86 | 100 | 58-42 |  |
| 35 | **us:c_well9** | 1905 | 52 | 260 | 138-122 |  |
| 36 | **us:c_end2** | 1898 | 86 | 100 | 57-43 |  |
| 37 | **us:c_flee3** | 1888 | 85 | 100 | 56-44 |  |
| 38 | **us:c_open1** | 1888 | 85 | 100 | 56-44 |  |
| 39 | **us:c_anc3** | 1883 | 65 | 163 | 88-75 |  |
| 40 | **us:c_aura2** | 1883 | 48 | 314 | 162-152 |  |
| 41 | ethanlabelle.dev | 1849 | 43 | 416 | 230-186 | 52% (c_well9 17-16) |
| 42 | **us:c_nav5** | 1825 | 75 | 126 | 61-65 |  |
| 43 | NotLLeon.v7 | 1822 | 34 | 774 | 372-402 | 69% (c_gp1 9-4*) |
| 44 | **us:c_nav6** | 1810 | 74 | 129 | 58-71 |  |
| 45 | georgezhang02.CB_tuning2 | 1805 | 34 | 780 | 365-415 | 100% (c_gp1 10-0*) |
| 46 | **us:c_nav4** | 1788 | 56 | 221 | 108-113 |  |
| 47 | britacatalin.FinalBot | 1739 | 35 | 731 | 314-417 | 80% (c_gp1 8-2*) |
| 48 | ethanlabelle.v19 | 1737 | 43 | 406 | 205-201 | 83% (c_well9 5-1*) |
| 49 | GabeG888.v8 | 1717 | 46 | 333 | 185-148 | 67% (c_well9 2-1*) |
| 50 | VarunVejalla.karel | 1717 | 43 | 422 | 214-208 | 67% (c_gp1 2-1*) |
| 51 | **us:c_swarm1** | 1709 | 52 | 271 | 128-143 |  |
| 52 | programjames.fourthbot | 1704 | 46 | 337 | 184-153 | 64% (c_mend2 7-4*) |
| 53 | GabeG888.v8o1 | 1692 | 46 | 333 | 185-148 | 33% (c_well9 1-2*) |
| 54 | VarunVejalla.ali8 | 1688 | 47 | 321 | 171-150 | 83% (c_mend2 5-1*) |
| 55 | **us:c_line8a** | 1666 | 75 | 139 | 47-92 |  |
| 56 | **us:g_iter0** | 1646 | 52 | 456 | 230-226 |  |
| 57 | **us:c_line6** | 1629 | 91 | 100 | 32-68 |  |
| 58 | NicholasKelly15.gopher10 | 1626 | 47 | 310 | 171-139 | 100% (c_anc3 3-0*) |
| 59 | DannyZhang686.pqual2 | 1623 | 44 | 372 | 188-184 | 83% (c_mend2 5-1*) |
| 60 | louishu17.louisv10 | 1618 | 47 | 321 | 173-148 | 100% (c_bc1 3-0*) |
| 61 | SampleProvider.SPAARK | 1617 | 47 | 320 | 172-148 | 33% (c_anc3 1-2*) |
| 62 | **us:c_line7m** | 1617 | 92 | 100 | 31-69 |  |
| 63 | louishu17.wouisv8 | 1609 | 46 | 342 | 181-161 | 83% (c_aura2 5-1*) |
| 64 | reeceyang.v5anaconda | 1602 | 36 | 735 | 263-472 | 100% (c_gp1 10-0*) |
| 65 | **us:c_line5** | 1579 | 94 | 100 | 28-72 |  |
| 66 | battlecode-archive.Sprint1 | 1547 | 37 | 708 | 228-480 | 100% (c_gp1 10-0*) |
| 67 | **us:c_line4** | 1539 | 97 | 100 | 25-75 |  |
| 68 | ipince.bobby | 1478 | 49 | 305 | 157-148 | 67% (c_swarm1 2-1*) |
| 69 | SteamBlizzard.newVnewME | 1460 | 44 | 372 | 190-182 | 80% (g_iter0 4-1*) |
| 70 | legobridge.tacoplayer | 1439 | 46 | 366 | 175-191 | 100% (c_mend2 6-0*) |
| 71 | TheK098.qp1_7_sprint_1 | 1419 | 45 | 363 | 196-167 | 100% (c_mend2 6-0*) |
| 72 | polyllc.poly | 1406 | 50 | 303 | 153-150 | 100% (g_iter0 2-0*) |
| 73 | ColtG5.rexv9 | 1370 | 44 | 376 | 187-189 | 100% (g_iter0 2-0*) |
| 74 | toyat522.bot5a | 1364 | 45 | 372 | 177-195 | 80% (g_iter0 4-1*) |
| 75 | elgoldie.head_v5 | 1343 | 44 | 360 | 176-184 | 100% (g_iter0 2-0*) |
| 76 | DukeBas._main | 1335 | 45 | 377 | 207-170 | 100% (c_mend2 6-0*) |
| 77 | beaverbois.USQualifiers | 1312 | 45 | 358 | 187-171 | 50% (g_iter0 1-1*) |
| 78 | Nawlej.PoonPoon | 1274 | 47 | 342 | 172-170 | 100% (g_iter0 2-0*) |
| 79 | kevinli405.maggi3_2 | 1267 | 44 | 397 | 203-194 | 100% (g_iter0 2-0*) |
| 80 | yaonam.PoonPoonv4 | 1245 | 40 | 777 | 234-543 | 100% (c_gp1 10-0*) |
| 81 | BrysonJGalapon.friday | 1230 | 44 | 366 | 191-175 | 100% (g_iter0 2-0*) |
| 82 | nail-e.Barry | 1205 | 45 | 374 | 188-186 | 100% (g_iter0 2-0*) |
| 83 | aj-chau.attempt1 | 1197 | 44 | 392 | 204-188 | 100% (g_iter0 5-0*) |
| 84 | kevinli405.maggi3 | 1193 | 46 | 381 | 185-196 | 100% (g_iter0 5-0*) |
| 85 | prisms-cs-club.prisms10 | 1164 | 45 | 392 | 201-191 | 100% (g_iter0 2-0*) |
| 86 | mama4294.currentPlayer | 1152 | 44 | 393 | 195-198 | 100% (g_iter0 2-0*) |
| 87 | ipince.bobby_v2 | 1128 | 43 | 438 | 217-221 | 67% (c_swarm1 2-1*) |
| 88 | bewuwy.deathbot4 | 1039 | 43 | 467 | 230-237 | 100% (g_iter0 2-0*) |
| 89 | JfeMak.realplayer2 | 1035 | 44 | 429 | 213-216 | 100% (g_iter0 2-0*) |
| 90 | andrewgopher.gopherbot | 1029 | 44 | 438 | 205-233 | 100% (g_iter0 2-0*) |
| 91 | BrysonJGalapon.aloha | 1022 | 43 | 459 | 230-229 | 100% (c_swarm1 3-0*) |
| 92 | PSUtblock.sprint_four_player | 987 | 46 | 423 | 206-217 | 100% (g_iter0 2-0*) |
| 93 | SampleProvider.SPAARK_1_12_2023 | 958 | 45 | 472 | 242-230 | 100% (c_swarm1 3-0*) |
| 94 | Nawlej.PoonPoonv3 | 935 | 45 | 460 | 220-240 | 100% (g_iter0 5-0*) |
| 95 | SDainard-PDX.Team_Player | 922 | 47 | 419 | 195-224 | 100% (g_iter0 2-0*) |
| 96 | Juanbri02.matfisplayer1 | 921 | 45 | 459 | 226-233 | 100% (g_iter0 5-0*) |
| 97 | NolanChai.nolan_1 | 914 | 44 | 477 | 234-243 | 100% (g_iter0 2-0*) |
| 98 | andrewgopher.gopherbot1 | 900 | 46 | 434 | 199-235 | 100% (g_iter0 2-0*) |
| 99 | jyorkio.elicompbot | 877 | 45 | 445 | 217-228 | 100% (g_iter0 2-0*) |
| 100 | vontell.regressiongames | 803 | 46 | 470 | 230-240 | 100% (g_iter0 5-0*) |
| 101 | legobridge.kushalplayer | 783 | 48 | 421 | 194-227 | 100% (g_iter0 2-0*) |
| 102 | SteamBlizzard.Block | 735 | 48 | 481 | 224-257 | 100% (g_iter0 5-0*) |
| 103 | Patela171.Battlecode2023_Robot | 728 | 48 | 457 | 214-243 | 100% (g_iter0 2-0*) |
| 104 | ax-95174.MPAction | 702 | 48 | 465 | 208-257 | 100% (c_swarm1 3-0*) |
| 105 | nail-e.Dante | 655 | 49 | 490 | 245-245 | 100% (g_iter0 2-0*) |
| 106 | Chahat08.toph | 647 | 49 | 467 | 216-251 | 100% (g_iter0 2-0*) |
| 107 | michael-tyl.hqrewrite | 644 | 50 | 443 | 216-227 | 100% (g_iter0 2-0*) |
| 108 | JackLee9355.jackPlayer | 639 | 52 | 425 | 187-238 | 100% (g_iter0 2-0*) |
| 109 | mama4294.learningBot | 633 | 50 | 471 | 231-240 | 100% (g_iter0 2-0*) |
| 110 | anicolao.submission | 588 | 50 | 514 | 241-273 | 100% (g_iter0 2-0*) |
| 111 | team-remember-to-hydrate.sprint_1 | 577 | 51 | 477 | 217-260 | 100% (g_iter0 2-0*) |
| 112 | Vinceyou1.Player1 | 463 | 53 | 467 | 215-252 | 100% (g_iter0 2-0*) |
| 113 | addiesteward.elicompbot | 446 | 53 | 491 | 218-273 | 100% (g_iter0 5-0*) |
| 114 | toyat522.bot5 | 444 | 53 | 517 | 225-292 | 100% (g_iter0 2-0*) |
| 115 | michael-tyl.cc_v0_5_0_6 | 440 | 52 | 550 | 256-294 | 100% (g_iter0 2-0*) |
| 116 | Chahat08.lazarus | 407 | 54 | 508 | 234-274 | 100% (g_iter0 2-0*) |
| 117 | Swordman51.AdeptusAstartes2 | 404 | 55 | 492 | 238-254 | 100% (g_iter0 2-0*) |
| 118 | monmouth-college-cs.elicompbot | 374 | 54 | 528 | 233-295 | 100% (g_iter0 2-0*) |
| 119 | anicolao.jumbled | 288 | 58 | 514 | 237-277 | 100% (g_iter0 5-0*) |
| 120 | ShatterXD.SRNNbot | 270 | 58 | 508 | 242-266 | 100% (g_iter0 2-0*) |
| 121 | NotLLeon.player | 33 | 72 | 477 | 224-253 | 100% (g_iter0 2-0*) |
| 122 | CodeClash-ai.mysubmission | -71 | 76 | 500 | 222-278 | 100% (g_iter0 2-0*) |
| 123 | addiesteward.NDeClaw | -82 | 77 | 465 | 205-260 | 100% (g_iter0 5-0*) |
| 124 | Yooncw0223.lec3player | -389 | 88 | 433 | 77-356 | 100% (g_iter0 5-0*) |
| 125 | andrewkbank.First | -446 | 92 | 346 | 54-292 | 100% (g_iter0 2-0*) |
