"""a2_census: selected census.csv fields, us / them, for the 19 long games. Usage: python3 -I a2_census.py [field ...]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
F = sys.argv[1:] or ['built_C', 'built_L', 'built_A', 'coll_Mn', 'coll_Ad', 'anchors_built', 'anchors_placed', 'anchors_lost',
                     'first_anchor', 'island_rounds', 'isl500', 'isl1000', 'isl_end', 'exch_ratio', 'healed', 'idle_funds']
print('game | k | ' + ' | '.join(F))
for m, g, k in A.ALL:
    u, t = A.census(m, g)
    print(A.label(m, g) + ' | ' + k + ' | ' + ' | '.join(f"{u.get(f, '?')}/{t.get(f, '?')}" for f in F))
