// Minimal .bc23 replay reader, using only the generated flatbuffers classes (battlecode.schema.*)
// and com.google.flatbuffers.* that ship inside the engine fat jar battlecode23-3.0.15.jar.
//
// Build:  javac -source 8 -target 8 -cp battlecode23-3.0.15.jar -d classes ReplayReader.java
// Run:    java -cp classes:battlecode23-3.0.15.jar ReplayReader <file.bc23> [round,round,...]
//
// It replays the event stream, keeps a robot table (spawned/died/moved), cumulative team resources
// (sum of Round.teamXxChanges), per-robot inventories (sum of CHANGE_* actions), and prints a summary
// for the requested rounds. It also runs consistency checks that tie the file to the engine semantics.
import battlecode.schema.*;

import java.io.*;
import java.nio.ByteBuffer;
import java.util.*;
import java.util.zip.GZIPInputStream;

public class ReplayReader {

    // robot record: [team, type, x, y, ad, mn, ex]
    static final int TEAM = 0, TYPE = 1, X = 2, Y = 3, AD = 4, MN = 5, EX = 6;

    static Map<Integer, int[]> alive = new HashMap<>();
    static Map<Integer, int[]> ever = new HashMap<>();   // never removed: lookups for dead robots
    static long[][] teamRes = new long[3][3];             // [teamID 1..2][ad,mn,ex] cumulative
    static int width, height;
    static int[] bytecodeLimit = new int[6];             // by BodyType, from GameHeader.bodyTypeMetadata
    static Set<Integer> wellLocs = new HashSet<>();
    static Map<String, Integer> checks = new TreeMap<>();  // name -> violations
    static Map<String, String> firstSample = new TreeMap<>();

    static void check(String name, boolean ok) {
        checks.merge(name, ok ? 0 : 1, Integer::sum);
    }

    static Map<String, Integer> stats = new TreeMap<>();

    static void stat(String name, int n) {
        stats.merge(name, n, Integer::sum);
    }

    static byte[] gunzip(String path) throws IOException {
        try (InputStream in = new GZIPInputStream(new BufferedInputStream(new FileInputStream(path)))) {
            ByteArrayOutputStream out = new ByteArrayOutputStream(1 << 23);
            byte[] buf = new byte[1 << 16];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            return out.toByteArray();
        }
    }

    static String loc(int idx) {
        return "(" + (idx % width) + "," + (idx / width) + ")";
    }

