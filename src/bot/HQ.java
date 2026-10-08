package bot;

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
        build();
        if (rc.getResourceAmount(ResourceType.MANA) >= 200 || rc.getResourceAmount(ResourceType.ADAMANTIUM) >= 200) floatRounds++;
        G.note = "C" + carriersBuilt + "L" + launchersBuilt + "A" + ampsBuilt + "K" + anchorsBuilt;
        Telemetry.code = Telemetry.hqCode(reason, G.nEnemyFighters > 0, lastWant);
    }

    static void build() throws GameActionException {
        RobotController rc = G.rc;
        boolean threatened = G.nEnemyFighters > 0;
        // launchers leave in batches built in the same turn (they share cooldowns, so they travel and arrive together:
        // diag-top4 showed our launchers fighting one at a time); a threatened HQ builds whatever it can
        int mnStart = rc.getResourceAmount(ResourceType.MANA);
        boolean batchOK = threatened || G.round <= 2 || mnStart >= 45 * C.LAUNCHER_BATCH;
        reason = -1;
        lastWant = false;
        int guard;
        for (guard = 0; guard < 6 && rc.isActionReady() && Clock.getBytecodesLeft() > 7000; guard++) {
            int ad = rc.getResourceAmount(ResourceType.ADAMANTIUM), mn = rc.getResourceAmount(ResourceType.MANA);
            boolean wantAnchor = !threatened && G.round >= C.ANCHOR_START && launchersBuilt >= C.ANCHOR_MIN_LAUNCHERS
                && rc.getNumAnchors(Anchor.STANDARD) == 0 && G.round - lastAnchorRound >= C.ANCHOR_PERIOD && islandToTake();
            lastWant = wantAnchor;
            tileFail = false;
            if (wantAnchor && ad >= 80 && mn >= 80 && rc.canBuildAnchor(Anchor.STANDARD)) {
                rc.buildAnchor(Anchor.STANDARD);
                anchorsBuilt++;
                lastAnchorRound = G.round;
                continue;
            }
            int resAd = wantAnchor ? 80 : 0, resMn = wantAnchor ? 80 : 0;
            boolean room = carrierRoom();
            boolean carrierFirst = !threatened && carriersBuilt <= launchersBuilt && room;
            if (carrierFirst && ad - resAd >= 50 && tryBuild(RobotType.CARRIER)) { carriersBuilt++; continue; }
            if (batchOK && mn - resMn >= 45 && tryBuild(RobotType.LAUNCHER)) { launchersBuilt++; continue; }
            if (!threatened && ad - resAd >= 50 && room && tryBuild(RobotType.CARRIER)) { carriersBuilt++; continue; }
            if (!threatened && launchersBuilt >= C.LAUNCHERS_PER_AMP * (ampsBuilt + 1) && ad - resAd >= 30 && mn - resMn >= 15
                && tryBuild(RobotType.AMPLIFIER)) { ampsBuilt++; continue; }
            reason = Telemetry.hqReason(tileFail, wantAnchor, batchOK, threatened, room, ad, mn, resAd, resMn);
            break;
        }
        if (reason < 0) reason = guard >= 6 ? 2 : !rc.isActionReady() ? 0 : 1;
    }

    /**
     * Whether another carrier may be built. The old cap counted carriers EVER built by this HQ (not a census), so in
     * losses, where 19 of 21 carriers died, it read full and nothing was replaced, while 1,000-1,900 Ad floated
     * (calib-g_iter0 census; awesomelemonade.finalBot on ReverseFunnel). Now the bound is on our LIVE robots
     * (getRobotCount is exact) and scales with the wells we know: about C.ROBOTS_PER_WELL robots per known well.
     */
    static boolean carrierRoom() throws GameActionException {
        int wells = 0;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) { if (Comms.read(i) == 0) break; wells++; }
        if (C.TELEMETRY) lastWells = wells;
        return G.rc.getRobotCount() < C.ROBOTS_BASE + C.ROBOTS_PER_WELL * Math.max(1, wells);
    }

    /** True if some island is not ours (or islands exist that nobody has reported yet). */
    static boolean islandToTake() throws GameActionException {
        int n = G.rc.getIslandCount();
        // only islands an anchor can go on: neutral or not yet reported (audit R6: enemy-held islands counted, so
        // HQs kept building anchors no carrier could place; launchers neutralise those first)
        for (int id = 1; id <= n && id <= 35; id++) if (Comms.islandOwner(id) == 0) return true;
        return false;
    }

    /** Build on the free spawn tile nearest the unit's purpose: carriers toward wells, others toward the enemy. */
    static int[] threatCache;
    static int threatRound = -1;

    /**
     * A newborn cannot act until next round, but enemies that move after us this round can shoot it: spawn on the tile
     * the fewest visible enemy fighters can reach (r2 26), then nearest the unit's purpose (C.SPAWN_SAFETY). Computed
     * once per turn (c_audit1 recomputed it for every build: 29 tiles x enemies x up to 6 builds pushed sieged HQs past
     * their 20,000 bytecodes, 111 overruns in 10 of 174 calibration games).
     */
    static int[] spawnThreat() {
        if (threatRound == G.round && threatCache != null) return threatCache;
        int n = spawnTiles.length;
        int[] th = new int[n];
        // under a heavy siege (20+ fighters in view) the scoring costs ~29 x F x 12 bytecodes: skip it rather than
        // overrun (c_line4 trial: HQ overruns only in sieges, 1-37 a game)
        if (C.SPAWN_SAFETY && G.nEnemyFighters > 0 && Clock.getBytecodesLeft() > 8000 + n * G.nEnemyFighters * 14) {
            int f = 0;
            int[] fx = new int[G.nEnemyFighters], fy = new int[G.nEnemyFighters];
            for (int k = G.enemies.length; --k >= 0 && f < fx.length; ) {
                RobotInfo e = G.enemies[k];
                if (e.type == RobotType.LAUNCHER || e.type == RobotType.DESTABILIZER) { fx[f] = e.location.x; fy[f++] = e.location.y; }
            }
            for (int i = n; --i >= 0; ) {
                int x = spawnTiles[i].x, y = spawnTiles[i].y, c = 0;
                for (int k = f; --k >= 0; ) { int dx = x - fx[k], dy = y - fy[k]; if (dx * dx + dy * dy <= C.THREAT_R2) c++; }
                th[i] = c;
            }
        }
        threatCache = th;
        threatRound = G.round;
        return th;
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
        int[] threat = spawnThreat();
        for (int i = spawnTiles.length; --i >= 0; ) {
            if (Clock.getBytecodesLeft() < 3500) break;       // keep the turn: the best tile so far, or none
            MapLocation l = spawnTiles[i];
            if (!rc.canBuildRobot(t, l)) continue;
            long d = threat[i] * 100_000L + l.distanceSquaredTo(goal);
            if (d < bd) { bd = d; best = l; }
        }
        if (best == null) { tileFail = true; return false; }
        rc.buildRobot(t, best);
        return true;
    }
}
