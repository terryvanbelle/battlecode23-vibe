# Sampled native control helper packet

This packet preserves the exact sampled host, selector, guarded native reader and own replay parser used for the Mend2 control. The [control report](../../2026-10-13-c_mend3-sampled-control.md) explains measurements and limits; `control-evidence.json` contains compact measured evidence without deployment paths. `source-manifest.json` verifies packet source hashes. Raw replay/native tables and runtime credentials are not included.

The unchanged official jar is SHA256 `5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a`; measured runtime was Temurin8u504. Both own teams use frozen source: Mend2 `d62033781fbd`, arch_ampmid `9b1099e4e1cf`. The map is built-in Cornucopia, seed272, round limit2000. Nothing overrides seed, bot decisions, map state or bytecode limits. The host changes which robots are recorded, and the complete-game state/bytecode/footer comparison establishes identity for this measured cell.

## Zero-game preparation

`run.sh` only prepares helpers or inspects existing replays. It never launches games. All compiler, test and reader processes have explicit timeouts; outputs must use a new private directory.

```sh
JAVA_HOME=/path/to/jdk8 bash ./run.sh --prepare /path/to/repo /tmp/mend-sampled-prepare-new
```

Local source-built API fixtures require the explicit `--prototype` label:

```sh
JAVA_HOME=/path/to/jdk8 bash ./run.sh --prepare --prototype /path/to/repo /tmp/mend-sampled-prototype-new
```

Preparation compiles host/readers and private synthetic calibration code. It runs 18 host checks, 6 instrumented cache/metering checks, 39 native-parser fixtures, 17 selector fixtures and 17 selected-coverage/scope fixtures. No game or real replay selection occurs. The cache fixture demonstrates why unsampled robots retain non-null no-op profilers: a null first loader caches classes without later profiling hooks. Prototype preparation is not official cost or gameplay evidence.

## Inspect the preserved control

The exact off and sampled on replays, plus the sampled host's `sampling.json`, remain in owned runtime artifacts. Supply those existing files; their replay hashes are enforced. At least 3GiB available RAM and 2GiB free disk are recommended for the 2GiB bounded readers.

```sh
JAVA_HOME=/path/to/jdk8 bash ./run.sh --inspect /path/to/repo /tmp/mend-sampled-inspect-new \
  /path/to/preserved-off.bc23 /path/to/sampled-on.bc23 /path/to/sampled-game
```

Inspection copies inputs into the new output, recomputes complete state and metered-bytecode fingerprints and terminal result, then parses native events and ordinary own telemetry. Costs are gated by exact paired identity, uncapped complete selected launcher traces, cumulative `ex=0` through final recorded turn, no exception death, and aligned native/replay turn counters. The final scope gate additionally requires a completed owned-target recheck and its same-turn march/pickObjective/Launcher tail. A positive footprint alone does not supply that method scope. Invalid or capped data remains censored.

`OwnLauncherSelector.java` can independently read the preserved off replay after preparation. It pins the off hash and ranks three to five supported own IDs using fresh non-centre healing OBJ events and end-round HP/island proxies. Its default output IDs were 13460,11979,12422. These are selected lifetimes, not random or representative workload samples. Selection proxies do not establish sensed/shared knowledge, blocked-nearest or fallback availability, and no native event-volume forecast is inferred from off-turn totals.

The source `SampledProfileHost.java` permits actual games only on `battlecode-dev`, JDK8u504 and the pinned official jar. A game launcher is deliberately outside this replay-inspection packet. Any subsequent experiment must use the normal shared slot/time/resource bounds, preserve the off control, validate complete off/on identity, and report selected-ID changes after candidate divergence. `validate_candidate.py` provides the separate candidate-package/off-completion/selected-ID coverage gate; it is not used to relabel this Mend2 evidence.

The summary keeps nonsampled robots as missing-profile denominators. Its overall observed-frequency fields are therefore lower bounds; they must not become population cost weights. Reported method costs and fallback/tail/target/healing context concern usable selected lifetimes only. A fresh same-turn kind3 OBJ is a positive target witness in the frozen own source; missing or unchanged OBJ leaves delivery unknown. Repeated healing windows can overlap and do not attribute HP causally to fallback. This packet establishes the measurement route, not a candidate result or promotion.
