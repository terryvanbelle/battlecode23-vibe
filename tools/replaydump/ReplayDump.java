package replaydump;

import battlecode.schema.*;

import java.io.*;
import java.nio.ByteBuffer;
import java.util.*;
import java.util.zip.GZIPInputStream;

/**
 * The microscope: a .bc23 replay (gzipped flatbuffer, schema battlecode.fbs of engine 3.0.15) to text.
 *
 * State is rebuilt from events, because a 2023 replay stores no per-round snapshot of health or inventory:
 *   spawns (spawnedBodies), positions (movedIDs: every robot, every round), deaths (diedIDs),
 *   per-robot deltas CHANGE_HEALTH / CHANGE_ADAMANTIUM / CHANGE_MANA / CHANGE_ELIXIR, team deltas (teamAdChanges...),
 *   island ownership (all islands, every round), indicator strings and bytecodes (every robot, every round).
 * Event encodings (engine InternalRobot/RobotControllerImpl/InternalCarrier):
 *   LAUNCH_ATTACK / THROW_ATTACK target = victim id on a hit, else -(x+y*W)-1;  PICK_UP_RESOURCE / PLACE_RESOURCE target
 *   = x+y*W of the well/HQ;  PICK_UP_ANCHOR = hqId*2+accel (negative-1 = returnAnchor);  PLACE_ANCHOR = island id;
 *   BUILD_ANCHOR = accel index; SPAWN_UNIT = new id; DIE_EXCEPTION = robot died of an uncaught exception.
 * Team ids in the file: 1 = A, 2 = B. Map symmetry: 0 rotation, 1 horizontal, 2 vertical (GameMap.symmetry).
 * Our bot's indicator string is "note|k=v,k=v": --census sums each key's last value per robot (counters) per team.
 *
 * Modes (one per run):
 *   (default)                 summary: map, teams, result, per-team production, deaths, economy, combat, islands,
 *                             bytecode, exceptions
 *   --census                  CSV: one row per team (the gate/basics input; header first)
 *   --metrics [--every N]     CSV: per-round team aggregates (units by type, resources, islands, cumulative events)
 *   --robot ID                one robot's life (spawn, moves, actions, hp, inventory, indicator changes, death)
 *   --map-at R                ASCII board at the end of round R
 *   --logs [--team A|B] [--id ID] [--from R --to R]   indicator strings (changes only)
 *   --bytecode                per team and type: max, mean, p99, near misses (>=90%), overruns (>= limit)
 *   --navstats                per team and type: moved share, still streaks, ABA oscillation
 *   --events --from R --to R  every event in a round window
 *   --islands                 island ownership changes over time
 *   --overruns                every robot-turn that used its whole bytecode limit (round, robot, age in rounds)
 */
public class ReplayDump {
    static final String[] TN = {"HQ", "CARRIER", "LAUNCHER", "AMPLIFIER", "DESTABILIZER", "BOOSTER"};
    static final char[] TC = {'H', 'C', 'L', 'A', 'D', 'B'};
    static final int NT = 6;
    static final int[] BC_LIMIT = {20000, 12500, 10000, 10000, 10000, 10000};

    // ---------------------------------------------------------------- model
    static final class Robot {
        int id, team, type, x, y, hp, ad, mn, ex, anchors, born, died = -1, px = -1, py = -1, ppx = -1, ppy = -1;
        String ind = "";
        int stillRun, maxStill;
        Map<String, Integer> counters = new HashMap<>();
    }

    GameWrapper gw;
    String mapName, teamA = "A", teamB = "B";
    int W, H, symmetry, winner, totalRounds;
    boolean[] wall, cloud;
    int[] current, island, resource;
    int[] maxHp = {1, 150, 200, 120, 300, 400};
    final Map<Integer, Robot> robots = new LinkedHashMap<>();
    final List<Round> rounds = new ArrayList<>();
    int nIslands;
    int[] islandOwner = new int[64];
    int[][] teamRes = new int[3][3];   // [team][Ad,Mn,Ex] running totals

