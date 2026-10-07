#!/usr/bin/env python3
"""Tests for the replica build of galaxy's frontend (tools/galaxy/frontend). No network, no node.
Run: python3 test/galaxy/test_frontend.py

1. replica.patch applies without fuzz to frontend/ of the pinned galaxy commit, and the patched tree names no
   battlecode.org backend, no Google Fonts and no releases.battlecode.org replay client;
2. check_bundle.py classifies synthetic bundles correctly (fetches fail, hyperlinks pass);
3. the built bundle, when one is present (GALAXY_FRONTEND_DIST, build/galaxy-frontend/..., or the installed copy),
   passes check_bundle.py and has no api.battlecode.org anywhere, source maps included.
The galaxy checkout defaults to ~/projects/vibe/reference/galaxy (GALAXY_SRC overrides); parts 1 and 3 skip when
their input is absent."""
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TOOL = os.path.join(REPO, 'tools', 'galaxy', 'frontend')
sys.path.insert(0, TOOL)
import check_bundle  # noqa: E402

PATCH = os.path.join(TOOL, 'replica.patch')
GALAXY_SRC = os.environ.get('GALAXY_SRC', os.path.expanduser('~/projects/vibe/reference/galaxy'))


def pinned_commit():
    with open(os.path.join(TOOL, 'build.sh')) as fh:
        return re.search(r'^GALAXY_COMMIT=([0-9a-f]{40})$', fh.read(), re.M).group(1)


def has_commit(commit):
    return os.path.isdir(GALAXY_SRC) and subprocess.run(
        ['git', '-C', GALAXY_SRC, 'cat-file', '-e', commit + '^{commit}'], capture_output=True).returncode == 0


def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


class PatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commit = pinned_commit()
        if not has_commit(cls.commit):
            raise unittest.SkipTest(f'no galaxy checkout with {cls.commit[:7]} at {GALAXY_SRC}')
        cls.tmp = tempfile.TemporaryDirectory(prefix='galaxy-fe-test-')
        archive = subprocess.run(['git', '-C', GALAXY_SRC, 'archive', cls.commit, 'frontend'],
                                 capture_output=True, check=True).stdout
        subprocess.run(['tar', '-x', '-C', cls.tmp.name], input=archive, check=True)
        with open(PATCH, 'rb') as fh:
            cls.patch = subprocess.run(['patch', '-d', cls.tmp.name, '-p1', '--forward', '--batch', '--fuzz=0',
                                        '--no-backup-if-mismatch'], stdin=fh, capture_output=True, text=True)
        cls.fe = os.path.join(cls.tmp.name, 'frontend')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_applies_cleanly(self):
        self.assertEqual(self.patch.returncode, 0, self.patch.stdout + self.patch.stderr)
        self.assertNotRegex(self.patch.stdout, r'(?i)fuzz|offset|reject')

    def test_environment(self):
        env = dict(line.split('=', 1) for line in read(os.path.join(self.fe, '.env.production')).splitlines()
                   if line and not line.startswith('#'))
        self.assertEqual(env['VITE_BACKEND_URL'], '')                 # same origin: /api/... on this site
        self.assertEqual(env['VITE_EMAIL_VERIFICATION_ENABLED'], 'false')
        self.assertNotIn('battlecode.org', read(os.path.join(self.fe, '.env.production')))
        self.assertIn('VITE_BACKEND_URL=""', read(os.path.join(TOOL, 'build.sh')))

    def test_sources(self):
        helpers = read(os.path.join(self.fe, 'src', 'api', 'helpers.ts'))
        self.assertNotIn('https://releases.battlecode.org', helpers)
        self.assertIn('`/viewer/visualizer.html${', helpers)
        self.assertIn('accessToken: () => Cookies.get("access")', helpers)   # stock JWT Bearer header
        self.assertIn('DEFAULT_EPISODE = "bc23"', read(os.path.join(self.fe, 'src', 'utils', 'constants.ts')))
        self.assertIn('@fontsource/inter/400.css', read(os.path.join(self.fe, 'src', 'index.css')))
        self.assertEqual(check_bundle.check_csp(read(os.path.join(self.fe, 'index.html'))), [])

    def test_no_third_party_loads_in_tree(self):
        hits = []
        for root, _dirs, files in os.walk(self.fe):
            if os.sep + 'node_modules' in root or os.sep + '_autogen' in root:
                continue
            for name in files:
                if name.endswith(('.ts', '.tsx', '.css', '.html', '.json', '.js', '.svg', '.txt')) or \
                        name.startswith('.env'):
                    text = read(os.path.join(root, name))
                    for bad in ('fonts.googleapis', 'fonts.gstatic', 'api.battlecode.org', 'googletagmanager',
                                'google-analytics', 'sentry'):
                        if bad in text and name != 'package-lock.json':
                            hits.append(f'{os.path.relpath(os.path.join(root, name), self.fe)}: {bad}')
        # .env.development is deleted by build.sh; it names only localhost and play.battlecode.org (unused variable)
        self.assertEqual(hits, [])

    def test_lockfile_matches_package_json(self):
        import json
        pkg = json.loads(read(os.path.join(self.fe, 'package.json')))
        lock = json.loads(read(os.path.join(self.fe, 'package-lock.json')))
        self.assertEqual(lock['packages']['']['dependencies'], pkg['dependencies'])
        for name in ('@fontsource/inter', '@fontsource/josefin-sans'):
            entry = lock['packages']['node_modules/' + name]
            self.assertEqual(entry['version'], pkg['dependencies'][name])
            self.assertTrue(entry['resolved'].startswith('https://registry.npmjs.org/'))
            self.assertTrue(entry['integrity'].startswith('sha512-'))


