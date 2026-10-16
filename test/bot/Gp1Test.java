package c_gp1;

import battlecode.common.MapLocation;

/** c_gp1 (c_guard1 + c_pack1) collect-square choice (Carrier.packPick). Forest (8,12) at r47 of 7415 game 4: walls at x=7, collectors
 *  on the five open neighbours, the well tile free; then Guard1Test's home-zone cases. Exits non-zero on a failure. */
public class Gp1Test {
    public static void main(String[] a) {
        check(C.PACK && C.PACK_R2 >= 8 && C.PACK_MARGIN < C.CARRIER_RETURN_LOAD, "arm on");
        MapLocation well = new MapLocation(8, 12);
        boolean[] free = new boolean[9];
        free[8] = true;   // only the well tile
        check(well.equals(Carrier.packPick(new MapLocation(8, 14), well, free)), "Forest: the well tile is the free square");
        free[8] = false;
        check(Carrier.packPick(new MapLocation(8, 14), well, free) == null, "none free: hold");
        // open well, near side (south, toward the carrier) taken: the nearest free far-side square
        boolean[] f2 = new boolean[9];
        for (int i = 0; i < 9; i++) f2[i] = true;
        f2[3] = f2[4] = f2[5] = false;   // SOUTHEAST, SOUTH, SOUTHWEST occupied
        MapLocation p = Carrier.packPick(new MapLocation(8, 9), well, f2);
        check(p.equals(well), "the well tile (r2 9) before east/west (r2 10): " + p);
        f2[8] = false;
        p = Carrier.packPick(new MapLocation(8, 9), well, f2);
        check(p.equals(new MapLocation(9, 12)) || p.equals(new MapLocation(7, 12)), "then a side square: " + p);
        // a tie between the well tile and a neighbour goes to the well tile; otherwise the nearer square
        boolean[] f3 = new boolean[9];
        f3[8] = true; f3[1] = true;   // the well tile and NORTHEAST (9,13)
        check(well.equals(Carrier.packPick(new MapLocation(11, 10), well, f3)), "tie r2 13: the well tile");
        check(new MapLocation(9, 13).equals(Carrier.packPick(new MapLocation(10, 14), well, f3)), "(9,13) at r2 2 before the well at 8");
        // c_guard1's home zone (Guard1Test)
        check(C.GUARD, "arm on");
        MapLocation[] ours = {new MapLocation(6, 23), new MapLocation(15, 3)};
        MapLocation[] ehq = {new MapLocation(53, 23), new MapLocation(44, 3)};
        MapLocation hwell = new MapLocation(16, 15);
        check(Launcher.homeZone(hwell, G.nearest(hwell, ours), ehq), "home mana well (16,15), r2 145 from (15,3)");
        MapLocation mid = new MapLocation(30, 15);
        check(!Launcher.homeZone(mid, G.nearest(mid, ours), ehq), "midfield (30,15): beyond r2 200");
        MapLocation far = new MapLocation(40, 10);
        check(!Launcher.homeZone(far, G.nearest(far, ours), ehq), "enemy half (40,10)");
        // a small map: a point within r2 200 of our HQ but nearer a predicted enemy HQ is not home
        MapLocation[] o2 = {new MapLocation(3, 3)}, e2 = {new MapLocation(16, 16)};
        MapLocation q = new MapLocation(11, 11);
        check(q.distanceSquaredTo(o2[0]) <= C.GUARD_HOME_R2 && !Launcher.homeZone(q, o2[0], e2), "nearer the enemy HQ");
        check(Launcher.homeZone(new MapLocation(8, 8), o2[0], e2), "our side of a small map");
        check(Launcher.homeZone(new MapLocation(8, 8), o2[0], new MapLocation[0]), "no enemy HQ predicted");
        check(C.GUARD_REPORT_AGE >= 19, "a 30 kg carrier's 12-tile walk home fits the report age");
        System.out.println("gp1 pack + guard home zone: " + checks + " cases ok");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
