package c_well6;

import battlecode.common.MapLocation;

/** c_well6's hot wells: the shared well slot's hot bits (Comms.wellType, hotLevel, withHot, cooled), the front-well
 *  gate (Carrier.frontGate), Carrier.minD2 and Carrier.homeOf. Map data from the engine maps (diag/map.py): Forest,
 *  our HQ (11,48), enemy (48,48), midline mana wells (29,48) and (30,48); Pillars, our HQs (1,2) and (1,18), mana well
 *  (7,10). Exits non-zero on a failure. */
public class HotWellTest {
    public static void main(String[] a) {
        int enc = 29 * 64 + 48 + 1, slot = (2 << 12) | enc;                 // mana well (29,48), not hot
        check(Comms.wellType(slot) == 2 && Comms.hotLevel(slot) == 0, "a fresh slot: type 2, not hot");
        int hot = Comms.withHot(slot);
        check(Comms.hotLevel(hot) == C.HOT_LEVEL && Comms.wellType(hot) == 2 && (hot & 0xfff) == enc,
            "withHot keeps type and location, sets HOT_LEVEL");
        check(hot <= 0xffff, "a hot slot fits the 16-bit shared array");
        check(Comms.withHot(hot) == hot, "marking a hot well again changes nothing");
        int c = hot, periods = 0;
        while (Comms.hotLevel(c) > 0) { c = Comms.cooled(c); periods++; }
        check(periods == C.HOT_LEVEL && c == slot, "HOT_LEVEL decays back to the plain slot");
        check(Comms.cooled(slot) == slot, "cooling a cool slot changes nothing");
        check(Comms.wellType((3 << 12) | enc | (1 << 14)) == 3, "elixir type read through a hot bit");
        check(((3 << 12) | (59 * 64 + 59 + 1) | (3 << 14)) <= 0xffff, "the largest hot slot fits 16 bits");
        // front wells: Forest's midline wells are; Pillars' (7,10) and MassiveL's (2,0) are home wells
        MapLocation forestHome = new MapLocation(11, 48), forestEnemy = new MapLocation(48, 48);
        MapLocation[] fh = {forestHome}, fe = {new MapLocation(59, 0), new MapLocation(53, 30), forestEnemy};
        MapLocation w1 = new MapLocation(29, 48), w2 = new MapLocation(30, 48);
        check(Carrier.frontGate(Carrier.minD2(w1, fh), Carrier.minD2(w1, fe)), "Forest (29,48) is a front well");
        check(Carrier.frontGate(Carrier.minD2(w2, fh), Carrier.minD2(w2, fe)), "Forest (30,48) is a front well");
        check(w1.distanceSquaredTo(w2) <= C.HOT_NEAR_D2, "one fighter's spot covers both midline wells");
        MapLocation[] ph = {new MapLocation(1, 2), new MapLocation(1, 18)};
        MapLocation[] pe = {new MapLocation(33, 2), new MapLocation(33, 18)};
        MapLocation p = new MapLocation(7, 10);
        check(Carrier.minD2(p, ph) == 100, "Pillars (7,10) is r2 100 from our HQs");
        check(!Carrier.frontGate(Carrier.minD2(p, ph), Carrier.minD2(p, pe)), "Pillars (7,10) is a home well (100 vs 740)");
        check(!Carrier.frontGate(Carrier.minD2(new MapLocation(2, 0), new MapLocation[]{new MapLocation(7, 5)}),
            Carrier.minD2(new MapLocation(2, 0), new MapLocation[]{new MapLocation(52, 54)})), "MassiveL (2,0) is a home well");
        check(!Carrier.frontGate(64, 100), "r2 64 from home is home, however near the enemy");
        check(!Carrier.frontGate(81, Integer.MAX_VALUE), "no enemy HQ candidate: never a front well");
        check(Carrier.minD2(p, null) == Integer.MAX_VALUE && Carrier.minD2(p, new MapLocation[]{null}) == Integer.MAX_VALUE,
            "minD2 of nothing");
        HQState.ourHQs = ph;                                                  // homeOf: the first HQ on a tie, no RNG
        check(new MapLocation(1, 2).equals(Carrier.homeOf(p)), "Pillars (7,10) ties: the first HQ in order");
        check(new MapLocation(1, 18).equals(Carrier.homeOf(new MapLocation(5, 15))), "nearest HQ");
        HQState.ourHQs = null;
        check(Carrier.homeOf(p) == null, "no HQ known: null");
        System.out.println("hot wells: " + checks + " cases ok");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
