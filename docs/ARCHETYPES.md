# ARCHETYPES.md: field-style sparring partners and the pre-trial screen

Owner, PROMPTS 22-23 (2026-10-08): candidates are screened locally before a replica trial (a head-to-head against
the validated build), and the previous-year practice of building archetypes comes back. This document is the design:
five archetypes (section 4), the pre-trial screen (section 5) and the interfaces that let the archetype builders and
the screen builder work in parallel (section 6). Nothing in it has been built or run yet. Every number comes from the
400 replica panel games described in section 1 or from the prior-year practice in the filtered readroom.

## 0. What archetypes are for, and the rules that bind them

An **archetype** is our own package, `src/arch_<name>/` (package `arch_<name>`). It reproduces one style of field bot
that we have observed on the replica panel. Because it is our own build, CLAUDE.md rule 10 lets us play it locally:
on any map, from either side, on a fixed seed, and paired cell by cell (games are deterministic). The panel bots
themselves can only be played as replica matches.

Uses:
- **A screen (regression filter).** Before a trial, the candidate plays every archetype and is compared with the
  incumbent on the same cells.
- **A diagnostic harness.** A loss to a field style can be reproduced on a fixed cell and read with the replay tools.
- **A second arm for changes aimed at a field-only threat.** The prior practice: the archetype arm must improve, and
  the plain mirror must not get worse.

Not a use: judging strength. The replica panel decides (`docs/LADDER_STRATEGY.md`). The prior years measured this
directly: a league of our own archetypes tracked the ladder only across big rating gaps (bc20, 792 games, top five
builds all at 85-86%), a rusher rated far below the incumbent on the field (bc24: 1537 against 1830-1888), and defences
built against an archetype mostly failed on the field. The archetype roster can block a candidate. It can never accept
one.

Lessons the design carries from the readroom (`~/projects/vibe/reference/readroom-no2023/`: bc21 METHOD 6b-ii,
bc24 TRAINING_LOG 82-160, bc26 TRAINING_LOG 13710-13945, advice/ADVICE.md):
- **A sparring partner is an instrument: run it before you trust it.** Every failed archetype of the prior years was
  found by a logged game, never by reading its code. Two examples: polrush produced its target condition for 0 rounds,
  and expander v3 took 8 centres and still lost on votes. Hence the measured fidelity gate (section 3.4).
- **Too weak misleads.** arch_rush won 15.6% where it was meant to be competitive. A bc25 archetype lost 97.5% because
  it attacked with the wrong unit, and that null closed a line of questions for 70 iterations. Hence the strength bar
  (section 3.5).
- **A null against an unfaithful archetype is not a refutation.** Treat a null as a statement about the instrument
  until fidelity is re-checked. When rejects pile up in one area, suspect the partner first.
- **Saturation is censoring.** A partner the incumbent always beats or always loses to can move in only one
  direction. The screen reports this (section 5.2).
- **Coupling is a defect in an arm and a virtue in an opponent.** Archetypes are forks of our strongest frozen build
  with freely coupled edits, not one-trait toggles.
- **Copy the offence and submit it; build the defence against your own copy** (bc20: arch_rush2 became g_iter12, +79
  on the ladder). If an archetype beats the incumbent in 15 or more of its 20 strength cells, it is also a candidate
  for the working line (section 3.7).

Binding rules (CLAUDE.md):
- **Rule 3.** No external bot's source is read, opened, printed, grepped or decompiled; this covers everything under
  `~/projects/vibe/bc23-benchmarks`. Archetypes are built only from observed behaviour:
  - replica replays (`gauntlet/*-panel1-*/replays/<match>.bc23`) read with `tools/replay-dump.sh`;
  - extracts (`matches/<id>/extract/*.csv`), match reports (`research/matches/<id>.md`) and `progress/telemetry.jsonl`;
  - `tools/telemetry_query.py --opponent NAME`;
  - this document's tables.
- **Rule 4.** Prior-year documents are read only through `readroom-no2023/`. No Battlecode 2023 post-mortems.
- **Rule 10.** Local games are only between our own builds: archetypes, snapshots, `examplefuncsplayer`. Nothing in
  this design submits to the replica, requests scrimmages, or touches `progress/ladder-state.json` or a running trial.
- **Rules 1 and 5 (VM).** Games in volume run only on `battlecode-dev`, through the standing queue
  (`tools/vm-enqueue.sh`, which syncs), with `tools/gauntlet.sh` at `MAXJOBS=2` at most: the game-slot semaphore is
  shared, and the galaxy replica runs 7 engines on the same VM. Never `battlecode-dev2`. The driver plays at most one
  diagnostic game at a time (`tools/lib.sh run_game`).
- **Rule 6.** `tools/unit-tests.sh` after every change to an archetype or a tool. The working line `src/bot` and the
  existing snapshots under `src/` are never edited by this work.

## 1. Evidence base

The survey covered 400 replica games: 40 unranked panel matches (`test/cells/panel-v1.txt`), 10 bots × 10 maps × 4 of
our builds. The builds are g_iter0 (submission 24), c_line4 (112), c_line5 (114) and c_line6 (116).
- Every metric comes from the opponent's side of `matches/<id>/extract/*.csv`, computed by the survey scripts.
- Signatures barely change across our four builds. For example, vrangr1 had 14/14/12/12 launchers at r100.
- Replays repeat exactly per cell, so each bot's 40 games are about 10 independent maps.
- Panel maps: DefaultMap, Maze, Forest, ReverseFunnel, Cat, IslandHopping, Hah, BatSignal, Cornucopia, MassiveL.

| style | members (field names) | panel matches (subs 24 / 112 / 114 / 116) | our losses (of 284) | victim win share: g_iter0 / all four builds |
|---|---|---|---|---|
| S1 early mana swarm, besieges our HQ | vrangr1.AFinalsBot, awesomelemonade.finalBot, jmerle.camel_case_v30_final, NotLLeon.v7 | 6/195/530/596, 9/198/533/599, 7/196/531/597, 18/200/535/601 | 149 | 3/40 = 0.075 / 11/160 = 0.069 |
| S2 mana army, amplifier at r36, takes midfield | pranayagra.finalbotfinal | 10/199/534/600 | 37 | 2/10 / 3/40 = 0.075 |
| S3 balanced horde: throws, late amplifiers, island holding | georgezhang02.CB_tuning2 | 8/197/532/598 | 33 | 1/10 / 7/40 = 0.175 |
| S4 attrition blob that anchors only at the end | britacatalin.FinalBot | 22/204/539/605 | 28 | 4/10 / 12/40 = 0.30 |
| S5 adamantium economy, light army, long game | battlecode-archive.Sprint1, reeceyang.v5anaconda, yaonam.PoonPoonv4 (thrower) | 19/201/536/602, 20/202/537/603, 21/203/538/604 | 37 | 21/30 = 0.70 / 83/120 = 0.69 |

The "victim win share" is our build's share of wins against the style. "Victim" below always means the build the
archetype plays against: in the survey, our panel builds; in fidelity runs, g_iter0.

**Why each style beats us, in one line each** (full detail in the survey that produced this document):
- **S1** collects 210-308 more Mn by r100, because every carrier mines mana. It fights in our third from about r20
  and kills about 15 of our carriers by r300. Its launchers fight in groups of 7-35 against our 3, so our exposure is
  7-23 times theirs.
- **S2** wins the first fights with one extra launcher and an early amplifier, then snowballs to +6 launchers by r150
  and raids our carriers.
- **S3** out-produces us with a carrier mass (32 alive at r250). It throws 46 times a game, then sits on islands we
  cannot contest until r2000.
- **S4** wins on maps where our early mana is low: we feed launchers piecemeal into one giant blob (group size 63).
  It then spawn-camps our HQ and anchors 2-4 islands in the last 150 rounds (26 of its 28 wins are island tiebreaks).
