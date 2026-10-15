package c_cap1;

/** c_cap1 is c_mend2 with only the team carrier cap raised: every other cap and economy constant is unchanged. */
public final class Cap1Test {
    static int checks;
    public static void main(String[] args) {
        check(C.CAP_MAX == 45 && c_mend2.C.CAP_MAX == 30, "cap raised from 30 to 45");
        check(C.CAP_PER_MN_WELL == c_mend2.C.CAP_PER_MN_WELL && C.CAP_MIN_PER_HQ == c_mend2.C.CAP_MIN_PER_HQ
            && C.CAP_GROW_ROUNDS == c_mend2.C.CAP_GROW_ROUNDS, "other cap terms unchanged");
        check(C.AD_NEED == c_mend2.C.AD_NEED && C.AD_BANK_CAP == c_mend2.C.AD_BANK_CAP && C.ROLES == c_mend2.C.ROLES
            && C.CARRIER_RETURN_LOAD == c_mend2.C.CARRIER_RETURN_LOAD, "economy constants unchanged");
        System.out.println("cap1: " + checks + " cases ok");
    }
    static void check(boolean ok, String message) { checks++; if (!ok) throw new AssertionError(message); }
}
