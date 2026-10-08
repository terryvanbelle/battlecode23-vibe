package c_line8m;

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
    // telemetry only (never read by decisions): the previous turn's state, the last well announced and its type
    static char prevState = '?';
    static MapLocation lastWell;
    static int wellType;

    static void run() throws GameActionException {
        RobotController rc = G.rc;
        if (role == 0) { role = pickRole(); if (C.TELEMETRY) Telemetry.emitRole(0, role, 0, -1, -1, 0, trips); }
        MapMem.scan();
        if ((G.round + G.id) % 3 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        reportEnemies();
        if (rc.getNumAnchors(null) > 0) { state = 'K'; deliverAnchor(); note(); return; }
        int thrown = throwsMade;
        if (survive()) { state = throwsMade != thrown ? 'V' : 'F'; note(); return; }
        int w = rc.getWeight();
        if (w >= C.CARRIER_RETURN_LOAD) returning = true;
        if (returning || (w > 0 && rc.getRoundNum() > 1900)) { state = 'R'; deliver(); }
        else if (takeAnchor()) state = 'T';
        else gather();
        note();
    }

    /** State token this turn (TELEMETRY.md 1.1): G going to a well, C at the well collecting, W waiting at a crowded well,
     *  S switched well (crowd patience ran out), X exploring for a well, R returning, D depositing, F fleeing, V threw
     *  the load, T took an anchor, K/Q/E carrying an anchor to a known island / a predicted island / no target, Y taking
     *  it home after the timeout, P placed it. */
    static char state = '?';

    /** End of turn: the telemetry code and the indicator rest (role digit, plus k<island> while an anchor has a target). */
    static void note() {
        int st = Telemetry.CARRIER_STATES.indexOf(state);
        Telemetry.code = Telemetry.carrierCode(st < 0 ? 0 : st, role);
        G.note = role + (anchorTarget != null ? "k" + anchorIsland : "");
        prevState = state;
    }

    /** Mana first (launchers, the army, cost mana; strong field bots mine mostly mana: camel_case on Risk collected
     *  1,700 Mn and 27 Ad, awesomelemonade on ReverseFunnel 12,186 Mn and 4,521 Ad). The opening alternates so the HQs can
     *  afford carriers; afterwards a carrier mines adamantium only when its HQ is short of it (deliver()). */
    /** Role (1 adamantium, 2 mana) by C.ROLES: 0 = balance by HQ stock (c_nav1); 1 = mana-first with adamantium while
     *  the HQ holds < AD_LOW (c_mana1: the HQ spends Ad on carriers, so it read short most of the time and carriers
     *  mined MORE Ad: Mn -294, Ad +229, net -7 games, t -2.1, on the 174 calibration cells); 2 = 1 in 5 on adamantium,
     *  overrides by HQ stock (c_mana2). */
    static int pickRole() {
        switch (C.ROLES) {
            case 1: return G.round < C.OPENING_ROUNDS ? 1 + (G.id & 1) : 2;
            case 2: return G.id % C.MANA2_AD_EVERY == 0 ? 1 : 2;
            default: return G.round < 60 ? 1 + (G.id & 1) : (G.id % 3 == 0 ? 1 : 2);
        }
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
        boolean threw = false;
        if (w >= 8 && bd <= 9 && rc.getHealth() <= 60 && rc.canAttack(threat.location)) {
            rc.attack(threat.location);   // throws everything: worth it only when the carrier is about to die
            throwsMade++;
            returning = false;
            threw = true;
        }
        MapLocation home = HQState.nearest(G.here);
        boolean moved = false;
        if (home != null && home.distanceSquaredTo(threat.location) > G.here.distanceSquaredTo(threat.location))
            moved = Nav.moveTo(home);
        if (!moved) moved = Nav.moveAway(threat.location);
        if (moved && G.rc.isMovementReady()) {               // light carriers move twice a turn (cooldown 5 + 0.375 w)
            if (home != null && home.distanceSquaredTo(threat.location) > G.rc.getLocation().distanceSquaredTo(threat.location))
                { if (!Nav.moveTo(home)) Nav.moveAway(threat.location); }
            else Nav.moveAway(threat.location);
        }
        if (moved) fled++;
        if (C.TELEMETRY && (moved || bd <= 20) && (threw || (prevState != 'F' && prevState != 'V')))
            Telemetry.emitFlee(bd, G.nEnemyFighters, rc.getHealth(), threw, moved, Telemetry.loc12(threat.location), w,
                Telemetry.loc12(home), G.round);
        return moved || bd <= 20;
    }

    static void deliver() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation home = HQState.nearest(G.here);
        if (home == null) return;
        if (G.here.distanceSquaredTo(home) > 2) moveTwice(home);
        if (G.rc.getLocation().distanceSquaredTo(home) <= 2) {
            state = 'D';
            ResourceType[] types = {ResourceType.ADAMANTIUM, ResourceType.MANA, ResourceType.ELIXIR};
            int load = 0;
            for (int i = 0; i < 3 && rc.isActionReady(); i++) {
                int a = rc.getResourceAmount(types[i]);
                if (a > 0 && rc.canTransferResource(home, types[i], a)) { rc.transferResource(home, types[i], a); load += a; }
            }
            if (rc.getWeight() == 0) {
                returning = false;
                trips++;
                if (C.TELEMETRY) Telemetry.trip(home, load, role, well, wellType);
                RobotInfo hq = rc.senseRobotAtLocation(home);
                if (hq != null) {
                    int ad = hq.getResourceAmount(ResourceType.ADAMANTIUM), mn = hq.getResourceAmount(ResourceType.MANA);
                    int want;
                    switch (C.ROLES) {
                        case 1: want = ad < C.AD_LOW ? 1 : 2; break;
                        case 2: want = ad > C.MANA2_AD_HIGH ? 2 : (ad < C.MANA2_AD_LOW && mn > C.MANA2_MN_HIGH) ? 1 : role; break;
                        default: want = mn + 100 < ad ? 2 : ad + 150 < mn ? 1 : role;   // mine what the HQ is short of
                    }
                    if (want != role) {
                        if (C.TELEMETRY) Telemetry.emitRole(role, want, 1, ad, mn, Telemetry.loc12(home), trips);
                        role = want;
                        well = null;
                    }
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
        if (rc.canTakeAnchor(home, Anchor.STANDARD)) {
            if (C.ANCHOR_GATE) {                     // take one only with somewhere to put it (C.ANCHOR_GATE)
                anchorTarget = null;
                chooseIsland();
                if (anchorTarget == null) return false;
            }
            MapLocation chosen = anchorTarget;
            rc.takeAnchor(home, Anchor.STANDARD);
            anchorTarget = C.ANCHOR_GATE ? chosen : null;
            anchorTurns = 0;
            if (C.TELEMETRY) Telemetry.emitAnch(7, 0, 0, false, Telemetry.loc12(home), 0, G.here.distanceSquaredTo(home), G.round);
            return true;
        }
        return false;
    }

    static void gather() throws GameActionException {
        RobotController rc = G.rc;
        if (well == null) {
            MapLocation sh = Comms.nearestWell(G.here, role);
            well = nearer(sh, MapMem.nearestSeenWell(G.here, role));
            if (C.TELEMETRY && well != null) wellHook(well == sh ? 1 : 2, role);
        }
        // C.WELL_DANGER: leave a well with a fresh enemy-launcher sighting near it for another known well (self-play
        // Cat vs g_iter0: 24 of our carriers died, most at one contested well cluster, fleeing or on their way there)
        if (C.WELL_DANGER && well != null && G.round % 4 == G.id % 4 && Comms.enemyNear(well, C.WELL_DANGER_R2, 1)) {
            MapLocation alt = safeWell();
            if (alt != null) well = alt;
        }
        if (well == null && ++searchTurns > C.WELL_SEARCH_TURNS) {
            MapLocation sh = Comms.nearestWell(G.here, 0);
            well = nearer(sh, MapMem.nearestSeenWell(G.here, 0));
            if (C.TELEMETRY && well != null) wellHook(well == sh ? 3 : 4, well == sh ? Comms.lastWellType : MapMem.lastSeenType);
        }
        if (well == null) { state = 'X'; explore(); return; }
        searchTurns = 0;
        state = 'G';
        int d = G.here.distanceSquaredTo(well);
        if (d > 2) {
            moveTwice(well);
            d = rc.getLocation().distanceSquaredTo(well);
            if (d <= 8 && d > 2) {                          // near the well but not at it: crowded (one tick a turn)
                state = 'W';
                if (++crowdTurns > C.WELL_CROWD_PATIENCE) { switchWell(); crowdTurns = 0; state = 'S'; }
            }
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

    /** The nearest known well (shared or seen) with no fresh enemy sighting near it, own role first; else null. */
    static MapLocation safeWell() throws GameActionException {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
            int c = Comms.read(i);
            if (c == 0) break;
            MapLocation l = G.dec(c & 0xfff);
            int d = G.here.distanceSquaredTo(l) + ((c >>> 12) == role ? 0 : 400);
            if (d < bd && !Comms.enemyNear(l, C.WELL_DANGER_R2, 1)) { bd = d; best = l; }
        }
        for (int i = MapMem.seenWellCount(); --i >= 0; ) {
            MapLocation l = MapMem.seenWellAt(i);
            int d = G.here.distanceSquaredTo(l) + (MapMem.seenWellTypeAt(i) == role ? 0 : 400);
            if (d < bd && !Comms.enemyNear(l, C.WELL_DANGER_R2, 1)) { bd = d; best = l; }
        }
        return best;
    }

    static MapLocation nearer(MapLocation a, MapLocation b) {
        if (a == null) return b;
        if (b == null) return a;
        return G.here.distanceSquaredTo(b) < G.here.distanceSquaredTo(a) ? b : a;
    }

    /** Another known well (shared or seen by this carrier) of the same type, else any type. */
    static void switchWell() throws GameActionException {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE, bt = 0, i;
        for (i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
            int c = Comms.read(i);
            if (c == 0) break;
            MapLocation l = G.dec(c & 0xfff);
            if (l.equals(well)) continue;
            int d = G.here.distanceSquaredTo(l) + ((c >>> 12) == role ? 0 : 400);
            if (d < bd) { bd = d; best = l; if (C.TELEMETRY) bt = c >>> 12; }
        }
        if (C.TELEMETRY) { Comms.lastWellCount = i - Comms.WELLS; Telemetry.crowdSwitches++; }
        for (int j = MapMem.seenWellCount(); --j >= 0; ) {
            MapLocation l = MapMem.seenWellAt(j);
            if (l.equals(well)) continue;
            int d = G.here.distanceSquaredTo(l) + (MapMem.seenWellTypeAt(j) == role ? 0 : 400);
            if (d < bd) { bd = d; best = l; if (C.TELEMETRY) bt = MapMem.seenWellTypeAt(j); }
        }
        if (best != null) { well = best; if (C.TELEMETRY) wellHook(5, bt); }
    }

    /** WELL record: `well` was just set to a non-null tile (source 1 shared, 2 seen, 3 any shared, 4 any seen, 5 crowd
     *  switch). Comms.lastWellCount is from this turn's scan of the shared wells. */
    static void wellHook(int source, int type) {
        Telemetry.emitWell(Telemetry.loc12(well), type, source, role, G.here.distanceSquaredTo(well), Comms.lastWellCount,
            MapMem.seenWellCount(), searchTurns, crowdTurns, Telemetry.loc12(lastWell));
        lastWell = well;
        wellType = type;
    }

    static void explore() throws GameActionException {
        if (exploreTarget == null || G.here.distanceSquaredTo(exploreTarget) <= 8 || Nav.stuckOn(exploreTarget)) {
            MapLocation home = HQState.nearest(G.here);
            Direction d = G.DIRS[G.rand(8)];
            int r = 8 + G.rand(8);
            int x = (home == null ? G.here.x : home.x) + d.dx * r, y = (home == null ? G.here.y : home.y) + d.dy * r;
            exploreTarget = new MapLocation(Math.max(0, Math.min(G.W - 1, x)), Math.max(0, Math.min(G.H - 1, y)));
        }
        moveTwice(exploreTarget);
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
        if (tryPlace()) { state = 'P'; return; }
        if (anchorTurns > C.ANCHOR_TIMEOUT) {                 // give up: return the anchor so it can be reused
            state = 'Y';
            if (C.TELEMETRY && anchorTurns == C.ANCHOR_TIMEOUT + 1)
                Telemetry.emitAnch(4, anchorIsland, 0, false, Telemetry.loc12(anchorTarget), anchorTurns, 0, G.round);
            MapLocation home = HQState.nearest(G.here);
            if (home != null) {
                if (G.here.distanceSquaredTo(home) > 2) moveTwice(home);
                if (rc.canReturnAnchor(home)) {
                    rc.returnAnchor(home);
                    anchorsReturned++;
                    if (C.TELEMETRY) Telemetry.emitAnch(5, 0, 0, false, Telemetry.loc12(home), anchorTurns, 0, G.round);
                    anchorTurns = 0;
                    anchorTarget = null;
                }
            }
            return;
        }
        // a predicted island (id -1) in sight: learn its real id, or remember that the prediction was wrong (audit
        // ANCHOR-P: an unresolved prediction was never re-chosen, and the anchor idled until the timeout)
        if (anchorTarget != null && anchorIsland < 0 && rc.canSenseLocation(anchorTarget)) {
            int id = rc.senseIsland(anchorTarget);
            if (id > 0) anchorIsland = id;
            else {
                if (C.TELEMETRY) Telemetry.emitAnch(2, -1, 3, false, Telemetry.loc12(anchorTarget), anchorTurns,
                    G.here.distanceSquaredTo(anchorTarget), G.round);
                rejectPrediction(anchorTarget);
                anchorTarget = null;
            }
        }
        if (anchorTarget == null || (anchorIsland > 0 && ownerOf(anchorIsland) != 0)) {
            boolean had = anchorTarget != null;
            chooseIsland();
            if (C.TELEMETRY && anchorTarget != null) {
                int d2 = G.here.distanceSquaredTo(anchorTarget);
                Telemetry.emitAnch(had ? 3 : 1, anchorIsland, anchorIsland < 0 ? 3 : MapMem.islandTile[anchorIsland] != null ? 1 : 2,
                    chosenScore != d2, Telemetry.loc12(anchorTarget), anchorTurns, d2, G.round);
            }
        }
        if (anchorTarget == null) { state = 'E'; explore(); return; }
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
        state = anchorIsland < 0 ? 'Q' : 'K';
        if (tryPlace()) state = 'P';
    }

    static boolean tryPlace() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation at = rc.getLocation();
        int id = rc.senseIsland(at);
        if (id <= 0 || rc.senseTeamOccupyingIsland(id) != Team.NEUTRAL || !rc.canPlaceAnchor()) return false;
        rc.placeAnchor();
        anchorsPlaced++;
        if (C.TELEMETRY) Telemetry.emitAnch(6, id, 0, false, Telemetry.loc12(at), anchorTurns, 0, G.round);
        anchorTarget = null;
        anchorTurns = 0;
        MapMem.islandOwner[id] = 1;
        MapMem.islandSeen[id] = G.round;
        MapMem.islandTile[id] = at;
        Comms.canWrite = true;      // standing on our own island now: writes are allowed (r2 4)
        Comms.reportIsland(id, 1, at);
        return true;
    }

    /** Move up to twice: a carrier's move cooldown is floor(0.375 w) + 5, under 10 up to 13 kg, so an empty or light
     *  carrier makes two moves a turn (audit R1: gather, explore and flight moved once, at half the allowed speed).
     *  The second move stops short of a target already adjacent. */
    static void moveTwice(MapLocation t) throws GameActionException {
        Nav.moveTo(t);
        if (G.rc.isMovementReady() && G.rc.getLocation().distanceSquaredTo(t) > 2) Nav.moveTo(t);
    }

    static int ownerOf(int id) throws GameActionException {
        if (id < 0) return 0;          // a predicted island: unknown id, treated as free until seen
        if (id == 0) return -1;
        if (MapMem.islandSeen[id] > 0 && G.round - MapMem.islandSeen[id] < 10) return MapMem.islandOwner[id];
        return Comms.islandOwner(id);
    }

    /** Telemetry only: chooseIsland's score of its choice (dist2, or 4 x dist2 + 400 on the enemy side). */
    static int chosenScore;

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
        if (C.TELEMETRY) chosenScore = bd;
        if (anchorTarget != null || !MapMem.decided()) return;
        // predicted islands: images of known island tiles that no known island covers yet. Known tiles are read once
        // (shared slot or this robot's own sighting); the pairwise check is bounded by the bytecode left (audit BC-1:
        // decoding n x n slots cost ~40k bytecodes on 35-island maps against the carrier's 12,500)
        int s = MapMem.cand == 1 || MapMem.cand == 2 || MapMem.cand == 4 ? MapMem.cand : (MapMem.cand & 1) != 0 ? 1 : (MapMem.cand & 2) != 0 ? 2 : 4;
        MapLocation[] known = new MapLocation[n];
        int k = 0;
        for (int id = 1; id <= n; id++) {
            MapLocation t = Comms.islandTile(id);
            if (t == null) t = MapMem.islandTile[id];
            if (t != null) known[k++] = t;
        }
        for (int a = 0; a < k; a++) {
            if (Clock.getBytecodesLeft() < 3000) break;
            MapLocation p = MapMem.img(s, known[a]);
            boolean covered = rejected(p);
            for (int j = k; --j >= 0 && !covered; ) if (known[j].distanceSquaredTo(p) <= 25) covered = true;
            if (covered) continue;
            int d = G.here.distanceSquaredTo(p);
            if (enemySide(p, ehq)) d = d * 4 + 400;
            if (d < bd) { bd = d; anchorTarget = p; anchorIsland = -1; }
        }
        if (C.TELEMETRY) chosenScore = bd;
    }

    static MapLocation[] rejectedPred = new MapLocation[8];
    static int nRejected;

    static void rejectPrediction(MapLocation p) {
        if (nRejected < rejectedPred.length) rejectedPred[nRejected++] = p;
        else rejectedPred[G.rand(rejectedPred.length)] = p;
    }

    static boolean rejected(MapLocation p) {
        for (int i = nRejected; --i >= 0; ) if (rejectedPred[i].distanceSquaredTo(p) <= 8) return true;
        return false;
    }

    /** A location nearer the predicted enemy HQs than our own. */
    static boolean enemySide(MapLocation t, MapLocation[] ehq) {
        MapLocation mine = HQState.nearest(t);
        if (mine == null || ehq.length == 0) return false;
        MapLocation theirs = G.nearest(t, ehq);
        return theirs != null && t.distanceSquaredTo(theirs) < t.distanceSquaredTo(mine);
    }
}
