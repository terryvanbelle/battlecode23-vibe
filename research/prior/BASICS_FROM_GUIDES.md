# Basics from the cross-year guides, mapped onto Battlecode 2023

Slice: **basics-guides**. Written 2026-10-07 by a research-reader subagent for the 2023 practice project.

Sources: the five filtered topic guides plus ADVICE.md and PROMPTS.md under
`/home/terryvanbelle/projects/vibe/reference/readroom-no2023/advice/`; the engine's public API and constants
(javap of `2023/engine/battlecode23-3.0.15.jar`); the header comments of the project's own tools in `2023/tools/`.
I read no 2023 strategy source. Each "2023 mapping" below is my own reasoning from the task's rules summary and
the engine API. Where it goes beyond what the engine confirms, it says **(inference)** or **VERIFY**.

Verdict tags used in §5: **CORE** = belongs in the foundation bot; **ADAPT** = use with the stated changes once
the foundation works; **LATER** = worth a measured experiment after the foundation; **SKIP** = does not apply under
the 2023 rules.

---

## 1. Scope

### 1.1 Read in full (filtered copies)

| File | Lines | Bytes | Lines in the original (from `git log --stat`) | Removed by the 2023 filter |
|---|---|---|---|---|
| ECONOMY.md | 383 | 25,122 | 452 | 69 (15%) |
| NAVIGATION.md | 372 | 24,147 | 480 | 108 (23%) |
| EXPLORATION.md | 299 | 20,657 | 382 | 83 (22%) |
| SYMMETRY.md | 265 | 14,878 | 312 | 47 (15%) |
| COMBAT.md | 392 | 26,122 | 508 | 116 (23%) |
| ADVICE.md | 1,282 | 86,078 | about 1,284 (1,271 at creation, +7/−3, +9) | about 2 |
| PROMPTS.md | 38 | 3,046 | n/a | n/a |

The original line counts come from commit metadata only (`git log --stat` in `reference/battlecode-vibe`,
commits 5405036 and 3a8433f). I did not open the original files.

**Where the filter removed blocks.** Numbering gaps show where 2023-tagged blocks were cut: ECONOMY §1 item 4;
NAVIGATION §1 items 5 and 7, §3c and §4a; EXPLORATION §1 item 2; SYMMETRY §1 items 1 and 3; COMBAT §1 items 1
and 3. All five "Sources" lists are empty. I did not try to reconstruct any of them. A grep finds no remaining
"2023" string in the filtered files.

### 1.2 Code

`reference/battlecode-vibe` holds only these seven Markdown files (`find` lists 7 files), so this slice has no
code to read. To ground the 2023 mapping I read engine API, not strategy:

- `javap` of `RobotController`, `GameConstants`, `RobotType`, `Anchor`, `MapInfo`, `WellInfo` and `world.Well`;
- the legality assertions in `world.RobotControllerImpl` for collect, transfer, attack, act-location and
  shared-array writes (disassembly saved to my scratchpad).

I read only the header comments of `2023/tools/*`, to inventory what already exists.

### 1.3 Skipped

- The original .md files in every repo.
- The sibling reports in `2023/research/prior/`.
- All benchmark or opponent source.
- Anything about 2023 strategy.

### 1.4 Nature of the evidence

- The five guides are second-hand distillations of 2009–2026 post-mortems, tagged `[year team]`.
- ADVICE.md distils five practice seasons. PROMPTS.md prompt 1 names the battlecode20, 21, 22, 25 and 26
  repositories.
- Almost no item carries a p-value. Numbers below are quoted exactly as written, and most come from one team.
- ADVICE asks to "treat every idea as a hypothesis to measure rather than a rule to obey". This report does the
  same.

---

## 2. What worked (evidence as written, with effect size)

### Economy
- **Read the win condition first.** One team won a year "on the tiebreak metric (total unit health) by buying
  the best HP per cost: 'Surprisingly, almost no one copied'" [2019 smite]. Effect: a season win.
  ADVICE §1: "One season's founding thesis was refuted by a single tally: nearly all games were decided by a
  term the bot was not optimising."
- **The opening.**
  - Copying the top teams' opening queue made one finalist's rank jump "instantly" [2021 Stone Tao].
  - An untuned opening sank a sprint finalist to 9th [2018 smite].
  - ADVICE §11: "the whole-game gap was often decided before round fifty and no aggregate showed it".
- **Central site assignment.** When gatherers picked the nearest free site, the loser of each race "wasted ~25
  turns". The spawner assigning the exact site at birth fixed it [2019 smite, 1st]. The 2018 winner used Hungarian
  matching with 5 slots of decreasing value (1.0…0.2), and greedy matching above 30 workers.
- **Converting surplus.** Om Nom "spent 13,000 banked in under 60 rounds and went from 8 units to 23"; confused got
  "a 70%+ win rate against its previous bot" [2025]. It was spotted by watching another team's replay.
- **Carry cap matched to the movement penalty.** One team "gained a lot by raising its cap when the penalty turned
  out small" [2026]. No number is given.
- **Global all-in.** "~100% of income goes to the offensive for ~100 rounds" [2020 smite]. No effect size.
- **Production mechanisms.**
  - A score-sorted purchase queue with "save for the top item" [2018 Orbitary Graph, 1st].
  - Composition-driven thresholds gave a "cleaner build order" than the winner's [2020 The High Ground].
- **First-turn bytecode.** Fixing overruns on a unit's first turn "was a substantial win" [2025 Om Nom].
- **Compute as economy (older years).** A 69-bytecode hibernation loop "roughly doubled the sustainable army"
  [2012]. Spending 5000 bytecode per unit instead of ~0 "cut a sustainable army from 40 to 27" [2013].
- **Practice seasons (ADVICE §11).**
  - "Repairs of defects and removals of binding caps transferred to the field in every season; reallocations
    between unit types mostly did not."
  - "Three of one season's largest wins were such gates."
  - "two measurements replaced seven failed guesses".
  - For a rate limit, "Every ceiling raise in one season failed; halving the period was accepted."

### Navigation
- **Build bug navigation early and keep it.** Winners built bug navigation in week 1 and kept it all season
  [2020 Java Best Waifu, 1st]. The 2025 winner: "Every year I toy with BFS and come back to bugnav".
- **Path length decides first contact.** "A path two rounds shorter wins the first engagement" [2012].
- **Optimal Bug** costs "about 1.5k bytecode per turn" [2025 Om Nom]. The 2026 runner-up and a 2026 finalist said
  they would adopt it.
- **Threat overlay.** With reference-counted turret ranges, "raiders circled the enemy base just outside turret
  range" [2020 JBW, 1st].
- **Direction walks** "saved over 2000 bytecode per turn" [2020 JBW].
- **Row-bitmask BFS.** Reachability over the remembered map costs "about 300 bytecode" [2026 GST]. GST's
  bit-shift flood fill also stopped micro from trying to move "through" walls.
- **One-line guards (ADVICE §7).**
  - "The largest single gain of one season was one line: a target re-pick that reset the stall counter every
    turn".
  - "Two short guards against degenerate movement outweighed the rest of one season's bot in ablation."

### Exploration
- **Random targets are enough.** "Random map location, re-picked when within distance² 5" matched every fancier
  scheme a 2025 top-3 team tried [Om Nom].
- **Battlefront broadcast.** Broadcasting the battlefront "cut idle exploration massively" [2025 Kragle].
- **Hub over relay.** Switching from unit-to-unit relay to a hub "worked much better" [2021 naalit].
- **Coordinates mod 128** "improved my bot efficiency 2 fold in comms" [2021 wstan2001].
- **O(1) index.** A grid indexed by spacing guarantees replaced "a 144-entry linear search that ran out of
  bytecode under message load" [2025 SPAARK].
- **Clustering sightings.** Online 3-means clustering of enemy sightings cured "distress-call oscillation"
  [2022 5 Musketeers].
- **Edge-hugging scouts** became a deliberate flanking strategy [2021 Stone Tao].
- **Fingerprinting.** Identifying the opponent from its message formats "won the 2012 final" [2012 fun gamers].

### Symmetry
- **Practice-repo measurements.**
  - A blind rotational guess "was wrong on 4 of 10 maps, and against one opponent the guess was wrong in 28% of
    games".
  - "Observed symmetry was settled by round 1 in about half of games and by round 30 in about three quarters".
- **Row bitmasks** run "about 9x faster than per-tile checks, about 1k bytecode for an exhaustive check"
  [2025 Om Nom].
- **Rally targets from symmetry.** Late improvements built on rally and rush targets from turn 1 "took one
  first-year team from the top 20 into the top 15" [2021 naalit].
- **Centre first.** A rush unit that settled symmetry at the centre first was slower when the default guess was
  right but "more consistent overall" [2020 The High Ground, 2025 confused].

### Combat
- **Lanchester force-ratio table** [2013 devs]:

  | Unit advantage | Better kill ratio |
  |---|---|
  | 5% more | ~20% |
  | 10% more | ~40% |
  | 15% more | ~80% |
  | ~33% more | lose nobody |

- **The micro kernel.** The 9-move scoring kernel "is the micro every strong team copies" (ADVICE §13).
  Unrolled and object-free, it "came out about 2x cheaper and needed no bytecode checks" [2025 Om Nom].
- **Copying better micro.**
  - "Rob XSquare's micro and turn it against him" took "~20 minutes and gained +100 rating" [2024, second-hand].
  - ADVICE §18: "three accepted micro fixes in one season were direct ports".
  - Copying the opponent's offence "paid immediately and was one season's only step outside the error bars".
- **Other measured results.**
  - Decoys "escaped chasers ~85% of the time" [2016].
  - Saturating a defence took "about 10 attackers per defensive turret in one year" [2020].
  - A swarm moving to "most allies, fewest enemies" produced a concave that "beat [an equal army] decisively"
    [2013].
  - "Just spawn more units when in danger" was enough against every rush bot one team met [2026 Lorem Ipsum].
- **Standing defences (ADVICE §15).** "Three variants that waited for evidence of a rush all lost more." The
  conditional counter "was neutral in the mirror and turned the losses to swarm opponents".

### Method (ADVICE)
- **Diagnostic before gate.** The "one logged diagnostic before any gate" rule "caught three inert candidates in
  one season and many more later".
- **Audit at a plateau.** A correctness audit "ended a plateau that dozens of tactical experiments had not".
- **Re-opening rejections.** "about one in three reopens paid".
- **Paired controls.** One unpaired gate read "thirty-four to forty-six with seventy-four of eighty pairs
  identical and the rest in the candidate's favour". Pairing would have shown the change helping.

---

## 3. What did not work, and closed directions

### Economy
- **Coordination-heavy plans.** "Every time I'd implement a sophisticated strategy that requires a lot of
  coordination it would always flop" [2020 JBW, 1st]. Why: such plans are fragile under deaths and comms delay.
- **Reserves and windows.**
  - A floating-bank reserve "actually makes us build fewer units", so it was dropped [2017 Bruteforcer].
  - Round-window build rules overproduce [2025 Om Nom].
  - Interleaving research with units was worse than doing them in sequence [2013].
  - A fixed "keep ~16 alive" paid more per traded unit on small maps [2026 food].
- **Emergency responses.**
  - Emergency defence "overproduced late game, fed units into enemy lines" [2019 smite].
  - An "extended rush" stalemate froze one team's economy [2020 HG].
  - One team panicked into melee units against a ranged unit they could never reach [2019 Double J].
- **Healing and exploits.**
  - "Heal lowest-HP first" left some units waiting "over 1000 rounds" [2022].
  - Bots tuned to an exploit crashed after the patch [2021 Stone Tao].
- **Timing and banking.**
  - Stockpiling under decay for 500 turns gained only ~30% [2013].
  - Switching to the tiebreak too late lost two finals games [2019].
- **Practice seasons (ADVICE).**
  - "Every attempt to buy units the economy could not feed failed."
  - A census that counted dead units as alive shut production off "forever at round five hundred".
  - Rebuilding around the opponents' unit mix "loses every game" (§26).

### Navigation
- **Skipping pathing.** Skipping real pathfinding "because there are no walls" cost map control, neutral captures
  and attack timing, and "went unnoticed for 1.5 weeks" [2021 Stone Tao].
