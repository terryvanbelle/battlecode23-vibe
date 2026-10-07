# BENCHMARK.md — the external field

## Rules (binding)

1. **External bots' source is never read.** They are discovered by script, cloned sparsely (Java sources and build
   metadata only) to `~/projects/vibe/bc23-benchmarks/` outside this repo, classified by *counting* files that use
   2023-only API names, compiled blind (`tools/bench-compile.sh`, diagnostics to log files only, `javac -proc:none`), and
   scanned for risky API patterns by count (`tools/bench-scan.sh`); a hit is ruled in or out from the matching line only.
2. Their games and replays may be studied freely. Tactics they beat us with are recorded.
3. Battlecode 2023 post-mortems are never read, first- or second-hand.

## Discovery (2026-10-07)

| step | count |
|---|---|
| GitHub repository search (names, descriptions, topics, creation and push date windows) + forks of `battlecode/battlecode23-scaffold` (`tools/bench-discover.py`) | 864 candidates |
| web sweep (search engines, GitHub topic and user pages, community listings; URLs only) | 22 more |
| repos whose Java uses 2023-only API names (`tools/bench-fetch.sh`) | 148 |
| excluded: official engine repo and 15 forks of it (their only 2023 code is the example bots), our own repo, an AI-environment repo | 18 |
| compiled bot packages (`manifest.tsv`) | 968 |
| field entrants (`tools/field.txt`, `tools/bench-roster.py`) | 87 |

GitHub's code-search API returned HTTP 500 for every query on 2026-10-07, so code search could not be used.

**Choosing each repo's bot.** Two rules disagree on about a third of repos: names alone (final > qualifier > sprint >
highest version) and names-then-last-commit-date (from GitHub commit metadata per package path,
`tools/bench-dates.py`). Both picks enter the field; byte-identical packages (archive copies, forks) are merged by a hash
of their class files (`tools/bench-hash.py`), keeping the team's own repo name. Entrants excluded by hand are listed with
reasons in `tools/field-exclude.txt` (a bot that resigns at round 200).

**Security.** 12 repos had risky-pattern hits: test files (never compiled), tooling in non-bot repos (excluded), and
three single unused imports (`java.nio.file.Path`, `java.lang.reflect.Array`, `java.lang.reflect.Constructor`) that the
engine sandbox rejects at load time anyway. No risk found. Compilation runs no code (`-proc:none`); bots run inside the
engine's instrumented sandbox.

**Smoke test** (2026-10-07, 61 entrants then, examplefuncsplayer vs each, both sides): no duds, no instrumentation
failures; one bot resigned at round 200 in both games (excluded). Four entrants lost both games to examplefuncsplayer
(weak early bots; kept). A second smoke test covers the entrants added by the two-rule selection.
