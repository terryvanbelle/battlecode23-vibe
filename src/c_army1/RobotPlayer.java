package c_army1;

import battlecode.common.*;

/**
 * The turn loop. Every exception is caught and counted (an uncaught exception DESTROYS the robot, HQs included:
 * GameWorld.updateRobot after SandboxedRobotPlayer terminates). Overrun = the round changed while our turn ran
 * (the engine pauses mid-code and resumes next round with stale state). Near miss = more than 90% of the limit.
 * Indicator string: "note|ov=,ex=,nm=,sm=,sd=" -- note first (the engine cuts at 64 chars); tools/replay-dump.sh
 * --census sums the counters per team.
 */
public strictfp class RobotPlayer {
    public static void run(RobotController rc) {
        G.init(rc);
        Nav.init();
        int limit = rc.getType().bytecodeLimit;
        while (true) {
            int r0 = rc.getRoundNum();
            try {
                G.startTurn();
                Comms.startTurn();
                HQState.refresh();
                switch (G.type) {
                    case HEADQUARTERS: HQ.run(); break;
                    case CARRIER: Carrier.run(); break;
                    case LAUNCHER: Launcher.run(); break;
                    case AMPLIFIER: Amplifier.run(); break;
                    default: Other.run(); break;
                }
            } catch (GameActionException e) {
                G.exceptions++;
                if (G.DEBUG) { System.out.println("EXC r" + r0 + " " + G.type + "#" + G.id); e.printStackTrace(); }
            } catch (Exception e) {
                G.exceptions++;
                if (G.DEBUG) { System.out.println("EXC r" + r0 + " " + G.type + "#" + G.id); e.printStackTrace(); }
            }
            // near misses and the peak are measured on the turn's own work, before the deliberate budget fill below
            // (a fill to a fixed reserve would otherwise saturate the near-miss count: bc24 M10)
            int work = Clock.getBytecodeNum();
            if (rc.getRoundNum() == r0) {
                if (work > G.maxBc) G.maxBc = work;
                if (work * 100 > limit * C.NEAR_MISS_PCT) {
                    G.nearMiss++;
                    if (G.DEBUG) System.out.println("NM r" + r0 + " " + G.type + " age=" + (r0 - G.spawnRound) + " used=" + work + " note=" + G.note);
                }
            }
            try {
                if (rc.getRoundNum() == r0) {
                    // the fill stops at 88% of the limit for every type, below the 90% near-miss line, so replay-side
                    // near-miss counts measure real work (carriers at a fixed 1200 reserve filled to 90.4%)
                    MapMem.process(limit * 12 / 100);
                    if ((r0 + G.id) % 5 == 0) MapMem.flushIslands();
                }
            } catch (Exception e) {
                G.exceptions++;
                if (G.DEBUG) { System.out.println("EXC-END r" + r0 + " " + G.type + "#" + G.id); e.printStackTrace(); }
            }
            if (rc.getRoundNum() != r0) G.overruns++;
            rc.setIndicatorString(G.note + "|ov=" + G.overruns + ",ex=" + G.exceptions + ",nm=" + G.nearMiss
                + ",sm=" + MapMem.cand + ",sd=" + MapMem.decidedRound + ",wh=" + Nav.wallHits + ",bf=" + (Nav.budgetFlips + Nav.edgeFlips) + G.extra);
            Clock.yield();
        }
    }
}
