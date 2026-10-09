package c_def3;

import battlecode.common.*;

/**
 * Amplifier: lets our robots within r2 20 write the shared array. It stays behind the army: at the centre of the
 * launchers it can see, keeping out of enemy fighters' reach (THREAT_R2); with no army in sight it walks toward the
 * freshest enemy sighting from our nearest HQ (where the army is heading) and stops short of it.
 */
public final class Amplifier {
    static void run() throws GameActionException {
        RobotController rc = G.rc;
        MapMem.scan();
        if ((G.round + G.id) % 4 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        for (int i = G.enemies.length; --i >= 0; ) {
            RobotInfo e = G.enemies[i];
            if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) {
                Comms.reportEnemy(e.location);
                if (G.here.distanceSquaredTo(e.location) <= C.THREAT_R2 + 8) {
                    Nav.moveAway(e.location);
                    G.note = String.valueOf(G.nAllyFighters);          // our launchers in vision (= n below)
                    Telemetry.code = Telemetry.ampCode(0, G.nAllyFighters);
                    return;
                }
            }
        }
        int sx = 0, sy = 0, n = 0;
        for (int i = G.nearby.length; --i >= 0; ) {
            RobotInfo r = G.nearby[i];
            if (r.team == G.us && r.type == RobotType.LAUNCHER) { sx += r.location.x; sy += r.location.y; n++; }
        }
        MapLocation goal;
        int mode;                                   // telemetry: 0 F back away, 1 C centroid, 2 S toward a sighting, 3 H home
        if (n > 0) { goal = new MapLocation(sx / n, sy / n); mode = 1; }
        else {
            MapLocation e = Comms.nearestEnemy(G.here, 3);
            MapLocation home = HQState.nearest(G.here);
            if (e != null && home != null) { goal = new MapLocation((e.x + 2 * home.x) / 3, (e.y + 2 * home.y) / 3); mode = 2; }
            else { goal = home; mode = 3; }
        }
        if (goal != null && G.here.distanceSquaredTo(goal) > 4) Nav.moveTo(goal);
        G.note = String.valueOf(n);
        Telemetry.code = Telemetry.ampCode(mode, n);
    }
}