- **S5** loses to us 69% of the time. Its wins come on four maps (ReverseFunnel 11, MassiveL 9, Forest 8,
  BatSignal 4 of 37), in long games decided by islands after about r900.

## 2. Metric dictionary (the contract between the measurement tool, the builders and the screen)

`tools/archsig.py` (section 6.3) computes one row per game. The row has two sides:
- `t_*` columns are the **subject**: the field bot in replica games, the archetype in local games.
- `u_*` columns are the **victim**: our build.
- `prog` is BFS progress in the victim's frame: 0 at the victim's HQ, 1 at the subject's (TELEMETRY.md B.2).

Column names are exactly those of the survey script, so the survey's numbers and the archetype's numbers come from the
same code.

Aggregation over a block of games:
- **median** and **mean**: of the per-game values, skipping blanks.
- **pooled**: sum of the numerators over sum of the denominators.
- **share**: the fraction of qualifying games.

| id | per-game column / definition | source | aggregation |
|---|---|---|---|
| mn50, mn100 | `t_coll_Mn@50`, `t_coll_Mn@100` | timeline.csv `coll_Mn` at that round | median |
| ad100, ad250 | `t_coll_Ad@100`, `t_coll_Ad@250` | timeline.csv `coll_Ad` | median |
| mn_share100 | `t_mn_share@100` = mn100 / (mn100 + ad100), per game (new column) | timeline.csv | median |
| mn100_mr | mn100 over games on MassiveL and ReverseFunnel only | timeline.csv | median |
| trip_mn100 | `t_trip_mn_share@100`: share of deposits by r100 from mana wells (`well_type` 2) | trips.csv | median |
| C100, C250 | `t_alive_C@100`, `t_alive_C@250` | timeline.csv `alive_C` | median |
| L100, L250 | `t_alive_L@100`, `t_alive_L@250` | timeline.csv `alive_L` | median |
| Lb100 | `t_built_L@100` | timeline.csv `built_L` | median |
| L_lead100 | `L_lead@100` = `t_alive_L@100 - u_alive_L@100` (new column) | timeline.csv | median |
| L_total | `t_built_L` | census `built_L` | median |
| cpw | `t_carriers_per_well` | census `carriers_per_well` | median |
| amps | `t_built_A` | census `built_A` | mean |
| first_A | `t_first_A`: the first amplifier's birth round; games without one are skipped | robots.csv | median |
| amp_early | share of games with 30 ≤ `t_first_A` ≤ 40 | robots.csv | share |
| A250 | `t_alive_A@250` | timeline.csv `alive_A` | mean |
| throws | `t_throws` | census `throws` | mean |
| throw_kills | `u_killed_by_throw`: victim robots killed by a throw | deaths.csv `cause` = throw | mean |
| first_contact | `first_contact`: the earliest engagement `r0` | engagements.csv | median |
| eng_prog300 | `eng_prog_us_r300`: median `prog0` (victim frame) of engagements with `r0` ≤ 300 | engagements.csv | median |
| first_press | `first_press_us`: first 25-round bucket with `pressure34` > 0 at a victim HQ | hq.csv | median |
| press250 | `press34_us@250`: sum of `pressure34` at victim HQs over buckets ≤ 250 | hq.csv | median |
| ckill150, ckill300 | `u_C_killed_r150`, `u_C_killed_r300`: victim carriers killed by launcher, throw or destabilizer | deaths.csv | mean |
| cdeath_prog | `u_C_death_prog_med`: median prog of victim carrier deaths by launcher or throw | deaths.csv | median |
| aura300 | `t_deaths_aura_r300`: subject robots killed by the victim's HQ aura by r300 | deaths.csv | mean |
| spawn_kills | `u_spawn_kills`: victim robots killed within 5 rounds of birth | census `spawn_kills` (victim row) | mean |
| exposed | `t_exposed` | census `micro_L` token `exposed` | median |
| dmgc | `t_dmg_per_contact`: damage taken per contact launcher-round | census `micro_L` token `dmg/contact` | median |
| ahead_share | Σ`t_eng_n_ahead` / Σ`t_eng_n` (engagements started 2 or more ahead) | census | pooled |
| ahead_win | Σ`t_eng_won_ahead` / Σ`t_eng_n_ahead` | census | pooled |
| par_win | Σ`t_eng_won_par` / Σ`t_eng_n_par` | census | pooled |
| first_hit | `t_first_hit_rate` | census `first_hit_rate` | median |
| group, alone, focus | `t_group_p50`, `t_alone20`, `t_focus` | census | median |
| first_eng_won | `first_eng_result_t`: the first engagement's result for the subject (1, 0.5 or 0) | engagements.csv | mean |
| first_eng_dn | `first_eng_dN_t`: subject minus victim launchers at the first engagement's start | engagements.csv | mean |
| first_anchor | `t_first_anchor`; games without an anchor are skipped | census `first_anchor` | median |
| anchor_games | share of games in which the subject placed an anchor | census | share |
| anchors | `t_anchors_placed` | census | mean |
| isl_rounds | `t_island_rounds` | census `island_rounds` | median |
| conquest_round | `rounds` over the subject's wins with `win_reason` = conquest | census | median |
| tb_share | the subject's wins with `win_reason` = tb_islands, divided by the subject's wins | census | share |
| open_rule | share of games whose first 8 builds (census `first_builds`) follow S3's rule: at least 6 carriers when min(W, H) ≥ 40, else at least 3 launchers among the first 4 | census + games.csv | share |
| victim_share | `won_us`, the victim's win share; coin-flip games excluded | census | mean |
| loss_maps4 | the victim's losses on ReverseFunnel, MassiveL, Forest or BatSignal, divided by all its losses | census | share |
| loss_round | `rounds` over the victim's losses | census | median |

**Known-answer check.** `tools/archsig.py members` must reproduce the survey on the 400 panel games: every per-bot
value in sections 1 and 4 within rounding. This is its first acceptance test (bc21 METHOD 6b-ii: run an instrument on
a case whose answer you already know). Two examples: `ahead_share` pooled gives vrangr1 0.539 and jmerle 0.742, while
per-game medians would give 0.627 and 0.773; `ahead_win` gives vrangr1 0.94 and britacat 0.97.

## 3. Rules common to every archetype

### 3.1 Base and construction

- **Base: a fork of `src/c_line6`** (code hash `5bc8e7e545ac`). It is frozen, and its code equals today's `src/bot`
  apart from one comment.
  - Over g_iter0 it adds the switches the styles need: `C.ARMY` cohesion, `C.MICRO2` parity hold, `C.ROLES`,
    `C.HQ_THREAT`, `C.SPAWN_SAFETY`.
  - It has the telemetry, so archetype games carry decision codes.
  - It has the audit's bytecode fixes, and it played 100 replica games with 0 overruns and 0 exceptions.
  - It is not the validated build. That does not matter for an opponent; the prior-year rule "rebuild from the newest
    accepted snapshot" applied to one-trait arms, whose meaning drifts as the incumbent changes.
- Fork with `tools/fork.sh c_line6 arch_<name>` (section 6.1). Until it exists, use the sed loop of
  `tools/snapshot.sh` with `bot` replaced by `c_line6`.
- Every archetype constant lives in a block at the top of `C.java`, headed `ARCHETYPE arch_<name> (S<k>)`. Each
  constant carries the member measurement that sets it, as the base already does.
  - Set `C.TELE_BUILD`: arch_swarm 101, arch_adecon 102, arch_blob 103, arch_horde 104, arch_ampmid 105.
  - Keep `C.TELEMETRY = true` unless it causes near misses; record the reason if it is turned off.
- Robustness is part of the specification:
  - 0 uncaught exceptions;
  - 0 overruns: every loop over robots, tiles or islands is guarded by `Clock.getBytecodesLeft()`, as in the base;
  - randomness only through `G.rand`, so games stay deterministic.
