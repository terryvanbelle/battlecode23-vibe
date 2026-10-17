package c_sym1;

import battlecode.common.MapLocation;

/** c_sym1 (c_gp1 + C.SYM_CENTROID): the knobs and Launcher.centroid (rounding, fewer than two predictions, the Quiet
 *  corner case). Exits non-zero on a failure. */
public class Sym1Test {
    static int fails;

    public static void main(String[] a) {
        check(C.SYM_CENTROID, "arm on");
        check(C.SYM_NEAR_R2 == 20, "the switch back to the nearest prediction at launcher vision (r2 20)");
        check(Launcher.centroid(new MapLocation[0]) == null, "no prediction: null");
        check(Launcher.centroid(new MapLocation[]{new MapLocation(5, 5)}) == null, "one prediction: null (siegeTarget's)");
        // Quiet, our HQ (3,3): rotation (16,16), reflections (3,16) and (16,3): centroid (11.67, 11.67) -> (12,12)
        MapLocation q = Launcher.centroid(new MapLocation[]{new MapLocation(16, 16), new MapLocation(3, 16), new MapLocation(16, 3)});
        check(q.x == 12 && q.y == 12, "Quiet from (3,3): (12,12), got " + q);
        // from (16,16): (3,3), (16,3), (3,16): (7.33, 7.33) -> (7,7)
        MapLocation r = Launcher.centroid(new MapLocation[]{new MapLocation(3, 3), new MapLocation(16, 3), new MapLocation(3, 16)});
        check(r.x == 7 && r.y == 7, "Quiet from (16,16): (7,7), got " + r);
        // halves round up: (0,0) and (1,1) -> (1,1)
        MapLocation h = Launcher.centroid(new MapLocation[]{new MapLocation(0, 0), new MapLocation(1, 1)});
        check(h.x == 1 && h.y == 1, "x.5 rounds up, got " + h);
        if (fails > 0) { System.out.println("Sym1Test: " + fails + " FAILED"); System.exit(1); }
        System.out.println("Sym1Test: all passed");
    }

    static void check(boolean ok, String what) {
        if (!ok) { fails++; System.out.println("FAIL " + what); }
    }
}
