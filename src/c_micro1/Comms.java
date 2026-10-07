package c_micro1;

import battlecode.common.*;

/**
 * Shared-array schema (64 slots x 16 bits). Locations are G.enc = x*64+y+1 (12 bits, 0 = none).
 * Writing is allowed only near our HQ (r2 9), our amplifier (r2 20) or our anchored island (r2 4); HQs and
 * amplifiers can always write. Reading is free everywhere (2 bytecodes), writing costs 75.
 *
 *   0..3    HQ_LOC     our HQs, enc(loc), in creation order (HQs write at round 1)
 *   4       SYM_ELIM   symmetry candidates ELIMINATED (bit 0 ROT, 1 FLIP_X, 2 FLIP_Y); OR-merged, so no init needed
 *   5..20   WELLS      (type << 12) | enc(loc); type 1 Ad, 2 Mn, 3 Ex; first free slot claims
 *   21..56  ISLANDS    slot 20+id: (owner << 12) | enc(a tile of the island); owner 0 neutral/unknown, 1 us, 2 them
 *   57..60  ENEMY      enemy fighter sightings: (stamp << 12) | enc(loc); stamp = (round/16) & 15
 *   61      ANCHOR_REQ round (mod 65536) at which an HQ last asked for anchor carriers (unused in g_iter0)
 *   62..63  reserved
 */
public final class Comms {
    public static final int HQ_LOC = 0, SYM_ELIM = 4, WELLS = 5, NWELLS = 16, ISLANDS = 20, ENEMY = 57, NENEMY = 4;

    public static boolean canWrite;   // refreshed once per turn

    public static void startTurn() throws GameActionException {
        canWrite = G.rc.canWriteSharedArray(0, 0);
    }

    public static int read(int i) throws GameActionException { return G.rc.readSharedArray(i); }

    public static boolean write(int i, int v) throws GameActionException {
        if (!canWrite || G.rc.readSharedArray(i) == v) return false;
        return put(i, v);
    }

    /** The only call site of writeSharedArray: legality is re-checked at write time (10 bytecodes), because a robot
     *  that moved since startTurn may have left the write zone (a failed write throws and costs 500). */
    static boolean put(int i, int v) throws GameActionException {
        if (!G.rc.canWriteSharedArray(i, v)) { canWrite = false; return false; }
        G.rc.writeSharedArray(i, v);
        return true;
    }

    // ---------------------------------------------------------------- HQs
    public static MapLocation[] ourHQs() throws GameActionException {
        int n = 0;
        for (int i = 0; i < 4; i++) if (read(HQ_LOC + i) != 0) n++;
        MapLocation[] out = new MapLocation[n];
        n = 0;
        for (int i = 0; i < 4; i++) { int v = read(HQ_LOC + i); if (v != 0) out[n++] = G.dec(v); }
        return out;
    }

    public static void registerHQ(MapLocation l) throws GameActionException {
        int e = G.enc(l);
        for (int i = 0; i < 4; i++) {
            int v = read(HQ_LOC + i);
            if (v == e) return;
            if (v == 0) { put(HQ_LOC + i, e); return; }
        }
    }

    // ---------------------------------------------------------------- symmetry
    public static int symEliminated() throws GameActionException { return read(SYM_ELIM) & 7; }

    public static void publishSym(int eliminated) throws GameActionException {
        int cur = read(SYM_ELIM);
        if ((cur | eliminated) != cur) write(SYM_ELIM, cur | eliminated);
    }

    // ---------------------------------------------------------------- wells
    public static void registerWell(MapLocation l, int t) throws GameActionException {
        if (!canWrite) return;
        int e = G.enc(l), v = (t << 12) | e;
        for (int i = WELLS; i < WELLS + NWELLS; i++) {
            int c = read(i);
            if ((c & 0xfff) == e) { if (c != v) put(i, v); return; }
            if (c == 0) { put(i, v); return; }
        }
    }

    /** Nearest registered well of a type (0 = any). */
    public static MapLocation nearestWell(MapLocation from, int t) throws GameActionException {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = WELLS; i < WELLS + NWELLS; i++) {
            int c = read(i);
            if (c == 0) break;
            if (t != 0 && (c >>> 12) != t) continue;
            MapLocation l = G.dec(c & 0xfff);
            int d = from.distanceSquaredTo(l);
            if (d < bd) { bd = d; best = l; }
        }
        return best;
    }

    // ---------------------------------------------------------------- islands
    public static void reportIsland(int islandId, int owner, MapLocation tile) throws GameActionException {
        if (!canWrite || islandId <= 0 || islandId > 36) return;
        int v = (owner << 12) | G.enc(tile);
        int c = read(ISLANDS + islandId);
        if ((c >>> 12) != owner || c == 0) put(ISLANDS + islandId, v);
    }

    public static int islandOwner(int islandId) throws GameActionException { return read(ISLANDS + islandId) >>> 12; }

    public static MapLocation islandTile(int islandId) throws GameActionException { return G.dec(read(ISLANDS + islandId) & 0xfff); }

    // ---------------------------------------------------------------- enemy sightings
    public static void reportEnemy(MapLocation l) throws GameActionException {
        if (!canWrite) return;
        int stamp = (G.round >> 4) & 15, v = (stamp << 12) | G.enc(l);
        int oldest = ENEMY, oldestAge = -1;
        for (int i = ENEMY; i < ENEMY + NENEMY; i++) {
            int c = read(i);
            if (c == 0) { put(i, v); return; }
            MapLocation cl = G.dec(c & 0xfff);
            if (cl.distanceSquaredTo(l) <= 20) { if (c != v) put(i, v); return; }   // same cluster: refresh
            int age = (stamp - (c >>> 12)) & 15;
            if (age > oldestAge) { oldestAge = age; oldest = i; }
        }
        put(oldest, v);
    }

    /** Freshest enemy sighting nearest to `from` that is at most maxAge*16 rounds old, or null. */
    public static MapLocation nearestEnemy(MapLocation from, int maxAge) throws GameActionException {
        int stamp = (G.round >> 4) & 15;
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = ENEMY; i < ENEMY + NENEMY; i++) {
            int c = read(i);
            if (c == 0) continue;
            if (((stamp - (c >>> 12)) & 15) > maxAge) continue;
            MapLocation l = G.dec(c & 0xfff);
            int d = from.distanceSquaredTo(l);
            if (d < bd) { bd = d; best = l; }
        }
        return best;
    }

    /** Clear a sighting near l (we looked and nobody is there). */
    public static void clearEnemyNear(MapLocation l) throws GameActionException {
        if (!canWrite) return;
        for (int i = ENEMY; i < ENEMY + NENEMY; i++) {
            int c = read(i);
            if (c != 0 && G.dec(c & 0xfff).distanceSquaredTo(l) <= 8) put(i, 0);
        }
    }
}
