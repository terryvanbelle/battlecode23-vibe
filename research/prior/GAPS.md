# Gap reads

Sections appended by coverage-gap readers. Each section covers one prior document (read through the readroom-no2023 filtered copy) plus any code it points to.

## Gap read: /home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc24/research/criteria-review-2026-10-05/alternatives.md

**What it is.** A 16,985 B bc24 criteria-review note from 2026-10-05. The owner asked whether the promotion criteria in REWRITE_EVAL.md were "too strict". The note proposes replacement shipping rules and simulates their false-promotion rate, power and game cost on the measured g4ship1-vs-g_iter4 pairs. It ran no games. **Code also read, directly from the repo:** `/home/terryvanbelle/projects/vibe/2024/tools/eval-paired.py` (116 lines) and the judge's independent re-simulation in `/home/terryvanbelle/projects/vibe/2024/research/criteria-review-2026-10-05/judge/` (`jsim.py`, `jsim2.py`, `jsim3.py` and their `.out` files). The note's own `sim/` scripts (extract.py, sim.py, power.py, hybrid.py, decision.py) and `pairs.json` lived in a 2024 session scratchpad and **are not on disk** any more. I checked: the path that jsim.py hard-codes does not exist. Nothing here describes 2023 play. It is pure evaluation method, which feeds SYNTHESIS C12 ("bc24's structure, on a 2023 per-pair margin, with power simulated first").

### Lessons with evidence (numbers quoted as written)

1. **Check false promotions and power separately. The bc24 rule was not too strict on false promotions. It lacked power.** Under an exact null, the rule as practised promoted a no-effect arm "**2.5%**" of the time, "**1.4%**" as written, and "**3.8%**" if every arm got 4 seeds. But it "rejects **66%** of g4ship1-sized gains (+0.14 capture difference, about +2.4 points of win rate, about +29 Elo) and **80%** of +0.10 gains (about +21 Elo)". It "catches only **17%** of a +0.14 gain that lands in the lower half of the band". The note's conclusion: "Use a better test, not a lower bar."
2. **Test the per-pair statistic that carries the most information, not the headline one.** "Criterion (a) tests wins, which carry about 2.6 times less information per pair than captures." Pairs needed for 80% power at one-sided 2.5% on a +0.14 effect: "all-cell captures **~810**; upper-tier captures ~1,880; wins ~2,070". At +0.10 the figures are 1,590 / 3,680 / 4,060. The per-pair correlation between the wins change and the capture change is "**0.73**". A joint wins+captures estimator "gains about 2% information, because wins are mostly a coarser copy of captures". Only 15.8% of pairs (76/480) were discordant on wins, which is why wins are a weak statistic.
3. **A union of two tests "spends the error budget twice".** R0 pooled-only, (a) or (b) with every arm extended, ran 3.8% under the null "without buying power". The exception was a gain confined to the upper tier: R0 pooled-only 81% vs 57% for the single all-cell test (i).
4. **Sequential looks buy power at the same alpha.** The looks fall at 240, 480 and 720 pairs, i.e. seeds 1-2, 3-4 and 5-6.
   - (iv) all-cell: early promote at look 1 if t >= 3.0, stop if t < 0.5. At look 2, promote if t >= 2.1, stop if t < 1.0. At look 3, promote if t >= 2.1. Wins net >= 0 is required at any promotion. Result: null **2.5%**, **67%** at +0.14, 41% at +0.10, cost "339 / 493" arm games (null / +0.14).
   - (iv-h) hybrid: promote if "(all-cell t >= 2.2 **or** upper t >= 2.5) and net >= 0". Futility stops when "max(t_all, t_up - 0.3) < 0.5 at look 1 and < 1.0 at look 2". Result: null **2.6%**; **66%** even effect, **84%** upper-only, **65%** rest-only; 358 / 506 games.
   - All boundaries were "set by simulation" to the target false-promotion rate.
   - The simplest single-look option is (i)+screen: stop at 240 if t < 0.5, else pooled t >= 2 and net >= 0. It gave 2.1% null and 54% at +0.14 for 315-443 games.
5. **Do not buy power by relaxing alpha.** Rule (ii), a one-sided sign test at 0.10, "triples false promotions to **8.2%**". It promotes harmful (-0.05) builds 3.1% of the time vs 0.3-0.7%. It "would have rejected **g3lost**, today's incumbent": p 0.121 on the actual data, and 46% promotion on the bootstrap. The note calls (ii) "dominated". It reaches (i)'s power at +0.10 "only with 3.4 times the false promotions and 10 times the harmful promotions".
6. **Bayesian framing is a way to report, not a separate rule.** With a skeptical normal prior N(0, tau²), P(delta>0) >= 0.95 reduces to "t >= 1.645·sqrt(1 + SE²/tau²)". That is t >= 1.96 at SE 0.065 and tau 0.10. tau 0.05 gives 2.70, tau 0.07 gives 2.24 and tau 0.20 gives 1.73. A point-mass "inert" prior (30-50% of arms exactly 0) needs "t >= 2.7-3.2". The note's advice: "Report the posterior next to the verdict."
7. **Pre-registration discipline.** g4ship1 had t 2.21 at 480 pairs and sat "right on every boundary": "the hybrid passes it by 0.01 t". The new rules were "chosen after its result was seen, so promoting it on the same data would break ... pre-registration". The clean route: adopt the rule for future arms and resolve the borderline arm with the rule's own third look, i.e. seeds 5-6 plus "a one-time 240-game g_iter4 control" on the same seeds.
8. **Decision analysis over a prior on effects (per-arm uniform tilt).** "Under every prior, the sequential rules give about 1.25-1.45 times R0's Elo per game and promote fewer harmful builds." Under the history prior N(+0.06, 0.08), (iv) gives "+21" Elo per 1,000 arm games vs R0 practice "+14", and misses 31% vs 61% of arms with delta >= 0.10. The prior came from "REML on the 11 behaviour-changing arms" (capture mu +0.09, tau 0.06). It was softened because arms that share one incumbent's control have correlated errors.
9. **The shared, selected control biases later arms.** "g_iter4's control runs are g3lost's own band games, chosen because they looked good". Later deltas are "biased down by ... roughly -0.01 all-cell and -0.02 upper, i.e. 0.15-0.2 SE". Fix: "play a fresh incumbent control on new seeds at each promotion".
10. **Multiplicity across arms.** "About six [arms] so far against g_iter4. At 2.5% each, six truly null arms in a row produce a false promotion about 14% of the time." The note uses this as an argument against loosening, not for tightening.
11. **A criterion tied to a tier list is fragile.** "g2cr met (b) at 240 only while waffle was in the tier". "An all-cell primary test does not depend on the tier list."
12. **Calibrate the margin to Elo and check it against the ladder.** In bc24, "+0.10 capture delta = about +21 Elo" (about 12 Elo per win-rate point). g2cr was predicted at +53 vs +59 measured, and g3lost at +25-29 vs +31, "both have ±35 error". Wins move "0.14-0.20" per capture unit across all past arms. The proxy "overstates arms whose extra captures come in games already decided (g3lost: 0.136)".
13. **The number of identical games drives the SE.** g4ship1 had heavy variance with only 16/240 games identical. g3lost had 86/234 identical, a smaller SE and more power under every rule. Pairs were treated as independent because "seeds draw new maps". Inference is limited to the fixed opponent set.
14. **Cost model.** "A 120-game seed run takes about 13.5 min on the VM ... so a 240-pair block is about 27 min." The worst case is 720 arm games, plus 240 incumbent games once per incumbent for seeds 5-6.

### What the judge's independent check and the shipped code add

These points come from code and its outputs. They are not in alternatives.md.

- **The thresholds that shipped are 0.1 t stricter than the note recommended.** `eval-paired.py::ship_decision` uses `(t_all >= 2.3 or t_up >= 2.6) and net >= 0` at looks 2 and 3. At look 1 it ships only if `t_all >= 3.0 and net >= 0` and stops if `t_all < 0.5 and t_up < 0.8`. At look 2 it stops if `t_all < 1.0 and t_up < 1.3`. Its docstring cites "owner PROMPTS 186-188 ... verdict.md". `judge/jsim.out` shows why the choice matters:
  - (iv-h) 2.3/2.6: null 2.0-2.1%, g4ship1 bootstrap 65.1%.
  - (iv-h) 2.2/2.5: null 2.5-2.6%, g4ship1 bootstrap 67.8%.
  - (iv-h) 2.0/2.3: null **3.7-3.9%**.
  - Inference: under 2.3/2.6, g4ship1's look-2 data (2.21 / 1.39 / +12) does not ship and goes to look 3. That matches the note's boundary warning.
- **The wins net >= 0 guard is weak against "trade" arms.** These are arms that gain the margin but lose games. In `judge/jsim2.out`, a "trade: capture +0.15, wins -2 pt" arm is promoted 12.5% of the time by (iv-h) 2.2/2.5. A "trade +0.15 / -1 pt" arm is promoted 25.9% of the time. `judge/jsim3.out` tests stronger guards, with the wins z-score written as net / sqrt(discordant):
  - wins z >= 1.0: the -2 pt trade drops to 1.5% and the -1 pt trade to 5.3%.
  - The cost: "pure capture +0.14, wins 0" falls from 37.8% to 12.9%, and g3lost-as-observed from 96.2% to 78.6%.
  - The note itself argues to keep net >= 0, since it "is the only check that a capture gain is not bought with lost games". It costs g3lost 84% vs 91%. The guard strength is a real trade-off that the 2023 team should simulate, not assume.
- Null rates hold up when the sign-flip uses other arms' pair distributions: all g4-era arms pooled (n=1901) and g3lost (n=473) both give the same ~2.0-2.7% across the rules (jsim.out).

### Tools and reuse verdicts

| tool | what it does | verdict for 2023 |
|---|---|---|
| `2024/tools/eval-paired.py` | Pairs arm vs control games on the same (seed, replay basename), split by tier. Reports wins gained/lost, net, an exact **two-sided** sign p, the paired capture-difference delta ± SE (t) and the identical-game count. `ship_decision(look, t_all, t_up, net)` encodes the 3-look rule. | **ADAPT.** Keep the pairing logic, `summarize`, `stats` and `ship_decision`. Change three things: (1) the census columns (`captured`, `enemyCaptured`) to a 2023 per-pair margin; (2) the seed regex `__s\d+(?=__bot[AB]\.bc24$)` to `.bc23`; (3) the tier file. Re-derive the thresholds by simulation on 2023 pairs. Do not copy 2.3/2.6. |
| `2024/research/criteria-review-2026-10-05/judge/jsim.py` (99 lines) | Vectorised numpy simulator. Each block bootstrap-samples 120 upper + 120 rest real pairs. Up to 3 looks. Joint random sign-flip = exact paired null; a tilted sign = alternatives. Per-look stats (net, t, t_up, sign-test criterion A, upper criterion B), then rule functions including a parameterised hybrid that returns promotion and games used. | **ADAPT** (small). It hard-codes a `pairs.json` path into a deleted 2024 scratchpad. It needs per-pair rows `{up, aw, cw, ad, cd}` and numpy. Reusable as the "power simulated first" step of C12 once 2023 has some real pairs. `CRIT` is the smallest gained count with exact two-sided p < 0.05, i.e. one-sided 2.5%. Criterion B in jsim is `tu >= 2 & net >= -5`. |
| `judge/jsim2.py`, `judge/jsim3.py` | Tilt alternatives with an independent wins target (harm and trade scenarios), and wins-guard variants (net >= 0, wins z >= 0.5, wins z >= 1.0). | **ADAPT** together with jsim.py. These scenarios are the right battery for choosing a guard. |
| The note's own `sim/` (extract, sim, power, hybrid, decision) | The note's main simulator and prior/decision analysis | **GONE**. Not on disk. The decision-analysis method (draw true effects from a prior, report Elo per 1,000 arm games and the missed-arm rate) must be rewritten if wanted. It is about 20 lines on top of jsim. |
| Skeptical-prior threshold `t >= 1.645·sqrt(1 + SE²/tau²)` | Turns a normal-prior P(delta>0) >= 0.95 into a t bar | **REUSE as-is** for reporting posteriors next to verdicts. |

### Pitfalls and implications for 2023 (C12)

- **Choose the per-pair margin by information per pair and validate it, as bc24 did.** bc24 required the margin to correlate with wins (0.73) and to have a stable wins-per-unit slope across arms (0.14-0.20). *Inference:* 2023 games end only by the 75%-island anchor win or at round 2000, since HQs are indestructible. The tiebreak goes islands held, then anchors placed, then elixir, mana and adamantium. A per-pair margin built from that order, plus rounds-to-win for decisive games, is the natural candidate. It must be checked for correlation with wins, and for the "already decided games" overstatement, before thresholds are fixed.
- **Simulate the boundaries before the first arm is judged, then freeze them.** Never pick or adjust a rule after seeing an arm's result. Give borderline arms a pre-registered third look instead.
- **Do not union two independent tests at full alpha each, and do not relax alpha to 0.10.** If an upper-tier route is wanted, build it as one hybrid whose combined null rate is simulated, as (iv-h) was.
- **Re-run a fresh incumbent control on new seeds at each promotion.** Reusing the promoted arm's own lucky games as the control biases later arms and correlates their errors.
- **Budget for multiplicity.** At 2.5% per arm, about six null arms against one incumbent give about a 14% chance of one false promotion.
- **Decide the wins-guard strength explicitly** with trade scenarios: net >= 0 lets 12-26% of trade arms through in the judge's sims.
- **Turn pair counts into wall-clock time using 2023's per-game time.** bc24 needed about 13.5 min per 120 games. The bc24 worst case is 720 arm games plus 240 control games per incumbent.

## Gap read: /home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc24/research/criteria-review-2026-10-05/power.md

Read in full (17,596 B, 276 lines). Nothing in it describes 2023 play; it is pure evaluation method from bc24. Code checked:
`/home/terryvanbelle/projects/vibe/2024/tools/eval-paired.py` (116 lines), and for context the 2023 repo's `tools/sprt.py`,
`tools/throughput.sh` and `tools/statlib.py`. Prior reports quoted only the headline (17% to 63-65%); that headline is the
verdict's, so this section covers what power.md itself adds.

### What the document is

A Monte Carlo of bc24's full two-stage promotion rule, written 2026-10-05 to answer the owner's question "are the shipping
criteria too strict?". Quotes: "resampling the per-pair outcomes of the 19 seeded band runs"; "No games were played and
nothing in the repo was edited". The rule it simulates is the **old** one, which `tools/eval-paired.py` no longer implements:
"(a) all-cell wins net > 0 with exact two-sided sign p < 0.05, or (b) upper-tier capture delta t >= 2 with all-cell net >= -5.
Stage 1 uses 240 pairs; confirmation pools 480 pairs and must still meet (a) or (b)." The rule adopted afterwards,
`(t_all >= 2.3 or t_up >= 2.6) and net >= 0` with looks at 240/480/720 pairs, comes from verdict.md and alternatives.md.
Its "63-65%" figure is also from verdict.md, not power.md. The nearest power.md row is "only: all-cell capture >= 1.645 SE
and net >= 0, one-shot": null 5.0%, +2 pt 47%, +3 pt 76%.

### Lessons with evidence

1. **Simulate the whole decision procedure, not one test.** The answer depends on the stage-1 gate, the OR of two criteria,
   the pooling and the informal practice, and no single-test power formula captures all of them. Three variants were
   modelled. "Written": stage 1 then pooled. "Practice": extension when "promising", which the author operationalised as
   "net >= +5 and all-cell capture t >= 1" and flagged as "my reading ... not a written rule". "One-shot": pooled 480 only.
   At +3 pt the results were written 25%, practice 41%, one-shot 50%.
2. **Calibrate the simulator against the real evaluator before trusting it.** "pairs.py ... reproduces every milestone
   row; for example, g4ship1 stage 1 gives net +9, capture +0.113 +- 0.093, upper +0.100 +- 0.142." Simulated SEs were
   compared with observed ones: all cells "0.088 at 240 pairs and 0.062 at 480 (observed about 0.09 and 0.06)"; upper tier
   "0.127 and 0.090 (observed 0.12-0.14 and 0.09-0.10)". Independence was checked too: "g4ship1's four runs share only 1-5
   of 120 (opponent, map, side) cells."
3. **The per-pair model, in enough detail to rebuild it.** Each pair is a gain, a loss or concordant.
   - A gain's continuous delta is drawn from the empirical "flip" distribution ("mean 2.26 in the upper tier, 2.73 in the
     rest"). A loss is drawn from minus that distribution.
   - A concordant pair is drawn from "the symmetrised empirical concordant distribution (sd 0.92 upper, 0.81 rest; 53-60%
     zeros)". The effect on concordant pairs is "a +-1 shift with the matching probability".
   - Discordance rate q: "0.18 upper and 0.14 rest (0.16 overall)". Pairs are split "exactly half in the upper tier (120
     per stage)".
   - Replications: 200k for null and harmful rows, 100k for the others, 60k per grid cell. "Monte Carlo SE is at most 0.2
     points."
   - **Inference:** the text does not say exactly how a win effect of w points becomes gain and loss probabilities. The
     natural reading is P(gain) - P(loss) = w/100 within the discordant mass.
4. **Couple the win effect and the continuous effect using the measured ratio.** "Real arms' capture gain is about half
   from flipped games (about 2.5 captures per flip) and half from games whose outcome did not change." The ratio was
   "roughly constant: g2cr 0.054 capture per point, g4ship1 0.056, g4pick 0.065, g3lost 0.074". A "realistic arm" was
   therefore defined as w points plus 0.05*w capture. Pure-win and pure-capture arms were also tabled separately, which
   shows that the win-only criterion (a) contributes little: pure win +3 pt gives one-shot 37%; pure capture +0.15 gives 32%.
5. **The headline power table (written rule, realistic arms).**

   | Win effect | Elo | Written | One-shot 480 |
   |---|---|---|---|
   | +1 pt | ~+13 | 4.4% | 12% |
   | +2 pt | ~+26 | 12% | 28% |
   | +2.5 pt | ~+32 | 17% | 38% |
   | +3 pt | ~+39 | 25% | 50% |
   | +5 pt | ~+65 | 61% | 89% |

   "The written rule reaches 50% only at about +4.5 points (about +58 Elo) and 80% only at about +6.5 points." The
   project's own arms "average +2.0 win points and +0.10 capture", and "their spread across arms is no larger than sampling
   noise". The rule's power was lowest exactly where the arms were. g4ship1's miss was "the expected outcome": "a real arm
   of g4ship1's apparent size fails about two times in three."
6. **A strict rule is not a safe rule; it is a slow one.** False promotion was already low: null 1.3% written, 3.8% one-shot
   at 480; a -2 pt realistic-harm arm 0.04%. "The exact sign test is conservative (1.9% at the null)." Requiring both stage 1
   and the pooled result to pass "cuts the error rate to a third". The cost was power, not safety.
7. **What made the procedure strict, largest effect first, quoted.**
   1. "The stage-1 gate ... halves power at +2 to +5 points."
   2. "Criterion (b) reads only the upper half. Its effective sample is 240 pairs at confirmation, and it ignores capture
      gains in the rest tier."
   3. "The all-cell capture delta (SE 0.06 at 480) is the most precise statistic the band produces, yet no criterion uses
      it."
   4. "The exact two-sided sign test needs about +4 points to reach 50% at 480 pairs." With about 77 discordant pairs it
      needs net >= +19, and g4ship1 had +12.
   5. "Even an ideal rule needs 1,000-1,500 pairs for 80% power at +2 points."
8. **Where the gain lands matters for a tier-restricted criterion.** At +3 pt / +0.15: uniform gives 25% written; all in
   the upper tier 62%; all in the rest tier 14%. Real cases: "g3lost was promoted that way, with upper +0.24 and rest +0.01",
   but criterion (b) "is blind to gains in the rest tier: g4crumb had rest +0.18 and upper -0.03."
9. **A fixed non-inferiority margin in raw counts changes meaning with N.** "net >= -5: that is -2.1 points at 240 pairs and
   -1.0 at 480. A -2-point arm still clears it 32% of the time at 480 pairs and 55% at 240." The real false-promotion risk
   is the "trade" arm, which gives up wins for the secondary metric: -2 pt / +0.15 capture is promoted 8.7% written and 18%
   one-shot. Adding (c) raises it to 30%; tightening (c) to net >= 0 brings it to 15%. The adopted bc24 rule uses net >= 0
   (eval-paired.py `ship_decision`).
10. **Discordance rate q.** "The null rate does not depend on q. Power falls as q rises: more discordant pairs means more
    noise around the same net." At +3 pt one-shot: q 0.11 gives 62%, q 0.16 gives 50%, q 0.21 gives 43%. Arms that change
    play only after an event have "lower q and more identical games (g3lost, g4crumb: q about 0.10), which helps them."
11. **Pairs needed, with VM cost (bc24 VM, "about 13.5 minutes per 120 arm games").** Current rule: 80% at +3 pt needs about
    1,000 pairs and at +2 pt about 2,200. With (c), "all-cell capture >= 2 SE, net >= -5", the figures are about 600 and
    1,400. At 960 pairs the current rule gives null 3.8%, +2 pt 46%, +3 pt 78%, "about 1 hour more VM time per arm".
    "Beyond 480 pairs the incumbent's control also needs new seeds, but only once per incumbent."
12. **Judge rules by expected Elo per arm tested, under a prior from the track record.** With the prior N(+2, 1.5) on the
    true effect and 13 Elo per point: current written rule 17% promoted, +7.4 Elo per arm; one-shot 33%, +13.3; with (c)
    one-shot 44%, +17.1; "capture >= 1.645 SE and net >= 0, one-shot" 48%, +18.4. P(promote and harmful) stays 0.1-0.2%.
    Under the sceptical prior N(0, 2) the figures are written +2.2 and loosest +5.9, with harmful 0.2-0.7%. "Under every
    prior tried, each loosening shown raises the expected gain." The written rule captured "about 40% of the Elo" of the
    loosest rule.
13. **A futility-only first look is almost free.** It stops "only when net < 0 and all-cell capture t < 0" and otherwise
    decides on the pooled 480. It "stops 36% of null arms and 72% of -2-point arms early, and only 3% of +3-point arms".
    Power equals one-shot (+3 pt 50%), and null is 3.7%. bc24's current `ship_decision` keeps this shape with explicit
    thresholds: look 1 stops when t_all < 0.5 and t_up < 0.8, and ships early at t_all >= 3.0.
14. **Elo conversion and the ladder's blind spot.** "g_iter4's per-opponent band win rates give a mean p(1-p) of 0.126. One
    band win point is therefore about 13 Elo." "The ladder's per-build SE is 33-39 Elo, so the ladder cannot verify a +2-3
    point arm either." **Inference:** this follows from dElo/dp = 400/(ln10 * p(1-p)); at p near 0.5 a point is about 7
    Elo. The conversion must therefore be recomputed from 2023's own band win rates.

### Caveats the document raises (pitfalls to carry over)

- **Shared control games correlate arms.** "Arms tested against the same control can pass or fail together. The g4 arms'
  stage-1 nets were all positive (+1 to +9), which may partly be luck in the g_iter4 control draws."
- **Selection inside a stacked arm.** g4ship1 "stacks two arms chosen on their seed 515151/616161 results". "The
  confirmation seeds alone (net +3, capture +0.17 +- 0.09) are the unbiased read." True size plausibly "+1 to +2.5 points
  and +0.10 to +0.17 capture".
- **Unwritten practice.** The analyst had to infer the "extend if promising" rule. Write extension rules down so they can
  be simulated.
- **Not modelled.** Opponent-level heterogeneity of effects, which matters for band-to-ladder transfer, and the basics
  battery, which "can only lower every promotion rate".
- **Prior is for delivered arms only.** "Arms reach the band only after a delivery gate, so the prior describes delivered
  arms."

### Tools and reuse verdicts

