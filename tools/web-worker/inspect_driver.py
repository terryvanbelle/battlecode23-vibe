#!/usr/bin/env python3
"""First worker job: read-only driver inspection, no sync, games, secrets or process changes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess

repo = Path(os.environ['BC23_WORKER_REPO'])


def command(*args):
    result = subprocess.run(args, cwd=repo, capture_output=True, text=True, timeout=30)
    return {'exit_code': result.returncode, 'stdout': result.stdout[-12000:], 'stderr': result.stderr[-2000:]}


data = {'hostname': socket.gethostname(), 'user': command('id', '-un'), 'repo': str(repo),
        'git_status': command('git', 'status', '--short'),
        'git_log': command('git', 'log', '-5', '--format=%h %s'),
        'disk_free_bytes': shutil.disk_usage(repo).free,
        'programs': {name: shutil.which(name) for name in ('gcloud', 'ssh', 'python3', 'java', 'javac')}}
state = repo / 'progress/ladder-state.json'
if state.exists():
    data['ladder_state'] = json.loads(state.read_text())
jar = repo / 'engine/battlecode23-3.0.15.jar'
if jar.exists():
    data['engine_sha256'] = hashlib.sha256(jar.read_bytes()).hexdigest()
print(json.dumps(data, indent=2))
