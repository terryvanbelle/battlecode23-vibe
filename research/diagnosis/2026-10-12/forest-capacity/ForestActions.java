import battlecode.schema.*;
import com.google.flatbuffers.FlatBufferBuilder;
import java.io.*;
import java.nio.ByteBuffer;
import java.util.*;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;

/** Read existing game 4 only. No robot classes, instrumentation, simulation or subprocesses. */
public final class ForestActions {
    static final int[][] WINDOWS={{1,100},{101,250},{251,500},{501,1000}};
    static final int[] CHECKPOINTS={100,250,500,1000};
    static final class Body {int team,type;Body(int t,int y){team=t;type=y;}}
    static final class Sum {
        int side,well,resource,window,first=Integer.MAX_VALUE,last,actions,maxAmount,multiTurns,maxActionsPerTurn;
        long amount;Set<Integer> carriers=new HashSet<>();Map<Integer,Integer> turnActions=new HashMap<>();
        Sum(int s,int w,int r,int p){side=s;well=w;resource=r;window=p;}
        void add(int round,int actor,int kg) {
            amount+=kg;actions++;first=Math.min(first,round);last=Math.max(last,round);maxAmount=Math.max(maxAmount,kg);carriers.add(actor);
            int n=turnActions.getOrDefault(actor,0)+1;turnActions.put(actor,n);if(n==2)multiTurns++;maxActionsPerTurn=Math.max(maxActionsPerTurn,n);
        }
        void endRound(){turnActions.clear();}
    }
    static String q(String s){return "\""+s.replace("\\","\\\\").replace("\"","\\\"")+"\"";}
    static String res(int n){return n==1?"Ad":n==2?"Mn":n==3?"Ex":"?";}
    static String xy(int index,int w,int ox,int oy){return "["+(ox+index%w)+","+(oy+index/w)+"]";}
    static void spawn(Map<Integer,Body> bodies,SpawnedBodyTable s) {
        if(s!=null)for(int i=0;i<s.robotIDsLength();i++)bodies.put(s.robotIDs(i),new Body(s.teamIDs(i),s.types(i)));
    }
    static int resourceAction(int a){return a==Action.CHANGE_ADAMANTIUM?1:a==Action.CHANGE_MANA?2:a==Action.CHANGE_ELIXIR?3:0;}
    static String key(int side,int well,int resource,int window){return side+":"+well+":"+resource+":"+window;}
    static Sum sum(Map<String,Sum> sums,int side,int well,int resource,int window){return sums.computeIfAbsent(key(side,well,resource,window),k->new Sum(side,well,resource,window));}
    static void read(String replay,int match,PrintStream out)throws Exception {
        File file=new File(replay);if(file.length()>64L*1024*1024)throw new IOException("compressed replay exceeds64MiB bound");
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();
        try(InputStream in=new GZIPInputStream(new FileInputStream(file))) {
            byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1){if(bytes.size()+(long)n>768L*1024*1024)throw new IOException("inflated replay exceeds768MiB bound");bytes.write(buf,0,n);}
        }
        GameWrapper game=GameWrapper.getRootAsGameWrapper(ByteBuffer.wrap(bytes.toByteArray()));
        Map<Integer,Body> bodies=new HashMap<>();Map<String,Sum> sums=new TreeMap<>(),deposits=new TreeMap<>();
        List<String> snapshots=new ArrayList<>(),changes=new ArrayList<>(),roundPeaks=new ArrayList<>();
        Map<Integer,int[]> previousWells=new HashMap<>();Set<Integer> initialWells=new HashSet<>(),hqs=new HashSet<>();
        int gi=-1,w=0,h=0,ox=0,oy=0,roundsWalked=0,maxRound=0,unpairedPickups=0,unpairedPlaces=0,zeroPickups=0;
        String map="?";long[] totals=new long[4],paired={0};int[] hqCounts=new int[3];
        for(int ei=0;ei<game.eventsLength();ei++) {
            EventWrapper ev=game.events(ei);
            if(ev.eType()==Event.MatchHeader) {
                gi++;if(gi!=4)continue;GameMap m=((MatchHeader)ev.e(new MatchHeader())).map();map=m.name();
                if(!map.equals("Forest"))throw new IOException("game4 is notForest");
                ox=m.minCorner().x();oy=m.minCorner().y();w=m.maxCorner().x()-ox;h=m.maxCorner().y()-oy;
                spawn(bodies,m.bodies());
                SpawnedBodyTable initial=m.bodies();for(int j=0;j<initial.robotIDsLength();j++)if(initial.types(j)==0) {
                    hqs.add(initial.locs().xs(j)-ox+(initial.locs().ys(j)-oy)*w);
                    if(initial.teamIDs(j)>0&&initial.teamIDs(j)<3)hqCounts[initial.teamIDs(j)]++;
                }
                for(int j=0;j<w*h;j++)if(m.resources(j)>0){initialWells.add(j);previousWells.put(j,new int[]{m.resources(j),0,0,0,0});}
            }
            if(gi!=4||ev.eType()!=Event.Round)continue;
            Round r=(Round)ev.e(new Round());int rn=r.roundID();if(rn>1000)continue;roundsWalked++;maxRound=Math.max(maxRound,rn);spawn(bodies,r.spawnedBodies());
            int window=rn<=100?0:rn<=250?1:rn<=500?2:3;
            Map<String,Long> roundAmount=new TreeMap<>();int prevId=-1,prevResource=0,prevAmount=0;
            for(int a=0;a<r.actionsLength();a++) {
                int action=r.actions(a),actor=r.actionIDs(a),target=r.actionTargets(a),resource=resourceAction(action);
                if(resource>0){prevId=actor;prevResource=resource;prevAmount=target;continue;}
                Body body=bodies.get(actor);
                if(action==Action.PICK_UP_RESOURCE) {
                    if(body==null||body.type!=1||prevId!=actor||prevResource==0||prevAmount<0||!initialWells.contains(target))unpairedPickups++;
                    else {
                        sum(sums,body.team,target,prevResource,window).add(rn,actor,prevAmount);totals[prevResource]+=prevAmount;paired[0]++;
                        String rk=key(body.team,target,prevResource,0);roundAmount.put(rk,roundAmount.getOrDefault(rk,0L)+prevAmount);
                        if(prevAmount==0)zeroPickups++;
                    }
                } else if(action==Action.PLACE_RESOURCE&&!hqs.contains(target)) {
                    if(body==null||body.type!=1||prevId!=actor||prevResource==0||prevAmount>=0||!initialWells.contains(target))unpairedPlaces++;
                    else sum(deposits,body.team,target,prevResource,window).add(rn,actor,-prevAmount);
                }
                // Require adjacent CHANGE_* event, rather than accidentally reusing an old carrier delta.
                prevId=-1;prevResource=0;prevAmount=0;
            }
            for(Sum s:sums.values())s.endRound();for(Sum s:deposits.values())s.endRound();
            for(Map.Entry<String,Long> peak:roundAmount.entrySet())if(peak.getValue()>=7) {
                String[] pk=peak.getKey().split(":");int side=Integer.parseInt(pk[0]),well=Integer.parseInt(pk[1]),resource=Integer.parseInt(pk[2]);
                roundPeaks.add("{\"round\":"+rn+",\"side\":"+q(side==1?"A":"B")+",\"well\":"+xy(well,w,ox,oy)+",\"resource\":"+q(res(resource))+",\"kg\":"+peak.getValue()+"}");
            }
            int n=r.resourceWellLocsLength();
            if(n!=initialWells.size()||n!=r.resourceIDLength()||n!=r.wellAccelerationIDLength()||n!=r.wellAdamantiumValuesLength()||n!=r.wellManaValuesLength()||n!=r.wellElixirValuesLength())throw new IOException("wellvectorlength mismatch");
            for(int j=0;j<n;j++) {
                int well=r.resourceWellLocs(j);int[] now={r.resourceID(j),r.wellAccelerationID(j),r.wellAdamantiumValues(j),r.wellManaValues(j),r.wellElixirValues(j)};
                int[] before=previousWells.get(well);if(before==null)throw new IOException("round well absent from initial map");
                if(now[1]<before[1])throw new IOException("upgradeflag regressed");
                if(now[0]!=before[0]||now[1]!=before[1])changes.add(wellRow(rn,well,now,w,ox,oy));
                for(int c:CHECKPOINTS)if(rn==c)snapshots.add(wellRow(rn,well,now,w,ox,oy));
                previousWells.put(well,now);
            }
        }
        if(roundsWalked==0)throw new IOException("noForestgame4 rounds");
        out.println("{\"match\":"+match+",\"game\":4,\"map\":"+q(map)+",\"games_run\":0,\"rounds_walked\":"+roundsWalked
            +",\"width\":"+w+",\"height\":"+h+",\"origin\":["+ox+","+oy+"],\"initial_HQ_count\":{\"A\":"+hqCounts[1]+",\"B\":"+hqCounts[2]+"}"
            +",\"unpaired_pickup_actions\":"+unpairedPickups+",\"unpaired_well_place_actions\":"+unpairedPlaces+",\"zero_amount_pickup_actions\":"+zeroPickups
            +",\"max_round\":"+maxRound+",\"paired_pickup_actions\":"+paired[0]+",\"paired_kg\":["+totals[1]+","+totals[2]+","+totals[3]+"],\"pickups\":"+sumRows(sums,w,ox,oy,maxRound)
            +",\"well_deposits\":"+sumRows(deposits,w,ox,oy,maxRound)+",\"well_changes\":["+String.join(",",changes)+"],\"well_snapshots\":["+String.join(",",snapshots)
            +"],\"round_well_kg_ge7\":["+String.join(",",roundPeaks)+"],\"limits\":[\"Pickup kg/resource comes from adjacent same-actor CHANGE then PICK_UP event; unpaired events remain unknown.\",\"Per-round well fields are end-of-round; a transition round does not timestamp upgrade relative to pickups. Amount>=2 proves that pickup used upgraded rate.\",\"Trip or end-round position does not reveal pickup-time standing square or exact cooldown modifiers.\"]}");
    }
    static String wellRow(int round,int well,int[] now,int w,int ox,int oy) {
        return "{\"round\":"+round+",\"well\":"+xy(well,w,ox,oy)+",\"resource\":"+q(res(now[0]))+",\"upgraded\":"+(now[1]==1)
            +",\"cumulative_deposits\":{\"Ad\":"+now[2]+",\"Mn\":"+now[3]+",\"Ex\":"+now[4]+"}}";
    }
    static String sumRows(Map<String,Sum> sums,int w,int ox,int oy,int maxRound) {
        List<String> rows=new ArrayList<>();for(Sum s:sums.values()) {
            int[] win=WINDOWS[s.window];rows.add("{\"side\":"+q(s.side==1?"A":s.side==2?"B":"?")+",\"well\":"+xy(s.well,w,ox,oy)+",\"resource\":"+q(res(s.resource))
                +",\"start\":"+win[0]+",\"end\":"+win[1]+",\"observed_end_round\":"+Math.min(win[1],maxRound)+",\"kg\":"+s.amount+",\"kg_per_round\":"+((double)s.amount/(Math.min(win[1],maxRound)-win[0]+1))
                +",\"pickup_or_deposit_actions\":"+s.actions+",\"distinct_carriers\":"+s.carriers.size()+",\"first_action\":"+s.first+",\"last_action\":"+s.last
                +",\"max_action_amount\":"+s.maxAmount+",\"carrier_turns_with_multiple_actions\":"+s.multiTurns+",\"max_actions_same_carrier_turn\":"+s.maxActionsPerTurn+"}");
        }return "["+String.join(",",rows)+"]";
    }
    static int fixtureRound(FlatBufferBuilder b,int rn,int[] ids,byte[] actions,int[] targets,int[] types,int[] upgrades,int[] ad,int[] mn) {
        int ai=Round.createActionIDsVector(b,ids),aa=Round.createActionsVector(b,actions),at=Round.createActionTargetsVector(b,targets);
        int wells=Round.createResourceWellLocsVector(b,new int[]{37,38}),resources=Round.createResourceIDVector(b,types),acc=Round.createWellAccelerationIDVector(b,upgrades);
        int wa=Round.createWellAdamantiumValuesVector(b,ad),wm=Round.createWellManaValuesVector(b,mn),we=Round.createWellElixirValuesVector(b,new int[]{0,0});
        Round.startRound(b);Round.addRoundID(b,rn);Round.addActionIDs(b,ai);Round.addActions(b,aa);Round.addActionTargets(b,at);
        Round.addResourceWellLocs(b,wells);Round.addResourceID(b,resources);Round.addWellAccelerationID(b,acc);
        Round.addWellAdamantiumValues(b,wa);Round.addWellManaValues(b,wm);Round.addWellElixirValues(b,we);
        return EventWrapper.createEventWrapper(b,Event.Round,Round.endRound(b));
    }
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    static void selftest()throws Exception {
        // Serialization fixtures exercise pairing and field interpretation, not game legality.
        FlatBufferBuilder b=new FlatBufferBuilder(8192);
        int xx=VecTable.createXsVector(b,new int[]{107,108,102}),yy=VecTable.createYsVector(b,new int[]{203,203,202});
        int locs=VecTable.createVecTable(b,xx,yy);
        int bodies=SpawnedBodyTable.createSpawnedBodyTable(b,SpawnedBodyTable.createRobotIDsVector(b,new int[]{17,18,19}),
            SpawnedBodyTable.createTeamIDsVector(b,new byte[]{1,2,1}),SpawnedBodyTable.createTypesVector(b,new byte[]{1,1,0}),locs);
        int[] resources=new int[100];resources[37]=2;resources[38]=1;int rv=GameMap.createResourcesVector(b,resources),name=b.createString("Forest");
        GameMap.startGameMap(b);GameMap.addName(b,name);GameMap.addBodies(b,bodies);GameMap.addResources(b,rv);
        GameMap.addMinCorner(b,Vec.createVec(b,100,200));GameMap.addMaxCorner(b,Vec.createVec(b,110,210));int map=GameMap.endGameMap(b);
        int[] events=new int[9];for(int i=0;i<5;i++)events[i]=EventWrapper.createEventWrapper(b,Event.MatchHeader,MatchHeader.createMatchHeader(b,map,2000));
        events[5]=fixtureRound(b,1,new int[]{17,17,17,17,17,17,17,17,17,17,18,18,18,18,18,19,19},
            new byte[]{Action.CHANGE_MANA,Action.PICK_UP_RESOURCE,Action.CHANGE_MANA,Action.THROW_ATTACK,Action.CHANGE_MANA,Action.PLACE_RESOURCE,
                Action.CHANGE_ADAMANTIUM,Action.PICK_UP_RESOURCE,Action.CHANGE_ADAMANTIUM,Action.PLACE_RESOURCE,Action.CHANGE_MANA,Action.PICK_UP_RESOURCE,
                Action.CHANGE_MANA,Action.CHANGE_HEALTH,Action.PICK_UP_RESOURCE,Action.CHANGE_MANA,Action.SPAWN_UNIT},
            new int[]{1,37,-1,-1,2,22,3,38,-40,38,0,37,1,-5,37,-45,23},new int[]{2,1},new int[]{0,1},new int[]{0,1400},new int[]{0,0});
        events[6]=fixtureRound(b,2,new int[]{17,17,17,17,18,18},
            new byte[]{Action.CHANGE_MANA,Action.PICK_UP_RESOURCE,Action.CHANGE_MANA,Action.PICK_UP_RESOURCE,Action.CHANGE_MANA,Action.PLACE_RESOURCE},
            new int[]{3,37,2,37,-40,37},new int[]{2,1},new int[]{1,1},new int[]{0,1400},new int[]{1400,0});
        events[7]=fixtureRound(b,100,new int[]{},new byte[]{},new int[]{},new int[]{2,1},new int[]{1,1},new int[]{0,1400},new int[]{1400,0});
        events[8]=fixtureRound(b,250,new int[]{18,18},new byte[]{Action.CHANGE_ELIXIR,Action.PICK_UP_RESOURCE},new int[]{3,37},
            new int[]{3,1},new int[]{1,1},new int[]{600,1400},new int[]{1400,0});
        int ev=GameWrapper.createEventsVector(b,events);GameWrapper.startGameWrapper(b);GameWrapper.addEvents(b,ev);b.finish(GameWrapper.endGameWrapper(b));
        File fixture=File.createTempFile("forest-actions-fixture-",".bc23");
        try {
            try(OutputStream output=new GZIPOutputStream(new FileOutputStream(fixture))){output.write(b.sizedByteArray());}
            ByteArrayOutputStream result=new ByteArrayOutputStream();read(fixture.toString(),0,new PrintStream(result));String text=result.toString("UTF-8");
            check(text.contains("\"origin\":[100,200]")&&text.contains("\"well\":[107,203]"),"header coordinate translation");
            check(text.contains("\"initial_HQ_count\":{\"A\":1,\"B\":0}"),"initialHQ metadata");
            check(text.contains("\"paired_kg\":[3,6,3]"),"noncollection inventory changes excluded; actual resource uses CHANGE rather than header");
            check(text.contains("\"unpaired_pickup_actions\":1")&&text.contains("\"zero_amount_pickup_actions\":1"),"stale pairing rejected and zero pickups counted");
            check(text.contains("\"carrier_turns_with_multiple_actions\":1")&&text.contains("\"max_actions_same_carrier_turn\":2"),"same-carrier multi-action turns");
            check(text.contains("\"well\":[107,203],\"resource\":\"Mn\",\"start\":1,\"end\":100,\"observed_end_round\":100,\"kg\":40"),"signed well deposit positive40");
            check(text.contains("\"round\":2,\"well\":[107,203],\"resource\":\"Mn\",\"upgraded\":true"),"upgrade transition");
            check(text.contains("\"round\":250,\"well\":[107,203],\"resource\":\"Ex\",\"upgraded\":true"),"upgrade survives resource conversion");
            check(text.contains("\"cumulative_deposits\":{\"Ad\":600,\"Mn\":1400,\"Ex\":0}"),"current well deposit snapshot fields");
            check(text.contains("\"round\":100")&&text.contains("\"max_action_amount\":3"),"checkpoint snapshots and rate3 amount");
        } finally {if(!fixture.delete())fixture.deleteOnExit();}
        System.out.println("{\"fixture_checks\":10,\"games_run\":0,\"mode\":\"serialization_fixture_passed\"}");
    }
    public static void main(String[] args)throws Exception {
        if(args.length==1&&args[0].equals("--selftest")){selftest();return;}
        if(args.length!=2)throw new IllegalArgumentException("ForestActions <existingreplay.bc23> <matchid>");
        read(args[0],Integer.parseInt(args[1]),System.out);
    }
}
