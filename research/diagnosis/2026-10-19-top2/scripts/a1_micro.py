"""a1_micro: launcher fight behaviour per side, r < RMAX, from sa_L.csv (a1_split.sh layout). A contact turn has an enemy
launcher within r2 20 at the start of the turn. Per side: contact turns, the share outnumbered (enemy_L_20 > ally_L_20+1)
and alone (no ally within r2 20), launcher hits per 100 contact turns, how those hits were made (atk_order: 'nomove'
stand, 'before' = fired then moved, 'after' = moved then fired, 'either'), the share of contact turns that ended farther
from the nearest enemy launcher (retreat), and kills (hits on a launcher with atk_target_hp_before <= 20).
Usage: a1_micro.py SA300_DIR [RMAX]"""
import sys, math
sys.path.insert(0, '/home/terryvanbelle/projects/vibe/2023/research/diagnosis/2026-10-19-top2/scripts')
from a1_common import *
SA = sys.argv[1]
RMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 150

def stats(m, g, side):
    c = collections.Counter()
    p = os.path.join(SA, '%dg%d%s' % (m, g, side), 'sa_L.csv')
    with open(p) as fh:
        for r in csv.DictReader(fh):
            if int(r['round']) >= RMAX:
                continue
            eL, aL = int(r['enemy_L_20']), int(r['ally_L_20'])
            att = r['attacked'] == '1' or (r['n_attacks'] not in ('', '0'))
            hitL = att and r['atk_hit'] == '1' and r['atk_target_type'] == 'L'
            if hitL:
                c['hitL_all'] += 1
                if r['atk_target_hp_before'] not in ('', None) and int(r['atk_target_hp_before']) <= 20:
                    c['killL'] += 1
            if att and r['atk_hit'] == '1' and r['atk_target_type'] == 'C':
                c['hitC'] += 1
            if eL == 0:
                continue
            c['contact'] += 1
            c['outnum'] += eL > aL + 1
            c['alone'] += aL == 0
            c['ahead2'] += aL + 1 - eL >= 2
            c['e16'] += int(r['enemy_L_16']) > 0
            if hitL:
                c['hitL'] += 1
                c['hit_' + (r['atk_order'] or 'none')] += 1
            if r['moved'] == '1' and r['move_dir'] not in ('', 'CENTER') and r['near_eL_dx'] != '':
                dx, dy = int(r['near_eL_dx']), int(r['near_eL_dy'])
                v = {'NORTH': (0, 1), 'NORTHEAST': (1, 1), 'EAST': (1, 0), 'SOUTHEAST': (1, -1), 'SOUTH': (0, -1),
                     'SOUTHWEST': (-1, -1), 'WEST': (-1, 0), 'NORTHWEST': (-1, 1)}.get(r['move_dir'])
                if v:
                    d0 = dx * dx + dy * dy
                    d1 = (dx - v[0]) ** 2 + (dy - v[1]) ** 2
                    c['mv'] += 1
                    c['mv_away'] += d1 > d0
                    c['mv_in'] += d1 < d0
    return c

if __name__ == '__main__':
    keys = ['contact', 'outnum', 'alone', 'ahead2', 'hitL', 'hit/100', 'stand', 'fire>move', 'move>fire', 'mv_away', 'mv_in', 'killL', 'hitC']
    print('group\tmatch\tg\tmap\twho\t' + '\t'.join(keys))
    tot = collections.defaultdict(collections.Counter)
    for grp, lst in (('collapse', COLLAPSE), ('earlywin', EARLYWIN)):
        for (m, g) in lst:
            G = games(m)[g]
            for who, side in (('us', G['us']), ('them', G['them'])):
                try:
                    c = stats(m, g, side)
                except FileNotFoundError:
                    continue
                n = max(1, c['contact'])
                row = [c['contact'], '%.2f' % (c['outnum'] / n), '%.2f' % (c['alone'] / n), '%.2f' % (c['ahead2'] / n), c['hitL'],
                       '%.1f' % (100 * c['hitL'] / n), c['hit_nomove'], c['hit_before'], c['hit_after'],
                       '%d/%d' % (c['mv_away'], c['mv']), c['mv_in'], c['killL'], c['hitC']]
                print('%s\t%d\t%d\t%s\t%s\t' % (grp, m, g, G['map'], who) + '\t'.join(str(x) for x in row))
                if (m, g) != (9921, 0):
                    tot[(grp, who)].update(c)
    print('\npooled (9921 g0 excluded)')
    for k, c in tot.items():
        n = max(1, c['contact'])
        print('%s %s: contact %d outnum %.2f alone %.2f ahead2 %.2f hitL %d (%.1f per 100 contact turns) stand %d fire>move %d move>fire %d either %d; moves away %d of %d, in %d; kills of L %d; hits on C %d (all turns)' % (
            k[0], k[1], c['contact'], c['outnum'] / n, c['alone'] / n, c['ahead2'] / n, c['hitL'], 100 * c['hitL'] / n,
            c['hit_nomove'], c['hit_before'], c['hit_after'], c['hit_either'], c['mv_away'], c['mv'], c['mv_in'], c['killL'], c['hitC']))
