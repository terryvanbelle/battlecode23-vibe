package c_route1;

import battlecode.common.*;
import battlecode.instrumenter.inject.RobotMonitor;
import java.lang.reflect.Proxy;

/** Actual carrier guard/state transitions with controlled Clock input. Native movement, collection and real
 *  bytecode costs are checked separately; these tests do not treat an unmetered host call as a cost measurement. */
public class Route1Test {
    static int checks;
    static boolean movementReady, actionReady;
    static MapLocation here;
    static final MapLocation WELL = new MapLocation(20, 10);
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            switch (method.getName()) {
                case "isMovementReady": return movementReady;
                case "isActionReady": return actionReady;
                case "getLocation": return here;
                case "getWeight": return 0;
                default: throw new UnsupportedOperationException("unexpected engine call " + method.getName());
            }
        });

    public static void main(String[] args) throws Exception {
        memory(); gates(); recovery(); collectionExit(); recoveryTelemetry();
        check(C.CARRIER_RETURN_LOAD == c_mend2.C.CARRIER_RETURN_LOAD && C.WELL_CROWD_PATIENCE == c_mend2.C.WELL_CROWD_PATIENCE,
            "load and crowd policy unchanged");
        check(C.CAP_MAX == c_mend2.C.CAP_MAX && C.ROLES == c_mend2.C.ROLES && C.MEND_MIN_LEFT == c_mend2.C.MEND_MIN_LEFT,
            "HQ, role and healing parameters unchanged");
        System.out.println("route1: " + checks + " cases ok");
    }

    static void memory() {
        MapLocation other = new MapLocation(21, 10);
        Carrier.routeReset();
        check(!Carrier.routeTick(WELL, WELL, 3, 3, 10, true), "initial wave is progress");
        check(!Carrier.routeTick(WELL, WELL, 3, 4, 10, true) && Carrier.routeWaits == 1, "one stagnant eligible start");
        check(!Carrier.routeTick(WELL, WELL, 3, 4, 10, true) && Carrier.routeWaits == 1, "same round never counts twice");
        check(!Carrier.routeTick(WELL, WELL, 3, 5, 9, true) && Carrier.routeWaits == 0, "new best wave resets");
        check(!Carrier.routeTick(WELL, WELL, 3, 6, 10, true), "walking back does not improve best");
        check(!Carrier.routeTick(WELL, WELL, 3, 7, 10, true), "two non-improving starts");
        check(!Carrier.routeTick(WELL, WELL, 3, 8, 9, true), "equal best still does not improve");
        check(Carrier.routeTick(WELL, WELL, 3, 9, 9, true), "four starts without new best become due");
        check(!Carrier.routeTick(other, other, 3, 10, 9, true) && Carrier.routeWaits == 0, "nearby exact target change resets");
        check(!Carrier.routeTick(other, other, 4, 11, 9, true) && Carrier.routeWaits == 0, "new field epoch resets");
        check(!Carrier.routeTick(other, WELL, 4, 12, 9, true) && Carrier.routeWell == null, "nearby field is not exact well");
        check(!Carrier.routeTick(other, other, 4, 13, -1, true) && Carrier.routeWell == null, "unknown wave cannot poison progress");
        check(!Carrier.routeTick(other, other, 4, 14, 9, false) && Carrier.routeWell == null, "ineligible start clears memory");
        check(!Carrier.routeTick(other, other, 4, 15, 9, true) && Carrier.routeBest == 9, "valid route after gap starts fresh");
    }

    static void reset() throws Exception {
        G.rc = RC; G.W = G.H = 60; G.id = 12004; G.type = RobotType.CARRIER;
        here = G.here = new MapLocation(10, 10); G.round = 50;
        movementReady = true; actionReady = false;
        MapMem.tile = new char[G.W * G.H]; MapMem.cand = 0; MapMem.nEnemyHQSeen = 0;
        HQState.ourHQs = new MapLocation[0];
        Field.target = null; Field.vis = null; Field.nWaves = 0; Field.usedRound = Field.startRound = -1000;
        Field.init(); budget(100000); Field.request(WELL, true); Field.think(1500);
        Nav.fieldOn = true; Nav.fieldFor = WELL; Nav.target = WELL;
        Nav.bugging = false; Nav.left = true; Nav.bugMoves = Nav.bugFlips = 0;
        Carrier.well = WELL; Carrier.role = 2; Carrier.state = 'G'; Carrier.returning = false;
        Carrier.routeReset(); Carrier.routeRecoveries = 0;
        budget(10000);
    }

    static void gated(String why) throws Exception {
        Carrier.routeUpdate(WELL);
        check(Carrier.routeWell == null && Carrier.routeLock == null && Carrier.routeRecoveries == 0, why);
        check(!Nav.bugging, why + ": ordinary bug state unchanged");
    }

    static void gates() throws Exception {
        reset(); budget(C.CARRIER_ROUTE_MIN_LEFT - 1); gated("entry budget below guard");
        reset(); budget(C.CARRIER_ROUTE_MIN_LEFT); Carrier.routeUpdate(WELL);
        check(WELL.equals(Carrier.routeWell), "entry budget at guard can record progress");
        reset(); movementReady = false; gated("movement cooldown");
        reset(); Nav.fieldOn = false; gated("greedy route without active field");
        reset(); Nav.fieldFor = new MapLocation(21, 10); gated("Nav field identity differs");
        reset(); Field.target = new MapLocation(21, 10); gated("nearby target field is not exact");
        reset(); Field.nWaves = 0; gated("fresh/pending field");
        reset(); Field.vis[here.y] &= ~(1L << here.x); gated("partial field does not reach current tile");
        reset(); here = G.here = new MapLocation(18, 8); gated("distance squared eight stays with crowd policy");
        reset(); here = G.here = new MapLocation(17, 10); Carrier.routeUpdate(WELL);
        check(WELL.equals(Carrier.routeWell), "distance squared nine is an eligible route");
        reset(); Carrier.routeUpdate(null);
        check(Carrier.routeWell == null && Carrier.routeLock == null, "absent exact target clears memory");
        reset(); Carrier.routeUpdate(WELL); G.round++; Carrier.routeUpdate(WELL);
        Field.startRound++; G.round++; Carrier.routeUpdate(WELL);
        check(Carrier.routeWaits == 0, "actual guard notices rebuilt field epoch");
    }

    static void recovery() throws Exception {
        reset();
        int initialWave = Field.level(here.x, here.y);
        for (int r = 50; r < 54; r++) {
            G.round = r; Carrier.routeUpdate(WELL);
            check(Carrier.routeLock == null && !Nav.bugging, "unimproved start " + r + " does not recover early");
        }
        G.round = 54; Carrier.routeUpdate(WELL);
        check(WELL.equals(Carrier.routeLock) && Carrier.routeRecoveries == 1, "fifth valid start triggers four-round stagnation");
        check(Nav.bugging && !Nav.fieldOn && Nav.left, "ordinary bug entry preserves original hand");
        check(WELL.equals(Nav.target) && here.directionTo(WELL) == Nav.bugDir && Nav.bugStartDist == Nav.score(here, WELL),
            "normal bug target and entry geometry initialized");
        check(Nav.bugMoves == 0 && Nav.bugFlips == 0 && here.equals(Nav.bugStart) && Nav.bugStartRound == 54 && Nav.bugEpMoves == 0,
            "movement and telemetry episode start initialized");
        check(Carrier.routeBest == initialWave, "entry uses observed current wave");
        budget(1); G.round++; Field.startRound++; Carrier.routeUpdate(WELL);
        check(WELL.equals(Carrier.routeLock) && Carrier.routeRecoveries == 1, "existing lock is not repeated or dropped on new epoch/low budget");
        Carrier.routeUpdate(new MapLocation(21, 10));
        check(Carrier.routeLock == null && Carrier.routeWell == null, "exact changed target releases old lock");
    }

    static void collectionExit() throws Exception {
        reset(); Carrier.routeLock = WELL;
        here = G.here = new MapLocation(20, 9); Carrier.gather();
        check(Carrier.state == 'C' && Carrier.routeLock == null && Carrier.routeWell == null, "actual gather collection footprint releases lock");
    }

    static void recoveryTelemetry() throws Exception {
        reset(); Carrier.anchorTarget = null; Carrier.routeRecoveries = 12;
        Carrier.note();
        check(G.extra.equals(",rr=12"), "actual carrier note publishes cumulative recovery count");
        String indicator = Telemetry.indicatorString('G', Telemetry.code, G.note, 0, 0, 0, 4, 1999, 2000, 2000, G.extra);
        check(indicator.endsWith(",rr=12") && indicator.length() <= 64, "healthy late-game indicator preserves visible recovery counter");
        Carrier.routeReset(); Carrier.state = 'D'; Carrier.note();
        check(G.extra.equals(",rr=12"), "delivery/route reset retains the cumulative decision counter");
        budget(C.IND_GUARD + 199); Carrier.note();
        check(G.extra.equals(""), "short note defers extra formatting and clears stale suffix");
        budget(C.IND_GUARD + 200); Carrier.note();
        check(G.extra.equals(",rr=12"), "note formatting admission boundary includes recovery count");
        Carrier.routeRecoveries = 0; Carrier.note();
        check(G.extra.equals(",rr=0"), "normal carrier reports explicit zero decisions");
    }

    static void budget(int left) throws Exception {
        java.lang.reflect.Field f = RobotMonitor.class.getDeclaredField("bytecodesLeft");
        f.setAccessible(true); f.setInt(null, left); RobotMonitor.setBytecodeLimit(12500);
    }
    static void check(boolean ok, String message) {
        checks++; if (!ok) throw new AssertionError(message);
    }
}