    // per-team accumulators [team 1..2]
    final long[][] built = new long[3][NT], died = new long[3][NT], diedExc = new long[3][NT];
    final long[] launchShots = new long[3], launchHits = new long[3], throwShots = new long[3], throwHits = new long[3];
    final long[] dmgDealt = new long[3], healed = new long[3], pickups = new long[3], deposits = new long[3];
    final long[][] collected = new long[3][3], deposited = new long[3][3];
    final long[] anchorsBuilt = new long[3], anchorsTaken = new long[3], anchorsPlaced = new long[3], islandRounds = new long[3];
    final long[] kills = new long[3];
    final long[][] wellThrown = new long[3][3], gifted = new long[3][3];
    final Map<Integer, Integer> hitRound = new HashMap<>();
    final long[][] bcMax = new long[3][NT], bcSum = new long[3][NT], bcN = new long[3][NT], bcNear = new long[3][NT], bcOver = new long[3][NT];
    final long[][] moveTurns = new long[3][NT], aliveTurns = new long[3][NT], aba = new long[3][NT];
    final List<int[]>[][] bcHist = new List[3][NT];
    int firstAnchor[] = {-1, -1, -1}, firstEnemySeenBy[] = {-1, -1, -1};
    final int[][] snapRounds = {{100, 0}, {250, 0}, {500, 0}, {1000, 0}, {1500, 0}, {2000, 0}};
    final Map<Integer, int[][]> snaps = new TreeMap<>();   // round -> [team][Ad,Mn,Ex,islands,carriers,launchers,amps,units]

    static byte[] read(String f) throws IOException {
        try (InputStream in = new GZIPInputStream(new FileInputStream(f)); ByteArrayOutputStream o = new ByteArrayOutputStream()) {
            byte[] b = new byte[1 << 16];
            int n;
            while ((n = in.read(b)) > 0) o.write(b, 0, n);
            return o.toByteArray();
        }
    }

    ReplayDump(String file) throws IOException {
        gw = GameWrapper.getRootAsGameWrapper(ByteBuffer.wrap(read(file)));
        for (int i = 0; i < gw.eventsLength(); i++) {
            EventWrapper ew = gw.events(i);
            byte t = ew.eType();
            if (t == Event.GameHeader) {
                GameHeader h = (GameHeader) ew.e(new GameHeader());
                for (int k = 0; k < h.teamsLength(); k++) {
                    TeamData td = h.teams(k);
                    if (td.teamID() == 1) teamA = td.name(); else teamB = td.name();
                }
                for (int k = 0; k < h.bodyTypeMetadataLength(); k++) {
                    BodyTypeMetadata m = h.bodyTypeMetadata(k);
                    if (m.type() >= 0 && m.type() < NT) maxHp[m.type()] = m.health();
                }
            } else if (t == Event.MatchHeader) {
                GameMap g = ((MatchHeader) ew.e(new MatchHeader())).map();
                mapName = g.name();
                W = g.maxCorner().x() - g.minCorner().x();
                H = g.maxCorner().y() - g.minCorner().y();
                symmetry = g.symmetry();
                int n = W * H;
                wall = new boolean[n]; cloud = new boolean[n]; current = new int[n]; island = new int[n]; resource = new int[n];
                for (int k = 0; k < n; k++) {
                    wall[k] = g.walls(k); cloud[k] = g.clouds(k); current[k] = g.currents(k);
                    island[k] = g.islands(k); resource[k] = g.resources(k);
                    nIslands = Math.max(nIslands, island[k]);
                }
                SpawnedBodyTable b = g.bodies();
                for (int k = 0; k < b.robotIDsLength(); k++)
                    spawn(b.robotIDs(k), b.teamIDs(k), b.types(k), b.locs().xs(k), b.locs().ys(k), 0);
            } else if (t == Event.Round) {
                rounds.add((Round) ew.e(new Round()));
            } else if (t == Event.MatchFooter) {
                MatchFooter f = (MatchFooter) ew.e(new MatchFooter());
                winner = f.winner();
                totalRounds = f.totalRounds();
            }
        }
        for (int t = 0; t < 3; t++) for (int k = 0; k < NT; k++) bcHist[t][k] = new ArrayList<>();
    }

    Robot spawn(int id, int team, int type, int x, int y, int round) {
        Robot r = new Robot();
        r.id = id; r.team = team; r.type = type; r.x = x; r.y = y; r.hp = maxHp[type]; r.born = round;
        robots.put(id, r);
        if (round > 0) built[team][type]++;
        return r;
    }

    static String side(int team) { return team == 1 ? "A" : team == 2 ? "B" : "?"; }

    /** Event callback for the streaming modes; null = none. */
    interface Listener { void event(int round, String line); }

    Listener listener;

    void emit(int round, String s) { if (listener != null) listener.event(round, s); }

    boolean listening() { return listener != null; }

