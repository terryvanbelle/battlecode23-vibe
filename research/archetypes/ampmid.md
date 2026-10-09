# arch_ampmid: S2 archetype (mana army with an amplifier at r36 that takes midfield)

Design: `docs/ARCHETYPES.md` section 4.5. Package `src/arch_ampmid/` (package `arch_ampmid`), telemetry build tag 105.
**Code hash 9b1099e4e1cf** (v4, the measured and delivered version). Member modelled: pranayagra.finalbotfinal (panel
matches 10, 199, 534, 600).

**Base.** The design builds it as arch_swarm plus edits, once arch_swarm is VALID. arch_swarm is not VALID: its builder
reports INVALID by one core metric (`eng_prog300`), with its 4-version budget spent (`research/archetypes/swarm.md`).
arch_ampmid forks the delivered arch_swarm v4c (b646f1e92c6b) anyway, because the failed metric is exactly what the
ampmid edits replace (where the army fights), and the coordinator dispatched this build. arch_swarm is itself a fork of
c_line6 (5bc8e7e545ac).

It was built only from observed behaviour (CLAUDE.md rule 3). The sources were:
- the member's 40 survey rows (scratchpad `games_sig.csv`, the survey's `sig.py` output) and `matches/10/extract/`
  (robots.csv birth rounds, timeline.csv, census `first_builds`);
- `research/matches/10.md`;
- `tools/replay-dump.sh --map-at` on `gauntlet/20261008-011350-panel1-g_iter0/replays/10.bc23` (DefaultMap game 3 at
  r40, r60, r100, r150, r200; Cat game 1 at r40, r80, r120, r160).

