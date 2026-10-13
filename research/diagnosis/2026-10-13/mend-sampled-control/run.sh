#!/usr/bin/env bash
# Prepare or inspect existing replays. This packet script never launches a game.
set -euo pipefail
umask 077
PACKET_MODE=${1:?usage: run.sh --prepare REPO NEWOUT | --inspect REPO NEWOUT OFF ON SAMPLED_GAME_DIR}
shift
[[ $PACKET_MODE == --prepare || $PACKET_MODE == --inspect ]] || { echo 'use --prepare or --inspect' >&2; exit 3; }
PACKET_PROTOTYPE=false
if [[ ${1-} == --prototype ]]; then PACKET_PROTOTYPE=true; shift; fi
PACKET_REPO=${1:?supply repo};PACKET_OUTPUT=${2:?supply fresh output directory}
PACKET_HERE=$(cd "$(dirname "$0")" && pwd)
PACKET_JAR="$PACKET_REPO/engine/battlecode23-3.0.15.jar"
PACKET_RELEASE=5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a
PACKET_ACTUAL=$(sha256sum "$PACKET_JAR" | cut -d' ' -f1)
if [[ $PACKET_PROTOTYPE == true ]]; then
  [[ $PACKET_MODE == --prepare ]] || { echo 'prototype mode permits zero-game fixtures only' >&2; exit 3; }
else
  [[ $PACKET_ACTUAL == "$PACKET_RELEASE" ]] || { echo 'official jar pin mismatch' >&2; exit 3; }
fi
[[ ! -e $PACKET_OUTPUT ]] || { echo 'use a fresh private output directory' >&2; exit 3; }
export JAVA_HOME=${JAVA_HOME:-$HOME/jdk/jdk8u504-b01}
export PATH="$JAVA_HOME/bin:$PATH"
mkdir -p "$PACKET_OUTPUT/host" "$PACKET_OUTPUT/calibration" "$PACKET_OUTPUT/helpers"
PACKET_OUTPUT=$(cd "$PACKET_OUTPUT" && pwd)
cp "$PACKET_HERE/helpers/"* "$PACKET_OUTPUT/helpers/"
java -version 2> "$PACKET_OUTPUT/java-version.txt"
grep -Eq 'version "1\.8\.' "$PACKET_OUTPUT/java-version.txt" || { echo 'JDK8 required' >&2; exit 3; }
timeout --kill-after=5s 90s javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -cp "$PACKET_JAR" -d "$PACKET_OUTPUT/host" \
  "$PACKET_OUTPUT/helpers/SampledProfileHost.java" "$PACKET_OUTPUT/helpers/SamplingCacheTest.java" \
  "$PACKET_OUTPUT/helpers/OwnLauncherSelector.java" "$PACKET_OUTPUT/helpers/NativeProfile.java" "$PACKET_OUTPUT/helpers/ReplayDump.java"
timeout --kill-after=5s 30s javac -nowarn -encoding UTF-8 -source 8 -target 8 -proc:none -d "$PACKET_OUTPUT/calibration" "$PACKET_OUTPUT/helpers/SamplingCalibration.java"
for packet_class in SampledProfileHost NativeProfile OwnLauncherSelector; do
  timeout --kill-after=5s 30s java -Xmx512m -cp "$PACKET_OUTPUT/host:$PACKET_JAR" "$packet_class" --selftest > "$PACKET_OUTPUT/$packet_class-selftest.json"
