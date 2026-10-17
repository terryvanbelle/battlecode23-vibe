package c_flee9;

import battlecode.common.*;

/**
 * Carrier: the economy and the anchor courier.
 * c_gp1 = c_guard1 + c_pack1's well packing (C.PACK): near its well a carrier takes the nearest free collect square and
 * a collector steps onto a free well tile (packApproach, packStep).
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
 * c_mid1 (C.MID): at the contested mana well (Mid.site, or its twin) a gathering carrier keeps mining while our
 * launchers in vision outnumber the enemy fighters, none is within r2 C.MID_SAFE_R2 and one of our launchers stands
 * nearer the fighter than the carrier (survive, screened); one that flees there while outnumbered, or waits there
 * C.WELL_CROWD_PATIENCE turns (anywhere within r2 C.MID_AREA_R2, on turns it gets no nearer), leaves the site and its
 * twin for C.MID_AVOID rounds: it walks home, then takes the nearest other well measured from home (midLeave, gather,
 * midOther, switchWell). C.PROBE_FRONT is on again: the front probe is what finds and publishes Forest's pair. C.HOT
 * stays on (c_well9's hot wells) but for the site and its twin: front() is false there (never marked hot), and while a
 * carrier avoids the site hotLocal() is true there (every hot-aware choice skips it).
 * c_flee4 = c_flee1 + bytecode headroom on flight turns: survive's fallback flight takes Nav.moveTo only with
 * C.FLEE4_FALLBACK_LEFT left, else one Nav.moveAway step (c_flee1: 6 carrier overruns on Cornucopia, all on F turns).
 * c_flee1 (C.FLEE1) = c_gp1 + carrier flight: a 4-round memory of enemy fighters (memTurn) keeps the flight going after
 * sight is lost (ghostFlee) and keeps every other move out of r2 C.FLEE1_STAND of a sighting unless strictly outward
 * (Nav.can, moveTwice, unjam, packStep); the flee step is scored over every visible and remembered fighter, one or two
 * steps (fleeMove); a carrier next to an HQ deposits first (bank); a hit carrier of C.FLEE1_LIGHT_W kg or more throws
 * its load (lighten); a second flight from the same well within C.FLEE1_REPEAT rounds drops it, home wells included,
 * unless the alternative is far (noteFlight, hotLocal, gather).
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
    // c_flee1: the fighter memory (gr 0 = empty slot), fleeMove's threat points, the HP watch, the second-flight drop
    // (the well of the last flight, its round, role and telemetry type; the raided point, the drop's end, the raided
    // well's r2 to our nearest HQ, and whether the carrier went back to it for want of a near alternative)
    static final int[] gx = new int[C.FLEE1_N], gy = new int[C.FLEE1_N], gr = new int[C.FLEE1_N];
    static final int[] tx = new int[8], ty = new int[8];
    static int memUntil = -1, lastHp = 150, hurtRound = -100;
    static MapLocation fWell, badAt;
    static int fWellRound = -1000, fRole, fType, badUntil, badD2;
    static boolean badKeep;
    public static int memFlights, lightens, drops;   // diagnostics (indicator mf, lt, dw)
    static int extraSum = -1;                        // the indicator's counters last written to G.extra
    static final ResourceType[] DEPOSIT = {ResourceType.ADAMANTIUM, ResourceType.MANA, ResourceType.ELIXIR};

    static void run() throws GameActionException {
        Nav.danger = false;                                   // c_flee1: set again by ghostFlee while a sighting is live
        RobotController rc = G.rc;
        if (C.ROLES == 3) Comms.censusTick();
        if (G.here.equals(lastLoc)) stillTurns++; else { stillTurns = 0; lastLoc = G.here; }
        if (role == 0) { role = pickRole(); if (C.TELEMETRY) Telemetry.emitRole(0, role, 0, -1, -1, 0, trips); }
        MapMem.scan();
        if ((G.round + G.id) % 3 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        reportEnemies();
        if (C.FLEE1) memTurn();
        // c_guard1: the fighter it last fled, reported at the first write turn (raiders at a home well 12 tiles out are
        // beyond every writer's reach)
        if (C.GUARD && fledFrom != null && Comms.canWrite) {
            if (G.round - fledRound <= C.GUARD_REPORT_AGE) {
                Comms.reportEnemy(fledFrom);
                if (G.DEBUG) System.out.println("GUARD r" + G.round + " #" + G.id + " report " + fledFrom + " seen r" + fledRound);
            }
            fledFrom = null;
        }
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
            // c_flee1: Nav.can (canMove plus the stand-off while a sighting is live): the random step never ends inside a ring
            if (Nav.can(d)) { G.rc.move(d); G.here = G.rc.getLocation(); stillTurns = 0; lastLoc = G.here; unjams++; return; }
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
        if (C.FLEE1) {
            // c_flee1 counters (mf memory flights, lt lightening throws, dw well drops, rb stand-off refusals): rebuilt only
            // when one changed (each only grows, so their sum is the dirty test); rb last, as the 64-character cut drops
            // whole trailing fields and rb is the longest number
            int sum = memFlights + lightens + drops + Nav.ringBlocks;
            if (sum != extraSum) {
                extraSum = sum;
                G.extra = ",mf=" + memFlights + ",lt=" + lightens + ",dw=" + drops + ",rb=" + Nav.ringBlocks;
            }
        }
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

    /** c_guard1: the nearest fighter in vision at this carrier's last survive() turn out of write range, and its round. */
    static MapLocation fledFrom;
    static int fledRound;

    static void reportEnemies() throws GameActionException {
        if (!Comms.canWrite || G.nEnemyFighters == 0) return;
        for (int i = G.enemies.length; --i >= 0; ) {
            RobotInfo e = G.enemies[i];
            if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) { Comms.reportEnemy(e.location); return; }
        }
    }

    /** Flee from armed enemies in vision; throw the load at an adjacent-range fighter when hurt and cornered. c_flee1:
     *  with none in vision, the flight from memory (ghostFlee); with one, the second-flight note, the deposit next to an
     *  HQ, the lightening throw and the scored flight (fleeMove). */
    static boolean survive() throws GameActionException {
        if (G.nEnemyFighters == 0) return C.FLEE1 && C.FLEE1_MEMORY && ghostFlee();
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
        if (C.GUARD && !Comms.canWrite) { fledFrom = threat.location; fledRound = G.round; }
        // c_mid1: at the site, gathering (not returning), our launchers ahead in vision, no fighter in attack range and
        // one of ours nearer the fighter than this carrier: keep mining (the squad fights); outnumbered there: flee, and
        // leave the site through home for C.MID_AVOID rounds (no walking back into the fire)
        boolean site = C.MID && well != null && G.here.distanceSquaredTo(well) <= C.MID_AREA_R2 && Mid.isSite(well);
        if (site) {
            if (!returning && G.nAllyFighters > G.nEnemyFighters && bd > C.MID_SAFE_R2 && screened(threat.location, bd)) return false;
            if (G.nEnemyFighters > G.nAllyFighters) midLeave();
        }
        if (C.FLEE1 && C.FLEE1_DROP && !site) noteFlight(threat.location);   // c_flee1: the site keeps c_mid1's rules
        // c_well6: a fighter near this carrier's front well makes the front wells around it hot (gather() drops the
        // well; marked in the shared list at the next write turn)
        if (C.HOT && well != null && well.distanceSquaredTo(threat.location) <= C.HOT_NEAR_D2 && front(well)) {
            hotSpot = threat.location;
            hotUntil = G.round + C.HOT_LOCAL;
            hotPending = true;
        }
        int w = rc.getWeight(), w0 = w;                      // w0: the FLEE record's weight, as in c_gp1
        boolean threw = false;
        // c_flee1: home above the throw (the same single HQState.nearest call, so the same RNG draw as c_gp1)
        MapLocation home = HQState.nearest(G.here);
        if (C.FLEE1 && C.FLEE1_BANK && bank(home)) w = rc.getWeight();
        if (C.FLEE1 && C.FLEE1_LIGHTEN && shouldLighten(w, rc.getNumAnchors(null), bd, G.round, hurtRound)
                && lighten(threat.location)) { threw = true; w = 0; }
        if (!threw && w >= 8 && bd <= 9 && rc.getHealth() <= 60 && rc.canAttack(threat.location)) {
            rc.attack(threat.location);   // throws everything: worth it only when the carrier is about to die
            throwsMade++;
            returning = false;
            threw = true;
        }
        boolean moved = false;
        int fm = -1;                                          // fleeMove's result; -1: not run or not scanned
        if (C.FLEE1 && C.FLEE1_MOVE && Clock.getBytecodesLeft() > C.FLEE1_MIN_LEFT + 500) {
            fm = fleeMove(home, C.FLEE1_MIN_LEFT);
            moved = fm > 0;
            if (moved && C.FLEE1_BANK && !threw) bank(home);   // the flight may end next to an HQ
        }
        if (fm < 0 && C.FLEE1_MOVE && Clock.getBytecodesLeft() < C.FLEE4_FALLBACK_LEFT) {
            // c_flee4: too few bytecodes for c_gp1's flight (Nav.moveTo's bug nav costs thousands): one step away. c_flee1
            // ran Nav.moveTo here with as little as ~2,000 left: 6 carrier overruns on Cornucopia, all on F turns.
            moved = Nav.moveAway(threat.location);
        } else if (fm < 0) {                                  // c_gp1's flight (also when the single steps went unscored)
            if (home != null && home.distanceSquaredTo(threat.location) > G.here.distanceSquaredTo(threat.location))
                moved = Nav.moveTo(home);
            if (!moved) moved = Nav.moveAway(threat.location);
            if (moved && G.rc.isMovementReady()) {               // light carriers move twice a turn (cooldown 5 + 0.375 w)
                if (home != null && home.distanceSquaredTo(threat.location) > G.rc.getLocation().distanceSquaredTo(threat.location))
                    { if (!Nav.moveTo(home)) Nav.moveAway(threat.location); }
                else Nav.moveAway(threat.location);
            }
        }
        if (moved) fled++;
        if (C.TELEMETRY && (moved || bd <= 20) && (threw || (prevState != 'F' && prevState != 'V')))
            Telemetry.emitFlee(bd, G.nEnemyFighters, rc.getHealth(), threw, moved, Telemetry.loc12(threat.location), w0,
                Telemetry.loc12(home), G.round);
        return moved || bd <= 20 || hold();
    }

    /** c_flee9: after a flight check that left the carrier in place: with fewer than C.FLEE9_REST bytecodes left it
     *  collects if it is at its well and ends the turn (true), since deliver/gather/explore could overrun. */
    static boolean hold() throws GameActionException {
        if (!C.FLEE9_HOLD || Clock.getBytecodesLeft() >= C.FLEE9_REST) return false;
        holds++;
        RobotController rc = G.rc;
        if (well != null && !returning && rc.getLocation().distanceSquaredTo(well) <= 2) {
            while (rc.isActionReady() && rc.getWeight() < C.CARRIER_RETURN_LOAD) {
                int room = C.CARRIER_RETURN_LOAD - rc.getWeight();
                if (rc.canCollectResource(well, -1)) rc.collectResource(well, -1);
                else if (rc.canCollectResource(well, room)) rc.collectResource(well, room);
                else break;
            }
            if (rc.getWeight() >= C.CARRIER_RETURN_LOAD) returning = true;
        }
        return true;
    }
    public static int holds;   // diagnostics

    // ---------------------------------------------------------------- c_flee1: carrier flight (C.FLEE1)
    /** Every turn after reportEnemies: an HP loss with no fighter in vision leaves a ghost on this square (the shooter
     *  is unseen: a cloud's vision is r2 4); the fighters in vision are stored; Nav's live list (points seen in the last
     *  C.FLEE1_MEM rounds within r2 C.FLEE1_NEAR_R2) is computed once for the turn. About 20 bytecodes with no
     *  sighting in the last C.FLEE1_MEM rounds and no hit. */
    static void memTurn() throws GameActionException {
        int hp = G.rc.getHealth();
        if (hp < lastHp) {
            hurtRound = G.round;
            if (C.FLEE1_MEMORY && G.nEnemyFighters == 0) memAdd(G.here.x, G.here.y);
        }
        lastHp = hp;
        if (C.FLEE1_MEMORY && G.nEnemyFighters > 0) remember();
        Nav.ringN = !C.FLEE1_MEMORY || G.round > memUntil ? 0
            : liveNear(gx, gy, gr, G.round - C.FLEE1_MEM, G.here.x, G.here.y, C.FLEE1_NEAR_R2, Nav.ringX, Nav.ringY);
    }

    /** The launchers and destabilizers in vision, at most C.FLEE1_N of them, into the memory. */
    static void remember() {
        for (int i = G.enemies.length, m = 0; --i >= 0 && m < C.FLEE1_N; ) {
            RobotInfo e = G.enemies[i];
            if (e.type != RobotType.LAUNCHER && e.type != RobotType.DESTABILIZER) continue;
            m++;
            if (!memAdd(e.location.x, e.location.y)) break;
        }
    }

    /** One sighting this round at (x,y); false when every slot was already written this round. */
    static boolean memAdd(int x, int y) {
        int k = slot(gx, gy, gr, x, y, G.round);
        if (k < 0) return false;
        gx[k] = x; gy[k] = y; gr[k] = G.round; memUntil = G.round + C.FLEE1_MEM;
        return true;
    }

    /** Pure: the slot of a stored sighting within r2 C.FLEE1_MERGE_R2 not written this round (the same fighter, moved),
     *  else the oldest slot not written this round (empty first); -1 when every slot was written this round (round r). */
    static int slot(int[] gx, int[] gy, int[] gr, int x, int y, int r) {
        int k = -1, old = r;
        for (int j = gr.length; --j >= 0; ) {
            if (gr[j] == r) continue;
            int dx = gx[j] - x, dy = gy[j] - y;
            if (gr[j] > 0 && dx * dx + dy * dy <= C.FLEE1_MERGE_R2) return j;
            if (gr[j] < old) { old = gr[j]; k = j; }
        }
        return k;
    }

    /** Pure: copies the entries seen at rounds >= r0 (gr > 0: an empty slot is never live) within r2 near of (x,y)
     *  into (lx,ly), which hold at least gr.length; returns the count. */
    static int liveNear(int[] gx, int[] gy, int[] gr, int r0, int x, int y, int near, int[] lx, int[] ly) {
        int n = 0;
        for (int j = gr.length; --j >= 0; ) {
            if (gr[j] <= 0 || gr[j] < r0) continue;
            int dx = gx[j] - x, dy = gy[j] - y;
            if (dx * dx + dy * dy <= near) { lx[n] = gx[j]; ly[n++] = gy[j]; }
        }
        return n;
    }

    /** Pure: the index of the point nearest (x,y) within r2 C.FLEE1_STAND, or -1. */
    static int ghostAt(int x, int y, int[] lx, int[] ly, int n) {
        int bd = C.FLEE1_STAND + 1, b = -1;
        for (int k = n; --k >= 0; ) { int dx = x - lx[k], dy = y - ly[k], d = dx * dx + dy * dy; if (d < bd) { bd = d; b = k; } }
        return b;
    }

    /** Pure, larger is safer: fewer shots (4 per fighter within r2 16, 2 within C.THREAT_R2, 1 within C.FLEE1_STAND),
     *  then the larger least r2 to a fighter (capped at C.FLEE1_STAND + 1), then nearer (hx,hy). n <= 8: the danger sum
     *  is at most 32 < 64 and the capped r2 under 128, so the three fields never overlap. */
    static int fleeScore(int x, int y, int[] tx, int[] ty, int n, int hx, int hy) {
        int danger = 0, mn = C.FLEE1_STAND + 1;
        for (int j = n; --j >= 0; ) {
            int dx = x - tx[j], dy = y - ty[j], d = dx * dx + dy * dy;
            if (d <= C.FLEE1_STAND) { danger += d <= 16 ? 4 : d <= C.THREAT_R2 ? 2 : 1; if (d < mn) mn = d; }
        }
        int dh = (x - hx) * (x - hx) + (y - hy) * (y - hy);
        return ((64 - danger) << 20) + (mn << 13) + 8191 - (dh < 8191 ? dh : 8191);
    }

    /** Pure: a carrier's move cooldown at weight w (RULES 5.1: floor(0.375 w) + 5, times 1.2 rounded on a cloud
     *  destination; no x.5 cases there). Boosts, destabilizers and anchors are left out (estimate). */
    static int moveCost(int w, boolean cloud) { int b = (int) (0.375f * w) + 5; return cloud ? (b * 12 + 5) / 10 : b; }

    /** Pure: throw the load to flee faster: C.FLEE1_LIGHT_W kg or more (one move a turn or fewer), no anchor, a fighter
     *  within C.THREAT_R2 and hit within C.FLEE1_HURT rounds. In play the bd term always holds (G.enemies is vision,
     *  r2 20 or 4 on a cloud, inside THREAT_R2 26): by design every fighter in vision can step and shoot next turn. */
    static boolean shouldLighten(int w, int anchors, int bd, int round, int hurt) {
        return w >= C.FLEE1_LIGHT_W && anchors == 0 && bd <= C.THREAT_R2 && round - hurt <= C.FLEE1_HURT;
    }

    /** Pure: an alternative at r2 altD2 from our nearest HQ is too far to replace a raided well at r2 raidD2 (raidD2
     *  capped at 10,000 before x4: minD2 is Integer.MAX_VALUE with no HQ). */
    static boolean farAlt(int altD2, int raidD2) { return altD2 > Math.max(C.FLEE1_ALT_D2, 4 * Math.min(raidD2, 10000)); }

    /** Pure: the raided well comes back when there is no alternative of the role (none, or only the any-type
     *  fallback's), or when the alternative at r2 altD2 from our nearest HQ is far (farAlt). */
    static boolean backToRaided(boolean noRoleAlt, int altD2, int raidD2) { return noRoleAlt || farAlt(altD2, raidD2); }

    /** fleeMove's single-step scores by G.DIRS index (Integer.MIN_VALUE: not movable, or already expanded). */
    static final int[] s1 = new int[8];
    static final boolean[] c1 = new boolean[8];

    /**
     * The scored flight: stay, one step or two steps (two when the cooldown allows a second move after the first, the
     * first step's cloud counted), to the square with the best fleeScore over every launcher and destabilizer in vision
     * and every live remembered one (this round's entries repeat the visible fighters, except a ghost left by a hit
     * with none in vision), each square scored where its current pushes it (currents, clouds, walls and robots sensed
     * live). Pass 1 scores all 8 single steps (no direction order bias); pass 2 expands second steps from the first
     * steps in descending single-step score. Bytecodes are checked before each square: pass 1 stops below `floor`,
     * pass 2 below floor + (C.FLEE1_GUARD - C.FLEE1_MIN_LEFT), so the flight ends with about `floor` left. Returns 1 when
     * it moved, 0 when it stayed (movement not ready, or no scored square beats staying), -1 when pass 1 was cut short
     * before any step beat staying (the caller's fallback flight runs).
     */
    static int fleeMove(MapLocation home, int floor) throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.isMovementReady()) return 0;
        int n = 0, r0 = G.round - C.FLEE1_MEM;
        for (int i = G.enemies.length; --i >= 0 && n < 8; ) {
            RobotInfo e = G.enemies[i];
            if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) { tx[n] = e.location.x; ty[n++] = e.location.y; }
        }
        if (C.FLEE1_MEMORY)
            for (int j = C.FLEE1_N; --j >= 0 && n < 8; )
                if (gr[j] > 0 && gr[j] >= r0 && (gr[j] != G.round || G.nEnemyFighters == 0)) { tx[n] = gx[j]; ty[n++] = gy[j]; }
        if (n == 0) return 0;
        MapLocation here = rc.getLocation();
        int hx = home == null ? here.x : home.x, hy = home == null ? here.y : home.y;
        int w = rc.getWeight(), cd = rc.getMovementCooldownTurns();
        int best = scoreCur(here.x, here.y, rc.senseMapInfo(here).getCurrentDirection(), n, hx, hy);
        Direction b1 = null, b2 = null;
        int i = 8;
        while (--i >= 0) {                                          // pass 1: every single step
            if (Clock.getBytecodesLeft() < floor) break;
            Direction d = G.DIRS[i];
            int s = Integer.MIN_VALUE;
            if (rc.canMove(d)) {
                MapLocation a = here.add(d);
                MapInfo mi = rc.senseMapInfo(a);                    // adjacent: sensable even on a cloud (r2 4)
                c1[i] = mi.hasCloud();
                s = scoreCur(a.x, a.y, mi.getCurrentDirection(), n, hx, hy);
                if (s > best) { best = s; b1 = d; }
            }
            s1[i] = s;
        }
        if (i >= 0) { if (b1 == null) return -1; }                  // cut short: no pass 2
        else if (cd + moveCost(w, false) < 10) {                    // pass 2: second steps, best first steps first
            int guard = floor + C.FLEE1_GUARD - C.FLEE1_MIN_LEFT;
            outer:
            for (int j; (j = takeBest(s1)) >= 0; ) {
                if (cd + moveCost(w, c1[j]) >= 10) continue;         // no second move after this first step
                Direction d = G.DIRS[j];
                int ax = here.x + d.dx, ay = here.y + d.dy;
                for (int k = 3; --k >= 0; ) {
                    if (Clock.getBytecodesLeft() < guard) break outer;
                    Direction e = k == 2 ? d : k == 1 ? d.rotateLeft() : d.rotateRight();
                    int cx = ax + e.dx, cy = ay + e.dy;
                    if (!G.onMap(cx, cy)) continue;                  // canSenseLocation does not check the map
                    MapLocation c = new MapLocation(cx, cy);
                    if (!rc.canSenseLocation(c)) continue;           // out of sight (a cloud): not a target
                    MapInfo mi = rc.senseMapInfo(c);
                    if (!mi.isPassable() || rc.isLocationOccupied(c)) continue;
                    int s = scoreCur(cx, cy, mi.getCurrentDirection(), n, hx, hy);
                    if (s > best) { best = s; b1 = d; b2 = e; }
                }
            }
        }
        if (b1 == null) return 0;
        rc.move(b1);                                    // canMove(b1) checked this turn, nothing changed since
        if (b2 != null && rc.canMove(b2)) rc.move(b2);
        G.here = rc.getLocation();
        return 1;
    }

    /** Pure: the index of the largest entry above Integer.MIN_VALUE (the highest index on a tie), which is then set to
     *  Integer.MIN_VALUE; -1 when there is none. */
    static int takeBest(int[] s) {
        int b = -1, bs = Integer.MIN_VALUE;
        for (int q = s.length; --q >= 0; ) if (s[q] > bs) { bs = s[q]; b = q; }
        if (b >= 0) s[b] = Integer.MIN_VALUE;
        return b;
    }

    /** fleeScore of the square (x,y), on the map by construction, where its current c pushes it (when the push square
     *  is on the map and not a known wall). */
    static int scoreCur(int x, int y, Direction c, int n, int hx, int hy) {
        if (c != null && c != Direction.CENTER && G.onMap(x + c.dx, y + c.dy) && !MapMem.isWall(x + c.dx, y + c.dy)) { x += c.dx; y += c.dy; }
        return fleeScore(x, y, tx, ty, n, hx, hy);
    }

    /** Deposit first: a loaded carrier without an anchor next to `home` (r2 2) with its action ready transfers its load
     *  (one resource type an action), with deliver's trip accounting when it is empty. Returns whether it transferred. */
    static boolean bank(MapLocation home) throws GameActionException {
        RobotController rc = G.rc;
        if (home == null || rc.getWeight() == 0 || rc.getNumAnchors(null) > 0 || !rc.isActionReady()
                || rc.getLocation().distanceSquaredTo(home) > 2) return false;
        int load = 0;
        for (int i = 0; i < 3 && rc.isActionReady(); i++) {
            ResourceType t = DEPOSIT[i];
            int a = rc.getResourceAmount(t);
            if (a > 0 && rc.canTransferResource(home, t, a)) { rc.transferResource(home, t, a); load += a; }
        }
        if (load == 0) return false;
        if (rc.getWeight() == 0) {
            returning = false;
            trips++;
            if (C.TELEMETRY) Telemetry.trip(home, load, role, well, wellType);
        }
        return true;
    }

    /** Throw the whole load (RULES 3.4) to move faster: at the fighter when it is in throw range, else at the square
     *  next to this carrier toward it (between two squares on the map, so on the map). Returns whether it threw. */
    static boolean lighten(MapLocation t) throws GameActionException {
        RobotController rc = G.rc;
        MapLocation at = t;
        if (!rc.canAttack(at)) {
            MapLocation h = rc.getLocation();
            at = h.add(h.directionTo(t));
            if (!rc.canAttack(at)) return false;
        }
        rc.attack(at);
        throwsMade++;
        lightens++;
        returning = false;
        return true;
    }

    /**
     * The flight from memory, with no fighter in vision (survive): while a sighting is live (Nav.ringN), every move this
     * turn keeps the stand-off (Nav.danger); inside a ring (r2 C.FLEE1_STAND of a live point) the carrier deposits if it
     * can and takes the scored flight (or steps away from the nearest point when the bytecodes are short). Outside
     * every ring, or when no step improves on staying, it works as usual and never steps in. c_mid1's site with our
     * launchers in vision keeps c_mid1's rule (no flight from memory there).
     */
    static boolean ghostFlee() throws GameActionException {
        if (Nav.ringN == 0) return false;
        if (C.MID && G.nAllyFighters > 0 && well != null && G.here.distanceSquaredTo(well) <= C.MID_AREA_R2 && Mid.isSite(well)) return false;
        Nav.danger = true;
        int g = ghostAt(G.here.x, G.here.y, Nav.ringX, Nav.ringY, Nav.ringN);
        if (g < 0) return false;
        MapLocation home = homeOf(G.here), gl = new MapLocation(Nav.ringX[g], Nav.ringY[g]);   // homeOf: no RNG
        if (C.FLEE1_BANK) bank(home);
        // floor C.FLEE1_GHOST_LEFT: a carrier that stays goes on to deliver, gather or explore this turn
        int fm = C.FLEE1_MOVE && Clock.getBytecodesLeft() > C.FLEE1_GHOST_LEFT + 500 ? fleeMove(home, C.FLEE1_GHOST_LEFT) : -1;
        boolean moved = fm > 0 || (fm < 0 && Nav.moveAway(gl));
        if (!moved) return hold();                            // c_flee9: stayed, and short of bytecodes: the turn ends
        if (C.FLEE1_BANK) bank(home);
        fled++;
        memFlights++;
        if (C.TELEMETRY && prevState != 'F' && prevState != 'V')
            Telemetry.emitFlee(G.here.distanceSquaredTo(gl), 0, G.rc.getHealth(), false, true, Telemetry.loc12(gl),
                G.rc.getWeight(), Telemetry.loc12(home), G.round);       // enemy_fighters 0: a flight from memory
        return true;
    }

    /** The second-flight drop: the first turn of a flight (not F or V last turn) from a fighter within r2
     *  C.FLEE1_WELL_R2 of this carrier's well counts for the well; a second one from the same well within
     *  C.FLEE1_REPEAT rounds drops it (any well: hotLocal) for C.FLEE1_AVOID rounds. Local only (no shared mark). */
    static void noteFlight(MapLocation t) throws GameActionException {
        if (well == null || prevState == 'F' || prevState == 'V' || well.distanceSquaredTo(t) > C.FLEE1_WELL_R2) return;
        if (well.equals(fWell) && G.round - fWellRound <= C.FLEE1_REPEAT) {
            badAt = t;
            badUntil = G.round + C.FLEE1_AVOID;
            badKeep = false;
            badD2 = minD2(well, HQState.ourHQs);
            drops++;
        }
        fWell = well;
        fWellRound = G.round;
        fRole = role;
        fType = wellType;
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
        boolean avoid = C.MID && G.round < midAvoidUntil;                               // c_mid1: not the site for now
        if (avoid && well != null && Mid.isSite(well)) well = null;
        // c_mid1: a carrier leaving the site walks home first ('R') and chooses its next well there (midLeave)
        if (midHome) {
            MapLocation h = homeOf(G.here);
            if (!avoid || h == null || G.here.distanceSquaredTo(h) <= C.MID_HOME_D2) midHome = false;
            else { state = 'R'; moveTwice(h); return; }
        }
        if (C.PROBE && role == 2 && well == null && !probeDone && probeTurn()) return;   // c_well3
        boolean cool = C.HOT && anyHot();       // c_well6: with no hot well the choice is c_well5's
        MapLocation home = cool ? homeOf(G.here) : null;
        if (home == null) home = G.here;
        boolean anyType = false;                // c_flee1: the any-type fallback chose this turn's well
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
                // c_mid1: not the site: the nearest other well measured from home (WELL source 6, as c_well6's cool
                // choice above, which skips the site through hotLocal): from the front the nearest can be the enemy's
                // ((51,12) from x >= 30)
                if (avoid && Mid.isSite(well)) { well = midOther(midFrom(), role); if (C.TELEMETRY && well != null) wellHook(6, role); }
                else if (C.TELEMETRY && well != null) wellHook(well == sh ? 1 : 2, role);
            }
        }
        if (well == null && ++searchTurns > C.WELL_SEARCH_TURNS) {
            anyType = true;
            if (cool) {
                well = nearestCool(home, 0);
                if (C.TELEMETRY && well != null) wellHook(7, Comms.lastWellType);
            } else {
                MapLocation sh = Comms.nearestWell(G.here, 0);
                well = nearer(sh, MapMem.nearestSeenWell(G.here, 0));
                if (avoid && Mid.isSite(well)) { well = midOther(midFrom(), 0); if (C.TELEMETRY && well != null) wellHook(7, Comms.lastWellType); }   // c_mid1
                else if (C.TELEMETRY && well != null) wellHook(well == sh ? 3 : 4, well == sh ? Comms.lastWellType : MapMem.lastSeenType);
            }
        }
        // c_flee1: a dropped (raided) well comes back when no alternative of the role is near: none, one of another type
        // (the any-type fallback: a mana carrier kept mining a home Ad well, and the deposit re-pick never undid it), or
        // one more than max(C.FLEE1_ALT_D2, 4 x the raided well's r2) from our nearest HQ; no home wait (memory and
        // stand-off guard it). WELL source 0 (kept_hot): a hot well kept for want of a cool one
        if (C.FLEE1 && G.round < badUntil && !badKeep && fWell != null && role == fRole
                && backToRaided(well == null || anyType, well == null ? 0 : minD2(well, HQState.ourHQs), badD2)) {
            well = fWell;
            badKeep = true;
            if (C.TELEMETRY) wellHook(0, fType);
        }
        if (well == null) { state = 'X'; explore(); return; }
        searchTurns = 0;
        state = 'G';
        int d = G.here.distanceSquaredTo(well);
        if (d > 2) {
            boolean ready = rc.isMovementReady();
            if (C.PACK && d <= C.PACK_R2) packApproach(well);
            else moveTwice(well);
            int d1 = rc.getLocation().distanceSquaredTo(well);
            // c_mid1: at the site the queue reaches past r2 8 (51-57 of our carriers within r2 64 of Forest's pair from
            // r600, 3.4-4.2 of them on its collect tiles): a move-ready turn there without getting nearer ticks too
            boolean site = C.MID && d1 > 8 && d1 <= C.MID_AREA_R2 && ready && d1 >= d && Mid.isSite(well);
            d = d1;
            if ((d <= 8 && d > 2) || site) {                // near the well but not at it: crowded (one tick a turn)
                state = 'W';
                if (++crowdTurns > C.WELL_CROWD_PATIENCE) {
                    crowdTurns = 0;
                    state = 'S';
                    // c_mid1: a crowded site is left whole, through home (switchWell bounced carriers between the pair's
                    // two wells: 249 and 227 switches, and from the front it picks wells down the central corridor)
                    if (C.MID && Mid.isSite(well)) { midLeave(); well = null; if (C.TELEMETRY) Telemetry.crowdSwitches++; }
                    else switchWell();
                }
            }
        }
        if (well != null && rc.getLocation().distanceSquaredTo(well) <= 2) {   // switchWell may have dropped the well
            if (C.PACK) packStep(well);
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

    /** c_mid1: the round until which this carrier leaves the site alone (it fled there while outnumbered, or the site
     *  was crowded); midHome: it walks home before choosing its next well (gather). */
    static int midAvoidUntil;
    static boolean midHome;

    /** c_mid1: leave the site (and its twin) for C.MID_AVOID rounds, through home: from Forest's pair the nearest other
     *  mana well, (8,12), lies down the central corridor, where 54 of the 58 carriers that chose it there died (median
     *  13 rounds after the choice). The way home is the way the carrier came. */
    static void midLeave() {
        midAvoidUntil = G.round + C.MID_AVOID;
        midHome = true;
    }

    /** c_mid1: where a carrier avoiding the site measures its next well from: its nearest HQ (no RNG), else here. */
    static MapLocation midFrom() {
        MapLocation h = homeOf(G.here);
        return h != null ? h : G.here;
    }

    /** c_mid1: whether one of our launchers in vision stands nearer t than this carrier (dist2 bd). */
    static boolean screened(MapLocation t, int bd) {
        RobotInfo[] nb = G.nearby;
        Team us = G.us;
        for (int i = nb.length; --i >= 0; ) {
            RobotInfo r = nb[i];
            if (r.team == us && r.type == RobotType.LAUNCHER && r.location.distanceSquaredTo(t) < bd) return true;
        }
        return false;
    }

    /** c_mid1: the nearest well of type t (0 = any) to `from`, shared or seen by this carrier, that is not the site or
     *  its twin (r2 C.MID_TWIN_R2); null if none (about 16 x 40 + 32 x 30 bytecodes, only while avoiding the site).
     *  Telemetry: Comms.lastWellType and lastWellCount as in Comms.nearestWell. */
    static MapLocation midOther(MapLocation from, int t) throws GameActionException {
        MapLocation best = null, s = Mid.site();
        int bd = Integer.MAX_VALUE, bt = 0, i;
        for (i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
            int c = Comms.read(i);
            if (c == 0) break;
            int ct = Comms.wellType(c);
            if (t != 0 && ct != t) continue;
            MapLocation l = G.dec(c & 0xfff);
            int d = from.distanceSquaredTo(l);
            if (d < bd && (s == null || s.distanceSquaredTo(l) > C.MID_TWIN_R2)) { bd = d; best = l; bt = ct; }
        }
        if (C.TELEMETRY) Comms.lastWellCount = i - Comms.WELLS;
        for (int j = MapMem.seenWellCount(); --j >= 0; ) {
            int st = MapMem.seenWellTypeAt(j);
            if (t != 0 && st != t) continue;
            MapLocation l = MapMem.seenWellAt(j);
            int d = from.distanceSquaredTo(l);
            if (d < bd && (s == null || s.distanceSquaredTo(l) > C.MID_TWIN_R2)) { bd = d; best = l; bt = st; }
        }
        if (C.TELEMETRY) Comms.lastWellType = bt;
        return best;
    }

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

    static boolean front(MapLocation l) throws GameActionException {
        if (C.MID && Mid.isSite(l)) return false;   // c_mid1: the site and its twin are the squad's (survive, midLeave)
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
        if (G.round < hotUntil || (C.FLEE1 && G.round < badUntil && !badKeep)) return true;   // c_flee1: a dropped well
        loadHot();
        return nHot > 0;
    }

    /** Whether l is a front well near this carrier's own hot spot (distance first: front() only near the spot). */
    static boolean hotLocal(MapLocation l) throws GameActionException {
        if (C.MID && G.round < midAvoidUntil && Mid.isSite(l)) return true;   // c_mid1: a carrier leaving the site
        // c_flee1: a well near the point of a second flight (any well, home wells included) until the drop ends or the
        // carrier went back to it for want of a near alternative
        if (C.FLEE1 && G.round < badUntil && !badKeep && l.distanceSquaredTo(badAt) <= C.FLEE1_WELL_R2) return true;
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
    /** c_pack1: near the well, walk to the nearest free collect square (packTarget), up to two steps; hold when none. */
    static void packApproach(MapLocation well) throws GameActionException {
        RobotController rc = G.rc;
        for (int k = 0; k < 2 && rc.isMovementReady() && G.here.distanceSquaredTo(well) > 2; k++) {
            MapLocation t = packTarget(well);
            if (t == null) return;
            Nav.moveTo(t);
        }
    }

    /** c_pack1: the free collect square of `well` nearest this carrier (the well tile or a neighbour: on the map,
     *  passable, no robot, no current), or null when there is none or our carrier on the well tile is full (its way
     *  out must stay open). */
    static MapLocation packTarget(MapLocation well) throws GameActionException {
        RobotController rc = G.rc;
        if (!rc.canSenseLocation(well)) return well;
        RobotInfo on = rc.senseRobotAtLocation(well);
        if (on != null && on.team == G.us && on.type == RobotType.CARRIER && load(on) >= C.CARRIER_RETURN_LOAD) return null;
        boolean[] free = new boolean[9];
        for (int i = 9; --i >= 0; ) {
            MapLocation l = i == 8 ? well : well.add(G.DIRS[i]);
            if (!rc.canSenseLocation(l) || rc.senseRobotAtLocation(l) != null) continue;
            MapInfo mi = rc.senseMapInfo(l);
            free[i] = mi.isPassable() && mi.getCurrentDirection() == Direction.CENTER;
        }
        return packPick(G.here, well, free);
    }

    /** c_pack1: the free square (free[i]: the well's neighbour in G.DIRS[i], free[8]: the well tile) nearest `here`,
     *  the well tile on a tie; null when none is free. */
    static MapLocation packPick(MapLocation here, MapLocation well, boolean[] free) {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = 9; --i >= 0; ) {
            if (!free[i]) continue;
            MapLocation l = i == 8 ? well : well.add(G.DIRS[i]);
            int dd = here.distanceSquaredTo(l);
            if (dd < bd) { bd = dd; best = l; }
        }
        return best;
    }

    static int load(RobotInfo r) {
        return r.getResourceAmount(ResourceType.ADAMANTIUM) + r.getResourceAmount(ResourceType.MANA)
            + r.getResourceAmount(ResourceType.ELIXIR) + 40 * r.getTotalAnchors();
    }

    /** c_pack1: a collector next to the well with more than C.PACK_MARGIN kg of room steps onto the free well tile
     *  (not onto a current, nor into a cloud from clear air), freeing its square for a queued carrier. */
    static void packStep(MapLocation well) throws GameActionException {
        RobotController rc = G.rc;
        if (G.here.equals(well) || !rc.isMovementReady() || rc.getWeight() > C.CARRIER_RETURN_LOAD - C.PACK_MARGIN) return;
        Direction dir = G.here.directionTo(well);
        if (!Nav.can(dir)) return;                       // c_flee1: canMove plus the stand-off
        MapInfo mi = rc.senseMapInfo(well);
        if (mi.getCurrentDirection() != Direction.CENTER || (mi.hasCloud() && !rc.senseMapInfo(G.here).hasCloud())) return;
        rc.move(dir);
        G.here = rc.getLocation();
    }

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
            if (C.MID && G.round < midAvoidUntil && Mid.isSite(l)) continue;             // c_mid1
            int d = G.here.distanceSquaredTo(l) + (t == role ? 0 : 400);
            if (d < bd) { bd = d; best = l; if (C.TELEMETRY) bt = t; }
        }
        if (C.TELEMETRY) { Comms.lastWellCount = i - Comms.WELLS; Telemetry.crowdSwitches++; }
        for (int j = MapMem.seenWellCount(); --j >= 0; ) {
            MapLocation l = MapMem.seenWellAt(j);
            if (l.equals(well)) continue;
            if (C.ROLES == 3 && role == 2 && MapMem.seenWellTypeAt(j) != 2) continue;
            if (C.HOT && hot(l)) continue;                                                  // c_well6: hot
            if (C.MID && G.round < midAvoidUntil && Mid.isSite(l)) continue;                // c_mid1
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
        if (ringHold(t)) return;
        Nav.moveTo(t);
        if (G.rc.isMovementReady() && G.rc.getLocation().distanceSquaredTo(t) > 2) { if (ringHold(t)) return; Nav.moveTo(t); }
    }

    /** c_flee1: while the stand-off holds (Nav.danger), the straight step toward t would end inside a ring and not
     *  strictly outward: hold instead of wall-following around it (Nav.moveTo treats a refused step as a wall when one of
     *  its three greedy squares is one, and would request a field around the ring). */
    static boolean ringHold(MapLocation t) {
        if (!Nav.danger || Nav.ringN == 0) return false;
        MapLocation s = G.rc.getLocation();
        Direction d = s.directionTo(t);
        return d != Direction.CENTER && Nav.ringBlocks(s.x, s.y, s.x + d.dx, s.y + d.dy, Nav.ringX, Nav.ringY, Nav.ringN);
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
        // c_well10: no front probe (C.PROBE_FRONT false): with no mana well known, no probe at all (c_bc1's explore)
        if (k == null && !C.PROBE_FRONT) { if (G.DEBUG) probeStartLog(home, null, kc, null, "no-front"); return false; }
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
            // c_well4's midpoint, except that a distance tie no longer draws from the RNG (none on MassiveL or Forest);
            // c_well10: only with C.PROBE_FRONT (the midpoint found Forest's midline well and fed carriers to it)
            if (C.PROBE_FRONT) {
                front = probeFront(home, MapMem.enemyHQs());
                if (front != null) addProbePt(front.x, front.y);
            }
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
