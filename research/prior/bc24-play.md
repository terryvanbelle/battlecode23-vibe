# bc24-play: gameplay, tactics, ladder and benchmark experience of the 2024 project

Reader's report for the Battlecode 2023 practice project. Source: the 2024 project (`battlecode24-vibe`, one week,
2026-09-30 to 2026-10-07). This is the most recent prior project and carries the most weight. I read its documents only
from the filtered reading room `/home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc24/`, where 2023-tagged
blocks had been removed. Code and scripts I read directly from `/home/terryvanbelle/projects/vibe/2024/`. I read no
external competitor source. Numbers are quoted as the 2024 documents give them. Anything marked **(inference)** is my own
reading, not a measurement in the 2024 record. The 2023 game facts used for mapping come only from the task brief.

---

## 1. Scope

### 1.1 Read in full (filtered reading room unless noted)

| file | size (bytes) | notes |
|---|---|---|
| `TRAINING_LOG.md` | 231,557 (2,238 lines) | read end to end; the primary record |
| `LEARNINGS.md` | 41,173 | the week's lessons with evidence; written at shutdown |
| `research/TACTIC_LEVELS.md` | 66,717 | TL-1 procedure, capability statuses, why each adoption arm failed |
| `research/CRACK.md` (ColtG5), `CRACK-WAFFLE.md`, `CRACK-CYRIL.md`, `CRACK-GYMHGY.md`, `CRACK-ANDLI28.md` | 7,087 / 10,864 / 20,412 / 11,409 / 5,398 | how each ladder target was attacked |
| `TACTICS.md` | 4,716 | **filtered copy is much shorter than the repo copy (27,810)**: only T1-T12 and the TL-1 table survive. T13-T19 are reconstructed here from TRAINING_LOG and LEARNINGS |
| `BENCHMARK.md` | 1,761 | **filtered copy is 1.8 KB vs 61 KB in the repo**: the rules and discovery numbers survive, the roster table does not |
| `progress/SURVEY.md`, `ELO.md`, `ONSET.md`, `REWRITE.md` | 960 / 3,447 / 4,564 / 7,970 | ladder table, per-arm paired statistics, onset table (a g_iter2 snapshot) |
| `research/BCENV.md` | 14,885 | review of anicolao/bcenv (a design repo with no runnable code) |
| `TRAINING_ALGORITHM.md`, `RULES.md`, `PROMPTS.md`, `HANDOFF.md`, `CLAUDE.md`, `README.md` | 12,259 / 7,080 / 14,383 / 6,094 / 6,107 / 2,361 | loop, engine-checked 2024 rules, every owner prompt, state at shutdown |
| `research/REWRITE_EVAL.md`, `CAPABILITIES.md`, `criteria-review-2026-10-05/verdict.md`, `upper-tier-micro-2026-10-06/README.md` | 6,085 / 2,100 / 13,176 / 2,280 | shipping rule and its power analysis; the study behind the biggest single micro gain |
| `research/PRIOR_2020.md` | 39,258 | the 2024 session's digest of 2020 |

### 1.2 Read in part or skimmed

- `research/PRIOR_2021.md` (39,690): about two thirds, including the gate history, the ladder rules and what worked.
  `PRIOR_2022_2026.md` (32,028): head, the season-2 method summary and the "day-one rules" list. `PRIOR_2025.md` (36,710):
  the verdict and the method section. These are the 2024 session's own summaries of prior years. Other slices cover those
  years directly, so I note below only what 2024 took from them.
- `research/upper-tier-study-2026-10-07/synthesis.md` (51,349): the first 80 lines (findings and ranking).
  `research/andli28-study-2026-10-06/synthesis.md` (35,379): the first 70 lines. `research/RETEST.md`: the first 30 lines.
  `REWRITE_DESIGN.md`: headings only. `AUDIT-2026-10-02.md` and `AUDIT-2026-10-03.md`: headings and finding titles.
  `progress/BRIEFING.md`, `CAPABILITY_CENSUS.md`, `level-dump-2026-10-06/README.md`: first 25-40 lines.
- `research/ADVICE-crossyear.md` (87,454): I diffed it against `readroom-no2023/advice/ADVICE.md` and did not read it.
  It is an older copy of the same file. It lacks only the §29 "audit correctness first" paragraph that the 2024 project
  later added to ADVICE.md (PROMPTS 173), and it carries a prompt-record tail. **It adds nothing beyond the advice guides.**

### 1.3 Skipped, and why

- The lens reports of the four multi-agent studies (gymhgy, andli28, g4contact design, upper-tier) and the criteria-review
  sub-analyses (power, history, alternatives). Their syntheses and the TRAINING_LOG carry the conclusions.
- `AUDIT_PLAYBOOK.md` and `AUDIT_PROMPT.md`. These describe method, which is outside this slice's focus. Their content is
  summarised in LEARNINGS R1 and TRAINING_LOG.
- `research/premise/*.txt`. These are raw premise-check outputs.
- The data `.txt` files under `tools/` in the reading room. Many are 0 bytes in the filtered copy (`ladder-bots.txt`,
  `band.txt`, `roster.txt`, `upper-tier.txt`). Rule 1 forbids reading the repo versions, so I did not.

### 1.4 Code read (repo, direct)

- Bot `src/g_iter7/`: the final incumbent. `RobotPlayer.java` and `G.java` in full; `Nav.java` in full; the `Comms.java`
  schema header; the structure and comments of `Sym.java`; from `Micro.java`, `bestTarget`, `tryHeal` and `fight`; from
  `Duck.java`, `turn`, `buyUpgrades` and `trySpawn`, plus the full method list. Line counts: Duck 1,242, Micro 451,
  Track 528, Sym 258, Comms 227, C 181, Nav 115, G 101 (total about 3,100).
- Tools `tools/`: the header comment of every script. In full: `elolib.py`, `scrim.sh`, `lib.sh`, `bench-compile.sh`,
  `bench-select.py` and `vm-queue.sh`. In part: `eval-paired.py`, `delivery-check.py`, `basics.py`, `build-engine.sh`,
  `unit-tests.sh`, and the mode list of `replaydump/ReplayDump.java` (2,085 lines).

---

## 2. What worked (with the evidence as written)

### 2.1 The ladder climb in one table (final fit, LEARNINGS §1)

The final fit uses 45,389 games, with each pair counted at most 200 times. "Rank" is out of 88 players: 55 ladder bots
plus 33 of our builds.

| build | promoted | what changed | rating | rank | field score | vs higher | step |
|---|---|---|---|---|---|---|---|
| g_iter0 | 09-30 | foundation bot | 1257 | 53 | 52.2% | 9.5% | - |
| g_iter1 | 09-30 | symmetry guess, trap rings, advance rule, float spending, carrier chase | 1652 | 41 | 73.0% | 16.1% | +395 |
| g_iter2 | 10-03 | first audit's basic bug fixes (A1-A7, A9) + observed symmetry | 1821 | 27 | 79.0% | 20.4% | +169 |
| g_iter3 | 10-03 | carrier stun + flag relocation V2 (the waffle crack) | 1876 | 19 | 80.8% | 19.3% | +55 |
| g_iter4 | 10-04 | C.FLAG_LOST (second audit, BOT1) | 1892 | 18 | 81.4% | 20.7% | +16 |
| g_iter5 | 10-05 | stack: centre crumbs + pick-after-move (BOT4, BOT5) | 1943 | 15 | 83.1% | 25.4% | +51 |
| g_iter6 | 10-06 | relocation climb (BOT3(a)) | 1969 | 13 | 83.9% | 25.6% | +26 |
| g_iter7 | 10-06 | heal hold (TACTICS T16) | 2113 | 6 | 88.6% | 30.5% | +144 |

The LEARNINGS attribution: "Plain bug fixes from the two audits gave +185 (g_iter2 +169, g_iter4 +16). Levers that audit
findings motivated added +77 (g_iter5 +51, the owner's stack, and g_iter6 +26). The heal hold found by a contrast study
gave +144 and the waffle crack +55." Between g_iter1 (09-30) and the first audit (10-02), "about 80 builds (arms,
ablations, sweeps and controls) followed, and none beat g_iter1."

Ratings quoted at the time ran high. g_iter2 read 1918, g_iter3 1977, and g_iter7 peaked at 2150: about 100 points above
the final fit for g_iter1-g_iter3 and 30-40 points above it for g_iter5-g_iter7 (LEARNINGS §1, M8).

### 2.2 Items that worked, by size of effect

1. **The correctness audit and its basic bug fixes (g1basics -> g_iter2, +169 Elo).** Band test, 2 seeds, exact
   seed-paired against the seeded g_iter1 control: "all 234: wins 78 -> 111, gained 44 lost 11, **net +33 (sign p <
   0.001)**", capture-difference delta +0.66 +- 0.11. On confirmation seeds: net +29 (p < 0.001), +0.68 +- 0.10. Pooled
   over 4 seeds (473 pairs): gained 79, lost 17. The fixed defects:
   - **A1 (critical):** the own-flag alert fired on any enemy seen near a flag. It was "fresh in 1057-1686 of 1800
     post-setup rounds", switched off every defender and parked ducks on the flag tile for up to 1,466 rounds. After the
     fix, false alerts fell from 305-2324 to 0-81 a game.
   - **A2:** enemy flag ids encode the exact enemy spawn-centre index and were never decoded.
   - **A3:** the symmetry was guessed by fixed order, and was wrong on 32.4% of map-sides.
   - **A4:** any visible enemy took the whole turn, even behind a wall. 16-36% of enemy-in-vision robot-rounds were
     locked idle on walled maps.
   - **A5/A6:** the enemy-flag registry went stale for up to 1,393 rounds.
   - **A7:** navigation reset its bug state whenever the target moved.

   Against ColtG5, the build changed nothing ColtG5-specific and still went 46/80 = 57.5% where g_iter1 managed 35.0%
   (paired +18, +3.1 SE). CRACK.md: "The crack was in our own basics."
