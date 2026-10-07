package c_batch1;

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
        if (rc.getNumAnchors(null) > 0) { state = 'K'; deliverAnchor(); note(); return; }
        if (survive()) { state = 'F'; note(); return; }
        int w = rc.getWeight();
        if (w >= C.CARRIER_RETURN_LOAD) returning = true;
        if (returning || (w > 0 && rc.getRoundNum() > 1900)) { state = 'R'; deliver(); }
        else if (takeAnchor()) state = 'T';
        else gather();
        note();
    }

    /** State token this turn, first character of the indicator note: G going to a well, C collecting, W waiting at a
     *  crowded well, R returning, D depositing, F fleeing, X exploring for a well, K carrying an anchor, T took an anchor. */
    static char state = '?';

    static void note() { G.note = "" + state + role + (anchorTarget != null ? "k" + anchorIsland : ""); }

    /** Mana first (launchers, the army, cost mana; strong field bots mine mostly mana: camel_case on Risk collected
     *  1,700 Mn and 27 Ad, awesomelemonade on ReverseFunnel 12,186 Mn and 4,521 Ad). The opening alternates so the HQs can
     *  afford carriers; afterwards a carrier mines adamantium only when its HQ is short of it (deliver()). */
    static int pickRole() {
        return G.round < C.OPENING_ROUNDS ? 1 + (G.id & 1) : 2;
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
            state = 'D';
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
                    int want = ad < C.AD_LOW ? 1 : 2;     // adamantium only while this HQ is short of it
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
        if (rc.canTakeAnchor(home, Anchor.STANDARD)) { rc.takeAnchor(home, Anchor.STANDARD); anchorTarget = null; anchorTurns = 0; return true; }
        return false;
    }

    static void gather() throws GameActionException {
        RobotController rc = G.rc;
        if (well == null) well = Comms.nearestWell(G.here, role);
        if (well == null && ++searchTurns > C.WELL_SEARCH_TURNS) well = Comms.nearestWell(G.here, 0);
        if (well == null) { state = 'X'; explore(); return; }
        searchTurns = 0;
        state = 'G';
        int d = G.here.distanceSquaredTo(well);
        if (d > 2) {
            Nav.moveTo(well);
            d = rc.getLocation().distanceSquaredTo(well);
            if (d <= 8 && d > 2) state = 'W';
            if (d <= 8 && d > 2 && !rc.isMovementReady()) crowdTurns++;
            if (d <= 8 && d > 2 && ++crowdTurns > C.WELL_CROWD_PATIENCE) { switchWell(); crowdTurns = 0; }
        }
        if (rc.getLocation().distanceSquaredTo(well) <= 2) {
            crowdTurns = 0;
            state = 'C';
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

    static int anchorTurns;
    public static int anchorsReturned;

    /**
     * Take the anchor to an island nobody owns and place it. Targets on our side of the map first (nearer our HQs than
     * the predicted enemy HQs), the nearest free tile of the island once it is in view, predicted islands (mirror
     * images of known ones) when no free island is known. A carrier that cannot place within C.ANCHOR_TIMEOUT turns
     * brings the anchor home and returns it (foundation2/Forest: 85 anchors taken, 4 placed, the rest carried for the
     * whole game).
     */
    static void deliverAnchor() throws GameActionException {
        RobotController rc = G.rc;
        anchorTurns++;
        if (tryPlace()) return;
        if (anchorTurns > C.ANCHOR_TIMEOUT) {                 // give up: return the anchor so it can be reused
            MapLocation home = HQState.nearest(G.here);
            if (home != null) {
                if (G.here.distanceSquaredTo(home) > 2) moveTwice(home);
                if (rc.canReturnAnchor(home)) { rc.returnAnchor(home); anchorsReturned++; anchorTurns = 0; anchorTarget = null; }
            }
            return;
        }
        if (anchorTarget == null || (anchorIsland > 0 && ownerOf(anchorIsland) != 0)) chooseIsland();
        if (anchorTarget == null) { explore(); return; }
        if (anchorIsland > 0 && G.here.distanceSquaredTo(anchorTarget) <= 20) {
            MapLocation[] tiles = rc.senseNearbyIslandLocations(anchorIsland);
            MapLocation best = null;
            int bd = Integer.MAX_VALUE;
            for (int i = tiles.length; --i >= 0; ) {
                MapLocation t = tiles[i];
                if (!t.equals(G.here) && rc.canSenseLocation(t) && rc.isLocationOccupied(t)) continue;
                int d = G.here.distanceSquaredTo(t);
                if (d < bd) { bd = d; best = t; }
            }
            if (best != null) anchorTarget = best;
        }
        moveTwice(anchorTarget);
        tryPlace();
    }

    static boolean tryPlace() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation at = rc.getLocation();
        int id = rc.senseIsland(at);
        if (id <= 0 || rc.senseTeamOccupyingIsland(id) != Team.NEUTRAL || !rc.canPlaceAnchor()) return false;
        rc.placeAnchor();
        anchorsPlaced++;
        anchorTarget = null;
        anchorTurns = 0;
        MapMem.islandOwner[id] = 1;
        MapMem.islandSeen[id] = G.round;
        MapMem.islandTile[id] = at;
        Comms.canWrite = true;      // standing on our own island now: writes are allowed (r2 4)
        Comms.reportIsland(id, 1, at);
        return true;
    }

    /** Move up to twice (a light carrier's move cooldown can be under 10). */
    static void moveTwice(MapLocation t) throws GameActionException {
        Nav.moveTo(t);
        if (G.rc.isMovementReady()) Nav.moveTo(t);
    }

    static int ownerOf(int id) throws GameActionException {
        if (id < 0) return 0;          // a predicted island: unknown id, treated as free until seen
        if (id == 0) return -1;
        if (MapMem.islandSeen[id] > 0 && G.round - MapMem.islandSeen[id] < 10) return MapMem.islandOwner[id];
        return Comms.islandOwner(id);
    }

    /** Nearest neutral island, preferring our side of the map; else a predicted island (mirror of a known one). */
    static void chooseIsland() throws GameActionException {
        anchorTarget = null;
        anchorIsland = 0;
        int n = Math.min(35, G.rc.getIslandCount());
        MapLocation[] ehq = MapMem.enemyHQs();
        int bd = Integer.MAX_VALUE;
        for (int id = 1; id <= n; id++) {
            MapLocation t = MapMem.islandTile[id];
            if (t == null) t = Comms.islandTile(id);
            if (t == null || ownerOf(id) != 0) continue;
            int d = G.here.distanceSquaredTo(t);
            if (enemySide(t, ehq)) d = d * 4 + 400;           // contested islands only when nothing safer is known
            if (d < bd) { bd = d; anchorTarget = t; anchorIsland = id; }
        }
        if (anchorTarget != null || !MapMem.decided()) return;
        // predicted islands: images of known island tiles that no known island covers yet
        int s = MapMem.cand == 1 || MapMem.cand == 2 || MapMem.cand == 4 ? MapMem.cand : (MapMem.cand & 1) != 0 ? 1 : (MapMem.cand & 2) != 0 ? 2 : 4;
        for (int id = 1; id <= n; id++) {
            MapLocation t = Comms.islandTile(id);
            if (t == null) continue;
            MapLocation p = MapMem.img(s, t);
            boolean covered = false;
            for (int j = 1; j <= n && !covered; j++) {
                MapLocation u = Comms.islandTile(j);
                if (u != null && u.distanceSquaredTo(p) <= 25) covered = true;
            }
            if (covered) continue;
            int d = G.here.distanceSquaredTo(p);
            if (enemySide(p, ehq)) d = d * 4 + 400;
            if (d < bd) { bd = d; anchorTarget = p; anchorIsland = -1; }
        }
    }

    /** A location nearer the predicted enemy HQs than our own. */
    static boolean enemySide(MapLocation t, MapLocation[] ehq) {
        MapLocation mine = HQState.nearest(t);
        if (mine == null || ehq.length == 0) return false;
        MapLocation theirs = G.nearest(t, ehq);
        return theirs != null && t.distanceSquaredTo(theirs) < t.distanceSquaredTo(mine);
    }
}
