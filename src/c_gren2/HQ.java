package c_gren2;

import battlecode.common.*;

/**
 * Headquarters: registers itself, maps its vision (wells, islands, symmetry evidence), reports threats, and spends.
 * Action cooldown 2 against a decrement of 10: up to 5 builds/anchors per turn (RULES). Resources are per HQ.
 * Spending order each action: anchor (when wanted and affordable) > launcher > carrier (under the cap) > amplifier.
 * Never float: every action that can be afforded is taken, except what an anchor in preparation reserves.
 * c_gren1 (C.GREN): a threatened HQ with C.GREN_AD_MIN Ad builds grenadier carriers (Carrier.grenTurn) on the free
 * adjacent tile nearest the nearest enemy fighter, while fewer than C.GREN_MAX of its grenadiers are in its vision
 * (grenRoom), and marks the round for the newborns (Comms.setGrenMark).
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
        // c_well6: HQ 0 cools the hot wells (hqIdx is set by swarmEconomy)
        if (C.HOT && hqIdx == 0 && G.round % C.HOT_DECAY == 0) Comms.decayHot();
        // c_def2: raid alarm (hqIdx is set by swarmEconomy): our-half launchers rally here while it reads C.RAID_ALARM+
        if (C.RECALL) Comms.setAlarm(hqIdx, G.nEnemyFighters > G.nAllyFighters ? G.nEnemyFighters : 0);
        build();
        // c_mid1: HQ 0 chooses and publishes the contested mana well (Mid), after the build loop (which needs 7,000)
        if (C.MID && hqIdx == 0 && G.round % C.MID_EVERY == 0 && Clock.getBytecodesLeft() > C.MID_HQ_LEFT) Mid.update();
        if (rc.getResourceAmount(ResourceType.MANA) >= 200 || rc.getResourceAmount(ResourceType.ADAMANTIUM) >= 200) floatRounds++;
        G.note = "C" + carriersBuilt + "L" + launchersBuilt + "A" + ampsBuilt + "K" + anchorsBuilt;
        if (C.GREN && grenBuilt > 0) G.note += "G" + grenBuilt;
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
        // c_gren1: the mark of last round's grenadier builds, written before they first act (they act after every older
        // robot: RULES 4); not ALARM, which this round's view rewrites (last round's launchers count in it)
        if (C.GREN) { grenThisTurn = 0; grenNear = -1; Comms.setGrenMark(hqIdx, grenMarked(grenRound, G.round)); }
        // c_anc3: whether an anchor may be built at all, once per turn (one pass over the island slots, ~350 bytecodes):
        // before C.ANCHOR_GATE_UNTIL only while no HQ of ours is pressed and they hold no more islands than we do; then
        // for a located neutral island, or for an unlocated one from C.ANCHOR_BLIND_FROM at most once per
        // C.ANCHOR_BLIND_PERIOD rounds (replaces islandToTake: any unreported island let the HQs build anchors that
        // couriers carried with no target and lost)
        Comms.islandStats(rc.getIslandCount());
        boolean gate = G.round >= C.ANCHOR_GATE_UNTIL || (!Comms.anyPressed() && Comms.islThem <= Comms.islUs);
        boolean anchorAllowed = gate && (Comms.islLocNeutral > 0 || (Comms.islUnloc > 0 && G.round >= C.ANCHOR_BLIND_FROM
            && G.round - lastAnchorRound >= C.ANCHOR_BLIND_PERIOD));
        int guard;
        for (guard = 0; guard < 6 && rc.isActionReady() && Clock.getBytecodesLeft() > 7000; guard++) {
            int ad = rc.getResourceAmount(ResourceType.ADAMANTIUM), mn = rc.getResourceAmount(ResourceType.MANA);
            boolean wantAnchor = !threatened && G.round >= C.ANCHOR_START && launchersBuilt >= C.ANCHOR_MIN_LAUNCHERS
                && rc.getNumAnchors(Anchor.STANDARD) == 0 && G.round - lastAnchorRound >= C.ANCHOR_PERIOD && anchorAllowed;
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
            // c_gren1: banked Ad at a besieged HQ becomes grenadiers (the carrier line above never builds under threat)
            if (C.GREN && threatened && ad - resAd >= C.GREN_AD_MIN && grenRoom() && buildGren()) { grenBuilt++; grenThisTurn++; continue; }
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
        // c_anc3: pressure = enemy fighters in this HQ's vision (r2 34, hq.csv pressure34) summed per C.PRESS_BUCKET
        // rounds; pressed while the previous or the current bucket reaches C.PRESS_SUM
        int b = G.round / C.PRESS_BUCKET;
        if (b != pressBucket) {
            pressPrev = pressBucket == b - 1 ? pressAcc : 0;
            pressAcc = 0;
            pressBucket = b;
        }
        pressAcc += G.nEnemyFighters;
        Comms.setPressed(hqIdx, pressPrev >= C.PRESS_SUM || pressAcc >= C.PRESS_SUM);
    }

    /** c_anc3: enemy fighter-rounds in vision in the current and the previous C.PRESS_BUCKET-round bucket. */
    static int pressAcc, pressPrev, pressBucket = -1;

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

    // ---------------------------------------------------------------- c_gren1: grenadiers (C.GREN)
    /** Grenadiers built (indicator "G<n>"), this turn; those built earlier still in vision (-1: not counted yet this
     *  turn, set by build()); the round of the last grenadier build (0: none); the IDs of the grenadiers built and in
     *  vision at the last count, then this turn's (grenIds[0..nGren), at most C.GREN_MAX). No static initializer, so
     *  C.GREN false leaves HQ.<clinit> as c_di1's. */
    static int grenBuilt, grenThisTurn, grenNear, grenRound, nGren;
    static int[] grenIds;

    /** Pure: the grenadier mark at round `round` for the last grenadier build at round `built` (0: none): built last round. */
    static boolean grenMarked(int built, int round) { return built > 0 && built == round - 1; }

    /** c_gren1: room for another grenadier: the grenadiers this HQ built still in its vision (grenLive, once a turn)
     *  plus this turn's builds stay under C.GREN_MAX (the ones out on the leash, r2 9-20, count; ordinary carriers do not). */
    static boolean grenRoom() {
        if (grenNear < 0) grenNear = grenLive();
        return grenNear + grenThisTurn < C.GREN_MAX;
    }

    /** c_gren1: keep in grenIds only the grenadiers this HQ can still sense (canSenseRobot, at most C.GREN_MAX calls;
     *  the dead and the departed drop out) and count them. */
    static int grenLive() {
        int[] a = grenIds;
        int n = 0;
        if (a != null) for (int i = 0; i < nGren; i++) if (G.rc.canSenseRobot(a[i])) a[n++] = a[i];
        nGren = n;
        return n;
    }

    /** c_gren1: record a grenadier just built at t (its ID, for grenLive) and the round (grenMarked). */
    static void grenAdd(MapLocation t) throws GameActionException {
        grenRound = G.round;
        if (!G.rc.canSenseLocation(t)) return;
        RobotInfo r = G.rc.senseRobotAtLocation(t);
        if (r == null) return;
        if (grenIds == null) grenIds = new int[C.GREN_MAX];
        if (nGren < grenIds.length) grenIds[nGren++] = r.ID;
    }

    /** c_gren1: build a carrier on the free adjacent tile (r2 <= 2: the grenadier can withdraw at once) nearest the
     *  nearest enemy launcher or destabilizer in vision (ties: lowest G.DIRS index); false if no adjacent tile is
     *  buildable (8 canBuildRobot calls, about 200 bytecodes, and one pass over G.enemies). */
    static boolean buildGren() throws GameActionException {
        RobotController rc = G.rc;
        MapLocation e = nearestFighter(G.enemies, G.here);
        if (e == null) return false;
        boolean[] ok = new boolean[8];
        for (int i = 8; --i >= 0; ) ok[i] = rc.canBuildRobot(RobotType.CARRIER, G.here.add(G.DIRS[i]));
        int k = grenTile(G.here, ok, e);
        if (k < 0) return false;
        rc.buildRobot(RobotType.CARRIER, G.here.add(G.DIRS[k]));
        grenAdd(G.here.add(G.DIRS[k]));
        return true;
    }

    /** Pure: the G.DIRS index of the buildable neighbour of hq (ok[i]) nearest e, the lowest index on a tie; -1 if none. */
    static int grenTile(MapLocation hq, boolean[] ok, MapLocation e) {
        int best = -1, bd = Integer.MAX_VALUE;
        for (int i = 0; i < 8; i++) {
            if (!ok[i]) continue;
            int d = hq.add(G.DIRS[i]).distanceSquaredTo(e);
            if (d < bd) { bd = d; best = i; }
        }
        return best;
    }

    /** Pure: the location of the enemy launcher or destabilizer in es nearest `from` (the first in es on a tie, no RNG);
     *  null if none. */
    static MapLocation nearestFighter(RobotInfo[] es, MapLocation from) {
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        if (es != null) for (int i = 0; i < es.length; i++) {
            RobotInfo r = es[i];
            if (r.type != RobotType.LAUNCHER && r.type != RobotType.DESTABILIZER) continue;
            int d = from.distanceSquaredTo(r.location);
            if (d < bd) { bd = d; best = r.location; }
        }
        return best;
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
