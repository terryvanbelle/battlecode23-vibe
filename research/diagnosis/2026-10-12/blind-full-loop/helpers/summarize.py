#!/usr/bin/env python3
"""Exact zero identity and controlled delivery checks. Reads owned fixture artifacts only."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def zero_gate(base, zero):
    require(base['pass'] and zero['pass'], 'full-loop base/zero fixture failed')
    require(base['rounds'] == zero['rounds'] == 32, 'incomplete full-loop zero control')
    require([row['round'] for row in base['native_states']] == [row['round'] for row in zero['native_states']] == list(range(1, 33)),
            'missing native zero round state')
    require(base['geometry_sha256'] == zero['geometry_sha256'], 'zero map changed')
    require(base['native_states'] == zero['native_states'], 'zero native state/shared/inventory/bytecode mismatch')
    require(base['script_events'] == zero['script_events'], 'zero scripted actor sequence changed')
    require(len(base['turns']) == len(zero['turns']) == 31, 'missing scheduled zero turns')
    require([row['round'] for row in base['turns']] == [row['round'] for row in zero['turns']] == list(range(2, 33)),
            'zero scheduled turn sequence changed')
    for expected, actual in zip(base['turns'], zero['turns']):
        for key in ('round', 'start_cd', 'end_cd', 'whole_turn_bytecodes', 'native_bytecode_limit',
                    'attacks', 'api_calls', 'indicator', 'memory'):
            require(expected[key] == actual[key], 'zero common turn mismatch: ' + key)
        require(all(actual['counters'].get(key) == value for key, value in expected['counters'].items()),
                'zero common source counter/RNG mismatch')
    return {'pass': True, 'native_state_and_bytecode_identity': True,
            'ordinary_action_and_api_trace_identity': True, 'indicator_identity': True,
            'selected_map_field_memory_identity': True, 'rounds': 32, 'scheduled_launcher_turns': 31,
            'native_state_sha256': digest(base['native_states']),
            'whole_turn_bytecodes_sha256': digest([t['whole_turn_bytecodes'] for t in base['turns']]),
            'scored_game_identity_claimed': False}


def arm_summary(result, baseline):
    require(result['pass'] and result['rounds'] == 32 and len(result['turns']) == 31, 'incomplete/unsafe arm fixture')
    require([row['round'] for row in result['turns']] == list(range(2, 33)), 'missing scheduled arm round')
    require(result['first_turn_initialization_included'] and not result['clock_or_owned_memory_modified'],
            'full native sandbox initialization/scheduling required')
    ordinary_base = {t['round']: t['attacks'] for t in baseline['turns'] if 18 <= t['round'] <= 21}
    hits = misses = damage = allied_damage = right_censored = observed_next = suffix_gaps = 0
    last_bs = 0
    own_cost = []
    work = []
    for turn in result['turns']:
        counters = turn['counters']
        require(counters['exceptions'] == counters['overruns'] == 0, 'bad source basics counters')
        require(turn['whole_turn_bytecodes'] < turn['native_bytecode_limit'], 'native scheduler exhaustion')
        require(turn['sandbox_paused'], 'source counter was not read at pause boundary')
        bs = counters['blindShots']
        delta = bs - last_bs
        last_bs = bs
        shots = [a for a in turn['attacks'] if a['blind_caller']]
        require(delta == len(shots) and 0 <= delta <= 1, 'paused bs/native hook attack mismatch')
        if shots:
            require(len(turn['attacks']) == 1, 'hook combined with an ordinary shot')
            attack = shots[0]
            require(attack['native_damage'] >= 0, 'invalid native attack damage')
            require(attack['hidden_at_attack'] and attack['native_can_attack'], 'shot was not hidden/legal natively')
            require(attack['pre_cd'] + attack['actual_rounded_cost'] <= 10, 'strict native cooldown policy violated')
            if 'next_actual_own_start_cd' in turn:
                require(turn['next_actual_own_start_cd'] == 0, 'next actual scheduled start has debt')
                observed_next += 1
            else:
                require(turn['round'] == 32 and turn['end_cd'] <= 10, 'unexplained missing next-start observation')
                right_censored += 1
            if attack['native_damage'] > 0:
                require(attack['target_team'] == 'B', 'friendly damage')
                hits += 1
                damage += attack['native_damage']
            else:
                misses += 1
            if attack['target_team'] == 'A':
                allied_damage += attack['native_damage']
            own_cost.append(attack['bytecodes_left'])
        token = re.search(r'(?:\||,)bs=(\d+)(?:,|$)', turn['indicator'])
        if token:
            require(int(token.group(1)) == bs, 'emitted bs token differs from paused source counter')
        elif bs:
            suffix_gaps += 1
        if 18 <= turn['round'] <= 21:
            expected = ordinary_base[turn['round']]
            require(len(expected) == len(turn['attacks']) == 1, 'visible ordinary shot lost')
            for key in ('shooter_at', 'target', 'hidden_at_attack', 'native_can_attack', 'pre_cd',
                        'actual_rounded_cost', 'post_cd', 'native_damage'):
                require(expected[0][key] == turn['attacks'][0][key], 'ordinary native behavior changed: ' + key)
            require(not turn['attacks'][0]['blind_caller'], 'ordinary shot relabelled as hook')
        work.append(counters['maxBc'])
    require(allied_damage == 0, 'allied carrier harmed')
    require(suffix_gaps == 0, 'controlled local indicators do not support complete action/bs matching')
    return {'arm': result['arm'], 'pass': True, 'launcher_turns': 31, 'blind_shots': hits + misses,
            'useful_hidden_hits': hits, 'native_hidden_damage': damage, 'zero_damage_misses': misses,
            'allied_damage': allied_damage, 'observed_actual_next_start_zero': observed_next,
            'right_censored_final_next_start': right_censored, 'emitted_bs_gaps': suffix_gaps,
            'ordinary_visible_phase_shots_preserved': 4, 'maximum_native_turn_bytecodes': max(t['whole_turn_bytecodes'] for t in result['turns']),
            'maximum_prefill_work_counter': max(work), 'minimum_native_attack_entry_left': min(own_cost) if own_cost else None,
            'map_field_progress': [{'round': t['round'], 'memory': t['memory']} for t in result['turns']],
            'native_state_sha256': digest(result['native_states']), 'scored_games': 0}


def all_summary(output):
    records = {name: json.loads((output / name / 'result.json').read_text()) for name in ('base', '0', '4', '2', '1')}
    identity = zero_gate(records['base'], records['0'])
    summaries = [arm_summary(records[name], records['base']) for name in ('base', '0', '4', '2', '1')]
    for name in ('base', '0'):
        require(next(s for s in summaries if s['arm'] == name)['blind_shots'] == 0, 'base/zero produced a hook')
    one = next(s for s in summaries if s['arm'] == '1')
    require(one['useful_hidden_hits'] >= 1 and one['native_hidden_damage'] >= 20, 'controlled full-loop useful damage absent')
    one_turns = records['1']['turns']
    require(any(10 <= t['round'] <= 13 and t['attacks'] and t['attacks'][0]['blind_caller'] and t['attacks'][0]['target_id'] is None for t in one_turns), 'empty hidden-cloud miss absent')
    require(any(14 <= t['round'] <= 17 and t['attacks'] and t['attacks'][0]['blind_caller'] and t['attacks'][0]['target_team'] == 'A' and t['attacks'][0]['native_damage'] == 0 for t in one_turns), 'native harmless allied-cloud delivery absent')
    return {'pass': True, 'zero_gate': identity, 'arms': summaries, 'controlled_fixtures_run': 5,
            'scored_games_run': 0, 'native_rounds_per_fixture': 32,
            'full_owned_launcher_loop': True, 'natural_complete_game_or_field_verdict': False,
            'limits': ['Only the actor runs actual owned RobotPlayer; all other units are fixed host-scripted actors.',
                       'Native controller, scheduler and first-turn initialization are real; host observations/proxy bodies are unmetered.',
                       'Boxed movement and fixed phases isolate delivery; no opponent realism or promotion claim.',
                       'The round-32 next own-start is right-censored when the last turn fires; its end-CD bound is reported, not labelled as an observed next turn.',
                       'Map/field progress is observed; padded final bytecodes do not establish equal useful planning work.']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zero', nargs=2, type=Path)
    parser.add_argument('--all', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.zero:
        result = zero_gate(*(json.loads((p / 'result.json').read_text()) for p in args.zero))
    else:
        result = all_summary(args.all)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'arms'}, sort_keys=True))


if __name__ == '__main__':
    main()
