# bc24-tools-code: the 2024 project's tools, tests and bot code, and what to reuse for 2023

Reader: the agent and owner of the Battlecode 2023 ("Tempest") practice project.
Source: battlecode24-vibe (Battlecode 2024, engine 3.0.6, one week, 2026-09-30 to 2026-10-07), the latest and
highest-weight prior project. Code was read directly from `/home/terryvanbelle/projects/vibe/2024`. Prose documents
were read only from the filtered reading room `/home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc24/`.
Numbers are quoted as written in those files. **(inference)** marks my own reading. Facts about the 2023 engine
were checked against the official engine source at `reference/battlecode23` (tag 3.0.15) and the staged fat jar
`2023/engine/battlecode23-3.0.15.jar`, not taken from any 2023 strategy write-up.

This report is the tools-and-code slice. Two sibling reports cover the method (`bc24-method.md`) and the gameplay and
ladder (`bc24-play.md`). I repeat their facts only where a tool decision depends on them.

---

## 1. Scope

### 1.1 Code read in full (from the repo)

- **Runner and engine:** `tools/lib.sh` (68 lines), `run-match.sh`, `run-dev.sh`, `snapshot.sh`, `replay-dump.sh`,
  `build-engine.sh`.
- **Batch play:** `gauntlet.sh` (135 lines), `scrim.sh`, `mirror.sh`, `paired.sh`, `diag-batch.sh`, `filler-pair.sh`,
  `collect-fillers.sh`, `filler-tally.py`.
- **Ladder and statistics:** `elolib.py`, `elo.py`, `sprt.py`, `statlib.py`, `scrim-record.py`, `post-block.sh`,
  `field-score.py`, `progress-chart.py`, `eval-paired.py`, `arm-deltas.py`, `compare.py`, `derived.py`, `polarity.py`.
- **Gates and checks:** `delivery-gate.sh`, `delivery-check.py`, `band-test.sh`, `basics.py`, `deadcode.py`,
  `unit-tests.sh`.
- **Census and study:** `capability-census.sh`, `capability-summary.py`, `scrim-study.sh`, `scrim-study.py`,
  `onset-merged.sh`, `log-scan.sh`, `side-indsum.sh`, `stun-check.sh`, `defense-profile.py`, `fill-origin.py`.
- **VM:** `vm.sh`, `vm-run.sh`, `vm-queue.sh`, `vm-enqueue.sh`, `vm-collect.sh`, `vm-prune.sh`, `vm-stop.sh`,
  `vm-sync.sh`, `vm-tail.sh`.
- **External field:** `bench-compile.sh`, `benchcompile/BenchCompiler.java`, `bench-select.py`, `bench-roster.py`.
- **Bot (incumbent `src/g_iter7`):** `RobotPlayer.java` (39 lines), `G.java` (101), `Nav.java` (115), `Sym.java` (258),
  `Comms.java` (227; schema header and functions). Read in part: `C.java` (181, first 60 lines), `Micro.java` (451;
  header, `fight`, `threat`, `engageableRef`, `engageableFast`, function list) and `Duck.java` (1,242; `turn()`,
  `trySpawn`, `explore`, `fieldTarget`, function list). Diffed `src/bot` against `src/g_iter7` file by file: Nav, Sym and
  Track are identical; Duck differs by 241 lines, Micro 142, C 98, Comms 11, G 11 and RobotPlayer 3 (the arm switches,
  all off by default).

### 1.2 Code read in part

- `tools/replaydump/ReplayDump.java` (2,085 lines, 161 KB): the mode list and column documentation (lines 1-216), `main`,
  `load`, `run`, `header`, `round` up to the indicator strings (lines 217-860), and the bytecode and action handling.
  I did not read the 2024 study analysers inside it (Track belief, chains, step census, reach census).
- `tools/test_tools.py` (1,031 lines, 208 `check(` calls): header, the SPRT and Elo tests, the replay-dump fixture
  integrity block (lines 95-210), and grep of the remaining sections.
- `tools/test_metrics.py` (34 checks): header and the polarity and statlib block.
- Headers only: `correlate.py`, `onset.py`, `tactics-survey.py`, `premise.py` (21.7 KB), `contact-d0.py`,
  `recall-d0.py`. These are 2024 study analysers.
- `test/bot/BotTest.java` (75 checks; the fake `RobotController` and `main`), `SymTest.java` (16 checks; the property
  test), `AuditTest.java` (214 checks; header and two helpers), `ContactTest.java` (78 checks; header).

### 1.3 Documents read (filtered reading room)

- In full: README.md, HANDOFF.md, CLAUDE.md, TRAINING_ALGORITHM.md, AUDIT_PROMPT.md, BENCHMARK.md (1,761 bytes in the
  filtered copy), and LEARNINGS.md sections 1, 2 (M1-M10, P1-P5, R8, T1-T5, O1-O4, F1-F5), 3, 4 and 5.
- Read in part: research/AUDIT-2026-10-03.md §4 (MEAS1-MEAS17) and §6 (systematic tests); research/BCENV.md (head);
  progress/ELO.md (head); and TRAINING_LOG.md (Phase 0, iteration 0-1, the throughput audit, the 2026-10-02 symmetry
  repair entries, and the disk and ops entries found by grep).
- `tools/arm-intent.txt` from the filtered copy (it is identical to the repo copy). I did not read the other
  `tools/*.txt` data lists (band, roster, ladder-bots, upper-tier, map lists); several are 0 bytes in the filtered copy.

### 1.4 Skipped, and why

- Every 2024 opponent-specific study (CRACK-*.md, study lenses) and research/TACTIC_LEVELS.md and REWRITE_DESIGN.md:
  the gameplay sibling covers them.
- `src/*` other than `bot` and `g_iter7` (163 more packages: older snapshots and arms). Their diffs are recorded in
  `tools/arm-intent.txt` and TRAINING_LOG.
- `src/*/Track.java` (528 lines): it is compiled out of the incumbent (`C.TRACK = false`; audit MEAS14 counts it as dead).
- Any external bot source and `~/projects/vibe/bc24-benchmarks` (hard rule 4).

### 1.5 2023-side facts checked for this report

- `2023/engine/battlecode23-3.0.15.jar` is already staged. It holds the `battlecode.schema` flatbuffer classes and 103
  `.map23` maps (`unzip -l`).
- `2023/tools/lib.sh` and `get-engine.sh` already port the 2024 runner: the fat jar, a patched `LiveMap.getSeed()` first
  on the classpath, the `team-a.package` and `team-b.package` flags, and `-proc:none`. `build.sh` and `throughput.sh`
  also exist.
- `2023/matches/test1.bc23` starts with `1f 8b`, so a `.bc23` file is gzip around a flatbuffer, as in 2024.
- The driver has 2 vCPUs and about 1-2 GB of RAM, Python 3.11 without matplotlib, and JDK `~/jdk/jdk8u504-b01`. Its disk
  was at 89% (3.4 GB free) when I checked.
- The relayed owner note ("You can clear local storage from bc24 to free up disk space") grants permission. It does not
  ask a read-only reader to delete anything, so nothing was deleted.

---

## 2. What worked (evidence as written)

These are the tool and code items with measured effects. The ladder climb itself is in the siblings: g_iter1 1652 to
g_iter7 2113 (+461) in four days after the first audit, final rank 6 of 88, field score 88.6% (LEARNINGS §1).

1. **Seeded paired cells, proved by an identity control.** `scrim.sh` writes a fourth field per cell, an engine seed
   drawn from a second RNG stream (`rs = random.Random(seed ^ 0x5EED5EED)`), so the cell sequence for a block seed does
   not change. `paired.sh` plays every cell twice: candidate against reference, then reference against itself, on the
   same seed.
   - Before this, identical code flipped 15-29% of cells, so "about 2.5 days of gained/lost tallies were mostly noise"
     (M1, audit B2).
   - After it, a byte-identical copy (g1copy) read 0 of 80 discordant, and z1copy read 0-0 in 48 pairs (TRAINING_LOG
     2026-09-30 harness check).
   - Effect: this made every later verdict interpretable. It is the single most important harness property.
2. **The correctness audit of bot plus tools.** It ended a plateau of about 80 failed builds. Bug-fix promotions gave
   +185 of the +461 (g_iter2 +169, g_iter4 +16), and audit-motivated levers gave +77 (LEARNINGS §1). The tool side of the
   second audit (MEAS1-MEAS17, §3 below) found defects that had silently decided verdicts.
3. **Observed symmetry, tested offline (`Sym.java`, `SymTest.java`).** g_iter1 guessed the symmetry and had wrong enemy
   centres in 28% of ColtG5 games and 34% of band games (Sym.java header). The rewrite decides by observation.
   - SymTest runs the real pruning code over 300 random symmetric maps (30-60 a side, random wall density): the true
     symmetry is never eliminated, the set never empties, and every map is decided within 13 vision disks (bar 60).
   - Six verification batches followed on real maps, ending with 0 overruns and the right answer at r250 on 8 of 10 hard
     maps (TRAINING_LOG 2026-10-02).
   - The fix alone was band-neutral (g1sym vs g_iter1 63-57, net -6; M7). As part of g_iter2 it shipped:
     234 seeded band pairs, wins 78 -> 111, net +33 (44-11), p < 0.001.