2. **The heal hold (g6heal -> g_iter7, +144 Elo, the largest single-look effect of the week).** C.HEAL_HOLD: "no heal with
   an enemy within dist2 10 unless the target carries a flag". The premise came from a contrast study. With an enemy
   within dist2 10 we healed 0.445 of the time against the upper tier's 0.257, and held a ready strike 0.196 against
   their 0.318. Against the rest of the band both were near parity (0.467 vs 0.399, 0.244 vs 0.242).
   - Band look 1, 240 seeded pairs: "wins 136 -> 164, gained 36, lost 8, net +28 (sign p < 0.001); capture delta +0.57 +-
     0.09 (t_all 6.46); upper 31 -> 50 (24-5), +0.72 +- 0.14 (t_up 5.31)". It shipped at look 1.
   - Its control on the band went 514-206 (71.4%), against g_iter6's 413-307 (57.4%). These were played on different look
     seeds, so they are not paired.
   - The micro study (`research/upper-tier-micro-2026-10-06`) read 15 replays. Against the upper tier only, "ready-and-
     striking on contact 0.27 vs 0.44", and "their hits landing on a robot still on cooldown 0.49 vs 0.36". We healed 1.50
     times per attack to their 0.98, a heal costs 30 cooldown, and 9.8% of their attacks landed on our robots that had
     just healed.
3. **Initial stack g_iter1 over g_iter0 (+395 final fit; +246 at the time).** The stack repaired a self-play standoff:
   every g_iter0 mirror game ran to r2000 with 13k crumbs floating. It added an advance rule, float spending, trap rings,
   carrier chase and a symmetry guess. Mirror SPRT: "ACCEPT 27-1 discordant after 48 pairs". Field: 81-29. Losses before
   r600 fell from 26 to 6. Attribution was never settled: "Three of its five parts ablate to about 0 on the band"
   (TACTIC_LEVELS §1.3).
4. **The waffle crack (g2cr -> g_iter3, +55).** Carrier stun (C.CARRIER_STUN: a duck with a carrier within dist2 18 builds
   a stun within dist2 8 of it, ahead on its way home) plus flag relocation V2.
   - Against waffle, pre-registered victory read over 240 games on six fresh filler seeds: "g_iter3 (g2cr code) **146-94
     = 60.8%, p = 0.001**; g_iter2 on the same cells 108-132 (45.0%)". Paired net +38.
   - Band, pooled over 473 pairs: net +22 (sign p 0.017), capture delta +0.25 +- 0.07 (t 3.8).
   - The mechanism: waffle loses fights 2:1 but "re-grabbed 87% [of its drops of our flags] in our losses". Denying the
     re-grab was "physically infeasible": 1-9 waffle robots stood within dist2 8 of each drop. "Slowing worked": a frozen
     carrier "delays waffle's captures more than it prevents them, and the time goes to our offense."
5. **Stacking two near-misses (g4ship1 -> g_iter5, +51).** g4crumb (C.CRUMB_STEP + C.POST_SETUP_CRUMBS: take the centre
   crumbs the dam was hiding) plus g4pick (C.PICKUP_AFTER_MOVE: a pickup is legal after a move; fight() had struck first
   and blocked the pickup). Look 3 pooled 720 pairs: "t_all +3.25, t_up +1.98, net +23 (sign p 0.033) -> SHIP".
   - Against Gymhgy, paired filler: +84 over 1,200 pairs (+3.9 SE), about +7 points.
   - g4crumb alone against Gymhgy: +30 over 640 pairs (+2.3 SE). On chosen centre-crumb cells it won 7 vs 1 (6-0
     discordant), with crumbs r201-400 at x1.9.
6. **Flag distance by a greedy climb (g5climb2 -> g_iter6, +26).** C.RELOC_CLIMB: "the carrier steps each ready turn to the
   visible passable tile farthest from the nearest live enemy spawn centre, within 20 tiles of its spawn centre ... and
   drops at a local maximum". The fixed-spot relocation it replaced had 23% unreachable spots.
   - Premise against Gymhgy: chains on our flags "converted 0.50 within 20 tiles ... and 0.13 at 36-47 tiles".
   - Band delivery: flagDistMean +2.53 tiles, enemy captures 1.83 -> 1.33.
   - Pooled 480 pairs: t_all 3.44, t_up 3.34, net +20 (sign p 0.045).
7. **FLAG_LOST (g3lost -> g_iter4, +16).** The engine removes a captured flag. Before this fix, "defenders, rings, alerts and
   respawns serve an empty home in 82% of Cyril games". Pooled 473 pairs: upper +0.24 +- 0.06 (t 3.8), all +0.14 +- 0.05
   (t 3.1), net +9. A small bug fix produced a real, measurable gain.
8. **Two load-bearing defaults, found by ablation and sweep (pre-audit, unseeded, so read as leans):**
   - Buying ATTACK first: "capture-first 14-33 (p about 0.005)", heal-first 22-26.
   - HEALING at r1200: CAPTURING instead "cost late captures" (g2up3: capturedLate 0.33 vs 0.44, kills -6.6% = -2.9 SE).
   - Combat stun traps "only lean load-bearing" (16-26, p about 0.16).
9. **Cheaper bytecode at identical play.** C.REACH_FAST marks attack-range tiles once per enemy instead of testing every
   enemy at every reached tile. Its band run was "identical to g_iter2 on all 234 cells", and the per-game peak fell (for
   example Divergent 21.0k -> 17.7k). A refactor proven inert by an identity read is safe to fold in.
10. **The fixed symmetry as a foundation.** On its own the symmetry repair was neutral: 63-57 head to head, net -6 on the
    band, because g_iter1 used symmetry in only two places. It still had to exist before anything could use destinations,
    such as carrier interception or the relocation climb's "farthest from the nearest live enemy spawn centre".

### 2.3 How each opponent was "cracked" (or passed)

| target (dates) | baseline | what decided it | outcome |
|---|---|---|---|
| ColtG5.Goob_final (10-02 to 10-03) | g_iter1 85-135 (38.6%); 102 of its 135 wins came from the more-flags tiebreak at r2000 | trip study: 56% of its captured trips were unopposed. A counter-raid screen (rush and flank builds, 37 identical cells) reached its flags (pickups x12-30) but never converted. The real fix was our own basics (g1basics). | 71/120 = 59.2% (p 0.055), one win short of the pre-registered 60% bar. The owner declared it defeated (PROMPTS 157). Final: g_iter7 46-2 |
| winkelmantanner.waffle (10-03) | g_iter2 10-14; all 14 losses by three captures | distance gradient (our flags under 20 tiles from its spawn captured 88%; 28-36 tiles, 50%) plus re-grab chains. Chain-breaking by attack failed (g2z2w re-grabs 21.1 vs 21.1); slowing it with carrier stuns plus relocation worked | **victory read passed: 146-94, 60.8%, p 0.001**; shipped band-wide as g_iter3 |
| CyrilSharma.finalBot (10-03 to 10-04) | g_iter3 ~30% | defence study: its kill box is symmetric, it lays no trap ring, and "its offense decides games" (no Cyril capture: we win 84%; any capture: 18%). Its economy built 475 traps to our 247, at about 54 crumbs per stun to our 77 | about 15 arms, none cracked it (g4econ2 stopped for futility at 120 pairs). Passed later by band-wide promotions: final g_iter7 35-13 |
| Gymhgy.v10official (10-04 to 10-06) | g_iter4 43% | its group size at the grab predicts the chain (12+ robots: 0.36-0.54 capture rate); the recall premise was refuted (route R3); the local fight was not decisive | about 10 arms, none cracked it alone. Centre crumbs +30/640 (+2.3 SE) and the climb +24/520 moved the matchup. Passed by g_iter7. Final 39-9 |
| hsmalladi, andrewgopher | 3-21 on band seeds (g_iter3 era) | never targeted directly | passed by band-wide promotions |
| NotLLeon.v3 (10-06) | 6-6 | none | level at shutdown (2113 vs 2113); g_iter7 leads 48-40 head to head |
| andli28.v9_USQuals_angle (10-06 to 10-07) | g_iter7 14-34 | loss study: kill share 0.37 in every phase; our mid-HP robots step in 40% of the time vs its 15%; our step-in strikes kill within 2 rounds 22.5% vs its 43.8% | **not cracked**: 1739-4109 (30%). g7ehp (step-in gate) was +28/240 against it (+3.3 SE) but band-neutral. Vertical-symmetry maps: 0.187 vs 0.383 on rotational, the top open lead |

