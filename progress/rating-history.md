# Rating history (replica)

The replica's Team Settings > Rating History chart for vibe23: siarnaq's penalized displayed rating after each rated (ranked, non-tournament) scrimmage, from `GET /api/compete/bc23/match/historical_rating/`, with each submission's first completed rated match marked. Regenerate with `tools/rating_history.py`; data fetched 2026-10-18 13:43 PDT.

![rating history](rating-history.png)

728 rated matches; latest rating 1,667 (2026-10-18 13:35 PDT). Times are Pacific; the replica's own chart shows UTC (galaxy sets Highcharts `time.useUTC` under an axis titled "Local Date & Time"), so it reads 7 h later than this page.

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
| #164 | c_well9 | validated | 7610 | 2026-10-15 12:19 | 1,662 | 1,651 | 46 |
| #166 | c_well9 | re-upload | 7864 | 2026-10-16 01:00 | 1,663 | 1,660 | 4 |
| #168 | c_well9 | re-upload | 8024 | 2026-10-16 06:16 | 1,653 | 1,649 | 5 |
| #176 | c_gp1 | validated | 8231 | 2026-10-16 15:11 | 1,657 | 1,655 | 24 |
| #178 | c_gp1 | re-upload | 8487 | 2026-10-17 01:00 | 1,710 | 1,698 | 4 |
| #180 | c_gp1 | re-upload | 8623 | 2026-10-17 05:41 | 1,702 | 1,706 | 7 |
| #184 | c_gp1 | re-upload | 8822 | 2026-10-17 14:24 | 1,696 | 1,693 | 1 |
| #185 | c_hr1 | validated | 8833 | 2026-10-17 15:17 | 1,693 | 1,697 | 34 |
| #186 | c_isle1 | validated | 9049 | 2026-10-17 22:46 | 1,681 | 1,678 | 26 |
| #188 | c_isle1 | re-upload | 9257 | 2026-10-18 05:19 | 1,693 | 1,706 | 46 |
| #189 | c_loose1 | validated | 9485 | 2026-10-18 13:35 | 1,662 | 1,667 | 1 |

\* Not a missing value: the API's old_rating for our first rated match. Siarnaq displays the penalized rating Elo mean - 1500 x 0.85^n (n = rated games so far), which starts at 1500 - 1500 = 0.

No rated match: #112 c_line4 (trial), #114 c_line5 (trial), #116 c_line6 (trial), #118 c_line7m (trial), #119 g_iter0 (re-upload), #127 c_flee3 (trial), #130 c_well5 (trial), #132 c_spread2 (trial), #134 c_scout1 (trial), #137 c_mend2 (re-upload), #138 c_bc1 (re-upload), #139 c_well7 (trial), #140 c_bc1 (re-upload), #141 c_end2 (trial), #142 c_bc1 (re-upload), #144 c_bc3 (trial), #146 c_blind1 (trial), #147 c_mend2 (re-upload), #148 c_mend3 (trial), #149 c_mend2 (re-upload), #150 c_seam1 (trial), #151 c_mend2 (re-upload), #152 c_blind2 (trial), #153 c_mend2 (re-upload), #154 c_seam2 (trial), #156 c_cap1 (trial), #157 c_mend2 (re-upload), #158 c_thr1 (trial), #160 c_open1 (trial), #161 c_mend2 (re-upload), #162 c_siege1 (trial), #165 c_well10 (trial), #167 c_mid1 (trial), #169 c_pack1 (re-upload), #170 c_well9 (re-upload), #171 c_gp1 (re-upload), #172 c_well9 (re-upload), #173 c_tune1 (trial), #174 c_well9 (re-upload), #175 c_pack1 (validated), #177 c_adlo2 (trial), #179 c_expl1 (trial), #181 c_hunt1 (trial), #182 c_gp1 (re-upload), #183 c_rot1 (trial), #187 c_di1 (trial).

#175 c_pack1 was the validated build from 10-16 14:38 to 10-16 15:04 PDT, when #176 c_gp1 replaced it before any ranked match was created: it has no point on the curve.

The chart's left axis starts at 1,400 (owner, PROMPTS 45): 28 rated matches below it, the last at 2026-10-08 00:59 PDT, are off the chart (the table keeps their submissions).

## Bradley-Terry ratings (the right axis)

Our Bradley-Terry fit, as in [ELO.md](ELO.md): `tools/elolib.py` over every recorded game of progress/games.csv, each build its own player; +- 95% = 1.96 SE; a rating is relative to that fit's mean, so it compares only within the fit. Every rating below is today's fit, drawn over the build's rated tenure or at its trial start. The chart's right axis is the left one relabelled through

**BT = -4,851.5 + 3.977 x galaxy rating** (r = 0.967, 63 teams; residual SD 106 BT = 27 galaxy points),

a least-squares fit over the field teams of the replica's Rankings page that our fit also rates, with a galaxy rating of at least 1,400 and at least 30 BT games (not us, not a stock baseline). One galaxy point is about 4.0 BT points: siarnaq's match-level Elo (K 24) compresses the scale, so BT numbers never go on the galaxy axis raw. "As galaxy" = (BT - a) / b, where the line puts a team that strong. It is not exact: single field teams sit within ±52 galaxy points of the line 95% of the time; the line also misfits locally: the 8 field teams within 40 galaxy points of our latest rating (1,667) rate 19 galaxy points below what their BT converts to, on average. The +- 95% column, and the chart's green bands and bars, carry the BT fit's SE alone (±10 to ±24 galaxy points here), so a gap between "As galaxy" and "Galaxy at end of tenure" compares with ±52, not with them. Our galaxy rating carries over from build to build; each build is its own BT player.