- **Global BFS.** The 2017 winner "disabled its BFS and shipped distBug": "A stale global path can be worse than
  fresh local bug."
- **Bug on moving targets.** Bug "regressed for moving ones" [practice-repo measurement]. Resetting bug whenever
  the target "changes" loops in mazes [2026 Lorem Ipsum, 2025 Om Nom].
- **Other failures.**
  - A cross-product m-line test "failed at varying distances" [2026 nfgehrs].
  - A carrier picking up stuck units "was not a substitute for pathfinding" [2020 confused].
- **Practice seasons (ADVICE §7).**
  - A cost-aware pathfinder was "reverted unrun once the navigation statistics showed movement was not the gap".
  - "a shared stuck counter that fires on benign congestion near the base regresses everything".
  - "Absolute stickiness lost heavily; per-tick re-optimisation ping-pongs."
  - A hidden off-facing move penalty "sat unnoticed for a hundred and fifty iterations and cost a quarter of all
    movement".

### Exploration and communication
- **Relays and silence.**
  - Unit-to-unit relay was "a lot of complication" [2021 naalit].
  - Turning off chatty messages "broke half the bot" [2026 Lorem Ipsum].
  - Multi-turn protocols between moving units fail as units drift out of range [2016].
- **Bad target schemes.** Quadrant-centre targets "spread units too thinly on big walled maps" [2025 SPAARK].
  "'Move away from home' exploration walked units into the enemy" (ADVICE §7).
- **Broadcasting to everyone (ADVICE §9).** Pooled sightings "caused stampedes onto one tile and a distress call
  scattered defenders". In one season mobile units wrote a channel only the base could write: "every call threw
  and aborted the turn".
- **Coverage is a marker, not a lever.** "Coverage predicted wins early in one season and more scouting did not
  win games" (§26).
- **Probing for a constant** "cost one season's rush three hundred rounds of arrival time" (§8).

### Symmetry
- A partial row check accepted the wrong symmetry [2019 Codelympians].
- An over-eager "symmetry explore" "sent single units into 1-vs-5 fights" [2026 TSPAARK].
- ADVICE §8: "Symmetry inference implemented and firing was still worth nothing in one season because no decision
  consumed the answer." Runtime classification can also mislead: "a base near one mirror axis reads as 'close'
  under the wrong symmetry".

### Combat
- **Trickling.** "Fighting one-by-one loses" [2014 schnitzel].
- **Rush strategies** that win sprint 1 "rarely survive to the finals" [2025, 2026].
- **Baitable retreat rules.** An opponent advancing one unit at a time "herded its whole army back to base"
  [2014 Darkpurple].
- **Wasted or mixed ideas.**
  - The 2016 winner's anti-turtle mode was never used in the tournament.
  - Kiting a neutral at the enemy did *not* work in 2026 [3Mice], though it won 2016.
  - Rewarding unseen tiles made one team hit its own base [2019 Double J].
- **Stale state.** Computing range from a stale pre-move object made melee units step in, "wait a turn to attack,
  and die" [2018 smite].
- **Practice seasons (ADVICE).**
  - "Leashes that halved deaths and mechanisms that raised damage both lost when they cost the thing that
    converts" (§13).
  - "Micro tweaks before the army can move together measured zero" (§12).
  - A "rally before reinforcing" rule "failed repeatedly" (§14).
  - "an internal rusher beat the incumbent and rated well below it on the field" (§27).

### Method (ADVICE)
- **Bad instruments.**
  - "Eight rejections in a row that were the instrument's fault" (§22).
  - "a zero-to-five read that ended eleven-to-five voided a gate".
  - "a stale sparring partner scores 95% when the truth is 62%" (§6).
  - A mirror win "by nineteen points" moved the ladder "by nothing" (§23).
- **Narrow testing.**
  - "a redesign that won two hand-picked maps by ten to fifteen percent lost the random-map gate three times".
  - "one lineage ran every stage-zero test on the single most outlying map of seventy-five".
  - "Sixteen iterations attacked the failure mode of the only two maps anyone had opened" (§17).
- **Hidden dependencies.** "A correct exploit tested as zero effect for twenty-seven iterations because the
  economy never produced the unit it applied to" (§24).
- **Structural work.**
  - A structural programme "ran thirty-six stages ... and was closed by the criterion written at stage thirty".
  - A rewrite that began from a copied design "rated far below the incumbent until the proven parts were
    restored" (§30).
  - Head-to-head margins "plus eight, plus six, and plus eight overall" do not chain (§27).

---

## 4. Method lessons

### 4.1 Training loop and gating (ADVICE Parts I and III)

**Instruments before the bot**, in this order:

1. a rules digest;
2. a headless runner (bare JVM, parallel, recording `(opponent, map, side, seed) -> winner, rounds, reason`);
3. a determinism check;
4. a replay-to-text reader;
5. an in-bot bytecode monitor;
6. snapshot, mirror and sparring tools;
7. unit tests;
8. standing charts.

Each one must be proven on a trivial bot, on a case whose answer is already known.

**The engine is the truth.**
- Read the legality assertion of every engine call you rely on, and tag each fact with where it was verified.
- I did this for collect, transfer, attack and write (§5.0). It overturned one assumption I would otherwise have
  made: deposits do *not* work at range 9.

**Statistics arithmetic.**
- "Separating fifty-five percent from fifty needs on the order of eight hundred games."
- "detecting a five-point difference at conventional power needs over a thousand a side".
- "a ninety-six-game block resolves roughly twenty points".
- "Most of what you can build is a two to eight point effect."

**Gate design.**
- Use SPRT against the incumbent on random maps and random sides, in capped batches.
- Pair every candidate game with an incumbent-versus-itself control on the same seed. Judge by discordant pairs
  with a sign test.
