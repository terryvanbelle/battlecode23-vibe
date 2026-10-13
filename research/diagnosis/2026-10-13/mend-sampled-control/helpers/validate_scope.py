#!/usr/bin/env python3
"""Admit only useful own Mend2 cost scope; never executes games or queries a VM."""
import collections
import json
import sys
from pathlib import Path

from summarize import coverage_ok, integer, usable


REQUIRED_METHODS = ('mendUpdate', 'march', 'pickObjective')
PACKAGE = 'c_mend2'
MAP = 'Cornucopia'
SEED = 272


def identity(row):
    return tuple(row.get(key) for key in ('game', 'map', 'side', 'package', 'robot'))


def counter_range(call):
    start, end = integer(call.get('open_at')), integer(call.get('close_at'))
    return (start, end) if start is not None and end is not None and 0 <= start <= end else None


def metered_budget(call):
    entry, returned = integer(call.get('entry_budget')), integer(call.get('return_budget'))
    cost = integer(call.get('native_inclusive'))
    counters = counter_range(call)
    return (entry is not None and returned is not None and cost is not None
            and counters is not None and counters[1] - counters[0] == cost
            and 0 < returned <= entry <= 10000 and cost > 0 and entry - returned == cost)


def target(row):
    return (row.get('game') == 0 and row.get('map') == MAP and row.get('side') == 'A'
            and row.get('package') == PACKAGE)


