package arch_ampmid;

import battlecode.common.*;

/**
 * Launcher: the army. Attack r2 16, vision r2 20, 20 damage per action (one per turn), one move per two turns
 * (move cooldown 20). HQs cannot be damaged (RULES), so they are never targeted.
 *
 * Turn: shoot if a target is in range; if movement is ready, fight (score the 9 tiles) when enemies are visible, else
 * march to the objective; shoot again if the action is still ready after moving.
 * Objective: a fresh enemy sighting (comms) > an enemy-held island (stand on it so its anchor decays) > the predicted
 * enemy HQ (symmetry; stop outside its r2 9 fire).
 * arch_ampmid: before C.HQ_APPROACH_FROM the last objective is the midfield rally point instead, with surplus groups
 * detaching to raid enemy wells in the enemy half (rallyPoint, midRaid); nothing then goes near an enemy HQ.
 */
public final class Launcher {
    public static int shots, steppedIn, kited;   // diagnostics
    static MapLocation objective;
    /** Telemetry (TELEMETRY.md 1.1): this turn's mode (0 N nothing, 1 F fight, 2 H hold and shoot, 3 M march, 4 S stand,
     *  5 G regroup, 6 W follow) and the kind of the last objective pickObjective chose (0 sighting, 1 enemy island,
     *  2 predicted enemy HQ, 3 centre). Never read by decisions. */
    static int mode, objKind = 3;
    // telemetry only: OBJ (effective objective kind 0-7 and its location; the last one emitted) and FIGHT words
    static int objEff = -1, lastObjKind = -1, shots0, fightShots, firstTarget, fightA, fightB, fightC;
    static MapLocation objLoc, lastObjLoc;
    static boolean fought;