- Keep small positives provisionally as a stack and test the stack.
- Never read a running batch.
- Controls expire on every accept (the winner's curse).
- Use small maps for diagnostics, never for the gate.

**Pre-registration.**
- Write down the counter, gate, falsifier, selection rule and deciding instrument before the run. "Then do not
  move a bar after seeing a number, and never reinterpret a null."
- No gate starts until one logged diagnostic game shows the decision counter firing at roughly the claimed rate.

**Three instruments, never confused.**
- The mirror measures marginal value against your own build and is blind to shared weaknesses.
- Sparring archetypes reproduce one behaviour each. A partner must score "roughly a quarter to three quarters
  against the incumbent".
- The external ladder sees strength. It is rated by a batch Bradley-Terry fit on the Elo scale. "two hundred and
  forty games is the floor for a ladder verdict". A submission whose rating interval falls below the previous
  one's is withdrawn.

**Plateaus.**
- Audit correctness first, of both the bot and the instruments, through independent lenses.
- Then escalate in order: ablate, sweep the API, re-read the allowed games, re-read cross-year research, attempt a
  structural change, rewrite.
- After three rejects in one functional area, the next candidate comes from another area.
- Make at least one structural attempt in four.

**Records.**
- An append-only training log.
- A closed-directions ledger, with the kind of closure and a checkable re-open condition.
- "Record the measurement, not the explanation."
- Process rules live in tools that refuse; "a lesson written down is not a control".

**Agent operations.**
- Never idle.
- One session per working tree.
- "Delegate reading, not deciding ... Parallelise games, not agents."
- Read documents from extracted text, because a summarising fetch "invents quotes".

### 4.2 Owner (human) interventions and what they corrected

- **ADVICE §35.** "The most valuable interventions in five seasons were about method, not strategy: restate the
  objective as absolute strength, not beating a rival; play the frozen roster on every accept; copy an
  opponent's tactic and submit it; re-read the principles of other years when stuck; keep trying and rewrite if
  that is what it takes."
  - The owner also supplied "the risk appetite, the never-idle rule, the 'copy the tactic' rule and the 'if two
    instruments disagree, run the third' rule that the agent would not have found alone".
- **PROMPTS.md (this repo).**
  - Prompt 1 demanded year-agnostic content, weighting later seasons more, and forbade reading years not yet
    practised.
  - Prompt 3 corrected formatting (index rendering).
  - Prompt 4 asked that an update be made "much much more concise ... a small paragraph summary" with no references
    to the current year. Commit 11faab4 then added a single 9-line paragraph to ADVICE §29.
  - Prompt 5 commissioned the five topic guides "in the form of text and pseudocode".
  - The owner corrected concision and year-agnosticism, not strategy.

### 4.3 How the agent went wrong (as recorded in ADVICE)

- Two seasons blamed outcome shifts on bytecode without measuring; "both retractions came after the monitor was
  read".
- Result rows were mislabelled by the newest directory.
- Running batches were read as results.
- A stale sparring partner was trusted.
- Inert candidates were gated for hours.
- Probe maps were outliers.
- Reverts went wrong: "source control does not undo a committed change and a stash does nothing to committed
  code".
- A shell script was edited while a job ran it.
- Processes were killed by a pattern matching the agent's own command line.
- A fetch fabricated quotes.
- "the owner has to say 'not much is happening'".

### 4.4 Micro-specific method (COMBAT §13)

- Use test maps with pre-placed armies, then 3–5 purpose-built maps per behaviour.
- "Watch one unit", fix its stupidest decision, and disturb the good ones as little as possible.
- Copy better micro, then understand it.
- Keep imitation bots of top opponents as permanent sparring partners.

### 4.5 2023 mapping of method

The project already has most instruments: `tools/gauntlet.sh`, `sprt.py`, `elolib.py` (Bradley-Terry),
`compare.py`, `summarize.py`, `unit-tests.sh`, `deadcode.py`, and `replaydump/ReplayDump.java`. ReplayDump's
modes are summary, `--census`, `--metrics`, `--robot`, `--map-at`, `--logs`, `--bytecode`, `--navstats`,
`--events` and `--islands`.

- **Counters are ready to use.** ReplayDump's `--census` reads indicator strings of the form `note|k=v,k=v`. That
  is the ADVICE "decision counter" channel, and the foundation bot should emit it from its first commit.
- **Keep the counters short.** `GameConstants.INDICATOR_STRING_MAX_LENGTH = 64`, so use 1–3 character keys and
  only the counters the current candidate needs.

---

## 5. Bot architecture and the basics, mapped onto 2023

### 5.0 2023 facts used for the mapping

These come from the task's rules summary plus the engine jar, read with javap. Rows marked "engine" were read from
the 3.0.15 jar. The RobotType and Anchor values were decoded from the enum static initialisers in field-declaration
order, so the order should be checked once against the official specs.

| Unit | Ad | Mn | Ex | Action CD | Move CD | HP | Dmg | Action r² | Vision r² | Bytecode |
|---|---|---|---|---|---|---|---|---|---|---|
| HQ | – | – | – | 2 | – | 1 (indestructible) | 4 | 9 | 34 | 20000 |
| Carrier | 50 | 0 | 0 | 10 | floor(5+3m/8) | 150 | throw | 9 | 20 | 12500 |
| Launcher | 0 | 45 | 0 | 10 | 20 | 200 | 20 | 16 | 20 | 10000 |
| Destabilizer | 0 | 0 | 200 | 70 | 25 | 300 | 50 | 13 | 20 | 10000 |
| Booster | 0 | 0 | 150 | 140 | 25 | 400 | 0 | – | 20 | 10000 |
| Amplifier | 30 | 15 | 0 | – | 15 | 120 | 0 | – | 34 | 10000 |

| Fact | Value | Source |
|---|---|---|
| Map bounds | `getMapWidth()`/`getMapHeight()` exist, so edges and the centre are known on turn 0 | engine API |
| HQs; islands; wells | 1–4 HQs; 4–35 islands of at most 20 tiles each (`getIslandCount()` on turn 0); wells at most 4% of tiles; `MIN_NEAREST_AD_DISTANCE = 100` | GameConstants |
| Start bank / passive income | 200 Ad + 200 Mn (`INITIAL_*_AMOUNT`); +6 Ad +6 Mn per 5 rounds. Whether this is per HQ: **VERIFY** | GameConstants, rules |
| Cooldowns | A unit may act while cooldown < 10; −10 per turn | rules |
| Collect | Must be **adjacent** to the well (`isAdjacentTo`); amount ≤ well rate; adds the carrier's action cooldown (10), so **one collect per turn**. `Well.getRate()` is 3 if upgraded, else 1 (`WELL_STANDARD_RATE = 1`, `WELL_ACCELERATED_RATE = 3`). Confirm the per-turn yield in a logged game. | engine |
| Transfer | Must be **adjacent** to the target ("Robot needs to be adjacent to transfer."), not merely within r² 9 | engine |
| Well mutation | Depositing ≥1400 of a well's own type upgrades it (rate 3). Depositing ≥600 Ad into a Mn well converts it to an **Elixir** well (`Well.addAdamantium`). The Mn→Ad direction is presumed symmetric: **VERIFY** | engine |
| Attack | Needs action radius, an on-map target and a ready action. There is **no vision check**, so blind fire at a tile is legal. Carriers can attack only with inventory (weight > 0). The throw damage formula (`CARRIER_DAMAGE_FACTOR = 1.25`) is **VERIFY** | engine |
| Shared array | 64 words in [0, 65535]. A write throws unless `inRangeForAmplification` (HQ r² 9, amplifier r² 20, own island r² 4). An exception costs 500 bytecode (`EXCEPTION_BYTECODE_PENALTY`) | engine |
| Anchors | STANDARD: 80 Ad + 80 Mn, 250 HP. ACCELERATING: 300 Ex, 750 HP, −0.15 cooldown multiplier, 4 units affected. The enum also has `healingFrequency`/`healingAmount` fields; how anchors heal is **VERIFY** | engine (decoded) |
| Clouds; currents; multipliers | Cloud: vision r² 4, cooldown ×1.2. Current strength 1 tile. Booster −0.1/stack (max 3, r² 20, 10 turns). Destabilizer +0.1 (max 2, r² 15, 5 turns) | GameConstants |
| Tiles within r² | 2→9, 4→13, 9→29, 13→45, 16→49, 20→69, 34→109 (each count includes the centre tile) | computed |

**Consequences derived from these facts (inference):**

- **Carrier speed** is 10 / floor(5+3m/8) tiles per turn:

  | Load m | 0 | 13 | 14 | 26 | 40 (or carrying an anchor) |
  |---|---|---|---|---|---|
  | Tiles per turn | 2.0 | 1.11 | 1.0 | 0.71 | 0.5 |

  An empty carrier is the fastest unit and the only one that outruns a launcher. A loaded carrier or an anchor
  carrier moves at launcher pace.
- **Launchers** attack every turn but move once per 2 turns. Movement is their scarce cooldown, and stepping into
  range commits them for two turns. Amplifiers move twice every 3 turns.
- **HQ production rate is not the constraint.** With action cooldown 2, an HQ can build at cooldown 0, 2, 4, 6 and
  8, so up to 5 units per turn; currency limits it first. The real throughput limits are the **8 tiles adjacent to
  each HQ** (deposits) and the **8 tiles adjacent to each well** (collection).
- **HQs cannot die**, so there is no base kill. Macro targets are carriers, islands and well access.
- **Launcher vision (r² 20) exceeds launcher attack (r² 16).** The 20-tile annulus between them is where a launcher
  sees an enemy it cannot yet hit.

### 5.1 Architecture (ADVICE §4 and §5, guides)

- **Layering.** CORE.
  - `RobotPlayer` dispatches to `Hq`, `Carrier`, `Launcher` and `Amplifier`, with stubs for `Booster` and
    `Destabilizer`.
  - Utility classes: `Comms`, `MapMem` (row bitmasks), `Sym`, `Nav`, `Micro`, `Explore`, `Econ`, and `Dbg`
    (counters plus the overrun monitor).
  - One constants file, each constant with the measurement that set it.
- **Per-unit state machine.** Sense, determine state, execute, then state-invariant post-actions. CORE.
- **Goal memory with a return point.** A carrier remembers its well and its HQ. An anchor carrier remembers its
  island tile. A launcher remembers its rally point and, while fighting, its last enemy sighting. CORE.
- **Sense once per turn.** Call `senseNearbyRobots()` once and pass the result around. CORE.
- **Statics are per robot.** Team state lives only in the shared array. CORE. (Inference: the HQ is immortal, so
  its statics are the one reliable long-lived memory the team has. Use the HQ as the planner.)
- **Map latches computed once** at spawn or on round 1 (§5.2, item 3a). CORE.
- **Return whether an action actually happened**, and let handlers fall through on failure. ADVICE's worst bug
  class was "camp forever on an unreachable target". CORE.
- **Audit every tie-break on the day it is written.** ADVICE §5: identical code split "100/0" on a map because of a
  fixed compass order. 2023 maps can be reflections as well as rotations, so a fixed `Direction` iteration order
  favours one side. Break ties toward the target or by score, and run the mirror from both sides on every map.
  CORE.

### 5.2 Economy

#### Principles (ECONOMY §1)

1. **Find out what actually wins.** Sources: 2019 smite; 2017 E Doc Tablet; 2019 Wololo. CORE.
   - **2023:** The score term is islands. Anchors on 75% of islands win instantly. Otherwise the round-2000
     tiebreak keys run: islands held, then anchors placed in total, then elixir, mana, adamantium.
   - (Inference) Any Ad or Mn still banked near the end is worth less than one more anchor placed.
   - Read the ending reason of one starter game. The committed fixture `test/fixtures/example-mirror-maptestsmall.bc23`
     is a 2000-round examplefuncsplayer mirror, so games between weak bots end on the tiebreak.
2. **Know what counts as a resource.** Test from 2021 wololo: (a) having none is close to losing; (b) you can take
   it; (c) the opponent can block your access. ADAPT.
   - **2023:** Islands pass all three tests (occupation decays enemy anchors). Launchers and carriers pass all
     three. Cargo in transit passes (b), because a dead carrier loses it.
   - Banked HQ stock fails (b), so it is a constraint, not a resource.
   - Wells are infinite but access to them is contestable (c).
3. **The opening snowballs.** Compare the first 50 rounds of events side by side with the strongest opponent
   (`ReplayDump --metrics --every 1`). CORE as a method.
4. **Simulate the economy offline** [2013 devs]. CORE: an hour of Python.
   - Model one carrier cycle with d = Chebyshev distance from well to HQ, m = load, r = well rate:

     ```
     T(d, m) = d/2                        // out, empty: 2 tiles/turn
             + ceil(m / r)                // one collect per turn (engine: cooldown 10, amount <= rate)
             + d * floor(5 + 3m/8) / 10   // back, loaded
             + 1                          // deposit (adjacent to the HQ)
     income(d, m) = m / T(d, m)
     ```

   - Examples at d = 10 (inference, rates unverified):

     | Rate | m = 40 | m = 20 | m = 13 | m = 14 |
     |---|---|---|---|---|
     | r = 1 | ≈ 0.60/turn | ≈ 0.53/turn | ≈ 0.46/turn | – |
     | r = 3 | ≈ 1.0/turn | – | – | ≈ 0.67/turn |

     When collection dominates the cycle, full loads win.
   - A 50-Ad carrier pays back in roughly 80–90 turns at r = 1, and about 50 turns at r = 3.
   - The same model gives "army vs round" for 3–4 openings, and the value of upgrading a well (rate 1→3).
5. **Floating resources are not a lead.** ADAPT.
   - **2023:** If each HQ keeps its own stock (**VERIFY**), this is exactly Kragle's "ten structures each holding
     70": four HQs can each sit below an anchor's 80/80.
   - Fix: route deliveries to the HQ whose priority purchase is short. Consumers leave exactly what producers
     need.
6. **Spend continuously on what compounds; bank only for a known, near, high-yield purchase.** CORE.
   - **2023:** Carriers compound. Bank only for an anchor or a launcher batch.
7. **Production rate as the constraint.** **2023:** HQ rate is not binding (up to 5 builds per turn). The binding
   limits are income and deposit slots (inference). ADAPT.
8. **Rush, economy and turtle form a triangle.** ADAPT.
   - **2023:** HQs are invulnerable and deal 4 per round, so no rush can kill a base.
   - A "rush" means early launchers at enemy wells and the HQ perimeter, killing carriers.
   - "Economy" means carriers plus anchors. "Turtle" means launchers holding our own islands.
   - Choose per map from the latches below.
9. **Every action that costs a shared resource is an economic decision.** **2023:** Moves, attacks and messages
   are free, so this does not apply. SKIP.

#### Gathering (ECONOMY §2)

- **Centralise assignment** [2019 smite; Hungarian, 2018]. CORE.
  - The HQ sees wells within r² 34 on round 1 and assigns each new carrier at birth. Each well has up to 8
    adjacent slots, minus walls.
  - The handoff is the spawn position: the HQ builds the carrier on the spawn tile closest to the assigned well,
    and the newborn takes the nearest known well of the needed type. No comms are needed. A one-round order would
    be missed, because newborns act the round after they are built (ADVICE §9).

  ```
  hqAssign(type):                       // HQ statics persist: the HQ is immortal
      w = argmax over known wells of type: rate(w) / T(d(w), m*) * safety(w) / (1 + assigned[w]/slots(w))
      buildRobot(CARRIER, freeSpawnTileNearestTo(w)); assigned[w]++
  safety(w) = (dist(w, nearestEnemyHqCandidate) > dist(w, nearestOwnHq)) ? 1 : 0.5   // midline term, ECONOMY §2b
  ```

- **Deterministic shared enumeration** (5-bit cluster index) [2019 smite]. ADAPT. A well's slot index in the shared
  array is its canonical id.
- **Site scoring** [2015, 2016]. ADAPT.
  - The yield × safety ÷ distance form maps directly; use the formula above.
  - "Ring-search, relax threshold" does not apply, because wells are discrete.
  - Add `−100·occupied`: a well whose 8 tiles are full sends the carrier to the next well.
- **Depot placement.** SKIP. Nothing in 2023 can be built as a depot. Deliver to the nearest of up to 4 HQs.
- **Carry policy** [2026 food, Lorem Ipsum]. CORE.
  - Return at a cargo threshold chosen from the offline model (likely full).
  - Return early when a threat appears (§5.6).
  - "Ignore small piles" and "collect on the way back" do not apply.
- **Gatherer memory and ghost resources** [2020 smite]. ADAPT.
  - Wells never empty, so there are no ghosts.
  - Well *type* can change (conversion to Ex) and wells can upgrade. Re-sense on arrival, and broadcast upgraded
    wells (rate 3) as "richest site" [2015].
- **Regrowing resources** [2022]. SKIP. Wells do not deplete.
  - The denial analogue is to kill enemy carriers at enemy wells, located by mirroring our wells.
- **Taxi and transfer.** LATER, and only if carrier-to-carrier `transferResource` is legal (**VERIFY**). Compute
  its value against direct delivery first.
- **Upkeep payback.** SKIP. There is no upkeep.

#### Build orders (ECONOMY §3)

- **Score-sorted queue, save for the top item** [2018, 1st]. CORE: pick this one mechanism and keep it. The 2023
  version keeps two currencies:

  ```
  each HQ turn:
      items = [(score(t), costAd(t), costMn(t), t) for t in {CARRIER, LAUNCHER, AMPLIFIER, ANCHOR}] sorted by score desc
      for it in items:
          if it.score <= 0: break
          if affordable(it): build(it); continue        // HQ may build up to 5 per turn
          reserveAd += it.costAd; reserveMn += it.costMn   // save for it: block anything that needs that currency
      // scores diminish with count: e.g. 2 + 20/(10 + count[t]); counters to observed enemy types add a bonus
  ```

  An anchor blocks both currencies. A launcher blocks only Mn, so carriers (Ad) keep flowing while the HQ saves Mn.
- **Composition-driven thresholds** [2020 HG]: `threshold[t] = base[t]·f(actual/desired)`. ADAPT. This is an
  alternative to the queue; don't implement both.
- **Proportional rules** [2017]. ADAPT.
  - Split carriers between Ad and Mn wells in proportion to planned spending. Launchers cost 45 Mn, carriers 50
    Ad, anchors 80/80.
  - Grow soldiers sublinearly: `(income+1)^0.9 > launchers`.
- **Decide, save, build; no round windows** [2025 Om Nom]. CORE. This is what the queue already does.
- **Modulo cycle with overrides** [2016, 1st]. CORE as the first-day build order before the queue exists, for
  example {carrier, launcher, carrier, launcher} with "army below N → launcher".
- **Income target before attacking** [2021 Baby Ducks, 1st]. ADAPT.
  - Build carriers until a measured income target is met, then launchers.
  - Raise the target when guards sit idle (a defensive map).
- **Spending escalation and a "desperation index"** [2020 JBW]. LATER.
  - Count rounds in which an anchor was affordable but no safe unclaimed island was known.
  - Relax in stages to contested islands.
- **Tech when upkeep is saturated.** SKIP. 2023 has no research or upkeep.
- **Population targets scale with map size** [2026 food]. ADAPT. Scale the launcher target with map area and
  `islandCount`.
- **Per-map plan from cheap latches (§3a).** CORE.
  - The latches: map area W·H; number of our HQs; rush distance (Chebyshev distance from our nearest HQ to the
    nearest enemy-HQ candidate, worst case over live symmetries); `islandCount`; Ad and Mn wells visible from the
    HQ; wall fraction among the 109 tiles the HQ sees.
  - Start from the 2×2 table (small/open → launcher-first; large → carrier-first) as a hypothesis to measure.
- **"Lost early last game" feedback.** SKIP. Statics do not survive between games.
- **Counter-production from scouting** [2019]. ADAPT. If enemy launchers are seen near our wells, raise launcher
  priority.
  - Reading the enemy bank or queue through the API does not apply: RobotController exposes neither. SKIP.
  - "Time the counter to the opponent's spending" does not apply for the same reason. SKIP.
- **Rush response: time-boxed, capped, and able to engage the threat** [2019, 2020]. CORE.
  - Every emergency mode gets a round limit and a cap.
  - Every fighter is ranged, so "can it engage" reduces to "is it in range".
- **Global all-in switch** [2020 smite]. LATER.
  - A HALT bit in the array stops carrier production and sends all Mn to launchers for about 100 rounds, when
    enemy islands are weakly held.
- **Designated producer and fair rotation among several producers** [2019 smite; 2022 5 Musketeers]. ADAPT.
  - **2023:** With per-HQ stock, coordination is about *which HQ builds the next anchor* and where carriers
    deliver.
  - The commander HQ writes `anchorHq = i`. Other HQs keep building cheap units and tell carriers to deliver to
    HQ i.
  - Turn-order tokens: the first HQ to act each round resets the accumulators. HQs never die, so the commander can
    be fixed (inference).
- **Mobile or forward producers.** SKIP. HQs never move.

#### Expansion and territory (ECONOMY §4)

- **Develop only what you can defend all game** [2020 Bowl of Chowder]. CORE. Anchor own-side islands first, then
  contested ones. Use the symmetry midline.
- **Expansion pipeline** [2019]. ADAPT. Allow at most k anchors in transit, perhaps 2. Measure whether to race
  central islands first.
- **Escort the first expeditions** [2019 plzgoeasy]. CORE in phase P5. An anchor carrier moves at launcher pace
  (0.5 tiles per turn), so a carrier-plus-launchers convoy moves as one group (inference).
- **Lattices and packing.** SKIP. Nothing is buildable. The "leave a gap" lesson becomes "keep the HQ ring clear"
  (§5.3).
- **Denial.** LATER.
  - "Taint": occupy enemy islands to decay their anchors. This is a rule of the game.
  - "Bury a spawner" is impractical: an HQ has about 28 spawn tiles, except at walls or corners, and hits for 4
    per round.
- **Punish over-extension.** CORE in targeting. Enemy carriers at far wells and anchor carriers in transit are the
  over-extended assets.

#### Retreat and repair (ECONOMY §5)

- **Refill or replace.** ADAPT.
  - A launcher costs 45 Mn. Healing exists only through anchors (**VERIFY**).
  - Retreat a wounded launcher only when one of our anchored islands is close. Otherwise fight on.
- **Finish the kill before retreating** [2025]. CORE in micro.
- **Heal queues need starvation control.** LATER, only if island healing is used.

#### Conversions (ECONOMY §6)

- **Convert surplus into the scarce resource.** LATER. This is a high-value experiment.
  - Surplus Ad deposited into one of our wells upgrades it at 1400 (rate 3 for every carrier there).
  - 600 Ad into a Mn well makes an Ex well. Elixir is tiebreak key 3 and buys boosters and destabilizers.
  - Price both conversions with the offline model.
- **Dead units drop resources?** Probably not. **VERIFY**. ADAPT: a doomed carrier throws its cargo at the enemy
  (§5.6) rather than losing it.
- **Infer state from income.** ADAPT.
  - Each HQ sees its stock rise and the carriers adjacent to it. A per-ID "last deposit round" table in HQ statics
    gives a live carrier census with no comms.
  - `getRobotCount()` gives our exact total.

#### Endgame (ECONOMY §7)

- **Switch to tiebreak value in time** [2019]. CORE (cheap).
  - From `2000 − round`, carrier income and the travel time to the nearest unclaimed island, compute the last
    round at which an anchor can be built and placed.
  - From then on, Ad and Mn go only into anchors.
- **Points race** [2017]. CORE formula for anchor priority:

  ```
  need = ceil(0.75 * islandCount) - islandsHeld
  anchorsAffordableSoon = (bankAd + projAd)/80, (bankMn + projMn)/80 -> min
  if anchorsAffordableSoon >= need and paths to `need` free islands are safe: ALL-IN on anchors
  ```

- **Close the game when ahead.** CORE goal. Reaching 75% ends the game.

#### Compute (ECONOMY §8)

- Hibernation does not apply: 2023 does not refund unused bytecode as far as the given rules say. SKIP.
- "Never exceed the budget on a unit's first turn" applies. CORE.
- "A skipped turn in the economy loop is invisible" applies, so log overruns. CORE.

### 5.3 Navigation

#### Strategy (NAVIGATION §1)

- **Build navigation in week 1 and keep it.** CORE.
- **Match the algorithm to the terrain.**
  - **2023:** Walls are binary. Clouds are graded (cooldown ×1.2, blind). Currents are directed one-tile pushes at
    end of turn. All units are 1×1.
  - So use bug with a local BFS, plus cost terms for clouds and currents.
  - Unit footprint and "dig rather than path" do not apply. SKIP.

#### Movement primitives (§2)

`tryMoveToward(d)` tries d, d.left, d.right (and optionally the next pair), with the two sides ordered by which
ends closer to the target. It takes a pluggable `safe()` policy. CORE.

```
safe_carrier(loc) = dist2(loc, knownEnemyHq) > 9                       // HQ hits 4/round
                 && for each visible enemy launcher e: dist2(loc, e) > 26  // max r2 hittable after one enemy step (computed)
safe_launcher(loc) = dist2(loc, knownEnemyHq) > 9 || allIn
```

RobotInfo does not show enemy cooldowns, so assume the worst case: the enemy can step, then shoot.

- **Never move away from the target in direct mode; hand over to bug instead.** CORE.
- **Cheapest-step greedy** [2021]. ADAPT.
  - Step cost = 1 × cloud multiplier, plus a penalty if the tile's current pushes away from the target.
  - Use `MapInfo.getCooldownMultiplier(team)` and `getCurrentDirection()`.
- **Dig or clear.** SKIP. 2023 has no destructible terrain.
- **Handle the degenerate CENTER direction.** CORE.
- **"Don't let a cooldown make terrain look like a wall"** [2026 food]. CORE, and important in 2023.
  - Carriers move 2, 1 or 0.5 tiles per turn depending on load. Launchers move every other turn.
  - Check `isMovementReady()` before calling navigation at all.
  - A cooldown-blocked `canMove` must never advance bug's state or its stall counters.
  - Navigation is called once per move: up to twice per turn for an empty carrier.

#### Bug navigation (§3)

The core loop is CORE, as written by the 2014–15 winner:

```
state: mode {DIRECT,BUG}, wallSide, startDist2, rotationCount, lastDir
step(target):
  if mode==DIRECT: if tryDirect(target): return
                   mode=BUG; startDist2=dist2(here,target); rotationCount=0; wallSide=side whose first free rotation ends closer
  d = lastDir rotated twice toward wallSide
  for i in 0..7: if canMove(d) and safe(d): break; d = rotate away from wallSide; rotationCount += ±1
  if cell on wallSide is OFF_MAP: flip wallSide; restart BUG
  move(d); lastDir = d
  if (rotationCount<=0 or >=8) and dist2(here,target) <= startDist2: mode=DIRECT
```

- **Leave rules.**
  - Use "closer than the start" together with net rotation. CORE.
  - Bug 2 (m-line) and Dist-Bug are LATER.
  - "Patience": return to direct mode after N moves with no wall contact. CORE.
- **Currents** (inference; LATER experiment).
  - The end-of-turn push can move the unit off the wall it follows, which is the "state breaks" edge case.
  - In BUG mode, treat a current tile as a wall unless its push has a component toward the target.
  - Reset bug when a push displaced the unit.
- **Wall-side choice** (§3b).
  - The AWAY and AROUND modes of the same wall-follower are ADAPT: AWAY lets a carrier flee; AROUND lets a launcher
    orbit an island or patrol at a fixed radius from the HQ.
  - Tangent bug and path smoothing are LATER.
- **Failure-mode guards** (§3d). CORE.
  - Do not reset on a nearby target change: an anchor carrier picks **one** fixed island tile.
  - Use greedy plus an oscillation escape against moving targets (enemy launchers).
  - Keep a visited history for "circling a box with a tiny gap".

#### Local search (§4)

- **Vision Dijkstra with a progress-per-cost exit** [2021 Malott Fat Cats]. LATER.
  - It covers 69 tiles at r² 20, and runs only when at least 2500 bytecode remain. After a revisit, go greedy for
    4 turns.

  ```
  for tiles l_i in generated ring order: if onMap: p_i = cost(l_i); relax from processed neighbours
  choose tile maximising (initialDist - dist(l_i, target)) / v_i; move d_i
  ```

- **Row-bitmask BFS** (one `long` per row; width ≤ 60 fits in 64 bits). ADAPT.
  - Use it for reachability checks over remembered and mirrored terrain: "is this island or well reachable?"
  - Reported cost: "about 300 bytecode" [2026 GST].
- **Neighbour bitflags per tile and bucket queues.** LATER.
- **"Optimal Bug"** (about 1.5k bytecode per turn) [2025 Om Nom]. LATER, as the target state once plain bug is
  measured.
  - Advance a virtual bug target K steps inside vision, then bitmask-BFS back to it.
  - It cuts corners, steers around units and keeps bug's arrival guarantee.
- **BugBFS** [2026 GST]. LATER alternative.

#### Global and shared pathfinding (§5)

- **Base-computed BFS and per-cell direction fields** [2014]. SKIP as shared fields.
  - A 60×60 direction field needs about 10,800 bits; the whole array has 1,024.
  - ADAPT the idea instead: the HQ (20000 bytecode, immobile, idle after its builds) runs BFS over its own memory
    for its own decisions, such as rush distance and well reachability.
- **Distributed BFS and coarse shared maps through the array.** SKIP for the foundation, because the array is too
  small. A 15×15 grid of 4×4 chunks would cost 15 words for marginal value.
- **Flow fields; unified target-and-path search** [2018]. LATER, local only.
- **Node-capped A\*** [2019]; coarse swarm graphs. SKIP or LATER.
- **Breadcrumbs.** ADAPT for carriers.
  - Push locations on the way out and return along them. A breadcrumb trail "never gets stuck and tends to avoid
    enemies, but detours" [2024].
  - Cheap, and the out/back route repeats every cycle.

#### Costs and hazards (§6)

- **Enemy threat as soft walls** [2020 JBW, 1st]. CORE.
  - The enemy HQ (r² 9, 4 per round) is the only static turret. With at most 4 HQs, a distance check replaces the
    reference-count grid.
  - For carriers, it is a wall. For launchers, it is a cost, switched off for an all-in.
  - "Circle the enemy base just outside turret range" maps to holding r² 10–16 from an enemy HQ (LATER: spawn
    camping).
- **Movement that costs resources.** SKIP.
- **Retreat only onto acceptable terrain** [2022]. ADAPT.
  - Do not retreat into clouds (slow and blind) or onto currents that push toward the enemy.

#### Congestion (§7)

- **"Keep the spawn and deposit ring clear"**: a recurring, season-wrecking bug [2019 ×3]. CORE.
  - **2023:** The HQ spawns within r² 9 (about 28 tiles), and deposits need one of its 8 adjacent tiles.
  - No unit parks within r² 13 of our HQ.
  - A carrier deposits and leaves the same turn. When the HQ ring is full, it waits at distance 2, not adjacent.
  - The same rule applies to the 8 tiles around a well: a carrier finding a full well re-targets.
  - Counters: `bs` (HQ wanted to build but had no free tile), `dw` (deposit wait turns).
- **Movement order.** ADVICE §1 says to check the engine's turn order before relying on it. **VERIFY**. If units
  act in ID order, a stuck unit broadcasts or swaps by ID.
- **Ally repulsion and lanes at corners.** LATER.
- **Reserved zones.** CORE in implicit form: the HQ ring is computed from the HQ locations in the array.

#### Stuck detection and reachability (§8, §9)

- **A time budget per target**: `turns ≤ dist × turnsPerTile(type, load) + 20`, then switch target and blacklist
  it. CORE. This covers ADVICE's largest single gain. The counter must survive target flicker.
- **Position history** scaled to unit speed. ADAPT. A launcher normally covers only about 10 tiles in 20 turns.
- **Exhaust timer in combat.** CORE: no action for N turns means leave the fight.
- **Unreachable targets and split maps.** ADAPT. Use a bitmask flood fill over known plus mirrored terrain before
  committing an anchor run.
- **"Return paths can be easier."** SKIP in 2023. Deposits need adjacency, according to the engine, so getting
  "close enough" does not count.
- **`disintegrate()` exists.** LATER: recycle a carrier stuck for 50 turns [2015], since it frees an 8-tile slot.

#### Navigation bytecode (§11)

- **Direction walks instead of coordinate tables.** CORE.
- **BFS-ordered offset tables** for r² 20 (69 entries). CORE.
- **Incremental sensing** of only the newly visible tiles after a move. LATER, if map memory is costly.
- **Size the search to `Clock.getBytecodesLeft()`, with a greedy fallback.** CORE.

### 5.4 Exploration

#### Strategy (EXPLORATION §1)

- **Simple can be enough.** CORE: random unexplored targets, measured before anything fancier.
- **Idle units are wasted economy.** CORE: broadcast the battlefront.
- **Information is worth fighting for.** ADAPT: counter-production from what launchers see.
- **Read the comms rules first.** Done (§5.0).
  - Reads are global and free of range limits.
  - Writes are range-limited. **Discovery is store-and-forward**: a carrier's trip home is the courier
    (inference).

#### Choosing targets (§2a)

- **Random direction extended to the map edge** [2025 JWU]. CORE: the cheapest default. Edges are known.
- **Uniformly random unexplored tile** [2026 SPAARK, code]. CORE (P6).
  - Pick it from 60 `long` seen-rows: count zero bits, draw r, walk rows by popcount.
  - Timeout = `distance × turnsPerTile + 20`.
- **"Diffusion"**: move one way until blocked, then turn, with crowd avoidance [2025]. ADAPT for amplifiers.
- **Phased targets.** CORE.
  - Early: the map centre (it settles symmetry fastest) and the enemy-HQ candidates.
  - Later: the nearest unexplored region and unclaimed islands.
- **Coarse grid of exploration points** [2016, 1st]. LATER.
- **Frontier search over a seen-mask.** ADAPT, local per unit. Computing it centrally needs shared space the array
  lacks.
- **Toward the enemy, with randomness.** CORE for launchers.
- **Zones or quadrant centres.** SKIP: too thin on big walled maps [2025 SPAARK].

#### Movement patterns (§2b)

- **Zig-zag on diagonals** (diagonal moves cost the same). ADAPT for exploring carriers and amplifiers.
- **Vision-cone scanning.** SKIP. 2023 vision is not directional.
- **Edge-hugging flankers; border patrol.** LATER.
- **Head toward unknown edges.** SKIP. Edges are known.

#### Spreading explorers (§2c)

- **Coulomb repulsion with momentum** [2021 wololo]. ADAPT for launchers and amplifiers sweeping for islands.

  ```
  F = Σ over visible same-role allies e with distToUnexplored(e) <= distToUnexplored(me): (me − e)/|me − e|²
  heading = normalize(α·heading + F)
  ```

- **Cheap repulsion; heading explorer that rotates off map edges** [2022, 2026 code]. ADAPT.
- **Potential-field explorer** with weights −1000 threat, −2000 last-damage spot, +100 momentum, −128 standing
  still [2016]. LATER.
- **Give up on unreachable targets**: turns proportional to distance; blacklist after 20 turns. CORE.
- **Always have a next target** after an objective falls. CORE: the next island, cluster or candidate.

#### Sensing and inference (§3)

- **Every unit is a sensor.** CORE, in 2023 form.
  - Buffer sightings in unit statics. Flush when `canWriteSharedArray` is true (near an HQ, an amplifier or our
    own island).
  - Carriers flush every cycle. Launchers rarely do, which is the case for amplifiers near the front.
- **Use negative information.** CORE.
  - A predicted enemy-HQ tile seen empty eliminates that symmetry.
  - An island seen with no enemy units is safe to anchor.
- **Persistent forward observers.** LATER. An amplifier parked near the front relays writes (r² 20), sees r² 34,
  and has 120 HP.
- **Infer unseen threats from damage.** ADAPT.
  - Inside a cloud a unit sees only r² 4, but can be hit from r² 16, and attacks need no vision.
  - `damageTaken > 20·(visible enemy launchers within r² 16) + 4·(enemy HQ within r² 9)` means an unseen
    attacker. Step out of the cloud, or blind-fire at the last sighting.
- **Hidden state from aggregates.** ADAPT.
  - `getRobotCount()` is an exact own-team census for free.
  - The enemy bank and income are not observable. SKIP.
- **Track entities by ID; candidate lists with a "missing" state.** CORE. Enemy-HQ slots are filled from symmetry
  and confirmed by sight; HQs never move.

#### Representing knowledge (§4)

- **Bitmask rows**, one `long` per row: seen, wall, cloud, well, island. CORE.
- **Packed blocks.** SKIP.
- **O(1) indices from guarantees.** CORE. `senseIsland(loc)` returns a global island id from 1 to `islandCount`,
  so array slots are indexed by island id with no coordinates.
- **Retractable facts with round stamps.** CORE: island ownership, enemy clusters, well type.

#### Edges and coordinates (§5)

Edge probing, maximum-size bounds, edge sharing and mod-128 addressing all SKIP: `getMapWidth()` and
`getMapHeight()` exist. Encode a location as `x*60 + y + 1` (12 bits, 0 = empty), which leaves 4 spare bits per
word.

#### Turning knowledge into targets (§7)

- **Online clustering of enemy sightings** [2022 5 Musketeers]. CORE (P6).
  - Keep 3 running means in the array. Each sighting joins the nearest mean or starts a new one.
  - The first HQ each round decays the means.
  - This also fixes distress oscillation.
- **Shared target board with decaying priority** [2017 AGRF, 1st]. ADAPT.
  - Replacement rule: `old/(20+age) < new/20`.
  - Consumers pick the slot maximising `priority/(age+5)/(dist²+10)`.
  - A few slots of (stamp, priority, location) fit in the array.
- **Event queue plus a visited grid in shared memory.** SKIP: no room.
- **Attack the weakest enemy bases first** [2021]. ADAPT: enemy islands ordered by `senseAnchorPlantedHealth`,
  lowest first.
- **Battlefront broadcast; rally on the target nearest the army's centre of mass; "push the enemy base to last".**
  CORE, with one 2023 change: **never** target an enemy HQ itself, because it is invulnerable.
- **Resource discovery broadcasts and per-unit discovery memory.** CORE for wells and islands, including mirrored
  ones.

### 5.5 Symmetry

#### Why it pays (SYMMETRY §1)

All four surviving items apply in 2023:

- **Doubled map knowledge.** Mirror walls, clouds, currents, wells and islands.
- **Our half against theirs.** It gives island and well safety.
- **Income asymmetry.** It is the win condition here, applied to islands.
- **Deficit detection.** "Islands held < half of the mirror-paired set" means some enemy pocket is on our side.

#### Candidate set (§2)

**2023:** rotation, horizontal reflection or vertical reflection.

- The engine's `GameMap.symmetry` takes 0 for rotation, 1 for horizontal and 2 for vertical, per the ReplayDump
  header comment. Diagonals are therefore impossible. SKIP them.
- Define each name by its formula in code, never by the English word. CORE.

#### Integer-safe formulas (§2)

**2023:** The centre is known on turn 0: `cx2 = W−1`, `cy2 = H−1`. CORE.

```java
static int mirX(int s, int x){ return s == HREF ? x : W1 - x; }   // W1 = W-1
static int mirY(int s, int y){ return s == VREF ? y : H1 - y; }   // H1 = H-1
// ROT: (W1-x, H1-y); HREF (horizontal mirror line): (x, H1-y); VREF (vertical mirror line): (W1-x, y)
```

#### Detection

- **Spawn-set test (§3a).** ADAPT. Enemy HQ positions are not given; RobotController has no such call.
  - **Turn 0, from our own HQs (inference):** for each s and each own HQ h, eliminate s if `mirror(s,h) == h`, if
    `mirror(s,h)` is another of our HQs, or if `mirror(s,h)` lies inside some own HQ's vision with no enemy HQ
    sensed there. This is cheap, and decisive on small maps.
  - **Once enemy HQs are seen:** run the multiset test from SYMMETRY §3a. Use the geometric shortcut too: if an own
    HQ and a seen enemy HQ share neither x nor y, only rotation can map one to the other. With several HQs, rely on
    the multiset test.
- **Full map at turn 0 (§3b).** SKIP: there is fog.
- **Fog elimination (§3c).** CORE.
  - Compare only **static** features: walls; clouds; island-tile presence (not ids, which may not mirror); well
    presence; currents **with their direction mirrored**.
  - Direction mirroring: ROT gives the opposite direction; HREF negates dy; VREF negates dx. The guide warns about
    "Forgetting to mirror direction-valued tiles".
  - Compare well *type* only with care, because a Mn well can become Ex.
  - Never compare robots, island ownership, anchors, or well inventory and upgrades.
  - Use the row-bitmask XOR test. **Java needs the unsigned shift**: `R(x) = Long.reverse(x) >>> (64 − W)`. The
    guide writes `>>`, which smears the sign bit when the top bit is set.

  ```
  HREF invalid if ((wall[y] ^ wall[H1-y]) & (exp[y] & exp[H1-y])) != 0
  VREF invalid if ((R(wall[y]) ^ wall[y]) & (R(exp[y]) & exp[y])) != 0
  ROT  invalid if ((R(wall[y]) ^ wall[H1-y]) & (R(exp[y]) & exp[H1-y])) != 0
  // repeat per static layer; only rows in the current vision band; flag self-found eliminations to send first
  ```

  Cost: "about 1k bytecode for an exhaustive check" [2025 Om Nom]. Do the full check on the HQ's spare bytecode.
  Units check only the rows in their vision band.
- **Visit the predicted HQ (§3d).** CORE.
  - Launchers head for the enemy-HQ candidates, rotation first if the corpus prior says so.
  - On arrival within r² 20, if no HQ is there, eliminate that symmetry.

#### Who finds it and where (§4)

- **The map centre first.** CORE for early launchers and scout carriers.
- **Report as soon as you can write.** CORE.
  - A unit that eliminates a symmetry in the field cannot write until it is near an HQ, an amplifier or our own
    island. It keeps the 3-bit mask and flushes at the first chance.
- **Don't send singles to symmetry targets.** CORE. Pair the targets with groups [2026 TSPAARK].
- **Fall back gracefully; check reachability of the predicted HQ.** CORE.

#### Using it (§5)

A `Sym` class keeps the OR-merged eliminated mask from the array, `bestGuess()`, `enemyHqGuesses()`,
`effectiveTile()` and `onFeatureDiscovered()` (record the mirror twin). CORE.

- **Hedge until it is decided.** For anchor-island choice and well safety, take the worst case over every live
  candidate.
- **Name the consumers before building the detector** (ADVICE §8). The 2023 consumers:
  1. launcher rally and raid targets (enemy-HQ perimeter, enemy wells);
  2. mirrored islands as enemy-side targets;
  3. own-half classification of islands and wells (anchor priority, carrier safety);
  4. the rush-distance latch;
  5. unseen-terrain fill for reachability BFS.

  `tools/deadcode.py` exists because a `Sym.observe` was once never called (owner prompt 127, per its header).
  Keep running it.

#### Checklist (§7)

Tabulate the symmetry of all 103 maps in the engine jar from `GameMap.symmetry` with a one-off tool. Use the result
as the prior for `bestGuess`, and test each symmetry type from both sides.

### 5.6 Combat

#### Laws (COMBAT §1)

- **Concentrate.** Fights are Lanchester-non-linear. CORE.
  - Launchers deal aimed, ranged, single-target fire, so the square law applies (inference).
  - "Never engage when outnumbered unless next to your base." In 2023, "next to base" means within our HQ's r² 9
    (+4 per round), or on our anchored island if anchors heal (VERIFY).
- **Reach and awareness gaps.** CORE plus LATER.
  - Launchers on both sides see r² 20 and hit r² 16, so that gap is symmetric.
  - **Clouds** create asymmetric gaps: inside, a unit sees r² 4 but can be hit from r² 16.
  - Blind fire is legal per the engine. "Keep firing at a last known location" [2017 Segfault] maps directly.
  - "Attack static defences from just outside their range" maps to staying outside r² 9 of an enemy HQ while
    hitting units near it.
- **Defence is hard, attack is easy.** In 2023 the base cannot die, so the things to defend are carriers and
  islands.
- **Emergent beats commanded.** CORE.

#### The micro kernel (§2)

CORE, adapted to 2023 launchers:

```
microTurn():                                              // called first; return false -> macro
  enemies = senseNearbyRobots(20, opp) (cached); if none and no recent threat: return false
  cands = isMovementReady() ? [CENTER] + 8 dirs(canMove) : [CENTER]
  for c in cands:
    m.loc = here + c
    for e in enemies:
      threatR2 = e.type==LAUNCHER ? 26 (may step then shoot) : e.type==DESTABILIZER ? 25 : e.type==HQ ? 9 : carrier w/ cargo ? 9+ : 0
      if dist2(m.loc,e) <= threatR2: m.danger++; m.expDmg += dmg(e.type)
      if dist2(m.loc,e) <= 16: m.canAttack = true; m.bestTarget = max(value(e))
      m.minDist = min(m.minDist, dist2(m.loc,e))
    m.support = allies (launchers) that can hit the same nearest enemy
    m.cost = cloud(m.loc) + currentAway(m.loc)
  best = argmax by isBetterThan
  // both orders: if attack available now and best moves away -> attack then move; if best steps in -> move then attack
isBetterThan: not-lethal first; if canAttack matters -> canAttack, fewer danger, more support;
              else fewer danger, larger minDist; then lower cost; then closer to macro target
```

- **2023 twist (inference).** The weapon is almost always ready (action cooldown 10, so one attack per turn); the
  scarce cooldown is **movement**. Branch on `isMovementReady()`, not on "weapon ready".
  - Stepping into r² 16 holds the unit there for 2 turns, so step in only with local superiority or a kill.
  - When the move is ready and an enemy is in range: attack, then step out if outnumbered, or hold if not.
- **Variants.**
  - Single-currency additive score [2025 SPAARK]. ADAPT.
  - Jointly evaluate move then act. CORE (both orders, above).
  - Expected-damage minimisation, plus the "hide" variant that keeps a unit outside every enemy's *vision*.
    CORE for carriers: their flee step.
  - Distance bands [2013 Teh Nubs, 1st]. CORE as the first cheap version, using bands at r² 16, 26 and about 45.
    Rules: an enemy in range means fight; no enemy within 3 bands or allies ≥ 3× enemies means advance; otherwise
    compare counts + 1.
  - Ideal range per enemy type [2017]. ADAPT: hold at the edge of r² 16, with type weights.
  - Attract/repel potentials [2017]. LATER.
  - Directional facing. SKIP.
  - Influence maps. SKIP: too expensive at 10000 bytecode.
- **Implementation.**
  - Keep the kernel unrolled and object-free (≈2x cheaper [2025 Om Nom]).
  - Trigger micro on enemies visible or remembered.
  - Skip micro when the enemy is unreachable, with an exhaust timer.
  - **Refresh state after every action** [2018 smite]. CORE.

#### Engagement decisions (§3)

- **Local numeric superiority.** CORE. Count enemy launchers that can hit me against allied launchers that can hit
  the nearest enemy. Use `guessIfFightIsWinning`: allies ≥ {2, 4, 5, 1.5n} for n = {1, 2, 3, ≥4} [2014, 1st].
- **Exact 1v1 cooldown race.** CORE. In 2023:

  ```
  myTurnsToKill    = (isActionReady()?0:1) + ceil(enemyHP/20) - 1   // 200 HP -> 10 hits
  theirTurnsToKill = 0 + ceil(myHP/20) - 1  (+ HQ: subtract 4/turn from the side inside an HQ's r2 9)
  fight iff myTurnsToKill <= theirTurnsToKill   (±1 for whoever spends this turn moving in)
  ```

  Equal-HP launchers trade evenly. **Whoever shoots first wins the duel.** So the move-then-attack step-in decides
  fights, and holding just outside r² 16 so that the enemy steps in is the right default (inference).
- **Strength over a wider area from shared sightings** [2012]. LATER.
- **Contextual aggression** [2026 food]. ADAPT: halve the proximity penalty at a 2:1 advantage, and charge when an
  anchor carrier is threatened.
- **Step-in discipline** [2024 replay study; 2019 smite]. CORE: "strike → leave reach → hold one step outside
  reach → strike". In 2023 the cycle period is set by the 2-turn movement cooldown.
- **Hysteresis states** (OFFENSIVE / DEFENSIVE / RUNAWAY). CORE.
- **Retreat rules must not be baitable.** ADAPT: retreat on local counts, not on any single sighting.

#### Kiting (§4)

- **Kiting skeleton.** ADAPT. Kite slow enemies and fight equal-speed ones.
  - Launchers against launchers are equal speed, so stand and fight with superiority, or leave early.
  - An **empty carrier outruns everything**, so it always flees.
  - A **loaded or anchor-carrying carrier cannot flee** (0.5–1 tiles per turn). It throws its cargo at the
    attacker (§12) or retreats toward support.
- **Synchronise attackers against single-target defences.** LATER, depending on whether the HQ hits one target or
  all within r² 9 (VERIFY).

#### Targeting (§5)

CORE: score actions on a common value scale.

```
value(e) = (e.health <= 20 ? 1000 : 0)               // guaranteed kill this turn
         + typeValue[e.type]                          // LAUNCHER 45, DESTABILIZER 200, BOOSTER 150, AMPLIFIER 45 (+comm denial),
                                                      // CARRIER 50 + cargo + (anchor? 160 : 0)
         - e.health/10                                // lowest HP first within a class
// never target HEADQUARTERS (indestructible; RobotType.health = 1 is not a real HP)
```

- **Focus fire through a shared slot.** ADAPT.
  - Writes are range-limited, so get implicit focus instead: every launcher applies the same deterministic order
    (value, then lowest ID). That needs no comms.
  - The 2014/2019 posted-target slot is LATER, near amplifiers.
- **Area attacks** (destabilizer r² 13, cost 200 Ex). LATER. Score each aim point +10 per enemy and −10 per ally,
  and never reward unseen tiles.
- **Line-of-fire checks; spread versus single shots.** SKIP: there are no projectiles to block or spread.

#### Retreat and survival (§6)

- **Healing state with hysteresis** (enter below 20% HP, leave above 80%) [2014, 1st]. ADAPT, only if anchored
  islands heal (VERIFY).
- **Retreat direction from the sum of enemy vectors**, trying ±1..±4 rotations while skipping enemy-HQ range. Ban
  directions toward a nearby corner. CORE.
- **VIP flee arc** [2012]. ADAPT for the anchor carrier, our VIP. Score 8 directions, smooth with neighbours, and
  flee to the centre of the widest low-score arc.
- **Perpendicular escape from a straight-line chaser.** ADAPT for carriers.
- **Spawn units toward attackers** to body-block near the HQ [2026]. CORE in rush defence.

#### Groups (§7)

- **Spawn order as an implicit formation.** CORE (inference).
  - The HQ can build up to 5 launchers in one turn. Launchers built on the same turn share a movement-cooldown
    phase, so they move in lockstep.
  - Build launchers in batches toward the target side. This is "emergent coordination" for free.
- **Swarm physics and concave "most allies, fewest enemies".** LATER.
- **Lattices.** ADAPT on islands. Units block tiles, so a launcher ring on an island denies enemy carriers the
  tiles they must stand on to `placeAnchor()`.
- **Distress without oscillation.** CORE: use the sighting clusters (§5.4).
- **Multi-pronged pressure and edge flanking.** LATER.
- **Enemy bodies as cover.** SKIP.

#### Macro (§8)

- **Hit the economy, not the army.** CORE.
  - Target enemy carriers at enemy wells (mirrored from ours) and anchor carriers in transit.
  - "Kill production" does not apply, because HQs cannot die. Spawn camping from just outside r² 9 is the LATER
    analogue.
- **Harassment that blocks movement; mass arrival; timed all-ins.** ADAPT.
  - Use mass arrival at islands.
  - Time the all-in against the round-2000 deadline or the enemy's approach to 75%:
    `moveOut = deadline − travel`.
- **Close the game when ahead.** CORE: 75% of islands.
- **Body-blocking walls.** LATER: island denial.
- **Static defences; anti-turtle mode.** SKIP. Nothing is buildable, and "build what the field actually does".

#### Rush defence (§9)

- **Detect early.** ADAPT: HQ vision reaches r² 34, plus amplifiers.
- **Respond proportionately.** CORE. The HQ can turn banked Mn into up to 5 launchers per turn on the attack side.
  "Just spawn more units when in danger" was enough for one team [2026 Lorem Ipsum].
- **Cap and time-box the response.** CORE.
- **Defend starting production**: the wells near the HQ. CORE.

#### Neutral hazards; projectiles (§10, §11)

SKIP. 2023 has no neutral faction and no projectiles. Clouds and currents are terrain, handled in §5.3.

#### Ability combos and action economy (§12)

- **"Look for anything that multiplies actions per turn."** LATER, but high potential (inference).
  - Boosters stack −10% cooldown up to 3 times; the accelerating anchor gives −15%.
  - A launcher's action cooldown of 10 × 0.7 = 7 allows a second attack in some turns (0 → 7 → 14). That averages
    about 1.4 attacks per turn, *if* the multipliers apply to action cooldown.
  - Destabilizers add +10% per stack to enemy cooldowns.
  - **VERIFY in the engine before spending elixir.** The guide's own note: "Both years' biggest surprises came from
    reading the turn queue and cooldown rules."
- **Carry and throw** [2026 GST, Lorem Ipsum, food]. ADAPT.
  - A carrier with cargo can attack (throw, `CARRIER_DAMAGE_FACTOR = 1.25`; the formula is VERIFY).
  - Rule: a carrier that will die anyway (in range of enemy launchers and too slow to escape) throws its cargo at
    the best target rather than dying with it.
- **Relay objectives (handing anchors between carriers).** SKIP unless the engine allows carrier-to-carrier anchor
  transfer (VERIFY).

#### Improving micro (§13)

ADAPT. 2023 map files can pre-place only HQs, wells, islands and terrain, not units. So build small "arena" maps
with the HQs close together, plus the "watch one unit" loop through `ReplayDump --robot ID`.

### 5.7 Communication

The sources are EXPLORATION §6 and ADVICE §9; the 2023 rules are in §5.0.

#### Channel rules

- **Read the channel rules first.** Done.
  - 64 words of 16 bits.
  - Read anywhere.
  - Write only in range, or the call throws (500 bytecode, and an uncaught throw ends the turn). Always guard with
    `canWriteSharedArray`.
  - **VERIFY:** whether a write is visible to later robots in the same round, and whether a newborn can read on its
    first turn.

#### Topology

- **Hub and spoke.** CORE. The HQ always writes, has 20000 bytecode and is immortal.
  - "Send the results of a large computation rather than the base data" [2013].
- **Rotating commander.** ADAPT.
  - HQs never die, so a fixed commander (the HQ with the lowest index in the array) is enough.
  - Use a per-round token so the first-acting HQ resets accumulators and the last commits them.
- **Relay with a gradient; amplifiers as relays.** LATER (P6).
- **Spawn-time handoff.** CORE, by spawn position (§5.2).
- **Security.** SKIP. Each team has its own array (VERIFY).
- **"Don't advertise to hazards."** SKIP.

#### Encoding

- **Type header plus payload.** CORE. A word holds 12 bits of location plus 4 bits of type or flags.
- **Deterministic enumeration.** CORE. Island ids index island words directly.
- **Log-scale 4-bit counts.** CORE for cluster sizes.
- **Priority arbitration and dedupe.** LATER.
- **Flush on a schedule.** ADAPT: flush whenever a write is possible, oldest-stamped facts first.

#### Liveness and censuses

- **Heartbeats.** ADAPT for amplifiers only, since HQs cannot die.
- **"Decide what happens when a writer dies; stamp claims; newer wins."** CORE.
- **Census.** ADAPT.
  - The accumulator scheme fails in 2023 because far units cannot check in.
  - Use `getRobotCount()` for the exact total, HQ deposit check-ins for carriers, and HQ build counts minus
    observed or estimated deaths.
  - ADVICE warns that "a cumulative 'ever built' counter is not a census and becomes a lockout under attrition".
- **"Prefer positive claims under a lossy channel."** CORE.
  - The 2023 channel is lossy for far units: silence from a launcher group means "cannot write", not "nothing
    seen".

#### Proposed 64-word schema (my design; a starting point, not evidence)

| Words | Content |
|---|---|
| 0 | round stamp (12 bits) + commander token and phase flags (4 bits) |
| 1–4 | own HQ locations (12 bits, x*60+y+1) + flags (under attack, anchor-builder, …) |
| 5 | symmetry eliminated mask (3 bits) + confirmed bit + enemy-HQ count (3 bits) + all-in / endgame bits |
| 6–9 | enemy HQ locations (12 bits) + 2-bit confidence |
| 10–17 | wells: location (12 bits) + type (2 bits) + upgraded + enemy-side |
| 18–52 | islands by id (1..35): one known tile (12 bits) + owner (2 bits: unknown / none / us / them) + anchor-in-transit claim + contested |
| 53–58 | 3 enemy sighting clusters: (location 12 bits + log-count 4 bits), (round stamp) |
| 59–61 | census accumulators or targets (carriers, launchers, amplifiers) |
| 62 | per-HQ build intents (4 HQs × 4 bits) |
| 63 | rally or target word (location + type) |

The schema should be generated from one table into the code, and unit-tested for encode/decode (ADVICE §6).

### 5.8 Bytecode

The sources are ADVICE §3, NAVIGATION §11, ECONOMY §8 and COMBAT §2.

#### The monitor (CORE, day 1)

- Compare `getRoundNum()` before and after the turn logic; a change means an overrun.
- Read `Clock.getBytecodesLeft()` at the end of the turn and flag a near miss above 90%.
- Report both as indicator counters.
- `ReplayDump --bytecode` already reports per-type maximum, mean, p99, near misses and overruns from the replay.
- "Zero overruns is the standard". "Treat any overrun in a candidate as voiding its evaluation."

#### Cheap patterns (CORE style rules)

- Static fields over instance fields; arrays over collections.
- Unrolled loops over fixed radii; direction walks.
- A hand-rolled xorshift instead of `java.util.Random`; it also keeps play deterministic.
- `long` rows per feature; a switch rather than an if-chain.
- **No allocation in inner loops.** One allocating terrain scan "put units over budget a hundred times a game".
- In Java 8, avoid streams, lambdas and boxing.

#### Amortise

- Update map memory only for newly visible tiles.
- Run full symmetry checks on the HQ's spare bytecode. HQs are the free-compute units: 20000 bytecode and few
  actions.
- Spread scans over turns, and skip a scan when the budget is gone so the unit still acts.

#### First turn (CORE)

- Carriers spawn constantly, so a heavy static initialiser is paid many times.
- Keep the first turn small: `long[60]` rows, lazy tables.
- **VERIFY** how the instrumenter charges array allocation before using any `int[3600]`.
- The cost of `senseNearbyMapInfos()` (up to 69 `MapInfo` objects at r² 20) should be measured. Prefer per-tile
  `senseMapInfo` on newly visible tiles if it is expensive.

#### Debugging

- Keep the debug class trivial; reflection-flavoured calls can be rejected by the instrumenter.
- Count exceptions; ReplayDump's summary includes them, and `DIE_EXCEPTION` events.
- "Do not optimise first": budget rarely binds until the basics work.

#### Older-year compute tricks

The 69-bytecode hibernation does not apply, because 2023 has no refund. SKIP. Budget-sized searches (BFS radius
chosen from `getBytecodesLeft()`) are CORE for navigation.

---

## 6. Tools and infrastructure inventory

### 6.1 This slice's repository (`reference/battlecode-vibe`)

It holds documentation only; there are no scripts.

| Path | Purpose | Quality | Reuse verdict for 2023 |
|---|---|---|---|
| `ADVICE.md` | 37 problems plus appendices: foundations, bot capabilities, method | High; year-agnostic; unattributed | Steal as-is as the method reference. Appendix B's checklists are the day-one list |
| `ECONOMY.md`, `NAVIGATION.md`, `EXPLORATION.md`, `SYMMETRY.md`, `COMBAT.md` | Cross-year techniques with pseudocode | Good; second-hand; source lists stripped by the filter | Steal as reference. §5 of this report is the 2023 adaptation |
| `PROMPTS.md` | Owner prompts, verbatim | n/a | The 2023 project already keeps its own `PROMPTS.md` |

There is no code to port from this slice.

### 6.2 ADVICE's instrument list against what `2023/tools` already has

I read header comments only; auditing these tools is not this slice's job.

| ADVICE instrument | 2023 tool | Status, and what must change |
|---|---|---|
| Rules digest with engine provenance | `docs/` is empty | **Gap.** Start `docs/RULES.md` from §5.0 here, with javap provenance |
| Headless parallel runner, bare JVM | `tools/gauntlet.sh` + `lib.sh` (JDK 8u504; cells file; MAXJOBS; GAME_TIMEOUT) | Present |
| Seed per game / determinism | `get-engine.sh` patches `LiveMap.getSeed()` to honour `-Dbc.game.seed` | Seed control present. I did not see an identity/determinism test; add one (ADVICE §2) |
| Replay-to-text reader | `tools/replaydump/ReplayDump.java` (.bc23, flatbuffer schema of engine 3.0.15; 10 modes incl. `--census`, `--bytecode`, `--navstats`) | Present; matches ADVICE's list. The bot must emit `note|k=v` indicator strings of at most 64 chars |
| In-bot bytecode/overrun monitor | none (`src/` holds only `examplefuncsplayer`) | **Gap.** Plan step P0.3 |
| Snapshot tool (renamed package) | not seen | **Gap**, or done by hand. Each accepted build becomes `g_iterN` (naming per `elolib.py`) |
| Mirror and sparring | `gauntlet.sh` with `OPPONENTS` | Present. A play-symmetry (side split) report is not seen; `summarize.py` has a side split |
| Unit tests | `tools/unit-tests.sh` (bot compile, `test/bot/*Test.java` mains, `tools/test_tools.py`) | Present |
| SPRT | `tools/sprt.py` | Present. Its docstring says "no draws in BC20"; 2023 also has no draws (the tiebreak ends in a coin flip), but check the default p0/p1 |
| Batch Bradley-Terry ladder | `tools/elolib.py` | Present |
| Game-by-game diff | `tools/compare.py` | Present |
| Correlation and onset | `tools/statlib.py` (its docstring names `correlate.py` and `onset.py`) | Partial: those two scripts are not in `tools/` (inference from the listing) |
| Dead-code check | `tools/deadcode.py` | Present. It guards "symmetry inference that feeds no decision" |
| Compute VM | `tools/vm.sh`, `vm-run.sh`, `vm-tail.sh` (battlecode-dev e2-standard-8; driver e2-small) | Present. ADVICE: never run volume on the session host |
| Throughput measurement | `tools/throughput.sh` | Present |
| Benchmark handling without reading source | `bench-*.sh/.py`, `benchcompile/BenchCompiler.java` | Present (rule 4) |
| Reading-room filter | `filter_year.py`, `build_readroom.py` | Present |
| Map-corpus symmetry tabulation | none | **Gap.** One-off: read `GameMap.symmetry` for the 103 maps in the jar |
| Purpose-built test maps | none | **Gap** (P4) |

**What must change for 2023.** Nothing from this slice needs porting. For the bot itself:

- Java 8 only (no `var`, records or switch expressions).
- The engine 3.0.15 API names in §5.0.
- Indicator strings of at most 64 characters.
- The `.bc23` replay schema is already handled by ReplayDump.

---

## 7. Pitfalls and gotchas

Costs are given where the source states one.

### From the guides and ADVICE

1. **A stall counter reset by target re-picks.** Fixing it was "the largest single gain of one season" (ADVICE §7).
   Make stall counters survive target flicker.
2. **Hidden movement penalties.** One "sat unnoticed for a hundred and fifty iterations and cost a quarter of all
   movement". In 2023, read the engine's move cost rules: clouds, currents, carrier load.
3. **A blocked spawn or deposit ring**: "a recurring, season-wrecking bug". In 2023 it is 8 deposit tiles per HQ
   and 8 collection tiles per well.
4. **Writing to a channel you cannot write.** "every call threw and aborted the turn". In 2023, each throw also
   costs 500 bytecode. Always guard with `canWriteSharedArray`.
5. **A census that counts dead units as alive.** It shut production off "forever at round five hundred".
6. **One-round orders.** A unit built this round acts next round, so it never reads a one-round order.
7. **Symmetry bugs.**
   - comparing dynamic state;
   - forgetting to mirror direction-valued tiles (currents);
   - accepting a partial check;
   - building a detector that feeds no decision.
8. **Bytecode.**
   - An allocating scan in a hot loop ("a hundred times a game").
   - Overruns on the first turn.
   - Blaming outcomes on bytecode without reading the monitor (two seasons, both retracted).
9. **Probing at runtime for a corpus constant.** It cost a rush "three hundred rounds of arrival time". Tabulate
   the 103 maps instead.
10. **State that is stale after a move.** Melee units stepped in and "waited a turn to attack, and died". Re-sense
    after every action.
11. **A cooldown that looks like a wall.** In 2023 this hits carriers at every load change and launchers on
    alternate turns.
12. **Reading a running batch.** A "zero-to-five read that ended eleven-to-five voided a gate".
13. **Fixed compass tie-breaks.** They produce mirror splits of "100/0". Audit them, and play both sides.
14. **Absolute stickiness against per-tick ping-pong.** Give each target a release condition.
15. **Distress oscillation and stampedes.** Cluster the sightings, and don't broadcast single targets to
    everyone.
16. **Baitable retreat rules.**
17. **Copied code that nobody understands.** "Copying without understanding made later changes hard."
18. **Heal-queue starvation** ("over 1000 rounds").
19. **Emergency modes that freeze the economy.** Time-box them.

### Found while mapping onto 2023 (engine reads)

20. **The guide's row-mirror formula is unsafe in Java.** It writes `Long.reverse(x) >> (64 − W)`; Java needs
    `>>>`.
21. **Collect and transfer need adjacency** (distance² ≤ 2), even though the carrier's action radius is r² 9.
    Planning deposits "within 3 tiles of the HQ" would fail every time.
22. **`GameConstants.SPEC_VERSION` reads "3.0.14"** inside the 3.0.15 jar. Don't use it to identify the engine.
23. **`RobotType.HEADQUARTERS.health = 1`.** HQs are indestructible, so never put HQ "HP" into a value or kill
    calculation.
24. **Indicator strings are capped at 64 characters.** They limit how many ReplayDump counters one robot can
    carry.
25. **A carrier can `attack` only with inventory.** Empty carriers cannot throw.
26. **Attacks have no vision check.** Not seeing the enemy, for example in a cloud, does not mean it cannot hit
    you.
27. **Well type changes** (Mn → Ex after 600 Ad). It is not a static symmetry feature, and assignments must
    re-sense the well.
28. **`tools/sprt.py`'s docstring still describes BC20**, and `statlib.py` names `correlate.py` and `onset.py`,
    which are absent. Check both before relying on them.

---

## 8. Top 15 takeaways for the 2023 project, ranked by expected value

1. **Aim the foundation at islands from day 1.** Seventy-five percent instant win; tiebreak islands held, then
   anchors placed. Read one starter game's ending reason (ADVICE §1). Build the anchor pipeline (HQ builds,
   carrier delivers, places, launchers guard) into the foundation, not after "economy, navigation and combat".
