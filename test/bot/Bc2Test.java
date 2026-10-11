package c_bc2;

import battlecode.common.*;
import battlecode.world.Inventory;

import java.lang.reflect.Proxy;
import java.util.Random;

/** c_bc2 = c_bc1 + a decision-preserving cut of Launcher.computePredWells: (a) a pass whose inputs (symmetry,
 *  predicted enemy HQs, shared well slots, the count of seen wells) equal those of the last pass that finished keeps
 *  its list and only restarts the timer; (b) candidates outside the HQs' box grown by C.RAID_BOX are rejected on raw
 *  coordinates; (c) the duplicate test compares location codes. The c_bc1 functions are copied below as ref*
 *  functions and compared on seeded random inputs: fresh passes (contents, order, the 38 limit, the seen wells' own
 *  objects), a launcher's sequence of timer fires (skips exactly when the inputs equal the last finished pass's, a call
 *  under the guard is c_bc1's guarded pass (an empty list, retried in 5 rounds, the key forgotten), raidWell on top),
 *  the helper addPredE and the box bound. Clock.getBytecodesLeft() is the engine monitor's field, set by reflection. Bc1Test's cases are included, ported to c_bc2 (c_bc1's cuts against the c_aura2
 *  code they replace): G.startTurn, the island scan of Launcher.pickObjective, Launcher.enemyHQs and siegeTarget
 *  (cached), raidWell's candidate list and clearRaid/cleared, Launcher.enemiesStale. A RobotController proxy serves the
 *  shared array, the island count, the round, the location and the sensed robots; any other engine call fails the
 *  test. Exits non-zero on a failure. */
public class Bc2Test {
    static final Random R = new Random(20261011);
    static final int[] shared = new int[64];
    static RobotInfo[] sensed = new RobotInfo[0];
    /** The proxy drops the budget under the guard when it serves this slot (-1: never). */
    static int dropAt = -1;
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
        try {                                                   // c_bc2
            raidBox();
            addPredE();
            predWellsRandom();
            predWellsSequence();
        } catch (GameActionException e) { check(false, "threw " + e); }
        System.out.println("bc2: " + checks + " cases ok");
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

