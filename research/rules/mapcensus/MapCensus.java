import battlecode.common.Direction;
import battlecode.common.GameConstants;
import battlecode.common.MapLocation;
import battlecode.common.RobotInfo;
import battlecode.common.RobotType;
import battlecode.common.Team;
import battlecode.server.Config;
import battlecode.server.Server;
import battlecode.world.GameMapIO;
import battlecode.world.LiveMap;
import battlecode.world.MapBuilder;
import battlecode.world.MapSymmetry;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.PrintStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Battlecode 2023 map census.
 *
 * Loads every .map23 shipped inside the engine jar (battlecode/world/resources/) through the engine's own loader
 * (GameMapIO.getAvailableMaps + GameMapIO.loadMapAsResource) and prints one TSV row per map.
 *
 * Also runs, per map:
 *  - the engine's run-time validator Server.validateMapOnGuarantees (private; called by reflection), which is what
 *    the server executes before every match when bc.server.validate-maps=true (the default);
 *  - the Java map-builder's symmetry test MapBuilder.getSymmetry (private; by reflection) after copying the map into
 *    a MapBuilder. That test uses the builder's own conventions (island id -> W*H-id, current -> opposite()).
 *
 * Our own symmetry test (column sym_all) uses the geometric definition shared by MapBuilder.symmetricX/Y and the
 * client map editor (forms/symmetry.ts transformLocStatic):
 *   ROT  (x,y) -> (W-1-x, H-1-y)
 *   HORI (x,y) -> (x,     H-1-y)   ("HORIZONTAL": mirror across a horizontal line, y flips)
 *   VERT (x,y) -> (W-1-x, y    )   ("VERTICAL":   mirror across a vertical line,   x flips)
 * with currents transformed geometrically (ROT negates dx,dy; HORI negates dy; VERT negates dx), islands compared
 * as a partition (the tile set of every island must map onto the tile set of exactly one island, ids may differ),
 * and HQs required to map onto an HQ of the other team.
 *
 * Appended columns (v2): whether the symmetry stored in the map file is actually consistent; HQs standing on clouds
 * (their vision collapses to radius^2 4); currents whose end tile holds an HQ or another current; the number of
 * islands a team must hold to win by conquest; and, per team, which symmetries survive (a) own HQ positions only and
 * (b) everything the team's HQs can sense on round 1 (see deduce()); distinct islands that touch diagonally; the
 * fewest tiles any HQ can spawn onto (action radius^2 9, but the tile must also be sensable, so radius^2 4 when the
 * HQ or the tile is a cloud); and king-move reachability from each team's spawn tiles (passable tiles reached by
 * neither / only one team; wells with no reachable adjacent tile; islands with no reachable tile).
 *
 * Column semantics worth knowing: hqAB_min_dist2 / hqAB_min_cheb are between the closest A-B HQ pair;
 * hqAB_path_steps is a king-move BFS from all A HQs to the first B HQ through non-wall, non-HQ tiles (currents and
 * clouds ignored); worst_hq_nearest_*_dist2 is the max over HQs of the dist^2 to that HQ's nearest well of the type;
 * hqs_with_*_in_vision34 counts HQs with such a well within the HQ vision radius^2 (34).
 *
 * Usage: java -Xmx300m -cp classes:battlecode23-3.0.15.jar MapCensus [clientConstants.ts]
 */
public class MapCensus {

    static final String[] SYM_NAMES = {"ROT", "HORI", "VERT"};
    static final MapSymmetry[] SYMS = {MapSymmetry.ROTATIONAL, MapSymmetry.HORIZONTAL, MapSymmetry.VERTICAL};

    static int W, H;

    static int sx(int s, int x) { return (s == 1) ? x : W - 1 - x; }        // HORI keeps x
    static int sy(int s, int y) { return (s == 2) ? y : H - 1 - y; }        // VERT keeps y

    static int idx(int x, int y) { return x + y * W; }

    static Direction mirrorDir(int s, Direction d) {
        int dx = d.dx, dy = d.dy;
        if (s == 0) { dx = -dx; dy = -dy; }
        else if (s == 1) { dy = -dy; }
        else { dx = -dx; }
        for (Direction c : Direction.values()) if (c.dx == dx && c.dy == dy) return c;
        throw new IllegalStateException();
    }

