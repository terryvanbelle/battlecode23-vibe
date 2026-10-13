# Independent audit of the official controlled launcher block

Audited locally on 2026-10-13 UTC. No VM access, game execution, tracked edits or publication.

Artifact `official-full-loop-artifact.json`: SHA256 `4676ddf483b78d0cebd52a64dcd4f4c87f45e8692261567a1a7f48fc1587ee54`, 257,232 bytes. Response `official-full-loop-response.json`: SHA256 `6184022055c0335a6929db1e291fe783e7760fd0a01b67025f0c3ee197843b28`. Its compressed artifact decodes to the exact local artifact bytes. Response summaries match after omitting their intentionally absent `map_field_progress` lists; every artifact summary memory list equals its compact turn memory list exactly. The recorded worker elapsed time is 47.097 seconds, on `battlecode-dev`, with official engine SHA256 `5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a`. Raw archive SHA256: `34d5cdf6f80e3c24da80fbf6cf11c59f4092aea6f72191a22ba1e6d3e867ecc6`; raw files are represented here by their manifest rather than independently re-read.

The inspected `ControlledBlindGame.java` and `summarize.py` match the artifact helper hashes (`f6bccf4cb91c5fc6543b70a9993dce7ac81ba489898c0605df5d53a8bbea4787` and `79829fee2ddb282ccdb574e828ec7b769915a055c1887e88de61723e6cb93dcd`). All 15 inspected frozen base files match their artifact hashes. Source hashes are base `d62033781fbd`; periods 0/4/2/1 `43138ce60516` / `625c5733784a` / `6b6275c740cb` / `9ce6956c844b`.

## Identity, cold start and measured cost

Each arm has 31 launcher turns, rounds 2–32, after an HQ-only round 1. Round 2 includes real cold RobotPlayer initialization. The compact records independently reproduce base/zero equality in actions, cooldowns, indicators, selected memory, native bytecode counts and all common counters. The passed zero gate additionally reports exact full native-state/shared/inventory and API-trace identity, which cannot be recomputed from the compact records alone. Zero native-state digest is `836c96e85f67dd385f52a41d89842dad9a6974c5244ccc54684ca00e79ba3289`; native bytecode-vector digest is `38ecab9f4ff1c657bfa58eacc22527301a07db188073503fed4cbc191316ed8c`.

| Arm | Cold prefill work / running peak | Cold complete turn | Maximum complete turn | Blind shots / hits / damage | RNG mismatches vs base |
|---|---:|---:|---:|---:|---:|
| Base | 4,336 | 9,109 | 9,109 | 0 / 0 / 0 | 0/31 |
| 0 | 4,336 | 9,109 | 9,109 | 0 / 0 / 0 | 0/31 |
| 4 | 4,346 | 9,109 | 9,173 | 6 / 4 / 80 | 0/31 |
| 2 | 4,346 | 9,109 | 9,109 | 13 / 9 / 180 | 0/31 |
| 1 | 4,562 | 9,109 | 9,109 | 27 / 19 / 380 | 0/31 |

`G.maxBc` is measured before telemetry records and background map/field work, and is a cumulative maximum. Each arm attains its recorded maximum on the cold turn and holds it throughout this block. Thus the measured cold prefill differences are +10 for periods 4/2 (phase skipped) and +226 for period 1. These records do not contain each warm turn's unpadded prefill cost. Complete-turn counts include background planning, indicator construction and modulo-64 padding. Equal cold totals or maxima do **not** establish free work. Period 4's maximum is actually 64 above base, at round 3.

## Map and field work changes

Pending entries are MapMem entries remaining after the turn. Field entries below are `nWaves / wy`, meaning completed wave count and partial-wave row cursor; `wy=-1` means no wave currently in progress.

