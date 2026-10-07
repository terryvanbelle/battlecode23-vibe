# Prior project: battlecode25-vibe (docs slice): what it teaches the 2023 project

Reader: research agent, slice "bc25-docs", 3rd attempt. Written 2026-10-07.
Sources: the 2023-filtered copies under `/home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc25/`
(documents), plus code read directly from `/home/terryvanbelle/projects/vibe/2025/` (tools and our own bots only).
No external competitor bot source was opened. Nothing below describes what 2023 teams did. Where I infer
something (especially the mapping onto the 2023 game), I say "inference".

**Background on the game.** BC25 ("Chromatic Conflict", engine 3.1.0, JDK 21) is a paint-coverage game.
Soldiers, moppers and splashers spend paint to paint tiles. Towers are built on ruins by painting a 5x5 pattern,
and they produce paint or chips. A team wins by painting 70% of the map, or on a coverage tiebreak at round 2000.
Most BC25-specific facts below are useful only as patterns. What transfers is the method, the infrastructure,
and a handful of engineering techniques.

---

## 1. Scope

### What the project was

- Ran 2026-09-06 to 2026-09-16, with 2,138 commits on the repo. Driver VM `claude-driver`, game VM
  `battlecode-dev` (GCE e2-standard-8: 8 vCPU, 31 GB RAM, 20 GB disk).
- Three independent lineages (alice, bob, carol) each ran `TRAINING_ALGORITHM.md` in isolation. A twice-daily
  round-robin tournament between them was the only sanctioned channel. A coordinator session maintained
  `METHODS.md`.
- Bob was retired on 2026-09-10 because of account usage limits. The user then retired alice and carol, and the
  coordinator started a fourth lineage, **darla**, on 2026-09-10. Darla was allowed to use everything all three
  had found. Alice's and carol's workspaces were formally opened for reading on 2026-09-14.
- Final package counts in `src/`: alice 185 packages, 18 frozen snapshots (last `alice_iter43`); bob 27, 9
  (last `bob_iter20`); carol 204, 19 (`carol_iter45`); darla 208 packages, about 191 arms, 7 snapshots
  (`darla-i7`).
- External yardsticks were two BC25 finals bots run only by the coordinator: `v3` (finalist strength) and
  `TSPAARKHS` (winner strength). Agents were forbidden their code and, at first, their games.

### Read in full (filtered copies, sizes in bytes)

| file | size | note |
|---|---|---|
| `README.md`, `OBJECTIVE.md`, `TRAINING_LOG.md` (top-level) | 0.9K, 3.7K, 3.1K | |
| `METHODS.md` | 71K | 86 entries in 5 families; §54 and §56 bodies were empty in the filtered copy (read in EVIDENCE) |
| `TRAINING_ALGORITHM.md` | 52K | the loop and 20 measurement doctrines |
| `MULTI_AGENT.md` | 38K | |
| `TRAINING_CASES.md` | 20K | |
| `RESTART_SESSION.md`, `WIPE-RUNBOOK.md` | 8.7K, 5.4K | |
| `tools/engine-facts.md` | 7.6K | |
| `benchmarks/HISTORY.md`, `tournaments/HISTORY.md` | 5.7K, 0.8K | |
| `.methods-queue/pending.md` | 13.8K | |
| `.claude/README.md` | 4.5K | permissions policy |
| `reference/README.md`, `reference/RESEARCH.md` | 2.3K, 18K | cross-year findings 2019-2024 |
| `reference/22-LEARNINGS.md` | 37K | the 2022 project's lessons, copied in |
| `agents/alice/LEARNINGS.md`, `CLOSURE_MAP.md`, `UNCONFIRMED.md`, `AGENT.md` | 58K, 18.5K, 3.5K, 7.2K | |
| `agents/bob/LEARNINGS.md`, `CLOSED.md` | 19K, 14K | plus `progress/roster_extra.txt`, `milestones.txt` |
| `agents/carol/LEARNINGS.md`, `CLOSURE_MAP.md` | 48K, 38K | |
| `tools/agent-prompts/alice.md`, `resume.md` | 15K, 1.3K | bob's and carol's prompts are near-copies |
| `tools/mapdata/README.md`, `tools/systemd/README.md` | 2.9K, 2.8K | |
| `tournaments/20260910-1300/report.md` | 3.4K | one tournament report as a sample |

### Skimmed (sections chosen by grep and heading)

- `agents/darla/DESIGN.md` (633K, 11,641 lines). This is darla's lab notebook. I read the thesis, all seven
  accept sections, the owner interventions, the v3 replay analysis, both resume points, and the navigation,
  symmetry and comms arms: roughly lines 1-830, 1067-1110, 1616-1905, 2372-2445, 2633-3060, 3165-3530,
  3736-4215, 5293-5460, 5825-6140, 6366-6470, 8010-8110, 8279-8330, 9040-9300 and 11100-11641. The rest I
  read only through its 190 headings.
- `METHODS_EVIDENCE.md` (169K). Grep-only by its own design. I read §1, §45, §54, §56 and §16.
- `agents/*/RULES.md` (20-30K each). These are BC25 rule digests. I read the headings plus the bytecode,
  determinism, provenance and API-sweep sections.
- `reference/22-ART_OF_WAR.md` (18.7K). Headings and two sections. It is low value.
- `agents/*/LEARNINGS_ARCHIVE.md` (162-217K each). Grep-only. I read the "self-referential blind spot", bytecode
  and "candidate set" entries.
- `agents/*/TRAINING_LOG.md` (1.1-1.5 MB each, 18-25K lines). Grep-only, for owner interventions and iteration
  counts.

### Code read directly (our own bots and tools only)

- `tools/gauntlet.sh` (headless runner), `tools/replaydump/ReplayDump.java` (header and method list), and the
  header comment of every `tools/*.sh` / `*.py`.
- Every header in `agents/darla/tools/`, plus selected headers from alice, bob and carol tools.
- `agents/darla/src/darla/RobotPlayer.java`: `run`, `monitorAndYield`, `runTower`, `runSplasher`,
  `moveExploring`, `stepToward`.

### Skipped, and why

- Raw run data: about 1,600 files of gauntlet, `.dumpcache`, `losses`, `results.txt`, `reasons.txt` and
  benchmark `summary.md`/`bots.txt`. It is numbers, already summarised in the notebooks.
- `agents/*/logs/*.txt`: raw match output.
- `carol/notes/i15a_empty_sighting.java.txt` and `DARLA_SCRATCH_v10.java.txt` (first 60 lines only). These are
  code snapshots.
- The remaining agent charters (bob, carol). They duplicate alice's.
- The benchmark bots, which live in `~/bc25-benchmarks` on the VM. Never opened.

---

## 2. What worked (with the evidence as written)

### 2.1 Headline outcome: a single "use everything" lineage beat three isolated ones

Absolute yardstick, from `benchmarks/HISTORY.md`, 150 games each (75 maps x both sides):

| build | vs `v3` | vs `TSPAARKHS` |
|---|---|---|
| bob (best) | 4.7% | 0.0% |
| alice (best) | 17.3% | 1.3% (2/150) |
| carol (best) | 24.7% | 0.0% |
| darla1 (day one: carol's economy + carol's siege fork) | 34.0% | 0.7% |
| darla-i1 | 42.0% | 0.0% |
| darla-i3 / i4 / i5 | 43.3% / 42.7% / 46.0% | n/a |
| darla-i6 | 48.0% (72/150) | n/a |
| **darla-i7** | **56.0% (84/150)** | n/a |

Effect size: the best isolated lineage reached 24.7%, the integrating lineage 56.0%. Two caveats apply. All
lineages remained around 0-1% against a winner-level bot. And from 2026-09-14 darla was selected partly **on**
`v3` (owner's rule change), so the last steps (46 -> 56%) are no longer an unbiased yardstick (darla's own
caveat).

**Darla's starting point.** It was not new strategy. Carol had built a 38-line fork of her own bot that sieges
towers with splashers, purely as a stress opponent. It "beat her 60/40" and "nobody adopted it". Darla started
from carol's economy plus that siege, and on day one the siege was "worth roughly +12 points" against carol
(darla1 beat carol 30/48).

### 2.2 Accepted iterations that moved absolute strength (darla)

All are paired head-to-heads on the full 75-map corpus, both sides, or 450-key paired roster runs. z is McNemar
on discordant keys.

