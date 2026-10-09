package arch_blob;

import battlecode.common.*;

/**
 * Headquarters: registers itself, maps its vision (wells, islands, symmetry evidence), reports threats, and spends.
 * Action cooldown 2 against a decrement of 10: up to 5 builds/anchors per turn (RULES). Resources are per HQ.
 * Spending order each action: anchor (when wanted and affordable) > launcher > carrier (under the cap) > amplifier.
 * Never float: every action that can be afforded is taken, except what an anchor in preparation reserves.
 */
public final class HQ {
    static int carriersBuilt, launchersBuilt, ampsBuilt, anchorsBuilt;
    static int lastAnchorRound = -1000;
    static MapLocation[] spawnTiles;
    public static int floatRounds;      // rounds ending with >= 200 of a resource unspent (diagnostic)
    // telemetry only (never read by decisions): why build() stopped (Telemetry.hqReason; 0 '.', 1 'b', 2 'g' are loop
    // exits), the last iteration's wantAnchor, whether a tryBuild found no tile this iteration, wells counted by carrierRoom
    static int reason;
    static boolean lastWant, tileFail;
    static int lastWells;

    static void run() throws GameActionException {
        RobotController rc = G.rc;
        if (spawnTiles == null) {
            Comms.registerHQ(G.here);
            spawnTiles = rc.getAllLocationsWithinRadiusSquared(G.here, 9);
        }
        MapMem.scan();
        if (G.round % 8 == 1) MapMem.scanIslands();
        MapMem.syncSym();
        if (G.nEnemyFighters > 0) {
            for (int i = G.enemies.length; --i >= 0; ) {
                RobotInfo e = G.enemies[i];
                if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) { Comms.reportEnemy(e.location); break; }
            }
        }
        Comms.expireEnemies();
        // arch_blob: under pressure (2+ enemy fighters in vision and more than our launchers here) call the army home
        if (G.nEnemyFighters >= C.HELP_MIN && G.nEnemyFighters > G.nAllyFighters) Comms.callHelp(G.here);
        else if (G.nEnemyFighters == 0) Comms.clearHelp(G.here);
        build();
        if (rc.getResourceAmount(ResourceType.MANA) >= 200 || rc.getResourceAmount(ResourceType.ADAMANTIUM) >= 200) floatRounds++;
        G.note = "C" + carriersBuilt + "L" + launchersBuilt + "A" + ampsBuilt + "K" + anchorsBuilt;
        Telemetry.code = Telemetry.hqCode(reason, G.nEnemyFighters > 0, lastWant);
    }

    /**
     * arch_blob production: a launcher whenever Mn >= 45 (on r1 that is 4 launchers, then a carrier: the member's LLLLC),
     * then a carrier whenever Ad >= 50 under the per-HQ cap; no amplifiers, destabilizers or boosters. From C.SAVE_FROM
     * nothing but anchors (from C.ANCHOR_START, one per C.ANCHOR_PERIOD, while an island can be taken without conquest).
     */
    static void build() throws GameActionException {
        RobotController rc = G.rc;
        boolean threatened = C.HQ_THREAT == 0 ? G.nEnemyFighters > 0 : inDanger();
        boolean save = G.round >= C.SAVE_FROM;
        reason = -1;
        lastWant = false;
        int guard;
        for (guard = 0; guard < 6 && rc.isActionReady() && Clock.getBytecodesLeft() > 7000; guard++) {
            int ad = rc.getResourceAmount(ResourceType.ADAMANTIUM), mn = rc.getResourceAmount(ResourceType.MANA);
            boolean wantAnchor = !threatened && G.round >= C.ANCHOR_START && launchersBuilt >= C.ANCHOR_MIN_LAUNCHERS
                && rc.getNumAnchors(Anchor.STANDARD) == 0 && G.round - lastAnchorRound >= C.ANCHOR_PERIOD && islandToTake()
                && anchorRoom();
            lastWant = wantAnchor;
            tileFail = false;
            if (wantAnchor && ad >= 80 && mn >= 80 && rc.canBuildAnchor(Anchor.STANDARD)) {
                rc.buildAnchor(Anchor.STANDARD);
                anchorsBuilt++;
                lastAnchorRound = G.round;
                continue;
            }
            boolean room = !save && carrierRoom();
            if (!save && mn >= 45 && tryBuild(RobotType.LAUNCHER)) { launchersBuilt++; continue; }
            if (!save && !threatened && ad >= 50 && room && tryBuild(RobotType.CARRIER)) { carriersBuilt++; continue; }
            reason = Telemetry.hqReason(tileFail, wantAnchor, true, threatened, room, ad, mn, 0, 0);
            break;
        }
        if (reason < 0) reason = guard >= 6 ? 2 : !rc.isActionReady() ? 0 : 1;
    }

    /** arch_blob: carriers built by this HQ stay under C.CARRIER_CAP0 + round / C.CARRIER_CAP_ROUNDS. */
    static boolean carrierRoom() throws GameActionException {
        if (carriersBuilt >= C.CARRIER_CAP0 + G.round / C.CARRIER_CAP_ROUNDS) return false;
        int wells = 0;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) { if (Comms.read(i) == 0) break; wells++; }
        if (C.TELEMETRY) lastWells = wells;
        int nHQ = HQState.ourHQs == null || HQState.ourHQs.length == 0 ? 1 : HQState.ourHQs.length;
        if (carriersBuilt >= Math.max(C.CARRIER_CAP0, C.CARRIERS_PER_WELL * wells / nHQ + 2) + G.round / C.CARRIER_REPLACE_ROUNDS) return false;
        int crowd = 0;
        for (int i = G.nearby.length; --i >= 0; ) {
            RobotInfo r = G.nearby[i];
            if (r.team == G.us && r.type == RobotType.CARRIER && ++crowd >= C.CARRIER_CROWD) return false;
        }
        return true;
    }

    /** arch_blob (C.NO_CONQUEST): another anchor only while we hold fewer islands (shared slots) than one short of the
     *  conquest threshold (75% of the islands). */
    static boolean anchorRoom() throws GameActionException {
        if (!C.NO_CONQUEST) return true;
        int n = G.rc.getIslandCount(), owned = 0;
        for (int id = 1; id <= n && id <= 35; id++) if (Comms.islandOwner(id) == 1) owned++;
        return owned < conquestLimit(n);
    }

    /** The most islands a team may hold without winning by conquest: one less than ceil(0.75 n). */
    static int conquestLimit(int n) { return (3 * n + 3) / 4 - 1; }

    /** True if some island is not ours (or islands exist that nobody has reported yet). */
    static boolean islandToTake() throws GameActionException {
        int n = G.rc.getIslandCount();
        // only islands an anchor can go on: neutral or not yet reported (audit R6: enemy-held islands counted, so
        // HQs kept building anchors no carrier could place; launchers neutralise those first)
        // arch_blob: any island not ours (the shared slots keep "enemy" for islands our launchers neutralised far from
        // a writer; v3 Hah and Cornucopia built no anchor at all)
        for (int id = 1; id <= n && id <= 35; id++) if (Comms.islandOwner(id) != 1) return true;
        return false;
    }

    /** Build on the free spawn tile nearest the unit's purpose: carriers toward wells, others toward the enemy. */
    /**
     * C.HQ_THREAT = 1: the HQ is threatened only under real danger: an enemy fighter within r2 C.HQ_DANGER_R2 of the
     * HQ, and enemy fighters in vision outnumber our launchers in vision. Replica panel telemetry (100 games, c_line4):
     * the build loop withheld an affordable carrier "under threat" in 43% of HQ turns, with enemies merely in vision
     * (r2 34); opponents under the same pressure left funds idle half as often (idle HQ-rounds ~750 vs our ~1,650).
     */
    static boolean inDanger() {
        if (G.nEnemyFighters == 0 || G.nEnemyFighters <= G.nAllyFighters) return false;
        for (int i = G.enemies.length; --i >= 0; ) {
            RobotInfo e = G.enemies[i];
            if ((e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER)
                && G.here.distanceSquaredTo(e.location) <= C.HQ_DANGER_R2) return true;
        }
        return false;
    }

    static int[] threatCache, fx, fy;
    static int threatRound = -1, nf;

    /**
     * A newborn cannot act until next round, but enemies that move after us this round can shoot it: spawn on the tile
     * the fewest visible enemy fighters can reach (r2 26), then nearest the unit's purpose (C.SPAWN_SAFETY).
     * Lazy and cached per turn: only tiles where a build is possible are scored (under a siege most spawn tiles are
     * occupied). Scoring every tile cost ~21 bytecodes per tile and fighter, 15,000 with 24 fighters in view, and left
     * the build loop no bytecodes to build at all (profiled in a self-play siege, DefaultMap r571-586).
     */
    static int tileThreat(int i) {
        if (!C.SPAWN_SAFETY || G.nEnemyFighters == 0) return 0;
        if (threatRound != G.round) {
            threatRound = G.round;
            if (threatCache == null) threatCache = new int[spawnTiles.length];
            java.util.Arrays.fill(threatCache, -1);
            fx = new int[G.nEnemyFighters]; fy = new int[G.nEnemyFighters]; nf = 0;
            for (int k = G.enemies.length; --k >= 0 && nf < fx.length; ) {
                RobotInfo e = G.enemies[k];
                if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) { fx[nf] = e.location.x; fy[nf++] = e.location.y; }
            }
        }
        int c = threatCache[i];
        if (c >= 0) return c;
        if (Clock.getBytecodesLeft() < 4000 + nf * 25) return 0;   // no room to score: treat as safe
        int x = spawnTiles[i].x, y = spawnTiles[i].y;
        c = 0;
        for (int k = nf; --k >= 0; ) { int dx = x - fx[k], dy = y - fy[k]; if (dx * dx + dy * dy <= C.THREAT_R2) c++; }
        threatCache[i] = c;
        return c;
    }

    static boolean tryBuild(RobotType t) throws GameActionException {
        RobotController rc = G.rc;
        MapLocation goal;
        if (t == RobotType.CARRIER) {
            goal = Comms.nearestWell(G.here, 0);
        } else {
            MapLocation[] e = MapMem.enemyHQs();
            goal = e.length > 0 ? G.nearest(G.here, e) : new MapLocation(G.W / 2, G.H / 2);
        }
        if (goal == null) goal = new MapLocation(G.W / 2, G.H / 2);
        MapLocation best = null;
        long bd = Long.MAX_VALUE;
        for (int i = spawnTiles.length; --i >= 0; ) {
            if (Clock.getBytecodesLeft() < 3500) break;       // keep the turn: the best tile so far, or none
            MapLocation l = spawnTiles[i];
            if (!rc.canBuildRobot(t, l)) continue;
            long d = tileThreat(i) * 100_000L + l.distanceSquaredTo(goal);
            if (d < bd) { bd = d; best = l; }
        }
        if (best == null) { tileFail = true; return false; }
        rc.buildRobot(t, best);
        return true;
    }
}
