package c_rally1;

/** c_rally1's step after a shot (Launcher.kiteScore, C.KITE_RALLY): fewest threats first, then distance from the
 *  nearest enemy fighter (capped at r2 50) against distance to the rally point (capped at r2 400), the parity
 *  fallback's weights. A 9-tile case from Cat (c_well9 panel match 7600 game 1): out of reach of a fighter to the south-east,
 *  the old score walks on away from it, c_rally1's toward the rally point, our HQ (14,34). Exits non-zero on a failure. */
public class Rally1Test {
    public static void main(String[] a) {
        check(C.KITE_RALLY && C.RALLY_HOME, "both arms on");
        check(Launcher.kiteScore(0, 0, 400) > Launcher.kiteScore(1, 50, 0), "a threat outweighs every distance");
        check(Launcher.kiteScore(0, 80, 10) > Launcher.kiteScore(0, 200, 30), "beyond r2 50 the rally decides");
        check(Launcher.kiteScore(0, 16, 100) < Launcher.kiteScore(0, 34, 100), "same rally distance: farther from the enemy");
        check(Launcher.kiteScore(0, 60, 400) == Launcher.kiteScore(0, 50, 900), "both caps");

        // launcher at (21,36) after its shot; enemy fighter at (27,33), r2 45 (out of reach, THREAT_R2 26); rally (14,34)
        int[] e = {27, 33}, r = {14, 34};
        int hx = 21, hy = 36, oldBest = -1, newBest = -1;
        long oldS = Long.MIN_VALUE, newS = Long.MIN_VALUE;
        int[][] d = {{0, 0}, {0, 1}, {1, 1}, {1, 0}, {1, -1}, {0, -1}, {-1, -1}, {-1, 0}, {-1, 1}};
        for (int k = 0; k < 9; k++) {
            int tx = hx + d[k][0], ty = hy + d[k][1];
            int md = (tx - e[0]) * (tx - e[0]) + (ty - e[1]) * (ty - e[1]);
            int threat = md <= C.THREAT_R2 ? 1 : 0;
            int rd = (tx - r[0]) * (tx - r[0]) + (ty - r[1]) * (ty - r[1]);
            long so = -threat * 10_000L + Math.min(md, 100) * 10 + (k == 0 ? 1 : 0);
            long sn = Launcher.kiteScore(threat, md, rd) + (k == 0 ? 1 : 0);
            if (so > oldS) { oldS = so; oldBest = k; }
            if (sn > newS) { newS = sn; newBest = k; }
        }
        check(d[oldBest][0] == -1 && d[oldBest][1] == 1, "old score: north-west, away from the fighter (got " + oldBest + ")");
        check(d[newBest][0] == -1 && d[newBest][1] == -1, "c_rally1: south-west, toward (14,34) (got " + newBest + ")");
        System.out.println("rally kite: " + checks + " cases ok");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