The method shared by all targets is in §4.4.

---

## 3. What did not work / closed directions (with evidence)

### 3.1 Everything built on the broken base (09-30 to 10-02)

None of about 80 builds beat g_iter1. Many of those verdicts were later called "diluted, not biased", because pairs were
unseeded and identical code flipped 15-29% of cells (RETEST.md). The main closures from the 2026-10-01 ledger:

| direction | measurement | why it failed (as recorded) |
|---|---|---|
| flag relocation (first version) | 81 vs 84/110; 20-21 vs arch_rush10 | the engine broadcasts every uncarried flag within dist2 100, so hiding cannot delay raiders. It came back later with a premise (distance gradient) and shipped twice |
| flag relay (T3) | 81 vs 84/110 | defective: 219 drops per capture vs the opponents' 3-7; the dropper re-picks its own drop |
| setup digging (T4) | 84, 82 vs 84; later b3own band net -13 | starved (median 0 digs). Once delivered: "every dig crumb is a stun not built" (stun400 -20.8, -14.6 SE) |
| bank through setup, trap in the fight (T5) | 82, 82 vs 84 | the bank was spent by r250 either way |
| aggression dose (T6) | e1 83, e2 81 vs 84 | a symptom, not a knob |
| retreat threshold (T8) | full ladder 0:85, 150:83, 300:84, 500:82, 700:80 | more retreat was monotonically worse |
| more defenders / wider alert / fortress / flag-tile stun | 9-25, 12-31, 16-29, 19-23 (paired SPRT vs the rush partner) | "Bodies pulled home cost more than they save" |
| attack specialisation (never-heal attackers) | sp3 19-22, sp5 18-17, sp7 12-30 | fewer healers meant more deaths and a lower level sum; attack mastery arrives too late |
| smooth-score micro v2 | **1-25 and 1-26** in paired mirror SPRT | "The lexicographic engage/kite micro is far better than this smooth scoring" |
| cohesion (GROUP_MIN) | gr4 20-23, **gr8 4-18** | "Cohesion hurts in proportion to how hard it is enforced: tempo and spread win flags" |
| flank raid squad | fl6 19-21, fl10 20-23, fl15 2-16 (1 seed) | a squad bolted onto local rules takes bodies from the army |
| hold a front line (S1) | stage A 0/7, 1/7 wins | a static line "does not stop an advancing opponent" and we lost the tiebreaks too |
| forward drift in the hold branch | g1drift80 band 11-24 (p 0.041), kills -62 | "buys early ground that is gone by r300 and costs fights" |
| upgrade order heal/capture first | 22-26, 14-33 | ATTACK first is load-bearing |

### 3.2 Offensive presence (closed repeatedly; LEARNINGS S6)

"Arms that added offensive presence (grabs, re-grabs, relays, escorts, dives, late all-ins) failed again and again. More
attempts traded more carriers. Presence at enemy flags is an outcome of winning the fight, not a lever."

- b2rg (re-grab anywhere): re-grabs +4.8 (+9.1 SE), but carrier deaths +4.8 (+5.9 SE), captures -0.04, kills -37. Band
  11-26.
- g3escrg2 convoy against Cyril: pickups 20 vs 12.7, carrier deaths 15.8 vs 8.8, band k/d 2.13 vs 3.11. Paired filler net
  +8 over 240 (+1.0 SE).
- g4relay2: looked like +54% captures on 8 cells, then +2% at 96 cells (-2.0 SE).
- g4contact8 (in-fight dive toward a convoy chain): screening got worse (-2.7 SE).
- The interception family (g1icpt, g1camp, g1icamp, g2icamp, g3camp, g3camp2, g4pred): intercepts "fire constantly but do
  not put more ducks near carriers". "The unopposed carriers ... are the ones nobody sees", and "local rules that only see a
  fight do not reach the carriers nobody sees". Our ducks had an enemy in view about 95% of the time they stood still
  after setup, so no-fight branches rarely ran.

### 3.3 Economy and level-sum arms (eight; none shipped; LEARNINGS S4)

- Stopped at 5(a): g4farm, g4farm3, g4builder (two attempts), g7dig, g7bank.
- Parked after delivery: g4farm2 (INCONCLUSIVE at 96 cells, +23% vs a +25% bar), g4econ2 (Cyril delivery PASS, then band
  net +3), g7fc (fires in 17/17 games where its trigger holds; a stack candidate).
- Why they failed: "The economic lever that worked took free resources without taking actions or crumbs from fights."
  Against andli28 the level gap was "mostly heal XP (-27.6 of -35.3 levels) plus attack XP lost while in jail; digs explain
  about 13 levels". g7bank was designed for +22 levels and delivered +7.

### 3.4 Saving robots alone (LEARNINGS S8)

- g7ehp (no lethal step-in below 700 HP): deaths -12%, lethal step-ins from 364 to 1.5 a game (+19 SE). Band look 1:
  capture t -1.12. Parked.
- g7kite (leave enemy reach below 700 HP when not ready): ending turns in reach fell from 0.22 to 0.00 (+17.9 SE). Look 1
  read t 2.03, but pooled over 480 pairs t_all was 0.32. Parked.
- g7spawn (avoid contested spawn zones): enemy captures rose 1.00 -> 1.50. Closed. "That flag lost its reinforcements."
- The stack g7kiterc (kite plus a supported hold at HP >= 700) fired every pre-registered 5(a) bar but was never
  band-tested.

### 3.5 Other closures

- **Territory-aware micro (g6terr).** The kill reward (+30 crumbs only on enemy territory) is the economic gap against the
  upper tier: about 10,200 crumbs a game to them from our deaths on our side vs about 2,400 to us. But "where kills happen
  follows the game's flow, not a tile preference": paidKillShare moved the wrong way (-0.086).
- **Target-only gains do not climb the ladder (LEARNINGS S1).** g7ehp: +28/240 against andli28, band net +2. g4gym1: +12
  over 1,880 against Gymhgy (its early +31/400 had been noise).
- **The decision-layer rewrite** (shared flag tracks + an auction of responders; an 8-agent design). Its consumer was never
  built. 528 of g_iter3's ~900 dead lines were its unused Track sensor (LEARNINGS F1).
- **Wholesale re-testing of closed arms** (RETEST queue, 8 arms on g_iter2): none delivered.
- **Stacking on non-inferiority (bases B1-B3).** B1 ended at -30 over about 1,870 pairs vs g_iter1 (-1.8 SE). Final fit:
  b1v2 1626, b1z2b 1652, b2fs 1638, against g_iter1 1652.

---

## 4. Method lessons

### 4.1 The loop as practised (TRAINING_ALGORITHM.md, CLAUDE.md)

1. Select a target from a rotation: own-game defects, tactics the field beats us with (TACTICS.md), block census, the
   capability gap, or tactic levels.
2. Trace the motivating replay with the reader.
3. Pre-register in TRAINING_LOG: the mechanism, its counter, reachability, trigger frequency, price, gate and falsifier.
4. Implement one change as a `C.java` switch, default off. `src/bot` with defaults always plays as the incumbent, and
   `tools/arm-intent.txt` asserts every flipped constant.
5. **Step 5(a):** diagnostic games on chosen cells, read against "twins" (the incumbent on the same seed), until the
   mechanism shows firing.
6. **Step 5(b):** a paired delivery mini-block (`tools/delivery-gate.sh`, 24 cells, auto-extended to 48, 96 and then
   192) with pre-registered signature bars.
7. Band test (240 seeded pairs per look) under the shipping rule.
8. On accept: snapshot, ladder record, refreshed charts and TACTICS, commit and push.

A closed-directions ledger with re-open conditions sits in mid-log (2026-10-01). The promised functional-area map was
never written.

### 4.2 Gating and statistics: what changed and why

- **Seeded pairing.** `tools/scrim.sh` draws the engine seed in a second RNG stream, as the 4th cell field, so a SEED's
  cell sequence is unchanged. Until 2026-10-02 23:00 UTC every build drew its own engine seed per cell, and "identical code
  flipped 15-29% of cells ... about 2.5 days of gained/lost tallies were mostly noise" (M1). After the fix: "g_iter1 vs the
  copy g1copy read 0 of 80 discordant."
- **Seeding is exact only for inert code.** "Arms that change behaviour still disagree with the control on 14-38% of
  pairs". On 234 band pairs, 1 SE is about 6.5 net games, or about 20 Elo, "so only effects of about 40 Elo or more were
  visible" (M2). The judge's conversion was "12-13 Elo per band win point".