    public static void main(String[] args) throws Exception {
        String path = args.length > 0 ? args[0] : "/home/terryvanbelle/projects/vibe/2023/matches/test1.bc23";
        Set<Integer> want = new TreeSet<>(Arrays.asList(1, 100, 500, 2000));
        if (args.length > 1) {
            want.clear();
            for (String s : args[1].split(",")) want.add(Integer.parseInt(s.trim()));
        }

        byte[] raw = gunzip(path);
        System.out.println("file: " + path + "  gunzipped bytes: " + raw.length);
        ByteBuffer bb = ByteBuffer.wrap(raw);
        GameWrapper gw = GameWrapper.getRootAsGameWrapper(bb);
        System.out.println("GameWrapper: events=" + gw.eventsLength() + " matchHeaders=" + ints(gw.matchHeadersLength(), gw::matchHeaders)
                + " matchFooters=" + ints(gw.matchFootersLength(), gw::matchFooters));

        int prevRound = 0;
        Round lastRound = null;
        int lastPrinted = -1;
        EventWrapper ew = new EventWrapper();
        for (int i = 0; i < gw.eventsLength(); i++) {
            gw.events(ew, i);
            byte t = ew.eType();
            switch (t) {
                case Event.GameHeader: {
                    GameHeader gh = (GameHeader) ew.e(new GameHeader());
                    System.out.println("[" + i + "] GameHeader specVersion=" + gh.specVersion());
                    for (int k = 0; k < gh.teamsLength(); k++) {
                        TeamData td = gh.teams(k);
                        System.out.println("    team id=" + td.teamID() + " name=" + td.name() + " package=" + td.packageName());
                    }
                    for (int k = 0; k < gh.bodyTypeMetadataLength(); k++) {
                        BodyTypeMetadata m = gh.bodyTypeMetadata(k);
                        bytecodeLimit[m.type()] = m.bytecodeLimit();
                        System.out.printf("    body %-12s cost Ad/Mn/Ex=%d/%d/%d actCD=%d moveCD=%d hp=%d actR2=%d visR2=%d bc=%d%n",
                                BodyType.name(m.type()), m.buildCostAd(), m.buildCostMn(), m.buildCostEx(), m.actionCooldown(),
                                m.movementCooldown(), m.health(), m.actionRadiusSquared(), m.visionRadiusSquared(), m.bytecodeLimit());
                    }
                    Constants c = gh.constants();
                    System.out.println("    constants increasePeriod=" + c.increasePeriod() + " AdAdditiveIncrease=" + c.AdAdditiveIncrease()
                            + " MnAdditiveIncrease=" + c.MnAdditiveIncrease());
                    break;
                }
                case Event.MatchHeader: {
                    MatchHeader mh = (MatchHeader) ew.e(new MatchHeader());
                    GameMap m = mh.map();
                    // a .bc23 may hold several matches; robot IDs restart per match, so reset all state
                    alive.clear(); ever.clear(); wellLocs.clear(); teamRes = new long[3][3]; prevRound = 0;
                    width = m.maxCorner().x() - m.minCorner().x();
                    height = m.maxCorner().y() - m.minCorner().y();
                    int[] resCount = new int[4];
                    Set<Integer> islands = new TreeSet<>();
                    int walls = 0, clouds = 0, currents = 0;
                    for (int k = 0; k < m.resourcesLength(); k++) {
                        resCount[m.resources(k)]++;
                        if (m.resources(k) != 0) wellLocs.add(k);
                        if (m.islands(k) != 0) islands.add(m.islands(k));
                        if (m.walls(k)) walls++;
                        if (m.clouds(k)) clouds++;
                        if (m.currents(k) != 0) currents++;
                    }
                    System.out.println("[" + i + "] MatchHeader map=" + m.name() + " min=(" + m.minCorner().x() + "," + m.minCorner().y()
                            + ") max=(" + m.maxCorner().x() + "," + m.maxCorner().y() + ") => " + width + "x" + height
                            + " symmetry=" + m.symmetry() + " seed=" + m.randomSeed() + " maxRounds=" + mh.maxRounds());
                    System.out.println("    tiles: walls=" + walls + " clouds=" + clouds + " currents=" + currents
                            + " wells Ad/Mn/Ex=" + resCount[1] + "/" + resCount[2] + "/" + resCount[3]
                            + " islands=" + islands.size() + " ids=" + islands);
                    SpawnedBodyTable b = m.bodies();
                    VecTable bl = b.locs();
                    for (int k = 0; k < b.robotIDsLength(); k++) {
                        int[] r = {b.teamIDs(k), b.types(k), bl.xs(k), bl.ys(k), 0, 0, 0};
                        alive.put(b.robotIDs(k), r);
                        ever.put(b.robotIDs(k), r);
                        System.out.println("    initial body id=" + b.robotIDs(k) + " team=" + b.teamIDs(k) + " type="
                                + BodyType.name(b.types(k)) + " at (" + bl.xs(k) + "," + bl.ys(k) + ")");
                    }
                    break;
                }
                case Event.Round: {
                    Round r = (Round) ew.e(new Round());
                    check("roundID increments by 1", r.roundID() == prevRound + 1);
                    prevRound = r.roundID();
                    Map<String, Integer> actionCounts = processRound(r);
                    lastRound = r;
                    if (want.contains(r.roundID())) {
                        printRound(r, actionCounts);
                        lastPrinted = r.roundID();
                    }
                    break;
                }
                case Event.MatchFooter: {
                    MatchFooter mf = (MatchFooter) ew.e(new MatchFooter());
                    System.out.println("[" + i + "] MatchFooter winner=" + mf.winner() + " totalRounds=" + mf.totalRounds()
                            + " profilerFiles=" + mf.profilerFilesLength());
                    check("MatchFooter.totalRounds == last Round.roundID", lastRound != null && mf.totalRounds() == lastRound.roundID());
                    if (lastRound != null && lastPrinted != lastRound.roundID()) {
                        System.out.println("    (requested rounds beyond the end were not reached; last round is " + lastRound.roundID() + ")");
                    }
                    break;
                }
                case Event.GameFooter: {
                    GameFooter gf = (GameFooter) ew.e(new GameFooter());
                    System.out.println("[" + i + "] GameFooter winner=" + gf.winner());
                    break;
                }
                default:
                    System.out.println("[" + i + "] unknown event type " + t);
            }
        }
        System.out.println("\nfirst decoded sample of each action type:");
        for (Map.Entry<String, String> e : firstSample.entrySet()) System.out.println("    " + e.getKey() + ": " + e.getValue());
        System.out.println("\nwhole-match tallies:");
        for (Map.Entry<String, Integer> e : stats.entrySet()) System.out.println("    " + e.getValue() + "  " + e.getKey());
        System.out.println("\nconsistency checks (violations):");
        for (Map.Entry<String, Integer> e : checks.entrySet()) System.out.println("    " + e.getValue() + "  " + e.getKey());
    }

