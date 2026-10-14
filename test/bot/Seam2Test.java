package c_seam2;

import battlecode.common.*;
import battlecode.instrumenter.inject.RobotMonitor;
import java.lang.reflect.Proxy;
import java.util.Arrays;

/** Actual policy state transitions with a controlled RC/Clock. These are logical tests, not native price tests. */
public final class Seam2Test {
    static int checks, load, moves;
    static MapLocation here;
    static boolean moving;
    static final MapLocation HOME = new MapLocation(8, 12);
    static final int[] shared = new int[64];
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            switch (method.getName()) {
                case "getWeight": return load;
                case "getLocation": return here;
                case "getRoundNum": return G.round;
                case "isMovementReady": return moving;
                case "isActionReady": return false;
                case "canMove": return false;
                case "move": moves++; throw new AssertionError("blocked fixture must never move");
                case "readSharedArray": return shared[(Integer) args[0]];
                case "onTheMap": return G.onMap(((MapLocation) args[0]).x, ((MapLocation) args[0]).y);
                case "canSenseLocation": return true;
                case "sensePassability": return true;
                case "setIndicatorDot": case "setIndicatorString": case "setIndicatorLine": return null;
                default: throw new UnsupportedOperationException("unexpected policy call: " + method.getName());
            }
        });

    public static void main(String[] args) throws Exception {
        retirementAndAliases(); resetGates(); guardsAndExhaustion(); arrivalAndWalls(); trace(); knownWellGate();
        check(C.CROWD_SEARCH && C.CROWD_SEARCH_ROUNDS == 24 && C.CROWD_SEARCH_GUARD == 6000
            && C.CROWD_SCAN_RESERVE == 4000 && C.CROWD_RETREAT_ROUNDS == 16, "frozen policy dose and guards");
        check(C.WELL_CROWD_PATIENCE == c_mend2.C.WELL_CROWD_PATIENCE && C.ROLES == c_mend2.C.ROLES
            && C.CARRIER_RETURN_LOAD == c_mend2.C.CARRIER_RETURN_LOAD && C.CAP_MAX == c_mend2.C.CAP_MAX,
            "crowd trigger, roles, load and HQ cap parameters preserved");
        System.out.println("seam2: " + checks + " cases ok");
    }

    static void reset() throws Exception {
        G.rc = RC; G.W = G.H = 60; G.id = 123; G.type = RobotType.CARRIER; G.us = Team.A; G.them = Team.B;
        G.round = 50; here = G.here = new MapLocation(10, 12); load = moves = 0; moving = true;
        G.nearby = G.enemies = new RobotInfo[0]; G.nEnemyFighters = G.nAllyFighters = 0;
        HQState.ourHQs = new MapLocation[]{new MapLocation(0, 0), new MapLocation(6, 30),
            new MapLocation(7, 30), new MapLocation(11, 48)};
        Arrays.fill(shared, 0); shared[5] = 2 << 12 | G.enc(HOME); Comms.canWrite = false;
        MapMem.tile = null; MapMem.cand = 7; MapMem.decidedRound = -1; MapMem.nEnemyHQSeen = 0;
        set(MapMem.class, "nSeenWell", 0); set(MapMem.class, "nUnreported", 0);
        Field.target = null; Field.vis = Field.blk = null; Field.nWaves = 0; Field.pending = Field.stale = false; Field.init();
        Nav.target = null; Nav.bugging = Nav.fieldOn = false; Nav.fieldFor = null; Nav.stallFlips = Nav.sinceBest = 0; Nav.init();
        Carrier.role = 2; Carrier.well = null; Carrier.crowdRejected = HOME; Carrier.crowdExploreUntil = 74;
        Carrier.crowdWaypoint = Carrier.crowdWaypointLastPos = Carrier.crowdRetreatHome = Carrier.crowdOutcomeWell = null;
        Carrier.crowdRetreatUntil = Carrier.crowdWaypointStill = Carrier.crowdRetiredCount = 0;
        Carrier.crowdCursorInit = false; Carrier.crowdCursor = 0; Carrier.crowdRetired = null;
        Carrier.crowdSearchStarts = Carrier.crowdSearchTurns = Carrier.crowdSearchFound = 0;
        Carrier.crowdWaypointChecks = Carrier.crowdWaypointsReached = Carrier.crowdRetreats = 0;
        Carrier.crowdTurns = 6; Carrier.returning = false; Carrier.trips = 0; Carrier.searchTurns = 0;
        budget(12500);
    }

    static void seedRetired(MapLocation... points) {
        Carrier.crowdRetired = new MapLocation[8]; System.arraycopy(points, 0, Carrier.crowdRetired, 0, points.length);
        Carrier.crowdRetiredCount = points.length;
    }

    static void retirementAndAliases() throws Exception {
        reset(); seedRetired(new MapLocation(30, 48));
        Carrier.crowdExplore(); MapLocation first = Carrier.crowdWaypoint;
        check(new MapLocation(30, 30).equals(first), "best unretired goal has duplicate HQ-row projections");
        for (int i = 0; i < 2; i++) { G.round++; Carrier.crowdExplore(); check(first.equals(Carrier.crowdWaypoint), "goal persists before third stationary call"); }
        G.round++; Carrier.crowdExplore();
        check(Carrier.crowdWasRetired(first) && Carrier.crowdRetiredCount == 2, "blocked best retired once by coordinate");
        check(Carrier.crowdWaypoint != null && !first.equals(Carrier.crowdWaypoint), "distinct next goal excludes both aliases");
        check(!Carrier.crowdHQGoal(Carrier.crowdWaypoint), "a known occupied HQ is never a waypoint");
        check(moves == 0 && Carrier.crowdWaypointChecks <= 16, "blocked scan remains bounded");
    }

    static void resetGates() throws Exception {
        for (int kind = 0; kind < 3; kind++) {
            reset(); seedRetired(new MapLocation(30, 48));
            if (kind == 0) Carrier.role = 1; else if (kind == 1) load = 5; else Carrier.crowdExploreUntil = G.round;
            moving = false; Carrier.gather(); check(Carrier.crowdRetiredCount == 0, "role/cargo/expiry clears retired coordinates");
        }
        reset(); seedRetired(new MapLocation(30, 48)); Carrier.crowdRejected = null; Carrier.well = HOME; moving = false;
        Carrier.gather(); check(Carrier.crowdSearchStarts == 1 && Carrier.crowdRetiredCount == 0, "new episode clears old exclusions");
        reset(); seedRetired(new MapLocation(30, 48)); shared[6] = 2 << 12 | G.enc(new MapLocation(29, 48)); moving = false;
        Carrier.gather(); check(new MapLocation(29, 48).equals(Carrier.well) && Carrier.crowdRetiredCount == 0
            && Carrier.crowdRejected == null, "known new Mana ends search and retirement state");
        reset(); moving = false; Carrier.crowdExploreUntil = G.round; Carrier.gather();
        MapLocation fixed = Carrier.crowdRetreatHome; check(fixed != null && Carrier.trips == 0, "deadline begins direct HQ retreat without empty delivery trip");
        G.round++; Carrier.gather(); check(fixed.equals(Carrier.crowdRetreatHome), "retreat target stays fixed");
        G.round = Carrier.crowdRetreatUntil; Carrier.gather(); check(Carrier.crowdRetreatHome == null, "retreat expiry resumes ordinary behavior");
    }

    static void guardsAndExhaustion() throws Exception {
        reset(); budget(5999); Carrier.gather();
        check(Carrier.crowdWaypointChecks == 0 && Carrier.crowdSearchTurns == 0 && moves == 0, "entry guard defers additional scan/movement");
        reset(); budget(3999); Carrier.crowdExplore();
        check(Carrier.crowdWaypointChecks == 0 && Carrier.crowdWaypoint == null && moves == 0, "scan guard retains reserve");
        reset(); budget(4000); Carrier.crowdExplore(); check(Carrier.crowdWaypointChecks == 8, "exact controlled scan threshold admits finite HQ projection pass");
        reset(); seedRetired(new MapLocation(30, 0), new MapLocation(0, 30), new MapLocation(30, 30),
            new MapLocation(6, 30), new MapLocation(7, 30), new MapLocation(30, 48), new MapLocation(11, 30));
        Carrier.crowdExplore(); check(Carrier.crowdWaypoint == null && Carrier.state == 'W' && moves == 0
            && Carrier.crowdRetiredCount == 7, "all retired coordinates and aliases cause bounded wait");
    }

    static void arrivalAndWalls() throws Exception {
        reset(); Carrier.crowdWaypoint = here; Carrier.crowdExplore();
        check(Carrier.crowdWasRetired(here) && Carrier.crowdWaypointsReached == 1, "exact arrival retires coordinate");
        Carrier.crowdWaypoint = here; int count = Carrier.crowdRetiredCount; Carrier.crowdExplore();
        check(Carrier.crowdRetiredCount == count, "duplicate retirement does not consume another slot");
        reset(); MapLocation wall = new MapLocation(30, 30); Carrier.crowdWaypoint = wall;
        MapMem.tile = new char[3600]; MapMem.tile[wall.x + wall.y * 60] = 3; Carrier.crowdExplore();
        check(Carrier.crowdWasRetired(wall) && !wall.equals(Carrier.crowdWaypoint), "newly known wall cannot be reassigned");
    }

    static void trace() {
        int packed = Carrier.crowdTrace(1, 19, 1);
        check((packed >>> 20) == 1 && ((packed >>> 8) & 4095) == 19 && (packed & 255) == 1,
            "cx independently decodes starts/search-turns/first-new-site collects");
        check(Carrier.crowdTrace(99999, 99999, 99999) == 0x0fffffff, "cx saturates each component without signed overflow");
    }

    /** c_seam2: a search starts only when no Mana well other than the crowded one is in the shared array. */
    static void knownWellGate() throws Exception {
        reset();
        check(Carrier.crowdOtherManaKnown(HOME) == 0, "only the crowded well known: search allowed");
        shared[6] = 1 << 12 | G.enc(new MapLocation(30, 30));
        check(Carrier.crowdOtherManaKnown(HOME) == 0, "an Adamantium well is no alternative");
        shared[7] = 2 << 12 | G.enc(new MapLocation(40, 40));
        check(Carrier.crowdOtherManaKnown(HOME) == 1, "another Mana well known: no search");
        check(Carrier.crowdOtherManaKnown(new MapLocation(40, 40)) == 1, "the crowded one is excluded, HOME remains");
        shared[6] = 0;
        check(Carrier.crowdOtherManaKnown(HOME) == 0, "the list ends at the first empty slot");
    }

    static void budget(int left) throws Exception {
        RobotMonitor.setBytecodeLimit(12500); set(RobotMonitor.class, "bytecodesLeft", left); set(RobotMonitor.class, "bytecodesToRemove", 0);
    }
    static void set(Class<?> cls, String name, int value) throws Exception {
        java.lang.reflect.Field field = cls.getDeclaredField(name); field.setAccessible(true); field.setInt(null, value);
    }
    static void check(boolean ok, String message) { checks++; if (!ok) throw new AssertionError(message); }
}
