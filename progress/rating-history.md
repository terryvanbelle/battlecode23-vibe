# Rating history (replica)

The replica's Team Settings > Rating History chart for vibe23: siarnaq's penalized displayed rating after each rated (ranked, non-tournament) scrimmage, from `GET /api/compete/bc23/match/historical_rating/`, with each submission's first completed rated match marked. Regenerate with `tools/rating_history.py`; data fetched 2026-10-15 15:31 PDT.

![rating history](rating-history.png)

560 rated matches; latest rating 1,627 (2026-10-15 15:16 PDT). Times are Pacific; the replica's own chart shows UTC (galaxy sets Highcharts `time.useUTC` under an axis titled "Local Date & Time"), so it reads 7 h later than this page.

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
| #133 | c_aura2 | re-upload | 3770 | 2026-10-10 14:14 | 1,612 | 1,616 | 30 |
| #135 | c_aura2 | re-upload | 4173 | 2026-10-10 21:15 | 1,604 | 1,601 | 1 |
| #136 | c_bc1 | validated | 4240 | 2026-10-10 22:44 | 1,601 | 1,613 | 23 (1 cancelled) |
| #143 | c_mend2 | validated | 4604 | 2026-10-11 06:08 | 1,647 | 1,658 | 31 |
| #145 | c_mend2 | re-upload | 4958 | 2026-10-11 13:22 | 1,700 | 1,700 | 143 |
| #155 | c_mend2 | re-upload | 7071 | 2026-10-14 17:00 | 1,662 | 1,666 | 4 |
| #159 | c_mend2 | re-upload | 7245 | 2026-10-15 01:00 | 1,668 | 1,679 | 4 |
| #163 | c_mend2 | re-upload | 7432 | 2026-10-15 09:00 | 1,684 | 1,672 | 4 |
| #164 | c_well9 | validated | 7610 | 2026-10-15 12:19 | 1,662 | 1,651 | 30 |

\* Not a missing value: the API's old_rating for our first rated match. Siarnaq displays the penalized rating Elo mean - 1500 x 0.85^n (n = rated games so far), which starts at 1500 - 1500 = 0.

No rated match: #112 c_line4 (trial), #114 c_line5 (trial), #116 c_line6 (trial), #118 c_line7m (trial), #119 g_iter0 (re-upload), #127 c_flee3 (trial), #130 c_well5 (trial), #132 c_spread2 (trial), #134 c_scout1 (trial), #137 c_mend2 (re-upload), #138 c_bc1 (re-upload), #139 c_well7 (trial), #140 c_bc1 (re-upload), #141 c_end2 (trial), #142 c_bc1 (re-upload), #144 c_bc3 (trial), #146 c_blind1 (trial), #147 c_mend2 (re-upload), #148 c_mend3 (trial), #149 c_mend2 (re-upload), #150 c_seam1 (trial), #151 c_mend2 (re-upload), #152 c_blind2 (trial), #153 c_mend2 (re-upload), #154 c_seam2 (trial), #156 c_cap1 (trial), #157 c_mend2 (re-upload), #158 c_thr1 (trial), #160 c_open1 (trial), #161 c_mend2 (re-upload), #162 c_siege1 (trial).

The chart's left axis starts at 1,400 (owner, PROMPTS 45): 28 rated matches below it, the last at 2026-10-08 00:59 PDT, are off the chart (the table keeps their submissions).

## Bradley-Terry ratings (the right axis)

Our Bradley-Terry fit, as in [ELO.md](ELO.md): `tools/elolib.py` over every recorded game of progress/games.csv, each build its own player; +- 95% = 1.96 SE; a rating is relative to that fit's mean, so it compares only within the fit. Every rating below is today's fit, drawn over the build's rated tenure or at its trial start. The chart's right axis is the left one relabelled through

**BT = -5,480.5 + 4.444 x galaxy rating** (r = 0.981, 67 teams; residual SD 87 BT = 20 galaxy points),

a least-squares fit over the field teams of the replica's Rankings page that our fit also rates, with a galaxy rating of at least 1,400 and at least 30 BT games (not us, not a stock baseline). One galaxy point is about 4.4 BT points: siarnaq's match-level Elo (K 24) compresses the scale, so BT numbers never go on the galaxy axis raw. "As galaxy" = (BT - a) / b, where the line puts a team that strong. It is not exact: single field teams sit within ±38 galaxy points of the line 95% of the time; the line also misfits locally: the 14 field teams within 40 galaxy points of our latest rating (1,627) rate 14 galaxy points below what their BT converts to, on average. The +- 95% column, and the chart's green bands and bars, carry the BT fit's SE alone (±9 to ±22 galaxy points here), so a gap between "As galaxy" and "Galaxy at end of tenure" compares with ±38, not with them. Our galaxy rating carries over from build to build; each build is its own BT player.

