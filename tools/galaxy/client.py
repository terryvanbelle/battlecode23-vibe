#!/usr/bin/env python3
"""A small HTTP client for the galaxy replica's public API (siarnaq), shared by the field tools
(tools/galaxy/field.py), the results download (tools/galaxy/results.py) and the ladder snapshot
(tools/galaxy/snapshot.py). Standard library only.

Every request goes to the replica site, the way the website's own calls do:
- without a JWT (logged out: sign-up, login, the Rankings page, replay files) a request carries the site's basic-auth
  gate (user owner, password in ~/.bc23-replica-password), as the browser does once the owner has typed it;
- with a JWT a request carries only `Authorization: Bearer <token>`, which the gate passes straight to siarnaq.

It refuses any URL that is not on the replica site and any site under the official contest domain (OFFICIAL; owner,
PROMPTS 12: nothing may touch the real contest website). `connect` sends the TCP connection to another address (e.g. 127.0.0.1 on the
VM) while keeping the site's host name for TLS (SNI and certificate check) and the Host header, like
`curl --resolve`; the request still goes through the site's Caddy front, exactly as from outside.
"""
import base64
import http.client
import io
import json
import os
import socket
import ssl
import time
import urllib.parse
import uuid

SITE = (os.environ.get('GALAXY_SITE') or os.environ.get('CONTEST_SITE')
        or 'https://galaxy.136-86-167-127.sslip.io').rstrip('/')
EPISODE = os.environ.get('CONTEST_EPISODE', 'bc23')
GATE_USER = 'owner'
GATE_FILE = os.path.expanduser('~/.bc23-replica-password')
OFFICIAL = 'battlecode' + '.org'      # the official contest's domain, built so that no file here names the host


class ApiError(Exception):
    def __init__(self, code, detail):
        super().__init__(f'HTTP {code}: {detail[:300]}')
        self.code, self.detail = code, detail

    def code_name(self):
        """siarnaq's error code (e.g. 'scrimmages_rate_limited'), when the body says so."""
        try:
            body = json.loads(self.detail)
        except ValueError:
            return ''
        if isinstance(body, dict):
            return str(body.get('code') or '')
        return ''


def check_site(site):
    p = urllib.parse.urlparse(site)
    host = (p.hostname or '').lower()
    if p.scheme != 'https' or not host:
        raise SystemExit(f'refusing site {site!r}: an https URL of our replica is required')
    if host == OFFICIAL or host.endswith('.' + OFFICIAL):
        raise SystemExit(f'refusing site {site!r}: these tools talk only to our replica, never to {OFFICIAL}')
    return p


