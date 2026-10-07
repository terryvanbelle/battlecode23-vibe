# Prior project BC25: tools, infrastructure and bot code (slice `bc25-tools-code`)

Research reader's report for the 2023 ("Tempest") practice project. Source: the 2025 project at
`/home/terryvanbelle/projects/vibe/2025` (code read directly) and its documents, which I read only from the filtered copy
`/home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc25/`. Numbers are quoted as the documents state them.
Anything I infer is marked **(inference)**.

---

## 1. Scope

### What the 2025 project was

Four bot "lineages" developed by Claude agents on one repo between 2026-09-06 and 2026-09-15:

- **alice, bob, carol**: three isolated agents started together. Each had its own workspace `agents/<name>/`, and the
  three met in a round-robin tournament twice a day. Bob was retired on 2026-09-10 and alice and carol later that day.
- **darla**: started 2026-09-10 by the coordinator after the retirements, the only live lineage from then on. Its
  `src/darla/RobotPlayer.java` header still reads "Carol iteration 0: minimal instrumented bot", and its method list
  matches carol's line for line. **(Inference: darla's code is a fork of carol's bot plus darla's changes. DESIGN.md
  says it was "written from scratch but not from nothing" and that `darla1` is "carol's economy plus the siege".)**
- External yardsticks: two downloaded BC25 finalist bots, `v3` and `TSPAARKHS`. They lived only on the VM, and I did
  not read them. I read only the scripts that score against them and the committed `benchmarks/HISTORY.md`.

### Read in full (code, directly from the repo)

| path | size | notes |
|---|---|---|
| `tools/lib.sh` | 3.2 KB | VM/ssh helpers, IP cache, workspace detection |
| `tools/remote-slot.sh`, `tools/semaphore-test.sh` | 1.9 + 1.8 KB | cross-runner flock semaphore and its race test |
| `tools/gauntlet.sh`, `tools/collate.sh`, `tools/gauntlet-collect.sh` | 13.3 + 6.2 + 4.7 KB | the main evaluation runner, its collation, and run recovery |
| `tools/tournament.sh`, `tools/cron-tournament.sh`, `tools/systemd/*` | 12.6 + 2.2 KB + units | the twice-daily round-robin |
| `tools/vm-match.sh`, `tools/engine-jar.sh`, `tools/engine-javap.sh` | 2.7 + 3.1 + 2.1 KB | single debug match; pinned-engine probes |
| `tools/agent-commit.sh`, `tools/agent-watchdog.sh` | 3.1 + 4.3 KB | private-index commits; outside-session watchdog |
| `agents/darla/src/darla/RobotPlayer.java` | 959 lines, 57 KB | latest and strongest bot, read end to end |
| `agents/darla/tools/{arm-runner,idle-filler,make-arm,accept-iteration,head-to-head,paired-roster,roster-screen,replicate,widen,jobs,disk-guard}.sh` | 976 lines total | darla's experiment pipeline |
| `agents/bob/src/bob/{Nav,G,RobotPlayer}.java` | ~150 lines | bob's architecture: multi-file, greedy navigation |

### Skimmed (headers and docstrings, or targeted ranges)

- **Remaining tools**: `isolation-sweep.sh`, `benchmark.sh`, `benchmark-arm.sh`, `benchmark-replay.sh`,
  `benchmark-history.py`, `map-resample.py`, `map-subset.py`, `track_vs_old_bots.py`, `progress_lib.py`,
  `bot_identity.py`, `tournament-report.py`, `replay-dump.sh`, `replaydump/ReplayDump.java` (header and design comments,
  36 KB file), `driver-prune.sh`, `vm-prune.sh` and `redact-2025.py`.
- **Darla's other tools**: `status-line.sh`, `watch-state.sh`, `plot_arms.py`.
- **Per-agent tools**: about 20 scripts in `agents/{alice,bob,carol}/{tools,bob-tools,carol-tools}`, headers only.
- **Bots**: method signatures and the main loop of `agents/alice/src/alice/RobotPlayer.java` (655 lines). Carol's
  `RobotPlayer.java` (903 lines) only to confirm it is darla's ancestor.
- **Build files**: `arena/build.gradle`, including the `printClasspath` and `run` tasks.
- **Filtered documents**: `README.md`, `OBJECTIVE.md`, `TRAINING_LOG.md` (top level, 3 KB), `MULTI_AGENT.md` (read in
  full), `TRAINING_ALGORITHM.md` (Phase 0 to the gauntlet section), the `METHODS.md` index, and the first sections of
  `RESTART_SESSION.md` and `WIPE-RUNBOOK.md`. Also `tools/engine-facts.md` (first two facts), `tools/mapdata/README.md`,
  `tools/agent-prompts/{alice,resume}.md`, `benchmarks/HISTORY.md` (in full) and
  `tournaments/20260910-1300/report.md`.
- **`agents/darla/DESIGN.md` (633 KB, 11,641 lines)**: every heading, plus about 1,000 lines of targeted sections. These
  were the accept write-ups for iterations 1–7, the instrument-resolution and overfitting audits, the "first look at
  v3" opening analysis, the owner rule changes, and the communication, symmetry, navigation, splasher and SRP results.

### Skipped, and why

- **Per-lineage training logs and archives**: `agents/{alice,bob,carol}/TRAINING_LOG.md` (1.1–1.5 MB each) and
  `LEARNINGS_ARCHIVE.md` (160–220 KB each). These are grep-only by the project's own rule, and the methodology content
  belongs to the method slice.
- **`METHODS_EVIDENCE.md` (169 KB) and `reference/*` (cross-year digests)**: other slices cover them.
- **The ~600 snapshot and arm packages under `agents/*/src/`**: only the latest bot of each lineage matters for
  architecture.
- **Never opened**: `tools/.venv` (vendored Python packages) and the `benchmarks/` bot code, which is not in the repo
  anyway.
- **2023 project files**: I glanced at `2023/tools/gauntlet.sh`, `lib.sh` and `CLAUDE.md` headers, but only to write
  the "what must change" notes in section 6.

---

## 2. What worked

### 2.1 Darla's results on the external yardstick

Benchmark records (`benchmarks/HISTORY.md`, 150 games = 75 maps × 2 sides vs `v3`):

| lineage | first | best | runs |
|---|---|---|---|
| bob | 4.7% | 4.7% | retired |
| alice | 8.0% | **17.3%** | `20260910-0149` |
| carol | 5.3% | **24.7%** | `20260910-0149` |
| darla | 34.0% (`20260910-2317`) | **56.0%, 84/150** (`20260915-1907`) | 42.0 → 43.3 → 46.0 → 48.0 → 56.0 |

Against `TSPAARKHS`, nobody beat about 1%: alice 1.3% and darla 0.7%. The owner then declared it "not a target"
(DESIGN.md, "WHAT THIS PROJECT IS FOR").

Darla had 7 accepts out of about 193 arm packages (darla2–darla193) in about 5 days. Each accept with its evidence:

