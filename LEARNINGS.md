# LEARNINGS

What training a Battlecode 2023 bot teaches (battlecode23-vibe, from 2026-10-07), kept as a living document and
finished at shutdown. Readers: the owner, and the agent that runs the next practice year or the real tournament.

How to read it. Each lesson is one or two sentences, then its evidence and a reference. "PROMPTS n" is an entry in
PROMPTS.md; TRAINING_LOG entries are cited by date (PDT). Lessons are year-agnostic unless marked **[2023]** (facts of
this game: a filter that replays 2023 drops them, every other year may use them). Times are PDT.

## 1. Cross-year principles (owner, PROMPTS 49)

From the blind-fire investigation: the teams that beat us have 43-70% zero-damage launcher shots, while several teams
we beat and our own bot have none (historical census `blind_rate`, panel
`gauntlet/20261011-080046-panel-c_mend2`; TRAINING_LOG 2026-10-11 07:25). Correction, 2026-10-12: that metric is a
miss fraction, not visibility. It motivates the investigation but does not establish how many shots were aimed
outside vision. Re-extract the panels with the shot visibility classifier before making that quantitative claim.

1. **Look for actions that cost nothing, and give them something to do at all times, even at low odds.** An unused
   cooldown is lost for good; a small chance of damage on every idle turn is free value. Audit every per-turn action
   (attack, build, write, sense) for the turns it sits idle. **[2023]** A launcher's attack needs no vision (RULES 5.2)
   and a cloud cuts vision to r2 4 (RULES 6.1), so an idle launcher can shoot cloud tiles that may hide an enemy.
2. **Look for patterns in enemy combat actions that capture what they do and we don't, beyond raw counts.** Classify
   each action by its context (what the actor could see, where it aimed, terrain, timing, target) and compare the
   distributions: the teams that beat us, the teams we beat, us. Shot and damage totals alone cannot distinguish
   missed visible attacks from attacks outside vision.
3. **In a live contest, lurk on the contest's discussion channels (e.g. Discord) for ideas.** Strategies are discussed
   while the contest runs. In a practice replay of a past year this is excluded: the old discussions are second-hand
   strategy content for that year, like its post-mortems (CLAUDE.md rule 4).

## 2. How ideas migrate from practice year to practice year to the tournament (owner, PROMPTS 50)

1. **One file per year carries the transferable ideas: LEARNINGS.md.** The next project's reading room
   (tools/build_readroom.py) copies every .md of the prior repos, filtered of the replayed year's tagged blocks; adding
   this repo to its SRC list is the whole migration step. Write lessons year-neutral, tag game facts with the year so
   the filter drops them only where they would be spoilers, and give each one its evidence and effect size so a later
   reader can weigh it.
2. **Ideas must be pulled, not just stored.** TRAINING_ALGORITHM.md names them as sources in "pick a target" and in the
   plateau protocol, and the diagnosis workflow gets a lens per principle ("free actions", "action patterns"); a
   principle no step reads is lost.
3. **Tools carry ideas better than prose.** A per-shot visibility classifier in the replay dumper, paired panels with
   two reference draws, parked trials, the pre-trial screen, the rating-history chart: each embodies a lesson and
   transfers by porting the code. Keep a list of them with the problem each solved (section 4).
4. **Distil at milestones, not only at shutdown.** When a lesson is confirmed (an accept, a rejected class, a broken
   instrument), move it here the same day, while the evidence is at hand.
5. **The tournament starter kit is the union**: every year's LEARNINGS, TRAINING_ALGORITHM and tools, the diagnosis and
   build workflow scripts, and the live-contest-only principles (discussion channels, scrimmage etiquette) that no
   practice year can exercise.
6. **The owner merges the durable principles into the cross-year guides** (terryvanbelle/battlecode-vibe): a practice
   repo may not read that repo's unfiltered documents (rule 4), so the merge is the owner's.

## 3. Lessons so far

### Measurement

- **Check what a metric measures before naming the mechanism.** A miss fraction called `blind_rate` was mistaken for
  attacks outside vision. Replay endpoints also follow current pushes and do not timestamp movement; preserve unknown
  shot geometries and rate bounds instead of guessing attack positions (TRAINING_LOG 2026-10-12).
- **One reference panel is one draw; judge against two.** A build's panel is a single
  realisation of its bytecode-timing-dependent outcomes on reproducible cells, and a change can re-draw borderline
  cells. Every candidate after c_aura2 lost island-rounds against its panel (-77 to -198) and the flips ran 15 lost to
  10 gained; c_bc1, with
  identical decisions, scored 58 to c_aura2's 62. Judge against the base and the previous build (TRAINING_LOG
  2026-10-10 22:45).
