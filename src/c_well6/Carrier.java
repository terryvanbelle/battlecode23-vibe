package c_well6;

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
 * c_well5: a probe point counts as covered within r2 C.PROBE_SEE and is dropped as unreachable only after
 * C.PROBE_POINT_TURNS turns aimed at it; an odd-id prober aims at its farthest point first; a prober that finds nothing
 * releases the HQ's claim before C.PROBE_UNTIL (a later carrier retries); with no mana well known before C.PROBE_EARLY,
 * the probe walks to the front point alone when it is at least C.PROBE_FRONT_MIN from the HQ.
 * c_well6 (C.HOT): a carrier that sees an enemy fighter within r2 C.HOT_NEAR_D2 of its front well (Carrier.frontGate)
 * drops it and marks the front wells around the fighter hot in the shared list; every carrier skips a hot well and
 * takes the cool well nearest our HQ.
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
        if (C.HOT && hotPending && Comms.canWrite) {          // c_well6: mark the front wells near the fighter it fled
            if (G.round < hotUntil) markHot();
            hotPending = false;
        }
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
        // c_well6: a fighter near this carrier's front well makes the front wells around it hot (gather() drops the
        // well; marked in the shared list at the next write turn)
        if (C.HOT && well != null && well.distanceSquaredTo(threat.location) <= C.HOT_NEAR_D2 && front(well)) {
            hotSpot = threat.location;
            hotUntil = G.round + C.HOT_LOCAL;
            hotPending = true;
        }
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
                // replaces the current one; gather() then picks the nearest from here, next to the HQ (~1,500 bytecodes:
                // 16 shared slots and at most 32 seen wells)
                if (C.PROBE && well != null) {
                    MapLocation k = C.HOT && anyHot() ? nearestCool(home, role)               // c_well6
                        : nearerTo(home, Comms.nearestWell(home, role), MapMem.nearestSeenWell(home, role));
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
        // c_well5: a prober that ended without a find clears its HQ's claim at its first write turn, before
        // C.PROBE_UNTIL, so a later mana carrier of that HQ can probe again (with its own point order)
        if (probeRelease && Comms.canWrite) {
            if (G.round < C.PROBE_UNTIL) {
                int v = Comms.read(Comms.AD_FLAGS);
                boolean ok = Comms.write(Comms.AD_FLAGS, v & ~(1 << (C.PROBE_SHIFT + probeIdx)));
                if (G.DEBUG) probeLog("release hq" + probeIdx + " wrote=" + ok);
            }
            probeRelease = false;
        }
        if (C.HOT && well != null && hot(well)) well = null;                          // c_well6
        if (C.PROBE && role == 2 && well == null && !probeDone && probeTurn()) return;   // c_well3
        boolean cool = C.HOT && anyHot();       // c_well6: with no hot well the choice is c_well5's
        MapLocation home = cool ? homeOf(G.here) : null;
        if (home == null) home = G.here;
        if (well == null) {
            if (cool) {
                // nearest to our HQ, not to here: from the front the nearest cool well can be theirs
                well = nearestCool(home, role);
                if (C.TELEMETRY && well != null) wellHook(6, role);
                // every known well of the role is hot: no centre-first search back toward the fight, any cool well now
                if (well == null && (Comms.nearestWell(G.here, role) != null || MapMem.nearestSeenWell(G.here, role) != null))
                    searchTurns = C.WELL_SEARCH_TURNS;
            } else {
                MapLocation sh = Comms.nearestWell(G.here, role);
                well = nearer(sh, MapMem.nearestSeenWell(G.here, role));
                if (C.TELEMETRY && well != null) wellHook(well == sh ? 1 : 2, role);
            }
        }
        if (well == null && ++searchTurns > C.WELL_SEARCH_TURNS) {
            if (cool) {
                well = nearestCool(home, 0);
                if (C.TELEMETRY && well != null) wellHook(7, Comms.lastWellType);
            } else {
                MapLocation sh = Comms.nearestWell(G.here, 0);
                well = nearer(sh, MapMem.nearestSeenWell(G.here, 0));
                if (C.TELEMETRY && well != null) wellHook(well == sh ? 3 : 4, well == sh ? Comms.lastWellType : MapMem.lastSeenType);
            }
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

    // ---------------------------------------------------------------- c_well6: hot wells (C.HOT)
    /** The enemy fighter this carrier last fled near its front well; until hotUntil every front well within
     *  r2 C.HOT_NEAR_D2 of it is hot for this carrier (it is marked in the shared list at the next write turn while
     *  hotPending). The shared hot wells' encodings and the enemy HQ candidates, read once a round. */
    static MapLocation hotSpot;
    static int hotUntil, hotRound = -1, nHot, ehqRound = -1;
    static boolean hotPending;
    static int[] hotEnc = new int[16];
    static MapLocation[] hotEhq;

    /** Whether a well with these squared distances to our nearest HQ and to the nearest enemy HQ candidate is a front
     *  well that may turn hot: farther than r2 C.HOT_HOME_D2 from home, and at least C.HOT_FRONT_PCT percent of the
     *  enemy distance squared (60% of the distance: Forest's midline (29,48) 324 vs 361 is; Pillars' (7,10), 100 vs
     *  740, and MassiveL's (2,0) are home wells). */
    static boolean frontGate(int homeD2, int enemyD2) {
        return homeD2 > C.HOT_HOME_D2 && 100L * homeD2 >= (long) C.HOT_FRONT_PCT * enemyD2;
    }

    static boolean front(MapLocation l) {
        if (ehqRound != G.round) { ehqRound = G.round; hotEhq = MapMem.enemyHQs(); }   // allocates: once a round, lazily
        return frontGate(minD2(l, HQState.ourHQs), minD2(l, hotEhq));
    }

    /** Least squared distance from l to a location in a (nulls skipped); Integer.MAX_VALUE when there is none. No RNG
     *  (HQState.nearest draws on a tie: the RNG stream would differ from c_well5's on maps with no hot well). */
    static int minD2(MapLocation l, MapLocation[] a) {
        int bd = Integer.MAX_VALUE;
        if (a != null) for (int i = a.length; --i >= 0; ) if (a[i] != null) { int d = l.distanceSquaredTo(a[i]); if (d < bd) bd = d; }
        return bd;
    }

    /** Our HQ nearest to l, the first in HQ order on a tie (no RNG); null before the HQs register. */
    static MapLocation homeOf(MapLocation l) {
        MapLocation[] a = HQState.ourHQs;
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        if (a != null) for (int i = 0; i < a.length; i++) { int d = l.distanceSquaredTo(a[i]); if (d < bd) { bd = d; best = a[i]; } }
        return best;
    }

    static void loadHot() throws GameActionException {
        if (hotRound == G.round) return;
        hotRound = G.round;
        nHot = 0;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
            int c = Comms.read(i);
            if (c == 0) break;
            if (c >= 0x4000) hotEnc[nHot++] = c & 0xfff;
        }
    }

    /** At a write turn: every shared front well within r2 C.HOT_NEAR_D2 of hotSpot marked hot (Forest's midline mana
     *  wells (29,48) and (30,48) lie side by side: marking one sent the carrier to the other). */
    static void markHot() throws GameActionException {
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
            int c = Comms.read(i);
            if (c == 0) break;
            MapLocation l = G.dec(c & 0xfff);
            if (l.distanceSquaredTo(hotSpot) <= C.HOT_NEAR_D2 && front(l)) Comms.setHotSlot(i);
        }
        hotRound = -1;                                              // the cache reloads with the new marks
    }

    /** Whether any well is hot for this carrier (its own hot spot or a shared mark). */
    static boolean anyHot() throws GameActionException {
        if (G.round < hotUntil) return true;
        loadHot();
        return nHot > 0;
    }

    /** Whether l is a front well near this carrier's own hot spot (distance first: front() only near the spot). */
    static boolean hotLocal(MapLocation l) throws GameActionException {
        return G.round < hotUntil && l.distanceSquaredTo(hotSpot) <= C.HOT_NEAR_D2 && front(l);
    }

    /** Whether l is hot for this carrier: near its own hot spot or marked hot in the shared list. */
    static boolean hot(MapLocation l) throws GameActionException {
        if (hotLocal(l)) return true;
        loadHot();
        if (nHot == 0) return false;
        int e = G.enc(l);
        for (int i = nHot; --i >= 0; ) if (hotEnc[i] == e) return true;
        return false;
    }

    /** The nearest well of type t (0 = any) to `from`, shared or seen by this carrier, that is not hot; null if none
     *  (about 16 x 70 + 32 x 32 bytecodes, plus hot() for each seen well that is nearer than the best so far).
     *  Telemetry: Comms.lastWellType and lastWellCount as in Comms.nearestWell. */
    static MapLocation nearestCool(MapLocation from, int t) throws GameActionException {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE, bt = 0, i;
        for (i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
            int c = Comms.read(i);
            if (c == 0) break;
            int ct = Comms.wellType(c);
            if ((t != 0 && ct != t) || c >= 0x4000) continue;
            MapLocation l = G.dec(c & 0xfff);
            int d = from.distanceSquaredTo(l);
            if (d < bd && !hotLocal(l)) { bd = d; best = l; bt = ct; }
        }
        if (C.TELEMETRY) Comms.lastWellCount = i - Comms.WELLS;
        for (int j = MapMem.seenWellCount(); --j >= 0; ) {
            int st = MapMem.seenWellTypeAt(j);
            if (t != 0 && st != t) continue;
            MapLocation l = MapMem.seenWellAt(j);
            int d = from.distanceSquaredTo(l);
            if (d < bd && !hot(l)) { bd = d; best = l; bt = st; }
        }
        if (C.TELEMETRY) Comms.lastWellType = bt;
        return best;
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
            int t = Comms.wellType(c);
            if (C.ROLES == 3 && role == 2 && t != 2) continue;
            if (C.HOT && (c >= 0x4000 || hotLocal(l))) continue;                         // c_well6: hot
            int d = G.here.distanceSquaredTo(l) + (t == role ? 0 : 400);
            if (d < bd) { bd = d; best = l; if (C.TELEMETRY) bt = t; }
        }
        if (C.TELEMETRY) { Comms.lastWellCount = i - Comms.WELLS; Telemetry.crowdSwitches++; }
        for (int j = MapMem.seenWellCount(); --j >= 0; ) {
            MapLocation l = MapMem.seenWellAt(j);
            if (l.equals(well)) continue;
            if (C.ROLES == 3 && role == 2 && MapMem.seenWellTypeAt(j) != 2) continue;
            if (C.HOT && hot(l)) continue;                                                  // c_well6: hot
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

    // ---------------------------------------------------------------- c_well3: near-well probe (c_well5: made reliable)
    static boolean probeDone, probeInit;
    static int probeTurns, probeFar, nProbe;
    static MapLocation probeHome, publishWell;
    static MapLocation[] probePts = new MapLocation[5];
    /** c_well5: the point aimed at last turn and the turns aimed at it since it was chosen (the stall rule); the HQ
     *  index whose claim this carrier holds; the point count at the claim (the odd-id far-first order holds until a
     *  point is dropped); a claim to release at the next write turn (the probe ended without a find). */
    static MapLocation probeCur;
    static int probeCurTurns, probeIdx, probeN0;
    static boolean probeRelease;

    /**
     * Near-well probe (C.PROBE), called at the top of gather() by a mana carrier with no well. Once per carrier
     * (probeStart): when the nearest HQ's nearest known mana well (shared or seen) is farther than C.PROBE_FAR
     * (Chebyshev) and the round is before C.PROBE_UNTIL, the carrier claims the HQ's probe (Comms.AD_FLAGS bit
     * C.PROBE_SHIFT+i) and visits the 4 diagonals at +-C.PROBE_NEAR from the HQ and the midpoint toward the nearest
     * enemy HQ pulled in to C.PROBE_TOWARD ('X', at most C.PROBE_TURNS turns). c_well5: with no mana well known before
     * C.PROBE_EARLY it visits that midpoint alone, when it is at least C.PROBE_FRONT_MIN from the HQ. Points go nearest
     * first, except that an odd-id prober aims at its farthest point first and keeps it until a point is dropped; a point
     * is dropped when it is within r2 C.PROBE_SEE, a known wall, or stuck on (Nav.stuckOn) after C.PROBE_POINT_TURNS turns
     * aimed at it. A mana well it has seen within C.PROBE_FAR of the HQ and at least 4 nearer than the known one (any,
     * for the front probe) becomes its well, after it has walked it home and published it ('R') when the shared list
     * does not hold it yet. A probe that ends without a find releases the claim (gather()). survive() runs before this,
     * so a prober still flees. Returns true when it took the turn.
     */
    static boolean probeTurn() throws GameActionException {
        if (publishWell == null) {
            if (!probeInit && !probeStart()) { probeDone = true; return false; }
            MapLocation w = MapMem.nearestSeenWell(probeHome, 2);   // found check
            if (w != null && !(C.HOT && hot(w))) {                     // c_well6: never a hot well
                int dw = G.cheb(probeHome, w);
                if (dw <= C.PROBE_FAR && dw + 4 <= probeFar) {
                    if (G.DEBUG) probeLog("found " + w + " cheb=" + dw + " shared=" + Wells.known(w) + " turns=" + probeTurns);
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
            if (wrote || Wells.known(publishWell) || ++probeTurns > 2 * C.PROBE_TURNS) {
                if (G.DEBUG) probeLog("take " + publishWell + " shared=" + Wells.known(publishWell) + " turns=" + probeTurns);
                probeTake(publishWell);
            }
            return true;
        }
        if (++probeTurns > C.PROBE_TURNS) { probeEnd("timeout"); return false; }
        MapLocation best = null, far = null;
        int bd = Integer.MAX_VALUE, fd = -1;
        for (int i = nProbe; --i >= 0; ) {                          // at most 5 points
            MapLocation p = probePts[i];
            int d = G.here.distanceSquaredTo(p);
            // c_well5: covered within r2 C.PROBE_SEE; unreachable only after C.PROBE_POINT_TURNS turns aimed at it
            // (the spec's Nav.stuckOn(p) && p.equals(probeCur) && turns test, cheapest term first)
            if (d <= C.PROBE_SEE || (probeCurTurns >= C.PROBE_POINT_TURNS && p.equals(probeCur) && Nav.stuckOn(p))
                    || (MapMem.known(p.x, p.y) && MapMem.isWall(p.x, p.y))) {
                probePts[i] = probePts[--nProbe];                   // reached or unreachable: dropped (the last point,
                probePts[nProbe] = null;                            // already scored, moves into its place)
                continue;
            }
            if (d < bd) { bd = d; best = p; }
            if (d > fd) { fd = d; far = p; }
        }
        if (best == null) { probeEnd("exhausted"); return false; }
        // c_well5 first-point order: an odd-id prober aims at the point farthest from here first and keeps it until a
        // point is dropped (with 4-5 points: retries of the same HQ then walk different orders); nearest first after
        if ((G.id & 1) == 1 && nProbe == probeN0 && nProbe >= 4) best = probeCur != null ? probeCur : far;
        if (best.equals(probeCur)) probeCurTurns++;
        else {
            probeCur = best;
            probeCurTurns = 0;
            if (G.DEBUG) probeLog("point " + best + " d2=" + G.here.distanceSquaredTo(best) + " left=" + nProbe + " turns=" + probeTurns);
        }
        state = 'X';
        moveTwice(best);
        return true;
    }

    /** c_well5: the probe ended without a find (turn cap or no point left): release the claim at the next write turn. */
    static void probeEnd(String why) {
        if (G.DEBUG) probeLog(why + " turns=" + probeTurns + " left=" + nProbe);
        probeRelease = true;
        probeDone = true;
    }

    /** Once per carrier: whether a probe is needed and this carrier claimed it; sets the probe points. */
    static boolean probeStart() throws GameActionException {
        probeInit = true;
        if (G.round >= C.PROBE_UNTIL) return false;
        MapLocation home = HQState.nearest(G.here);
        if (home == null) { if (G.DEBUG) probeLog("start home=null"); return false; }
        MapLocation k = nearerTo(home, Comms.nearestWell(home, 2), MapMem.nearestSeenWell(home, 2));
        int kc = k == null ? -1 : G.cheb(home, k);
        if (k != null && kc <= C.PROBE_FAR) { if (G.DEBUG) probeStartLog(home, k, kc, null, "near"); return false; }
        MapLocation front = null;
        if (k == null) {
            // c_well5 front probe: no mana well known yet. Only in the opening, and only when the front point is far
            // (Forest (11,48) -> (29,48), cheb 18); Cornucopia's cheb-9 front point keeps today's centre-first explore
            if (G.round >= C.PROBE_EARLY) { if (G.DEBUG) probeStartLog(home, null, kc, null, "none-late"); return false; }
            front = probeFront(home, MapMem.enemyHQs());
            if (front == null || G.cheb(home, front) < C.PROBE_FRONT_MIN) {
                if (G.DEBUG) probeStartLog(home, null, kc, front, "front-near");
                return false;
            }
        }
        int idx = Comms.hqIndex(home);
        if (idx < 0) { if (G.DEBUG) probeStartLog(home, k, kc, front, "no-hq-index"); return false; }
        int v = Comms.read(Comms.AD_FLAGS), bit = 1 << (C.PROBE_SHIFT + idx);
        if ((v & bit) != 0) { if (G.DEBUG) probeStartLog(home, k, kc, front, "taken"); return false; }
        if (!Comms.write(Comms.AD_FLAGS, v | bit)) { if (G.DEBUG) probeStartLog(home, k, kc, front, "write-refused"); return false; }
        probeHome = home;
        probeIdx = idx;
        nProbe = 0;
        if (k == null) {                                            // the front point alone; any near well is a find
            probeFar = 99;
            addProbePt(front.x, front.y);
        } else {
            probeFar = kc;
            addProbePt(home.x - C.PROBE_NEAR, home.y - C.PROBE_NEAR);
            addProbePt(home.x + C.PROBE_NEAR, home.y - C.PROBE_NEAR);
            addProbePt(home.x - C.PROBE_NEAR, home.y + C.PROBE_NEAR);
            addProbePt(home.x + C.PROBE_NEAR, home.y + C.PROBE_NEAR);
            // c_well4's midpoint, except that a distance tie no longer draws from the RNG (none on MassiveL or Forest)
            front = probeFront(home, MapMem.enemyHQs());
            if (front != null) addProbePt(front.x, front.y);
        }
        probeN0 = nProbe;
        if (G.DEBUG) probeStartLog(home, k, kc, front, "claimed hq" + idx + " points=" + nProbe);
        return true;
    }

    /**
     * c_well5: the probe's front point: the midpoint from home toward the nearest of ehq, pulled in to at most
     * C.PROBE_TOWARD (Chebyshev) from home; null when ehq is empty. The midpoint of two on-map tiles is on the map.
     * Forest (11,48) with (48,48) nearest -> (29,48); Cornucopia (29,51) -> cheb 9. Pure: a distance tie goes to the
     * last candidate in array order, never to G.nearest's RNG draw, because the front probe's gate calls this on every
     * mana carrier that knows no mana well before C.PROBE_EARLY, and a draw there would shift the RNG stream on maps
     * where the probe never fires (Cornucopia's (29,51) ties at d2 482 under its true symmetry; Maze's (21,21) ties
     * while the symmetry is undecided).
     */
    static MapLocation probeFront(MapLocation home, MapLocation[] ehq) {
        if (ehq == null) return null;
        MapLocation e = null;
        int bd = Integer.MAX_VALUE;
        for (int i = ehq.length; --i >= 0; ) {                     // at most 12 (3 symmetries x 4 HQs)
            MapLocation l = ehq[i];
            if (l == null) continue;
            int d = home.distanceSquaredTo(l);
            if (d < bd) { bd = d; e = l; }
        }
        if (e == null) return null;
        int dx = (e.x - home.x) / 2, dy = (e.y - home.y) / 2, c = Math.max(Math.abs(dx), Math.abs(dy));
        if (c > C.PROBE_TOWARD) { dx = dx * C.PROBE_TOWARD / c; dy = dy * C.PROBE_TOWARD / c; }
        return new MapLocation(home.x + dx, home.y + dy);
    }

    /** G.DEBUG only: one probe line (grep "PROBE r"). */
    static void probeLog(String s) { System.out.println("PROBE r" + G.round + " #" + G.id + " " + s); }

    /** G.DEBUG only: probeStart's decision (k and front "-" when not known or not computed). */
    static void probeStartLog(MapLocation home, MapLocation k, int kc, MapLocation front, String result) {
        probeLog("start home=" + home + " k=" + (k == null ? "-" : k + " cheb=" + kc) + " front="
            + (front == null ? "-" : front + " cheb=" + G.cheb(home, front)) + " -> " + result);
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