2. **Instruments first, in the bot.**
   - An overrun monitor plus `note|k=v` decision counters, consumed by `ReplayDump --census`/`--bytecode`.
   - Zero overruns, and no gate until a logged game shows the counter firing.
3. **Carrier economy done right.**
   - The HQ assigns wells at birth, with the spawn tile as the handoff.
   - The load threshold comes from an offline model: speed 10/floor(5+3m/8), one collect per turn.
   - Deposits are adjacent-only, so the HQ and well rings must stay clear.
   - Verify the collection rate first.
4. **Bug navigation with a safety policy and cooldown awareness.**
   - The enemy HQ's r² 9 is a wall for carriers.
   - Treat launcher threat as r² 26 (r² 16 after one enemy step).
   - Never let a not-ready movement cooldown corrupt bug's state.
   - Use a per-target time budget that survives target flicker.
5. **Symmetry with three candidates, settled early, feeding named decisions.**
   - Turn-0 eliminations from our own HQs; fog elimination with mirrored currents and `>>>`; visits to predicted
     HQs.
   - Feed enemy-HQ and enemy-well targets, mirrored islands and own-half safety.
6. **The shared-array schema before the logic.**
   - The HQ is the hub; carriers are couriers; facts are store-and-forward with round stamps.
   - Guard every write with `canWriteSharedArray`.
   - Island words are indexed by island id.
