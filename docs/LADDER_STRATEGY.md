# Ladder strategy: when to play ranked and when to play unranked

Owner, PROMPTS 17-18 (2026-10-07): use the optimal strategy for choosing which games to request, and document it.
This applies to the galaxy replica exactly as it would to play.battlecode.org. The policy is implemented in
`tools/ladder_policy.py`, and its state lives in `progress/ladder-state.json`.

## What each kind of game gives

| | Unranked | Ranked |
|---|---|---|
| Opponent | anyone, weaker teams included | only teams rated at or above us |
| Maps and order | we choose (up to 10 maps; `+`, `-` or `?`) | 3 random maps, shuffled order |
| Rating | unchanged | moves (galaxy seeds tournaments by it) |
| Use | experiments: the same opponent, maps and order replay deterministically, so builds compare game for game | banking rating |

Galaxy's displayed rating is `mean - 1500 * 0.85^n`, where n counts rated matches. The penalty is 295 points at n = 10,
58 at n = 20 and 12 at n = 30. Each match moves the mean by `24 * (S - E)`, where S is our share of games won and E is
the expected share. Hourly limits are counted per kind, and they include requests plus every match of that kind that
we played (incoming challenges and autoscrims too). The replica allows 40 unranked and 20 ranked per hour.

**The trap.** A match plays the submission that is active when the match is created. Testing a candidate therefore
means making it active, and while it is active, autoscrims and every accepted incoming ranked challenge play it.

## The policy

**1. Learn with unranked games.**
- Every candidate is judged on a fixed unranked panel (`test/cells/panel-v1.txt`: ten opponents rated near or above
  us, ten maps, order `+`). Its results are paired game for game with the validated build's panel results.
- Unranked probes also serve diagnostics: reproducing a loss on a chosen map, or studying a top team.

**2. Bank rating with ranked games, and only with a validated build active.**
- *Validated* means the build passed the panel gate (`TRAINING_ALGORITHM.md`).
- Challenges go to the open team at or above us with the largest **expected gain** `24 * (P - E)`: P is our win
  chance from the Bradley-Terry fit over every game we have (`tools/elolib.py`; refit hourly), E is what galaxy
  expects from the two displayed ratings. If no team offers a positive gain, the loop sends no ranked request. The
  fit predicts held-out games better than galaxy's running Elo (log-loss 0.572 vs 0.628, `LEARNINGS.md`), and
  galaxy's scale is compressed: on 2026-10-14 BT spread the 13 teams above us over 290 points where galaxy spread
  them over 120, so 11 of them offered negative gains (-2 to -6) and only one a clear positive one (+3.1). Without a
  BT estimate (a build with no games, a failed fit) the loop falls back to one of the 3 teams rated closest above us.
- Galaxy refuses ranked challenges to weaker teams; weaker teams challenge us instead. Incoming ranked challenges stay on
  auto-accept: on 2026-10-14 all 73 teams below us offered a positive expected gain (+0.3 to +8.5; the same
  compression, seen from above). Re-check with the same fit before ever declining one.

**3. Pace ranked play.**
- **BURST** (one request every 5 minutes) while ratings are young (fewer than 30 rated matches) or the build was
  validated in the last 24 hours. Early on, volume removes the n-penalty, and a freshly improved build is
  underrated.
- **MAINTAIN** (one every 30 minutes) otherwise. Once ratings have converged, ranked games mostly tread water.
- Never while 2 or more of our matches already wait in the queue, so that our panels are not slowed down.

**4. Trials: keep the exposure window short.** `trial-start <package>`:
0. Refuses unless the candidate passed the pre-trial screen (below): a PASS record in `progress/screens/` for the
   candidate's code hash against the current validated build's code hash. The check runs before any replica call;
   `--skip-screen "<reason>"` overrides it and the reason is kept in the trial-start history event.
