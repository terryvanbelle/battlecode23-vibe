# Live recovery check

Updated October 12, 2026, 13:14 PDT from this Codex web session.

The web worker authenticated to the existing `claude-driver` VM and reached `battlecode-dev` with strict SSH host-key
verification. The replica is https://galaxy.136-86-167-127.sslip.io/; no work moved to a CLI conversation.

At 13:05 PDT the contestant API saved and returned `vibe23` (team 28)'s quote:

> Codex web connection verified - Oct 12, 2026, 01:05 PM PDT

The owner confirmed seeing this on the replica's My Team page. The active submission stayed unchanged.

| Item | Verified state |
| --- | --- |
| Validated bot | `g_iter10 = c_mend2`, active submission 145 |
| Parked candidate | `c_bc3`, submission 144: 100 complete cells, 61 wins, identical win/loss outcomes to `c_mend2` |
| Candidate decision | Keep `c_mend2` active; establish actual method cost savings before accepting `c_bc3` |
| `c_well9` | Screen failed: 9–11 head-to-head, no gain in the gating roster |
| `c_ward3` | Recorded queue job missing; recover the reference cache and resume its screen |
| Tool checks | Driver passed the repaired rating, collector and worker checks; full official-engine suite running since 13:11 PDT |

Result exports and charts are being refreshed. Missing old field-only replays will be recorded separately in
`field-replay-gaps.jsonl`; they contribute no invented winners to `games.csv`. Rating deduplication now keeps A/B labels
as part of simulation identity. See [HANDOFF](../HANDOFF.md) and [continuation instructions](../docs/CONTINUATION.md).