    /** Replay every round in order, updating the state and accumulators; calls perRound after each round. */
    void run(java.util.function.IntConsumer perRound) {
        for (Round r : rounds) {
            int rn = r.roundID();
            // team totals
            for (int k = 0; k < r.teamIDsLength(); k++) {
                int t = r.teamIDs(k);
                if (t < 1 || t > 2) continue;
                teamRes[t][0] += r.teamAdChanges(k); teamRes[t][1] += r.teamMnChanges(k); teamRes[t][2] += r.teamExChanges(k);
            }
            SpawnedBodyTable s = r.spawnedBodies();
            if (s != null) for (int k = 0; k < s.robotIDsLength(); k++) {
                Robot nr = spawn(s.robotIDs(k), s.teamIDs(k), s.types(k), s.locs().xs(k), s.locs().ys(k), rn);
                if (listener != null) emit(rn, String.format("spawn %s %s#%d at %d,%d", side(nr.team), TN[nr.type], nr.id, nr.x, nr.y));
            }
            int lastChgId = -1, lastChgRes = -1, lastChgAmt = 0;
            for (int k = 0; k < r.actionsLength(); k++) {
                int id = r.actionIDs(k), tgt = r.actionTargets(k);
                byte a = r.actions(k);
                Robot rb = robots.get(id);
                if (rb == null) continue;
                int tm = rb.team;
                switch (a) {
                    case Action.LAUNCH_ATTACK:
                        launchShots[tm]++;
                        if (tgt >= 0) { launchHits[tm]++; hitRound.put(tgt, rn); }
                        break;
                    case Action.THROW_ATTACK:
                        throwShots[tm]++;
                        if (tgt >= 0) { throwHits[tm]++; hitRound.put(tgt, rn); }
                        break;
                    case Action.CHANGE_HEALTH:
                        rb.hp += tgt;
                        if (tgt < 0) dmgDealt[3 - tm] -= tgt; else healed[tm] += tgt;
                        break;
                    case Action.CHANGE_ADAMANTIUM: case Action.CHANGE_MANA: case Action.CHANGE_ELIXIR: {
                        int ri = a == Action.CHANGE_ADAMANTIUM ? 0 : a == Action.CHANGE_MANA ? 1 : 2;
                        if (ri == 0) rb.ad += tgt; else if (ri == 1) rb.mn += tgt; else rb.ex += tgt;
                        lastChgId = id; lastChgRes = ri; lastChgAmt = tgt;   // engine order: CHANGE_* then PICK_UP/PLACE_RESOURCE
                        break;
                    }
                    case Action.PICK_UP_RESOURCE:
                        pickups[tm]++;
                        if (lastChgId == id && lastChgAmt > 0) collected[tm][lastChgRes] += lastChgAmt;
                        break;
                    case Action.PLACE_RESOURCE: {
                        deposits[tm]++;
                        int x = tgt % W, y = tgt / W;
                        Robot hq = null;
                        for (Robot o : robots.values()) if (o.died < 0 && o.type == 0 && o.x == x && o.y == y) hq = o;
                        if (hq != null && hq.team == tm && lastChgId == id && lastChgAmt < 0) deposited[tm][lastChgRes] -= lastChgAmt;
                        if (hq == null && lastChgId == id && lastChgAmt < 0) wellThrown[tm][lastChgRes] -= lastChgAmt;
                        if (hq != null && hq.team != tm && lastChgId == id && lastChgAmt < 0) gifted[tm][lastChgRes] -= lastChgAmt;
                        break;
                    }
                    case Action.BUILD_ANCHOR: anchorsBuilt[tm]++; break;
                    case Action.PICK_UP_ANCHOR:
                        if (tgt >= 0) { anchorsTaken[tm]++; rb.anchors++; } else rb.anchors = Math.max(0, rb.anchors - 1);
                        break;
                    case Action.PLACE_ANCHOR:
                        anchorsPlaced[tm]++;
                        rb.anchors = Math.max(0, rb.anchors - 1);
                        if (firstAnchor[tm] < 0) firstAnchor[tm] = rn;
                        break;
                    case Action.DIE_EXCEPTION: diedExc[tm][rb.type]++; break;
                    default: break;
                }
                if (listener != null) emit(rn, String.format("act %s %s#%d %s %d", side(tm), TN[rb.type], id, Action.name(a), tgt));
            }
            // positions: every living robot, every round
            for (int k = 0; k < r.movedIDsLength(); k++) {
                Robot rb = robots.get(r.movedIDs(k));
                if (rb == null) continue;
                int nx = r.movedLocs().xs(k), ny = r.movedLocs().ys(k);
                if (listener != null && (nx != rb.x || ny != rb.y)) emit(rn, String.format("move %s %s#%d %d,%d -> %d,%d", side(rb.team), TN[rb.type], rb.id, rb.x, rb.y, nx, ny));
                rb.ppx = rb.px; rb.ppy = rb.py; rb.px = rb.x; rb.py = rb.y; rb.x = nx; rb.y = ny;
            }
            for (int k = 0; k < r.diedIDsLength(); k++) {
                Robot rb = robots.get(r.diedIDs(k));
                if (rb == null || rb.died >= 0) continue;
                rb.died = rn;
                died[rb.team][rb.type]++;
                Integer hr = hitRound.get(rb.id);
                if (hr != null && hr == rn) kills[3 - rb.team]++;   // killed by a launcher hit or a throw this round
                if (listener != null) emit(rn, String.format("died %s %s#%d at %d,%d hp=%d", side(rb.team), TN[rb.type], rb.id, rb.x, rb.y, rb.hp));
            }
            for (int k = 0; k < r.islandIDsLength(); k++) {
                int iid = r.islandIDs(k), own = r.islandOwnership(k);
                if (iid >= islandOwner.length) islandOwner = Arrays.copyOf(islandOwner, iid + 16);
                if (listener != null && islandOwner[iid] != own) emit(rn, String.format("island %d %s -> %s", iid, side(islandOwner[iid]), side(own)));
                islandOwner[iid] = own;
                if (own == 1 || own == 2) islandRounds[own]++;
            }
            for (int k = 0; k < r.indicatorStringIDsLength(); k++) {
                Robot rb = robots.get(r.indicatorStringIDs(k));
                if (rb == null) continue;
                String str = r.indicatorStrings(k);
                if (str == null) str = "";
                if (listener != null && !str.equals(rb.ind)) emit(rn, String.format("ind %s %s#%d '%s'", side(rb.team), TN[rb.type], rb.id, str));
                rb.ind = str;
                parseCounters(rb, str);
            }
            for (int k = 0; k < r.bytecodeIDsLength(); k++) {
                Robot rb = robots.get(r.bytecodeIDs(k));
                if (rb == null) continue;
                int used = r.bytecodesUsed(k), lim = BC_LIMIT[rb.type], t = rb.team, ty = rb.type;
                bcMax[t][ty] = Math.max(bcMax[t][ty], used); bcSum[t][ty] += used; bcN[t][ty]++;
                if (used >= lim) { bcOver[t][ty]++; if (listener != null) emit(rn, String.format("overrun %s %s#%d age=%d used=%d", side(t), TN[ty], rb.id, rn - rb.born, used)); }
                else if (used * 10 >= lim * 9) bcNear[t][ty]++;
                bcHist[t][ty].add(new int[]{used});
            }
            // navigation statistics for living mobile robots
            for (Robot rb : robots.values()) {
                if (rb.died >= 0 || rb.born >= rn || rb.type == 0) continue;
                aliveTurns[rb.team][rb.type]++;
                boolean moved = rb.px >= 0 && (rb.px != rb.x || rb.py != rb.y);
                if (moved) { moveTurns[rb.team][rb.type]++; rb.stillRun = 0; }
                else { rb.stillRun++; rb.maxStill = Math.max(rb.maxStill, rb.stillRun); }
                if (moved && rb.ppx == rb.x && rb.ppy == rb.y) aba[rb.team][rb.type]++;
            }
            for (int[] sr : snapRounds) if (sr[0] == rn) snaps.put(rn, snapshot());
            if (perRound != null) perRound.accept(rn);
        }
        if (!snaps.containsKey(totalRounds)) snaps.put(totalRounds, snapshot());
    }

