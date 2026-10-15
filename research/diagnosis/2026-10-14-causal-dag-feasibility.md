# Causal DAG from losing panel games: feasibility (owner, PROMPTS 101)

2026-10-14 18:45 PDT. Evaluation only; nothing is implemented.

## Verdict

Feasible, and stronger than it first looks, for one reason: **panel games are deterministic per cell**. c_seam2
reproduced c_seam1 on all 100 cells (same map, opponent, side, seed), because its gate never bound. So when a
candidate runs the same 100 cells as the incumbent, each losing cell gets a true counterfactual: the same game with
one change. That is the part that is usually impossible. The DAG does not have to be inferred from correlations
alone. Each edge "A causes B" can be tested by a change that removes A, then checking cell by cell whether B goes
away too.

Two parts are hard. (1) The game is full of feedback loops, so the graph must be unrolled in time. (2) Each test
costs a panel (3–4 hours of queue), so about 6–10 tests fit in the remaining week.

## Data already on hand

- 29 panels on the same 100 cells (`gauntlet/*-panel-*`), each with `results.csv`, `census.csv` and its replays kept
  locally (10 `.bc23` files per panel), so any panel can be extracted with ReplayDump.
- Per game (`matches/<id>/extract/`):
  - `timeline.csv`: both teams every 10 rounds: alive and built by type; Ad and Mn collected, banked and carried;
    army value; value lost; damage; kills; islands; anchors; in contact.
  - `engagements.csv`: each fight's start, size on each side, first hit, exchange, result.
  - `hq.csv`: per-HQ bank, pressure, idle funds, and the HQ's own reason codes.
  - `trips.csv`, `deaths.csv`.
  - `tele_states.csv`: our bots' own decision codes, e.g. 't' for "carrier withheld under threat".
- The rules are known exactly (RULES.md, checked against the engine). So the graph's skeleton, meaning which
  variable can affect which at all, comes from game physics, not from data mining.

## Method sketched

1. **Nodes.** Binary states over time windows (r0-50, 50-100, 100-150, 150-250, 250-500, 500+). Each one compares us
   to the opponent in the same game, e.g. "Ad collected trails by ≥40 at r100", "live carriers trail by ≥4",
   "first lost engagement before r150", "HQ pressure r2≤9 for ≥20 rounds", "islands behind at r500", and "loss".
   Thresholds are set where the win rates of the two sides of the split differ most.
2. **Skeleton.** Edges come only from mechanisms in the rules, and always point forward in time. Unrolling in time
   breaks the cycles. For example, "fewer launchers → HQ besieged → carriers withheld → less mana → fewer launchers"
   becomes a chain across windows instead of a loop.
3. **Edge weights.** P(B | A) against P(B | not A), compared within one opponent and map cell. The paired panels
   control for opponent strength, which is the main confounder. Where an edge passes through one of our own
   decisions, the bot's reason codes show the mechanism directly; no inference is needed.
4. **Backward walk.** For each loss, follow active parents from "loss" back to the earliest active node with no active
   parent. Cluster losses by their root. The expectation, based on today's numbers, is 3–5 roots covering most losses:
   - early adamantium (Ad@100 −104);
   - first fight lost (dN at contact);
   - map-specific pathing (Forest);
   - opponent rush.
5. **Forward chain and fix.** For the largest cluster, for example: Ad short at r100 (A) → carriers capped by Ad, about
   60 built against their 109 (B) → Mn trails from r250 and launcher count falls behind (C) → HQ besieged and carriers
   withheld (D) → loss. Then:
   - **Change 1** targets A (c_ad1 does exactly this).
   - **Check 1.** On the same cells, did A switch off? Did B follow? If A is fixed but B is not, the edge was wrong or a
     side path took over. Example: c_seam1 fixed Forest mana (+285) but lost launchers (−8.9).
   - **Change 2** targets B with A fixed, built on top of change 1, and so on down the chain. Each step is one panel;
     determinism makes the per-cell comparison exact.

