#!/usr/bin/env python3
"""Prepare the reviewed full-loop worker, never connect or start fixtures."""
import base64
import gzip
import hashlib
import io
import json
import difflib
from pathlib import Path
import py_compile
import tarfile

ROOT = Path('/workspace/work/blind-full-turn')
PINS = {
    'ControlledBlindGame.java': 'f6bccf4cb91c5fc6543b70a9993dce7ac81ba489898c0605df5d53a8bbea4787',
    'run.sh': '37dae563b54be7e2bf877c360065fc7dfdc2a4162044b54ffb8093b4ed5ec2bf',
    'summarize.py': '79829fee2ddb282ccdb574e828ec7b769915a055c1887e88de61723e6cb93dcd',
    'test_summary.py': 'e47f9097f929bc6062e78296bdef283b7334d1e21ba5b874017366e58092e9b5',
    'README.md': 'b67c0f6b25ade560698facfa3b580dc607cdaeaca948acec9ca997524949d719',
    'prepare.py': '2e5fbfe7c922c321eb5d33f209ff7e01454ed788eca13e1ba2abe7f05ac406bc',
    'base-provenance.json': 'd1f0f1e7b311f6282f0ceb6196854256cbbff0ec26402f0a028c08f7427f4791',
    'BlindCalibration.java': '457d20e99c1cb397594554a86f1c00daad538786589588b30df0b88da2aad632',
    'src/c_blind1/C.java': '7d187dc930b6d0d60891fb2abcfaa908e01f2be071fbbde5e235fffe91776141',
    'src/c_blind1/Launcher.java': 'abf696af24d63bbe32c421bcf50fbd24b28a96653a1f0ae2fcdaa9f4274f0b2e',
}


