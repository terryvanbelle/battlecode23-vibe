#!/usr/bin/env python3
"""Prepare private dose sources and provenance; no games, credentials, networking or tracked edits."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

root = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
if out.exists():
    raise SystemExit('use a fresh output directory')
out.mkdir(mode=0o700)
original = Path(os.environ.get('BLIND_BASE_SOURCE', str(root / 'baseline-src' / 'c_mend2')))
assert original.is_absolute() and original.resolve(strict=True) == original
expected_base = json.loads((root / 'base-provenance.json').read_text(encoding='utf-8'))['base_files']
def verify_base(path):
    assert {p.name for p in path.iterdir()} == set(expected_base)
    for name, digest in expected_base.items():
        p = path / name
        assert p.is_file() and not p.is_symlink()
        assert hashlib.sha256(p.read_bytes()).hexdigest() == digest
verify_base(original)
snapshot = out / 'baseline-source' / 'c_mend2'
shutil.copytree(original, snapshot)
verify_base(snapshot)
def code_hash(path, package, exclude=()):
    text = ''.join(p.read_text().replace('package ' + package + ';', 'package PKG;')
                   .replace('import ' + package + '.', 'import PKG.')
                   .replace('import static ' + package + '.', 'import static PKG.')
                   for p in sorted(path.glob('*.java')) if p.name not in exclude)
    return hashlib.sha1(text.encode()).hexdigest()[:12]
assert code_hash(snapshot, 'c_mend2') == 'd62033781fbd'
info = {'base_hash': 'd62033781fbd', 'doses': [], 'guards': {'entry': 4000, 'scan': 3500, 'stats': 2000}, 'games_run': 0}
expected_doses = {0: '43138ce60516', 1: '9ce6956c844b', 2: '6b6275c740cb', 4: '625c5733784a'}
for period in (0, 1, 2, 4):
    target = out / ('period-' + str(period)) / 'source' / 'c_blind1'
    shutil.copytree(snapshot, target)
    for p in target.glob('*.java'):
        body = p.read_text(encoding='utf-8').replace('package c_mend2;', 'package c_blind1;')
        body = body.replace('import c_mend2.', 'import c_blind1.').replace('import static c_mend2.', 'import static c_blind1.')
        p.write_text(body, encoding='utf-8')
    # The only candidate inputs are these two owned overlays; all other code comes from the frozen base.
    for name in ('C.java', 'Launcher.java'):
        shutil.copy2(root / 'src' / 'c_blind1' / name, target / name)
    constants = target / 'C.java'
    body, count = re.subn(r'BLIND_PERIOD = 1;', 'BLIND_PERIOD = ' + str(period) + ';', constants.read_text())
    assert count == 1
    constants.write_text(body)
    shutil.copy2(root / 'BlindCalibration.java', target / 'BlindCalibration.java')
    assert code_hash(target, 'c_blind1', ('BlindCalibration.java',)) == expected_doses[period]
    info['doses'].append({'period': period, 'hash_with_test_wrapper': code_hash(target, 'c_blind1'),
                          'production_hash': code_hash(target, 'c_blind1', ('BlindCalibration.java',))})
verify_base(original)
(out / 'source-provenance.json').write_text(json.dumps(info, indent=2) + '\n')
print(json.dumps(info))
