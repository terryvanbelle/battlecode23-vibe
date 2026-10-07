# bcenv (anicolao/bcenv): research reader report for the 2023 project

Slice: `bcenv`. Repo: `/home/terryvanbelle/projects/vibe/reference/bcenv` at commit `7f868dc`
(2026-09-11 10:02 -0400, Alex Nicolaou, "Center the design on supervised NixOS competitor environments"; the
local clone holds only this one commit). Documents were read only from
`/home/terryvanbelle/projects/vibe/reference/readroom-no2023/bcenv/`.

**Summary.** bcenv is a design and research repository, not an environment. Its README says: "This project is
in its initial design stage. There is no implementation or runnable environment yet." It has no simulator, agent,
match runner, Elo code, replay parser, Nix flake, Dockerfile or season integration. Its only executable code is a
Husky git hook (`scripts/check-prompts.mjs`, 35 lines) and its test (`scripts/check-prompts.test.mjs`, 70 lines).
The hook enforces a byte-for-byte append-only `PROMPTS.md`. Its value for 2023 lies elsewhere:

1. A sourced survey (`HISTORICAL_LEARNINGS.md`) that turns the anicolao/battlecode-2026 campaign and Terry Van
   Belle's 22/26/25 projects into a catalogue of failure modes, especially bugs in the evaluation tooling itself.
2. A design (`INITIAL_DESIGN_SKETCH.md`) for trustworthy evaluation: frozen experiment manifests, job accounting,
   paired comparisons, block-level uncertainty, holdouts, manipulation checks and a hypothesis register.
3. The hook, which can guard 2023's `PROMPTS.md` and `TRAINING_LOG.md` after a small change.

The bc20, bc21 and bc24 projects already read bcenv as mandatory input. The bc24 project wrote its own review
(`readroom-no2023/bc24/research/BCENV.md`, 14,885 bytes) of the same commit and reached the same verdict:
"a well-sourced design document plus a 35-line git hook".

---

## 1. Scope

### 1.1 Read in full

| Path | Size read | Original size (stat only) | Notes |
| --- | --- | --- | --- |
| `readroom-no2023/bcenv/HISTORICAL_LEARNINGS.md` | 60,385 B, 451 lines | 73,195 B (527 lines per the bc24 review) | about 12.8 KB removed by the 2023 filter |
| `readroom-no2023/bcenv/INITIAL_DESIGN_SKETCH.md` | 39,493 B, 324 lines | 41,314 B (332 lines per the bc24 review) | about 1.8 KB removed |
| `readroom-no2023/bcenv/README.md` | 5,647 B | 5,647 B | unfiltered |
| `readroom-no2023/bcenv/PROMPTS.md` | 3,551 B | 3,551 B | 10 owner prompts, verbatim |
| `readroom-no2023/bcenv/VISION.md` | 1,701 B | 1,701 B | |
| `readroom-no2023/bcenv/AGENTS.md` | 1,016 B | 1,016 B | |
| `bcenv/scripts/check-prompts.mjs` | 1,500 B, 35 lines | (code, read directly) | the only tool |
| `bcenv/scripts/check-prompts.test.mjs` | 3,372 B, 70 lines | | hermetic `node:test` suite |
| `bcenv/.husky/pre-commit`, `.husky/pre-merge-commit` | 31 B each | | both run `node scripts/check-prompts.mjs` |
| `bcenv/package.json` | 275 B | | husky 9.1.7, scripts `prepare`, `check:prompts`, `test` |
| `bcenv/package-lock.json` | 695 B | | lockfile with one package, `node_modules/husky` |
| `bcenv/.gitignore` | 14 B | | `node_modules/` |

The tree has 14 files and no `src/`, `tools/`, `flake.nix`, `Dockerfile` or `.github/`.

### 1.2 Skimmed

- `bcenv/LICENSE` (35,149 B): only the header, which is standard GPLv3 text.
- **Filter gaps.** I never opened the original `.md` files. Their sizes come from `stat`, which reads metadata
  only. In the filtered `HISTORICAL_LEARNINGS.md`, source notes 6, 27, 43–46, 48, 50–53, 59–60, 78–81 and 98
  are now defined but never cited, and note 57 is cited but undefined. From those orphans, the removed blocks
  appear to have covered:
  - a 2015 paragraph;
  - the 2022 season section;
  - the body of "Concrete experiments, with their limits" (StrategyChooser, FightMicroGA, an REU poster,
    Re;Battlecode22, Ratbot);
  - CodeClash's training arenas and arena adapters;
  - Cambridge Battlecode;
  - most of "Repository references and upstream ancestry";
  - the XSquare guide note.

  In `INITIAL_DESIGN_SKETCH.md`, notes 11 and 12 are cited but undefined, and "Relationship to earlier
  environments" starts mid-thought ("Their match, submission, and replay tools..."). I did not try to
  reconstruct any removed content.

### 1.3 Read for cross-reference (outside the bcenv repo, allowed sources only)

- `readroom-no2023/bc24/research/BCENV.md` (filtered): the bc24 project's review of this same commit. It has a
  `[REDACTED]` note where 2024 post-mortems were cited, and its section 5 is empty after filtering.
- `readroom-no2023/bc26/TRAINING_LOG.md` lines 3365–3440: the external-benchmark entry. It contains independent
  evidence about the anicolao/battlecode-2026 bot that bcenv describes.
- Headers of `readroom-no2023/bc20/` and `bc21/` (`TRAINING_ALGORITHM.md`, `TRAINING_LOG.md`, `RESEARCH.md`) and
  `bc24/PROMPTS.md` line 12, to see how later projects used bcenv.
