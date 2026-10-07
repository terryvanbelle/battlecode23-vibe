#!/usr/bin/env python3
"""List every absolute URL in galaxy's built frontend and fail if any is fetched automatically.

  python3 tools/galaxy/frontend/check_bundle.py DIST      (DIST = the Vite build output: index.html, assets/, ...)

Every shipped file except source maps (*.map: fetched only by an open developer console; reported separately) is
scanned for scheme URLs (http, https, ws, wss) and quoted protocol-relative URLs. Each occurrence gets a kind from the
code just before it:
  FETCH  loaded without a click: fetch/XHR/WebSocket/EventSource/Worker/importScripts/sendBeacon, src/srcset/poster/
         data/url/basePath/action/formAction assignments, CSS url() and @import, location assignments and redirects,
         <script>/<link>/<img>/<iframe>/... tags, window.open;
  LINK   a hyperlink the user may click: href/to props, markdown [text](url) and [url] forms, window.open in an
         onClick handler, and the five reviewed react-social-icons URLs (SOCIAL_ICON_URLS);
  TEXT   anything else: comments, license text, XML namespaces, messages.
The check fails (exit 1) when
  - any FETCH URL names another host (the site must load and call only its own origin);
  - any battlecode.org URL is not a LINK, or battlecode.org appears outside a URL;
  - a banned string appears anywhere (api.battlecode.org, Google Fonts, analytics, Sentry);
  - index.html lacks the replica's Content-Security-Policy (connect-src 'self', ...).
Output: one tab-separated line per URL occurrence (kind, host, file, url, context), then a summary.
"""
import os
import re
import sys

URL_RE = re.compile(r"""(?:(?:https?|wss?):)//[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+(?::\d+)?[^\s"'`<>()\\]*"""
                    r"""|(?<=["'`(])//[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[a-z]{2,}(?::\d+)?(?:/[^\s"'`<>()\\]*)?""")
FETCH_BEFORE = [re.compile(p + r'\s*["\'`]?$') for p in (
    r'\b(?:fetch|importScripts|sendBeacon|WebSocket|EventSource|Worker|SharedWorker|open|assign|replace|redirect'
    r'|import)\s*\(',
    r'\.open\(\s*["\'`]\w+["\'`]\s*,',
    r'\b(?:src|srcset|poster|data|action|formAction|basePath|BASE_PATH|baseURL|baseUrl|endpoint|url|URL|location'
    r'|href\s*=\s*location|location\.href)\s*[:=]',
    r'\burl\(',
    r'@import\s+(?:url\()?',
)] + [re.compile(r'<(?:script|link|img|iframe|source|video|audio|embed|object|track|input|form|meta\s+http-equiv'
                 r'="refresh")\b[^<>]*$', re.I)]
LINK_BEFORE = [re.compile(p) for p in (
    r'\b(?:href|to)\s*[:=]\s*\{?\s*["\'`]?$',
    r'\]\($',             # markdown [text](url)
    r'\[$',               # markdown [url](...), the link text
    r'<a\b[^<>]*$',
    r'\bhref\s*[:=]\s*["\'`]javascript:window\.open\(\s*["\']?$',             # Highcharts credits link
    r'\bonClick\s*:\s*(?:\([^()]*\)|\w+)\s*=>\s*\{?\s*window\.open\(\s*["\'`]?$',  # opened by a click
)]
# Reviewed by hand: the `url` prop of react-social-icons' SocialIcon (galaxy's sidebar footer) renders <a href=url>
# around an inline SVG chosen from the URL's domain; nothing is fetched. Only these exact URLs get this reading.
SOCIAL_ICON_BEFORE = re.compile(r'\.jsx\(\w+,\{url:\s*["\'`]$')
SOCIAL_ICON_URLS = {'https://discord.gg/N86mxkH', 'https://www.youtube.com/@MITBattlecode', 'https://x.com/mitbattlecode',
                    'https://www.instagram.com/mitbattlecode', 'https://www.github.com/battlecode'}
TEXT_BEFORE = [re.compile(p) for p in (r'(?:createElementNS|setAttributeNS|getAttributeNS)\(\s*["\'`]?$',
                                       r'xmlns(?::\w+)?\s*[:=]\s*["\'`]?$')]
BANNED = ('api.battlecode.org', 'fonts.googleapis.com', 'fonts.gstatic.com', 'googletagmanager.com',
          'google-analytics.com', 'gtag(', 'sentry.io', 'sentry-cdn', 'plausible.io', 'posthog', 'hotjar',
          'segment.com/analytics', 'mixpanel', 'amplitude.com/libs', 'cdn.jsdelivr', 'unpkg.com', 'cdnjs.')
CSP_NEEDS = ("default-src 'self'", "script-src 'self'", "connect-src 'self'", "img-src 'self'", "font-src 'self'",
             "frame-src 'self'", "form-action 'self'")