1. **Iteration 1: unit mix plus a splash threshold** (`SPLASHER_IN_20` 3 -> 14, `SPLASH_MIN_SCORE` 8 -> 14).
   - Head-to-head 97-53 (64.7%), z = +3.59, swept maps 32 win / 10 loss.
   - Attribution: each constant alone gave +2.61 sd and +1.80 sd, roughly additive.
   - Fresh-sample absolute series: 63.1% -> 68.8%, t = 3.41 over 3,150 games. v3 moved 34.0 -> 42.0%.
   - Crucially, this had screened at only +4/144 on the 3-opponent gauntlet ("inside the floor"). Only the
     paired full-corpus head-to-head saw it.
2. **Iteration 2: don't queue at a dry tower.**
   - A replay state-token census showed soldier `S HOME` (walking to refill) at 63-79% of soldier-turns. One
     soldier was latched for **416 consecutive turns** (`rt=1, ht=416`). The cause was a refill latch whose
     exit condition looked at the robot's paint, not at whether the tower could supply any.
   - The fix took the head-to-head to 87/150 (+12, z ≈ 1.96) and the 450-key paired roster to 326 vs 307
     (41-22 discordant, z = +2.39).
   - Counters confirmed it: worst `rt/ht` went from 5/138 to 2/49.
3. **Iteration 3: an "escape hatch" bug-nav.**
   - Measured stuck rate (moves that fail to reduce distance to the same target): 21.6% on Bread, 27.8% on
     Portal, 0.0% on Fossil.
   - Full wall-following replacing the greedy fallback **lost 14** (`darla82`). Wall-following that engages
     **only on a turn after the stuck counter fired** won +13 (`darla84`): head-to-head 88/150 (19-6 of 25
     discordant, z = +2.60), roster 341 vs 326 (z +1.69), Stouffer z ≈ +3.03.
   - Stuck rate fell to 16.1% and 18.7%.
4. **Iteration 4: build a money tower only when chips are actually spare.** This replaced a fixed 1-in-4
   share with a demand test derived from existing constants. Combined over three disjoint opponent sets: 1,091
   vs 1,062, 85 discordant, **z = +3.26**, the strongest roster result. **v3 moved -1 (z −0.33).**
5. **Iteration 5: soldiers until the third tower, bounded by round 100.**
   - Positive on every instrument: combined rosters z +2.70, v3 69/150 (+5, 46.0%), all four combined z +2.75.
   - It came from v3 replays: v3 completed its first tower at r22-r34 versus darla's r36-r266. On `shell`,
     darla's first tower came at r266 against v3's r34.
6. **Iteration 6:** four combined changes, including the ruin-unlock splash. Roster 398/450, 56 vs 20
   discordant, **z = +4.13**. v3 72/150 (+3, z +0.47).
7. **Iteration 7: one constant.** `RUIN_BAN_ROUNDS` 250 -> 10 (how long a soldier avoids a ruin whose pattern
   holds enemy paint). v3 84/150, **16 vs 4 discordant, z = +2.68**. The dose curve on `i6` was monotone:
   250 -> 72, 100 -> 74, 50 -> 76, 25 -> 77, 10 -> 84. The constant protected against a case the bot "had
   stopped having" once splashers began clearing ruins.

**Pattern.** None of the accepts came from tuning a promising constant chosen by reasoning (darla's own
summary). They came from:

- (a) combining existing pieces;
- (b) counting state tokens in one replay to find an absolute degeneracy (the latch);
- (c) a counter built to test a documented failure, then reused as a trigger (stuck nav);
- (d) replacing fixed rules with demand tests the actor can evaluate locally;
- (e) reading games against a stronger, independent opponent;
- (f) late re-tests of never-varied constants. Five constants had never been varied when darla twice claimed
  the constant space was exhausted.

### 2.3 Earlier lineages: what paid

- **The tournament exposed a capability gap that self-play hid.**
  - Alice had a **95.8% self-measured win rate** while missing "find ruins outside vision". In the first
    round-robin "bob beat alice 143-7 while alice beat carol 55-26".
  - Two of three lineages had independently grown the same trap: reactive `senseNearbyRuins` soldiers. The
    tournament was the only instrument that could see it. Cost: 11 iterations.
- **Tournament standings moved, though they are zero-sum.**
  - 20260907-0100 -> 20260908-1300: alice 35.3 -> 56.3%, carol 19.0 -> 45.3%, bob 95.7 -> 48.3%.
  - Bob's frozen roster still showed his strongest build ever (40 -> 70 vs a fixed ancestor) while his
    standing halved.
- **The `CHIP_RESERVE` lesson.** "A constant set above the level its resource normally holds is an off switch."
  - Darla fixes: a splasher gate pinned the realised share at 1.2-2.7% against an intended 15% (accepted at
    44/50). An upgrade gate at 3,700 fired 4 times in 9,147 eligible turns.
  - Alice: a 200-paint refill reserve against towers holding 154.8 on average disabled her mechanism on 82.9%
    of frames.
- **Carol's iteration 60 (paint logistics with hysteresis, splashers walk home to refill)** was accepted at
  +26/150 and validated on three external instruments. Bob had closed the same mechanism at −6 at both doses.
  The reconciliation ratio was attackCost/capacity: 2.5% for bob's soldier, 16.7% for carol's splasher, so the
  benefit is 6.7x larger on carol's architecture.
- **Bob's early accepts came from counter dumps, not reasoning.** "327,000 credits unspent at round 2000" and
  "coverage peaks at round 150 then declines" were obvious absolute degeneracies. Three accepted iterations came
  from such dumps; the one that came from reasoning was rejected.
- **Alice's plateau check: thirteen accepts measured +10 net swept (1.89 sd) against a single-accept bar of
  +12.** Her roster showed steep gains to about iteration 28, then about 15 iterations with no measurable
  absolute gain. Recording this as a result, not a disappointment, is what made the stall decision-grade.

---

## 3. What did not work / closed directions

These are BC25-specific unless marked, but the failure shapes recur.

### 3.1 Whole framings that failed

- **The joint local optimum.**
  - Alice and carol spent weeks optimising the head-to-head gap against each other. Both drove that framing
    "to exhaustion" (complete enumerations, closure maps).
  - Both still lost about 75% of games to `v3` (17.3% and 24.7%). The owner's `OBJECTIVE.md` (2026-09-10)
    retired the framing.
  - Every closure of the form "the winner is on the other side of this metric" lost its authority. One carol
    candidate re-opened, then died on value.
- **Darla's founding thesis ("tower removal is the lever")** was refuted on the win condition. A win-type
  tally of 144 games:

  | win type | games | share |
  |---|---|---|
  | painted enough of the map | 125 | 86.8% |
  | tiebreakers (painted more of the map) | 14 | 9.7% |
  | destroyed all enemy units | 5 | 3.5% |

  So 96.5% of games were decided by paint coverage. "I did not think to register" this tally. The siege was
  kept as cheap, but the design centre moved to coverage.
- **In-family roster gains did not transfer to the external opponent.**
  - Iterations 2+3 gave +19 and +15 on the roster but +2 on v3 (z +0.38). Iteration 4 gave +29/1,350 roster
    and −1 on v3.
  - Darla: "the roster is not a proxy for a finalist bot".
  - The owner's audit found held-out fresh samples at about 60% of the in-pool estimate, "the signature of mild
    evaluation-set overfitting".
- **Fixing the most striking deficit did not win.**
  - `darla102` (soldiers only for the first 100 rounds) moved the first tower on `shell` from r266 to r30.
  - It then **lost 7 more games to v3** (57/150, z −1.07) while gaining +21 on a roster (z +2.23). It was
    refused because it helped against relatives and hurt against the stranger.
  - The fix that worked conjoined a self-limiting condition with a round bound (iteration 5). An intermediate
    version gated only on tower count never ended on maps where expansion never began.

### 3.2 Closed mechanism families, with the number that closed each

- **Memory of unseen targets.**
  - Bob's ruin memory (#31) was "identical to the exact zero arm to three decimals". Recall can only return
    ruins already sensed.
  - Alice found 8-20 sites unclaimed for 700 rounds, "seen at zero samples".
  - Darla's remembered ruins were stale on arrival: 95% had enemy paint on the pattern by the time the soldier
    got there.