- Official 2023 engine source, `reference/battlecode23` @ `af42086` (2023-02-05):
  `RobotControllerImpl.getResourceAmount` and `buildRobot`, `Server.getWinnerString`, and the `DominationFactor`
  enum. I also extracted the reason strings from the pinned jar `2023/engine/battlecode23-3.0.15.jar`
  (`battlecode/server/Server.class`) to check that the source matches 3.0.15. These checks map bcenv's lessons
  onto 2023 facts; they are marked **[engine-verified]** below.
- The 2023 project's `tools/lib.sh` (`parse_result`), lines 65–85 of `tools/test_tools.py`, and grep hits in
  `tools/summarize.py`, `elolib.py` and `gauntlet.sh`. The purpose was to see which bcenv lessons the project
  already implements.

### 1.4 Not available or skipped

- The private repos and PRs that bcenv cites (anicolao/battlecode-2026 `scripts/*.py`,
  `tools_src/tools/InspectReplay.java`, `build.gradle`, PRs #30–#33) are not in the local reference tree.
  Everything I report about them is bcenv's description, not my own inspection.
- battlecode25-vibe's `tools/bot_identity.py`, `tools/tournament.sh` and `tools/agent-watchdog.sh` are not in the
  local reference tree. Their documents sit in `readroom-no2023/bc25/`, and the sibling report
  `2023/research/prior/bc25-docs.md` already covers them.
- No external links were followed (no network), and no games, builds or npm commands were run.

---

## 2. What worked (evidence as written)

bcenv ran no experiments. Every number below is quoted from bcenv's documents, which repeatedly say these are
"self-reported" and "not independently reproduced", or from the cross-reference files named in each item.

### 2.1 The prompt-record hook works, and its test is a good pattern

- `check-prompts.mjs` reads the **staged** blob (`git show :PROMPTS.md`) and `HEAD:PROMPTS.md`. It rejects the
  commit unless the staged file starts with HEAD's bytes exactly and the new tail contains non-whitespace. It
  also requires the index entry to match `^100644 <sha> 0\tPROMPTS.md\n$`, which means a regular, non-executable
  file that is not in a merge-conflict stage. It handles an unborn `HEAD` (a repository with no commits) so the
  first commit works.
- `check-prompts.test.mjs` builds a temporary git repo with `GIT_*` variables scrubbed, `XDG_CONFIG_HOME`
  redirected and `commit.gpgsign=false`, then checks 11 cases:
  - **Rejected:** missing initial record, blank initial record, unchanged record (`--allow-empty`), unstaged
    addition, whitespace-only addition, rewritten history with an addition, truncated record, deleted record,
    and a direct run of `.husky/_/pre-merge-commit`.
  - **Accepted:** a valid initial record, and a valid staged append even when the worktree differs from the
    index.
- **Effect size:** not applicable. The hook makes edits to the record tamper-evident. bcenv's README admits the
  limits: "Hooks verify append-only bytes, not whether text truly matches the original prompt"; "Local hooks can
  be bypassed"; "Fast-forward merges create no new commit and do not run these checks."

### 2.2 Process patterns the survey found across winners (qualitative)

- **"Central finding":** "The strongest recurring pattern ... is a development process: understand the
  particular game, build a working economy and combat policy, examine failures, and test changes against varied
  opponents. Successful bots frequently combine relatively compact strategic rules with sophisticated
  navigation, communication, and implementation techniques."
- **Separating global computation from local action:** the 2014 winner computed BFS pathfinding at HQ and
  broadcast it, with bug navigation as the fallback while the BFS data was incomplete.
- **Map-wide testing workflows and retained version history:** the 2017/2018 winners.
- **Explicit unit states with remembered return locations:** 2025 winner Just Woke Up, so units can resume
  interrupted tasks. The same account replaced "an expensive spatial structure with cheaper grid-based
  bookkeeping".
- **Doing fewer unproductive actions:** 2025 runner-up confused: "A bot can become stronger by doing fewer
  unproductive actions rather than by adding a more elaborate planner."
- **Generated Java through templates** to meet runtime limits: 2025 Om Nom.
- **Better testing infrastructure:** 3MiceWalkIntoABar (2026) "reports that better testing raised benchmark win
  rate from below 50% to around 70%, and describes hundreds of games within minutes" using the distributed
  runner Nudge. bcenv qualifies this as "self-reported workflow results with a particular comparison set".

### 2.3 What worked in the anicolao/battlecode-2026 campaign (the predecessor bcenv was built from)

- `DEVELOPMENT_LOOP.md` prescribes: analysis, one testable change, local regression checks, remote scrimmages,
  then retain or revert.
- **Iteration 0034 / PR #32:** "Reports a three-map win against `betterexamplefuncsplayer` after making units
  converge to defend the king." bcenv's qualifier: "Evidence of a claimed targeted improvement, not general
  tournament strength."
- **`build.gradle`:** "places tools in a separate source set and packages the main sources", which bcenv calls
  "a useful existing solution to the packaging concern".
- **`InspectReplay.java`:** "detects A–B–A movement, reads native replay structures, and reports selected
  actions." An A–B–A oscillation detector is a cheap and useful replay diagnostic.

### 2.4 What worked in Terry Van Belle's projects (as bcenv summarizes them)

- **External benchmarks exposed a blind spot.** In the 2026 project, the `g_iter14` baseline was "**20/20** wins
  against the lecture player and **20/20** against the imported anicolao bot, but **0/20** against each of three
  stronger external entries". As a measurement method this worked: it found a structural gap that self-play
  could not.
- **The objective revision of September 10, 2026 (2025 project)** changed the goal from beating the other live
  lineages to "absolute performance against a frozen roster with external validation". The supporting numbers:

  | Date | Lineage | vs `v3` | vs `TSPAARKHS` |
  | --- | --- | --- | --- |
  | Sept 10 | Alice | 26/150 | 2/150 |
  | Sept 10 | Carol | 37/150 | 0/150 |
  | Sept 11 | Darla | 63/150 | 0/150 |

  These are the repository-reported measurements bcenv quotes.
- **2022 replay tool:** renders a native replay as an ASCII board plus an event transcript, with selectable
  rounds, movement, indicators and CSV metrics. Its tests build a synthetic replay. bcenv calls this "a stronger
  starting point for an agent-readable replay interface than an unstructured game log alone."
- **`tournament.sh` (2025):** "copies its own script before execution to avoid edits corrupting an in-flight
  shell run".
- **`compare_gauntlets.py` (2026):** joins games by opponent, map and player side, and reports outcome flips and
  round changes.

### 2.5 Downstream adoption (cross-reference)

- bc21's `TRAINING_ALGORITHM.md` was "Written fresh ... after reading the 2022, 2026 and 2025 predecessors and
  `anicolao/bcenv`; it keeps what those runs proved out (roughly 900 logged iterations between them)".
- bc20's training log lists "anicolao/bcenv (README, VISION, AGENTS, PROMPTS, INITIAL_DESIGN_SKETCH,
  HISTORICAL_LEARNINGS minus its 2020 section)" as read before any code.
