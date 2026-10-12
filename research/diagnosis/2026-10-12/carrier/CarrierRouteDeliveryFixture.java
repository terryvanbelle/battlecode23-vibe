package c_mend2;

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
public final class CarrierRouteDeliveryFixture {
    static final int ACTOR=12004;
    static final MapLocation START=new MapLocation(5,20);
    static int assertions;
    static final class RouteMemory {
        MapLocation well,fieldTarget;int epoch,lastRound=-1,best=Integer.MAX_VALUE,waited;
        void clear(){well=fieldTarget=null;epoch=lastRound=-1;best=Integer.MAX_VALUE;waited=0;}
        int tick(MapLocation w,MapLocation ft,int e,int round,int wave,boolean eligible){
            if(!eligible || w==null || ft==null || !w.equals(ft) || wave<0){clear();return 0;}
            if(!w.equals(well) || !ft.equals(fieldTarget) || epoch!=e){clear();well=w;fieldTarget=ft;epoch=e;}
            if(lastRound==round)return waited;lastRound=round;
            if(wave<best){best=wave;waited=0;}else waited++;return waited;
        }
    }
    static final class Trial {
        final MapLocation goal;final String blockers,policy,fieldMode;final int waits,departureRound;final boolean avoidReturn,partial,knownSymmetry;
        final List<Object> turns=new ArrayList<>(),blocked=new ArrayList<>();
        Trial(MapLocation goal,String blockers,int waits,String policy,boolean partial,String fieldMode){this(goal,blockers,waits,policy,partial,fieldMode,false);}
        Trial(MapLocation goal,String blockers,int waits,String policy,boolean partial,String fieldMode,boolean knownSymmetry){this.goal=goal;this.blockers=blockers;this.waits=waits;this.policy=policy;this.partial=partial;this.fieldMode=fieldMode;this.knownSymmetry=knownSymmetry;this.avoidReturn=policy.equals("no_second_return");this.departureRound=blockers.endsWith("release5")?5:blockers.endsWith("release9")?9:0;}
    }
    static final class Provider extends NullControlProvider {
        final Trial trial;final LiveMap map;GameWorld world;Throwable failure;boolean initialized,finished;
        Integer firstCollection,firstDeposit;int totalCollected,deposited;MapLocation depositHQ;
        final RouteMemory memory=new RouteMemory();int noProgress,tabooUntil;boolean recovered,routeLocked;MapLocation taboo;
        int nativeMoves,returnVetoes;String phase;MapLocation turnOrigin;RobotController nativeRC;
        List<Object> moves;
        Provider(Trial t,LiveMap m){trial=t;map=m;}
        @Override public void matchStarted(GameWorld w){world=w;}
        @Override public void runRobot(InternalRobot robot) {
            if(robot.getID()!=ACTOR || finished)return;
            try {
                ampleBudget();nativeRC=robot.getController();
                if(world.getCurrentRound()==trial.departureRound)releaseBlockers();
                if(!initialized){initializeBot(nativeRC,map,trial.goal,trial.waits,trial.partial,trial.knownSymmetry);configureFieldMode(trial.fieldMode);initialized=true;}
                G.rc=observedController();G.startTurn();if(trial.partial)MapMem.scan();turnOrigin=nativeRC.getLocation();nativeMoves=0;returnVetoes=0;moves=new ArrayList<>();
                if(G.here.equals(Carrier.lastLoc))Carrier.stillTurns++;else{Carrier.stillTurns=0;Carrier.lastLoc=G.here;}
                boolean returning=nativeRC.getWeight()>=30 || Carrier.returning;Carrier.state=returning?'R':'G';int wave=Field.level(turnOrigin.x,turnOrigin.y);
                boolean lockedPolicy=trial.policy.equals("bug_still_lock") || trial.policy.equals("bug_wave_lock");
                boolean eligible=!returning && turnOrigin.distanceSquaredTo(trial.goal)>(lockedPolicy?8:2) && nativeRC.isMovementReady()
                    && Nav.fieldOn && trial.goal.equals(Nav.fieldFor) && Field.ready(trial.goal) && wave>=0 && Clock.getBytecodesLeft()>C.FIELD_LEVEL_GUARD;
                noProgress=memory.tick(trial.goal,Field.target,Field.startRound,G.round,wave,eligible);
                boolean trigger=trial.policy.equals("bug_still_lock")?Carrier.stillTurns>=4:noProgress>=4;
                if(eligible && !recovered && trigger && !trial.policy.equals("none") && !trial.policy.equals("no_second_return"))recover();
                Map<String,Object> row=new LinkedHashMap<>();row.put("recovery_applied",recovered);row.put("no_progress",noProgress);row.put("trigger_eligible",eligible);
                row.put("round",world.getCurrentRound());row.put("start",xy(turnOrigin));row.put("start_cd",nativeRC.getMovementCooldownTurns());row.put("start_weight",nativeRC.getWeight());row.put("returning",returning);
                row.put("start_wave",Field.level(turnOrigin.x,turnOrigin.y));row.put("still_turns",Carrier.stillTurns);
                phase="moveTwice";
                if(returning){routeLocked=false;phase="deliver";Carrier.deliver();}
                else if(nativeRC.getLocation().distanceSquaredTo(trial.goal)>2)moveToWell();
                MapLocation after=nativeRC.getLocation();
                row.put("after_moveTwice",xy(after));row.put("moveTwice_cd",nativeRC.getMovementCooldownTurns());
                row.put("moveTwice_ready",nativeRC.isMovementReady());row.put("moveTwice_waits",Nav.fieldWaits);
                row.put("second_return_vetoes",returnVetoes);int unjams=Carrier.unjams;
                if(!returning && after.distanceSquaredTo(trial.goal)<=2) {
                    routeLocked=false;Carrier.state='C';
                    while(nativeRC.isActionReady() && nativeRC.getWeight()<30){
                        int before=nativeRC.getWeight(),room=30-before;
                        if(nativeRC.canCollectResource(trial.goal,-1))nativeRC.collectResource(trial.goal,-1);
                        else if(nativeRC.canCollectResource(trial.goal,room))nativeRC.collectResource(trial.goal,room);else break;
                        check(nativeRC.getWeight()>before,"native collection increased cargo");totalCollected+=nativeRC.getWeight()-before;
                        if(firstCollection==null)firstCollection=world.getCurrentRound();
                    }
                    if(nativeRC.getWeight()>=30)Carrier.returning=true;
                }
                phase="unjam";Carrier.unjam();
                row.put("unjam_moved",Carrier.unjams>unjams);row.put("final",xy(nativeRC.getLocation()));
                row.put("final_cd",nativeRC.getMovementCooldownTurns());row.put("final_weight",nativeRC.getWeight());row.put("moves",moves);trial.turns.add(row);
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
        void recover() throws Exception {
            recovered=true;
            if(trial.policy.equals("taboo_origin")){taboo=turnOrigin;tabooUntil=world.getCurrentRound()+8;return;}
            if(trial.policy.equals("bug_keep") || trial.policy.equals("bug_flip") || trial.policy.equals("bug_still_lock") || trial.policy.equals("bug_wave_lock")) {
                Nav.fieldOn=false;Nav.target=trial.goal;Nav.bugging=true;Nav.bugDir=turnOrigin.directionTo(trial.goal);
                Nav.bugStartDist=Nav.score(turnOrigin,trial.goal);Nav.bugMoves=0;Nav.bugFlips=0;
                Nav.bugStart=turnOrigin;Nav.bugStartRound=G.round;Nav.bugEpMoves=0;
                routeLocked=trial.policy.equals("bug_still_lock") || trial.policy.equals("bug_wave_lock");
                if(trial.policy.equals("bug_flip"))Nav.left=!Nav.left;return;
            }
            if(trial.policy.equals("rebuild_blockers")) {
                long[] staticWall=Field.wall;Field.wall=staticWall.clone();
                for(RobotInfo body:nativeRC.senseNearbyRobots())if(body.ID!=ACTOR)Field.wall[body.location.y]|=1L<<body.location.x;
                Field.target=null;Field.vis=null;Field.nWaves=0;Field.request(trial.goal,true);Field.think(0);Field.wall=staticWall;
                Nav.fieldOn=true;Nav.fieldFor=trial.goal;Nav.bugging=false;Nav.fieldWaits=0;return;
            }
            throw new AssertionError("unknown recovery policy "+trial.policy);
        }
        void moveToWell() throws GameActionException {
            if(!routeLocked){Carrier.moveTwice(trial.goal);return;}
            // Counterfactual is confined to this carrier's gather leg. Clear
            // fieldOn before BOTH own Nav calls so a wall hit cannot reactivate
            // the stale distance field halfway through a double move.
            Nav.fieldOn=false;Nav.moveTo(trial.goal);
            Nav.fieldOn=false;if(G.rc.isMovementReady() && G.rc.getLocation().distanceSquaredTo(trial.goal)>2)Nav.moveTo(trial.goal);
            Nav.fieldOn=false;
        }
        RobotController observedController() {
            return (RobotController)Proxy.newProxyInstance(RobotController.class.getClassLoader(),new Class<?>[]{RobotController.class},(proxy,method,args)->{
                if(method.getName().equals("canMove") && taboo!=null && world.getCurrentRound()<tabooUntil && nativeRC.getLocation().add((Direction)args[0]).equals(taboo) && nativeRC.canMove((Direction)args[0])) {returnVetoes++;return false;}
                if(method.getName().equals("canMove") && trial.avoidReturn && "moveTwice".equals(phase) && nativeMoves>0) {
                    Direction d=(Direction)args[0];
                    if(nativeRC.getLocation().add(d).equals(turnOrigin) && nativeRC.canMove(d)){returnVetoes++;return false;}
                }
                if(method.getName().equals("move")) {
                    MapLocation before=nativeRC.getLocation();int cd=nativeRC.getMovementCooldownTurns();
                    Object result=invoke(method,args);nativeMoves++;
                    moves.add(Arrays.<Object>asList(phase,xy(before),xy(nativeRC.getLocation()),cd,nativeRC.getMovementCooldownTurns(),Nav.fieldWaits));
                    return result;
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
        Carrier.well=goal;Carrier.wellType=Carrier.role;Carrier.trips=0;Carrier.crowdTurns=0;Telemetry.init();
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
        round(world,provider,1);world.spawnRobot(ACTOR,RobotType.CARRIER,START,Team.A);
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
    @SuppressWarnings("unchecked")
    static List<Object> movementRows(Map<String,Object> result) {
        List<Object> rows=new ArrayList<>();for(Object item:(List<Object>)result.get("turns")) {
            Map<String,Object> row=new LinkedHashMap<>((Map<String,Object>)item);
            row.remove("second_return_vetoes");row.remove("recovery_applied");row.remove("no_progress");row.remove("trigger_eligible");rows.add(row);
        }return rows;
    }
    @SuppressWarnings("unchecked")
    public static void main(String[] args)throws Exception {
        testRouteMemory();
        List<Object> results=new ArrayList<>();
        String[] policies={"none","no_second_return","taboo_origin","bug_keep","bug_flip","rebuild_blockers","bug_still_lock","bug_wave_lock"};
        for(boolean partial:new boolean[]{false,true})for(MapLocation goal:new MapLocation[]{new MapLocation(9,21),new MapLocation(8,12)})
            for(String blockers:new String[]{"none","down","down_same","down_same_release5","down_same_release9"})for(String policy:policies)
                results.add(run(new Trial(goal,blockers,blockers.startsWith("down_same")?2:0,policy,partial,"complete")));
        for(boolean partial:new boolean[]{false,true})for(MapLocation goal:new MapLocation[]{new MapLocation(9,21),new MapLocation(8,12)})
            for(String fieldMode:new String[]{"fresh","pending5"})for(String blockers:new String[]{"none","down_same"})for(String policy:policies)
                results.add(run(new Trial(goal,blockers,blockers.startsWith("down_same")?2:0,policy,partial,fieldMode)));
        for(MapLocation goal:new MapLocation[]{new MapLocation(9,21),new MapLocation(8,12)})
            for(String blockers:new String[]{"none","down_same"})for(String policy:policies)
                results.add(run(new Trial(goal,blockers,blockers.startsWith("down_same")?2:0,policy,true,"complete",true)));
        int common=0,firstDetours=0,preTrigger=0,completeCommon=0;List<Object> changedPaths=new ArrayList<>();
        for(int i=0;i<results.size();i+=policies.length) {
            Map<String,Object> old=(Map<String,Object>)results.get(i);
            for(int j=1;j<policies.length;j++) {
                Map<String,Object> fix=(Map<String,Object>)results.get(i+j);
                Map<String,Object> a=(Map<String,Object>)((List<Object>)old.get("turns")).get(0);
                Map<String,Object> b=(Map<String,Object>)((List<Object>)fix.get("turns")).get(0);
                check(((List<Object>)a.get("moves")).get(0).equals(((List<Object>)b.get("moves")).get(0)),"first legal detour preserved");firstDetours++;
                List<Object> oldRows=movementRows(old),fixRows=movementRows(fix);
                if(!fix.get("policy").equals("no_second_return")) {
                    List<Object> turnRows=(List<Object>)fix.get("turns");int limit=0;
                    while(limit<turnRows.size() && !Boolean.TRUE.equals(((Map<String,Object>)turnRows.get(limit)).get("recovery_applied")))limit++;
                    check(oldRows.size()>=limit && oldRows.subList(0,limit).equals(fixRows.subList(0,limit)),"movement/cooldown/unjam unchanged before recovery trigger");preTrigger++;
                }
                if(oldRows.equals(fixRows))common++;
                else {
                    Map<String,Object> delta=new LinkedHashMap<>();delta.put("goal",old.get("goal"));delta.put("map_knowledge",old.get("map_knowledge"));
                    delta.put("blocker_mode",old.get("blocker_mode"));delta.put("policy",fix.get("policy"));delta.put("field_initialization",old.get("field_initialization"));delta.put("prescribed_resolved_map_symmetry",old.get("prescribed_resolved_map_symmetry"));int at=0;
                    while(at<oldRows.size() && at<fixRows.size() && oldRows.get(at).equals(fixRows.get(at)))at++;
                    delta.put("first_changed_turn_index",at);delta.put("control",at<oldRows.size()?oldRows.get(at):null);delta.put("variant",at<fixRows.size()?fixRows.get(at):null);changedPaths.add(delta);
                }
                if(old.get("field_initialization").equals("complete") && old.get("map_knowledge").equals("prescribed_complete") && !((String)old.get("blocker_mode")).startsWith("down_same")) {
                    check(oldRows.equals(fixRows),"complete-map common native movement/cooldown/unjam path preserved: "+old.get("goal")+"/"+old.get("blocker_mode")+"/"+fix.get("policy"));completeCommon++;
                }
            }
        }
        Map<String,Object> out=new LinkedHashMap<>();out.put("registered_games_run",0);out.put("native_fixture_cases",results.size());
        out.put("assertions",assertions);out.put("instruction_metered",false);
        out.put("first_detour_preservation_pairs",firstDetours);out.put("common_decision_path_identity_pairs",common);
        out.put("pre_trigger_decision_path_identity_pairs",preTrigger);
        out.put("complete_open_down_decision_path_identity_pairs",completeCommon);out.put("route_memory_selfchecks",14);out.put("native_target_change_paths_exercised",false);
        out.put("changed_decision_paths",changedPaths);
        out.put("semantics",Arrays.asList("Native move legality, occupancy, cooldown and end-round physics; owned NullControlProvider only, no player sandbox or field opponent classes.",
            "Frozen c_mend2 Nav/Carrier moveTwice and deliver methods with controlled fixed well choice, stationary own blockers and native 30kg collection/transfer. Complete static knowledge or initial local vision are prescribed. Initial field modes cover completed active, fresh greedy and pending field work withheld through r6. Subsequent local scans occur before moves and processing/field work at turn end with the production 1500 reserve and synthetic budget. Explicit resolved-symmetry cases prescribe the native map symmetry after validating its wall geometry; all others disable symmetry inference. No replay private field state is inferred.",
            "Clock guard input is synthetic ample100000; host calls are not charged and no budget performance claim is made.",
            "Recovery policies trigger once on an eligible gather leg after four starts without a new best field wave, except bug_still_lock uses four identical start locations. Both bug_still_lock and bug_wave_lock apply outside distance squared 8 and suppress field use before both gather-leg Nav calls until collection radius. Returning, collecting, invalid/inactive fields and movement-not-ready turns cannot trigger. Return movement uses frozen deliver with no remedy; native 30kg deposit determines route completion.",
            "release5/release9 cases prescribe own blockers leaving the tested patch before/after the initial r6 trigger opportunity; their off-route relocation is a controlled occupancy change, not a claim of legal one-turn travel.",
            "Rows trace native in-turn moves; field replay endpoints cannot establish that their actors took these same steps."));
        out.put("results",results);System.out.println(json(out));
    }
    static void testRouteMemory() {
        RouteMemory m=new RouteMemory();MapLocation a=new MapLocation(9,21),b=new MapLocation(8,12);
        check(m.tick(a,a,2,2,14,true)==0,"initial valid wave resets");
        check(m.tick(a,a,2,3,14,true)==1,"one eligible stagnant round");
        check(m.tick(a,a,2,3,14,true)==1,"duplicate round is not counted");
        check(m.tick(a,a,2,4,13,true)==0,"new best wave resets");
        check(m.tick(a,a,2,5,13,true)==1,"same wave counts");
        check(m.tick(a,a,2,6,14,true)==2,"back wave counts");
        check(m.tick(a,a,2,7,14,true)==3,"stagnation persists");
        check(m.tick(a,a,2,8,13,true)==4,"four rounds without new best");
        check(m.tick(b,b,2,9,8,true)==0,"exact changed target resets even same field start round");
        check(m.tick(b,b,3,10,8,true)==0,"new field epoch resets");
        check(m.tick(b,a,3,11,8,true)==0 && m.well==null,"nearby different field cannot count");
        check(m.tick(b,b,3,12,-1,true)==0 && m.best==Integer.MAX_VALUE,"invalid wave cannot poison best");
        check(m.tick(b,b,3,13,8,false)==0 && m.well==null,"ineligible phase/cooldown/field cannot count");
        check(m.tick(b,b,3,14,8,true)==0,"valid route after gap starts fresh");
    }
}
