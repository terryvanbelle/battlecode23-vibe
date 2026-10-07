package c_micro1;

import battlecode.common.*;

/** Boosters and destabilizers (not built in g_iter0): stay with the army or at home. */
public final class Other {
    static void run() throws GameActionException {
        MapMem.scan();
        MapMem.syncSym();
        RobotController rc = G.rc;
        if (G.type == RobotType.BOOSTER && rc.isActionReady() && G.nAllyFighters >= 2 && rc.canBoost()) rc.boost();
        if (G.type == RobotType.DESTABILIZER && rc.isActionReady()) {
            for (int i = G.enemies.length; --i >= 0; ) {
                if (rc.canDestabilize(G.enemies[i].location)) { rc.destabilize(G.enemies[i].location); break; }
            }
        }
        MapLocation e = Comms.nearestEnemy(G.here, 2);
        if (e != null) Nav.moveTo(e);
        else Nav.moveTo(HQState.nearest(G.here));
    }
}
