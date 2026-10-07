# Replay viewer: the official Battlecode 2023 web client, self-hosted

The replica's web front plays match replays in the browser with the **official Battlecode 2023 web client
(visualizer), release 3.0.15**, unmodified, served by the replica's own HTTP server (`tools/replica/web.py`) under
`/viewer/`. Every match page has a **Watch replay** link. Nothing in the viewer contacts Battlecode or any other
host at runtime (section 4).

| URL (behind Caddy: HTTPS + basic auth) | What |
|---|---|
| `/viewer/visualizer.html?gameSource=/replay/<uuid>.bc23` | the viewer, playing one match's replay (all its games) |
| `/viewer/visualizer.html?/replay/<uuid>.bc23` | the same; this is the 2023 client's own form |
| `/viewer/visualizer.html` | the viewer with no replay (drop a local `.bc23` file on it) |
| `/viewer/out/app.js`, `/viewer/out/<name>-<hash>.png` | the client bundle and its images |
| `/replay/<uuid>.bc23` | the raw replay, exactly as the engine wrote it |

**Query parameter.** The 2023 client takes the whole query string as the match file URL. Its `visualizer.html`
runs `match_url = window.location.search.substr(1)` and then `config.matchFileURL = match_url`. Galaxy's frontend
builds bc22/bc23 links the same way, as `visualizer.html?<gameSource>` (`frontend/src/api/helpers.ts:146-150`).
`?gameSource=<url>` is the form from 2024 onward. The replica's page accepts both forms and loads only this
replica's replays: the URL must match `/replay/<uuid>.bc23`.

## 1. Provenance: the one-time download

Option (a) of the brief, an official release artifact, worked, so nothing was built from source.

- **When and how:** 2026-10-07T19:52:01Z, from the driver (`claude-driver`), with plain read-only
  `curl --proto '=https' -fsS` GETs. There were 26 requests: 25 files (all 200) and 1 request that returned 403,
  for `./static/img/controls/skip-forward.png`, a path the image-name extraction matched by mistake. Nothing was
  sent except the GETs, and nothing has been fetched since. `tools/replica/viewer.py` contains no network code.
- **Base URL:** `https://releases.battlecode.org/client/battlecode23/3.0.15/`. Files:
  `https://releases.battlecode.org/client/battlecode23/3.0.15/visualizer.html`,
  `https://releases.battlecode.org/client/battlecode23/3.0.15/out/app.js`, and
  `https://releases.battlecode.org/client/battlecode23/3.0.15/out/<file>.png` for the 23 images below.
- **Why that path:** the bc23 release workflow builds the web client with `npm run prod` and uploads `out/` and
  `visualizer.html` to `gs://mitbattlecode-releases/client/battlecode23/$RELEASE_VERSION/`, which is served as
  `releases.battlecode.org` (`reference/battlecode23/.github/workflows/release.yml:99-101, 120-124`). 3.0.15 is
  the engine version the replica runs (`engine/battlecode23-3.0.15.jar`).
- **The image list:** webpack emits images over its inline limit as `out/<name>-<hash7>.png`. The 23 names were
  taken from `app.js` (`n.p="out/"` plus each emitted name). Smaller images are inlined in `app.js` as data URIs.
- **Cross-checks against the source** (`reference/battlecode23`, tag 3.0.15): `visualizer.html` is byte-identical
  to `client/visualizer/visualizer.html`, and all 23 PNGs are byte-identical to their originals under
  `client/visualizer/src/static/img/`. `app.js` cannot be compared byte for byte without a node build. Its config
  says `gameVersion:"3.0.14"`, as `client/visualizer/src/config.ts:157` does at tag 3.0.15, so the splash screen
  shows "v3.0.14". That text is cosmetic.

