import battlecode.common.*;
import battlecode.instrumenter.TeamClassLoaderFactory;
import battlecode.server.*;
import battlecode.world.*;
import battlecode.world.control.NullControlProvider;
import java.lang.reflect.*;
import java.io.*;
import java.util.*;

/** Own instrumented methods over prescribed states and native Forest controllers.
 * Host setup/API implementation bodies are excluded; instrumented player instructions
 * and engine MethodCosts at their API call sites are charged. No player matches. */
public final class CarrierRouteCostProbe {
    static final int BIG=1000000, ROUND=320, ACTOR=12004;
    static final MapLocation START=new MapLocation(5,20), GOAL=new MapLocation(9,21);
    static int assertions;
    static final class BudgetStop extends RuntimeException {}
    static java.lang.reflect.Field f(Class<?> c,String n)throws Exception {java.lang.reflect.Field x=c.getDeclaredField(n);x.setAccessible(true);return x;}
    static Method m(Class<?> c,String n,Class<?>...a)throws Exception {Method x=c.getDeclaredMethod(n,a);x.setAccessible(true);return x;}
    static void set(Class<?> c,String n,Object v)throws Exception {f(c,n).set(null,v);}
    static int integer(Class<?> c,String n)throws Exception {try{return f(c,n).getInt(null);}catch(NoSuchFieldException old){return 0;}}
    static MapLocation location(Class<?> c,String n)throws Exception {try{return(MapLocation)f(c,n).get(null);}catch(NoSuchFieldException old){return null;}}
    static Object xy(MapLocation p){return p==null?null:Arrays.asList(p.x,p.y);}
    static void check(boolean value,String msg){assertions++;if(!value)throw new IllegalStateException(msg);}
    static final class Shape {
        final String name;final int longWave,lastK;
        Shape(String n){this(n,0,0);}Shape(String n,int w,int k){name=n;longWave=w;lastK=k;}
    }
    static final class Result {
        int cost,left,debt,initialization,pauses,minApiLeft=BIG;
        boolean completed;final List<Object> api=new ArrayList<>(),moves=new ArrayList<>();
        Map<String,Object> state;
        Map<String,Object> data(){Map<String,Object>x=new LinkedHashMap<>();x.put("charged_cost",completed?cost:null);x.put("return_raw_left",completed?left:null);x.put("pending_debt",completed?debt:null);x.put("paused_raw_left_observed",completed?null:left);x.put("paused_pending_debt_observed",completed?null:debt);x.put("completed",completed);x.put("pause_count",pauses);x.put("minimum_api_effective_left",minApiLeft==BIG?null:minApiLeft);x.put("class_initialization_cost_excluded",initialization);x.put("state",state);x.put("api_trace",api);x.put("native_moves",moves);return x;}
    }
    static final class Fixture {
        final ClassLoader loader;final Class<?> monitor,g,carrier,nav,field,mem;
        final java.lang.reflect.Field remaining,debt;final String pkg;final Shape shape;
        final LiveMap map;final GameWorld world;final InternalRobot actor;final RobotController nativeRC;
        int initialization;Result observation;MapLocation here;
        Fixture(TeamClassLoaderFactory factory,String pkg,Shape shape)throws Exception {
            this.pkg=pkg;this.shape=shape;loader=factory.createLoader(false);
            monitor=loader.loadClass("battlecode.instrumenter.inject.RobotMonitor");remaining=f(monitor,"bytecodesLeft");debt=f(monitor,"bytecodesToRemove");
            Class<?> pauser=Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Pauser"),killer=Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Killer");
            Object p=Proxy.newProxyInstance(pauser.getClassLoader(),new Class<?>[]{pauser},(o,m,a)->{if(observation!=null)observation.pauses++;throw new BudgetStop();});
            Object k=Proxy.newProxyInstance(killer.getClassLoader(),new Class<?>[]{killer},(o,m,a)->{throw new IllegalStateException("fixture robot killed");});
            monitor.getMethod("init",pauser,killer,int.class,Class.forName("battlecode.instrumenter.profiler.Profiler")).invoke(null,p,k,ACTOR,null);
            monitor.getMethod("setBytecodeLimit",int.class).invoke(null,12500);budget(BIG);
            g=Class.forName(pkg+".G",true,loader);carrier=Class.forName(pkg+".Carrier",true,loader);nav=Class.forName(pkg+".Nav",true,loader);
            field=Class.forName(pkg+".Field",true,loader);mem=Class.forName(pkg+".MapMem",true,loader);
            for(String name:new String[]{"C","Comms","Telemetry","HQState"})Class.forName(pkg+"."+name,true,loader);
            initialization=BIG-remaining.getInt(null);
            map=GameMapIO.loadMap("Forest",new File("/nonexistent-own-route-cost-maps"),false);
            GameInfo info=new GameInfo("own-cost-A","own.costA",null,"own-cost-B","own.costB",null,new String[]{"Forest"},null,false);
            GameMaker maker=new GameMaker(info,null,false);maker.makeGameHeader();world=new GameWorld(map,new NullControlProvider(),maker.getMatchMaker());
            check(world.runRound()==GameState.RUNNING,"native fixture initial round");
            here=START;
            if(shape.name.equals("near8"))for(int q=0;q<map.getResourceArray().length;q++){MapLocation p2=new MapLocation(q%map.getWidth(),q/map.getWidth());int d=p2.distanceSquaredTo(GOAL);if(d>2&&d<=8&&!map.getWallArray()[q]&&world.getRobot(p2)==null){here=p2;break;}}
            world.spawnRobot(ACTOR,RobotType.CARRIER,here,Team.A);actor=world.getRobot(here);actor.setMovementCooldownTurns(shape.name.equals("movement_not_ready")?10:0);nativeRC=actor.getController();
            if(shape.name.equals("temporary_bodies")||shape.name.startsWith("stall_enter")||shape.name.equals("locked")){
                int id=20001;for(MapLocation p2:new MapLocation[]{new MapLocation(5,21),new MapLocation(4,21),new MapLocation(4,20)})if(world.getRobot(p2)==null)world.spawnRobot(id++,RobotType.CARRIER,p2,Team.A);
            }
            RobotController observed=(RobotController)Proxy.newProxyInstance(RobotController.class.getClassLoader(),new Class<?>[]{RobotController.class},(o,method,args)->{
                if(observation!=null){int raw=remaining.getInt(null),pending=debt.getInt(null),effective=raw-pending;observation.minApiLeft=Math.min(observation.minApiLeft,effective);
                    observation.api.add(Arrays.<Object>asList(method.getName(),raw,pending,effective));}
                MapLocation before=method.getName().equals("move")?nativeRC.getLocation():null;int cd=before==null?0:nativeRC.getMovementCooldownTurns();
                try{Object answer=method.invoke(nativeRC,args);if(before!=null&&observation!=null)observation.moves.add(Arrays.<Object>asList(xy(before),xy(nativeRC.getLocation()),cd,nativeRC.getMovementCooldownTurns()));return answer;}
                catch(InvocationTargetException error){throw error.getCause();}
            });
            budget(BIG);m(g,"init",RobotController.class).invoke(null,observed);
            set(g,"here",here);set(g,"round",ROUND);set(g,"note","");set(g,"extra",",stale");
            set(g,"nearby",new RobotInfo[0]);set(g,"enemies",new RobotInfo[0]);
            set(mem,"cand",0);set(mem,"nEnemyHQSeen",0);set(mem,"nSeenWell",0);set(mem,"nUnreported",0);
            char[] tiles=new char[map.getWidth()*map.getHeight()];long[] walls=new long[map.getHeight()];
            for(int i=0;i<tiles.length;i++){Direction d=Direction.DIRECTION_ORDER[map.getCurrentArray()[i]];tiles[i]=(char)(1|(map.getWallArray()[i]?2:0)|(map.getCloudArray()[i]?4:0)|(d==Direction.CENTER?0:(d.ordinal()+1)<<3));if(map.getWallArray()[i])walls[i/map.getWidth()]|=1L<<(i%map.getWidth());}
            set(mem,"tile",tiles);set(field,"wall",walls);set(field,"full",(1L<<map.getWidth())-1);
            configureWaves();
            set(nav,"target",GOAL);set(nav,"fieldFor",shape.name.equals("nav_target_wrong")?new MapLocation(8,12):GOAL);set(nav,"fieldOn",!shape.name.equals("no_field"));
            set(nav,"fieldWaits",2);set(nav,"left",true);set(nav,"bugging",false);set(nav,"bestDist",Integer.MAX_VALUE);set(nav,"sinceBest",0);
            set(carrier,"well",GOAL);set(carrier,"wellType",1);set(carrier,"role",1);set(carrier,"state",'G');set(carrier,"crowdTurns",0);set(carrier,"returning",false);
            if(!pkg.equals("c_mend2")){
                m(carrier,"routeReset").invoke(null);set(carrier,"routeRecoveries",shape.name.equals("note_large")?Integer.MAX_VALUE:shape.name.equals("note_one")?1:0);
                if(shape.name.startsWith("stall_enter")||shape.name.equals("temporary_bodies")||shape.longWave!=0){set(carrier,"routeWell",GOAL);set(carrier,"routeField",GOAL);set(carrier,"routeEpoch",ROUND-10);set(carrier,"routeRound",ROUND-1);set(carrier,"routeBest",shape.longWave!=0?Math.max(0,shape.longWave):levelAt(here));set(carrier,"routeWaits",3);}
                if(shape.name.equals("locked")||shape.name.equals("lock_changed")){
                    set(carrier,"routeLock",shape.name.equals("lock_changed")?new MapLocation(8,12):GOAL);set(carrier,"routeRecoveries",1);
                }
            }
            if(shape.name.equals("locked")||shape.name.equals("lock_changed")){
                set(nav,"fieldOn",false);set(nav,"bugging",true);set(nav,"bugDir",here.directionTo(GOAL));set(nav,"bugStartDist",here.distanceSquaredTo(GOAL));set(nav,"bugStart",here);set(nav,"bugStartRound",ROUND-1);
            }
            budget(BIG);
        }
        int levelAt(MapLocation p)throws Exception {
            int n=integer(field,"nWaves");long[][] waves=(long[][])f(field,"waves").get(null);for(int i=0;i<n;i++)if((waves[i][p.y]&(1L<<p.x))!=0)return i;return-1;
        }
        void configureWaves()throws Exception {
            int w=map.getWidth(),h=map.getHeight();long[][] waves=new long[400][h];long[] vis=new long[h];int n;
            if(shape.longWave!=0){n=400;vis[here.y]|=1L<<here.x;if(shape.longWave>0)waves[shape.longWave][here.y]|=1L<<here.x;}
            else{int[] distance=new int[w*h];Arrays.fill(distance,-1);ArrayDeque<Integer> q=new ArrayDeque<>();distance[GOAL.x+GOAL.y*w]=0;q.add(GOAL.x+GOAL.y*w);int max=0;
                while(!q.isEmpty()){int p=q.remove();for(Direction d:Direction.DIRECTION_ORDER){int x=p%w+d.dx,y=p/w+d.dy;if(x<0||y<0||x>=w||y>=h)continue;int to=x+y*w;if(map.getWallArray()[to]||distance[to]>=0)continue;distance[to]=distance[p]+1;max=Math.max(max,distance[to]);q.add(to);}}
                for(int p=0;p<distance.length;p++)if(distance[p]>=0){waves[distance[p]][p/w]|=1L<<(p%w);vis[p/w]|=1L<<(p%w);}n=max+1;}
            if(shape.name.equals("invalid_vis"))vis[here.y]&=~(1L<<here.x);
            if(shape.name.equals("wave_missing")){for(long[] wave:waves)wave[here.y]&=~(1L<<here.x);vis[here.y]|=1L<<here.x;}
            set(field,"target",shape.name.equals("field_target_wrong")?new MapLocation(8,12):GOAL);set(field,"waves",waves);set(field,"vis",vis);set(field,"nWaves",shape.name.equals("no_field")?0:n);set(field,"lastK",shape.lastK);
            set(field,"startRound",ROUND-10);set(field,"done",true);set(field,"pending",false);set(field,"stale",false);
        }
        void budget(int amount)throws Exception {remaining.setInt(null,amount);debt.setInt(null,0);}
        Result call(String method,int amount)throws Exception {
            observation=new Result();budget(amount);boolean paused=false;
            try{if(method.equals("routeUpdate")||method.equals("moveTwice"))m(carrier,method,MapLocation.class).invoke(null,GOAL);else m(carrier,method).invoke(null);}
            catch(InvocationTargetException error){Throwable cause=error.getCause();if(cause instanceof BudgetStop)paused=true;else throw new IllegalStateException("actual instrumented method failed "+pkg+"/"+shape.name+"/"+method+"/"+amount,cause);}
            Result out=observation;observation=null;out.completed=!paused;out.left=remaining.getInt(null);out.debt=debt.getInt(null);out.cost=amount-out.left;out.initialization=initialization;
            if(out.completed)check(out.debt==0,"completed actual instrumented method must flush all pending debt");
            Map<String,Object> state=new LinkedHashMap<>();state.put("location",xy(nativeRC.getLocation()));state.put("movement_cd",nativeRC.getMovementCooldownTurns());state.put("weight",nativeRC.getWeight());state.put("field_lastK",integer(field,"lastK"));state.put("field_on",f(nav,"fieldOn").getBoolean(null));state.put("field_waits",integer(nav,"fieldWaits"));state.put("bugging",f(nav,"bugging").getBoolean(null));state.put("bug_dir",String.valueOf(f(nav,"bugDir").get(null)));state.put("state",String.valueOf(f(carrier,"state").get(null)));
            state.put("route_lock",xy(location(carrier,"routeLock")));state.put("route_well",xy(location(carrier,"routeWell")));state.put("route_waits",integer(carrier,"routeWaits"));state.put("route_recoveries",integer(carrier,"routeRecoveries"));state.put("note",f(g,"note").get(null));state.put("extra",f(g,"extra").get(null));out.state=state;return out;
        }
    }
    static Object decision(Result r){Map<String,Object>x=new LinkedHashMap<>(r.state);for(String n:new String[]{"route_lock","route_well","route_waits","route_recoveries"})x.remove(n);return Arrays.<Object>asList(r.completed,x,r.moves);}
    static String json(Object o){if(o==null)return"null";if(o instanceof Number||o instanceof Boolean)return o.toString();if(o instanceof String)return"\""+((String)o).replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n")+"\"";StringBuilder b=new StringBuilder();boolean first=true;if(o instanceof Map){b.append('{');for(Map.Entry<?,?>e:((Map<?,?>)o).entrySet()){if(!first)b.append(',');first=false;b.append(json(e.getKey())).append(':').append(json(e.getValue()));}return b.append('}').toString();}if(o instanceof Iterable){b.append('[');for(Object e:(Iterable<?>)o){if(!first)b.append(',');first=false;b.append(json(e));}return b.append(']').toString();}throw new IllegalArgumentException(o.getClass().toString());}
    static Map<String,Object> calibrate(TeamClassLoaderFactory factory)throws Exception {
        Fixture x=new Fixture(factory,"c_route1",new Shape("normal"));Class<?> api=Class.forName("RouteCostApiCalibration",true,x.loader);
        RobotController rc=(RobotController)f(x.g,"rc").get(null);String[] names={"shared","map","ready","location","weight","canMove","move"};int[] expected={5,8,3,3,12,13,3};Map<String,Object> out=new LinkedHashMap<>();
        for(int i=0;i<names.length;i++){x.budget(10000);
            if(names[i].equals("map"))m(api,names[i],RobotController.class,MapLocation.class).invoke(null,rc,START);
            else if(names[i].equals("canMove")||names[i].equals("move"))m(api,names[i],RobotController.class,Direction.class).invoke(null,rc,Direction.NORTH);
            else m(api,names[i],RobotController.class).invoke(null,rc);
            int cost=10000-x.remaining.getInt(null);check(cost==expected[i]&&x.debt.getInt(null)==0,"instrumented API call-site calibration "+names[i]+"="+cost);out.put(names[i],cost);
        }return out;
    }
    public static void main(String[] args)throws Exception {
        if(args.length!=2)throw new IllegalArgumentException("CarrierRouteCostProbe <private own classes> <result.json>");
        TeamClassLoaderFactory factory=new TeamClassLoaderFactory(args[0]);Map<String,Object> calibration=calibrate(factory);List<Object> rows=new ArrayList<>();int repeatDrift=0,zeroDrift=0,completed=0,pauses=0;
        Shape[] update={new Shape("normal"),new Shape("normal_cached",0,14),new Shape("no_field"),new Shape("near8"),new Shape("movement_not_ready"),new Shape("field_target_wrong"),new Shape("nav_target_wrong"),new Shape("invalid_vis"),new Shape("wave_missing"),new Shape("stall_enter"),new Shape("stall_enter_cached",0,14),new Shape("locked"),new Shape("lock_changed"),new Shape("temporary_bodies"),new Shape("long120_cache0",120,0),new Shape("long399_cache0",399,0),new Shape("long399_cache200",399,200),new Shape("long399_cache399",399,399),new Shape("long_missing_cache0",-1,0),new Shape("long_missing_cache200",-1,200),new Shape("long_missing_cache399",-1,399)};
        Shape[] travel={new Shape("normal"),new Shape("normal_cached",0,14),new Shape("no_field"),new Shape("movement_not_ready"),new Shape("stall_enter"),new Shape("stall_enter_cached",0,14),new Shape("locked"),new Shape("temporary_bodies"),new Shape("long120_cache0",120,0),new Shape("long399_cache0",399,0),new Shape("long399_cache200",399,200),new Shape("long399_cache399",399,399),new Shape("long_missing_cache0",-1,0),new Shape("long_missing_cache200",-1,200),new Shape("long_missing_cache399",-1,399)};
        String[] modes={"c_mend2","c_route0","c_route1"};
        for(String method:new String[]{"routeUpdate","gather","moveTwice","note"}){
            Shape[] shapes=method.equals("routeUpdate")?update:method.equals("note")?new Shape[]{new Shape("note_zero"),new Shape("note_one"),new Shape("note_large")}:travel;
            int[] budgets=method.equals("routeUpdate")?new int[]{0,50,600,6499,6500,6501,6525,6550,6575,6600,7000,10000,12500,100000}:method.equals("note")?new int[]{0,50,500,599,600,601,620,625,626,627,628,629,630,650,700,800,1000}:new int[]{2000,6499,6500,6600,7000,10000,12500};
            for(Shape shape:shapes)for(int budget:budgets){Result base=null,zero=null;
                for(String pkg:method.equals("routeUpdate")?new String[]{"c_route1"}:modes){
                    Result a=new Fixture(factory,pkg,shape).call(method,budget),b=new Fixture(factory,pkg,shape).call(method,budget);
                    if(!json(a.data()).equals(json(b.data())))repeatDrift++;
                    if(a.completed)completed++;else pauses++;
                    Map<String,Object> row=new LinkedHashMap<>();row.put("method",method);row.put("shape",shape.name);row.put("package",pkg);row.put("method_entry_budget",budget);row.put("long_wave",shape.longWave);row.put("initial_lastK",shape.lastK);row.put("result",a.data());rows.add(row);
                    if(pkg.equals("c_mend2"))base=a;if(pkg.equals("c_route0")){zero=a;if(!decision(base).equals(decision(zero))||base.cost!=zero.cost||base.debt!=zero.debt||base.initialization!=zero.initialization||!base.api.equals(zero.api))zeroDrift++;}
                }
            }
        }
        Map<String,Object> out=new LinkedHashMap<>();out.put("api_callsite_calibration",calibration);out.put("registered_games_run",0);out.put("instruction_metered",true);out.put("cases",rows.size());out.put("assertions",assertions);out.put("repeated_measurement_differences",repeatDrift);out.put("zero_arm_differences",zeroDrift);out.put("completed_cases",completed);out.put("paused_cases",pauses);
        out.put("semantics",Arrays.asList("Own actual compiled classes instrumented by TeamClassLoaderFactory; monitor budget sets the real method-entry instruction allowance and calls are then charged by the engine instrumenter. No reflected allowance is used as a substitute for instruction metering.","Native Forest movement readiness, legality, occupancy and cooldowns through an observing controller proxy; host API bodies/setup/class initialization are excluded, player instructions and engine API call-site charges are included.","routeUpdate is measured directly only for enabled candidate; baseline has no such method. gather, moveTwice and note compare frozen baseline, privately compiled disabled flag and actual enabled candidate.","Full G.startTurn, Carrier.run survival/anchor/scout/census, map scan, unjam, note after travel, indicator composition and background tail/Field.think are excluded. This is method price, not full-turn cost or game value.","400-wave late/missing lookups are prescribed synthetic field states that stress the current Field.level bound, not claims of geometry or hidden field state in a replay. Native Forest BFS fields supply the ordinary shapes.","0/low-entry probes may pause before the method can reach its guards; they are reported explicitly. Completed returns must have pending debt0; paused paths retain the observed debt and are never presented as safe complete execution.","API snapshots record raw remaining, cumulative pending debt and effective remaining=raw-pending before the unmetered native API implementation body; pending debt is not cleared at callbacks."));
        out.put("rows",rows);try(PrintWriter p=new PrintWriter(new OutputStreamWriter(new FileOutputStream(args[1]),"UTF-8"))){p.println(json(out));}
        Map<String,Object> summary=new LinkedHashMap<>(out);summary.remove("rows");System.out.println(json(summary));
        check(repeatDrift==0,"instrumented cost/decision repeat drift");check(zeroDrift==0,"disabled actual methods differ from frozen baseline");
    }
}

/** Separately loaded own calibration class; the enclosing host file is never instrumented. */
final class RouteCostApiCalibration {
    public static int shared(RobotController rc)throws GameActionException{return rc.readSharedArray(5);}
    public static boolean map(RobotController rc,MapLocation p){return rc.onTheMap(p);}
    public static boolean ready(RobotController rc){return rc.isMovementReady();}
    public static MapLocation location(RobotController rc){return rc.getLocation();}
    public static int weight(RobotController rc){return rc.getWeight();}
    public static boolean canMove(RobotController rc,Direction d){return rc.canMove(d);}
    public static void move(RobotController rc,Direction d)throws GameActionException{rc.move(d);}
}
