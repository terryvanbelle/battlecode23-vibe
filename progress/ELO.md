# Ladder

225 games (180 ours, 45 between field bots on the ladder replica), 225 distinct (a repeated pairing on the same map, orientation and seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (so one heavily repeated pairing cannot pull the fit); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| g_iter0 | 1744 +- 67 | 16 of 89 | 177 | 134-43 | 75.3% | 36.2% (vs 15) |
| examplefuncsplayer | 1280 +- 381 | 85 of 89 | 3 | 0-3 | 25.1% | 23.8% (vs 83) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | georgezhang02.FB_ZZZ | 1996 | 373 | 5 | 5-0 | 0% (g_iter0 0-2*) |
| 2 | carlguo866.submit26_final | 1875 | 389 | 5 | 5-0 | 0% (g_iter0 0-2*) |
| 3 | maxwelljones14.MPWorking | 1875 | 389 | 5 | 5-0 | 0% (g_iter0 0-2*) |
| 4 | AnOvercookedFork.quals | 1835 | 410 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 5 | CyrilSharma.finalBot | 1835 | 410 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 6 | DannyZhang686.pqual2 | 1835 | 410 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 7 | GabeG888.v8o1 | 1835 | 410 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 8 | IvanGeffner.fortytwo | 1835 | 410 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 9 | NotLLeon.v7 | 1835 | 410 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 10 | battlecode-archive.sprintBot | 1835 | 410 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 11 | ethanlabelle.dev | 1835 | 410 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 12 | pranayagra.finalbotfinaltwo | 1835 | 410 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 13 | awesomelemonade.finalBot | 1824 | 292 | 5 | 4-1 | 0% (g_iter0 0-2*) |
| 14 | pranayagra.finalbotfinal | 1824 | 292 | 5 | 4-1 | 0% (g_iter0 0-2*) |
| 15 | vrangr1.AFinalsBot | 1769 | 295 | 5 | 4-1 | 50% (g_iter0 1-1*) |
| 16 | **us:g_iter0** | 1744 | 67 | 177 | 134-43 |  |
| 17 | jmerle.camel_case_v30_final | 1743 | 299 | 5 | 4-1 | 0% (g_iter0 0-2*) |
| 18 | georgezhang02.CB_tuning2 | 1720 | 303 | 5 | 2-3 | 0% (g_iter0 0-2*) |
| 19 | battlecode-archive.Sprint1 | 1693 | 254 | 8 | 5-3 | 50% (g_iter0 1-1*) |
| 20 | reeceyang.v5anaconda | 1693 | 254 | 8 | 5-3 | 50% (g_iter0 1-1*) |
| 21 | GabeG888.v8 | 1622 | 362 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 22 | VarunVejalla.ali8 | 1622 | 362 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 23 | beaverbois.USQualifiers | 1622 | 362 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 24 | britacatalin.FinalBot | 1622 | 362 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 25 | ethanlabelle.v19 | 1622 | 362 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 26 | louishu17.wouisv8 | 1622 | 362 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 27 | yaonam.PoonPoonv4 | 1570 | 253 | 8 | 4-4 | 50% (g_iter0 1-1*) |
| 28 | BrysonJGalapon.friday | 1535 | 298 | 5 | 3-2 | 100% (g_iter0 2-0*) |
| 29 | PSUtblock.sprint_four_player | 1524 | 303 | 5 | 3-2 | 100% (g_iter0 2-0*) |
| 30 | aj-chau.attempt1 | 1524 | 303 | 5 | 3-2 | 100% (g_iter0 2-0*) |
| 31 | legobridge.tacoplayer | 1524 | 303 | 5 | 3-2 | 100% (g_iter0 2-0*) |
| 32 | toyat522.bot5a | 1502 | 299 | 5 | 1-4 | 80% (g_iter0 4-1*) |
| 33 | ipince.bobby | 1502 | 299 | 5 | 1-4 | 100% (g_iter0 2-0*) |
| 34 | DukeBas._main | 1448 | 282 | 5 | 2-3 | 100% (g_iter0 2-0*) |
| 35 | anicolao.submission | 1448 | 282 | 5 | 2-3 | 100% (g_iter0 2-0*) |
| 36 | BrysonJGalapon.aloha | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 37 | Chahat08.lazarus | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 38 | Chahat08.toph | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 39 | CodeClash-ai.mysubmission | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 40 | ColtG5.rexv9 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 41 | JfeMak.realplayer2 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 42 | Juanbri02.matfisplayer1 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 43 | Nawlej.PoonPoon | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 44 | Nawlej.PoonPoonv3 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 45 | NicholasKelly15.gopher10 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 46 | NolanChai.nolan_1 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 47 | Patela171.Battlecode2023_Robot | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 48 | SDainard-PDX.Team_Player | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 49 | SampleProvider.SPAARK | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 50 | SampleProvider.SPAARK_1_12_2023 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 51 | ShatterXD.SRNNbot | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 52 | SteamBlizzard.Block | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 53 | SteamBlizzard.newVnewME | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 54 | Swordman51.AdeptusAstartes2 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 55 | TheK098.qp1_7_sprint_1 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 56 | VarunVejalla.karel | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 57 | Yooncw0223.lec3player | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 58 | addiesteward.NDeClaw | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 59 | addiesteward.elicompbot | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 60 | andrewgopher.gopherbot1 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 61 | andrewkbank.First | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 62 | anicolao.jumbled | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 63 | bewuwy.deathbot4 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 64 | ipince.bobby_v2 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 65 | jyorkio.elicompbot | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 66 | kevinli405.maggi3 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 67 | kevinli405.maggi3_2 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 68 | legobridge.kushalplayer | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 69 | mama4294.learningBot | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 70 | michael-tyl.cc_v0_5_0_6 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 71 | michael-tyl.hqrewrite | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 72 | monmouth-college-cs.elicompbot | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 73 | nail-e.Barry | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 74 | nail-e.Dante | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 75 | polyllc.poly | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 76 | programjames.fourthbot | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 77 | team-remember-to-hydrate.sprint_1 | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 78 | vontell.regressiongames | 1410 | 410 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 79 | elgoldie.head_v5 | 1369 | 389 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 80 | louishu17.louisv10 | 1369 | 389 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 81 | JackLee9355.jackPlayer | 1368 | 295 | 5 | 1-4 | 100% (g_iter0 2-0*) |
| 82 | andrewgopher.gopherbot | 1368 | 295 | 5 | 1-4 | 100% (g_iter0 2-0*) |
| 83 | ax-95174.MPAction | 1320 | 377 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 84 | prisms-cs-club.prisms10 | 1320 | 377 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 85 | **us:examplefuncsplayer** | 1280 | 381 | 3 | 0-3 |  |
| 86 | toyat522.bot5 | 1271 | 373 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 87 | NotLLeon.player | 1249 | 373 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 88 | Vinceyou1.Player1 | 1249 | 373 | 5 | 0-5 | 100% (g_iter0 2-0*) |
| 89 | mama4294.currentPlayer | 1249 | 373 | 5 | 0-5 | 100% (g_iter0 2-0*) |
