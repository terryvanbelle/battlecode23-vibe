import battlecode.common.*;
import battlecode.instrumenter.SandboxedRobotPlayer;
import battlecode.instrumenter.TeamClassLoaderFactory;
import battlecode.server.*;
import battlecode.world.*;
import battlecode.world.control.RobotControlProvider;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** Entire owned RobotPlayer launcher loop under the official scheduler. Other actors execute a fixed host script.
 * Host observations/proxy bodies are unmetered; no Clock, cooldown, bytecode or owned memory writes occur. */
public final class ControlledBlindGame {
    static final int ACTOR=10003, LAST_ROUND=32;
    static final MapLocation HERE=new MapLocation(6,6), HIDDEN=new MapLocation(9,6), VISIBLE=new MapLocation(8,6);
    static int checks;
    static void check(boolean ok,String message){checks++;if(!ok)throw new IllegalStateException(message);}
    static Map<String,Object> obj(Object...values){Map<String,Object> m=new TreeMap<>();for(int i=0;i<values.length;i+=2)m.put((String)values[i],values[i+1]);return m;}
    static String quote(String s){StringBuilder b=new StringBuilder("\"");for(char c:s.toCharArray()){if(c=='"'||c=='\\')b.append('\\').append(c);else if(c<32)b.append(String.format("\\u%04x",(int)c));else b.append(c);}return b.append('"').toString();}
    static String json(Object v){
        if(v==null)return "null";if(v instanceof String)return quote((String)v);if(v instanceof Number||v instanceof Boolean)return v.toString();
        if(v instanceof Map){List<String> parts=new ArrayList<>();for(Object entry:((Map<?,?>)v).entrySet()){Map.Entry<?,?> e=(Map.Entry<?,?>)entry;parts.add(quote(String.valueOf(e.getKey()))+":"+json(e.getValue()));}return "{"+String.join(",",parts)+"}";}
        if(v instanceof Iterable){List<String> parts=new ArrayList<>();for(Object e:(Iterable<?>)v)parts.add(json(e));return "["+String.join(",",parts)+"]";}
        if(v.getClass().isArray()){List<String> parts=new ArrayList<>();for(int i=0;i<Array.getLength(v);i++)parts.add(json(Array.get(v,i)));return "["+String.join(",",parts)+"]";}
        if(v instanceof MapLocation){MapLocation p=(MapLocation)v;return "["+p.x+","+p.y+"]";}
        if(v instanceof Enum)return quote(v.toString());return quote(v.toString());
    }
    static String sha(String text)throws Exception{return sha(text.getBytes(StandardCharsets.UTF_8));}
    static String sha(byte[] bytes)throws Exception{StringBuilder s=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(bytes))s.append(String.format("%02x",b&255));return s.toString();}
    static Field field(Class<?> type,String name)throws Exception{Field f=type.getDeclaredField(name);f.setAccessible(true);return f;}
    static MapLocation mirror(MapLocation p){return new MapLocation(19-p.x,19-p.y);}
    static final class Geometry {
        final boolean[] walls=new boolean[400],clouds=new boolean[400];final int[] currents=new int[400],islands=new int[400],resources=new int[400];
        Geometry(){
            for(MapLocation center:new MapLocation[]{HERE,mirror(HERE)})for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++)if(dx!=0||dy!=0)walls[center.x+dx+20*(center.y+dy)]=true;
            clouds[HIDDEN.x+20*HIDDEN.y]=clouds[mirror(HIDDEN).x+20*mirror(HIDDEN).y]=true;
            MapLocation[] locations={HERE,mirror(HERE),new MapLocation(6,13),new MapLocation(13,6)};
            for(int i=0;i<locations.length;i++)islands[locations[i].x+20*locations[i].y]=i+1;
        }
        LiveMap map(){RobotInfo[] hqs={new RobotInfo(1,Team.A,RobotType.HEADQUARTERS,new Inventory(),1,new MapLocation(1,1)),new RobotInfo(2,Team.B,RobotType.HEADQUARTERS,new Inventory(),1,new MapLocation(18,18))};
            return new LiveMap(20,20,new MapLocation(0,0),1,2000,"OwnBlindControlled32",MapSymmetry.ROTATIONAL,hqs,walls,clouds,currents,islands,resources);}
        Map<String,Object> record(){return obj("width",20,"height",20,"origin",new MapLocation(0,0),"seed",1,"max_rounds",2000,"walls",walls,"clouds",clouds,"currents",currents,"islands",islands,"resources",resources);}
    }
    static final class Observer implements RobotControlProvider {
        final String pkg;final TeamClassLoaderFactory factory;final PrintWriter raw;final OutputStream playerLog;
        final List<Map<String,Object>> turns=new ArrayList<>();final List<Map<String,Object>> scripts=new ArrayList<>();
        GameWorld world;InternalRobot actor;SandboxedRobotPlayer player;TeamClassLoaderFactory.Loader loader;
        Class<?> monitor;List<Map<String,Object>> apis,attacks;String indicator;Throwable failure;int victimID=20000;
        Map<String,Object> lastTurn;boolean previousBlind;
        Observer(String pkg,String classes,PrintWriter raw,OutputStream playerLog){this.pkg=pkg;factory=new TeamClassLoaderFactory(classes);this.raw=raw;this.playerLog=playerLog;}
        public void matchStarted(GameWorld w){world=w;}
        public void matchEnded(){if(player!=null&&!player.getTerminated())player.terminate();}
        public void robotKilled(InternalRobot r){if(r.getID()==ACTOR&&player!=null)player.terminate();}
        public void robotSpawned(InternalRobot r){
            if(r.getID()!=ACTOR)return;
            try{
                actor=r;loader=factory.createLoader(false);
                monitor=loader.loadClass("battlecode.instrumenter.inject.RobotMonitor");
                final RobotController nativeRC=r.getController();
                RobotController observed=(RobotController)Proxy.newProxyInstance(RobotController.class.getClassLoader(),new Class<?>[]{RobotController.class},(o,m,a)->observe(nativeRC,m,a));
                player=new SandboxedRobotPlayer(pkg,observed,r.getID(),loader,playerLog,null);
            }catch(Throwable error){failure=error;}
        }
        Object observe(RobotController nativeRC,Method method,Object[] args)throws Throwable{
            String name=method.getName();boolean blind=false,owned=false;
            for(StackTraceElement frame:Thread.currentThread().getStackTrace()){
                if(frame.getClassName().startsWith(pkg+"."))owned=true;
                if(frame.getClassName().equals(pkg+".Launcher")&&frame.getMethodName().equals("blindShot"))blind=true;
            }
            Map<String,Object> entry=obj("method",name,"arguments",args==null?Collections.emptyList():Arrays.asList(args),"blind_caller",blind,"owned_caller",owned,
                "native_round",world.getCurrentRound(),"bytecodes_left",field(monitor,"bytecodesLeft").getInt(null),"pending_debt",field(monitor,"bytecodesToRemove").getInt(null));
            Map<String,Object> attack=null;InternalRobot target=null;int hp=0;
            if(name.equals("attack")){
                check(owned,"launcher attack originates in actual owned player frame");
                MapLocation to=(MapLocation)args[0];target=world.getRobot(to);hp=target==null?0:target.getHealth();
                attack=obj("round",world.getCurrentRound(),"shooter",ACTOR,"shooter_at",actor.getLocation(),"target",to,"target_id",target==null?null:target.getID(),"target_team",target==null?null:target.getTeam().toString(),"target_type",target==null?null:target.getType().toString(),
                    "blind_caller",blind,"hidden_at_attack",!nativeRC.canSenseLocation(to),"native_can_attack",nativeRC.canAttack(to),"pre_cd",actor.getActionCooldownTurns(),
                    "actual_rounded_cost",world.getCooldownWithMultiplier(10,actor.getLocation(),actor.getTeam()),"actual_multiplier",world.getCooldownMultiplier(actor.getLocation(),actor.getTeam()),"bytecodes_left",entry.get("bytecodes_left"),"victim_hp_before",hp);
            }
            try{
                Object value=method.invoke(nativeRC,args);
                if(name.equals("setIndicatorString"))indicator=(String)args[0];
                if(attack!=null){
                    int after=target==null?0:target.getHealth();attack.put("victim_hp_after",after);attack.put("native_damage",hp-after);attack.put("post_cd",actor.getActionCooldownTurns());attacks.add(attack);
                    if(blind){check((Boolean)attack.get("hidden_at_attack")&&(Boolean)attack.get("native_can_attack"),"blind attack uses native hidden legal target");check((Integer)attack.get("pre_cd")+(Integer)attack.get("actual_rounded_cost")<=10,"strict actual native sum at attack");}
                }
                if(value==null||value instanceof Number||value instanceof Boolean||value instanceof String||value instanceof Enum||value instanceof MapLocation)entry.put("return",value);
                else if(value.getClass().isArray())entry.put("returned_array_length",Array.getLength(value));
                else entry.put("return_description",value.toString());
                if(apis!=null)apis.add(entry);return value;
            }catch(InvocationTargetException error){entry.put("native_error",error.getCause().toString());if(apis!=null)apis.add(entry);throw error.getCause();}
        }
        public void roundStarted(){
            try{
                int round=world.getCurrentRound();if(round<2)return;
                if(round==2)world.spawnRobot(ACTOR,RobotType.LAUNCHER,HERE,Team.A);
                if(round==10||round==14||round==18||round==22){remove(HIDDEN);remove(VISIBLE);}
                if(round>=2&&round<=9&&world.getRobot(HIDDEN)==null)spawnVictim(HIDDEN,Team.B);
                if(round==14)spawnVictim(HIDDEN,Team.A);
                if(round==18)spawnVictim(VISIBLE,Team.B);
                if(round>=22&&world.getRobot(HIDDEN)==null)spawnVictim(HIDDEN,Team.B);
                if(round==22){
                    Geometry geometry=new Geometry();int number=0;
                    for(int x=0;x<20&&number<32;x++)for(int y=0;y<20&&number<32;y++){
                        MapLocation p=new MapLocation(x,y);if(p.distanceSquaredTo(HERE)>20||geometry.walls[x+20*y]||geometry.clouds[x+20*y]||world.getRobot(p)!=null)continue;
                        world.spawnRobot(30000+number++,RobotType.LAUNCHER,p,Team.A);
                    }
                    check(number==32,"fixed passable friendly crowd capacity");scripts.add(obj("round",round,"event","spawn_crowd","count",number));
                }
            }catch(Throwable error){failure=error;}
        }
        void remove(MapLocation p){InternalRobot r=world.getRobot(p);if(r!=null){scripts.add(obj("round",world.getCurrentRound(),"event","script_remove","id",r.getID(),"at",p));world.destroyRobot(r.getID());}}
        void spawnVictim(MapLocation p,Team team){int id=victimID++;check(world.getRobot(p)==null,"script spawn tile empty");world.spawnRobot(id,RobotType.CARRIER,p,team);scripts.add(obj("round",world.getCurrentRound(),"event","script_spawn","id",id,"at",p,"team",team.toString()));}
        public void roundEnded(){}
        public void runRobot(InternalRobot r){
            if(r.getID()!=ACTOR){
                try{if(world.getCurrentRound()==1&&r.getType()==RobotType.HEADQUARTERS)r.getController().writeSharedArray(0,r.getLocation().x*64+r.getLocation().y+1);}catch(Throwable error){failure=error;}
                return;
            }
            try{
                if(failure!=null)return;
                int round=world.getCurrentRound();
                if(lastTurn!=null){lastTurn.put("next_actual_own_start_cd",r.getActionCooldownTurns());if(previousBlind)check(r.getActionCooldownTurns()==0,"next actual scheduled own-start zero debt");}
                apis=new ArrayList<>();attacks=new ArrayList<>();indicator=null;
                int startCD=r.getActionCooldownTurns();player.setBytecodeLimit(r.getBytecodeLimit());player.step();
                int used=player.getBytecodesUsed();
                check(!player.getTerminated(),"owned RobotPlayer continues at yield");check(used<r.getBytecodeLimit(),"native sandbox did not exhaust a turn");
                check(indicator!=null,"actual full RobotPlayer reached indicator before yield");
                Class<?> g=Class.forName(pkg+".G",false,loader),launcher=Class.forName(pkg+".Launcher",false,loader);
                Map<String,Object> counters=new TreeMap<>();
                for(String name:new String[]{"overruns","exceptions","nearMiss","maxBc","round","spawnRound","rng"})counters.put(name,field(g,name).get(null));
                for(String name:new String[]{"shots","steppedIn","kited","pinnedSeen","unsafeStepsAvoided"})counters.put(name,field(launcher,name).get(null));
                if(!pkg.equals("c_mend2"))for(String name:new String[]{"blindChecks","blindEligible","blindShots","blindBudgetSkipped","blindCooldownSkipped","blindNoTarget","blindStale"})counters.put(name,field(launcher,name).get(null));
                else counters.put("blindShots",0);
                check((Integer)counters.get("overruns")==0&&(Integer)counters.get("exceptions")==0,"complete loop basics counters zero");
                check((Integer)counters.get("round")==round,"owned turn cache matches scheduled native round");
                int before=turns.isEmpty()?0:(Integer)((Map<?,?>)turns.get(turns.size()-1).get("counters")).get("blindShots");
                int delta=(Integer)counters.get("blindShots")-before;long hookActions=attacks.stream().filter(a->Boolean.TRUE.equals(a.get("blind_caller"))).count();
                check(delta==hookActions&&delta>=0&&delta<=1,"paused cumulative counter matches native hook attacks");
                if(delta==1)check(attacks.size()==1,"hook turn has no ordinary attack displaced or combined");
                previousBlind=delta==1;
                lastTurn=obj("round",round,"start_cd",startCD,"end_cd",r.getActionCooldownTurns(),"whole_turn_bytecodes",used,"native_bytecode_limit",r.getBytecodeLimit(),
                    "counters",counters,"indicator",indicator,"attacks",attacks,"api_calls",apis,"sandbox_paused",true,"memory",memory());
                turns.add(lastTurn);raw.println(json(obj("kind","turn","observation",lastTurn)));raw.flush();
            }catch(Throwable error){failure=error;raw.println(json(obj("kind","failed_turn","round",world.getCurrentRound(),"failure",error.toString(),"native_cd",r.getActionCooldownTurns(),"api_calls",apis,"attacks",attacks)));raw.flush();}
        }
        Map<String,Object> memory()throws Exception{
            Map<String,Object> out=new TreeMap<>();
            for(String[] names:new String[][]{{"MapMem","tile","pendingIdx","maxPending","cand","decidedRound"},{"Field","target","nWaves","pending","done","stale","iy","wy","waves","wall"}}){
                Class<?> type=Class.forName(pkg+"."+names[0],false,loader);
                for(int i=1;i<names.length;i++){Object value=field(type,names[i]).get(null);out.put(names[0]+"."+names[i],value==null?null:value.getClass().isArray()?sha(json(value)):value);}
            }
            return out;
        }
        public int getBytecodesUsed(InternalRobot r){return r.getID()==ACTOR&&player!=null?player.getBytecodesUsed():0;}
        public boolean getTerminated(InternalRobot r){return r.getID()==ACTOR&&player!=null&&player.getTerminated();}
    }
    static Map<String,Object> nativeState(GameWorld w){
        List<Map<String,Object>> robots=new ArrayList<>();List<InternalRobot> sorted=new ArrayList<>();for(InternalRobot r:w.getObjectInfo().robots())sorted.add(r);sorted.sort(Comparator.comparingInt(InternalRobot::getID));
        for(InternalRobot r:sorted)robots.add(obj("id",r.getID(),"team",r.getTeam().toString(),"type",r.getType().toString(),"at",r.getLocation(),"hp",r.getHealth(),"action_cd",r.getActionCooldownTurns(),"move_cd",r.getMovementCooldownTurns(),"age",r.getRoundsAlive(),
            "Ad",r.getResource(ResourceType.ADAMANTIUM),"Mn",r.getResource(ResourceType.MANA),"Ex",r.getResource(ResourceType.ELIXIR),"standard_anchors",r.getNumAnchors(Anchor.STANDARD),"accelerating_anchors",r.getNumAnchors(Anchor.ACCELERATING),"bytecodes",r.getBytecodesUsed()));
        List<Map<String,Object>> teams=new ArrayList<>();for(Team team:new Team[]{Team.A,Team.B}){int[] shared=new int[64];for(int i=0;i<64;i++)shared[i]=w.getTeamInfo().readSharedArray(team,i);teams.add(obj("team",team.toString(),"Ad",w.getTeamInfo().getAdamantium(team),"Mn",w.getTeamInfo().getMana(team),"Ex",w.getTeamInfo().getElixir(team),"anchors_placed",w.getTeamInfo().getAnchorsPlaced(team),"shared",shared));}
        List<Map<String,Object>> islands=new ArrayList<>();for(int i=1;i<=4;i++){Island island=w.getIsland(i);islands.add(obj("id",i,"owner",island.getTeam().toString(),"anchor",island.getAnchor(),"hp",island.getHealth()));}
        return obj("round",w.getCurrentRound(),"robots",robots,"teams",teams,"islands",islands);
    }
    public static void main(String[] args)throws Exception{
        if(args.length!=4)throw new IllegalArgumentException("ControlledBlindGame <owned package> <classes> <fresh output> <arm>");
        check(System.getProperty("java.version").startsWith("1.8."),"JDK8");check(args[0].equals("c_mend2")||args[0].equals("c_blind1"),"owned frozen packages only");
        Config.setGlobalConfig(new Config(new String[]{"-c","-"}));
        Path out=Paths.get(args[2]);Files.createDirectory(out);Geometry geometry=new Geometry();
        Files.write(out.resolve("geometry.json"),(json(geometry.record())+"\n").getBytes(StandardCharsets.UTF_8));
        List<Map<String,Object>> states=new ArrayList<>();Throwable fatal=null;Observer observer=null;GameMaker maker=null;
        try(PrintWriter raw=new PrintWriter(new OutputStreamWriter(new FileOutputStream(out.resolve("raw.jsonl").toFile()),StandardCharsets.UTF_8));OutputStream logs=new FileOutputStream(out.resolve("player.log").toFile())){
            observer=new Observer(args[0],args[1],raw,logs);
            GameInfo info=new GameInfo("owned-full-launcher",args[0],args[1],"owned-scripted-fixture","owned.scripted",null,new String[]{"OwnBlindControlled32"},null,false);
            maker=new GameMaker(info,null,true);maker.makeGameHeader();GameWorld world=new GameWorld(geometry.map(),observer,maker.getMatchMaker());
            for(int round=1;round<=LAST_ROUND;round++){
                check(world.runRound()==GameState.RUNNING&&world.getCurrentRound()==round,"controlled native round ran exactly once");
                if(observer.failure!=null)throw new IllegalStateException("owned full-loop observation failed",observer.failure);
                Map<String,Object> state=nativeState(world);states.add(state);raw.println(json(obj("kind","native_round_state","state",state)));raw.flush();
            }
            check(observer.turns.size()==31,"all scheduled launcher turns observed including initialization");
            // Neutral synthetic footer closes this forced-cutoff diagnostic archive; it supplies no scored winner.
            maker.getMatchMaker().makeMatchFooter(Team.NEUTRAL,LAST_ROUND,Collections.emptyList());maker.makeGameFooter(Team.NEUTRAL);maker.writeGame(out.resolve("native.bc23").toFile());
        }catch(Throwable error){fatal=error;}
        finally{if(observer!=null)observer.matchEnded();}
        Map<String,Object> result=obj("scope","full-owned-launcher-RobotPlayer-controlled-native-scheduler","arm",args[3],"package",args[0],"rounds",states.size(),"checks",checks,
            "pass",fatal==null,"failure",fatal==null?null:fatal.toString(),"failure_cause",fatal==null||fatal.getCause()==null?null:fatal.getCause().toString(),
            "geometry_sha256",sha(json(geometry.record())),"native_states",states,"turns",observer==null?Collections.emptyList():observer.turns,"script_events",observer==null?Collections.emptyList():observer.scripts,
            "host_observation_work_metered",false,"first_turn_initialization_included",true,"clock_or_owned_memory_modified",false,"scored_games",0,"controlled_cutoff",LAST_ROUND,"synthetic_neutral_footer",true);
        Files.write(out.resolve("result.json"),(json(result)+"\n").getBytes(StandardCharsets.UTF_8));
        System.out.println(json(obj("arm",args[3],"pass",fatal==null,"rounds",states.size(),"checks",checks,"output",out.toString(),"scored_games",0)));
        if(fatal!=null)throw new IllegalStateException("controlled full RobotPlayer fixture failed",fatal);
    }
}