- **Messaging (BC25 tower-gated comms).** Reporters see 2.48x fewer empty tiles than non-reporters, because
  sending needed a friendly paint path to a tower. "Being where the WORK is means being where the TOWERS are
  not." Darla's comms arm leaned +1.14 on one head-to-head and decayed to +0.57 points (t = 0.32) over 18
  fresh samples and 2,700 games.
- **Symmetry inference (bob #32).**
  - Sized at 0.53 ruins/game, 19% of the gap at the ceiling, about 2 wins in 50.
  - Carol's version was blocked: robots die after 4.7-5.6 witnesses.
  - Darla's four arms either no-op'd (per-robot statics), ran an un-eliminated guess, or overran bytecode
    (`ov=3` to `8`). The answer was consumed only "as the fallback of a fallback".
- **Navigation family.** Carol found "units are blocked by robots, not terrain". Full bug-nav replacing greedy
  lost (darla82 −14, carol stage-0 kills). Only the trigger-gated escape hatch won.
- **De-clumping movement (bob #25/#27).** +6, +5, +6 of 50 against a +10 bar. A saturating exchange rate: 1.0
  paint/unit-round saved ≈ 25 wins/50.
- **Composition / unit mix.** A local optimum in both directions: bob's splasher peak sat at 2 of 5 slots and
  mopper harm was monotone. Carol's allocation oracle was +7, only 27% of her bar.
- **Accumulate by spending less (alice 19).** Cutting spawns 78% left tower paint at 147.0 vs 147.4, and the
  arm held half the towers. "The spending IS the investment."
- **Splasher repositioning (darla, four variants).** The dose-response ran the wrong way. One arm scored 7/150:
  "walking splashers onto enemy paint is fatal".
- **Moppers (darla81).** Removing the paint floor let moppers become 25 of 42 robots and cost 22 games. The
  floor was vindicated by ablation.
- **Self-play blindness excuse (carol).** She twice argued "my self-play gate is blind" and was refuted twice
  by a cross-architecture opponent: +6/50 vs −2/150, and +4/50 vs **−16/150**.

### 3.3 Why things failed (the recurring causes)

1. **Wrong binding term.** Alice's decomposition read production = tower ratio / per-tower-output ratio =
   1.12 / 2.03. She then spent a session on eight directions all aimed at tower count, the numerator she was
   already winning.
2. **Lever attached to a rare decision.** E2 was attached to tower-type choice: about 5 opportunities in
   r1-300, against about 2,700 soldier movement-turns.
3. **Benefit arrives after the window that decides.** The r300 tower leader wins 79-81%, so a slow-compounding
   lever cannot pay.
4. **Prosperity-gated levers** are absent exactly where the deficit lives.
5. **Inert by construction.** Choice sets of size one, unreachable branches, or a gate above the operating band.
6. **A confirmed mechanism that does not convert.** Carol's iteration 76 moved coverage 37% -> 65%, towers
   10 -> 14 and won the demo 700-219, yet screened +0/−10/−4, because it was regime-limited to large maps.

---

## 4. Method lessons

### 4.1 The training loop as designed (`TRAINING_ALGORITHM.md`)

**Phase 0, before any strategy code:**

1. A rules digest.
2. Engine probing via `javap` of the pinned jar.
3. An unused-API sweep **on a trigger**: at iteration 5, every 10 iterations, and whenever stalled.
4. A radius-asymmetry hunt.
5. Headless match and replay-to-text infrastructure.
6. A determinism check.
7. Bytecode monitoring wired in at iteration 0.
8. A play-symmetry audit.
9. The map symmetry contract.

**Iteration 0:** the smallest legal bot plus instrumentation.

**Loop:**

1. Select a target. Don't sample only losses, and prefer absolute degeneracy signals.
2. Trace, don't theorise.
3. Form a hypothesis and run three cheap pre-checks: reachability (guard, choice set, scale), trigger
   frequency across other games, and generality on another losing game. Also do a history check, a check of
   evidence already on disk, and price the cost including the displaced use.
4. Implement small, unbundled changes and verify the mechanism engaged.
5. Staged evaluation:
   - stage 0, a one-map identity check;
   - a cheap reproduction sample;
   - a full gauntlet plus head-to-head versus the last snapshot;
   - accept, near-miss refine, or reject.

"Most of what you try will fail. That is the design." When stalled: ablate accepted features, try structural
exploration, re-read cross-year research, or consider a from-scratch rewrite.

**Hyperparameters:** WinPct 60%, NearMissMargin 5, MaxConsecutiveRejects 3 (then change functional area),
ReproSampleSize 8. In practice the lineages replaced the WinPct gate with head-to-head margins and censuses.

**Lineage throughput:**

- Carol: about 80 iterations, about 19 snapshots.
- Alice: about 60 logged iterations, 18 snapshots.
- Bob: 61 iterations, 9 snapshots.
- Darla: about 191 arms, 7 accepts. The first accept came after 28 arms. 31 arms on 2026-09-14 gave 31
  closures and 0 accepts.

### 4.2 Statistics on a deterministic engine: the most transferable part

- **Determinism.**
  - Identical code reproduces byte-identically: 150/150 identical games, and 10 promotion tests returned their
    exact expected scores.
  - Re-running is worthless. The only randomness is **which maps were drawn**, so the map is the unit of
    resampling (`tools/map-resample.py`: bootstrap and jackknife over maps).
- **But a code change perturbs the PRNG stream, which creates "engine chaos".**
  - A policy-identical, phase-different pair over 75 maps measured **sd 4.80 games per 150 (78% of
    binomial)**, with only 38 of 75 maps surviving a phase change.
  - Another lineage measured **sd 6.48 (106%)**, with 33 of 75 surviving.
  - A PRNG seed offset with zero policy content moved alice's census by **+12 net swept**.
  - Lesson: calibrate your own floor with a phase twin; never inherit one.
- **Cross-architecture games are more chaotic.** Only 2% of games against a foreign-style bot survived a seed
  change, versus 44% in self-play. External instruments need more games, not fewer.
- **State the unit.**
  - sd(margin W−L) = 2 x sd(win count). One gate tool printed "2.0 sd" that was 1.0 sd, a false-accept rate
    near 16%. A published "6.8 sd" was really 3.39 sd.
  - Carol's corrected census gate: ≥ +26 accept, +18..+25 replicate, ≤ +17 reject, on margin over 150.
  - Alice's gate: screen ≥ +4 net swept on 25 maps (50 games); census ≥ +12 on 75 maps (2.27 sd on
    sd_net_swept = 5.29).
- **Swept maps and margin are the same number.** wins − losses = 2 x (swept − swept against). Citing both
  cites one number twice; the sweep counts add only D, the number of split maps. Corollary: identical code
  sweeps nothing (every map splits 1-1), so a census with any sweep proves the change did something.
- **Screens vs census vs paired head-to-head.**
  - A 50-game arm "cannot resolve anything smaller than a ~14-point effect".
  - A 150-game fresh 25-map sample has a 2-sd floor of about 5.5 points (darla, 6 baseline samples, run-to-run
    sd 2.75 points). Later, over 38 samples, mean 102.0/150 with sd 7.71: an unchanged build moved 16 games
    between samples.
  - The **paired head-to-head of candidate versus baseline on all maps, both sides** removes map difficulty.
    It turned "+4/144, noise" into "+22/150, z +3.59" for the same change.
  - The **450-key paired roster** (3 opponents x 75 maps x 2 sides) triples the discordant keys.
  - Screen margins inflate about 2x against the census (carol: +12 screen vs +6 census on the same arm).
- **Self-play gate vs roster: signs disagreed twice in one day.** darla124/129 swept 17-20 maps in the mirror
  and lost on the roster. darla133 was +13 in the mirror and −9 on the 450 roster (z −1.08). Self-play became
  a catastrophe check only. The first gate became a pinned 25-map sample against the three frozen lineages,
  paired so McNemar applies (`roster-screen.sh`).
- **Head-to-head margins do not chain.**
  - Measured exactly on one 25-map sample: part 1 +8, part 2 on top +6, whole +8 (not +14).
  - A destructive pair scored 76% and 82% separately and 56% combined.
  - When the frozen roster drops, ablate **pairwise**, with the pair named by ancestry, not plausibility.
    Reasoning-nominated pairs were refuted 2 of 3 times.
- **Frozen roster design.**
  - Iteration 0 plus every 5th snapshot, never retired. Saturated rungs are "censored, not blind". Repair by
    **adding the newest accepted snapshot** as a rung.
  - Hand-built archetypes failed in both directions: one too strong, one swept 25-0.
  - Tie the roster run to accepts. Alice's was four accepts stale, and her live bot was in fact losing to
    iteration 39 at 18/50. `roster-stale.sh` now exits non-zero.
  - With 12 cells per run, P(any cell ≤ −2.29 sd) = 0.121, so a multiplicity correction is required.
- **There was no Elo or ladder.** Instruments were tournament win% (zero-sum, relative), frozen-roster win%
  (absolute but in-family), benchmark win% (absolute, external), and McNemar z on paired keys for accepts.
  Inference for 2023: if we build an Elo ladder, these findings say the decision instrument should still be a
  paired comparison on identical (map, side) keys, not an Elo delta.

### 4.3 Pre-registration and measurement discipline (selected from 86 METHODS entries)

- Register the gate, the selection rule, the **falsifier**, the precedence between primary and control, and
  the **residual "neither" branch**. Branches must partition the outcome space; carol's two branches missed a
  uniform +14..+42% result.
- Put the branch **order** in code (VOID first; alice's `e2-gate.py`), and arm the gate on the completion
  marker so partial numbers are never seen.
- **Manipulation checks prove a knob moved, not that it helped.** Carol's `noPaint` went 0.0% -> 49.0% with a
  flat screen. The bot's own decision statistics are "the most tempting and least trustworthy secondaries".
- Specify a manipulation check as a share. Make sure the denominator is not caused by the treatment: one
  denominator grew 11x across arms.
- **Funnel a mechanism that does not fire.** Alice's lever fired on about 1%:

  | stage | pass rate |
  |---|---|
  | action free | 45.4% |
  | spare resource | 60.0% |
  | **recipient in range** | **20.0%** |
  | recipient needs it | 21.4% |

  The fix was adjacency, not the dose she was about to change.
- **Measure jointly, not marginally.** A marginal product of 2.10% passed a 2.0% bar; the joint was 0.93%. A
  dose sized from one gate of a four-gate conjunction predicted 5.7x and realised 1.15x.
- **A rate cannot tell slow from stopped.** A median gap of 57 vs 37 hid a sequence of 25, 54, 174, 191, 248,
  **869**.
- **Plot X past round R.** 48% of alice's losses were games she led at r300.
- **Mirror check before calling a collapse a mechanism.** Alice retained 99.3% of her peak in wins and 69.4% in
  losses; the opponent mirrored it at 62.9% / 99.6%. The collapse is downstream of the outcome.
- **Replay per-robot state is recorded post-action**, so it cannot price affordability. "Affordable on 0.10% of
  turns" implied about 24 opportunities while 572 soldiers were actually built. To measure a decision,
  instrument the decision in-bot.
- **Prove a check can fail.** `diff | head && echo IDENTICAL` reads head's status. A waiter counted 58 lines as
  50 games when the run was at 19, and the partial file looked like an inert mechanism.
- **Re-derive engine facts from the jar.** Two digests agreeing is not verification. Alice's and bob's digests
  carried the **same** error independently. Tag facts `[E]` with provenance.
- **Closure ledger with KIND and a testable re-open condition.**
  - Kinds: measured-and-small, oracle-ceilinged, refuted-on-value, structurally-impossible, feasibility,
    gate-unimplementable, excluded-by-measurement, blocked.
  - Grep it by hypothesis name before proposing anything. Bob spent 24 games re-deriving a defect his own log
    held.
  - Power-check a re-open condition when you write it. One was a 0.33-sd comparison, unsatisfiable at 300
    games.
  - A **ceiling** ("no implementation can clear the bar") is stronger than a closure.
- **Record the measurement, not the explanation.** This rule recurs most often in METHODS and it cost two wrong
  entries.

### 4.4 Process rules that earned their place

- **"A lesson you wrote is not a control. Install the check where the mistake happens"** (doctrine 19). All
  three lineages converged on tools that refuse the error:
  - carol's `stage0.sh` and bob's `stage0.py` **refuse to print who won**;
  - bob's `gate.py` puts the unit in every name;
  - carol's `margin.py` refuses a signed margin without `--candidate`;
  - alice's `unconfirmed.sh` ratchet blocks promotion after 3 unconfirmed keeps;
  - darla's `make-arm.sh` proves an arm differs from baseline exactly as intended.
- **Accept routine, scripted** (`accept-iteration.sh`): freeze the outgoing build, promote, run a promotion test
  with an *exact* expected score, benchmark on every accept, push.
- **The machine must never idle.**
  - `arm-runner.sh` drains a queue file. `idle-filler.sh` runs fresh-sample absolute measurements when the
    queue is empty and yields to real measurements. A state-based watcher (`watch-state.sh`) scans for new
    `summary.txt` instead of tailing logs.
  - Queue depth ≥ 3 at all times (owner rule). A 10-minute heartbeat via `/loop`.
- **Context economy.**
  - A cold start's mandatory reading was about 5,200 lines (~77k tokens), 20-50% of a session.
  - Fixes: resume agents by `SendMessage` by default; split read-first indexes (LEARNINGS, METHODS) from
    grep-only archives; a CLOSURE_MAP as the handoff; cycle agents at about 250k context.
  - Both lineages "produced their sharpest work of the day after compaction, at a third of the context".
- **Logging.** Supersede in place and annotate the old entry; never delete. Run consistency passes; a correct
  rule and a contradicting rule sat eight lines apart and the wrong one was quoted for three iterations. Leave a
  machine-checkable resume point (run-ids and gates, not intentions).

### 4.5 Multi-agent: what running several agents taught

- **Gained:** a real measurement against opponents the lineage did not produce. It exposed the shared blind
  spot (alice 143-7 to bob).
- **Gained:** pair decomposition of pooled rates (doctrine 20). A 25.0%-vs-49.9% pooled subset (z = 4.15) was
  flat against one opponent (−2.9 points) and −41.4 / −35.8 in the pairs involving the third. "Two of the three
  lack a capability", not "I am broken".
- **Cost: co-evolution into a joint local optimum.** Alice and carol fought over a 3-point gap while losing
  three quarters of their games externally.
- **Cost: isolation leaks.** Shared scratchpad `tasks/` transcripts, `.bc25` replays at the scratchpad root,
  unscoped `pgrep`/`ps`, VM home listings of generated runner scripts, opponent indicator strings inside
  tournament replays. Each needed a rule plus a mechanical control (`isolation-sweep.sh`, `u=wx` on the root).
- **Cost: a shared git index.** 1,716 lines of one lineage's work were committed under another's message, which
  led to `agent-commit.sh` with a private index.
- **Cost: duplicate sessions, five times.** Messaging a "completed" agent resumes it. "Completed" is a snapshot,
  not a state. The fix is `TaskStop` before every relaunch, plus a duplicate-gauntlet warning in `gauntlet.sh`.
- **Cost: usage limits.** Bob was retired to fit the account. A systemd watchdog exists because a usage limit
  kills the coordinator's own recovery loop.
- **Verdict.** The decisive gain came from **ending isolation**. Darla, which could combine all three
  lineages' findings and their overlooked pieces (carol's siege fork), went from 24.7% to 34.0% on day one and
  56.0% later. Inference for 2023: one integrating lineage with a diverse frozen opponent pool beats several
  isolated ones unless an external ladder exists. If multiple agents are used, keep them as *opponent
  generators* (diverse archetypes), not competing developers.

### 4.6 Owner (human) interventions and what each corrected

| when | intervention | what it corrected |
|---|---|---|
| start | no web-downloaded bots; no current-year post-mortems (filter before reading, `redact-2025.py`) | kept the search honest |
| 09-07 | finals bots are a yardstick only: no code, no replays, no running, never an opponent; scores only | stopped tuning to a fixed opponent |
| 09-09 | resume agents by default | ~77k tokens per cold start, ~1M/day re-learning |
| 09-10 | `OBJECTIVE.md`: absolute strength, not the rival gap; re-examine every comparative closure | the joint local optimum |
| 09-10 | retire bob (usage), then alice and carol; start darla with access to everything | isolation's cost exceeded its value |
| 09-10 | cycle agents at ~250k context | cost per tool call; agents ran at 700-965k |
| 09-11 | "never idle" machine requirement | VM sat idle when the session slept |
| 09-11/12 | "you have been stopping and idling" (10 commits, mean gap 44 min) | single-result gating and blind log watchers |
| 09-13 | benchmark v3 on every accept; "where are the later versions?" | **31 unpushed commits**; benchmark two accepts stale, which hid that roster gains did not transfer |
| 09-13 | audit: "progress looks flat"; are the criteria right? | held-out at ~60% of in-pool, i.e. selection overfitting (left as is) |
| 09-13 | permissions: do legitimate work without asking, ask when unusual; web moved to ask; `rm -rf` moved inside a script | prompts on routine steps |
| 09-14 | grant v3 replays; v3 may count for accepts; "WHAT THIS PROJECT IS FOR": practice for a contest, generalisation over any one opponent, ignore the too-strong bot | produced iteration 5 (the opening) and iteration 7 |
| 09-14 | "not much is happening"; "don't stall on ideas"; cap at 2 run drivers; accept on McNemar z > 2 on either instrument; "no wrapping up, keep exploring" | over-strict self-imposed rules turning into stalls |
| (bc22, cited) | "we're never going to defeat [a benchmark] by being cautiously incremental" | escalation to structural attempts |

### 4.7 How the agents went wrong (recurring)

- **Generating mechanisms faster than locating defects.** Alice's iterations 44-47 were four mechanisms
  without a located defect, all rejected. "Census before mechanism."
- **Wrong referent.**
  - `bot_result` read from the wrong perspective. Carol did it twice, once producing −11.24 sd, caught only by
    its absurdity.
  - Coverage computed over total area instead of passable area.
  - A "6.3 vs 17.0 capability gap" quoted for weeks that paired two different maps; matched, it was 1.25x.
  - A recorded cost table wrong by 2.3-21x with no method attached.
- **Premises carried without provenance.** "Ruins saturate" came from one map, late, in self-play, and bore 44
  iterations, killing three. In fact 42-79% of ruins were still unbuilt at the decisive round, and 0 of 142
  observations had none left.
- **Asserting exhaustion without checking.** Darla said "constant space exhausted" twice with five constants
  never varied. One of them (`RUIN_BAN_ROUNDS`) later gave the v3 accept.
- **Waiting instead of queuing.** Committing without pushing. Self-imposed rules ("no same-day rebuilds")
  hardening into stalls.
- **Over-process.** 86 METHODS entries, 20 doctrines, 11,641-line notebooks. My judgement: the lineages with
  the most elaborate methodology (alice, carol) reached 17-25% vs v3. The lineage that reused pieces and fixed
  degeneracies doubled that.

---

## 5. Bot architecture and the basics (with mapping to BC23)

All four BC25 bots were single-file or near-single-file Java: darla `RobotPlayer.java` 959 lines; carol 903;
alice 655; bob split into `Soldier/Tower/Splasher/Mopper/Nav/G` (783 lines in total). Constants are documented
inline with the measurement that set them. That is worth copying: every constant comment names its arm, dose
and result.

### 5.1 Main loop and bytecode monitoring (darla `RobotPlayer.run` / `monitorAndYield`)

- Per robot, the loop is: seed the RNG from `rc.getID()*7919+13` (not team-correlated), run the type handler
  inside try/catch that turns exceptions into a state string, then in `finally` call `monitorAndYield`.
- `monitorAndYield` compares the round before and after the logic (an **overrun**, since the limiter pauses
  silently), flags a near-miss above 80% of the limit, tracks the max, and writes **one** indicator string:
  `[BUILD] bc=used/limit max= ov= nm= <mechanism counters...> | state`.
- Every arm's mechanism counters ride in that string, and the replay dumper reads them. A rule earned twice: an
  arm whose robots overrun (`ov>0`) is **void**, not worse.
- Gotcha: the indicator string is **one slot per robot per turn, last writer wins**. Alice's census was erased
  by her own `finally` block. Length truncates silently (bc22).
- Bytecode headroom in BC25 was large. Alice measured peak 1,638/17,500 (9%) for soldiers and 534/20,000 (3%)
  for towers. Darla's terrain-in-vision symmetry sweep (`senseNearbyMapInfos(-1)`, about 69 tiles x 3
  candidates) still overran.
