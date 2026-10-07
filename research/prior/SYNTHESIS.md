# SYNTHESIS: six prior projects, distilled for Battlecode 2023

Written 2026-10-07. This synthesizes the twelve reader reports in `research/prior/`. The prior projects were attempted in this
order: bc22, bc26, bc25, bc21, bc20, bc24. Each built on the ones before it, so **later findings weigh more**. Where two
years disagree, §2 says which one is later.

Some prior reports left questions open about the 2023 engine. Where this project's own engine-checked digests in
`research/rules/` settle them, they are cited as **[rules]**. Those digests were written from the 3.0.15 source and jar.
They contain no 2023 strategy material, and I read only their surprises, wells/carriers/HQ and map-census sections.

Numbers are quoted exactly as the reports give them. **(inference)** marks my own reading. Source tags:

| tag | report | tag | report |
|---|---|---|---|
| [22] | bc22.md | [20] | bc20.md |
| [26] | bc26.md | [24m] / [24p] / [24t] | bc24-method.md / bc24-play.md / bc24-tools-code.md |
| [25d] / [25t] | bc25-docs.md / bc25-tools-code.md | [env] | bcenv.md |
| [21] | bc21.md | [B] / [G] | BASICS_FROM_GUIDES.md / GALAXY.md |

---

## 0. The six projects in one table

| order | project (2026 dates) | volume | best external result | what actually moved it |
|---|---|---|---|---|
| 1 | bc22 (08-26 to 09-01) | 128 iterations, 62 snapshots | `sample_camelcase` 0/20 almost always (best 1/20); `sample_afinals` 2-4/20 | combat-first targeting, sticky miner target, one shared objective. The external gap never closed [22] |
| 2 | bc26 (09-01 to 09-06) | 252 iterations, 34 snapshots | 10/162 against five benchmark bots | two degeneracy preventers: exploration-heading reassignment (ablated, the mirror fell to 22.2%) and the replacement reserve (ablated, 25.9%) [26] |
| 3 | bc25 (09-06 to 09-16) | 4 lineages; darla ran ~191 arms for 7 accepts | darla-i7 56.0% (84/150) vs `v3` (a finalist-level bot; this number is biased, because `v3` was also used to select builds); about 0-1% vs `TSPAARKHS` | ending isolation (24.7% to 34.0% on day one), a state-token census, and opening fixes taken from `v3` replays [25d] |
| 4 | bc21 (09-16 to 09-23) | 63 iterations, 13 snapshots | `g_iter13` 334/432 (77.3%) over nine 48-game blocks against a fixed field of 8; Elo 1742, rank 3 of 21; 33% against the top bot | opening deployment (+22 points), removing a guard sink, a broadcast fix. All three were found by reading games [21] |
| 5 | bc20 (09-23 to 09-30) | 19 snapshots, ~15,400 scrimmages | `g_iter19` 1752 ± 29, 11th of 65, field score 81.4%, 23.9% against the 10 higher-rated bots | copying an opponent's rush (+79) and an owner-forced rewrite (+49) [20] |
| 6 | bc24 (09-30 to 10-07) | ~80 failed builds, then 6 promotions | `g_iter7` 2113, rank 6 of 88, field score 88.6%, 30.5% against the 5 bots above | a correctness audit (+185 direct, +77 from levers it motivated), a heal hold found by a contrast study (+144), and the "waffle crack" (+55) [24m] |

**(inference)** The projects that gained most measured themselves against an external field with a batch rating (bc21,
bc20, bc24), and the best of them repaired its own basics before adding tactics (bc24). bc22 and bc26 measured mostly
against themselves and plateaued far below the external bar.

---

## 1. The 25 most important lessons

Each lesson lists its supporting years, the evidence, and what it means for 2023.

### Method

**1. Measure against independent external opponents from day one. Self-play gains do not transfer.**
*Years: all six; strongest in bc25, bc20 and bc24.*
- bc22: 62 accepted snapshots moved camelcase from 0/20 to, at best, 1/20 [22].
- bc26: `g_iter14` went 20/20 against the lecture player and against the anicolao bot, then 0/20 against each of three
  stronger entries [env].
- bc25: roster gains of +19, +15 and +29 games bought +2, +2 and −1 against `v3`. Held-out estimates ran at about 60% of
  the in-pool ones [25d].
- bc21: `g_iter5` won its mirror 68.8% but scored 12/48 against 14/48 for the previous build on the ladder [21].
- bc20: six head-to-head accepts totalling +311 added +12 on the ladder. Gate g13 rejected 24-39 a build that the ladder
  put +30 ahead [20].
- 2023: the galaxy-lite ladder against the 61-entrant field is the judge. The mirror is a regression screen only.

**2. Fix basics and correctness before tactics. At a plateau, audit the bot and the measurement tools first.**
*Years: bc24 (decisive), bc22, bc26, bc25, bc20.*
- bc24: about 80 tactic builds failed to beat `g_iter1`. A correctness audit then ran with 8 agents (five lenses, two
  verifiers, one synthesizer), took 4.2 h and confirmed 41 of 42 findings. It gave +185 Elo directly and +77 through the
  levers it motivated, out of a +461 climb [24m].
- bc24: the symmetry was guessed, and wrong on 32.4% of map-sides, while `Sym.observe` had no callers. Lesson F2: "One
  broken basic is a sample of a class: audit at once" [24m].
- bc22: a heal-pre-empts-build bug sat for about 77 iterations, with 6,815 lead left unspent. It was found only when the
  owner asked for a benchmark tally [22].
- 2023: run `readroom-no2023/bc24/AUDIT_PROMPT.md` and `AUDIT_PLAYBOOK.md` on the first working bot and again at every
  plateau.

**3. Find absolute degeneracies by tracing one replay with decision counters, before inventing mechanisms.**
*Years: all six.*
- bc25: counting state tokens in one replay showed soldiers in `S HOME` on 63-79% of their turns, one of them latched for
  416 straight turns. The fix gained +12 head to head and +19 on the roster [25d].
- bc26: one traced rat oscillated for about 1,985 rounds. The fix (heading reassignment) was the largest feature
  measured [26].
- bc22: per-unit move traces showed Miners ping-ponging between tiles. A sticky target gave +9.4 points, the project's
  largest single jump [22].
- bc21: six intake counters found a broadcast-starvation bug in one afternoon, after four hypotheses had failed. From
  its post-mortem: "Every accept this season came from a counter that said 'this never fires' or 'this fires 520
  times'" [21].
- bc20: "895 (47%) mined nothing between r300 and r500" led to iteration 34 [20].
- 2023: put `note|k=v` counters in the indicator string (64 characters, note first) for every latched state: a carrier
  at a well, returning, or queueing; an anchor carry; a launcher at its rally point.

**4. Run no test until the mechanism demonstrably fires (a manipulation check), and enforce this with a tool that refuses.**
*Years: bc21, bc20, bc24, bc26, bc25, bcenv.*
- bc21: the diagnostic-first rule caught three inert candidates [21].
- bc24: the delivery gate stopped about ten arms before each cost a 240-game band test. Before the gate, "10 of 11
  adoption arms had been judged on wins without reproducing the opponent's behaviour" [24p].
- bc26: an arm-to-arm identity check (`same == n`) caught three changes that never executed [26].
- bc25: alice's lever fired on about 1% of turns because the "recipient in range" stage passed only 20% [25d].
- bcenv names the three cases a check must separate: inactive, active without benefit, and beneficial but regressed
  [env].

**5. Determinism, seeded pairing and an identity control come before any verdict. The unit of evidence is the map or cell, not the game.**
*Years: all six.*
- bc20: the engine seeded games from the map file, so 491 of 2,825 ladder games were exact repeats. An unpaired gate
  read REJECT 34-46 while 74 of its 80 pairs were concordant [20].
- bc24: unseeded pairs flipped 15-29% of cells with identical code, so "about 2.5 days ... mostly noise". Once seeded, a
  byte-identical copy read 0 of 80 discordant [24t].
- Even seeded, behaviour-changing arms disagree with the control on 14-38% of pairs [24t].
- bc26 measured a noise floor of about ±9 games per 54 [26]. bc25's phase twins gave an sd of 4.80-6.48 games per 150
  [25d].
- 2023 [rules]: a game is deterministic except for two things: the final coin flip (unseeded `Math.random()`; seven
  identical games gave A, B, B, A, A, A, B) and the depth at which `StackOverflowError` fires.
- 2023 [rules]: our seed patch changes only the ids of spawned robots, and through them their `Random` streams. HQ ids
  and HQ randomness come from the map file.
- So coin-flip games must never count as discordant pairs.

**6. Choose a gate with enough power, on the most informative per-pair statistic, and simulate its power before relying on it.**
*Years: bc21, bc20, bc25, bc24 (decisive), bc22.*
- bc24: the shipping rule had 17% power at a +30 Elo effect. That meant "45 hours without a promotion" until the owner
  asked about the criteria. Rebuilt on the capture difference, it reached 63-65% power at 2.0% false promotion; per pair,
  wins carried 2.2-5.6x less information [24m].
- bc21: the 48-cell panel "could not have accepted anything we were able to build". It produced eight rejects in a row
  and cost about 28 VM-hours [21].
- bc20: three 96-game arms read +18 to +26 and fell back at 240 games [20].
- bc25: one gate tool printed "2.0 sd" for what was really 1.0 sd [25d].
- First looks regress toward zero: bc24's g7kite went from t 2.03 at look 1 to 0.32 pooled [24p].
- 2023 **(inference)**: candidate per-pair margins are islands held at the end, anchors placed, or the island count
  integrated over rounds. Measure each one's information per pair before adopting it.

**7. Instruments disagree, and resolution is not representativeness. Keep an instrument that poses each threat, and when two disagree, run a third.**
*Years: bc26, bc21, bc20, bc24, bc25.*
- bc26: ablating the trap ring looked "free" on the mirror, yet benchmark early wipes rose from 16% to 26%.
- bc26: the owner's rule "if benchmark and mirror contradict, break the tie with a full peer evaluation" rescued
  Iteration 151 (+18 peer games) [26].
