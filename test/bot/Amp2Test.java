package c_amp2;

import battlecode.common.MapLocation;
import battlecode.common.RobotController;
import battlecode.common.Team;
import java.lang.reflect.Field;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/** c_amp2's pure helpers. HQ.ampGate (each condition alone blocks the build; the 64-round builder rotation; no build at an
 *  epoch's last round). The census (Comms.CENSUS bits 0-9 carriers, 10-15 amplifiers): carriers 1023 plus amplifiers
 *  read back exactly, Comms.ampCount follows the carrier census's half-epoch rule, and a simulated game (HQs act before
 *  the newborn, HQ 0 zeroes the next slot at phase 32, the amplifier counts itself at its first turn) never builds a
 *  second amplifier while one lives, for 1-4 HQs and every death round. Comms.legacyRule (write zones without the
 *  amplifier, by census liveness), Comms.islandWriteOK (C.AMP_ENEMY_ISLANDS), Amplifier.scoutWanted, scoutSafe and escortPoint. Exits
 *  non-zero on a failure. With a RobotController proxy (shared array, island sensing, write legality): Comms.legacyZone
 *  against the 4-slot HQ_LOC reads it replaced (HQState's copy, and the first-turn fallback with none), and the well
 *  queue: flushWells publishes it whole, last first, as c_bc1 did, in a legacy zone; through the amplifier's zone alone it
 *  writes nothing and flushWellsLate publishes it in the same order at the end of the turn, keeps it where a write is no
 *  longer legal, and stops at its bytecode reserve (Clock.getBytecodesLeft() is 0 outside the engine). */
public class Amp2Test {
    public static void main(String[] a) throws Exception {
        gate();
        census();
        rotation();
        zones();
        amplifier();
        G.rc = proxy();
        G.us = Team.A;
        legacyZoneSame();
        wellFlush();
        System.out.println("amp2: ampGate, census masking and rotation, legacy write zones, island switch, scout and escort, "
            + "legacyZone, well flush: " + checks + " cases ok");
    }

    // ---------------------------------------------------------------- proxy state
    static int[] shared = new int[64];
    static boolean writable = true;
    static int islandHere;
    static Team islandOwner = Team.NEUTRAL;
    static List<int[]> writesSeen = new ArrayList<>();

    static RobotController proxy() {
        return (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
            new Class<?>[]{RobotController.class}, (p, m, args) -> {
                switch (m.getName()) {
                    case "readSharedArray": return shared[(Integer) args[0]];
                    case "canWriteSharedArray": return writable;
                    case "writeSharedArray":
                        if (!writable) throw new IllegalStateException("write outside a write zone");
                        shared[(Integer) args[0]] = (Integer) args[1];
                        writesSeen.add(new int[]{(Integer) args[0], (Integer) args[1]});
                        return null;
                    case "senseIsland": return islandHere;
                    case "senseTeamOccupyingIsland": return islandOwner;
                    default: break;
                }
                throw new UnsupportedOperationException("engine call outside the test's proxy: " + m.getName());
            });
    }

    // ---------------------------------------------------------------- Comms.legacyZone (HQState's copy of HQ_LOC)
    /** c_amp2's first legacyZone: the HQ test from the 4 HQ_LOC slots. */
    static boolean zoneBySlots(MapLocation here) {
        for (int i = 0; i < 4; i++) {
            int v = shared[Comms.HQ_LOC + i];
            if (v != 0 && here.distanceSquaredTo(G.dec(v)) <= C.HQ_WRITE_R2) return true;
        }
        return islandHere > 0 && islandOwner == G.us;
    }