The signature numbers come from a stand-in for `tools/archsig.py`, which does not exist yet: the swarm builder's
`lsig.py` (the survey's per-game logic with the archetype as the subject) and an S2 aggregation with the section 2
rules and the section 3.4 tolerances. As a known-answer check, the stand-in run on the member's 40 survey rows
reproduces every member value in the section 4.5 table (amps 9.425, A250 3.23, first_eng_won 0.85, eng_prog300 0.476,
press250 34.5, ckill300 13.2, first_anchor 451, first_eng_dn 0.975, ...; `mn_share100` is n/a there because the survey
CSV has no such column). Treat the values as provisional until `archsig.py check` reproduces them. The stand-in lives
in the session scratchpad (`scratchpad/ampmid/lsig.py`, `acheck.py`, `fe.py` for first engagements), which is temporary.

**Verdict (my computation; `tools/archsig.py` does not exist yet): VALID, by the narrowest margin on one core metric.**
`first_eng_won` is 0.60 (12 of 20), exactly the faithful bound (0.8 − 0.25 × 0.8). In floating point,
0.8 − 0.25 × 0.8 is 0.6000000000000001, so a checker that compares raw floats rejects 12/20. `archsig.py check` has to
compare with a tolerance, or this verdict flips. One more lost first engagement also flips it. The 4-version budget is
spent.

| check | rule | result |
|---|---|---|
| fidelity | every core metric faithful | 12 of 12: pass (`first_eng_won` 0.60 at its bound) |
| fidelity | at least 75% of core metrics on target | 10 of 12 (83%): pass (off target: `first_eng_won` 0.60, `ckill300` 11.1) |
| fidelity | at least 50% of secondary metrics faithful | 10 of 10: pass |
| strength | g_iter0 wins 0-5 of 20 | 1 of 20: pass |
| strength | c_line6 wins 0-5 of 20 | 3 of 20: pass |
| robustness | 20 of 20 against examplefuncsplayer; no overruns, exceptions, self-deaths or wrong symmetry in any of the 60 games | 20/20; every count 0 (the bot's own `ov`/`ex` counters too): pass |

Runs (VM, the 20 screen cells, `SEED_MODE=map`, `MAXJOBS=2`, `CENSUS=1`, private `CLASSES`). They were fetched into
`gauntlet/` without replays; the replays stay on the VM.
- fidelity: `gauntlet/20261008-234912-ampmid-v4-fid` (`BOT=g_iter0`, `KEEP_ALL=1`, extracts in `extract/`);
- strength: `gauntlet/20261009-000239-ampmid-v4-str` (`BOT=c_line6`);
- robust: `gauntlet/20261009-001519-ampmid-v4-rob` (`BOT=arch_ampmid`, `OPPONENTS=examplefuncsplayer`).

Their provenance records `seed_mode=map` and `opp_hash.arch_ampmid=9b1099e4e1cf`, so the fidelity and strength runs
are also the screen cache's g_iter0 and c_line6 cells for this archetype hash.

## What it does

The archetype constants are in the `ARCHETYPE arch_ampmid (S2)` block at the top of `C.java`, each with the
observation that set it. The constants below that block are arch_swarm's, and the code inherits arch_swarm's
behaviour except for the edits listed here (`research/archetypes/swarm.md` describes the inherited part: the LLLL C
opening, the live-carrier cap, 30 kg loads, carrier unjam, cohesion, parity-hold micro, focus fire, the team target,
the carrier raid and the siege ring).

**Amplifiers (HQ)**
- HQ i (in `Comms` HQ_LOC order) builds its first amplifier from round 36 + 33 i: r36, r69, r102, r135. The member's
  first amplifier is born at r34-37 in 36 of its 40 games, and its next ones follow at about that spacing on 2-4 HQ
  maps (Cat r36/84, DefaultMap r34/66/151, Forest r36/76/111/162).
- Then one more per 15 launchers that HQ has built, at most ceil(12 / HQs) per HQ.
- The amplifier comes before launchers and carriers in the spend order, and its 30 Ad + 15 Mn are reserved while it
  is due: by HQ 0 from round 1, by the others from 10 rounds before.
- Before the approach round (below) an amplifier sits at the rally point; afterwards it does what arch_swarm's
  amplifier does (follows the centroid of the launchers it sees, keeps out of enemy reach).

**Economy (carriers)**
- One carrier in 6, by id, mines adamantium; the rest mine mana (arch_swarm: one in 8 on request, one in 4 from r200).
- A loaded carrier with an enemy fighter within r² 9 throws its load once its health is at most 110 (arch_swarm: 60).

**Launchers: midfield until r225, then arch_swarm's siege**
- Before r225 (`HQ_APPROACH_FROM`):
  - Objectives, in order:
    1. a shared enemy sighting within r² 64;
    2. an enemy-held island;
    3. a raid: when the launcher sees at least 4 of our launchers (itself included), the uncleared predicted enemy well
       in the enemy half nearest the rally point;
    4. the rally point, held within r² 10.
  - None of these may lie within r² 34 of a predicted enemy HQ, and marching never steps deeper into r² 34 of a seen
    enemy HQ (`Nav.avoidR2`).
  - The rally point is the midpoint between the team target (the predicted enemy HQ nearest our HQs' centroid) and our
    HQ nearest it. It is snapped once, when a launcher is within r² 64 of it, to the nearest tile known passable within
    Chebyshev 4.
  - "Enemy half" means nearer an enemy HQ than any of ours. A raided well reached with no enemy in sight is cleared for
    40 rounds, and the raider goes back to the rally point. The predicted wells are our known wells and their images
    under the decided symmetry.
  - A launcher at the rally point never counts as "forming" (arch_swarm's 4-to-leave rule near home).
- From r225: arch_swarm's objectives (sightings, enemy islands, the carrier raid on wells near the target HQ, the siege
  ring at r² 16-34).
- Micro: arch_swarm's, except that the step-in scoring applies from a local lead of 1 (allies in vision plus self minus
  enemy fighters ≥ 1) instead of 2.

**Islands.** Anchors from r425 (the design said r440; the target is the first anchor at r440-470, and placement lagged
the start by 28 rounds in v1 quick). Enemy islands are hunted from r0, as in arch_swarm, unless they lie in the
approach zone before r225.

**Deliberate deviations from the design sketch.** Each was forced by a measured failure:
- **No holding body at the rally point.** The sketch had launchers hold midfield, with groups of 3+ detaching to raid.
  - v1 kept 6 holders and let only the surplus raid. It raided too little: 8.8 of our carriers killed by r300 against
    the member's 13.2, and the first engagement won 0.5 against 0.85.
  - On Cat it lost: holding the rally point, the army lost the opening brawl 16 kills to 33, where the same launchers
    pushing into g_iter0's wells won it 19 to 7 (driver games 6 and 8).
  - The member's launchers on Cat were at our mana well (x 17-20 of 50) by r80.
  - So every group raids (3+ in v2-v3, 4+ in v4), and the rally point is where groups return to and where singles
    gather.
- **Approach at r225, not r150.** v2 quick (r150) pressed g_iter0's HQs for 370 launcher-buckets by r250 (median;
  member 34, target ≤ 100), with the siege arriving from r175. By the per-bucket pressure of v2's games, r225 puts the
  median near 70.
- **The approach zone is r² 34.** v1 kept objectives out of r² 50; v2 narrowed the zone to the pressure radius, r² 34,
  together with the raid change.
- **Amplifier rate.** The sketch said one per 3 launchers. The member builds 9.4 amplifiers per 190 launchers (0.05)
  and has 2-5 alive at r250, so one per 3 would hold 12 by r150. It is one per 15 launchers per HQ.
- **Adamantium share.** The sketch said one carrier in 3. In driver game 1 that gave Ad@100 222 (target 50-170); one in
  4 gave 215 in v1 quick. One in 6 gave 91.5 in v2 quick (member 122).
- **No sighting-defence radius.** v1 also answered every sighting within r² 144 of the rally point. v2 dropped it with
  the holders. Restoring it on top of v2's raids still lost DefaultMap B (driver game 13, as v2 had in game 12), so it
  stayed out.
- **Raids need 4, not 3** (v4). See the version table.

## Versions

Each version was measured on the screen cells (`SEED_MODE=map`, `MAXJOBS=2`, `CENSUS=1`). Quick runs are the
fidelity run only, on 10 cells (one side per map, alternating A and B in panel order). Runs were fetched without
replays, which stay on the VM.

| version | hash | run | core faithful / on target | secondary faithful | g_iter0 wins | what changed |
|---|---|---|---|---|---|---|
| v1 | 2f90868f73c6 | quick, `20261008-204934-ampmid-v1q-fid` | 9/12, 5/12 | 9/10 | 1/10 | fork of arch_swarm v4c plus the design edits: amplifiers (r36 + 33 per HQ index, 1 per 15 launchers, 12 per game), 1 carrier in 4 on Ad, AHEAD_MIN 1, anchors from r410, midfield until r150 (rally point = midpoint between the team target and our nearest HQ, 6 holders, surplus groups of 3 raid enemy-half wells outside r² 50 of enemy HQs, sightings within r² 144 of the rally point answered). **203 overruns, 1 exception** (the rally-point snap searched an 11 × 11 square with one bytecode check per ring) |
| v2 | 7ac8e45909de | quick, `20261008-211044-ampmid-v2q-fid` | 11/12, 8/12 | 10/10 | 1/10 | every group of 3+ raids (no holders), approach zone r² 34, no sighting-defence radius, lazy perimeter snap, 1 carrier in 6 on Ad, first amplifier's cost reserved 10 rounds ahead, anchors from r425. 0 overruns. Failed `press250` (370: the siege from r150 reached the victim HQs from r175) |
| v3 | 4020df441a43 | full, `20261008-214231/221810/224730-ampmid-v3-{fid,str,rob}` | 11/12, 10/12 | 10/10 | 2/20; c_line6 3/20 | approach (siege) from r225; HQ 0 reserves the first amplifier from round 1 (v2: Cornucopia's first amplifier at r111); carriers throw at health ≤ 110. Failed only `first_eng_won` (0.55, faithful from 0.60) |
| v4 | 9b1099e4e1cf | full, `20261008-234912/20261009-000239/20261009-001519-ampmid-v4-{fid,str,rob}` | 12/12, 10/12 | 10/10 | 1/20; c_line6 3/20 | raids need 4 launchers in vision instead of 3 |

Driver diagnostics (one game at a time, `tools/lib.sh run_game`, the map's own seed, so each one replays the VM cell
exactly; the v4 VM games matched the driver's):
- **Rally point and cohesion** (DefaultMap, games 1-3 and 12-14):
  - Game 1: the first rally point lay within r² 50 of one of the archetype's HQs, so the group holding it counted as
    "forming" and walked home. Regroup took 23% of launcher turns, and the game was lost at r281.
  - Game 2: the midpoint of the two teams' HQ centroids lay in a cloud 12 tiles from the fighting. Lost at r324.
  - Game 3 (the team-target midpoint, with the forming fix): won at r637.
  - Games 12-14 (v2): side B lost at r404 without the sighting radius and lost with it; side A won.
- **Hold against push** (Cat B, games 4-9):
  - Holding the rally point lost the opening brawl. Games 4, 5, 7 and 8 all lost, whether the step-in threshold was +1
    or +2, with or without the sighting radius, and whatever a lone launcher did (went to the rally point or home).
  - The same code marching straight at the enemy HQ (`HQ_APPROACH_FROM = 0`, game 6) won the brawl 19 kills to 7.
  - Raiding g_iter0's wells (game 9) won at r751.
  - Game 11 (v2 on Cat B against c_line6) also won.
- **Probes of v3's cells for `first_eng_won`.** v3 lost 9 of its 20 first engagements.
  - `AHEAD_MIN` 2 on 8 cells: no first engagement changed.
  - A lone launcher going to the rally point instead of home, on 4 cells: no first engagement changed.
  - `GROUP_MIN` 5 on 12 cells: 4 first engagements turned into wins and 4 into losses. Hah A, Hah B and Cat B were
    lost as games: the first wave left later and g_iter0 reached the archetype's carriers.
  - `RAID_GROUP` 4 on 10 cells: DefaultMap B's first engagement turned from a 2-1 loss into a 5-3 win, and nothing else
    changed. This became v4.

## Signature against the targets (v4, 20 fidelity games against g_iter0)

"member" is the design's member value (section 4.5). Faithful means within the range widened by 25% (section 3.4).

| id | core | target | member | arch_ampmid | on target | faithful |
|---|---|---|---|---|---|---|
| amp_early | core | 0.9 - | every game, r36 | 0.950 | yes | yes |
| A250 | core | 3 - | 3.2 | 3.4 | yes | yes |
| amps | core | 6 - 12 | 9.4 | 8.7 | yes | yes |
| mn100 | core | 250 - 560 | 305 [244-562] | 376.5 | yes | yes |
| ad100 | core | 50 - 170 | 122 [48-167] | 111.5 | yes | yes |
| L100 | core | 12 - 17 | 13.5 | 13 | yes | yes |
| L250 | core | 20 - 40 | 28 [20.5-39.5] | 23 | yes | yes |
| first_eng_won | core | 0.8 - | 0.85 | 0.600 | no | yes |
| eng_prog300 | core | 0.42 - 0.52 | 0.48 | 0.519 | yes | yes |
| press250 | core | - 100 | 34 | 5 | yes | yes |
| ckill300 | core | 12 - | 13.2 | 11.1 | no | yes |
| first_anchor | core | 440 - 470 | 451 | 462 | yes | yes |
| first_eng_dn |  | 0.75 - | 0.98 | 1 | yes | yes |
| throws |  | 5 - 9 | 7.1 | 6.3 | yes | yes |
| mn_share100 |  | 0.6 - 0.85 | 0.70 | 0.735 | yes | yes |
| conquest_round |  | 570 - 820 | 645 | 701 | yes | yes |
| first_press |  | 150 - | 200 | 200 | yes | yes |
| exposed |  | - 0.02 | 0.012 | 0.015 | yes | yes |
| group |  | 7 - | 15.5 | 10.5 | yes | yes |
| ahead_share |  | 0.6 - | 0.70 | 0.660 | yes | yes |
| ckill150 |  | 3 - | 4.1 | 4.0 | yes | yes |
| first_contact |  | - 30 | 23 | 21 | yes | yes |

**Robustness and strength (v4):**
- fidelity, against g_iter0: g_iter0 wins 1 of 20 (Cat, archetype on A, r327). Band 0-5: pass.
- strength, against c_line6: c_line6 wins 3 of 20 (Cat r334, Cornucopia r523 and IslandHopping r462, with
  the archetype on sides A, B and A). Band 0-5: pass.
- robust, against examplefuncsplayer: 20 of 20, rounds 520-1186.
- In all 60 games: census `over` 0, `exceptions` 0, `deaths_self` 0, `sym_wrong` 0; the bot's own `ov`/`ex` counters 0.
- No coin-flip games.
- Near misses (they do not gate):
  - the census `near` column (turns at 90% or more of the limit, counted from the replay) totals 2,198
    (fidelity), 2,062 (strength) and 8,313 (robust: long games with large armies), against g_iter0's 820 and
    c_line6's 2,648;
  - the bot's own `nm` counter reads 0, 0 and 2,257.

## Remaining gaps

- **`first_eng_won` 0.60 against the member's 0.85.**
  - It is the weakest metric: it sits at the faithful bound and below the target.
  - The losses:
    - BatSignal B, 3v4 (one of the first four walked home after losing sight of the others);
    - Forest A and B (3v4, and 5v1 that became 2v7 in the clouds);
    - MassiveL A and B (4v4 decided on damage after 3 kills each; 2v4);
    - Maze A (a one-round hit on a carrier at r4, no deaths, decided on damage);
    - Maze B and Cat A (g_iter0's first launchers among the archetype's carriers: 6 and 12 of them died in those
      engagements).
  - In match 10 the member started 6 of its 10 first fights 1-2 launchers ahead (4v3, 4v3, 4v2, 4v2, 4v2, 3v1).
    g_iter0's launchers reach the archetype's first wave of 4 while they are still together.
  - Of the levers tried, only raids needing 4 (v4) raised it without losing games, and only by one engagement. The
    step-in threshold and a lone launcher going to the rally point changed nothing; a 5-launcher first wave lost
    games.
- **`ckill300` 11.1** (target 12, faithful from 9).
  - g_iter0's carriers die mostly to the siege after r225, and the count is 0-6 on Forest, MassiveL and
    ReverseFunnel.
  - The member kills 13.2, many of them at the victim's wells before r225 on the small maps.
- **The approach round is r225, not the design's r150.** The member's first pressure on our HQs scales with the HQ
  distance:
  - r50-125 on DefaultMap, Maze, Cat and Cornucopia (10-22 tiles);
  - r175-350 on the 29-53-tile maps.
  - A fixed r225 matches the median (first_press 200) and `press250` (5, member 34), but not the per-map shape. On Cat
    and DefaultMap the member pressed g_iter0's HQs for 1,170 and 1,989 launcher-buckets by r250; the archetype
    presses 0-2,795 there.
- **`eng_prog300` 0.519** is at the top of its range (0.42-0.52).
  - On Forest and MassiveL B the fights before r300 are on the archetype's side (0.65-0.72).
  - With raids on Cat B and IslandHopping they are on g_iter0's side (0.25-0.30).
- **Cat with the archetype on side A** is lost to g_iter0's anchor rush at r327. The opening brawl is lost 15
  launchers and 12 carriers to 13 launchers, and g_iter0 anchors 5 of 6 islands. The member never lost Cat (4 of 4).
  - Strength still passes: 1 of 20 against g_iter0, 3 of 20 against c_line6.
- **Not modelled:** the member's amplifier counts on MassiveL (28-31 per game; the archetype caps at 12, as the design
  says) and its Cornucopia first amplifier (r76-111; the archetype reserves for r36).
- **Inherited from arch_swarm:** the base is not VALID itself (its `eng_prog300`), and the near-miss load above.