- **No automatic resync.** Archetypes emulate frozen field bots, not "our bot minus one trait", so they do not follow
  the working line.
  - Staleness here means the proxy no longer predicts the field. The calibration check after every trial measures
    that (section 5.6).
  - An archetype is revalidated when its code changes or calibration flags it.

### 3.2 Behaviour comes from observation

Each builder studies the members' panel games before coding. Sources:
- the per-game narratives in `research/matches/<id>.md`;
- `tools/replay-dump.sh <replay> --game N` with `--map-at R`, `--robot ID`, `--states` and `--events`;
- `tools/telemetry_query.py opening|econ|fights|deaths --opponent <member>`.

Match ids are in the section 1 table; the replays are `gauntlet/*-panel1-*/replays/<match>.bc23`.

The behaviour sketches in section 4 are starting points. Fidelity is judged on numbers, never by reading code.

### 3.3 Validation cells and runs

All validation games use the **screen cells**: the 10 panel maps × sides A and B, seed = the map's own seed. The
gauntlet takes `SEED_MODE=map`, or a CELLS file whose fourth field is `map`. The same cells are used by the screen,
so validation games also fill the screen's cache (section 5.4).

| run | command (on the VM, through the queue) | games | used for |
|---|---|---|---|
| robust | `BOT=arch_<n> OPPONENTS=examplefuncsplayer` | 20 | competence and basics |
| fidelity | `BOT=g_iter0 OPPONENTS=arch_<n> KEEP_ALL=1`, then `tools/archsig.py extract` and `games` on the VM | 20 | signature and strength against g_iter0 |
| strength | `BOT=c_line6 OPPONENTS=arch_<n>` | 20 | strength against a second build (c_line6 beats g_iter0 15/20 in local self-play) |

All three runs take `MAXJOBS=2 CENSUS=1 SEED_MODE=map` and a private `CLASSES=build/arch-<hash>`.
`tools/archsig.py queue arch_<n>` queues all three as one VM job.

**Iterating.** `--quick` runs only the fidelity run, on 10 cells: one side per map, alternating A and B in panel-file
order. Use it for v1-v3. The full 60 games are run only for the version expected to pass. At most one validation job
per archetype may wait in the queue.

### 3.4 Fidelity: what "faithful" means

Each archetype has a target list (section 4). Every entry has an id from section 2, a range [lo, hi] (either side may
be open), and a flag: core or secondary.
- The archetype's value is the aggregate over its 20 fidelity games against g_iter0 (10 with `--quick`).
- **On target**: lo ≤ value ≤ hi.
- **Faithful**: within the range widened by 25% of each bound: [lo − 0.25·|lo|, hi + 0.25·|hi|].
  - An open side stays open.
  - A bound of 0 stays exactly 0 (for example "no amplifiers" means 0).
  - Shares are clipped to [0, 1].
- **Fidelity passes** when:
  - every core metric is faithful;
  - at least 75% of core metrics are on target;
  - at least 50% of secondary metrics are faithful.
- A metric with no data (for example `conquest_round` when the archetype never wins by conquest) is n/a. At most 2
  core metrics may be n/a.

The ranges were set before any archetype exists. They are pre-registered: a change needs a logged reason (a
measurement error, not "the archetype missed"), and it is made before the next validation run.

### 3.5 Strength: comparable to the members

The victim's win share against the archetype must lie within **±0.20 of the members' victim share over all four
builds** (section 1), clipped to [0, 1]. The bar is checked in both the fidelity run (g_iter0) and the strength run
(c_line6), 20 cells each, with coin-flip games excluded. On 20 cells ±0.20 is about 2 standard errors.

| archetype | members' victim share | band | victim wins allowed (of 20) |
|---|---|---|---|
| arch_swarm (S1) | 0.069 | 0 - 0.27 | 0-5 |
| arch_ampmid (S2) | 0.075 | 0 - 0.275 | 0-5 |
| arch_horde (S3) | 0.175 | 0 - 0.375 | 0-7 |
| arch_blob (S4) | 0.30 | 0.10 - 0.50 | 2-10 |
| arch_adecon (S5) | 0.69 | 0.49 - 0.89 | 10-17 |

