package c_evac1;

import battlecode.common.*;
import battlecode.world.Inventory;
import java.lang.reflect.Field;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;

/** c_evac1 (c_isle1 + C.EVAC: a raided HQ zone is evacuated). The raided bits (AD_FLAGS 12-15) survive setAdFlag,
 *  setPressed and the probe release (gather) and claim (probeStart), and setRaided writes only on a change; the flag's
 *  timing through HQ.swarmEconomy (on at the round the previous + current bucket reach C.RAID_SUM, off C.RAID_HOLD
 *  rounds after the last such round); the carrier gate (evacBlocks, clearExists) and HQ.build through the proxy
 *  (launchers still built, the carrier held below C.EVAC_AD_RELEASE, reason 10 only in place of 9); safeFrom (nearest
 *  clear HQ, first in HQ order on a tie), evacuated (radius, home HQ, the Mid site), nearestEvac, deliverHome (the
 *  bounded redirect, sticky for the trip, reset by a raided evacHome, by the deposit and by a throw), switchWell's
 *  filter, gather's drop and evacRepick (WELL source 0, the C.EVAC_RETRY wait, the C.EVAC_MIN_LEFT guard, a collector
 *  keeps its well, no WELL record when the drop's pick is the dropped well), the probe gate, survive's flee target and
 *  swarmRole's Ad flag. With the mask at 0 every new branch is a no-op, and no new code draws G.rand(). API bodies here
 *  are a decision fixture, not engine prices. Exits non-zero on a failure. */
