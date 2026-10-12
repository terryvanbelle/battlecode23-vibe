package replaydump;

import battlecode.schema.*;
import java.io.*;
import java.util.*;

/** Read-only host replay pass. Uses the repository's calibrated BCC decoder;
 * skips combat modeling. No bots/classes are loaded and no game is launched.
 * Positions are end-of-round, AFTER currents. Equal endpoints mean no NET
 * displacement; they do not prove there was no move during the turn. */
public final class CarrierMovementProbe extends ReplayDump {
    static final String[] COLS = {"carrier_turns", "code_unknown", "code_other", "G",
        "G_endpoint_missing", "G_net_displacement", "G_same_endpoint", "G_ABA",
        "G_initial_map_mana_distance_decreased", "G_initial_map_mana_distance_increased", "G_initial_map_mana_distance_equal",
        "G_nearest_initial_map_mana_d2_le2", "G_nearest_initial_map_mana_d2_3to8",
        "G_nearest_initial_map_mana_d2_9to20", "G_nearest_initial_map_mana_d2_21to50", "G_nearest_initial_map_mana_d2_gt50",
        "G_no_adjacent_empty_passable_tile_at_end", "G_actual_collect_actions"};
    final long[][] counts = new long[4][COLS.length];
    final Map<Integer, Episode> active = new HashMap<>();
    final List<Episode> episodes = new ArrayList<>();
    final Map<Integer, Point> hotspots = new HashMap<>();
    final Map<Integer, Integer> firstCollections = new HashMap<>();
    final Map<Integer, Integer> endpointStamp = new HashMap<>();
    final int match;

    static final class Episode {
        int id, r0, r1, x, y, g, other, unknown, minCargo = Integer.MAX_VALUE,
            maxCargo, minFree = 8, maxFree;
        int span() { return r1-r0+1; }
        boolean predominantlyG() { return span() >= 20 && g >= 20 && 10*g >= 9*(g+other); }
    }
    static final class Point {
        int x, y, gStill, freeSum, noFree, manaD2, anyWellD2;
    }

    CarrierMovementProbe(String file, int game, int match) throws IOException {
        super(file, game); this.match=match; deep=true;
        if(originX!=0 || originY!=0) throw new IllegalArgumentException("nonzero map origin");
    }

    // Keep only the alive list needed by the base per-round position prepass.
    @Override void microRound(Round round) {
        alive.clear();
        for(Robot rb:robots.values()) if(rb.died<0 || rb.died==round.roundID()) alive.add(rb);
    }

    static int distance(int x,int y,int x2,int y2) { int dx=x-x2,dy=y-y2; return dx*dx+dy*dy; }
    int nearestWellD2(int x,int y,int type) {
        int best=Integer.MAX_VALUE;
        for(int p=0;p<resource.length;p++) if(resource[p]>0 && (type==0 || resource[p]==type)) {
            int d=distance(x,y,p%W,p/W); if(d<best)best=d;
        }
        return best;
    }
    int emptyAdjacent(Robot rb, Set<Integer> occupied) {
        int count=0;
        for(int dx=-1;dx<=1;dx++)for(int dy=-1;dy<=1;dy++) {
            if(dx==0 && dy==0)continue;
            int x=rb.x+dx,y=rb.y+dy;
            if(x>=0 && y>=0 && x<W && y<H && !wall[x+y*W] && !occupied.contains(x+y*W))count++;
        }
        return count;
    }
    static int code(int rn,int used,int limit,int offset,boolean calibrated) {
        return calibrated && rn%50!=25 && used<=limit-BCC_GUARD ? (used-offset)&63 : -1;
    }
    void increment(int phase,int col) { counts[0][col]++;counts[phase][col]++; }
    void finishEpisode(int id) {
        Episode e=active.remove(id); if(e!=null && e.predominantlyG())episodes.add(e);
    }