**Robustness** (robust run, and every other validation game): the archetype wins 20/20 against examplefuncsplayer,
and its rows show:
- census `over` = 0 (overruns);
- `exceptions` = 0 (the bot's counter; `tele_exc_turns` when indicator strings are absent);
- `deaths_self` = 0;
- `sym_wrong` = 0.

Near misses are reported but do not gate.

### 3.6 Status and records

`tools/archsig.py check` writes `progress/archetypes/<name>-<hash>.json` (section 6.4) with verdict **VALID** when
robustness, fidelity and strength all pass, otherwise **INVALID** with the failed ids. Only a VALID record for the
archetype's *current* code hash makes it a screen partner. Changing the code after validation removes it from the
roster until it is revalidated.

Version budget: 4 versions per archetype. If v4 still fails, the archetype stays a diagnostic tool, never a screen
partner. The builder returns the failed metric ids and the measured values, and the training log records why. That is
a statement about our ability to build the proxy, not about the style.

### 3.7 An archetype that beats the incumbent

If an archetype wins 15 or more of its 20 cells against the validated build, it is also queued as a candidate for the
working line: a snapshot through the normal loop, screen and trial. bc20 shipped its rush copy for +79.

If such a style becomes the incumbent, its archetype turns into a near-mirror. The screen then reports it as
"incumbent's own style" (section 5.2) instead of reading its 50% as information.

## 4. The five archetypes

**Priority order:**
1. **arch_swarm**: 149 of 284 losses, decided earliest.
2. **arch_adecon**: the only style the incumbent mostly beats, so it is where regressions show. It is also the
   cheapest, being closest to the base.
3. **arch_blob**: mid-range partner.
4. **arch_horde**.
5. **arch_ampmid**: built from arch_swarm once that is VALID.

The roster is useful with the first three. Builders may work in parallel (section 6).

Notes on the target tables:
- "Members" gives the members' per-bot medians over 40 games each, IQR in brackets for single-member styles.
- Team totals scale with the HQ count (1-4 per map). Members and archetypes are measured on the same 10 maps, so they
  are comparable.
- Values in the survey and in fidelity runs are against our builds. The aggression and raid metrics partly reflect
  the victim's weaknesses, so fidelity is always measured against g_iter0 and never against a stronger future build.

### 4.1 arch_swarm (S1, early mana swarm; model jmerle)

**Members:** vrangr1, awesomelemonade, jmerle, NotLLeon. jmerle is the cluster centre: it merged first with NotLLeon,
then vrangr1, then awesomel.

**Behaviour to implement:**
- **Opening, per HQ.** On r1, 4 launchers then 1 carrier (180 Mn + 50 Ad of the starting 200/200). On r2-r3,
  carriers with the remaining adamantium. Expected team totals: about 10 carriers and 13-14 launchers built by r50.
- **Economy.**
  - A new role policy, `ROLES = 3`: mana only. A carrier takes adamantium only while its HQ holds less than 50 Ad and
    the carrier cap is not reached, so carriers stay affordable.
  - From r200, one carrier in 4 mines adamantium to fund anchors.
  - Carrier cap: 4 live carriers per known mana well, at least 4 per HQ, at most 30.
  - No adamantium banking for an early anchor: g_iter0's `EARLY_CAP_UNTIL` cap and the r120 anchor rush are removed.
- **Production.** A launcher whenever Mn ≥ 45; a carrier whenever Ad ≥ 50 and under the cap. No amplifiers. vrangr1's
  amplifier at about r111 is the optional `SWARM_DIVE` switch below.
- **Movement.**
  - Launchers leave at once and move as groups: `C.ARMY = true`, `GROUP_MIN = 4`, `FOLLOW_R2 = 8`, and groups merge
    when they meet.
  - Objectives in order:
    1. enemies in sight;
    2. the enemy's wells nearest the enemy HQ, predicted by symmetry from our known wells (the carrier raid);
    3. a ring at r² 16-34 around the enemy HQ, outside its r² 9 aura, to catch spawns.
  - Never end a turn inside an enemy HQ aura unless the shot kills.
- **Micro.**
  - When the group is locally ahead by 2 or more (allies plus self, minus enemies), use the base scoring: step in to
    fire.
  - Otherwise use `C.MICRO2` (parity hold): never step into extra enemy reach to fire, and fire only from tiles at
    most one enemy can reach. With no such tile, fall back toward the nearest ally cluster.
  - Focus fire: the lowest-HP launcher in range, ties broken by lowest id so the group picks the same target. Then
    carriers holding anchors, then carriers, then amplifiers.
  - `C.HQ_THREAT = 1`.
- **Islands.** `ANCHOR_START = 250`, `ANCHOR_MIN_LAUNCHERS = 12`. After r250, launchers neutralise enemy islands (base
  `pickObjective`). Members' conquests land at r470-940.
- **Optional `SWARM_DIVE` (vrangr1, off in v1):**
  - one amplifier per HQ at about r110;
  - launchers dive the victim HQ, accepting aura deaths;
  - targets: first_A 100-120, aura300 ≥ 3, conquest_round ≤ 500.

**Targets.**

| id | lo - hi | core | members |
|---|---|---|---|
| mn_share100 | 0.84 - | core | 0.85-0.98 |
| mn100 | 480 - 620 | core | 492-618 |
| L100 | 10 - 14 | core | 10.5-13 |
| L_lead100 | 3 - | core | 3-7 |
| first_contact | - 25 | core | 14-22 |
| eng_prog300 | - 0.35 | core | 0.27-0.35 |
| press250 | 230 - | core | 236-975 |
| ckill150 | 4.5 - | core | 4.5-7.3 |
| ahead_share | 0.54 - | core | 0.54-0.80 |
| exposed | - 0.025 | core | 0.007-0.022 |
| group | 7 - | core | 7-34.5 |
| first_anchor | 260 - 410 | core | 262-406 |
| mn50 | 170 - | | 168-264 |
| ad100 | - 100 | | 10-92 |
| Lb100 | 21 - 24 | | 21-23.5 |
| L250 | 24 - 32 | | 24-32 |
| C100 | 12 - 14 | | 12-13 |
| C250 | 21 - 28 | | 21-28.5 |
| cpw | 3 - 5 | | 3-5 |
| first_press | - 100 | | 75-100 |
| ckill300 | 10.8 - | | 10.8-15.6 |
| cdeath_prog | - 0.15 | | 0.10-0.14 |
| dmgc | - 8.5 | | 6.4-8.4 |
| alone | - 0.08 | | 0.04-0.07 |
| focus | 0.45 - | | 0.46-0.65 |
| first_hit | 0.70 - | | 0.72-0.81 |
| ahead_win | 0.89 - | | 0.91-0.98 |
| anchors | 4 - 5.5 | | 4.1-5.3 |
| conquest_round | 470 - 940 | | 470-940 |
| amps | - 8 | | 0-7.3 |
| throws | - 9 | | 0-8.8 |

**Strength:** the victim wins 0-5 of 20, against g_iter0 and against c_line6.

**Risks:**
- Our own mana-first and cohesion arms failed or cost islands as *single* changes (c_mana1 rejected; c_army1 7/20 vs
  15/20 against g_iter0). The style works only as the coupled whole: mana tempo, groups, parity micro and the raid
  together.
- If v2 still loses to g_iter0's anchor rush, read how g_iter0's anchors survive (`--islands`, deaths of
  anchor-carrying carriers) before changing anything else.

### 4.2 arch_adecon (S5, adamantium economy and light army; model Sprint1 and reeceyang)

**Members:** battlecode-archive.Sprint1, reeceyang.v5anaconda, and yaonam.PoonPoonv4 (the thrower variant, the
`THROWER` switch below).

**Behaviour to implement:**
- **Opening.** Sprint1's: carriers first, 4 per HQ on r1, the first launcher at about r5.
- **Economy.** Adamantium-leaning: 2 carriers in 3 mine adamantium until r300, then the base's balance by HQ stock.
  Expected Mn share at r100 about 0.4.
- **Army.** Light: a launcher only while live launchers < 6 + round/100 per team. Amplifiers from about r150, one
  per 3 launchers built (5-11 per game).
- **Movement.**
  - Launchers keep to their own half. Objectives: enemy sightings with prog ≥ 0.5 in the victim's frame (that is,
    nearer the archetype's HQ), then own and neutral islands.
  - They never pass midfield before r900.
  - Base micro without cohesion (`C.ARMY = false`, `C.MICRO2 = false`). Its high exposure is part of the signature.
- **Islands.** `ANCHOR_START = 500`. Anchors go to the nearest neutral islands, and launchers garrison them; this is
  the long game.
- **`THROWER` (yaonam, off in v1).** Alternating C/L opening, no amplifiers, carriers throw at any enemy within r² 9
  when loaded with 10 or more. Target: throws ≥ 90 per game.

**Targets** (v1 is the amplifier branch):

| id | lo - hi | core | members |
|---|---|---|---|
| mn_share100 | 0.25 - 0.55 | core | 0.33-0.55 |
| ad100 | 250 - 390 | core | 254-390 |
| mn100 | 170 - 250 | core | 172-247 |
| L100 | 6 - 9 | core | 6-9 |
| L250 | 4 - 8 | core | 4-8 |
| eng_prog300 | 0.50 - | core | 0.51-0.74 |
| press250 | - 30 | core | 0 |
| exposed | 0.06 - | core | 0.071-0.077 |
| first_anchor | 530 - 950 | core | 534-948 |
| amps | 4 - 12 | core | 4.7-11.3 (THROWER: throws ≥ 90 instead) |
| loss_maps4 | 0.60 - | core | 32/37 = 0.86 |
| mn100_mr | 250 - 520 | | 250-520 |
| Lb100 | 12 - 19 | | 12-19 |
| C100 | 6 - 15 | | 6.5-14.5 |
| dmgc | 13 - | | 13.4-21.1 |
| first_hit | - 0.40 | | 0.27-0.35 |
| group | - 5 | | 3-4 |
| ahead_share | - 0.45 | | 0.21-0.41 |
| ckill300 | - 5 | | 3.5-4.4 |
| first_A | 150 - 260 | | 159-176 |
| spawn_kills | - 5 | | 0.6-5 |
| anchors | 1.5 - 3 | | 1.9-2.3 |
| anchor_games | 0.20 - 0.45 | | 0.23-0.42 |
| first_press | 150 - | | 150-262 |
| loss_round | 900 - | | 1074 |

**Strength:** the victim wins 10-17 of 20, against g_iter0 and against c_line6.

**Risk:** the map concentration (`loss_maps4`) is emergent and cannot be coded directly. If it fails while everything
else passes, the archetype still serves as a regression partner, but its "why we lose" mechanism is unconfirmed. Log
it that way.

### 4.3 arch_blob (S4, attrition blob that anchors only at the end; britacatalin.FinalBot)

**Behaviour to implement:**
- **Economy.** Mana-first: the swarm's `ROLES = 3`. Carriers capped at 3 per well. From r1500, one carrier in 3 on
  adamantium, to bank 80/80 per anchor.
- **Production.** A launcher whenever Mn ≥ 45. No amplifiers, destabilizers or boosters. Carriers never throw (they
  flee only).
- **Movement.**
  - Launchers gather at a rally point on the archetype's side until the blob holds `BLOB_MIN` launchers in the
    leader's vision. The leader is the lowest id; `BLOB_MIN` is 12, plus 1 per 50 rounds, capped at 40.
  - The whole blob then advances at the leader's pace toward, in order: enemy wells, enemy-held islands (to
    neutralise them), and the enemy HQ. Engagements should centre at prog 0.35-0.45 (victim frame).
  - It falls back to the rally point when the local count drops below enemies + 2.
