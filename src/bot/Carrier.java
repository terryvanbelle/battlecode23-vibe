package bot;

import battlecode.common.*;

/**
 * Carrier: the economy and the anchor courier.
 *
 * Roles: role 1 mines adamantium, role 2 mana (mana pays for launchers, adamantium for carriers and anchors).
 * Rates (RULES): 1 kg per collect at a standard well, one collect per turn at multiplier 1.0; capacity 40; move
 * cooldown floor(5 + 3m/8) by load. Full loads give the most kg per trip, so carriers fill up before returning.
 * Priorities each turn: anchor delivery > survival (flee armed enemies; throw the load only when cornered) >
 * delivering a full load > taking an anchor waiting at the HQ > gathering.
 */
public final class Carrier {
    static int role;
    static MapLocation well;
    static int crowdTurns;
    static boolean returning;
    static int anchorIsland;
    static MapLocation anchorTarget;
    static MapLocation exploreTarget;
    static int searchTurns;
    public static int trips, throwsMade, anchorsPlaced, fled;   // diagnostics

    static void run() throws GameActionException {
        RobotController rc = G.rc;
        if (role == 0) role = pickRole();
        MapMem.scan();
        if ((G.round + G.id) % 3 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        reportEnemies();
        if (rc.getNumAnchors(null) > 0) { deliverAnchor(); note(); return; }
        if (survive()) { note(); return; }
        int w = rc.getWeight();
        if (w >= C.CARRIER_RETURN_LOAD) returning = true;
        if (returning || (w > 0 && rc.getRoundNum() > 1900)) deliver();
        else if (!takeAnchor()) gather();
        note();
    }

    static void note() { G.note = (returning ? "R" : "G") + role + (anchorTarget != null ? "K" + anchorIsland : ""); }

    /** Early carriers alternate; later two in three mine mana (launchers are the main spend). Roles adapt at each
     *  delivery to the HQ's stock (deliver()). */
    static int pickRole() {
        return G.round < 60 ? 1 + (G.id & 1) : (G.id % 3 == 0 ? 1 : 2);
    }

    static void reportEnemies() throws GameActionException {
        if (!Comms.canWrite || G.nEnemyFighters == 0) return;
        for (int i = G.enemies.length; --i >= 0; ) {
            RobotInfo e = G.enemies[i];
            if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) { Comms.reportEnemy(e.location); return; }
        }
    }

    /** Flee from armed enemies in vision; throw the load at an adjacent-range fighter when hurt and cornered. */
    static boolean survive() throws GameActionException {
        if (G.nEnemyFighters == 0) return false;
        RobotController rc = G.rc;
        RobotInfo threat = null;
        int bd = Integer.MAX_VALUE;
        for (int i = G.enemies.length; --i >= 0; ) {
            RobotInfo e = G.enemies[i];
            if (e.type != RobotType.LAUNCHER && e.type != RobotType.DESTABILIZER) continue;
            int d = G.here.distanceSquaredTo(e.location);
            if (d < bd) { bd = d; threat = e; }
        }
        if (threat == null) return false;
        int w = rc.getWeight();
        if (w >= 8 && bd <= 9 && rc.getHealth() <= 60 && rc.canAttack(threat.location)) {
            rc.attack(threat.location);   // throws everything: worth it only when the carrier is about to die
            throwsMade++;
            returning = false;
        }
        MapLocation home = HQState.nearest(G.here);
        boolean moved = false;
        if (home != null && home.distanceSquaredTo(threat.location) > G.here.distanceSquaredTo(threat.location))
            moved = Nav.moveTo(home);
        if (!moved) moved = Nav.moveAway(threat.location);
        if (moved) fled++;
        return moved || bd <= 20;
    }

