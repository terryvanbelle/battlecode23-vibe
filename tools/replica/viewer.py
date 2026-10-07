#!/usr/bin/env python3
"""Install the replay viewer: the official Battlecode 2023 web client (release 3.0.15), self-hosted by web.py.

The files come from a one-time, read-only download of the official public web-client release, made on 2026-10-07 and
recorded with every URL and sha256 in docs/replica/VIEWER.md. This script never downloads anything. It checks a local
copy against the pins below and copies what the server needs (out/app.js and the client's images) into
$REPLICA_VIEWER_DIR (default $REPLICA_HOME/viewer), where web.py serves it under /viewer/out/. The release's own
visualizer.html is pinned for provenance but not served: web.py renders an equivalent page without the external
font stylesheet (docs/replica/VIEWER.md).

  python3 tools/replica/viewer.py check SRC      verify SRC (a directory holding visualizer.html and out/)
  python3 tools/replica/viewer.py install SRC    verify SRC, then copy it into the viewer dir (run as the replica user)
  python3 tools/replica/viewer.py status         verify the installed copy
On battlecode-dev the downloaded copy lives in ~terryvanbelle/projects/vibe/bc23-viewer-3.0.15 (outside the repo).
"""
import hashlib
import os
import shutil
import sys

if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from replica import web   # noqa: E402
else:
    from . import web

VERSION = '3.0.15'
# sha256 of every file of the downloaded web client (path relative to the client root).
PINS = {
    'visualizer.html': 'd7408c481b4864a293e716687bff78df59c627f8291e5a285709bc9e4ac3f7df',
    'out/app.js': '18224c97d0716c8d54a6ea3035a78270ea1d26c4164ac7b22dd419bce1d8299e',
    'out/accelerating_anchor-28RvaC8.png': '87314dd0a15a375aacf89e9138b406343acbfe8d5c523fdf37f0822abe2d68e2',
    'out/adamantium-3Fm4tKT.png': '5317abedc1fe48956935abccb536255eb7e2df2086c06f321df463ca792607b4',
    'out/adamantium_well-1kamILF.png': '31882512a3622000c46e27cdf55408c09434c393ff215f1440c4aad45e8db11a',
    'out/adamantium_well_upgraded-2IAFOfE.png': 'a3648a702eb16b3f4754f192c20395ffe5f7db3488c5aff4b2f674091f41e195',
    'out/anchor-1YMw3VT.png': '9f3d5e4c5dc80370a68434299c2cde6c8c0013ee970e896d4a94f025a600be09',
    'out/blue_amplifier-3MreEw-.png': '9b2fcd54271a4856852fe9391bba0a80bc06a94754fa3fd2ad3a3e795ed6599a',
    'out/blue_booster-2tIkyvu.png': '5d132bf8d7bfbec8928f78e17c55f5b3bfaef9271cf591d44641815c36bcc79a',
    'out/blue_carrier-1yl6Fmp.png': 'a1d033a897db302220826901f2f350ec06bf0ece2fb77aa629767cd02c71197a',
    'out/blue_destabilizer-2qduVso.png': '4c5faee8c59d4355ef2563049d666d3b871366908dda0507eb898623bea52839',
    'out/blue_headquarters-1CRcHK6.png': '84832450c5b601850787a7afaa264042883542ec948dc74b36a9aa52c1d67fbe',
    'out/blue_launcher-39KWivh.png': '291f4d4ab78563b0e347339e78d646dcdaf910282a9ffc2e652cb91d65aeec9f',
    'out/elixir-doIIVgD.png': '0197014978019e9aaec0925ffc3f7b3a9d1114c1da69428008b9b22f346b76c2',
    'out/elixir_well-2iS1DjJ.png': 'd097a030ca1343c4f010cfc129f549d05c391bd272d3511dbdd56bccb60ce24d',
    'out/elixir_well_upgraded-J1onBnd.png': '852521fbb632a007189f39d90fc26498442719c6eb4a6031d59bb2a10833df7e',
    'out/mana-2F-J7Aq.png': '0cdda4da678841418e5018f107789369dde4b3547d6886960fc668237cdca40a',
    'out/mana_well-10tEVDo.png': '38ae7024c488a4fbe97d8ceb1be5d3ffc37a89921a1e339f6faeae5a4894b868',
    'out/mana_well_upgraded-gdzfxoz.png': 'a48e0882388aa0d7f2f1571af4304f60542e695fae6b43b8705c34cf35269083',
    'out/red_amplifier-2duPjF9.png': '1625736bab0f60b1c9d504e11aaad9c39b9702ba11d6b8eed6256346d5317113',
    'out/red_booster-3m3EMHO.png': 'dcc51b12a6b7980182be76e510d4e06c5662f4fd896d1fd9676789eb4311eaef',
    'out/red_carrier-3QDuG23.png': '6a0c01b796d3e83e9bb611cac61f0f3bd77e24b07ee8a4ea25b618cb6ed869a8',
    'out/red_destabilizer-2d6gJ0c.png': 'b6e9c48f9c2ded576b9ea1d4f166e649d88f798804b9cbf60601f6bfbf01dc7c',
    'out/red_headquarters-2lACvwz.png': '486beaceccde7e582d93254bd870b85f7b8d35fc24bca7df4433985a8d0f437e',
    'out/red_launcher-3xzUg_N.png': 'eb03fd4ae5e4940c1442f85eadb893f7327bb4f05097d01779dc73357e3d74b0',
}
SERVED = sorted(p for p in PINS if p.startswith('out/'))


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def check(src, files=None, pins=None):
    """[(path, problem)] for every pinned file under src that is missing or has another sha256."""
    pins = PINS if pins is None else pins
    bad = []
    for rel in (files if files is not None else sorted(pins)):
        p = os.path.join(src, rel)
        if not os.path.isfile(p):
            bad.append((rel, 'missing'))
        elif sha256(p) != pins[rel]:
            bad.append((rel, 'sha256 mismatch'))
    return bad


