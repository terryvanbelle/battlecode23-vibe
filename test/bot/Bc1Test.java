package c_bc1;

import battlecode.common.*;
import battlecode.world.Inventory;

import java.lang.reflect.Proxy;
import java.util.Random;

/** c_bc1's bytecode cuts against the c_aura2 code they replace (copied below as ref* functions), on seeded random
 *  inputs: G.startTurn (enemies in nearby's order, fighter counts, and the lowest-id ally launcher and group size that
 *  Launcher.regroup used to count itself), the island scan of Launcher.pickObjective (ids downward, fast skip),
 *  Launcher.enemyHQs (cached MapMem.enemyHQs), Launcher.siegeTarget (cached), Launcher.raidWell (candidate list) and
 *  clearRaid/cleared (int codes, same RNG draws), and Launcher.enemiesStale (the end-of-turn shot re-senses after a
 *  move or an overrun, as c_aura2 always did). A RobotController proxy serves the shared array, the island count,
 *  the round, the location and the sensed robots; any other engine call fails the test. Exits non-zero on a failure. */
public class Bc1Test {
    static final Random R = new Random(20261011);
    static final int[] shared = new int[64];
    static RobotInfo[] sensed = new RobotInfo[0];
    static int islands, roundNow;
    static MapLocation locNow;

    public static void main(String[] a) {
        G.rc = proxy();
        G.us = Team.A; G.them = Team.B;
        G.W = 60; G.H = 60;
        rng(987654321);
        startTurn();
        islandScan();
        enemyHQsCache();
        siegeCache();
        raidAndCleared();
        enemiesStale();
        System.out.println("bc1: " + checks + " cases ok");
    }

    // ---------------------------------------------------------------- G.startTurn
    static final RobotType[] TYPES = {RobotType.LAUNCHER, RobotType.CARRIER, RobotType.AMPLIFIER, RobotType.HEADQUARTERS,
        RobotType.DESTABILIZER, RobotType.BOOSTER};

    static void startTurn() {
        RobotType[] self = {RobotType.LAUNCHER, RobotType.CARRIER, RobotType.HEADQUARTERS, RobotType.AMPLIFIER};
        for (int c = 0; c < 3000; c++) {
            int n = c % 7 == 0 ? 0 : R.nextInt(95);
            RobotInfo[] rs = new RobotInfo[n];
            int[] ids = shuffledIds(n);
            int enemyShare = c % 3 == 0 ? 0 : R.nextInt(101);   // a third of the cases: no enemy in vision
            for (int i = 0; i < n; i++) {
                Team t = R.nextInt(100) < enemyShare ? Team.B : Team.A;
                RobotType ty = R.nextInt(3) > 0 ? RobotType.LAUNCHER : TYPES[R.nextInt(TYPES.length)];
                rs[i] = new RobotInfo(ids[i], t, ty, new Inventory(), 1 + R.nextInt(200), L(R.nextInt(60), R.nextInt(60)));
            }
            sensed = rs;
            roundNow = 1 + R.nextInt(2000);
            locNow = L(R.nextInt(60), R.nextInt(60));
            G.type = self[c % self.length];
            G.allyLeader = null;
            try { G.startTurn(); } catch (GameActionException e) { check(false, "startTurn threw " + e); }
            check(G.nearby == rs && G.round == roundNow && G.here == locNow, "startTurn: nearby, round, here");
            RobotInfo[] e = refEnemies(rs);
            check(G.enemies.length == e.length, "startTurn: enemy count " + e.length + ", got " + G.enemies.length);
            for (int i = 0; i < e.length; i++) check(G.enemies[i] == e[i], "startTurn: enemy " + i + " in nearby's order");
            check(G.nEnemyFighters == refFighters(rs, Team.B) && G.nAllyFighters == refFighters(rs, Team.A),
                "startTurn: fighter counts");
            if (G.type == RobotType.LAUNCHER) {
                RobotInfo leader = null;
                int nGroup = 1;                                // c_aura2 Launcher.regroup's loop
                for (int i = rs.length; --i >= 0; ) {
                    RobotInfo r = rs[i];
                    if (r.team != G.us || r.type != RobotType.LAUNCHER) continue;
                    nGroup++;
                    if (leader == null || r.ID < leader.ID) leader = r;
                }
                check(G.allyLeader == leader, "startTurn: allyLeader is regroup's lowest-id ally launcher");
                check(1 + G.nAllyFighters == nGroup, "startTurn: 1 + nAllyFighters is regroup's n");
            } else check(G.allyLeader == null, "startTurn: allyLeader is set only for launchers");
        }
    }

