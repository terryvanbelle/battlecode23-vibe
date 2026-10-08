package c_line6a;

import battlecode.common.*;

/**
 * Per-robot memory of immutable tile features and the map-symmetry inference that uses it.
 *
 * Tile code (char per tile, index x + y*W): bit 0 known, bit 1 wall, bit 2 cloud, bits 3-6 current (Direction
 * ordinal + 1; 0 = none), bits 7-8 well type (1 Ad, 2 Mn, 3 Ex), bit 9 island.
 *
 * Symmetry: candidates ROT (x,y)->(W-1-x,H-1-y), FLIP_X (x,y)->(W-1-x,y), FLIP_Y (x,y)->(x,H-1-y) as a bitmask
 * (1, 2, 4). A candidate is eliminated only by contradicting evidence: a known tile whose remembered image differs
 * (walls, clouds, transformed currents, well presence), an enemy HQ seen where the candidate predicts none, or a
 * predicted enemy HQ location seen empty. The mask is never emptied (a contradiction that would empty it is counted in
 * symConflicts and ignored). Eliminations are OR-merged through Comms.SYM_ELIM.
 */
public final class MapMem {
    public static final int ROT = 1, FLIP_X = 2, FLIP_Y = 4;
    public static char[] tile;            // lazily allocated (W*H bytecodes)
    public static int cand = 7;            // surviving symmetry candidates
    public static int symConflicts;
    public static int decidedRound = -1;
    private static int published;          // eliminations already published
    private static MapLocation lastScan;
    public static MapLocation[] enemyHQSeen = new MapLocation[4];
    public static int nEnemyHQSeen;
    // islands seen by this robot: id -> one tile and last-seen owner (0 neutral, 1 us, 2 them), round seen
    public static MapLocation[] islandTile = new MapLocation[40];
    public static int[] islandOwner = new int[40];
    public static int[] islandSeen = new int[40];

    static void alloc() { if (tile == null) tile = new char[G.W * G.H]; }

    // vision disk awaiting processing (bytecode-budgeted: processed at the end of the turn, resumed next turn)
    private static MapInfo[] pending;
    private static int pendingIdx;
    // wells seen but not yet published (published when the robot can write)
    private static MapLocation[] unreported = new MapLocation[16];
    private static int[] unreportedType = new int[16];
    private static int nUnreported;
    // every well this robot has seen (never cleared): a carrier mines a well it saw before the team hears of it, and
    // wells beyond the 16 shared slots stay usable (audit WELL-1/2: gather() read only the shared array)
    private static MapLocation[] seenWell = new MapLocation[32];
    private static int[] seenWellType = new int[32];
    private static int nSeenWell;
    // telemetry only (never read by decisions): peaks of the vision backlog after the fill and of unpublished wells;
    // the type of the well nearestSeenWell returned last
    public static int maxPending, maxUnreported, lastSeenType;

    /** Cheap per-turn sensing: wells (100) and, after a move, queue the vision disk for budgeted processing. */
    public static void scan() throws GameActionException {
        RobotController rc = G.rc;
        if (lastScan == null || !lastScan.equals(G.here)) {
            lastScan = G.here;
            pending = rc.senseNearbyMapInfos();
            pendingIdx = pending.length;
            WellInfo[] wells = rc.senseNearbyWells();
            int[] fresh = new int[wells.length];
            int nf = 0;
            for (int i = wells.length; --i >= 0; ) {           // pass 1: record every well in vision
                MapLocation l = wells[i].getMapLocation();
                ResourceType rt = wells[i].getResourceType();
                int t = rt == ResourceType.ADAMANTIUM ? 1 : rt == ResourceType.MANA ? 2 : 3;
                if (tile != null) {
                    int idx = l.x + l.y * G.W;
                    if (((tile[idx] >> 7) & 3) == 0) { tile[idx] = (char) (tile[idx] | (t << 7)); fresh[nf++] = idx; }
                }
                noteWell(l, t);
            }
            if (cand != 1 && cand != 2 && cand != 4)               // pass 2: a sensed image with no well contradicts
                for (int i = nf; --i >= 0; ) checkWell(fresh[i] % G.W, fresh[i] / G.W, 0);
        }
        observeHQs();
        flushWells();
        if (decidedRound < 0 && (cand == 1 || cand == 2 || cand == 4)) decidedRound = G.round;
    }

