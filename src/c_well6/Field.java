package c_well6;

import battlecode.common.*;

/**
 * Breadth-first distance field toward one target (owner, PROMPTS 35: on Target, match 1208, launchers pooled in a
 * dead-end corridor for 300+ rounds; greedy steps lead into any pocket that points at the target, and wall-following
 * lost its state whenever cohesion switched the robot to another target).
 *
 * Rows are 64-bit masks (W <= 60): wall[y] bit x = a wall this robot has sensed, plus its image once the symmetry is
 * decided (taken when a field starts); unknown squares count as open. waves[k][y] bit x = the squares exactly k king
 * moves from the target. A field starts when wall-following begins toward a target and is computed a wave at a time in
 * the bytecodes left at the end of the turn (think: about 30 bytecodes per row per wave). A robot on wave k steps to a
 * neighbour on wave k - 1 (Nav.moveTo). A wall sensed on a square the field counted as open marks it stale, and it is
 * recomputed (at most once per C.FIELD_RESTART rounds).
 */
public final class Field {
    static final int MAX_WAVES = 400;
    static long[] wall;
    static long full;
    static MapLocation target;
    static long[][] waves = new long[MAX_WAVES][];
    static int nWaves;
    static long[] vis, blk;
    static boolean pending, done, stale;
    static int startRound = -1000, usedRound = -1000, ylo, yhi, lastK = -1;
    // resumable work: the obstacle rows being built (iy counts down, -1 = not started) and the wave in progress
    static long[] nb, nv, cw, nw;
    static int iy = -1, sym, wy = -1, wlo, whi, nlo, nhi;
    static long hp, hc;
    public static int fields, restarts, descents;   // diagnostics

    static void init() {
        wall = new long[G.H];
        full = (1L << G.W) - 1;
    }

    /** MapMem.process: a wall sensed at (x, y). */
    static void addWall(int x, int y) {
        long b = 1L << x;
        wall[y] |= b;
        if (vis != null && (vis[y] & b) != 0) stale = true;
    }

    /** Start (or restart, when stale) a field toward t; the work happens in think(). A plan (the march's team target)
     *  replaces another target's field; a field asked for on hitting a wall does not replace one that is young (still
     *  being built), in use, or aimed within r2 C.FIELD_NEAR_D2 of t (cohesion moves and raid wells near the team
     *  target made fields restart 49 times in one launcher's life before any finished: Target, c_nav3 v2). */
    static void request(MapLocation t, boolean plan) {
        if (target != null && target.equals(t)) {
            if (!stale || G.round - startRound < C.FIELD_RESTART) return;
            restarts++;
        } else {
            if (target != null && !plan && (G.round - usedRound <= C.FIELD_KEEP || G.round - startRound <= C.FIELD_YOUNG
                || target.distanceSquaredTo(t) <= C.FIELD_NEAR_D2)) return;
            fields++;
        }
        target = t;
        pending = true;
        iy = -1;
        wy = -1;
        done = false;
        stale = false;
        nWaves = 0;
        lastK = -1;
        startRound = G.round;
    }

    static boolean ready(MapLocation t) { return target != null && nWaves > 0 && target.equals(t); }

