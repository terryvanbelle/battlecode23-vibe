# arch_swarm: S1 archetype (early mana swarm that besieges the HQ)

Design: `docs/ARCHETYPES.md` section 4.1. Package `src/arch_swarm/` (package `arch_swarm`), a fork of `src/c_line6`
(5bc8e7e545ac), telemetry build tag 101. **Code hash b646f1e92c6b** (v4c, the measured and delivered version).
Members modelled: vrangr1.AFinalsBot, awesomelemonade.finalBot, jmerle.camel_case_v30_final (the model) and
NotLLeon.v7. The `SWARM_DIVE` switch (vrangr1's amplifier at about r111) is not built.

It was built only from observed behaviour (CLAUDE.md rule 3), using these sources:
- the survey rows of the 160 member panel games (scratchpad `games_sig.csv`);
- `matches/7/extract/*.csv`: jmerle against g_iter0, in particular DefaultMap game 3 (timeline, trips, engagements);
- the Cat games of matches 6, 9 and 18 (vrangr1, awesomelemonade, NotLLeon against g_iter0);
- `research/matches/7.md`;
- `tools/replay-dump.sh --map-at` on `gauntlet/20261008-011350-panel1-g_iter0/replays/7.bc23`.

**Verdict (my computation; `tools/archsig.py` does not exist yet): INVALID on fidelity, by one core metric. The
4-version budget is spent.** The failed metric is `eng_prog300`: 0.444 against a target of ≤ 0.35, and the faithful
bound is 0.4375.

| check | rule | result |
|---|---|---|
| fidelity | every core metric faithful | 11 of 12: **fail** (`eng_prog300` 0.444) |
| fidelity | at least 75% of core metrics on target | 10 of 12 (83%): pass |
| fidelity | at least 50% of secondary metrics faithful | 19 of 19: pass |
| strength | g_iter0 wins 0-5 of 20 | 1 of 20: pass |
| strength | c_line6 wins 0-5 of 20 | 5 of 20: pass (at the band's edge) |
| robustness | 20 of 20 against examplefuncsplayer; no overruns, exceptions, self-deaths or wrong symmetry in any of the 60 games | 20/20; every count 0 (bot counters `ov`/`ex` included): pass |

Runs (VM, `SEED_MODE=map`, `MAXJOBS=2`, `CENSUS=1`, the 20 screen cells; fetched without replays, which stay on the
VM):
- fidelity: `gauntlet/20261008-183419-swarm-v4c-fid` (`BOT=g_iter0`, `KEEP_ALL=1`, extracts in `extract/`);
- strength: `gauntlet/20261008-184743-swarm-v4c-str` (`BOT=c_line6`);
- robust: `gauntlet/20261008-190334-swarm-v4c-rob` (`BOT=arch_swarm`, `OPPONENTS=examplefuncsplayer`).

The metric values come from a stand-in for `archsig.py`. It applies the survey's `sig.py` logic per game, with the
archetype as the subject, and then the section 2 aggregations and the section 3.4 tolerance rules. Treat them as
provisional until `archsig.py check` reproduces them.

## What it does

All archetype constants are in the `ARCHETYPE arch_swarm (S1)` block at the top of `C.java`. Every base constant it
changes is marked `arch_swarm`. Each constant carries the observation that set it.

**Production (HQ)**
- A launcher whenever Mn ≥ 45, then a carrier whenever Ad ≥ 50 and the team is under the carrier cap. No amplifiers.
- So round 1 is 4 launchers then 1 carrier per HQ, and round 2 spends the remaining 150 Ad on 3 carriers. Every S1
  member opens LLLL C.
- Anchors start at r250, once the HQ has built 12 launchers. g_iter0's early carrier cap and its r120 anchor rush are
  gone (`EARLY_CAP_UNTIL = 0`). `HQ_THREAT = 1`.
- The carrier cap counts live carriers for the whole team: the larger of 8 per known mana well and (6 + round/50) per
  HQ, at most 30.
  - Live carriers come from a census in the shared array, slots 62 and 63. Each carrier adds 1 per 64-round epoch,
    at its first turn with write access.
  - Slot 61 holds one bit per HQ: "wants adamantium", set when the HQ has Ad < 50 and the cap has room.

**Economy (carriers, `ROLES = 3`)**
- Carriers mine mana. The exceptions are one carrier in 8 (by id) while its HQ's bit is set, and from r200 one
  carrier in 4, to fund anchors.
- Loads are 30 kg, as jmerle's are: 42 of its 47 deposits by r120 on DefaultMap were 30 kg, with a trip cycle of 36
  rounds against 54 for 40 kg loads.
- A mana carrier switches only to another mana well. If its well is crowded and no other is known, or it knows none
  at all, it searches toward the map centre first.
- A carrier that has not moved for 5 turns while travelling or waiting steps to a random free tile (`unjam`).

**Launchers**
- Cohesion (`ARMY`):
  - Within r² 50 of home, a launcher waits until 4 launchers are in vision (2 if it stands in a cloud).
  - In the field a pair counts as a group. Only a launcher with no ally in sight goes back.
  - It follows the lowest-id launcher in vision when farther than r² 8.
  - Home defence applies only to sightings within r² 20 of one of our HQs.
- Objectives, in order:
  1. a shared sighting within r² 64;
  2. enemy-held islands, from r0, using the launcher's own sighting when the shared slot is empty;
  3. the carrier raid, once the symmetry is decided: predicted enemy wells within r² 100 of the target HQ, nearest to
     that HQ first. A well seen empty is skipped for 40 rounds.
  4. the siege ring: hold at r² 16-34 from the target HQ, outside its aura, once that HQ has been seen.
- There is one team target: the enemy HQ nearest the centroid of our HQs, ties broken by location, so that every group
  agrees on it. Rotating the target was tried and is off (`SIEGE_ROTATE_FROM = 2000`).
- Micro:
  - When the launcher is ahead by 2 or more (allies in vision + 1 - enemy fighters), it uses g_iter0's step-in scoring.
  - Otherwise it holds parity. It fires only from a tile that at most one enemy can reach and that is no more exposed
    than its current tile. With no such tile, it falls back away from the enemy, toward the centroid of our launchers
    (else home).
  - It never ends a turn inside an enemy HQ aura unless the shot from there kills. While marching, tiles within r² 9 of
    a seen enemy HQ count as walls.
- Focus fire: launchers first (lowest HP, then lowest id), then carriers holding anchors, then carriers, then
  amplifiers.

Telemetry is on (`TELEMETRY = true`). The FIGHT record's "micro" bit carries the archetype's `ahead` flag.

**Deliberate deviations from the design sketch.** Each was forced by a measured failure:
- Enemy islands are hunted from r0, not r250. v2 lost ReverseFunnel by conquest at r224 to g_iter0's anchor rush.
- There is one team target instead of each HQ's nearest enemy HQ. On Cat in v3, each HQ's first four launchers went
  to a different enemy HQ, and both groups lost at parity: 18 kills against our 6. In matches 6, 9 and 18 the members
  brought 8 launchers to the one fight and won it 13-17 kills to 3-6.
- `GROUP_MIN = 4` applies only while forming near home. In v3, requiring 4 in the field made launchers regroup in 44-53%
  of their opening turns, and on Cat 44% of their contact turns were fought alone.
- The carrier cap is looser than "4 per known mana well, at least 4 per HQ". With that rule, v1 held DefaultMap at 12
  carriers until r100 with 480 Ad banked. The members build a carrier from every bit of Ad they receive: jmerle on
  DefaultMap had 18 carriers by r100 and 27 by r250, with Ad@100 = 1.

## Versions

| version | hash | run | core faithful / on target | secondary faithful | victim (g_iter0) wins | what changed |
|---|---|---|---|---|---|---|
| v1 | 89ebc741b246 | quick, `gauntlet/20261008-143812-swarm-v1q` | 7/12, 4/12 | 13/19 | 5/10 | fork plus the design behaviour. After three driver games: cap 8 per mana well and 6 per HQ, census uses the current count in the second half of an epoch, 1 in 8 on Ad, 30 kg loads |
| v2 | 029fda035e71 | quick, `...-151132-swarm-v2q` | 8/12, 6/12 | 15/19 | 5/10 | home defence r² 100 → 20 (lone launchers chased every sighting near three HQs: alone 0.32, exposed 0.18); fallback away from the enemy; mana carriers switch only to mana wells (v1 Ad@100 164) |
| v3 | 0b6fad85526c | quick, `...-154936-swarm-v3q` | 11/12, 7/12 | 19/19 | 2/10 | pair counts as a group in a cloud (Forest); islands hunted from r0; raid only once the symmetry is decided, approach a predicted HQ until it is seen (Cat: the raid walked to rotation images); mana search toward the centre (Cornucopia: 13 of 28 early trips died while exploring) |
| v4 | bed7677f805f | quick, `...-161550-swarm-v4q` | 12/12, 8/12 | 18/19 | 0/10 | team target; 4 to form at home, pairs in the field; carrier unjam (MassiveL: 8 of 12 carriers never moved again); cap grows 1 per HQ per 50 rounds; mana carriers search when crowded. **825 caught exceptions** |
| v4b | ff6fb9cb54f6 | full, `...-170216-swarm-v4b-{fid,str,rob}` | 11/12, 10/12 | 19/19 | 1/20; c_line6 5/20 | null guard for the well that `switchWell` drops (the source of all 825 exceptions). **Launcher overruns on Cornucopia: 11 + 59 + 18** |
| v4c | b646f1e92c6b | full, `...-183419/184743/190334-swarm-v4c-*` | 11/12, 10/12 | 19/19 | 1/20; c_line6 5/20 | bytecode guards in `computePredWells` (12 wells × 48 candidates × dedup). 0 overruns and 0 exceptions in 60 games |

v4b and v4c are robustness fixes to v4 with no policy change. Their numbers differ only in the Cornucopia games.

Driver diagnostics (one game at a time; `tools/lib.sh run_game` against g_iter0):
- DefaultMap: 4 games, which moved the cap, the load and the cohesion settings.
- Forest: 3 games (clouds and passivity).
- Cat: 2 games (team target, cohesion; a win at r409 after the v4 changes).
- MassiveL: 3 games (carrier jam, cap, siege rotation tried and reverted).
- ReverseFunnel and Cornucopia: 1 game each, checking the two fixes.

## Signature against the targets (v4c, 20 fidelity games against g_iter0)

"members" is the design's member range (section 4.1). Faithful means within the range widened by 25% (section 3.4).

| id | core | target | members | arch_swarm | on target | faithful |
|---|---|---|---|---|---|---|
| mn_share100 | core | 0.84 - | 0.85-0.98 | 0.851 | yes | yes |
| mn100 | core | 480 - 620 | 492-618 | 396 | no | yes |
| L100 | core | 10 - 14 | 10.5-13 | 12.5 | yes | yes |
| L_lead100 | core | 3 - | 3-7 | 5 | yes | yes |
| first_contact | core | - 25 | 14-22 | 20 | yes | yes |
| eng_prog300 | core | - 0.35 | 0.27-0.35 | 0.444 | no | **no** |
| press250 | core | 230 - | 236-975 | 439 | yes | yes |
| ckill150 | core | 4.5 - | 4.5-7.3 | 5.0 | yes | yes |
| ahead_share | core | 0.54 - | 0.54-0.80 | 0.607 | yes | yes |
| exposed | core | - 0.025 | 0.007-0.022 | 0.018 | yes | yes |
| group | core | 7 - | 7-34.5 | 8 | yes | yes |
| first_anchor | core | 260 - 410 | 262-406 | 293 | yes | yes |
| mn50 |  | 170 - | 168-264 | 234 | yes | yes |
| ad100 |  | - 100 | 10-92 | 74.5 | yes | yes |
| Lb100 |  | 21 - 24 | 21-23.5 | 21 | yes | yes |
| L250 |  | 24 - 32 | 24-32 | 24 | yes | yes |
| C100 |  | 12 - 14 | 12-13 | 10.5 | no | yes |
| C250 |  | 21 - 28 | 21-28.5 | 17.5 | no | yes |
| cpw |  | 3 - 5 | 3-5 | 3 | yes | yes |
| first_press |  | - 100 | 75-100 | 75 | yes | yes |
| ckill300 |  | 10.8 - | 10.8-15.6 | 11.2 | yes | yes |
| cdeath_prog |  | - 0.15 | 0.10-0.14 | 0.172 | no | yes |
| dmgc |  | - 8.5 | 6.4-8.4 | 7 | yes | yes |
| alone |  | - 0.08 | 0.04-0.07 | 0.042 | yes | yes |
| focus |  | 0.45 - | 0.46-0.65 | 0.508 | yes | yes |
| first_hit |  | 0.70 - | 0.72-0.81 | 0.677 | no | yes |
| ahead_win |  | 0.89 - | 0.91-0.98 | 0.895 | yes | yes |
| anchors |  | 4 - 5.5 | 4.1-5.3 | 5.3 | yes | yes |
| conquest_round |  | 470 - 940 | 470-940 | 485.5 | yes | yes |
| amps |  | - 8 | 0-7.3 | 0 | yes | yes |
| throws |  | - 9 | 0-8.8 | 3.1 | yes | yes |

**Strength:**
- against g_iter0: 19-1. The only loss is Hah with the archetype on side A, at r317.
- against c_line6: 15-5. c_line6 won, on c_line6's side, Cornucopia A, Hah B, IslandHopping B, and ReverseFunnel
  on both sides.
- 0 coin games.

## Remaining gaps

- **`eng_prog300` (the failed metric).** The per-game medians range from 0.15 to 0.90:
  - Cat, MassiveL, Hah B, Maze A and IslandHopping A sit at 0.15-0.34, like the members.
  - Forest (0.69 and 0.87), DefaultMap B (0.67), IslandHopping B (0.67), Cornucopia (0.53-0.56), BatSignal
    (0.45-0.49) and Hah A (0.90, the one loss) start their fights mid-map or on the archetype's own half. (Sides here
    are the archetype's.)
  - On Forest the swarm is slow to cross: first pressure on the victim HQ only at r1350-1675. Launchers bug-navigate
    along the long walls at x = 23 and x = 36 (5,776 and 7,340 wall hits in the two Forest games), and group counts fail in the clouds.
  - On BatSignal (1 HQ, 60×20) first pressure is at r300-325.
  - A fix would need either navigation work on Forest-like maps or an earlier, faster first wave. Both are policy
    changes beyond the budget.
- **Mana income.** `mn100` is 396: faithful, but below the members' 492-618.
  - The shortfall is largest on Cat (263-304 against the members' 408), BatSignal (301-305 against 329), Forest
    (317-365 against 420) and MassiveL (341 against 535).
  - Carriers alive are also low: C100 10.5 and C250 17.5, against 12-14 and 21-28.
  - The members mine more per carrier. jmerle had 842 Mn by r100 with 15 carriers on DefaultMap; the archetype has
    553-919 there.
- **Engagement quality** is slightly below the members: `first_hit` 0.677 against 0.72-0.81, `ahead_win` 0.895
  against 0.91-0.98, and our carriers die farther from our HQ (`cdeath_prog` 0.172 against 0.10-0.14).
- **Strength against c_line6 sits at the band's edge (5 of 20).** One more c_line6 win would fail the strength bar.
- **Near misses.** The census `near` column (turns at ≥ 90% of the bytecode limit, counted from the replay)
  totals 2,057-2,716 per 20 games, against g_iter0's 832. The bot's own `nm` counter, which measures the turn's work
  before the telemetry fill, reads 0 in all 60 v4c games.
- **Not built:** `SWARM_DIVE` (vrangr1's r111 amplifier and HQ dive).
- **Overlap with the screen cache:** the fidelity run used `BOT=g_iter0`, so its 20 cells are g_iter0's cached cells
  for this archetype hash.