    static RobotInfo[] refEnemies(RobotInfo[] nearby) {           // c_aura2 G.startTurn
        int ne = 0;
        for (int i = nearby.length; --i >= 0; ) if (nearby[i].team == G.them) ne++;
        RobotInfo[] e = new RobotInfo[ne];
        for (int i = nearby.length; --i >= 0; ) if (nearby[i].team == G.them) e[--ne] = nearby[i];
        return e;
    }

    static int refFighters(RobotInfo[] nearby, Team t) {
        int n = 0;
        for (RobotInfo r : nearby) {
            if (r.team != t) continue;
            if (r.type == RobotType.LAUNCHER || (t == G.them && r.type == RobotType.DESTABILIZER)) n++;
        }
        return n;
    }

    static int[] shuffledIds(int n) {
        int[] ids = new int[n];
        for (int i = 0; i < n; i++) ids[i] = 10000 + i * 7;
        for (int i = n; --i > 0; ) { int j = R.nextInt(i + 1), t = ids[i]; ids[i] = ids[j]; ids[j] = t; }
        return ids;
    }

    // ---------------------------------------------------------------- pickObjective's island scan
    static void islandScan() {
        HQState.ourHQs = new MapLocation[]{L(2, 2), L(3, 50)};
        MapMem.cand = MapMem.ROT;
        MapMem.nEnemyHQSeen = 0;
        Launcher.ehqC = null;
        int found = 0, ties = 0;
        for (int c = 0; c < 4000; c++) {
            java.util.Arrays.fill(shared, 0);
            G.round = 1 + R.nextInt(1500);
            G.here = L(10 + R.nextInt(3), 10 + R.nextInt(3));
            islands = c % 11 == 0 ? 0 : 1 + R.nextInt(35);
            Launcher.islandCount = -1;                         // read once per game; a new "game" here
            for (int id = 1; id < 40; id++) {
                MapMem.islandOwner[id] = R.nextInt(3);
                MapMem.islandSeen[id] = R.nextInt(3) == 0 ? 0 : Math.max(1, G.round - R.nextInt(25));
                MapMem.islandTile[id] = R.nextInt(5) == 0 ? null : L(7 + R.nextInt(7), 7 + R.nextInt(7));
                if (MapMem.islandSeen[id] == 0 && R.nextBoolean()) MapMem.islandOwner[id] = 0;
                if (id <= 35 && R.nextInt(10) < 7)
                    shared[Comms.ISLANDS + id] = (R.nextInt(3) << 12) | G.enc(L(7 + R.nextInt(7), 7 + R.nextInt(7)));
            }
            int[] want = refIslands();
            int seed = R.nextInt() | 1, prev = rng(seed);
            Launcher.predRound = G.round;                      // no prediction pass (it needs a live Clock)
            MapLocation got;
            try { got = Launcher.pickObjective(); } catch (GameActionException e) { check(false, "pickObjective threw " + e); return; }
            check(rng(prev) == seed, "pickObjective drew from the RNG");
            if (want[0] > 0) {
                found++;
                if (want[2] > 1) ties++;
                check(Launcher.objKind == 1 && Launcher.objIsland == want[0], "islands: id " + want[0] + ", got kind "
                    + Launcher.objKind + " id " + Launcher.objIsland + " (case " + c + ")");
                check(got != null && got.x == want[1] / 64 && got.y == want[1] % 64, "islands: tile of id " + want[0]);
            } else check(Launcher.objKind == 2 && Launcher.objIsland == 0, "islands: none theirs, the siege target (case " + c + ")");
        }
        check(found > 500 && ties > 100, "islands: the cases hit enemy islands (" + found + ") and distance ties (" + ties + ")");
        MapMem.cand = 7;
        Launcher.ehqC = null;
    }

