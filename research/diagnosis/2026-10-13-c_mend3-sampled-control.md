# Mend2 sampled native control: measured cost scope recovered

The official engine now supplies complete, usable native traces for three explicitly selected own launchers in one frozen control cell. The sampled replay matches the preserved profiler-off replay in full state fingerprint, metered-bytecode fingerprint and terminal result. This recovers a measurement route after whole-team profiling exhausted the 2,000,000-OPEN cap; it does not establish a Mend3 result or population workload weights.

The cell is `c_mend2` (`d62033781fbd`) A versus our `arch_ampmid` (`9b1099e4e1cf`) B on unmodified built-in Cornucopia, seed272, round limit2000. Runtime was Temurin JDK8u504 and the official 3.0.15 jar SHA256 `5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a`. The sampled control completed at `2026-10-13T00:08:52Z`. Its A win at round2000 repeats the preserved off result; this own diagnostic cell is not a panel or promotion verdict.

## Recording policy and validation

Host code replaces the official player providers' profiler collections before robots spawn. IDs `13460`, `11979` and `12422` receive normal native profilers for their entire lifetimes. Every other robot receives a non-null no-op profiler. This preserves `factory.createLoader(profiler != null)` and the team's cache of transformed class bytes: returning null for an early HQ can silently cache classes without hooks for later sampled launchers. Official zero-game preparation passed 18 host/API checks, 6 cache/metering checks and 17 read-only selector fixtures. The cache fixture retains40 events and332 metered bytecodes with zero pending debt; the complete-game identity check supplies the stronger gameplay validation for this cell.

The own stream has 266,778 OPEN events and three profiles, with no truncation. All three traces are valid and complete, align to their recorded turn counters, and observe cumulative `ex=0` through their final recorded turn at r2000. No selected robot has an exception death or recorded overrun. The other team has no recorded native profiles. Nonsampled robots remain outside measured native cost scope.

| Own ID | Recorded turns | Native OPEN events | Final exception coverage |
| --- | ---: | ---: | --- |
| 13460 | 1185 | 147313 | zero through r2000 |
| 11979 | 649 | 74151 | zero through r2000 |
| 12422 | 434 | 45314 | zero through r2000 |

IDs were selected from the pinned off replay by observed own healing-objective transitions, low boundary HP from r250 near publicly owned islands, wounded turns and deterministic ties. These are deliberate diagnostic samples. Public end-round HP, positions and island ownership do not establish sensed enemies, cooldown readiness, shared-array knowledge, blocked-nearest cases or fallback opportunities. The off replay supplies no native event-volume forecast.

## Costs in these selected lifetimes

Native inclusive costs include nested work and charged API/library work, and exclude caller argument/invocation setup. Terminal forced closures and unusable traces are censored.

| Interval | Count | Median | p90 | Maximum | Sum |
| --- | ---: | ---: | ---: | ---: | ---: |
| `mendUpdate` | 2268 | 18 | 19 | 693 | 59026 |
| following `march` | 1758 | 1626 | 4697 | 5280 | 3632205 |
| `pickObjective` inside march | 1758 | 1019 | 4052 | 4786 | 2576336 |
| `Launcher.run` | 2268 | 2216 | 5275 | 6123 | 5482156 |
| remaining `Launcher.run` after mend | 2268 | 1729 | 4667 | 5506 | 4014334 |

All 2268 `mendUpdate` intervals have aligned entry/return budgets. Its mean inclusive cost is 26.0 bytecodes and most calls return cheaply from the due check. The selected scope contains 16 completed owned-target scan witnesses with a nested `nearestEnemy` and measurable same-turn march, objective selection and enclosing Launcher tail. These prove that an owned target was evaluated. They do **not** prove a blocked nearest target, an available safe second target, or fallback delivery.

Five retained scan examples leave 6316,6287,7229,7274 and7331 bytecodes after the measured Launcher tail. These are descriptive observations, not a return floor: the tail alone reaches 5506 bytecodes elsewhere in this sample, and later RobotPlayer/comms/background-fill work is outside that containing-method tail. The method's 6000 scan reserve and 7500 fallback admission threshold cannot establish universal full-turn safety.

The next prepared diagnostic uses frozen `c_mend3` (`db9f54f47fea`) in two candidate off/on games, reusing this measured Mend2 control without another control game. Candidate off/on identity is mandatory before costs are used. The same three IDs remain conditional after decision/spawn divergence; missing or changed-type IDs leave the selected scope incomplete instead of being replaced. Native fallback entry, fresh healing-target witnesses, subsequent march/objective work and remaining Launcher tail will be measured only from uncapped, complete, final-zero-exception, aligned traces. No candidate measurement or promotion is claimed here.

## Reproduction and artifact identity

[The helper packet](2026-10-13/mend-sampled-control/README.md) contains exact host/selector/native readers, bounded zero-game preparation and replay inspection instructions, hash manifests, and [compact control evidence](2026-10-13/mend-sampled-control/control-evidence.json). It omits raw traces, credentials, deployment settings and private VM paths.

| Artifact | SHA256 |
| --- | --- |
| preserved off replay | `6544c8b768bd53579dc06473de148e464edd5262c663e7968e9586b630ec436b` |
| sampled on replay | `71863f3f3e7069ee7a377d5c5faa670992e3738411ebb93186000adb3f06af78` |
| sampled control provenance | `42a5b11ec69d5d6c9ecb5b3ab419856f47c94f7f2599d547c8910c60e0abcad6` |
| sampled host source | `2848b63dfff7ef84f8578945794e80d94f251bc18713ecebf1ffd1c8fd5e7e62` |

State fingerprint: `9676e3f4731b44a8a84aa6bd0a2cd89a677fdf5e`; metered-bytecode fingerprint: `ce1b2c67ffb5c388e5afb44b372b8fe6abc0e8e0`. Both fingerprints and the terminal footer agree exactly between the two control replays.
