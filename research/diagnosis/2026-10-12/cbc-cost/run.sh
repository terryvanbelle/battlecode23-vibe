#!/usr/bin/env bash
# Run on battlecode-dev with the official release. --prototype explicitly permits a local source-built fixture jar.
set -euo pipefail
CBC_PROTOTYPE=false
if [[ ${1-} == --prototype ]]; then CBC_PROTOTYPE=true; shift; fi
CBC_REPO=${1:?usage: run.sh [--prototype] <battlecode23-vibe repo> [private output directory]}
CBC_REPO=$(cd "$CBC_REPO" && pwd)
CBC_HERE=$(cd "$(dirname "$0")" && pwd)
CBC_OUTPUT=${2:-$(mktemp -d /tmp/bc23-cbc-cost.XXXXXX)}
mkdir -p "$CBC_OUTPUT"
CBC_OUTPUT=$(cd "$CBC_OUTPUT" && pwd)
CBC_JAR="$CBC_REPO/engine/battlecode23-3.0.15.jar"
CBC_RELEASE_SHA=5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a
CBC_JAR_SHA=$(sha256sum "$CBC_JAR" | cut -d' ' -f1)
if [[ $CBC_PROTOTYPE == false ]]; then
  [[ $(hostname -s) == battlecode-dev ]] || { echo 'release cost probe must run on battlecode-dev' >&2; exit 3; }
  [[ $CBC_JAR_SHA == "$CBC_RELEASE_SHA" ]] || { echo 'official release checksum mismatch' >&2; exit 3; }
fi
export JAVA_HOME=${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}
export PATH="$JAVA_HOME/bin:$PATH"
java -version 2> "$CBC_OUTPUT/java-version.txt"
grep -Eq 'version "1\.8\.' "$CBC_OUTPUT/java-version.txt" || { echo 'JDK8 required' >&2; exit 3; }
cbc_hash() {
  local cbc_root=$1 cbc_package=$2 cbc_file
  for cbc_file in "$cbc_root/$cbc_package"/*.java; do
    sed -e "s/^package $cbc_package;/package PKG;/" -e "s/^import $cbc_package\./import PKG./" -e "s/^import static $cbc_package\./import static PKG./" "$cbc_file"
  done | sha1sum | cut -c1-12
}
[[ ! -e "$CBC_OUTPUT/source" && ! -e "$CBC_OUTPUT/bots" && ! -e "$CBC_OUTPUT/host" ]] || { echo 'use a fresh private output directory' >&2; exit 3; }
mkdir -p "$CBC_OUTPUT/source" "$CBC_OUTPUT/bots" "$CBC_OUTPUT/host"
cp -a "$CBC_REPO/src/c_mend2" "$CBC_REPO/src/c_bc3" "$CBC_OUTPUT/source/"
CBC_CANDIDATE_HASH=$(cbc_hash "$CBC_OUTPUT/source" c_bc3)
CBC_MEND_HASH=$(cbc_hash "$CBC_OUTPUT/source" c_mend2)
[[ $CBC_CANDIDATE_HASH == ed3aceb26a90 && $CBC_MEND_HASH == d62033781fbd ]] || { echo 'frozen source hash mismatch' >&2; exit 3; }
find "$CBC_OUTPUT/source" -type f -name '*.java' -print | sort > "$CBC_OUTPUT/sources.list"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$CBC_JAR" -d "$CBC_OUTPUT/bots" @"$CBC_OUTPUT/sources.list"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$CBC_JAR" -d "$CBC_OUTPUT/host" "$CBC_HERE/CbcCostProbe.java"
javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$CBC_JAR" -d "$CBC_OUTPUT/bots" "$CBC_HERE/ApiCalibration.java"
python3 - "$CBC_OUTPUT" "$CBC_PROTOTYPE" "$CBC_JAR_SHA" "$CBC_CANDIDATE_HASH" "$CBC_MEND_HASH" "$CBC_HERE/CbcCostProbe.java" "$CBC_HERE/ApiCalibration.java" <<'PY'
import hashlib,json,sys
from pathlib import Path
out,prototype,engine,candidate,mend,probe,calibration=sys.argv[1:]
p=Path(out)
info={'prototype_only':prototype=='true','engine_sha256':engine,'c_bc3_hash':candidate,'c_mend2_hash':mend,
      'probe_sha256':hashlib.sha256(Path(probe).read_bytes()).hexdigest(),'calibration_sha256':hashlib.sha256(Path(calibration).read_bytes()).hexdigest(),
      'java_version':(p/'java-version.txt').read_text().strip(),
      'method':'computePredWells','games_run':0,'output_dir':out,
      'note':'Synthetic fixed inputs. cached/changed warm at10000; cached_unbounded warms at1000000 and may be unreachable. Cost includes instrumented own instructions/array accounting and API callsite charges; host setup/proxy body excluded. Pending debt asserted zero.'}
(p/'provenance.json').write_text(json.dumps(info,sort_keys=True)+'\n')
print(json.dumps({'provenance':info},sort_keys=True))
PY
timeout 90 java -Xmx512m -XX:+UseSerialGC -Dbc.engine.debug-methods=false -Dbc.engine.enable-profiler=false \
  -cp "$CBC_OUTPUT/host:$CBC_JAR" CbcCostProbe "$CBC_OUTPUT/bots" "$CBC_OUTPUT/result.json"
