package c_gh2;

import battlecode.common.*;
import battlecode.world.Inventory;
import java.lang.reflect.Field;
import java.lang.reflect.Proxy;
import java.util.*;

/** c_gh1 (c_di1 + C.GHOST, research/diagnosis/2026-10-18-launcher-micro-vs-strong.md 4 Plan 1). The shared fighter
 *  memory ported from c_blind2 (Blind2Test's memory cases: recording, in-place update, set replacement, memPick's age,
 *  visibility, range, order and extrapolation, memForget, track()'s recording, shoot()'s forgetting) with the age and
 *  scan guard as arguments. GHOST's invariants: an empty memory has no candidate; the age boundary counts at GHOST_AGE
 *  and not at GHOST_AGE+1; the r2 boundary counts at 26 and not beyond (exhaustive over offsets; 27 and 28 are no
 *  lattice distance, so 29 is the next); 0 <= ghostCount <= max and sensed slots never count, the count never rising as
 *  sensed bits are added (exhaustive over every cand and sensed mask and max 0..MEM_N); with 0 ghosts aheadLead is
 *  c_hr1's expression for every nAlly and nEnemy in 0..20; a slot killed through shoot() is forgotten (controlled RC).
 *  Through the RC: ghostAhead's guards (not ahead by vision, stale memory, GHOST_MIN_LEFT) make no RC call, a hidden
 *  fresh fighter within r2 26 flips a 2-lead and is capped at GHOST_MAX, a fighter in vision never counts, a memory
 *  holding no vanished fighter leaves vision's test (random states), no RNG draw; fight() steps in by vision and holds
 *  with the ghost when ready; when not ready or mending it makes no ghost check (no canSenseRobot, no flip, vision's
 *  ahead bit) and chooses the same tile either way. gf is published only after a flip, first; with none the indicator
 *  string is c_di1's. Exits non-zero on a failure. */