7. **The launcher micro kernel**, adapted to movement as the scarce cooldown.
   - Evaluate both move-then-attack and attack-then-move.
   - Step in only with superiority or a kill.
   - Hold just outside r² 16 so the enemy steps in. Whoever shoots first wins equal duels.
8. **Concentrate (Lanchester).**
   - Batch-build launchers on one turn so they move in phase.
   - Never trickle; regroup when outnumbered.
   - Rally on sighting clusters, not on single sightings.
9. **Production as a score queue that saves for the top item**, with two currencies. Route deliveries to the HQ
   that needs them, because banks are probably per HQ: avoid the "four HQs each holding 70" float.
10. **Endgame arithmetic.** A points-race formula for going all-in on anchors at 75%, and a deadline switch that
    turns every remaining Ad and Mn into placed anchors before round 2000.
11. **Hit the economy, never the HQ.**
    - Raid enemy carriers at mirrored enemy wells. Anchor carriers in transit are the top target.
    - Occupy enemy islands to decay their anchors.
    - Keep out of the enemy HQ's r² 9.
12. **Cheap map latches drive the opening**: map area, HQ count, rush distance (worst case over live symmetries),
    `islandCount`, wells near the HQ, wall fraction. They beat any global constant (ADVICE §4, §17).
13. **Simple exploration plus a never-idle rule.** Random unexplored targets with timeouts, the centre first for
    symmetry, then a battlefront or next-island broadcast so no unit idles.