| Tool | Where | Verdict |
|---|---|---|
| power-sim scripts: `pairs.py`, `power.py`, `run_all.py`, `run_n.py`, `run_futility.py`, `tables.py`, `summarize.py` (numpy) | "scratchpad, criteria/power-sim/" | **Not available: rebuild.** A grep finds no `power-sim`, `power.py` or `run_all.py` anywhere under `/home/terryvanbelle/projects/vibe/2024`; only the .md describes them. Lessons 2-4 above contain the full spec. A rebuild is about 150-250 lines of numpy (**inference**). |
| Calibration data | the 19 `census-*-seeded.csv` files "on the VM" | **Mostly absent.** Only 6 are in `/home/terryvanbelle/projects/vibe/2024/research/`: g1basics, g1basics-conf, g2bc, g2nonav, g_iter1, g_iter1-conf. The g3/g4 runs are not local. Irrelevant for 2023 anyway: calibrate on 2023 pairs. |
| `eval-paired.py` | `/home/terryvanbelle/projects/vibe/2024/tools/eval-paired.py` | **Adapt** (agrees with bc24-method and bc24-play). Concrete changes for 2023: (1) the `SEEDSEG` regex hard-codes `__bot[AB]\.bc24$`; change it to `.bc23`. (2) `load()` reads census columns `won`, `captured`, `opp`, `rounds` and `enemyCaptured`; swap `captured`/`ecap` for the 2023 per-pair margin. (3) `ship_decision` thresholds 2.3/2.6/3.0/0.5/0.8/1.0/1.3 were tuned on bc24 capture data; re-derive them with a rebuilt simulator. (4) The "identical" count compares (won, rounds, cap, ecap), which gives the concordant share for free. (5) `sign_p` uses `math.comb` (Python 3.8+). |
| 2023 `tools/sprt.py` | `/home/terryvanbelle/projects/vibe/2023/tools/sprt.py` | **Keep as screen only.** Its docstring still says "no draws in BC20" and sets p1 = 0.58 ("~56 Elo"). By power.md's numbers, typical real arms are +13 to +39 Elo on a band. **Inference:** an SPRT tuned to 56 Elo head-to-head will mostly return CONTINUE or REJECT for typical-size arms. Use it for crashes and regressions, not acceptance. |
| 2023 `tools/throughput.sh` | `/home/terryvanbelle/projects/vibe/2023/tools/throughput.sh` | **Use** to measure 2023's minutes per game, which replaces bc24's "13.5 minutes per 120 arm games" in the pairs-needed table. |

The 2023 repo has no paired evaluator and no power simulator yet (checked: `tools/` lists neither). `statlib.py` holds
correlation and onset helpers only.

### What to do for 2023 (inference, derived from the above)

1. Before fixing any ship rule, collect one seeded control-vs-control (or control-vs-trivial-arm) batch on 2023 maps. From
   it, measure per tier: the discordance rate q, the flip distribution of each candidate margin, and the concordant
   distribution, including its share of zeros. Candidate margins, per SYNTHESIS rule 6: islands held at the end, anchors
   placed, island count integrated over rounds. Candidates specific to 2023's lexicographic tiebreak: the tiebreak vector
   difference, or win round for anchor wins.
2. Rebuild the resampling simulator to the spec in lessons 2-4. Validate it the way power.md did: reproduce the
   evaluator's numbers on real runs, and match simulated SEs to observed SEs at the planned N.
3. Pick the statistic with the most information per pair. power.md's grid shows that a precise all-cell continuous
   statistic beats the sign test and tier-restricted criteria. Use **net >= 0**, not a raw-count margin, as the
   non-inferiority guard, and a **futility-only** first look.
4. Tabulate power at +1/+2/+3/+5 points and the expected Elo per arm under a track-record prior. Expect to need about
   1,000 pairs for 80% power at +3 points if 2023's per-pair noise resembles bc24's (**inference**). Budget VM time from
   `throughput.sh`.
5. Refresh the control seeds per incumbent, and note when several arms share one control. Never pool a stacked arm with
   the seeds used to select its parts.

## Gap read: /home/terryvanbelle/projects/vibe/2025/agents/alice/tools/gate-read.sh

Source: the script (code, read directly, 3,426 B). Context from the filtered reading room only:
`readroom-no2023/bc25/agents/alice/TRAINING_LOG.md` (lines ~9526-9541, 10303-10330, 13905-14005, 14370-14575,
14898-14910, 16180-16210, 16815-16840, 16935-16945) and `LEARNINGS_ARCHIVE.md` (lines 610-620, 1550-1590, 1720-1732,
2585-2665, 2885-2935). Writer formats checked in code: `/home/terryvanbelle/projects/vibe/2025/tools/gauntlet.sh:195-197`
and `/home/terryvanbelle/projects/vibe/2025/tools/tournament.sh:174`. No 2023-game content was found or used.

### What the tool does

`tools/gate-read.sh gauntlet/<run-id> [opponent ...]` reads a bc25 gauntlet `results.txt` and does three things:

1. It prints **four standing pre-checks to stderr, unconditionally, before any numbers**: SCARCITY, UNIT, BITE and
   DIVERSION. They print "whether or not I think I need it" (script comment).
2. It prints one row per opponent: record, `SW` (maps where the bot won both sides), `SL` (maps it lost on both sides),
   split, `margin = wins - N_maps`, and an **identity column**, `OK` or `MISMATCH (wins-N=…, SW-SL=…)`.
3. It prints `exceptions:`, the sum of the `EXC` lines' 5th field. That field is `grep -c "^\[$SIDE:.*Exception"`,
   so it counts the bot's own side only.

The script's header comment fixes the gauntlet RESULT layout as `RESULT <OPP> <MAP> <MY-SIDE> <WINNING-SIDE> <ROUNDS>`
("I win a game iff field 4 == field 5. Field 2 is the OPPONENT, never the winner"). The comment cites
`tools/gauntlet.sh:148`, but the current writer is at line 195. The line reference is stale; the layout still matches.

### Lessons, with evidence

**0. The meta-lesson: "a lesson you wrote is not a control; install the check where the mistake happens."**
- Origin (LEARNINGS_ARCHIVE "a lesson written THREE times is not a lesson, it is a missing control"): the same
  scarcity error happened in iterations 20, 26 and 39a. The log calls this "two prior write-ups that did not stop the
  third."
- First evidence that it works (TRAINING_LOG ~14506-14520): hours after the SCARCITY line was installed, alice drafted
  an iteration-40 candidate that "*was* iteration 20". The printed check named the precedent by number, and
  "Iteration 40 is closed, unbuilt, at zero game cost." Alice's own caveat: "the sample is one … what it demonstrably
  prevented here is a screen, not an accept."
- Admitted weakness (LEARNINGS_ARCHIVE ~2614): "it fires when I *read* a result, not when I *design* a candidate — so
  it can still cost a screen, but not an accept. That is a strictly smaller blast radius, not a cure."
- The doctrine's number varies between documents: "Doctrine 16" in this script and alice's log, §17 in
  `bc25/METHODS.md`, and "doctrine 19" in our bc25-docs report. It is the same rule.

**1. SCARCITY: name the binding resource before you claim waste.** Three costs:
- i20 freed soldier turns while paint was binding. Result: null.
- i26 spent chips while paint was binding. Result: −21 net swept.
- i39a measured "1,315 idle build-turns" as "pure waste". The tower could not afford the paint on 96% of
  splasher-gate firings. The candidate drove "gate firings 1374 -> 0 on two maps" and splashers to 0, because "the
  idling *was* the accumulation mechanism".
- Generalised tell: "a 96% 'unaffordable' rate is not a failure rate if the other 4% is what the 96% was saving up
  for. Any denominator that includes the accumulation phase of a savings behaviour will read as waste."
- 2023 translation (**inference**): an HQ that idles while saving 80 Ad + 80 Mn for an anchor, or saving mana for
  launchers, will look like waste in the same way. So will a carrier waiting at a well. Name the binding resource first:
  mana, adamantium, carrier trips, or island-capture tempo.

**2. UNIT: the gate and the floor must be in the same unit.** Derivation (LEARNINGS_ARCHIVE ~2626), with every map
played on both sides:
- `wins - N = SW - SL = net_swept` exactly.
- `wins - losses = 2*net_swept`, so its sd is doubled.
- `Var(net_swept) = decisive`, so `sd(net_swept) = sqrt(decisive) = sd(wins)`.
- What it caught: another lineage's gate "computed the sd of the **win count** while quoting its threshold on the
  **margin**". Every gate it produced was "1.0 sd wearing a 2.0 sd label", with a one-tail false-accept rate "near 16%
  where it believed it had 2%".
- Alice's numbers: census null `sd_net_swept = 5.29`, gate +12, so 2.27 sd. A 25-map screen with 7 decisive maps has
  null sd 2.65, so the gate scales to "+6.0 net swept" there. Accept i39c: 91–59, SW 17, SL 1, split 57, net swept +16
  (3.02 sd), identity `91−75 = 16 = 17−1`.
- Two independent tools check the same identity: `noise-floor.py` asserts it, and gate-read prints it. The log calls
  this "the reconciliation doctrine 5 asks for rather than a single tool trusted twice".

**3. BITE: run the mechanism check on a map where the mechanism is known to act.**
- The iteration-38 error (TRAINING_LOG ~13907): `alice_i38a` vs `alice_iter30`, one game on `DefaultMedium`, moppers
  by r200 "arm 9, baseline 8". The arm enforced exactly 1 in 4, which is the intended rate, so it is "near-inert on any
  map whose fixed draw already sits near 25%". Only a skewed map would show a difference: "the id3/offset-17 case was
  5 of 12". The game "says **nothing either way**".
- i38 was then rejected on its screen: i38a +3 (+1.13 sd), i38b +1 (+0.38 sd). The arm-to-arm identity check found
  "10 of 50 cells identical, 40 differ", which shows the arms were genuinely different builds.
- **BITE proves action, not benefit** (LEARNINGS_ARCHIVE ~2909):
  - i45 passed BITE "spectacularly". On BatSignal the arm won "at round 919 against the control's 1209".
  - Its 75-map census lost: 64 vs 86 wins, median winning round **1582 vs 972**, 56.2% vs 73.3% of wins by the instant
    win. The single map "got the **sign backwards on the mechanism's own metric**."
  - Rule: "record it as evidence of **action only**, and never let it stand in for the census".
- Done right (i39c): alice chose a loss replay where the mechanism should fire (`AlarmClock`). Splashers built in the
  400–600 window were "+14" vs "+8".
- 2023 translation (**inference**): most 2023 mechanisms act on only some maps. Examples are clouds, currents, island
  count and distance, 1 vs 4 HQs, and elixir conversion. Keep a per-mechanism list of bite maps. A cloud-handling change
  checked on a cloudless map, or an anchor change on a map whose islands are never reached, is the i38 error.

**4. DIVERSION: measure what diverted turns were doing before.**
- i44 diverted "hungry" soldiers to remembered towers and lost **−58 net swept**, "the largest negative ever measured
  here".
- The branch was "inert on 96.2% of turns". Those turns were the soldier painting and capturing ruins. "Paint was not
  binding; ruin-capture TEMPO was". Towers were "4 v 8 by round 200".
- The mechanism also "fired as designed (late paint transfers 14 against the control's 2) and **still failed its own
  objective**". Starvation deaths were 3/2/5 vs 2/1/8.
- Re-open standard: "**a diversion may only capture turns that are already producing nothing.**"
- It caught the next iteration. The i45 draft ("steer the idle soldier toward the nearest empty tile in vision") was
  probed first: there was "no empty tile in vision at all on 72–92% of those turns". The draft was "Killed for the cost
  of two matches instead of 150 games."
- An independent route reached the same variable. Between near-identical bots, tower count at r300 "decides the match
  13 times in 14". The exception was `Bunny__botA`, which led 11 v 7 towers and still lost.
- 2023 translation (**inference**): pulling carriers off mining to carry anchors, escort, or flee, and pulling
  launchers off a front to chase, are all diversions. Measure the mining trips or front-holding those turns produced
  before. 2023's analogue of ruin-capture tempo is plausibly early island capture and economy tempo; this is
  unverified.

**5. RESULT field semantics: read the writer, not the data.** (LEARNINGS_ARCHIVE ~1550)
- Alice's tally of a tournament `results.txt` gave "alice 75-75 vs bob, alice 75-75 vs carol, winning side A=180 /
  B=180, and **zero swept maps**". Alice nearly reported "the tournament runner is broken".
- Cause: the tournament writer is `RESULT <teamA> <teamB> <map> <winnerSide> <rounds>`, so field 2 is team A, not the
  winner. Corrected, the run was "alice 39-111 vs bob (26.0%) and 103-47 vs carol (68.7%)".
- **Pitfall:** the project had **two RESULT formats with different field meanings**. The tournament writer has team A
  in field 2 and the winner in field 5. The gauntlet writer has the opponent in field 2 and the winner in field 5. The
  script's comment covers only the gauntlet format.
- Lessons quoted: "Real systems are lopsided; file formats are symmetric. Treat exact symmetry as evidence about the
  parser first." And: "when the uncertainty is about the SEMANTICS of a field … the discriminating case is the code
  that writes it. More data cannot resolve a definition."
- A phantom bug report also "teaches the other two lineages to distrust an instrument that was fine".

**6. Report split and sweep counts beside every head-to-head.** gate-read's first run (TRAINING_LOG ~10303):

| opponent | record | SW | SL | margin |
|---|---|---|---|---|
| `alice_flood` | 44-6 | 19 | 0 | +19 |
| `alice_iter7` | 42-1 | 20 | 0 | +20 |
| `alice_iter24` (the gate) | 26-24 | 4 | 3 | +1 |

- The headline across all three opponents was 81.3%, while the only row that matters is a coin flip. "The strong rows
  are strong *because* they are irrelevant."
- "sweeps in *both* directions" is "exactly what a mechanism that perturbs without improving looks like".

**7. Sign convention on screens.** Alice ran screens with the baseline in `BOT` and the arms as opponents, so "an arm is
good when the BOT loses". gate-read always reports the bot's side, so every such read was inverted by hand. Alice
wrote: "this is the run type where I have inverted the sign before". bc25-docs notes that carol's `margin.py` refuses a
signed margin without `--candidate`; that is the installed fix.

### Code-level pitfalls in gate-read itself (read from the code)

- **One game per side per map is assumed.** Sweeps are counted with `wm[k]==2` and `lm[k]==2`, keyed on map name
  (`$3`) only.
  - Repeats of a map (several seeds) make sweeps miscount. `nmaps` also undercounts, so the identity check prints
    `MISMATCH`. That failure is loud, which is good.
- **A missing or `?` result counts as a loss**, because `$4 != $5`.
  - A map with only one game recorded passes the identity check silently when that game is a win. It fails it when
    that game is a loss.
  - So the identity column catches unit errors but **not all incomplete runs** (worked through by hand from the awk).
- **Pointed at a 2023 run, it exits 1 with "no results.txt"**, because 2023 writes `results.csv`. It fails loudly
  rather than printing an empty table.
- **The pre-checks go to stderr.** `gate-read.sh … > file` leaves them on the terminal and out of the saved file. That
  is intentional for a human reader, but an agent capturing only stdout will never see them (**inference**).

### Tools and reuse verdicts

| Tool | Where | Verdict |
|---|---|---|
| `gate-read.sh` | `/home/terryvanbelle/projects/vibe/2025/agents/alice/tools/gate-read.sh` | **Adapt, not reuse verbatim.** Port it into 2023's `tools/summarize.py` or a small `gate-read.py` over `results.csv`. Use the named columns `opponent,map,bot_side,winner_side,rounds,bot_result,reason,seed`, which removes the field-position hazard. Changes: (1) pair on (opponent, map), and also on the seed pair when CELLS supplies seeds, and **refuse** unless each pair has exactly one A and one B game; (2) exclude `unknown`/`dud` rows and report them, rather than scoring them as losses; (3) print `SW, SL, split, net_swept, decisive, sd=sqrt(decisive), in-sd` and the `wins-N == SW-SL` identity; (4) add `--candidate <name>` so screens with the baseline in `BOT` print the arm's side, or refuse to print a signed margin without it; (5) keep the four pre-check headings printed unconditionally, and replace the bc25 worked examples with 2023 ones as they occur. Inference: about 40-60 lines of Python. |
| 2023 `summarize.py` | `/home/terryvanbelle/projects/vibe/2023/tools/summarize.py` | **Extend.** It reports wins per opponent, the side split, unknowns, duds and reasons. It has **no SW/SL/split/net-swept or identity check** (grep for `swept` in `2023/tools` finds nothing outside `compare.py`). |
| 2023 `compare.py` | `/home/terryvanbelle/projects/vibe/2023/tools/compare.py` | **Keep; one hazard.** It keys on `(opponent, map, bot_side)` with plain dict assignment. If a CELLS file repeats a cell with several seeds, later rows **silently overwrite** earlier ones (read from the code at line 19). Add `seed` to the key, or refuse duplicates. Its `sweeps()` requires `len(v)==2`, so the same duplicates would also drop those maps from the sweep counts. |
| Pre-check text | the `PRECHECK` heredoc in gate-read.sh | **Reuse the pattern.** Install the 2023 project's standing checks as text printed by the verdict reader itself, not as LEARNINGS prose. Alice's evidence: the printed check stopped a repeat that two write-ups had not. That is one instance, and it prevented a screen, not an accept. |

### Coverage note

A grep for `BITE` and `DIVERSION` in bc25-docs, bc25-tools-code and SYNTHESIS finds nothing; this section adds both.
UNIT is already covered: bc25-docs lines 347 and 771 and SYNTHESIS line 117 carry the "1.0 sd wearing a 2.0 sd label"
incident, and bc25-docs carries alice's +12 / 5.29 / 2.27 sd gate. What this section adds there is the exact
`wins-N == SW-SL` derivation and the printed identity column. A grep for `39a` finds no hit in those three reports,
so the i20/i26/i39a scarcity chain is new here too.

## Gap read: /home/terryvanbelle/projects/vibe/2024/research/criteria-review-2026-10-05/judge/jsim.py

**What it is.** These are the judge's power simulators for the bc24 criteria review: `jsim.py` (99 lines), `jsim2.py` (38), `jsim3.py` (37) and their `.out` files. I read the code directly from the repo. For context I read only the filtered `readroom-no2023/bc24/.../verdict.md`, which describes them as "Judge's simulator (independent re-implementation, census copies only)" with "8,000 draws per repetition, 4-8 repetitions per row". The alternatives.md section above already gives their role and the main reuse verdict. This section adds four things: a code-level audit, a smoke test I ran on synthetic pairs, `.out` numbers not quoted above, and the concrete changes 2023 would need. Nothing here describes 2023 play.

### How the code works (from the source)

- **Input.** `pairs.json` maps an arm key (`g4ship1`, `g4ship1-conf`, `g3lost`, ...) to rows `{up, aw, cw, ad, cd}`. `arr()` builds three arrays:
  - `up`: whether the pair is upper tier;
  - `dw = aw - cw`: the wins change, in {-1, 0, +1};
  - `dc = ad - cd`: the change in the per-game capture difference.
  The path is hard-coded at line 4 to a 2024 session scratchpad and is evaluated **at import time**, so `jsim2` and `jsim3` fail at import too. That directory no longer exists (checked).
- **`CRIT[n]`** is the smallest gained count with an exact two-sided sign p < 0.05 and g > l. Values I printed: n=6→6, 10→9, 20→15, 38→26, 50→33, 76→48, 100→61, 150→88, 200→115. n ≤ 5 can never pass. The array is capped at index 799. `sign_p()` is defined but unused.
- **`stats()`** is vectorised over N simulated arms. It returns:
  - `net`;
  - the paired t on `dc` (ddof=1);
  - `tu`, the same t on the upper-tier subset;
  - criterion A: sign test, g > l and g ≥ CRIT;
  - criterion B: `tu >= 2 & net >= -5`. The -5 is an absolute count that does not scale with n.
- **`simulate()`** builds each look block by bootstrapping **120 upper + 120 rest** real pairs with replacement. The 120/240 constants are hard-coded here and again in `jsim2.sim_tilt`. It returns stats at looks 1-3 (240/480/720 pairs).
  - Null: one random sign per pair multiplies **both** `dw` and `dc`. That keeps the real within-pair coupling of wins and margin. It is an exact paired sign-flip null.
  - Alternatives: the same flip, with P(+) set by `tilt`.
- **`rules()`** returns promotion masks and, for the sequential rules, arm games used: 240 if stopped or shipped at look 1, 480 at look 2, 720 at look 3. The rules are:
  - three legacy bc24 rules: R0 written, R0 practice and R0 pooled480;
  - `(i)+screen`;
  - the hybrid `(iv-h)` at four threshold pairs. Its screen statistic `max(t, tu - (cu - ca))` matches the futility rule in the shipped `eval-paired.py::ship_decision` (`t_all < 0.5 and t_up < 0.8`, then `< 1.0 / < 1.3` for 2.3/2.6; checked);
  - the all-cell `(iv) 2.1`.
  The `ca, cu` arguments of `rules()` are unused, because the loop overrides them.
- **`jsim2.sim_tilt(cap_target, win_target)`** first orients every pair so that its capture change is ≥ 0. It then flips signs with P(+) = `0.5 + cap_target / (2·mean|dc|)`.
  - If `win_target` is given, it **re-draws the sign of every discordant wins change independently** of the capture change. That **decouples wins from margin**, so the "trade" and "pure capture" rows are pessimistic about coupling by construction.
  - If `|cap_target| > mean|dc|`, the tilt saturates without warning. I confirmed this: asking for -5.0 on synthetic data returned -0.821, which was the synthetic mean|dc|.
- **`jsim3`** adds `disc` (the discordant count) by monkey-patching `jsim.stats` and `jsim2.stats`. I confirmed that this works. `disc_of()` is a dead stub. Its guards are `net >= 0`, `net >= 0.5·sqrt(disc)` and `net >= 1.0·sqrt(disc)`, applied at every ship decision of the 2.3/2.6 hybrid.
- **Seeds and sample sizes.** Seeds are fixed (jsim argv default 1, jsim2 11, jsim3 23), so the `.out` files are reproducible given `pairs.json`. Sizes are N=8000 × R=8 (jsim), × 5 (jsim2) and × 4 (jsim3). The same rule agrees across files within about 0.5 pt:
  - 2.3/2.6 null: 2.0-2.1% (jsim) vs 1.9% (jsim3);
  - g4ship1 observed: 65.1% vs 65.3%;
  - g3lost: 96.3% vs 96.2%;
  - g4pick: 29.5% vs 29.5%.

### Smoke test I ran (scratchpad copies, synthetic pairs, no games)

- **Environment.** The system `python3` has **no numpy**. The scripts run unchanged on `/home/terryvanbelle/projects/vibe/2025/tools/.venv/bin/python` (numpy 2.4.6, Python 3.11.2) once the path is patched. One N=4000, 1-replicate run of `simulate` + `rules` took 7.0 s. *Inference:* a full `jsim.py` run (9 scenarios × 8 × N=8000) is on the order of 15-20 min.
- **The null rate is not portable. It depends on how strongly wins move with the margin.** I used the same synthetic margin pairs both times; only the wins column differed.
  - Wins independent of the margin (corr -0.05): `(iv-h) 2.3/2.6` null **0.9%**, `2.2/2.5` 1.1%, `(i)+screen` 0.8%.
  - Wins coupled to the margin (corr 0.53): **2.1%**, 2.7% and 2.0%. That reproduces jsim.out's 2.0-2.6% on real bc24 pairs.
  - The reason: the `net >= 0` guard is nearly free when wins follow the margin, and it cuts the rate in half when they do not.
  - So the bc24 thresholds hit about 2.5% only because bc24's wins/capture correlation was 0.73. 2023 must re-simulate on its own pairs.

### Lessons with evidence (from the .out files; not quoted in the section above)

1. **Pair variance matters as much as effect size.**
   - g3lost (mean cap delta +0.140) and g4ship1 (+0.144) have nearly the same effect. Under `(iv-h) 2.3/2.6`, g3lost ships **96.3%** of the time and g4ship1 **65.1%**. Under R0 written the gap is 83.8% vs 17.3% (jsim.out).
   - alternatives.md attributes this to identical games (86/234 vs 16/240).
   - For 2023: anything that makes arm and control games identical when behaviour is unchanged buys power for free.
2. **Small effects are invisible at 720 pairs.**
   - Uniform +0.05 ships 11.0-13.4% of the time under every rule. +0.10 ships 36-41% and +0.20 91-92% (jsim2.out).
   - verdict.md scales +0.10 to "about +1.7 pt, +21 Elo". *Inference:* gains under about 10-15 Elo will usually be parked. That is acceptable only if arms are sized to aim higher.
3. **Threshold sensitivity, as one curve** (jsim.out; g4ship1 sign-flip null and g4ship1 bootstrap):

   | (iv-h) thresholds | null | g4ship1 bootstrap |
   |---|---|---|
   | 2.0/2.3 | 3.7% | 72.4% |
   | 2.2/2.5 | 2.5% | 67.8% |
   | 2.3/2.6 | 2.0% | 65.1% |
   | 2.4/2.7 | 1.6% | 62.2% |

   Going from 2.0 to 2.4 cuts the null rate by about 2 points and costs about 10 points of power.
4. **Trade arms are the most expensive to judge.**
   - Arm games used: "trade: capture +0.15, wins -2 pt" 628, "-1 pt" 604, "+0.10 / -2 pt" 562. Compare about 507 for uniform +0.14, about 359 for a null and 262-296 for harmful arms (jsim2.out, 2.2/2.5).
   - The futility screen looks only at the margin, so trade arms run to look 3 and are then blocked by the wins guard.
   - *Inference:* a wins term in the futility screen would save games.
5. **When wins decouple, the guard eats power.**
   - "pure capture +0.14, wins 0" ships 40.2% under 2.2/2.5 vs 66.3% for coupled uniform +0.14 (jsim2.out).
   - With the wins z ≥ 1.0 guard it falls to **12.9%** (jsim3.out).
   - For 2023: measure the margin-wins correlation first, because it decides the guard choice.
