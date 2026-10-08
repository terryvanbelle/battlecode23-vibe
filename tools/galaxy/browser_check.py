#!/usr/bin/env python3
"""Headless-Chromium walk through the galaxy site, by its real host name, as a contestant uses it.

  python3 tools/galaxy/browser_check.py --site https://galaxy.<ip-with-dashes>.sslip.io --out DIR
          [--chromium /usr/bin/chromium] [--password-file ~/.bc23-replica-password] [--prefix e2e-]

Run on battlecode-dev as the operator, with a Chromium installed for the check (docs/galaxy/README.md). The browser
resolves the site to 127.0.0.1 (Caddy, real certificate) and every other host to a dead proxy, so it can reach
nothing else; each URL it requests is recorded. The basic-auth login is given the way a person gives it: Chromium
gets Caddy's 401 challenge and the check answers it (CDP Fetch.authRequired), so the browser's own auth cache decides
what later requests carry. The password is read from the file and never printed or put on a command line.

Steps: two throwaway contestants are created through the API (team B also uploads a bot); then in the browser:
logged-out pages (home, rankings, queue, resources); log in as A through the login form; upload
examplefuncsplayer on the Submissions page; request an unranked scrimmage with B on the Scrimmaging page; log out,
log in as B, accept it from the inbox; once it has run, press Replay! and play the replay in the viewer. Writes
screenshots and report.json to DIR and prints a summary: every host contacted, which requests carried Basic,
Bearer or no Authorization, failed requests, console errors and CSP violations. Clean up afterwards:
bc23-galaxy-manage bootstrap purge-teams <prefix>.
"""
import argparse
import base64
import json
import os
import secrets
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e2e  # noqa: E402