| iter | change (one line each) | evidence as written |
|---|---|---|
| 1 | `SPLASHER_IN_20` 3→14 (splasher share 15%→70%) + `SPLASH_MIN_SCORE` 8→14, jointly | h2h vs baseline 97–53 (64.7%), z +3.59 sd, swept 32 win / 10 loss. This came after 27 failed arms; the screens had shown +2, +2 and +4. |
| 2 | don't queue at a dry tower: in `walkHomeIfDry`, unlatch if already within r²≤2 of the target tower | 450-key paired roster 326 vs 307, discordant 41–22, z +2.39 |
| 3 | "escape hatch" bug-walk in `stepToward`, engaged only on the turn after the stuck condition fired for the same target | h2h 88/150 (+13). Paired roster +15. Stuck-move counter on Bread 21.6%→16.1%, on Portal 27.8%→18.7%. |
| 4 | money tower only when chips are actually scarce (`towerTypeFor`) | standard roster 17–15 (z +0.35), widened roster 24–9 (z +2.61). v3 64/150. |
| 5 | soldiers-only opening until the 3rd tower, bounded by round 100 | combined rosters z +2.70. v3 69/150 = 46.0%. "Positive on every instrument and every individual opponent." |
| 6 | four mechanisms combined (`MONEY_MOD` 4→2, 100-round opening, one floor-exempt soldier per 3 splashers per tower, ruin-unlock splash) | paired roster 398/450 (88.4%), 56 vs 20 discordant, z +4.13. v3 72/150. Alone, `darla145` gave +8 (z +1.21) and `darla170` +4; together +36. |
| 7 | `RUIN_BAN_ROUNDS` 250→10 | v3 84/150 (56.0%), 16 vs 4 discordant vs `i6`, z +2.68. Monotone dose curve: 250→72, 100→74, 50→76, 25→77, 10→84. |

Effect sizes: iterations 1–6 moved the in-family roster a lot. Only iterations 5 and 7 moved `v3` measurably: 43.3% to
46.0%, then 48.0% to 56.0%.

### 2.2 Matching the instrument to the question

- **The head-to-head was the right instrument for one change.** Darla's iteration 1 write-up puts it this way: "Both
  constants screened at +2 and the pair at +4, all inside a 6.7-point floor … A direct match plays both builds on the
  same 75 maps, so map difficulty cancels instead of compounding, and a +4-on-144 lean resolves into +22-on-150 … **The
  bottleneck was never the VM or the ideas; it was measuring the wrong difference.**"
- **The paired 450-key roster** (candidate vs 3 frozen lineages × 75 maps × 2 sides) plus a McNemar test on discordant
  keys became the standing accept instrument. It "triples the keys … without weakening the pairing"
  (`paired-roster.sh`).
- **Measured noise floor.** Darla's idle filler produced fresh-sample baselines of 97, 94 and 101 out of 150. Observed
  run-to-run sd was 2.34 points against a binomial 4.08. Over 37 samples the shipped build scored mean 102.5/150,
  sd 7.34. Conclusion: "a 150-game fresh sample cannot resolve anything under about 5 points (2 sd)", and "this
  instrument can only see damage, not improvement, at the sizes I have been producing."

### 2.3 Determinism-based statistics (MULTI_AGENT.md, carol, alice, bob tools)

- **The mirror null.** Identical code split "all 20 maps, exactly 20/40, with zero swept maps". A candidate had been
  rejected as "inside the noise floor" and then had to be accepted on review.
- **The error bar is over maps, not games.** `tools/map-resample.py` bootstraps and jackknifes over maps. The binomial
  model "overstated the spread ~2x".
- **Census vs sample.** Carol's `sampledgate.py` and bob's `gate_sd.py` derive the variance of a 25-of-75 map draw with
  the finite-population correction `Var = n·s²·(N−n)/(N−1)`, paired per map.
- **Perturbation floor.** Any code change perturbs the PRNG stream, so even a policy-identical pair has a floor.
  Alice's `noise-floor.py` measures it with a seed-offset twin (`alice_phase`); carol's `noisefloor.py` does the same.
- **Deduplication.** Tournament games between unchanged commits reproduce exactly ("150/150 identical"), so
  `tournament-report.py` and `map-subset.py` deduplicate before pooling.
- **Exact promotion tests.** Because the engine is deterministic, a promoted build must reproduce its arm's score
  exactly. For example, "must return exactly 87/150". Darla recorded ten-plus such checks passing, which caught build
  or packaging errors for free.

### 2.4 Replays against the real opponent, once the owner allowed them

The owner granted `v3` replays on 2026-09-14 (`tools/benchmark-replay.sh`). The first look found that "the race is lost
in the first hundred rounds":

- On `shell`, v3's first five towers came at r34, 64, 119, 148 and 203. Darla's first and only tower came at r266.
- Robots built by r40: darla-i4 had 1 soldier and 4 splashers; v3 had 6 soldiers and 1 splasher.

This produced iteration 5 and then iterations 6 and 7. "None of this was visible until the owner granted replay access
to `v3` games. The roster could not see it, and 1,350 paired games did not."

### 2.5 Engine-verified mechanics, the biggest single code wins

Each of these reads like a bug fix rather than a strategy:

- **A soldier attack on enemy paint costs 5 paint and does nothing.** The engine deducts the cost before it checks the
  tile (`engine-facts.md`, javap offsets 58 vs 178). Carol measured "71–85% of ALL soldier attacks were discarded this
  way, burning 42–55% of the entire soldier paint budget". The fix is a guard on the engine's own predicate in
  `workOnRuin`.
- **Denied ruins.** One enemy-painted pattern tile makes a ruin permanently uncompletable for a soldier. Carol's win rate
  fell "43.5% → 34.9% → 23.1% → 14.0% across ruin-count quartiles (Cochran-Armitage trend z = −8.44)". The fix is the
  `banRuin` ring buffer with `BAN_CAP = 8`.
- **Radius asymmetry, used for the siege.** A splasher reaches distance 4; a paint or money tower answers only to 3.
  "darla1 beats carol 30/48 (62.5%) … the siege is worth roughly +12 points, measured."
- **Gates above where the treasury actually sits are off switches.** For example, a tower upgrade fired "4 times
  against 9,147 `upgPoor`" because "a gate above where the treasury actually sits is not a policy, it is an off switch".

### 2.6 Infrastructure that demonstrably paid

- **Detached remote runners plus recovery.** Runs are `setsid` and survive session death, and `gauntlet-collect.sh`
  recovers their results.
- **A never-idle queue.** Darla's `arm-runner.sh`, `idle-filler.sh` and a state-based watcher turned the VM into a
  24-hour pipeline. About 190 arms ran in 5 days.
- **The shared semaphore is correct.** Peak was 8 games against `HARD_CAP` 7 without the gate and 7 with it
  (`semaphore-test.sh`).
- **Cached replay-dump compile.** It cut "71s of wall time per game" of setup. `ensure_vm`'s cached IP removed a
  measured "32.5s of wall time per invocation".

---

## 3. What did not work / closed directions

### 3.1 Process and objective failures

- **Three isolated lineages co-adapted into a joint local optimum.** From `OBJECTIVE.md`: "Both lineages lose three
  quarters of their games against the external standard, and have spent weeks contesting a three-point gap between each
  other." Their final `v3` scores were 17.3% and 24.7%. Both lineages wrote complete closure maps ("every design premise
  closed") while far from strong. Being ahead of a rival "is not evidence of being near optimal".
- **Roster gains did not transfer.** Darla's accepted iterations worth +19, +15 and +29 games on the roster moved `v3`
  by +2, +2 and −1. Between i1 and i3 the `v3` change was "15–13 of 28 discordant, z = +0.38". Iteration 1, accepted at
  +3.59 sd on the roster, was the very change that made the opening lose to `v3` (70% splashers, so too few soldiers to
  claim ruins).
- **Evaluation-set overfitting.** The owner's audit on 2026-09-13 found "the held-out estimate is ~60% of the in-pool
  one": i3 − i1 = +9.2 games/150 (t +3.84) where the paired instrument predicted about +15. With about 23 arms at a
  z ≈ 2.4 bar, the audit expected "~0.4 expected false accepts". Once `v3` became a selection instrument, it inherited
  the same bias. The 56% figure is therefore a selected number **(the documents say so explicitly; the size of the
  discount is not measured)**.
