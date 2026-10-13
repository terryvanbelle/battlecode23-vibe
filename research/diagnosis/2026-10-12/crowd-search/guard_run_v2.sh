#!/usr/bin/env bash
# No server games: own method checks and a real-engine API state fixture.
set -euo pipefail
GUARD_PROTOTYPE=false
if [[ ${1-} == --prototype ]];then GUARD_PROTOTYPE=true;shift;fi
GUARD_REPO=${1:?usage: guard_run_v2.sh [--prototype] REPO FROZEN_CROWD_SOURCE NEW_OUTPUT}
GUARD_REPO=$(cd "$GUARD_REPO" && pwd)
GUARD_FROZEN=${2:?frozen proved crowd source required}
GUARD_FROZEN=$(cd "$GUARD_FROZEN" && pwd)
GUARD_OUTPUT=${3:?use a new private output}
GUARD_HERE=$(cd "$(dirname "$0")" && pwd)
GUARD_JAR="$GUARD_REPO/engine/battlecode23-3.0.15.jar"
[[ ! -e "$GUARD_OUTPUT" ]] || { echo 'output exists' >&2;exit 3; }
mkdir -p "$GUARD_OUTPUT/helpers" "$GUARD_OUTPUT/host"
GUARD_OUTPUT=$(cd "$GUARD_OUTPUT" && pwd)
for GUARD_FILE in CarrierCrowdProbe.java Explore1Probe.java BytecodeIdentity.java explore_source.py explore_run.sh ExploreGuardProbeV2.java guard_run_v2.sh;do
 cp "$GUARD_HERE/$GUARD_FILE" "$GUARD_OUTPUT/helpers/"
done
if [[ $GUARD_PROTOTYPE == true ]];then
 bash "$GUARD_OUTPUT/helpers/explore_run.sh" --prototype "$GUARD_REPO" "$GUARD_FROZEN" "$GUARD_OUTPUT/own-fixture" > "$GUARD_OUTPUT/own-fixture.log" 2>&1
else
 bash "$GUARD_OUTPUT/helpers/explore_run.sh" "$GUARD_REPO" "$GUARD_FROZEN" "$GUARD_OUTPUT/own-fixture" > "$GUARD_OUTPUT/own-fixture.log" 2>&1
fi
export JAVA_HOME=${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}
export PATH="$JAVA_HOME/bin:$PATH"
python3 - "$GUARD_OUTPUT" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);info=json.loads((p/'own-fixture/provenance.json').read_text())
assert info['c_explore1_hash']=='409cfdfcbfd8' and info['c_explore0_hash']=='cc6a4611d061'
assert info['base_hash']=='d62033781fbd' and info['zero_identity']['methods']==222
PY
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$GUARD_JAR:$GUARD_OUTPUT/own-fixture/host" -d "$GUARD_OUTPUT/host" "$GUARD_OUTPUT/helpers/ExploreGuardProbeV2.java"
nice -n5 timeout --foreground -k10s 60 java -Xmx512m -XX:+UseSerialGC -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false \
 -cp "$GUARD_OUTPUT/host:$GUARD_OUTPUT/own-fixture/host:$GUARD_JAR" ExploreGuardProbeV2 "$GUARD_OUTPUT/own-fixture/classes" "$GUARD_OUTPUT/result.json"
python3 - "$GUARD_OUTPUT" "$GUARD_JAR" <<'PY'
import hashlib,json,sys,zipfile
from pathlib import Path
p,jar=map(Path,sys.argv[1:]);base=json.loads((p/'own-fixture/provenance.json').read_text())
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
with zipfile.ZipFile(jar) as z:mapsha=hashlib.sha256(z.read('battlecode/world/resources/Forest.map23')).hexdigest()
result=json.loads((p/'result.json').read_text())
assert result['server_games_run']==0 and result['fixture_worlds']==55
info={'server_games_run':0,'mode':'actual_GameWorld_RC_API_fixture_clean_symmetry7_and2',
 'prototype_engine':base['prototype_engine'],'engine_sha256':base['engine_sha256'],'forest_map23_sha256':mapsha,
 'java_version':base['java_version'],'source_pin':{'base':'d62033781fbd','enabled':'409cfdfcbfd8','zero':'cc6a4611d061'},
 'helper_sha256':{f.name:sha(f) for f in sorted((p/'helpers').iterdir())},'own_fixture_provenance_sha256':sha(p/'own-fixture/provenance.json'),
 'own_fixture_result_sha256':sha(p/'own-fixture/result.json'),'result_sha256':sha(p/'result.json'),
 'own_fixture':base,'limit':'Actual native world/controller physics; manually initialized owner/memory/blockers. Full RobotPlayer loop, scheduling, competing bot turns and general game delivery/budget gate remain absent.'}
(p/'provenance.json').write_text(json.dumps(info,sort_keys=True,indent=2)+'\n')
quick=[]
for budget in sorted({c['budget'] for c in result['cases']}):
 worst=min((c for c in result['cases'] if c['budget']==budget),key=lambda c:c['after_tail'])
 quick.append({'budget':budget,'worst_after_tail':worst['after_tail'],'worst_gather_cost':worst['gather']})
print(json.dumps({'server_games_run':0,'checks':result['checks'],'quick_costs':quick,
 'forest':[{k:v for k,v in f.items() if k!='trace'} for f in result['forest']],
 'result_sha256':info['result_sha256'],'prototype_engine':info['prototype_engine']},sort_keys=True))
PY