CSP = ('<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\'; '
       'style-src \'self\' \'unsafe-inline\'; img-src \'self\' data: blob:; font-src \'self\' data:; '
       'connect-src \'self\'; frame-src \'self\'; form-action \'self\'" />')


class CheckerTest(unittest.TestCase):
    def run_check(self, js, index=None):
        with tempfile.TemporaryDirectory() as d:
            os.mkdir(os.path.join(d, 'assets'))
            with open(os.path.join(d, 'index.html'), 'w') as fh:
                fh.write(index if index is not None else f'<html><head>{CSP}</head></html>')
            with open(os.path.join(d, 'assets', 'index-x.js'), 'w') as fh:
                fh.write(js)
            return check_bundle.check(d)

    def kinds(self, js):
        return [r[0] for r in self.run_check(js)[0]]

    def test_fetches_fail(self):
        for js in ('fetch("https://api.example.com/x")', 'e.src="https://cdn.example.com/a.png"',
                   'new WebSocket("wss://example.com/s")', 'const c=new Configuration({basePath:"https://x.org"})',
                   'window.open("https://example.com/")', 'x.open("GET","https://example.com/a")'):
            rows, bad, _ = self.run_check(js)
            self.assertEqual([r[0] for r in rows], ['FETCH'], js)
            self.assertTrue(bad, js)

    def test_battlecode_org(self):
        self.assertTrue(self.run_check('fetch("https://play.battlecode.org/api/x")')[1])
        self.assertTrue(self.run_check('const u="https://releases.battlecode.org/client/x"')[1])  # TEXT: refused
        self.assertTrue(self.run_check('const h="api."+"battlecode.org"')[1])                    # outside a URL
        self.assertTrue(self.run_check('/* https://api.battlecode.org in a comment */')[1])      # banned string
        rows, bad, _ = self.run_check('jsx(L,{to:`https://releases.battlecode.org/specs/${v}/specs.pdf`})'
                                      '+"see [our landing page](https://battlecode.org/)."')
        self.assertEqual(([r[0] for r in rows], bad), (['LINK', 'LINK'], []))

    def test_links_and_text_pass(self):
        js = ('createElement("a",{href:"https://github.com/x"});'
              'createElementNS("http://www.w3.org/2000/svg","svg");'
              'r={xmlns:"http://www.w3.org/2000/svg"};'
              'g.jsx(B,{onClick:()=>{window.open(`https://www.challonge.com/${e}`,"_blank")}});'
              'credits:{href:\'javascript:window.open("https://www.highcharts.com/?credits", "_blank")\'};'
              'g.jsx(kd,{url:"https://discord.gg/N86mxkH",className:s});'
              '"Read more at http://fb.me/use-check-prop-types"')
        rows, bad, _ = self.run_check(js)
        self.assertEqual(bad, [])
        self.assertEqual(sorted(r[0] for r in rows), ['LINK'] * 4 + ['TEXT'] * 3)

    def test_social_icon_rule_is_exact(self):
        self.assertEqual(self.kinds('g.jsx(kd,{url:"https://discord.gg/other"})'), ['FETCH'])
        self.assertEqual(self.kinds('g.jsx(Frame,{url:"https://example.com/"})'), ['FETCH'])

    def test_css_and_html(self):
        self.assertTrue(self.run_check('@import url("https://fonts.googleapis.com/css2?family=Inter");')[1])
        self.assertTrue(self.run_check('a{background:url(https://example.com/a.png)}')[1])
        self.assertTrue(self.run_check('', index='<html><head></head></html>')[1])           # no CSP
        loose = CSP.replace("connect-src 'self'", "connect-src 'self' https://api.battlecode.org")
        self.assertTrue(self.run_check('', index=f'<html><head>{loose}</head></html>')[1])
        ext = f'<html><head>{CSP}<script src="https://cdn.example.com/x.js"></script></head></html>'
        self.assertTrue(self.run_check('', index=ext)[1])


