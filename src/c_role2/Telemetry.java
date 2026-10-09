package c_role2;

import battlecode.common.*;

/**
 * Telemetry (docs/TELEMETRY.md, part A): the per-turn 6-bit state code, the v2 indicator string, data dots and the
 * bytecode channel (BCC). Statics only: no per-turn allocation beyond the string, no G.rand() calls, no shared-array
 * writes, no writes to anything decision code reads. With C.TELEMETRY false the dots and the pad compile away; the
 * code and the v2 string stay.
 *
 * Channels: the replica runs with indicators off, so only bytecodesUsed reaches its replays. pad() makes this turn's
 * bytecodesUsed congruent to the code (mod 64), and to SYNC_CODE on rounds = 25 (mod 50) so a decoder can find the
 * offset. Dots carry the records of TELEMETRY.md A.6 at x = -2 - kind; the string carries the code as its 2nd char.
 *
 * Saturation: event fields that a count, round or id feeds are clamped to [0, 2^w - 1] (s8/s16/sat); loc12 values
 * (at most 3,836 on a 60 x 60 map) and enum fields set by our own code are masked to their width. The periodic
 * records (CNT, CNTT, CNTM, HQS) carry counters, stocks and rounds that are never negative, so they are clamped at the
 * top only, inline (Math.min costs 1 against ~9 for a helper call: TELEMETRY.md A.7 budgets CNT x 3 at 120). Booleans,
 * small enums, loc12 values and counts bounded by vision are bounded by construction and only shifted (FIGHT runs on
 * every fight turn).
 */
public final class Telemetry {
    // ---------------------------------------------------------------- shared constants (TELEMETRY.md section 1)
    public static final int MAGIC = 0x7E1E0001;
    public static final String ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_";
    public static final int SYNC_CODE = 42, BCC_GUARD = 300;
    /** Record kinds (A.6); COMMS chunk j is kind COMMS + j. */
    public static final int HDR = 0, EXC = 1, NM = 2, OVR = 3, CNT = 4, CNTT = 5, CNTM = 6, SYM = 7, ROLE = 8, WELL = 9,
        TRIP = 10, FLEE = 11, ANCH = 12, OBJ = 13, FIGHT = 14, HQS = 15, BUG = 16, COMMS = 24;
    /** Letters of the 64 codes per type, in the replay schema's body-type order (0 HQ, 1 C, 2 L, 3 A, 4 D, 5 B);
     *  '?' marks an invalid code (TELEMETRY.md 1.1). */
    static final String L_HQ = ".bgpwcastx?????!.bgpwcastx?????!.bgpwcastx?????!.bgpwcastx?????!";
    static final String L_CARRIER = "!!GGCCWWSSXXRRDDFFVVTTKKQQEEYYPP????????????????????????????????";
    static final String L_LAUNCHER = "NFHMSGW!NFHMSGW!NFHMSGW!NFHMSGW!NFHMSGW!NFHMSGW!NFHMSGW!NFHMSGW!";
    static final String L_AMPLIFIER = "FCSHFCSHFCSHFCSHFCSHFCSHFCSHFCSHFCSHFCSHFCSHFCSHFCSHFCSHFCSH???!";
    static final String L_OTHER = "O!??????????????????????????????????????????????????????????????";
    /** Carrier state letters by state number (state = code >> 1). */
    static final String CARRIER_STATES = "!GCWSXRDFVTKQEYP";

    // ---------------------------------------------------------------- per-robot state
    /** This turn's 6-bit code; phase 1 start, 2 unit code, 3 endTurn, 4 fill, 5 indicator; bytecodes after shared start. */
    public static int code, phase, t1;
    static int ttype, limit, excCode, reserve;
    static String letters = L_OTHER;
    static int ovPhase;                     // phase in which the round changed (0 = not seen yet)
    static int nextCnt, nextHqs = 25, commsHQ;   // commsHQ: 0 unknown, 1 yes, 2 no
    static int endCost, maxCost, errors, deferrals;
    // carrier: the current trip (since the last emptying deposit or spawn) and cumulative state counters
    static int tStart, tFirst, tLast, tWait, tExplore, tFlee, tCollect;
    static int waitTurns, exploreTurns, crowdSwitches;
    // launcher
    static int guardBreaks;
    /** Unit tests (G.rc == null): records land here as (x, a, b, c, d) quintuples in a ring. */
    static int[] TEST_SINK;
    static int sinkN;

