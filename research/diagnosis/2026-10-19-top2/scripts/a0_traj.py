# Army and economy trajectory per game (timeline.csv): launchers alive us/them, carriers alive us/them and mana
# collected us/them at r30, 50, 80, 100, 150, 200, 250.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a0_common import *
RS = [30, 50, 80, 100, 150, 200, 250]

if __name__ == '__main__':
    print('| game | res | ' + ' | '.join(f'r{r} L / C / Mn' for r in RS) + ' |')
    print('|' + '---|' * (len(RS) + 2))
    for G in sorted(all_games(), key=lambda G: (G['won'], G['rounds'])):
        T = {(int(r['round']), r['side']): r for r in rd(G['m'], 'timeline') if int(r['game']) == G['g']}
        cells = []
        for rn in RS:
            a, b = T.get((rn, G['us'])), T.get((rn, G['them']))
            if not a or not b: cells.append('-'); continue
            cells.append(f"{a['alive_L']}-{b['alive_L']} / {a['alive_C']}-{b['alive_C']} / {a['coll_Mn']}-{b['coll_Mn']}")
        print(f"| {label(G)} | {'W' if G['won'] else 'L'} | " + ' | '.join(cells) + ' |')
