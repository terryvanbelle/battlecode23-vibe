package c_gren2;

import battlecode.common.*;
import battlecode.world.Inventory;
import java.lang.reflect.Field;
import java.lang.reflect.Proxy;
import java.util.*;

/** c_gren1 (c_di1 + C.GREN: grenadiers at a besieged HQ). Pure rules: grenTarget exhaustively over small enemy sets
 *  against a sorted reference (kill first and the highest health among kills, else the lowest health; ties nearest,
 *  then the lowest ID; fighters before carriers and amplifiers; never an HQ or a robot beyond r2 9), grenAmount over
 *  weight 0..40 and HQ stock -100..100 (the stock to spare), the bornGren and grenMarked truth tables, HQ.grenTile /
 *  Carrier.grenAdj / Carrier.grenStep over every movable or buildable mask (never a blocked or non-adjacent tile, never
 *  past the leash), HQ.grenLive and grenRoom. Through a RobotController proxy (a small world: one controlled robot, our
 *  HQ, other robots, walls): the birth rule against the shared HQ_LOC slots and the HQ's grenadier mark (AD_FLAGS bit
 *  Comms.GREN_SHIFT+i; ALARM ignored), one grenadier cycle (withdraw on turn 1, throw at an enemy launcher at r2 <= 9
 *  on turn 2), the approach, the walk back, the C.GREN_IDLE conversion and the hand-back that is no trip, the idle
 *  pre-load that leaves C.GREN_IDLE_KEEP, the bytecode guard, and HQ.build under threat (200 Ad: grenadiers on the
 *  adjacent tile nearest the enemy, at most C.GREN_MAX of its own in vision, those out on the leash counted, ordinary
 *  carriers not; 80 Ad or no threat: none), its mark the next round (newborns are grenadiers although last round's
 *  launchers zero ALARM; carriers of an unthreatened HQ never are). With C.GREN false only the zero dose runs (c_di1's
 *  HQ.build: nothing under threat). Exits non-zero on a failure. */
public class Gren2Test {
    static int checks;

    // ---------------------------------------------------------------- proxy world
    static final int MW = 30, MH = 30;
    static final MapLocation HQL = new MapLocation(10, 10);
    static final int HQ_ID = 3;
    static MapLocation me;
    static RobotType meType;
    static int actCD, moveCD, weight, hqAd, hqMn, nativeRound, nextId = 20000;
    static final int[] shared = new int[64];
    static final Map<MapLocation, RobotInfo> robots = new LinkedHashMap<>();
    static final Set<MapLocation> walls = new HashSet<>();
    static final List<MapLocation> attacks = new ArrayList<>(), builds = new ArrayList<>();
    static final List<Integer> withdrawals = new ArrayList<>();
    static final List<String> calls = new ArrayList<>();

    static boolean onMap(MapLocation l) { return l.x >= 0 && l.y >= 0 && l.x < MW && l.y < MH; }
    static boolean occupied(MapLocation l) { return l.equals(HQL) || robots.containsKey(l) || l.equals(me); }
    static int vision() { return meType == RobotType.HEADQUARTERS ? 34 : 20; }
    static RobotInfo hqInfo() {
        Inventory inv = new Inventory();
        inv.addAdamantium(hqAd); inv.addMana(hqMn);
        return new RobotInfo(HQ_ID, Team.A, RobotType.HEADQUARTERS, inv, 1, HQL);
    }
    static boolean canMove(Direction d) {
        MapLocation n = me.add(d);
        return meType == RobotType.CARRIER && moveCD < 10 && onMap(n) && !walls.contains(n) && !occupied(n);
    }
    static boolean canAttack(MapLocation t) {
        return meType == RobotType.CARRIER && actCD < 10 && weight > 0 && onMap(t) && me.distanceSquaredTo(t) <= 9;
    }
    static boolean canTransfer(MapLocation l, ResourceType rt, int amt) {
        if (meType != RobotType.CARRIER || actCD >= 10 || amt == 0 || rt != ResourceType.ADAMANTIUM) return false;
        if (me.distanceSquaredTo(l) > 2) return false;
        if (amt > 0) return weight >= amt;
        return l.equals(HQL) && weight - amt <= GameConstants.CARRIER_CAPACITY && hqAd >= -amt;
    }
    static boolean canBuild(RobotType t, MapLocation l) {
        return meType == RobotType.HEADQUARTERS && actCD < 10 && t == RobotType.CARRIER && hqAd >= 50 && onMap(l)
            && HQL.distanceSquaredTo(l) <= 9 && !walls.contains(l) && !occupied(l);
    }

