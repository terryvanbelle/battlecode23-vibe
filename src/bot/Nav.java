package bot;

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

    /** Effective squared distance to t after stepping to n and being pushed by n's current (if any). */
    static int score(MapLocation n, MapLocation t) {
        Direction c = MapMem.current(n.x, n.y);
        if (c != Direction.CENTER) {
            int px = n.x + c.dx, py = n.y + c.dy;
            if (G.onMap(px, py) && !MapMem.isWall(px, py)) return G.dist2(px, py, t.x, t.y);
        }
        return n.distanceSquaredTo(t);
    }

    public static boolean moveTo(MapLocation t) throws GameActionException {
        RobotController rc = G.rc;
        if (t == null || !rc.isMovementReady()) return false;
        MapLocation here = rc.getLocation();
        if (here.equals(t)) return false;
        if (target == null || target.distanceSquaredTo(t) > 8) {
            bugging = false;
            bestDist = Integer.MAX_VALUE;
            sinceBest = 0;
        }
        target = t;
        int dHere = score(here, t);
        if (bugging) {
            if (dHere < bugStartDist) bugging = false;
        }
        if (!bugging) {
            Direction dir = here.directionTo(t);
            Direction a = left ? dir.rotateLeft() : dir.rotateRight(), b = left ? dir.rotateRight() : dir.rotateLeft();
            Direction best = null;
            int bs = dHere;
            if (rc.canMove(dir)) { int s = score(here.add(dir), t); if (s < bs) { bs = s; best = dir; } }
            if (rc.canMove(a)) { int s = score(here.add(a), t); if (s < bs) { bs = s; best = a; } }
            if (rc.canMove(b)) { int s = score(here.add(b), t); if (s < bs) { bs = s; best = b; } }
            if (best != null) { step(best, t); return true; }
            // nothing closer: is a wall (or the map edge) in the way, or only robots?
            if (!blockedByWall(here, dir) && !blockedByWall(here, a) && !blockedByWall(here, b)) {
                // robots only: sidestep sideways if that does not lose ground, else wait for them to move
                Direction c1 = left ? dir.rotateLeft().rotateLeft() : dir.rotateRight().rotateRight();
                Direction c2 = c1.opposite();
                if (rc.canMove(c1) && score(here.add(c1), t) <= dHere + 2) { step(c1, t); return true; }
                if (rc.canMove(c2) && score(here.add(c2), t) <= dHere + 2) { step(c2, t); return true; }
                return false;
            }
            bugging = true;
            bugEntries++;
            bugStartDist = dHere;
            bugDir = dir;
        }
        // wall-following: rotate away from the wall until a step is free; afterwards look back toward the wall first
        Direction d = bugDir;
        for (int i = 0; i < 8; i++) {
            if (rc.canMove(d)) {
                step(d, t);
                bugDir = left ? d.rotateLeft().rotateLeft() : d.rotateRight().rotateRight();
                return true;
            }
            d = left ? d.rotateRight() : d.rotateLeft();
        }
        return false;
    }

    static void step(Direction d, MapLocation t) throws GameActionException {
        G.rc.move(d);
        G.here = G.rc.getLocation();
        int s = score(G.here, t);
        if (s < bestDist) { bestDist = s; sinceBest = 0; }
        else if (++sinceBest > STALL_LIMIT) {     // stuck circling: flip the hand and start afresh
            left = !left;
            bugging = false;
            bestDist = s;
            sinceBest = 0;
            stallFlips++;
        }
    }

    static boolean blockedByWall(MapLocation here, Direction d) throws GameActionException {
        MapLocation n = here.add(d);
        if (!G.rc.onTheMap(n)) return true;
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
            if (!rc.canMove(d)) continue;
            int s = score(here.add(d), from);
            if (s > bs) { bs = s; best = d; }
        }
        if (best == null) return false;
        rc.move(best);
        G.here = rc.getLocation();
        return true;
    }
}
