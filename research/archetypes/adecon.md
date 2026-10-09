# arch_adecon: S5 archetype (adamantium economy, light early army, long game)

Design: `docs/ARCHETYPES.md` section 4.2. Package `src/arch_adecon/` (package `arch_adecon`). It is a fork of
`src/c_line6` (5bc8e7e545ac) and its telemetry build tag is 102. **Code hash b774bf16efe4** (v4, the measured version).
Members modelled: battlecode-archive.Sprint1 and reeceyang.v5anaconda. yaonam's THROWER variant is not built.
It was built only from observed behaviour (CLAUDE.md rule 3), using these sources:
- the survey rows of the 120 member panel games;
- the member timelines in `matches/{19,20}/extract/timeline.csv`;
- `research/matches/19.md`;
- `tools/replay-dump.sh --map-at` on `gauntlet/20261008-011350-panel1-g_iter0/replays/19.bc23`.

**Verdict (my computation, `tools/archsig.py` does not exist yet): INVALID on fidelity by one metric. The 4-version
budget is spent.**

| check | rule | result |
|---|---|---|
| fidelity | every core metric faithful | 11 of 11: pass |
| fidelity | at least 75% of core metrics on target | 8 of 11 (73%): **fail** |
| fidelity | at least 50% of secondary metrics faithful | 12 of 14: pass |
| strength | g_iter0 wins 10-17 of 20 | 13 of 20: pass |
| strength | c_line6 wins 10-17 of 20 | 13 of 20: pass |
| robustness | 20 of 20 against examplefuncsplayer, and no overruns, exceptions, self-deaths or wrong symmetry in any of the 60 games | pass |

## What it does

The constants are in the `ARCHETYPE arch_adecon (S5)` block at the top of `C.java`. Each one carries the observation
that set it.

**Opening and economy**
- On r1 each HQ builds 4 carriers. Launchers start at r5. This is Sprint1's opening: CCCC in 40/40 games, first
  launcher at r5.
- Until r300, 1 carrier in 2 mines adamantium (by robot id), and carriers do not switch role by HQ stock. After r300,
  the base's balance by HQ stock applies.
- Everything affordable is spent. There is no early carrier cap and no launcher cap: carriers come first, then
  launchers whenever Mn ≥ 45.
  - **This deviates from the design sketch on purpose.** Members never float resources and never cap. In matches 19/7
    and 19/9, Sprint1 banks only 30-350 Ad and 90-250 Mn at every 50-round sample. It built 145 carriers and 155
    launchers by r900 on MassiveL, and reeceyang had 188 launchers alive at r750 on Maze.
  - The army is light only early, because the economy leans on adamantium and launchers are lost.
  - The sketch's live-launcher cap still exists, behind `C.AE_L_CAPPED = false`. It estimates live launchers from team
    build counters in Comms slots 62-63 and exact deaths. In the one diagnostic game the cap was on (Hah), it starved
    the army: 2 alive at r100 and 0 from r180.
- Live-robot bound: 40 + 20 per known well. The base's is 30 + 15.

**Amplifiers**
- From r150, one per 3 launchers the HQ has built.
- At most 2 per HQ, plus 1 per 250 rounds after r500.

**Movement before r900: own half only**
- A location counts as our half when it is nearer our nearest HQ than the nearest predicted enemy HQ.
- Objectives, in order:
  1. fresh enemy sightings in our half;
  2. enemy-held islands in our half, which launchers neutralise by standing on them;
  3. a post.
- A post is one of our anchored islands (garrison) or a guard point. The guard point lies 20% of the way to the enemy
  before r100 and 45% after, scattered by up to 9 tiles. Each launcher redraws its post at random every 50 rounds.
- From r900, launchers use the base objectives: enemy islands, then the enemy HQ.
- There is no cohesion code (`C.ARMY` and `C.MICRO2` are off).

**Micro ("brave", `C.AE_BRAVE`)**
- With the action ready, a launcher steps in to fire whatever the local count, at the edge of range. Threats only break
  ties.