done
timeout --kill-after=5s 30s java -Xmx512m -Dbc.engine.debug-methods=false -cp "$PACKET_OUTPUT/host:$PACKET_JAR" SamplingCacheTest "$PACKET_OUTPUT/calibration" > "$PACKET_OUTPUT/cache-selftest.json"
(cd "$PACKET_OUTPUT/helpers" && timeout --kill-after=5s 30s python3 -m unittest test_sampled test_scope) > "$PACKET_OUTPUT/gate-selftest.log" 2>&1
python3 - "$PACKET_OUTPUT" "$PACKET_ACTUAL" "$PACKET_PROTOTYPE" <<'PY'
import hashlib,json,sys
from pathlib import Path
output,engine,prototype=sys.argv[1:];root=Path(output)
value={'prepare_only':True,'prototype_only':prototype=='true','engine_sha256':engine,'games_run':0,
       'java_version':(root/'java-version.txt').read_text().strip(),
       'helper_sha256':{path.name:hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in sorted((root/'helpers').iterdir()) if path.is_file()}}
(root/'preparation.json').write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
print(json.dumps(value,sort_keys=True))
PY
if [[ $PACKET_MODE == --prepare ]]; then exit 0; fi
PACKET_OFF=${3:?supply preserved off replay};PACKET_ON=${4:?supply sampled on replay};PACKET_GAME=${5:?supply sampled-game directory with sampling.json}
[[ $(sha256sum "$PACKET_OFF" | cut -d' ' -f1) == 6544c8b768bd53579dc06473de148e464edd5262c663e7968e9586b630ec436b ]] || { echo 'preserved off pin mismatch' >&2; exit 3; }
[[ $(sha256sum "$PACKET_ON" | cut -d' ' -f1) == 71863f3f3e7069ee7a377d5c5faa670992e3738411ebb93186000adb3f06af78 ]] || { echo 'sampled on pin mismatch' >&2; exit 3; }
mkdir "$PACKET_OUTPUT/pair"
cp "$PACKET_OFF" "$PACKET_OUTPUT/pair/off.bc23"
cp "$PACKET_ON" "$PACKET_OUTPUT/pair/on.bc23"
for packet_mode in off on; do
  for packet_flag in fingerprint games; do
    timeout --kill-after=5s 120s java -Xmx2048m -cp "$PACKET_OUTPUT/host:$PACKET_JAR" replaydump.ReplayDump "$PACKET_OUTPUT/pair/$packet_mode.bc23" "--$packet_flag" > "$PACKET_OUTPUT/pair/$packet_mode.$packet_flag"
  done
done
python3 "$PACKET_OUTPUT/helpers/summarize.py" --compare "$PACKET_OUTPUT/pair"
python3 - "$PACKET_OUTPUT/pair/identity.json" <<'PY'
import json,sys
value=json.load(open(sys.argv[1]))
if any(value.get(key) is not True for key in ('fingerprint_identity','footer_result_identity','terminal_metadata_valid')):
    raise SystemExit('complete state/bytecode/footer identity required')
PY
timeout --kill-after=5s 180s java -Xmx2048m -cp "$PACKET_OUTPUT/host:$PACKET_JAR" NativeProfile "$PACKET_OUTPUT/pair/on.bc23" "$PACKET_OUTPUT/pair/native"
python3 "$PACKET_OUTPUT/helpers/validate_sampled.py" "$PACKET_GAME" "$PACKET_OUTPUT/pair" "$PACKET_OUTPUT/pair/native" > "$PACKET_OUTPUT/pair/sample-coverage.json"
timeout --kill-after=5s 180s java -Xmx2048m -cp "$PACKET_OUTPUT/host:$PACKET_JAR" replaydump.ReplayDump "$PACKET_OUTPUT/pair/on.bc23" --extract "$PACKET_OUTPUT/pair/telemetry" --match 0 --tele-turns > "$PACKET_OUTPUT/pair/telemetry.log"
timeout --kill-after=5s 60s python3 "$PACKET_OUTPUT/helpers/summarize.py" --extract "$PACKET_OUTPUT/pair/native" --telemetry "$PACKET_OUTPUT/pair/telemetry" > "$PACKET_OUTPUT/pair/summary.log"
python3 "$PACKET_OUTPUT/helpers/validate_scope.py" "$PACKET_OUTPUT/pair/native"