    static void legacyZoneSame() throws Exception {
        Random r = new Random(23);
        Team[] owners = {Team.A, Team.B, Team.NEUTRAL};
        int in = 0, out = 0;
        for (int c = 0; c < 20000; c++) {
            java.util.Arrays.fill(shared, 0);
            int n = 1 + r.nextInt(4);
            for (int i = 0; i < n; i++) shared[Comms.HQ_LOC + i] = G.enc(new MapLocation(r.nextInt(60), r.nextInt(60)));
            // half the robots near an HQ (within 4 tiles), half anywhere
            MapLocation h = G.dec(shared[Comms.HQ_LOC + r.nextInt(n)]);
            G.here = r.nextBoolean() ? new MapLocation(Math.max(0, Math.min(59, h.x + r.nextInt(9) - 4)),
                Math.max(0, Math.min(59, h.y + r.nextInt(9) - 4))) : new MapLocation(r.nextInt(60), r.nextInt(60));
            islandHere = r.nextInt(3) == 0 ? 1 + r.nextInt(35) : 0;
            islandOwner = owners[r.nextInt(3)];
            boolean want = zoneBySlots(G.here);
            HQState.ourHQs = r.nextInt(4) == 0 ? null : Comms.ourHQs();   // null: a robot's first turn
            check(Comms.legacyZone() == want, "legacyZone at " + G.here + " with " + n + " HQs, island " + islandHere + " "
                + islandOwner + (HQState.ourHQs == null ? " (first turn)" : ""));
            if (want) in++; else out++;
        }
        check(in > 5000 && out > 5000, "legacyZone: both answers exercised (" + in + " in, " + out + " out)");
        HQState.ourHQs = null;
    }

    // ---------------------------------------------------------------- MapMem well queue
    static void setQueue(MapLocation[] wells) throws Exception {
        Field f = MapMem.class.getDeclaredField("nUnreported");
        f.setAccessible(true);
        f.setInt(null, 0);
        for (int i = 0; i < wells.length; i++) MapMem.noteWell(wells[i], 1 + i % 3);
        check(f.getInt(null) == wells.length, "queue holds " + wells.length + " wells");
    }

    static int queued() throws Exception {
        Field f = MapMem.class.getDeclaredField("nUnreported");
        f.setAccessible(true);
        return f.getInt(null);
    }

    /** c_bc1's flushWells write sequence for a queue of `wells` into an empty well table: last first, one slot each. */
    static boolean bc1Order(MapLocation[] wells) {
        if (writesSeen.size() != wells.length) return false;
        for (int k = 0; k < wells.length; k++) {
            int i = wells.length - 1 - k;
            int[] w = writesSeen.get(k);
            if (w[0] != Comms.WELLS + k || w[1] != ((1 + i % 3) << 12 | G.enc(wells[i]))) return false;
        }
        return true;
    }

    static void wellFlush() throws Exception {
        Random r = new Random(5);
        for (int c = 0; c < 400; c++) {
            int n = 1 + r.nextInt(16);
            MapLocation[] wells = new MapLocation[n];
            for (int i = 0; i < n; i++) wells[i] = new MapLocation(i * 3 + r.nextInt(3), r.nextInt(60));   // distinct
            // a legacy zone (no amplifier, or an HQ's or island's zone): the whole queue at once, as c_bc1
            java.util.Arrays.fill(shared, 0); writesSeen.clear(); writable = true;
            setQueue(wells);
            Comms.canWrite = true; Comms.legacyWrite = true;
            MapMem.flushWells();
            check(bc1Order(wells) && queued() == 0, "legacy zone: " + n + " wells published last first, queue empty");
            MapMem.flushWellsLate(-1);
            check(writesSeen.size() == n, "legacy zone: nothing left for the end of the turn");
            // the amplifier's zone alone: nothing at the start of the turn, the queue kept
            java.util.Arrays.fill(shared, 0); writesSeen.clear();
            setQueue(wells);
            Comms.canWrite = true; Comms.legacyWrite = false;
            MapMem.flushWells();
            check(writesSeen.isEmpty() && queued() == n, "amplifier zone: no write at the start of the turn");
            // end of the turn, at the reserve (outside the engine 0 bytecodes are left): nothing, the queue kept
            MapMem.flushWellsLate(0);
            check(writesSeen.isEmpty() && queued() == n, "amplifier zone: the reserve stops the late flush");
            // left the zone since startTurn: nothing written, nothing dropped, no refused write
            writable = false;
            int refused = Comms.refusedWrites;
            MapMem.flushWellsLate(-1);
            check(writesSeen.isEmpty() && queued() == n && Comms.refusedWrites == refused && Comms.canWrite,
                "amplifier zone left: the queue is kept");
            // still in the zone: c_bc1's order
            writable = true;
            MapMem.flushWellsLate(-1);
            check(bc1Order(wells) && queued() == 0, "amplifier zone: " + n + " wells published last first at the end of the turn");
            // no write access at the start of the turn: never
            java.util.Arrays.fill(shared, 0); writesSeen.clear();
            setQueue(wells);
            Comms.canWrite = false; Comms.legacyWrite = false;
            MapMem.flushWells();
            MapMem.flushWellsLate(-1);
            check(writesSeen.isEmpty() && queued() == n, "no write access: the queue waits");
        }
        java.util.Arrays.fill(shared, 0); writesSeen.clear();
        setQueue(new MapLocation[0]);
    }