    // ---------------------------------------------------------------- codes (TELEMETRY.md 1.1)
    static int typeNum(RobotType t) {
        if (t == RobotType.HEADQUARTERS) return 0;
        if (t == RobotType.CARRIER) return 1;
        if (t == RobotType.LAUNCHER) return 2;
        if (t == RobotType.AMPLIFIER) return 3;
        return t == RobotType.DESTABILIZER ? 4 : 5;
    }

    /** The 64 code letters of a type ('?' = invalid); the letter of code c is letters(type).charAt(c). */
    static String letters(int type) {
        switch (type) {
            case 0: return L_HQ;
            case 1: return L_CARRIER;
            case 2: return L_LAUNCHER;
            case 3: return L_AMPLIFIER;
            default: return L_OTHER;
        }
    }

    /** The '!' code of a type: exception, or a turn that ended before its code was set. */
    static int excCode(int type) {
        switch (type) {
            case 0: return 15;
            case 1: return 0;
            case 2: return 7;
            case 3: return 63;
            default: return 1;
        }
    }

    public static int carrierCode(int state, int role) { return (state & 15) << 1 | (role == 2 ? 1 : 0); }

    public static int launcherCode(int mode, int obj, boolean out) { return (mode & 7) | (obj & 3) << 3 | (out ? 32 : 0); }

    public static int hqCode(int reason, boolean threat, boolean wantAnchor) {
        return (reason & 15) | (threat ? 16 : 0) | (wantAnchor ? 32 : 0);
    }

    public static int ampCode(int mode, int n) { return (mode & 3) | (n < 0 ? 0 : n > 14 ? 14 : n) << 2; }

    /**
     * Why HQ.build() broke out of its loop (TELEMETRY.md A.4), from the values of the iteration that broke:
     * 7 s no spawn tile, 6 a anchor reserve, 4 w batch wait, 5 c carrier cap, 8 t threatened, 3 p poor, 9 x other.
     * (0 '.', 1 'b' and 2 'g' are loop-condition exits, decided by the caller.) Update with HQ.build().
     */
    public static int hqReason(boolean tileFail, boolean wantAnchor, boolean batchOK, boolean threatened, boolean room,
                               int ad, int mn, int resAd, int resMn) {
        if (tileFail) return 7;
        if (wantAnchor && ((batchOK && mn >= 45 && mn - 80 < 45) || (!threatened && room && ad >= 50 && ad - 80 < 50))) return 6;
        if (mn - resMn >= 45 && !batchOK) return 4;
        if (ad - resAd >= 50 && !threatened && !room) return 5;
        if ((ad - resAd >= 50 || (ad - resAd >= 30 && mn - resMn >= 15)) && threatened) return 8;
        if (mn - resMn < 45 && ad - resAd < 50) return 3;
        return 9;
    }

    // ---------------------------------------------------------------- helpers
    public static int loc12(MapLocation l) { return l == null ? 0 : l.x * 64 + l.y + 1; }

    /** Clamp to [0, 2^bits - 1]. */
    public static int sat(int v, int bits) { int m = (1 << bits) - 1; return v < 0 ? 0 : v > m ? m : v; }

    static int s8(int v) { return v < 0 ? 0 : v > 255 ? 255 : v; }

    static int s16(int v) { return v < 0 ? 0 : v > 65535 ? 65535 : v; }

