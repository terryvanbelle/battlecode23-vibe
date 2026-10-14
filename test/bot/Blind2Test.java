package c_blind2;

import battlecode.common.*;
import battlecode.world.Inventory;
import java.lang.reflect.Field;
import java.lang.reflect.Proxy;
import java.util.*;

/** c_blind2's memory arm. Pure candidate selection (age, visibility, range, most recent first, id update, set
 *  replacement, extrapolation) under a fake round, then track()'s recording, blindShot and shoot() through a controlled
 *  RC and a reflected Clock. API bodies here are a decision fixture, not measured prices or native engine checks. */
public class Blind2Test {
    static final int N = C.BLIND_MEM_N, AGE = C.BLIND_MEM_AGE;
    static final MapLocation HERE = new MapLocation(10, 10);
    static final List<String> calls = new ArrayList<>();
    static final List<MapLocation> attacks = new ArrayList<>();
    static final Map<MapLocation, RobotInfo> robots = new LinkedHashMap<>();
    static final Set<MapLocation> clouds = new LinkedHashSet<>();
    static MapLocation nativeHere;
    static double multiplier;
    static int checks, cooldown, nativeRound, roundReads, advanceOnRead, senseReads, firstSenseBudget, mapInfoBudget;
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            String name = method.getName();
            String entry = name;
            if (args != null) for (Object arg : args) entry += ":" + arg;
            calls.add(entry);
            switch (name) {
                case "getRoundNum":
                    if (++roundReads == advanceOnRead) nativeRound++;
                    return nativeRound;
                case "getActionCooldownTurns": return cooldown;
                case "getLocation": return nativeHere;
                case "isActionReady": return cooldown < 10;
                case "senseMapInfo":
                    check(nativeHere.equals(args[0]), "multiplier queried on the actual current tile");
                    if (mapInfoBudget >= 0) budget(mapInfoBudget);
                    return new MapInfo(nativeHere, clouds.contains(nativeHere), true, new double[]{multiplier, multiplier},
                        Direction.CENTER, new int[2][2], new int[2][2]);
                case "senseNearbyCloudLocations": {
                    int r2 = clouds.contains(nativeHere) ? Math.min(4, (Integer) args[0]) : (Integer) args[0];
                    List<MapLocation> out = new ArrayList<>();
                    for (MapLocation c : clouds) if (nativeHere.distanceSquaredTo(c) <= r2) out.add(c);
                    return out.toArray(new MapLocation[0]);
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
        if (!Launcher.MEM) zeroDose();
        else {
            check(N >= 4 && Integer.bitCount(N) == 1 && N <= 16, "BLIND_MEM_N is a power of two from 4 to 16 for these cases");
            check(AGE >= 3, "these cases use sightings up to 3 rounds old");
            recordAndUpdate(); setReplacement(); pickAge(); pickVisibility(); pickRange(); pickOrder(); extrapolation();
            forget(); trackRecords(); blindFromCloud(); blindClearSource(); blindVisibleSkipped(); blindFallback();
            blindMostRecent(); blindFutile(); blindGuards(); blindStatsSuffix(); shootForgetsKills();
        }
        System.out.println("blind2 mem " + N + " age " + AGE + " debt " + C.BLIND_MEM_DEBT + ": " + checks + " checks ok");
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
    static boolean sensable(MapLocation t) {
        if (t.x < 0 || t.y < 0 || t.x >= G.W || t.y >= G.H) return false;
        return nativeHere.distanceSquaredTo(t) <= (clouds.contains(nativeHere) || clouds.contains(t) ? 4 : 20);
    }
    static boolean legal(MapLocation t) {
        return cooldown < 10 && t.x >= 0 && t.y >= 0 && t.x < G.W && t.y < G.H && nativeHere.distanceSquaredTo(t) <= 16;
    }
    static void reset() throws Exception {
        calls.clear(); attacks.clear(); robots.clear(); clouds.clear();
        multiplier = 1; cooldown = 0; nativeHere = HERE; nativeRound = 20;
        roundReads = senseReads = 0; advanceOnRead = -1; firstSenseBudget = mapInfoBudget = -1;
        G.rc = RC; G.id = 10003; G.round = 20; G.here = HERE; G.us = Team.A; G.them = Team.B;
        G.W = G.H = 30; G.enemies = G.nearby = new RobotInfo[0]; G.extra = ",pn=0,ua=0,rg=0,fo=0";
        Launcher.shots = Launcher.blindShots = Launcher.blindMemShots = Launcher.blindChecks = Launcher.blindEligible = 0;
        Launcher.blindBudgetSkipped = Launcher.blindCooldownSkipped = Launcher.blindNoTarget = Launcher.blindStale = 0;
        Launcher.memReset(); Launcher.prevRound = -10; Launcher.nPrev = 0; Launcher.nPinned = 0; Launcher.firstTarget = 0;
        set(G.class, "rng", 987654321); budget(10000);
    }
    static void noRng(String message) throws Exception { check((Integer) get(G.class, "rng") == 987654321, message + ": no RNG draw"); }
    static int bit(int id, boolean ext) { return slotOf(id) * 2 + (ext ? 1 : 0); }

    // ---- pure helpers
    static void recordAndUpdate() throws Exception {
        reset();
        see(A, 5, 5, 10);
        int s = slotOf(A);
        check(s == 2 * (A & mask()), "new id takes way 0 of its set");
        check(Launcher.memLoc[s].equals(new MapLocation(5, 5)) && Launcher.memRound[s] == 10 && Launcher.memDir[s] == null,
            "first sighting stored without a direction");
        see(A, 6, 5, 11);
        check(slotOf(A) == s && Launcher.memLoc[s].equals(new MapLocation(6, 5)) && Launcher.memRound[s] == 11,
            "same id updated in place");
        check(Launcher.memDir[s] == Direction.EAST, "observed step sets the last movement direction");
        see(A, 6, 5, 12);
        check(Launcher.memDir[s] == Direction.EAST && Launcher.memRound[s] == 12, "standing sighting keeps the last direction");
        see(A, 4, 7, 15);
        check(Launcher.memDir[s] == new MapLocation(6, 5).directionTo(new MapLocation(4, 7)) && Launcher.memDir[s] == Direction.NORTHWEST,
            "multi-tile displacement keeps directionTo's heading");
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
        check(Launcher.memPick(20, HERE, 0) == b, "age 0 accepted");
        check(Launcher.memPick(20 + AGE, HERE, 0) == b, "age C.BLIND_MEM_AGE accepted");
        check(Launcher.memPick(21 + AGE, HERE, 0) == -1, "older than C.BLIND_MEM_AGE rejected");
        reset();
        check(Launcher.memPick(1, HERE, 0) == -1 && Launcher.memPick(3, HERE, 0) == -1, "empty slots never picked, even early");
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
        int skip = Launcher.memBlocked(RC, 20, HERE);
        check(skip == 3 << (2 * sd), "robot in vision now masks both of its bits; a hidden remembered tile nothing");
        check(Launcher.memPick(20, HERE, 0) == bit(D, false), "without vision the newer sighting first");
        check(Launcher.memPick(20, HERE, skip) == 2 * sa, "robot in vision now is never a candidate");
        robots.remove(dNow);
        check(Launcher.memBlocked(RC, 20, HERE) == 0, "nothing in vision, every tile hidden: nothing masked");
        see(B, 11, 11, 19);
        robots.put(new MapLocation(13, 13), fighter(B, 13, 13));
        check(Launcher.memBlocked(RC, 20, HERE) == 3 << (2 * slotOf(B)), "way-1 id masked");
        reset(); clouds.add(new MapLocation(12, 11));
        see(A, 10, 11, 18); see(A, 11, 11, 19);      // remembered (11,11) clear and sensable; extrapolated (12,11) hidden
        check(Launcher.memBlocked(RC, 20, HERE) == 1 << bit(A, false), "sensable remembered tile masked, hidden extrapolation kept");
        reset(); clouds.add(new MapLocation(14, 10));
        see(A, 14, 10, 19); cooldown = 10;           // hidden but the attack is illegal (cooldown)
        check(Launcher.memBlocked(RC, 20, HERE) == 1 << bit(A, false), "an illegal attack is masked");
        reset();
        see(A, 18, 18, 19); see(D, 10, 13, 20 - AGE - 1);   // beyond r2 16; older than C.BLIND_MEM_AGE
        calls.clear();
        check(Launcher.memBlocked(RC, 20, HERE) == 0 && calls.isEmpty(), "out-of-range and expired slots cost no RC call");
        noRng("visibility");
    }

    static void pickRange() throws Exception {
        reset();
        see(A, 14, 10, 19);                     // d2 16 from HERE
        check(Launcher.memPick(20, HERE, 0) == bit(A, false), "remembered tile at r2 16 accepted");
        reset();
        see(A, 14, 11, 19);                     // d2 17
        check(Launcher.memPick(20, HERE, 0) == -1, "remembered tile beyond r2 16 rejected");
        check(Launcher.memPick(20, new MapLocation(11, 11), 0) == bit(A, false), "range measured from the launcher's position now");
    }

    static void pickOrder() throws Exception {
        reset();
        see(A, 10, 12, 17); see(D, 12, 10, 19); see(E, 8, 10, 18);
        int skip = 0, first = Launcher.memPick(20, HERE, skip);
        check(first == bit(D, false), "most recent sighting first");
        skip |= 1 << first;
        int second = Launcher.memPick(20, HERE, skip);
        check(second == bit(E, false), "then the next most recent");
        skip |= 1 << second;
        check(Launcher.memPick(20, HERE, skip) == bit(A, false), "then the oldest");
        check(Launcher.memPick(20, HERE, skip | 1 << bit(A, false)) == -1, "every candidate skipped: none");
        reset();
        see(D, 12, 10, 18); see(E, 8, 10, 18);
        int lower = Math.min(slotOf(D), slotOf(E));
        check(Launcher.memPick(20, HERE, 0) == 2 * lower, "same-round tie: the lower slot");
        noRng("order");
    }

    static void extrapolation() throws Exception {
        reset();
        see(A, 10, 12, 17); see(A, 11, 12, 18);    // moving east, last seen (11,12) in round 18
        see(D, 8, 10, 18);
        int ra = bit(A, false), xa = bit(A, true), rd = bit(D, false);
        check(Launcher.memTile(xa).equals(new MapLocation(12, 12)), "extrapolated tile one step along the last direction");
        int order = Launcher.memPick(20, HERE, 0);
        check(order == Math.min(ra, rd), "a remembered tile before any extrapolated tile of its round");
        int skip = 1 << ra | 1 << rd;
        check(Launcher.memPick(20, HERE, skip) == xa, "extrapolated tile after every remembered tile of the round");
        see(E, 9, 9, 17);
        check(Launcher.memPick(20, HERE, skip) == xa, "a newer extrapolation before an older remembered tile");
        check(Launcher.memPick(20, HERE, skip | 1 << xa) == bit(E, false), "then the older sighting");
        reset();
        see(A, 10, 12, 19); see(A, 11, 12, 20);
        check(Launcher.memPick(20, HERE, 1 << bit(A, false)) == -1, "no extrapolation for a sighting this round (it has not moved)");
        check(Launcher.memPick(21, HERE, 1 << bit(A, false)) == bit(A, true), "extrapolated once a round old");
        reset();
        G.W = G.H = 14;
        see(A, 12, 10, 18); see(A, 13, 10, 19);    // moving east along the map edge x = 13
        check(Launcher.memPick(20, HERE, 1 << bit(A, false)) == -1, "off-map extrapolation never offered");
        reset();
        see(A, 13, 10, 18); see(A, 14, 10, 19);    // remembered at r2 16, extrapolated (15,10) at r2 25
        check(Launcher.memPick(20, HERE, 0) == bit(A, false) && Launcher.memPick(20, HERE, 1 << bit(A, false)) == -1,
            "extrapolated tile beyond r2 16 rejected");
        noRng("extrapolation");
    }

    static void forget() throws Exception {
        reset();
        see(A, 10, 12, 19); see(B, 10, 8, 19);
        Launcher.memForget(B);
        check(slotOf(B) == -1 && slotOf(A) >= 0 && Launcher.memPick(20, HERE, 0) == bit(A, false), "forget clears one slot only");
        Launcher.memForget(99999);
        check(slotOf(A) >= 0, "forgetting an unknown id is a no-op");
        see(CC, 1, 1, 19);
        check(slotOf(CC) == 2 * (A & mask()) + 1, "a forgotten way is reused first");
    }

    // ---- recording through track()
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
        noRng("track");
    }

    // ---- blindShot
    static void hook() throws Exception { Launcher.blindShot(); }
    static void memFire(MapLocation target, String message) {
        check(attacks.size() == 1 && attacks.get(0).equals(target) && Launcher.blindMemShots == 1 && Launcher.blindShots == 1
            && Launcher.shots == 1, message);
    }
    static void cloudBlock(int x0, int y0, int x1, int y1) {
        for (int x = x0; x <= x1; x++) for (int y = y0; y <= y1; y++) clouds.add(new MapLocation(x, y));
    }

    static void blindFromCloud() throws Exception {
        // launcher on a cloud: every tile beyond r2 4 is hidden; enemy last seen a round ago at r2 9 on a clear tile
        reset(); clouds.add(HERE); multiplier = 1.0; see(A, 13, 10, 19);
        hook(); memFire(new MapLocation(13, 10), "memory arm fires from a cloud source at a clear remembered tile");
        check(calls.stream().noneMatch(c -> c.startsWith("senseNearbyCloudLocations")), "no cloud discovery once the memory arm fires");
        check(cooldown == 10, "strict rule: the next own turn starts at cooldown zero");
        reset(); clouds.add(HERE); multiplier = 1.2; see(A, 13, 10, 19);
        hook();
        if (C.BLIND_MEM_DEBT >= 2) {
            memFire(new MapLocation(13, 10), "unboosted cloud source fires within the allowed debt");
            check(cooldown == 12, "debt of two: still ready next turn");
        } else {
            check(attacks.isEmpty() && Launcher.blindCooldownSkipped == 1, "unboosted cloud price (12) exceeds the strict rule");
        }
        reset(); clouds.add(HERE); multiplier = 1.0; see(A, 11, 11, 19);
        hook();
        check(attacks.isEmpty() && Launcher.blindNoTarget == 1, "remembered tile within r2 4 of a cloud source is sensable: no shot");
        noRng("blind from cloud");
    }

    static void blindClearSource() throws Exception {
        // enemy walked east then out of sight into a cloud bank: its last tile is clear and empty, the next is hidden
        reset(); cloudBlock(13, 8, 15, 12);
        see(A, 11, 10, 17); see(A, 12, 10, 18);
        hook(); memFire(new MapLocation(13, 10), "sensable remembered tile skipped; hidden extrapolated cloud tile fired");
        int rem = calls.indexOf("canSenseLocation:" + new MapLocation(12, 10)), ext = calls.indexOf("canSenseLocation:" + new MapLocation(13, 10));
        check(rem >= 0 && ext > rem, "remembered tile checked before the extrapolated tile");
        // remembered tile itself hidden (enemy seen on a cloud tile within r2 4 earlier, launcher since stepped back)
        reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 18);
        hook(); memFire(new MapLocation(14, 10), "hidden remembered cloud tile fired from a clear source");
        // cooldown rule on a clear tile (cost 10): cd + 10 <= 10 + C.BLIND_MEM_DEBT
        for (int cd = 1; cd <= 4; cd++) {
            reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 18); cooldown = cd;
            hook();
            if (cd <= C.BLIND_MEM_DEBT) memFire(new MapLocation(14, 10), "memory arm within its debt at cd " + cd);
            else check(attacks.isEmpty() && Launcher.blindCooldownSkipped == 1, "cd " + cd + " + cost 10 exceeds the rule");
        }
        if (C.BLIND_MEM_DEBT > 0) {
            reset(); cloudBlock(13, 8, 15, 12); cooldown = 1;
            hook(); check(attacks.isEmpty() && Launcher.blindCooldownSkipped == 1, "the cloud scan keeps the strict rule under debt");
        }
        noRng("blind clear source");
    }

    static void blindVisibleSkipped() throws Exception {
        // the remembered robot is in vision now (out of attack range): its old hidden tile is not a target
        reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 18);
        G.enemies = new RobotInfo[]{fighter(A, 12, 14)};   // clear tile at r2 20: in vision, out of attack range
        robots.put(G.enemies[0].location, G.enemies[0]);
        check(sensable(G.enemies[0].location) && !legal(G.enemies[0].location), "fixture: visible, not attackable");
        hook();
        check(Launcher.blindMemShots == 0, "robot in vision now is never shot from memory");
        check(attacks.size() == 1 && clouds.contains(attacks.get(0)) && !sensable(attacks.get(0)), "c_blind1's cloud scan follows");
        noRng("visible");
    }

    static void blindFallback() throws Exception {
        reset(); cloudBlock(13, 8, 15, 12);
        hook();
        check(Launcher.blindMemShots == 0 && Launcher.blindShots == 1 && attacks.size() == 1 && clouds.contains(attacks.get(0)),
            "no memory: c_blind1's rotating cloud scan unchanged");
        check(calls.contains("senseNearbyCloudLocations:16"), "cloud discovery bounded by r2 16");
        List<String> bare = new ArrayList<>(calls);
        reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 20 - AGE - 1);
        hook();
        check(Launcher.blindMemShots == 0 && Launcher.blindShots == 1, "expired sighting falls through to the cloud scan");
        check(calls.equals(bare), "no fresh sighting: exactly the calls of an empty memory (c_blind1's path)");
        // the same under a budget that drops below the scan guard after the entry: c_blind1 still discovers clouds first
        reset(); cloudBlock(13, 8, 15, 12); mapInfoBudget = C.BLIND_SCAN_LEFT - 1;
        hook();
        List<String> bareLow = new ArrayList<>(calls);
        check(attacks.isEmpty() && Launcher.blindBudgetSkipped == 1 && calls.contains("senseNearbyCloudLocations:16"), "fixture: c_blind1's low-budget path");
        reset(); cloudBlock(13, 8, 15, 12); mapInfoBudget = C.BLIND_SCAN_LEFT - 1; see(A, 14, 10, 20 - AGE - 1);
        hook();
        check(calls.equals(bareLow) && Launcher.blindBudgetSkipped == 1, "no fresh sighting: the memory arm is skipped, not entered");
        reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 19); Launcher.memForget(A);
        hook();
        check(Launcher.blindMemShots == 0 && Launcher.blindShots == 1 && calls.stream().noneMatch(c -> c.startsWith("canSenseRobot")),
            "a forgotten robot is never checked");
        reset(); clouds.add(HERE); multiplier = 1.0;
        hook();
        check(attacks.isEmpty() && Launcher.blindNoTarget == 1, "cloud source without memory: no cloud scan, no shot");
        check(calls.stream().noneMatch(c -> c.startsWith("senseNearbyCloudLocations")), "no futile discovery from a cloud source");
    }

    static void blindMostRecent() throws Exception {
        reset(); cloudBlock(6, 8, 7, 12); cloudBlock(13, 8, 14, 12);
        see(D, 6, 10, 17); see(A, 13, 9, 19); see(E, 13, 12, 18);
        hook(); memFire(new MapLocation(13, 9), "most recent hidden sighting fired");
        reset(); cloudBlock(6, 8, 7, 12);
        see(D, 6, 10, 17); see(A, 12, 10, 19);       // newest is on a clear tile in vision and absent: skipped
        hook(); memFire(new MapLocation(6, 10), "next most recent hidden sighting fired");
        noRng("most recent");
    }

    static void blindFutile() throws Exception {
        // every fresh slot holds a robot that left (or died) on clear ground: remembered and extrapolated tiles are all in
        // range and sensable; each tile is checked once (no re-scan per rejected candidate), then the cloud scan runs
        reset(); cloudBlock(6, 8, 7, 12);           // hidden clouds west, away from every remembered tile
        int fresh = 0;
        for (int i = 0; i < N; i++) {
            int id = 10000 + i;
            see(id, 9 + i % 3, 9 + i / 3 % 3, 18); see(id, 10 + i % 3, 9 + i / 3 % 3, 19);
            if (slotOf(id) >= 0) fresh++;
        }
        check(fresh == N, "fixture: every slot fresh");
        hook();
        long senses = calls.stream().filter(c -> c.startsWith("canSenseLocation")).count();
        long robotsChecked = calls.stream().filter(c -> c.startsWith("canSenseRobot")).count();
        check(Launcher.blindMemShots == 0 && Launcher.blindShots == 1 && clouds.contains(attacks.get(0)), "nothing hidden: the cloud scan fires");
        check(robotsChecked == N, "one vision check per fresh slot");
        check(senses <= 2 * N + 1 + 16, "at most one sensing check per candidate tile, then the cloud scan's");
        noRng("futile");
    }

    static void blindGuards() throws Exception {
        reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 18);
        budget(C.BLIND_ENTRY_LEFT - 1); hook();
        check(attacks.isEmpty() && calls.isEmpty() && Launcher.blindBudgetSkipped == 1, "entry guard: no RC calls");
        reset(); cloudBlock(13, 8, 15, 12); see(A, 12, 10, 19); see(D, 13, 9, 18);
        firstSenseBudget = C.BLIND_SCAN_LEFT - 1;   // budget drops after the first (sensable) candidate
        hook();
        check(attacks.isEmpty() && senseReads == 1 && Launcher.blindBudgetSkipped == 1, "scan guard stops the memory arm");
        check(calls.stream().noneMatch(c -> c.startsWith("senseNearbyCloudLocations")), "and the cloud scan after it");
        reset(); cloudBlock(13, 8, 15, 12); see(A, 12, 10, 19); see(D, 13, 9, 18);
        budget(C.BLIND_ENTRY_LEFT); firstSenseBudget = C.BLIND_SCAN_LEFT; hook();
        memFire(new MapLocation(13, 9), "exact entry and scan thresholds allowed");
        reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 18); nativeRound = 21;
        hook(); check(attacks.isEmpty() && Launcher.blindStale == 1, "stale entry round refuses");
        reset(); cloudBlock(13, 8, 15, 12); see(A, 14, 10, 18); advanceOnRead = 2;
        hook(); check(attacks.isEmpty() && Launcher.blindStale == 1, "round change before the attack refuses");
        noRng("guards");
    }

    static void blindStatsSuffix() throws Exception {
        reset(); Launcher.blindStats(); check(G.extra.equals(",pn=0,ua=0,rg=0,fo=0"), "never fired: no suffix");
        Launcher.blindShots = 7; Launcher.blindStats(); check(G.extra.equals(",bs=7,pn=0,ua=0,rg=0,fo=0"), "cloud scan only: bs alone");
        reset(); Launcher.blindShots = 7; Launcher.blindMemShots = 3; Launcher.blindStats();
        check(G.extra.equals(",bs=7,bm=3,pn=0,ua=0,rg=0,fo=0"), "memory share follows bs");
        reset(); Launcher.blindShots = 7; budget(C.BLIND_STATS_LEFT - 1); Launcher.blindStats();
        check(G.extra.equals(",pn=0,ua=0,rg=0,fo=0"), "low reserve: no string work");
    }

    // ---- shoot(): targeting unchanged, kills forgotten
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

    static void zeroDose() throws Exception {
        reset();
        G.enemies = new RobotInfo[]{fighter(A, 12, 12)};
        Launcher.track();
        check(Launcher.memId.length == 0 || slotOf(A) == -1, "compiled out: nothing remembered");
        reset(); clouds.add(new MapLocation(13, 10)); hook();
        check(Launcher.blindMemShots == 0, "compiled out: no memory shots");
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
