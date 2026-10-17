package c_mn1;

/** c_mn1 (c_expl1 + no dead-end well choice): the knobs, Carrier.tripDrop's truth table (a fallback well lasts one
 *  trip only once a well of the role is known) and Carrier.bankNoWell's threshold. Exits non-zero on a failure. */
public class Mn1Test {
    static int fails;

    public static void main(String[] a) {
        // 1. knobs
        check(C.MN_TRIP && C.MN_AVOID_JUMP && C.MN_BANK, "arms on");
        check(C.ROLES == 3, "tripDrop acts under the role split (ROLES 3)");
        check(C.MN_BANK_MIN > 0 && C.MN_BANK_MIN < C.CARRIER_RETURN_LOAD, "bank threshold between empty and a full load");
        check(C.HOT_KEEP_MN && C.EXPL, "built on c_keep2 and c_expl1");

        // 2. tripDrop: only a fallback well with a role well known is dropped
        check(Carrier.tripDrop(true, true), "fallback + role known: drop");
        check(!Carrier.tripDrop(true, false), "fallback, no role well known: keep (a drop restarts the 60-turn search)");
        check(!Carrier.tripDrop(false, true), "role well: keep");
        check(!Carrier.tripDrop(false, false), "no fallback, nothing known: keep");

        // 3. bankNoWell: at and above the threshold only
        check(!Carrier.bankNoWell(0), "empty: explore");
        check(!Carrier.bankNoWell(C.MN_BANK_MIN - 1), "below the threshold: explore");
        check(Carrier.bankNoWell(C.MN_BANK_MIN), "at the threshold: bank");
        check(Carrier.bankNoWell(C.CARRIER_RETURN_LOAD), "full: bank");

        // 4. the flag starts clear
        check(!Carrier.fallback, "fallback starts false");
        if (fails > 0) { System.out.println("Mn1Test: " + fails + " FAILED"); System.exit(1); }
        System.out.println("Mn1Test: all passed");
    }

    static void check(boolean ok, String what) {
        if (!ok) { fails++; System.out.println("FAIL " + what); }
    }
}