    int[][] snapshot() {
        int[][] s = new int[3][8];
        for (int t = 1; t <= 2; t++) { s[t][0] = teamRes[t][0]; s[t][1] = teamRes[t][1]; s[t][2] = teamRes[t][2]; }
        for (int i = 1; i < islandOwner.length; i++) if (islandOwner[i] == 1 || islandOwner[i] == 2) s[islandOwner[i]][3]++;
        for (Robot rb : robots.values()) {
            if (rb.died >= 0) continue;
            if (rb.type == 1) s[rb.team][4]++;
            if (rb.type == 2) s[rb.team][5]++;
            if (rb.type == 3) s[rb.team][6]++;
            if (rb.type != 0) s[rb.team][7]++;
        }
        return s;
    }

    /** Our indicator format: "note|k=v,k=v". Keeps the latest value of every integer key per robot. */
    static void parseCounters(Robot rb, String s) {
        int bar = s.indexOf('|');
        if (bar < 0) return;
        for (String kv : s.substring(bar + 1).split(",")) {
            int eq = kv.indexOf('=');
            if (eq <= 0) continue;
            try { rb.counters.put(kv.substring(0, eq).trim(), Integer.parseInt(kv.substring(eq + 1).trim())); }
            catch (NumberFormatException ignored) { }
        }
    }