| File | Bytes | sha256 |
|---|---:|---|
| `visualizer.html` | 1422 | `d7408c481b4864a293e716687bff78df59c627f8291e5a285709bc9e4ac3f7df` |
| `out/app.js` | 1148565 | `18224c97d0716c8d54a6ea3035a78270ea1d26c4164ac7b22dd419bce1d8299e` |
| `out/accelerating_anchor-28RvaC8.png` | 266347 | `87314dd0a15a375aacf89e9138b406343acbfe8d5c523fdf37f0822abe2d68e2` |
| `out/adamantium-3Fm4tKT.png` | 270216 | `5317abedc1fe48956935abccb536255eb7e2df2086c06f321df463ca792607b4` |
| `out/adamantium_well-1kamILF.png` | 284942 | `31882512a3622000c46e27cdf55408c09434c393ff215f1440c4aad45e8db11a` |
| `out/adamantium_well_upgraded-2IAFOfE.png` | 319506 | `a3648a702eb16b3f4754f192c20395ffe5f7db3488c5aff4b2f674091f41e195` |
| `out/anchor-1YMw3VT.png` | 269853 | `9f3d5e4c5dc80370a68434299c2cde6c8c0013ee970e896d4a94f025a600be09` |
| `out/blue_amplifier-3MreEw-.png` | 223899 | `9b2fcd54271a4856852fe9391bba0a80bc06a94754fa3fd2ad3a3e795ed6599a` |
| `out/blue_booster-2tIkyvu.png` | 241846 | `5d132bf8d7bfbec8928f78e17c55f5b3bfaef9271cf591d44641815c36bcc79a` |
| `out/blue_carrier-1yl6Fmp.png` | 224165 | `a1d033a897db302220826901f2f350ec06bf0ece2fb77aa629767cd02c71197a` |
| `out/blue_destabilizer-2qduVso.png` | 323254 | `4c5faee8c59d4355ef2563049d666d3b871366908dda0507eb898623bea52839` |
| `out/blue_headquarters-1CRcHK6.png` | 233225 | `84832450c5b601850787a7afaa264042883542ec948dc74b36a9aa52c1d67fbe` |
| `out/blue_launcher-39KWivh.png` | 345963 | `291f4d4ab78563b0e347339e78d646dcdaf910282a9ffc2e652cb91d65aeec9f` |
| `out/elixir-doIIVgD.png` | 343162 | `0197014978019e9aaec0925ffc3f7b3a9d1114c1da69428008b9b22f346b76c2` |
| `out/elixir_well-2iS1DjJ.png` | 331452 | `d097a030ca1343c4f010cfc129f549d05c391bd272d3511dbdd56bccb60ce24d` |
| `out/elixir_well_upgraded-J1onBnd.png` | 333904 | `852521fbb632a007189f39d90fc26498442719c6eb4a6031d59bb2a10833df7e` |
| `out/mana-2F-J7Aq.png` | 341060 | `0cdda4da678841418e5018f107789369dde4b3547d6886960fc668237cdca40a` |
| `out/mana_well-10tEVDo.png` | 282216 | `38ae7024c488a4fbe97d8ceb1be5d3ffc37a89921a1e339f6faeae5a4894b868` |
| `out/mana_well_upgraded-gdzfxoz.png` | 304800 | `a48e0882388aa0d7f2f1571af4304f60542e695fae6b43b8705c34cf35269083` |
| `out/red_amplifier-2duPjF9.png` | 216107 | `1625736bab0f60b1c9d504e11aaad9c39b9702ba11d6b8eed6256346d5317113` |
| `out/red_booster-3m3EMHO.png` | 235432 | `dcc51b12a6b7980182be76e510d4e06c5662f4fd896d1fd9676789eb4311eaef` |
| `out/red_carrier-3QDuG23.png` | 220168 | `6a0c01b796d3e83e9bb611cac61f0f3bd77e24b07ee8a4ea25b618cb6ed869a8` |
| `out/red_destabilizer-2d6gJ0c.png` | 314948 | `b6e9c48f9c2ded576b9ea1d4f166e649d88f798804b9cbf60601f6bfbf01dc7c` |
| `out/red_headquarters-2lACvwz.png` | 227851 | `486beaceccde7e582d93254bd870b85f7b8d35fc24bca7df4433985a8d0f437e` |
| `out/red_launcher-3xzUg_N.png` | 334542 | `eb03fd4ae5e4940c1442f85eadb893f7327bb4f05097d01779dc73357e3d74b0` |

The same 25 hashes are pinned in `tools/replica/viewer.py` (`PINS`). The served files take 7.3 MiB.

## 2. Where the files are

- **Download copy (install source):** `~/projects/vibe/bc23-viewer-3.0.15/` on battlecode-dev, outside the repo.
  It holds the 25 files, `SHA256SUMS` and `fetched-at.txt`. `sha256sum -c SHA256SUMS` passes.
- **Served copy:** `$REPLICA_VIEWER_DIR`, which defaults to `$REPLICA_HOME/viewer`, so on battlecode-dev it is
  `/home/bcreplica/replica/viewer/`. It holds `out/` (`app.js` and the 23 images, 24 files) and `VERSION`, owned
  by `bcreplica`. The release's own `visualizer.html` is pinned but not served (section 3).
- The repo holds none of the client's files, only the pins and this record.

## 3. Install, check, reinstall

```bash
# on battlecode-dev, from ~/projects/vibe/2023
python3 tools/replica/viewer.py check ~/projects/vibe/bc23-viewer-3.0.15      # all 25 files against the pins
sudo -u bcreplica env REPLICA_HOME=/home/bcreplica/replica bash -c \
  'umask 027; python3 tools/replica/viewer.py install /home/terryvanbelle/projects/vibe/bc23-viewer-3.0.15'
sudo -u bcreplica env REPLICA_HOME=/home/bcreplica/replica python3 tools/replica/viewer.py status
```

`install` refuses to copy anything unless every pinned file matches. It stages the copy in `viewer.new` and swaps
it in with a rename, so the running server never sees a half-installed viewer. Nothing needs restarting. Without an
installed viewer, `/viewer/visualizer.html` answers 503 with these instructions, and the raw replays still work.
If the download copy is lost, a new one-time download of the same URLs must reproduce the hashes above. Record any
new download here.

**The served page.** `web.py` renders its own `visualizer.html` instead of serving the release's. It loads
`out/app.js` and mounts the client the same way, with four differences:
1. no Google Fonts stylesheet (the release page links `fonts.googleapis.com/css?family=Graduate`), so the client
   falls back to a local font;
