package c_end3;

import battlecode.common.MapLocation;

/** c_end3's Launcher.endPick (c_end1 rebased onto c_bc1, then onto c_mend2; judge8b spec): attackers (id bit
 *  (id / C.END_RING_KEEP) & 1 clear) take the nearest enemy island, else one of ours; defenders take one of ours
 *  (spread by id over our islands), else the enemy island; nothing to take gives 0; islands with no known tile are
 *  skipped. Only ids that reach endPick in play are used (id % C.END_RING_KEEP != 0; the others keep the siege ring).
 *  Exits non-zero on a failure. */
public class End3Test {
    static final MapLocation HERE = new MapLocation(20, 20);

    public static void main(String[] a) {
        // owners {1:1, 2:2, 3:1, 4:0}, every island with a tile
        int[] own = {0, 1, 2, 1, 0};
        MapLocation[] tile = {null, new MapLocation(5, 5), new MapLocation(30, 30), new MapLocation(10, 40), new MapLocation(21, 21)};
        boolean saw1 = false, saw3 = false;
        int att = 0, def = 0;
        for (int id = 1; id < 4096; id++) {
            if (id % C.END_RING_KEEP == 0) continue;
            int p = Launcher.endPick(own, tile, 4, HERE, id);
            if (attacker(id)) { att++; check(p == 2, "attacker id " + id + " takes the enemy island 2, got " + p); }
            else {
                def++;
                check(p == 1 || p == 3, "defender id " + id + " takes our island 1 or 3, got " + p);
                if (p == 1) saw1 = true;
                if (p == 3) saw3 = true;
            }
        }
        check(saw1 && saw3, "defenders spread over both our islands (1 " + saw1 + ", 3 " + saw3 + ")");
        check(att > 0 && def > 0 && Math.abs(att - def) <= C.END_RING_KEEP, "attackers " + att + " and defenders " + def + " split evenly");
        // the defender's own island follows the id order of our islands, (id / (2 * END_RING_KEEP)) % nOwn
        check(Launcher.endPick(own, tile, 4, HERE, C.END_RING_KEEP + 1) == 1, "defender index 0: island 1");
        check(Launcher.endPick(own, tile, 4, HERE, 3 * C.END_RING_KEEP + 1) == 3, "defender index 1: island 3");
        // the nearest enemy island wins; a tie goes to the lower island id (no RNG)
        int[] two = {0, 2, 2, 2};
        MapLocation[] tt = {null, new MapLocation(40, 40), new MapLocation(25, 20), new MapLocation(15, 20)};
        for (int id = 1; id < 256; id++) {
            if (id % C.END_RING_KEEP == 0) continue;
            int p = Launcher.endPick(two, tt, 3, HERE, id);
            check(p == 2, "nearest enemy island (tie 2 vs 3 at r2 25 goes to 2) for id " + id + ", got " + p);
        }
        // no enemy island: attackers (and defenders) take one of ours
        int[] noEnemy = {0, 1, 0, 1};
        MapLocation[] t3 = {null, new MapLocation(5, 5), new MapLocation(30, 30), new MapLocation(10, 40)};
        for (int id = 1; id < 4096; id++) {
            if (id % C.END_RING_KEEP == 0) continue;
            int p = Launcher.endPick(noEnemy, t3, 3, HERE, id);
            check(p == 1 || p == 3, "no enemy island: id " + id + " (attacker " + attacker(id) + ") takes ours, got " + p);
        }
        // attackers with no enemy island also spread over ours by (id / (2 * END_RING_KEEP)) % nOwn
        check(Launcher.endPick(noEnemy, t3, 3, HERE, 1) == 1, "attacker id 1, no enemy island: index 0, island 1");
        check(Launcher.endPick(noEnemy, t3, 3, HERE, 2 * C.END_RING_KEEP + 1) == 3, "attacker id 9, no enemy island: index 1, island 3");
        // only ids 1..n count (endIsland passes the ids its guarded loop read): enemy island 2 beyond n = 1 is ignored
        for (int id = 1; id < 256; id++) {
            if (id % C.END_RING_KEEP == 0) continue;
            check(Launcher.endPick(own, tile, 1, HERE, id) == 1, "n = 1: id " + id + " takes our island 1");
        }
        // no own island: defenders take the enemy island
        int[] noOwn = {0, 0, 2, 0};
        for (int id = 1; id < 4096; id++) {
            if (id % C.END_RING_KEEP == 0) continue;
            check(Launcher.endPick(noOwn, t3, 3, HERE, id) == 2, "no own island: id " + id + " takes the enemy island");
        }
        // no owned and no enemy island: 0
        int[] neutral = {0, 0, 0, 0};
        for (int id = 1; id < 4096; id++) check(Launcher.endPick(neutral, t3, 3, HERE, id) == 0, "all neutral: id " + id + " gets 0");
        check(Launcher.endPick(new int[1], new MapLocation[1], 0, HERE, 5) == 0, "no islands: 0");
        // ids with null tiles are skipped: the nearer enemy island 1 has no tile, our island 2 has none either
        int[] mixed = {0, 2, 1, 2, 1};
        MapLocation[] tn = {null, null, null, new MapLocation(40, 40), new MapLocation(10, 40)};
        for (int id = 1; id < 4096; id++) {
            if (id % C.END_RING_KEEP == 0) continue;
            int p = Launcher.endPick(mixed, tn, 4, HERE, id);
            check(p == (attacker(id) ? 3 : 4), "null tiles skipped: id " + id + " (attacker " + attacker(id) + "), got " + p);
        }
        int[] allNull = {0, 2, 1};
        for (int id = 1; id < 256; id++) check(Launcher.endPick(allNull, new MapLocation[3], 2, HERE, id) == 0, "every tile null: id " + id + " gets 0");
        System.out.println("end3: endPick attackers, defenders, no enemy, nothing, null tiles: " + checks + " cases ok");
    }

    static boolean attacker(int id) { return ((id / C.END_RING_KEEP) & 1) == 0; }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("end3 FAILED: " + what); System.exit(1); }
    }
}