6. **Two 240-pair blocks of the same arm can disagree.**
   - Pooled g4ship1: n=480, +0.144, +0.0250 wins/pair. Confirmation seeds only: n=240, +0.175, +0.0125 (jsim.out).
   - *Arithmetic inference:* the first block was therefore about +0.11 capture and +0.0375 wins/pair, i.e. more wins and fewer captures than the confirmation block.
   - Do not judge on one block without a pre-registered next look.
7. **The legacy "as practised" rule doubled the false-promotion rate.** R0 written ran 1.2% and R0 practice 2.4% on the same null (jsim.out). In practice, an informal "t >= 1 is promising, extend" step is a second test.
8. **Write up the guard result before shipping the verdict.** The filtered verdict.md still contains the literal placeholder `GUARD_RESULT` after "ships 25% of the time, against 18% under current practice". jsim3.out is the only record of the guard comparison: null 1.9 / 1.8 / 1.7%, uniform +0.14 64.0 / 63.0 / 59.4%, "trade +0.15 / -1 pt" 24.6 / 11.9 / 5.3%. Grep for placeholder tokens before committing a decision document.
9. **Commit the simulator's input with its output.** The bc24 `pairs.json` (and the note's `sim/`) lived only in a scratchpad. None of these numbers can be regenerated, and the bc24 data cannot be used to sanity-check a 2023 port.

### Tools and reuse verdicts

| item | verdict for 2023 |
|---|---|
| `judge/jsim.py` | **ADAPT** (about 1-2 h, inference). Required changes: (1) take the `pairs.json` path from argv and stop loading at import time; (2) replace the 120/120 block constants with the 2023 gauntlet's per-look upper/rest counts; (3) delete the R0/(i) legacy rules and keep `(iv-h)` and `(iv)` as templates; (4) add a per-stratum tilt so that upper-only and rest-only effects can be simulated (the note's lost `sim/` did this and jsim does not); (5) extend `CRIT` if a look ever exceeds 799 pairs. The keepers are the sign-flip null, the stratified bootstrap, `stats()` and the parameterised hybrid with its games count. |
| `judge/jsim2.py` | **ADAPT** with jsim. Its harm, uniform and trade battery is the right set of scenarios for choosing thresholds and a guard. Label decoupled-wins rows as pessimistic, and assert `0 <= tilt <= 1`. |
| `judge/jsim3.py` | **ADAPT**. Fold `disc` into `stats()` and drop the monkey-patch and the `disc_of` stub. Keep the three guards as candidates. |
| pairs.json builder | **WRITE** (about 10 lines, inference). No code that writes `pairs.json` survives. From `eval-paired.py`'s `load`/`pairs`, each `(c, a)` pair maps to `{'up': c['opp'] in upper, 'aw': a['won'], 'cw': c['won'], 'ad': a['cap']-a['ecap'], 'cd': c['cap']-c['ecap']}`. For 2023, `cap`/`ecap` become the chosen per-game margin and `SEEDSEG` must match `.bc23`. |
| `2023/tools/compare.py`, `2023/tools/sprt.py` | Context only, our own 2023 code. `compare.py` pairs games on (opponent, map, bot_side) and reports flips and identical cells. It has no margin, no t and no tier split, so it is a candidate base for the pair builder. `sprt.py` is a wins-only SPRT (p0 0.50 / p1 0.58) whose docstring still says "no draws in BC20". 2023 has **no** margin-based paired test or power simulator yet, and jsim is the only committed one in any prior repo. |

### Pitfalls

