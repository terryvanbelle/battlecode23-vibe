package c_uh1;

import battlecode.common.*;
import battlecode.world.Inventory;
import java.lang.reflect.Field;
import java.lang.reflect.Proxy;
import java.util.*;

/** c_uh1's UHIT arm (research/diagnosis/2026-10-18-launcher-micro-vs-strong.md, Plan 2) and its fighter memory, ported
 *  from c_blind2. The pure rules exhaustively (unseenHit, exitPick, shotKeepsNextTurn, EXIT_NEAR_R2), Blind2Test's
 *  memory cases with the age as a parameter, then cloudExit and uhitShot through a controlled RC and a reflected Clock.
 *  API bodies here are a decision fixture, not measured prices or native engine checks. */
public class Uh1Test {
    static final int N = C.MEM_N, AGE = C.UHIT_AGE;
    static final MapLocation HERE = new MapLocation(10, 10);
    static final List<String> calls = new ArrayList<>();
    static final List<MapLocation> attacks = new ArrayList<>();
    static final List<Direction> moves = new ArrayList<>();
    static final Map<MapLocation, RobotInfo> robots = new LinkedHashMap<>();
    static final Set<MapLocation> clouds = new LinkedHashSet<>(), walls = new LinkedHashSet<>();
    static MapLocation nativeHere;
    static double multiplier;
    static int checks, cooldown, moveCooldown, nativeRound, roundReads, advanceOnRead, senseReads, firstSenseBudget, health;
    /** run() probe: any RC call made under Launcher.cloudExit sets exitEntered; the first one under Launcher.fight or
     *  Launcher.march records it in stoppedIn and throws Stop (the fixture does not model those). */
    static boolean probe, exitEntered;
    static String stoppedIn;
    static final class Stop extends RuntimeException { Stop() { super(null, null, false, false); } }
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            String name = method.getName();
            String entry = name;
            if (args != null) for (Object arg : args) entry += ":" + arg;
            calls.add(entry);
            if (probe) for (StackTraceElement f : Thread.currentThread().getStackTrace()) {
                if (!f.getClassName().equals("c_uh1.Launcher")) continue;
                String m = f.getMethodName();
                if (m.equals("cloudExit")) exitEntered = true;
                if (m.equals("fight") || m.equals("march")) { stoppedIn = m; throw new Stop(); }
            }
            switch (name) {
                case "getHealth": return health;
                case "senseNearbyMapInfos": return new MapInfo[0];
                case "senseNearbyWells": return new WellInfo[0];
                case "senseNearbyIslands": return new int[0];
                case "readSharedArray": return 0;
                case "getRoundNum":
                    if (++roundReads == advanceOnRead) nativeRound++;
                    return nativeRound;
                case "getActionCooldownTurns": return cooldown;
                case "getLocation": return nativeHere;
                case "isActionReady": return cooldown < 10;
                case "isMovementReady": return moveCooldown < 10;
                case "onTheMap": return onMap((MapLocation) args[0]);
                case "senseCloud": {
                    MapLocation t = (MapLocation) args[0];
                    check(onMap(t), "senseCloud never off the map (the engine has no on-map check there)");
                    if (nativeHere.distanceSquaredTo(t) > (clouds.contains(nativeHere) ? 4 : 20))
                        throw new GameActionException(GameActionExceptionType.CANT_DO_THAT, "This location cannot be sensed");
                    return clouds.contains(t);
                }
                case "senseMapInfo":
                    check(nativeHere.equals(args[0]), "multiplier queried on the actual current tile");
                    return new MapInfo(nativeHere, clouds.contains(nativeHere), true, new double[]{multiplier, multiplier},
                        Direction.CENTER, new int[2][2], new int[2][2]);
                case "canMove": return movable((Direction) args[0]);
                case "move": {
                    Direction d = (Direction) args[0];
                    check(movable(d), "never forces an illegal move");
                    nativeHere = nativeHere.add(d);
                    moveCooldown += 20;
                    moves.add(d);
                    return null;
                }
                case "canSenseLocation": {
                    boolean sensed = sensable((MapLocation) args[0]);
                    if (++senseReads == 1 && firstSenseBudget >= 0) budget(firstSenseBudget);
                    return sensed;
                }
                case "canAttack": return legal((MapLocation) args[0]);
                case "canSenseRobot": {
                    int id = (Integer) args[0];
                    for (RobotInfo r : robots.values()) if (r.ID == id) return sensable(r.location);
                    return false;
                }
                case "senseNearbyRobots": {
                    Team team = args != null && args.length == 2 ? (Team) args[1] : null;
                    List<RobotInfo> seen = new ArrayList<>();
                    for (RobotInfo r : robots.values()) if ((team == null || r.team == team) && sensable(r.location)) seen.add(r);
                    return seen.toArray(new RobotInfo[0]);
                }
                case "attack": {
                    MapLocation target = (MapLocation) args[0];
                    check(legal(target), "never forces an illegal native attack");
                    attacks.add(target);
                    cooldown += (int) Math.round(10 * multiplier);
                    RobotInfo victim = robots.get(target);
                    if (victim != null && victim.team == Team.B && victim.type != RobotType.HEADQUARTERS) {
                        if (victim.health <= 20) robots.remove(target);
                        else robots.put(target, robot(victim.ID, victim.type, victim.health - 20, target));
                    }
                    return null;
                }
                default: throw new UnsupportedOperationException("unexpected call: " + name);
            }
        });

    public static void main(String[] args) throws Exception {
        // first, before any reset: the class initialisation is c_di1's (the memory is allocated by run's first turn)
        check(Launcher.memId == null && Launcher.memRound == null && Launcher.memLoc == null && Launcher.memDir == null,
            "class initialisation allocates no fighter memory");
        check(Launcher.lastHp == 0 && Launcher.lastHpRound == 0 && !Launcher.uhitNow, "no HP reading before the first turn");
        if (!Launcher.MEM) zeroDose();
        else {
            check(N >= 4 && Integer.bitCount(N) == 1 && N <= 16, "MEM_N is a power of two from 4 to 16 for these cases");
            check(AGE >= 3, "these cases use sightings up to 3 rounds old");
            check(C.UHIT_SCAN_LEFT < C.UHIT_MIN_LEFT, "the inner guard sits below the entry guard");
            // cloudExit's javadoc: at most about 1,600 bytecodes before the first scoring guard (8 open neighbours, 4 seen
            // enemy HQs, 8 near slots); entered below this margin it could pay that and score nothing
            check(C.UHIT_EXIT_LEFT - C.UHIT_SCAN_LEFT >= 1600, "the exit's entry bar covers its setup before the scoring guard");
            unseenHitAll(); exitPickAll(); shotRuleAll(); nearBound();
            allocation(); recordAndUpdate(); setReplacement(); pickAge(); pickVisibility(); pickRange(); pickOrder();
            extrapolation(); pickWall(); forget(); trackRecords(); shootForgetsKills();
            exitOffCloud(); exitThreat(); exitHome(); exitNone(); exitEdges(); exitAura(); exitBudget(); exitDrift();
            exitCostsAll();
            shotFromCloud(); shotRuleThroughRc(); shotStale(); shotVisibleOrGone(); shotFromOpenTile(); shotOverrun();
            shotGuard(); shotMostRecent(); shotAtWall();
            runFirstTurn(); runExitThenShot(); runExitBeforeFight(); runNoHitMarches(); runExitBudget(); runNotMovable();
            runShotGate();
        }
        System.out.println("Uh1Test PASS (" + checks + " checks)");
    }

    // ---- fixture
    static int mask() { return N / 2 - 1; }
    /** Three ids in set 0 and one in each of sets 1 and 2, for any N. */
    static final int A = 10000, B = 10000 + N / 2, CC = 10000 + N, D = 10001, E = 10002;
    static int slotOf(int id) { for (int s = 0; s < N; s++) if (Launcher.memId[s] == id && Launcher.memRound[s] > Launcher.MEM_NONE) return s; return -1; }
    static RobotInfo robot(int id, RobotType type, int hp, MapLocation loc) {
        return new RobotInfo(id, Team.B, type, new Inventory(), hp, loc);
    }
    static RobotInfo fighter(int id, int x, int y) { return robot(id, RobotType.LAUNCHER, 200, new MapLocation(x, y)); }
    static void see(int id, int x, int y, int round) { Launcher.remember(fighter(id, x, y), round); }
    static boolean onMap(MapLocation t) { return t.x >= 0 && t.y >= 0 && t.x < G.W && t.y < G.H; }
    static boolean sensable(MapLocation t) {
        if (!onMap(t)) return false;
        return nativeHere.distanceSquaredTo(t) <= (clouds.contains(nativeHere) || clouds.contains(t) ? 4 : 20);
    }
    static boolean legal(MapLocation t) { return cooldown < 10 && onMap(t) && nativeHere.distanceSquaredTo(t) <= 16; }
    static boolean movable(Direction d) {
        MapLocation t = nativeHere.add(d);
        return moveCooldown < 10 && d != Direction.CENTER && onMap(t) && !walls.contains(t) && !robots.containsKey(t);
    }
    static void reset() throws Exception {
        calls.clear(); attacks.clear(); moves.clear(); robots.clear(); clouds.clear(); walls.clear();
        multiplier = 1; cooldown = 0; moveCooldown = 0; nativeHere = HERE; nativeRound = 20;
        roundReads = senseReads = 0; advanceOnRead = -1; firstSenseBudget = -1; health = 200;
        probe = exitEntered = false; stoppedIn = null;
        G.rc = RC; G.id = 10003; G.round = 20; G.here = HERE; G.us = Team.A; G.them = Team.B;
        G.W = G.H = 30; G.enemies = G.nearby = new RobotInfo[0]; G.extra = ""; G.nEnemyFighters = G.nAllyFighters = 0;
        Launcher.shots = Launcher.uhitShots = Launcher.uhitExits = 0;
        Launcher.memReset(); Launcher.prevRound = -10; Launcher.nPrev = 0; Launcher.nPinned = 0; Launcher.firstTarget = 0;
        Launcher.lastHp = Launcher.lastHpRound = 0; Launcher.uhitNow = false; Launcher.mode = 0;
        MapMem.nEnemyHQSeen = 0; MapMem.tile = null; HQState.ourHQs = null; Nav.avoid = false; Comms.canWrite = false;
        set(G.class, "rng", 987654321); budget(10000);
    }
    static void noRng(String message) throws Exception { check((Integer) get(G.class, "rng") == 987654321, message + ": no RNG draw"); }
    static int bit(int id, boolean ext) { return slotOf(id) * 2 + (ext ? 1 : 0); }
    static void cloudBlock(int x0, int y0, int x1, int y1) {
        for (int x = x0; x <= x1; x++) for (int y = y0; y <= y1; y++) clouds.add(new MapLocation(x, y));
    }
    static int dirIndex(Direction d) { for (int k = 0; k < 8; k++) if (G.DIRS[k] == d) return k; return -1; }
    /** One mapped tile in MapMem's encoding (MapMem.process: bit 0 known, 1 wall, 2 cloud, bits 3-6 current + 1). */
    static void mapTile(int x, int y, boolean wall, boolean cloud, Direction cur) {
        if (MapMem.tile == null) MapMem.tile = new char[G.W * G.H];
        int c = 1 | (wall ? 2 : 0) | (cloud ? 4 : 0);
        if (cur != null && cur != Direction.CENTER) c |= (cur.ordinal() + 1) << 3;
        MapMem.tile[x + y * G.W] = (char) c;
    }
    static long count(String prefix) { return calls.stream().filter(c -> c.startsWith(prefix)).count(); }

    // ---- pure rules, exhaustive
    static void unseenHitAll() {
        for (int hp = 1; hp <= 200; hp++)
            for (int last = 0; last <= 200; last++)
                for (int gap = -1; gap <= 5; gap++)
                    for (int n = 0; n <= 3; n++) {
                        boolean got = Launcher.unseenHit(hp, last, 100 - gap, 100, n);
                        check(got == (hp < last && gap <= 2 && n == 0), "unseenHit " + hp + "/" + last + " gap " + gap + " n " + n);
                        if (hp >= last) check(!got, "unchanged or risen HP (island healing) is never a hit");
                        if (n > 0) check(!got, "a sensed fighter is never an unseen hit");
                    }
        for (int hp = 1; hp <= 200; hp++)
            for (int round = 1; round <= 2000; round++) {
                check(!Launcher.unseenHit(hp, 0, 0, round, 0), "first turn (class-init state) is never a hit");
                check(!Launcher.unseenHit(hp, 200, -10, round, 0), "first turn (plan's 200 / -10 state) is never a hit");
            }
    }

    static int exitRef(int movable, int cloud, int drift, int[] threat, int[] home) {
        int best = -1;
        for (int k = 0; k < 8; k++) {
            if ((movable >> k & 1) == 0 || (cloud >> k & 1) != 0) continue;
            if (best < 0) { best = k; continue; }
            int dk = drift >> k & 1, db = drift >> best & 1;
            if (dk < db || (dk == db && (threat[k] < threat[best] || (threat[k] == threat[best] && home[k] < home[best])))) best = k;
        }
        return best;
    }

    static void exitPickAll() {
        List<int[][]> cases = new ArrayList<>();
        cases.add(new int[][]{new int[8], new int[8]});
        cases.add(new int[][]{{7, 6, 5, 4, 3, 2, 1, 0}, {0, 0, 0, 0, 0, 0, 0, 0}});
        cases.add(new int[][]{{1, 1, 1, 1, 1, 1, 1, 1}, {9, 8, 7, 6, 5, 4, 3, 2}});
        cases.add(new int[][]{{0, 2, 0, 2, 0, 2, 0, 2}, {5, 1, 5, 1, 4, 1, 4, 1}});
        Random rnd = new Random(20261018);
        for (int c = 0; c < 8; c++) {
            int[] t = new int[8], h = new int[8];
            for (int k = 0; k < 8; k++) { t[k] = rnd.nextInt(3); h[k] = rnd.nextInt(4) * 37; }
            cases.add(new int[][]{t, h});
        }
        int[] drifts = {0, 0xff, 0x01, 0x0f, 0xa5, 0x5a, rnd.nextInt(256), rnd.nextInt(256)};
        for (int[][] tc : cases)
            for (int dr : drifts)
                for (int mv = 0; mv < 256; mv++)
                    for (int cl = 0; cl < 256; cl++) {
                        int k = Launcher.exitPick(mv, cl, dr, tc[0], tc[1]);
                        check((k == -1) == ((mv & ~cl) == 0), "exitPick -1 iff no open neighbour (a drift tile is still one)");
                        if (k >= 0) check((mv >> k & 1) == 1 && (cl >> k & 1) == 0, "exitPick never a blocked or cloud tile");
                        if (k >= 0 && (dr >> k & 1) == 1) check((mv & ~cl & ~dr) == 0, "a drift tile only when every open tile drifts");
                        check(k == exitRef(mv, cl, dr, tc[0], tc[1]), "no drift first, then fewest threats, then home r2, then the lowest index");
                    }
    }

    static void shotRuleAll() {
        for (int cd = 0; cd <= 29; cd++)
            for (int cost = 6; cost <= 14; cost++) {
                boolean ok = Launcher.shotKeepsNextTurn(cd, cost);
                int next = Math.max(0, cd + cost - 10);   // RULES 5.1: 10 off at the start of the next own turn
                check(ok == (cd < 10 && cd + cost < 20), "shotKeepsNextTurn cd " + cd + " cost " + cost);
                if (cd < 10) check(ok == (next < 10), "allowed exactly when the next own turn starts ready");
                else check(!ok, "never when the action is not ready now");
            }
        // every reachable rounded cost lies in the exhaustive range (multiplier 0.55..1.40, RULES 5.1)
        for (int m = 55; m <= 140; m++) {
            int cost = (int) Math.round(10 * (m / 100.0));
            check(cost >= 6 && cost <= 14, "launcher action cost " + cost + " at m " + m / 100.0 + " is in 6..14");
        }
    }

    static void nearBound() {
        check(C.THREAT_R2 == 26, "EXIT_NEAR_R2 is derived for THREAT_R2 26");
        boolean tight = false;
        for (int dx = -9; dx <= 9; dx++)
            for (int dy = -9; dy <= 9; dy++) {
                boolean reach = false;
                for (Direction d : G.DIRS) { int ax = dx - d.dx, ay = dy - d.dy; if (ax * ax + ay * ay <= C.THREAT_R2) reach = true; }
                int r2 = dx * dx + dy * dy;
                if (reach) check(r2 <= Launcher.EXIT_NEAR_R2, "a threat to some neighbour is within EXIT_NEAR_R2 of here");
                if (reach && r2 == Launcher.EXIT_NEAR_R2) tight = true;
            }
        check(tight, "EXIT_NEAR_R2 is tight");
    }

    // ---- fighter memory (Blind2Test's cases; the age is memPick's and memBlocked's parameter)
    static void allocation() throws Exception {
        Launcher.memReset();
        check(Launcher.memId.length == N && Launcher.memRound.length == N && Launcher.memLoc.length == N && Launcher.memDir.length == N,
            "memReset allocates MEM_N slots");
        for (int k = 0; k < N; k++) check(Launcher.memRound[k] == Launcher.MEM_NONE && Launcher.memLoc[k] == null, "every slot empty");
        check(Launcher.memLast == Launcher.MEM_NONE, "memLast empty");
    }

    static void recordAndUpdate() throws Exception {
        reset();
        see(A, 5, 5, 10);
        int s = slotOf(A);
        check(s == 2 * (A & mask()), "new id takes way 0 of its set");
        check(Launcher.memLoc[s].equals(new MapLocation(5, 5)) && Launcher.memRound[s] == 10 && Launcher.memDir[s] == null,
            "first sighting stored without a direction");
        see(A, 6, 5, 11);
        check(slotOf(A) == s && Launcher.memLoc[s].equals(new MapLocation(6, 5)) && Launcher.memRound[s] == 11, "same id updated in place");
        check(Launcher.memDir[s] == Direction.EAST, "observed step sets the last movement direction");
        see(A, 6, 5, 12);
        check(Launcher.memDir[s] == Direction.EAST && Launcher.memRound[s] == 12, "standing sighting keeps the last direction");
        see(A, 4, 7, 15);
        check(Launcher.memDir[s] == Direction.NORTHWEST, "multi-tile displacement keeps directionTo's heading");
        int used = 0;
        for (int k = 0; k < N; k++) if (Launcher.memId[k] == A) used++;
        check(used == 1, "an id never occupies two slots");
        check(Launcher.memLast == 15, "memLast follows the newest sighting");
        Launcher.memForget(A);
        check(Launcher.memLast == 15, "forgetting leaves memLast (conservative)");
        Launcher.memReset();
        check(Launcher.memLast == Launcher.MEM_NONE, "reset clears memLast");
        check(calls.isEmpty(), "recording makes no RC calls");
        noRng("recording");
    }

    static void setReplacement() throws Exception {
        reset();
        see(A, 1, 1, 10); see(B, 2, 2, 11);
        int w0 = 2 * (A & mask());
        check(slotOf(A) == w0 && slotOf(B) == w0 + 1, "second id of a set takes way 1");
        see(B, 3, 2, 12);
        check(slotOf(B) == w0 + 1 && Launcher.memDir[w0 + 1] == Direction.EAST, "way-1 id updated in place");
        see(CC, 4, 4, 13);
        check(slotOf(A) == -1 && slotOf(CC) == w0 && slotOf(B) == w0 + 1, "third id replaces the older way (way 0)");
        check(Launcher.memDir[w0] == null && Launcher.memLoc[w0].equals(new MapLocation(4, 4)), "replacement clears the old direction");
        see(A, 5, 5, 14);
        check(slotOf(B) == -1 && slotOf(A) == w0 + 1 && slotOf(CC) == w0, "older way 1 replaced next");
        reset();
        see(A, 1, 1, 10); see(B, 2, 2, 10); see(CC, 3, 3, 10);
        check(slotOf(CC) == w0 && slotOf(B) == w0 + 1, "same-round tie replaces way 0");
        see(D, 7, 7, 10);
        check(slotOf(D) == 2 * (D & mask()) && slotOf(CC) == w0, "another set is untouched");
    }

    static void pickAge() throws Exception {
        reset();
        see(A, 10, 13, 20);
        int b = bit(A, false);
        check(Launcher.memPick(20, HERE, 0, AGE) == b, "age 0 accepted");
        check(Launcher.memPick(20 + AGE, HERE, 0, AGE) == b, "age C.UHIT_AGE accepted");
        check(Launcher.memPick(21 + AGE, HERE, 0, AGE) == -1, "older than C.UHIT_AGE rejected");
        check(Launcher.memPick(22, HERE, 0, 1) == -1 && Launcher.memPick(21, HERE, 0, 1) == b, "the age is the caller's");
        reset();
        check(Launcher.memPick(1, HERE, 0, AGE) == -1 && Launcher.memPick(3, HERE, 0, AGE) == -1, "empty slots never picked, even early");
        noRng("age");
    }

    static void pickVisibility() throws Exception {
        // memBlocked: a remembered robot in vision now masks both bits; a sensable tile in range masks its own bit
        reset(); clouds.add(new MapLocation(10, 13)); clouds.add(new MapLocation(12, 12));
        see(A, 10, 13, 18); see(D, 12, 12, 19);
        int sa = slotOf(A), sd = slotOf(D);
        MapLocation dNow = new MapLocation(12, 14), car = new MapLocation(9, 9);
        robots.put(dNow, fighter(D, 12, 14)); robots.put(car, robot(55555, RobotType.CARRIER, 150, car));
        check(sensable(dNow), "fixture: D in vision now");
        int skip = Launcher.memBlocked(RC, 20, HERE, AGE);
        check(skip == 3 << (2 * sd), "robot in vision now masks both of its bits; a hidden remembered tile nothing");
        check(Launcher.memPick(20, HERE, 0, AGE) == bit(D, false), "without vision the newer sighting first");
        check(Launcher.memPick(20, HERE, skip, AGE) == 2 * sa, "robot in vision now is never a candidate");
        robots.remove(dNow);
        check(Launcher.memBlocked(RC, 20, HERE, AGE) == 0, "nothing in vision, every tile hidden: nothing masked");
        see(B, 11, 11, 19);
        robots.put(new MapLocation(13, 13), fighter(B, 13, 13));
        check(Launcher.memBlocked(RC, 20, HERE, AGE) == 3 << (2 * slotOf(B)), "way-1 id masked");
        reset(); clouds.add(new MapLocation(12, 11));
        see(A, 10, 11, 18); see(A, 11, 11, 19);      // remembered (11,11) clear and sensable; extrapolated (12,11) hidden
        check(Launcher.memBlocked(RC, 20, HERE, AGE) == 1 << bit(A, false), "sensable remembered tile masked, hidden extrapolation kept");
        reset(); clouds.add(new MapLocation(14, 10));
        see(A, 14, 10, 19); cooldown = 10;           // hidden but the attack is illegal (cooldown)
        check(Launcher.memBlocked(RC, 20, HERE, AGE) == 1 << bit(A, false), "an illegal attack is masked");
        reset();
        see(A, 18, 18, 19); see(D, 10, 13, 20 - AGE - 1);   // beyond r2 16; older than C.UHIT_AGE
        calls.clear();
        check(Launcher.memBlocked(RC, 20, HERE, AGE) == 0 && calls.isEmpty(), "out-of-range and expired slots cost no RC call");
        noRng("visibility");
    }

    static void pickRange() throws Exception {
        reset();
        see(A, 14, 10, 19);                     // d2 16 from HERE
        check(Launcher.memPick(20, HERE, 0, AGE) == bit(A, false), "remembered tile at r2 16 accepted");
        reset();
        see(A, 14, 11, 19);                     // d2 17
        check(Launcher.memPick(20, HERE, 0, AGE) == -1, "remembered tile beyond r2 16 rejected");
        check(Launcher.memPick(20, new MapLocation(11, 11), 0, AGE) == bit(A, false), "range measured from the launcher's position now");
    }

    static void pickOrder() throws Exception {
        reset();
        see(A, 10, 12, 17); see(D, 12, 10, 19); see(E, 8, 10, 18);
        int skip = 0, first = Launcher.memPick(20, HERE, skip, AGE);
        check(first == bit(D, false), "most recent sighting first");
        skip |= 1 << first;
        int second = Launcher.memPick(20, HERE, skip, AGE);
        check(second == bit(E, false), "then the next most recent");
        skip |= 1 << second;
        check(Launcher.memPick(20, HERE, skip, AGE) == bit(A, false), "then the oldest");
        check(Launcher.memPick(20, HERE, skip | 1 << bit(A, false), AGE) == -1, "every candidate skipped: none");
        reset();
        see(D, 12, 10, 18); see(E, 8, 10, 18);
        int lower = Math.min(slotOf(D), slotOf(E));
        check(Launcher.memPick(20, HERE, 0, AGE) == 2 * lower, "same-round tie: the lower slot");
        noRng("order");
    }

    static void extrapolation() throws Exception {
        reset();
        see(A, 10, 12, 17); see(A, 11, 12, 18);    // moving east, last seen (11,12) in round 18
        see(D, 8, 10, 18);
        int ra = bit(A, false), xa = bit(A, true), rd = bit(D, false);
        check(Launcher.memTile(xa).equals(new MapLocation(12, 12)), "extrapolated tile one step along the last direction");
        check(Launcher.memPick(20, HERE, 0, AGE) == Math.min(ra, rd), "a remembered tile before any extrapolated tile of its round");
        int skip = 1 << ra | 1 << rd;
        check(Launcher.memPick(20, HERE, skip, AGE) == xa, "extrapolated tile after every remembered tile of the round");
        see(E, 9, 9, 17);
        check(Launcher.memPick(20, HERE, skip, AGE) == xa, "a newer extrapolation before an older remembered tile");
        check(Launcher.memPick(20, HERE, skip | 1 << xa, AGE) == bit(E, false), "then the older sighting");
        reset();
        see(A, 10, 12, 19); see(A, 11, 12, 20);
        check(Launcher.memPick(20, HERE, 1 << bit(A, false), AGE) == -1, "no extrapolation for a sighting this round (it has not moved)");
        check(Launcher.memPick(21, HERE, 1 << bit(A, false), AGE) == bit(A, true), "extrapolated once a round old");
        reset();
        G.W = G.H = 14;
        see(A, 12, 10, 18); see(A, 13, 10, 19);    // moving east along the map edge x = 13
        check(Launcher.memPick(20, HERE, 1 << bit(A, false), AGE) == -1, "off-map extrapolation never offered");
        reset();
        see(A, 13, 10, 18); see(A, 14, 10, 19);    // remembered at r2 16, extrapolated (15,10) at r2 25
        check(Launcher.memPick(20, HERE, 0, AGE) == bit(A, false) && Launcher.memPick(20, HERE, 1 << bit(A, false), AGE) == -1,
            "extrapolated tile beyond r2 16 rejected");
        noRng("extrapolation");
    }

    static void pickWall() throws Exception {
        // review finding 3: an extrapolated tile that MapMem knows is a wall holds no robot (attacking it is legal, wasted)
        reset();
        see(A, 10, 11, 18); see(A, 10, 12, 19);      // moving north, extrapolated (10,13)
        int skip = 1 << bit(A, false);
        check(Launcher.memPick(20, HERE, skip, AGE) == bit(A, true), "fixture: unmapped extrapolated tile offered");
        mapTile(10, 13, false, true, null);
        check(Launcher.memPick(20, HERE, skip, AGE) == bit(A, true), "a mapped open (cloud) tile offered");
        mapTile(10, 13, true, false, null);
        check(MapMem.isWall(10, 13), "fixture: wall mapped");
        check(Launcher.memPick(20, HERE, skip, AGE) == -1, "an extrapolated tile mapped as a wall never offered");
        check(Launcher.memPick(20, HERE, 0, AGE) == bit(A, false), "the remembered tile itself unaffected");
        reset(); G.W = G.H = 14;
        see(A, 10, 12, 18); see(A, 10, 13, 19);      // north along the top edge: (10,14) at r2 16 indexes past the map
        mapTile(10, 13, false, false, null);
        check(Launcher.memPick(20, HERE, 1 << bit(A, false), AGE) == -1, "off-map extrapolation never offered, checked before the wall lookup");
        noRng("wall");
    }

    static void forget() throws Exception {
        reset();
        see(A, 10, 12, 19); see(B, 10, 8, 19);
        Launcher.memForget(B);
        check(slotOf(B) == -1 && slotOf(A) >= 0 && Launcher.memPick(20, HERE, 0, AGE) == bit(A, false), "forget clears one slot only");
        Launcher.memForget(99999);
        check(slotOf(A) >= 0, "forgetting an unknown id is a no-op");
        see(CC, 1, 1, 19);
        check(slotOf(CC) == 2 * (A & mask()) + 1, "a forgotten way is reused first");
    }

    static void trackRecords() throws Exception {
        reset();
        G.enemies = new RobotInfo[]{robot(20001, RobotType.CARRIER, 150, new MapLocation(9, 9)), fighter(A, 12, 12),
            robot(20002, RobotType.HEADQUARTERS, 1, new MapLocation(5, 5)), robot(D, RobotType.DESTABILIZER, 300, new MapLocation(8, 12)),
            robot(20003, RobotType.AMPLIFIER, 120, new MapLocation(11, 9)), robot(20004, RobotType.BOOSTER, 400, new MapLocation(9, 11))};
        Launcher.track();
        int n = 0;
        for (int k = 0; k < N; k++) if (Launcher.memRound[k] > Launcher.MEM_NONE) n++;
        check(n == 2 && slotOf(A) >= 0 && slotOf(D) >= 0, "only enemy launchers and destabilizers are remembered");
        check(Launcher.memRound[slotOf(A)] == 20 && Launcher.memLoc[slotOf(D)].equals(new MapLocation(8, 12)), "sighting at G.round");
        check(calls.isEmpty(), "track's recording makes no RC calls");
        G.round = 21; G.enemies = new RobotInfo[]{fighter(A, 13, 12)};
        Launcher.track();
        check(Launcher.memDir[slotOf(A)] == Direction.EAST && Launcher.memRound[slotOf(A)] == 21, "next turn updates in place");
        check(Launcher.memRound[slotOf(D)] == 20, "an unseen robot keeps its last sighting");
        reset();
        G.enemies = new RobotInfo[]{fighter(A, 12, 12)};
        budget(C.TRACK_MIN_LEFT - 1);
        Launcher.track();
        check(slotOf(A) == -1, "below track's guard nothing is recorded");
        reset();
        Launcher.track();
        for (int k = 0; k < N; k++) check(Launcher.memRound[k] == Launcher.MEM_NONE, "no enemy in vision records nothing");
        reset();
        RobotInfo[] many = new RobotInfo[C.TRACK_MAX + 3];
        for (int i = 0; i < many.length; i++) many[i] = fighter(30000 + i, 1 + i, 1);
        G.enemies = many;
        Launcher.track();
        int seen = 0;
        for (int i = 0; i < many.length; i++) for (int k = 0; k < N; k++) if (Launcher.memId[k] == 30000 + i && Launcher.memRound[k] == 20) { seen++; check(i < C.TRACK_MAX, "only track's first TRACK_MAX fighters are recorded"); }
        check(seen > 0, "a crowd is recorded up to TRACK_MAX");
        noRng("track");
    }

    static void shootForgetsKills() throws Exception {
        for (int hp : new int[]{20, 40}) {
            List<String> refCalls = null;
            List<MapLocation> refAttacks = null;
            for (boolean remembered : new boolean[]{false, true}) {
                reset();
                MapLocation at = new MapLocation(12, 11);
                robots.put(at, robot(A, RobotType.LAUNCHER, hp, at));
                MapLocation car = new MapLocation(9, 12);
                robots.put(car, robot(20001, RobotType.CARRIER, 30, car));
                if (remembered) see(A, 12, 11, 20);
                G.enemies = robots.values().toArray(new RobotInfo[0]);
                calls.clear();
                Launcher.shoot();
                if (!remembered) { refCalls = new ArrayList<>(calls); refAttacks = new ArrayList<>(attacks); }
                else {
                    check(refCalls.equals(calls) && refAttacks.equals(attacks), "memory never changes ordinary targeting, hp " + hp);
                    check(attacks.get(0).equals(at), "launcher first");
                    check((slotOf(A) == -1) == (hp <= 20), "a kill is forgotten, a survivor is kept, hp " + hp);
                }
            }
        }
        noRng("shoot");
    }

    // ---- cloudExit
    static void exitOffCloud() throws Exception {
        reset(); cloudBlock(11, 9, 11, 11);
        check(!Launcher.cloudExit() && moves.isEmpty(), "not on a cloud: no exit");
        check(calls.equals(Arrays.asList("getLocation", "senseCloud:" + HERE)), "not on a cloud: one senseCloud, nothing else");
        check(!Nav.avoid, "Nav.avoid untouched");
    }

    static void exitThreat() throws Exception {
        // a cloud bank with two open neighbours, west and east; a fighter seen east (tile within r2 26 of east only)
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(9, 10)); clouds.remove(new MapLocation(11, 10));
        see(A, 15, 11, 19);
        check(Launcher.cloudExit(), "an open neighbour: exit");
        check(moves.equals(Collections.singletonList(Direction.WEST)) && G.here.equals(new MapLocation(9, 10)) && !clouds.contains(nativeHere),
            "the open neighbour fewer remembered fighters reach");
        check(!Nav.avoid, "Nav.avoid restored");
        check(count("senseCloud") == 9 && count("onTheMap") == 8 && count("canMove") == 2, "8 neighbours sensed once; Nav.can only off clouds");
        noRng("exit threat");
        // the same with the fighter remembered too long ago: no threat, the lower index (EAST before WEST in G.DIRS)
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(9, 10)); clouds.remove(new MapLocation(11, 10));
        see(A, 15, 11, 20 - AGE - 1);
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.EAST)), "an expired sighting is no threat");
        // a sighting beyond EXIT_NEAR_R2 of here threatens no neighbour
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(9, 10)); clouds.remove(new MapLocation(11, 10));
        see(A, 16, 10, 19);                          // r2 36 from here, 25 from east: a threat
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.WEST)), "r2 25 of a neighbour is a threat");
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(9, 10)); clouds.remove(new MapLocation(11, 10));
        see(A, 17, 10, 19);                          // r2 49 from here, 36 from east
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.EAST)), "beyond r2 26 of every neighbour: no threat");
    }

    static void exitHome() throws Exception {
        // equal threats: the neighbour nearer our HQ nearest here; no HQs: the lowest index
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(10, 11)); clouds.remove(new MapLocation(10, 9));
        HQState.ourHQs = new MapLocation[]{new MapLocation(10, 0), new MapLocation(25, 25)};
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.SOUTH)), "toward our HQ nearest here");
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(10, 11)); clouds.remove(new MapLocation(10, 9));
        HQState.ourHQs = new MapLocation[]{null, new MapLocation(10, 29)};
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.NORTH)), "a null HQ entry skipped");
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(10, 11)); clouds.remove(new MapLocation(10, 9));
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.NORTH)), "no HQs: the lowest index (NORTH)");
        // threat outranks home
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(10, 11)); clouds.remove(new MapLocation(10, 9));
        HQState.ourHQs = new MapLocation[]{new MapLocation(10, 0)};
        see(A, 10, 4, 19);                           // r2 25 of the south neighbour, 49 of the north one
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.NORTH)), "fewer threats before home");
        noRng("exit home");
    }

    static void exitNone() throws Exception {
        reset(); cloudBlock(9, 9, 11, 11);
        check(!Launcher.cloudExit() && moves.isEmpty(), "every neighbour a cloud: no exit");
        check(count("canMove") == 0, "a cloud neighbour never pays Nav.can");
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(11, 10)); clouds.remove(new MapLocation(9, 10));
        walls.add(new MapLocation(11, 10));
        robots.put(new MapLocation(9, 10), robot(4242, RobotType.CARRIER, 60, new MapLocation(9, 10)));
        check(!Launcher.cloudExit() && moves.isEmpty(), "open tiles blocked by a wall and a robot: no exit");
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(11, 10)); moveCooldown = 10;
        check(!Launcher.cloudExit() && moves.isEmpty(), "movement not ready: canMove refuses, no exit");
        check(!Nav.avoid, "Nav.avoid restored");
    }

    static void exitEdges() throws Exception {
        int[][] corners = {{0, 0}, {29, 29}, {0, 29}, {29, 0}, {0, 15}, {15, 29}};
        for (int[] c : corners) {
            reset();
            MapLocation h = new MapLocation(c[0], c[1]);
            nativeHere = h; G.here = h; clouds.add(h);
            check(Launcher.cloudExit(), "an edge or corner cloud tile with open neighbours exits");
            check(onMap(nativeHere) && !clouds.contains(nativeHere), "onto an on-map open tile");
            int on = 0;
            for (Direction d : G.DIRS) if (onMap(h.add(d))) on++;
            // the fixture's senseCloud fails any off-map call; here: the own tile plus each on-map neighbour once
            check(count("senseCloud") == 1 + on && count("onTheMap") == 8, "every neighbour checked by onTheMap first");
        }
    }

    static void exitAura() throws Exception {
        // a seen enemy HQ at (10,13): here (r2 9) is inside its aura; north (r2 4) is a step inward, so Nav.can refuses it
        // even though our HQ is north; south (r2 16) is allowed
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(10, 11)); clouds.remove(new MapLocation(10, 9));
        HQState.ourHQs = new MapLocation[]{new MapLocation(10, 29)};
        MapMem.enemyHQSeen[0] = new MapLocation(10, 13); MapMem.nEnemyHQSeen = 1;
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.SOUTH)), "no step deeper into a seen enemy HQ's aura");
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(10, 11)); clouds.remove(new MapLocation(10, 9));
        HQState.ourHQs = new MapLocation[]{new MapLocation(10, 29)};
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.NORTH)), "fixture: without the HQ, north");
        MapMem.nEnemyHQSeen = 0;
    }

    static void exitBudget() throws Exception {
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(11, 10));
        budget(C.UHIT_SCAN_LEFT - 1);
        check(!Launcher.cloudExit() && moves.isEmpty(), "below the scoring guard: no neighbour scored, no move");
        check(!Nav.avoid, "Nav.avoid restored");
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(11, 10));
        budget(C.UHIT_SCAN_LEFT);
        check(Launcher.cloudExit() && moves.equals(Collections.singletonList(Direction.EAST)), "exact guard allowed");
        // exitPick takes only the scored bits: a neighbour left unscored is never chosen
        int[] t = new int[8], h = new int[8];
        reset(); budget(C.UHIT_SCAN_LEFT - 1);
        check(Launcher.exitCosts(0xff, HERE, 20, t, h) == 0, "nothing scored below the guard");
        reset();
        check(Launcher.exitCosts(0xa5, HERE, 20, t, h) == 0xa5, "every open neighbour scored above it");
    }

    /** Review finding 2: the two open neighbours of a 3x3 cloud bank, east (11,10) and west (9,10); east's current
     *  (mapped) pushes it to `to`, whose mapping is set by `mapTo` (0 unmapped, 1 mapped open, 2 mapped cloud). */
    static Direction driftCase(Direction cur, int mapTo, boolean westCurrentToCloud, boolean threatWest) throws Exception {
        reset(); cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(9, 10)); clouds.remove(new MapLocation(11, 10));
        mapTile(11, 10, false, false, cur);
        mapTile(9, 10, false, false, westCurrentToCloud ? Direction.WEST : null);
        if (westCurrentToCloud) { clouds.add(new MapLocation(8, 10)); mapTile(8, 10, false, true, null); }
        MapLocation to = new MapLocation(11, 10).add(cur);
        if (mapTo > 0 && !to.equals(HERE)) mapTile(to.x, to.y, false, mapTo == 2, null);
        if (mapTo == 2) clouds.add(to);
        mapTile(10, 10, false, true, null);
        if (threatWest) see(A, 5, 10, 19);           // r2 16 of west, 36 of east
        check(MapMem.current(11, 10) == cur, "fixture: current mapped");
        check(Launcher.cloudExit() && moves.size() == 1, "an exit");
        check(!Nav.avoid, "Nav.avoid restored");
        return moves.get(0);
    }

    static void exitDrift() throws Exception {
        check(driftCase(Direction.EAST, 2, false, false) == Direction.WEST, "a current onto a mapped cloud ranks after a still tile");
        check(driftCase(Direction.WEST, 2, false, false) == Direction.WEST, "a current straight back onto our cloud ranks last");
        check(driftCase(Direction.EAST, 0, false, false) == Direction.WEST, "a current onto an unmapped tile ranks last");
        check(driftCase(Direction.EAST, 1, false, false) == Direction.EAST, "a current onto a mapped open tile is no drift (lower index)");
        check(driftCase(Direction.NORTHEAST, 1, false, false) == Direction.EAST, "a diagonal current onto a mapped open tile: no drift");
        check(driftCase(Direction.EAST, 2, false, true) == Direction.WEST, "no drift before fewer threats");
        check(driftCase(Direction.EAST, 1, false, true) == Direction.EAST, "no drift on either side: fewer threats");
        check(driftCase(Direction.EAST, 2, true, false) == Direction.EAST, "every open tile drifts: still an exit, the lower index");
        noRng("exit drift");
        // exitCosts' drift bits sit above the scored bits, for scored neighbours only
        reset();
        mapTile(11, 10, false, false, Direction.EAST); mapTile(12, 10, false, true, null);   // east drifts
        mapTile(9, 10, false, false, Direction.NORTH);                                      // west pushes to unmapped (9,11)
        mapTile(10, 11, false, false, Direction.NORTH); mapTile(10, 12, false, false, null); // north pushes to mapped open
        int[] t = new int[8], h = new int[8];
        int e = dirIndex(Direction.EAST), w = dirIndex(Direction.WEST), n = dirIndex(Direction.NORTH);
        int open = 1 << e | 1 << w | 1 << n;
        check(Launcher.exitCosts(open, HERE, 20, t, h) == (open | (1 << e | 1 << w) << 8), "drift bits: east and west, not north");
        check(Launcher.exitCosts(1 << n, HERE, 20, t, h) == 1 << n, "only open neighbours get a drift bit");
        budget(C.UHIT_SCAN_LEFT - 1);
        check(Launcher.exitCosts(open, HERE, 20, t, h) == 0, "nothing scored, no drift bit, below the guard");
        check(calls.isEmpty(), "the drift test makes no RC calls");
    }

    static void exitCostsAll() throws Exception {
        // random memories against a brute-force count (no near filter): threat and home for every open neighbour
        Random rnd = new Random(42);
        for (int trial = 0; trial < 3000; trial++) {
            reset();
            int now = 20 + rnd.nextInt(5);
            MapLocation here = new MapLocation(3 + rnd.nextInt(24), 3 + rnd.nextInt(24));
            int k0 = rnd.nextInt(N + 3);
            for (int i = 0; i < k0; i++) see(40000 + rnd.nextInt(64), here.x - 8 + rnd.nextInt(17), here.y - 8 + rnd.nextInt(17), now - rnd.nextInt(AGE + 3));
            HQState.ourHQs = rnd.nextBoolean() ? null : new MapLocation[]{new MapLocation(rnd.nextInt(30), rnd.nextInt(30)), new MapLocation(rnd.nextInt(30), rnd.nextInt(30))};
            int open = rnd.nextInt(256);
            if (rnd.nextBoolean()) for (int x = here.x - 2; x <= here.x + 2; x++) for (int y = here.y - 2; y <= here.y + 2; y++)
                if (rnd.nextInt(4) > 0) mapTile(x, y, false, rnd.nextBoolean(), rnd.nextInt(3) == 0 ? G.DIRS[rnd.nextInt(8)] : null);
            int[] t = new int[8], h = new int[8];
            int drift = 0;
            for (int k = 0; k < 8; k++) {
                if ((open >> k & 1) == 0) continue;
                MapLocation n = here.add(G.DIRS[k]);
                Direction c = MapMem.current(n.x, n.y);
                MapLocation p = n.add(c);
                if (c != Direction.CENTER && (!MapMem.known(p.x, p.y) || MapMem.cloud(p.x, p.y))) drift |= 1 << k;
            }
            check(Launcher.exitCosts(open, here, now, t, h) == (open | drift << 8), "every open neighbour scored, drift bits above");
            MapLocation home = null;
            if (HQState.ourHQs != null) for (MapLocation q : HQState.ourHQs) if (home == null || here.distanceSquaredTo(q) < here.distanceSquaredTo(home)) home = q;
            for (int k = 0; k < 8; k++) {
                if ((open >> k & 1) == 0) { check(t[k] == 0 && h[k] == 0, "an unscored neighbour untouched"); continue; }
                MapLocation n = here.add(G.DIRS[k]);
                int want = 0;
                for (int s = 0; s < N; s++) if (now - Launcher.memRound[s] <= AGE && n.distanceSquaredTo(Launcher.memLoc[s]) <= C.THREAT_R2) want++;
                check(t[k] == want, "threat = fresh remembered fighters within r2 26 of the neighbour");
                check(h[k] == (home == null ? 0 : n.distanceSquaredTo(home)), "home = r2 to our HQ nearest here");
            }
            check(calls.isEmpty(), "exitCosts makes no RC calls");
        }
        noRng("exit costs");
    }

    // ---- uhitShot
    static void memFire(MapLocation target, String message) {
        check(attacks.size() == 1 && attacks.get(0).equals(target) && Launcher.uhitShots == 1 && Launcher.shots == 1, message);
    }

    static void shotFromCloud() throws Exception {
        // on an unboosted cloud (cost 12): the enemy last seen a round ago at r2 9 is hidden (vision r2 4)
        reset(); clouds.add(HERE); multiplier = 1.2; see(A, 13, 10, 19);
        Launcher.uhitShot(); memFire(new MapLocation(13, 10), "fires from a cloud at the remembered tile");
        check(cooldown == 12 && Math.max(0, cooldown - 10) < 10, "and the next own turn starts ready (c_blind2's DEBT 0 forbade it)");
        check(count("senseNearbyCloudLocations") == 0, "no cloud scan");
        reset(); clouds.add(HERE); multiplier = 1.2; see(A, 11, 11, 19);
        Launcher.uhitShot();
        check(attacks.isEmpty() && Launcher.uhitShots == 0, "a remembered tile within r2 4 of a cloud is sensable: no shot");
        noRng("shot from cloud");
    }

    static void shotRuleThroughRc() throws Exception {
        double[] ms = {0.55, 0.6, 0.7, 0.8, 0.9, 1.0, 1.05, 1.1, 1.2, 1.3, 1.4};
        for (double m : ms)
            for (int cd = 0; cd <= 9; cd++) {
                reset(); clouds.add(HERE); multiplier = m; cooldown = cd; see(A, 13, 10, 19);
                Launcher.uhitShot();
                int cost = (int) Math.round(10 * m);
                boolean want = cd + cost < 20;
                check((attacks.size() == 1) == want, "fires iff cd + cost < 20: cd " + cd + " m " + m);
                if (!want) check(count("canSenseRobot") == 0, "a refused cooldown checks no slot");
                else check(Math.max(0, cooldown - 10) < 10, "the next own turn starts ready");
            }
    }

    static void shotStale() throws Exception {
        reset(); clouds.add(HERE); see(A, 13, 10, 20 - AGE - 1);
        Launcher.uhitShot();
        check(attacks.isEmpty() && calls.isEmpty(), "no sighting within C.UHIT_AGE: no RC call at all");
        reset(); clouds.add(HERE);
        Launcher.uhitShot();
        check(attacks.isEmpty() && calls.isEmpty(), "empty memory: no RC call at all");
        reset(); clouds.add(HERE); see(A, 13, 10, 19); Launcher.memForget(A);
        Launcher.uhitShot();
        check(attacks.isEmpty() && count("canSenseRobot") == 0, "a forgotten robot is never checked or shot");
    }

    static void shotVisibleOrGone() throws Exception {
        // the remembered robot is in vision now (out of attack range): its old hidden tile is not a target
        reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 18);
        robots.put(new MapLocation(12, 14), fighter(A, 12, 14));
        check(sensable(new MapLocation(12, 14)) && !legal(new MapLocation(12, 14)), "fixture: visible, not attackable");
        Launcher.uhitShot();
        check(attacks.isEmpty(), "a robot in vision now is never shot from memory");
        // off a cloud, a remembered clear tile within r2 16 is sensable: the robot left, no shot
        reset(); see(A, 12, 12, 19);
        Launcher.uhitShot();
        check(attacks.isEmpty() && count("canSenseLocation") == 1, "a sensable empty remembered tile: no shot");
    }

    static void shotFromOpenTile() throws Exception {
        // after the exit: from an open tile, a remembered fighter on a cloud tile within r2 16 is hidden
        reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 18);
        Launcher.uhitShot(); memFire(new MapLocation(14, 10), "a hidden remembered cloud tile fired from an open tile");
        check(cooldown == 10, "clear tile: cost 10");
        // the extrapolated tile when the remembered one is clear and empty
        reset(); cloudBlock(13, 8, 15, 12); see(A, 11, 10, 17); see(A, 12, 10, 18);
        Launcher.uhitShot(); memFire(new MapLocation(13, 10), "sensable remembered tile skipped; hidden extrapolated tile fired");
        noRng("shot from open tile");
    }

    static void shotOverrun() throws Exception {
        reset(); clouds.add(HERE); see(A, 13, 10, 19); nativeRound = 21;
        Launcher.uhitShot();
        check(attacks.isEmpty() && count("canSenseRobot") == 0, "an overrun turn (round changed) does not fire");
        reset(); clouds.add(HERE); see(A, 13, 10, 19); advanceOnRead = 2;
        Launcher.uhitShot();
        check(attacks.isEmpty(), "a round change before the attack refuses");
    }

    static void shotGuard() throws Exception {
        reset(); clouds.add(HERE); see(A, 13, 10, 19);
        budget(C.UHIT_SCAN_LEFT - 1);
        Launcher.uhitShot();
        check(attacks.isEmpty() && count("canSenseRobot") == 0, "below the scan guard: no slot checked, no shot");
        reset(); cloudBlock(13, 8, 15, 12); see(A, 12, 10, 19); see(D, 13, 9, 18);
        firstSenseBudget = C.UHIT_SCAN_LEFT - 1;     // budget drops after the first (sensable) candidate
        Launcher.uhitShot();
        check(attacks.isEmpty() && senseReads == 1, "memBlocked stopped by the guard: never pick unchecked slots");
        reset(); cloudBlock(13, 8, 15, 12); see(A, 12, 10, 19); see(D, 13, 9, 18);
        budget(C.UHIT_SCAN_LEFT); firstSenseBudget = C.UHIT_SCAN_LEFT;
        Launcher.uhitShot(); memFire(new MapLocation(13, 9), "exact scan threshold allowed");
    }

    static void shotMostRecent() throws Exception {
        reset(); cloudBlock(6, 8, 7, 12); cloudBlock(13, 8, 14, 12);
        see(D, 6, 10, 17); see(A, 13, 9, 19); see(E, 13, 12, 18);
        Launcher.uhitShot(); memFire(new MapLocation(13, 9), "most recent hidden sighting fired");
        reset(); cloudBlock(6, 8, 7, 12);
        see(D, 6, 10, 17); see(A, 12, 10, 19);       // newest is on a clear tile in vision and absent: skipped
        Launcher.uhitShot(); memFire(new MapLocation(6, 10), "next most recent hidden sighting fired");
        noRng("most recent");
    }

    static void shotAtWall() throws Exception {
        // review finding 3 through uhitShot: on a cloud the remembered tile (r2 4) is sensable and empty; the robot's
        // extrapolated tile (r2 9, hidden) is a mapped wall: no shot (c_blind2 fired there); unmapped, it is fired at
        reset(); clouds.add(HERE); multiplier = 1.2;
        see(A, 10, 11, 18); see(A, 10, 12, 19);
        mapTile(10, 13, true, false, null);
        Launcher.uhitShot();
        check(attacks.isEmpty() && Launcher.uhitShots == 0, "never fires at a mapped wall");
        reset(); clouds.add(HERE); multiplier = 1.2;
        see(A, 10, 11, 18); see(A, 10, 12, 19);
        Launcher.uhitShot(); memFire(new MapLocation(10, 13), "fixture: the same tile unmapped is fired at");
    }

    // ---- run(): the wiring (review finding 4). Turn order: shoot, the trigger, the move block (exit before fight and
    // march), the re-sense and shoot, the memory shot, then the indicator suffix.
    static String extraPrefix() {
        return ",pn=" + Launcher.pinnedSeen + ",ua=" + Launcher.unsafeStepsAvoided + (C.ARMY ? ",rg=" + Launcher.regroups + ",fo=" + Launcher.follows : "");
    }
    /** One own turn at `round` with `hp`, as RobotPlayer calls it after G.startTurn; Stop (fight or march) ends it. */
    static void runTurn(int round, int hp) throws Exception {
        G.round = round; nativeRound = round; health = hp; G.here = nativeHere; G.extra = ",stale";   // nothing clears it between turns
        calls.clear(); attacks.clear(); moves.clear(); roundReads = 0;
        probe = true; exitEntered = false; stoppedIn = null;
        try { Launcher.run(); } catch (Stop s) { check(stoppedIn != null, "Stop only from fight or march"); }
        finally { probe = false; }
    }
    /** A 3x3 cloud bank around HERE with one open neighbour, east (11,10). */
    static void bank() { cloudBlock(9, 9, 11, 11); clouds.remove(new MapLocation(11, 10)); }

    static void runFirstTurn() throws Exception {
        reset(); bank(); moveCooldown = 10;
        runTurn(20, 200);
        check(!Launcher.uhitNow && Launcher.lastHp == 200 && Launcher.lastHpRound == 20, "first turn: HP and round recorded, no hit");
        check(!exitEntered && stoppedIn == null && moves.isEmpty(), "movement not ready: no move block");
        check(G.extra.equals(extraPrefix()), "no exit or shot: the indicator fields are c_di1's, no suffix");
        runTurn(21, 200);
        check(!Launcher.uhitNow && Launcher.lastHp == 200 && Launcher.lastHpRound == 21, "unchanged HP: no hit, the round updated");
        runTurn(22, 180);
        check(Launcher.uhitNow && Launcher.lastHp == 180 && Launcher.lastHpRound == 22, "lower HP a round later: a hit, both updated");
        runTurn(23, 190);
        check(!Launcher.uhitNow && Launcher.lastHp == 190 && Launcher.lastHpRound == 23, "risen HP (island healing): no hit");
        check(Launcher.uhitExits == 0 && Launcher.uhitShots == 0 && G.extra.equals(extraPrefix()), "nothing fired: no suffix");
        noRng("run first turn");
    }

    static void runExitThenShot() throws Exception {
        // turn 1 stands (movement not ready, no hit); turn 2 is hit unseen: it exits east, then fires from the open tile
        // at the remembered fighter on the cloud bank east of it (r2 9, hidden)
        reset(); bank(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 19); moveCooldown = 10;
        runTurn(20, 200);
        check(attacks.isEmpty() && Launcher.uhitShots == 0, "no hit: no memory shot");
        moveCooldown = 0;
        runTurn(21, 180);
        check(Launcher.uhitNow && exitEntered && stoppedIn == null, "a hit on the cloud: the exit, never fight or march");
        check(moves.equals(Collections.singletonList(Direction.EAST)) && nativeHere.equals(new MapLocation(11, 10)), "stepped off the cloud");
        check(Launcher.mode == 1 && Launcher.uhitExits == 1, "mode F, one exit counted");
        check(attacks.equals(Collections.singletonList(new MapLocation(14, 10))) && Launcher.uhitShots == 1, "then the memory shot");
        check(count("senseNearbyRobots") >= 1, "the re-sense after the move ran before the memory shot");
        check(Launcher.lastHp == 180 && Launcher.lastHpRound == 21, "HP and round recorded");
        check(G.extra.equals(extraPrefix() + ",ue=1,us=1"), "the suffix follows the unchanged indicator fields");
        noRng("run exit");
    }

    static void runExitBeforeFight() throws Exception {
        // a carrier in vision (hittable, not a fighter): the hit still counts as unseen and the exit runs before fight()
        for (boolean hit : new boolean[]{true, false}) {
            reset(); bank();
            MapLocation car = new MapLocation(9, 9);
            robots.put(car, robot(20001, RobotType.CARRIER, 150, car));
            G.enemies = robots.values().toArray(new RobotInfo[0]);
            Launcher.lastHp = 200; Launcher.lastHpRound = 20;
            runTurn(21, hit ? 180 : 200);
            check(attacks.equals(Collections.singletonList(car)), "the ordinary shot first");
            if (hit) {
                check(exitEntered && stoppedIn == null && moves.equals(Collections.singletonList(Direction.EAST)), "hit: the exit, not fight()");
                check(Launcher.uhitExits == 1 && Launcher.uhitShots == 0, "the action spent: no memory shot");
                check(G.extra.equals(extraPrefix() + ",ue=1,us=0"), "suffix with the exit only");
            } else {
                check(!exitEntered && "fight".equals(stoppedIn) && moves.isEmpty(), "no hit: fight(), no exit");
                check(Launcher.lastHp == 200 && Launcher.lastHpRound == 21, "HP recorded before the move block");
            }
        }
    }

    static void runNoHitMarches() throws Exception {
        int[][] cases = {{200, 20}, {210, 20}, {180, 18}};   // unchanged, risen, a hit three rounds ago (gap 3 > 2)
        for (int[] c : cases) {
            reset(); bank();
            Launcher.lastHp = 200; Launcher.lastHpRound = c[1];
            runTurn(21, c[0]);
            check(!Launcher.uhitNow && !exitEntered && "march".equals(stoppedIn) && moves.isEmpty(), "no unseen hit: march(), no exit");
            check(Launcher.lastHp == c[0] && Launcher.lastHpRound == 21, "HP and round recorded");
        }
    }

    static void runExitBudget() throws Exception {
        // review finding 1: from C.UHIT_MIN_LEFT up to C.UHIT_EXIT_LEFT the exit's setup could leave less than
        // C.UHIT_SCAN_LEFT for its first neighbour; it is not entered there
        for (int left : new int[]{C.UHIT_MIN_LEFT, C.UHIT_EXIT_LEFT - 1, C.UHIT_EXIT_LEFT}) {
            reset(); bank();
            Launcher.lastHp = 200; Launcher.lastHpRound = 20;
            budget(left);
            runTurn(21, 180);
            check(Launcher.uhitNow, "a hit");
            if (left < C.UHIT_EXIT_LEFT) check(!exitEntered && "march".equals(stoppedIn) && moves.isEmpty(), "below the exit's bar: march(), the exit not entered");
            else check(exitEntered && stoppedIn == null && moves.equals(Collections.singletonList(Direction.EAST)), "at the bar: the exit");
        }
    }

    static void runNotMovable() throws Exception {
        // movement not ready: no exit (and no fight or march); the memory shot from the cloud (cost 12, next turn ready)
        reset(); clouds.add(HERE); multiplier = 1.2; see(A, 13, 10, 19); moveCooldown = 10;
        Launcher.lastHp = 200; Launcher.lastHpRound = 20;
        runTurn(21, 180);
        check(Launcher.uhitNow && !exitEntered && stoppedIn == null && moves.isEmpty(), "no exit while movement is not ready");
        check(Launcher.mode == 0, "mode N");
        check(attacks.equals(Collections.singletonList(new MapLocation(13, 10))) && Launcher.uhitShots == 1, "the memory shot");
        check(G.extra.equals(extraPrefix() + ",ue=0,us=1"), "suffix with the shot only");
    }

    static void runShotGate() throws Exception {
        // the memory shot needs the hit, the action ready and C.UHIT_MIN_LEFT (uhitShot's own guard alone would fire)
        int[][] cases = {{200, 10000, 0}, {180, C.UHIT_MIN_LEFT - 1, 0}, {180, C.UHIT_MIN_LEFT, 0}, {180, 10000, 10}};
        for (int[] c : cases) {
            reset(); clouds.add(HERE); multiplier = 1.2; see(A, 13, 10, 19); moveCooldown = 10;
            Launcher.lastHp = 200; Launcher.lastHpRound = 20;
            budget(c[1]); cooldown = c[2];
            check(C.UHIT_MIN_LEFT - 1 >= C.UHIT_SCAN_LEFT, "fixture: uhitShot's inner guard passes at the outer bar minus one");
            runTurn(21, c[0]);
            boolean want = c[0] < 200 && c[1] >= C.UHIT_MIN_LEFT && c[2] < 10;
            check((attacks.size() == 1) == want && Launcher.uhitShots == (want ? 1 : 0), "memory shot iff hit, budget, ready: " + Arrays.toString(c));
            if (!want) check(count("getActionCooldownTurns") == 0, "uhitShot not entered");
        }
        noRng("run shot gate");
    }

    static void zeroDose() throws Exception {
        reset();
        G.enemies = new RobotInfo[]{fighter(A, 12, 12)};
        Launcher.memId = null; Launcher.memRound = null; Launcher.memLoc = null; Launcher.memDir = null;
        Launcher.track();
        Launcher.shoot();
        check(Launcher.memId == null, "compiled out: track and shoot never touch the memory");
    }

    static Object get(Class<?> cls, String name) throws Exception {
        Field field = cls.getDeclaredField(name); field.setAccessible(true); return field.get(null);
    }
    static void set(Class<?> cls, String name, Object value) throws Exception {
        Field field = cls.getDeclaredField(name); field.setAccessible(true); field.set(null, value);
    }
    static void budget(int value) {
        try {
            Field field = Class.forName("battlecode.instrumenter.inject.RobotMonitor").getDeclaredField("bytecodesLeft");
            field.setAccessible(true); field.setInt(null, value);
        } catch (Exception e) { throw new RuntimeException(e); }
    }
    static void check(boolean passed, String message) { checks++; if (!passed) throw new AssertionError(message); }
}
