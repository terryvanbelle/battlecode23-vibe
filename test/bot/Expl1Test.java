package c_expl1;

import battlecode.common.*;

import java.lang.reflect.Proxy;
import java.util.Random;

/** c_expl1 (c_keep2 + C.EXPL): the frontier explorer's helpers (Carrier.gridX/gridY/cell, coveredCode, fanSlot/fanNext,
 *  explAnchor, explPen, explCovered, mirrorPick), the pass explScan and the neighbour pick explNear (hand cases, then
 *  seeded random boards against plain reference versions: pick, score and done marks), and explInit / explFrontier
 *  (the goal while a pass is unfinished, stale bests, the rescored incumbent, short and long gaps, detours) through a
 *  RobotController proxy that serves the shared array, the island count, sensing of the target and isMovementReady
 *  (false: moveTwice does nothing), so the claim, the pick, the drop rules, the episode reset and the fallbacks run as
 *  in a game. Clock.getBytecodesLeft() is the engine monitor's field, set by reflection (Bc3Test's setBudget). Exits
 *  non-zero on a failure. */
public class Expl1Test {
    static final Random R = new Random(20261017);
    static final int BIG = 12000;
    static final int[] shared = new int[64];
    static int islands = 10, writes;
    static boolean occupied, sensable = true;

    public static void main(String[] a) {
        G.rc = proxy();
        G.us = Team.A; G.them = Team.B;
        setBudget(BIG);
        arm();
        grid();
        codes();
        fan();
        anchors();
        pen();
        covered();
        scanCases();
        scanRandom();
        mirror();
        try { initClaims(); } catch (GameActionException e) { throw new RuntimeException(e); }
        frontier();
        try { nearCases(); } catch (GameActionException e) { throw new RuntimeException(e); }
        nearRandom();
        System.out.println("expl1 frontier explorer: " + checks + " cases ok");
    }

    // ---------------------------------------------------------------- 1-2 arm and direction order
    static void arm() {
        check(C.EXPL && !C.EXPL_MIRROR && C.EXPL_STEP == 5 && C.EXPL_GUARD >= 4000, "arm: EXPL on, mirror off, step 5, guard");
        check(C.EXPL_FAN.length == 8, "fan has 8 slots");
        boolean[] seen = new boolean[8];
        for (int f : C.EXPL_FAN) { int o = ((f % 8) + 8) % 8; check(!seen[o], "fan offsets distinct mod 8: " + f); seen[o] = true; }
        check(C.EXPL_FAN[0] == 0, "slot 0 keeps the centre bearing (c_keep2's centre leg)");
        for (int i = 0; i < 8; i++) check(G.DIRS[i].ordinal() == i, "G.DIRS[" + i + "].ordinal()");
        check(Comms.FAN == Comms.ISLANDS + 35 && Comms.FAN < Comms.ALARM, "FAN is island 35's slot, below ALARM");
    }

    // ---------------------------------------------------------------- 3-4 grid
    static void grid() {
        check(Carrier.gridX(0, 8, 40) == 2 && Carrier.gridX(7, 8, 40) == 37 && Carrier.gridY(40, 8, 30) == 27, "40x30 points");
        check(Carrier.cell(37, 27, 8) == 47 && Carrier.cell(0, 0, 8) == 0 && Carrier.cell(39, 29, 8) == 47, "40x30 cells");
        check(Carrier.gridX(4, 5, 21) == 20 && Carrier.gridY(20, 5, 21) == 20, "21x21: last row and column clamped");
        int k = Carrier.cell(20, 20, 5);
        check(k == 24 && Carrier.gridX(k, 5, 21) == 20 && Carrier.gridY(k, 5, 21) == 20, "21x21: standing on a clamped point is detected");
        // every size: every point lies in its own cell, every tile's cell is in range, points distinct
        for (int W = 20; W <= 60; W++) for (int H = 20; H <= 60; H += 7) {
            int nx = (W + 4) / 5, n = nx * ((H + 4) / 5);
            boolean[] hit = new boolean[W * H];
            for (int q = 0; q < n; q++) {
                int x = Carrier.gridX(q, nx, W), y = Carrier.gridY(q, nx, H);
                check(x >= 0 && x < W && y >= 0 && y < H, "point on the map " + W + "x" + H + " k" + q);
                check(Carrier.cell(x, y, nx) == q, "point in its own cell " + W + "x" + H + " k" + q);
                check(!hit[x + y * W], "points distinct");
                hit[x + y * W] = true;
            }
            check(Carrier.cell(W - 1, H - 1, nx) == n - 1 && Carrier.cell(0, 0, nx) == 0, "cells in range " + W + "x" + H);
        }
    }

    // ---------------------------------------------------------------- 5 tile codes
    static void codes() {
        check(Carrier.coveredCode(1) && Carrier.coveredCode(3) && Carrier.coveredCode(1 | (5 << 3)), "known open, wall, current: covered");
        check(Carrier.coveredCode(1 | (2 << 7)), "known open with a mana well: covered");
        check(!Carrier.coveredCode(5) && !Carrier.coveredCode(0) && !Carrier.coveredCode(2 << 7), "cloud, unknown, well bits only: not");
        check(!Carrier.coveredCode(5 | (2 << 7)), "known cloud with a well: not covered");
    }

    // ---------------------------------------------------------------- 6 fan claims
    static void fan() {
        check(Carrier.fanSlot(0, 2) == 0, "fresh slot 0");
        int v = Carrier.fanNext(0, 2);
        check(Carrier.fanSlot(v, 2) == 1 && Carrier.fanSlot(v, 0) == 0, "HQ 2 advanced, HQ 0 kept");
        check(Carrier.fanSlot(Carrier.fanNext(7 << 3, 1), 1) == 0, "wrap 7 -> 0");
        int[] cnt = new int[4];
        v = 0;
        for (int t = 0; t < 200; t++) {
            int i = R.nextInt(4);
            check(Carrier.fanSlot(v, i) == (cnt[i] & 7), "slot = claims mod 8");
            v = Carrier.fanNext(v, i);
            cnt[i]++;
            check(v >= 0 && v < (1 << 12), "value below 1 << 12");
            for (int j = 0; j < 4; j++) check(Carrier.fanSlot(v, j) == (cnt[j] & 7), "HQs independent");
        }
    }