    /** One data record: a dot at (-2 - kind, a) with colour (b, c, d). Without an engine (BotTest) it goes to TEST_SINK. */
    static void dot(int kind, int a, int b, int c, int d) {
        RobotController rc = G.rc;
        if (rc != null) { rc.setIndicatorDot(new MapLocation(-2 - kind, a), b, c, d); return; }
        if (TEST_SINK == null) TEST_SINK = new int[5 * 1024];
        int i = (sinkN % 1024) * 5;
        TEST_SINK[i] = -2 - kind; TEST_SINK[i + 1] = a; TEST_SINK[i + 2] = b; TEST_SINK[i + 3] = c; TEST_SINK[i + 4] = d;
        sinkN++;
    }

    // ---------------------------------------------------------------- turn loop (TELEMETRY.md A.2)
    static void init() {
        ttype = typeNum(G.type);
        limit = G.type.bytecodeLimit;
        reserve = limit * 12 / 100 + (ttype == 0 ? 1500 : 400);
        letters = letters(ttype);
        excCode = excCode(ttype);
        code = excCode;
        nextCnt = G.spawnRound + 1 + G.id % 50;
        tStart = G.spawnRound;
        if (C.TELEMETRY) emitHdr(ttype, G.spawnRound, loc12(G.rc.getLocation()), C.ROLES, C.MICRO ? 1 : 0, C.ARMY ? 1 : 0,
            C.SPAWN_SAFETY ? 1 : 0, C.LAUNCHER_BATCH, C.PADK, SYNC_CODE, C.TELE_BUILD);
    }

    static void startTurn() {
        phase = 1;
        code = excCode;
    }

    /** In each catch of the turn loop: an EXC record, and this turn's code becomes the type's '!' code. */
    static void exc(int site, Exception e, int r0) {
        if (C.TELEMETRY) {
            try {
                int gae = 0, cls = 15;
                if (e instanceof GameActionException) {
                    GameActionExceptionType t = ((GameActionException) e).getType();
                    gae = t == null ? 255 : t.ordinal() + 1;
                    cls = 0;
                } else if (e instanceof NullPointerException) cls = 1;
                else if (e instanceof ArrayIndexOutOfBoundsException) cls = 2;
                else if (e instanceof ArithmeticException) cls = 3;
                else if (e instanceof ClassCastException) cls = 4;
                else if (e instanceof NegativeArraySizeException) cls = 5;
                else if (e instanceof IllegalArgumentException) cls = 6;
                else if (e instanceof IllegalStateException) cls = 7;
                emitExc(site, gae, phase, code, r0, G.rc == null ? r0 : G.rc.getRoundNum(), cls);
            } catch (Exception x) { errors++; }
        }
        code = excCode;
    }

    static void nearMiss(int work, int r0) {
        try {
            emitNm(work, t1, code, G.nEnemyFighters, G.nAllyFighters, G.nearby == null ? 0 : G.nearby.length,
                MapMem.pendingTiles(), G.enemies == null ? 0 : G.enemies.length, r0);
        } catch (Exception x) { errors++; }
    }

    static void overrun(int r0, int work) {
        try {
            emitOvr(r0, G.rc.getRoundNum(), code, ovPhase != 0 ? ovPhase : phase, work);
        } catch (Exception x) { errors++; }
        ovPhase = 0;
    }

    /** Before the fill: carrier trip counts, then the periodic records that are due (deferred under the reserve). */
    static void endTurn(int r0) {
        phase = 3;
        int b0 = Clock.getBytecodeNum();
        try {
            if (ttype == 1) tripCount(r0);
            if (r0 >= nextCnt) {
                if (Clock.getBytecodesLeft() < reserve) deferrals++;
                else { counters(); nextCnt += 50; }
            }
            if (ttype == 0 && r0 >= nextHqs) {
                if (Clock.getBytecodesLeft() < reserve) deferrals++;
                else { hqs(); nextHqs += 25; }
            }
        } catch (Exception e) { errors++; }
        endCost = Clock.getBytecodeNum() - b0;
    }

