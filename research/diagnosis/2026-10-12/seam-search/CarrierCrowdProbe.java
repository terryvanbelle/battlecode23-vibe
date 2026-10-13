import battlecode.common.*;
import battlecode.instrumenter.TeamClassLoaderFactory;
import battlecode.world.Inventory;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

/** Own instrumented source; bounded synthetic controller, no GameWorld or games. */
public final class CarrierCrowdProbe {
    static final MapLocation HOME=new MapLocation(8,12),HQ=new MapLocation(4,10),NEW=new MapLocation(13,20);
    static Field field(Class<?> c,String n)throws Exception{Field f=c.getDeclaredField(n);f.setAccessible(true);return f;}
    static Method method(Class<?> c,String n,Class<?>...p)throws Exception{Method m=c.getDeclaredMethod(n,p);m.setAccessible(true);return m;}
    static int checks;
    static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    static String q(String s){return "\""+s.replace("\\","\\\\").replace("\"","\\\"")+"\"";}
    static final class World implements InvocationHandler {
        MapLocation here=new MapLocation(6,12);int round=50,weight,moveCd,actionCd,moves,collected,delivered;boolean discover,knownOther,freezeMotion;
        int[] shared=new int[64];
        World(boolean d,boolean known,int load){discover=d;knownOther=known;weight=load;shared[1]=enc(HQ);shared[5]=(2<<12)|enc(HOME);if(known)shared[6]=(2<<12)|enc(NEW);}
        int enc(MapLocation l){return l.x*64+l.y+1;}
        boolean blocked(MapLocation l){return l.x>=7&&l.x<=9&&l.y>=11&&l.y<=13;}
        boolean onMap(MapLocation l){return l.x>=0&&l.x<60&&l.y>=0&&l.y<60;}
        boolean canMove(Direction d){MapLocation l=here.add(d);return !freezeMotion&&d!=Direction.CENTER&&moveCd<10&&onMap(l)&&!blocked(l)&&!l.equals(HQ);}
        void next(){round++;moveCd=Math.max(0,moveCd-10);actionCd=Math.max(0,actionCd-10);}
        public Object invoke(Object obj,Method m,Object[] args){
            String n=m.getName();
            switch(n){
                case "readSharedArray":return shared[(Integer)args[0]];
                case "canWriteSharedArray":return false;
                case "getLocation":return here;
                case "getRoundNum":return round;
                case "getWeight":return weight;
                case "isMovementReady":return moveCd<10;
                case "getMovementCooldownTurns":return moveCd;
                case "isActionReady":return actionCd<10;
                case "getActionCooldownTurns":return actionCd;
                case "canMove":return canMove((Direction)args[0]);
                case "move": {Direction d=(Direction)args[0];if(!canMove(d))throw new IllegalStateException("illegal mocked move");here=here.add(d);moveCd+=(int)Math.floor(.375*weight)+5;moves++;return null;}
                case "onTheMap":return onMap((MapLocation)args[0]);
                case "canSenseLocation":return onMap((MapLocation)args[0])&&here.distanceSquaredTo((MapLocation)args[0])<=20;
                case "sensePassability":return true;
                case "senseNearbyMapInfos":return new MapInfo[0];
                case "senseNearbyRobots":return new RobotInfo[0];
                case "senseNearbyWells": {
                    ArrayList<WellInfo> wells=new ArrayList<>();if(here.distanceSquaredTo(HOME)<=20)wells.add(new WellInfo(HOME,ResourceType.MANA,new Inventory(),false));
                    if(discover&&here.distanceSquaredTo(NEW)<=20)wells.add(new WellInfo(NEW,ResourceType.MANA,new Inventory(),false));
                    return wells.toArray(new WellInfo[0]);}
                case "canCollectResource": {MapLocation at=(MapLocation)args[0];int amount=(Integer)args[1];return at.equals(NEW)&&(discover||knownOther)&&here.distanceSquaredTo(at)<=2&&actionCd<10&&weight<40&&(amount==-1||amount>=0&&amount<=1);}
                case "collectResource": {MapLocation at=(MapLocation)args[0];if(!at.equals(NEW)||here.distanceSquaredTo(at)>2||actionCd>=10)throw new IllegalStateException("illegal mocked collect");int amount=(Integer)args[1];if(amount==-1)amount=1;weight+=amount;collected+=amount;actionCd+=10;return null;}
                case "getResourceAmount":return args[0]==ResourceType.MANA?weight:0;
                case "canTransferResource":return args[0].equals(HQ)&&here.distanceSquaredTo(HQ)<=2&&actionCd<10&&args[1]==ResourceType.MANA&&(Integer)args[2]>0&&(Integer)args[2]<=weight;
                case "transferResource": {int amount=(Integer)args[2];if(!args[0].equals(HQ)||here.distanceSquaredTo(HQ)>2||actionCd>=10||amount>weight)throw new IllegalStateException("illegal mocked transfer");weight-=amount;delivered+=amount;actionCd+=10;return null;}
                case "senseRobotAtLocation":return args[0].equals(HQ)?new RobotInfo(9,Team.A,RobotType.HEADQUARTERS,new Inventory(),1,HQ):null;
                case "setIndicatorDot":case "setIndicatorString":case "setIndicatorLine":return null;
                default:throw new IllegalStateException("unplanned controller method: "+n);
            }
        }
    }
    static final class Fixture {
        World world;Class<?> g,carrier,mapmem,monitor;Field remaining,debt;Method gather,scan,deliver;String pkg;
        int xTurns,peakCost;boolean switched,returnedSame,sawNew,selectedNew;List<String> trace=new ArrayList<>();
        Fixture(TeamClassLoaderFactory factory,String p,boolean discover,boolean known,int load)throws Exception{
            pkg=p;world=new World(discover,known,load);ClassLoader loader=factory.createLoader(false);
            monitor=loader.loadClass("battlecode.instrumenter.inject.RobotMonitor");remaining=field(monitor,"bytecodesLeft");debt=field(monitor,"bytecodesToRemove");
            Class<?> pauser=Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Pauser"),killer=Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Killer");
            Object pause=Proxy.newProxyInstance(pauser.getClassLoader(),new Class<?>[]{pauser},(o,m,a)->{throw new IllegalStateException("fixture exhausted native budget");});
            Object kill=Proxy.newProxyInstance(killer.getClassLoader(),new Class<?>[]{killer},(o,m,a)->{throw new IllegalStateException("fixture robot killed");});
            monitor.getMethod("init",pauser,killer,int.class,Class.forName("battlecode.instrumenter.profiler.Profiler")).invoke(null,pause,kill,123,null);
            monitor.getMethod("setBytecodeLimit",int.class).invoke(null,12500);budget(1000000);
            g=Class.forName(p+".G",true,loader);carrier=Class.forName(p+".Carrier",true,loader);mapmem=Class.forName(p+".MapMem",true,loader);
            Class<?> comms=Class.forName(p+".Comms",true,loader),nav=Class.forName(p+".Nav",true,loader),hqs=Class.forName(p+".HQState",true,loader);
            Class.forName(p+".Field",true,loader);Class.forName(p+".Telemetry",true,loader);Class.forName(p+".C",true,loader);Class.forName(p+".Wells",true,loader);
            field(g,"rc").set(null,Proxy.newProxyInstance(RobotController.class.getClassLoader(),new Class<?>[]{RobotController.class},world));
            field(g,"W").setInt(null,60);field(g,"H").setInt(null,60);field(g,"id").setInt(null,123);field(g,"rng").setInt(null,71);
            field(g,"us").set(null,Team.A);field(g,"them").set(null,Team.B);field(g,"type").set(null,RobotType.CARRIER);
            field(g,"nearby").set(null,new RobotInfo[0]);field(g,"enemies").set(null,new RobotInfo[0]);
            field(hqs,"ourHQs").set(null,new MapLocation[]{HQ});field(mapmem,"cand").setInt(null,1);
            field(carrier,"role").setInt(null,2);field(carrier,"well").set(null,HOME);field(carrier,"crowdTurns").setInt(null,6);
            method(mapmem,"noteWell",MapLocation.class,int.class).invoke(null,HOME,2);
            field(comms,"canWrite").setBoolean(null,false);method(nav,"init").invoke(null);
            gather=method(carrier,"gather");scan=method(mapmem,"scan");deliver=method(carrier,"deliver");
        }
        void budget(int amount)throws Exception{remaining.setInt(null,amount);debt.setInt(null,0);}
        void tick()throws Exception {
            budget(12500);field(g,"round").setInt(null,world.round);field(g,"here").set(null,world.here);
            try {
                scan.invoke(null);
                if(world.weight>=30||field(carrier,"returning").getBoolean(null))deliver.invoke(null);else gather.invoke(null);
            }catch(InvocationTargetException e){throw new IllegalStateException("instrumented fixture call failed",e.getCause());}
            check(debt.getInt(null)==0,"pending instrumentation debt flushed");int cost=12500-remaining.getInt(null);peakCost=Math.max(peakCost,cost);
            char state=field(carrier,"state").getChar(null);MapLocation well=(MapLocation)field(carrier,"well").get(null);
            if(state=='X')xTurns++;if(state=='S')switched=true;if(switched&&HOME.equals(well))returnedSame=true;if(NEW.equals(well))selectedNew=true;
            int n=field(mapmem,"nSeenWell").getInt(null);MapLocation[] seen=(MapLocation[])field(mapmem,"seenWell").get(null);for(int i=0;i<n;i++)if(NEW.equals(seen[i]))sawNew=true;
            if(trace.size()<16||world.delivered>0&&trace.size()<17)trace.add("{\"round\":"+world.round+",\"state\":"+q(String.valueOf(state))+",\"here\":["+world.here.x+","+world.here.y+"],\"well\":"+(well==null?"null":"["+well.x+","+well.y+"]")+",\"weight\":"+world.weight+",\"cost\":"+cost+"}");
            world.next();
        }
        String json(String name){return "{\"case\":"+q(name)+",\"package\":"+q(pkg)+",\"switched\":"+switched+",\"reselected_home\":"+returnedSame+",\"explore_turns\":"+xTurns+",\"discovered_new\":"+sawNew+",\"selected_new\":"+selectedNew+",\"collected\":"+world.collected+",\"delivered\":"+world.delivered+",\"peak_synthetic_tick_bytecodes\":"+peakCost+",\"trace\":["+String.join(",",trace)+"]}";}
    }
    public static void main(String[] args)throws Exception {
        if(args.length!=2)throw new IllegalArgumentException("CarrierCrowdProbe <own private classes> <result.json>");
        TeamClassLoaderFactory factory=new TeamClassLoaderFactory(args[0]);List<String> results=new ArrayList<>();
        Fixture base=new Fixture(factory,"c_mend2",true,false,0);for(int i=0;i<80;i++)base.tick();
        check(base.switched&&base.returnedSame&&base.xTurns==0&&!base.sawNew&&base.world.collected==0,"baseline no-alternative arm immediately reacquires home and cannot reach discovery in fixture");results.add(base.json("unknown_alternative"));
        Fixture fixed=new Fixture(factory,"c_crowdprobe",true,false,0);for(int i=0;i<100&&fixed.world.delivered==0;i++)fixed.tick();
        check(fixed.xTurns>0&&fixed.sawNew&&fixed.selectedNew&&fixed.world.collected>=30&&fixed.world.delivered>=30,"bounded rejection permits discovery, collecting and normal return");results.add(fixed.json("unknown_alternative"));
        Fixture timeout=new Fixture(factory,"c_crowdprobe",false,false,0);timeout.tick();int until=field(timeout.carrier,"crowdExploreUntil").getInt(null);
        while(timeout.world.round<=until)timeout.tick();check(field(timeout.carrier,"crowdRejected").get(null)==null,"rejection ends on deadline");results.add(timeout.json("no_discovery_timeout"));
        Fixture cargo=new Fixture(factory,"c_crowdprobe",true,false,5);cargo.tick();cargo.tick();check(cargo.xTurns==0&&cargo.returnedSame&&field(cargo.carrier,"crowdRejected").get(null)==null,"partial cargo retains original arm");results.add(cargo.json("partial_cargo"));
        Fixture knownBase=new Fixture(factory,"c_mend2",false,true,0),knownFix=new Fixture(factory,"c_crowdprobe",false,true,0);knownBase.tick();knownFix.tick();
        check(NEW.equals(field(knownBase.carrier,"well").get(null))&&NEW.equals(field(knownFix.carrier,"well").get(null)),"known alternative switch unchanged");results.add(knownBase.json("known_alternative"));results.add(knownFix.json("known_alternative"));
        Fixture roleChange=new Fixture(factory,"c_crowdprobe",false,false,0);roleChange.tick();field(roleChange.carrier,"role").setInt(null,1);roleChange.tick();
        check(field(roleChange.carrier,"crowdRejected").get(null)==null,"role change clears temporary exclusion");results.add(roleChange.json("role_change"));
        Fixture outside=new Fixture(factory,"c_crowdprobe",true,false,0);outside.world.here=new MapLocation(5,12);outside.world.freezeMotion=true;outside.tick();
        check(!outside.switched&&field(outside.carrier,"crowdRejected").get(null)==null&&field(outside.carrier,"crowdTurns").getInt(null)==6,"existing outside-radius9 crowd trigger unchanged");results.add(outside.json("outside_crowd_radius"));
        Fixture adBase=new Fixture(factory,"c_mend2",false,false,0),adFix=new Fixture(factory,"c_crowdprobe",false,false,0);field(adBase.carrier,"role").setInt(null,1);field(adFix.carrier,"role").setInt(null,1);adBase.tick();adFix.tick();
        check(HOME.equals(field(adBase.carrier,"well").get(null))&&HOME.equals(field(adFix.carrier,"well").get(null))&&field(adFix.carrier,"crowdRejected").get(null)==null,"non-Mana arm unchanged");results.add(adBase.json("ad_role"));results.add(adFix.json("ad_role"));
        String json="{\"games_run\":0,\"checks\":"+checks+",\"cases\":["+String.join(",",results)+"],\"limits\":[\"Synthetic open terrain with a fully occupied home collection footprint and native own instructions/API callsite charges; controller mock body/setup are unmetered.\",\"Fixture calls actual MapMem.scan and Carrier gather/deliver; excludes full run survival, anchors, scouting, unjam and end-turn fill.\",\"New well(13,20) is sensed only within actual carrier vision20; this is a structural reachability proof, not Forest discovery timing or a game win claim.\",\"Prototype changes only empty Mana no-known-alternative crowd search,12-turn rejection, no HQ, role ratio, crowd-radius or navigation changes.\"]}";
        try(PrintWriter out=new PrintWriter(args[1])){out.println(json);}
        System.out.println("{\"games_run\":0,\"checks\":"+checks+",\"baseline_explore_turns\":"+base.xTurns+",\"prototype_explore_turns\":"+fixed.xTurns+",\"prototype_delivered\":"+fixed.world.delivered+",\"result\":"+q(args[1])+"}");
    }
}