public class Gh2Test {
    static final int N = C.MEM_N, AGE = 6, SCAN_LEFT = 3500, GA = C.GHOST_AGE;   // AGE, SCAN_LEFT: c_blind2's values
    static final MapLocation HERE = new MapLocation(10, 10);
    static final List<String> calls = new ArrayList<>();
    static final List<MapLocation> attacks = new ArrayList<>();
    static final Map<MapLocation, RobotInfo> robots = new LinkedHashMap<>();
    static final Set<MapLocation> clouds = new LinkedHashSet<>();
    static MapLocation nativeHere;
    static int checks, fails, cooldown, nativeRound;
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            String name = method.getName();
            String entry = name;
            if (args != null) for (Object arg : args) entry += ":" + arg;
            calls.add(entry);
            switch (name) {
                case "getRoundNum": return nativeRound;
                case "getLocation": return nativeHere;
                case "isActionReady": return cooldown < 10;
                case "canSenseLocation": return sensable((MapLocation) args[0]);
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
                case "canMove": {
                    MapLocation t = nativeHere.add((Direction) args[0]);
                    return t.x >= 0 && t.y >= 0 && t.x < G.W && t.y < G.H && !robots.containsKey(t);
                }
                case "move": {
                    MapLocation t = nativeHere.add((Direction) args[0]);
                    check(!robots.containsKey(t) && t.x >= 0 && t.y >= 0 && t.x < G.W && t.y < G.H, "never forces an illegal move");
                    nativeHere = t;
                    return null;
                }
                case "attack": {
                    MapLocation target = (MapLocation) args[0];
                    check(legal(target), "never forces an illegal native attack");
                    attacks.add(target);
                    cooldown += 10;
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
        knobs();
        recordAndUpdate(); setReplacement(); pickAge(); pickVisibility(); pickRange(); pickOrder(); extrapolation();
        forget(); trackRecords(); shootForgetsKills(); blockedGuard();
        ghostEmpty(); ghostAge(); ghostRange(); ghostCandidatesRandom(); ghostCountExhaustive(); aheadLeadExhaustive();
        ghostSensedCalls(); ghostGuards(); ghostFlip(); ghostKilledByShoot(); ghostNoVanished(); fightReady(); fightNotReady();
        fightMending(); indicator();
        System.out.println(fails == 0 ? "Gh2Test PASS (" + checks + " checks)" : "Gh2Test FAIL " + fails + " of " + checks);
        if (fails > 0) System.exit(1);
    }

    // ---- fixture
    static int mask() { return N / 2 - 1; }
    /** Three ids in set 0 and one in each of sets 1 and 2, for any N >= 4. */
    static final int A = 10000, B = 10000 + N / 2, CC = 10000 + N, D = 10001, E = 10002;
    static int slotOf(int id) { for (int s = 0; s < N; s++) if (Launcher.memId[s] == id && Launcher.memRound[s] > Launcher.MEM_NONE) return s; return -1; }
    static RobotInfo robot(int id, RobotType type, int hp, MapLocation loc) {
        return new RobotInfo(id, Team.B, type, new Inventory(), hp, loc);
    }
    static RobotInfo fighter(int id, int x, int y) { return robot(id, RobotType.LAUNCHER, 200, new MapLocation(x, y)); }
    static void see(int id, int x, int y, int round) { Launcher.remember(fighter(id, x, y), round); }
    /** An enemy fighter standing at (x, y) now (the RC can sense it when in vision) and remembered at `round`. */
    static void place(int id, int x, int y, int round) { MapLocation l = new MapLocation(x, y); robots.put(l, fighter(id, x, y)); see(id, x, y, round); }
    static boolean sensable(MapLocation t) {
        if (t.x < 0 || t.y < 0 || t.x >= G.W || t.y >= G.H) return false;
        return nativeHere.distanceSquaredTo(t) <= (clouds.contains(nativeHere) || clouds.contains(t) ? 4 : 20);
    }
    static boolean legal(MapLocation t) {
        return cooldown < 10 && t.x >= 0 && t.y >= 0 && t.x < G.W && t.y < G.H && nativeHere.distanceSquaredTo(t) <= 16;
    }
    static void reset() throws Exception {
        calls.clear(); attacks.clear(); robots.clear(); clouds.clear();
        cooldown = 0; nativeHere = HERE; nativeRound = 20;
        G.rc = RC; G.id = 10003; G.round = 20; G.here = HERE; G.us = Team.A; G.them = Team.B;
        G.W = G.H = 30; G.enemies = G.nearby = new RobotInfo[0]; G.extra = ",pn=0,ua=0,rg=0,fo=0";
        G.nAllyFighters = G.nEnemyFighters = 0;
        HQState.ourHQs = null;
        Launcher.shots = 0; Launcher.ghostFlips = 0; Launcher.mending = false;
        Launcher.memReset(); Launcher.prevRound = -10; Launcher.nPrev = 0; Launcher.nPinned = 0; Launcher.firstTarget = 0;
        set(G.class, "rng", 987654321); budget(10000);
    }
    static void noRng(String message) throws Exception { check((Integer) get(G.class, "rng") == 987654321, message + ": no RNG draw"); }
    static int bit(int id, boolean ext) { return slotOf(id) * 2 + (ext ? 1 : 0); }
    static long count(String prefix) { return calls.stream().filter(c -> c.startsWith(prefix)).count(); }

    // ---- knobs
    static void knobs() {
        check(C.GHOST && Launcher.MEM, "arm on, memory compiled in");
        check(N >= 4 && N <= 16 && Integer.bitCount(N) == 1, "MEM_N a power of two, 4..16 for these cases");
        check(GA == 2 && C.GHOST_R2 == 26 && C.GHOST_MAX == 2 && C.GHOST_MIN_LEFT == 3500, "the plan's GHOST constants");
        check(C.GHOST_R2 == C.THREAT_R2, "ghost reach is fight()'s threat reach (one step plus attack)");
        check(C.GHOST_MIN_LEFT - 45 * N - 100 > C.FIGHT_GUARD, "a ghost check started at GHOST_MIN_LEFT leaves fight()'s scoring above FIGHT_GUARD");
        check(0 - Launcher.MEM_NONE > GA && 0 - Launcher.MEM_NONE > AGE, "MEM_NONE is never fresh, from round 0");
    }

    // ---- shared memory (Blind2Test's cases)
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
        check(Launcher.memPick(20 + AGE, HERE, 0, AGE) == b, "age `age` accepted");
        check(Launcher.memPick(21 + AGE, HERE, 0, AGE) == -1, "older than `age` rejected");
        check(Launcher.memPick(20 + GA, HERE, 0, GA) == b && Launcher.memPick(21 + GA, HERE, 0, GA) == -1, "the age argument is the bound");
        reset();
        check(Launcher.memPick(1, HERE, 0, AGE) == -1 && Launcher.memPick(3, HERE, 0, AGE) == -1, "empty slots never picked, even early");
        noRng("age");
    }

