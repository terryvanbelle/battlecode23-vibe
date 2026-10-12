package c_mend3;

import battlecode.common.*;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/** Exercise the actual selector with an RC proxy and reflected engine Clock, as Bc3Test does.
 * Common safe-nearest cases are compared to the unchanged c_mend2 implementation, including its exact engine-call
 * trace. These tests measure decisions and guards; they do not claim measured in-game method bytecode costs. */
public class Mend3Test {
    static final int[] shared = new int[64];
    static final List<String> calls = new ArrayList<>();
    static final Map<Integer, Integer> budgetDrops = new HashMap<>();
    static int checks, reads, health, islands;
    static final MapLocation HERE = new MapLocation(10, 10);
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, arguments) -> {
            switch (method.getName()) {
                case "getHealth": calls.add("health"); return health;
                case "getIslandCount": calls.add("islands"); return islands;
                case "readSharedArray":
                    int slot = (Integer) arguments[0];
                    calls.add("read:" + slot);
                    reads++;
                    if (budgetDrops.containsKey(reads)) budget(budgetDrops.get(reads));
                    return shared[slot];
                default: throw new UnsupportedOperationException("unexpected engine call: " + method.getName());
            }
        });

    public static void main(String[] arguments) throws Exception {
        blockedNearest();
        noAlternative();
        ownership();
        tiesAndBounds();
        freshness();
        budgets();
        commonPathReference();
        check(C.MEND_HP == c_mend2.C.MEND_HP && C.MEND_FULL == c_mend2.C.MEND_FULL
            && C.MEND_R2 == c_mend2.C.MEND_R2 && C.MEND_RECHECK == c_mend2.C.MEND_RECHECK
            && C.MEND_MIN_LEFT == c_mend2.C.MEND_MIN_LEFT && C.MEND_SIGHT_R2 == c_mend2.C.MEND_SIGHT_R2,
            "original thresholds unchanged");
        System.out.println("mend3: " + checks + " cases ok");
    }

    static void reset(int count) throws Exception {
        Arrays.fill(shared, 0);
        Arrays.fill(MapMem.islandSeen, 0);
        Arrays.fill(MapMem.islandOwner, 0);
        Arrays.fill(MapMem.islandTile, null);
        calls.clear(); budgetDrops.clear(); reads = 0;
        health = C.MEND_HP; islands = count;
        G.rc = RC; G.W = 60; G.H = 60; G.here = HERE;
        G.enemies = new RobotInfo[0];
        G.round = Math.max(320, C.ANCHOR_START);
        Launcher.mending = false; Launcher.mendTile = null; Launcher.mendIsland = 0; Launcher.mendCheck = 0;
        budget(10000);
    }

    static void island(int id, int x, int y, int owner) {
        shared[Comms.ISLANDS + id] = (owner << 12) | G.enc(new MapLocation(x, y));
    }

    static void sighting(int offset, int x, int y, int age) {
        int stamp = (((G.round >> 4) & 15) - age) & 15;
        shared[Comms.ENEMY + offset] = (stamp << 12) | G.enc(new MapLocation(x, y));
    }

    static void twoIslands() throws Exception {
        reset(2); island(1, 11, 10, 1); island(2, 10, 18, 1); sighting(0, 12, 10, 0);
    }

    static void selected(int id, String message) {
        check(Launcher.mending && Launcher.mendIsland == id && Launcher.mendTile != null, message);
        check(Launcher.mendCheck == G.round + C.MEND_RECHECK, "recheck cadence unchanged");
    }

    static void none(String message) {
        check(!Launcher.mending && Launcher.mendIsland == 0 && Launcher.mendTile == null, message);
    }

    static void blockedNearest() throws Exception {
        twoIslands(); Launcher.mendUpdate(); selected(2, "blocked nearest selects safe second");
        check(reads == 2 * islands + 2 * Comms.NENEMY, "one cached sighting scan, two island scans");
        check(calls.stream().filter(x -> x.equals("islands")).count() == 1, "island count reused");
    }

    static void noAlternative() throws Exception {
        twoIslands(); sighting(1, 10, 18, 0); Launcher.mendUpdate(); none("all owned islands blocked");
        twoIslands(); island(2, 10, 18, 2); Launcher.mendUpdate(); none("enemy-owned alternative excluded");
        twoIslands(); island(2, 10, 18, 0); Launcher.mendUpdate(); none("neutral alternative excluded");
        twoIslands(); shared[Comms.ISLANDS + 2] = 0; Launcher.mendUpdate(); none("unknown alternative excluded");
    }

    static void ownership() throws Exception {
        twoIslands(); island(2, 10, 18, 2);
        MapMem.islandSeen[2] = G.round - 10; MapMem.islandOwner[2] = 1;
        MapMem.islandTile[2] = new MapLocation(10, 18);
        Launcher.mendUpdate(); selected(2, "fresh local owner overrides shared enemy owner at age ten");
        twoIslands(); island(2, 10, 18, 2);
        MapMem.islandSeen[2] = G.round - 11; MapMem.islandOwner[2] = 1;
        MapMem.islandTile[2] = new MapLocation(10, 18);
        Launcher.mendUpdate(); none("stale local owner yields to shared enemy owner");
        twoIslands(); shared[Comms.ISLANDS + 2] = 0;
        MapMem.islandSeen[2] = G.round - 50; MapMem.islandOwner[2] = 1;
        MapMem.islandTile[2] = new MapLocation(10, 18);
        Launcher.mendUpdate(); selected(2, "empty shared slot keeps located local ownership");
        twoIslands(); MapMem.islandSeen[2] = G.round; MapMem.islandOwner[2] = 2;
        MapMem.islandTile[2] = new MapLocation(10, 18);
        Launcher.mendUpdate(); none("fresh local loss overrides shared owned island");
        twoIslands(); shared[Comms.ISLANDS + 2] = 0;
        MapMem.islandSeen[2] = G.round; MapMem.islandOwner[2] = 1;
        Launcher.mendUpdate(); none("ownership without any known tile is insufficient");
    }

    static void tiesAndBounds() throws Exception {
        reset(3); island(1, 11, 10, 1); island(2, 10, 18, 1); island(3, 2, 10, 1);
        sighting(0, 12, 10, 0); Launcher.mendUpdate(); selected(2, "equal safe distance keeps first island id");
        twoIslands(); island(2, 22, 10, 1); Launcher.mendUpdate(); selected(2, "radius squared 144 included");
        twoIslands(); island(2, 22, 11, 1); Launcher.mendUpdate(); none("radius squared 145 excluded");
        twoIslands(); island(2, 12, 16, 1); Launcher.mendUpdate(); none("threat squared 36 excluded");
        twoIslands(); island(2, 13, 16, 1); Launcher.mendUpdate(); selected(2, "threat squared 37 allowed");
        reset(36); island(1, 11, 10, 1); island(36, 10, 18, 1); sighting(0, 12, 10, 0);
        Launcher.mendUpdate(); none("island ids beyond 35 never considered");
        check(!calls.contains("read:" + (Comms.ISLANDS + 36)), "no island-36 shared read");
    }

    static void freshness() throws Exception {
        twoIslands(); sighting(0, 12, 10, 1); Launcher.mendUpdate(); selected(2, "age-one threat blocks nearest");
        twoIslands(); sighting(0, 12, 10, 2); Launcher.mendUpdate(); selected(1, "age-two threat does not block");
        check(reads == islands + Comms.NENEMY, "stale sightings do not trigger extra reads");
        twoIslands(); G.round = (Math.max(512, C.ANCHOR_START) + 255) & ~255;
        Arrays.fill(shared, Comms.ENEMY, Comms.ENEMY + Comms.NENEMY, 0);
        sighting(0, 12, 10, 1); Launcher.mendUpdate(); selected(2, "fresh stamp wraps 15 to zero");
        twoIslands(); G.round = (Math.max(512, C.ANCHOR_START) + 255) & ~255;
        Arrays.fill(shared, Comms.ENEMY, Comms.ENEMY + Comms.NENEMY, 0);
        sighting(0, 12, 10, 2); Launcher.mendUpdate(); selected(1, "age-two wrapped stamp ignored");
    }

    static void budgets() throws Exception {
        twoIslands(); budgetDrops.put(islands + Comms.NENEMY, C.MEND_MIN_LEFT + 1499);
        Launcher.mendUpdate(); none("no second scan without its full entry reserve");
        check(reads == islands + Comms.NENEMY, "low fallback budget adds no shared reads");
        twoIslands(); budgetDrops.put(islands + Comms.NENEMY, C.MEND_MIN_LEFT + 1500);
        Launcher.mendUpdate(); selected(2, "fallback at exact entry reserve");
        twoIslands(); budgetDrops.put(islands + 2 * Comms.NENEMY, C.MEND_MIN_LEFT - 1);
        Launcher.mendUpdate(); none("fallback stops before spending original recheck tail reserve");
        check(reads == islands + 2 * Comms.NENEMY, "no below-guard fallback island reads");
        twoIslands(); budgetDrops.put(islands + 2 * Comms.NENEMY, C.MEND_MIN_LEFT);
        Launcher.mendUpdate(); selected(2, "fallback scans at exact tail reserve");
        twoIslands(); budgetDrops.put(islands + 2 * Comms.NENEMY + 1, C.MEND_MIN_LEFT - 1);
        Launcher.mendUpdate(); none("fallback stops after reserve falls during an island read");
        check(reads == islands + 2 * Comms.NENEMY + 1, "no later island read after reserve falls");
        twoIslands(); G.enemies = new RobotInfo[1]; // Only length is read; no enemy object or API call is required.
        Launcher.mendUpdate(); none("visible enemies bypass fallback even with full budget");
        check(reads == islands + Comms.NENEMY, "visible-enemy bypass adds no sighting or island reads");
        twoIslands(); budget(C.MEND_MIN_LEFT - 1);
        Launcher.mending = true; Launcher.mendTile = new MapLocation(8, 8); Launcher.mendIsland = 2;
        Launcher.mendUpdate(); selectedExisting(2, "original low-budget recheck keeps current target");
        check(reads == 0 && Launcher.mendCheck == 0, "deferred recheck makes no shared reads or cadence change");
    }

    static void selectedExisting(int id, String message) {
        check(Launcher.mending && Launcher.mendIsland == id && Launcher.mendTile != null, message);
    }

    static void commonPathReference() throws Exception {
        Random random = new Random(20261012);
        Method original = c_mend2.Launcher.class.getDeclaredMethod("mendUpdate"); original.setAccessible(true);
        for (int iteration = 0; iteration < 400; iteration++) {
            reset(1 + random.nextInt(35));
            for (int id = 1; id <= islands; id++) island(id, random.nextInt(25), random.nextInt(25), random.nextInt(3));
            sighting(0, 59, 59, iteration % 3); // All possible nearest islands are outside the guard radius.
            if (iteration % 7 == 0) health = C.MEND_HP + 1;
            if (iteration % 5 == 0) G.enemies = new RobotInfo[1];
            if (iteration % 11 == 0) budget(C.MEND_MIN_LEFT - 1);
            if (iteration % 13 == 0) G.round = C.ANCHOR_START - 1;
            int initialBudget = Clock.getBytecodesLeft();
            c_mend2.G.rc = RC; c_mend2.G.W = G.W; c_mend2.G.H = G.H;
            c_mend2.G.here = G.here; c_mend2.G.round = G.round;
            c_mend2.MapMem.islandSeen = MapMem.islandSeen.clone();
            c_mend2.MapMem.islandOwner = MapMem.islandOwner.clone();
            c_mend2.MapMem.islandTile = MapMem.islandTile.clone();
            set(c_mend2.Launcher.class, "mending", false); set(c_mend2.Launcher.class, "mendTile", null);
            set(c_mend2.Launcher.class, "mendIsland", 0); set(c_mend2.Launcher.class, "mendCheck", 0);
            original.invoke(null);
            List<String> expectedCalls = new ArrayList<>(calls);
            Object[] expected = state(c_mend2.Launcher.class);
            calls.clear(); reads = 0; budget(initialBudget);
            Launcher.mendUpdate();
            check(Arrays.equals(expected, state(Launcher.class)), "original safe-nearest state case " + iteration);
            check(expectedCalls.equals(calls), "original safe-nearest engine-call trace case " + iteration);
        }
        reset(2); island(1, 10, 18, 1); island(2, 2, 10, 1);
        Launcher.mendUpdate(); selected(1, "common-path equal-distance tie unchanged");
        check(reads == islands + Comms.NENEMY, "common path has exactly original shared reads");
    }

    static Object[] state(Class<?> type) throws Exception {
        return new Object[]{get(type, "mending"), get(type, "mendTile"), get(type, "mendIsland"), get(type, "mendCheck")};
    }

    static Object get(Class<?> type, String name) throws Exception {
        Field field = type.getDeclaredField(name); field.setAccessible(true); return field.get(null);
    }

    static void set(Class<?> type, String name, Object value) throws Exception {
        Field field = type.getDeclaredField(name); field.setAccessible(true); field.set(null, value);
    }

    static void budget(int value) {
        try {
            Field field = Class.forName("battlecode.instrumenter.inject.RobotMonitor").getDeclaredField("bytecodesLeft");
            field.setAccessible(true); field.setInt(null, value);
        } catch (ReflectiveOperationException error) { throw new RuntimeException(error); }
    }

    static void check(boolean passed, String message) {
        checks++;
        if (!passed) throw new AssertionError(message);
    }
}