    // ================================================================ c_bc2: Launcher.computePredWells
    /** The c_bc1 computePredWells and addPred (copied; the bytecode guard left out: the reference is c_bc1's pass when
     *  it finishes), over the same shared array (proxy), MapMem seen wells, MapMem.cand and G.W/G.H. */
    static MapLocation[] refPredWells(MapLocation[] ehq) throws GameActionException {
        int s = MapMem.cand == 1 || MapMem.cand == 2 || MapMem.cand == 4 ? MapMem.cand : (MapMem.cand & 1) != 0 ? 1 : (MapMem.cand & 2) != 0 ? 2 : 4;
        MapLocation[] out = new MapLocation[40];
        int n = 0;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS && n < 38; i++) {
            int c = Comms.read(i);
            if (c == 0) break;
            MapLocation l = G.dec(c & 0xfff);
            n = refAddPred(out, n, l, ehq);
            n = refAddPred(out, n, MapMem.img(s, l), ehq);
        }
        for (int j = MapMem.seenWellCount(); --j >= 0 && n < 38; ) {
            MapLocation l = MapMem.seenWellAt(j);
            n = refAddPred(out, n, l, ehq);
            n = refAddPred(out, n, MapMem.img(s, l), ehq);
        }
        MapLocation[] r = new MapLocation[n];
        System.arraycopy(out, 0, r, 0, n);
        return r;
    }

    /** c_bc1's computePredWells verbatim, guards included, on the test's state; returns its list and its predRound in
     *  round[0] (Clock.getBytecodesLeft() is constant here: a budget under 4,500 cuts it at its first guard). */
    static MapLocation[] refPredWellsGuarded(MapLocation[] ehq, int[] round) throws GameActionException {
        int predRound = G.round;
        int s = MapMem.cand == 1 || MapMem.cand == 2 || MapMem.cand == 4 ? MapMem.cand : (MapMem.cand & 1) != 0 ? 1 : (MapMem.cand & 2) != 0 ? 2 : 4;
        MapLocation[] out = new MapLocation[40];
        int n = 0;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS && n < 38; i++) {
            if (Clock.getBytecodesLeft() < 4500) { predRound = G.round - 15; break; }
            int c = Comms.read(i);
            if (c == 0) break;
            MapLocation l = G.dec(c & 0xfff);
            n = refAddPred(out, n, l, ehq);
            n = refAddPred(out, n, MapMem.img(s, l), ehq);
        }
        for (int j = MapMem.seenWellCount(); --j >= 0 && n < 38; ) {
            if (Clock.getBytecodesLeft() < 4500) { predRound = G.round - 15; break; }
            MapLocation l = MapMem.seenWellAt(j);
            n = refAddPred(out, n, l, ehq);
            n = refAddPred(out, n, MapMem.img(s, l), ehq);
        }
        round[0] = predRound;
        MapLocation[] r = new MapLocation[n];
        System.arraycopy(out, 0, r, 0, n);
        return r;
    }

    static int refAddPred(MapLocation[] out, int n, MapLocation l, MapLocation[] ehq) {
        boolean near = false;
        for (int k = ehq.length; --k >= 0; ) if (ehq[k].distanceSquaredTo(l) <= C.RAID_R2) { near = true; break; }
        if (!near) return n;
        for (int k = n; --k >= 0; ) if (out[k].equals(l)) return n;
        out[n] = l;
        return n + 1;
    }

    static final int BIG = 1000000;

    /** The box bound: RAID_BOX is the integer square root of RAID_R2, and a tile outside the box of the HQs grown by
     *  RAID_BOX is beyond r2 RAID_R2 of every HQ (brute force); the box keeps every tile within r2 RAID_R2 of one. */
    static void raidBox() {
        check(C.RAID_BOX * C.RAID_BOX <= C.RAID_R2 && (C.RAID_BOX + 1) * (C.RAID_BOX + 1) > C.RAID_R2,
            "RAID_BOX " + C.RAID_BOX + " is the integer square root of RAID_R2 " + C.RAID_R2);
        int outside = 0, inside = 0;
        for (int c = 0; c < 3000; c++) {
            MapLocation[] h = randomLocs(1 + R.nextInt(12));
            int x0 = 1000, x1 = -1000, y0 = 1000, y1 = -1000;
            for (MapLocation l : h) { x0 = Math.min(x0, l.x); x1 = Math.max(x1, l.x); y0 = Math.min(y0, l.y); y1 = Math.max(y1, l.y); }
            for (int t = 0; t < 40; t++) {
                MapLocation p = L(R.nextInt(60), R.nextInt(60));
                boolean near = false;
                for (MapLocation l : h) if (l.distanceSquaredTo(p) <= C.RAID_R2) near = true;
                boolean in = p.x >= x0 - C.RAID_BOX && p.x <= x1 + C.RAID_BOX && p.y >= y0 - C.RAID_BOX && p.y <= y1 + C.RAID_BOX;
                if (!in) { outside++; check(!near, "box: " + p + " outside the box is within r2 RAID_R2 of an HQ"); }
                else inside++;
            }
        }
        check(outside > 10000 && inside > 10000, "box: cases on both sides (" + outside + ", " + inside + ")");
    }

    /** Launcher.addPredE (the duplicate test and append, called for a candidate the caller found near an HQ with
     *  c_bc1's distanceSquaredTo test) against c_bc1's addPred on random lists: same answer, same list. */
    static void addPredE() {
        int added = 0, dups = 0, far = 0;
        for (int c = 0; c < 4000; c++) {
            MapLocation[] h = randomLocs(R.nextInt(13));
            MapLocation[] ref = new MapLocation[40];
            int n = 0, rn = 0;
            for (int t = 0; t < 39 && n < 38; t++) {
                MapLocation p = h.length > 0 && R.nextInt(3) > 0 ? near(h[R.nextInt(h.length)], 12, 60, 60) : L(R.nextInt(60), R.nextInt(60));
                if (rn > 0 && R.nextInt(5) == 0) { MapLocation d = ref[R.nextInt(rn)]; p = L(d.x, d.y); }   // listed: a duplicate
                int was = rn;
                rn = refAddPred(ref, rn, p, h);
                boolean isNear = false;                         // computePredWells' inline near test
                for (int q = h.length; --q >= 0; ) if (h[q].distanceSquaredTo(p) <= C.RAID_R2) { isNear = true; break; }
                int got = isNear ? Launcher.addPredE(n, p.x * 64 + p.y + 1, p) : n;
                check(got == rn, "addPredE: count " + rn + ", got " + got);
                if (rn > was) {
                    added++;
                    check(Launcher.predOut[n] == p && Launcher.predEnc[n] == G.enc(p), "addPredE: the entry (itself) and its code");
                } else if (isNear) dups++; else far++;
                n = got;
            }
            for (int i = 0; i < n; i++) check(Launcher.predOut[i].equals(ref[i]), "addPredE: list entry " + i);
        }
        check(added > 20000 && dups > 2000 && far > 5000, "addPredE: added " + added + ", duplicates " + dups + ", far " + far);
    }

    // scenario state: the shared well slots are shared[Comms.WELLS..], the seen wells MapMem's (reflection)
    static int nSlots;
    static MapLocation[] seenObjs = new MapLocation[32];
    static int nSeenObjs;

    /** A location within `r` tiles (x and y) of c, clamped to a W x H map. */
    static MapLocation near(MapLocation c, int r, int w, int h) {
        int x = Math.max(0, Math.min(w - 1, c.x - r + R.nextInt(2 * r + 1)));
        int y = Math.max(0, Math.min(h - 1, c.y - r + R.nextInt(2 * r + 1)));
        return L(x, y);
    }

    /** A well location: near a predicted HQ, near the image of one (so its image is near), or anywhere. */
    static MapLocation wellLoc(MapLocation[] ehq, int s, boolean dense) {
        int k = R.nextInt(10);
        if (ehq.length > 0 && k < (dense ? 5 : 3)) return near(ehq[R.nextInt(ehq.length)], 13, G.W, G.H);
        if (ehq.length > 0 && k < (dense ? 9 : 6)) return near(MapMem.img(s, ehq[R.nextInt(ehq.length)]), 13, G.W, G.H);
        return L(R.nextInt(G.W), R.nextInt(G.H));
    }

    static int symOf(int cand) { return cand == 1 || cand == 2 || cand == 4 ? cand : (cand & 1) != 0 ? 1 : (cand & 2) != 0 ? 2 : 4; }

    static void addSlot(MapLocation l) { shared[Comms.WELLS + nSlots++] = ((1 + R.nextInt(3)) << 12) | G.enc(l); }

    /** Appends a seen well (a new object, as MapMem keeps its own): sometimes the location of a shared one. */
    static void addSeen(MapLocation[] ehq, int s, boolean dense) {
        MapLocation l;
        if (nSlots > 0 && R.nextInt(4) == 0) l = G.dec(shared[Comms.WELLS + R.nextInt(nSlots)] & 0xfff);
        else if (nSeenObjs > 0 && R.nextInt(12) == 0) { MapLocation d = seenObjs[R.nextInt(nSeenObjs)]; l = L(d.x, d.y); }
        else l = wellLoc(ehq, s, dense);
        seenObjs[nSeenObjs++] = l;
        setSeen();
    }

    static MapLocation[] randomEhq(int s) {
        int k = R.nextInt(10);
        if (k == 0) return new MapLocation[0];
        if (k < 6) {                                               // MapMem.enemyHQs(): images of our HQs
            int n = 1 + R.nextInt(4);
            MapLocation[] o = new MapLocation[n];
            for (int i = 0; i < n; i++) o[i] = L(R.nextInt(G.W), R.nextInt(G.H));
            HQState.ourHQs = o;
            MapMem.nEnemyHQSeen = 0;
            return MapMem.enemyHQs();
        }
        MapLocation[] e = new MapLocation[1 + R.nextInt(12)];
        for (int i = 0; i < e.length; i++) e[i] = L(R.nextInt(G.W), R.nextInt(G.H));
        return e;
    }

    static void newScenario() {
        G.W = 20 + R.nextInt(41); G.H = 20 + R.nextInt(41);
        MapMem.cand = 1 + R.nextInt(7);
        java.util.Arrays.fill(shared, 0);
        nSlots = 0; nSeenObjs = 0;
        setSeen();
    }

    /** Compares Launcher.predWells with the reference list: contents, order, length (the 38 limit) and, for each entry
     *  the reference took from MapMem's seen wells, the same object. */
    static void checkPred(MapLocation[] want, String what) {
        MapLocation[] got = Launcher.predWells;
        check(got.length == want.length, what + ": " + want.length + " wells, got " + got.length);
        for (int i = 0; i < want.length; i++) {
            check(got[i].equals(want[i]), what + ": entry " + i + " " + want[i] + ", got " + got[i]);
            boolean seenObj = false;
            for (int j = 0; j < nSeenObjs; j++) if (seenObjs[j] == want[i]) seenObj = true;
            if (seenObj) check(got[i] == want[i], what + ": entry " + i + " is the seen well's own object");
        }
    }

    /** Fresh passes (no remembered key) on random inputs: the list is c_bc1's. */
    static void predWellsRandom() throws GameActionException {
        setBudget(BIG);
        int limit = 0, empty = 0, boxed = 0, seenListed = 0, cases = 0;
        for (int c = 0; c < 30000; c++) {
            boolean dense = c % 3 == 0;
            newScenario();
            int s = symOf(MapMem.cand);
            MapLocation[] ehq = randomEhq(s);
            int slots = c % 5 == 0 ? 16 : R.nextInt(17), seen = c % 7 == 0 ? 32 : R.nextInt(33);
            for (int i = 0; i < slots; i++) addSlot(nSlots > 0 && R.nextInt(15) == 0 ? G.dec(shared[Comms.WELLS] & 0xfff) : wellLoc(ehq, s, dense));
            for (int i = 0; i < seen; i++) addSeen(ehq, s, dense);
            Launcher.pkS = -1;
            G.round = 1 + R.nextInt(2000);
            int seed = R.nextInt() | 1, prev = rng(seed);
            MapLocation[] want = refPredWells(ehq);
            Launcher.computePredWells(ehq);
            check(rng(prev) == seed, "computePredWells drew from the RNG");
            checkPred(want, "predWells (case " + c + ")");
            check(Launcher.predRound == G.round && Launcher.pkS == s, "predWells: a finished pass restarts the timer and keeps its key");
            cases++;
            if (want.length >= 38) limit++;
            if (want.length == 0) empty++;
            if (ehq.length > 0 && boxRejects(ehq, s) > 0) boxed++;
            for (MapLocation w : want) for (int j = 0; j < nSeenObjs; j++) if (seenObjs[j] == w) { seenListed++; break; }
        }
        check(limit > 2000 && empty > 1000 && boxed > 10000 && seenListed > 10000, "predWells: cases at the 38 limit (" + limit
            + "), empty (" + empty + "), with box rejections (" + boxed + "), seen objects listed (" + seenListed + ")");
        System.out.println("bc2: " + cases + " fresh passes (" + limit + " at the 38 limit, " + empty + " empty)");
    }

    /** Candidates of the current inputs that the box rejects (each is also far from every HQ: raidBox). */
    static int boxRejects(MapLocation[] ehq, int s) {
        int x0 = 1000, x1 = -1000, y0 = 1000, y1 = -1000, r = 0;
        for (MapLocation l : ehq) { x0 = Math.min(x0, l.x); x1 = Math.max(x1, l.x); y0 = Math.min(y0, l.y); y1 = Math.max(y1, l.y); }
        for (int i = 0; i < nSlots + nSeenObjs; i++) {
            MapLocation l = i < nSlots ? G.dec(shared[Comms.WELLS + i] & 0xfff) : seenObjs[i - nSlots];
            for (MapLocation p : new MapLocation[]{l, MapMem.img(s, l)})
                if (p.x < x0 - C.RAID_BOX || p.x > x1 + C.RAID_BOX || p.y < y0 - C.RAID_BOX || p.y > y1 + C.RAID_BOX) r++;
        }
        return r;
    }

    /** A launcher's game: inputs change one at a time (wells appended, a slot's type rewritten, the symmetry narrowed,
     *  a new ehq array with the same or other content, a call under the guard) and raidWell's 20-round timer fires the
     *  pass. A pass is skipped (same predWells array, timer restarted) exactly when the inputs equal those of the last
     *  pass that finished; the list is c_bc1's whenever the pass finishes; a call under the guard is c_bc1's cut pass
     *  (an empty list, retried in 5 rounds) and forgets the key. */
    static void predWellsSequence() throws GameActionException {
        int skips = 0, runs = 0, cuts = 0, cutSkips = 0, midCuts = 0, midSkips = 0, raids = 0, typeOnly = 0, sameContent = 0, reverts = 0;
        for (int g = 0; g < 400; g++) {
            boolean dense = g % 2 == 0;
            newScenario();
            MapMem.cand = 7;
            int s = symOf(MapMem.cand);
            MapLocation[] ehq = randomEhq(s);
            if (ehq.length == 0) ehq = new MapLocation[]{L(R.nextInt(G.W), R.nextInt(G.H))};
            Launcher.pkS = -1; Launcher.predWells = new MapLocation[0]; Launcher.predRound = -100; Launcher.rcPred = null;
            Launcher.nCleared = 0; rN = 0;                    // no raided well: raidWell's answer is the nearest
            G.round = 2;
            String lastKey = null;                              // the test's own key of the last finished pass
            MapLocation[] prevEhq = null;                       // the HQs before the last change (k 8 reverts to them)
            for (int step = 0; step < 80; step++) {
                int k = R.nextInt(16);
                boolean cut = false, midCut = k == 10 || k == 11;   // 11: usually unchanged inputs
                MapLocation[] before5 = ehq;
                if (k == 0 && nSlots < 16) addSlot(wellLoc(ehq, s, dense));
                else if (k == 1 && nSlots > 0) {               // the type of a slot changes, its location does not
                    int i = Comms.WELLS + R.nextInt(nSlots), v = shared[i];
                    shared[i] = ((((v >>> 12) % 3) + 1) << 12) | (v & 0xfff);
                    typeOnly++;
                } else if (k == 2 && nSeenObjs < 32) addSeen(ehq, s, dense);
                else if (k == 3 && Integer.bitCount(MapMem.cand) > 1) {
                    int bits = MapMem.cand, drop;
                    do { drop = 1 << R.nextInt(3); } while ((bits & drop) == 0);
                    MapMem.cand = bits & ~drop;
                    s = symOf(MapMem.cand);
                } else if (k == 4) { ehq = ehq.clone(); sameContent++; }
                else if (k == 5) {
                    MapLocation[] e = ehq.clone();
                    e[R.nextInt(e.length)] = L(R.nextInt(G.W), R.nextInt(G.H));
                    ehq = e;
                } else if (k == 6) {                           // a call under the guard on changed inputs
                    cut = true;
                    if (R.nextBoolean() && nSeenObjs < 32) addSeen(ehq, s, dense);
                    else { MapLocation[] e = ehq.clone(); e[R.nextInt(e.length)] = L(R.nextInt(G.W), R.nextInt(G.H)); ehq = e; }
                } else if (k == 7) cut = true;                 // under the guard on usually unchanged inputs: c_bc1
                else if (k == 8 && prevEhq != null) { ehq = prevEhq.clone(); reverts++; }   // back to earlier HQs
                else if (k == 10 && nSeenObjs < 32) addSeen(ehq, s, dense);
                else if (k == 9 && nSlots > 0) {               // a slot's location rewritten (the bot claims a slot
                    int i = Comms.WELLS + R.nextInt(nSlots);     // once; the key compares locations all the same)
                    shared[i] = (shared[i] & 0xf000) | G.enc(wellLoc(ehq, s, dense));
                }
                if (k == 5 || k == 6) prevEhq = before5;
                G.round += 20 + R.nextInt(3);
                MapLocation[] before = Launcher.predWells;
                String key = keyOf(s, ehq);
                boolean expectSkip = key.equals(lastKey);
                if (cut) {                                      // under the guard: c_bc1's guarded pass, whatever the key
                    setBudget(4499);
                    int[] refRound = new int[1];
                    MapLocation[] refList = refPredWellsGuarded(ehq, refRound);
                    Launcher.computePredWells(ehq);
                    setBudget(BIG);
                    check(Launcher.predRound == refRound[0] && refRound[0] == G.round - 15 && Launcher.pkS == -1,
                        "a call under the guard retries in 5 rounds, as c_bc1's cut pass, and forgets the key");
                    check(Launcher.predWells != before && sameLocs(Launcher.predWells, refList) && refList.length == 0,
                        "a call under the guard lists nothing, as c_bc1's pass cut at its first guard");
                    if (expectSkip) cutSkips++;
                    lastKey = null;
                    cuts++;
                    continue;
                }
                if (midCut) {                                   // the budget runs out on the key's last slot read
                    dropAt = Comms.WELLS + Math.min(nSlots, Comms.NWELLS - 1);
                    Launcher.computePredWells(ehq);
                    dropAt = -1;
                    setBudget(BIG);
                    if (expectSkip) {                           // a matching key returns before the pass and its guard
                        check(Launcher.predWells == before && Launcher.predRound == G.round, "a skip after the budget ran out");
                        skips++; midSkips++;
                    } else if (nSlots + nSeenObjs == 0) {       // no well to visit: no guard reached, finished
                        check(Launcher.predWells.length == 0 && Launcher.predRound == G.round, "no wells: an empty list, finished");
                        lastKey = key;
                        runs++;
                    } else {                                    // the pass stops at its first guard: forgotten
                        check(Launcher.predRound == G.round - 15 && Launcher.pkS == -1 && Launcher.predWells != before
                            && Launcher.predWells.length == 0, "a pass cut at its first guard: empty, retried in 5, forgotten");
                        lastKey = null;
                        midCuts++;
                    }
                    continue;
                }
                MapLocation hq = ehq[R.nextInt(ehq.length)];
                MapLocation want = refRaidWell(hq, refPredWells(ehq));
                MapLocation got = Launcher.raidWell(hq, ehq);
                check(Launcher.predRound == G.round, "the timer restarts (step " + step + ")");
                checkPred(refPredWells(ehq), "sequence g" + g + " step " + step);
                check(want == null ? got == null : want.equals(got), "raidWell after the pass: " + want + ", got " + got);
                if (got != null) raids++;
                if (expectSkip) { check(Launcher.predWells == before, "unchanged inputs: the pass is skipped (step " + step + ")"); skips++; }
                else { check(Launcher.predWells != before, "changed inputs: the pass runs (step " + step + ")"); runs++; }
                lastKey = key;
                // between timer fires: raidWell does not recompute
                int r0 = G.round;
                G.round += R.nextInt(20);
                if (G.round - r0 < 20) {
                    MapLocation[] pw = Launcher.predWells;
                    Launcher.raidWell(hq, ehq);
                    check(Launcher.predWells == pw && Launcher.predRound == r0, "no pass before the 20-round timer");
                }
            }
        }
        check(skips > 8000 && runs > 5000 && cuts > 1000 && cutSkips > 300 && midCuts > 1000 && midSkips > 300 && raids > 3000
            && typeOnly > 1000 && sameContent > 1000 && reverts > 1000,
            "sequence: skips " + skips + ", runs " + runs + ", cuts " + cuts + " (" + cutSkips + " on a matching key), cut at the "
            + "first guard " + midCuts + " (skips after the budget ran out " + midSkips + "), raid answers " + raids
            + ", type-only rewrites " + typeOnly + ", same-content ehq " + sameContent + ", reverts " + reverts);
        System.out.println("bc2: sequence " + skips + " skips (" + midSkips + " after the budget ran out), " + runs + " passes, "
            + cuts + " calls under the guard (" + cutSkips + " on a matching key), " + midCuts + " passes cut at their first guard, "
            + raids + " raid answers");
    }

    /** The inputs a pass depends on, as the test sees them: s, ehq's coordinates, the slots' locations, the seen wells. */
    static String keyOf(int s, MapLocation[] ehq) {
        StringBuilder b = new StringBuilder().append(s).append('|');
        for (MapLocation l : ehq) b.append(l.x).append(',').append(l.y).append(';');
        b.append('|');
        for (int i = 0; i < nSlots; i++) b.append(shared[Comms.WELLS + i] & 0xfff).append(';');
        b.append('|');
        for (int i = 0; i < nSeenObjs; i++) b.append(seenObjs[i].x).append(',').append(seenObjs[i].y).append(';');
        return b.toString();
    }

    /** MapMem's seen-well list := seenObjs[0..nSeenObjs) (reflection: the list is private and append-only). */
    static void setSeen() {
        try {
            java.lang.reflect.Field a = MapMem.class.getDeclaredField("seenWell"), n = MapMem.class.getDeclaredField("nSeenWell");
            a.setAccessible(true); n.setAccessible(true);
            MapLocation[] arr = (MapLocation[]) a.get(null);
            java.util.Arrays.fill(arr, null);
            System.arraycopy(seenObjs, 0, arr, 0, nSeenObjs);
            n.setInt(null, nSeenObjs);
        } catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
    }

    /** Clock.getBytecodesLeft() := v (the engine's monitor field; nothing counts bytecodes outside a game). */
    static void setBudget(int v) {
        try {
            java.lang.reflect.Field f = Class.forName("battlecode.instrumenter.inject.RobotMonitor").getDeclaredField("bytecodesLeft");
            f.setAccessible(true);
            f.setInt(null, v);
            check(Clock.getBytecodesLeft() == v, "budget set");
        } catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
    }

    // ---------------------------------------------------------------- helpers
    static RobotController proxy() {
        return (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
            new Class<?>[]{RobotController.class}, (p, m, args) -> {
                switch (m.getName()) {
                    case "readSharedArray":
                        if ((Integer) args[0] == dropAt) { dropAt = -1; setBudget(4499); }   // the budget runs out here
                        return shared[(Integer) args[0]];
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
        if (!ok) { System.out.println("bc2 FAILED: " + what); System.exit(1); }
    }
}
