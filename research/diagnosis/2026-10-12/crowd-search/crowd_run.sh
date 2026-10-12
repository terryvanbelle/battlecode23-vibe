#!/usr/bin/env bash
# Own-source zero-game native fixture. --prototype permits local source-built engine for structural checks.
set -euo pipefail
CROWD_PROTOTYPE=false
if [[ ${1-} == --prototype ]]; then CROWD_PROTOTYPE=true;shift;fi
CROWD_REPO=${1:?usage: crowd_run.sh [--prototype] REPO NEW_OUTPUT}
CROWD_REPO=$(cd "$CROWD_REPO" && pwd)
CROWD_OUTPUT=${2:?supply a new private output directory}
CROWD_HERE=$(cd "$(dirname "$0")" && pwd)
CROWD_JAR="$CROWD_REPO/engine/battlecode23-3.0.15.jar"
CROWD_ENGINE_SHA=$(sha256sum "$CROWD_JAR"|cut -d' ' -f1)
if [[ $CROWD_PROTOTYPE == false ]];then
 [[ $(hostname -s) == battlecode-dev ]] || { echo 'official fixture must run on battlecode-dev' >&2;exit 3; }
 [[ $CROWD_ENGINE_SHA == 5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a ]] || { echo 'official engine checksum mismatch' >&2;exit 3; }
fi
[[ ! -e "$CROWD_OUTPUT" ]] || { echo 'use a new output directory' >&2;exit 3; }
mkdir -p "$CROWD_OUTPUT/helpers" "$CROWD_OUTPUT/classes" "$CROWD_OUTPUT/host"
CROWD_OUTPUT=$(cd "$CROWD_OUTPUT" && pwd)
cp "$CROWD_HERE/CarrierCrowdProbe.java" "$CROWD_HERE/crowd_source.py" "$CROWD_HERE/crowd_run.sh" "$CROWD_OUTPUT/helpers/"
export JAVA_HOME=${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}
export PATH="$JAVA_HOME/bin:$PATH"
java -version 2> "$CROWD_OUTPUT/java-version.txt"
grep -Eq 'version "1\.8\.' "$CROWD_OUTPUT/java-version.txt" || { echo 'JDK8 required' >&2;exit 3; }
python3 "$CROWD_OUTPUT/helpers/crowd_source.py" "$CROWD_REPO" "$CROWD_OUTPUT/source"
crowd_hash(){
 local crowd_pkg=$1 crowd_file
 for crowd_file in "$CROWD_OUTPUT/source/$crowd_pkg"/*.java;do
  sed -e "s/^package $crowd_pkg;/package PKG;/" -e "s/^import $crowd_pkg\./import PKG./" -e "s/^import static $crowd_pkg\./import static PKG./" "$crowd_file"
 done |sha1sum|cut -c1-12
}
CROWD_BASE_HASH=$(crowd_hash c_mend2)
CROWD_PATCH_HASH=$(crowd_hash c_crowdprobe)
[[ $CROWD_BASE_HASH == d62033781fbd ]] || { echo 'frozen baseline source hash mismatch' >&2;exit 3; }
find "$CROWD_OUTPUT/source" -name '*.java' -print |sort > "$CROWD_OUTPUT/source.list"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$CROWD_JAR" -d "$CROWD_OUTPUT/classes" @"$CROWD_OUTPUT/source.list"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$CROWD_JAR" -d "$CROWD_OUTPUT/host" "$CROWD_OUTPUT/helpers/CarrierCrowdProbe.java"
python3 - "$CROWD_OUTPUT" "$CROWD_PROTOTYPE" "$CROWD_ENGINE_SHA" "$CROWD_BASE_HASH" "$CROWD_PATCH_HASH" <<'PY'
import hashlib,json,sys
from pathlib import Path
out,prototype,engine,base,patch=sys.argv[1:];p=Path(out)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
info={'games_run':0,'prototype_only':prototype=='true','engine_sha256':engine,'base_hash':base,'scratch_patch_hash':patch,
      'java_version':(p/'java-version.txt').read_text().strip(),
      'helper_sha256':{f.name:sha(f) for f in sorted((p/'helpers').iterdir())},
      'source_sha256':{str(f.relative_to(p/'source')):sha(f) for f in sorted((p/'source').rglob('*.java'))},
      'note':'Structural gather/deliver fixture; mock controller and host setup unmetered. Pending instrumentation debt checked. Source-built prototype cost is not release cost. No full run, games, HQ changes, radius changes, role ratio or navigation patch.'}
(p/'provenance.json').write_text(json.dumps(info,sort_keys=True,indent=2)+'\n')
print(json.dumps({'provenance':str(p/'provenance.json'),'prototype_only':info['prototype_only'],'base_hash':base,'scratch_patch_hash':patch,'games_run':0},sort_keys=True))
PY
nice -n5 timeout --foreground -k10s 60 java -Xmx512m -XX:+UseSerialGC -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false \
 -cp "$CROWD_OUTPUT/host:$CROWD_JAR" CarrierCrowdProbe "$CROWD_OUTPUT/classes" "$CROWD_OUTPUT/result.json"
