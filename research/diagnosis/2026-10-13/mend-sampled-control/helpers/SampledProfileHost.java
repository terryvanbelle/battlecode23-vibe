import battlecode.common.RobotType;
import battlecode.common.Team;
import battlecode.instrumenter.profiler.Profiler;
import battlecode.instrumenter.profiler.ProfilerCollection;
import battlecode.instrumenter.profiler.ProfilerEvent;
import battlecode.instrumenter.profiler.ProfilerEventType;
import battlecode.server.Config;
import battlecode.server.GameInfo;
import battlecode.server.GameMaker;
import battlecode.server.Server;
import battlecode.server.ServerState;
import battlecode.world.LiveMap;
import battlecode.world.GameMapIO;
import battlecode.world.control.PlayerControlProvider;
import battlecode.world.control.RobotControlProvider;
import battlecode.world.control.TeamControlProvider;
import java.io.File;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Host-only selective native recording; never enters the bot class path. */
public final class SampledProfileHost {
    static final String RELEASE="5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a";
    static final int OPEN_CAP=2000000;

    /** Keep profiler != null for every loader; cache instrumentation must stay enabled. */
    static final class NoopProfiler extends Profiler {
        NoopProfiler(ProfilerCollection owner) {super(owner,"unrecorded robot");}
        @Override public void incrementBytecodes(int amount) {}
        @Override public void enterMethod(String name) {}
        @Override public void exitMethod(String name) {}
        @Override public void exitOpenMethods() {}
    }

    static final class SampledCollection extends ProfilerCollection {
        final Set<Integer> wanted;
        final Set<Integer> sampled=new LinkedHashSet<Integer>();
        final Set<Integer> wrongType=new LinkedHashSet<Integer>();
        final NoopProfiler noop=new NoopProfiler(this);
        int noopRobots;
        SampledCollection(Set<Integer> ids) {
            wanted=Collections.unmodifiableSet(new LinkedHashSet<Integer>(ids));
        }
        @Override public Profiler createProfiler(int id,RobotType type) {
            if(wanted.contains(id)&&type==RobotType.LAUNCHER) {
                if(!sampled.add(id))throw new IllegalStateException("duplicate selected robot ID");
                return super.createProfiler(id,type);
            }
            if(wanted.contains(id))wrongType.add(id);
            noopRobots++;
            return noop;
        }
        long opens() {
            long count=0;
            for(Profiler profiler:getProfilers())for(ProfilerEvent event:profiler.getEvents())
                if(event.getType()==ProfilerEventType.OPEN)count++;
            return count;
        }
        boolean completeSelection() {return sampled.equals(wanted)&&wrongType.isEmpty();}
    }

    static Set<Integer> parseIds(String text,boolean game) {
        String[] parts=text.split(",",-1);
        if(parts.length<1||parts.length>5||(game&&parts.length<3))
            throw new IllegalArgumentException("provide three to five explicit own launcher IDs");
        Set<Integer> ids=new LinkedHashSet<Integer>();
        for(String part:parts) {
            if(!part.matches("[1-9][0-9]{0,9}"))throw new IllegalArgumentException("positive decimal robot IDs required");
            int id=Integer.parseInt(part);
            if(!ids.add(id))throw new IllegalArgumentException("duplicate sample ID");
        }
        return ids;
    }