- bc21: a defensive change gets a second, pre-registered arm against a sparring partner. A partner needs two verified
  properties: it reproduces the condition, and it wins 25-75% against the incumbent [21].
- bc20: two-arm rule; iteration 58 went 28-6 against `arch_rush` and 2-2 in the mirror [20].
- bc26: "Every self-derived archetype is either a mirror or saturated" [26].

**8. Rate with a batch Bradley-Terry fit, with each build as its own player. Never use a sequential Elo.**
*Years: bc21, bc20, bc24.*
- bc20, with sequential K=32 Elo: "96 calibration games against unplaced bots (88 wins) lifted us from rank 65 to rank 4
  of 66" [20].
- bc21: four weak newcomers lifted a build from 1511 to 1692 [21].
- bc24 added three fixes [24p]:
  - iterate to tolerance (a 3,000-iteration cap had left ratings 30-46 points low);
  - cap each pair at 200 games (1,500 filler games had pulled `g_iter7` from 2150 to 2116, below a bot it beats);
  - calibrate bots rated on few games (uravt was 2274 ± 348 on 26 games, then 1920).
- 2023: `tools/elolib.py` already has the pair cap and the tolerance loop. Galaxy's penalized Elo (K=24) is for
  emulating the official ladder only. Its stationary noise is about 27 Elo and its memory about 30 matches (inference)
  [G].

**9. Copy what beats you. Read how strong bots win, and contrast behaviour rates between the bots that beat you and the bots you beat.**
*Years: bc20, bc25, bc24, bc21.*
- bc20: the copied rush was the largest gain of the project (+79), "the first step outside the error bars" [20].
- bc25: `v3` replays showed its first tower at r34 against darla's r266 on `shell`. That produced iterations 5-7
  (46.0% to 56.0%). "None of this was visible until the owner granted replay access" [25t].
- bc24: a two-group contrast showed us healing under threat 0.445 of the time against the upper tier's 0.257. The heal
  hold built from it gave +144 Elo at t_all 6.46 [24m]. Against waffle, "slow it if you cannot stop it" gave +55 [24p].
- Limits: copies that need an economy we lack failed (bc20's vaporator copy 3-20, its enclosure 4-44 [20]; bc21's
  `arch_big` 0-24 [21]).
- 2023: CLAUDE.md rule 3 allows studying external bots' games and replays. Do it from week one.

**10. The opening decides the game. Instrument the first 50-100 rounds against the strongest opponents.**
*Years: bc21, bc25, bc20, bc22, the guides.*
- bc21: the opening deployment (the whole starting budget into income at round 1) was the largest accepted effect, SPRT
  46-18 (71.9%), and the first change that moved the ladder. The losing games were already 226 behind at r50 [21].
- bc25: the largest gains against `v3` came from the opening ("soldiers until the third tower, bounded by round 100")
  [25t].
- bc20: the earliest onset predictors of a win were economic, at r150-200 [20].
- The cross-year advice: "the whole-game gap was often decided before round fifty" [B].
- 2023 [rules]: each HQ starts with 200 Ad + 200 Mn and can build 5 units per turn from turn 1, so the round-1 build is a
  real decision. On 62 of 103 maps no HQ sees a mana well at spawn.

**11. Tally how games are actually won before choosing a thesis.**
*Years: bc25, bc26, bc24, the guides.*
- bc25: darla's founding thesis died on a win-type tally: 96.5% of 144 games were decided by paint coverage [25d].
- bc26: once both sides used cat traps, the cats died around r177, and every game ended on points at that moment [26].
- bc24: 102 of ColtG5's 135 wins came from the tiebreak [24p].
- 2023: the score term is islands. Anchors on 75% of islands at once win. Otherwise the tiebreak runs islands held,
  anchors placed, Ex, Mn, Ad [B]. The first examplefuncsplayer mirror ended on the mana tiebreak (TRAINING_LOG).
  `MatchFooter` has no win type, so the reason exists only in engine stdout [24t], and the runner must record it.

### Bot

**12. Find the binding resource and the phase in which it binds. Keep every threshold inside the measured operating band, and spend continuously on what compounds.**
*Years: bc22, bc26, bc25, bc20, bc24, bc21.*
- bc25: alice's mean stock was 42,712 chips, but only 1,502 in the deciding r100-300 window. "A gate above where the
  treasury actually sits ... is an off switch": one upgrade gate fired 4 times in 9,147 turns [25d].
- bc20: "a reserve nobody spends is bodies nobody has"; lowering the school banks from 300/700 to 200 gated 30-8 [20].
- bc22: the gap to the benchmarks was production scale (camelcase: 72 Miners and 143 Watchtowers) [22].
- Counterweight: bc21 found "a besieged centre is right to hoard" [21], and bc26's reserve was load-bearing (25.9%
  without it), once it was denominated in units of what it buys [26]. Reserves need a release valve, not removal.
- 2023 [rules]: stockpiles are **per HQ**. `buildRobot` spends only the calling HQ's stock. Each HQ starts with 200/200
  and gains +6/+6 every 5 rounds. Route deliveries to the HQ that will spend them.

**13. Repairs and cap removals transfer to the field; reallocations between unit types rarely do. Prefer changes that cost nothing.**
*Years: bc26, bc21, bc20, bc24, bc25.*
- bc26: "The three changes that ever paid share one property: capability preserved at ZERO marginal cost ... a proposal
  that spends anything to gain something has roughly a one-in-fifteen chance" [26].
- bc21: "Five reallocations ... were all rejected; all three accepts removed a constraint or a bug" [21].
- bc24: none of eight economy or level arms shipped. The one that paid took free resources without costing fight actions
  [24p].
- The cross-year advice: "Repairs of defects and removals of binding caps transferred to the field in every season" [B].

**14. Navigation: greedy plus bug with id-parity handedness; a heavier fallback only when a measured stuck counter fires; stall counters that survive target changes.**
*Years: bc25, bc20, bc24, bc26, bc21, bc22.*
- bc25: an escape hatch gated on the stuck counter gained +13. Full wall-following replacing greedy lost 14 [25d].
- bc20, "the most expensive nav bug": `setTarget` reset the stall counter, so miners froze. The fix gated 32-9 [20].
- bc24:
  - A7: bug state reset whenever a moving target moved.
  - A4: an unreachable visible enemy took the whole turn; 16-36% of enemy-in-view robot-rounds sat idle on walled maps
    [24p].
- Heavier pathfinding is contested: bc21 reverted a Dijkstra before running it, while bc22's vendored one won 13/20.
  See §2.
- 2023 [rules]:
  - Currents push at end of round.
  - The movement cooldown uses the destination tile's multiplier.
  - An empty carrier moves twice per turn.
  - A not-ready cooldown must never advance bug state [B].

**15. Commit to targets (wells, rally points) with explicit release conditions. Never recompute "nearest" every turn, and never commit forever.**
*Years: bc22, bc20, bc26, the guides.*
- bc22: a sticky Miner beacon took the peer rate from 60.3% to 69.7%, and mining actions from 436 to 1,450 on the
  reproduction game. Absolute stickiness lost (68/160) [22].
- bc26: remembered targets were "superb on one map, then 130/216 vs 161" [26].
- The cross-year advice: "Absolute stickiness lost heavily; per-tick re-optimisation ping-pongs" [B].

**16. Keep play symmetric from day one: no compass-order tie-breaks, no first-of-scan picks, per-robot RNG from the id, mirrors from both sides on every map. Do not fix bias by randomizing every decision.**
*Years: bc22, bc26, bc25, bc24, bc21.*
- bc22: identical code won 71.4% as A and 43.6% as B over 720 games. Symmetric tie-breaks gave 61.0% against 57.5%, and
  the A/B gap fell from 27.8 to 14.2 points [22].
- Randomized ties lost twice: bc26 dropped from 62.5% to 52.5% [26], and bc22's random variants also lost [22].
- 2023 [rules]: `senseNearbyRobots`, wells and map infos return column-major order, and `senseNearbyIslands` returns
  HashSet order. Turn order is spawn order across both teams. Which team's HQ acts first is set by the map: B on 59 of
  103 maps.

**17. Decide map symmetry by observation, never by guessing. Name its consumers first, make detection cheap, share the result, and test offline over every map.**
*Years: bc24, bc20, bc21, bc22, bc25, bc26.*
- bc24: a fixed-order guess was wrong on 32.4% of map-sides. The observed version uses a bitmask, per-robot terrain
  memory, collapsing equivalent candidates, scouts and an AND-merge [24t]. SymTest ran it over 300 random symmetric maps
  and never eliminated the true symmetry [24t].
- Caveats:
  - In bc24 the fix was neutral alone (63-57) [24p].
  - bc22's correct terrain scout was net −9 games [22].
  - bc25's arms were inert or overran bytecode, because the answer fed "the fallback of a fallback" [25d].
  - Guessing is worse: bc26's rotation guess was wrong on 16 of 27 maps [26], and bc20's raiders waited 1,500 rounds at
    a wrong image [20].
- 2023 [rules]:
  - The corpus is ROT 44, VERT 42, HORI 16, plus Cornucopia, which is both ROT and HORI.
  - Own HQ positions settle the symmetry on 0 maps; round-1 HQ vision settles it on only 10 of 103.
  - HORIZONTAL means y flips.
  - Currents mirror geometrically. Using `opposite()` is wrong on 41 of the 54 reflection maps that have currents.
  - On FourNations, well types break a symmetry that positions satisfy.

**18. Monitor bytecode, overruns and exceptions from iteration 0. An overrun voids an arm. Count exceptions in the bot, not from the replay.**
*Years: all six.*
- bc21: a candidate's home EC lost 213-404 rounds a game to overruns. Fixes worth about +10% gated at 53% until profiled
  [21].
