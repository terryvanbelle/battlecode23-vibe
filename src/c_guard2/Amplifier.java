package c_guard2;

import battlecode.common.*;

/**
 * Amplifier: lets our robots within r2 20 write the shared array. It stays behind the army: at the centre of the
 * launchers it can see, keeping out of enemy fighters' reach (THREAT_R2); with no army in sight it walks toward the
 * freshest enemy sighting from our nearest HQ (where the army is heading) and stops short of it.
 * c_guard2 (C.SENTRY): every amplifier is a sentry: it keeps its HQ's heartbeat bit set and holds a post C.SENTRY_OUT
 * tiles beyond that HQ's nearest mana well (sentryPost), reporting and backing away from fighters as before.
 */
public final class Amplifier {
    /** c_guard2: the tile out tiles beyond the well w on the line from the HQ h, clamped to the map (w itself when h is
     *  w). */
    static MapLocation sentryPost(MapLocation h, MapLocation w, int out, int width, int height) {
        int dx = w.x - h.x, dy = w.y - h.y;
        double n = Math.sqrt(dx * dx + dy * dy);
        if (n == 0) return w;
        int x = (int) Math.round(w.x + dx * out / n), y = (int) Math.round(w.y + dy * out / n);
        return new MapLocation(Math.max(0, Math.min(width - 1, x)), Math.max(0, Math.min(height - 1, y)));
    }

    /** c_guard2: the sentry's HQ index (-2 before its first turn) and its post (null: no well, the army behaviour). */
    static int sentryHq = -2;
    static MapLocation post;

    static void run() throws GameActionException {
        RobotController rc = G.rc;
        MapMem.scan();
        if ((G.round + G.id) % 4 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        if (C.SENTRY) {
            if (sentryHq == -2) {   // first turn: the HQ that built it is adjacent; its nearest shared mana well
                MapLocation home = HQState.nearest(G.here);
                sentryHq = home == null ? -1 : Comms.hqIndex(home);
                MapLocation w = home == null ? null : Comms.nearestWell(home, 2);
                if (w != null) post = sentryPost(home, w, C.SENTRY_OUT, G.W, G.H);
            }
            if (sentryHq >= 0 && !Comms.sentryBeat(sentryHq)) Comms.setSentryBeat(sentryHq, true);
        }
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
        if (C.SENTRY && post != null) {           // c_guard2: hold the post (enemies were reported and fled above)
            if (G.here.distanceSquaredTo(post) > 2) Nav.moveTo(post);
            G.note = "S";
            Telemetry.code = Telemetry.ampCode(3, 0);
            return;
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
