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
outside vision. Re-extract the panels with the shot visibility classifier before making that quantitative claim. Measured 2026-10-14
(panel `gauntlet/20261014-160033-panel-c_blind1`): the panel opponents land 20.7 outside-vision hits a game, and our
blind-firing c_blind1 lands 20.2 of 10,551 such shots (damage +96 a game, t 0.07). Blind fire correlates with the teams
that beat us but does not explain their wins; the principle stands (it was free), the expected value here is ~1% of damage.

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
- **Local proxies measure soundness, not matchups.** Over 20 trials with a screen and a panel, the head-to-head score
  (+0.45) and the roster net (+0.42) each track the panel's paired net, a blend +0.58; but no archetype's net tracks
  the panel against the teams it was modelled on (-0.31 to +0.26). Weight local opponents near 50% (the mirror,
  arch_jm), read the roster as a regression check, and let only the panel judge a matchup (TRAINING_LOG 2026-10-16
  11:50, 12:18).
- **A batch Bradley-Terry fit predicts better than the ladder's running Elo when the field is fixed.** Held out, per
  game: log-loss 0.572 vs 0.628 (+3 points accuracy); the ladder's rating for one unchanged build ranged 191 points
  in 33 hours. Use it to choose builds and ranked opponents (expected gain = K x (P_BT - E_ladder)); the ladder's
  number is for seeding only (TRAINING_LOG 2026-10-14 10:40).
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
- **Repair the route, then count the removed stalls.** A second-return veto removes an immediate carrier
  cancellation but still fails to collect for64 native fixture turns, replacing it with a longer cycle and
  suppressing an unjam. A lower oscillation count does not establish delivery. Validate first collection and
  resource return as well as common action paths (`research/diagnosis/2026-10-12-forest-carrier-routing.md`).
- **Separate sites, upgrades and staffing in an income gap.** Exact Forest actions show comparable home-well
  production, while enemy centre wells supply903/544kg of the945/471kg Mana gaps duringr101–250. Neither side
  upgraded throughr1000. Worker counts and whole-trip totals could not identify this; pair action targets with
  signed inventory changes and reconcile the totals (`research/diagnosis/2026-10-12-forest-mana-capacity.md`).

### Process and gates

- **Self-play tournaments select against our own style, not the field.** The Swiss winner over 16 variants of our
  build (c_sw07: GROUP_MIN 3, FORM_MAX_TURNS 11, a wider siege ring, 18/24) scored 63/100 on the field panel: net
  -8 vs c_gp1 and island-rounds -727 (t -3.53) vs c_well9, on whose panel it tied. Its screen h2h was 9/20. A
  parameter search needs field-like opponents (archetypes, panel cells) in its scoring, and its winner still faces
  the panel (TRAINING_LOG 2026-10-16 15:42).
- **Overlap trials.** A replica match plays the submission active when it is created, so a candidate needs to be active
  only while its panel's matches are created (about a minute); park it and run the next. Serial trials gave one per
  8-hour window behind the autoscrim backlog (TRAINING_LOG 2026-10-11 01:03).
- **Zero overruns needs headroom, not luck.** Launchers in big blobs ran within a few hundred bytecodes of the limit;
  every arm that added launcher work overran (c_lane1: 21). A decision-preserving cut (c_bc1: median calm-march turn
  6,856 -> 3,664) was the prerequisite for the launcher arms (TRAINING_LOG 2026-10-10 21:20).

### Budget (owner, PROMPTS 88)

- **An agent project's weekly usage is dominated by idle cache rewrites and context size, not by thinking.** Audit of
  2026-10-07..11 (scratchpad tokens/tally.py, reprice.py): workflow agents that waited 5-60 minutes inside a turn
  rewrote their whole context on resuming (5-minute cache): 18% of all usage; every main-session turn re-read a
  430-730k context: 20%; fixed 30-minute checks cost ~85-165k units each even when idle (past 60 minutes they would
  rewrite the context into a new 1-hour cache entry and cost more). Workflow agents should queue long jobs and stop, a
  fresh agent collects; keep checks under the 1-hour cache TTL and let an event watcher wake the session; compact the
  main context early; one-off setup (reading prior years, building a replica) spent 56% of the first week.

### Tooling

- **Inspect cancelled queue entries as well as pending, running and done.** The standard status helper called a
  cancelled c_ward3 job "missing"; the recursive enqueue check found its preserved entry before any duplicate job ran.
  Recover full run summaries too: copying only results/census/provenance left a completed reference run uncached
  because ingestion requires `summary.txt` (TRAINING_LOG 2026-10-12 13:41).
- **Budget native-profiler storage separately from ordinary games.** A normal control finished, but its profiler
  twin exhausted768MB while serializing the footer. Preserve completed controls and re-run only the failed
  measurement with explicit runtime provenance and simulation identity; a larger heap does not remove trace
  caps or make censored costs usable (TRAINING_LOG 2026-10-12 15:43).

- **A state check and the action it authorizes must share the transition lock.** The ranked loop checked the validated
  submission, then a trial could activate its candidate before the ranked POST. Serialize fresh checks through match
  creation; both concurrent orderings are regression-tested. Local file locks require one authoritative checkout
  (TRAINING_LOG 2026-10-12).
- **Parallel processes need per-process temp files and a lock.** The trial state and the API token were both written
  through one shared temp file; overlapping panels crashed a collector (TRAINING_LOG 2026-10-11 07:25).
- **Reference caches are per incumbent.** The first screen against a new incumbent replays its 100 roster games; queue
  the second screen only after the first fills the cache (TRAINING_LOG 2026-10-11 06:50).
- **Every long-running component needs a liveness alarm that wakes the agent.** On 2026-10-12 18:48 PDT the replica
  and the VM queue runner both stopped without a recorded reason; nothing reported it, and screens queued 40 hours
  later sat pending unseen. An event watcher now exits (waking the session) on a dead replica, ranked loop, VM or
  queue runner; test liveness by the component's own lock or API, not a process name (the runner re-executes from a
  temp copy). Age since creation is no stuck-match test behind a batch backlog: alarm on time seen running
  (TRAINING_LOG 2026-10-14).

- 2026-10-14 (causal graph of panel losses): paired panel cells give a true per-cell counterfactual, and stratifying
  by cell separates causes from effects (enemy carrier kills fell from -2.4 to -0.67 once fights were held fixed). But
  small code changes diverge chaotically from r60-100: wins and losses of the same cell differ by many small amounts,
  not by one early mistake. Use capped or median statistics: means of trip times were dominated by 1,000-round trips.

- 2026-10-16 (PROMPTS 121): a refresh step killed by its timeout must fail loudly, or its output goes stale unseen
  (rating-history.md missed two accepts; the cost had grown quadratically with the number of chart labels). A monitor
  that scans the newest N items misses the one old item that matters: siarnaq's rating chain waits on the OLDEST
  unfinished match, so look for it by state (every RUN match), not by recency.
- 2026-10-17: the replica's host name resolves through an external wildcard DNS (sslip.io), and lookups fail now and
  then (Errno -5 twice in 10 minutes, fine a minute later). A long-lived client must resend on a failed lookup or a
  refused connection (the request never left), and resend a GET on any network error; a POST that may have reached
  the server is not resent (a duplicate scrimmage request). trial-start's in-process panel block died on one lookup.
