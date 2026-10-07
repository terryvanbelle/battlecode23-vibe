package c_batch1;

import battlecode.common.*;

/**
 * Launcher: the army. Attack r2 16, vision r2 20, 20 damage per action (one per turn), one move per two turns
 * (move cooldown 20). HQs cannot be damaged (RULES), so they are never targeted.
 *
 * Turn: shoot if a target is in range; if movement is ready, fight (score the 9 tiles) when enemies are visible, else
 * march to the objective; shoot again if the action is still ready after moving.
 * Objective: a fresh enemy sighting (comms) > an enemy-held island (stand on it so its anchor decays) > the predicted
 * enemy HQ (symmetry; stop outside its r2 9 fire).
 */
public final class Launcher {
    public static int shots, steppedIn, kited;   // diagnostics
    static MapLocation objective;

    static void run() throws GameActionException {
        RobotController rc = G.rc;
        MapMem.scan();
        if ((G.round + G.id) % 4 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        report();
        track();
        shoot();
        if (rc.isMovementReady()) {
            if (hasHittableEnemies()) fight();
            else march();
        }
        if (rc.isActionReady()) { G.here = rc.getLocation(); refreshEnemies(); shoot(); }
        G.note = "L";
        G.extra = ",pn=" + pinnedSeen + ",ua=" + unsafeStepsAvoided;
    }

    static void report() throws GameActionException {
        if (!Comms.canWrite) return;
        for (int i = G.enemies.length; --i >= 0; ) {
            RobotInfo e = G.enemies[i];
            if (e.type != RobotType.HEADQUARTERS) { Comms.reportEnemy(e.location); return; }
        }
        if (objective != null && G.here.distanceSquaredTo(objective) <= 8) Comms.clearEnemyNear(objective);
    }

    static boolean hasHittableEnemies() {
        for (int i = G.enemies.length; --i >= 0; ) if (G.enemies[i].type != RobotType.HEADQUARTERS) return true;
        return false;
    }

    static void refreshEnemies() throws GameActionException {
        G.enemies = G.rc.senseNearbyRobots(-1, G.them);
    }

    /** Priority: fighters and anchor-carrying carriers, then amplifiers, then the rest; lowest health first. */
    static int priority(RobotInfo e) {
        switch (e.type) {
            case LAUNCHER: case DESTABILIZER: return 4;
            case CARRIER: return e.getTotalAnchors() > 0 ? 4 : 2;
            case AMPLIFIER: return 3;
            case BOOSTER: return 3;
            default: return 0;
        }
    }

    static void shoot() throws GameActionException {
        RobotController rc = G.rc;
        while (rc.isActionReady()) {
            RobotInfo best = null;
            int bp = -1, bh = Integer.MAX_VALUE;
            for (int i = G.enemies.length; --i >= 0; ) {
                RobotInfo e = G.enemies[i];
                if (e.type == RobotType.HEADQUARTERS || !rc.canAttack(e.location)) continue;
                int p = priority(e);
                if (p > bp || (p == bp && e.health < bh)) { bp = p; bh = e.health; best = e; }
            }
            if (best == null) return;
            rc.attack(best.location);
            shots++;
            refreshEnemies();
        }
    }

    // enemy fighters seen on our previous turn: an enemy that has moved since cannot move on its next turn (launcher
    // move cooldown 20 against a decrement of 10), so it threatens only its attack radius r2 16, not the one-step
    // reach r2 26 (C.THREAT_R2)
    static int[] prevIds = new int[32];
    static MapLocation[] prevLocs = new MapLocation[32];
    static int nPrev, prevRound = -10;
    public static int pinnedSeen, unsafeStepsAvoided;   // diagnostics

    static int[] pinnedIds = new int[32];
    static int nPinned;

    /** Every turn, before acting: which visible enemy fighters moved since our previous turn (pinned for their next
     *  turn), then remember where every visible enemy fighter stands now. */
    static void track() {
        RobotInfo[] es = G.enemies;
        boolean fresh = prevRound == G.round - 1;
        int n = 0, np = 0;
        int[] ids = new int[32];
        MapLocation[] locs = new MapLocation[32];
        for (int i = 0; i < es.length && n < 32; i++) {
            RobotInfo e = es[i];
            if (e.type != RobotType.LAUNCHER && e.type != RobotType.DESTABILIZER) continue;
            if (fresh) for (int k = nPrev; --k >= 0; ) {
                if (prevIds[k] == e.ID) { if (!prevLocs[k].equals(e.location) && np < 32) { pinnedIds[np++] = e.ID; pinnedSeen++; } break; }
            }
            ids[n] = e.ID;
            locs[n++] = e.location;
        }
        nPinned = np;
        prevIds = ids; prevLocs = locs; nPrev = n; prevRound = G.round;
    }

    static boolean isPinned(int id) {
        for (int k = nPinned; --k >= 0; ) if (pinnedIds[k] == id) return true;
        return false;
    }

    /**
     * Score the 9 tiles (lexicographic). threat(tile) = enemy fighters that can hit the tile on their next turn (r2 16 if
     * the enemy is pinned, else r2 26) plus enemy HQs within r2 9.
     * Action ready: step in only to a tile that can hit something AND where at most one enemy can answer, unless we
     * have local superiority (our launchers in vision + 1 > their fighters); among those, fewest threats, then the
     * edge of range. With no acceptable hitting tile: fewest threats, staying put on ties.
     * Action spent: fewest threats, then staying put (moving costs the next turn's move).
     * diag-top4 (2026-10-07): we ended 14-28% of launcher-rounds inside enemy reach against the top bots' 0.3-3%, and
     * took 9-26 damage per contact round against their 3.5-7.7.
     */
    static void fight() throws GameActionException {
        RobotController rc = G.rc;
        boolean ready = rc.isActionReady();
        boolean superior = G.nAllyFighters + 1 > G.nEnemyFighters;
        MapLocation here = rc.getLocation();
        Direction best = Direction.CENTER;
        long bestScore = Long.MIN_VALUE;
        boolean anyCanHit = false;
        for (int k = 0; k < 9; k++) {
            Direction d = G.DIRS9[k];
            if (d != Direction.CENTER && !rc.canMove(d)) continue;
            MapLocation t = here.add(d);
            int threat = 0, minD = Integer.MAX_VALUE;
            boolean canHit = false;
            for (int i = G.enemies.length; --i >= 0; ) {
                RobotInfo e = G.enemies[i];
                int dd = t.distanceSquaredTo(e.location);
                if (e.type == RobotType.HEADQUARTERS) { if (dd <= 9) threat++; continue; }
                if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) {
                    if (dd <= (isPinned(e.ID) ? 16 : C.THREAT_R2)) threat++;
                    if (dd < minD) minD = dd;
                }
                if (dd <= 16) canHit = true;
            }
            long s;
            if (ready) {
                boolean acceptable = canHit && (threat <= 1 || superior);
                if (canHit && !acceptable) unsafeStepsAvoided++;
                if (acceptable) anyCanHit = true;
                s = (acceptable ? 1_000_000L : 0) - threat * 10_000L + Math.min(minD, 100) * 10;
            } else {
                s = -threat * 10_000L + Math.min(minD, 100);
            }
            if (d == Direction.CENTER) s += 50;   // moving costs the next turn's move: stay on ties
            s += G.rand(3);
            if (s > bestScore) { bestScore = s; best = d; }
        }
        if (best != Direction.CENTER) {
            rc.move(best);
            G.here = rc.getLocation();
            if (ready && anyCanHit) steppedIn++; else kited++;
        }
    }

    static void march() throws GameActionException {
        objective = pickObjective();
        if (objective == null) return;
        MapLocation[] ehq = MapMem.enemyHQs();
        // never walk into enemy HQ fire unless there is something to fight there
        for (int i = ehq.length; --i >= 0; ) {
            if (objective.equals(ehq[i]) && G.here.distanceSquaredTo(ehq[i]) <= 16) return;
        }
        Nav.moveTo(objective);
    }

    static MapLocation pickObjective() throws GameActionException {
        MapLocation e = Comms.nearestEnemy(G.here, 2);
        if (e != null) return e;
        int n = Math.min(35, G.rc.getIslandCount());
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int id = 1; id <= n; id++) {
            if (Comms.islandOwner(id) != 2) continue;
            MapLocation t = Comms.islandTile(id);
            if (t == null) continue;
            int d = G.here.distanceSquaredTo(t);
            if (d < bd) { bd = d; best = t; }
        }
        if (best != null) return best;
        MapLocation[] ehq = MapMem.enemyHQs();
        if (ehq.length > 0) return G.nearest(G.here, ehq);
        return new MapLocation(G.W / 2, G.H / 2);
    }
}
