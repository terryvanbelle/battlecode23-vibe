#!/usr/bin/env bash
set -euo pipefail
SEAM_PROTOTYPE=false
if [[ ${1-} == --prototype ]];then SEAM_PROTOTYPE=true;shift;fi
SEAM_REPO=${1:?usage: seam_run.sh [--prototype] REPO FROZEN409_SOURCE NEW_OUTPUT}
SEAM_REPO=$(cd "$SEAM_REPO" && pwd)
SEAM_FROZEN=${2:?frozen409 source directory required}
SEAM_FROZEN=$(cd "$SEAM_FROZEN" && pwd)
SEAM_OUTPUT=${3:?use a new private output}
SEAM_HERE=$(cd "$(dirname "$0")" && pwd)
SEAM_JAR="$SEAM_REPO/engine/battlecode23-3.0.15.jar"
SEAM_ENGINE=$(sha256sum "$SEAM_JAR"|cut -d' ' -f1)
if [[ $SEAM_PROTOTYPE == false ]];then
 [[ $(hostname -s) == battlecode-dev && $SEAM_ENGINE == 5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a ]] || { echo 'official zero-game proof requires battlecode-dev and pinned release jar' >&2;exit 3; }
fi
[[ ! -e "$SEAM_OUTPUT" ]] || { echo 'output exists' >&2;exit 3; }
mkdir -p "$SEAM_OUTPUT/helpers" "$SEAM_OUTPUT/host" "$SEAM_OUTPUT/reference/classes" "$SEAM_OUTPUT/repair/classes"
SEAM_OUTPUT=$(cd "$SEAM_OUTPUT" && pwd)
for SEAM_FILE in CarrierCrowdProbe.java ExploreGuardProbeV2.java FrontierProbeV2.java FrontierIdentity.java SeamProbe.java SeamRepairProbe.java frontier_source_v5.py frontier_source.py seam_run.sh SEAM_PROTOCOL.md;do
 cp "$SEAM_HERE/$SEAM_FILE" "$SEAM_OUTPUT/helpers/"
done
export JAVA_HOME=${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}
export PATH="$JAVA_HOME/bin:$PATH"
java -version 2> "$SEAM_OUTPUT/java-version.txt"
grep -Fq 'version "1.8.0_504"' "$SEAM_OUTPUT/java-version.txt" || { echo 'JDK8u504 required' >&2;exit 3; }
python3 "$SEAM_OUTPUT/helpers/frontier_source_v5.py" "$SEAM_FROZEN" "$SEAM_OUTPUT/reference/source"
python3 "$SEAM_OUTPUT/helpers/frontier_source.py" "$SEAM_FROZEN" "$SEAM_OUTPUT/repair/source"
python3 - "$SEAM_OUTPUT" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);expect={'reference':{'c_mend2':'d62033781fbd','c_frontier0':'226e6b36d330','c_frontier12':'e4ba60fec324','c_frontier24':'2d68c1ace68f'},'repair':{'c_mend2':'d62033781fbd','c_frontier0':'9a9dc1b0f12f','c_frontier12':'dea201597e9b','c_frontier24':'5e11b3da11c9'}}
for key,pins in expect.items():assert json.loads((p/key/'source/source-hashes.json').read_text())==pins
PY
for SEAM_KIND in reference repair;do
 find "$SEAM_OUTPUT/$SEAM_KIND/source" -name '*.java' -print|sort > "$SEAM_OUTPUT/$SEAM_KIND/source.list"
 javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$SEAM_JAR" -d "$SEAM_OUTPUT/$SEAM_KIND/classes" @"$SEAM_OUTPUT/$SEAM_KIND/source.list"
done
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$SEAM_JAR" -d "$SEAM_OUTPUT/host" "$SEAM_OUTPUT/helpers/CarrierCrowdProbe.java" "$SEAM_OUTPUT/helpers/ExploreGuardProbeV2.java" "$SEAM_OUTPUT/helpers/FrontierProbeV2.java" "$SEAM_OUTPUT/helpers/FrontierIdentity.java" "$SEAM_OUTPUT/helpers/SeamProbe.java" "$SEAM_OUTPUT/helpers/SeamRepairProbe.java"
for SEAM_KIND in reference repair;do
 timeout --foreground -k10s 30 java -Xmx512m -cp "$SEAM_OUTPUT/host:$SEAM_JAR" FrontierIdentity "$SEAM_OUTPUT/$SEAM_KIND/classes" > "$SEAM_OUTPUT/$SEAM_KIND/zero-identity.json"
done
nice -n5 timeout --foreground -k10s 60 java -Xmx512m -XX:+UseSerialGC -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false -cp "$SEAM_OUTPUT/host:$SEAM_JAR" SeamProbe "$SEAM_OUTPUT/reference/classes" "$SEAM_OUTPUT/reference/result.json"
nice -n5 timeout --foreground -k10s 60 java -Xmx512m -XX:+UseSerialGC -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false -cp "$SEAM_OUTPUT/host:$SEAM_JAR" SeamRepairProbe "$SEAM_OUTPUT/repair/classes" "$SEAM_OUTPUT/repair/result.json"
python3 - "$SEAM_OUTPUT" "$SEAM_JAR" "$SEAM_PROTOTYPE" <<'PY'
import hashlib,json,sys,zipfile
from pathlib import Path
p,jar=map(Path,sys.argv[1:3]);prototype=sys.argv[3]=='true'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
with zipfile.ZipFile(jar) as z:mapsha=hashlib.sha256(z.read('battlecode/world/resources/Forest.map23')).hexdigest()
data={}
for key in ('reference','repair'):
 identity=json.loads((p/key/'zero-identity.json').read_text());assert identity['methods']==222 and identity['zero_arm_existing_method_identity']
 data[key]={'source_pins':json.loads((p/key/'source/source-hashes.json').read_text()),'zero_identity':identity,'result_sha256':sha(p/key/'result.json'),'source_sha256':{str(f.relative_to(p/key/'source')):sha(f) for f in sorted((p/key/'source').rglob('*.java'))}}
info={'server_games_run':0,'prototype_engine':prototype,'engine_sha256':sha(jar),'forest_map23_sha256':mapsha,'java_version':(p/'java-version.txt').read_text().strip(),'helper_sha256':{f.name:sha(f) for f in sorted((p/'helpers').iterdir())},'arms':data,'limit':'Actual native RC/controller API fixtures, manuallyinitialized state/inertotherrobots, plus labelled syntheticlogical cases. FullRobotPlayer/bookkeeping/nearmiss/yield/scheduler/nativefullbotgame notrun; no screen or promotion.'}
(p/'provenance.json').write_text(json.dumps(info,sort_keys=True,indent=2)+'\n')
print(json.dumps({'server_games_run':0,'prototype_engine':prototype,'arms':{key:{'source_pins':v['source_pins'],'zero_methods':v['zero_identity']['methods'],'result_sha256':v['result_sha256']} for key,v in data.items()}},sort_keys=True))
PY