| Build | Rated tenure (PDT) | BT rating | +- 95% | BT games | As galaxy | Galaxy at end of tenure |
|---|---|---:|---:|---:|---:|---:|
| g_iter0 | 10-07 18:45 to 10-08 12:44 | 1,688 | 53 | 456 | 1,613 | 1,491 |
| c_line8a | 10-08 12:44 to 10-08 17:00 | 1,705 | 75 | 139 | 1,617 | 1,484 |
| c_swarm1 | 10-08 17:00 to 10-09 04:14 | 1,750 | 53 | 271 | 1,627 | 1,563 |
| c_nav4 | 10-09 04:14 to 10-09 09:28 | 1,828 | 57 | 221 | 1,645 | 1,583 |
| c_nav5 | 10-09 09:28 to 10-09 13:14 | 1,866 | 75 | 126 | 1,653 | 1,589 |
| c_nav6 | 10-09 13:14 to 10-09 15:14 | 1,850 | 75 | 129 | 1,649 | 1,582 |
| c_anc3 | 10-09 15:14 to 10-09 21:39 | 1,925 | 66 | 163 | 1,666 | 1,587 |
| c_def3 | 10-09 21:39 to 10-10 06:14 | 1,952 | 60 | 199 | 1,672 | 1,622 |
| c_aura2 | 10-10 06:14 to 10-10 22:44 | 1,924 | 49 | 314 | 1,666 | 1,601 |
| c_bc1 | 10-10 22:44 to 10-11 06:08 | 1,955 | 66 | 164 | 1,673 | 1,647 |
| c_mend2 | 10-11 06:08 to 10-15 12:19 | 1,956 | 40 | 612 | 1,673 | 1,662 |
| c_well9 | 10-15 12:19 to now | 1,969 | 61 | 186 | 1,676 | 1,627 (latest) |

Trial candidates that never played a rated match (hollow diamonds, at their trial start):

| Build | Trial start (PDT) | BT rating | +- 95% | BT games | As galaxy |
|---|---|---:|---:|---:|---:|
| c_line4 | 10-07 22:09 | 1,580 | 98 | 100 | 1,589 |
| c_line5 | 10-08 01:05 | 1,620 | 95 | 100 | 1,598 |
| c_line6 | 10-08 05:26 | 1,670 | 92 | 100 | 1,609 |
| c_line7m | 10-08 09:05 | 1,658 | 92 | 100 | 1,606 |
| c_flee3 | 10-10 01:02 | 1,929 | 86 | 100 | 1,667 |
| c_well5 | 10-10 11:39 | 2,013 | 87 | 100 | 1,686 |
| c_spread2 | 10-10 13:20 | 1,981 | 87 | 100 | 1,679 |
| c_scout1 | 10-10 17:10 | 1,971 | 86 | 100 | 1,677 |
| c_well7 | 10-11 01:02 | 1,971 | 86 | 100 | 1,677 |
| c_end2 | 10-11 01:46 | 1,939 | 86 | 100 | 1,670 |
| c_bc3 | 10-11 09:14 | 1,981 | 87 | 100 | 1,679 |
| c_blind1 | 10-14 09:00 | 2,002 | 87 | 100 | 1,684 |
| c_mend3 | 10-14 09:01 | 1,981 | 87 | 100 | 1,679 |
| c_seam1 | 10-14 10:01 | 1,960 | 86 | 100 | 1,674 |
| c_blind2 | 10-14 10:22 | 2,002 | 87 | 100 | 1,684 |
| c_seam2 | 10-14 15:19 | 1,960 | 86 | 100 | 1,674 |
| c_cap1 | 10-14 17:13 | 1,960 | 86 | 100 | 1,674 |
| c_thr1 | 10-14 17:57 | 1,971 | 86 | 100 | 1,677 |
| c_open1 | 10-15 01:02 | 1,929 | 86 | 100 | 1,667 |
| c_siege1 | 10-15 05:48 | 1,950 | 86 | 100 | 1,672 |
