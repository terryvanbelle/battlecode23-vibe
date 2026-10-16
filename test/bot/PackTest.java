package c_pack1;

import battlecode.common.MapLocation;

/** c_pack1's collect-square choice (Carrier.packPick). Forest (8,12) at r47 of 7415 game 4: walls at x=7, collectors
 *  on the five open neighbours, the well tile free. Exits non-zero on a failure. */
public class PackTest {
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
        System.out.println("pack: " + checks + " cases ok");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