- **BC23 mapping (inference): bytecode will bind much harder.** Launchers have a 10,000 limit and carriers
  12,500, against BC25's 17,500. Wire `monitorAndYield` in at iteration 0 exactly as is. It ports almost
  verbatim (use `rc.getType()` and the bc23 limits).

### 5.2 Navigation (darla `moveExploring` / `stepToward`; accepted iteration 3)

- **Greedy step:** direct direction first, then ±45°, then ±90°. The left/right tie is broken on robot ID
  parity, not compass order (play-symmetry).
- **Stuck detector:** counts consecutive calls toward the *same* target where distance did not decrease
  (`mvStuck/mvTry`).
- **Escape hatch:** only on the turn after the stuck flag fired, rotate consistently from the last bug
  direction (side by ID parity) until a legal move, then rotate back toward the wall. State is dropped the
  moment the direct step works.
- **Exploration:** a persistent far target, the farthest of 4 random samples. It is re-rolled on arrival
  (d² ≤ 8), after being stuck 6 turns, or after 120 turns. If fully blocked, any legal move beats standing
  still.
- **Evidence:** full wall-following replacing the greedy fallback lost 14 games. The trigger-gated hatch won 13.
  "Reading the digest correctly mattered more than implementing it well."
- **BC23 mapping (inference):** BC23 has walls, currents that push units, and clouds that slow cooldowns, and
  launcher moves are expensive (cooldown 20). Expect pathing to matter more than in BC25. Start with this exact
  greedy + measured-stuck-trigger hatch, plus the `mv` counter. Treat currents as obstacles for pathing; heavier
  pathing (BFS) has to be priced against 10k bytecode. Carol's warning transfers: "the dominant obstacle field
  is the bot's own units", and units re-target constantly. Measure the stuck rate per map before building more.