    /** End of turn: build a requested field's obstacle rows, then add waves, row by row while more than `reserve`
     *  bytecodes remain (both resume next turn where they stopped: a launcher rarely has more than 5,000 to spare). */
    static void think(int reserve) {
        if (target == null) return;
        int H = G.H;
        if (pending) {
            if (iy < 0) {
                if (Clock.getBytecodesLeft() < reserve + 800) return;
                nb = new long[H];
                nv = new long[H];
                sym = MapMem.decided() ? MapMem.cand : 0;
                iy = H - 1;
            }
            long out = ~full;
            while (iy >= 0) {
                if (Clock.getBytecodesLeft() < reserve + 300) return;
                int y = iy--;
                long w = wall[y];
                if (sym == MapMem.FLIP_X) w |= rev(wall[y]);
                else if (sym == MapMem.FLIP_Y) w |= wall[H - 1 - y];
                else if (sym == MapMem.ROT) w |= rev(wall[H - 1 - y]);
                nb[y] = w | out;
            }
            if (Clock.getBytecodesLeft() < reserve + 600) return;
            // headquarters never move: their squares are obstacles too (the target's own square is the seed)
            MapLocation[] o = HQState.ourHQs;
            if (o != null) for (int i = o.length; --i >= 0; ) nb[o[i].y] |= 1L << o[i].x;
            for (int i = MapMem.nEnemyHQSeen; --i >= 0; ) { MapLocation e = MapMem.enemyHQSeen[i]; nb[e.y] |= 1L << e.x; }
            long[] w0 = new long[H];
            long seed = 1L << target.x;
            w0[target.y] = seed;
            nv[target.y] = seed;
            blk = nb;
            vis = nv;
            waves[0] = w0;
            nWaves = 1;
            ylo = yhi = target.y;
            wy = -1;
            pending = false;
        }
        long[] b = blk, v = vis;
        while (!done) {
            if (wy < 0) {                       // begin the next wave
                if (Clock.getBytecodesLeft() < reserve + 400) return;
                cw = waves[nWaves - 1];
                nw = new long[H];
                wlo = ylo > 0 ? ylo - 1 : 0;
                whi = yhi < H - 1 ? yhi + 1 : H - 1;
                long x = cw[wlo];
                hp = 0;
                hc = x | (x << 1) | (x >>> 1);
                nlo = nhi = -1;
                wy = wlo;
            }
            long[] c = cw, n = nw;
            while (wy <= whi) {
                if (Clock.getBytecodesLeft() < reserve + 150) return;
                int y = wy++;
                long hn = 0;
                if (y < whi) { long x = c[y + 1]; hn = x | (x << 1) | (x >>> 1); }
                long m = (hp | hc | hn) & ~(b[y] | v[y]);
                if (m != 0) { n[y] = m; v[y] |= m; if (nlo < 0) nlo = y; nhi = y; }
                hp = hc;
                hc = hn;
            }
            wy = -1;
            if (nlo < 0) { done = true; return; }
            waves[nWaves++] = n;
            ylo = nlo;
            yhi = nhi;
            if (nWaves >= MAX_WAVES) done = true;
        }
    }

    /** The W low bits of v in reverse order (bit x -> bit W-1-x). */
    static long rev(long v) {
        v = ((v >>> 1) & 0x5555555555555555L) | ((v & 0x5555555555555555L) << 1);
        v = ((v >>> 2) & 0x3333333333333333L) | ((v & 0x3333333333333333L) << 2);
        v = ((v >>> 4) & 0x0F0F0F0F0F0F0F0FL) | ((v & 0x0F0F0F0F0F0F0F0FL) << 4);
        v = ((v >>> 8) & 0x00FF00FF00FF00FFL) | ((v & 0x00FF00FF00FF00FFL) << 8);
        v = ((v >>> 16) & 0x0000FFFF0000FFFFL) | ((v & 0x0000FFFF0000FFFFL) << 16);
        v = (v >>> 32) | (v << 32);
        return v >>> (64 - G.W);
    }

    /** The wave holding (x, y), or -1 when the field does not reach it yet (or the search ran out of bytecodes).
     *  c_nav5: the cached wave and its neighbours first, then outward from it, stopping with fewer than
     *  C.FIELD_LEVEL_GUARD bytecodes left: an unguarded scan of up to 400 waves (about 10 bytecodes each) ran inside the
     *  turn's own work and overran 3 launcher turns in g_iter3's replica panel (match 1811, Cornucopia, r1801-1979). */
    static int level(int x, int y) {
        long bit = 1L << x;
        if (vis == null || (vis[y] & bit) == 0) return -1;
        int n = nWaves, c = lastK < 0 ? 0 : lastK < n ? lastK : n - 1;
        for (int d = 0; d < n; d++) {
            int lo = c - d, hi = c + d;
            if (lo < 0 && hi >= n) break;
            if ((d & 7) == 7 && Clock.getBytecodesLeft() < C.FIELD_LEVEL_GUARD) return -1;
            if (lo >= 0 && (waves[lo][y] & bit) != 0) return lastK = lo;
            if (d > 0 && hi < n && (waves[hi][y] & bit) != 0) return lastK = hi;
        }
        return -1;
    }
}
