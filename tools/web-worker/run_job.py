#!/usr/bin/env python3
"""Run a trusted private-control-repository job in the existing driver checkout.

This is a job transport, not a sandbox. Only the owner and intended GitHub
connection may write the private control repository. Credentials stay on the
driver; jobs must not print them or read opponent source.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time

MAX_LOG = 64 * 1024
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z')
SHA = re.compile(r'[a-f0-9]{64}\Z')
ORIGINS = {'https://github.com/terryvanbelle/battlecode23-vibe',
           'git@github.com:terryvanbelle/battlecode23-vibe',
           'ssh://git@github.com/terryvanbelle/battlecode23-vibe'}


def require_file(path, limit):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise ValueError('expected a bounded regular control file')


def validate_repo(repo):
    repo = repo.resolve()
    if not repo.is_dir() or repo.stat().st_uid != os.getuid():
        raise ValueError('the existing driver checkout is missing or owned by another account')
    try:
        top = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', '--show-toplevel'],
                                      stderr=subprocess.DEVNULL, timeout=10).decode().strip()
        origin = subprocess.check_output(['git', '-C', str(repo), 'config', '--get', 'remote.origin.url'],
                                         stderr=subprocess.DEVNULL, timeout=10).decode().strip()
    except (OSError, subprocess.SubprocessError):
        raise ValueError('unable to verify the existing driver checkout') from None
    origin = origin[:-4] if origin.endswith('.git') else origin
    if Path(top).resolve() != repo or origin not in ORIGINS:
        # Never print a remote URL: it might contain an embedded credential.
        raise ValueError('the driver checkout root or origin does not match battlecode23-vibe')
    return repo


def read_request(path):
    require_file(path, 4096)
    request = json.loads(path.read_text())
    if not isinstance(request, dict) or not isinstance(request.get('id'), str) or not ID.fullmatch(request['id']):
        raise ValueError('invalid request id')
    if not isinstance(request.get('sha256'), str) or not SHA.fullmatch(request['sha256']):
        raise ValueError('invalid job hash')
    timeout = request.get('timeout_seconds', 300)
    if type(timeout) is not int or not 1 <= timeout <= 1800:
        raise ValueError('timeout must be an integer from 1 to 1800 seconds')
    request['timeout_seconds'] = timeout
    return request


def redact(text):
    text = re.sub(r'(?i)\bBearer\s+\S+', 'Bearer [REDACTED]', text)
    text = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{12,})\b', '[REDACTED]', text)
    text = re.sub(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', '[REDACTED]', text)
    return text


def job_environment(repo, output):
    # Do not pass Actions service tokens to project jobs. Existing GCloud/SSH
    # file-based credentials are intentionally used on the original driver.
    keep = {'HOME', 'PATH', 'USER', 'LOGNAME', 'SHELL', 'TZ', 'LANG', 'JAVA_HOME',
            'GOOGLE_APPLICATION_CREDENTIALS', 'CLOUDSDK_CONFIG', 'CLOUDSDK_ACTIVE_CONFIG_NAME',
            'SSH_AUTH_SOCK', 'HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy'}
    env = {key: value for key, value in os.environ.items() if key in keep or key.startswith('LC_')}
    env['BC23_WORKER_REPO'] = str(repo)
    env['BC23_WORKER_OUTPUT'] = str(output)
    return env


class Tail:
    def __init__(self):
        self.data = bytearray()
        self.total = 0
        self.lock = threading.Lock()

    def read(self, stream):
        try:
            while True:
                chunk = stream.read(8192)
                if not chunk:
                    break
                with self.lock:
                    self.total += len(chunk)
                    self.data.extend(chunk)
                    if len(self.data) > MAX_LOG:
                        del self.data[:-MAX_LOG]
        finally:
            stream.close()

    def snapshot(self):
        with self.lock:
            return redact(self.data.decode('utf-8', errors='replace')), max(0, self.total - len(self.data))


def run(request_path, job_path, repo, output, state=None):
    request = read_request(request_path)
    require_file(job_path, 512 * 1024)
    job_hash = hashlib.sha256(job_path.read_bytes()).hexdigest()
    if job_hash != request['sha256']:
        raise ValueError('job does not match the requested hash')
    repo = validate_repo(repo)
    output = output.resolve()
    if output == repo or repo in output.parents or output in repo.parents:
        raise ValueError('worker results must be separate from the live checkout')
    if state is not None:
        state.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            with (state / (request['id'] + '.json')).open('x') as stream:
                json.dump({'id': request['id'], 'sha256': job_hash}, stream)
        except FileExistsError:
            raise ValueError('request id was already reserved; submit a new id instead of rerunning') from None
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    monotonic = time.monotonic()
    process = subprocess.Popen([sys.executable, str(job_path.resolve())], cwd=repo,
                               env=job_environment(repo, output), stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    stdout, stderr = Tail(), Tail()
    threads = [threading.Thread(target=tail.read, args=(stream,), daemon=True)
               for tail, stream in ((stdout, process.stdout), (stderr, process.stderr))]
    for thread in threads:
        thread.start()
    status = 'finished'
    try:
        process.wait(timeout=request['timeout_seconds'])
    except subprocess.TimeoutExpired:
        status = 'timeout'
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        # Kill descendants still holding output pipes after their parent exits.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    for thread in threads:
        thread.join(timeout=2)
    out, out_dropped = stdout.snapshot()
    err, err_dropped = stderr.snapshot()
    if output.is_symlink() or output.resolve() != output or not output.is_dir():
        raise ValueError('the worker results directory changed during execution')
    for name in ('stdout.txt', 'stderr.txt', 'result.json'):
        path = output / name
        if path.is_symlink() or path.exists():
            raise ValueError('the wrapper result paths already exist')
    for name, content in (('stdout.txt', out), ('stderr.txt', err)):
        with (output / name).open('x') as stream:
            stream.write(content)
    result = {'id': request['id'], 'sha256': job_hash, 'status': status,
              'exit_code': process.returncode, 'started_at': started,
              'duration_seconds': round(time.monotonic() - monotonic, 3),
              'logs_complete': all(not thread.is_alive() for thread in threads),
              'stdout_dropped_bytes': out_dropped, 'stderr_dropped_bytes': err_dropped}
    with (output / 'result.json').open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--job', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(os.environ.get('BC23_WORKER_REPO', str(Path.home() / 'projects/vibe/2023')))
    output = Path(os.environ['BC23_WORKER_OUTPUT'])
    result = run(args.request, args.job, repo, output, Path(os.environ['BC23_WORKER_STATE']))
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
            stream.write('export_ready=true\n')
    print(json.dumps(result))
    return 0 if result['status'] == 'finished' and result['exit_code'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