### 5.3 Economy and production

- **Find the binding resource and the phase in which it binds.** Alice held a mean **42,712 chips** while
  towers could not afford a 200-paint soldier. Chips averaged 1,502 in r100-300 (the deciding window) and
  56,706 late, so the pooled surplus was "a shortage in the phase that decides".
- **"Can't" vs "won't":** a tower choosing not to spawn would pile up at its 1,000 cap. "At-cap 0.0% across
  2,542 frames" proved the towers were broke.
- **Spending is the investment** when income scales with what you build. Cutting spawns banked nothing.
- **Demand tests over fixed shares** (iteration 4). Self-limiting conditions must be bounded by something that
  happens regardless (iteration 5: towers ≤ 2 AND round < 100).
- **Spawn-stream shape matters.** Making a 1-in-3 soldier rhythm exact lost 5 keys (darla177). Halving the roll
  rate lost 6 (darla179). Removing the chip wait lost 11 (darla180). "The shape of the spawn stream, not the
  mean share, is what the census is pricing."
- **Thresholds must sit inside the operating band.** Measure the treasury's distribution before setting a
  reserve. `CHIP_RESERVE` 1200 against a treasury sawtooth in [1,200, 1,600) blocked soldiers "forever".
- **Pooled vs per-payer budget.** A unit is built from **one** tower's own stock (carol: pooled income said
  affordable; one tower held ≥ 300 paint in only 27-54% of rounds).
- **BC23 mapping (inference):**
  - HQs build from a team-level pool, but carriers deliver to a specific HQ. On multi-HQ maps, check whether
    the per-HQ stock (not the team total) gates builds. The engine is the authority: verify with `javap`
    whether resources are per-HQ.
  - Ad vs Mn vs Ex: apply the "which resource binds, in which phase" measurement before tuning carrier
    allocation. Launchers cost Mn, carriers and amplifiers cost Ad, anchors need both.
  - Any reserve constant (e.g. "save 80 Ad + 80 Mn for an anchor") must be checked against the measured
    treasury band, or it becomes an off switch.

### 5.4 Latches and degeneracies

- The refill latch (iteration 2) is the archetype: a state entered on the unit's condition, exited only when
  the unit's condition recovers, with the supplier able to give nothing. 416 turns were spent commuting.
- How it was found: count state tokens across robots in one replay, then follow the largest block.
- **BC23 mapping (inference):** carriers have exactly this shape:
  - waiting at a crowded or unreachable well;
  - returning to an HQ they cannot reach;
  - holding an anchor with no reachable unclaimed island.

  So do launchers chasing a target behind walls. Put `latches/turns-latched` counters (`rt/ht`) on every
  latched state from day 0, and run the state-token census early.