- **Micro.**
  - Fire only from tiles at most one enemy can reach, unless ahead by 2 or more. Fire-retreat at the edge of reach.
  - Focus the lowest-HP launcher. Target exposure ≤ 0.006, first hit about 0.9.
- **Spawn camp.** When no enemy launcher has been seen near the enemy HQ for 20 rounds, the blob holds r² 10-25
  around it, outside the aura, and fires at newborns.
- **Islands.**
  - No anchor before r1800. `ANCHOR_START = 1820`, `ANCHOR_PERIOD = 5`.
  - The blob clears enemy islands from about r1700. Carriers anchor the nearest free islands from r1840 to r1870.
  - The aim is to win the r2000 island tiebreak.
- **Bytecode.** With 60+ launchers in vision, sensing and scoring must be capped: the 20 nearest robots, plus Clock
  guards. Overruns are the main build risk.

**Targets:**

| id | lo - hi | core | member |
|---|---|---|---|
| mn_share100 | 0.80 - | core | 0.87 [0.46-0.91] |
| L100 | 6 - 10 | core | 7 [4-10] |
| L250 | 13 - 24 | core | 14 [9-24] |
| amps | 0 - 0 | core | 0 |
| throws | 0 - 0 | core | 0 |
| group | 30 - | core | 63 |
| exposed | - 0.006 | core | 0.004 |
| ahead_share | 0.75 - | core | 0.79 |
| spawn_kills | 40 - | core | 60 |
| first_anchor | 1800 - 1880 | core | 1858 [1839-1868] |
| tb_share | 0.80 - | core | 26/28 = 0.93 |
| L_lead100 | -5 - 0 | | -2 [-5 to 1] |
| eng_prog300 | 0.30 - 0.45 | | 0.38 |
| first_hit | 0.80 - | | 0.90 |
| alone | - 0.10 | | 0.09 |
| ahead_win | 0.90 - | | 0.97 |
| anchors | 2 - | | 6.1 |
| anchor_games | 0.60 - | | 0.70 |
| L_total | 250 - | | 493 |
| isl_rounds | - 400 | | 202 |
| mn100 | 216 - 360 | | 288 |

**Strength:** the victim wins 2-10 of 20, against g_iter0 and against c_line6.

### 4.4 arch_horde (S3, balanced horde with throws, late amplifiers and island holding; georgezhang02.CB_tuning2)

**Behaviour to implement:**
- **Opening by map.**
  - When min(W, H) ≥ 40 (Maze, Forest, Cat, Cornucopia, MassiveL): 8 carriers first per HQ, 4 on r1 and 4 as
    adamantium arrives.
  - Otherwise: 4 launchers and 1 carrier.
- **Economy.** Balanced: the base `ROLES = 0`. A high carrier cap: 6 live carriers per known well, with the early cap
  removed. Targets: ≥ 30 carriers alive at r250, Ad@250 ≥ 650.
- **Production.**
  - Launchers whenever Mn ≥ 45 once the carrier cap is met.
  - No amplifier before r260. From r260, one amplifier per 4 launchers built (≥ 20 per game). They escort groups
    (base `Amplifier`).
- **Throws.** A carrier loaded with 20 or more throws at an enemy launcher or carrier within r² 9 when a friendly
  launcher is within r² 20, or when its own HP ≤ 90; then it returns to mine. Targets: ≥ 30 throws and ≥ 3 victim
  kills by throw per game.
- **Islands.**
  - `ANCHOR_START = 290`.
  - Launchers without an enemy in sight garrison owned islands by standing on island squares (this heals the anchor
    and blocks it). Anchors continue until every island is held.
  - No all-in conquest push, so many games go to r2000.
- **Spawn kills.** Launchers near the enemy HQ fire at spawns (member: 38 per game).

**Targets:**

| id | lo - hi | core | member |
|---|---|---|---|
| open_rule | 0.80 - | core | by construction |
| mn_share100 | 0.40 - 0.60 | core | 0.49 [0.31-0.71] |
| ad250 | 650 - | core | 1172 [662-1540] |
| C250 | 30 - | core | 31.5 [14.5-40.5] |
| L250 | 13 - 35 | core | 22.5 [12.8-34.8] |
| amps | 20 - | core | 26.6 |
| first_A | 260 - | core | 428 [262-477] |
| throws | 30 - | core | 46 |
| throw_kills | 3 - | core | 3.6 |
| isl_rounds | 2000 - | core | 2020 |
| first_anchor | 290 - 460 | core | 350 |
| tb_share | 0.40 - | core | 15/33 = 0.45 |
| mn100 | 240 - 440 | | 370 [238-440] |
| ad100 | 180 - 470 | | 354 [177-472] |
| L100 | 6 - 13 | | 10 [6-13] |
| C100 | 12 - 20 | | 16 |
| cpw | 4 - 6 | | 5 |
| spawn_kills | 25 - | | 38 |
| eng_prog300 | 0.33 - 0.47 | | 0.40 |
| group | 8 - | | 12.5 |
| exposed | - 0.015 | | 0.010 |
| ahead_share | 0.70 - | | 0.79 |
| first_press | 100 - 150 | | 125 |
| conquest_round | 700 - 950 | | 828 |

**Strength:** the victim wins 0-7 of 20, against g_iter0 and against c_line6.

### 4.5 arch_ampmid (S2, mana army with an amplifier at r36 that takes midfield; pranayagra.finalbotfinal)

Built as arch_swarm plus edits, after arch_swarm is VALID.

**Behaviour to implement (the edits):**
- **Amplifiers.** Each HQ builds one amplifier in r30-40, then one per 3 launchers, capped at 12 per game. Amplifiers
  sit at the rally point.
- **Economy.** One carrier in 3 on adamantium (Ad@100 50-170).
- **Movement.**
  - The rally point is midfield: the midpoint between our HQ and the predicted enemy HQ, snapped to the nearest
    passable tile. Launchers hold there.
  - Groups of 3 or more detach to raid enemy carriers at wells in the enemy half when they are locally ahead.
  - No approach to the enemy HQ before r150.
- **Engagement.** Engage at a local +1 or better, instead of +2.
- **Islands.** `ANCHOR_START = 440`.

**Targets:**

| id | lo - hi | core | member |
|---|---|---|---|
| amp_early | 0.90 - | core | every game, r36 |
| A250 | 3 - | core | 3.2 |
| amps | 6 - 12 | core | 9.4 |
| mn100 | 250 - 560 | core | 305 [244-562] |
| ad100 | 50 - 170 | core | 122 [48-167] |
| L100 | 12 - 17 | core | 13.5 |
| L250 | 20 - 40 | core | 28 [20.5-39.5] |
| first_eng_won | 0.80 - | core | 0.85 |
| eng_prog300 | 0.42 - 0.52 | core | 0.48 |
| press250 | - 100 | core | 34 |
| ckill300 | 12 - | core | 13.2 |
| first_anchor | 440 - 470 | core | 451 |
| first_eng_dn | 0.75 - | | 0.98 |
| throws | 5 - 9 | | 7.1 |
| mn_share100 | 0.60 - 0.85 | | 0.70 |
| conquest_round | 570 - 820 | | 645 |
| first_press | 150 - | | 200 |
| exposed | - 0.02 | | 0.012 |
| group | 7 - | | 15.5 |
| ahead_share | 0.60 - | | 0.70 |
| ckill150 | 3 - | | 4.1 |
| first_contact | - 30 | | 23 |

**Strength:** the victim wins 0-5 of 20, against g_iter0 and against c_line6.

## 5. The pre-trial screen (owner-approved, PROMPTS 23)

### 5.1 Stages

A candidate is a frozen package (a snapshot, normally). The **incumbent** is `validated.package` in
`progress/ladder-state.json`, read only. The **roster** is every archetype with `"gate": true` in
`tools/archetypes/<name>.json` that has a VALID record for its current code hash (section 3.6). An archetype whose
hash equals the candidate's is dropped from the roster.

