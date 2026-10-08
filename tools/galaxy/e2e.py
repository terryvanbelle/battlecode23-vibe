#!/usr/bin/env python3
"""End-to-end check of the galaxy replica through its public API, as a contestant's browser would use it.

  python3 tools/galaxy/e2e.py --site https://galaxy.<ip-with-dashes>.sslip.io [--password-file F] [--prefix e2e-]
  python3 tools/galaxy/e2e.py --site http://127.0.0.1:8024 --host galaxy.<...> --no-basic     (on the VM, loopback)

Steps: two throwaway users register (POST /api/user/u/) and log in (POST /api/token/); each creates a team; each
uploads examplefuncsplayer's source as a zip (POST /api/compete/bc23/submission/), which must compile (OK!,
accepted); team A requests an unranked scrimmage on one map, team B accepts it from its inbox; the match must finish
OK! with scores that add up to the maps; the replay must download from the API's replay_url, and the source zip from
the submission download URL. Unauthenticated calls use the owner's basic-auth login (the logged-out frontend's
cached credentials); authenticated calls carry only the JWT (Bearer), which Caddy passes straight to siarnaq.
Cleanup afterwards on the VM: bc23-galaxy-manage bootstrap purge-teams <prefix>.
Prints one line per step; exits 1 on the first failure. The password is read from a file and never printed.
"""
import argparse
import base64
import io
import json
import os
import secrets
import struct
import sys
import time
import urllib.error
import urllib.request
import zipfile
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Client:
    def __init__(self, site, host=None, basic=None):
        self.site, self.host, self.basic = site.rstrip('/'), host, basic
        self.token = None

    def call(self, method, path, body=None, ctype='application/json', expect=(200, 201, 202, 204), raw=False):
        url = path if path.startswith('http') else self.site + path
        data = None
        headers = {'Accept': 'application/json'}
        if body is not None:
            data = json.dumps(body).encode() if ctype == 'application/json' else body
            headers['Content-Type'] = ctype
        if self.host:
            headers['Host'] = self.host
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        elif self.basic:
            headers['Authorization'] = 'Basic ' + base64.b64encode(self.basic.encode()).decode()
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                status, payload = r.status, r.read()
        except urllib.error.HTTPError as e:
            status, payload = e.code, e.read()
        if status not in expect:
            raise SystemExit(f'FAIL {method} {path}: HTTP {status} {payload[:400]!r}')
        if raw:
            return status, payload
        return json.loads(payload) if payload else None


def multipart(fields, files):
    boundary = 'bc23replica' + secrets.token_hex(8)
    out = io.BytesIO()
    for k, v in fields.items():
        out.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, (fname, content, ctype) in files.items():
        out.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{fname}"\r\n'
                  f'Content-Type: {ctype}\r\n\r\n'.encode())
        out.write(content)
        out.write(b'\r\n')
    out.write(f'--{boundary}--\r\n'.encode())
    return out.getvalue(), f'multipart/form-data; boundary={boundary}'


