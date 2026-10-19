"""a2_tl: one game's timeline, us vs them, every STEP rounds from FROM: islands, anchors placed, alive launchers and
carriers, our banked Ad and Mn. Usage: python3 -I a2_tl.py MATCH GAME [STEP=100] [FROM=300]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_common as A


def main():
    m, g = int(sys.argv[1]), int(sys.argv[2])
    step = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    lo = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    t = A.timeline(m, g)
    end = A.G(m, g)['rounds']
    print(A.label(m, g), 'rounds', end, '| round: islands us/them, anchors placed, alive L, alive C | our bank Ad/Mn')
    for r in range(lo, end + 1, step):
        u, th = A.at(t['us'], r), A.at(t['them'], r)
        if u is None or th is None:
            continue
        print(f"r{r}: isl {u['islands']}/{th['islands']} anch {u['anchors_placed']}/{th['anchors_placed']} "
              f"L {u['alive_L']}/{th['alive_L']} C {u['alive_C']}/{th['alive_C']} | bank {u['bank_Ad']}/{u['bank_Mn']}")


if __name__ == '__main__':
    main()