### 5.5 Exploration and information

- Alice's limiting fact was a **vision gap, not a decision gap**. Units saw a mean of 1.00 open ruins each, so
  shared tie-breaks had nothing to break.
- 93.6% of paintable tiles were invisible to the whole team at once. Yet "the median soldier ... is 4 tiles from
  unexplored map at all times": reaching new ground was never the barrier, knowing which way to go was.
- Exploration and work are in tension: the idle unit is the explorer.
- **BC23 mapping (inference):**
  - Wells, islands and the enemy HQ are the "ruins" of BC23. Unlike BC25's tower-gated messaging, BC23's
    shared array lets any unit **read** everything, and lets units near an HQ, amplifier or anchored island
    **write**. So the "reporters are systematically where the information is not" selection effect applies
    to writes from the frontier.
  - Amplifiers are the designed fix. Measure the share of frontier sightings that can be written before
    designing a comms schema (alice: "name the badly-made decision before designing a schema").

### 5.6 Symmetry

- Bob's corpus census: the transform was recoverable from the ruin set alone and **unique on 95% of maps**:
  reflectH 43%, rot180 28%, reflectV 24%, ambiguous 5%. Rotation, the naive guess, held on only 27 of 75 maps.
  "Infer, never assume."
- It was **worth little in BC25** because the consumer branch was a fallback of a fallback, and witnesses
  accumulated too slowly.
- Darla's `darla74` was the right control: a free heading with no inference at all, to test whether the
  consumer matters before paying for the derivation.
- Engine gotcha: **static fields are per robot**. `myStart` set only on towers left every soldier with null, a
  no-op arm.
- **BC23 mapping (inference): far more valuable.** The enemy HQs are the primary launcher targets and their
  locations follow from own-HQ positions under the map symmetry (1-4 HQs, symmetric by rotation or
  reflection). Islands and wells mirror too.
  - The HQ can test candidates at round 1 from visible terrain.
  - Eliminations can go in the shared array: a few bits, writable by the HQ.
  - Check the consumer exists first: launchers that march to the enemy HQ need the answer every game.
  - Measure the symmetry-type distribution of the BC23 map pool with a scanner like `RuinScan.java`.

### 5.7 Combat and micro

- **Radius asymmetry was exploitable.** A splasher's attack centre at r² ≤ 4 plus AoE r² ≤ 4 reaches distance
  4, while a paint or money tower reaches r² 9 (distance 3). The siege controller keeps a firing ring at
  r² 10..16 (approach if > 16, back off if ≤ 9). Probe result: 0.2% of 433 splasher deaths and 0 of 108
  soldier deaths happened inside tower range.
- **Tower damage is permanent** (no regeneration), so "a unit cannot finish a tower" was burst arithmetic
  wrongly applied to an accumulating quantity. Observed: about 25 hits per kill.
- **Tower attack logic** (darla `runTower`): single-target the lowest-HP enemy in range, plus the AoE if any
  enemy is near.
- **Splash target scoring:** score each centre within r² 4 by enemy towers inside the AoE (money 100, paint
  60), enemy paint within r² 2 of the centre (+3), and empty passable tiles (+2). Fire only above
  `SPLASH_MIN_SCORE`.
  - The engine's exact predicate mattered. Enemy paint is overwritten only within r² 2. A soldier attack on
    enemy paint **costs 5 paint and does nothing** (the engine debits before it checks). Switching the guard
    from a "not mine" proxy to the engine's "EMPTY" predicate cut starvation deaths about 4x.
- **BC23 mapping (inference):**
  - HQs hit r² 9 and launchers attack r² 16 with vision r² 20, so launchers can stand off HQs. The same
    ring logic applies (stay between r² 10 and 16 of an HQ you are sieging, though HQs are indestructible, so
    sieging means denying the area).
  - Launcher vs launcher (both r² 16 attack, r² 20 vision) is symmetric: micro is about first shot, cooldown
    timing and focus fire.
  - Carriers can throw cargo as damage; sweep the API for such secondary uses (§16 below).
  - Guard every action on the engine's own predicate, and check with `javap` whether any BC23 action debits
    before it validates.

### 5.8 Communication

- In BC25 messaging was closed on delivery and structure: 4-byte messages, robots r² 20 to towers, towers
  broadcast r² 80.
- Bob's lesson: "I designed a protocol around **who owns the radio** rather than who holds the information."
- Alice's: "When every re-open condition for a direction is a change to a DIFFERENT subsystem, the direction is
  not a lever, it is a consequence of one."
- From bc22, still relevant: fixed slots per purpose with a single writer and an explicit clearing condition.
  "A signal that only clears under a rare game state can get permanently stuck open." Use live census by an
  accumulator ("first actor publishes last round's total"), not cumulative counters.
- **BC23 mapping (inference):** the 64 x 16-bit array maps directly onto the bc22 slot design. The write
  constraint makes amplifier placement the comms design problem. Log-encode wide ranges (RESEARCH §4).

### 5.9 Play symmetry and determinism (Phase 0)

- Engine scan order is fixed (x ascending, then y), and turn order is by (roundsAlive, ID).
- Any "first satisfying result" or compass-ordered tie-break correlates with spawn geometry. In bc22, a mirror
  match showed a 100%/0% side split on one map.
- A fixed-seed shared `Random` gives identical values to corresponding robots on both teams.
- BC25 games were deterministic except the final random tiebreak.
- **BC23 action (inference):** verify determinism in week 1 by running identical code twice and diffing
  game-by-game. Everything in §4.2 depends on it.

---

## 6. Tools and infrastructure inventory (reuse verdicts for 2023)

Paths are relative to `/home/terryvanbelle/projects/vibe/2025/`. Quality: the shared tools are carefully
written, heavily commented with the bug history that shaped each one, and have accreted many defensive layers.

**Changes needed everywhere for 2023:**

- **Java 8.** BC23 engine 3.0.15 runs on Java 8. Remove the `--add-opens` flags (Java 8 rejects them).
  Install a JDK 8 on the VM instead of `~/jdk21`.
- **Engine artefact name and version pin.** Resolve the BC23 jar name from the gradle cache and pin it in an
  `engine_version.txt`.
- **Replays are `.bc23`** with a different flatbuffer schema.
- **Map files and map list.** Map extension and list differ (`tools/bc25-maps.txt` holds 75 maps).
- **Server log format and win-reason strings.** The `sed` parsers for "(A) wins (round N)" and "Reason:" must be
  checked against 3.0.15 output.
- **VM names, paths and caps.** `battlecode-dev`, `claude-driver`, `tvanbelle-vibecode`, `us-west1-b`, repo
  path, `GLOBAL_CAP`/`HARD_CAP`.

### 6.1 Match running and orchestration

