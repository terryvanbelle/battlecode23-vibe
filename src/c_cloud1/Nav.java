package c_cloud1;

import battlecode.common.*;

/**
 * Movement: greedy steps scored after the end-of-round current push, then wall-following (bug) when a wall blocks.
 *
 * - Currents push every robot at the END of the round (GameWorld.applyCurrents): a step onto a current tile is scored
 *   at the push destination, so a current toward the target is a free step and one away from it is avoided.
 * - Robots are temporary obstacles: a robot in the way triggers a sidestep or a wait, never wall-following.
 * - Wall-following keeps the wall on one hand (handedness from the robot id, so both teams' identical code do not
 *   mirror each other), leaves bug mode once strictly closer than where it started, and flips handedness after
 *   STALL_LIMIT moves without a new best distance (the stall survives small target changes: a target that moves by
 *   dist2 <= 8 keeps the bug state).
 */
public final class Nav {
    static MapLocation target;
    static boolean bugging, left;
    static Direction bugDir;
    static int bugStartDist, bestDist, sinceBest;
    public static int bugEntries, stallFlips;   // diagnostic counters
    static final int STALL_LIMIT = 24;

    static { left = false; }

    public static void init() { left = (G.id & 1) == 0; }

    /** arch_swarm: while set (launchers marching), tiles within r2 9 of a seen enemy HQ count as walls: a launcher never
     *  ends a move inside an enemy HQ aura (it fires into it only from Launcher.fight, and only for a kill). */
    public static boolean avoid;

    static boolean aura(MapLocation n) {
        if (!avoid) return false;
        for (int k = MapMem.nEnemyHQSeen; --k >= 0; ) if (MapMem.enemyHQSeen[k].distanceSquaredTo(n) <= 9) return true;
        return false;
    }

    static boolean can(Direction d) throws GameActionException {
        return G.rc.canMove(d) && (!avoid || !aura(G.rc.getLocation().add(d)));
    }

    /** Effective squared distance to t after stepping to n and being pushed by n's current (if any). */
    static int score(MapLocation n, MapLocation t) {
        Direction c = MapMem.current(n.x, n.y);
        if (c != Direction.CENTER) {
            int px = n.x + c.dx, py = n.y + c.dy;
            if (G.onMap(px, py) && !MapMem.isWall(px, py)) return G.dist2(px, py, t.x, t.y);
        }
        return n.distanceSquaredTo(t);
    }

    // bug state (per target): the hand is kept for the whole obstacle; a flip happens only at the map edge or after a
    // budget proportional to the map's size (the old 24-move stall flip made launchers oscillate along long walls:
    // calib-g_iter0, ReverseFunnel, launchers moving 46% of turns for 130+ rounds without crossing the wall)
    static int bugMoves, bugFlips;
    static MapLocation dbgPos; static int dbgStill;
    static boolean fieldOn;   // c_nav4: greedy hit a wall on the way to fieldFor: descend its field from now on
    static MapLocation fieldFor;
    static int fieldWaits;   // c_nav3: turns waited behind robots on the field's path
    public static int wallHits, edgeFlips, budgetFlips;   // counters (indicator)
    // telemetry only (BUG record): where and when the current wall-following episode started, and its moves
    static MapLocation bugStart;
    static int bugStartRound, bugEpMoves;

