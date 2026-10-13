#!/usr/bin/env python3
"""Parser rejection tests on synthetic records; executes no engine, bot, Clock or game."""
from copy import deepcopy
import unittest
from summarize import arm_summary, zero_gate


def fixture(name='base', hook_rounds=()):
    turns = []
    bs = 0
    for r in range(2, 33):
        attacks = []
        if r in hook_rounds or 18 <= r <= 21:
            blind = r in hook_rounds
            if blind:
                bs += 1
            attacks = [{'round': r, 'shooter_at': [6, 6], 'target': [9, 6] if blind else [8, 6],
                        'target_team': 'B', 'hidden_at_attack': blind, 'native_can_attack': True,
                        'pre_cd': 0, 'actual_rounded_cost': 10, 'post_cd': 10, 'native_damage': 20,
                        'blind_caller': blind, 'bytecodes_left': 5000, 'target_id': 20000}]
        counters = {'blindShots': bs, 'overruns': 0, 'exceptions': 0, 'maxBc': 2000, 'rng': 42}
        turn = {'round': r, 'start_cd': 0, 'end_cd': 10 if attacks else 0,
                'whole_turn_bytecodes': 8899, 'native_bytecode_limit': 10000, 'attacks': attacks,
                'api_calls': [], 'indicator': 'La0|ov=0,ex=0' + (',bs=' + str(bs) if bs else ''),
                'memory': {'MapMem.pendingIdx': 0}, 'counters': counters, 'sandbox_paused': True}
        if r < 32:
            turn['next_actual_own_start_cd'] = 0
        turns.append(turn)
    return {'arm': name, 'pass': True, 'rounds': 32, 'geometry_sha256': 'fixture',
            'native_states': [{'round': r, 'robots': [{'bytecodes': 0 if r == 1 else 8899}]} for r in range(1, 33)],
            'script_events': [], 'turns': turns, 'first_turn_initialization_included': True,
            'clock_or_owned_memory_modified': False}


class SummaryTest(unittest.TestCase):
    def test_live_zero_pair(self):
        result = zero_gate(fixture(), fixture('0'))
        self.assertTrue(result['native_state_and_bytecode_identity'])
        self.assertFalse(result['scored_game_identity_claimed'])

    def test_native_state_and_missing_round_rejected(self):
        for mutate in ('bytecodes', 'round'):
            record = fixture('0')
            if mutate == 'bytecodes':
                record['native_states'][-1]['robots'][0]['bytecodes'] += 1
            else:
                record['native_states'].pop()
            with self.assertRaises(ValueError):
                zero_gate(fixture(), record)

    def test_source_api_and_rng_differences_rejected(self):
        for key in ('api_calls', 'rng'):
            record = fixture('0')
            if key == 'api_calls':
                record['turns'][0]['api_calls'].append({'method': 'getLocation'})
            else:
                record['turns'][0]['counters']['rng'] += 1
            with self.assertRaises(ValueError):
                zero_gate(fixture(), record)

    def test_real_next_start_and_terminal_censoring(self):
        record = fixture('1', (2, 32))
        summary = arm_summary(record, fixture())
        self.assertEqual(summary['observed_actual_next_start_zero'], 1)
        self.assertEqual(summary['right_censored_final_next_start'], 1)
        self.assertEqual(summary['native_hidden_damage'], 40)
        record['turns'][0]['next_actual_own_start_cd'] = 1
        with self.assertRaises(ValueError):
            arm_summary(record, fixture())

    def test_counter_and_indicator_join_rejected(self):
        for mutation in ('counter', 'token', 'gap'):
            record = fixture('1', (2,))
            if mutation == 'counter':
                record['turns'][0]['counters']['blindShots'] = 0
            elif mutation == 'token':
                record['turns'][0]['indicator'] = 'La0|ov=0,ex=0,bs=2'
            else:
                record['turns'][0]['indicator'] = 'La0|ov=0,ex=0'
            with self.assertRaises(ValueError):
                arm_summary(record, fixture())

    def test_ordinary_attack_displacement_rejected(self):
        record = fixture('1', (2,))
        record['turns'][16]['attacks'][0]['native_damage'] = 0
        with self.assertRaises(ValueError):
            arm_summary(record, fixture())

    def test_native_policy_and_basics_rejected(self):
        for mutation in ('hidden', 'debt', 'ally', 'exhaustion', 'exception', 'override'):
            record = fixture('1', (2,))
            turn = record['turns'][0]
            if mutation == 'hidden':
                turn['attacks'][0]['hidden_at_attack'] = False
            elif mutation == 'debt':
                turn['attacks'][0]['pre_cd'] = 1
            elif mutation == 'ally':
                turn['attacks'][0]['target_team'] = 'A'
            elif mutation == 'exhaustion':
                turn['whole_turn_bytecodes'] = 10000
            elif mutation == 'exception':
                turn['counters']['exceptions'] = 1
            else:
                record['clock_or_owned_memory_modified'] = True
            with self.assertRaises(ValueError):
                arm_summary(record, fixture())


if __name__ == '__main__':
    unittest.main()
