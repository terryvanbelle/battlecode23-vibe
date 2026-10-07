# battlecode23-vibe

A Battlecode 2023 ("Tempest") bot built by an autonomous agent under an evidence-driven training loop, as practice.
No official Battlecode infrastructure is used for evaluation: games run on our own VM, and the scrimmage ladder is a
private replica of the official judging stack (galaxy) that never contacts battlecode.org services.

Start with `TRAINING_ALGORITHM.md` (the loop), `RULES.md` (the game, engine-checked) and `HANDOFF.md` (current state).
All owner prompts are in `PROMPTS.md` (PDT).

The ladder replica has a password-protected web front with rankings and replays: see `ACCESS.md`. Its code is in
`tools/replica/` and its documentation in `docs/replica/`. Snapshots of the standings are committed as
`progress/ladder.md` and `progress/ladder.png`; our own rating history over every recorded game is in `progress/ELO.md`.