    interface IntAt { int at(int j); }

    static String ints(int n, IntAt f) {
        StringBuilder sb = new StringBuilder("[");
        for (int j = 0; j < n; j++) sb.append(j > 0 ? "," : "").append(f.at(j));
        return sb.append("]").toString();
    }

    static Map<String, Integer> processRound(Round r) {
        Map<String, Integer> counts = new TreeMap<>();
        // 1. spawns (robots built this round; initial HQs are only in MatchHeader.map.bodies)
        SpawnedBodyTable sb = r.spawnedBodies();
        Set<Integer> spawnedNow = new HashSet<>();
        if (sb != null) {
            VecTable sl = sb.locs();
            for (int k = 0; k < sb.robotIDsLength(); k++) {
                int[] rec = {sb.teamIDs(k), sb.types(k), sl.xs(k), sl.ys(k), 0, 0, 0};
                check("spawned id is new", !ever.containsKey(sb.robotIDs(k)));
                alive.put(sb.robotIDs(k), rec);
                ever.put(sb.robotIDs(k), rec);
                spawnedNow.add(sb.robotIDs(k));
            }
        }
        // 2. actions, in the order the engine appended them
        for (int k = 0; k < r.actionsLength(); k++) {
            int id = r.actionIDs(k), a = r.actions(k), tgt = r.actionTargets(k);
            String name = Action.name(a);
            int[] actor = ever.get(id);
            check("action actor id known", actor != null);
            String key = name + (actor != null ? " team" + actor[TEAM] : "");
            counts.merge(key, 1, Integer::sum);
            stat("action total " + name, 1);
            if (a >= Action.CHANGE_ADAMANTIUM && a <= Action.CHANGE_ELIXIR && tgt == 0) stat("CHANGE_AD/MN/EX entries with delta 0", 1);
            String sample = null;
            switch (a) {
                case Action.CHANGE_ADAMANTIUM: if (actor != null) actor[AD] += tgt; sample = "delta " + tgt; break;
                case Action.CHANGE_MANA:       if (actor != null) actor[MN] += tgt; sample = "delta " + tgt; break;
                case Action.CHANGE_ELIXIR:     if (actor != null) actor[EX] += tgt; sample = "delta " + tgt; break;
                case Action.THROW_ATTACK:
                    // InternalCarrier.emptyResources() zeroes the inventory WITHOUT emitting CHANGE_* actions
                    if (actor != null) { actor[AD] = 0; actor[MN] = 0; actor[EX] = 0; }
                    // fall through to decode target like a launcher attack
                case Action.LAUNCH_ATTACK:
                    if (tgt >= 0) {
                        int[] victim = ever.get(tgt);
                        check(name + " robot target is an enemy", victim != null && actor != null && victim[TEAM] != actor[TEAM]);
                        sample = "robot " + tgt + (victim != null ? " " + BodyType.name(victim[TYPE]) : "");
                    } else {
                        sample = "no-damage location " + loc(-tgt - 1);
                    }
                    break;
                case Action.SPAWN_UNIT:
                    check("SPAWN_UNIT target in this round's spawnedBodies", spawnedNow.contains(tgt));
                    check("SPAWN_UNIT actor is HQ", actor != null && actor[TYPE] == BodyType.HEADQUARTERS);
                    sample = "new robot " + tgt + (ever.containsKey(tgt) ? " " + BodyType.name(ever.get(tgt)[TYPE]) : "");
                    break;
                case Action.PICK_UP_RESOURCE:
                    check("PICK_UP_RESOURCE target is a well", wellLocs.contains(tgt));
                    sample = "well at " + loc(tgt);
                    break;
                case Action.PLACE_RESOURCE:
                    sample = "at " + loc(tgt) + (wellLocs.contains(tgt) ? " (well)" : " (HQ)");
                    break;
                case Action.BUILD_ANCHOR: sample = tgt == 0 ? "STANDARD" : "ACCELERATING"; break;
                case Action.PICK_UP_ANCHOR:
                    sample = tgt >= 0 ? "take from HQ " + (tgt / 2) + " anchor " + (tgt % 2)
                                      : "return to HQ " + ((-tgt - 1) / 2) + " anchor " + ((-tgt - 1) % 2);
                    break;
                case Action.PLACE_ANCHOR: sample = "island " + tgt; break;
                case Action.CHANGE_HEALTH: sample = "delta " + tgt; break;
                case Action.BOOST: case Action.DESTABILIZE: case Action.DESTABILIZE_DAMAGE: sample = "at " + loc(tgt); break;
                case Action.DIE_EXCEPTION: sample = "target " + tgt; break;
                default: sample = "target " + tgt;
            }
            firstSample.putIfAbsent(name, "round " + r.roundID() + " robot " + id
                    + (actor != null ? " " + BodyType.name(actor[TYPE]) + " team" + actor[TEAM] : "") + " -> " + sample);
        }
        // 2b. per-victim bookkeeping: robot-target attacks vs negative CHANGE_HEALTH entries (keyed by the VICTIM's id)
        Map<Integer, Integer> hits = new HashMap<>(), negHealth = new HashMap<>();
        for (int k = 0; k < r.actionsLength(); k++) {
            int a = r.actions(k), tgt = r.actionTargets(k);
            if ((a == Action.LAUNCH_ATTACK || a == Action.THROW_ATTACK) && tgt >= 0) hits.merge(tgt, 1, Integer::sum);
            if (a == Action.CHANGE_HEALTH && tgt < 0) negHealth.merge(r.actionIDs(k), 1, Integer::sum);
            if (a == Action.DIE_EXCEPTION) stat("DIE_EXCEPTION actions", 1);
        }
        // 3. deaths
        for (int k = 0; k < r.diedIDsLength(); k++) {
            int id = r.diedIDs(k);
            int[] dead = alive.remove(id);
            check("died id was alive", dead != null);
            if (dead != null) check("dead robot inventory zeroed by CHANGE_* actions", dead[AD] == 0 && dead[MN] == 0 && dead[EX] == 0);
            int diff = hits.getOrDefault(id, 0) - negHealth.getOrDefault(id, 0);
            boolean nearEnemyHq = false;
            if (dead != null)
                for (int[] o : alive.values())
                    if (o[TYPE] == BodyType.HEADQUARTERS && o[TEAM] != dead[TEAM])
                        // last known position is the previous end of round; allow one step of movement this turn
                        for (int dx = -1; dx <= 1; dx++) for (int dy = -1; dy <= 1; dy++) {
                            int ex = dead[X] + dx - o[X], ey = dead[Y] + dy - o[Y];
                            if (ex * ex + ey * ey <= 9) nearEnemyHq = true;
                        }
            stat("deaths where (robot-target hits - negative CHANGE_HEALTH that round) = " + diff
                    + (nearEnemyHq ? ", within one step of enemy HQ r2<=9" : ", not near enemy HQ"), 1);
        }
        // robots built this round do not take a turn this round
        for (int k = 0; k < r.bytecodeIDsLength(); k++) {
            check("robot spawned this round is absent from bytecodeIDs", !spawnedNow.contains(r.bytecodeIDs(k)));
            int[] rec = ever.get(r.bytecodeIDs(k));
            // RobotMonitor: used = limit - bytecodesLeft; a turn cut off by the limit pauses with bytecodesLeft <= 0
            if (rec != null && r.bytecodesUsed(k) >= bytecodeLimit[rec[TYPE]])
                stat("bytecode overruns (bytecodesUsed >= limit) team" + rec[TEAM] + " " + BodyType.name(rec[TYPE]), 1);
        }
        for (int k = 0; k < r.indicatorStringsLength(); k++)
            stat(r.indicatorStrings(k).isEmpty() ? "indicator string entries that are empty" : "indicator string entries non-empty", 1);
        // 4. positions: the engine lists EVERY living robot here at end of round, not only movers
        VecTable ml = r.movedLocs();
        check("movedIDs == all living robots", r.movedIDsLength() == alive.size());
        for (int k = 0; k < r.movedIDsLength(); k++) {
            int[] rec = alive.get(r.movedIDs(k));
            check("moved id is alive", rec != null);
            if (rec != null) { rec[X] = ml.xs(k); rec[Y] = ml.ys(k); }
        }
        // 5. team resources (cumulative sum of per-round deltas)
        for (int k = 0; k < r.teamIDsLength(); k++) {
            int team = r.teamIDs(k);
            teamRes[team][0] += r.teamAdChanges(k);
            teamRes[team][1] += r.teamMnChanges(k);
            teamRes[team][2] += r.teamExChanges(k);
        }
        // team total == sum of all living robots' inventories (HQs + carriers)
        long[][] sum = new long[3][3];
        for (int[] rec : alive.values()) { sum[rec[TEAM]][0] += rec[AD]; sum[rec[TEAM]][1] += rec[MN]; sum[rec[TEAM]][2] += rec[EX]; }
        for (int team = 1; team <= 2; team++)
            check("team totals == sum of living robots' inventories", Arrays.equals(sum[team], teamRes[team]));
        check("one indicator string per robot that ran", r.indicatorStringIDsLength() == r.bytecodeIDsLength());
        check("islands listed every round", r.islandIDsLength() > 0);
        check("wells listed every round == wells on map", r.resourceWellLocsLength() == wellLocs.size());
        return counts;
    }