    /** Sum of each counter key over a team's robots (latest value per robot), and max for keys starting with "max". */
    Map<String, Long> counterTotals(int team) {
        Map<String, Long> m = new TreeMap<>();
        for (Robot rb : robots.values()) {
            if (rb.team != team) continue;
            for (Map.Entry<String, Integer> e : rb.counters.entrySet()) {
                String k = e.getKey();
                long v = e.getValue();
                if (k.equals("sm") || k.equals("sd")) continue;   // masks and rounds, not counters: see symStats
            if (k.startsWith("max")) m.merge(k, v, Math::max); else m.merge(k, v, Long::sum);
            }
        }
        return m;
    }

    String winnerSide() { return side(winner); }

    /** The true symmetry as our bot's candidate bit (MapMem: 1 ROT, 2 FLIP_X = engine VERTICAL, 4 FLIP_Y = HORIZONTAL). */
    int truthBit() { return symmetry == 0 ? 1 : symmetry == 1 ? 4 : 2; }

    /** [robots reporting sm, robots whose final mask excludes the truth, earliest decided round or -1, undecided at end]. */
    int[] symStats(int team) {
        int n = 0, wrong = 0, first = -1, undecided = 0, tb = truthBit();
        for (Robot rb : robots.values()) {
            if (rb.team != team) continue;
            Integer sm = rb.counters.get("sm"), sd = rb.counters.get("sd");
            if (sm == null) continue;
            n++;
            if ((sm & tb) == 0) wrong++;
            if (sm != 1 && sm != 2 && sm != 4) undecided++;
            if (sd != null && sd >= 0 && (first < 0 || sd < first)) first = sd;
        }
        return new int[]{n, wrong, first, undecided};
    }

    // ---------------------------------------------------------------- modes
    void summary(PrintStream o) {
        run(null);
        o.printf("map %s %dx%d symmetry=%s islands=%d   A=%s  B=%s%n", mapName, W, H,
            symmetry == 0 ? "ROT" : symmetry == 1 ? "HORIZ" : "VERT", nIslands, teamA, teamB);
        o.printf("result: %s (%s) wins at round %d%n", winnerSide(), winner == 1 ? teamA : teamB, totalRounds);
        for (int t = 1; t <= 2; t++) {
            o.printf("--- team %s (%s)%n", side(t), t == 1 ? teamA : teamB);
            o.printf("  built:  %s%n", typeList(built[t]));
            o.printf("  died:   %s   (exceptions: %s)%n", typeList(died[t]), typeList(diedExc[t]));
            o.printf("  econ:   collected Ad=%d Mn=%d Ex=%d  deposited Ad=%d Mn=%d Ex=%d  pickups=%d deposits=%d%n",
                collected[t][0], collected[t][1], collected[t][2], deposited[t][0], deposited[t][1], deposited[t][2], pickups[t], deposits[t]);
            o.printf("  wells:  thrown into wells Ad=%d Mn=%d Ex=%d   gifted to enemy HQ Ad=%d Mn=%d Ex=%d%n",
                wellThrown[t][0], wellThrown[t][1], wellThrown[t][2], gifted[t][0], gifted[t][1], gifted[t][2]);
            o.printf("  combat: launcher shots=%d hits=%d  throws=%d hits=%d  damage dealt=%d  kills=%d  healed=%d%n",
                launchShots[t], launchHits[t], throwShots[t], throwHits[t], dmgDealt[t], kills[t], healed[t]);
            o.printf("  islands: anchors built=%d taken=%d placed=%d first=%s island-rounds=%d%n",
                anchorsBuilt[t], anchorsTaken[t], anchorsPlaced[t], firstAnchor[t] < 0 ? "-" : "r" + firstAnchor[t], islandRounds[t]);
            StringBuilder sb = new StringBuilder();
            for (Map.Entry<Integer, int[][]> e : snaps.entrySet()) {
                int[] s = e.getValue()[t];
                sb.append(String.format(" r%d[Ad%d Mn%d Ex%d isl%d C%d L%d]", e.getKey(), s[0], s[1], s[2], s[3], s[4], s[5]));
            }
            o.printf("  snaps:%s%n", sb);
            StringBuilder bc = new StringBuilder();
            for (int ty = 0; ty < NT; ty++) if (bcN[t][ty] > 0)
                bc.append(String.format(" %s max=%d mean=%d near=%d over=%d;", TN[ty], bcMax[t][ty], bcSum[t][ty] / bcN[t][ty], bcNear[t][ty], bcOver[t][ty]));
            o.printf("  bytecode:%s%n", bc);
            Map<String, Long> c = counterTotals(t);
            if (!c.isEmpty()) o.printf("  counters: %s%n", c);
            int[] ss = symStats(t);
            if (ss[0] > 0) o.printf("  symmetry: truth=%d robots=%d wrong=%d undecided_at_end=%d first_decided=r%d%n", truthBit(), ss[0], ss[1], ss[3], ss[2]);
        }
    }

