package c_blind1;

import battlecode.common.*;
import battlecode.world.Inventory;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.*;

/** Actual blind hook decisions and unchanged ordinary attacks, using a controlled RC and reflected Clock.
 * API bodies here are a decision fixture, not measured prices or a replacement for native engine checks. */
public class Blind1Test {
    static final MapLocation HERE = new MapLocation(6, 6), HIDDEN = new MapLocation(9, 6);
    static final List<String> calls = new ArrayList<>();
    static final List<MapLocation> attacks = new ArrayList<>();
    static final Map<MapLocation, RobotInfo> robots = new LinkedHashMap<>();
    static final Set<MapLocation> denied = new HashSet<>();
    static MapLocation[] clouds;
    static MapLocation nativeHere;
    static Team ownTeam;
    static double multiplierA, multiplierB;
    static int checks, cooldown, nativeRound, roundReads, advanceOnRead, discoveryBudget, firstSenseBudget, senseReads;
    static boolean sourceCloud;
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            String name = method.getName();
            String entry = name;
            if (args != null) for (Object arg : args) entry += ":" + (arg instanceof MapLocation ? encode((MapLocation) arg) : arg);
            calls.add(entry);
            switch (name) {
                case "getRoundNum":
                    if (++roundReads == advanceOnRead) nativeRound++;
                    return nativeRound;
                case "getActionCooldownTurns": return cooldown;
                case "getLocation": return nativeHere;
                case "senseMapInfo":
                    check(nativeHere.equals(args[0]), "multiplier queried on actual current tile");
                    return new MapInfo(nativeHere, sourceCloud, true, new double[]{multiplierA, multiplierB},
                        Direction.CENTER, new int[2][2], new int[2][2]);
                case "senseNearbyCloudLocations":
                    check((Integer) args[0] == 16, "cloud discovery bounded by launcher attack radius");
                    if (discoveryBudget >= 0) budget(discoveryBudget);
                    return clouds.clone();
                case "canSenseLocation":
                    boolean sensed = sensable((MapLocation) args[0]);
                    if (++senseReads == 1 && firstSenseBudget >= 0) budget(firstSenseBudget);
                    return sensed;
                case "canAttack": return legal((MapLocation) args[0]);
                case "isActionReady": return cooldown < 10;
                case "senseNearbyRobots":
                    Team team = args != null && args.length == 2 ? (Team) args[1] : null;
                    List<RobotInfo> seen = new ArrayList<>();
                    for (RobotInfo robot : robots.values()) if ((team == null || robot.team == team) && sensable(robot.location)) seen.add(robot);
                    return seen.toArray(new RobotInfo[0]);
                case "attack":
                    MapLocation target = (MapLocation) args[0];
                    check(legal(target), "never forces an illegal native attack");
                    attacks.add(target); cooldown += roundedCost();
                    RobotInfo victim = robots.get(target);
                    if (victim != null && victim.team != ownTeam && victim.type != RobotType.HEADQUARTERS) {
                        if (victim.health <= 20) robots.remove(target);
                        else robots.put(target, robot(victim.ID, victim.type, victim.health - 20, target, victim.team));
                    }
                    return null;
                default: throw new UnsupportedOperationException("unexpected hook/ordinary call: " + name);
            }
        });

    public static void main(String[] args) throws Exception {
        if (C.BLIND_PERIOD == 0) zeroDose();
        else {
            cooldownBoundaries(); sourceAndTargetVisibility(); nativeFreshness(); budgetGuards();
            deterministicCadence(); diagnosticSuffix(); commonOrdinaryReference();
        }
        System.out.println("blind1 period " + C.BLIND_PERIOD + ": " + checks + " checks ok");
    }

    static int encode(MapLocation loc) { return loc.x * 64 + loc.y + 1; }
    static int roundedCost() { return (int) Math.round(10 * (ownTeam == Team.A ? multiplierA : multiplierB)); }
    static boolean sensable(MapLocation target) {
        boolean cloud = Arrays.asList(clouds).contains(target);
        return nativeHere.distanceSquaredTo(target) <= (sourceCloud || cloud ? 4 : 20);
    }
    static boolean legal(MapLocation target) {
        return cooldown < 10 && target.x >= 0 && target.y >= 0 && target.x < 20 && target.y < 20
            && nativeHere.distanceSquaredTo(target) <= 16 && !denied.contains(target);
    }
    static RobotInfo robot(int id, RobotType type, int hp, MapLocation loc, Team team) {
        return new RobotInfo(id, team, type, new Inventory(), hp, loc);
    }
    static void reset() throws Exception {
        calls.clear(); attacks.clear(); robots.clear(); denied.clear();
        ownTeam = Team.A; multiplierA = multiplierB = 1; cooldown = 0; sourceCloud = false;
        clouds = new MapLocation[]{HIDDEN}; nativeHere = HERE; nativeRound = 1;
        roundReads = senseReads = 0; advanceOnRead = -1; discoveryBudget = firstSenseBudget = -1;
        G.rc = RC; G.id = 10003; G.round = 1; G.here = HERE; G.us = Team.A; G.them = Team.B;
        G.W = G.H = 20; G.enemies = G.nearby = new RobotInfo[0]; G.extra = ",pn=0,ua=0,rg=0,fo=0";
        Launcher.shots = Launcher.blindShots = Launcher.blindChecks = Launcher.blindEligible = 0;
        Launcher.blindBudgetSkipped = Launcher.blindCooldownSkipped = Launcher.blindNoTarget = Launcher.blindStale = 0;
        set(G.class, "rng", 987654321); budget(10000);
    }
    static void hook() throws Exception { if (C.BLIND_PERIOD > 0) Launcher.blindShot(); }
    static void fire(String message) { check(attacks.size() == 1 && Launcher.blindShots == 1 && Launcher.shots == 1, message); }
    static void none(String message) { check(attacks.isEmpty() && Launcher.blindShots == 0 && Launcher.shots == 0, message); }

    static void cooldownBoundaries() throws Exception {
        double[] multipliers = {.55, .65, .70, .75, .80, .85, .90, .95, 1, 1.10, 1.20};
        for (double multiplier : multipliers) for (int cd = 0; cd < 10; cd++) {
            reset(); multiplierA = multiplier; cooldown = cd; hook();
            boolean fits = cd + (int) Math.round(10 * multiplier) <= 10;
            check(attacks.size() == (fits ? 1 : 0), "strict rounded sum at m=" + multiplier + " cd=" + cd);
            if (fits) check(Math.max(0, cooldown - 10) == 0, "next own-start exactly zero after firing");
            check((Integer) get(G.class, "rng") == 987654321, "eligibility matrix consumes no combat RNG");
        }
        reset(); ownTeam = G.us = Team.B; G.them = Team.A; multiplierA = 1.2; multiplierB = .55; cooldown = 4;
        hook(); fire("team B reads its own minimum-cost multiplier"); check(cooldown == 10, "native team-specific sum reaches ten");
        reset(); multiplierA = .95; cooldown = 1; hook(); none("round-half-up 9.5 costs ten, rejecting eleven");
    }

    static void sourceAndTargetVisibility() throws Exception {
        reset(); sourceCloud = true; multiplierA = 1; hook(); none("boosted cloud source still excluded from discovery arm");
        check(!calls.contains("senseNearbyCloudLocations:16") && Launcher.blindNoTarget == 1, "no futile discovery from cloud source");
        reset(); sourceCloud = true; multiplierA = 1.2; hook(); none("unbuffed cloud price exceeds strict sum");
        check(Launcher.blindCooldownSkipped == 1, "unbuffed cloud rejected by debt policy");
        reset(); clouds = new MapLocation[]{new MapLocation(8, 6)}; hook(); none("cloud tile within r2 four is sensable");
        check(calls.stream().noneMatch(s -> s.startsWith("canAttack:")), "sensable tile does not proceed to attack check");
        reset(); clouds = new MapLocation[0]; hook(); none("empty discovered cloud list");
        reset(); denied.add(HIDDEN); hook(); none("hidden tile still requires native canAttack");
        reset(); clouds = new MapLocation[]{new MapLocation(7, 6), HIDDEN}; hook(); fire("skips visible first cloud for hidden legal second");
        check(attacks.get(0).equals(HIDDEN), "selected hidden cloud tile");
    }

    static void nativeFreshness() throws Exception {
        reset(); G.here = new MapLocation(1, 1); hook(); fire("uses native location after ordinary movement despite stale cache");
        check(G.here.equals(new MapLocation(1, 1)), "hook does not mutate ordinary sensing cache");
        reset(); nativeRound = 2; hook(); none("stale entry round refuses shot");
        check(calls.equals(Arrays.asList("getRoundNum")) && Launcher.blindStale == 1, "stale entry has no cooldown/map reads");
        reset(); advanceOnRead = 2; hook(); none("round changes after target checks refuse shot");
        check(Launcher.blindStale == 1, "second native round guard catches stale target window");
    }

    static void budgetGuards() throws Exception {
        reset(); budget(C.BLIND_ENTRY_LEFT - 1); hook(); none("entry below threshold");
        check(calls.isEmpty() && Launcher.blindBudgetSkipped == 1, "entry rejection has no RC calls");
        reset(); budget(C.BLIND_ENTRY_LEFT); hook(); fire("exact internal entry Clock threshold allowed");
        reset(); discoveryBudget = C.BLIND_SCAN_LEFT - 1; hook(); none("reserve lost during discovery prevents first scan");
        check(calls.stream().noneMatch(s -> s.startsWith("canSenseLocation:")), "no target read below scan reserve");
        reset(); discoveryBudget = C.BLIND_SCAN_LEFT; hook(); fire("exact internal scan Clock threshold allowed");
        reset(); clouds = new MapLocation[]{new MapLocation(7, 6), HIDDEN}; firstSenseBudget = C.BLIND_SCAN_LEFT - 1;
        hook(); none("reserve lost after first visible tile prevents later hidden shot");
        check(senseReads == 1 && Launcher.blindBudgetSkipped == 1, "scan stops without a later tile read");
    }

    static void deterministicCadence() throws Exception {
        int[] fireRounds = new int[3];
        for (int i = 0; i < 12; i++) {
            reset(); G.round = nativeRound = 1 + i * Math.max(1, C.BLIND_PERIOD);
            clouds = new MapLocation[]{HIDDEN, new MapLocation(6, 9), new MapLocation(3, 6)};
            hook(); fire("eligible scheduled round fires once");
            for (int slot = 0; slot < clouds.length; slot++) if (attacks.get(0).equals(clouds[slot])) fireRounds[slot]++;
            check((Integer) get(G.class, "rng") == 987654321, "rotation consumes no combat RNG");
        }
        check(Arrays.equals(fireRounds, new int[]{4, 4, 4}), "deterministic rotation covers each cloud without RNG");
        if (C.BLIND_PERIOD > 1) {
            reset(); G.round = nativeRound = 2; hook(); none("off-cadence round has no attack");
            check(calls.isEmpty() && Launcher.blindChecks == 0, "off cadence has no RC reads or eligibility counters");
        }
    }

    static void diagnosticSuffix() throws Exception {
        reset(); Launcher.blindStats(); check(G.extra.equals(",pn=0,ua=0,rg=0,fo=0"), "never-fired suffix omitted");
        Launcher.blindShots = 1999; budget(C.BLIND_STATS_LEFT - 1); Launcher.blindStats();
        check(G.extra.equals(",pn=0,ua=0,rg=0,fo=0") && Launcher.blindShots == 1999, "low reserve retains counter without string work");
        budget(C.BLIND_STATS_LEFT); Launcher.blindStats();
        check(G.extra.equals(",bs=1999,pn=0,ua=0,rg=0,fo=0"), "exact suffix threshold publishes late-game cumulative count before prior extras");
        check(calls.isEmpty(), "diagnostic suffix adds no RC calls");
    }

    static void commonOrdinaryReference() throws Exception {
        Method original = c_mend2.Launcher.class.getDeclaredMethod("shoot"); original.setAccessible(true);
        Random random = new Random(20261012L);
        RobotType[] types = {RobotType.CARRIER, RobotType.LAUNCHER, RobotType.DESTABILIZER,
            RobotType.AMPLIFIER, RobotType.BOOSTER, RobotType.HEADQUARTERS};
        for (int iteration = 0; iteration < 200; iteration++) {
            reset(); multiplierA = new double[]{.55, .9, 1, 1.2}[iteration % 4]; cooldown = iteration % 3;
            for (int n = 0; n < 6; n++) {
                MapLocation location = new MapLocation(4 + n % 3, 4 + n / 3);
                RobotType type = n == 0 ? RobotType.LAUNCHER : types[random.nextInt(types.length)];
                robots.put(location, robot(20000 + n, type, 20 * (1 + random.nextInt(10)), location, Team.B));
            }
            RobotInfo[] initial = robots.values().toArray(new RobotInfo[0]);
            int initialCooldown = cooldown;
            c_mend2.G.rc = RC; c_mend2.G.us = Team.A; c_mend2.G.them = Team.B;
            c_mend2.G.enemies = initial.clone(); c_mend2.G.here = HERE; c_mend2.G.round = 1;
            c_mend2.Launcher.shots = 0;
            original.invoke(null);
            List<String> expectedCalls = new ArrayList<>(calls);
            List<MapLocation> expectedAttacks = new ArrayList<>(attacks);
            int expectedCooldown = cooldown, expectedShots = c_mend2.Launcher.shots;
            calls.clear(); attacks.clear(); robots.clear(); for (RobotInfo robot : initial) robots.put(robot.location, robot);
            cooldown = initialCooldown; roundReads = senseReads = 0; G.enemies = initial.clone();
            Launcher.shoot();
            check(expectedCalls.equals(calls) && expectedAttacks.equals(attacks), "actual incumbent ordinary attack trace " + iteration);
            check(Launcher.shots == expectedShots && cooldown == expectedCooldown, "actual incumbent ordinary cooldown/count " + iteration);
            List<MapLocation> ordinaryAttacks = new ArrayList<>(attacks);
            hook();
            check(ordinaryAttacks.equals(attacks) && Launcher.blindShots == 0 && cooldown == expectedCooldown,
                "post-ordinary hook never adds debt or replaces any visible attack " + iteration);
            check((Integer) get(G.class, "rng") == 987654321, "common ordinary path preserves combat RNG " + iteration);
        }
    }

    static void zeroDose() throws Exception {
        for (int value : new int[]{1, 1999, 4000, 10000}) {
            reset(); budget(value); hook();
            check(calls.isEmpty() && attacks.isEmpty() && Launcher.blindChecks == 0 && cooldown == 0,
                "compiled dose zero hook omitted even on eligible state");
            check((Integer) get(G.class, "rng") == 987654321, "zero dose leaves combat RNG unchanged");
        }
    }
    static Object get(Class<?> cls, String name) throws Exception {
        Field field = cls.getDeclaredField(name); field.setAccessible(true); return field.get(null);
    }
    static void set(Class<?> cls, String name, Object value) throws Exception {
        Field field = cls.getDeclaredField(name); field.setAccessible(true); field.set(null, value);
    }
    static void budget(int value) throws Exception {
        Field field = Class.forName("battlecode.instrumenter.inject.RobotMonitor").getDeclaredField("bytecodesLeft");
        field.setAccessible(true); field.setInt(null, value);
    }
    static void check(boolean passed, String message) { checks++; if (!passed) throw new AssertionError(message); }
}
