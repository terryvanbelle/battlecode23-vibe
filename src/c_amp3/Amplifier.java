package c_amp3;

import battlecode.common.*;

/**
 * c_amp2: the team's one amplifier (HQ.ampGate builds it while the census reads none). Our robots within r2 20 of it
 * can write the shared array: islands, wells, symmetry and the census wherever it goes; enemy sightings only from the
 * zones writable without it (Comms.sightWrite while C.AMP_SIGHTINGS is false), so the sighting objectives stay as today.
 *
 * Turn: count itself in the census (Comms.ampTick); flee enemy fighters within C.THREAT_R2 + 8 (120 HP, no attack).
 * SCOUT, before C.AMP_SCOUT_UNTIL while no located island is neutral and some island is unlocated (Comms.islandStats,
 * every C.AMP_SCOUT_CHECK rounds): toward a random unknown tile away from seen enemy HQs and fresh sightings (and off
 * the enemy side once the symmetry is decided), redrawn on arrival, when stuck or when it turns unsafe; islands are
 * scanned every 2 turns and published at once (an amplifier can always write).
 * ESCORT (C.AMP_RELAY): the centroid of the launchers in view, else 2/3 of the way from our HQ centroid to the siege
 * target, where the army is (not toward a sighting or home); without C.AMP_RELAY it goes home after scouting.
 * Every move avoids seen enemy HQ auras (Nav.avoid); a goal inside one counts as reached within r2 C.RING_MAX.
 * Telemetry (ampCode, format unchanged): 0 F flee, 1 C centroid, 2 S toward the escort point, 3 H scout or home
 * (with C.AMP_RELAY on, 3 is the scout phase: the escort goes home only before an enemy HQ is predicted).
 */
public final class Amplifier {
    static MapLocation scoutTarget;
    static int scoutCheck;
    static boolean scoutNeed;

    static void run() throws GameActionException {
        Comms.ampTick();
        MapMem.scan();
        boolean scout = scouting();
        if (scout ? (G.round & 1) == 0 : (G.round + G.id) % 4 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        for (int i = G.enemies.length; --i >= 0; ) {
            RobotInfo e = G.enemies[i];
            if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) {
                Comms.reportEnemy(e.location);                       // only from an HQ zone (Comms.sightWrite)
                if (G.here.distanceSquaredTo(e.location) <= C.THREAT_R2 + 8) {
                    Nav.avoid = true;
                    Nav.moveAway(e.location);
                    Nav.avoid = false;
                    G.note = String.valueOf(G.nAllyFighters);          // our launchers in vision (= n below)
                    Telemetry.code = Telemetry.ampCode(0, G.nAllyFighters);
                    return;
                }
            }
        }
        if (scout) {
            scoutMove();
            G.note = String.valueOf(G.nAllyFighters);
            Telemetry.code = Telemetry.ampCode(3, G.nAllyFighters);
            return;
        }
        int sx = 0, sy = 0, n = 0;
        for (int i = G.nearby.length; --i >= 0; ) {
            RobotInfo r = G.nearby[i];
            if (r.team == G.us && r.type == RobotType.LAUNCHER) { sx += r.location.x; sy += r.location.y; n++; }
        }
        MapLocation goal;
        int mode;
        if (!C.AMP_RELAY) { goal = HQState.nearest(G.here); mode = 3; }
        else if (n > 0) { goal = new MapLocation(sx / n, sy / n); mode = 1; }
        else {
            MapLocation[] ehq = Launcher.enemyHQs();
            if (ehq.length > 0) { goal = escortPoint(Launcher.ourCentroid(), Launcher.siegeTarget(ehq)); mode = 2; }
            else { goal = HQState.nearest(G.here); mode = 3; }
        }
        MapLocation h = Nav.auraOf(G.here);
        Nav.avoid = true;
        if (h != null) Nav.moveAway(h);                              // inside a seen enemy HQ aura: step out first
        else if (goal != null && G.here.distanceSquaredTo(goal) > (Nav.auraOf(goal) != null ? C.RING_MAX : 4)) Nav.moveTo(goal);
        Nav.avoid = false;
        G.note = String.valueOf(n);
        Telemetry.code = Telemetry.ampCode(mode, n);
    }