public class Evac1Test {
    static int checks, fails;
    static final int[] shared = new int[64];
    static int writes, ad, mn, actions, maxActions = 5;
    static final StringBuilder builds = new StringBuilder();
    static final List<Integer> wellDots = new ArrayList<>(), wellPrev = new ArrayList<>();
    static int fleeHome = -1, hp = 100;
    static boolean attackable;
    static MapLocation transferTo;
    static final int RNG_SEED = 123456789;
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            switch (method.getName()) {
                case "readSharedArray": return shared[(Integer) args[0]];
                case "canWriteSharedArray": return true;
                case "writeSharedArray": writes++; shared[(Integer) args[0]] = (Integer) args[1]; return null;
                case "getRoundNum": return G.round;
                case "getLocation": return G.here;
                case "getIslandCount": return 0;
                case "getNumAnchors": return 0;
                case "isActionReady": return actions < maxActions;
                case "isMovementReady": return false;              // nobody moves: decisions only
                case "getResourceAmount": {
                    ResourceType t = (ResourceType) args[0];
                    return t == ResourceType.ADAMANTIUM ? ad : t == ResourceType.MANA ? mn : 0;
                }
                case "getWeight": return ad + mn;
                case "getHealth": return hp;
                case "canBuildRobot": {
                    RobotType t = (RobotType) args[0];
                    return t == RobotType.LAUNCHER ? mn >= 45 : t == RobotType.CARRIER && ad >= 50;
                }
                case "buildRobot": {
                    RobotType t = (RobotType) args[0];
                    if (t == RobotType.LAUNCHER) { mn -= 45; builds.append('L'); } else { ad -= 50; builds.append('C'); }
                    actions++;
                    return null;
                }
                case "canTransferResource": return true;
                case "transferResource": {
                    ResourceType t = (ResourceType) args[1];
                    int n = (Integer) args[2];
                    if (t == ResourceType.ADAMANTIUM) ad -= n; else if (t == ResourceType.MANA) mn -= n;
                    transferTo = (MapLocation) args[0];
                    actions++;
                    return null;
                }
                case "senseRobotAtLocation": return null;
                case "canCollectResource": return false;
                case "canAttack": return attackable;
                case "attack": ad = mn = 0; actions++; return null;   // a carrier's throw empties it
                case "setIndicatorDot": {
                    MapLocation at = (MapLocation) args[0];
                    if (at.x == -2 - Telemetry.WELL) { wellDots.add(at.y); wellPrev.add((Integer) args[3] >> 8 & 4095); }
                    if (at.x == -2 - Telemetry.FLEE) fleeHome = (Integer) args[2];
                    return null;
                }
                default: throw new AssertionError("unexpected RC call " + method.getName());
            }
        });

    static final MapLocation A = L(5, 5), B = L(40, 40);   // A raided, B clear (unless a test says otherwise)

    public static void main(String[] a) throws Exception {
        check(C.EVAC && C.EVAC_SPAWN, "arm and sub-switch on");
        check(C.RAID_SUM == 25 && C.RAID_HOLD == 25 && C.RAID_SHIFT == 12 && C.EVAC_WELL_R2 == 144 && C.EVAC_DELIVER_SLACK == 4
            && C.EVAC_MIN_LEFT == 5000 && C.EVAC_RETRY == 10 && C.EVAC_AD_RELEASE == C.AD_BANK_CAP, "the spec's knobs");
        check(C.RAID_SHIFT > C.PROBE_SHIFT + 3 && C.PROBE_SHIFT > Comms.PRESS_SHIFT + 3 && C.RAID_SHIFT + 3 <= 15,
            "AD_FLAGS: Ad 0-3, pressed 4-7, probe 8-11, raided 12-15");
        bits();
        timing();
        gate();
        safe();
        evacuatedRule();
        nearest();
        deliverHomeRule();
        switchRule();
        repick();
        grafts();
        identity();
        System.out.println(fails == 0 ? "Evac1Test PASS (" + checks + " checks)" : "Evac1Test FAIL " + fails + " of " + checks);
        if (fails > 0) System.exit(1);
    }

    // ---------------------------------------------------------------- T1 bit preservation
    static void bits() throws Exception {
        carrier(100, L(6, 8), L(20, 0), L(40, 0), L(5, 7), B);   // home (5,7) is HQ_LOC slot 2
        shared[Comms.AD_FLAGS] = 0x0F73;
        Comms.setRaided(2, true);
        check(shared[Comms.AD_FLAGS] == 0x4F73, "setRaided(2, true): 0x4F73 (" + hex() + ")");
        Comms.setAdFlag(1, false);
        check(shared[Comms.AD_FLAGS] == 0x4F71, "setAdFlag(1, false) keeps bit 14 (" + hex() + ")");
        Comms.setPressed(3, true);
        check(shared[Comms.AD_FLAGS] == 0x4FF1, "setPressed(3, true) keeps bit 14 (" + hex() + ")");
        // the probe release through gather() (HQ index 2's claim, bit 10)
        Comms.canWrite = true;
        Carrier.probeRelease = true; Carrier.probeIdx = 2; Carrier.role = 1; Carrier.well = L(30, 30);
        Carrier.gather();
        check(shared[Comms.AD_FLAGS] == 0x4BF1 && !Carrier.probeRelease, "probe release of bit 10 keeps bit 14 (" + hex() + ")");
        // the probe claim through probeStart(): home (5,7), its nearest mana well far (cheb 25)
        shared[Comms.WELLS] = 2 << 12 | G.enc(L(30, 7));
        Carrier.probeInit = false;
        boolean claimed = Carrier.probeStart();
        check(claimed && Carrier.probeIdx == 2 && shared[Comms.AD_FLAGS] == 0x4FF1, "probe claim of bit 10 keeps bit 14 (" + hex() + ")");
        check(Comms.raidMask() == 4, "raidMask() == 4");
        int w = writes;
        Comms.setRaided(2, true);
        check(writes == w, "setRaided(2, true) again: no write");
        Comms.setRaided(2, false);
        check(shared[Comms.AD_FLAGS] == 0x0FF1 && writes == w + 1, "setRaided(2, false): bit 14 cleared, the rest kept (" + hex() + ")");
        Comms.setRaided(-1, true);
        check(shared[Comms.AD_FLAGS] == 0x0FF1, "setRaided(-1): nothing");
        Comms.canWrite = false;
    }

    // ---------------------------------------------------------------- T2 flag timing through swarmEconomy
    static void timing() throws Exception {
        java.util.Arrays.fill(shared, 0);
        G.rc = RC; G.here = A; HQState.ourHQs = new MapLocation[]{A, B};
        HQ.hqIdx = 0; HQ.pressAcc = 0; HQ.pressPrev = 0; HQ.pressBucket = -1; HQ.raidUntil = 0;
        ad = mn = 0;
        boolean[] on = new boolean[231];
        for (int r = 1; r <= 230; r++) {
            G.round = r;
            G.nEnemyFighters = r >= 31 && r <= 43 ? 2 : r >= 150 && r <= 154 ? 5 : 0;
            HQ.swarmEconomy();
            on[r] = (shared[Comms.AD_FLAGS] >> 12 & 1) != 0;
            check((shared[Comms.AD_FLAGS] >> Comms.PRESS_SHIFT & 1) == 0, "r" + r + ": never pressed (PRESS_SUM 100)");
        }
        for (int r = 1; r <= 42; r++) check(!on[r], "r" + r + ": off (sum <= 24)");
        check(on[43], "r43: on (sum 26)");
        for (int r = 43; r <= 98; r++) check(on[r], "r" + r + ": on (r74 pressPrev 26, raidUntil 99)");
        for (int r = 99; r <= 120; r++) check(!on[r], "r" + r + ": off (raidUntil 74 + 25)");
        // exactly RAID_SUM: 5 a round from r150 (bucket 6): on at r154 (25), held through bucket 7 (pressPrev 25) to r199
        for (int r = 121; r <= 153; r++) check(!on[r], "r" + r + ": off (sum <= 20)");
        for (int r = 154; r <= 223; r++) check(on[r], "r" + r + ": on (sum 25, the threshold inclusive; raidUntil 199 + 25)");
        for (int r = 224; r <= 230; r++) check(!on[r], "r" + r + ": off");
        check(HQ.raidUntil == 224, "raidUntil 224 (" + HQ.raidUntil + ")");
        G.nEnemyFighters = 0;
    }

    // ---------------------------------------------------------------- T3 build gate
    static void gate() throws Exception {
        check(HQ.evacBlocks(true, 120) && !HQ.evacBlocks(true, 150) && !HQ.evacBlocks(true, 151), "evacRaid: 120 blocks, 150 releases");
        check(!HQ.evacBlocks(false, 0) && !HQ.evacBlocks(false, 120), "not raided: never blocks");
        check(Comms.clearExists(1, 2) && !Comms.clearExists(3, 2), "two HQs: one raided has a clear sibling, both raided none");
        check(!Comms.clearExists(1, 1) && !Comms.clearExists(0, 0) && Comms.clearExists(0, 1), "one HQ: no sibling");
        check(Comms.clearExists(7, 4) && !Comms.clearExists(15, 4) && Comms.clearExists(8, 3) && !Comms.clearExists(7, 3), "n bounds the mask");

        // HQ 0 raided, HQ 1 clear: the launcher still, no carrier at 120 Ad, reason 10
        hq(true, 1 << 12, 120, 45, A, B);
        HQ.build();
        check(HQ.evacRaid && builds.toString().equals("L") && HQ.reason == 10, "raided, 120 Ad 45 Mn: L only, reason 10 (" + builds + " " + HQ.reason + ")");
        check(HQ.launchersBuilt == 1 && HQ.carriersBuilt == 0, "build counters");
        // 150 Ad releases one carrier (then 100 < 150 holds)
        hq(true, 1 << 12, 150, 0, A, B);
        HQ.build();
        check(builds.toString().equals("C") && HQ.reason == 10, "raided, 150 Ad: one carrier, then held (" + builds + " " + HQ.reason + ")");
        // both raided: no sibling to evacuate to, c_isle1's build
        hq(true, 3 << 12, 120, 0, A, B);
        HQ.build();
        check(!HQ.evacRaid && builds.toString().equals("CC") && HQ.reason == 3, "both raided: CC, poor (" + builds + " " + HQ.reason + ")");
        // one HQ: n = 1, mask 1
        hq(true, 1 << 12, 120, 0, A);
        HQ.build();
        check(!HQ.evacRaid && builds.toString().equals("CC"), "one HQ raided: CC (" + builds + ")");
        // not raided by its own clock (raidUntil passed) although the bit reads set: c_isle1's build
        hq(false, 1 << 12, 120, 0, A, B);
        HQ.build();
        check(!HQ.evacRaid && builds.toString().equals("CC"), "raidUntil passed: CC (" + builds + ")");
        // the override only replaces 9: poor stays 3, no cap room stays 5
        hq(true, 1 << 12, 30, 0, A, B);
        HQ.build();
        check(HQ.evacRaid && builds.length() == 0 && HQ.reason == 3, "raided, 30 Ad: poor 3 (" + HQ.reason + ")");
        hq(true, 1 << 12, 120, 0, A, B);
        HQ.liveCarriers = HQ.carrierCap;
        HQ.build();
        check(HQ.evacRaid && builds.length() == 0 && HQ.reason == 5, "raided, no cap room: 5 (" + HQ.reason + ")");
        check(Telemetry.hqCode(10, false, false) == 10 && Telemetry.letters(0).charAt(10) == 'r' && Telemetry.letters(0).charAt(42) == 'r',
            "code 10 decodes as 'r' (indicator letters)");
    }

    // ---------------------------------------------------------------- T4 safeFrom
    static void safe() throws Exception {
        MapLocation h0 = L(0, 0), h1 = L(20, 0), h2 = L(40, 0), h3 = L(0, 40);
        carrier(100, L(5, 0), h0, h1, h2, h3);
        int rng = rng();
        mask(1);
        check(Carrier.evac && h1.equals(Carrier.safeFrom(h0, L(5, 0))), "mask 0001 from (5,0): (20,0)");
        mask(3);
        check(h2.equals(Carrier.safeFrom(h0, L(5, 0))), "mask 0011 from (5,0): (40,0)");
        mask(1);
        check(h1.equals(Carrier.safeFrom(h0, L(10, 20))), "tie at d2 500: the first in HQ order, (20,0)");
        check(h1.equals(Carrier.safeFrom(h1, L(10, 20))), "a clear n: n");
        check(Carrier.safeFrom(null, L(10, 20)) == null, "null n: null");
        check(Carrier.safeFrom(L(7, 7), L(10, 20)).equals(L(7, 7)), "not one of our HQs: n");
        mask(15);
        check(!Carrier.evac && h0.equals(Carrier.safeFrom(h0, L(5, 0))), "mask 1111: evac off, n");
        Carrier.evac = true;     // even with evac forced on, no clear HQ: n
        check(h0.equals(Carrier.safeFrom(h0, L(5, 0))), "no clear HQ: n");
        mask(0);
        check(!Carrier.evac && h0.equals(Carrier.safeFrom(h0, L(5, 0))), "mask 0: n");
        check(rng() == rng, "safeFrom: no RNG draw");
    }

    // ---------------------------------------------------------------- T5 evacuated
    static void evacuatedRule() throws Exception {
        carrier(100, L(20, 20), A, B);
        int rng = rng();
        mask(1);
        check(Carrier.evacuated(L(10, 10)), "(10,10) d2 50 from the raided (5,5), its home: evacuated");
        check(Carrier.evacuated(L(5, 17)), "(5,17) d2 144: evacuated (inclusive)");
        check(!Carrier.evacuated(L(15, 15)), "(15,15) d2 200: not evacuated");
        check(!Carrier.evacuated(L(38, 38)), "near the clear HQ: not evacuated");
        check(!Carrier.evacuated(null), "null: false");
        shared[Comms.SYM_ELIM] = Comms.withSite(0, G.enc(L(10, 10)));
        check(!Carrier.evacuated(L(10, 10)) && !Carrier.evacuated(L(10, 11)), "the Mid site and its twin: not evacuated");
        check(Carrier.evacuated(L(8, 8)), "near the site but beyond MID_TWIN_R2 (d2 8): evacuated");
        shared[Comms.SYM_ELIM] = 0;
        carrier(100, L(20, 20), A, L(14, 14));
        mask(1);
        check(!Carrier.evacuated(L(11, 11)), "(11,11) d2 72 from the raided (5,5) but home is the clear (14,14): false");
        check(Carrier.evacuated(L(7, 7)), "(7,7): home (5,5), evacuated");
        mask(0);
        check(!Carrier.evacuated(L(7, 7)) && !Carrier.evacuated(L(10, 10)), "mask 0: false");
        check(rng() == rng, "evacuated: no RNG draw");
    }

    // ---------------------------------------------------------------- T6 nearestEvac
    static void nearest() throws Exception {
        carrier(100, L(12, 12), A, B);
        wells(L(8, 8), 2, L(36, 36), 2);
        seen(L(30, 30), 2);
        mask(1);
        int rng = rng();
        check(L(36, 36).equals(Carrier.nearestEvac(B, 2)), "from (40,40): (36,36)");
        check(L(30, 30).equals(Carrier.nearestEvac(L(12, 12), 2)), "from (12,12): not the evacuated (8,8), the seen (30,30)");
        check(L(8, 8).equals(Carrier.nearestCool(L(12, 12), 2)), "nearestCool from (12,12) takes (8,8): the filter is the difference");
        check(Carrier.nearestEvac(L(12, 12), 1) == null, "no Ad well: null");
        shared[Comms.WELLS + 1] |= 0x4000; Carrier.hotRound = -1;
        check(L(30, 30).equals(Carrier.nearestEvac(B, 2)), "(36,36) hot: (30,30)");
        clearSeen();
        wells(L(8, 8), 2);
        check(Carrier.nearestEvac(B, 2) == null && Carrier.nearestEvac(A, 0) == null, "only (8,8) known: null");
        check(rng() == rng, "nearestEvac: no RNG draw");
    }

    // ---------------------------------------------------------------- T7 deliverHome
    static void deliverHomeRule() throws Exception {
        MapLocation c1 = L(20, 10);
        carrier(100, L(10, 10), A, c1, B);
        mask(1);
        int rng = rng();
        check(c1.equals(Carrier.deliverHome()) && c1.equals(Carrier.evacHome) && Carrier.evacDelivers == 1,
            "cheb 10 <= 5 * 3 / 2 + 4 = 11: the clear (20,10), sticky");
        G.here = L(11, 10);
        check(c1.equals(Carrier.deliverHome()) && Carrier.evacDelivers == 1, "one step on: evacHome, no new redirect");
        G.here = L(8, 8);
        check(c1.equals(Carrier.deliverHome()), "sticky even where the bound would fail (cheb 12 vs 3 * 3 / 2 + 4)");
        G.here = L(11, 10);
        mask(3);                                     // evacHome raided too; B still clear
        check(Carrier.evac && A.equals(Carrier.deliverHome()) && Carrier.evacHome == null,
            "evacHome raided: reset; the clear (40,40) is out of bounds: the nearest (5,5)");
        mask(1);
        G.here = L(10, 10);
        check(c1.equals(Carrier.deliverHome()) && c1.equals(Carrier.evacHome), "redirect again");
        mask(0);
        check(Carrier.evacHome == null && A.equals(Carrier.deliverHome()), "mask 0: evacTick clears evacHome, the nearest HQ");
        check(rng() == rng, "no tie: no RNG draw");
        // (22,10) at cheb 12 > 11: no redirect
        carrier(100, L(10, 10), A, L(22, 10), B);
        mask(1);
        check(A.equals(Carrier.deliverHome()) && Carrier.evacHome == null && Carrier.evacDelivers == 0, "cheb 12 > 11: the raided (5,5)");
        // a clear nearest HQ: itself
        carrier(100, L(18, 10), A, c1, B);
        mask(1);
        check(c1.equals(Carrier.deliverHome()) && Carrier.evacHome == null && Carrier.evacDelivers == 0, "nearest clear: itself, not sticky");
        // the draw count: a tie between (5,5) and (15,15) draws exactly as HQState.nearest does
        carrier(100, L(10, 10), A, L(15, 15), B);
        mask(1);
        for (int s = 1; s <= 40; s++) {
            setRng(s * 7919 + 13); MapLocation n = HQState.nearest(G.here); int r1 = rng();
            setRng(s * 7919 + 13); Carrier.evacHome = null; MapLocation d = Carrier.deliverHome(); int r2 = rng();
            check(r1 == r2 && r1 != s * 7919 + 13, "seed " + s + ": one draw, as HQState.nearest");
            check(L(15, 15).equals(d), "seed " + s + ": the clear (15,15) whichever way the tie fell (" + n + ")");
        }
        // the deposit ends the trip: evacHome reset where returning goes false
        carrier(100, L(10, 10), A, c1, B);
        mask(1);
        Carrier.deliverHome();
        G.here = L(19, 10);
        ad = 0; mn = 40; Carrier.returning = true; Carrier.well = null;
        Carrier.deliver();
        check(c1.equals(transferTo) && mn == 0 && !Carrier.returning && Carrier.evacHome == null && Carrier.state == 'D',
            "deposit at the clear HQ: returning false, evacHome reset");
        // a throw ends the trip too: the next trip is not sent to the last trip's clear HQ past the bound
        carrier(100, L(20, 20), A, B);
        mask(1);
        check(B.equals(Carrier.deliverHome()) && B.equals(Carrier.evacHome), "trip 1 from (20,20): cheb 20 <= 15 * 3 / 2 + 4, the clear (40,40)");
        int thrown = Carrier.throwsMade;
        mn = 30; hp = 50; attackable = true; Carrier.returning = true;
        G.enemies = new RobotInfo[]{new RobotInfo(9001, Team.B, RobotType.LAUNCHER, new Inventory(), 200, L(22, 22))};
        G.nEnemyFighters = 1;
        check(Carrier.survive() && Carrier.throwsMade == thrown + 1 && mn == 0 && !Carrier.returning && Carrier.evacHome == null,
            "throw at d2 8 (hp 50, load 30): returning false, evacHome reset");
        G.enemies = new RobotInfo[0]; G.nEnemyFighters = 0; hp = 100; attackable = false;
        G.here = L(0, 18); mn = 40; Carrier.returning = true;
        mask(1);
        check(A.equals(Carrier.deliverHome()) && Carrier.evacHome == null && Carrier.evacDelivers == 1,
            "trip 2 from (0,18): cheb 40 > 13 * 3 / 2 + 4, the raided nearest (5,5), not the stale (40,40)");
    }

    // ---------------------------------------------------------------- T8 switchWell
    static void switchRule() throws Exception {
        carrier(100, L(15, 15), A, B);
        Carrier.role = 2; Carrier.well = L(14, 18);
        wells(L(14, 18), 2, L(8, 8), 2, L(30, 30), 2);
        mask(1);
        Carrier.switchWell();
        check(L(30, 30).equals(Carrier.well) && lastSource() == 5, "an evacuated (8,8) nearer than the clear (30,30): (30,30)");
        // the seen loop too
        Carrier.well = L(14, 18);
        wells(L(14, 18), 2);
        seen(L(9, 9), 2); seen(L(28, 28), 2);
        Carrier.switchWell();
        check(L(28, 28).equals(Carrier.well), "seen: the evacuated (9,9) skipped, (28,28)");
        // only evacuated alternatives (role 2): c_isle1's no-best branch
        clearSeen();
        Carrier.well = L(14, 18); Carrier.searchTurns = 7; Carrier.centreTried = true;
        wells(L(14, 18), 2, L(8, 8), 2);
        Carrier.switchWell();
        check(Carrier.well == null && !Carrier.centreTried && Carrier.searchTurns == 0, "only evacuated alternatives: well null, search");
    }

    // ---------------------------------------------------------------- T9 gather's drop and evacRepick
    static void repick() throws Exception {
        // the c_isle1 pick (8,8) is evacuated, (30,30) known: replaced, a source-0 WELL record after the source-1 one
        carrier(100, L(12, 12), A, B);
        wells(L(8, 8), 2, L(30, 30), 2);
        mask(1);
        Carrier.gather();
        check(L(30, 30).equals(Carrier.well) && Carrier.evacPicks == 1 && Carrier.state == 'G', "repick: (30,30), evacPicks 1");
        check(wellDots.size() == 2 && source(wellDots.get(0)) == 1 && source(wellDots.get(1)) == 0
            && (wellDots.get(1) & 4095) == G.enc(L(30, 30)), "WELL records: source 1 (8,8), then source 0 (30,30)");
        // no alternative: c_isle1's pick stands, no drop for EVAC_RETRY rounds
        carrier(100, L(12, 12), A, B);
        wells(L(8, 8), 2);
        mask(1);
        Carrier.gather();
        check(L(8, 8).equals(Carrier.well) && Carrier.evacFallUntil == 110 && Carrier.evacPicks == 0, "no alternative: (8,8) kept, retry at 110");
        for (int r = 101; r < 110; r++) {
            G.round = r; mask(1); Carrier.gather();
            check(L(8, 8).equals(Carrier.well) && wellDots.size() == 1, "r" + r + ": no drop before evacFallUntil");
        }
        G.round = 110; mask(1); Carrier.gather();
        check(L(8, 8).equals(Carrier.well) && Carrier.evacFallUntil == 120 && wellDots.size() == 1,
            "r110: dropped, re-picked (the same well: no WELL record), retry at 120");
        G.round = 120; wells(L(8, 8), 2, L(30, 30), 2); mask(1); Carrier.gather();
        check(L(30, 30).equals(Carrier.well) && Carrier.evacPicks == 1, "r120 with (30,30) published: dropped and repicked");
        check(wellDots.size() == 2 && lastSource() == 0 && lastPrev() == Telemetry.loc12(L(8, 8)),
            "r120: one record, source 0 from (8,8) (the re-pick of the dropped (8,8) emits none)");
        // the drop's pick is another well (the nearest from here, clear): c_isle1's record, no repick
        carrier(100, L(20, 20), A, B);
        wells(L(8, 8), 2, L(30, 30), 2);
        mask(1);
        Carrier.well = L(8, 8); Carrier.lastWell = L(8, 8);
        Carrier.gather();
        check(L(30, 30).equals(Carrier.well) && Carrier.evacPicks == 0 && wellDots.size() == 1 && lastSource() == 1
            && lastPrev() == Telemetry.loc12(L(8, 8)), "dropped (8,8), the pick from (20,20) the clear (30,30): source 1, no repick");
        // a collector at its evacuated well keeps it
        carrier(100, L(8, 9), A, B);
        wells(L(8, 8), 2, L(30, 30), 2);
        mask(1);
        Carrier.well = L(8, 8);
        Carrier.gather();
        check(L(8, 8).equals(Carrier.well) && Carrier.state == 'C' && wellDots.isEmpty(), "at the well (d2 1): keeps collecting");
        // short budget: no repick this turn (c_isle1's pick stands), retried next turn
        carrier(100, L(12, 12), A, B);
        wells(L(8, 8), 2, L(30, 30), 2);
        mask(1);
        budget(C.EVAC_MIN_LEFT - 1000);
        Carrier.gather();
        check(L(8, 8).equals(Carrier.well) && Carrier.evacPicks == 0 && Carrier.evacFallUntil == 0, "budget 4000: no change");
        G.round = 101; mask(1);
        Carrier.gather();
        check(L(8, 8).equals(Carrier.well) && Carrier.evacPicks == 0 && wellDots.size() == 1,
            "r101, budget 4000 again: dropped and re-picked, no WELL record");
        budget(20000); G.round = 102; mask(1);
        Carrier.gather();
        check(L(30, 30).equals(Carrier.well) && Carrier.evacPicks == 1 && wellDots.size() == 2 && lastSource() == 0
            && lastPrev() == Telemetry.loc12(L(8, 8)), "next turn with the budget: dropped and repicked (one record, source 0)");
        // the search fallback (any type) is repicked too
        carrier(100, L(12, 12), A, B);
        wells(L(8, 8), 1, L(30, 30), 1);
        mask(1);
        Carrier.searchTurns = C.WELL_SEARCH_TURNS;
        Carrier.gather();
        check(L(30, 30).equals(Carrier.well) && Carrier.evacPicks == 1 && source(wellDots.get(wellDots.size() - 1)) == 0,
            "search fallback (any type): (30,30), source 0");
        // the probe gate: no probe starts from a raided zone; with the mask at 0 the probe starts (probeInit)
        carrier(100, L(12, 12), A, B);
        wells(L(8, 8), 2, L(30, 30), 2);
        mask(1);
        Carrier.probeDone = false; Carrier.probeInit = false;
        Carrier.gather();
        check(!Carrier.probeInit && !Carrier.probeDone && L(30, 30).equals(Carrier.well), "raided zone: no probe start, probeDone kept");
        mask(0);
        Carrier.well = null;
        Carrier.gather();
        check(Carrier.probeInit, "mask 0: the probe starts as in c_isle1");
    }

    // ---------------------------------------------------------------- copy-design grafts: survive, swarmRole
    static void grafts() throws Exception {
        // survive: the flee target is the clear HQ (FLEE home field), evacFlees counts it
        carrier(100, L(12, 12), A, B);
        mask(1);
        ad = mn = 0; Carrier.prevState = 'G';
        G.enemies = new RobotInfo[]{new RobotInfo(9001, Team.B, RobotType.LAUNCHER, new Inventory(), 200, L(14, 14))};
        G.nEnemyFighters = 1;
        check(Carrier.survive() && fleeHome == G.enc(B) && Carrier.evacFlees == 1, "survive: flee home (40,40) (" + fleeHome + ")");
        mask(0); fleeHome = -1;
        check(Carrier.survive() && fleeHome == G.enc(A) && Carrier.evacFlees == 1, "mask 0: flee home (5,5)");
        G.enemies = new RobotInfo[0]; G.nEnemyFighters = 0;
        // swarmRole: the safe HQ's Ad flag (HQ 0 wants Ad, HQ 1 does not)
        carrier(100, L(12, 12), A, B);
        shared[Comms.AD_FLAGS] = 1;
        G.id = 16; mask(1);
        check(Carrier.swarmRole() == 2, "id 16, HQ 0 raided: HQ 1's flag (clear): mana");
        mask(0);
        check(Carrier.swarmRole() == 1, "id 16, mask 0: HQ 0's flag: adamantium");
        G.id = 17; mask(1);
        int rng = rng();
        check(Carrier.swarmRole() == 2 && rng() == rng, "id 17: mana, no draw");
        G.id = 10002;
    }

    // ---------------------------------------------------------------- T10 identity with the mask at 0
    static void identity() throws Exception {
        carrier(100, L(12, 12), A, B);
        wells(L(8, 8), 2, L(30, 30), 2);
        Carrier.evacHome = L(40, 40);
        mask(0);
        int rng = rng();
        check(!Carrier.evac && Carrier.evacHome == null, "mask 0: evac off, evacHome cleared");
        for (MapLocation h : HQState.ourHQs) check(h.equals(Carrier.safeFrom(h, L(12, 12))), "safeFrom(" + h + "): n");
        check(!Carrier.evacuated(L(8, 8)), "evacuated: false");
        Carrier.well = L(8, 8);
        Carrier.evacRepick(2);
        check(L(8, 8).equals(Carrier.well) && Carrier.evacPicks == 0 && Carrier.evacFallUntil == 0 && wellDots.isEmpty(), "evacRepick: no-op");
        Carrier.gather();
        check(L(8, 8).equals(Carrier.well) && wellDots.isEmpty(), "gather: no drop, the well kept");
        Carrier.well = null;
        Carrier.gather();
        check(L(8, 8).equals(Carrier.well) && wellDots.size() == 1 && source(wellDots.get(0)) == 1, "gather: c_isle1's pick (8,8), source 1");
        Carrier.well = L(14, 18);
        wells(L(14, 18), 2, L(8, 8), 2, L(30, 30), 2);
        G.here = L(15, 15);
        Carrier.switchWell();
        check(L(8, 8).equals(Carrier.well), "switchWell: c_isle1's nearest (8,8)");
        check(rng() == rng, "no RNG draw in any of them");
        G.here = L(10, 10);
        check(A.equals(Carrier.deliverHome()) && Carrier.evacHome == null && Carrier.evacDelivers == 0, "deliverHome: the nearest HQ");
        // evac stays off without a clear sibling: all raided, one HQ
        mask(3);
        check(!Carrier.evac && A.equals(Carrier.deliverHome()), "all raided: evac off");
        carrier(100, L(12, 12), A);
        mask(1);
        check(!Carrier.evac && !Carrier.evacuated(L(8, 8)) && A.equals(Carrier.deliverHome()), "one HQ raided: evac off");
    }

    // ---------------------------------------------------------------- fixture
    /** HQ build fixture: HQ 0 at hqs[0] (raided by its own clock when raided), AD_FLAGS = flags, the bank, room. */
    static void hq(boolean raided, int flags, int bankAd, int bankMn, MapLocation... hqs) throws Exception {
        java.util.Arrays.fill(shared, 0);
        for (int i = 0; i < hqs.length; i++) shared[Comms.HQ_LOC + i] = G.enc(hqs[i]);
        shared[Comms.AD_FLAGS] = flags;
        G.rc = RC; G.round = 100; G.here = hqs[0]; G.W = G.H = 60; G.id = 1;
        G.enemies = new RobotInfo[0]; G.nEnemyFighters = 0; G.nAllyFighters = 0;
        HQState.ourHQs = hqs.clone();
        MapMem.cand = 1;
        HQ.hqIdx = 0; HQ.raidUntil = raided ? G.round + 5 : G.round;
        HQ.liveCarriers = 0; HQ.pendingCarriers = 0; HQ.carrierCap = 20;
        HQ.launchersBuilt = HQ.carriersBuilt = 0;
        MapLocation h = hqs[0];
        HQ.spawnTiles = new MapLocation[]{h.translate(1, 0), h.translate(0, 1), h.translate(1, 1), h.translate(2, 0)};
        ad = bankAd; mn = bankMn; actions = 0; builds.setLength(0);
        budget(20000);
    }

    /** Carrier fixture at round r and here; our HQs in HQ_LOC order; no well, no probe, no hot well, mask 0. */
    static void carrier(int r, MapLocation here, MapLocation... hqs) throws Exception {
        java.util.Arrays.fill(shared, 0);
        for (int i = 0; i < hqs.length; i++) shared[Comms.HQ_LOC + i] = G.enc(hqs[i]);
        G.rc = RC; G.round = r; G.here = here; G.W = G.H = 60; G.id = 10002; G.type = RobotType.CARRIER;
        G.us = Team.A; G.them = Team.B; G.enemies = new RobotInfo[0]; G.nEnemyFighters = 0; G.nAllyFighters = 0;
        HQState.ourHQs = hqs.clone();
        MapMem.cand = 1;
        Comms.canWrite = false;
        Carrier.role = 2; Carrier.well = null; Carrier.returning = false; Carrier.searchTurns = 0; Carrier.crowdTurns = 0;
        Carrier.probeDone = true; Carrier.probeInit = true; Carrier.probeRelease = false; Carrier.midHome = false;
        Carrier.midAvoidUntil = 0; Carrier.hotSpot = null; Carrier.hotUntil = 0; Carrier.hotPending = false;
        Carrier.hotRound = -1; Carrier.ehqRound = -1; Carrier.prevState = 'G'; Carrier.state = '?';
        Carrier.evac = false; Carrier.evacMask = 0; Carrier.evacFallUntil = 0; Carrier.evacHome = null; Carrier.evacDropped = null;
        Carrier.evacPicks = Carrier.evacFlees = Carrier.evacDelivers = 0;
        clearSeen();
        wellDots.clear(); wellPrev.clear(); fleeHome = -1; transferTo = null; hp = 100; attackable = false;
        ad = mn = 0; actions = 0; writes = 0;
        setRng(RNG_SEED);
        budget(20000);
    }

    /** The raided bits as an HQ would set them, then this carrier's evacTick. */
    static void mask(int m) throws Exception {
        shared[Comms.AD_FLAGS] = (shared[Comms.AD_FLAGS] & ~(15 << C.RAID_SHIFT)) | m << C.RAID_SHIFT;
        Carrier.evacTick();
    }

    /** The shared well list: location, type pairs (no hot bits). */
    static void wells(Object... lt) {
        for (int i = 0; i < Comms.NWELLS; i++) shared[Comms.WELLS + i] = 0;
        for (int i = 0; i < lt.length; i += 2) shared[Comms.WELLS + i / 2] = ((Integer) lt[i + 1]) << 12 | G.enc((MapLocation) lt[i]);
        Carrier.hotRound = -1;
    }

    static void seen(MapLocation l, int t) { MapMem.noteWell(l, t); }

    static void clearSeen() throws Exception { set(MapMem.class, "nSeenWell", 0); set(MapMem.class, "nUnreported", 0); }

    static int source(int a) { return (a >> 14) & 7; }

    static int lastSource() { return wellDots.isEmpty() ? -1 : source(wellDots.get(wellDots.size() - 1)); }

    /** The last WELL record's prev_well (loc12), -1 if none. */
    static int lastPrev() { return wellPrev.isEmpty() ? -1 : wellPrev.get(wellPrev.size() - 1); }

    static String hex() { return Integer.toHexString(shared[Comms.AD_FLAGS]); }

    static MapLocation L(int x, int y) { return new MapLocation(x, y); }

    static int rng() throws Exception { return (Integer) get(G.class, "rng"); }

    static void setRng(int v) throws Exception { set(G.class, "rng", v); }

    static Object get(Class<?> cls, String name) throws Exception {
        Field f = cls.getDeclaredField(name); f.setAccessible(true); return f.get(null);
    }

    static void set(Class<?> cls, String name, Object value) throws Exception {
        Field f = cls.getDeclaredField(name); f.setAccessible(true); f.set(null, value);
    }

    static void budget(int value) {
        try {
            Field f = Class.forName("battlecode.instrumenter.inject.RobotMonitor").getDeclaredField("bytecodesLeft");
            f.setAccessible(true); f.setInt(null, value);
        } catch (Exception e) { throw new RuntimeException(e); }
    }

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { fails++; System.out.println("FAIL " + what); }
    }
}