    // ---------------------------------------------------------------- HQ.ampGate
    static boolean g(int round, int launchers, boolean threatened, int hqIdx, int nHQ, int lastAmp, int ad, int mn, boolean room) {
        return HQ.ampGate(round, launchers, threatened, hqIdx, nHQ, lastAmp, ad, mn, room);
    }

    static void gate() {
        int r = C.AMP_FROM + 1;   // epoch 0: HQ 0 is the builder
        check(g(r, C.AMP_MIN_L, false, 0, 3, -1000, 30, 15, false), "base case builds");
        check(!g(C.AMP_FROM - 1, C.AMP_MIN_L, false, 0, 3, -1000, 30, 15, false), "before AMP_FROM: no");
        check(g(C.AMP_FROM, C.AMP_MIN_L, false, 0, 3, -1000, 30, 15, false), "at AMP_FROM: yes");
        check(!g(r, C.AMP_MIN_L - 1, false, 0, 3, -1000, 30, 15, false), "too few launchers: no");
        check(!g(r, C.AMP_MIN_L, true, 0, 3, -1000, 30, 15, false), "threatened: no");
        check(!g(r, C.AMP_MIN_L, false, 1, 3, -1000, 30, 15, false), "not this HQ's epoch: no");
        check(!g(r, C.AMP_MIN_L, false, -1, 3, -1000, 30, 15, false), "unknown HQ index: no");
        check(!g(r, C.AMP_MIN_L, false, 0, 0, -1000, 30, 15, false), "no HQ count: no");
        check(!g(r, C.AMP_MIN_L, false, 0, 3, r - C.AMP_PERIOD + 1, 30, 15, false), "inside AMP_PERIOD: no");
        check(g(r + C.AMP_PERIOD * 3, C.AMP_MIN_L, false, 0, 3, r, 30, 15, false), "after AMP_PERIOD (epoch 3, HQ 0): yes");
        check(!g(r, C.AMP_MIN_L, false, 0, 3, -1000, 29, 15, false), "29 Ad: no");
        check(!g(r, C.AMP_MIN_L, false, 0, 3, -1000, 30, 14, false), "14 Mn: no");
        check(!g(r, C.AMP_MIN_L, false, 0, 3, -1000, 30 + C.AMP_AD_KEEP - 1, 15, true), "carrier room keeps a carrier's Ad: no");
        check(g(r, C.AMP_MIN_L, false, 0, 3, -1000, 30 + C.AMP_AD_KEEP, 15, true), "carrier room and enough Ad: yes");
        // rotation: in each round exactly one HQ index passes (all else equal), the one of (round >> 6) % nHQ
        for (int n = 1; n <= 4; n++)
            for (int round = C.AMP_FROM; round < 2000; round++) {
                int pass = 0, who = -1;
                for (int k = 0; k < n; k++) if (g(round, 99, false, k, n, -1000, 999, 999, false)) { pass++; who = k; }
                if ((round & 63) == 63) check(pass == 0, "nHQ " + n + " round " + round + ": no build at an epoch's last round");
                else check(pass == 1 && who == (round >> 6) % n, "nHQ " + n + " round " + round + ": one builder, HQ " + ((round >> 6) % n));
            }
    }

