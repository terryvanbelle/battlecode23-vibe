import battlecode.common.*;
import battlecode.instrumenter.TeamClassLoaderFactory;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

/** Zero-game own-code checks; every controller event and its physical consequences are synthetic. */
public final class Explore1Probe {
    static int checks;
    static Field field(Class<?> c,String n)throws Exception{return CarrierCrowdProbe.field(c,n);}
    static Method method(Class<?> c,String n,Class<?>...p)throws Exception{return CarrierCrowdProbe.method(c,n,p);}
    static String q(String s){return CarrierCrowdProbe.q(s);}
    static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    static final MapLocation HOME=CarrierCrowdProbe.HOME,NEW=CarrierCrowdProbe.NEW;
    static void invoke(Method m)throws Exception{try{m.invoke(null);}catch(InvocationTargetException e){throw new IllegalStateException(e.getCause());}}
    static int count(CarrierCrowdProbe.Fixture f,String n)throws Exception{return field(f.carrier,n).getInt(null);}
    static void here(CarrierCrowdProbe.Fixture f)throws Exception{field(f.g,"round").setInt(null,f.world.round);field(f.g,"here").set(null,f.world.here);}
    static void direct(CarrierCrowdProbe.Fixture f,int budget)throws Exception{f.budget(budget);here(f);invoke(f.gather);check(f.debt.getInt(null)==0&&f.remaining.getInt(null)>0,"guarded gather returns within synthetic budget");}
    static int noteCost(CarrierCrowdProbe.Fixture f)throws Exception{f.budget(12500);invoke(method(f.carrier,"note"));check(f.debt.getInt(null)==0,"note debt flushed");return 12500-f.remaining.getInt(null);}
    static int indicatorCost(CarrierCrowdProbe.Fixture f)throws Exception{
        Class<?> tele=Class.forName(f.pkg+".Telemetry",true,f.g.getClassLoader());
        f.budget(1000000);field(tele,"ttype").setInt(null,1);field(tele,"letters").set(null,method(tele,"letters",int.class).invoke(null,1));
        f.budget(12500);invoke(method(tele,"indicator"));check(f.debt.getInt(null)==0,"indicator debt flushed");return 12500-f.remaining.getInt(null);
    }
    public static void main(String[] args)throws Exception{
        if(args.length!=2)throw new IllegalArgumentException("Explore1Probe <scratch classes> <result.json>");
        TeamClassLoaderFactory factory=new TeamClassLoaderFactory(args[0]);List<String> cases=new ArrayList<>();
        CarrierCrowdProbe.Fixture base=new CarrierCrowdProbe.Fixture(factory,"c_mend2",true,false,0),zero=new CarrierCrowdProbe.Fixture(factory,"c_explore0",true,false,0);
        for(int i=0;i<80;i++){
            base.tick();zero.tick();check(base.world.here.equals(zero.world.here)&&base.world.weight==zero.world.weight
                &&Objects.equals(field(base.carrier,"well").get(null),field(zero.carrier,"well").get(null))
                &&field(base.carrier,"state").getChar(null)==field(zero.carrier,"state").getChar(null),"zero arm logical tick identity");
        }
        check(zero.xTurns==0&&zero.returnedSame&&zero.peakCost==base.peakCost,"zero arm native tick/crowd behavior identity");cases.add(base.json("unknown_alternative"));cases.add(zero.json("zero_arm"));
        CarrierCrowdProbe.Fixture fix=new CarrierCrowdProbe.Fixture(factory,"c_explore1",true,false,0);for(int i=0;i<100&&fix.world.delivered==0;i++)fix.tick();
        check(fix.xTurns==3&&fix.sawNew&&fix.selectedNew&&fix.world.delivered==30,"enabled arm discovers/selects well and calls own deliver with mock30kg transfer");
        check(count(fix,"crowdSearchStarts")==1&&count(fix,"crowdSearchTurns")==3&&count(fix,"crowdSearchFound")==1,"start/explore/new-site outcome counters");cases.add(fix.json("enabled_discovery"));
        CarrierCrowdProbe.Fixture guard=new CarrierCrowdProbe.Fixture(factory,"c_explore1",false,false,0);guard.tick();int moves=guard.world.moves;direct(guard,2999);
        check(guard.world.moves==moves&&count(guard,"crowdSearchTurns")==0&&field(guard.carrier,"well").get(null)==null&&field(guard.carrier,"state").getChar(null)=='W',"active guard defers extra search/movement");cases.add(guard.json("active_guard"));
        CarrierCrowdProbe.Fixture startup=new CarrierCrowdProbe.Fixture(factory,"c_explore1",false,false,0);direct(startup,2000);
        check(field(startup.carrier,"crowdRejected").get(null)==null&&count(startup,"crowdSearchStarts")==0,"insufficient startup budget keeps baseline no-alternative arm");cases.add(startup.json("startup_guard"));
        CarrierCrowdProbe.Fixture timeout=new CarrierCrowdProbe.Fixture(factory,"c_explore1",false,false,0);timeout.tick();int until=field(timeout.carrier,"crowdExploreUntil").getInt(null);
        while(timeout.world.round<=until)timeout.tick();check(field(timeout.carrier,"crowdRejected").get(null)==null&&timeout.xTurns==11,"12-round deadline bounds subsequent exploratory turns");cases.add(timeout.json("deadline"));
        CarrierCrowdProbe.Fixture cargo=new CarrierCrowdProbe.Fixture(factory,"c_explore1",true,false,5);cargo.tick();cargo.tick();check(cargo.returnedSame&&count(cargo,"crowdSearchStarts")==0,"partial cargo retains baseline arm");cases.add(cargo.json("partial_cargo"));
        CarrierCrowdProbe.Fixture known=new CarrierCrowdProbe.Fixture(factory,"c_explore1",false,true,0);known.tick();check(NEW.equals(field(known.carrier,"well").get(null))&&count(known,"crowdSearchStarts")==0,"known alternative avoids experimental search");cases.add(known.json("known_alternative"));
        CarrierCrowdProbe.Fixture role=new CarrierCrowdProbe.Fixture(factory,"c_explore1",false,false,0);role.tick();field(role.carrier,"role").setInt(null,1);role.tick();check(field(role.carrier,"crowdRejected").get(null)==null,"role change releases rejection");cases.add(role.json("role_change"));
        CarrierCrowdProbe.Fixture outside=new CarrierCrowdProbe.Fixture(factory,"c_explore1",false,false,0);outside.world.here=new MapLocation(5,12);outside.world.freezeMotion=true;outside.tick();
        check(!outside.switched&&count(outside,"crowdSearchStarts")==0&&field(outside.carrier,"crowdTurns").getInt(null)==6,"d2=9 trigger unchanged");cases.add(outside.json("outside_radius"));
        CarrierCrowdProbe.Fixture dense=new CarrierCrowdProbe.Fixture(factory,"c_explore1",false,false,0);dense.tick();
        for(int i=1;i<16;i++)dense.world.shared[5+i]=(2<<12)|dense.world.enc(new MapLocation(10+i%5,20+i/5));
        MapLocation[] seen=new MapLocation[32];int[] types=new int[32];for(int i=0;i<32;i++){seen[i]=new MapLocation(10+i%8,30+i/8);types[i]=2;}
        field(dense.mapmem,"seenWell").set(null,seen);field(dense.mapmem,"seenWellType").set(null,types);field(dense.mapmem,"nSeenWell").setInt(null,32);
        direct(dense,3100);int denseCost=3100-dense.remaining.getInt(null);
        check(field(dense.carrier,"well").get(null)!=null&&field(dense.carrier,"crowdOutcomeWell").get(null)!=null&&count(dense,"crowdSearchFound")==0,"dense32seen16shared guarded selection completes without claiming pickup");cases.add(dense.json("dense_guard"));
        Method pack=method(fix.carrier,"crowdTrace",int.class,int.class,int.class);fix.budget(1000000);
        int packed=(Integer)pack.invoke(null,1,3,1),max=(Integer)pack.invoke(null,99999,99999,99999);
        check((packed>>>20)==1&&((packed>>>8)&4095)==3&&(packed&255)==1,"trace packing decodes start/explore/outcome");
        check(max==0x0fffffff,"trace counters saturate independently without sign overflow");
        int baseNote=noteCost(base),zeroNote=noteCost(zero),newNote=noteCost(fix),baseIndicator=indicatorCost(base),newIndicator=indicatorCost(fix);
        check(baseNote==zeroNote&&field(zero.g,"extra").get(null).equals(""),"zero-arm note identity with no experimental counter");
        check(field(fix.g,"extra").get(null).equals(",cx="+packed),"visible packed trace");
        Class<?> tele=Class.forName(fix.pkg+".Telemetry",true,fix.g.getClassLoader());fix.budget(1000000);
        String indicator=(String)method(tele,"indicatorString",char.class,int.class,String.class,int.class,int.class,int.class,int.class,int.class,int.class,int.class,String.class)
            .invoke(null,'X',11,"2",0,0,0,1,0,0,0,",cx="+max);
        check(indicator.length()<=64&&indicator.contains(",cx="+max),"max-packed trace fits ordinary carrier indicator");
        checks += CarrierCrowdProbe.checks;
        String result="{\"games_run\":0,\"checks\":"+checks+",\"dense_gather_cost\":"+denseCost+",\"note_costs\":{\"base\":"+baseNote+",\"zero\":"+zeroNote+",\"enabled\":"+newNote+"},\"indicator_costs\":{\"base\":"+baseIndicator+",\"enabled\":"+newIndicator+"},\"packed_trace\":"+packed+",\"cases\":["+String.join(",",cases)+"],\"limits\":[\"Own instructions/API charges instrumented; RobotController body, world positions/cooldowns/resources/transfer outcomes are synthetic.\",\"Logical fixture does not execute full RobotPlayer run or native GameWorld; a real own-game delivery gate remains required.\",\"cx must be decoded per robot before aggregation; fields saturate at255/4095/255; absence after indicator truncation is unknown.\"]}";
        try(PrintWriter out=new PrintWriter(args[1])){out.println(result);}
        System.out.println("{\"games_run\":0,\"checks\":"+checks+",\"dense_gather_cost\":"+denseCost+",\"note_added\":"+(newNote-baseNote)+",\"indicator_added\":"+(newIndicator-baseIndicator)+",\"result\":"+q(args[1])+"}");
    }
}