TEXT_EXT = ('.html', '.js', '.mjs', '.css', '.json', '.txt', '.svg', '.webmanifest', '.xml', '.map')
FETCH_ALLOW = set()      # hosts a FETCH may name: none (relative URLs are not matched)


def host_of(url):
    return re.split(r'[/?#:]', re.sub(r'^(?:[a-z]+:)?//', '', url))[0].lower()


def classify(before, url=''):
    """Kind of a URL occurrence from up to 200 characters of text before it."""
    tail = before[-200:]
    if url in SOCIAL_ICON_URLS and SOCIAL_ICON_BEFORE.search(tail):
        return 'LINK'
    if any(p.search(tail) for p in TEXT_BEFORE):
        return 'TEXT'
    if any(p.search(tail) for p in LINK_BEFORE):
        return 'LINK'
    if any(p.search(tail) for p in FETCH_BEFORE):
        return 'FETCH'
    return 'TEXT'


def scan_text(text):
    """[(kind, host, url, start, end)] for every URL occurrence in text."""
    out = []
    for m in URL_RE.finditer(text):
        url = m.group(0).rstrip('.,;:]}')
        out.append((classify(text[max(0, m.start() - 200):m.start()], url), host_of(url), url, m.start(), m.end()))
    return out


def problems_in(text, rel, hits):
    """Failures for one file, given its URL occurrences."""
    bad = []
    for kind, host, url, _s, _e in hits:
        if kind == 'FETCH' and host not in FETCH_ALLOW:
            bad.append(f'{rel}: automatically fetched URL {url}')
        if host.endswith('battlecode.org') and kind != 'LINK':
            bad.append(f'{rel}: battlecode.org URL that is not a hyperlink ({kind}): {url}')
    spans = [(s, e) for _k, _h, _u, s, e in hits]
    for m in re.finditer(r'battlecode\.org', text):
        if not any(s <= m.start() < e for s, e in spans):
            bad.append(f'{rel}: battlecode.org outside a URL: ...{context(text, m.start(), m.end())}...')
    low = text.lower()
    for b in BANNED:
        if b in low:
            bad.append(f'{rel}: banned string {b!r}')
    return bad


def context(text, s, e, width=60):
    return re.sub(r'\s+', ' ', text[max(0, s - width):min(len(text), e + 20)])


def check_csp(index_html):
    m = re.search(r'<meta\s+http-equiv="Content-Security-Policy"\s+content="([^"]*)"', index_html)
    if not m:
        return ['index.html: no Content-Security-Policy meta tag']
    csp = m.group(1)
    bad = [f'index.html: CSP lacks {need!r}' for need in CSP_NEEDS if need not in csp]
    if re.search(r'https?:|\*', csp):
        bad.append('index.html: CSP allows another host')
    if re.search(r'<(?:script|link)\b[^>]*(?:src|href)="(?:https?:)?//', index_html):
        bad.append('index.html: loads a script or stylesheet from another host')
    return bad


def check(dist):
    """(rows, problems, map_counts): rows = [(kind, host, rel, url, ctx)] for shipped files."""
    rows, bad, maps = [], [], {}
    for root, _dirs, files in os.walk(dist):
        for name in sorted(files):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, dist)
            if not name.endswith(TEXT_EXT):
                continue
            with open(path, encoding='utf-8', errors='replace') as fh:
                text = fh.read()
            if name.endswith('.map'):
                maps[rel] = text.count('battlecode.org')
                continue
            hits = scan_text(text)
            rows += [(k, h, rel, u, context(text, s, e)) for k, h, u, s, e in hits]
            bad += problems_in(text, rel, hits)
    index = os.path.join(dist, 'index.html')
    if os.path.isfile(index):
        with open(index, encoding='utf-8') as fh:
            bad += check_csp(fh.read())
    else:
        bad.append('no index.html')
    return sorted(rows), bad, maps


def main(argv):
    if len(argv) != 2 or not os.path.isdir(argv[1]):
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    rows, bad, maps = check(argv[1])
    for k, h, rel, u, ctx in rows:
        print(f'{k}\t{h}\t{rel}\t{u}\t{ctx}')
    kinds = {k: sum(1 for r in rows if r[0] == k) for k in ('FETCH', 'LINK', 'TEXT')}
    bco = [r for r in rows if r[1].endswith('battlecode.org')]
    print(f'# {len(rows)} URL occurrences in shipped files: {kinds}; battlecode.org: {len(bco)}, all LINK: '
          f'{all(r[0] == "LINK" for r in bco)}; source maps (not shipped to browsers unless a console opens them): '
          f'{sum(maps.values())} battlecode.org strings in {len(maps)} files')
    for b in bad:
        print(f'FAIL {b}')
    print('bundle check: ' + ('PASS' if not bad else f'FAIL ({len(bad)} problems)'))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
