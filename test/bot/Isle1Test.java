package c_isle1;

import battlecode.common.*;
import java.lang.reflect.Field;
import java.lang.reflect.Proxy;

/** c_isle1 (c_hr1 + C.ISLE_THREAT). Pure parts: conquestNeed is ceil(0.75 n) (the engine's float test); conquestThreat
 *  is false with no island theirs, monotone in them, with the plan's thresholds; isleFirst diverts even ids only;
 *  theirsFor is pickObjective's rule plus our own fresh-enough "theirs" over a neutral slot, never over "ours", and
 *  islandScan's early skip is exact; MapMem.mayWrite equals c_hr1's flush rule for owners 0 and 1 (age 0..70 x slot
 *  empty/0/1/2), adds only "theirs" over a neutral slot, never overwrites "ours", and flushIslands' age shortcut is
 *  exact. Through a controlled RC: flushIslands' writes; pickObjective diverts an even id under a threat (no shared
 *  write, no RNG draw), not an odd id, a mender or an even id below the threshold; the scan runs once per
 *  C.ISLE_RECHECK rounds, waits for C.ISLE_MIN_LEFT, keeps the last result when the loop guard cuts it, and a target
 *  our own record of the last 10 rounds says is not theirs is dropped (also seen on a turn without march; an older
 *  record yields to the slot). API bodies here are a decision fixture, not engine prices. Exits non-zero on a
 *  failure. */
