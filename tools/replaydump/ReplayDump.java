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
 *   --states                  per team and type, the share of robot-turns in each state token (first note char)
 *   --overruns                every robot-turn that used its whole bytecode limit (round, robot, age in rounds)
 * Telemetry and extraction (docs/TELEMETRY.md part B; the B.2 model is built in run() when `deep` is set):
 *   --extract DIR [--match ID] [--games all|i,j] [--tele-turns]   one decompression, then every selected game's files
 *                             (games, census, deaths, engagements, timeline, hq, robots, tele_states, trips .csv;
 *                             tele_events.jsonl when a side has dots; tele_turns.csv with --tele-turns) into DIR
 *   --tele                    telemetry check of one game: status per side, offset, sync, agreement, records, states
 *   --fingerprint             one line per game: game map rounds state_sha1 bytecode_sha1 (indicators excluded)
 *   --decode-record KIND A B C D [--type T]   the tele_events.jsonl JSON of one data-dot record (no replay file)
 *   --checks                  model identities (hp never above max, team totals = HQ banks + cargo, hit pairing)
 * --census appends the columns of TELEMETRY.md B.5 after `counters`. Legacy columns keep their meaning: `dmg` credits
 * every negative CHANGE_HEALTH (HQ aura included) to the other team and leaves out lethal damage, and `kills` counts
 * any death that had a hit in the same round. New tools use `dmg_hits` and `kills_hits`.
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
        // ---- deep model (TELEMETRY.md B.2); maintained only when ReplayDump.deep is set
        int bornX, bornY, preX, preY, hp2, hpStart, anc, turnIdx = -1, turnRound = -1;
        final int[] inv = new int[3], deathCargo = new int[3];
        Robot killer; boolean killThrow, deathDone; int hpBefore, cause = -1, deathAnc;
        int fireRound = -1, fireTgt;
        int curCode = -1, curCodeRound = -1, lastCode = -1;
        int[] codeCnt;                         // per code, telemetry sides only
        int nTurns, bcMax2, bcOver2, bcNear2;
        int stillLen, stillStart, maxStill2, stillR0 = -1;
        int engId = -1, lastCellRound = -1000, inCellRound = -1, deathEng = -1;
        int nodeStamp = -1, nodeIdx;
        Trip trip; int depRound = -1, depAmt, collRound = -1;
        int builtRound = -1;                   // HQ: built a robot or an anchor this round
        int[] hqB;                             // HQ bucket: built C, L, A, K, pressure34, pressure9, idle_funds
        TreeMap<Character, Integer> hqCodes;
        int hitStamp = -1, hitCount;           // hits taken this round (focus)
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
    final long[][][] stateCount = new long[3][NT][128];
    // micro (launchers): [team][0 rounds,1 contact,2 fired|contact,3 moved|contact,4 exposed at end,5 dmg taken in
    // contact,6 fired total,7 contact with fighter,8 fired|fighter contact,9 ended in reach of a ready-to-fire fighter]
    final long[][] micro = new long[3][10];    // [team][type][first char of the indicator note]
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

    // a match file holds one game per map (galaxy matches: 3 to 10); every view reads one game (--game N, 0-based)
    final java.util.List<String> gameList = new ArrayList<>();

    ReplayDump(String file) throws IOException { this(file, 0); }

    ReplayDump(String file, int game) throws IOException { this(load(file), game); }

    static GameWrapper load(String file) throws IOException { return GameWrapper.getRootAsGameWrapper(ByteBuffer.wrap(read(file))); }

    /** One game's model over an already decompressed file (--extract decompresses once for every game). */
    ReplayDump(GameWrapper gw0, int game) {
        gw = gw0;
        gameIdx = game;
        int gi = -1;
        String curMap = "?";
        for (int i = 0; i < gw.eventsLength(); i++) {
            EventWrapper ew = gw.events(i);
            byte t = ew.eType();
            if (t == Event.MatchHeader) { gi++; curMap = ((MatchHeader) ew.e(new MatchHeader())).map().name(); }
            if (t == Event.MatchFooter) {
                MatchFooter f0 = (MatchFooter) ew.e(new MatchFooter());
                gameList.add(gi + " " + curMap + " " + (f0.winner() == 1 ? "A" : f0.winner() == 2 ? "B" : "-") + " " + f0.totalRounds());
            }
            if (t != Event.GameHeader && t != Event.GameFooter && gi != game) continue;
            if (t == Event.GameHeader) {
                GameHeader h = (GameHeader) ew.e(new GameHeader());
                for (int k = 0; k < h.teamsLength(); k++) {
                    TeamData td = h.teams(k);
                    if (td.teamID() == 1) teamA = td.name(); else teamB = td.name();
                }
                for (int k = 0; k < h.bodyTypeMetadataLength(); k++) {
                    BodyTypeMetadata m = h.bodyTypeMetadata(k);
                    if (m.type() >= 0 && m.type() < NT) maxHp[m.type()] = m.health();
                    if (m.type() >= 0 && m.type() < NT && m.bytecodeLimit() > 0) lim[m.type()] = m.bytecodeLimit();
                }
            } else if (t == Event.MatchHeader) {
                MatchHeader mh = (MatchHeader) ew.e(new MatchHeader());
                if (mh.maxRounds() > 0) maxRounds = mh.maxRounds();
                GameMap g = mh.map();
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
        r.bornX = r.preX = x; r.bornY = r.preY = y; r.hp2 = r.hpStart = maxHp[type]; r.stillStart = round;
        alive.add(r);
        if (deep) deepSpawn(r, round);
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
        if (deep) deepInit();
        for (Round r : rounds) {
            int rn = r.roundID();
            if (deep) deepBegin(r);
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
                if (str.length() > 0 && str.charAt(0) < 128) stateCount[rb.team][rb.type][str.charAt(0)]++;
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
            // micro: contact is judged on positions at the end of the previous round (what the launcher saw)
            microRound(r);
            // navigation statistics for living mobile robots
            for (Robot rb : robots.values()) {
                if (rb.died >= 0 || rb.born >= rn || rb.type == 0) continue;
                aliveTurns[rb.team][rb.type]++;
                boolean moved = rb.px >= 0 && (rb.px != rb.x || rb.py != rb.y);
                if (moved) { moveTurns[rb.team][rb.type]++; rb.stillRun = 0; }
                else { rb.stillRun++; rb.maxStill = Math.max(rb.maxStill, rb.stillRun); }
                if (moved && rb.ppx == rb.x && rb.ppy == rb.y) aba[rb.team][rb.type]++;
            }
            if (deep) deepRound(r);
            for (int[] sr : snapRounds) if (sr[0] == rn) snaps.put(rn, snapshot());
            if (perRound != null) perRound.accept(rn);
        }
        if (!snaps.containsKey(totalRounds)) snaps.put(totalRounds, snapshot());
        if (deep) deepFinish();
    }

    void microRound(Round r) {
        java.util.HashSet<Integer> fired = new java.util.HashSet<>();
        java.util.HashMap<Integer, Integer> dmg = new java.util.HashMap<>();
        for (int k = 0; k < r.actionsLength(); k++) {
            // a shot counts only if it hit a robot: some bots fire every round at empty tiles (blind fire), which is
            // not combat (diag-top4: awesomelemonade launchers fired at fixed empty tiles every round)
            if (r.actions(k) == Action.LAUNCH_ATTACK && r.actionTargets(k) >= 0) fired.add(r.actionIDs(k));
            if (r.actions(k) == Action.CHANGE_HEALTH && r.actionTargets(k) < 0) dmg.merge(r.actionIDs(k), -r.actionTargets(k), Integer::sum);
        }
        java.util.List<Robot> alive = new java.util.ArrayList<>();
        for (Robot rb : robots.values()) if (rb.died < 0 || rb.died == r.roundID()) alive.add(rb);
        for (Robot rb : alive) {
            if (rb.type != 2 || rb.px < 0 || rb.born >= r.roundID()) continue;
            int t = rb.team;
            boolean contact = false, fighter = false, exposed = false;
            for (Robot e : alive) {
                if (e.team == t || e.px < 0 || e.type == 0) continue;
                int d0 = G2(rb.px, rb.py, e.px, e.py);
                if (d0 <= 16) { contact = true; if (e.type == 2 || e.type == 4) fighter = true; }
                if ((e.type == 2) && e.died < 0 && G2(rb.x, rb.y, e.x, e.y) <= 16) exposed = true;
            }
            micro[t][0]++;
            boolean f = fired.contains(rb.id), mv = rb.px != rb.x || rb.py != rb.y;
            if (f) micro[t][6]++;
            if (contact) {
                micro[t][1]++;
                if (f) micro[t][2]++;
                if (mv) micro[t][3]++;
                micro[t][5] += dmg.getOrDefault(rb.id, 0);
            }
            if (fighter) { micro[t][7]++; if (f) micro[t][8]++; }
            if (exposed && rb.died < 0) micro[t][4]++;
        }
    }

    static int G2(int x1, int y1, int x2, int y2) { int dx = x1 - x2, dy = y1 - y2; return dx * dx + dy * dy; }

    String microShares(int t) {
        long[] m = micro[t];
        if (m[0] == 0) return "";
        return String.format("contact=%.3f hit|contact=%.3f hit|fighter=%.3f move|contact=%.3f exposed=%.3f dmg/contact=%.1f hit=%.3f",
            ratio(m[1], m[0]), ratio(m[2], m[1]), ratio(m[8], m[7]), ratio(m[3], m[1]), ratio(m[4], m[0]),
            m[1] == 0 ? 0.0 : (double) m[5] / m[1], ratio(m[6], m[0]));
    }

    int[][] snapshot() {
        int[][] s = new int[3][10];
        for (int t = 1; t <= 2; t++) {
            s[t][0] = teamRes[t][0]; s[t][1] = teamRes[t][1]; s[t][2] = teamRes[t][2];
            s[t][8] = (int) collected[t][0]; s[t][9] = (int) collected[t][1];   // cumulative Ad, Mn collected
        }
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
        + "L_end,C_end,bc_max_C,bc_max_L,bc_max_HQ,near,over,still_L,still_C,aba,sym_robots,sym_wrong,sym_first_decided,sym_undecided,"
        + "C100,L100,cAd100,cMn100,C250,L250,cAd250,cMn250,states_C,micro_L,counters";

    void census(PrintStream o, boolean header) {
        deep = true;
        run(null);
        if (header) o.println(CENSUS_HDR_ALL);
        for (String row : censusRows()) o.println(row);
    }

    /** The census rows (team A, then B) of a model that has run with `deep` set: the legacy columns, then B.5's. */
    List<String> censusRows() {
        List<String> rows = new ArrayList<>();
        for (int t = 1; t <= 2; t++) {
            int[][] s500 = snaps.get(500), s1000 = snaps.get(1000), s1500 = snaps.get(1500), s250 = snaps.get(250), sEnd = snaps.get(totalRounds);
            long near = 0, over = 0, exc = 0;
            for (int ty = 0; ty < NT; ty++) { near += bcNear[t][ty]; over += bcOver[t][ty]; exc += diedExc[t][ty]; }
            StringBuilder cs = new StringBuilder();
            for (Map.Entry<String, Long> e : counterTotals(t).entrySet()) cs.append(e.getKey()).append('=').append(e.getValue()).append(';');
            rows.add(String.join(",", mapName, t == 1 ? teamA : teamB, side(t), winner == t ? "1" : "0", "" + totalRounds,
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
                "" + (aba[t][1] + aba[t][2]), "" + symStats(t)[0], "" + symStats(t)[1], "" + symStats(t)[2], "" + symStats(t)[3],
                snapCol(100, t, 4), snapCol(100, t, 5), snapCol(100, t, 8), snapCol(100, t, 9),
                snapCol(250, t, 4), snapCol(250, t, 5), snapCol(250, t, 8), snapCol(250, t, 9), stateShares(t, 1), microShares(t), cs.toString())
                + "," + String.join(",", deepCensusCols(t)));
        }
        return rows;
    }

    /** A snapshot column, blank when the game ended before that round. */
    String snapCol(int round, int team, int idx) {
        int[][] sn = snaps.get(round);
        return sn == null ? "" : "" + sn[team][idx];
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

    /** "C:G=.31 C=.25 ..." state-token shares for one team and type, from the first character of the note. */
    String stateShares(int t, int ty) {
        long tot = 0;
        for (long c : stateCount[t][ty]) tot += c;
        if (tot == 0) return "";
        StringBuilder sb = new StringBuilder();
        for (int ch = 33; ch < 127; ch++) {
            long c = stateCount[t][ty][ch];
            if (c * 100 >= tot) sb.append((char) ch).append('=').append(String.format("%.2f", (double) c / tot)).append(' ');
        }
        return sb.toString().trim();
    }

    void states(PrintStream o) {
        run(null);
        for (int t = 1; t <= 2; t++) o.printf("%s LAUNCHER micro: %s%n", side(t), microShares(t));
        for (int t = 1; t <= 2; t++) for (int ty = 0; ty < NT; ty++) {
            String sh = stateShares(t, ty);
            if (!sh.isEmpty()) o.printf("%s %-12s %s%n", side(t), TN[ty], sh);
        }
    }

    void islands(PrintStream o) {
        listener = (rn, line) -> { if (line.startsWith("island ") || line.contains("PLACE_ANCHOR")) o.printf("r%-5d %s%n", rn, line); };
        run(null);
        o.printf("final island owners:");
        for (int i = 1; i <= nIslands; i++) o.printf(" %d:%s", i, islandOwner[i] == 0 ? "-" : side(islandOwner[i]));
        o.println();
    }

    // ================================================================ part B: the deep model (docs/TELEMETRY.md)
    // Shared constants of TELEMETRY.md section 1 (the bot's src/bot/Telemetry.java holds the same values).
    static final int MAGIC = 0x7E1E0001, SYNC_CODE = 42, BCC_GUARD = 300;
    static final String ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_";
    static final String LET_C = "!GCWSXRDFVTKQEYP", LET_L = "NFHMSGW!", LET_HQ = ".bgpwcastx?????!", LET_A = "FCSH";
    static final int[] VALUE = {0, 50, 45, 45, 200, 150};      // unit value (resource cost); HQ 0
    static final String[] OBJ_NAMES = {"sighting", "enemy_island", "enemy_hq", "centre"};
    static final String[] DIR9 = {"CENTER", "NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST"};
    // map currents index Direction.DIRECTION_ORDER {CENTER, WEST, NORTHWEST, NORTH, NORTHEAST, EAST, SOUTHEAST, SOUTH, SOUTHWEST}
    static final int[] CUR_DX = {0, -1, -1, 0, 1, 1, 1, 0, -1}, CUR_DY = {0, 0, 1, 1, 1, 0, -1, -1, -1};
    static final String[] CAUSES = {"launcher", "throw", "destab", "hq_aura", "self", "resign"};
    static final int C_LAUNCHER = 0, C_THROW = 1, C_DESTAB = 2, C_AURA = 3, C_SELF = 4, C_RESIGN = 5;
    static final String[] PHASES = {"all", "open", "mid", "late"};
    static final String[] KITE = {"stand_fire", "fire_retreat", "stepin_fire", "fire_ambiguous", "advance", "retreat", "hold"};
    static final String[] SYM_NAMES = {"ROT", "HORIZ", "VERT"};

    static final String CENSUS_HDR_T1 = "win_reason,tele,tele_offset,tele_agree,tele_exc_turns,tstates_C,tstates_L,tstates_HQ,tstates_A,"
        + "tele_carrier_mn,tele_L_out,deaths_launcher,deaths_throw,deaths_destab,deaths_aura,deaths_self,deaths_resign,value_lost,"
        + "cargo_lost_Ad,cargo_lost_Mn,anchors_lost,spawn_kills,dmg_hits,kills_hits,dmg_aura,kills_aura,eng_n,eng_won,eng_lost,"
        + "eng_n_par,eng_won_par,eng_n_ahead,eng_won_ahead,eng_n_behind,eng_won_behind,exch_ratio,first_hit_rate,turn_round,"
        + "lock_round,onset_L,onset_Mn,onset_value,onset_islands,idle_funds";
    static final String CENSUS_HDR_T2 = "kite_stand_fire,kite_fire_retreat,kite_stepin_fire,kite_fire_ambiguous,kite_advance,"
        + "kite_retreat,kite_hold,exposed_end,alone20,group_p50,trip_cycle_p50,partial_loads,carriers_per_well,blind_rate,focus,"
        + "kill_conv,first_builds";
    static final String CENSUS_HDR_ALL = CENSUS_HDR + "," + CENSUS_HDR_T1 + "," + CENSUS_HDR_T2;

    static final String GAMES_HDR = "match,game,map,width,height,symmetry,islands,rounds,side,team,won,win_reason,tb_margin,vtb500,"
        + "vtb1000,vtb1500,tele,tele_offset,tele_sync_n,tele_sync,tele_agree_n,tele_agree,tele_valid,tele_invalid,tele_exc_turns,"
        + "tele_dots,tele_unknown_kinds";
    static final String DEATHS_HDR = "match,game,round,id,side,type,age,x,y,prog,cause,killer_id,killer_type,hp_before,cargo_Ad,"
        + "cargo_Mn,cargo_Ex,anchors,spawn_kill,eng,last_code,last_token";
    static final String ENG_HDR = "match,game,eng,r0,r1,dur,x0,y0,prog0,nA0,nB0,hpA0,hpB0,peakA,peakB,joinA,joinB,first_hit,"
        + "dmg_by_A,dmg_by_B,kills_by_A,kills_by_B,val_lost_A,val_lost_B,aura_dmg_A,aura_dmg_B,surv_A,surv_B,held,result,codes_A,codes_B";
    static final String TIMELINE_HDR = "match,game,round,side,alive_C,alive_L,alive_A,alive_D,alive_B,built_C,built_L,built_A,coll_Ad,"
        + "coll_Mn,coll_Ex,bank_Ad,bank_Mn,bank_Ex,carried_Ad,carried_Mn,carried_Ex,army_value,value_lost,dmg_dealt,kills,islands,"
        + "anchors_placed,in_contact";
    static final String HQ_HDR = "match,game,round,side,hq_id,x,y,bank_Ad,bank_Mn,bank_Ex,built_C,built_L,built_A,built_K,"
        + "pressure34,pressure9,idle_funds,codes";
    static final String ROBOTS_HDR = "match,game,id,side,type,born,died,cause,x_born,y_born,turns,max_still,still_r0,bc_max,bc_over,"
        + "bc_near,codes";
    static final String STATES_HDR = "match,game,side,type,phase,code,letter,detail,turns,share,src_bcc,src_str";
    static final String TURNS_HDR = "match,game,round,id,side,type,used,code_bcc,code_str,sync";
    static final String TRIPS_HDR = "match,game,side,carrier,t0,first_collect,last_collect,t_end,well_x,well_y,well_type,collects,"
        + "load,wait_rounds,outcome,codes";

    /** The letter of a 6-bit code for a body type (TELEMETRY.md 1.1); '?' = invalid for that type. */
    static char letter(int type, int code) {
        if (code < 0 || code > 63) return '?';
        switch (type) {
            case 0: return LET_HQ.charAt(code & 15);
            case 1: return code >= 32 ? '?' : LET_C.charAt(code >> 1);
            case 2: return LET_L.charAt(code & 7);
            case 3: return code == 63 ? '!' : code >= 60 ? '?' : LET_A.charAt(code & 3);
            default: return code == 0 ? 'O' : code == 1 ? '!' : '?';
        }
    }

    /** tele_states.csv `detail`: the fields of a code other than its letter. */
    static String detail(int type, int code) {
        switch (type) {
            case 0: return "threat=" + ((code >> 4) & 1) + ";anchor=" + ((code >> 5) & 1);
            case 1: return code >= 32 ? "" : "role=" + ((code & 1) == 1 ? "Mn" : "Ad");
            case 2: return "obj=" + OBJ_NAMES[(code >> 3) & 3] + ";out=" + ((code >> 5) & 1);
            case 3: return code >= 60 ? "" : "n=" + (code >> 2);
            default: return "";
        }
    }

    // ---- record decoding (TELEMETRY.md A.6): one spec per kind, fields "name:<word><offset>:<width>[:mod]"
    // words a..d; width 32 = the whole word as a signed int; mods: L loc12 -> [x,y] or null, T type letter, K the code's
    // letter (token) for the emitting robot's type, M value-1, I 255 -> -1, R role-change reason name, D direction name
    static final String[] KIND_NAMES = {"HDR", "EXC", "NM", "OVR", "CNT", "CNTT", "CNTM", "SYM", "ROLE", "WELL", "TRIP", "FLEE",
        "ANCH", "OBJ", "FIGHT", "HQS", "BUG"};
    static final String[] KIND_SPEC = {
        "version:a0:16 type:b0:8:T spawn_round:b8:16 spawn:c0:12:L roles:c12:2 micro:c14:1 army:c15:1 spawn_safety:c16:1 "
            + "launcher_batch:c17:3 padk:d0:8 sync:d8:8 build:d16:16",
        "site:a0:4 gae_type:a4:8 phase:a12:4 code:a16:6 token:a16:6:K r0:b0:32 round_now:c0:32 exc_class:d0:32",
        "work:a0:16 t1:a16:16 code:b0:6 token:b0:6:K enemy_fighters:b8:8 ally_fighters:b16:8 nearby:b24:8 pending_tiles:c0:16 "
            + "enemies:c16:8 r0:d0:32",
        "r0:a0:32 round_now:b0:32 code:c0:6 token:c0:6:K phase:c8:4 work:d0:32",
        "ov:a0:16 ex:a16:16 nm:b0:16 max_bc:b16:16 wall_hits:c0:16 stall_flips:c16:16 edge_flips:d0:16 budget_flips:d16:16",
        null,   // CNTT: 16-bit pairs named by type
        "cand:a0:3 decided_round:a4:12:M sym_conflicts:a16:16 writes:b0:16 refused_writes:b16:16 max_pending:c0:16 seen_wells:c16:8 "
            + "max_unreported:c24:8 tele_max_cost:d0:16 tele_errors:d16:8 tele_deferrals:d24:8",
        "eliminated:a0:3 evidence:a4:3 cand_after:a8:3 conflict:a12:1 at:b0:32:L r0:c0:32 sym_conflicts:d0:32",
        "old:a0:4 new:a4:4 reason:a8:4:R hq_ad:b0:32 hq_mn:c0:32 hq:d0:12:L trips:d12:16",
        "well:a0:12:L well_type:a12:2 source:a14:3 role:a17:2 d2:b0:32 shared_wells:c0:8 seen_wells:c8:8 search_turns:c16:16 "
            + "crowd_turns:d0:8 prev_well:d8:12:L",
        "well:a0:12:L well_type:a12:2 role:a14:2 load:a16:8 hq:a24:2 t_start:b0:16 t_first_collect:b16:16 t_last_collect:c0:16 "
            + "t_deposit:c16:16 wait:d0:8 explore:d8:8 flee:d16:8 collect:d24:8",
        "threat_d2:a0:8 enemy_fighters:a8:8 hp:a16:8 threw:a24:1 moved:a25:1 threat:b0:12:L weight:b12:8 home:c0:32:L r0:d0:32",
        "event:a0:4 island:a4:8:I source:a12:2 enemy_side:a14:1 target:b0:12:L anchor_turns:b12:12 d2:c0:16 r0:d0:32",
        "obj_kind:a0:4 sighting_age:a4:4 ally_launchers:a8:8 enemy_fighters:a16:8 island:a24:8 objective:b0:32:L at:c0:32:L r0:d0:32",
        "ready:a0:1 superior:a1:1 outnumbered:a2:1 any_can_hit:a3:1 moved:a4:1 dir:a5:4:D guard_break:a9:1 micro:a10:1 "
            + "shots_before:a12:2 shots_after:a14:2 enemy_fighters:a16:8 ally_fighters:a24:8 threat:b0:8 can_hit:b8:1 min_d2:b16:8 "
            + "pinned:b24:8 stay_threat:c0:8 stay_can_hit:c8:1 stay_min_d2:c16:8 tiles:c24:4 hp:d0:8 enemies:d8:8 target:d16:16",
        "ad:a0:16 mn:a16:16 ex:b0:16 robots:b16:16 carriers_built:c0:8 launchers_built:c8:8 amps_built:c16:8 anchors_built:c24:8 "
            + "shared_wells:d0:8 carrier_cap:d8:8 float_rounds:d16:16",
        "moves:a0:16 flips:a16:8 reason:a24:4 target:b0:12:L start:b12:12:L start_round:c0:16 r0:c16:16 start_d2:d0:16 exit_d2:d16:16",
    };
    /** CNTT pair names (a.lo, a.hi, b.lo, ... d.hi) by type: HQ, carrier, launcher; other types print "v". */
    static final String[][] CNTT_NAMES = {
        {"carriers_built", "launchers_built", "amps_built", "anchors_built", "float_rounds"},
        {"trips", "fled", "throws", "anchors_placed", "anchors_returned", "crowd_switches", "wait_turns", "explore_turns"},
        {"shots", "stepped_in", "kited", "pinned_seen", "unsafe_avoided", "regroups", "follows", "guard_breaks"}};
    static final int COMMS0 = 24;

    static String locJson(int v) { return v <= 0 ? "null" : "[" + (v - 1) / 64 + "," + (v - 1) % 64 + "]"; }

    static String kindName(int kind) {
        if (kind >= 0 && kind < KIND_NAMES.length) return KIND_NAMES[kind];
        if (kind >= COMMS0 && kind < COMMS0 + 8) return "COMMS";
        return "K" + kind;
    }

    static boolean knownKind(int kind) { return (kind >= 0 && kind < KIND_NAMES.length) || (kind >= COMMS0 && kind < COMMS0 + 8); }

    /**
     * The JSON members of one record, starting with "kind" (no braces). type = the emitting robot's body type (-1 =
     * unknown: tokens print null and CNTT prints its raw pairs). inJsonl: HDR's own "type" is dropped when it equals the
     * common key (it is printed as "hdr_type" when it differs). A single COMMS chunk prints its 64-slot array with nulls.
     */
    static String decodeFields(int kind, int a, int b, int c, int d, int type, boolean inJsonl) {
        int[] w = {a, b, c, d};
        StringBuilder sb = new StringBuilder("\"kind\":\"").append(kindName(kind)).append('"');
        if (kind == 5) {
            String[] names = type >= 0 && type <= 2 ? CNTT_NAMES[type] : null;
            if (names == null) {
                sb.append(",\"v\":[");
                for (int i = 0; i < 8; i++) sb.append(i == 0 ? "" : ",").append((w[i / 2] >>> (16 * (i % 2))) & 0xFFFF);
                sb.append(']');
            } else for (int i = 0; i < names.length; i++) sb.append(",\"").append(names[i]).append("\":").append((w[i / 2] >>> (16 * (i % 2))) & 0xFFFF);
        } else if (kind >= 0 && kind < KIND_SPEC.length) {
            for (String f : KIND_SPEC[kind].split(" ")) {
                String[] p = f.split(":");
                int word = p[1].charAt(0) - 'a', off = Integer.parseInt(p[1].substring(1)), width = Integer.parseInt(p[2]);
                String mod = p.length > 3 ? p[3] : "";
                int v = width == 32 ? w[word] : (w[word] >>> off) & ((1 << width) - 1);
                String name = p[0];
                if (mod.equals("T") && inJsonl) { if (v == type) continue; name = "hdr_type"; }
                sb.append(",\"").append(name).append("\":");
                switch (mod) {
                    case "L": sb.append(locJson(v)); break;
                    case "T": sb.append(v >= 0 && v < NT ? "\"" + TC[v] + "\"" : "" + v); break;
                    case "K": sb.append(type >= 0 && type < NT ? "\"" + letter(type, v) + "\"" : "null"); break;
                    case "M": sb.append(v - 1); break;
                    case "I": sb.append(v == 255 ? -1 : v); break;
                    case "R": sb.append(v == 0 ? "\"spawn\"" : v == 1 ? "\"hq_stock\"" : "" + v); break;
                    case "D": sb.append(v < DIR9.length ? "\"" + DIR9[v] + "\"" : "" + v); break;
                    default: sb.append(v);
                }
            }
        } else if (kind >= COMMS0 && kind < COMMS0 + 8) {
            int[] slots = new int[64];
            boolean[] has = new boolean[64];
            for (int i = 0; i < 8; i++) { slots[(kind - COMMS0) * 8 + i] = (w[i / 2] >>> (16 * (i % 2))) & 0xFFFF; has[(kind - COMMS0) * 8 + i] = true; }
            sb.append(",\"slots\":").append(slotsJson(slots, has));
        }
        return sb.toString();
    }

    static String slotsJson(int[] slots, boolean[] has) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < 64; i++) sb.append(i == 0 ? "" : ",").append(has[i] ? "" + slots[i] : "null");
        return sb.append(']').toString();
    }

    // ---- model classes
    static final class Hit { Robot att, vic; int dmg, idx, round; boolean lethal, thr; }

    static final class Trip {
        Robot c; int t0, first = -1, last = -1, tEnd, load, collects; String outcome;
        final Map<Integer, int[]> wellAmt = new LinkedHashMap<>();   // well loc -> [amount, Ad, Mn, Ex]
        final Map<Integer, int[]> near = new HashMap<>();            // well loc -> [rounds near without collecting, of them after the last collect]
        int[] letters;                                               // per letter char, telemetry sides only
    }

    static final class Eng {
        int id, parent, r0, r1, x0, y0, touchRound = -1, cn, fhRound = -1, fhIdx, fhSide;
        String prog0 = "", held = "-";
        double cx, cy, lcx, lcy;
        boolean done;
        final int[] n0 = new int[3], hp0 = new int[3], peak = new int[3], cntL = new int[3], surv = new int[3];
        final long[] dmgBy = new long[3], killsBy = new long[3], valLost = new long[3], aura = new long[3];
        final List<Set<Integer>> joined = Arrays.<Set<Integer>>asList(null, new HashSet<>(), new HashSet<>());
        final List<TreeMap<String, Integer>> codes = Arrays.<TreeMap<String, Integer>>asList(null, new TreeMap<>(), new TreeMap<>());
    }

    // ---- deep state
    boolean deep;
    int matchId, gameIdx, maxRounds = 2000;
    String prefix = "0,0";
    final int[] lim = BC_LIMIT.clone();
    final List<Robot> alive = new ArrayList<>();
    final List<Robot> hqs = new ArrayList<>();
    final Map<Integer, Robot> hqAt = new HashMap<>();
    int[] distA, distB;
    int[][] wellsNear8;
    Robot[] occR;
    int[] occS;
    int[] isl2 = new int[64];
    final long[] anchorsPlaced2 = new long[3];
    boolean conquest;
    final boolean[] resignSide = new boolean[3];
    // telemetry (B.3)
    final Set<Integer> teleRobots = new HashSet<>();
    final boolean[] dotSide = new boolean[3], bccSide = new boolean[3];
    final int[] kstar = new int[3], nSync = new int[3], sSync = new int[3];
    final double[] offShare = new double[3];     // share of non-sync turns on the sync residue at k*
    final long[] codeTurns = new long[3], invalidN = new long[3], excTurns = new long[3], bothN = new long[3], agreeN = new long[3],
        mismatchN = new long[3], teleDotsN = new long[3], unknownN = new long[3];
    final long[][][][][] stc = new long[3][NT][4][64][2];      // [team][type][phase][code][src 0 bcc, 1 string]
    final long[][] kindN = new long[3][COMMS0 + 1];             // records by kind; COMMS (merged) at COMMS0
    final List<TreeMap<String, Long>> unknownKinds = Arrays.<TreeMap<String, Long>>asList(null, new TreeMap<>(), new TreeMap<>());
    PrintStream eventsOut, turnsOut;
    // per-round scratch
    final List<Hit> roundHits = new ArrayList<>();
    final List<int[]> eorDmg = new ArrayList<>();          // [victim id, amount, class 1 aura 2 destab 3 other]
    final List<Robot> throwers = new ArrayList<>(), nodes = new ArrayList<>();
    final List<int[]> destabs = new ArrayList<>();         // [round, team, x, y]
    final int[] inContactR = new int[3];
    // deaths and damage
    final List<Robot> deaths = new ArrayList<>();
    final long[][] deathsBy = new long[3][6], cargoLost = new long[3][3];
    final long[] valueLost = new long[3], anchorsLost = new long[3], spawnKills = new long[3], dmgHits = new long[3],
        killsHits = new long[3], dmgAura = new long[3], killsAura = new long[3];
    // engagements
    final List<Eng> engs = new ArrayList<>(), openEngs = new ArrayList<>();
    int[] uf = new int[256];
    // tier 2
    final long[][] kite = new long[3][7];
    final long[] contactTurns = new long[3], exposedEnd = new long[3], alone20 = new long[3], shots2 = new long[3],
        blind2 = new long[3], hitsN = new long[3], focusN = new long[3];
    final List<List<Integer>> groupSizes = Arrays.<List<Integer>>asList(null, new ArrayList<>(), new ArrayList<>());
    final List<List<Integer>> cpw = Arrays.<List<Integer>>asList(null, new ArrayList<>(), new ArrayList<>());
    final List<int[]> hitVictims = new ArrayList<>();      // [attacking team, victim id, round]
    final List<Set<Integer>> usedWells = Arrays.<Set<Integer>>asList(null, new LinkedHashSet<>(), new LinkedHashSet<>());
    final List<List<String>> firstBuilds = Arrays.<List<String>>asList(null, new ArrayList<>(), new ArrayList<>());
    final List<Trip> trips = new ArrayList<>();
    // timeline, HQ buckets, game level
    final List<String> timelineRows = new ArrayList<>(), hqRows = new ArrayList<>();
    final List<long[][]> samples = new ArrayList<>();      // [team][round, army value, alive L, coll Mn, value destroyed, islands]
    final long[] idleFunds = new long[3];
    final String[] vtbSide = {"", "", ""};
    String winReason = "other", tbMargin = "", turnRound = "", lockRound = "", onsetL = "", onsetMn = "", onsetValue = "", onsetIslands = "";
    // identities (--checks)
    long hpOverMax, badHits, teamTotalMismatch, invNeg, deadInvNonzero, hpNonposAlive, rounds2;

    // ---- geometry helpers
    static boolean reach1(int px, int py, int qx, int qy) {
        int dx = Math.max(Math.abs(px - qx) - 1, 0), dy = Math.max(Math.abs(py - qy) - 1, 0);
        return dx * dx + dy * dy <= 16;
    }

    boolean enemyHqWithin(int team, int x, int y, int r2) {
        for (Robot h : hqs) if (h.team != team && h.died < 0 && G2(h.x, h.y, x, y) <= r2) return true;
        return false;
    }

    /** Enemy HQs whose r^2 9 aura a robot at (x, y) can reach with two steps (B.2 death cause, hq_aura). */
    int enemyHqsInReach2(int team, int x, int y) {
        int n = 0;
        for (Robot h : hqs) {
            if (h.team == team || h.died >= 0) continue;
            int dx = Math.max(Math.abs(h.x - x) - 2, 0), dy = Math.max(Math.abs(h.y - y) - 2, 0);
            if (dx * dx + dy * dy <= 9) n++;
        }
        return n;
    }

    boolean destabNear(Robot v, int rn) {
        for (int[] d : destabs) if (d[0] == rn - 4 && d[1] != v.team && G2(d[2], d[3], v.preX, v.preY) <= 15) return true;
        return false;
    }

    boolean cur(Robot rb) {
        if (rb.preX < 0 || rb.preX >= W || rb.preY < 0 || rb.preY >= H) return false;
        int c = current[rb.preX + rb.preY * W];
        return c > 0 && c < 9 && rb.x == rb.preX + CUR_DX[c] && rb.y == rb.preY + CUR_DY[c];
    }

    int[] bfs(int team) {
        int n = W * H;
        int[] d = new int[n];
        Arrays.fill(d, -1);
        int[] q = new int[n];
        int qh = 0, qt = 0;
        for (Robot h : hqs) if (h.team == team) { int i = h.x + h.y * W; if (d[i] < 0) { d[i] = 0; q[qt++] = i; } }
        while (qh < qt) {
            int i = q[qh++], x = i % W, y = i / W;
            for (int dx = -1; dx <= 1; dx++) for (int dy = -1; dy <= 1; dy++) {
                int nx = x + dx, ny = y + dy;
                if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
                int j = nx + ny * W;
                if (wall[j] || d[j] >= 0) continue;
                d[j] = d[i] + 1;
                q[qt++] = j;
            }
        }
        return d;
    }

    /** prog(tile) = dA/(dA+dB) over 8-connected non-wall paths from each side's HQs; NaN when unreachable. */
    double prog(int x, int y) {
        if (x < 0 || y < 0 || x >= W || y >= H) return Double.NaN;
        int a = distA[x + y * W], b = distB[x + y * W];
        if (a < 0 || b < 0) return Double.NaN;
        return a + b == 0 ? 0.5 : (double) a / (a + b);
    }

    static String fmtP(double p) { return Double.isNaN(p) ? "" : String.format("%.3f", p); }

    int[] wellsNear(int x, int y) {
        int i = x + y * W;
        if (wellsNear8[i] == null) {
            List<Integer> l = new ArrayList<>();
            for (int k = 0; k < W * H; k++) if (resource[k] > 0 && G2(k % W, k / W, x, y) <= 8) l.add(k);
            int[] a = new int[l.size()];
            for (int k = 0; k < a.length; k++) a[k] = l.get(k);
            wellsNear8[i] = a;
        }
        return wellsNear8[i];
    }

    // ---- deep: setup, per round, finish
    void deepInit() {
        int n = W * H;
        for (Robot rb : robots.values()) if (rb.type == 0) { hqs.add(rb); hqAt.put(rb.x + rb.y * W, rb); rb.hqB = new int[7]; rb.hqCodes = new TreeMap<>(); }
        distA = bfs(1);
        distB = bfs(2);
        wellsNear8 = new int[n][];
        occR = new Robot[n];
        occS = new int[n];
        Arrays.fill(occS, -1);
        isl2 = new int[Math.max(64, nIslands + 1)];
        // prepass (B.3 steps 1-2): which robots carry dot telemetry (first kind-0 record has a == MAGIC), and the
        // bytecode-channel offset per side from the sync turns (round % 50 == 25, used <= limit - 300)
        Map<Integer, int[]> tt = new HashMap<>();
        for (Robot rb : robots.values()) tt.put(rb.id, new int[]{rb.team, rb.type});
        Map<Integer, Boolean> hdr = new HashMap<>();
        int[][] hist = new int[3][64], histOff = new int[3][64];
        int[] nOff = new int[3];
        for (Round r : rounds) {
            SpawnedBodyTable s = r.spawnedBodies();
            if (s != null) for (int k = 0; k < s.robotIDsLength(); k++) tt.put(s.robotIDs(k), new int[]{s.teamIDs(k), s.types(k)});
            int nd = r.indicatorDotIDsLength();
            if (nd > 0) {
                VecTable locs = r.indicatorDotLocs();
                for (int k = 0; k < nd; k++)
                    if (locs.xs(k) == -2 && !hdr.containsKey(r.indicatorDotIDs(k))) hdr.put(r.indicatorDotIDs(k), locs.ys(k) == MAGIC);
            }
            boolean sync = r.roundID() % 50 == 25;
            for (int k = 0; k < r.bytecodeIDsLength(); k++) {
                int[] ti = tt.get(r.bytecodeIDs(k));
                if (ti == null || ti[0] < 1 || ti[0] > 2 || ti[1] < 0 || ti[1] >= NT) continue;
                int used = r.bytecodesUsed(k);
                if (used > lim[ti[1]] - BCC_GUARD) continue;
                if (!sync) { nOff[ti[0]]++; histOff[ti[0]][(used - SYNC_CODE) & 63]++; continue; }
                nSync[ti[0]]++;
                hist[ti[0]][(used - SYNC_CODE) & 63]++;
            }
        }
        for (Map.Entry<Integer, Boolean> e : hdr.entrySet()) {
            if (!e.getValue()) continue;
            teleRobots.add(e.getKey());
            int[] ti = tt.get(e.getKey());
            if (ti != null && ti[0] >= 1 && ti[0] <= 2) dotSide[ti[0]] = true;
        }
        for (int t = 1; t <= 2; t++) {
            int best = 0;
            for (int k = 1; k < 64; k++) if (hist[t][k] > hist[t][best]) best = k;
            kstar[t] = best;
            sSync[t] = hist[t][best];
            // B.3 step 2, plus a guard the design's 1/64 collision argument leaves out: a bot whose robots spend the
            // same bytecodes every turn concentrates its residues on sync and non-sync turns alike (examplefuncsplayer
            // puts 30% of its sync turns on one residue), while a telemetry side pads sync turns only
            offShare[t] = nOff[t] == 0 ? 0 : (double) histOff[t][best] / nOff[t];
            bccSide[t] = nSync[t] >= 10 && sSync[t] >= 0.9 * nSync[t] && offShare[t] < 0.5;
        }
    }

    boolean teleSide(int t) { return t >= 1 && t <= 2 && (dotSide[t] || bccSide[t]); }

    String teleStatus(int t) { return dotSide[t] && bccSide[t] ? "both" : dotSide[t] ? "dots" : bccSide[t] ? "bcc" : "none"; }

    void deepSpawn(Robot r, int round) {
        if (r.type == 1) openTrip(r, round);
        if (round > 0) addFirstBuild(r.team, round, TC[r.type]);
    }

    void addFirstBuild(int team, int round, char t) {
        if (team >= 1 && team <= 2 && firstBuilds.get(team).size() < 12) firstBuilds.get(team).add(round + ":" + t);
    }

    void openTrip(Robot c, int round) {
        Trip t = new Trip();
        t.c = c;
        t.t0 = round;
        c.trip = t;
    }

    void tripCollect(Trip t, int rn, int well, int res, int amt) {
        if (t.first < 0) t.first = rn;
        t.last = rn;
        t.collects += amt;
        int[] w = t.wellAmt.computeIfAbsent(well, z -> new int[4]);
        w[0] += amt;
        w[1 + res] += amt;
        for (int[] c : t.near.values()) c[1] = 0;
    }

    void closeTrip(Robot c, int rn, String outcome, int load) {
        Trip t = c.trip;
        if (t == null) return;
        t.tEnd = rn;
        t.outcome = outcome;
        t.load = load;
        trips.add(t);
        c.trip = null;
    }

    void deepBegin(Round r) {
        for (Robot rb : alive) { rb.preX = rb.x; rb.preY = rb.y; rb.hpStart = rb.hp2; }
    }

    void deepRound(Round r) {
        final int rn = r.roundID();
        final boolean fin = rn == totalRounds;
        rounds2++;
        int nb = r.bytecodeIDsLength();
        for (int k = 0; k < nb; k++) { Robot rb = robots.get(r.bytecodeIDs(k)); if (rb != null) { rb.turnIdx = k; rb.turnRound = rn; } }
        roundHits.clear(); eorDmg.clear(); throwers.clear();
        // ---- actions in order: HP, inventories, hit attribution, builds, anchors, trips (B.2). Engine order: a hit's
        // CHANGE_HEALTH comes right before its LAUNCH/THROW_ATTACK; a lethal hit has none (the victim's death CHANGE_*
        // entries come instead), so a hit not preceded by its victim's damage entry is the lethal one.
        int na = r.actionsLength(), lcId = -1, lcRes = -1, lcAmt = 0;
        for (int k = 0; k < na; k++) {
            int id = r.actionIDs(k), tgt = r.actionTargets(k);
            byte a = r.actions(k);
            Robot rb = robots.get(id);
            if (rb == null) continue;
            int tm = rb.team;
            switch (a) {
                case Action.LAUNCH_ATTACK: case Action.THROW_ATTACK: {
                    boolean thr = a == Action.THROW_ATTACK;
                    if (rb.fireRound != rn) { rb.fireRound = rn; rb.fireTgt = tgt; }
                    if (!thr) { shots2[tm]++; if (tgt < 0) blind2[tm]++; }
                    else if (!throwers.contains(rb)) throwers.add(rb);
                    Robot v = tgt >= 0 ? robots.get(tgt) : null;
                    if (v != null) {
                        Hit h = new Hit();
                        h.att = rb; h.vic = v; h.thr = thr; h.idx = k; h.round = rn;
                        boolean paired = k > 0 && r.actions(k - 1) == Action.CHANGE_HEALTH && r.actionIDs(k - 1) == tgt && r.actionTargets(k - 1) < 0;
                        if (paired) h.dmg = -r.actionTargets(k - 1);
                        else if (v.died == rn && v.killer == null) {
                            h.lethal = true; h.dmg = Math.max(0, v.hp2);
                            v.hpBefore = v.hp2; v.killer = rb; v.killThrow = thr;
                        } else badHits++;
                        roundHits.add(h);
                        dmgHits[tm] += h.dmg;
                        if (h.lethal) killsHits[tm]++;
                        hitsN[tm]++;
                        if (v.hitStamp != rn) { v.hitStamp = rn; v.hitCount = 0; hitVictims.add(new int[]{tm, v.id, rn}); }
                        v.hitCount++;
                    }
                    if (thr && rb.type == 1) {
                        closeTrip(rb, rn, "throw", rb.inv[0] + rb.inv[1] + rb.inv[2]);
                        openTrip(rb, rn);
                    }
                    if (thr) { rb.inv[0] = rb.inv[1] = rb.inv[2] = 0; rb.anc = 0; }
                    break;
                }
                case Action.CHANGE_HEALTH: {
                    rb.hp2 += tgt;
                    if (rb.hp2 > maxHp[rb.type]) hpOverMax++;
                    if (tgt < 0) {
                        boolean paired = k + 1 < na && (r.actions(k + 1) == Action.LAUNCH_ATTACK || r.actions(k + 1) == Action.THROW_ATTACK)
                            && r.actionTargets(k + 1) == id;
                        if (!paired) eorDmg.add(new int[]{id, -tgt, 3});
                    }
                    break;
                }
                case Action.CHANGE_ADAMANTIUM: case Action.CHANGE_MANA: case Action.CHANGE_ELIXIR: {
                    int ri = a == Action.CHANGE_ADAMANTIUM ? 0 : a == Action.CHANGE_MANA ? 1 : 2;
                    rb.inv[ri] += tgt;
                    if (rb.inv[ri] < 0) invNeg++;
                    if (rb.died == rn) rb.deathCargo[ri] = -tgt;   // a death's CHANGE_* entries are the robot's last
                    lcId = id; lcRes = ri; lcAmt = tgt;
                    break;
                }
                case Action.PICK_UP_RESOURCE:
                    if (lcId == id && lcAmt > 0) {
                        if (rb.trip == null && rb.type == 1) openTrip(rb, rn);
                        if (rb.trip != null) tripCollect(rb.trip, rn, tgt, lcRes, lcAmt);
                        rb.collRound = rn;
                        if (tm >= 1 && tm <= 2) usedWells.get(tm).add(tgt);
                    }
                    break;
                case Action.PLACE_RESOURCE: {
                    Robot hq = hqAt.get(tgt);
                    if (hq != null && hq.died < 0 && hq.team == tm && lcId == id && lcAmt < 0 && rb.type == 1) {
                        if (rb.depRound != rn) { rb.depRound = rn; rb.depAmt = 0; }
                        rb.depAmt -= lcAmt;
                    }
                    break;
                }
                case Action.SPAWN_UNIT: {
                    rb.builtRound = rn;
                    Robot nr = robots.get(tgt);
                    if (rb.hqB != null && nr != null && nr.type >= 1 && nr.type <= 3) rb.hqB[nr.type - 1]++;
                    break;
                }
                case Action.BUILD_ANCHOR:
                    rb.builtRound = rn;
                    if (rb.hqB != null) rb.hqB[3]++;
                    addFirstBuild(tm, rn, 'K');
                    break;
                case Action.PICK_UP_ANCHOR:
                    if (tgt >= 0) { rb.anc++; closeTrip(rb, rn, "anchor", 0); }
                    else { rb.anc = Math.max(0, rb.anc - 1); if (rb.trip == null && rb.type == 1 && rb.anc == 0) openTrip(rb, rn); }
                    break;
                case Action.PLACE_ANCHOR: {
                    rb.anc = Math.max(0, rb.anc - 1);
                    if (tgt > 0 && tgt < isl2.length) {
                        if (isl2[tgt] != tm) anchorsPlaced2[tm]++;   // TeamInfo.placeAnchor counts only a change of owner
                        isl2[tgt] = tm;
                        if (fin && tm == winner && nIslands > 0) {
                            int c = 0;
                            for (int i = 1; i <= nIslands; i++) if (isl2[i] == tm) c++;
                            if ((float) c / nIslands >= 0.75f) conquest = true;
                        }
                    }
                    if (rb.trip == null && rb.type == 1 && rb.anc == 0) openTrip(rb, rn);
                    break;
                }
                case Action.DESTABILIZE: destabs.add(new int[]{rn, tm, tgt % W, tgt / W}); break;
                default: break;
            }
        }
        for (Hit h : roundHits) if (h.vic.hitCount >= 2) focusN[h.att.team]++;
        // ---- deaths (B.2 death cause, first rule that matches)
        if (fin) {
            int[] aliveN = new int[3], diedN = new int[3];
            for (Robot rb : alive) if (rb.team >= 1 && rb.team <= 2) { aliveN[rb.team]++; if (rb.died == rn) diedN[rb.team]++; }
            for (int t = 1; t <= 2; t++) resignSide[t] = aliveN[t] > 0 && diedN[t] == aliveN[t] && winner != t;
        }
        int deaths0 = deaths.size();
        for (int k = 0; k < r.diedIDsLength(); k++) {
            Robot v = robots.get(r.diedIDs(k));
            if (v == null || v.died != rn || v.deathDone) continue;
            v.deathDone = true;
            int c;
            if (fin && resignSide[v.team]) c = C_RESIGN;
            else if (v.killer != null) c = v.killThrow ? C_THROW : C_LAUNCHER;
            else if (v.type == 0) c = C_SELF;
            else if (destabNear(v, rn)) c = C_DESTAB;
            else if (enemyHqWithin(v.team, v.preX, v.preY, 9)) c = C_AURA;
            // a robot that stepped into the aura this turn has no recorded in-turn position (dead robots get no
            // end-of-round position): HP within the reachable HQs' 4 per round, and an HQ in reach after two steps
            else if (v.hp2 > 0 && v.hp2 <= 4 * enemyHqsInReach2(v.team, v.preX, v.preY)) c = C_AURA;
            else c = C_SELF;
            if (v.killer == null) v.hpBefore = v.hp2;
            v.cause = c;
            v.deathAnc = v.anc;
            if (v.team < 1 || v.team > 2) continue;
            deathsBy[v.team][c]++;
            valueLost[v.team] += VALUE[v.type];
            for (int i = 0; i < 3; i++) cargoLost[v.team][i] += v.deathCargo[i];
            anchorsLost[v.team] += v.anc;
            if (rn - v.born <= 5 && c != C_SELF && c != C_RESIGN) spawnKills[v.team]++;
            if (c == C_AURA) { dmgAura[3 - v.team] += Math.max(0, v.hpBefore); killsAura[3 - v.team]++; }
            if (v.inv[0] != 0 || v.inv[1] != 0 || v.inv[2] != 0) deadInvNonzero++;
            closeTrip(v, rn, "death", v.deathCargo[0] + v.deathCargo[1] + v.deathCargo[2]);
            deaths.add(v);
        }
        // end-of-round damage (negative CHANGE_HEALTH not paired with a hit)
        for (int[] e : eorDmg) {
            Robot v = robots.get(e[0]);
            int px = v.died == rn ? v.preX : v.x, py = v.died == rn ? v.preY : v.y;
            if (enemyHqWithin(v.team, v.preX, v.preY, 9) || enemyHqWithin(v.team, px, py, 9)) { e[2] = 1; if (v.team >= 1 && v.team <= 2) dmgAura[3 - v.team] += e[1]; }
            else if (destabNear(v, rn)) e[2] = 2;
        }
        // ---- positions: still runs (post vs pre), HP identity
        for (Robot rb : alive) {
            if (rb.died >= 0 || rb.born >= rn) continue;
            if (rb.hp2 <= 0) hpNonposAlive++;
            if (rb.x != rb.preX || rb.y != rb.preY) rb.stillLen = 0;
            else {
                if (rb.stillLen == 0) rb.stillStart = rn;
                rb.stillLen++;
                if (rb.stillLen > rb.maxStill2) { rb.maxStill2 = rb.stillLen; rb.stillR0 = rb.stillStart; }
            }
        }
        // ---- telemetry: one code per robot-turn (B.3 step 3)
        boolean hasStr = r.indicatorStringIDsLength() == nb;
        boolean sync = rn % 50 == 25;
        int phase = rn <= 150 ? 1 : rn <= 600 ? 2 : 3;
        for (int k = 0; k < nb; k++) {
            Robot rb = robots.get(r.bytecodeIDs(k));
            if (rb == null) continue;
            int used = r.bytecodesUsed(k), t = rb.team, ty = rb.type, L = lim[ty];
            rb.nTurns++;
            if (used > rb.bcMax2) rb.bcMax2 = used;
            if (used >= L) rb.bcOver2++; else if (used * 10 >= L * 9) rb.bcNear2++;
            if (!teleSide(t)) continue;
            int cb = -1, cs = -1;
            if (bccSide[t] && !sync && used <= L - BCC_GUARD) cb = (used - kstar[t]) & 63;
            if (hasStr && r.indicatorStringIDs(k) == rb.id) {
                String s = r.indicatorStrings(k);
                if (s != null && s.length() >= 2) {
                    int c = ALPHA.indexOf(s.charAt(1));
                    if (c >= 0) cs = c;
                    if (c < 0 || s.charAt(0) != letter(ty, c)) mismatchN[t]++;
                }
            }
            if (turnsOut != null) turnsOut.println(prefix + "," + rn + "," + rb.id + "," + side(t) + "," + TC[ty] + "," + used + ","
                + (cb < 0 ? "" : "" + cb) + "," + (cs < 0 ? "" : "" + cs) + "," + (sync ? 1 : 0));
            if (cb >= 0 && cs >= 0) { bothN[t]++; if (cb == cs) agreeN[t]++; }
            int best = cb >= 0 ? cb : cs, src = cb >= 0 ? 0 : 1;
            rb.lastCode = best;
            if (best < 0) continue;
            char let = letter(ty, best);
            codeTurns[t]++;
            if (let == '?') invalidN[t]++;
            if (let == '!') excTurns[t]++;
            stc[t][ty][0][best][src]++;
            stc[t][ty][phase][best][src]++;
            rb.curCode = best;
            rb.curCodeRound = rn;
            if (rb.codeCnt == null) rb.codeCnt = new int[64];
            rb.codeCnt[best]++;
            if (rb.hqCodes != null) rb.hqCodes.merge(let, 1, Integer::sum);
            if (rb.trip != null) { if (rb.trip.letters == null) rb.trip.letters = new int[128]; rb.trip.letters[let]++; }
        }
        // ---- engagements (B.4 engagements.csv) and the contact statistics
        engagements(rn, deaths0);
        // ---- trips: deposits close a trip at the end of the round; rounds near a well without collecting
        for (Robot rb : alive) {
            if (rb.type != 1 || rb.died >= 0) continue;
            if (rb.depRound == rn && rb.depAmt > 0 && rb.trip != null) { closeTrip(rb, rn, "deposit", rb.depAmt); openTrip(rb, rn); }
            if (rb.trip != null && rb.collRound != rn)
                for (int w : wellsNear(rb.x, rb.y)) { int[] c = rb.trip.near.computeIfAbsent(w, z -> new int[2]); c[0]++; c[1]++; }
        }
        // ---- occupancy at the end of the round; HQ buckets; wells; timeline
        for (Robot rb : alive) if (rb.died < 0) { int i = rb.x + rb.y * W; if (i >= 0 && i < occS.length) { occR[i] = rb; occS[i] = rn; } }
        for (Robot h : hqs) {
            if (h.died >= 0) continue;
            for (Robot rb : alive) {
                if (rb.died >= 0 || rb.type != 2 || rb.team == h.team) continue;
                int d = G2(rb.x, rb.y, h.x, h.y);
                if (d <= 34) h.hqB[4]++;
                if (d <= 9) h.hqB[5]++;
            }
            if ((h.inv[0] >= 50 || h.inv[1] >= 45) && h.builtRound != rn && freeTile(h, rn)) { h.hqB[6]++; if (h.team >= 1 && h.team <= 2) idleFunds[h.team]++; }
            if (rn % 25 == 0 || fin) {
                StringBuilder cs = new StringBuilder();
                if (teleSide(h.team)) for (Map.Entry<Character, Integer> e : h.hqCodes.entrySet()) cs.append(cs.length() == 0 ? "" : ";").append(e.getKey()).append('=').append(e.getValue());
                hqRows.add(prefix + "," + rn + "," + side(h.team) + "," + h.id + "," + h.x + "," + h.y + "," + h.inv[0] + "," + h.inv[1] + "," + h.inv[2]
                    + "," + h.hqB[0] + "," + h.hqB[1] + "," + h.hqB[2] + "," + h.hqB[3] + "," + h.hqB[4] + "," + h.hqB[5] + "," + h.hqB[6] + "," + cs);
                Arrays.fill(h.hqB, 0);
                h.hqCodes.clear();
            }
        }
        for (int t = 1; t <= 2; t++) for (int w : usedWells.get(t)) {
            int wx = w % W, wy = w / W, own = 0, all = 0;
            for (int dx = -1; dx <= 1; dx++) for (int dy = -1; dy <= 1; dy++) {
                int x = wx + dx, y = wy + dy;
                if (x < 0 || y < 0 || x >= W || y >= H) continue;
                int i = x + y * W;
                if (occS[i] != rn || occR[i].type != 1) continue;
                all++;
                if (occR[i].team == t) own++;
            }
            if (own > 0) cpw.get(t).add(all);
        }
        long[][] bank = new long[3][3], carried = new long[3][3];
        long[] army = new long[3];
        int[][] aliveT = new int[3][NT];
        for (Robot rb : alive) {
            if (rb.died >= 0 || rb.team < 1 || rb.team > 2) continue;
            aliveT[rb.team][rb.type]++;
            army[rb.team] += VALUE[rb.type];
            for (int i = 0; i < 3; i++) { if (rb.type == 0) bank[rb.team][i] += rb.inv[i]; else carried[rb.team][i] += rb.inv[i]; }
        }
        for (int t = 1; t <= 2; t++) for (int i = 0; i < 3; i++) if (bank[t][i] + carried[t][i] != teamRes[t][i]) teamTotalMismatch++;
        int[] isl = new int[3];
        for (int i = 1; i <= nIslands && i < islandOwner.length; i++) if (islandOwner[i] == 1 || islandOwner[i] == 2) isl[islandOwner[i]]++;
        if (rn % 10 == 0 || fin) {
            long[][] s = new long[3][6];
            for (int t = 1; t <= 2; t++) {
                timelineRows.add(prefix + "," + rn + "," + side(t) + "," + aliveT[t][1] + "," + aliveT[t][2] + "," + aliveT[t][3] + "," + aliveT[t][4]
                    + "," + aliveT[t][5] + "," + built[t][1] + "," + built[t][2] + "," + built[t][3] + "," + collected[t][0] + "," + collected[t][1]
                    + "," + collected[t][2] + "," + bank[t][0] + "," + bank[t][1] + "," + bank[t][2] + "," + carried[t][0] + "," + carried[t][1]
                    + "," + carried[t][2] + "," + army[t] + "," + valueLost[t] + "," + dmgHits[t] + "," + killsHits[t] + "," + isl[t]
                    + "," + anchorsPlaced2[t] + "," + inContactR[t]);
                s[t][0] = rn; s[t][1] = army[t]; s[t][2] = aliveT[t][2]; s[t][3] = collected[t][1]; s[t][4] = valueLost[3 - t]; s[t][5] = isl[t];
            }
            samples.add(s);
        }
        if (rn == 500 || rn == 1000 || rn == 1500) vtbSide[rn / 500 - 1] = tbLeader(tbCrit(isl));
        if (fin) tbFinal = tbCrit(isl);
        // ---- islands as they stand at the end of the round (decay), for the next round's placement count
        for (int i = 1; i <= nIslands && i < isl2.length && i < islandOwner.length; i++) isl2[i] = islandOwner[i];
        // ---- data dots of telemetry robots (B.3 step 1)
        int nd = r.indicatorDotIDsLength();
        if (nd > 0 && !teleRobots.isEmpty()) decodeDots(r, rn, nd);
        // ---- engagements that are over: finalised 5 rounds after their last cell (held)
        for (Iterator<Eng> it = openEngs.iterator(); it.hasNext(); ) {
            Eng e = it.next();
            if (e.parent != e.id) { it.remove(); continue; }
            if (rn >= e.r1 + 5) { finalizeEng(e); it.remove(); }
        }
        destabs.removeIf(d -> d[0] < rn - 6);
        alive.removeIf(rb -> rb.died >= 0);
    }

    long[][] tbFinal;

    /** The tiebreak criteria of RULES 8.4 per team: islands owned, anchors placed, Ex, Mn, Ad (team totals). */
    long[][] tbCrit(int[] isl) {
        long[][] c = new long[3][5];
        for (int t = 1; t <= 2; t++) { c[t][0] = isl[t]; c[t][1] = anchorsPlaced2[t]; c[t][2] = teamRes[t][2]; c[t][3] = teamRes[t][1]; c[t][4] = teamRes[t][0]; }
        return c;
    }

    static String tbLeader(long[][] c) {
        for (int k = 0; k < 5; k++) if (c[1][k] != c[2][k]) return c[1][k] > c[2][k] ? "A" : "B";
        return "-";
    }

    boolean freeTile(Robot h, int rn) {
        for (int dx = -3; dx <= 3; dx++) for (int dy = -3; dy <= 3; dy++) {
            if ((dx == 0 && dy == 0) || dx * dx + dy * dy > 9) continue;
            int x = h.x + dx, y = h.y + dy;
            if (x < 0 || y < 0 || x >= W || y >= H) continue;
            int i = x + y * W;
            if (!wall[i] && occS[i] != rn) return true;
        }
        return false;
    }

    // ---- engagements
    int ufFind(int i) { while (uf[i] != i) { uf[i] = uf[uf[i]]; i = uf[i]; } return i; }

    void ufUnion(int a, int b) { a = ufFind(a); b = ufFind(b); if (a != b) { if (a < b) uf[b] = a; else uf[a] = b; } }

    int engFind(int e) {
        while (engs.get(e).parent != e) { Eng x = engs.get(e); x.parent = engs.get(x.parent).parent; e = x.parent; }
        return e;
    }

    void addNode(Robot rb, int rn) {
        if (rb.nodeStamp == rn) return;
        rb.nodeStamp = rn;
        rb.nodeIdx = nodes.size();
        nodes.add(rb);
    }

    void engagements(int rn, int deaths0) {
        inContactR[1] = inContactR[2] = 0;
        nodes.clear();
        for (Robot rb : alive) if (rb.born < rn && (rb.type == 2 || rb.type == 4)) addNode(rb, rn);
        for (Robot t : throwers) addNode(t, rn);
        for (Hit h : roundHits) { addNode(h.att, rn); addNode(h.vic, rn); }
        int n = nodes.size();
        if (n == 0) return;
        if (uf.length < n) uf = new int[2 * n];
        for (int i = 0; i < n; i++) uf[i] = i;
        for (int i = 0; i < n; i++) {
            Robot p = nodes.get(i);
            if (p.team != 1) continue;
            for (int j = 0; j < n; j++) {
                Robot q = nodes.get(j);
                if (q.team == 2 && reach1(p.preX, p.preY, q.preX, q.preY)) ufUnion(i, j);
            }
        }
        for (Hit h : roundHits) ufUnion(h.att.nodeIdx, h.vic.nodeIdx);
        int[] mask = new int[n];
        for (int i = 0; i < n; i++) { int t = nodes.get(i).team; if (t == 1 || t == 2) mask[ufFind(i)] |= t; }
        Map<Integer, List<Robot>> cells = new LinkedHashMap<>();
        for (int i = 0; i < n; i++) { int root = ufFind(i); if (mask[root] == 3) cells.computeIfAbsent(root, z -> new ArrayList<>()).add(nodes.get(i)); }
        if (cells.isEmpty()) return;
        List<Eng> touched = new ArrayList<>();
        for (List<Robot> cell : cells.values()) {
            List<Eng> found = new ArrayList<>();
            for (Robot m : cell) if (m.engId >= 0 && m.lastCellRound >= rn - 3) { Eng e = engs.get(engFind(m.engId)); if (!found.contains(e)) found.add(e); }
            Eng root;
            if (found.isEmpty()) root = newEng(cell, rn);
            else {
                root = found.get(0);
                for (Eng e : found) if (e.r0 < root.r0 || (e.r0 == root.r0 && e.id < root.id)) root = e;
                for (Eng e : found) if (e != root) mergeEng(root, e, rn, touched);
            }
            if (root.touchRound != rn) { root.touchRound = rn; root.cx = root.cy = 0; root.cn = 0; root.cntL[1] = root.cntL[2] = 0; touched.add(root); }
            for (Robot m : cell) {
                m.engId = root.id; m.lastCellRound = rn; m.inCellRound = rn;
                root.cx += m.preX; root.cy += m.preY; root.cn++;
                if (m.type == 2 && (m.team == 1 || m.team == 2)) { root.joined.get(m.team).add(m.id); root.cntL[m.team]++; inContactR[m.team]++; }
            }
        }
        for (Eng e : touched) {
            if (e.parent != e.id || e.cn == 0) continue;
            e.r1 = rn;
            e.lcx = e.cx / e.cn; e.lcy = e.cy / e.cn;
            for (int t = 1; t <= 2; t++) e.peak[t] = Math.max(e.peak[t], e.cntL[t]);
        }
        for (Hit h : roundHits) {
            Eng e = engs.get(engFind(h.att.engId));
            int t = h.att.team;
            if (t < 1 || t > 2) continue;
            e.dmgBy[t] += h.dmg;
            if (h.lethal) e.killsBy[t]++;
            if (e.fhRound < 0) { e.fhRound = rn; e.fhIdx = h.idx; e.fhSide = t; }
        }
        for (int k = deaths0; k < deaths.size(); k++) {
            Robot v = deaths.get(k);
            if (v.inCellRound != rn) continue;
            v.deathEng = v.engId;
            Eng e = engs.get(engFind(v.engId));
            e.valLost[v.team] += VALUE[v.type];
            if (v.cause == C_AURA) e.aura[v.team] += Math.max(0, v.hpBefore);
        }
        for (int[] d : eorDmg) {
            Robot v = robots.get(d[0]);
            if (d[2] == 1 && v.inCellRound == rn && v.team >= 1 && v.team <= 2) engs.get(engFind(v.engId)).aura[v.team] += d[1];
        }
        // launcher turns in a cell: telemetry codes (codes_A) and the Tier 2 contact statistics
        List<List<Robot>> lau = Arrays.<List<Robot>>asList(null, new ArrayList<>(), new ArrayList<>());
        for (Robot m : nodes) if (m.type == 2 && m.born < rn && (m.team == 1 || m.team == 2)) lau.get(m.team).add(m);
        int[][] comp = new int[3][];
        for (Robot m : nodes) {
            if (m.type != 2 || m.inCellRound != rn || m.team < 1 || m.team > 2) continue;
            int t = m.team;
            if (m.curCodeRound == rn && m.curCode >= 0 && teleSide(t)) {
                String key = letter(2, m.curCode) + (((m.curCode >> 5) & 1) == 1 ? "o" : "");
                engs.get(engFind(m.engId)).codes.get(t).merge(key, 1, Integer::sum);
            }
            if (m.turnRound != rn) continue;
            contactTurns[t]++;
            boolean fired = m.fireRound == rn, aliveEnd = m.died < 0;
            boolean moved = aliveEnd && (m.x != m.preX || m.y != m.preY) && !cur(m);
            int cls;
            if (fired && !moved) cls = 0;
            else if (fired) {
                int tx, ty;
                if (m.fireTgt < 0) { int loc = -m.fireTgt - 1; tx = loc % W; ty = loc / W; }
                else {
                    Robot v = robots.get(m.fireTgt);
                    boolean earlier = v != null && v.turnRound == rn && v.turnIdx < m.turnIdx && v.died < 0;
                    tx = v == null ? m.preX : earlier ? v.x : v.preX;
                    ty = v == null ? m.preY : earlier ? v.y : v.preY;
                }
                boolean fromPre = G2(m.preX, m.preY, tx, ty) <= 16, fromPost = G2(m.x, m.y, tx, ty) <= 16;
                cls = fromPre && !fromPost ? 1 : !fromPre && fromPost ? 2 : 3;
            } else if (moved) {
                Robot near = null;
                int best = Integer.MAX_VALUE;
                for (Robot e : lau.get(3 - t)) { int d = G2(m.preX, m.preY, e.preX, e.preY); if (d < best) { best = d; near = e; } }
                if (near == null) for (Robot e : nodes) if (e.team == 3 - t) { int d = G2(m.preX, m.preY, e.preX, e.preY); if (d < best) { best = d; near = e; } }
                cls = near != null && G2(m.x, m.y, near.preX, near.preY) < best ? 4 : 5;
            } else cls = 6;
            kite[t][cls]++;
            if (aliveEnd) for (Robot e : lau.get(3 - t)) if (e.died < 0 && G2(m.x, m.y, e.x, e.y) <= 16) { exposedEnd[t]++; break; }
            boolean alone = true;
            for (Robot o : lau.get(t)) if (o != m && G2(m.preX, m.preY, o.preX, o.preY) <= 20) { alone = false; break; }
            if (alone) alone20[t]++;
            if (comp[t] == null) comp[t] = groupComponents(lau.get(t));
            groupSizes.get(t).add(comp[t][lau.get(t).indexOf(m)]);
        }
    }

    /** For each launcher of the list, the size of its component under r^2 20 (pre positions). */
    int[] groupComponents(List<Robot> l) {
        int n = l.size();
        int[] p = new int[n];
        for (int i = 0; i < n; i++) p[i] = i;
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++)
            if (G2(l.get(i).preX, l.get(i).preY, l.get(j).preX, l.get(j).preY) <= 20) {
                int a = i, b = j;
                while (p[a] != a) a = p[a];
                while (p[b] != b) b = p[b];
                if (a != b) p[Math.max(a, b)] = Math.min(a, b);
            }
        int[] root = new int[n], size = new int[n], out = new int[n];
        for (int i = 0; i < n; i++) { int a = i; while (p[a] != a) a = p[a]; root[i] = a; size[a]++; }
        for (int i = 0; i < n; i++) out[i] = size[root[i]];
        return out;
    }

    Eng newEng(List<Robot> cell, int rn) {
        Eng e = new Eng();
        e.id = engs.size();
        e.parent = e.id;
        e.r0 = e.r1 = rn;
        double cx = 0, cy = 0, ps = 0;
        int pn = 0;
        for (Robot m : cell) {
            cx += m.preX; cy += m.preY;
            double p = prog(m.preX, m.preY);
            if (!Double.isNaN(p)) { ps += p; pn++; }
        }
        cx /= cell.size(); cy /= cell.size();
        e.x0 = (int) Math.round(cx); e.y0 = (int) Math.round(cy);
        e.prog0 = pn == 0 ? "" : fmtP(ps / pn);
        for (Robot rb : alive) {
            if (rb.type != 2 || rb.born >= rn || rb.team < 1 || rb.team > 2) continue;
            double dx = rb.preX - cx, dy = rb.preY - cy;
            if (dx * dx + dy * dy <= 36) { e.n0[rb.team]++; e.hp0[rb.team] += rb.hpStart; }
        }
        engs.add(e);
        openEngs.add(e);
        return e;
    }

    void mergeEng(Eng root, Eng e, int rn, List<Eng> touched) {
        e.parent = root.id;
        for (int t = 1; t <= 2; t++) {
            root.peak[t] = Math.max(root.peak[t], e.peak[t]);
            root.dmgBy[t] += e.dmgBy[t]; root.killsBy[t] += e.killsBy[t]; root.valLost[t] += e.valLost[t]; root.aura[t] += e.aura[t];
            root.joined.get(t).addAll(e.joined.get(t));
            for (Map.Entry<String, Integer> c : e.codes.get(t).entrySet()) root.codes.get(t).merge(c.getKey(), c.getValue(), Integer::sum);
        }
        if (e.fhRound >= 0 && (root.fhRound < 0 || e.fhRound < root.fhRound || (e.fhRound == root.fhRound && e.fhIdx < root.fhIdx))) {
            root.fhRound = e.fhRound; root.fhIdx = e.fhIdx; root.fhSide = e.fhSide;
        }
        root.r1 = Math.max(root.r1, e.r1);
        if (e.touchRound == rn) {   // e already took cells this round: carry them over
            if (root.touchRound != rn) { root.touchRound = rn; root.cx = root.cy = 0; root.cn = 0; root.cntL[1] = root.cntL[2] = 0; touched.add(root); }
            root.cx += e.cx; root.cy += e.cy; root.cn += e.cn; root.cntL[1] += e.cntL[1]; root.cntL[2] += e.cntL[2];
            e.touchRound = -1;
        }
    }

    void finalizeEng(Eng e) {
        e.done = true;
        int[] cnt = new int[3];
        for (Robot rb : alive) {
            if (rb.died >= 0 || rb.type != 2 || rb.team < 1 || rb.team > 2) continue;
            double dx = rb.x - e.lcx, dy = rb.y - e.lcy;
            if (dx * dx + dy * dy <= 36) cnt[rb.team]++;
        }
        e.held = cnt[1] > cnt[2] ? "A" : cnt[2] > cnt[1] ? "B" : "-";
        for (int t = 1; t <= 2; t++) for (int id : e.joined.get(t)) { Robot rb = robots.get(id); if (rb.died < 0 || rb.died > e.r1) e.surv[t]++; }
    }

    static String engResult(Eng e) {
        if (e.valLost[2] > e.valLost[1]) return "A";
        if (e.valLost[1] > e.valLost[2]) return "B";
        if (e.dmgBy[1] > e.dmgBy[2]) return "A";
        if (e.dmgBy[2] > e.dmgBy[1]) return "B";
        return "draw";
    }

    // ---- data dots
    void decodeDots(Round r, int rn, int nd) {
        VecTable locs = r.indicatorDotLocs();
        RGBTable rgb = r.indicatorDotRGBs();
        Map<Integer, int[]> comms = null;          // id -> 64 slots + 64 presence flags
        for (int k = 0; k < nd; k++) {
            int x = locs.xs(k);
            if (x > -2) continue;
            int id = r.indicatorDotIDs(k);
            if (!teleRobots.contains(id)) continue;
            Robot rb = robots.get(id);
            if (rb == null || rb.team < 1 || rb.team > 2) continue;
            int t = rb.team, kind = -2 - x, a = locs.ys(k), b = rgb.red(k), c = rgb.green(k), d = rgb.blue(k);
            teleDotsN[t]++;
            if (kind >= COMMS0 && kind < COMMS0 + 8) {
                if (comms == null) comms = new LinkedHashMap<>();
                int[] s = comms.computeIfAbsent(id, z -> new int[128]);
                int[] w = {a, b, c, d};
                for (int i = 0; i < 8; i++) { s[(kind - COMMS0) * 8 + i] = (w[i / 2] >>> (16 * (i % 2))) & 0xFFFF; s[64 + (kind - COMMS0) * 8 + i] = 1; }
                continue;
            }
            if (knownKind(kind)) kindN[t][kind]++;
            else { unknownN[t]++; unknownKinds.get(t).merge("K" + kind, 1L, Long::sum); }
            if (eventsOut != null) eventsOut.println("{" + commonJson(rn, rb) + "," + decodeFields(kind, a, b, c, d, rb.type, true) + "}");
        }
        if (comms != null) for (Map.Entry<Integer, int[]> e : comms.entrySet()) {
            Robot rb = robots.get(e.getKey());
            kindN[rb.team][COMMS0]++;
            if (eventsOut == null) continue;
            int[] s = e.getValue();
            boolean[] has = new boolean[64];
            for (int i = 0; i < 64; i++) has[i] = s[64 + i] == 1;
            eventsOut.println("{" + commonJson(rn, rb) + ",\"kind\":\"COMMS\",\"slots\":" + slotsJson(Arrays.copyOf(s, 64), has) + "}");
        }
    }

    String commonJson(int rn, Robot rb) {
        return "\"match\":" + matchId + ",\"game\":" + gameIdx + ",\"round\":" + rn + ",\"id\":" + rb.id + ",\"side\":\"" + side(rb.team)
            + "\",\"type\":\"" + TC[rb.type] + "\"";
    }

    // ---- end of game
    void deepFinish() {
        for (Robot rb : alive) if (rb.trip != null) closeTrip(rb, totalRounds, "end", rb.inv[0] + rb.inv[1] + rb.inv[2]);
        for (Eng e : openEngs) if (e.parent == e.id && !e.done) finalizeEng(e);
        openEngs.clear();
        int w = winner, l = 3 - winner;
        if (w == 1 || w == 2) {
            turnRound = fromEnd(i -> samples.get(i)[w][1] > samples.get(i)[l][1]);
            lockRound = fromEnd(i -> { long vw = samples.get(i)[w][1], vl = samples.get(i)[l][1]; return (vw - vl) / (double) Math.max(Math.max(vw, vl), 1) >= 0.33; });
            onsetL = fromEnd(i -> samples.get(i)[w][2] > samples.get(i)[l][2]);
            onsetMn = fromEnd(i -> samples.get(i)[w][3] > samples.get(i)[l][3]);
            onsetValue = fromEnd(i -> samples.get(i)[w][4] > samples.get(i)[l][4]);
            onsetIslands = fromEnd(i -> samples.get(i)[w][5] > samples.get(i)[l][5]);
            if (conquest) winReason = "conquest";
            else if (resignSide[l]) winReason = "resign";
            else if (totalRounds >= maxRounds && tbFinal != null) {
                String[] names = {"tb_islands", "tb_anchors", "tb_ex", "tb_mn", "tb_ad"};
                int k = 0;
                while (k < 5 && tbFinal[1][k] == tbFinal[2][k]) k++;
                if (k == 5) winReason = "coin";
                else if ((tbFinal[w][k] > tbFinal[l][k])) { winReason = names[k]; tbMargin = "" + (tbFinal[w][k] - tbFinal[l][k]); }
                else winReason = "other";
            } else winReason = "other";
        }
    }

    /** The round of the earliest sample from which ok holds at every later sample; blank if not even at the last. */
    String fromEnd(java.util.function.IntPredicate ok) {
        int first = -1;
        for (int i = samples.size() - 1; i >= 0 && ok.test(i); i--) first = i;
        return first < 0 ? "" : "" + samples.get(first)[1][0];
    }

    // ---- output rows (B.4, B.5)
    static String f3(double d) { return String.format("%.3f", d); }

    static String f4(double d) { return String.format("%.4f", d); }

    static String share(long a, long b) { return b == 0 ? "" : f3((double) a / b); }

    static int median(List<Integer> l) {
        List<Integer> s = new ArrayList<>(l);
        Collections.sort(s);
        return s.get(s.size() / 2);
    }

    /** Letter shares of the best codes (>= 1%) for one team and type, in the states_C format; phase 0 = all. */
    String teleShares(int t, int ty, int phase) {
        long[] byLetter = new long[128];
        long tot = 0;
        for (int c = 0; c < 64; c++) { long n = stc[t][ty][phase][c][0] + stc[t][ty][phase][c][1]; byLetter[letter(ty, c)] += n; tot += n; }
        if (tot == 0) return "";
        StringBuilder sb = new StringBuilder();
        for (int ch = 33; ch < 127; ch++) if (byLetter[ch] * 100 >= tot && byLetter[ch] > 0) sb.append((char) ch).append('=').append(String.format("%.2f", (double) byLetter[ch] / tot)).append(' ');
        return sb.toString().trim();
    }

    List<String> deepCensusCols(int t) {
        int o = 3 - t;
        boolean tele = teleSide(t);
        List<String> c = new ArrayList<>();
        c.add(winReason);
        c.add(teleStatus(t));
        c.add(bccSide[t] ? "" + kstar[t] : "");
        c.add(tele && bothN[t] > 0 ? f4((double) agreeN[t] / bothN[t]) : "");
        c.add(tele ? "" + excTurns[t] : "");
        for (int ty : new int[]{1, 2, 0, 3}) c.add(tele ? teleShares(t, ty, 0) : "");
        long mn = 0, ct = 0, out = 0, fh = 0;
        for (int code = 0; code < 64; code++) {
            long nC = stc[t][1][0][code][0] + stc[t][1][0][code][1], nL = stc[t][2][0][code][0] + stc[t][2][0][code][1];
            ct += nC;
            if ((code & 1) == 1 && code < 32) mn += nC;
            char l = letter(2, code);
            if (l == 'F' || l == 'H') { fh += nL; if (((code >> 5) & 1) == 1) out += nL; }
        }
        c.add(tele ? share(mn, ct) : "");
        c.add(tele ? share(out, fh) : "");
        for (int k = 0; k < 6; k++) c.add("" + deathsBy[t][k]);
        c.add("" + valueLost[t]);
        c.add("" + cargoLost[t][0]);
        c.add("" + cargoLost[t][1]);
        c.add("" + anchorsLost[t]);
        c.add("" + spawnKills[t]);
        c.add("" + dmgHits[t]);
        c.add("" + killsHits[t]);
        c.add("" + dmgAura[t]);
        c.add("" + killsAura[t]);
        int n = 0, won = 0, lost = 0, nPar = 0, wPar = 0, nAh = 0, wAh = 0, nBe = 0, wBe = 0, fhN = 0, fhMine = 0;
        long destroyed = 0, lostV = 0;
        for (Eng e : engs) {
            if (e.parent != e.id) continue;
            n++;
            String res = engResult(e);
            boolean w = res.equals(side(t));
            if (w) won++; else if (res.equals(side(o))) lost++;
            int dN = e.n0[t] - e.n0[o];
            if (dN == 0) { nPar++; if (w) wPar++; }
            else if (dN >= 2) { nAh++; if (w) wAh++; }
            else if (dN <= -2) { nBe++; if (w) wBe++; }
            destroyed += e.valLost[o];
            lostV += e.valLost[t];
            if (e.fhRound >= 0) { fhN++; if (e.fhSide == t) fhMine++; }
        }
        for (int v : new int[]{n, won, lost, nPar, wPar, nAh, wAh, nBe, wBe}) c.add("" + v);
        c.add(lostV == 0 ? "" : f3((double) destroyed / lostV));
        c.add(share(fhMine, fhN));
        c.add(turnRound); c.add(lockRound); c.add(onsetL); c.add(onsetMn); c.add(onsetValue); c.add(onsetIslands);
        c.add("" + idleFunds[t]);
        // Tier 2
        for (int k = 0; k < 7; k++) c.add(share(kite[t][k], contactTurns[t]));
        c.add(share(exposedEnd[t], contactTurns[t]));
        c.add(share(alone20[t], contactTurns[t]));
        c.add(groupSizes.get(t).isEmpty() ? "" : "" + median(groupSizes.get(t)));
        List<Integer> cyc = new ArrayList<>();
        int dep = 0, partial = 0;
        for (Trip tr : trips) if (tr.c.team == t && "deposit".equals(tr.outcome)) { cyc.add(tr.tEnd - tr.t0); dep++; if (tr.load < 40) partial++; }
        c.add(cyc.isEmpty() ? "" : "" + median(cyc));
        c.add(share(partial, dep));
        c.add(cpw.get(t).isEmpty() ? "" : "" + median(cpw.get(t)));
        c.add(share(blind2[t], shots2[t]));
        c.add(share(focusN[t], hitsN[t]));
        // kill_conv: distinct victims this team hit, converted when the victim died within 3 rounds of its last hit
        Map<Integer, Integer> lastHit = new HashMap<>();
        for (int[] h : hitVictims) if (h[0] == t) lastHit.merge(h[1], h[2], Math::max);
        long conv = 0;
        for (Map.Entry<Integer, Integer> e : lastHit.entrySet()) { Robot v = robots.get(e.getKey()); if (v.died >= 0 && v.died <= e.getValue() + 3) conv++; }
        c.add(share(conv, lastHit.size()));
        c.add(String.join(" ", firstBuilds.get(t)));
        return c;
    }

    List<String> gamesRows() {
        List<String> rows = new ArrayList<>();
        for (int t = 1; t <= 2; t++) {
            boolean tele = teleSide(t);
            rows.add(String.join(",", prefix, mapName, "" + W, "" + H, symmetry >= 0 && symmetry < 3 ? SYM_NAMES[symmetry] : "" + symmetry,
                "" + nIslands, "" + totalRounds, side(t), t == 1 ? teamA : teamB, winner == t ? "1" : "0", winReason, tbMargin,
                totalRounds >= 500 ? vtbSide[0] : "", totalRounds >= 1000 ? vtbSide[1] : "", totalRounds >= 1500 ? vtbSide[2] : "",
                teleStatus(t), bccSide[t] ? "" + kstar[t] : "", "" + nSync[t], nSync[t] == 0 ? "" : f3((double) sSync[t] / nSync[t]),
                "" + bothN[t], bothN[t] == 0 ? "" : f4((double) agreeN[t] / bothN[t]),
                codeTurns[t] == 0 ? "" : f4((double) (codeTurns[t] - invalidN[t]) / codeTurns[t]),
                tele ? "" + invalidN[t] : "", tele ? "" + excTurns[t] : "", "" + teleDotsN[t], "" + unknownN[t]));
        }
        return rows;
    }

    List<String> deathsRows() {
        List<String> rows = new ArrayList<>();
        for (Robot v : deaths) {
            boolean tele = teleSide(v.team);
            rows.add(String.join(",", prefix, "" + v.died, "" + v.id, side(v.team), "" + TC[v.type], "" + (v.died - v.born), "" + v.preX, "" + v.preY,
                fmtP(prog(v.preX, v.preY)), CAUSES[v.cause], v.killer == null ? "" : "" + v.killer.id, v.killer == null ? "" : "" + TC[v.killer.type],
                "" + v.hpBefore, "" + v.deathCargo[0], "" + v.deathCargo[1], "" + v.deathCargo[2], "" + v.deathAnc,
                v.died - v.born <= 5 ? "1" : "0", v.deathEng < 0 ? "" : "" + engFind(v.deathEng),
                tele && v.lastCode >= 0 ? "" + v.lastCode : "", tele && v.lastCode >= 0 ? "" + letter(v.type, v.lastCode) : ""));
        }
        return rows;
    }

    static String codesStr(TreeMap<String, Integer> m) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, Integer> e : m.entrySet()) sb.append(sb.length() == 0 ? "" : ";").append(e.getKey()).append('=').append(e.getValue());
        return sb.toString();
    }

    List<String> engRows() {
        List<String> rows = new ArrayList<>();
        for (Eng e : engs) {
            if (e.parent != e.id) continue;
            rows.add(String.join(",", prefix, "" + e.id, "" + e.r0, "" + e.r1, "" + (e.r1 - e.r0 + 1), "" + e.x0, "" + e.y0, e.prog0,
                "" + e.n0[1], "" + e.n0[2], "" + e.hp0[1], "" + e.hp0[2], "" + e.peak[1], "" + e.peak[2],
                "" + e.joined.get(1).size(), "" + e.joined.get(2).size(), e.fhRound < 0 ? "-" : side(e.fhSide),
                "" + e.dmgBy[1], "" + e.dmgBy[2], "" + e.killsBy[1], "" + e.killsBy[2], "" + e.valLost[1], "" + e.valLost[2],
                "" + e.aura[1], "" + e.aura[2], "" + e.surv[1], "" + e.surv[2], e.held, engResult(e),
                teleSide(1) ? codesStr(e.codes.get(1)) : "", teleSide(2) ? codesStr(e.codes.get(2)) : ""));
        }
        return rows;
    }

    /** "G=40;C=30;R=20;D=10": a robot's top 4 letters by turns. */
    static String topLetters(int type, int[] codeCnt) {
        if (codeCnt == null) return "";
        Map<Character, Integer> m = new TreeMap<>();
        for (int c = 0; c < 64; c++) if (codeCnt[c] > 0) m.merge(letter(type, c), codeCnt[c], Integer::sum);
        List<Map.Entry<Character, Integer>> l = new ArrayList<>(m.entrySet());
        l.sort((x, y) -> y.getValue() != x.getValue().intValue() ? y.getValue() - x.getValue() : x.getKey() - y.getKey());
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < l.size() && i < 4; i++) sb.append(i == 0 ? "" : ";").append(l.get(i).getKey()).append('=').append(l.get(i).getValue());
        return sb.toString();
    }

    List<String> robotsRows() {
        List<String> rows = new ArrayList<>();
        for (Robot rb : robots.values())
            rows.add(String.join(",", prefix, "" + rb.id, side(rb.team), "" + TC[rb.type], "" + rb.born, rb.died < 0 ? "" : "" + rb.died,
                rb.cause < 0 ? "" : CAUSES[rb.cause], "" + rb.bornX, "" + rb.bornY, "" + rb.nTurns, "" + rb.maxStill2,
                rb.stillR0 < 0 ? "" : "" + rb.stillR0, "" + rb.bcMax2, "" + rb.bcOver2, "" + rb.bcNear2,
                teleSide(rb.team) ? topLetters(rb.type, rb.codeCnt) : ""));
        return rows;
    }

    List<String> statesRows() {
        List<String> rows = new ArrayList<>();
        for (int t = 1; t <= 2; t++) {
            if (!teleSide(t)) continue;
            for (int ty = 0; ty < NT; ty++) for (int ph = 0; ph < 4; ph++) {
                long tot = 0;
                for (int c = 0; c < 64; c++) tot += stc[t][ty][ph][c][0] + stc[t][ty][ph][c][1];
                if (tot == 0) continue;
                for (int c = 0; c < 64; c++) {
                    long b = stc[t][ty][ph][c][0], s = stc[t][ty][ph][c][1];
                    if (b + s == 0) continue;
                    rows.add(String.join(",", prefix, side(t), "" + TC[ty], PHASES[ph], "" + c, "" + letter(ty, c), detail(ty, c),
                        "" + (b + s), f4((double) (b + s) / tot), "" + b, "" + s));
                }
            }
        }
        return rows;
    }

    List<String> tripsRows() {
        List<String> rows = new ArrayList<>();
        for (Trip tr : trips) {
            int well = -1, best = -1, res = 0;
            for (Map.Entry<Integer, int[]> e : tr.wellAmt.entrySet()) if (e.getValue()[0] >= best) { best = e.getValue()[0]; well = e.getKey(); }
            int wait = 0;
            if (well >= 0) {
                int[] a = tr.wellAmt.get(well);
                res = a[1] >= a[2] && a[1] >= a[3] ? 1 : a[2] >= a[3] ? 2 : 3;
                int[] nr = tr.near.get(well);
                if (nr != null) wait = nr[0] - nr[1];
            }
            String codes = "";
            if (tr.letters != null && teleSide(tr.c.team)) {
                StringBuilder sb = new StringBuilder();
                for (int ch = 33; ch < 127; ch++) if (tr.letters[ch] > 0) sb.append(sb.length() == 0 ? "" : ";").append((char) ch).append('=').append(tr.letters[ch]);
                codes = sb.toString();
            }
            rows.add(String.join(",", prefix, side(tr.c.team), "" + tr.c.id, "" + tr.t0, tr.first < 0 ? "" : "" + tr.first,
                tr.last < 0 ? "" : "" + tr.last, "" + tr.tEnd, well < 0 ? "" : "" + well % W, well < 0 ? "" : "" + well / W,
                well < 0 ? "" : "" + res, "" + tr.collects, "" + tr.load, "" + wait, tr.outcome, codes));
        }
        return rows;
    }

    // ---- modes
    void tele(PrintStream o) {
        deep = true;
        run(null);
        o.printf("game %d map %s rounds %d%n", gameIdx, mapName, totalRounds);
        for (int t = 1; t <= 2; t++) {
            String team = t == 1 ? teamA : teamB;
            if (!teleSide(t)) { o.printf("side %s team %s tele=none%n", side(t), team); continue; }
            o.printf("side %s team %s tele=%s offset=%s sync=%d/%d (%s) agree=%d/%d (%s) valid=%s invalid=%d exc_turns=%d dots=%d unknown_kinds=%d letter_mismatch=%d%n",
                side(t), team, teleStatus(t), bccSide[t] ? "" + kstar[t] : "-", sSync[t], nSync[t], nSync[t] == 0 ? "-" : f3((double) sSync[t] / nSync[t]),
                agreeN[t], bothN[t], bothN[t] == 0 ? "-" : f4((double) agreeN[t] / bothN[t]),
                codeTurns[t] == 0 ? "-" : f3((double) (codeTurns[t] - invalidN[t]) / codeTurns[t]), invalidN[t], excTurns[t], teleDotsN[t],
                unknownN[t], mismatchN[t]);
            if (teleDotsN[t] > 0) {
                StringBuilder sb = new StringBuilder();
                for (int k = 0; k <= COMMS0; k++) if (kindN[t][k] > 0) sb.append(' ').append(kindName(k)).append('=').append(kindN[t][k]);
                for (Map.Entry<String, Long> e : unknownKinds.get(t).entrySet()) sb.append(' ').append(e.getKey()).append('=').append(e.getValue());
                o.printf("side %s records%s%n", side(t), sb);
            }
            for (int ty = 0; ty < NT; ty++) { String sh = teleShares(t, ty, 0); if (!sh.isEmpty()) o.printf("side %s %s %s%n", side(t), TN[ty], sh); }
        }
    }

    void checks(PrintStream o) {
        deep = true;
        run(null);
        o.printf("checks rounds=%d hp_over_max=%d hp_nonpos_alive=%d inv_negative=%d team_total_mismatch=%d dead_inv_nonzero=%d unattributed_hits=%d%n",
            rounds2, hpOverMax, hpNonposAlive, invNeg, teamTotalMismatch, deadInvNonzero, badHits);
    }

    /** Game count and indices of a decompressed file. */
    static int countGames(GameWrapper gw) {
        int n = 0;
        for (int i = 0; i < gw.eventsLength(); i++) if (gw.events(i).eType() == Event.MatchHeader) n++;
        return n;
    }

    static void extract(String file, String[] a) throws IOException {
        File dir = new File(arg(a, "--extract", "."));
        String base = new File(file).getName();
        int lead = 0;
        while (lead < base.length() && Character.isDigit(base.charAt(lead))) lead++;
        int match = Integer.parseInt(arg(a, "--match", lead > 0 && lead < 10 ? base.substring(0, lead) : "0"));
        GameWrapper gw = load(file);
        int ng = countGames(gw);
        List<Integer> sel = new ArrayList<>();
        String gs = arg(a, "--games", "all");
        if (gs.equals("all")) for (int g = 0; g < ng; g++) sel.add(g);
        else for (String s : gs.split(",")) { int g = Integer.parseInt(s.trim()); if (g >= 0 && g < ng) sel.add(g); }
        if (!dir.isDirectory() && !dir.mkdirs()) throw new IOException("cannot create " + dir);
        boolean wantTurns = flag(a, "--tele-turns");
        String[][] files = {{"games.csv", GAMES_HDR}, {"census.csv", "match,game," + CENSUS_HDR_ALL}, {"deaths.csv", DEATHS_HDR},
            {"engagements.csv", ENG_HDR}, {"timeline.csv", TIMELINE_HDR}, {"hq.csv", HQ_HDR}, {"robots.csv", ROBOTS_HDR},
            {"tele_states.csv", STATES_HDR}, {"trips.csv", TRIPS_HDR}};
        Map<String, PrintStream> out = new LinkedHashMap<>();
        for (String[] f : files) {
            PrintStream p = new PrintStream(new BufferedOutputStream(new FileOutputStream(new File(dir, f[0]))), false, "US-ASCII");
            p.println(f[1]);
            out.put(f[0], p);
        }
        File evTmp = new File(dir, "tele_events.jsonl.tmp"), ev = new File(dir, "tele_events.jsonl"), turns = new File(dir, "tele_turns.csv");
        PrintStream evOut = new PrintStream(new BufferedOutputStream(new FileOutputStream(evTmp)), false, "US-ASCII");
        PrintStream turnsOut = null;
        if (wantTurns) { turnsOut = new PrintStream(new BufferedOutputStream(new FileOutputStream(turns)), false, "US-ASCII"); turnsOut.println(TURNS_HDR); }
        else turns.delete();
        boolean anyDots = false;
        for (int g : sel) {
            ReplayDump d = new ReplayDump(gw, g);
            d.deep = true;
            d.matchId = match;
            d.prefix = match + "," + g;
            d.eventsOut = evOut;
            d.turnsOut = turnsOut;
            d.run(null);
            anyDots |= d.dotSide[1] || d.dotSide[2];
            for (String row : d.gamesRows()) out.get("games.csv").println(row);
            for (String row : d.censusRows()) out.get("census.csv").println(d.prefix + "," + row);
            for (String row : d.deathsRows()) out.get("deaths.csv").println(row);
            for (String row : d.engRows()) out.get("engagements.csv").println(row);
            for (String row : d.timelineRows) out.get("timeline.csv").println(row);
            for (String row : d.hqRows) out.get("hq.csv").println(row);
            for (String row : d.robotsRows()) out.get("robots.csv").println(row);
            for (String row : d.statesRows()) out.get("tele_states.csv").println(row);
            for (String row : d.tripsRows()) out.get("trips.csv").println(row);
            System.out.printf("%d %s %d %s %s tele_A=%s tele_B=%s%n", g, d.mapName, d.totalRounds, d.winner == 1 ? "A" : d.winner == 2 ? "B" : "-",
                d.winReason, d.teleStatus(1), d.teleStatus(2));
            System.out.flush();
        }
        for (PrintStream p : out.values()) p.close();
        evOut.close();
        if (turnsOut != null) turnsOut.close();
        ev.delete();
        if (anyDots) { if (!evTmp.renameTo(ev)) throw new IOException("cannot rename " + evTmp); }
        else evTmp.delete();
    }

    /** SHA-1 over the decimal game state per round (B.1) and over (round, id, used); indicators excluded. */
    static void fingerprint(GameWrapper gw, PrintStream o) throws Exception {
        java.security.MessageDigest ms = null, mb = null;
        int gi = -1;
        String map = "?";
        for (int i = 0; i < gw.eventsLength(); i++) {
            EventWrapper ew = gw.events(i);
            byte t = ew.eType();
            if (t == Event.MatchHeader) {
                gi++;
                map = ((MatchHeader) ew.e(new MatchHeader())).map().name();
                ms = java.security.MessageDigest.getInstance("SHA-1");
                mb = java.security.MessageDigest.getInstance("SHA-1");
            } else if (t == Event.Round && ms != null) {
                Round r = (Round) ew.e(new Round());
                StringBuilder s = new StringBuilder().append(r.roundID());
                SpawnedBodyTable sp = r.spawnedBodies();
                if (sp != null) for (int k = 0; k < sp.robotIDsLength(); k++)
                    s.append(',').append(sp.robotIDs(k)).append(',').append(sp.teamIDs(k)).append(',').append(sp.types(k))
                        .append(',').append(sp.locs().xs(k)).append(',').append(sp.locs().ys(k));
                for (int k = 0; k < r.actionsLength(); k++) s.append(',').append(r.actionIDs(k)).append(',').append(r.actions(k)).append(',').append(r.actionTargets(k));
                VecTable ml = r.movedLocs();
                for (int k = 0; k < r.movedIDsLength(); k++) s.append(',').append(r.movedIDs(k)).append(',').append(ml.xs(k)).append(',').append(ml.ys(k));
                for (int k = 0; k < r.diedIDsLength(); k++) s.append(',').append(r.diedIDs(k));
                for (int k = 0; k < r.teamIDsLength(); k++)
                    s.append(',').append(r.teamIDs(k)).append(',').append(r.teamAdChanges(k)).append(',').append(r.teamMnChanges(k)).append(',').append(r.teamExChanges(k));
                for (int k = 0; k < r.islandIDsLength(); k++) s.append(',').append(r.islandIDs(k)).append(',').append(r.islandOwnership(k));
                s.append('\n');
                ms.update(s.toString().getBytes(java.nio.charset.StandardCharsets.US_ASCII));
                StringBuilder b = new StringBuilder().append(r.roundID());
                for (int k = 0; k < r.bytecodeIDsLength(); k++) b.append(',').append(r.bytecodeIDs(k)).append(',').append(r.bytecodesUsed(k));
                b.append('\n');
                mb.update(b.toString().getBytes(java.nio.charset.StandardCharsets.US_ASCII));
            } else if (t == Event.MatchFooter && ms != null) {
                MatchFooter f = (MatchFooter) ew.e(new MatchFooter());
                o.printf("%d %s %d %s %s%n", gi, map, f.totalRounds(), hex(ms.digest()), hex(mb.digest()));
                ms = mb = null;
            }
        }
    }

    static String hex(byte[] d) {
        StringBuilder sb = new StringBuilder();
        for (byte x : d) sb.append(String.format("%02x", x));
        return sb.toString();
    }

    /** --decode-record KIND A B C D [--type T]: KIND is a number or a name (COMMS = chunk 0). */
    static void decodeRecordMain(String[] a) {
        if (a.length < 6) { System.err.println("usage: ReplayDump --decode-record KIND A B C D [--type H|C|L|A|D|B]"); System.exit(2); }
        int kind = -1;
        for (int k = 0; k < KIND_NAMES.length; k++) if (KIND_NAMES[k].equalsIgnoreCase(a[1])) kind = k;
        if (a[1].equalsIgnoreCase("COMMS")) kind = COMMS0;
        if (kind < 0) kind = Integer.parseInt(a[1]);
        int[] w = new int[4];
        for (int k = 0; k < 4; k++) w[k] = (int) Long.parseLong(a[2 + k]);
        String ts = arg(a, "--type", null);
        int type = -1;
        if (ts != null) for (int k = 0; k < NT; k++) if (ts.equalsIgnoreCase("" + TC[k]) || ts.equalsIgnoreCase(TN[k])) type = k;
        System.out.println("{" + decodeFields(kind, w[0], w[1], w[2], w[3], type, false) + "}");
    }


    // ---------------------------------------------------------------- main
    static String arg(String[] a, String k, String def) {
        for (int i = 0; i < a.length - 1; i++) if (a[i].equals(k)) return a[i + 1];
        return def;
    }

    static boolean flag(String[] a, String k) { return Arrays.asList(a).contains(k); }

    public static void main(String[] a) throws Exception {
        if (a.length == 1 && a[0].equals("--census-header")) { System.out.println(CENSUS_HDR_ALL); return; }
        if (a.length >= 1 && a[0].equals("--decode-record")) { decodeRecordMain(a); return; }
        if (a.length < 1) {
            System.err.println("usage: ReplayDump <replay.bc23> [--game N] [--games | --census [--no-header] | --metrics [--every N] | --robot ID | --map-at R | "
                + "--logs [--team A|B] [--id ID] [--from R --to R] | --bytecode | --navstats | --events --from R --to R | --islands | --tele | --checks"
                + " | --fingerprint | --extract DIR [--match ID] [--games all|i,j] [--tele-turns]]   or   ReplayDump --decode-record KIND A B C D [--type T]");
            System.exit(2);
        }
        if (flag(a, "--extract")) { extract(a[0], a); return; }
        if (flag(a, "--fingerprint")) {
            PrintStream fo = new PrintStream(new BufferedOutputStream(System.out), false);
            fingerprint(load(a[0]), fo);
            fo.flush();
            return;
        }
        ReplayDump d = new ReplayDump(a[0], Integer.parseInt(arg(a, "--game", "0")));
        if (flag(a, "--games")) {      // one line per game in the file: index map winner(A|B) rounds
            for (String g : d.gameList) System.out.println(g);
            return;
        }
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
        else if (flag(a, "--states")) d.states(o);
        else if (flag(a, "--tele")) d.tele(o);
        else if (flag(a, "--checks")) d.checks(o);
        else if (flag(a, "--overruns")) { d.listener = (rn, line) -> { if (line.startsWith("overrun")) o.printf("r%-5d %s%n", rn, line); }; d.run(null); }
        else d.summary(o);
        o.flush();
    }
}
