package c_econ1;

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
        shoot();
        if (rc.isMovementReady()) {
            if (hasHittableEnemies()) fight();
            else march();
        }
        if (rc.isActionReady()) { G.here = rc.getLocation(); refreshEnemies(); shoot(); }
        G.note = objective == null ? "L-" : "L" + objective.x + "," + objective.y;
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

    /**
     * Score the 9 tiles. threat(tile) = enemy fighters within THREAT_R2 (they can reach it next turn) plus enemy HQs
     * within r2 9. With the action ready: a tile that can hit something, fewest threats, then the farthest such tile
     * (hit from the edge of range). With the action spent: fewest threats (kite out of reach), then nearer allies.
     * Outnumbered (enemy fighters > our fighters + 1): fewest threats first regardless.
     */
    static void fight() throws GameActionException {
        RobotController rc = G.rc;
        boolean ready = rc.isActionReady();
        boolean outnumbered = G.nEnemyFighters > G.nAllyFighters + 1;
        MapLocation here = rc.getLocation();
        Direction best = Direction.CENTER;
        long bestScore = Long.MIN_VALUE;
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
                    if (dd <= C.THREAT_R2) threat++;
                    if (dd < minD) minD = dd;
                }
                if (dd <= 16) canHit = true;
            }
            long s;
            if (ready && !outnumbered) s = (canHit ? 1_000_000L : 0) - threat * 10_000L + Math.min(minD, 100) * 10;
            else s = -threat * 10_000L + Math.min(minD, 100) * 10;
            if (d == Direction.CENTER) s += 1;   // prefer not moving on a tie (moves cost two turns)
            s += G.rand(3);
            if (s > bestScore) { bestScore = s; best = d; }
        }
        if (best != Direction.CENTER) {
            rc.move(best);
            G.here = rc.getLocation();
            if (ready) steppedIn++; else kited++;
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
