package c_ad1;

/** c_ad1 is c_mend2 with one carrier in 4 (was 8) mining adamantium while its HQ asks for it (Ad@250 252 vs 516). */
public final class Ad1Test {
    public static void main(String[] args) {
        if (!(C.AD_EARLY_EVERY == 4 && c_mend2.C.AD_EARLY_EVERY == 8)) throw new AssertionError("early Ad share 1/8 -> 1/4");
        if (!(C.AD_NEED == c_mend2.C.AD_NEED && C.AD_LATE_EVERY == c_mend2.C.AD_LATE_EVERY && C.AD_ROLE_FROM == c_mend2.C.AD_ROLE_FROM
              && C.CAP_MAX == c_mend2.C.CAP_MAX && C.ROLES == c_mend2.C.ROLES)) throw new AssertionError("other economy constants unchanged");
        System.out.println("ad1: 2 cases ok");
    }
}
