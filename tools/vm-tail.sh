#!/usr/bin/env bash
# Show the tail of a detached VM job's log:  tools/vm-tail.sh <name> [lines]
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; source "$REPO/tools/vm.sh"; IP="${IP:-10.138.0.3}"
gssh "tail -n ${2:-20} ~/$REMOTE_REPO/logs/$1.log"
