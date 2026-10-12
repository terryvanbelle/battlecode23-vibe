"""Read-only Forest economy/first-collection probe, own field matches 4566/4570.

No source changes, game launches, opponent source reads, or writes. Inventory
balance measures net non-passive HQ inflow, not gross carrier deposits.
"""
import collections
import csv
import hashlib
import json
import os
import pathlib
import statistics
import subprocess

BOUNDS = (0, 100, 250, 500, 750, 1000, 1500, 2000)
HQ_COLUMNS = ('r0,r1,side,hq,x,y,net_inflow_Ad,net_inflow_Mn,built_C,built_L,built_K,'
              'pressure34,pressure9,idle_funds,code_c,code_t,code_p,code_a,code_s,code_b,'
              'bank_Ad_p50,bank_Mn_p50').split(',')


def integer(value, default=0):
    return int(value) if value not in (None, '') else default


def median(values):
    return statistics.median(values) if values else None


def read(path, manifest):
    raw = path.read_bytes()
    manifest[path.name] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    return list(csv.DictReader(raw.decode('ascii').splitlines()))


def parse_codes(text):
    c = collections.Counter()
    for token in (text or '').split(';'):
        if '=' in token:
            key, value = token.split('=', 1)
            c[key] += int(value)
    return c


def inspect(repo, match):
    root = repo / 'matches' / str(match) / 'extract'
    required = ('games.csv', 'hq.csv', 'timeline.csv', 'tele_states.csv', 'trips.csv', 'robots.csv')
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        return {'match': match, 'missing': missing}
    manifest = {}
    tables = {name: [r for r in read(root / name, manifest) if integer(r.get('game'), -1) == 4]
              for name in required}
    game = {r['side']: r for r in tables['games.csv']}
    assert game['A']['map'] == 'Forest' and integer(game['A']['rounds']) == 2000
    rows = tables['hq.csv']
    hq_groups = collections.defaultdict(list)
    for row in rows:
        hq_groups[(row['side'], row['hq_id'])].append(row)
    hq_intervals, accounting_notes = [], []
    for (side, hq), buckets in sorted(hq_groups.items()):
        buckets.sort(key=lambda r: integer(r['round']))
        prev_round, prev_ad, prev_mn = 0, 200, 200
        ex_known_absent = all(integer(r.get('coll_Ex')) == 0 and integer(r.get('bank_Ex')) == 0
                              and integer(r.get('carried_Ex')) == 0
                              for r in tables['timeline.csv'] if r['side'] == side)
        enriched = []
        for row in buckets:
            round_ = integer(row['round'])
            assert round_ > prev_round
            ad, mn = integer(row['bank_Ad']), integer(row['bank_Mn'])
            builds = {t: integer(row['built_' + t]) for t in ('C', 'L', 'A', 'K')}
            passive = 6 * (round_ // 5 - prev_round // 5)
            net_ad = ad - prev_ad + 50 * builds['C'] + 30 * builds['A'] + 80 * builds['K'] - passive
            net_mn = mn - prev_mn + 45 * builds['L'] + 15 * builds['A'] + 80 * builds['K'] - passive
            enriched.append(dict(row, prev_round=prev_round, net_ad=net_ad, net_mn=net_mn,
                                 codes_decoded=parse_codes(row['codes'])))
            prev_round, prev_ad, prev_mn = round_, ad, mn
        if not ex_known_absent:
            accounting_notes.append({'side': side, 'hq': hq,
                                     'warning': 'Observed Ex permits accelerating anchors; net A/Mn inflow not reported.'})
        for r0, r1 in zip(BOUNDS, BOUNDS[1:]):
            selection = [r for r in enriched if r0 < integer(r['round']) <= r1]
            if not selection:
                continue
            codes = sum((r['codes_decoded'] for r in selection), collections.Counter())
            totals = lambda field: sum(integer(r[field]) for r in selection)
            hq_intervals.append([r0, r1, side, hq, integer(selection[0]['x']), integer(selection[0]['y']),
                                 totals('net_ad') if ex_known_absent else None,
                                 totals('net_mn') if ex_known_absent else None,
                                 totals('built_C'), totals('built_L'), totals('built_K'),
                                 totals('pressure34'), totals('pressure9'), totals('idle_funds'),
                                 *[codes.get(code, 0) for code in ('c', 't', 'p', 'a', 's', 'b')],
                                 median([integer(r['bank_Ad']) for r in selection]),
                                 median([integer(r['bank_Mn']) for r in selection])])
    phase_states = []
    for phase in ('open', 'mid', 'late'):
        own = [r for r in tables['tele_states.csv'] if r['side'] == 'A' and r['phase'] == phase]
        for type_ in ('C', 'H'):
            typed = [r for r in own if r['type'] == type_]
            codes = collections.Counter()
            for row in typed:
                codes[row['letter']] += integer(row['turns'])
            total = sum(codes.values())
            phase_states.append({'phase': phase, 'type': type_, 'decoded_turns': total,
                                 'letter_turns': dict(codes),
                                 'mana_role_turns': sum(integer(r['turns']) for r in typed
                                                        if type_ == 'C' and integer(r['code']) % 2 == 1)})
    robot_rows = [r for r in tables['robots.csv'] if r['type'] == 'C']
    earliest = {}
    for row in tables['trips.csv']:
        if row['first_collect']:
            key = (row['side'], row['carrier'])
            first = integer(row['first_collect'])
            earliest[key] = min(earliest.get(key, first), first)
    population = []
    slow = []
    for side in ('A', 'B'):
        carriers = [r for r in robot_rows if r['side'] == side]
        for round_ in BOUNDS[1:]:
            alive = [r for r in carriers if integer(r['born']) <= round_
                     and (integer(r['died'], -1) < 0 or integer(r['died']) > round_)]
            unseen = [r for r in alive if earliest.get((side, r['id']), round_ + 1) > round_]
            tline = next((r for r in tables['timeline.csv'] if r['side'] == side and integer(r['round']) == round_), None)
            population.append({'side': side, 'round': round_, 'reconstructed_alive_carriers': len(alive),
                               'timeline_alive_carriers': integer(tline['alive_C']) if tline else None,
                               'alive_without_any_recorded_collection_yet': len(unseen),
                               'no_collection_carrier_age_p50': median([round_ - integer(r['born']) for r in unseen]),
                               'collected_Mn': integer(tline['coll_Mn']) if tline else None,
                               'collected_Ad': integer(tline['coll_Ad']) if tline else None})
            if side == 'A' and round_ == 1000:
                old = sorted((r for r in unseen if integer(r['born']) < 500), key=lambda r: integer(r['born']))[:12]
                slow = [{'id': r['id'], 'born': integer(r['born']),
                         'first_recorded_collection': earliest.get((side, r['id'])),
                         'max_still_any_context': integer(r['max_still']),
                         'still_r0': r['still_r0'], 'born_xy': [integer(r['x_born']), integer(r['y_born'])]}
                        for r in old]
    return {'match': match, 'side_A_is_ours': True, 'metadata': game,
            'files': manifest, 'hq_phase_columns': HQ_COLUMNS, 'hq_phase_rows': hq_intervals,
            'accounting_warnings': accounting_notes, 'own_state_counts': phase_states,
            'carrier_first_collection_population': population,
            'old_own_carriers_without_collection_at_1000': slow}


def main():
    repo = pathlib.Path(os.environ.get('BC23_WORKER_REPO', '.')).resolve()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    print(json.dumps({'head': head, 'games_run': 0, 'semantics': [
        'HQ net non-passive inflow = bank delta + observed build costs - passive income; includes withdrawals as negative.',
        'Initial HQ bank=200 and +6 Ad/Mn every fifth end-of-round. Standard anchor costs assumed only when all Ex is absent.',
        'HQ codes are observed build-loop stop reasons, not mutually exclusive causal costs or whole-turn decisions.',
        'Pressure is observed end-of-round launcher range exposure, not the exact inDanger predicate.',
        'Fleet non-collection counts include legitimate courier duty; max_still spans any life context.',
        'Snapshots/first-collection counts alone cannot identify actual G-turn stalls; raw replay movement is needed.'],
                      'matches': [inspect(repo, m) for m in (4566, 4570)]}, separators=(',', ':')))


if __name__ == '__main__':
    main()