14. **Read the engine for action multipliers and conversions.**
    - Boosters and the accelerating anchor reduce cooldowns: possibly about 1.4 attacks per turn for launchers.
    - Wells upgrade at 1400 deposited (rate ×3) and convert to Ex at 600.
    - Carriers can throw cargo.
    - These are the "biggest surprise" class. Measure them after the foundation.
15. **Measurement discipline from the start.**
    - Paired same-seed controls and SPRT on random maps and sides; mirrors from both sides on every map.
    - A frozen-roster ladder (Bradley-Terry) on every accept.
    - Copy any opponent tactic that beats us and submit it.
    - Record measurements, not stories.

---

## 9. Prioritised implementation plan for a 2023 foundation bot

The order follows ADVICE §12 ("Sequence capabilities") and Appendix B. Every step names its decision counter and
the check it must pass. Steps marked ★ are the minimum viable foundation.

### P0. Verify the engine facts that change designs (one logged diagnostic game each, or an engine read)

| # | Question | Why it matters |
|---|---|---|
| V1 | Collect yield per turn (rate 1, one collect per turn?) | It drives the whole carrier model |
| V2 | Are banks per HQ, and is the 200/200 start per HQ? | Delivery routing and anchor coordination |
| V3 | Does a newborn act the round it is built? Are array writes visible within the same round? | Handoff and comms timing |
| V4 | Robot turn order within a round | HQ token; congestion |
| V5 | Does the HQ attack one target or all within r² 9? | Defence and raids |
| V6 | Who sees units inside clouds, and from where? | Micro and blind fire |
| V7 | Current push rules (blocked? stacking?) | Navigation |
| V8 | Island occupancy rules: anchor HP decay and rise, what counts as occupying, and how anchors heal | Islands; retreat |
| V9 | Carrier throw damage formula; carrier-to-carrier transfer | Carrier combat; taxis |
| V10 | Mn→Ad-well conversion (`Well.addMana`) | Elixir |
| V11 | Do booster and anchor multipliers also scale action cooldown? | Action economy |
| V12 | Meaning of "anchors placed total" in the tiebreak | Endgame dump |
| V13 | Symmetry type frequencies across the 103 maps | Prior for `bestGuess` |

