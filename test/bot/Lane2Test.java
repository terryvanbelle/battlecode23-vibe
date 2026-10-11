package c_lane2;

import battlecode.common.Clock;
import battlecode.common.MapLocation;

/** c_lane2 (c_lane1 rebased on c_bc1): c_lane1's siege target helpers: Launcher.laneTarget (the enemy HQ nearest any
 *  of ours, ties by d2 to the centroid, then G.enc) against Launcher.centroidTarget (today's rank-0 rule: nearest the centroid, ties by G.enc). Map data
 *  from the judge's spec (engine maps): on Forest the two rules differ under both symmetry states, on Cornucopia,
 *  DefaultMap, Maze and decided MassiveL they agree (the lane branch then leaves siegeTarget's loop to run as before).
 *  Neither helper draws from the RNG. Also siegeTarget's lane branch on a short turn (siegeShortTurn). Exits non-zero
 *  on a failure. */
public class Lane2Test {
    public static void main(String[] a) {
        int rng0 = rng(12345);
        // Forest: ours (0,0), (6,30), (7,30), (11,48), centroid (6,27)
        MapLocation[] ours = {L(0, 0), L(6, 30), L(7, 30), L(11, 48)};
        MapLocation from = L(6, 27);
        check(from.equals(centroid(ours)), "Forest centroid (6,27)");
        MapLocation[] rotFx = {L(59, 59), L(53, 29), L(52, 29), L(48, 11), L(59, 0), L(53, 30), L(52, 30), L(48, 48)};
        both(ours, rotFx, from, L(48, 48), L(48, 11), "Forest ROT+FX");
        MapLocation[] fx = {L(59, 0), L(53, 30), L(52, 30), L(48, 48)};
        both(ours, fx, from, L(48, 48), L(52, 30), "Forest FX");
        // array order does not matter (ties are broken by location, never by order)
        MapLocation[] rev = new MapLocation[rotFx.length];
        for (int i = 0; i < rev.length; i++) rev[i] = rotFx[rotFx.length - 1 - i];
        both(ours, rev, from, L(48, 48), L(48, 11), "Forest ROT+FX reversed");
        // Cornucopia: every m ties at 482, (48,40) and (10,40) tie at d2 482 from (29,29): G.enc picks (10,40)
        ours = new MapLocation[]{L(29, 51), L(48, 18), L(10, 18)};
        MapLocation[] cor = {L(48, 40), L(29, 7), L(10, 40)};
        both(ours, cor, L(29, 29), L(10, 40), L(10, 40), "Cornucopia");
        both(ours, new MapLocation[]{L(10, 40), L(29, 7), L(48, 40)}, L(29, 29), L(10, 40), L(10, 40), "Cornucopia reversed");
        // DefaultMap: (18,8) and (6,13) tie at m 149, (6,13) nearer the centroid
        both(new MapLocation[]{L(4, 26), L(13, 23), L(25, 18)}, new MapLocation[]{L(27, 5), L(18, 8), L(6, 13)}, L(14, 22),
            L(6, 13), L(6, 13), "DefaultMap");
        // Maze
        both(new MapLocation[]{L(11, 2), L(3, 46), L(21, 21)}, new MapLocation[]{L(38, 47), L(46, 3), L(28, 28)}, L(11, 23),
            L(28, 28), L(28, 28), "Maze");
        // MassiveL decided (ROT, 40x40): (32,34) and (37,2) tie at m 909, (32,34) nearer the centroid
        MapLocation[] ml = {L(7, 5), L(2, 37)};
        both(ml, new MapLocation[]{L(32, 34), L(37, 2)}, L(4, 21), L(32, 34), L(32, 34), "MassiveL decided");
        // ... and why the gate (C.LANE_MIN_HQS or MapMem.decided()) exists: undecided ROT+FX MassiveL would flip to (32,5)
        both(ml, new MapLocation[]{L(32, 34), L(37, 2), L(32, 5), L(37, 37)}, L(4, 21), L(32, 5), L(32, 34),
            "MassiveL undecided (gated off: 2 HQs)");
        check(ml.length < C.LANE_MIN_HQS && 3 >= C.LANE_MIN_HQS, "the gate admits 3-HQ maps, not 2-HQ maps");
        // degenerate inputs
        check(Launcher.laneTarget(ours, new MapLocation[0], from) == null, "laneTarget of no enemy HQ: null");
        check(Launcher.centroidTarget(new MapLocation[0], from) == null, "centroidTarget of no enemy HQ: null");
        check(L(9, 9).equals(Launcher.laneTarget(new MapLocation[]{L(0, 0)}, new MapLocation[]{L(9, 9)}, from)), "one HQ");
        siegeShortTurn();
        check(rng(rng0) == 12345, "a helper or siegeTarget drew from the RNG");
        System.out.println("lane: " + checks + " cases ok");
    }

