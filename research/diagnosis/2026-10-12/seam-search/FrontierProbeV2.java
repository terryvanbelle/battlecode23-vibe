import battlecode.common.*;
import battlecode.instrumenter.TeamClassLoaderFactory;
import battlecode.world.*;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

/** Scratch only: synthetic logical checks plus actual native RC state fixtures; zero server games. */
public final class FrontierProbeV2 {
    static int checks;
    static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    static Field field(Class<?> c,String n)throws Exception{return CarrierCrowdProbe.field(c,n);}
    static Method method(Class<?> c,String n,Class<?>...p)throws Exception{return CarrierCrowdProbe.method(c,n,p);}
    static void call(Method m,Object...args)throws Exception{ExploreGuardProbeV2.call(m,args);}
    static void here(CarrierCrowdProbe.Fixture f)throws Exception{field(f.g,"here").set(null,f.world.here);field(f.g,"round").setInt(null,f.world.round);}
    static int integer(CarrierCrowdProbe.Fixture f,String n)throws Exception{return field(f.carrier,n).getInt(null);}
    static CarrierCrowdProbe.Fixture logical(TeamClassLoaderFactory factory)throws Exception{
        CarrierCrowdProbe.Fixture f=new CarrierCrowdProbe.Fixture(factory,"c_frontier24",false,false,0);here(f);
        field(f.carrier,"well").set(null,null);field(f.carrier,"crowdRejected").set(null,CarrierCrowdProbe.HOME);
        field(f.carrier,"crowdExploreUntil").setInt(null,74);return f;
    }
    static int explore(CarrierCrowdProbe.Fixture f,int budget)throws Exception{
        f.budget(budget);here(f);call(method(f.carrier,"crowdExplore"));check(f.debt.getInt(null)==0,"pending debt flushed");
        check(f.remaining.getInt(null)>0,"synthetic bounded exploration returns positivebudget");return budget-f.remaining.getInt(null);
    }
    static List<String> logicalChecks(TeamClassLoaderFactory factory)throws Exception{
        List<String> result=new ArrayList<>();
        CarrierCrowdProbe.Fixture all=logical(factory);char[] tile=new char[3600];Arrays.fill(tile,(char)1);field(all.mapmem,"tile").set(null,tile);
        int allCost=explore(all,12500);check(integer(all,"crowdWaypointChecks")==16&&field(all.carrier,"crowdWaypoint").get(null)==null&&all.world.moves==0,"all-known boundedscan no movement");
        int cursor=integer(all,"crowdCursor");explore(all,12500);check(integer(all,"crowdCursor")==((cursor+16)%100),"persistentcursor traverses laterbatch");
        result.add("{\"case\":\"all_known\",\"cost\":"+allCost+"}");
        CarrierCrowdProbe.Fixture later=logical(factory);char[] laterTiles=tile.clone();laterTiles[21+15*60]=0;field(later.mapmem,"tile").set(null,laterTiles);
        field(later.carrier,"crowdCursorInit").setBoolean(null,true);field(later.carrier,"crowdCursor").setInt(null,7);
        explore(later,12500);check(field(later.carrier,"crowdWaypoint").get(null)==null&&integer(later,"crowdCursor")==23,"first16invalid do not hide seventeenth permanently");
        int laterCost=explore(later,12500);check(new MapLocation(21,15).equals(field(later.carrier,"crowdWaypoint").get(null)),"valid seventeenth selected nextboundedbatch");
        laterTiles[21+15*60]=1;explore(later,12500);check(new MapLocation(21,15).equals(field(later.carrier,"crowdWaypoint").get(null)),"firstsensing doesnotretire target beforeactualarrival");
        result.add("{\"case\":\"seventeenth_valid\",\"cost\":"+laterCost+"}");
        CarrierCrowdProbe.Fixture low=logical(factory);field(low.carrier,"crowdCursorInit").setBoolean(null,true);field(low.carrier,"crowdCursor").setInt(null,33);
        int lowCost=explore(low,3999);check(integer(low,"crowdCursor")==33&&integer(low,"crowdWaypointChecks")==0&&low.world.moves==0,"budgetcutoff preservescursor andmotion");
        result.add("{\"case\":\"scan_guard\",\"cost\":"+lowCost+"}");
        CarrierCrowdProbe.Fixture ended=logical(factory);ended.world.here=new MapLocation(20,20);here(ended);field(ended.carrier,"crowdExploreUntil").setInt(null,50);
        ended.budget(12500);call(ended.gather);check(field(ended.carrier,"crowdRejected").get(null)==null&&CarrierCrowdProbe.HQ.equals(field(ended.carrier,"crowdRetreatHome").get(null))&&integer(ended,"trips")==0,"deadline beginsstableHQretreatwithoutemptydeliver");
        MapLocation retreat=(MapLocation)field(ended.carrier,"crowdRetreatHome").get(null);ended.world.next();here(ended);ended.budget(3999);int moves=ended.world.moves;call(ended.gather);
        check(retreat.equals(field(ended.carrier,"crowdRetreatHome").get(null))&&ended.world.moves==moves,"retreat retainsHQandmovementguard");
        ended.world.round=integer(ended,"crowdRetreatUntil");here(ended);ended.budget(12500);call(ended.gather);check(field(ended.carrier,"crowdRetreatHome").get(null)==null,"retreatexpires evenifhomeunreached");
        CarrierCrowdProbe.Fixture missing=logical(factory);Class<?> hqs=Class.forName("c_frontier24.HQState",true,missing.g.getClassLoader());field(hqs,"ourHQs").set(null,new MapLocation[0]);
        missing.budget(12500);call(missing.gather);check(field(missing.carrier,"crowdRejected").get(null)==null&&field(missing.carrier,"crowdRetreatHome").get(null)==null,"missingHQabortsunknownexplorationcleanly");
        CarrierCrowdProbe.Fixture cargo=logical(factory);cargo.world.weight=5;here(cargo);cargo.budget(12500);call(cargo.gather);
        check(field(cargo.carrier,"crowdRejected").get(null)==null&&field(cargo.carrier,"crowdRetreatHome").get(null)==null&&integer(cargo,"crowdSearchStarts")==0,"partialcargo disablesnewepisode");
        CarrierCrowdProbe.Fixture role=logical(factory);field(role.carrier,"role").setInt(null,1);role.budget(12500);call(role.gather);
        check(field(role.carrier,"crowdRejected").get(null)==null&&field(role.carrier,"crowdRetreatHome").get(null)==null,"rolechange disablessearchretreat");
        for(int width:new int[]{20,21,23,24,59,60}){
            CarrierCrowdProbe.Fixture edge=logical(factory);field(edge.g,"W").setInt(null,width);field(edge.g,"H").setInt(null,width);
            field(edge.mapmem,"tile").set(null,new char[width*width]);int total=((width+5)/6)*((width+5)/6);
            field(edge.carrier,"crowdCursorInit").setBoolean(null,true);field(edge.carrier,"crowdCursor").setInt(null,total-1);explore(edge,12500);
            MapLocation target=(MapLocation)field(edge.carrier,"crowdWaypoint").get(null);check(target==null||target.x>=0&&target.y>=0&&target.x<width&&target.y<width,"latticeboundsonnonmultiplewidth");
        }
        return result;
    }
    static String forest(TeamClassLoaderFactory factory,String pkg,int symmetry)throws Exception{
        ExploreGuardProbeV2.NativeFixture n=new ExploreGuardProbeV2.NativeFixture(factory,pkg,false,true,symmetry);List<String> trace=new ArrayList<>();
        MapLocation ca=new MapLocation(29,48),cb=new MapLocation(30,48);int seenRound=0,selectedRound=0,pickups=0,deposits=0,firstEpisode=0,firstEpisodeUntil=0,firstEpisodeSeen=0,peak=0,maxChecks=0;
        for(int i=0;i<160;i++){
            n.begin(12500);call(method(n.telemetry,"startTurn"));call(method(n.f.g,"startTurn"));call(method(n.comms,"startTurn"));call(method(n.hqs,"refresh"));
            int bank0=0;for(InternalRobot r:n.world.getObjectInfo().robots())if(r.getTeam()==Team.A&&r.getType()==RobotType.HEADQUARTERS)bank0+=r.getResource(ResourceType.MANA);
            int cargo0=n.owner.getResource(ResourceType.MANA),checks0=integer(n.f,"crowdWaypointChecks");call(method(n.f.carrier,"run"));int round=n.world.getCurrentRound();
            maxChecks=Math.max(maxChecks,integer(n.f,"crowdWaypointChecks")-checks0);peak=Math.max(peak,12500-n.left());
            MapLocation well=(MapLocation)field(n.f.carrier,"well").get(null),target=(MapLocation)field(n.f.carrier,"crowdWaypoint").get(null),home=(MapLocation)field(n.f.carrier,"crowdRetreatHome").get(null);
            int ns=field(n.f.mapmem,"nSeenWell").getInt(null);MapLocation[] seen=(MapLocation[])field(n.f.mapmem,"seenWell").get(null);boolean learned=false;
            for(int j=0;j<ns;j++)if(ca.equals(seen[j])||cb.equals(seen[j]))learned=true;
            if(integer(n.f,"crowdSearchStarts")>0&&firstEpisode==0){firstEpisode=round;firstEpisodeUntil=integer(n.f,"crowdExploreUntil");}
            if(learned&&seenRound==0)seenRound=round;if(learned&&round<firstEpisodeUntil&&firstEpisodeSeen==0)firstEpisodeSeen=round;
            if((ca.equals(well)||cb.equals(well))&&selectedRound==0)selectedRound=round;
            if(n.owner.getResource(ResourceType.MANA)>cargo0&&(ca.equals(well)||cb.equals(well)))pickups+=n.owner.getResource(ResourceType.MANA)-cargo0;
            int bank1=0;for(InternalRobot r:n.world.getObjectInfo().robots())if(r.getTeam()==Team.A&&r.getType()==RobotType.HEADQUARTERS)bank1+=r.getResource(ResourceType.MANA);deposits+=Math.max(0,bank1-bank0);
            if(i<48||learned&&trace.size()<52||deposits>0)trace.add("{\"round\":"+round+",\"state\":"+CarrierCrowdProbe.q(String.valueOf(field(n.f.carrier,"state").getChar(null)))+",\"here\":["+n.owner.getLocation().x+","+n.owner.getLocation().y+"],\"target\":"+loc(target)+",\"retreat_HQ\":"+loc(home)+",\"well\":"+loc(well)+",\"seen_centre\":"+learned+",\"mana\":"+n.owner.getResource(ResourceType.MANA)+",\"work\":"+(12500-n.left())+"}");
            call(method(n.telemetry,"endTurn",int.class),round);call(method(n.f.mapmem,"process",int.class),1500);call(method(n.distance,"think",int.class),1500);
            if(n.left()>=400)call(method(n.telemetry,"indicator"));call(method(n.telemetry,"pad"));check(n.left()>0,"nativeforestCarrierplushelpersreturnswithin12500");n.world.processEndOfRound();if(deposits>0)break;
        }
        check(maxChecks<=16,"nativeboundedcandidateevaluations");
        return "{\"package\":"+CarrierCrowdProbe.q(pkg)+",\"initial_symmetry_mask\":"+symmetry+",\"first_episode_round\":"+firstEpisode+",\"first_episode_until\":"+firstEpisodeUntil+",\"first_episode_centre_seen_round\":"+firstEpisodeSeen+",\"first_seen_centre_round\":"+seenRound+",\"first_selected_centre_round\":"+selectedRound+",\"centre_pickup_kg\":"+pickups+",\"hq_mana_transfer_kg\":"+deposits+",\"search_starts\":"+integer(n.f,"crowdSearchStarts")+",\"search_turns\":"+integer(n.f,"crowdSearchTurns")+",\"waypoint_checks\":"+integer(n.f,"crowdWaypointChecks")+",\"waypoints_reached\":"+integer(n.f,"crowdWaypointsReached")+",\"retreats\":"+integer(n.f,"crowdRetreats")+",\"peak_shared_plus_Carrier_run\":"+peak+",\"trace\":["+String.join(",",trace)+"]}";
    }
    static String loc(MapLocation l){return l==null?"null":"["+l.x+","+l.y+"]";}
    public static void main(String[]args)throws Exception{
        if(args.length!=2)throw new IllegalArgumentException("FrontierProbeV2 <own scratch classes> <result.json>");
        TeamClassLoaderFactory factory=new TeamClassLoaderFactory(args[0]);List<String> logic=logicalChecks(factory),forests=new ArrayList<>();
        for(int symmetry:new int[]{7,2}){forests.add(forest(factory,"c_frontier12",symmetry));forests.add(forest(factory,"c_frontier24",symmetry));}
        String result="{\"server_games_run\":0,\"checks\":"+checks+",\"logical_prices\":["+String.join(",",logic)+"],\"forest\":["+String.join(",",forests)+"],\"limits\":[\"Local source-built engine prototype only until official execution. Synthetic logical cases price own instructions/API charges; actual Forest cases use native controller/world physics with manuallyinitialized ownstate and inertotherrobots.\",\"No full RobotPlayer loop/yield/server scheduling or native fullbotgame; no generalturnsafety, completecoverage or fieldstrength claim.\",\"TargetswithinHQradius24 do notbound everyroute; atmosttwoownmoves plus anendroundcurrentpush can overshootbefore nextcheck. Retreat16is a boundedattempt, notguaranteed homearrival.\"]}";
        try(PrintWriter out=new PrintWriter(args[1])){out.println(result);}System.out.println("{\"server_games_run\":0,\"checks\":"+checks+",\"result\":"+CarrierCrowdProbe.q(args[1])+"}");
    }
}
