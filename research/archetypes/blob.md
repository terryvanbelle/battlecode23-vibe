# arch_blob: S4 archetype (attrition blob that anchors only at the end)

Design: `docs/ARCHETYPES.md` section 4.3. Package `src/arch_blob/` (package `arch_blob`), a fork of `src/c_line6`
(5bc8e7e545ac), telemetry build tag 103. **Code hash 3c54b97e654b** (v4, the measured version). Member modelled:
britacatalin.FinalBot (panel matches 22, 204, 539, 605).

It was built only from observed behaviour (CLAUDE.md rule 3). The sources were:
- the member's census, timeline and engagement rows in `matches/{22,204,539,605}/extract/`;
- `research/matches/22.md`;
- `tools/replay-dump.sh --map-at` on `gauntlet/20261008-011350-panel1-g_iter0/replays/22.bc23` (BatSignal, MassiveL).

**Verdict (my computation; `tools/archsig.py` does not exist yet): INVALID.**
- Fidelity fails by one on-target metric.
- Robustness fails on one launcher overrun in 60 validation games.
- The 4-version budget is spent.

| check | rule | result |
|---|---|---|
| fidelity | every core metric faithful | 11 of 11: pass |
| fidelity | at least 75% of core metrics on target | 8 of 11 (73%): **fail** (mn_share100 0.749, L100 12.5, L250 24.5) |
| fidelity | at least 50% of secondary metrics faithful | 9 of 10: pass |
| strength | g_iter0 wins 2-10 of 20 | 6 of 20: pass |
| strength | c_line6 wins 2-10 of 20 | 8 of 20: pass |
| robustness | 20 of 20 against examplefuncsplayer; no overruns, exceptions, self-deaths or wrong symmetry | 20 of 20 wins, but **`over` = 1** (one launcher turn at 10,001 of 10,000, Maze A in the robust run); 0 exceptions, self-deaths and wrong symmetry |

## What it does

The constants are in the `ARCHETYPE arch_blob (S4)` block at the top of `C.java`. Each one carries the observation
that set it.

**Opening and production (`HQ.build`)**
- A launcher whenever Mn ≥ 45, then a carrier whenever Ad ≥ 50 under the cap. With 200/200 on r1 this gives LLLLC
  per HQ on r1 and CCC on r2, the member's opening on most maps (BatSignal: `1:L 1:L 1:L 1:L 1:C 2:C 2:C 2:C`; on Cat
  it opens with 2 launchers on r1).
- `C.OPEN_LAUNCHERS` and its comment ("LLLLC ... in all 40 games") overstate this, and no code reads the constant. I
  left them as they are so as not to change the measured hash.
- No amplifiers, destabilizers or boosters. Carriers never throw; they only flee.
- From r1800 (`SAVE_FROM`) nothing is built but anchors. The member's built counters freeze at r1800 in every long
  game, and its banks then rise.
- The HQ threat test is the real-danger one (`HQ_THREAT = 1`), so it keeps building under pressure.

**Economy (`ROLES = 3`)**
- Carriers mine mana. One carrier in `AD_EVERY` mines adamantium while its HQ holds less than 150 Ad. `AD_EVERY` is 9
  before r250, 5 to r1500, and 3 after (to bank 80/80 per anchor). The "one in k" choice uses a mixed hash of the id;
  `id % 9` put 5 of 15 early carriers on adamantium in v3.
- Each carrier re-picks its well on every trip, so one that fell back to an adamantium well returns to mana.
- Carriers built per HQ stay under three caps:
  - 4 + round/30;
  - 3 per known well, shared among our HQs, + 2, + round/150 (design: 3 per well);
  - none while 9 of our carriers stand in the HQ's vision.
  These caps came from v2 (30 carriers jammed around a corner HQ on ReverseFunnel and filled its spawn tiles) and v3
  (111 carriers jammed around one mid-map well on Hah from r800, which stopped the mana income).