def multipart(fields, files):
    """multipart/form-data body: fields {name: str}, files {name: (filename, bytes, content type)}."""
    b = uuid.uuid4().hex
    out = io.BytesIO()
    for k, v in fields.items():
        out.write(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, (fname, data, ct) in files.items():
        out.write(f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{fname}"\r\n'
                  f'Content-Type: {ct}\r\n\r\n'.encode())
        out.write(data)
        out.write(b'\r\n')
    out.write(f'--{b}--\r\n'.encode())
    return out.getvalue(), f'multipart/form-data; boundary={b}'


class _Conn(http.client.HTTPSConnection):
    """HTTPS to `connect_ip` with TLS and Host for the site's own name (curl --resolve)."""

    def __init__(self, host, connect_ip=None, **kw):
        super().__init__(host, **kw)
        self.connect_ip = connect_ip

    def connect(self):
        if not self.connect_ip:
            return super().connect()
        sock = socket.create_connection((self.connect_ip, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


class Client:
    """Requests to one replica site. gate=None reads the gate password from GATE_FILE on first use."""

    def __init__(self, site=SITE, connect=None, gate=None, gate_file=GATE_FILE, episode=EPISODE):
        self.site = site.rstrip('/')
        p = check_site(self.site)
        self.host, self.port = p.hostname, p.port or 443
        self.connect, self.episode = connect, episode
        self._gate, self.gate_file = gate, gate_file
        self.ctx = ssl.create_default_context()

    def gate(self):
        if self._gate is None:
            with open(self.gate_file) as fh:
                self._gate = 'Basic ' + base64.b64encode(f'{GATE_USER}:{fh.readline().strip()}'.encode()).decode()
        return self._gate

    def path_of(self, url):
        """A site path from an absolute URL on the site or a path; anything else is refused."""
        if url.startswith('/'):
            return url
        p = urllib.parse.urlparse(url)
        if (p.scheme, (p.hostname or '').lower(), p.port or 443) != ('https', self.host.lower(), self.port):
            raise SystemExit(f'refusing a request outside the replica site: {url}')
        return p.path + (f'?{p.query}' if p.query else '')

    def request(self, method, url, body=None, token=None, ctype=None, raw=False, timeout=120, retries=3):
        """One request; token=None -> the basic-auth gate. Returns parsed JSON (bytes if raw). Raises ApiError.
        Connection errors and 502/503/504 are retried (idempotent methods only)."""
        path = self.path_of(url)
        headers = {'Authorization': f'Bearer {token}' if token else self.gate(), 'Accept': 'application/json',
                   'User-Agent': 'bc23-replica-tools'}
        data = None
        if body is not None:
            if ctype:
                data, headers['Content-Type'] = body, ctype
            else:
                data, headers['Content-Type'] = json.dumps(body).encode(), 'application/json'
        for attempt in range(retries + 1):
            conn = _Conn(self.host, connect_ip=self.connect, port=self.port, timeout=timeout, context=self.ctx)
            try:
                conn.request(method, path, body=data, headers=headers)
                r = conn.getresponse()
                status, out = r.status, r.read()
            except (OSError, http.client.HTTPException) as e:
                if method != 'GET' or attempt == retries:
                    raise ApiError(0, f'{type(e).__name__}: {e}') from None
                time.sleep(2 + 3 * attempt)
                continue
            finally:
                conn.close()
            if status in (502, 503, 504) and method == 'GET' and attempt < retries:
                time.sleep(2 + 3 * attempt)
                continue
            if status >= 400:
                raise ApiError(status, out.decode(errors='replace')[:2000])
            if raw:
                return out
            return json.loads(out) if out else None
        raise ApiError(0, 'unreachable')

    def pages(self, path, token=None, limit=None):
        """Follow siarnaq's paginated lists ({count, next, results}); a plain list is returned as is."""
        out, url, n = [], path, 0
        while url and (limit is None or n < limit):
            r = self.request('GET', url, token=token)
            if isinstance(r, list):
                return r
            out += r.get('results', [])
            url = r.get('next')
            n += 1
        return out

    def login(self, username, password):
        """POST /api/token/ (the login form) -> access token."""
        return self.request('POST', '/api/token/', {'username': username, 'password': password})['access']


class Session:
    """One user logged in to the site: api() carries its JWT and logs in again once if the token is refused."""

    def __init__(self, client, username, password):
        self.c, self.username, self._pw = client, username, password
        self.token = None

    def api(self, method, path, body=None, **kw):
        if self.token is None:
            self.token = self.c.login(self.username, self._pw)
        try:
            return self.c.request(method, path, body, token=self.token, **kw)
        except ApiError as e:
            if e.code not in (401, 403) or 'token' not in e.detail.lower():
                raise
            self.token = self.c.login(self.username, self._pw)
            return self.c.request(method, path, body, token=self.token, **kw)

    def pages(self, path, limit=None):
        if self.token is None:
            self.token = self.c.login(self.username, self._pw)
        return self.c.pages(path, token=self.token, limit=limit)


def rankings(client, episode=None):
    """The Rankings page's data: GET /api/team/<ep>/t/?ordering=-rating,name, every page, logged out (the gate).
    -> [{'rank', 'id', 'name', 'rating', 'status', 'has_active_submission', 'members', 'quote'}] in page order."""
    ep = episode or client.episode
    out = []
    for i, t in enumerate(client.pages(f'/api/team/{ep}/t/?ordering=-rating%2Cname')):
        prof = t.get('profile') or {}
        out.append({'rank': i + 1, 'id': t['id'], 'name': t['name'], 'rating': prof.get('rating'),
                    'status': t.get('status'), 'has_active_submission': t.get('has_active_submission'),
                    'members': [m.get('username') for m in t.get('members') or []], 'quote': prof.get('quote') or ''})
    return out
