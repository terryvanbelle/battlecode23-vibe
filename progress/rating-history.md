# Rating history (replica)

The replica's Team Settings > Rating History chart for vibe23: siarnaq's penalized displayed rating after each rated (ranked, non-tournament) scrimmage, from `GET /api/compete/bc23/match/historical_rating/`, with each submission's first completed rated match marked. Regenerate with `tools/rating_history.py`; data fetched 2026-10-10 17:11 PDT.

![rating history](rating-history.png)

316 rated matches; latest rating 1,603 (2026-10-10 16:56 PDT). Times are Pacific; the replica's own chart shows UTC (galaxy sets Highcharts `time.useUTC` under an axis titled "Local Date & Time"), so it reads 7 h later than this page.

Kind: validated = the submission an init/accept event of progress/ladder-state.json names; re-upload = another upload of a build validated at some point; trial = a build never validated.

| Submission | Build | Kind | First rated match | Time (PDT) | Rating before | Rating after | Rated matches |
|---:|---|---|---:|---|---:|---:|---:|
| #24 | g_iter0 | validated | 23 | 2026-10-07 18:45 | 0\* | 237 | 15 |
| #113 | g_iter0 | re-upload | 258 | 2026-10-07 23:30 | 1,303 | 1,315 | 17 |
| #115 | g_iter0 | re-upload | 582 | 2026-10-08 05:14 | 1,441 | 1,435 | 3 |
| #117 | g_iter0 | re-upload | 635 | 2026-10-08 06:41 | 1,431 | 1,447 | 25 |
| #120 | c_line8a | validated | 968 | 2026-10-08 12:44 | 1,491 | 1,484 | 13 |
| #121 | c_swarm1 | validated | 1130 | 2026-10-08 17:00 | 1,484 | 1,495 | 59 |
| #122 | c_nav4 | validated | 1853 | 2026-10-09 04:14 | 1,563 | 1,576 | 41 |
| #123 | c_nav5 | validated | 2172 | 2026-10-09 09:28 | 1,583 | 1,579 | 9 |
| #124 | c_nav6 | validated | 2367 | 2026-10-09 13:14 | 1,589 | 1,602 | 10 |
| #125 | c_anc3 | validated | 2465 | 2026-10-09 15:14 | 1,582 | 1,594 | 22 (1 cancelled) |
| #126 | c_def3 | validated | 2804 | 2026-10-09 21:39 | 1,587 | 1,591 | 33 |
| #128 | c_def3 | re-upload | 3231 | 2026-10-10 05:14 | 1,634 | 1,622 | 1 |
| #129 | c_aura2 | validated | 3280 | 2026-10-10 06:14 | 1,622 | 1,626 | 33 |
| #131 | c_aura2 | re-upload | 3685 | 2026-10-10 12:39 | 1,626 | 1,622 | 9 |
| #133 | c_aura2 | re-upload | 3770 | 2026-10-10 14:14 | 1,612 | 1,616 | 26 |

\* Not a missing value: the API's old_rating for our first rated match. Siarnaq displays the penalized rating Elo mean - 1500 x 0.85^n (n = rated games so far), which starts at 1500 - 1500 = 0.

No rated match: #112 c_line4 (trial), #114 c_line5 (trial), #116 c_line6 (trial), #118 c_line7m (trial), #119 g_iter0 (re-upload), #127 c_flee3 (trial), #130 c_well5 (trial), #132 c_spread2 (trial), #134 c_scout1 (trial).
