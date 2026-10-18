package c_drop1;

import battlecode.common.*;

import java.lang.reflect.Proxy;
import java.util.Random;

/** c_drop1 (c_hr1 + C.DROP, research/diagnosis/2026-10-17-panel-losses-c_hr1.md 4b): the pure rules (dropHit, farAlt,
 *  backToRaided, Flee4Test's sections 12-13 cases), noteFlight (only the first turn of a flight counts, a second one
 *  from the same well within DROP_REPEAT drops it, home wells included; c_mid1's site and twin excluded), the drop's
 *  span in hotLocal and anyHot (DROP_AVOID rounds, or until badKeep; never the site or twin), nearestCool's choice
 *  under a drop and dropBack (never stranded: no near alternative of the role brings the raided well back, even after a
 *  later single flight from another well; a changed role ends the drop), gather() itself under a drop (never 'X', a
 *  changed role gets c_hr1's choice the same turn). With no drop on, hotLocal and anyHot
 *  equal c_hr1's (copied below as refHotLocal and refAnyHot) on random states, front-well hot spots included; with one
 *  on, hotLocal is c_hr1's plus the wells near the raided point. No shared write, no hot mark, no RNG draw. A
 *  RobotController proxy serves the shared array and the indicator dots; any other engine call fails the test. Exits
 *  non-zero on a failure. */
public class Drop1Test {
    static final Random R = new Random(20261017);
    static final int[] shared = new int[64];
    static int writesSeen, lastWellDot = -1;

    static final MapLocation HQ0 = L(10, 10);
    static final MapLocation W0 = L(14, 10);    // home mana well: r2 16 from the HQ, not a front well
    static final MapLocation T1 = L(16, 8);     // the raider: r2 8 from W0
    static final MapLocation A1 = L(8, 15);     // near mana alternative: r2 29 from the HQ, r2 113 from T1 (cool)
    static final MapLocation A2 = L(26, 10);    // far mana alternative: r2 256 from the HQ, r2 104 from T1 (cool)
    static final MapLocation AD = L(5, 13);     // near adamantium well: r2 34 from the HQ, r2 146 from T1 (cool)
    static final MapLocation ADZ = L(16, 12);   // adamantium well in the raid: r2 16 from T1, r2 40 from the HQ

    public static void main(String[] a) throws Exception {
        G.rc = proxy();
        G.us = Team.A; G.them = Team.B;
        G.W = 60; G.H = 60;
        G.type = RobotType.CARRIER;
        G.here = L(12, 10);
        HQState.ourHQs = new MapLocation[]{HQ0};
        MapMem.cand = 1;                                       // rotation: the enemy HQ is (49,49)
        Comms.canWrite = false;
        knobs();
        pure();
        noteFlight();
        span();
        choice();
        gatherTurn();
        sameAsHr1();
        check(writesSeen == 0, "no shared-array write");
        System.out.println("drop1: " + checks + " cases ok");
    }

    // ---------------------------------------------------------------- 1. knobs
    static void knobs() {
        check(C.DROP, "arm on");
        check(C.HOT, "the drop rides on c_well6's hot-well checks (gather's hot(well) drop, anyHot's cool choice)");
        check(C.DROP_WELL_R2 == 64 && C.DROP_REPEAT == 30 && C.DROP_AVOID == 40 && C.DROP_ALT_D2 == 100,
            "c_flee4's FLEE1_WELL_R2, FLEE1_REPEAT, FLEE1_AVOID, FLEE1_ALT_D2");
        check(C.SIEGE_ROTATE == 100 && C.SIEGE_ROTATE_FROM == 300 && C.HUNT && C.MID && C.GUARD, "c_hr1's other knobs");
    }

