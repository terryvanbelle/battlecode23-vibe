#!/usr/bin/env bash
# Stop one of our detached VM jobs (tools/vm-run.sh) by its process group, on battlecode-dev only (owner, PROMPTS 124).
#   tools/vm-stop.sh <name>        # the job vm-run.sh started as <name>: its pgid is in logs/<name>.pgid on the VM
#   tools/vm-stop.sh --pgid N      # a job started before vm-run.sh recorded pgids
# The group gets SIGTERM (the job's shell, gauntlet, xargs and game JVMs) and logs/<name>.log a line saying so.
# Refuses: any VM but battlecode-dev (CLAUDE rule 1: battlecode-dev2 is never touched); a name outside
# [A-Za-z0-9._-]; a pgid that is not a number; a group whose leader is not a bash process running in our repo on the
# VM (its working directory must be ~/projects/vibe/2023), so the galaxy replica, its runner and other projects' jobs
# are out of reach. DRY=1 prints the remote command instead of running it.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
usage() { echo "usage: tools/vm-stop.sh <name> | --pgid N" >&2; exit 2; }
[ $# -ge 1 ] || usage
if [ "$1" = "--pgid" ]; then
  [ $# -eq 2 ] && [[ "$2" =~ ^[0-9]+$ ]] || { echo "vm-stop: --pgid takes a number" >&2; exit 2; }
  NAME=""; PGID_SRC="echo $2"
else
  [ $# -eq 1 ] && [[ "$1" =~ ^[A-Za-z0-9._-]+$ ]] && [[ "$1" != .* ]] || { echo "vm-stop: bad job name '$1'" >&2; exit 2; }
  NAME="$1"; PGID_SRC="cat logs/$NAME.pgid 2>/dev/null"
fi
source "$REPO/tools/vm.sh"
[ "$VM" = battlecode-dev ] || { echo "vm-stop: refusing VM '$VM' (battlecode-dev only)" >&2; exit 2; }
note=""
[ -n "$NAME" ] && note="echo \"[vm-stop] stopped \$(date -u +%FT%TZ): SIGTERM to process group \$g\" >> logs/$NAME.log;"
REMOTE="cd ~/$REMOTE_REPO || exit 3; g=\$($PGID_SRC); [ -n \"\$g\" ] || { echo 'vm-stop: no pgid recorded for that job'; exit 3; };
case \"\$g\" in *[!0-9]*) echo \"vm-stop: bad pgid \$g\"; exit 3;; esac;
[ \"\$(ps -o pgid= -p \$g 2>/dev/null | tr -d ' ')\" = \"\$g\" ] || { echo \"vm-stop: \$g is not a running group leader\"; exit 3; };
case \"\$(ps -o comm= -p \$g)\" in bash) ;; *) echo \"vm-stop: leader of \$g is not bash\"; exit 3;; esac;
[ \"\$(readlink /proc/\$g/cwd)\" = \"\$HOME/$REMOTE_REPO\" ] || { echo \"vm-stop: \$g does not run in our repo\"; exit 3; };
echo \"vm-stop: group \$g: \$(ps -o pid= -g \$g | wc -l) processes; leader: \$(ps -o args= -p \$g | cut -c1-120)\";
kill -TERM -- -\$g && $note echo \"vm-stop: SIGTERM sent to group \$g\""
if [ "${DRY:-0}" = 1 ]; then echo "$REMOTE"; exit 0; fi
ensure_vm
gssh "$REMOTE"
