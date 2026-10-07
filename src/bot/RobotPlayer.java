package bot;

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
            try {
                if (rc.getRoundNum() == r0) {
                    MapMem.process(G.type == RobotType.HEADQUARTERS ? 2500 : 1200);
                    if ((r0 + G.id) % 5 == 0) MapMem.flushIslands();
                }
            } catch (Exception e) {
                G.exceptions++;
                if (G.DEBUG) { System.out.println("EXC-END r" + r0 + " " + G.type + "#" + G.id); e.printStackTrace(); }
            }
            if (rc.getRoundNum() != r0) G.overruns++;
            int used = Clock.getBytecodeNum();
            if (used > G.maxBc) G.maxBc = used;
            if (used * 100 > limit * C.NEAR_MISS_PCT) G.nearMiss++;
            rc.setIndicatorString(G.note + "|ov=" + G.overruns + ",ex=" + G.exceptions + ",nm=" + G.nearMiss
                + ",sm=" + MapMem.cand + ",sd=" + MapMem.decidedRound);
            Clock.yield();
        }
    }
}
