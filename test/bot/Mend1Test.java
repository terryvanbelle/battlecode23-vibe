package c_mend1;

/** c_mend1's Launcher.mendScore (fight() tile score while mending): threat dominates distance; a zero-threat tile that
 *  can hit beats a nearer one that cannot only when the action is ready; at equal threat and hit the tile nearer the
 *  mending tile wins; the distance term is capped at dist2 400. Launcher.mendDue (when the island loop runs): at
 *  C.MEND_HP or less or while mending, once the re-check round is reached, never before C.ANCHOR_START and only with
 *  C.MEND_MIN_LEFT bytecodes left. Exits non-zero on a failure. */
public class Mend1Test {
    public static void main(String[] a) {
        // threat dominates: threat 0 far beats threat 1 near (both ways of hitting)
        check(Launcher.mendScore(false, false, 0, 400) > Launcher.mendScore(false, false, 1, 0), "threat 0 far > threat 1 near");
        check(Launcher.mendScore(true, false, 0, 10_000) > Launcher.mendScore(true, true, 1, 0), "threat 0 far > threat 1 near hitting");
        check(Launcher.mendScore(true, true, 1, 0) > Launcher.mendScore(true, true, 2, 0), "threat 1 > threat 2");
        // at threat 0 a hitting tile beats a nearer non-hitting tile only when ready
        check(Launcher.mendScore(true, true, 0, 300) > Launcher.mendScore(true, false, 0, 0), "ready: hitting far > not hitting near");
        check(Launcher.mendScore(false, true, 0, 300) < Launcher.mendScore(false, false, 0, 0), "not ready: nearer wins");
        // the hit bonus needs zero threat: at threat 1 hitting is worth nothing
        check(Launcher.mendScore(true, true, 1, 300) < Launcher.mendScore(true, false, 1, 0), "threat 1: no hit bonus");
        // equal threat and hit: nearer the mending tile wins
        check(Launcher.mendScore(true, true, 0, 4) > Launcher.mendScore(true, true, 0, 5), "nearer wins (hitting)");
        check(Launcher.mendScore(false, false, 1, 0) > Launcher.mendScore(false, false, 1, 1), "nearer wins (threat 1)");
        // the distance term is capped at 400
        check(Launcher.mendScore(false, false, 0, 400) == Launcher.mendScore(false, false, 0, 5000), "cap at 400");
        check(Launcher.mendScore(false, false, 0, 399) > Launcher.mendScore(false, false, 0, 400), "399 > 400");
        check(Launcher.mendScore(false, false, 0, 0) == 0L, "zero");
        check(Launcher.mendScore(true, true, 0, 400) == 1_000_000L - 1200L, "ready hit far value");
        // one dist2 unit is worth 3 (fight() then adds CENTER +1 and G.rand(3), unchanged)
        check(Launcher.mendScore(false, false, 0, 3) - Launcher.mendScore(false, false, 0, 4) == 3L, "one dist2 unit is 3");

        // mendDue: the island loop's gate (r = a round from C.ANCHOR_START, L = a full budget)
        int r = C.ANCHOR_START + 100, L = 10_000, hp = C.MEND_HP;
        check(Launcher.mendDue(hp, false, r, 0, L), "wounded at MEND_HP: due");
        check(!Launcher.mendDue(hp + 1, false, r, 0, L), "above MEND_HP, not mending: not due");
        check(Launcher.mendDue(C.MEND_FULL - 1, true, r, 0, L), "mending above MEND_HP: due");
        check(!Launcher.mendDue(hp, false, r, r + 1, L), "before the re-check round: not due");
        check(Launcher.mendDue(hp, false, r, r, L), "at the re-check round: due");
        check(!Launcher.mendDue(1, false, C.ANCHOR_START - 1, 0, L), "before ANCHOR_START no island is ours: not due");
        check(!Launcher.mendDue(1, true, C.ANCHOR_START - 1, 0, L), "before ANCHOR_START, even if mending: not due");
        check(Launcher.mendDue(1, false, C.ANCHOR_START, 0, L), "at ANCHOR_START: due");
        check(!Launcher.mendDue(hp, true, r, 0, C.MEND_MIN_LEFT - 1), "short turn: deferred");
        check(Launcher.mendDue(hp, true, r, 0, C.MEND_MIN_LEFT), "MEND_MIN_LEFT left: due");
        // the deferral is safe: the loop's own guard never cuts a 35-id pass started with MEND_MIN_LEFT
        check(C.MEND_MIN_LEFT - 35 * 70 - 300 > C.ISLAND_LOOP_GUARD, "MEND_MIN_LEFT covers 35 owned ids at 70 + nearestEnemy");
        System.out.println("mend score and gate: " + checks + " cases ok");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("mend FAILED: " + what); System.exit(1); }
    }
}