4. **Delivery gate enforced by a tool.** `band-test.sh` exits 5 without `gauntlet/delivery-<arm>.PASS`, and
   `delivery-check.py` gives three-way verdicts. After it, step 5(a) or 5(b) stopped z1hold, b2dig5, g1icpt, g1esc2,
   b2rgc, g2rgh, g4contact8, g7fc, g7ring "and others before a 240-game band test" (P1). Effect: about 240 games saved
   per stopped arm **(inference from the band-test size)**.
5. **Three-way verdicts with auto-extension.** PASS needs the margin to clear the bar by 1 SE, FAIL means 2 SE short,
   and anything between is INCONCLUSIVE, which extends 24 -> 48 -> 96 cells (192 later). Before this, 16 of 28 FAILs and
   7 of 15 PASSes sat within 1 SE of their bars (MEAS1). After it, g3tether was a powered FAIL at -2.3 SE and g7ehp
   moved from INCONCLUSIVE at 96 to PASS at 192 (M4).
6. **Shipping rule on the capture difference with sequential looks (`eval-paired.py --look`).** Per pair, wins carry
   2.2-5.6x less information than the capture difference. The new rule (t_all >= 2.3 or t_up >= 2.6, wins net >= 0, looks
   at 240/480/720 pairs) promotes a +30-Elo gain 63-65% of the time at 2.0% false promotion. The old rule managed 17% as
   written and 34% as practised (M3). It shipped g_iter5 at look 3 (t_all 3.25, 720 pairs).
7. **Batch Bradley-Terry ladder (`elolib.py`).**
   - The fit has no play order and rates each build as its own player.
   - It uses a weak prior, dedupes on (A, B, map, seed), caps each pair at 200 games, iterates to tolerance and warns if
     it does not converge.
   - It replaced a sequential K=32 Elo in which "96 easy calibration games lifted 'us' from rank 65 to rank 4" (elolib
     docstring).
   - The pair cap fixed a distortion: about 1,500 filler games against andli28 had pulled g_iter7 from 2150 to 2116, below
     NotLLeon, which it beats 48-40 (M8).
8. **Standing VM queue plus idle filler (`vm-queue.sh`).** The throughput audit (2026-10-01) found the 8 vCPUs saturated
   during runs (7 games, load about 19) but the VM idle about 29% of its uptime between runs. The queue and filler removed
   the gap (T1). The filler then supplied 36,440 of the 45,389 ladder games (80%; P5).
9. **Heal hold found by a two-group contrast census (ReplayDump `--capabilities` columns `healThreat10`,
   `readyHeld20`).** This was the largest single step: +144 Elo. The upper tier healed under threat 26% of the time to
   our 45% (720-game census). The arm shipped at look 1 with wins 136 -> 164 over 240 pairs (net +28, 36-8, p < 0.001) and
   t_all 6.46 (HANDOFF). The census made the lever visible, so it is a direct return on the replay tool.
