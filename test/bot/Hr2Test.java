package c_hr2;

/** c_hr2 (c_hr1 + C.ROT_KNOWN): rotRank is 0 before SIEGE_ROTATE_FROM, while the enemy HQs are only guesses (USA: the
 *  army cycled between symmetry candidates of one HQ), and with one HQ; otherwise it steps every SIEGE_ROTATE rounds
 *  as c_hr1's did. Exits non-zero on a failure. */
public class Hr2Test {
    static int fails;

    public static void main(String[] a) {
        check(C.ROT_KNOWN, "arm on");
        check(C.SIEGE_ROTATE_FROM == 300 && C.SIEGE_ROTATE == 100, "c_hr1's rotation timing");
        check(C.HUNT, "c_hunt1's raid kept");
        check(Launcher.rotRank(299, 3, true) == 0, "before SIEGE_ROTATE_FROM: nearest");
        check(Launcher.rotRank(300, 3, true) == 1, "at SIEGE_ROTATE_FROM: second");
        check(Launcher.rotRank(399, 3, true) == 1, "still second at 399");
        check(Launcher.rotRank(400, 3, true) == 2, "third at 400");
        check(Launcher.rotRank(500, 3, true) == 0, "back to the nearest at 500");
        check(Launcher.rotRank(450, 3, false) == 0, "guessed HQs: nearest");
        check(Launcher.rotRank(1500, 3, false) == 0, "guessed HQs late: nearest");
        check(Launcher.rotRank(450, 1, true) == 0, "one HQ: 0");
        check(Launcher.rotRank(450, 1, false) == 0, "one guessed HQ: 0");
        // c_hr1's formula on known HQs, every round to 2000 and n 1..4
        for (int n = 1; n <= 4; n++)
            for (int r = 0; r <= 2000; r++) {
                int old = r < C.SIEGE_ROTATE_FROM ? 0 : (1 + (r - C.SIEGE_ROTATE_FROM) / C.SIEGE_ROTATE) % n;
                if (Launcher.rotRank(r, n, true) != old) { check(false, "c_hr1's rank at r" + r + " n" + n); n = 5; break; }
            }
        System.out.println(fails == 0 ? "Hr2Test PASS" : "Hr2Test FAIL " + fails);
        if (fails > 0) System.exit(1);
    }

    static void check(boolean ok, String what) {
        if (!ok) { fails++; System.out.println("FAIL " + what); }
    }
}
