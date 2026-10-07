# Correctness audit plan (TRAINING_ALGORITHM §4 step 1; method from the 2024 audit playbook, year-agnostic)

When: on the first accepted build after g_iter0 (g_iter1), and at every plateau.

Scope: the incumbent package, src/bot with its switches at defaults and on, every tool a verdict rests on
(tools/lib.sh, gauntlet.sh, paired.py, delivery.py, scrim-record.py, elolib.py, elo.py, basics.py, replay-dump.sh /
ReplayDump.java, bench-*.{sh,py}, vm-queue.sh, the replica under tools/replica).

Lenses (one read-only auditor each, no games, no edits):
1. dead code and unreachable branches (every switch, every guard, every counter that is written but never read);
2. rules and engine API: every engine call checked against RULES.md and the engine source, including information
   the engine gives away (ids, RobotInfo inventories, island/well sensing, turn order);
3. shared state and coordination: every Comms slot's writer, reader, staleness and clearing rule; per-robot statics
   that act as team state;
4. in-game behaviour from replays: traces of our robots in losses (state tokens, micro rates, navigation stalls,
   carrier idle, anchor logistics), each finding with replay output;
5. the measurement pipeline: identity control, provenance, census columns against the engine's own numbers, paired
   statistics, reason codes, the rating fit, the replica export.

Every finding: ID, evidence (file:line, replay output, rule line or harness output), quantified impact, fix, and a
regression test. Adversarial verifiers try to refute every finding; unverified findings are reported as such.
Follow-through: fix tool defects first and prove them with an identity control; one combined arm of the bot fixes
behind switches; delivery, then the paired gate; guards installed as tests.
