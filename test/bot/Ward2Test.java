package c_ward2;

import battlecode.common.*;
import battlecode.world.Inventory;

import java.lang.reflect.Proxy;
import java.util.Arrays;
import java.util.Random;

/** c_ward2 (c_ward1's spec on c_bc1): Launcher.homeOf (nearest HQ, ties to the first, no RNG), Launcher.wardTarget
 *  (2+ launchers, within r2 FORM_R2 of home, the fresh sighting nearest home within r2 WARD_R2; no RNG, no writes),
 *  Launcher.pickObjective against c_bc1's code (copied below as refPick: identical results and side effects whenever
 *  the ward does not trigger; the ward's target otherwise), Launcher.regroup's ward bypass (no hold, no follow, objEff
 *  7, formTurns untouched) and the lone launcher's unchanged hold, Comms.reportEnemyAt (honest stamp, never replaces a
 *  sighting at least as fresh) against a two-pass reference, and Carrier.reportThreat (REPORT_AGE, write access).
 *  A RobotController proxy serves the shared array, the island count and senseCloud; any other engine call fails the
 *  test. Exits non-zero on a failure. */
public class Ward2Test {
    static final Random R = new Random(20261011);
    static final int[] shared = new int[64];
    static int islands, writesSeen;
    static boolean writable;

    public static void main(String[] a) throws GameActionException {
        G.rc = proxy();
        G.us = Team.A; G.them = Team.B;
        G.W = 60; G.H = 60;
        G.type = RobotType.LAUNCHER;
        G.nearby = new RobotInfo[0];
        G.enemies = new RobotInfo[0];
        rng(987654321);
        homeOf();
        wardTarget();
        scenarios();
        pickDifferential();
        reportEnemyAt();
        reportThreat();
        System.out.println("ward2: " + checks + " cases ok");
    }

    // ---------------------------------------------------------------- Launcher.homeOf
    static void homeOf() {
        check(Launcher.homeOf(L(5, 5), null) == null, "homeOf: null list");
        check(Launcher.homeOf(L(5, 5), new MapLocation[0]) == null, "homeOf: empty list");
        MapLocation[] tie = {L(10, 10), L(0, 0), L(20, 20)};
        check(Launcher.homeOf(L(5, 5), tie) == tie[0], "homeOf: tie goes to the first");
        int ties = 0;
        for (int c = 0; c < 20000; c++) {
            MapLocation[] h = randomLocs(1 + R.nextInt(4), 60);
            MapLocation from = L(R.nextInt(60), R.nextInt(60));
            // half the cases: a second HQ at the reflection of the first through `from` (equidistant), in a random slot
            if (c % 2 == 0 && h.length > 1) {
                int x = 2 * from.x - h[0].x, y = 2 * from.y - h[0].y;
                if (x >= 0 && y >= 0 && x < 60 && y < 60) {
                    MapLocation t = L(x, y);
                    int j = 1 + R.nextInt(h.length - 1);
                    if (R.nextBoolean()) h[j] = t; else { h[j] = h[0]; h[0] = t; }
                }
            }
            int bd = Integer.MAX_VALUE, bi = -1, nAt = 0;
            for (int i = 0; i < h.length; i++) {
                int d = from.distanceSquaredTo(h[i]);
                if (d < bd) { bd = d; bi = i; nAt = 1; } else if (d == bd) nAt++;
            }
            if (nAt > 1) ties++;
            int seed = R.nextInt() | 1, prev = rng(seed);
            MapLocation got = Launcher.homeOf(from, h);
            check(rng(prev) == seed, "homeOf drew from the RNG");
            check(got == h[bi], "homeOf: nearest, first on ties (case " + c + ")");
        }
        check(ties > 200, "homeOf: the cases hit distance ties (" + ties + ")");
    }

