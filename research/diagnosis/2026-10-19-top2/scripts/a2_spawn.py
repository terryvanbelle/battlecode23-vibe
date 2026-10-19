"""a2_spawn: launchers our HQs build into a siege. For each of our launchers (robots.csv) we look up the enemy
launchers within r2 34 of the HQ that built it (nearest of our HQs to the birth tile) on the birth round (sa_HQ
enemy_L_34). Besieged birth = 3+ enemy launchers there. Per game and pooled: launchers built besieged, their median life,
the share dead within 10 rounds, the kills they made (deaths.csv killer_id), and the same for the opponent's HQs.
Usage: python3 -I a2_spawn.py"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A


def hq_pressure(m, g, side):
    p = {}
    hqs = set()
    for r in A.sa_iter(m, g, side, 'HQ', ['round', 'x', 'y', 'enemy_L_34']):
        k = (int(r['x']), int(r['y']))
        hqs.add(k)
        p[(int(r['round']), k)] = int(r['enemy_L_34'] or 0)
    return p, sorted(hqs)


def analyse(m, g, side):
    p, hqs = hq_pressure(m, g, side)
    kills = collections.Counter()
    for x in A.rows(m, 'deaths'):
        if int(x['game']) == g and x['killer_id']:
            kills[x['killer_id']] += 1
    out = collections.Counter()
    lives = {'bes': [], 'free': []}
    for r in A.rows(m, 'robots'):
        if int(r['game']) != g or r['side'] != side or r['type'] != 'L':
            continue
        b = int(r['born'])
        bx, by = int(r['x_born']), int(r['y_born'])
        h = min(hqs, key=lambda q: (q[0] - bx) ** 2 + (q[1] - by) ** 2)
        e = p.get((b, h), p.get((b - 1, h), 0))
        k = 'bes' if e >= 3 else 'free'
        died = r['died']
        life = (int(died) - b) if died else None
        out[k] += 1
        if life is not None:
            lives[k].append(life)
            out[k + '_dead10'] += life <= 10
        out[k + '_kills'] += kills[r['id']]
        out[k + '_late'] += b >= 600
    return out, lives


def main():
    pool = collections.defaultdict(collections.Counter)
    plives = collections.defaultdict(list)
    print('game | k | our L built besieged / total | besieged: median life, dead<=10r, kills | free: median life, kills | '
          'their L built besieged / total')
    for m, g, kk in A.ALL:
        d = A.G(m, g)
        if A.sa_path(m, g, d['us'], 'HQ')[0] is None:
            continue
        o, lv = analyse(m, g, d['us'])
        t, tl = analyse(m, g, d['them'])
        cls = 'L' if kk != 'W' else 'W'
        pool[cls].update(o); pool[cls + 'them'].update(t)
        plives[cls + 'bes'] += lv['bes']; plives[cls + 'free'] += lv['free']
        print(f"{A.label(m, g)} | {kk} | {o['bes']}/{o['bes'] + o['free']} | {A.med(lv['bes'])}, {o['bes_dead10']}, {o['bes_kills']} | "
              f"{A.med(lv['free'])}, {o['free_kills']} | {t['bes']}/{t['bes'] + t['free']}")
    for cls in ('L', 'W'):
        o, t = pool[cls], pool[cls + 'them']
        print(f"pooled {cls}: our launchers built besieged {o['bes']} of {o['bes'] + o['free']} ({o['bes_late']} from r600), "
              f"dead within 10 rounds {o['bes_dead10']}, median life {A.med(plives[cls + 'bes'])} vs {A.med(plives[cls + 'free'])} unbesieged; "
              f"kills by them {o['bes_kills']} ({o['bes_kills'] / max(1, o['bes']):.2f} per launcher) vs unbesieged {o['free_kills'] / max(1, o['free']):.2f}; "
              f"Mn spent besieged {45 * o['bes']}. Opponent launchers built besieged {t['bes']} of {t['bes'] + t['free']}")


if __name__ == '__main__':
    main()