    /** The v2 indicator string (A.5), every turn. */
    static void indicator() {
        int b0 = Clock.getBytecodeNum();
        phase = 5;
        try {
            G.rc.setIndicatorString(indicatorString(letters.charAt(code & 63), code, G.note, G.overruns, G.exceptions,
                G.nearMiss, MapMem.cand, MapMem.decidedRound, Nav.wallHits, Nav.budgetFlips + Nav.edgeFlips, G.extra));
        } catch (Exception e) { errors++; }
        if (C.TELEMETRY) {
            int c = endCost + Clock.getBytecodeNum() - b0;
            if (c > maxCost) maxCost = c;
            endCost = 0;
        }
    }

    /** "<letter><ALPHA[code]><rest>|ov=..,ex=..,nm=..,sm=..,sd=..,wh=..,bf=..<extra>", cut to 64 characters at a comma
     *  so only whole trailing fields are dropped (the engine cuts at 64 and would split a number). */
    public static String indicatorString(char letter, int code, String rest, int ov, int ex, int nm, int sm, int sd,
                                         int wh, int bf, String extra) {
        String s = new StringBuilder(96).append(letter).append(ALPHA.charAt(code & 63)).append(rest).append("|ov=").append(ov)
            .append(",ex=").append(ex).append(",nm=").append(nm).append(",sm=").append(sm).append(",sd=").append(sd)
            .append(",wh=").append(wh).append(",bf=").append(bf).append(extra).toString();
        if (s.length() > 64) {
            int k = s.lastIndexOf(',', 64);
            s = s.substring(0, k > 0 ? k : 64);
        }
        return s;
    }

    /**
     * The bytecode channel: burn n = (c - now - PADK) & 63 bytecodes so that the turn's recorded bytecodesUsed is
     * congruent to c (mod 64); c = this turn's code, or SYNC_CODE on sync rounds. The LAST call before Clock.yield():
     * C.PADK is the constant overhead from the getBytecodeNum() read to the pause (recalibrate if this changes).
     */
    static void pad() {
        if (Clock.getBytecodesLeft() < BCC_GUARD) return;
        int c = G.rc.getRoundNum() % 50 == 25 ? SYNC_CODE : code;
        int now = Clock.getBytecodeNum();
        int n = (c - now - C.PADK) & 63;
        int s = 0;
        switch (n) {   // fall-through: case k costs exactly k (each s++ is one instruction in its own basic block)
            case 63: s++; case 62: s++; case 61: s++; case 60: s++; case 59: s++; case 58: s++; case 57: s++; case 56: s++;
            case 55: s++; case 54: s++; case 53: s++; case 52: s++; case 51: s++; case 50: s++; case 49: s++; case 48: s++;
            case 47: s++; case 46: s++; case 45: s++; case 44: s++; case 43: s++; case 42: s++; case 41: s++; case 40: s++;
            case 39: s++; case 38: s++; case 37: s++; case 36: s++; case 35: s++; case 34: s++; case 33: s++; case 32: s++;
            case 31: s++; case 30: s++; case 29: s++; case 28: s++; case 27: s++; case 26: s++; case 25: s++; case 24: s++;
            case 23: s++; case 22: s++; case 21: s++; case 20: s++; case 19: s++; case 18: s++; case 17: s++; case 16: s++;
            case 15: s++; case 14: s++; case 13: s++; case 12: s++; case 11: s++; case 10: s++; case 9: s++; case 8: s++;
            case 7: s++; case 6: s++; case 5: s++; case 4: s++; case 3: s++; case 2: s++; case 1: s++; case 0:
        }
    }