1. Refuses unless the validated build is active and the trial can end before the next autoscrim (2.5 hours; start a
   trial right after an autoscrim fires).
2. Sets incoming ranked requests to auto-reject. Autoscrims still play, which is why trials avoid them.
3. Submits the candidate and runs the panel. If the candidate has not compiled after 30 minutes, the trial is recorded
   without a panel, because the candidate may still become active: end it with `trial-end --reject`.

Then `trial-end --accept` makes the candidate the validated build (a fresh build: BURST), and `trial-end --reject`
resubmits the validated build at once. Both restore auto-accept, and the ranked loop pauses throughout the trial.

**Parked trials.** The replica plays every match from one shared queue. After each autoscrim (17:00, 01:00 and 09:00
PDT), the backlog delays a panel by about 3 hours: c_scout1's trial started at 17:10, and its first panel match played
at 20:00. Holding the candidate active until the panel finishes blocks the next trial for hours, keeps the ranked loop
paused and incoming ranked challenges rejected, and leaves the candidate exposed to autoscrims. Trials therefore ran
one per 8-hour window. Parking removes the wait. A match's submission is fixed when the match is created (the trap
above), and the unranked panel requests are auto-accepted, so their matches are created within minutes. Once they all
exist, the candidate need not stay active.
- `trial-park` waits until every panel cell has a created match whose submission (our participant row's) is the
  candidate's. Then it resubmits the validated build (as `trial-end --reject` does), restores auto-accept and moves
  the trial to the parked list (`parked` in `progress/ladder-state.json`, with its run directory and the trial-start
  process id). Another trial may start, and autoscrims and incoming ranked challenges play the validated build. The
  ranked loop may challenge again, but only once fewer than 2 of our matches wait in the queue, the parked panel's
  included (section 3). If the matches do not all exist within 20 minutes, `trial-park` stops with an error and the
  trial stays open.
- The trial-start process keeps waiting for the panel. When the panel ends, it records the run on the parked entry.
- `trial-decide <package> --accept|--reject` then decides a parked trial whose panel is done. `--reject` drops it.
  `--accept` resubmits the package, refusing if its code hash differs from the trial's, and makes that new submission
  the validated build (a fresh build: BURST). `--accept` is refused while a trial is open, because the resubmission
  would replace the candidate as the active submission. A trial submission id can stand in for the package name.
  Compare the run with the panel run of the build validated at decision time, since another parked trial may have
  been accepted in the meantime. `status` prints the `tools/paired.py` command.
- Overlapping panels have identical cells. `tools/contest.py block` therefore records the block's submission in each
  request of `requests.jsonl`, and it pairs a match with a request only if our participant row carries it. For
  `trial-start`, the block's submission is the candidate's; otherwise it is the one active when the block starts. The
  block stops before a request if another submission is active. A resumed run keeps the submission its requests name;
  for a run from before the field, the first line of its `provenance.txt` names it, and its old entries keep the old
  rule (opponent, map set and match floor). The old rule also applies when a match row carries no submission key at all
  (the replica's rows do carry one), but `trial-park` never parks on it.
- `trial-start` refuses `RESUME=<dir>` when the directory already holds requests, because it would submit a new build.
  Resume a crashed panel with `RESUME=<dir> tools/contest.py block <cells> --tag <tag>`. For a parked trial,
  `trial-decide` finds the run once its `results.csv` exists.
- Every command that writes `progress/ladder-state.json` holds its lock (`build/ladder-state.lock`) for the whole
  read-modify-write. `trial-start`, `trial-park`, `trial-end` and `trial-decide` hold it from their checks
  through the compile wait to the write. Another command therefore waits (and says so) instead of acting on a state
  that is about to change. The trial-start process takes the lock again when its panel ends.

**5. Endgame.** Before a submission freeze or tournament seeding, run no trials. Keep the best validated build active,
and spend the ranked budget early enough for the rating to converge.

## Pre-trial screen

Owner, PROMPTS 22-23: a candidate is screened locally before it uses replica games (design: `docs/ARCHETYPES.md`
section 5). `tools/screen.py <package>` queues one job on the VM (standing queue, `MAXJOBS=2`; every game on the map's
own seed, both sides) and judges it on the driver:

| stage | games | bar |
|---|---|---|
| (a) basics | 8: candidate vs examplefuncsplayer on SmallElements, Contraction, FourNations, Tightrope | 8/8 wins; candidate over = exceptions = deaths_self = sym_wrong = 0. A failure stops the screen. |
| (b) head-to-head | 20: candidate vs the validated build on the 10 panel maps | s = wins + 0.5 coin: PASS at s >= 11, BORDERLINE at 9-10.5, FAIL below 9 (stops the screen) |
| (c) roster | 20 per archetype, paired cell by cell with the validated build's games (cached by code hash) | per archetype: REGRESSION when net <= -3 and net <= -2 sqrt(g + l); pooled over the gating archetypes: Net <= -4 and Net <= -2 sqrt(G + L) |
| (d) basics | every candidate game | over = exceptions = deaths_self = 0 |

**PASS** when (a), (c) and (d) pass and (b) is PASS, or (b) is BORDERLINE with a pooled roster Net >= +2. Otherwise
FAIL; INCOMPLETE when unknown games (timeouts) could change a verdict, or when a run's recorded code hash is not the
expected one. The roster (`tools/archetypes.txt`, default every `src/arch_*`) can block a candidate, never accept one:
an archetype gates only with a VALID validation record for its current code hash (`progress/archetypes/`); the others
are played and reported for information. An archetype at the candidate's hash is dropped; one at the incumbent's hash
is the incumbent's own style and is not played (its games would repeat stage (b)). The record (`progress/screens/<package>-<hash>.json`) carries each stage's
counts and, per archetype, both builds' wins, gained, lost, both-won, both-lost and a censoring flag (the incumbent
won none or all of its cells). The validated build's roster games are cached in `progress/screens/cache.csv` by
(code hashes, map, side, seed), so each is played once per pair of hashes. A `--maps` subset or a `--roster` override
writes a `.reduced` record that never admits a trial. Exit codes: 0 PASS, 1 FAIL, 2 INCOMPLETE, 3 refused. After each trial,
`tools/screen.py calibrate <record> <panel run>` compares the screen's paired counts per style with the trial panel's.

## Operation

```
tools/ladder_policy.py status                       # state, active and validated submissions, mode, next autoscrim
tools/screen.py <package> [--no-wait]               # the pre-trial screen (VM job; collect with tools/screen.py collect)
tools/ladder_policy.py trial-start <package>        # submit a candidate and run the panel (long: run it detached)
                                                    # refuses without a passing screen; --skip-screen "<reason>"
tools/ladder_policy.py trial-end --accept|--reject  # decided by tools/paired.py on the two panel runs
tools/ladder_policy.py trial-park                   # once every panel match exists (waits up to 20 min): the
                                                    # validated build is back, the panel keeps playing; then
tools/ladder_policy.py trial-decide <package> --accept|--reject   # once the parked panel is done (tools/paired.py)
tools/ladder_policy.py ranked                       # the ranked loop (detached on the driver, logs/ranked-policy.log)
```

The usual cycle is `trial-start` (detached), then `trial-park` a few minutes later. The next `trial-start` may follow at
once: the screen and the autoscrim window still apply, and `block` waits out the hourly unranked limit (a 10-request
panel counts 20 of the 40). `status` lists the parked trials and shows whether each one's panel is playing or done.

The autoscrim schedule is not published by the API: it is staff-only, as in the contest, and a contestant learns it by
watching when autoscrim matches appear. Ours is every 8 hours: 17:00, 01:00 and 09:00 PDT (the cron `AUTOSCRIM_CRON` is in UTC,
`docs/galaxy/README.md` section 6).