def install(src, dest=None, pins=None):
    """Verify src, then copy the served files into dest (default web.viewer_dir()) through a staging dir and a
    rename, so a running server never sees a half-installed viewer. Returns dest."""
    pins = PINS if pins is None else pins
    bad = check(src, pins=pins)
    if bad:
        raise SystemExit('viewer: refusing to install: ' + '; '.join(f'{p} {why}' for p, why in bad))
    dest = os.path.abspath(dest or web.viewer_dir())
    stage, old = dest + '.new', dest + '.old'
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(os.path.join(stage, 'out'))
    for rel in sorted(p for p in pins if p.startswith('out/')):
        shutil.copyfile(os.path.join(src, rel), os.path.join(stage, rel))
    with open(os.path.join(stage, 'VERSION'), 'w') as fh:
        fh.write(f'battlecode23 web client {VERSION}; files verified against tools/replica/viewer.py PINS\n')
    shutil.rmtree(old, ignore_errors=True)
    if os.path.exists(dest):
        os.rename(dest, old)
    os.rename(stage, dest)
    shutil.rmtree(old, ignore_errors=True)
    return dest


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else ''
    if cmd in ('check', 'install') and len(argv) == 2:
        src = os.path.abspath(os.path.expanduser(argv[1]))
        if cmd == 'check':
            bad = check(src)
            for p, why in bad:
                print(f'BAD  {p}: {why}')
            print(f'viewer {VERSION} at {src}: ' + ('all {} files match the pins'.format(len(PINS)) if not bad
                                                     else f'{len(bad)} of {len(PINS)} files fail'))
            return 1 if bad else 0
        dest = install(src)
        print(f'viewer {VERSION}: {len(SERVED)} files verified and installed in {dest}')
        return 0
    if cmd == 'status' and len(argv) == 1:
        dest = web.viewer_dir()
        bad = check(dest, SERVED)
        print(f'viewer dir {dest}: ' + ('installed, {} files match the pins'.format(len(SERVED)) if not bad
                                        else f'{len(bad)} of {len(SERVED)} files missing or modified'))
        return 1 if bad else 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
