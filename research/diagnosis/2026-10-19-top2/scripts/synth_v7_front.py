"""synth_v7_front.py: where the opening launcher war is fought and lost (deaths.csv, per-turn sa_L for the local odds).

Launcher deaths at round <= 150 per class (synth_common.klass) and side: count, and the share by position along the
HQ axis, prog = d(own HQ) / (d(own HQ) + d(enemy HQ)) (Euclidean, nearest HQs): home < 0.33, mid, enemy half > 0.67.
Local odds at a death (per-turn rows, the victim's last row at or before the death round): allies in vision + 1 vs
enemy launchers in vision (ally_L_20, enemy_L_20), median and the share outnumbered (enemies > allies + 1).
Usage: python3 -I synth_v7_front.py
"""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_common import *

SP = '/tmp/claude-1000/-home-terryvanbelle-projects-vibe-2023/4344f381-983b-4736-adb6-8d7ba2ecdeb6/scratchpad/top2'


def last_rows(G, side):
    for p in (f"{SP}/a0/sa/{G['m']}g{G['g']}{side}/sa_L.csv", f"{SP}/a1/sa300/{G['m']}g{G['g']}{side}/sa_L.csv"):
        if os.path.exists(p):
            last = {}
            with open(p) as fh:
                for r in csv.DictReader(fh):
                    if int(r['round']) > 155: break
                    last[int(r['id'])] = (int(r['ally_L_20']), int(r['enemy_L_20']))
            return last
    return None


def main():
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    for G in distinct():
        k = klass(G)
        for s in ('us', 'them'):
            side = G[s]
            own, opp = G['hqs'][side], G['hqs'][other(side)]
            lr = last_rows(G, side)
            for r in deaths(G, side):
                if r['type'] != 'L' or int(r['round']) > 150: continue
                xy = (int(r['x']), int(r['y']))
                a, b = math.sqrt(mind2(xy, own)), math.sqrt(mind2(xy, opp))
                pg = a / (a + b) if a + b else 0.5
                q = agg[(k, s)]
                q['zone'].append('home' if pg < 0.33 else 'enemy' if pg > 0.67 else 'mid')
                if lr is not None and int(r['id']) in lr:
                    al, en = lr[int(r['id'])]
                    q['odds'].append((al + 1, en))
    for k in ('A', 'A0', 'BC', 'W'):
        for s in ('us', 'them'):
            q = agg[(k, s)]
            z = collections.Counter(q['zone']); n = len(q['zone'])
            o = q['odds']
            outn = sum(1 for a, e in o if e > a)
            print(f"{k:3} {s:4}: launcher deaths <= r150 {n}; home {z['home']}, mid {z['mid']}, enemy half {z['enemy']}; "
                  f"odds at the last turn (covered {len(o)}): ours {med([a for a, e in o])} vs theirs {med([e for a, e in o])}, "
                  f"outnumbered {outn / max(1, len(o)):.2f}")


main()