# ---------------------------------------------------------------- a minimal websocket client (RFC 6455) for CDP
class WebSocket:
    def __init__(self, url, timeout=60):
        u = urllib.parse.urlsplit(url)
        self.sock = socket.create_connection((u.hostname, u.port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\n'
                           f'Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n')
                          .encode())
        head = b''
        while b'\r\n\r\n' not in head:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError('websocket handshake failed')
            head += chunk
        if b' 101 ' not in head.split(b'\r\n')[0]:
            raise ConnectionError(head[:200])
        self.buf = head.split(b'\r\n\r\n', 1)[1]
        self.sock.settimeout(None)      # the reader blocks between events (a match can take minutes)
        self.lock = threading.Lock()

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(1 << 16)
            if not chunk:
                raise ConnectionError('websocket closed')
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, text):
        data = text.encode()
        head = bytearray([0x81])
        n = len(data)
        if n < 126:
            head.append(0x80 | n)
        elif n < 65536:
            head.append(0x80 | 126)
            head += struct.pack('!H', n)
        else:
            head.append(0x80 | 127)
            head += struct.pack('!Q', n)
        mask = os.urandom(4)
        with self.lock:
            self.sock.sendall(bytes(head) + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def recv(self):
        parts = []
        while True:
            b0, b1 = self._read(2)
            n = b1 & 0x7f
            if n == 126:
                n = struct.unpack('!H', self._read(2))[0]
            elif n == 127:
                n = struct.unpack('!Q', self._read(8))[0]
            payload = self._read(n)
            op = b0 & 0x0f
            if op == 9:                       # ping
                continue
            if op == 8:
                raise ConnectionError('websocket closed by peer')
            parts.append(payload)
            if b0 & 0x80:
                return b''.join(parts).decode('utf-8', 'replace')


class CDP:
    """One page session: commands with replies, events dispatched to handlers on a reader thread."""

    def __init__(self, ws_url):
        self.ws = WebSocket(ws_url)
        self.next_id, self.pending, self.handlers = 0, {}, {}
        self.cv = threading.Condition()
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        while True:
            try:
                msg = json.loads(self.ws.recv())
            except Exception:
                return
            if 'id' in msg:
                with self.cv:
                    self.pending[msg['id']] = msg
                    self.cv.notify_all()
            else:
                for fn, inline in self.handlers.get(msg.get('method'), []):
                    if inline:      # bookkeeping: keeps the order of events
                        fn(msg.get('params') or {})
                    else:           # handlers that send commands must not block the reader
                        threading.Thread(target=fn, args=(msg.get('params') or {},), daemon=True).start()

    def on(self, method, fn, inline=False):
        self.handlers.setdefault(method, []).append((fn, inline))

    def call(self, method, timeout=60, **params):
        with self.cv:
            self.next_id += 1
            i = self.next_id
        self.ws.send(json.dumps({'id': i, 'method': method, 'params': params}))
        with self.cv:
            if not self.cv.wait_for(lambda: i in self.pending, timeout):
                raise TimeoutError(method)
            msg = self.pending.pop(i)
        if 'error' in msg:
            raise RuntimeError(f'{method}: {msg["error"]}')
        return msg.get('result') or {}


# ---------------------------------------------------------------- the walk
class Walk:
    def __init__(self, cdp, site, basic, out):
        self.cdp, self.site, self.basic, self.out = cdp, site.rstrip('/'), basic, out
        self.origin = self.site
        self.host = urllib.parse.urlsplit(site).hostname
        self.requests, self.failed, self.console, self.blocked, self.auth_answers = {}, [], [], [], 0
        self.rechallenges = []
        self.inflight, self.lock = set(), threading.Lock()
        self.shots = []
        c = cdp
        c.on('Fetch.authRequired', self._auth)
        c.on('Fetch.requestPaused', self._paused)
        c.on('Network.requestWillBeSent', self._sent, inline=True)
        c.on('Network.requestWillBeSentExtraInfo', self._extra, inline=True)
        c.on('Network.responseReceivedExtraInfo', self._resp_extra, inline=True)
        c.on('Network.responseReceived', self._resp, inline=True)
        c.on('Network.loadingFinished', lambda p: self._done(p['requestId']), inline=True)
        c.on('Network.loadingFailed', self._failed, inline=True)
        c.on('Runtime.consoleAPICalled', lambda p: self.console.append(
            (p.get('type'), ' '.join(str(a.get('value', a.get('description', ''))) for a in p.get('args', []))[:300])),
            inline=True)
        c.on('Runtime.exceptionThrown', lambda p: self.console.append(
            ('exception', json.dumps(p.get('exceptionDetails', {}))[:300])), inline=True)
        c.on('Log.entryAdded', lambda p: self.console.append(
            ('log:' + p['entry'].get('source', '') + ':' + p['entry'].get('level', ''),
             (p['entry'].get('text', '') + ' ' + p['entry'].get('url', ''))[:300])), inline=True)
        for d in ('Network', 'Page', 'Runtime', 'Log', 'DOM'):
            c.call(f'{d}.enable')
        c.call('Fetch.enable', handleAuthRequests=True, patterns=[{'urlPattern': '*'}])
        c.call('Emulation.setDeviceMetricsOverride', width=1400, height=1000, deviceScaleFactor=1, mobile=False)

    # -- events
    def _auth(self, p):
        ch = p.get('authChallenge') or {}
        ok = ch.get('source') == 'Server' and ch.get('scheme', '').lower() == 'basic' and \
            urllib.parse.urlsplit(ch.get('origin', '')).hostname == self.host
        with self.lock:
            first = ok and self.auth_answers == 0
            if first:
                self.auth_answers += 1
            elif ok:
                self.rechallenges.append(p['request']['url'][:200])
        if first:
            user, pw = self.basic.split(':', 1)
            resp = {'response': 'ProvideCredentials', 'username': user, 'password': pw}
        else:   # a person would see a password prompt here: count it and cancel (the request fails with 401)
            resp = {'response': 'CancelAuth'}
        self.cdp.call('Fetch.continueWithAuth', requestId=p['requestId'], authChallengeResponse=resp)

    def _paused(self, p):
        url = p['request']['url']
        u = urllib.parse.urlsplit(url)
        if u.scheme in ('data', 'blob') or (u.scheme == 'https' and u.hostname == self.host):
            self.cdp.call('Fetch.continueRequest', requestId=p['requestId'])
        else:
            self.blocked.append(url[:200])
            self.cdp.call('Fetch.failRequest', requestId=p['requestId'], errorReason='BlockedByClient')

    def _sent(self, p):
        with self.lock:
            self.inflight.add(p['requestId'])
            self.requests.setdefault(p['requestId'], {}).update(url=p['request']['url'], method=p['request']['method'],
                                                                type=p.get('type'))

    def _extra(self, p):
        h = {k.lower(): v for k, v in (p.get('headers') or {}).items()}
        a = h.get('authorization', '')
        kind = 'Bearer' if a.startswith('Bearer ') else 'Basic' if a.startswith('Basic ') else 'none'
        with self.lock:
            self.requests.setdefault(p['requestId'], {}).setdefault('attempts', []).append(kind)

    def _resp_extra(self, p):
        with self.lock:
            self.requests.setdefault(p['requestId'], {}).setdefault('statuses', []).append(p.get('statusCode'))

    def _resp(self, p):
        with self.lock:
            self.requests.setdefault(p['requestId'], {})['status'] = p['response'].get('status')

    def _done(self, rid):
        with self.lock:
            self.inflight.discard(rid)

    def _failed(self, p):
        r = self.requests.get(p['requestId'], {})
        self.failed.append((r.get('url', '?')[:200], p.get('errorText'), p.get('blockedReason')))
        self._done(p['requestId'])

    # -- helpers
    def settle(self, quiet=1.5, timeout=45):
        t0, last = time.time(), time.time()
        while time.time() - t0 < timeout:
            with self.lock:
                busy = bool(self.inflight)
            if busy:
                last = time.time()
            elif time.time() - last > quiet:
                return
            time.sleep(0.2)

    def go(self, path):
        self.cdp.call('Page.navigate', url=path if path.startswith('http') else self.origin + path)
        time.sleep(0.5)
        self.settle()

    def js(self, expr, await_promise=False):
        r = self.cdp.call('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=await_promise)
        if 'exceptionDetails' in r:
            raise RuntimeError(f'js: {r["exceptionDetails"].get("text")} {expr[:80]}')
        return (r.get('result') or {}).get('value')

    def wait_js(self, expr, what, timeout=60):
        t0 = time.time()
        while time.time() - t0 < timeout:
            v = self.js(expr)
            if v:
                return v
            time.sleep(0.5)
        raise SystemExit(f'FAIL browser: {what} (waited {timeout} s)')

    def shot(self, name):
        data = self.cdp.call('Page.captureScreenshot', format='png')['data']
        path = os.path.join(self.out, f'{len(self.shots) + 1:02d}-{name}.png')
        with open(path, 'wb') as fh:
            fh.write(base64.b64decode(data))
        self.shots.append(path)

    def fill(self, name, value, selector=None):
        sel = selector or f'input[name={json.dumps(name)}]'
        ok = self.js(f"""(() => {{ const el = [...document.querySelectorAll({json.dumps(sel)})]
                                      .find(e => e.getClientRects().length > 0);
            if (!el) return false;
            const set = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el), 'value').set;
            set.call(el, {json.dumps(value)});
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
            el.dispatchEvent(new Event('change', {{bubbles: true}}));
            return true; }})()""")
        if not ok:
            raise SystemExit(f'FAIL browser: no input named {name} on {self.js("location.pathname")}')

    def click(self, text, within=None):
        """Click the visible, enabled button labelled `text`; with `within`, the one whose nearest ancestor that
        mentions `within` is smallest (the table row of that team)."""
        ok = self.js(f"""(() => {{
            const bs = [...document.querySelectorAll('button')].filter(b => b.textContent.trim() === {json.dumps(text)}
                && !b.disabled && b.getClientRects().length > 0);
            const want = {json.dumps(within)};
            let best = null, bestLen = Infinity;
            for (const b of bs) {{
                if (want === null) {{ best = b; break; }}
                let e = b;
                while (e && !e.textContent.includes(want)) e = e.parentElement;
                if (e && e.textContent.length < bestLen) {{ best = b; bestLen = e.textContent.length; }}
            }}
            if (!best) return false;
            best.click(); return true; }})()""")
        if not ok:
            raise SystemExit(f'FAIL browser: no enabled button "{text}"' + (f' in the row of {within}' if within else '')
                             + f' on {self.js("location.pathname")}')
        time.sleep(0.5)
        self.settle()

    def login(self, user, pw):
        self.go('/login')
        self.wait_js("!!document.querySelector('input[name=username]')", 'login form')
        self.fill('username', user)
        self.fill('password', pw)
        self.click('Log in')
        self.wait_js("!location.pathname.startsWith('/login')", 'leave the login page after logging in')
        self.settle()


def find_free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--site', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--chromium', default=shutil.which('chromium') or '/usr/bin/chromium')
    ap.add_argument('--password-file', default=os.path.expanduser('~/.bc23-replica-password'))
    ap.add_argument('--prefix', default='e2e-')
    ap.add_argument('--episode', default='bc23')
    ap.add_argument('--match-timeout', type=int, default=1800)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    with open(a.password_file) as fh:
        basic = 'owner:' + fh.readline().strip()
    site, ep = a.site.rstrip('/'), a.episode
    host = urllib.parse.urlsplit(site).hostname
    # on the VM, reach the site through Caddy on loopback (certificate and Host checked as usual)
    real_getaddrinfo = socket.getaddrinfo
    socket.getaddrinfo = lambda h, *rest, **kw: real_getaddrinfo('127.0.0.1' if h == host else h, *rest, **kw)

    # ---- two throwaway contestants through the API (as e2e.py); B uploads a bot now, A will upload in the browser
    anon = e2e.Client(site, None, basic)
    tag = secrets.token_hex(3)
    people = {}
    for side in 'ab':
        user, pw = f'{a.prefix}{side}-{tag}', secrets.token_urlsafe(18)
        anon.call('POST', '/api/user/u/', {'username': user, 'password': pw, 'email': f'{user}@example.invalid',
                                           'first_name': 'Browser', 'last_name': side.upper(),
                                           'profile': {'gender': '?', 'country': 'US'}})
        c = e2e.Client(site, None, None)
        c.token = anon.call('POST', '/api/token/', {'username': user, 'password': pw})['access']
        team = c.call('POST', f'/api/team/{ep}/t/', {'name': f'{a.prefix}team-{side}-{tag}'})
        people[side] = {'user': user, 'pw': pw, 'client': c, 'team': team}
        print(f'ok   contestant {user}, team {team["name"]} (id {team["id"]})')
    zipdata = e2e.source_zip()
    body, ctype = e2e.multipart({'package': 'examplefuncsplayer', 'description': 'browser check: B'},
                                {'source_code': ('source.zip', zipdata, 'application/zip')})
    people['b']['client'].call('POST', f'/api/compete/{ep}/submission/', body, ctype)
    zpath = os.path.join(a.out, 'examplefuncsplayer.zip')
    with open(zpath, 'wb') as fh:
        fh.write(zipdata)

    # ---- the browser
    port = find_free_port()
    profile = tempfile.mkdtemp(prefix='bc23-chromium-')
    cmd = [a.chromium, '--headless=new', f'--remote-debugging-port={port}', '--remote-debugging-address=127.0.0.1',
           f'--user-data-dir={profile}', '--no-first-run', '--no-default-browser-check', '--disable-sync',
           '--disable-background-networking', '--disable-component-update', '--disable-default-apps',
           '--disable-features=Translate,OptimizationHints,MediaRouter', '--password-store=basic',
           '--proxy-server=http://127.0.0.1:9', f'--proxy-bypass-list={host}',
           f'--host-resolver-rules=MAP {host} 127.0.0.1, MAP * ~NOTFOUND', 'about:blank']
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report = {'site': site, 'steps': []}
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list', timeout=2) as r:
                    pages = [t for t in json.load(r) if t.get('type') == 'page']
                if pages:
                    break
            except OSError:
                pass
            time.sleep(0.2)
        w = Walk(CDP(pages[0]['webSocketDebuggerUrl']), site, basic, a.out)

        def step(msg):
            print('ok  ', msg)
            report['steps'].append(msg)

        # logged out
        w.go('/')
        w.wait_js("document.querySelectorAll('nav, aside, header').length > 0 || document.body.innerText.length > 50",
                  'the frontend renders')
        w.shot('home-logged-out')
        step(f'logged-out home: {w.js("location.pathname")}, title {w.js("document.title")!r}')
        for path in (f'/{ep}/rankings', f'/{ep}/queue', f'/{ep}/resources'):
            w.go(path)
            time.sleep(1)
            w.shot(path.strip('/').replace('/', '-'))
        step('logged-out rankings, queue, resources rendered')

        # A logs in, uploads, requests
        A, B = people['a'], people['b']
        w.login(A['user'], A['pw'])
        w.shot('logged-in-a')
        step(f'logged in as {A["user"]} through the login form -> {w.js("location.pathname")}')
        w.go(f'/{ep}/submissions')
        w.wait_js("!!document.querySelector('input[type=file]')", 'the submission form')
        doc = w.cdp.call('DOM.getDocument', depth=1)
        node = w.cdp.call('DOM.querySelector', nodeId=doc['root']['nodeId'], selector='input[type=file]')['nodeId']
        w.cdp.call('DOM.setFileInputFiles', files=[zpath], nodeId=node)
        w.fill('packageName', 'examplefuncsplayer')
        w.fill('description', 'browser check: A')
        w.click('Submit')
        w.shot('submitted')

        def latest(c):
            page = c.call('GET', f'/api/compete/{ep}/submission/')
            subs = page['results'] if isinstance(page, dict) else page
            return subs[0] if subs else None
        s = e2e.wait_for(lambda: (lambda x: x if x and x['status'] in ('OK!', 'ERR') else None)(latest(A['client'])),
                         'compile of the browser upload', 600)
        if s['status'] != 'OK!' or not s['accepted'] or s['description'] != 'browser check: A':
            raise SystemExit(f'FAIL browser upload: {s["status"]} accepted={s["accepted"]} {s["description"]!r}')
        sb = e2e.wait_for(lambda: (lambda x: x if x and x['status'] in ('OK!', 'ERR') else None)(latest(B['client'])),
                          'compile of B', 600)
        if not sb['accepted']:
            raise SystemExit('FAIL compile of B')
        w.go(f'/{ep}/submissions')
        time.sleep(1)
        w.shot('submissions-compiled')
        step(f'uploaded examplefuncsplayer on the Submissions page: submission {s["id"]} {s["status"]}, accepted')
        w.go(f'/{ep}/scrimmaging')
        w.wait_js("[...document.querySelectorAll('button')].some(b => b.textContent.trim() === 'Find Teams')",
                  'the Find Teams tab')
        w.click('Find Teams')
        w.wait_js("!!document.querySelector('input[placeholder^=\"Search for a team\"]')", 'the team search box')
        w.fill(None, B['team']['name'], selector='input[placeholder^="Search for a team"]')
        w.click('Search!')
        w.wait_js(f"document.body.innerText.includes({json.dumps(B['team']['name'])})", 'team B in the teams table')
        w.click('Request', within=B['team']['name'])
        w.wait_js("[...document.querySelectorAll('button')].some(b => b.textContent.trim() === 'Request Scrimmage')",
                  'the request modal')
        w.shot('request-modal')
        w.click('Request Scrimmage')
        out = A['client'].call('GET', f'/api/compete/{ep}/request/outbox/')
        reqs = out['results'] if isinstance(out, dict) else out
        if not reqs:
            raise SystemExit('FAIL browser: no scrimmage request in A\'s outbox')
        step(f'requested a scrimmage with {B["team"]["name"]} in the modal: request {reqs[0]["id"]}, '
             f'maps {reqs[0]["maps"]}, ranked={reqs[0]["is_ranked"]}')

        # B accepts
        w.click('Open user menu')
        w.wait_js("[...document.querySelectorAll('button')].some(b => b.textContent.trim() === 'Sign out')",
                  'the Sign out item')
        w.click('Sign out')
        w.wait_js("document.body.innerText.includes('Log in')", 'the logged-out header')
        step(f'signed out {A["user"]} from the user menu')
        w.login(B['user'], B['pw'])
        w.go(f'/{ep}/scrimmaging')
        w.wait_js("[...document.querySelectorAll('button')].some(b => b.textContent.trim() === 'Accept')",
                  'the request in B\'s inbox')
        w.shot('inbox-b')
        w.click('Accept')
        step(f'logged in as {B["user"]} and accepted the request from the inbox')

        def finished():
            page = B['client'].call('GET', f'/api/compete/{ep}/match/scrimmage/?team_id={B["team"]["id"]}')
            ms = page['results'] if isinstance(page, dict) else page
            return ms[0] if ms and ms[0]['status'] in ('OK!', 'ERR', 'CAN') else None
        m = e2e.wait_for(finished, 'the scrimmage', a.match_timeout, every=5)
        if m['status'] != 'OK!':
            raise SystemExit(f'FAIL match {m["id"]}: {m["status"]}')
        step(f'match {m["id"]} ran: ' + ', '.join(f'{p["teamname"]} {p["score"]}' for p in m['participants'])
             + f' on {m["maps"]}')
        w.go(f'/{ep}/scrimmaging')
        w.wait_js("[...document.querySelectorAll('button')].some(b => b.textContent.trim() === 'Scrim History')",
                  'the Scrim History tab')
        w.click('Scrim History')
        w.wait_js("[...document.querySelectorAll('button')].some(b => b.textContent.trim() === 'Replay!' && !b.disabled)",
                  'an enabled Replay! button', 60)
        w.shot('history-b')
        w.js("window.__opened = null; window.open = (u) => { window.__opened = u; return null; };")
        w.click('Replay!')
        url = w.wait_js('window.__opened', 'Replay! to open the viewer')
        step(f'Replay! opens {url}')
        n0 = len(w.console)
        w.go(url)
        w.wait_js("document.querySelectorAll('canvas').length > 0", 'the viewer canvas', 60)
        t0 = time.time()
        while time.time() - t0 < 60 and not any('Running a game' in t or 'un-gzipped' in t
                                                for _, t in w.console[n0:]):
            time.sleep(0.5)
        time.sleep(3)
        w.shot('viewer')
        viewer_log = [t for _, t in w.console[n0:]]
        step('viewer console: ' + ' | '.join(viewer_log[:8]))
        report['viewer_console'] = viewer_log
    except SystemExit:
        try:
            w.shot('failure')
            with open(os.path.join(a.out, 'failure.txt'), 'w') as fh:
                fh.write(w.js('location.href') + '\n' + (w.js('document.body.innerText') or '')[:5000])
        except Exception:
            pass
        raise
    finally:
        proc.terminate()
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)

    # ---- summary
    reqs = list(w.requests.values())
    hosts = sorted({urllib.parse.urlsplit(r.get('url', '')).hostname or urllib.parse.urlsplit(r.get('url', '')).scheme
                    for r in reqs})
    by_auth = {}
    for r in reqs:
        u = urllib.parse.urlsplit(r.get('url', ''))
        if u.scheme != 'https':
            continue
        cls = '/api/' if u.path.startswith('/api/') else '/' + u.path.split('/')[1] + '/' \
            if u.path.count('/') > 1 else 'top-level'
        key = f'{cls} {"->".join(r.get("attempts") or ["(cache)"])} {r.get("status")}'
        by_auth[key] = by_auth.get(key, 0) + 1
    csp = [t for k, t in w.console if 'Content Security Policy' in t or 'Refused to' in t]
    errors = [(k, t) for k, t in w.console if k in ('error', 'exception') or k.endswith(':error')]
    report.update(hosts=hosts, auth_by_class=by_auth, blocked=w.blocked, failed=w.failed, csp_violations=csp,
                  console_errors=errors, basic_auth_challenges_answered=w.auth_answers,
                  later_challenges=w.rechallenges, screenshots=w.shots,
                  requests=reqs)
    with open(os.path.join(a.out, 'report.json'), 'w') as fh:
        json.dump(report, fh, indent=1)
    print('hosts contacted:', hosts)
    print('requests by path class and Authorization:', json.dumps(by_auth, sort_keys=True))
    print('basic-auth challenges answered (the one password entry):', w.auth_answers)
    print('later challenges (a person would get a password prompt):', w.rechallenges or 'none')
    print('blocked (other hosts):', w.blocked or 'none')
    print('failed requests:', w.failed or 'none')
    print('CSP violations:', csp or 'none')
    print('console errors:', errors[:10] or 'none')
    ok = hosts and set(hosts) <= {host, 'data', 'blob'} and not w.blocked and not csp and not w.rechallenges
    print('browser: PASS' if ok else 'browser: CHECK the report')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