| stage | games | cells | bar |
|---|---|---|---|
| (a) basics | 8 | candidate vs examplefuncsplayer on SmallElements (20x20, 2 HQs), Contraction (60x60, 37% walls, 14% clouds), FourNations (13% currents), Tightrope (58% impassable): off-panel maps that stress contact, navigation and bytecode; both sides, seed = map | 8/8 wins; candidate rows: `over` = 0, `exceptions` = 0, `deaths_self` = 0, `sym_wrong` = 0. Failing stops the screen. |
| (b) head-to-head | 20 | candidate vs incumbent, 10 panel maps × 2 sides, seed = map | score s = wins + 0.5 × coin games. **PASS** at s ≥ 11; **BORDERLINE** at 9 ≤ s < 11; **FAIL** at s < 9, which stops the screen. |
| (c) roster | 20 per archetype | candidate vs each roster archetype, same 20 cells; paired with the incumbent's cached games on identical cells | per archetype and pooled, below |
| (d) basics over the whole screen | all | every candidate game of (a)-(c) | `over` = 0, `exceptions` = 0, `deaths_self` = 0 |

**Roster judgement.** For each archetype, take the pairs (cell, candidate game, incumbent game), dropping any pair
where either game ended by coin flip. Count:
- **gained** g: the candidate won, the incumbent lost;
- **lost** l: the candidate lost, the incumbent won;
- net = g − l.

The verdicts:
- **REGRESSION on one archetype** when net ≤ −3 **and** net ≤ −2·√(g + l): at least 3 games and 2 standard errors.
- **Pooled REGRESSION** over the roster when Net ≤ −4 **and** Net ≤ −2·√(G + L).
- **Censoring.** The record marks an archetype "censored-low" when the incumbent won 0 of its cells (only gains can
  show) and "censored-high" when it won all of them (only losses can show). It marks "incumbent's own style" when the
  archetype is or descends from the incumbent's code (section 3.7).

**Verdict: PASS** when all of these hold:
- (a) passes;
- (d) passes;
- (c) has no per-archetype regression and no pooled regression;
- (b) is PASS, or (b) is BORDERLINE and the pooled roster Net ≥ +2. This is the bc21 pattern: a mirror-neutral
  change with a gain on the field-style arm is a finding.

Otherwise the verdict is **FAIL**, with every failed bar listed. An empty roster (no VALID archetype yet) passes
stage (c) with a note, but then a BORDERLINE (b) fails.

**Identity control.** Screening a byte-identical copy of the incumbent (`--allow-identity`) must read exactly s = 10
in (b) (each map is a side split) and 0 discordant pairs in every archetype. That is BORDERLINE with Net 0, so FAIL.
Anything else is a harness defect.

**First use.** Once `tools/screen.py` works, run a backtest before the first gating use:
- the identity control;
- c_line4, c_line5 and c_line6 against g_iter0.

Their replica trials read 25, 28 and 32 against g_iter0's 31 of 100. The backtest is informational. The bars may be
revised once, before the first gating use, with the reason logged. After that they change only by a logged decision
made before a screen, never after seeing a candidate's numbers.

### 5.2 What the record reports

For each stage, the record holds the counts above. For each archetype it also holds:
- the incumbent's and the candidate's wins out of 20;
- g, l, both-won and both-lost counts;
- the censoring flag;
- the archetype's hash and validation record.

These are the gained/lost numbers the owner asked for.

### 5.3 `tools/screen.py`

```
tools/screen.py <candidate> [--incumbent PKG] [--no-wait] [--rerun] [--allow-identity]
tools/screen.py collect <candidate>          # resume a --no-wait screen: wait, fetch, judge, write the record
tools/screen.py show <candidate | record>    # a record as a table
tools/screen.py roster                       # gating archetypes with a VALID record for their current hash
tools/screen.py gate a|b --run DIR [--team PKG]   # VM-side fail-fast checks (stdlib only): exit 0 pass, 1 fail
tools/screen.py ingest [RUN ...]             # add fetched runs to the cache (default: every local gauntlet run)
tools/screen.py calibrate <record> <panel run>    # after a trial (section 5.6)
```

The verbs are reserved words: a package can never be named `collect`, `show`, `roster`, `gate`, `ingest` or
`calibrate`.

**Exit codes:**
- 0 PASS;
- 1 FAIL;
- 2 INCOMPLETE or error;
- 3 refused.

It **refuses**:
- when `src/<candidate>` does not compile (checked locally into `build/screen-check/` before anything is queued);
- when the candidate's hash equals the incumbent's (unless `--allow-identity`);
- when the VM has less than 2 GB of free disk;
- when a finished record for this candidate hash and incumbent hash already exists. It prints that record instead,
  unless `--rerun`.

**Steps:**
1. Compute the hashes with `tools/bot-hash.sh`: candidate, incumbent, examplefuncsplayer and every roster archetype.
2. Load the cache (section 5.4) after `ingest` of the local gauntlet runs. Find the incumbent's missing
   (incumbent hash, archetype, archetype hash, cell) results.
3. Write the job and queue it with `tools/vm-enqueue.sh scr-<candidate>-<hash> '<script>'`, through `tools/vmjobs.py`
   (section 6.5). The job script:
   - takes `MAXJOBS=2 CENSUS=1 SEED_MODE=map CLASSES=build/scr-<hash>`;
   - writes each stage's CELLS file from a heredoc (lines `opponent map side map`);
   - runs, in order:
     1. stage (a): `tools/gauntlet.sh`, then `python3 tools/screen.py gate a ... || exit 0`;
     2. stage (b): `SKIP_COMPILE=1` gauntlet, then `gate b` (fails only at s < 9) `|| exit 0`;
     3. the incumbent's missing roster cells, as one `SKIP_COMPILE=1 BOT=<incumbent>` gauntlet;
     4. stage (c), as one `SKIP_COMPILE=1 BOT=<candidate>` gauntlet over every roster archetype;
     5. `rm -rf build/scr-<hash>`.
   - Run tags: `scr-<hash>-a`, `-b`, `-inc`, `-c`.
4. Save the pending state in `build/screens/<candidate>-<hash>.state.json`: job id, hashes, roster and expected run
   tags. With `--no-wait`, exit 2 here.
5. Wait, polling the VM queue every 60 s. Then fetch every `gauntlet/*-scr-<hash>-*` run without its replays
   (`results.csv`, `census.csv`, `provenance.txt`, `cells.txt`, `summary.txt`, unknown and dud logs).
6. **Check provenance before judging.** Every run's `bot_hash` and `opp_hash.*` must equal the expected hashes.
   - If the candidate's or the incumbent's hash differs, the result is INCOMPLETE (exit 2), to be rerun.
   - If an archetype's hash differs (its code changed on the VM before the job started), that archetype is excluded,
     with the reason recorded.
7. Judge. Ingest every fetched run into the cache. Write `progress/screens/<candidate>-<hash>.json` (section 6.6).
   Print a one-screen summary. The coordinator commits the record and the cache.

**Volume.**
- Candidate: 8 + 20 + 20·K games for K archetypes, 128 with all five.
- Incumbent: 20 per archetype, once per (incumbent hash, archetype hash). These cells are usually already filled by
  the archetype's own fidelity run (g_iter0) or strength run (c_line6).

Self-play games against the incumbent are mostly short: c_line6 vs g_iter0 (20 cells) had a median of about r470,
but 3 of 20 games reached r2000. arch_blob and arch_horde games run to r2000 by design. Record the first screen's
wall time in the training log, and set the pre-trial lead time from it. Screen a candidate while the previous trial
or autoscrim round is running; the screen uses no replica capacity.

### 5.4 The cache

**File:** `progress/screens/cache.csv` (committed; one row per game; append-only; file-locked writes).

```
bot,bot_hash,opp,opp_hash,map,side,seed,result,winner_side,rounds,reason,over,exceptions,deaths_self,run,added
```