- The 2023 owner prompt (`2023/PROMPTS.md`, prompt 1) also requires reviewing bcenv.

bcenv's ideas are therefore already part of the family's method. Their benefit has never been measured in
isolation.

---

## 3. What did not work and closed directions

Each item gives the evidence as written and why it failed.

1. **Genetic parameter optimization (Greg Little, 2008).** "Even with a 16-core machine, only a few generations
   were practical, and new strategic ideas lay outside the parameter space being optimized." Why it failed:
   tuning a fixed strategy "cannot discover an idea the representation excludes".
2. **AI-assisted parameter tuner (Lorem Ipsum, 2026).** "too slow and did not produce useful improvements". The
   team "still relied on targeted scenarios, broader matches, and scrimmages." Combined with item 1, that is two
   independent failures of automated parameter tuning.
3. **anicolao 2026, iteration 1.** "a local win against the basic example bot, losses in five remote
   scrimmages, and a navigation change that regressed locally and was reverted." The local result did not
   predict scrimmages.
4. **anicolao 2026, iterations 25–83.** "repeated attempts to address starvation, traffic around the king,
   delivery priorities, and mining." The record is a single retrospective that "explicitly substitutes a
   retrospective for missing individual records". It also contradicts itself: it says iterations 25–83 lacked
   documents, yet some numbered files in that range exist. Why it failed: the economy and traffic problems
   recurred across dozens of iterations, and the missing records make it impossible to tell which attempts did
   what.
5. **anicolao 2026, PR #31 (spawning).** "the account attributes spawning failures to confusion between carried
   and global cheese and to an incorrect spawn distance." Cause: the rules or API were misread, which "can look
   like strategic weakness". A human recommended regression bisection.
6. **anicolao 2026, PR #33 (workspaces and packaging).** "Human feedback identifies two workspaces and warns
   against including analysis tools in the submission source." Cause: work split across two checkouts, and the
   submission was contaminated with tooling.
7. **The anicolao bot as an external opponent (cross-reference, bc26 `TRAINING_LOG.md`).** bc26 imported it as
   `bench_anicolao`.
   - Smoke test: "vs bench_anicolao WIN (r131)".
   - Baseline: "vs bench_anicolao 20/20 (100%) earlier LLM-vibe-coded bot".
   - Replay: it "uses zero traps/ratnaps/throws" and "its `cheeseTransferred` stayed at **0** for the whole game
     while its King starved out at round 131".

   This is independent confirmation that the starvation and delivery failure bcenv describes (item 4) was still
   present in the bot's final state.
8. **anicolao 2026 tooling contracts.** bcenv calls these "a producer/consumer contract mismatch":
   - `analyze_matches.py` expects `Match Ended - Winner ID:`, but the Java tool prints `Match Winner:`. The winner
     is initialized to `?`, and anything other than `1` maps to `NO`, so the winner field can never be filled.
   - A required lookup of `KingBDied` "can raise `KeyError` rather than produce a report".
   - Replay IDs below a hard-coded threshold are silently excluded.
   - Team A's result is treated as "our win" without resolving which slot was ours.
   - bcenv adds: "it does **not** establish that earlier reported scrimmage wins were false".
9. **anicolao 2026 submission scripts.**
   - `upload_submission.py` does not bind the ZIP to a source snapshot or wait for compilation, and its command
     line "does not turn a returned upload failure into a failing exit status".
   - `check_submission.py` "returns the same false result for rejection and timeout".
   - `review_scrimmages.py` "fetches only the first history page and marks completed results as reviewed
     independently of replay-download success".
10. **Terry 2022: a long loop that did not close the external gap.** It ran 128 iterations. "a persistent
    **0/20** result against `sample_camelcase` and approximately **3/20** against `sample_afinals`." Also
    "features that could not help because prerequisite units were almost never produced." Why it failed: "a
    long sequence of locally useful changes did not close the independent-opponent gap."
11. **Terry 2026: self-play bubble.** 0/20 against each of three stronger external bots. The explanation
    "emphasizes traps, ratnapping, and throwing missing from its earlier opponent pool". bcenv: "A pool can
    contain many old versions and several named archetypes while still omit the behaviors needed to expose a
    strategic weakness."
12. **Terry 2025: optimizing against live rivals.** "optimizing the gap between the live lineages had produced
    co-adaptation without sufficient external strength". The fix was the objective revision in section 2.4.
13. **muskellunge (2024).** "increased healing or feature complexity did not reliably improve results. Testing
    against older versions of oneself missed problems that outside opponents exposed."
14. **Planning before playing (Stuart Johnson, 2017).** "substantial architecture work preceded a viable
    economy, and the competitive meta changed while planned features were being built." Lesson: "keep a playable
    reference bot and shorten the interval between an idea and a real game."