    // ---------------------------------------------------------------- 7 anchors
    static void anchors() {
        MapLocation h = L(7, 4);
        check(Carrier.explAnchor(h, 0, 40, 30).equals(L(19, 16)), "SoundWave slot 0 NE " + Carrier.explAnchor(h, 0, 40, 30));
        check(Carrier.explAnchor(h, 1, 40, 30).equals(L(19, 4)), "slot 1 E");
        check(Carrier.explAnchor(h, 2, 40, 30).equals(L(7, 16)), "slot 2 N");
        check(Carrier.explAnchor(h, 7, 40, 30).equals(L(0, 0)), "slot 7 SW clamped");
        h = L(4, 6);
        check(Carrier.explAnchor(h, 0, 40, 40).equals(L(16, 18)), "Turtle slot 0 NE");
        check(Carrier.explAnchor(h, 1, 40, 40).equals(L(16, 6)), "slot 1 E");
        check(Carrier.explAnchor(h, 2, 40, 40).equals(L(4, 18)), "slot 2 N");
        check(Carrier.explAnchor(h, 3, 40, 40).equals(L(16, 0)), "slot 3 SE clamped");
        check(Carrier.explAnchor(h, 8, 40, 40).equals(L(16, 18)), "slot 8 = slot 0 (index masked)");
        check(Carrier.explAnchor(L(10, 10), 0, 20, 20).equals(L(10, 19)), "centre HQ: CENTER bearing -> N, clamped");
        for (int t = 0; t < 2000; t++) {                       // always on the map
            int W = 20 + R.nextInt(41), H = 20 + R.nextInt(41);
            MapLocation p = Carrier.explAnchor(L(R.nextInt(W), R.nextInt(H)), R.nextInt(64), W, H);
            check(p.x >= 0 && p.x < W && p.y >= 0 && p.y < H, "anchor on the map");
        }
    }

    // ---------------------------------------------------------------- 8 penalty
    static void pen() {
        MapLocation[] ours = {L(7, 4), L(24, 11)}, ehq = {L(7, 25), L(24, 18)};
        check(Carrier.explPen(27, 17, ours, ehq) == 9, "(27,17): 3 x (6 - 3)");
        check(Carrier.explPen(22, 22, ours, ehq) == 21, "(22,22): 3 x (11 - 4)");
        check(Carrier.explPen(16, 2, ours, ehq) == 0, "(16,2): our side");
        check(Carrier.explPen(27, 17, ours, new MapLocation[0]) == 0 && Carrier.explPen(27, 17, ours, null) == 0, "no enemy HQ: 0");
        check(Carrier.explPen(27, 17, ours, new MapLocation[]{null, L(24, 18)}) == 9, "null entry skipped");
        check(Carrier.explPen(27, 17, new MapLocation[]{null, L(24, 11)}, ehq) == 9, "null HQ of ours skipped");
    }

    // ---------------------------------------------------------------- explCovered
    static void covered() {
        G.W = 20; G.H = 20;
        MapMem.tile = null;
        check(!Carrier.explCovered(5, 5), "no tile[]: not covered");
        MapMem.tile = new char[400];
        MapMem.cand = 7;
        set(5, 5, 1);
        check(Carrier.explCovered(5, 5) && !Carrier.explCovered(14, 5), "own tile; undecided: no image");
        MapMem.cand = 2;                                        // FLIP_X: (5,5) <-> (14,5)
        check(Carrier.explCovered(14, 5), "FLIP_X image covered");
        MapMem.cand = 4;
        check(!Carrier.explCovered(14, 5) && Carrier.explCovered(5, 14), "FLIP_Y image");
        MapMem.cand = 1;
        check(Carrier.explCovered(14, 14), "ROT image");
        set(5, 5, 5);
        check(!Carrier.explCovered(14, 14) && !Carrier.explCovered(5, 5), "a cloud image covers nothing");
        MapMem.cand = 7;
    }