    public static boolean moveTo(MapLocation t) throws GameActionException {
        RobotController rc = G.rc;
        if (t == null || !rc.isMovementReady()) return false;
        MapLocation here = rc.getLocation();
        if (here.equals(t)) return false;
        if (target == null || target.distanceSquaredTo(t) > 8) {
            if (C.TELEMETRY && bugging) bugEnd(2, target == null ? 0 : here.distanceSquaredTo(target));
            bugging = false;
            bugFlips = 0;
            bestDist = Integer.MAX_VALUE;
            sinceBest = 0;
        }
        target = t;
        if (G.DEBUG) {
            if (here.equals(dbgPos)) { if (++dbgStill == 25) System.out.println("STUCK r" + G.round + " #" + G.id + " at " + here + " t=" + t
                + " field=" + Field.target + " ready=" + Field.ready(t) + " n=" + Field.nWaves + " done=" + Field.done + " pend=" + Field.pending
                + " stale=" + Field.stale + " lvl=" + (Field.target != null && Field.nWaves > 0 ? Field.level(here.x, here.y) : -9)
                + " vis=" + (Field.vis != null && (Field.vis[here.y] >>> here.x & 1) != 0) + " blkHere=" + (Field.blk != null && (Field.blk[here.y] >>> here.x & 1) != 0) + " bug=" + bugging + " flips=" + bugFlips
                + " used=" + Field.usedRound + " fields=" + Field.fields + " restarts=" + Field.restarts); }
            else { dbgPos = here; dbgStill = 0; }
        }
        // c_nav3: a ready distance field toward t (or toward a target within r2 C.FIELD_NEAR_D2 of t while t is still
        // far): step to a free neighbour one wave nearer (ties: the score)
        MapLocation ft = Field.target;
        // c_nav4: only after greedy hit a wall on the way to this target (fieldOn, sticky until the field's target
        // changes): c_nav3 descended every field from the first turn and lost 9-11 in self-play on open maps
        boolean viaField = ft != null && fieldOn && ft.equals(fieldFor)
            && (ft.equals(t) || (ft.distanceSquaredTo(t) <= C.FIELD_NEAR_D2 && here.distanceSquaredTo(t) > C.FIELD_FAR_D2));
        if (viaField && Field.ready(ft) && Clock.getBytecodesLeft() > C.FIELD_LEVEL_GUARD) {   // c_nav5: guarded
            int k = Field.level(here.x, here.y);
            if (k > 0) {
                long[] up = Field.waves[k - 1], same = Field.waves[k];
                long[] back = k + 1 < Field.nWaves ? Field.waves[k + 1] : null;
                boolean wallDown = false;   // a downhill square turned out to be a wall: the field is out of date
                Direction down = null, side = null, up2 = null;
                int ds = Integer.MAX_VALUE, ss = Integer.MAX_VALUE;
                for (int i = 8; --i >= 0; ) {
                    Direction d = G.DIRS[i];
                    int nx = here.x + d.dx, ny = here.y + d.dy;
                    if (nx < 0 || ny < 0 || nx >= G.W || ny >= G.H) continue;
                    long bit = 1L << nx;
                    boolean isUp = (up[ny] & bit) != 0, isSame = (same[ny] & bit) != 0;
                    if (!isUp && !isSame && (back == null || (back[ny] & bit) == 0)) continue;
                    if (!can(d) || pushesBack(here.add(d), here)) {
                        if (isUp && MapMem.isWall(nx, ny)) wallDown = true;
                        continue;
                    }
                    int s = score(here.add(d), ft);
                    if (isUp) { if (s < ds) { ds = s; down = d; } }
                    else if (isSame) { if (s < ss) { ss = s; side = d; } }
                    else up2 = d;
                }
                // downhill; behind robots, wait two turns, then sidestep on the same wave, then (a jam in a corridor:
                // robots going both ways) step back one wave every other turn
                Direction go = down != null ? down : side;
                if (go == null && fieldWaits >= 2 && (fieldWaits & 1) == 0) go = up2;
                if (go != null) {
                    Field.usedRound = G.round;
                    Field.descents++;
                    if (go == down) fieldWaits = 0; else fieldWaits++;
                    if (bugging) { if (C.TELEMETRY) bugEnd(1, dHere0(here, t)); bugging = false; }
                    step(go, t);
                    return true;
                }
                // a stale field is used until it fails here: then it is rebuilt (a rebuild discards it, and robots
                // without one walked into the dead ends again)
                if (down == null && wallDown) { Field.stale = true; Field.request(ft, true); }
                else { fieldWaits++; Field.usedRound = G.round; return false; }   // robots in the way
            }
        }
        int dHere = score(here, t);
        if (bugging && dHere < bugStartDist) { if (C.TELEMETRY) bugEnd(1, dHere); bugging = false; }   // past the obstacle: back to greedy
        if (!bugging) {
            Direction dir = here.directionTo(t);
            Direction a = left ? dir.rotateLeft() : dir.rotateRight(), b = left ? dir.rotateRight() : dir.rotateLeft();
            Direction best = null;
            int bs = dHere;
            if (can(dir)) { int s = score(here.add(dir), t); if (s < bs) { bs = s; best = dir; } }
            if (can(a)) { int s = score(here.add(a), t); if (s < bs) { bs = s; best = a; } }
            if (can(b)) { int s = score(here.add(b), t); if (s < bs) { bs = s; best = b; } }
            if (best != null) { step(best, t); return true; }
            if (!blockedByWall(here, dir) && !blockedByWall(here, a) && !blockedByWall(here, b)) {
                // robots only: sidestep if that does not lose ground, else wait for them to move
                Direction c1 = left ? dir.rotateLeft().rotateLeft() : dir.rotateRight().rotateRight();
                Direction c2 = c1.opposite();
                if (can(c1) && score(here.add(c1), t) <= dHere + 2) { step(c1, t); return true; }
                if (can(c2) && score(here.add(c2), t) <= dHere + 2) { step(c2, t); return true; }
                return false;
            }
            bugging = true;
            if (here.distanceSquaredTo(t) > C.FIELD_MIN_D2) {
                Field.request(t, false);   // c_nav3: plan around the obstacle
                MapLocation f2 = Field.target;
                if (f2 != null && (f2.equals(t) || f2.distanceSquaredTo(t) <= C.FIELD_NEAR_D2)) { fieldOn = true; fieldFor = f2; }
            }
            wallHits++;
            bugEntries++;
            bugStartDist = dHere;
            bugDir = dir;
            bugMoves = 0;
            if (C.TELEMETRY) { bugStart = here; bugStartRound = G.round; bugEpMoves = 0; }
        }
        // wall-following: from the direction pointing back at the wall, rotate away from it until a step is free
        Direction d = bugDir;
        for (int i = 0; i < 8; i++) {
            MapLocation n = here.add(d);
            if (!rc.onTheMap(n)) {
                // the obstacle runs into the map edge: follow it the other way (once per target)
                if (bugFlips < 2) { left = !left; bugFlips++; edgeFlips++; bugDir = d.opposite(); }
                else bugging = false;    // c_nav3: no permanent stall against the map edge (the field takes over)
                return false;
            }
            if (can(d) && !pushesBack(n, here)) {
                step(d, t);
                if (C.TELEMETRY) bugEpMoves++;
                bugDir = left ? d.rotateLeft().rotateLeft() : d.rotateRight().rotateRight();
                if (++bugMoves > 2 * (G.W + G.H)) {       // a full circuit without getting closer: try the other hand
                    left = !left;
                    bugMoves = 0;
                    budgetFlips++;
                    if (++bugFlips > 2) { if (C.TELEMETRY) bugEnd(3, G.here.distanceSquaredTo(t)); bugging = false; }
                }
                return true;
            }
            // a robot on the wall-following path is routed around like a wall (c_nav2: waiting up to 3 turns for it,
            // as c_nav1 did, raised still rounds and cut collection by ~7% on the 174 calibration cells)
            d = left ? d.rotateRight() : d.rotateLeft();
        }
        return false;
    }