- **Key:** (bot_hash, opp_hash, map, side, seed). Determinism makes a cached result valid for any later screen with
  the same key. The key never uses the package name: provenance by code hash, as in `tools/gauntlet.sh`.
- **Sources:** any local gauntlet run whose provenance carries `seed_mode=map` and hashes for both teams. This
  includes archetype validation runs, so `BOT=g_iter0` fidelity runs fill the incumbent's cells for free.
- **Not cached:** coin-flip games (the unseeded final tiebreak), unknown and dud games, and runs with random seeds.
- A key that appears twice with different results is a determinism failure. `ingest` reports it and refuses to use
  the key.

### 5.5 Enforcement in `tools/ladder_policy.py`

`trial-start <package>` refuses unless `progress/screens/` holds a record that meets all of these:
- `candidate_hash` = `tools/bot-hash.sh <package>`;
- `incumbent_hash` = the hash of `validated.package`;
- `verdict` = PASS.

The record is found by hash: any `progress/screens/*-<hash>.json`. The check runs **before** any replica call, and
the refusal names the command to run (`tools/screen.py <package>`).

The override is `--skip-screen "<reason>"`. A reason is required, and the trial-start history event records
`"screen_skipped": "<reason>"`; without the override it records `"screen": "<record path>"`. The existing `--force`
keeps its single meaning, the autoscrim window. Overloading it would let a window override silently skip the screen
too.

