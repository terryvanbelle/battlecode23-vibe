package c_well5;

import battlecode.common.MapLocation;

/** c_well5's Carrier.probeFront (research/diagnosis/2026-10-10-g_iter8.md, c_well5 (4)): the front point is the
 *  midpoint toward the nearest enemy HQ, pulled in to C.PROBE_TOWARD; the front probe needs it at least
 *  C.PROBE_FRONT_MIN from home. Map data from the engine's Forest and Cornucopia (diag/map.py). Exits non-zero on a
 *  failure. */
public class ProbeFrontTest {
    public static void main(String[] a) {
        // Forest: our (11,48); their HQs (59,0), (53,30), (52,30), (48,48): (48,48) is nearest (d2 1369)
        MapLocation home = new MapLocation(11, 48);
        MapLocation f = Carrier.probeFront(home, new MapLocation[]{new MapLocation(59, 0), new MapLocation(53, 30),
            new MapLocation(52, 30), new MapLocation(48, 48)});
        check(new MapLocation(29, 48).equals(f), "Forest (11,48) -> (29,48), got " + f);
        check(G.cheb(home, f) >= C.PROBE_FRONT_MIN, "Forest front cheb 18 passes PROBE_FRONT_MIN");
        // Cornucopia: our (29,51); their HQs (48,40), (29,7), (10,40): (48,40) and (10,40) tie at d2 482
        home = new MapLocation(29, 51);
        // the tie goes to the last candidate in array order, (10,40) -> (20,46), with no RNG draw (the gate runs on
        // every early mana carrier: a draw would shift the RNG stream on maps where the probe never fires)
        int rng0 = rng(12345);
        f = Carrier.probeFront(home, new MapLocation[]{new MapLocation(48, 40), new MapLocation(29, 7), new MapLocation(10, 40)});
        check(rng(rng0) == 12345, "probeFront drew from the RNG on a tie");
        check(new MapLocation(20, 46).equals(f), "Cornucopia tie -> (20,46), got " + f);
        check(f != null && G.cheb(home, f) == 9, "Cornucopia (29,51) -> cheb 9, got " + f);
        check(G.cheb(home, f) < C.PROBE_FRONT_MIN, "Cornucopia front stays under PROBE_FRONT_MIN (centre-first explore)");
        // clamp to C.PROBE_TOWARD: (0,0) toward (59,59), midpoint (29,29) cheb 29 -> (18,18)
        f = Carrier.probeFront(new MapLocation(0, 0), new MapLocation[]{new MapLocation(59, 59)});
        check(new MapLocation(C.PROBE_TOWARD, C.PROBE_TOWARD).equals(f), "clamp (0,0)->(59,59) gives (18,18), got " + f);
        check(Carrier.probeFront(home, new MapLocation[0]) == null, "no enemy HQ: null");
        System.out.println("probe front: 8 cases ok");
    }

    /** Sets G's private RNG state (reflection) and returns the previous one. */
    static int rng(int v) {
        try {
            java.lang.reflect.Field fl = G.class.getDeclaredField("rng");
            fl.setAccessible(true);
            int was = fl.getInt(null);
            fl.setInt(null, v);
            return was;
        } catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
    }

    static void check(boolean ok, String what) {
        if (!ok) { System.out.println("probe front FAILED: " + what); System.exit(1); }
    }
}