    // ---------------------------------------------------------------- periodic records
    static void counters() {
        emitCnt(G.overruns, G.exceptions, G.nearMiss, G.maxBc, Nav.wallHits, Nav.stallFlips, Nav.edgeFlips, Nav.budgetFlips);
        switch (ttype) {
            case 0: emitCntt(HQ.carriersBuilt, HQ.launchersBuilt, HQ.ampsBuilt, HQ.anchorsBuilt, HQ.floatRounds, 0, 0, 0); break;
            case 1: emitCntt(Carrier.trips, Carrier.fled, Carrier.throwsMade, Carrier.anchorsPlaced, Carrier.anchorsReturned,
                crowdSwitches, waitTurns, exploreTurns); break;
            case 2: emitCntt(Launcher.shots, Launcher.steppedIn, Launcher.kited, Launcher.pinnedSeen, Launcher.unsafeStepsAvoided,
                Launcher.regroups, Launcher.follows, guardBreaks); break;
            default:
        }
        emitCntm(MapMem.cand, MapMem.decidedRound, MapMem.symConflicts, Comms.writes, Comms.refusedWrites, MapMem.maxPending,
            MapMem.seenWellCount(), MapMem.maxUnreported, maxCost, errors, deferrals);
    }

    /** HQ snapshot, plus the shared array (8 records) from the HQ registered in Comms.HQ_LOC slot 0. */
    static void hqs() throws GameActionException {
        RobotController rc = G.rc;
        int w = HQ.lastWells;
        emitHqs(rc.getResourceAmount(ResourceType.ADAMANTIUM), rc.getResourceAmount(ResourceType.MANA),
            rc.getResourceAmount(ResourceType.ELIXIR), rc.getRobotCount(), HQ.carriersBuilt, HQ.launchersBuilt, HQ.ampsBuilt,
            HQ.anchorsBuilt, w, C.ROBOTS_BASE + C.ROBOTS_PER_WELL * (w > 1 ? w : 1), HQ.floatRounds);
        if (commsHQ == 0) commsHQ = rc.readSharedArray(Comms.HQ_LOC) == G.enc(G.here) ? 1 : 2;
        if (commsHQ != 1) return;
        for (int j = 0; j < 8; j++) {
            int k = j * 8;
            dot(COMMS + j, rc.readSharedArray(k) | rc.readSharedArray(k + 1) << 16, rc.readSharedArray(k + 2) | rc.readSharedArray(k + 3) << 16,
                rc.readSharedArray(k + 4) | rc.readSharedArray(k + 5) << 16, rc.readSharedArray(k + 6) | rc.readSharedArray(k + 7) << 16);
        }
    }

    // ---------------------------------------------------------------- carrier hooks
    /** Per-trip and cumulative state counts from this turn's carrier code (endTurn). */
    static void tripCount(int r0) {
        switch (code >> 1) {
            case 2: tCollect++; if (tFirst == 0) tFirst = r0; tLast = r0; break;
            case 3: case 4: tWait++; waitTurns++; break;
            case 5: tExplore++; exploreTurns++; break;
            case 8: case 9: tFlee++; break;
            default:
        }
    }

    /** A deposit that emptied the carrier: one TRIP record, then a new trip starts. */
    static void trip(MapLocation home, int load, int role, MapLocation well, int wellType) {
        try {
            int hq = 0;
            MapLocation[] hs = HQState.ourHQs;
            if (hs != null && home != null) for (int i = hs.length; --i >= 0; ) if (home.equals(hs[i])) hq = i;
            emitTrip(loc12(well), wellType, role, load, hq, tStart, tFirst, tLast, G.round, tWait, tExplore, tFlee, tCollect);
        } catch (Exception e) { errors++; }
        tStart = G.round;
        tFirst = tLast = tWait = tExplore = tFlee = tCollect = 0;
    }

    // ---------------------------------------------------------------- record packers (A.6; golden vectors in A.9)
    static void emitHdr(int type, int spawnRound, int spawn, int roles, int micro, int army, int spawnSafety, int batch,
                        int padk, int sync, int build) {
        dot(HDR, MAGIC, sat(type, 8) | s16(spawnRound) << 8,
            sat(spawn, 12) | sat(roles, 2) << 12 | sat(micro, 1) << 14 | sat(army, 1) << 15 | sat(spawnSafety, 1) << 16 | sat(batch, 3) << 17,
            s8(padk) | s8(sync) << 8 | s16(build) << 16);
    }