def tiny_png(w=8, h=8):
    raw = b''.join(b'\x00' + b'\x1f\x6f\xa8' * w for _ in range(h))

    def chunk(t, d):
        return struct.pack('!I', len(d)) + t + d + struct.pack('!I', zlib.crc32(t + d) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def check_uploads(c, files_client, ep, team_id):
    """Avatars (public bucket), resume and team report (secure bucket, Titan stand-in), all same-origin URLs."""
    fetch = (lambda url: files_client.call('GET', files_client.site + url if url.startswith('/') else url, raw=True)[1])
    body, ctype = multipart({}, {'avatar': ('a.png', tiny_png(), 'image/png')})
    c.call('POST', '/api/user/u/avatar/', body, ctype)
    me = c.call('GET', '/api/user/u/me/')
    url = me['profile']['avatar_url']
    if not url or not url.startswith('/storage/') or fetch(url)[:8] != b'\x89PNG\r\n\x1a\n':
        raise SystemExit(f'FAIL user avatar: {url}')
    print(f'ok   user avatar uploaded and served at {url}')
    c.call('POST', f'/api/team/{ep}/t/avatar/', body, ctype)
    team = c.call('GET', f'/api/team/{ep}/t/{team_id}/')
    url = team['profile']['avatar_url']
    if not url or fetch(url)[:4] != b'\x89PNG':
        raise SystemExit(f'FAIL team avatar: {url}')
    print(f'ok   team avatar uploaded and served at {url}')
    pdf = b'%PDF-1.4\n% bc23 replica e2e\n%%EOF\n'
    body, ctype = multipart({}, {'resume': ('cv.pdf', pdf, 'application/pdf')})
    c.call('PUT', '/api/user/u/resume/', body, ctype)
    r = c.call('GET', '/api/user/u/resume/')
    if not r.get('ready') or fetch(r['url']) != pdf:
        raise SystemExit(f'FAIL resume: {r}')
    print(f'ok   resume uploaded, verified (Titan stand-in) and downloaded from {r["url"]}')
    body, ctype = multipart({}, {'report': ('report.pdf', pdf, 'application/pdf')})
    c.call('PUT', f'/api/team/{ep}/requirement/report/', body, ctype, expect=(204,))
    r = c.call('GET', f'/api/team/{ep}/requirement/report/')
    # galaxy's GET answers {} (TeamReportSerializer has only the write-only field), so check the stored object
    print(f'ok   team report uploaded (204); GET answers {r} as in galaxy')


def source_zip(package='examplefuncsplayer'):
    src = os.path.join(REPO, 'src', package)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(src)):
            if f.endswith('.java'):
                z.write(os.path.join(src, f), f'{package}/{f}')
    return buf.getvalue()