    // ---------------------------------------------------------------- Launcher.wardTarget
    static void wardTarget() throws GameActionException {
        int fired = 0, lone = 0, far = 0, stale = 0, out = 0;
        for (int c = 0; c < 40000; c++) {
            randomState(c);
            MapLocation want = refWard();
            if (want != null) fired++;
            else if (G.nAllyFighters == 0) lone++;
            else if (G.here.distanceSquaredTo(Launcher.homeOf(G.here, HQState.ourHQs)) > C.FORM_R2) far++;
            else if (Comms.nearestEnemy(Launcher.homeOf(G.here, HQState.ourHQs), 1) == null) stale++;
            else out++;
            int seed = R.nextInt() | 1, prev = rng(seed), w0 = writesSeen;
            MapLocation got = Launcher.wardTarget();
            check(rng(prev) == seed, "wardTarget drew from the RNG");
            check(writesSeen == w0, "wardTarget wrote the shared array");
            check(want == null ? got == null : want.equals(got), "wardTarget: " + want + " got " + got + " (case " + c + ")");
        }
        check(fired > 1500 && lone > 1000 && far > 3000 && stale > 500 && out > 500,
            "wardTarget: every branch hit (fired " + fired + ", lone " + lone + ", far " + far + ", stale " + stale + ", beyond WARD_R2 " + out + ")");
    }

    /** The spec: 2+ of ours in vision, the launcher within r2 FORM_R2 of its nearest HQ (first on ties), a sighting at
     *  most 1 stamp old within r2 WARD_R2 of that HQ, the nearest to it (first slot on ties). */
    static MapLocation refWard() {
        if (G.nAllyFighters + 1 < C.WARD_MIN) return null;
        MapLocation[] h = HQState.ourHQs;
        if (h == null || h.length == 0) return null;
        MapLocation home = h[0];
        for (int i = 1; i < h.length; i++) if (G.here.distanceSquaredTo(h[i]) < G.here.distanceSquaredTo(home)) home = h[i];
        if (G.here.distanceSquaredTo(home) > C.FORM_R2) return null;
        int now = (G.round >> 4) & 15;
        MapLocation best = null;
        for (int i = Comms.ENEMY; i < Comms.ENEMY + Comms.NENEMY; i++) {
            int c = shared[i];
            if (c == 0 || ((now - (c >>> 12)) & 15) > 1) continue;
            MapLocation l = G.dec(c & 0xfff);
            if (best == null || home.distanceSquaredTo(l) < home.distanceSquaredTo(best)) best = l;
        }
        return best != null && home.distanceSquaredTo(best) <= C.WARD_R2 ? best : null;
    }

    /** Random HQs, a launcher near one of them, 0-5 allies, 0-4 sightings near the HQs with stamps 0-3 old. */
    static void randomState(int c) {
        Arrays.fill(shared, 0);
        G.round = 1 + R.nextInt(1999);
        int nh = 1 + R.nextInt(4);
        MapLocation[] h = randomLocs(nh, 60);
        HQState.ourHQs = h;
        for (int i = 0; i < nh; i++) shared[Comms.HQ_LOC + i] = G.enc(h[i]);
        MapLocation base = h[R.nextInt(nh)];
        G.here = L(clamp(base.x + R.nextInt(19) - 9), clamp(base.y + R.nextInt(19) - 9));
        G.nAllyFighters = c % 5 == 0 ? 0 : R.nextInt(6);
        int now = (G.round >> 4) & 15;
        for (int i = Comms.ENEMY; i < Comms.ENEMY + Comms.NENEMY; i++) {
            if (R.nextInt(3) == 0) continue;
            MapLocation hb = h[R.nextInt(nh)];
            MapLocation s = L(clamp(hb.x + R.nextInt(29) - 14), clamp(hb.y + R.nextInt(29) - 14));
            shared[i] = (((now - R.nextInt(4)) & 15) << 12) | G.enc(s);
        }
    }

