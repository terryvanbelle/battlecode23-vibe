#!/usr/bin/env bash
# Own logical/source checks only. --prototype permits source-built local fixture jar, never games.
set -euo pipefail
EX_PROTOTYPE=false
if [[ ${1-} == --prototype ]];then EX_PROTOTYPE=true;shift;fi
EX_REPO=${1:?usage: explore_run.sh [--prototype] REPO FROZEN_CROWD_SOURCE NEW_OUTPUT}
EX_REPO=$(cd "$EX_REPO" && pwd)
EX_FROZEN=${2:?frozen crowd source directory required}
EX_FROZEN=$(cd "$EX_FROZEN" && pwd)
EX_OUTPUT=${3:?use a new output directory}
EX_HERE=$(cd "$(dirname "$0")" && pwd)
EX_JAR="$EX_REPO/engine/battlecode23-3.0.15.jar"
EX_ENGINE=$(sha256sum "$EX_JAR"|cut -d' ' -f1)
if [[ $EX_PROTOTYPE == false ]];then
 [[ $(hostname -s) == battlecode-dev && $EX_ENGINE == 5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a ]] || { echo 'official fixture requires battlecode-dev and pinned jar' >&2;exit 3; }
fi
[[ ! -e "$EX_OUTPUT" ]] || { echo 'use a new private output directory' >&2;exit 3; }
mkdir -p "$EX_OUTPUT/helpers" "$EX_OUTPUT/classes" "$EX_OUTPUT/host"
EX_OUTPUT=$(cd "$EX_OUTPUT" && pwd)
cp "$EX_HERE/CarrierCrowdProbe.java" "$EX_HERE/Explore1Probe.java" "$EX_HERE/BytecodeIdentity.java" "$EX_HERE/explore_source.py" "$EX_HERE/explore_run.sh" "$EX_OUTPUT/helpers/"
export JAVA_HOME=${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}
export PATH="$JAVA_HOME/bin:$PATH"
java -version 2> "$EX_OUTPUT/java-version.txt"
grep -Eq 'version "1\.8\.' "$EX_OUTPUT/java-version.txt" || { echo 'JDK8 required' >&2;exit 3; }
ex_hash(){
 local ex_root=$1 ex_pkg=$2 ex_file
 for ex_file in "$ex_root/$ex_pkg"/*.java;do
  sed -e "s/^package $ex_pkg;/package PKG;/" -e "s/^import $ex_pkg\./import PKG./" -e "s/^import static $ex_pkg\./import static PKG./" "$ex_file"
 done|sha1sum|cut -c1-12
}
[[ $(ex_hash "$EX_FROZEN" c_crowdprobe) == afea19d5f29d ]] || { echo 'officially proved scratch source hash mismatch' >&2;exit 3; }
python3 "$EX_OUTPUT/helpers/explore_source.py" "$EX_REPO" "$EX_FROZEN" "$EX_OUTPUT/source"
[[ $(ex_hash "$EX_OUTPUT/source" c_mend2) == d62033781fbd ]] || { echo 'Mend2 baseline hash mismatch' >&2;exit 3; }
find "$EX_OUTPUT/source" -name '*.java' -print|sort > "$EX_OUTPUT/source.list"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$EX_JAR" -d "$EX_OUTPUT/classes" @"$EX_OUTPUT/source.list"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$EX_JAR" -d "$EX_OUTPUT/host" "$EX_OUTPUT/helpers/CarrierCrowdProbe.java" "$EX_OUTPUT/helpers/Explore1Probe.java" "$EX_OUTPUT/helpers/BytecodeIdentity.java"
timeout --foreground -k10s 60 java -Xmx512m -cp "$EX_OUTPUT/host:$EX_JAR" BytecodeIdentity "$EX_OUTPUT/classes"|tee "$EX_OUTPUT/zero-identity.json"
nice -n5 timeout --foreground -k10s 60 java -Xmx512m -XX:+UseSerialGC -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false \
 -cp "$EX_OUTPUT/host:$EX_JAR" Explore1Probe "$EX_OUTPUT/classes" "$EX_OUTPUT/result.json"
python3 - "$EX_OUTPUT" "$EX_PROTOTYPE" "$EX_ENGINE" "$(ex_hash "$EX_OUTPUT/source" c_explore1)" "$(ex_hash "$EX_OUTPUT/source" c_explore0)" <<'PY'
import hashlib,json,sys
from pathlib import Path
out,prototype,engine,enabled,zero=sys.argv[1:];p=Path(out)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
info={'games_run':0,'mode':'own_instrumented_instructions_synthetic_controller','prototype_engine':prototype=='true',
      'engine_sha256':engine,'base_hash':'d62033781fbd','proved_crowd_patch':'afea19d5f29d','c_explore1_hash':enabled,'c_explore0_hash':zero,
      'helper_sha256':{f.name:sha(f) for f in sorted((p/'helpers').iterdir())},
      'source_sha256':{str(f.relative_to(p/'source')):sha(f) for f in sorted((p/'source').rglob('*.java'))},
      'java_version':(p/'java-version.txt').read_text().strip(),'result_sha256':sha(p/'result.json'),'zero_identity':json.loads((p/'zero-identity.json').read_text()),
      'telemetry':{'key':'cx','decode':'starts=(cx>>>20)&255; exploration_turns=(cx>>>8)&4095; first_new_site_collects=cx&255',
                   'note':'Decode per robot before aggregation; counters saturate. New-site count means first successful collect call at the site selected by this crowd episode. Missing/truncated indicators remain unknown.'},
      'limit':'No native GameWorld, full RobotPlayer run or games. RC sensing/movement/cooldowns/inventory/transfer consequences are synthetic; full own-game delivery and normal training gates remain required.'}
(p/'provenance.json').write_text(json.dumps(info,sort_keys=True,indent=2)+'\n')
print(json.dumps({'output_dir':out,'games_run':0,'prototype_engine':info['prototype_engine'],'c_explore1_hash':enabled,'c_explore0_hash':zero,
                  'checks':json.loads((p/'result.json').read_text())['checks'],'zero_methods':info['zero_identity']['methods']},sort_keys=True))
PY
