# bc24-method: how the 2024 project worked, what it proved, and what to carry into 2023

Reader: the agent and owner running the Battlecode 2023 ("Tempest") practice project.
Source project: battlecode24-vibe (Battlecode 2024 "Breadwars", engine 3.0.6, one week, 2026-09-30 to 2026-10-07).
This is the latest and highest-weight prior project. All prose documents were read from the filtered reading room
(`/home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc24/`); code was read from `/home/terryvanbelle/projects/vibe/2024`.
Numbers are quoted as written in those files. Anything marked **(inference)** is my reading, not a measured fact.

---

## 1. Scope

### 1.1 Read in full (filtered copies, sizes in bytes)

Sizes in bytes: README.md 2,361; CLAUDE.md 6,107 (16 session rules with sources); HANDOFF.md 6,094; TRAINING_ALGORITHM.md
12,259; LEARNINGS.md 41,173 (lessons M, P, S, R, T, O, F with evidence); AUDIT_PROMPT.md 3,172; AUDIT_PLAYBOOK.md 31,377;
PROMPTS.md 14,383 (every owner prompt); RULES.md 7,080 (for format and provenance); BENCHMARK.md 1,761; TACTICS.md 4,716;
progress/BRIEFING.md 19,006; progress/REWRITE.md 7,970; progress/ELO.md 3,447; progress/ONSET.md 4,564; progress/SURVEY.md
960; research/REWRITE_EVAL.md 6,085; research/criteria-review-2026-10-05/verdict.md 13,176; research/CRACK.md 7,087;
research/CAPABILITIES.md 2,100; research/CAPABILITY_CENSUS.md 3,572; research/upper-tier-micro-2026-10-06/README.md 2,280.
Nearly in full: research/AUDIT-2026-10-02.md 58,317 (summary, symmetry requirement, A1-A5, every B finding, systematic tests,
appendix); research/AUDIT-2026-10-03.md 74,626 (method, summary, BOT1-BOT5, every MEAS finding, open findings, systematic
tests, appendix); research/RETEST.md 29,795 (protocol, queue, stay-closed table, correction); research/BCENV.md 14,885
(first 120 lines).

### 1.2 Read in part or skimmed

- research/REWRITE_DESIGN.md (48,790): intro, premise table, bytecode budget, identity rules, staged plan S0a/S0b. Skipped the auction and convoy detail (never built).
- research/TACTIC_LEVELS.md (66,717): headings, intro, summary. Skipped the per-tactic derivations (2024 tactics).
- TRAINING_LOG.md (231,557): headings; Phase 0 to iteration 5; the harness check; the throughput audit; the closed-directions ledger; the process correction; the 10-02 big-picture diagnosis; the ops/disk entries. The rest was searched with grep. It is an append-only log whose conclusions are restated in LEARNINGS.
- Studies (read the synthesis and/or critic only): gymhgy-study-2026-10-04 (synthesis summary and R1-R18, critic verdicts), andli28-study-2026-10-06 (synthesis opening), upper-tier-study-2026-10-07 (synthesis and critic openings), g4contact-design-2026-10-05/plan.md (opening), level-dump-2026-10-06/README.md (opening), research/premise/premise-band.txt (head).
- research/ADVICE-crossyear.md (87,454): index and sections 34-37 only (agent operation, owner, measurement honesty, tournaments). It is the cross-year digest and is covered by its own slice.

### 1.3 Not read, and why

