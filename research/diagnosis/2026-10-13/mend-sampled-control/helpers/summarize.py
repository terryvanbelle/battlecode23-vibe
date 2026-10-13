#!/usr/bin/env python3
"""Summarize Mend3 native counters and normal replay telemetry; never runs games."""
import argparse
import collections
import contextlib
import csv
import hashlib
import io
import json
import math
import re
import tempfile
import unittest
from pathlib import Path

METHODS = ('run', 'mendUpdate', 'march', 'fight', 'mendScore', 'pickObjective',
           'shoot', 'nearestEnemy', 'read')
OPEN_CAP = 2000000
MEND_RESERVE = 6000
METRICS = ('rounds', 'won', 'healed', 'died_L', 'island_rounds', 'over', 'near',
           'exceptions', 'deaths_self', 'tele_exc_turns', 'bc_max_L', 'sym_wrong')


def rows(path):
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def csv_rows(path):
    if not path.is_file():
        return []
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def integer(value):
    if isinstance(value, bool):
        return None
    try:
        if isinstance(value, float) and not value.is_integer():
            return None
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return None


def stats(values):
    values = sorted(value for value in values if value is not None)
    if not values:
        return dict(n=0, sum=0, mean=None, min=None, p50=None, p90=None, p99=None, max=None)
    return {'n': len(values), 'sum': sum(values), 'mean': sum(values) / len(values),
            'min': values[0], 'p50': values[math.ceil(.50 * len(values)) - 1],
            'p90': values[math.ceil(.90 * len(values)) - 1],
            'p99': values[math.ceil(.99 * len(values)) - 1], 'max': values[-1]}


def budget_bucket(value):
    if value is None:
        return 'unknown'
    for threshold, label in ((6000, '<6000'), (7500, '6000..7499'), (9000, '7500..8999'),
                             (10000, '9000..9999')):
        if value < threshold:
            return label
    return '>=10000'


def group_key(row):
    return tuple(row[key] for key in ('game', 'map', 'side', 'package'))


def robot_key(row):
    return group_key(row) + (row['robot'],)


def context_clear(row):
    return (row.get('exception_status') == 'zero_through_last_turn'
            and row.get('caller_context_status') == 'zero_observed_ex_valid_native_nesting')


def coverage_ok(robot, file_info):
    return (context_clear(robot) and robot.get('frequency_exact') is True and robot.get('trace_valid') is True
            and robot.get('entry_budget_aligned') is True and robot.get('team_capped') is False
            and file_info is not None and file_info.get('capped') is False
            and integer(file_info.get('open_events')) is not None
            and 0 <= integer(file_info['open_events']) < OPEN_CAP
            and robot.get('profile') is not None)


def usable(call, robot, file_info):
    return (coverage_ok(robot, file_info) and robot.get('native_costs_usable') is True
            and context_clear(call)
            and call.get('cost_usable') is True and call.get('terminal_close_ambiguous') is False
            and integer(call.get('native_inclusive')) is not None
            and integer(call['native_inclusive']) >= 0
            and integer(call.get('native_exclusive')) is not None
            and 0 <= integer(call['native_exclusive']) <= integer(call['native_inclusive']))


def load_telemetry(directory):
    out = {'directory': None if directory is None else str(directory), 'events_available': False,
           'games': {}, 'events': collections.defaultdict(list), 'census': {}, 'issues': []}
    if directory is None:
        return out
    for row in csv_rows(directory / 'games.csv'):
        game = integer(row.get('game'))
        key = (game, row.get('map'), row.get('side'))
        if game is None or key in out['games']:
            out['issues'].append('missing_game_or_duplicate_games_row')
            out['games'][key] = None
        else:
            out['games'][key] = row
    path = directory / 'tele_events.jsonl'
    out['events_available'] = path.is_file()
    if path.is_file():
        for event in rows(path):
            key = (integer(event.get('game')), event.get('side'), integer(event.get('id')),
                   integer(event.get('round')))
            out['events'][key].append(event)
    for row in csv_rows(directory / 'census.csv'):
        key = (integer(row.get('game')), row.get('map'), row.get('side'))
        if key in out['census']:
            out['issues'].append('duplicate_census_row')
            out['census'][key] = None
        else:
            out['census'][key] = row
    return out


