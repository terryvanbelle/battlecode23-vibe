import battlecode.schema.*;
import com.google.flatbuffers.FlatBufferBuilder;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.regex.*;
import java.util.zip.GZIPInputStream;

/** Public replay selection only. Never initializes a bot, game world or opponent classes. */
public final class OwnLauncherSelector {
    static final String REPLAY_SHA = "6544c8b768bd53579dc06473de148e464edd5262c663e7968e9586b630ec436b";
    static final int ANCHOR_START=250, MEND_HP=80, MEND_R2=144, LAUNCHER=2;
    static final Pattern EX_COUNTER=Pattern.compile("(?:^|[|,])ex=([0-9]+)(?:,|$)");
    static final int RAW_LIMIT=512*1024*1024;
    static final class Witness {
        int round,hp,x,y,near;
        Witness(int r,int h,int px,int py,int n) {round=r;hp=h;x=px;y=py;near=n;}
    }
    static final class Robot {
        int id,team,type,born,death=-1,hp,x,y,lastTurn=-1,turns,postTurns,overruns,minHp=1000000;
        int lowHp,nearOne,nearTwo,mendObjects,firstMend=-1,lastExRound=-1;
        long bytecodes,healed,maxEx,lastEx;
        boolean exSeen,exInvalid,exceptionDeath;
        final List<Witness> witnesses=new ArrayList<>();
        Robot(int i,int tm,int ty,int r,int h,int px,int py) {id=i;team=tm;type=ty;born=r;hp=h;x=px;y=py;}
        boolean ownLauncher() {return team==1&&type==LAUNCHER;}
        boolean exceptionClear() {return exSeen&&!exInvalid&&!exceptionDeath&&maxEx==0&&lastExRound==lastTurn;}
        boolean opportunityObserved() {return mendObjects>0||lowHp>0;}
    }
    static final class Model {
        int width,height,seed,rounds,headers,footers,footerRound,ownTurns,ownPostTurns;
        String map,packageA,packageB;
        final int[] health=new int[6],limits=new int[6];
        final TreeMap<Integer,Robot> robots=new TreeMap<>();
        final Map<Integer,List<int[]>> islandTiles=new TreeMap<>();
        final Map<Integer,Integer> islandOwners=new HashMap<>();
    }
    static String quote(String value) {
        if(value==null)return "null";
        StringBuilder out=new StringBuilder("\"");
        for(char c:value.toCharArray()) {
            if(c=='"'||c=='\\')out.append('\\');
            if(c<32)out.append(String.format("\\u%04x",(int)c));else out.append(c);
        }
        return out.append('"').toString();
    }
    static String hex(byte[] bytes) {
        StringBuilder text=new StringBuilder();for(byte b:bytes)text.append(String.format("%02x",b&255));return text.toString();
    }
    static String sha(Path path) throws Exception {
        MessageDigest digest=MessageDigest.getInstance("SHA-256");
        try(InputStream input=Files.newInputStream(path)) {byte[] block=new byte[65536];int count;while((count=input.read(block))!=-1)digest.update(block,0,count);}
        return hex(digest.digest());
    }
    static void pin(String observed) {if(!REPLAY_SHA.equals(observed))throw new IllegalArgumentException("preserved off replay SHA-256 mismatch");}
    static byte[] gunzip(Path path) throws IOException {
        try(InputStream input=new GZIPInputStream(new BufferedInputStream(Files.newInputStream(path)))) {
            ByteArrayOutputStream output=new ByteArrayOutputStream();byte[] block=new byte[65536];int count;
            while((count=input.read(block))!=-1) {
                if(output.size()>RAW_LIMIT-count)throw new IOException("decompressed replay exceeds 512 MiB read bound");
                output.write(block,0,count);
            }
            return output.toByteArray();
        }
    }
    static Robot robot(Model model,int id) {
        Robot robot=model.robots.get(id);if(robot==null)throw new IllegalArgumentException("event refers to unknown robot "+id);return robot;
    }
    static void spawn(Model model,SpawnedBodyTable bodies,int round) {
        if(bodies==null)return;
        if(bodies.teamIDsLength()!=bodies.robotIDsLength()||bodies.typesLength()!=bodies.robotIDsLength())throw new IllegalArgumentException("spawn vector length mismatch");
        VecTable locs=bodies.locs();
        for(int i=0;i<bodies.robotIDsLength();i++) {
            int id=bodies.robotIDs(i),type=bodies.types(i);
            if(type<0||type>=model.health.length||model.health[type]<=0||locs==null)throw new IllegalArgumentException("spawn metadata unavailable");
            if(model.robots.containsKey(id))throw new IllegalArgumentException("duplicate spawned robot");
            model.robots.put(id,new Robot(id,bodies.teamIDs(i),type,round,model.health[type],locs.xs(i),locs.ys(i)));
        }
    }
    static void indicator(Robot robot,int round,String text) {
        if(!robot.ownLauncher()||text==null)return;
        Matcher match=EX_COUNTER.matcher(text);if(!match.find())return;
        long value;
        try {value=Long.parseLong(match.group(1));}catch(NumberFormatException error){robot.exInvalid=true;return;}
        if(robot.exSeen&&value<robot.lastEx)robot.exInvalid=true;
        robot.exSeen=true;robot.lastEx=value;robot.maxEx=Math.max(robot.maxEx,value);robot.lastExRound=round;
    }
    static void action(Model model,int id,byte type,int value) {
        if(type==Action.CHANGE_HEALTH) {
            Robot robot=robot(model,id);robot.hp+=value;if(value>0)robot.healed+=value;
            if(robot.hp>model.health[robot.type])throw new IllegalArgumentException("health exceeds header maximum");
        } else if(type==Action.DIE_EXCEPTION)robot(model,id).exceptionDeath=true;
    }
    static int nearOwned(Model model,Robot robot) {
        int near=0;
        for(Map.Entry<Integer,List<int[]>> island:model.islandTiles.entrySet()) {
            if(!Integer.valueOf(1).equals(model.islandOwners.get(island.getKey())))continue;
            for(int[] tile:island.getValue()) {
                int dx=robot.x-tile[0],dy=robot.y-tile[1];
                if(dx*dx+dy*dy<=MEND_R2) {near++;break;}
            }
        }
        return near;
    }
    static void boundary(Model model,Robot robot,int round) {
        if(!robot.ownLauncher()||round<ANCHOR_START||robot.death>=0)return;
        robot.minHp=Math.min(robot.minHp,robot.hp);
        if(robot.hp<=0||robot.hp>MEND_HP)return;
        robot.lowHp++;
        int near=nearOwned(model,robot);
        if(near>=1)robot.nearOne++;
        if(near>=2)robot.nearTwo++;
        if(robot.witnesses.size()<5)robot.witnesses.add(new Witness(round,robot.hp,robot.x,robot.y,near));
    }
    static void objective(Model model,Robot robot,int round,int packed,int loc,int r0) {
        if(!robot.ownLauncher()||round<ANCHOR_START||r0!=round||(packed&15)!=3||loc<=0)return;
        int x=(loc-1)/64,y=(loc-1)%64;
        if(x<0||y<0||x>=model.width||y>=model.height||x==model.width/2&&y==model.height/2)return;
        robot.mendObjects++;if(robot.firstMend<0)robot.firstMend=round;
    }
    static Model parse(GameWrapper wrapper) {
        Model model=new Model();
        for(int index=0;index<wrapper.eventsLength();index++) {
            EventWrapper event=wrapper.events(index);
            if(event.eType()==Event.GameHeader) {
                GameHeader header=(GameHeader)event.e(new GameHeader());
                for(int i=0;i<header.bodyTypeMetadataLength();i++) {
                    BodyTypeMetadata metadata=header.bodyTypeMetadata(i);int type=metadata.type();
                    if(type>=0&&type<6){model.health[type]=metadata.health();model.limits[type]=metadata.bytecodeLimit();}
                }
                for(int i=0;i<header.teamsLength();i++) {
                    TeamData team=header.teams(i);
                    if(team.teamID()==1)model.packageA=team.packageName();
                    if(team.teamID()==2)model.packageB=team.packageName();
                }
            } else if(event.eType()==Event.MatchHeader) {
                if(++model.headers!=1)throw new IllegalArgumentException("exactly one game required");
                GameMap map=((MatchHeader)event.e(new MatchHeader())).map();
                model.map=map.name();model.seed=map.randomSeed();
                model.width=map.maxCorner().x()-map.minCorner().x();model.height=map.maxCorner().y()-map.minCorner().y();
                if(model.width<1||model.height<1||model.width>60||model.height>60||map.islandsLength()!=model.width*model.height)throw new IllegalArgumentException("map dimensions/islands mismatch");
                for(int i=0;i<map.islandsLength();i++)if(map.islands(i)>0)
                    model.islandTiles.computeIfAbsent(map.islands(i),key->new ArrayList<>()).add(new int[]{i%model.width,i/model.width});
                spawn(model,map.bodies(),0);
            } else if(event.eType()==Event.Round) {
                Round round=(Round)event.e(new Round());int rn=round.roundID();
                if(model.headers!=1||rn<=model.rounds)throw new IllegalArgumentException("round order invalid");
                model.rounds=rn;spawn(model,round.spawnedBodies(),rn);
                if(round.actionIDsLength()!=round.actionsLength()||round.actionTargetsLength()!=round.actionsLength())throw new IllegalArgumentException("action vector mismatch");
                for(int i=0;i<round.actionsLength();i++)action(model,round.actionIDs(i),round.actions(i),round.actionTargets(i));
                VecTable moved=round.movedLocs();
                for(int i=0;i<round.movedIDsLength();i++) {
                    Robot robot=robot(model,round.movedIDs(i));robot.x=moved.xs(i);robot.y=moved.ys(i);
                }
                if(round.islandIDsLength()!=round.islandOwnershipLength())throw new IllegalArgumentException("island ownership vector mismatch");
                for(int i=0;i<round.islandIDsLength();i++)model.islandOwners.put(round.islandIDs(i),round.islandOwnership(i));
                for(int i=0;i<round.diedIDsLength();i++)robot(model,round.diedIDs(i)).death=rn;
                if(round.bytecodeIDsLength()!=round.bytecodesUsedLength())throw new IllegalArgumentException("bytecode vector mismatch");
                Set<Integer> acted=new HashSet<>();
                for(int i=0;i<round.bytecodeIDsLength();i++) {
                    Robot robot=robot(model,round.bytecodeIDs(i));int used=round.bytecodesUsed(i);
                    if(!acted.add(robot.id)||used<0)throw new IllegalArgumentException("duplicate/negative turn bytecodes");
                    if(!robot.ownLauncher())continue;
                    robot.lastTurn=rn;robot.turns++;robot.bytecodes+=used;model.ownTurns++;
                    if(used>=model.limits[robot.type])robot.overruns++;
                    if(rn>=ANCHOR_START){robot.postTurns++;model.ownPostTurns++;}
                    boundary(model,robot,rn);
                }
                if(round.indicatorStringIDsLength()!=round.indicatorStringsLength())throw new IllegalArgumentException("indicator string vector mismatch");
                for(int i=0;i<round.indicatorStringIDsLength();i++)indicator(robot(model,round.indicatorStringIDs(i)),rn,round.indicatorStrings(i));
                VecTable locs=round.indicatorDotLocs();RGBTable colors=round.indicatorDotRGBs();
                for(int i=0;i<round.indicatorDotIDsLength();i++) {
                    if(locs==null||colors==null)throw new IllegalArgumentException("indicator dot vectors unavailable");
                    if(locs.xs(i)==-15)objective(model,robot(model,round.indicatorDotIDs(i)),rn,locs.ys(i),colors.red(i),colors.blue(i));
                }
            } else if(event.eType()==Event.MatchFooter) {
                MatchFooter footer=(MatchFooter)event.e(new MatchFooter());model.footers++;model.footerRound=footer.totalRounds();
                if(footer.profilerFilesLength()!=0)throw new IllegalArgumentException("selector requires profiler-off replay");
            }
        }
        if(model.headers!=1||model.footers!=1||model.rounds<ANCHOR_START||model.rounds!=model.footerRound)throw new IllegalArgumentException("terminal single-game shape invalid");
        if(!"Cornucopia".equals(model.map)||model.seed!=272||!"c_mend2".equals(model.packageA)||!"arch_ampmid".equals(model.packageB))throw new IllegalArgumentException("frozen own matchup/map/seed mismatch");
        if(model.health[LAUNCHER]!=200||model.limits[LAUNCHER]!=10000)throw new IllegalArgumentException("launcher header metadata mismatch");
        return model;
    }
    static List<Robot> select(Model model,int count) {
        if(count<3||count>5)throw new IllegalArgumentException("selection count must be 3..5");
        List<Robot> candidates=new ArrayList<>();
        for(Robot robot:model.robots.values())if(robot.ownLauncher()&&robot.opportunityObserved()&&robot.overruns==0&&robot.exceptionClear())candidates.add(robot);
        candidates.sort((left,right)->{
            int c=Boolean.compare(right.mendObjects>0,left.mendObjects>0);if(c!=0)return c;
            c=Integer.compare(right.mendObjects,left.mendObjects);if(c!=0)return c;
            c=Integer.compare(right.nearTwo,left.nearTwo);if(c!=0)return c;
            c=Integer.compare(right.nearOne,left.nearOne);if(c!=0)return c;
            c=Integer.compare(right.lowHp,left.lowHp);if(c!=0)return c;
            c=Integer.compare(right.postTurns,left.postTurns);if(c!=0)return c;
            c=Integer.compare(left.born,right.born);return c!=0?c:Integer.compare(left.id,right.id);
        });
        return new ArrayList<>(candidates.subList(0,Math.min(count,candidates.size())));
    }
    static String report(Model model,List<Robot> selected,int count,String replayHash) {
        StringBuilder out=new StringBuilder("{\"schema_version\":1,\"games_run\":0,\"input_replay_sha256\":").append(quote(replayHash))
            .append(",\"map\":").append(quote(model.map)).append(",\"map_seed\":").append(model.seed)
            .append(",\"side\":\"A\",\"package\":\"c_mend2\",\"match_rounds\":").append(model.rounds)
            .append(",\"requested_count\":").append(count).append(",\"selection_complete\":").append(selected.size()==count).append(",\"selected_ids\":[");
        long selectedTurns=0,selectedPost=0,selectedBytecodes=0;
        for(int i=0;i<selected.size();i++){Robot r=selected.get(i);if(i>0)out.append(',');out.append(r.id);selectedTurns+=r.turns;selectedPost+=r.postTurns;selectedBytecodes+=r.bytecodes;}
        out.append("],\"selected\":[");
        for(int i=0;i<selected.size();i++) {
            Robot r=selected.get(i);if(i>0)out.append(',');
            out.append("{\"id\":").append(r.id).append(",\"born_round\":").append(r.born).append(",\"recorded_death_round\":").append(r.death<0?"null":r.death)
                .append(",\"recorded_turns\":").append(r.turns).append(",\"recorded_turns_from_250\":").append(r.postTurns)
                .append(",\"recorded_bytecodes\":").append(r.bytecodes).append(",\"round_boundary_low_hp_turns_from_250\":").append(r.lowHp)
                .append(",\"round_boundary_low_hp_near_owned_island_turns\":").append(r.nearOne)
                .append(",\"round_boundary_low_hp_near_two_owned_islands_turns\":").append(r.nearTwo)
                .append(",\"fresh_noncentre_kind3_obj_events\":").append(r.mendObjects).append(",\"first_mending_obj_round\":").append(r.firstMend<0?"null":r.firstMend)
                .append(",\"lifetime_recorded_healed_hp\":").append(r.healed).append(",\"minimum_boundary_hp_from_250\":").append(r.minHp==1000000?"null":r.minHp)
                .append(",\"recorded_overruns\":").append(r.overruns).append(",\"exception_status\":\"zero_through_last_recorded_turn\",\"witness_rounds\":[");
            for(int j=0;j<r.witnesses.size();j++){Witness w=r.witnesses.get(j);if(j>0)out.append(',');out.append("{\"round\":").append(w.round).append(",\"end_round_hp\":").append(w.hp).append(",\"end_round_position\":[").append(w.x).append(',').append(w.y).append("],\"publicly_owned_islands_with_tile_within_144\":").append(w.near).append('}');}
            out.append("]}");
        }
        return out.append("],\"observed_selected_turns\":").append(selectedTurns).append(",\"observed_selected_turns_from_250\":").append(selectedPost)
            .append(",\"observed_selected_bytecodes\":").append(selectedBytecodes)
            .append(",\"selection_rule\":\"Own A launchers only, no recorded overruns or DIE_EXCEPTION, cumulative ex=0 through final recorded turn; rank fresh non-centre kind3 OBJ witnesses, then boundary HP<=80 from r250 near two/one owned islands, low-HP turns, post250 turns, birth and id.\"")
            .append(",\"native_open_event_forecast\":null,\"native_open_cap_per_team\":2000000")
            .append(",\"limits\":[\"Boundary HP/positions and public island ownership are replay proxies; they do not establish own-turn sensed enemies, cooldown readiness, shared-array contents, blocked-nearest or fallback entry.\",\"Fresh non-centre kind3 OBJ is evidence of a mending march objective in this frozen own source, not a fallback witness.\",\"The off replay supplies no native OPEN event counts; bytecode and turn totals cannot calibrate the event-volume or cap forecast.\",\"Explicit baseline IDs may be absent or a different type in a candidate after decisions/spawn order diverge; the sampled run must validate identity and actual selected coverage.\",\"A null death round means no death recorded this match, not post-match survival. Missing selection evidence leaves an incomplete selection instead of invented IDs.\"]}").toString();
    }
    static int checks;
    static void require(boolean test,String message){checks++;if(!test)throw new AssertionError(message);}
    static int vecs(FlatBufferBuilder b,int[] xs,int[] ys){int x=VecTable.createXsVector(b,xs),y=VecTable.createYsVector(b,ys);return VecTable.createVecTable(b,x,y);}
    static byte[] fixture() {
        FlatBufferBuilder b=new FlatBufferBuilder(65536);
        int ta=TeamData.createTeamData(b,b.createString("c_mend2"),b.createString("c_mend2"),(byte)1),tb=TeamData.createTeamData(b,b.createString("arch_ampmid"),b.createString("arch_ampmid"),(byte)2);
        BodyTypeMetadata.startBodyTypeMetadata(b);BodyTypeMetadata.addType(b,(byte)LAUNCHER);BodyTypeMetadata.addHealth(b,200);BodyTypeMetadata.addBytecodeLimit(b,10000);int meta=BodyTypeMetadata.endBodyTypeMetadata(b);
        int teams=GameHeader.createTeamsVector(b,new int[]{ta,tb}),metas=GameHeader.createBodyTypeMetadataVector(b,new int[]{meta});
        GameHeader.startGameHeader(b);GameHeader.addTeams(b,teams);GameHeader.addBodyTypeMetadata(b,metas);int header=GameHeader.endGameHeader(b);
        int he=EventWrapper.createEventWrapper(b,Event.GameHeader,header);
        int ids=SpawnedBodyTable.createRobotIDsVector(b,new int[]{17,19,21,25}),tms=SpawnedBodyTable.createTeamIDsVector(b,new byte[]{1,1,1,2}),tys=SpawnedBodyTable.createTypesVector(b,new byte[]{2,2,2,2});
        int locs=vecs(b,new int[]{29,30,31,30},new int[]{30,29,30,30});int bodies=SpawnedBodyTable.createSpawnedBodyTable(b,ids,tms,tys,locs);
        int[] tiles=new int[3600];tiles[29+29*60]=1;tiles[32+30*60]=2;int iv=GameMap.createIslandsVector(b,tiles),name=b.createString("Cornucopia");
        GameMap.startGameMap(b);GameMap.addName(b,name);GameMap.addRandomSeed(b,272);GameMap.addBodies(b,bodies);GameMap.addIslands(b,iv);GameMap.addMinCorner(b,Vec.createVec(b,0,0));GameMap.addMaxCorner(b,Vec.createVec(b,60,60));int map=GameMap.endGameMap(b);
        int mh=MatchHeader.createMatchHeader(b,map,2000),me=EventWrapper.createEventWrapper(b,Event.MatchHeader,mh);
        int[] re=new int[2];
        for(int turn=0;turn<2;turn++) {
            int r=250+turn,ais=Round.createActionIDsVector(b,turn==0?new int[]{17,19,21,25}:new int[]{17,19});
            byte[] actions=turn==0?new byte[]{Action.CHANGE_HEALTH,Action.CHANGE_HEALTH,Action.CHANGE_HEALTH,Action.CHANGE_HEALTH}:new byte[]{Action.CHANGE_HEALTH,Action.CHANGE_HEALTH};
            int acts=Round.createActionsVector(b,actions),targets=Round.createActionTargetsVector(b,turn==0?new int[]{-140,-120,-160,-180}:new int[]{20,20});
            int islands=Round.createIslandIDsVector(b,new int[]{1,2}),owners=Round.createIslandOwnershipVector(b,new int[]{1,1});
            int bcids=Round.createBytecodeIDsVector(b,new int[]{17,19,21,25}),used=Round.createBytecodesUsedVector(b,new int[]{9000,9000,9000,9000});
            int strings=Round.createIndicatorStringsVector(b,new int[]{b.createString("N0|ov=0,ex=0,nm=0"),b.createString("N0|ov=0,ex=0,nm=0"),b.createString("N0|ov=0,ex=0,nm=0")});
            int stringIds=Round.createIndicatorStringIDsVector(b,new int[]{17,19,21}),dots=Round.createIndicatorDotIDsVector(b,new int[]{17});
            int dotloc=vecs(b,new int[]{-15},new int[]{3}),red=RGBTable.createRedVector(b,new int[]{(turn==0?29:30)*64+(turn==0?29:30)+1}),green=RGBTable.createGreenVector(b,new int[]{29*64+30+1}),blue=RGBTable.createBlueVector(b,new int[]{r}),rgb=RGBTable.createRGBTable(b,red,green,blue);
            Round.startRound(b);Round.addRoundID(b,r);Round.addActionIDs(b,ais);Round.addActions(b,acts);Round.addActionTargets(b,targets);Round.addIslandIDs(b,islands);Round.addIslandOwnership(b,owners);Round.addBytecodeIDs(b,bcids);Round.addBytecodesUsed(b,used);Round.addIndicatorStringIDs(b,stringIds);Round.addIndicatorStrings(b,strings);Round.addIndicatorDotIDs(b,dots);Round.addIndicatorDotLocs(b,dotloc);Round.addIndicatorDotRGBs(b,rgb);int round=Round.endRound(b);re[turn]=EventWrapper.createEventWrapper(b,Event.Round,round);
        }
        int footer=MatchFooter.createMatchFooter(b,(byte)1,251,0),fe=EventWrapper.createEventWrapper(b,Event.MatchFooter,footer),events=GameWrapper.createEventsVector(b,new int[]{he,me,re[0],re[1],fe});
        GameWrapper.startGameWrapper(b);GameWrapper.addEvents(b,events);int wrapper=GameWrapper.endGameWrapper(b);b.finish(wrapper);return b.sizedByteArray();
    }
    static void selftest() throws Exception {
        Model model=parse(GameWrapper.getRootAsGameWrapper(ByteBuffer.wrap(fixture())));List<Robot> selected=select(model,3);
        require(selected.size()==3,"three actual own fixture robots");require(selected.get(0).id==17&&selected.get(1).id==21&&selected.get(2).id==19,"evidence ranking deterministic");
        require(model.ownTurns==6&&model.ownPostTurns==6,"only own acted turns counted");require(robot(model,17).hp==80&&robot(model,17).healed==20,"health deltas rebuilt");
        require(robot(model,17).mendObjects==1,"noncentre OBJ counted; centre ignored");require(robot(model,21).nearTwo==2,"near distinct public owned islands");
        require(robot(model,19).lowHp==1,"HP threshold inclusive and HP above eighty excluded");require(selected.stream().noneMatch(r->r.id==25),"other side never selected");
        objective(model,robot(model,21),251,3,29*64+29+1,250);require(robot(model,21).mendObjects==0,"stale OBJ excluded");
        int before=robot(model,21).lowHp;boundary(model,robot(model,21),249);require(robot(model,21).lowHp==before,"anchor start boundary");
        robot(model,21).overruns=1;require(select(model,3).size()==2,"recorded overrun excludes selection");robot(model,21).overruns=0;
        robot(model,21).lastExRound=250;require(select(model,3).size()==2,"stale zero ex excluded");robot(model,21).lastExRound=251;
        indicator(robot(model,21),251,"N0|ov=0,ex=1,nm=0");require(select(model,3).size()==2,"positive ex excluded");
        action(model,17,Action.DIE_EXCEPTION,0);require(!robot(model,17).exceptionClear()&&select(model,3).stream().noneMatch(r->r.id==17),"engine exception excludes even final cumulative ex zero");
        String report=report(model,select(model,3),3,"synthetic");require(report.contains("\"selection_complete\":false")&&report.contains("\"native_open_event_forecast\":null"),"missing evidence and event forecast remain unknown");
        boolean rejected=false;try{pin("bad");}catch(IllegalArgumentException expected){rejected=true;}require(rejected,"default input hash pin fails closed");pin(REPLAY_SHA);
        require(hex(MessageDigest.getInstance("SHA-256").digest("abc".getBytes(StandardCharsets.UTF_8))).equals("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),"SHA known answer");
        System.out.println("{\"selector_selftest\":\"passed\",\"checks\":"+checks+",\"games_run\":0}");
    }
    public static void main(String[] args) throws Exception {
        if(args.length==1&&args[0].equals("--selftest")){selftest();return;}
        if(args.length<1||args.length>2)throw new IllegalArgumentException("OwnLauncherSelector EXACT_OFF_REPLAY [3..5]");
        Path replay=Paths.get(args[0]);if(Files.isSymbolicLink(replay)||!Files.isRegularFile(replay))throw new IllegalArgumentException("input replay must be a regular file");
        String digest=sha(replay);pin(digest);int count=args.length==2?Integer.parseInt(args[1]):3;
        Model model=parse(GameWrapper.getRootAsGameWrapper(ByteBuffer.wrap(gunzip(replay))));pin(sha(replay));List<Robot> selected=select(model,count);
        System.out.println(report(model,selected,count,digest));if(selected.size()!=count)System.exit(3);
    }
}
