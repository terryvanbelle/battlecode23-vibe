# galaxy-lite (retired 2026-10-08 01:01 UTC)

galaxy-lite was our first private Battlecode 2023 ladder: a standard-library Python re-implementation of the
official judging stack (siarnaq + saturn) with galaxy's rating and matchmaking rules. It ran on `battlecode-dev`
from 2026-10-07 15:40 to 18:01 PDT (2026-10-08 01:01 UTC) and was then retired in favour of **the galaxy replica**, galaxy's own
siarnaq backend and frontend: **`docs/galaxy/README.md`**. Every game against another team now goes through that
site's API, as in the contest (CLAUDE.md rule 10). How the owner reaches it: `ACCESS.md`.

## What the retirement did

- `tools/replica-matchmaker.py` was stopped (by PID) and deleted; its role went to the galaxy field-activity process
  (`tools/galaxy/field.py activity`).
- The worker, the web/API service and the autoscrim timer are stopped and disabled. With
  `/etc/bc23-replica/galaxy-lite.retired` in place, `vm-setup.sh services` keeps them so (`vm-setup.sh retire-lite`).
  The 122 matches still queued and 3 interrupted ones were never played.
- The finished games went into `progress/games.csv` first (runs `replica-<match id>`, 159 games from 53 matches,
  field teams and `us:g_iter0`), then `tools/replica-export.sh` and `tools/replica-reset.sh` were deleted.
- Its data (`replica.db`, replays, submissions, logs, exports, the installed viewer) is archived, never deleted, under
  `/home/bcreplica/replica/archive/20261008-010127-retired/`. The test data of 2026-10-07 is in
  `archive/20261007-223917/`.
- Its host name, `https://<external-ip-with-dashes>.sslip.io/`, now answers with a 302 redirect to the galaxy site
  (`https://galaxy.<external-ip-with-dashes>.sslip.io/`, same path), without asking for the password.
- The galaxy saturn got the freed engine slots: `GALAXY_EXECUTE_SLOTS=5`.

## What is still in use

- `tools/replica/deploy/` and `docs/replica/DEPLOY.md`: the host guards both sites share (user `bcreplica`, the
  egress lockdown, Caddy, the host-name unit, the password, the GCP firewall rule) and `verify.sh`, which checks the
  retired state.
- `tools/replica/viewer.py` and `docs/replica/VIEWER.md`: the pins of the official 3.0.15 web client, which the
  galaxy site installs under `/viewer/`.
- `tools/replica/worker.py` `match_command`: the engine command line that the galaxy saturn reuses.

The rest of `tools/replica/` (and `tools/replica.py`) is the retired system's code. It stays because the galaxy
saturn imports part of it and `test/replica/test_replica.py` still covers all of it. `tools/replica/snapshot.py`
reads only the archived database, so it cannot overwrite `progress/ladder.md`; the ladder snapshot is now
`tools/galaxy/snapshot.py`.

## Looking at the archived data

```bash
# on the VM, read-only (any member of group bcreplica)
A=/home/bcreplica/replica/archive/20261008-010127-retired
REPLICA_HOME=$A python3 tools/replica.py status
REPLICA_HOME=$A python3 tools/replica.py ratings | head
```
