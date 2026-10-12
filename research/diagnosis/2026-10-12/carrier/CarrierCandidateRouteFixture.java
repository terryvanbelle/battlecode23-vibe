package c_route1;

import battlecode.common.*;
import battlecode.instrumenter.inject.RobotMonitor;
import battlecode.server.*;
import battlecode.world.*;
import battlecode.world.control.NullControlProvider;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

/** Frozen own Nav/Carrier logic against native movement/occupancy/cooldowns.
 * Host calls are NOT instruction-metered; Clock is a synthetic guard input.
 * Field initialization and map knowledge are prescribed fixture states, not
 * claims about a selected field replay's hidden per-robot state. */
public final class CarrierCandidateRouteFixture {
    static final int ACTOR=12004;
    static final MapLocation START=new MapLocation(5,20);
    static int assertions;
    static final class Trial {
        final MapLocation goal;final String blockers,policy,fieldMode;final int waits,departureRound;final boolean partial,knownSymmetry;final int targetChangeRound;
        final List<Object> turns=new ArrayList<>(),blocked=new ArrayList<>();
        Trial(MapLocation goal,String blockers,int waits,String policy,boolean partial,String fieldMode){this(goal,blockers,waits,policy,partial,fieldMode,false,0);}
        Trial(MapLocation goal,String blockers,int waits,String policy,boolean partial,String fieldMode,boolean knownSymmetry){this(goal,blockers,waits,policy,partial,fieldMode,knownSymmetry,0);}
        Trial(MapLocation goal,String blockers,int waits,String policy,boolean partial,String fieldMode,boolean knownSymmetry,int targetChangeRound){this.goal=goal;this.blockers=blockers;this.waits=waits;this.policy=policy;this.partial=partial;this.fieldMode=fieldMode;this.knownSymmetry=knownSymmetry;this.targetChangeRound=targetChangeRound;this.departureRound=blockers.endsWith("release5")?5:blockers.endsWith("release9")?9:0;}
    }
    static final class Provider extends NullControlProvider {
        final Trial trial;final LiveMap map;GameWorld world;Throwable failure;boolean initialized,finished;
        Integer firstCollection,firstDeposit;int totalCollected,deposited;MapLocation depositHQ;
        Integer firstRecovery;MapLocation changedWell;boolean targetChanged;
        int nativeMoves;String phase;MapLocation turnOrigin;RobotController nativeRC;
        List<Object> moves;
        Provider(Trial t,LiveMap m){trial=t;map=m;}
        @Override public void matchStarted(GameWorld w){world=w;}
        @Override public void runRobot(InternalRobot robot) {
            if(robot.getID()!=ACTOR || finished)return;
            try {
                ampleBudget();nativeRC=robot.getController();
                if(world.getCurrentRound()==trial.departureRound)releaseBlockers();
                if(!initialized){initializeBot(nativeRC,map,trial.goal,trial.waits,trial.partial,trial.knownSymmetry);configureFieldMode(trial.fieldMode);initialized=true;}
                G.rc=observedController();G.startTurn();if(trial.partial)MapMem.scan();
                if(G.round==trial.targetChangeRound)changeTarget();
                turnOrigin=nativeRC.getLocation();nativeMoves=0;moves=new ArrayList<>();
                if(G.here.equals(Carrier.lastLoc))Carrier.stillTurns++;else{Carrier.stillTurns=0;Carrier.lastLoc=G.here;}
                boolean returning=nativeRC.getWeight()>=C.CARRIER_RETURN_LOAD || Carrier.returning;
                Map<String,Object> row=new LinkedHashMap<>();row.put("round",G.round);row.put("start",xy(turnOrigin));row.put("start_cd",nativeRC.getMovementCooldownTurns());row.put("start_weight",nativeRC.getWeight());row.put("returning",returning);
                row.put("start_wave",Field.level(turnOrigin.x,turnOrigin.y));row.put("still_turns",Carrier.stillTurns);
                row.put("start_well",Carrier.well==null?null:xy(Carrier.well));row.put("start_field_target",Field.target==null?null:xy(Field.target));
                row.put("start_field_on",Nav.fieldOn);row.put("start_field_epoch",Field.startRound);
                int recoveries=routeInt("routeRecoveries"),unjams=Carrier.unjams;
                if(returning){phase="deliver";Carrier.state='R';Carrier.deliver();}
                else{phase="gather";Carrier.gather();}
                if(routeInt("routeRecoveries")>recoveries && firstRecovery==null)firstRecovery=G.round;
                row.put("recovery_applied",routeInt("routeRecoveries")>0);row.put("no_progress",routeInt("routeWaits"));
                row.put("route_lock",routeLocation("routeLock"));row.put("route_memory_well",routeLocation("routeWell"));
                row.put("after_gather",xy(nativeRC.getLocation()));row.put("after_gather_cd",nativeRC.getMovementCooldownTurns());
                row.put("after_gather_ready",nativeRC.isMovementReady());row.put("after_gather_waits",Nav.fieldWaits);
                phase="unjam";Carrier.unjam();
                row.put("unjam_moved",Carrier.unjams>unjams);row.put("final",xy(nativeRC.getLocation()));
                row.put("final_cd",nativeRC.getMovementCooldownTurns());row.put("final_weight",nativeRC.getWeight());row.put("state",Character.toString(Carrier.state));row.put("moves",moves);
                row.put("end_well",Carrier.well==null?null:xy(Carrier.well));trial.turns.add(row);
                if(trial.partial)MapMem.process(1500);
                if(trial.fieldMode.equals("pending5") && G.round<=6)setBudget(1800);
                Field.think(1500);ampleBudget();
            } catch(Throwable t){failure=t;}
        }
        @SuppressWarnings("unchecked")
        void releaseBlockers() {
            // Controlled occupancy change: own bodies leave the tested patch.
            // Their relocation is not presented as a legal one-turn route.
            for(Object old:trial.blocked){List<Integer> p=(List<Integer>)old;InternalRobot body=world.getRobot(new MapLocation(p.get(0),p.get(1)));boolean relocated=false;
                for(int y=G.H-1;y>=0 && !relocated;y--)for(int x=G.W-1;x>=0;x--){MapLocation spare=new MapLocation(x,y);
                    if(map.getWallArray()[x+y*G.W] || map.getCurrentArray()[x+y*G.W]!=Direction.CENTER.ordinal() || world.getRobot(spare)!=null
                        || spare.distanceSquaredTo(START)<400 || spare.distanceSquaredTo(trial.goal)<400)continue;
                    body.setLocation(spare);relocated=true;break;
                }check(relocated,"own prescribed blocker relocated off tested route");
            }
        }
        void changeTarget() throws Exception {
            check(firstCollection==null,"controlled real-well change before first collection");
            int[] resources=map.getResourceArray();MapLocation old=Carrier.well;int type=resources[old.x+old.y*G.W];
            int distance=Integer.MAX_VALUE;MapLocation chosen=null;
            for(int p=0;p<resources.length;p++)if(resources[p]==type){MapLocation loc=new MapLocation(p%G.W,p/G.W);
                if(loc.equals(old))continue;int d=G.here.distanceSquaredTo(loc);if(d<distance){distance=d;chosen=loc;}}
            check(chosen!=null && world.getWell(chosen)!=null,"alternate well exists in native initial map and world");
            java.lang.reflect.Field count=MapMem.class.getDeclaredField("nSeenWell");count.setAccessible(true);count.setInt(null,0);
            MapMem.noteWell(chosen,type);Carrier.switchWell();
            check(chosen.equals(Carrier.well),"actual switchWell selects prescribed different real same-type well");
            changedWell=Carrier.well;targetChanged=true;
        }
        RobotController observedController() {
            return (RobotController)Proxy.newProxyInstance(RobotController.class.getClassLoader(),new Class<?>[]{RobotController.class},(proxy,method,args)->{
                if(method.getName().equals("move")) {
                    MapLocation before=nativeRC.getLocation();int cd=nativeRC.getMovementCooldownTurns();
                    Object result=invoke(method,args);nativeMoves++;
                    moves.add(Arrays.<Object>asList(phase,xy(before),xy(nativeRC.getLocation()),cd,nativeRC.getMovementCooldownTurns(),Nav.fieldWaits));
                    return result;
                }
                if(method.getName().equals("collectResource")){
                    int before=nativeRC.getWeight();Object result=invoke(method,args);
                    check(nativeRC.getWeight()>before,"actual gather native collection increased cargo");totalCollected+=nativeRC.getWeight()-before;
                    if(firstCollection==null)firstCollection=G.round;return result;
                }
                if(method.getName().equals("transferResource") && (Integer)args[2]>0){
                    int before=nativeRC.getWeight();ResourceType type=(ResourceType)args[1];MapLocation home=(MapLocation)args[0];
                    RobotInfo hqBefore=nativeRC.senseRobotAtLocation(home);int bank=hqBefore.getResourceAmount(type);
                    Object result=invoke(method,args);int amount=before-nativeRC.getWeight();
                    check(amount==(Integer)args[2],"native transfer emptied exact requested cargo");deposited+=amount;depositHQ=(MapLocation)args[0];
                    check(nativeRC.senseRobotAtLocation(home).getResourceAmount(type)==bank+amount,"native own HQ bank gained exact transfer");
                    if(nativeRC.getWeight()==0){check(deposited==30 && totalCollected==30,"completed actual 30kg route");firstDeposit=world.getCurrentRound();finished=true;}return result;
                }
                return invoke(method,args);
            });
        }
        Object invoke(Method method,Object[] args)throws Throwable {
            try{return method.invoke(nativeRC,args);}catch(InvocationTargetException e){throw e.getCause();}
        }
    }
    static void ampleBudget()throws Exception {
        setBudget(100000);
    }
    static void setBudget(int amount)throws Exception {
        java.lang.reflect.Field left=RobotMonitor.class.getDeclaredField("bytecodesLeft");left.setAccessible(true);
        left.setInt(null,amount);
        RobotMonitor.setBytecodeLimit(12500);
    }
    static void configureFieldMode(String mode) {
        if(mode.equals("complete"))return;
        Field.target=null;Field.vis=null;Field.nWaves=0;Field.pending=false;Field.done=false;Field.stale=false;
        Nav.fieldOn=false;Nav.fieldFor=null;Nav.bugging=false;
        if(mode.equals("pending5")){Field.request(Carrier.well,true);Nav.fieldOn=true;Nav.fieldFor=Carrier.well;}
        else if(!mode.equals("fresh"))throw new AssertionError("unknown field mode "+mode);
    }
    static void initializeBot(RobotController rc,LiveMap map,MapLocation goal,int waits,boolean partial,boolean knownSymmetry)throws Exception {
        G.init(rc);G.rc=rc;G.round=rc.getRoundNum();G.here=rc.getLocation();
        G.enemies=new RobotInfo[0];G.nearby=new RobotInfo[0];G.nEnemyFighters=G.nAllyFighters=0;
        int prescribedSym=map.getSymmetry()==MapSymmetry.ROTATIONAL?MapMem.ROT:map.getSymmetry()==MapSymmetry.HORIZONTAL?MapMem.FLIP_Y:MapMem.FLIP_X;
        MapMem.cand=knownSymmetry?prescribedSym:0;MapMem.decidedRound=knownSymmetry?G.round:-1;MapMem.nEnemyHQSeen=0;MapMem.tile=new char[G.W*G.H];Comms.canWrite=false;
        for(String name:new String[]{"lastScan","pending"}) {java.lang.reflect.Field f=MapMem.class.getDeclaredField(name);f.setAccessible(true);f.set(null,null);}
        for(String name:new String[]{"nSeenWell","nUnreported","pendingIdx"}) {java.lang.reflect.Field f=MapMem.class.getDeclaredField(name);f.setAccessible(true);f.setInt(null,0);}
        boolean[] walls=map.getWallArray(),clouds=map.getCloudArray();int[] currents=map.getCurrentArray();
        if(knownSymmetry){boolean compatible=true;for(int i=0;i<walls.length;i++){int x=i%G.W,y=i/G.W;int sx=prescribedSym==MapMem.FLIP_Y?x:G.W-1-x,sy=prescribedSym==MapMem.FLIP_X?y:G.H-1-y;compatible&=walls[i]==walls[sx+sy*G.W];}check(compatible,"prescribed resolved map symmetry matches actual static walls");}
        for(int i=0;i<walls.length;i++) {
            Direction d=Direction.DIRECTION_ORDER[currents[i]];
            MapMem.tile[i]=(char)((partial?0:1)|(partial?0:((walls[i]?2:0)|(clouds[i]?4:0)|(d==Direction.CENTER?0:(d.ordinal()+1)<<3))));
        }
        List<MapLocation> ours=new ArrayList<>();for(RobotInfo b:map.getInitialBodies())if(b.team==Team.A)ours.add(b.location);
        HQState.ourHQs=ours.toArray(new MapLocation[0]);
        Field.vis=null;Field.target=null;Field.nWaves=0;Field.usedRound=Field.startRound=-1000;Field.init();
        if(partial){MapMem.scan();MapMem.process(0);}else for(int p=0;p<walls.length;p++)if(walls[p])Field.addWall(p%G.W,p/G.W);
        Field.request(goal,true);Field.think(0);check(Field.ready(goal)&&Field.done,"prescribed full field ready");
        Nav.init();Nav.avoid=false;Nav.target=goal;Nav.fieldFor=goal;Nav.fieldOn=true;Nav.fieldWaits=waits;
        Nav.bugging=false;Nav.bugFlips=0;Nav.bestDist=Integer.MAX_VALUE;Nav.sinceBest=0;
        Carrier.lastLoc=null;Carrier.stillTurns=0;Carrier.unjams=0;Carrier.returning=false;Carrier.role=goal.equals(new MapLocation(9,21))?1:2;
        Carrier.well=goal;Carrier.wellType=Carrier.role;Carrier.trips=0;Carrier.crowdTurns=0;Carrier.searchTurns=0;Carrier.prevState='?';Carrier.state='?';Telemetry.init();resetRoute();
    }
    static List<Integer> xy(MapLocation p){return Arrays.asList(p.x,p.y);}
    static void round(GameWorld world,Provider provider,int expected) {
        GameState status=world.runRound();check(status==GameState.RUNNING && world.getCurrentRound()==expected,"native round advanced");
        if(provider.failure!=null)throw new AssertionError("owned fixture callback failed",provider.failure);
    }
    static Map<String,Object> run(Trial trial)throws Exception {
        LiveMap map=GameMapIO.loadMap("Forest",new File("/nonexistent-own-carrier-map-dir"),false);
        Provider provider=new Provider(trial,map);
        GameInfo info=new GameInfo("own-fixture-A","own.fixtureA",null,"own-fixture-B","own.fixtureB",null,new String[]{"Forest"},null,false);
        GameMaker maker=new GameMaker(info,null,false);maker.makeGameHeader();GameWorld world=new GameWorld(map,provider,maker.getMatchMaker());
        setRecovery(trial.policy.equals("enabled"));round(world,provider,1);world.spawnRobot(ACTOR,RobotType.CARRIER,START,Team.A);
        ampleBudget();initializeBot(world.getRobot(START).getController(),map,trial.goal,trial.waits,trial.partial,trial.knownSymmetry);
        int k=Field.level(START.x,START.y),nextID=20001;List<Object> neighbours=new ArrayList<>();
        for(Direction d:G.DIRS){MapLocation p=START.add(d);if(!G.onMap(p.x,p.y)||map.getWallArray()[p.x+p.y*G.W])continue;
            int level=Field.level(p.x,p.y);neighbours.add(Arrays.<Object>asList(xy(p),level));
            boolean block=trial.blockers.equals("down")&&level==k-1 || trial.blockers.startsWith("down_same")&&(level==k-1||level==k);
            if(block && world.getRobot(p)==null){world.spawnRobot(nextID++,RobotType.CARRIER,p,Team.A);trial.blocked.add(xy(p));}
        }
        for(int rn=2;rn<=241 && !provider.finished;rn++)round(world,provider,rn);
        Map<String,Object> out=new LinkedHashMap<>();out.put("goal",xy(trial.goal));out.put("blocker_mode",trial.blockers);
        out.put("initial_field_waits",trial.waits);out.put("blocker_departure_round",trial.departureRound);out.put("policy",trial.policy);out.put("field_initialization",trial.fieldMode);out.put("map_knowledge",trial.partial?"local_sensed_start":"prescribed_complete");
        out.put("prescribed_resolved_map_symmetry",trial.knownSymmetry?map.getSymmetry().name():null);
        out.put("start_wave",k);out.put("initial_neighbour_waves",neighbours);out.put("blocker_positions",trial.blocked);
        out.put("first_native_collection_round",provider.firstCollection);out.put("first_native_deposit_round",provider.firstDeposit);
        out.put("first_recovery_round",provider.firstRecovery);out.put("target_change_round",trial.targetChangeRound);out.put("actual_switchWell_executed",provider.targetChanged);out.put("changed_native_well",provider.changedWell==null?null:xy(provider.changedWell));
        out.put("native_total_collected",provider.totalCollected);out.put("native_deposited",provider.deposited);out.put("native_deposit_hq",provider.depositHQ==null?null:xy(provider.depositHQ));out.put("turns",trial.turns);return out;
    }
    static String json(Object o) {
        if(o==null)return"null";if(o instanceof Number||o instanceof Boolean)return o.toString();
        if(o instanceof String)return"\""+((String)o).replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n")+"\"";
        StringBuilder s=new StringBuilder();boolean first=true;
        if(o instanceof Map){s.append('{');for(Map.Entry<?,?> e:((Map<?,?>)o).entrySet()){if(!first)s.append(',');first=false;s.append(json(e.getKey())).append(':').append(json(e.getValue()));}return s.append('}').toString();}
        if(o instanceof Iterable){s.append('[');for(Object v:(Iterable<?>)o){if(!first)s.append(',');first=false;s.append(json(v));}return s.append(']').toString();}
        throw new IllegalArgumentException("JSON class "+o.getClass());
    }
    static void check(boolean ok,String message){assertions++;if(!ok)throw new AssertionError(message);}
    static int routeInt(String name)throws Exception {
        try{java.lang.reflect.Field f=Carrier.class.getDeclaredField(name);f.setAccessible(true);return f.getInt(null);}catch(NoSuchFieldException baseline){return 0;}
    }
    static Object routeLocation(String name)throws Exception {
        try{java.lang.reflect.Field f=Carrier.class.getDeclaredField(name);f.setAccessible(true);MapLocation p=(MapLocation)f.get(null);return p==null?null:xy(p);}catch(NoSuchFieldException baseline){return null;}
    }
    static void resetRoute()throws Exception {
        try{Method m=Carrier.class.getDeclaredMethod("routeReset");m.setAccessible(true);m.invoke(null);
            java.lang.reflect.Field f=Carrier.class.getDeclaredField("routeRecoveries");f.setAccessible(true);f.setInt(null,0);
        }catch(NoSuchMethodException baseline){}
    }
    static void setRecovery(boolean enabled)throws Exception {
        try{java.lang.reflect.Field f=C.class.getDeclaredField("CARRIER_ROUTE_RECOVERY");f.setAccessible(true);check(f.getBoolean(null)==enabled,"fixture mode matches privately compiled constant");}catch(NoSuchFieldException baseline){check(!enabled,"frozen source has no enabled candidate flag");}
    }
    @SuppressWarnings("unchecked")
    public static void main(String[] args)throws Exception {
        boolean baseline=args.length>0 && args[0].equals("baseline");
        String[] policies=baseline?new String[]{"baseline"}:new String[]{args.length>0?args[0]:"enabled"};
        List<Object> results=new ArrayList<>();
        for(boolean partial:new boolean[]{false,true})for(MapLocation goal:new MapLocation[]{new MapLocation(9,21),new MapLocation(8,12)})
            for(String blockers:new String[]{"none","down","down_same","down_same_release5","down_same_release9"})for(String policy:policies)
                results.add(run(new Trial(goal,blockers,blockers.startsWith("down_same")?2:0,policy,partial,"complete")));
        for(boolean partial:new boolean[]{false,true})for(MapLocation goal:new MapLocation[]{new MapLocation(9,21),new MapLocation(8,12)})
            for(String fieldMode:new String[]{"fresh","pending5"})for(String blockers:new String[]{"none","down_same"})for(String policy:policies)
                results.add(run(new Trial(goal,blockers,blockers.startsWith("down_same")?2:0,policy,partial,fieldMode)));
        for(MapLocation goal:new MapLocation[]{new MapLocation(9,21),new MapLocation(8,12)})
            for(String blockers:new String[]{"none","down_same"})for(String policy:policies)
                results.add(run(new Trial(goal,blockers,blockers.startsWith("down_same")?2:0,policy,true,"complete",true)));
        for(boolean partial:new boolean[]{false,true})for(MapLocation goal:new MapLocation[]{new MapLocation(9,21),new MapLocation(8,12)})
            for(int changeRound:new int[]{4,7})for(String policy:policies)
                results.add(run(new Trial(goal,"down_same",2,policy,partial,"complete",false,changeRound)));
        int targetChanges=0;
        for(Object result:results){Map<String,Object> c=(Map<String,Object>)result;if(Boolean.TRUE.equals(c.get("actual_switchWell_executed")))targetChanges++;}
        for(Object item:results){Map<String,Object> c=(Map<String,Object>)item;if(c.get("target_change_round").equals(0))continue;
            Map<String,Object> change=null;for(Object turn:(List<Object>)c.get("turns")){Map<String,Object> row=(Map<String,Object>)turn;if(row.get("round").equals(c.get("target_change_round")))change=row;}
            check(change!=null && c.get("changed_native_well").equals(change.get("start_well")),"actual switch becomes gather target in same native turn");
            check(change.get("route_lock")==null,"old actual target lock cleared after native switch");
            Object mw=change.get("route_memory_well");check(mw==null || mw.equals(change.get("start_well")),"route memory never retains old target after native switch");
            check((Integer)change.get("no_progress")==0,"native well change clears no-progress count");
        }
        Map<String,Object> out=new LinkedHashMap<>();out.put("registered_games_run",0);out.put("native_fixture_cases",results.size());out.put("source_mode",policies[0]);out.put("assertions",assertions);out.put("instruction_metered",false);
        out.put("native_target_change_paths_exercised",targetChanges);
        out.put("semantics",Arrays.asList("Native GameWorld movement, occupancy, cooldown, real wells and actual30kg HQ transfer; owned NullControlProvider only, no player sandbox or field opponent classes.",
            "Calls actual source Carrier.gather, deliver and unjam; observer proxy cannot veto or alter API behavior. Complete or initial local map knowledge and resolved symmetry are prescribed fixture states. Complete/fresh/pending fields and controlled permanent/transient own blockers are independent scenarios.",
            "Clock guard input is synthetic ample100000; host calls are not instruction-metered and this fixture does not establish bytecode costs or performance under real finite budgets.",
            "Native target-change scenarios call actual Carrier.switchWell at r4/r7 after prescribing an alternate same-type well from the native initial-map and world; collection and deposit use native controller calls. Old private replay targets are not inferred.",
            "release5/release9 relocate controlled own blockers off the tested patch; relocation is an occupancy condition, not a legal one-turn travel claim. Returning legs use actual deliver without an external routing policy."));
        out.put("results",results);System.out.println(json(out));
    }
}