15. **Double J (2019).** A feature was "implemented in the wrong file and absent from the submission."
16. **Early ladder strength did not last.** Oak's Last Disciple (2019): "An initially strong rush-oriented
    approach encountered a shifting game balance and later tournament disappointment."
17. **Closed as sources of evidence.**
    - CodeClash: Battlecode "is not one of" its six main arenas and appears only in Appendix B.1. It reports
      "poorly grounded fixes and accumulating code complexity" as agent failure patterns.
    - Metta AI's cogame-battlecode: a Nim port with a "sealed doctrine" interface, not the official engine.
    - ECLAIR's battlecode-gym: "not evidence of a faithful MIT season adapter."
    - Neither the names nor the repositories of these projects are evidence of Battlecode skill.
18. **bcenv itself (inference).** After 10 owner prompts the project has produced research and design only, and
    its last prompt widened the scope to nested VMs and an outer supervisor LLM. bcenv's own README says "Early
    contributions should help establish the smallest complete workflow: an agent builds a baseline bot, runs a
    match, reads the result, and makes a measurable improvement." That workflow does not exist yet. The bc24
    review agrees: "Take the schemas and checklists ..., not the topology."

---

## 4. Method lessons

### 4.1 Training loop (from `INITIAL_DESIGN_SKETCH.md`, "Agent tools and the iteration loop")

- **The loop:** "hypothesis, candidate, experiment, diagnosis, and decision."
- **Record before comparing:** "Record the agent's stated hypothesis and expected observation before a
  comparison when possible."
- **Manipulation check:** "Attach a manipulation check: whether, where, and how often the changed behavior
  actually ran." This separates three cases: "an inactive feature, an active feature without benefit, and a
  beneficial mechanism whose full candidate regressed." In my view this is the highest-value single method rule
  in bcenv. Terry 2022's "features that could not help because prerequisite units were almost never produced" is
  exactly the inactive-feature case.
- **Engine probe and API audit:** "Add a small engine-probe capability and explicit reminders to audit unused
  APIs when an integration is established or development stalls. These should generate evidence about legal
  actions and costs, not merely another model-written rules digest." Terry 2026's never-tried `throwRat` is the
  cautionary case. 2023 has its own non-obvious actions: carriers throwing cargo, anchors, amplifiers,
  destabilizers and boosters.
- **Tool errors must name their cause:** "invalid request, invalid candidate, infrastructure failure, or
  unavailable capability."
- **Separate failure types:** "distinguish 'the strategy loses to an early rush' from 'the bot spent its turn
  budget before moving' and 'the runner failed to produce a result.'"

### 4.2 Gating and statistics ("Evaluation that supports decisions")

- **Freeze the experiment manifest:** candidates, opponents (with provenance and a fixed or maintained flag),
  maps, player slots, seeds, repetitions, environment identity, budgets and the intended comparison.
- **Paired player-slot comparisons.** "Repeating an identical deterministic match can check infrastructure
  consistency, but does not create independent evidence of playing strength."
- **Three uses of matches:** diagnostic cases, development suites and held-out evaluation. "Once a holdout
  repeatedly guides changes, relabel it as development evidence."
- **Uncertainty "at the level of meaningful independent blocks—often maps or map/opponent groups—rather than
  treating correlated repetitions as independent trials."** A clustered bootstrap is "one candidate method to
  validate".
- **Declare promotion criteria before looking:** "required correctness, tolerated regressions, minimum relevant
  gain, and any resource ceiling. 'Inconclusive' is a valid result. Avoid a fixed win-rate threshold that ignores
  opponent strength or sample size."
- **Account for every job:** game outcome (win, loss, tie, with tie-break reason) is separate from job state
  (queued, running, completed, failed, cancelled, unknown). "Never silently skip short logs or failed matches.
  Reports show scheduled, completed, excluded, retried, and unresolved counts, with an explicit scoring
  denominator." "Retries create linked attempts rather than replacing inconvenient results."
- **Breakdowns and metrics:** report results by map, opponent and player slot. "Longer survival is a diagnostic,
  not an interchangeable substitute for winning" (on `compare_gauntlets.py`). An intersection-only comparison
  should "also report unmatched jobs".

### 4.3 Ladder, Elo and opponent pool

bcenv has no Elo or rating design. On opponents it says:

- "Measure how much strategic behavior the pool actually covers, since many related opponents can share the same
  omissions."
- "Preserve simple baselines and several strategic styles, not only the latest best candidate."
- Matchups are nontransitive (SPAARK 2025): "beating a bot that beats another bot is not a guarantee of beating
  the latter."
- "A scheduled tournament measures the participating lineages. It does not establish absolute strength."
- "A comparison target that evolves with the agent must not silently replace the competition objective."

### 4.4 Process rules

- **Verbatim prompt record** (AGENTS.md):
  - append-only;
  - a 3–6 word summary heading is optional and never replaces the text;
  - "If one prompt leads to multiple commits, append another entry with that exact prompt and explain the
    repetition";
  - use a longer fence if a prompt contains code fences;
  - never bypass the hooks.
- **Immutable candidates:** "A candidate is an immutable snapshot, not a branch name or a moving workspace
  directory." Its identity changes when any input that affects execution changes.
- **Workspace registration:** bind every tool operation to a registered workspace ID and absolute root. This is
  motivated by the two-workspace correction in PR #33.
- **Package through an allowlist**, and keep tools in a separate source set.
- **Freeze the runner as well as the bot:** "an in-flight experiment must not change when someone edits a shared
  script. Resolve a single revision once and use it for all exports, rather than repeatedly consult a moving
  `HEAD`."
- **Two identities:** an agent configuration (model, instructions, memory policy, tools) is a separate identity
  from the candidate bot.
