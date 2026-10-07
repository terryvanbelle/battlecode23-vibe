#!/usr/bin/env bash
# The VM's standing job runner (adapted from the 2024 project; there the VM idled ~29% of its uptime between runs).
# Runs ~/projects/vibe/2023/queue/pending/*.job in name order, one at a time, each as a bash script from the repo root
# with its log in logs/<job>.log; finished jobs move to queue/done. When nothing is pending it runs queue/filler.job (if
# present) once per idle period, so the VM never sits empty. One runner only (flock). A job that fails within 30 s
# makes the runner back off (a disk-full queue once spun for 18 minutes).
#   start (from the driver): tools/vm-run.sh queue-runner 'bash tools/vm-queue.sh'
#   enqueue: tools/vm-enqueue.sh <name> '<command>'      stop: touch queue/STOP on the VM
# Runs from a private copy: vm_sync replaces tools/ under a running script.
if [ -z "${BC23_QREEXEC:-}" ]; then
  _self="/tmp/.vm-queue.$$"; cat "${BASH_SOURCE[0]}" > "$_self" || exit 1
  BC23_QREEXEC="$_self" exec bash "$_self" "$@"
fi
rm -f "$BC23_QREEXEC"
REPO="$HOME/projects/vibe/2023"; Q="$REPO/queue"; mkdir -p "$Q/pending" "$Q/running" "$Q/done" "$REPO/logs"
exec 9>"$Q/.lock"; flock -n 9 || { echo "another queue runner holds $Q/.lock"; exit 0; }
cd "$REPO"
while true; do
  [ -f "$Q/STOP" ] && { echo "$(date -u +%FT%TZ) STOP file present: exiting"; rm -f "$Q/STOP"; exit 0; }
  J="$(ls "$Q/pending/"*.job 2>/dev/null | sort | head -1)"
  if [ -n "$J" ]; then
    N="$(basename "$J" .job)"; mv "$J" "$Q/running/$N.job"
    echo "$(date -u +%FT%TZ) start $N"; t0=$(date +%s)
    bash "$Q/running/$N.job" > "logs/$N.log" 2>&1 < /dev/null
    rc=$?; echo "$(date -u +%FT%TZ) done $N (exit $rc)"; mv "$Q/running/$N.job" "$Q/done/$N.job"
    if [ $rc -ne 0 ] && [ $(( $(date +%s) - t0 )) -lt 30 ]; then echo "fast failure: backing off 120 s"; sleep 120; fi
  elif [ -f "$Q/filler.job" ]; then
    N="filler-$(date -u +%Y%m%d-%H%M%S)"; echo "$(date -u +%FT%TZ) idle: $N"; t0=$(date +%s)
    bash "$Q/filler.job" > "logs/$N.log" 2>&1 < /dev/null
    rc=$?; [ $rc -ne 0 ] && [ $(( $(date +%s) - t0 )) -lt 30 ] && { echo "filler fast failure: backing off 300 s"; sleep 300; }
  else
    sleep 15
  fi
done