    @Override void deepRound(Round round) {
        int rn=round.roundID(),phase=rn<=150?1:rn<=600?2:3;
        for(int k=0;k<round.movedIDsLength();k++)endpointStamp.put(round.movedIDs(k),rn);
        Set<Integer> occupied=new HashSet<>(),collecting=new HashSet<>();
        for(Robot rb:alive)if(rb.died<0)occupied.add(rb.x+rb.y*W);
        for(int k=0;k<round.actionsLength();k++)if(round.actions(k)==Action.PICK_UP_RESOURCE) {
            int id=round.actionIDs(k),target=round.actionTargets(k);Robot rb=robots.get(id);
            if(rb!=null && rb.team==1 && rb.type==1 && target>=0 && target<resource.length && resource[target]>0) {
                collecting.add(id);if(!firstCollections.containsKey(id))firstCollections.put(id,rn);
            }
        }
        for(int k=0;k<round.bytecodeIDsLength();k++) {
            Robot rb=robots.get(round.bytecodeIDs(k));
            if(rb==null || rb.team!=1 || rb.type!=1)continue;
            increment(phase,0);
            int c=code(rn,round.bytecodesUsed(k),lim[1],kstar[1],bccSide[1]);
            char letter=c<0?'?':letter(1,c);
            if(c<0 || letter=='?')increment(phase,1);
            else if(letter!='G')increment(phase,2);
            else increment(phase,3);
            boolean endpoint=endpointStamp.getOrDefault(rb.id,-1)==rn && rb.died<0;
            boolean same=endpoint && rb.px>=0 && rb.x==rb.px && rb.y==rb.py;
            int free=endpoint?emptyAdjacent(rb,occupied):-1;
            if(!same)finishEpisode(rb.id);
            else {
                Episode e=active.get(rb.id);
                if(e==null || e.r1!=rn-1 || e.x!=rb.x || e.y!=rb.y) {
                    finishEpisode(rb.id);e=new Episode();e.id=rb.id;e.r0=rn;e.x=rb.x;e.y=rb.y;active.put(rb.id,e);
                }
                e.r1=rn;
                if(letter=='G')e.g++;else if(c<0 || letter=='?')e.unknown++;else e.other++;
                int cargo=rb.ad+rb.mn+rb.ex;e.minCargo=Math.min(e.minCargo,cargo);e.maxCargo=Math.max(e.maxCargo,cargo);
                e.minFree=Math.min(e.minFree,free);e.maxFree=Math.max(e.maxFree,free);
            }
            if(letter!='G')continue;
            if(!endpoint) { increment(phase,4);continue; }
            if(same)increment(phase,6);else increment(phase,5);
            if(!same && rb.ppx==rb.x && rb.ppy==rb.y)increment(phase,7);
            int nearest=nearestWellD2(rb.x,rb.y,2);
            if(rb.px>=0) {
                int before=nearestWellD2(rb.px,rb.py,2);
                increment(phase,nearest<before?8:nearest>before?9:10);
            }
            increment(phase,nearest<=2?11:nearest<=8?12:nearest<=20?13:nearest<=50?14:15);
            if(free==0)increment(phase,16);
            if(collecting.contains(rb.id))increment(phase,17);
            if(same) {
                int p=rb.x+rb.y*W;Point point=hotspots.get(p);
                if(point==null) {point=new Point();point.x=rb.x;point.y=rb.y;point.manaD2=nearest;
                    point.anyWellD2=nearestWellD2(rb.x,rb.y,0);hotspots.put(p,point);}
                point.gStill++;point.freeSum+=free;if(free==0)point.noFree++;
            }
        }
        for(int k=0;k<round.diedIDsLength();k++)finishEpisode(round.diedIDs(k));
    }

    @Override void deepFinish() {
        for(int id:new ArrayList<Integer>(active.keySet()))finishEpisode(id);
    }

    Map<String,Object> result() {
        Map<String,Object> out=new LinkedHashMap<>();
        out.put("match",match);out.put("game",gameIdx);out.put("map",mapName);out.put("side","A");
        out.put("team_A",teamA);out.put("team_B",teamB);out.put("rounds",totalRounds);
        out.put("calibration",Arrays.asList(bccSide[1],kstar[1],sSync[1],nSync[1],offShare[1]));
        out.put("calibration_columns",Arrays.asList("valid_BCC","offset","sync_agreement_count","sync_turns","off_sync_same_residue_share"));
        out.put("count_columns",Arrays.asList(COLS));out.put("count_phases",Arrays.asList("all","open_r1to150","mid_r151to600","late_r601to2000"));
        List<List<Long>> countRows=new ArrayList<>();
        for(long[] row:counts) {List<Long> values=new ArrayList<>();for(long n:row)values.add(n);countRows.add(values);}
        out.put("count_rows",countRows);
        List<Point> points=new ArrayList<>(hotspots.values());
        points.sort((a,b)->Integer.compare(b.gStill,a.gStill));
        List<List<Object>> pointRows=new ArrayList<>();
        for(Point p:points.subList(0,Math.min(20,points.size())))pointRows.add(Arrays.<Object>asList(p.x,p.y,p.gStill,p.manaD2,p.anyWellD2,p.freeSum,p.noFree));
        out.put("G_same_endpoint_hotspot_columns",Arrays.asList("x","y","G_turns","nearest_initial_map_mana_d2","nearest_any_initial_map_well_d2","sum_adj_empty_passable","no_adj_empty_passable_turns"));
        out.put("G_same_endpoint_hotspots",pointRows);
        episodes.sort((a,b)->Integer.compare(b.g,a.g));
        List<List<Object>> episodeRows=new ArrayList<>();
        for(Episode e:episodes.subList(0,Math.min(30,episodes.size())))episodeRows.add(Arrays.<Object>asList(e.id,e.r0,e.r1,e.span(),e.g,e.other,e.unknown,e.x,e.y,nearestWellD2(e.x,e.y,2),nearestWellD2(e.x,e.y,0),e.minCargo,e.maxCargo,e.minFree,e.maxFree,firstCollections.get(e.id)));
        out.put("long_G_same_endpoint_episodes_total",episodes.size());
        out.put("long_G_same_endpoint_episode_columns",Arrays.asList("id","r0","r1","span_rounds","observed_G","observed_other","unknown","x","y","nearest_initial_map_mana_d2","nearest_any_initial_map_well_d2","min_resource_cargo","max_resource_cargo","min_adj_empty","max_adj_empty","first_collection_round_ever"));
        out.put("long_G_same_endpoint_episodes_top",episodeRows);
        return out;
    }

