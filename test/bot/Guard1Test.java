package c_guard1;

import battlecode.common.MapLocation;

/** c_guard1's home zone (Launcher.homeZone, C.GUARD_HOME_R2) on IslandHopping as side A (c_well9 panel match 7601
 *  game 6): our HQs (6,23) and (15,3), jmerle's (53,23) and (44,3). The home mana well (16,15), where jmerle's launchers
 *  stood while our Mn stalled, is in the zone; the midfield and the enemy half are not. Exits non-zero on a failure. */
public class Guard1Test {
    public static void main(String[] a) {
        check(C.GUARD, "arm on");
        MapLocation[] ours = {new MapLocation(6, 23), new MapLocation(15, 3)};
        MapLocation[] ehq = {new MapLocation(53, 23), new MapLocation(44, 3)};
        MapLocation well = new MapLocation(16, 15);
        check(Launcher.homeZone(well, G.nearest(well, ours), ehq), "home mana well (16,15), r2 145 from (15,3)");
        MapLocation mid = new MapLocation(30, 15);
        check(!Launcher.homeZone(mid, G.nearest(mid, ours), ehq), "midfield (30,15): beyond r2 200");
        MapLocation far = new MapLocation(40, 10);
        check(!Launcher.homeZone(far, G.nearest(far, ours), ehq), "enemy half (40,10)");
        // a small map: a point within r2 200 of our HQ but nearer a predicted enemy HQ is not home
        MapLocation[] o2 = {new MapLocation(3, 3)}, e2 = {new MapLocation(16, 16)};
        MapLocation p = new MapLocation(11, 11);
        check(p.distanceSquaredTo(o2[0]) <= C.GUARD_HOME_R2 && !Launcher.homeZone(p, o2[0], e2), "nearer the enemy HQ");
        check(Launcher.homeZone(new MapLocation(8, 8), o2[0], e2), "our side of a small map");
        check(Launcher.homeZone(new MapLocation(8, 8), o2[0], new MapLocation[0]), "no enemy HQ predicted");
        check(C.GUARD_REPORT_AGE >= 19, "a 30 kg carrier's 12-tile walk home fits the report age");
        System.out.println("guard home zone: " + checks + " cases ok");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