- With the action spent, it holds its tile unless a step lowers the threat by 2 or more.

**Islands**
- `ANCHOR_START = 520`. Carriers take anchors to the nearest neutral island, preferring our side (base code).

## Signature against g_iter0

Fidelity run `gauntlet/20261008-151938-adecon-v4-fid`: g_iter0 against arch_adecon on 20 cells (10 panel maps × 2
sides, seed = map), with `MAXJOBS=2 CENSUS=1 KEEP_ALL=1`. It was extracted on the VM.

Metrics come from `<scratchpad>/adecon_sig.py`, which uses the survey's `sig.py` column definitions and the section 2
aggregations. Run on Sprint1's 40 panel games as a known-answer check, it reproduces the design's member values: ad100
259.5 (survey 260), mn100 247, exposed 0.072, dmgc 13.4, first_anchor 566, amps 4.725, loss_maps4 0.88.

Marks: `(f)` = faithful but off target, `(NF)` = not faithful. v1-v3 are `--quick` runs (10 cells: one side per map,
alternating). v4 is the full 20.

| id | target | core | members | v1 | v2 | v3 | v4 (20) |
|---|---|---|---|---|---|---|---|
| mn_share100 | 0.25-0.55 | core | 0.33-0.55 | 0.404 | 0.393 | 0.392 | 0.373 |
| ad100 | 250-390 | core | 254-390 | 386 | 372 | 410 (f) | 356 |
| mn100 | 170-250 | core | 172-247 | 258 (f) | 200 | 241 | 242 |
| L100 | 6-9 | core | 6-9 | 8.0 | 6.0 | 3.5 (NF) | 5.0 (f) |
| L250 | 4-8 | core | 4-8 | 19.5 (NF) | 18.5 (NF) | 12.0 (NF) | 10.0 (f) |
| eng_prog300 | ≥ 0.50 | core | 0.51-0.74 | 0.624 | 0.657 | 0.644 | 0.657 |
| press250 | ≤ 30 | core | 0 | 0 | 0 | 0 | 0 |
| exposed | ≥ 0.06 | core | 0.071-0.077 | 0.035 (NF) | 0.036 (NF) | 0.083 | 0.071 |
| first_anchor | 530-950 | core | 534-948 | 528 (f) | 546 | 554 | 546 |
| amps | 4-12 | core | 4.7-11.3 | 7.1 | 8.0 | 7.0 | 6.35 |
| loss_maps4 | ≥ 0.60 | core | 0.86 | 0.33 (NF) | 0.50 (f) | 0.75 | 0.571 (f) |
| mn100_mr | 250-520 | | 250-520 | 378 | 345 | 368 | 346.5 |
| Lb100 | 12-19 | | 12-19 | 16.5 | 17.0 | 17.5 | 17.0 |
| C100 | 6-15 | | 6.5-14.5 | 14.0 | 12.0 | 15.5 (f) | 11.5 |
| dmgc | ≥ 13 | | 13.4-21.1 | 9.1 (NF) | 10.1 (f) | 16.8 | 14.5 |
| first_hit | ≤ 0.40 | | 0.27-0.35 | 0.506 (NF) | 0.567 (NF) | 0.468 (f) | 0.436 (f) |
| group | ≤ 5 | | 3-4 | 13.5 (NF) | 13.5 (NF) | 8.5 (NF) | 7.0 (NF) |
| ahead_share | ≤ 0.45 | | 0.21-0.41 | 0.573 (NF) | 0.528 (f) | 0.368 | 0.371 |
| ckill300 | ≤ 5 | | 3.5-4.4 | 6.6 (NF) | 5.2 (f) | 2.9 | 3.2 |
| first_A | 150-260 | | 159-176 | 156 | 156 | 151 | 156.5 |
| spawn_kills | ≤ 5 | | 0.6-5 | 6.2 (f) | 3.4 | 1.9 | 1.2 |
| anchors | 1.5-3 | | 1.9-2.3 | 3.9 (NF) | 3.9 (NF) | 2.8 | 3.0 |
| anchor_games | 0.20-0.45 | | 0.23-0.42 | 0.70 (NF) | 0.70 (NF) | 0.60 (NF) | 0.60 (NF) |
| first_press | ≥ 150 | | 150-262 | 588 | 325 | 375 | 525 |
| loss_round | ≥ 900 | | 1074 | 937 | 1043 | 1166 | 937 |
| **victim (g_iter0) wins** | 10-17 of 20 | | 0.69 | 4/10 | 4/10 | 6/10 | **13/20** |
| core faithful / on target | 11 / ≥ 9 | | | 8 / 6 | 9 / 8 | 9 / 8 | **11 / 8** |
| secondary faithful | ≥ 7 of 14 | | | 7 | 10 | 12 | 12 |