    static void run() throws GameActionException {
        RobotController rc = G.rc;
        if (C.TELEMETRY) { shots0 = shots; firstTarget = 0; fought = false; objEff = -1; }
        MapMem.scan();
        if ((G.round + G.id) % 4 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        report();
        track();
        shoot();
        if (rc.isMovementReady()) {
            if (hasHittableEnemies()) { mode = 1; fight(); }
            else march();
        } else mode = hasHittableEnemies() ? 2 : 0;
        if (rc.isActionReady()) { G.here = rc.getLocation(); refreshEnemies(); shoot(); }
        G.note = String.valueOf((char) ('0' + objKind));
        G.extra = ",pn=" + pinnedSeen + ",ua=" + unsafeStepsAvoided + (C.ARMY ? ",rg=" + regroups + ",fo=" + follows : "");
        Telemetry.code = Telemetry.launcherCode(mode, objKind, G.nEnemyFighters > G.nAllyFighters + 1);
        if (C.TELEMETRY) {
            if (fought) Telemetry.dot(Telemetry.FIGHT, fightA | (shots - shots0 - fightShots & 3) << 14, fightB, fightC,
                Telemetry.fightD(rc.getHealth(), G.enemies.length, firstTarget));
            if (objEff >= 0) objHook();
        }
    }

    /** OBJ record on a change of the effective objective kind, or a move of a kind 0-3 objective by more than dist2 8. */
    static void objHook() {
        if (objEff == lastObjKind && (objEff >= 4 || objLoc == null || lastObjLoc == null || objLoc.distanceSquaredTo(lastObjLoc) <= 8)) return;
        Telemetry.emitObj(objEff, objEff == 0 ? Comms.lastAge : 15, G.nAllyFighters, G.nEnemyFighters, objEff == 1 ? objIsland : 0,
            Telemetry.loc12(objLoc), Telemetry.loc12(G.here), G.round);
        lastObjKind = objEff;
        lastObjLoc = objLoc;
    }

    static void report() throws GameActionException {
        if (!Comms.canWrite) return;
        for (int i = G.enemies.length; --i >= 0; ) {
            RobotInfo e = G.enemies[i];
            if (e.type != RobotType.HEADQUARTERS) { Comms.reportEnemy(e.location); return; }
        }
        if (objective != null && G.here.distanceSquaredTo(objective) <= 8) Comms.clearEnemyNear(objective);
    }

    static boolean hasHittableEnemies() {
        for (int i = G.enemies.length; --i >= 0; ) if (G.enemies[i].type != RobotType.HEADQUARTERS) return true;
        return false;
    }

    static void refreshEnemies() throws GameActionException {
        G.enemies = G.rc.senseNearbyRobots(-1, G.them);
    }

    /** arch_swarm focus fire: launchers (lowest HP, then lowest id, so a group picks the same target), then carriers
     *  holding anchors, then carriers, then amplifiers (members' focus 0.46-0.65, first hit 0.72-0.81). */
    static int priority(RobotInfo e) {
        switch (e.type) {
            case LAUNCHER: case DESTABILIZER: return 5;
            case CARRIER: return e.getTotalAnchors() > 0 ? 4 : 3;
            case AMPLIFIER: return 2;
            case BOOSTER: return 2;
            default: return 0;
        }
    }

    static void shoot() throws GameActionException {
        RobotController rc = G.rc;
        while (rc.isActionReady()) {
            RobotInfo best = null;
            int bp = -1, bh = Integer.MAX_VALUE, bid = Integer.MAX_VALUE;
            for (int i = G.enemies.length; --i >= 0; ) {
                RobotInfo e = G.enemies[i];
                if (e.type == RobotType.HEADQUARTERS || !rc.canAttack(e.location)) continue;
                int p = priority(e);
                if (p > bp || (p == bp && (e.health < bh || (e.health == bh && e.ID < bid)))) { bp = p; bh = e.health; bid = e.ID; best = e; }
            }
            if (best == null) return;
            rc.attack(best.location);
            shots++;
            if (C.TELEMETRY && firstTarget == 0) firstTarget = best.ID;
            refreshEnemies();
        }
    }

    // enemy fighters seen on our previous turn: an enemy that has moved since cannot move on its next turn (launcher
    // move cooldown 20 against a decrement of 10), so it threatens only its attack radius r2 16, not the one-step
    // reach r2 26 (C.THREAT_R2)
    static int[] prevIds = new int[32];
    static MapLocation[] prevLocs = new MapLocation[32];
    static int nPrev, prevRound = -10;
    public static int pinnedSeen, unsafeStepsAvoided;   // diagnostics

    static int[] pinnedIds = new int[32];
    static int nPinned;

    /** Every turn, before acting: which visible enemy fighters moved since our previous turn (pinned for their next
     *  turn), then remember where every visible enemy fighter stands now. */
    static void track() {
        RobotInfo[] es = G.enemies;
        boolean fresh = prevRound == G.round - 1;
        int n = 0, np = 0;
        int[] ids = new int[32];
        MapLocation[] locs = new MapLocation[32];
        for (int i = 0; i < es.length && n < 32; i++) {
            RobotInfo e = es[i];
            if (e.type != RobotType.LAUNCHER && e.type != RobotType.DESTABILIZER) continue;
            if (fresh) for (int k = nPrev; --k >= 0; ) {
                if (prevIds[k] != e.ID) continue;
                MapLocation was = prevLocs[k];
                // moved by its own step (a current push adds no cooldown, audit R8): pinned
                if (!was.equals(e.location) && !was.add(MapMem.current(was.x, was.y)).equals(e.location) && np < 32) {
                    pinnedIds[np++] = e.ID; pinnedSeen++;
                }
                break;
            }
            ids[n] = e.ID;
            locs[n++] = e.location;
        }
        nPinned = np;
        prevIds = ids; prevLocs = locs; nPrev = n; prevRound = G.round;
    }

    static boolean isPinned(int id) {
        for (int k = nPinned; --k >= 0; ) if (pinnedIds[k] == id) return true;
        return false;
    }

    /**
     * Score the 9 tiles (lexicographic). threat(tile) = enemy fighters that can hit the tile on their next turn (r2 16 if
     * the enemy is pinned, else r2 26) plus enemy HQs within r2 9.
     * Action ready: step in only to a tile that can hit something AND where at most one enemy can answer, unless we
     * have local superiority (our launchers in vision + 1 > their fighters); among those, fewest threats, then the
     * edge of range. With no acceptable hitting tile: fewest threats, staying put on ties.
     * Action spent: fewest threats, then staying put (moving costs the next turn's move).
     * diag-top4 (2026-10-07): we ended 14-28% of launcher-rounds inside enemy reach against the top bots' 0.3-3%, and
     * took 9-26 damage per contact round against their 3.5-7.7.
     */
    static void fight() throws GameActionException {
        RobotController rc = G.rc;
        boolean ready = rc.isActionReady();
        boolean superior = G.nAllyFighters + 1 > G.nEnemyFighters;
        boolean outnumbered = G.nEnemyFighters > G.nAllyFighters + 1;
        // arch_swarm: locally ahead by 2 or more (allies in vision plus self, minus enemy fighters): the base scoring,
        // step in to fire; otherwise the parity hold (members started 54-80% of engagements 2+ ahead and won 91-98% of those)
        boolean ahead = G.nAllyFighters + 1 - G.nEnemyFighters >= C.AHEAD_MIN;   // arch_ampmid: +1 (member engages at +1)
        MapLocation here = rc.getLocation();
        // per-enemy data computed once (audit R2): kind 0 = hittable non-fighter, 1 = fighter, 2 = HQ; killable = one shot
        RobotInfo[] es = G.enemies;
        int n = es.length;
        int[] ex = new int[n], ey = new int[n], kind = new int[n];
        boolean[] kill = new boolean[n];
        for (int i = n; --i >= 0; ) {
            RobotInfo e = es[i];
            ex[i] = e.location.x; ey[i] = e.location.y;
            if (e.type == RobotType.HEADQUARTERS) kind[i] = 2;
            else { if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) kind[i] = 1; kill[i] = e.health <= 20; }
        }
        // fallback when no safe firing tile exists: away from the enemy, toward the centroid of our launchers in vision
        // (else our nearest HQ)
        int ax = 0, ay = 0, na = 0;
        for (int i = G.nearby.length; --i >= 0 && na < 12; ) {
            RobotInfo r = G.nearby[i];
            if (r.team == G.us && r.type == RobotType.LAUNCHER) { ax += r.location.x; ay += r.location.y; na++; }
        }
        MapLocation rally;
        if (na > 0) rally = new MapLocation(ax / na, ay / na);
        else rally = HQState.nearest(here);
        Direction best = Direction.CENTER;
        long bestScore = Long.MIN_VALUE;
        boolean anyCanHit = false;
        int threat0 = 0;
        boolean hit0 = false;
        // telemetry (FIGHT): tiles scored, guard break, the chosen tile's and the CENTER tile's threat / can-hit / min dist2
        int nt = 0, bk = 0, bThreat = 0, bMin = Integer.MAX_VALUE, sThreat = 0, sMin = Integer.MAX_VALUE;
        boolean gb = false, bHit = false, sHit = false;
        for (int k = 0; k < 9; k++) {
            if (Clock.getBytecodesLeft() < 2000) { if (C.TELEMETRY) gb = true; break; }   // keep the turn: the best tile so far (CENTER first)
            Direction d = G.DIRS9[k];
            if (d != Direction.CENTER && !rc.canMove(d)) continue;
            if (C.TELEMETRY) nt++;
            int tx = here.x + d.dx, ty = here.y + d.dy;
            int threat = 0, minD = Integer.MAX_VALUE;
            boolean canHit = false, aura = false, killShot = false;
            for (int i = n; --i >= 0; ) {
                int dx = tx - ex[i], dy = ty - ey[i], dd = dx * dx + dy * dy;
                switch (kind[i]) {
                    case 2: if (dd <= 9) { threat++; aura = true; } break;
                    case 1: if (dd <= C.THREAT_R2) threat++; if (dd < minD) minD = dd; if (dd <= 16) { canHit = true; if (kill[i]) killShot = true; } break;
                    default: if (dd <= 16) { canHit = true; if (kill[i]) killShot = true; }
                }
            }
            if (d == Direction.CENTER) { threat0 = threat; hit0 = canHit; }
            long s;
            if (ahead) {
                // g_iter0's scoring: ready -> any hitting tile, fewest threats, then the edge of range; else kite
                if (ready) { s = (canHit ? 1_000_000L : 0) - threat * 10_000L + Math.min(minD, 100) * 10; if (canHit) anyCanHit = true; }
                else s = -threat * 10_000L + Math.min(minD, 100) * 10;
            } else if (ready) {
                // parity hold: fire only from a tile at most one enemy can reach, never stepping into more reach than
                // where we stand; with no such tile, fall back toward our launchers (or home)
                boolean fire = canHit && threat <= 1 && (d == Direction.CENTER || threat <= threat0);
                if (fire) { s = 1_000_000L - threat * 10_000L + Math.min(minD, 100) * 10; anyCanHit = true; }
                else s = -threat * 10_000L + Math.min(minD, 50) * 10 - (rally == null ? 0 : Math.min(rally.distanceSquaredTo(new MapLocation(tx, ty)), 400)) * 3L;
            } else s = -threat * 10_000L + Math.min(minD, 100) * 10;
            // never end a turn inside an enemy HQ aura (r2 9) unless the shot from there kills
            if (aura && !(ready && killShot)) s -= 50_000_000L;
            if (d == Direction.CENTER) s += 1;
            s += G.rand(3);
            if (s > bestScore) {
                bestScore = s;
                best = d;
                if (C.TELEMETRY) {
                    bk = k; bThreat = threat; bHit = canHit; bMin = minD;
                    if (k == 0) { sThreat = threat; sHit = canHit; sMin = minD; }   // CENTER is scored first and always taken first
                }
            }
        }
        if (best != Direction.CENTER) {
            rc.move(best);
            G.here = rc.getLocation();
            if (ready && anyCanHit) steppedIn++; else kited++;
        }
        if (C.TELEMETRY) {
            if (gb) Telemetry.guardBreaks++;
            fightShots = shots - shots0;
            fightA = Telemetry.fightA(ready, superior, outnumbered, anyCanHit, best != Direction.CENTER, bk, gb, ahead,
                fightShots, 0, G.nEnemyFighters, G.nAllyFighters);
            fightB = Telemetry.fightTile(bThreat, bHit, bMin, nPinned);
            fightC = Telemetry.fightTile(sThreat, sHit, sMin, nt);
            fought = true;
        }
    }

