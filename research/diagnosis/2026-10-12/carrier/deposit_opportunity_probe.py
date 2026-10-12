"""Read-only replay telemetry probe; no new games, source edits, or opponent source.

The two matches' generated reports establish side A as our c_mend2/137.
Previous HQ COMMS snapshots establish observed shared knowledge; maps/other-team
collection do not. Counts describe opportunities, not exact counterfactual calls.
"""
import bisect
import collections
import csv
import hashlib
import json
import math
import os
import pathlib
import statistics
import subprocess


def loc(value):
    if isinstance(value, list) and len(value) == 2:
        return tuple(int(v) for v in value)
    return None


def decode(value):
    value = int(value) & 4095
    return None if value == 0 else ((value - 1) // 64, (value - 1) % 64)


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def read_csv(path, manifest):
    data = path.read_bytes()
    manifest[str(path)] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    return list(csv.DictReader(data.decode('ascii').splitlines()))


def run_match(repo, match):
    root = repo / 'matches' / str(match) / 'extract'
    required = ('games.csv', 'hq.csv', 'trips.csv')
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        return {'match': match, 'missing': missing}
    manifest = {}
    game_rows = read_csv(root / 'games.csv', manifest)
    games = {int(r['game']): r for r in game_rows if r['side'] == 'A'}
    assert games[7]['map'] == 'MassiveL', (match, games[7])
    hq_rows = read_csv(root / 'hq.csv', manifest)
    actual_hqs = collections.defaultdict(set)
    for r in hq_rows:
        if r['side'] == 'A':
            actual_hqs[int(r['game'])].add((int(r['x']), int(r['y'])))
    trip_rows = read_csv(root / 'trips.csv', manifest)
    replay_trips = collections.defaultdict(list)
    for r in trip_rows:
        if r['side'] == 'A':
            replay_trips[int(r['game'])].append(r)
    snapshots, dots, role_changes = (collections.defaultdict(list),
                                     collections.defaultdict(list), set())
    kinds = collections.Counter()
    event_sha, event_bytes, invalid = hashlib.sha256(), 0, 0
    event_path = root / 'tele_events.jsonl'
    event_available = event_path.is_file()
    event_file = event_path.open('rb') if event_available else []
    for line in event_file:
        event_sha.update(line)
        event_bytes += len(line)
        try:
            d = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            invalid += 1
            continue
        if d.get('side') != 'A':
            continue
        g = int(d['game'])
        kinds[d.get('kind', '?')] += 1
        if d.get('kind') == 'COMMS':
            slots = d.get('slots')
            if isinstance(slots, list) and len(slots) == 64:
                snapshots[g].append((int(d['round']), slots))
        elif d.get('kind') == 'TRIP':
            dots[g].append(d)
        elif d.get('kind') == 'ROLE' and d.get('reason') == 'hq_stock':
            if d.get('old') != d.get('new'):
                role_changes.add((g, int(d['id']), int(d['round'])))
    if event_available:
        event_file.close()
        manifest[str(event_path)] = {'bytes': event_bytes, 'sha256': event_sha.hexdigest()}
    summaries = []
    for g, metadata in sorted(games.items()):
        counts, examples = collections.Counter(), []
        shared_publications = {}
        ordered = sorted(snapshots[g], key=lambda x: x[0])
        snapshot_rounds = [x[0] for x in ordered]
        for round_, slots in ordered:
            for value in slots[5:21]:
                if value:
                    key = (decode(value), (int(value) >> 12) & 3)
                    shared_publications.setdefault(key, round_)
        for d in dots[g]:
            counts['trip_dots'] += 1
            round_ = int(d.get('t_deposit', d['round']))
            assert round_ == int(d['round']), ('trip round mismatch', d)
            if (g, int(d['id']), round_) in role_changes:
                counts['role_changed_at_deposit'] += 1
                continue
            well, role = loc(d.get('well')), int(d.get('role', 0))
            if well is None or role not in (1, 2, 3):
                counts['no_current_well_or_role'] += 1
                continue
            if int(d.get('load', 0)) <= 0:
                counts['zero_load_dot'] += 1
                continue
            # Strictly earlier snapshots avoid intra-round ordering assumptions.
            j = bisect.bisect_left(snapshot_rounds, round_) - 1
            if j < 0:
                counts['no_strictly_prior_snapshot'] += 1
                continue
            snapshot_round, slots = ordered[j]
            hq_index = int(d.get('hq', -1))
            home = decode(slots[hq_index]) if 0 <= hq_index < 4 and slots[hq_index] else None
            if home not in actual_hqs[g]:
                counts['unconfirmed_deposit_hq'] += 1
                continue
            counts['evaluable_same_role_deposits'] += 1
            counts['snapshot_age_sum'] += round_ - snapshot_round
            candidates = []
            for value in slots[5:21]:
                if not value:
                    break
                if (int(value) >> 12) == role:
                    candidates.append(decode(value))
            if not candidates:
                counts['no_shared_role_well'] += 1
                continue
            # Python min preserves slot order on equal distance, matching Comms.
            nearest = min(candidates, key=lambda x: dist2(home, x))
            old_d, new_d = cheb(home, well), cheb(home, nearest)
            if nearest == well or 2 * new_d + 4 > old_d:
                continue
            counts['prior_shared_candidate_meets_reset_geometry'] += 1
            # An unknown seen candidate closer in Euclidean distance may have
            # larger Chebyshev distance. This bound passes for every such point.
            robust = 2 * math.isqrt(dist2(home, nearest)) + 4 <= old_d
            if robust:
                counts['geometry_passes_even_with_closer_unrecorded_seen_well'] += 1
            counts['opportunity_load_kg'] += int(d['load'])
            if len(examples) < 6:
                examples.append({'round': round_, 'carrier': int(d['id']), 'home': home,
                                 'old_well': well, 'shared_candidate': nearest,
                                 'old_cheb': old_d, 'new_cheb': new_d,
                                 'strict_prior_snapshot_round': snapshot_round,
                                 'closer_seen_robust': robust})
        baseline = replay_trips[g]
        deposits = [r for r in baseline if r['outcome'] == 'deposit']
        collected = [r for r in baseline if r['first_collect'] and r['well_x']]
        wells = collections.Counter((int(r['well_x']), int(r['well_y']), int(r['well_type']))
                                    for r in collected)
        cycles = [int(r['t_end']) - int(r['t0']) for r in deposits]
        well_stats = []
        for well, count in wells.most_common(8):
            same = [r for r in collected if (int(r['well_x']), int(r['well_y']), int(r['well_type'])) == well]
            same_deposits = [r for r in same if r['outcome'] == 'deposit']
            same_cycles = [int(r['t_end']) - int(r['t0']) for r in same_deposits]
            well_stats.append({'well': well[:2], 'type': well[2], 'trips': count,
                               'first_collection_round': min(int(r['first_collect']) for r in same),
                               'deposit_trips': len(same_deposits),
                               'deposit_load_kg': sum(int(r['load']) for r in same_deposits),
                               'death_trips': sum(r['outcome'] == 'death' for r in same),
                               'deposit_cycle_median': statistics.median(same_cycles) if same_cycles else None,
                               'geometric_distance_to_each_own_hq': [
                                   {'hq': h, 'cheb': cheb(h, well[:2]), 'dist2': dist2(h, well[:2])}
                                   for h in sorted(actual_hqs[g])]})
        stats = {'replay_trips': len(baseline), 'deposit_trips': len(deposits),
                 'deposit_load_kg': sum(int(r['load']) for r in deposits),
                 'death_trips': sum(r['outcome'] == 'death' for r in baseline),
                 'deposit_cycle_median': statistics.median(cycles) if cycles else None,
                 'wells_by_collected_trip': well_stats}
        summaries.append({'game': g, 'map': metadata['map'], 'side': 'A',
                          'replay_team': metadata['team'], 'won': metadata['won'],
                          'rounds': metadata['rounds'], 'snapshots': len(ordered),
                          'replay_telemetry': {k: metadata.get(k) for k in ('tele', 'tele_dots', 'tele_unknown_kinds')},
                          'opportunity_counts': dict(counts) if event_available and ordered else None,
                          'opportunity_unavailable_reason': None if event_available and ordered else
                              'No COMMS/TRIP data dots; field replays disable indicators. Shared/private '
                              'well knowledge and actual deposit HQ per carrier are unavailable.',
                          'examples': examples,
                          'baseline': stats,
                          'first_shared_snapshots': [
                              {'well': k[0], 'type': k[1], 'round': r}
                              for k, r in sorted(shared_publications.items(), key=lambda x: x[1])]})
    return {'match': match, 'events_available': event_available,
            'invalid_event_lines': invalid if event_available else None,
            'our_dot_kinds': dict(kinds) if event_available else None,
            'files': manifest, 'games': summaries}


def main():
    repo = pathlib.Path(os.environ.get('BC23_WORKER_REPO', '.')).resolve()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    result = {'head': head, 'semantics': [
        'Side A fixed from own generated match reports 4562 and 4565.',
        'Only strictly earlier observed COMMS snapshots supply candidate wells.',
        'No map truth or other-team observation is treated as our knowledge.',
        'Replay trip well is the dominant collected well; reconstructed deposit load is all resources, '
        'not necessarily the dominant well resource alone. Per-trip deposit HQ is absent without dots.',
        'Opportunity geometry is not exact counterfactual call count: shared state between snapshots, '
        'current role/well changes after TRIP, private seen wells, movement, and budget are not fully observed.',
        'Zero opportunity counts do not rule out unobserved newly published or privately seen wells.'],
              'matches': [run_match(repo, m) for m in (4562, 4565)]}
    print(json.dumps(result, separators=(',', ':')))


if __name__ == '__main__':
    main()