**The blob (`Launcher.blobMove`)**, used whenever no enemy is in sight
- *Gather.* The leader is the lowest id in vision. It walks to the rally point, 60% of the way from the centroid of
  our HQs toward the centroid of the predicted enemy HQs. There it waits until it sees `BLOB_MIN` launchers:
  6 + round/25, capped at 30.
  - It also goes after 80 rounds of waiting with two thirds of `BLOB_MIN`.
  - From r150 it goes with 4 or more once it has seen no enemy for 50 rounds.
- *Follow.* A follower keeps within r² 8 of its leader. When the blob is advancing, a follower close to the leader
  steps toward the blob's objective, but never gets ahead of the leader (v2: followers that only held boxed their
  leader in).
- *Advance.* The leader goes to known enemy-held islands first, then to the nearest predicted enemy HQ. It waits while
  fewer than 6 (and fewer than a third) of the launchers it sees are close.
- A depleted blob (under a third of `BLOB_MIN`) falls back only if it has seen an enemy in the last 50 rounds.
- No launcher ever holds within r² 20 of our own HQ; it walks toward the rally point instead (v2 BatSignal: launchers
  holding by the HQ jammed it with its carriers).
- *Home defence.*
  - An HQ that sees 2 or more enemy fighters, more than our launchers there, writes a HELP slot (`Comms.HELP` = slot
    62). Every launcher that is not on a siege ring answers it.
  - The base's sighting rule also stays: a sighting within r² 100 of our HQ, for launchers within r² 400 of it.

**Spawn camp**
- A launcher within r² 64 of an enemy HQ, with no enemy in sight, holds a free tile at r² 10-25 from it. That is outside
  the r² 9 aura and in range of the near spawn tiles, so it fires at newborns.
- A launcher that sees more than 14 of ours there moves on to the next enemy HQ. With no other HQ, it stands behind the
  ring.
- The fight scoring never ends a turn inside an enemy HQ aura.

**Micro**
- `MICRO2` parity hold: unless ahead by 2 or more, a launcher never steps into extra enemy reach to fire. With the action
  spent, it takes the fewest-threat tile (fire-retreat).
- Focus fire: the lowest-HP target first, ties to the lowest id.

**Islands**
- Every launcher that sees an enemy-held island stands on it.
- Hunters go to every enemy island they know, else to the symmetric images of the islands on our side that they have
  not visited in 150 rounds. One launcher in three hunts from r400, two in three from r1700.
- Anchors from r1820, one per HQ every 5 rounds.
- `NO_CONQUEST`: a carrier never places the anchor that would reach 75% of the islands, so wins come on the r2000
  tiebreak, as the member's do (26 of its 28 wins).
- An island the shared slots still call enemy-held, but that the carrier has not seen lately, counts as a candidate for
  the HQ and the carriers: launchers far from any writer neutralise islands without updating the slots.

## Signature against g_iter0

**Fidelity games (20 cells: 10 panel maps × 2 sides, seed = map, `MAXJOBS=2 CENSUS=1 KEEP_ALL=1`)** come from two runs
of the same code:
- `gauntlet/20261008-174917-blob-q4` (the 10 quick cells);
- `gauntlet/20261008-181117-blob-v4-fidelity` (the other 10, plus Cat with arch_blob on side B again as a determinism
  check: r376, the same result).

Both were extracted on the VM.

**How the metrics were computed.** `<scratchpad>/blob/blob_sig.py` uses the survey's `sig.py` column definitions and
the section 2 aggregations (median, mean, pooled, share). It was run on the member's 40 panel games as a known-answer
check, and it reproduces every member value in the 4.3 table: mn_share100 0.869, L100 7, L250 14, group 63, exposed
0.004, ahead_share 0.788, spawn_kills 59.6, first_anchor 1858, tb_share 0.929, L_lead100 -2, eng_prog300 0.381,
first_hit 0.897, alone 0.092, ahead_win 0.969, anchors 6.1, anchor_games 0.70, L_total 493, isl_rounds 202.5, mn100 288.