    // ---------------------------------------------------------------- 2. pure rules
    static void pure() {
        // dropHit: the edges are inclusive
        check(Carrier.dropHit(false, 64, true, 30), "first turn, r2 64, same well, 30 rounds: drop");
        check(Carrier.dropHit(false, 0, true, 0), "r2 0, same round: drop");
        check(!Carrier.dropHit(true, 64, true, 30), "a continued flight (F or V last turn): no drop");
        check(!Carrier.dropHit(false, 65, true, 30), "fighter at r2 65 from the well: no drop");
        check(!Carrier.dropHit(false, 64, false, 30), "another well: no drop");
        check(!Carrier.dropHit(false, 64, true, 31), "31 rounds after the last flight: no drop");
        check(!Carrier.dropHit(false, 10, true, 1000 + 5), "no earlier flight (fWellRound -1000): no drop");
        int n = 0, hits = 0;
        for (int c = 0; c < 2; c++)
            for (int d2 : new int[]{0, 63, 64, 65, 400, Integer.MAX_VALUE})
                for (int s = 0; s < 2; s++)
                    for (int t : new int[]{0, 1, 29, 30, 31, 1000}) {
                        n++;
                        boolean want = c == 0 && d2 <= 64 && s == 1 && t <= 30;
                        if (want) hits++;
                        check(Carrier.dropHit(c == 1, d2, s == 1, t) == want, "dropHit truth table " + c + " " + d2 + " " + s + " " + t);
                    }
        check(n == 144 && hits == 12, "truth table: 12 of 144 cases drop");

        // farAlt (Flee4Test 12)
        check(!Carrier.farAlt(90, 25), "raided at r2 25: an alternative at 90 is near");
        check(Carrier.farAlt(120, 25), "raided at r2 25: 120 is far (bar 100)");
        check(!Carrier.farAlt(100, 25) && Carrier.farAlt(101, 25), "the floor bar DROP_ALT_D2 is inclusive");
        check(!Carrier.farAlt(1600, 400) && Carrier.farAlt(1601, 400), "raided at r2 400: bar 1,600");
        check(!Carrier.farAlt(40000, Integer.MAX_VALUE) && Carrier.farAlt(40001, Integer.MAX_VALUE),
            "no HQ (Integer.MAX_VALUE): bar 40,000, no overflow");
        check(Carrier.farAlt(Integer.MAX_VALUE, 25), "no alternative distance: far");

        // backToRaided (Flee4Test 13): no alternative of the role (none, or the any-type fallback's) brings the raided
        // well back
        check(Carrier.backToRaided(true, 0, 25), "no well: back to the raided one");
        check(Carrier.backToRaided(true, 40, 25), "a near any-type well (home Ad for a mana carrier): back to the raided one");
        check(!Carrier.backToRaided(false, 90, 25), "a near alternative of the role: kept");
        check(Carrier.backToRaided(false, 120, 25), "a far alternative of the role: back to the raided one");
        for (int alt : new int[]{0, 16, 100, 101, 1600, Integer.MAX_VALUE})
            for (int raid : new int[]{0, 16, 25, 400, 10000, Integer.MAX_VALUE}) {
                check(Carrier.backToRaided(true, alt, raid), "no role alternative: always back (" + alt + ", " + raid + ")");
                check(Carrier.backToRaided(false, alt, raid) == Carrier.farAlt(alt, raid), "a role alternative: farAlt (" + alt + ", " + raid + ")");
            }
    }

