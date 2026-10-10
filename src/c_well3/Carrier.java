package c_well3;

import battlecode.common.*;

/**
 * Carrier: the economy and the anchor courier.
 *
 * Roles: role 1 mines adamantium, role 2 mana (mana pays for launchers, adamantium for carriers and anchors).
 * Rates (RULES): 1 kg per collect at a standard well, one collect per turn at multiplier 1.0; capacity 40; move
 * cooldown floor(5 + 3m/8) by load. Full loads give the most kg per trip, so carriers fill up before returning.
 * Priorities each turn: anchor delivery (c_anc3: a courier with an enemy fighter in vision places, returns the anchor
 * to an adjacent HQ or flees first) > survival (flee armed enemies; throw the load only when cornered) > delivering a
 * full load > taking an anchor waiting at the HQ > c_anc3 island scouting (one carrier in C.SCOUT_EVERY) > gathering.
 * c_well3: gathering starts with the near-well probe (probeTurn: one mana carrier per HQ, when the HQ's nearest known
 * mana well is far), and a deposit drops a well more than twice as far from the HQ as a known one (deliver).
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
        if (C.ROLES == 3) Comms.censusTick();
        if (G.here.equals(lastLoc)) stillTurns++; else { stillTurns = 0; lastLoc = G.here; }
        if (role == 0) { role = pickRole(); if (C.TELEMETRY) Telemetry.emitRole(0, role, 0, -1, -1, 0, trips); }
        MapMem.scan();
        if ((G.round + G.id) % 3 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        reportEnemies();
        if (rc.getNumAnchors(null) > 0) {
            // c_anc3 courier survival: with an enemy fighter in vision place if possible, else hand the anchor back to
            // an adjacent HQ, else flee; a courier threatened for more than C.COURIER_BLOCKED turns takes the anchor
            // home through the timeout path (couriers died in K: 9.5 of 12.4 anchors a game lost in losses)
            if (C.ANCHOR_FLEE && G.nEnemyFighters > 0) {
                if (tryPlace()) { state = 'P'; note(); return; }
                // the step past C.ANCHOR_TIMEOUT is left to deliverAnchor, which emits the timeout record (ANCH 4) only
                // at C.ANCHOR_TIMEOUT + 1; the timeout decision is the same (deliverAnchor increments before it tests)
                if (anchorTurns != C.ANCHOR_TIMEOUT) anchorTurns++;
                courierThreat++;
                MapLocation h = HQState.nearest(G.here);
                if (h != null && rc.canReturnAnchor(h)) {
                    rc.returnAnchor(h);
                    anchorsReturned++;
                    if (C.TELEMETRY) Telemetry.emitAnch(5, 0, 0, false, Telemetry.loc12(h), anchorTurns, 0, G.round);
                    anchorTurns = 0;
                    anchorTarget = null;
                    courierThreat = 0;
                    state = 'Y';
                    note();
                    return;
                }
                int thrown = throwsMade;
                if (survive()) {
                    // a throw destroys the whole inventory, anchor included (RULES 3.4): no longer a courier, so no
                    // k<island> in the indicator and no stale courier counters
                    if (throwsMade != thrown) { anchorTarget = null; anchorIsland = 0; anchorTurns = 0; courierThreat = 0; }
                    state = throwsMade != thrown ? 'V' : 'F';
                    note();
                    return;
                }
            }
            if (courierThreat > C.COURIER_BLOCKED && anchorTurns < C.ANCHOR_TIMEOUT) anchorTurns = C.ANCHOR_TIMEOUT;
            state = 'K';
            deliverAnchor();
            note();
            return;
        }
        int thrown = throwsMade;
        if (survive()) { state = throwsMade != thrown ? 'V' : 'F'; note(); return; }
        int w = rc.getWeight();
        if (w >= C.CARRIER_RETURN_LOAD) returning = true;
        if (returning || (w > 0 && rc.getRoundNum() > 1900)) { state = 'R'; deliver(); }
        else if (takeAnchor()) state = 'T';
        else if (!scoutTurn()) gather();
        unjam();
        note();
    }

    static MapLocation lastLoc;
    static int stillTurns;
    public static int unjams;   // diagnostics

    /** arch_swarm: a carrier that has not moved for C.UNJAM_TURNS turns while travelling or waiting steps to a random
     *  free tile (v3 quick, MassiveL: carriers packed the corner around an HQ and its adjacent mana well, 8 of 12 never
     *  moved again, max still 528-709 rounds, and mana collection stopped at r150). */
    static void unjam() throws GameActionException {
        if (stillTurns < C.UNJAM_TURNS || !G.rc.isMovementReady()) return;
        if (state != 'G' && state != 'R' && state != 'W' && state != 'S' && state != 'X') return;
        int k = G.rand(8);
        for (int i = 0; i < 8; i++) {
            Direction d = G.DIRS[(k + i) & 7];
            if (G.rc.canMove(d)) { G.rc.move(d); G.here = G.rc.getLocation(); stillTurns = 0; lastLoc = G.here; unjams++; return; }
        }
    }

    /** State token this turn (TELEMETRY.md 1.1): G going to a well, C at the well collecting, W waiting at a crowded well,
     *  S switched well (crowd patience ran out), X exploring for a well, R returning, D depositing, F fleeing, V threw
     *  the load, T took an anchor, K/Q/E carrying an anchor to a known island / a predicted island / no target, Y taking
     *  it home after the timeout, P placed it. c_anc3: the island scout shows X while scouting and R while bringing an
     *  unpublished island home; a threatened courier shows P, Y (handed back), F or V before K. c_well3: the well probe
     *  shows X while walking its points and R while bringing an unpublished well home. */
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
    static int pickRole() throws GameActionException {
        switch (C.ROLES) {
            case 3: return swarmRole();
            case 1: return G.round < C.OPENING_ROUNDS ? 1 + (G.id & 1) : 2;
            case 2: return G.id % C.MANA2_AD_EVERY == 0 ? 1 : 2;
            default: return G.round < 60 ? 1 + (G.id & 1) : (G.id % 3 == 0 ? 1 : 2);
        }
    }

    /** arch_swarm (ROLES 3): mana, except one carrier in C.AD_EARLY_EVERY while the nearest HQ asks for adamantium
     *  (Comms.AD_FLAGS: under C.AD_NEED and room under the carrier cap), and from C.AD_ROLE_FROM one in C.AD_LATE_EVERY
     *  (anchors). */
    static int swarmRole() throws GameActionException {
        if (G.round >= C.AD_ROLE_FROM && G.id % C.AD_LATE_EVERY == 0) return 1;
        if (G.id % C.AD_EARLY_EVERY == 0 && Comms.adFlag(Comms.hqIndex(HQState.nearest(G.here)))) return 1;
        return 2;
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
                        case 3:
                            want = swarmRole();
                            // c_anc3: no more Ad to an HQ that banks C.AD_BANK_CAP (median bank_Ad at r500 380 in losses)
                            if (want == 1 && ad >= C.AD_BANK_CAP) want = 2;
                            break;
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
                // c_well3 re-pick: a known well of this role at most half as far from the HQ (less C.REPICK_MARGIN)
                // replaces the current one; gather() then picks the nearest from here, next to the HQ (~600 bytecodes:
                // 16 shared slots and at most 32 seen wells)
                if (C.PROBE && well != null) {
                    MapLocation k = nearerTo(home, Comms.nearestWell(home, role), MapMem.nearestSeenWell(home, role));
                    if (k != null && !k.equals(well) && G.cheb(home, k) * 2 + C.REPICK_MARGIN <= G.cheb(home, well)) well = null;
                }
            }
        }
    }

    /** An empty carrier next to an HQ holding an anchor takes it. c_anc3: never with an enemy fighter in vision, and
     *  the target is chosen first: a located island with a fresh enemy sighting (Comms, at most 1 stamp old) within
     *  r2 C.COURIER_SIGHT_R2 leaves the anchor in the HQ (which then builds no other). */
    static boolean takeAnchor() throws GameActionException {
        RobotController rc = G.rc;
        if (rc.getWeight() != 0 || G.nEnemyFighters > 0) return false;
        MapLocation home = HQState.nearest(G.here);
        if (home == null || G.here.distanceSquaredTo(home) > 2) return false;
        if (rc.canTakeAnchor(home, Anchor.STANDARD)) {
            chooseIsland();
            if (anchorIsland > 0) {
                MapLocation sighting = Comms.nearestEnemy(anchorTarget, 1);
                if (sighting != null && sighting.distanceSquaredTo(anchorTarget) <= C.COURIER_SIGHT_R2) {
                    anchorTarget = null;   // not carrying: the indicator's k<island> is for couriers only
                    anchorIsland = 0;
                    return false;
                }
            }
            rc.takeAnchor(home, Anchor.STANDARD);
            anchorTurns = 0;
            courierThreat = 0;
            if (C.TELEMETRY) {
                Telemetry.emitAnch(7, 0, 0, false, Telemetry.loc12(home), 0, G.here.distanceSquaredTo(home), G.round);
                if (anchorTarget != null) {          // the target record deliverAnchor emitted on its first choice
                    int d2 = G.here.distanceSquaredTo(anchorTarget);
                    Telemetry.emitAnch(1, anchorIsland, anchorIsland < 0 ? 3 : MapMem.islandTile[anchorIsland] != null ? 1 : 2,
                        chosenScore != d2, Telemetry.loc12(anchorTarget), anchorTurns, d2, G.round);
                }
            }
            return true;
        }
        return false;
    }

    static void gather() throws GameActionException {
        RobotController rc = G.rc;
        if (C.PROBE && role == 2 && well == null && !probeDone && probeTurn()) return;   // c_well3
        if (well == null) {
            MapLocation sh = Comms.nearestWell(G.here, role);
            well = nearer(sh, MapMem.nearestSeenWell(G.here, role));
            if (C.TELEMETRY && well != null) wellHook(well == sh ? 1 : 2, role);
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
        if (well != null && rc.getLocation().distanceSquaredTo(well) <= 2) {   // switchWell may have dropped the well
            crowdTurns = 0;
            state = 'C';
            while (rc.isActionReady() && rc.getWeight() < C.CARRIER_RETURN_LOAD) {
                int room = C.CARRIER_RETURN_LOAD - rc.getWeight();
                if (rc.canCollectResource(well, -1)) rc.collectResource(well, -1);
                else if (rc.canCollectResource(well, room)) rc.collectResource(well, room);
                else break;
            }
            if (rc.getWeight() >= C.CARRIER_RETURN_LOAD) returning = true;
        }
    }

    static MapLocation nearer(MapLocation a, MapLocation b) { return nearerTo(G.here, a, b); }

    /** The one of a, b (either may be null) nearer to `from` (dist2; a on ties). */
    static MapLocation nearerTo(MapLocation from, MapLocation a, MapLocation b) {
        if (a == null) return b;
        if (b == null) return a;
        return from.distanceSquaredTo(b) < from.distanceSquaredTo(a) ? b : a;
    }

    /** Another known well (shared or seen by this carrier) of the same type, else any type. arch_swarm: a mana carrier
     *  switches only to another mana well (v1: crowded mana carriers moved to adamantium wells, Ad@100 164 against the
     *  members' 10-92); with none known it searches for one (toward the map centre first). */
    static void switchWell() throws GameActionException {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE, bt = 0, i;
        for (i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
            int c = Comms.read(i);
            if (c == 0) break;
            MapLocation l = G.dec(c & 0xfff);
            if (l.equals(well)) continue;
            if (C.ROLES == 3 && role == 2 && (c >>> 12) != 2) continue;
            int d = G.here.distanceSquaredTo(l) + ((c >>> 12) == role ? 0 : 400);
            if (d < bd) { bd = d; best = l; if (C.TELEMETRY) bt = c >>> 12; }
        }
        if (C.TELEMETRY) { Comms.lastWellCount = i - Comms.WELLS; Telemetry.crowdSwitches++; }
        for (int j = MapMem.seenWellCount(); --j >= 0; ) {
            MapLocation l = MapMem.seenWellAt(j);
            if (l.equals(well)) continue;
            if (C.ROLES == 3 && role == 2 && MapMem.seenWellTypeAt(j) != 2) continue;
            int d = G.here.distanceSquaredTo(l) + (MapMem.seenWellTypeAt(j) == role ? 0 : 400);
            if (d < bd) { bd = d; best = l; if (C.TELEMETRY) bt = MapMem.seenWellTypeAt(j); }
        }
        if (best != null) { well = best; if (C.TELEMETRY) wellHook(5, bt); }
        else if (C.ROLES == 3 && role == 2) { well = null; centreTried = false; searchTurns = 0; }   // look for another mana well
    }

    /** WELL record: `well` was just set to a non-null tile (source 1 shared, 2 seen, 3 any shared, 4 any seen, 5 crowd
     *  switch). Comms.lastWellCount is from this turn's scan of the shared wells. */
    static void wellHook(int source, int type) {
        Telemetry.emitWell(Telemetry.loc12(well), type, source, role, G.here.distanceSquaredTo(well), Comms.lastWellCount,
            MapMem.seenWellCount(), searchTurns, crowdTurns, Telemetry.loc12(lastWell));
        lastWell = well;
        wellType = type;
    }

    static boolean centreTried;

    static void explore() throws GameActionException {
        // arch_swarm: a mana carrier that knows no mana well looks toward the map centre first (v2 quick, Cornucopia:
        // every mana well lies 10-16 tiles from the HQs toward the centre; random search around home found none and
        // 13 of 28 early trips ended in death while exploring)
        if (C.ROLES == 3 && role == 2 && !centreTried) {
            MapLocation c = new MapLocation(G.W / 2, G.H / 2);
            if (G.here.distanceSquaredTo(c) <= 8 || Nav.stuckOn(c)) centreTried = true;
            else { moveTwice(c); return; }
        }
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
    /** c_anc3: turns this courier has carried an anchor with an enemy fighter in vision (reset on take, place, return). */
    static int courierThreat;

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
                    courierThreat = 0;
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
        if (anchorTarget == null) { state = 'E'; scoutMove(); return; }   // c_anc3: search the whole map, not home
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
        courierThreat = 0;
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

    /** Telemetry only: chooseIsland's score of its choice (dist2, or 4 x dist2 + 400 for a located island on the enemy
     *  side; c_anc3: predicted islands on the enemy side are skipped). */
    static int chosenScore;

    /** Nearest neutral island, preferring our side of the map; else a predicted island (mirror of a known one). */
    static void chooseIsland() throws GameActionException {
        anchorTarget = null;
        anchorIsland = 0;
        int n = Math.min(35, G.rc.getIslandCount());
        MapLocation[] ehq = MapMem.enemyHQs();
        int bd = Integer.MAX_VALUE;
        for (int id = 1; id <= n; id++) {
            if (Clock.getBytecodesLeft() < C.ISLAND_LOOP_GUARD) break;   // c_anc3: also called from takeAnchor
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
            // c_anc3: never a predicted island on the enemy side (anchors carried there were lost in Q); located
            // enemy-side islands keep their penalty above (conquest needs them on Forest and Cornucopia)
            if (enemySide(p, ehq)) continue;
            int d = G.here.distanceSquaredTo(p);
            if (d < bd) { bd = d; anchorTarget = p; anchorIsland = -1; }
        }
        if (C.TELEMETRY) chosenScore = bd;
    }

    // ---------------------------------------------------------------- c_anc3: island scouting
    static MapLocation scoutTarget;
    static boolean scoutDone, scoutNeed;
    static int scoutTurns, scoutCheck;

    /** Toward a random tile on our side of the map at least 8 moves away (4 draws; else the last draw), redrawn on
     *  arrival (r2 8) or when Nav is stuck on it. Used by the island scout and by a courier with no target ('E'). */
    static void scoutMove() throws GameActionException {
        if (scoutTarget == null || G.here.distanceSquaredTo(scoutTarget) <= 8 || Nav.stuckOn(scoutTarget)) {
            MapLocation[] ehq = MapMem.enemyHQs();
            MapLocation t = null;
            for (int i = 0; i < 4; i++) {
                t = new MapLocation(G.rand(G.W), G.rand(G.H));
                if (!enemySide(t, ehq) && G.cheb(G.here, t) >= 8) break;
            }
            scoutTarget = t;
        }
        moveTwice(scoutTarget);
    }

    /**
     * Island scout (C.SCOUT): from C.SCOUT_FROM an empty carrier with id % C.SCOUT_EVERY == 1, while no located island
     * is neutral and some island is not located (Comms.islandStats, rechecked every 10 rounds), scouts with scoutMove
     * ('X') for at most C.SCOUT_MAX_TURNS turns; an island it has seen whose slot is still empty is published at once
     * when it can write, otherwise it takes it home ('R'; MapMem.flushIslands and scanIslands publish it there).
     * survive() has run before this, so a scout still flees. Returns false when the carrier should gather.
     */
    static boolean scoutTurn() throws GameActionException {
        RobotController rc = G.rc;
        if (!C.SCOUT || G.round < C.SCOUT_FROM || G.id % C.SCOUT_EVERY != 1 || scoutDone || rc.getWeight() != 0) return false;
        int n = Math.min(35, rc.getIslandCount());
        if (G.round >= scoutCheck) {
            scoutCheck = G.round + 10;
            Comms.islandStats(n);
            scoutNeed = Comms.islLocNeutral == 0 && Comms.islUnloc > 0;
        }
        if (!scoutNeed) return false;
        boolean unpublished = false;
        for (int id = 1; id <= n; id++) {
            if (Clock.getBytecodesLeft() < C.ISLAND_LOOP_GUARD) break;
            if (MapMem.islandTile[id] == null || Comms.read(Comms.ISLANDS + id) != 0) continue;
            // in write range: publish now (flushIslands republishes only sightings up to 60 rounds old, and a long
            // trip home could leave the scout waiting at the HQ for a publication that never comes)
            if (Comms.canWrite) { Comms.reportIsland(id, MapMem.islandOwner[id], MapMem.islandTile[id]); scoutCheck = G.round + 1; }
            if (Comms.read(Comms.ISLANDS + id) == 0) { unpublished = true; break; }
        }
        if (unpublished) {
            state = 'R';
            MapLocation home = HQState.nearest(G.here);
            if (home != null) moveTwice(home);
            return true;
        }
        state = 'X';
        scoutMove();
        if (++scoutTurns > C.SCOUT_MAX_TURNS) scoutDone = true;
        return true;
    }

    // ---------------------------------------------------------------- c_well3: near-well probe
    static boolean probeDone, probeInit;
    static int probeTurns, probeFar, nProbe;
    static MapLocation probeHome, publishWell;
    static MapLocation[] probePts = new MapLocation[5];

    /**
     * Near-well probe (C.PROBE), called at the top of gather() by a mana carrier with no well. Once per carrier
     * (probeStart): when the nearest HQ's nearest known mana well (shared or seen) is farther than C.PROBE_FAR
     * (Chebyshev) and the round is before C.PROBE_UNTIL, the carrier claims the HQ's probe (Comms.AD_FLAGS bit
     * C.PROBE_SHIFT+i, one per HQ per game) and visits, nearest first, the 4 diagonals at +-C.PROBE_NEAR from the HQ and
     * the midpoint toward the nearest enemy HQ pulled in to C.PROBE_TOWARD ('X', at most C.PROBE_TURNS turns). A mana
     * well it has seen within C.PROBE_FAR of the HQ and at least 4 nearer than the known one becomes its well, after it
     * has walked it home and published it ('R') when the shared list does not hold it yet. survive() runs before this, so
     * a prober still flees. Returns true when it took the turn.
     */
    static boolean probeTurn() throws GameActionException {
        if (publishWell == null) {
            if (!probeInit && !probeStart()) { probeDone = true; return false; }
            MapLocation w = MapMem.nearestSeenWell(probeHome, 2);   // found check
            if (w != null) {
                int dw = G.cheb(probeHome, w);
                if (dw <= C.PROBE_FAR && dw + 4 <= probeFar) {
                    if (Wells.known(w)) { probeTake(w); return false; }
                    publishWell = w;
                }
            }
        }
        if (publishWell != null) {                                  // walk it home and publish it
            state = 'R';
            moveTwice(probeHome);
            boolean wrote = false;
            if (G.rc.canWriteSharedArray(0, 0)) {
                Comms.canWrite = true;
                MapMem.flushWells();                                // registers the unreported well
                // flushWells keeps at most 16 unreported wells and forgets them after one attempt: register it directly
                if (!Wells.known(publishWell)) Comms.registerWell(publishWell, 2);
                wrote = true;
            }
            // in write range it is now shared, or the 16 well slots are full: mine it anyway (no endless 'R' at the
            // HQ); the turn cap covers a prober that cannot get home
            if (wrote || Wells.known(publishWell) || ++probeTurns > 2 * C.PROBE_TURNS) probeTake(publishWell);
            return true;
        }
        if (++probeTurns > C.PROBE_TURNS) { probeDone = true; return false; }
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = nProbe; --i >= 0; ) {                          // at most 5 points
            MapLocation p = probePts[i];
            int d = G.here.distanceSquaredTo(p);
            if (d <= 2 || Nav.stuckOn(p) || (MapMem.known(p.x, p.y) && MapMem.isWall(p.x, p.y))) {
                probePts[i] = probePts[--nProbe];                   // reached or unreachable: dropped (the last point,
                probePts[nProbe] = null;                            // already scored, moves into its place)
                continue;
            }
            if (d < bd) { bd = d; best = p; }
        }
        if (best == null) { probeDone = true; return false; }
        state = 'X';
        moveTwice(best);
        return true;
    }

    /** Once per carrier: whether a probe is needed and this carrier claimed it; sets the probe points. */
    static boolean probeStart() throws GameActionException {
        probeInit = true;
        if (G.round >= C.PROBE_UNTIL) return false;
        MapLocation home = HQState.nearest(G.here);
        if (home == null) return false;
        MapLocation k = nearerTo(home, Comms.nearestWell(home, 2), MapMem.nearestSeenWell(home, 2));
        // no known mana well keeps today's centre-first explore (Cornucopia needs it)
        if (k == null || G.cheb(home, k) <= C.PROBE_FAR) return false;
        int idx = Comms.hqIndex(home);
        if (idx < 0) return false;
        int v = Comms.read(Comms.AD_FLAGS), bit = 1 << (C.PROBE_SHIFT + idx);
        if ((v & bit) != 0 || !Comms.write(Comms.AD_FLAGS, v | bit)) return false;
        probeHome = home;
        probeFar = G.cheb(home, k);
        nProbe = 0;
        addProbePt(home.x - C.PROBE_NEAR, home.y - C.PROBE_NEAR);
        addProbePt(home.x + C.PROBE_NEAR, home.y - C.PROBE_NEAR);
        addProbePt(home.x - C.PROBE_NEAR, home.y + C.PROBE_NEAR);
        addProbePt(home.x + C.PROBE_NEAR, home.y + C.PROBE_NEAR);
        MapLocation[] ehq = MapMem.enemyHQs();
        if (ehq.length > 0) {
            MapLocation e = G.nearest(home, ehq);
            if (e != null) {                                        // the midpoint, at most C.PROBE_TOWARD from home
                int dx = (e.x - home.x) / 2, dy = (e.y - home.y) / 2, c = Math.max(Math.abs(dx), Math.abs(dy));
                if (c > C.PROBE_TOWARD) { dx = dx * C.PROBE_TOWARD / c; dy = dy * C.PROBE_TOWARD / c; }
                addProbePt(home.x + dx, home.y + dy);
            }
        }
        return true;
    }

    /** A probe point clamped to the map; skipped when it is a known wall. */
    static void addProbePt(int x, int y) {
        x = Math.max(0, Math.min(G.W - 1, x));
        y = Math.max(0, Math.min(G.H - 1, y));
        if (MapMem.known(x, y) && MapMem.isWall(x, y)) return;
        probePts[nProbe++] = new MapLocation(x, y);
    }

    /** The probe's well becomes this carrier's well; the probe ends (WELL record source 2: a well it saw). */
    static void probeTake(MapLocation w) throws GameActionException {
        well = w;
        publishWell = null;
        probeDone = true;
        if (C.TELEMETRY) {
            int n = 0;                                              // wellHook reports this turn's filled well slots
            while (n < Comms.NWELLS && Comms.read(Comms.WELLS + n) != 0) n++;
            Comms.lastWellCount = n;
            wellHook(2, 2);
        }
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