    static void printRound(Round r, Map<String, Integer> actionCounts) {
        System.out.println("\n=== Round " + r.roundID() + " ===");
        // robots per team by type (alive at end of round)
        int[][] byType = new int[3][6];
        for (int[] rec : alive.values()) byType[rec[TEAM]][rec[TYPE]]++;
        for (int team = 1; team <= 2; team++) {
            StringBuilder sb = new StringBuilder("  robots team" + team + ":");
            int tot = 0;
            for (int ty = 0; ty < 6; ty++) { sb.append(" ").append(BodyType.name(ty)).append("=").append(byType[team][ty]); tot += byType[team][ty]; }
            System.out.println(sb.append("  total=").append(tot));
        }
        // resources
        for (int team = 1; team <= 2; team++) {
            long hqAd = 0, hqMn = 0, hqEx = 0, cAd = 0, cMn = 0, cEx = 0;
            for (int[] rec : alive.values()) {
                if (rec[TEAM] != team) continue;
                if (rec[TYPE] == BodyType.HEADQUARTERS) { hqAd += rec[AD]; hqMn += rec[MN]; hqEx += rec[EX]; }
                else { cAd += rec[AD]; cMn += rec[MN]; cEx += rec[EX]; }
            }
            int idx = -1;
            for (int k = 0; k < r.teamIDsLength(); k++) if (r.teamIDs(k) == team) idx = k;
            System.out.printf("  resources team%d: total Ad/Mn/Ex=%d/%d/%d (HQs %d/%d/%d, carried %d/%d/%d); this-round delta %d/%d/%d%n",
                    team, teamRes[team][0], teamRes[team][1], teamRes[team][2], hqAd, hqMn, hqEx, cAd, cMn, cEx,
                    r.teamAdChanges(idx), r.teamMnChanges(idx), r.teamExChanges(idx));
        }
        System.out.println("  actions this round: " + actionCounts);
        int sp = r.spawnedBodies() == null ? 0 : r.spawnedBodies().robotIDsLength();
        System.out.println("  spawned=" + sp + " died=" + r.diedIDsLength() + " movedIDs(=living)=" + r.movedIDsLength()
                + " bytecodeIDs=" + r.bytecodeIDsLength() + " indicatorStrings=" + r.indicatorStringsLength()
                + " dots=" + r.indicatorDotIDsLength() + " lines=" + r.indicatorLineIDsLength());
        // bytecodes per team
        long[] bc = new long[3]; int[] n = new int[3]; int[] mx = new int[3];
        for (int k = 0; k < r.bytecodeIDsLength(); k++) {
            int[] rec = ever.get(r.bytecodeIDs(k));
            int team = rec == null ? 0 : rec[TEAM];
            bc[team] += r.bytecodesUsed(k); n[team]++; mx[team] = Math.max(mx[team], r.bytecodesUsed(k));
        }
        for (int team = 1; team <= 2; team++)
            System.out.printf("  bytecodes team%d: robots=%d sum=%d avg=%d max=%d%n", team, n[team], bc[team], n[team] == 0 ? 0 : bc[team] / n[team], mx[team]);
        // islands
        int[] own = new int[3]; StringBuilder isl = new StringBuilder();
        for (int k = 0; k < r.islandIDsLength(); k++) {
            own[r.islandOwnership(k)]++;
            if (r.islandOwnership(k) != 0) isl.append(" #").append(r.islandIDs(k)).append(":t").append(r.islandOwnership(k)).append(":hp").append(r.islandTurnoverTurns(k));
        }
        System.out.println("  islands: neutral=" + own[0] + " team1=" + own[1] + " team2=" + own[2] + (isl.length() > 0 ? "  owned:" + isl : ""));
        // wells
        int[] wt = new int[4]; int up = 0; long stAd = 0, stMn = 0, stEx = 0;
        for (int k = 0; k < r.resourceWellLocsLength(); k++) {
            wt[r.resourceID(k)]++; up += r.wellAccelerationID(k);
            stAd += r.wellAdamantiumValues(k); stMn += r.wellManaValues(k); stEx += r.wellElixirValues(k);
        }
        System.out.println("  wells: " + r.resourceWellLocsLength() + " (Ad/Mn/Ex type " + wt[1] + "/" + wt[2] + "/" + wt[3]
                + ") upgraded=" + up + " deposited-into-wells Ad/Mn/Ex=" + stAd + "/" + stMn + "/" + stEx);
        // a couple of indicator strings
        int shown = 0;
        for (int k = 0; k < r.indicatorStringsLength() && shown < 3; k++) {
            String s = r.indicatorStrings(k);
            if (s != null && !s.isEmpty()) { System.out.println("  indicator robot " + r.indicatorStringIDs(k) + ": \"" + s + "\""); shown++; }
        }
    }
}