    // ---------------------------------------------------------------- census bits
    static void census() {
        int v = 0;
        for (int i = 0; i < 1023; i++) v = Math.min(65535, v + 1);       // Comms.censusTick's carrier increment
        for (int k = 0; k < 63; k++) {
            check(Comms.carriersIn(v) == 1023 && Comms.ampCount(0, v, 40) == k, "1023 carriers and " + k + " amplifiers read back");
            v = Comms.withAmp(v);
        }
        check(Comms.carriersIn(v) == 1023 && Comms.ampCount(0, v, 40) == 63 && v == 65535, "saturated: 1023 carriers, 63 amplifiers");
        check(Comms.withAmp(v) == v, "amplifier count saturates at 63");
        // carriers after amplifiers: the low bits still count carriers
        int w = Comms.withAmp(Comms.withAmp(0));
        for (int i = 0; i < 30; i++) w = Math.min(65535, w + 1);
        check(Comms.carriersIn(w) == 30 && Comms.ampCount(0, w, 0) == 2, "2 amplifiers then 30 carriers");
        check(Comms.carriersIn(Comms.withAmp(0)) == 0, "an amplifier is not a carrier");
        // half-epoch rule: first half max(prev, cur), second half cur only
        int one = Comms.withAmp(7), none = 9;
        check(Comms.ampCount(one, none, 0) == 1 && Comms.ampCount(one, none, 31) == 1, "first half: the previous epoch's amplifier counts");
        check(Comms.ampCount(one, none, 32) == 0 && Comms.ampCount(one, none, 63) == 0, "second half: only the current count");
        check(Comms.ampCount(none, one, 5) == 1 && Comms.ampCount(none, one, 50) == 1, "the current count always counts");
        check(Comms.ampCount(Comms.withAmp(one), one, 10) == 2, "first half: the larger of the two");
    }

    /** A game of HQ turns (in HQ_LOC order, before the newborn), with the census and the gate as in play: HQ.build asks
     *  ampGate, then liveAmps (Comms.liveAmps' reads), and the amplifier counts itself from its first turn (the round after
     *  its birth) until it dies. At most one amplifier may be alive or about to be born at any time. */
    static void rotation() {
        int seed = 12345;
        for (int n = 1; n <= 4; n++)
            for (int death = -1; death < 1200; death += 7) {
                for (int skip = 0; skip < 5; skip++) {   // resources: every round, 1 in 2, 1 in 5, 1 in 17, only at phases 63 and 0
                int[] slot = new int[2];
                int[] lastAmp = {-1000, -1000, -1000, -1000};
                int alive = 0, ampEpoch = -1, born = -1, builds = 0;
                for (int round = 1; round < 1500; round++) {
                    int e = round >> 6, phase = round & 63;
                    for (int k = 0; k < n; k++) {
                        if (k == 0 && phase == 32) slot[(e + 1) & 1] = 0;          // Comms.liveCarriers' zeroer
                        int live = Comms.ampCount(e == 0 || phase >= 32 ? 0 : slot[(e - 1) & 1], slot[e & 1], phase);
                        seed = seed * 1103515245 + 12345;
                        int ad = skip == 4 ? (phase == 63 || phase == 0 ? 999 : 0)
                            : skip == 0 || ((seed >>> 16) % (skip == 1 ? 2 : skip == 2 ? 5 : 17)) == 0 ? 999 : 0;
                        if (HQ.ampGate(round, 99, false, k, n, lastAmp[k], ad, 999, false) && live == 0) {
                            check(alive == 0, "nHQ " + n + " death " + death + ": second amplifier at round " + round + " by HQ " + k);
                            alive = 1; born = round; ampEpoch = -1; lastAmp[k] = round; builds++;
                        }
                    }
                    if (alive == 1 && round > born) {                                // the amplifier's turn
                        if (death >= 0 && round >= born + 1 + death) { alive = 0; continue; }
                        if (e != ampEpoch) { slot[e & 1] = Comms.withAmp(slot[e & 1]); ampEpoch = e; }
                    }
                }
                check(builds >= 1, "nHQ " + n + " death " + death + ": an amplifier is built");
                if (death < 0) check(builds == 1, "nHQ " + n + ": an immortal amplifier is built once, got " + builds);
                }
            }
    }

