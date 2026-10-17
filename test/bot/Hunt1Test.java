package c_hunt1;

import battlecode.common.MapLocation;

/** c_hunt1 (c_gp1 + C.HUNT): the knob; huntWell (wells beyond r2 RAID_R2 of the siege target only, nearest first,
 *  ties to the lower index, cleared wells skipped, cache rebuilt for a new hq); the hashed raided-well table against a
 *  reference map (expiry, re-clear, collisions, a full table). Exits non-zero on a failure. */
public class Hunt1Test {
    static int fails;

    public static void main(String[] a) {
        check(C.HUNT, "arm on");
        check(C.RAID_R2 == 100 && C.RAID_CLEAR_ROUNDS == 40, "c_gp1's raid radius and clear time");
        // huntWell: siege target (10,18); (14,20) is within r2 100 of it (raidWell's), the others are not
        MapLocation hq = new MapLocation(10, 18);
        MapLocation near = new MapLocation(14, 20), w1 = new MapLocation(41, 22), w2 = new MapLocation(30, 44),
            w3 = new MapLocation(42, 14);
        MapLocation[] pw = {near, w1, w2, w3};
        G.round = 100;
        reset();
        // dist2 to hq: w1 961+16 = 977, w2 400+676 = 1076, w3 1024+16 = 1040: w1 first
        check(w1.equals(Launcher.huntWell(hq, pw)), "nearest beyond RAID_R2: w1");
        Launcher.clearRaid(w1, 100);
        check(w3.equals(Launcher.huntWell(hq, pw)), "w1 cleared: w3 (1040 < 1076)");
        Launcher.clearRaid(w3, 100);
        check(w2.equals(Launcher.huntWell(hq, pw)), "w1, w3 cleared: w2");
        Launcher.clearRaid(w2, 100);
        check(Launcher.huntWell(hq, pw) == null, "all cleared: null (the ring)");
        check(Launcher.huntWell(hq, new MapLocation[]{near}) == null, "only raidWell's own wells: null");
        G.round = 140;
        check(w1.equals(Launcher.huntWell(hq, pw)), "clear expires at round + RAID_CLEAR_ROUNDS");
        // equal distances: the scan runs over indices downward, d < bd keeps the first seen (higher index), as raidWell
        MapLocation e1 = new MapLocation(20, 30), e2 = new MapLocation(22, 8);   // 100+144, 144+100 = 244 each
        reset();
        MapLocation[] tie = {e1, e2};
        check(e2.equals(Launcher.huntWell(hq, tie)), "tie: higher index first (raidWell's scan order)");
        // a new hq rebuilds the cache
        MapLocation hq2 = new MapLocation(48, 18);
        // from (48,18): e1 784+144 = 928, e2 676+100 = 776: e2; then hq again: e2 (tie order), then from hq2 with e2
        // cleared: e1
        check(e2.equals(Launcher.huntWell(hq2, tie)), "new hq: nearest from (48,18) is e2");
        Launcher.clearRaid(e2, G.round);
        check(e1.equals(Launcher.huntWell(hq2, tie)), "new hq, e2 cleared: e1");
        check(e1.equals(Launcher.huntWell(hq, tie)), "back to the first hq: cache rebuilt, e2 still cleared: e1");
        // the hashed table vs a reference over many locations, rounds and collisions
        reset();
        java.util.HashMap<Integer, Integer> ref = new java.util.HashMap<>();
        java.util.Random r = new java.util.Random(7);
        for (int t = 0; t < 3000; t++) {
            G.round = 200 + t / 10;
            MapLocation l = new MapLocation(r.nextInt(8) * 8, r.nextInt(6));   // 48 keys, many share y
            if (r.nextInt(3) == 0) { Launcher.clearRaid(l, G.round); ref.put(G.enc(l), G.round + C.RAID_CLEAR_ROUNDS); }
            MapLocation q = new MapLocation(r.nextInt(8) * 8, r.nextInt(6));
            Integer u = ref.get(G.enc(q));
            boolean want = u != null && G.round < u;
            if (Launcher.cleared(q) != want) { check(false, "hash table vs reference at " + q + " round " + G.round); break; }
        }
        check(Launcher.nCleared == ref.size(), "distinct entries " + Launcher.nCleared + " = " + ref.size());
        // a full table (64 keys) still answers for the last key cleared and never loops
        reset();
        for (int k = 0; k < 70; k++) Launcher.clearRaid(new MapLocation(k % 60, k / 60), 300);
        G.round = 300;
        check(Launcher.cleared(new MapLocation(9, 1)), "full table: the last key is found");
        check(!Launcher.cleared(new MapLocation(59, 59)), "full table: an absent key is not cleared");
        if (fails > 0) { System.out.println("Hunt1Test: " + fails + " FAILED"); System.exit(1); }
        System.out.println("Hunt1Test: all passed");
    }

    static void reset() {
        java.util.Arrays.fill(Launcher.clKey, 0);
        java.util.Arrays.fill(Launcher.clUntil, 0);
        Launcher.nCleared = 0;
        Launcher.hcPred = null;
    }

    static void check(boolean ok, String what) {
        if (!ok) { fails++; System.out.println("FAIL " + what); }
    }
}