- bc20: an allocating scan put Miners over budget 120 times a game [20].
- bc25: a terrain sweep overran (`ov` 3 to 8) [25d].
- bc24 [24t]:
  - Its exceptions bar "can never fail", because the replay records only load failures.
  - A deliberate spare-bytecode fill hid a real 95% near miss.
- bc26 blamed bytecode twice without measuring it [26].
- 2023 [rules]:
  - Limits: HQ 20,000, carrier 12,500, all others 10,000.
  - A caught exception costs 500 bytecodes.
  - An overrun resumes mid-code next round with stale state.
  - An uncaught exception destroys the robot, an HQ included, together with its stockpile.
  - One illegal API call anywhere in the code poisons the whole team at load time.

**19. Comms: one purpose per slot, a single writer, round stamps and expiry on everything, explicit clearing rules. Instrument what is heard.**
*Years: bc22, bc21, bc20, bc24, bc26.*
- bc24 A1: an alert meaning "any enemy seen" was fresh in 1,057-1,686 of 1,800 post-setup rounds and switched off every
  defender. A5: a "carried" state never expired [24p].
- bc21: unstamped claims "ping-ponged between stale echoes", so the newer claim must win [21].
- bc22: `SA_HOME_THREAT` never cleared [22].
- bc26: writes from units that may not write threw and aborted the turn [26].
- 2023 [rules]:
  - Writes are allowed only within r² 9 of an own HQ, r² 20 of an own amplifier, or r² 4 of an own island. Reads are
    allowed everywhere.
  - A write costs 75 bytecodes and a read 2.
  - Writes are visible to robots later in the same round.
  - Newborns act next round.
  - So facts are store-and-forward.

**20. Combat: concentrate, reinforce the live fight, shoot what can shoot back, and protect tempo. Lexicographic micro beats smooth scoring, and "survival by inactivity" loses.**
*Years: bc22, bc24, bc20, bc26, the guides.*
- bc22 [22]:
  - Combat-units-first targeting raised the peer rate from 62.1% to 78.1% and gave the first win against camelcase.
  - One shared objective scored 76.7%.
  - A stable focus target took `valley` from 41% to 77%.
- bc24: the heal hold gave +144. Smooth tile scoring lost 1-25 and 1-26, and more retreat was monotonically worse [24p].
- bc26: leashes halved deaths and cost 18 peer games: "Our rats die because they are doing the thing that wins games"
  [26].
- bc20: "drones arriving one at a time die one at a time" [20].
- 2023:
  - Launchers attack every turn but move only every other turn [B].
  - HQs cannot be damaged at all. Their aura hits every enemy within r² 9 at end of round [rules].

**21. Check that every gate toggles and every branch is reachable, and check the premise (the proxy-to-outcome link) before building.**
*Years: bc22, bc26, bc24, bc25, bc21.*
- bc22: four "no contact in N rounds" mechanisms never toggled in a sustained war [22].
- bc26: three iterations tuned unreachable code. "Read the guard, not just the condition" [26].
- bc24: dam and float traps never fired (the bank was below 700 on 64 of 75 maps), so their ablations were void. b2rg
  raised re-grabs by +9.1 SE and lost 11-26 [24m].
- bc21: coverage was "a marker of games we win, not a lever" [21].

**22. The engine is the truth. Read its source or `javap` for every rule, sweep the API for unused capabilities on a schedule, and look for information the engine gives away.**
*Years: all six.*
- bc22: `mutate()` went unused for 81 iterations [22].
- bc25: the first API sweep, at iteration 29, found 37 of 68 methods unused. A soldier attack on enemy paint cost paint
  and did nothing, wasting 42-55% of the soldier paint budget [25t].
- bc26: `squeak` went unused until iteration 165 [26].
- bc24: the enemy flag id encoded its spawn centre [24m].
- bc21: "Eleven of the facts in section 5 contradicted what we assumed" [21].
- 2023 [rules] has already found several such facts:
  - stockpiles are per HQ;
  - deposits need adjacency;
  - a throw empties the whole inventory, even on a miss;
  - enemy inventories are readable through `RobotInfo`;
  - depositing into an enemy HQ gifts it the resources.

### Process

**23. A rule kept in prose decays. Turn each one into a tool that refuses the error.**
*Years: bc25, bc24, bc21, bc26, bc20.*
- bc25 doctrine 19: "a rule that has to be remembered is not a control". `make-arm.sh` exists because a sed matched
  nothing and an arm forfeited 0/72 [25t].
- bc24: "17 filler blocks (about 2,000 games) were played and never recorded until the owner asked" [24t].
- bc26: a staleness warning was printed on every run and "missed every time" [26].

**24. Never let the compute machine idle. Use a standing queue, an idle filler and automatic collection; budget the filler by information and record every game.**
*Years: bc25, bc24, bc22, bc21, bc20.*
- bc24: the VM sat idle about 29% of the time between runs until the queue existed [24t].
- bc25: "you have been stopping and idling" (10 commits, mean gap 44 min) [25d].
- Unbudgeted filler then made up 80% of bc24's games and distorted the rating fit until the pair cap [24p].

**25. Take big swings when incremental work stalls, but with kill criteria and an early field probe. Audit before rewriting, and integrate rather than isolate.**
*Years: bc22, bc20, bc24, bc25.*
- bc22, owner: "we're never going to defeat camelcase by being cautiously incremental" [22].
- bc20: the owner-forced rewrite gave +49, but the 36-stage enclosure programme first met the ladder at its end and
  probed 4-44 [20].
- bc24: the 8-agent rewrite design was never consumed, and its unused sensor was 18.8% of `g_iter3` [24p].
- bc25: the one lineage that reused everyone's pieces went from 24.7% to 34.0% on day one and to 56.0% later [25d].

---

## 2. Contradictions between years, and how to resolve them

Where the evidence differs, the later year generally wins, unless 2023's rules change the premise.