Also on day 0:

- **★ P0.1** Run one examplefuncsplayer mirror and read the ending reason. Fixture: a 2000-round game, decided by
  the tiebreak.
- **★ P0.2** Start `docs/RULES.md` with provenance (§5.0 here).
- **★ P0.3** Bot skeleton.
  - `RobotPlayer` dispatches by type.
  - `Dbg` provides the overrun monitor (counters `ov`, `nm`) and 64-character `note|k=v` counters.
  - A `try/catch` around each turn counts exceptions (`ex`).
  - Check: `unit-tests.sh` passes, and ReplayDump `--bytecode` and `--census` show the counters.

### P1. Comms and the HQ hub

1. **★** Implement the schema table and its encode/decode, with unit tests.
2. **★** On round 1, each HQ writes its location. The commander token goes in word 0.
3. **★** Units read the array once per turn into statics. Their outbound fact queue flushes when
   `canWriteSharedArray` is true. Counters: `fq` (queued), `ff` (flushed), `fd` (dropped stale).

### P2. Movement and economy loop

1. **★** `Nav.tryMoveToward` with a safety policy. A bug navigator (closer-than-start plus net-rotation leave
   rule, edge flip, no reset on a nearby target change). An `isMovementReady` guard. A per-target time budget and
   blacklist. Counters: `st` (stall exits), `bl` (blacklisted).
   - Check: `ReplayDump --navstats` shows no ABA oscillation streak over 20 turns on maze-like maps.