    static String symSet(boolean[] ok) {
        StringBuilder sb = new StringBuilder();
        for (int s = 0; s < 3; s++) if (ok[s]) { if (sb.length() > 0) sb.append('+'); sb.append(SYM_NAMES[s]); }
        return sb.length() == 0 ? "NONE" : sb.toString();
    }

    public static void main(String[] args) throws Exception {
        // tournament labels from the client's SERVER_MAPS table (client/visualizer/src/constants.ts)
        Map<String, String> tournament = new HashMap<>();
        if (args.length > 0 && new File(args[0]).exists()) {
            String src = new String(Files.readAllBytes(new File(args[0]).toPath()), StandardCharsets.UTF_8);
            Matcher mm = Pattern.compile("\\[\"(\\w+)\",\\s*MapType\\.(\\w+)\\]").matcher(src);
            while (mm.find()) tournament.put(mm.group(1), mm.group(2));
        }

        Server server = new Server(new Config(new String[0]), false);
        Method validate = Server.class.getDeclaredMethod("validateMapOnGuarantees", LiveMap.class);
        validate.setAccessible(true);
        Method builderGetSym = MapBuilder.class.getDeclaredMethod("getSymmetry", RobotInfo[].class);
        builderGetSym.setAccessible(true);

        List<String> names = GameMapIO.getAvailableMaps(null);   // built-in maps only (mapDir == null)
        PrintStream out = System.out;

        String[] cols = {"map", "tournament", "width", "height", "area", "origin", "seed",
                "declared_sym", "sym_all", "sym_terrain", "sym_walls_only", "sym_clouds", "sym_currents_geometric", "sym_currents_opposite", "sym_wells",
                "sym_islands", "sym_hqs", "builder_getSymmetry", "builder_getSymmetry_no_islands", "builder_assertIsValid",
                "server_validator",
                "hq_A", "hq_B", "hq_ids_exec_order",
                "wells_AD", "wells_MN", "wells_EX", "wells_cap_per_type",
                "islands", "island_area_total", "island_min", "island_max", "island_id_min", "island_id_max",
                "island_ids_1_to_N", "islands_4conn",
                "pct_impassable", "pct_cloud", "pct_current",
                "hq_on_island", "well_on_island", "cloud_on_island", "current_on_island", "well_on_cloud",
                "hqAB_min_dist2", "hqAB_min_cheb", "hqAB_path_steps",
                "worst_hq_nearest_AD_dist2", "worst_hq_nearest_MN_dist2", "hqs_with_AD_in_vision34",
                "hqs_with_MN_in_vision34", "hq_on_edge",
                // appended (v2)
                "declared_sym_consistent", "hq_on_cloud", "currents_into_hq", "currents_into_current",
                "islands_needed_to_win", "syms_left_ownHQs_A", "syms_left_ownHQs_B",
                "syms_left_round1_A", "syms_left_round1_B", "distinct_islands_touch_diag",
                "min_spawn_tiles_per_hq", "passable_tiles_reached_by_neither", "passable_tiles_reached_by_one_team_only", "unreachable_wells", "unreachable_islands"};
        out.println(String.join("\t", cols));

        for (String name : names) {
            LiveMap m = GameMapIO.loadMapAsResource(GameMapIO.class.getClassLoader(),
                    GameMapIO.DEFAULT_MAP_PACKAGE, name, false);
            W = m.getWidth();
            H = m.getHeight();
            int N = W * H;
            boolean[] wall = m.getWallArray();
            boolean[] cloud = m.getCloudArray();
            int[] cur = m.getCurrentArray();
            int[] isl = m.getIslandArray();
            int[] res = m.getResourceArray();
            RobotInfo[] bodies = m.getInitialBodies();   // sorted by ID == spawn == execution order

            // ---- HQs
            RobotInfo[] hqAt = new RobotInfo[N];
            int hqA = 0, hqB = 0;
            StringBuilder order = new StringBuilder();
            for (RobotInfo r : bodies) {
                if (r.type != RobotType.HEADQUARTERS) throw new IllegalStateException("non-HQ body in " + name);
                hqAt[idx(r.location.x - m.getOrigin().x, r.location.y - m.getOrigin().y)] = r;
                if (r.team == Team.A) hqA++; else if (r.team == Team.B) hqB++;
                if (order.length() > 0) order.append(',');
                order.append(r.team).append(r.ID);
            }

            // ---- symmetry (own, geometric)
            boolean[] okWalls = {true, true, true};
            boolean[] okTerrain = {true, true, true};     // walls + clouds + currents
            boolean[] okAll = {true, true, true};         // + wells + islands + HQs
            // per-feature consistency
            boolean[] fCloud = {true, true, true}, fCur = {true, true, true}, fCurOpp = {true, true, true},
                    fWell = {true, true, true}, fIsl = {true, true, true}, fHq = {true, true, true};
            for (int s = 0; s < 3; s++) {
                Map<Integer, Integer> islMap = new HashMap<>();
                for (int x = 0; x < W; x++) for (int y = 0; y < H; y++) {
                    int i = idx(x, y), j = idx(sx(s, x), sy(s, y));
                    if (wall[i] != wall[j]) { okWalls[s] = false; okTerrain[s] = false; okAll[s] = false; }
                    if (cloud[i] != cloud[j]) { fCloud[s] = false; okTerrain[s] = false; okAll[s] = false; }
                    Direction di = Direction.DIRECTION_ORDER[cur[i]];
                    Direction dj = Direction.DIRECTION_ORDER[cur[j]];
                    if (mirrorDir(s, di) != dj) { fCur[s] = false; okTerrain[s] = false; okAll[s] = false; }
                    if (di.opposite() != dj) fCurOpp[s] = false;
                    if (res[i] != res[j]) { fWell[s] = false; okAll[s] = false; }
                    if ((isl[i] == 0) != (isl[j] == 0)) { fIsl[s] = false; okAll[s] = false; }
                    else if (isl[i] != 0) {
                        Integer prev = islMap.putIfAbsent(isl[i], isl[j]);
                        if (prev != null && prev != isl[j]) { fIsl[s] = false; okAll[s] = false; }
                    }
                    RobotInfo a = hqAt[i], b = hqAt[j];
                    if ((a == null) != (b == null)) { fHq[s] = false; okAll[s] = false; }
                    else if (a != null && a.team == b.team) { fHq[s] = false; okAll[s] = false; }
                }
                // island map must be injective too
                if (new HashSet<>(islMap.values()).size() != islMap.size()) { fIsl[s] = false; okAll[s] = false; }
            }

            // ---- builder's own symmetry test and full builder validation
            MapBuilder mb = new MapBuilder(name, W, H, 0, 0, m.getSeed());
            RobotInfo[] robotsArr = new RobotInfo[N];
            for (int x = 0; x < W; x++) for (int y = 0; y < H; y++) {
                int i = idx(x, y);
                mb.setWall(x, y, wall[i]);
                mb.setCloud(x, y, cloud[i]);
                mb.setCurrent(x, y, cur[i]);
                mb.setIsland(x, y, isl[i]);
                mb.setResource(x, y, res[i]);
            }
            for (RobotInfo r : bodies) {
                mb.addHeadquarter(r.ID, r.team, r.location);
                robotsArr[idx(r.location.x, r.location.y)] = r;
            }
            mb.setSymmetry(m.getSymmetry());
            @SuppressWarnings("unchecked")
            List<MapSymmetry> bsyms = (List<MapSymmetry>) builderGetSym.invoke(mb, (Object) robotsArr);
            boolean[] okBuilder = new boolean[3];
            for (int s = 0; s < 3; s++) okBuilder[s] = bsyms.contains(SYMS[s]);
            MapBuilder mb2 = new MapBuilder(name, W, H, 0, 0, m.getSeed());
            for (int x = 0; x < W; x++) for (int y = 0; y < H; y++) {
                int i = idx(x, y);
                mb2.setWall(x, y, wall[i]);
                mb2.setCloud(x, y, cloud[i]);
                mb2.setCurrent(x, y, cur[i]);
                mb2.setResource(x, y, res[i]);
            }
            for (RobotInfo r : bodies) mb2.addHeadquarter(r.ID, r.team, r.location);
            @SuppressWarnings("unchecked")
            List<MapSymmetry> bsyms2 = (List<MapSymmetry>) builderGetSym.invoke(mb2, (Object) robotsArr);
            boolean[] okBuilder2 = new boolean[3];
            for (int s = 0; s < 3; s++) okBuilder2[s] = bsyms2.contains(SYMS[s]);
            String builderValid;
            PrintStream saved = System.out;
            System.setOut(new PrintStream(new ByteArrayOutputStream()));
            try { mb.assertIsValid(); builderValid = "PASS"; }
            catch (RuntimeException e) { builderValid = "FAIL:" + e.getMessage(); }
            finally { System.setOut(saved); }

            // ---- server run-time validator
            String serverValid;
            try { validate.invoke(server, m); serverValid = "PASS"; }
            catch (InvocationTargetException e) { serverValid = "FAIL:" + e.getCause().getMessage(); }

            // ---- wells
            int[] wellCount = new int[4];
            for (int i = 0; i < N; i++) wellCount[res[i]]++;
            int cap = (int) (N * GameConstants.MAX_MAP_PERCENT_WELLS);

            // ---- islands
            TreeMap<Integer, List<Integer>> islands = new TreeMap<>();
            for (int i = 0; i < N; i++) if (isl[i] != 0) islands.computeIfAbsent(isl[i], k -> new ArrayList<>()).add(i);
            int islTotal = 0, islMin = Integer.MAX_VALUE, islMax = 0;
            boolean all4conn = true;
            for (Map.Entry<Integer, List<Integer>> e : islands.entrySet()) {
                int sz = e.getValue().size();
                islTotal += sz; islMin = Math.min(islMin, sz); islMax = Math.max(islMax, sz);
                // 4-connected flood from the first tile
                Set<Integer> seen = new HashSet<>();
                Deque<Integer> dq = new ArrayDeque<>();
                dq.add(e.getValue().get(0)); seen.add(e.getValue().get(0));
                while (!dq.isEmpty()) {
                    int c = dq.poll(); int cx = c % W, cy = c / W;
                    int[][] nb = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
                    for (int[] d : nb) {
                        int nx = cx + d[0], ny = cy + d[1];
                        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
                        int ni = idx(nx, ny);
                        if (isl[ni] == e.getKey() && seen.add(ni)) dq.add(ni);
                    }
                }
                if (seen.size() != sz) all4conn = false;
            }
            boolean contiguousIds = islands.isEmpty() ||
                    (islands.firstKey() == 1 && islands.lastKey() == islands.size());

            // ---- tile percentages and overlaps
            int nWall = 0, nCloud = 0, nCur = 0, hqOnIsl = 0, wellOnIsl = 0, cloudOnIsl = 0, curOnIsl = 0, wellOnCloud = 0;
            for (int i = 0; i < N; i++) {
                if (wall[i]) nWall++;
                if (cloud[i]) nCloud++;
                if (cur[i] != 0) nCur++;
                if (isl[i] != 0) {
                    if (hqAt[i] != null) hqOnIsl++;
                    if (res[i] != 0) wellOnIsl++;
                    if (cloud[i]) cloudOnIsl++;
                    if (cur[i] != 0) curOnIsl++;
                }
                if (res[i] != 0 && cloud[i]) wellOnCloud++;
            }

            // ---- HQ distances
            int minD2 = Integer.MAX_VALUE, minCheb = Integer.MAX_VALUE;
            for (RobotInfo a : bodies) for (RobotInfo b : bodies) {
                if (a.team == b.team) continue;
                minD2 = Math.min(minD2, a.location.distanceSquaredTo(b.location));
                minCheb = Math.min(minCheb, Math.max(Math.abs(a.location.x - b.location.x),
                        Math.abs(a.location.y - b.location.y)));
            }
            // BFS (king moves) from all A HQs through non-wall, non-HQ tiles; stepping onto a B HQ ends a path.
            int[] dist = new int[N];
            Arrays.fill(dist, -1);
            Deque<Integer> q = new ArrayDeque<>();
            for (RobotInfo r : bodies) if (r.team == Team.A) { int i = idx(r.location.x, r.location.y); dist[i] = 0; q.add(i); }
            int pathSteps = -1;
            while (!q.isEmpty() && pathSteps < 0) {
                int c = q.poll(); int cx = c % W, cy = c / W;
                for (int dx = -1; dx <= 1 && pathSteps < 0; dx++) for (int dy = -1; dy <= 1; dy++) {
                    if (dx == 0 && dy == 0) continue;
                    int nx = cx + dx, ny = cy + dy;
                    if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
                    int ni = idx(nx, ny);
                    if (dist[ni] >= 0 || wall[ni]) continue;
                    if (hqAt[ni] != null) {
                        if (hqAt[ni].team == Team.B) { pathSteps = dist[c] + 1; break; }
                        continue;
                    }
                    dist[ni] = dist[c] + 1;
                    q.add(ni);
                }
            }

            // ---- nearest wells per HQ
            int worstAD = 0, worstMN = 0, adVis = 0, mnVis = 0, onEdge = 0;
            int vision = RobotType.HEADQUARTERS.visionRadiusSquared;
            for (RobotInfo r : bodies) {
                int bestAD = Integer.MAX_VALUE, bestMN = Integer.MAX_VALUE;
                for (int i = 0; i < N; i++) {
                    if (res[i] == 0) continue;
                    int d2 = r.location.distanceSquaredTo(new MapLocation(i % W, i / W));
                    if (res[i] == 1) bestAD = Math.min(bestAD, d2);
                    if (res[i] == 2) bestMN = Math.min(bestMN, d2);
                }
                worstAD = Math.max(worstAD, bestAD);
                worstMN = Math.max(worstMN, bestMN);
                if (bestAD <= vision) adVis++;
                if (bestMN <= vision) mnVis++;
                int x = r.location.x, y = r.location.y;
                if (x == 0 || y == 0 || x == W - 1 || y == H - 1) onEdge++;
            }

            // ---- v2 extras
            int declaredIdx = Arrays.asList(SYMS).indexOf(m.getSymmetry());
            boolean declaredOk = okAll[declaredIdx];
            int hqOnCloud = 0, curIntoHq = 0, curIntoCur = 0;
            for (RobotInfo r : bodies) if (cloud[idx(r.location.x, r.location.y)]) hqOnCloud++;
            for (int i = 0; i < N; i++) {
                if (cur[i] == 0) continue;
                Direction d = Direction.DIRECTION_ORDER[cur[i]];
                int ex = i % W + d.dx, ey = i / W + d.dy;      // validator guarantees on-map, non-wall
                int e = idx(ex, ey);
                if (hqAt[e] != null) curIntoHq++;
                if (cur[e] != 0) curIntoCur++;
            }
            // smallest k with (float)k/N >= 0.75f, as TeamInfo.placeAnchor tests it
            int nIsl = islands.size(), need = 0;
            while (((float) need) / nIsl < GameConstants.WIN_PERCENTAGE_OF_ISLANDS_OCCUPIED) need++;
            // distinct islands that touch only diagonally (4-adjacency between distinct islands never occurs)
            int islDiag = 0;
            for (int i = 0; i < N; i++) {
                if (isl[i] == 0) continue;
                int x = i % W, y = i / W;
                for (int[] d : new int[][]{{1, 1}, {1, -1}}) {
                    int nx = x + d[0], ny = y + d[1];
                    if (nx >= W || ny < 0 || ny >= H) continue;
                    int j = idx(nx, ny);
                    if (isl[j] != 0 && isl[j] != isl[i]) islDiag++;
                }
                for (int[] d : new int[][]{{1, 0}, {0, 1}}) {
                    int nx = x + d[0], ny = y + d[1];
                    if (nx >= W || ny >= H) continue;
                    int j = idx(nx, ny);
                    if (isl[j] != 0 && isl[j] != isl[i]) throw new IllegalStateException("distinct islands 4-adjacent in " + name);
                }
            }
            // spawnable tiles per HQ (RobotControllerImpl.assertCanBuildRobot: act radius 9, must SENSE the tile for
            // isLocationOccupied/sensePassability -> radius^2 4 if HQ or tile is a cloud; not a wall; not occupied)
            int minSpawn = Integer.MAX_VALUE;
            boolean[] seedA = new boolean[N], seedB = new boolean[N];
            int actR = RobotType.HEADQUARTERS.actionRadiusSquared;
            for (RobotInfo h : bodies) {
                int hi = idx(h.location.x, h.location.y), cnt = 0;
                for (int i = 0; i < N; i++) {
                    int x = i % W, y = i / W;
                    int d2 = (x - h.location.x) * (x - h.location.x) + (y - h.location.y) * (y - h.location.y);
                    int senseR = (cloud[hi] || cloud[i]) ? GameConstants.CLOUD_VISION_RADIUS_SQUARED : vision;
                    if (d2 <= actR && d2 <= senseR && !wall[i] && hqAt[i] == null) {
                        cnt++;
                        if (h.team == Team.A) seedA[i] = true; else seedB[i] = true;
                    }
                }
                minSpawn = Math.min(minSpawn, cnt);
            }
            // reachability: king moves through non-wall, non-HQ tiles from either team's spawn tiles (currents only
            // ever move a robot to an adjacent non-wall tile, so they add no connectivity)
            int unreachTiles = 0, oneTeamTiles = 0, unreachWells = 0, unreachIsl = 0;
            boolean[] reachA = flood(seedA, wall, hqAt), reachB = flood(seedB, wall, hqAt);
            Set<Integer> islReach = new HashSet<>();
            for (int i = 0; i < N; i++) {
                boolean both = reachA[i] && reachB[i];
                if (!wall[i] && hqAt[i] == null && !reachA[i] && !reachB[i]) unreachTiles++;
                if (!wall[i] && hqAt[i] == null && reachA[i] != reachB[i]) oneTeamTiles++;
                if (isl[i] != 0 && both) islReach.add(isl[i]);
                if (res[i] != 0) {   // collectable from any tile within Chebyshev 1 (MapLocation.isAdjacentTo)
                    boolean ok = false;
                    int x = i % W, y = i / W;
                    for (int dx = -1; dx <= 1; dx++) for (int dy = -1; dy <= 1; dy++) {
                        int nx = x + dx, ny = y + dy;
                        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
                        int j = idx(nx, ny);
                        if (reachA[j] && reachB[j]) ok = true;
                    }
                    if (!ok) unreachWells++;
                }
            }
            unreachIsl = islands.size() - islReach.size();
            String[] ownOnly = new String[2], round1 = new String[2];
            for (Team t : new Team[]{Team.A, Team.B}) {
                boolean[][] left = deduce(t, bodies, hqAt, wall, cloud, cur, isl, res, vision);
                ownOnly[t.ordinal()] = symSet(left[0]);
                round1[t.ordinal()] = symSet(left[1]);
            }

            String[] row = {
                    name, tournament.getOrDefault(name, "?"), "" + W, "" + H, "" + N,
                    m.getOrigin().x + "," + m.getOrigin().y, "" + m.getSeed(),
                    m.getSymmetry().name(), symSet(okAll), symSet(okTerrain), symSet(okWalls), symSet(fCloud), symSet(fCur),
                    symSet(fCurOpp), symSet(fWell), symSet(fIsl), symSet(fHq), symSet(okBuilder), symSet(okBuilder2),
                    builderValid, serverValid,
                    "" + hqA, "" + hqB, order.toString(),
                    "" + wellCount[1], "" + wellCount[2], "" + wellCount[3], "" + cap,
                    "" + islands.size(), "" + islTotal, "" + (islands.isEmpty() ? 0 : islMin), "" + islMax,
                    "" + (islands.isEmpty() ? 0 : islands.firstKey()), "" + (islands.isEmpty() ? 0 : islands.lastKey()),
                    "" + contiguousIds, "" + all4conn,
                    String.format("%.1f", 100.0 * nWall / N), String.format("%.1f", 100.0 * nCloud / N),
                    String.format("%.1f", 100.0 * nCur / N),
                    "" + hqOnIsl, "" + wellOnIsl, "" + cloudOnIsl, "" + curOnIsl, "" + wellOnCloud,
                    "" + minD2, "" + minCheb, "" + pathSteps,
                    "" + worstAD, "" + worstMN, adVis + "/" + bodies.length, mnVis + "/" + bodies.length, "" + onEdge,
                    "" + declaredOk, "" + hqOnCloud, "" + curIntoHq, "" + curIntoCur,
                    "" + need, ownOnly[0], ownOnly[1], round1[0], round1[1], "" + islDiag,
                    "" + minSpawn, "" + unreachTiles, "" + oneTeamTiles, "" + unreachWells, "" + unreachIsl
            };
            out.println(String.join("\t", row));
        }
    }