    static void march() throws GameActionException {
        groupN = 1;
        rankN = 0;
        for (int i = G.nearby.length; --i >= 0; ) {
            RobotInfo r = G.nearby[i];
            if (r.team == G.us && r.type == RobotType.LAUNCHER) { groupN++; if (r.ID < G.id) rankN++; }
        }
        objective = pickObjective();
        mode = 4;                                   // S, unless a move below is taken
        if (C.TELEMETRY) { objEff = objKind; objLoc = objective; }
        if (objective == null) return;
        // an enemy island in sight: each launcher takes the nearest free square of it (audit R4: anchor health falls
        // by 100 x (our robots on its squares) / area per round, and every launcher went to the one stored tile)
        if (objIsland > 0 && G.here.distanceSquaredTo(objective) <= 20) {
            if (G.rc.senseIsland(G.here) == objIsland) return;
            MapLocation[] tiles = G.rc.senseNearbyIslandLocations(objIsland);
            MapLocation best = null;
            int bd = Integer.MAX_VALUE;
            for (int i = tiles.length; --i >= 0; ) {
                MapLocation t = tiles[i];
                if (G.rc.canSenseLocation(t) && G.rc.isLocationOccupied(t)) continue;
                int d = G.here.distanceSquaredTo(t);
                if (d < bd) { bd = d; best = t; }
            }
            if (best != null) objective = best;
        }
        if (C.ARMY && regroup()) return;
        // arch_swarm: a raided well reached with no enemy in sight (march runs only then) is cleared for a while; a
        // predicted well that is not there is cleared for good
        if (objRaid != null && G.here.distanceSquaredTo(objRaid) <= 20 && G.rc.canSenseLocation(objRaid)) {
            boolean real = G.rc.senseWell(objRaid) != null;
            clearRaid(objRaid, real ? G.round : G.round + 5000);
        }
        // arch_ampmid: hold at the midfield rally point
        if (objRally != null && G.here.distanceSquaredTo(objRally) <= C.RALLY_HOLD_R2) return;
        // the siege ring around the enemy HQ: hold at r2 RING_MIN..RING_MAX, outside the aura
        if (objRing != null && seenHQ(objRing)) {        // a predicted HQ is approached until seen (or eliminated)
            int d = G.here.distanceSquaredTo(objRing);
            if (d >= C.RING_MIN && d <= C.RING_MAX) return;                  // S: hold, catch spawns
            if (d < C.RING_MIN) { mode = 3; Nav.avoid = true; Nav.moveAway(objRing); Nav.avoid = false; return; }
        }
        mode = 3;
        Nav.avoid = true;
        Nav.moveTo(objective);
        Nav.avoid = false;
    }