    // ---------------------------------------------------------------- 3. noteFlight
    static void noteFlight() throws Exception {
        clear();
        int rng = rng();
        Carrier.well = W0; Carrier.role = 2; Carrier.wellType = 2;
        Carrier.prevState = 'G'; G.round = 100;
        Carrier.noteFlight(T1);
        check(Carrier.fWell == W0 && Carrier.fWellRound == 100 && Carrier.badWell == null, "first flight: counted for the well");
        check(Carrier.badUntil == 0 && Carrier.drops == 0, "first flight: no drop (91-93% of carriers flee before dying)");
        Carrier.prevState = 'F'; G.round = 101;
        Carrier.noteFlight(T1);
        check(Carrier.fWellRound == 100 && Carrier.drops == 0, "a continued flight (F last turn) does not count");
        Carrier.prevState = 'V'; G.round = 102;
        Carrier.noteFlight(T1);
        check(Carrier.fWellRound == 100 && Carrier.drops == 0, "a continued flight (V last turn) does not count");
        Carrier.prevState = 'G'; G.round = 115;
        Carrier.noteFlight(L(14, 19));                         // r2 81 from W0
        check(Carrier.fWellRound == 100 && Carrier.drops == 0, "a fighter beyond r2 DROP_WELL_R2 of the well does not count");
        G.round = 130;                                         // DROP_REPEAT rounds after the first
        Carrier.noteFlight(T1);
        check(Carrier.drops == 1 && Carrier.badAt == T1 && Carrier.badUntil == 130 + C.DROP_AVOID && !Carrier.badKeep,
            "second flight within DROP_REPEAT: dropped for DROP_AVOID rounds");
        check(Carrier.badD2 == 16, "the raided well's r2 to our nearest HQ: " + Carrier.badD2);
        check(Carrier.badWell == W0 && Carrier.badRole == 2 && Carrier.badType == 2, "the raided well, its role and type");
        check(",dw=1".equals(G.extra), "the indicator's drop counter: " + G.extra);
        check(Carrier.fWellRound == 130, "the second flight is the new last flight");
        check(!Carrier.hotPending && Carrier.hotUntil == 0 && Carrier.hotSpot == null, "noteFlight sets no hot mark");
        G.round = 161;                                         // 31 rounds later
        Carrier.badUntil = 0;
        Carrier.noteFlight(T1);
        check(Carrier.drops == 1 && Carrier.badUntil == 0 && Carrier.fWellRound == 161,
            "31 rounds after the last: counted again, no drop");
        G.round = 170;
        Carrier.well = A1;
        Carrier.noteFlight(L(10, 18));
        check(Carrier.drops == 1 && Carrier.fWell == A1 && Carrier.fWellRound == 170, "another well: counted for it, no drop");
        Carrier.well = null; G.round = 175;
        Carrier.noteFlight(T1);
        check(Carrier.fWell == A1 && Carrier.fWellRound == 170, "no well: nothing counted");

        // c_mid1's site and its twin (r2 C.MID_TWIN_R2) keep their own rules
        clear();
        shared[Comms.SYM_ELIM] = G.enc(L(30, 30)) << 3;
        for (MapLocation s : new MapLocation[]{L(30, 30), L(31, 31)}) {
            Carrier.fWell = null; Carrier.fWellRound = -1000;
            Carrier.well = s; Carrier.prevState = 'G';
            G.round = 300; Carrier.noteFlight(L(33, 30));
            G.round = 310; Carrier.noteFlight(L(33, 30));
            check(Carrier.fWell == null && Carrier.drops == 0 && Carrier.badUntil == 0, "site " + s + ": never counted");
        }
        Carrier.well = L(32, 30);                              // r2 4 from the site: neither site nor twin
        G.round = 300; Carrier.noteFlight(L(33, 30));
        G.round = 310; Carrier.noteFlight(L(33, 30));
        check(Carrier.drops == 1, "a well at r2 4 from the site counts as any other");
        shared[Comms.SYM_ELIM] = 0;
        check(rng() == rng, "noteFlight draws no RNG");
    }

    // ---------------------------------------------------------------- 4. the drop's span (hotLocal, anyHot)
    static void span() throws Exception {
        drop(130);
        int rng = rng();
        for (int r : new int[]{130, 150, 169}) {
            G.round = r; Carrier.hotRound = -1;
            check(Carrier.hotLocal(W0) && Carrier.hot(W0), "r" + r + ": the raided home well is hot for this carrier");
            check(Carrier.hotLocal(L(16, 16)), "r" + r + ": a well at r2 64 from the raided point too");
            check(!Carrier.hotLocal(L(16, 17)) && !Carrier.hotLocal(A1), "r" + r + ": r2 81 and 113 from it are not");
            check(Carrier.anyHot(), "r" + r + ": anyHot (the cool choice from home)");
        }
        G.round = 170; Carrier.hotRound = -1;
        check(!Carrier.hotLocal(W0) && !Carrier.hot(W0) && !Carrier.anyHot(), "r170: expired after DROP_AVOID rounds");
        G.round = 150; Carrier.badKeep = true; Carrier.hotRound = -1;
        check(!Carrier.hotLocal(W0) && !Carrier.anyHot(), "badKeep: the drop ended early (the carrier went back)");
        Carrier.badKeep = false;
        check(rng() == rng && writesSeen == 0 && !Carrier.hotPending, "no RNG draw, no write, no hot mark");

        // c_mid1's site (18,8) and twin (19,9), r2 4 and 10 from the raider: never dropped (their own rules)
        drop(130); G.round = 140;
        shared[Comms.SYM_ELIM] = G.enc(L(18, 8)) << 3;
        wells(W0, 2, L(19, 9), 2);
        check(!Carrier.hotLocal(L(18, 8)) && !Carrier.hotLocal(L(19, 9)), "the site and its twin near the raid: not hot");
        check(Carrier.hotLocal(W0) && Carrier.hotLocal(ADZ), "the other wells near the raid: hot");
        shared[Comms.SYM_ELIM] = 0;
    }

