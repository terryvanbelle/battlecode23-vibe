package c_nav4;

import battlecode.common.*;

/**
 * The turn loop. Every exception is caught and counted (an uncaught exception DESTROYS the robot, HQs included:
 * GameWorld.updateRobot after SandboxedRobotPlayer terminates). Overrun = the round changed while our turn ran
 * (the engine pauses mid-code and resumes next round with stale state). Near miss = more than 90% of the limit.
 * Indicator string v2 (docs/TELEMETRY.md A.5): "<letter><code char><rest>|ov=,ex=,nm=,sm=,sd=,wh=,bf=<extra>"; the first
 * character is the state token, the second the 6-bit code; tools/replay-dump.sh --census sums the counters per team.
 * Telemetry order (A.2): records before the fill, the string after it, the bytecode-channel pad last before yield.
 */
public strictfp class RobotPlayer {
    public static void run(RobotController rc) {
        G.init(rc);
        Nav.init();
        Field.init();
        Telemetry.init();
        int limit = rc.getType().bytecodeLimit;
        while (true) {
            int r0 = rc.getRoundNum();
            Telemetry.startTurn();
            try {
                G.startTurn();
                Comms.startTurn();
                HQState.refresh();
                if (C.TELEMETRY) { Telemetry.t1 = Clock.getBytecodeNum(); Telemetry.phase = 2; }
                switch (G.type) {
                    case HEADQUARTERS: HQ.run(); break;
                    case CARRIER: Carrier.run(); break;
                    case LAUNCHER: Launcher.run(); break;
                    case AMPLIFIER: Amplifier.run(); break;
                    default: Other.run(); break;
                }
            } catch (GameActionException e) {
                G.exceptions++;
                Telemetry.exc(1, e, r0);
                if (G.DEBUG) { System.out.println("EXC r" + r0 + " " + G.type + "#" + G.id); e.printStackTrace(); }
            } catch (Exception e) {
                G.exceptions++;
                Telemetry.exc(2, e, r0);
                if (G.DEBUG) { System.out.println("EXC r" + r0 + " " + G.type + "#" + G.id); e.printStackTrace(); }
            }
            // near misses and the peak are measured on the turn's own work, before telemetry's records and the
            // deliberate budget fill below (a fill to a fixed reserve would otherwise saturate the near-miss count: bc24 M10)
            int work = Clock.getBytecodeNum();
            if (rc.getRoundNum() == r0) {
                if (work > G.maxBc) G.maxBc = work;
                if (work * 100 > limit * C.NEAR_MISS_PCT) {
                    G.nearMiss++;
                    if (C.TELEMETRY) Telemetry.nearMiss(work, r0);
                    if (G.DEBUG) System.out.println("NM r" + r0 + " " + G.type + " age=" + (r0 - G.spawnRound) + " used=" + work + " note=" + G.note);
                }
            } else if (C.TELEMETRY) Telemetry.ovPhase = Telemetry.phase;
            if (C.TELEMETRY) Telemetry.endTurn(r0);
            try {
                if (rc.getRoundNum() == r0) {
                    if (C.TELEMETRY) Telemetry.phase = 4;
                    // the fill stops at 88% of the limit for every type, below the 90% near-miss line, so replay-side
                    // near-miss counts measure real work (carriers at a fixed 1200 reserve filled to 90.4%)
                    // island flush BEFORE the fill, bounded: after the fill it ran on the 12% reserve and overran
                    // HQs by 1-12 bytecodes every ~40 rounds (HQ island scan every 8 rounds x flush every 5;
                    // c_line4 trial, match 196: 37 overruns in one game against camel_case)
                    if ((r0 + G.id) % 5 == 0) MapMem.flushIslands(limit * 12 / 100 + 1000);
                    MapMem.process(limit * 12 / 100);
                    Field.think(limit * 12 / 100);   // c_nav3: the distance field in what is left
                } else if (C.TELEMETRY && Telemetry.ovPhase == 0) Telemetry.ovPhase = 3;
            } catch (Exception e) {
                G.exceptions++;
                Telemetry.exc(3, e, r0);
                if (G.DEBUG) { System.out.println("EXC-END r" + r0 + " " + G.type + "#" + G.id); e.printStackTrace(); }
            }
            if (rc.getRoundNum() != r0) { G.overruns++; if (C.TELEMETRY) Telemetry.overrun(r0, work); }
            Telemetry.indicator();
            if (C.TELEMETRY) Telemetry.pad();   // must stay the last statement before the yield (C.PADK)
            Clock.yield();
        }
    }
}