## Risks and limits

- **Observation vs cause.** The skeleton plus the paired cells limits confounding, but an edge stays a hypothesis
  until a change tests it.
- **Sample.** About 40 losses per panel. The same cells repeat across 29 panels, though, so stable losses (a cell
  lost by every build) are well characterised.
- **Roots that cannot be fixed.** Some roots will be "the opponent is simply stronger on this map". The walk should
  say so rather than invent a cause.
- **A fix can create a new loss path.** Fixing A changes the whole trajectory afterwards, so "fix B given A" must be
  measured on the new games, not on the old ones.
- **Cost.** Building the extractor and the graph is about half a day of offline work. Extracting 29 panels' replays
  on the 2 GB driver may need the VM.

## First run (2026-10-14 19:23 PDT; owner, PROMPTS 102: "try it out, but only submit a bot if it yields a positive result")

Data: 20 panels × 100 shared cells = 2,000 games, 836 losses; 41 cells have both wins and losses across builds, and
every comparison below is loss minus win **within those cells**. Graph: `tools/causal_dag.py` →
`research/diagnosis/causal-dag.md`. Drill-down scripts: `research/diagnosis/causal/`.

Backward walk from "loss": the late nodes are launchers alive (RD +0.66 at r600), army and mana; the walk ends at
**mana collected behind by r200** (219 of 836 losses), r50/r100 mana (151) and army at r100 (82). Adamantium is not
a root: Ad@100 behind has RD −0.19 (we trail in Ad in 69% of wins), so c_ad1 is not supported.

Drilling the Mn@200 root (each step one level earlier):

| step | loss − win, same cell | reading |
|---|---|---|
| r200 economy | our Mn −132, theirs +90; carriers built equal; we lose 1.2 more, they lose 2.4 fewer | the gap is carriers dying, not carriers built |
| r≤200 kills | enemy carriers killed −2.4, almost all in their half; launcher kills equal | — |
| same, holding the fight record fixed | carrier kills −0.67 ± 0.30 | mostly a **consequence** of winning fights |
| r≤200 launcher fights | won −13 points; first hit −0.03 (n.s.); start numbers −0.3 (n.s.); fights 57 rounds longer; enemy feeds 9.8 more launchers in, we 4.2 | fronts are attrition, decided by reinforcement rate (production) |
| r≤150 carriers | collecting −2.5 points of turns, waiting at crowded wells +1.7, fleeing +1.0 | — |
| trips started r0–60 / r60–100 | wait +0.8 / +1.9 rounds a trip; cycle +0.1 / +3.1 (n.s. once 1,000-round outliers are capped) | small |
| identical | r50: everything equal (same opening) | divergence begins r60–100 |

Long trips are a property of Forest and MassiveL, not a bug of ours: on Forest our deposit trips take a median of 87
rounds against the opponents' 92, but they complete 7,713 deposits to our 4,496 (more carriers).

## Verdict of the first run

**No positive result for a new bot.** The within-cell divergence starts small and diffuse at r60–100. The largest
early lever is about 2 rounds of waiting a trip, under 4% of the cycle. It grows through a feedback loop: slightly
less mana → fewer reinforcements → longer fights lost → carriers on both sides die or survive → mana gap. That is
chaotic amplification, not one fixable event. Every builds-level difference in this dataset is a small code change,
so the cells show how small perturbations play out, not a single mistake.

The robust structural signal is the one already under test: opponents run far more carriers and trips (60 against
109 built). c_cap1 and c_thr1 target it. c_ad1 is held (Ad is not a root).

The method itself works: the graph, the paired cells and the stratified checks separated a cause (fight results)
from an effect (carrier kills), and caught two false leads (adamantium; Forest's "stuck" trips). Lessons for the next
run:
- use capped or median statistics, since means were dominated by 1,000-round trips;
- add per-round positions from the replays, to see what slows carriers near wells at r60–100.