- **A local screen cannot judge a narrow arm.** An arm that acts only past round 1700 (c_end2) or on one map (c_lane1)
  sits at the identity score on the head-to-head; read the cells it can change, or go to the panel (TRAINING_LOG
  2026-10-11 01:45).
- **Measure the mechanism, not only the score.** c_mend2 was accepted on healed HP x2.2 (t +4.8) with a net of +3;
  c_well7's MassiveL mana gain (t +6) came with 11-21 carriers fed on Forest that the score hid (TRAINING_LOG
  2026-10-11 05:14 and 06:05).
- **Measure cost before spare compute is consumed elsewhere; a missing counter is not a zero.** c_bc3's 100-cell
  panel kept all c_mend2 win/loss outcomes, but end-turn launcher maxima (medians 9,175/9,174) include background
  work and cannot establish its method savings. All indicator counter fields were blank; use surviving telemetry
  with coverage checks, and keep the optimization pending until cost delivery is measured (TRAINING_LOG 2026-10-12 13:05).
- **Exercise budget guards with the real instruction meter.** Reflection-set budgets proved logical completed-pass
  equality for CBC3 but missed 58 finite-budget list differences in 192 official instrumented fixtures. Cache hits
  also need reachable warm states and actual call weights; hypothetical unlimited warmups exaggerate savings
  (`research/diagnosis/2026-10-12-c_bc3-cost.md`, TRAINING_LOG 2026-10-12 14:20).
- **Simulation identity includes every observable input, not just starting positions.** [2023] `rc.getTeam()` exposes
  A/B labels: galaxy-3357/2 and galaxy-4694/3 give NolanChai the same physical spawns and named win, yet end at
  r1631/r1421 with opposite labels. Keep both raw rows and labelled pair/orientation keys; retain the strict invariant
  for exact labelled repeats (TRAINING_LOG 2026-10-12 13:05).

- **A loop guard is not a return reserve.** Mend3's official method fixtures admit an iteration above6,000 and
  return as low as5,912 after the iteration/epilogue. Measure the maximum admitted work and the rest of the turn
  before claiming guaranteed headroom (`research/diagnosis/2026-10-12-c_mend3-cost.md`).
- **Measure productive capacity before adding labour.** In two Forest games, our worker counts were already
  equal or greater early while resource collection lagged; the later95/96-carrier fleets did not close the gap.
  Counts of builds, movement and state labels alone do not identify usable capacity or progress. Preserve
  unknown goals and in-turn motion when measuring endpoint stalls (`research/diagnosis/2026-10-12/carrier/`).

### Process and gates

- **Overlap trials.** A replica match plays the submission active when it is created, so a candidate needs to be active
  only while its panel's matches are created (about a minute); park it and run the next. Serial trials gave one per
  8-hour window behind the autoscrim backlog (TRAINING_LOG 2026-10-11 01:03).
- **Zero overruns needs headroom, not luck.** Launchers in big blobs ran within a few hundred bytecodes of the limit;
  every arm that added launcher work overran (c_lane1: 21). A decision-preserving cut (c_bc1: median calm-march turn
  6,856 -> 3,664) was the prerequisite for the launcher arms (TRAINING_LOG 2026-10-10 21:20).

### Tooling

- **Inspect cancelled queue entries as well as pending, running and done.** The standard status helper called a
  cancelled c_ward3 job "missing"; the recursive enqueue check found its preserved entry before any duplicate job ran.
  Recover full run summaries too: copying only results/census/provenance left a completed reference run uncached
  because ingestion requires `summary.txt` (TRAINING_LOG 2026-10-12 13:41).

- **A state check and the action it authorizes must share the transition lock.** The ranked loop checked the validated
  submission, then a trial could activate its candidate before the ranked POST. Serialize fresh checks through match
  creation; both concurrent orderings are regression-tested. Local file locks require one authoritative checkout
  (TRAINING_LOG 2026-10-12).
- **Parallel processes need per-process temp files and a lock.** The trial state and the API token were both written
  through one shared temp file; overlapping panels crashed a collector (TRAINING_LOG 2026-10-11 07:25).
- **Reference caches are per incumbent.** The first screen against a new incumbent replays its 100 roster games; queue
  the second screen only after the first fills the cache (TRAINING_LOG 2026-10-11 06:50).