    // ---------------------------------------------------------------- 5. the choice under a drop (nearestCool, dropBack)
    static void choice() throws Exception {
        int rng = rng();
        // a near alternative of the role: chosen from home, and kept
        drop(130); G.round = 140;
        wells(W0, 2, A1, 2);
        check(A1.equals(Carrier.nearestCool(HQ0, 2)), "the raided W0 is skipped: the near A1 from home");
        Carrier.well = A1; lastWellDot = -1;
        Carrier.dropBack(false);
        check(Carrier.well == A1 && !Carrier.badKeep && lastWellDot == -1, "a near alternative of the role (r2 29): kept");
        Carrier.badKeep = true; Carrier.hotRound = -1;
        check(W0.equals(Carrier.nearestCool(HQ0, 2)), "no drop: c_hr1's choice, W0 nearest home");

        // a far alternative of the role: back to the raided well
        drop(130); G.round = 140;
        wells(W0, 2, A2, 2);
        check(A2.equals(Carrier.nearestCool(HQ0, 2)), "the far A2 is the only cool mana well");
        Carrier.well = A2; lastWellDot = -1;
        Carrier.dropBack(false);
        check(Carrier.well == W0 && Carrier.badKeep, "a far alternative (r2 256 > max(100, 4 x 16)): back to W0");
        check(lastWellDot >= 0 && (lastWellDot & 4095) == G.enc(W0) && (lastWellDot >> 14 & 7) == 0 && (lastWellDot >> 12 & 3) == 2,
            "WELL record source 0 (kept_hot), the raided well and its type");
        check(!Carrier.hotLocal(W0) && !Carrier.anyHot(), "after going back the well is no longer hot for it");

        // only another type near (the any-type fallback): back to the raided well
        drop(130); G.round = 140;
        wells(W0, 2, AD, 1);
        check(Carrier.nearestCool(HQ0, 2) == null && AD.equals(Carrier.nearestCool(HQ0, 0)), "only the Ad well is cool");
        Carrier.well = AD;
        Carrier.dropBack(true);
        check(Carrier.well == W0 && Carrier.badKeep, "the any-type fallback's well: back to W0");

        // nothing cool at all: back to the raided well, never 'X' (explore) or a wait
        drop(130); G.round = 140;
        wells(W0, 2);
        check(Carrier.nearestCool(HQ0, 2) == null && Carrier.nearestCool(HQ0, 0) == null, "nothing cool");
        Carrier.well = null;
        Carrier.dropBack(true);
        check(Carrier.well == W0 && Carrier.badKeep, "no well: back to W0 (no explore)");

        // a later single flight from another well recounts fWell but the drop's well stays the raided one
        drop(130); G.round = 140;
        Carrier.well = A1; Carrier.prevState = 'G';
        Carrier.noteFlight(L(10, 18));                         // r2 13 from A1: counted for A1, no drop
        check(Carrier.fWell == A1 && Carrier.badWell == W0 && Carrier.badUntil == 170 && Carrier.drops == 1,
            "a single flight from A1 during the drop: counted, the drop unchanged");
        wells(W0, 2, A2, 2);
        Carrier.well = A2;
        check(!Carrier.dropBack(false) && Carrier.well == W0 && Carrier.badKeep, "a far alternative: back to W0, not A1");

        // a role changed at a deposit: the drop does not hand the old role's well back; a near well of the new role
        // keeps the drop, none (or the any-type fallback's) ends it and asks for c_hr1's choice
        drop(130); G.round = 140;
        Carrier.role = 1; Carrier.well = AD;
        check(!Carrier.dropBack(false) && Carrier.well == AD && !Carrier.badKeep, "another role, a near well of it: kept");
        Carrier.well = null;
        check(Carrier.dropBack(true) && Carrier.well == null && Carrier.badKeep, "another role, no well: the drop ends");
        drop(130); G.round = 140;
        Carrier.role = 1; Carrier.well = A2;
        check(Carrier.dropBack(true) && Carrier.well == null && Carrier.badKeep,
            "another role, the any-type fallback's well: cleared, the drop ends");
        Carrier.role = 2;
        wells();
        check(rng() == rng && writesSeen == 0 && !Carrier.hotPending, "no RNG draw, no write, no hot mark");
    }

    // ---------------------------------------------------------------- 6. gather() under a drop (never 'X')
    /** One gather() turn of a mana carrier at (30,20) (far from every well; the proxy says not movement-ready, so it
     *  stays) with the drop of drop(130) on at round 140 and the wells lt shared. */
    static void gatherOnce(int role, Object... lt) throws Exception {
        drop(130); G.round = 140;
        wells(lt);
        G.here = L(30, 20);
        Carrier.role = role; Carrier.searchTurns = 0; Carrier.crowdTurns = 0;
        Carrier.probeDone = true; Carrier.probeRelease = false; Carrier.midHome = false; Carrier.returning = false;
        Carrier.state = '?';
        Carrier.gather();
    }

