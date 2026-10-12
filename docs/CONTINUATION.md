# Continuing from the web interface with the existing VMs

Updated 2026-10-12 PDT. **All ongoing owner interaction remains in the web interface** (PROMPTS 58). The original
driver and `battlecode-dev` are compute workers; do not transfer project control to a CLI session or require ongoing
CLI interaction. The owner has started a separate Codex instance in tmux on `claude-driver`, but that does not connect
this web chat to it. This web environment has no GCP identity, SSH credentials or VM route and has not inspected or
changed either VM. The authoritative live files, credentials, replays and running jobs remain on the original VMs.

## Establish remote access from the web environment

The runtime's documented SSH transport is a configured VPN route plus authorized private TCP forwarding. Current
observations show no VPN, no TCP grants, and no credential bindings. The environment configuration must provide a
working route to the existing VPC, a grant for `battlecode-dev` (`10.138.0.3/32`) and the driver's verified private IP,
and protected SSH authentication with verified host keys. Follow the cloud-environment-runtime networking and VPN
references; do not disable host-key checks or try to bypass the proxy. This setup cannot be supplied by editing the
executor's network-policy snapshot.

Once connected, the agent in this web session executes the recovery steps below remotely. A CLI agent may assist
with one-time connection setup only if the owner chooses; it is not the ongoing interaction model. GCP IAP over
HTTPS is another possible route, but proxy support for its WebSocket tunnel has not been verified here. No SSH/GCP
execution plugin was found by plugin discovery. A self-hosted job worker would require a separate initial setup and
has not been installed. Do not claim any route is operational until an authenticated read-only VM check succeeds.

The owner's SSH command for the driver is:

```bash
gcloud compute ssh claude-driver --zone=us-west1-b --project=tvanbelle-vibecode
```

## Recover the live state first

Read `CLAUDE.md`, `PROMPTS.md`, `HANDOFF.md`, `LEARNINGS.md`, `TRAINING_ALGORITHM.md`, `RULES.md`, and the recent
sections of `TRAINING_LOG.md` (grep-only, append-only). Preserve the no-opponent-source/no-2023-post-mortem rules,
replica-only field evaluation, PDT reporting and VM-only volume games. Never touch `battlecode-dev2`.

1. Remotely operate the existing `~/projects/vibe/2023` checkout on `claude-driver`. Inspect its git status, recent commits,
   changed-file names and local diffs before pulling, switching branches or applying patches. The old session reported
   a token-cache fix that was not committed: reconcile that local work with this branch rather than replacing it.
2. Identify the existing ranked policy, collectors, screens and queue runner. Keep one authoritative checkout and one
   ranked process. Our state lock is a local file lock: it cannot coordinate different checkouts or hosts. Stop or
   reuse the old process by its exact PID when adopting changed tools; never use a broad `pkill -f`.
3. Use the owner's connection:

   ```bash
   gcloud compute ssh battlecode-dev --zone us-west1-b --project tvanbelle-vibecode
   ```

   Inspect the VM checkout, queue files, disk and running services before any sync. `tools/vm.sh`'s `vm_sync` replaces
   directories with `--delete`, and even `tools/galaxy/deploy/deploy.sh status` pushes code. For read-only service
   status use the already-installed VM command:

   ```bash
   sudo /usr/local/lib/bc23-galaxy/galaxy-setup.sh status
   bc23-galaxy-manage bootstrap status
   ```

4. Run `python3 tools/ladder_policy.py status` on the driver and reconcile the current submission and trial state with
   live API results. Preserve uncommitted state and run directories; do not overwrite them with GitHub snapshots.
5. Check results collection immediately. Field-only replay pruning deletes by creation age after six hours and
   assumes the driver keeps exporting results. Our-team replays are exempt. The current results collector stops on
   a replay 404; diagnose missing field replays before repeatedly restarting it. Check for orphaned queue jobs before
   requeueing them, and do not start duplicate panels or ranked loops.

## Resume the existing experiments

The last committed state (2026-10-11 09:15 PDT, not a live observation) is:

| Item | State |
| --- | --- |
| Validated build | g_iter10 = c_mend2, active submission 145; accepted originally as 143 |
| Parked trial | c_bc3, submission 144, hash ed3aceb26a90 |
| Trial run | gauntlet/20261011-161413-panel-c_bc3 |
| Existing matches | 4943–4952 |
| Reference panels | gauntlet/20261011-080046-panel-c_mend2 and gauntlet/20261011-042052-panel-c_bc1 |
| Other work | c_well9 screen queued; c_ward3 held until c_mend2's reference cache exists |

Collect/resume the existing c_bc3 panel instead of `trial-start` again. The collector supports
`RESUME=<existing run directory> python3 tools/contest.py block test/cells/panel-v1.txt --tag panel-c_bc3`.
Confirm the submission recorded in `requests.jsonl` and that all requested matches belong to this panel first.
The current collector can write `results.csv` after a timeout, and the policy treats its existence as completion:
**check all 100 cells and terminal match statuses explicitly before any accept**. Then compare against both references
with `tools/paired.py`, inspect bytecode savings, overruns and exceptions, and use `trial-decide` for the parked trial.

Collect the existing c_well9 screen next; queue c_ward3 once its incumbent cache exists. c_well7, c_end2, c_lane2 and
c_amp2/c_amp3 are closed for the reasons in the log. Continue local candidate work while replica trials play.

## Changes prepared by this session

- `contest._save_token` now uses a unique private temporary file per write, atomically replaces the cache, and cleans
  up failed writes. Two regression tests cover simultaneous writers and failed-write preservation.
- The ranked policy holds the existing state lock through its fresh eligibility checks and request. Three concurrent
  regressions cover trial/ranked ordering and failure-path lock release. This requires every policy command to use
  the same checkout; it is not a distributed lock or a ranked-process singleton.
- ReplayDump adds conservative shot visibility and rate bounds, preserving historical `blind_rate` as the miss
  fraction and exposing `miss_rate` explicitly. Use `tools/replay-dump.sh FILE --shots`, or
  `tools/replay-dump.sh FILE --extract DIR --shots`, for per-shot CSV. Normal extracts do not create a large shots file;
  appended census counts and bounds are available normally. See `docs/TELEMETRY.md`.
- HANDOFF is reconciled with the latest committed state, and LEARNINGS retracts the unsupported claim that the old
  43–70% miss rates measured shots outside vision. Re-extract the available panels before designing a blind-fire arm
  or claiming blind-fire damage/deaths. Unknown geometries must remain unknown.

## Verification and adoption

Run `tools/unit-tests.sh` on the driver with the existing **checksum-pinned official 3.0.15 jar** before adopting these
changes. This cloud session installed JDK 8 and built the official tag's source for local unit/fixture checks only;
that temporary jar is gitignored, has a different checksum, and is never for deployment or trial judgments.
The instrument and concurrency regressions pass locally (111 analysis tests, one skip, plus 3 ranked and 2 token
regressions); release-backed compile integration requires the official jar.
Do not weaken the pin to make a source-built jar pass.

After reconciling local changes, apply the branch's changes, run the full suite, and restart only the affected driver
processes by PID. Changes to deployed tools need the established VM workflow after the live tree is preserved.
Resume result exports, snapshots and charts using the established contestant/API tools, and commit/push them together.
No new bot was promoted and no scrimmage was requested by this cloud session.
