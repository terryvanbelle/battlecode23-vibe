# c_mend3: completed sampled diagnostic

The candidate added measured work without a visible benefit in this Cornucopia game. Its full world-state fingerprint matches the c_mend2 control, including the same A win at round 2000. Candidate profiler off/on replays match in state, bytecode fingerprint and footer; the control pair also passes those checks. Candidate and control bytecode fingerprints differ, as expected from the extra work.

The three preselected own launcher lifetimes (13460, 11979, 12422) provide 2,268 aligned mendUpdate intervals. Their traces are uncapped and valid, their budgets align to replay turns, and their recorded exception counters remain zero through their final recorded turn at round 2000. This is selected diagnostic evidence, with no population weighting.

| Selected inclusive cost | c_mend2 | c_mend3 | Change |
| --- | ---: | ---: | ---: |
| mendUpdate | 59,026 | 59,620 | +594 |
| Launcher.run | 5,482,156 | 5,482,750 | +594 |
| march | 3,632,205 | 3,632,205 | 0 |
| pickObjective | 2,576,336 | 2,576,336 | 0 |
| Launcher tail after mendUpdate | 4,014,334 | 4,014,334 | 0 |

One fallback-entry witness appears for launcher 11979 at round 1472: 13 direct-child Comms.read calls after nearestEnemy closes inside mendUpdate. Against the frozen own candidate source, this identifies entry into the fallback scan. The whole mendUpdate call costs 1,256 bytecodes, entering with 8,549 and returning with 7,293; its remaining Launcher tail costs 108. The one measured return above 6,000 does not establish a general return floor or whole-turn safety.

Entry, decision and delivery remain separate. The trace establishes fallback entry; it does not identify the selected island or prove that an alternative was selected. No following march or pickObjective, or usable selected-target witness, was recorded for that call. Launcher.run checks rc.isMovementReady() after mendUpdate before invoking march. Movement not being ready is a source-based explanation consistent with this trace, awaiting the bounded replay-window reader rather than a directly observed cooldown fact.

The replay records 20 healed HP from round 1472 through 1482 inclusive and no recorded death for this robot in the match. That window is context, not healing attributable to the fallback; the unchanged world-state fingerprint supplies no visible benefit over the control. No survival claim extends beyond match end.

The prospective wider trial stays closed unless actual delivery evidence changes this assessment. These results support neither promotion nor a population-level cost or opportunity estimate.

Evidence: result-evidence.json records sanitized input hashes, replay/provenance pins, identity checks, selected cost totals and the fallback witness. It omits private VM paths and worker transport metadata.