def built_dist():
    for d in (os.environ.get('GALAXY_FRONTEND_DIST', ''), os.path.join(REPO, 'build', 'galaxy-frontend', 'dist'),
              os.path.join(REPO, 'build', 'galaxy-frontend', 'src', 'frontend', 'build'),
              '/home/bcreplica/galaxy/frontend-dist'):
        if d and os.access(os.path.join(d, 'index.html'), os.R_OK):
            return d
    return None


class BuiltBundleTest(unittest.TestCase):
    def setUp(self):
        self.dist = built_dist()
        if self.dist is None:
            self.skipTest('no built bundle (run tools/galaxy/frontend/build.sh on the VM)')

    def test_bundle_check_passes(self):
        rows, bad, _maps = check_bundle.check(self.dist)
        self.assertEqual(bad, [])
        self.assertTrue(rows)                                   # the scan saw the bundle
        self.assertTrue(all(r[0] == 'LINK' for r in rows if r[1].endswith('battlecode.org')))

    def test_no_api_host_anywhere(self):
        for root, _dirs, files in os.walk(self.dist):
            for name in files:
                with open(os.path.join(root, name), 'rb') as fh:
                    data = fh.read()
                for bad in (b'api.battlecode.org', b'fonts.googleapis.com', b'fonts.gstatic.com'):
                    self.assertNotIn(bad, data, os.path.join(root, name))

    def test_replay_link_and_auth_header(self):
        js = ''.join(read(os.path.join(self.dist, 'assets', n)) for n in os.listdir(os.path.join(self.dist, 'assets'))
                     if n.endswith('.js'))
        self.assertTrue('/viewer/visualizer.html' in js, 'no /viewer/ replay link in the bundle')
        self.assertFalse('releases.battlecode.org/client' in js, 'official replay client link in the bundle')
        self.assertTrue('Bearer ' in js, 'no JWT Bearer header in the bundle')


if __name__ == '__main__':
    unittest.main(verbosity=1)