    static Field field(Class<?> owner,String name) throws Exception {
        Field f=owner.getDeclaredField(name);f.setAccessible(true);return f;
    }
    static Method method(Class<?> owner,String name,Class<?>... arguments) throws Exception {
        Method m=owner.getDeclaredMethod(name,arguments);m.setAccessible(true);return m;
    }
    static Object invoke(Method method,Object object,Object... arguments) throws Exception {
        try {return method.invoke(object,arguments);}
        catch(InvocationTargetException error) {
            Throwable cause=error.getCause();
            if(cause instanceof Exception)throw (Exception)cause;
            if(cause instanceof Error)throw (Error)cause;
            throw error;
        }
    }
    static String sha(Path path) throws Exception {
        if(Files.isSymbolicLink(path)||!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS))
            throw new IllegalArgumentException("regular pinned input required");
        MessageDigest digest=MessageDigest.getInstance("SHA-256");
        try(java.io.InputStream stream=Files.newInputStream(path)) {
            byte[] data=new byte[1048576];int n;
            while((n=stream.read(data))!=-1)digest.update(data,0,n);
        }
        StringBuilder out=new StringBuilder();
        for(byte b:digest.digest())out.append(String.format("%02x",b));
        return out.toString();
    }
    static String quote(String value) {
        StringBuilder out=new StringBuilder("\"");
        for(char c:value.toCharArray()) {
            if(c=='\\'||c=='\"')out.append('\\').append(c);
            else if(c<32)out.append(String.format("\\u%04x",(int)c));
            else out.append(c);
        }
        return out.append('"').toString();
    }
    static void check(boolean value,String label) {
        if(!value)throw new AssertionError(label);
    }

    static void selftest() throws Exception {
        int tests=0;
        SampledCollection own=new SampledCollection(parseIds("11,22,33",true));
        Profiler hq=own.createProfiler(90,RobotType.HEADQUARTERS);
        check(hq!=null&&hq instanceof NoopProfiler,"early HQ loader keeps profiler hooks enabled");tests++;
        hq.incrementBytecodes(12000);hq.enterMethod("own.HQ.run");hq.exitMethod("own.HQ.run");hq.exitOpenMethods();
        check(own.getProfilers().isEmpty()&&own.getFrames().isEmpty()&&own.opens()==0,"unrecorded robot consumes no cap");tests++;
        Profiler selected=own.createProfiler(11,RobotType.LAUNCHER);
        check(selected!=null&&!(selected instanceof NoopProfiler)&&own.getProfilers().size()==1,"explicit own launcher recorded");tests++;
        selected.enterMethod("own.Launcher.run");selected.incrementBytecodes(331);selected.exitMethod("own.Launcher.run");
        check(selected.getEvents().size()==2&&selected.getEvents().get(1).getAt()==331&&own.opens()==1,"sampled native counters intact");tests++;
        own.createProfiler(22,RobotType.LAUNCHER).exitOpenMethods();own.createProfiler(33,RobotType.LAUNCHER).exitOpenMethods();
        check(own.completeSelection(),"all explicit own IDs observed");tests++;
        SampledCollection other=new SampledCollection(Collections.<Integer>emptySet());
        check(other.createProfiler(11,RobotType.LAUNCHER)!=null&&other.getProfilers().isEmpty(),"other side emits no profiles");tests++;
        SampledCollection wrong=new SampledCollection(parseIds("11",false));wrong.createProfiler(11,RobotType.CARRIER);
        check(!wrong.completeSelection()&&wrong.wrongType.contains(11)&&wrong.getProfilers().isEmpty(),"wrong type never changes execution by throwing");tests++;
        for(String bad:new String[]{"","0","-1","1,1","1,2,3,4,5,6","1,2,x","2147483648,2,3"}) {
            boolean rejected=false;try {parseIds(bad,false);}catch(IllegalArgumentException expected){rejected=true;}
            check(rejected,"invalid ID fixture rejected");tests++;
        }
        check(method(Server.class,"createControlProvider",GameInfo.class,GameMaker.class,boolean.class)!=null,"official provider API exists");tests++;
        check(method(Server.class,"runMatch",GameInfo.class,int.class,RobotControlProvider.class,GameMaker.class,boolean.class,boolean.class)!=null,"exact official match loop exists");tests++;
        check(field(TeamControlProvider.class,"teamProviderMap")!=null&&field(PlayerControlProvider.class,"profilerCollection")!=null,"host sampling fields exist");tests++;
        check(RELEASE.length()==64&&OPEN_CAP==2000000,"release/cap constants");tests++;
        System.out.println("{\"selftest\":\"passed\",\"checks\":"+tests+",\"games_run\":0,\"limits\":\"API/collection fixtures only; no gameplay identity demonstrated\"}");
    }

    @SuppressWarnings("unchecked")
    static void game(String[] args) throws Exception {
        if(args.length!=4)throw new IllegalArgumentException("SampledProfileHost OWN_PACKAGE FROZEN_BOTS NEW_OUTPUT_DIRECTORY IDS");
        String packageName=args[0];
        if(!packageName.equals("c_mend2")&&!packageName.equals("c_mend3"))throw new IllegalArgumentException("frozen own Mend2/Mend3 package required");
        Set<Integer> ids=parseIds(args[3],true);
        Path jar=Paths.get(Server.class.getProtectionDomain().getCodeSource().getLocation().toURI());
        if(!sha(jar).equals(RELEASE))throw new IllegalArgumentException("official release jar required for actual games");
        if(!Files.readAllLines(Paths.get("/etc/hostname")).get(0).split("\\.")[0].equals("battlecode-dev"))
            throw new IllegalArgumentException("actual games require battlecode-dev");
        if(!System.getProperty("java.version").equals("1.8.0_504"))throw new IllegalArgumentException("frozen JDK8u504 required");
        Path bots=Paths.get(args[1]).toRealPath(),out=Paths.get(args[2]).toAbsolutePath();
        if(!Files.isDirectory(bots.resolve(packageName))||!Files.isDirectory(bots.resolve("arch_ampmid")))
            throw new IllegalArgumentException("frozen own compiled packages required");
        if(Files.exists(out,LinkOption.NOFOLLOW_LINKS))throw new IllegalArgumentException("new private output directory required");
        Config options=new Config(new String[]{"-c=-"});
        for(String key:options.getKeys())if(key.startsWith("bc.")&&key.toLowerCase().contains("seed"))
            throw new IllegalArgumentException("no seed override allowed");
        options.set("bc.server.mode","headless");options.setBoolean("bc.server.websocket",false);
        options.setBoolean("bc.server.debug",false);options.setBoolean("bc.engine.debug-methods",false);
        options.setBoolean("bc.engine.enable-profiler",true);options.setBoolean("bc.server.validate-maps",false);
        options.setBoolean("bc.server.alternate-order",false);options.setBoolean("bc.engine.show-indicators",true);
        options.setBoolean("bc.server.robot-player-to-system-out",false);
        options.set("bc.server.robot-player-replay-file-per-team-limit-bytes","4000000");
        Files.createDirectory(out);Files.createDirectory(out.resolve("empty-map-directory"));
        options.set("bc.game.map-path",out.resolve("empty-map-directory").toString());
        Config.setGlobalConfig(options);
        LiveMap map=GameMapIO.loadMap("Cornucopia",out.resolve("empty-map-directory").toFile(),false);
        if(map.getSeed()!=272||map.getRounds()!=2000)throw new IllegalArgumentException("unchanged built-in Cornucopia required");
        Path replay=out.resolve("sampled-on.bc23");
        GameInfo info=new GameInfo(packageName,packageName,bots.toString(),"arch_ampmid","arch_ampmid",bots.toString(),new String[]{"Cornucopia"},replay.toFile(),false);
        GameMaker maker=new GameMaker(info,null,true);maker.makeGameHeader();
        Server server=new Server(options,false);
        TeamControlProvider controls=(TeamControlProvider)invoke(method(Server.class,"createControlProvider",GameInfo.class,GameMaker.class,boolean.class),server,info,maker,true);
        Map<Team,RobotControlProvider> providers=(Map<Team,RobotControlProvider>)field(TeamControlProvider.class,"teamProviderMap").get(controls);
        SampledCollection own=new SampledCollection(ids),other=new SampledCollection(Collections.<Integer>emptySet());
        field(PlayerControlProvider.class,"profilerCollection").set(providers.get(Team.A),own);
        field(PlayerControlProvider.class,"profilerCollection").set(providers.get(Team.B),other);
        Team winner=(Team)invoke(method(Server.class,"runMatch",GameInfo.class,int.class,RobotControlProvider.class,GameMaker.class,boolean.class,boolean.class),server,info,0,controls,maker,false,false);
        if(server.getState()!=ServerState.FINISHED)throw new IllegalStateException("official match did not finish");
        maker.makeGameFooter(winner==Team.B?Team.B:Team.A);maker.writeGame(replay.toFile());
        String result="{\"engine_sha256\":"+quote(RELEASE)+",\"engine_patch_used\":false,\"host_sampling_override\":true,\"bot_source_instrumented\":false,\"own_package\":"+quote(packageName)+",\"map\":\"Cornucopia\",\"map_seed\":272,\"map_round_limit\":2000,\"requested_ids\":"+ids+",\"recorded_ids\":"+own.sampled+",\"selected_ids_with_wrong_type\":"+own.wrongType+",\"selection_complete\":"+own.completeSelection()+",\"own_native_open_events\":"+own.opens()+",\"native_open_cap\":"+OPEN_CAP+",\"own_team_capped\":"+(own.opens()>=OPEN_CAP)+",\"other_native_open_events\":"+other.opens()+",\"replay_sha256\":"+quote(sha(replay))+",\"identity_verified\":false,\"native_costs_available\":false,\"note\":\"Recording completed. Full state, metered bytecode and footer identity plus uncapped final-ex-zero Mend scope must pass independently before costs are used. Noop profilers preserve non-null factory loader/cache instrumentation.\"}\n";
        Files.write(out.resolve("sampling.json"),result.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.print(result);
        if(!own.completeSelection())throw new IllegalStateException("not all requested own launcher IDs recorded; raw replay preserved");
    }
    public static void main(String[] args) throws Exception {
        if(Arrays.equals(args,new String[]{"--selftest"})){selftest();return;}
        game(args);
    }
}
