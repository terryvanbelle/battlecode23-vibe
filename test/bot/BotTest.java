package bot;

import battlecode.common.*;
import java.util.Random;

/**
 * Pure-logic tests for the bot (no engine): encodings, the comms layout, symmetry images and the inference.
 * Plain main with an exit code (the engine jar has no JUnit). Run by tools/unit-tests.sh.
 */
public class BotTest {
    static int fails, checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { fails++; System.out.println("FAIL: " + what); }
    }

    public static void main(String[] a) {
        encodings();
        commsLayout();
        symmetryImages();
        symmetryInference();
        System.out.println("BotTest: " + checks + " checks, " + fails + " failures");
        if (fails > 0) System.exit(1);
    }

    static void encodings() {
        for (int x = 0; x < 60; x++) for (int y = 0; y < 60; y++) {
            MapLocation l = new MapLocation(x, y);
            int e = G.enc(l);
            check(e > 0 && e < 4096, "enc fits 12 bits " + l);
            check(G.dec(e).equals(l), "dec(enc) " + l);
        }
        check(G.dec(0) == null, "dec(0) is none");
    }

    static void commsLayout() {
        // regions must not overlap and must fit in 64 slots
        int[][] regions = {{Comms.HQ_LOC, 4}, {Comms.SYM_ELIM, 1}, {Comms.WELLS, Comms.NWELLS}, {Comms.ISLANDS + 1, 36},
            {Comms.ENEMY, Comms.NENEMY}};
        boolean[] used = new boolean[64];
        for (int[] r : regions) for (int i = r[0]; i < r[0] + r[1]; i++) {
            check(i >= 0 && i < 64, "slot in range " + i);
            if (i >= 0 && i < 64) { check(!used[i], "slot used once " + i); used[i] = true; }
        }
        // a well entry: type in bits 12-13, location in 12 bits
        int v = (2 << 12) | G.enc(new MapLocation(59, 59));
        check((v >>> 12) == 2 && (v & 0xfff) == G.enc(new MapLocation(59, 59)) && v < 65536, "well entry packing");
        int iv = (2 << 12) | G.enc(new MapLocation(59, 59));
        check(iv < 65536, "island entry fits 16 bits");
    }

    static void symmetryImages() {
        G.W = 30; G.H = 20;
        for (int s = 1; s <= 4; s <<= 1) {
            for (int x = 0; x < G.W; x++) for (int y = 0; y < G.H; y++) {
                int ix = MapMem.imgX(s, x), iy = MapMem.imgY(s, y);
                check(ix >= 0 && ix < G.W && iy >= 0 && iy < G.H, "image on map");
                check(MapMem.imgX(s, ix) == x && MapMem.imgY(s, iy) == y, "image is an involution");
            }
            for (Direction d : G.DIRS) check(MapMem.imgDir(s, MapMem.imgDir(s, d)) == d, "dir image involution " + s + d);
        }
        check(MapMem.imgDir(MapMem.ROT, Direction.NORTH) == Direction.SOUTH, "ROT N->S");
        check(MapMem.imgDir(MapMem.ROT, Direction.NORTHEAST) == Direction.SOUTHWEST, "ROT NE->SW");
        check(MapMem.imgDir(MapMem.FLIP_X, Direction.NORTHEAST) == Direction.NORTHWEST, "FLIP_X NE->NW");
        check(MapMem.imgDir(MapMem.FLIP_X, Direction.NORTH) == Direction.NORTH, "FLIP_X N->N");
        check(MapMem.imgDir(MapMem.FLIP_Y, Direction.NORTHEAST) == Direction.SOUTHEAST, "FLIP_Y NE->SE");
        check(MapMem.imgDir(MapMem.FLIP_Y, Direction.EAST) == Direction.EAST, "FLIP_Y E->E");
    }

    /**
     * 300 random maps, each symmetric under one candidate (walls, clouds, currents transformed); tiles are revealed in
     * random order through MapMem.checkTile. The true symmetry must never be eliminated, and most maps must be decided.
     */
    static void symmetryInference() {
        Random rnd = new Random(2023);
        int decided = 0, total = 300;
        for (int m = 0; m < total; m++) {
            G.W = 20 + rnd.nextInt(41); G.H = 20 + rnd.nextInt(41);
            int truth = 1 << rnd.nextInt(3);
            char[] full = new char[G.W * G.H];
            for (int x = 0; x < G.W; x++) for (int y = 0; y < G.H; y++) {
                int ix = MapMem.imgX(truth, x), iy = MapMem.imgY(truth, y);
                int idx = x + y * G.W, iidx = ix + iy * G.W;
                if (iidx < idx) continue;        // fill one of each symmetric pair, then mirror it
                int c = 1;
                int r = rnd.nextInt(100);
                if (r < 15) c |= 2; else if (r < 25) c |= 4;
                Direction cur = Direction.CENTER;
                if ((c & 2) == 0 && rnd.nextInt(100) < 8) cur = G.DIRS[rnd.nextInt(8)];
                if (iidx == idx) cur = Direction.CENTER;   // a self-symmetric tile cannot hold a consistent current
                int cc = c, ic = c;
                if (cur != Direction.CENTER) {
                    cc |= (cur.ordinal() + 1) << 3;
                    ic |= (MapMem.imgDir(truth, cur).ordinal() + 1) << 3;
                }
                full[idx] = (char) cc;
                full[iidx] = (char) ic;
            }
            MapMem.tile = new char[G.W * G.H];
            MapMem.cand = 7;
            MapMem.symConflicts = 0;
            int n = G.W * G.H;
            int[] order = new int[n];
            for (int i = 0; i < n; i++) order[i] = i;
            for (int i = n - 1; i > 0; i--) { int j = rnd.nextInt(i + 1); int t = order[i]; order[i] = order[j]; order[j] = t; }
            for (int k = 0; k < n; k++) {
                int idx = order[k];
                MapMem.tile[idx] = full[idx];
                MapMem.checkTile(idx % G.W, idx / G.W);
            }
            check((MapMem.cand & truth) != 0, "true symmetry survives (map " + m + ")");
            check(MapMem.symConflicts == 0, "no conflicts on a consistent map (map " + m + ")");
            if (MapMem.cand == truth) decided++;
        }
        check(decided >= total * 9 / 10, "most random maps decided with full information: " + decided + "/" + total);
    }
}
