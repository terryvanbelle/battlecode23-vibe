# Forest carrier routes and capacity — 2026-10-12

The late Forest economy loses productivity before it loses worker count. Navigation deserves a delivery test,
but the long stall at `(5,20)` is an adamantium route, and a simple second-return veto does **not** repair it.
Keep c_mend2 validated. Do not repeat the carrier-cap or resource-share changes on this evidence.

## Field evidence

Existing field matches 4566 game4 (NotLLeon) and4570 game4 (britacatalin), our sideA, have favorable launcher
exchange but mana collection8761/27808 and7570/24932. At r1000 our actual living carrier fleets are95/96.
Late decoded carrier turns are72.19%/77.87% gathering and6.33%/4.54% collecting. These are state labels;
gathering does not prove progress toward a known target.

The income gap starts with comparable worker counts. Against NotLLeon at r150, we have31 carriers against27,
but cumulative mana627/1003; r100–150 collection is4.64/9.72kg per round. Against britacatalin at r250 both
have36 carriers, but cumulative mana1063/1381; r150–250 rates are4.66/8.91kg per round. Later build counts
cannot explain those earlier productivity differences. Trips, capacity, well upgrades and multiple collection
sites must be distinguished before choosing a repair.

The raw reader found ABA endpoints on19.1%/14.8% of moving gathering turns. Equal post-current endpoints can
hide two legal moves, and end-of-round free neighbours do not establish `canMove` during the robot's turn.
The three hundreds-of-round stalls at `(5,20)` are empty-cargo carriers:

| Match / carrier | Born | Long equal-endpoint interval | First actual collection |
|---|---:|---|---|
|4566 /12004|992|1009–1350,342 rounds|1358, adamantium `(9,21)`|
|4570 /11476|928|933–1349,417 rounds|1359, adamantium `(9,21)`|
|4570 /11128|1696|1701–1997,297 rounds|None before game end|

Their birth IDs satisfy our post-r200 adamantium assignment. For the first two, the actual pickup confirms the
resource and site. The third's chosen site and all three carriers' shared-memory contents remain unknown.
The missing field indicator dots cannot be reconstructed by extracting the same replay again.

## Official map geometry

A headers-only probe compared both replay game4 maps with the official engine's built-in Forest: all have terrain
SHA256 `6480cebb8fce2fc5b7133a799eec232f86643f56741cf02164c5be6a8abf7868`, four checks passed, zero rounds walked.
Cells x6,y18–22 form a wall east of the hotspot. The clear cells x4–5,y18–22 have no clouds or currents, so a
local current alone does not explain that endpoint stall.

The home mana well `(8,12)` has six passable collecting squares, all clear. At a standard rate1 well with no
boosts or same-round vacancy reuse, six uninterrupted resident collectors supply6kg per round. An upgraded
rate3 well has a corresponding18kg reference. The central mana pair `(29,48)`/`(30,48)` shares twelve distinct
collecting cells, including two clouds and four currents: do not add two nine-cell footprints as independent
capacity. Its simple stationary rate1 benchmark is11.667kg per round, before current effects.

These are conditional geometry benchmarks, not universal throughput ceilings or bot-knowledge claims. Well
upgrades, aura changes, turnover, death and actor ordering require actual replay evidence. Upgrading a well
requires1400 of its own resource deposited, per RULES.md §3.2; its current upgrade state is not the initial map.

## Native cancellation fixture

An owned host fixture invokes the frozen c_mend2 navigation and carrier routines against the official native
controller, with Forest terrain, prescribed map memory and stationary own blockers. It runs12 cases and366
assertions; no competitive games or opponent code. Host `Clock` supplies an ample synthetic budget: **there is
no instruction meter or bytecode-safety claim**.

With downhill and same-wave steps blocked, toward `(9,21)` the first move legally detours `(5,20)`→`(5,19)`
and the second returns `(5,19)`→`(5,20)`. Native movement cooldown goes0→5→10. The subsequent unjam routine
cannot move on that turn. This confirms a possible mechanism, not a reconstruction of the field robot's turn.

A controller veto of second moves back to the turn's starting square preserves all six paired first detours and
four tested complete open/downhill-only action paths, whose first collection is native round8. Veto checks still
occur on common paths; action identity does not imply identical API reads or costs. Under persistent downhill
and same-wave blockers, both the original and the veto fail to collect for64 turns. The veto changes a one-turn
cancellation into a longer cycle and suppresses the original's one observed unjam. **Do not promote this veto.**

The next route variant must reach and collect at the destination under those blockers, preserve the working
paths, then show instruction headroom and whole-game economy delivery in fixed own-versus-own controls.

## Reproducible artifacts

Exact field measurements, header results, owned Java sources and the92,058-byte native trace are in
`2026-10-12/carrier/`; `2026-10-12/manifest.json` supplies exported checksums. Official jar SHA256 is
`5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a`, VM JDK8u504.
Native source SHA256 `33077a92b79224526e3fd912e61fe028856027b97c8beb255787486cbfda3f05`;
native result SHA256 `e79d4c9f1a1194a9d0b6b34b1300ab3640f9d652c0ce729b54a0de9fb4f2a207`.
Private native artifact directory: `build/codex-recovery/carrier-native-20261012T221624Z` on driver and compute VM.

For CSV analysis, ReplayDump's `trips.collects` is **kilograms**, not action count: it adds each action's amount.
It includes all pickups in a trip but records only the dominant well/type. Do not use that coordinate to attribute
every kilogram, or assign a trip spanning an interval wholly to its first collection round.