    static String typeList(long[] a) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < NT; i++) if (a[i] > 0) sb.append(TN[i]).append('=').append(a[i]).append(' ');
        return sb.length() == 0 ? "-" : sb.toString().trim();
    }

    static final String CENSUS_HDR = "map,team,side,won,rounds,sym,islands_total,built_C,built_L,built_A,built_D,built_B,"
        + "died_C,died_L,died_A,died_D,died_B,exceptions,coll_Ad,coll_Mn,coll_Ex,dep_Ad,dep_Mn,dep_Ex,pickups,deposits,"
        + "shots,hits,throws,throw_hits,dmg,kills,healed,anchors_built,anchors_placed,first_anchor,island_rounds,"
        + "isl500,isl1000,isl1500,isl_end,bank250_Mn,bank250_Ad,bank500_Mn,bank500_Ad,bank_end_Ad,bank_end_Mn,bank_end_Ex,"
        + "L_end,C_end,bc_max_C,bc_max_L,bc_max_HQ,near,over,still_L,still_C,aba,sym_robots,sym_wrong,sym_first_decided,sym_undecided,counters";

    void census(PrintStream o, boolean header) {
        run(null);
        if (header) o.println(CENSUS_HDR);
        for (int t = 1; t <= 2; t++) {
            int[][] s500 = snaps.get(500), s1000 = snaps.get(1000), s1500 = snaps.get(1500), s250 = snaps.get(250), sEnd = snaps.get(totalRounds);
            long near = 0, over = 0, exc = 0;
            for (int ty = 0; ty < NT; ty++) { near += bcNear[t][ty]; over += bcOver[t][ty]; exc += diedExc[t][ty]; }
            StringBuilder cs = new StringBuilder();
            for (Map.Entry<String, Long> e : counterTotals(t).entrySet()) cs.append(e.getKey()).append('=').append(e.getValue()).append(';');
            o.println(String.join(",", mapName, t == 1 ? teamA : teamB, side(t), winner == t ? "1" : "0", "" + totalRounds,
                "" + symmetry, "" + nIslands,
                "" + built[t][1], "" + built[t][2], "" + built[t][3], "" + built[t][4], "" + built[t][5],
                "" + died[t][1], "" + died[t][2], "" + died[t][3], "" + died[t][4], "" + died[t][5], "" + exc,
                "" + collected[t][0], "" + collected[t][1], "" + collected[t][2], "" + deposited[t][0], "" + deposited[t][1], "" + deposited[t][2],
                "" + pickups[t], "" + deposits[t], "" + launchShots[t], "" + launchHits[t], "" + throwShots[t], "" + throwHits[t],
                "" + dmgDealt[t], "" + kills[t], "" + healed[t], "" + anchorsBuilt[t], "" + anchorsPlaced[t], "" + firstAnchor[t], "" + islandRounds[t],
                s500 == null ? "" : "" + s500[t][3], s1000 == null ? "" : "" + s1000[t][3], s1500 == null ? "" : "" + s1500[t][3], "" + sEnd[t][3],
                s250 == null ? "" : "" + s250[t][1], s250 == null ? "" : "" + s250[t][0], s500 == null ? "" : "" + s500[t][1], s500 == null ? "" : "" + s500[t][0],
                "" + sEnd[t][0], "" + sEnd[t][1], "" + sEnd[t][2], "" + sEnd[t][5], "" + sEnd[t][4],
                "" + bcMax[t][1], "" + bcMax[t][2], "" + bcMax[t][0], "" + near, "" + over,
                fmt(1.0 - ratio(moveTurns[t][2], aliveTurns[t][2])), fmt(1.0 - ratio(moveTurns[t][1], aliveTurns[t][1])),
                "" + (aba[t][1] + aba[t][2]), "" + symStats(t)[0], "" + symStats(t)[1], "" + symStats(t)[2], "" + symStats(t)[3], cs.toString()));
        }
    }

    static double ratio(long a, long b) { return b == 0 ? 0 : (double) a / b; }
    static String fmt(double d) { return String.format("%.3f", d); }

    void metrics(PrintStream o, int every) {
        o.println("round,team,carriers,launchers,amplifiers,others,Ad,Mn,Ex,islands,shots,dmg,kills,anchors_placed,collected_Mn,collected_Ad");
        run(rn -> {
            if (rn % every != 0 && rn != totalRounds) return;
            int[][] s = snapshot();
            for (int t = 1; t <= 2; t++) {
                int others = 0;
                for (Robot rb : robots.values()) if (rb.died < 0 && rb.team == t && rb.type >= 4) others++;
                o.printf("%d,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d%n", rn, side(t), s[t][4], s[t][5], s[t][6], others,
                    s[t][0], s[t][1], s[t][2], s[t][3], launchShots[t], dmgDealt[t], kills[t], anchorsPlaced[t], collected[t][1], collected[t][0]);
            }
        });
    }

    void robot(PrintStream o, int id) {
        listener = (rn, line) -> {
            int at = line.indexOf('#');
            if (at < 0) return;
            int end = at + 1;
            while (end < line.length() && Character.isDigit(line.charAt(end))) end++;
            if (Integer.parseInt(line.substring(at + 1, end)) == id) o.printf("r%-5d %s%n", rn, line);
        };
        run(rn -> {
            Robot rb = robots.get(id);
            if (rb != null && rb.died < 0 && rn % 100 == 0) o.printf("r%-5d state hp=%d inv Ad=%d Mn=%d Ex=%d anchors=%d at %d,%d%n", rn, rb.hp, rb.ad, rb.mn, rb.ex, rb.anchors, rb.x, rb.y);
        });
        Robot rb = robots.get(id);
        if (rb == null) o.println("no robot " + id);
        else o.printf("robot %d %s %s born r%d died %s maxStill=%d%n", id, side(rb.team), TN[rb.type], rb.born, rb.died < 0 ? "-" : "r" + rb.died, rb.maxStill);
    }

    void mapAt(PrintStream o, int at) {
        run(rn -> {
            if (rn != at) return;
            char[][] g = new char[H][W];
            for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) {
                int i = x + y * W;
                char c = wall[i] ? '#' : cloud[i] ? '~' : current[i] != 0 ? '>' : '.';
                if (resource[i] == 1) c = 'a'; else if (resource[i] == 2) c = 'm'; else if (resource[i] == 3) c = 'e';
                if (island[i] > 0) { int own = islandOwner[island[i]]; c = own == 1 ? 'I' : own == 2 ? 'i' : '+'; }
                g[y][x] = c;
            }
            for (Robot rb : robots.values()) {
                if (rb.died >= 0 || rb.born > rn) continue;
                char c = TC[rb.type];
                g[rb.y][rb.x] = rb.team == 1 ? c : Character.toLowerCase(c);
            }
            o.printf("round %d  (A upper, B lower; H hq C carrier L launcher A amp D destab B boost; # wall ~ cloud > current a/m/e well; I/i/+ island A/B/neutral)%n", rn);
            for (int y = H - 1; y >= 0; y--) o.println(new String(g[y]));
        });
    }

    void logs(PrintStream o, String team, int id, int from, int to) {
        listener = (rn, line) -> {
            if (!line.startsWith("ind ") || rn < from || rn > to) return;
            if (team != null && !line.startsWith("ind " + team + " ")) return;
            if (id >= 0 && !line.contains("#" + id + " ")) return;
            o.printf("r%-5d %s%n", rn, line.substring(4));
        };
        run(null);
    }

    void bytecode(PrintStream o) {
        run(null);
        o.println("team type robot-turns max mean p99 near90 overrun limit");
        for (int t = 1; t <= 2; t++) for (int ty = 0; ty < NT; ty++) {
            if (bcN[t][ty] == 0) continue;
            int[] v = new int[bcHist[t][ty].size()];
            for (int i = 0; i < v.length; i++) v[i] = bcHist[t][ty].get(i)[0];
            Arrays.sort(v);
            o.printf("%s %-12s %7d %6d %6d %6d %6d %6d %6d%n", side(t), TN[ty], bcN[t][ty], bcMax[t][ty], bcSum[t][ty] / bcN[t][ty],
                v[Math.min(v.length - 1, (int) (v.length * 0.99))], bcNear[t][ty], bcOver[t][ty], BC_LIMIT[ty]);
        }
    }

    void navstats(PrintStream o) {
        run(null);
        o.println("team type robot-rounds moved% still% aba maxStill(p50/p90/max)");
        for (int t = 1; t <= 2; t++) for (int ty = 1; ty < NT; ty++) {
            if (aliveTurns[t][ty] == 0) continue;
            List<Integer> ms = new ArrayList<>();
            for (Robot rb : robots.values()) if (rb.team == t && rb.type == ty) ms.add(rb.maxStill);
            Collections.sort(ms);
            o.printf("%s %-12s %7d %5.1f %5.1f %5d   %d/%d/%d%n", side(t), TN[ty], aliveTurns[t][ty],
                100.0 * ratio(moveTurns[t][ty], aliveTurns[t][ty]), 100.0 * (1 - ratio(moveTurns[t][ty], aliveTurns[t][ty])), aba[t][ty],
                ms.get(ms.size() / 2), ms.get(Math.min(ms.size() - 1, ms.size() * 9 / 10)), ms.get(ms.size() - 1));
        }
    }

    void events(PrintStream o, int from, int to) {
        listener = (rn, line) -> { if (rn >= from && rn <= to) o.printf("r%-5d %s%n", rn, line); };
        run(null);
    }

    void islands(PrintStream o) {
        listener = (rn, line) -> { if (line.startsWith("island ") || line.contains("PLACE_ANCHOR")) o.printf("r%-5d %s%n", rn, line); };
        run(null);
        o.printf("final island owners:");
        for (int i = 1; i <= nIslands; i++) o.printf(" %d:%s", i, islandOwner[i] == 0 ? "-" : side(islandOwner[i]));
        o.println();
    }

    // ---------------------------------------------------------------- main
    static String arg(String[] a, String k, String def) {
        for (int i = 0; i < a.length - 1; i++) if (a[i].equals(k)) return a[i + 1];
        return def;
    }

    static boolean flag(String[] a, String k) { return Arrays.asList(a).contains(k); }

    public static void main(String[] a) throws Exception {
        if (a.length == 1 && a[0].equals("--census-header")) { System.out.println(CENSUS_HDR); return; }
        if (a.length < 1) {
            System.err.println("usage: ReplayDump <replay.bc23> [--census [--no-header] | --metrics [--every N] | --robot ID | --map-at R | "
                + "--logs [--team A|B] [--id ID] [--from R --to R] | --bytecode | --navstats | --events --from R --to R | --islands]");
            System.exit(2);
        }
        ReplayDump d = new ReplayDump(a[0]);
        PrintStream o = new PrintStream(new BufferedOutputStream(System.out), false);
        int from = Integer.parseInt(arg(a, "--from", "0")), to = Integer.parseInt(arg(a, "--to", "1000000"));
        if (flag(a, "--census")) d.census(o, !flag(a, "--no-header"));
        else if (flag(a, "--metrics")) d.metrics(o, Integer.parseInt(arg(a, "--every", "50")));
        else if (flag(a, "--robot")) d.robot(o, Integer.parseInt(arg(a, "--robot", "-1")));
        else if (flag(a, "--map-at")) d.mapAt(o, Integer.parseInt(arg(a, "--map-at", "1")));
        else if (flag(a, "--logs")) d.logs(o, arg(a, "--team", null), Integer.parseInt(arg(a, "--id", "-1")), from, to);
        else if (flag(a, "--bytecode")) d.bytecode(o);
        else if (flag(a, "--navstats")) d.navstats(o);
        else if (flag(a, "--events")) d.events(o, from, to);
        else if (flag(a, "--islands")) d.islands(o);
        else if (flag(a, "--overruns")) { d.listener = (rn, line) -> { if (line.startsWith("overrun")) o.printf("r%-5d %s%n", rn, line); }; d.run(null); }
        else d.summary(o);
        o.flush();
    }
}