**Columns.**
- Map sides in this file are arch_blob's side.
- `(f)` marks a value that is faithful but off target; `(NF)` marks a value that is not faithful.
- v1 was 4 diagnostic cells (Forest B, DefaultMap A, BatSignal B, Maze A).
- v2, v3 and v4q are `--quick` runs: 10 cells, one side per map, alternating.
- v4 is all 20 cells.

| id | target | core | member | v1 (4) | v2 | v3 | v4q | v4 (20) |
|---|---|---|---|---|---|---|---|---|
| mn_share100 | ≥ 0.80 | core | 0.869 | 0.837 | 0.653 (f) | 0.664 (f) | 0.770 (f) | **0.749 (f)** |
| L100 | 6-10 | core | 7 | 12 (f) | 9.5 | 8.5 | 11 (f) | **12.5 (f)** |
| L250 | 13-24 | core | 14 | 29 (f) | 21 | 26.5 (f) | 24.5 (f) | **24.5 (f)** |
| amps | 0 | core | 0 | 0 | 0 | 0 | 0 | 0 |
| throws | 0 | core | 0 | 0 | 0 | 0 | 0 | 0 |
| group | ≥ 30 | core | 63 | 49.5 | 16.5 (NF) | 56 | 51.5 | 35 |
| exposed | ≤ 0.006 | core | 0.004 | 0.022 (NF) | 0.015 (NF) | 0.005 | 0.005 | 0.002 |
| ahead_share | ≥ 0.75 | core | 0.788 | 0.562 (NF) | 0.763 | 0.819 | 0.800 | 0.810 |
| spawn_kills | ≥ 40 | core | 59.6 | 16.5 (NF) | 40.3 | 64.7 | 62 | 66.0 |
| first_anchor | 1800-1880 | core | 1858 | 1843.5 | 1856.5 | 1828 | 1825 | 1831 |
| tb_share | ≥ 0.80 | core | 0.929 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| L_lead100 | -5 to 0 | | -2 | 3.5 (NF) | 1.5 (NF) | 1.5 (NF) | 4.5 (NF) | 5 (NF) |
| eng_prog300 | 0.30-0.45 | | 0.381 | 0.564 (NF) | 0.534 (f) | 0.492 (f) | 0.505 (f) | 0.495 (f) |
| first_hit | ≥ 0.80 | | 0.897 | 0.503 (NF) | 0.734 (f) | 0.903 | 0.894 | 0.927 |
| alone | ≤ 0.10 | | 0.092 | 0.068 | 0.054 | 0.054 | 0.045 | 0.044 |
| ahead_win | ≥ 0.90 | | 0.969 | 0.733 (f) | 0.927 | 0.973 | 0.957 | 0.964 |
| anchors | ≥ 2 | | 6.1 | 1.8 (f) | 2.5 | 2.7 | 3.1 | 3.1 |
| anchor_games | ≥ 0.60 | | 0.70 | 0.50 (f) | 0.60 | 0.60 | 0.70 | 0.75 |
| L_total | ≥ 250 | | 493 | 186.5 (NF) | 216.5 (f) | 269.5 | 278 | 294.5 |
| isl_rounds | ≤ 400 | | 202.5 | 134.5 | 126.5 | 359 | 472 (f) | 423.5 (f) |
| mn100 | 216-360 | | 288 | 410.5 (f) | 312.5 | 333.5 | 359 | 356 |
| **victim (g_iter0) wins** | 2-10 of 20 | | 12/40 | 3/4 | 5/10 | 5/10 | 3/10 | **6/20** |
| core faithful / on target | 11 / ≥ 9 | | 11 / 11 | 6 / 5 | 9 / 8 | 11 / 9 | 11 / 8 | **11 / 8** |
| secondary faithful | ≥ 5 of 10 | | 10 | 6 | 9 | 9 | 9 | 9 |

**v3 passed the fidelity rules on its 10 quick cells** (11 faithful, 9 on target), but g_iter0 won 5 of 10 there.
v4 fixed the late economy and the anchoring, which bought strength, and it pushed L100 and L250 just over their upper
bounds.

