import battlecode.schema.*;
import com.google.flatbuffers.FlatBufferBuilder;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import java.util.zip.GZIPInputStream;

/** Read native counters only; no bot source instrumentation and no engine execution. */
public final class NativeProfile {
    static final int OPEN_CAP = 2000000;
    static final String[] METHODS = {"run", "mendUpdate", "march", "fight", "mendScore", "pickObjective", "shoot", "nearestEnemy", "read"};
    static final Pattern ROBOT_ID = Pattern.compile("^#([0-9]+)(?:\\s|$)");
    static final Pattern EXCEPTIONS = Pattern.compile("(?:\\||,)ex=([0-9]+)(?:,|$)");
    static final int[] LIMITS = {20000,12500,10000,10000,10000,10000};
    static String selected(String frame) {
        for (String m : METHODS) {
            String owner = m.equals("nearestEnemy") || m.equals("read") ? ".Comms." : ".Launcher.";
            if (frame.endsWith(owner + m)) return m;
        }
        return null;
    }
    static String quote(String v) {
        if (v == null) return "null";
        StringBuilder s = new StringBuilder("\"");
        for (char c : v.toCharArray()) {
            if (c == '"' || c == '\\') s.append('\\').append(c);
            else if (c < 32) s.append(String.format("\\u%04x", (int)c));
            else s.append(c);
        }
        return s.append('"').toString();
    }
    static String strings(Collection<String> list) {
        StringBuilder s = new StringBuilder("["); boolean first=true;
        for (String v:list) { if (!first) s.append(','); first=false; s.append(quote(v)); }
        return s.append(']').toString();
    }
    static final class Turn { int round,used; Turn(int r,int u) {round=r;used=u;} }
    static final class Heal {int round,hp;Heal(int r,int value){round=r;hp=value;}}
    static final class Robot {
        int id,team,type; boolean hasProfile,uncaughtException; List<Turn> turns=new ArrayList<>();
        boolean exceptionSeen,exceptionRegression;long maxExceptions,lastExceptions;
        int lastExceptionRound=-1,exceptionSnapshots;
        long healedHp;int deathRound=-1;List<Heal> heals=new ArrayList<>();
        long[] before;
        Robot(int i,int tm,int ty) {id=i;team=tm;type=ty;}
        long total() {long s=0;for(Turn t:turns)s+=t.used;return s;}
        boolean overrun(int limit) {for(Turn t:turns)if(t.used>=limit)return true;return false;}
        void indicator(int round,String text) {
            if(text==null)return;Matcher match=EXCEPTIONS.matcher(text);if(!match.find())return;
            long value;
            try {value=Long.parseLong(match.group(1));}catch(NumberFormatException error){exceptionRegression=true;return;}
            if(exceptionSeen&&value<lastExceptions)exceptionRegression=true;
            exceptionSeen=true;lastExceptions=value;maxExceptions=Math.max(maxExceptions,value);
            lastExceptionRound=round;exceptionSnapshots++;
        }
        String exceptionStatus() {
            if(uncaughtException||maxExceptions>0)return "observed_exception";
            if(exceptionRegression)return "invalid_counter";
            if(!exceptionSeen)return "missing_counter";
            if(!turns.isEmpty()&&lastExceptionRound==turns.get(turns.size()-1).round)return "zero_through_last_turn";
            return "unobserved_tail";
        }
        boolean exceptionClear() {return exceptionStatus().equals("zero_through_last_turn");}
    }
    static final class Node {
        String frame,method,parent; int start; long children;
        int directReadsBefore,directReadsAfter,lastNearestEnd=-1;long pickCost;
        List<Interval> mends=new ArrayList<>(),marches=new ArrayList<>();
        Node(String f,int a,String p) {frame=f;method=selected(f);start=a;parent=p;}
    }
    static final class Interval {
        String method,parent,frame; int start,end; long inclusive,exclusive;
        int directReadsBefore,directReadsAfter,runEnd=-1;long pickCost,followingMarch,followingPick;
        Interval(Node n,int end) {
            method=n.method;parent=n.parent;frame=n.frame;start=n.start;this.end=end;
            inclusive=(long)end-start;exclusive=inclusive-n.children;
            directReadsBefore=n.directReadsBefore;directReadsAfter=n.directReadsAfter;pickCost=n.pickCost;
        }
    }
    static final class Trace {
        Map<String,Integer> entries=new TreeMap<>(); List<Interval> intervals=new ArrayList<>();
        List<Integer> turnStarts=new ArrayList<>(); Set<String> issues=new LinkedHashSet<>();
        int lastAt,events,opens; boolean valid=true;
        void issue(String s) {issues.add(s);valid=false;}
    }
    static Trace parse(String[] frames, int[] at, int[] frame, boolean[] open) {
        Trace t=new Trace(); Deque<Node> stack=new ArrayDeque<>(); int prev=-1;
        for(int i=0;i<at.length;i++) {
            t.events++;t.lastAt=at[i];
            if(at[i]<0)t.issue("negative_counter");
            if(at[i]<prev) t.issue("nonmonotonic_counter"); prev=at[i];
            if(at[i]==Integer.MAX_VALUE) t.issue("counter_saturated");
            if(frame[i]<0 || frame[i]>=frames.length || frames[frame[i]]==null) {t.issue("invalid_frame");continue;}
            String f=frames[frame[i]], m=selected(f);
            if(open[i]) {
                t.opens++;
                if(m!=null)t.entries.put(m,t.entries.getOrDefault(m,0)+1);
                if(f.endsWith(".Telemetry.startTurn"))t.turnStarts.add(at[i]);
            }
            if(!t.valid) continue; // costs after first broken nesting/counter cannot be reconstructed
            if(open[i]) stack.push(new Node(f,at[i],stack.isEmpty()?null:stack.peek().frame));
            else {
                if(stack.isEmpty() || !stack.peek().frame.equals(f)) {t.issue("unmatched_close");continue;}
                Node n=stack.pop();Interval v=new Interval(n,at[i]);
                if(v.exclusive<0) {t.issue("negative_exclusive_cost");continue;}
                if(!stack.isEmpty()) {
                    Node parent=stack.peek();parent.children+=v.inclusive;
                    if("mendUpdate".equals(parent.method)) {
                        if("read".equals(n.method)) {
                            if(parent.lastNearestEnd>=0&&n.start>=parent.lastNearestEnd)parent.directReadsAfter++;
                            else parent.directReadsBefore++;
                        }
                        if("nearestEnemy".equals(n.method))parent.lastNearestEnd=v.end;
                    }
                    if("march".equals(parent.method)&&"pickObjective".equals(n.method))parent.pickCost+=v.inclusive;
                    if("run".equals(parent.method)) {
                        if("mendUpdate".equals(n.method))parent.mends.add(v);
                        if("march".equals(n.method))parent.marches.add(v);
                    }
                }
                if("run".equals(n.method))for(Interval mend:n.mends) {
                    mend.runEnd=v.end;
                    for(Interval march:n.marches)if(march.start>=mend.end) {
                        mend.followingMarch+=march.inclusive;mend.followingPick+=march.pickCost;
                    }
                }
                if(n.method!=null)t.intervals.add(v);
            }
        }
        if(!stack.isEmpty())t.issue("unclosed_stack");
        return t;
    }
    static Trace parse(ProfilerFile file,ProfilerProfile profile) {
        String[] frames=new String[file.framesLength()];
        for(int i=0;i<frames.length;i++)frames[i]=file.frames(i);
        int n=profile.eventsLength();int[] at=new int[n],frame=new int[n];boolean[] open=new boolean[n];
        for(int i=0;i<n;i++) {ProfilerEvent e=profile.events(i);at[i]=e.at();frame[i]=e.frame();open[i]=e.isOpen();}
        return parse(frames,at,frame,open);
    }
    static boolean alignment(Trace t,Robot robot,int limit,boolean capped) {
        if(capped || !t.valid || robot==null || robot.overrun(limit) || t.lastAt!=robot.total()
                || t.turnStarts.size()!=robot.turns.size())return false;
        long before=0;
        for(int i=0;i<robot.turns.size();i++) {
            // startTurn is near the beginning of its turn, not necessarily at offset zero.
            if(t.turnStarts.get(i)<before || t.turnStarts.get(i)>before+robot.turns.get(i).used)return false;
            before+=robot.turns.get(i).used;
        }
        return true;
    }
    static long[] locate(Trace t,Robot robot,int at,int limit) {
        int lo=0,hi=t.turnStarts.size();
        while(lo<hi) {int mid=(lo+hi)>>>1;if(t.turnStarts.get(mid)<=at)lo=mid+1;else hi=mid;}
        int turn=lo-1;
        if(turn<0 || turn>=robot.turns.size())return null;
        if(robot.before==null||robot.before.length!=robot.turns.size()) {
            robot.before=new long[robot.turns.size()];long cumulative=0;
            for(int i=0;i<robot.turns.size();i++) {robot.before[i]=cumulative;cumulative+=robot.turns.get(i).used;}
        }
        Turn now=robot.turns.get(turn);long used=(long)at-robot.before[turn];
        if(used<0 || used>now.used || used>=limit)return null;
        return new long[]{now.round,limit-used};
    }
    static String mendFields(Trace trace,Interval mend,Robot robot,int limit,boolean aligned,boolean usable) {
        if(!mend.method.equals("mendUpdate"))return "";
        boolean known=usable&&aligned;
        long[] entry=known?locate(trace,robot,mend.start,limit):null;
        long[] end=known?locate(trace,robot,mend.end,limit):null;
        known=known&&entry!=null&&end!=null&&entry[0]==end[0];
        boolean tailKnown=known&&mend.runEnd>=mend.end&&mend.runEnd!=trace.lastAt;
        long windowHeal=0;
        if(known)for(Heal heal:robot.heals)if(heal.round>=entry[0]&&heal.round<=entry[0]+10)windowHeal+=heal.hp;
        return ",\"fallback_witness\":"+(known?String.valueOf(mend.directReadsAfter>0):"null")
            +",\"direct_reads_before_nearest\":"+(known?String.valueOf(mend.directReadsBefore):"null")
            +",\"direct_reads_after_nearest\":"+(known?String.valueOf(mend.directReadsAfter):"null")
            +",\"following_march_inclusive\":"+(tailKnown?String.valueOf(mend.followingMarch):"null")
            +",\"following_pick_objective_inclusive\":"+(tailKnown?String.valueOf(mend.followingPick):"null")
            +",\"launcher_tail_inclusive\":"+(tailKnown?String.valueOf((long)mend.runEnd-mend.end):"null")
            +",\"replay_healed_hp_next_10_rounds\":"+(known?String.valueOf(windowHeal):"null")
            +",\"replay_death_round\":"+(robot.deathRound<0?"null":String.valueOf(robot.deathRound));
    }
    static void spawn(Map<Integer,Robot> robots,SpawnedBodyTable bodies) {
        if(bodies==null)return;
        for(int i=0;i<bodies.robotIDsLength();i++) {
            int id=bodies.robotIDs(i);
            if(!robots.containsKey(id))robots.put(id,new Robot(id,bodies.teamIDs(i),bodies.types(i)));
        }
    }
    static String counts(Map<String,Integer> counts) {
        StringBuilder s=new StringBuilder("{");boolean first=true;
        for(String m:METHODS) {if(!first)s.append(',');first=false;s.append(quote(m)).append(':').append(counts.getOrDefault(m,0));}
        return s.append('}').toString();
    }
    static void process(GameWrapper wrapper,PrintWriter robotOut,PrintWriter callOut,PrintWriter metaOut) {
        Map<Integer,Robot> robots=new TreeMap<>();String[] names={"?","A","B"};
        int[] limits=LIMITS.clone();String map="?";int game=-1,mapSeed=0,width=0,height=0;
        for(int i=0;i<wrapper.eventsLength();i++) {
            EventWrapper e=wrapper.events(i);
            if(e.eType()==Event.GameHeader) {
                GameHeader h=(GameHeader)e.e(new GameHeader());
                for(int k=0;k<h.teamsLength();k++) {TeamData td=h.teams(k);if(td.teamID()>0&&td.teamID()<3)names[td.teamID()]=td.packageName()==null?td.name():td.packageName();}
                for(int k=0;k<h.bodyTypeMetadataLength();k++) {BodyTypeMetadata b=h.bodyTypeMetadata(k);if(b.type()>=0&&b.type()<6&&b.bytecodeLimit()>0)limits[b.type()]=b.bytecodeLimit();}
            } else if(e.eType()==Event.MatchHeader) {
                game++;robots.clear();GameMap g=((MatchHeader)e.e(new MatchHeader())).map();map=g.name();
                mapSeed=g.randomSeed();
                if(g.maxCorner()!=null&&g.minCorner()!=null) {width=g.maxCorner().x()-g.minCorner().x();height=g.maxCorner().y()-g.minCorner().y();}
                spawn(robots,g.bodies());
            } else if(e.eType()==Event.Round) {
                Round r=(Round)e.e(new Round());spawn(robots,r.spawnedBodies());
                for(int k=0;k<r.bytecodeIDsLength();k++) {
                    Robot rb=robots.get(r.bytecodeIDs(k));
                    if(rb==null)throw new IllegalStateException("bytecode ID missing robot metadata");
                    rb.turns.add(new Turn(r.roundID(),r.bytecodesUsed(k)));
                }
                for(int k=0;k<r.actionsLength();k++) {
                    Robot rb=robots.get(r.actionIDs(k));if(rb==null)continue;
                    if(r.actions(k)==Action.DIE_EXCEPTION)rb.uncaughtException=true;
                    if(r.actions(k)==Action.CHANGE_HEALTH&&r.actionTargets(k)>0) {
                        rb.healedHp+=r.actionTargets(k);rb.heals.add(new Heal(r.roundID(),r.actionTargets(k)));
                    }
                }
                for(int k=0;k<r.diedIDsLength();k++) {Robot rb=robots.get(r.diedIDs(k));if(rb!=null)rb.deathRound=r.roundID();}
                for(int k=0;k<r.indicatorStringIDsLength();k++) {
                    Robot rb=robots.get(r.indicatorStringIDs(k));String indicator=r.indicatorStrings(k);
                    if(rb==null||indicator==null)continue;
                    rb.indicator(r.roundID(),indicator);
                }
            } else if(e.eType()==Event.MatchFooter) {
                MatchFooter footer=(MatchFooter)e.e(new MatchFooter());
                Set<Integer> profiledIDs=new HashSet<>();
                for(int fi=0;fi<footer.profilerFilesLength();fi++) {
                    ProfilerFile file=footer.profilerFiles(fi);long opens=0;Integer fileSide=null;
                    for(int pi=0;pi<file.profilesLength();pi++) {
                        ProfilerProfile p=file.profiles(pi);Matcher m=ROBOT_ID.matcher(p.name());
                        if(!m.find())throw new IllegalStateException("invalid native robot profile name");
                        int id=Integer.parseInt(m.group(1));Robot rb=robots.get(id);
                        if(rb==null||!profiledIDs.add(id))throw new IllegalStateException("unmapped or duplicate native robot profile ID "+id);
                        if(!p.name().endsWith("("+BodyType.name(rb.type)+")"))throw new IllegalStateException("native/replay body type disagreement");
                        if(fileSide!=null&&fileSide!=rb.team)throw new IllegalStateException("mixed-side native profiler file");
                        fileSide=rb.team;
                        for(int k=0;k<p.eventsLength();k++)if(p.events(k).isOpen())opens++;
                    }
                    boolean capped=opens>=OPEN_CAP;
                    metaOut.println("{\"game\":"+game+",\"map\":"+quote(map)+",\"width\":"+width+",\"height\":"+height+",\"map_seed\":"+mapSeed+",\"file\":"+fi+",\"side\":"+quote(fileSide==null?"?":fileSide==1?"A":"B")+",\"open_events\":"+opens+",\"open_cap\":"+OPEN_CAP+",\"capped\":"+capped+",\"profile_count\":"+file.profilesLength()+"}");
                    for(int pi=0;pi<file.profilesLength();pi++) {
                        ProfilerProfile p=file.profiles(pi);Matcher idMatch=ROBOT_ID.matcher(p.name());
                        int id=idMatch.find()?Integer.parseInt(idMatch.group(1)):-1;Robot rb=robots.get(id);
                        if(rb!=null)rb.hasProfile=true;
                        Trace t=parse(file,p);
                        if(rb!=null&&!rb.turns.isEmpty()&&t.events==0)t.issue("empty_trace_with_recorded_turns");
                        int limit=rb==null?0:limits[rb.type];boolean exceptionFree=rb!=null&&rb.exceptionClear();
                        boolean aligned=exceptionFree&&alignment(t,rb,limit,capped);
                        boolean usable=!capped&&t.valid&&rb!=null&&exceptionFree;
                        String context=usable?"zero_observed_ex_valid_native_nesting":rb!=null&&(rb.maxExceptions>0||rb.uncaughtException)?"suppressed_observed_exception":"native_nesting_unverified";
                        String prefix="{\"game\":"+game+",\"map\":"+quote(map)+",\"file\":"+fi+",\"robot\":"+id
                            +",\"side\":"+quote(rb==null?"?":rb.team==1?"A":rb.team==2?"B":"?")
                            +",\"package\":"+quote(rb==null||rb.team<1||rb.team>2?"?":names[rb.team]);
                        robotOut.println(prefix+",\"type\":"+quote(rb==null?"?":BodyType.name(rb.type))+",\"profile\":"+quote(p.name())
                            +",\"recorded_turns\":"+(rb==null?0:rb.turns.size())+",\"recorded_bytecodes\":"+(rb==null?0:rb.total())
                            +",\"native_counter\":"+t.lastAt+",\"events\":"+t.events+",\"opens\":"+t.opens
                            +",\"team_capped\":"+capped+",\"trace_valid\":"+t.valid+",\"issues\":"+strings(t.issues)
                            +",\"recorded_caught_exceptions\":"+(rb.exceptionSeen?String.valueOf(rb.maxExceptions):"null")+",\"exception_counter_snapshots\":"+rb.exceptionSnapshots+",\"recorded_uncaught_exception\":"+rb.uncaughtException+",\"zero_recorded_exceptions\":"+exceptionFree
                            +",\"exception_max\":"+(rb.exceptionSeen?String.valueOf(rb.maxExceptions):"null")+",\"exception_death\":"+rb.uncaughtException
                            +",\"exception_status\":"+quote(rb.exceptionStatus())+",\"last_exception_counter_round\":"+rb.lastExceptionRound+",\"caller_context_status\":"+quote(context)
                            +",\"recorded_healed_hp\":"+rb.healedHp+",\"replay_death_round\":"+(rb.deathRound<0?"null":String.valueOf(rb.deathRound))
                            +",\"native_costs_usable\":"+usable+",\"frequency_exact\":"+usable
                            +",\"entry_budget_aligned\":"+aligned+",\"selected_entries\":"+counts(t.entries)+"}");
                        if(rb==null||rb.type!=BodyType.LAUNCHER)continue;
                        for(Interval v:t.intervals) {
                            boolean ambiguous=v.end==t.lastAt;
                            boolean costUsable=usable&&!ambiguous;
                            long[] loc=aligned&&exceptionFree?locate(t,rb,v.start,limit):null;
                            long[] endLoc=aligned&&costUsable?locate(t,rb,v.end,limit):null;
                            String mendFields=mendFields(t,v,rb,limit,aligned,costUsable);
                            callOut.println(prefix+",\"method\":"+quote(v.method)+",\"frame\":"+quote(v.frame)+",\"caller_frame\":"+quote(costUsable?v.parent:null)
                                +",\"caller_context_status\":"+quote(context)+",\"exception_status\":"+quote(rb.exceptionStatus())
                                +",\"open_at\":"+v.start+",\"close_at\":"+v.end+",\"native_inclusive\":"+(costUsable?String.valueOf(v.inclusive):"null")+",\"native_exclusive\":"+(costUsable?String.valueOf(v.exclusive):"null")
                                +",\"terminal_close_ambiguous\":"+ambiguous+",\"cost_usable\":"+costUsable
                                +",\"round\":"+(loc==null?"null":loc[0])+",\"entry_budget\":"+(loc==null?"null":loc[1])
                                +",\"return_budget\":"+(endLoc==null||loc==null||endLoc[0]!=loc[0]?"null":endLoc[1])+mendFields+"}");
                        }
                    }
                }
                // Missing profiles belong in the denominator, rather than silently disappear.
                for(Robot rb:robots.values())if(!rb.hasProfile&&rb.type==BodyType.LAUNCHER&&!rb.turns.isEmpty())
                    robotOut.println("{\"game\":"+game+",\"map\":"+quote(map)+",\"file\":null,\"robot\":"+rb.id
                        +",\"side\":"+quote(rb.team==1?"A":"B")+",\"package\":"+quote(names[rb.team])+",\"type\":\"LAUNCHER\",\"profile\":null"
                        +",\"recorded_turns\":"+rb.turns.size()+",\"recorded_bytecodes\":"+rb.total()+",\"issues\":[\"missing_profile\"]"
                        +",\"exception_status\":"+quote(rb.exceptionStatus())+",\"caller_context_status\":\"native_nesting_unverified\""
                        +",\"native_costs_usable\":false,\"frequency_exact\":false,\"entry_budget_aligned\":false,\"selected_entries\":"+counts(Collections.emptyMap())+"}");
            }
        }
    }
    static int checks;
    static void require(boolean condition,String why) {checks++;if(!condition)throw new AssertionError(why);}
    static int fixtureProfile(FlatBufferBuilder b,int id,String pkg) {
        String[] frames={pkg+".RobotPlayer.run",pkg+".Telemetry.startTurn",pkg+".Launcher.pickObjective",pkg+".Launcher.mendUpdate",pkg+".MapMem.helper"};
        int[] strings=new int[frames.length];for(int i=0;i<strings.length;i++)strings[i]=b.createString(frames[i]);
        int frameVec=ProfilerFile.createFramesVector(b,strings);
        int[] at={0,0,1,2,10,12,15,20,25,50},fr={0,1,1,2,3,4,4,3,2,0};
        boolean[] open={true,true,false,true,true,true,false,false,false,false};
        int[] events=new int[at.length];for(int i=0;i<at.length;i++)events[i]=ProfilerEvent.createProfilerEvent(b,open[i],at[i],fr[i]);
        int vec=ProfilerProfile.createEventsVector(b,events),name=b.createString("#"+id+" (LAUNCHER)");
        int profile=ProfilerProfile.createProfilerProfile(b,name,vec);
        return ProfilerFile.createProfilerFile(b,frameVec,ProfilerFile.createProfilesVector(b,new int[]{profile}));
    }
    static void flatbufferSelftest() {
        FlatBufferBuilder b=new FlatBufferBuilder(4096);
        int a=TeamData.createTeamData(b,b.createString("alias_A"),b.createString("c_bc3"),(byte)1);
        int bb=TeamData.createTeamData(b,b.createString("alias_B"),b.createString("arch_ampmid"),(byte)2);
        int header=GameHeader.createGameHeader(b,0,GameHeader.createTeamsVector(b,new int[]{a,bb}),0,0);
        int headerE=EventWrapper.createEventWrapper(b,Event.GameHeader,header);
        int ids=SpawnedBodyTable.createRobotIDsVector(b,new int[]{17,18,19});
        int teams=SpawnedBodyTable.createTeamIDsVector(b,new byte[]{1,2,1});
        int types=SpawnedBodyTable.createTypesVector(b,new byte[]{2,2,2});
        int bodies=SpawnedBodyTable.createSpawnedBodyTable(b,ids,teams,types,0),mapName=b.createString("fixture");
        GameMap.startGameMap(b);GameMap.addBodies(b,bodies);GameMap.addName(b,mapName);int map=GameMap.endGameMap(b);
        int mh=MatchHeader.createMatchHeader(b,map,2000),mhE=EventWrapper.createEventWrapper(b,Event.MatchHeader,mh);
        int bcIds=Round.createBytecodeIDsVector(b,new int[]{17,18,19}),used=Round.createBytecodesUsedVector(b,new int[]{50,50,50});
        int exText=b.createString("N0|ov=0,ex=0,nm=0"),exBad=b.createString("N0|ov=0,ex=1,nm=0");
        int text=Round.createIndicatorStringsVector(b,new int[]{exText,exBad,exText});
        Round.startRound(b);Round.addRoundID(b,12);Round.addBytecodeIDs(b,bcIds);Round.addBytecodesUsed(b,used);
        Round.addIndicatorStringIDs(b,bcIds);Round.addIndicatorStrings(b,text);int round=Round.endRound(b);
        int roundE=EventWrapper.createEventWrapper(b,Event.Round,round);
        // File index is deliberately reversed; robot ID, not file order, determines team.
        int fileB=fixtureProfile(b,18,"arch_ampmid"),fileA=fixtureProfile(b,17,"c_bc3");
        int footer=MatchFooter.createMatchFooter(b,(byte)1,12,MatchFooter.createProfilerFilesVector(b,new int[]{fileB,fileA}));
        int footerE=EventWrapper.createEventWrapper(b,Event.MatchFooter,footer);
        int ev=GameWrapper.createEventsVector(b,new int[]{headerE,mhE,roundE,footerE});GameWrapper.startGameWrapper(b);GameWrapper.addEvents(b,ev);
        b.finish(GameWrapper.endGameWrapper(b));
        StringWriter robots=new StringWriter(),calls=new StringWriter(),files=new StringWriter();
        PrintWriter ro=new PrintWriter(robots),co=new PrintWriter(calls),fo=new PrintWriter(files);
        process(GameWrapper.getRootAsGameWrapper(b.dataBuffer()),ro,co,fo);ro.flush();co.flush();fo.flush();
        String rs=robots.toString(),cs=calls.toString();
        require(rs.contains("\"file\":0,\"robot\":18,\"side\":\"B\",\"package\":\"arch_ampmid\""),"file order does not erase team identity");
        require(rs.contains("\"robot\":19")&&rs.contains("\"missing_profile\""),"missing launcher contributes denominator");
        require(cs.contains("\"native_inclusive\":10,\"native_exclusive\":7")&&cs.contains("\"round\":12,\"entry_budget\":9990"),"schema profile intervals join replay turns");
        require(files.toString().contains("\"open_events\":5")&&files.toString().contains("\"capped\":false"),"cap counts opens rather than closes");
        require(rs.contains("\"recorded_caught_exceptions\":0")&&rs.contains("\"zero_recorded_exceptions\":true"),"zero exception evidence from regular telemetry");
        String exceptionalRobot="",exceptionalCall="";
        for(String line:rs.split("\n"))if(line.contains("\"robot\":18,"))exceptionalRobot=line;
        for(String line:cs.split("\n"))if(line.contains("\"robot\":18,")&&line.contains("\"method\":\"mendUpdate\""))exceptionalCall=line;
        require(exceptionalRobot.contains("\"exception_status\":\"observed_exception\"")&&exceptionalRobot.contains("\"native_costs_usable\":false"),"positive ex censors even balanced native trace");
        require(exceptionalCall.contains("\"caller_frame\":null")&&exceptionalCall.contains("\"native_inclusive\":null")&&exceptionalCall.contains("\"native_exclusive\":null")
            &&exceptionalCall.contains("\"entry_budget\":null")&&exceptionalCall.contains("\"return_budget\":null")&&exceptionalCall.contains("\"fallback_witness\":null"),"exception censorship removes costs/caller/budgets/fallback classification");
        require(exceptionalRobot.contains("\"mendUpdate\":1")&&exceptionalRobot.contains("\"frequency_exact\":false"),"exception entries remain lower bounds");
    }
    static void fallbackSelftest() {
        String[] f={"c_mend3.RobotPlayer.run","c_mend3.Telemetry.startTurn","c_mend3.Launcher.run",
            "c_mend3.Launcher.mendUpdate","c_mend3.Comms.read","c_mend3.Comms.nearestEnemy",
            "c_mend3.Launcher.march","c_mend3.Launcher.pickObjective"};
        int[] at={0,0,1,5,10,12,17,20,21,26,30,32,37,45,48,50,80,100,110,120};
        int[] frame={0,1,1,2,3,4,4,5,4,4,5,4,4,3,6,7,7,6,2,0};
        boolean[] open={true,true,false,true,true,true,false,true,true,false,false,true,false,false,true,true,false,false,false,false};
        Trace trace=parse(f,at,frame,open);Robot robot=new Robot(1,1,2);robot.turns.add(new Turn(320,120));
        Interval mend=null;for(Interval value:trace.intervals)if(value.method.equals("mendUpdate"))mend=value;
        require(trace.valid&&mend!=null&&alignment(trace,robot,10000,false),"nested fallback trace aligns without games");
        String fields=mendFields(trace,mend,robot,10000,true,true);
        require(fields.contains("\"fallback_witness\":true")&&fields.contains("\"direct_reads_after_nearest\":1"),"post-nearest direct read witnesses fallback");
        require(fields.contains("\"direct_reads_before_nearest\":1"),"nested nearest read is excluded from direct reads");
        require(fields.contains("\"following_march_inclusive\":52")&&fields.contains("\"following_pick_objective_inclusive\":30")
            &&fields.contains("\"launcher_tail_inclusive\":65"),"following same-run tail measured");
        robot.heals.add(new Heal(319,20));robot.heals.add(new Heal(320,4));robot.heals.add(new Heal(330,8));robot.heals.add(new Heal(331,16));robot.deathRound=331;
        fields=mendFields(trace,mend,robot,10000,true,true);
        require(fields.contains("\"replay_healed_hp_next_10_rounds\":12")&&fields.contains("\"replay_death_round\":331"),"replay healing window includes call round through plus ten only");
        require(mendFields(trace,mend,robot,10000,false,true).contains("\"fallback_witness\":null"),"unknown alignment never invents fallback");
        require(mendFields(trace,mend,robot,10000,true,false).contains("\"fallback_witness\":null"),"invalid/capped/exception trace never invents fallback");
        Trace control=parse(f,new int[]{0,0,1,5,10,12,17,20,21,26,30,45,48,50,80,100,110,120},
            new int[]{0,1,1,2,3,4,4,5,4,4,5,3,6,7,7,6,2,0},
            new boolean[]{true,true,false,true,true,true,false,true,true,false,false,false,true,true,false,false,false,false});
        Interval base=null;for(Interval value:control.intervals)if(value.method.equals("mendUpdate"))base=value;
        require(control.valid&&mendFields(control,base,robot,10000,true,true).contains("\"fallback_witness\":false"),"ordinary nearest check has no fallback witness");
        require(selected("c_mend3.Comms.read").equals("read")&&selected("c_mend3.Launcher.read")==null,"class-specific selection avoids mislabeled methods");
        require(EXCEPTIONS.matcher("N|ov=0,ex=0,nm=0").find()&&!EXCEPTIONS.matcher("ex=0").find(),"exception counter requires its telemetry separator");
    }
    static void selftest() {
        String[] f={"c_bc3.RobotPlayer.run","c_bc3.Telemetry.startTurn","c_bc3.Launcher.pickObjective","c_bc3.Launcher.mendUpdate","c_bc3.MapMem.helper"};
        Trace t=parse(f,new int[]{0,0,1,2,10,12,15,20,25,50},new int[]{0,1,1,2,3,4,4,3,2,0},new boolean[]{true,true,false,true,true,true,false,false,false,false});
        Robot r=new Robot(1,1,2);r.turns.add(new Turn(12,50));
        require(t.valid&&t.intervals.size()==2,"nested trace valid");
        Interval v=t.intervals.get(0);require(v.method.equals("mendUpdate")&&v.inclusive==10&&v.exclusive==7,"inclusive/exclusive accounting");
        require(t.entries.get("mendUpdate")==1&&v.parent.equals(f[2]),"entry and caller");
        require(alignment(t,r,10000,false),"complete counter/turn alignment");
        long[] loc=locate(t,r,v.start,10000);require(loc[0]==12&&loc[1]==9990,"round/budget alignment");
        r.turns.get(0).used=51;require(!alignment(t,r,10000,false),"counter mismatch denies inferred budget");r.turns.get(0).used=50;
        require(!alignment(t,r,10000,true),"cap denies inferred budget");
        Trace broken=parse(f,new int[]{0,1,2},new int[]{0,3,2},new boolean[]{true,true,false});
        require(!broken.valid&&broken.entries.get("mendUpdate")==1,"broken closure retains observed entry only");
        Trace terminal=parse(f,new int[]{0,0,1,10,50,50},new int[]{0,1,1,3,3,0},new boolean[]{true,true,false,true,false,false});
        require(terminal.valid&&terminal.intervals.get(0).end==terminal.lastAt,"forced terminal closure marked ambiguous by final timestamp");
        Trace saturated=parse(f,new int[]{Integer.MAX_VALUE},new int[]{0},new boolean[]{true});require(!saturated.valid,"counter saturation");
        Trace invalid=parse(f,new int[]{0},new int[]{99},new boolean[]{true});require(!invalid.valid,"invalid frame");
        Trace backwards=parse(f,new int[]{5,4},new int[]{0,0},new boolean[]{true,false});require(!backwards.valid,"nonmonotonic time");
        Trace negative=parse(f,new int[]{-1},new int[]{0},new boolean[]{true});require(!negative.valid,"negative counter");
        r.turns.get(0).used=10000;require(!alignment(t,r,10000,false),"overrun denies inferred budget");
        Robot ex=new Robot(2,1,2);ex.turns.add(new Turn(12,50));
        require(ex.exceptionStatus().equals("missing_counter"),"missing exception counter is unknown");
        ex.indicator(11,"N0|ov=0,ex=0,nm=0");require(ex.exceptionStatus().equals("unobserved_tail"),"prior zero does not prove the last turn exception-free");
        ex.indicator(12,"N0|ov=0,ex=0,nm=0");require(ex.exceptionClear(),"last-turn cumulative zero validates exception coverage");
        ex.indicator(12,"N0|ov=0,ex=1,nm=0");require(!ex.exceptionClear()&&ex.exceptionStatus().equals("observed_exception"),"positive exception counter suppresses costs");
        ex.indicator(12,"N0|ov=0,ex=0,nm=0");require(!ex.exceptionClear(),"regressing zero never clears a known exception");
        Robot death=new Robot(3,1,2);death.turns.add(new Turn(12,50));death.indicator(12,"N0|ov=0,ex=0,nm=0");death.uncaughtException=true;
        require(!death.exceptionClear(),"DIE_EXCEPTION overrides a final zero string");
        Robot malformed=new Robot(4,1,2);malformed.turns.add(new Turn(12,50));malformed.indicator(12,"N0|ex=999999999999999999999999,nm=0");
        require(malformed.exceptionStatus().equals("invalid_counter"),"out-of-range counter is invalid rather than a parser crash");
        flatbufferSelftest();
        fallbackSelftest();
        System.out.println("{\"native_parser_selftest\":\"passed\",\"checks\":"+checks+",\"games_run\":0}");
    }
    public static void main(String[] args)throws Exception {
        if(args.length==1&&args[0].equals("--selftest")){selftest();return;}
        if(args.length!=2)throw new IllegalArgumentException("NativeProfile <replay.bc23> <new extraction dir> | --selftest");
        Path out=Paths.get(args[1]);Files.createDirectory(out);
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();
        try(InputStream in=new GZIPInputStream(new FileInputStream(args[0]))) {byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1)bytes.write(buf,0,n);}
        GameWrapper wrapper=GameWrapper.getRootAsGameWrapper(ByteBuffer.wrap(bytes.toByteArray()));
        try(PrintWriter robots=new PrintWriter(Files.newBufferedWriter(out.resolve("robots.jsonl"),StandardCharsets.UTF_8));
            PrintWriter calls=new PrintWriter(Files.newBufferedWriter(out.resolve("intervals.jsonl"),StandardCharsets.UTF_8));
            PrintWriter files=new PrintWriter(Files.newBufferedWriter(out.resolve("files.jsonl"),StandardCharsets.UTF_8))) {
            process(wrapper,robots,calls,files);
        }
    }
}