    /** c_aura2 pickObjective's island loop: {id, x*64+y of its tile, ids at the best distance} (id 0 = none). */
    static int[] refIslands() {
        int n = Math.min(35, islands);
        MapLocation best = null;
        int bd = Integer.MAX_VALUE, bid = 0, nAt = 0;
        int[] dist = new int[n + 1];
        for (int id = 1; id <= n; id++) {
            dist[id] = -1;
            int sh = shared[Comms.ISLANDS + id];
            int owner = MapMem.islandSeen[id] > 0 && (G.round - MapMem.islandSeen[id] <= 10 || sh == 0) ? MapMem.islandOwner[id] : sh >>> 12;
            if (owner != 2) continue;
            MapLocation t = G.dec(sh & 0xfff);
            if (t == null) t = MapMem.islandTile[id];
            if (t == null) continue;
            int d = G.here.distanceSquaredTo(t);
            dist[id] = d;
            if (d < bd) { bd = d; best = t; bid = id; }
        }
        for (int id = 1; id <= n; id++) if (dist[id] == bd) nAt++;
        return new int[]{bid, best == null ? -1 : best.x * 64 + best.y, nAt};
    }

    // ---------------------------------------------------------------- Launcher.enemyHQs
    static void enemyHQsCache() {
        G.W = 41; G.H = 33;
        MapMem.nEnemyHQSeen = 0;
        MapMem.cand = 7;
        HQState.ourHQs = null;
        Launcher.ehqC = null;
        MapLocation[] last = null;
        for (int step = 0; step < 3000; step++) {
            int k = R.nextInt(10);
            boolean same = false;
            if (k == 0) MapMem.cand = 1 + R.nextInt(7);
            else if (k == 1 && MapMem.nEnemyHQSeen < 4) MapMem.enemyHQSeen[MapMem.nEnemyHQSeen++] = L(R.nextInt(41), R.nextInt(33));
            else if (k == 2) HQState.ourHQs = randomHQs();
            else if (k == 3 && MapMem.nEnemyHQSeen >= 4) {       // a new game: the bot never shrinks the seen list
                MapMem.nEnemyHQSeen = 0; Launcher.ehqC = null; HQState.ourHQs = randomHQs();
            } else same = true;
            MapLocation[] got = Launcher.enemyHQs(), want = MapMem.enemyHQs();
            check(sameLocs(got, want), "enemyHQs: the cached array matches a fresh MapMem.enemyHQs() (step " + step + ")");
            if (same && last != null) check(got == last, "enemyHQs: nothing changed, the same array");
            last = got;
        }
    }

    static MapLocation[] randomHQs() {
        int n = R.nextInt(5);                                   // 0..4 (0: an empty list, as before registration)
        if (R.nextInt(8) == 0) return null;
        MapLocation[] o = new MapLocation[n];
        for (int i = 0; i < n; i++) o[i] = L(R.nextInt(G.W), R.nextInt(G.H));
        return o;
    }

    // ---------------------------------------------------------------- Launcher.siegeTarget
    static void siegeCache() {
        G.W = 60; G.H = 60;
        int[] rounds = {50, 1999, C.SIEGE_ROTATE_FROM, C.SIEGE_ROTATE_FROM + 99, C.SIEGE_ROTATE_FROM + 100, 2250, 2399, 2400};
        MapLocation[] ehq = randomLocs(1 + R.nextInt(8));
        int hits = 0;
        for (int step = 0; step < 5000; step++) {
            int k = R.nextInt(8);
            if (k == 0) ehq = randomLocs(1 + R.nextInt(8));
            else if (k == 1) HQState.ourHQs = randomHQs();
            else if (k == 2) G.round = rounds[R.nextInt(rounds.length)];
            else if (k == 3) G.here = L(R.nextInt(60), R.nextInt(60));
            else if (k == 4) ehq = ehq.clone();                // same contents, new array
            else hits++;
            if (G.here == null) G.here = L(30, 30);
            MapLocation want = refSiegeTarget(ehq), got = Launcher.siegeTarget(ehq);
            check(want == got, "siegeTarget: " + want + ", got " + got + " (step " + step + ")");
        }
        check(hits > 1000, "siegeTarget: repeated calls exercised");
    }