    static void emitExc(int site, int gaeType, int phase, int code, int r0, int roundNow, int excClass) {
        dot(EXC, (site & 15) | s8(gaeType) << 4 | (phase & 15) << 12 | (code & 63) << 16, r0, roundNow, excClass & 15);
    }

    static void emitNm(int work, int t1, int code, int ef, int af, int nearby, int pending, int enemies, int r0) {
        dot(NM, s16(work) | s16(t1) << 16, (code & 63) | s8(ef) << 8 | s8(af) << 16 | s8(nearby) << 24,
            s16(pending) | s8(enemies) << 16, r0);
    }

    static void emitOvr(int r0, int roundNow, int code, int phase, int work) {
        dot(OVR, r0, roundNow, (code & 63) | (phase & 15) << 8, work);
    }

    // periodic records: every argument is a counter, stock, round or mask that is never negative (clamped at the top)
    static void emitCnt(int ov, int ex, int nm, int maxBc, int wallHits, int stallFlips, int edgeFlips, int budgetFlips) {
        dot(CNT, Math.min(ov, 65535) | Math.min(ex, 65535) << 16, Math.min(nm, 65535) | Math.min(maxBc, 65535) << 16,
            Math.min(wallHits, 65535) | Math.min(stallFlips, 65535) << 16, Math.min(edgeFlips, 65535) | Math.min(budgetFlips, 65535) << 16);
    }

    static void emitCntt(int a0, int a1, int b0, int b1, int c0, int c1, int d0, int d1) {
        dot(CNTT, Math.min(a0, 65535) | Math.min(a1, 65535) << 16, Math.min(b0, 65535) | Math.min(b1, 65535) << 16,
            Math.min(c0, 65535) | Math.min(c1, 65535) << 16, Math.min(d0, 65535) | Math.min(d1, 65535) << 16);
    }

    /** decidedRound: -1 = undecided (packed as decided_round + 1). */
    static void emitCntm(int cand, int decidedRound, int symConflicts, int writes, int refused, int maxPending, int seenWells,
                         int maxUnreported, int teleMaxCost, int teleErrors, int teleDeferrals) {
        dot(CNTM, (cand & 7) | Math.min(decidedRound + 1, 4095) << 4 | Math.min(symConflicts, 65535) << 16,
            Math.min(writes, 65535) | Math.min(refused, 65535) << 16,
            Math.min(maxPending, 65535) | Math.min(seenWells, 255) << 16 | Math.min(maxUnreported, 255) << 24,
            Math.min(teleMaxCost, 65535) | Math.min(teleErrors, 255) << 16 | Math.min(teleDeferrals, 255) << 24);
    }

    static void emitSym(int eliminated, int evidence, int candAfter, int conflict, int at, int r0, int symConflicts) {
        dot(SYM, (eliminated & 7) | (evidence & 7) << 4 | (candAfter & 7) << 8 | (conflict & 1) << 12, at, r0, symConflicts);
    }

    static void emitRole(int old, int nw, int reason, int hqAd, int hqMn, int hq, int trips) {
        dot(ROLE, (old & 15) | (nw & 15) << 4 | (reason & 15) << 8, hqAd, hqMn, (hq & 4095) | s16(trips) << 12);
    }

    static void emitWell(int well, int wellType, int source, int role, int d2, int sharedWells, int seenWells, int searchTurns,
                         int crowdTurns, int prevWell) {
        dot(WELL, (well & 4095) | (wellType & 3) << 12 | (source & 7) << 14 | (role & 3) << 17, d2,
            s8(sharedWells) | s8(seenWells) << 8 | s16(searchTurns) << 16, s8(crowdTurns) | (prevWell & 4095) << 8);
    }