def build():
    frozen, files = {}, {}
    for name, wanted in PINS.items():
        path = ROOT / name
        data = path.read_bytes()
        if path.is_symlink() or not path.is_file() or hashlib.sha256(data).hexdigest() != wanted:
            raise RuntimeError('reviewed full-loop helper changed: ' + name)
        frozen[name] = data
        files[name] = {'sha256': wanted, 'mode': 0o700 if name == 'run.sh' else 0o600}
    # Ship only exact edit operations for the two overlays; verify reconstructed complete source SHA on the VM.
    base_pins = json.loads(frozen['base-provenance.json'])['base_files']
    overlays = {}
    base_source = Path('/workspace/work/blind-arm/baseline-src/c_mend2')
    for name in ('C.java', 'Launcher.java'):
        before = (base_source / name).read_bytes()
        if hashlib.sha256(before).hexdigest() != base_pins[name]:
            raise RuntimeError('frozen own base changed while deriving overlays')
        text = before.decode().replace('package c_mend2;', 'package c_blind1;')
        text = text.replace('import c_mend2.', 'import c_blind1.').replace('import static c_mend2.', 'import static c_blind1.')
        old = text.splitlines(True)
        new = frozen['src/c_blind1/' + name].decode().splitlines(True)
        operations = [{'start': i, 'end': j, 'removed': old[i:j], 'added': new[k:l]}
                      for tag, i, j, k, l in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes() if tag != 'equal']
        overlays[name] = {'sha256': PINS['src/c_blind1/' + name], 'operations': operations}
        del frozen['src/c_blind1/' + name]
        del files['src/c_blind1/' + name]
    frozen['overlays.json'] = (json.dumps(overlays, sort_keys=True, separators=(',', ':')) + '\n').encode()
    files['overlays.json'] = {'sha256': hashlib.sha256(frozen['overlays.json']).hexdigest(), 'mode': 0o600}
    manifest = {
        'scope': 'five controlled full-owned-launcher RobotPlayer fixtures, no natural scored games',
        'helper_files': dict(files),
        'base_hash': 'd62033781fbd', 'base_files_sha256': base_pins,
        'complete_overlay_sha256': {name: item['sha256'] for name, item in overlays.items()},
        'dose_hashes': {'0': '43138ce60516', '4': '625c5733784a', '2': '6b6275c740cb', '1': '9ce6956c844b'},
        'official_engine_sha256': '5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a',
        'fixture_order': ['base', '0', '4', '2', '1'], 'rounds_per_fixture_max': 32,
        'zero_gate_before_active_arms': True, 'vm_seconds_max': 175, 'worker_seconds_max': 300,
        'prototype_classes_jars_or_results_transferred': False,
    }
    frozen['source-manifest.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    files['source-manifest.json'] = {'sha256': hashlib.sha256(frozen['source-manifest.json']).hexdigest(), 'mode': 0o600}
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w') as archive:
        for name in sorted(frozen):
            member = tarfile.TarInfo(name)
            member.size, member.mode, member.mtime = len(frozen[name]), files[name]['mode'], 0
            archive.addfile(member, io.BytesIO(frozen[name]))
    raw = gzip.compress(buffer.getvalue(), compresslevel=9, mtime=0)
    if len(raw) >= 59000:
        raise RuntimeError('full-loop helper archive exceeds bound')
    (ROOT / 'helpers-v1.tar.gz').write_bytes(raw)
    (ROOT / 'source-manifest.json').write_bytes(frozen['source-manifest.json'])
    payload = {'data': base64.b64encode(raw).decode(), 'sha256': hashlib.sha256(raw).hexdigest(),
               'files': files, 'base_pins': manifest['base_files_sha256'], 'dose_hashes': manifest['dose_hashes'],
               'overlay_sha256': manifest['complete_overlay_sha256']}
    source = 'import base64,datetime,hashlib,io,json,os,pathlib,shlex,subprocess,tarfile,time,uuid,zlib\npayload=' + repr(payload) + '\n' + r'''
repo=pathlib.Path(os.environ['BC23_WORKER_REPO'])
if str(repo)!='/home/terryvanbelle/projects/vibe/2023' or repo.resolve()!=repo:raise RuntimeError('unexpected authoritative driver')
started=time.monotonic();deadline=started+300
ENGINE='5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a'
def run(args,timeout=35,allow_failure=False):
    remaining=deadline-time.monotonic()
    if remaining<=0:raise RuntimeError('full-loop worker deadline exhausted')
    p=subprocess.run(args,cwd=repo,capture_output=True,text=True,timeout=min(timeout,remaining))
    if p.returncode and not allow_failure:raise RuntimeError('owned full-loop command failed: '+p.stderr[-1200:]+' '+p.stdout[-600:])
    return p if allow_failure else p.stdout
def ssh(command,timeout=35,allow_failure=False):
    return run(['gcloud','compute','ssh','battlecode-dev','--zone=us-west1-b','--project=tvanbelle-vibecode','--internal-ip','--strict-host-key-checking=yes','--ssh-flag=-oBatchMode=yes','--command='+command],timeout,allow_failure)
def remote_python(code,args=(),timeout=35):
    return ssh('python3 -c '+shlex.quote(code)+''.join(' '+shlex.quote(str(a)) for a in args),timeout)
scp=['gcloud','compute','scp','--zone=us-west1-b','--project=tvanbelle-vibecode','--internal-ip','--strict-host-key-checking=yes','--scp-flag=-oBatchMode=yes']
def verify_driver():
    base=repo/'src/c_mend2'
    if base.resolve()!=base or {p.name for p in base.iterdir()}!=set(payload['base_pins']):raise RuntimeError('driver own base layout changed')
    for name,wanted in payload['base_pins'].items():
        p=base/name
        if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=wanted:raise RuntimeError('driver own frozen base changed')
    for name in ('C.java','Launcher.java'):
        p=repo/'src/c_blind1'/name
        if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=payload['overlay_sha256'][name]:raise RuntimeError('published own blind overlay changed')
verify_driver();head_start=run(['git','rev-parse','HEAD']).strip()
raw=base64.b64decode(payload['data'],validate=True)
if hashlib.sha256(raw).hexdigest()!=payload['sha256']:raise RuntimeError('helper archive checksum changed')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
relative='build/codex-recovery/blind-full-turn-'+stamp
local=repo/relative;local.mkdir(mode=0o700)
(local/'helpers.tar.gz').write_bytes(raw)
vmroot='/home/terryvanbelle/projects/vibe/2023/'+relative
remote_python("import pathlib,socket,sys;assert socket.gethostname().split('.')[0]=='battlecode-dev';pathlib.Path(sys.argv[1]).mkdir(mode=0o700)",(vmroot,))
run(scp+[str(local/'helpers.tar.gz'),'battlecode-dev:'+vmroot+'/helpers.tar.gz'])
extract=r"""
import hashlib,io,json,pathlib,shutil,socket,sys,tarfile
root=pathlib.Path(sys.argv[1]);files=json.loads(sys.argv[2]);pins=json.loads(sys.argv[4])
if socket.gethostname().split('.')[0]!='battlecode-dev' or root.resolve()!=root:raise RuntimeError('wrong VM or private root')
raw=(root/'helpers.tar.gz').read_bytes()
if hashlib.sha256(raw).hexdigest()!=sys.argv[3]:raise RuntimeError('VM archive checksum mismatch')
helpers=root/'helpers';helpers.mkdir(mode=0o700)
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
    members=archive.getmembers()
    if len(members)!=len(files) or {m.name for m in members}!=set(files):raise RuntimeError('unexpected frozen archive member')
    for m in members:
        name=pathlib.PurePosixPath(m.name);expected=files[m.name]
        if not m.isfile() or name.is_absolute() or any(p in ('.','..') for p in name.parts) or str(name)!=m.name:raise RuntimeError('known relative regular inputs only')
        data=archive.extractfile(m).read()
        if m.mode!=expected['mode'] or hashlib.sha256(data).hexdigest()!=expected['sha256']:raise RuntimeError('helper content/mode mismatch')
        p=helpers/m.name;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700);p.write_bytes(data);p.chmod(m.mode)
base=pathlib.Path('/home/terryvanbelle/projects/vibe/2023/src/c_mend2')
def verify(p):
    if p.resolve()!=p or {q.name for q in p.iterdir()}!=set(pins):raise RuntimeError('VM own base layout changed')
    for name,wanted in pins.items():
        q=p/name
        if not q.is_file() or q.is_symlink() or hashlib.sha256(q.read_bytes()).hexdigest()!=wanted:raise RuntimeError('VM own base content mismatch')
verify(base);snapshot=helpers/'baseline-src/c_mend2';shutil.copytree(base,snapshot);verify(snapshot);verify(base)
overlays=json.loads((helpers/'overlays.json').read_text())
if set(overlays)!={'C.java','Launcher.java'}:raise RuntimeError('unexpected own overlay inputs')
target=helpers/'src/c_blind1';target.mkdir(parents=True,mode=0o700)
for name,item in overlays.items():
    text=(snapshot/name).read_text().replace('package c_mend2;','package c_blind1;')
    text=text.replace('import c_mend2.','import c_blind1.').replace('import static c_mend2.','import static c_blind1.')
    lines=text.splitlines(True);result=[];at=0
    for edit in item['operations']:
        start,end=edit['start'],edit['end']
        if not at<=start<=end<=len(lines) or lines[start:end]!=edit['removed']:raise RuntimeError('exact frozen overlay context mismatch')
        result+=lines[at:start]+edit['added'];at=end
    data=''.join(result+lines[at:]).encode()
    if hashlib.sha256(data).hexdigest()!=item['sha256']:raise RuntimeError('complete reconstructed overlay SHA mismatch')
    (target/name).write_bytes(data);(target/name).chmod(0o600)
engine=hashlib.sha256(pathlib.Path('/home/terryvanbelle/projects/vibe/2023/engine/battlecode23-3.0.15.jar').read_bytes()).hexdigest()
if engine!=sys.argv[5]:raise RuntimeError('prototype engine excluded')
print(json.dumps({'files_verified':len(files),'base_files_verified':len(pins),'engine_sha256':engine}))
"""
verified=json.loads(remote_python(extract,(vmroot,json.dumps(payload['files']),payload['sha256'],json.dumps(payload['base_pins']),ENGINE),45))
command='cd '+shlex.quote(str(repo))+' && nice -n5 bash '+shlex.quote(vmroot+'/helpers/run.sh')+' '+shlex.quote(str(repo))+' '+shlex.quote(vmroot+'/output')
execution=ssh(command,195,allow_failure=True)
pack=r"""
import hashlib,json,pathlib,sys,tarfile
root=pathlib.Path(sys.argv[1]);out=root/'output';entries={}
names=['result.json','zero-gate.json','source-provenance.json','jdk.txt','parser-tests.txt']
for arm in ('base','0','4','2','1'):
    names += [arm+'.stdout.log',arm+'.stderr.log']
    names += [arm+'/'+leaf for leaf in ('result.json','geometry.json','raw.jsonl','player.log','native.bc23')]
total=0
with tarfile.open(root/'raw-artifacts.tar.gz','w:gz') as archive:
    for name in names:
        p=out/name
        if not p.exists():continue
        if not p.is_file() or p.is_symlink():raise RuntimeError('unexpected raw output type')
        data=p.read_bytes();total+=len(data)
        if total>20000000:raise RuntimeError('bounded raw archive exceeded')
        entries[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
        archive.add(p,arcname=name,recursive=False)
engine=hashlib.sha256(pathlib.Path('/home/terryvanbelle/projects/vibe/2023/engine/battlecode23-3.0.15.jar').read_bytes()).hexdigest()
if engine!=sys.argv[2]:raise RuntimeError('engine changed during fixture')
archive=root/'raw-artifacts.tar.gz'
manifest={'files':entries,'raw_bytes':total,'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'engine_sha256':engine}
(root/'artifact-manifest.json').write_text(json.dumps(manifest,sort_keys=True)+'\n')
print(json.dumps(manifest,sort_keys=True))
"""
artifact_manifest=json.loads(remote_python(pack,(vmroot,ENGINE),45))
run(scp+['battlecode-dev:'+vmroot+'/raw-artifacts.tar.gz',str(local)])
archive=local/'raw-artifacts.tar.gz'
if hashlib.sha256(archive.read_bytes()).hexdigest()!=artifact_manifest['archive_sha256']:raise RuntimeError('returned raw archive checksum mismatch')
observations=local/'observations';observations.mkdir(mode=0o700)
with tarfile.open(archive,'r:gz') as raw_archive:
    members=raw_archive.getmembers()
    if len(members)!=len(artifact_manifest['files']) or {m.name for m in members}!=set(artifact_manifest['files']):raise RuntimeError('raw archive entries mismatch')
    for m in members:
        name=pathlib.PurePosixPath(m.name)
        if not m.isfile() or name.is_absolute() or any(p in ('.','..') for p in name.parts) or str(name)!=m.name:raise RuntimeError('regular private observation files required')
        data=raw_archive.extractfile(m).read();wanted=artifact_manifest['files'][m.name]
        if len(data)!=wanted['bytes'] or hashlib.sha256(data).hexdigest()!=wanted['sha256']:raise RuntimeError('returned raw file checksum mismatch')
        p=observations/m.name;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700);p.write_bytes(data);p.chmod(0o600)
verify_driver();head_end=run(['git','rev-parse','HEAD']).strip()
summary=json.loads((observations/'result.json').read_text()) if (observations/'result.json').exists() else None
zero=json.loads((observations/'zero-gate.json').read_text()) if (observations/'zero-gate.json').exists() else None
source_provenance=json.loads((observations/'source-provenance.json').read_text()) if (observations/'source-provenance.json').exists() else None
if source_provenance and (source_provenance['base_hash']!='d62033781fbd' or {str(d['period']):d['production_hash'] for d in source_provenance['doses']}!=payload['dose_hashes']):raise RuntimeError('frozen private source changed')
compact_turns={}
for arm in ('base','0','4','2','1'):
    p=observations/arm/'result.json'
    if p.exists():
        data=json.loads(p.read_text());compact_turns[arm]={'pass':data['pass'],'rounds':data['rounds'],'failure':data['failure'],'failure_cause':data['failure_cause'],
            'turns':[{key:turn[key] for key in ('round','start_cd','end_cd','whole_turn_bytecodes','counters','indicator','attacks','memory')}
                     | ({'next_actual_own_start_cd':turn['next_actual_own_start_cd']} if 'next_actual_own_start_cd' in turn else {}) for turn in data['turns']]}
provenance={'scope':'controlled full-owned-launcher native RobotPlayer diagnostics','prototype_only':False,'official_engine_sha256':verified['engine_sha256'],
    'helper_archive_sha256':payload['sha256'],'helper_files':payload['files'],'base_files_sha256':payload['base_pins'],'dose_hashes':payload['dose_hashes'],
    'driver_head_start':head_start,'driver_head_end':head_end,'head_pinned_or_mutated':False,'vm_host':'battlecode-dev','vm_deadline_seconds':175,'worker_deadline_seconds':300,
    'actual_scheduler_clock_and_cold_initialization':True,'host_observation_bodies_metered':False,'manual_clock_cooldown_or_owned_memory_writes':False,
    'controlled_fixtures_max':5,'native_rounds_per_fixture_max':32,'natural_scored_games':0,'field_submissions':0,'source_deployment':False,'elapsed_seconds':round(time.monotonic()-started,3)}
artifact={'provenance':provenance,'summary':summary,'zero_gate':zero,'source_provenance':source_provenance,'compact_turns':compact_turns,'raw_artifact_manifest':artifact_manifest,
    'execution_returncode':execution.returncode,'execution_stdout_tail':execution.stdout[-1500:],'execution_stderr_tail':execution.stderr[-1500:]}
raw=(json.dumps(artifact,sort_keys=True,separators=(',',':'))+'\n').encode();encoded=base64.b64encode(zlib.compress(raw,9)).decode()
(local/'artifact.json').write_bytes(raw)
(local/'artifact-manifest.json').write_text(json.dumps(artifact_manifest,sort_keys=True,indent=2)+'\n')
state='controlled_full_loop_passed' if execution.returncode==0 and summary and summary.get('pass') else 'controlled_full_loop_failed'
quick_summary=None if summary is None else {key:value for key,value in summary.items() if key!='arms'}
if quick_summary is not None:quick_summary['arms']=[{key:value for key,value in arm.items() if key!='map_field_progress'} for arm in summary['arms']]
response={'state':state,'driver_artifacts':str(local),'vm_artifacts':vmroot+'/output','summary':quick_summary,'zero_gate':zero,
    'artifact_sha256':hashlib.sha256(raw).hexdigest(),'artifact_zlib_b64':encoded,'raw_archive_sha256':artifact_manifest['archive_sha256'],'natural_scored_games':0,'promotion_claimed':False}
if len(json.dumps(response).encode())>=59000:raise RuntimeError('bounded full-loop response exceeded')
print(json.dumps(response,sort_keys=True))
'''
    # dict union is supported on the canonical Python 3.9 driver.
    output = Path('/workspace/work/remote-jobs/run_blind_full_turn.py')
    output.write_text(source)
    py_compile.compile(str(output), doraise=True)
    if output.stat().st_size >= 59000:
        raise RuntimeError('bounded control worker source exceeded')
    record = {'worker': str(output), 'worker_bytes': output.stat().st_size, 'worker_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'helper_archive_bytes': len(raw), 'helper_archive_sha256': payload['sha256'], 'files': files,
              'workflow_timeout_seconds': 300, 'vm_timeout_seconds': 175, 'prepared_only': True, 'fixtures_launched': 0}
    (ROOT / 'transfer-preparation.json').write_text(json.dumps(record, sort_keys=True, indent=2) + '\n')
    print(json.dumps(record, sort_keys=True))


if __name__ == '__main__':
    build()
