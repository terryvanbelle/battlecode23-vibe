package c_open1;

/** c_open1 is c_mend2 with a carrier-first opening through round C.CARRIER_FIRST_UNTIL; nothing else changes. */
public final class Open1Test {
    public static void main(String[] args) {
        if (C.CARRIER_FIRST_UNTIL != 10) throw new AssertionError("carrier first through round 10");
        if (!(C.CAP_MAX == c_mend2.C.CAP_MAX && C.OPENING_ROUNDS == c_mend2.C.OPENING_ROUNDS && C.AD_EARLY_EVERY == c_mend2.C.AD_EARLY_EVERY
              && C.HQ_THREAT == c_mend2.C.HQ_THREAT)) throw new AssertionError("other constants as c_mend2");
        System.out.println("open1: 2 cases ok");
    }
}