| tool | purpose | verdict for 2023 |
|---|---|---|
| `tools/gauntlet.sh` | Headless gauntlet on the VM. Raw `java ... battlecode.server.Main` (no Gradle per game), `-Dbc.server.mode=headless`, per-game replay file, parallel jobs, random 25-map sample (or pinned `MAPS`), setsid-detached remote runner, 45 s poll, results/reasons/summary, keeps losing replays, re-execs from a private copy so editing the script mid-run cannot corrupt it, warns on duplicate in-flight runs | **Adapt.** Core loop is gold. Change JDK, flags, property names (verify against 3.0.15), map list, parsers |
| `tools/lib.sh` | `ensure_vm` (starts a stopped VM on demand), cached IP, plain ssh/scp with the gcloud key (gcloud ssh stalls under load) | Adapt (names) |
| `tools/remote-slot.sh`, `semaphore-test.sh` | flock counting semaphore held for each game's lifetime; `GLOBAL_CAP`/`HARD_CAP`; test reproduces the old check-then-take race (peak 8 vs cap 7) | **Steal as-is** |
| `tools/collate.sh`, `gauntlet-collect.sh` | collate raw results; recover runs whose driver died (`--list`, `GAUNTLET-COMPLETE` marker, `!! INCOMPLETE` label) | Adapt (parsers) |
| `tools/vm-match.sh` | single matches; builds in a sibling directory so `./gradlew run` never rewrites `build/classes` under running games | Adapt |
| `agents/darla/tools/head-to-head.sh` | candidate vs explicit reference on all maps, both sides; flock-serialised; never identifies its run by `ls -1t` | **Steal** (the decision instrument) |
| `agents/darla/tools/paired-roster.sh`, `widen.sh`, `widen2.sh`, `roster-screen.sh` (+ `roster-screen-maps.txt`) | 450-key paired roster vs 3 frozen opponents; alternate opponent sets; pinned 25-map paired gate | **Steal / adapt** (opponent lists) |
| `agents/darla/tools/replicate.sh` | fresh random-sample replication (held-out instrument) | Steal |
| `agents/darla/tools/make-arm.sh` | create an arm by sed and **prove** the package line, a non-empty diff and the intended change. Born from `darla14`, a 0/72 forfeit where the sed matched nothing | **Steal** |
| `agents/darla/tools/accept-iteration.sh` | freeze, promote, print the diff; refuses to overwrite a snapshot; does not commit (the write-up needs a person) | **Steal** |
| `agents/darla/tools/arm-runner.sh`, `idle-filler.sh`, `jobs.sh` | queue file drained forever (flock, setsid, skips finished arms); idle filler runs absolute-strength samples and yields to real jobs; one registry of job types with a self-check | **Steal** if running unattended |
| `agents/darla/tools/watch-state.sh`, `status-line.sh` | watch artefacts (`summary.txt`) not logs; one-line RUNNING/WAITING/IDLE (skips orphans by write freshness) | Steal |
| `agents/darla/tools/disk-guard.sh`, `tools/driver-prune.sh`, `tools/vm-prune.sh` | replay pruning on driver and VM (keep newest N runs, minimum age); two-stage guard | Adapt. Size the disk at 50G instead |
| `tools/tournament.sh`, `tournament-report.py`, `cron-tournament.sh`, `systemd/bc25-tournament.*` | round-robin from HEAD (never the working tree); per-bot compile in isolation (a failed compile forfeits); report with dedupe warnings, swept maps, attribution when an opponent is unchanged; systemd timers in Pacific time | Adapt **only** if multiple lineages or archetypes are kept |
| `tools/benchmark.sh`, `benchmark-arm.sh`, `benchmark-replay.sh`, `benchmark-collect.sh`, `benchmark-collate.sh`, `benchmark-history.py`, `cron-benchmark.sh` | external yardstick: no replay written **by construction** (omits `-Dbc.server.save-file`); arm benchmarking; opt-in replay variant; idempotent HISTORY regeneration | Adapt if we have any external yardstick bot. The by-construction design is the transferable idea |
| `tools/agent-watchdog.sh` + `systemd/bc25-agent-watchdog.*` | nudges the coordinator tmux session if its heartbeat goes stale (survives usage-limit pauses) | Adapt if running long unattended sessions |
| `tools/agent-commit.sh`, `alice/tools/ac.sh` | commit through a private git index; commit from any cwd | Skip unless several agents share one checkout |
| `tools/isolation-sweep.sh` | quarantines sibling transcripts and replays in a shared scratchpad | Skip (single lineage) |

### 6.2 Engine and replay analysis

| tool | purpose | verdict |
|---|---|---|
| `tools/engine-jar.sh`, `engine-javap.sh` | resolve the **pinned** engine jar (refuses a version mismatch; the VM held 1.0.0 beside 3.1.0); run javap where a JDK exists | **Steal the pattern.** Change the jar glob to battlecode23 and pin 3.0.15 |
| `tools/replay-dump.sh`, `tools/replaydump/ReplayDump.java` (36K) | replay to text using the engine jar's own `battlecode.schema` classes: headers (size, symmetry, walls), per-sample team aggregates, every spawn and death, action window, per-robot track, ASCII arena, coverage self-check against engine totals, indicator strings opt-in per team, final-round flush | **Adapt / rewrite** for the `.bc23` schema. Keep the design: engine schema classes, gzip, self-check, stride 1, flush last round, opt-in indicators |
| `tools/mapdata/ruinscan/RuinScan.java`, `ruin_parity.txt` | reads `.map25` flatbuffers from the jar; corpus facts (parity traps, density outliers) | Adapt to `.map23`: islands, wells by type, HQ count/positions, symmetry, size |
| `bob/bob-tools/map_symmetry.py` | symmetry type from map data | Adapt |
| `tools/map-resample.py` | bootstrap and jackknife over maps; distance from the mirror null | **Steal as-is** (reads results.csv) |
| `tools/map-subset.py` | pooled vs pair decomposition on a map subset | Adapt (only with ≥ 3 bots) |
| `bob/bob-tools/gate.py`, `gate_sd.py`, `stage0.py` | gate with units in names; gate in sd with finite-population correction; stage 0 that refuses to print the verdict | **Steal** |
| `carol/carol-tools/gateverdict.py`, `noisefloor.py`, `gatepower.py`, `sampledgate.py`, `stage0.sh`; `carol/tools/margin.py` | gate application; noise floor from a policy-identical pair (with a ≤ 0.25 sanity bound); FPC power; derive the sampled gate from a census; margin that refuses the wrong referent | **Steal** (consolidate into one module) |
| `alice/tools/noise-floor.py`, `determinism-check.sh`, `diff-runs.py`, `e2-gate.py`, `roster-stale.sh`, `unconfirmed.sh` | phase-twin floor; cell-by-cell determinism diff; game-by-game run diff; VOID-first gate in code; stale-roster alarm (non-zero exit); unconfirmed-keep ratchet | **Steal** (determinism-check and diff-runs first) |
| `tools/bot_identity.py` | identifies which build played by content hash (package line normalised) | Steal |
| `tools/progress_lib.py`, `track_vs_old_bots.py`, `plot_vs_old_bots.py`, `plot_progress.py` | frozen-roster history CSV and charts (UTC stored, Pacific displayed); refuses benchmark bot names | Adapt |
| `agents/darla/tools/plot_arms.py` + `progress/arms.txt` | dose-ladder charts per axis | Adapt |
| `tools/redact-2025.py` | drop every blank-line block mentioning a forbidden year, **before** reading | **Steal** (as a 2023 redactor; this project already did that) |
| ~100 one-off census scripts in `alice/tools`, `bob/bob-tools`, `carol/carol-tools` | per-hypothesis replay censuses | Skip. Too BC25-specific; the pattern is what transfers |

### 6.3 Operational documents

- `RESTART_SESSION.md` (tmux `~/bc25`, `--continue`, re-arming the `/loop` heartbeat, permission modes; deny
  rules work live in bypass mode) and `WIPE-RUNBOOK.md`: **adapt**.
- `.claude/README.md` permissions policy: **adapt**. Prefer moving a dangerous step inside a checked script over
  widening a permission. `pgrep -fa` before `pkill`, and never a pattern matching the shell running it.

---

## 7. Pitfalls and gotchas that cost time

The cost is given where the document states it.

### Measurement and statistics

| pitfall | cost / evidence |
|---|---|
| Unused mechanic never found until an API sweep (bc22) | **81 iterations**. BC25's first sweep at iteration 29 found **37 of 68** RobotController methods unused, including a whole mechanic |
| Self-play blind spot (shared defect invisible in-family) | **11 iterations** behind a 95.8% self-measured win rate |
| Premise without provenance ("ruins saturate", one map, late, self-play) | carried **44 iterations**, killed 3 |
| Gate in the wrong unit (win count vs margin) | every gate was "1.0 sd wearing a 2.0 sd label"; a published 6.8 sd was really 3.39 sd |
| Binomial noise bands on a deterministic engine | over-stated spread ~2x; a real 2-sd accept was hedged, and a rejected candidate had to be accepted on review |
| Stale absolute instrument | four accepts unmeasured; the live bot was losing to its own iteration-39 snapshot (18/50, −7 net swept) |
| Stage-0 probe map was a corpus outlier (Leaf: 3,600 area, 52 ruins, 99th percentile) | over-stated 3 mechanisms in one session; one "won there and then lost 38/150" |
| Only ever traced two maps from one regime | 16 consecutive iterations attacked one failure mode; the untraced band was 64 of 150 games |
| Mirror package left stale | "an ordinary head-to-head against a stale opponent"; two nulls one accept apart disagreed on 6 of 40 games |
| Inverted referent in a gate tool (`gateverdict.py` counted the baseline's wins as the candidate's) | would have reported a −28 regression as ACCEPT |
| `ReplayDump --every N` dropped up to N−1 rounds at each game's end | the one bias that would have faked iteration 47's result; use stride 1 |
| Reading a dump before its writer exited | 41% read off a partial file that finished at 4.1% |
| Indicator-string census without a window | read "0 occurrences" from a run that never looked; fixed by reporting withheld counts |