2. `websocketURL` is left unset; the release page sets `ws://localhost:6175`, the live-game socket of a local
   engine, which the replica disables (`-Dbc.server.websocket=false`);
3. only `/replay/<uuid>.bc23` URLs are passed to the client, from `?gameSource=` or the bare query;
4. no tournament mode.

The page sends this Content-Security-Policy. The inline script is pinned by its hash, and `connect-src 'self'`
limits the client's network requests (XHR, fetch, WebSocket) to this origin:
`default-src 'self'; script-src 'self' 'sha256-…'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:;
connect-src 'self'; font-src 'self' data:; frame-src 'self'; worker-src 'self' blob:; object-src 'none';
base-uri 'none'; form-action 'none'; frame-ancestors 'self'`.

## 4. Absolute URLs inside the bundle

From `grep -oE '(https?:)?//[A-Za-z0-9.-]+\.[a-z]{2,}[^"'"'"' )]*' out/app.js`, plus checks for `fetch(`,
`XMLHttpRequest`, `new WebSocket`, `importScripts`, `sendBeacon` and `@import`. None of these URLs is fetched
when a replay is played. Each was left in place: the bundle stays byte-identical to the pinned release file.

| URL in `app.js` | Where it is used | Fetched by the replica's viewer? |
|---|---|---|
| `https://play.battlecode.org/replays/<id>.bc23` | tournament mode: builds replay URLs from a tournament JSON loaded in the Queue tab | no: the page never enables tournament mode, and `connect-src 'self'` would block it |
| `new WebSocket(this.url)` | live games from a local engine, only when `websocketURL` is set | no: left unset; CSP limits sockets to this origin |
| `XMLHttpRequest` (`loadGameFromURL`) | loads `matchFileURL` | yes, the one request: `/replay/<uuid>.bc23` on this origin |
| `https://www.speedscope.app/file-format-schema.json` | a `$schema` string inside a message to the profiler iframe | no: it is a string, not a request |
| `https://discordapp.com/channels/…`, `https://github.com/battlecode/battlecode23-scaffold/blob/master/{build.gradle,gradle.properties}` | links in the Help text | only if the viewer user clicks one |
| `http://momentjs.com/guides/#/warnings/…` | text of console warnings | no |
| `https://github.com/marcj/css-element-queries`, `https://davidwalsh.name/detect-node-insertion` | library comments | no |

The client source also has version checks against `api.battlecode.org` and `2023.battlecode.org`
(`client/visualizer/src/main/sidebar.ts:230-258`, `gamearea/gamearea.ts:99-125`). They sit under
`if (process.env.ELECTRON)` and are not in the web bundle: `battlecode.org` appears in `app.js` only in the
tournament-mode string above.

## 5. Verification (2026-10-07, battlecode-dev, through Caddy with the owner password)

```
/viewer/visualizer.html?gameSource=/replay/7d21a717-d249-4601-999c-be794d725fde.bc23  200 text/html 861 B
/viewer/out/app.js                                         200 application/javascript 1148565 B sha256=18224c97d0716c8d…
/viewer/out/red_carrier-3QDuG23.png                        200 image/png 220168 B sha256=6a0c01b796d3e83e…
/replay/7d21a717-d249-4601-999c-be794d725fde.bc23          200 application/octet-stream 2092709 B sha256=f5e1f7d1dcf0d800…
/replay/7cc904ae-c26c-453e-b8b6-f2985fec5cfb.bc23          200 application/octet-stream 3146301 B sha256=6632e5292db16d0c…
```

The replay hashes equal those of the files in `/home/bcreplica/replica/replay/`. `verify.sh` also checks for
`replay viewer page: 200`.

**In a browser:** headless Chromium on the VM opened
`http://127.0.0.1:8023/viewer/visualizer.html?gameSource=/replay/7cc904ae-….bc23` directly on loopback, since
basic auth in a headless browser would have put the password on a command line. Its console, in order:
`Battlecode client loading...`, `Total 44 images loaded: 44 successful, 0 failed.`,
`Loading provided match file: /replay/7cc904ae-c26c-453e-b8b6-f2985fec5cfb.bc23`, `Game un-gzipped!`,
`Applying events!`, `Running a game`. There were no CSP violations and no failed requests. The screenshot shows
match 13 (us:examplefuncsplayer, red, against Chahat08.toph, blue) at round 0 of 2000, on its map.

## 6. Limits

- **Profiler tab:** its iframe loads `out/speedscope/index.html`, which was not part of the download, so the tab
  stays empty. Replica replays are recorded with the profiler off (`-Dbc.engine.enable-profiler=false`), so there
  is nothing to show anyway.
- **Runner tab:** running games needs the desktop (Electron) client. The web build only plays files.
- **One replay holds every game of a match.** The Queue tab lists the games. Games 2, 4, ... have spawn sides
  swapped while the code keeps its A/B label (the match page lists which).
- Not tested: Safari and Firefox (only Chromium 154 was tested), and playback speed and memory on long replays on
  a phone.