def target_witness(call, telemetry):
    """Positive-only evidence. Never infer rejection from a missing/suppressed OBJ."""
    round_number = integer(call.get('round'))
    if round_number is None:
        return {'status': 'unknown', 'reason': 'native_round_unknown'}
    if (integer(call.get('following_march_inclusive')) is None
            or integer(call['following_march_inclusive']) <= 0):
        return {'status': 'unknown', 'reason': 'no_usable_following_march'}
    if not telemetry['events_available']:
        return {'status': 'unknown', 'reason': 'dots_unavailable'}
    meta = telemetry['games'].get((call['game'], call['map'], call['side']))
    width = integer(meta.get('width')) if meta else None
    height = integer(meta.get('height')) if meta else None
    if width is None or height is None or not 1 <= width <= 64 or not 1 <= height <= 64:
        return {'status': 'unknown', 'reason': 'map_dimensions_unavailable'}
    key = (call['game'], call['side'], call['robot'], round_number)
    objectives = [event for event in telemetry['events'].get(key, [])
                  if event.get('kind') == 'OBJ' and event.get('type') == 'L']
    if len(objectives) != 1:
        return {'status': 'unknown', 'reason': 'fresh_obj_missing' if not objectives else 'multiple_obj_records'}
    event = objectives[0]
    if integer(event.get('r0')) != round_number or integer(event.get('obj_kind')) != 3:
        return {'status': 'unknown', 'reason': 'obj_not_current_mending_kind'}
    objective = event.get('objective')
    if not isinstance(objective, list) or len(objective) != 2:
        return {'status': 'unknown', 'reason': 'objective_unavailable'}
    x, y = (integer(value) for value in objective)
    if x is None or y is None or not 0 <= x < width or not 0 <= y < height:
        return {'status': 'unknown', 'reason': 'objective_out_of_bounds'}
    if [x, y] == [width // 2, height // 2]:
        return {'status': 'unknown', 'reason': 'centre_objective_ambiguous'}
    return {'status': 'positive', 'reason': 'same_turn_noncentre_kind3_obj',
            'objective': [x, y], 'selected_mend_island': None}


def counters(raw):
    result = {}
    for item in (raw or '').strip(';').split(';'):
        name, sep, value = item.partition('=')
        number = integer(value)
        if sep and number is not None:
            result[name] = number
    return result


def same_turn_events(call, telemetry):
    round_number = integer(call.get('round'))
    if round_number is None:
        return []
    return [event for event in telemetry['events'].get((call['game'], call['side'], call['robot'], round_number), [])
            if event.get('type') == 'L' and event.get('kind') in ('OBJ', 'NM', 'OVR', 'FIGHT', 'CNT', 'CNTT')]


def descriptive_telemetry(key, telemetry):
    game, map_name, side, package = key
    row = telemetry['census'].get((game, map_name, side))
    events = [event for event_key, selected in telemetry['events'].items()
              if event_key[:2] == (game, side) for event in selected if event.get('type') == 'L']
    launcher_context = {
        'event_scope': 'LAUNCHER',
        'nm_work_bytecodes': stats(event.get('work') for event in events if event.get('kind') == 'NM'),
        'nm_t1_bytecodes': stats(event.get('t1') for event in events if event.get('kind') == 'NM'),
        'ovr_phases': dict(sorted(collections.Counter(str(event.get('phase', 'unknown')) for event in events
                                                     if event.get('kind') == 'OVR').items())),
        'fight_events': sum(event.get('kind') == 'FIGHT' for event in events),
        'fight_guard_breaks': sum(event.get('guard_break') == 1 for event in events if event.get('kind') == 'FIGHT'),
        'fight_scored_tiles': stats(event.get('tiles') for event in events if event.get('kind') == 'FIGHT'),
        'event_counts': dict(sorted(collections.Counter(event.get('kind', 'unknown') for event in events).items())),
    }
    if row is None:
        return {'census_available': False, 'metrics': {name: None for name in METRICS},
                'caught_exceptions_counter': None, 'prefill_near_misses_counter': None,
                **launcher_context}
    own_counters = counters(row.get('counters'))
    return {'census_available': True, 'team': row.get('team'), 'package_from_native': package,
            'telemetry_status': row.get('tele'), 'metrics': {name: integer(row.get(name)) for name in METRICS},
            'caught_exceptions_counter': own_counters.get('ex'),
            'prefill_near_misses_counter': own_counters.get('nm'),
            **launcher_context}


def summary(extract, telemetry_directory=None):
    robots, intervals, files = (rows(extract / name) for name in ('robots.jsonl', 'intervals.jsonl', 'files.jsonl'))
    telemetry = load_telemetry(telemetry_directory)
    file_index = {(row.get('game'), row.get('file')): row for row in files}
    robot_index = {}
    groups = collections.defaultdict(lambda: {'robots': [], 'calls': []})
    for robot in robots:
        if robot['type'] == 'LAUNCHER':
            key = robot_key(robot)
            if key in robot_index:
                raise ValueError('duplicate native launcher robot')
            robot_index[key] = robot
            groups[group_key(robot)]['robots'].append(robot)
    orphan_intervals = 0
    for call in intervals:
        if robot_key(call) not in robot_index:
            orphan_intervals += 1
        else:
            groups[group_key(call)]['calls'].append(call)
    summaries = []
    for key, data in sorted(groups.items()):
        bots, calls = data['robots'], data['calls']
        recorded_turns = sum(robot['recorded_turns'] for robot in bots)
        full_coverage = (all(coverage_ok(robot, file_index.get((robot['game'], robot.get('file')))) for robot in bots)
                         and all(context_clear(call) for call in calls))
        frequency_exact = full_coverage
        def cost_ok(call):
            return usable(call, robot_index[robot_key(call)], file_index.get((call['game'], call.get('file'))))
        methods = {}
        for method in METHODS:
            entries = sum(robot['selected_entries'].get(method, 0) for robot in bots)
            selected = [call for call in calls if call['method'] == method]
            accepted = [call for call in selected if cost_ok(call)]
            caller_groups = collections.defaultdict(list)
            for call in accepted:
                caller_groups[call.get('caller_frame')].append(call)
            methods[method] = {
                'observed_entries': entries, 'entry_frequency_exact': frequency_exact,
                'entries_per_1000_recorded_launcher_turns': 1000 * entries / recorded_turns if recorded_turns else None,
                'frequency_is_lower_bound': not frequency_exact,
                'usable_completed_intervals': len(accepted), 'entries_without_usable_cost': entries - len(accepted),
                'terminal_close_ambiguous_intervals': sum(call.get('terminal_close_ambiguous') is True for call in selected),
                'native_inclusive_bytecodes': stats(call['native_inclusive'] for call in accepted),
                'native_exclusive_bytecodes': stats(call['native_exclusive'] for call in accepted),
                'completed_entry_budget_histogram': dict(sorted(collections.Counter(budget_bucket(call.get('entry_budget')) for call in accepted).items())),
                'completed_return_budget_histogram': dict(sorted(collections.Counter(budget_bucket(call.get('return_budget')) for call in accepted).items())),
                'caller_contexts': {caller: {'completed_intervals': len(selected_calls),
                                           'native_inclusive_bytecodes': stats(call['native_inclusive'] for call in selected_calls)}
                                    for caller, selected_calls in sorted(caller_groups.items(), key=lambda item: item[0] or '')},
            }
        mend = [call for call in calls if call['method'] == 'mendUpdate']
        usable_mend = [call for call in mend if cost_ok(call)]
        observed_fallback = [call for call in mend if call.get('fallback_witness') is True
                             and integer(call.get('direct_reads_after_nearest')) is not None
                             and call['direct_reads_after_nearest'] > 0]
        fallback = [call for call in observed_fallback if cost_ok(call)]
        classifications = [(call, target_witness(call, telemetry)) for call in fallback]
        reason_counts = collections.Counter(result['reason'] for _, result in classifications)
        classification_exact = (full_coverage and len(usable_mend) == methods['mendUpdate']['observed_entries']
                                and all(isinstance(call.get('fallback_witness'), bool) for call in usable_mend))
        fields = ('native_inclusive', 'native_exclusive', 'entry_budget', 'return_budget',
                  'following_march_inclusive', 'following_pick_objective_inclusive', 'launcher_tail_inclusive')
        summaries.append({
            'game': key[0], 'map': key[1], 'side': key[2], 'package': key[3],
            'launcher_robots': len(bots), 'recorded_launcher_turns': recorded_turns,
            'robots_with_profile': sum(robot.get('profile') is not None for robot in bots),
            'robots_with_complete_valid_trace': sum(coverage_ok(robot, file_index.get((robot['game'], robot.get('file')))) for robot in bots),
            'robots_with_entry_budget_alignment': sum(robot.get('entry_budget_aligned') is True for robot in bots),
            'robots_with_observed_exception_counter': sum(integer(robot.get('exception_max')) is not None
                                                        and integer(robot['exception_max']) >= 0 for robot in bots),
            'robots_with_zero_recorded_exceptions': sum(robot.get('exception_status') == 'zero_through_last_turn' for robot in bots),
            'exception_status_counts': dict(sorted(collections.Counter(robot.get('exception_status', 'missing_status') for robot in bots).items())),
            'caller_context_status_counts': dict(sorted(collections.Counter(robot.get('caller_context_status', 'missing_status') for robot in bots).items())),
            'interval_exception_status_counts': dict(sorted(collections.Counter(call.get('exception_status', 'missing_status') for call in calls).items())),
            'interval_caller_context_status_counts': dict(sorted(collections.Counter(call.get('caller_context_status', 'missing_status') for call in calls).items())),
            'full_launcher_coverage': full_coverage,
            'capped_profile_files': sorted({robot['file'] for robot in bots if robot.get('team_capped') is True}),
            'trace_issues': dict(sorted(collections.Counter(issue for robot in bots for issue in robot.get('issues', [])).items())),
            'robot_replay_context': {
                'lifetime_recorded_healed_hp': stats(robot.get('recorded_healed_hp') for robot in bots),
                'robots_with_death_context': sum('replay_death_round' in robot for robot in bots),
                'robots_with_recorded_death': sum(robot.get('replay_death_round') is not None for robot in bots),
                'recorded_death_rounds': stats(robot.get('replay_death_round') for robot in bots),
            },
            'methods': methods,
            'fallback': {
                'definition': 'Immediate-child Comms.read after nearestEnemy CLOSE in the same mendUpdate; this witnesses entry, not every latent opportunity.',
                'observed_witnesses': len(observed_fallback), 'usable_witnesses': len(fallback),
                'classification_exact_for_recorded_turns': classification_exact,
                'frequency_is_lower_bound': not classification_exact,
                'usable_witnesses_per_1000_recorded_launcher_turns': 1000 * len(fallback) / recorded_turns if recorded_turns else None,
                'costs': {field: stats(call.get(field) for call in fallback) for field in fields},
                'return_below_6000': sum(call.get('return_budget') is not None and call['return_budget'] < MEND_RESERVE for call in fallback),
                'return_budget_unknown': sum(call.get('return_budget') is None for call in fallback),
                'successful_target_witnesses': sum(result['status'] == 'positive' for _, result in classifications),
                'target_success_unknown': sum(result['status'] == 'unknown' for _, result in classifications),
                'target_witness_reasons': dict(sorted(reason_counts.items())),
                'selected_mend_island': None,
                'replay_context': {
                    'window': 'Current fallback-call round through r0+10 inclusive; repeated windows may overlap.',
                    'recorded_healed_hp_in_window': stats(call.get('replay_healed_hp_next_10_rounds') for call in fallback),
                    'calls_with_death_context': sum('replay_death_round' in call for call in fallback),
                    'calls_for_robot_with_recorded_death': sum(call.get('replay_death_round') is not None for call in fallback),
                    'recorded_death_rounds': stats(call.get('replay_death_round') for call in fallback),
                },
                'samples': [{name: call.get(name) for name in ('robot', 'round', 'entry_budget', 'return_budget',
                             'direct_reads_after_nearest', 'following_march_inclusive', 'following_pick_objective_inclusive',
                             'launcher_tail_inclusive', 'replay_healed_hp_next_10_rounds', 'replay_death_round')} | {
                             'replay_death_context_available': 'replay_death_round' in call, 'target_witness': result,
                             'same_turn_launcher_events': same_turn_events(call, telemetry)}
                            for call, result in classifications[:10]],
            },
            'descriptive_telemetry': descriptive_telemetry(key, telemetry),
        })
    return {'schema_version': 1, 'profile_files': files, 'launcher_summaries': summaries,
            'orphan_intervals': orphan_intervals,
            'telemetry': {'directory': telemetry['directory'], 'events_available': telemetry['events_available'],
                          'issues': telemetry['issues']},
            'limits': [
                'Costs require parser cost_usable, complete valid uncapped coverage and entry-budget alignment, plus exception_status zero_through_last_turn and caller_context_status zero_observed_ex_valid_native_nesting on robot and interval.',
                'Cumulative ex must remain zero through the final recorded turn. Observed exceptions, DIE_EXCEPTION, regressing or missing counters, and stale zero samples with an unobserved tail suppress costs, callers, budgets and exact-frequency claims even if native nesting appears balanced.',
                'The cumulative ex counter covers unit/end-turn exceptions handled by these frozen bots, not proof that every internally caught exception was counted. Caller context describes validated native nesting, not source lines.',
                'Native costs exclude caller argument/invocation setup. Exclusive costs subtract nested profiled methods; API and filtered library charges remain.',
                'Identity comparison is a separate gate: require exact state and bytecode fingerprints plus terminal footer identity for each measured cell.',
                'Caps, missing profiles, invalid traces and unclassified entries produce lower bounds, not zero opportunities.',
                'Fallback witnesses show entered fallback, not all blocked-nearest/wounded opportunities or an alternative target existing.',
                'Only a fresh same-turn non-centre OBJ kind 3 after a usable following march is a positive target-selection witness in these frozen sources.',
                'OBJ is change-suppressed and kind 3 includes map centre. Missing/ambiguous OBJ is unknown; OBJ kind 3 does not store selected mendIsland.',
                'Counter NM measures work before fill; census near and turn bytecodes include deliberate fill and cannot measure method savings.',
                'Event distributions cover Launcher records only; census metrics and ex/nm counters remain team-wide descriptive aggregates.',
                'Healed is team-wide positive health delta, not HP caused specifically by fallback. These cells supply descriptive workload evidence, not a promotion verdict.',
                'Per-robot recorded_healed_hp is lifetime public-action healing. Fallback healing windows include the call round through r0+10, may overlap, and do not attribute healing to fallback.',
                'A present replay_death_round field containing null means no death recorded during this match; it says nothing about survival after the match. An absent field leaves death context unavailable.',
                'Native and telemetry directories must come from the same replay; the runner records their replay provenance. This reader cannot establish cross-directory replay identity.',
            ]}


def sha(path):
    with path.open('rb') as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def compare(pair):
    fingerprints = {mode: (pair / (mode + '.fingerprint')).read_text().strip() for mode in ('off', 'on')}
    footers = {mode: (pair / (mode + '.games')).read_text().strip() for mode in ('off', 'on')}
    def terminal_shape(fingerprint, footer):
        if len(fingerprint.splitlines()) != 1 or len(footer.splitlines()) != 1:
            return False
        f, g = fingerprint.split(), footer.split()
        return (len(f) == 5 and len(g) == 4 and f[0] == g[0] == '0' and f[1] == g[1]
                and f[2].isdigit() and int(f[2]) > 0 and f[2] == g[3] and g[2] in ('A', 'B', '-')
                and all(re.fullmatch('[0-9a-f]{40}', value) for value in f[3:]))
    valid = all(terminal_shape(fingerprints[mode], footers[mode]) for mode in ('off', 'on'))
    result = {'fingerprint_identity': valid and fingerprints['off'] == fingerprints['on'],
              'footer_result_identity': valid and footers['off'] == footers['on'],
              'off_fingerprint': fingerprints['off'], 'on_fingerprint': fingerprints['on'],
              'off_result': footers['off'], 'on_result': footers['on'], 'terminal_metadata_valid': valid,
              'off_replay_sha256': sha(pair / 'off.bc23'), 'on_replay_sha256': sha(pair / 'on.bc23')}
    result['measurement_identity_pass'] = result['fingerprint_identity'] and result['footer_result_identity']
    (pair / 'identity.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'pair': pair.name, **result}, sort_keys=True))
    return result['measurement_identity_pass']


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.extract = self.root / 'native'
        self.telemetry = self.root / 'telemetry'
        self.extract.mkdir()
        self.telemetry.mkdir()
        self.robot = {'game': 0, 'map': 'fixture', 'side': 'A', 'package': 'c_mend3', 'robot': 1,
                      'type': 'LAUNCHER', 'recorded_turns': 10, 'profile': '#1 (LAUNCHER)',
                      'frequency_exact': True, 'trace_valid': True, 'entry_budget_aligned': True,
                      'native_costs_usable': True, 'file': 0, 'team_capped': False, 'issues': [],
                      'exception_status': 'zero_through_last_turn', 'exception_max': 0,
                      'caller_context_status': 'zero_observed_ex_valid_native_nesting',
                      'selected_entries': {method: int(method == 'mendUpdate') for method in METHODS}}
        self.call = {key: self.robot[key] for key in ('game', 'map', 'side', 'package', 'robot', 'file',
                                                    'exception_status', 'caller_context_status')}
        self.call.update(method='mendUpdate', cost_usable=True, terminal_close_ambiguous=False,
                         native_inclusive=4088, native_exclusive=4000, entry_budget=10000, return_budget=5912,
                         caller_frame='c_mend3.Launcher.run', round=320, fallback_witness=True,
                         direct_reads_after_nearest=21, following_march_inclusive=1500,
                         following_pick_objective_inclusive=600, launcher_tail_inclusive=1800)
        self.file = {'game': 0, 'file': 0, 'side': 'A', 'open_events': 100, 'capped': False}
        self.event = dict(game=0, round=320, r0=320, id=1, side='A', type='L', kind='OBJ',
                          obj_kind=3, objective=[10, 11], island=0)
        (self.telemetry / 'games.csv').write_text('game,map,side,width,height\n0,fixture,A,60,60\n')
        (self.telemetry / 'census.csv').write_text('game,map,side,team,healed,over,near,counters\n0,fixture,A,c_mend3,120,0,4,ex=0;nm=1\n')

    def evaluate(self, events=True):
        for name, values in (('robots', [self.robot]), ('intervals', [self.call]), ('files', [self.file])):
            (self.extract / (name + '.jsonl')).write_text(''.join(json.dumps(row) + '\n' for row in values))
        if events:
            (self.telemetry / 'tele_events.jsonl').write_text(json.dumps(self.event) + '\n')
        return summary(self.extract, self.telemetry)['launcher_summaries'][0]

    def test_positive_and_reserve_overshoot(self):
        row = self.evaluate()
        self.assertEqual(row['fallback']['successful_target_witnesses'], 1)
        self.assertEqual(row['fallback']['return_below_6000'], 1)
        self.assertEqual(row['fallback']['costs']['return_budget']['min'], 5912)
        self.assertIsNone(row['fallback']['selected_mend_island'])
        self.assertEqual(row['descriptive_telemetry']['metrics']['healed'], 120)
        self.assertEqual(row['descriptive_telemetry']['prefill_near_misses_counter'], 1)

    def test_optional_replay_health_context_and_missing_fields(self):
        row = self.evaluate()
        self.assertEqual(row['fallback']['replay_context']['recorded_healed_hp_in_window']['n'], 0)
        self.assertEqual(row['fallback']['replay_context']['calls_with_death_context'], 0)
        self.assertFalse(row['fallback']['samples'][0]['replay_death_context_available'])
        self.robot.update(recorded_healed_hp=120, replay_death_round=500)
        self.call.update(replay_healed_hp_next_10_rounds=40, replay_death_round=500)
        row = self.evaluate()
        self.assertEqual(row['robot_replay_context']['lifetime_recorded_healed_hp']['sum'], 120)
        self.assertEqual(row['fallback']['replay_context']['recorded_healed_hp_in_window']['sum'], 40)
        self.assertEqual(row['fallback']['samples'][0]['replay_death_round'], 500)
        self.call['replay_death_round'] = None
        row = self.evaluate()['fallback']
        self.assertEqual(row['replay_context']['calls_with_death_context'], 1)
        self.assertEqual(row['replay_context']['calls_for_robot_with_recorded_death'], 0)
        self.assertTrue(row['samples'][0]['replay_death_context_available'])

    def test_zero_fallback_is_not_zero_latent_opportunity(self):
        self.call.update(fallback_witness=False, direct_reads_after_nearest=0)
        row = self.evaluate()['fallback']
        self.assertEqual(row['observed_witnesses'], 0)
        self.assertTrue(row['classification_exact_for_recorded_turns'])
        self.assertEqual(row['costs']['native_inclusive']['n'], 0)

    def test_missing_dots_unknown_success(self):
        row = self.evaluate(events=False)['fallback']
        self.assertEqual(row['usable_witnesses'], 1)
        self.assertEqual(row['successful_target_witnesses'], 0)
        self.assertEqual(row['target_witness_reasons'], {'dots_unavailable': 1})

    def test_exact_cap_suppresses_costs_and_success(self):
        self.file['open_events'] = OPEN_CAP
        row = self.evaluate()
        self.assertEqual(row['fallback']['observed_witnesses'], 1)
        self.assertEqual(row['fallback']['usable_witnesses'], 0)
        self.assertTrue(row['fallback']['frequency_is_lower_bound'])
        self.assertFalse(row['full_launcher_coverage'])

    def test_alignment_failure_suppresses_even_flagged_cost(self):
        self.robot['entry_budget_aligned'] = False
        row = self.evaluate()
        self.assertEqual(row['methods']['mendUpdate']['native_inclusive_bytecodes']['n'], 0)
        self.assertEqual(row['fallback']['successful_target_witnesses'], 0)
        self.assertTrue(row['methods']['mendUpdate']['frequency_is_lower_bound'])
        self.assertEqual(row['robots_with_complete_valid_trace'], 0)

    def test_launcher_context_excludes_carriers(self):
        self.evaluate()
        events = [self.event,
                  dict(game=0, side='A', id=1, round=320, type='L', kind='NM', work=9500, t1=500),
                  dict(game=0, side='A', id=1, round=320, type='L', kind='OVR', phase=2),
                  dict(game=0, side='A', id=1, round=320, type='L', kind='FIGHT', guard_break=1, tiles=5),
                  dict(game=0, side='A', id=2, round=320, type='C', kind='NM', work=12000, t1=900)]
        (self.telemetry / 'tele_events.jsonl').write_text(''.join(json.dumps(event) + '\n' for event in events))
        row = summary(self.extract, self.telemetry)['launcher_summaries'][0]
        context = row['descriptive_telemetry']
        self.assertEqual(context['nm_work_bytecodes']['sum'], 9500)
        self.assertEqual(context['nm_t1_bytecodes']['sum'], 500)
        self.assertEqual(context['ovr_phases'], {'2': 1})
        self.assertEqual(context['fight_guard_breaks'], 1)
        self.assertEqual(len(row['fallback']['samples'][0]['same_turn_launcher_events']), 4)

    def test_parser_exception_gate_and_terminal_close(self):
        for field in ('native_costs_usable', 'cost_usable'):
            with self.subTest(field=field):
                target = self.call if field == 'cost_usable' else self.robot
                target[field] = False
                self.assertEqual(self.evaluate()['fallback']['usable_witnesses'], 0)
                target[field] = True
        self.call['terminal_close_ambiguous'] = True
        self.assertEqual(self.evaluate()['fallback']['usable_witnesses'], 0)

    def test_balanced_stale_or_exception_context_censors_cost_callers_budgets(self):
        for status in ('unobserved_tail', 'observed_exception', 'invalid_counter', 'missing_counter'):
            for target_name in ('robot', 'call'):
                with self.subTest(status=status, target=target_name):
                    target = getattr(self, target_name)
                    old_status = target['exception_status']
                    target['exception_status'] = status
                    # All native balance/cost flags intentionally stay positive: statuses must override them.
                    row = self.evaluate()
                    method = row['methods']['mendUpdate']
                    self.assertEqual(method['observed_entries'], 1)
                    self.assertTrue(method['frequency_is_lower_bound'])
                    self.assertEqual(method['native_inclusive_bytecodes']['n'], 0)
                    self.assertEqual(method['native_exclusive_bytecodes']['n'], 0)
                    self.assertEqual(method['caller_contexts'], {})
                    self.assertEqual(method['completed_entry_budget_histogram'], {})
                    self.assertEqual(method['completed_return_budget_histogram'], {})
                    self.assertEqual(row['fallback']['successful_target_witnesses'], 0)
                    target['exception_status'] = old_status
        for target_name in ('robot', 'call'):
            target = getattr(self, target_name)
            old_context = target['caller_context_status']
            target['caller_context_status'] = 'suppressed_observed_exception'
            self.assertEqual(self.evaluate()['fallback']['usable_witnesses'], 0)
            target['caller_context_status'] = old_context

    def test_null_raw_exception_intervals_remain_observed_lower_bounds(self):
        self.robot.update(exception_status='observed_exception', exception_max=1,
                          caller_context_status='suppressed_observed_exception')
        self.call.update(exception_status='observed_exception', caller_context_status='suppressed_observed_exception',
                         native_inclusive=None, native_exclusive=None, caller_frame=None, entry_budget=None,
                         return_budget=None, cost_usable=False)
        row = self.evaluate()['methods']['mendUpdate']
        self.assertEqual(row['observed_entries'], 1)
        self.assertTrue(row['frequency_is_lower_bound'])
        self.assertEqual(row['native_inclusive_bytecodes']['n'], 0)
        self.assertEqual(row['caller_contexts'], {})

    def test_stale_centre_wrong_side_and_missing_march(self):
        for changes in (dict(r0=319), dict(objective=[30, 30]), dict(side='B'), dict(objective=[60, 2])):
            saved = self.event.copy()
            self.event.update(changes)
            self.assertEqual(self.evaluate()['fallback']['successful_target_witnesses'], 0)
            self.event = saved
        self.call['following_march_inclusive'] = None
        self.assertEqual(self.evaluate()['fallback']['target_success_unknown'], 1)
        self.call['following_march_inclusive'] = 0
        self.assertEqual(self.evaluate()['fallback']['target_success_unknown'], 1)
        self.call['round'] = None
        self.assertEqual(self.evaluate()['fallback']['target_witness_reasons'], {'native_round_unknown': 1})

    def test_duplicate_obj_rejected(self):
        self.evaluate()
        path = self.telemetry / 'tele_events.jsonl'
        path.write_text(path.read_text() * 2)
        row = summary(self.extract, self.telemetry)['launcher_summaries'][0]['fallback']
        self.assertEqual(row['target_witness_reasons'], {'multiple_obj_records': 1})

    def test_field_method_names_and_uncounted_method(self):
        self.call.update(method='read', caller_frame='c_mend3.Comms.nearestEnemy')
        self.robot['selected_entries']['read'] = 1
        row = self.evaluate()['methods']['read']
        self.assertEqual(row['observed_entries'], 1)
        self.assertEqual(row['native_inclusive_bytecodes']['n'], 1)
        self.assertIn('c_mend3.Comms.nearestEnemy', row['caller_contexts'])

    def test_identity_requires_footer_and_both_digests(self):
        pair = self.root / 'pair'
        pair.mkdir()
        fingerprint = '0 fixture 12 ' + 'a' * 40 + ' ' + 'b' * 40 + '\n'
        for mode in ('off', 'on'):
            (pair / (mode + '.fingerprint')).write_text(fingerprint)
            (pair / (mode + '.games')).write_text('0 fixture A 12\n')
            (pair / (mode + '.bc23')).write_bytes(b'fixture; not an engine replay')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(compare(pair))
            (pair / 'on.games').write_text('0 fixture B 12\n')
            self.assertFalse(compare(pair))
            (pair / 'on.games').write_text('0 fixture A 12\n')
            (pair / 'on.fingerprint').write_text(fingerprint.replace('b' * 40, 'c' * 40))
            self.assertFalse(compare(pair))
            (pair / 'on.fingerprint').write_text('')
            self.assertFalse(compare(pair))


def selftest():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SummaryTests)
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=2).run(suite)
    if not result.wasSuccessful():
        for test, traceback in result.failures + result.errors:
            print(str(test) + '\n' + traceback)
        raise SystemExit(2)
    print(json.dumps({'summary_selftest': 'passed', 'tests': result.testsRun, 'games_run': 0}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--selftest', action='store_true')
    modes.add_argument('--compare', type=Path)
    modes.add_argument('--extract', type=Path)
    parser.add_argument('--telemetry', type=Path)
    args = parser.parse_args()
    if args.telemetry is not None and args.extract is None:
        parser.error('--telemetry requires --extract')
    if args.selftest:
        selftest()
    elif args.compare:
        raise SystemExit(0 if compare(args.compare) else 4)
    else:
        result = summary(args.extract, args.telemetry)
        (args.extract / 'summary.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
        for row in result['launcher_summaries']:
            print(json.dumps({'game': row['game'], 'map': row['map'], 'side': row['side'],
                              'package': row['package'], 'launcher_turns': row['recorded_launcher_turns'],
                              'fallback': row['fallback'], 'descriptive_telemetry': row['descriptive_telemetry'],
                              'trace_issues': row['trace_issues'], 'capped_files': row['capped_profile_files'],
                              'exception_status_counts': row['exception_status_counts'],
                              'caller_context_status_counts': row['caller_context_status_counts'],
                              'full_launcher_coverage': row['full_launcher_coverage']}, sort_keys=True))
