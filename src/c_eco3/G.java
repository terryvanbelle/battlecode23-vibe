package c_eco3;

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
    /** Type-specific counters appended to the indicator (",k=v" pairs); keep the whole string under 64 characters. */
    public static String extra = "";

    // per-turn sensing cache: one senseNearbyRobots call (100 bytecodes) per turn
    public static RobotInfo[] nearby;
    public static RobotInfo[] enemies;   // enemy robots in vision, HQs excluded from enemyFighters
    public static int nEnemyFighters;     // enemy launchers + destabilizers in vision
    public static int nAllyFighters;      // our launchers in vision
    /** Launchers only: the lowest-id launcher of ours in vision (null if none), Launcher.regroup's leader. */
    public static RobotInfo allyLeader;
    /** c_mid1 (C.MID): this launcher is in the contested-well squad (id % C.MID_MOD == 0, set by init; cleared for good
     *  when its tour ends, Launcher.endTour); for squad members only, the launchers of ours in vision with a squad id
     *  (a member whose tour is over still counts) and the lowest-id one (Launcher.midRegroup). */
    public static boolean squad;
    public static int nSquad;
    public static RobotInfo squadLeader;

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
        squad = C.MID && type == RobotType.LAUNCHER && id % C.MID_MOD == 0;
        DEBUG = "true".equals(System.getProperty("bc.testing.debug"));
        // seeded from the id, never from the team: identical code on both sides must not share a sequence
        rng = id * 7919 + 13;
        if (rng == 0) rng = 1;
    }

    public static void startTurn() throws GameActionException {
        round = rc.getRoundNum();
        here = rc.getLocation();
        RobotInfo[] nb = rc.senseNearbyRobots();
        nearby = nb;
        Team th = them;
        int ne = 0, ef = 0, af = 0;
        if (squad) {
            // c_mid1: a squad member's loop also counts the squad launchers in vision and takes the lowest-id one
            // (about 6 more per ally launcher; the other launchers keep the loop below unchanged)
            RobotInfo lead = null, slead = null;
            int lid = Integer.MAX_VALUE, sid = Integer.MAX_VALUE, ns = 0, mod = C.MID_MOD;
            for (int i = nb.length; --i >= 0; ) {
                RobotInfo ri = nb[i];
                if (ri.team == th) {
                    ne++;
                    if (ri.type == RobotType.LAUNCHER || ri.type == RobotType.DESTABILIZER) ef++;
                } else if (ri.type == RobotType.LAUNCHER) {
                    af++;
                    int rid = ri.ID;
                    if (rid < lid) { lid = rid; lead = ri; }
                    if (rid % mod == 0) { ns++; if (rid < sid) { sid = rid; slead = ri; } }
                }
            }
            allyLeader = lead;
            squadLeader = slead;
            nSquad = ns;
        } else if (type == RobotType.LAUNCHER) {
            // bytecodes: launchers also take the lowest-id ally launcher here (about 4 per ally), so Launcher.regroup
            // needs no loop of its own over G.nearby (24 per ally there: 1,650 of a 65-launcher blob's march turn)
            RobotInfo lead = null;
            int lid = Integer.MAX_VALUE;
            for (int i = nb.length; --i >= 0; ) {
                RobotInfo ri = nb[i];
                if (ri.team == th) {
                    ne++;
                    if (ri.type == RobotType.LAUNCHER || ri.type == RobotType.DESTABILIZER) ef++;
                } else if (ri.type == RobotType.LAUNCHER) {
                    af++;
                    if (ri.ID < lid) { lid = ri.ID; lead = ri; }
                }
            }
            allyLeader = lead;
        } else {
            for (int i = nb.length; --i >= 0; ) {
                RobotInfo ri = nb[i];
                if (ri.team == th) {
                    ne++;
                    if (ri.type == RobotType.LAUNCHER || ri.type == RobotType.DESTABILIZER) ef++;
                } else if (ri.type == RobotType.LAUNCHER) af++;
            }
        }
        RobotInfo[] e = new RobotInfo[ne];
        // bytecodes: no copy pass with no enemy in vision (10 per robot for nothing: 750 with 75 robots in a calm blob),
        // and the pass stops at the last enemy it needs; the same array, in nearby's order
        if (ne > 0) for (int i = nb.length; --i >= 0; ) if (nb[i].team == th) { e[--ne] = nb[i]; if (ne == 0) break; }
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
