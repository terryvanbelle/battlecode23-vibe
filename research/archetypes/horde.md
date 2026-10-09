# arch_horde: S3 archetype (balanced horde with throws, late amplifiers and island holding)

Design: `docs/ARCHETYPES.md` section 4.4. Package `src/arch_horde/` (package `arch_horde`), a fork of `src/c_line6`
(5bc8e7e545ac), telemetry build tag 104. **Code hash 82311f9b016d** (v4, the measured version). Member modelled:
georgezhang02.CB_tuning2 (panel matches 8, 197, 532, 598).

It was built only from observed behaviour (CLAUDE.md rule 3). The sources were:
- the member's census, timeline, deaths and engagement rows in `matches/{8,197,532,598}/extract/`;
- `research/matches/8.md`;
- `tools/replay-dump.sh --map-at` and `--islands` on `gauntlet/20261008-011350-panel1-g_iter0/replays/8.bc23`
  (DefaultMap game 3 and Forest game 4).

**Verdict (my computation; `tools/archsig.py` does not exist yet): INVALID on fidelity by one core metric, by 0.1.
The 4-version budget is spent.** The failed metric is `throws`: a mean of 22.4 throws a game against a target of ≥ 30.
The faithful bound is 22.5.

| check | rule | v4 result |
|---|---|---|
| fidelity | every core metric faithful | 11 of 12: **fail** (`throws` 22.4, faithful from 22.5) |
| fidelity | at least 75% of core metrics on target | 11 of 12 (92%): pass |
| fidelity | at least 50% of secondary metrics faithful | 12 of 12: pass |
| strength | g_iter0 wins 0-7 of 20 | 5 of 20: pass |
| strength | c_line6 wins 0-7 of 20 | 7 of 20: pass (at the band's edge) |
| robustness | 20 of 20 against examplefuncsplayer; no overruns, exceptions, self-deaths or wrong symmetry in any of the 60 games | 20/20; every count 0, bot counters `ov`/`ex` included: pass |

The previous version, v3 (5df4fee1c068), had the opposite result. Fidelity passed: 12 of 12 core faithful, 11 of 12 on
target, 11 of 12 secondary faithful. Strength failed against c_line6 by one game: c_line6 won 8 of 20. v4 is the one
left in `src/`, because a partner that is too weak misleads (section 0).

The metric values come from a stand-in for `archsig.py`, the scratchpad script `horde/horde_sig.py`. It applies the
survey's `sig.py` column definitions per game, with the archetype as the subject, and then the section 2
aggregations and the section 3.4 tolerance rules. Known-answer check: run on the member's 40 panel games
(`matches/{8,197,532,598}/extract --subject georgezhang02`), it reproduces all 24 values in the member column of section
4.4. Two examples: `tb_share` 15/33 = 0.455 and `ahead_share` pooled 0.790. Treat the values as provisional until
`archsig.py check` reproduces them.

Runs (VM, `SEED_MODE=map`, `MAXJOBS=2`, `CENSUS=1`, the 20 screen cells):
- The fidelity and strength runs were split in two:
  - the `--quick` 10 cells: g_iter0 on A on the even panel maps, B on the odd ones;
  - their complement: the other side of every map.

  Games are deterministic per (code hash, cell, seed), so the two halves together are the 20-cell run. Every run below
  played hash 82311f9b016d.
- fidelity (`BOT=g_iter0`, `KEEP_ALL=1`, extracts in `extract/`): `gauntlet/20261008-213238-horde-v4q` +
  `gauntlet/20261008-214602-horde-v4c-fid`;
- strength (`BOT=c_line6`, `KEEP_ALL=1`, extracts): `gauntlet/20261008-213251-horde-v4s` +
  `gauntlet/20261008-214618-horde-v4c-str`;
- robust (`BOT=arch_horde`, `OPPONENTS=examplefuncsplayer`, 20 cells): `gauntlet/20261008-214624-horde-v4c-rob`.

The runs live on the VM. Copies without replays are in the session scratchpad, under `horde/runs/`. The VM keeps
replays for v4 only; v1-v3 replays were pruned when the VM disk reached 93%.

## What it does

The archetype constants are in the `ARCHETYPE arch_horde (S3)` block at the top of `C.java`. Every base constant it
changes is marked `arch_horde`. Each constant carries the observation that set it.

**Opening and production (`HQ.build`)**
- On maps with min(W, H) ≥ 40, round 1 is carriers only: 4 per HQ (`BIG_MAP`).
  - The member's first builds on Maze, Forest, Cat, Cornucopia and MassiveL were CCCC per HQ on r1, then LLLL on r2,
    in all 20 games.
- On smaller maps, round 1 builds launchers first and then one carrier: LLLLC per HQ.
- After round 1, the build order is:
  1. a carrier, when Ad ≥ 50 and the team is under the live-carrier cap;
  2. an amplifier, when one is due;
  3. a launcher, whenever Mn ≥ 45.
- Amplifiers: none before r260 (`AMP_START`). After that, one per 7 launchers that the HQ has built since r260
  (`AMP_PER_L`). The design says one per 4, but at 4, v2 built 54 a game and 207 on Cornucopia, against the member's
  26.6. Amplifiers escort the launchers (base `Amplifier`).
- `HQ_THREAT = 1`: the HQ keeps building unless it is in real danger.
- The early cap is gone (`EARLY_CAP_UNTIL = 0`).

**Carrier cap**
- The cap counts live carriers, from a census in the shared array (slots 62-63, as arch_swarm's). Each carrier counts
  itself once per 64-round epoch.
- The cap is max(6 per known well, 6 per HQ) plus 1 per HQ every 100 rounds, at most 150 (`CARRIERS_PER_WELL`,
  `CARRIER_MIN_PER_HQ`, `CARRIER_GROW`, `CARRIER_MAX`).
- Why the growth term: v1 used a fixed 6 per well and froze Forest at 65 carriers built from r300, with 4,000 Ad
  unspent. The member's live carriers keep growing, to 120-860 by r2000.

**Economy (`ROLES = 4`)**
- One carrier in 4 (by id) mines adamantium; the others mine mana.
- A carrier whose type has no known well searches for one. Its first search target is toward the map centre, at most
  12 tiles from home (`EXPLORE_FIRST`).
- From r100 a carrier switches, at delivery, to whatever its HQ is short of (the base rule).
- **Throws** (`hordeThrow`): a carrier holding at least 20 throws its load at an enemy launcher within r² 9. Failing a
  launcher, it throws at a carrier, then an amplifier, lowest health first. It throws only when one of our launchers is
  in its vision or its own health is ≤ 90. It then goes back to mining.
- The base's cornered throw (health ≤ 60) is unchanged.

**Islands**
- Anchors start at r290 (`ANCHOR_START`), as the design specifies.
- A team anchor clock (shared slot 61) then spaces them:
  - the n-th next anchor waits `100 + 60·(n-1)` rounds after the previous one (`ANCHOR_GAP0`, `ANCHOR_GAP_STEP`);
  - while the enemy holds 2 or more islands, the gap is the per-HQ `ANCHOR_PERIOD` of 30 instead
    (`HURRY_ENEMY_ISLANDS`).

  This slows anchoring as the game goes on. The member placed 3-10 anchors a game, at a slowing pace (DefaultMap:
  r298, 387, 568, 1184). It held 4 of the 6 islands from r1000 to r2000, so 15 of its 33 wins came on the r2000 island
  tiebreak. With the base's per-HQ period of 30, v1 conquered at r509-566 and its tb_share was 0.
- Anchors go on until every island is held (the base `islandToTake`).

**Launchers**
- Garrison (`GARRISON_MOD = 3`): one launcher in 3 (by id) holds one of our islands, spread over the islands by id. It
  stands on a free square, which heals the anchor and blocks the square. It leaves only for a fresh sighting within
  r² 64 of its island.
- The other launchers pick objectives in this order:
  1. a sighting within r² 100 of one of our HQs (home defence);
  2. an enemy-held island, using the launcher's own sighting from the last 100 rounds when the shared slot does not say
     the island is ours (`OWN_ISLAND_MEMORY`);
  3. any other fresh sighting;
  4. the predicted enemy HQ, held at r² ≤ 16 outside its aura. The spawn kills come from there (48 a game).
- Micro: `MICRO2` (parity hold) is on. Cohesion `ARMY` is off, because in v1 Forest it spent 23,747 launcher turns
  regrouping and the army held our half all game. The horde still fights in groups: group size 15 against the
  member's 12.5.

Telemetry is on (`TELEMETRY = true`, `TELE_BUILD = 104`).

**Deliberate deviations from the design sketch.** Each was forced by a measurement:
- The anchor clock is slow and team-wide, where the design says only "anchors continue until every island is held".
  Without it, conquests came at r509-566, tb_share was 0 and isl_rounds was 718 (v1).
- There is one amplifier per 7 launchers, not per 4: see the opening and production section above.
- Roles are 1 in 4 on adamantium, not the base's balance:
  - with the base rule (v1), the Mn share was 0.41;
  - with the nearest well's type (v2), Maze and Cat mined 0 Mn by r100;
  - with 1 in 3 plus a fallback to the other type (v3), mana was too thin on DefaultMap: 439 against g_iter0's 694 at
    r100.
- Enemy islands come before ordinary sightings. In v1 Hah, g_iter0 anchored 3 of 4 islands by r278 while our
  launchers chased sightings.
- The carrier cap grows with time (see the carrier cap section above).

**Known stale comment:** the `ROLE_AD_EVERY` javadoc in `C.java` still says "a carrier whose type has no known well
takes the other type". That was v3; v4 searches instead (see `Carrier.hordeRole`). It was left unchanged so that the
code hash stays the measured one. Fix it at the next code change, which needs a revalidation anyway.

## Versions

| version | hash | runs | core faithful / on target | secondary faithful | victim wins: g_iter0; c_line6 | what changed |
|---|---|---|---|---|---|---|
| v1 | (not kept) | quick, `gauntlet/20261008-193028-horde-v1q` | 8/12, 6/12 | 9/12 | 4/10; - | fork plus the design behaviour: opening by map, 6 live carriers per well (census), amplifiers from r260 at 1 per 4, throws, garrison, `ARMY` and `MICRO2` on, `HQ_THREAT = 1` |
| v2 | 4d9f93f73048 | quick, `...-194922-horde-v2q`, `...-195230-horde-v2s` | 12/12, 11/12 | 11/12 | 3/10; 7/10 | team anchor clock; `ARMY` off; enemy islands before sightings; cap grows 1 per HQ per 100 rounds; roles by the nearest well's type |
| v3 | 5df4fee1c068 | full (quick + complement), `...-202207-horde-v3q`, `...-202209-horde-v3s`, `...-205306-horde-v3c-fid`, `...-205318-horde-v3c-str` | 12/12, 11/12 | 11/12 | 6/20; **8/20** | roles 1 in 3 on Ad, falling back to the other type when no well of the own type is known; balance from r100; amplifiers 1 per 7 |
| v4 | 82311f9b016d | full, `...-213238-horde-v4q`, `...-213251-horde-v4s`, `...-214602-horde-v4c-fid`, `...-214618-horde-v4c-str`, `...-214624-horde-v4c-rob` | 11/12, 11/12 | 12/12 | 5/20; 7/20 | no type fallback (search toward the centre); roles 1 in 4 on Ad; launchers' own island memory; anchor hurry while the enemy holds 2+ islands |

v3 lost to c_line6 by early conquest on maps where the opening HQs saw only adamantium wells. Every opening carrier
then mined Ad: on Maze, 0 Mn by r25 against c_line6's 62. c_line6 conquered Maze at r213 and Hah at r284. v4 fixed
the mana and won both of those cells. In exchange it mined less Ad and threw less in the long Forest and MassiveL
games: Forest went from 105-108 throws to 60, and both MassiveL games ended early.

A v3 robust run (`...-205324-horde-v3c-rob`) was stopped after 10 of 20 games, all won, once v3 was superseded.

Driver diagnostics: one game on Forest against g_iter0 (v1), which showed the cohesion regroup holding the army at home.
A second driver game was skipped because another builder's game held the driver.

## Signature against the targets (v4, 20 fidelity games against g_iter0)

"members" is the member's value from the design (section 4.4): median [IQR] over its 40 panel games. Faithful means
within the range widened by 25% (section 3.4).

| id | core | target | member | arch_horde v4 | on target | faithful | v3 (for reference) |
|---|---|---|---|---|---|---|---|
| open_rule | core | 0.80 - | by construction | 1.00 | yes | yes | 1.00 |
| mn_share100 | core | 0.40 - 0.60 | 0.49 [0.31-0.71] | 0.589 | yes | yes | 0.455 |
| ad250 | core | 650 - | 1172 [662-1540] | 1028 | yes | yes | 1477 |
| C250 | core | 30 - | 31.5 [14.5-40.5] | 34 | yes | yes | 38 |
| L250 | core | 13 - 35 | 22.5 [12.8-34.8] | 23.5 | yes | yes | 18 |
| amps | core | 20 - | 26.6 | 35.5 | yes | yes | 37.2 |
| first_A | core | 260 - | 428 [262-477] | 321 | yes | yes | 319 |
| throws | core | 30 - | 46 | **22.4** | no | **no** (from 22.5) | 29.1 |
| throw_kills | core | 3 - | 3.6 | 3.45 | yes | yes | 4.95 |
| isl_rounds | core | 2000 - | 2020 | 2685 | yes | yes | 2515 |
| first_anchor | core | 290 - 460 | 350 | 327 | yes | yes | 331 |
| tb_share | core | 0.40 - | 15/33 = 0.45 | 7/15 = 0.467 | yes | yes | 0.429 |
| mn100 |  | 240 - 440 | 370 [238-440] | 428 | yes | yes | 322 |
| ad100 |  | 180 - 470 | 354 [177-472] | 266 | yes | yes | 377 |
| L100 |  | 6 - 13 | 10 [6-13] | 11 | yes | yes | 7 |
| C100 |  | 12 - 20 | 16 | 14 | yes | yes | 16.5 |
| cpw |  | 4 - 6 | 5 | 4 | yes | yes | 4 |
| spawn_kills |  | 25 - | 38 | 48 | yes | yes | 37.6 |
| eng_prog300 |  | 0.33 - 0.47 | 0.40 | 0.331 | yes | yes | 0.373 |
| group |  | 8 - | 12.5 | 15 | yes | yes | 14 |
| exposed |  | - 0.015 | 0.010 | 0.004 | yes | yes | 0.005 |
| ahead_share |  | 0.70 - | 0.79 | 0.759 | yes | yes | 0.700 |
| first_press |  | 100 - 150 | 125 | 100 | yes | yes | 62.5 (miss) |
| conquest_round |  | 700 - 950 | 828 | 652 | no | yes | 1132 |

Throws per cell, v4 (v3 in brackets):
- Forest 60/60 (108/105), DefaultMap 87/52 (50/18), Maze 50/39 (47/38), Cornucopia 28/43 (71/37);
- every other map 0-6.

The member's throws are also concentrated in long games: DefaultMap 112-209, ReverseFunnel 97-222 in its three r2000
games, Forest 19-56, BatSignal 0, Hah 0-7. Our ReverseFunnel fidelity games end by conquest at r660 and r794, while
three of the member's four went to r2000.

## Strength

| victim | wins (of 20) | band | cells the victim won |
|---|---|---|---|
| g_iter0 | 5 | 0-7 | Forest A and B (r2000, islands tiebreak), MassiveL A and B (conquest r598, r872), ReverseFunnel B (conquest r794) |
| c_line6 | 7 | 0-7 | Forest A and B (r2000 tiebreak), MassiveL A and B (conquest r645, r1983), ReverseFunnel A and B (r889, r1175), DefaultMap A (conquest r421) |

No coin-flip games. The per-map pattern differs from the member's. The member lost Cat to every one of our builds
(4 of 4) and won Forest 4 of 4. arch_horde wins Cat 4 of 4 and loses Forest 4 of 4, always at r2000 on the
tiebreak (once on anchors placed, against c_line6). Against all four of our builds, the member's victim share was
0.175 over its 40 panel games.

## Robustness

- Robust run: 20 of 20 wins against examplefuncsplayer. 13 came on the r2000 island tiebreak, 6 by conquest and 1 on
  the mana tiebreak. The slow anchor clock rarely reaches 75% of the islands against an opponent that does not fight.
- In all 60 games: census `over` = 0, `exceptions` = 0, `deaths_self` = 0, `sym_wrong` = 0. The bot's own `ov=`/`ex=`
  counters are also 0.
- Near misses are reported but do not gate. There were 8,266 in the 20 fidelity games: launchers 5,443, amplifiers
  1,613, carriers 1,210, HQs 0. The two Cornucopia games, with their large armies, account for 2,483 and 3,071. On the
  same cells the victims had far fewer: g_iter0 878, and c_line6 2,338 in the strength games. The horde's crowded
  vision is a bytecode risk to watch, although no turn overran.

## Remaining gaps

1. **`throws` 22.4 against ≥ 30 (faithful from 22.5): the only failed bar.** A cheap fix, for a future revalidation
   only, is a lower `THROW_LOAD`, or throwing also when an enemy launcher is adjacent to an allied carrier. v3 threw
   29.1 a game with the same rule; v4's shorter games and its mana-heavier carriers threw less.
2. `conquest_round` 652 against 700-950. It is faithful, but our conquests on 4-island maps (BatSignal, Hah) come at
   r620-650, before the member's r820-877 on BatSignal.
3. The map pattern is not the member's: Cat is ours and Forest is the victim's. The aggregate strength is in the band.
   Treat a regression signal concentrated on Forest or Cat with care.
4. The strength against c_line6 sits at the band's edge: 7 of 20. A small policy change could tip it to INVALID.
5. `tools/archsig.py` does not exist yet. These numbers come from the stand-in, which reproduces the member column
   exactly. `archsig.py check` must confirm them before any record is written.
