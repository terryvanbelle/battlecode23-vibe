import battlecode.instrumenter.TeamClassLoaderFactory;
import battlecode.instrumenter.profiler.Profiler;
import battlecode.instrumenter.profiler.ProfilerCollection;
import java.lang.reflect.Field;
import java.lang.reflect.Proxy;

/** Zero-game fixture: cache hooks and metering with normal versus non-null no-op. */
public final class SamplingCacheTest {
    static final class Result {int answer,cost,debt;}
    static Result call(TeamClassLoaderFactory factory,boolean hooks,Profiler profiler) throws Exception {
        ClassLoader loader=factory.createLoader(hooks);
        Class<?> monitor=loader.loadClass("battlecode.instrumenter.inject.RobotMonitor");
        Class<?> pauser=Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Pauser");
        Class<?> killer=Class.forName("battlecode.instrumenter.SandboxedRobotPlayer$Killer");
        Object p=Proxy.newProxyInstance(pauser.getClassLoader(),new Class<?>[]{pauser},
                (o,m,a)->{throw new IllegalStateException("fixture unexpectedly exhausted budget");});
        Object k=Proxy.newProxyInstance(killer.getClassLoader(),new Class<?>[]{killer},
                (o,m,a)->{throw new IllegalStateException("fixture unexpectedly killed");});
        monitor.getMethod("init",pauser,killer,int.class,Profiler.class).invoke(null,p,k,123,profiler);
        monitor.getMethod("setBytecodeLimit",int.class).invoke(null,10000);
        Field remaining=SampledProfileHost.field(monitor,"bytecodesLeft");
        Field debt=SampledProfileHost.field(monitor,"bytecodesToRemove");
        remaining.setInt(null,10000);debt.setInt(null,0);
        Class<?> calibration=Class.forName("samplefixture.SamplingCalibration",true,loader);
        remaining.setInt(null,10000);debt.setInt(null,0);
        Result result=new Result();
        result.answer=(Integer)calibration.getMethod("burn",int.class).invoke(null,13);
        result.cost=10000-remaining.getInt(null);result.debt=debt.getInt(null);
        return result;
    }
    public static void main(String[] args) throws Exception {
        if(args.length!=1)throw new IllegalArgumentException("SamplingCacheTest PRIVATE_CALIBRATION_CLASSES");
        TeamClassLoaderFactory safe=new TeamClassLoaderFactory(args[0]);
        ProfilerCollection collection=new ProfilerCollection();
        Profiler noop=new SampledProfileHost.NoopProfiler(collection);
        Result unrecorded=call(safe,true,noop);
        Profiler normal=collection.createProfiler(19,battlecode.common.RobotType.LAUNCHER);
        Result recorded=call(safe,true,normal);
        Result ordinary=call(new TeamClassLoaderFactory(args[0]),false,null);
        int checks=0;
        SampledProfileHost.check(unrecorded.answer==recorded.answer&&recorded.answer==ordinary.answer,"same arithmetic answer");checks++;
        SampledProfileHost.check(unrecorded.cost>0&&unrecorded.cost==recorded.cost&&recorded.cost==ordinary.cost,"same metered bytecodes across no-op/normal/off");checks++;
        SampledProfileHost.check(unrecorded.debt==0&&recorded.debt==0&&ordinary.debt==0,"zero pending debt at fixture return");checks++;
        SampledProfileHost.check(noop.getEvents().isEmpty(),"non-null no-op emits zero events");checks++;
        SampledProfileHost.check(normal.getEvents().size()>=40,"later selected robot retains cached profiling hooks");checks++;
        TeamClassLoaderFactory unsafe=new TeamClassLoaderFactory(args[0]);
        call(unsafe,false,null);
        Profiler lost=new ProfilerCollection().createProfiler(23,battlecode.common.RobotType.LAUNCHER);
        call(unsafe,true,lost);
        SampledProfileHost.check(lost.getEvents().isEmpty(),"null early profiler loses later cache hooks: known trap reproduced");checks++;
        System.out.println("{\"selftest\":\"passed\",\"checks\":"+checks+",\"metered_fixture_cost\":"+recorded.cost+",\"sampled_fixture_events\":"+normal.getEvents().size()+",\"pending_debt\":0,\"games_run\":0,\"limits\":\"Synthetic cache fixture only. Full state/bytecode/footer game identity remains unproven.\"}");
    }
}
