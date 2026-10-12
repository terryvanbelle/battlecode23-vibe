import battlecode.common.*;
import battlecode.instrumenter.TeamClassLoaderFactory;
import java.lang.reflect.*;
import java.io.*;
import java.util.*;

/** Host-only method probe. Only our frozen bot classes are instrumented; setup and observation are not.
 * No GameWorld, engine game, opponent, network or submission is created. Run with the pinned release jar/JDK8.
 * Finite-budget output differences are retained: logical unbounded equivalence does not prove guarded equivalence.
 */
public final class CbcCostProbe {
    static final int[] BUDGETS = {4499, 4500, 4550, 4800, 5500, 7000, 10000, 1000000};
    static final String[] PHASES = {"fresh", "cached", "changed_location", "cached_unbounded"};
    static final int BIG = 1000000;
    static final class Scenario {
        final String name;
        final MapLocation[] hqs, seen;
        final int[] shared;
        final int symmetry;
        Scenario(String name, MapLocation[] hqs, int slots, int seenCount, int symmetry, boolean spread) {
            this.name = name; this.hqs = hqs; this.symmetry = symmetry;
            shared = new int[64]; seen = new MapLocation[seenCount];
            for (int i = 0; i < slots; i++) {
                MapLocation p = point(i, spread);
                shared[5 + i] = 2 << 12 | encode(p);
            }
            for (int i = 0; i < seenCount; i++) seen[i] = point(i + 16, spread);
        }
        MapLocation point(int i, boolean spread) {
            if (name.equals("tight_far")) return new MapLocation(20 + i % 6, 20 + (i / 6) % 6);
            if (spread) {
                int[] corners = {4, 55};
                return new MapLocation(corners[i % 2] + (i / 4) % 4 - 1, corners[(i / 2) % 2] + (i / 16) % 4 - 1);
            }
            // Distinct clustered/home-image wells; repeated coordinates deliberately exercise duplicate checks.
            return new MapLocation(3 + (i % 8), 3 + (i / 8) % 6);
        }
    }
    static MapLocation[] locations(int... xy) {
        MapLocation[] out = new MapLocation[xy.length / 2];
        for (int i = 0; i < out.length; i++) out[i] = new MapLocation(xy[2*i], xy[2*i+1]);
        return out;
    }
    static int encode(MapLocation p) { return p.x * 64 + p.y + 1; }
    static Scenario[] scenarios() {
        return new Scenario[] {
            new Scenario("empty", locations(48,48, 50,48, 48,50, 50,50), 0, 0, 1, false),
            new Scenario("tight_sparse", locations(48,48, 50,48, 48,50, 50,50), 4, 0, 1, false),
            new Scenario("tight_dense", locations(48,48, 50,48, 48,50, 50,50), 16, 32, 1, false),
            new Scenario("tight_far", locations(48,48, 50,48, 48,50, 50,50), 16, 32, 1, false),
            new Scenario("spread_dense", locations(5,5, 5,54, 54,5, 54,54), 16, 32, 1, true),
            new Scenario("spread_flip_x", locations(5,5, 5,54, 54,5, 54,54), 16, 32, 2, true)
        };
    }
    static Field field(Class<?> c, String name) throws Exception { Field f = c.getDeclaredField(name); f.setAccessible(true); return f; }
    static Method method(Class<?> c, String name, Class<?>... args) throws Exception {
        Method m = c.getDeclaredMethod(name, args); m.setAccessible(true); return m;
    }
    static final class Result {
        int cost, predRound, key, initialization;
        int[] list;
        boolean skip, complete, warmComplete;
    }
    static final class Fixture {
        final ClassLoader loader;
        final Class<?> monitor, globals, mapmem, launcher;
        final Field remaining, debt;
        final Method compute;
        final int[] shared;
        final Scenario scenario;
        final int initialization;
        boolean warmComplete;
        Fixture(TeamClassLoaderFactory factory, String pkg, Scenario s) throws Exception {
            scenario = s; shared = s.shared.clone();
            loader = factory.createLoader(false);
            monitor = loader.loadClass("battlecode.instrumenter.inject.RobotMonitor");
            remaining = field(monitor, "bytecodesLeft"); debt = field(monitor, "bytecodesToRemove");
            // Guarded methods should never pause. Fail rather than allow a synthetic pause to reset the budget.
            Class<?> pauser = Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Pauser");
            Class<?> killer = Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Killer");
            Object p = Proxy.newProxyInstance(pauser.getClassLoader(), new Class<?>[]{pauser}, (o,m,a) -> { throw new IllegalStateException("probe budget exhausted"); });
            Object k = Proxy.newProxyInstance(killer.getClassLoader(), new Class<?>[]{killer}, (o,m,a) -> { throw new IllegalStateException("probe robot killed"); });
            monitor.getMethod("init", pauser, killer, int.class, Class.forName("battlecode.instrumenter.profiler.Profiler")).invoke(null,p,k,123,null);
            monitor.getMethod("setBytecodeLimit", int.class).invoke(null,10000);
            budget(BIG);
            globals = Class.forName(pkg + ".G", true, loader);
            mapmem = Class.forName(pkg + ".MapMem", true, loader);
            launcher = Class.forName(pkg + ".Launcher", true, loader);
            // Force constants/Comms initialization before recording method cost.
            Class.forName(pkg + ".C", true, loader); Class.forName(pkg + ".Comms", true, loader);
            initialization = BIG - remaining.getInt(null);
            RobotController rc = (RobotController) Proxy.newProxyInstance(RobotController.class.getClassLoader(),
                new Class<?>[]{RobotController.class}, (o,m,a) -> {
                    if (m.getName().equals("readSharedArray")) return shared[(Integer)a[0]];
                    if (m.getName().equals("onTheMap")) return true; // calibration fixture only
                    throw new IllegalStateException("unplanned controller method: " + m.getName());
                });
            field(globals,"rc").set(null,rc); field(globals,"W").setInt(null,60); field(globals,"H").setInt(null,60);
            field(globals,"round").setInt(null,100); field(mapmem,"cand").setInt(null,s.symmetry);
            MapLocation[] seen = new MapLocation[32]; System.arraycopy(s.seen,0,seen,0,s.seen.length);
            field(mapmem,"seenWell").set(null,seen); field(mapmem,"nSeenWell").setInt(null,s.seen.length);
            compute = method(launcher,"computePredWells",MapLocation[].class);
        }
        void budget(int amount) throws Exception { remaining.setInt(null,amount); debt.setInt(null,0); }
        Result call(int amount) throws Exception {
            Object before = field(launcher,"predWells").get(null);
            budget(amount);
            try { compute.invoke(null,(Object)scenario.hqs); }
            catch (InvocationTargetException e) { throw new IllegalStateException("instrumented call failed",e.getCause()); }
            if (debt.getInt(null) != 0) throw new IllegalStateException("unflushed instrumenter bytecode debt at method return");
            Result out = new Result(); out.cost = amount - remaining.getInt(null);
            out.initialization = initialization;
            out.warmComplete = warmComplete;
            MapLocation[] wells = (MapLocation[])field(launcher,"predWells").get(null);
            out.list = new int[wells.length]; for(int i=0;i<wells.length;i++) out.list[i]=encode(wells[i]);
            out.skip = before == wells; out.predRound = field(launcher,"predRound").getInt(null);
            out.complete = out.predRound == field(globals,"round").getInt(null);
            try { out.key = field(launcher,"pkS").getInt(null); } catch (NoSuchFieldException e) { out.key=-1; }
            return out;
        }
        void prepare(String phase) throws Exception {
            if (!phase.equals("fresh")) {
                Result warm = call(phase.equals("cached_unbounded") ? BIG : 10000);
                warmComplete = warm.complete;
                if (phase.equals("cached_unbounded") && !warm.complete) throw new IllegalStateException("unbounded warmup not complete");
                field(globals,"round").setInt(null,120);
                if (phase.equals("changed_location")) shared[5] = 2 << 12 | encode(new MapLocation(13,11));
            }
        }
    }
    static Result run(TeamClassLoaderFactory factory,String pkg,Scenario s,String phase,int budget) throws Exception {
        Fixture f = new Fixture(factory,pkg,s); f.prepare(phase); return f.call(budget);
    }
    static String quote(String s) {
        StringBuilder out = new StringBuilder("\"");
        for (char c : s.toCharArray()) { if(c=='\\' || c=='\"') out.append('\\'); if(c<32) out.append(String.format("\\u%04x",(int)c)); else out.append(c); }
        return out.append('"').toString();
    }
    static int[] calibrate(TeamClassLoaderFactory factory) throws Exception {
        Fixture f = new Fixture(factory,"c_bc3",scenarios()[0]);
        Class<?> api = Class.forName("cbcprobe.ApiCalibration",true,f.loader);
        RobotController rc = (RobotController)field(f.globals,"rc").get(null);
        f.budget(10000); method(api,"shared",RobotController.class).invoke(null,rc);
        int read = 10000-f.remaining.getInt(null);
        if(f.debt.getInt(null)!=0)throw new IllegalStateException("calibration read has pending debt");
        f.budget(10000); method(api,"map",RobotController.class,MapLocation.class).invoke(null,rc,new MapLocation(1,1));
        int map = 10000-f.remaining.getInt(null);
        if(f.debt.getInt(null)!=0)throw new IllegalStateException("calibration map has pending debt");
        if(read!=5 || map!=8 || map-read!=3)throw new IllegalStateException("API callsite calibration mismatch: "+read+"/"+map);
        return new int[]{read,map};
    }
    static String scenarioJson(Scenario s) {
        int[] hq=new int[s.hqs.length],seen=new int[s.seen.length];
        for(int i=0;i<hq.length;i++)hq[i]=encode(s.hqs[i]); for(int i=0;i<seen.length;i++)seen[i]=encode(s.seen[i]);
        return "{\"name\":"+quote(s.name)+",\"symmetry\":"+s.symmetry+",\"hq_loc12\":"+Arrays.toString(hq)
            +",\"seen_loc12\":"+Arrays.toString(seen)+",\"shared_slots\":"+Arrays.toString(s.shared)+"}";
    }
    public static void main(String[] args) throws Exception {
        if(args.length!=2) throw new IllegalArgumentException("CbcCostProbe <private bot classes dir> <full result.json>");
        TeamClassLoaderFactory mend = new TeamClassLoaderFactory(args[0]), candidate = new TeamClassLoaderFactory(args[0]);
        int[] calibration=calibrate(candidate);
        StringBuilder rows = new StringBuilder(), differences = new StringBuilder(), inputs = new StringBuilder(), nominated = new StringBuilder();
        for(Scenario s:scenarios()) { if(inputs.length()>0)inputs.append(',');inputs.append(scenarioJson(s)); }
        int count=0, listDifferences=0, unboundedDifferences=0, repeatDifferences=0, cachedGain=0, reachableCachedGain=0;
        for(Scenario s:scenarios()) for(String phase:PHASES) for(int budget:BUDGETS) {
            Result m=run(mend,"c_mend2",s,phase,budget), c=run(candidate,"c_bc3",s,phase,budget);
            Result m2=run(mend,"c_mend2",s,phase,budget), c2=run(candidate,"c_bc3",s,phase,budget);
            boolean same=Arrays.equals(m.list,c.list);
            if(m.cost!=m2.cost || c.cost!=c2.cost || m.predRound!=m2.predRound || c.predRound!=c2.predRound
                || c.key!=c2.key || c.skip!=c2.skip || !Arrays.equals(m.list,m2.list) || !Arrays.equals(c.list,c2.list)) repeatDifferences++;
            if(!same) { listDifferences++; if(budget==BIG)unboundedDifferences++;
                if(differences.length()>0) differences.append(',');
                differences.append('[').append(quote(s.name)).append(',').append(quote(phase)).append(',').append(budget)
                    .append(',').append(Arrays.toString(m.list)).append(',').append(Arrays.toString(c.list)).append(']'); }
            if(phase.equals("cached_unbounded") && budget==10000 && c.cost<m.cost) cachedGain++;
            if(phase.equals("cached") && budget==10000 && c.warmComplete && c.skip && c.cost<m.cost) reachableCachedGain++;
            if(count++>0) rows.append(',');
            StringBuilder line = new StringBuilder();
            line.append('[').append(quote(s.name)).append(',').append(quote(phase)).append(',').append(budget)
                .append(',').append(m.cost).append(',').append(c.cost).append(',').append(m.list.length).append(',').append(c.list.length)
                .append(',').append(same).append(',').append(m.predRound).append(',').append(c.predRound).append(',').append(c.key)
                .append(',').append(c.skip).append(',').append(m.complete).append(',').append(c.complete)
                .append(',').append(m.initialization).append(',').append(c.initialization)
                .append(',').append(m.warmComplete).append(',').append(c.warmComplete).append(']');
            rows.append(line);
            if((s.name.equals("spread_dense") && phase.equals("fresh") && budget==4800)
                || (s.name.equals("tight_sparse") && phase.equals("cached") && budget==10000)
                || (s.name.equals("tight_far") && phase.equals("cached") && budget==10000)
                || (s.name.equals("tight_dense") && phase.startsWith("cached") && budget==10000)
                || (s.name.equals("empty") && phase.equals("cached") && budget==10000)) {
                if(nominated.length()>0)nominated.append(','); nominated.append(line);
            }
        }
        String fields="[\"shape\",\"phase\",\"budget\",\"mend_cost\",\"cbc_cost\",\"mend_wells\",\"cbc_wells\",\"same_list\",\"mend_predRound\",\"cbc_predRound\",\"cbc_key\",\"cbc_skip\",\"mend_complete\",\"cbc_complete\",\"mend_initialization\",\"cbc_initialization\",\"mend_warm_complete\",\"cbc_warm_complete\"]";
        String summary="\"cases\":"+count+",\"repeated_measurement_differences\":"+repeatDifferences+",\"list_differences\":"+listDifferences
            +",\"unbounded_list_differences\":"+unboundedDifferences+",\"hypothetical_cached_shapes_saving_at_10000\":"+cachedGain
            +",\"reachable_cached_shapes_saving_at_10000\":"+reachableCachedGain+",\"api_calibration_costs\":"+Arrays.toString(calibration);
        try(PrintWriter out=new PrintWriter(new OutputStreamWriter(new FileOutputStream(args[1]),"UTF-8"))) {
            out.println("{"+summary+",\"width\":60,\"height\":60,\"loc12\":\"x*64+y+1\",\"changed_location_loc12\":844,"
                +"\"inputs\":["+inputs+"],\"fields\":"+fields+",\"rows\":["+rows+"],\"different_lists\":["+differences+"]}");
        }
        System.out.println("{"+summary+",\"fields\":"+fields+",\"nominated_rows\":["+nominated+"]}");
        if(repeatDifferences!=0 || unboundedDifferences!=0) System.exit(2);
    }
}