- **Test the most informative per-pair statistic.** Per pair, wins carry 2.2-5.6x less information than the capture
  difference. The old rule (wins net >= 2 SE, or upper-tier capture >= 2 SE) promoted a g4ship1-sized gain (+30 Elo) "17%
  of the time as written and 34% as practised". **The adopted rule:** ship if `(t_all >= 2.3 or t_up >= 2.6) and wins net
  >= 0`, read at looks of 240, 480 and 720 pairs with stop rules. Look 1 ships only at t_all >= 3.0, and parks if t_all <
  0.5 and t_up < 0.8. Simulated: null 2.0%, harmful <= 0.2%, g4ship1-sized gain 63-65%. "Before it there was no promotion
  for 45 hours."
- **Three-way verdicts on delivery.** PASS when the margin is >= 1 SE beyond the bar, FAIL when it is >= 2 SE short,
  otherwise INCONCLUSIVE with an auto-extension. Before this, "16 of 28 FAILs (including 3 of the 5 Cyril closures) and 7
  of 15 PASSes sat within 1 SE of their bar". Guards (`nw:`) fail only beyond 2 paired SE, and read INCONCLUSIVE when
  "the worst plausible drop" exceeds 20%.
- **First looks regress toward zero (M5).** g4relay2: +54% on 8 cells, +2% at 96. g4gym1: +31/400, then +12/1,880.
  g7kite: t 2.03 at look 1, 0.32 pooled.
- **The basics battery (`tools/basics.py`) on every block.**
  - Absolute bars: symWrong 0; symmetry decided by r201 in >= 95% of setup-decidable games and by r400 in >= 90% on the
    15 post-setup maps; 0 overruns; 0 exceptions.
  - Relative bars, FAIL only beyond 2 SE: stillPost, kill/death, trapsHit, gathered400, floating crumbs at r250.
  - Owner exception (PROMPTS 168): "cracking an opponent overrides" relative checks that the tactic pays by design.
- **No kills guard at delivery** (PROMPTS 183). "A mechanism that trades bodies for flags or crumbs is judged by the band
  test, not stopped at delivery."
- **Don't price a fix from a correlational split (M7).** "We lose more when the symmetry is wrong" (25.0% vs 39.9% against
  ColtG5) turned out to be a map effect: the fix went 63-57 head to head.

### 4.3 Ladder and Elo design (what it was and what it showed)

- **Games.** Scrimmages only: a random map from the corpus, a random side, a fresh seed, rotating opponents (never the
  same one twice in a row, each at most ceil(N/pool) times per block). External bots never play each other.
  `scrim.sh` refuses to run if `progress/games.csv` is missing rather than fall back silently.
- **Fit (`tools/elolib.py`).** Batch Bradley-Terry by minorise-maximise on the Elo scale (1500 anchor), with a weak prior
  of one virtual win and one loss. Each of our builds is its own player. Games are deduped on (teamA, teamB, map, seed).
  Two fixes:
  - (MEAS11) iterate to tolerance: "the old 3,000-iteration cap had every rating 30-46 points low"; convergence takes
    about 24,000 iterations.
  - (PROMPTS 191) a per-pair cap of 200 games. About 1,500 filler games against andli28 had pulled g_iter7 from 2150 to
    2116, below NotLLeon, "which it beats head to head".
- **Grade.** Rating +- 95%, rank, field score (expected score against every ladder bot, one game each), and "vs higher".
- **Pools.** Day 1: two games against all 55 field bots (110 games per build). From 10-01: "the band", the 20 bots rated
  nearest the incumbent (`elo.py --band 20`). The upper tier is the bots rated above it. The band was refreshed at each
  promotion with fresh look seeds (PROMPTS 184-185).
- **Calibration blind spot.** uravt.Version18Final rated "2274 +- 348 on 26 day-one games" (26-0 against weak early
  builds), fell outside the band and was never redrawn. A 40-game block put it at 1920. A bot rated on few games needs a
  calibration block, not a band.
- **Composition.** 45,389 games; "36,440 ... (80%) were filler games, mostly target matchups (Gymhgy 12,450, andli28 6,770,
  Cyril 6,170)". Absolute Elo is not comparable across fits: g_iter1 was quoted at 1756, 1853, 1811 and 1762 before
  settling at 1652.
- **Instrument power.** The 110-game full-field block had "every arm ... within +-4 of 84/110"; the band was the fix. The
  band held 11 of the 12 bots rated 2050+, but we won about 9% of those cells, so "the capture difference became the
  measure there".

### 4.4 How opponents were cracked: the procedure

From CRACK.md (owner PROMPTS 120: "pick a strategy and focus ... a single, unambiguous victory over a higher-ranked
opponent ... find a little crack to widen"):

1. **Pick the target** from our record against every bot above us. Take the closest reachable one, preferably with close
   losses: ColtG5's wins were "close games: 102 of 135 are the 'captured more flags' tiebreak".
2. **Pre-register a victory read before any number.** ">= 60% of at least 120 games (two-sided binomial p < 0.05) ... and
   paired net >= +2 SE vs [the incumbent]", later raised to 240 games. Later targets used "its rating exceeds the
   target's on the converged fit".
3. **Point the idle filler at the target** (`FILLPOOL=<bot> tools/filler-pair.sh <incumbent> <candidate> 40`) to build a
   paired baseline and a replay corpus on random maps and sides.
4. **Study how it wins from replays only.** Tools used: `--defense` trips, `--trapgeo`, the census, and multi-lens study
   workflows (5 lenses, a synthesis, an adversarial critic). Map-class cells were allowed for diagnostics after PROMPTS
   178.
5. **Build arms against that mechanism.** Each passes 5(a) and a delivery block on the target pool (`DGPOOL=`), then the
   paired filler gives the matchup read.
6. **Ship only on the band.** A target counts as beaten when the ladder ranks it below us (PROMPTS 157-159), then the
   target moves to the bot just above (CLAUDE rule 14).

Results: one direct crack (waffle). ColtG5 fell to basics; Cyril, Gymhgy, hsmalladi and andrewgopher fell to band-wide
promotions. LEARNINGS S1: "Target studies found levers, but only the ones that were also band-positive climbed the
ladder." S2: "If the mechanism cannot be stopped, slowing it may be enough."

### 4.5 Process rules that held up

- **Diagnostic before any test; delivery before any band test**, enforced by a tool that refuses (`band-test.sh` needs
  `gauntlet/delivery-<arm>.PASS`; override only with a written reason). "10 of 11 adoption arms had been judged on wins
  without reproducing the opponent's behaviour" (PROMPTS 66-67).
- **Every rule kept in prose decayed (P2).** "17 filler blocks (about 2,000 games) were played and never recorded until the
  owner asked." Each rule became a tool: the delivery refusal, `collect-fillers.sh` at every task check, the arm-intent
  check, and `deadcode.py` in the unit tests.
- **TACTICS.md updated after every ladder run** (standing order, PROMPTS 18), with columns named **Adoption** and
  **Neutralization**, not offence and defence (PROMPTS 21: "the offense/defense dichotomy is confusing you").
- **TL-1 (TACTIC_LEVELS.md):** a tactic is testable only once our copy reproduces the opponents' state, and pays only when
  the capabilities between that state and a win term are at par. The procedure: a symptom screen (is the signature a
  policy or an outcome?), then a payoff graph (count the below-par root capabilities), then a delivery mini-block. Under
  it, "None of the 12 is elementary". T6, T8 and T9 were symptoms (for example, beaters heal more than they attack because
  they win fights). TL-1 was never re-run after 10-01 (`tools/tl1.py` was never built).
- **Three rejects in one area leave the area. One structural swing in four attempts.** The plateau escalation order, as
  amended: correctness audit first, then ablation, API sweep, re-reading games, re-reading advice, jointly necessary
  pairs, a structural attempt, and a rewrite.
- **A standing VM queue with an idle filler**, collected at every 30-minute `/loop` task check.

### 4.6 Owner interventions and what they corrected

| PROMPTS | intervention | what it corrected or produced |
|---|---|---|
| 6 | "implement a rush offense. Then you can use self-play to develop a rush defence" | `arch_rush*` sparring partners. The all-out rush went 5/32 vs g_iter1 (a "filter, not a verdict"); arch_rush10 at 17/32 sat in the 25-75% sparring band |
| 17-22 | "Are T1-T4 the only tactics...?"; TACTICS comprehensive; Adoption vs Neutralization | all four had been traced from hsmalladi games; TACTICS grew to 19 rows |
| 36 | "Are you fully utilizing all the VM's CPUs?" | the VM sat idle about 29% of the time between runs, which led to the standing queue and filler |
| 56 | can tactics be told "elementary" from infrastructure-heavy? | TACTIC_LEVELS.md (TL-1); "10 of 11 adoption arms never delivered" |
| 66-67 | "you failed to reproduce the enemy's tactics, but went ahead with a ladder test anyways" | the delivery gate, enforced in tools |
| 72-73 | idle-filler blocks | 17 unrecorded blocks recovered; the filler was redesigned to pair candidate and control on the same seeds |
| 111-113 | "take a step back ... diagnosis"; "try it out, but keep statistics"; enemy systems evolve gradually in a real tournament | the stack on non-inferiority was dropped; REWRITE_EVAL pre-registered; the curriculum idea (archetype -> rung -> band) |
| 120 | "one unambiguous victory over a higher-ranked opponent" | the crack programme (§4.4) |
| 125-127, 137 | "I was under the impression we could figure [symmetry] out via observations"; "This is basic stuff"; "The basics ... are the foundation" | observed symmetry, then the correctness audit that ended the plateau; CLAUDE rule 15 (basics first) |
| 150 | "old approaches that you discarded are worth revisiting" | RETEST queue; 8 arms, none delivered |
| 154-155, 181 | "I don't see g_iter2 in github"; "our last run" column stale | promotion checklist; one generated state source |
| 157-159, 177 | ColtG5 is defeated; pick the next target; open the list if lines run out | the target rotation rule |
| 168 | "cracking an opponent should override" | crack exception to the relative basics veto |
| 169, 173 | capture the audit as a reusable prompt; ADVICE much more concise | `AUDIT_PROMPT.md`, `AUDIT_PLAYBOOK.md`; one-paragraph ADVICE §29 |
| 178 | maps and sides may be chosen against benchmarks (diagnostics only) | chosen-cell 5(a) found the centre-crumb effect (7-1 on 16 cells). The ban had been the agent's own over-reading of PROMPTS 1, "carried for about 4 days ... and never raised" |
| 180, 187 | stack close-to-good ideas; note it is permissible | g4ship1 -> g_iter5 |
| 182-183 | run the band test anyway; remove the kill guard | g4ship1 delivered; k/d turned out level on the band (3.09 vs 3.09) |
| 184-185 | why so few games vs uravt? refresh the band | calibration fix |
| 186-188 | "evaluate whether the shipping criteria are too strict" | the power analysis (17% power) and the new rule (63-65%) |
| 191 | cap each pair's weight in the fit | Elo distortion by filler sampling fixed |

LEARNINGS O1: "The owner's short, basic questions were the cheapest audits of the week." O2: "Bring the owner a rule's
measured cost with a recommended option, and ask directly."

### 4.7 How the agent went wrong (LEARNINGS F1-F5, plus the log)

- **F1: escalating to an elaborate redesign before checking the basics.** The response to PROMPTS 111 named an
  "architecture ceiling" and launched an 8-agent rewrite design. "The binding terms were basic bugs."
- **F2: deferring a broken basic because its consumer looked minor.** On 10-01 TACTIC_LEVELS recorded that `Sym.observe`
  was never called, and moved it out of the work block. Twenty-six hours later the owner asked.
- **F3: not questioning the yardstick.** Three positive arms sat short of promotion for about 45 hours before the owner
  asked about the rule's power.
- **F4: building a study's ranked levers before following its top open question.** The vertical-map penalty against
  andli28 (0.195 vs 0.366, z -2.9) was named on 10-06; four levers were built first and none shipped. "Slice a target's
  games by map symmetry and side on day one: it is cheap."
- **F5: `pkill -f` / `pgrep -f` matching the issuing shell.** Five times in the week, including at shutdown.
- **From the log:** a "default-equivalent" trap-placement rewrite was not equivalent (an 18-32 "inert" control) and
  contaminated four arms. A sed that flipped an arm's switch silently matched nothing (g1sym verification 4 ran OFF). Ten
  of eleven adoption arms were judged on wins without delivering the tactic. Bars were sometimes set on downstream
  outcomes, which blocked a winning mechanism (g2cstun froze carriers x3 and won 13 of 14 discordant pairs, yet failed
  both capture bars; R3).

---

## 5. Bot architecture and the basics (with mapping to 2023)

All paths are under `/home/terryvanbelle/projects/vibe/2024/src/g_iter7/`, the final incumbent. `src/bot` is the working
copy with every arm's switch, default off. The bot is about 3,100 lines in nine files.

### 5.1 Turn loop, monitoring, constants

- **`RobotPlayer.run`.** One static loop per robot: `G.startTurn()`, `Sym.scout()` (moves first while the symmetry is
  undecided), `Duck.turn()`, then `Sym.update()` (observation after the turn, with spare bytecode only). Every
  `GameActionException` or `Exception` is caught and counted (`G.exceptions`). After the turn: overrun = "the round changed
  while our turn ran"; near miss = more than 90% of the limit (`C.NEAR_MISS_BC`); `G.maxBc` tracks the peak.
  `Clock.yield()` ends the turn.
- **`G.java`.** Per-robot statics: an xorshift RNG seeded from the id ("identical code on both sides never shares a
  sequence"); `G.nearest` breaks ties by the robot's own RNG, "never array order". The 64-character indicator string puts
  the note first, then the counters. Audit MEAS5 found the old string "overflowed the 64-char cap on 70-75% of turns".
- **`C.java`.** Every arm is a named switch. Arms are built by flipping constants, checked by `tools/arm-intent.txt` and
  `test_tools.py`. Dead code is checked by `tools/deadcode.py` in the unit tests.
- **2023 mapping.** Copy this loop shape as is. The 2023 limits are 10,000 (launchers etc.), 12,500 (carriers) and 20,000
  (HQ), against 25,000 in 2024, so the near-miss and overrun counters matter more. the g_iter6/g_iter7 band blocks peaked at
  24.1-24.8k of 25k, partly by design, because symmetry observation filled spare budget. Lesson M10: "keep the near-limit check able to see": a real
  95% near miss (BOT16) hid among the deliberate fills.

### 5.2 Navigation (`Nav.java`, 115 lines)

- **`Nav.moveTo(t)`.** Greedy direct step, then the two side-steps that reduce distance (order by a per-robot handedness:
  `left = (G.id & 1) == 0`). If both fail: fill water (`fillToward`), else enter bug mode, wall-following until strictly
  closer than at the start. Stall exit: `noProgress > STALL (20)` flips handedness and resets.
- **Audit fixes.** A7 (`resetNeeded`): keep the bug state when the target moves at most dist2 8, so a moving carrier or
  escort point does not reset wall-following every turn. A9: one map-edge flip per call. BOT8 (`C.FILL_STEP`): step onto
  the tile just filled in the same turn; it fired 100-387 times a game on water maps. FILL_SMART: take a free land step
  instead of an avoidable fill (26% of fills were avoidable).
- **Measured.** Stillness after setup was 36.1% for us vs 22.0% for opponents. Only 4.6 points of it came with no enemy in
  view: "our stillness is in fights". This was a micro issue, not navigation. The A4 fix (only engage enemies reachable in
  3 moves, by a BFS over sensed passable tiles) cut post-setup stillness on Tunnels from 58.9 to 37.1.
- **2023 mapping (inference).** Bug nav with handedness and a stall exit transfers. The new hazards are currents (they push
  units at end of turn) and clouds (vision r² 4, cooldowns slowed 20%). Fold both into one legality and cost check, as
  2024 did with water in `fillToward`. Carrier move cooldown grows with load, so a carrier path should weigh distance by
  its load. The A4 lesson ("an unreachable visible enemy took the whole turn") applies to walls, and possibly to currents.

### 5.3 Symmetry (`Sym.java`, 258 lines; `test/bot/SymTest.java`)

- **Representation.** Candidates are a bitmask (ROT=1, FX=2, FY=4). Per-robot bitsets record `seen`, `wall`, `spawn` and
  `dam` tiles, plus `ours` for our 27 spawn tiles (O(1) membership; "nested loops cost ~35k bytecode").
- **Eliminations.**
  - `geometric()`: a symmetry that maps one of our spawn centres into our own spawn zone is impossible.
  - `observeSpawnImage()`: the image of our centre must be their spawn tile.
  - `observeEnemyCentre()`: an enemy flag id is their spawn-centre index (audit A2).
  - `observeTile()`: a tile seen now must match its remembered image. The setup dam counts too.
  - `collapseEquivalent()`: candidates that predict the same enemy spawn zones count as decided.
  - The set is never emptied; a contradiction is counted instead. Results are AND-merged through shared slot 16.
- **Budget and scouts.** `update()` runs after the turn only with >= 6,000 bytecodes left (`BC_START`) and stops at 2,500
  (`BC_STOP`); each tile is processed once. That cut Soccer's undecided cost from 14.8k a turn to 6.3k. Three scouts (idx
  3-5) walk to the nearest distinguishing tile while undecided.
- **Tests.** "300 random symmetric maps ... the true symmetry is never eliminated ... every map is decided within 13
  disks". In play: decided by r201 in 194/196 setup-decidable games, and by r400 on 38/38 post-setup maps. symWrong was 0
  in all 1,520 andli28 games.
- **2023 mapping (inference).** The same three-candidate structure applies; the brief says 2023 maps are symmetric by
  rotation or reflection. The fixed features are HQ positions (our HQs map to theirs), walls, wells, islands, clouds and
  currents. The 2024 spawn-zone check corresponds to "the image of our HQ must be an enemy HQ" (one sighting confirms or
  eliminates). Budget: the 2024 thresholds (6,000 start, 2,500 stop) assume 25k. At 10k they must be scaled, or the
  memory work moved to the HQ (20,000 budget, stationary), with scouts reporting. Writing slot 16 in 2023 needs a robot
  within range of an HQ, amplifier or anchored island, so the merge will lag. Remember lesson F2: "Symmetry must be
  decided by observation, never guessed", but price the fix on identical cells (it alone was neutral in 2024).

### 5.4 Combat micro (`Micro.java`, 451 lines)

- **`Micro.fight(enemies, allies, goal)`.** Lexicographic scoring of the 9 tiles (8 moves and CENTER):
  - Strike first if something is in reach (`tryAttack`).
  - A visible enemy flag carrier: score 20000 minus 10 x dist2 (close in regardless).
  - A loose enemy flag (REGRAB or pick-after-move): 19000 band.
  - **Engage** (action ready, not hurt, an enemy in reach, and either `strong` or few threats): 10000 - 100 x threat + 10 x
    adjacent allies. This means "hit from the safest reaching tile".
  - **Advance** under clear local superiority (allies + 1 >= enemies + ADVANCE_MARGIN): 5000 - 20 x minD - 50 x threat.
  - **Kite/hold** otherwise: -1000 x threat + 10 x adjacent allies, +50 for a tile at dist2 11-20 from the nearest enemy.
  - Threat = enemies within dist2 10 of the tile (an enemy can step once and still reach dist2 4). Random tie-break.
- **`bestTarget`.** Flag carriers first, then lowest HP x 10, then highest attack level. Optional Z2ESCORT: hit the
  carrier's escorts first.
- **`tryHeal`.** Lowest HP below `HEAL_HP_BELOW`. With C.HEAL_HOLD and an enemy within `HOLD_R2` (10), only flag carriers
  are healed: the action is kept for the enemy that steps in. This is the +144 Elo change.
- **`engageable` / `engageableFast`** (A4 and REACH_FAST): an enemy takes the turn only if it is within dist2 8 or
  reachable in 3 moves. It falls back to "yes" under 8,000 bytecodes left.
- **Open defects at shutdown.**
  - T19: "the kite score counts threats out to dist2 10, so stepping out of reach earns nothing". After a strike we stayed
    in enemy reach 0.252 of the time vs the upper tier's 0.111.
  - The engage rule steps in at mid HP (40% vs andli28's 15%).
  - `strong` "compares allies within dist2 20 against every visible enemy" (andli28 synthesis).
- **What was learnt.** Smooth weighted scoring lost 1-25. Tempo (strike when ready, do not waste the action, leave reach
  while recharging) was where the upper tier beat us; target choice and focus fire were at parity. The kite score's
  coin-flip ties were mined as a randomized experiment (R7): "ending a turn in reach below 300 HP raised 3-round deaths by
  0.16-0.21, while at 700 HP and above it raised strikes by 0.07-0.13."
- **2023 mapping (inference).** Launchers (45 Mn, 200 HP, 20 dmg, attack r² 16, vision r² 20, move cooldown 20) are the
  main fighter. Reuse the lexicographic tile scoring and define "threat" from the 2023 geometry: the set of tiles an enemy
  launcher could attack from after its next possible move. With move cooldown 20, a launcher moves at most every other
  turn, so being caught in range while unable to step away matters even more than in 2024. Measure "ready-and-striking on
  contact", "hits taken while on cooldown" and "ending turns in reach" from replays early, and contrast them against the
  bots that beat us and the bots we beat (S3, the method behind +144). Targeting: the HQ is indestructible per the brief,
  so never waste a shot on it. Carriers can throw cargo as damage, and anchor carriers are the "flag carriers" of 2023:
  the "carrier first" rank transfers.

### 5.5 Economy, exploration, team logic (`Duck.java`, 1,242 lines)

- **`Duck.turn()` priority order.**
  1. Upgrades: `buyUpgrades`, ATTACK > HEALING > CAPTURING.
  2. Spawn if jailed: `trySpawn` picks the spawn tile nearest the carrier target, an alerted flag or the field target.
  3. Round 1-3 symmetry hints, then shared-array sync and `sense`.
  4. Carry a flag if holding one; setup phase; pick up flags.
  5. Then, in order: carrier stun; a fight if any enemy is engageable (with `placeCombatTrap` first); defend; level farm;
     heal; post-setup crumb detours; field target via `Nav.moveTo`; pickup after move; heal; spend a floating bank.
- **Economy lessons.**
  - Free income wins. Centre crumbs behind the dam (`POST_SETUP_CRUMBS` idle detours) gave crumbs r201-400 at x1.9; the
    in-fight crumb step "barely fired".
  - Every reallocation of the bank was neutral or negative (setup digs vs stuns, banking, builders, farms).
  - Against the upper tier "the economic gap was the kill reward, not the map's crumbs".
  - Fires-or-not census first (R2): dam traps and float traps never fired on most maps ("bank < 700 in setup on 64 of 75
    maps"), so their ablations were void.
- **Exploration.** The broadcast-hint idle defect was measured and found not to cost anything (b2hint 21-25, closed).
  Flag-sighting time was "inherited" from territory (C11), not a search defect.
- **2023 mapping (inference).**
  - Economy: carriers to wells, mana for launchers, adamantium for carriers and anchors. The transferable rule is to take
    uncontested free income (wells behind your lines, the HQ's passive 6 Ad + 6 Mn every 5 rounds) without diverting
    fighters.
  - HQ build timing replaces 2024's spawn logic. The HQ can build several units a turn (cooldown 2 vs a decrement of 10),
    so the "bank floating" check (13k crumbs floating in g_iter0's standoff) becomes "resources piling up in the HQ".
  - The 2023 tiebreak counts islands held, anchors placed, elixir, mana and adamantium. The 2024 lesson that late flag
    states freeze (andli28: captures after r1900 in only 2 of 63 level games) suggests late-game banking and anchor
    counts may decide many ties. Measure tie frequency on day one.

### 5.6 Communication (`Comms.java`, 227 lines)

- **Schema.** The header documents one purpose per slot of the 64 x 16-bit array. Locations are encoded as `x*64+y+1` (0 =
  none). Slot 0 hands out creation-order indices (`claimIndex`). Registries: EF_ID / EF_LOC / EF_STATE for enemy flags;
  OF_ALERT / OF_LOC / OF_CARRY / OF_HOME / OF_THREAT / OF_SEEN for our flags; slot 16 for symmetry; slot 58 for the lost
  mask.
- **Defects found by the audits** (each a freshness or state-machine bug):
  - A1: an alert meaning "any enemy seen" stayed fresh all game.
  - A5/A6: a "carried by us" state never expired when our carrier died; a drop tile was kept after the flag went home.
  - BOT1: captured own flags were never recognised.
  - BOT10: carrier sightings expired after 5 rounds.
  - A11/BOT13: shared state contradicted its schema.
- **Tests.** `test/bot/AuditTest.java` (84 KB) pins each fix, including slot-layout tests.
- **2023 mapping (inference).** Same array size, so the documented-schema discipline and the per-slot freshness rules
  transfer. In 2023 only robots near an HQ (r² 9), an amplifier (r² 20) or an anchored island (r² 4) can write, while
  everyone can read. A unit's report reaches the team only after it walks into write range, and 2024's "free compute and
  comms for jailed robots" trick does not exist. Every entry should carry a round stamp and an explicit expiry. Plan for
  stale data from day one (the A1, A5 and BOT10 classes).

### 5.7 Bytecode

- Measured peaks: g_iter0 13,981; g_iter1 about 15k; g1basics 24.7k (thin margin from the A4 BFS); g_iter6/g_iter7
  band blocks 24.1-24.8k per game.
- One overrun in a 234-pair block (g2nonav, a crowded late fight: "BFS ... followed by Micro.fight's loops over many
  robots").
- Round-1 turns at 22.8-22.9k came from symmetry terrain fill by design, not from `G.init` (the INIT_FAST arm changed
  nothing).
- **2023 mapping (inference).** With launchers at 10,000, a 2024-style BFS-reachability check plus full-vision symmetry
  observation will not fit. Use REACH_FAST-style precomputation (mark attack tiles once per enemy) and give heavy
  bookkeeping to the HQ.

---

## 6. Tools and infrastructure inventory (reuse verdicts for 2023)

All under `/home/terryvanbelle/projects/vibe/2024/tools/` unless noted. "Steal" means copy and change only paths, names
and the year. Changes needed everywhere: the engine is battlecode23 **3.0.15** (2024 used 3.0.6), replays are `.bc23`,
maps are the 2023 corpus, the JDK stays 8, and the VM name, zone and paths (`battlecode-dev2`, us-west2-a,
`~/projects/vibe/2024`, `~/projects/vibe/bc24-benchmarks`) change.

### 6.1 Engine, runner, compile

| tool | purpose | quality | verdict for 2023 |
|---|---|---|---|
| `build-engine.sh` (81) | clone and patch the engine, build with JDK 8 + Gradle 7.6, stage `engine/` and the map list. Maven artefacts returned 403; a rotted jsi snapshot jar was rebuilt; `LiveMap.getSeed` was patched to honour `-Dbc.game.seed` | worked day 1; determinism verified | **adapt**: the 2023 engine repo and tag 3.0.15. Check whether its LiveMap seed hook and Gradle dependencies have the same shape (unverified for 2023) |
| `lib.sh` (68) | `run_game` (bare java, `timeout`, `-Xmx512m -XX:+UseSerialGC`, `-Dbc.*` flags, `GAME_SEED`), `parse_result` (`(A) wins (round N)`, `Reason:`), `engine_busy` via `ps|awk` (not pgrep), `compile_src` (javac -source 8) | solid | **adapt**: check the 2023 `-Dbc.*` flag names and the result-line regex against the 2023 engine's stdout |
| `run-match.sh`, `run-dev.sh` | one game; dev uses a private class tree per process; `LOG_OUT=` keeps engine stdout | solid | **steal** |
| `gauntlet.sh` (135) | parallel runner over cells; seed column; `CELLS=`, `CLASSES=`; refuses external opponents unless `SCRIM=1`; re-execs from a copy; dud detection | workhorse | **steal** (map list and silence flags) |
| `snapshot.sh` | freeze `src/bot` as `src/<name>` with a package rewrite | trivial | **steal** |
| `bench-compile.sh` + `benchcompile/BenchCompiler.java` (43 + 86) | blind compile of every benchmark repo; one JVM per repo; logs to files; `manifest.tsv` (`name package classdir repo commit`) | worked: 681 packages from 58 repos | **steal** |
| `bench-select.py` | name-only choice of each repo's final bot (final > postqual > qual > seeding > version > sprint2 > sprint; junk regex) | worked | **steal** |
| `bench-roster.py` | roster table between markers in BENCHMARK.md | fine | **steal** |

**Benchmark discovery (BENCHMARK.md, 2026-09-30):**
- Repository searches: `battlecode24`, `battlecode2024`, `battlecode 2024`, `battlecode-2024`, `bc24`, `bc2024`,
  `breadwars`, and `battlecode` with 2024 creation dates.
- Code search for 2024-only API names (`TrapType.STUN`, `GlobalUpgrade.ATTACK`, `senseLegalStartingFlagPlacement`).
- "694 search rows -> 462 candidate repos cloned -> **73 repos use the 2024 API**". Repos were classified by counting
  files that use 2024-only API names, with no content displayed. Clones are sparse (source files only) in
  `~/projects/vibe/bc24-benchmarks/`, outside the repo.
- Result: 681 packages from 58 repos, a ladder field of 55 bots (one per repo).

For 2023, repeat this with 2023 queries (`battlecode23`, `bc23`, `tempest`) and 2023-only API names (inference: names
such as `ResourceType`, anchor and island methods; check them against the 3.0.15 API). The discovery script itself is not
in `tools/`, so this step must be scripted afresh.

### 6.2 Ladder and statistics

| tool | purpose | quality | verdict |
|---|---|---|---|
| `elolib.py` (97) | batch Bradley-Terry MM with a weak prior, dedupe on seed, convergence to tolerance with a warning, PAIR_CAP 200, `field_score`, `current_build` | tested; the two fixes (MEAS11 convergence, pair cap) are already in | **steal as is** |
| `elo.py` (128) | ELO.md table, `elo.png`, `--band N --as B`, `--explore`, grade per build | good | **steal** |
| `scrim.sh` (66) | contest-rule block: band pool, rotating opponents, random map and side, **engine seed as the 4th cell field from a second RNG stream**, `MAPFILE=` for diagnostics only; refuses without games.csv | good after the B2 fix | **steal** |
| `scrim-record.py`, `post-block.sh`, `field-score.py`, `progress-chart.py` | record a block idempotently; one command after each block; charts with projections | good | **steal** |
| `eval-paired.py` (116) | paired evaluation by tier (all / upper / rest): wins gained and lost with an exact sign test, capture-difference delta +- SE (t), identical-game count, `--look N` ship decision | core of the shipping rule | **adapt**: replace "captures" with the 2023 outcome metric, such as islands or anchors difference at game end (inference; choose by the information per pair, M3) |
| `delivery-gate.sh` (63) + `delivery-check.py` (82) | 24 -> 48 -> 96 -> 192-cell paired mini-block; checks `median:` / `mean:` / `fire:` / `rel:` / `nw:`; three-way verdicts; `MIN_PAIRS` 18; worst-plausible-drop guard; `DGPOOL`, `DGMAPS`, `DGTAG` (refuses a pool without a tag) | the most important gate tool; many fixes already in | **steal**; only the census column names change |
| `band-test.sh` (24) | band test on the incumbent's look seeds; **refuses without the delivery PASS file** | good | **steal** |
| `basics.py` (120) | basics battery: absolute bars (symWrong, symmetry decided in time, overruns, exceptions) and relative bars (stillPost, k/d, trapsHit, gathered400, floating crumbs) | good; MEAS7 (the exceptions bar is structurally 0) still open | **adapt** the columns: no traps in 2023; use resources gathered, floating HQ resources, launcher k/d |
| `sprt.py`, `paired.sh`, `mirror.sh`, `compare.py` | mirror SPRT on discordant pairs (H0 0.50 / H1 0.58, α = β = 0.05, batches of 16); paired cells; game-by-game diff | inherited from 2020/2021 | **steal** (as a regression screen only; the mirror cannot judge field-facing changes, M9) |
| `filler-pair.sh`, `collect-fillers.sh`, `filler-tally.py` | idle filler pairs the control and candidate on one fresh seed; collected at every task check; running paired tally | good, but over-used | **steal** with the information budget of P5 |
| `arm-deltas.py`, `capability-census.sh`, `capability-summary.py`, `tactics-survey.py` | paired capability deltas with SE; census CSVs; opponent tactic survey that regenerates TACTICS' measured section | good | **adapt** (all the columns are 2024-specific) |
| `correlate.py`, `onset.py`, `onset-merged.sh`, `statlib.py`, `polarity.py`, `derived.py`, `test_metrics.py` | correlation and onset of metrics with the result | inherited; the onset table was rarely acted on in 2024 | **adapt** (low priority) |
| `premise.py`, `recall-d0.py`, `contact-d0.py`, `defense-profile.py`, `fill-origin.py`, `stun-check.sh`, `side-indsum.sh` | premise checks and specific studies | one-off | **skip**, except `side-indsum.sh` (sums indicator counters on our side) **adapt** |

### 6.3 Replay reader

`replaydump/ReplayDump.java` (2,085 lines) and `replay-dump.sh` (compiled on demand, cached by source hash). Modes:
`--every`, `--metrics`, `--from/--to`, `--robot`, `--map-at`, `--logs`, `--bytecode`, `--near90`, `--trapgeo`,
`--navstats`, `--flags`, `--levels`, `--defense`, `--comm` (the stored shared array per round), `--track`, `--capabilities`,
`--survey`, `--contact-d0`, `--recall-d0`, and `--calc`. It was integrity-tested on a committed fixture replay. **Verdict:
adapt.** Keep the mode list and the CSV contracts (`--capabilities` and `--survey` feed every gate). Rewrite the event
handlers against the `.bc23` flatbuffer schema of engine 3.0.15. Of all the modes, `--comm` (shared array per round) and
the per-robot cooldown and position reconstruction behind the micro studies were the most valuable. 2024 replays carried no
robot stdout, so counters lived in 64-character indicator strings; check whether 2023 replays carry logs.

### 6.4 VM and operations

| tool | purpose | verdict |
|---|---|---|
| `vm.sh`, `vm-sync.sh`, `vm-run.sh`, `vm-tail.sh`, `vm-collect.sh`, `vm-stop.sh` | ssh helpers (`ensure_vm`), tar-over-ssh sync (no rsync on the VM), detached runs, collection (replays stay on the VM unless `REPLAYS=1`) | **steal**; change the instance name, zone and paths |
| `vm-queue.sh` (31), `vm-enqueue.sh` | standing job runner with flock, a STOP file and an idle `filler.job`; exit status logged correctly after B12 | **steal** |
| `vm-prune.sh` (32) | replay prune above 80% disk; keeps listed builds, delivery-gate base runs, the newest 25 filler runs per kept build and diagnostic runs for 1,440 minutes | **steal**; make retention follow the consumers (T3) |
| `diag-batch.sh` (36) | step-5(a) games in parallel through the queue, at most 8 at once; external opponents on chosen maps and sides; `__bot<side>` names | **steal** |
| `unit-tests.sh`, `test_tools.py` (1,031 lines), `deadcode.py`, `arm-intent.txt` | bot tests (plain mains), tool tests on synthetic inputs, dead-code check, switch-intent check; arm tests rerun on copies with switches on | **steal** the structure; add a lock (T5) |

### 6.5 bcenv

`research/BCENV.md`: bcenv is "a well-sourced design document plus a 35-line git hook". The append-only PROMPTS.md hook
(`scripts/check-prompts.mjs` + its test) is the only code. **Verdict: optional.** The experiment-manifest and
job-accounting checklists are worth a read; nothing else applies.

---

## 7. Pitfalls and gotchas that cost time (cost when stated)

1. **Unseeded paired cells**: "about 2.5 days of gained/lost tallies were mostly noise"; identical code flipped 15-29% of
   cells.
2. **Tactic arms on a broken base**: about 80 builds over about 2 days, none accepted (09-30 to 10-02).
3. **A shipping rule with 17% power**: 45 hours without a promotion while positive arms waited.
4. **A self-imposed ban on choosing maps and sides in diagnostics**: carried for about 4 days, never raised with the owner.
   Lifting it found the centre-crumb effect at once (7-1 on 16 cells).
5. **Disk full, three times.**
   - Driver: 2.6 GB of replays on 10-02.
   - VM: 49 GB disk with 35 GB of replays on 10-02. "the runner spun on failing fillers for 18 minutes", while
     `vm-queue` logged "exit 0" for every job.
   - Driver: 85 MB free on 10-06/07; 1.7 GB of workflow scratch was deleted.
   - Census CSVs were committed empty while the disk was full.
6. **Prune rules deleting needed data**: step-5(a) replays were deleted an hour after they ran, and "all 880 g_iter5
   filler replays that a queued premise check needed".
7. **Silent arm-switch failures**: a moved comment made a sed miss, so g1sym's verification 4 ran with the switch OFF. A
   "default-equivalent" rewrite was not equivalent and contaminated c4bank, e1aggr and e2aggr. The fixes were the
   arm-intent check and identity controls.
8. **Key collisions**: replay names without the seed dropped 1.6-2.5% of band games and 11.5% of ColtG5 filler games, and
   in a 17-map class "only 17 of 24 and 26 of 48 cells paired". This voided g4crumb's 96-cell gate. Diagnostic output names
   without the opponent let arch_rush10 games overwrite the mirror games.
9. **Indicator string overflow** (64 chars) on 70-75% of turns: counters were cut off and per-robot sums undercounted.
10. **Tool reading the wrong team**: `side-indsum` showed g4pick's after-move pickups as 0 when they were 5-99 a game.
11. **Concurrency**: 24 diagnostic games on 8 vCPUs "starved the VM's sshd for minutes", so a task check hung (the cap is
    now 8). Parallel compiles raced and lost 2 of 234 band games. Overlapping unit runs shared build directories. The unit
    suite took about 10 minutes on the 2-vCPU driver and ran about 220 times (about 37 hours of driver time; my
    arithmetic).
12. **`pkill -f` / `pgrep -f`** matching their own shell: five incidents, including a remote pkill that killed its own ssh.
    "until ! pgrep -f" waits spun for about 10 minutes.
13. **Elo artefacts**: the fit stopped early (30-46 low); filler-heavy sampling of one matchup pulled g_iter7 below a bot
    it beats; uravt was mis-rated from 26 games; promotion games were recorded under the arm name (g1basics), so the front
    page did not show g_iter2.
14. **Infrastructure on day 1**: `ZONE_RESOURCE_POOL_EXHAUSTED` for e2-standard-8 in us-west1-b, so the VM moved to
    us-west2-a. Maven engine artefacts returned 403, so the engine was built from source with a rebuilt jsi jar.
15. **Engine quirks (2024)**:
    - The final tiebreak used unseeded `Math.random()`.
    - `examplefuncsplayer` ignores the engine seed (static `Random(6147)`).
    - Some external bots (Gymhgy) are deterministic under a fixed seed, which makes chosen-cell twins exact.
    - A driver game on DefaultSmall takes 2-4 minutes; about 19 minutes on large maps.
    - VM throughput: about 240 games in about 27 minutes (my arithmetic from the criteria verdict: about 9 games a minute
      on 8 vCPUs with 7 parallel).
16. **First-look optimism**: 5(a) blocks of 8-16 cells and look 1 regressed. g4relay2 went from +54% to +2%; g4gym1 from
    +31/400 to +12/1,880; g7kite from t 2.03 to 0.32.
17. **Study syntheses over-optimistic** (R6): the andli28 synthesis valued FINAL_COMPLETE at +2.2 pp x 0.65 and
    ENGAGE_HP at +2-4 pp x 0.4; neither shipped. Critics were better calibrated but also erred (symOk=0 was a one-tile
    artefact).

---

## 8. Top 15 takeaways for the 2023 project (ranked by expected value)

1. **Build the measurement stack before the first arm.**
   - Engine seed in every cell (patch the 3.0.15 engine's seed hook and verify determinism).
   - An identity control on the exact verdict path: 0 discordant.
   - Three-way delivery verdicts.
   - A pair-capped, converged Bradley-Terry ladder.
   - A shipping rule on the most informative per-pair statistic, with simulated power.

   2024 lost about 2.5 days to unseeded pairs and 45 hours to a 17%-power rule. Copy `elolib.py`, `scrim.sh`,
   `eval-paired.py`, `delivery-gate.sh`/`delivery-check.py` and `band-test.sh`, and pick the 2023 analogue of "capture
   difference" (inference: islands or anchors held at the end) by measuring information per pair.
2. **Run a correctness audit of the bot and the tools on the first working bot, and again at every plateau** (five lenses,
   adversarial verifiers, fixes behind switches, one combined build judged on exact pairs). In 2024 this ended a plateau
   of about 80 builds and gave +185 Elo directly plus +77 from its findings. Treat any broken basic as a sample of a class.
3. **Make the basics observable and exact: symmetry decided by observation, never guessed.** Use bitmask candidates, a
   per-robot terrain memory, HQ images, scouts to distinguishing tiles, merges through the shared array, and tests on
   hundreds of random symmetric maps. Then *price* it on identical cells. At 2023's 10k bytecode, budget it, possibly on
   the HQ.
4. **Find micro levers by contrasting behaviour rates against the bots that beat you and the bots you beat.** Tempo (shots
   when ready, actions wasted, standing in reach while on cooldown) gave the single biggest step (+144). For launchers,
   instrument "ready and striking on contact", "hit while on cooldown" and "ending turns in reach" from replays in week 1,
   and keep lexicographic engage/kite scoring (smooth scoring lost 1-25).
5. **Enforce "the mechanism fires, then the behaviour is delivered" with tools that refuse.** Step 5(a) on chosen cells
   with twins, then a paired delivery block, then the band test. In 2024, 10 of 11 adoption arms had never delivered.
   Condition delivery on the trigger (R4) and pair a signature bar with an outcome guard (R3).
6. **Discover, compile and select external 2023 bots by script on day one, blind** (repo search plus code search on
   2023-only API names, sparse clones outside the repo, `bench-compile.sh`, name-only `bench-select.py`). Calibrate every
   bot with a block, so none is rated on a handful of games (uravt).
7. **Ship on the band; use targets as diagnostics.** One target at a time (the bot just above) with a pre-registered
   victory read, a filler baseline and replay studies. But promote only band-positive changes: target-only gains (g7ehp
   +28/240 against andli28) did not climb. Count a target beaten when the ladder ranks it below you.
8. **When an opponent's mechanism cannot be stopped, slow it.** Waffle's re-grab chains could not be denied (1-9 robots
   within dist2 8 of each drop); freezing carriers plus flag distance won 60.8% (p 0.001). For 2023 (inference): an
   opponent's anchor convoys or island chains may be cheaper to delay than to kill.
9. **Before building an arm, estimate the proxy-to-outcome link.** Re-grabs x6, levels +10, stillness -4 points, deaths
   -12% and inEnemy +3 all "delivered" and none moved wins. Presence at enemy objectives was an outcome of winning fights,
   not a lever.
10. **Measure how often each code path runs before tuning or ablating it.** Dam and float traps never fired, so their
    ablations were void. Our robots had an enemy in view 95% of the time when still, so no-fight-branch levers rarely
    ran.
11. **Take free income that costs no fighting actions; distrust reallocations.** Centre crumbs paid; every bank, dig,
    builder or farm reallocation failed. For 2023 (inference): uncontested wells and the HQ's passive income first. Watch
    floating HQ resources, and measure how often games go to the tiebreak (which counts mana and adamantium) before
    investing in late banking.
12. **Stack positive near-misses with independent mechanisms. Never stack on "not worse".** g4ship1 shipped from two arms
    at t 1.0 and 1.3; the non-inferiority stack B1-B3 drifted below the incumbent.
13. **Design shared-array state around freshness.** Every entry gets a round stamp and an expiry, and a state machine that
    cannot stick (A1 always-on alert, A5 never-expiring "carried", BOT1 unrecognised lost flags). In 2023, writes need an
    HQ, amplifier or island nearby, so reports arrive late. Make staleness explicit from day one.
14. **Operations: a standing VM queue with an idle filler, collected automatically, but budgeted by information.**
    - Replay retention keyed to the analyses that still need the files.
    - Results keyed by (code, opponent, map, side, seed).
    - A disk check before writes; a lock on unit tests; at most cores-1 games.
    - Kill by PID, never `pkill -f`.
15. **With the owner: answer basic questions with data, raise any rule's measured cost at once, keep the front page
    generated, and slice each target's games by map symmetry and side on day one.** The vertical-map penalty against
    andli28 (0.187 vs 0.383 over 5,720 games) was found late and never explained.