- **Do not copy 2.3/2.6, or any thresholds.** The null rate depends on wins-margin coupling (see the smoke test), on block composition and on the margin's distribution. Re-calibrate on 2023 pairs, then freeze.
- **jsim.out's "half its observed effect" header is mislabelled.** It prints the observed "+0.144" because it calls `dc.mean()` on the raw data, but the simulated effect is +0.072. Its rows (e.g. (iv-h) 2.2/2.5 22.6%) are for +0.072.
- **"As observed" bootstrap rows are plug-in power at a selected point estimate.** *Inference:* for an arm that was examined because it looked good, these rows overstate true power. Use the uniform-tilt rows for planning.
- **Precision.** Use at least 32,000 simulated arms per row (jsim3's minimum). Between files, rows drift by about 0.5 pt, so do not tune thresholds finer than that.
- **Bootstrapping 720 pairs from a 480-pair pool** treats the observed pairs as the population. With few real 2023 pairs, plan from tilted scenarios, not from bootstraps.

## Gap read: /home/terryvanbelle/projects/vibe/2025/agents/carol/carol-tools/covar/sizestrat.py

**Sources.** Code read directly:
- `2025/agents/carol/carol-tools/covar/sizestrat.py` (4,012 B)
- `2025/agents/carol/carol-tools/covar/mapcovar.py` (3,874 B)
- `2025/agents/alice/tools/map-axis-split.py` (8,330 B)

Documents read only from the filtered reading room `reference/readroom-no2023/bc25/`:
- `agents/carol/carol-tools/towercensus/README.md`
- `agents/carol/TRAINING_LOG.md`, lines 9050-9330 and 9590-9620
- `agents/carol/LEARNINGS_ARCHIVE.md`, lines 1140-1175
- `agents/alice/TRAINING_LOG.md`, lines 6115-6170, 6450-6505, 15885-15990 and 16100-16140
- `agents/alice/LEARNINGS_ARCHIVE.md`, lines 900-1000
- `tools/mapdata/README.md`

I also ran two read-only commands, listed below. They take under a second, play no games and write no files:
- `sizestrat.py` over the committed 2025 tournaments
- `mapcovar.py --corpus`

### What the three tools compute (from the code)

- **`sizestrat.py`** reads `tournaments/<run>/results.csv` in the 2025 three-body format: `team_a,team_b,map,winner_side,winner_bot,rounds`.
  - For every bot in every tournament it prints the overall win%, then the win% in four **absolute** area bins: `tiny<=900`, `small` 901-1600, `large` 1601-2500, `huge>2500`.
  - It also prints Spearman rho (midranks) between per-map win fraction and map area, with the normal-theory `t` on `maps-2` df.
  - `sizestrat.py <run> <bot>` prints the per-map detail, sorted by area.
- **`mapcovar.py`** reads a **gauntlet** `results.csv`: columns `opponent`, `map`, `bot_result`.
  - It joins per-map wins to `area` and `ruins` from the shared corpus file and prints the join table.
  - It prints tie-corrected Spearman rho with a `t` approximation. Its docstring says this "is NOT an exact permutation test and is quoted as such".
  - It also prints a median split on each covariate.
  - `--corpus` prints the collinearity of the two covariates over the whole corpus.
- **`map-axis-split.py`** grew out of alice's `density-split.py`, which is now a shim calling it with `--axis density`.
  - It labels Spearman rho with a **permutation p** (3000 shuffles, seed 11) as `PRIMARY`. It reads "no trend" when p > 0.10 and needs at least 8 maps.
  - It prints the median split underneath, marked "DESCRIPTIVE ONLY". Each half gets a **bootstrap over maps** (20000 draws, seed 7) with se and a 95% CI.
  - The header carries the run's `bot.txt` bot name, so the reader knows whose wins are counted.
  - Maps missing from the corpus file are listed as "unpriced", not dropped silently.
  - The `size` median is computed from the corpus, not hard-coded, "because ... a hardcoded copy would go stale silently".

### Lessons, with the evidence as written

**1. One aggregate win rate cannot see a trade between map strata. A roster of your own snapshots cannot see it either.**

The sizestrat header says a change that "helps small maps a lot and hurts large maps a little passes that gate every time". It adds that "the deficit cancels in every head-to-head carol runs", because carol's snapshots share the weakness.

Carol's log ("INSTRUMENT FINDING ... carol scales *inversely* with map area") gives this table:

| tournament | carol overall | tiny | small | large | huge | rho(area) |
|---|---|---|---|---|---|---|
| 20260907-0100 | 19.0% | 15.8% | 20.8% | 18.4% | 21.2% | +0.029 |
| 20260907-1300 | 19.7% | 36.8% | 18.8% | 13.2% | 5.8% | -0.401 |
| 20260908-0100 | 32.3% | 56.6% | 33.3% | 18.4% | 15.4% | -0.546 (t = -5.57, 73 df) |

- In carol's words, "tiny went **+40.8 points** while huge went **-5.8**".
- The other two lineages went the other way: alice +0.217, bob +0.443.

Carol's diagnosis names two blind instruments:
- "The gauntlet gate is one aggregate number over a random 25-map sample ... The gate is not wrong, it is *unstratified*."
- "Every roster member is a carol snapshot, so they all share the large-map weakness and it **cancels in the head-to-head**."

**Reproduced.** I ran `sizestrat.py` today. It regenerates all three rows above exactly. It also shows the gradient outlived the fix:
- `20260910-1300`: carol 56.0% overall, tiny 78.9%, huge 36.5%, rho -0.458 (t -4.40).
- Carol's absolute level rose, but the gradient did not close.

Alice measured the same blind spot independently, in `TRAINING_LOG` near line 16110:
- Inside her own lineage: "**Spearman rho vs size = +0.014, p = 0.903 — the size axis is NULL inside my own lineage**".
- Against foreign bots: the same axis "separates the tournament at |z| > 4".
- Her conclusion: "my gauntlet cannot see the axis that decides my cross-lineage results."

**2. A map-axis finding can belong to a correlated axis. Check collinearity before naming the axis.**

The map-axis-split header records that the "sparse maps" finding "turned out to be a CONFOUND -- the axis that separates this lineage's results is map SIZE, and density was riding on its correlation with area".

Evidence (alice `TRAINING_LOG` line 15885), alice vs carol, 19-map quartile cuts against their complements:

| cut | delta | z |
|---|---|---|
| 19 smallest by area | -28.7 | -5.48 |
| 19 largest by area | +21.8 | +4.16 |
| sparsest by ruin density | -7.6 | -1.44 |
| densest | -6.4 | -1.22 |

The discriminating test was the two disjoint residual cuts:

| residual cut | delta | z |
|---|---|---|
| "sparse but NOT small" | +2.4 | +0.44 (NULL) |
| "small but NOT sparse" | -21.4 | -3.84 |

Alice's scope note: this establishes the **cross-lineage** deficit only. The gauntlet figure "needs a roster run cut the same way, and I have not run one".

My run of `mapcovar.py --corpus` shows how collinear the two axes are: **rho(area, ruins) = +0.841, t = 13.29, df = 73** over the 75 BC25 maps. That is the mechanism of the confound.

Carol stated the same limit before her iteration-35 run: "area and ruin count are collinear in this corpus, so a positive rho cannot separate 'longer payback horizon' from 'more towers to upgrade'."

**3. Never dichotomise a continuous covariate. The rank correlation is the primary statistic.**

- alice's median split on ruin density reported iteration 22 at "+6 sparse vs +2 dense", "roughly 1.5 sd".
- At full resolution: "**rho = -0.093, p = 0.673**", which is "as close to no relationship as 25 maps can express".
- Cause, in her words: "With 14 maps against 11, moving two across the line moves the headline by several points."
- Lesson she drew: "**Flagging uncertainty is not a substitute for resolving it when resolving it is cheap.**"

The fix went into the instrument: rho is printed first as PRIMARY. Her stated principle: "A lesson that lives only in a log entry has to be remembered by whoever next runs the tool."

**4. Every statistic in a verdict must come from a committed script. Validate a new tool against a number you already know.**

- Carol's iteration-34 commit message headlined "rho=+0.624".
- When `mapcovar.py` was built, the recomputation gave **+0.244, t = +1.21**. Every other number in the entry reproduced exactly: 28/50, swept 7/4/14, and both half-splits.
- Seven alternative computations were tried. None reached +0.624; the largest |rho| in the whole space was 0.474.
- Her verdict on the original number: "It was computed ad hoc in session, never written to a file, and therefore never checkable."
- Rule adopted: "any statistic that appears in a verdict must be produced by a committed script that regenerates it from `gauntlet/<run>/results.csv`."

The accept stood, because "rho was never part of" the pre-registered gate. Lesson: "Separate the gate from the argument, in advance."

**5. Pre-register the covariate, use exogenous map facts only, and do not count a null as confirmation.**

Carol chose map area because it "is known from the corpus before the sample is drawn". Game length is endogenous: "winning quickly shortens the game and would fake the correlation in the direction I want".

The iteration-35 result:
- rho = +0.291, t = +1.46, df = 23.
- Her reading: "It is consistent with the prediction and it is not evidence for it."

**6. When map covariates fail twice, run an ablation instead.**

alice's iteration 23 (alice `LEARNINGS_ARCHIVE` around line 955):

| attempt | rho | p |
|---|---|---|
| density, pre-registered | +0.318 | 0.127 |
| ruin count, post-hoc | +0.104 | 0.640 |
| area, control | -0.116 | 0.606 |

Her rule: "Cross-map variation can only separate two mechanisms if they scale with different map properties."

Corollary: "a change with no detectable covariate structure is not a weak result — it is a uniform one". Iteration 23 "swept 9 maps and lost none" across a 6x area range.

**7. Read how games end in each stratum before naming the mechanism.**

- Alice, small maps vs carol: "**38 of 38 games end 'The winning team painted enough of the map'** ... **Zero tiebreakers**", with a median of 429 rounds.
  - Her conclusion: "Had I named it a rush I would have built early-aggression code and measured nothing."
- Carol's losses on large maps came at a median of **847** rounds, 82% "painted out", against 998 on tiny maps.
  - Her conclusion: "out-expanded and finished early".

**8. Register a map-level falsifier before the run.**

- For alice's iteration 44: "a genuine gain must sit on the **LARGE half** ... A gain concentrated on small maps is not this mechanism, whatever the total says."
- The result was SMALL 14.3% against LARGE 8.8%, with rho -0.117, p 0.327. In her words, "if anything, *worse* on the large half where the mechanism was supposed to help most. Even had the total been positive, this cut would have disqualified it."

**9. Lessons from the towercensus README (companion file).**

- **"check a derived table against a total you already know"**:
  - The first `towercensus.py` indexed regex groups one off and keyed counts by round instead of by team.
  - "Every tower column came back 0, which is what exposed it. A subtler off-by-one would have looked entirely plausible".
- **Offline map scans that cost no games "changed a hypothesis before it was built"**:
  - `KScan` showed realized money share 24.9% against an intended 27.1%, so "that hypothesis died here".
  - `SrpScan` found "**ZERO valid centres on** ... `DefaultSmall`", which is the project's default trace map: "tracing SRP there would measure a mechanism that cannot fire and report it as dead code".
- **Say which denominator you used.** The replay MatchHeader `ruins` count is "exactly FOUR more than the claimable ruins".
- **Reconcile a scan against the engine's own record.** "Both scans reconcile exactly against the replay MatchHeader (Leaf: walls 160/3600, ruins 56) — which is what verifies the assumed flat-vector index order rather than merely asserting it."

### Translating to 2023 (inference unless marked as read)

- **The bins carry over unchanged.** 2023 maps are 20x20 to 60x60 (area 400-3600), the same range sizestrat was written for.
  - The bins are at 30^2 = 900, 40^2 = 1600 and 50^2 = 2500.
  - How many of the 103 maps fall in each bin is **not yet measured**. A bin with few maps will be noisy.
- **Candidate 2023 map axes:**
  - area
  - HQ count (1-4)
  - island count
  - rush distance
  - Ad/Mn/Ex well counts
  - cloud and current fraction
  - symmetry type

  Several are probably collinear with area, island count especially. Run the `mapcovar --corpus` style collinearity matrix over all of them **before** pre-registering any one, or lesson 2 repeats.
- **No 2023 map-facts file exists (read).**
  - `2023/tools` has only `maps.txt` (103 names). The engine jar contains 103 `.map23` files.
  - `tools/replaydump/ReplayDump.java` already parses the MatchHeader `GameMap`: `W`, `H`, `symmetry`, walls, clouds, currents, islands, resources, and spawn bodies (HQ count).
  - Its `--census` output already has `sym,islands_total`.
  - A `tools/mapfacts.py` or `.java` scan of the jar's maps, reconciled against ReplayDump on one replay per lesson 9, is the missing input. Also assert `W*H == walls length`.
- **The "foreign opponent" in 2023 is the benchmark field** (`tools/field.txt`, `bench-*`), not `g_iter*` snapshots.
  - Per lesson 1, a size or HQ-count split run only against our own roster can read flat while the field punishes us.
  - Run the split on field arms.
- **The 2023 gauntlet defaults to all 103 maps, both sides, random seeds (read: `MAPS` defaults to `maps.txt`; `SEED_MODE` defaults to random).**
  - Sample size is not the issue. Stratification is: an all-map aggregate still hides a trade.
  - With random seeds a map is not deterministic, so a per-map record is a noisy cluster. A bootstrap over maps as the cluster unit still applies.
- **Note on three-body tournaments.** In a closed round-robin, wins are conserved, so one bot's negative size gradient is partly the mirror of the others' positive ones: carol -0.546 against alice +0.217 and bob +0.443. A gradient measured in such a pool is relative to that pool.

### Tools and reuse verdicts

| Tool | Verdict | Notes |
|---|---|---|
| `mapcovar.py` | **Adapt** (best starting point) | Column-compatible with 2023 `results.csv` (`opponent,map,bot_result`). Needed changes: (1) swap `ruin_parity.txt` for a 2023 map-facts file and make the covariate list generic; (2) add map-axis-split's permutation p and label rho PRIMARY, with the split marked descriptive; (3) report `unknown`/`dud` rows instead of counting them as losses (any non-`win` counts as a game lost); (4) keep the printed per-map join, which is what made the +0.624 error findable. Minor: crashes with no arguments (`sys.argv[1]`). The median split is an upper median with ties sent high. |
| `sizestrat.py` | **Adapt the idea, rewrite the I/O** | Input is the 2025 tournament format (`team_a,team_b,winner_bot`), which 2023 does not produce. Keep the four absolute area bins and the per-bot rho row, and drive it from gauntlet runs per field opponent. Pitfalls: an unknown map raises `KeyError` instead of being excluded; `t` is an approximation with no permutation p; `record()` takes an unused argument. |
| `map-axis-split.py` | **Adapt** (strongest statistics) | Has the permutation p, a bootstrap per half, fixed seeds, the bot shown in the header, and unpriced maps listed. Pitfalls: (1) denominators are hard-coded `2*n`, assuming exactly two games per (opponent, map), which is wrong under 2023 `CELLS` or seed repeats; use actual game counts. (2) It needs `bot.txt`, which the 2023 `gauntlet.sh` does not write (grep finds none), so it prints `BOT=?`. (3) Map names are matched case-sensitively, unlike carol's lowercased lookup. (4) The density `MEDIAN = 11.4` is a BC25 constant. (5) Its own comment: the map list is sorted **by name**, because re-ordering "changes the bootstrap realisation" (se 2.70 -> 2.73). Keep that if recorded se values must reproduce. |
| `density-split.py` (shim) | Skip | Kept only so commands in old logs still run. |
| towercensus `KScan`/`SrpScan`/`towercensus.py` | **Reuse the pattern, not the code** | BC25-specific (ruins, SRP). The pattern to keep: offline jar scans of every map for "can this mechanism fire here?", run before building, reconciled against the replay header. 2023 analogues: per-map island count, HQ-to-nearest-island distance, wells per type. |
| 2023 `statlib.py` | Extend | Has `within_group` (per-group deviations) and `pointbiserial`. It has no Spearman, permutation test or map bootstrap, so the ported code belongs here, unit-tested in `test_tools.py`. |

### Pitfalls checklist

- Collinear axes. In BC25, rho(area, ruins) was +0.841. Cut on the residuals (A-but-not-B and B-but-not-A) before naming an axis.
- A median split as headline. Report rho with a permutation p; the split is descriptive only.
- Orientation. map-axis-split counts the BOT's wins and map-resample counts the opponent's. Print whose wins are counted.
- An in-session number never written to a file. Regenerate every verdict statistic from `results.csv` by a committed script.
- A flat result against your own snapshots. Self-play cancels a shared weakness; confirm on foreign or field opponents.
- An endogenous covariate, such as game length. Use only map facts known before the draw.
- A derived table that looks plausible. Check it against a known total, such as total games or the header counts.
- Tracing on a map where the mechanism cannot fire. Scan the corpus first.

### Proposed 2023 rule (inference; not in any report)

Every accept verdict against field opponents prints:
- per-area-bin win rates;
- Spearman rho vs area, with a permutation p.

A pre-registered clause applies: the candidate must not lose ground on the large half.

Carol's wording: "An iteration that wins overall while going backwards on the large half is **not** an accept".

Caveat: each half holds about 51 maps. Fix the "lose ground" band in advance from the measured noise of a half; without a band the clause rejects on noise.

A grep for `stratif|density|map size|dichotom|0.624` across the prior reports finds only:
- bc21's "map-size confounding" (raw coverage counts)
- BASICS' "Population targets scale with map size"
- TRAINING_ALGORITHM's "stratify within map and opponent", which is for correlations, not gates

None of them is a gate rule, so this section is new.

## Gap read: /home/terryvanbelle/projects/vibe/2025/agents/carol/carol-tools/clock/clock.py

**What it is.** This is carol's "Race-to-70% CLOCK", a bc25 script of 78 lines (3,857 B). I read the code directly from the repo. Its context comes only from the filtered copy `readroom-no2023/bc25/agents/carol/TRAINING_LOG.md`, lines about 13620-14110 (2026-09-09), plus doctrine 18 in `readroom-no2023/bc25/TRAINING_ALGORITHM.md` (line 315). No other prior report mentions the tool, and the filtered `carol-tools/` holds no README for it. I also read, as our own code: the 2025 `tools/gauntlet.sh` and `tools/collate.sh`, which produce its inputs; the 2023 `tools/gauntlet.sh`, `tools/lib.sh::parse_result`, `tools/replaydump/ReplayDump.java` and `src/examplefuncsplayer/RobotPlayer.java`; and the win-reason strings inside `2023/engine/battlecode23-3.0.15.jar`. Nothing here describes what 2023 teams did. This is evaluation method only.

### What the code does (from the source)

- **Usage:** `clock.py <runA-dir> <labelA> <runB-dir> <labelB>`. Each run directory is one gauntlet run: **one arm against one fixed opponent** on a pinned map list, both sides.
- **`load()`** reads `results.csv` (`map`, `bot_side`, `bot_result`, `rounds`) and the optional `reasons.txt`. `reasons.txt` is produced by bc25 `collate.sh`, which strips the `REASON ` prefix, so each line is `OPP MAP SIDE text...`. The code keys reasons on `(map, side)` and ignores the opponent, which is correct only when a run has a single opponent. Each game gets one of four kinds, chosen by substring:
  - `paint70` if the reason contains "painted enough";
  - `tiebreak` if it contains "tiebreak";
  - `annihilation` if it contains "destroy" or **"all"** (case-insensitive);
  - `?` otherwise.
- **`report()`** prints, per arm:
  - CLOSED, meaning won and `paint70`, with the median rounds of those games;
  - wins on tiebreak, marked "did NOT close the map";
  - wins by annihilation, marked "clock stopped for another reason";
  - lost, meaning every game where `bot_result != "win"`.
- **`main()`** prints the "PRE-REGISTERED COMPARISON". It gives:
  - the difference in closed counts;
  - on the cells where **both** arms closed, the number where B was faster and the number where B was slower;
  - the list of cells that only one arm closed.

  It computes **no** sign test, no median or mean paired difference, no relative speed-up and no peak coverage. The log's p-values were computed outside this tool (see below).

### Lessons with evidence (numbers quoted as written)

1. **A race outcome in a head-to-head is zero-sum, so it cannot measure a build's speed.** The docstring says: "'who reached 70% first' is ZERO-SUM inside a head-to-head -- only one side can finish -- so a head-to-head can never separate 'my build got faster' from 'the other build got slower'." The log names the trap that prompted it. On the dense census (run `20260909-104327`, 34 games, `carol_iter44` vs `carol_i47_1400`), the margin was "**+0**". Split by end type, the candidate won "decided" games **13-5** and lost "round-2000 tiebreak" games **4-12**, so "two large opposite effects" cancelled to zero.
2. **Do not condition on an outcome that the build itself causes.** The log says: "Whether a game is 'decided' is determined by whether someone reached 70% — and the candidate is the build that reaches 70%. So 'the candidate wins the decided games' is *partly definitional*". It calls this "the same error family as doctrine 18" (doctrine 18 is "replay per-robot state is recorded POST-action"). The log kept the pre-registered verdict ("margin 0, direction closed") and refused to accept anything on the split. It kept only the non-definitional facts: "Of 18 games that anyone finished, the candidate finished 13 and the incumbent 5", and "In the 16 games nobody finished, the incumbent had painted more by round 2000, 12-4."
3. **The fix is to take the opponent out of the statistic.** The docstring says: "Each arm plays the SAME fixed weak opponent on the SAME maps, and we read the clock off each arm separately. Neither arm can interfere with the other's clock because they never meet." The fixed opponent was `examplefuncsplayer`, chosen because it was "already a frozen entry in `roster_extra.txt`, so it adds no new instrument and cannot go stale". Annihilation endings are counted separately because they stop the clock "for an unrelated reason".
4. **Result on dense maps.** Both arms played vs `examplefuncsplayer` on the 17 maps with at least 24 ruins, both sides.

   | arm | games | wins | closed by >70% | median rounds to close |
   |---|---|---|---|---|
   | `carol_iter44` | 34 | 34 | 31 | **717** |
   | `carol_i47_1400` | 34 | 34 | 32 | **612** |

   Paired on the 31 cells both arms closed: "faster / slower / tied **22 / 9 / 0**", "median round difference **−89**", "mean round difference **−112.6**", "sign test, two-sided **p = 0.029**". I recomputed the exact two-sided binomial for 22 of 31 and got 0.0294, so the figure reproduces. The log adds: "This is not conditioned on any outcome the build causes: both arms won all 34 games, so there is no selection on winning either."
5. **The count statistic saturated on the first arm.** That arm closed 31/34. The log says: "There is almost no headroom ... **the informative statistic here is the CLOCK, and the count is dead.**" It fixed the reading rule before arm 2 returned: judge on median rounds-to-close and paired per-map differences, and treat the count as "a floor check only". The lesson it carried was: "*check a new instrument for ceiling and floor effects on the first arm, before spending the second.*" On sparse maps both arms closed **34/34**, so "the count arm of this instrument is dead everywhere".
6. **A clock against a weak opponent changed the diagnosis.** `carol_iter44` closed 16 of 17 dense maps at a median of 717 rounds. So the log said "the capability gap ... is **not absolute — it is contested**". The earlier wording, "carol cannot finish dense maps", "was wrong". The clock also overturned a one-game disqualification ("~701 tiles on Leaf against a threshold near 2,400 ... from one map, one side, in a contested head-to-head"). That build then qualified as an opponent archetype (`carol_racer`): "closes dense maps by the >70% condition **32 of 34**", with a peer band of **42%** vs `carol_iter44`.
7. **Pre-register both halves, then report the outcome nobody named.** The sparse arms are `20260909-111613` and `20260909-112249`. Dense vs sparse: the median REL speed-up was **−11.8%** vs **−4.2%**; paired faster/slower was **22/9** vs **21/12**; sign-test p was **0.029** vs **0.163** (I recomputed 21/33 and got 0.163). A Mann-Whitney on the per-cell relative speed-ups gave "**z = −1.34, p = 0.180**". The verdict was "**unresolved**", which matched neither pre-registered branch. The log's next step was "a better-powered contrast, not a bigger one": a third, mid-density point to make a dose-response, because "more maps do not exist — those are censuses of both tails". It also said: "a clock is not a gate". Iteration 47 stayed rejected despite the clock passing.
8. **A free determinism control.** A duplicate launch of arm 2 (a mistake, logged) gave "**34 of 34 cells identical — same winner AND same round count**". This is the only reason the paired (map, side) design is noise-free in bc25. *Inference:* 2023 does not get this for free (see Pitfalls).
9. **Related doctrine: tournament standings are zero-sum too** (`TRAINING_ALGORITHM.md` ~l.718). "bob's fall is not a decline ... his own frozen roster, the only instrument that reports a level, has him going 40 -> 70 against a fixed ancestor". The same principle applies one level up: read level from a fixed reference, never from a zero-sum share.

### Transfer to 2023 (inference unless marked as checked)

- **The 2023 conquest condition is race-shaped.** The jar's reason strings (checked) include "The winning team won by capturing 75% of sky islands." (`CONQUEST`). Two teams cannot both hold 75% of the islands, so "who conquered first" is zero-sum inside a head-to-head, exactly like bc25's 70% paint. The other `DominationFactor` values, all checked in the jar, are:
  - `MORE_SKY_ISLANDS`: "won by having more sky islands";
  - `MORE_REALITY_ANCHORS`, `MORE_ELIXIR/MANA/ADAMANTIUM_NET_WORTH`: "won on tiebreakers (more ...)";
  - `RESIGNATION`;
  - `WON_BY_DUBIOUS_REASONS`: "won arbitrarily (coin flip)".

  There is **no destruction factor**, because HQs are indestructible. *Inference:* every 2023 game therefore ends by conquest before round 2000, by resignation or crash, or at round 2000 on a tiebreak. The "annihilation" bucket becomes resignation/crash only.
- **The 2023 clock is rounds-to-conquest per arm against a fixed opponent.** For maps the arm never conquers, record a secondary "peak islands held, as a fraction of the total". `ReplayDump --metrics` already emits per-round island counts per team, and `--islands` emits ownership changes (checked in its header). The 2023 `examplefuncsplayer` builds and places anchors (checked, `RobotPlayer.java` l.117-161), so it competes for islands much as bc25's version competed for paint. That is fair to both arms, but the absolute rounds are not "time to conquer an empty map". The log made the same caveat for bc25.
- **Use it when the end-type tally says the race regime matters.** SYNTHESIS lesson 11 records that the first 2023 `examplefuncsplayer` mirror "ended on the mana tiebreak". If our bot rarely conquers even a weak opponent, the clock has a **floor** problem (few closed cells to pair) rather than bc25's ceiling problem. Check the first arm for both before running the second (lesson 5).

### Reuse verdict

| item | verdict for 2023 |
|---|---|
| `clock.py` as written | **DO NOT RUN on 2023 output.** It cannot read the 2023 format. I smoke-tested it on synthetic 2023-format runs in the scratchpad (checked): (a) the 2023 `gauntlet.sh` writes the reason **inline** as a `reason` column in `results.csv` and writes no `reasons.txt`, so every game is classified `?`; (b) given a `reasons.txt` carrying 2023 strings, conquest and "more sky islands" still fall to `?`, and only "on tiebreakers" is matched; (c) a `?` win is counted in **no** bucket and nothing prints the unclassified count, so the output reads "CLOSED ... 0" with a silent shortfall; (d) `int(r["rounds"])` **crashes** on the 2023 runner's `?` rounds for unknown/timeout games. |
| `clock.py` design | **ADAPT** (about 30-60 lines, inference). Read the `reason` column. Classify `capturing 75%` → closed; `more sky islands` / `tiebreakers` / `coin flip` → tiebreak; `resigned` → separate; anything else → `?`, **printed**. Key cells on (map, side, **seed**). Skip or count `unknown`/`dud` rows separately rather than lumping them into "lost". Add what the log computed by hand: paired median/mean difference, median relative difference, exact two-sided sign test, and optionally a rank-sum across map strata. The 2023 `tools/statlib.py` has no sign test (checked its `def`s). Optionally join `ReplayDump --metrics` for rounds to k islands and peak islands. |
| 2023 `tools/compare.py` | It already pairs (opponent, map, bot_side) and reads `rounds`, so it is a candidate base. It has no end-type split and no seed key. |

### Pitfalls

- **Pin the seeds.** The 2023 `gauntlet.sh` defaults to `SEED_MODE=random`, so a clock run there would play each (map, side) cell under a different random seed in each arm (checked in its header). bc25's paired design leaned on "34 of 34 cells identical". For a 2023 clock, run both arms with `SEED_MODE=map` or with a `CELLS` file that pins the seeds, and verify determinism once with a duplicate cell set.
- **Win replays are deleted by default.** The 2023 runner deletes win replays unless `KEEP_ALL=1` (checked). A clock against a weak opponent is nearly all wins, so without that flag no trajectory or peak-island reading is possible afterwards.
- **The loose `"all"` substring in the annihilation test** matches any reason containing "all" (for example "small" or "wall"). It is harmless in bc25 only because of the order of checks and the actual strings. Match exact reason strings or enum names instead.
- **One opponent per run directory.** The reason key ignores the opponent, so a multi-opponent run would silently overwrite reasons.
- **A clock is a secondary, not a gate** (lesson 7). Pre-register which statistic is primary, and fix the reading rule after seeing arm 1's ceiling or floor but before arm 2 returns.
- **Do not re-introduce the conditioning error through the back door.** If an arm loses some clock games, "median rounds among closed games" is again conditioned on an outcome. *Inference:* report closed count and clock together, or use a survival-style reading that treats unclosed games as censored at 2000, rather than a median over survivors only.
- **Chained launches.** The duplicate arm-2 launch came from a check that "shared a failure mode" with the waiter (both read the same unflushed log). The log's control is to list in-flight runs (`gauntlet-collect.sh --list`) before launching rather than inferring from a log.

## Gap read: /home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc24/research/g4contact-design-2026-10-05/judge-measurement.md

**What it is.** A 14,704 B bc24 review dated 2026-10-05, written through a measurement lens. It judges three "convoy-response" arm designs against Gymhgy.v10official: A g4contact, B g4deny, C g4meet. Each is scored on five axes out of 10 (total out of 50): A 31, B 28, C 27. The review checks each design's claims against the bot code, `ReplayDump.java`, `delivery-gate.sh` and `delivery-check.py`, and lists grafts for the winner. No games were played. I checked its tool claims against `/home/terryvanbelle/projects/vibe/2024/tools/delivery-check.py` (82 lines), `delivery-gate.sh` (63) and `replaydump/ReplayDump.java`. I took the arm's outcome from the filtered `bc24/TRAINING_LOG.md`, lines 1702-1766. The sibling `judge-engineering.md` (10,346 B) is **still unread**.

### Gate-design holes that carry over (each with the review's evidence and, where known, what happened)

1. **Population mismatch: the arm decides on an observed, decaying lower bound, but the gate column splits on the truth.** Quote: "The arm decides on the live, observed en20: a lower bound that decays. The column splits chains by the true grab group. Divers that enter chains with a grab group of 12+ are invisible to the numerator, and u12 chains that grow past 12 dilute it." The fix: put the decision bucket in the note ("dive7"), and measure **leakage** (action turns where the true population is outside the arm's target) "in every delivery game, not only in 5(a)". **What happened:** this was built as the `diveLeak12` column. At group gate 12 the 5(a) read **diveLeak12 0.39 (bar 0.3)**, so the hole was real and large. The one pre-registered recalibration (gate 8) brought it to 0.18. *2023 relevance (inference):* clouds cut vision to r^2 4, so any arm conditioned on "enemy launchers I can see" acts on an even weaker lower bound. Leakage columns matter more in 2023, not less.
2. **Length weighting of shares.** "A share of flag-rounds is weighted by chain length. Returned chains run 0.73-0.79 contact and capture chains 0.36. If the dive shortens chains, the share moves through composition." The fix: a per-chain indicator (`noContact10u12`, the share of chains with none of ours within dist2 20 during t1-10). *2023 analogue (inference):* use per-trip or per-island-contest indicators, not per-round shares, whenever the arm can change how long trips or contests last.
3. **A ceiling makes a x1.15 bar unreachable.** "The per-game flagContact20 baseline is 0.585 ... A x1.15 bar may ask for near returned-chain levels, about 0.75-0.8." Gate instead on the low-baseline complement (the screened share). **What happened:** the offline premise check found the opposite problem in the per-chain column. Its route R4 measured a noContact10u12 baseline of **0.061 (< 0.08)**, and "only 4% of no-contact u12 chains seen at t0". The pre-registered switch therefore made the gate `rel:screened20u12<=0.8`. *Lesson (inference):* before fixing a ratio bar, check that the baseline sits in a band where the ratio has room. A ceiling breaks a `>=` bar, and a floor near 0 makes a `<=0.8` bar too noisy to read. Pre-register the fallback column.
4. **No guard for the arm's own named falsifier.** "The gate has no `enemyStunVictims` guard and no `enemyFirstGrabs` guard, yet defenders may dive for their own flag." **What happened:** the delivery line carried `nw:enemyFirstGrabs<=1.1 nw:enemyStunVictims<=1.2` (the review proposed 1.15; the log shows 1.2). Rule: every pre-mortem falsifier gets an `nw:` guard on the gate line.
5. **Denominator dilution (design B).** The denominator was "8+ enemies within dist2 100 of the home, a disc of about 314 tiles", while "the trigger needs 8+ enemies inside one duck's vision, about 61 tiles. Many denominator rounds can never fire." Rule: count only rounds in which the trigger could have fired.
6. **"An outcome column is gated" that "can be gamed" (design B).** "`rel:enemyAtGrab20<=0.85` is an effect, and as a mean per grab it can be gamed. If the muster pulls ducks off the other flags, extra small grabs there lower the mean and produce a false PASS." Rule: gate on the mechanism's own output. Outcome columns, especially per-event means whose event mix the arm can change, belong in the effect reads.
7. **Ungated parts (design B).** "The flag-stun part, which carries most of the claimed effect, and the respawn part appear in no gated column." Rule: every sub-mechanism that carries claimed effect needs a gated column or its own dose.
8. **"Ever" indicators on long chains can be met by chance (design C).** On 52-round capture chains, an "ever" signal "depends on the chain-length mix through the 10-round filter". Rule: use a fixed window (t1-10), not "ever".
9. **Unknown baseline (design C).** "Set it offline first, not from 5(a)."
10. **Side effects before the first action break the paired control.** A's `contactSight` called `Comms.reportCarried` on every dropped sighting. That fed trySpawn, the chase and the far-duck redirect, so "paired games therefore diverge at the first dropped-flag sighting, and the 12+ group is not an untouched control". The fix: keep the arm's state in its own shared-array slots, or put the side effect behind its own sub-switch. **What happened:** after the fix, the identity read passed: "every pair identical until our first dive or predicted chase". *2023 relevance:* the shared array has 64 slots, and writes are allowed only near our HQ, an amplifier or an anchored island. Give each arm its own slots, and test that with the switch off the bot writes nothing new.
11. **Run an offline premise check with pre-registered routes before building (the "D0" check).** It is computed from existing replays and pinned to build, recalibrate or park routes. **What happened:** it was built as `tools/contact-d0.py` (151 lines, four routes R1-R4 in its docstring) and run on "400 newest g_iter4-vs-Gymhgy replays, 3,878 chains on our flags: 3,044 u12, 834 12+". R1 median error 1-2 tiles; R2 reach 0.686 (bar 0.25) -> BUILD; R3 0.151 -> gate 12; R4 switched the column. **Reuse verdict: ADAPT the pattern, not the code.** It depends on a bc24 `--contact-d0` dump mode.
12. **Check the magnitudes in a scoring function on diagonals.** "The raw `-dist2(goal)` tie-break is worth +22 to +38 on diagonal steps at Chebyshev 6-8, so 100 + 30 - 120 > 0 and the step through two threats is taken." The fix: scale the term (dist2/8) or cap it below the smallest penalty. This applies directly to 2023 launcher micro scores (inference).
13. **Overreads to catch.** A per-game number (first sight of any flag, median r243, to the first grab of the game) was read as a per-flag lead time. "On our half more than 10 tiles from the flag" was read as "idle". And A's motivating trace (a 13-robot grab) is "a case the arm excludes". Rule: quote the definition behind every statistic in a design.
14. **The insertion point can silently replay a closed arm.** C's assignment "lands right before Duck.java 39 ... Z1HOLD's hold branch. Committed ducks ... would run the closed g4z1 behaviour and return before the meet branch." Rule: list every early return between the insertion point and the intended branch.

### Outcome of the arm the review picked (from the filtered TRAINING_LOG)

Both judges chose g4contact, and it was built with the grafts. At gate 12 the 5(a) leaked (0.39). The g4contact8 recalibration passed its 5(a) with a weak signature preview: "screened20u12 0.260 vs 0.294 (-12%, bar -20%)". The trace showed "4 of 10" first divers "moving away". Its Gymhgy delivery: "**FAIL** (24 cells): dives fire in 100% of games, but screened20u12 rose, 0.28 vs 0.24 (-2.7 SE against the x0.8 bar)". The line was then closed, with "census columns and D0 tool" kept. *Lessons (inference):* (a) The measurement fixes worked as instruments. They killed a non-working mechanism in two gates with one pre-registered recalibration, and nothing was left to argue about. (b) A 16-cell 5(a) preview pointed the right way (0.245 vs 0.294) but reversed in the 24-cell delivery. Treat 5(a) previews as wiring checks, not as evidence of direction. (c) The review's graft 5 rationale ("that cap is what protects `nw:kills`") was overtaken by owner PROMPTS 183: "No kills guard ... a mechanism that trades bodies is judged by the band test" (`delivery-gate.sh` header, lines 8-9).

### Tool facts (verified in code) and reuse verdicts

| item | fact (checked) | verdict for 2023 |
|---|---|---|
| `delivery-check.py` `rel:`/`nw:` pairing | It pairs only cells where both arm and base parse as float (lines 43-46), so blank conditional columns are safe, as the review says. Each pair is weighted equally: `e = arm - ratio*base` per game, then mean and SE (lines 48-51). It is a mean of per-game values, not a pooled share; `contact-d0.py` R4 notes "the quantity delivery-check's rel: compares; the pooled share printed beside". | **STEAL** (P1 in SYNTHESIS). |
| `delivery-check.py` `fire:` | The denominator is every game with a numeric value (`vals()`, lines 22-27; check at 68-70), so a **0 counts as "not fired"** and a blank is skipped. The default need is 0.9. The bc24 census adopted the rule "blank when the event is absent, so tools/delivery-check.py skips the game" (ReplayDump header line 67). `diveTurns` is "blank without a g0 < 12 chain, so a fire check skips the game". | Port the convention: a 2023 census column feeding `fire:` must be **blank** in games where the trigger cannot occur (e.g. no enemy amplifier seen, no island contested). |
| `delivery-check.py` `median:`/`mean:` | Point checks with no SE and no INCONCLUSIVE state (lines 71-75). Only `rel:`/`nw:` are three-way. | Use `median:`/`mean:` only for hard floors such as `mean:overruns<=0`. |
| **`delivery-check.py` line 14 port hazard** | `SEEDSEG = re.compile(r'__s\d+(?=__bot[AB]\.bc24$)')` hardcodes `.bc24`. The 2023 `gauntlet.sh` line 67 names replays `${OPP}__${MAP}__s${SEED}__bot${SIDE}.bc23`. *Inference:* unchanged, the regex never matches 2023 names, so the MEAS3 seedless-pairing fallback silently stops working. A seeded-vs-seedless mix would then pair nothing ("NO PAIRED DATA" -> FAIL). | Change the regex to `.bc23` (or `\.bc2\d`) when porting, and add a unit test with 2023 file names. |
| `delivery-check.py` row filter | It keeps only rows with `us == '1'` (line 11). | The 2023 census must emit a `us` column. |
| `delivery-gate.sh` | The header documents three-way verdicts, the 24 -> 48 -> 96 extension, `DGPOOL` needing `DGTAG` (exit 2), `DGMAPS`, and no kills guard since PROMPTS 183. | **STEAL** with the above. |
| ReplayDump indicator parsing | It "does not parse indicator dots; it reads only indicator strings". `diveTurns` counts post-setup robot-turns whose string **starts with** "dive". | For 2023, build note-prefix columns rather than dot-based ones, since dots need new parsing code. |
| `contact-d0.py` (151 lines) | Implements pre-registered routes over replay truth and reports PARTIAL with exit 1 when a replay is missing or fails to dump. | **ADAPT the pattern** (pre-registered routes, PARTIAL on missing input, exact-fraction bar comparisons). Skip the code: it is bc24-specific. |

### Indicator-string truncation (verified in the 2023 engine)

- The 2023 engine caps the string at **64 characters**. I parsed `battlecode/common/GameConstants.class` in `/home/terryvanbelle/projects/vibe/2023/engine/battlecode23-3.0.15.jar`: `INDICATOR_STRING_MAX_LENGTH = 64` (also `SHARED_ARRAY_LENGTH = 64`, `MAX_SHARED_ARRAY_VALUE = 65535`).
- bc24 evidence. The review: "G.java 69-71 builds about 72-80 characters with a 12-character note ... so the trailing counters (an, wy, cr) are cut. Any counter inserted after 'x' ... pushes pr/cs/fs off as well." The bc24 `src/bot/G.java` comment (line 66, audit MEAS5): "the old string overflowed the 64-char cap on 70-75% of turns and cut off the note and the last counters".
- bc24 used two orderings. The default puts the note first, then counters with the most-used first; the C.TRACK mode puts counters first "so the 64-char cut never drops them". The cut is silent: the census simply sees smaller or missing counters, which biases any 5(a) bar read from them.
- Our 2023 bot (`/home/terryvanbelle/projects/vibe/2023/src/bot/RobotPlayer.java:54`) already writes `G.note + "|ov=" + overruns + ",ex=" + exceptions + ",nm=" + nearMiss + ",sm=" + MapMem.cand + ",sd=" + MapMem.decidedRound`. A long note cuts `sd`, then `sm`, silently. *Recommendations (inference):*
  - Cap the note length.
  - Unit-test that the full string stays within 64 characters with worst-case counter widths.
  - Have the 2023 replay reader count strings of exactly 64 characters as "possibly truncated" and report that share per game.
  - Keep any note that the census prefix-matches at position 0.

### Pitfalls

- A gate column must measure the **arm's own output on the population it acts on**, computed from replay truth so the base also gets a value. The review's "good" list: computed from true positions, conditioned on the band where the effect lives, a leakage read for a partial sensor.
- **Never gate on an outcome mean whose event mix the arm can shift**, e.g. a mean per grab or per fight.
- **Do not treat a stratum as an untouched control unless the code proves it.** An identity read ("pairs identical until first action") is the check.
- **A per-chain indicator fixes composition but can sit at the floor** (0.061). Have the D0-style offline check choose between the per-chain column and its complement before any games are played.
- Ratio bars in `nw:` guards: the review proposed `nw:enemyStunVictims<=1.15`, and the shipped line used 1.2. Record which bar was pre-registered.

## Gap read: /home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc24/research/criteria-review-2026-10-05/history.md

**What it is.** Read in full (13,948 B, 178 lines). It is the bc24 criteria review's history file, dated 2026-10-05, covering the "seeded era" from 2026-10-02 23:00 UTC. It recomputes every band-tested arm from the VM census files with `tools/eval-paired.py`'s own `load`, `pairs` and `sign_p`. It reports pairs, sign p, discordance, and the all-cell and upper-tier t for each arm. Then it asks whether promoted gains held, how tier membership moves criterion (b), whether rejected arms stack, and what the target-filler pairs say. Nothing in it describes 2023 play. It is evaluation method, relevant to SYNTHESIS C12 ("bc24's structure, on a 2023 per-pair margin"), whose `t_up` route is the referent-dependent part.

**Code also read, directly from the repo:**
- `/home/terryvanbelle/projects/vibe/2024/tools/eval-paired.py`, mainly its tier docstring and `--tier`.
- The git history of `/home/terryvanbelle/projects/vibe/2024/tools/upper-tier.txt`, through `git log` and `git show` (read-only).
- `/home/terryvanbelle/projects/vibe/2024/tools/filler-tally.py` and `filler-pair.sh`.
- `/home/terryvanbelle/projects/vibe/2024/tools/arm-deltas.py`.

The doc's own script `scratchpad/criteria/per_seed.py` and its `per_seed.out` **are not on disk** (`find /` returns nothing). Only 6 of the census files are local, in `/home/terryvanbelle/projects/vibe/2024/research/`: g_iter1, g_iter1-conf, g1basics, g1basics-conf, g2bc and g2nonav. The g3 and g4 arms cannot be re-run locally.

### Independent check I ran (read-only, on the local census files)

The test: g1basics against g_iter1, under all four historical versions of `upper-tier.txt`. The script imports eval-paired.py and was not modified. It lives in the session scratchpad as `hist/tierdrift.py` and is ephemeral.

**It reproduces the doc's pooled row exactly:** "473 pairs, net +62 (79-17), all +0.67 +- 0.07 (t 9.3), upper +0.40 +- 0.09 (t 4.7)" under the 11-bot tier.

On the **same 473 games**, the upper slice moves as follows:

| tier version (commit, date) | members | upper pairs | upper wins ctl->arm (net) | upper delta (t), pooled | seeds 1-2 only, t |
|---|---|---|---|---|---|
| d26d1fb, 10-02: "rated 2050+" | 12 (incl. waffle, uravt) | 260 | 25->42 (+17) | +0.40 +- 0.09 (4.6) | 2.8 |
| 618f6f3, 10-04: re-derived, waffle out | 11 | 236 | 16->32 (+16) | +0.40 +- 0.09 (4.7) | 3.1 |
| 15b04e2, 10-05: "10 bots above g_iter5" (uravt out) | 10 | 236 | identical to 11-bot, because uravt never played in this band | 4.7 | 3.1 |
| 80f7e73, 10-06: "5 bots above" the incumbent | 5 | **116** | **7->6 (net -1)** | +0.27 +- 0.10 (**2.7**) | **1.6** |

**What this shows (inference from my rerun):**
- **The definition itself drifted three times in four days.** It went from an absolute rating cut, to a re-fit, to "rated above the incumbent, re-derived at each promotion" (eval-paired.py docstring). Each promotion therefore shrinks the tier.
- **On the 5-bot tier, the largest promotion bc24 ever made shows no upper-tier win gain at all.** At seeds 1-2 its t_up of 1.6 would fail today's 2.6 upper route. The all-cell t of 6.2 would still ship it.
- **Against top bots, wins are too rare to carry information:** 7 of 116 control games. The upper-tier capture delta also loses about 30% of its size (0.40 to 0.27), because a tier of only the strongest bots is where an arm's gain is smallest.

### Lessons with evidence (numbers quoted as written)

1. **A criterion defined on "the upper tier" changes verdicts when membership changes, even on identical games** (section 6). "Dropping waffle from the tier (12 of the ~240 band games per two seeds) moves g3escrg2's upper t from 1.7 (not met) to **2.5** (met), on the same games; g2cr's pooled upper t from 2.0 to 1.7." The doc's conclusion: "A half-sample test near the 2 SE line flips on tier membership."
   - The tier also listed a bot that never played in the band: "the upper slice has never contained uravt (absent from the band; PROMPTS 184)".
   - Older REWRITE.md rows used the 12-bot tier, so "some older upper values below differ from REWRITE.md". The arm ledger mixed two referents without saying so.
2. **The upper-tier signal that triggers a confirmation run is mostly the winner's curse** (section 4). g2cr: "criterion (b) on the first two seeds (upper +0.30, t 2.3) sent it to confirmation. On the confirmation seeds the upper tier did not replicate (+0.07 +- 0.13; +0.02 and +0.20 per seed under today's tier)." It was promoted on criterion (a), the pooled all-cell wins with p 0.017, and its waffle crack held. Across g2cr, g3lost, g4pick and g4ship1, "first-pair to confirmation shrinkage ... averages about 25%".
3. **No promoted gain reversed, but one promotion was weaker on wins than a rejected arm** (sections 4 and 5).
   - g3lost (promoted on route (b)): wins "band +9/473 (p 0.24); Cyril +10/224 (p 0.14); only the combined 680 pairs reach p 0.048".
   - g4ship1 (rejected): +12/480, all-cell +0.144 +- 0.065 (t 2.2).
   - Same capture effect: g3lost +0.140 (t 3.1), g4ship1 +0.144.
   - Upper-tier t: g3lost 4.2, g4ship1 1.4.
   - The doc's diagnosis: "The protocol rewards narrow, low-variance changes aimed at the upper tier. It has no route for an all-cell capture delta >= 2 SE."
   - g3lost's discordance was 10% ("changes play only after a capture"); g4ship1's was 16%.
4. **Outcome after this doc**, from the existing bc24-play.md, not from history.md. g4ship1 later shipped as g_iter5 at look 3, pooled over 720 pairs: "t_all +3.25, t_up +1.98, net +23 (sign p 0.033) -> SHIP". That was the all-cell route; t_up was still below both the old 2.0 bar and the new 2.6 bar. The final ladder gave g_iter5 +51 over g_iter4, and Gymhgy filler gave "+84 over 1,200 pairs (+3.9 SE)". The doc's argument that a broad, consistent arm was being wrongly rejected was borne out.
5. **Per-seed sign consistency is a cheap, informative screen** (section 2).
   - g4ship1: "12 of 12 per-seed capture readings positive and no seed with negative wins". g3lost: 4/4 and upper 4/4. g1basics: 4/4.
   - The arms that failed were mixed: g4econ2 0/2, g4gym1 1/2, g2bc2 1/2.
   - g2cr was 4/4 on all-cell, but "upper was strong only on seed 1". Its seed-by-seed upper deltas were +0.40 / +0.02 / +0.02 / +0.20. That is the winner's curse from lesson 2, made visible.
6. **Rejected arms lean positive, and the "rest" half is where economy changes pay** (sections 1 and 9). On g_iter4 the six band arms' all-cell deltas were "+0.08, +0.08, -0.08, +0.08, -0.06, +0.14 (mean +0.04)". The "rest" half was positive in all six, and the upper tier was negative in four. "Economy and re-grab changes help against the weaker half and cost against the top, and only the top half counts under (b)."
   - Promotions by family: "Every promotion so far came from the bug-fix and crack families. None of the four economy or re-grab arms on g_iter4 has passed." Of 11 behaviour-changing arms, 3 were promoted.
7. **Effects stack roughly additively, slightly sub-additively, and the check is cheap when arms share a control** (section 7).
   - Component effects are derived by differencing arms on the same control cells. Examples: PICKUP_AFTER_MOVE +0.08 all; crumbs +0.08 all and -0.03 upper; DAM_FIRST -0.13; builders -0.16; FILL_STEP+RELOC_STALL -0.04 all and -0.29 upper.
   - The direct test: g4ship1 = crumbs + pick, predicted "+0.157 all, +0.064 upper, about +14 net". Measured: "+0.144 all, +0.138 upper, +12 net (92% of the predicted all-cell sum)". On the first two seeds alone it reached 56%.
   - Discount a projected stack by the 56-92% additivity ratio and by the ~25% winner's-curse shrinkage. The doc's full-stack projection fell from "+0.33" to "+0.20 to +0.28 all-cell".
   - Caveats it lists: overlapping mechanisms ("both multiply re-grabs ... 'more re-grabs, not more captures' recurs"); a component measured on an older base; and the k/d veto from the basics battery (2.13 vs 3.11).
8. **Early reads of long filler tallies regress, and closes must be logged at the true final count** (section 8).
   - g4gym1 against Gymhgy: "it peaked at +31 after 400 pairs, then regressed" to +12 over 1,880 pairs (p 0.68).
   - g4crumb: the "log closed it at 560 pairs, +20 (+1.6 SE); the last 80 pairs (+10) were never logged". The true total was 640 pairs, +30 (p 0.029). g3escrg2 had the same problem (closed at 240, +8; actual 280, +14).
   - A tally that keeps running after its logged close leaves the ledger stale in both directions.
9. **Ratings of builds drift for reasons unrelated to the build** (section 3).
   - After each promotion the incumbent fell in absolute rank: g_iter3 from 12 to 20 and g_iter4 from 12 to 15. The reason: "the filler then spent thousands of games on its worst matchup, the next target, and one-dimensional Bradley-Terry cannot model a matchup that does not follow the ratings".
   - "Every gap to the predecessor stayed positive."
   - Unpromoted arms rated above the incumbent, for example g4ship1 at 1994 +- 76. Those ratings "come only from Gymhgy filler games and are not comparable".
   - A Bradley-Terry refit added "about +45 to every rating".
   - *Inference:* any tier defined by ratings inherits all of these artefacts.
10. **The ledger lost rows.** "g2nonav, g2bc, g2bc2, g2fast and g4econ2 have band tests in TRAINING_LOG.md but no row in REWRITE.md, although its table claims to hold every evaluated build." Two arms, g2bc and g2fast, had 0% discordance ("identical"). They are pure-refactor checks, and they confirm the pairing is exact when play does not change.
11. **The doc's rough strictness figures** (section 9, simulation "treats the three tests as independent", so overstated):
    - Null pass rate "about 3%".
    - A g4ship1-sized effect passed about 45% at 480 pairs; a pick-sized effect about 22%.
    - With an all-cell route (>= 2 SE, wins net >= -5), power rose to about 75% and the null to at most about 5%.

### Tools and reuse verdicts

| tool | what it does | verdict for 2023 |
|---|---|---|
| `2024/tools/eval-paired.py --tier <file>` | Splits paired results into all / upper / rest by a tier file. The default is `tools/upper-tier.txt`, re-derived at each promotion. | **ADAPT** (as other sections say). Add: (1) print the tier file's path and hash in every result line, and record it in the arm ledger; (2) **pin the tier file per incumbent at pre-registration**, with no edits mid-arm; (3) print per-seed rows, which give lesson 5's consistency screen for free. |
| `upper-tier.txt` git history (4 versions: 12, 11, 10, 5 bots) | Evidence of referent drift | **Lesson only.** It shows that "rated above the incumbent" shrinks the tier as you improve. |
| `2024/tools/filler-tally.py` (39 lines) | Running paired tally of a candidate vs a control on shared filler seeds. Keys on (opp, map, side, seed). Reports net, SE, identical and discordant counts. | **ADAPT** for 2023 target-filler pairs. Change the results.csv columns and pin the seed. Add a pre-registered N and a stop rule (lesson 8). As written it is an open-ended running tally, and that invites peeking. |
| `2024/tools/filler-pair.sh` (18 lines) | Runs the incumbent and a candidate on the same fresh band cells with one seed. | **ADAPT.** The idea is reusable. It is bound to bc24's scrim.sh, capability-census.sh and VM queue. |
| `2024/tools/arm-deltas.py` (41 lines) | Paired per-column capability deltas, arm minus control. Has a `--beaters` slice. | **ADAPT** for the component-differencing in lesson 7. Its seed regex hard-codes `.bc24`. |
| `per_seed.py` / `per_seed.out` | The doc's recomputation | **GONE.** It is reproducible in about 20 lines on top of eval-paired.py; my `tierdrift.py` is an example. |

### Pitfalls and implications for 2023 (inference unless quoted)

- **If 2023 keeps an upper-tier route, freeze its referent.** Use a fixed, named opponent list per incumbent, chosen before the arm is run. Record it with each verdict, and never re-derive it mid-arm or from ratings that the filler schedule distorts. Better: make the all-cell continuous margin the primary route (alternatives.md lesson 11 agrees). Report the upper slice descriptively, or only as part of a single simulated hybrid.
- **A relative tier ("above the incumbent") shrinks as you climb.** Its SE grows, and its share of wins tends toward zero. bc24's 5-bot tier gave 7 control wins in 116 games, so a sign test there is uninformative. In 2023 most games against strong bots may end only at round 2000 on the tiebreak, so the per-pair margin must stay informative in losses (islands held, anchors placed, resources), not only in wins.
- **Expect about 25% shrinkage from a first look to confirmation,** and treat a first-look upper-tier spike as suspect until the confirmation seeds replicate it (g2cr: +0.30 to +0.07).
- **Use per-seed sign consistency as a cheap screen** for near-miss arms. Consistent near-misses on independent mechanisms are stacking candidates. Projected stack gains should be discounted by the 56-92% additivity ratio.
- **Watch which opponents economy changes help.** If economy-style arms help mostly against weaker bots, a top-tier-weighted gate will reject all of them. That is bc24's "rest positive in 6/6, upper negative in 4/6". 2023's resource and anchor economy will produce many such arms.
- **Ledger hygiene.** Every band-tested arm, including no-op and refactor arms, gets a row with its tier version. Close every filler tally at a pre-registered N and log the final count.
- **Use one Elo-per-point conversion.** history.md uses about 7 Elo per win point ("+1.9 points, about +13 Elo near 50%"), while power.md uses 13 per point (band p(1-p) 0.126). The two are a factor of 2 apart in the same review. Derive 2023's figure from its own band win rates.

## Gap read: /home/terryvanbelle/projects/vibe/2025/agents/alice/tools/b0-null.py

Sources: `b0-null.py` (code, read directly, 5,584 B) and its sibling `tools/tail-check.py` (code, read directly,
4,133 B); a glance at `tools/b0-vision.py` (header and disc constant only). Context from the filtered reading room only:
`readroom-no2023/bc25/agents/alice/TRAINING_LOG.md` lines ~21040-21260 (Funnel B design and "B0 RUN"),
22040-22058 (requirement I closed on arithmetic), 22960-23090 (mopper tail and "TAIL PRECONDITION CHECK"),
`LEARNINGS.md` lines 168-172, `CLOSURE_MAP.md` rows 2 and 14 and section 18. No 2023-game content was found or used.
Nothing was run; every number below is quoted from the log unless marked (inference) or (computed here).

### What the tools do

**b0-null.py** reads bc25 `replay-dump.sh --map-at` ASCII arena frames on stdin. For each team-frame it computes,
over the vision discs (r^2 20, 69 tiles) of every soldier, three reference points instead of one:

- **OBSERVED** `U` = size of the union of discs (wall tiles excluded from board, discs and union alike).
- **CEILING** = `min(non-wall tiles, sum of clipped disc sizes)`: "perfect spread, nothing wasted."
- **RANDOM** = `A * (1 - prod_i(1 - d_i/A))`: the expected union if the SAME n units, with the frame's actual disc
  sizes, were dropped uniformly at random. Docstring: "This is the null a movement rule has to beat: scatter with no
  coordination at all already de-overlaps, because independent points rarely stack."

It prints per-frame `obs/ceil` and `obs/rand`, then aggregates (all frames, n>=6, early <300 / mid / late >=800) with
the registered ratio printed alongside both references and two "recoverable" tile counts: `RAND-U` (by merely beating
random) and `CEIL-U` (by perfect spread). If no frames parse it prints `!! no frames -- refusing to print a ratio` and
exits 1 rather than printing a ratio over nothing.

**tail-check.py** reads a bc25 census dump of 21 games, ranks games by alice's mopper spawns, takes the top 3 as the
"tail" and scores five candidates as **tail mean / rest mean**, against a list fixed in its docstring before the data
was opened (commit `e9b6614`). Registered PASS is C1 only (mopper share > 40%); C2 volume, C4 length and C5 tower count
are labelled KILL branches. It closes with a decomposition line: mopper count = share x volume, which factor carries it.

### Lessons, with evidence

**1. Before scoring a bar, ask "what is this a ratio OF?" and check the bar is reachable at all.**
- Registered: B0 = union / (n x 69), "**B0 KILL, zero code, decides first:** if measured non-redundancy is **>= 0.92**,
  B is dead." Measured **0.483** (wall-excluded variant **0.422**): "B0 does not kill B."
- But `n x 69` "demands n discs overlapping nowhere and falling entirely on the board. At 83 soldiers on a 60x60 map
  that is 5,727 distinct tiles from a 3,600-tile board. **0.92 was unreachable by arithmetic, not by any fact about
  alice.**" (83 x 69 = 5,727, checked here.)
- The direction of the error matters: "the mis-specification pushed toward B *passing*, i.e. toward spending the
  budget." It was still scored as registered ("a bar that cannot be met is not a gate", but moving it after seeing data
  is worse; b0-vision.py: "moving a goalpost after seeing the data is worse than a known bias whose direction is
  declared").
- Codified in LEARNINGS.md 168: "**Check a bar's DENOMINATOR and a proxy's DIRECTION before scoring anything against
  them.** ... **An upper-bound proxy is honest for a KILL and inadmissible for a PASS.**"

**2. Report OBSERVED between a RANDOM null and a CEILING, never against the raw bar alone.**
- Log table: CEILING "U/CEIL = **0.615**"; RANDOM "**U/RAND = 0.796**". "**Alice's soldiers cluster HARDER THAN
  CHANCE.** Dropping the same soldiers at random would see **25.6% more distinct tiles** than alice actually sees, and
  it degrades through the game: 0.863 early -> 0.797 mid -> **0.761 late**."
- The docstring gives the reading rule: "The number that matters ... is where OBSERVED sits BETWEEN RANDOM and
  CEILING. Below RANDOM means alice clusters harder than chance and even a crude repulsion recovers tiles. At or above
  RANDOM means the spread is already doing work and only a genuinely clever rule gains anything."
- The two references then closed a later requirement with no experiment (log ~22044): a registered target of **+54%**
  visible area vs "beating random placement (what a real rule could plausibly reach) **+25.6%**" and "perfect spread
  (an oracle no rule achieves) +62.6%". "Requirement I's terminal bar is **unreachable by the spacing family**, and
  that follows from three numbers I already had rather than from any new experiment."

**3. Passing a gate is not being the lever: convert the ceiling into the terminal currency.**
- "Perfect spread raises the union by 62.6%. If empties scale with union, empty-visibility goes **6.4% -> ~10.4%**.
  B's entire ceiling is **+4 percentage points against a 93.6% deficit.** B cleared B0 honestly and is *still* not the
  answer." CLOSURE_MAP row 2 files spacing as `oracle-ceilinged`: "none written; the ceiling is arithmetic."
- The ceiling measurement also found the real deficit: "Of **52,879** paintable-empty tiles ... **3,384 (6.4%)** are
  inside the union of the whole team's soldier vision", and "on mit, **8-20 unclaimed tower sites sit on the board for
  700 rounds and alice's entire team can see zero of them at every single sample.**" Cost: "**zero games.**"

**4. Score tail hypotheses only against candidates committed before looking, derived from the code, not the data.**
- "n=3 with an unbounded candidate set always succeeds, so the candidates come from the spawn decision itself, not from
  the replays." Candidates C1-C5 were taken from the verbatim spawn rule
  (`(rnd(4) == 0) ? MOPPER : SOLDIER`, plus the affordability guard) and committed in `e9b6614` **before** opening data.
- The expected answer was written down first: "So I expect a KILL, and say so before measuring."
- "**Measured as prevalence-in-tail against prevalence-in-rest, never presence-in-tail** -- a property shared by all
  three tail games *and* most of the other eighteen explains nothing."
- "**A weak hit reads as KILL**, not as encouragement: with three games the power to separate a shared trigger from
  coincidence is genuinely low, so only a large, clean separation counts."

**5. Decompose a count into share x volume before calling a heavy tail a pathology.**
- The tail: mopper spawns per game sorted "3, 4, 5, ... 38, **118, 119, 292**", mean **38.8**, median **18**, sd
  **66.3**, 95% CI **10.4 ... 67.2**; "**3 of 21 games (14%) account for 529 of 815 mopper spawns -- 65%**". It was
  first read as an absorbing state.
- Result table: C1 share **0.260 v 0.195 (1.33x)**; C2 total spawns **674.3 v 84.3 (8.00x)**; C3 1.59x; C4 game length
  **2.21x**; C5 towers **3.02x**. "Registered PASS was C1 > 40%. Measured 26.0% -- which IS the intended 25% roll.
  **VERDICT: KILL. The tail is VOLUME, not a mopper pathology.**" Tail games: "DefaultHuge, DonkeyKong and Circuit --
  the long, big, many-tower games."
- "It is also what game-size variance looks like from outside, and I had no way to tell them apart until I measured
  the share. **A shape is not a mechanism.**" Also: "**I proposed capping a runaway that no longer runs away.**"
  CLOSURE_MAP row 14: `refuted-on-value`.

**6. A single quoted figure from a heavy-tailed distribution is not a rate.** "The log's '7 per game' is the 5th of 21
games ... **it was a mean compared against an unprovenanced draw from a heavy tail I had never characterised.**" The
direction survived because its price was computed at every candidate rate (8.7% / 22.4% / 48.3% of paint).

### Tools, with reuse verdicts

| tool | verdict | why |
|---|---|---|
| `b0-null.py` | **PORT the `analyse()` math (~30 lines); discard the parser** | The `frames()` parser is bc25-only (`=== ARENA round` ASCII, glyphs `.#o*aAbBtTnNdDsSmMpP`, soldier `s`/`S`). The null/ceiling arithmetic is game-agnostic. The disc constant transfers exactly: r^2 20 = **69 tiles** (computed here), and 2023 launcher vision is r^2 20. Needs a .bc23-to-grid dumper first. |
| `tail-check.py` | **REWRITE (~60 lines), keep the structure** | Regex is bc25 census format and hard-codes `'alice' in who`. Keep: candidate list in the docstring with a commit hash, tail-vs-rest ratios, one registered PASS condition, explicit KILL branches, share x volume closing line. |
| `b0-vision.py` (sibling) | reference only | Shows the companion practice of printing the registered ratio AND a clip-corrected one, with the known bias direction declared in the header. |

Other 2023 disc sizes for the same procedure (computed here): r^2 4 = 13 tiles (cloud vision, island write zone),
r^2 9 = 29 (HQ attack and HQ write zone), r^2 16 = 49 (launcher attack), r^2 34 = 109.

### Pitfalls found in the code (inference from reading, not run)

- **b0-null's "registered" line is not quite the registered number.** Its `U` excludes walls, so `U/(n*69)` there
  should reproduce the wall-excluded variant (log: 0.422), not the registered 0.483 printed by b0-vision.py.
- **CEILING is conditional on observed positions.** It sums the discs as clipped at the units' actual locations; an
  oracle placement would move units off edges and walls and get bigger discs, so the true ceiling is >= the printed
  one and "recoverable by perfect spread" is an underestimate.
- **RANDOM is an analytic approximation.** `P(tile covered) = d_i/A` treats every tile as equally coverable and uses
  observed disc sizes; edge tiles are covered by fewer placements. For 2023 maps with walls, clouds (vision r^2 4) and
  currents, a Monte Carlo null (drop the same n units on passable tiles, recompute the union, repeat ~200 times) is
  cheap at <= 3,600 tiles and exact.
- `RAND - U` goes negative when the bot beats random; read the sign, not just the magnitude.
- **tail-check selects the tail on the outcome** (top-3 mopper count). If volume varies more across games than share,
  C2 will look elevated almost automatically, so C2 alone is not evidence. Only C1 is coded into the verdict; the KILL
  string "the tail is VOLUME" is fixed text that the code does not test (the closing decomposition line does compare
  c1 and c2). It uses unweighted means of per-game shares, applies no permutation null over random 3-game subsets,
  ties in the sort are arbitrary, and fewer than 4 games crashes `statistics.mean` on an empty rest.

### Transfer to Battlecode 2023 (inference)

- **Pre-check every coverage bar against the 3,600-tile maximum board.** Example (computed here): 4 amplifiers x 69 =
  276 tiles = **7.7%** of a 60x60 map but **69%** of a 20x20 map. A bar such as "amplifiers keep X% of the map
  writable" is unreachable above ~8% on large maps whatever the placement rule. The same holds for launcher-vision
  coverage, island discovery and well discovery.
- **Use OBSERVED / RANDOM / CEILING for any spread question:** amplifier write-zone coverage (HQ r^2 9 + amplifier
  r^2 20 + anchored island r^2 4), launcher vision union, scout coverage of islands and wells. Clouds shrink vision to
  13 tiles, so treat cloud tiles like the wall exclusion when sizing discs.
- **The sign of "below RANDOM" depends on the objective.** In bc25 painting, clustering harder than chance was a
  deficit. In 2023 combat, launchers clustering for focus fire (20 dmg, attack r^2 16) may be intended. State before
  measuring whether below-random is good or bad for that unit type.
- **Normalize volume before reading tails.** Count variables in 2023 will be driven by map size (20x20..60x60), HQ count
  (1-4) and game length. Before calling a heavy tail in carrier deaths, launcher spawns or anchor losses a pathology,
  split count into share x volume and take the candidate triggers from our own HQ build and carrier logic, committed
  before opening replays.

## Gap read: /home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc25/agents/darla/DESIGN.md

Scope: read in full lines 827–2643, 1767–1903, 4216–5430, 6176–7284 and 7922–8060 of the filtered copy
(11,641 lines). Code checked directly: `2025/agents/darla/tools/{make-arm.sh, plot_arms.py, disk-guard.sh,
status-line.sh}`. Items the bc25 reports already carry are only cross-referenced here: `ls -1t` run identification,
the pipefail/SIGPIPE guard, `pgrep` self-kill, `watch-state.sh`, the self-limiting-condition rule, held-out ≈60%
overfitting, and determinism checks. Everything below is new or adds evidence. "Inference" marks my own reasoning.
Numbers are as the notebook gives them; "sd" means the notebook's z or sd figures.

### 1. Checks to run before an experiment (most were learned by wasting runs)

| Check | What happened | Quote / number |
|---|---|---|
| **An impossible result is a harness bug** | `darla14` returned **0/144**, every game lost. The sed matched nothing, so the file kept `package darla;` and the engine could not load `darla14.RobotPlayer`. `javac ... && echo COMPILE_OK` printed OK because it compiled *the baseline* under a new directory name. | "A verification whose failure mode is silence is not a verification." "A one-constant change cannot lose 144 of 144 ... a result far outside what the mechanism could produce is a bug report about the harness, not a finding." |
| **Quarantine voids, don't delete them** | Void runs had `bot=` rewritten to `darla14VOID`, with a `VOID.md` beside each, so `plot_arms.py` could not aggregate them. Aggregated, the void would have drawn the splasher-share ladder "as a cliff at 55%", with "a tidy story available". | Evidence kept, number excluded. |
| **Static no-op check: can this dose change the argmax?** | The splash scorer's paint terms max out at **9×3 + 4×2 = 35**, so any tower bonus above 35 always wins whenever a tower is in range. Doses 50, 100 and 200 all scored 89/144, with "**0 differing game rows**" against the baseline: "288 games bought zero information". The first dose below the ceiling (20/12) changed **104 of 144** games and scored −6. | "A constant that already dominates its competitors has no dose-response — it has a threshold, and the only informative doses are near that threshold." |
| **Does the dose leave a viable configuration?** | The mix was `SPLASHER_IN_20 : 2 : (18 − SPLASHER_IN_20)`, so dose 18 meant **0% soldiers**. Result 47/150, z −4.58: "that known cliff, not information about the question I was asking." | "check that the dose leaves a viable configuration, not just a different one." |
| **Does treatment differ from control on these games?** | `darla56` switched behaviour at 1,600 tiles. It was then run on the 1,200–1,599-tile band, where it is byte-identical to the baseline (40/48, uninterpretable). | "three separate times tonight I have launched a comparison whose two sides were guaranteed to be the same." |
| **Count the units before checking the mechanism** | The mopper paint-mule arm read `mu=0/0` because one game built **217 soldiers, 24 splashers, 1 mopper**. `PAINT_FLOOR` 200 meant a mopper needed its tower to hold 300 paint; towers held about 54. So the earlier "mopper" arms were mislabelled: `darla3` improved the navigation of a unit that existed once per game, and `darla2` (moppers = 0) quietly raised the soldier share from 75% to 85%. | "A population census is as necessary as a mechanism census, and it is cheaper." |
| **Multiply the branch's conditions before building** | `darla90` (a free action during refill trips) changed only 6 of 75 maps; 69 played 1–1. `darla93` (ruin crowding) was closed without an arm: ruin work is ~20% of soldier turns and crowding ~15% of that, so "~3% of soldier turns". | "where the change requires two conditions at once, multiply them." |
| **Measure the trigger rate in both directions** | `darla99`'s trigger was almost always true and flooded the army. `darla106`'s (defend a tower, only within r² 16 of one) fired **3 times in 1,949 soldier turns (0.15%)**. Pre-measurements later killed arms for the price of one probe: `darla110` found **0.27 soldiers per damaged tower-turn**, which refuted routing before it was built; `darla111` found siege movement on **1.2%** of splasher turns against a registered 5% bar. | "The permission was never the constraint; presence was." |
| **Rare vs suppressed** | The `foe == 0` gate hid a branch. The earlier arm `darla74` had measured it at under 1% and drawn conclusions from that. Removing the gate took `frontNone` from 0 to 28 and `IDLE-ENEMY` from 149 to "absent from the top five". | "the next arm that reasons from 'this branch is rarely reached' needs to know the difference between *rare* and *suppressed*." |
| **Pin falsifiers to measured quantities** | `darla108` registered `ac >= 10` by carrying over a count of stalled *turns* (252) to a counter that ticks once per *ruin*. It got 7. `darla109`'s "8 of 12 games" bar was a guess, and it got 7 of 12. Neither bar was moved after the data came in ("precisely the `darla98` failure"), and a one-shot hard stop was registered. | "a falsifier should be pinned to something already measured ... not to a round number." |
| **State why the lever is causal** | Final tower count and coverage "agree in all twelve" `v3` games, so `darla113` raised towers. Mean final towers went **5.8 → 8.7**, coverage *fell* (maze A 422→249, maze B 477→152, TheBest A 171→132), the roster scored **33/150**, and `v3` went **56/150 (37.3%)** against 46.0%. | "before moving any quantity X, state what makes X *causal* for coverage rather than merely correlated with it." "Coverage decides the game; tower count does not." |
| **Declare combination arms before seeing scores** | `darla28` combined two +2 leans and was registered as a joint arm, with its falsifier, before the results. | "combining candidates after seeing their scores is exactly how noise gets promoted" |

### 2. Instrument lessons

- **The noise floor needs more than 3 points.** Fresh-sample baselines over 150 games: 97, 94, 101 gave sd **2.34**.
  Adding 89 gave **3.37** ("The estimate moved 44%"), with a 2-sd floor of 6.7 points. Six points (97, 94, 101, 89,
  92, 95, pooled 568/900) settled at sd **2.75**, a **5.5-point** 2-sd floor. The binomial sd (4.08) was a
  conservative upper bound. Consequence: "this instrument can only see damage, not improvement, at the sizes I have
  been producing". Detecting +3% would need "on the order of a thousand games per arm".
- **A difference of differences hides real effects.** Two independent +2 screens and their +4 combination
  (+0.67 sd) were all inside the floor. The paired head-to-head on 75 maps × 2 sides read **97–53, z +3.59, swept
  32/10**. Identity check: wins − losses = 2 × (swept − swept-against), 44 = 2 × 22. Attribution head-to-heads:
  share alone **91/150 (z +2.61)**, threshold alone **86/150 (z +1.80)**, roughly additive. The flat ladder used to
  dismiss the threshold was itself a blunt-instrument artefact: "A flat curve measured with a blunt instrument is
  not a flat curve."
- **The paired mirror cannot see opponent-specific effects.** The post-accept large-map gap split by opponent was
  carol −1.0 points, bob 36.0, alice 41.9. The large-map rule measured head-to-head (against a carol-shaped
  baseline) read exactly 75/150. The same rule against alice and bob read 76/148 vs 69/148, McNemar z +1.12. The
  notebook's instrument table: "does this change help *in general*?" → paired head-to-head; "against a specific
  economy?" → screen split by opponent.
- **A lead built on a subset of opponents can be a trade.** The large-map rule had a monotone dose curve (50%
  splasher +1.12, 40% +0.00, 30% −0.47), an interpolated prediction that held, and the same sign against alice and
  bob. Against the excluded opponent: alice +5, bob +2, **carol −5**, net **+2 over 222 games**. It was not
  adopted. "every one of those measurements excluded the opponent the change hurts." Rule: prefer changes that help
  uniformly over trades, because the hidden benchmark's response to a trade is unpredictable.
- **Instruments can disagree in sign.** `darla86` read −6 in the mirror and **+1.60** on the 450-game roster.
  Standing rule: if the trigger reads the **opponent's** state, the mirror is a screen and the roster decides; if
  it reads only our own state, the two agree. "self-play does not neutralise an opponent-dependent trigger, it
  standardises it, which is a different bias and not a smaller one."
- **Per-opponent slices are noise unless large.** A 150-game slice with about 17 discordant pairs has sd ≈ √17 ≈ 4
  games. Carol read **+9, −9, −1** across three gate variants, and two arms (`darla91`, `darla92`) were built on
  that story. Rule: "do not build an arm on a slice difference under ~8 games, and never on the most extreme slice
  of several without counting how many were looked at." Also: "a per-opponent decomposition is a hypothesis
  generator, not evidence"; "One roster produces stories; two rosters test them"; "Aggregates are where opposite
  effects go to cancel."
- **Match a second roster's difficulty to the first.** Reference scores: standard 341/450 (75.8%), widened 338/450
  (75.1%), third generation 383/450 (85.1%). The easier set yielded **32 discordant pairs against 47 and 56** (a thin
  vote, as predicted before it ran). Still, a third set flipped decisions twice. It closed `darla86` (combined
  +1.18 over 135 discordant) and carried `darla96` from "null" on one roster (+0.35, 17–15 of 32) to **+3.26**
  combined (widened +2.61, third +2.68, 85 discordant). "The habit that saved it was queueing both rosters by
  default for a change, not the judgement I applied to the first number."
- **A fixed pool is a census, not a sample.** A replication of `i5` against `v3` came back byte-identical on all
  150 rows. The notebook had written a "±4 point error bar" one entry earlier and then retracted it: "There is no
  sampling error in that number at all; it is known exactly." What is uncertain is transfer to maps and opponents
  outside the pool. "Repetition is never power here." On a fixed pool, 70 vs 69 is a real one-map-side difference,
  and "a one-game edge on the 75-map pool we tune against is the definition of what does not generalise".
- **Benefits a screen cannot express show up there only as costs.** No tower dies in a darla mirror, so the
  tower-defence arm read −4 there: "a screen that cannot express the mechanism reports only the cost". Against
  `v3`, our towers died (**3 of 12** built on TheBest, against v3's 0; `v3` made 106 tower attacks for 5,500 damage
  vs our 18 for 1,250). "Every finding built on 'towers are permanent' was true of the instrument and false of the
  opponent."
- **A self-play catastrophe reads worse than it is:** 7/150 (4.7%) in the mirror and 82/450 (18.2%) on the roster.
  **Queue the long confirm run after the screen reports** when the registered risk (here, bytecode) shows up in
  the first games. The screen took 13 minutes; the confirm took 40.
- **Opponent independence is necessary, not sufficient.** Iteration 4 was the strongest roster result (+3.26 over
  1,350 games) and moved `v3` by −1 game (9 discordant, z −0.33). The roster lineages share darla's ancestry "and
  therefore its blind spots."
- **Small but real waste is invisible.** Soldiers hitting towers that never die was 1.3% of soldier turns × 20%
  soldiers ≈ **0.3% of unit-turns**. Removing it was null (−0.98 sd). Separately, four "well-argued,
  mechanism-grounded" predictions (splash-score weights, `MONEY_MOD`, `CHIP_RESERVE`, refill logistics) were flat
  nulls because each described "something the decision procedure never actually consults".
- **Exact 75/150 needs one more check.** "all 75 maps split 1–1" means a provable no-op (e.g. a census override
  that `MONEY_MOD = 4` made unreachable). 67 maps 1–1 with 8 diverging that cancel is a real zero effect: "same
  number, different fact."

### 3. Design-shape findings that transfer (bc25 game, abstracted)

- **Gate rule:** "a gate is flat on the side where it is already saturated, and bites on the side where it starts
  admitting something." Four gates, two in each direction:

  | gate | loose side | tight / admitting side |
  |---|---|---|
  | `CHIP_RESERVE` 1200 | 600: 76/150, z +0.16 | 2400: **18/150, z −9.31** (treasury normally ~1,400) |
  | `MONEY_MOD` 4 | 8: −2 | 2: **−30, −5.00 sd** |
  | `PAINT_FLOOR` 200 | 300: exactly 75/150 | 100: **−2.29 sd** (moppers re-admitted) |
  | `REFILL_LOW` 50 | 25: z −0.82 | 100: **36/150, z −6.37** (commuting flood) |

  The worst results all had one cause: "a constant set above the level its resource normally holds". A gate's shape
  also moved with the build: `SPLASH_FLOOR` went from steep on both sides to "flat below and sloped above" after the
  mix changed. Its notebook verdict: "a gate's shape is a property of the build, not of the game."
- **Gates that read noisy state need a decaying counter, and a working valve can still be worth nothing.** A release
  valve that needed 10 *consecutive* pinned rounds never fired (`pin=1`, `pin=2`; `pf=0` for the bot's whole life).
  Changing reset-to-0 into decrement-by-1 made it fire 34–48 times per tower, and it was worth **19–19 of 38,
  z 0.00**. The 10-consecutive-rounds requirement was "a quantity that cannot stay still for ten rounds".
- **The binding constraint flipped with map size** (`sb=` per tower). Small maps were paint-blocked, e.g. Brat
  78 chips / 423 paint / 9 spawned. Large maps were chip-blocked, e.g. TheBest 397 / 314 / 1 and DefaultHuge
  544 / 227 / 14. DefaultSmall spawned 32 times. Releasing chips did nothing. The win (iteration 4, +3.26) was to
  build money towers only "when the treasury already covers the reserve plus our most expensive robot". It derived
  the threshold from existing constants and swept no dose.
- **Heading targets must be stable, not merely good.** Splasher positioning record: the tower attractor was worth
  **99–51**; nearest enemy paint −38; enemy-paint centroid −22, and **27/150 (−7.84 sd)** at 70% splashers;
  "dispersed" ID-indexed enemy tile **9/150 (−10.78 sd)**. Walking onto enemy paint scored **7/150**, with games
  ending earlier (1,035 → 836 rounds). Stopping two tiles short scored 10/150. Three explanations (tower kills,
  proximity, dispersion) were each refuted before the founding note's "a persistent heading beats a nearest-target
  rule" fit all five data points. "The requirement is a *stable target*, not a good one."
- **A stall detector cannot tell stalled from finished.** "Expansion has stalled" and "expansion is complete" are
  the same observation without a team-wide count of what is left. Tower-count insurance scored 35/150 (−6.54 sd)
  because "every game starts at 2 towers", so it fired through every opening. Stall-triggered insurance scored
  40/150.
- **Recomputed decisions conflict with permanent commitments.** Tower type was recomputed every turn (from a
  treasury threshold and a per-robot census), while pattern marks were laid once. A finished pattern could then
  never complete: 252 stalled soldier-turns and 21 patience bans in 12 games. The fix made "the *ground* the
  authority", and a geometric key `|2x-(w-1)| + |2y-(h-1)|` kept choices invariant under rotation and reflection.
  The fix built 7 extra towers and was worth **exactly 75/150**: "a correctness fix whose correctness does not
  matter" (left documented, not shipped).
- **Factual misreads of the replay header.** The header lists both teams' starting towers (4), which was read as
  ours (2). That made `towers <= 4` permanently true, and the opening override never switched off: 19 soldiers,
  0 splashers, 53/150. In replay aggregates, `team1` flips by side. Keyed on T1 the table showed 6 of 12 wins;
  re-keyed from each file's `GameHeader` it matched the benchmark's 4 of 12.
- **The whole army was idle.** Splashers, 70% of robot-turns, splashed on **1.9–2.4%** of turns. Soldiers
  painted on **9.2%** and were idle on **67%**. `v3` landed 46,171 paint actions to our 35,776. An earlier census
  read only the first token of the state string, missed appended tokens (`approach/ring/backoff`, `pnt`), and was
  wrong twice. "a cumulative state string cannot be censused on its first token."

### 4. Tooling and process pitfalls (new beyond the bc25 reports)

- **Wrong-path append:** a `cat >> DESIGN.md` run from the repo root wrote six sections to `/DESIGN.md`, untracked,
  for about a day. They were recovered out of order and labelled. "an append is silent when it lands in the wrong
  place." The notebook was the one unguarded write. **(Inference: always append with an absolute path and
  verify with `grep -c '^## Gap read'` afterwards; this report was appended that way.)**
- **`paste` over two independently sorted lists** produced alice −12 / carol +18 instead of the true −1 / +7: "`join`
  on a key, never `paste` on two sorts."
- **`$(grep -c ... || echo 0)` on an empty file gives `"0\n0"`**, because grep prints 0 and exits 1. The orphan
  quarantine missed the very directory that caused a ghost-run report ("54-hour-old directory reported as live").
- **Multi-line sed comment inserts glue the next code line onto a `//` line.** Rule: one-line code comments, with
  the reasoning in the notebook.
- **Disk:** the driver hit 100% (6.6M free) and a commit failed with ENOSPC. Runs wrote 40–70MB each, and the VM's
  smaller disk filled first (three arms died "inside four seconds"). The deployed `disk-guard.sh` is two-stage
  (`LOW_MB` default 1200, escalating below 500 MB, `DISK CRITICAL` below 400). This differs from the notebook's
  first description ("below 2GB"), because a too-eager first version deleted a needed control replay.
- **A model handoff needs a machine-checkable resume point**, written per METHODS §18 as "run-ids and gates, not
  intentions": shipped build plus run ids, in-flight jobs and PIDs, a closed-directions table with reopen
  conditions, and open problems with numbers.

### 5. Tools: reuse verdicts

| Tool (`2025/agents/darla/tools/`) | Lines | Verdict for 2023 |
|---|---|---|
| `make-arm.sh` | 56 | **Adapt.** Copies the shipped package, applies a sed, and refuses (deleting the dir) unless: the package line is rewritten (`grep -qx`), the `BUILD` constant is rewritten (any prior value), the EXPECT text is present in non-comment code (single `awk ... index()` pass, no pipeline race), and the diff below the package line is non-empty. Change `package darla;` and the paths. Cosmetic: the final `grep -n "$EXPECT"` echo is a regex. Add a viability or decision-change note per arm (section 1). |
| `plot_arms.py` | 218 | **Reference / adapt.** One dose-response chart per axis with ≥3 points, from `progress/arms.txt` (`pkg|axis|dose|label`) plus `progress/baseline-doses.txt`, so the shipped value plots as a point. Error bars are binomial at p=0.5 (`0.5*sqrt(n)` games). Tied to bc25 `summary.txt` and the three-opponent layout. |
| `disk-guard.sh` | 57 | **Adapt if replays are kept.** flock single-instance loop, two-stage prune via the sanctioned prune tool, prunes the VM too. Paths and thresholds are bc25-specific. (.bc23 replay sizes are unmeasured here.) |
| `status-line.sh` | 82 | Already "Steal" in the bc25 reports. The new detail: pick the live run by name-sorted timestamp dirs, skip ones with `summary.txt`, and skip orphans by **write freshness** `max(mtime(dir), mtime(results.txt))`, not by whether a file exists. |

### 6. Transfer to Battlecode 2023 (inference throughout)

- **Run the section-1 checks before every arm.** Most map onto 2023 directly:
  - *Static argmax ceilings:* launcher target scoring, carrier well choice and island priority. A weight that always
    dominates is a switch, so dose only near its threshold.
  - *Population census:* how many amplifiers, boosters and destabilizers actually get built. Any shared-array arm
    is untested if write-capable units (within r² 9 of HQ, r² 20 of an amplifier, r² 4 of an anchored island)
    are rarely in range, so log write attempts vs successes (`ms=sent/heard`-style).
  - *Viability:* a mix dose must not zero carriers or launchers.
  - *Multiplied trigger rates:* e.g. "launcher sees enemy AND is within r² 16 AND has cooldown".
- **Gates in the HQ build queue.** The 2023 HQ has resource gates: saving 80 Ad + 80 Mn for an anchor, Mn for
  45-Mn launchers, Ad for 50-Ad carriers. Before sweeping, probe the side that starts admitting (or blocking) builds,
  check each gate against the level its resource normally holds, and log *why* each build roll died (the
  `darla112` table: reserve 51.2%, floor 42.1%, `canBuildRobot` 5.5%, built **1.2%**). Expect the binding resource
  to differ between 20x20 and 60x60 maps, as it did in bc25.
- **Stable landmarks exist in 2023.** Wells, islands and (via symmetry) enemy HQs never move. Prefer locking units
  onto a fixed landmark over recomputing "nearest enemy" each turn. A darla note: an enemy HQ is a "stable landmark
  ... known before any enemy is seen". 2023 HQs are indestructible and deal 4 damage within r² 9, so the
  standoff geometry matters (compare darla88 vs darla89).
- **Shared commitments need a single authority.** Which island to anchor or which well a carrier serves should be
  keyed on invariant data (coordinates or ids) or written once to the shared array. Do not let each unit re-derive
  it per turn. Unlike bc25, 2023 has a team-wide array, so the "is anything left to claim?" signal that bc25
  could not compute (unclaimed islands, uncontested wells) is available. The stalled-vs-finished trap therefore
  has an exit in 2023.
- **Choose instruments by trigger class.** Arms that read enemy state (launcher micro, retreat on enemy count,
  island contest) go to a diverse opponent set, never only the mirror. Our-state arms (carrier load thresholds,
  build order) can use the paired mirror. With one 150-game run per opponent, per-opponent slices carry sd ≈ 4
  games, so do not chase slices under ~8.
- **Correlation trap for 2023's tiebreaks.** The tiebreak goes islands, anchors placed, elixir, mana, adamantium.
  "Winners hold more islands" does not mean "push anchors" without a causal argument; a carrier hauling an anchor is
  not mining (cf. `darla113`). State the causal path before moving a quantity.
- **Check determinism once, then stop re-running.** If engine 3.0.15 replays identically for the same build, maps
  and opponent (unverified for 2023; check once with a byte-identical repeat), then repeats add nothing and only
  new maps or opponents add power. Key wins off each .bc23 file's own header and team mapping, never a fixed team
  slot.
- **Instrument indicator strings for whole-string token counts** (not first-token), plus a bytecode-overrun
  counter and the void-on-overrun rule. 2023 limits are tighter (carrier 12,500, others 10,000).

## Gap read: /home/terryvanbelle/projects/vibe/reference/readroom-no2023/bc25/METHODS_EVIDENCE.md

**What it is.** I read the whole file (168,984 B, 2,544 lines), all 71 `### §N` sections in order. Its header says
"Do not read this file whole"; the reason given is cold-start token cost, not content. It holds the worked evidence for
71 of the 86 METHODS entries. **15 entries have no section here:** §3, §4, §5, §7, §8, §8b, §9, §11, §15, §17, §18, §23,
§24b, §28 and §39. Their only evidence is the inline text in METHODS.md. I pulled that inline text for the six that 2023
relies on (§4, §5, §9, §17, §18, §23) from the filtered METHODS.md.

Everything here is bc25 (the 2025 paint game). It covers three lineages (alice, bob, carol) and the coordinator's own
"my error" entries. Nouns are deliberately generic ("unit", "structure", "resource", "the binding term"), so the numbers
are bc25-specific and every transfer below is **inference**. Nothing in the file describes 2023 play.

**Code read directly:**
- bc25: `/home/terryvanbelle/projects/vibe/2025/agents/alice/tools/e2-gate.py`, `roster-stale.sh`, `check-pointers.sh`,
  `sweep-tally.sh`, and the head of `unconfirmed.sh`.
- 2023: `/home/terryvanbelle/projects/vibe/2023/tools/gauntlet.sh` and the docstring of `compare.py`.
- 2023: `/home/terryvanbelle/projects/vibe/2023/TRAINING_ALGORITHM.md` §2 ("TA" below). It is our own 2023 document, not
  a prior-year one.

### 1. The evidence behind each rule 2023 adopts

"S" is SYNTHESIS.md and "TA" is TRAINING_ALGORITHM.md. Numbers are quoted as the file writes them.

| 2023 rule (where adopted) | METHODS § | the failure or cost that produced it | what the evidence adds or corrects |
|---|---|---|---|
| Show delivery before you judge value (S §6.1 row 1; TA step 5) | §34, §35, §9, §1 | A lever that fired on about 1% of turns was nearly closed as a null: "a lever that fires at 1% is UNTESTED, not rejected". A treatment moved +6.4% while a byte-identical null arm moved ±7.7%. The treatment went 4–2 and **the null also went 4–2**. §9 (inline): a share check caught a 4× dose overshoot for one game; the same error class had earlier cost a full 50-game screen | **Measure the funnel jointly.** Conditioned stage by stage, the funnel ran 6.2% → 15.1% → 48.6%, 0.45% overall against a 2.0% bar. The middle step was 34.0% as a marginal. So the naive product through step two gave 2.10% ("a licence to build"), but the joint measurement was 0.93%, which reverses the decision. Estimates composed from separately measured parts were wrong by 5–10× three times in one day (5.7× predicted vs 1.15× realised; 21× vs 2.22×; 8.9% vs 1.4%). Per-stage counters are marginals by construction, so record the **cross-tab**. Measure at the call site where a **decision** exists: 64% of entries into one movement path followed an already-open heading, with no choice at all |
| Reachability: the choice set has more than one member (TA step 3) | §27, §35 | The choice set was "1.00 candidates per turn and was never 2 across 15,229 turns", so a shared tie-break had no tie to break. A "44.8% real choice" pass had been measured over hypothetical moves | When agents' inputs do not overlap, no local rule can coordinate them: "no function of each agent's own inputs can coordinate agents whose inputs do not overlap". A channel is required |
| Price what the change displaces (TA step 3) | §2, §35, §66 | A theoretical exchange rate used for 50 iterations was **8× optimistic**. The real rate came from the lineage's own rejected gates. A "free" opportunity-only mechanism (5 resource per attempt × 698 opportunities) would have consumed **70% of the unit-spawn budget**: "The turn is free; the resource is not". A mechanism priced at 2.8% of frames against one opponent was producing **38.2%** of the unit mix in the test population. It was removed: "I removed a working mechanism and replaced it with a weaker one" | Price against the **null action**: a ferry returned 0.0020, and building one more consumer also returned 0.0020, while the ferry paid double the drain. Extrapolate at the **marginal** rate, not the average: +3 vs +9, against a +26 bar. Price against **your own** observed best, not the opponent's: 1.2 : 1 vs 2.3 : 1, which changed which half to aim at. Before deleting a constraint, list every policy that reads it, **from the source**. One deletion inverted the mix 13× |
| Check that we are behind on a quantity before optimising it (TA step 2) | §32, §55, §81 | The check was free, off replays already on disk, and killed three candidates in one session. On its fourth use it found a real deficit: "36 against 106". A queued lever ("cutting it to 40 is worth 50% of the gap") had been priced on the lineage's own bot with one parameter changed. The opponent's real value was 95.8 vs 99.8, a ratio of 0.96, so the axis did not exist | A mirror gauntlet is 50/50 **by construction**, so it cannot condition on outcome. §55: a lineage was best in the field on a cost ratio **and losing because of it**. On the third such instance it became a standing check: "measure the winner's value of a cost before pricing it as a defect". One replay dump then killed three candidates |
| Dose ladder including a zero arm (TA step 3) | §43, §53, §69, §21 | A zero arm did not lose on score; it **ended early**, because the zeroed term "was the only brake her bot had on the opponent's win condition". A rule requiring 300 of a stock that holds about 154 skipped **97.7%** of its decisions (708 allowed vs 29,920 skipped). A threshold on a quantised quantity sat on a mass point, and the verdict turned on "0.08 of a unit" | "A zero dose tests REMOVAL, not reduction." A one-knob ladder cannot attribute a gain between two quantities that the knob moves in opposite directions. **Prefer a rate to a threshold** when the distribution is unmeasured. Set detector thresholds from a measured healthy baseline (there, the longest innocent run was 1) |
| Identity control on every verdict path (S lesson 5; P0 `determinism-check`) | §54, §78, §46 | On a deterministic engine, a policy-identical placebo gives a floor of **zero**. It "actively licenses the broken check", because the noise lives in arm and control playing **different games**. A seed-change placebo showed only **2% of cross-architecture games survive a seed change, against 44% of self-play games**. The floor was sd 4.18 per 150. A −4 bucket called "a refutation" was 1.46 sd | Register the identity check's expected **values** (three specific round counts), not "should match". Run the null arm **in the same gauntlet** so the map draw is shared, and treat \|net_null\| ≥ bar as **VOID**, not as a reject. A same-game counterfactual counter is exact at any n (97 permitted vs 51). **For 2023 (inference): "a byte-identical copy reads 0 discordant" proves identity only. The noise floor needs a seed-varied null, and external-field pairs will need more games than mirror pairs** |
| Know the gate's power (S lesson 6; P1 gate maths) | §4, §5 (inline), §41, §73 | §4: over 59 arms, a gate labelled 2.0 sd was worth about 1.0 sd. §41: a rung at 18/50 was called "4.0 sd below even"; it was **2.0 sd**. With 12 rungs, P(at least one at \|z\| ≥ 2) = **43%** | §5: with n=25 drawn from N=75, the finite-population correction cuts sd by 18%, and the natural unit is per-map wins in {0,1,2}. A 25-map cell has sd ≈ 3.05 net swept and "cannot resolve anything below about ±6". An alarming cell triggers a census; it is never a finding. A registered multiplicity margin stopped a re-open at 5.2× against a 5× bar (4% over). "A correction that never changes an answer is decoration" |
| Pre-register the gate, falsifier, branch order and a "neither" branch (S §6.1 row 2) | §56, §38, §47, §72, §40, §77, §54 | Branch order chosen with the numbers on screen "is how a void quietly becomes whichever verdict the author preferred". A registered branch was **already refuted** by data in hand when it was written, and partitioning did not catch it. A revised bar (≥3× → ≥1.7×) had four protections and was **still withdrawn**: the fifth, a noise-floor check, put both the bar and its falsifier inside the noise. Reverting on a screen alone "would have destroyed a correct accept on noise". The confirmation census reproduced an accept made on 8 games, at 150 games | Put branch order in code, VOID first (`e2-gate.py`), and arm the gate on the completion marker so partial numbers are never seen. Guard on what the arm **contains**, not on what the outcome does: a ±10% guard voided an arm whose quantity rose 2.27× **because the mechanism worked**. Write down beforehand what a pass licenses. **Verify the promotion**: the promoted edit reproduced the arm's three numbers. A win delivered by an unregistered mechanism (a unit mix already measured at −5.71 sd) means the edit misfired. A keep-if-≥0 rule needs a ratchet (§77): +0.16/map on 25 maps vs +0.067/map on 75 maps (2.4× smaller) is "a favourable draw exactly at its threshold" |
| Closed-directions ledger with closure kind and a re-open condition (S §6.1 row 3; TA step 8) | §13, §23 (inline), §22, §71, §42, §26, §60, §63, §76, §49, §34 | §23: one re-open condition needed a 0.33 sd difference, "unresolvable at 300 games", and "had sat there for days looking actionable". §26: a condition written at iteration 9 was satisfiable long before anyone checked it, and "fired the moment someone looked". §42: the lineage's own accept moved a closed floor from 1.2 to 6.7 blocked turns per fire | Use the kinds, not a bare "closed": oracle-ceilinged, feasibility, refuted-on-value, structurally unavailable, blocked, and **UNEVIDENCED** ("not refuted; unevidenced, which is worse, because I priced and built on them"). Keep "not refuted and not pursued" separate. Strike spent conditions in the same edit. A re-open is legitimate only when it "depends on something that did not exist when the closure was written". Give each condition a **magnitude clause** (one that fired held 0.8 units of real slack). A closure's scope widens every time it is cited (§60). Sweep set-aside notes on the API-sweep schedule. "A ledger entry that proposes its own repair is the highest-value thing in a ledger and the easiest to walk past" |
| Record the measurement, not the explanation (S §6.1) | §52, §44, §63, §14 | The coordinator recorded a lineage's **interpretation** "the third time in one session" (§44), not twice. "Early-credit starvation" was refuted at −49 of 1,391 units and −0.12 structures. "A heavy tail is what an absorbing state looks like" was killed by share 1.33× vs volume 8.00×. "The constraint is density" did not survive. §14: a recorded cost was overstated **2.3× to 21×**, and "no tool in the repo produces those numbers at all" | Test for any figure: **name the tool that produced it**; without one it is not a measurement and nothing may be registered on it. "A quotable line is the most likely thing in a report to be an explanation rather than an observation." When two of your own numbers disagree, trace them. A 900× conflict reconciled exactly as a funnel (691 → 79 → 4). A 5.5× conflict was a summary against a draw (mean 38.8, median 18, sd 1.7× the mean; the log's figure was game 5 of 21) |
| Tools that refuse the error (S lesson 23; §17) | §25, §17 (inline) | The same lineage hit `diff \| head && echo IDENTICAL` and `check-pointers.sh \| tail -2 && commit` in one day. The second time, the check printed FAIL, the commit ran anyway, and a broken pointer landed in the repo. Backticks in a double-quoted `-m` were executed. A malformed `-gt` argument made `roster-stale.sh` print "OK: the roster is current enough to trust". A check came back 606 of 606 clean on a code path that `break`s before the flag could be appended | Gate on the tool's own exit status or `set -o pipefail`. Write commit messages with a quoted heredoc. Ship `SELFTEST=1`. "A self-test proves the branch is REACHABLE; only a real defect proves the DETECTOR works." Bound every derived quantity: a 184% utilisation exposed a cooldown divisor that was 10× wrong. §17: scope-check every guard. alice's ratchet fires only when bot source is in the commit, and N was derived from the instrument's resolution |
| Frozen roster and benchmark on every accept (S §6.1; C16) | §40, §30, §45 | The roster was four accepts stale, and the live iteration 43 **lost to iteration 39 by −7 net swept**. "An entire session had been spent probing and optimising from a baseline that had already regressed" (the `roster-stale.sh` header) | A saturated rung is **censored, not blind**: it absorbs a small regression and catches a large one. A roster of your own snapshots measures tuning. Add rungs you can **lose** to: carol forked her strongest bot with deliberately coupled edits and landed at **40.5%**. An earlier archetype failed at 97.5% "because it attacked with the wrong unit type" and was "then left alone for seventy iterations". Choose rungs against the hypothesis, not the scoreboard |
| The mirror screens and the external field decides (S lessons 1, 7) | §46 | Self-play read **+4** and the external instrument read **−16**. Treating the screen as blind would have shipped a −3.83 sd regression | Self-play was "not blind, it was **optimistic**". External instruments need **more** games, not fewer (the 2% vs 44% seed survival above) |
| Keep positive near-misses and stack them (TA step 8; S §6.2) | §27, §84 | Three levers had oracle prices of +12, +7 and +4 against a +26 bar. Two edited **the same target-selection routine**, so they were "portions of that axis's single ceiling rather than quantities that add". The two distinct axes anti-correlated at −0.48 (n=8): "the stack's honest value was dominated by its best single member". A jointly-necessary pair measured **1.94× against a ≥5× bar**, because its two resources were anti-correlated in time (rank correlation −0.496; 0.0% of 244 frames clear). Another pair was mutually destructive: joint affordability went from 21.1% to 0.2% | **Before any stack arm, read the diff:** members that edit one function are not addends. Measure the joint before building a pair. A rewrite is the right *instrument* for a jointly-necessary pair, and the file required "a rival is observably running the pair" first |
| Rewrite only with kill criteria (S lesson 25; C11) | §45, §84 | A lineage with 16 iterations and 0 accepts had in fact moved **5.3% → 20.7% → 24.7%** on the absolute instrument (maps swept on it fell 68 → 52 → 48 of 75). Thirteen accepts summed to **+10 net at 1.89 sd**, against the +12 required of one accept. The other lineage's rewrite was "rejected at −5.71 sd and still paid" | Register in advance what would make a rewrite the indicated experiment ("ceiling is the design" vs "ceiling is the game"). A failure that never reached its dose (2.22× of an intended 5×) counts toward **neither** branch. Separate CLOSURE ("an implementation failed") from CEILING ("no implementation can succeed"). Stage the rewrite so that execution failure and premise failure are separable at every stage. Report the registered outcome **before** diagnosing it. The handoff survey must list "true facts a context-free reader will MISREAD" (an 81% idle rate is an information ceiling, not headroom). carol's question cost 8 probe games, with no screen and no census |
| Trace replays and tally how games are won (S lessons 3, 11) | §82, §6, §36, §85 | Hand reading had covered **two maps**. In the neglected regime, 92–100% of the loss channel was a mechanism never countered, and 0–3% was the one countered. That explained a −3.83 sd reject | "Ask which games you have opened, not which games you have scored", and keep the list. §6: with both sides played, a 1–1 map split adds exactly zero to the margin (wins − losses = 2 × (swept − swept against)). The split set had the cleanest mechanism (p = 0.0012) "applied to the regime that cannot move her outcome". The maps lost **from both sides** carry the whole margin. §85: check whether the opponent shows the same pattern with the signs swapped; if so it is the scoreboard. §36: plot the predictor past round R |
| Unused-API sweep on a schedule (S lesson 22) | §16 | "unused did not mean overlooked; it meant the primitive does not do what I hoped": the jar's capacity number made a design break-even. Four sweeps reported the attack call as "used", which it was, constantly, but **never aimed at** the class of object the master variable counts | Read the deciding number from the source before building. Also sweep **targets**: "what does this bot never do TO the thing it cares most about?" Check call sites and arguments, not the call list |
| Census contrasts and cuts (S lesson 9; P1 contrast census) | §19, §57, §58, §59, §75 | A map-size deficit read −28.7 against one lineage and +0.85 against the other, so "the six iterations aimed at the pooled reading were aimed at nothing". A whole-game −4% stock gap was −9%, −16% and −18% in the deciding windows | Cross every cut with the opponent (the 2×2). Compare unequal-length games at a **common round** (an arm that won at r709 against a control that ran to 1393; another comparison widened from 2.7:1 to ~10:1 in the deciding window). A subgroup must be pre-outcome and pass two tests: it contains the deficit (11.38 vs 15.17) and it does not predict the outcome (4/7 vs 5/12). Before naming a limiter, measure both arrival and service time (L = λW; service ≈ 74 rounds). The limiter can change by phase |
| Resume point and context economy (S §6.1; §18) | §18 (inline), §45 | Sessions that recovered cleanly had described in-flight work "by run-id and gate rather than by intention" | The rewrite that worked "began from a committed survey rather than from the context that generated it" |

