package c_ex0;

import battlecode.common.*;

/**
 * Launcher: the army. Attack r2 16, vision r2 20, 20 damage per action (one per turn), one move per two turns
 * (move cooldown 20). HQs cannot be damaged (RULES), so they are never targeted.
 *
 * Turn: shoot if a target is in range; if movement is ready, fight (score the 9 tiles) when enemies are visible, else
 * march to the objective; shoot again if the action is still ready after moving.
 * Objective: a fresh enemy sighting (comms) > an enemy-held island (stand on it so its anchor decays) > the predicted
 * enemy HQ (symmetry; stop outside its r2 9 fire).
 * c_mend1 (C.MEND): a launcher at C.MEND_HP or less walks to the nearest island we own within r2 C.MEND_R2 and holds
 * within r2 4 of it until C.MEND_FULL HP (mendUpdate); in a fight it fires only from zero-threat tiles and otherwise
 * edges toward that island (mendScore).
 * c_mid1 (C.MID): a squad member (G.squad, id % C.MID_MOD == 0) takes the contested mana well (Mid.site) as its
 * objective after a sighting or a recall and before enemy islands, for one tour of C.MID_TOUR rounds from its arrival
 * (endTour); it forms at home on squad members only, follows only a squad member nearer the site, and holds within
 * r2 C.MID_HOLD_R2 of the site on a tile with no current outside the carriers' free zone (midRegroup, midHold). No
 * launcher follows a leader standing at the site (regroup).
 * c_guard1 (C.GUARD): after the recall, a fresh sighting in our home zone within r2 C.GUARD_R2 and nearer than the
 * site or the siege target is the objective (homeSighting; carriers report the raider they fled at their next write
 * turn); a launcher that reaches it and sees nobody skips it until it is stamped again.
 * c_isle1 (C.ISLE_THREAT): when the enemy is C.ISLE_MARGIN_SMALL (C.ISLE_MARGIN_LARGE on large maps) islands short of
 * conquest, an even-id launcher in march takes the nearest enemy-held island before any sighting (islandScan).
 */
public final class Launcher {
    public static int shots, steppedIn, kited;   // diagnostics
    static MapLocation objective;
    /** Telemetry (TELEMETRY.md 1.1): this turn's mode (0 N nothing, 1 F fight, 2 H hold and shoot, 3 M march, 4 S stand,
     *  5 G regroup, 6 W follow) and the kind of the last objective pickObjective chose (0 sighting, 1 enemy island,
     *  2 predicted enemy HQ, 3 centre, or c_mend1's mending island: march sets kind 3 for a mender). Never read by
     *  decisions. */
    static int mode, objKind = 3;
    // telemetry only: OBJ (effective objective kind 0-7 and its location; the last one emitted) and FIGHT words
    static int objEff = -1, lastObjKind = -1, shots0, fightShots, firstTarget, fightA, fightB, fightC;
    static MapLocation objLoc, lastObjLoc;
    static boolean fought;
    /** c_mend1 (C.MEND): this launcher is walking to (or holding on) an island we own to heal; mendTile is a tile of
     *  island mendIsland; mendCheck is the first round of the next target re-check. */
    static boolean mending;
    static MapLocation mendTile;
    static int mendIsland, mendCheck;

