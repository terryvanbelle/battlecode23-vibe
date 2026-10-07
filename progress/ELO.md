# Ladder

174 scrimmages (ours only), 174 distinct (a repeated pairing with the same seed replays the same game and counts once), rated by a batch Bradley-Terry fit on the Elo scale (`tools/elolib.py`), each pair of players counting at most 200 games (owner PROMPTS 191: the target filler plays one opponent thousands of times); each of our builds is its own player. 87 of 87 ladder bots met.

Our builds (rating +- 95%; field score = expected score against every ladder bot, one game each; vs higher = the same against only the ladder bots rated above the build, with their count):

| build | rating | rank | games | record | field score | vs higher |
|---|---|---|---|---|---|---|
| g_iter0 | 1732 +- 66 | 17 of 88 | 174 | 131-43 | 75.0% | 36.8% (vs 16) |

Our record = OUR win rate (our W-L) against the bot by the incumbent (g_iter0), whatever the count; * marks fewer than 30 games (+- 18 points at 95% for 30 games, +- 20 for 24); a bot the incumbent never met shows the most recent of our builds that did; blank if none has.

| rank | player | rating | +- 95% | games | W-L | our record |
|---|---|---|---|---|---|---|
| 1 | AnOvercookedFork.quals | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 2 | CyrilSharma.finalBot | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 3 | DannyZhang686.pqual2 | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 4 | GabeG888.v8o1 | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 5 | IvanGeffner.fortytwo | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 6 | NotLLeon.v7 | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 7 | awesomelemonade.finalBot | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 8 | battlecode-archive.sprintBot | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 9 | carlguo866.submit26_final | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 10 | ethanlabelle.dev | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 11 | georgezhang02.CB_tuning2 | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 12 | georgezhang02.FB_ZZZ | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 13 | jmerle.camel_case_v30_final | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 14 | maxwelljones14.MPWorking | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 15 | pranayagra.finalbotfinal | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 16 | pranayagra.finalbotfinaltwo | 1827 | 409 | 2 | 2-0 | 0% (g_iter0 0-2*) |
| 17 | **us:g_iter0** | 1732 | 66 | 174 | 131-43 |  |
| 18 | GabeG888.v8 | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 19 | VarunVejalla.ali8 | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 20 | battlecode-archive.Sprint1 | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 21 | beaverbois.USQualifiers | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 22 | britacatalin.FinalBot | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 23 | ethanlabelle.v19 | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 24 | louishu17.wouisv8 | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 25 | reeceyang.v5anaconda | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 26 | toyat522.bot5a | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 27 | vrangr1.AFinalsBot | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 28 | yaonam.PoonPoonv4 | 1616 | 360 | 2 | 1-1 | 50% (g_iter0 1-1*) |
| 29 | BrysonJGalapon.aloha | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 30 | BrysonJGalapon.friday | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 31 | Chahat08.lazarus | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 32 | Chahat08.toph | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 33 | CodeClash-ai.mysubmission | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 34 | ColtG5.rexv9 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 35 | DukeBas._main | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 36 | JackLee9355.jackPlayer | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 37 | JfeMak.realplayer2 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 38 | Juanbri02.matfisplayer1 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 39 | Nawlej.PoonPoon | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 40 | Nawlej.PoonPoonv3 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 41 | NicholasKelly15.gopher10 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 42 | NolanChai.nolan_1 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 43 | NotLLeon.player | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 44 | PSUtblock.sprint_four_player | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 45 | Patela171.Battlecode2023_Robot | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 46 | SDainard-PDX.Team_Player | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 47 | SampleProvider.SPAARK | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 48 | SampleProvider.SPAARK_1_12_2023 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 49 | ShatterXD.SRNNbot | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 50 | SteamBlizzard.Block | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 51 | SteamBlizzard.newVnewME | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 52 | Swordman51.AdeptusAstartes2 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 53 | TheK098.qp1_7_sprint_1 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 54 | VarunVejalla.karel | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 55 | Vinceyou1.Player1 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 56 | Yooncw0223.lec3player | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 57 | addiesteward.NDeClaw | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 58 | addiesteward.elicompbot | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 59 | aj-chau.attempt1 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 60 | andrewgopher.gopherbot | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 61 | andrewgopher.gopherbot1 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 62 | andrewkbank.First | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 63 | anicolao.jumbled | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 64 | anicolao.submission | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 65 | ax-95174.MPAction | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 66 | bewuwy.deathbot4 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 67 | elgoldie.head_v5 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 68 | ipince.bobby | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 69 | ipince.bobby_v2 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 70 | jyorkio.elicompbot | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 71 | kevinli405.maggi3 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 72 | kevinli405.maggi3_2 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 73 | legobridge.kushalplayer | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 74 | legobridge.tacoplayer | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 75 | louishu17.louisv10 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 76 | mama4294.currentPlayer | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 77 | mama4294.learningBot | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 78 | michael-tyl.cc_v0_5_0_6 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 79 | michael-tyl.hqrewrite | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 80 | monmouth-college-cs.elicompbot | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 81 | nail-e.Barry | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 82 | nail-e.Dante | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 83 | polyllc.poly | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 84 | prisms-cs-club.prisms10 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 85 | programjames.fourthbot | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 86 | team-remember-to-hydrate.sprint_1 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 87 | toyat522.bot5 | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
| 88 | vontell.regressiongames | 1406 | 409 | 2 | 0-2 | 100% (g_iter0 2-0*) |