- **Self-play gates disagreed in sign with the roster.** "darla133 scored 88/150 in the mirror, 13 over the bar, and
  came in 9 games BELOW the incumbent on the 450-game paired roster (McNemar z = −1.08)." Self-play was then demoted to a
  catastrophe check (`roster-screen.sh` header).
- **Early reads of small effects evaporated.** `darla65` (the first use of communication) read +1.14 sd on the h2h. Its
  estimate then ran "+1.5 (n=4) → +0.3 → +1.6 → +2.5 → +0.8 → +0.57 (n=18)" over 2,700 games, SE 1.77, t 0.32, and it
  was rejected.
- **A 12-map mechanism probe over-read the census five times.** For example, darla175's "every mechanism counter up,
  and the census down".

### 3.2 Closed mechanism directions (darla, with evidence)

| direction | result | why it failed (as written) |
|---|---|---|
| Replace the greedy fallback with full bug navigation (`darla82`) | 61/150, −14 | "walked the long way around obstacles a single ±45° dodge would have cleared". The bounded escape hatch won +13 instead. |
| Bug2 leave condition (`darla124`) and "follow terrain" (`darla129`) | 65/150 and 71/150 roster screens | "Navigation was never the soldier problem": soldiers arrive 85% under i5 |
| Symmetry inference by travelling to the mirror (`darla71`) | −0.49 sd, zero eliminations | elimination needs to *see* the mirrored tile across the map |
| Symmetry elimination from terrain in vision (`darla72/73`) | void | bytecode overruns, `ov` 3 and 4–8. `senseNearbyMapInfos(-1)` is about 69 tiles × candidates × `senseMapInfo`. The answer was also consumed only as "the fallback of a fallback". |
| Splashers walk to the nearest enemy paint (`darla88`) | **7/150** | standing on enemy paint drains paint and the 300-paint unit dies. Games shortened from 1,035 to 836 rounds. |
| Splasher repositioning (`darla20` nearest enemy paint; `darla22` and `darla41` enemy-paint centroid) | −38 (−6.33 sd), −22, −7.84 sd | "Positioning is tower-specific" |
| Special resource patterns (SRPs): `darla121/122/123/125/164–167` | down to v3 31/150 (z −5.55) | 226 completions in 12 games with 2 alive. Patterns were bought, broken by its own splashes and bought again. "Line closed for good." |
| Mopper lines (`darla99/101/146–148`) | 22/150 for the flood variant | moppers "walk home 88% of the time and mop 10%" |
| Communication relay, soldiers tell towers about ruins (`darla156`) | closed | relay fired 2,107 times and built 29 soldiers, with no gain |
| Tower defence (`darla106`), defense towers (`darla55`, `darla109`) | null | "3 fires in 1,949 soldier turns" |
| Many constant re-tunes on accepted builds (`CHIP_RESERVE`, `PAINT_FLOOR`, `REFILL_LOW`, `SPLASH_MIN_SCORE`, ratios) | mostly null | `CHIP_RESERVE` 2400 at −9.31 sd and `REFILL_LOW` 100 at −6.37 sd show the incumbent values were near optimal |
| The longer opening (`darla162/163`, to r200/r150) | v3 67 and 66/150 | "the opening bound is 100" |
| Soldiers-first opening alone (`darla102`) | roster +2.57 but v3 −7 | "The opening is worth buying; it is not worth trading for." Gating on tower count alone never lifted on the maps where expansion never began (`darla103/104`). |

### 3.3 Closed infrastructure ideas

- **The fixed-list map screen.** Accepted iterations drift toward the maps in the list. `collate.sh` now warns when a
  run reuses a previous run's map list for an accept screen.
- **A rule as the only control.** Rules alone failed for duplicate sessions (5 occurrences), shared `git add`, scratchpad
  globbing and unscoped `ps`. Each failure ended in a tool-level control. Doctrine 19: "a rule that has to be remembered
  is not a control."
- **Disk pruning on a timer sized for a slow loop.** The VM hit 20G/20G and the driver 100%. A first, aggressive
  disk-guard "deleted the darla15 control replay six minutes before that control was needed".

---

## 4. Method lessons

### 4.1 Training loop

From `TRAINING_ALGORITHM.md` and the darla practice:

- **Phase 0 before strategy.** Digest the spec into `RULES.md`. Probe the engine with `javap`. Sweep the
  `RobotController` API for never-called methods "at iteration 5, every 10 iterations after that, and whenever the loop
  stalls". A prior project lost 81 iterations to an unused mechanic, and this one rediscovered unused mechanics only at
  iteration 29. Also: look for radius asymmetries, build headless runners and a replay-to-text tool first, verify
  determinism, wire bytecode monitoring in at iteration 0, audit play-symmetry, and know the map symmetry contract.
- **The loop.** Pick a target from a measured deficit, trace rather than theorise, pre-register the gate and the
  falsifier, change one mechanism, evaluate in stages, accept or reject, log, commit.
  - **Dose ladders with a byte-identical zero arm.** Darla read curve shapes: "concave with interior optimum",
    "a SWITCH, not a dial", "monotone, steepest at the end".
  - **A pre-registered mechanism counter in the same build as the change.** Darla82's falsifier could not be checked
    because the counter lived in a different build: "when an arm's registered check reads a counter, the arm must
    contain the counter."
  - **Stage 0 refuses to print the verdict.** Bob's `stage0.py` and carol's `stage0.sh` check only that the arms
    differ and the dose landed, so nobody reads a verdict from mechanism data.
- **Darla's accept sequence**, scripted in `accept-iteration.sh`:
  1. freeze the outgoing build as `src/darla_iterN`;
  2. promote the arm and bump `BUILD`;
  3. run the exact promotion test;
  4. run the v3 benchmark;
  5. push.

  It was scripted because "31 commits once sat unpushed" and "the benchmark went two accepted iterations stale".

### 4.2 Gating and statistics, the transferable core

- **Instruments, in the order darla converged on.** About 900–1,350 games per candidate decision **(inference from the
  instrument sizes)**.
  - **12-map probe**: counters only, for the mechanism.
  - **Roster screen**: 25 pinned maps × 3 lineages × 2 sides = 150 games, paired.
  - **v3 census**: 150 keys.
  - **450-key paired roster**: all 75 maps × 3 lineages × 2 sides.
  - **Fresh-sample series**: held out.
- **Accept rule (owner, 2026-09-14).** "An arm is accepted if it beats the shipped build with McNemar z > 2 on the
  discordant keys of either" instrument. The ≥50%-per-lineage floor stays.
- **The swept-map identity.** wins − losses = 2 × (swept − swept against). Sweeps restate the margin rather than
  corroborating it; what they add is the number of split maps (`tournament-report.py`).
- **Partial runs are prefixes, not samples.** Opponents are the outer loop, so an incomplete opponent has played a
  prefix of the map list. "An interim read of one arm at 89% against completed arms at 80% nearly produced a wrong dose
  decision" (`collate.sh`).
- **The resolution budget.** "Detecting a real +3% would need on the order of a thousand games per arm." Resolving
  +5/150 at sd 7.4 on held-out samples "needs roughly 35 samples per side".

### 4.3 Ladder and Elo design

There was no Elo in BC25. The rating devices were:

- the twice-daily round-robin (450 games, standings, head-to-head, sweeps, "vs last" deltas);
- per-lineage frozen rosters (`track_vs_old_bots.py`, holding iteration 0 plus snapshots ending in 1 or 6);
- the external benchmark, records only (`benchmark-history.py`).

