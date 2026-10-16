package c_sim1;

/** c_sim1's engagement test (Launcher.simKeep, C.SIM_KEEP): percent of our shots-to-kill left after a focus-fire
 *  simulation, -1 when we do not win it. Full-health calibration against the count rule, mutual destruction, unsorted
 *  input, and the Cat case (c_well9 panel match 7600 game 1, r45: three of ours at 180/200/120 HP against six at
 *  20/20/40/180/20/80, a fight the count rule refused). Exits non-zero on a failure. */
public class Sim1Test {
    public static void main(String[] x) {
        check(C.SIM_KEEP == 60 && C.SIM_STAND == 1 && C.SIM_MIN_LEFT == 5000, "constants");
        check(full(2, 1) == 75 && full(3, 2) == 63 && full(4, 3) == 55, "one ahead keeps 75 / 63 / 55");
        check(full(3, 1) == 86 && full(4, 2) == 80 && full(5, 3) == 74 && full(6, 4) == 66, "two ahead keeps 86 / 80 / 74 / 66");
        for (int n = 1; n <= 8; n++) check(full(n, n) == -1, "equal numbers annihilate: " + n);
        check(full(1, 2) == -1 && full(3, 5) == -1, "behind loses");
        check(Launcher.simKeep(new int[]{10}, 1, new int[12], 0) == 100, "no enemy fighter");
        check(Launcher.simKeep(new int[]{10}, 1, new int[]{9}, 1) == 10, "one v one, one shot more");
        check(Launcher.simKeep(new int[]{9, 10, 6}, 3, new int[]{1, 1, 2, 9, 1, 4}, 6) == 20, "Cat r45: won, keeps 20");
        check(Launcher.simKeep(new int[]{6, 10, 9}, 3, new int[]{4, 9, 1, 2, 1, 1}, 6) == 20, "order does not matter");
        check(Launcher.simKeep(new int[]{1, 1, 1}, 3, new int[]{10}, 1) == -1, "three one-shot launchers lose to one healthy");
        check(Launcher.simKeep(new int[]{10, 10}, 2, new int[]{1, 1, 1}, 3) == 80, "two healthy beat three one-shot (keep 80)");
        // the count rule (AHEAD_MIN 2) refuses the Cat case and 3 v 2; SIM_KEEP 60 takes 3 v 2 and still refuses Cat
        check(3 - 6 < C.AHEAD_MIN && 3 - 2 < C.AHEAD_MIN, "count rule refuses both");
        check(full(3, 2) >= C.SIM_KEEP && Launcher.simKeep(new int[]{9, 10, 6}, 3, new int[]{1, 1, 2, 9, 1, 4}, 6) < C.SIM_KEEP,
            "SIM_KEEP 60: 3 v 2 yes, Cat no");
        System.out.println("fight simulation: " + checks + " cases ok");
    }

    static int full(int a, int b) {
        int[] x = new int[12], y = new int[12];
        for (int i = 0; i < a; i++) x[i] = 10;
        for (int i = 0; i < b; i++) y[i] = 10;
        return Launcher.simKeep(x, a, y, b);
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
