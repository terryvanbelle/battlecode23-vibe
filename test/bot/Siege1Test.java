package c_siege1;

/** c_siege1 is c_mend2 with siege batching: a threatened HQ facing >= 2 enemy fighters spawns launchers only as a batch
 *  of min(5, enemies + 1) in one turn (HQ action cooldown 2: 5 builds a turn). */
public final class Siege1Test {
    public static void main(String[] args) {
        if (!(C.SIEGE_MIN == 2 && C.SIEGE_BATCH_MAX == 5)) throw new AssertionError("siege parameters");
        if (C.SIEGE_BATCH_MAX * 2 > 10) throw new AssertionError("a batch must fit in one turn (5 builds at cooldown 2)");
        if (!(C.LAUNCHER_BATCH == c_mend2.C.LAUNCHER_BATCH && C.HQ_THREAT == c_mend2.C.HQ_THREAT && C.CAP_MAX == c_mend2.C.CAP_MAX))
            throw new AssertionError("other constants as c_mend2");
        System.out.println("siege1: 3 cases ok");
    }
}
