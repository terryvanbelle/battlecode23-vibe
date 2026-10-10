package c_well3;

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
 *   61      AD_FLAGS   arch_swarm: bit i (0-3) set = HQ i (HQ_LOC order) wants adamantium for carriers (C.AD_NEED, cap
 *                      room); c_anc3: bit PRESS_SHIFT+i (4-7) set = HQ i is pressed (C.PRESS_SUM enemy fighter-rounds in
 *                      its vision in the last or current C.PRESS_BUCKET-round bucket); each HQ writes only its own bits;
 *                      c_well3: bit C.PROBE_SHIFT+i (8-11) set = HQ i's well probe has been claimed (one per HQ per
 *                      game, set once by the claiming carrier, never cleared; setAdFlag and setPressed keep it)
 *   62..63  CENSUS     arch_swarm: live-carrier census, slot 62 + (epoch & 1), epoch = round >> 6; each carrier adds 1
 *                      once per epoch at its first writable turn; HQ 0 zeroes the next epoch's slot at phase 32
 */
public final class Comms {
    public static final int HQ_LOC = 0, SYM_ELIM = 4, WELLS = 5, NWELLS = 16, ISLANDS = 20, ENEMY = 57, NENEMY = 4,
        AD_FLAGS = 61, CENSUS = 62;
    /** c_anc3: AD_FLAGS bits PRESS_SHIFT..PRESS_SHIFT+3 are the HQs' "pressed" flags (adFlag reads only bits 0-3). */
    public static final int PRESS_SHIFT = 4;

    public static boolean canWrite;   // refreshed once per turn
    /** Telemetry only (never read by decisions): shared-array writes made and refused; the age in stamps of the sighting
     *  nearestEnemy returned last; the type of the well nearestWell returned last and the count of filled well slots. */
    public static int writes, refusedWrites, lastAge = 15, lastWellType, lastWellCount;

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
        if (!G.rc.canWriteSharedArray(i, v)) { canWrite = false; if (C.TELEMETRY) refusedWrites++; return false; }
        G.rc.writeSharedArray(i, v);
        if (C.TELEMETRY) writes++;
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

    /** Index of an HQ location in HQ_LOC (0-3), or -1. */
    public static int hqIndex(MapLocation l) throws GameActionException {
        if (l == null) return -1;
        int e = G.enc(l);
        for (int i = 0; i < 4; i++) if (read(HQ_LOC + i) == e) return i;
        return -1;
    }

    // ---------------------------------------------------------------- arch_swarm: carrier census and Ad flags
    static int censusEpoch = -1;

    /** Carriers: count this carrier once per 64-round epoch, at its first turn with write access (near an HQ). */
    public static void censusTick() throws GameActionException {
        int e = G.round >> 6;
        if (e == censusEpoch || !canWrite) return;
        int slot = CENSUS + (e & 1);
        if (put(slot, Math.min(65535, read(slot) + 1))) censusEpoch = e;
    }

    /** HQs: the complete count of the previous epoch (read while it is still intact) and the current partial count. */
    static int prevCensus;

    public static int liveCarriers(boolean zeroer) throws GameActionException {
        int e = G.round >> 6, phase = G.round & 63;
        int cur = read(CENSUS + (e & 1));
        if (e == 0) prevCensus = 0;
        else if (phase < 32) prevCensus = read(CENSUS + ((e - 1) & 1));
        else if (zeroer && phase == 32) put(CENSUS + ((e + 1) & 1), 0);
        // first half of an epoch: the previous complete count (dead carriers still in it); second half: the current
        // count, which by then holds nearly every carrier (trip cycles 37-67 rounds)
        return phase < 32 ? Math.max(prevCensus, cur) : cur;
    }

    public static boolean adFlag(int hq) throws GameActionException { return hq >= 0 && (read(AD_FLAGS) >> hq & 1) != 0; }

    public static void setAdFlag(int hq, boolean on) throws GameActionException {
        if (hq < 0) return;
        int v = read(AD_FLAGS), n = on ? v | (1 << hq) : v & ~(1 << hq);
        if (n != v) put(AD_FLAGS, n);
    }

    /** c_anc3: set or clear HQ hq's pressed bit (HQs only; they can always write). setAdFlag keeps bits 4-7. */
    public static void setPressed(int hq, boolean on) throws GameActionException {
        if (hq < 0) return;
        int v = read(AD_FLAGS), b = 1 << (PRESS_SHIFT + hq), n = on ? v | b : v & ~b;
        if (n != v) put(AD_FLAGS, n);
    }

    /** c_anc3: whether any of our HQs is pressed. */
    public static boolean anyPressed() throws GameActionException { return (read(AD_FLAGS) >>> PRESS_SHIFT & 15) != 0; }

