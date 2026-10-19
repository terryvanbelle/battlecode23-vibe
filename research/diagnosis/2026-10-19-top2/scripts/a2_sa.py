"""a2_sa: one streaming pass over the per-turn dumps (sa_L, sa_HQ, sa_C) of the 19 games, both teams; writes per
(match, game, who=us|them, 100-round bin) metrics to $SP/a2/out/sa_bins.csv.
Launchers: turns; heal = sum of positive hp steps between a robot's consecutive rows (only islands heal, RULES 8.1);
dmg = negative steps; position by e = sqrt(d2_own_hq) / (sqrt(d2_own_hq) + sqrt(d2_enemy_hq)) (Euclidean progress
from the own nearest HQ: home < 0.35, mid, far > 0.65); ring = 16 <= d2_enemy_hq <= 34 (our C.RING_MIN..MAX);
isl = within r2 4 of an own island square (heal range); contact = an enemy launcher within r2 20; outn = contact turns
with enemy_L_20 > ally_L_20 + 1 (ally excludes self); alone = contact turns with ally_L_20 == 0; shots/hits.
HQs: HQ-rounds; enemy_L_34 summed (pressure); HQ-rounds with enemy_L_34 >= 3 and with enemy_L_9 >= 1.
Carriers: turns; turns carrying an anchor; anchor placements and takes; collected Ad/Mn; turns with an enemy launcher
within r2 20. Usage: python3 -I a2_sa.py [match ...]"""
import sys, os, csv, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
OUT = A.SP + '/a2/out/sa_bins.csv'
FIELDS = ['L_turns', 'L_heal', 'L_dmg', 'L_home', 'L_mid', 'L_far', 'L_ring', 'L_isl', 'L_contact', 'L_outn', 'L_alone',
          'L_ahead', 'L_shots', 'L_hits', 'H_rounds', 'H_eL34', 'H_press3', 'H_eL9', 'C_turns', 'C_anchor', 'C_place',
          'C_take', 'C_Ad', 'C_Mn', 'C_threat', 'C_home', 'C_mid', 'C_far']


def i(x, d=-1):
    try:
        return int(x)
    except ValueError:
        return d


def run_game(m, g, who, side):
    acc = collections.defaultdict(collections.Counter)
    last = {}
    for r in A.sa_iter(m, g, side, 'L', ['round', 'id', 'hp', 'd2_own_hq', 'd2_enemy_hq', 'ally_L_20', 'enemy_L_20',
                                        'd2_island_own', 'n_attacks', 'atk_hit']):
        rn = int(r['round']); b = rn // 100; c = acc[b]
        c['L_turns'] += 1
        hp = int(r['hp']); rid = r['id']
        if rid in last:
            dh = hp - last[rid]
            if dh > 0: c['L_heal'] += dh
            elif dh < 0: c['L_dmg'] -= dh
        last[rid] = hp
        do, de = i(r['d2_own_hq']), i(r['d2_enemy_hq'])
        if do >= 0 and de >= 0:
            e = math.sqrt(do) / (math.sqrt(do) + math.sqrt(de)) if do + de > 0 else 0.5
            c['L_home' if e < 0.35 else 'L_mid' if e <= 0.65 else 'L_far'] += 1
            if 16 <= de <= 34: c['L_ring'] += 1
        io = i(r['d2_island_own'])
        if 0 <= io <= 4: c['L_isl'] += 1
        al, en = i(r['ally_L_20'], 0), i(r['enemy_L_20'], 0)
        if en > 0:
            c['L_contact'] += 1
            if en > al + 1: c['L_outn'] += 1
            if al == 0: c['L_alone'] += 1
            if al + 1 - en >= 2: c['L_ahead'] += 1
        c['L_shots'] += i(r['n_attacks'], 0)
        c['L_hits'] += r['atk_hit'] == '1'
    for r in A.sa_iter(m, g, side, 'HQ', ['round', 'enemy_L_34', 'enemy_L_9']):
        rn = int(r['round']); c = acc[rn // 100]
        c['H_rounds'] += 1
        e34 = i(r['enemy_L_34'], 0)
        c['H_eL34'] += e34
        c['H_press3'] += e34 >= 3
        c['H_eL9'] += i(r['enemy_L_9'], 0) >= 1
    for r in A.sa_iter(m, g, side, 'C', ['round', 'anchor', 'anchor_place', 'anchor_take', 'collect_res', 'collect_amt',
                                        'near_eL_d2', 'd2_own_hq']):
        rn = int(r['round']); c = acc[rn // 100]
        c['C_turns'] += 1
        if i(r['anchor'], 0) > 0: c['C_anchor'] += 1
        c['C_place'] += i(r['anchor_place'], 0) > 0
        c['C_take'] += i(r['anchor_take'], 0) > 0
        amt = i(r['collect_amt'], 0)
        if r['collect_res'] in ('Ad', '1', 'ADAMANTIUM'): c['C_Ad'] += amt
        elif r['collect_res'] in ('Mn', '2', 'MANA'): c['C_Mn'] += amt
        nd = i(r['near_eL_d2'])
        if 0 <= nd <= 20: c['C_threat'] += 1
    return acc


def main():
    ms = set(int(x) for x in sys.argv[1:])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    old = []
    if ms and os.path.exists(OUT):
        with open(OUT) as fh:
            old = [r for r in csv.DictReader(fh) if int(r['match']) not in ms]
    with open(OUT, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['match', 'game', 'who', 'bin'] + FIELDS)
        for r in old:
            w.writerow([r['match'], r['game'], r['who'], r['bin']] + [r[f] for f in FIELDS])
        for m, g, k in A.ALL:
            if ms and m not in ms:
                continue
            d = A.G(m, g)
            for who, side in (('us', d['us']), ('them', d['them'])):
                if A.sa_path(m, g, side, 'L')[0] is None:
                    print('missing dump', m, g, side, file=sys.stderr)
                    continue
                acc = run_game(m, g, who, side)
                for b in sorted(acc):
                    w.writerow([m, g, who, b] + [acc[b][f] for f in FIELDS])
                print('done', A.label(m, g), who, file=sys.stderr)


if __name__ == '__main__':
    main()
