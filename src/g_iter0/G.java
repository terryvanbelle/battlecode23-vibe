package g_iter0;

import battlecode.common.*;

/**
 * Per-robot globals (statics are per robot: every robot runs in its own JVM sandbox, so nothing here is shared).
 * Holds the controller, identity, map size, the per-turn sensing cache, a private RNG and the health counters that
 * the indicator string reports.
 */
public final class G {
    public static RobotController rc;
    public static int id, W, H, round, spawnRound;
    public static Team us, them;
    public static RobotType type;
    public static MapLocation here;

    // health counters reported in the indicator string (tools/replay-dump.sh --census sums them per team)
    public static int overruns, exceptions, maxBc, nearMiss;
    /** -Dbc.testing.debug=true (only bc.testing.* properties are readable by bots): print caught exceptions. */
    public static boolean DEBUG;
    public static String note = "";

    // per-turn sensing cache: one senseNearbyRobots call (100 bytecodes) per turn
    public static RobotInfo[] nearby;
    public static RobotInfo[] enemies;   // enemy robots in vision, HQs excluded from enemyFighters
    public static int nEnemyFighters;     // enemy launchers + destabilizers in vision
    public static int nAllyFighters;      // our launchers in vision

    public static final Direction[] DIRS = {Direction.NORTH, Direction.NORTHEAST, Direction.EAST, Direction.SOUTHEAST,
        Direction.SOUTH, Direction.SOUTHWEST, Direction.WEST, Direction.NORTHWEST};
    public static final Direction[] DIRS9 = {Direction.CENTER, Direction.NORTH, Direction.NORTHEAST, Direction.EAST,
        Direction.SOUTHEAST, Direction.SOUTH, Direction.SOUTHWEST, Direction.WEST, Direction.NORTHWEST};

    private static int rng;

    public static void init(RobotController r) {
        rc = r;
        id = r.getID();
        us = r.getTeam();
        them = us.opponent();
        type = r.getType();
        W = r.getMapWidth();
        H = r.getMapHeight();
        spawnRound = r.getRoundNum();
        DEBUG = "true".equals(System.getProperty("bc.testing.debug"));
        // seeded from the id, never from the team: identical code on both sides must not share a sequence
        rng = id * 7919 + 13;
        if (rng == 0) rng = 1;
    }

    public static void startTurn() throws GameActionException {
        round = rc.getRoundNum();
        here = rc.getLocation();
        nearby = rc.senseNearbyRobots();
        int ne = 0, ef = 0, af = 0;
        for (int i = nearby.length; --i >= 0; ) {
            RobotInfo ri = nearby[i];
            if (ri.team == them) {
                ne++;
                if (ri.type == RobotType.LAUNCHER || ri.type == RobotType.DESTABILIZER) ef++;
            } else if (ri.type == RobotType.LAUNCHER) af++;
        }
        RobotInfo[] e = new RobotInfo[ne];
        for (int i = nearby.length; --i >= 0; ) if (nearby[i].team == them) e[--ne] = nearby[i];
        enemies = e;
        nEnemyFighters = ef;
        nAllyFighters = af;
    }

    /** xorshift32: cheap and deterministic per robot. */
    public static int rand() {
        int x = rng;
        x ^= x << 13;
        x ^= x >>> 17;
        x ^= x << 5;
        rng = x;
        return x & 0x7fffffff;
    }

    public static int rand(int n) { return rand() % n; }

    public static int enc(MapLocation l) { return l.x * 64 + l.y + 1; }          // 0 = none; fits in 12 bits + 1

    public static MapLocation dec(int v) { return v <= 0 ? null : new MapLocation((v - 1) / 64, (v - 1) % 64); }

    public static int dist2(int x1, int y1, int x2, int y2) { int dx = x1 - x2, dy = y1 - y2; return dx * dx + dy * dy; }

    /** Chebyshev distance: the number of moves between two tiles on an open board. */
    public static int cheb(MapLocation a, MapLocation b) { return Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y)); }

    public static boolean onMap(int x, int y) { return x >= 0 && y >= 0 && x < W && y < H; }

    /** Nearest of a list (null entries skipped); ties broken by the robot's own RNG, never by array order. */
    public static MapLocation nearest(MapLocation from, MapLocation[] locs) {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = locs.length; --i >= 0; ) {
            MapLocation l = locs[i];
            if (l == null) continue;
            int d = from.distanceSquaredTo(l);
            if (d < bd || (d == bd && (rand() & 1) == 0)) { bd = d; best = l; }
        }
        return best;
    }
}