2. **★** Carrier loop.
   - Assignment by spawn tile; collect to the model's threshold; deposit when adjacent; leave the ring.
   - Re-target when a well's 8 tiles are full. Flee when empty or threatened; throw when doomed (after V9).
   - Counters: `cy` (cycles), `dw` (deposit wait), `wf` (well full), `th` (throws).
   - Check: income per carrier per turn is within 20% of the offline model (built in P0/V1).
3. **★** HQ production v0: a modulo cycle {carrier, carrier, launcher} plus a minimum-carrier rule. Counter `bs`
   (blocked spawn).
   - Check: beats examplefuncsplayer from both sides on every map; zero overruns.

### P3. Map memory and symmetry

1. **★** Row bitmasks (seen, wall, cloud, well, island, current planes), updated from newly sensed tiles.
2. **★** `Sym`:
   - turn-0 eliminations from own HQs;
   - an incremental XOR test on the rows in vision, with `>>>` and mirrored currents;
   - predicted-HQ visits;
   - an OR-merged mask in word 5.

   Counters: `se` (eliminations), with the round of settlement written by the HQ.
   - Check: on maps of each symmetry type, from both sides, the correct symmetry is never eliminated (assert in
     tests), and the settlement-round distribution is logged. The practice baseline was "by round 1 in about
     half ... by round 30 in about three quarters".
3. **★** Wire the consumers (enemy-HQ guesses, mirrored wells and islands, own-half test). Check: `deadcode.py`
   finds every `Sym` entry point called.

### P4. Launchers: micro and macro

1. **★** Distance-band micro first (cheap), then the 9-candidate kernel.
   - Both action orders; step-in discipline; 1v1 race; superiority check; hysteresis states.
   - Targeting by value, with deterministic implicit focus fire.
   - Counters: `ad` (attacks), `kl` (kills), `si` (step-ins), `rt` (retreats).
2. **★** Batch spawning: the HQ builds launchers in groups of 3–5 on one turn, toward the target side. Rally
   targets in order: sighting cluster, enemy wells, enemy-HQ perimeter (never inside r² 9).
3. Arena test maps (HQs close together; open and cloudy variants). Tune with "watch one unit". Check: the mirror
   splits evenly from both sides; the micro version beats the previous micro in paired SPRT.

### P5. Islands and anchors (the score term)

1. **★** The HQ builds a STANDARD anchor (80 Ad + 80 Mn) under the score-queue rule.
   - The anchor-builder HQ is chosen by the commander. Carriers route deliveries to it.
   - Counters: `ab` (anchors built), `ar` (Ad/Mn delivered to the builder).
2. **★** Anchor carrier.
   - Target: the nearest own-side unclaimed island, worst case over live symmetries, checked reachable.
   - It fixes one island tile, moves at launcher pace with an escort from the same batch, then places.
   - Counters: `ap` (placed), `al` (lost in transit).
3. **★** Launchers guard our islands (AROUND mode) and occupy enemy islands to decay their anchors.
   - Island-state words carry ownership by id.
4. **★** Endgame: the points-race all-in plus a deadline dump of all Ad and Mn into placed anchors. Counter `eg`
   (endgame mode entered).
   - Check: on the 2000-round games in a gauntlet, our islands held at the end ≥ the opponent's against the P4
     build, by paired SPRT.

### P6. Exploration and relay

1. Random unexplored targets with timeouts, the centre first, and zig-zag moves. Discovery broadcasts for wells
   and islands, including mirrored ones.
2. Sighting clusters (3 means) for rallies and defence. Battlefront and next-island words, so no unit idles.
   Counter `id` (idle turns).
3. Amplifiers as relays near the front (heartbeat bit), only if comms latency measurably costs fights. Measure
   facts dropped or late first.

### P7. Production policy and map adaptation

1. Replace the modulo cycle with the score-sorted queue: save for the top item per currency, diminishing scores,
   counters to observed enemy types.
2. Map latches feed opening choice and population targets.
3. Time-boxed, capped rush response: the HQ turns banked Mn into launchers on the attack side.
4. Income target before attacking, adapted by idle guards.

### P8. Later experiments, each a pre-registered candidate

- Well upgrade (1400) and elixir conversion (600), priced with the offline model.
- Boosters and the accelerating anchor (300 Ex), after V11.
- Destabilizer area damage.
- Optimal Bug or a vision Dijkstra, if `--navstats` shows movement is the gap. ADVICE §7 notes one season
  "reverted unrun" a pathfinder once stats showed movement was not the gap.
- Spawn camping just outside the enemy HQ's r² 9.
- A global all-in HALT bit.
- Island body-blocking lattices.

### Gates throughout (ADVICE §22, Appendix B)

- Paired same-seed controls; SPRT on random maps and sides; mirror splits from both sides.
- Snapshot every accept as `g_iterN`.
- Play the frozen roster on every accept.
- Use small maps for diagnosis only.
- After three rejects in one area, change area.
