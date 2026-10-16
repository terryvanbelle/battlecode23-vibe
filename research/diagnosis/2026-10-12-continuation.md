# Continuing from the web interface with the existing VMs

> **Archived 2026-10-15** (was `docs/CONTINUATION.md`). It describes the 2026-10-12 continuation through the Codex web
> session. Since 2026-10-14 the CLI session on claude-driver runs the project; see `HANDOFF.md` for the current state.

Updated 2026-10-12 PDT. **All ongoing owner interaction remains in the web interface** (PROMPTS 58). The original
driver and `battlecode-dev` are compute workers; do not transfer project control to a CLI session or require ongoing
CLI interaction. The private GitHub worker now connects this web session to the original driver account and checkout.
Authenticated driver inspection and strict host-key-checked internal SSH to battlecode-dev succeeded on 2026-10-12.
GCP credentials remain on the driver. The authoritative live files, replays and running jobs remain on the original VMs.
Publish every completed update to `main`, including generated progress, as the owner instructed in PROMPTS 69–70.
The owner confirmed this agent is the only repository writer; a continuation branch alone is not publication.

## Establish remote access from the web environment

The owner authorizes one-time setup commands while requiring ongoing web interaction (PROMPTS 58–59). The environment
Edit assistant confirmed that this instance has VPN disabled and no TCP grants, and that its available tools cannot
configure either (PROMPTS 61). Its SSH helper does not establish a route. Do not request more guesses about settings,
enroll a VPN that this web instance cannot use, or treat an HTTP allowlist as raw TCP authorization.

The selected route is a **private GitHub control repository with a repository-scoped Actions runner on claude-driver**.
The runner picks up jobs through outbound HTTPS. This web session writes the trusted job and request, and reads a
bounded JSON response from that private repository. Existing GCP/SSH credentials remain on the driver. The driver
then reuses its existing access to battlecode-dev; no new incoming VM port is needed.

Follow [WEB_WORKER_SETUP.md](../../docs/WEB_WORKER_SETUP.md) for the concrete one-time setup. The public bot repository contains
the installer and workflow template only; never register this credential-bearing runner to the public repository.
The private repo's writers have command access as the driver account, so keep access limited to the owner and intended
GitHub connection. This transport executes trusted jobs; it is not a sandbox.

The runner is installed as a service and the initial inspection returned successfully through the private response
channel with the expected request ID and job hash. A follow-up preserved all 37 dirty driver files in
`build/codex-recovery/20261012T191037Z` and verified internal SSH plus active replica services. The current cloud policy
still has no VPN/TCP route; the GitHub worker does not change it.

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
   assumes the driver keeps exporting results. Our-team replays are exempt. The repaired collector records eligible
   old field-only HTTP 404/410 gaps separately in `progress/field-replay-gaps.jsonl`, without inventing game results.
   Our-team, recent and tournament replay failures still stop collection. Check for orphaned queue jobs before
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
| Other work | c_well9 collected: FAIL (9–11 head-to-head, roster Net 0); c_ward3's recorded queue job is missing |

Recovery verified the existing c_bc3 panel's 100 unique cells and all ten terminal matches. It won 61/100, with
identical cell outcomes to c_mend2 and no coin flips; it remains parked until actual `computePredWells` cost savings
are established. End-of-turn bytecode counts include other work and do not establish that mechanism. If re-collection
is needed, use the existing panel instead of `trial-start` again. The collector supports
`RESUME=<existing run directory> python3 tools/contest.py block test/cells/panel-v1.txt --tag panel-c_bc3`.
Confirm the submission recorded in `requests.jsonl` and that all requested matches belong to this panel first.
The current collector can write `results.csv` after a timeout, and the policy treats its existence as completion:
**check all 100 cells and terminal match statuses explicitly before any accept**. Then compare against both references
with `tools/paired.py`, inspect bytecode savings, overruns and exceptions, and use `trial-decide` for the parked trial.

Reconcile the reference cache and c_ward3's missing queue job before enqueueing its screen. c_well7, c_end2, c_lane2 and
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
- Rating deduplication preserves team A/B labels as observable simulation inputs. Swapped labels with reversed
  spawns are distinct games, even when the same named team owns the same HQ locations; original CSV rows stay intact.
- The worker's bootstrap test fixture reads its two named files explicitly, supporting the driver's Python 3.9.

## Browser-visible connection proof

On 2026-10-12 at 13:05 PDT the worker changed team `vibe23` (ID 28)'s profile quote through the contestant API to
`Codex web connection verified - Oct 12, 2026, 01:05 PM PDT`, read it back, and verified the active submission stayed
unchanged. The owner confirmed seeing it on `/bc23/my_team` (PROMPTS 67). The previous quote is preserved on the driver
in `build/codex-recovery/team-quote-before-20261012.json`; only the quote was changed.

## Verification and adoption

Run `tools/unit-tests.sh` on the driver with the existing **checksum-pinned official 3.0.15 jar** for these
changes. The initial driver run compiled all 79 bot packages and passed the bot, analysis, ranked/token, report,
replica and Galaxy checks; it failed the Python 3.9 bootstrap fixture and the incorrect cross-label replay invariant.
The corrected driver rerun passed at code commit `83ae37a`, 13:11:10–13:33:38 PDT on 2026-10-12, with exit 0 and no
timeout. All 79 packages and the bot/tool/replica checks passed; the report suite had two existing skips.
This cloud session installed JDK 8 and built the
official tag's source for local unit/fixture checks only;
that temporary jar is gitignored, has a different checksum, and is never for deployment or trial judgments.
The instrument and concurrency regressions pass locally (111 analysis tests, one skip, plus 3 ranked and 2 token
regressions); release-backed compile integration requires the official jar.
Do not weaken the pin to make a source-built jar pass.

After reconciling local changes, apply the branch's changes, run the full suite, and restart only the affected driver
processes by PID. Changes to deployed tools need the established VM workflow after the live tree is preserved.
Resume result exports, snapshots and charts using the established contestant/API tools, and commit/push them together.
No new bot was promoted and no scrimmage was requested by this cloud session.