**Per map (v4, g_iter0's wins of 2), beside the member against g_iter0 (match 22, one game per map):**

| | BatSignal | Cat | Cornucopia | DefaultMap | Forest | Hah | IslandHopping | MassiveL | Maze | ReverseFunnel |
|---|---|---|---|---|---|---|---|---|---|---|
| g_iter0 vs arch_blob v4 | 1 (tb_anchors) | 2 (conquest r376, r513) | 0 | 0 | 1 (tb_islands 4-3) | 2 (conquest r1283; tb_anchors) | 0 | 0 | 0 | 0 |
| g_iter0 vs britacatalin (match 22) | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 |

- **Like the member**, it loses Cat early to g_iter0's anchor rush. It wins the long maps on the r2000 island tiebreak
  after a siege: 29-147 spawn kills (Forest B only 10), and g_iter0 has 0-2 islands at the end.
- **Unlike the member**, it wins DefaultMap and Maze, where the member lost early. It also leads g_iter0 in launchers
  at r100 (L_lead100 +5 against the member's -2), which is why L100 runs high. Why it leads is not measured; fewer early
  losses is the likely cause.
- **Its three non-conquest losses are anchoring failures.**
  - BatSignal A and Hah A: 0 islands each at r2000, and it placed no anchor.
  - Forest A: 3 islands to 4.
  - In BatSignal A, mana collection stops at r1300: 19 carriers collect nothing from then on, while 158 launchers fill
    the narrow map. The HQ holds 12-192 Mn after r1800, so it builds 1 anchor and places none.

**Robustness** (all 20 fidelity games):
- census `over` = 0, `exceptions` = 0, `deaths_self` = 0, `sym_wrong` = 0 and `tele_exc_turns` = 0;
- bytecode peaks: carrier 11,403 of 12,500, launcher 9,991 of 10,000 (Maze, arch_blob on side A) and HQ 17,987 of
  20,000;
- 8,316 near misses, mostly the telemetry pad. The bot's own near-miss counter, measured before the pad, reads 2.

**Robust run** `gauntlet/20261008-192009-blob-v4-robust` (arch_blob, hash 3c54b97e654b in its provenance, against
examplefuncsplayer on 20 cells):
- **Results:** 20 of 20 wins, all at r2000, as designed (no anchor before r1820, and no conquest):
  - 17 on the islands tiebreak (2-6 islands each);
  - 3 on the mana tiebreak with 0-0 islands (Forest A, Hah A, Hah B: no anchor placed).
- **Robustness:**
  - `exceptions` = 0, `deaths_self` = 0, `sym_wrong` = 0 and `tele_exc_turns` = 0;
  - **`over` = 1**: Maze A, a launcher turn at 10,001 of 10,000 bytecodes. The bot's own overrun counter reads 0 there,
    so the limit was crossed after its last check.

**Likely cause of the overrun (not confirmed: the replay was a win and was deleted).** The only work after that check
is `Telemetry.indicator()`, which runs on the reserve that `MapMem.process` leaves (12% of the limit).
- v2 lengthened the launcher indicator extra (`,bl=`, `,oc=`, `,hp=`). The string now often exceeds 64 characters, so
  `indicatorString` takes its `lastIndexOf`/`substring` truncation path more often.
- The cheapest fix: drop those three diagnostic fields, or raise the launcher reserve. That would be v5 and needs a new
  validation.

## Strength

| run | victim | victim wins | band | coin flips | verdict |
|---|---|---|---|---|---|
| fidelity (the two runs above) | g_iter0 (e6f2fc5356c6) | 6 of 20 (0.30) | 2-10 | 0 | pass |
| `gauntlet/20261008-183551-blob-v4-strength` | c_line6 (5bc8e7e545ac) | 8 of 20 (0.40) | 2-10 | 0 | pass |

- **Where c_line6 wins:**
  - DefaultMap B (conquest r722), Cat A (r493), IslandHopping B (r460) and Hah B (r302), all by early conquest;
  - Forest A, on the islands tiebreak 1-3;
  - Hah A and both BatSignal games, on the anchor tiebreak with 0-0 islands, where arch_blob placed no anchor (the same
    late-mana stall as against g_iter0).
- **Its signature against c_line6** (informational: fidelity is judged against g_iter0 only):
  - core: 11/11 faithful, 6/11 on target (group 26 and spawn_kills 37.2 also fall under their lower bounds);
  - secondary: 9/10 faithful.
- **Robustness** across the 20 strength games: `over` = 0, `exceptions` = 0, `deaths_self` = 0, `sym_wrong` = 0 and
  `tele_exc_turns` = 0. The bot's own near-miss counter reads 4.

## Versions

- **v1.** The design as written:
  - rally at 35%;
  - `BLOB_MIN` = 12 + round/50, capped at 40;
  - one ring with overflow;
  - anchors from r1820, with no conquest.

  4 cells: g_iter0 won 3. It anchored 3 islands behind our idle blob and won BatSignal by conquest at r286. On Forest,
  194 launchers were alive at r1800, yet every engagement was on our side (victim-frame prog 0.6-0.94). The leader's
  wait rule ("half of the blob within r² 8") can never hold in a big blob.
- **v2.** Changed:
  - rally at 60%;
  - `BLOB_MIN` = 6 + round/25, capped at 30;
  - overflow to the next HQ at 14;
  - a leader wait that a big blob can satisfy;
  - island hunters from r400, which also visit the predicted (mirror) islands.

  Quick: 5/10. The losses came from carrier and launcher jams around HQs (ReverseFunnel, BatSignal: production stopped)
  and from g_iter0 besieging an HQ the blob never came back to (Forest).
- **v3.** Added:
  - the carrier crowd cap at the HQ;
  - no launcher holds by our HQ;
  - the quiet-front advance;
  - HQ HELP calls;
  - followers that advance with the leader;
  - the well re-pick each trip.

  Quick: fidelity passed (11/11 faithful, 9/11 on target) at 5/10. The losses on Hah and Cornucopia had no anchor
  placed. The late mana income had stopped: on Hah, 111 carriers were jammed around one mid-map well from r800.
  Islands still marked enemy in the slots may have added to it; that part is a hypothesis, not verified.
- **v4.** Added:
  - the carrier cap by known wells;
  - the hashed "one in k" (adamantium share);
  - stale-enemy islands as anchor candidates.

  Quick: 3/10 with 8/11 on target. The full 20 cells: 6/20 with 8/11 on target (see above).

## Remaining gaps

1. **L100 and L250 sit just over their bounds** (12.5 against ≤ 10; 24.5 against ≤ 24), and **mn_share100 just under its
   bound** (0.749 against ≥ 0.80). Each is faithful. Hitting one more on target would pass fidelity.
   - The likely levers are fewer early carriers (`CARRIER_CAP0` 3) or a later first carrier wave, and an adamantium role
     that starts at r100.
   - These are untested, so they are listed for a v5 and not applied: the budget is spent.
2. **L_lead100 +5 against -5..0.** The member is behind g_iter0 at r100 and wins later. This archetype is ahead at
   r100, probably because its launchers lose fewer of the early fights (not measured). This is the one secondary metric
   that is not faithful.
3. **Late economy on narrow maps** (BatSignal A, Hah A): mana income stops in the last third of the game and no anchor
   can be paid for. A launcher-free zone around wells, or banking 3 anchors' worth from r1600, would close it.
4. **One overrun in 60 validation games** (robust run, Maze A, a launcher at 10,001 of 10,000). The peaks in the
   fidelity and strength games are 9,991 (Maze, arch_blob on side A). The probable cause and fix are in the
   robustness paragraph above.
5. **Forest:** island tiebreaks are close (3-4 islands each). Hunters reach few of g_iter0's islands across the
   wall-split map.