    static void noteWell(MapLocation l, int t) {
        int k = nSeenWell;
        while (--k >= 0 && !seenWell[k].equals(l)) { }
        if (k >= 0) seenWellType[k] = t;
        else if (nSeenWell < seenWell.length) { seenWell[nSeenWell] = l; seenWellType[nSeenWell++] = t; }
        for (int i = nUnreported; --i >= 0; ) if (unreported[i].equals(l)) { unreportedType[i] = t; return; }
        if (nUnreported < unreported.length && !Wells.known(l)) {
            unreported[nUnreported] = l; unreportedType[nUnreported++] = t;
            if (C.TELEMETRY && nUnreported > maxUnreported) maxUnreported = nUnreported;
        }
    }

    /** Nearest well of type t (0 = any) that this robot has seen itself, or null. */
    public static MapLocation nearestSeenWell(MapLocation from, int t) {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = nSeenWell; --i >= 0; ) {
            if (t != 0 && seenWellType[i] != t) continue;
            int d = from.distanceSquaredTo(seenWell[i]);
            if (d < bd) { bd = d; best = seenWell[i]; if (C.TELEMETRY) lastSeenType = seenWellType[i]; }
        }
        return best;
    }

    public static int seenWellCount() { return nSeenWell; }

    public static MapLocation seenWellAt(int i) { return seenWell[i]; }

    public static int seenWellTypeAt(int i) { return seenWellType[i]; }

    static void flushWells() throws GameActionException {
        if (!Comms.canWrite) return;
        for (int i = nUnreported; --i >= 0; ) Comms.registerWell(unreported[i], unreportedType[i]);
        nUnreported = 0;
    }

    /** Process queued vision tiles while more than `reserve` bytecodes remain (call at the end of the turn). */
    public static void process(int reserve) throws GameActionException {
        if (pending == null) return;
        if (tile == null) {
            if (Clock.getBytecodesLeft() < G.W * G.H + reserve + 200) return;
            tile = new char[G.W * G.H];
        }
        int W = G.W;
        boolean undecided = cand != 1 && cand != 2 && cand != 4;
        while (pendingIdx > 0 && Clock.getBytecodesLeft() > reserve) {
            MapInfo mi = pending[--pendingIdx];
            MapLocation l = mi.getMapLocation();
            int idx = l.x + l.y * W;
            if ((tile[idx] & 1) != 0) continue;
            int c = 1;
            if (!mi.isPassable()) c |= 2;
            if (mi.hasCloud()) c |= 4;
            Direction cd = mi.getCurrentDirection();
            if (cd != null && cd != Direction.CENTER) c |= (cd.ordinal() + 1) << 3;
            tile[idx] = (char) (tile[idx] | c);
            if (undecided) { checkTile(l.x, l.y); undecided = cand != 1 && cand != 2 && cand != 4; }
        }
        if (C.TELEMETRY && pendingIdx > maxPending) maxPending = pendingIdx;
        if (decidedRound < 0 && !undecided) decidedRound = G.round;
    }

    public static int pendingTiles() { return pendingIdx; }

    /** Islands are costly to sense (200 + 100 per island); callers decide how often. */
    public static void scanIslands() throws GameActionException {
        RobotController rc = G.rc;
        int[] ids = rc.senseNearbyIslands();
        for (int i = ids.length; --i >= 0; ) {
            int id = ids[i];
            if (id <= 0 || id >= 40) continue;
            Team t = rc.senseTeamOccupyingIsland(id);
            int owner = t == G.us ? 1 : t == G.them ? 2 : 0;
            if (islandTile[id] == null || islandSeen[id] < G.round - 50) {
                MapLocation[] locs = rc.senseNearbyIslandLocations(id);
                if (locs.length > 0) islandTile[id] = G.nearest(G.here, locs);
            }
            islandOwner[id] = owner;
            islandSeen[id] = G.round;
            if (islandTile[id] != null) Comms.reportIsland(id, owner, islandTile[id]);
        }
    }

    /** Publish islands this robot has seen in the last C.ISLAND_FRESH rounds. Island slots carry no timestamp, so an
     *  older observation would overwrite newer news (audit ISL-1: a 60-round window let carriers republish
     *  "neutral" over an island anchored since, and "ours" over one the enemy had taken). */
    public static void flushIslands(int reserve) throws GameActionException {
        if (!Comms.canWrite) return;
        for (int id = 1; id < 40; id++) {
            if (Clock.getBytecodesLeft() < reserve) return;
            if (islandTile[id] == null) continue;
            int age = G.round - islandSeen[id];
            // fresh sightings may overwrite (owner news); older ones (up to 60 rounds, g_iter0's window) only fill an
            // EMPTY slot: the 8-round rule alone kept islands seen far from a writer out of the shared array, and
            // anchor carriers chose far or duplicate targets (self-play Maze vs g_iter0: 2 placed vs 6)
            if (age > 60 || (age > C.ISLAND_FRESH && Comms.read(Comms.ISLANDS + id) != 0)) continue;
            Comms.reportIsland(id, islandOwner[id], islandTile[id]);
        }
    }

    // ---------------------------------------------------------------- symmetry
    public static int imgX(int s, int x) { return s == FLIP_Y ? x : G.W - 1 - x; }

    public static int imgY(int s, int y) { return s == FLIP_X ? y : G.H - 1 - y; }

    public static MapLocation img(int s, MapLocation l) { return new MapLocation(imgX(s, l.x), imgY(s, l.y)); }

    static Direction imgDir(int s, Direction d) {
        int dx = d.dx, dy = d.dy;
        if (s != FLIP_Y) dx = -dx;
        if (s != FLIP_X) dy = -dy;
        for (int i = 8; --i >= 0; ) if (G.DIRS[i].dx == dx && G.DIRS[i].dy == dy) return G.DIRS[i];
        return Direction.CENTER;
    }

    static void checkTile(int x, int y) {
        int c = tile[x + y * G.W];
        for (int s = 1; s <= 4; s <<= 1) {
            if ((cand & s) == 0) continue;
            int ix = imgX(s, x), iy = imgY(s, y);
            int o = tile[ix + iy * G.W];
            if ((o & 1) == 0) continue;
            boolean bad = (c & 6) != (o & 6);
            if (!bad) {
                int cc = (c >> 3) & 15, oc = (o >> 3) & 15;
                if ((cc == 0) != (oc == 0)) bad = true;
                else if (cc != 0 && imgDir(s, G.DIRS[cc - 1]).ordinal() != oc - 1) bad = true;
            }
            if (bad) eliminate(s, 1, x, y);
        }
    }

    static void checkWell(int x, int y, int t) {
        for (int s = 1; s <= 4; s <<= 1) {
            if ((cand & s) == 0) continue;
            int ix = imgX(s, x), iy = imgY(s, y);
            int o = tile[ix + iy * G.W];
            if ((o & 1) == 0 || !G.rc.canSenseLocation(new MapLocation(ix, iy))) continue;
            // a sensed image tile with no well contradicts s (well types can convert, so only presence is compared)
            if (((o >> 7) & 3) == 0) eliminate(s, 2, x, y);
        }
    }

    /** Eliminate candidate s on evidence ev (SYM record: 1 tile, 2 well, 3 enemy HQ seen, 4 predicted HQ absent) at (x, y). */
    static void eliminate(int s, int ev, int x, int y) {
        if ((cand & ~s) == 0) { symConflicts++; if (C.TELEMETRY) symHook(s, ev, 1, x * 64 + y + 1); return; }
        cand &= ~s;
        if (C.TELEMETRY) symHook(s, ev, 0, x * 64 + y + 1);
    }

    static void symHook(int s, int ev, int conflict, int at) {
        Telemetry.emitSym(s, ev, cand, conflict, at, G.round, symConflicts);
    }

    private static int lastConflictElim = -1;   // telemetry: comms conflicts are recorded once per team mask

    /** Enemy HQ evidence: a seen enemy HQ must be an image of one of ours; a predicted image seen empty kills it. */
    static void observeHQs() throws GameActionException {
        MapLocation[] ours = HQState.ourHQs;
        // before round 2 the list of our HQs is incomplete (HQs register on their round-1 turn, in turn order), and an
        // enemy HQ that is the image of a not-yet-registered HQ of ours would wrongly eliminate the true symmetry
        // (foundation2 census: Sine, both sides, symWrong 1, decided at round 1)
        if (ours == null || ours.length == 0 || G.round < 2) return;
        RobotController rc = G.rc;
        for (int i = G.enemies.length; --i >= 0; ) {
            RobotInfo ri = G.enemies[i];
            if (ri.type != RobotType.HEADQUARTERS) continue;
            boolean known = false;
            for (int k = nEnemyHQSeen; --k >= 0; ) if (enemyHQSeen[k].equals(ri.location)) known = true;
            if (!known && nEnemyHQSeen < 4) enemyHQSeen[nEnemyHQSeen++] = ri.location;
            for (int s = 1; s <= 4; s <<= 1) {
                if ((cand & s) == 0) continue;
                boolean match = false;
                for (int k = ours.length; --k >= 0; ) if (img(s, ours[k]).equals(ri.location)) match = true;
                if (!match) eliminate(s, 3, ri.location.x, ri.location.y);
            }
        }
        if (cand == 1 || cand == 2 || cand == 4) return;
        for (int s = 1; s <= 4; s <<= 1) {
            if ((cand & s) == 0) continue;
            for (int k = ours.length; --k >= 0; ) {
                MapLocation p = img(s, ours[k]);
                if (!rc.canSenseLocation(p)) continue;
                RobotInfo r = rc.senseRobotAtLocation(p);
                if (r == null || r.type != RobotType.HEADQUARTERS || r.team != G.them) { eliminate(s, 4, p.x, p.y); break; }
            }
        }
    }

    /** True when one candidate survives, or every survivor predicts the same set of enemy HQs (then the choice
     *  cannot matter for any HQ-based decision; terrain may still differ). */
    public static boolean decided() {
        if (cand == 1 || cand == 2 || cand == 4) return true;
        MapLocation[] ours = HQState.ourHQs;
        if (ours == null || ours.length == 0 || G.round < 2) return false;
        int first = -1;
        for (int s = 1; s <= 4; s <<= 1) {
            if ((cand & s) == 0) continue;
            if (first < 0) { first = s; continue; }
            for (int k = ours.length; --k >= 0; ) {
                MapLocation p = img(s, ours[k]);
                boolean found = false;
                for (int j = ours.length; --j >= 0; ) if (img(first, ours[j]).equals(p)) found = true;
                if (!found) return false;
            }
        }
        return true;
    }

    /** Merge with the team's eliminations and publish ours when we can write. */
    public static void syncSym() throws GameActionException {
        int teamElim = Comms.symEliminated();
        int merged = cand & ~teamElim;
        if (merged != 0) {
            int was = cand;
            cand = merged;
            if (C.TELEMETRY && merged != was) Telemetry.emitSym(was & teamElim, 5, cand, 0, 0, G.round, symConflicts);
        } else {
            symConflicts++;
            if (C.TELEMETRY && teamElim != lastConflictElim) { lastConflictElim = teamElim; Telemetry.emitSym(cand & teamElim, 5, cand, 1, 0, G.round, symConflicts); }
        }
        int mine = 7 & ~cand;
        if (Comms.canWrite && (mine & ~published) != 0) { Comms.publishSym(mine); published |= mine; }
        if (decidedRound < 0 && decided()) decidedRound = G.round;
    }

    /** Predicted enemy HQ locations under the surviving candidates (seen ones first). */
    public static MapLocation[] enemyHQs() {
        if (nEnemyHQSeen > 0 && HQState.ourHQs != null && nEnemyHQSeen >= HQState.ourHQs.length) {
            MapLocation[] out = new MapLocation[nEnemyHQSeen];
            System.arraycopy(enemyHQSeen, 0, out, 0, nEnemyHQSeen);
            return out;
        }
        MapLocation[] ours = HQState.ourHQs;
        if (ours == null) return new MapLocation[0];
        int n = 0;
        for (int s = 1; s <= 4; s <<= 1) if ((cand & s) != 0) n += ours.length;
        MapLocation[] out = new MapLocation[n];
        n = 0;
        for (int s = 1; s <= 4; s <<= 1) if ((cand & s) != 0) for (int k = 0; k < ours.length; k++) out[n++] = img(s, ours[k]);
        return out;
    }

    public static boolean isWall(int x, int y) { return tile != null && (tile[x + y * G.W] & 2) != 0; }

    public static boolean known(int x, int y) { return tile != null && (tile[x + y * G.W] & 1) != 0; }

    public static Direction current(int x, int y) {
        if (tile == null) return Direction.CENTER;
        int c = (tile[x + y * G.W] >> 3) & 15;
        return c == 0 ? Direction.CENTER : G.DIRS[c - 1];
    }

    public static boolean cloud(int x, int y) { return tile != null && (tile[x + y * G.W] & 4) != 0; }
}
