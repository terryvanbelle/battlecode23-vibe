package arch_adecon;

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
                if (p > bp || (p == bp && e.health < bh)) { bp = p; bh = e.health; best = e; }
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
                if (C.AE_BRAVE && ready) {
                    // arch_adecon: step in to fire whatever the count, at the edge of range, threats only a tiebreak
                    s = (hit ? 1_000_000L : 0) + Math.min(minD, 100) * 100 - threat * 10L; if (hit) anyCanHit = true;
                }
                else if (ready && !outnumbered) { s = (hit ? 1_000_000L : 0) - threat * 10_000L + Math.min(minD, 100) * 10; if (hit) anyCanHit = true; }
                else if (C.AE_BRAVE) s = (d == Direction.CENTER ? 15_000L : 0) - threat * 10_000L + Math.min(minD, 100) * 10;   // hold unless 2+ fewer threats
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

    /**
     * arch_adecon, before C.AE_MIDFIELD_FROM: keep to our own half. A fresh enemy sighting on our side, else an
     * enemy-held island on our side (neutralise it by standing on it), else this launcher's post: one of our anchored
     * islands (stand on it: garrison) and the guard point C.AE_GUARD_PCT% (C.AE_EARLY_GUARD_PCT% before
     * C.AE_FORWARD_FROM) of the way from our nearest HQ toward the nearest predicted enemy HQ, drawn at random every
     * C.AE_POST_ROUNDS rounds; the guard point is scattered by up to
     * C.AE_POST_SCATTER tiles so the launchers do not stack (members' group size p50 3-4, alone20 0.07-0.36).
     * objKind: 0 sighting, 1 island, 3 post.
     */
    static MapLocation pickHomeObjective() throws GameActionException {
        objIsland = 0;
        MapLocation[] ehq = MapMem.enemyHQs();
        int stamp = (G.round >> 4) & 15;
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = Comms.ENEMY; i < Comms.ENEMY + Comms.NENEMY; i++) {
            int c = Comms.read(i);
            if (c == 0 || ((stamp - (c >>> 12)) & 15) > 2) continue;
            MapLocation l = G.dec(c & 0xfff);
            if (!ownHalf(l, ehq)) continue;
            int d = G.here.distanceSquaredTo(l);
            if (d < bd) { bd = d; best = l; }
        }
        if (best != null) { objKind = 0; return best; }
        int n = Math.min(35, G.rc.getIslandCount());
        for (int id = 1; id <= n; id++) {
            int owner = MapMem.islandSeen[id] > 0 && G.round - MapMem.islandSeen[id] <= 10 ? MapMem.islandOwner[id] : Comms.islandOwner(id);
            if (owner != 2) continue;
            MapLocation t = Comms.islandTile(id);
            if (t == null || !ownHalf(t, ehq)) continue;
            int d = G.here.distanceSquaredTo(t);
            if (d < bd) { bd = d; best = t; objIsland = id; }
        }
        if (best != null) { objKind = 1; return best; }
        if (post == null || G.round >= postUntil) pickPost(ehq, n);
        objIsland = postIsland;
        objKind = postIsland > 0 ? 1 : 3;
        return post;
    }

    static MapLocation post;
    static int postIsland, postUntil;

    /** Draw a post uniformly (reservoir sampling, bytecode-guarded) among our anchored islands and the guard point. */
    static void pickPost(MapLocation[] ehq, int nIslands) throws GameActionException {
        MapLocation home = HQState.nearest(G.here);
        if (home == null) { post = new MapLocation(G.W / 2, G.H / 2); postIsland = 0; postUntil = G.round + 10; return; }
        MapLocation e = ehq.length > 0 ? G.nearest(home, ehq) : new MapLocation(G.W / 2, G.H / 2);
        int pct = G.round < C.AE_FORWARD_FROM ? C.AE_EARLY_GUARD_PCT : C.AE_GUARD_PCT;
        post = new MapLocation(home.x + (e.x - home.x) * pct / 100, home.y + (e.y - home.y) * pct / 100);
        postIsland = 0;
        postUntil = G.round < C.AE_FORWARD_FROM ? Math.min(G.round + C.AE_POST_ROUNDS, C.AE_FORWARD_FROM) : G.round + C.AE_POST_ROUNDS;
        int k = 1;
        for (int id = 1; id <= nIslands; id++) {
            if (Clock.getBytecodesLeft() < 3000) break;
            if (Comms.islandOwner(id) != 1) continue;
            MapLocation t = Comms.islandTile(id);
            if (t == null) continue;
            if (G.rand(++k) == 0) { post = t; postIsland = id; }
        }
        // scatter: a random tile within C.AE_POST_SCATTER (Chebyshev) of the drawn post, unless it is an island to hold
        if (postIsland == 0 && C.AE_POST_SCATTER > 0) {
            int r = C.AE_POST_SCATTER, x = post.x + G.rand(2 * r + 1) - r, y = post.y + G.rand(2 * r + 1) - r;
            MapLocation p = new MapLocation(Math.max(0, Math.min(G.W - 1, x)), Math.max(0, Math.min(G.H - 1, y)));
            if (ownHalf(p, ehq)) post = p;
        }
    }

    /** A location nearer our nearest HQ than the nearest predicted enemy HQ (prog >= 0.5 in the opponent's frame). */
    static boolean ownHalf(MapLocation t, MapLocation[] ehq) {
        MapLocation mine = HQState.nearest(t);
        if (mine == null || ehq.length == 0) return true;
        MapLocation theirs = G.nearest(t, ehq);
        return t.distanceSquaredTo(mine) <= t.distanceSquaredTo(theirs);
    }

    static MapLocation pickObjective() throws GameActionException {
        if (G.round < C.AE_MIDFIELD_FROM) return pickHomeObjective();
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