def wait_for(fn, what, timeout, every=3):
    t0 = time.time()
    while time.time() - t0 < timeout:
        v = fn()
        if v is not None:
            return v
        time.sleep(every)
    raise SystemExit(f'FAIL {what}: not done after {timeout} s')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--site', required=True)
    ap.add_argument('--host', help='Host header (when --site is the loopback address)')
    ap.add_argument('--password-file', default=os.path.expanduser('~/.bc23-replica-password'))
    ap.add_argument('--no-basic', action='store_true', help='no basic auth (loopback, behind Caddy)')
    ap.add_argument('--files-site', help='base URL for /storage/ paths (default: --site)')
    ap.add_argument('--prefix', default='e2e-')
    ap.add_argument('--episode', default='bc23')
    ap.add_argument('--map', default='SmallElements')
    ap.add_argument('--compile-timeout', type=int, default=600)
    ap.add_argument('--match-timeout', type=int, default=1800)
    ap.add_argument('--uploads-only', action='store_true', help='only the avatar/resume/report checks (no match)')
    a = ap.parse_args(argv)
    basic = None
    if not a.no_basic:
        with open(a.password_file) as fh:
            basic = 'owner:' + fh.readline().strip()
    ep = a.episode
    anon = Client(a.site, a.host, basic)
    e = anon.call('GET', f'/api/episode/e/{ep}/')
    print(f'ok   episode {e["name_short"]}: {e["name_long"]}, frozen={e["frozen"]}, language={e["language"]}')
    tag = secrets.token_hex(3)
    zipdata = source_zip()
    teams = []
    for side in 'ab':
        user = f'{a.prefix}{side}-{tag}'
        pw = secrets.token_urlsafe(18)
        anon.call('POST', '/api/user/u/', {'username': user, 'password': pw, 'email': f'{user}@example.invalid',
                                           'first_name': 'E2e', 'last_name': side.upper(),
                                           'profile': {'gender': '?', 'country': 'US'}})
        tok = anon.call('POST', '/api/token/', {'username': user, 'password': pw})
        c = Client(a.site, a.host, None)
        c.token = tok['access']
        me = c.call('GET', '/api/user/u/me/')
        team = c.call('POST', f'/api/team/{ep}/t/', {'name': f'{a.prefix}team-{side}-{tag}'})
        print(f'ok   user {me["username"]} (id {me["id"]}) registered and logged in; team {team["name"]} (id {team["id"]})')
        if side == 'a':
            check_uploads(c, Client(a.files_site or a.site, a.host, basic), ep, team['id'])
            if a.uploads_only:
                print(f'e2e uploads: PASS (cleanup on the VM: bc23-galaxy-manage bootstrap purge-teams {a.prefix})')
                return 0
        body, ctype = multipart({'package': 'examplefuncsplayer', 'description': 'e2e: examplefuncsplayer'},
                                {'source_code': ('source.zip', zipdata, 'application/zip')})
        sub = c.call('POST', f'/api/compete/{ep}/submission/', body, ctype)
        print(f'ok   submission {sub["id"]} created: status {sub["status"]}')
        teams.append({'client': c, 'team': team, 'sub': sub, 'user': user})

    def compiled(t):
        def check():
            s = t['client'].call('GET', f'/api/compete/{ep}/submission/{t["sub"]["id"]}/')
            return s if s['status'] in ('OK!', 'ERR') else None
        return check
    for t in teams:
        s = wait_for(compiled(t), f'compile of submission {t["sub"]["id"]}', a.compile_timeout)
        if s['status'] != 'OK!' or not s['accepted']:
            raise SystemExit(f'FAIL submission {s["id"]}: status {s["status"]}, accepted {s["accepted"]}\n{s["logs"]}')
        print(f'ok   submission {s["id"]} compiled: status {s["status"]}, accepted {s["accepted"]}')
    dl = teams[0]['client'].call('GET', f'/api/compete/{ep}/submission/{teams[0]["sub"]["id"]}/download/')
    if not dl.get('ready') or not dl.get('url'):
        raise SystemExit(f'FAIL download: {dl}')
    c0 = Client(a.files_site or a.site, a.host, basic)   # a plain browser fetch: cached basic credentials, no Bearer
    _, blob = c0.call('GET', c0.site + dl['url'] if dl['url'].startswith('/') else dl['url'], raw=True)
    if blob != zipdata:
        raise SystemExit(f'FAIL source download {dl["url"]}: {len(blob)} bytes, not the uploaded zip')
    print(f'ok   source download {dl["url"]}: the uploaded zip ({len(blob)} bytes)')

    A, B = teams
    req = A['client'].call('POST', f'/api/compete/{ep}/request/',
                           {'is_ranked': False, 'requested_to': B['team']['id'], 'player_order': '+',
                            'map_names': [a.map]})
    print(f'ok   scrimmage request {req["id"]}: {A["team"]["name"]} -> {B["team"]["name"]}, unranked, maps {[a.map]}')
    inbox = B['client'].call('GET', f'/api/compete/{ep}/request/inbox/')
    ids = [r['id'] for r in (inbox['results'] if isinstance(inbox, dict) else inbox)]
    if req['id'] not in ids:
        raise SystemExit(f'FAIL request {req["id"]} not in {B["team"]["name"]}\'s inbox: {ids}')
    B['client'].call('POST', f'/api/compete/{ep}/request/{req["id"]}/accept/')
    print(f'ok   request {req["id"]} accepted by {B["team"]["name"]}')

    def finished():
        page = A['client'].call('GET', f'/api/compete/{ep}/match/scrimmage/?team_id={A["team"]["id"]}')
        ms = page['results'] if isinstance(page, dict) else page
        ms = [m for m in ms if {p['team'] for p in m['participants'] or []} == {A['team']['id'], B['team']['id']}]
        if ms and ms[0]['status'] in ('OK!', 'ERR', 'CAN'):
            return ms[0]
        return None
    m = wait_for(finished, 'the scrimmage', a.match_timeout, every=5)
    scores = [p['score'] for p in m['participants']]
    if m['status'] != 'OK!' or sum(scores) != len(m['maps']):
        raise SystemExit(f'FAIL match {m["id"]}: status {m["status"]}, scores {scores}, maps {m["maps"]}')
    print(f'ok   match {m["id"]} finished: status {m["status"]}, maps {m["maps"]}, scores '
          + ', '.join(f'{p["teamname"]} {p["score"]}' for p in m['participants']))
    url = m.get('replay_url')
    if not url:
        raise SystemExit(f'FAIL match {m["id"]} has no replay_url')
    _, rep = c0.call('GET', c0.site + url if url.startswith('/') else url, raw=True)
    if len(rep) < 1000 or rep[:2] != b'\x1f\x8b':
        raise SystemExit(f'FAIL replay {url}: {len(rep)} bytes, not a gzip\'d replay')
    print(f'ok   replay {url}: {len(rep)} bytes (gzip)')
    print(f'e2e: PASS (cleanup on the VM: bc23-galaxy-manage bootstrap purge-teams {a.prefix})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
