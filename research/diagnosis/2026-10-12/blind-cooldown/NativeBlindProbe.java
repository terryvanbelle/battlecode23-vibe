import battlecode.common.*;
import battlecode.server.Config;
import battlecode.server.GameInfo;
import battlecode.server.GameMaker;
import battlecode.server.GameState;
import battlecode.world.*;
import battlecode.world.control.NullControlProvider;

/** Host-side native-engine correctness fixtures. No player sandbox, Clock calls, networking or real games. */
public strictfp final class NativeBlindProbe {
    private static final int WIDTH = 20, HEIGHT = 20, SHOOTER = 10001, VICTIM = 10002;
    private static final MapLocation FROM = new MapLocation(6, 6), TARGET = new MapLocation(9, 6);
    private static int checks, cases;

    static final class Case {
        final String name;
        final boolean cloud, anchor, enabled, forced;
        final int boosts, destabs, pre, suppliedBudget, expectedCost;
        final boolean expectedFire;
        Case(String name, boolean cloud, boolean anchor, int boosts, int destabs, int pre,
                int budget, boolean enabled, boolean forced, int cost, boolean fire) {
            this.name = name; this.cloud = cloud; this.anchor = anchor; this.boosts = boosts;
            this.destabs = destabs; this.pre = pre; suppliedBudget = budget; this.enabled = enabled;
            this.forced = forced; expectedCost = cost; expectedFire = fire;
        }
    }

    static final class Result {
        int pre, cost, post, next, hpBefore, hpAfter, hookInvocations, nativeApiCalls;
        boolean fired, canAttack, canSense, cloudDiscoverable, nextReady;
        double multiplier;
        String reason;
    }

    static final class OwnProvider extends NullControlProvider {
        final Case fixture;
        final Result result = new Result();
        GameWorld world;
        Throwable failure;
        OwnProvider(Case fixture) { this.fixture = fixture; }
        @Override public void matchStarted(GameWorld world) { this.world = world; }
        @Override public void runRobot(InternalRobot robot) {
            if (robot.getID() != SHOOTER) return;
            try {
                RobotController rc = robot.getController();
                if (world.getCurrentRound() == 2) {
                    result.pre = rc.getActionCooldownTurns();
                    result.multiplier = rc.senseMapInfo(rc.getLocation()).getCooldownMultiplier(Team.A);
                    result.cost = (int) Math.round(RobotType.LAUNCHER.actionCooldown * result.multiplier);
                    check(result.cost == world.getCooldownWithMultiplier(10, FROM, Team.A), "native charge agrees");
                    result.canAttack = rc.canAttack(TARGET);
                    result.canSense = rc.canSenseLocation(TARGET);
                    for (MapLocation tile : rc.senseNearbyCloudLocations(16))
                        if (tile.equals(TARGET)) result.cloudDiscoverable = true;
                    boolean senseRejected = false;
                    try { rc.senseRobotAtLocation(TARGET); }
                    catch (GameActionException expected) { senseRejected = true; }
                    check(senseRejected, "hidden victim cannot be sensed");
                    result.hpBefore = world.getRobot(TARGET).getHealth();
                    hook(rc, fixture, result);
                    result.hpAfter = world.getRobot(TARGET).getHealth();
                    result.post = rc.getActionCooldownTurns();
                } else if (world.getCurrentRound() == 3) {
                    result.next = rc.getActionCooldownTurns();
                    result.nextReady = rc.isActionReady();
                }
            } catch (Throwable error) {
                // GameWorld.runRound catches ordinary engine exceptions; preserve and rethrow outside its wrapper.
                failure = error;
            }
        }
    }

    /** suppliedBudget is synthetic input: host invocation has no instruction meter. */
    private static void hook(RobotController rc, Case fixture, Result result) throws GameActionException {
        result.hookInvocations++;
        if (!fixture.forced && fixture.suppliedBudget < 3000) { result.reason = "budget"; return; }
        result.nativeApiCalls++; int cd = rc.getActionCooldownTurns();
        result.nativeApiCalls++; MapLocation here = rc.getLocation();
        result.nativeApiCalls++; MapInfo info = rc.senseMapInfo(here);
        result.nativeApiCalls++; Team team = rc.getTeam();
        int cost = (int) Math.round(10 * info.getCooldownMultiplier(team));
        if (cd >= 10) { result.reason = "not_ready"; return; }
        if (!fixture.forced && cd + cost > 10) { result.reason = "cooldown"; return; }
        result.nativeApiCalls++; if (rc.canSenseLocation(TARGET)) { result.reason = "visible"; return; }
        result.nativeApiCalls++; if (!rc.canAttack(TARGET)) { result.reason = "illegal"; return; }
        if (!fixture.enabled && !fixture.forced) { result.reason = "zero_arm"; return; }
        result.nativeApiCalls++; rc.attack(TARGET);
        result.fired = true;
        result.reason = fixture.forced ? "forced_native_control" : "fired";
    }

    private static LiveMap map(boolean cloudShooter) {
        boolean[] walls = new boolean[WIDTH * HEIGHT], clouds = new boolean[WIDTH * HEIGHT];
        int[] currents = new int[WIDTH * HEIGHT], islands = new int[WIDTH * HEIGHT], resources = new int[WIDTH * HEIGHT];
        clouds[TARGET.x + TARGET.y * WIDTH] = true;
        clouds[(WIDTH - 1 - TARGET.x) + (HEIGHT - 1 - TARGET.y) * WIDTH] = true;
        if (cloudShooter) {
            clouds[FROM.x + FROM.y * WIDTH] = true;
            clouds[(WIDTH - 1 - FROM.x) + (HEIGHT - 1 - FROM.y) * WIDTH] = true;
        }
        islands[FROM.x + FROM.y * WIDTH] = 1;
        islands[13 + 13 * WIDTH] = 2;
        islands[6 + 13 * WIDTH] = 3;
        islands[13 + 6 * WIDTH] = 4;
        resources[2 + 2 * WIDTH] = resources[17 + 17 * WIDTH] = 1;
        resources[2 + 3 * WIDTH] = resources[17 + 16 * WIDTH] = 2;
        RobotInfo[] bodies = {
            new RobotInfo(1, Team.A, RobotType.HEADQUARTERS, new Inventory(), 1, new MapLocation(1, 1)),
            new RobotInfo(2, Team.B, RobotType.HEADQUARTERS, new Inventory(), 1, new MapLocation(18, 18))
        };
        return new LiveMap(WIDTH, HEIGHT, new MapLocation(0, 0), 1, 2000, "own-blind-cd-host",
            MapSymmetry.ROTATIONAL, bodies, walls, clouds, currents, islands, resources);
    }

    private static void round(GameWorld world, OwnProvider provider, int expected) {
        GameState state = world.runRound();
        check(state == GameState.RUNNING && world.getCurrentRound() == expected, "native round completed");
        if (provider.failure != null) throw new AssertionError("scripted provider failed", provider.failure);
    }

    private static void run(Case fixture) throws Exception {
        OwnProvider provider = new OwnProvider(fixture);
        GameInfo info = new GameInfo("own-A", "own.hostA", null, "own-B", "own.hostB", null,
            new String[]{"own-blind-cd-host"}, null, false);
        GameMaker maker = new GameMaker(info, null, false); // null packet sink: no sockets/websocket server.
        maker.makeGameHeader();
        GameWorld world = new GameWorld(map(fixture.cloud), provider, maker.getMatchMaker());
        round(world, provider, 1); // Engine round 1 requires the initial robots to be HQs.
        world.spawnRobot(SHOOTER, RobotType.LAUNCHER, FROM, Team.A);
        world.spawnRobot(VICTIM, RobotType.CARRIER, TARGET, Team.B);
        if (fixture.anchor) world.getIsland(1).placeAnchor(Team.A, Anchor.ACCELERATING);
        for (int i = 0; i < fixture.boosts; i++) world.addBoost(FROM, Team.A);
        for (int i = 0; i < fixture.destabs; i++) world.addDestabilize(FROM, Team.B);
        // Set a boundary fixture's native internal state. Round 2 subtracts 10 normally before the callback.
        // This is not a claim that every prescribed pre-CD was reached by playing a particular action history.
        world.getRobot(FROM).setActionCooldownTurns(fixture.pre + 10);
        round(world, provider, 2);
        round(world, provider, 3);
        Result result = provider.result;
        check(result.hookInvocations == 1, "one hook invocation");
        if (fixture.suppliedBudget < 3000) {
            check(result.reason.equals("budget") && result.nativeApiCalls == 0, "budget guard precedes policy API calls");
        }
        if (!fixture.enabled && !fixture.forced) check(result.reason.equals("zero_arm"), "zero-arm policy boundary reached");
        check(result.pre == fixture.pre, "native pre-CD");
        check(result.cost == fixture.expectedCost, "expected native rounding");
        check(!result.canSense && result.canAttack, "hidden target still natively attackable");
        check(result.cloudDiscoverable == !fixture.cloud, "native cloud discovery exception");
        check(result.fired == fixture.expectedFire, "expected firing decision");
        check(result.hpBefore == 150 && result.hpAfter == 150 - (result.fired ? 20 : 0), "native hidden damage");
        check(result.post == result.pre + (result.fired ? result.cost : 0), "native post-CD");
        check(result.next == Math.max(0, result.post - 10), "native next-own-start decrement");
        check(result.nextReady == (result.next < 10), "native next readiness");
        if (result.fired && !fixture.forced) check(result.next == 0, "strict policy leaves zero next-turn debt");
        if (fixture.forced) check(result.post == 12 && result.next == 2, "forced cloud control demonstrates debt");
        cases++;
        System.out.println("{\"case\":\"" + fixture.name + "\",\"native_rounds\":3,\"pre_cd\":" + result.pre
            + ",\"multiplier\":" + result.multiplier + ",\"charged_cost\":" + result.cost
            + ",\"post_cd\":" + result.post + ",\"next_own_start_cd\":" + result.next
            + ",\"next_ready\":" + result.nextReady + ",\"target_sensable\":" + result.canSense
            + ",\"native_can_attack\":" + result.canAttack + ",\"target_cloud_discoverable\":" + result.cloudDiscoverable
            + ",\"fired\":" + result.fired + ",\"damage\":" + (result.hpBefore - result.hpAfter)
            + ",\"hook_invocations\":" + result.hookInvocations + ",\"hook_native_api_calls\":" + result.nativeApiCalls
            + ",\"supplied_budget_fixture\":" + fixture.suppliedBudget
            + ",\"hook_bytecodes\":null,\"instruction_metered\":false,\"reason\":\"" + result.reason + "\"}");
    }

    public static void main(String[] arguments) throws Exception {
        check(System.getProperty("java.version").startsWith("1.8."), "JDK 8 required");
        check(GameConstants.SPEC_VERSION.equals("3.0.14"), "release 3.0.15 carries SPEC metadata 3.0.14");
        Config.setGlobalConfig(new Config(new String[]{"-c", "-"})); // Do not read caller cwd's bc.conf.
        Case[] fixtures = {
            new Case("clear_zero_arm", false, false, 0, 0, 0, 10000, false, false, 10, false),
            new Case("clear_hidden_cloud_hit", false, false, 0, 0, 0, 10000, true, false, 10, true),
            new Case("clear_sum11_reject", false, false, 0, 0, 1, 10000, true, false, 10, false),
            new Case("cloud_shooter_reject", true, false, 0, 0, 0, 10000, true, false, 12, false),
            new Case("cloud_forced_native_control", true, false, 0, 0, 0, 10000, true, true, 12, true),
            new Case("boost_sum10", false, false, 1, 0, 1, 10000, true, false, 9, true),
            new Case("boost_sum11_reject", false, false, 1, 0, 2, 10000, true, false, 9, false),
            new Case("anchor_round085_sum10", false, true, 0, 0, 1, 10000, true, false, 9, true),
            new Case("anchor_destab_round095", false, true, 0, 1, 0, 10000, true, false, 10, true),
            new Case("cloud_anchor_round105_reject", true, true, 0, 0, 0, 10000, true, false, 11, false),
            new Case("threeboost_anchor_round055", false, true, 3, 0, 4, 10000, true, false, 6, true),
            new Case("threeboost_anchor_sum11_reject", false, true, 3, 0, 5, 10000, true, false, 6, false),
            new Case("synthetic_budget_reject", false, false, 0, 0, 0, 2999, true, false, 10, false)
        };
        for (Case fixture : fixtures) run(fixture);
        System.out.println("{\"summary\":\"PASS\",\"cases\":" + cases + ",\"assertions\":" + checks
            + ",\"scope\":\"native-host-correctness-only\",\"instruction_metered\":false}");
    }
    private static void check(boolean condition, String message) {
        checks++;
        if (!condition) throw new AssertionError(message);
    }
}