    // ---------------------------------------------------------------- arch_ampmid: midfield and raids
    /** Launchers in vision plus self, and how many of them have a lower id (march). */
    static int groupN, rankN;
    static MapLocation objRally;
    /** This launcher's midfield raid target; kept until the well is cleared or the group falls apart. */
    static MapLocation raidTgt;
    public static int raidsStarted;   // diagnostics

    static boolean early() { return G.round < C.HQ_APPROACH_FROM; }

    static boolean nearEnemyHQ(MapLocation l, MapLocation[] ehq) {
        for (int k = ehq.length; --k >= 0; ) if (ehq[k].distanceSquaredTo(l) <= C.NO_APPROACH_R2) return true;
        return false;
    }

    static MapLocation rallyFor, rallyPt;
    static boolean rallySnapped;

    /** The midfield rally point: the midpoint between the team target (siegeTarget: the predicted enemy HQ nearest the
     *  centroid of our HQs) and our HQ nearest it. Snapped once, when within r2 64 of it, to the nearest tile known
     *  passable within Chebyshev 4 (MapMem; perimeter rings, a bytecode check per tile: v1's full-square search with
     *  one check per ring overran launchers 185 times in 10 games). The member's band sits there: Cat r40-r120 x 22-28
     *  of 50 between the HQ pairs at x 11-14 and 35-38. Driver game 2 used the midpoint of the two teams' HQ centroids
     *  instead: on DefaultMap it lay in a cloud 12 tiles from where g_iter0's launchers attacked (between the facing
     *  HQs), and the army lost every fight there (ahead share 0.05). Also used by Amplifier. */
    static MapLocation rallyPoint(MapLocation[] ehq) {
        MapLocation hq = siegeTarget(ehq);
        if (!hq.equals(rallyFor) || rallyPt == null) {
            MapLocation ours = HQState.nearest(hq);
            if (ours == null) return hq;
            rallyFor = hq;
            rallyPt = new MapLocation((ours.x + hq.x) / 2, (ours.y + hq.y) / 2);
            rallySnapped = false;
        }
        if (rallySnapped || MapMem.tile == null || G.here.distanceSquaredTo(rallyPt) > 64) return rallyPt;
        int mx = rallyPt.x, my = rallyPt.y;
        if (MapMem.known(mx, my) && !MapMem.isWall(mx, my)) { rallySnapped = true; return rallyPt; }
        int bd = Integer.MAX_VALUE, bx = mx, by = my;
        for (int r = 1; r <= 4 && bd == Integer.MAX_VALUE; r++) {
            for (int i = 8 * r; --i >= 0; ) {
                if (Clock.getBytecodesLeft() < 3000) return rallyPt;     // not snapped yet: retried next turn
                int side = i / (2 * r), off = i % (2 * r), x, y;
                switch (side) {
                    case 0: x = mx - r + off; y = my - r; break;
                    case 1: x = mx + r; y = my - r + off; break;
                    case 2: x = mx + r - off; y = my + r; break;
                    default: x = mx - r; y = my + r - off;
                }
                if (!G.onMap(x, y) || !MapMem.known(x, y) || MapMem.isWall(x, y)) continue;
                int d = G.dist2(x, y, mx, my);
                if (d < bd) { bd = d; bx = x; by = y; }
            }
        }
        rallySnapped = true;                                   // a passable tile, or none known within 4: keep the midpoint
        if (bd != Integer.MAX_VALUE) rallyPt = new MapLocation(bx, by);
        return rallyPt;
    }