    // ---------------------------------------------------------------- scenarios
    static void scenarios() throws GameActionException {
        MapMem.cand = 7; MapMem.nEnemyHQSeen = 0; Launcher.ehqC = null;
        islands = 0; Launcher.islandCount = -1;
        MapLocation hq = L(10, 10);
        Arrays.fill(shared, 0);
        HQState.ourHQs = new MapLocation[]{hq};
        shared[Comms.HQ_LOC] = G.enc(hq);
        G.round = 200;
        int now = (G.round >> 4) & 15;
        // the case the spec's order missed: forming at home (r2 8), the raid sighting within r2 64 of the launcher
        // (SIGHTING_R2) and r2 100 of the HQ: the SIGHTING path would hand it to regroup's forming hold
        G.here = L(12, 12);
        MapLocation raid = L(16, 18);                   // r2 52 from the launcher, 100 from the HQ
        shared[Comms.ENEMY] = (now << 12) | G.enc(raid);
        G.nAllyFighters = 1;
        G.allyLeader = new RobotInfo(1, Team.A, RobotType.LAUNCHER, new Inventory(), 200, L(13, 12));
        G.id = 50;
        MapLocation got = pick();
        check(raid.equals(got) && Launcher.ward && Launcher.objKind == 0 && !Launcher.recalled, "pair at home: ward on the raid");
        Launcher.objective = got;
        Launcher.formTurns = 7;
        Launcher.objEff = -1;
        check(!Launcher.regroup() && Launcher.objEff == 7 && Launcher.formTurns == 7, "pair at home: no hold, objEff 7, formTurns kept");
        // a formed group with a far leader of lower id: the ward goes without following (c_bc1 would follow)
        G.nAllyFighters = 5;
        G.allyLeader = new RobotInfo(1, Team.A, RobotType.LAUNCHER, new Inventory(), 200, L(5, 5));
        got = pick();
        Launcher.objective = got;
        check(Launcher.ward && !Launcher.regroup() && Launcher.mode != 6, "group at home: ward, no follow");
        // alone: c_bc1's rules (SIGHTING path, then the forming hold since r2 100 > HOME_DEFENCE_R2)
        G.nAllyFighters = 0;
        G.allyLeader = null;
        got = pick();
        check(raid.equals(got) && !Launcher.ward && Launcher.objKind == 0, "alone at home: SIGHTING path, no ward");
        Launcher.objective = got;
        Launcher.formTurns = 0;
        check(Launcher.regroup() && Launcher.mode == 5 && Launcher.formTurns == 1, "alone at home: the forming hold");
        // the sighting 2 stamps old: no ward (maxAge 1), still a SIGHTING_R2 objective (maxAge 2)
        G.nAllyFighters = 1;
        shared[Comms.ENEMY] = (((now - 2) & 15) << 12) | G.enc(raid);
        got = pick();
        check(raid.equals(got) && !Launcher.ward, "stale sighting: no ward, the SIGHTING path");
        // beyond WARD_R2 of the HQ (r2 145): no ward
        MapLocation far = L(22, 11);                    // r2 145 from the HQ, 101 from the launcher
        shared[Comms.ENEMY] = (now << 12) | G.enc(far);
        got = pick();
        check(!Launcher.ward && Launcher.objKind != 0, "beyond WARD_R2 and SIGHTING_R2: no ward, no sighting objective");
        MapLocation edge = L(22, 10);                   // r2 144: a ward
        shared[Comms.ENEMY] = (now << 12) | G.enc(edge);
        got = pick();
        check(edge.equals(got) && Launcher.ward, "at WARD_R2: ward");
        // outside the forming area (r2 61 from the HQ): no ward, the SIGHTING path (r2 9 from the launcher)
        G.here = L(16, 15);
        shared[Comms.ENEMY] = (now << 12) | G.enc(raid);
        got = pick();
        check(raid.equals(got) && !Launcher.ward, "outside FORM_R2: no ward");
        // two sightings: the ward takes the one nearest home, the SIGHTING path the one nearest the launcher
        G.here = L(14, 10);                             // r2 16 from the HQ
        MapLocation nearMe = L(19, 10), nearHome = L(5, 14);   // r2 25 / 97 from me; r2 81 / 41 from the HQ
        shared[Comms.ENEMY] = (now << 12) | G.enc(nearMe);
        shared[Comms.ENEMY + 1] = (now << 12) | G.enc(nearHome);
        got = pick();
        check(nearHome.equals(got) && Launcher.ward, "two sightings: the ward takes the one nearest home");
        G.nAllyFighters = 0;
        got = pick();
        check(nearMe.equals(got) && !Launcher.ward, "two sightings alone: the one nearest the launcher");
        G.allyLeader = null;
    }

    static MapLocation pick() throws GameActionException {
        Launcher.predRound = G.round;                   // no prediction pass (it needs a live Clock)
        int seed = R.nextInt() | 1, prev = rng(seed), w0 = writesSeen;
        MapLocation got = Launcher.pickObjective();
        check(rng(prev) == seed, "pickObjective drew from the RNG");
        check(writesSeen == w0, "pickObjective wrote the shared array");
        return got;
    }

