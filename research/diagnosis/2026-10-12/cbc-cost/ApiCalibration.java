package cbcprobe;
import battlecode.common.*;
/** Our own deliberately tiny instrumented fixture. Both wrappers push two arguments and return a primitive;
 * the engine API callsite table charges readSharedArray 2 and onTheMap 5, giving a three-bytecode difference. */
public final class ApiCalibration {
    public static int shared(RobotController rc) throws GameActionException { return rc.readSharedArray(5); }
    public static boolean map(RobotController rc, MapLocation p) { return rc.onTheMap(p); }
}
