package c_spread2;

import battlecode.common.MapLocation;

/** c_spread2's Launcher.spreadNext (judge8 spec): a launcher leaving a saturated ring goes to another enemy HQ, never
 *  to its current one nor to one within r2 C.SPREAD_SAME_R2 of it, and the id bits spread a ring over every other HQ.
 *  Exits non-zero on a failure. */
public class SpreadTest {
    public static void main(String[] a) {
        // Cornucopia: the team target (10,40); the other two enemy HQs are (48,40) and (29,7)
        MapLocation cur = new MapLocation(10, 40);
        MapLocation[] corn = {new MapLocation(48, 40), new MapLocation(29, 7), new MapLocation(10, 40)};
        boolean sawA = false, sawB = false;
        for (int id = 0; id < 4096; id++) for (int hops = 0; hops < 3; hops++) {
            MapLocation n = Launcher.spreadNext(corn, cur, id, hops);
            if (n == null || n.equals(cur)) fail("Cornucopia id " + id + " hops " + hops + " got " + n);
            if (n.equals(corn[0])) sawA = true;
            if (n.equals(corn[1])) sawB = true;
        }
        if (!sawA || !sawB) fail("Cornucopia: both other HQs over ids (48,40) " + sawA + " (29,7) " + sawB);
        // Forest: (53,30) is the same front as (52,30)
        MapLocation f = new MapLocation(52, 30);
        MapLocation[] forest = {new MapLocation(53, 30), new MapLocation(52, 30), new MapLocation(7, 19)};
        for (int id = 0; id < 4096; id++) {
            MapLocation n = Launcher.spreadNext(forest, f, id, 0);
            if (n == null || n.equals(f) || n.equals(forest[0])) fail("Forest id " + id + " got " + n);
        }
        // a single HQ: nowhere to spread
        if (Launcher.spreadNext(new MapLocation[]{cur}, cur, 12345, 0) != null) fail("single HQ: not null");
        // duplicates (enemyHQs() repeats the set per agreeing symmetry candidate) count once
        MapLocation[] dup = {corn[0], corn[1], corn[2], corn[0], corn[1], corn[2]};
        for (int id = 0; id < 256; id++) {
            MapLocation n = Launcher.spreadNext(dup, cur, id, 0);
            MapLocation want = Launcher.spreadNext(corn, cur, id, 0);
            if (n == null || !n.equals(want)) fail("duplicates id " + id + " got " + n + " want " + want);
        }
        System.out.println("spread: Cornucopia, Forest, single HQ, duplicates ok");
    }

    static void fail(String what) { System.out.println("spread FAILED: " + what); System.exit(1); }
}
