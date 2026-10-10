package c_aura1;

import battlecode.common.MapLocation;

/** c_aura1's Nav.auraStepOK (research/diagnosis/2026-10-09-g_iter6.md, rank 3): inside an enemy HQ aura (r2 <= 9) a
 *  launcher may step only to a tile strictly farther from that HQ; outside, it may not step in. Cases from the
 *  reviewer's harness (2026-10-09). Exits non-zero on a failure. */
public class AuraStepTest {
    public static void main(String[] a) {
        MapLocation h = new MapLocation(10, 10);
        check(Nav.auraStepOK(new MapLocation(12, 10), new MapLocation(12, 12), h), true, "r2 4 -> 8 out");
        check(Nav.auraStepOK(new MapLocation(12, 10), new MapLocation(11, 11), h), false, "r2 4 -> 2 deeper");
        check(Nav.auraStepOK(new MapLocation(14, 10), new MapLocation(13, 10), h), false, "r2 16 -> 9 into the aura");
        check(Nav.auraStepOK(new MapLocation(13, 10), new MapLocation(13, 11), h), true, "r2 9 -> 10 out");
        check(Nav.auraStepOK(new MapLocation(12, 11), new MapLocation(12, 12), h), true, "r2 5 -> 8 farther");
        check(Nav.auraStepOK(new MapLocation(12, 12), new MapLocation(12, 11), h), false, "r2 8 -> 5 deeper");
        check(Nav.auraStepOK(new MapLocation(12, 11), new MapLocation(11, 12), h), false, "r2 5 -> 5 sideways");
        System.out.println("aura step: 7 cases ok");
    }

    static void check(boolean got, boolean want, String what) {
        if (got != want) { System.out.println("aura step FAILED: " + what + " got " + got); System.exit(1); }
    }
}