public class Isle1Test {
    static int checks, fails;
    static final int[] shared = new int[64];
    static int islandReads, writes, nIslands = 4, readCost;
    static int rngSeed = 987654321;
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            switch (method.getName()) {
                case "readSharedArray": {
                    int i = (Integer) args[0];
                    if (i > Comms.ISLANDS && i <= Comms.ISLANDS + 35) { islandReads++; if (readCost > 0) budget(left() - readCost); }
                    return shared[i];
                }
                case "canWriteSharedArray": return true;
                case "writeSharedArray": writes++; shared[(Integer) args[0]] = (Integer) args[1]; return null;
                case "getIslandCount": return nIslands;
                case "getRoundNum": return G.round;
                case "getLocation": return G.here;
                default: throw new AssertionError("unexpected RC call " + method.getName());
            }
        });

    public static void main(String[] a) throws Exception {
        check(C.ISLE_THREAT && C.ISLE_STICKY, "arm and sub-switch on");
        check(C.ISLE_STICKY_AGE <= 60, "ISLE_STICKY_AGE within flushIslands' 60 (its age shortcut stays exact)");
        check(C.ISLE_RECHECK == 5 && C.ISLE_MEM == 150, "plan's recheck and memory");
        check(C.ISLE_MIN_LEFT - 35 * 45 > C.ISLAND_LOOP_GUARD, "a scan started at ISLE_MIN_LEFT is never cut (35 ids at 45)");
        pure();
        mayWrite();
        flush();
        pick();
        System.out.println(fails == 0 ? "Isle1Test PASS (" + checks + " checks)" : "Isle1Test FAIL " + fails + " of " + checks);
        if (fails > 0) System.exit(1);
    }

    // ---------------------------------------------------------------- pure functions
    static void pure() {
        int[][] need = {{4, 3}, {6, 5}, {7, 6}, {8, 6}, {9, 7}, {12, 9}, {35, 27}};
        for (int[] p : need) check(Launcher.conquestNeed(p[0]) == p[1], "conquestNeed(" + p[0] + ") == " + p[1]);
        for (int n = 1; n <= 35; n++) {
            int k = 0;
            while ((float) k / n < 0.75f) k++;                  // the engine's test (RULES: anchors / N >= 0.75f)
            check(Launcher.conquestNeed(n) == k, "conquestNeed(" + n + ") is the engine's least winning count");
        }
        int[][] thr = {{4, 2}, {6, 3}, {7, 4}, {8, 4}, {9, 5}, {12, 7}, {35, 25}};
        for (int[] p : thr) {
            check(!Launcher.conquestThreat(p[1] - 1, p[0]), "n=" + p[0] + ": no threat at " + (p[1] - 1));
            check(Launcher.conquestThreat(p[1], p[0]), "n=" + p[0] + ": threat at " + p[1]);
        }
        for (int n = -1; n <= 35; n++) {
            check(!Launcher.conquestThreat(0, n), "no island theirs: no threat (n=" + n + ")");
            for (int t = 0; t <= Math.max(0, n); t++)
                if (Launcher.conquestThreat(t, n) && !Launcher.conquestThreat(t + 1, n)) check(false, "monotone n=" + n + " t=" + t);
            if (n <= 0) for (int t = 0; t < 5; t++) check(!Launcher.conquestThreat(t, n), "n<=0: never");
        }
        for (int id = 0; id < 64; id++) {
            check(Launcher.isleFirst(true, id) == ((id & 1) == 0), "isleFirst(true, " + id + ")");
            check(!Launcher.isleFirst(false, id), "isleFirst(false, " + id + ")");
        }
        // theirsFor against pickObjective's rule (round 1000; slots: empty, neutral, ours, theirs with a tile)
        int r = 1000, tile = G.enc(new MapLocation(5, 5));
        int[] slots = {0, tile, 0x1000 | tile, 0x2000 | tile};
        int[] seens = {0, r, r - 5, r - 10, r - 11, r - 100, r - C.ISLE_MEM, r - C.ISLE_MEM - 1};
        for (int sh : slots) for (int own = 0; own <= 2; own++) for (int seen : seens) {
            int rule = seen > 0 && (r - seen <= 10 || sh == 0) ? own : sh >>> 12;
            boolean th = Launcher.theirsFor(sh, own, seen, r);
            String at = " (slot " + Integer.toHexString(sh) + " own " + own + " age " + (seen > 0 ? r - seen : -1) + ")";
            if (rule == 2) check(th, "pickObjective's theirs is theirs" + at);
            else {
                boolean extra = own == 2 && seen > 0 && r - seen > 10 && r - seen <= C.ISLE_MEM && sh != 0 && (sh >>> 12) == 0;
                check(th == extra, "beyond pickObjective's rule only our own fresh-enough theirs over a neutral slot" + at);
            }
            if ((sh >>> 12) == 1 && rule != 2) check(!th, "never over ours" + at);
            if (sh < 0x2000 && own != 2) check(!th, "islandScan's early skip is exact" + at);
        }
    }

    // ---------------------------------------------------------------- MapMem.mayWrite
    static void mayWrite() {
        int tile = G.enc(new MapLocation(7, 3));
        int[] slots = {0, tile, 0x1000 | tile, 0x2000 | tile};
        for (int age = 0; age <= 70; age++) for (int sh : slots) for (int owner = 0; owner <= 2; owner++) {
            boolean hr1 = !(age > 60 || (age > C.ISLAND_FRESH && sh != 0));   // c_hr1's flushIslands line 173
            boolean w = MapMem.mayWrite(age, sh, owner);
            String at = " (age " + age + " slot " + Integer.toHexString(sh) + " owner " + owner + ")";
            if (owner != 2) check(w == hr1, "owner 0/1: c_hr1's rule" + at);
            else check(w == (hr1 || (age <= C.ISLE_STICKY_AGE && sh != 0 && (sh >>> 12) == 0)), "owner 2: c_hr1's rule or sticky" + at);
            if ((sh >>> 12) == 1) check(w == hr1, "an owner-1 slot only as c_hr1" + at);
            if (age > C.ISLAND_FRESH && (sh >>> 12) == 1) check(!w, "the sticky write never overwrites ours" + at);
            if (age > 60) check(!w, "flushIslands' shortcut: past 60 never" + at);
            if (age <= C.ISLAND_FRESH) check(w, "flushIslands' shortcut: fresh always" + at);
        }
    }

    // ---------------------------------------------------------------- flushIslands through the RC
    static void flush() throws Exception {
        reset(10002, 500);
        Comms.canWrite = true;
        MapLocation t = new MapLocation(9, 9);
        int e = G.enc(t), sh0 = G.enc(new MapLocation(8, 8));
        // id: own owner, age, slot before, slot after
        int[][] cases = {
            {1, 2, 30, sh0, 0x2000 | e},                 // stale theirs over neutral: sticky write
            {2, 2, 30, 0x1000 | sh0, 0x1000 | sh0},      // never over ours
            {3, 0, 30, 0x2000 | sh0, 0x2000 | sh0},      // stale neutral over theirs: c_hr1 keeps it
            {4, 2, 61, sh0, sh0},                        // past 60: nothing
            {5, 1, 3, 0x2000 | sh0, 0x1000 | e},         // fresh news overwrites (c_hr1)
            {6, 2, 30, 0, 0x2000 | e},                   // fills an empty slot (c_hr1)
            {7, 2, C.ISLE_STICKY_AGE, sh0, 0x2000 | e},  // the window's last round
            {8, 1, 30, sh0, sh0},                        // stale ours over neutral: c_hr1 keeps neutral
        };
        for (int[] c : cases) {
            MapMem.islandTile[c[0]] = t; MapMem.islandOwner[c[0]] = c[1]; MapMem.islandSeen[c[0]] = 500 - c[2];
            shared[Comms.ISLANDS + c[0]] = c[3];
        }
        MapMem.flushIslands(0);
        for (int[] c : cases) check(shared[Comms.ISLANDS + c[0]] == c[4], "flush id " + c[0] + ": slot " + Integer.toHexString(shared[Comms.ISLANDS + c[0]]) + " want " + Integer.toHexString(c[4]));
    }

    // ---------------------------------------------------------------- pickObjective through the RC
    static final MapLocation HERE = new MapLocation(10, 10), NEAR = new MapLocation(14, 12), FAR = new MapLocation(25, 25),
        SIGHT = new MapLocation(12, 10);

    /** Islands 1..4: 1 theirs far, 2 theirs near, 3 ours, 4 neutral; a fresh sighting r2 4 away. */
    static void board(int round) {
        java.util.Arrays.fill(shared, 0);
        shared[Comms.ISLANDS + 1] = 0x2000 | G.enc(FAR);
        shared[Comms.ISLANDS + 2] = 0x2000 | G.enc(NEAR);
        shared[Comms.ISLANDS + 3] = 0x1000 | G.enc(new MapLocation(3, 3));
        shared[Comms.ISLANDS + 4] = G.enc(new MapLocation(30, 3));
        shared[Comms.ENEMY] = (((round >> 4) & 15) << 12) | G.enc(SIGHT);
    }

    static void pick() throws Exception {
        // even id under a threat (2 of 4 theirs, threshold 2): the nearest theirs before the sighting
        reset(10002, 500); board(500);
        MapLocation o = Launcher.pickObjective();
        check(NEAR.equals(o) && Launcher.objKind == 1 && Launcher.objIsland == 2, "even id under threat: nearest enemy island, kind 1, id 2");
        check(Launcher.isleThreat && Launcher.isleCheck == 500 + C.ISLE_RECHECK, "scan ran, next at +ISLE_RECHECK");
        check(islandReads == 4, "one scan reads each island once (" + islandReads + ")");
        check(writes == 0, "no shared write"); noRng("diverted");
        // cached for ISLE_RECHECK rounds: no island read until the next scan
        for (int r = 501; r < 500 + C.ISLE_RECHECK; r++) {
            G.round = r; islandReads = 0; board(r);
            o = Launcher.pickObjective();
            check(NEAR.equals(o) && Launcher.objKind == 1 && islandReads == 0, "r" + r + ": cached target, no scan");
        }
        G.round = 500 + C.ISLE_RECHECK; islandReads = 0; board(G.round);
        o = Launcher.pickObjective();
        check(NEAR.equals(o) && islandReads == 4 && Launcher.isleCheck == 500 + 2 * C.ISLE_RECHECK, "rescan at +ISLE_RECHECK");
        // the target seen this round not theirs is dropped (the sighting, c_hr1's path) until the next scan
        G.round = 506; board(506);
        MapMem.islandSeen[2] = 506; MapMem.islandOwner[2] = 0;
        o = Launcher.pickObjective();
        check(SIGHT.equals(o) && Launcher.objKind == 0 && Launcher.isleBest == null, "target seen neutral: dropped, sighting");
        G.round = 510; board(510);
        o = Launcher.pickObjective();
        check(!Launcher.isleThreat && SIGHT.equals(o) && Launcher.objKind == 0, "rescan: 1 of 4 theirs (own fresh neutral), no threat");
        check(writes == 0, "no shared write"); noRng("dropped");
        // dropped also when the sighting fell on a turn without march (a moving launcher marches every other round)
        reset(10002, 500); board(500);
        Launcher.pickObjective();
        G.round = 502; board(502); MapMem.islandSeen[2] = 501; MapMem.islandOwner[2] = 0;
        o = Launcher.pickObjective();
        check(SIGHT.equals(o) && Launcher.isleBest == null, "target seen neutral the round before this march: dropped");
        // our own record more than 10 rounds old yields to the slot (kept); a fresh "ours" drops the target
        reset(10002, 500); board(500); MapMem.islandSeen[2] = 489; MapMem.islandOwner[2] = 0;
        o = Launcher.pickObjective();
        check(NEAR.equals(o) && Launcher.isleThreat, "own neutral record 11 rounds old: the slot's theirs, diverted");
        G.round = 501; board(501);
        o = Launcher.pickObjective();
        check(NEAR.equals(o) && Launcher.isleBest != null, "own record past 10 rounds: target kept");
        G.round = 503; board(503); MapMem.islandSeen[2] = 502; MapMem.islandOwner[2] = 1;
        o = Launcher.pickObjective();
        check(SIGHT.equals(o) && Launcher.isleBest == null, "own fresh ours: dropped");
        // an empty slot: our own "theirs" at any age (pickObjective's rule) and our own tile
        reset(10002, 500); board(500); shared[Comms.ISLANDS + 2] = 0;
        MapMem.islandOwner[2] = 2; MapMem.islandSeen[2] = 300; MapMem.islandTile[2] = NEAR;
        o = Launcher.pickObjective();
        check(NEAR.equals(o) && Launcher.objIsland == 2 && Launcher.isleThreat, "empty slot: own theirs and MapMem.islandTile");
        check(writes == 0, "no shared write"); noRng("drop rule");

        // odd id: c_hr1's order (the sighting), no scan
        reset(10003, 500); board(500);
        o = Launcher.pickObjective();
        check(SIGHT.equals(o) && Launcher.objKind == 0 && Launcher.isleCheck == -1000, "odd id: sighting, no scan");
        check(islandReads == 0, "odd id: no island read before the sighting"); noRng("odd id");

        // a mender: no scan, c_hr1's pickObjective (march then overrides its objective)
        reset(10002, 500); board(500); Launcher.mending = true;
        o = Launcher.pickObjective();
        check(SIGHT.equals(o) && Launcher.isleCheck == -1000 && islandReads == 0, "mender: sighting, no scan");
        Launcher.mending = false;

        // even id below the threshold (1 of 4 theirs): the scan runs, the sighting stands
        reset(10002, 500); board(500); shared[Comms.ISLANDS + 1] = G.enc(FAR);
        o = Launcher.pickObjective();
        check(SIGHT.equals(o) && Launcher.objKind == 0 && !Launcher.isleThreat && Launcher.isleBest != null, "below threshold: sighting");

        // our own stale "theirs" within ISLE_MEM over a neutral slot counts (threat, target); past ISLE_MEM it does not
        reset(10002, 500); board(500); shared[Comms.ISLANDS + 1] = G.enc(FAR);
        MapMem.islandOwner[1] = 2; MapMem.islandSeen[1] = 500 - C.ISLE_MEM; MapMem.islandTile[1] = FAR;
        o = Launcher.pickObjective();
        check(NEAR.equals(o) && Launcher.isleThreat, "own theirs within ISLE_MEM: 2 of 4, threat");
        reset(10002, 500); board(500); shared[Comms.ISLANDS + 1] = G.enc(FAR);
        MapMem.islandOwner[1] = 2; MapMem.islandSeen[1] = 500 - C.ISLE_MEM - 1; MapMem.islandTile[1] = FAR;
        o = Launcher.pickObjective();
        check(SIGHT.equals(o) && !Launcher.isleThreat, "own theirs past ISLE_MEM: no threat");

        // short turn: the scan waits (isleCheck kept), c_hr1's path this turn
        reset(10002, 500); board(500); budget(C.ISLE_MIN_LEFT - 1);
        o = Launcher.pickObjective();
        check(SIGHT.equals(o) && Launcher.isleCheck == -1000 && !Launcher.isleThreat, "short turn: no scan, sighting");
        budget(10000);
        o = Launcher.pickObjective();
        check(NEAR.equals(o) && Launcher.isleCheck == 500 + C.ISLE_RECHECK, "next turn with the budget: scan, diverted");

        // a pass cut by ISLAND_LOOP_GUARD keeps the last result
        G.round = 505; board(505); shared[Comms.ISLANDS + 2] = G.enc(NEAR);   // now 1 of 4: a full scan would clear the threat
        budget(C.ISLAND_LOOP_GUARD + 1500); readCost = 1000;
        Launcher.islandScan();
        readCost = 0; budget(10000);
        check(Launcher.isleThreat && NEAR.equals(Launcher.isleBest) && Launcher.isleBestId == 2, "cut pass: last result kept");
        Launcher.islandScan();
        check(!Launcher.isleThreat && FAR.equals(Launcher.isleBest), "full pass: 1 of 4, no threat, far island kept as target");
        check(writes == 0, "no shared write in any launcher path");
    }

    // ---------------------------------------------------------------- fixture
    static void reset(int id, int round) throws Exception {
        java.util.Arrays.fill(shared, 0);
        java.util.Arrays.fill(MapMem.islandTile, null);
        java.util.Arrays.fill(MapMem.islandOwner, 0);
        java.util.Arrays.fill(MapMem.islandSeen, 0);
        G.rc = RC; G.id = id; G.round = round; G.here = HERE; G.W = G.H = 40; G.squad = false; G.us = Team.A; G.them = Team.B;
        Comms.canWrite = false;
        Launcher.isleCheck = -1000; Launcher.isleThreat = false; Launcher.isleBest = null; Launcher.isleBestId = 0;
        Launcher.islandCount = -1; Launcher.mending = false; Launcher.objKind = 3;
        islandReads = writes = readCost = 0; nIslands = 4;
        set(G.class, "rng", rngSeed);
        budget(10000);
    }

    static void noRng(String what) throws Exception { check((Integer) get(G.class, "rng") == rngSeed, what + ": no RNG draw"); }

    static Object get(Class<?> cls, String name) throws Exception {
        Field f = cls.getDeclaredField(name); f.setAccessible(true); return f.get(null);
    }

    static void set(Class<?> cls, String name, Object value) throws Exception {
        Field f = cls.getDeclaredField(name); f.setAccessible(true); f.set(null, value);
    }

    static int left() { return Clock.getBytecodesLeft(); }

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