| Round | Pending base/0 | Pending 4 | Pending 2 | Pending 1 | Field base/0 | Field 4 | Field 2 | Field 1 |
|---|---:|---:|---:|---:|---|---|---|---|
| 2 | 51 | 51 | 51 | 52 | 0/-1 | 0/-1 | 0/-1 | 0/-1 |
| 3 | 24 | 24 | 25 | 26 | 0/-1 | 0/-1 | 0/-1 | 0/-1 |
| 4 | 0 | 0 | 0 | 0 | 0/-1 | 0/-1 | 0/-1 | 0/-1 |
| 5 | 0 | 0 | 0 | 0 | 10/-1 | 9/17 | 10/14 | 9/17 |
| 6 | 0 | 0 | 0 | 0 | 15/15 | 15/12 | 16/-1 | 15/9 |
| 7 | 0 | 0 | 0 | 0 | 19/-1 | 19/-1 | 19/-1 | 19/-1 |

At round 4 all fields still have `pending=true`; period 2 additionally has obstacle-row cursor `iy=1`, while base/0/4/1 have `iy=-1`. All fields seed and leave pending state by round 5. At round 7 every arm reaches `done=true`, 19 waves, identical field/wall/tile hashes, and keeps that state through round 32. All targets remain (1,18), symmetry candidates remain 7 and `decidedRound=-1` throughout.

Period 1 has a real early map backlog (+1 at round 2, +2 at round 3) and periods 1/4 have one fewer completed field wave at round 5 and less partial-row progress at round 6. Period 2 also changes work allocation, including **more** completed waves than base at round 6. The partial loop allocation is not a monotone cost meter. Live progress differs, then converges; final equality cannot replace the intermediate evidence. Period 1's diagnostic `MapMem.maxPending` remains 52 rather than 51 on every later turn, so complete selected memory is not byte-identical even after live planning state converges.

## Guards and reporting coverage

| Active period | Checks | Cooldown skips | Eligible / fired | Positive-counter turns with exact bs token | Minimum attack-entry bytecodes left |
|---|---:|---:|---:|---:|---:|
| 4 | 7 | 1 | 6 / 6 | 28/28, starting r5 | 6,921 |
| 2 | 15 | 2 | 13 / 13 | 30/30, starting r3 | 6,921 |
| 1 | 31 | 4 | 27 / 27 | 31/31, starting r2 | 5,624 |

Every active arm ends with zero budget skips, no-target skips and stale skips. The block exercises successful entry/scan/statistics paths and ordinary-shot cooldown rejection; it does not exercise failures at the 4,000 / 3,500 / 2,000 guards. Every blind shot has actual multiplier 1.0, rounded cost 10 and pre-CD 0. Actual next own-start CD is zero for all 45 observable blind shots (6+13+26); period 1's final round-32 shot is right-censored, with end-CD 10. Every arm preserves the four ordinary round-18–21 shots at (8,6), each for 20 damage with native CD 0→10; even their recorded attack-entry budget matches base exactly.

All 155 recorded source exception, overrun and prefill near-miss counters are zero. Emitted bs is exact on every positive-counter turn, including phase-skipped turns after firing. However, inserting bs causes the existing trailing `fo` indicator field to disappear on rounds 11–32 in **all active arms** (22 turns per arm), while base/zero retain it on all 31 turns. This is a measured reporting displacement from the 64-character truncation, even when bs is only 1; it must not be described as preserving every previous indicator field.

## Scope of the finding

The full native scheduler, real Clock, cold initialization and complete owned launcher loop establish controlled delivery and expose its planning/reporting price. They do not establish unchanged useful work, realistic firing frequency, a natural full-game basics bar or promotion. Only this one actor executes owned logic; movement is boxed, the target and enemy/allied phases are scripted, only one hidden attack-range cloud is available, terrain has no currents/wells, all shot costs are unbuffed, and each fixture stops at round 32. Once the field finishes at round 7, most observed later turns cannot price loss of ongoing planning capacity. Natural diagnostics need to preserve cold/low-headroom turns and intermediate map/field progress rather than accept matching padded maxima or final memory as a cost gate.