10. **Static guards in the unit suite.**
    - `deadcode.py` first flagged `Sym.observe` as never called, the bug behind the symmetry guess (TRAINING_LOG
      2026-10-02; owner prompt 127).
    - `arm-intent.txt` (149 assertions such as `g1sym Sym.OBSERVE=true`) was added after a moved comment made a sed flip
      match nothing, so an arm ran with its switch off. Only its bytecode (14.9k, equal to g_iter1's) gave it away (M6).
11. **Cheap bytecode rewrites, each pinned by a test.**
    - `C.INIT_FAST`: round 1 ran at 22.8-22.9k of 25k, about 18k of it a 27x27 adjacency loop; a spawn bitset replaced it
      (G.java comment).
    - `C.REACH_FAST`: the same answer at a fraction of the cost. "g2fast band: 0 of 234 cells differ" (C.java), and
      AuditTest compares it with the reference version.
    - Sym's per-duck tile memory: undecided Soccer turns went from 14.8k to 6.3k mean (TRAINING_LOG verification 6).

---

## 3. What did not work, and closed directions (tool and code side)

1. **Unseeded pairing (until 2026-10-02 23:00 UTC).** Identical code flipped 15-29% of cells, the same size as most arms'
   discordance (15-20%). Directions closed on unseeded cells were later found "not refuted" (R8): relocation and centre
   crumbs both came back and shipped.
2. **Seeding is exact only for code that changes nothing (MEAS2).** Behaviour-changing arms still disagree with the
   control on 14-38% of pairs (band arms mostly 16-20%). On 234 band pairs, 1 SE is about 6.5 net games, about 20 Elo,
   "so only effects of about 40 Elo or more were visible" (M2). RETEST's premise that seeded re-tests are much stronger was
   false. The RETEST queue ran 8 closed arms on g_iter2, and none delivered (R8).
3. **Point bars in the delivery check (MEAS1).**
   - 43 of 91 `rel:` verdicts lay within 1 SE of the bar.
   - The PASS that opened g_iter3's band test cleared its bar "by 0.00 SE".
   - `nw:` guards could only see drops of 19-47%. g3escrg2 passed `nw:kills`, then its band test measured kills -43 ± 19.
4. **A shared cached base (MEAS4).** One base draw (`dg-census-$BASE-909090`) served 12 band gates and several Cyril gates.
   That base won 0.50 against the population's 0.30 (z +2.1), so every arm on it shared the base's luck with the same sign.
   Still open at shutdown.
5. **Unconverged Elo fit (MEAS11).** 3,000 iterations stopped at delta 1.84e-4; the tolerance needed 23,317 iterations on
   18,949 rows, and every rating was 30-44 points low. Absolute levels were "about three times the stated 95% interval
   off", and the 2050 tier threshold rested on it.
6. **Replay names without the seed (MEAS3, T2).**
   - The names were `opp__map__botX.bc24`. Repeated cells overwrote each other: 264 of 2,200 g_iter3 filler games (12.0%)
     were missing from the census, exactly the number of name collisions.
   - 1.6-2.5% of band games and 11.5% of ColtG5 filler games were dropped. Wins were lost more often than losses (6.3% vs
     4.2%).
   - g4crumb's 96-cell gate was voided.
7. **Indicator-string overflow (MEAS5).** 73.8% of strings in a sampled game were exactly 64 characters. The note was cut
   off, and 9 fields (28 characters) were compile-time zero. Neither of two new incumbent mechanisms had a firing counter
   in any replay.
8. **A vacuous exceptions bar (MEAS7).** The engine records `DIE_EXCEPTION` only for player-load failures. Caught in-turn
   exceptions never reach the replay, so `basics.py`'s exceptions bar "can never fail". The near-miss measure was also
   saturated by `Sym.update`'s deliberate fill to 2,500 bytecodes left (92% of turns at 22.5k or more), which hid a real
   23,591-bytecode relocation scan (BOT16; M10).
9. **Unpaired k/d in basics (MEAS6).** A mean of per-game ratios (one game at 737/23) overstated a real effect about 1.7x,
   and five one-sided checks fail a neutral arm about 11% of the time.
10. **Dead code (MEAS14).** About 900 of g_iter3's 2,807 lines (32%) were dead. Track alone was 528 lines (18.8%): the
    rewrite's sensor, whose consumer was never built, with 285 test lines maintaining it. `deadcode.py` saw none of it,
    because it has no constant folding over `static final boolean` switches. This is F1's cost: "an 8-agent rewrite
    design ... its consumer was never built".
11. **`log-scan.sh` can never produce output (MEAS17).** It passes an unknown flag (`--logs-team`). ReplayDump exits 2,
    but the script uses `set -u` without `-e` and discards stderr, so it prints "0 lines" and writes a tarball. It is a
    2021 carry-over with no consumer.
12. **Results labelled by package name, not by code (MEAS10).** 40 games of g_iter3's code stayed labelled `us:g2cr`.
    g_iter2's 600 games sat under `g1basics`, so the owner could not see g_iter2 on GitHub (PROMPTS 154-155, O3).
    `band-test.sh` checks only that a PASS file exists, not that the code is unchanged since it was written.
13. **Prose-only rules.**
    - 17 filler blocks (about 2,000 games) were played and never recorded until the owner asked (PROMPTS 72-73; P2).
    - Step 5 shrank to "a counter fires" until the tool refused (P1).
14. **Stacking on non-inferiority (P3).** Bases B1-B3 advanced on "not worse" reads. The paired filler later put B1 at -30
    over about 1,870 pairs (-1.8 SE). These are method results, but the filler tally tool is what exposed them.

---

## 4. Method lessons (as they bear on tools)

### 4.1 The loop, as the tools enforce it

TRAINING_ALGORITHM.md §3 says: select, trace, pre-register, implement with tests, diagnose (5a then 5b), gate, then
accept or reject. Each step has a tool, and the tool is the enforcement (P2).

| step | tool |
|---|---|
| trace | `replay-dump.sh` modes (`--from/--to`, `--robot`, `--map-at`, `--logs`) |
| 5(a) diagnostic games | `diag-batch.sh <bot>:<opp>:<map>:<seed>[:<side>]`, at most 8 games at once |
| 5(b) delivery | `delivery-gate.sh <arm> "<checks>"` |
| band test | `band-test.sh`, refuses without the delivery PASS |
| decision | `eval-paired.py --look N` |
| after a block | `post-block.sh`: record, refit, roster, study, onset, tactics survey |
| every change | `unit-tests.sh` |

### 4.2 Gating and statistics worth keeping

- **SPRT on discordant pairs** (`sprt.py`): H0 0.50, H1 0.58, α = β = 0.05, batches of 16, cap 320 pairs. The docstring
  puts p1 = 0.58 at "~56 Elo", resolved in 80-200 games.
- **Sign test** on discordant pairs (`paired.sh`, `eval-paired.py`), plus a paired t on a continuous per-pair margin
  (capture difference). Use the most informative per-pair number (M3) and simulate the rule's power before relying on
  it.
- **Three-way verdicts** (§2.5). Never close a line on INCONCLUSIVE.
- **Identity control on the exact verdict path** after any tool change (TRAINING_ALGORITHM §2.8). "A pass on a sibling
  harness proves nothing" (AUDIT_PROMPT).
- **Look rule:** first looks and small blocks regress toward zero (M5). g7kite read t_all 2.03 at look 1 and 0.32 pooled
  over 480 pairs.

### 4.3 Ladder and Elo design

- Ladder games use random map, random side, a fresh seed and rotating opponents (`scrim.sh`). Each opponent plays at most
  `ceil(N/pool)` times per block and never twice in a row. The pool is the N rated bots nearest the build
  (`elo.py --band`), plus EXPLORE never-played bots for calibration.
- `scrim.sh` refuses (exit 4) if `progress/games.csv` is missing. The "roster fallback" had silently challenged the wrong
  bots from 2026-09-17 to 09-20 (an inherited lesson recorded in the script).
- The ladder is rated by a batch BT fit (§2.7) with a pair cap. Absolute Elo is not comparable across fits, so compare
  builds within one fit (M8).
- **For 2023:** the owner asked for a galaxy-based replica of the judging infrastructure (2023 PROMPTS 1). Keep
  `elolib.fit` as the offline analysis fit over galaxy's match records. It handles per-build players, dedupe and pair
  caps, which a live ladder rating may not **(inference: I did not check galaxy's rating algorithm)**.

### 4.4 Process rules that became tools

| rule | tool that enforces it |
|---|---|
| no band test without delivery | `band-test.sh` exit 5 |
| filler always recorded | `collect-fillers.sh` at every task check |
| switch intent | `arm-intent.txt`, checked in `test_tools.py` |
| no dead code | `deadcode.py` in `unit-tests.sh` |
| no recompiling a class tree in use | `gauntlet.sh` exit 3 |
| no editing a running script | gauntlet and vm-queue re-exec from a private copy |
| self-play never graded | `scrim-record.py` exit 3 |
| a tagged delivery pool needs a tag | `delivery-gate.sh` exit 2 |

### 4.5 Owner interventions that corrected tools

From O1:
- PROMPTS 36 (the VM was 29% idle): the queue.
- PROMPTS 66 (arms skipped delivery): the gate refusal.
- PROMPTS 72 (fillers unrecorded): collect-fillers.
- PROMPTS 125-128 (symmetry guessed, "This is basic stuff"): Sym rewrite, SymTest, deadcode.py, and the audit.
- PROMPTS 154 (stale front page): relabelling.
- PROMPTS 181 (stale ELO column): the incumbent's record column.
- PROMPTS 184 (an under-sampled bot was left out of the band).
- PROMPTS 186 ("Can you evaluate whether the shipping criteria are too strict?"): the 17% power finding and the new rule.
- PROMPTS 191: the pair cap.

The agent carried an over-strict reading of a rule (no chosen maps or sides in diagnostics) for about 4 days without
raising it (O2).

### 4.6 How the agent went wrong with tools

- F1: built an elaborate rewrite instrument (Track, `premise.py`, `--track`) before checking the basics.
- T4: tool defects were frequent and silently changed verdicts. Examples: side-indsum read the wrong team, the census
  died under pipefail, and vm-queue logged every job as "exit 0" because `$?` held a date substitution's status (B12).
- F5: `pkill -f` and `pgrep -f` matched the issuing shell five times. The last, at shutdown, killed its own ssh session.
- T5: overlapping unit-test runs raced on the same build directories. `unit-tests.sh` "still has no lock".

---

## 5. Bot architecture and the basics, mapped onto 2023

The 2024 bot is one package of nine static-class files. 2024 robots ("ducks") are all one type, so `Duck.java` holds
every behaviour. A 2023 bot needs per-type behaviour (HQ, Carrier, Launcher, Amplifier, Destabilizer, Booster) on the
same plumbing. Everything below is in `src/g_iter7` (identical in behaviour to `src/bot` with its defaults).

### 5.1 Turn loop and monitoring: `RobotPlayer.run`, `G`

- `RobotPlayer.run` runs `G.init(rc)`, then loops: `startRound = rc.getRoundNum()`, `G.startTurn()`, `Sym.scout()`,
  `Duck.turn()`, `Sym.update()`. Every `GameActionException` and `Exception` is caught and counted in `G.exceptions`
  (stack trace only if `C.DEBUG`).
- After the turn: if `rc.getRoundNum() != startRound` it counts an overrun (`G.overruns++`); else above
  `C.NEAR_MISS_BC = 22500` (90% of 25,000) a near miss. Then `G.endTurn()` and `Clock.yield()`.
- `G`: per-robot statics. `rand(n)` is an xorshift seeded `id * 0x9E3779B1 + 12345`, "so identical code on both sides
  never shares a sequence". `nearest()` breaks ties by the robot's own RNG, never array order. `bcLeft()` has a test
  override `testBc`, because `Clock.getBytecodesLeft()` returns 0 outside the engine (a test-harness defect the tests
  found).
- `G.endTurn()` writes the indicator string: note first, then counters (`o` overruns, `x` exceptions, mechanism
  counters), because the engine cuts at 64 characters (MEAS5).
- **2023 mapping:**
  - Keep the loop, the overrun rule, the per-id RNG, the tie-break helper and the note-first indicator.
  - Bytecode limits differ by type in 3.0.15 (`RobotType.java`): HQ 20000, Carrier 12500, Launcher, Destabilizer,
    Booster and Amplifier 10000. The near-miss threshold must be `rc.getType().bytecodeLimit * 9 / 10`, not a constant.
  - The 2023 engine charges `EXCEPTION_BYTECODE_PENALTY = 500` per exception (GameConstants), so a caught-exception
    storm also eats budget.
  - There is no "unspawned" state in 2023: HQs build units. `rc.isSpawned()` and jail logic disappear.

### 5.2 Constants: `C.java`

There are 137 `static final` constants and switches. Each is documented with the measurement or reason that set it
(e.g. `NEAR_MISS_BC = 22500 // 90% of the 25,000 limit`). Arms flip switches from these defaults, and `arm-intent.txt`
asserts each flip.

- **Keep the pattern.** But fix two weaknesses for 2023:
  - javac folds `static final boolean` switches, so hooks behind an off switch are compiled out. `unit-tests.sh` has to
    re-run tests on sed-made copies with switches on.
  - `deadcode.py` cannot see code behind a false constant (MEAS14).
- **(inference)** Make arm switches `static boolean` (not final) in the working bot so tests can flip them, and keep
  `final` only in frozen snapshots. Or add constant folding to `deadcode.py`, as MEAS14 proposes.

### 5.3 Navigation: `Nav.moveTo`

- Greedy step toward the target. If blocked, try the two adjacent directions that get strictly closer (order by
  per-robot handedness `left = (id & 1) == 0`). Otherwise start bug wall-following (`bugDir` rotates by handedness) until
  strictly closer than when the obstruction began.
- Stall exit: no progress for `STALL = 20` turns flips handedness and resets.
- Audit A7: bug state survives a target move of dist² <= 8 (`resetNeeded`). Before that, a moving target (a carrier, an
  escort point) reset bugging every turn.
- A9: one map-edge flip per call.
- 2024-only: fill water in the way (`fillToward`), then step onto it the same turn (`C.FILL_STEP`, audit BOT8: "~90 lost
  steps a game, up to 279 on water maps").
- There is no BFS or Dijkstra pathfinder anywhere in the 2024 bot. The only BFS is the 7x7 reachability check in
  `Micro.engageableFast`.
- **2023 mapping:**
  - Bug nav with handedness, the stall exit and the A7 rule port directly (a 2023 `Direction` and `canMove` API exists).
  - New for 2023: currents move a unit at the end of its turn, and clouds slow cooldowns and cut vision to r² 4. Carrier
    move cooldown grows with load. A greedy-plus-bug walker will be pushed off its path by currents.
  - **(inference)** Plan routes with the current direction as part of tile cost, and test with audit systematic test 2: a
    map sweep over all 103 maps x 2 sides with the real bot classes, asserting every chosen destination is reachable and
    reporting the maximum bytecode per turn.

### 5.4 Symmetry: `Sym.java` (258 lines) and `SymTest.java`

- Candidates are a bitmask (ROT 1, FX 2, FY 4) and never left empty: a contradiction is counted in `conflicts`, not
  applied. `image(m, s)` and `imageIndex` are involutions (tested).
- Eliminations:
  - `geometric()`: a symmetry mapping one of our spawn centres into our own spawn zone is impossible.
  - `observeSpawnImage()`: the image of each of our spawn tiles must be their spawn-zone tile.
  - `observeEnemyCentre(flagId)`: a 2024 quirk; the flag id encodes the centre index.
  - `observeTile()`: per-duck bitset memory of every tile seen (`seen`, `wall`, `spawn`, plus setup-only `dam`). A newly
    seen tile is compared with its remembered image under each surviving symmetry.
- `collapseEquivalent()` keeps one of two candidates that predict identical enemy zones, so no scout is sent for
  nothing.
- Scouting: `scoutTarget()` is the nearest tile where the surviving candidates disagree about the enemy spawn (an image
  of one of our spawn tiles under one candidate that is not an image under another). Duck indices 3-5 walk there after
  setup while undecided.
- Bytecode: `update()` runs after the turn, only with `BC_START = 6000` left, and stops each loop at `BC_STOP = 2500`.
  Each tile is processed once per duck.
- Sharing: `Comms.syncSym()` AND-merges slot 16.
- **2023 mapping, the most transferable piece of the bot:**
  - **The memory compare.** Fixed features in 2023 are walls, cloud tiles, current tiles (with direction), well positions
    and types, island tiles, and HQ positions. All are immutable, so `observeTile` generalises: store a few bits per tile
    and compare with the image.
  - **Current directions transform under the symmetry.** Under a flip, a current's direction is mirrored, and under
    rotation it is reversed. A naive compare of direction values would eliminate the true symmetry **(inference from
    geometry)**.
  - **Geometry.** The image of one of our HQs under the true symmetry is an enemy HQ, so it cannot be one of our own HQ
    tiles.
  - **The scout target becomes the nearest candidate enemy-HQ location.** With 1-4 HQs, one sighting of an image tile
    decides.
  - **SymTest ports almost unchanged:** a random symmetric map, simulated vision disks (2023 vision r² 20 for most units,
    34 for HQ and amplifier, 4 in clouds), and the real pruning code. Add a property test over all 103 real maps, which
    are in the jar.
  - **Sharing must change** (§5.6): a 2023 robot can write only near its HQ, amplifier or anchored island. A field robot
    must keep its local mask and publish when it can.
  - **The replay has the truth.** The 2023 `GameMap.symmetry` field ("0 for rotation, 1 for horizontal, 2 for vertical",
    `battlecode.fbs`) gives the true symmetry. The basics bar "never wrong, decided in time" can then be checked from
    replays, provided the bot prints its mask in the indicator string (the shared array is not in a 2023 replay, §6.4).
    Verify which axis "horizontal" means before trusting it.

### 5.5 Combat micro: `Micro.fight`

- Strike first if something is in reach (`tryAttack`; `bestTarget`: flag carriers first, then lowest HP, then highest
  attack level). Then score all 9 directions (8 plus CENTER) and move.
- Scores by situation:
  - an enemy carrier: close in;
  - a loose flag: go for it;
  - engage if the action is ready, the robot is not hurt, a tile is in range, and the side is strong or the threat is
    low;
  - advance under clear local superiority (`allies + 1 >= enemies + ADVANCE_MARGIN`);
  - otherwise kite or hold: minimise `threat(l) = number of enemies within dist² 10`, with a bonus for staying at
    dist² 11-20 so the robot can strike next turn.
- `threat` uses dist² 10 because "an enemy can step once and hit from dist² 4" (BotTest pins it).
- `engageableFast`: is any enemy reachable within 3 moves? A BFS on a 7x7 grid, with tiles in attack range of an enemy
  pre-marked by 13 offsets, so the search is cheap. Without it, unreachable enemies froze the army (audit A4). The
  heal hold (`C.HEAL_HOLD`, `HOLD_R2 = 10`) keeps the action for a strike when an enemy is close.
- **2023 mapping:** the 9-direction scoring loop is the right skeleton for launchers. The parameters change completely:
  - attack r² 16, vision r² 20, action cooldown 10, move cooldown 20;
  - a launcher can attack every turn but move only every other turn (more slowly in clouds).
  - **(inference)** The threat radius becomes "within r² 16 now, or after one step if the enemy's movement is ready".
    Vision 20 barely exceeds attack 16, so the bot will often not see a threat before it is in range, and an amplifier's
    r² 34 vision and HQ comms become the early warning.
  - The `bestTarget` order maps to carriers carrying anchors or resources first, then lowest HP, then launchers.
  - The reachability BFS ports directly (walls, and currents as forced moves).
  - HQ auto-damage (4 per round within r² 9) is a static threat zone to add to `threat()`.

### 5.6 Communication: `Comms.java`

- The header documents a 64 x 16-bit schema, "one purpose per slot". Locations are `x*64 + y + 1` (0 = none); this fits
  60x60, and BotTest checks the round trip over the whole map range.
- Packers and unpackers are pure functions (`ctPack`, `auxSet`, `diveAdd`) with exhaustive round-trip tests in BotTest.
  A slot-layout test asserts that ranges are disjoint and below 64. MEAS15 found that test missed live slots 49-57: it
  should derive its ranges from the constants.
- Uses:
  - `claimIndex()`: slot 0 is a creation counter, giving every robot a stable index for roles (defenders 0-2, scouts 3-5,
    builders every tenth);
  - the enemy flag registry and our flag alerts with a threat location (A1: "responders go to the threat, never onto the
    flag tile");
  - drop expiry by round stamp;
  - the symmetry mask in slot 16, AND-merged.
- **2023 mapping:**
  - Reading is free everywhere. Writing works only within r² 9 of our HQ, r² 20 of our amplifier, or r² 4 of an anchored
    island of ours.
  - `claimIndex()` still works, since a new unit stands within the HQ's action radius r² 9 on its first turn
    **(inference from RobotType HEADQUARTERS actionRadiusSquared 9)**.
  - Every field report (enemy sightings, symmetry eliminations, wells) needs a pending-write buffer flushed when
    `canWriteSharedArray` holds. Amplifiers become mobile write points.
  - The schema header, the `enc`/`dec` encoding, the pure packers with round-trip tests, the slot-layout test and the
    "stamp with round & 15" trick (`diveCount`, `diveAdd`) port directly.
  - The BotTest fake controller must model the 2023 write-range rule. Otherwise tests pass on writes the engine refuses.

### 5.7 Economy, exploration and roles: `Duck.java`

- Roles come from the creation index: `isDefender` is idx < 3, scouts are idx 3-5, and builders are idx 9, 19, ... (when
  switched on).
- `explore()` picks a random map tile and changes it after reaching it or after 40 rounds: weak, but cheap.
- `fieldTarget()` is a priority chain: chase an enemy carrier, defend, answer the nearest fresh alert's threat, a
  visible enemy flag, escort a friendly carrier, then a front point.
- `trySpawn()` spawns on the tile nearest the robot's wanted point.
- The 2024 economy (crumbs, levels, traps) does not transfer. The method lesson does (S4): eight economy and level arms
  did not ship. "Break a gap down by source before building against it."
- **(inference)** For 2023, a census of income by source and phase comes first: Ad, Mn and Ex delivered per carrier
  trip, trip length, idle carriers, carrier deaths by phase, and HQ passive income. Do it before any economy arm.

### 5.8 Bytecode discipline (the habits worth copying)

- Bitsets over nested loops: `Sym.ours` instead of a 27x27 adjacency scan.
- Do work only with budget left (`BC_START`/`BC_STOP`), and resume partial work across turns. `AuditTest.spreadSame`
  proves that a scan paused at every column gives the same answer as one run.
- Reference and fast versions side by side, with a test that they agree (`engageableRef` vs `engageableFast`).
- **Keep the near-miss measure honest (M10).** A deliberate fill to a fixed floor saturates the max-bytecode column.
  Measure near misses before the fill, or exclude the fill's turns.

---

## 6. Tools and infrastructure inventory

Paths are under `/home/terryvanbelle/projects/vibe/2024/tools/` unless noted. There are 78 files: about 336 KB of shell
and Python, plus ReplayDump.java (2,085 lines), BenchCompiler.java and 13 data lists.

Verdicts: **steal** (use as-is or with path edits), **adapt** (logic stays, year-specific parts change), **rewrite**
(keep the spec and interface, new code), **skip**.

Changes that apply to everything:

- Repo path `~/projects/vibe/2023`.
- Benchmark root `~/projects/vibe/bc23-benchmarks` (already in 2023 `lib.sh`).
- Replay extension `.bc23` everywhere. That includes the replay-name regex `__s\d+(?=__bot[AB]\.bc24$)` in
  `eval-paired.py`, `delivery-check.py` and `arm-deltas.py`, and the side parsers in `side-indsum.sh`, `stun-check.sh`,
  `defense-profile.py`, `fill-origin.py` and `premise.py`.
- Map list `tools/bc23-maps.txt` from the jar:
  `unzip -Z1 engine/battlecode23-3.0.15.jar 'battlecode/world/resources/*.map23' | sed 's#.*/##; s/\.map23$//' | sort`
  (103 maps).
- Rename variables such as `BC24_REEXEC` and `BC24_QREEXEC`.
- `grep -l 'bc24\|BC24'` finds year references in 38 files under `tools/` (lines: test_tools.py 23, premise.py 10,
  gauntlet.sh 7, diag-batch.sh 7, ...).

### 6.1 Engine, runner, compile

| file | what it does; inputs -> outputs | quality | 2023 verdict and exact changes |
|---|---|---|---|
| `lib.sh` | Sourced helpers: JDK 8 on PATH; `engine_cp`; `team_url` (our `build/classes` else `$BENCH_CLASSES`); `run_game A B map replay [-D...]` (headless bare `java`, `timeout ${GAME_TIMEOUT:-1800}`, `-Xmx512m -XX:+UseSerialGC`, seed via `GAME_SEED`); `engine_busy` (ps\|awk, never `pgrep -f`); `parse_result` -> `RESULT <A\|B\|?> <round> <reason>`; `compile_src` (javac `-source 8 -target 8`) | good; the timeout came from an 83-minute invisible hang | **Already adapted** in `2023/tools/lib.sh` (fat jar, `patch/` first, `team-X.package`, `-proc:none`, `SHOW_LOGS`, `CUSTOM_MAPS`, `validate-maps=false`). `parse_result` works unchanged: 3.0.15 `Server.java:605-607` prints `<pkg> (A) wins (round N)` and `Reason: ...`. |
| `run-match.sh` | one game -> RESULT line; replay default `matches/<A>-vs-<B>-on-<map>.bc24` | trivial | steal; `.bc23` |
| `run-dev.sh` | one game from a **private per-process compile** (`build/dev-classes-$$`, removed on exit); `LOG_OUT=` keeps engine stdout; resolves external names through the manifest | good: parallel diagnostics once shared a tree and lost 6 of 20 games | steal; `.bc23`, manifest columns as 2023 `lib.sh` (`name package classdir`) |
| `snapshot.sh <name> [arch]` | copies `src/bot/*.java` to `src/<name>/`, seds `package bot;` and the imports; refuses `bot`, `examplefuncsplayer`, existing names and non `[a-z0-9_]` | good | steal; if the 2023 bot uses subpackages, extend the sed to `package bot.x;` |
| `build-engine.sh` | clones battlecode24 at 3.0.6, patches `LiveMap.getSeed()` to read `-Dbc.game.seed`, works around the rotted jsi snapshot, builds with Gradle under JDK 8, stages jar, libs, maps, VERSION, map list | good (maven returned 403 in 2024) | **skip**: superseded by `2023/tools/get-engine.sh` (official fat jar, checksum-pinned, one patched class, `javap` signature diff) |
| `bench-compile.sh` + `benchcompile/BenchCompiler.java` | compiles each external repo **without printing source**: one JVM per repo; roots are parents of `RobotPlayer.java`; one pass, else per-top-level-package passes to a fixpoint; diagnostics to `_logs/<repo>.log`, one count line to stdout; `manifest.tsv` = `name package classdir repo commit` with name `<owner>.<package>` | good; enforces the never-read rule by construction | **steal**. Classpath = the fat jar. Name packages as 2023 `lib.sh` expects. |
| `bench-select.py` | picks each repo's final bot **by package name only** (final > postqual > qual > seeding > version > sprint2 > sprint; junk regex) | good | steal; manifest path |
| `bench-roster.py` | regenerates the roster table in BENCHMARK.md between markers, with tiers locked/target/peer/solved from the latest submission's record (builds with >= 200 games) | fine; was broken until 09-20 (KeyError) | adapt (paths) or drop if galaxy shows the roster |
| `diag-batch.sh <tag> bot:opp:map:seed[:side]...` | step-5(a) games in parallel (cap `PAR=8`: "24 at once on 8 vCPUs starved sshd"); external opponents silenced; never recorded; writes `diag/<tag>/...` and a summary of selected census columns | good | adapt: the `cut -d, -f...` column picks are 2024 census positions; select by header name instead |

### 6.2 Batch play and pairing

| file | what it does | quality | 2023 verdict |
|---|---|---|---|
| `gauntlet.sh` | the engine of all batch play. Plays a CELLS file (`opp map side [seed]`) or the opponents x maps x sides product, `xargs -P $MAXJOBS`. Writes `gauntlet/<stamp>-<TAG>/results.csv` (`opponent,map,bot_side,winner_side,rounds,bot_result,reason,seed`), `summary.txt` with per-opponent and per-side splits, `losses/`, `replays/` (wins deleted unless `KEEP_ALL`). Guards: re-execs from a private copy (editing a running bash script corrupts it; a predecessor lost a 450-game collation); refuses to recompile a class tree in use (exit 3; a mixed-bot block on 09-20); unique run dir; seed in replay names (MEAS3); duds when the opponent fails instrumentation; unknown on timeout; external bots only with `SCRIM=1` | good after B13/MEAS3 | **adapt**. (1) Its `game()` inlines its own `java` command instead of calling `run_game`, so the 2023 port of `lib.sh` (`team-X.package`, `patch/` classpath) would be bypassed. Make `game()` call `run_game` and pass `-Dbc.engine.silence-a/b` through. (2) `QUICK_MAPS`/`SCREEN_MAPS` are 2024 map names. (3) `.bc23`. (4) Record a reason **code** (§7.1). |
| `scrim.sh` | ladder block: pool from `elo.py --band/--pool/--established/--challenge` (refuses a missing games.csv; roster fallback under 40 games); N cells with opponent rotation, random map and side, engine seed from a second RNG stream; `DRY=1`; then `gauntlet.sh` with `SCRIM=1 KEEP_ALL=1` | good | **steal**; if galaxy schedules the ladder, keep it for delivery and band blocks |
| `mirror.sh` | SPRT mirror: batches of `BATCH` random (map, side, seed) cells through `paired.sh` (default) or gauntlet; `sprt.py` after each batch; ACCEPT, REJECT or INCONCLUSIVE; `W0/L0` resume | good; note the stale default `REF=g_iter4` | steal; make REF required |
| `paired.sh cells.txt` | each cell (map, side, seed) as BOT vs REF and REF vs REF on the same seed (or both vs `OPP`); counts `LOGTAG` lines BOT printed (needs `robot-player-to-system-out=true`); deletes concordant replays; prints concordant W/L, discordant each way, exact sign-test p, "same end round", "mechanism fired in" | good; the core of exact pairing | **steal**. 2023 caveat: the final tiebreak coin flip uses unseeded `Math.random()` (§7.2), so a game reaching it can be discordant with identical code. Report `WON_BY_DUBIOUS_REASONS` games separately. |
| `compare.py base_run cand_run [--opponent]` | game-by-game diff on (opponent, map, side): identical cells, flips each way with maps, sweeps, per-side split, maps with more than one flip ("read the shape") | good | steal |
| `filler-pair.sh ctl cand[,cand2] [N]` | idle filler: control and candidates play the same fresh band cells (one seed); census each; calls `vm-prune.sh` first | good | adapt (`.bc23`, census) |
| `collect-fillers.sh [ctl cand]` | driver side: fetch finished filler runs not yet in games.csv, record under their label, refit and charts, run the paired tally | good, but its default `CTL=g_iter1` is stale (MEAS10) | adapt; require arguments |
| `filler-tally.py ctl cand` | running paired tally over filler seeds: gained, lost, net, SE, identical share, discordance | good (MEAS2 fix prints discordance) | steal |

### 6.3 Ladder, ratings and charts

| file | what it does | quality | 2023 verdict |
|---|---|---|---|
| `elolib.py` | `progress/games.csv` (`run,seq,teamA,teamB,map,winner,rounds,reason,seed`; ours as `us:<build>`). `fit()`: Bradley-Terry by minorise-maximise, prior 1 win + 1 loss vs a 1500 anchor, `dedupe` on (A, B, map, seed), `PAIR_CAP = 200` (each game of a pair with n > 200 weighs 200/n), iterates to `tol=1e-10` (up to 100,000) and warns otherwise; SE from Fisher information; `field_score`, `current_build`, `accepted_builds` | good; year-agnostic; tested (play-order independence, builds rated separately, unmet bot = 1500) | **steal as-is** |
| `elo.py` | ranking table, `progress/ELO.md` and `elo.png` (matplotlib from `tools/.venv`); pool selection `--band N --explore K --as BUILD`, `--pool`, `--established`, `--challenge`; `--build X` gives the record with a Wilson 95% interval, rating, rank and field score; the incumbent's record per opponent with a thin-sample `*` | good | steal; the driver lacks matplotlib (the chart is skipped with a message) |
| `scrim-record.py run --label B` | appends a run's results to games.csv, idempotent per run id; refuses puppets and our own packages as opponents (self-play never grades); stores `reason[:40]` | good | **adapt**: the 40-character cut merges all four 2023 tiebreak reasons (§7.1). Store a reason code and a code hash. |
| `post-block.sh run label` | one command after a block: collect, record, refit, field-score chart, progress chart, roster, study, correlate, onset, merged onset, tactics survey | good: this is how "nothing stale" was kept | adapt; trim the 2024 study steps |
| `field-score.py` | rating per submission over time, fitted `R = R0 + a ln(1 + t/tau)` by weighted least squares, mapped to field score, score vs higher-rated bots and rank, projected to week 1 and week 4 (no projection until 3 submissions span half a day: "two builds an hour apart extrapolated to a rating of 26,000"). Needs numpy and matplotlib | good chart for the owner | adapt: `START` date and horizons are hard-coded (2026-09-30); PDT conversion is right |
| `progress-chart.py` | `progress.png`: rating ± 95% and field score of every accepted `g_iterN` | simple, good | steal |
| `sprt.py W L [--p0 --p1 --alpha --beta]` | Wald SPRT -> ACCEPT, REJECT or CONTINUE with the LLR and bounds | correct (tested at the accept boundary) | steal (fix the "no draws in BC20" docstring) |

### 6.4 The replay reader: `replaydump/ReplayDump.java` + `replay-dump.sh`

`replay-dump.sh` compiles `ReplayDump.java` on demand into `build/replaydump-<sha1 of source>` against the engine
classpath, so an edit recompiles automatically and parallel callers share the build. Then it runs
`java replaydump.ReplayDump <replay> [flags]`.

**Modes:**
- summary (map, symmetry, seed, per-team totals, winner and win type);
- `--every N`, `--metrics N` (per-team CSV with columns `METRIC_COLS`);
- `--from R --to R` (an event window: spawns, deaths, actions, flags);
- `--robot ID` (one robot's life), `--map-at R` (ASCII board);
- `--logs REGEX [--team]` (indicator strings);
- `--bytecode`, `--near90`, `--navstats` (coverage, moves per robot-round, ABA oscillation, still rounds);
- `--flags`, `--levels`, `--comm R-R2` (the stored shared array);
- `--capabilities` (one census row per team per game, about 118 columns by October);
- `--survey` (tactic features), `--trapgeo`, `--defense`;
- 2024 study modes: `--track`, `--contact-d0`, `--recall-d0`, and a `--calc` stdin calculator.

Unknown flags are hard errors (exit 2). Quality: it is the project's microscope, and integrity-tested on two committed
fixtures (`test/fixtures/example-DefaultSmall-s1.bc24` and `bot-vs-example-DefaultSmall-b1.bc24`):
- the summary matches the engine result;
- A's deaths equal B's kills;
- cumulative columns never decrease;
- captures plus carrier deaths never exceed pickups;
- `--metrics 50` gives 40 rounds x 2 teams.

**Verdict: rewrite against the 2023 schema, keeping the mode list, the cached-compile wrapper, the hard-error flags and
the fixture integrity tests as the spec.** The reusable skeleton is unchanged:
- `load()`, which gunzips if the magic is `1f 8b` (true for `.bc23`);
- `run()`, which walks the `GameWrapper` events (`GameHeader`, `MatchHeader`, `Round`, `MatchFooter`); 3.0.15 uses the
  same event union names.

What changes, from `reference/battlecode23/schema/battlecode.fbs`:

| 2024 replay (what ReplayDump relies on) | 2023 replay (3.0.15) | consequence for the 2023 reader |
|---|---|---|
| `Round.robotIds/robotLocs/robotHealths` and per-robot levels and cooldowns: a full snapshot every round | **no snapshot**: `movedIDs` + `movedLocs` (movers only), `spawnedBodies` (id, team, **type**, loc), `diedIDs` | keep a live state map: position updated from moves, type and team from spawns, removal on death. Initial HQs come from `GameMap.bodies`. |
| HP per robot per round | **only `Action.CHANGE_HEALTH`** (target = health delta) | HP = type max (`RobotType` health) + summed deltas. Test: HP never exceeds max, and a death follows HP <= 0. |
| `teamCommunication` (CommTable): the whole shared array every round | **not stored** | `--comm`, `symOk`, `psymOk` and every slot contract (audit systematic test 3) cannot read the array from the replay. The bot must print what tools need (its symmetry mask, decided round, key slot values) in the first fields of its indicator string, and the reader parses them. |
| `teamResourceAmounts` (crumbs now) | `teamIDs` + `teamAdChanges`, `teamMnChanges`, `teamExChanges` (per-round **changes**) | totals by cumulative sum. Income vs spend needs action attribution: `PICK_UP_RESOURCE`, `PLACE_RESOURCE`, `SPAWN_UNIT`, `BUILD_ANCHOR`. |
| `MatchFooter.winType` (CAPTURE, LEVEL_SUM, ...) | `MatchFooter` has `winner`, `totalRounds`, `profilerFiles` and **no win type** | the reason exists only in engine stdout (`DominationFactor`: CONQUEST, MORE_SKY_ISLANDS, MORE_REALITY_ANCHORS, MORE_ELIXIR_NET_WORTH, MORE_MANA_NET_WORTH, MORE_ADAMANTIUM_NET_WORTH, WON_BY_DUBIOUS_REASONS, RESIGNATION). Gauntlet must keep it in results.csv, and the summary must not pretend to know it. **(inference)** Reconstructing it from island ownership and anchor counts at the last round is possible, with a test against stdout. |
| one bytecode limit (25,000) | per-type limits (HQ 20000, Carrier 12500, others 10000) | `BYTECODE_LIMIT` becomes a per-body-type lookup, using types from `spawnedBodies.types`. |
| `GameMap`: `size`, `walls`, `water`, `divider` (dam), `spawnLocations`, `resourcePiles` | `minCorner`/`maxCorner`, `symmetry` (0 rotation, 1 horizontal, 2 vertical), `bodies`, `randomSeed`, `walls`, `clouds`, `currents`, `islands`, `resources` | new board layers. `symmetry` gives a truth column for the symmetry basics bar. |
| actions ATTACK, HEAL, DIG, FILL, traps, flags, GLOBAL_UPGRADE, DIE_EXCEPTION | `LAUNCH_ATTACK`, `THROW_ATTACK`, `SPAWN_UNIT`, `PICK_UP_RESOURCE`, `PLACE_RESOURCE`, `DESTABILIZE`, `DESTABILIZE_DAMAGE`, `BOOST`, `BUILD_ANCHOR`, `PICK_UP_ANCHOR`, `PLACE_ANCHOR`, `CHANGE_HEALTH`, `CHANGE_ADAMANTIUM`, `CHANGE_MANA`, `CHANGE_ELIXIR`, `DIE_EXCEPTION` | rewrite the action switch. `ACTION[]` must follow the 2023 enum order. The schema comment says an attack's target is "ID for direction", but the engine writes the victim's robot id, or `-(x + y*W) - 1` for an attack on an empty tile (`InternalRobot.java:408-412`, `InternalCarrier.java:66-70`). Trust the engine. |
| — | `islandIDs`, `islandTurnoverTurns`, `islandOwnership`; `resourceWellLocs` + well values; `wellAccelerationID` | new per-round state: an island ownership timeline (the win condition) and well state. |
| `indicatorStrings`, `bytecodeIDs`/`bytecodesUsed` | same fields, plus indicator dots and lines | `--logs`, `--bytecode` and `--near90` port directly (same 64-character cap). |

**2023 census columns to build first (inference):**
- per team: Ad, Mn and Ex delivered by phase (r100/r300/r600); carriers alive and idle; carrier trips and mean trip
  rounds; launchers built and lost; kills and deaths by type; HQ damage dealt;
- anchors built, picked up and placed; islands held per round; first island round;
- `symWrong` and `symDecidedRound` (from the indicator string vs `GameMap.symmetry`);
- overruns, near misses (per-type limit), caught exceptions (from the indicator's `x` field, MEAS7);
- navigation coverage and stillness.

### 6.5 Census, study and statistics

| file | what it does | quality | 2023 verdict |
|---|---|---|---|
| `capability-census.sh out.csv run...` | `replay-dump --capabilities` over every replay of the runs (`P` parallel, `nice 19`) -> one row per team per game plus `file,opp,us` | the pipefail bug fixed (10-04); still no K-of-M check (MEAS3 fix proposed) | adapt; add "K of M against results.csv, exit non-zero on mismatch" |
| `capability-summary.py` | medians us vs them, split by opponents that beat us and the rest, and by our wins and losses -> `research/CAPABILITY_CENSUS.md` | fine; the two-group split is what found the heal hold (S3) | adapt the column list |
| `basics.py census [--survey] [--base]` | basics battery. Absolute bars: `symWrong == 0`; symmetry decided by r201 in >= 95% (setup-decidable maps) or by r400 in >= 90% (15 named post-setup maps); overruns == 0; exceptions == 0. Relative to a base (FAIL only if worse by > 2 SE): stillPost, k/d, trapsHit, gathered400, floating250. A column missing from the census, or from a base that was given, fails ("a basic that is not measured fails"). Exit 1 on any fail | good design; k/d unpaired (MEAS6); exceptions vacuous (MEAS7) | **adapt**: 2023 columns; paired log-ratio for k/d; caught exceptions from the indicator; per-type bytecode; the bar maps derived from all 103 maps offline ("compute the bound offline over every map and side", AUDIT_PROMPT) |
| `eval-paired.py ctl.csv arm.csv runC,runA... [--tier] [--rung] [--look N]` | pairs cells by (run, replay basename with seed); slices all, upper tier and rest; wins, gained/lost, exact sign p, capture-difference delta ± SE (t), identical count; `ship_decision(look, t_all, t_up, net)` | good, tested | **adapt**: pick 2023's per-pair margin (islands held at the end, or anchors placed, or a continuous resource margin); re-simulate power before adopting the thresholds (M3) |
| `delivery-gate.sh arm "checks"` + `delivery-check.py` | a 24-cell mini-block on the band (or `DGPOOL` with a required `DGTAG`, or `DGMAPS`), census and survey, checks `median:`, `mean:`, `fire:col>v>=share`, `rel:col<=ratio` (paired vs `BASE` on the same cells), `nw:` guards; three-way verdict; auto-extends on INCONCLUSIVE; writes `gauntlet/delivery-<arm>.{PASS,INCONCLUSIVE,FAIL}` | good after MEAS1/MEAS13; base cache shared across gates (MEAS4, open) | **steal the logic**; draw a fresh base seed per gate (or pool 3+); key the cache on sha1(base src, pool, N, seed, reader source) |
| `band-test.sh arm` | 2 seeds x 120 games on `tools/band.txt` with seeds from `band-seeds.txt`, then census; **refuses without a delivery PASS** unless `NO_DELIVERY_REASON` | good; PASS not tied to code (MEAS10) | steal; refuse if the arm's source hash differs from the one in the PASS file |
| `arm-deltas.py` | paired per-column deltas (mean ± SE) of an arm vs control on identical cells, optionally on "beater" cells only | good | steal |
| `statlib.py` | `pointbiserial`, `noise_floor(n) = 2/sqrt(n)`, `onset` (first round a correlation reaches the threshold and holds at 0.8 of it the next sample, signed), `anti_onset`, `within_group` (deviations from each opponent's mean) | good, unit-tested | **steal** |
| `polarity.py`, `derived.py` | metric orientation (higher = better for us) and derived `net = kills - deaths`; `STUDY_COLS` | fine | adapt the column lists |
| `correlate.py run [--round R]` | point-biserial of every metric and us-them gap with the result, by round; warns that late-round correlations are "the outcome leaking backwards" | good caution | steal |
| `onset.py run` | correlation curve per metric over rounds; metrics ranked by onset; markdown and plot | good idea; ONSET was stale at shutdown | steal; run on merged blocks (one block's noise floor 0.30) |
| `scrim-study.sh run` + `scrim-study.py` | per-team metrics every 50 rounds and navigation stats for every replay -> `study.tsv`, `nav.tsv`; medians by round, wins vs losses | fine | adapt |
| `onset-merged.sh build` | onset over every block of a submission (>= 200 games) | exits quietly when no `study.tsv` exists (never produced for g_iter7) | adapt or fold into onset.py |
| `tactics-survey.py` | `--survey` over every kept replay, cached in `progress/survey.csv`; per-opponent named tactics by thresholds -> `progress/SURVEY.md` | fine (the owner's standing order kept TACTICS.md current) | rewrite the 2023 tactic list |
| `premise.py`, `contact-d0.py`, `recall-d0.py` | pre-registered premise checks (routes and bars pinned before the data) over `--track`, `--contact-d0` and `--recall-d0` rows; a missing replay or failed dump turns into a PARTIAL report with exit 1 | careful sample checks; 2024-specific content | **skip the content, steal the pattern**: "the sample is checked, never assumed" (K of M, kind=missing rows, PARTIAL exit) |
| `defense-profile.py`, `fill-origin.py`, `stun-check.sh`, `side-indsum.sh` | 2024 flag-trip, dig/fill origin, stun latency and indicator-counter sums | `side-indsum` once read the wrong team (T4) | skip (keep "max over a robot's strings" from side-indsum for counters cut at 64 characters) |
| `log-scan.sh` | meant to extract our log lines per game | **broken: can never produce output** (MEAS17) | skip |

### 6.6 VM and operations

| file | what it does | quality | 2023 verdict |
|---|---|---|---|
| `vm.sh` (sourced) | `VM=battlecode-dev2 ZONE=us-west2-a PROJECT=tvanbelle-vibecode`; ssh options with timeouts and keepalives; `ensure_vm` (cached IP trusted after one probe; starts the VM if stopped; waits for ssh); `vm_games` via `pgrep -fc "[b]attlecode.server.Main"` | good | **adapt**: `REMOTE_REPO='projects/vibe/2023'`, `VM_IP_CACHE` name. The VM is stopped and reusable (HANDOFF). The original `battlecode-dev` zone had no e2-standard-8 capacity on 09-30. |
| `vm-run.sh name 'cmd'` | sync, then `setsid nohup bash -c CMD > gauntlet/<name>.log & disown` | good; the comment explains why `cd X; CMD &` and not `cd X && CMD &` (the latter hangs the ssh) | steal |
| `vm-queue.sh` | standing runner: re-execs from a private copy (vm-sync replaces tools/ under it); one runner via `flock`; runs `queue/pending/*.job` in name order (moved to `running/`, then `done/`), each with its log; when idle, runs `queue/filler.job`; a `STOP` file exits | good after B12 (exit code captured right after the job) | **steal**; add a back-off when a job fails fast (the disk-full incident spun 18 minutes) |
| `vm-enqueue.sh name 'cmd'` | sync (5 retries), then write `queue/pending/<UTC stamp>-<name>.job` atomically (tmp + mv); `FILLER=1` replaces the filler | good | steal |
| `vm-sync.sh` | tar over ssh (no rsync on the VM): JDK once, benchmark classes and manifest once (`FULL=1` re-pushes), engine if missing, then `src tools test progress` and two docs **swapped in by rename**. The old `rm -rf && tar -x` left a window with no `tools/`, and a gate lost ten cells to it. `progress/` travels so `scrim.sh` sees games.csv | good | adapt paths; engine check `engine/battlecode23-3.0.15.jar` and `engine/patch/` |
| `vm-collect.sh run` | pull a run's results, summary and logs; **replays stay on the VM unless `REPLAYS=1`** (local copies filled the driver disk twice) | good | steal |
| `vm-prune.sh` | above `THRESH`% disk, delete `.bc24` files older than `AGE` minutes from scrim runs that have results, except builds in `keep-replays.txt`, delivery-gate bases (`*-dg<seed>`), the newest `KEEP_FILLS=25` filler runs per kept build, and diagnostics for `DIAG_AGE=1440` minutes; never touches results or census | good; earlier rules deleted replays still needed (880 g_iter5 filler replays) | steal; better, key retention to declared consumers (T3) |
| `vm-stop.sh` | stops the VM only if no games are in flight | good | steal |
| `vm-tail.sh name [lines]` | tail of a remote log plus games in flight and load | good | steal |

### 6.7 Tests and static checks

| file | what it does | quality | 2023 verdict |
|---|---|---|---|
| `unit-tests.sh` | compile `src/bot` + `test/bot` against the engine; run every `*Test` main (no JUnit; exit 1 on failure); re-run ContactTest and AuditTest's arm tests on sed-made copies of `src/bot` with switches on (javac drops hooks behind `static final false`); `deadcode.py src/bot`; `test_metrics.py`; `test_tools.py` | good coverage; about 10 minutes on the 2-vCPU driver and run about 220 times (T5); no lock | **adapt**: add `flock`; split fast tests (bot logic, seconds) from slow ones (replay fixtures); use non-final switches (§5.2) so no sed copies are needed |
| `test/bot/BotTest.java` | **fake `RobotController` via `java.lang.reflect.Proxy`**: a 64-slot shared array with write-range checks, vision dist² 20, walls and water, robots, `canMove`/`move`, `canAttack`/`attack`, cooldowns, crumbs; tests of Comms encoding, slot layout, the RNG, the Micro threat radius and targeting, symmetry images, and the Track packers | good pattern | **steal the pattern**: 2023 `RobotController` is also an interface (`public strictfp interface RobotController`), so the Proxy works. Model the 2023 rules (write ranges, per-type cooldowns, carrier capacity and weight, clouds, currents) and pin them against the engine source (audit systematic test 1: "an engine-contract fake controller") |
| `test/bot/SymTest.java` | the property test over 300 random symmetric maps plus hand cases (§5.4) | good | **steal and extend** to real `.map23` maps loaded from the jar |
| `test/bot/AuditTest.java` | regression tests per audit finding (A1-A9, BOT*), including reference vs fast equivalence and a paused-scan equivalence | good | pattern only |
| `test/bot/ContactTest.java` | the g4contact arm's hooks, run with the switch off and on | arm-specific | skip |
| `test/fixtures/*.bc24` | two committed replays (example mirror on DefaultSmall seed 1; our bot vs example, won by capture at r746) used by test_tools' integrity checks | essential | **regenerate for 2023**: one example mirror and one of our games, committed (about 0.6-1.1 MB each in 2024) |
| `test_tools.py` | 1,031 lines, 208 checks: SPRT boundaries, Elo fit properties, scrim-record, bench-select, replay-dump fixture integrity, census, delivery gate verdicts, band-test refusal, filler-tally, scrim reproducibility, vm-prune keep rules (temp tree), eval-paired, deadcode, arm-intent, basics | good; "every check names what it protects" | adapt: keep the year-agnostic blocks (about half), rewrite the replay-dump block for the new fixtures |
| `test_metrics.py` | polarity, derived, statlib, correlate and onset end to end on a synthetic block | good | steal |
| `deadcode.py [pkg] [--allow]` | lists methods never called and `static final` constants never read (comments and strings stripped); exit 1 if any | useful, but blind to code behind false switches and to write-only fields (MEAS14) | steal and extend (constant folding over `C`, write-only fields) |
| `arm-intent.txt` | `<arm> <File.CONSTANT>=<value>` lines checked by test_tools against `src/<arm>/<File>.java` | small, high value | steal |

### 6.8 Data lists in `tools/` (not read; line counts only)

- `bc24-maps.txt` (78 maps), `ladder-bots.txt` and `roster.txt` (55 each), `band*.txt` (20), `band-seeds.txt` (3),
  `upper-tier.txt` (5), `keep-replays.txt` (5), `next-rung.txt` (4), and two map-class lists for 2024 studies.
- All are regenerated or replaced for 2023. The idea worth keeping is that band, seeds and tier are files refreshed at
  each promotion (PROMPTS 184-185), not constants in scripts.

---

## 7. Pitfalls and gotchas (cost where stated)

### 7.1 New for 2023 (found while mapping; not in the 2024 docs)

1. **`scrim-record.py` truncates the reason to 40 characters.** All four 2023 tiebreak reasons begin "The winning team won
   on tiebreakers (mor", which is exactly 40 characters (checked with Python on the 3.0.15 `Server.java` strings). Islands,
   anchors, elixir, mana and adamantium wins would be indistinguishable in games.csv. Store a short reason code parsed
   from stdout.
2. **The 2023 replay has no win type, no shared array, no per-round HP or position snapshot** (§6.4). Every 2024 census
   column that read those must be redesigned, and the bot must print what the tools need in its indicator string.
3. **The final coin flip is unseeded.** `GameWorld.setWinnerArbitrary()` calls `Math.random()` (3.0.15
   `GameWorld.java:627`). The comment in `2023/tools/get-engine.sh` says "robot ids, every sandboxed Random and the final
   coin flip derive from the map seed". The last part is not true of the engine source. Games that reach
   `WON_BY_DUBIOUS_REASONS` are not reproducible under a fixed seed and must not count as discordant pairs. 2024 had the
   same property ("The engine's final tiebreak uses unseeded `Math.random()`", HANDOFF gotchas).
4. **`examplefuncsplayer` may ignore the seed.** In 2024 it used a static `Random(6147)`, so its mirror games were
   identical across seeds (HANDOFF). Check the 2023 example bot before using it in an identity control.
5. **Per-type bytecode limits and a 500-bytecode exception penalty.** A single 22,500 near-miss constant would never fire
   for a 10,000-limit launcher.
6. **Gauntlet bypasses `lib.sh`.** Its inlined `java` command would not get the 2023 `team-X.package` flags or the patched
   classpath. Route it through `run_game`.

### 7.2 Carried from 2024 (cost as written)

1. **Unseeded paired cells:** about 2.5 days of gained/lost tallies "mostly noise" (M1).
2. **Disk:**
   - The driver disk filled by 10-02 01:56 UTC (2.6 GB of replays). The VM's 49 GB disk filled on 10-02 at 12:12 UTC
     (35 GB of replays); the runner spun for 18 minutes, and census CSVs were committed empty (T3).
   - On 10-07 the driver had 85 MB free of 30 GB, mostly other projects (TRAINING_LOG).
   - **For 2023:** the driver now has 3.4 GB free. The 2024 replays on the VM should be archived or cleared before 2023
     runs (the owner has permitted clearing bc24 local storage). Keep `vm-collect` replay-free by default.
3. **Unrecorded filler:** 17 blocks, about 2,000 games (P2).
4. **Name-keyed results:** 2.5% of band pairs and 9-12.5% of single-opponent census games dropped. g_iter2 invisible on
   GitHub (MEAS3, MEAS10, O3).
5. **Editing a running bash script** corrupts it. A predecessor project lost a finished 450-game collation; both
   gauntlet.sh and vm-queue.sh re-exec from a copy.
6. **A shared class tree recompiled under running games:** a whole block silently played a different bot (09-20,
   gauntlet.sh comment). A parallel-compile race lost 2 of 234 band games (T5). Six of twenty diagnostics were lost to a
   shared dev-classes tree (run-dev.sh comment).
7. **`pkill -f` / `pgrep -f` match the issuing shell:** five incidents; two "until ! pgrep -f" waits spun about 10
   minutes each (F5). Use `ps | awk` or a `[b]racket` pattern.
8. **Too many games at once:** 24 diagnostic games on 8 vCPUs starved the VM's sshd for minutes (cap at 8). The driver
   plays one game at a time: "Driver game on DefaultSmall takes 2-4 minutes" (HANDOFF).
9. **`$?` after a command substitution:** the queue logged every job "exit 0" (B12).
10. **A sed that flips a switch can silently match nothing.** An arm ran with its switch off (g1sym verification 4). Use
    a regex that asserts one match, plus `arm-intent.txt`.
11. **The 64-character indicator cap:** notes cut on about three quarters of turns (MEAS5). Put the note and the
    must-have counters first, and test the worst-case length.
12. **`Clock.getBytecodesLeft()` returns 0 outside the engine:** tests need an override (`G.testBc`).
13. **An unconverged rating fit:** ratings 30-44 low for days (MEAS11). Iterate to tolerance and warn.
14. **One opponent sampled thousands of times distorts BT** under non-transitive matchups (M8). Cap pairs.
15. **Maven artefacts for 2024 returned 403**, and a rotted jsi snapshot needed a local jar (build-engine.sh). For 2023
    this is already solved by the checksum-pinned fat jar.
16. **The unit suite on a 2-vCPU driver:** about 10 minutes per run, about 220 runs (T5), roughly 36 hours of driver time
    **(inference: 220 x 10 minutes)**. Split fast and slow tests.

---

## 8. Top 15 takeaways for the 2023 project (ranked by expected value)

1. **Port the paired, seeded harness first and prove it with an identity control.** That means `scrim.sh`'s fourth-field
   seed, `paired.sh`, `sprt.py`, `compare.py` and `filler-tally.py`, then a byte-identical copy reading 0 discordant on
   the exact verdict path. Exclude coin-flip games, which are unseeded in 3.0.15. Nothing else is interpretable without it
   (M1: 15-29% flips otherwise).
2. **Rewrite ReplayDump for `.bc23` on day one, keeping its mode list, cached-compile wrapper and fixture integrity tests.**
   Reconstruct state from deltas (moves, spawns, deaths, `CHANGE_HEALTH`, resource changes, island ownership). Use
   per-type bytecode limits. Read the win reason from stdout. The census found the largest single lever of 2024 (+144).
3. **Make the bot report what the replay cannot.** In 2023 the replay holds no shared array and no stdout. Put the
   symmetry mask and decided round, caught exceptions, overruns and the mechanism counters in the first characters of
   the 64-character indicator string, and test the worst-case length (MEAS5, MEAS7).
4. **Port `Sym.java` and `SymTest.java` nearly verbatim**, with 2023 fixed features (walls, clouds, currents with
   transformed direction, wells, islands, HQs) and a scout to the nearest distinguishing enemy-HQ image. Check
   correctness from replays against `GameMap.symmetry`. Symmetry was guessed wrong in 28-34% of 2024 games before the fix.
5. **Steal `elolib.py`, `elo.py` and the record format as the analysis layer under the galaxy ladder.** That is batch BT,
   dedupe by seed, pair cap 200, convergence warning, each build its own player. Fix `scrim-record.py`'s 40-character
   reason cut and add a code hash per row.
6. **Steal the VM stack** (`vm.sh`, `vm-run`, `vm-queue` with flock and private copy, `vm-enqueue`, `vm-sync` with
   rename-swap, `vm-collect` without replays, `vm-prune`, `vm-stop`) with `REMOTE_REPO` changed. Add a fail-fast back-off.
   It recovered the 29% idle time.
7. **Port the BotTest Proxy fake controller and pin it to the 2023 engine contract.** That means write ranges for the
   shared array, per-type cooldowns, carrier weight and capacity, clouds and currents. Tests that run on a lenient fake
   pass code the engine refuses.
8. **Route `gauntlet.sh` through the already-ported `run_game`.** Key every result and replay by (code hash, opponent,
   map, side, seed), and record a reason code (T2, MEAS3, MEAS10).
9. **Install the refusing gates before the first arm:** `delivery-gate.sh` + `delivery-check.py` (three-way, extend on
   INCONCLUSIVE, a fresh base seed per gate) and `band-test.sh` (refuse without PASS, refuse on a code-hash mismatch).
   They stopped about ten undelivered arms before 240-game tests.
10. **Choose the 2023 per-pair margin and simulate the shipping rule's power before using it.** Candidates are islands
    held or anchors placed at the end, and a resource margin. The 2024 rule went from 17% to 63-65% power at 2.0% false
    promotion (M3).
11. **Run `basics.py`, rebuilt for 2023, on every build.** Absolute bars: symmetry never wrong and decided in time
    (bounds computed offline over all 103 maps), 0 overruns at per-type limits, 0 caught exceptions. Relative checks are
    paired and fail only beyond 2 SE (MEAS6).
12. **Keep `deadcode.py` and `arm-intent.txt` in the unit suite, and extend `deadcode.py` with constant folding and
    write-only fields.** In 2024, 32% of the incumbent was dead, and a switch once silently ran off.
13. **Copy the bot plumbing, not the 2024 behaviours.** Keep the turn loop with overrun and near-miss monitoring, per-id
    xorshift RNG, rng tie-breaks, the documented constants file, the Comms schema header with pure packers and a
    slot-layout test, and the bytecode-budgeted resumable scans. Rebuild nav (currents), micro (launcher ranges) and the
    economy for 2023.
14. **Protect the disks.** Replays stay on the VM, retention is keyed to consumers, and there is a disk check before
    writes. The 2024 project filled the driver twice and the VM once. The driver has 3.4 GB free now. Clear or archive
    the 2024 replays on the VM before reuse.
15. **Keep `post-block.sh` as the one command after every block** (record, refit, charts, study, survey), with
    `progress-chart.py` and an adapted `field-score.py`. Install matplotlib in `tools/.venv` on the driver: it is missing
    now. The owner reads progress through these generated files (O3).
