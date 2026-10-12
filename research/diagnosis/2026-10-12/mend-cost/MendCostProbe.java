import battlecode.common.*;
import battlecode.instrumenter.TeamClassLoaderFactory;
import java.lang.reflect.*;
import java.io.*;
import java.util.*;

/** Zero-game host probe: only our frozen player methods are instrumented. No GameWorld, opponent, or networking.
 * Guard thresholds apply inside the method after real earlier work; do not confuse entry budget with fallback budget.
 * Finite-budget decisions, repeatability, pending debt, and the final reserve are retained in the result. */
public final class MendCostProbe {
    static final int BIG=1000000, ROUND=320;
    static final int[] BUDGETS={5999,6000,7000,7499,7500,7800,8000,8250,8500,8750,9000,9500,10000};
    static final MapLocation HERE=new MapLocation(30,30);
    static int encode(MapLocation p) { return p.x*64+p.y+1; }
    static Field field(Class<?> type,String name) throws Exception { Field out=type.getDeclaredField(name);out.setAccessible(true);return out; }
    static Method method(Class<?> type,String name,Class<?>... args) throws Exception { Method out=type.getDeclaredMethod(name,args);out.setAccessible(true);return out; }
    static final class Scenario {
        final String name; final int islands; final boolean enemies; final int[] shared=new int[64];
        Scenario(String name,int islands,boolean enemies) {this.name=name;this.islands=islands;this.enemies=enemies;}
        Scenario island(int id,int x,int y,int owner) {shared[20+id]=owner<<12|encode(new MapLocation(x,y));return this;}
        Scenario enemy(int offset,int x,int y,int age) {shared[57+offset]=(((ROUND>>4)-age)&15)<<12|encode(new MapLocation(x,y));return this;}
    }
    static Scenario dense(String name,int owned,boolean blocked) {
        Scenario out=new Scenario(name,35,false);
        out.island(1,31,30,1);
        for(int id=2;id<=35;id++) {
            int x=24+(id-2)%12,y=25+(id-2)/12*3;
            out.island(id,x,y,id<=owned?1:2);
        }
        out.enemy(0,32,30,0).enemy(1,29,26,1).enemy(2,34,26,0).enemy(3,28,34,0);
        if(!blocked) out.island(2,30,41,1);
        return out;
    }
    static Scenario[] scenarios() {
        return new Scenario[]{
            new Scenario("empty",0,false),
            new Scenario("none_owned",35,false),
            new Scenario("nearest_safe",2,false).island(1,31,30,1).island(2,30,38,1).enemy(0,59,59,0),
            new Scenario("blocked_then_safe",2,false).island(1,31,30,1).island(2,30,38,1).enemy(0,32,30,0),
            new Scenario("all_blocked",2,false).island(1,31,30,1).island(2,32,30,1).enemy(0,32,30,0),
            dense("35_owned_four_sightings",35,false),
            dense("35_mixed_four_sightings",12,false),
            dense("35_owned_all_blocked",35,true),
            new Scenario("visible_enemy_bypass",2,true).island(1,31,30,1).island(2,30,38,1).enemy(0,32,30,0)
        };
    }
    static final class Result {
        int cost,left,initialization,id,tile,check,reads,islandReads,enemyReads,debt,minFallbackApiLeft=BIG;
        boolean mending,fallback;
        final List<int[]> readTrace=new ArrayList<>();
        String signature() {return cost+":"+left+":"+id+":"+tile+":"+check+":"+mending+":"+reads+":"+islandReads+":"+enemyReads+":"+minFallbackApiLeft;}
    }
    static final class Fixture {
        final ClassLoader loader; final Class<?> monitor,globals,mapmem,launcher;
        final Field remaining,debt; final Method mend; final Scenario scenario;
        int initialization; Result observation;
        Fixture(TeamClassLoaderFactory factory,String pkg,Scenario scenario) throws Exception {
            this.scenario=scenario;
            loader=factory.createLoader(false);
            monitor=loader.loadClass("battlecode.instrumenter.inject.RobotMonitor");
            remaining=field(monitor,"bytecodesLeft");debt=field(monitor,"bytecodesToRemove");
            Class<?> pauser=Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Pauser");
            Class<?> killer=Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Killer");
            Object p=Proxy.newProxyInstance(pauser.getClassLoader(),new Class<?>[]{pauser},(o,m,a)->{throw new IllegalStateException("probe budget exhausted");});
            Object k=Proxy.newProxyInstance(killer.getClassLoader(),new Class<?>[]{killer},(o,m,a)->{throw new IllegalStateException("probe robot killed");});
            monitor.getMethod("init",pauser,killer,int.class,Class.forName("battlecode.instrumenter.profiler.Profiler")).invoke(null,p,k,123,null);
            monitor.getMethod("setBytecodeLimit",int.class).invoke(null,10000);
            budget(BIG);
            globals=Class.forName(pkg+".G",true,loader);mapmem=Class.forName(pkg+".MapMem",true,loader);
            launcher=Class.forName(pkg+".Launcher",true,loader);
            Class.forName(pkg+".C",true,loader);Class.forName(pkg+".Comms",true,loader);
            initialization=BIG-remaining.getInt(null);
            RobotController rc=(RobotController)Proxy.newProxyInstance(RobotController.class.getClassLoader(),new Class<?>[]{RobotController.class},(o,m,a)->{
                switch(m.getName()) {
                    case "getHealth": return 80;
                    case "getIslandCount": return scenario.islands;
                    case "onTheMap": return true;
                    case "readSharedArray":
                        int slot=(Integer)a[0];
                        if(observation!=null) {
                            int effective=remaining.getInt(null)-debt.getInt(null);
                            observation.reads++;
                            if(slot>=57 && slot<=60) observation.enemyReads++;
                            if(slot>=21 && slot<=55) {
                                observation.islandReads++;
                                if(observation.enemyReads>=8) observation.minFallbackApiLeft=Math.min(observation.minFallbackApiLeft,effective);
                            }
                            observation.readTrace.add(new int[]{slot,remaining.getInt(null),debt.getInt(null),effective});
                        }
                        return scenario.shared[slot];
                    default: throw new IllegalStateException("unplanned controller method: "+m.getName());
                }
            });
            field(globals,"rc").set(null,rc);field(globals,"W").setInt(null,60);field(globals,"H").setInt(null,60);
            field(globals,"here").set(null,HERE);field(globals,"round").setInt(null,ROUND);
            field(globals,"enemies").set(null,new RobotInfo[scenario.enemies?1:0]);
            field(mapmem,"islandSeen").set(null,new int[40]);field(mapmem,"islandOwner").set(null,new int[40]);
            field(mapmem,"islandTile").set(null,new MapLocation[40]);
            field(launcher,"mending").setBoolean(null,false);field(launcher,"mendTile").set(null,null);
            field(launcher,"mendIsland").setInt(null,0);field(launcher,"mendCheck").setInt(null,0);
            mend=method(launcher,"mendUpdate");
        }
        void budget(int value) throws Exception {remaining.setInt(null,value);debt.setInt(null,0);}
        Result call(int value) throws Exception {
            observation=new Result();budget(value);
            try {mend.invoke(null);} catch(InvocationTargetException error) {throw new IllegalStateException("instrumented mendUpdate failed",error.getCause());}
            if(debt.getInt(null)!=0)throw new IllegalStateException("pending instrumenter debt at return");
            Result out=observation;observation=null;
            out.left=remaining.getInt(null);out.cost=value-out.left;out.initialization=initialization;out.debt=debt.getInt(null);
            out.mending=field(launcher,"mending").getBoolean(null);out.id=field(launcher,"mendIsland").getInt(null);
            MapLocation tile=(MapLocation)field(launcher,"mendTile").get(null);out.tile=tile==null?0:encode(tile);
            out.check=field(launcher,"mendCheck").getInt(null);out.fallback=out.enemyReads>=8;
            if(out.minFallbackApiLeft==BIG)out.minFallbackApiLeft=-1;
            return out;
        }
    }
    static int[] calibrate(TeamClassLoaderFactory factory) throws Exception {
        Fixture fixture=new Fixture(factory,"c_mend3",scenarios()[0]);
        Class<?> api=Class.forName("mendprobe.ApiCalibration",true,fixture.loader);
        RobotController rc=(RobotController)field(fixture.globals,"rc").get(null);
        String[] names={"shared","map","health","islands"};int[] expected={5,8,3,22},actual=new int[4];
        for(int i=0;i<names.length;i++) {
            fixture.budget(10000);
            if(names[i].equals("map")) method(api,names[i],RobotController.class,MapLocation.class).invoke(null,rc,HERE);
            else method(api,names[i],RobotController.class).invoke(null,rc);
            actual[i]=10000-fixture.remaining.getInt(null);
            if(fixture.debt.getInt(null)!=0)throw new IllegalStateException("calibration pending debt");
        }
        if(!Arrays.equals(actual,expected))throw new IllegalStateException("API calibration mismatch: "+Arrays.toString(actual));
        return actual;
    }
    static String quote(String value) {
        StringBuilder out=new StringBuilder("\"");
        for(char c:value.toCharArray()) {if(c=='\\'||c=='\"')out.append('\\');if(c<32)out.append(String.format("\\u%04x",(int)c));else out.append(c);}
        return out.append('"').toString();
    }
    static String decision(Result out) {
        return "{\"cost\":"+out.cost+",\"left\":"+out.left+",\"mending\":"+out.mending+",\"island\":"+out.id
            +",\"tile_loc12\":"+out.tile+",\"recheck_round\":"+out.check+",\"reads\":"+out.reads+",\"island_reads\":"+out.islandReads
            +",\"enemy_reads\":"+out.enemyReads+",\"fallback_started\":"+out.fallback+",\"min_fallback_api_left\":"+out.minFallbackApiLeft
            +",\"pending_debt\":"+out.debt+",\"initialization_cost_excluded\":"+out.initialization+"}";
    }
    static String traces(Result out) {
        StringBuilder rows=new StringBuilder("[");for(int[] row:out.readTrace){if(rows.length()>1)rows.append(',');rows.append(Arrays.toString(row));}return rows.append(']').toString();
    }
    public static void main(String[] args) throws Exception {
        if(args.length!=2)throw new IllegalArgumentException("MendCostProbe <private own classes> <result.json>");
        TeamClassLoaderFactory baseline=new TeamClassLoaderFactory(args[0]),candidate=new TeamClassLoaderFactory(args[0]);
        int[] calibration=calibrate(candidate);
        StringBuilder rows=new StringBuilder(),nominated=new StringBuilder(),inputs=new StringBuilder();
        for(Scenario scenario:scenarios()) {
            if(inputs.length()>0)inputs.append(',');
            inputs.append("{\"name\":").append(quote(scenario.name)).append(",\"islands\":").append(scenario.islands)
                .append(",\"visible_enemies\":").append(scenario.enemies?1:0).append(",\"health\":80,\"shared_slots\":")
                .append(Arrays.toString(scenario.shared)).append('}');
        }
        int cases=0,repeats=0,commonDifferences=0,fallbacks=0,reserveOvershoots=0,minLeft=10000;
        for(Scenario scenario:scenarios())for(int budget:BUDGETS) {
            Result base=new Fixture(baseline,"c_mend2",scenario).call(budget),arm=new Fixture(candidate,"c_mend3",scenario).call(budget);
            Result base2=new Fixture(baseline,"c_mend2",scenario).call(budget),arm2=new Fixture(candidate,"c_mend3",scenario).call(budget);
            if(!base.signature().equals(base2.signature())||!arm.signature().equals(arm2.signature()))repeats++;
            boolean same=base.id==arm.id && base.tile==arm.tile && base.mending==arm.mending && base.check==arm.check;
            if((scenario.name.equals("nearest_safe")||scenario.name.equals("visible_enemy_bypass"))
                &&(!same||base.reads!=arm.reads||base.islandReads!=arm.islandReads||base.enemyReads!=arm.enemyReads))commonDifferences++;
            if(arm.fallback) {fallbacks++;minLeft=Math.min(minLeft,arm.left);if(arm.left<6000)reserveOvershoots++;}
            String row="{\"scenario\":"+quote(scenario.name)+",\"entry_budget\":"+budget+",\"same_decision\":"+same
                +",\"baseline\":"+decision(base)+",\"candidate\":"+decision(arm)
                +",\"trace_fields\":[\"slot\",\"raw_left\",\"pending_debt\",\"effective_left\"],\"baseline_read_trace\":"+traces(base)
                +",\"candidate_read_trace\":"+traces(arm)+"}";
            if(cases++>0)rows.append(',');rows.append(row);
            if(budget==6000||budget==7500||budget==10000||arm.fallback&&arm.left<6000){if(nominated.length()>0)nominated.append(',');
                nominated.append("{\"scenario\":").append(quote(scenario.name)).append(",\"entry_budget\":").append(budget)
                    .append(",\"baseline\":").append(decision(base)).append(",\"candidate\":").append(decision(arm)).append('}');}
        }
        String summary="\"games_run\":0,\"cases\":"+cases+",\"repeated_measurement_differences\":"+repeats
            +",\"common_path_decision_differences\":"+commonDifferences+",\"fallback_cases\":"+fallbacks
            +",\"fallback_returns_below_6000\":"+reserveOvershoots+",\"minimum_fallback_return_left\":"+(fallbacks==0?-1:minLeft)
            +",\"api_calibration_shared_map_health_islands\":"+Arrays.toString(calibration);
        try(PrintWriter out=new PrintWriter(new OutputStreamWriter(new FileOutputStream(args[1]),"UTF-8"))){
            out.println("{"+summary+",\"width\":60,\"height\":60,\"round\":"+ROUND+",\"here_loc12\":"+encode(HERE)
                +",\"loc12\":\"x*64+y+1\",\"inputs\":["+inputs+"],\"rows\":["+rows+"]}");}
        System.out.println("{"+summary+",\"nominated_rows\":["+nominated+"]}");
        if(repeats!=0||commonDifferences!=0)System.exit(2);
    }
}