    // ---------------------------------------------------------------- 9 explScan, 20x20 hand cases
    static void scanCases() {
        G.W = 20; G.H = 20;
        // (a) spec setup: here (16,2), anchor (4,14), nothing known. (12,7) and (7,12) both score 13 (the least, as
        // cheb(here, anchor) = 12 is reached by no point); the downward pass keeps the first: (7,12), k 9
        scanSetup(L(16, 2), L(4, 14), 7);
        Carrier.explScan();
        check(Carrier.xK == 0 && Carrier.xBestS == 13 && Carrier.xBestK == Carrier.cell(7, 12, 4), "(a) tie at 13 -> (7,12): k" + Carrier.xBestK + " s" + Carrier.xBestS);
        // (a2) anchor = here: nearest first, (17,2) strictly (score 2)
        scanSetup(L(16, 2), L(16, 2), 7);
        Carrier.explScan();
        check(Carrier.xK == 0 && Carrier.xBestK == Carrier.cell(17, 2, 4) && Carrier.xBestS == 2, "(a2) nearest (17,2)");
        // (b) (17,2) known open: done on the way, the next nearest (12,2) (score 8) strictly
        set(17, 2, 1);
        restart();
        Carrier.explScan();
        check(Carrier.xDone[Carrier.cell(17, 2, 4)] && Carrier.xBestK == Carrier.cell(12, 2, 4) && Carrier.xBestS == 8, "(b) covered point done, next chosen");
        // (c) (12,2) a known cloud: not done, still the target (cloud points must be stood on)
        set(12, 2, 5);
        restart();
        Carrier.explScan();
        check(!Carrier.xDone[Carrier.cell(12, 2, 4)] && Carrier.xBestK == Carrier.cell(12, 2, 4), "(c) cloud point stays a frontier point");
        // (d) FLIP_X with (2,7), the image of (17,7), known open: (17,7) is done once it is a candidate best
        scanSetup(L(17, 7), L(17, 7), 2);
        set(2, 7, 1);
        Carrier.explScan();
        check(Carrier.xDone[Carrier.cell(17, 7, 4)] && Carrier.xDone[Carrier.cell(2, 7, 4)], "(d) mirror-covered and own-covered done");
        check(Carrier.xBestK == Carrier.cell(17, 12, 4) && Carrier.xBestS == 10, "(d) next best (17,12) at 10: k" + Carrier.xBestK);
        scanSetup(L(17, 7), L(17, 7), 7);                      // undecided: no mirror, (17,7) itself (score 0)
        set(2, 7, 1);
        Carrier.explScan();
        check(!Carrier.xDone[Carrier.cell(17, 7, 4)] && Carrier.xBestK == Carrier.cell(17, 7, 4) && Carrier.xBestS == 0, "(d) undecided: no image rule");
        // (e) at the guard the pass does nothing and resumes later
        scanSetup(L(16, 2), L(4, 14), 7);
        setBudget(C.EXPL_GUARD);
        Carrier.explScan();
        check(Carrier.xK == 16 && Carrier.xBestK == -1 && Carrier.xBestS == Integer.MAX_VALUE, "(e) no work at the guard");
        setBudget(C.EXPL_GUARD + 1);
        Carrier.explScan();
        check(Carrier.xK == 0 && Carrier.xBestK == Carrier.cell(7, 12, 4), "(e) resumed above the guard: as (a)");
        setBudget(BIG);
        // (f) penalty on: ours (16,2), enemy (3,17): (7,12) (enemy side by 5: +15) loses to (12,7) at 13
        scanSetup(L(16, 2), L(4, 14), 7);
        Carrier.xPenOn = true;
        HQState.ourHQs = new MapLocation[]{L(16, 2)};
        Carrier.xEhq = new MapLocation[]{L(3, 17)};
        Carrier.explScan();
        check(Carrier.xBestK == Carrier.cell(12, 7, 4) && Carrier.xBestS == 13, "(f) our-side point wins the tie: k" + Carrier.xBestK);
        check(Carrier.xPen[Carrier.cell(7, 12, 4)] == 16 && Carrier.xPen[Carrier.cell(12, 7, 4)] == 1, "(f) penalties cached (1 + pen)");
        Carrier.xPenOn = false;
        // all points done: no best
        scanSetup(L(16, 2), L(4, 14), 7);
        for (int k = 0; k < 16; k++) Carrier.xDone[k] = true;
        Carrier.explScan();
        check(Carrier.xK == 0 && Carrier.xBestK == -1, "exhausted grid: no best");
    }

    static void scanSetup(MapLocation here, MapLocation anchor, int cand) {
        MapMem.tile = new char[G.W * G.H];
        MapMem.cand = cand;
        Carrier.xNx = (G.W + 4) / 5;
        Carrier.xN = Carrier.xNx * ((G.H + 4) / 5);
        Carrier.xDone = new boolean[Carrier.xN];
        Carrier.xPen = new int[Carrier.xN];
        Carrier.xPenOn = false;
        G.here = here;
        Carrier.xAnchor = anchor;
        restart();
    }

    static void restart() { Carrier.xK = Carrier.xN; Carrier.xBestK = -1; Carrier.xBestS = Integer.MAX_VALUE; }

    static void set(int x, int y, int c) { MapMem.tile[x + y * G.W] = (char) c; }

    // ---------------------------------------------------------------- explScan vs a plain reference pass
    static void scanRandom() {
        int[] cands = {1, 2, 4, 3, 5, 6, 7};
        int picks = 0, none = 0, mirrored = 0, penal = 0;
        for (int t = 0; t < 4000; t++) {
            G.W = 20 + R.nextInt(41); G.H = 20 + R.nextInt(41);
            int cand = cands[R.nextInt(cands.length)];
            scanSetup(L(R.nextInt(G.W), R.nextInt(G.H)), L(R.nextInt(G.W), R.nextInt(G.H)), cand);
            double pk = R.nextDouble();                       // share of known tiles
            for (int i = 0; i < G.W * G.H; i++) {
                if (R.nextDouble() >= pk) continue;
                int r = R.nextInt(10);
                MapMem.tile[i] = (char) (r < 6 ? 1 : r < 8 ? 3 : r < 9 ? 5 : 1 | (3 << 3) | (2 << 7));
            }
            for (int k = 0; k < Carrier.xN; k++) if (R.nextInt(6) == 0) Carrier.xDone[k] = true;
            boolean penOn = R.nextBoolean();
            MapLocation[] ours = randomLocs(1 + R.nextInt(4)), ehq = R.nextInt(8) == 0 ? new MapLocation[0] : randomLocs(1 + R.nextInt(6));
            if (ehq.length > 0 && R.nextInt(5) == 0) ehq[0] = null;
            Carrier.xPenOn = penOn;
            HQState.ourHQs = ours;
            Carrier.xEhq = ehq;
            boolean[] refDone = Carrier.xDone.clone();
            int[] ref = refScan(refDone, G.here, Carrier.xAnchor, penOn, ours, ehq, cand);
            Carrier.explScan();
            check(Carrier.xK == 0, "complete pass");
            check(Carrier.xBestK == ref[0] && (ref[0] < 0 || Carrier.xBestS == ref[1]), "best = reference: k" + Carrier.xBestK + "/" + ref[0] + " s" + Carrier.xBestS + "/" + ref[1]);
            for (int k = 0; k < Carrier.xN; k++) check(Carrier.xDone[k] == refDone[k], "done marks = reference at k" + k);
            if (ref[0] >= 0) picks++; else none++;
            if (ref[2] > 0) mirrored++;
            if (penOn && ref[3] > 0) penal++;
            if (ref[0] >= 0) {                                 // the pick is not done, not covered, and no other point scores less
                check(!refDone[ref[0]] && !Carrier.explCovered(Carrier.explX(ref[0]), Carrier.explY(ref[0])), "pick is a frontier point");
            }
        }
        check(picks > 1000 && none > 0 && mirrored > 100 && penal > 100, "random coverage: picks " + picks + " none " + none + " mirrored " + mirrored + " penal " + penal);
    }

