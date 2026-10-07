#!/usr/bin/env python3
"""Unit tests for the analysis and process tools (synthetic inputs; no games). Run by tools/unit-tests.sh."""
import importlib.util, os, subprocess, sys, tempfile, unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, TOOLS / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class FilterYearTest(unittest.TestCase):
    """The reading-room filter must drop every block tagged with the forbidden year and keep everything else."""

    def setUp(self):
        self.f = load('filter_year', 'filter_year.py')

    def test_drops_tagged_bullet_with_continuation(self):
        md = "# T\n\n- keep me [2024 X]\n- drop me [2023 Y] first line\n  continuation of the dropped bullet\n- keep too\n"
        out = self.f.filt(md)
        self.assertIn('keep me', out)
        self.assertIn('keep too', out)
        self.assertNotIn('drop me', out)
        self.assertNotIn('continuation of the dropped', out)

    def test_drops_whole_section_under_tagged_heading(self):
        md = "# A\n\n### 3c. Something [2023 Team]\n\ntext in section\n\n```\ncode\n```\n\n### 3d. Other\n\nkept\n"
        out = self.f.filt(md)
        self.assertNotIn('text in section', out)
        self.assertNotIn('code', out)
        self.assertIn('kept', out)
        self.assertIn('3d. Other', out)

    def test_drops_code_block_introduced_by_dropped_colon_line(self):
        md = "para one\n\nLayout used (1024 bits) [2023 Z]:\n\n```\nsecret layout\n```\n\nafter\n"
        out = self.f.filt(md)
        self.assertNotIn('secret layout', out)
        self.assertIn('after', out)
        self.assertIn('para one', out)

    def test_nested_child_of_tagged_parent_dropped(self):
        md = "- parent [2014, 2023, 2025 Q]\n  - child a\n  - child b\n- sibling\n"
        out = self.f.filt(md)
        self.assertNotIn('child a', out)
        self.assertIn('sibling', out)

    def test_team_and_unit_names_without_year_are_dropped(self):
        md = "- kite like Gone Fishin' did\n- carriers throw cargo at the launcher\n- generic advice\n"
        out = self.f.filt(md)
        self.assertEqual(out.strip(), '- generic advice')

    def test_untagged_text_unchanged(self):
        md = "# Title\n\nPlain paragraph.\n\n- a\n- b\n"
        self.assertEqual(self.f.filt(md).strip(), md.strip())


class ParseResultTest(unittest.TestCase):
    """tools/lib.sh parse_result reads the engine's end-of-match lines."""

    def run_parse(self, text):
        cmd = f'source "{TOOLS}/lib.sh"; parse_result "$(cat)"'
        return subprocess.run(['bash', '-c', cmd], input=text, capture_output=True, text=True).stdout.strip()

    def test_win_line(self):
        log = ("[server] -------------------- Match Starting --------------------\n"
               "[server] a vs. b on maptestsmall\n"
               "[server]               a (A) wins (round 2000)\n"
               "[server] Reason: The winning team won on tiebreakers (more mana net worth).\n")
        self.assertEqual(self.run_parse(log), 'RESULT A 2000 The winning team won on tiebreakers (more mana net worth).')

    def test_b_wins_early(self):
        log = "[server]   x (B) wins (round 734)\n[server] Reason: The winning team won by anchoring sky islands.\n"
        self.assertEqual(self.run_parse(log), 'RESULT B 734 The winning team won by anchoring sky islands.')

    def test_garbage(self):
        self.assertEqual(self.run_parse('java.lang.OutOfMemoryError\n'), 'RESULT ? ? ?')


class BenchSelectTest(unittest.TestCase):
    """Name-only choice of a repo's final bot."""

    def setUp(self):
        self.s = load('bench_select', 'bench-select.py')

    def test_final_beats_versions(self):
        self.assertGreater(self.s.score('finalbot'), self.s.score('v12'))
        self.assertGreater(self.s.score('qualsbot'), self.s.score('sprint2'))
        self.assertGreater(self.s.score('v9'), self.s.score('v3'))

    def test_junk_pattern(self):
        for junk in ('examplefuncsplayer', 'testbot', 'donothing', 'template'):
            self.assertTrue(self.s.JUNK.search(junk), junk)
        self.assertFalse(self.s.JUNK.search('launcherbot'))


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=0).result
    print(f"test_tools: {r.testsRun} tests, {len(r.failures)} failures, {len(r.errors)} errors")
    sys.exit(0 if r.wasSuccessful() else 1)
