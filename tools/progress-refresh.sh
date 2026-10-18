#!/usr/bin/env bash
# Refresh progress/ (CLAUDE.md rule 8): galaxy results -> games.csv, Elo and field-score charts, rating history, ladder
# snapshot, reports for our unreported matches, the attempts table (progress/ATTEMPTS.md, owner PROMPTS 130). Run
# from the session on a HEARTBEAT; commit progress/ and research/matches/ after.
# A step that fails or times out is named ("!! <step> FAILED") and the script exits 1: until 2026-10-16 a killed step
# was silent, and rating-history.md stayed a day stale through two refreshes (owner, PROMPTS 121).
cd "$(dirname "$0")/.."
LOG="$(mktemp)"; trap 'rm -f "$LOG"' EXIT; FAILS=()
step () {   # step <name> <timeout s> <lines of output kept> <command ...>
  local name="$1" t="$2" n="$3" rc; shift 3
  echo "== $name"
  timeout "$t" "$@" > "$LOG" 2>&1; rc=$?
  tail -"$n" "$LOG"
  if [ "$rc" -ne 0 ]; then
    echo "!! $name FAILED (exit $rc$([ "$rc" = 124 ] && echo ", timed out after ${t} s"))"; FAILS+=("$name")
  fi
}
echo "== start $(date -u +%H:%M)"
step results 5400 3 python3 tools/galaxy/results.py
step elo 900 2 tools/.venv/bin/python tools/elo.py --quiet
step "field score" 900 3 tools/.venv/bin/python tools/field_score.py
step "rating history" 900 2 tools/.venv/bin/python tools/rating_history.py
step snapshot 900 2 tools/.venv/bin/python tools/galaxy/snapshot.py
step sweep 5400 4 env MATCH_REPORT_MIN_FREE_GB=1 python3 tools/match_report.py sweep --pages 10 --max 40
step attempts 120 2 python3 tools/attempts.py refresh
echo "== done $(date -u +%H:%M)"
if [ "${#FAILS[@]}" -gt 0 ]; then echo "!! failed steps: ${FAILS[*]} (their progress/ files are stale)"; exit 1; fi