The tournament report warns that "standings are relative, not absolute … the three win counts always sum to 450".
Absolute strength came only from frozen opponents and the external benchmark.

### 4.4 Process rules and owner interventions

| when | owner intervention | what it corrected |
|---|---|---|
| 09-09 | resume agents by default (`SendMessage`), cold-start only when forced | a cold start re-read about 5,200 lines (~77k tokens), 20–50% of a session's 150–360k |
| 09-10 | retire bob, then alice and carol; open their workspaces for reading | the account usage limit; the co-adapted optimum |
| 09-10 | `OBJECTIVE.md`: optimise absolute strength, not the rival gap | the joint local optimum |
| 09-10 | cycle agents at about 250k context tokens | contexts ran above 700k (about 965k before compaction); agents were 83% of token spend |
| 09-11 | "the machine is never idle" | led to darla's arm-runner, idle-filler and monitor |
| 09-11 | make "waiting" visible | `status-line.sh` |
| 09-13 | benchmark against v3 on every accept | the benchmark was two accepts stale and 31 commits unpushed |
| 09-13 | overfitting audit of the chart | found the held-out/in-pool ratio of about 60% (kept the criteria anyway) |
| 09-14 | allow `v3` replays, and let `v3` results count for accepts | the roster's blindness to the opening race |
| 09-14 | "WHAT THIS PROJECT IS FOR": practice for a real contest against varied opponents | reframed the target as generalisation; TSPAARKHS is not a target |
| 09-14 ~19:00 | "not much is happening" / "ensure that you don't stall on ideas any more" | darla had queued nothing for about 2 hours; new rule: "at least three items queued at all times" |
| 09-14 ~20:10 | cap at two run drivers | driver memory: "the driver reaped two background waits for memory" |
| 09-15 01:1x | "no wrapping up — keep exploring while the VM has room" | premature wind-down |

### 4.5 How the agents went wrong

- **They optimised the relative metric that was available instead of absolute strength.** Alice and carol spent weeks
  on a 3-point gap.
- **They over-built methodology.** `METHODS.md` grew to 86 numbered entries and alice's `RULES.md` to 30 KB, while the
  bot stayed a ~650–950-line single file far from the external standard. **(Inference: methodology bloat cost
  attention. The darla notebook's best gains came from a few large, concrete fixes found by counting indicator-string
  states in one replay.)**
- **They trusted an instrument that could only see damage**, running 27 arms through it.
- **They applied a reasonable rule ("no rebuilds of refuted arms today") as "no arms at all"**, and stalled.
- **They narrated rather than measured.** METHODS records that "the coordinator wrote down a lineage's *explanation*
  instead of its *measurement*" three times. "Record the measurement, not the explanation" is its most-repeated rule.
- **They made concurrency mistakes on shared state** (sections 6 and 7).

---

## 5. Bot architecture and the basics

### 5.1 Overall shape

All four BC25 bots were small:

- **darla**: 959 lines in one `RobotPlayer.java`.
- **carol**: 903 lines.
- **alice**: 655 lines.
- **bob**: 783 lines over 7 files (`G.java` globals, `Nav.java`, one class per unit type, `Tower.java`).

Structure common to all:

- **Static state** per robot (statics are per-robot, a fact darla70 had to discover).
- **A `switch` on `rc.getType()`** inside `while(true)`.
- **try/catch around the turn body**, which converts exceptions into indicator text (`"GAE:"`, `"EXC:"`).
- **A `finally` that runs the monitor and calls `Clock.yield()`.**

No bot used BFS, flow fields or a pathfinding library.

### 5.2 Instrumentation, the one practice to copy verbatim

`RobotPlayer.monitorAndYield(int startRound, String state)` in darla:

- **Overrun.** `endRound != startRound` counts a confirmed overrun (`ov`). Using more than 80% of the limit counts a
  near-miss (`nm`). It also tracks `bcMaxUsed`.
- **A BUILD tag in every indicator string**: `"[" + BUILD + "] bc=..."`. That way a replay of a build against its own
  snapshot can be split by team. Each arm gets its own tag from `make-arm.sh`.
- **Every decision counter in the indicator**: `rzf`, `sx`, `mp`, `rt` (refill trips), `ht` (home turns), `dn` (deny
  bans), `bs` (ban skips), `mv` (stuck/tried moves) and so on, plus a per-unit state token such as
  `S HOME`, `IDLE-ALLY4/0`, `P SPLASH`, `P cd`, `P noPaint`, `approach`, `ring` or `backoff`.
  - Darla's iteration 2 "came from counting soldier `state` tokens in one replay". It found `S HOME` was 63–79% of
    soldier turns and one soldier "latched for refill once and commuting for 416 straight turns".
  - Bob also prints `BCMON` lines every 500 rounds.

**2023 mapping.** This transfers directly. Use `rc.setIndicatorString` with a build tag and counters, and
`Clock.getBytecodeNum()` against the limit for the robot type. In 2023 that is HQ 20000, carrier 12500, others 10000,
so read the limit per type rather than one constant. The 2023 replay dumper must be able to print indicator strings per
team.

### 5.3 Economy

The resource-binding analysis is the transferable technique. Darla's tower code
(`runTower`, `towerTypeFor`, `walkHomeIfDry`, `refillIfPossible`) carries several such fixes, each with its measured
justification in the comments.

- **Find which resource binds.** "100.0% of chips-available no-builds are `tpIn < paintCost`". Then build income only
  for the binding resource. Iteration 4's rule makes a money tower "only when chips are ACTUALLY scarce" (threshold
  `CHIP_RESERVE + SPLASHER.moneyCost`).
- **Reserve dead band.** A reserve that protects a 1000-chip build can pin the treasury in
  `[RESERVE, RESERVE + cheapest)` for ever. "On Castle 83.4% of tower turns, DefaultLarge 79.3%". The fix is the
  `pinnedTurns`/`stagnantTurns` release after `STAGNANT_ROUNDS = 10`. The reserve itself proved load-bearing:
  `CHIP_RESERVE` to 0 made "towers collapse".
- **Cheap units starve expensive ones through an unchecked second resource.** In `PAINT_FLOOR = 200`, the mopper
  (100 paint) prevented the soldier (200) from ever being afforded: "0.9^40 = 1.5%". The fix protects the expensive
  unit's floor.
- **"Spending is the investment."** Cutting spawns by 78% "banked nothing". "Never gate a paint-costly action on chips:
  rank correlation −0.496."