    /** The pass written plainly: [best k (-1 none), best score, mirror marks, penalised picks]; marks done as explScan. */
    static int[] refScan(boolean[] done, MapLocation here, MapLocation anchor, boolean pen, MapLocation[] ours, MapLocation[] ehq, int cand) {
        int nx = (G.W + 4) / 5, n = nx * ((G.H + 4) / 5), bk = -1, bs = Integer.MAX_VALUE, mir = 0, penal = 0;
        boolean single = cand == 1 || cand == 2 || cand == 4;
        for (int k = n - 1; k >= 0; k--) {
            if (done[k]) continue;
            MapLocation p = L(Math.min(G.W - 1, (k % nx) * 5 + 2), Math.min(G.H - 1, (k / nx) * 5 + 2));
            int c = MapMem.tile[p.x + p.y * G.W];
            if ((c & 1) != 0 && (c & 4) == 0) { done[k] = true; continue; }
            int s = G.cheb(here, p) + G.cheb(p, anchor), pe = pen ? Carrier.explPen(p.x, p.y, ours, ehq) : 0;
            if (s + pe >= bs) continue;
            if (single) {
                MapLocation im = MapMem.img(cand, p);
                int ic = MapMem.tile[im.x + im.y * G.W];
                if ((ic & 1) != 0 && (ic & 4) == 0) { done[k] = true; mir++; continue; }
            }
            bs = s + pe; bk = k;
            if (pe > 0) penal++;
        }
        return new int[]{bk, bs, mir, penal};
    }

    // ---------------------------------------------------------------- 10 mirror pick
    static void mirror() {
        G.W = 40; G.H = 40;
        MapLocation h = L(4, 6);
        check(L(1, 18).equals(Carrier.mirrorPick(h, L(38, 18), 2)), "Turtle: (38,18) -> image (1,18)");
        check(Carrier.mirrorPick(h, L(16, 18), 2) == null, "(16,18): image (23,18) not nearer");
        check(Carrier.mirrorPick(h, L(38, 18), 3) == null && Carrier.mirrorPick(null, L(38, 18), 2) == null
            && Carrier.mirrorPick(h, null, 2) == null, "undecided symmetry or nulls: none");
        // margin edge: (30,26) -> (9,26): cheb 20 + 6 == 26 accepted; (30,27) -> (9,27): 21 + 6 > 26 refused
        check(G.cheb(h, L(9, 26)) + C.EXPL_MIRROR_MARGIN == G.cheb(h, L(30, 26)) && L(9, 26).equals(Carrier.mirrorPick(h, L(30, 26), 2)), "margin edge accepted");
        check(Carrier.mirrorPick(h, L(30, 27), 2) == null, "one short of the margin refused");
        check(L(35, 33).equals(Carrier.mirrorPick(L(36, 34), L(4, 6), 1)), "ROT image");
    }

    // ---------------------------------------------------------------- explInit: the per-HQ fan claim
    static void initClaims() throws GameActionException {
        G.W = 40; G.H = 30;
        java.util.Arrays.fill(shared, 0);
        MapLocation hq0 = L(7, 4), hq1 = L(32, 25);
        shared[Comms.HQ_LOC] = G.enc(hq0);
        shared[Comms.HQ_LOC + 1] = G.enc(hq1);
        HQState.ourHQs = new MapLocation[]{hq0, hq1};
        Comms.canWrite = true;
        islands = 10;
        MapLocation[] want = {L(19, 16), L(19, 4), L(7, 16), L(19, 0), L(0, 16), L(7, 0), L(0, 4), L(0, 0), L(19, 16)};
        for (int c = 0; c < 9; c++) {                           // HQ 0's carriers take slots 0, 1, 2, ... in turn
            resetCarrier(L(8, 5), 100 + c);
            check(Carrier.explInit(), "init " + c);
            check(Carrier.xN == 48 && Carrier.xNx == 8 && Carrier.xDone.length == 48 && Carrier.xPen.length == 48, "grid 40x30: 48");
            check(Carrier.xSlot == (c & 7) && Carrier.xAnchor.equals(want[c]), "HQ 0 carrier " + c + " slot " + Carrier.xSlot + " anchor " + Carrier.xAnchor);
        }
        check(Carrier.fanSlot(shared[Comms.FAN], 0) == 1 && Carrier.fanSlot(shared[Comms.FAN], 1) == 0, "HQ 0 claimed 9 (mod 8), HQ 1 none");
        resetCarrier(L(31, 24), 7);                              // HQ 1: its own counter
        check(Carrier.explInit() && Carrier.xSlot == 0 && Carrier.fanSlot(shared[Comms.FAN], 1) == 1, "HQ 1 slot 0");
        check(Carrier.xAnchor.equals(L(20, 13)), "HQ 1 slot 0: SW toward the centre " + Carrier.xAnchor);
        int v = shared[Comms.FAN];
        resetCarrier(L(8, 5), 13);                               // out of write range: id & 7, no write
        Comms.canWrite = false;
        check(Carrier.explInit() && Carrier.xSlot == (13 & 7) && shared[Comms.FAN] == v, "no write range: id & 7, slot 55 untouched");
        Comms.canWrite = true;
        islands = 35;                                            // island 35 exists: slot 55 is its
        resetCarrier(L(8, 5), 21);
        check(Carrier.explInit() && Carrier.xSlot == (21 & 7) && shared[Comms.FAN] == v, "35 islands: no claim");
        islands = 10;
        resetCarrier(L(8, 5), 22);
        setBudget(C.EXPL_GUARD + 2 * 48 + 599);
        check(!Carrier.explInit() && Carrier.xN == -1 && shared[Comms.FAN] == v, "short of bytecodes: retry, nothing written");
        setBudget(BIG);
        HQState.ourHQs = null;
        check(!Carrier.explInit() && Carrier.xN == -1, "HQs not registered: retry");
        HQState.ourHQs = new MapLocation[]{hq0, hq1};
        G.W = 60; G.H = 60;
        resetCarrier(L(8, 5), 23);
        check(Carrier.explInit() && Carrier.xN == 144 && Carrier.xNx == 12, "60x60: 144 points");
    }

