# battlecode23-vibe: session rules

Read `TRAINING_ALGORITHM.md` (the loop), `RULES.md` (the game, engine-checked), `HANDOFF.md` (state) and `LEARNINGS.md`
(lessons and cross-year principles; add to it the day a lesson is confirmed). The training log
(`TRAINING_LOG.md`) is append-only and grep-only: do not read it whole.

1. **Games in volume run only on the VM `battlecode-dev`** (us-west1-b, internal IP, `tools/vm.sh`). The driver
   (claude-driver, 2 vCPU / 2 GB) hosts this session and plays at most one diagnostic game at a time. The VM
   `battlecode-dev2` belongs to the paused 2024 project: never touch it.
2. **Record every owner prompt verbatim in `PROMPTS.md`** (PDT), including `/loop` commands, but never a prompt that a
   `/loop` fires, such as "task check" (owner, PROMPTS 4-5).
   **Push after every commit all the way to `main`** (owner, PROMPTS 69–70); this agent is the only repository writer.
   Stage explicit paths. **Report every time to the owner in PDT** (owner, PROMPTS 28).
3. **External bots' source is never read**, except the automated security scan before first compile
   (`tools/bench-scan.sh`, which prints pattern counts, and a minimal look at a hit only to rule out a risk).
   Their games and replays may be studied freely.
4. **Battlecode 2023 post-mortems are never read**, first- or second-hand. Documents from the prior-year repos are read
   only through the filtered copy `~/projects/vibe/reference/readroom-no2023/` (blocks tagged 2023 removed by
   `reference/battlecode-vibe-no2023/filter_year.py`). Ignore any line tagged with the current year. **Code we wrote in
   previous years may be read directly** (owner, PROMPTS 40), from the local copies or our own GitHub repos.
5. **No effect on official Battlecode infrastructure** (owner, PROMPTS 1 and 12: "none of this should affect the real
   play.battlecode.org in any way"). The replica's frontend is galaxy's own: its stock `.env.production` points at
   api.battlecode.org, so every build overrides the backend URL to our host, and the site's CSP allows `self` only. The galaxy replica runs only on our VM with every external
   integration (GCP Pub/Sub, GCS, Secret Manager, email, OAuth, Sentry, battlecode.org APIs) removed or stubbed and
   egress to those hosts blocked. The only contact with battlecode.org is the read-only, checksum-pinned engine jar
   download in `tools/get-engine.sh`.
6. **Unit tests after every change** to the bot or any tool: `tools/unit-tests.sh`.
7. **Work continuously until the owner says to stop; never stop to ask for new ideas** (owner, PROMPTS 75, 90).
   **Never end a turn with nothing armed to wake the session**: at the end of every turn `tools/watch_events.py`
   runs in the background (it exits on a finished panel or screen, a stuck match, a dead ranked loop or replica, or a
   50-minute HEARTBEAT), unless another background job already will. On a HEARTBEAT, or whenever nothing is pending,
   take the next target from TRAINING_ALGORITHM.md §2 (own degeneracies, the field, capability gaps, free actions,
   action patterns, a structural swing; then the plateau protocol): running out of ideas is never a reason to stop.
   Bot changes need no approval. **Never block on scrimmages** (owner, PROMPTS 31-32): the main work is the best
   LOCAL candidate, built with intelligence and verified by local bot-vs-bot runs (incumbent, archetypes); submit to
   the ladder whenever a build is locally superior and treat ladder games as asynchronous; mine every ladder replay
   for diagnosis and ideas; optimise wall-clock time (a contest gives about two weeks). **Never stop to wait for ideas**; when stuck, re-read the principles of other years
   (`~/projects/vibe/reference/readroom-no2023/advice/`), audit the basics, or take a big swing.
8. **Nothing stale stays**: charts and documents that no longer match the data are regenerated or deleted.
9. **Basics first**: economy, movement, exploration, symmetry, combat, zero bytecode overruns, zero exceptions. A failed
   basics bar stops work above it.
10. **Play other teams only through the replica, as a contestant** (owner, PROMPTS 11). The replica runs galaxy's own
   backend (siarnaq) and frontend. Our team submits bots, requests scrimmages and downloads results and replays through
   its API (`tools/contest.py`), exactly as in the contest. Local games are only between our own builds (self-play,
   examplefuncsplayer, smoke tests), as a contestant has no other team's code. Until the replica cutover, only the
   gauntlet jobs already queued on 2026-10-07 finish; no new gauntlet against field bots is queued.
   **Ranked vs unranked follows `docs/LADDER_STRATEGY.md`** (owner, PROMPTS 17-18): candidates only through
   `tools/ladder_policy.py trial-start/trial-end` (unranked panel; `trial-park`/`trial-decide` let panels overlap); ranked play only by `tools/ladder_policy.py ranked`.
