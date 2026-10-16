package c_guard2;

import battlecode.common.MapLocation;

/** c_guard2's sentry: its post (Amplifier.sentryPost) beyond the home mana well and the HQ's build rule
 *  (HQ.sentryWanted). IslandHopping as side A (c_well9 panel match 7601 game 6): HQ (15,3), home mana well (16,15).
 *  Exits non-zero on a failure. */
public class Guard2Test {
    public static void main(String[] a) {
        check(C.SENTRY && C.GUARD, "arms on");
        MapLocation hq = new MapLocation(15, 3), well = new MapLocation(16, 15);
        MapLocation p = Amplifier.sentryPost(hq, well, C.SENTRY_OUT, 60, 30);
        check(p.equals(new MapLocation(16, 18)), "post 3 tiles beyond (16,15) away from the HQ: " + p);
        check(Amplifier.sentryPost(new MapLocation(5, 5), new MapLocation(1, 1), 3, 30, 30).equals(new MapLocation(0, 0)),
                "clamped to the map corner");
        check(Amplifier.sentryPost(well, well, 3, 60, 30).equals(well), "well on the HQ: the well");
        check(Amplifier.sentryPost(new MapLocation(10, 10), new MapLocation(10, 18), 3, 20, 20).equals(new MapLocation(10, 19)),
                "clamped to the top edge");
        int d = hq.distanceSquaredTo(well);   // 145
        check(HQ.sentryWanted(false, 1000, false, d), "no heartbeat, well at r2 145: build");
        check(!HQ.sentryWanted(true, 1000, false, d), "heartbeat set: a sentry lives");
        check(!HQ.sentryWanted(false, C.SENTRY_CHECK - 1, false, d), "built since the last check (no beat yet)");
        check(!HQ.sentryWanted(false, 1000, true, d), "HQ threatened");
        check(!HQ.sentryWanted(false, 1000, false, 20), "well in the HQ's vision");
        check(!HQ.sentryWanted(false, 1000, false, C.GUARD_HOME_R2 + 1), "well beyond the home zone");
        check(!HQ.sentryWanted(false, 1000, false, 0), "no known well");
        check(C.SENTRY_SHIFT + 3 <= 15, "4 HQ heartbeat bits fit the flags word");
        System.out.println("guard2 sentry: " + checks + " cases ok");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
