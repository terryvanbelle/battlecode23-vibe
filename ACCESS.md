# ACCESS.md — how to look at the scrimmage ladder

Our practice contest runs on a private copy of the Battlecode website: galaxy's own frontend and backend, the same
pages as play.battlecode.org, on our VM `battlecode-dev`. Nothing there touches the real play.battlecode.org.

## Open the site

1. Go to **https://galaxy.136-86-167-127.sslip.io/**
2. The browser first asks for the site password (the gate in front of everything): user **`owner`**, password from
   this Claude Code session with `! cat ~/.bc23-replica-password`. It is not in this repository (it is public).
3. Then log in on galaxy's own login page (Log In, top right): user **`owner`**, the same password. `owner` is the
   site's superuser: it sees every team, match and replay, and `/admin/` (Django admin; read there, change nothing).

The old address, https://136-86-167-127.sslip.io/, belonged to the first replica (galaxy-lite, retired in the evening of
2026-10-07 PDT) and now forwards to the new one.

## To watch our games (replays)

Galaxy shows Replay buttons only on a team's own pages, so watch as our team, not as `owner`:

1. Log out of galaxy if you are logged in as `owner` (top right), then Log In as **`vibe23`** (password:
   `! sed -n 2p ~/.bc23-galaxy-team`).
2. In the left sidebar, open **Scrimmaging**. Its scrimmage history lists our matches, newest first; press
   **Replay** on a match to open the Battlecode 2023 viewer on its games (one file holds all games of the match).
3. Sidebar **Client** does the same from a match picker.

**Queue** (sidebar) lists every match on the ladder, with teams, scores and rating changes, but, as on
play.battlecode.org, no replays: galaxy hides other teams' scrimmage replays from contestants.

## What is there (episode bc23, galaxy's own pages)

- **Rankings** (`/bc23/rankings`): every team and its rating. The rating is galaxy's displayed rating (a penalized
  Elo: every team starts at 0 and climbs over its first ~20 ranked matches). Our team is **vibe23**; the other 87
  teams are public 2023 bots, named `<github owner>.<package>`.
- **Queue** (`/bc23/queue`): every match, newest first, with status, score and rating change.
- **Team pages** (click a team name, `/bc23/team/<id>`): profile, members and rating history.
- **Scrimmaging**, **Submissions**, **My Team**: the logged-in team's own pages. As in the real contest, replays
  are watched from a team's own scrimmage history: to watch our games, log in as our team instead of `owner` (user
  **`vibe23`**, password from `! sed -n 2p ~/.bc23-galaxy-team`), open **Scrimmaging**, and press **Replay** on a
  match; it opens the official Battlecode 2023 viewer on that match's games. (`owner` has no team, so these pages
  are empty for it.)

Every 8 hours galaxy's automatic round gives each team 4 ranked best-of-3 matches. In between, our team requests
scrimmages as a contestant, and field teams challenge the teams rated just above them when the VM has spare time.

## If the address stops working

The host name is built from the VM's external IP, which changes if the VM is stopped and started; a boot script
renews the certificate, and this file is updated with the new address. If it is stale, ask me.

## Fallback in GitHub

`progress/ladder.md` (table) and `progress/ladder.png` (chart) are a snapshot of the Rankings page, with the latest
matches, regenerated at each check-in.