### 2. Lessons with a direct 2023 analogue (all inference)

- **Per-HQ stockpiles are not a pool (§57).** carol divided pooled income across six structures, but "the engine
  requires one structure to pay from its own reserve". Measured properly: the currency cleared its gate in 58–75% of
  rounds, the per-structure stock in 27–54%, and both together in 8.6–25%. A mean across units said 8.6% where the
  site-level probe said 1.4%.
  - 2023: stockpiles are per HQ [rules]. Any "the team can afford N launchers" figure from summed HQ stock overstates
    what one HQ can build. Measure at the building HQ.
- **"Being where the work is means being where the infrastructure is not" (§35).** Seeing unworked ground puts a unit
  at the frontier; the channel needs a path back through owned territory. The joint was far below the product.
  - 2023: shared-array writes need r² 9 of an own HQ, r² 20 of an own amplifier, or r² 4 of an own anchored island.
    The carriers and launchers that sight new wells, islands or enemies are at the frontier, out of write range.
  - Measure "saw it AND could write it" jointly before sizing any comms design.
- **A negative payload inverts under loss (§48).** At 34.7% delivery, "no reports arriving is indistinguishable from
  reports not getting through".
  - 2023: the array persists, but writes are range-gated, so the failure mode is staleness. Absence claims ("island X
    unclaimed", "no enemy at well Y") decay into confident falsehoods.
  - Prefer positive reports carrying a round stamp.
- **Information acquired and discarded (§37, §76).**
  - 77.7% of "blind" rounds still had unclaimed targets (median 7). The bot kept no memory of them while sighting 67%
    over a game.
  - Per-actor memory accumulated only 4.7–5.6 witnesses against a capacity of 32, "because the actors die first".
  - 2023: wells and islands seen by carriers that die are lost unless they reach the array or an HQ. The file's prescription was "a memory that outlives one actor".
- **Cooldown semantics (§25).** A 184% utilisation came from a divisor that was 10× wrong, because "a cooldown
  decrements per turn rather than gating a whole turn".
  - 2023 uses the same semantics: a per-turn decrement of 10, launcher move cooldown 20, carrier floor(5+3m/8), and
    clouds +20%.
  - Bound every utilisation against its physical ceiling.
- **Forbidden turns in a rate's denominator (§24).** Once turns where the engine forbade movement were removed, real
  obstruction was 9.2–23.5% of turns. 27–50% of stuck turns had **no adjacent wall** (mean 1.2–1.6 walls of 8), so the
  blockers were robots.
  - 2023: compute stuck rates only over turns with movement cooldown < 10.
  - Separate walls from robots: carrier queues at wells are the likely robot case.
- **Endurance vs decision (§1).** Run the class test first: "the unit died" is an endurance limit, and no targeting
  rule can repair it; "the unit was alive and elsewhere" is a decision.
  - "Every mechanism in that session which skipped the class test failed."
  - Run this class test before any carrier-loss or launcher-loss fix.
- **Exact zeros from map files (§1).** A zero from a sample (0 of 1,640) was promoted to a theorem using the engine's
  map files: no mutually visible pair on any of 75 maps.
  - The failure case is recorded with it: three days earlier the same argument was wrong for a unit standing **near**
    a target rather than **on** it, one tile apart.
  - 2023: the 103 jar maps allow the same arithmetic (HQ-to-well, HQ-to-island, vision overlap). Record the
    near/on case with each theorem.
- **Default 2023 tooling retains only losses (§1, §32, §6).**
  - `tools/gauntlet.sh` line 93 is `[ "$res" = win ] && [ "${KEEP_ALL:-0}" != 1 ] && rm -f "$REPLAY"`. Census rows
    (`CENSUS=1`) are written for every game before deletion.
  - bc25's version of this bit alice: "all 39 retained games were ones the arm won".
  - Remedies: `KEEP_ALL=1`; invert roles (play the opponent as BOT); or use the opponent's trajectory inside a
    retained replay as a **controlled winner** (same map, rounds and policies).
  - Fingerprint re-runs on **winner and round count**. 2023 `compare.py` already joins on outcome and round count.
- **A partial run is a prefix (§6).** `gauntlet.sh` line 50 writes cells in a fixed opponent → map → side order, so an
  interim tally estimates the first k cells, not a random k. Do not compare a partial arm with a complete one.
- **Splits on 2023.** With `SEED_MODE=random` (the default), the two sides of a map get different seeds, so a 1–1
  split may reflect the seed rather than the side. The bc25 identity (splits add zero to the margin) still holds
  arithmetically. The "side decided it" reading needs equal seeds per side.
- **Per-time rates across unequal lengths (§19).** 2023 games end by anchor win at any round or at r2000. Compare
  carrier deliveries, launcher builds and similar at a common round.
- **A surplus has a time profile (§52, §58).** 1,502 in the deciding early band vs 56,706 late. A proportional lever
  acts on the base present in the deciding window: 4.17 vs 9.00 structures, so 16 points of share were 0.7
  structures.
  - 2023: measure Mn and Ad stock, and HQ and island counts, in r1–100 (S lesson 10), not as game means.
- **An instrument fix that moves your result toward what you wanted deserves suspicion (§48).** A manipulation control
  (a signal that cannot work) scored 21.8% because of an east-biased, compass-ordered tie-break. Fixing it moved the
  candidate from 1.16× to 0.95× of null.
  - 2023: this is S C5 (side bias): direction-iteration order will leak into any "random" null.

### 3. Tools named or implied, with reuse verdicts

| tool (bc25) | what it does (read) | verdict for 2023 |
|---|---|---|
| alice `tools/e2-gate.py` (121 lines) | Applies a registered gate. It checks VOID first (\|net_null\| ≥ BAR); refuses a verdict without the `GAUNTLET-COMPLETE` marker; takes BAR as an argument so a screen and a census share one branch order; announces a missing null arm loudly; prints a per-map table even on reject | **Adapt (P0 with the paired gate).** Port the control flow onto 2023's `results.csv`. Defects: lines 93, 95 and 99 hard-code "4" in the printed text while the comparison uses BAR (display only). `net = oppw - maps` assumes every map was played from both sides. The 2023 runner writes no completion marker, so use the presence of `summary.txt` |
| alice `tools/roster-stale.sh` (80 lines) | Exits 1 when the last frozen-roster measurement is more than N accepts behind; `SELFTEST=1`; validates its argument (its first draft's silent `-gt` failure) | **Adapt (P1, with the frozen roster).** Snapshot glob `src/g_iterN`, plus the 2023 history file |
| alice `tools/check-pointers.sh` (19 lines) | Under `set -uo pipefail`, exits 1 on any dead LEARNINGS → archive pointer | **Steal the pattern** if 2023 keeps a short index with pointers into a grep-only log. Low priority |
| alice `tools/sweep-tally.sh` (12 lines) | Interim tally that prints both columns when BOT is the zero arm | **Skip.** Interim tallies are prefixes (§6), and 2023 `summarize.py` covers the rest |
| alice `tools/unconfirmed.sh` | Ratchet: exit 3 once N=3 unconfirmed keeps are pending. "N=3 is derived, not chosen" from a +12 census bar and a +5 change. Called with no pipe | **Adapt only if** TA step 8's kept near-misses can sit in HEAD unconfirmed. This agrees with bc25-tools-code |
| `tools/map-subset.py` (refuses a pooled rate without its pair rates) | named in §19 | **Skip,** as the earlier reports said; it is useful only with three or more lineages |
| §78 same-game counterfactual counter (no file named) | Counts events the new rule permits against those the old rule would have permitted, on identical turns | **Build** as an indicator counter (`note\|new=..,old=..`) for every threshold change. It is exact at any n |

2023 shell check (grep, read-only): no `| head … &&` or `| tail … &&` gate pattern in `tools/*.sh`. The string
`pipefail` appears in 11 of 14 `.sh` files; `vm.sh`, `vm-tail.sh` and the sourced `lib.sh` lack it.

### 4. Pitfalls not yet in the prior reports

- **A threshold imported from another population can already be met by the control (§62).** The control ran 42.6% and
  27.39 against ">25%" and ">14", so the test could only fail. "Identity maps are chosen for reproducibility, not for
  containing the deficit." State targets relative to the control on the same maps.
- **A gate on a negative over a rare object fires almost always (§48).** "None visible to this actor" fired on 87% of
  turns, reproducing the ungated arm that had already lost. The global proxy correlated +0.01. Closure kind: "the gate
  that would make it safe is not computable from the actor's observables". The re-open needs a new observable with
  |r| ≥ 0.6.
- **A self-consuming gate (§35).** When a mechanism spends the resource its own gate reads, static reachability
  overstates by construction: 21× static vs 2.22× realised. Compute the equilibrium. carol's was income-determined,
  `min(income_A/cost_A, income_B/cost_B)`; at the crossing point, rebalancing a `min()` cannot raise it.
- **An explanation has a sign (§61).** A stated cause predicted a fall where the measurement rose 2.27×. "One step from
  building a compensator on top of it."
- **Same-signed failures across independent implementations refute the shared premise (§51).** Two different
  mechanisms each moved the target quantity thirty-fold, and each lost −4 inside the target regime.
- **A licence is not evidence (§51).** Permission to rewrite led one lineage to price the cheap route, and that
  overturned its "no open axis" claim.
- **A link-by-link chain does not establish the end (§80).** Three arms were +2, +4 and +4 on large maps and −2, −14
  and −8 on small and mid maps. "28 of 50 screen games were the wrong regime." A +61% sizing was re-read as a
  large-map number.
- **The dedup key is the estimand (§26).** Keying by position collapsed repeats ("we claimed 10 to their 8"); recounted,
  the opponent repeated 43 times to 0.
  - A 59% "built" difference was 90% churn; the standing stock differed by 4%.
  - One bot's own composition ran 12.8%, 35.0% and 42.6% against three opponents.
  - A p90 distance of 6.3 was habit, not capability: the median was 8.89 and the maximum 25.24.
- **Where a temporary filter applies is a design decision (§56).** Filtering banned targets at record time scored −4
  against the null; at navigation time, +2.
- **Uncertain sign plus a large absolute cost: run three games (§20).** An ungated behaviour cost 4,296 units per
  1,000 rounds and scaled 8.8× with map area.
- **Verify a causal link you think is an identity (§63).** Spending was cut 78% and the stock did not move (147.0 vs
  147.4).
- **A threshold on a ceiling inverts the meaning of a pass (§31).** Clearing 16,000 by 1.4% is evidence the direction
  cannot pay.
- **Do not fit a threshold to a reporting bucket (§53).** A map-size bucket edge "was a line she had drawn to
  summarise results, not a feature of the game".

### 5. What this changes for 2023 (proposals; my judgement)

1. **TA step 8 ("positive near-misses … stacked").** Add §27's diff test (members that edit the same function are not
   addends) and §84's joint measurement before any stack arm. If near-misses stay in HEAD, add a §77 ratchet.
2. **Split the P0 identity control into two checks.**
   - (a) Byte-identical code on equal seeds gives 0 discordant pairs: this proves determinism and build identity.
   - (b) A seed-varied null arm sharing the arm's map draw gives the noise floor; evaluate it VOID-first.
   - bc25 shows that (a) alone "actively licenses the broken check" (§78). Its 2% vs 44% seed survival says field
     pairs need more games than mirror pairs. Measure that fraction on 2023 before sizing band tests.
3. **Any outcome-conditioned replay study needs `KEEP_ALL=1`.** Otherwise use census rows or role inversion. Default
   runs keep only losses.
4. **Comms design.** Before choosing a comms layout, measure the frontier-vs-write-range joint (§35) and prefer
   positive, round-stamped payloads (§48).
5. **On S §6.2's "a dozen core rules".** The evidence supports that verdict: most entries are refinements of an incident
   from a single session ("third instance in one day", §35; "three misses of 5–10× in one day", §35). By cost
   evidence, the rules that paid most are:
   - VOID-first gate code with a shared-draw null (§54, §56);
   - joint funnels at the call site (§35);
   - "name the tool" (§14);
   - the closure kinds plus a magnitude clause (§13, §63);
   - the stale-roster refusal (§40);
   - the "am I behind" comparative (§32);
   - the 2×2 with the opponent (§19);
   - "which games have I opened" (§82);
   - the same-function stack test (§27);
   - `pipefail` and `SELFTEST` (§25).

## Gap read: /home/terryvanbelle/projects/vibe/2020/tools/puppet.py

**Scope.** I read these in full: `2020/tools/puppet.py` (938 lines), `src/puppet/Puppet.java`, `src/puppet/Script.java`,
`tools/puppet.sh`, `tools/puppet/RawEvents.java`, `test/puppet/PuppetTest.java` and `golden.properties`,
`src/pup_g_iter13/RobotPlayer.java` (the shim), and `tools/{lib.sh, run-dev.sh, paired.sh, pair-batch.sh}`. Of
`tools/test_tools.py` I read only the names of the puppet checks.

Documents came only from the filtered room `readroom-no2023/bc20/`:
- DESIGN.md §"Puppet" (lines 241-297);
- TRAINING_LOG.md lines 4164-4177, 4199, 4269-4320, 4347-4354 and 4425;
- PROMPTS.md 59-67;
- BENCHMARK.md 19-25, CLAUDE.md 15-25 and TRAINING_ALGORITHM.md 20, 125 and 150-155;
- tools/README.md.

To check the `bc.testing.*` route I read the 2023 engine source (`reference/battlecode23`, where `git describe` gives
`3.0.15`, commit af42086 of 2023-02-05), the bytes of the staged jar, and 2023 project code (`tools/lib.sh`,
`tools/get-engine.sh`, `src/bot/G.java` and the header of `tools/replaydump/ReplayDump.java`). I read no competitor
code and no 2023 document. "Inference" marks my own reasoning.

### 1. Pipeline (what the unread bodies do)

1. **`puppet.sh raw|extract`.** `RawEvents.java` turns a `.bc20` into one text line per flatbuffer record:
   `H B F R S M A D W U X T K C E`. It gunzips the file if needed and refuses a file holding more than one match. Its
   documented rule: "The order ACROSS vectors of a round is meaningless ... only the in-vector order is the order in
   which the engine appended them." Messages are read raw from vtable offsets 36-42 because "the engine writes an int
   vector of char codes ... where the schema declares [string], so the generated accessor returns garbage".
2. **`puppet.py extract`.** It parses those lines into a `Game`, runs `Extraction` for side P (by default the side
   whose package is *not* one of ours), keys every P robot, encodes the result and writes
   `build/puppets/<Ppkg>__<map>__<A|B>-<sha8>.properties`. That file is a Java properties file with exactly two keys,
   `bc.testing.pup.idx` and `bc.testing.pup.dat`, whose values are `\uXXXX` escapes. Two provenance comment lines
   record the replay path and sha1, run, map, seed, side, P and O packages, rounds, winner, `engine/VERSION`, the
   sha12 of RawEvents.java and puppet.py, and the extraction time. Every structural assumption is a hard `fail()`
   that names the round, for example "r%d: #%d made %d own moves" or "%d dirt changes, %d consumed".
3. **Runtime.** The engine loads the fixture as its `-c` file. Each robot of a `pup_<base>` team runs
   `Puppet.play(rc)`, which reads the fixture through `System.getProperty`. The shim is 10 lines:
   `if (puppet.Puppet.play(rc)) <base>.MapState.setHome(puppet.Puppet.home); <base>.RobotPlayer.run(rc);`.
4. **`puppet.sh check`.** It plays the recorded O package against the puppet on the recorded map, side and seed.
   Then `puppet.py diff` compares the recording with the new replay round by round.
5. **`puppet.sh pair` and `pair-batch.sh`.** Both sides are scripted to the cutoff and then handed over at once.
   **`puppet.sh cells`** feeds `paired.sh`.

### 2. Replay rules from the bodies

**Keying (`Extraction.keys`, `Script.find`).**
- **The key.**
  - The HQ is `(HQ, 1, tile)`.
  - A built robot is `(type, spawn round + 1, spawn tile)`: its first turn comes the round after it is built.
  - A newborn that a drone holds at its first turn is keyed by its first release alive. That covers one picked in
    its spawn round, or picked at spawn+1 by an *older* drone (lower exec index). One that is never released is
    skipped with a note.
  - A robot dead at or before its spawn round never took a turn and gets no key. If it had a script, that is a
    `fail`.
  - A key collision is a `fail`.
- **Every P robot that takes a turn is keyed, events or not.** DESIGN: "an unkeyed vaporator fell back on a
  neighbour's record within d2 8 and 20 rounds and re-submitted its messages (2026-09-27, Constriction r1432)".
- **The lookup.** `find(idx, type, r0, x, y)` binary-searches the index (sorted by `type<<12|keyRound`) for the last
  record with a key ≤ (type, r0). It then scans back while `keyRound >= r0 - WINDOW` (WINDOW = 20):
  - an exact tile wins (the largest keyRound first);
  - otherwise the nearest tile within `NEAR_D2 = 8` (ties go to the largest keyRound);
  - otherwise there is no match: the robot prints `@pup miss`, idles until the cutoff, then hands over.
  - PuppetTest pins the edges: 20 rounds late is found; 21 is a miss; a key round after the first turn is a miss;
    d2 8 is found; d2 18 is a miss; the type must match.
  - A robot also skips TX records older than its first turn, which guards a fallback match.
- **Targets are tiles, never ids.** puppet.py's header says "ids shift as soon as either side builds
  differently". `diff` also keys robots by (team, type, spawn round, spawn tile).

**Extraction (`Extraction.round`).** For each round it does five things:
1. It pairs spawns with SPAWN actions by id and checks that the builder is adjacent.
2. It walks pick and drop sequences per target in action order.
3. It classifies each move entry as own move, carried, picked up or dropped. More than one own move, or a
   non-adjacent one, is a fail.
4. It walks the dirt and soup change vectors in action order, so that DIG, DEPOSIT and MINE get their tiles.
5. It attributes deaths. The explanations are narrow: shot; dropped into water; buried (with the `(-1, DEPOSIT, -1)`
   spill just before the deposit); or drowned by the end-of-round flood (only in the *suffix* of `diedIDs`, on a tile
   flooded that round). Any other P death becomes a `DIE` op ("`move()` into water kills before the move is
   recorded").

Events are sorted by (round, phase): PLACE first, then the act, then DIE.

**Runtime step rules (`Puppet.step` and `attempt`).**
- **Free events first.** These cost no cooldown:
  - PLACE updates the recorded position;
  - a MOVE whose target is already reached is consumed;
  - DROP while not holding is consumed, and PICK while holding is consumed;
  - DIE calls `disintegrate()`.
- **Then at most one act**, and only when the robot is ready and the act is due (recorded round ≤ now).
- **Out of reach.** The robot steps toward the recorded position: greedy, trying the direction, then left, then
  right. It never enters a flooded tile unless it flies or the recorded MOVE has `arg = 1` (it died there).
- **Fallbacks.**
  - BUILD tries the recorded direction. After one counted failure it tries the nearest other adjacent tile.
  - BUILD that lacks soup returns 0 ("waiting", not counted as a failure).
  - PICK takes the unit of the recorded type at the tile, else the nearest match.
  - SHOOT takes the drone at the tile, else the nearest enemy drone.
- **Give-up.**
  - An act is dropped after 3 failed ready turns (8 for MOVE), printing `@pup drop OP rN lagK`.
  - A BUILD more than 20 rounds late is dropped, "so that every robot the puppet builds finds its own record". The
    give-up is tied to `Script.WINDOW`.
- **Logging.** It records `maxLag`. `GameActionException` is caught and printed as `@pup exc`.

**Messages (2020-only machinery).**
- P's messages are the ones our `Comms.auth` (ported as `auth()`) does not claim for O, accepting signatures from
  round r or r-1. They are assigned to free P robots so that the minted blocks reproduce "order included".
- `ChainModel` re-implements the engine's `Random(seed)` (re-created at every spawn and drawn once per submission)
  and the `PriorityQueue` order (fee descending, then `other.id - this.id` as an int, then text). It beam-searches
  where each message sits among the round's spawns (beam 48, budget 200,000 steps).
- If no placement reproduces the block, it falls back to the "tail carriers" and restarts after the next round that
  empties the queue.
- Each robot's message capacity is `floor((limit - 600 - 700) / 270)`: HQ 69, miner, landscaper and drone 32, net
  gun 21, other buildings 13.
- Builders that submitted before building get the PRE flag (`0x8000`).

**Handover.**
- Handover happens at the first turn at or after the cutoff.
- A drone with a DROP ahead finishes the ferry first (at most 50 rounds). It then drops its own cargo on a dry tile,
  because "the base's drone drowns whatever it holds". If it still holds cargo at cutoff+100 it prints
  `@pup hocargo`.
- It prints `@pup ho <maxLag> <dropped>`. A robot whose first turn is at or after the cutoff is the base's from birth.
- **Cutoff precedence:** `bc.testing.pup.<A|B>.cutoff`, then `bc.testing.pup.cutoff`, then 99999. The cutoff is
  "never in the fixture (a `-c` file overrides `-D` for the same key)". PuppetTest and test_tools both assert this.

**Misconfiguration resigns.** `@pup nofixture`, or `@pup wrongfixture` (version, side, map width or height, or the HQ
tile for the HQ), calls `rc.resign()`: "a misconfigured puppet must not look like a game". `lib.sh run_game` also
refuses any `pup_` team without an existing `GAME_CONFIG`, because "the engine only prints a stack trace for a missing
-c file".

**`check` eligibility gates (puppet.sh).** All of these must hold:
- the recorded replay still exists;
- the O package is in `src/` and is not `bot` ("which changes; snapshot it");
- the run directory has a `YYYYMMDD-HHMMSS` stamp;
- `src/O` has no uncommitted changes;
- the last commit time of `src/O` is at or before the run stamp;
- `engine/VERSION` equals the fixture's.

`--as PKG` lets identical code under another package name play (`diff -q` after sed-renaming the package). The
play is one game through `run-dev.sh` with `GAME_TIMEOUT=5400` and robot stdout on. It waits at most 20 minutes for
another engine on the machine.

**`diff` (the `check` judge).**
- It records the first divergence round for each category: P and O positions, acts, soup, spawns and deaths; O
  bytecodes (per robot); the minted block (1 = order only, 2 = content). It also prints "ids equal to".
- **Cause priority:**
  1. at or after the cutoff gives exit 1;
  2. a P-side difference gives "puppet: <act> by <type>@(x,y) rec rN", exit 1;
  3. a block difference gives exit 1;
  4. an O-bytecode difference without an acts difference gives "O read something different", exit 1;
  5. anything else gives `UNEXPLAINED`, exit 2. This drops to 1 if the block differed earlier.
- A different result with no cause is exit 2. A tool error is exit 3.
- It counts `@pup` tags from the log: drop, miss, txlate, txdrop, ho, maxlag, nofixture, wrongfixture.
- DESIGN: "O-side bytecodes per robot are the most sensitive detector."
- TRAINING_ALGORITHM: before a fixture serves, `check` "must exit 0 or 1 with no divergence before the cutoff other
  than `block`".

**Pair mode (PROMPTS 66: "once you hit the cutoff, you have to hand off both sides simultaneously").**
- `pair` extracts P's fixture and then O's (`--side`). It merges them, rewriting the keys to
  `bc.testing.pup.<A|B>.*`, and makes the shims `pup_<cand>` and `pup_<base>` by running sed over the
  `pup_g_iter13` template.
- `PCUT` keeps P scripted to a later round (PROMPTS 67). `FIXTURE_ONLY=1` prints `fixture side map seed` and plays
  nothing.
- `pair-batch.sh` runs every cell against every build in parallel on the VM. It sets `-Dbc.testing.pup.cutoff=1`
  (our side is live from r1, since a robot whose first turn is ≥ cutoff plays the base from birth) and
  `-Dbc.testing.pup.<P>.cutoff=<pcut>`. Each game gets its own `DEV_OUT` class tree, deleted afterwards, and a
  3000 s timeout.

**`cells` and `paired.sh`.**
- `cells FIXTURE CUTOFF...` prints `map <O side> seed <abs fixture> <cutoff>`. The BOT side is O, the side we play.
- In `paired.sh`, fields 4-5 set `GAME_CONFIG` and `GAME_OPTS=-Dbc.testing.pup.cutoff=<cut>`, and the candidate and
  control games both face `OPP=pup_<base>`.
- `paired.sh` deletes the replays of concordant pairs.

### 3. Evidence (quoted from TRAINING_LOG / DESIGN)

- **Fidelity proof.** "the Constriction loss to cormackikkert (seed 318083382) replayed with g_iter13 on side B is
  IDENTICAL to the recording through r2427 in every category -- positions, acts, soup, spawns, deaths, robot ids,
  block order -- with no `@pup` lines; TheHighGround and WateredDown fixtures place every message exactly. Handover at
  r1500: 137 robots hand over to g_iter13 cleanly ...; g_iter13 then won the game it lost in the recording (r3054)."
- **Reviews.** "Two adversarial reviews found seven defects (message-model restart, send-before-build, flood/burial
  death attribution, own-cargo handover, per-message bytecode cost 270, build give-up at the 20-round find window,
  fixture uploads); all fixed and the proof re-run."
- **Bytecode budget** (Constriction r1-2427): "600-1100 bytecodes on the first turn, a mean of 30-160 per turn by
  type, about 270 per message carried ... The worst turn was a drone carrying 33 messages (before the cap), 9288 of
  10000."
- **Pair mode on the real wave.** "Both sides replayed exactly to r2090". With control g_iter13: "6 dropped script
  acts ..., 0 rescue shots ...; lost r3006". With candidate r1: "14 `@shoot kind=1` rescues ... (4,275 dropped script
  acts: the rescues change the board) ...; lost r3014". The mechanism fired but did not change the result. The
  ladder later read r1s17 as level: "1788 +- 39 against g_iter13's 1789 +- 34".
- **Other diagnostic uses.**
  - The NoU pair: "control g_iter13 reproduces the recording (2370 vs 2383 at r3000)". The pre-registered target
    had been "2383 vs 2413 at r3000". This is near, not exact, after an open-loop window.
  - r4 ring rate: "1.24 vs 0.99".
  - pair-batch over six mvpatel2000 losses: landscapers at r1000, g_iter13 -> r5, "SoupOnTheSide 0 -> 6",
    "DoesNotExist 0 -> 17", "Constriction 12 -> 8". r5's first ladder block read "1750 +- 46 ... against g_iter13
    1772 +- 35", with the verdict waiting on two more blocks.
- **Puppet league: INVALID.** "g_iter12 vs g_iter13 36-1 discordant, r1s17 7-0 -- g_iter13 replays its own losses
  exactly, and any build that plays differently knocks the open-loop script off its recording, so the puppet weakens
  with the build's divergence: it rewards difference, not strength."
- **Cost signal.** PROMPTS 62, the owner during the build: "It seems like the replay-puppet workflow has been going on
  for a while. Is it blocked/starved, or is it doing a lot more than I think it's doing?" Inference: most of that
  effort went into the message and chain model, which 2023 does not need (§5).

### 4. The `bc.testing.*` route in 2023: VERIFIED from source (bc20.md marked it inference)

- `engine/src/main/battlecode/instrumenter/inject/System.java`, the static initialiser (around lines 71-78):
  `Config global = Config.getGlobalConfig(); for (String key : global.getKeys()) if (key.startsWith("bc.testing"))
  props.put(key, global.get(key));`. The sandboxed `System.getProperty(key)` and `getProperty(key, def)` (lines
  136-141) are served from those `props`.
- `server/Config.java`:
  - the constructor copies every JVM property starting with `bc.` (and `drw.`);
  - `addArgs` then handles `-c <file>`: if the file is not `-`, `addFile` runs `Properties.load`. So **a `-c` file
    overrides a `-D` key of the same name**, which bears out DESIGN's rule that the cutoff never goes in the fixture;
  - a missing `-c` file only `printStackTrace()`s;
  - with no `-c` at all it silently tries `bc.conf`;
  - `getKeys()` = `properties.keySet()`, which holds explicitly set keys and leaves out the defaults. `bc.testing.*`
    keys are always set explicitly, so they are included.
- **The staged jar matches.** `engine/battlecode23-3.0.15.jar`'s `battlecode_version` reads `3.0.15`. The bytes of
  `battlecode/instrumenter/inject/System.class` contain `bc.testing` and `getGlobalConfig` (`grep -a`).
- **The 2023 project already uses the route.**
  - `src/bot/G.java:45`: `DEBUG = "true".equals(System.getProperty("bc.testing.debug"));`.
  - `tools/run-dev.sh` passes `-Dbc.testing.debug=true` under `DEBUG=1`.
  - Gap: `tools/lib.sh` hard-codes `-c=-`, so a `GAME_CONFIG` hook (2020's `-c="${GAME_CONFIG:--}"`) has to be added.
- **The seed.** `tools/get-engine.sh` patches `LiveMap.getSeed()` to `Integer.getInteger("bc.game.seed", seed)`.
  - That reads JVM properties only, so the seed must stay a `-D` flag and cannot go in the `-c` fixture.
  - `GameMapIO` serialises `gameMap.getSeed()` (source line 264), so our replays record the effective seed. That is
    what the fixture's `seed=` provenance needs.
  - Inference: a replay from an unpatched engine records the map's own seed.
- **Turn order.** `ObjectInfo.eachDynamicBodyByExecOrder` takes a snapshot of `dynamicBodyExecOrder.toArray()` at
  the start of the update. So a robot spawned in round r first acts in r+1: the 2020 key rule `(type, r+1, ·)`
  carries over.
- **Robot log prefix.** It is unchanged: `"[" + team + ":" + type + "#" + id + "@" + round + "] "`
  (`RoboPrintStream.getHeader`). So `pup_log`'s regex and `pup_counts`' grep carry over.

### 5. What a 2023 port keeps, drops, and must add

**Drops.** The 2023 replay `Round` table has no message or shared-array field. Its fields are team Ad/Mn/Ex
changes, moved ids and locations, spawned bodies, died ids, action ids, actions and targets, island ownership,
wells, indicators and bytecodes. That confirms bc20.md's inference: `auth`, `ours_msg`, `ChainModel`,
`assign_messages`, `allocate*`, `fill`, `TX_CAP`, the TX records, PRE, and `Puppet.tx` all go. In `puppet.py` that is
roughly 260 of 938 lines (my count: lines 106-125, 133-257, 466-485 and 487-579). The 2020 mechanics go too: pick and
drop, dirt, flood, burial, cows and drones.

- Side effect (inference): extraction no longer needs one side to be ours. The 2020 `extract` failed with
  "neither side is ours: messages cannot be attributed". `check` still needs O to be our unchanged package.

**Keeps.**
- the `Game`/`Round` raw-line parser pattern;
- the key and `find` scheme (WINDOW and NEAR_D2);
- the fixture encoding (`encode`/`decode`/`fixture_text`/`read_fixture`, 16-bit chars, sorted index with a sentinel);
- the `diff` structure and cause priority, minus `block`, plus island ownership and per-team Ad/Mn/Ex;
- `cells`;
- the `Puppet.play` skeleton (fixture lookup, resign on misconfiguration, per-team cutoff, miss→idle, drop
  thresholds, `@pup` tags, handover);
- all of `puppet.sh`'s gates.

Field limits: key round < 4096 (2023 runs at most 2000 rounds); x and y < 64 (maps are at most 60×60); type < 16 (six
2023 types).

**Must add.** All of this is inference from the 2023 engine source.
1. **Positions are recorded once per robot per round, after currents.** `GameWorld.processEndOfRound` runs
   `applyCurrents()` (`CURRENT_STRENGTH = 1`, so every round), then `addMoved(id, loc)` for *every* robot. In the
   jar, `GameWorld.class` contains `addMoved` and `RobotControllerImpl.class` does not.
   - Within-turn steps are invisible: an empty carrier moves twice a turn on a cooldown of `floor(5+3m/8)` = 5.
   - So is the current's push. The current-applying code skips robots that are blocked (the `notMoving` set).
   - So 2020's "one own adjacent move" invariant and its move classifier cannot be ported. Script MOVE should
     become "end-of-turn tile before the current". Extraction must undo `applyCurrents` by simulating it over all
     robots' positions; it has them all.
   - **Key tile.** A robot spawned in r can be pushed at the end of r. So the key tile must be its position at the
     start of r+1, which is the recorded end-of-r position, not the `spawnedBodies` tile.
2. **Move and act are separate cooldowns**, so a launcher can attack and move in the same turn. The record does not
   give their order. The runtime should try the act both before and after moving. Attack targets are victim ids
   (or `-(x+y*W)-1` on a miss), and the victim's tile at the time of the attack is ambiguous between its start and
   end positions. Use 2020's SHOOT-style fallback: the robot at the tile, else the nearest enemy of the recorded
   type within r² 16.
3. **HQs build several units per turn** (the brief: action cooldown 2 against a decrement of 10). The rule "at most
   one act when ready" has to become "every due BUILD that the cooldown allows".
4. **1-4 HQs.** The index header holds one HQ tile (`hqx<<6|hqy`), and `wrongfixture` checks one HQ. Both must
   handle a list, and the shim should prime the base with every HQ, not `MapState.setHome(home)`.
5. **New ops and amounts.**
   - Collect and transfer take a tile target, with amounts from the per-robot `CHANGE_ADAMANTIUM`/`MANA`/`ELIXIR`
     deltas. The 4-bit `arg` cannot hold 40 kg, so the event needs a third char.
   - `BUILD_ANCHOR` (accel), `PICK_UP_ANCHOR` (`hqId*2+accel`, negative = return; map the id to the HQ tile),
     `PLACE_ANCHOR` (island id; the carrier must stand on the island), `THROW_ATTACK`, `DESTABILIZE` and `BOOST`
     (tile).
   - Deaths can be explained from `CHANGE_HEALTH`, which tracks hp exactly, so the guessed 2020 explanations go.
     `DIE_EXCEPTION` is recorded.
6. **The raw reader.** Build it on `2023/tools/replaydump/ReplayDump.java` instead of porting RawEvents. Its header
   already documents every 2023 event encoding listed above. Adding a raw-lines mode costs less than a new reader.
7. **Handover state.**
   - The puppet side writes nothing to the shared array, so a base that expects HQ-written round-1 state starts
     blind. That is the 2023 counterpart of 2020's "no builder miner, a fresh miner burst from the HQ, build counters
     at zero".
   - Two mitigations: (a) keep our side live from r1 (the pair-batch pattern), and (b) have the shim run the base's
     round-1 initialisation for the scripted side at handover.

### 6. Pitfalls (each learned in 2020)

1. **Never use open-loop puppets as a strength league.** The evidence is 36-1 and 7-0 discordant (§3). They are for
   diagnostics only: an exact replay to a cutoff, or control against candidate over a short window.
2. **A pair handover after r2 loses birth-order roles.** "a pair handover after r2 rebuilds our robots mid-life and
   loses birth-order roles (the builder miner), so a pair that needs our opening must hand our side over at r1."
3. **Key every robot that takes a turn.** Otherwise it takes a neighbour's record (the vaporator incident above).
4. **Keep the cutoff out of the fixture** (`-c` beats `-D`). Pass it as `-D`, per team if needed.
5. **Fail closed.**
   - Refuse a `pup_` team without its fixture before Java starts.
   - Resign when the fixture is wrong.
   - Make the extractor abort with the round named whenever an invariant breaks, instead of guessing.
6. **A fixture is only valid against the exact O code and engine it was recorded with.** Enforce this with the
   git-time and VERSION gates, not by trust.
7. **Generated flatbuffer accessors can lie.** 2020's message vectors came back as "garbage". Check accessors against
   raw reads.
8. **Strings under the instrumenter.** Script.java: "charAt only (indexOf and split are O(n) under the instrumenter)".
   Re-measure first-turn parse cost on 2023's 10,000-bytecode units. In 2020 it was 600-1100.
9. **Disk.** "129 of them filled the VM's 20 GB" (pair-batch class trees, 2026-09-29). Delete each game's private
   class tree.
10. **Keep puppet games out of grades.** `scrim-record.py` refuses `pup_` labels and opponents ("puppet games never
    enter games.csv"). `puppet.sh play` refuses any opponent that is not one of our packages ("a puppet plays only our
    own bots"). `extract` refuses replays under `bc20-benchmarks`. Governance (PROMPTS 64): replaying a recorded game
    counts as reviewing it, but "in an actual contest there would be no mechanism to play a benchmark opponent using
    the puppet-replay".
11. **The open-loop drift budget is small.** With the candidate live, the r1 run dropped 4,275 script acts. Read any
    result after the first P divergence as approximate. `diff --cutoff` labels it "after cutoff".

### 7. Reuse verdicts

| Item | Verdict for 2023 | Why |
|---|---|---|
| `puppet.py` parse / keys / encode / decode / fixture / diff / cells / CLI | **adapt (major)** | Most of the skeleton carries. `Extraction.round` is rewritten for 2023 events (currents, multi-move, anchors). |
| `puppet.py` ChainModel, auth, TX allocation | **drop** | 2023 replays record no shared array, and it is team-private. |
| `src/puppet/Script.java` | **steal with edits** | Drop TX; widen events for amounts; list several HQs in the header. |
| `src/puppet/Puppet.java` | **adapt** | Keep the play loop and resign/miss/drop/handover. Rewrite `attempt()` for 2023 ops and allow move+act and multi-BUILD per turn. |
| `tools/puppet/RawEvents.java` | **replace** | Add a raw mode to `2023/tools/replaydump/ReplayDump.java`. |
| `tools/puppet.sh` (raw, extract, play, check gates, diff, cells, pair, FIXTURE_ONLY) | **steal with edits** | Changes: `.bc23`, the benchmarks path, the template shim name. |
| `tools/pair-batch.sh` (global cutoff 1 + per-side PCUT, private class trees) | **steal** | |
| `paired.sh` fields 4-5 (fixture, cutoff) | **steal** (bc20.md already steals paired.sh) | |
| `lib.sh` `GAME_CONFIG` / `-c` hook and `pup_` refusal | **steal** | 2023 `lib.sh` hard-codes `-c=-`. |
| `PuppetTest.java` + `golden.properties` + test_tools' byte-for-byte regeneration | **steal (pattern)** | One golden file that Python writes and Java decodes pins a cross-language contract. |
| `@pup` log tags + `pup_counts` | **steal** | The 2023 log prefix is unchanged. |

**Net.** I keep bc20.md's "adapt (major)" and SYNTHESIS's P2 priority. The blocker bc20.md flagged, the property
route, is cleared (§4).

Inference: a 2023 port is likely smaller than the 2020 build, because the chain model is gone, but it adds current
inversion and multi-move/act turns.

Open question (not checked here): do 2023's own rules allow seeded reruns against benchmark bots on a chosen map and
side? If they do, a closed-loop rerun may cover some of what the puppet was built for. The puppet would stay unique
for "exact to round N, then our candidate". If they do not, the puppet remains the only compliant way to re-run a
field loss from a chosen round.
