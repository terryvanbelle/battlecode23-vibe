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
 * Host calls are NOT instruction-metered. Clock=100000 is a synthetic ample
 * guard input. Complete static field knowledge is a prescribed fixture, not
 * a claim about the selected field replay's hidden per-robot map state. */
public final class CarrierCancellationFixture {
    static final int ACTOR=12004;
    static final MapLocation START=new MapLocation(5,20);
    static int assertions;
    static final class Trial {
        final MapLocation goal;final String blockers;final int waits;final boolean avoidReturn;
        final List<Object> turns=new ArrayList<>(),blocked=new ArrayList<>();
        Trial(MapLocation goal,String blockers,int waits,boolean avoidReturn){this.goal=goal;this.blockers=blockers;this.waits=waits;this.avoidReturn=avoidReturn;}
    }
    static final class Provider extends NullControlProvider {
        final Trial trial;final LiveMap map;GameWorld world;Throwable failure;boolean initialized,finished;
        Integer firstCollection;
        int nativeMoves,returnVetoes;String phase;MapLocation turnOrigin;RobotController nativeRC;
        List<Object> moves;
        Provider(Trial t,LiveMap m){trial=t;map=m;}
        @Override public void matchStarted(GameWorld w){world=w;}
        @Override public void runRobot(InternalRobot robot) {
            if(robot.getID()!=ACTOR || finished)return;
            try {
                ampleBudget();nativeRC=robot.getController();
                if(!initialized){initializeBot(nativeRC,map,trial.goal,trial.waits);initialized=true;}
                G.rc=observedController();G.startTurn();turnOrigin=nativeRC.getLocation();nativeMoves=0;returnVetoes=0;moves=new ArrayList<>();
                if(G.here.equals(Carrier.lastLoc))Carrier.stillTurns++;else{Carrier.stillTurns=0;Carrier.lastLoc=G.here;}
                Carrier.state='G';Map<String,Object> row=new LinkedHashMap<>();
                row.put("round",world.getCurrentRound());row.put("start",xy(turnOrigin));row.put("start_cd",nativeRC.getMovementCooldownTurns());
                row.put("start_wave",Field.level(turnOrigin.x,turnOrigin.y));row.put("still_turns",Carrier.stillTurns);
                phase="moveTwice";Carrier.moveTwice(trial.goal);MapLocation after=nativeRC.getLocation();
                row.put("after_moveTwice",xy(after));row.put("moveTwice_cd",nativeRC.getMovementCooldownTurns());
                row.put("moveTwice_ready",nativeRC.isMovementReady());row.put("moveTwice_waits",Nav.fieldWaits);
                row.put("second_return_vetoes",returnVetoes);int unjams=Carrier.unjams;
                // gather() changes to C inside the collection footprint before
                // its caller's unjam. Stop on one native collection to avoid
                // forcing G/unjam onto an already-arrived collector.
                if(after.distanceSquaredTo(trial.goal)<=2) {
                    Carrier.state='C';check(nativeRC.canCollectResource(trial.goal,1),"native well reached and collectible");
                    nativeRC.collectResource(trial.goal,1);firstCollection=world.getCurrentRound();finished=true;
                }
                phase="unjam";Carrier.unjam();
                row.put("unjam_moved",Carrier.unjams>unjams);row.put("final",xy(nativeRC.getLocation()));
                row.put("final_cd",nativeRC.getMovementCooldownTurns());row.put("moves",moves);trial.turns.add(row);
            } catch(Throwable t){failure=t;}
        }
        RobotController observedController() {
            return (RobotController)Proxy.newProxyInstance(RobotController.class.getClassLoader(),new Class<?>[]{RobotController.class},(proxy,method,args)->{
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
                return invoke(method,args);
            });
        }
        Object invoke(Method method,Object[] args)throws Throwable {
            try{return method.invoke(nativeRC,args);}catch(InvocationTargetException e){throw e.getCause();}
        }
    }
    static void ampleBudget()throws Exception {
        java.lang.reflect.Field left=RobotMonitor.class.getDeclaredField("bytecodesLeft");left.setAccessible(true);left.setInt(null,100000);
        RobotMonitor.setBytecodeLimit(12500);
    }
    static void initializeBot(RobotController rc,LiveMap map,MapLocation goal,int waits)throws Exception {
        G.init(rc);G.rc=rc;G.round=rc.getRoundNum();G.here=rc.getLocation();
        MapMem.cand=0;MapMem.nEnemyHQSeen=0;MapMem.tile=new char[G.W*G.H];
        boolean[] walls=map.getWallArray(),clouds=map.getCloudArray();int[] currents=map.getCurrentArray();
        for(int i=0;i<walls.length;i++) {
            Direction d=Direction.DIRECTION_ORDER[currents[i]];
            MapMem.tile[i]=(char)(1|(walls[i]?2:0)|(clouds[i]?4:0)|(d==Direction.CENTER?0:(d.ordinal()+1)<<3));
        }
        List<MapLocation> ours=new ArrayList<>();for(RobotInfo b:map.getInitialBodies())if(b.team==Team.A)ours.add(b.location);
        HQState.ourHQs=ours.toArray(new MapLocation[0]);
        Field.vis=null;Field.target=null;Field.nWaves=0;Field.init();
        for(int p=0;p<walls.length;p++)if(walls[p])Field.addWall(p%G.W,p/G.W);
        Field.request(goal,true);Field.think(0);check(Field.ready(goal)&&Field.done,"prescribed full field ready");
        Nav.init();Nav.avoid=false;Nav.target=goal;Nav.fieldFor=goal;Nav.fieldOn=true;Nav.fieldWaits=waits;
        Nav.bugging=false;Nav.bugFlips=0;Nav.bestDist=Integer.MAX_VALUE;Nav.sinceBest=0;
        Carrier.lastLoc=null;Carrier.stillTurns=0;Carrier.unjams=0;
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
        ampleBudget();initializeBot(world.getRobot(START).getController(),map,trial.goal,trial.waits);
        int k=Field.level(START.x,START.y),nextID=20001;List<Object> neighbours=new ArrayList<>();
        for(Direction d:G.DIRS){MapLocation p=START.add(d);if(!G.onMap(p.x,p.y)||map.getWallArray()[p.x+p.y*G.W])continue;
            int level=Field.level(p.x,p.y);neighbours.add(Arrays.<Object>asList(xy(p),level));
            boolean block=trial.blockers.equals("down")&&level==k-1 || trial.blockers.equals("down_same")&&(level==k-1||level==k);
            if(block && world.getRobot(p)==null){world.spawnRobot(nextID++,RobotType.CARRIER,p,Team.A);trial.blocked.add(xy(p));}
        }
        for(int rn=2;rn<=65 && !provider.finished;rn++)round(world,provider,rn);
        Map<String,Object> out=new LinkedHashMap<>();out.put("goal",xy(trial.goal));out.put("blocker_mode",trial.blockers);
        out.put("initial_field_waits",trial.waits);out.put("avoid_second_return_to_start",trial.avoidReturn);
        out.put("start_wave",k);out.put("initial_neighbour_waves",neighbours);out.put("blocker_positions",trial.blocked);
        out.put("first_native_collection_round",provider.firstCollection);out.put("turns",trial.turns);return out;
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
            row.remove("second_return_vetoes");rows.add(row);
        }return rows;
    }
    @SuppressWarnings("unchecked")
    public static void main(String[] args)throws Exception {
        List<Object> results=new ArrayList<>();
        for(MapLocation goal:new MapLocation[]{new MapLocation(9,21),new MapLocation(8,12)})
            for(String blockers:new String[]{"none","down","down_same"})for(boolean enabled:new boolean[]{false,true})
                results.add(run(new Trial(goal,blockers,blockers.equals("down_same")?2:0,enabled)));
        int common=0,firstDetours=0;
        for(int i=0;i<results.size();i+=2) {
            Map<String,Object> old=(Map<String,Object>)results.get(i),fix=(Map<String,Object>)results.get(i+1);
            Map<String,Object> a=(Map<String,Object>)((List<Object>)old.get("turns")).get(0);
            Map<String,Object> b=(Map<String,Object>)((List<Object>)fix.get("turns")).get(0);
            check(((List<Object>)a.get("moves")).get(0).equals(((List<Object>)b.get("moves")).get(0)),"first legal detour preserved");firstDetours++;
            if(!old.get("blocker_mode").equals("down_same")) {
                check(movementRows(old).equals(movementRows(fix)),"common native movement/cooldown/unjam path preserved");common++;
            }
        }
        Map<String,Object> out=new LinkedHashMap<>();out.put("registered_games_run",0);out.put("native_fixture_cases",results.size());
        out.put("assertions",assertions);out.put("instruction_metered",false);
        out.put("first_detour_preservation_pairs",firstDetours);out.put("common_decision_path_identity_pairs",common);
        out.put("semantics",Arrays.asList("Native move legality, occupancy, cooldown and end-round physics; owned NullControlProvider only, no player sandbox or field opponent classes.",
            "Frozen c_mend2 Nav/Carrier methods; complete known static field and stationary own blockers are prescribed, not inferred replay state.",
            "Clock guard input is synthetic ample100000; host calls are not charged and no budget performance claim is made.",
            "Counterfactual proxy vetoes only a legal move back to turn-start after at least one move in moveTwice; first detours and unjam are not vetoed.",
            "Rows trace native in-turn moves; field replay endpoints cannot establish that their actors took these same steps."));
        out.put("results",results);System.out.println(json(out));
    }
}