    static int dHere0(MapLocation here, MapLocation t) { return here.distanceSquaredTo(t); }

    /** BUG record: a wall-following episode ends (reason 1 closer than where it started, 2 new target, 3 flip budget). */
    static void bugEnd(int reason, int exitD2) {
        Telemetry.emitBug(bugEpMoves, bugFlips, reason, Telemetry.loc12(target), Telemetry.loc12(bugStart), bugStartRound, G.round,
            bugStartDist, exitD2);
    }

    /** A current on n that would carry a robot straight back to `from` makes the step useless. */
    static boolean pushesBack(MapLocation n, MapLocation from) {
        Direction c = MapMem.current(n.x, n.y);
        return c != Direction.CENTER && n.x + c.dx == from.x && n.y + c.dy == from.y;
    }

    static void step(Direction d, MapLocation t) throws GameActionException {
        G.rc.move(d);
        G.here = G.rc.getLocation();
        int s = score(G.here, t);
        if (s < bestDist) { bestDist = s; sinceBest = 0; }
        else if (!bugging && ++sinceBest > STALL_LIMIT) {   // greedy oscillation (not wall-following): flip the hand
            left = !left;
            bestDist = s;
            sinceBest = 0;
            stallFlips++;
        }
    }

    static boolean blockedByWall(MapLocation here, Direction d) throws GameActionException {
        MapLocation n = here.add(d);
        if (!G.rc.onTheMap(n)) return true;
        if (aura(n)) return true;
        if (MapMem.known(n.x, n.y)) return MapMem.isWall(n.x, n.y);
        return G.rc.canSenseLocation(n) && !G.rc.sensePassability(n);
    }

    /** True when the current target has gone STALL_LIMIT moves without a new best distance at least twice. */
    public static boolean stuckOn(MapLocation t) { return t.equals(target) && stallFlips > 0 && sinceBest > STALL_LIMIT / 2; }

    /** Step to the adjacent tile that maximises distance from `from` (used to flee); returns whether it moved. */
    public static boolean moveAway(MapLocation from) throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isMovementReady() || from == null) return false;
        MapLocation here = rc.getLocation();
        Direction best = null;
        int bs = score(here, from);
        for (int i = 8; --i >= 0; ) {
            Direction d = G.DIRS[i];
            if (!can(d)) continue;
            int s = score(here.add(d), from);
            if (s > bs) { bs = s; best = d; }
        }
        if (best == null) return false;
        rc.move(best);
        G.here = rc.getLocation();
        return true;
    }
}
