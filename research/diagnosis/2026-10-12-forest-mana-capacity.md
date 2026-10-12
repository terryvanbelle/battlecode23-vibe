# Forest Mana capacity — 2026-10-12

The Forest Mana gap comes from mining additional wells. In matches 4566 and 4570, our side collects Mana only at its home well `(8,12)` through round 1000. Both opponents use the centre pair `(29,48)` and `(30,48)`. Their home-well production is comparable to ours; centre production accounts for almost all of the growing income gap.

This is a read-only diagnosis of game 4 in two existing c_mend2 panel replays, not a new experiment or a candidate promotion. Match 4566 faces NotLLeon.v7; 4570 faces britacatalin.FinalBot. Our side is A in both.

Exact collected Mana over rounds 101–250:

| Match | Our home | Enemy home | Enemy centre pair | Enemy total minus ours |
|---|---:|---:|---:|---:|
| 4566 | 719 kg | 761 kg | 903 kg | +945 kg |
| 4570 | 692 kg | 619 kg | 544 kg | +471 kg |

The enemy starts collecting at `(30,48)` in round 36 and `(29,48)` in round 38 in 4566. The first cumulative income reversal is between rounds 50 and 60, with 20 carriers alive on each side. In 4570, centre pickups begin in rounds 125 and 196; its reversal is between rounds 200 and 210, with 33 of our carriers versus 32 enemy carriers. Worker quantity does not explain these early reversals.

Over rounds 101–250, our total Mana production is 4.79 and 4.61 kg/round; the opposing rates are 11.09 and 7.75. Over rounds 251–500 those rates become 4.78 versus 13.69, and 4.68 versus 12.53. In 4570 through round 1000, enemy home production is actually 47 kg below ours: 4348 versus 4395. Its centre pair adds 6797 kg and explains the full 6750 kg lead.

The well-upgrade explanation is excluded in these recordings through round 1000. Every paired pickup is 1 kg. Every well remains unupgraded, with no resource conversions or deposits into wells. The reader found zero unpaired pickups and well transfers. Its resource totals match canonical timeline deltas in all 48 comparisons: two matches, both sides, four windows and three resources. Trips were useful for locating the initial signal, but their `collects` field is whole-trip kg across all wells/resources and their coordinate/type records only the dominant well/type. The final numbers and first-use rounds above come from actual action targets and paired signed resource changes.

The next question is whether our carriers fail to discover the centre pair or fail to select it after learning about it. These replays have no shared-array or full WELL/COMMS telemetry, so pickup absence alone cannot decide that. Before changing a bot, inspect any existing own Forest telemetry for centre-well knowledge and assignment. A Cornucopia control can validate the telemetry reader and common selection logic, but cannot establish Forest discovery timing.

The next tests should keep mechanisms separate:

1. Give the selector known home and centre Mana wells in an isolated own-source fixture. Vary home occupancy, including carriers just outside the collection footprint, while holding discovery, roles, routes and economy fixed. Check whether a surplus carrier selects the centre pair and whether home workers remain assigned productively.
2. Audit discovery/reporting separately: establish when each centre coordinate becomes known locally and in shared memory, and whether a report reaches another carrier. If centre wells are already known but never selected, target selection; if knowledge arrives late, target exploration/reporting.
3. Verify any resulting candidate on the VM against frozen own references. Record actual Mana kg by well, first centre pickup, waiting, deaths and bytecode basics before proceeding through the normal screen/panel gates. This diagnosis does not justify changing carrier production or promote an untested allocation rule.

The previously observed Adamantium route-recovery defect needs its own fixture and candidate. Changing navigation together with Mana allocation would obscure which mechanism caused a result.

An upgrade is also a separate investment: official rules require depositing 1400 of the well's own resource to raise collection from 1 to 3 kg/action. Six continuously collecting clear-cell residents would ideally gain 12 kg/round, giving a post-upgrade payback of about 117 rounds before travel, transfer cooldown, turnover and lost military spending. That ideal does not explain the observed early gap; no upgrade occurred.

The official pass-only reader used JDK 8u504 and engine 3.0.15 SHA256 `5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a`. It passed ten serialization fixtures covering signed action pairing, noncollection inventory changes, coordinate origins, upgrade flags, resource conversion and snapshots. It ran no games and loaded no opponent classes/source. Reproducible driver artifacts are under `build/codex-recovery/forest-actions-20261012T223222Z`; the combined result SHA256 is `828f3d507d3035066370df1108ef24ee87f1442da5f4538f414d2c5128b36768`. Exact input replay and helper hashes are retained in its provenance.