`docs/LADDER_STRATEGY.md` gains a step 0 under "Trials" ("a candidate is screened locally first:
`tools/screen.py <package>`, docs/ARCHETYPES.md section 5; `trial-start` refuses without a passing screen record for
the candidate's code hash against the current validated build, unless `--skip-screen REASON`"). The Operation block
gains the screen command.

### 5.6 Calibration: does the screen predict the trial?

After every trial, run `tools/screen.py calibrate <record> <panel run>`. For each style, it sets two measurements side
by side:
- **local**: the screen's per-archetype paired counts, candidate vs incumbent (g, l), and the candidate's win share
  against the archetype;
- **replica**: the trial panel's paired counts against that style's members (candidate panel run vs the validated
  build's panel run, same cells), and the candidate's win share against the members.

It appends one row per style to `progress/archetypes/calibration.csv`:

```
date,candidate,candidate_hash,incumbent_hash,archetype,archetype_hash,local_g,local_l,local_share,replica_g,replica_l,replica_share
```

**Flag:** an archetype is flagged "suspect" when, on two consecutive trials, the local net and the replica net have
opposite signs with both |net| ≥ 2, or when |local_share − replica_share| > 0.30. A suspect archetype is revalidated
(section 3.3) before it gates again.

Calibration is a report. It never blocks a trial. It is the measure of whether the roster earns its games.

## 6. Interfaces for parallel work

### 6.1 Work packages and file ownership

| package | owner | files (only these) |
|---|---|---|
| M: measurement | builder M | `tools/archsig.py`, `tools/test_archsig.py`, `tools/fork.sh`, `tools/archetypes/*.json` (transcribed from section 4; then frozen), `progress/archetypes/members.csv` (written by `archsig members`) |
| S: screen | builder S | `tools/screen.py`, `tools/test_screen.py`, `tools/vmjobs.py`, `tools/gauntlet.sh` (provenance only, section 6.7), `tools/basics.py` (an additive `--json` flag), `tools/ladder_policy.py` (screen check, `--skip-screen`), the `LadderPolicyTest` class in `tools/test_tools.py`, `docs/LADDER_STRATEGY.md` |
| A1-A5: archetypes | one builder each | `src/arch_swarm/`, `src/arch_adecon/`, `src/arch_blob/`, `src/arch_horde/`, `src/arch_ampmid/` (A5 starts from a copy of arch_swarm once it is VALID) |
| coordinator | the session | commits, `tools/unit-tests.sh` (M and S each ask for one added line), `TRAINING_LOG.md`, `HANDOFF.md`, `progress/archetypes/*.json` and `progress/screens/*` produced by the tools |

**Nobody else edits:**
- `src/bot`;
- existing snapshots;
- `tools/vm-queue.sh` and `tools/vm.sh` (vmjobs wraps them);
- `progress/ladder-state.json`;
- anything under `tools/galaxy`.

Builders do not commit; they return their results to the coordinator.

**Dependencies and bootstrapping:**
- **A builders start immediately.** They fork, implement, unit-test, and play driver diagnostic games (one at a time,
  section 6.8). Until `archsig.py` lands they check signatures with the survey scripts, copied from the session
  scratchpad `/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/`
  (`sig.py`, `agg.py`). **M copies these into the repo first**: the scratchpad is temporary.
- **M delivers in order:** `fork.sh`, then `archsig.py members` (the known-answer test), then `games`, then `check`,
  then `queue` and `collect` (these need `vmjobs.py` from S; until it lands, `queue` prints the job script for
  `tools/vm-enqueue.sh`).
- **S delivers in order:**
  1. `vmjobs.py`;
  2. the gauntlet provenance;
  3. `screen.py` with an empty roster, so stages (a), (b) and (d) work and the backtest of section 5.1 can run;
  4. the roster stage, against fixture archetype records;
  5. the `ladder_policy.py` enforcement.

  S never runs `trial-start` against the live replica. Its tests mock every `contest` call.
- **The roster fills itself.** An archetype becomes a screen partner the moment its VALID record exists. No file is
  edited to enroll it.

### 6.2 Registry: `tools/archetypes/<name>.json` (one file per archetype; M writes, nobody edits after)

```json
{
  "v": 1,
  "name": "arch_swarm",
  "style": "S1",
  "title": "early mana swarm that besieges the HQ",
  "members": ["vrangr1.AFinalsBot", "awesomelemonade.finalBot", "jmerle.camel_case_v30_final", "NotLLeon.v7"],
  "model": "jmerle.camel_case_v30_final",
  "member_matches": [6, 195, 530, 596, 9, 198, 533, 599, 7, 196, 531, 597, 18, 200, 535, 601],
  "base": {"package": "c_line6", "hash": "5bc8e7e545ac"},
  "tele_build": 101,
  "priority": 1,
  "gate": true,
  "tolerance": 0.25,
  "targets": [
    {"id": "mn_share100", "lo": 0.84, "hi": null, "core": true, "members": "0.85-0.98"},
    {"id": "mn100", "lo": 480, "hi": 620, "core": true, "members": "492-618"}
  ],
  "strength": {"members_victim_share": 0.069, "band": 0.20, "vs": ["g_iter0", "c_line6"]},
  "switches": {"SWARM_DIVE": {"targets": [{"id": "first_A", "lo": 100, "hi": 120}, {"id": "aura300", "lo": 3, "hi": null}, {"id": "conquest_round", "lo": null, "hi": 500}]}}
}
```

- Metric ids are those of section 2. `archsig.py` holds each metric's definition and aggregation in code, so the JSON
  carries only ranges.
- `members` is documentation only.
- A target change is a new commit with a logged reason (section 3.4).

### 6.3 `tools/archsig.py` (stdlib only; M)

```
tools/archsig.py members [--out progress/archetypes/members.csv]   # 400 panel games; subject = field bot, victim = vibe23
tools/archsig.py extract <run>               # replay-dump --extract for every replay of a gauntlet run -> <run>/extract/<i>/
                                             # plus <run>/extract/manifest.csv (i, replay, opponent, map, side, seed)
tools/archsig.py games <run | extract dir> --subject <team> [--out F]   # per-game rows (section 2 columns) -> <run>/sig.csv
tools/archsig.py ref <name>                  # targets beside the members' per-bot values
tools/archsig.py check <name> --fidelity <run> [--robust <run>] [--strength <run>] [--write]
                                             # table: id, value, lo-hi, on target, faithful; strength; robustness;
                                             # --write: progress/archetypes/<name>-<hash>.json
tools/archsig.py queue <name> [--quick]      # the section 3.3 job on the VM (extract and games run on the VM)
tools/archsig.py collect <name>              # wait, fetch (no replays, no extract dirs), check --write
```

- The per-game column names are those of the survey's `sig.py`, plus `t_mn_share@100` and `L_lead@100`. The rows
  identify the subject by team name: `vibe23` is the victim in replica games, `--subject` names the subject in local
  games.
- Exit codes for `check`: 0 VALID, 1 INVALID, 2 missing data.
- **Tests** (`tools/test_archsig.py`):
  - the known-answer reproduction on a committed subset (for example two matches' extract CSVs under
    `test/fixtures/archsig/`);
  - the tolerance arithmetic (open bounds, zero bounds, clipping);
  - the pooled vs median distinction for `ahead_share`;
  - n/a handling;
  - a VALID and an INVALID record from synthetic rows.

### 6.4 Validation record: `progress/archetypes/<name>-<hash>.json` (written by `archsig check --write`)

```json
{
  "v": 1, "name": "arch_swarm", "hash": "<12 hex>", "base": {"package": "c_line6", "hash": "5bc8e7e545ac"},
  "checked": "<UTC ISO>", "quick": false,
  "runs": {"robust": "gauntlet/<id>", "fidelity": "gauntlet/<id>", "strength": "gauntlet/<id>"},
  "robust": {"games": 20, "wins": 20, "over": 0, "exceptions": 0, "deaths_self": 0, "sym_wrong": 0, "near": 0, "verdict": "PASS"},
  "metrics": [{"id": "mn100", "value": 512.0, "lo": 480, "hi": 620, "core": true, "on_target": true, "faithful": true, "n": 20}],
  "fidelity": {"core_faithful": "12/12", "core_on_target": "10/12", "secondary_faithful": "15/19", "na": [], "verdict": "PASS"},
  "strength": [{"vs": "g_iter0", "vs_hash": "e6f2fc5356c6", "victim_wins": 3, "games": 20, "coin": 0, "band": [0.0, 0.269], "verdict": "PASS"},
               {"vs": "c_line6", "vs_hash": "5bc8e7e545ac", "victim_wins": 4, "games": 20, "coin": 0, "band": [0.0, 0.269], "verdict": "PASS"}],
  "verdict": "VALID", "failed": []
}
```

A `--quick` check writes `"quick": true` and can never be VALID.

### 6.5 `tools/vmjobs.py` (S; the only code that talks to the VM queue for these tools)

```python
enqueue(name: str, script: str) -> str        # via tools/vm-enqueue.sh (which syncs); returns '<UTC stamp>-<name>'
status(job: str) -> str                       # 'pending' | 'running' | 'done' | 'missing' (queue/pending|running|done)
wait(job: str, poll: int = 60, timeout: float | None = None) -> str
find_runs(tag: str) -> list[str]              # VM gauntlet/*-<tag> run ids, oldest first
fetch(run: str, replays: bool = False, extract: bool = False) -> str   # rsync VM gauntlet/<run>/ -> local; returns the path
free_disk_gb() -> float
```

A CLI mirrors these (`tools/vmjobs.py status|wait|fetch|disk ...`). It uses `tools/vm.sh` (`ensure_vm`, `gssh`,
`SSHO`) through bash, and never rsyncs anything toward the VM except through `vm-enqueue.sh`.

### 6.6 Screen record: `progress/screens/<candidate>-<hash>.json`

```json
{
  "v": 1, "candidate": "c_line7", "candidate_hash": "<12 hex>", "incumbent": "g_iter0", "incumbent_hash": "e6f2fc5356c6",
  "created": "<UTC ISO>", "finished": "<UTC ISO>", "job": "<stamp>-scr-c_line7-<hash>", "seed_mode": "map",
  "maps": {"basics": ["SmallElements", "Contraction", "FourNations", "Tightrope"], "panel": ["DefaultMap", "Maze", "..."]},
  "stages": {
    "a": {"verdict": "PASS", "games": 8, "wins": 8, "over": 0, "exceptions": 0, "deaths_self": 0, "sym_wrong": 0, "near": 0, "run": "gauntlet/<id>"},
    "b": {"verdict": "PASS", "games": 20, "wins": 12, "coin": 0, "score": 12.0, "pass_at": 11, "borderline_at": 9, "run": "gauntlet/<id>"},
    "c": {"verdict": "PASS", "pooled": {"g": 9, "l": 5, "net": 4, "se": 3.74},
          "archetypes": [{"name": "arch_swarm", "hash": "<12 hex>", "record": "progress/archetypes/arch_swarm-<hash>.json",
                          "incumbent_wins": 2, "candidate_wins": 5, "g": 4, "l": 1, "both_won": 1, "both_lost": 14, "coin": 0,
                          "censored": null, "verdict": "ok"}],
          "excluded": [{"name": "arch_blob", "reason": "hash on the VM differed from the validated hash"}],
          "runs": ["gauntlet/<id>"], "incumbent_runs": ["gauntlet/<id>"]},
    "d": {"verdict": "PASS", "games": 128, "over": 0, "exceptions": 0, "deaths_self": 0}
  },
  "verdict": "PASS", "reasons": []
}
```

`ladder_policy.py` reads only `candidate_hash`, `incumbent_hash` and `verdict`. Pure function, tested:
`screen_check(screens_dir, cand_hash, inc_hash) -> (ok, path, reason)`.

### 6.7 Gauntlet provenance (S; additive)

`provenance.txt` gains these lines:
- `seed_mode=<map|random|cells>`;
- `opp_hash.<package>=<hash>` for every opponent that is one of our packages.

At compile time the gauntlet writes `$CLASSES/.hashes` (`<package> <hash>` for every package it compiled). With
`SKIP_COMPILE=1`, provenance is read from that file instead of being recomputed from `src/`. Then a `vm_sync` that
lands between two runs of one job cannot make the recorded hash disagree with the code that played.

Existing readers are unaffected: `paired.py` prints the file verbatim, and `contest.py` only appends to its own
runs' copy. S checks that both still pass their tests.

### 6.8 Archetype builder's loop

1. Fork: `tools/fork.sh c_line6 arch_<name>`. Set `C.TELE_BUILD`.
2. Study the members' games (section 3.2).
3. Implement the section 4 behaviour as constants and code in the package. Run `tools/unit-tests.sh`.
4. **One diagnostic game on the driver**, never two at once (check `engine_busy`):
   `CLASSES=build/diag-<name> bash tools/build.sh g_iter0 arch_<name>`, then
   `(source tools/lib.sh; CLASSES=build/diag-<name> run_game g_iter0 arch_<name> Forest <scratch>/d.bc23)`,
   `tools/replay-dump.sh <scratch>/d.bc23 --extract <scratch>/d`, and
   `tools/archsig.py games <scratch>/d --subject arch_<name>`. Read the mechanism, not the result: does it mine
   mana, does it group, where does it fight.
5. `tools/archsig.py queue arch_<name> --quick` (10 VM games), then `collect`. Iterate.
6. When the quick check is on target, run `queue arch_<name>` (the full 60 games), then `collect`. This writes the
   record.
7. Return to the coordinator:
   - the package path and code hash;
   - the record path and verdict;
   - the failed ids with their values, if any;
   - the strength numbers;
   - one line per version saying what changed.

## 7. Open points

- **Puppets** (bc20) replay one side of a recorded game up to a cutoff round. They could reproduce S1's first 100
  rounds exactly. They are usable only on that game's map, side and seed, and are not built now. Consider them if
  arch_swarm cannot reach its opening numbers.
- **Coverage beyond the panel.** A low-confidence sort of older local census data, from before rule 10, puts 9 field
  entrants in an S1-like class (our win share 0.13). The roster targets the panel. It is re-surveyed when the panel
  changes.
- **The incumbent's own style.** If a swarm-like build is accepted (section 3.7), arch_swarm becomes a near-mirror.
  The S1 slot in the roster would then need a harder S1 proxy: the newest accepted snapshot with the members' raid
  and dive added, as a coupled fork.
