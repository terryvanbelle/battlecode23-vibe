# HANDOFF.md — current state (keep this current at every accept)

Updated 2026-10-07 ~13:00 PDT.

## Where things stand

- **Phase 0 (foundations, TRAINING_ALGORITHM §1)** nearly complete:
  - rules: engine-verified area reports in `research/rules/` (round order, actions, constants, maps census, bytecode
    runtime); `RULES.md` is being assembled from them.
  - runner: `tools/lib.sh` (`run_game`), `tools/gauntlet.sh` (parallel cells, seeds, census per game with `CENSUS=1`),
    `tools/run-dev.sh` (one diagnostic game with robot output), engine `3.0.15` with a seed patch (`tools/get-engine.sh`).
  - replay reader: `tools/replay-dump.sh` (summary, census, metrics, robot, map-at, logs, bytecode, navstats, events,
    islands, overruns), fixture-tested.
  - bot: `src/bot` foundation (no snapshot yet; the first snapshot will be `g_iter0`).
  - field: 87 entrants (`tools/field.txt`) from 148 public 2023 repos; discovery, safety scan, blind compile, dedupe:
    `BENCHMARK.md` (to be written) and `tools/bench-*`.
  - ladder replica (galaxy-lite) being built by a workflow: `tools/replica/`, `docs/replica/`.
- **Foundation bar** (TRAINING_ALGORITHM §1): beats examplefuncsplayer 206/206 on all 103 maps from both sides
  (foundation1/2); 0 overruns, 0 exceptions; symmetry wrong on Sine (fixed: HQ evidence before round 2); anchor
  logistics degenerate on some maps (fixed, being re-measured in foundation3).

## Compute

- Driver `claude-driver` (2 vCPU, 2 GB): this session; one diagnostic game at a time at most.
- VM `battlecode-dev` (us-west1-b, 8 vCPU, 31 GB, 20 GB disk), internal IP 10.138.0.3: every game in volume
  (`tools/vm-run.sh <name> '<cmd>'`, `tools/vm-tail.sh <name>`). About 9-10 games/min at 8 parallel (example bots).
- `battlecode-dev2` (us-west2-a) belongs to the paused 2024 project: never touch it.

## Gotchas a fresh reader will hit

- The 2023 engine seeds robot ids and sandboxed randomness from the map file; `-Dbc.game.seed` (our patch) varies
  spawned robots only. The final tiebreak is an unseeded coin flip: such results are recorded as reason COIN and ignored.
- An uncaught exception destroys the robot (HQs included). Every write to the shared array is re-checked at write time
  (`Comms.put`); a robot that moved can leave the write zone.
- Replays carry no robot stdout: our counters are in the indicator string (`note|ov=,ex=,nm=,sm=,sd=`).
- The bot's near-miss counter measures work before the end-of-turn map-memory fill (fill stops at 88% of the limit).
- `-Dbc.testing.debug=true` does not seem to reach the bot (debug prints never appeared); open question.
- GitHub code search returned HTTP 500 on 2026-10-07; discovery used repo search, date windows and scaffold forks.