    /** The midfield raid. A launcher whose id ranks C.RAID_HOLD or more among the launchers in vision (at the rally point
     *  when C.RAID_HOLD > 0) raids when at least C.RAID_GROUP are surplus to the holders: the uncleared predicted enemy
     *  well in the enemy half (outside r2 C.NO_APPROACH_R2 of every enemy HQ) nearest the rally point. It keeps that
     *  target until the well is cleared (reached with no enemy in sight) or it has no ally in vision. */
    static MapLocation midRaid(MapLocation rally, MapLocation hq, MapLocation[] ehq) throws GameActionException {
        if (raidTgt != null) {
            if (cleared(raidTgt) || groupN < 2) raidTgt = null;
            else return raidTgt;
        }
        if (!MapMem.decided() || (C.RAID_HOLD > 0 && G.here.distanceSquaredTo(rally) > 2 * C.RALLY_HOLD_R2)) return null;
        if (rankN < C.RAID_HOLD || groupN - C.RAID_HOLD < C.RAID_GROUP) return null;
        if (G.round - halfRound >= 20) computeHalfWells(ehq);
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = halfWells.length; --i >= 0; ) {
            MapLocation w = halfWells[i];
            int d = w.distanceSquaredTo(rally);
            if (d >= bd || cleared(w)) continue;
            bd = d; best = w;
        }
        if (best != null) { raidTgt = best; raidsStarted++; }
        return best;
    }

    static MapLocation[] halfWells = new MapLocation[0];
    static int halfRound = -100;

    /** Predicted enemy wells in the enemy half (nearer an enemy HQ than any of ours) and outside r2 C.NO_APPROACH_R2 of
     *  every enemy HQ: known wells (shared slots, own sightings) and their images under the decided symmetry. */
    static void computeHalfWells(MapLocation[] ehq) throws GameActionException {
        halfRound = G.round;
        int s = MapMem.cand == 1 || MapMem.cand == 2 || MapMem.cand == 4 ? MapMem.cand : (MapMem.cand & 1) != 0 ? 1 : (MapMem.cand & 2) != 0 ? 2 : 4;
        MapLocation[] out = new MapLocation[40];
        int n = 0;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS && n < 38; i++) {
            if (Clock.getBytecodesLeft() < 4500) { halfRound = G.round - 15; break; }
            int c = Comms.read(i);
            if (c == 0) break;
            MapLocation l = G.dec(c & 0xfff);
            n = addHalf(out, n, l, ehq);
            n = addHalf(out, n, MapMem.img(s, l), ehq);
        }
        for (int j = MapMem.seenWellCount(); --j >= 0 && n < 38; ) {
            if (Clock.getBytecodesLeft() < 4500) { halfRound = G.round - 15; break; }
            MapLocation l = MapMem.seenWellAt(j);
            n = addHalf(out, n, l, ehq);
            n = addHalf(out, n, MapMem.img(s, l), ehq);
        }
        halfWells = new MapLocation[n];
        System.arraycopy(out, 0, halfWells, 0, n);
    }

    static int addHalf(MapLocation[] out, int n, MapLocation l, MapLocation[] ehq) {
        int de = Integer.MAX_VALUE;
        for (int k = ehq.length; --k >= 0; ) de = Math.min(de, ehq[k].distanceSquaredTo(l));
        if (de <= C.NO_APPROACH_R2) return n;
        MapLocation[] o = HQState.ourHQs;
        if (o != null) for (int k = o.length; --k >= 0; ) if (o[k].distanceSquaredTo(l) <= de) return n;
        for (int k = n; --k >= 0; ) if (out[k].equals(l)) return n;
        out[n] = l;
        return n + 1;
    }

    // ---------------------------------------------------------------- arch_swarm objectives
    /** The rank-th nearest enemy HQ to our centroid (ties by location), rank rotating every C.SIEGE_ROTATE rounds. */
    static MapLocation siegeTarget(MapLocation[] ehq) {
        MapLocation from = ourCentroid();
        int n = ehq.length;
        int rank = G.round < C.SIEGE_ROTATE_FROM ? 0 : (1 + (G.round - C.SIEGE_ROTATE_FROM) / C.SIEGE_ROTATE) % n;
        boolean[] used = new boolean[n];
        MapLocation hq = null;
        for (int r = 0; r <= rank; r++) {
            int bd = Integer.MAX_VALUE, bi = -1;
            for (int i = n; --i >= 0; ) {
                if (used[i]) continue;
                int d = from.distanceSquaredTo(ehq[i]);
                if (d < bd || (d == bd && G.enc(ehq[i]) < G.enc(ehq[bi]))) { bd = d; bi = i; }
            }
            used[bi] = true;
            hq = ehq[bi];
        }
        return hq;
    }

    static MapLocation ourCentroid() {
        MapLocation[] o = HQState.ourHQs;
        if (o == null || o.length == 0) return G.here;
        int x = 0, y = 0;
        for (int i = o.length; --i >= 0; ) { x += o[i].x; y += o[i].y; }
        return new MapLocation(x / o.length, y / o.length);
    }

    static boolean seenHQ(MapLocation l) {
        for (int k = MapMem.nEnemyHQSeen; --k >= 0; ) if (MapMem.enemyHQSeen[k].equals(l)) return true;
        return false;
    }

    static MapLocation objRaid, objRing;
    static MapLocation[] predWells = new MapLocation[0];
    static int predRound = -100;
    static MapLocation[] clearedLoc = new MapLocation[16];
    static int[] clearedUntil = new int[16];
    static int nCleared;

    static void clearRaid(MapLocation w, int round) {
        for (int i = nCleared; --i >= 0; ) if (clearedLoc[i].equals(w)) { clearedUntil[i] = round + C.RAID_CLEAR_ROUNDS; return; }
        int k = nCleared < clearedLoc.length ? nCleared++ : G.rand(clearedLoc.length);
        clearedLoc[k] = w;
        clearedUntil[k] = round + C.RAID_CLEAR_ROUNDS;
    }

    static boolean cleared(MapLocation w) {
        for (int i = nCleared; --i >= 0; ) if (clearedLoc[i].equals(w)) return G.round < clearedUntil[i];
        return false;
    }

    /** Enemy wells: wells we know (shared slots and our own sightings) and their images under the most likely
     *  symmetry, kept when within r2 C.RAID_R2 of a predicted enemy HQ. Recomputed every 20 rounds. */
    static void computePredWells(MapLocation[] ehq) throws GameActionException {
        predRound = G.round;
        // bytecode guards in both loops (v4 full run, Cornucopia: 12 wells, 48 candidates x dedup overran launchers by
        // up to 14 bytecodes, 11 times in one game); an interrupted pass keeps what it has and retries in 5 rounds
        int s = MapMem.cand == 1 || MapMem.cand == 2 || MapMem.cand == 4 ? MapMem.cand : (MapMem.cand & 1) != 0 ? 1 : (MapMem.cand & 2) != 0 ? 2 : 4;
        MapLocation[] out = new MapLocation[40];
        int n = 0;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS && n < 38; i++) {
            if (Clock.getBytecodesLeft() < 4500) { predRound = G.round - 15; break; }
            int c = Comms.read(i);
            if (c == 0) break;
            MapLocation l = G.dec(c & 0xfff);
            n = addPred(out, n, l, ehq);
            n = addPred(out, n, MapMem.img(s, l), ehq);
        }
        for (int j = MapMem.seenWellCount(); --j >= 0 && n < 38; ) {
            if (Clock.getBytecodesLeft() < 4500) { predRound = G.round - 15; break; }
            MapLocation l = MapMem.seenWellAt(j);
            n = addPred(out, n, l, ehq);
            n = addPred(out, n, MapMem.img(s, l), ehq);
        }
        predWells = new MapLocation[n];
        System.arraycopy(out, 0, predWells, 0, n);
    }

    static int addPred(MapLocation[] out, int n, MapLocation l, MapLocation[] ehq) {
        boolean near = false;
        for (int k = ehq.length; --k >= 0; ) if (ehq[k].distanceSquaredTo(l) <= C.RAID_R2) { near = true; break; }
        if (!near) return n;
        for (int k = n; --k >= 0; ) if (out[k].equals(l)) return n;
        out[n] = l;
        return n + 1;
    }

    /** The raid target: the uncleared predicted enemy well nearest the target enemy HQ. */
    static MapLocation raidWell(MapLocation hq, MapLocation[] ehq) throws GameActionException {
        if (G.round - predRound >= 20) computePredWells(ehq);
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = predWells.length; --i >= 0; ) {
            MapLocation w = predWells[i];
            int d = w.distanceSquaredTo(hq);
            if (d > C.RAID_R2 || d >= bd || cleared(w)) continue;
            bd = d; best = w;
        }
        return best;
    }

    public static int regroups, follows;   // diagnostics (C.ARMY)

    /**
     * Cohesion (C.ARMY), called only with no enemy in sight. Returns true if it took the move (or chose to hold).
     * Fewer than C.GROUP_MIN launchers here (self included): go to the nearest visible ally launcher, else back toward
     * the nearest own HQ, where new launchers appear, and hold there; except toward an enemy sighting near one of our
     * HQs (home defence). Enough launchers: follow the lowest-id launcher in vision when farther than C.FOLLOW_R2; the
     * leader itself marches to the objective.
     */
    static boolean regroup() throws GameActionException {
        RobotInfo leader = null, closest = null;
        int n = 1, cd = Integer.MAX_VALUE;
        for (int i = G.nearby.length; --i >= 0; ) {
            RobotInfo r = G.nearby[i];
            if (r.team != G.us || r.type != RobotType.LAUNCHER) continue;
            n++;
            if (leader == null || r.ID < leader.ID) leader = r;
            int d = G.here.distanceSquaredTo(r.location);
            if (d < cd) { cd = d; closest = r; }
        }
        // arch_swarm: GROUP_MIN launchers form up near home before leaving; in the field a pair is a group, and only a
        // launcher with no ally in sight turns back (v3: requiring 4 in the field made launchers regroup 44-53% of
        // their opening turns and fight alone, alone 0.44 on Cat). In a cloud vision is r2 4 (robots in clouds are
        // hidden beyond r2 4), so there a pair counts even at home (Forest: launchers huddled in their HQs' clouds).
        MapLocation home = HQState.nearest(G.here);
        // arch_ampmid: before C.HQ_APPROACH_FROM a launcher at the rally point never counts as forming (driver game 1,
        // DefaultMap: the rally lay within r2 50 of an HQ, so the group holding it read "forming" and walked back home)
        boolean atRally = early() && rallyPt != null && G.here.distanceSquaredTo(rallyPt) <= 2 * C.RALLY_HOLD_R2;
        boolean forming = home != null && G.here.distanceSquaredTo(home) <= C.FORM_R2 && !G.rc.senseCloud(G.here) && !atRally;
        if (n < (forming ? C.GROUP_MIN : 2)) {
            if (home != null && objective.distanceSquaredTo(home) <= C.HOME_DEFENCE_R2) { if (C.TELEMETRY) objEff = 7; return false; }
            regroups++;
            mode = 5;
            if (closest != null) {
                if (C.TELEMETRY) { objEff = 4; objLoc = closest.location; }
                if (cd > 2) Nav.moveTo(closest.location);
                return true;
            }
            if (C.TELEMETRY) { objEff = 5; objLoc = home; }
            if (home != null && G.here.distanceSquaredTo(home) > 13) Nav.moveTo(home);
            return true;
        }
        // arch_ampmid: a raider does not follow (its leader in vision is a holder at the rally point)
        if (raidTgt == null && leader.ID < G.id && G.here.distanceSquaredTo(leader.location) > C.FOLLOW_R2) {
            follows++;
            mode = 6;
            if (C.TELEMETRY) { objEff = 6; objLoc = leader.location; }
            Nav.moveTo(leader.location);
            return true;
        }
        return false;
    }

    static int objIsland;

    static MapLocation pickObjective() throws GameActionException {
        objIsland = 0;
        objRaid = null;
        objRing = null;
        objRally = null;
        // arch_ampmid: before C.HQ_APPROACH_FROM nothing within r2 C.NO_APPROACH_R2 of a predicted enemy HQ is an objective
        boolean early = early();
        MapLocation[] ehq = MapMem.enemyHQs();
        Nav.avoidR2 = early ? C.NO_APPROACH_R2 : 9;
        if (!early) raidTgt = null;
        // arch_swarm objectives: a nearby fight (shared sighting within r2 C.SIGHTING_R2); enemy-held islands from
        // C.ISLAND_HUNT_START; the carrier raid (predicted enemy wells nearest the enemy HQ); the siege ring
        MapLocation e = Comms.nearestEnemy(G.here, 2);
        if (e != null && G.here.distanceSquaredTo(e) <= C.SIGHTING_R2 && !(early && nearEnemyHQ(e, ehq))) { objKind = 0; return e; }
        if (G.round >= C.ISLAND_HUNT_START) {
            int n = Math.min(35, G.rc.getIslandCount());
            MapLocation best = null;
            int bd = Integer.MAX_VALUE;
            for (int id = 1; id <= n; id++) {
                // our own sighting when fresh, or when the shared slot is empty (launchers far from home cannot write)
                int shared = Comms.read(Comms.ISLANDS + id);
                int owner = MapMem.islandSeen[id] > 0 && (G.round - MapMem.islandSeen[id] <= 10 || shared == 0) ? MapMem.islandOwner[id] : shared >>> 12;
                if (owner != 2) continue;
                MapLocation t = Comms.islandTile(id);
                if (t == null) t = MapMem.islandTile[id];
                if (t == null || (early && nearEnemyHQ(t, ehq))) continue;
                int d = G.here.distanceSquaredTo(t);
                if (d < bd) { bd = d; best = t; objIsland = id; }
            }
            if (best != null) { objKind = 1; return best; }
        }
        if (ehq.length > 0) {
            // the nearest predicted enemy HQ, ties broken by location (not by each robot's RNG, so a group agrees);
            // until the symmetry is decided the group checks predicted HQs (an empty one eliminates its symmetry) and
            // does not raid wells predicted under a guessed symmetry (v2 quick, Cat: the raid sent the swarm south to
            // rotation images for 60 rounds while g_iter0 raided our only mana well)
            // one team target: the enemy HQ nearest the centroid of our HQs, so the launchers of every HQ converge on
            // one front (v3, Cat: each HQ's first four took their own nearest enemy HQ and both pairs of four lost at
            // parity, 18 kills to 6, where the members brought 8 to the one fight and won it 13-17 kills to 3-6)
            // from C.SIEGE_ROTATE_FROM the target steps through the enemy HQs in order of distance from our centroid
            MapLocation hq = siegeTarget(ehq);
            objKind = 2;
            if (early) {
                MapLocation r = rallyPoint(ehq);
                MapLocation w = midRaid(r, hq, ehq);
                if (w != null) { objRaid = w; return w; }
                objRally = r;
                return r;
            }
            if (MapMem.decided()) {
                MapLocation w = raidWell(hq, ehq);
                if (w != null) { objRaid = w; return w; }
            }
            objRing = hq;
            return hq;
        }
        objKind = 3;
        return new MapLocation(G.W / 2, G.H / 2);
    }
}
