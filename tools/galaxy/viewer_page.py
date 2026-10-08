#!/usr/bin/env python3
"""The galaxy site's replay viewer: the official Battlecode 2023 web client (3.0.15), served by Caddy under /viewer/.

  python3 tools/galaxy/viewer_page.py install SRC DEST    verify SRC (the one-time download, pinned in
                                                          tools/replica/viewer.py), copy out/ into DEST, write
                                                          DEST/visualizer.html and DEST/galaxy-viewer.js
  python3 tools/galaxy/viewer_page.py page                print visualizer.html
The galaxy frontend links a bc23 replay as /viewer/visualizer.html?<replay_url> (frontend/src/api/helpers.ts; the
2023 client's own form), where replay_url is what siarnaq's Match.get_replay_url() returns through the storage
stand-in: /storage/bc23-replica-secure/episode/<episode>/replays/<uuid>.<episode>. The page accepts that path (also
as ?gameSource=<path>, or as an absolute URL on this origin) and nothing else, so the client loads replays of this
site only; Caddy's Content-Security-Policy (connect-src 'self') keeps every request on this origin. As in
tools/replica/web.py's page: no Google Fonts stylesheet, no websocket URL, no tournament mode. The mount script is a
file of its own (script-src 'self', no inline script). Provenance of the client files: docs/replica/VIEWER.md.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from replica import viewer  # noqa: E402

REPLAY_PATH_RE = r'^\/storage\/bc23-replica-secure\/episode\/[a-z0-9]{1,16}\/replays\/[0-9a-f-]{36}\.[a-z0-9]{1,16}$'

SCRIPT = """// bc23 galaxy replica: mount the Battlecode 2023 client on a replay of this site (tools/galaxy/viewer_page.py)
(function () {
  var q = window.location.search.substring(1);
  var url = q;
  if (q.indexOf('gameSource=') === 0) url = q.substring(11);
  url = decodeURIComponent(url.split('&')[0]);
  var origin = window.location.origin;
  if (url.indexOf(origin + '/') === 0) url = url.substring(origin.length);
  var ok = /%s/.test(url);
  var config = {};
  if (ok) config.matchFileURL = url;
  window.battleClient = window.battlecode.mount(document.getElementById('client'), config);
})();
""" % REPLAY_PATH_RE

PAGE = ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Battlecode 2023 client</title>'
        '<style>html,body{height:100%;overflow:hidden;margin:0}</style></head>\n<body>'
        '<div id="altContent"><h1>Loading Battlecode client...</h1></div><div id="client"></div>\n'
        '<script type="text/javascript" src="out/app.js" charset="utf-8"></script>\n'
        '<script type="text/javascript" src="galaxy-viewer.js" charset="utf-8"></script>\n</body></html>\n')


def install(src, dest):
    dest = viewer.install(src, dest)
    for name, text in (('visualizer.html', PAGE), ('galaxy-viewer.js', SCRIPT)):
        with open(os.path.join(dest, name), 'w') as fh:
            fh.write(text)
    return dest


def main(argv):
    if len(argv) == 3 and argv[0] == 'install':
        dest = install(os.path.abspath(argv[1]), os.path.abspath(argv[2]))
        print(f'galaxy viewer: {len(viewer.SERVED)} client files verified and installed in {dest}')
        return 0
    if argv == ['page']:
        sys.stdout.write(PAGE)
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
