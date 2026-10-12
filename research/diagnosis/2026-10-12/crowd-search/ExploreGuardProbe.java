import battlecode.common.*;
import battlecode.instrumenter.TeamClassLoaderFactory;
import battlecode.server.*;
import battlecode.world.*;
import battlecode.world.control.NullControlProvider;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

/** Bounded API fixture: real GameWorld/RC physics, reflected own methods, no server game. */
public final class ExploreGuardProbe {
    static int checks;
    static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    static Field field(Class<?> c,String n)throws Exception{return CarrierCrowdProbe.field(c,n);}
    static Method method(Class<?> c,String n,Class<?>... p)throws Exception{return CarrierCrowdProbe.method(c,n,p);}
    static void call(Method m,Object...args)throws Exception{
        try{m.invoke(null,args);}catch(InvocationTargetException e){throw new IllegalStateException("own method "+m,e.getCause());}
    }
    static final MapLocation HOME=CarrierCrowdProbe.HOME,HQ=CarrierCrowdProbe.HQ,NEW=CarrierCrowdProbe.NEW;
    static final class NativeFixture {
        final CarrierCrowdProbe.Fixture f;
        final GameWorld world;final InternalRobot owner,hq;
        final Class<?> telemetry,nav,comms,hqs,distance;
        NativeFixture(TeamClassLoaderFactory factory,String pkg,boolean newWell)throws Exception {this(factory,pkg,newWell,false);}
        NativeFixture(TeamClassLoaderFactory factory,String pkg,boolean newWell,boolean forest)throws Exception {
            f=new CarrierCrowdProbe.Fixture(factory,pkg,false,false,0);
            int[] resources=new int[3600];resources[HOME.x+60*HOME.y]=ResourceType.MANA.ordinal();
            if(newWell)resources[NEW.x+60*NEW.y]=ResourceType.MANA.ordinal();
            LiveMap map=forest?GameMapIO.loadMap("Forest",null,false):new LiveMap(60,60,new MapLocation(0,0),1337,2000,"OwnExploreAPIFixture",MapSymmetry.ROTATIONAL,
                new RobotInfo[]{new RobotInfo(9,Team.A,RobotType.HEADQUARTERS,new Inventory(),1,HQ)},
                new boolean[3600],new boolean[3600],new int[3600],new int[3600],resources);
            GameMaker maker=new GameMaker(new GameInfo("own","c_mend2",null,"own","c_mend2",null,new String[0],null,false),null,true);
            maker.makeGameHeader();world=new GameWorld(map,new NullControlProvider(),maker.getMatchMaker());
            MapLocation start=new MapLocation(forest?10:6,12);world.spawnRobot(123,RobotType.CARRIER,start,Team.A);
            int id=200;for(int x=7;x<=9;x++)for(int y=11;y<=13;y++)
                if(!map.getWallArray()[x+60*y])world.spawnRobot(id++,RobotType.CARRIER,new MapLocation(x,y),Team.A);
            owner=world.getRobot(start);
            MapLocation[] ours;
            if(forest){List<MapLocation> ownHQs=new ArrayList<>();for(RobotInfo r:map.getInitialBodies())if(r.team==Team.A)ownHQs.add(r.location);
                ours=ownHQs.toArray(new MapLocation[0]);for(int i=0;i<ours.length;i++)world.getTeamInfo().writeSharedArray(Team.A,i,f.world.enc(ours[i]));}
            else{ours=new MapLocation[]{HQ};world.getTeamInfo().writeSharedArray(Team.A,0,f.world.enc(HQ));}
            hq=world.getRobot(ours[0]);
            world.getTeamInfo().writeSharedArray(Team.A,5,(2<<12)|f.world.enc(HOME));
            field(GameWorld.class,"currentRound").setInt(world,49);
            field(f.g,"rc").set(null,owner.getController());
            field(Class.forName(pkg+".HQState",true,f.g.getClassLoader()),"ourHQs").set(null,ours);
            field(f.g,"here").set(null,owner.getLocation());field(f.g,"round").setInt(null,49);
            telemetry=Class.forName(pkg+".Telemetry",true,f.g.getClassLoader());
            nav=Class.forName(pkg+".Nav",true,f.g.getClassLoader());
            comms=Class.forName(pkg+".Comms",true,f.g.getClassLoader());hqs=Class.forName(pkg+".HQState",true,f.g.getClassLoader());
            distance=Class.forName(pkg+".Field",true,f.g.getClassLoader());
            f.budget(1000000);call(method(distance,"init"));call(method(telemetry,"init"));
            check(owner.getController() instanceof RobotControllerImpl,"actual engine controller");
        }
        void begin(int budget)throws Exception {
            world.processBeginningOfRound();owner.processBeginningOfTurn();
            field(f.g,"here").set(null,owner.getLocation());field(f.g,"round").setInt(null,world.getCurrentRound());f.budget(budget);
        }
        int left()throws Exception {check(f.debt.getInt(null)==0,"pending instruction/API debt flushed");return f.remaining.getInt(null);}
        List<String> tail(boolean due)throws Exception {
            List<String> parts=new ArrayList<>();int before=left();call(method(f.carrier,"unjam"));parts.add("\"unjam\":"+(before-left()));
            before=left();call(method(f.carrier,"note"));parts.add("\"note\":"+(before-left()));
            field(telemetry,"nextCnt").setInt(null,due?world.getCurrentRound():100000);
            before=left();call(method(telemetry,"endTurn",int.class),world.getCurrentRound());parts.add("\"end_turn\":"+(before-left()));
            before=left();if((world.getCurrentRound()+123)%5==0)call(method(f.mapmem,"flushIslands",int.class),2500);
            call(method(f.mapmem,"process",int.class),1500);call(method(distance,"think",int.class),1500);
            parts.add("\"bounded_fill\":"+(before-left()));before=left();
            if(left()>=400)call(method(telemetry,"indicator"));parts.add("\"indicator\":"+(before-left()));
            before=left();call(method(telemetry,"pad"));parts.add("\"pad\":"+(before-left()));return parts;
        }
        void dense(int sharedType,int seenType)throws Exception {
            for(int i=1;i<16;i++)world.getTeamInfo().writeSharedArray(Team.A,5+i,(sharedType<<12)|f.world.enc(new MapLocation(10+i%5,20+i/5)));
            MapLocation[] seen=new MapLocation[32];int[] types=new int[32];
            for(int i=0;i<32;i++){seen[i]=new MapLocation(10+i%8,30+i/8);types[i]=seenType;}
            field(f.mapmem,"seenWell").set(null,seen);field(f.mapmem,"seenWellType").set(null,types);field(f.mapmem,"nSeenWell").setInt(null,32);
        }
    }
    static String scenario(TeamClassLoaderFactory factory,int budget,boolean due,boolean jam,int sharedType,int seenType)throws Exception{
        NativeFixture n=new NativeFixture(factory,"c_explore1",false);n.begin(12500);call(n.f.gather);
        check(field(n.f.carrier,"crowdRejected").get(null)!=null,"native crowd trigger starts episode");
        n.dense(sharedType,seenType);field(n.f.carrier,"stillTurns").setInt(null,jam?6:0);n.begin(budget);
        int before=n.left();call(n.f.gather);int gather=before-n.left(),after=n.left();List<String> tail=n.tail(due);
        check(n.left()>0,"native API fixture gather and own tail returned within assigned budget");
        return "{\"budget\":"+budget+",\"counter_due\":"+due+",\"jam\":"+jam+",\"shared_type\":"+sharedType+",\"seen_type\":"+seenType+
            ",\"gather\":"+gather+",\"after_gather\":"+after+",\"after_tail\":"+n.left()+",\"tail\":{"+String.join(",",tail)+"},\"state\":"+CarrierCrowdProbe.q(String.valueOf(field(n.f.carrier,"state").getChar(null)))+"}";
    }
    static String delivery(TeamClassLoaderFactory factory,String pkg)throws Exception{
        NativeFixture n=new NativeFixture(factory,pkg,true);int peak=0,x=0,firstNew=0,deposit=0;
        for(int i=0;i<100&&n.hq.getResource(ResourceType.MANA)==0;i++){
            n.begin(12500);call(method(n.telemetry,"startTurn"));call(method(n.f.g,"startTurn"));call(method(n.comms,"startTurn"));call(method(n.hqs,"refresh"));
            call(method(n.f.carrier,"run"));int used=12500-n.left();if(used>peak)peak=used;
            if(field(n.f.carrier,"state").getChar(null)=='X')x++;
            if(n.owner.getResource(ResourceType.MANA)>0&&firstNew==0)firstNew=n.world.getCurrentRound();
            // Carrier.run already calls unjam/note; this fixture invokes only the actual remaining telemetry/fill methods.
            call(method(n.telemetry,"endTurn",int.class),n.world.getCurrentRound());
            if((n.world.getCurrentRound()+123)%5==0)call(method(n.f.mapmem,"flushIslands",int.class),2500);
            call(method(n.f.mapmem,"process",int.class),1500);call(method(n.distance,"think",int.class),1500);
            if(n.left()>=400)call(method(n.telemetry,"indicator"));call(method(n.telemetry,"pad"));
            check(n.left()>0,"native actual Carrier.run plus remaining helper tail within12500");
            if(n.hq.getResource(ResourceType.MANA)>0)deposit=n.world.getCurrentRound();
        }
        int amount=n.hq.getResource(ResourceType.MANA);
        if(pkg.equals("c_explore1"))check(x>0&&firstNew>0&&amount>=30&&n.owner.getResource(ResourceType.MANA)==0,"actual engine pickup and own deliver transfer to HQ");
        else check(amount==0&&x==0,"native zero/base retain rejected-home loop");
        return "{\"package\":"+CarrierCrowdProbe.q(pkg)+",\"explore_turns\":"+x+",\"first_pickup_round\":"+firstNew+",\"hq_mana\":"+amount+",\"deposit_round\":"+deposit+",\"peak_shared_plus_Carrier_run\":"+peak+",\"cargo_final\":"+n.owner.getResource(ResourceType.MANA)+",\"location_final\":["+n.owner.getLocation().x+","+n.owner.getLocation().y+"]}";
    }
    static String forest(TeamClassLoaderFactory factory,boolean centreKnown)throws Exception{
        NativeFixture n=new NativeFixture(factory,"c_explore1",false,true);List<String> trace=new ArrayList<>();
        MapLocation centreA=new MapLocation(29,48),centreB=new MapLocation(30,48);
        if(centreKnown){n.world.getTeamInfo().writeSharedArray(Team.A,6,(2<<12)|n.f.world.enc(centreA));n.world.getTeamInfo().writeSharedArray(Team.A,7,(2<<12)|n.f.world.enc(centreB));}
        int seenRound=0,selectedRound=0,pickup=0,deposit=0,starts=0;
        for(int i=0;i<(centreKnown?140:32);i++){
            n.begin(12500);call(method(n.telemetry,"startTurn"));call(method(n.f.g,"startTurn"));call(method(n.comms,"startTurn"));call(method(n.hqs,"refresh"));
            int beforeMana=n.owner.getResource(ResourceType.MANA),beforeBanks=0;for(InternalRobot r:n.world.getObjectInfo().robots())if(r.getTeam()==Team.A&&r.getType()==RobotType.HEADQUARTERS)beforeBanks+=r.getResource(ResourceType.MANA);
            call(method(n.f.carrier,"run"));
            int round=n.world.getCurrentRound();MapLocation well=(MapLocation)field(n.f.carrier,"well").get(null);
            int ns=field(n.f.mapmem,"nSeenWell").getInt(null);MapLocation[] seen=(MapLocation[])field(n.f.mapmem,"seenWell").get(null);boolean learned=false;
            for(int j=0;j<ns;j++)if(centreA.equals(seen[j])||centreB.equals(seen[j]))learned=true;
            if(learned&&seenRound==0)seenRound=round;if((centreA.equals(well)||centreB.equals(well))&&selectedRound==0)selectedRound=round;
            if(n.owner.getResource(ResourceType.MANA)>beforeMana&&(centreA.equals(well)||centreB.equals(well)))pickup+=n.owner.getResource(ResourceType.MANA)-beforeMana;
            int afterBanks=0;for(InternalRobot r:n.world.getObjectInfo().robots())if(r.getTeam()==Team.A&&r.getType()==RobotType.HEADQUARTERS)afterBanks+=r.getResource(ResourceType.MANA);
            deposit+=Math.max(0,afterBanks-beforeBanks);starts=field(n.f.carrier,"crowdSearchStarts").getInt(null);
            if(i<32||deposit>0)trace.add("{\"round\":"+round+",\"state\":"+CarrierCrowdProbe.q(String.valueOf(field(n.f.carrier,"state").getChar(null)))+",\"here\":["+n.owner.getLocation().x+","+n.owner.getLocation().y+"],\"well\":"+(well==null?"null":"["+well.x+","+well.y+"]")+",\"search_until\":"+field(n.f.carrier,"crowdExploreUntil").getInt(null)+",\"seen_centre\":"+learned+",\"mana\":"+n.owner.getResource(ResourceType.MANA)+"}");
            call(method(n.telemetry,"endTurn",int.class),round);call(method(n.f.mapmem,"process",int.class),1500);call(method(n.distance,"think",int.class),1500);
            if(n.left()>=400)call(method(n.telemetry,"indicator"));call(method(n.telemetry,"pad"));check(n.left()>0,"Forest actual API Carrier/tail within12500");
            n.world.processEndOfRound();
            if(deposit>0)break;
        }
        check(centreKnown||starts>0,"unknown-centre Forest case actually reaches crowd episode");
        return "{\"map\":\"Forest\",\"initial_shared_centre_knowledge\":"+centreKnown+",\"search_starts\":"+starts+",\"first_seen_centre_round\":"+seenRound+",\"first_selected_centre_round\":"+selectedRound+",\"centre_pickup_kg\":"+pickup+",\"hq_mana_transfer_kg\":"+deposit+",\"trace\":["+String.join(",",trace)+"]}";
    }
    public static void main(String[] args)throws Exception{
        if(args.length!=2)throw new IllegalArgumentException("ExploreGuardProbe <own classes> <result.json>");
        TeamClassLoaderFactory factory=new TeamClassLoaderFactory(args[0]);List<String> cases=new ArrayList<>();
        for(int budget:new int[]{3000,3100,4000,4500,4550,5000})for(boolean due:new boolean[]{false,true})
            for(boolean jam:new boolean[]{false,true})for(int type:new int[]{1,2})cases.add(scenario(factory,budget,due,jam,type,type));
        List<String> cycles=new ArrayList<>();for(String pkg:new String[]{"c_mend2","c_explore0","c_explore1"})cycles.add(delivery(factory,pkg));
        List<String> forests=new ArrayList<>();forests.add(forest(factory,false));forests.add(forest(factory,true));
        String result="{\"server_games_run\":0,\"fixture_worlds\":"+(cases.size()+cycles.size()+forests.size())+",\"checks\":"+checks+",\"cases\":["+String.join(",",cases)+"],\"native_api_cycles\":["+String.join(",",cycles)+"],\"forest\":["+String.join(",",forests)+"],\"limits\":[\"Actual GameWorld, RobotControllerImpl, inventory, sensing, movement/action cooldowns and HQ resource transfer; artificial open-map cases and genuine builtin Forest map with stationary blockers.\",\"Own methods instrumented by TeamClassLoaderFactory including interface API charges; class warmup/setup and reflected host calls are unmetered.\",\"Carrier.run and individual turn-tail methods execute, but RobotPlayer loop bookkeeping, Clock.yield, exception catches and server scheduling do not. This is not a full-turn budget or native fullbot game gate.\",\"Dense remembered well coordinates are adversarial fixture inputs, not evidence of their frequency or availability in Forest.\",\"Forest carrier, memory and stationary collection-footprint occupancy are manually initialized. Other robots do not execute source; unknown sharedcentre case starts with only homeMana known, known case explicitly supplies centrepair.\"]}";
        try(PrintWriter out=new PrintWriter(args[1])){out.println(result);}
        System.out.println("{\"server_games_run\":0,\"fixture_worlds\":"+(cases.size()+cycles.size()+forests.size())+",\"checks\":"+checks+",\"result\":"+CarrierCrowdProbe.q(args[1])+"}");
    }
}
