package carrierheaders;

import battlecode.schema.*;
import battlecode.world.GameMapIO;
import battlecode.world.LiveMap;
import java.io.*;
import java.nio.*;
import java.security.*;
import java.util.*;
import java.util.zip.*;

/** Headers only: no Round object, action iteration, bot loading or game run. */
public final class ForestWellGeometry {
    static final class Geometry {
        String name; int w,h,ox,oy; boolean[] wall,cloud;int[] current,resource;
    }
    static Geometry builtin()throws IOException {
        LiveMap m=GameMapIO.loadMap("Forest",new File("/nonexistent-carrier-header-map-dir"),false);
        Geometry g=new Geometry();g.name=m.getMapName();g.w=m.getWidth();g.h=m.getHeight();
        g.ox=m.getOrigin().x;g.oy=m.getOrigin().y;g.wall=m.getWallArray();g.cloud=m.getCloudArray();
        g.current=m.getCurrentArray();g.resource=m.getResourceArray();return g;
    }
    static Geometry header(String path)throws IOException {
        byte[] bytes;
        try(InputStream in=new GZIPInputStream(new FileInputStream(path));ByteArrayOutputStream out=new ByteArrayOutputStream()) {
            byte[] buffer=new byte[65536];int n;while((n=in.read(buffer))>0)out.write(buffer,0,n);bytes=out.toByteArray();
        }
        GameWrapper game=GameWrapper.getRootAsGameWrapper(ByteBuffer.wrap(bytes));int index=-1;
        for(int i=0;i<game.eventsLength();i++) {
            EventWrapper e=game.events(i);
            if(e.eType()!=Event.MatchHeader)continue;
            index++;if(index!=4)continue;
            GameMap m=((MatchHeader)e.e(new MatchHeader())).map();Geometry g=new Geometry();
            g.name=m.name();g.ox=m.minCorner().x();g.oy=m.minCorner().y();
            g.w=m.maxCorner().x()-g.ox;g.h=m.maxCorner().y()-g.oy;int size=g.w*g.h;
            g.wall=new boolean[size];g.cloud=new boolean[size];g.current=new int[size];g.resource=new int[size];
            for(int p=0;p<size;p++){g.wall[p]=m.walls(p);g.cloud[p]=m.clouds(p);g.current[p]=m.currents(p);g.resource[p]=m.resources(p);}
            return g;
        }
        throw new IOException("Forest game4 header absent");
    }
    static String digest(Geometry g)throws Exception {
        MessageDigest d=MessageDigest.getInstance("SHA-256");
        ByteBuffer b=ByteBuffer.allocate(16+g.w*g.h*10).order(ByteOrder.LITTLE_ENDIAN);
        b.putInt(g.w).putInt(g.h).putInt(g.ox).putInt(g.oy);
        for(int p=0;p<g.w*g.h;p++)b.put((byte)(g.wall[p]?1:0)).put((byte)(g.cloud[p]?1:0)).putInt(g.current[p]).putInt(g.resource[p]);
        byte[] hash=d.digest(b.array());StringBuilder s=new StringBuilder();for(byte h:hash)s.append(String.format("%02x",h&255));return s.toString();
    }
    static Map<String,Object> well(Geometry g,int x,int y) {
        List<Object> cells=new ArrayList<>();int passable=0,cloudCells=0,normalCells=0;
        for(int dx=-1;dx<=1;dx++)for(int dy=-1;dy<=1;dy++) {
            int xx=x+dx,yy=y+dy;if(xx<0 || yy<0 || xx>=g.w || yy>=g.h)continue;
            int p=xx+yy*g.w;if(g.wall[p])continue;
            passable++;if(g.cloud[p])cloudCells++;else normalCells++;
            cells.add(Arrays.<Object>asList(xx,yy,g.cloud[p],g.current[p],g.cloud[p]?12:10));
        }
        Map<String,Object> out=new LinkedHashMap<>();out.put("initial_mana_well",Arrays.asList(x+g.ox,y+g.oy));
        out.put("passable_adjacency_cells_including_well_square",passable);out.put("cloud_cells",cloudCells);
        out.put("normal_cells",normalCells);out.put("cells_columns",Arrays.asList("x","y","cloud","raw_current_code","baseline_collect_cooldown"));
        out.put("cells",cells);
        out.put("resident_rate1_stationary_staffing_benchmark_kg_per_round_num_over6",6*normalCells+5*cloudCells);
        out.put("resident_rate1_stationary_staffing_benchmark_kg_per_round",normalCells+5.0*cloudCells/6.0);
        out.put("rate1_no_boost_no_midturn_vacancy_footprint_reference_upper_kg_per_round",passable);
        out.put("rate3_no_boost_no_midturn_vacancy_footprint_reference_upper_kg_per_round",3*passable);
        return out;
    }
    static Map<String,Object> describe(Geometry g,String source,String builtinHash)throws Exception {
        if(!"Forest".equals(g.name))throw new IllegalArgumentException("unexpected map "+g.name);
        Map<String,Object> out=new LinkedHashMap<>();String hash=digest(g);
        out.put("source",source);out.put("name",g.name);out.put("size",Arrays.asList(g.w,g.h));out.put("origin",Arrays.asList(g.ox,g.oy));
        out.put("terrain_geometry_sha256",hash);out.put("equals_official_builtin_terrain_geometry",hash.equals(builtinHash));
        List<Object> wells=new ArrayList<>();for(int p=0;p<g.resource.length;p++)if(g.resource[p]==2)wells.add(well(g,p%g.w,p/g.w));
        out.put("initial_mana_wells",wells);
        List<Object> patch=new ArrayList<>();
        for(int y=17;y<=23;y++)for(int x=3;x<=10;x++) {
            int p=x+y*g.w;patch.add(Arrays.<Object>asList(x,y,g.wall[p],g.cloud[p],g.current[p],g.resource[p]));
        }
        out.put("stall_neighbourhood_columns",Arrays.asList("x","y","wall","cloud","raw_current_code","initial_resource"));
        out.put("stall_neighbourhood",patch);
        List<Object> union=new ArrayList<>();Set<Integer> unique=new HashSet<>();int centreCloud=0;
        for(int p=0;p<g.resource.length;p++)if(g.resource[p]==2 && p/g.w==48 && (p%g.w==29 || p%g.w==30)) {
            int x=p%g.w,y=p/g.w;
            for(int dx=-1;dx<=1;dx++)for(int dy=-1;dy<=1;dy++) {
                int xx=x+dx,yy=y+dy,q=xx+yy*g.w;
                if(xx<0 || yy<0 || xx>=g.w || yy>=g.h || g.wall[q] || !unique.add(q))continue;
                if(g.cloud[q])centreCloud++;union.add(Arrays.<Object>asList(xx,yy,g.cloud[q],g.current[q]));
            }
        }
        out.put("centre_pair_distinct_collection_cells",union);
        out.put("centre_pair_resident_rate1_stationary_staffing_benchmark_kg_per_round",unique.size()-centreCloud/6.0);
        return out;
    }
    static String json(Object o) {
        if(o==null)return"null";if(o instanceof Number || o instanceof Boolean)return o.toString();
        if(o instanceof String)return"\""+((String)o).replace("\\","\\\\").replace("\"","\\\"")+"\"";
        StringBuilder s=new StringBuilder();boolean first=true;
        if(o instanceof Map){s.append('{');for(Map.Entry<?,?> e:((Map<?,?>)o).entrySet()){if(!first)s.append(',');first=false;s.append(json(e.getKey())).append(':').append(json(e.getValue()));}return s.append('}').toString();}
        if(o instanceof Iterable){s.append('[');for(Object v:(Iterable<?>)o){if(!first)s.append(',');first=false;s.append(json(v));}return s.append(']').toString();}
        throw new IllegalArgumentException("JSON type "+o.getClass());
    }
    static void selfTest() {
        Geometry g=new Geometry();g.w=3;g.h=3;g.wall=new boolean[9];g.cloud=new boolean[9];g.current=new int[9];g.resource=new int[9];
        g.wall[0]=true;g.cloud[1]=true;Map<String,Object> m=well(g,1,1);
        if(!m.get("passable_adjacency_cells_including_well_square").equals(8))throw new AssertionError("walls excluded");
        if(!m.get("cloud_cells").equals(1))throw new AssertionError("cloud costs");
        if(!m.get("resident_rate1_stationary_staffing_benchmark_kg_per_round_num_over6").equals(47))throw new AssertionError("7+5/6 staffing");
        if(!well(g,0,0).get("passable_adjacency_cells_including_well_square").equals(3))throw new AssertionError("offmap excluded");
    }
    public static void main(String[] args)throws Exception {
        selfTest();Geometry built=builtin();String builtinHash=digest(built);List<Object> maps=new ArrayList<>();
        maps.add(describe(built,"official_engine_builtin_Forest",builtinHash));
        if(args.length>2)throw new IllegalArgumentException("maximum two existing replay headers");
        for(String path:args){String name=new File(path).getName();if(!name.equals("4566.bc23") && !name.equals("4570.bc23"))throw new IllegalArgumentException("unapproved replay");maps.add(describe(header(path),path+":game4_MatchHeader",builtinHash));}
        Map<String,Object> out=new LinkedHashMap<>();out.put("games_run",0);out.put("rounds_walked",0);out.put("checks",4);
        out.put("semantics",Arrays.asList("Initial map geometry and resource types, never bot knowledge or reconstructed current well upgrades/conversions.",
            "Resident rate1 staffing benchmark sums 10/collectCooldown over passable collecting cells, assuming uninterrupted resident collectors, no boosts or accelerating anchors, and standard rate1 wells.",
            "Footprint reference upper rates assume no same-round vacancy reuse: our gather leaves a collector in place until its next turn; mid-round deaths can permit additional collectors. Currents can reduce attainable staffing.",
            "These are conditional geometric benchmarks, not unconditional resource throughput limits; upgrades, aura effects, actor order, duty turnover and vacancy reuse require separate verification.",
            "Terrain SHA includes width/height/origin and wall/cloud/current/initial-resource fields; excludes bodies, seed and island IDs."));
        out.put("maps",maps);System.out.println(json(out));
    }
}