- research/PRIOR_2020/2021/2022_2026/2025.md: digests of the earlier projects, covered by other slices.
- research/CRACK-WAFFLE/CYRIL/GYMHGY/ANDLI28.md and the study lens files: 2024 opponent-specific detail. Their conclusions appear in LEARNINGS and BRIEFING, which I read.
- research/premise/premise-colt*.txt (110 KB of raw tool output), tools/*.txt lists (data; several are 0 bytes in the filtered copy).
- Anything under `~/projects/vibe/bc24-benchmarks/` and any external bot source (hard rule 4).

### 1.4 Code read directly from /home/terryvanbelle/projects/vibe/2024

Bot: `src/bot/RobotPlayer.java`, `G.java`, `Nav.java`, `Sym.java`, `Comms.java` (schema header), `C.java` (head), `Micro.java` (lines 1-402), `Duck.java` (function list and `turn()`).
Tests: headers of `test/bot/BotTest.java`, `SymTest.java`, `AuditTest.java`, `tools/test_tools.py`.
Tools, in full: `lib.sh`, `run-match.sh`, `run-dev.sh`, `snapshot.sh`, `replay-dump.sh`, `scrim.sh`, `gauntlet.sh`, `build-engine.sh`, `bench-compile.sh`, `bench-select.py`, `eval-paired.py`, `delivery-gate.sh`, `delivery-check.py`, `band-test.sh`, `basics.py`, `elolib.py`, `elo.py` (first 80 lines), `deadcode.py`, `unit-tests.sh`, `arm-intent.txt`, `vm.sh`, `vm-run.sh`, `vm-queue.sh`, `vm-enqueue.sh`, `vm-prune.sh`, `filler-pair.sh`, `collect-fillers.sh`. Headers only for every other tool (list in section 6) and the mode list of `tools/replaydump/ReplayDump.java` (2,085 lines).

The relayed user note ("You can clear local storage from bc24 to free up disk space") grants a permission; it does not ask this reader to delete anything. This task is read-only, so nothing was deleted. For the record: the driver disk was at 89% (3.4 GB free) when I checked.

---

## 2. What worked (with evidence and effect size)

The headline: from 09-30 to 10-02 the foundation bot went from g_iter0 (1257) to g_iter1 (1652) in a day. Then about 80 builds failed to beat g_iter1. On 10-02 a correctness audit broke the plateau, and six promotions in four days took the bot from 1652 to 2113 (+461), rank 6 of 88 players (55 external bots plus 33 of our builds). Field score 88.6%; 30.5% against the 5 bots above it (LEARNINGS §1, final fit with each pair capped at 200 games).

| build | promoted | change | final-fit Elo | evidence as written |
|---|---|---|---|---|
| g_iter1 | 09-30 | stack: self-play standoff repair, float spend, carrier chase, symmetry guess, trap rings, advance | 1257 -> 1652 | mirror SPRT 27-1 discordant after 48 pairs; field judge then +246 Elo at the time. "Attribution between them is open"; TACTIC_LEVELS says three of its five parts ablate to about 0 on the band |
| g_iter2 | 10-03 | first audit's fixes (A1-A7, A9) plus observed symmetry | +169 | 234 seeded band pairs: wins 78 -> 111, net +33 (44-11), p < 0.001; capture delta +0.66 +- 0.11; confirmation on fresh seeds +29 over 239, p < 0.001 |
| g_iter3 | 10-03 | carrier stun + flag relocation (waffle crack) | +55 | pooled 473 band pairs net +22 (p 0.017), capture delta +0.25 +- 0.07 (t 3.8); vs waffle 146-94 (60.8%, p 0.001) where g_iter2 went 108-132 on the same games |
| g_iter4 | 10-04 | C.FLAG_LOST (second audit BOT1: recognise our captured flags) | +16 | pooled 473 pairs net +9 (p 0.24); capture +0.14 +- 0.05; upper tier +0.24 +- 0.06 |
| g_iter5 | 10-05 | owner's stack: centre crumbs + pick-after-move | +51 | 720 pairs net +23 (p 0.033), t_all 3.25; shipped at look 3 under the new rule |
| g_iter6 | 10-06 | relocation climb (audit BOT3(a)) | +26 | 480 pairs net +20 (p 0.045), t_all 3.44, t_up 3.34 |
| g_iter7 | 10-06 | heal hold (no heal with an enemy within dist2 10) | +144 | 240 pairs wins 136 -> 164, net +28 (36-8), p < 0.001, t_all 6.46, t_up 5.31 |

Attribution (LEARNINGS §1): plain bug fixes from the two audits gave +185 (g_iter2 +169, g_iter4 +16). Levers that audit findings motivated gave +77 (g_iter5 +51, g_iter6 +26). The contrast study's heal hold gave +144, and the waffle crack +55.

Things that worked (details and numbers for the method items are in section 4):

1. **The correctness audit of bot and measurement pipeline.** First audit: 8 agents (five lenses, two verifiers, one synthesizer), 4.2 h, 1.78M tokens, no games, 41 of 42 findings confirmed. Second: 56 of 56 reproduced. Direct gain +185, motivated +77. The first combined audit build also beat ColtG5, which targeted rush and flank builds had failed to move (seeded pairs +18 of 80, +3.1 SE): "the crack was in our own basics".
2. **Seeded paired cells with an identity control**: a byte-identical copy read 0 of 80 discordant after the fix (15-29% flips before).
3. **Delivery gates enforced by a tool**: they stopped z1hold, b2dig5, g1icpt (intercepts fired up to 88 per robot while chasers moved +0.09), g1esc2, b2rgc, g2rgh, g4contact8, g7fc, g7ring and others before each cost a 240-game band test.
4. **Three-way verdicts and a power-tested shipping rule**: 63-65% power for a +30 Elo gain at 2.0% false promotion, against 17% as written and 34% as practised; before it, 45 hours without a promotion.
5. **A two-group contrast study of behaviour rates**: with an enemy within dist2 10 we healed at 0.445 against the upper tier's 0.257 and held a ready strike at 0.196 against their 0.318, while both were near parity against the rest. The heal hold built from it gave t_all 6.46 and +144 Elo.
6. **Slowing a mechanism that cannot be stopped**: waffle re-grabbed 87% of its carriers' drops in our losses with 1-9 escorts beside each drop, so denial was infeasible (g2z2w re-grabs 21.1 vs 21.1); a stun beside the carrier plus relocation (g2cr) went 146-94 against waffle and was band-positive.
7. **Stacking positive near-misses with independent mechanisms**: g4crumb (net +4, t 1.0) + g4pick (+6 over 473 pairs, t 1.3) shipped as g4ship1 at 720 pairs.
8. **Paired 5(a) blocks on chosen cells with exact twins**: centre crumbs won 7 cells to the base's 1 on 16 chosen cells (6-0 discordant). Gymhgy replays identically under a fixed seed, so twins were reusable.
9. **A standing VM queue with an idle filler**, once collection was automatic (the VM had been idle about 29% of uptime between runs).
10. **Cheaper code with identical play**: C.REACH_FAST 0 of 234 discordant, peak bytecode 24.7k -> 23.0k; C.INIT_FAST removed a 27x27 adjacency loop that took about 18k of round 1's 22.8-22.9k bytecodes.
11. **Re-opening a closed direction on a new premise**: flag relocation, closed on 09-30 at 81 vs 84 of 110 (unseeded), shipped twice (g_iter3, g_iter6) once waffle's distance gradient gave it a premise.

---

## 3. What did not work, and closed directions

| direction | evidence as written | why it failed |
|---|---|---|
| ~80 tactic arms, ablations, sweeps and controls on the pre-audit base (09-30 to 10-02) | none beat g_iter1 | the base had broken basics (an alert on almost all game, frozen robots, a stale registry, guessed symmetry) and the paired harness was not seeded, so verdicts were mostly noise |
| Stacking on non-inferiority (bases B1, B2, B3) | B1 -30 over about 1,870 filler pairs vs g_iter1 (-1.8 SE); final fit b1v2 1626, b1z2b 1652, b2fs 1638 vs g_iter1 1652 | small negative layers accumulate; dropped after the 10-02 diagnosis |
| Economy and level-sum arms (8) | five stopped at 5(a) (g4farm, g4farm3, g4builder twice, g7dig, g7bank); g4farm2 INCONCLUSIVE at 96 cells; g4econ2 Cyril-delivered but band-neutral (net +3); g7fc fires rarely | the gap was misattributed: the andli28 level gap was mostly heal XP (-27.6 of -35.3 levels) plus attack XP lost in jail; digs explain about 13 levels. g7bank's design projected +22 levels and delivered +7 |
| More offensive presence (re-grabs, relays, convoys, dives, late all-ins) | b2rg 11-26 (carrier deaths +5.9 SE); g3escrg2 convoy: pickups 20 vs 12.7, carrier deaths 15.8 vs 8.8, k/d 2.13 vs 3.11; g4relay2 +2% at 96 cells; g4contact8 screening -2.7 SE | "presence at enemy flags is an outcome of winning the fight, not a lever"; more attempts traded more carriers |
| Saving robots alone | g7ehp cut deaths 12% (377 vs 429), band look 1 capture t -1.12; g7kite pooled t 0.32; g7spawn raised enemy captures 1.00 -> 1.50 on 24 cells | the deaths-to-captures link is near zero; g7kite's premise check had forecast P(ships alone) of about 0.05 |
| Target-only gains | g7ehp +28 over 240 pairs vs andli28 (+3.3 SE) but band-neutral; g4gym1 band net +1 | levers specific to one target did not climb the ladder; about 15 arms against Cyril and 10 against Gymhgy cracked neither, and both fell to band-wide promotions |
| Rewrite (8-agent decision-layer design, research/REWRITE_DESIGN.md) | S0a premise passed, S0b sensor built (identity confirmed), consumer never built; 528 lines of unused Track sensor became 18.8% of g_iter3 | escalated to architecture before checking basics (F1); the crack and the audit overtook it |
| Re-testing closed arms wholesale (RETEST, PROMPTS 150) | 8 closed arms re-run on g_iter2; none delivered | the second audit later read most failures as INCONCLUSIVE (missed by less than 1 SE) |
| Large studies' top-ranked levers | andli28 synthesis: FINAL_COMPLETE +2.2 pp x 0.65, ENGAGE_HP +2-4 pp x 0.4; neither shipped | syntheses were over-optimistic; critics were better calibrated |
| Micro v2 (smooth tile scoring) | exact pairs 1-25, 1-26 | refuted |
| Specialisation, cohesion, hold-a-line | sp7 12-30; gr8 4-18 (worse with dose); hold line 0/7, 1/7 | refuted |
| Upgrade order (2024) | capture-first 14-33 (p about 0.005), heal-first 22-26 | ATTACK first and HEALING at r1200 were load-bearing |
| Retreat threshold | RETREAT_HP 0:85, 150:83, 300:84, 500:82, 700:80 of 110 | monotone in the wrong direction: "a symptom, not a knob" |
| Aggression dose | e1aggr 83/110, e2aggr 81/110 vs control 84 | "the attack/heal gap vs top bots is a symptom" |
| Territory-aware micro (g6terr) | 5(a) failed: paidKillShare rose on 5 of 12 cells, mean moved -0.086 | where kills happen follows the game's flow, not a tile preference (R5) |
| Mirror gate for field-facing changes | relocation's mirror read 36-40 after 160 pairs | "the mirror cannot price a defence against rushes"; g1drift doubled ground against g_iter1 and gained none on the band |
| Full-field 110-game instrument | every arm within +-4 of 84/110 | half the block went to bots we always beat; replaced by the 20-bot band |
| Dam and float trap ablations | ab1nodam 20-16, ab3nofloat 19-20 | VOID: the mechanisms almost never fired (bank below 700 on 64 of 75 maps) |

---

## 4. Method lessons

### 4.1 The loop (TRAINING_ALGORITHM.md, as it stood at shutdown)

Objective: absolute strength against the external field (ladder rating and expected score against every ladder bot). Beating our own builds is a means. "Two instruments disagreeing is a finding to surface, not a verdict to pick."

Phase 0 (day one):
1. Rules digest with engine provenance for every mechanic; one starter-bot game read for its ending.
2. Headless bare-JVM runner, parallel gauntlet, per-game fresh seed recorded, timeout per game, dud and exception detection, private class trees per run, guards that refuse rather than fall back.
3. Determinism check: same seed twice identical, different seed different.
4. Replay reader with per-round metrics, event window, one robot's life, board at a round, logs, bytecode, navigation; unit tests on synthetic replays.
5. Bot iteration 0: turn loop with a bytecode monitor (overrun = round changed during the turn; near miss > 90%), per-robot RNG from the id, decision-point log tags, constants file, unit tests on pure logic, snapshot tool.
6. External field: scripted discovery, blind compile, select each repo's final bot by name, calibrate each bot with two games.
7. Charts and handoff regenerated by one post-block command.
8. Identity control on every tool path that produces verdicts: a byte-identical copy reads 0 discordant pairs. Re-run when a tool changes.
9. Basics battery on every build and test block.

The loop proper:
1. Select a target from the rotation (own defects; tactics the field beats us with; block census; capability gap; tactic levels).
2. Trace the motivating replay before hypothesising; check a second game against a different opponent.
3. Pre-register in the log: mechanism, decision counter, reachability, trigger frequency, price, deciding instrument, gate, falsifier, and for numeric changes a dose ladder with a byte-identical zero arm.
4. Implement one change behind a switch; tests pass (dead-code and switch-intent checks); 0 overruns; basics hold.
5. Diagnose, no shortcuts (owner PROMPTS 66-67): (a) one logged game where the mechanism can fire, against the incumbent on the same seed; (b) a delivery mini-block (about 24 band cells): the mechanism fires in >= 90% of games and its signature reaches target (for a copied tactic, >= 50% of the gap to the opponents'). `band-test.sh` refuses without the PASS file. A failed delivery is never judged on wins.
6. Gate. 7. On accept: snapshot, archetype regression, ladder blocks, post-block, update TACTICS/ledger/handoff, commit, push. 8. On reject: restore src/bot byte for byte; ledger entry with the closing number and a re-open condition; near-misses stay available as stack parts.

Rotation balance: after 3 consecutive rejects in one area, leave it; at least one structural swing every 4 attempts. Plateau escalation, in order: correctness audit first; then ablate accepted features; API/engine sweep; re-read field games; re-read cross-year advice; jointly necessary pairs; structural attempt; rewrite.

Hyperparameters: SPRT p0/p1/alpha/beta/batch/cap 0.50/0.58/0.05/0.05/16/320 pairs; ladder block 48 games; band = 20 nearest bots; filler block 40 games; near-miss 90% of the bytecode limit; concurrency cores-1 on the compute machine, 1 on the session machine.

### 4.2 Instruments and what each cannot see

| instrument | answers | blind to |
|---|---|---|
| mirror gate (candidate vs incumbent, seeded paired cells) | is this change better than what it replaces | anything both builds share; anything only the field does |
| sparring archetypes (our own one-trick bots copying a field tactic) | does the change survive or exploit that tactic | everything else |
| ladder (scrims vs the external field, batch Bradley-Terry) | are we stronger | map/side noise at small N |
| replay reader | why one game went the way it did | statistics |

The 2024 evidence that this matters: the mirror could not price a field-facing defence (relocation 36-40); g1drift gained ground against g_iter1 and nothing on the band; arch_rush won its first diagnostic game and then went 5 of 32.

### 4.3 Gates and statistics

**Pairing.** Each cell is (opponent, map, side, engine seed); both builds play it; only discordant pairs count. SE(net) = sqrt(gained + lost); for example +33 on 55 discordant = +4.4 SE. Facts the project measured:
- Without a shared engine seed, identical code flipped 15.2% of cells (26-29% against ColtG5). Arms sat at the same level (14.9-19.7%), so the tallies were noise (audit B2).
- With the seed shared, identity is exact (0 of 80), but **arms that change behaviour still disagree with the control on 14-38% of pairs** (band arms mostly 16-20%), because any change re-draws the games (MEAS2). On 234 band pairs, 1 SE is about 6.5 net games, about 2.8 win points, about 20 Elo; only effects of about 40 Elo were visible.
- About 12-13 Elo per band win point (criteria verdict).
- Per pair, wins carried 2.2-5.6x less information than the capture difference. When most cells are foregone conclusions (we won about 9% of upper-tier cells), wins barely move. Use the most informative per-pair number.

**Mirror screen**: SPRT on discordant pairs (H0 0.50, H1 0.58, alpha = beta = 0.05, batches of 16); at the cap, sign test p < 0.01 with >= 12 discordant decides; p < 0.10 = provisional. An overrun or new exceptions voids a candidate (void, not rejected).

**Delivery gate** (`tools/delivery-gate.sh`, `tools/delivery-check.py`): checks like `median:col>=x`, `mean:`, `fire:col>0>=0.9`, `rel:col<=0.7` (arm vs ratio x base, paired on shared cells) and `nw:` guards. After MEAS1 the verdict is three-way: rel PASS only when the margin is at least 1 paired SE beyond the bar, FAIL only at 2 SE short, else INCONCLUSIVE, and the gate re-runs itself on twice the cells (24 -> 48 -> 96). Fewer than 18 shared cells is INCONCLUSIVE. `nw:` guards FAIL at 2 SE worse and are INCONCLUSIVE when the worst plausible drop exceeds 20%. Never close a line on INCONCLUSIVE. Why: 16 of 28 FAILs and 7 of 15 PASSes had sat within 1 SE of their bar; g2cr's PASS cleared its bar by 0.00 SE; b1z2b read 9.2 and then 4.83 on the same 24 cells.

**Shipping rule** (owner PROMPTS 186-188; `eval-paired.py --look N`):

| look | pairs | ship if | stop (park) if | otherwise |
|---|---|---|---|---|
| 1 | 240 (seeds 1-2) | t_all >= 3.0 and net >= 0 | t_all < 0.5 and t_up < 0.8 | seeds 3-4 |
| 2 | 480 pooled | ship test | t_all < 1.0 and t_up < 1.3 | seeds 5-6 |
| 3 | 720 pooled | ship test | everything else | - |

Ship test = (t_all >= 2.3 or t_up >= 2.6) and net >= 0. t = capture-difference delta / SE. The upper-tier list is frozen when the arm is registered. Simulated: a null arm ships 2.0%, a harmful one <= 0.2%, a +0.14 capture gain 63%. The incumbent's control on seeds 5-6 is played once per incumbent and reused; each promotion gets a fresh control on fresh seeds and a band refresh. The verdict judged a looser wins test (one-sided p 0.10) as a mistake: it triples false promotions (8.2%).

**Regression guard**: all-cell net <= -2 SE stops an arm.

**Basics battery** (`tools/basics.py`): absolute bars (symWrong = 0; symmetry decided by r201 in >= 95% of setup-decidable games and by r400 in >= 90% of the rest; 0 overruns; 0 exceptions) plus relative checks against a control (stillPost, kill/death, trapsHit, gathered400, floating crumbs) that fail only when worse by more than 2 SE. A basic the census does not measure FAILs ("not measured"). Owner exception (PROMPTS 168): an arm that passes its pre-registered victory read against the ladder target is not vetoed by a relative check its tactic pays by design; absolute bars still stop it. Known weaknesses: k/d as an unpaired mean of ratios overstated a veto about 1.7x (MEAS6; use the paired log((k+1)/(d+1))); five independent checks fail a neutral arm about 11% of the time.

**Re-test rule** (RETEST.md): exact-harness verdicts stand unless a fixed defect changed what the switch does; unseeded verdicts are diluted, not biased (|z| >= 2.5 stands, |z| < 2 is no evidence). One second attempt only after a trace explains the first failure, on a fresh seed. Beware regression to the mean: on one 24-game block the cached base won 21% against 43% overall, so every arm "gained".

**Reading rules**: never read a running batch; never move a bar after seeing a number; diff game by game and read the shape (one-directional on one map or side = real; scattered = noise); first looks and small blocks regress toward zero (g4relay2 +54% captures on 8 cells, +2% at 96; g4gym1 +2.5 SE at 400 pairs, +0.4 SE at 1,880).

### 4.4 Ladder and Elo design

- Ladder games against external bots are scrimmages: random map from the corpus, random side, fresh engine seed (the 4th cell field), rotating opponents (never the same twice in a row; each at most ceil(N/pool) times per block). External bots never play each other. Diagnostics may choose maps and sides (PROMPTS 178) but never enter the ladder.
- Pool = the band: the 20 rated bots nearest the build's rating on either side (`elo.py --band 20`). Never-played bots get a two-game calibration block. `scrim.sh` refuses to fall back when `progress/games.csv` is missing (a predecessor project once challenged the wrong bots for days on a silent roster fallback).
- Rating = batch Bradley-Terry by minorise-maximise over all our games (`tools/elolib.py`), Elo scale, weak prior (one virtual win and loss against a 1500 anchor), each of our builds its own player, repeated (pair, map, seed) cells counted once. Inherited reason: a sequential K=32 Elo depended on play order, and 96 easy calibration games once lifted "us" from rank 65 to rank 4.
- Iterate to tolerance and warn if not converged (MEAS11: the 3,000-iteration cap left every rating 30-44 points low on 18,949 rows; convergence needs about 24,000 iterations).
- Cap each pair at 200 games (PROMPTS 191): about 1,500 filler games against andli28 (a 30% matchup) pulled g_iter7 from 2150 to 2116, below NotLLeon, which it beats head to head. 200 games pin a pair's win rate to about +-3.5 points.
- Grade = rating +- 95%, rank, field score (expected score against every ladder bot, one game each), and score against the bots rated above. Withdraw a submission whose interval falls below the previous submission's rating. Compare builds only within one fit: g_iter1 was quoted at 1756, 1853, 1811 and 1762 before settling at 1652.
- Calibrate bots rated on few games: uravt rated 2274 +- 348 on 26 games and fell to 1920 after 40 more; it had been left out of the band.
- Target ladder (owner PROMPTS 120, 157-159, 177): one target at a time, usually the bot just above; when it ranks below us, pick the next without asking. Count a target beaten when the ladder ranks it below us. A pre-registered 60% bar kept work on ColtG5 after the ladder had ranked g_iter2 above it, until the owner declared it beaten.
- 45,389 ladder games in the week; 36,440 (80%) were filler games, mostly target matchups.

### 4.5 Process rules and why each exists (CLAUDE.md)

| rule | why (source) |
|---|---|
| Games in volume only on the VM; the driver plays one diagnostic game at a time | driver is 2 vCPU / 2 GB; a DefaultSmall game takes 2-4 min there |
| Push after every commit; record every prompt verbatim, except /loop prompts | owner follows from GitHub; PROMPTS 171-172 |
| External bots' source never read | practice must approximate a contest (PROMPTS 1) |
| Ladder = random scrimmages; diagnostics may choose (PROMPTS 178 relaxed an over-reading of PROMPTS 1) | choosing cells for the ladder would bias the rating |
| No gate before a diagnostic shows the mechanism firing | arms were judged on wins without delivering |
| Unit tests after every change to the bot or any tool | owner PROMPTS 1 |
| Bot changes need no approval; never stop to wait for ideas | owner PROMPTS 1 |
| Nothing stale stays | owner found stale charts and columns (PROMPTS 154, 181) |
| No 2024 post-mortems | practice rule |
| Replays have no robot stdout: counters in 64-char indicator strings | engine fact |
| TACTICS.md updated after every ladder run and comprehensive | owner standing order (PROMPTS 18, 21) |
| A standing VM queue; never launch an experiment beside a running one | 29% VM idle between runs (PROMPTS 36) |
| Delivery mini-block mandatory; band-test refuses without PASS | PROMPTS 66-67: 10 of 11 adoption arms had skipped delivery |
| One ladder target at a time; next without asking when it ranks below | PROMPTS 73, 120, 157-159, 177 |
| Basics first: battery on every block; a failed basic stops work above it; symmetry decided by observation | PROMPTS 127, 137 |
| Incumbent named, frozen copy kept, src/bot defaults play as the incumbent | identity checks need an exact reference |

### 4.6 Owner (human) interventions and what each corrected

| PROMPTS | owner said (gist) | what it corrected | outcome |
|---|---|---|---|
| 6 | if self-play can't show a rush defence, build a rush offence and spar against it | mirror blind spot | sparring archetypes (arch_rush, arch_rush10) became 5(a) opponents |
| 9, 154-155, 181 | field-score graphs; "I don't see g_iter2 in github"; stale ELO column | front page and state files stale (g_iter2's 600 games filed under the arm name) | promotions update README/HANDOFF in the same commit (O3) |
| 17-22 | are T1-T4 really the only tactics?; update TACTICS every ladder run; call it Adoption/Neutralization | survey too narrow (all four from one opponent); offence/defence framing confused the agent | TACTICS grew to 19 rows; survey regenerated by post-block |
| 36 | are all VM CPUs used? | 29% VM idle between runs | standing queue + idle filler |
| 56 | is there a way to tell elementary tactics from infrastructure-heavy ones? focus on basics | tactics adopted without their prerequisites | TACTIC_LEVELS (TL-1); "10 of 11 adoption arms never reproduced the tactic" |
| 66-67 | you went to ladder tests without reproducing the behaviour; honour step 5, no shortcuts | step 5 had shrunk to "a counter fires" | delivery gate tool and band-test refusal |
| 72-73 | tell me about the idle-filler blocks | 17 filler blocks (about 2,000 games) never recorded | paired filler + collect-fillers.sh at every task check |
| 92 | permission to delete what we no longer need, never anything on GitHub | disks filling | replay pruning |
| 111-113 | step back: why no progress past g_iter1? | the agent answered "architecture ceiling" and launched a rewrite | later judged a failure mode (F1) |
| 120 | pick one strategy; one unambiguous win over a higher-ranked bot | diffuse band-wide work | the crack method (CRACK*.md) |
| 125-127 | tell me about the symmetry check; "This is basic stuff"; do an audit; add tests | symmetry guessed (wrong on 32.4% of map-sides) while an observation routine sat uncalled | the audit that ended the plateau (+169) |
| 137 | the basics are the foundation; when stuck, check the basics | | CLAUDE rule 15, basics battery |
| 150 | revisit discarded approaches now that bugs are fixed | | RETEST: 8 arms, none delivered |
| 157-159, 177 | ColtG5 is defeated, move on; pick the next opponent yourself; open the list if lines run out | agent held to its own 60% bar after the ladder had ranked us above | target rule 14 |
| 168 | cracking an opponent overrides relative basics checks | relative vetoes blocking a crack | exception to rule 15 |
| 169, 173 | give me a prompt that captures the audit; make ADVICE.md a short year-free paragraph | method not portable | AUDIT_PROMPT.md, AUDIT_PLAYBOOK.md |
| 178 | you may choose maps and sides against benchmarks | the agent had carried its own stricter reading for about 4 days without raising it | centre-crumb lever measured on chosen cells, half of g_iter5 |
| 180, 187 | stack two close-to-good ideas | positive near-misses parked | g_iter5 |
| 182-183 | run the band test anyway; remove the kill guard | a kills guard blocked mechanisms that trade bodies | g4ship1 shipped with k/d level |
| 184-185 | why so few games against uravt? | band missed an under-sampled bot | band refresh at each promotion |
| 186-188 | are the shipping criteria too strict? | rule had 17% power at realistic effect sizes | new rule, 63-65% power |
| 191 | cap pair weight in the fit | filler games distorting the ladder | PAIR_CAP 200 |

LEARNINGS O1: "The owner's short, basic questions were the cheapest audits of the week." O2: each time a rule's measured cost was shown, the owner relaxed it; the agent should bring the cost and a recommendation and ask, rather than silently keep a stricter reading. O4: praise went to the audits, the ColtG5 crack and the overnight climb; the asks were to carry the method forward.

### 4.7 How the agent went wrong (LEARNINGS F1-F5 and related)

- **F1, escalating to a redesign before checking basics.** The answer to PROMPTS 111 named an "architecture ceiling" and launched an 8-agent rewrite whose consumer was never built. The binding terms were basic bugs; `Sym.observe` had no callers.
- **F2, deferring a broken basic because its consumer looked minor.** On 10-01 at 15:55 UTC a research note recorded that `Sym.observe` is never called and moved it out of the work block. 26 hours later the owner asked about symmetry. One broken basic is a sample of a class: audit at once.
- **F3, not questioning the yardstick** when positive arms kept falling short: about 45 hours without a promotion until the owner asked about the criteria.
- **F4, building a study's ranked levers before chasing its top open question.** The andli28 study named the vertical-symmetry penalty (0.195 vs 0.366 win rate, z -2.9) as its highest-value question; four other levers were built first and none shipped. Slice a target's games by map symmetry and side on day one.
- **F5, `pkill -f` / `pgrep -f` matching the issuing shell's own command line**: five times in the week; a remote `pkill -f "vm-queue"` killed its own ssh shell; two `until ! pgrep -f` waits spun about 10 minutes.
- Others: a rule kept only in prose was followed in letter, not spirit (P2); "default-equivalent" refactors were assumed, not verified (an "inert" trap rewrite read 18-32 discordant and contaminated three arms); the agent's own extension of the ladder rule was carried 4 days unraised (O2); a correlational split was used to price a fix (g_iter1's wrong symmetry "cost" 25.0% vs 39.9% wins, yet the fix went 63-57 and net -6 on the band; M7).

### 4.8 Research method: studies, critics, premise checks

- **Studies as workflows**: several lens agents (maps, their offense, our offense, fights/economy, setup), a synthesis, and an adversarial critic. Lesson R6: syntheses were over-optimistic; critics were better calibrated but over-trusted between-map correlations (the Gymhgy critic demoted centre crumbs on Spearman -0.06 between maps, yet the paired chosen-cell test won 6-0 discordant and the arm shipped).
- **Within-map comparisons**: win/loss contrasts computed within map (harmonic weights, permutation of labels within map) because map identity confounds everything. The Gymhgy critic found side mattered (+5.3 points within map, perm p 0.029) once the sample grew, against the lens's "side p 0.75" on the first 499 games.
- **R5, outcome-shaped statistics are consequences, not levers**: "92.4% of Gymhgy's captures are unopposed" because a relay's last leg always is; "third flag lost 0% in wins" is true by definition.
- **R3, a mechanism can deliver its proxy and still lose**: b2rg raised re-grabs +9.1 SE and went 11-26; b3own raised levels +16.5 SE and went net -13. Estimate the proxy-to-outcome link first; pair a signature bar with an outcome guard.
- **R4, condition delivery on the trigger**: g7fc fired in 17 of 17 games where its trigger held, but its delivery averaged over all games and missed its bar.
- **R7, coin-flip tie-breaks in our own policy are randomised experiments**: the kite score's random ties (about 2.5k decisions per HP bin in upper-tier games) gave causal estimates by HP band and set g7kite's HP < 700 gate.
- **Premise checks from replay truth before code** (REWRITE_DESIGN S0a; `tools/premise.py`): pre-registered bars P1-P6 on offline-reconstructed beliefs, with routing rules (fail -> close with no bot code).
- **Two-group contrast** (S3, above): the single most productive study design of the week.

---

## 5. Bot architecture and the basics, mapped onto 2023

### 5.1 Architecture of src/bot (2024)

- `RobotPlayer.java` (42 lines): one static loop per robot. Records the start round; runs `G.startTurn()`, the symmetry scout, `Duck.turn()`, then `Sym.update()` with spare bytecode; catches `GameActionException` and `Exception` into `G.exceptions`; after the turn, an **overrun is "the round changed while our turn ran"**, a near miss is more than `C.NEAR_MISS_BC` (22,500 = 90%), and `G.maxBc` keeps the peak; `G.endTurn()` writes the indicator; `Clock.yield()`.
- `G.java`: per-robot globals; xorshift RNG seeded from the robot id ("so identical code on both sides never shares a sequence"); `nearest()` breaks ties by the robot's own RNG, never by array order; the indicator string puts the note first, then counters, because the engine cuts it at 64 chars.
- `C.java` (275 lines): every tunable constant and every switch, each commented with the measurement or reason that set it. Every new arm is a `static final` switch, off by default, so javac drops its code and src/bot at defaults plays exactly as the incumbent.
- `Comms.java`: the shared-array schema documented in the header, one purpose per slot (64 x 16 bits; locations as x*64+y+1, 0 = none). Index claiming in slot 0; enemy flag registry; own-flag alerts; symmetry bitmask in slot 16 (AND-merged by every robot).
- `Duck.java` (1,473 lines): one class for all 50 robots with roles by creation index (defenders idx 0-2, scouts 3-5, builders, rushers). `turn()`: upgrades -> spawn -> symmetry hints -> sense -> carry -> setup -> pickup -> fight branch (with reachability filter `Micro.engageable`) -> defend -> heal -> crumbs -> field target -> pickup after move -> spend float.
- `Micro.java`: kite-and-strike by scoring all 9 tiles each fight turn (carrier chase 20000, loose flag 19000, engage 10000 - threats, advance 5000, else kite/hold: -1000 per threat plus a 50 bonus for dist2 11-20, i.e. "out of reach but close enough to strike next turn"). Strike first if something is in reach; heal if the action is still free, unless `C.HEAL_HOLD` and an enemy is within dist2 10.
- `Nav.java` (115 lines): greedy step, then bug wall-following with per-robot handedness (`left = id & 1`), stall exit after 20 turns without progress (flips handedness), map-edge flip once per call (A9), water fill when stuck, and the A7 fix: only a real goal change (moved more than dist2 8) resets bug state.
- `Sym.java` (258 lines): symmetry by observation (details below).
- Tests: `test/bot/BotTest.java` with a hand-written fake RobotController (shared array, vision disk, walls, water, robots, flags, cooldowns), `SymTest.java` (300 random symmetric synthetic maps through the real pruning code), `AuditTest.java` (one test per audit finding), `ContactTest.java`. Plain `main` with exit codes, no JUnit. Arms whose switches are off are re-tested on a sed-copied tree with the switches on, because javac drops `static final false` code (a hook once broke and every test still passed).

What hurt: by g_iter3 about 900 of 2,807 lines (32%) were dead (528 of them the unused Track sensor), comments asserted behaviour the code lacked, and 22 static counters were write-only (MEAS14, MEAS5). One giant switch-laden class made the inert-identity discipline possible but accumulated dead weight.

### 5.2 The basics and how each maps onto 2023

**Symmetry (the defect that ended the plateau).** g_iter1 narrowed candidates with broadcast hints from rounds 1-3 and then picked ROT > FX > FY in a fixed order; a terrain check existed and was never called; it was wrong on 32.4% of (map, side) pairs. The fix (`Sym.java`, `Sym.OBSERVE`):
- candidates as a bitmask (1 rotation, 2 flip x, 4 flip y), never emptied (a contradiction is counted, not applied);
- geometry at start (an image of our spawn centre cannot fall in our own spawn zone);
- spawn-zone images: one sight of the image tile confirms or eliminates a symmetry;
- per-robot terrain memory as `long[]` bitsets (seen, wall, spawn, setup-seen, dam); each newly seen tile is compared with its remembered image under every surviving symmetry; only immutable features are compared;
- `collapseEquivalent()`: candidates that predict the same enemy spawn set count as decided;
- `scoutTarget()`: the nearest tile where surviving candidates disagree; 3 scouts walk there while undecided;
- information the engine gave away: an enemy flag's id was its spawn centre's location index, and one id decided the symmetry in 418 of 468 cases (audit A2);
- published through the shared array (AND-merge);
- the offline bar: an exhaustive scan of all 78 engine maps and both sides showed 268 of 298 wrong-symmetry cases are decidable before r201 from immutable evidence; the other 30, on 15 maps, need one post-setup sighting. The bar became symWrong = 0 and "decided within the bound", not the build's current rate.

2023 mapping **(inference)**: the same design ports almost directly. HQ positions are the anchors (images of our HQs under each candidate are the enemy HQ candidates); walls, clouds, currents, wells and islands are immutable features to compare; an enemy HQ sighting decides. Three 2023 differences matter. (1) Writes to the shared array are allowed only within r^2 9 of our HQ, r^2 20 of our amplifier or r^2 4 of our anchored island, so eliminations must be held in robot memory and published at the next write opportunity; 2024's "every robot, even jailed, writes every turn" does not hold. (2) Bytecode is 10,000 for most units (12,500 carriers, 20,000 HQ) against 25,000 in 2024, so the per-tile memory compare must be budgeted, and the HQ (20k, stationary, can write) is the natural place for heavy symmetry work. (3) Before relying on it, write the offline scan over every 2023 engine map and both sides to compute the decidability bound, and make "decided within the bound, never wrong" an absolute basics bar from day one. Also run the "information the engine gives away" lens on the 2023 API (ids, indices, orderings).

**Movement.** Bug nav with handedness, stall exit, and the two audit fixes. Defects found only by the audit: A7 (bug state reset whenever a moving target moved, so chasers could not round a wall), A9 (edge ping-pong, 12-25 episodes a game on some maps), A4 (any visible enemy took the whole turn even behind a wall: 16-36% of enemy-in-view robot-rounds frozen on walled maps, one robot for 164 rounds), BOT3 (relocation targets on walls/water: 23.5% unreachable; carriers move every second turn, so a 12-"turn" stall was 6 moves), BOT8 (fill then not stepping onto the filled tile, about 90 lost steps a game). Measures: `--navstats` (moves per robot-round, still%, ABA oscillation), stillPost, lockedIdle, edge-stall episodes.
2023 mapping **(inference)**: currents push units at end of turn and clouds slow cooldowns 20%, so the nav needs a passability/cost model that includes currents (a current tile can undo a step), and launchers move every second turn (move cooldown 20 vs decrement 10) while carriers' cooldown grows with load: count stalls in movement-ready turns, not turns (the BOT3(b) lesson). Port the reachability filter (do not let an unreachable visible enemy take the turn) and the stall/edge fixes as day-one tests.

**Combat/micro.** The heal hold (+144 Elo) was a tempo fix: keep the action for a strike when an enemy is close. The upper-tier study found the remaining gap was "tempo while not ready": after a strike we stayed in enemy reach 0.252 of the time vs 0.111 for the upper bots, because the kite score counted threats out to dist2 10, so stepping out of reach earned nothing. Target choice, finishing wounded robots and follow-up were at parity. The andli28 study found our step-in converted at half its rate, and we stepped in at 300-699 HP on 39.8% of one-step decisions vs 15.1%.
2023 mapping **(inference)**: launchers (attack r^2 16, vision r^2 20, move cooldown 20) are the analog of the 2024 duck. The lessons that transfer: measure "ready strike held near an enemy", "ended a recharge turn in enemy reach" and "stepped in below X HP" as census columns from replays; compare them across the two groups (bots that beat us, bots we beat); prefer a policy that shoots then steps out of reach and steps in only when ready. Mine the bot's own coin-flip tie-breaks for causal estimates before writing micro arms.

**Economy.** In 2024 the one economic lever that shipped took free resources without taking actions from fights (centre crumbs after the dam opened: our r201-400 collection had been 838 crumbs vs Cyril's 3,572). Eight other economy/level arms failed, mostly because the gap was misattributed. Census columns per phase and per half (gathered200, gathered201to400, bank at fixed rounds, floating crumbs) made the comparisons possible.
2023 mapping **(inference)**: economy is far more central in 2023 (carriers, three resources, anchors, and a tiebreak on islands, anchors, elixir, mana, adamantium). Lesson S4 applies directly: break any economy gap down by source and phase (well type, trips, carrier idle, load, distance, HQ income of 6 Ad + 6 Mn every 5 rounds) before building against it, and check "floating" resources at fixed rounds as a basic.

**Exploration and enemy localisation.** g_iter1 first saw an enemy flag at r1674 on Tunnels because the own-flag alert never lapsed and parked the army (A1). firstFlagSight and firstEnemySide were census columns. Under the rewrite design, a per-object track predicted toward its destination was built and scored against replay truth before any consumer existed.

**Communication.** Lessons from the audits: document each slot's meaning in the header and test the layout from the constants (MEAS15: the layout test omitted live slots 49-57); expire everything that can go stale (A5: "carried by us" never expired when our carrier died; A6: a dropped flag's tile outlived its return; BOT10: a 5-round carrier sighting expiry); an alert must mean what the schema says (A1 fired on any enemy seen near the flag and was fresh in 1,057-1,686 of 1,800 post-setup rounds, switching off every defender); check every documented slot meaning as a contract against replay truth. 2024 replays stored the shared array every round, so `--comm` could audit comms offline.
2023 mapping **(inference)**: with write locations restricted, staleness is the main risk: a value written at the HQ can sit for many rounds. Every slot needs a round stamp or an expiry rule from day one. Verify whether .bc23 replays store the shared array per round; if they do, port the `--comm` mode and replay contracts.

**Bytecode.** Overrun = round changed during the turn; near miss > 90%; maximum per turn. Pitfalls: a feature that deliberately fills spare bytecode (Sym.update ran until 2,500 were left) saturates the near-miss metric, so 92% of turns at 22.5k+ were those fills and a real near miss (a 23,591-bytecode relocation scan, 95% of the limit) hid among them (MEAS7). Round 1 is expensive (INIT_FAST). Measure near misses before any deliberate spare-bytecode work, and keep a per-turn worst case table for each new mechanism (REWRITE_DESIGN 2.8 is a good template, using the engine's MethodCosts).
2023 mapping: limits are 2.5x tighter for most units, so this is a first-week basic, not a late polish.

**Exceptions.** Every exception is caught and counted, and a caught exception abandons the rest of the turn. Pitfall: the census's "exceptions" column counted engine DIE_EXCEPTION, which only fires on player load failure, so the absolute bar could never fail (MEAS7). Read the bot's own counter from the indicator string.

**Indicator strings and logs.** 2024 replays carried no robot stdout, so counters went into 64-char indicator strings, and 68-75% of strings sat at the cap, cutting off the note and later counters (MEAS5). Put the note first, keep only live counters, and assert the length in a unit test. 2023: verify whether .bc23 replays carry robot logs and the indicator limit; design the counter layout from that.

---

## 6. Tools and infrastructure inventory

All paths are under `/home/terryvanbelle/projects/vibe/2024/tools/` unless noted. Quality reflects the audits and what I read. Changes needed for 2023, in general: engine 3.0.15 built for battlecode23, `.map23` maps and `.bc23` replays, Java 8 (same JDK 8 path works), repo path `~/projects/vibe/2023`, benchmark directory `bc23-benchmarks`, the VM's REMOTE_REPO and benchmark paths.

### 6.1 Engine, runner, field

| tool | purpose | quality | verdict for 2023 |
|---|---|---|---|
| `build-engine.sh` | clone battlecode24 at a tag, patch `LiveMap.getSeed()` to honour `-Dbc.game.seed`, fix rotted jsi dependency, build with JDK 8, stage engine.jar, libs, maps, VERSION, map list | good; maven artifacts returned 403 so source build was required | **adapt**: battlecode23 repo and tag for 3.0.15; verify the seed hook location in the 2023 engine; map extension; dependency fixes may differ |
| `lib.sh` | JDK/engine classpath, `run_game` (headless bare java, wall-clock timeout, replay save, seed), `parse_result`, `compile_src`, `engine_busy` (ps/awk, not pgrep -f) | good | **adapt** paths only |
| `run-match.sh`, `run-dev.sh` | one game; run-dev compiles to a private per-process tree (parallel diagnostics once collided) | good | **adapt** (trivial) |
| `gauntlet.sh` | parallel games from CELLS or opponents x maps x sides; re-execs from a private copy (editing a running bash script corrupts it); refuses to recompile a class tree in use; seed in replay names; dud/timeout/unknown detection; results.csv with seed | good after B13/MEAS3 fixes | **adapt**: .bc23 names, result parsing for 2023 engine output |
| `scrim.sh` | ladder block: band pool from elo.py, random map/side, rotation, engine seed as 4th field from a second RNG stream, refuses missing history | good | **steal**, change map list |
| `bench-compile.sh` + `benchcompile/BenchCompiler.java` | compile every external repo blind, logs to files, counts only, manifest.tsv | good, rule-enforcing | **adapt**: classify by 2023-only API names |
| `bench-select.py` | choose each repo's final bot by package name only | good | **steal** |
| `bench-roster.py` | roster table in BENCHMARK.md | fine | adapt |
| `snapshot.sh` | freeze src/bot as a package by sed-renaming `package bot;` | good | **adapt** (2023 bot will have per-unit files; same rename) |
| `diag-batch.sh` | step-5(a) games in parallel, capped at 8 (24 at once starved sshd) | good | **adapt** |

### 6.2 Measurement and statistics

| tool | purpose | quality | verdict |
|---|---|---|---|
| `tools/replaydump/ReplayDump.java` (2,085 lines) + `replay-dump.sh` (compile cached by source hash) | replay to text: summary, `--every`, `--metrics`, `--from/--to`, `--robot`, `--map-at`, `--logs`, `--bytecode`, `--near90`, `--navstats`, `--flags`, `--comm`, `--capabilities` (census), `--survey`, plus many 2024 study modes | the project's microscope; dozens of columns | **rewrite** against the .bc23 flatbuffer schema; keep the mode list as the spec; add 2023 census columns (resources by type and phase, carrier trips, launcher micro rates, island/anchor timeline, symWrong/symDecidedRound) |
| `capability-census.sh` | one census row per team per game from `--capabilities` | needed K-of-M checks (MEAS3) | adapt |
| `eval-paired.py` | paired evaluation by tier (all, upper, rest), wins sign test, capture-difference delta +- SE, identical share, `--look` shipping decision | good | **adapt**: pick 2023's most informative per-pair number (see takeaway 4) |
| `delivery-gate.sh` + `delivery-check.py` | 24-cell delivery block vs cached base, three-way verdicts, auto-extension 24 -> 48 -> 96, DGPOOL/DGTAG/DGMAPS | good after MEAS1/MEAS13 fixes; base cache still shared across gates (MEAS4) | **steal** logic; draw a fresh seed per gate |
| `band-test.sh` | 2 seeds x 120 games on the band; refuses without PASS | good; PASS keyed by name, not code hash (MEAS10) | **steal**; add code-hash check |
| `basics.py` | basics battery | good; k/d unpaired (MEAS6) | **adapt** (2023 columns; paired log-ratio) |
| `sprt.py`, `paired.sh`, `mirror.sh`, `compare.py` | SPRT, seeded paired mirror cells, game-by-game diff with shape | good | **steal** |
| `arm-deltas.py` | paired capability deltas per census column | good | **steal** |
| `filler-pair.sh`, `collect-fillers.sh`, `filler-tally.py` | idle filler on shared seeds; driver collects, records, refits, tallies | worked once collection was automatic | **adapt** |
| `statlib.py`, `onset.py`, `correlate.py`, `polarity.py`, `derived.py`, `test_metrics.py`, `scrim-study.sh/.py`, `onset-merged.sh` | correlation with outcome by round; onset (first round a metric predicts the result); noise floor | good statistics; ONSET was stale at shutdown | **steal** statlib/onset; adapt the column lists |
| `tactics-survey.py`, `capability-summary.py` | opponent tactic survey, capability census summary | fine | adapt thresholds and columns |
| `premise.py`, `recall-d0.py`, `contact-d0.py`, `defense-profile.py`, `fill-origin.py`, `stun-check.sh`, `side-indsum.sh` | 2024 study-specific analysers | good as patterns | **skip** (keep the pattern: analysers that studies rely on live in the repo with tests) |
| `log-scan.sh` | log extraction | dead: can never produce output (MEAS17) | **skip** |

### 6.3 Ladder and records

| tool | purpose | verdict |
|---|---|---|
| `elolib.py` | batch Bradley-Terry (MM), weak prior, dedupe by (A, B, map, seed), pair cap 200, convergence warning, field score | **steal as-is** (year-agnostic) |
| `elo.py` | ladder table, ELO.md, band/pool selection, build grade | **steal** |
| `scrim-record.py` | append games.csv, refuses self-play as grading | steal; add code hash |
| `post-block.sh` | fetch, record, refit, re-tier, study, onset, charts | adapt |
| `field-score.py`, `progress-chart.py` | field score and rating charts with a diminishing-returns projection | **steal** |

### 6.4 Compute (GCE VM)

| tool | purpose | verdict |
|---|---|---|
| `vm.sh` | VM name/zone/project (battlecode-dev2, us-west2-a, tvanbelle-vibecode), ssh helpers, `ensure_vm`, `vm_games` with a bracket pattern | **adapt** REMOTE_REPO and benchmark paths; the VM is stopped and reusable |
| `vm-run.sh` | detached run after sync (`setsid nohup`, with a note on why `cd X; CMD &`) | steal |
| `vm-queue.sh` | standing queue: pending jobs in order, filler when idle, flock, STOP file, runs from a private copy, exit code captured correctly (B12) | **steal** |
| `vm-enqueue.sh` | submit a job or set the filler | steal |
| `vm-prune.sh` | replay retention above 80% disk; keeps listed builds, gate bases, newest 25 filler runs per kept build, diagnostics 24 h | **steal**; key retention to consumers |
| `vm-sync.sh`, `vm-collect.sh` (no replays unless REPLAYS=1), `vm-stop.sh` (refuses while games run), `vm-tail.sh` | sync and fetch | steal |

### 6.5 Tests and checks

| tool | purpose | verdict |
|---|---|---|
| `unit-tests.sh` | compile bot + tests, run every *Test main, re-run arm tests on sed-copies with switches on, deadcode, metric and tool tests | **adapt**; add a lock (overlapping runs raced on 10-06); about 10 minutes on the 2-vCPU driver |
| `deadcode.py` | uncalled methods and unread constants | **steal**; extend to write-only fields, constant returns, switch-dead code |
| `arm-intent.txt` + its check in `test_tools.py` | asserts every arm's switch values in the built source | **steal** (a moved comment once made an arm run with its switch off) |
| `test_tools.py` (1,031 lines) | synthetic-input tests for every tool | adapt; much is 2024-specific |
| `test/bot/*Test.java` | fake RobotController, SymTest over synthetic symmetric maps | **adapt the pattern**; for 2023, run property tests over every real engine map |

Not in this repo: anicolao/bcenv (research/BCENV.md) has no runnable environment; its only tool is a git hook enforcing an append-only PROMPTS.md. **Optional**: it could guard the prompt record.

---

## 7. Pitfalls and gotchas that cost time

| pitfall | cost as stated |
|---|---|
| Paired tools drew a random engine seed per build until 10-02 23:00 UTC | identical code flipped 15-29% of cells; "about 2.5 days of gained/lost tallies were mostly noise" |
| Seeding read as making arms exact | arms still disagree 14-38% of pairs; RETEST assumed seeded re-tests were much stronger (false) |
| Point-bar delivery checks | 16 of 28 FAILs inside 1 SE, including 3 of the 5 Cyril closures that "defined" a plateau |
| Shipping rule never tested for power | 17% power; 45 hours with no promotion |
| Tactic arms on a broken base | about 80 builds over two days, none accepted |
| Symmetry routine written but never called | wrong on 32.4% of map-sides; noted and deferred for 26 hours |
| "Default-equivalent" refactor not verified | read 18-32 discordant as an "inert" control; contaminated c4bank, e1aggr, e2aggr |
| Arm switch silently off (moved comment broke the sed) | g1sym verification 4 ran with its switch off; caught only by bytecode equal to g_iter1's |
| Test hooks compiled out | ContactTest passed while javac had dropped its hooks (static final false) |
| Indicator string over the 64-char cap | 68-75% of turns cut; notes and counters lost; parking defect invisible |
| Replay names without the seed | dropped 1.6-2.5% of band games, 11.5% of ColtG5 filler games, 12% of g_iter3 census rows; voided g4crumb's 96-cell gate |
| Results keyed by package name | g_iter2's 600 games filed under g1basics, invisible to the charts |
| Driver disk full 10-02 01:56 UTC | 2.6 GB of replays; again at 98% later |
| VM disk full 10-02 12:12 UTC | 49 GB disk, 35 GB replays; runner spun 18 minutes on failing fillers; queue logged every job "exit 0" because `$?` held a date substitution's status |
| First prune rule | deleted 5(a) replays an hour after they ran, and all 880 g_iter5 filler replays a queued premise check needed |
| Unconverged Elo fit | ratings 17-27 points low (first audit), later 30-44 low |
| Filler games dominating the fit | 80% of ladder games; g_iter7 pulled 2150 -> 2116 until the pair cap |
| 17 filler blocks never recorded | about 2,000 games until the owner asked |
| `pkill -f` / `pgrep -f` self-match | five incidents; waits spun about 10 minutes |
| Unit suite on the 2-vCPU driver | about 10 minutes, run about 220 times (session figure); about 37 hours in total by my arithmetic **(inference)**; no lock, overlapping runs raced |
| Parallel compile race | 2 of 234 band games lost |
| 24 diagnostic games at once on 8 vCPUs | sshd starved for minutes; capped at 8 |
| e2-standard-8 unavailable in us-west1-b on 09-30 | `ZONE_RESOURCE_POOL_EXHAUSTED`, retried every 5 minutes; moved to us-west2-a |
| Official maven engine artifacts 403 | engine built from source with a rotted jsi snapshot dependency |
| Engine tiebreak uses unseeded `Math.random()` | the only nondeterminism; examplefuncsplayer ignores the seed (static Random(6147)) so its mirror games are identical across seeds |
| A driver game | 2-4 minutes on DefaultSmall; about 19 minutes on large maps |
| Self-imposed ban on chosen maps for diagnostics | carried about 4 days, never raised with the owner |
| Cached delivery base reused across gates | one base won 0.50 vs a population 0.30 (z +2.1), biasing every arm on it the same way |
| Census counts blank when the event is absent | arms that removed an event got no credit (MEAS8) |
| Basics bar on exceptions structurally 0 | the bar could never fail (MEAS7) |
| Delivery cache without a tag | a pool block could overwrite the band PASS file (caught twice) |
| Stale documents at shutdown | rating and target record disagreed across README, HANDOFF, CLAUDE rule 14 and a memory file |

---

## 8. Top 15 takeaways for the 2023 project, ranked by expected value

1. **Build the measurement before the first arm.** Patch the 2023 engine to honour a per-game seed, put the seed in every cell and every replay name, key every result by (code hash, opponent, map, side, seed), and prove the verdict path with an identity control (byte-identical copy reads 0 discordant) on every tool path and opponent pool. In 2024 the missing seed made 2.5 days of verdicts noise.
2. **Run the correctness audit (AUDIT_PROMPT.md / AUDIT_PLAYBOOK.md) on the first working bot and at every plateau, bot and measurement together.** Five lenses (dead code; rules and engine API including information the engine gives away; shared state; in-game behaviour from replays; measurement pipeline), adversarial verifiers that default to "not real", every finding with a fix and a regression test; fix tool defects first, then one combined build of bot fixes behind switches, judged on exact pairs and confirmed on fresh seeds. In 2024 this produced +185 Elo directly and +77 indirectly of the +461 climb, after 80 failed builds.
3. **Make the basics measurable absolute bars from day one: symmetry decided by observation and never wrong, 0 overruns, exceptions counted by the bot.** Compute the symmetry decidability bound offline over every 2023 map and side, port Sym.java's bitmask/memory/collapse/scout design, and budget it for 10k-bytecode units and 2023's restricted write zones.
4. **Choose the most informative per-pair statistic and simulate the shipping rule's power before relying on it.** 2024's wins carried 2.2-5.6x less information than the capture difference; the rule on the right statistic doubled power (17% -> 63-65%) at 2.0% false promotion. For 2023, candidates are the end-of-game tiebreak vector (islands held, anchors placed, elixir, mana, adamantium) or an island-count difference integrated over rounds **(inference; measure which has the best signal per pair before adopting)**.
5. **Enforce the delivery gate with tools: no band test until the mechanism fires in >= 90% of games and its signature reaches target, with three-way verdicts (PASS 1 SE beyond, FAIL 2 SE short, else extend).** Condition the signature on the trigger, pair it with an outcome guard, and do not use a kills guard on mechanisms that trade bodies by design.
6. **Run the ladder as 2024 ended it**: batch Bradley-Terry to convergence, pair cap 200, band of the 20 nearest bots, two-game calibration of new bots, band refreshed with fresh seeds at each promotion, builds compared only within one fit, and targets counted beaten when the ladder ranks them below us.
7. **Ship on the band; use single targets as diagnostics.** Target-specific gains (g7ehp +3.3 SE against andli28) did not climb; band-positive levers found through target studies did.
8. **Run a two-group contrast study early**: behaviour rates in the bots that beat us vs the bots we beat, kept only where we differ from the first group and sit at parity with the second. It produced the week's largest single effect (t 6.46, +144 Elo). For 2023 launchers, start with ready-strike-held, ends-turn-in-reach and step-in-by-HP rates **(inference)**.
9. **Read how a stronger opponent actually wins, and if the mechanism cannot be stopped, slow it** (waffle: carrier stuns plus relocation, 146-94). Slice every target's games by map symmetry and side on day one (the vertical-map penalty, 0.19 vs 0.38, was found late and never explained).
10. **Do not stack on non-inferiority; do stack positive near-misses with independent mechanisms and test the stack as a new arm.** B1-B3 drifted below the incumbent; g4ship1 shipped.
11. **Check the premise before building**: estimate the proxy-to-outcome link (b2rg's +9.1 SE re-grabs lost 11-26), mine the bot's own coin-flip tie-breaks for causal effects, and treat outcome-shaped statistics as consequences. Discount study syntheses; run a critic; test even demoted levers cheaply on identical cells.
12. **Keep the compute busy and the disk safe**: standing VM queue with an idle filler whose results are collected automatically and whose games are budgeted by information; replay retention keyed to the analyses that still need the files; a disk check before writes; exit codes that fail loudly. Reuse the 2024 VM tooling almost as-is.
13. **Enforce every rule with a tool that refuses**: arm-intent assertions, dead-code check, inert-refactor identity check, switch-on test copies, a lock on the unit-test runner, PASS files keyed by code hash, K-of-M counts in every census. Every prose-only rule in 2024 was breached at least once.
14. **Write the .bc23 replay reader early and treat it as the core instrument**, with census columns for every basic and every live mechanism's firing counter, tested on fixture replays. Verify on day one whether .bc23 replays carry robot stdout and the shared array; if not, design indicator strings with the note first and a length test.
15. **Work with the owner the 2024 way**: answer "how does X work?" from the code and data, never from memory; treat a basic question as an audit trigger; bring a blocking rule's measured cost with a recommendation instead of silently keeping a stricter reading; update README/HANDOFF/progress in the same commit as a promotion; record every prompt verbatim.
