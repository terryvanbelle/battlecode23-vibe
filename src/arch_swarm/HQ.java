package arch_swarm;

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
        swarmEconomy();
        build();
        if (rc.getResourceAmount(ResourceType.MANA) >= 200 || rc.getResourceAmount(ResourceType.ADAMANTIUM) >= 200) floatRounds++;
        G.note = "C" + carriersBuilt + "L" + launchersBuilt + "A" + ampsBuilt + "K" + anchorsBuilt;
        Telemetry.code = Telemetry.hqCode(reason, G.nEnemyFighters > 0, lastWant);
    }

    static void build() throws GameActionException {
        RobotController rc = G.rc;
        boolean threatened = C.HQ_THREAT == 0 ? G.nEnemyFighters > 0 : inDanger();
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
            // arch_swarm: a launcher whenever Mn >= 45, then a carrier whenever Ad >= 50 under the cap; no amplifiers
            // (round 1: 4 launchers then 1 carrier, as every S1 member opens: first builds LLLL C)
            if (batchOK && mn - resMn >= 45 && tryBuild(RobotType.LAUNCHER)) { launchersBuilt++; continue; }
            if (!threatened && ad - resAd >= 50 && room && tryBuild(RobotType.CARRIER)) { carriersBuilt++; pendingCarriers++; continue; }
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
    static int liveCarriers, carrierCap, pendingCarriers;
    static int hqIdx = -2;

    /** arch_swarm: the live-carrier census (Comms.CENSUS), the team cap, and this HQ's "wants adamantium" flag. */
    static void swarmEconomy() throws GameActionException {
        if (hqIdx == -2) hqIdx = Comms.hqIndex(G.here);
        liveCarriers = Comms.liveCarriers(hqIdx == 0);
        pendingCarriers = 0;           // carriers built this turn: counted by the census from their first turn
        int nHQ = HQState.ourHQs == null ? 1 : Math.max(1, HQState.ourHQs.length);
        carrierCap = Math.min(C.CAP_MAX, Math.max((C.CAP_MIN_PER_HQ + G.round / C.CAP_GROW_ROUNDS) * nHQ, C.CAP_PER_MN_WELL * Comms.wellCount(2)));
        boolean want = G.rc.getResourceAmount(ResourceType.ADAMANTIUM) < C.AD_NEED && liveCarriers < carrierCap;
        Comms.setAdFlag(hqIdx, want);
    }

    static boolean carrierRoom() throws GameActionException {
        // arch_swarm: the team cap on LIVE carriers (census); carriers built this turn are not counted yet
        if (C.ROLES == 3) return liveCarriers + pendingCarriers < carrierCap;
        // early game: g_iter0's per-HQ cap on carriers built (4 + round/40), so adamantium banks for the anchor rush
        // (replica panel: g_iter0 banked 390-750 Ad at r150 and won 24 games by r400; the uncapped line banked 133
        // less at r250 and won 18); later, the live-robot bound (the built cap locked out replacements in losses)
        if (G.round < C.EARLY_CAP_UNTIL) return carriersBuilt < C.CARRIER_BASE + G.round / C.CARRIER_PER_ROUNDS;
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