    /** Scout phase test, refreshed every C.AMP_SCOUT_CHECK rounds (islandStats: one pass over the island slots). */
    static boolean scouting() throws GameActionException {
        if (G.round >= C.AMP_SCOUT_UNTIL) return false;
        if (G.round >= scoutCheck) {
            scoutCheck = G.round + C.AMP_SCOUT_CHECK;
            Comms.islandStats(G.rc.getIslandCount());
            scoutNeed = scoutWanted(G.round, Comms.islLocNeutral, Comms.islUnloc);
        }
        return scoutNeed;
    }

    /** c_amp2 (pure): scout while before C.AMP_SCOUT_UNTIL no located island is neutral and some island is unlocated. */
    static boolean scoutWanted(int round, int locNeutral, int unloc) {
        return round < C.AMP_SCOUT_UNTIL && locNeutral == 0 && unloc > 0;
    }

    static void scoutMove() throws GameActionException {
        MapLocation[] ehq = Launcher.enemyHQs();
        boolean decided = MapMem.decided();
        MapLocation t = scoutTarget;
        if (t == null || G.here.distanceSquaredTo(t) <= 8 || Nav.stuckOn(t) || !acceptable(t, ehq, decided))
            scoutTarget = t = drawTarget(ehq, decided);
        if (t == null) return;                                       // nothing safe drawn: hold, draw again next turn
        Nav.avoid = true;
        Nav.moveTo(t);
        Nav.avoid = false;
    }

    /** Up to C.AMP_SCOUT_DRAWS random tiles: the first acceptable one this robot has not seen, else the first acceptable
     *  one, else null. */
    static MapLocation drawTarget(MapLocation[] ehq, boolean decided) throws GameActionException {
        MapLocation fallback = null;
        for (int i = 0; i < C.AMP_SCOUT_DRAWS; i++) {
            MapLocation t = new MapLocation(G.rand(G.W), G.rand(G.H));
            if (!acceptable(t, ehq, decided)) continue;
            if (!MapMem.known(t.x, t.y)) return t;
            if (fallback == null) fallback = t;
        }
        return fallback;
    }

    /** Safe (scoutSafe against the seen enemy HQs and the nearest sighting at most 1 stamp old) and, once the symmetry
     *  is decided, not on the enemy side (Carrier.enemySide: nearer a predicted enemy HQ than our nearest HQ). */
    static boolean acceptable(MapLocation t, MapLocation[] ehq, boolean decided) throws GameActionException {
        return scoutSafe(t, MapMem.enemyHQSeen, MapMem.nEnemyHQSeen, Comms.nearestEnemy(t, 1))
            && !(decided && Carrier.enemySide(t, ehq));
    }

    /** c_amp2 (pure): a scout target farther than r2 C.AMP_SCOUT_AVOID_R2 from every seen enemy HQ (the first nSeen of
     *  seenHQ) and from the given sighting (null = none). */
    static boolean scoutSafe(MapLocation t, MapLocation[] seenHQ, int nSeen, MapLocation sighting) {
        for (int k = nSeen; --k >= 0; ) if (seenHQ[k].distanceSquaredTo(t) <= C.AMP_SCOUT_AVOID_R2) return false;
        return sighting == null || sighting.distanceSquaredTo(t) > C.AMP_SCOUT_AVOID_R2;
    }

    /** c_amp2 (pure): the escort point, 2/3 of the way from `from` (our HQ centroid) to `to` (the siege target). */
    static MapLocation escortPoint(MapLocation from, MapLocation to) {
        return new MapLocation((from.x + 2 * to.x) / 3, (from.y + 2 * to.y) / 3);
    }
}
