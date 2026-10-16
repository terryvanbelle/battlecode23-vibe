package c_front1;

import battlecode.common.MapLocation;

/** c_front1's midfield front (Launcher.frontPct, frontPoint; C.FRONT, ported from arch_jm): the share of the way from
 *  our HQ centroid to the siege target by round, and the point itself on IslandHopping (our HQs (6,23), (15,3), the
 *  target (44,3)) with no wall known. Exits non-zero on a failure. */
public class Front1Test {
    public static void main(String[] a) {
        check(Launcher.frontPct(0) == 50 && Launcher.frontPct(149) == 50, "50% before r150");
        check(Launcher.frontPct(150) == 60 && Launcher.frontPct(224) == 60, "60% from r150");
        check(Launcher.frontPct(225) == 70 && Launcher.frontPct(300) == 80 && Launcher.frontPct(374) == 80, "70%, 80%");
        check(Launcher.frontPct(375) > C.FRONT_MAX, "past FRONT_MAX from r375: the raid and the ring resume");
        G.W = 60; G.H = 30;
        HQState.ourHQs = new MapLocation[] {new MapLocation(6, 23), new MapLocation(15, 3)};
        MapLocation hq = new MapLocation(44, 3);
        check(Launcher.frontPoint(hq, 50).equals(new MapLocation(27, 8)), "IslandHopping r0: (27,8), got " + Launcher.frontPoint(hq, 50));
        check(Launcher.frontPoint(hq, 80).equals(new MapLocation(37, 5)), "IslandHopping r300: (37,5), got " + Launcher.frontPoint(hq, 80));
        check(Launcher.frontPoint(hq, 80) == Launcher.frontPoint(hq, 80), "the point is cached while unchanged");
        System.out.println("front: " + checks + " cases ok");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