    static void gatherTurn() throws Exception {
        int rng = rng();
        gatherOnce(2, W0, 2, A1, 2);
        check(Carrier.state == 'G' && A1.equals(Carrier.well) && !Carrier.badKeep, "gather: the raided W0 dropped, the near A1");
        gatherOnce(2, W0, 2, A2, 2);
        check(Carrier.state == 'G' && W0.equals(Carrier.well) && Carrier.badKeep, "gather: only the far A2: back to W0");
        gatherOnce(2, W0, 2, AD, 1);
        check(Carrier.state == 'G' && W0.equals(Carrier.well) && Carrier.badKeep, "gather: only another type cool: back to W0");
        gatherOnce(2, W0, 2, ADZ, 1);
        check(Carrier.state == 'G' && W0.equals(Carrier.well) && Carrier.badKeep, "gather: nothing cool: back to W0, no 'X'");
        check(rng() == rng && writesSeen == 0 && !Carrier.hotPending, "gather under a drop: no RNG draw, no write, no hot mark");
        // a new role (Ad) whose only well is in the raid: the drop ends and c_hr1's choice takes it the same turn
        gatherOnce(1, W0, 2, ADZ, 1);
        check(Carrier.state == 'G' && ADZ.equals(Carrier.well) && Carrier.badKeep, "gather, a new role: c_hr1's ADZ, no 'X'");
        gatherOnce(1, W0, 2, ADZ, 1, A2, 2);
        check(Carrier.state == 'G' && ADZ.equals(Carrier.well) && Carrier.badKeep,
            "gather, a new role: not the any-type fallback's far mana A2, c_hr1's ADZ");
        gatherOnce(1, W0, 2, ADZ, 1, AD, 1);
        check(Carrier.state == 'G' && AD.equals(Carrier.well) && !Carrier.badKeep, "gather, a new role with a cool well of it: AD");
        Carrier.role = 2; G.here = L(12, 10);
        wells();
    }

    // ---------------------------------------------------------------- 7. no drop on: c_hr1's hotLocal and anyHot
    static void sameAsHr1() throws Exception {
        int rng = rng(), off = 0, on = 0, front = 0, diff = 0;
        for (int k = 0; k < 4000; k++) {
            clear();
            G.round = 1 + R.nextInt(1999);
            Carrier.hotSpot = R.nextInt(4) == 0 ? null : L(R.nextInt(60), R.nextInt(60));
            Carrier.hotUntil = Carrier.hotSpot == null ? 0 : G.round - 70 + R.nextInt(140);
            Carrier.midAvoidUntil = G.round - 70 + R.nextInt(140);
            shared[Comms.SYM_ELIM] = R.nextInt(3) == 0 ? G.enc(L(R.nextInt(60), R.nextInt(60))) << 3 : 0;
            for (int i = 0; i < Comms.NWELLS; i++) {
                if (R.nextInt(3) == 0) break;
                shared[Comms.WELLS + i] = (R.nextInt(4) == 0 ? 3 << 14 : 0) | (1 + R.nextInt(2)) << 12 | G.enc(L(R.nextInt(60), R.nextInt(60)));
            }
            boolean active = R.nextInt(3) == 0;
            Carrier.badAt = !active && R.nextInt(3) == 0 ? null : L(R.nextInt(60), R.nextInt(60));
            if (active) { Carrier.badUntil = G.round + 1 + R.nextInt(40); Carrier.badKeep = false; }
            else if (R.nextBoolean()) { Carrier.badUntil = G.round - R.nextInt(100); Carrier.badKeep = R.nextBoolean(); }
            else { Carrier.badUntil = G.round + 1 + R.nextInt(40); Carrier.badKeep = true; }
            Carrier.hotRound = -1; Carrier.ehqRound = -1;
            boolean any = Carrier.anyHot();
            Carrier.hotRound = -1;
            boolean refAny = refAnyHot();
            check(any == (refAny || active), "anyHot = c_hr1's or an active drop (k " + k + ")");
            for (int j = 0; j < 6; j++) {
                MapLocation l = j == 0 && Carrier.hotSpot != null ? Carrier.hotSpot.translate(R.nextInt(9) - 4, R.nextInt(9) - 4)
                    : j == 1 && Carrier.badAt != null ? Carrier.badAt.translate(R.nextInt(17) - 8, R.nextInt(17) - 8) : L(R.nextInt(60), R.nextInt(60));
                boolean ref = refHotLocal(l), got = Carrier.hotLocal(l);
                boolean want = ref || (active && l.distanceSquaredTo(Carrier.badAt) <= C.DROP_WELL_R2 && !Mid.isSite(l));
                check(got == want, "hotLocal = c_hr1's" + (active ? " or near the raided point" : "") + " at " + l + " (k " + k + ")");
                if (active) on++; else off++;
                if (ref && G.round < Carrier.hotUntil) front++;
                if (got != ref) diff++;
            }
        }
        check(off > 6000 && on > 3000 && front > 100 && diff > 100, "coverage: off " + off + ", on " + on + ", front hot " + front + ", drop-only " + diff);
        check(rng() == rng && writesSeen == 0, "no RNG draw, no write");
    }