    // ---------------------------------------------------------------- write zones
    static void zones() {
        // canWrite false: never
        for (int m = 0; m < 16; m++) check(!Comms.legacyRule(false, (m & 1) != 0, (m & 2) != 0, (m & 4) != 0, (m & 8) != 0), "no write: no legacy write");
        check(Comms.legacyRule(true, true, false, true, false), "an HQ always");
        check(Comms.legacyRule(true, false, false, false, false), "no amplifier alive: the zone is an HQ's or an island's");
        check(!Comms.legacyRule(true, false, false, true, false), "amplifier alive, outside HQ/island zones: no");
        check(Comms.legacyRule(true, false, false, true, true), "amplifier alive, inside an HQ/island zone: yes");
        check(!Comms.legacyRule(true, false, true, false, false), "the amplifier itself away from an HQ: no");
        check(Comms.legacyRule(true, false, true, false, true), "the amplifier itself near an HQ: yes");
        // C.AMP_ENEMY_ISLANDS: with the switch on every owner is published; off, enemy-held only from a legacy zone
        for (int owner = 0; owner <= 2; owner++) {
            check(Comms.islandWriteOK(owner, true), "owner " + owner + " from a legacy zone");
            check(Comms.islandWriteOK(owner, false) == (C.AMP_ENEMY_ISLANDS || owner != 2), "owner " + owner + " through the amplifier zone");
        }
    }

    // ---------------------------------------------------------------- Amplifier
    static void amplifier() {
        check(Amplifier.scoutWanted(100, 0, 3), "no neutral located, 3 unlocated: scout");
        check(!Amplifier.scoutWanted(100, 1, 3), "a neutral island located: escort");
        check(!Amplifier.scoutWanted(100, 0, 0), "every island located: escort");
        check(!Amplifier.scoutWanted(C.AMP_SCOUT_UNTIL, 0, 3), "from AMP_SCOUT_UNTIL: escort");
        check(Amplifier.scoutWanted(C.AMP_SCOUT_UNTIL - 1, 0, 3), "just before AMP_SCOUT_UNTIL: scout");
        MapLocation t = new MapLocation(30, 30);
        MapLocation[] hqs = {new MapLocation(30, 38), new MapLocation(0, 0), null, null};
        check(!Amplifier.scoutSafe(t, hqs, 1, null), "r2 64 of a seen enemy HQ: unsafe");
        check(Amplifier.scoutSafe(t, new MapLocation[] {new MapLocation(30, 39)}, 1, null), "r2 81 of a seen enemy HQ: safe");
        check(Amplifier.scoutSafe(t, hqs, 0, null), "no seen HQ counted (nSeen 0): safe");
        check(!Amplifier.scoutSafe(t, new MapLocation[0], 0, new MapLocation(35, 35)), "r2 50 of a fresh sighting: unsafe");
        check(Amplifier.scoutSafe(t, new MapLocation[0], 0, new MapLocation(36, 36)), "r2 72 of a fresh sighting: safe");
        MapLocation p = Amplifier.escortPoint(new MapLocation(0, 0), new MapLocation(30, 60));
        check(p.x == 20 && p.y == 40, "escort point 2/3 of the way: " + p);
        MapLocation q = Amplifier.escortPoint(new MapLocation(10, 50), new MapLocation(40, 5));
        check(q.x == 30 && q.y == 20, "escort point toward smaller y: " + q);
        MapLocation s = Amplifier.escortPoint(new MapLocation(7, 7), new MapLocation(7, 7));
        check(s.x == 7 && s.y == 7, "escort point when both coincide");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("amp2 FAILED: " + what); System.exit(1); }
    }
}
