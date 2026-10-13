import battlecode.common.*;
import battlecode.instrumenter.TeamClassLoaderFactory;
import battlecode.world.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;

/** Extra regression for unique coordinate retirement in the separately frozen seam repair. */
public final class SeamRepairProbe {
    static int checks;
    static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    static Field field(Class<?> c,String n)throws Exception{return CarrierCrowdProbe.field(c,n);}
    static Method method(Class<?> c,String n,Class<?>...p)throws Exception{return CarrierCrowdProbe.method(c,n,p);}
    static void call(Method m,Object...a)throws Exception{ExploreGuardProbeV2.call(m,a);}
    static int count(CarrierCrowdProbe.Fixture f,String n)throws Exception{return field(f.carrier,n).getInt(null);}
    static void retired(CarrierCrowdProbe.Fixture f,MapLocation...locs)throws Exception{
        MapLocation[] values=new MapLocation[8];System.arraycopy(locs,0,values,0,locs.length);field(f.carrier,"crowdRetired").set(null,values);field(f.carrier,"crowdRetiredCount").setInt(null,locs.length);
    }
    static boolean has(CarrierCrowdProbe.Fixture f,MapLocation l)throws Exception{
        f.budget(1000000);return (Boolean)method(f.carrier,"crowdWasRetired",MapLocation.class).invoke(null,l);
    }
    static String blocked(TeamClassLoaderFactory factory,int symmetry)throws Exception{
        ExploreGuardProbeV2.NativeFixture n=new ExploreGuardProbeV2.NativeFixture(factory,"c_frontier24",false,true,symmetry);
        MapLocation start=n.owner.getLocation();int id=600;
        for(int x=start.x-1;x<=start.x+1;x++)for(int y=start.y-1;y<=start.y+1;y++){
            MapLocation at=new MapLocation(x,y);if(at.equals(start)||n.world.getGameMap().getWallArray()[x+60*y]||n.world.getRobot(at)!=null)continue;
            n.world.spawnRobot(id++,RobotType.CARRIER,at,Team.A);
        }
        retired(n.f,new MapLocation(30,48));field(n.f.carrier,"well").set(null,null);field(n.f.carrier,"crowdRejected").set(null,CarrierCrowdProbe.HOME);
        field(n.f.carrier,"crowdExploreUntil").setInt(null,74);List<String> trace=new ArrayList<>();MapLocation first=null,next=null;int minLeft=12500;
        for(int i=0;i<4;i++){
            n.begin(12500);call(method(n.telemetry,"startTurn"));call(method(n.f.g,"startTurn"));call(method(n.comms,"startTurn"));call(method(n.hqs,"refresh"));call(method(n.f.carrier,"run"));
            MapLocation target=(MapLocation)field(n.f.carrier,"crowdWaypoint").get(null);if(i==0)first=target;else if(target!=null&&!target.equals(first))next=target;
            check(start.equals(n.owner.getLocation()),"native owner remains physically blocked");
            trace.add("{\"round\":"+n.world.getCurrentRound()+",\"here\":"+FrontierProbeV2.loc(n.owner.getLocation())+",\"target\":"+FrontierProbeV2.loc(target)+",\"retired_count\":"+count(n.f,"crowdRetiredCount")+"}");
            call(method(n.telemetry,"endTurn",int.class),n.world.getCurrentRound());call(method(n.f.mapmem,"process",int.class),1500);call(method(n.distance,"think",int.class),1500);
            if(n.left()>=400)call(method(n.telemetry,"indicator"));call(method(n.telemetry,"pad"));minLeft=Math.min(minLeft,n.left());check(n.left()>0,"nativeblocked regression returns within12500");n.world.processEndOfRound();
        }
        check(new MapLocation(30,30).equals(first),"bestremaininggoalhas two actualForestHQ aliases");
        check(first!=null&&next!=null&&!first.equals(next)&&has(n.f,first),"blockedbest is retired bycoordinate and distinctnext selected");
        check(!(Boolean)method(n.f.carrier,"crowdHQGoal",MapLocation.class).invoke(null,next),"distinctnext is not an occupied alliedHQ");
        return "{\"initial_symmetry_mask\":"+symmetry+",\"prior_retired_fixture_point\":[30,48],\"first_target\":"+FrontierProbeV2.loc(first)+",\"distinct_next_target\":"+FrontierProbeV2.loc(next)+",\"retired_count\":"+count(n.f,"crowdRetiredCount")+",\"min_after_helpers\":"+minLeft+",\"trace\":["+String.join(",",trace)+"]}";
    }
    public static void main(String[]args)throws Exception{
        if(args.length!=2)throw new IllegalArgumentException("SeamRepairProbe <ownclasses> <result.json>");
        SeamProbe.main(new String[]{args[0],args[1]+".base.json"});TeamClassLoaderFactory factory=new TeamClassLoaderFactory(args[0]);
        for(int mode=0;mode<3;mode++){
            CarrierCrowdProbe.Fixture f=SeamProbe.logical(factory);retired(f,new MapLocation(4,30));
            if(mode==0)field(f.carrier,"role").setInt(null,1);else if(mode==1)f.world.weight=5;else field(f.carrier,"crowdExploreUntil").setInt(null,50);
            f.budget(12500);call(f.gather);check(count(f,"crowdRetiredCount")==0,"retirement resets on role/cargo/expiry");
        }
        CarrierCrowdProbe.Fixture fresh=SeamProbe.logical(factory);retired(fresh,new MapLocation(4,30));field(fresh.carrier,"crowdRejected").set(null,null);field(fresh.carrier,"well").set(null,CarrierCrowdProbe.HOME);
        fresh.budget(12500);call(fresh.gather);check(count(fresh,"crowdSearchStarts")==1&&count(fresh,"crowdRetiredCount")==0,"new episode resets priorretirements");
        CarrierCrowdProbe.Fixture known=SeamProbe.logical(factory);retired(known,new MapLocation(4,30));known.world.shared[6]=(2<<12)|known.world.enc(CarrierCrowdProbe.NEW);known.budget(12500);call(known.gather);
        check(CarrierCrowdProbe.NEW.equals(field(known.carrier,"well").get(null))&&count(known,"crowdRetiredCount")==0,"accepting knownalternative endsretirement episode");
        CarrierCrowdProbe.Fixture arrived=SeamProbe.logical(factory);arrived.world.here=new MapLocation(4,30);field(arrived.g,"here").set(null,arrived.world.here);field(arrived.carrier,"crowdWaypoint").set(null,arrived.world.here);
        SeamProbe.explore(arrived,12500);check(count(arrived,"crowdRetiredCount")==1&&count(arrived,"crowdWaypointsReached")==1,"actualarrival retirescoordinate");
        field(arrived.carrier,"crowdWaypoint").set(null,arrived.world.here);SeamProbe.explore(arrived,12500);check(count(arrived,"crowdRetiredCount")==1,"duplicate retirement doesnotgrowboundedset");
        CarrierCrowdProbe.Fixture exhausted=SeamProbe.logical(factory);Class<?> hqs=Class.forName("c_frontier24.HQState",true,exhausted.g.getClassLoader());
        field(hqs,"ourHQs").set(null,new MapLocation[]{new MapLocation(0,0),new MapLocation(6,30),new MapLocation(7,30),new MapLocation(11,48)});
        retired(exhausted,new MapLocation(30,0),new MapLocation(0,30),new MapLocation(30,30),new MapLocation(6,30),new MapLocation(7,30),new MapLocation(30,48),new MapLocation(11,30));
        SeamProbe.explore(exhausted,12500);check(field(exhausted.carrier,"crowdWaypoint").get(null)==null&&exhausted.world.moves==0&&count(exhausted,"crowdRetiredCount")==7,"all retired aliases causeboundedwait");
        List<String> blocked=new ArrayList<>();for(int symmetry:new int[]{7,2})blocked.add(blocked(factory,symmetry));
        String base=new String(Files.readAllBytes(Paths.get(args[1]+".base.json")),"UTF-8").trim();
        String result="{\"server_games_run\":0,\"repair_checks\":"+checks+",\"base\":"+base+",\"native_blocked_alias_regressions\":["+String.join(",",blocked)+"],\"limits\":[\"Additional retirement tests distinguish unique coordinate exclusion from immediate reassignment. All nativeworld/host/fullRobotPlayer limits frombase stillapply.\",\"Prior retired(30,48) and expected(30,30) are diagnostic fixturecoordinates derivedfromactualmap/HQstate; neither is a decisionconstant.\"]}";
        try(PrintWriter out=new PrintWriter(args[1])){out.println(result);}System.out.println("{\"server_games_run\":0,\"repair_checks\":"+checks+",\"result\":"+CarrierCrowdProbe.q(args[1])+"}");
    }
}