    static final RobotController RC = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
        new Class<?>[]{RobotController.class}, (proxy, method, args) -> {
            String name = method.getName();
            String entry = name;
            if (args != null) for (Object arg : args) entry += ":" + arg;
            calls.add(entry);
            switch (name) {
                case "getRoundNum": return nativeRound;
                case "getLocation": return me;
                case "getType": return meType;
                case "getTeam": return Team.A;
                case "isActionReady": return actCD < 10;
                case "isMovementReady": return moveCD < 10;
                case "getWeight": return weight;
                case "getIslandCount": return 0;
                case "getNumAnchors": return 0;
                case "readSharedArray": return shared[(Integer) args[0]];
                case "canWriteSharedArray": return true;
                case "writeSharedArray": shared[(Integer) args[0]] = (Integer) args[1]; return null;
                case "setIndicatorDot": return null;
                case "canSenseRobot": {
                    int id = (Integer) args[0];
                    if (id == HQ_ID) return me.distanceSquaredTo(HQL) <= vision();
                    for (RobotInfo r : robots.values()) if (r.ID == id) return me.distanceSquaredTo(r.location) <= vision();
                    return false;
                }
                case "getResourceAmount": {
                    ResourceType rt = (ResourceType) args[0];
                    if (meType == RobotType.HEADQUARTERS) return rt == ResourceType.ADAMANTIUM ? hqAd : rt == ResourceType.MANA ? hqMn : 0;
                    return rt == ResourceType.ADAMANTIUM ? weight : 0;
                }
                case "senseNearbyRobots": {
                    check(args == null || args.length == 0, "only the no-argument sense (G.startTurn)");
                    List<RobotInfo> out = new ArrayList<>();
                    if (!me.equals(HQL) && me.distanceSquaredTo(HQL) <= vision()) out.add(hqInfo());
                    for (RobotInfo r : robots.values()) if (me.distanceSquaredTo(r.location) <= vision()) out.add(r);
                    return out.toArray(new RobotInfo[0]);
                }
                case "canSenseLocation": return me.distanceSquaredTo((MapLocation) args[0]) <= vision();
                case "senseRobotAtLocation": {
                    MapLocation l = (MapLocation) args[0];
                    if (me.distanceSquaredTo(l) > vision()) throw new GameActionException(GameActionExceptionType.CANT_SENSE_THAT, "not sensable");
                    if (l.equals(HQL)) return hqInfo();
                    return robots.get(l);
                }
                case "canMove": return canMove((Direction) args[0]);
                case "move": {
                    Direction d = (Direction) args[0];
                    check(canMove(d), "never an illegal move");
                    me = me.add(d);
                    moveCD += (int) Math.floor(GameConstants.CARRIER_MOVEMENT_SLOPE * weight) + GameConstants.CARRIER_MOVEMENT_INTERCEPT;
                    return null;
                }
                case "canAttack": return canAttack((MapLocation) args[0]);
                case "attack": {
                    MapLocation t = (MapLocation) args[0];
                    check(canAttack(t), "never an illegal throw");
                    attacks.add(t);
                    int dmg = (int) Math.floor(GameConstants.CARRIER_DAMAGE_FACTOR * weight);
                    RobotInfo v = robots.get(t);
                    if (v != null && v.team == Team.B && v.type != RobotType.HEADQUARTERS) {
                        if (v.health <= dmg) robots.remove(t);
                        else robots.put(t, new RobotInfo(v.ID, v.team, v.type, new Inventory(), v.health - dmg, t));
                    }
                    weight = 0;
                    actCD += 10;
                    return null;
                }
                case "canTransferResource": return canTransfer((MapLocation) args[0], (ResourceType) args[1], (Integer) args[2]);
                case "transferResource": {
                    MapLocation l = (MapLocation) args[0];
                    int amt = (Integer) args[2];
                    check(canTransfer(l, (ResourceType) args[1], amt), "never an illegal transfer");
                    weight -= amt;
                    hqAd += amt;
                    actCD += 10;
                    withdrawals.add(-amt);
                    return null;
                }
                case "canBuildRobot": return canBuild((RobotType) args[0], (MapLocation) args[1]);
                case "buildRobot": {
                    RobotType t = (RobotType) args[0];
                    MapLocation l = (MapLocation) args[1];
                    check(canBuild(t, l), "never an illegal build");
                    hqAd -= 50;
                    actCD += 2;
                    builds.add(l);
                    robots.put(l, new RobotInfo(nextId++, Team.A, t, new Inventory(), 150, l));
                    return null;
                }
                case "toString": return "Gren2Test.RC";
                case "hashCode": return 1;
                case "equals": return proxy == args[0];
                default: throw new UnsupportedOperationException("unexpected call: " + name);
            }
        });

    static RobotInfo bot(int id, Team t, RobotType type, int hp, int x, int y) {
        return new RobotInfo(id, t, type, new Inventory(), hp, new MapLocation(x, y));
    }
    static RobotInfo enemy(int id, RobotType type, int hp, int x, int y) { return bot(id, Team.B, type, hp, x, y); }
    static void put(RobotInfo r) { robots.put(r.location, r); }

    static void reset() throws Exception {
        calls.clear(); attacks.clear(); builds.clear(); withdrawals.clear(); robots.clear(); walls.clear();
        Arrays.fill(shared, 0);
        shared[Comms.HQ_LOC] = G.enc(HQL);
        actCD = moveCD = weight = 0; hqAd = 100; hqMn = 0; nativeRound = 400;
        G.rc = RC; G.us = Team.A; G.them = Team.B; G.W = MW; G.H = MH; G.id = 10007; G.round = 400;
        G.squad = false; G.extra = ""; G.note = "";
        HQState.ourHQs = new MapLocation[]{HQL};
        Carrier.gren = false; Carrier.grenHQ = null; Carrier.grenIdle = 0; Carrier.grenThrows = Carrier.grenWithdraws = 0;
        Carrier.drops = 0; Carrier.returning = false; Carrier.role = 2; Carrier.state = '?'; Carrier.anchorTarget = null;
        Carrier.stillTurns = 0; Carrier.grenLoad = false; Carrier.well = null; Carrier.trips = 0;
        HQ.grenBuilt = HQ.grenThisTurn = HQ.grenRound = HQ.nGren = 0; HQ.grenIds = null; HQ.grenNear = -1; HQ.hqIdx = 0;
        HQ.carriersBuilt = HQ.launchersBuilt = 0;
        HQ.liveCarriers = HQ.pendingCarriers = HQ.carrierCap = 0; HQ.spawnTiles = null; HQ.threatRound = -1;
        set(G.class, "rng", 987654321);
        budget(20000);
    }
    static void noRng(String m) throws Exception { check((Integer) get(G.class, "rng") == 987654321, m + ": no RNG draw"); }

    /** A carrier turn: cooldowns drop by 10, the sensing cache, then the grenadier's turn as Carrier.run gives it. */
    static void carrierTurn(boolean first) throws Exception {
        actCD = Math.max(0, actCD - 10); moveCD = Math.max(0, moveCD - 10);
        meType = RobotType.CARRIER; G.type = RobotType.CARRIER;
        G.startTurn();
        if (first) Carrier.grenBirth();
        if (C.GREN && Carrier.gren) { Carrier.grenTurn(); Carrier.note(); }
    }

    /** An HQ turn's spending as HQ.run gives it after the sensing cache: the ALARM write (c_def2), then the build loop. */
    static void hqTurn() throws Exception {
        actCD = Math.max(0, actCD - 10);
        me = HQL; meType = RobotType.HEADQUARTERS; G.type = RobotType.HEADQUARTERS;
        G.startTurn();
        if (C.RECALL) Comms.setAlarm(HQ.hqIdx, G.nEnemyFighters > G.nAllyFighters ? G.nEnemyFighters : 0);
        HQ.build();
    }

    static final int MARK0 = 1 << Comms.GREN_SHIFT;   // HQ 0's grenadier mark in AD_FLAGS

    public static void main(String[] a) throws Exception {
        if (!C.GREN) zeroDose();
        else {
            knobs(); target(); amount(); born(); tiles(); room();
            birth(); cycle(); approach(); walkBack(); idle(); handBack(); guard(); hqBuild(); mark();
        }
        System.out.println("Gren2Test PASS (" + checks + " checks)");
    }

    // ---------------------------------------------------------------- 1. knobs
    static void knobs() {
        check(C.GREN_AD_MIN == 90 && C.GREN_MAX == 3 && C.GREN_IDLE_KEEP == 80 && C.GREN_THROW_MIN == 32 && C.GREN_IDLE == 15
            && C.GREN_LEASH_R2 == 20 && C.GREN_MIN_LEFT == 2500, "the knobs");
        check(Comms.GREN_SHIFT == 12 && C.PROBE_SHIFT + 4 == Comms.GREN_SHIFT && Comms.PRESS_SHIFT + 4 == C.PROBE_SHIFT,
            "AD_FLAGS: Ad flags 0-3, pressed 4-7, probes 8-11, grenadier marks 12-15");
        check(C.GREN_THROW_MIN * 5 / 4 == 40, "a minimum throw deals 40 (floor(1.25 w))");
        check(C.GREN_AD_MIN >= 50 + 40, "a grenadier and its first load");
        check(C.RECALL && C.HQ_THREAT == 1, "the HQ writes ALARM, threat = inDanger (the test's hqTurn mirrors both)");
        for (int w = 0; w <= 40; w++) check(w * 5 / 4 == (int) Math.floor(1.25f * w), "integer damage = engine damage, w " + w);
    }

    // ---------------------------------------------------------------- 2. grenTarget
    static final MapLocation HERE = new MapLocation(10, 10);

    /** Reference: in range, fighters before carriers/amplifiers, then sorted by (kill, health, distance, ID). */
    static RobotInfo refTarget(List<RobotInfo> es, MapLocation here, int w) {
        int dmg = (int) Math.floor(1.25f * w);
        List<RobotInfo> f = new ArrayList<>(), o = new ArrayList<>();
        for (RobotInfo r : es) {
            if (here.distanceSquaredTo(r.location) > 9) continue;
            if (r.type == RobotType.LAUNCHER || r.type == RobotType.DESTABILIZER) f.add(r);
            else if (r.type == RobotType.CARRIER || r.type == RobotType.AMPLIFIER) o.add(r);
        }
        List<RobotInfo> c = f.isEmpty() ? o : f;
        if (c.isEmpty()) return null;
        c.sort(Comparator.<RobotInfo>comparingInt(r -> r.health <= dmg ? 0 : 1)
            .thenComparingInt(r -> r.health <= dmg ? -r.health : r.health)
            .thenComparingInt(r -> here.distanceSquaredTo(r.location))
            .thenComparingInt(r -> r.ID));
        return c.get(0);
    }

    static void target() throws Exception {
        reset();
        // named cases (HERE (10,10)); r2 in brackets
        RobotInfo big = enemy(1, RobotType.LAUNCHER, 200, 12, 10);       // [4]
        RobotInfo k40 = enemy(2, RobotType.LAUNCHER, 40, 13, 10);        // [9] a kill at 40 damage
        RobotInfo k50 = enemy(3, RobotType.LAUNCHER, 50, 10, 13);        // [9] a kill only at 50
        RobotInfo far = enemy(4, RobotType.LAUNCHER, 10, 13, 11);        // [10] out of range
        RobotInfo car = enemy(5, RobotType.CARRIER, 10, 11, 10);         // [1]
        RobotInfo hq = enemy(6, RobotType.HEADQUARTERS, 1, 9, 10);       // [1] never
        RobotInfo amp = enemy(7, RobotType.AMPLIFIER, 120, 10, 11);      // [1]
        RobotInfo des = enemy(8, RobotType.DESTABILIZER, 300, 11, 11);   // [2]
        check(Carrier.grenTarget(new RobotInfo[0], HERE, 40) == null && Carrier.grenTarget(null, HERE, 40) == null, "empty: null");
        check(Carrier.grenTarget(new RobotInfo[]{far, hq}, HERE, 40) == null, "out of range and an HQ: null");
        check(Carrier.grenTarget(new RobotInfo[]{big, k40}, HERE, 32) == k40, "a kill before a nearer healthy launcher");
        check(Carrier.grenTarget(new RobotInfo[]{big, k40, k50}, HERE, 40) == k50, "among kills the highest health (50 at w 40)");
        check(Carrier.grenTarget(new RobotInfo[]{big, k40, k50}, HERE, 32) == k40, "w 32 (40 damage): 50 hp is no kill");
        check(Carrier.grenTarget(new RobotInfo[]{big, des}, HERE, 40) == big, "no kill: the lowest health (200 < 300)");
        check(Carrier.grenTarget(new RobotInfo[]{car, amp, big}, HERE, 40) == big, "a fighter before a carrier or an amplifier");
        check(Carrier.grenTarget(new RobotInfo[]{car, amp, far}, HERE, 40) == car, "no fighter in range: the carrier (a kill)");
        check(Carrier.grenTarget(new RobotInfo[]{amp, hq}, HERE, 40) == amp, "no fighter in range: the amplifier, never the HQ");
        RobotInfo t1 = enemy(30, RobotType.LAUNCHER, 120, 12, 10), t2 = enemy(31, RobotType.LAUNCHER, 120, 11, 11);
        check(Carrier.grenTarget(new RobotInfo[]{t1, t2}, HERE, 40) == t2, "health tie: the nearer (r2 2 before 4)");
        RobotInfo t3 = enemy(33, RobotType.LAUNCHER, 120, 10, 12), t4 = enemy(32, RobotType.LAUNCHER, 120, 8, 10);
        check(Carrier.grenTarget(new RobotInfo[]{t3, t4, t1}, HERE, 40) == t1, "health and distance tie: the lowest ID");
        check(Carrier.grenTarget(new RobotInfo[]{t1, t4, t3}, HERE, 40) == t1, "the lowest ID whatever the order");

        // exhaustive: every subset of a pool, two array orders, three loads
        RobotInfo[] pool = {big, k40, k50, far, car, hq, amp, des, t1, t3,
            enemy(40, RobotType.LAUNCHER, 45, 9, 9), enemy(41, RobotType.CARRIER, 60, 8, 11)};
        int n = pool.length, cases = 0, nulls = 0;
        for (int mask = 0; mask < 1 << n; mask++) {
            List<RobotInfo> set = new ArrayList<>();
            for (int i = 0; i < n; i++) if ((mask >> i & 1) != 0) set.add(pool[i]);
            for (int w : new int[]{32, 36, 40}) {
                RobotInfo want = refTarget(set, HERE, w);
                if (want == null) nulls++;
                RobotInfo[] fw = set.toArray(new RobotInfo[0]);
                List<RobotInfo> rev = new ArrayList<>(set); Collections.reverse(rev);
                check(Carrier.grenTarget(fw, HERE, w) == want, "grenTarget = reference, mask " + mask + " w " + w);
                check(Carrier.grenTarget(rev.toArray(new RobotInfo[0]), HERE, w) == want, "order-free, mask " + mask + " w " + w);
                cases++;
            }
        }
        check(cases == 3 << n && nulls > 0 && nulls < cases, "exhaustive: " + cases + " cases");
        check(calls.isEmpty(), "grenTarget makes no RC calls");
        noRng("grenTarget");
    }

    // ---------------------------------------------------------------- 3. grenAmount
    static void amount() {
        for (int w = 0; w <= 40; w++)
            for (int s = -100; s <= 100; s++) {
                int x = Carrier.grenAmount(w, s);
                check(x == Math.max(0, Math.min(40 - w, s)), "grenAmount(" + w + ", " + s + ") = " + x);
                check(x >= 0 && (x == 0 || x <= s) && w + x <= GameConstants.CARRIER_CAPACITY, "fits the stock and the capacity");
                check((x == 0) == (w == 40 || s <= 0), "nothing only when full or nothing to spare");
                if (w == 0 && s >= 40) check(x == 40, "an empty grenadier takes a full 40 kg load (50 damage)");
            }
    }

    // ---------------------------------------------------------------- 4. bornGren
    static void born() {
        int yes = 0, n = 0;
        for (int d = 0; d <= 9; d++)
            for (int ef : new int[]{0, 1, 2, 5})
                for (boolean mk : new boolean[]{false, true}) {
                    boolean want = d <= 2 && ef > 0 && mk;
                    if (want) yes++;
                    n++;
                    check(Carrier.bornGren(d, ef, mk) == want, "bornGren(" + d + ", " + ef + ", " + mk + ")");
                }
        check(n == 80 && yes == 9, "truth table: 9 of 80 are grenadiers");
        yes = 0;
        for (int b = 0; b <= 6; b++)
            for (int r = 0; r <= 7; r++) {
                boolean want = b > 0 && b == r - 1;
                if (want) yes++;
                check(HQ.grenMarked(b, r) == want, "grenMarked(" + b + ", " + r + ")");
            }
        check(yes == 6 && !HQ.grenMarked(0, 1), "marked only the round after a build (none at round 1 with no build)");
    }

    // ---------------------------------------------------------------- 5. tile choices
    static int brute(MapLocation from, boolean[] ok, MapLocation e, java.util.function.IntPredicate allowed, int bar) {
        int best = -1, bd = bar;
        for (int i = 0; i < 8; i++) {
            if (!ok[i] || !allowed.test(i)) continue;
            int d = from.add(G.DIRS[i]).distanceSquaredTo(e);
            if (d < bd) { bd = d; best = i; }
        }
        return best;
    }

    static void tiles() throws Exception {
        reset();
        MapLocation[] es = {new MapLocation(14, 10), new MapLocation(10, 6), new MapLocation(13, 13), new MapLocation(6, 11),
            new MapLocation(10, 10), new MapLocation(25, 3)};
        for (int mask = 0; mask < 256; mask++) {
            boolean[] ok = new boolean[8];
            for (int i = 0; i < 8; i++) ok[i] = (mask >> i & 1) != 0;
            for (MapLocation e : es) {
                int k = HQ.grenTile(HQL, ok, e);
                check((k < 0) == (mask == 0), "grenTile: -1 only with no buildable neighbour");
                if (k >= 0) {
                    check(ok[k], "grenTile never picks an unbuildable tile");
                    int d2 = HQL.distanceSquaredTo(HQL.add(G.DIRS[k]));
                    check(d2 >= 1 && d2 <= 2, "grenTile is adjacent");
                }
                check(k == brute(HQL, ok, e, i -> true, Integer.MAX_VALUE), "grenTile: nearest e, lowest index on a tie");
            }
        }
        check(HQ.grenTile(HQL, new boolean[]{true, true, true, true, true, true, true, true}, new MapLocation(10, 30)) == 0,
            "enemy due north: NORTH");
        check(HQ.grenTile(HQL, new boolean[]{true, true, true, true, true, true, true, true}, new MapLocation(20, 0)) == 3,
            "enemy south-east: SOUTHEAST");
        check(HQ.grenTile(HQL, new boolean[]{true, true, true, true, true, true, true, true}, HQL) == 0,
            "every neighbour tied by class: N (1) before E... lowest index among r2 1");

        // grenAdj and grenStep from every tile within r2 25 of the HQ
        int adjCases = 0, stepCases = 0;
        for (int x = 5; x <= 15; x++)
            for (int y = 5; y <= 15; y++) {
                MapLocation h = new MapLocation(x, y);
                int hd = HQL.distanceSquaredTo(h);
                if (hd == 0 || hd > 25) continue;
                for (int mask = 0; mask < 256; mask += (hd <= 8 ? 1 : 7)) {
                    boolean[] mov = new boolean[8];
                    for (int i = 0; i < 8; i++) mov[i] = (mask >> i & 1) != 0;
                    for (MapLocation e : new MapLocation[]{null, new MapLocation(14, 10), new MapLocation(7, 13), new MapLocation(16, 16)}) {
                        int k = Carrier.grenAdj(h, HQL, mov, e);
                        boolean any = false;
                        for (int i = 0; i < 8; i++) {
                            int d = HQL.distanceSquaredTo(h.add(G.DIRS[i]));
                            if (mov[i] && d >= 1 && d <= 2) any = true;
                        }
                        check((k >= 0) == any, "grenAdj: a tile exactly when a movable neighbour is adjacent to the HQ");
                        if (k >= 0) {
                            int d = HQL.distanceSquaredTo(h.add(G.DIRS[k]));
                            check(mov[k] && d >= 1 && d <= 2, "grenAdj never picks an unmovable or non-adjacent tile");
                            MapLocation ref = e != null ? e : HQL;
                            int bk = brute(h, mov, ref, i -> { int dd = HQL.distanceSquaredTo(h.add(G.DIRS[i])); return dd >= 1 && dd <= 2; }, Integer.MAX_VALUE);
                            check(k == bk, "grenAdj: nearest the fighter (the HQ without one), lowest index on a tie");
                        }
                        adjCases++;
                        if (e == null) continue;
                        int s = Carrier.grenStep(h, HQL, mov, e);
                        int bs = brute(h, mov, e, i -> HQL.distanceSquaredTo(h.add(G.DIRS[i])) <= C.GREN_LEASH_R2, h.distanceSquaredTo(e));
                        check(s == bs, "grenStep: the strictly nearer leashed tile, else stay");
                        if (s >= 0) {
                            MapLocation n = h.add(G.DIRS[s]);
                            check(mov[s] && HQL.distanceSquaredTo(n) <= C.GREN_LEASH_R2 && n.distanceSquaredTo(e) < h.distanceSquaredTo(e),
                                "grenStep: movable, on the leash, nearer");
                        }
                        stepCases++;
                    }
                }
            }
        check(adjCases > 10000 && stepCases > 7000, "tile cases: " + adjCases + " / " + stepCases);
        check(calls.isEmpty(), "pure tile choices make no RC calls");
        noRng("tiles");
    }

    // ---------------------------------------------------------------- 6. grenRoom (grenLive: the HQ's grenadiers by ID)
    static void room() throws Exception {
        reset();
        me = HQL; meType = RobotType.HEADQUARTERS; G.here = HQL;
        put(bot(100, Team.A, RobotType.CARRIER, 150, 11, 10));    // r2 1
        put(bot(101, Team.A, RobotType.CARRIER, 150, 14, 12));    // r2 20: out on the leash
        put(bot(102, Team.A, RobotType.CARRIER, 150, 15, 13));    // r2 34: the edge of HQ vision
        put(bot(103, Team.A, RobotType.CARRIER, 150, 16, 13));    // r2 45: out of vision
        put(bot(104, Team.A, RobotType.CARRIER, 150, 9, 10));     // an ordinary carrier, not built as a grenadier
        check(HQ.grenLive() == 0 && HQ.nGren == 0, "no grenadier built: none, whatever carriers stand around");
        HQ.grenIds = new int[]{100, 101, 102};
        HQ.nGren = 3;
        check(HQ.grenLive() == 3 && HQ.nGren == 3, "adjacent, on the leash (r2 20) and at r2 34: all counted");
        HQ.grenIds = new int[]{103, 100, 999};
        HQ.nGren = 3;
        check(HQ.grenLive() == 1 && HQ.nGren == 1 && HQ.grenIds[0] == 100, "out of vision (103) and dead (999) drop out");
        HQ.grenIds = new int[]{101, 999, 102};
        HQ.nGren = 2;
        check(HQ.grenLive() == 1 && HQ.grenIds[0] == 101, "only the first nGren IDs are read");
        int[][] sets = {{}, {100}, {100, 101}, {100, 101, 102}};
        for (int near = 0; near <= 3; near++)
            for (int built = 0; built <= 3; built++) {
                HQ.grenIds = sets[near].clone();
                HQ.nGren = near;
                HQ.grenNear = -1;
                HQ.grenThisTurn = built;
                check(HQ.grenRoom() == (near + built < C.GREN_MAX), "grenRoom near " + near + " built " + built);
                check(HQ.grenNear == near, "counted once: " + HQ.grenNear);
            }
        HQ.grenIds = new int[]{100, 101, 102};
        HQ.nGren = 3;
        HQ.grenNear = 0; HQ.grenThisTurn = 0;
        int n = calls.size();
        check(HQ.grenRoom() && calls.size() == n, "the count is cached for the turn (grenNear set: not recounted)");
        noRng("room");
    }

    // ---------------------------------------------------------------- 7. birth (shared HQ_LOC and the grenadier mark)
    static void birth() throws Exception {
        MapLocation hq2 = new MapLocation(20, 20);
        for (int c = 0; c < 8; c++) {
            reset();
            me = new MapLocation(11, 11);                              // r2 2 from HQL
            put(enemy(1, RobotType.LAUNCHER, 200, 14, 13));
            boolean want = true;
            switch (c) {
                case 0: shared[Comms.AD_FLAGS] = MARK0; break;           // HQ 0's mark
                case 1: shared[Comms.AD_FLAGS] = MARK0 << 1; want = false; break;   // another HQ's mark only
                case 2: shared[Comms.AD_FLAGS] = MARK0; me = new MapLocation(12, 10); want = false; break;   // r2 4
                case 3: shared[Comms.AD_FLAGS] = MARK0; robots.clear(); put(enemy(2, RobotType.CARRIER, 150, 13, 12)); want = false; break;
                case 4:                                                      // our HQ 1 (HQ_LOC order), its bit
                    shared[Comms.HQ_LOC + 1] = G.enc(hq2); HQState.ourHQs = new MapLocation[]{HQL, hq2};
                    shared[Comms.AD_FLAGS] = MARK0 << 1; me = new MapLocation(21, 19); robots.clear();
                    put(enemy(3, RobotType.LAUNCHER, 200, 23, 17)); break;
                case 5: shared[Comms.AD_FLAGS] = MARK0; HQState.ourHQs = null; want = false; break;   // HQs not registered
                case 6: shared[Comms.ALARM] = 2; shared[Comms.AD_FLAGS] = 0x0fff; want = false; break;   // ALARM, other bits: no
                default: shared[Comms.AD_FLAGS] = MARK0 | 0x0fff; shared[Comms.ALARM] = 0;   // the mark with ALARM 0: yes
            }
            carrierTurn(true);
            check(Carrier.gren == want, "birth case " + c + ": " + Carrier.gren);
            if (want) check(Carrier.grenHQ.equals(c == 4 ? hq2 : HQL), "the grenadier's HQ, case " + c);
            if (want) check(G.extra.startsWith(",gt=") || G.extra.contains(",gt="), "indicator gt/gw from birth: " + G.extra);
            noRng("birth " + c);
        }
    }

    /** A newborn grenadier next to HQL (HQ 0 built a grenadier last round: its mark) with the enemies es. */
    static void newborn(MapLocation at, RobotInfo... es) throws Exception {
        reset();
        me = at;
        shared[Comms.AD_FLAGS] = MARK0;
        for (RobotInfo e : es) put(e);
    }

    // ---------------------------------------------------------------- 8. one grenadier cycle
    static void cycle() throws Exception {
        RobotInfo L = enemy(1, RobotType.LAUNCHER, 200, 13, 11);      // r2 5 from (11,10), r2 10 from the HQ
        newborn(new MapLocation(11, 10), L);
        hqAd = 100;
        carrierTurn(true);                                            // turn 1: birth, withdraw
        check(Carrier.gren && withdrawals.equals(Collections.singletonList(40)) && weight == 40 && hqAd == 60,
            "turn 1: withdraws a full 40 kg load: " + withdrawals + " w " + weight + " hq " + hqAd);
        check(attacks.isEmpty() && me.equals(new MapLocation(11, 10)), "turn 1: no throw (action used), no step (in range)");
        check(Carrier.state == 'D' && Carrier.grenWithdraws == 1 && G.extra.equals(",gt=0,gw=1"), "turn 1 state and indicator " + G.extra);
        check(Telemetry.code == Telemetry.carrierCode(7, Carrier.role), "telemetry code 'D' (never '!', an exception turn)");
        carrierTurn(false);                                           // turn 2: throw
        check(attacks.equals(Collections.singletonList(L.location)) && weight == 0, "turn 2: throws at the launcher at r2 5");
        check(robots.get(L.location).health == 150, "50 damage (floor(1.25 x 40))");
        check(Carrier.state == 'V' && Carrier.grenThrows == 1 && G.extra.equals(",gt=1,gw=1"), "turn 2 state and indicator " + G.extra);
        check(me.equals(new MapLocation(11, 10)), "turn 2: stays next to the HQ (never flees)");
        carrierTurn(false);                                           // turn 3: reload
        check(weight == 40 && hqAd == 20 && withdrawals.size() == 2, "turn 3: reloads");
        carrierTurn(false);                                           // turn 4: second throw
        check(attacks.size() == 2 && robots.get(L.location).health == 100, "turn 4: second throw");
        carrierTurn(false);                                           // turn 5: the HQ holds 20
        check(weight == 20 && hqAd == 0 && withdrawals.get(2) == 20, "turn 5: takes what the HQ holds");
        carrierTurn(false);                                           // turn 6: 20 kg < GREN_THROW_MIN, HQ empty
        check(attacks.size() == 2 && withdrawals.size() == 3 && weight == 20, "turn 6: no light throw, no zero withdraw");
        hqAd = 30;
        carrierTurn(false);                                           // turn 7: tops up
        check(weight == 40 && hqAd == 10 && withdrawals.get(3) == 20, "turn 7: tops up to 40");
        carrierTurn(false);
        check(attacks.size() == 3 && robots.get(L.location).health == 50, "turn 8: third throw");
        noRng("cycle");

        // a kill first, the highest health among kills, a fighter before a carrier
        RobotInfo a = enemy(1, RobotType.LAUNCHER, 200, 12, 11), b = enemy(2, RobotType.LAUNCHER, 45, 13, 10),
            k = enemy(3, RobotType.LAUNCHER, 50, 11, 12), cr = enemy(4, RobotType.CARRIER, 20, 10, 11);
        newborn(new MapLocation(11, 10), a, b, k, cr);
        weight = 40;
        carrierTurn(true);
        check(attacks.equals(Collections.singletonList(k.location)) && !robots.containsKey(k.location), "kills the 50 hp launcher");
        carrierTurn(false);                                           // reload
        carrierTurn(false);
        check(attacks.get(1).equals(b.location) && !robots.containsKey(b.location), "then the 45 hp one");
        // only a carrier in range (the fighter out of range): the carrier
        RobotInfo fl = enemy(5, RobotType.LAUNCHER, 200, 15, 12), cc = enemy(6, RobotType.CARRIER, 150, 12, 12);
        newborn(new MapLocation(11, 10), fl, cc);
        weight = 40;
        moveCD = 30;                                                  // pinned: no step this turn
        carrierTurn(true);
        check(attacks.equals(Collections.singletonList(cc.location)), "no fighter within r2 9: the carrier");
    }

    // ---------------------------------------------------------------- 9. the approach (loaded, leash)
    static void approach() throws Exception {
        RobotInfo L = enemy(1, RobotType.LAUNCHER, 200, 14, 12);      // r2 13 from (11,10); r2 20 from the HQ
        newborn(new MapLocation(11, 10), L);
        hqAd = 100;
        carrierTurn(true);                                            // withdraw, then one loaded step toward L
        check(weight == 40 && me.distanceSquaredTo(L.location) < 13 && HQL.distanceSquaredTo(me) <= C.GREN_LEASH_R2,
            "loaded: one step toward the fighter, on the leash: " + me);
        check(attacks.isEmpty() && moveCD == 20, "loaded step cooldown 20 (floor(0.375 x 40) + 5)");
        MapLocation at = me;
        carrierTurn(false);                                           // action ready: in range now?
        if (me.distanceSquaredTo(L.location) <= 9) check(attacks.size() == 1, "in range after the step: throws");
        check(me.equals(at) || attacks.size() == 1, "move cooldown 10: no second step");
        // the leash: a fighter far out, the grenadier at the leash edge stays
        RobotInfo F = enemy(2, RobotType.LAUNCHER, 200, 18, 10);      // r2 64 from the HQ, in vision from (14,10)
        newborn(new MapLocation(14, 10), F);                         // r2 16 from the HQ
        weight = 40;
        Carrier.gren = true; Carrier.grenHQ = HQL;
        carrierTurn(false);
        check(me.equals(new MapLocation(14, 10)), "every nearer tile is past r2 GREN_LEASH_R2 of the HQ: stays at " + me);
        noRng("approach");
    }

    // ---------------------------------------------------------------- 10. the walk back (light)
    static void walkBack() throws Exception {
        RobotInfo L = enemy(1, RobotType.LAUNCHER, 200, 15, 10);
        newborn(new MapLocation(13, 12), L);                          // r2 13 from the HQ
        Carrier.gren = true; Carrier.grenHQ = HQL;
        hqAd = 100;
        carrierTurn(false);
        int d = HQL.distanceSquaredTo(me);
        check(d >= 1 && d <= 2, "light: back next to the HQ in two moves: " + me);
        check(me.equals(new MapLocation(11, 10)), "the adjacent tile nearest the fighter (EAST of the HQ): " + me);
        check(weight == 40 && withdrawals.size() == 1, "and withdraws on arrival (action still ready)");
        // blocked tiles: never steps onto an occupied tile
        newborn(new MapLocation(12, 10), enemy(1, RobotType.LAUNCHER, 200, 15, 10));
        put(bot(50, Team.A, RobotType.CARRIER, 150, 11, 10));
        put(bot(51, Team.A, RobotType.CARRIER, 150, 11, 11));
        Carrier.gren = true; Carrier.grenHQ = HQL;
        carrierTurn(false);
        d = HQL.distanceSquaredTo(me);
        check(d >= 1 && d <= 2 && !me.equals(new MapLocation(11, 10)) && !me.equals(new MapLocation(11, 11)),
            "the nearest free adjacent tile: " + me);
        check(me.equals(new MapLocation(11, 9)), "(11,9): r2 17 from the fighter, the free adjacent one nearest it");
    }

    // ---------------------------------------------------------------- 11. GREN_IDLE conversion
    static void idle() throws Exception {
        newborn(new MapLocation(11, 10), enemy(1, RobotType.LAUNCHER, 200, 13, 11));
        hqAd = 200;                                                   // the idle reload leaves C.GREN_IDLE_KEEP
        carrierTurn(true);
        check(Carrier.gren && weight == 40, "a loaded grenadier");
        robots.clear();                                               // the fighter is gone
        for (int t = 1; t < C.GREN_IDLE; t++) {
            carrierTurn(false);
            check(Carrier.gren && Carrier.grenIdle == t, "idle turn " + t + ": still a grenadier");
            check(me.equals(new MapLocation(11, 10)) && attacks.isEmpty(), "idle: stays put");
        }
        put(enemy(2, RobotType.LAUNCHER, 200, 14, 10));               // a fighter returns: the count restarts
        carrierTurn(false);
        check(Carrier.gren && Carrier.grenIdle == 0, "a fighter in vision resets grenIdle");
        robots.clear();
        for (int t = 1; t < C.GREN_IDLE; t++) carrierTurn(false);
        check(Carrier.gren, "GREN_IDLE - 1 idle turns: still a grenadier");
        carrierTurn(false);
        check(!Carrier.gren && Carrier.returning && weight > 0, "GREN_IDLE idle turns: an ordinary carrier, the load goes home");
        check(G.extra.equals(",gt=1,gw=2"), "after the conversion gt/gw stay once it has thrown: " + G.extra);
        // an empty one tops up while idle, only above the HQ's C.GREN_IDLE_KEEP, then converts and returns
        newborn(new MapLocation(11, 10), enemy(1, RobotType.LAUNCHER, 200, 13, 11));
        hqAd = 0;
        carrierTurn(true);
        robots.clear();
        hqAd = 95;
        carrierTurn(false);
        check(weight == 15 && hqAd == C.GREN_IDLE_KEEP, "idle and light next to the HQ: tops up what the HQ spares: " + weight);
        for (int t = 2; t <= C.GREN_IDLE; t++) carrierTurn(false);
        check(!Carrier.gren && Carrier.returning, "converted with 15 kg: returning");
        check(G.extra.equals(""), "never thrown: no gt/gw after the conversion: " + G.extra);
        newborn(new MapLocation(11, 10), enemy(1, RobotType.LAUNCHER, 200, 13, 11));
        hqAd = 0;
        carrierTurn(true);
        robots.clear();
        for (int t = 1; t <= C.GREN_IDLE; t++) carrierTurn(false);
        check(!Carrier.gren && !Carrier.returning && weight == 0, "an empty one converts without a trip home");
        // the idle pre-load leaves the HQ its anchor's Ad (C.GREN_IDLE_KEEP); with a fighter in vision it takes all
        int[][] keep = {{80, 0, 80}, {81, 1, 80}, {110, 30, 80}, {120, 40, 80}, {200, 40, 160}, {60, 0, 60}};
        for (int[] k : keep) {
            newborn(new MapLocation(11, 10), enemy(1, RobotType.LAUNCHER, 200, 13, 11));
            hqAd = 0;
            carrierTurn(true);
            robots.clear();
            hqAd = k[0];
            carrierTurn(false);
            check(weight == k[1] && hqAd == k[2], "idle pre-load from " + k[0] + ": " + weight + " kg, HQ " + hqAd);
        }
        newborn(new MapLocation(11, 10), enemy(1, RobotType.LAUNCHER, 200, 13, 11));
        hqAd = 30;
        carrierTurn(true);
        check(weight == 30 && hqAd == 0, "a fighter in vision: no reserve kept");
        noRng("idle");
    }

    // ---------------------------------------------------------------- 11b. the hand-back is no trip (telemetry)
    /** A carrier's turn that runs deliver() (the returning branch of Carrier.run) after the sensing cache. */
    static void deliverTurn() throws Exception {
        actCD = Math.max(0, actCD - 10); moveCD = Math.max(0, moveCD - 10);
        meType = RobotType.CARRIER; G.type = RobotType.CARRIER;
        G.startTurn();
        Carrier.deliver();
    }

    static void handBack() throws Exception {
        newborn(new MapLocation(11, 10), enemy(1, RobotType.LAUNCHER, 200, 13, 11));
        hqAd = 100;
        carrierTurn(true);
        robots.clear();
        for (int t = 1; t < C.GREN_IDLE; t++) carrierTurn(false);
        Telemetry.tFlee = 3; Telemetry.tStart = 1;                    // a grenadier's 'V' turns count as flee turns
        nativeRound = 450;
        carrierTurn(false);
        check(!Carrier.gren && Carrier.returning && Carrier.grenLoad && weight == 40 && hqAd == 60, "converted with the HQ's 40 kg");
        if (C.TELEMETRY) check(Telemetry.tStart == 450 && Telemetry.tFlee == 0, "a new trip window at the conversion");
        nativeRound = 452;
        deliverTurn();
        check(weight == 0 && hqAd == 100 && Carrier.state == 'D', "the load goes back into the HQ");
        check(Carrier.trips == 0 && !Carrier.grenLoad && !Carrier.returning, "the hand-back is no trip: " + Carrier.trips);
        if (C.TELEMETRY) check(Telemetry.tStart == 452, "and starts a new trip window");
        // the next (mined) load is a trip
        weight = 40;
        Carrier.returning = true;
        nativeRound = 480;
        deliverTurn();
        check(weight == 0 && Carrier.trips == 1, "a mined load after it: one trip");
        // an ordinary carrier (never a grenadier): every emptying deposit is a trip, as c_di1
        reset();
        me = new MapLocation(11, 10);
        weight = 30;
        Carrier.returning = true;
        deliverTurn();
        check(weight == 0 && Carrier.trips == 1 && !Carrier.grenLoad, "an ordinary deposit: one trip");
        noRng("hand-back");
    }

    // ---------------------------------------------------------------- 12. bytecode guard
    static void guard() throws Exception {
        newborn(new MapLocation(11, 10), enemy(1, RobotType.LAUNCHER, 200, 13, 11));
        carrierTurn(true);
        int w = weight, n = calls.size();
        budget(C.GREN_MIN_LEFT - 1);
        carrierTurn(false);
        int grenCalls = 0;
        for (int i = n; i < calls.size(); i++) if (!calls.get(i).startsWith("getRoundNum") && !calls.get(i).startsWith("getLocation")
            && !calls.get(i).startsWith("senseNearbyRobots")) grenCalls++;
        check(grenCalls == 0 && weight == w && attacks.isEmpty(), "under GREN_MIN_LEFT the grenadier does nothing");
        check(Carrier.grenIdle == 0, "and counts no idle turn");
        budget(20000);
    }

    // ---------------------------------------------------------------- 13. HQ.build under threat
    static void hqBuild() throws Exception {
        // threatened (two enemy launchers within r2 20, no launcher of ours), 200 Ad, no Mn
        reset();
        RobotInfo e1 = enemy(1, RobotType.LAUNCHER, 200, 14, 11), e2 = enemy(2, RobotType.LAUNCHER, 200, 13, 13);
        put(e1); put(e2);
        hqAd = 200;
        hqTurn();
        check(HQ.inDanger(), "fixture: in danger");
        check(builds.size() == C.GREN_MAX && HQ.grenBuilt == C.GREN_MAX && HQ.carriersBuilt == 0, "3 grenadiers: " + builds);
        check(builds.get(0).equals(new MapLocation(11, 11)), "the first on the adjacent tile nearest the nearest enemy: " + builds.get(0));
        for (MapLocation b : builds) { int d = HQL.distanceSquaredTo(b); check(d >= 1 && d <= 2, "adjacent: " + b); }
        check(builds.get(1).equals(new MapLocation(11, 10)) && builds.get(2).equals(new MapLocation(11, 9)),
            "then the next nearest free adjacent tiles (r2 10, then 13 from the enemy): " + builds);
        check(hqAd == 50, "150 Ad spent");
        check(HQ.nGren == 3 && HQ.grenRound == 400, "the three IDs tracked, the round kept for the mark");
        for (int i = 0; i < 3; i++) check(HQ.grenIds[i] == robots.get(builds.get(i)).ID, "tracked ID " + i);
        hqAd = 200;
        hqTurn();                                                     // the three stand next to it: no room
        check(builds.size() == 3 && HQ.grenBuilt == 3, "GREN_MAX grenadiers of its own in vision: no more");
        // one walks out on the leash (r2 18): still counted (a count within r2 8 built a fourth here)
        moveBot(builds.get(2), new MapLocation(13, 7));
        hqAd = 200;
        hqTurn();
        check(builds.size() == 3, "a grenadier out on the leash still counts: no build");
        moveBot(new MapLocation(13, 7), new MapLocation(16, 7));     // r2 45: out of vision
        hqTurn();
        check(builds.size() == 4 && HQ.nGren == 3, "out of vision: dropped, one more built");
        robots.remove(builds.get(0));                                 // one dies
        hqTurn();
        check(builds.size() == 5 && HQ.nGren == 3, "a dead one: dropped, one more built");
        // ordinary carriers of ours near do not count
        reset();
        put(e1); put(e2); put(bot(60, Team.A, RobotType.CARRIER, 150, 12, 12)); put(bot(61, Team.A, RobotType.CARRIER, 150, 9, 9));
        hqAd = 200;
        hqTurn();
        check(builds.size() == 3, "two ordinary carriers near: still three grenadiers");
        // GREN_AD_MIN: 80 none, 90 one
        reset(); put(e1); put(e2); hqAd = 80; hqTurn();
        check(builds.isEmpty() && HQ.grenBuilt == 0 && hqAd == 80, "80 Ad: no grenadier");
        reset(); put(e1); put(e2); hqAd = 90; hqTurn();
        check(builds.size() == 1 && hqAd == 40, "90 Ad: one (and its first load stays)");
        // adjacent tiles walled: none (the r2 4-9 spawn tiles are never used)
        reset(); put(e1); put(e2); hqAd = 200;
        for (Direction d : G.DIRS) walls.add(HQL.add(d));
        hqTurn();
        check(builds.isEmpty() && HQ.grenBuilt == 0, "no free adjacent tile: no grenadier");
        // not threatened: as many of our launchers as theirs (and a free carrier cap: c_di1's carrier, no grenadier)
        reset(); put(e1); put(e2);
        put(bot(70, Team.A, RobotType.LAUNCHER, 200, 9, 9)); put(bot(71, Team.A, RobotType.LAUNCHER, 200, 8, 9));
        hqAd = 200;
        hqTurn();
        check(!HQ.inDanger() && builds.isEmpty() && HQ.grenBuilt == 0, "not threatened, no carrier room: nothing");
        reset();
        hqAd = 200;
        HQ.carrierCap = 1;
        HQ.spawnTiles = spawnTiles();
        hqTurn();
        check(builds.size() == 1 && HQ.carriersBuilt == 1 && HQ.grenBuilt == 0, "no enemy: c_di1's one carrier, no grenadier");
        // enemy fighters far (r2 > 20): not in danger
        reset(); put(enemy(3, RobotType.LAUNCHER, 200, 15, 10)); put(enemy(4, RobotType.LAUNCHER, 200, 10, 15));
        hqAd = 200;
        hqTurn();
        check(builds.isEmpty() && HQ.grenBuilt == 0, "fighters at r2 25: not in danger, no grenadier");
        noRng("hq build");
    }

    static void moveBot(MapLocation from, MapLocation to) {
        RobotInfo r = robots.remove(from);
        check(r != null && !occupied(to), "fixture: a robot moves from " + from + " to a free " + to);
        robots.put(to, new RobotInfo(r.ID, r.team, r.type, new Inventory(), r.health, to));
    }

    // ---------------------------------------------------------------- 14. the grenadier mark (next round, before the newborns)
    static void mark() throws Exception {
        // round 400: threatened (two enemy launchers within r2 20, none of ours), 300 Ad: three grenadiers
        reset();
        put(enemy(1, RobotType.LAUNCHER, 200, 14, 11)); put(enemy(2, RobotType.LAUNCHER, 200, 13, 13));
        hqAd = 300;
        hqTurn();
        check(builds.size() == 3 && HQ.grenRound == 400, "round 400: three grenadiers");
        check((shared[Comms.AD_FLAGS] & MARK0) == 0 && Comms.alarm(0) == 2, "round 400: not marked yet; ALARM 2");
        // round 401: last round's launchers (the launcher line builds first under threat) stand in HQ vision, so
        // ALARM reads 0; the mark is up
        nativeRound = 401;
        put(bot(80, Team.A, RobotType.LAUNCHER, 200, 8, 10)); put(bot(81, Team.A, RobotType.LAUNCHER, 200, 10, 8));
        hqTurn();
        check(Comms.alarm(0) == 0 && Comms.grenMark(0), "round 401: ALARM 0, the mark up");
        check(builds.size() == 3, "round 401: not threatened, no build");
        // the newborns act after the HQ: each one is a grenadier (the ALARM rule made all three ordinary carriers)
        for (MapLocation b : new ArrayList<>(builds)) {
            RobotInfo self = robots.remove(b);
            me = b; weight = 0; actCD = moveCD = 10;
            Carrier.gren = false; Carrier.grenHQ = null; Carrier.grenIdle = 0;
            carrierTurn(true);
            check(Carrier.gren && HQL.equals(Carrier.grenHQ), "the newborn at " + b + " is a grenadier");
            robots.put(me, new RobotInfo(self.ID, Team.A, RobotType.CARRIER, new Inventory(), 150, me));
        }
        // round 402: no grenadier at 401: the mark is down, a carrier first acting now is ordinary
        nativeRound = 402;
        hqTurn();
        check(!Comms.grenMark(0), "round 402: the mark down");
        // an unthreatened HQ (fighters at r2 25-26, ALARM up) builds an ordinary carrier next to it (the nearest well
        // is adjacent); a fighter arrives the next round in the newborn's vision: it stays an ordinary carrier
        reset();
        put(enemy(1, RobotType.LAUNCHER, 200, 5, 10)); put(enemy(2, RobotType.LAUNCHER, 200, 5, 11));
        shared[Comms.WELLS] = (2 << 12) | G.enc(new MapLocation(11, 10));
        hqAd = 200;
        HQ.carrierCap = 1;
        HQ.spawnTiles = spawnTiles();
        hqTurn();
        check(!HQ.inDanger() && Comms.alarm(0) == 2, "fixture: not threatened, ALARM up");
        check(builds.size() == 1 && builds.get(0).equals(new MapLocation(11, 10)) && HQ.carriersBuilt == 1 && HQ.grenBuilt == 0,
            "an ordinary carrier on the adjacent well tile: " + builds);
        nativeRound = 401;
        put(enemy(3, RobotType.LAUNCHER, 200, 15, 12));               // r2 29 from the HQ, r2 20 from the newborn
        hqTurn();
        check(!HQ.inDanger() && Comms.alarm(0) == 3 && !Comms.grenMark(0), "round 401: ALARM 3, no mark");
        RobotInfo self = robots.remove(builds.get(0));
        me = builds.get(0); weight = 0; actCD = moveCD = 10;
        carrierTurn(true);
        check(self != null && G.nEnemyFighters == 1 && !Carrier.gren, "adjacent, a fighter in vision, ALARM up, no mark: ordinary");
        noRng("mark");
    }

    static MapLocation[] spawnTiles() {
        List<MapLocation> out = new ArrayList<>();
        for (int x = HQL.x - 3; x <= HQL.x + 3; x++)
            for (int y = HQL.y - 3; y <= HQL.y + 3; y++) {
                MapLocation l = new MapLocation(x, y);
                int d = HQL.distanceSquaredTo(l);
                if (d >= 1 && d <= 9) out.add(l);
            }
        return out.toArray(new MapLocation[0]);
    }

    // ---------------------------------------------------------------- zero dose (C.GREN false)
    static void zeroDose() throws Exception {
        reset();
        put(enemy(1, RobotType.LAUNCHER, 200, 14, 11)); put(enemy(2, RobotType.LAUNCHER, 200, 13, 13));
        hqAd = 200;
        hqTurn();
        check(builds.isEmpty() && HQ.grenBuilt == 0, "compiled out: c_di1 builds nothing under threat");
        newborn(new MapLocation(11, 10), enemy(1, RobotType.LAUNCHER, 200, 13, 11));
        carrierTurn(false);
        check(!Carrier.gren, "compiled out: no grenadier");
    }

    // ---------------------------------------------------------------- helpers
    static Object get(Class<?> cls, String name) throws Exception {
        Field f = cls.getDeclaredField(name); f.setAccessible(true); return f.get(null);
    }
    static void set(Class<?> cls, String name, Object value) throws Exception {
        Field f = cls.getDeclaredField(name); f.setAccessible(true); f.set(null, value);
    }
    static void budget(int value) {
        try {
            Field f = Class.forName("battlecode.instrumenter.inject.RobotMonitor").getDeclaredField("bytecodesLeft");
            f.setAccessible(true); f.setInt(null, value);
        } catch (Exception e) { throw new RuntimeException(e); }
    }
    static void check(boolean passed, String message) {
        checks++;
        if (!passed) { System.out.println("Gren2Test FAIL: " + message); System.exit(1); }
    }
}
