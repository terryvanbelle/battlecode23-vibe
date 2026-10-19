"""a2_mapisl: islands of a map (map file via a0_common.load_map): id, size, centre, Euclidean progress
e = d(our nearest HQ) / (d(ours) + d(theirs)) from OUR side in game (m, g), and the owner at the end of the game
from the last per-turn rows (our launchers' d2_island_own == 0 / d2_island_enemy == 0 on a tile, approximate).
Usage: python3 -I a2_mapisl.py MATCH GAME"""
import sys, os, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A
import a0_common as Z


def islands(name):
    mp = Z.load_map(name)
    W = mp['W']
    d = collections.defaultdict(list)
    for k, v in enumerate(mp['islands']):
        if v > 0:
            d[v].append((k % W, k // W))
    return d


def main():
    m, g = int(sys.argv[1]), int(sys.argv[2])
    G = A.G(m, g)
    hq = Z.hqs(m, g)
    us, th = hq[G['us']], hq[G['them']]
    print(f"{A.label(m, g)} N={G['nisl']} our HQs {us} their HQs {th}")
    for i, tiles in sorted(islands(G['map']).items()):
        cx = sum(t[0] for t in tiles) / len(tiles); cy = sum(t[1] for t in tiles) / len(tiles)
        du = min(math.hypot(cx - x, cy - y) for x, y in us); dt = min(math.hypot(cx - x, cy - y) for x, y in th)
        print(f"  island {i}: {len(tiles)} tiles, centre ({cx:.0f},{cy:.0f}), e from us {du / (du + dt):.2f} (d us {du:.0f}, them {dt:.0f})")


if __name__ == '__main__':
    main()