    static void pickVisibility() throws Exception {
        reset(); clouds.add(new MapLocation(10, 13)); clouds.add(new MapLocation(12, 12));
        see(A, 10, 13, 18); see(D, 12, 12, 19);
        int sa = slotOf(A), sd = slotOf(D);
        MapLocation dNow = new MapLocation(12, 14), car = new MapLocation(9, 9);
        robots.put(dNow, fighter(D, 12, 14)); robots.put(car, robot(55555, RobotType.CARRIER, 150, car));
        check(sensable(dNow), "fixture: D in vision now");
        int skip = Launcher.memBlocked(RC, 20, HERE, AGE, SCAN_LEFT);
        check(skip == 3 << (2 * sd), "robot in vision now masks both of its bits; a hidden remembered tile nothing");
        check(Launcher.memPick(20, HERE, 0, AGE) == bit(D, false), "without vision the newer sighting first");
        check(Launcher.memPick(20, HERE, skip, AGE) == 2 * sa, "robot in vision now is never a candidate");
        robots.remove(dNow);
        check(Launcher.memBlocked(RC, 20, HERE, AGE, SCAN_LEFT) == 0, "nothing in vision, every tile hidden: nothing masked");
        see(B, 11, 11, 19);
        robots.put(new MapLocation(13, 13), fighter(B, 13, 13));
        check(Launcher.memBlocked(RC, 20, HERE, AGE, SCAN_LEFT) == 3 << (2 * slotOf(B)), "way-1 id masked");
        reset(); clouds.add(new MapLocation(12, 11));
        see(A, 10, 11, 18); see(A, 11, 11, 19);      // remembered (11,11) clear and sensable; extrapolated (12,11) hidden
        check(Launcher.memBlocked(RC, 20, HERE, AGE, SCAN_LEFT) == 1 << bit(A, false), "sensable remembered tile masked, hidden extrapolation kept");
        reset(); clouds.add(new MapLocation(14, 10));
        see(A, 14, 10, 19); cooldown = 10;           // hidden but the attack is illegal (cooldown)
        check(Launcher.memBlocked(RC, 20, HERE, AGE, SCAN_LEFT) == 1 << bit(A, false), "an illegal attack is masked");
        reset();
        see(A, 18, 18, 19); see(D, 10, 13, 20 - AGE - 1);   // beyond r2 16; older than `age`
        calls.clear();
        check(Launcher.memBlocked(RC, 20, HERE, AGE, SCAN_LEFT) == 0 && calls.isEmpty(), "out-of-range and expired slots cost no RC call");
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
        check(Launcher.nPinned == 1 && Launcher.nPrev == 1, "track's own pinned match unchanged");
        reset();
        G.enemies = new RobotInfo[]{fighter(A, 12, 12)};
        budget(C.TRACK_MIN_LEFT - 1);
        Launcher.track();
        check(slotOf(A) == -1, "below track's guard nothing is recorded");
        reset();
        RobotInfo[] many = new RobotInfo[C.TRACK_MAX + 3];
        for (int i = 0; i < many.length; i++) many[i] = fighter(30000 + i, 5 + i % 10, 5 + i / 10);
        G.enemies = many;
        Launcher.track();
        int rec = 0;
        for (int i = 0; i < many.length; i++) for (int k = 0; k < N; k++) if (Launcher.memId[k] == 30000 + i && Launcher.memRound[k] == 20) rec++;
        check(rec <= Math.min(N, C.TRACK_MAX) && slotOf(30000 + C.TRACK_MAX) == -1, "only track's first TRACK_MAX fighters are recorded");
        reset();
        Launcher.track();
        for (int k = 0; k < N; k++) check(Launcher.memRound[k] == Launcher.MEM_NONE, "no enemy in vision records nothing");
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

    static void blockedGuard() throws Exception {
        reset(); clouds.add(new MapLocation(13, 10));
        see(A, 13, 10, 19);
        budget(SCAN_LEFT - 1);
        check(Launcher.memBlocked(RC, 20, HERE, AGE, SCAN_LEFT) == 0 && calls.isEmpty(), "memBlocked: no RC call under minLeft");
        budget(SCAN_LEFT);
        check(Launcher.memBlocked(RC, 20, HERE, AGE, SCAN_LEFT) == 0 && count("canSenseRobot") == 1, "memBlocked: checks at exactly minLeft");
    }

    // ---- GHOST: pure parts
    static void ghostEmpty() throws Exception {
        reset();
        for (int now : new int[]{0, 1, 2, 3, 20, 999, 1000, 1001, 2000})
            for (int x = 0; x < 30; x += 7) for (int y = 0; y < 30; y += 7)
                check(Launcher.ghostCandidates(now, new MapLocation(x, y)) == 0, "1. an empty memory gives no candidate");
        see(A, 11, 10, 19); Launcher.memForget(A);
        check(Launcher.ghostCandidates(20, HERE) == 0, "1. a forgotten slot is no candidate");
        check(calls.isEmpty(), "ghostCandidates makes no RC call");
        noRng("empty");
    }

    static void ghostAge() throws Exception {
        reset();
        see(A, 12, 12, 20);
        int b = 1 << slotOf(A);
        for (int now = 20; now <= 20 + GA; now++) check(Launcher.ghostCandidates(now, HERE) == b, "2. counts at age 0..GHOST_AGE");
        check(Launcher.ghostCandidates(21 + GA, HERE) == 0, "2. not at GHOST_AGE + 1");
        check(Launcher.ghostCandidates(30 + GA, HERE) == 0, "2. nor later");
        see(D, 11, 11, 20 - GA); see(E, 9, 9, 19 - GA);
        check(Launcher.ghostCandidates(20, HERE) == (b | 1 << slotOf(D)), "2. a mix: the age-GHOST_AGE slot in, the older one out");
    }

    static void ghostRange() throws Exception {
        for (int dx = -7; dx <= 7; dx++) for (int dy = -7; dy <= 7; dy++) {
            reset();
            see(A, 10 + dx, 10 + dy, 19);
            boolean in = dx * dx + dy * dy <= 26;
            check((Launcher.ghostCandidates(20, HERE) != 0) == in, "3. counted iff d2 <= 26");
        }
        reset();
        see(A, 15, 11, 19);          // d2 26
        check(Launcher.ghostCandidates(20, HERE) != 0, "3. d2 26 counts");
        reset();
        see(A, 15, 12, 19);          // d2 29: 27 and 28 are no sum of two squares
        check(Launcher.ghostCandidates(20, HERE) == 0, "3. beyond 26 (next lattice d2 29) does not");
        check(Launcher.ghostCandidates(20, new MapLocation(11, 11)) != 0, "3. range from the launcher's position now");
    }

    static void ghostCandidatesRandom() throws Exception {
        Random r = new Random(20261018);
        for (int t = 0; t < 3000; t++) {
            reset();
            int now = 20 + r.nextInt(10);
            for (int k = 0; k < 2 * N; k++) see(10000 + r.nextInt(64), r.nextInt(30), r.nextInt(30), now - r.nextInt(GA + 3));
            if (r.nextInt(4) == 0) Launcher.memForget(Launcher.memId[r.nextInt(N)]);
            MapLocation h = new MapLocation(r.nextInt(30), r.nextInt(30));
            int ref = 0;
            for (int s = 0; s < N; s++)
                if (Launcher.memRound[s] > Launcher.MEM_NONE && now - Launcher.memRound[s] <= GA && h.distanceSquaredTo(Launcher.memLoc[s]) <= C.GHOST_R2) ref |= 1 << s;
            check(Launcher.ghostCandidates(now, h) == ref, "candidate mask = fresh slots within r2 26 (random memories)");
        }
    }

    static void ghostCountExhaustive() {
        int full = (1 << N) - 1;
        for (int max = 0; max <= N; max++) for (int cand = 0; cand <= full; cand++) for (int sensed = 0; sensed <= full; sensed++) {
            int g = Launcher.ghostCount(cand, sensed, max);
            check(g >= 0 && g <= max, "4. 0 <= ghostCount <= max");
            check(g == Math.min(max, Integer.bitCount(cand & ~sensed)), "ghostCount = min(max, unsensed candidates)");
            check(Launcher.ghostCount(cand, sensed | cand, max) == 0, "5. sensed slots never count");
            for (int b = 0; b < N; b++) {
                int g2 = Launcher.ghostCount(cand, sensed | 1 << b, max);
                check(g2 <= g, "5. the count never rises as a sensed bit is added");
                if ((cand >>> b & 1) == 0) check(g2 == g, "a sensed bit outside cand changes nothing");
            }
        }
    }

    static void aheadLeadExhaustive() {
        for (int a = 0; a <= 20; a++) for (int e = 0; e <= 20; e++) {
            boolean hr1 = a + 1 - e >= 2;   // c_hr1 / c_di1: G.nAllyFighters + 1 - G.nEnemyFighters >= 2
            check(Launcher.aheadLead(a, e, 0) == hr1, "6. aheadLead with 0 ghosts is c_hr1's expression");
            for (int g = 0; g <= C.GHOST_MAX; g++) {
                check(!Launcher.aheadLead(a, e, g + 1) || Launcher.aheadLead(a, e, g), "a ghost never turns 'not ahead' into 'ahead'");
                check(!Launcher.aheadLead(a, e, g) || hr1, "ahead with ghosts implies ahead by vision");
            }
        }
    }

    // ---- GHOST through the RC
    static void ghostSensedCalls() throws Exception {
        reset(); clouds.add(new MapLocation(13, 12));
        place(A, 12, 12, 19);                  // in vision now (clear tile, d2 8)
        place(D, 13, 12, 19);                  // hidden on a cloud (d2 13)
        see(E, 16, 10, 19);                    // gone, d2 36: no candidate
        int cand = Launcher.ghostCandidates(20, HERE);
        check(cand == (1 << slotOf(A) | 1 << slotOf(D)), "fixture: two candidates");
        calls.clear();
        int sensed = Launcher.ghostSensed(RC, cand);
        check(sensed == 1 << slotOf(A), "ghostSensed: only the robot in vision");
        check(count("canSenseRobot") == 2 && calls.size() == 2, "one canSenseRobot per candidate, nothing else");
        check(Launcher.ghostCount(cand, sensed, C.GHOST_MAX) == 1, "one ghost");
        calls.clear();
        check(Launcher.ghostSensed(RC, 0) == 0 && calls.isEmpty(), "no candidate: no RC call");
        noRng("sensed");
    }

    static void ghostGuards() throws Exception {
        // vision not ahead (lead 1): false, and the memory is never read
        reset(); clouds.add(new MapLocation(12, 12)); see(A, 12, 12, 19);
        G.nAllyFighters = 0; G.nEnemyFighters = 0;
        check(!Launcher.ghostAhead(RC, HERE) && calls.isEmpty() && Launcher.ghostFlips == 0, "not ahead by vision: false, no RC call");
        G.nAllyFighters = 3; G.nEnemyFighters = 3;
        check(!Launcher.ghostAhead(RC, HERE) && calls.isEmpty() && Launcher.ghostFlips == 0, "par by vision: false, no RC call");
        // stale memory
        reset(); clouds.add(new MapLocation(12, 12)); see(A, 12, 12, 19 - GA);
        G.nAllyFighters = 1;
        check(Launcher.ghostAhead(RC, HERE) && calls.isEmpty() && Launcher.ghostFlips == 0, "no sighting within GHOST_AGE: vision's test, no RC call");
        // empty memory
        reset(); G.nAllyFighters = 1;
        check(Launcher.ghostAhead(RC, HERE) && calls.isEmpty(), "empty memory: vision's test, no RC call");
        // budget guard
        reset(); clouds.add(new MapLocation(12, 12)); see(A, 12, 12, 19);
        G.nAllyFighters = 1; budget(C.GHOST_MIN_LEFT - 1);
        check(Launcher.ghostAhead(RC, HERE) && calls.isEmpty() && Launcher.ghostFlips == 0, "under GHOST_MIN_LEFT: vision's test, no RC call");
        budget(C.GHOST_MIN_LEFT);
        check(!Launcher.ghostAhead(RC, HERE) && Launcher.ghostFlips == 1, "at exactly GHOST_MIN_LEFT the memory is used");
        // fresh memory, nothing in r2 26
        reset(); see(A, 20, 20, 19); G.nAllyFighters = 1;
        check(Launcher.ghostAhead(RC, HERE) && calls.isEmpty(), "no candidate within r2 26: no RC call");
        noRng("guards");
    }

    static void ghostFlip() throws Exception {
        // lead 2 (one ally in vision, no enemy fighter) and one fighter seen last round on a cloud within r2 26
        reset(); clouds.add(new MapLocation(12, 13)); place(A, 12, 13, 19);
        G.nAllyFighters = 1;
        check(!Launcher.ghostAhead(RC, HERE) && Launcher.ghostFlips == 1, "a hidden fresh fighter flips a 2-lead");
        check(count("canSenseRobot") == 1 && calls.size() == 1, "one canSenseRobot, nothing else");
        // the same fighter in vision now: no ghost
        reset(); place(A, 12, 13, 19);
        G.nAllyFighters = 1;
        check(Launcher.ghostAhead(RC, HERE) && Launcher.ghostFlips == 0, "a remembered fighter in vision never counts");
        // seen exactly GHOST_AGE ago: counts; GHOST_AGE+1 with a fresher sensed sighting keeping memLast fresh: does not
        reset(); clouds.add(new MapLocation(12, 13)); place(A, 12, 13, 20 - GA);
        G.nAllyFighters = 1;
        check(!Launcher.ghostAhead(RC, HERE), "a ghost seen GHOST_AGE rounds ago counts");
        reset(); clouds.add(new MapLocation(12, 13)); place(A, 12, 13, 19 - GA); place(D, 11, 11, 20);
        G.nAllyFighters = 1;
        check(Launcher.ghostAhead(RC, HERE) && Launcher.ghostFlips == 0, "a ghost seen GHOST_AGE + 1 rounds ago does not");
        // beyond r2 26 (d2 29), hidden
        reset(); clouds.add(new MapLocation(15, 12)); see(A, 15, 12, 19);
        G.nAllyFighters = 1;
        check(Launcher.ghostAhead(RC, HERE) && calls.isEmpty(), "a hidden fighter at d2 29 does not count");
        // lead 3 with 1 ghost: still ahead; with 2: flip; lead 4 with 3 ghosts: capped at GHOST_MAX 2, still ahead
        int[][] cases = {{2, 1, 1}, {2, 2, 0}, {3, 2, 1}, {3, 3, 1}, {3, 8, 1}, {1, 1, 0}, {2, 0, 1}};   // allies, ghosts, ahead
        for (int[] c : cases) {
            reset();
            for (int k = 0; k < c[1]; k++) { MapLocation l = new MapLocation(8 + k, 13); clouds.add(l); see(10000 + k, l.x, l.y, 19); }
            int ghosts = Integer.bitCount(Launcher.ghostCandidates(20, HERE));
            G.nAllyFighters = c[0];
            boolean ahead = Launcher.ghostAhead(RC, HERE);
            check(ahead == (c[2] == 1), "lead " + (c[0] + 1) + " with " + ghosts + " ghosts");
            check(ahead == Launcher.aheadLead(c[0], 0, Math.min(C.GHOST_MAX, ghosts)), "ghostAhead = aheadLead with the capped ghosts");
            check(Launcher.ghostFlips == (ahead ? 0 : 1), "a flip is counted exactly when vision's ahead is lost");
        }
        noRng("flip");
    }

    static void ghostKilledByShoot() throws Exception {
        // 7. enemy launcher at 20 HP in range, seen this turn (track), killed by shoot(): forgotten, never a ghost
        reset();
        MapLocation at = new MapLocation(12, 11);
        robots.put(at, robot(A, RobotType.LAUNCHER, 20, at));
        G.enemies = robots.values().toArray(new RobotInfo[0]);
        G.nAllyFighters = 2; G.nEnemyFighters = 1;      // lead 2 by vision at the start of the turn
        Launcher.track();
        check(slotOf(A) >= 0, "fixture: remembered by track");
        Launcher.shoot();
        check(attacks.size() == 1 && !robots.containsKey(at), "fixture: killed by shoot");
        check(slotOf(A) == -1, "7. a slot killed through shoot() is forgotten");
        calls.clear();
        check(Launcher.ghostAhead(RC, HERE) && Launcher.ghostFlips == 0 && calls.isEmpty(), "7. the dead fighter is no ghost (no candidate, no RC call)");
        // a survivor (40 HP) stays remembered and in vision: still no ghost
        reset();
        robots.put(at, robot(A, RobotType.LAUNCHER, 40, at));
        G.enemies = robots.values().toArray(new RobotInfo[0]);
        G.nAllyFighters = 2; G.nEnemyFighters = 1;
        Launcher.track(); Launcher.shoot();
        check(slotOf(A) >= 0 && Launcher.ghostAhead(RC, HERE) && Launcher.ghostFlips == 0, "a survivor in vision is kept and never a ghost");
        noRng("killed");
    }

    static void ghostNoVanished() throws Exception {
        // random memories with no vanished fighter within reach: every fresh sighting within r2 26 stands in vision now;
        // the rest are fresh but beyond r2 26, or older than GHOST_AGE (hidden on clouds near us): vision's test for
        // every count, no flip
        Random r = new Random(7);
        List<MapLocation> near = new ArrayList<>();
        for (int x = 0; x < 30; x++) for (int y = 0; y < 30; y++) {
            MapLocation l = new MapLocation(x, y);
            if (!l.equals(HERE) && HERE.distanceSquaredTo(l) <= 20) near.add(l);
        }
        for (int t = 0; t < 200; t++) {
            reset();
            List<Integer> ids = new ArrayList<>();
            for (int i = 0; i < 40; i++) ids.add(10000 + i);
            Collections.shuffle(ids, r);
            Collections.shuffle(near, r);
            int k = r.nextInt(N + 3), q = 0;
            for (int i = 0; i < k; i++) {
                int id = ids.get(q++);
                switch (r.nextInt(3)) {
                    case 0: { MapLocation l = near.get(i); place(id, l.x, l.y, 20 - r.nextInt(GA + 1)); break; }   // in vision now
                    case 1: { see(id, 10 + 6 + r.nextInt(4), 10 + r.nextInt(8), 20 - r.nextInt(GA + 1)); break; }   // fresh, d2 >= 36
                    default: { MapLocation l = near.get(i); clouds.add(l); see(id, l.x, l.y, 19 - GA - r.nextInt(5)); }   // hidden, stale
                }
            }
            MapLocation last = near.get(k);
            place(ids.get(q), last.x, last.y, 20);   // this turn's sighting, in vision: memLast fresh
            for (int a = 0; a <= 20; a++) for (int e = 0; e <= 20; e++) {
                G.nAllyFighters = a; G.nEnemyFighters = e;
                check(Launcher.ghostAhead(RC, HERE) == (a + 1 - e >= 2), "no vanished fighter: c_di1's 'ahead'");
            }
            check(Launcher.ghostFlips == 0, "no vanished fighter: no flip");
        }
        noRng("no vanished");
    }

    // ---- fight(): the decision
    /** Two enemy launchers at (14,12) and (12,14) (d2 20 from HERE: in vision, out of range); every tile that can hit
     *  one is within r2 26 of both (threat 2), and (9,9) is out of both reaches. Three allies in vision (lead 2 by
     *  vision); ghost: a fighter seen last round at (13,13) on a cloud (hidden, d2 18). */
    static Direction fightOnce(boolean ghost, boolean ready) throws Exception { return fightOnce(ghost, ready, false); }
    /** As above; mend: mending toward (5,5). */
    static Direction fightOnce(boolean ghost, boolean ready, boolean mend) throws Exception {
        reset();
        cooldown = ready ? 0 : 10;
        if (mend) { Launcher.mending = true; Launcher.mendTile = new MapLocation(5, 5); }
        MapLocation e1 = new MapLocation(14, 12), e2 = new MapLocation(12, 14);
        robots.put(e1, fighter(D, 14, 12)); robots.put(e2, fighter(E, 12, 14));
        see(D, 14, 12, 20); see(E, 12, 14, 20);       // this turn's sightings (track)
        if (ghost) { MapLocation g = new MapLocation(13, 13); clouds.add(g); place(A, 13, 13, 19); }
        G.enemies = new RobotInfo[]{robots.get(e1), robots.get(e2)};
        G.nAllyFighters = 3; G.nEnemyFighters = 2;
        Launcher.fight();
        return HERE.directionTo(nativeHere);
    }
    static boolean canHitFrom(MapLocation t) {
        return t.distanceSquaredTo(new MapLocation(14, 12)) <= 16 || t.distanceSquaredTo(new MapLocation(12, 14)) <= 16;
    }

    static void fightReady() throws Exception {
        Direction plain = fightOnce(false, true);
        boolean aheadBit = (Launcher.fightA >> 10 & 1) == 1;
        check(plain != Direction.CENTER && canHitFrom(HERE.add(plain)), "vision ahead: steps in to a hitting tile");
        check(aheadBit && Launcher.ghostFlips == 0, "vision ahead: FIGHT's ahead bit set, no flip");
        Direction held = fightOnce(true, true);
        check(!canHitFrom(HERE.add(held)) && held == Direction.SOUTHWEST, "with the ghost: the parity hold, back out of both reaches to (9,9)");
        check((Launcher.fightA >> 10 & 1) == 0 && Launcher.ghostFlips == 1, "with the ghost: FIGHT's ahead bit clear, one flip");
        check(count("canSenseRobot") == 3, "fight(): one canSenseRobot per fresh candidate (two in vision, one ghost)");
    }

    static void fightNotReady() throws Exception {
        Direction plain = fightOnce(false, false);
        int rngPlain = (Integer) get(G.class, "rng");
        Direction ghost = fightOnce(true, false);
        int rngGhost = (Integer) get(G.class, "rng");
        check(plain == ghost && rngPlain == rngGhost, "action not ready: the same tile and RNG either way (identical scoring)");
        check(Launcher.ghostFlips == 0 && count("canSenseRobot") == 0, "action not ready: no ghost check, no flip counted");
        check((Launcher.fightA >> 10 & 1) == 1, "action not ready: FIGHT's ahead bit is vision's");
    }

    static void fightMending() throws Exception {
        Direction plain = fightOnce(false, true, true);
        int rngPlain = (Integer) get(G.class, "rng");
        Direction ghost = fightOnce(true, true, true);
        int rngGhost = (Integer) get(G.class, "rng");
        check(plain == ghost && rngPlain == rngGhost, "mending: the same tile and RNG either way (mendScore ignores 'ahead')");
        check(Launcher.ghostFlips == 0 && count("canSenseRobot") == 0, "mending: no ghost check, no flip counted");
        check((Launcher.fightA >> 10 & 1) == 1, "mending: FIGHT's ahead bit is vision's");
    }

    // ---- telemetry
    static void indicator() throws Exception {
        // no flip: G.extra untouched, c_di1's string with every field (the review's case: 61 characters, fo kept)
        reset();
        String di1 = ",pn=3,ua=0,rg=10,fo=12";
        G.extra = di1; Launcher.ghostFlips = 0;
        Launcher.ghostStats();
        check(G.extra.equals(di1), "no flip: G.extra is c_di1's");
        String s0 = Telemetry.indicatorString('F', 1, "3", 0, 0, 0, 1, 87, 2, 0, G.extra);
        check(s0.equals(Telemetry.indicatorString('F', 1, "3", 0, 0, 0, 1, 87, 2, 0, di1)) && s0.endsWith(",rg=10,fo=12"),
            "no flip: the indicator string is c_di1's, fo kept");
        G.extra = ",pn=12,ua=0,rg=25,fo=31";
        Launcher.ghostStats();
        check(Telemetry.indicatorString('F', 1, "3", 0, 0, 0, 1, 150, 12, 0, G.extra).endsWith(",fo=31"), "no flip: a long string keeps fo");
        // a flip: published first
        G.extra = di1; Launcher.ghostFlips = 3;
        Launcher.ghostStats();
        check(G.extra.equals(",gf=3" + di1), "a flip: gf first, then c_di1's fields");
        String base = ",pn=123,ua=0,rg=45,fo=67";
        String first = Telemetry.indicatorString('F', 1, "0", 0, 0, 0, 1, 150, 23, 4, ",gf=9" + base);
        String last = Telemetry.indicatorString('F', 1, "0", 0, 0, 0, 1, 150, 23, 4, base + ",gf=9");
        check(first.contains(",gf=9") && first.length() <= 64, "gf first survives the 64-character cut");
        check(!last.contains(",gf=9"), "fixture: appended last it would be cut (why it goes first)");
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
    static void check(boolean passed, String message) {
        checks++;
        if (!passed) { if (fails++ < 30) System.out.println("FAIL: " + message); }
    }
}