    /** siegeTarget's lane branch on a short turn. Outside the engine Clock.getBytecodesLeft() is 0, below C.LANE_GUARD,
     *  so the recompute never runs here: with no cached lane target the base loop answers (the centroid rule) and the
     *  key stays unset; a cached target stands until a call with bytecodes to spare; no own HQs, or a rotated rank, skip
     *  the branch. Forest ROT+FX, as above. */
    static void siegeShortTurn() {
        if (Clock.getBytecodesLeft() >= C.LANE_GUARD) { System.out.println("lane: Clock live, short-turn cases skipped"); return; }
        G.W = 60; G.H = 60; G.round = 100; G.here = L(6, 27);
        HQState.ourHQs = new MapLocation[]{L(0, 0), L(6, 30), L(7, 30), L(11, 48)};
        MapMem.cand = MapMem.ROT | MapMem.FLIP_X;
        MapMem.nEnemyHQSeen = 0;
        MapLocation[] ehq = MapMem.enemyHQs();
        check(ehq.length == 8, "Forest ROT+FX predicts 8 enemy HQs, got " + ehq.length);
        Launcher.laneKey = -1; Launcher.laneHQ = null; Launcher.laneDiff = false;
        MapLocation t = Launcher.siegeTarget(ehq);
        check(L(48, 11).equals(t) && Launcher.laneKey == -1 && !Launcher.laneDiff, "short turn, nothing cached: base loop (48,11), got " + t);
        Launcher.laneHQ = L(48, 48); Launcher.laneDiff = true;
        t = Launcher.siegeTarget(ehq);
        check(L(48, 48).equals(t) && Launcher.laneKey == -1, "short turn: the cached lane target (48,48) stands, got " + t);
        // c_lane2: the first call primed c_bc1's result cache with the centroid answer for these same arrays and rank;
        // the lane branch runs ahead of it, so the cache cannot mask the lane target
        check(Launcher.stEhq == ehq && Launcher.stRank == 0 && L(48, 11).equals(Launcher.stHq),
            "c_bc1 cache not primed with (48,11) for the same ehq and rank, so the cached-lane check above proves no order");
        G.round = C.SIEGE_ROTATE_FROM;                    // rank 1: the branch is off; the second nearest the centroid
        t = Launcher.siegeTarget(ehq);
        check(L(52, 29).equals(t), "rotation rank 1 ignores the lane: (52,29), got " + t);
        G.round = 100;
        HQState.ourHQs = null;                            // no own HQs: centroid G.here, branch skipped despite the cache
        t = Launcher.siegeTarget(ehq);
        check(L(48, 11).equals(t), "no own HQs: base loop (48,11), got " + t);
        Launcher.laneHQ = null; Launcher.laneDiff = false; MapMem.cand = 7; G.round = 0; G.here = null;
    }

    static MapLocation L(int x, int y) { return new MapLocation(x, y); }

    static MapLocation centroid(MapLocation[] o) {
        int x = 0, y = 0;
        for (MapLocation l : o) { x += l.x; y += l.y; }
        return new MapLocation(x / o.length, y / o.length);
    }

    static void both(MapLocation[] ours, MapLocation[] ehq, MapLocation from, MapLocation lane, MapLocation cen, String what) {
        MapLocation l = Launcher.laneTarget(ours, ehq, from), c = Launcher.centroidTarget(ehq, from);
        check(lane.equals(l), what + ": laneTarget " + lane + ", got " + l);
        check(cen.equals(c), what + ": centroidTarget " + cen + ", got " + c);
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

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("lane FAILED: " + what); System.exit(1); }
    }
}