    static void run() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation at = G.here;                    // where G.startTurn sensed G.enemies
        if (C.TELEMETRY) { shots0 = shots; firstTarget = 0; fought = false; objEff = -1; }
        MapMem.scan();
        if ((G.round + G.id) % 4 == 0) MapMem.scanIslands();
        MapMem.syncSym();
        report();
        track();
        shoot();
        if (C.MEND) mendUpdate();
        if (rc.isMovementReady()) {
            if (hasHittableEnemies()) { mode = 1; fight(); }
            else march();
        } else mode = hasHittableEnemies() ? 2 : 0;
        // bytecodes: a robot that has not moved sees the same enemies (none acts during our turn, and shoot() re-senses
        // after each attack), so the re-sense (100) runs only after a move or an overrun; every standing turn paid it
        if (rc.isActionReady()) { G.here = rc.getLocation(); if (enemiesStale(at)) refreshEnemies(); shoot(); }
        G.note = String.valueOf((char) ('0' + objKind));
        G.extra = ",pn=" + pinnedSeen + ",ua=" + unsafeStepsAvoided + (C.ARMY ? ",rg=" + regroups + ",fo=" + follows : "");
        Telemetry.code = Telemetry.launcherCode(mode, objKind, G.nEnemyFighters > G.nAllyFighters + 1);
        if (C.TELEMETRY) {
            if (fought) Telemetry.dot(Telemetry.FIGHT, fightA | (shots - shots0 - fightShots & 3) << 14, fightB, fightC,
                Telemetry.fightD(rc.getHealth(), G.enemies.length, firstTarget));
            if (objEff >= 0) objHook();
        }
    }

    /**
     * c_mend1: at C.MEND_HP or less (or while mending), every C.MEND_RECHECK rounds pick the nearest island we own
     * within r2 C.MEND_R2 (owner by pickObjective's rule: our own sighting when fresh or when the shared slot is empty,
     * else the shared slot) whose tile has no enemy sighting at most 1 stamp old within r2 C.MEND_SIGHT_R2; none: stop
     * mending. Mending ends at C.MEND_FULL HP. No RNG; the island loop never runs above C.MEND_HP unless mending, never
     * before C.ANCHOR_START, and only on a turn with C.MEND_MIN_LEFT bytecodes left (mendDue).
     */
    static void mendUpdate() throws GameActionException {
        int hp = G.rc.getHealth();
        if (mending && hp >= C.MEND_FULL) { mending = false; mendTile = null; mendIsland = 0; }
        if (mendDue(hp, mending, G.round, mendCheck, Clock.getBytecodesLeft())) {
            mendCheck = G.round + C.MEND_RECHECK;
            int n = Math.min(35, G.rc.getIslandCount()), bd = C.MEND_R2 + 1, bi = 0;
            MapLocation bt = null;
            for (int id = 1; id <= n; id++) {
                if (Clock.getBytecodesLeft() < C.ISLAND_LOOP_GUARD) break;
                int shared = Comms.read(Comms.ISLANDS + id);
                int owner = MapMem.islandSeen[id] > 0 && (G.round - MapMem.islandSeen[id] <= 10 || shared == 0) ? MapMem.islandOwner[id] : shared >>> 12;   // pickObjective's rule
                if (owner != 1) continue;
                MapLocation t = shared != 0 ? G.dec(shared & 0xfff) : MapMem.islandTile[id];
                if (t == null) continue;
                int d = G.here.distanceSquaredTo(t);
                if (d < bd) { bd = d; bi = id; bt = t; }
            }
            if (bt != null) { MapLocation s = Comms.nearestEnemy(bt, 1); if (s != null && s.distanceSquaredTo(bt) <= C.MEND_SIGHT_R2) bt = null; }
            if (bt != null) { mending = true; mendTile = bt; mendIsland = bi; } else { mending = false; mendTile = null; mendIsland = 0; }
        }
    }

    /** c_mend1: whether this turn re-checks the mending target: at C.MEND_HP or less or while mending, once round
     *  reaches check; never before C.ANCHOR_START (HQ.build builds anchors only from then, so no island can be ours and
     *  the opening keeps c_aura2's bytecodes, hence its field and symmetry timing); only with C.MEND_MIN_LEFT bytecodes
     *  left (a short turn leaves check unchanged, so the re-check waits for the next turn and the target is kept). */
    static boolean mendDue(int hp, boolean mending, int round, int check, int left) {
        return (hp <= C.MEND_HP || mending) && round >= check && round >= C.ANCHOR_START && left >= C.MEND_MIN_LEFT;
    }

    /** c_mend1: fight() tile score while mending. A zero-threat tile that can hit, with the action ready, first; then
     *  fewest threats; then nearest the mending tile (dist2 capped at 400). */
    static long mendScore(boolean ready, boolean canHit, int threat, int d2) {
        return (ready && canHit && threat == 0 ? 1_000_000L : 0) - threat * 10_000L - 3L * Math.min(d2, 400);
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
        // c_guard1: at a home sighting with no enemy in sight, this launcher drops it (it usually cannot write there)
        if (C.GUARD && guardObj && objective != null && G.here.distanceSquaredTo(objective) <= 8 && !hasHittableEnemies()) {
            guardClear = objective;
            guardClearStamp = guardStamp;
        }
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

    /** Whether G.enemies, sensed by G.startTurn at `at`, can differ from a fresh sense now (G.here already re-read): after
     *  a move, or after an overrun, when the engine resumes the robot at the same instruction a round later and other
     *  robots have acted (c_aura2 re-sensed then too; cooldowns have also dropped, so the action can be ready again). */
    static boolean enemiesStale(MapLocation at) { return !G.here.equals(at) || G.rc.getRoundNum() != G.round; }

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
                if (best != null && Clock.getBytecodesLeft() < C.SHOOT_GUARD) break;   // c_nav6: crowds, keep the turn
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
        // c_nav6: at most C.TRACK_MAX fighters (the match below is quadratic: 32 x 32 cost 4,000-7,000 bytecodes in
        // late-game crowds and starved fight(), 3 overruns on g_iter3/4's replica panel), and none when the turn is
        // already short; its result now feeds only telemetry (fight threat uses C.THREAT_R2)
        if (Clock.getBytecodesLeft() < C.TRACK_MIN_LEFT) { nPinned = 0; nPrev = 0; prevRound = G.round; return; }
        RobotInfo[] es = G.enemies;
        // bytecodes: no enemy in vision leaves the same state (nothing pinned, nothing remembered) without the two
        // TRACK_MAX arrays (an array costs its length) and the loop: about 35 on every calm turn
        if (es.length == 0) { nPinned = 0; nPrev = 0; prevRound = G.round; return; }
        boolean fresh = prevRound == G.round - 1;
        int n = 0, np = 0;
        int[] ids = new int[C.TRACK_MAX];
        MapLocation[] locs = new MapLocation[C.TRACK_MAX];
        for (int i = 0; i < es.length && n < C.TRACK_MAX; i++) {
            RobotInfo e = es[i];
            if (e.type != RobotType.LAUNCHER && e.type != RobotType.DESTABILIZER) continue;
            if (fresh) for (int k = nPrev; --k >= 0; ) {
                if (prevIds[k] != e.ID) continue;
                MapLocation was = prevLocs[k];
                // moved by its own step (a current push adds no cooldown, audit R8): pinned
                if (!was.equals(e.location) && !was.add(MapMem.current(was.x, was.y)).equals(e.location) && np < C.TRACK_MAX) {
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
        boolean ahead = G.nAllyFighters + 1 - G.nEnemyFighters >= 2;
        MapLocation here = rc.getLocation();
        // per-enemy data computed once (audit R2): kind 0 = hittable non-fighter, 1 = fighter, 2 = HQ; killable = one shot
        // c_nav6: every fighter and HQ, but at most C.FIGHT_MAX_OTHERS non-fighters (48 enemy carriers in vision made
        // the 9-tile scoring cost ~6,500 bytecodes and overran: Cornucopia vs georgezhang, r1801); a tile needs only one
        // hittable target, and the shot itself (shoot) still considers every enemy
        RobotInfo[] es = G.enemies;
        int m = es.length, n = 0, others = 0;
        int[] ex = new int[m], ey = new int[m], kind = new int[m];
        boolean[] kill = new boolean[m];
        for (int i = 0; i < m; i++) {
            RobotInfo e = es[i];
            int k;
            if (e.type == RobotType.HEADQUARTERS) k = 2;
            else if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) k = 1;
            else { if (others >= C.FIGHT_MAX_OTHERS) continue; others++; k = 0; }
            ex[n] = e.location.x; ey[n] = e.location.y; kind[n] = k;
            if (k != 2) kill[n] = e.health <= 20;
            n++;
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
            if (Clock.getBytecodesLeft() < C.FIGHT_GUARD) { if (C.TELEMETRY) gb = true; break; }   // keep the turn: the best tile so far (CENTER first)
            Direction d = G.DIRS9[k];
            if (d != Direction.CENTER && !rc.canMove(d)) continue;
            if (C.TELEMETRY) nt++;
            int tx = here.x + d.dx, ty = here.y + d.dy;
            int threat = 0, minD = Integer.MAX_VALUE, auraD = 99;   // auraD (c_aura1): nearest enemy HQ in whose aura the tile is
            boolean canHit = false, aura = false, killShot = false;
            for (int i = n; --i >= 0; ) {
                int dx = tx - ex[i], dy = ty - ey[i], dd = dx * dx + dy * dy;
                switch (kind[i]) {
                    case 2: if (dd <= 9) { threat++; aura = true; if (dd < auraD) auraD = dd; } break;
                    case 1: if (dd <= C.THREAT_R2) threat++; if (dd < minD) minD = dd; if (dd <= 16) { canHit = true; if (kill[i]) killShot = true; } break;
                    default: if (dd <= 16) { canHit = true; if (kill[i]) killShot = true; }
                }
            }
            if (d == Direction.CENTER) { threat0 = threat; hit0 = canHit; }
            long s;
            if (C.MEND && mending) {
                // c_mend1: fire only from a zero-threat tile, else fewest threats, then toward the mending tile
                int mx = tx - mendTile.x, my = ty - mendTile.y;
                s = mendScore(ready, canHit, threat, mx * mx + my * my);
                if (ready && canHit && threat == 0) anyCanHit = true;
            } else if (ahead) {
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
            // never end a turn inside an enemy HQ aura (r2 9) unless the shot from there kills; c_aura1: among aura tiles
            // the one farthest from the HQ wins, so a launcher inside steps outward even with enemies in view
            if (aura && !(ready && killShot)) s -= 50_000_000L + (C.AURA_SAFE ? (9 - auraD) * C.AURA_OUT_W : 0);
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
        objective = pickObjective();
        // c_mend1: a mender's objective is its island tile (kind 3, which telemetry otherwise uses only for the centre)
        boolean mend = C.MEND && mending;
        if (mend) { objective = mendTile; objIsland = mendIsland; objKind = 3; objHQ = null; objRaid = null; objRing = null; objMid = null; recalled = false; guardObj = false; }
        // c_nav3: plan the long march to the team target from the first turn, while forming up at home (a field built
        // only after hitting a wall arrived too late: launchers filled dead-end corridors on Target first)
        if (!mend) {
            // c_mid1: a squad member plans toward the site (Nav descends a field only toward its own target or one within
            // r2 C.FIELD_NEAR_D2 of it, and the site is far from the siege target), also on a turn whose objective is a
            // sighting or a recall: Field.request restarts the field on every change of target
            MapLocation plan = objMid != null ? objMid : midSite != null ? midSite : objHQ;
            if (plan == null) { MapLocation[] ehq = enemyHQs(); if (ehq.length > 0) plan = siegeTarget(ehq); }
            if (plan != null && G.here.distanceSquaredTo(plan) > C.FIELD_FAR_D2) Field.request(plan, true);
        }
        mode = 4;                                   // S, unless a move below is taken
        if (C.TELEMETRY) { objEff = recalled ? 7 : objMid != null ? 8 : objKind; objLoc = objective; }   // c_def2: a recall is kind 7 (home defence); c_mid1: the site 8
        // c_aura1: inside a seen enemy HQ's aura (r2 9), step outward first (aura tiles allowed only strictly outward,
        // Nav.auraStepOK); with no free outward tile, today's logic below
        if (C.AURA_SAFE && G.rc.isMovementReady()) {
            MapLocation h = Nav.auraOf(G.here);
            if (h != null) {
                Nav.avoid = true;
                boolean mv = Nav.moveAway(h);
                Nav.avoid = false;
                if (mv) { mode = 3; return; }
            }
        }
        if (objective == null) return;
        // c_mend1: within r2 4 of a square of the island (heal range, RULES 8.1) hold (mode S); 100 bytecodes, menders only
        if (mend && G.rc.senseNearbyIslandLocations(4, mendIsland).length > 0) return;
        // an enemy island in sight (c_mend1: or a mender's own island, farther than r2 4): each launcher takes the
        // nearest free square of it (audit R4: anchor health falls by 100 x (our robots on its squares) / area per
        // round, and every launcher went to the one stored tile)
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
        if (C.ARMY && !mend && regroup()) return;
        // arch_swarm: a raided well reached with no enemy in sight (march runs only then) is cleared for a while; a
        // predicted well that is not there is cleared for good
        if (objRaid != null && G.here.distanceSquaredTo(objRaid) <= 20 && G.rc.canSenseLocation(objRaid)) {
            boolean real = G.rc.senseWell(objRaid) != null;
            clearRaid(objRaid, real ? G.round : G.round + 5000);
        }
        // c_mid1: within r2 C.MID_HOLD_R2 of the site, hold on a hold tile or step to one (midHold)
        if (objMid != null && G.here.distanceSquaredTo(objMid) <= C.MID_HOLD_R2) { midHold(); return; }
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

    // ---------------------------------------------------------------- arch_swarm objectives
    /** The rank-th nearest enemy HQ to our centroid (ties by location), rank rotating every C.SIEGE_ROTATE rounds. */
    static MapLocation siegeTarget(MapLocation[] ehq) {
        int n = ehq.length;
        int rank = G.round < C.SIEGE_ROTATE_FROM ? 0 : (1 + (G.round - C.SIEGE_ROTATE_FROM) / C.SIEGE_ROTATE) % n;
        MapLocation[] o = HQState.ourHQs;
        // bytecodes: the target is a function of ehq, our HQs (the centroid) and the rank alone, and neither array is
        // written after it is built, so a call with the same two arrays and rank returns the last answer (150-250 per
        // call, once or twice a march turn; ehq comes from the cached enemyHQs() below)
        if (ehq == stEhq && o == stOurs && rank == stRank && o != null && o.length > 0) return stHq;
        MapLocation from = ourCentroid();
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
        stEhq = ehq; stOurs = o; stRank = rank; stHq = hq;
        return hq;
    }

    static MapLocation[] stEhq, stOurs;
    static int stRank;
    static MapLocation stHq;

    static MapLocation[] ehqC, ehqOurs;
    static int ehqCand = -1, ehqSeen = -1;

    /** MapMem.enemyHQs(), rebuilt only when its inputs change. Bytecodes: it builds a new array of symmetry images on
     *  every call (100-400, once or twice a march turn); its result depends only on the surviving candidates, the seen
     *  enemy HQs (append-only, so their count) and our HQ list (a new array whenever it is re-read). Callers here never
     *  write into the returned array. */
    static MapLocation[] enemyHQs() {
        MapLocation[] o = HQState.ourHQs;
        if (ehqC == null || MapMem.cand != ehqCand || MapMem.nEnemyHQSeen != ehqSeen || o != ehqOurs) {
            ehqC = MapMem.enemyHQs();
            ehqCand = MapMem.cand;
            ehqSeen = MapMem.nEnemyHQSeen;
            ehqOurs = o;
        }
        return ehqC;
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

    static MapLocation objRaid, objRing, objHQ;   // objHQ (c_nav3): the team target behind a raid or a ring
    /** c_mid1: this turn's objective is the contested mana well (a squad member's Mid.site()); midSite: the site while
     *  this launcher is in the squad, whatever this turn's objective (march's field plan). */
    static MapLocation objMid, midSite;
    /** c_mid1: the round this squad member first came within r2 C.MID_AREA_R2 of the site (-1: not yet; its tour of
     *  C.MID_TOUR rounds starts there); move-ready turns a holder spent in the free zone with no tile out. */
    static int midSince = -1, midStuck;

    /** c_mid1: this launcher leaves the squad for good (tour over, or boxed in the free zone): the islands and the
     *  siege from its next turn. */
    static void endTour() {
        G.squad = false;
        objMid = null;
        midSite = null;
    }

    /**
     * c_mid1: a holder within r2 C.MID_HOLD_R2 of the site (march, movement ready, no enemy in sight). It stays (S) on a
     * hold tile: outside the free zone (Mid.free: r2 C.MID_FREE_R2 of the site or its twin, the carriers' queue and
     * collect tiles) with no current (a current pushes it at the end of the round: Forest's y=49 currents carried
     * holders onto the pair's collect tiles). Otherwise it steps to the open neighbour that is a hold tile nearest the
     * site; with none, a holder inside the zone takes any tile outside it, nearest the site (Nav.moveAway took only a
     * strictly farther tile, and three holders inside the old zone found none for 1,700 rounds); one that finds no tile
     * out for C.MID_STUCK move-ready turns ends its tour. About 8 x 60 bytecodes on a turn it moves.
     */
    static void midHold() throws GameActionException {
        MapLocation here = G.here, s = objMid;
        boolean inZone = Mid.free(here);
        if (!inZone && MapMem.current(here.x, here.y) == Direction.CENTER) { midStuck = 0; return; }
        Direction best = null;
        int bs = Integer.MAX_VALUE;
        Nav.avoid = true;
        for (int i = 8; --i >= 0; ) {
            Direction d = G.DIRS[i];
            if (!Nav.can(d)) continue;
            MapLocation n = here.add(d);
            if (Mid.free(n)) continue;
            int dn = n.distanceSquaredTo(s);
            int sc = dn <= C.MID_HOLD_R2 && MapMem.current(n.x, n.y) == Direction.CENTER ? dn : 1000 + dn;
            if (sc < bs) { bs = sc; best = d; }
        }
        Nav.avoid = false;
        if (best != null && (inZone || bs < 1000)) {
            mode = 3;
            G.rc.move(best);
            G.here = G.rc.getLocation();
            midStuck = 0;
            return;
        }
        if (inZone && ++midStuck >= C.MID_STUCK) endTour();
    }

    static MapLocation[] predWells = new MapLocation[0];
    static int predRound = -100;
    // c_hunt1: the raided-well table is an open-addressing hash on G.enc (CL_SIZE slots, linear probing; key 0 = empty),
    // so a lookup costs a probe or two however many wells the wider raid clears (the linear table cost 8 an entry, and
    // huntWell can test 39 wells a turn). A full table overwrites the key's home slot (no RNG).
    static final int CL_SIZE = 64, CL_MASK = CL_SIZE - 1;
    static int[] clKey = new int[CL_SIZE], clUntil = new int[CL_SIZE];
    static int nCleared;

    /** Home slot of a location code: mixes x and y (enc & 63 alone is y + 1). */
    static int clHome(int e) { return (e ^ ((e >>> 6) * 11)) & CL_MASK; }

    static void clearRaid(MapLocation w, int round) {
        int e = G.enc(w), i = clHome(e);
        for (int p = 0; p < CL_SIZE; p++, i = (i + 1) & CL_MASK) {
            int k = clKey[i];
            if (k == e) { clUntil[i] = round + C.RAID_CLEAR_ROUNDS; return; }
            if (k == 0) { clKey[i] = e; clUntil[i] = round + C.RAID_CLEAR_ROUNDS; nCleared++; return; }
        }
        i = clHome(e);
        clKey[i] = e;
        clUntil[i] = round + C.RAID_CLEAR_ROUNDS;
    }

    static boolean cleared(MapLocation w) { return clearedEnc(G.enc(w)); }

    /** cleared() by location code. */
    static boolean clearedEnc(int e) {
        int i = clHome(e);
        for (int p = 0; p < CL_SIZE; p++, i = (i + 1) & CL_MASK) {
            int k = clKey[i];
            if (k == e) return G.round < clUntil[i];
            if (k == 0) return false;
        }
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
        // bytecodes: the wells within r2 RAID_R2 of hq, with their dist2 and code, are listed once per predWells (a new
        // array at most every 5-20 rounds) and hq, in the scan order below (index descending), so a turn scans only
        // those (the full scan cost 16 a predicted well, up to 39, every march turn); same tests, same order, same well
        MapLocation[] pw = predWells;
        if (pw != rcPred || !hq.equals(rcHq)) {
            int k = 0;
            for (int i = pw.length; --i >= 0; ) {
                MapLocation w = pw[i];
                int d = w.distanceSquaredTo(hq);
                if (d > C.RAID_R2) continue;
                rcWell[k] = w; rcD[k] = d; rcEnc[k++] = G.enc(w);
            }
            rcN = k; rcPred = pw; rcHq = hq;
        }
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int j = 0; j < rcN; j++) {
            int d = rcD[j];
            if (d >= bd || clearedEnc(rcEnc[j])) continue;
            bd = d; best = rcWell[j];
        }
        if (best == null && C.HUNT) best = huntWell(hq, pw);
        return best;
    }

    /** c_hunt1 (C.HUNT): the uncleared predicted well nearest hq among those beyond r2 C.RAID_R2 of it (each lies within
     *  RAID_R2 of another predicted enemy HQ: computePredWells keeps no other), ties to the lower index as raidWell's
     *  scan. Its candidate list is cached per predWells and hq, as raidWell's. */
    static MapLocation huntWell(MapLocation hq, MapLocation[] pw) {
        if (pw != hcPred || !hq.equals(hcHq)) {
            int k = 0;
            for (int i = pw.length; --i >= 0; ) {
                MapLocation w = pw[i];
                int d = w.distanceSquaredTo(hq);
                if (d <= C.RAID_R2) continue;
                hcWell[k] = w; hcD[k] = d; hcEnc[k++] = G.enc(w);
            }
            hcN = k; hcPred = pw; hcHq = hq;
        }
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int j = 0; j < hcN; j++) {
            int d = hcD[j];
            if (d >= bd || clearedEnc(hcEnc[j])) continue;
            bd = d; best = hcWell[j];
        }
        return best;
    }

    static MapLocation[] hcWell = new MapLocation[40], hcPred;
    static int[] hcD = new int[40], hcEnc = new int[40];
    static int hcN;
    static MapLocation hcHq;

    // raidWell's candidates (predWells holds at most 39: computePredWells stops adding at 38, two at a time)
    static MapLocation[] rcWell = new MapLocation[40], rcPred;
    static int[] rcD = new int[40], rcEnc = new int[40];
    static int rcN;
    static MapLocation rcHq;

    public static int regroups, follows;   // diagnostics (C.ARMY)
    static int formTurns;

    /**
     * Cohesion (C.ARMY), called only with no enemy in sight. Returns true if it took the move (or chose to hold).
     * Fewer than C.GROUP_MIN launchers here (self included): go to the nearest visible ally launcher, else back toward
     * the nearest own HQ, where new launchers appear, and hold there; except toward an enemy sighting near one of our
     * HQs (home defence). Enough launchers: follow the lowest-id launcher in vision when farther than C.FOLLOW_R2; the
     * leader itself marches to the objective.
     */
    static boolean regroup() throws GameActionException {
        // c_def2: a recalled launcher neither holds to form, follows nor retreats alone: it walks to the alarmed HQ,
        // fight() takes over when raiders are in sight, and the siege resumes when the alarm drops
        if (recalled) { if (C.TELEMETRY) objEff = 7; return false; }
        if (objMid != null) return midRegroup();         // c_mid1: the squad keeps to itself
        // bytecodes: n and the lowest-id leader come from G.startTurn's robot loop (nAllyFighters, allyLeader: the same
        // robots of G.nearby; robots are all ours or theirs), and the closest ally matters only below the group size, so
        // it alone is searched, and only then (a 65-launcher blob spent 2,300 in this loop every march turn)
        RobotInfo leader = G.allyLeader, closest = null;
        int n = 1 + G.nAllyFighters, cd = Integer.MAX_VALUE;
        if (n < C.GROUP_MIN) {
            for (int i = G.nearby.length; --i >= 0; ) {
                RobotInfo r = G.nearby[i];
                if (r.team != G.us || r.type != RobotType.LAUNCHER) continue;
                int d = G.here.distanceSquaredTo(r.location);
                if (d < cd) { cd = d; closest = r; }
            }
        }
        // arch_swarm: GROUP_MIN launchers form up near home before leaving; in the field a pair is a group, and only a
        // launcher with no ally in sight turns back (v3: requiring 4 in the field made launchers regroup 44-53% of
        // their opening turns and fight alone, alone 0.44 on Cat). In a cloud vision is r2 4 (robots in clouds are
        // hidden beyond r2 4), so there a pair counts even at home (Forest: launchers huddled in their HQs' clouds).
        MapLocation home = HQState.nearest(G.here);
        boolean forming = home != null && G.here.distanceSquaredTo(home) <= C.FORM_R2 && !G.rc.senseCloud(G.here);
        if (!forming || n >= C.GROUP_MIN) formTurns = 0;
        if (n < (forming ? C.GROUP_MIN : 2)) {
            if (home != null && objective.distanceSquaredTo(home) <= C.HOME_DEFENCE_R2) { if (C.TELEMETRY) objEff = 7; return false; }
            if (forming && ++formTurns > C.FORM_MAX_TURNS) return false;   // c_nav3: waited long enough, go
            regroups++;
            mode = 5;
            // c_aura1: the three regroup moves avoid enemy HQ auras like the march (they moved without avoid)
            if (closest != null) {
                if (C.TELEMETRY) { objEff = 4; objLoc = closest.location; }
                if (cd > 2) { Nav.avoid = C.AURA_SAFE; Nav.moveTo(closest.location); Nav.avoid = false; }
                return true;
            }
            if (C.TELEMETRY) { objEff = 5; objLoc = home; }
            if (home != null && G.here.distanceSquaredTo(home) > 13) { Nav.avoid = C.AURA_SAFE; Nav.moveTo(home); Nav.avoid = false; }
            return true;
        }
        // c_mid1: never a leader at the site (a holder does not move: 11672 stood 1,433 rounds on a collect tile of the
        // pair following holder 10044, r2 18 away in the packed hold disc)
        if (leader.ID < G.id && G.here.distanceSquaredTo(leader.location) > C.FOLLOW_R2 && !atSite(leader.location)) {
            follows++;
            mode = 6;
            if (C.TELEMETRY) { objEff = 6; objLoc = leader.location; }
            Nav.avoid = C.AURA_SAFE;
            Nav.moveTo(leader.location);
            Nav.avoid = false;
            return true;
        }
        return false;
    }

    /** c_mid1: whether l is within r2 C.MID_AREA_R2 of the published site (false with none or with C.MID off). */
    static boolean atSite(MapLocation l) throws GameActionException {
        if (!C.MID) return false;
        MapLocation s = Mid.site();
        return s != null && l.distanceSquaredTo(s) <= C.MID_AREA_R2;
    }

    /**
     * c_mid1: cohesion for a squad member bound for the site (called by regroup; true if it took the move or holds).
     * Within r2 C.MID_AREA_R2 of the site: nothing (march holds or approaches; Forest's site lies in a cloud strip
     * where vision is r2 4, and the lone-launcher rule walked holders home). Forming at home: wait for C.MID_GROUP squad
     * members in vision, at most C.FORM_MAX_TURNS move-ready turns (regroup's counter). Otherwise follow the
     * lowest-id squad member in vision when farther than C.FOLLOW_R2 and nearer the site than this launcher
     * (regroup's leader would be a siege launcher and lead the squad to the siege; G counts squad members by id, and a
     * member whose tour is over walks away from the site), and march to the site alone when no squad member is in
     * sight.
     */
    static boolean midRegroup() throws GameActionException {
        if (G.here.distanceSquaredTo(objMid) <= C.MID_AREA_R2) { formTurns = 0; return false; }
        int n = 1 + G.nSquad;
        MapLocation home = HQState.nearest(G.here);
        boolean forming = home != null && G.here.distanceSquaredTo(home) <= C.FORM_R2 && !G.rc.senseCloud(G.here);
        if (!forming || n >= C.MID_GROUP) formTurns = 0;
        else if (++formTurns <= C.FORM_MAX_TURNS) {
            regroups++;
            mode = 5;
            if (C.TELEMETRY) { objEff = 5; objLoc = home; }
            if (G.here.distanceSquaredTo(home) > 13) { Nav.avoid = C.AURA_SAFE; Nav.moveTo(home); Nav.avoid = false; }
            return true;
        }
        RobotInfo leader = G.squadLeader;
        if (leader != null && leader.ID < G.id && G.here.distanceSquaredTo(leader.location) > C.FOLLOW_R2
                && leader.location.distanceSquaredTo(objMid) < G.here.distanceSquaredTo(objMid)) {
            follows++;
            mode = 6;
            if (C.TELEMETRY) { objEff = 6; objLoc = leader.location; }
            Nav.avoid = C.AURA_SAFE;
            Nav.moveTo(leader.location);
            Nav.avoid = false;
            return true;
        }
        return false;
    }

    static int objIsland;
    static int islandCount = -1;   // min(35, getIslandCount()), read once
    /** c_def2: this turn's objective is an alarmed HQ (Comms.ALARM), set by pickObjective. */
    static boolean recalled;

    /** c_guard1: this turn's objective is a home sighting (homeSighting), its slot's stamp, and the sighting this
     *  launcher found empty with the stamp it then had (skipped until the slot is stamped again). */
    static boolean guardObj;
    static MapLocation lastGuardLog;   // G.DEBUG only
    static int guardStamp, guardClearStamp;
    static MapLocation guardClear;

    /**
     * c_guard1: the sighting nearest this launcher, within r2 C.GUARD_R2 of it, with stamp age at most 1 (31 rounds),
     * in our home zone (within r2 C.GUARD_HOME_R2 of our nearest HQ and nearer it than every predicted enemy HQ), and
     * not the one this launcher found empty under the same stamp; null if none. Sets guardStamp.
     */
    static MapLocation homeSighting() throws GameActionException {
        int stamp = (G.round >> 4) & 15, bd = C.GUARD_R2 + 1;
        MapLocation best = null;
        MapLocation[] ehq = null;
        for (int i = Comms.ENEMY; i < Comms.ENEMY + Comms.NENEMY; i++) {
            int c = Comms.read(i);
            if (c == 0) continue;
            int st = c >>> 12;
            if (((stamp - st) & 15) > 1) continue;
            MapLocation l = G.dec(c & 0xfff);
            int d = G.here.distanceSquaredTo(l);
            if (d >= bd) continue;
            if (st == guardClearStamp && guardClear != null && guardClear.distanceSquaredTo(l) <= 20) continue;
            MapLocation h = HQState.nearest(l);
            if (h == null || h.distanceSquaredTo(l) > C.GUARD_HOME_R2) continue;
            if (ehq == null) ehq = enemyHQs();
            if (!homeZone(l, h, ehq)) continue;
            bd = d;
            best = l;
            guardStamp = st;
        }
        return best;
    }

    /** c_guard1: l lies within r2 C.GUARD_HOME_R2 of h (our HQ nearest l) and nearer h than every predicted enemy HQ. */
    static boolean homeZone(MapLocation l, MapLocation h, MapLocation[] ehq) {
        int dh = h.distanceSquaredTo(l);
        if (dh > C.GUARD_HOME_R2) return false;
        for (int k = ehq.length; --k >= 0; ) if (ehq[k].distanceSquaredTo(l) <= dh) return false;
        return true;
    }

    /** c_isle1 (C.ISLE_THREAT): an even-id launcher's last island scan (islandScan): the round of the next one, whether
     *  the enemy is within the margin of conquest, and the nearest located island theirs by theirsFor (null: none). */
    static int isleCheck = -1000, isleBestId;
    static boolean isleThreat;
    static MapLocation isleBest;

    /** c_isle1: islands a team needs for conquest, ceil(0.75 n) (RULES: anchors / N >= 0.75f at a placement). */
    static int conquestNeed(int n) { return (3 * n + 3) / 4; }        // 4->3 6->5 7->6 8->6 9->7 12->9

    /** c_isle1: the enemy holds `them` of n islands, within C.ISLE_MARGIN_SMALL of conquest (C.ISLE_MARGIN_LARGE from
     *  C.ISLE_LARGE_N islands), and at least one. */
    static boolean conquestThreat(int them, int n) {
        if (n <= 0 || them <= 0) return false;
        return them >= Math.max(1, conquestNeed(n) - (n >= C.ISLE_LARGE_N ? C.ISLE_MARGIN_LARGE : C.ISLE_MARGIN_SMALL));
    }

    /** c_isle1: under a threat even ids take the island first; odd ids keep c_hr1's objectives. */
    static boolean isleFirst(boolean threat, int id) { return threat && (id & 1) == 0; }

    /** c_isle1: theirs for the threat: pickObjective's rule (our own record when fresh or the slot is empty, else the
     *  slot), or our own owner-2 record within C.ISLE_MEM rounds over a neutral slot. */
    static boolean theirsFor(int shared, int own, int seen, int round) {
        int rule = seen > 0 && (round - seen <= 10 || shared == 0) ? own : shared >>> 12;
        return rule == 2 || (own == 2 && seen > 0 && round - seen <= C.ISLE_MEM && (shared >>> 12) == 0);
    }

    /** c_isle1: pickObjective's island loop with theirsFor: the islands theirs (isleThreat by conquestThreat) and the
     *  nearest located one (lowest id among equals). A pass cut by C.ISLAND_LOOP_GUARD keeps the last result. */
    static void islandScan() throws GameActionException {
        if (islandCount < 0) islandCount = Math.min(35, G.rc.getIslandCount());
        RobotController rc = G.rc;
        int[] own = MapMem.islandOwner, seen = MapMem.islandSeen;
        int round = G.round, them = 0, bd = Integer.MAX_VALUE, bi = 0;
        MapLocation best = null;
        for (int id = islandCount; id > 0; id--) {
            if (Clock.getBytecodesLeft() < C.ISLAND_LOOP_GUARD) return;
            int shared = rc.readSharedArray(Comms.ISLANDS + id);
            if (shared < 0x2000 && own[id] != 2) continue;          // neither source can say "theirs" (most ids)
            if (!theirsFor(shared, own[id], seen[id], round)) continue;
            them++;
            MapLocation t = G.dec(shared & 0xfff);
            if (t == null) t = MapMem.islandTile[id];
            if (t == null) continue;
            int d = G.here.distanceSquaredTo(t);
            if (d <= bd) { bd = d; best = t; bi = id; }
        }
        isleThreat = conquestThreat(them, islandCount);
        isleBest = best;
        isleBestId = bi;
    }

    static MapLocation pickObjective() throws GameActionException {
        recalled = false;
        guardObj = false;
        objIsland = 0;
        objHQ = null;
        objRaid = null;
        objRing = null;
        objMid = null;
        // c_mid1: a squad member's site (null for every other launcher and while no site is published). Its tour starts
        // when it first comes within r2 C.MID_AREA_R2 of the site; C.MID_TOUR rounds later it leaves the squad for good
        MapLocation site = G.squad ? Mid.site() : null;
        if (site != null) {
            if (midSince < 0) { if (G.here.distanceSquaredTo(site) <= C.MID_AREA_R2) midSince = G.round; }
            else if (G.round - midSince >= C.MID_TOUR) { endTour(); site = null; }
        }
        midSite = site;
        // c_isle1: under a conquest threat an even-id launcher takes the nearest enemy-held island before any sighting
        // (march stands it on a free square, so the anchor decays); a target our own record of the last 10 rounds says is
        // not theirs (theirsFor's answer whatever the slot) is dropped until the next scan, every C.ISLE_RECHECK rounds
        // and only with C.ISLE_MIN_LEFT bytecodes left (review: "seen this round" alone missed it whenever the sighting
        // fell on a turn without march: scanIslands runs every 4th round, a moving launcher marches every other one,
        // and an even id's scan rounds are even). Menders keep theirs.
        if (C.ISLE_THREAT && (G.id & 1) == 0 && !(C.MEND && mending)) {
            if (isleBest != null && MapMem.islandOwner[isleBestId] != 2 && G.round - MapMem.islandSeen[isleBestId] <= 10 && MapMem.islandSeen[isleBestId] > 0) isleBest = null;
            if (G.round >= isleCheck && Clock.getBytecodesLeft() >= C.ISLE_MIN_LEFT) { isleCheck = G.round + C.ISLE_RECHECK; islandScan(); }
            if (isleFirst(isleThreat, G.id) && isleBest != null) { objKind = 1; objIsland = isleBestId; return isleBest; }
        }
        // arch_swarm objectives: a nearby fight (shared sighting within r2 C.SIGHTING_R2); enemy-held islands from
        // C.ISLAND_HUNT_START; the carrier raid (predicted enemy wells nearest the enemy HQ); the siege ring
        MapLocation e = Comms.nearestEnemy(G.here, 2);
        if (e != null && G.here.distanceSquaredTo(e) <= C.SIGHTING_R2) { objKind = 0; return e; }
        // c_def2 recall: the nearest of our HQs with alarm >= C.RAID_ALARM, within r2 C.RECALL_R2 and nearer than the
        // siege target, before C.RECALL_UNTIL; the launcher rallies on the HQ tile. Slot 0 means no alarm anywhere, so
        // the common turn pays one read; the siege target is computed only once an HQ passes the alarm and range tests.
        if (C.RECALL && G.round < C.RECALL_UNTIL && Comms.read(Comms.ALARM) != 0) {
            MapLocation best = null;
            int bd = Integer.MAX_VALUE, td = -1;
            for (int i = 0; i < 4; i++) {                 // HQ_LOC order is the HQs' alarm order (HQ.hqIdx)
                int v = Comms.read(Comms.HQ_LOC + i);
                if (v == 0 || Comms.alarm(i) < C.RAID_ALARM) continue;
                MapLocation h = G.dec(v);
                int d = G.here.distanceSquaredTo(h);
                if (d > C.RECALL_R2) continue;
                if (td < 0) {                             // dist2 to the siege target; none known: no limit
                    MapLocation[] ehq = enemyHQs();
                    // c_mid1: a squad member compares the alarmed HQ with the site (holders stay; one near home defends)
                    td = site != null ? G.here.distanceSquaredTo(site)
                        : ehq.length > 0 ? G.here.distanceSquaredTo(siegeTarget(ehq)) : Integer.MAX_VALUE;
                }
                if (d >= td) continue;
                if (d < bd) { bd = d; best = h; }
            }
            if (best != null) { objKind = 0; recalled = true; return best; }
        }
        // c_guard1: a raid on our home zone (a home well 12 tiles out is beyond SIGHTING_R2), when nearer than the site
        // or the siege target (the recall's rule: holders and the far army keep to theirs); grouping is unchanged
        if (C.GUARD && G.round < C.GUARD_UNTIL) {
            MapLocation g = homeSighting();
            if (g != null) {
                MapLocation[] ehq = enemyHQs();
                int td = site != null ? G.here.distanceSquaredTo(site)
                    : ehq.length > 0 ? G.here.distanceSquaredTo(siegeTarget(ehq)) : Integer.MAX_VALUE;
                if (G.here.distanceSquaredTo(g) < td) {
                    if (G.DEBUG && !g.equals(lastGuardLog)) { lastGuardLog = g; System.out.println("GUARD r" + G.round + " #" + G.id + " at " + G.here + " objective " + g + " td " + td); }
                    objKind = 0; guardObj = true; return g;
                }
            }
        }
        // c_mid1: the site, before enemy islands (the island hunt from r0 would pull the holders away); telemetry code
        // kind 2 (the 2-bit field is full), OBJ kind 8
        if (site != null) { objKind = 2; objMid = site; return site; }
        if (G.round >= C.ISLAND_HUNT_START) {
            // bytecodes (28-39 an id, 35 ids, every march turn): the island count is fixed for the map (20 a call);
            // the slot is read directly; an id is skipped at once when neither source can say "theirs" (a slot below
            // 0x2000 has owner 0 or 1, and our own record is not 2), which is most ids; ids run downward, so d <= bd
            // keeps the lowest id among equals as the upward d < bd did
            if (islandCount < 0) islandCount = Math.min(35, G.rc.getIslandCount());
            RobotController rc = G.rc;
            int[] own = MapMem.islandOwner, seen = MapMem.islandSeen;
            MapLocation best = null;
            int bd = Integer.MAX_VALUE;
            for (int id = islandCount; id > 0; id--) {
                int shared = rc.readSharedArray(Comms.ISLANDS + id);
                if (shared < 0x2000 && own[id] != 2) continue;
                // our own sighting when fresh, or when the shared slot is empty (launchers far from home cannot write)
                int owner = seen[id] > 0 && (G.round - seen[id] <= 10 || shared == 0) ? own[id] : shared >>> 12;
                if (owner != 2) continue;
                MapLocation t = Comms.islandTile(id);
                if (t == null) t = MapMem.islandTile[id];
                if (t == null) continue;
                int d = G.here.distanceSquaredTo(t);
                if (d <= bd) { bd = d; best = t; objIsland = id; }
            }
            if (best != null) { objKind = 1; return best; }
        }
        MapLocation[] ehq = enemyHQs();
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
            objHQ = hq;
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
