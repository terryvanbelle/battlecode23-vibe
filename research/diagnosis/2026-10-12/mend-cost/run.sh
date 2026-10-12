#!/usr/bin/env bash
# Zero-game method measurement. Default requires the pinned official engine.
set -euo pipefail
if [[ ${BC23_MEND_COST_WRAPPED-} != 1 ]]; then
  exec timeout --kill-after=5s 180s env BC23_MEND_COST_WRAPPED=1 bash "$0" "$@"
fi
umask 077
MEND_PROTOTYPE=false
if [[ ${1-} == --prototype ]]; then MEND_PROTOTYPE=true; shift; fi
MEND_REPO=${1:?usage: run.sh [--prototype] <repo> [fresh output directory] (optional MEND_CANDIDATE_SOURCE directory)}
MEND_REPO=$(cd "$MEND_REPO" && pwd)
MEND_HERE=$(cd "$(dirname "$0")" && pwd)
MEND_CANDIDATE_SOURCE=${MEND_CANDIDATE_SOURCE:-$MEND_REPO/src/c_mend3}
MEND_OUTPUT=${2:-$(mktemp -d /tmp/bc23-mend3-cost.XXXXXX)}
mkdir -p "$MEND_OUTPUT"
MEND_OUTPUT=$(cd "$MEND_OUTPUT" && pwd)
MEND_JAR="$MEND_REPO/engine/battlecode23-3.0.15.jar"
MEND_RELEASE_SHA=5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a
MEND_JAR_SHA=$(sha256sum "$MEND_JAR" | cut -d' ' -f1)
if [[ $MEND_PROTOTYPE == false ]]; then
  case $(hostname -s) in claude-driver|battlecode-dev) ;; *) echo 'release probe requires an existing 2023 worker' >&2; exit 3 ;; esac
  [[ $MEND_JAR_SHA == "$MEND_RELEASE_SHA" ]] || { echo 'official engine checksum mismatch' >&2; exit 3; }
fi
export JAVA_HOME=${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}
export PATH="$JAVA_HOME/bin:$PATH"
java -version 2> "$MEND_OUTPUT/java-version.txt"
grep -Eq 'version "1\.8\.' "$MEND_OUTPUT/java-version.txt" || { echo 'JDK8 required' >&2; exit 3; }
mend_hash() {
  local mend_root=$1 mend_package=$2 mend_file
  for mend_file in "$mend_root/$mend_package"/*.java; do
    sed -e "s/^package $mend_package;/package PKG;/" -e "s/^import $mend_package\./import PKG./" -e "s/^import static $mend_package\./import static PKG./" "$mend_file"
  done | sha1sum | cut -c1-12
}
[[ ! -e "$MEND_OUTPUT/source" && ! -e "$MEND_OUTPUT/bots" && ! -e "$MEND_OUTPUT/host" ]] || { echo 'use a fresh private output directory' >&2; exit 3; }
mkdir "$MEND_OUTPUT/source" "$MEND_OUTPUT/bots" "$MEND_OUTPUT/host"
python3 - "$MEND_REPO/src/c_mend2" "$MEND_CANDIDATE_SOURCE" <<'PY'
import sys
from pathlib import Path
names={name+'.java' for name in ('Amplifier','C','Carrier','Comms','Field','G','HQ','HQState','Launcher','MapMem','Nav','Other','RobotPlayer','Telemetry','Wells')}
for value in sys.argv[1:]:
    source=Path(value)
    if source.is_symlink() or not source.is_dir():
        raise SystemExit('frozen package source must be a regular directory')
    entries=list(source.iterdir())
    if {entry.name for entry in entries} != names or any(entry.is_symlink() or not entry.is_file() for entry in entries):
        raise SystemExit('frozen package source must contain exactly the fifteen known regular Java files')
PY
cp -a "$MEND_REPO/src/c_mend2" "$MEND_OUTPUT/source/c_mend2"
cp -a "$MEND_CANDIDATE_SOURCE" "$MEND_OUTPUT/source/c_mend3"
MEND_BASE_HASH=$(mend_hash "$MEND_OUTPUT/source" c_mend2)
MEND_CANDIDATE_HASH=$(mend_hash "$MEND_OUTPUT/source" c_mend3)
[[ $MEND_BASE_HASH == d62033781fbd && $MEND_CANDIDATE_HASH == db9f54f47fea ]] || { echo 'frozen own source hash mismatch' >&2; exit 3; }
find "$MEND_OUTPUT/source" -type f -name '*.java' -print | sort > "$MEND_OUTPUT/sources.list"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$MEND_JAR" -d "$MEND_OUTPUT/bots" @"$MEND_OUTPUT/sources.list"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$MEND_JAR" -d "$MEND_OUTPUT/bots" "$MEND_HERE/ApiCalibration.java"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$MEND_JAR" -d "$MEND_OUTPUT/host" "$MEND_HERE/MendCostProbe.java"
python3 - "$MEND_OUTPUT" "$MEND_PROTOTYPE" "$MEND_JAR_SHA" "$MEND_BASE_HASH" "$MEND_CANDIDATE_HASH" "$MEND_HERE" <<'PY'
import hashlib,json,sys
from pathlib import Path
out,prototype,engine,baseline,candidate,source=sys.argv[1:]
p=Path(out);s=Path(source)
info={'prototype_only':prototype=='true','engine_sha256':engine,'c_mend2_hash':baseline,'c_mend3_hash':candidate,
      'probe_sha256':hashlib.sha256((s/'MendCostProbe.java').read_bytes()).hexdigest(),
      'calibration_sha256':hashlib.sha256((s/'ApiCalibration.java').read_bytes()).hexdigest(),
      'java_version':(p/'java-version.txt').read_text().strip(),'method':'mendUpdate','games_run':0,
      'note':'Own frozen classes only; API bodies/setup excluded, API callsite charges included. Pending debt asserted zero. Finite real method-entry budgets; reserve overshoots reported, never hidden. Method probe does not measure the later fight/march tail.'}
(p/'provenance.json').write_text(json.dumps(info,sort_keys=True)+'\n')
print(json.dumps({'provenance':info},sort_keys=True))
PY
timeout 165 java -Xmx512m -XX:+UseSerialGC -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false \
  -cp "$MEND_OUTPUT/host:$MEND_JAR" MendCostProbe "$MEND_OUTPUT/bots" "$MEND_OUTPUT/result.json"