    static MapLocation refSiegeTarget(MapLocation[] ehq) {        // c_aura2 Launcher.siegeTarget + ourCentroid
        MapLocation from;
        MapLocation[] o = HQState.ourHQs;
        if (o == null || o.length == 0) from = G.here;
        else {
            int x = 0, y = 0;
            for (int i = o.length; --i >= 0; ) { x += o[i].x; y += o[i].y; }
            from = new MapLocation(x / o.length, y / o.length);
        }
        int n = ehq.length;
        int rank = G.round < C.SIEGE_ROTATE_FROM ? 0 : (1 + (G.round - C.SIEGE_ROTATE_FROM) / C.SIEGE_ROTATE) % n;
        boolean[] used = new boolean[n];
        MapLocation hq = null;
        for (int r = 0; r <= rank; r++) {
            int bd = Integer.MAX_VALUE, bi = -1;
            for (int i = n; --i >= 0; ) {
                if (used[i]) continue;
                int d = from.distanceSquaredTo(ehq[i]);
                if (d < bd || (d == bd && G.enc(ehq[i]) < G.enc(ehq[bi]))) { bd = d; bi = i; }
            }
            used[bi] = true;
            hq = ehq[bi];
        }
        return hq;
    }

    // ---------------------------------------------------------------- raidWell, clearRaid, cleared
    static MapLocation[] rLoc = new MapLocation[16];
    static int[] rUntil = new int[16];
    static int rN;

    static void raidAndCleared() {
        G.round = 100;
        MapLocation hq = L(30, 30);
        MapLocation[] pw = randomWells();
        int answered = 0, rngDraws = 0;
        for (int step = 0; step < 20000; step++) {
            G.round += R.nextInt(4);
            int k = R.nextInt(12);
            if (k == 0) pw = randomWells();
            else if (k == 1) pw = pw.clone();
            else if (k == 2) hq = L(26 + R.nextInt(9), 26 + R.nextInt(9));
            else if (k == 3) hq = new MapLocation(hq.x, hq.y);  // equal hq, new object
            else if (k <= 5 && pw.length > 0) {
                MapLocation w = R.nextInt(6) == 0 ? L(R.nextInt(60), R.nextInt(60)) : pw[R.nextInt(pw.length)];
                int until = R.nextBoolean() ? G.round : G.round + 5000;
                int before = rng(0);
                rng(before);
                Launcher.clearRaid(w, until);
                int after = rng(before);                        // replay the c_aura2 clearRaid from the same RNG state
                refClearRaid(w, until);
                check(rng(after) == after, "clearRaid: same RNG draws as c_aura2");
                if (after != before) rngDraws++;
                check(Launcher.nCleared == rN, "clearRaid: table size");
                for (int i = 0; i < rN; i++)
                    check(Launcher.clearedLoc[i].equals(rLoc[i]) && Launcher.clearedUntil[i] == rUntil[i]
                        && Launcher.clearedEnc[i] == G.enc(rLoc[i]), "clearRaid: entry " + i);
            }
            Launcher.predWells = pw;
            Launcher.predRound = G.round;                      // no prediction pass (it needs a live Clock)
            MapLocation want = refRaidWell(hq, pw), got;
            try { got = Launcher.raidWell(hq, null); } catch (GameActionException e) { check(false, "raidWell threw " + e); return; }
            check(want == got, "raidWell: " + want + ", got " + got + " (step " + step + ")");
            if (got != null) answered++;
            for (int t = 0; t < 3; t++) {
                MapLocation w = L(20 + R.nextInt(21), 20 + R.nextInt(21));
                check(Launcher.cleared(w) == refCleared(w), "cleared(" + w + ")");
            }
        }
        check(answered > 2000 && rngDraws > 50 && rN == 16, "raidWell: answers (" + answered + ") and full-table RNG draws ("
            + rngDraws + ") exercised");
    }

    static MapLocation[] randomWells() {
        int n = R.nextInt(40);                                  // computePredWells keeps at most 39
        MapLocation[] w = new MapLocation[n];
        for (int i = 0; i < n; i++) w[i] = L(20 + R.nextInt(21), 20 + R.nextInt(21));
        return w;
    }