- **Logistics hysteresis.** Below `REFILL_LOW`, latch and walk to the nearest remembered tower (a `towerMem` list of up
  to 12). Unlatch at half capacity, and also unlatch if already standing beside the tower ("queueing at a dry tower is
  strictly worse than acting with what we hold"; this was iteration 2).
- **Exact transfer amounts.** Alice's refill notes "a withdraw credits via `addPaint` (which CLAMPS at capacity) while
  debiting the tower the FULL amount, so over-asking silently burns the tower's paint".

**2023 mapping (inference).**

- **Carriers are the paint-refill problem turned inside out.** Carrier move cooldown grows with load, so the same
  hysteresis and "don't queue at a dry or full site" logic applies at wells (which can be crowded) and at the HQ.
- **Ad vs Mn is the chips-vs-paint question.** Launchers need Mn, carriers and amplifiers need Ad, and anchors need
  both (80/80). The 2025 lesson is to measure which resource blocks builds ("no-build because X") before tuning ratios.
- **Anchor saving is the reserve dead band.** The 2023 bot will need an anchor reserve with an explicit release valve.
- **The opening race likely decides the game, as it did against v3.** In 2023 the analogue is early carriers, wells and
  launchers before about round 100.

### 5.4 Navigation and pathing

Darla's `stepToward(MapLocation to)`:

1. **Greedy.** Try the direct direction, then ±45°, then ±90°.
2. **Symmetric tie-breaking.** The left/right preference comes from `rc.getID() & 1`, so obstacle-skirting is not
   correlated with team identity ("play-symmetry").
3. **The escape hatch.** Track `mvLastTo`/`mvLastD`. If the last step toward the same target did not reduce
   distance (`stuckLast`), wall-follow with a persistent `bugDir` until a move succeeds, rotating back toward the wall
   after each step.

Iteration 3 accepted this at +13 and +15. Full bug navigation as the fallback lost 14 games.

Bob's `Nav.navTo` is the same greedy cone plus a first pass that avoids enemy paint and a random move after 3 stuck
turns.

**2023 mapping.** Start with greedy plus a bounded bug escape, but 2023 adds three things 2025 lacked:

- **Currents** push units at end of turn.
- **Clouds** slow cooldowns by 20%.
- **Wells and HQs are destinations, and carriers repeat the same trip.**

**(Inference: a cached BFS or flow field from each HQ to known wells may pay off in 2023 where it did not in 2025,
because the 2023 trips repeat.)** The 2025 evidence says to engage any heavy fallback only on a measured stuck
condition.

### 5.5 Exploration

- **Far target.** `newExploreTarget()` samples 4 uniformly random map coordinates and keeps the farthest. The target is
  replaced when reached (d² ≤ 8), after 6 stuck turns, or after 120 turns of age.
- **Frontier seeking.** `nearestVisibleEmpty()` scans the whole vision disc for an unpainted tile when nothing is
  paintable within action range (iteration 14 of the old lineage).
- **Ruin memory.** A ban list (`ruinBanned`, `banRuin`, `BAN_CAP = 8`, `RUIN_BAN_ROUNDS = 10` after iteration 7) and a
  patience timeout (`RUIN_PATIENCE = 40`).
- **Remembered ruins go stale.** "95% of remembered ruins have enemy paint on the pattern by arrival" (`darla139`).

**2023 mapping (inference).** In 2023 the shared array lets the team share discovered wells and islands. The 2025
lesson that memory goes stale suggests re-verifying claims on arrival and storing a timestamp.

### 5.6 Symmetry

Two techniques, at two levels:

- **Play-symmetry hygiene** (TRAINING_ALGORITHM Phase 0.7). No fixed compass-order tie-breaks, per-robot RNG seeds
  (`new Random(rc.getID()*7919+13)`), and keys that are invariant under all symmetries. `towerTypeFor` uses
  `min(x, W−1−x) + min(y, H−1−y)`, which is invariant under reflection and 180° rotation, so mirrored ruins get
  mirrored types. Bob's `BobSym.java` audits whether mirrored ruin pairs get different types.
- **The parity trap** (`mapdata/README.md`). An `(x+y)&1` key is single-branch on 4 of 75 maps (gridworld 21/0, Filter
  5/0, Snowman 6/0, CastleDefense 0/6). It produced a "latent bug" report that had to be retracted.
- **Inferring map symmetry** did not pay in BC25. Travel-based elimination never eliminated anything, and in-vision
  terrain elimination overran bytecode. In any case, the consumer was a "fallback of a fallback".

**2023 mapping (inference).** Symmetry matters far more in 2023, because enemy HQ positions are deterministic under the
symmetry and launchers need targets. Eliminating from HQ positions known at round 1 and from wells or islands seen, then
broadcasting the result in the shared array, avoids the 2025 bytecode trap: sense once, share for everyone.

### 5.7 Combat and micro

- **Tower targeting.** Single-target the lowest-HP enemy in range, plus AoE when any enemy is near.
- **Splasher siege as range kiting.** Target ranking puts money towers first ("killing the last money tower freezes
  the victim's production permanently — 1,887 consecutive frozen rounds measured"). Movement:
  - d² > 16: approach;
  - d² ≤ 9: back off along `siege.directionTo(me)` with ±45° fallbacks;
  - 10..16: hold the ring, inside splash reach and outside tower reach.
- **Splash scoring.** Score each centre within r² 4: towers in the AoE +100/+60, enemy paint within r² 2 of the centre
  +3, empty passable tile +2. Fire if the score is at least `SPLASH_MIN_SCORE` (14) or the splash clears a denied ruin
  (`rzHit`). The comment records a scoring bug that was fixed: the footprint was being scored as if larger than the
  engine's.
- **Moppers.** The `mopSwing` direction is reduced to a cardinal. Moppers were mostly a failed line for darla.

**2023 mapping.** Launchers have attack r² 16 and vision r² 20, and an HQ deals 4 damage per round within r² 9. The
ring logic (approach, hold the band where you can hit but are not hit, back off) maps directly onto launcher micro
against HQ zones and onto kiting enemy launchers by timing cooldowns. The scoring-function pattern carries over too:
compute the target score with the engine's exact footprint and threshold it with a named, dose-able constant.

### 5.8 Communication

BC25 used per-unit messages (`ms=sent/heard` counters), not a shared array. Darla's first communication arm (darla65) was
a real, firing mechanism but null over 2,700 games. The ruin relay (darla156) was closed. **(Inference: this is weak
evidence about 2023, where the 64 × 16-bit shared array, writable only near an HQ, amplifier or anchored island, is
the central coordination tool. Do not import the 2025 null.)** What does transfer:

- verify both halves of a channel separately ("a soldier never reads, so a soldier's heard-count is 0 by construction");
- put the counters in the build.

### 5.9 Bytecode

- Darla's peak robot bytecode was "37.5% of 17500" at one point. The darla88 check found "peak bytecode 8,138 of
  17,500" and `ov` 0.
- **Rule: an arm whose robots overrun is VOID regardless of score** (darla8 registration, applied to darla72/73).
- **Whole-vision scans dominate cost.** `senseNearbyMapInfos(-1)` returns about 69 tiles. In 2023, with 10000
  bytecodes for non-HQ units and 12500 for carriers, budget any per-tile loop in the same way.

---

## 6. Tools and infrastructure inventory

**Context for the verdicts.** The 2023 project already has bare-java `tools/gauntlet.sh` (with the re-exec trick and
seed support), `lib.sh` (JDK 8 at `~/jdk/jdk8u504-b01`, engine 3.0.15 jar with a seed patch on `LiveMap`), `vm.sh`,
bench tools for external bots, and `filter_year.py`. So "steal" usually means porting a feature into the existing 2023
tool rather than copying a file.

**Changes common to every port:**

- **Engine.** `battlecode23-3.0.15.jar`, resolved via 2023's `engine_cp`.
- **Java 8.** Drop the five `--add-opens` JVM flags, which a Java 8 JVM does not accept **(inference: they are Java 9+
  options)**. Keep bot code free of Java 9+ syntax.
- **Replays and maps.** `.bc23` replays and `.map23` maps.
- **VM layout.** `battlecode-dev` on its internal IP. Never touch `battlecode-dev2`.
- **Engine properties.** Re-check the `-Dbc.*` system property names against 3.0.15 (2023's `lib.sh` already uses
  `-Dbc.game.maps` and `-Dbc.server.save-file`).
- **Paths.** Every hard-coded `/home/terryvanbelle/projects/vibe/2025` path.

### 6.1 Shared runner and VM layer (`2025/tools/`)

| tool | purpose | quality | 2023 verdict |
|---|---|---|---|
| `lib.sh` | `ensure_vm` with cached IP (one ssh probe, else the slow gcloud path), `gssh`/`gscp` over plain ssh (avoids `gcloud compute ssh` re-pushing keys), `find_workspace` | high; heavily commented with costs | **adapt.** The 2023 `vm.sh` covers the basics. Port the IP-cache idea if the 2023 path still calls `gcloud describe` per invocation (32.5 s each in 2025). |
| `remote-slot.sh` | `acquire_slot`: a cross-runner flock semaphore (`GLOBAL_CAP` slot files) plus a machine-wide `HARD_CAP` on `pgrep -fc battlecode.server.Main`, taken under a gate lock so check-then-take cannot interleave | high, test-backed | **steal as-is** if more than one runner (gauntlet, ladder, tournament, ad-hoc) can start games on the VM at once. Inline it into every game-starting path. |
| `semaphore-test.sh` | reproduces the HARD_CAP race with fake games (peak 8 ungated vs 7 gated) | high | **steal** with the semaphore |
| `gauntlet.sh` | detached (`setsid`) remote runner. Random `NMAPS` sample, both sides, `MAXJOBS`; writes `maps.txt`, `maps.src` (sampled/pinned), `bot.txt` (build identity); warns about an in-flight run in the same workspace; atomic `mkdir` run id; runner script inside the run dir; 45 s poll with a 180-minute deadline; exception counts per game | very high | **adapt features into 2023's gauntlet.sh**: `maps.src` provenance, `bot.txt`, atomic run id, exception counting, setsid plus a recovery path, the warning for the same workspace in flight. Already present in 2023: re-exec copy, bare java, private class tree. |
| `collate.sh` | results.csv / reasons / summary. Warns `!! INCOMPLETE`, "same map list as …", unequal samples (prefix, not subsample), exceptions; prints swept-win, swept-loss and split per opponent | very high | **adapt** into 2023's `summarize.py`. The three warnings are the valuable part. |
| `gauntlet-collect.sh` | recovers a finished-but-uncollated detached run (`--list` shows runs and completeness) | high | **adapt** (needed if 2023 runs outlive sessions) |
| `vm-match.sh` | one debug match through gradle in a sibling dir, so a gauntlet's `build/classes` is never rewritten; takes a slot | good | **adapt the principle** ("never build into a tree games are loading from"). 2023's gauntlet already refuses this. |
| `tournament.sh` + `cron-tournament.sh` + `systemd/bc25-tournament.{service,timer}` | round-robin of committed HEAD bots via `git archive` (never the working tree). Isolated compile per bot (a broken bot forfeits); random map order so a truncated run is an unbiased subset; `bots.txt` with commit hash only (never the subject, which leaks mechanism); `flock` single instance; systemd timer in Pacific time (Debian cron has no `CRON_TZ`); `OnSuccess=` chains the benchmark; ff-only sync (never `--autostash` on a shared tree) | high | **adapt** for a ladder of frozen snapshots plus external benchmarks. The HEAD-export, isolated-compile, random-order and chaining patterns all transfer. |
| `tournament-report.py` | per-run `report.md` plus `HISTORY.md` league table. Deduplicates byte-identical games, prints the sweep identity, outcome-type shares and caveats | high | **adapt** if 2023 runs a recurring ladder; the dedupe logic is the key part |
| `map-subset.py` | pooled vs pairwise decomposition on a map subset, with complement z-test | good, niche | **skip** (three-body tournaments only) |
| `isolation-sweep.sh` | deletes sibling transcript symlinks in the shared `tasks/`; quarantines scratchpad-root files older than 2 h | good | **skip** unless 2023 runs isolated multi-agent lineages |
| `agent-commit.sh` | commits through a private `GIT_INDEX_FILE` seeded from HEAD, refuses paths outside the workspace, re-syncs the shared index, retries ref-lock races | high | **steal** if several agents or daemons commit from one working tree; otherwise skip |
| `agent-watchdog.sh` + `systemd/bc25-agent-watchdog.{service,timer}` | every 10 min: if the coordinator heartbeat file is over 30 min stale, type a nudge into its tmux session (queues through a usage-limit pause); recreate tmux if gone; 15-minute cooldown; runs the isolation sweep | good, clever | **adapt** if 2023 runs a long-lived coordinator in tmux. It is the only recovery that survives an account usage-limit 429. |
| `vm-prune.sh`, `driver-prune.sh`, systemd timers | delete old `.bc25` blobs only (never results text); keep the newest N runs per workspace; grace period; tournaments kept longer | good | **adapt** (`.bc23`, 2023 paths). Size it for the fast loop from day one. |
| `engine-jar.sh` | resolve the jar pinned by `engine_version.txt` and refuse any other version (the VM cache held both 1.0.0 and 3.1.0); `BC25_ENGINE_VERSION` env override so failure paths are never tested by editing a shared file | high | **adapt the principle.** 2023 pins by sha256 in `lib.sh`; make any javap helper use `engine_cp`. |
| `engine-javap.sh` | one command: resolve the pinned jar, put the JDK on PATH, run javap locally or on the VM | good | **steal** (trivial port; 2023 has the jar and JDK 8 locally) |
| `engine-facts.md` | engine facts, each with javap offsets and a re-verify command; corrections kept in full | very high as a format | **steal the format** for 2023's `RULES.md` engine-checked entries |
| `replay-dump.sh` + `replaydump/ReplayDump.java` (36 KB) | replay to text, compiled against the engine jar's own `battlecode.schema` classes. Team aggregates per sample, spawns, deaths, an action window, a per-robot track, ASCII arena (terrain, paint, units), coverage self-check against the engine's counts. Indicator strings opt-in per team (`--ind`). The compiled tool is cached on the VM, keyed by tool hash plus engine version; `--vm` dumps in place | high | **adapt heavily.** The `.bc23` schema differs (resources, anchors, islands, clouds, currents, carriers), so the flatbuffer reading must be rewritten. Keep: schema-from-jar, cache, `--ind` per team, ASCII views, and the "reconstruction vs engine count" self-check. |
| `mapdata/ruinscan/RuinScan.java` + `ruin_parity.txt` + README | reads the official `.map25` corpus from the jar: per-map ruin counts and parity, density outliers | good | **adapt** into a 2023 map census (`.map23`: size, symmetry, HQ count, wells by type, islands, clouds, currents). Use it to catch degenerate maps before tracing. |
| `bc25-maps.txt` | the 75-map pool | n/a | 2023 has `maps.txt` |
| `map-resample.py` | per-opponent map-level bootstrap and jackknife, 95% CI, distance from the mirror null; reports from the launched bot's perspective (the inversion bug is documented) | high | **steal**, and extend keys to (map, side, seed) when the 2023 seed patch is used |
| `bot_identity.py` | identifies the playing build by content against every snapshot (package line normalised): `label`, `base+cand`, `head`, `dirty` | high | **steal** |
| `track_vs_old_bots.py`, `plot_vs_old_bots.py`, `plot_progress.py`, `progress_lib.py` | frozen-roster win% history CSV (committed) and charts; UTC stored, Pacific displayed; refuses unequal-sample runs | good | **adapt** for a 2023 frozen-roster chart |
| `benchmark.sh`, `benchmark-arm.sh`, `benchmark-collect.sh`, `benchmark-collate.sh`, `cron-benchmark.sh`, `benchmark-history.py` | score committed bots or arms vs external bots that live only on the VM; scores only, no replay written; `HISTORY.md` regenerated as records-only from `scores.csv` (idempotent) | high | **adapt.** 2023 rules allow studying external bots' games and replays, so the no-replay restriction is unnecessary. Keep: regenerate-not-append history, records table, benchmark-on-accept. |
| `benchmark-replay.sh` | opt-in copy that keeps replays (owner exception) | fine | **skip** (fold into the adapted benchmark) |
| `redact-2025.py` | drop any blank-line block mentioning the contest year | simple | already done in 2023 (`filter_year.py`) |
| `agent-prompts/{alice,bob,carol,resume}.md` | cold-start prompt (work out your own state from git, collect runs, check tournaments) and a short resume prompt ("do not re-read doctrine") | good | **adapt** the resume prompt pattern for any 2023 subagents |

### 6.2 Darla's experiment pipeline (`agents/darla/tools/`), the most reusable piece

| tool | purpose | 2023 verdict |
|---|---|---|
| `make-arm.sh <name> '<sed>' '<expected>'` | copy the shipped bot into a new package, apply the sed, and **prove** it: package line rewritten, BUILD rewritten, expected text present in code (not only in a comment), diff below the package line not empty. Deletes the arm on any failure. Exists because `darla14`'s sed matched nothing and forfeited 0/72. | **steal** (adapt package names) |
| `arm-runner.sh` | daemon draining `progress/pending-arms.txt`: flock, setsid, waits out other gauntlets, skips arms that already have 144 games, retires an arm only if games were actually produced (a disk-full failure once "completed" the whole queue in 4 s) | **steal** |
| `idle-filler.sh` | when the queue is empty and no evaluation is running, play a fresh random 25-map sample of the shipped build vs frozen opponents and record it to history. Yields to any evaluation job and re-sources `jobs.sh` every loop. | **steal.** It doubles as the held-out time series. |
| `jobs.sh` | one regex defining "an evaluation job", with a self-check that warns if a gauntlet-launching script is not in it. The pattern went stale 7 times. | **steal** |
| `head-to-head.sh`, `paired-roster.sh`, `roster-screen.sh`, `replicate.sh`, `widen.sh`, `widen2.sh` | the instruments: candidate vs reference on all maps; vs 3 lineages on all maps (450); on 25 pinned maps (150); on a fresh random sample; vs 3 mid-lineage snapshots. All serialised by one flock (`/tmp/darla-eval-driver.lock`); the run is identified from the gauntlet's own stdout, never `ls -t`. | **adapt** (opponent sets differ in 2023; keep the serialisation and run-id capture) |
| `accept-iteration.sh <arm> <N>` | freeze, promote, verify package and BUILD, print the behavioural diff, list the remaining steps; deliberately does not commit | **steal** |
| `watch-state.sh` | state-based watcher: reports any new run dir that has a `summary.txt`, whatever produced it (log tailing went blind as producers were added) | **steal** |
| `status-line.sh` | one line saying what the VM is doing; finds the live run by name order and write freshness | **adapt** |
| `disk-guard.sh` | two-stage prune when free space is low, on driver and VM; gentle first, because aggressive pruning destroyed a needed control replay | **adapt** |
| `plot_arms.py` | arm ladder and dose-curve charts | **adapt** (optional) |

### 6.3 Per-lineage statistical tools worth porting

- **Gate maths.** bob `gate_sd.py`, carol `sampledgate.py` and `gatepower.py`: finite-population and paired-map gate
  variance. **Adapt.**
- **Floor estimation.** alice `noise-floor.py` and carol `noisefloor.py`: the floor from a policy-identical,
  phase-different twin. **Adapt**; in 2023 the twin is a seed offset or a map-seed variation.
- **Stage 0.** bob `stage0.py` and carol `stage0.sh`: refuse to print who won. **Steal the idea.**
- **Determinism checks.** alice `determinism-check.sh` and `dose-compare.sh`: exact cell-by-cell comparisons on shared
  (map, side). **Steal.**
- **Cumulative ratchet.** alice `unconfirmed.sh`: a ratchet that forces a cumulative check on unconfirmed
  keeps (`SELFTEST=1` proves the failure branch). **Adapt** if a "keep if not worse" rule is used.
- **Bundled checklist.** carol `tools/eval-run.sh`: one script runs every per-evaluation check (completeness,
  map-resampled CI, sweeps, side split, exceptions, bytecode, frozen-treasury gate). **Adapt as a 2023
  "basics bar" checker.**
- **Snapshot and promotion.** bob `snapshot.sh`, `compile-check.sh` and carol `promote.sh`: superseded by darla's
  `accept-iteration.sh`.
- **Replay text.** carol `replay-strings.py`: printable strings and `--hash` of decompressed replay content
  ("byte-identical content == byte-identical game; gzip wrapper carries a timestamp"). **Steal the hash trick** for
  determinism checks.

### 6.4 Running many agents: the machinery and its lessons

- **Topology.** One coordinator Claude session in tmux on `claude-driver` spawned the lineages as subagents. Games ran on
  `battlecode-dev` (8 vCPU, 20G disk). Agents shared one working tree, one `.git/index`, the scratchpad (`tasks/` and
  root), the VM HOME and the process table. Every shared surface leaked or raced at least once (section 7).
- **Liveness.** `ListAgents` "completed" is a snapshot, not a state, because agents resume when their background
  children finish. The authority is a transcript that is still growing. The rule became: always `TaskStop` the old
  agent before launching its replacement. "No task found with ID" is the clean signal. Messaging a finished agent
  resumes it.
- **Cost control.**
  - Resume (`SendMessage` with `resume.md`) instead of cold-starting: 77k tokens per cold start.
  - Cycle agents at about 250k context, with `CLOSURE_MAP.md` as the handoff.
  - Training logs are grep-only (about 320k tokens each).
  - The project dropped from 3 lineages to 2, then to 1, "to fit within the account's usage limits".
- **Throughput.** `GLOBAL_CAP` 5→7 and `HARD_CAP` 7→8 once BC26 left the VM; `MAXJOBS` ≤ 3 per run; the owner later
  capped darla at "two run drivers" for driver memory. **(Inference: with one lineage, the darla daemon pipeline kept
  the 8-core VM busy around the clock and gave more decisions per day than three agents with their own loops.)**

---

## 7. Pitfalls and gotchas that cost time

| # | pitfall | cost as stated | control that fixed it |
|---|---|---|---|
| 1 | bash reads scripts lazily, so editing a running script corrupts it | "killed the collation of a finished 450-game tournament" | re-exec from a private unlinked copy (2023 already does this) |
| 2 | two runs started in the same second shared a `RUN_ID` and directory | the paired run "lost all 450 of its own" | `mkdir` without `-p` as an atomic claim; one eval-driver flock |
| 3 | identifying a run by `ls -t` (collation rewrites mtimes) | reported 123/150 for a run that was really 352/450 | parse the run id from the gauntlet's own stdout; sort by name |
| 4 | `pgrep` for `tools/gauntlet.sh` matches nothing because of the re-exec name | daemons launched into running gauntlets | match `\.reexec-gauntlet\.sh` |
| 5 | an inherited flock fd in child processes | a killed daemon could not restart while its orphaned gauntlet ran | `9>&-` when spawning |
| 6 | hard-coded lists of job types went stale | the filler starved head-to-heads for 70 min; results sat unread 73 min; 7 recurrences | single `jobs.sh` regex with a self-check; state-based watcher |
| 7 | the arm sed silently matched nothing | darla14: 0/72 forfeits, briefly read as a catastrophe | `make-arm.sh` assertions, with EXPECT matched in code not comments; awk instead of `grep -q` under pipefail (SIGPIPE 141) |
| 8 | the registered falsifier's counter was missing from the arm build | darla82's −14 could not be attributed; one extra arm | rule: the arm contains its counter |
| 9 | the HARD_CAP check-then-take race | VM at 8 games against a cap of 7; load 10.3 on 8 vCPUs | gate lock in `acquire_slot` |
| 10 | debug gradle build in the gauntlet's workspace swaps classes under live games | silent corruption, never announced | build in a sibling dir; refuse when the class tree is in use |
| 11 | disks filled: VM 20G/20G, driver 100% | ENOSPC on commit; "three arms died on ENOSPC inside four seconds" | prune timers, disk-guard; replays kept for losses only |
| 12 | aggressive prune deleted needed evidence | control replay deleted "six minutes before" it was needed | two-stage prune with a grace period |
| 13 | the wrong engine jar decompiled (1.0.0 vs 3.1.0 in the gradle cache) | "confident, false facts", nearly into `engine-facts.md` | `engine-jar.sh` refuses a version mismatch |
| 14 | testing a failure path by editing a shared tracked file | a lineage saw `engine_version.txt` read 9.9.9 mid-probe | env override (`BC25_ENGINE_VERSION`) |
| 15 | shared `.git/index`: `git add` then a sibling's commit | 1,716 lines committed under the wrong lineage | `agent-commit.sh` private index |
| 16 | two sessions of one lineage | happened 5 times; 6 concurrent jobs against `MAXJOBS` ≤ 3; two "iteration 45"s; two parallel log accounts for 30 min | `TaskStop` before every relaunch; gauntlet in-flight warning |
| 17 | shared scratchpad and process listings leaked across lineages | a sibling's unit type disclosed; 100 replays at the root | sweep, `u=wx` root, scoped `pgrep -fc` |
| 18 | committed but unpushed | 31 commits unpushed, including two accepts | `accept-iteration.sh` lists push as a step; owner rule |
| 19 | `ensure_vm` called `gcloud describe` twice per tool call | 32.5 s per invocation; a 71 s replay dump | IP cache plus a one-probe fast path |
| 20 | partial runs compared with complete ones | near wrong dose decision (89% vs 80%) | `!! UNEQUAL SAMPLES` warning |
| 21 | pooling deterministic repeat games | inflated z | game-level dedupe |
| 22 | parity-keyed policies on degenerate maps | retracted "half of all ruins wasted" report | map corpus census |
| 23 | `(x<<6)\|y` keys and per-robot statics assumed shared | darla70: "the symmetry arm was a NO-OP: statics are per-robot" | none; it was a bot-level misunderstanding |
| 24 | a gate set above the reachable range (upgrades at 3,700 chips when the treasury oscillates 1,600–2,450) | mechanism effectively off for iterations | log the gate predicate's firing rate |
| 25 | the indicator-string window in `ReplayDump` defaulted to empty | a census read "0 occurrences" from a run that never looked | `indWithheld` counter in the footer |
| 26 | the resampling tool silently inverted under one launch convention | wrong-sign estimates that "read plausibly" | always report from the launched bot's perspective |
| 27 | commit messages in double quotes ate backticks and `$(...)` | lost text from commit messages | single-quoted heredoc |
| 28 | a systemd timer was needed for local-time scheduling | an hour of slip at each DST change with cron | `OnCalendar` in America/Los_Angeles |
| 29 | `--autostash` pulls on a shared dirty tree | would poison in-flight builds | `git merge --ff-only` only |

---

## 8. Top 15 takeaways for the 2023 project, ranked by expected value

1. **Measure against a real external opponent early and often, and look at those replays.** The roster of your own
   lineages is blind to shared weaknesses. In BC25, +19, +15 and +29 roster games bought +2, +2 and −1 against `v3`,
   and the decisive opening deficit (first tower r266 vs r34) was invisible until `v3` replays were opened. 2023 rules
   allow studying external bots' games, so do it from week one.
2. **The opening decides the game. Instrument the first 100 rounds** (units by type at r40/r100, first income
   structures). Darla's biggest `v3` gains (46% to 56%) came from opening and expansion fixes, not mid-game polish.
3. **Use paired designs and McNemar on discordant keys, with the map (not the game) as the unit of uncertainty.** A
   direct head-to-head turned a "+4 inside the floor" into +22/150. Keys are (opponent, map, side), plus seed in 2023.
   Port `map-resample.py` and the finite-population gate maths.
4. **Keep a held-out instrument that never selects**: fresh random map samples vs frozen opponents, run by an idle
   filler. In-pool accepts were about 60% real on held-out data. Report both numbers on every accept.
5. **Never let the VM idle, and never let the agent wait.** Use darla's queue daemon, idle filler and state-based
   watcher, with "at least three items queued at all times". The owner had to intervene repeatedly about stalls.
6. **Instrument every unit with a BUILD tag, decision counters and a state token in the indicator string, plus a
   bytecode overrun counter. Void any arm with overruns.** Darla's iterations 2 and 3 came from counting state tokens
   in one replay (`S HOME` at 63–79%).
7. **Find the binding resource from no-build reasons before tuning ratios, and check every gate is reachable.**
   Watch for reserve dead bands, cheap units starving expensive ones through an unchecked resource, and gates above the
   treasury's real range. Expect the same failure classes with Ad, Mn and anchor reserves.
8. **Guard on the engine's own predicate, verified with `javap`**, and keep `engine-facts.md`-style entries with
   re-verify commands. One proxy guard wasted 42–55% of a unit type's paint budget.
9. **Navigation: greedy plus a bounded bug-escape triggered only by a measured stuck condition, with ID-parity
   tie-breaks for play-symmetry.** The full bug fallback lost 14 games; the escape hatch gained 13–15. Re-test in 2023
   because of currents and clouds.
10. **Make every arm by script and prove it differs** (`make-arm.sh`), **and accept by script**
    (`accept-iteration.sh`: freeze, promote, exact promotion test, benchmark, push). A silent sed no-op cost a full arm
    run.
11. **Concurrency hygiene on shared infrastructure.** Use one flock semaphore for every game-starting path, atomic run
    directories, run ids parsed from stdout, re-exec copies of running scripts, no builds into live class trees, and
    content-based build identity (`bot_identity.py`). Each one cost a real run in 2025.
12. **Plan disk from day one.** Keep replays of losses only, prune results never, prune in two stages with grace
    periods, and treat the VM's smaller disk as the one that fills first.
13. **Exploit radius asymmetries and kite in a range band** (approach / hold ring / back off). The splasher-vs-tower
    asymmetry was worth about +12 points. In 2023, look at launcher r² 16 vs HQ r² 9 and vision r² 20.
14. **Share expensive inference instead of recomputing it per robot.** BC25's symmetry inference died on per-robot
    bytecode (about 69 tiles × candidates). 2023's shared array lets one unit infer and broadcast symmetry, wells and
    islands. Do not import BC25's communication nulls; they were for a weaker message channel.
15. **Prefer few large mechanism changes with opponent-independent triggers over constant tweaks and
    opponent-specific fixes.** Most of about 190 darla arms were nulls inside a ±5-point floor. The accepts that
    survived fixed the bot wasting its own turns, paint or units, and opponent-targeted arms failed to replicate across
    opponent sets.

### Sources most worth re-opening

- `2025/agents/darla/src/darla/RobotPlayer.java` (the whole bot, with measured justifications inline).
- `2025/agents/darla/tools/*.sh`.
- `2025/tools/{gauntlet.sh,collate.sh,remote-slot.sh,map-resample.py,bot_identity.py}`.
- `2025/tools/replaydump/ReplayDump.java` as a template for a `.bc23` dumper.
- `readroom-no2023/bc25/MULTI_AGENT.md` for the multi-agent operating manual.
- `readroom-no2023/bc25/agents/darla/DESIGN.md`: grep the `ITERATION n — ACCEPTED`, `FIRST LOOK AT v3`, `overfitting
  exposure` and `instrument's resolution` sections.
