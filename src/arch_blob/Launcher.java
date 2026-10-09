package arch_blob;

import battlecode.common.*;

/**
 * Launcher: the army. Attack r2 16, vision r2 20, 20 damage per action (one per turn), one move per two turns
 * (move cooldown 20). HQs cannot be damaged (RULES), so they are never targeted.
 *
 * Turn: shoot if a target is in range; if movement is ready, fight (score the 9 tiles) when enemies are visible, else
 * march to the objective; shoot again if the action is still ready after moving.
 * Objective: a fresh enemy sighting (comms) > an enemy-held island (stand on it so its anchor decays) > the predicted
 * enemy HQ (symmetry; stop outside its r2 9 fire).
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
        if (lastEnemyRound < 0) lastEnemyRound = G.spawnRound;
        if (G.nEnemyFighters > 0) lastEnemyRound = G.round;
        track();
        shoot();
        if (rc.isMovementReady()) {
            if (hasHittableEnemies()) { mode = 1; fight(); }
            else blobMove();
        } else mode = hasHittableEnemies() ? 2 : 0;
        if (rc.isActionReady()) { G.here = rc.getLocation(); refreshEnemies(); shoot(); }
        G.note = String.valueOf((char) ('0' + objKind));
        G.extra = ",pn=" + pinnedSeen + ",ua=" + unsafeStepsAvoided + ",bl=" + (advancing ? 1 : 0) + ",oc=" + overflows + ",hp=" + helps;
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

    /** Priority: fighters and anchor-carrying carriers, then amplifiers, then the rest; lowest health first. */
    static int priority(RobotInfo e) {
        switch (e.type) {
            case LAUNCHER: case DESTABILIZER: return 4;
            case CARRIER: return e.getTotalAnchors() > 0 ? 4 : 2;
            case AMPLIFIER: return 3;
            case BOOSTER: return 3;
            default: return 0;
        }
    }

    static void shoot() throws GameActionException {
        RobotController rc = G.rc;
        while (rc.isActionReady()) {
            RobotInfo best = null;
            int bp = -1, bh = Integer.MAX_VALUE;
            for (int i = G.enemies.length; --i >= 0; ) {
                RobotInfo e = G.enemies[i];
                if (e.type == RobotType.HEADQUARTERS || !rc.canAttack(e.location)) continue;
                int p = priority(e);
                // arch_blob: focus the lowest-HP target, ties by the lowest id (the whole blob picks the same one)
                if (p > bp || (p == bp && (e.health < bh || (e.health == bh && best != null && e.ID < best.ID)))) { bp = p; bh = e.health; best = e; }
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
        boolean ahead = G.nAllyFighters + 1 - G.nEnemyFighters >= 2;
        int threat0 = 0;
        boolean hit0 = false;
        MapLocation here = rc.getLocation();
        // per-enemy data computed once (audit R2: per-tile pinned lookups made a 10-fighter fight cost ~12k bytecodes
        // against the launcher's 10k): kind 0 = hittable non-fighter, 1 = fighter (threat radius r), 2 = HQ
        RobotInfo[] es = G.enemies;
        int n = es.length;
        int[] ex = new int[n], ey = new int[n], er = new int[n], kind = new int[n];
        for (int i = n; --i >= 0; ) {
            RobotInfo e = es[i];
            ex[i] = e.location.x; ey[i] = e.location.y;
            if (e.type == RobotType.HEADQUARTERS) kind[i] = 2;
            else if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) { kind[i] = 1; er[i] = C.MICRO && isPinned(e.ID) ? 16 : C.THREAT_R2; }
        }
        Direction best = Direction.CENTER;
        long bestScore = Long.MIN_VALUE;
        boolean anyCanHit = false;
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
            boolean canHit = false;
            for (int i = n; --i >= 0; ) {
                int dx = tx - ex[i], dy = ty - ey[i], dd = dx * dx + dy * dy;
                switch (kind[i]) {
                    case 2: if (dd <= 9) threat++; break;
                    case 1: if (dd <= er[i]) threat++; if (dd < minD) minD = dd; if (dd <= 16) canHit = true; break;
                    default: if (dd <= 16) canHit = true;
                }
            }
            long s;
            boolean aura = false;
            for (int i = n; --i >= 0; ) if (kind[i] == 2) { int dx = tx - ex[i], dy = ty - ey[i]; if (dx * dx + dy * dy <= 9) aura = true; }
            if (!C.MICRO) {
                // g_iter0's scoring (c_micro1's pinned/acceptable/stay rules failed delivery on diag-top4: exposure
                // +0.029, t +1.75; kills -5.3, t -2.3): not outnumbered and ready -> any hitting tile, fewest
                // threats, then the edge of range; else fewest threats, then the farthest tile
                if (d == Direction.CENTER) { threat0 = threat; hit0 = canHit; }
                boolean hit = canHit;
                // C.MICRO2 (parity hold): unless clearly ahead, never step into more enemy reach to fire, and stay to
                // fire when we can already hit (replica telemetry: at dN=0 we won 0.31 of engagements vs their 0.61;
                // first hit 0.42 vs 0.58; we stepped in to fire 0.155 of turns vs their 0.107)
                if (C.MICRO2 && !ahead && d != Direction.CENTER && (hit0 || threat > threat0)) hit = false;
                if (ready && !outnumbered) { s = (hit ? 1_000_000L : 0) - threat * 10_000L + Math.min(minD, 100) * 10; if (hit) anyCanHit = true; }
                else s = -threat * 10_000L + Math.min(minD, 100) * 10;
                if (d == Direction.CENTER) s += 1;
            } else if (ready) {
                boolean acceptable = canHit && (threat <= 1 || superior);
                if (canHit && !acceptable) unsafeStepsAvoided++;
                if (acceptable) anyCanHit = true;
                s = (acceptable ? 1_000_000L : 0) - threat * 10_000L + Math.min(minD, 100) * 10;
                if (d == Direction.CENTER) s += 50;
            } else {
                s = -threat * 10_000L + Math.min(minD, 100);
                if (d == Direction.CENTER) s += 50;   // moving costs the next turn's move: stay on ties
            }
            if (aura) s -= 5_000_000L;      // arch_blob: never end a turn inside an enemy HQ aura (spawn camp from r2 10-25)
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
            fightA = Telemetry.fightA(ready, superior, outnumbered, anyCanHit, best != Direction.CENTER, bk, gb, C.MICRO,
                fightShots, 0, G.nEnemyFighters, G.nAllyFighters);
            fightB = Telemetry.fightTile(bThreat, bHit, bMin, nPinned);
            fightC = Telemetry.fightTile(sThreat, sHit, sMin, nt);
            fought = true;
        }
    }

    // ------------------------------------------------------------------ arch_blob: the blob
    static boolean advancing, movingOn;
    static int lastEnemyRound = -1;
    static int holdSince = -1;
    public static int overflows, helps;   // diagnostics: launchers that found the siege ring full; turns answering HELP
    static MapLocation siegeHQ;
    static MapLocation rally;
    static int rallyRound = -1000;

    /** BLOB_BASE + round / BLOB_ROUNDS, at most BLOB_MAX. */
    static int blobMin() { return Math.min(C.BLOB_MAX, C.BLOB_BASE + G.round / C.BLOB_ROUNDS); }

    /**
     * No enemy in sight. In order: an enemy HQ within C.SIEGE_R2 -> hold the spawn-camp ring; from C.CLEAR_FROM two in
     * three clear enemy-held islands; a follower (a lower id in vision) keeps within C.BLOB_FOLLOW_R2 of the lowest id it
     * sees; the leader gathers at the rally point until it sees blobMin() launchers, then advances (enemy-held islands,
     * then the enemy HQs), waiting while fewer than half of the launchers it sees are close.
     */
    static void blobMove() throws GameActionException {
        MapLocation here = G.here;
        RobotInfo leader = null;
        int n = 1, close = 0;
        for (int i = G.nearby.length; --i >= 0; ) {
            if (Clock.getBytecodesLeft() < 4000) break;
            RobotInfo r = G.nearby[i];
            if (r.team != G.us || r.type != RobotType.LAUNCHER) continue;
            n++;
            if (r.ID < G.id && (leader == null || r.ID < leader.ID)) leader = r;
            if (here.distanceSquaredTo(r.location) <= C.BLOB_FOLLOW_R2) close++;
        }
        int bmin = blobMin();
        boolean quiet = G.round - lastEnemyRound >= C.QUIET_GO;
        if (n >= bmin) advancing = true;
        else if (n * 3 < bmin && !quiet) advancing = false;     // a depleted blob falls back only under threat
        mode = 4;
        if (C.TELEMETRY) objEff = -1;
        // home defence: a fresh sighting close to one of our HQs pulls every launcher that is not sieging
        MapLocation e = Comms.nearestEnemy(here, 1);
        MapLocation home = HQState.nearest(here);
        MapLocation[] ehq = MapMem.enemyHQs();
        if (siegeHQ == null || !contains(ehq, siegeHQ)) { siegeHQ = ehq.length > 0 ? G.nearest(here, ehq) : null; movingOn = false; }
        boolean atSiege = siegeHQ != null && here.distanceSquaredTo(siegeHQ) <= C.SIEGE_R2;
        if (!atSiege && e != null && home != null && e.distanceSquaredTo(home) <= C.HOME_DEFENCE_R2 && here.distanceSquaredTo(e) <= 400) {
            objKind = 0; go(e, 0); return;
        }
        MapLocation help = atSiege ? null : Comms.help(2);
        if (help != null && here.distanceSquaredTo(help) > 13) { objKind = 0; helps++; go(help, 0); return; }
        if (atSiege) {
            MapLocation next = null;
            int bd = Integer.MAX_VALUE;
            for (int i = ehq.length; --i >= 0; ) {
                if (ehq[i].equals(siegeHQ)) continue;
                int d = here.distanceSquaredTo(ehq[i]);
                if (d < bd) { bd = d; next = ehq[i]; }
            }
            movingOn = false;
            if (n > C.RING_FULL && next != null) { overflows++; siegeHQ = next; movingOn = true; objKind = 2; go(next, 2); return; }   // enough here: the next HQ
            else {
                if (camp(siegeHQ)) return;
                overflows++;
                MapLocation isl = enemyIsland();
                if (isl != null) { objKind = 1; go(isl, 1); return; }
                if (next != null) siegeHQ = next;
                else { objKind = 2; return; }           // the only ring is full: stand behind it
            }
        }
        if (movingOn && siegeHQ != null) { objKind = 2; go(siegeHQ, 2); return; }
        MapLocation isl0 = enemyIsland();
        // an enemy-held island in sight is stood on by everyone who sees it (anchor health falls by 100 x our robots
        // on it / area per round); hunters (one in three from C.HUNT_FROM, two in three from C.CLEAR_FROM) go to every
        // enemy island they know, else to the images of our side's islands they have not visited lately
        int h3 = G.idHash() % 3;
        boolean hunter = (G.round >= C.HUNT_FROM && h3 == 0) || (G.round >= C.CLEAR_FROM && h3 != 2);
        if (isl0 != null && (here.distanceSquaredTo(isl0) <= 20 || hunter)) { objKind = 1; go(isl0, 1); return; }
        if (hunter) {
            MapLocation p = predictedIsland();
            if (p != null) { objKind = 1; islandAt = 0; go(p, 1); return; }
        }
        MapLocation r = rallyPoint();
        // never hold next to one of our HQs: launchers that stood there (followers of a blocked leader) jammed the HQ
        // with its carriers and filled its spawn tiles (v2 BatSignal: production stopped at r600, HQ "no spawn tile"
        // 60% of turns, no anchor could be taken)
        if (home != null && r != null && here.distanceSquaredTo(home) <= C.HOME_CLEAR_R2) {
            mode = 5; objKind = 3;
            if (C.TELEMETRY) { objEff = 5; objLoc = r; }
            if (!Nav.moveTo(r)) Nav.moveAway(home);
            return;
        }
        if (leader != null) {
            int dl = here.distanceSquaredTo(leader.location);
            if (dl > C.BLOB_FOLLOW_R2) {
                mode = 6;
                if (C.TELEMETRY) { objEff = 6; objLoc = leader.location; }
                Nav.moveTo(leader.location);
                follows++;
            } else if (advancing) {
                // close to an advancing leader: step toward the blob's objective too, but never ahead of the leader (v2
                // Forest: followers that only held boxed their leader in, and a 60-launcher blob sat beside our HQ)
                MapLocation t = isl0 != null ? isl0 : siegeHQ;
                if (t != null && Math.sqrt(here.distanceSquaredTo(t)) >= Math.sqrt(leader.location.distanceSquaredTo(t)) - 1.5) {
                    mode = 3; objKind = isl0 != null ? 1 : 2;
                    if (C.TELEMETRY) { objEff = objKind; objLoc = t; }
                    Nav.moveTo(t);
                }
            }
            return;
        }
        if (!advancing) {
            if (holdSince < 0) holdSince = G.round;
            // a blob stuck under its size for long (a corridor, losses) goes with two thirds of it; and once the front
            // has been quiet for C.QUIET_GO rounds any group of 4 goes (v2 BatSignal: g_iter0 had no launcher from r250,
            // but a 30-launcher BLOB_MIN held most of ours at the rally and only 6 reached its HQ)
            if (G.round - holdSince > 80 && n * 3 >= bmin * 2) advancing = true;
            if (G.round >= C.QUIET_FROM && quiet && n >= 4) advancing = true;
        }
        if (!advancing) {
            regroups++;
            objKind = 3;
            if (r != null && here.distanceSquaredTo(r) > 2) { mode = 5; if (C.TELEMETRY) { objEff = 5; objLoc = r; } Nav.moveTo(r); }
            return;
        }
        holdSince = -1;
        // let the blob catch up: wait while few of the launchers seen are close (v1: "half of them within r2 8" could
        // never hold in a blob of 40+, and a 190-launcher blob sat at its rally all game on Forest)
        if (close < 6 && close * 3 < n - 1) { objKind = 2; return; }
        if (isl0 != null) { objKind = 1; go(isl0, 1); return; }
        if (siegeHQ != null) { objKind = 2; go(siegeHQ, 2); return; }
        objKind = 3;
        go(new MapLocation(G.W / 2, G.H / 2), 3);
    }

    static boolean contains(MapLocation[] a, MapLocation l) {
        for (int i = a.length; --i >= 0; ) if (a[i].equals(l)) return true;
        return false;
    }

    /** March toward t (kind for telemetry: 0 sighting, 1 enemy island, 2 enemy HQ, 3 centre); on an enemy island in
     *  sight take its nearest free square; never walk into enemy HQ fire. */
    static void go(MapLocation t, int kind) throws GameActionException {
        objective = t;
        objIsland = kind == 1 ? islandAt : 0;
        if (C.TELEMETRY) { objEff = kind; objLoc = t; }
        if (objIsland > 0 && G.here.distanceSquaredTo(objective) <= 20) {
            if (G.rc.senseIsland(G.here) == objIsland) return;
            MapLocation[] tiles = G.rc.senseNearbyIslandLocations(objIsland);
            MapLocation best = null;
            int bd = Integer.MAX_VALUE;
            for (int i = tiles.length; --i >= 0; ) {
                if (Clock.getBytecodesLeft() < 2500) break;
                MapLocation tl = tiles[i];
                if (G.rc.canSenseLocation(tl) && G.rc.isLocationOccupied(tl)) continue;
                int d = G.here.distanceSquaredTo(tl);
                if (d < bd) { bd = d; best = tl; }
            }
            if (best != null) objective = best;
        }
        MapLocation[] ehq = MapMem.enemyHQs();
        for (int i = ehq.length; --i >= 0; ) {
            if (G.here.distanceSquaredTo(ehq[i]) <= 25 && objective.distanceSquaredTo(ehq[i]) <= 9) return;
        }
        mode = 3;
        Nav.moveTo(objective);
    }

    /** The rally point: C.RALLY_PCT percent of the way from the centroid of our HQs toward that of the predicted enemy
     *  HQs (recomputed every 50 rounds, as symmetry resolves). */
    static MapLocation rallyPoint() {
        if (rally != null && G.round - rallyRound < 50) return rally;
        MapLocation[] ours = HQState.ourHQs;
        if (ours == null || ours.length == 0) return null;
        int ox = 0, oy = 0;
        for (int i = ours.length; --i >= 0; ) { ox += ours[i].x; oy += ours[i].y; }
        ox /= ours.length; oy /= ours.length;
        MapLocation[] ehq = MapMem.enemyHQs();
        int ex = G.W - 1 - ox, ey = G.H - 1 - oy;
        if (ehq.length > 0) {
            ex = 0; ey = 0;
            for (int i = ehq.length; --i >= 0; ) { ex += ehq[i].x; ey += ehq[i].y; }
            ex /= ehq.length; ey /= ehq.length;
        }
        rally = new MapLocation(ox + (ex - ox) * C.RALLY_PCT / 100, oy + (ey - oy) * C.RALLY_PCT / 100);
        rallyRound = G.round;
        return rally;
    }

    static int[] ringDx, ringDy;

    /** Spawn camp: hold a tile at r2 RING_MIN..RING_MAX from the enemy HQ h; false when no free ring tile is in vision. */
    static boolean camp(MapLocation h) throws GameActionException {
        RobotController rc = G.rc;
        objKind = 2;
        if (C.TELEMETRY) { objEff = 2; objLoc = h; }
        int d0 = G.here.distanceSquaredTo(h);
        if (d0 >= C.RING_MIN && d0 <= C.RING_MAX) return true;      // on the ring: hold and fire at newborns
        if (ringDx == null) {
            int k = 0;
            int[] dx = new int[120], dy = new int[120];
            for (int x = -5; x <= 5; x++) for (int y = -5; y <= 5; y++) {
                int dd = x * x + y * y;
                if (dd >= C.RING_MIN && dd <= C.RING_MAX) { dx[k] = x; dy[k++] = y; }
            }
            ringDx = new int[k]; ringDy = new int[k];
            System.arraycopy(dx, 0, ringDx, 0, k); System.arraycopy(dy, 0, ringDy, 0, k);
        }
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = ringDx.length; --i >= 0; ) {
            if (Clock.getBytecodesLeft() < 2500) break;
            int x = h.x + ringDx[i], y = h.y + ringDy[i];
            if (!G.onMap(x, y)) continue;
            int d = G.dist2(x, y, G.here.x, G.here.y);
            if (d >= bd || d > 20) continue;                          // in vision only
            if (MapMem.known(x, y) && MapMem.isWall(x, y)) continue;
            MapLocation t = new MapLocation(x, y);
            if (!rc.canSenseLocation(t) || !rc.sensePassability(t) || rc.isLocationOccupied(t)) continue;
            bd = d; best = t;
        }
        if (best != null) { mode = 3; Nav.moveTo(best); return true; }
        if (d0 > 36) { mode = 3; Nav.moveTo(h); return true; }      // the ring is not in view yet: approach
        if (d0 < C.RING_MIN) { mode = 3; Nav.moveAway(h); return true; }
        return false;                                                 // the ring in view is full
    }

    static int islandAt;
    static int[] visited = new int[40];

    /** Hunters: the image (under the surviving symmetry) of an island tile in the shared slots that this launcher has not
     *  been near in the last 150 rounds. */
    static MapLocation predictedIsland() throws GameActionException {
        if (!MapMem.decided()) return null;
        int s = MapMem.cand == 1 || MapMem.cand == 2 || MapMem.cand == 4 ? MapMem.cand : (MapMem.cand & 1) != 0 ? 1 : (MapMem.cand & 2) != 0 ? 2 : 4;
        int n = Math.min(35, G.rc.getIslandCount());
        MapLocation best = null;
        int bd = Integer.MAX_VALUE, bid = 0;
        for (int id = 1; id <= n; id++) {
            if (Clock.getBytecodesLeft() < 3000) break;
            if (visited[id] > 0 && G.round - visited[id] < 150) continue;
            MapLocation t = Comms.islandTile(id);
            if (t == null) continue;
            MapLocation p = MapMem.img(s, t);
            int d = G.here.distanceSquaredTo(p);
            if (d <= 13) { visited[id] = G.round; continue; }
            if (d < bd) { bd = d; best = p; bid = id; }
        }
        return best;
    }

    /** The nearest island an enemy anchor holds, by this robot's sightings (fresher than 100 rounds) or the shared
     *  slots; sets islandAt. */
    static MapLocation enemyIsland() throws GameActionException {
        int n = Math.min(35, G.rc.getIslandCount());
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        islandAt = 0;
        for (int id = 1; id <= n; id++) {
            int owner;
            MapLocation t;
            if (MapMem.islandSeen[id] > 0 && G.round - MapMem.islandSeen[id] <= 100) { owner = MapMem.islandOwner[id]; t = MapMem.islandTile[id]; }
            else { owner = Comms.islandOwner(id); t = Comms.islandTile(id); }
            if (owner != 2 || t == null) continue;
            int d = G.here.distanceSquaredTo(t);
            if (d < bd) { bd = d; best = t; islandAt = id; }
        }
        return best;
    }

    static void march() throws GameActionException {
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
        MapLocation[] ehq = MapMem.enemyHQs();
        // never walk into enemy HQ fire unless there is something to fight there
        for (int i = ehq.length; --i >= 0; ) {
            if (objective.equals(ehq[i]) && G.here.distanceSquaredTo(ehq[i]) <= 16) return;
        }
        mode = 3;
        Nav.moveTo(objective);
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
        if (n < C.GROUP_MIN) {
            MapLocation home = HQState.nearest(G.here);
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
        if (leader.ID < G.id && G.here.distanceSquaredTo(leader.location) > C.FOLLOW_R2) {
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
        MapLocation e = Comms.nearestEnemy(G.here, 2);
        if (e != null) { objKind = 0; return e; }
        int n = Math.min(35, G.rc.getIslandCount());
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int id = 1; id <= n; id++) {
            // our own fresh sighting beats the shared slot (audit ISL-2: launchers stood on an island that had
            // decayed to neutral because the slot still said enemy and nobody near could rewrite it)
            int owner = MapMem.islandSeen[id] > 0 && G.round - MapMem.islandSeen[id] <= 10 ? MapMem.islandOwner[id] : Comms.islandOwner(id);
            if (owner != 2) continue;
            MapLocation t = Comms.islandTile(id);
            if (t == null) continue;
            int d = G.here.distanceSquaredTo(t);
            if (d < bd) { bd = d; best = t; objIsland = id; }
        }
        if (best != null) { objKind = 1; return best; }
        MapLocation[] ehq = MapMem.enemyHQs();
        if (ehq.length > 0) { objKind = 2; return G.nearest(G.here, ehq); }
        objKind = 3;
        return new MapLocation(G.W / 2, G.H / 2);
    }
}