    static void resetCarrier(MapLocation here, int id) {
        G.here = here; G.id = id;
        Carrier.xN = -1; Carrier.xK = -1; Carrier.xLast = -9; Carrier.xTarget = null; Carrier.xGone = false;
        Carrier.xPenOn = false; Carrier.xEhq = null; Carrier.xSlot = -1; Carrier.centreTried = false; Carrier.xPrev = null;
        Nav.bugging = false; Field.usedRound = -1000;
    }

    // ---------------------------------------------------------------- explFrontier: picks, drops, episodes, fallbacks
    static void frontier() {
        try { frontierCases(); } catch (GameActionException e) { throw new RuntimeException(e); }
    }

    static void frontierCases() throws GameActionException {
        G.W = 20; G.H = 20;
        java.util.Arrays.fill(shared, 0);
        MapLocation hq = L(3, 3);
        shared[Comms.HQ_LOC] = G.enc(hq);
        HQState.ourHQs = new MapLocation[]{hq};
        Comms.canWrite = true;
        MapMem.cand = 7;
        MapMem.decidedRound = -1;
        MapMem.tile = null;
        resetCarrier(L(4, 4), 40);
        G.round = 10;
        // tile[] not allocated: set up, no target, toward the anchor (slot 0: NE from (3,3) -> (15,15))
        check(Carrier.explFrontier() && Carrier.xTarget == null && Carrier.xAnchor.equals(L(15, 15)) && Carrier.xK == -1, "no tile[]: anchor");
        MapMem.tile = new char[400];
        G.round = 11;
        check(Carrier.explFrontier() && Carrier.xTarget != null, "first pick");
        // from (4,4) to the anchor (15,15): (7,7) and (12,12) score 11 (= cheb(here, anchor), the least); the downward
        // pass keeps (12,12) (k 10 before k 5), cheb 8 from here: cap 8 / 2 + slack
        check(Carrier.xTarget.equals(L(12, 12)) && Carrier.xBest == 8 && Carrier.xCap == 8 / 2 + C.EXPL_SLACK && Carrier.xStall == 0, "pick (12,12): " + Carrier.xTarget);
        int tk = Carrier.xTk;
        // stalled: same place every turn; given up after EXPL_STALL turns without a new best, then the next point
        for (int i = 1; i <= C.EXPL_STALL; i++) {
            G.round++;
            Carrier.explFrontier();
            check(Carrier.xTarget != null && Carrier.xTk == tk && Carrier.xStall == i, "kept while stalled " + i);
        }
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xDone[tk] && Carrier.xTarget != null && Carrier.xTk != tk, "stall drop, next target " + Carrier.xTarget);
        // the turn cap: progress every turn but too slowly
        tk = Carrier.xTk;
        int cap = Carrier.xCap, d0 = Carrier.xBest;
        check(cap == d0 / 2 + C.EXPL_SLACK, "cap = cheb / 2 + slack");
        // a short gap (a flight turn in between): the target and its give-up counters are kept (no new best: a stall)
        G.round += 2;
        Carrier.explFrontier();
        check(Carrier.xTarget != null && Carrier.xTk == tk && Carrier.xTurns == 1 && Carrier.xStall == 1, "short gap: target and counters kept");
        G.round += C.EXPL_GAP;
        Carrier.explFrontier();
        check(Carrier.xTarget != null && Carrier.xTk == tk && Carrier.xTurns == 2 && Carrier.xStall == 2, "gap of EXPL_GAP: kept");
        // a long gap (over EXPL_GAP rounds): a new episode, the same point re-picked (nothing changed), counters reset
        G.round += C.EXPL_GAP + 1;
        Carrier.explFrontier();
        check(Carrier.xTarget != null && Carrier.xTk == tk && Carrier.xTurns == 0 && Carrier.xStall == 0, "long gap: re-picked, counters reset");
        // the target covered (tile seen, not a cloud): dropped, and its best open grid neighbour taken without a pass
        MapLocation t = Carrier.xTarget;
        set(t.x, t.y, 1);
        boolean[] rd = Carrier.xDone.clone();
        rd[tk] = true;
        int want = refNear(rd, tk, G.here, Carrier.xAnchor, false, null, null, MapMem.cand);
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xDone[tk] && !t.equals(Carrier.xTarget), "covered target dropped");
        check(want >= 0 && Carrier.xTk == want && Carrier.xK == -1 && Carrier.xPrev == null && Carrier.explGoal() == Carrier.xTarget,
            "covered drop: best neighbour k" + want + " taken, no pass: k" + Carrier.xTk + " xK " + Carrier.xK);
        check(Math.abs(Carrier.xTk % 4 - tk % 4) <= 1 && Math.abs(Carrier.xTk / 4 - tk / 4) <= 1, "the pick is a grid neighbour");
        check(Carrier.xStall == 0 && Carrier.xTurns == 0 && Carrier.xBest == G.cheb(G.here, Carrier.xTarget), "neighbour pick: fresh counters");
        tk = Carrier.xTk;
        // a cloud target: stood on -> done; occupied next to it -> dropped
        tk = Carrier.xTk;
        t = Carrier.xTarget;
        set(t.x, t.y, 5);
        G.here = t;
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xDone[tk] && !t.equals(Carrier.xTarget), "stood-on cloud point done");
        tk = Carrier.xTk;
        t = Carrier.xTarget;
        set(t.x, t.y, 5);
        G.here = L(Math.max(0, t.x - 1), t.y);
        if (G.here.equals(t)) G.here = L(t.x + 1, t.y);
        occupied = true;
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xDone[tk] && !t.equals(Carrier.xTarget), "occupied cloud point next to us dropped");
        occupied = false;
        // the image rule under a single symmetry drops a target whose image is covered
        tk = Carrier.xTk;
        t = Carrier.xTarget;
        MapMem.cand = 1;
        set(19 - t.x, 19 - t.y, 1);
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xDone[tk] && !t.equals(Carrier.xTarget), "image-covered target dropped");
        MapMem.cand = 7;
        // the grid used up: today's explore from now on (xGone, centre leg skipped)
        for (int i = 0; i < 400; i++) MapMem.tile[i] = 1;
        G.round++;
        check(!Carrier.explFrontier() && Carrier.xGone && Carrier.centreTried && Carrier.xTarget == null, "grid exhausted: fallback for good");
        // the turn cap on a fresh carrier: moving one tile closer every turn never stalls, the cap drops it
        MapMem.tile = new char[400];
        resetCarrier(L(4, 4), 41);
        G.round = 100;
        Carrier.explFrontier();
        tk = Carrier.xTk;
        t = Carrier.xTarget;
        cap = Carrier.xCap;
        int turns = 0;
        while (Carrier.xTk == tk && Carrier.xTarget != null && turns < 50) {
            G.round++;
            turns++;
            // a fake approach: a new best cheb each turn (never reaches it), so only the cap ends it
            Carrier.xBest = 99;
            Carrier.explFrontier();
        }
        check(turns == cap + 1 && Carrier.xDone[tk], "turn cap " + cap + " ended the target after " + turns);
    }

    // ---------------------------------------------------------------- explNear, the goal, stale bests, rescoring, detours
    static void nearCases() throws GameActionException {
        G.W = 40; G.H = 40;
        java.util.Arrays.fill(shared, 0);
        MapLocation hq = L(4, 6);
        shared[Comms.HQ_LOC] = G.enc(hq);
        HQState.ourHQs = new MapLocation[]{hq};
        Comms.canWrite = true;
        MapMem.cand = 7; MapMem.decidedRound = -1; MapMem.nEnemyHQSeen = 0;
        MapMem.tile = new char[1600];
        resetCarrier(L(5, 8), 60);                              // not a grid point (x 2, 7, ..; y 2, 7, ..)
        G.round = 200;
        setBudget(BIG);
        check(Carrier.explFrontier() && Carrier.xTarget != null && Carrier.xN == 64 && Carrier.xNx == 8, "40x40 first pick");
        int nx = Carrier.xNx, ny = Carrier.xN / nx;
        // (1) no open neighbour: the full pass runs and picks the global best (a non-neighbour)
        int tk = Carrier.xTk;
        for (int dy = -1; dy <= 1; dy++) for (int dx = -1; dx <= 1; dx++) {
            int x = tk % nx + dx, y = tk / nx + dy;
            if (x >= 0 && y >= 0 && x < nx && y < ny) Carrier.xDone[x + y * nx] = true;   // tk too: covered (stood on)
        }
        boolean[] rd = Carrier.xDone.clone();
        int[] ref = refScan(rd, G.here, Carrier.xAnchor, false, null, null, 7);
        G.round++;
        Carrier.explFrontier();
        check(ref[0] >= 0 && Carrier.xTarget != null && Carrier.xTk == ref[0] && Carrier.xK == -1 && Carrier.xPrev == null,
            "no open neighbour: the full pass picks k" + ref[0] + ": k" + Carrier.xTk);
        check(Math.abs(Carrier.xTk % nx - tk % nx) > 1 || Math.abs(Carrier.xTk / nx - tk / nx) > 1, "the full pass's pick is no neighbour");
        // (2) a covered drop with no bytecodes for explNear or the pass: no target, the goal is the point just covered
        tk = Carrier.xTk;
        MapLocation t = Carrier.xTarget;
        Carrier.xDone[tk] = true;
        setBudget(C.EXPL_GUARD);                                // explNear needs EXPL_NEAR_MIN more, the pass any more
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTarget == null && t.equals(Carrier.xPrev) && Carrier.explGoal() == Carrier.xPrev && Carrier.xK == Carrier.xN,
            "pass unfinished after a covered drop: toward the point just covered");
        G.round++;                                              // still no bytecodes: the goal stays
        Carrier.explFrontier();
        check(Carrier.xTarget == null && t.equals(Carrier.explGoal()) && Carrier.xK == Carrier.xN, "goal kept while the pass waits");
        setBudget(BIG);
        rd = Carrier.xDone.clone();
        ref = refScan(rd, G.here, Carrier.xAnchor, false, null, null, 7);
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTarget != null && Carrier.xTk == ref[0] && Carrier.xPrev == null && Carrier.xK == -1 && Carrier.explGoal() == Carrier.xTarget,
            "pass resumed and complete: the pick, xPrev cleared");
        // explNear needs EXPL_GUARD + EXPL_NEAR_MIN: at exactly that the full pass picks instead
        tk = Carrier.xTk;
        Carrier.xDone[tk] = true;
        rd = Carrier.xDone.clone();
        ref = refScan(rd, G.here, Carrier.xAnchor, false, null, null, 7);
        int wantN = refNear(rd.clone(), tk, G.here, Carrier.xAnchor, false, null, null, 7);
        setBudget(C.EXPL_GUARD + C.EXPL_NEAR_MIN);
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTk == ref[0] && Carrier.xK == -1, "explNear short of bytecodes: the pass picks k" + ref[0] + " (neighbour k" + wantN + ")");
        setBudget(BIG);
        // (3) a drop for a stall with the pass unfinished: no goal of its own, toward the anchor
        tk = Carrier.xTk;
        Carrier.xStall = C.EXPL_STALL;
        setBudget(C.EXPL_GUARD);
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTarget == null && Carrier.xPrev == null && Carrier.xDone[tk] && Carrier.explGoal() == Carrier.xAnchor, "stall drop, pass unfinished: the anchor");
        setBudget(BIG);
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTarget != null && Carrier.xK == -1, "then the pass completes");
        // (4) a wall-following or field-descent turn before this one is no stall; a plain turn without a new best is
        tk = Carrier.xTk;
        int st = Carrier.xStall;
        Nav.bugging = true;
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTk == tk && Carrier.xStall == st, "after a wall-following move: no stall");
        Nav.bugging = false;
        Field.usedRound = G.round;                              // this turn's move descended a field
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTk == tk && Carrier.xStall == st, "after a field descent: no stall");
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTk == tk && Carrier.xStall == st + 1, "a plain turn without a new best: a stall");
        Field.usedRound = -1000;
        // (5) a resumed pass rescores its incumbent from here: a bogus 0 would win; the true score loses to a nearer point
        int far = Carrier.xN - 1;                               // (37,37): far from (5,8) and from the anchor
        check(!Carrier.xDone[far], "far corner open");
        Carrier.xTarget = null; Carrier.xPrev = null;
        Carrier.xK = far; Carrier.xBestK = far; Carrier.xBestS = 0;
        rd = Carrier.xDone.clone();
        ref = refScan(rd, G.here, Carrier.xAnchor, false, null, null, 7);
        G.round++;
        Carrier.explFrontier();
        check(ref[0] != far && Carrier.xTk == ref[0] && Carrier.xK == -1, "rescored incumbent: the true best k" + ref[0] + ": k" + Carrier.xTk);
        // (6) a stale best (covered while the pass ran over several turns): no target, marked done, a new pass next turn
        int best = Carrier.xTk;
        Carrier.xTarget = null; Carrier.xPrev = null;
        Carrier.xK = best; Carrier.xBestK = best; Carrier.xBestS = 0;
        set(Carrier.explX(best), Carrier.explY(best), 1);
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTarget == null && Carrier.xDone[best] && Carrier.xK == -1 && Carrier.explGoal() == Carrier.xAnchor, "stale best: no target, done, the anchor");
        rd = Carrier.xDone.clone();
        ref = refScan(rd, G.here, Carrier.xAnchor, false, null, null, 7);
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTarget != null && Carrier.xTk == ref[0] && ref[0] != best, "next turn: a new pass picks k" + ref[0]);
        // a stood-on stale best (xDone set meanwhile, tile unknown) is stale too
        best = Carrier.xTk;
        Carrier.xTarget = null;
        Carrier.xK = best; Carrier.xBestK = best; Carrier.xBestS = 0;
        Carrier.xDone[best] = true;
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTarget == null && Carrier.xK == -1, "stood-on stale best: no target");
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xTarget != null && Carrier.xTk != best, "then a new pick");
        // (7) the symmetry decided: the penalty starts at a covered drop (no pass runs then) and explNear uses it
        MapMem.decidedRound = 150; MapMem.cand = 2;
        check(!Carrier.xPenOn, "penalty off before");
        tk = Carrier.xTk;
        set(Carrier.explX(tk), Carrier.explY(tk), 1);
        MapLocation[] ehq = MapMem.enemyHQs();
        rd = Carrier.xDone.clone();
        rd[tk] = true;
        wantN = refNear(rd, tk, G.here, Carrier.xAnchor, true, HQState.ourHQs, ehq, 2);
        G.round++;
        Carrier.explFrontier();
        check(Carrier.xPenOn && Carrier.xEhq != null && Carrier.xEhq.length == 1 && Carrier.xEhq[0].equals(L(35, 6)), "penalty on at the drop: " + java.util.Arrays.toString(Carrier.xEhq));
        check(wantN >= 0 ? Carrier.xTk == wantN && Carrier.xK == -1 : Carrier.xK == -1, "penalised neighbour pick k" + wantN + ": k" + Carrier.xTk);
        MapMem.decidedRound = -1; MapMem.cand = 7;
        // (8) explNear at the guard: nothing done, no pick
        Carrier.xTarget = null; Carrier.xPrev = L(1, 1);
        boolean[] before = Carrier.xDone.clone();
        setBudget(C.EXPL_GUARD);
        Carrier.explNear(Carrier.xTk, G.here);
        check(Carrier.xTarget == null && Carrier.xPrev.equals(L(1, 1)) && java.util.Arrays.equals(before, Carrier.xDone), "explNear at the guard: no work");
        setBudget(BIG);
        Carrier.xPrev = null;
    }

    /** explNear against a plain reference on seeded random boards: the pick (or none), its counters, the done marks. */
    static void nearRandom() {
        int[] cands = {1, 2, 4, 3, 5, 6, 7};
        int picks = 0, none = 0;
        for (int t = 0; t < 4000; t++) {
            G.W = 20 + R.nextInt(41); G.H = 20 + R.nextInt(41);
            int cand = cands[R.nextInt(cands.length)];
            scanSetup(L(R.nextInt(G.W), R.nextInt(G.H)), L(R.nextInt(G.W), R.nextInt(G.H)), cand);
            double pk = R.nextDouble();
            for (int i = 0; i < G.W * G.H; i++) {
                if (R.nextDouble() >= pk) continue;
                int r = R.nextInt(10);
                MapMem.tile[i] = (char) (r < 6 ? 1 : r < 8 ? 3 : r < 9 ? 5 : 1 | (3 << 3) | (2 << 7));
            }
            for (int k = 0; k < Carrier.xN; k++) if (R.nextInt(4) == 0) Carrier.xDone[k] = true;
            boolean penOn = R.nextBoolean();
            MapLocation[] ours = randomLocs(1 + R.nextInt(4)), ehq = R.nextInt(8) == 0 ? new MapLocation[0] : randomLocs(1 + R.nextInt(6));
            Carrier.xPenOn = penOn;
            HQState.ourHQs = ours;
            Carrier.xEhq = ehq;
            int k0 = R.nextInt(Carrier.xN);
            if (R.nextBoolean()) Carrier.xDone[k0] = true;
            boolean[] refDone = Carrier.xDone.clone();
            int want = refNear(refDone, k0, G.here, Carrier.xAnchor, penOn, ours, ehq, cand);
            Carrier.xTarget = null; Carrier.xTk = -7; Carrier.xPrev = L(0, 0);
            Carrier.explNear(k0, G.here);
            if (want < 0) {
                none++;
                check(Carrier.xTarget == null && Carrier.xTk == -7 && Carrier.xPrev != null, "no open neighbour: no pick");
            } else {
                picks++;
                MapLocation p = L(Carrier.explX(want), Carrier.explY(want));
                check(Carrier.xTk == want && p.equals(Carrier.xTarget) && Carrier.xPrev == null, "neighbour pick = reference: k" + Carrier.xTk + "/" + want);
                check(Carrier.xStall == 0 && Carrier.xTurns == 0 && Carrier.xBest == G.cheb(G.here, p) && Carrier.xCap == Carrier.xBest / 2 + C.EXPL_SLACK, "pick counters");
                check(!refDone[want] && !Carrier.explCovered(p.x, p.y), "pick is a frontier point");
                int nx = Carrier.xNx;
                check(want != k0 && Math.abs(want % nx - k0 % nx) <= 1 && Math.abs(want / nx - k0 / nx) <= 1, "pick is a grid neighbour");
            }
            for (int k = 0; k < Carrier.xN; k++) check(Carrier.xDone[k] == refDone[k], "near: done marks = reference at k" + k);
        }
        check(picks > 1000 && none > 100, "near random coverage: picks " + picks + " none " + none);
    }

    /** explNear written plainly: the best open grid neighbour of k0 (-1 none), highest index on a tie; marks done as
     *  explNear (covered on the way; image-covered when a candidate best). */
    static int refNear(boolean[] done, int k0, MapLocation here, MapLocation anchor, boolean pen, MapLocation[] ours, MapLocation[] ehq, int cand) {
        int nx = (G.W + 4) / 5, n = nx * ((G.H + 4) / 5), bk = -1, bs = Integer.MAX_VALUE;
        boolean single = cand == 1 || cand == 2 || cand == 4;
        for (int k = n - 1; k >= 0; k--) {
            if (k == k0 || Math.abs(k % nx - k0 % nx) > 1 || Math.abs(k / nx - k0 / nx) > 1 || done[k]) continue;
            MapLocation p = L(Math.min(G.W - 1, (k % nx) * 5 + 2), Math.min(G.H - 1, (k / nx) * 5 + 2));
            int c = MapMem.tile[p.x + p.y * G.W];
            if ((c & 1) != 0 && (c & 4) == 0) { done[k] = true; continue; }
            int s = G.cheb(here, p) + G.cheb(p, anchor), pe = pen ? Carrier.explPen(p.x, p.y, ours, ehq) : 0;
            if (s + pe >= bs) continue;
            if (single) {
                MapLocation im = MapMem.img(cand, p);
                int ic = MapMem.tile[im.x + im.y * G.W];
                if ((ic & 1) != 0 && (ic & 4) == 0) { done[k] = true; continue; }
            }
            bs = s + pe; bk = k;
        }
        return bk;
    }

    // ---------------------------------------------------------------- helpers
    static RobotController proxy() {
        return (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
            new Class<?>[]{RobotController.class}, (p, m, args) -> {
                switch (m.getName()) {
                    case "readSharedArray": return shared[(Integer) args[0]];
                    case "canWriteSharedArray": return Comms.canWrite;
                    case "writeSharedArray": shared[(Integer) args[0]] = (Integer) args[1]; writes++; return null;
                    case "getIslandCount": return islands;
                    case "isMovementReady": return false;               // moveTwice does nothing
                    case "getLocation": return G.here;
                    case "canSenseLocation": return sensable;
                    case "isLocationOccupied": return occupied;
                    default: break;
                }
                throw new UnsupportedOperationException("engine call outside the test's proxy: " + m.getName());
            });
    }

    static void setBudget(int v) {
        try {
            java.lang.reflect.Field f = Class.forName("battlecode.instrumenter.inject.RobotMonitor").getDeclaredField("bytecodesLeft");
            f.setAccessible(true);
            f.setInt(null, v);
            check(Clock.getBytecodesLeft() == v, "budget set");
        } catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
    }

    static MapLocation[] randomLocs(int n) {
        MapLocation[] o = new MapLocation[n];
        for (int i = 0; i < n; i++) o[i] = L(R.nextInt(G.W), R.nextInt(G.H));
        return o;
    }

    static MapLocation L(int x, int y) { return new MapLocation(x, y); }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("expl1 FAILED: " + what); System.exit(1); }
    }
}
