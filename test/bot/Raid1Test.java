package c_raid1;

import battlecode.common.MapLocation;

/** c_raid1's mana raid (Launcher.addPred, theirSide, raidKey, C.RAID_MANA): a predicted mana well nearer an enemy HQ
 *  than each of ours is a raid candidate at any distance, and ranks before every well of another type. Map data from
 *  Mid1Test (the c_well9 panel replay 7601, we are side A) and the jmerle study: IslandHopping's (39,13) and (43,15),
 *  r2 125-145 from jmerle's HQ (44,3), come before its Ad well (38,7); Cornucopia's (26,34) and (32,34) are theirs, the
 *  rest of the ring is not. Exits non-zero on a failure. */
public class Raid1Test {
    public static void main(String[] a) {
        // IslandHopping, 60x30, flip x: ours (6,23), (15,3); theirs (53,23), (44,3)
        MapLocation[] ours = hq(6, 23, 15, 3), theirs = hq(53, 23, 44, 3);
        check(Launcher.theirSide(loc(39, 13), 125, ours), "IslandHopping (39,13): r2 125 from (44,3), 676 from (15,3)");
        check(Launcher.theirSide(loc(43, 15), 145, ours), "IslandHopping (43,15) is theirs");
        check(!Launcher.theirSide(loc(20, 13), 676, ours), "IslandHopping (20,13) is ours");
        check(!Launcher.theirSide(loc(23, 29), 290, hq(29, 51, 10, 18, 48, 18)), "Cornucopia (23,29): a tie is not theirs");
        check(!Launcher.theirSide(loc(1, 1), 5, null) && !Launcher.theirSide(loc(1, 1), 5, new MapLocation[0]),
            "no HQ of ours known: not theirs");

        // raidKey: mana on their side at any distance, the rest within r2 RAID_R2, other types after every mana well
        check(Launcher.raidKey(125, 2) == 125 && Launcher.raidKey(5000, 2) == 5000, "their mana: its r2, at any distance");
        check(Launcher.raidKey(52, 1) == 52 && Launcher.raidKey(52, 0) == 52 + C.RAID_OTHER, "near: mana before Ad");
        check(Launcher.raidKey(C.RAID_R2, 0) == C.RAID_R2 + C.RAID_OTHER, "r2 RAID_R2 is near, inclusive");
        check(Launcher.raidKey(C.RAID_R2 + 1, 0) == -1 && Launcher.raidKey(C.RAID_R2 + 1, 1) == -1,
            "beyond RAID_R2 only their mana counts");
        check(C.RAID_OTHER > 2 * 60 * 60, "RAID_OTHER exceeds any r2 on a 60x60 map");

        // IslandHopping end to end: wells known in the order a launcher meets them (ours, then images, one duplicate)
        MapLocation[] out = new MapLocation[40];
        int[] m = new int[40];
        int n = 0;
        n = Launcher.addPred(out, m, n, loc(20, 13), 2, theirs, ours);
        n = Launcher.addPred(out, m, n, loc(39, 13), 2, theirs, ours);
        n = Launcher.addPred(out, m, n, loc(16, 15), 2, theirs, ours);
        n = Launcher.addPred(out, m, n, loc(43, 15), 2, theirs, ours);
        n = Launcher.addPred(out, m, n, loc(21, 7), 1, theirs, ours);
        n = Launcher.addPred(out, m, n, loc(38, 7), 1, theirs, ours);
        n = Launcher.addPred(out, m, n, loc(39, 13), 2, theirs, ours);
        check(n == 3, "IslandHopping: three candidates, got " + n);
        MapLocation[] order = rank(out, m, n, loc(44, 3));
        check(order[0].equals(loc(39, 13)) && order[1].equals(loc(43, 15)) && order[2].equals(loc(38, 7)),
            "IslandHopping, target (44,3): (39,13), (43,15), then the Ad well (38,7)");

        // Cornucopia, 59x59, rotation: their HQs are the images of ours; the ring's p = .50 pair is theirs
        MapLocation[] cOurs = hq(29, 51, 10, 18, 48, 18), cTheirs = hq(29, 7, 48, 40, 10, 40);
        n = 0;
        int[] ring = {26, 24, 32, 24, 23, 29, 35, 29, 26, 34, 32, 34};
        for (int i = 0; i < ring.length; i += 2) n = Launcher.addPred(out, m, n, loc(ring[i], ring[i + 1]), 2, cTheirs, cOurs);
        n = Launcher.addPred(out, m, n, loc(17, 36), 1, cTheirs, cOurs);
        check(n == 3 && out[0].equals(loc(26, 34)) && m[0] == 2 && out[1].equals(loc(32, 34)) && m[1] == 2
            && out[2].equals(loc(17, 36)) && m[2] == 0, "Cornucopia: (26,34), (32,34) theirs, then the Ad well (17,36)");
        order = rank(out, m, n, loc(10, 40));
        check(order[0].equals(loc(26, 34)) && order[1].equals(loc(32, 34)) && order[2].equals(loc(17, 36)),
            "Cornucopia, target (10,40): the ring pair before (17,36), r2 65");

        System.out.println("mana raid: " + checks + " cases ok");
    }

    /** The candidates out[0..n) by raidKey for target hq (raidWell's order without the cleared and site tests). */
    static MapLocation[] rank(MapLocation[] out, int[] m, int n, MapLocation hq) {
        MapLocation[] r = new MapLocation[n];
        int[] k = new int[n];
        int c = 0;
        for (int i = 0; i < n; i++) {
            int key = Launcher.raidKey(out[i].distanceSquaredTo(hq), m[i]);
            if (key < 0) continue;
            int j = c++;
            while (j > 0 && k[j - 1] > key) { k[j] = k[j - 1]; r[j] = r[j - 1]; j--; }
            k[j] = key; r[j] = out[i];
        }
        return java.util.Arrays.copyOf(r, c);
    }

    static MapLocation loc(int x, int y) { return new MapLocation(x, y); }

    static MapLocation[] hq(int... xy) {
        MapLocation[] o = new MapLocation[xy.length / 2];
        for (int i = 0; i < o.length; i++) o[i] = loc(xy[2 * i], xy[2 * i + 1]);
        return o;
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