    // ---------------------------------------------------------------- pickObjective vs c_bc1
    static void pickDifferential() throws GameActionException {
        int wards = 0, same = 0, alarms = 0, isl = 0;
        for (int c = 0; c < 20000; c++) {
            randomState(c);
            MapMem.cand = 1 + R.nextInt(7);
            MapMem.nEnemyHQSeen = 0;
            if (R.nextInt(4) == 0) shared[Comms.ALARM] = R.nextInt(1 << 16);
            if (G.round < C.RECALL_UNTIL && shared[Comms.ALARM] != 0) alarms++;
            islands = R.nextInt(3) == 0 ? 0 : 1 + R.nextInt(35);
            Launcher.islandCount = -1;
            for (int id = 1; id < 40; id++) {
                MapMem.islandOwner[id] = R.nextInt(3);
                MapMem.islandSeen[id] = R.nextInt(3) == 0 ? 0 : Math.max(1, G.round - R.nextInt(25));
                MapMem.islandTile[id] = R.nextInt(5) == 0 ? null : L(R.nextInt(60), R.nextInt(60));
                if (id <= 35 && R.nextInt(10) < 3) shared[Comms.ISLANDS + id] = (R.nextInt(3) << 12) | G.enc(L(R.nextInt(60), R.nextInt(60)));
            }
            MapLocation ward = refWard();
            Launcher.predRound = G.round;
            Object[] want = refPick();
            if (ward == null && want[1].equals(1)) isl++;
            Launcher.islandCount = -1;
            MapLocation got = pick();
            Object[] have = snap(got);
            if (ward != null) {
                wards++;
                check(ward.equals(got) && Launcher.ward && Launcher.objKind == 0 && !Launcher.recalled && Launcher.objIsland == 0
                    && Launcher.objHQ == null && Launcher.objRaid == null && Launcher.objRing == null, "pick: the ward target (case " + c + ")");
            } else {
                same++;
                check(!Launcher.ward, "pick: no ward flag without a ward target");
                check(Arrays.equals(want, have), "pick: c_bc1's result without a ward (case " + c + "): " + Arrays.toString(want) + " got " + Arrays.toString(have));
            }
        }
        check(wards > 500 && same > 10000 && alarms > 500 && isl > 500,
            "pick: wards " + wards + ", c_bc1 paths " + same + ", alarms " + alarms + ", island objectives " + isl);
        MapMem.cand = 7;
        Launcher.ehqC = null;
    }

    static Object[] snap(MapLocation got) {
        return new Object[]{got, Launcher.objKind, Launcher.recalled, Launcher.objIsland, Launcher.objHQ, Launcher.objRaid, Launcher.objRing};
    }