    /** c_anc3 islandStats: island slots by state, ids 1..min(35, n): not located (empty slot), located neutral, ours,
     *  theirs. One pass, about 10 bytecodes an id; stops under C.ISLAND_LOOP_GUARD (counts then partial). */
    public static int islUnloc, islLocNeutral, islUs, islThem;

    public static void islandStats(int n) throws GameActionException {
        int unloc = 0, neutral = 0, us = 0, them = 0;
        if (n > 35) n = 35;
        for (int id = 1; id <= n; id++) {
            if (Clock.getBytecodesLeft() < C.ISLAND_LOOP_GUARD) break;
            int c = read(ISLANDS + id);
            if (c == 0) unloc++;
            else switch (c >>> 12) {
                case 0: neutral++; break;
                case 1: us++; break;
                case 2: them++; break;
                default: break;
            }
        }
        islUnloc = unloc; islLocNeutral = neutral; islUs = us; islThem = them;
    }

    /** Number of shared wells of type t. */
    public static int wellCount(int t) throws GameActionException {
        int n = 0;
        for (int i = WELLS; i < WELLS + NWELLS; i++) { int c = read(i); if (c == 0) break; if ((c >>> 12) == t) n++; }
        return n;
    }

    // ---------------------------------------------------------------- symmetry
    public static int symEliminated() throws GameActionException { return read(SYM_ELIM) & 7; }

    /** OR-merge eliminations; never eliminate all three (audit SYM-1: a destroyed enemy HQ seen as an empty predicted
     *  tile can eliminate the true symmetry, and an all-eliminated mask is useless to every reader). */
    public static void publishSym(int eliminated) throws GameActionException {
        int cur = read(SYM_ELIM);
        int next = (cur | eliminated) & 7;
        if (next != (cur & 7) && next != 7) write(SYM_ELIM, next);
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
        int bd = Integer.MAX_VALUE, i;
        for (i = WELLS; i < WELLS + NWELLS; i++) {
            int c = read(i);
            if (c == 0) break;
            if (t != 0 && (c >>> 12) != t) continue;
            MapLocation l = G.dec(c & 0xfff);
            int d = from.distanceSquaredTo(l);
            if (d < bd) { bd = d; best = l; if (C.TELEMETRY) lastWellType = c >>> 12; }
        }
        if (C.TELEMETRY) lastWellCount = i - WELLS;
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
        int oldest = ENEMY, oldestAge = -1, empty = -1;
        for (int i = ENEMY; i < ENEMY + NENEMY; i++) {       // same cluster first, then an empty slot, then the oldest
            int c = read(i);
            if (c == 0) { if (empty < 0) empty = i; continue; }
            MapLocation cl = G.dec(c & 0xfff);
            if (cl.distanceSquaredTo(l) <= 20) { if (c != v) put(i, v); return; }   // same cluster: refresh
            int age = (stamp - (c >>> 12)) & 15;
            if (age > oldestAge) { oldestAge = age; oldest = i; }
        }
        put(empty >= 0 ? empty : oldest, v);
    }

    /** Freshest enemy sighting nearest to `from` that is at most maxAge*16 rounds old, or null. */
    public static MapLocation nearestEnemy(MapLocation from, int maxAge) throws GameActionException {
        int stamp = (G.round >> 4) & 15;
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = ENEMY; i < ENEMY + NENEMY; i++) {
            int c = read(i);
            if (c == 0) continue;
            int age = (stamp - (c >>> 12)) & 15;
            if (age > maxAge) continue;
            MapLocation l = G.dec(c & 0xfff);
            int d = from.distanceSquaredTo(l);
            if (d < bd) { bd = d; best = l; if (C.TELEMETRY) lastAge = age; }
        }
        return best;
    }

    /** Clear a sighting near l that this robot can see (we looked and nobody is there). Only tiles in our own
     *  vision (audit ENEMY-2: a launcher cleared sightings beyond its vision and on clouds it could not see into). */
    public static void clearEnemyNear(MapLocation l) throws GameActionException {
        if (!canWrite) return;
        for (int i = ENEMY; i < ENEMY + NENEMY; i++) {
            int c = read(i);
            if (c == 0) continue;
            MapLocation cl = G.dec(c & 0xfff);
            if (cl.distanceSquaredTo(l) <= 8 && G.rc.canSenseLocation(cl)) put(i, 0);
        }
    }

    /** Zero sightings older than 3 stamps (48-63+ rounds): nobody acts on them, and a 4-bit stamp wraps after 256
     *  rounds, which would make an uncleared one look fresh again (audit ENEMY-1). Called by HQs, which can always write. */
    public static void expireEnemies() throws GameActionException {
        if (!canWrite) return;
        int stamp = (G.round >> 4) & 15;
        for (int i = ENEMY; i < ENEMY + NENEMY; i++) {
            int c = read(i);
            if (c != 0 && ((stamp - (c >>> 12)) & 15) > 3) put(i, 0);
        }
    }
}
