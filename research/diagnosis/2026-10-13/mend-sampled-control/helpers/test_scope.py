#!/usr/bin/env python3
"""Synthetic admission regressions; no games, VM queries or original baseline writes."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_scope import assess


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.robot = dict(game=0, map='Cornucopia', side='A', package='c_mend2', robot=7, file=0,
                          type='LAUNCHER', profile='#7 (LAUNCHER)', frequency_exact=True, trace_valid=True,
                          entry_budget_aligned=True, team_capped=False, native_costs_usable=True, recorded_turns=20,
                          exception_status='zero_through_last_turn',
                          caller_context_status='zero_observed_ex_valid_native_nesting')
        self.file = dict(game=0, map='Cornucopia', map_seed=272, side='A', file=0, capped=False, open_events=100)
        def call(method, owner, parent, begin, end):
            row = {key: self.robot[key] for key in ('game', 'map', 'side', 'package', 'robot', 'file',
                                                   'exception_status', 'caller_context_status')}
            row.update(method=method, frame='c_mend2.' + owner + '.' + method,
                       caller_frame='c_mend2.' + parent, round=320, open_at=begin, close_at=end,
                       native_inclusive=end-begin, native_exclusive=end-begin, entry_budget=10000-begin,
                       return_budget=10000-end, cost_usable=True, terminal_close_ambiguous=False)
            return row
        self.mend = call('mendUpdate', 'Launcher', 'Launcher.run', 100, 500)
        self.mend.update(direct_reads_before_nearest=9, following_march_inclusive=700,
                         following_pick_objective_inclusive=200, launcher_tail_inclusive=1000)
        self.nearest = call('nearestEnemy', 'Comms', 'Launcher.mendUpdate', 350, 450)
        self.march = call('march', 'Launcher', 'Launcher.run', 600, 1300)
        self.pick = call('pickObjective', 'Launcher', 'Launcher.march', 650, 850)
        self.run = call('run', 'Launcher', 'RobotPlayer.run', 0, 1500)
        self.robots = [self.robot]
        self.files = [self.file]
        self.calls = [self.run, self.mend, self.nearest, self.march, self.pick]

    def result(self):
        return assess(self.robots, self.calls, self.files)

    def test_complete_actual_mend_target_and_tail_admits(self):
        result = self.result()
        self.assertTrue(result['ready'])
        self.assertEqual(result['same_turn_mend_tail_witnesses'], 1)
        self.assertEqual(result['samples'][0]['return_budget'], 9500)

    def test_other_side_caps_and_unrelated_carrier_exception_do_not_block(self):
        other = copy.deepcopy(self.file)
        other.update(side='B', file=1, capped=True, open_events=2000000)
        self.files.append(other)
        carrier = copy.deepcopy(self.robot)
        carrier.update(robot=8, type='CARRIER', exception_status='observed_exception', native_costs_usable=False)
        self.robots.append(carrier)
        self.assertTrue(self.result()['ready'])

    def test_own_team_cap_blocks_even_positive_interval_flags(self):
        self.file.update(capped=True, open_events=2000000)
        self.assertFalse(self.result()['ready'])
        self.file.update(capped=False)
        self.assertFalse(self.result()['ready'])

    def test_stale_zero_exception_and_invalid_context_block(self):
        for status in ('unobserved_tail', 'observed_exception', 'invalid_counter', 'missing_counter'):
            self.robot['exception_status'] = status
            self.assertFalse(self.result()['ready'])
        self.robot['exception_status'] = 'zero_through_last_turn'
        self.mend['caller_context_status'] = 'native_nesting_unverified'
        self.assertFalse(self.result()['ready'])

    def test_unknown_or_inconsistent_budget_alignment_blocks(self):
        saved = self.mend['return_budget']
        for returned in (None, 9501, -1):
            self.mend['return_budget'] = returned
            self.assertFalse(self.result()['ready'])
        self.mend['return_budget'] = saved
        self.robot['entry_budget_aligned'] = False
        self.assertFalse(self.result()['ready'])

    def test_no_actual_primary_scan_or_owned_target_blocks(self):
        self.mend['direct_reads_before_nearest'] = 0
        self.assertFalse(self.result()['ready'])
        self.mend['direct_reads_before_nearest'] = 9
        self.calls.remove(self.nearest)
        self.assertFalse(self.result()['ready'])

    def test_next_turn_or_unrelated_pick_does_not_prove_tail(self):
        self.pick['round'] = 321
        self.assertFalse(self.result()['ready'])
        self.pick['round'] = 320
        self.pick['caller_frame'] = 'c_mend2.Launcher.raidWell'
        self.assertFalse(self.result()['ready'])

    def test_wrong_map_seed_side_package_and_empty_scope_block(self):
        for field, value in (('map_seed', 273), ('side', 'B')):
            saved = self.file[field]
            self.file[field] = value
            self.assertFalse(self.result()['ready'])
            self.file[field] = saved
        self.robot['package'] = 'c_mend3'
        self.assertFalse(self.result()['ready'])
        self.robots = []
        self.assertFalse(self.result()['ready'])

    def test_tail_annotations_must_match_completed_sibling_methods(self):
        self.mend['following_pick_objective_inclusive'] += 1
        self.assertFalse(self.result()['ready'])
        self.mend['following_pick_objective_inclusive'] -= 1
        self.mend['launcher_tail_inclusive'] = 500
        self.assertFalse(self.result()['ready'])

    def test_enclosing_run_and_raw_counter_consistency_required(self):
        self.run['close_at'] += 1
        self.assertFalse(self.result()['ready'])
        self.run['close_at'] -= 1
        self.calls.remove(self.run)
        self.assertFalse(self.result()['ready'])

    def test_duplicate_own_robot_is_invalid(self):
        self.robots.append(copy.deepcopy(self.robot))
        with self.assertRaises(ValueError):
            self.result()

    def test_cli_writes_only_new_extraction_scope_and_exit_three_when_not_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            native = root / 'new-extraction'
            native.mkdir()
            for name, rows in (('robots', self.robots), ('intervals', self.calls), ('files', self.files)):
                (native / (name + '.jsonl')).write_text(''.join(json.dumps(row) + '\n' for row in rows))
            command = [sys.executable, str(Path(__file__).with_name('validate_scope.py')), str(native)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads((native / 'scope.json').read_text())['ready'])
            (native / 'intervals.jsonl').write_text('')
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertFalse(json.loads((native / 'scope.json').read_text())['ready'])


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ScopeTests)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print(json.dumps({'scope_selftest': 'passed' if result.wasSuccessful() else 'failed',
                      'tests': result.testsRun, 'games_run': 0}))
    raise SystemExit(0 if result.wasSuccessful() else 2)