| Build | Rated tenure (PDT) | BT rating | +- 95% | BT games | As galaxy | Galaxy at end of tenure |
|---|---|---:|---:|---:|---:|---:|
| g_iter0 | 10-07 18:45 to 10-08 12:44 | 1,601 | 52 | 456 | 1,622 | 1,491 |
| c_line8a | 10-08 12:44 to 10-08 17:00 | 1,621 | 75 | 139 | 1,627 | 1,484 |
| c_swarm1 | 10-08 17:00 to 10-09 04:14 | 1,663 | 52 | 271 | 1,638 | 1,563 |
| c_nav4 | 10-09 04:14 to 10-09 09:28 | 1,744 | 56 | 221 | 1,658 | 1,583 |
| c_nav5 | 10-09 09:28 to 10-09 13:14 | 1,782 | 75 | 126 | 1,668 | 1,589 |
| c_nav6 | 10-09 13:14 to 10-09 15:14 | 1,767 | 74 | 129 | 1,664 | 1,582 |
| c_anc3 | 10-09 15:14 to 10-09 21:39 | 1,841 | 65 | 163 | 1,683 | 1,587 |
| c_def3 | 10-09 21:39 to 10-10 06:14 | 1,870 | 59 | 199 | 1,690 | 1,622 |
| c_aura2 | 10-10 06:14 to 10-10 22:44 | 1,840 | 48 | 314 | 1,682 | 1,601 |
| c_bc1 | 10-10 22:44 to 10-11 06:08 | 1,870 | 65 | 164 | 1,690 | 1,647 |
| c_mend2 | 10-11 06:08 to 10-15 12:19 | 1,871 | 38 | 612 | 1,690 | 1,662 |
| c_well9 | 10-15 12:19 to 10-16 15:11 | 1,865 | 52 | 260 | 1,689 | 1,657 |
| c_gp1 | 10-16 15:11 to 10-17 15:17 | 1,996 | 58 | 205 | 1,722 | 1,693 |
| c_hr1 | 10-17 15:17 to 10-17 22:46 | 1,982 | 59 | 195 | 1,718 | 1,681 |
| c_isle1 | 10-17 22:46 to 10-18 13:35 | 1,947 | 48 | 303 | 1,709 | 1,662 |
| c_loose1 | 10-18 13:35 to now | 2,103 | 96 | 100 | 1,748 | 1,667 (latest) |

Trial candidates that never played a rated match (hollow diamonds, at their trial start):

| Build | Trial start (PDT) | BT rating | +- 95% | BT games | As galaxy |
|---|---|---:|---:|---:|---:|
| c_line4 | 10-07 22:09 | 1,492 | 97 | 100 | 1,595 |
| c_line5 | 10-08 01:05 | 1,532 | 94 | 100 | 1,605 |
| c_line6 | 10-08 05:26 | 1,582 | 91 | 100 | 1,618 |
| c_line7m | 10-08 09:05 | 1,570 | 92 | 100 | 1,615 |
| c_flee3 | 10-10 01:02 | 1,844 | 85 | 100 | 1,683 |
| c_well5 | 10-10 11:39 | 1,928 | 87 | 100 | 1,705 |
| c_spread2 | 10-10 13:20 | 1,896 | 86 | 100 | 1,697 |
| c_scout1 | 10-10 17:10 | 1,886 | 86 | 100 | 1,694 |
| c_well7 | 10-11 01:02 | 1,886 | 86 | 100 | 1,694 |
| c_end2 | 10-11 01:46 | 1,854 | 85 | 100 | 1,686 |
| c_bc3 | 10-11 09:14 | 1,896 | 86 | 100 | 1,697 |
| c_blind1 | 10-14 09:00 | 1,917 | 86 | 100 | 1,702 |
| c_mend3 | 10-14 09:01 | 1,896 | 86 | 100 | 1,697 |
| c_seam1 | 10-14 10:01 | 1,875 | 86 | 100 | 1,691 |
| c_blind2 | 10-14 10:22 | 1,917 | 86 | 100 | 1,702 |
| c_seam2 | 10-14 15:19 | 1,875 | 86 | 100 | 1,691 |
| c_cap1 | 10-14 17:13 | 1,875 | 86 | 100 | 1,691 |
| c_thr1 | 10-14 17:57 | 1,886 | 86 | 100 | 1,694 |
| c_open1 | 10-15 01:02 | 1,844 | 85 | 100 | 1,683 |
| c_siege1 | 10-15 05:48 | 1,865 | 86 | 100 | 1,689 |
| c_well10 | 10-15 17:32 | 1,907 | 86 | 100 | 1,699 |
| c_mid1 | 10-16 01:06 | 1,907 | 86 | 100 | 1,699 |
| c_pack1 | 10-16 09:01 | 1,960 | 88 | 100 | 1,713 |
| c_tune1 | 10-16 11:43 | 1,917 | 86 | 100 | 1,702 |
| c_adlo2 | 10-16 20:44 | 1,971 | 88 | 100 | 1,715 |
| c_expl1 | 10-17 02:14 | 1,971 | 88 | 100 | 1,715 |
| c_hunt1 | 10-17 09:05 | 2,005 | 89 | 100 | 1,724 |
| c_rot1 | 10-17 11:36 | 2,017 | 90 | 100 | 1,727 |
| c_di1 | 10-18 04:11 | 2,005 | 89 | 100 | 1,724 |