    static String json(Object o) {
        if(o==null)return"null";
        if(o instanceof Number || o instanceof Boolean)return o.toString();
        if(o instanceof String)return"\""+((String)o).replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r").replace("\t","\\t")+"\"";
        StringBuilder s=new StringBuilder();
        if(o instanceof Map) {
            s.append('{');boolean first=true;
            for(Object item:((Map<?,?>)o).entrySet()) {Map.Entry<?,?> e=(Map.Entry<?,?>)item;if(!first)s.append(',');first=false;s.append(json(e.getKey())).append(':').append(json(e.getValue()));}
            return s.append('}').toString();
        }
        if(o instanceof Iterable) {
            s.append('[');boolean first=true;for(Object item:(Iterable<?>)o){if(!first)s.append(',');first=false;s.append(json(item));}
            return s.append(']').toString();
        }
        throw new IllegalArgumentException("Cannot encode "+o.getClass());
    }

    static void selfTest() {
        if(code(25,5000,12500,14,true)!=-1)throw new AssertionError("sync must remain unknown");
        if(code(26,12500,12500,14,true)!=-1)throw new AssertionError("overrun must remain unknown");
        if(code(26,10000+14+3,12500,14,true)!=19)throw new AssertionError("BCC residue");
        if(code(26,10000,12500,14,false)!=-1)throw new AssertionError("uncalibrated unknown");
        Episode e=new Episode();e.r0=100;e.r1=129;e.g=28;e.unknown=2;
        if(!e.predominantlyG())throw new AssertionError("observed G with honest unknowns");
        e.other=10;if(e.predominantlyG())throw new AssertionError("mixed state excluded");
        e.other=0;e.g=19;if(e.predominantlyG())throw new AssertionError("too few observed G");
        if(distance(8,12,10,15)!=13)throw new AssertionError("outside crowd radius");
        System.out.println("{\"self_test\":\"passed\",\"checks\":8,\"games_run\":0}");
    }

    public static void main(String[] args)throws Exception {
        if(args.length==1 && args[0].equals("--self-test")) {selfTest();return;}
        boolean fixture=args.length==2 && args[0].equals("--fixture");
        if(!fixture && (args.length<1 || args.length>2))throw new IllegalArgumentException("one or two own field replay paths");
        List<Object> outputs=new ArrayList<>();
        for(int i=fixture?1:0;i<args.length;i++) {
            int match=fixture?0:Integer.parseInt(new File(args[i]).getName().replace(".bc23",""));
            if(!fixture && match!=4566 && match!=4570)throw new IllegalArgumentException("unapproved match");
            CarrierMovementProbe d=new CarrierMovementProbe(args[i],fixture?0:4,match);
            if(!fixture && !d.mapName.equals("Forest"))throw new IllegalArgumentException("wrong map");
            d.run(null);outputs.add(d.result());
        }
        Map<String,Object> output=new LinkedHashMap<>();output.put("games_run",0);
        output.put("semantics",Arrays.asList("No net endpoint change is observed after currents; in-turn moves are not timestamped.",
            "Nearest well locations/types are INITIAL-MAP TRUTH from MatchHeader; conversions are not reconstructed. They do not infer knowledge or actual targets.",
            "Empty adjacent tiles are end-of-round occupancy, not exact canMove legality during the actor's turn.",
            "PICK_UP_RESOURCE is counted only when its target is an initial-map well location; HQ withdrawal uses PLACE_RESOURCE in engine 3.0.15. Sync and insufficient-budget BCC turns stay unknown; no state is copied forward.",
            "Long episodes require >=20 observed G turns and >=90% G among observed states, with unknowns retained."));
        output.put("replays",outputs);System.out.println(json(output));
    }
}
