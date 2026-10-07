package g_iter0;

import battlecode.common.*;

/**
 * Headquarters: registers itself, maps its vision (wells, islands, symmetry evidence), reports threats, and spends.
 * Action cooldown 2 against a decrement of 10: up to 5 builds/anchors per turn (RULES). Resources are per HQ.
 * Spending order each action: anchor (when wanted and affordable) > launcher > carrier (under the cap) > amplifier.
 * Never float: every action that can be afforded is taken, except what an anchor in preparation reserves.
 */
public final class HQ {
    static int carriersBuilt, launchersBuilt, ampsBuilt, anchorsBuilt;
    static int lastAnchorRound = -1000;
    static MapLocation[] spawnTiles;
    public static int floatRounds;      // rounds ending with >= 200 of a resource unspent (diagnostic)

    static void run() throws GameActionException {
        RobotController rc = G.rc;
        if (spawnTiles == null) {
            Comms.registerHQ(G.here);
            spawnTiles = rc.getAllLocationsWithinRadiusSquared(G.here, 9);
        }
        MapMem.scan();
        if (G.round % 8 == 1) MapMem.scanIslands();
        MapMem.syncSym();
        if (G.nEnemyFighters > 0) {
            for (int i = G.enemies.length; --i >= 0; ) {
                RobotInfo e = G.enemies[i];
                if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) { Comms.reportEnemy(e.location); break; }
            }
        }
        build();
        if (rc.getResourceAmount(ResourceType.MANA) >= 200 || rc.getResourceAmount(ResourceType.ADAMANTIUM) >= 200) floatRounds++;
        G.note = "C" + carriersBuilt + "L" + launchersBuilt + "A" + ampsBuilt + "K" + anchorsBuilt;
    }

    static void build() throws GameActionException {
        RobotController rc = G.rc;
        boolean threatened = G.nEnemyFighters > 0;
        for (int guard = 0; guard < 6 && rc.isActionReady(); guard++) {
            int ad = rc.getResourceAmount(ResourceType.ADAMANTIUM), mn = rc.getResourceAmount(ResourceType.MANA);
            boolean wantAnchor = !threatened && G.round >= C.ANCHOR_START && launchersBuilt >= C.ANCHOR_MIN_LAUNCHERS
                && rc.getNumAnchors(Anchor.STANDARD) == 0 && G.round - lastAnchorRound >= C.ANCHOR_PERIOD && islandToTake();
            if (wantAnchor && ad >= 80 && mn >= 80 && rc.canBuildAnchor(Anchor.STANDARD)) {
                rc.buildAnchor(Anchor.STANDARD);
                anchorsBuilt++;
                lastAnchorRound = G.round;
                continue;
            }
            int resAd = wantAnchor ? 80 : 0, resMn = wantAnchor ? 80 : 0;
            boolean carrierFirst = !threatened && carriersBuilt <= launchersBuilt && carriersBuilt < carrierCap();
            if (carrierFirst && ad - resAd >= 50 && tryBuild(RobotType.CARRIER)) { carriersBuilt++; continue; }
            if (mn - resMn >= 45 && tryBuild(RobotType.LAUNCHER)) { launchersBuilt++; continue; }
            if (!threatened && ad - resAd >= 50 && carriersBuilt < carrierCap() && tryBuild(RobotType.CARRIER)) { carriersBuilt++; continue; }
            if (!threatened && launchersBuilt >= C.LAUNCHERS_PER_AMP * (ampsBuilt + 1) && ad - resAd >= 30 && mn - resMn >= 15
                && tryBuild(RobotType.AMPLIFIER)) { ampsBuilt++; continue; }
            break;
        }
    }

    static int carrierCap() {
        return Math.min(C.CARRIER_MAX, C.CARRIER_BASE + G.round / C.CARRIER_PER_ROUNDS);
    }

    /** True if some island is not ours (or islands exist that nobody has reported yet). */
    static boolean islandToTake() throws GameActionException {
        int n = G.rc.getIslandCount();
        for (int id = 1; id <= n && id <= 35; id++) if (Comms.islandOwner(id) != 1) return true;
        return false;
    }

    /** Build on the free spawn tile nearest the unit's purpose: carriers toward wells, others toward the enemy. */
    static boolean tryBuild(RobotType t) throws GameActionException {
        RobotController rc = G.rc;
        MapLocation goal;
        if (t == RobotType.CARRIER) {
            goal = Comms.nearestWell(G.here, 0);
        } else {
            MapLocation[] e = MapMem.enemyHQs();
            goal = e.length > 0 ? G.nearest(G.here, e) : new MapLocation(G.W / 2, G.H / 2);
        }
        if (goal == null) goal = new MapLocation(G.W / 2, G.H / 2);
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = spawnTiles.length; --i >= 0; ) {
            MapLocation l = spawnTiles[i];
            if (!rc.canBuildRobot(t, l)) continue;
            int d = l.distanceSquaredTo(goal);
            if (d < bd) { bd = d; best = l; }
        }
        if (best == null) return false;
        rc.buildRobot(t, best);
        return true;
    }
}