    static void deliver() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation home = HQState.nearest(G.here);
        if (home == null) return;
        if (G.here.distanceSquaredTo(home) > 2) Nav.moveTo(home);
        if (G.rc.getLocation().distanceSquaredTo(home) <= 2) {
            ResourceType[] types = {ResourceType.ADAMANTIUM, ResourceType.MANA, ResourceType.ELIXIR};
            for (int i = 0; i < 3 && rc.isActionReady(); i++) {
                int a = rc.getResourceAmount(types[i]);
                if (a > 0 && rc.canTransferResource(home, types[i], a)) rc.transferResource(home, types[i], a);
            }
            if (rc.getWeight() == 0) {
                returning = false;
                trips++;
                RobotInfo hq = rc.senseRobotAtLocation(home);
                if (hq != null) {
                    int ad = hq.getResourceAmount(ResourceType.ADAMANTIUM), mn = hq.getResourceAmount(ResourceType.MANA);
                    int want = mn + 100 < ad ? 2 : ad + 150 < mn ? 1 : role;   // mine what the HQ is short of
                    if (want != role) { role = want; well = null; }
                }
            }
        }
    }

    /** An empty carrier next to an HQ holding an anchor takes it. */
    static boolean takeAnchor() throws GameActionException {
        RobotController rc = G.rc;
        if (rc.getWeight() != 0) return false;
        MapLocation home = HQState.nearest(G.here);
        if (home == null || G.here.distanceSquaredTo(home) > 2) return false;
        if (rc.canTakeAnchor(home, Anchor.STANDARD)) { rc.takeAnchor(home, Anchor.STANDARD); anchorTarget = null; return true; }
        return false;
    }

    static void gather() throws GameActionException {
        RobotController rc = G.rc;
        if (well == null) well = Comms.nearestWell(G.here, role);
        if (well == null && ++searchTurns > C.WELL_SEARCH_TURNS) well = Comms.nearestWell(G.here, 0);
        if (well == null) { explore(); return; }
        searchTurns = 0;
        int d = G.here.distanceSquaredTo(well);
        if (d > 2) {
            Nav.moveTo(well);
            d = rc.getLocation().distanceSquaredTo(well);
            if (d <= 8 && d > 2 && !rc.isMovementReady()) crowdTurns++;
            if (d <= 8 && d > 2 && ++crowdTurns > C.WELL_CROWD_PATIENCE) { switchWell(); crowdTurns = 0; }
        }
        if (rc.getLocation().distanceSquaredTo(well) <= 2) {
            crowdTurns = 0;
            while (rc.isActionReady() && rc.getWeight() < 40) {
                int room = 40 - rc.getWeight();
                if (rc.canCollectResource(well, -1)) rc.collectResource(well, -1);
                else if (rc.canCollectResource(well, room)) rc.collectResource(well, room);
                else break;
            }
            if (rc.getWeight() >= C.CARRIER_RETURN_LOAD) returning = true;
        }
    }

    /** Another registered well of the same type, else any type. */
    static void switchWell() throws GameActionException {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
            int c = Comms.read(i);
            if (c == 0) break;
            MapLocation l = G.dec(c & 0xfff);
            if (l.equals(well)) continue;
            int d = G.here.distanceSquaredTo(l) + ((c >>> 12) == role ? 0 : 400);
            if (d < bd) { bd = d; best = l; }
        }
        if (best != null) well = best;
    }

    static void explore() throws GameActionException {
        if (exploreTarget == null || G.here.distanceSquaredTo(exploreTarget) <= 8 || Nav.stuckOn(exploreTarget)) {
            MapLocation home = HQState.nearest(G.here);
            Direction d = G.DIRS[G.rand(8)];
            int r = 8 + G.rand(8);
            int x = (home == null ? G.here.x : home.x) + d.dx * r, y = (home == null ? G.here.y : home.y) + d.dy * r;
            exploreTarget = new MapLocation(Math.max(0, Math.min(G.W - 1, x)), Math.max(0, Math.min(G.H - 1, y)));
        }
        Nav.moveTo(exploreTarget);
    }

    /** Take the anchor to the nearest island nobody owns; place it on arrival. */
    static void deliverAnchor() throws GameActionException {
        RobotController rc = G.rc;
        int here = rc.senseIsland(G.here);
        if (here > 0 && rc.senseTeamOccupyingIsland(here) == Team.NEUTRAL && rc.canPlaceAnchor()) {
            rc.placeAnchor();
            anchorsPlaced++;
            anchorTarget = null;
            MapMem.islandOwner[here] = 1;
            Comms.reportIsland(here, 1, G.here);
            return;
        }
        if (anchorTarget == null || ownerOf(anchorIsland) != 0) chooseIsland();
        if (anchorTarget == null) { explore(); return; }
        Nav.moveTo(anchorTarget);
        int now = rc.senseIsland(rc.getLocation());
        if (now > 0 && rc.senseTeamOccupyingIsland(now) == Team.NEUTRAL && rc.canPlaceAnchor()) {
            rc.placeAnchor();
            anchorsPlaced++;
            anchorTarget = null;
            MapMem.islandOwner[now] = 1;
            Comms.reportIsland(now, 1, rc.getLocation());
        }
    }

    static int ownerOf(int id) throws GameActionException {
        if (id <= 0) return -1;
        if (MapMem.islandSeen[id] > 0 && G.round - MapMem.islandSeen[id] < 10) return MapMem.islandOwner[id];
        return Comms.islandOwner(id);
    }

    static void chooseIsland() throws GameActionException {
        anchorTarget = null;
        anchorIsland = 0;
        int n = Math.min(35, G.rc.getIslandCount());
        int bd = Integer.MAX_VALUE;
        for (int id = 1; id <= n; id++) {
            MapLocation t = MapMem.islandTile[id];
            if (t == null) t = Comms.islandTile(id);
            if (t == null || ownerOf(id) != 0) continue;
            int d = G.here.distanceSquaredTo(t);
            if (d < bd) { bd = d; anchorTarget = t; anchorIsland = id; }
        }
    }
}