    static void refClearRaid(MapLocation w, int round) {          // c_aura2 Launcher.clearRaid
        for (int i = rN; --i >= 0; ) if (rLoc[i].equals(w)) { rUntil[i] = round + C.RAID_CLEAR_ROUNDS; return; }
        int k = rN < rLoc.length ? rN++ : G.rand(rLoc.length);
        rLoc[k] = w;
        rUntil[k] = round + C.RAID_CLEAR_ROUNDS;
    }

    static boolean refCleared(MapLocation w) {                     // c_aura2 Launcher.cleared
        for (int i = rN; --i >= 0; ) if (rLoc[i].equals(w)) return G.round < rUntil[i];
        return false;
    }

    static MapLocation refRaidWell(MapLocation hq, MapLocation[] predWells) {   // c_aura2 Launcher.raidWell's scan
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = predWells.length; --i >= 0; ) {
            MapLocation w = predWells[i];
            int d = w.distanceSquaredTo(hq);
            if (d > C.RAID_R2 || d >= bd || refCleared(w)) continue;
            bd = d; best = w;
        }
        return best;
    }

    // ---------------------------------------------------------------- Launcher.enemiesStale
    /** c_aura2 re-sensed the enemies before every end-of-turn shot; c_bc1 keeps G.startTurn's G.enemies only when the
     *  sense is certainly current: the robot stands on the tile it sensed from, in the round it sensed in. Moved, or
     *  resumed after an overrun (the same instruction, a round or more later), it re-senses. */
    static void enemiesStale() {
        G.type = RobotType.LAUNCHER;
        int moved = 0, overran = 0, kept = 0;
        for (int c = 0; c < 3000; c++) {
            sensed = new RobotInfo[0];
            roundNow = 1 + R.nextInt(2000);
            locNow = L(R.nextInt(60), R.nextInt(60));
            try { G.startTurn(); } catch (GameActionException e) { check(false, "startTurn threw " + e); return; }
            MapLocation at = G.here;
            boolean move = R.nextInt(3) == 0, overrun = R.nextInt(3) == 0;
            if (move) { Direction d = G.DIRS[R.nextInt(8)]; locNow = at.add(d); }
            else locNow = new MapLocation(at.x, at.y);           // the same tile, another object
            if (overrun) roundNow += 1 + R.nextInt(3);
            G.here = G.rc.getLocation();                        // Launcher.run re-reads it first
            boolean got = Launcher.enemiesStale(at);
            check(got == (move || overrun), "enemiesStale: moved " + move + ", overran " + overrun + ", got " + got);
            if (move) moved++; else if (overrun) overran++; else kept++;
        }
        check(moved > 500 && overran > 300 && kept > 500, "enemiesStale: cases exercised (" + moved + ", " + overran + ", "
            + kept + ")");
    }

    // ---------------------------------------------------------------- helpers
    static RobotController proxy() {
        return (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
            new Class<?>[]{RobotController.class}, (p, m, args) -> {
                switch (m.getName()) {
                    case "readSharedArray": return shared[(Integer) args[0]];
                    case "getIslandCount": return islands;
                    case "getRoundNum": return roundNow;
                    case "getLocation": return locNow;
                    case "senseNearbyRobots": if (args == null || args.length == 0) return sensed; break;
                    default: break;
                }
                throw new UnsupportedOperationException("engine call outside the test's proxy: " + m.getName());
            });
    }

    static MapLocation[] randomLocs(int n) {
        MapLocation[] o = new MapLocation[n];
        for (int i = 0; i < n; i++) o[i] = L(R.nextInt(60), R.nextInt(60));
        return o;
    }

    static boolean sameLocs(MapLocation[] a, MapLocation[] b) {
        if (a.length != b.length) return false;
        for (int i = 0; i < a.length; i++) if (!a[i].equals(b[i])) return false;
        return true;
    }

    static MapLocation L(int x, int y) { return new MapLocation(x, y); }

    /** Sets G's private RNG state (reflection) and returns the previous one. */
    static int rng(int v) {
        try {
            java.lang.reflect.Field fl = G.class.getDeclaredField("rng");
            fl.setAccessible(true);
            int was = fl.getInt(null);
            fl.setInt(null, v);
            return was;
        } catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("bc1 FAILED: " + what); System.exit(1); }
    }
}
