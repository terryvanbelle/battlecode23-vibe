#!/usr/bin/env bash
# Refresh progress/ (CLAUDE.md rule 8): galaxy results -> games.csv, Elo and field-score charts, rating history, ladder
# snapshot, reports for our unreported matches. Run from the session on a HEARTBEAT; commit progress/ and research/matches/ after.
cd "$(dirname "$0")/.."
echo "== results $(date -u +%H:%M)"; timeout 5400 python3 tools/galaxy/results.py 2>&1 | tail -3
echo "== elo"; timeout 900 tools/.venv/bin/python tools/elo.py --quiet 2>&1 | tail -2
echo "== field score"; timeout 900 tools/.venv/bin/python tools/field_score.py 2>&1 | tail -3
echo "== rating history"; timeout 900 tools/.venv/bin/python tools/rating_history.py 2>&1 | tail -2
echo "== snapshot"; timeout 900 tools/.venv/bin/python tools/galaxy/snapshot.py 2>&1 | tail -2
echo "== sweep"; MATCH_REPORT_MIN_FREE_GB=1 timeout 5400 python3 tools/match_report.py sweep --pages 10 --max 40 2>&1 | tail -4
echo "== done $(date -u +%H:%M)"
