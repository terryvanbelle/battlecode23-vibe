import battlecode.common.*;
import battlecode.instrumenter.TeamClassLoaderFactory;
import battlecode.world.GameWorld;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

/** Distinct scratch HQ-network seam target policy. Synthetic logical and actual native API fixtures. */
public final class SeamProbe {
    static int checks;
    static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    static Field field(Class<?> c,String n)throws Exception{return CarrierCrowdProbe.field(c,n);}
    static Method method(Class<?> c,String n,Class<?>...p)throws Exception{return CarrierCrowdProbe.method(c,n,p);}
    static void call(Method m,Object...a)throws Exception{ExploreGuardProbeV2.call(m,a);}
    static CarrierCrowdProbe.Fixture logical(TeamClassLoaderFactory factory)throws Exception{
        CarrierCrowdProbe.Fixture f=new CarrierCrowdProbe.Fixture(factory,"c_frontier24",false,false,0);
        field(f.g,"round").setInt(null,f.world.round);field(f.g,"here").set(null,f.world.here);
        field(f.carrier,"well").set(null,null);field(f.carrier,"crowdRejected").set(null,CarrierCrowdProbe.HOME);field(f.carrier,"crowdExploreUntil").setInt(null,74);return f;
    }
    static int explore(CarrierCrowdProbe.Fixture f,int budget)throws Exception{
        f.budget(budget);field(f.g,"round").setInt(null,f.world.round);field(f.g,"here").set(null,f.world.here);call(method(f.carrier,"crowdExplore"));
        check(f.debt.getInt(null)==0&&f.remaining.getInt(null)>0,"nativeinstrumentation debt and returnbudget");return budget-f.remaining.getInt(null);
    }
    static int count(CarrierCrowdProbe.Fixture f,String n)throws Exception{return field(f.carrier,n).getInt(null);}
    static String nativePrice(TeamClassLoaderFactory factory,int sym,int budget,boolean due)throws Exception{
        ExploreGuardProbeV2.NativeFixture n=new ExploreGuardProbeV2.NativeFixture(factory,"c_frontier24",false,true,sym);
        n.begin(12500);call(n.f.gather);check(field(n.f.carrier,"crowdRejected").get(null)!=null,"native price reaches actual crowd arm");
        n.begin(1000000);call(n.f.scan);n.f.budget(budget);
        int checks0=count(n.f,"crowdWaypointChecks"),before=n.left();call(n.f.gather);int gather=before-n.left(),after=n.left();
        List<String> tail=n.tail(due);check(n.left()>0,"native goal and measured helper tail preserve positive assigned budget");
        return "{\"initial_symmetry_mask\":"+sym+",\"budget\":"+budget+",\"counter_due\":"+due+",\"gather_cost\":"+gather+",\"after_gather\":"+after+",\"after_tail\":"+n.left()+",\"waypoint_checks\":"+(count(n.f,"crowdWaypointChecks")-checks0)+",\"target\":"+FrontierProbeV2.loc((MapLocation)field(n.f.carrier,"crowdWaypoint").get(null))+",\"tail\":{"+String.join(",",tail)+"}}";
    }
    public static void main(String[]args)throws Exception{
        if(args.length!=2)throw new IllegalArgumentException("SeamProbe <ownclasses> <result.json>");
        TeamClassLoaderFactory factory=new TeamClassLoaderFactory(args[0]);List<String> prices=new ArrayList<>();
        CarrierCrowdProbe.Fixture all=logical(factory);char[] known=new char[3600];Arrays.fill(known,(char)1);field(all.mapmem,"tile").set(null,known);
        int knownCost=explore(all,12500);check(count(all,"crowdWaypointChecks")==2&&all.world.moves==0&&field(all.carrier,"crowdWaypoint").get(null)==null,"allknownseams no movement and boundedtwoHQprojections");
        prices.add("{\"case\":\"all_known\",\"cost\":"+knownCost+"}");
        CarrierCrowdProbe.Fixture unknown=logical(factory);int unknownCost=explore(unknown,12500);MapLocation target=(MapLocation)field(unknown.carrier,"crowdWaypoint").get(null);
        check(new MapLocation(4,30).equals(target)&&count(unknown,"crowdWaypointChecks")==2,"liveoneHQmidline choosesvalidseam withoutanyresourcecoordinate");
        char[] sensed=new char[3600];sensed[4+30*60]=1;field(unknown.mapmem,"tile").set(null,sensed);unknown.world.next();explore(unknown,12500);
        check(target.equals(field(unknown.carrier,"crowdWaypoint").get(null)),"firstsensing doesnotretiretargetbeforearrival");
        prices.add("{\"case\":\"unknown_seam\",\"cost\":"+unknownCost+"}");
        CarrierCrowdProbe.Fixture low=logical(factory);field(low.carrier,"crowdCursorInit").setBoolean(null,true);field(low.carrier,"crowdCursor").setInt(null,1);
        int lowCost=explore(low,3999);check(count(low,"crowdWaypointChecks")==0&&count(low,"crowdCursor")==1&&low.world.moves==0,"scanbudgetcutoff preservesvalidcursorandmotion");
        prices.add("{\"case\":\"scan_guard\",\"cost\":"+lowCost+"}");
        CarrierCrowdProbe.Fixture cargo=logical(factory);cargo.world.weight=5;cargo.budget(12500);call(cargo.gather);
        check(field(cargo.carrier,"crowdRejected").get(null)==null&&field(cargo.carrier,"crowdRetreatHome").get(null)==null,"partialcargo clearsnewpolicy");
        CarrierCrowdProbe.Fixture role=logical(factory);field(role.carrier,"role").setInt(null,1);role.budget(12500);call(role.gather);
        check(field(role.carrier,"crowdRejected").get(null)==null&&field(role.carrier,"crowdRetreatHome").get(null)==null,"rolechange clearsnewpolicy");
        CarrierCrowdProbe.Fixture missing=logical(factory);Class<?> hqs=Class.forName("c_frontier24.HQState",true,missing.g.getClassLoader());field(hqs,"ourHQs").set(null,new MapLocation[0]);
        missing.budget(12500);call(missing.gather);check(field(missing.carrier,"crowdRejected").get(null)==null&&field(missing.carrier,"crowdRetreatHome").get(null)==null,"missingHQabortcleanly");
        CarrierCrowdProbe.Fixture deadline=logical(factory);deadline.world.here=new MapLocation(20,20);field(deadline.g,"here").set(null,deadline.world.here);field(deadline.carrier,"crowdExploreUntil").setInt(null,50);
        deadline.budget(12500);call(deadline.gather);check(CarrierCrowdProbe.HQ.equals(field(deadline.carrier,"crowdRetreatHome").get(null))&&count(deadline,"trips")==0,"deadline startsdirectretreatnoemptydeliverytrip");
        deadline.world.round=count(deadline,"crowdRetreatUntil");field(deadline.g,"round").setInt(null,deadline.world.round);deadline.budget(12500);call(deadline.gather);
        check(field(deadline.carrier,"crowdRetreatHome").get(null)==null,"retreatexpiry resumesbaselineevenifhomeunreached");
        CarrierCrowdProbe.Fixture four=logical(factory);Class<?> fourHqs=Class.forName("c_frontier24.HQState",true,four.g.getClassLoader());
        field(fourHqs,"ourHQs").set(null,new MapLocation[]{new MapLocation(0,0),new MapLocation(6,30),new MapLocation(7,30),new MapLocation(11,48)});
        int fourCost=explore(four,12500);check(count(four,"crowdWaypointChecks")==8,"fourHQscanexaminesexactlyeightprojections");
        prices.add("{\"case\":\"four_HQ\",\"cost\":"+fourCost+"}");
        CarrierCrowdProbe.Fixture ordinary=new CarrierCrowdProbe.Fixture(factory,"c_frontier24",false,false,0);field(ordinary.carrier,"crowdTurns").setInt(null,0);ordinary.tick();
        check(count(ordinary,"crowdSearchStarts")==0&&CarrierCrowdProbe.HOME.equals(field(ordinary.carrier,"well").get(null)),"ordinaryemptywait has no premature episode");
        CarrierCrowdProbe.Fixture alternative=new CarrierCrowdProbe.Fixture(factory,"c_frontier24",false,true,0);alternative.tick();
        check(count(alternative,"crowdSearchStarts")==0&&CarrierCrowdProbe.NEW.equals(field(alternative.carrier,"well").get(null)),"knownalternative keeps existing switch");
        CarrierCrowdProbe.Fixture entry=logical(factory);entry.budget(5999);call(entry.gather);
        check(entry.world.moves==0&&count(entry,"crowdWaypointChecks")==0&&count(entry,"crowdSearchTurns")==0,"lowentrybudget defers goal scan and movement");
        CarrierCrowdProbe.Fixture stale=logical(factory);char[] walls=new char[3600];walls[4+30*60]=3;field(stale.mapmem,"tile").set(null,walls);field(stale.carrier,"crowdWaypoint").set(null,new MapLocation(4,30));
        explore(stale,12500);check(field(stale.carrier,"crowdWaypoint").get(null)==null,"newlyknownwall retires stalegoal");
        CarrierCrowdProbe.Fixture blocked=logical(factory);blocked.world.freezeMotion=true;field(blocked.carrier,"crowdWaypoint").set(null,new MapLocation(4,30));field(blocked.carrier,"crowdWaypointLastPos").set(null,blocked.world.here);
        for(int i=0;i<3;i++){explore(blocked,12500);blocked.world.next();}
        check(count(blocked,"crowdWaypointChecks")>0,"threestationarycalls retire and rescan blockedgoal");
        ExploreGuardProbeV2.NativeFixture flee=new ExploreGuardProbeV2.NativeFixture(factory,"c_frontier24",false);
        flee.world.spawnRobot(500,RobotType.LAUNCHER,new MapLocation(6,14),Team.B);flee.begin(12500);field(flee.f.carrier,"well").set(null,null);field(flee.f.carrier,"crowdRejected").set(null,CarrierCrowdProbe.HOME);field(flee.f.carrier,"crowdExploreUntil").setInt(null,74);
        call(method(flee.f.g,"startTurn"));call(method(flee.f.carrier,"run"));
        check(field(flee.f.carrier,"state").getChar(null)=='F'&&count(flee.f,"crowdSearchTurns")==0,"actualnative enemy fighter preserves flee priority");
        ExploreGuardProbeV2.NativeFixture current=new ExploreGuardProbeV2.NativeFixture(factory,"c_frontier24",false);
        current.owner.setLocation(new MapLocation(28,10));field(GameWorld.class,"currentRound").setInt(current.world,54);current.begin(12500);
        Direction[] currents=(Direction[])field(GameWorld.class,"currents").get(current.world);currents[28+10*60]=Direction.EAST;current.world.processEndOfRound();
        check(new MapLocation(29,10).equals(current.owner.getLocation()),"actualnative outwardcurrent exceeds radius24 before nextturn");
        current.begin(12500);field(current.f.carrier,"well").set(null,null);field(current.f.carrier,"crowdRejected").set(null,CarrierCrowdProbe.HOME);field(current.f.carrier,"crowdExploreUntil").setInt(null,74);call(current.f.gather);
        check(count(current.f,"crowdRetreats")==1&&CarrierCrowdProbe.HQ.equals(field(current.f.carrier,"crowdRetreatHome").get(null)),"nextturn boundarycheck begins native stableHQretreat");
        List<String> nativePrices=new ArrayList<>();for(int sym:new int[]{7,2})for(int budget:new int[]{6000,6100,6500,7000,10000})for(boolean due:new boolean[]{false,true})nativePrices.add(nativePrice(factory,sym,budget,due));
        List<String> forests=new ArrayList<>();for(int sym:new int[]{7,2}){forests.add(FrontierProbeV2.forest(factory,"c_frontier0",sym));forests.add(FrontierProbeV2.forest(factory,"c_frontier12",sym));forests.add(FrontierProbeV2.forest(factory,"c_frontier24",sym));}
        String result="{\"server_games_run\":0,\"logical_checks\":"+checks+",\"native_checks\":"+FrontierProbeV2.checks+",\"native_setup_checks\":"+ExploreGuardProbeV2.checks+",\"logical_prices\":["+String.join(",",prices)+"],\"native_prices\":["+String.join(",",nativePrices)+"],\"forest\":["+String.join(",",forests)+"],\"limits\":[\"Engine provenance supplied by runner; syntheticlogical and actualnativeRC/world fixtures use manuallyinitializedownstate/inertotherrobots.\",\"HQseam targets derive fromknownalliedHQrows/columns andmapmidlines; no resourcecoordinates in source. Thisis targetedwaypointexploration, notfullmapcoverage.\",\"Full RobotPlayer/bookkeeping/nearmiss/yield/scheduler andnativefullbotgame gatesremainpending. No screen/promotion or universal safetyclaim.\"]}";
        try(PrintWriter out=new PrintWriter(args[1])){out.println(result);}System.out.println("{\"server_games_run\":0,\"logical_checks\":"+checks+",\"native_checks\":"+FrontierProbeV2.checks+",\"result\":"+CarrierCrowdProbe.q(args[1])+"}");
    }
}