| # | topic | earlier position (year) | later position (year) | resolution for 2023 |
|---|---|---|---|---|
| C1 | What decides an accept | bc21 (4th): an SPRT mirror is "the only gate" (owner PROMPTS 37), and the ladder is the consequence | bc20 (5th) reversed this by 09-29: the ladder head-to-head judges, the mirror screens. bc24 (6th): a band test on seeded pairs under a power-tested ship rule, with the mirror only a screen | **Use bc24's order.** Mirror SPRT catches crashes and regressions; the delivery gate shows the mechanism works; band and ladder tests decide; a pre-registered archetype arm covers defences. The 2023 owner asks for both data sources, local fights and online scrimmages (PROMPTS 1) |
| C2 | Rating | bc21: sequential K=32 Elo | bc20, bc24: batch Bradley-Terry | **BT** for decisions. Galaxy's penalized Elo only for emulating the official ladder [G] |
| C3 | Heavy pathfinding | bc22 (1st): a vendored Dijkstra won 13/20 on pathing alone | bc25 (3rd): full bug lost 14 and a gated hatch won 13. bc21 (4th): a Dijkstra was reverted before running, because navstats showed movement was not the gap. bc24 (6th): no BFS beyond a 7x7 reachability check; "our stillness is in fights" | **Measure first:** navstats and stuck rate per map class. Start with greedy + bug + a gated hatch. 2023 maps range from 1.1% to 71.5% walls, and the BFS/Chebyshev ratio reaches 6.4 on Potions [rules], so pathing may matter on maze maps **(inference)**. Price any BFS against 10k bytecodes |
| C4 | Is symmetry inference worth it? | Closed in bc22 (scout −9); never done in bc26; worth little in bc25 | bc24: essential to the +169 build, though the fix alone read 63-57. bc20: positive | **Build it,** because 2023 has consumers in every game (enemy HQs, wells, islands). Keep it cheap: observe during normal movement, do the heavy work on the HQ, scout only distinguishing tiles. Price it on identical cells |
| C5 | Fixing side bias | bc22: shuffles and random tie-breaks lost. bc26: random ties 62.5% → 52.5% | bc22's shipped fix was goal- and centre-relative tie-breaks (+3.5 points). bc24 breaks ties with the robot's own RNG (cost not separately measured) | **Use consistent, symmetry-relative preferences** (toward the goal or centre; id parity for handedness). Use per-robot RNG only where no symmetric key exists. Verify with mirrors from both sides |
| C6 | Determinism | bc22: one note says reruns were "not perfectly seed-stable"; most notes say byte-identical | bc20: fixed map seeds made repeats. bc24: seeding is exact only for identical code | 2023 [rules] measured it: deterministic except the coin flip and StackOverflow depth, and the seed patch changes only spawned ids. **Run an identity control on day one and exclude coin-flip games** |
| C7 | Survival levers | bc22: retreat-to-heal plus repair helped as a package, but retreating at HP ≤ 15 put 28% of turns into "heal" | bc26: survival by inactivity lost. bc24: more retreat was monotonically worse, and the heal hold (+144) meant healing less | **Do not trade tempo for survival.** In 2023, healing exists only near own islands (+4 a round for STANDARD, +6 for ACCELERATING, within r² 4) [rules]. Retreat to them sparingly, and measure |
| C8 | Standing defence | bc22: garrisons failed. bc20: mirror-priced defences failed, and R2 was accepted against `arch_rush` but withdrawn on the ladder | bc21: cheap guards only under a muckraker swarm were accepted. bc26: a zero-cost trap ring was load-bearing. bc24: "bodies pulled home cost more than they save" | **Defences must be conditional on an observed signature, time-boxed, and tested with an archetype arm.** 2023 HQs are invulnerable and deal 4 per round, so defend carriers, wells and islands, not the HQ **(inference)** |
| C9 | Reserves | bc20: remove reserves nobody spends | bc26: a reserve in units of what it buys was load-bearing, with an "army gone → spend" override. bc25: a reserve can be a dead band, yet removing it collapsed towers. bc21: hoard under siege | **Denominate reserves in units of what they buy, keep them inside the measured band, and give them a release valve** (a stagnation timer; carriers or army gone means spend) |
| C10 | Using several agents | bc25: isolated lineages co-adapted into a joint local optimum. bc20: sub-agent design panels were slow | bc24: multi-agent audits worked (41 of 42 findings confirmed); study critics were better calibrated than syntheses; an 8-agent rewrite design went unused | "Delegate reading, not deciding. Parallelise games, not agents" [B]. Use subagents for audits with adversarial verifiers, for reading, and as critics. Keep one integrating development lineage |
| C11 | Rewrites | bc20: the rewrite helped (+49, p about 0.11, with a winner's curse later) | bc24: the rewrite failed. Advice: a rewrite from a copied design "rated far below the incumbent until the proven parts were restored" | **Audit first.** Rewrite only with an early ladder probe and kill criteria, and keep the proven parts |
| C12 | Accept rule details | bc22: an absolute 60% WinPct gate, which drifted. bc25: McNemar z > 2 on either instrument (owner). bc20: +1 SE, a confirming repeat, and a pooled lower bound | bc24: t_all/t_up at looks of 240, 480 and 720 pairs | **bc24's structure, on a 2023 per-pair margin,** with power simulated first |
| C13 | Studying stronger bots' games | bc21: a tier rule locked replays of bots we beat under 20%, which starved the census | bc20: the owner retired that rule. bc25: `v3` replays were forbidden until 09-14, then decisive | **Study every game freely** (2023 CLAUDE.md rule 3) |
| C14 | Choosing maps | bc21: contest rules banned chosen-map play against external bots | bc24: the agent over-read that ban for 4 days; the owner then allowed chosen maps for diagnostics (PROMPTS 178) | **The ladder stays random; diagnostics may choose maps and sides,** including one map where the mechanism can fire and one where it cannot [21] |
| C15 | Games between external bots | bc21 owner (PROMPTS 27): "external-vs-external is a waste of VM" | The 2023 owner (PROMPTS 1): "In the spare VM cycles, have random bots on the ladder do the same" | **Follow 2023:** autoscrims among field bots at filler priority. They also calibrate field ratings in the BT fit **(inference)** |
| C16 | Benchmark cadence | bc22: every 3 Gauntlets, and it went stale | bc26, bc25: on every accept (owner requests) | **Every accept, scripted** |
| C17 | Exploration | bc20: sector exploration raised coverage from 22.8% to 37.5%. bc21: more scouting was not a lever (coverage is a marker) | bc26: fixing stuck explorers was the largest single feature (+28) | **Fix degenerate explorers first;** don't expect more scouting to win on its own. 2023 still needs scouting for mana wells and symmetry, so measure what consumes it |
| C18 | Logging channel | bc21, bc20: grep-able `@tag` lines on stdout | bc24: replays carry no stdout, so counters go in indicator strings | 2023 [rules]: no robot output in the replay; indicators are capped at 64 characters, and only the last one per turn is kept. **Counters go in indicators; stdout only in diagnostic runs** |
| C19 | Symmetry names | bc24: FX (x flips) and FY (y flips) | 2023 engine: HORIZONTAL flips y and VERTICAL flips x, named after the mirror line [rules] | **Define each candidate by its formula in code** [B]. Test our `FLIP_X`/`FLIP_Y` against `GameMap.symmetry` (0 ROT, 1 HORI, 2 VERT) |
| C20 | How fast symmetry settles | Advice quotes a practice season: "settled by round 1 in about half of games and by round 30 in about three quarters" [B] | 2023 map census: round-1 HQ vision settles only 10 of 103 maps [rules] | **Plan for scouting,** and measure the 2023 settle-round distribution |

---

## 3. Consolidated steal list

Priorities: **P0** before the first gated arm; **P1** during the foundation; **P2** when a need appears. Path roots:
`V24` = `~/projects/vibe/2024`, `V25` = `~/projects/vibe/2025`, `V20` = `~/projects/vibe/2020`, `R21`/`R22`/`R26` =
`~/projects/vibe/reference/battlecode2{1,2,6}-vibe`, `GX` = `~/projects/vibe/reference/galaxy`, `ENV` =
`~/projects/vibe/reference/bcenv`, `RR` = `~/projects/vibe/reference/readroom-no2023`.

### 3.1 Already present in `2023/tools` (checked by listing and grep, not audited): verify and extend

| piece (2023 path) | origin | what to add | prio |
|---|---|---|---|
| `lib.sh` `run_game` | V24 `lib.sh` | Add `-Dbc.server.websocket=false`: grep finds no such flag, so every game binds port 6175 [G][rules]. Parse a **reason code**: the eight 3.0.15 reason strings plus `nobody wins` [env]. Flag coin-flip games | P0 |
| `gauntlet.sh` | V24 `gauntlet.sh` | It inlines its own `java` command (line 70) instead of calling `run_game`, the same defect [24t] flagged in 2024. Route it through `run_game`. Add a code hash per row (`bot_identity`), `maps.src`/`bot.txt` provenance, an atomic run id, an exception count from indicators, and an in-flight warning [25t] | P0 |
| `summarize.py` | V25 `collate.sh` | The warnings `!! INCOMPLETE`, "same map list as …", unequal samples; swept maps per opponent | P1 |
| `compare.py` | V24 / R26 / R22 | Already joins on (opponent, map, side) with identity and flips. Add the round delta on games whose outcome held [26][22] | P1 |
| `elolib.py` | V24 | Has the pair cap 200 and the tolerance loop. Add reason-code and code-hash columns to `games.csv` | P0 |
| `sprt.py` | V24 / R21 | Its docstring still says BC20 [B]. Check the defaults (p0 0.50, p1 0.58) | P1 |
| `statlib.py` | V24 / R21 | Its docstring names `correlate.py` and `onset.py`, which are absent [B] | P2 |
| `deadcode.py` | V24 | Add constant folding over `C` switches and detection of write-only fields (MEAS14) [24t] | P1 |
| `unit-tests.sh`, `test_tools.py`, `test/bot/BotTest.java` | V24 | Add a `flock`; split fast tests from slow ones (bc24's suite took ~10 min and ran ~220 times on the 2-vCPU driver) [24t] | P1 |
| `replaydump/ReplayDump.java` (.bc23, 11 modes) | V24 / V25 / V20 / R21 design | Census columns (§5.3); fixture integrity tests (deaths equal kills, cumulative columns never fall, summary matches stdout) [24t]; multi-game replay files for the replica [G] | P0-P1 |
| `bench-discover.py`, `bench-fetch.sh`, `bench-scan.sh`, `bench-hash.py`, `bench-select.py`, `bench-compile.sh` + `benchcompile/`, `bench-roster.py`, `bench-dates.py`; `field.txt` (61 entrants) | V24 | A provenance table (repo, commit, date, package, hash); a two-game calibration block for every new bot [24p] | P1 |
| `vm.sh`, `vm-run.sh`, `vm-tail.sh`, `throughput.sh` | V24 / R21 | Add the queue tools listed in §3.2 | P0 |
| `get-engine.sh` | V24 `build-engine.sh` idea | Correct the comment: the seed patch does **not** reseed HQ ids or the coin flip [rules] | P1 |
| `research/rules/mapcensus/MapCensus.java` | V25 RuinScan, R21 MapInfo | Already the corpus census (symmetry, HQs, wells, islands, reachability) | done |

### 3.2 To port

| piece | source path | what changes for 2023 | prio |
|---|---|---|---|
| `snapshot.sh` (freeze `src/bot` as `src/g_iterN`, rewrite package, refuse existing names) | `V24/tools/snapshot.sh` (also `R22/tools/snapshot.sh`) | nothing; 2023 has none | **P0** |
| Content-hash build identity | `V25/tools/bot_identity.py` | the package line normalised; a hash in every result row and PASS file | **P0** |
| Determinism and identity control | `V25/agents/alice/tools/determinism-check.sh`, `diff-runs.py`; the content-hash trick from `V25/agents/carol/…/replay-strings.py --hash` | exclude coin-flip games; a byte-identical copy must read 0 discordant | **P0** |
| Seeded paired cells, SPRT on discordant pairs | `V24/tools/paired.sh`, `mirror.sh` (design from V20) | `.bc23`; report coin flips separately; make `REF` a required argument | **P0** |
| Ladder blocks with the seed as a 4th cell field | `V24/tools/scrim.sh`, `scrim-record.py` | store a reason code. The 40-character cut would merge every tiebreak reason, since all share the prefix "The winning team won on tiebreakers (mor" [24t]. Keep for band and delivery blocks if the replica schedules the ladder | **P0** |
| Standing VM queue | `V24/tools/vm-queue.sh`, `vm-enqueue.sh`, `vm-collect.sh` (no replays by default), `vm-sync.sh` (rename swap), `vm-prune.sh`, `vm-stop.sh` | `REMOTE_REPO=projects/vibe/2023`; a back-off when jobs fail fast (a disk-full queue spun for 18 min) | **P0** |
| Cross-runner game semaphore | `V25/tools/remote-slot.sh` + `semaphore-test.sh` | one flock for every game-starting path: gauntlet, replica worker, filler | **P0** once the replica runs |
| Symmetry property test | `V24/test/bot/SymTest.java` | the 2023 fixed features; all 103 real maps from the jar plus 300 random maps, both sides | **P0** |
| Correctness audit | `RR/bc24/AUDIT_PROMPT.md`, `AUDIT_PLAYBOOK.md` | run on the first working bot | **P0** (process) |
| Reason-string fixtures | bcenv's list [env] | the 8 real strings plus `nobody wins`; replace the synthetic "won by anchoring sky islands" test | **P0** |
| Delivery gate and band test | `V24/tools/delivery-gate.sh`, `delivery-check.py`, `band-test.sh` | 2023 census columns; a fresh base seed per gate; PASS tied to a code hash | P1 |
| Paired evaluation with looks | `V24/tools/eval-paired.py` | swap the capture difference for the 2023 per-pair margin; re-simulate power | P1 |
| Basics battery | `V24/tools/basics.py` | absolute bars: symWrong 0, decided by the offline bound, 0 overruns, 0 exceptions read from the indicator. Relative checks paired, failing only beyond 2 SE | P1 |
| Fake `RobotController` (Proxy) | `V24/test/bot/BotTest.java` | model write ranges, per-type cooldowns, carrier weight, clouds and currents [24t] | P1 |
| Arm creation and acceptance by script | `V25/agents/darla/tools/make-arm.sh`, `accept-iteration.sh`; `V24/tools/arm-intent.txt` + its check | package names; or make switches non-final in `src/bot` [24t] | P1 |
| Filler, collection and tally | `V24/tools/filler-pair.sh`, `collect-fillers.sh`, `filler-tally.py`; `V25/agents/darla/tools/idle-filler.sh`, `jobs.sh`, `watch-state.sh`, `status-line.sh` | budget filler games; watch artefacts (`summary.txt`), not logs | P1 |
| Post-block command and charts | `V24/tools/post-block.sh`, `field-score.py` (from V20), `progress-chart.py`, `elo.py` (band, pool, explore) | install matplotlib in `tools/.venv` (the driver lacks it); `field-score.py`'s start date | P1 |
| Diagnostic batches | `V24/tools/diag-batch.sh` | at most 8 games at once; select columns by header name | P1 |
| Map-level resampling | `V25/tools/map-resample.py` | keys (map, side, seed) | P1 |
| Run recovery | `V25/tools/gauntlet-collect.sh` | parsers | P1 |
| Frozen-roster history | `R26/tools/track_vs_old_bots.py` (or `V25/tools/`) | roster of `g_iter0` plus every 5th snapshot; label rows by the binary that played | P1 |
| Cheap 4-match screen | `R26/tools/paired-check.sh` | one maze map and one open map; 2023 counters | P1 |
| Gate maths (finite-population correction, noise floor, power, refuse wrong referent) | `V25/agents/bob/bob-tools/gate_sd.py`, `stage0.py`; carol's `sampledgate.py`, `gatepower.py`, `noisefloor.py`, `margin.py`; alice's `noise-floor.py` | consolidate into one module | P1-P2 |
| Two-group contrast census (the method behind +144) | `V24/tools/capability-census.sh`, `capability-summary.py`, `arm-deltas.py` | 2023 columns (§5.3) | P1 once columns exist |
| Galaxy rating, finalization, matchmaking | `GX/backend/siarnaq/api/teams/models.py:13-58`, `api/compete/models.py:454-542`, `api/teams/managers.py:11-90,163-253`, `api/compete/serializers.py:35-69,400-465`, `saturn/pkg/run/java.go:16`; tests `api/compete/test_models.py:160-485`, `api/teams/tests.py:21-110` | re-implement in stdlib Python (§5.6) | **P0** for the replica |
| Correlation and onset pipeline | `V24/tools/correlate.py`, `onset.py`, `polarity.py`, `derived.py`, `scrim-study.*`, `test_metrics.py` | 2023 metric list; run on merged blocks | P2 |
| Replay puppet | `V20/tools/puppet.sh`, `puppet.py`, `puppet/RawEvents.java`, `src/puppet/` | 2023 bots can read `-Dbc.testing.*` [rules]; diagnostics only, never a strength measure [20] | P2 |
| Early-deficit and HQ "why no build" censuses | `R26/tools/early_wipes.py`, `king_census.py` | concepts: carriers wiped by round N; HQ build reasons | P2 |
| Tournament scheduling patterns | `V25/tools/tournament.sh`, `tournament-report.py`, `systemd/` | HEAD export, isolated compile, dedupe; for the replica timer | P2 |
| Session watchdog | `V25/tools/agent-watchdog.sh` + systemd | only for long unattended runs (survives usage-limit pauses) | P2 |
| Two-stage disk prune | `V25/agents/darla/tools/disk-guard.sh`, `V25/tools/driver-prune.sh` | `.bc23`; keep replays that consumers need | P2 |
| Append-only record hook | `ENV/scripts/check-prompts.mjs` | as a ~10-line shell byte-prefix check guarding `PROMPTS.md` and `TRAINING_LOG.md`, without the "must append" rule [env] | P2 |
| Remote control from a phone | `RR/bc21/REMOTE_CONTROL.md` (tmux + `claude --rc`) | — | P2 |
| Generated unrolled Dijkstra | the idea in `R22/src/bot/Dijkstra20.java`'s provenance header | write our own generator with symmetric tie-breaks; only if navstats demand it | P2 |

### 3.3 Bot patterns to copy (designs, not files)

| pattern | source | 2023 status / change |
|---|---|---|
| Turn loop: overrun means the round changed during the turn; near miss above 90%; exceptions counted; per-id RNG; note-first indicator | `V24/src/g_iter7/RobotPlayer.java`, `G.java`; `V25/agents/darla/src/darla/RobotPlayer.java` `monitorAndYield` | in `2023/src/bot/RobotPlayer.java`; see §4.9 |
| Constants with measured provenance, plus switch invariants tested | `V24/src/g_iter7/C.java`; `R21/src/bot/C.java` + `test/bot/ConstantsTest` | `C.java` exists; add invariant tests |
| Observed symmetry: bitmask never emptied, `collapseEquivalent`, `scoutTarget`, budgeted `update` (`BC_START`/`BC_STOP`) | `V24/src/g_iter7/Sym.java`; `V20/src/bot/MapState.java` (`pruneEmpty`); `R21/src/bot/MapState.java` | `MapMem.java` does part of this; check against §4.6 |
| Lexicographic 9-tile micro; `engageableFast`/REACH_FAST reachability | `V24/src/g_iter7/Micro.java` | re-derive the radii for launchers (§4.7) |
| Nav fixes: A7 `resetNeeded`, A9 edge flip; escape hatch; heading reassignment; Bug2 only for stationary targets, tracing only terrain | `V24/.../Nav.java`; `V25/.../darla RobotPlayer.stepToward`; `R26/src/bot/RobotPlayer.java` `explore()`, `moveToward` | `Nav.java` has A7 and handedness; add the rest (§4.4) |
| Schema header, pure packers, slot-layout test derived from constants; stamped claims, newer wins | `V24/src/g_iter7/Comms.java`; `R21/src/bot/MapState.java` (`claimEnemy`/`claimOwn`) | `Comms.java` has the header; add stamps and tests (§4.8) |
| Per-turn sensing cache; strided scans of large sensing results | `V20/src/bot/Robot.java` `sense()`; `V20/src/bot/Miner.java` `rememberSoup` | apply to wells, clouds and islands |
| Offline economic breakpoints with a unit test | `R21/src/bot/Econ.java` (`bestSize`) | becomes the carrier load and trip model (§4.3) |

### 3.4 Skip

- `R22/src/bot/Dijkstra20.java`: external code (rule 4), and its tie-break chain is a symmetry hazard.
- `bc22_schema.py`: generated for 2022.
- `build-engine.sh`: superseded by `get-engine.sh`.
- `tier-check.sh`: its rule was retired.
- `log-scan.sh`: broken (MEAS17).
- 2021's `band.py`, `ladder.sh` and old plots.
- `isolation-sweep.sh` and `agent-commit.sh`: needed only for several lineages.
- `vm-match.sh` variants.
- `scan.sh`: chosen-map scans against external bots.
- 2024's study analysers (`premise.py` etc.): keep the pattern only.
- bcenv's NixOS/GCE supervisor topology.
- Galaxy's siarnaq deployment, saturn, titan, `deploy/`, the frontend production build and the scaffold's Gradle tasks: each
  of these reaches official infrastructure [G].

---

## 4. Foundation bot plan for 2023

### 4.0 Where the bot stands (observed 2026-10-07 ~18:30)

`src/bot` holds:
- `RobotPlayer`: the turn loop, with counters `ov`, `ex`, `nm`, `sm`, `sd`, and `MapMem.process` run on spare bytecode;
- `G`, `C`, `Comms` (schema), `HQ`, `HQState`, `Carrier`, `Launcher`, `Amplifier`, `Other`, `Wells`;
- `MapMem`: tile memory plus symmetry;
- `Nav`: greedy scored after the current push, plus bug.

The bot has no git commit yet, and `docs/` is empty. CLAUDE.md points to `TRAINING_ALGORITHM.md`, `RULES.md` and
`HANDOFF.md`, none of which exist yet.

### 4.1 2023 facts that settle what the prior reports left open

The V-numbers refer to the questions in BASICS §9 P0 [B]. All rows are [rules].

| V | question | answer |
|---|---|---|
| V1 | collect yield | 1 kg per collect (3 if the well is upgraded); with action cooldown 10, that is one collect per turn. Adjacency includes the carrier's own tile. Up to 9 carriers can mine one well, with no per-well cap. Filling 40 kg takes 40 turns at a standard well |
| V2 | are banks per HQ? | **Yes.** 200 Ad + 200 Mn per HQ at round 1, and +6/+6 per HQ every 5 rounds. Carriers can withdraw only from an own HQ |
| V3 | timing | Newborns act the next round. Shared-array writes are visible to robots later in the same round |
| V4 | turn order | Spawn order, across both teams. The map decides which team's HQ goes first (B on 59 of 103 maps) |
| V5 | HQ attack | Every enemy within r² 9 loses 4 HP at end of round; several HQs stack. HQs cannot be damaged |
| V6 | clouds | A robot in a cloud sees only r² 4, and robots in clouds are invisible beyond r² 4. Attacks need no vision. A spawn tile must be sensable |
| V8 | islands | Health changes by floor(100·(own − enemy)/area) per round. Nothing decays on an empty island. Own robots within r² 4 heal +4 (STANDARD) or +6 (ACCELERATING). The win is checked only on placement |
| V9 | throw | Damage is floor(1.25·weight), at most 50. The **whole inventory, anchors included, is destroyed even on a miss.** Deposits go to wells or HQs of either team |
| V10 | Ad→Ex conversion | Symmetric: an Ad well plus 600 Mn, or a Mn well plus 600 Ad, becomes an elixir well. 1,400 of the well's own type upgrades it. Changes are permanent |
| V11 | action multipliers | Multipliers apply to action cooldowns too, so a boosted launcher sometimes attacks twice in a turn |
| V12 | "anchors placed" | Recaptures count again; re-anchoring your own island adds 0 |
| V13 | symmetry frequencies | ROT 44, VERT 42, HORI 16; Cornucopia is both ROT and HORI |
| — | carrier movement | Move cooldown = floor(0.375·weight) + 5. An empty carrier moves twice per turn; from 14 kg it needs at least one turn per move; at 40 kg, or holding an anchor, it moves every other turn. **Collect after moving** |

### 4.2 Architecture

Keep the current layering, which matches the guides [B] and the bc24, bc21 and bc20 skeletons. The rules:
- Statics are per robot, so team state lives only in the shared array. Sense once per turn.
- Every action helper returns whether it acted, so handlers fall through on failure (bc26 iteration 3; [B]).
- The HQ is the planner. It is immortal, has 20,000 bytecodes, and can always write.
- Every constant carries the measurement that set it. Arm switches are checked by `arm-intent` or are non-final in the
  working bot [24t].
- Audit every tie-break on the day it is written (lesson 16).
- Catch around the whole turn. `StackOverflowError` cannot be caught at all [rules].
- No `java.util` in hot paths (`HashMap.put` ≈ 143 bytecodes).
- No big static initializers: every robot pays for them on its first turn. A 3,000-element array costs a new carrier
  3,003 of its 12,500 [rules].
- No reflection-flavoured calls anywhere: they poison the whole team at load [rules].

### 4.3 Economy

- **Offline model first** [B]. One carrier cycle is T(d, m) = d/2 + ceil(m/r) + d·floor(5 + 3m/8)/10 + 1, and income is
  m/T. Validate it to within 20% in a logged game. **(inference)** At a standard well, collecting dominates the cycle,
  which favours full loads; `C.CARRIER_RETURN_LOAD = 40` is still a first guess.
- **Assignment at birth.** The HQ builds a carrier on the spawn tile nearest the well it assigns. Since a newborn acts next
  round and takes the nearest known well of the needed type, no comms are needed [B].
- **Carrier life:**
  - commit to a well, with release conditions (a crowding patience and a timeout);
  - deposit to the HQ that will spend (banks are per HQ), then leave the ring;
  - flee when empty (the fastest unit), throw only when doomed (never as a test), and never deposit next to an enemy HQ.
- **Mana is not guaranteed near HQs.** On 62 of 103 maps no HQ sees a mana well at spawn, and on 37 maps some HQ's nearest
  mana well is beyond d² 100 [rules]. Early scouting for mana is part of the economy **(inference)**.
- **Production:**
  - day one: a modulo cycle;
  - then a score-sorted queue that saves for its top item in each currency (an anchor blocks both, a launcher only Mn) [B];
  - reserves in units of what they buy, with a stagnation release [26][25t];
  - "carriers gone → rebuild carriers regardless of reserves" **(inference from bc26's emergency override)**.
- **Anchors belong in the foundation.** One HQ builds anchors and carriers route Ad and Mn to it. The number needed is
  ceil(0.75·N): 3 on 44 maps and 6 on 33 [rules]. An endgame deadline turns every remaining Ad and Mn into placed anchors
  before round 2000 [B].
- **Counters:**
  - `cy` cycles, `dw` deposit waits, `wf` well full, `bs` blocked spawns;
  - floating Ad and Mn per HQ at r100, r300 and r600;
  - deliveries per HQ per 100 rounds;
  - "why no build" reasons [26].
- **Bars:** every HQ receives deliveries in every 100-round window; a zero is the 2023 version of bc26's starving King
  [env].

### 4.4 Navigation

- **Present:** greedy scored at the destination after the current push; bug with id handedness; a stall flip; a target
  move of d² ≤ 8 keeps bug state (A7).
- **Add:**
  - a loop on `isMovementReady()`, since a light carrier may move twice;
  - a not-ready cooldown never advances bug state or stall counters;
  - a time budget per target (`dist × turnsPerTile + 20`), then blacklist the target [B];
  - a reachability filter so an unreachable enemy cannot take a launcher's turn (A4);
  - a map-edge flip (A9);
  - an A–B–A oscillation guard.
- **Clear rings** [B][20]:
  - no unit parks within r² 13 of an own HQ;
  - a carrier waits at distance 2 when the deposit ring is full;
  - a carrier re-targets when a well's tiles are full.
- **Costs:** an enemy HQ's r² 9 is a wall for carriers and a cost for launchers. Stepping into a cloud costs ×1.2 on that
  move [rules].
- **Measure before building more:** `ReplayDump --navstats` per map class. Heavier tools come later and only on evidence: a
  bitmask BFS over remembered terrain (reported at about 300 bytecodes [B]), HQ-side BFS for well reachability, Optimal Bug.

### 4.5 Exploration

- **Targets:** random far targets with timeouts, and the centre first, since it settles symmetry fastest [B]. Reassign the
  heading after explore stalls (bc26: +28).
- **Never idle:** a battlefront or next-island word in the array [B].
- **Every unit is a sensor:** buffer facts and flush when a write is possible. Carriers are the natural couriers. Add
  amplifiers as relays only once facts are measured arriving late [21][B].
- **Metrics:** first-sighting round of mana wells, Ad wells, islands and enemy HQs. Coverage is a marker only [21].

### 4.6 Symmetry

- **Present:** `MapMem` (char codes per tile, a candidate mask OR-merged into slot 4, never emptied, conflicts counted).
- **Check against the 2023 facts [rules]:**
  - currents mirrored geometrically;
  - well type compared with care, since conversion changes it;
  - geometric elimination from own HQs, and "predicted HQ seen empty";
  - the Cornucopia tie handled by collapsing candidates that predict the same enemy HQs [24t].
- **Budget:** the lazy W·H `char` array costs up to 3,600 bytecodes per robot when allocated **(inference from [rules]'s
  allocation rule)**.
- **Offline tests:** SymTest on 300 random maps plus all 103 real maps, from both sides. The true symmetry is never
  eliminated; record the distribution of decision rounds, and set the "decided by" bar from that offline bound [24t].
- **In replays:** compare the indicator's `sm`/`sd` with `GameMap.symmetry`. **symWrong = 0** is an absolute bar.
- **Name the consumers** (and let `deadcode.py` prove each is called):
  - enemy HQ candidates (launcher targets; stay out of their r² 9);
  - enemy wells (raids);
  - mirrored islands;
  - own-half safety for choosing anchor islands;
  - filling unseen terrain for reachability.
- **Scouts** go to the nearest tile where the candidates disagree, in groups rather than alone [24t][B].

### 4.7 Combat

- **Kernel:** lexicographic scoring of the 9 tiles (bc24 `Micro` shape). Branch on `isMovementReady()`, since movement is
  the scarce cooldown. Evaluate both attack-then-move and move-then-attack [B].
- **Threat model:** an enemy launcher can hit any tile within **r² 26** after one step (computed [B]; I re-derived it: the
  offset (5,1) reaches (4,0) at 16, and (5,2) cannot). **Flag:** `C.THREAT_R2 = 20` in `src/bot/C.java` is below that
  worst case, and its own comment ("a step adds ~1.4 tiles", about (4+1.41)² ≈ 29) disagrees with the value. Check it
  **(inference from reading the code)**. Other threats: the HQ's static r² 9; a carrier with cargo throws at r² 9.
- **Targets:** a kill this turn first; then anchor-carrying carriers (visible through `RobotInfo.getTotalAnchors`
  [rules]); launchers; lowest HP within a class. Never target HQs. A deterministic order (value, HP, id) gives focus fire
  without comms [22][B].
- **Concentrate:** batch-build launchers in one turn so they move in phase **(inference)**. Rally on clustered sightings.
  Note that bc22's "rally before reinforcing" kept failing [B].
- **Tempo:** strike when ready and step out of reach while cooling down. bc24 left this open: we stayed in reach 0.252 of
  the time against the upper tier's 0.111 [24p].
- **Islands:** launchers standing on enemy islands decay their anchors through net occupancy; own islands heal [rules].
- **Census from day one:**
  - ready and striking on contact;
  - hit while unable to move away;
  - ended the turn in reach;
  - step-ins by HP;
  - kills and deaths by type.

  Contrast these between the bots that beat us and the bots we beat [24m].

### 4.8 Communication

- **Present schema** (`Comms.java`):

  | slots | content |
  |---|---|
  | 0-3 | our HQ locations |
  | 4 | symmetry eliminations |
  | 5-20 | wells |
  | 21-56 | islands, by id |
  | 57-60 | enemy sightings, with a 4-bit stamp |
  | 61 | anchor request |
  | 62-63 | reserved |

  The guides propose adding enemy HQ words, a commander token, per-HQ build intents and sighting clusters [B].
- **Rules:**
  - Everything that can go stale carries a stamp and an expiry. **(inference)** Island ownership currently has owner bits
    but no stamp.
  - Newer claims win [21].
  - Every write is guarded by `canWrite` (the code already does this).
  - A pending-write queue with counters `fq`/`ff`/`fd`.
  - A slot-layout test derived from the constants (MEAS15).
  - An encode/decode round trip over the whole 60×60 range.
- **Census:** `getRobotCount()` gives the exact total. Carriers check in at deposits. Never use "ever built" counters as a
  census [B].
- **Instrument what is heard:** writes attempted versus succeeded, overwrites, and what readers decode [21].

### 4.9 Bytecode

- **Present:** `ov`, `ex`, `nm` and `maxBc`, with `MapMem.process` filling spare budget (2,500 left on the HQ, 1,200 on
  others).
- **Bars:** 0 overruns and 0 exceptions per type in every block; any overrun voids an arm [25t].
- **Watch** **(inference, from reading `MapMem.process` and `RobotPlayer`)**: the fill runs while more than the reserve
  is left, and `nm` is counted after it. So the fill reaches about 87.5% of the limit on HQs (20,000 − 2,500) and 88% on
  launchers (10,000 − 1,200), but about 90.4% on carriers (12,500 − 1,200), above the 90% near-miss line. Carrier near
  misses will therefore saturate on any turn with pending tiles. This is bc24's M10 hazard: a deliberate fill hid a real
  95% near miss. Measure near misses *before* the fill, or exclude fill turns.
- **Keep a margin before `Clock.yield()`**: running out right before the yield costs a whole extra turn [rules].

### 4.10 Build order and the foundation bar

The order follows BASICS §9, adjusted for what exists:

| phase | content | where it stands |
|---|---|---|
| P0 | skeleton and RULES digest | mostly done |
| P1 | comms hub | — |
| P2 | movement, the carrier loop, HQ modulo production | — |
| P3 | map memory and symmetry | — |
| P4 | launcher micro and macro | — |
| P5 | islands and anchors | — |
| P6 | exploration and relays | — |
| P7 | production policy and map latches | — |
| P8 | experiments: well upgrade and elixir, boosters, destabilizers, Optimal Bug, spawn camping | — |

**The foundation is done** when the bot:
- beats examplefuncsplayer from both sides on all 103 maps;
- has 0 overruns and 0 exceptions;
- shows symWrong = 0;
- has non-zero deliveries for every HQ.

Then calibrate it on the ladder and run the first correctness audit (lesson 2).

---

## 5. Infrastructure plan

### 5.1 Runner and results contract

- **Fixes:** the §3.1 fixes to `run_game` and `gauntlet.sh` (websocket off, one code path, reason code, code hash, seed,
  coin-flip flag, exceptions read from indicators).
- **Results row:** `opponent,map,bot_side,winner_side,rounds,bot_result,reason,reason_code,seed,bot_hash,opp_hash,run_id`.
- **Job accounting** [env]: report scheduled, completed, excluded and retried counts with an explicit denominator.
  Retries are linked attempts; nothing is silently dropped.
- **Day one:** a determinism check (identical code twice) and an identity control (a byte-identical copy reads 0
  discordant, coin flips excluded) on every verdict path [24m].
- **Throughput** (TRAINING_LOG): 8.9 games/min at K=8 and 9.7 at K=12 on the 8-vCPU VM, about 3 MB per replay.
  **(inference)** The knee is near 8. Cap all game sources together at 7-8, since 24 games at once starved sshd in bc24
  [24t].

### 5.2 VM queue and operations

- **Queue:** `vm-queue`/`vm-enqueue` (flock, STOP file, private copy, correct exit codes, fail-fast back-off), an idle
  filler (replica autoscrim rounds and paired filler), automatic collection at every task check, and one cross-runner
  semaphore [24t][25t].
- **Disk:**
  - The VM has 20 GB, with 8.6 GB free at the start.
  - Keep loss replays and the replays on consumers' keep lists; prune in two stages.
  - `vm-collect` brings no replays back by default.
  - The driver is at 90% with 2.9 GB free: never store replays or run volume there.
- **Hygiene:**
  - Push after every commit.
  - Kill by PID, never with `pkill -f` (five self-kills in bc24 [24m]).
  - Re-exec running scripts from a private copy.
  - Use private class trees per run.

### 5.3 Replay reader (`tools/replaydump`, present)

**Next census columns** (from [24t], [B] and §4):
- Ad, Mn and Ex delivered per HQ, by phase;
- carrier trips, idle carriers, carrier deaths by phase;
- floating stock per HQ at fixed rounds;
- `bs`/`dw`;
- launcher tempo rates (§4.7);
- kills and deaths by type;
- anchors built, picked up, placed and lost; islands held per round; first island round;
- `symWrong` and `symDecidedRound`;
- overruns and near misses by type; exceptions read from the indicator;
- navstats and A–B–A oscillation.

The win reason must be joined from engine stdout. The replica's 3-game replay files must be handled [G].

### 5.4 Unit tests

- Bot logic through the fake controller, with the 2023 contract.
- `SymTest`.
- Comms layout and round trip.
- The carrier economic model.
- Micro threat radii (pin r² 26).
- Tool tests on fixtures, including the eight reason strings.
- `deadcode.py` and `arm-intent`.
- A lock, and a fast/slow split. Run after every bot or tool change (CLAUDE.md rule 6).

### 5.5 Charts and owner-facing state

- **`post-block.sh`** regenerates `ELO.md`, `elo.png`, the field-score chart (the owner's favourite in bc20), the progress
  chart and a basics table. matplotlib must be installed in `tools/.venv`, or the charts rendered on the VM.
- **Promotions** update README and HANDOFF in the same commit, from one generated state source (bc24 O3).
- **Owner PROMPTS 8** asks for web access to rankings and scrimmage replays, or else screenshots in GitHub.
  **(inference)** Options, in order of safety:
  1. Always commit a generated ladder page (Markdown table plus PNG) after every autoscrim round.
  2. Serve a read-only dashboard bound to 127.0.0.1 on the VM, reached through `ssh -L`. This needs no public port, in
     keeping with rule 5.
  3. View replays in the official client run locally, after checking it makes no external calls.

### 5.6 The galaxy-lite ladder (GALAXY option B)

Build stdlib Python plus SQLite in `tools/replica/`, running on `battlecode-dev`. GALAXY estimates about 1.5 agent-days
(inference) [G].

1. **Lock down first:**
   - a dedicated uid `bcreplica` with no credentials;
   - an nftables egress drop for that uid (loopback only, metadata server 169.254.169.254 blocked);
   - HTTP on 127.0.0.1;
   - a test that fails on `battlecode.org`, `googleapis`, `challonge`, `mailjet` or `github.com` in the source;
   - `-Dbc.server.websocket=false`.
2. **Port the rating exactly:**
   - μ' = μ + 24·(S − E);
   - E uses opponents' pre-match means on a 400 scale;
   - S is the fraction of games won in the match;
   - the displayed value is μ − 1500·0.85^n, so a new team shows 0.
   - Finalize ratings in match-creation order per team with a fixed-point loop instead of Cloud Tasks. Port galaxy's 9
     finalization tests and the hand-computed tables.
3. **Matchmaking and format:**
   - `generate_4regular_graph`/`autoscrim` verbatim: rating *mean*, neighbours at most 4 ranks apart, best of 3,
     4 matches per team per round;
   - ranked matches play 3 random public maps in shuffled order, with `-Dbc.server.alternate-order=true`, in one engine
     invocation per match.
4. **Worker:** compile like the judge (5 MiB zip, zip-slip check, non-empty package, `javac -source 8 -target 8`, then
   `battlecode.instrumenter.Verifier`). Use saturn's winner regex. Galaxy's report semantics apply: RUN/OK!/TRY/ERR, a
   409-style no-op once finalized, ERR after 5 failures. Be stricter than galaxy: `[0,0]` or partial scores mean TRY, and
   stale RUN jobs are reaped.
5. **Export every game** (map, side, winner, round, reason) to `progress/games.csv`, so each match adds three BT data
   points.
6. **Policies:**
   - Use a *measurement mode* (one team per build, seeded) for decisions, and a *faithful mode* (map seeds, request rules
     on, one team receiving successive uploads) to rehearse the official ladder. Record the mode with every result [G].
   - Challenge "slightly better and worse" bots as the owner asked: a band around our rating.
   - Run autoscrims among field bots in spare cycles (C15).
   - Keep examplefuncsplayer plus one frozen build of ours as fixed anchors [G].

**Decision hierarchy:**
1. mirror SPRT, as a screen;
2. the delivery gate;
3. the band test on the BT fit with paired cells, under the ship rule;
4. the frozen roster and the replica rating, as guards and as the owner's view.

### 5.7 Benchmark acquisition and safety

- **Present pipeline:** discovery uses repository search and the forks of the scaffold, because code search returned
  HTTP 500 (864 candidates). Then a blind fetch with classification by 2023-only API names, `bench-scan.sh`
  (pattern counts only; `--show` prints only matching lines), selection by name, a content-hash dedupe (61 entrants),
  and a blind compile.
- **Add:**
  - a provenance table (repo, commit, date, package, hash);
  - two-game calibration of every new bot, so none is rated on a handful of games (uravt, [24p]);
  - a record of duds that fail instrumentation;
  - re-running the scan before any newly fetched code compiles.
- **Defence in depth:** the engine sandbox already rejects file I/O, networking, reflection, threads and `System.exit`, and
  compiles use `-proc:none`. Running the replica worker as the egress-blocked uid adds a second layer **(inference)**.
  Never read benchmark source beyond scan hits (rule 3).

---

## 6. Process rules

### 6.1 Worth keeping

| rule | evidence that it paid | years |
|---|---|---|
| A diagnostic, then a delivery gate, before any test, enforced by a refusing tool | caught three inert candidates [21]; stopped about ten arms early [24p] | bc21, bc20, bc24 |
| Pre-register the counter, gate, falsifier, branch order and a "neither" branch; never move a bar after seeing a number | stopped post-hoc rescue of a 0/60 line [26]; carol's branches missed a uniform result [25d] | bc26, bc25, bc21, bc24 |
| A closed-directions ledger with closure kind, closing number and a testable re-open condition; grep it before proposing | bob spent 24 games re-deriving a defect his own log held [25d]; re-opening on a new premise shipped relocation twice [24m]; "about one in three reopens paid" [B] | bc25, bc21, bc24 |
| Three rejects in one area mean leave the area; at least one structural attempt every four | carried from bc22 through bc24; prevents reject spirals [22][24m] | bc22, bc21, bc24 |
| A standing queue that is never idle, with at least 3 items queued | recovered 29% of idle VM time [24t]; owner rule after a 2-hour stall [25t] | bc25, bc24 |
| Benchmark and frozen roster on every accept, by script | 31 unpushed commits and a benchmark two accepts stale hid that roster gains did not transfer [25d] | bc26, bc25 |
| Arms made by script with proof that they differ; accept by script with an exact promotion score | a no-op sed caused 0/72 forfeits [25t]; ten-plus exact promotion checks passed [25t] | bc25, bc24 |
| Unit tests after every bot or tool change | caught a CSV column misalignment that reported "cumulative moves as map coverage" [21] | bc21, bc20, bc24 |
| Record every prompt verbatim; push after every commit; nothing stale stays | the owner reads the repository as a dashboard [20][24m] | bc21, bc20, bc24 |
| Record the measurement, not the explanation | "its most-repeated rule", and it cost two wrong entries [25d] | bc25 |
| Re-exec running scripts from a private copy; private class trees; kill by PID | a 450-game collation was killed by an edit [25t]; a block silently played a different bot [24t]; `pkill -f` self-kills, five in bc24 alone [24m] | bc25, bc21, bc20, bc24 |
| Games in volume only on the VM | two games on the 2 GB driver swapped and took 50 minutes [21] | bc21, bc24 |
| Resume agents rather than cold-start; short read-first indexes and grep-only archives | 77k tokens per cold start, "on the order of a million tokens" a day [25d] | bc25 |

### 6.2 Cost more than they gave

| rule or practice | cost (evidence) | years | replace with |
|---|---|---|---|
| A fixed absolute win-rate gate (60% WinPct) | drifted from about 65% to 57.5% "independent of actual quality"; accepts made below the bar [22]; abandoned [26] | bc22, bc26 | paired diffs and a power-tested ship rule |
| Self-derived peer pools, retirement, archetype forks | stale archetypes inflated 62.5% to 95.0% [26]; "mirror or saturated" [26]; the pool drifted [22] | bc22, bc26 | frozen snapshots plus the external field |
| Counting neutral accepts as progress | about 35 snapshots after iteration 28 added little; the bot reached one 1,772-line file [22] | bc22 | ship only on measured gains |
| Underpowered instruments | eight rejects and about 28 VM-hours [21]; 45 hours without a promotion [24m]; 96-game arms read noise [20] | bc21, bc24, bc20 | simulate power first |
| Locking replays of stronger bots (tier rule; `v3` ban) | the census starved [21]; the opening deficit stayed invisible until 09-14 [25t] | bc21, bc20, bc25 | study all games |
| Isolated rival lineages and tournaments between them | a joint local optimum (17-25% vs `v3`); five duplicate sessions; 1,716 lines committed under the wrong lineage [25d] | bc25 | one integrating lineage |
| Very elaborate methodology (86 METHODS entries, 11,641-line notebooks) | the most elaborate lineages reached 17-25% against darla's 56% [25d] | bc25 | a dozen core rules, enforced by tools |
| Sub-agent design panels and a rewrite design | slow, per the owner [20]; never consumed; 32% dead code [24p] | bc20, bc24 | subagents for audits and reading only |
| The mirror as sole judge | a week of mirror accepts that moved the ladder 0-25 points [20]; a series of accepts never moved the rating [21] | bc20, bc21 | the hierarchy in §5.6 |
| Stricter self-imposed readings never raised with the owner | a ban on chosen maps carried for about 4 days [24m]; "no same-day rebuilds" led to a 2-hour stall [25t] | bc24, bc25 | bring the cost and a recommendation to the owner |
| Stacking on non-inferiority | B1 ended −30 over about 1,870 pairs [24m] | bc24 | stack positive near-misses only |
| Wholesale re-tests of closed arms | 8 arms re-run, none delivered [24p] | bc24 | re-open only on a new premise |
| Long structural programmes without kill criteria | enclosure: 36 stages, then probed 4-44 [20] | bc20 | a kill criterion and an early ladder probe |
| Large narrative logs | a 590 KB log "unreadable at scale" [22]; 1.1-1.5 MB per lineage [25d] | bc22, bc25, bc24 | structured records plus a grep-only log |
| Unbudgeted filler | 80% of all games; the fit was distorted until the pair cap [24p] | bc24 | an information budget |
| The full test suite on the 2-vCPU driver | about 10 minutes per run, about 220 runs [24t] | bc24 | a fast/slow split and a lock |
| A hook requiring every commit to append to the prompt record | forced a duplicate prompt entry [env] | bcenv | a byte-prefix check only |
| Study syntheses taken at face value | over-optimistic; neither top lever shipped [24m] | bc24 | an adversarial critic, then a cheap test on identical cells |

---

## 7. Owner (human) interventions across years

### 7.1 What the owner repeatedly had to ask for

| theme | bc22 | bc26 | bc25 | bc21 | bc20 | bc24 | 2023 so far |
|---|---|---|---|---|---|---|---|
| **Keep working; don't wait; decide yourself** | "not working on anything is not an acceptable response" (after 108) | "immediately start the next iteration" | "never idle"; "you have been stopping and idling"; "not much is happening"; "no wrapping up" | blanket authorization (24); `/loop` "task check ... start a new idea" | "you don't need my approval" (44); "you will make a decision without my input and you will keep trying" (48-49); "don't wait until the next task check" (36-37) | "never stop to wait for ideas"; pick the next target without asking (157-159, 177) | "Keep going" (6); PROMPTS 1: "At no time should you stop and wait for me" |
| **Measure externally and absolutely, and keep it current** | asked for the benchmark win rate (91, which exposed the 6,815-lead bug); retirement 90% → 80% | `g_iter1` as a yardstick; vs_old_bots after every accept; a roster of every 10th, later every 5th snapshot; external benchmarks | `OBJECTIVE.md`: absolute strength; benchmark `v3` on every accept; grant `v3` replays | contest-realistic scrimmages (25); an Elo list (26-27); a fixed field (74) | "progress against a fixed roster?"; "a roster that's too strong?" (7-9); more games (10-12); calibration (80) | band refresh (184-185); a pair cap (191) | galaxy replica plus downloaded benchmarks (1) |
| **Basics: symmetry, stuck units, bytecode** | symmetry audit (126); "this can silently kill a strategy" → bytecode monitoring (127) | "Baby Rats tend to get stuck in one small region" (+28) | — | "both sides have the same behavior in a mirror test?" (62) | — | "This is basic stuff" (125-127); "the basics are the foundation" (137) | "If you don't have them right, nothing built on top of them will be effective" (1) |
| **Bolder swings, copying, rewriting** | "never going to defeat camelcase by being cautiously incremental" (33); "many high-risk projects" (108) | "a modification that lets us move more freely should be a good thing" (rescued +18) | "don't stall on ideas" | — | learn to rush, copy the tactic (39-42); a complete rewrite (48-49) | build a rush offence to spar against (6); "one unambiguous victory" (120); stack close-to-good ideas (180, 187) | "a good combination of incremental tweaks and big swings ... complete rewrite" (1) |
| **Instrument and statistics correctness** | rewrite the training algorithm to match practice (after 102) | tie rule: benchmark vs mirror goes to a peer evaluation | an overfitting audit ("progress looks flat") | "work out how many cells are needed" (20-21); "neutral against the mirror but aligns with the opponents who beat you" (71) | approve the batch BT fit (15-17); why weren't these arms accepted? (32-33) | delivery skipped (66-67); "are the shipping criteria too strict?" (186-188); unrecorded filler (72-73) | — |
| **Visibility: docs, charts, GitHub** | archive one replay per iteration (26) | "regenerate cumulative-iterations graph after every accept" | "where are the later versions?" (31 unpushed commits) | — | "ELO.md ... contradicts your statement" (19-20); chart dates, time zone (46, 50); "I frequently look at the docs in the Github repository" | "I don't see g_iter2 in github" (154-155); a stale ELO column (181); keep TACTICS current (18) | "What is the progress on the galaxy-based infrastructure?" (7); web access or screenshots (8) |
| **Use the compute well** | "use the GCloud account for compute" | — | cycle agents at about 250k context; resume them; cap at 2 drivers | "You're not running the games on claude-driver, are you?" (9, 11) | "Builds taking hours seems like quite a drawback" (71-72) | "Are you fully utilizing all the VM's CPUs?" (36) | permission to clear bc24 storage (3) |
| **Relaxing rules the agent over-read** | declined an extra "must beat the latest iteration" gate (after 37) | — | `v3` replays allowed; over-strict self-imposed rules "turning into stalls" | locked bots are about time allocation, not a ban (72) | retire the 20% replay rule (45) | chosen maps allowed for diagnostics (178); cracking a target overrides relative basics vetoes (168); remove the kill guard (182-183) | — |

### 7.2 What this says about how to behave

These are the strongest behavioural signals in the record. Each theme above recurred in at least four of the six
projects, and the 2023 charter (PROMPTS 1) already writes most of them in.

1. **Never stop, and never wait for an idea or an approval.** Every project needed this said, and 2023 has already needed
   it ("Keep going"). An idle VM or an empty queue at a task check is a failure. Keep at least three items queued, and when
   stuck, audit, re-read the principles, or take a big swing.
2. **Decide yourself, and raise only measured trade-offs.** When a rule blocks progress, bring its measured cost and a
   recommendation (bc24 O2). Do not silently keep a stricter reading, and do not ask open questions the loop can answer.
3. **Keep the external yardstick and every owner-facing artefact current and pushed on every accept.** The owner reads
   GitHub. Stale charts, unpushed commits and missing builds were caught by the owner in five of six projects. For 2023,
   that means the replica ladder view or screenshots (PROMPTS 8).
4. **Treat a short, basic owner question as an audit trigger, and answer it from code and data, never from memory.** "The
   owner's short, basic questions were the cheapest audits of the week" (bc24 O1). Several of the largest gains came from
   such questions: stuck rats (+28), symmetry ("This is basic stuff", which led to the audit), and the benchmark tally that
   exposed the 6,815-lead bug.
5. **Basics first. A broken basic is a sample of a class.**
6. **Prefer bold, measured swings to cautious neutral tweaks**: copy what beats you, rewrite when stuck, and stack
   near-misses. Pair each with kill criteria and an early field probe.
7. **Use all the compute, and protect the disks and the official infrastructure.** Run every game on the VM, keep the
   replica locked down, and push nothing to Battlecode's systems.