def assess(robots, intervals, files):
    """Cost-scope admission only; fingerprint/provenance validation is a separate prior gate."""
    file_index = {}
    for file in files:
        key = (file.get('game'), file.get('file'))
        if key in file_index:
            raise ValueError('duplicate native profile file')
        file_index[key] = file
    relevant = [robot for robot in robots if target(robot) and robot.get('type') == 'LAUNCHER']
    robot_index = {}
    for robot in relevant:
        key = identity(robot)
        if key in robot_index:
            raise ValueError('duplicate own launcher robot')
        robot_index[key] = robot
    accepted_robots = {}
    exclusions = collections.Counter()
    for key, robot in robot_index.items():
        file = file_index.get((robot.get('game'), robot.get('file')))
        if file is None:
            exclusions['missing_own_profile_file'] += 1
        elif file.get('game') != 0 or file.get('map') != MAP or file.get('map_seed') != SEED or file.get('side') != 'A':
            exclusions['own_profile_map_seed_side_mismatch'] += 1
        elif not coverage_ok(robot, file) or robot.get('native_costs_usable') is not True:
            exclusions['own_launcher_cost_coverage_unusable'] += 1
        elif integer(robot.get('recorded_turns')) is None or integer(robot['recorded_turns']) < 1:
            exclusions['own_launcher_has_no_recorded_turns'] += 1
        else:
            accepted_robots[key] = robot
    accepted_calls = []
    for call in intervals:
        if not target(call):
            continue
        robot = accepted_robots.get(identity(call))
        if robot is None:
            continue
        file = file_index.get((robot['game'], robot.get('file')))
        if (call.get('file') != robot.get('file') or not usable(call, robot, file)
                or integer(call.get('round')) is None or not metered_budget(call)
                or counter_range(call) is None):
            exclusions['own_interval_cost_or_budget_unusable'] += 1
            continue
        accepted_calls.append(call)
    method_counts = collections.Counter(call.get('method') for call in accepted_calls)
    by_turn = collections.defaultdict(list)
    for call in accepted_calls:
        by_turn[identity(call) + (call['round'],)].append(call)
    witnesses = []
    for mend in accepted_calls:
        if mend.get('method') != 'mendUpdate' or mend.get('frame') != PACKAGE + '.Launcher.mendUpdate':
            continue
        direct = integer(mend.get('direct_reads_before_nearest'))
        march_cost = integer(mend.get('following_march_inclusive'))
        pick_cost = integer(mend.get('following_pick_objective_inclusive'))
        tail_cost = integer(mend.get('launcher_tail_inclusive'))
        if (direct is None or direct < 1 or march_cost is None or march_cost <= 0
                or pick_cost is None or pick_cost <= 0 or tail_cost is None or tail_cost < march_cost):
            continue
        begin, end = counter_range(mend)
        run_end = end + tail_cost
        peers = by_turn[identity(mend) + (mend['round'],)]
        runs = [call for call in peers if call.get('method') == 'run'
                and call.get('frame') == PACKAGE + '.Launcher.run'
                and mend.get('caller_frame') == call['frame']
                and counter_range(call)[0] <= begin and counter_range(call)[1] == run_end]
        nearest = [call for call in peers if call.get('method') == 'nearestEnemy'
                   and call.get('frame') == PACKAGE + '.Comms.nearestEnemy'
                   and call.get('caller_frame') == mend['frame']
                   and begin <= counter_range(call)[0] <= counter_range(call)[1] <= end]
        marches = [call for call in peers if call.get('method') == 'march'
                   and call.get('frame') == PACKAGE + '.Launcher.march'
                   and call.get('caller_frame') == PACKAGE + '.Launcher.run'
                   and end <= counter_range(call)[0] <= counter_range(call)[1] <= run_end]
        if not runs or not nearest or not marches:
            continue
        paired = []
        for march in marches:
            march_begin, march_end = counter_range(march)
            picks = [call for call in peers if call.get('method') == 'pickObjective'
                     and call.get('frame') == PACKAGE + '.Launcher.pickObjective'
                     and call.get('caller_frame') == march['frame']
                     and march_begin <= counter_range(call)[0] <= counter_range(call)[1] <= march_end]
            if picks:
                paired.append((march, picks))
        if not paired:
            continue
        if (sum(march['native_inclusive'] for march in marches) != march_cost
                or sum(pick['native_inclusive'] for _, picks in paired for pick in picks) != pick_cost):
            exclusions['mend_tail_annotations_disagree'] += 1
            continue
        witnesses.append({key: mend.get(key) for key in ('game', 'map', 'side', 'package', 'robot', 'round',
                          'entry_budget', 'return_budget', 'native_inclusive', 'direct_reads_before_nearest',
                          'following_march_inclusive', 'following_pick_objective_inclusive', 'launcher_tail_inclusive')})
    missing = []
    if not accepted_robots:
        missing.append('no_complete_aligned_usable_own_launcher')
    for method in REQUIRED_METHODS:
        if not method_counts[method]:
            missing.append('no_usable_budgeted_' + method)
    if not witnesses:
        missing.append('no_same_turn_owned_target_mend_march_pick_tail_witness')
    return {'schema_version': 1, 'ready': not missing, 'status': 'ready' if not missing else 'not_ready',
            'scope': {'game': 0, 'map': MAP, 'map_seed': SEED, 'side': 'A', 'package': PACKAGE},
            'own_launcher_robots': len(relevant), 'usable_aligned_own_launchers': len(accepted_robots),
            'usable_budgeted_method_intervals': {name: method_counts[name] for name in (*REQUIRED_METHODS, 'run', 'nearestEnemy')},
            'same_turn_mend_tail_witnesses': len(witnesses), 'samples': witnesses[:5],
            'missing_requirements': missing, 'excluded_records': dict(sorted(exclusions.items())),
            'limits': [
                'Admission concerns useful measured cost scope only. Exact replay identity, hashes, source/classes, engine/JDK and matchup provenance must pass separately first.',
                'One complete owned-target recheck and its march/pickObjective tail are sufficient for this diagnostic admission; this is not a statistical or promotion gate.',
                'Nested nearestEnemy proves an owned target was evaluated, not that it was blocked or a fallback alternative existed.',
                'Other-side profile caps and unrelated non-launcher exceptions do not block this narrow scope. A cap on the selected own team file still censors all launcher costs in that file.',
                'No usable scope means not_ready and zero new candidate games; it is not evidence of zero fallback opportunities.',
            ]}


def read_scope(directory):
    def read(name):
        with (directory / name).open() as stream:
            return [json.loads(line) for line in stream if line.strip()]
    return assess(read('robots.jsonl'), read('intervals.jsonl'), read('files.jsonl'))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('validate_scope.py NEW_REEXTRACTED_NATIVE_DIRECTORY')
    directory = Path(sys.argv[1])
    if directory.is_symlink() or not directory.is_dir():
        raise SystemExit('native extraction must be a regular directory')
    try:
        result = read_scope(directory)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = {'schema_version': 1, 'ready': False, 'status': 'not_ready',
                  'missing_requirements': ['invalid_native_scope_inputs'], 'error': str(error)}
    (directory / 'scope.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result['ready'] else 3)