### Arms, builds and process

| pitfall | cost / evidence |
|---|---|
| sed arm that matched nothing (`darla14`) | 0/72 forfeits that briefly looked like a catastrophic result |
| `producer \| grep -q` under `set -o pipefail` (SIGPIPE 141) | a guard that fails *because* it matched; recorded as sound after one rerun |
| `&&` chain across a heredoc | push and launches ran after a failed build; a benchmark staged a package that did not exist |
| Falsifier read a counter the arm did not carry (`darla82`) | an un-evaluable falsifier; needed a whole extra arm |
| Per-robot statics assumed shared (`darla70`) | an arm provably no-op (75/150, all maps split 1-1); repeated right after being diagnosed |
| Five constants never varied while "exhausted" was claimed | one of them later gave the v3 accept (+12) |
| Self-imposed rule became a stall ("no same-day rebuilds") | about 2 hours with only the idle filler running |
| Commit without push | **31 commits** unpushed, including two accepted iterations and the notebook |
| Watcher tailing named logs (and `tail -F glob` expands once) | results unread for **73 minutes**; mean commit gap of 44 minutes over 8 hours |
| Two drivers wrote one run directory (check-then-act) | a 450-game reference run lost |
| Identifying a run by `ls -1t` (collation rewrites mtimes) | reported "123/150" for the wrong run; the real result was 352/450 |
| Agents re-reading all doctrine at every cold start | ~77k tokens each; "on the order of a million tokens" a day |

### Infrastructure

| pitfall | cost / evidence |
|---|---|
| Editing a bash script while it runs | killed the collation of a finished **450-game** tournament ("syntax error near unexpected token") |
| VM disk 20G | filled on 2026-09-11 and **killed three arms mid-run**; 50G recommended. Driver root hit 100% and `git commit` failed with ENOSPC |
| Pruning replays too aggressively | deleted a control replay 6 minutes before it was needed; replays are the only mechanism evidence |
| 2GB driver | OOM killer took a shell loop and its benchmark with no trace; the session reached ~430MB RSS |
| Two engine jars in the gradle cache | a lineage decompiled 1.0.0 and caught it only because `getChips` was missing |
| `javap` with stderr suppressed | reported "no such method" when the cause was no JDK on PATH |
| `pkill -f` pattern matched its own shell; unscoped `pgrep -f <run-id>` matched the polling loop | |
| Testing a failure path by mutating a shared live file (`engine_version.txt`) | confused a running lineage |
| Commit messages in double quotes with backticks | code silently vanished from the message; use a single-quoted heredoc |
| Web summaries of post-mortem PDFs (bc22 note) | "confident fabricated quotes"; extract the text and read it |

---

## 8. Top 15 takeaways for the 2023 project, ranked by expected value

1. **Make the decision instrument a paired comparison on identical keys, over the full map pool, both sides.**
   Quote margins in games and z on discordant keys (McNemar), never binomial. Use the 3-opponent screen only to
   catch catastrophes. This turned a "+4, noise" into "+22, z +3.59" for the same change. Build
   `head-to-head.sh` / `paired-roster.sh` equivalents in week 1.
2. **Get an opponent that is not your own family as early as possible, and benchmark on every accept.** In-family
   roster gains of +19, +15 and +29 bought +2, +2 and −1 against `v3`. The held-out estimate ran at about 60% of
   the in-pool one. For 2023 that means several deliberately different archetypes (rush, eco, island-rush),
   plus any external bot we are allowed to run, re-run after each accept. Never tune toward one opponent.
3. **Verify determinism, then calibrate your own noise floor with a policy-identical, phase-different twin.**
   Identical code gives zero variance, but code changes perturb the PRNG: sd 4.8-6.5 games per 150. Put the unit
   in every name (sd of margin = 2 x sd of wins). Gates and floors must be in the same unit.
4. **Hunt absolute degeneracies with a state-token census of one replay, before inventing mechanisms.** Every
   unit writes a short state token plus mechanism counters in its indicator string; count tokens across robots
   and follow the biggest block. This found the 416-turn refill latch (+12/+19) and the stuck-move rate
   (+13/+15). Put latch counters on every latched state (carrier return, well queue, anchor carry).
5. **Wire bytecode monitoring and the indicator-string contract into iteration 0** (`monitorAndYield`: round
   before/after = overrun, >80% = near-miss, `ov>0` voids an arm). BC23 limits (10k launcher, 12.5k carrier) are
   tighter than BC25's 17.5k, and even BC25 overran on a terrain sweep.
6. **Navigation: greedy plus a bounded escape hatch triggered by a measured stuck counter.** Do not replace greedy
   with wall-following (−14 vs +13). Break ties on robot ID, not compass order. Measure the per-map stuck rate
   first. Treat currents and clouds explicitly (inference).
7. **Infer map symmetry from what is already visible, and check the consumer exists before building the
   derivation.** BC25: reflection was two-thirds of maps, rotation only 27 of 75; worth little there because
   the answer fed a fallback branch. BC23 (inference): enemy HQ locations follow from own HQs plus symmetry, and
   launchers consume that every game, so expect high value. Statics are per robot; share eliminations through
   the array.
8. **Tally how games are actually won before choosing a thesis, and plot the early-lead variable past the round
   where it predicts.** Darla's thesis died on a 96.5% coverage win-type tally. Alice's "r300 tower leader wins
   79-81%" hid that 48% of her losses were games she led at r300. In BC23: islands and anchors vs the round-2000
   tiebreak; measure the split.
9. **Every threshold must sit inside the measured operating band of the quantity it gates, and prefer demand
   tests to fixed shares.** Several reserves were effective off switches (realised share 1.2-2.7% vs an intended
   15%; an upgrade gate fired 4 times in 9,147 turns). "Money tower only when chips are spare" was the strongest
   roster accept (z +3.26). Self-limiting conditions need a bound that fires regardless (towers ≤ 2 AND
   round < 100).
10. **Find which resource binds, in which phase, and price reallocations against what they displace.** Use
    surplus measurements: 42,712 chips in surplus, but only 1,502 in the deciding window. "Can't vs won't" means
    checking whether the stock ever hits its cap. In BC23, run this for Ad vs Mn vs Ex per HQ before tuning
    carrier allocation (inference).
11. **Integrate rather than isolate.** One lineage that reused all findings and an overlooked 38-line fork went
    from 24.7% to 34.0% on day one and 56% later; the isolated lineages co-evolved into a joint local optimum.
    If we run several agents, make them archetype or opponent generators, not rival developers.
12. **Keep a closed-directions ledger with closure KIND, the closing number and a testable re-open condition,
    and grep it before proposing.** Distinguish closed from blocked from ceilinged. A closure that is "relative to
    a rival" must be re-examined when the reference changes. Periodically enumerate never-varied constants and
    set-aside notes: `RUIN_BAN_ROUNDS` 250 -> 10 was +12 vs v3 after being "exhausted".
13. **Turn lessons into tools that refuse the error.** `make-arm.sh` (proves the diff), `stage0` scripts that
    refuse to print the winner, gate scripts that apply registered branches in code (VOID first), a margin tool
    that refuses the wrong referent, `accept-iteration.sh` with an exact promotion-test value, a stale-roster
    alarm. Written lessons repeatedly failed to fire, sometimes within the hour.
14. **Infrastructure first, sized properly, and robust to session death.** Raw `java` headless runs, a flock
    semaphore, setsid-detached remote runners with collect-on-recovery, artefact-based watchers, an always-full
    queue (≥ 3) plus an idle filler, scripts re-exec'd from a private copy, 50G disks, push after every accept.
    Steal from `tools/` and `agents/darla/tools/`. Adapt the JDK (8), the jar pin (3.0.15), parsers and the
    `.bc23` replay dumper.
15. **Keep the method lean and token-cheap.** Short read-first indexes, grep-only archives, a CLOSURE_MAP or
    resume point by run-id, resume rather than cold-start, and at most a dozen core rules. The two lineages with
    the most elaborate methodology (86 METHODS entries, 25k-line logs) ended at 17-25% vs `v3`. Rigor protected
    against false accepts but did not find strength; trace-driven degeneracy fixes and outside opponents did
    (my judgement from the record).