    /** c_bc1's Launcher.pickObjective (src/c_bc1/Launcher.java), its results and side effects as snap() lists them. */
    static Object[] refPick() throws GameActionException {
        Launcher.recalled = false;
        Launcher.objIsland = 0;
        Launcher.objHQ = null;
        Launcher.objRaid = null;
        Launcher.objRing = null;
        MapLocation e = Comms.nearestEnemy(G.here, 2);
        if (e != null && G.here.distanceSquaredTo(e) <= C.SIGHTING_R2) { Launcher.objKind = 0; return snap(e); }
        if (C.RECALL && G.round < C.RECALL_UNTIL && Comms.read(Comms.ALARM) != 0) {
            MapLocation best = null;
            int bd = Integer.MAX_VALUE, td = -1;
            for (int i = 0; i < 4; i++) {
                int v = Comms.read(Comms.HQ_LOC + i);
                if (v == 0 || Comms.alarm(i) < C.RAID_ALARM) continue;
                MapLocation h = G.dec(v);
                int d = G.here.distanceSquaredTo(h);
                if (d > C.RECALL_R2) continue;
                if (td < 0) {
                    MapLocation[] ehq = Launcher.enemyHQs();
                    td = ehq.length > 0 ? G.here.distanceSquaredTo(Launcher.siegeTarget(ehq)) : Integer.MAX_VALUE;
                }
                if (d >= td) continue;
                if (d < bd) { bd = d; best = h; }
            }
            if (best != null) { Launcher.objKind = 0; Launcher.recalled = true; return snap(best); }
        }
        if (G.round >= C.ISLAND_HUNT_START) {
            if (Launcher.islandCount < 0) Launcher.islandCount = Math.min(35, G.rc.getIslandCount());
            RobotController rc = G.rc;
            int[] own = MapMem.islandOwner, seen = MapMem.islandSeen;
            MapLocation best = null;
            int bd = Integer.MAX_VALUE;
            for (int id = Launcher.islandCount; id > 0; id--) {
                int sh = rc.readSharedArray(Comms.ISLANDS + id);
                if (sh < 0x2000 && own[id] != 2) continue;
                int owner = seen[id] > 0 && (G.round - seen[id] <= 10 || sh == 0) ? own[id] : sh >>> 12;
                if (owner != 2) continue;
                MapLocation t = Comms.islandTile(id);
                if (t == null) t = MapMem.islandTile[id];
                if (t == null) continue;
                int d = G.here.distanceSquaredTo(t);
                if (d <= bd) { bd = d; best = t; Launcher.objIsland = id; }
            }
            if (best != null) { Launcher.objKind = 1; return snap(best); }
        }
        MapLocation[] ehq = Launcher.enemyHQs();
        if (ehq.length > 0) {
            MapLocation hq = Launcher.siegeTarget(ehq);
            Launcher.objKind = 2;
            Launcher.objHQ = hq;
            if (MapMem.decided()) {
                MapLocation w = Launcher.raidWell(hq, ehq);
                if (w != null) { Launcher.objRaid = w; return snap(w); }
            }
            Launcher.objRing = hq;
            return snap(hq);
        }
        Launcher.objKind = 3;
        return snap(new MapLocation(G.W / 2, G.H / 2));
    }

    // ---------------------------------------------------------------- Comms.reportEnemyAt
    static void reportEnemyAt() throws GameActionException {
        int[] kinds = new int[4];   // written: same cluster, empty, evicted; skipped
        for (int c = 0; c < 60000; c++) {
            Arrays.fill(shared, 0);
            G.round = c % 9 == 0 ? 240 + R.nextInt(40) : R.nextInt(2000);   // also across the 4-bit stamp wrap
            int now = (G.round >> 4) & 15;
            MapLocation l = L(R.nextInt(60), R.nextInt(60));
            for (int i = Comms.ENEMY; i < Comms.ENEMY + Comms.NENEMY; i++) {
                if (R.nextInt(4) == 0) continue;
                MapLocation s = R.nextInt(3) == 0 ? L(clamp(l.x + R.nextInt(9) - 4), clamp(l.y + R.nextInt(9) - 4)) : L(R.nextInt(60), R.nextInt(60));
                shared[i] = (((now - R.nextInt(5)) & 15) << 12) | G.enc(s);
            }
            int seen = Math.max(0, G.round - R.nextInt(C.REPORT_AGE + 1));
            int[] before = shared.clone();
            int want = refReportAt(before, l, seen);
            Comms.canWrite = true;
            writable = true;
            int w0 = writesSeen;
            int got = Comms.reportEnemyAt(l, seen);
            check(got == want, "reportEnemyAt: slot " + want + " got " + got + " (case " + c + ")");
            int[] after = before.clone();
            if (want >= 0) after[want] = (((seen >> 4) & 15) << 12) | G.enc(l);
            check(Arrays.equals(after, shared) && writesSeen - w0 == (want >= 0 ? 1 : 0), "reportEnemyAt: exactly the one slot written");
            if (want >= 0) {
                int age = (now - (shared[want] >>> 12)) & 15;
                check(age == ((now - ((seen >> 4) & 15)) & 15) && age <= 2, "reportEnemyAt: honest stamp, at most 2 old");
                kinds[clusterOf(before, l) >= 0 ? 0 : before[want] == 0 ? 1 : 2]++;
            } else kinds[3]++;
            // no write access: nothing written, -1
            System.arraycopy(before, 0, shared, 0, 64);
            Comms.canWrite = false;
            check(Comms.reportEnemyAt(l, seen) == -1 && Arrays.equals(before, shared), "reportEnemyAt: no write without canWrite");
            // access lost since startTurn (the robot moved): the put is refused, -1, canWrite cleared
            Comms.canWrite = true;
            writable = false;
            check(Comms.reportEnemyAt(l, seen) == -1 && Arrays.equals(before, shared) && (want < 0 || !Comms.canWrite),
                "reportEnemyAt: a refused put writes nothing");
            writable = true;
        }
        check(kinds[0] > 3000 && kinds[1] > 3000 && kinds[2] > 1000 && kinds[3] > 1000,
            "reportEnemyAt: every branch hit " + Arrays.toString(kinds));
        Comms.canWrite = false;
    }

