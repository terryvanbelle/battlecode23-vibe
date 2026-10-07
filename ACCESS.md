# ACCESS.md — how to look at the scrimmage ladder

The private ladder (a replica of the official judging stack, built on galaxy's rating and matchmaking rules) runs on our
VM `battlecode-dev`. It has a web front end where you can see who is ranked where and replay any scrimmage game.

## Open the site

- **URL:** https://136-86-167-127.sslip.io/
- **User name:** `owner`
- **Password:** not stored in this repository (it is public). It is in `~/.bc23-replica-password` on the driver machine
  (and on the VM). From this Claude Code session you can show it with:

  ```
  ! cat ~/.bc23-replica-password
  ```

The site uses HTTPS (a Let's Encrypt certificate) and HTTP basic authentication, and it is read-only: nothing can be
changed from the browser.

## What is there

- **Ladder** (`/`): every team with its rank, displayed rating (galaxy's penalized Elo), rating mean, matches played and
  win-loss record. Our builds are named `us:<build>` and highlighted.
- **Team pages** (`/team/<id>`): rating history and every match with opponent, score and maps.
- **Matches** (`/matches`): the most recent matches and their status.
- **Match pages** (`/match/<id>`): the three games (map, winner, rounds, end reason), the rating change, and a **Watch**
  link that opens the official Battlecode 2023 replay viewer (hosted on the VM itself) on that game.

## If the address stops working

The host name is built from the VM's external IP address, which changes if the VM is stopped and started. A boot script
updates the site's certificate and name automatically, and this file is updated with the new address. If it is stale,
ask me (or run `tools/replica/deploy/refresh-hostname.sh` on the VM). Reserving a static IP would remove this problem;
that is an owner decision because it costs money while the VM is stopped (`docs/replica/DEPLOY.md`).

## Fallback in GitHub

After every ladder round the current standings are also committed as `progress/ladder.md` (a table) and
`progress/ladder.png` (a picture), so you can check them from GitHub without the site.
