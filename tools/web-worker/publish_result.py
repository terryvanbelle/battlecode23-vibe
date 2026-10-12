#!/usr/bin/env python3
"""Publish bounded non-secret results to the PRIVATE control repo, never the bot repo."""
import argparse
import base64
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

from run_job import ID, MAX_LOG, read_request, redact, require_file

CONTROL_REPO = 'terryvanbelle/battlecode23-control'
RESULT_FIELDS = ('id', 'sha256', 'status', 'exit_code', 'started_at', 'duration_seconds',
                 'logs_complete', 'stdout_dropped_bytes', 'stderr_dropped_bytes')


def make_response(request_path, output, export_ready=True):
    request = read_request(request_path)
    if export_ready and (output / 'result.json').exists():
        require_file(output / 'result.json', 32 * 1024)
        result = json.loads((output / 'result.json').read_text())
        if not isinstance(result, dict):
            raise ValueError('invalid worker result')
        if result.get('id') != request['id'] or result.get('sha256') != request['sha256']:
            raise ValueError('result provenance does not match this request')
        result = {key: result[key] for key in RESULT_FIELDS if key in result}
    else:
        result = {'id': request['id'], 'sha256': request['sha256'], 'status': 'setup_failed', 'exit_code': None}
    for name in ('stdout', 'stderr'):
        path = output / (name + '.txt')
        if export_ready and path.exists():
            if path.is_symlink() or not path.is_file():
                raise ValueError('refusing a symlink or special file in worker results')
            with path.open('rb') as stream:
                stream.seek(max(0, path.stat().st_size - MAX_LOG))
                result[name] = redact(stream.read(MAX_LOG).decode('utf-8', errors='replace'))
        else:
            result[name] = ''
    result['workflow_run_id'] = os.environ.get('GITHUB_RUN_ID')
    result['workflow_run_attempt'] = os.environ.get('GITHUB_RUN_ATTEMPT')
    result['control_commit'] = os.environ.get('GITHUB_SHA')
    artifact = os.environ.get('BC23_WORKER_ARTIFACT_ID', '')
    result['artifact_id'] = artifact if artifact.isdigit() else None
    return result


def publish(response):
    if not isinstance(response.get('id'), str) or not ID.fullmatch(response['id']):
        raise ValueError('invalid response id')
    if os.environ.get('GITHUB_REPOSITORY') != CONTROL_REPO or os.environ.get('GITHUB_REF') != 'refs/heads/main':
        raise ValueError('refusing publication outside the private control repository main branch')
    if os.environ.get('GITHUB_API_URL', 'https://api.github.com') != 'https://api.github.com':
        raise ValueError('unexpected GitHub API endpoint')
    token = os.environ['GH_TOKEN']
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json'}
    repo_url = 'https://api.github.com/repos/' + CONTROL_REPO
    try:
        with urllib.request.urlopen(urllib.request.Request(repo_url, headers=headers), timeout=60) as stream:
            repository = json.load(stream)
    except urllib.error.HTTPError as error:
        raise RuntimeError('repository privacy check failed: HTTP ' + str(error.code)) from None
    if repository.get('private') is not True or repository.get('full_name') != CONTROL_REPO:
        raise ValueError('refusing publication to a repository that is not the expected private control repository')
    url = 'https://api.github.com/repos/' + CONTROL_REPO + '/contents/responses/' + response['id'] + '.json'
    body = {'message': 'Record worker result ' + response['id'], 'branch': 'main',
            'content': base64.b64encode((json.dumps(response, indent=2) + '\n').encode()).decode()}
    # IDs are single-use. Preserve the first response even if someone reruns an
    # Actions workflow; a retry must have a new request ID.
    try:
        with urllib.request.urlopen(urllib.request.Request(url + '?ref=main', headers=headers), timeout=60) as stream:
            json.load(stream)
            return
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise RuntimeError('response lookup failed: HTTP ' + str(error.code)) from None
    request = urllib.request.Request(url, json.dumps(body).encode(), headers, method='PUT')
    try:
        with urllib.request.urlopen(request, timeout=60) as stream:
            json.load(stream)
    except urllib.error.HTTPError as error:
        raise RuntimeError('response publication failed: HTTP ' + str(error.code)) from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    args = parser.parse_args()
    response = make_response(args.request, Path(os.environ['BC23_WORKER_OUTPUT']),
                             os.environ.get('BC23_WORKER_EXPORT_READY') == 'true')
    publish(response)
    print('Published response for ' + response['id'])


if __name__ == '__main__':
    main()
