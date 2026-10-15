package c_thr1;

import battlecode.common.*;
import battlecode.world.Inventory;
import battlecode.instrumenter.inject.RobotMonitor;
import java.lang.reflect.Proxy;
import java.util.HashSet;
import java.util.Set;

/** c_thr1's safeCarrierTile: a threatened HQ may build a carrier only on a buildable spawn tile no visible enemy
 *  fighter reaches (r2 C.THREAT_R2), and a tile it cannot afford to score is never called safe. */
public final class Thr1Test {
    static int checks;
    static final Set<MapLocation> buildable = new HashSet<>();
    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            if (method.getName().equals("canBuildRobot")) return buildable.contains((MapLocation) args[1]);
            throw new UnsupportedOperationException("unexpected call: " + method.getName());
        });

    public static void main(String[] args) throws Exception {
        G.rc = RC; G.us = Team.A; G.them = Team.B;
        G.here = new MapLocation(10, 10);
        HQ.spawnTiles = new MapLocation[]{new MapLocation(7, 10), new MapLocation(13, 10)};   // west and east of the HQ
        enemies(new MapLocation(18, 10));                       // reaches the east tile (d2 25), not the west (d2 121)
        buildable.clear(); buildable.add(new MapLocation(7, 10)); buildable.add(new MapLocation(13, 10));
        budget(12000); check(HQ.safeCarrierTile(), "the west tile is out of reach: build");
        buildable.remove(new MapLocation(7, 10));
        budget(12000); check(!HQ.safeCarrierTile(), "only the reachable east tile is free: withhold");
        enemies(new MapLocation(18, 10), new MapLocation(2, 10));    // both tiles reached
        buildable.add(new MapLocation(7, 10));
        budget(12000); check(!HQ.safeCarrierTile(), "every free tile reached: withhold");
        enemies(new MapLocation(30, 30));
        budget(5000); check(!HQ.safeCarrierTile(), "no bytecodes to score: never safe");
        budget(12000); check(HQ.safeCarrierTile(), "same position with bytecodes: safe");
        check(C.SPAWN_SAFETY && C.THREAT_R2 == 26 && C.HQ_DANGER_R2 == 20
            && C.HQ_THREAT == 1 && C.CAP_MAX == 30, "threat and cap parameters as c_mend2");
        System.out.println("thr1: " + checks + " cases ok");
    }

    static void enemies(MapLocation... at) {
        G.enemies = new RobotInfo[at.length];
        for (int i = 0; i < at.length; i++)
            G.enemies[i] = new RobotInfo(100 + i, Team.B, RobotType.LAUNCHER, new Inventory(), 200, at[i]);
        G.nEnemyFighters = at.length;
        HQ.threatRound = -1; HQ.threatCache = null;          // a new turn for the per-round threat cache
    }
    static void budget(int left) throws Exception {
        RobotMonitor.setBytecodeLimit(12500); set(RobotMonitor.class, "bytecodesLeft", left); set(RobotMonitor.class, "bytecodesToRemove", 0);
    }
    static void set(Class<?> cls, String name, int value) throws Exception {
        java.lang.reflect.Field field = cls.getDeclaredField(name); field.setAccessible(true); field.setInt(null, value);
    }
    static void check(boolean ok, String message) { checks++; if (!ok) throw new AssertionError(message); }
}