**Per map (v4, g_iter0's wins of 2):**

| | BatSignal | Cat | Cornucopia | DefaultMap | Forest | Hah | IslandHopping | MassiveL | Maze | ReverseFunnel |
|---|---|---|---|---|---|---|---|---|---|---|
| g_iter0 vs arch_adecon v4 | 0 | 2 | 0 | 2 | 2 (tb r2000) | 2 | 1 | 0 | 2 | 2 |
| g_iter0 vs Sprint1 (match 19) | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 |
| g_iter0 vs reeceyang (match 20) | 1 | 1 | 1 | 1 | 0 (tb) | 1 | 1 | 0 | 0 | 0 |

- The members' losses to g_iter0 are early conquests (r240-400). Their wins come late, by conquest at r775-1661 or by
  tiebreak, once their uncapped economy has outgrown g_iter0's: 50-190 launchers alive by r750.
- v4 has the same shape: g_iter0 wins Cat, DefaultMap, Maze and one Hah at r263-365 (the other Hah at r615).
- It differs in three places:
  - it holds Cornucopia, where both members lose;
  - it loses ReverseFunnel, which both members win;
  - it loses Forest to the r2000 island tiebreak.

**Robustness** (all 20 fidelity games): census `over` = 0, `exceptions` = 0, `deaths_self` = 0, `sym_wrong` = 0 and
`tele_exc_turns` = 0. Bytecode peaks are carrier 11,403 of 12,500, launcher 9,416 of 10,000 and HQ 17,988 of 20,000,
with 3,219 near misses in total (these do not gate). The symmetry stays undecided all game on some maps (the launchers
never see the far half), which is harmless.

**Robust run** `gauntlet/20261008-153205-adecon-v4-rob` (arch_adecon against examplefuncsplayer, 20 cells): 20 of 20
wins, all by conquest at r623-1039 (anchors start at r520). `over` = 0, `exceptions` = 0, `deaths_self` = 0 and
`sym_wrong` = 0, with 2,833 near misses.

## Strength

| run | victim | victim wins | band | coin flips | verdict |
|---|---|---|---|---|---|
| `gauntlet/20261008-151938-adecon-v4-fid` | g_iter0 (e6f2fc5356c6) | 13 of 20 (0.65) | 10-17 | 0 | pass |
| `gauntlet/20261008-154647-adecon-v4-str` | c_line6 (5bc8e7e545ac) | 13 of 20 (0.65) | 10-17 | 0 | pass |

- In the strength run, c_line6 lost BatSignal A, Cornucopia on both sides, Forest B (tiebreak), IslandHopping B and
  MassiveL on both sides.
- The archetype rows show `over` = 0, `exceptions` = 0, `deaths_self` = 0 and `sym_wrong` = 0.
- The members' victim share is 0.69, and against g_iter0 0.70.
- The archetype never reaches 15 of 20 against either build, so section 3.7 does not apply.

## Data

- **Runs on the VM.** All runs are on battlecode-dev under `gauntlet/<run>/`. The fidelity runs keep their replays and
  `extract/` directories there.
- **Local copies.** Each run's `results.csv`, `census.csv`, `cells.txt`, `provenance.txt` and `summary.txt` were
  fetched into the local `gauntlet/` (ignored by git). The v4 fidelity run also has its per-game signature rows,
  `sig.csv`.
- **Measurement script.** It is not in the repo: `adecon_sig.py` in the session scratchpad. Re-measure with
  `tools/archsig.py` once it lands.
- **Partial runs.** The robust runs of v1 (`20261008-144340-adecon-v1-rob`) and v2 (`20261008-145732-adecon-v2-rob`)
  were stopped after 2 and 4 games (all wins) when the next version superseded them.

## Versions

The pre-v1 version (4291dfaab873) followed the design sketch literally: a live-launcher cap of 6 + round/100, 2 in 3
carriers on adamantium, and the base's early carrier cap. Its one driver diagnostic game, on Hah, starved the army
(2 launchers alive at r100) and floated 400-800 Ad. The ad100 was 451 against a target of 250-390. It was withdrawn
before its VM run.

| version | hash | change | result |
|---|---|---|---|
| v1 | 2106ab883908 | Full spending, no caps; 1 in 2 carriers on adamantium; launcher posts at wells, islands and a guard point at 35%, redrawn every 100 rounds | g_iter0 won 4 of 10. The archetype ambushed from its posts: group 13.5, ahead_share 0.57, exposure 0.035. |
| v2 | b298f9cc8959 | Brave micro (when ready); posts redrawn every 50 rounds and scattered by 6; ANCHOR_START 500 to 520 | g_iter0 won 4 of 10. Little changed: group 13.5, exposure 0.036, L250 18.5. |
| v3 | 82321027003e | Posts only at the guard point (now 45%) and our anchored islands; brave hold when the action is spent | g_iter0 won 6 of 10. Exposure 0.083, ahead_share 0.37, loss_maps4 0.75; but L100 fell to 3.5 (early fights at midfield). |
| v4 | b774bf16efe4 | Guard point at 20% before r100; scatter 9 | g_iter0 won 13 of 20; core 11/11 faithful, 8/11 on target |

## Remaining gaps

**Core metrics off target** (all within the 25% tolerance):
- **L100 = 5.0** against 6-9. Launchers built by r100 are on target (17), but 12 of them are lost; Sprint1 loses
  about 10 of 19.
- **L250 = 10.0** against 4-8. This is exactly at the faithful bound. It is high in the games the archetype survives
  and the members did not (Cornucopia, IslandHopping).
- **loss_maps4 = 0.571** against ≥ 0.60. g_iter0's 7 losses were BatSignal 2, MassiveL 2, Cornucopia 2 and
  IslandHopping 1. Cornucopia and IslandHopping are maps both members lose to g_iter0. One Cornucopia game flipped
  would pass it.

**Secondary metrics not faithful:**
- **group = 7.0** (≤ 5). Long games grow groups with a median of 9-37 launchers; short games sit at 2-4.
- **anchor_games = 0.60** (≤ 0.45). 12 of 20 games placed an anchor: every game that lasted past r620 except
  ReverseFunnel at r636. The members' games are shorter more often: they lose 69% of them, early.

**Mechanism not reproduced:**
- The members win ReverseFunnel and Forest: by conquest at r849-1661, or reeceyang's Forest by the r2000 tiebreak.
  v4 loses both to g_iter0: ReverseFunnel by conquest at r636 and r1364, Forest by the r2000 tiebreak.
- v4 holds Cornucopia instead.
- The design marks this map concentration as emergent and unconfirmed when it fails (section 4.2, Risk).

**Next step, if a v5 is allowed (it would exceed the 4-version budget):**
- Keep the guard point at about 10-20% until about r150, so that L100 rises and L250 falls.
- Move a share of launchers forward after that.

**Stale comment:** the javadoc of `C.AE_MIDFIELD_FROM` still says "then our and neutral islands on our side". Since v3
the order is: enemy-held islands on our side, then the post. I left it unchanged so that the code hash stays the one
that was measured (b774bf16efe4). Fix it with any next code change.