    /** The first non-empty slot of l's cluster (r2 20), or -1. */
    static int clusterOf(int[] sh, MapLocation l) {
        for (int i = Comms.ENEMY; i < Comms.ENEMY + Comms.NENEMY; i++)
            if (sh[i] != 0 && G.dec(sh[i] & 0xfff).distanceSquaredTo(l) <= 20) return i;
        return -1;
    }

    /** Two passes: the cluster slot when older than the report; else the first empty slot; else the oldest (first of
     *  equals) when older than the report. */
    static int refReportAt(int[] sh, MapLocation l, int seen) {
        int now = (G.round >> 4) & 15, mine = (now - ((seen >> 4) & 15)) & 15;
        int k = clusterOf(sh, l);
        if (k >= 0) return ((now - (sh[k] >>> 12)) & 15) > mine ? k : -1;
        for (int i = Comms.ENEMY; i < Comms.ENEMY + Comms.NENEMY; i++) if (sh[i] == 0) return i;
        int oldest = -1, oa = -1;
        for (int i = Comms.ENEMY; i < Comms.ENEMY + Comms.NENEMY; i++) {
            int age = (now - (sh[i] >>> 12)) & 15;
            if (age > oa) { oa = age; oldest = i; }
        }
        return oa > mine ? oldest : -1;
    }

    // ---------------------------------------------------------------- Carrier.reportThreat
    static void reportThreat() throws GameActionException {
        MapLocation t = L(30, 30);
        for (int age = 0; age <= C.REPORT_AGE + 3; age++) {
            for (int w = 0; w < 2; w++) {
                Arrays.fill(shared, 0);
                G.round = 500 + age;
                Carrier.threatLoc = t;
                Carrier.threatRound = 500;
                Comms.canWrite = w == 1;
                writable = true;
                Carrier.reportThreat();
                if (age > C.REPORT_AGE) check(Carrier.threatLoc == null && shared[Comms.ENEMY] == 0, "reportThreat: dropped past REPORT_AGE (" + age + ")");
                else if (w == 0) check(Carrier.threatLoc == t && shared[Comms.ENEMY] == 0, "reportThreat: kept until it can write (" + age + ")");
                else check(Carrier.threatLoc == null && shared[Comms.ENEMY] == ((((500 >> 4) & 15) << 12) | G.enc(t)),
                    "reportThreat: written with the sighting's stamp (" + age + ")");
            }
        }
        Comms.canWrite = false;
    }

    // ---------------------------------------------------------------- harness
    static RobotController proxy() {
        return (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
            new Class<?>[]{RobotController.class}, (p, m, args) -> {
                switch (m.getName()) {
                    case "readSharedArray": return shared[(Integer) args[0]];
                    case "canWriteSharedArray": return writable;
                    case "writeSharedArray":
                        if (!writable) throw new IllegalStateException("write without access");
                        shared[(Integer) args[0]] = (Integer) args[1];
                        writesSeen++;
                        return null;
                    case "getIslandCount": return islands;
                    case "senseCloud": return false;
                    default: break;
                }
                throw new UnsupportedOperationException("engine call outside the test's proxy: " + m.getName());
            });
    }

    static MapLocation[] randomLocs(int n, int w) {
        MapLocation[] o = new MapLocation[n];
        for (int i = 0; i < n; i++) o[i] = L(R.nextInt(w), R.nextInt(w));
        return o;
    }

    static int clamp(int v) { return Math.max(0, Math.min(59, v)); }

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
        if (!ok) { System.out.println("ward2 FAILED: " + what); System.exit(1); }
    }
}
