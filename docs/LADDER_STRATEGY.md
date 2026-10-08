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
- Challenges go to one of the 3 teams rated closest at or above us. Above us, the expected score is low, so a win
  gains a lot and a loss costs little.
- Galaxy refuses ranked challenges to weaker teams; weaker teams challenge us instead.

**3. Pace ranked play.**
- **BURST** (one request every 5 minutes) while ratings are young (fewer than 30 rated matches) or the build was
  validated in the last 24 hours. Early on, volume removes the n-penalty, and a freshly improved build is
  underrated.
- **MAINTAIN** (one every 30 minutes) otherwise. Once ratings have converged, ranked games mostly tread water.
- Never while 2 or more of our matches already wait in the queue, so that our panels are not slowed down.

**4. Trials: keep the exposure window short.** `trial-start <package>`:
1. Refuses unless the validated build is active and the trial can end before the next autoscrim (2.5 hours; start a
   trial right after an autoscrim fires).
2. Sets incoming ranked requests to auto-reject. Autoscrims still play, which is why trials avoid them.
3. Submits the candidate and runs the panel.

Then `trial-end --accept` makes the candidate the validated build (a fresh build: BURST), and `trial-end --reject`
resubmits the validated build at once. Both restore auto-accept, and the ranked loop pauses throughout the trial.

**5. Endgame.** Before a submission freeze or tournament seeding, run no trials. Keep the best validated build active,
and spend the ranked budget early enough for the rating to converge.

## Operation

```
tools/ladder_policy.py status                       # state, active and validated submissions, mode, next autoscrim
tools/ladder_policy.py trial-start <package>        # submit a candidate and run the panel (long: run it detached)
tools/ladder_policy.py trial-end --accept|--reject  # decided by tools/paired.py on the two panel runs
tools/ladder_policy.py ranked                       # the ranked loop (detached on the driver, logs/ranked-policy.log)
```

The autoscrim schedule is not published by the API: it is staff-only, as in the contest, and a contestant learns it by
watching when autoscrim matches appear. Ours is every 8 hours: 17:00, 01:00 and 09:00 PDT (the cron `AUTOSCRIM_CRON` is in UTC,
`docs/galaxy/README.md` section 6).