    /** c_hr1's hotLocal, verbatim but for the class prefixes. */
    static boolean refHotLocal(MapLocation l) throws GameActionException {
        if (C.MID && G.round < Carrier.midAvoidUntil && Mid.isSite(l)) return true;
        return G.round < Carrier.hotUntil && l.distanceSquaredTo(Carrier.hotSpot) <= C.HOT_NEAR_D2 && Carrier.front(l);
    }

    /** c_hr1's anyHot, verbatim but for the class prefixes. */
    static boolean refAnyHot() throws GameActionException {
        if (G.round < Carrier.hotUntil) return true;
        Carrier.loadHot();
        return Carrier.nHot > 0;
    }

    // ---------------------------------------------------------------- harness
    /** A mana carrier on W0 that fled T1 at round r - 30 and again at round r: the drop is on until r + DROP_AVOID. */
    static void drop(int r) throws GameActionException {
        clear();
        Carrier.well = W0; Carrier.role = 2; Carrier.wellType = 2; Carrier.prevState = 'G';
        G.round = r - C.DROP_REPEAT; Carrier.noteFlight(T1);
        G.round = r; Carrier.noteFlight(T1);
        check(Carrier.badUntil == r + C.DROP_AVOID && !Carrier.badKeep && Carrier.badAt == T1, "drop at r" + r);
        Carrier.hotRound = -1;
    }

    /** The shared well list: location, type pairs (no hot bits). */
    static void wells(Object... lt) {
        for (int i = 0; i < Comms.NWELLS; i++) shared[Comms.WELLS + i] = 0;
        for (int i = 0; i < lt.length; i += 2) shared[Comms.WELLS + i / 2] = ((Integer) lt[i + 1]) << 12 | G.enc((MapLocation) lt[i]);
        Carrier.hotRound = -1;
    }

    static void clear() {
        java.util.Arrays.fill(shared, 0);
        Carrier.fWell = null; Carrier.badWell = null; Carrier.badAt = null;
        Carrier.fWellRound = -1000; Carrier.badRole = 0; Carrier.badType = 0; Carrier.badUntil = 0; Carrier.badD2 = 0;
        Carrier.badKeep = false; Carrier.drops = 0; G.extra = "";
        Carrier.hotSpot = null; Carrier.hotUntil = 0; Carrier.hotPending = false; Carrier.hotRound = -1;
        Carrier.midAvoidUntil = 0;
    }

    static RobotController proxy() {
        return (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
            new Class<?>[]{RobotController.class}, (p, m, args) -> {
                switch (m.getName()) {
                    case "readSharedArray": return shared[(Integer) args[0]];
                    case "canWriteSharedArray": return false;
                    case "writeSharedArray": writesSeen++; return null;
                    case "isMovementReady": return false;              // gather(): the carrier stays where it is
                    case "getLocation": return G.here;
                    case "setIndicatorDot":
                        MapLocation at = (MapLocation) args[0];
                        if (at.x == -2 - Telemetry.WELL) lastWellDot = at.y;
                        return null;
                    default: break;
                }
                throw new UnsupportedOperationException("engine call outside the test's proxy: " + m.getName());
            });
    }

    /** G's private RNG state (reflection). */
    static int rng() throws Exception {
        java.lang.reflect.Field f = G.class.getDeclaredField("rng");
        f.setAccessible(true);
        return f.getInt(null);
    }

    static MapLocation L(int x, int y) { return new MapLocation(x, y); }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