    /**
     * Which symmetries can team t NOT rule out at the start of the game?
     *
     * Knowledge model (engine rules: InternalRobot.canSenseLocation, RobotControllerImpl.senseNearbyCloudLocations):
     *  - all own HQ locations are known (HQs can share them through the shared array in round 1);
     *  - a tile is fully sensed (wall, cloud, current, well type, island presence, robot) if some own HQ h has
     *    dist2(h,tile) <= R, where R = CLOUD_VISION_RADIUS_SQUARED (4) when h or the tile is a cloud, else the HQ
     *    vision radius (34);
     *  - the cloud bit alone is also known for every tile within 34 of an own HQ that is not itself on a cloud.
     * A symmetry is excluded when it maps an own HQ onto itself, onto another own HQ, or onto a sensed tile without
     * an enemy HQ; when it maps a seen enemy HQ onto a non-own-HQ tile; or when two sensed tiles that it pairs
     * differ in wall / cloud / current (geometric) / well type / island presence / HQ presence.
     *
     * @return [0] = symmetries left using own HQ positions only; [1] = symmetries left after round-1 sensing.
     */
    /** 8-connected flood fill over non-wall, non-HQ tiles from the given seed tiles. */
    static boolean[] flood(boolean[] seed, boolean[] wall, RobotInfo[] hqAt) {
        int N = W * H;
        boolean[] seen = new boolean[N];
        Deque<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < N; i++) if (seed[i]) { seen[i] = true; q.add(i); }
        while (!q.isEmpty()) {
            int c = q.poll(), cx = c % W, cy = c / W;
            for (int dx = -1; dx <= 1; dx++) for (int dy = -1; dy <= 1; dy++) {
                int nx = cx + dx, ny = cy + dy;
                if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
                int j = idx(nx, ny);
                if (seen[j] || wall[j] || hqAt[j] != null) continue;
                seen[j] = true;
                q.add(j);
            }
        }
        return seen;
    }

    static boolean[][] deduce(Team t, RobotInfo[] bodies, RobotInfo[] hqAt, boolean[] wall, boolean[] cloud,
                              int[] cur, int[] isl, int[] res, int vision) {
        int N = W * H;
        boolean[] known = new boolean[N], cloudKnown = new boolean[N];
        List<RobotInfo> own = new ArrayList<>();
        for (RobotInfo r : bodies) if (r.team == t) own.add(r);
        for (RobotInfo h : own) {
            boolean hCloud = cloud[idx(h.location.x, h.location.y)];
            for (int i = 0; i < N; i++) {
                int x = i % W, y = i / W;
                int d2 = (x - h.location.x) * (x - h.location.x) + (y - h.location.y) * (y - h.location.y);
                int r2 = (hCloud || cloud[i]) ? GameConstants.CLOUD_VISION_RADIUS_SQUARED : vision;
                if (d2 <= r2) { known[i] = true; cloudKnown[i] = true; }
                if (!hCloud && d2 <= vision) cloudKnown[i] = true;
            }
        }
        boolean[] ownOnly = {true, true, true}, round1 = {true, true, true};
        for (int s = 0; s < 3; s++) {
            for (RobotInfo h : own) {
                int i = idx(h.location.x, h.location.y), j = idx(sx(s, h.location.x), sy(s, h.location.y));
                if (i == j || (hqAt[j] != null && hqAt[j].team == t)) { ownOnly[s] = false; round1[s] = false; }
                if (known[j] && (hqAt[j] == null || hqAt[j].team == t)) round1[s] = false;
            }
            for (int i = 0; i < N && round1[s]; i++) {
                int x = i % W, y = i / W, j = idx(sx(s, x), sy(s, y));
                if (known[i] && hqAt[i] != null && hqAt[i].team != t && (hqAt[j] == null || hqAt[j].team != t))
                    round1[s] = false;
                if (cloudKnown[i] && cloudKnown[j] && cloud[i] != cloud[j]) round1[s] = false;
                if (!(known[i] && known[j])) continue;
                if (wall[i] != wall[j] || res[i] != res[j] || (isl[i] == 0) != (isl[j] == 0)
                        || mirrorDir(s, Direction.DIRECTION_ORDER[cur[i]]) != Direction.DIRECTION_ORDER[cur[j]]
                        || (hqAt[i] == null) != (hqAt[j] == null)
                        || (hqAt[i] != null && hqAt[i].team == hqAt[j].team))
                    round1[s] = false;
            }
        }
        return new boolean[][]{ownOnly, round1};
    }
}
