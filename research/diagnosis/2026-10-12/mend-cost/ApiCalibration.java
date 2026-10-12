package mendprobe;
import battlecode.common.*;
/** Instrumented own wrappers; proxy bodies remain host-only. */
public final class ApiCalibration {
    public static int shared(RobotController rc) throws GameActionException { return rc.readSharedArray(5); }
    public static boolean map(RobotController rc, MapLocation p) { return rc.onTheMap(p); }
    public static int health(RobotController rc) { return rc.getHealth(); }
    public static int islands(RobotController rc) { return rc.getIslandCount(); }
}