- **Hypothesis register:** "claim, scope, evidence, decision, unresolved uncertainty, and the observation that
  would justify reopening it." A change in objective or architecture "must trigger review of old conclusions".
- **Records as work occurs:** "retrospective prose cannot substitute for records written as work occurs." The
  motivating case is the 25–83 summary.
- **Long-running operation:** "A usage-limited or unavailable model cannot be responsible for its own sole
  recovery path: use an external supervisor, heartbeat, single-coordinator lease, and explicit resume state.
  Test interruption after dispatch and before acknowledgment."
- **Measure autonomy separately from strength:** record human strategic advice, manual fixes, model
  configuration, elapsed time and compute.

### 4.5 Owner interventions recorded in bcenv's `PROMPTS.md`

| Prompt | What the owner did | What it corrected (inference marked) |
| --- | --- | --- |
| 3 | "The VISION shoudl not stray into roadmap or immediate priorities. It is a VISION statement only." | The agent had mixed roadmap content into the vision document. |
| 4 | Allowed optional 3–6 word summary headings. | Readability of the record; no correction. |
| 6 | The hook forced prompt 5 to be re-appended for a second commit. | Process friction caused by the "every commit must append" rule. |
| 8 | "review all of my repositories for battlecode related work and any repositories tehy refer to" | The first survey (prompt 7) had not used the owner's own work. |
| 9 | "did my repositories lead you to also look at Terry Van Belle's efforts in this area? If not, do so now." | The agent had missed them. HISTORICAL_LEARNINGS confirms the gap: the link was "an **incoming reference from Terry's repository**", which "the earlier account-wide outgoing-reference screen did not capture." |
| 10 | Asked for containerization "near the top of the design sketch": a NixOS VM image for GCE, with an inner LLM developing and an outer LLM provisioning and supervising. | The agent had not proposed an isolation and deployment architecture. The owner supplied it, and the sketch was rewritten around it (the sole commit's message: "Center the design on supervised NixOS competitor environments"). |

Interventions in the anicolao/battlecode-2026 campaign, per bcenv:

- **PR #30:** a human asked for dependable submission, status checking, opponent selection, replay download and
  analysis, and "explicitly distinguishes successful upload from accepted compilation".
- **PR #31:** "Human instructions recommend regression bisection".
- **PR #33:** a human identified the two workspaces and the tool contamination.

bcenv's conclusion is that the "Human diagnosis also prevents classifying this record as an independently
completed campaign."

### 4.6 How the agents went wrong (pattern summary)

- **Plausible but unchecked feedback:** "The lesson is that **the feedback system is itself experimental
  software**. A plausible report is not enough."
- **Documentation and code drift apart:** the 2026 tools README "still says there is no test suite" while tests
  exist.
- **Retrospectives standing in for records.**
- **Rules misread** (carried versus global resource).
- **Workspace confusion and packaging contamination.**
- **A self-play bubble and co-adaptation.**
- **Research that follows only outgoing links** (bcenv's own miss of Terry's projects).

---

## 5. Bot architecture and the basics

bcenv contains **no bot code**. Its survey names techniques but gives no file paths or function names inside any
bot. Below are those techniques, grouped by basic, each mapped onto 2023. Statements about 2023 are marked
**[engine-verified]** when I checked them in the 2023 engine source or the 3.0.15 jar; everything else is
inference.

### 5.1 Economy

- **Sources:**
  - Java Best Waifu 2020: "economy and defense supported the eventual attack rather than existing as independent
    subsystems."
  - confused 2025: "fewer unproductive actions".
  - anicolao 2026: starvation, delivery priorities, mining; `cheeseTransferred` stayed at 0 and the King starved
    at round 131 (bc26 cross-reference).
  - PR #31: "confusion between carried and global cheese".
- **2023 mapping:**
  - **[engine-verified]** In 2023 every robot, each HQ included, has its own inventory.
    `RobotControllerImpl.getResourceAmount(rType)` returns `this.robot.getResource(rType)`, and `buildRobot`
    debits `this.robot.addResourceAmount(rType, -1*type.getBuildCost(rType))`.
    - So resources are **per HQ**, not team-wide. A carrier must deliver to the HQ that will spend the
      resources.
    - A carrier's `getResourceAmount` is its own cargo.
    - This is the same carried-versus-global trap as PR #31.
  - **Inference: add a basics metric**, delivered Ad/Mn per HQ per 100 rounds, broken down per carrier. A zero is
    the 2023 version of `cheeseTransferred = 0`.
  - The load-dependent carrier move cooldown, floor(5+3m/8), makes "fewer unproductive actions" concrete: avoid
    trips with partial loads and long walks to far wells.

### 5.2 Navigation and pathing

- **Sources:**
  - 2014 winner: BFS at HQ, broadcast to units, with bug navigation as the fallback.
  - confused 2025: "local navigation backed by bug navigation".
  - Om Nom 2025: "bit-oriented pathfinding".
  - Generalized Stroke's Theorem 2026: "difficulty validating navigation changes near the deadline".
  - anicolao 2026: "traffic around the king", and A–B–A oscillation detection in `InspectReplay.java`.
- **2023 mapping (inference):**
  - HQ-computed BFS broadcast does **not** carry over. The shared array is 64 × 16 bits = 1,024 bits, against up
    to 3,600 cells on a 60x60 map, and writes are allowed only within r^2 9 of an own HQ, r^2 20 of an own
    amplifier, or r^2 4 of an own anchored island.
  - Use per-unit bug navigation, with bit-parallel local BFS in the spirit of "bit-oriented pathfinding" if
    bytecode allows. Currents (end-of-turn pushes) and clouds (20% cooldown penalty) are the 2023-specific nav
    hazards.
  - **Port the A–B–A oscillation detector** to the .bc23 replay tool as a navigation regression metric.
  - Traffic near the HQ is the 2023 version of "traffic around the king": carriers queue to deliver, and HQ
    spawns need free adjacent tiles.

### 5.3 Exploration

- **Sources:** confused 2025 used "scored exploration". 3 Musketeers and M.A.R.S. (2021) combined scouting with
  HQ-mediated coordination.
- **2023 mapping (inference):** score frontier tiles by unseen area plus well and island discoveries. Units must
  physically return near an HQ or amplifier to report findings, so exploration value includes the trip home.

### 5.4 Symmetry

- **Source:** bcenv says only that Terry 2022 had "symmetry-sensitive decisions".
- **2023 mapping (inference):** 2023 maps are symmetric by rotation or reflection. Use the standard approach:
  maintain the three candidate symmetries, eliminate them with observed walls, wells and islands, and store the
  surviving set in a few bits of the shared array.

### 5.5 Combat and micro

- **Sources:**
  - Cout for Clout 2024: "micro that compares candidate moves by priorities".
  - Generalized Stroke's Theorem 2026: "A generic nine-move micro interface would have been too narrow for this
    season".
  - The High Ground 2020 and confused 2020: defense that holds against trickling attackers "may fail against
    coordination".
  - Malott Fat Cats 2021: flanking toward the enemy economy.
- **2023 mapping (inference):**
  - Launchers suit nine-move candidate scoring. Launcher attack is r^2 16 against vision r^2 20, the move
    cooldown is 20, and HQs deal 4 damage per round within r^2 9.
  - Carriers' cargo-throw attack and destabilizer area effects fall outside a nine-move interface, so design the
    micro interface to allow special actions.
  - Concentrated launcher groups beat trickles, and an attack on enemy carriers is an attack on the enemy
    economy.

### 5.6 Communication

- **Sources:**
  - smite 2019: grouped resources "into clusters, allowing compact cluster identifiers".
  - Ivy Zhang 2021: "Compressed information into flags".
  - wololo 2021: "distributed Bellman–Ford-style information propagation".
  - M.A.R.S. 2021: "headquarters-mediated coordination".
- **2023 mapping (inference):**
  - Compress well and island locations into compact IDs. 12 bits covers a (x,y) on 60x60 (6+6), which leaves 4
    bits for type or status in a 16-bit slot.
  - Because writing is local (HQ, amplifier or island radius), "HQ-mediated coordination" fits naturally.
    Amplifiers act as relays that extend the write area.

### 5.7 Architecture patterns

- **Explicit states with remembered return locations** (Just Woke Up 2025). Carriers that are interrupted by a
  threat and later resume the trip to their well or HQ.
- **Goals with start, execution and stop conditions** (The Kragle 2025).
- **Separate state updates from behavior selection** (Generalized Stroke's Theorem 2026).
- bcenv explicitly does not prescribe one: "State machines, goal systems, tactical search, and generated code
  are all reasonable experiments."

### 5.8 Bytecode

- **Sources:**
  - Just Woke Up 2025: grid bookkeeping replaced an expensive spatial structure.
  - Om Nom 2025: generated Java through templates "to meet runtime constraints".
  - Generalized Stroke's Theorem 2026: "bytecode pressure".
  - From the design: "record whether instrumentation changes execution cost"; "A final validation run should use
    the actual submission configuration".
- **2023 mapping:** the limits are HQ 20,000, carrier 12,500, others 10,000. Measure per-type bytecode and count
  overruns. Generate unrolled loops for vision-radius scans. **[engine-verified]** Vision is r^2 20 for carriers,
  launchers, destabilizers and boosters, and r^2 34 for HQs and amplifiers (`RobotType.java`), so the vision sets
  are small enough to unroll. Remember that debug indicators cost bytecode.

---

## 6. Tools and infrastructure inventory

### 6.1 Code inside bcenv

| Path | Purpose | Quality | 2023 verdict | What must change |
| --- | --- | --- | --- | --- |
| `bcenv/scripts/check-prompts.mjs` (35 lines) | Pre-commit check: the staged file must start with HEAD's bytes, and the tail must be non-whitespace | Small, careful: index-authoritative, unborn-HEAD aware, mode check | **Adapt** | (1) Take a list of files so it also guards `TRAINING_LOG.md`, which 2023's CLAUDE.md calls append-only. (2) Drop or relax the "must add non-whitespace" rule: 2023 commits often carry no new owner prompt, and 2023's PROMPTS.md deliberately omits `/loop`-fired prompts. Keep the byte-prefix check, which is the tamper-evidence. (3) Node v20.20.2 is installed, so it runs as-is. |
| `bcenv/scripts/check-prompts.test.mjs` (70 lines) | Hermetic hook test in a temporary repo | Good pattern: scrubbed `GIT_*`, redirected `XDG_CONFIG_HOME`, `commit.gpgsign=false` | **Adapt** | Remove the husky install step (`node_modules/husky/bin.js`). Point at a plain hook and change the acceptance cases to the relaxed rule. Wire into `tools/unit-tests.sh`. |
| `bcenv/.husky/pre-commit`, `.husky/pre-merge-commit` | Run the check on commit and merge-commit | Trivial | **Skip husky** | Install with `git config core.hooksPath` or a plain `.git/hooks/pre-commit`. `npm ci` would need the network, and husky adds nothing here. |
| `bcenv/package.json`, `package-lock.json` | husky 9.1.7 devDependency, npm scripts | Fine | **Skip** | Not needed without husky. |
| `bcenv/AGENTS.md` | Agent rules for the prompt record | Clear | **Adapt (mostly done)** | 2023's CLAUDE.md rule 2 already records prompts. Add only "use a longer fence if a prompt contains code fences" and "never edit existing bytes". |

**Inference:** a 10-line shell version is enough for 2023:

```sh
git show HEAD:F > old
git show :F | head -c $(wc -c < old) | cmp -s - old
```

Run it per guarded file `F`.

### 6.2 Design artifacts inside bcenv (no code, but directly usable as checklists)

| Section of `INITIAL_DESIGN_SKETCH.md` | Use for 2023 | Verdict |
| --- | --- | --- |
| "Season integrations" table (Identity, Rules, Toolchain, Game execution, Evidence, Submission) | A one-page `ENVIRONMENT` manifest: engine 3.0.15 jar checksum, Java 8 toolchain, map list with hashes, seed control, the replay schema version, and the terminal-outcome mapping (the 8 `DominationFactor` reasons) | **Adapt as checklist** |
| "Freeze the experiment before running it" | The fields a gauntlet run records | **Adapt** |
| "Account for every job" | Acceptance checklist for `gauntlet.sh`, `summarize.py` and `elolib.py` | **Adapt** |
| "Compare with appropriate uncertainty" | Clustered (by map) bootstrap or paired tests in `statlib.py`/`sprt.py`; pre-declared promotion criteria | **Adapt** |
| Agent operations table (`inspect_season`, `create_candidate`, `build`, `run_matches`, `inspect_match`, `compare`, `select_candidate`, `package`, `submit`) | A vocabulary for the 2023 tool surface; every long operation returns a durable ID | **Adapt as naming and contract guide** |
| "How to evaluate bcenv itself": required checks "for valid and invalid bots, every terminal outcome including ties, truncated output, timeouts, cancellation, interrupted jobs, replay parsing, and package identity" | A test list for 2023's `tools/test_tools.py` | **Steal as a test list** |
| VM topology (supervisor VM, competitor NixOS VMs, GCE images, campaign journal, content-addressed store, SQLite index) | Too heavy for a single-season practice project. 2023 already uses a driver host plus the `battlecode-dev` VM. | **Skip** |

### 6.3 Tools that bcenv cites but does not contain

| Tool (as cited) | Local availability | Verdict |
| --- | --- | --- |
| anicolao/battlecode-2026: `scripts/analyze_matches.py`, `tools_src/tools/InspectReplay.java`, `upload_submission.py`, `check_submission.py`, `review_scrimmages.py`, `build.gradle` | Not local (private). bcenv's description only. | **Skip the code.** Use their defects as regression fixtures (section 7). Borrow the A–B–A oscillation idea and the separate tools source set. |
| Terry 2022 replay tool | `reference/battlecode22-vibe/tools/bc22_replay.py`, `test_bc22_replay.py` | See `2023/research/prior/bc22.md` (verdict there: adapt; rebuild for the .bc23 schema) |
| Terry 2026 `ReplayDump.java`, `test_replaydump.py`, `compare_gauntlets.py` | `reference/battlecode26-vibe/tools/` | See `bc26.md` and `bc22.md` (`compare_gauntlets.py`: steal if the results.csv schema is kept) |
| Terry 2025 `bot_identity.py`, `tournament.sh`, `agent-watchdog.sh` | Not in the local reference tree. Documents are in `readroom-no2023/bc25/`. | See `bc25-docs.md` (`bot_identity.py`: steal; watchdog: adapt for long unattended sessions) |
| Nudge distributed runner; CodeClash arena adapters | External, not local; no network | **Skip** |

### 6.4 Where 2023 already meets bcenv's bar, and one small gap

- **Already met.** `tools/lib.sh` `parse_result` parses `(A|B) wins (round N)` and `Reason:`, and returns
  `RESULT ? ? ?` on garbage. The test is `test_garbage`, so missing data is represented as missing rather than as
  a default. `gauntlet.sh` records `bot_side` and `winner_side` separately, which avoids the "Team A is us"
  assumption. `summarize.py` reports "unknown/dud counts, end reasons".
- **Small gap [engine-verified].** `tools/test_tools.py` `test_b_wins_early` uses the reason text "The winning
  team won by anchoring sky islands." The 3.0.15 jar never prints that string. Its eight reasons are:
  - "The winning team won by capturing 75% of sky islands."
  - "... by having more sky islands."
  - "... on tiebreakers (more reality anchors)."
  - "... on tiebreakers (more elixir net worth)."
  - "... on tiebreakers (more mana net worth)."
  - "... on tiebreakers (more adamantium net worth)."
  - "... arbitrarily (coin flip)."
  - "Other team has resigned. Congrats on scaring them I guess..."

  The engine also prints `nobody wins (round N)` when there is no winner, which `parse_result` would map to `?`.
  Today the reason is only recorded and counted, so nothing breaks. If any tool later classifies wins by reason
  (conquest versus tiebreak), it should be tested against the real eight strings. This is exactly bcenv's "test
  producer and consumer together" lesson. Inference: add one fixture per real reason plus the `nobody` case.

---

## 7. Pitfalls and gotchas that cost time

Costs are given where bcenv states them. Most entries have no stated cost.

1. **Winner-label mismatch between producer and consumer** (anicolao `analyze_matches.py` against the Java tool).
   The winner field could not be filled, defaulted to `?`, and became `NO`. Cost not stated. bcenv: "it does
   **not** establish that earlier reported scrimmage wins were false".
2. **Unconditional lookup of a metric that may be absent** (`KingBDied`): `KeyError` instead of a report.
3. **Assuming Team A is us:** misclassified outcomes. (2023's `gauntlet.sh` already avoids this.)
4. **Hard-coded exclusion thresholds** (replay IDs below N silently dropped). "Those assumptions must be explicit
   experimental filters."
5. **Upload accepted is not the same as compiled**; rejection and timeout returned the same `False`; scrimmage
   history read only from page 1; "reviewed" set even when the replay download failed. Practice-only for 2023,
   since there is no submission, but the same separation applies to the local galaxy replica.
6. **Two workspaces.** Work was split across two checkouts and a human had to correct it (PR #33).
7. **Analysis tools inside the submission.** Use a separate source set and an allowlist.
8. **A feature placed in the wrong file never reached the submission** (Double J 2019).
9. **Rules or API misread looking like weak strategy:** carried versus global cheese, and the wrong spawn
   distance. In 2023 this becomes per-HQ inventories (section 5.1).
10. **Retrospective summaries instead of records:** iterations 25–83 left an "incomplete, overlapping narrative".
11. **Documentation and code out of sync:** a tools README claimed there were no tests when tests existed.
12. **Self-play bubble:**
    - 2022: 128 iterations, still 0/20 and about 3/20 against the samples.
    - 2026: 0/20 against three external bots. bc26's own log says "95-100% against old snapshots was real
      progress *inside a bubble*".
13. **Co-adaptation between live lineages** (2025). The objective had to be revised.
14. **Editing a running shell script corrupts the run.** The fix is to copy the script before executing it
    (`tournament.sh`).
15. **Resolving a moving `HEAD` repeatedly during an export.** Resolve one revision once.
16. **The coordinator stalls on a model usage limit.** Recovery must not depend on the model. Terry 2025
    retired a lineage (Bob) "to fit resource limits".
17. **Boundary turns.** Ivy Zhang 2021 reported "a turn-equality bug and voting-related failure"; "Boundary turns
    and victory conditions deserve explicit regression cases." For 2023 (inference): round 2000 tiebreaks, and
    the moment an island reaches 75% anchored.
18. **Within-season engine changes.** The 2024 specs carry "a substantial changelog". "Do not run an automatic
    engine update during a measured comparison." 2023 is pinned to 3.0.15.
19. **Privileged replay information leaking into policy design:** "Label the difference between a bot's in-game
    observation and privileged full-replay information".
20. **Instrumentation cost:** indicators and counters cost bytecode. The final validation must use the
    submission configuration.
21. **Hook friction.** The "every commit must append" rule forced a duplicate prompt entry (prompt 6). Hooks are
    local and bypassable, and fast-forward merges skip them.
22. **Search effort.** Greg Little's genetic optimization got "only a few generations" on 16 cores. The Lorem
    Ipsum tuner was "too slow". Parameter search is an expensive way to find nothing new.

---

## 8. Top 15 takeaways for the 2023 project, ranked by expected value

1. **Benchmark against independent external bots from the start, and never treat self-play numbers as
   strength.** Evidence: Terry 2026 g_iter14 was 20/20, 20/20, then 0/20 ×3; Terry 2022 sat at 0/20 and about
   3/20 after 128 iterations. Self-play hides missing mechanics. For 2023, the mechanics at risk include carrier
   cargo throws, anchors, amplifier relays and elixir units.
2. **Attach a manipulation check to every change:** did it run, where, and how often. Use counters in indicator
   strings or replay tags. This separates "inactive", "active without benefit" and "beneficial but the full
   candidate regressed", and it would have caught Terry 2022's features that never fired.
3. **Treat the evaluation pipeline as software under test.** Test the producer (engine output, `.bc23` replay)
   and consumer (`parse_result`, `summarize.py`, replay-dump) together. Represent missing data as missing. Add
   fixtures for all eight real 3.0.15 reason strings and `nobody wins`, and replace the synthetic "won by
   anchoring sky islands" fixture.
4. **Verify engine facts by probing, before building strategy on them.** Rules misreadings look like strategic
   weakness (PR #31). The 2023 example is per-HQ inventories **[engine-verified]**: carriers must deliver to the
   HQ that builds.
5. **Instrument economic throughput as a basics gate:** delivered Ad/Mn per HQ per 100 rounds and per carrier. A
   zero is the 2023 form of anicolao's `cheeseTransferred = 0` King starvation, which bc26 saw at round 131.
6. **Account for every job and compare in pairs:** separate outcome from job state, use an explicit denominator,
   link retries, never drop crashes, swap sides, and put uncertainty at the map (block) level rather than the
   game level.
7. **Declare promotion criteria before running,** allow "inconclusive", and avoid a fixed win-rate threshold that
   ignores opponent strength.
8. **Keep three tiers of matches:** small diagnostic scenarios for debugging, a broad development suite, and a
   protected holdout. Relabel the holdout once it starts steering changes.
9. **Make the objective absolute strength against a frozen roster,** never the gap to a co-evolving internal
   rival (Terry 2025: Alice, Carol and Darla at 0–2/150 against `TSPAARKHS`).
10. **Prefer code edits over parameter tuning for strategy.** Two independent tuners failed (2008 GA, 2026 Lorem
    Ipsum). Keep restricted tuning for small, stable subsystems only.
11. **Freeze what you measure:** one resolved revision per run, the runner script copied before execution,
    content-hashed bot identity, packaging by allowlist, and tools kept out of the bot source set.
12. **Write a hypothesis register as you go:** claim, scope, evidence, decision, and the condition for reopening
    it. A retrospective written afterwards cannot rebuild what was lost (the 25–83 summary).
13. **Design communication around 2023's write locality.** 1,024 bits, written only near an HQ, amplifier or
    anchored island, rules out broadcast navigation fields. Compress wells and islands into 12-bit
    coordinates with status bits, coordinate through the HQ, and use amplifiers as relays.
14. **Use explicit unit states with remembered return locations** (Just Woke Up). For carriers interrupted by
    launchers or currents, resuming well/HQ trips cleanly is worth more than a richer planner. Add an A–B–A
    oscillation detector to the replay tool to catch navigation regressions.
15. **Guard `PROMPTS.md` and `TRAINING_LOG.md` with an append-only pre-commit check:** the byte-prefix half of
    `check-prompts.mjs`, without the "must append" half. It costs about 10 lines, runs on the installed Node v20
    or plain shell, and makes the owner-prompt record tamper-evident. Do not adopt husky, and do not adopt the
    NixOS/GCE supervisor topology.