    static void emitTrip(int well, int wellType, int role, int load, int hq, int tStart, int tFirst, int tLast, int tDeposit,
                         int wait, int explore, int flee, int collect) {
        dot(TRIP, (well & 4095) | (wellType & 3) << 12 | (role & 3) << 14 | s8(load) << 16 | (hq & 3) << 24,
            s16(tStart) | s16(tFirst) << 16, s16(tLast) | s16(tDeposit) << 16,
            s8(wait) | s8(explore) << 8 | s8(flee) << 16 | s8(collect) << 24);
    }

    static void emitFlee(int threatD2, int ef, int hp, boolean threw, boolean moved, int threat, int weight, int home, int r0) {
        dot(FLEE, s8(threatD2) | s8(ef) << 8 | s8(hp) << 16 | (threw ? 1 << 24 : 0) | (moved ? 1 << 25 : 0),
            (threat & 4095) | s8(weight) << 12, home, r0);
    }

    /** island: an id, -1 for a predicted island (packed as 255), 0 for none. */
    static void emitAnch(int event, int island, int source, boolean enemySide, int target, int anchorTurns, int d2, int r0) {
        dot(ANCH, (event & 15) | (island < 0 ? 255 : s8(island)) << 4 | (source & 3) << 12 | (enemySide ? 1 << 14 : 0),
            (target & 4095) | sat(anchorTurns, 12) << 12, s16(d2), r0);
    }

    static void emitObj(int kind, int sightingAge, int allies, int ef, int island, int objective, int at, int r0) {
        dot(OBJ, (kind & 15) | (sightingAge & 15) << 4 | s8(allies) << 8 | s8(ef) << 16 | s8(island) << 24, objective, at, r0);
    }

    /** FIGHT word a (shots_after may be OR-ed in later at bit 14). Every field is bounded by construction. */
    static int fightA(boolean ready, boolean superior, boolean outnumbered, boolean anyCanHit, boolean moved, int dir,
                      boolean guardBreak, boolean micro, int shotsBefore, int shotsAfter, int ef, int af) {
        return (ready ? 1 : 0) | (superior ? 2 : 0) | (outnumbered ? 4 : 0) | (anyCanHit ? 8 : 0) | (moved ? 16 : 0)
            | (dir & 15) << 5 | (guardBreak ? 1 << 9 : 0) | (micro ? 1 << 10 : 0) | (shotsBefore & 3) << 12
            | (shotsAfter & 3) << 14 | (ef & 255) << 16 | (af & 255) << 24;
    }

    /** FIGHT words b (chosen tile; top = pinned enemies) and c (CENTER tile; top = tiles scored). */
    static int fightTile(int threat, boolean canHit, int minD2, int top) {
        return (threat & 255) | (canHit ? 256 : 0) | (minD2 < 255 ? minD2 : 255) << 16 | (top & 255) << 24;
    }

    static int fightD(int hp, int enemies, int target) {
        return (hp & 255) | (enemies & 255) << 8 | (target < 65535 ? target : 65535) << 16;
    }

    static void emitHqs(int ad, int mn, int ex, int robots, int carriers, int launchers, int amps, int anchors, int sharedWells,
                        int carrierCap, int floatRounds) {
        dot(HQS, Math.min(ad, 65535) | Math.min(mn, 65535) << 16, Math.min(ex, 65535) | Math.min(robots, 65535) << 16,
            Math.min(carriers, 255) | Math.min(launchers, 255) << 8 | Math.min(amps, 255) << 16 | Math.min(anchors, 255) << 24,
            Math.min(sharedWells, 255) | Math.min(carrierCap, 255) << 8 | Math.min(floatRounds, 65535) << 16);
    }

    static void emitBug(int moves, int flips, int reason, int target, int start, int startRound, int r0, int startD2, int exitD2) {
        dot(BUG, s16(moves) | s8(flips) << 16 | (reason & 15) << 24, (target & 4095) | (start & 4095) << 12,
            s16(startRound) | s16(r0) << 16, s16(startD2) | s16(exitD2) << 16);
    }
}
