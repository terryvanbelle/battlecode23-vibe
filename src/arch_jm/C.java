package arch_jm;

/**
 * Every tunable constant and every arm switch, each with the measurement or reason that set it.
 * g_iter0 values are first guesses from the rules (RULES.md) and are to be measured, not trusted.
 */
public final class C {
    // ==== ARCHETYPE arch_jm: a sparring partner imitating jmerle.camel_case_v30_final. A copy of c_mend2 with
    // c_blind2's blind fire (the block below) and four behaviours changed, each set from 240 replica replays of jmerle
    // (research/clone/jmerle/sa_*.csv.gz, state-action rows; ours_sa_*.csv.gz the same rows for our games). Every other
    // value is c_mend2's (arch_swarm line).
    /** (1) Mana first. jmerle's deposits are 89% mana through r600 (ours 69-81%) and its HQ Ad bank stays 40-75 (ours
     *  184 at r400, 255 at r600). arch_jm: the late Ad role is off (AD_ROLE_FROM 2000), so a carrier mines Ad only as the
     *  one in AD_EARLY_EVERY whose nearest HQ raises its Ad flag (HQ.swarmEconomy): below AD_NEED with carrier-cap room,
     *  and, with AD_ANCHOR_FLAG, below ANCHOR_AD while that HQ wants an anchor (HQ.build's wantAnchor), so anchors stay
     *  fundable after the carrier cap is reached. AD_BANK_CAP is ANCHOR_AD (80): below it an Ad carrier could stop with
     *  the bank short of the anchor. */
    public static final boolean AD_ANCHOR_FLAG = true;
    /** Adamantium for one Standard anchor (RULES: 80 Ad + 80 Mn; HQ.build's literal 80). */
    public static final int ANCHOR_AD = 80;
    /** (3) Midfield front. Launcher turns by prog = d(own HQ) / (d(own HQ) + d(enemy HQ)), home (< 0.4) / mid / deep
     *  (> 0.6): jmerle r0-100 55/28/18%, r100-200 45/29/26, r200-300 38/28/34, r300-400 32/26/42; ours 78/14/8, 64/15/21,
     *  62/8/30, 59/4/37, and ours spend 13-22% of launcher turns within r2 36 of an enemy HQ (the siege ring) against
     *  jmerle's 8-15%: jmerle leaves home early, holds the middle and pushes gradually. With FRONT, where
     *  Launcher.pickObjective returned the raid well or the siege ring it returns the front point (frontPoint), at
     *  FRONT_P0 percent of the way from our HQ centroid to the siege target before round FRONT_FROM, FRONT_STEP more at
     *  FRONT_FROM and every FRONT_EVERY rounds after (60 from r150, 70 from r225, 80 from r300); past FRONT_MAX (r375)
     *  the raid and ring resume. A launcher within r2 FRONT_HOLD_R2 of the point holds there. A point on a known wall
     *  moves to the nearest tile within FRONT_SNAP (king steps) that is not a known wall. */
    public static final boolean FRONT = true;
    public static final int FRONT_P0 = 50, FRONT_FROM = 150, FRONT_STEP = 10, FRONT_EVERY = 75, FRONT_MAX = 80;
    public static final int FRONT_HOLD_R2 = 10, FRONT_SNAP = 3;
    /** (4) Close in out of range. With an enemy launcher in vision but none within r2 16, jmerle steps toward it on
     *  33-38% of turns and away on 7-13%, whatever the numbers; ours, outnumbered, 12% toward and 37% away. Once in range
     *  the two match (toward 4-7%, away 37-43%), so that case is unchanged. With CLOSE_IN, Launcher.fight in the
     *  out-of-range case scores no tile that ends farther from the nearest enemy fighter than standing still: ready, it
     *  steps in to fire (any numbers), else it holds; not at CLOSE_IN_HP or less, and not while mending (C.MEND). */
    public static final boolean CLOSE_IN = true;
    public static final int CLOSE_IN_HP = 60;
    // (2) blind fire: c_blind2's arm below, with BLIND_MEM_DEBT set for jmerle's firing rate on clouds.
    // (3a) GROUP_MIN 2 while forming at home. (1) also sets AD_ROLE_FROM and AD_BANK_CAP below; each is marked arch_jm.

    /** c_blind1: 0 compiles the arm out; 1 every eligible turn, 2/4 every second/fourth round by id phase. */
    public static final int BLIND_PERIOD = 1;
    /** Provisional reserves. Actual hook and subsequent tail costs must be measured before any trial. */
    public static final int BLIND_ENTRY_LEFT = 4000, BLIND_SCAN_LEFT = 3500, BLIND_STATS_LEFT = 2000;
    /** c_blind2 memory arm (Launcher.remember/memBlocked/memPick): each launcher remembers its own last sightings of enemy
     *  launchers and destabilizers in BLIND_MEM_N slots (0 compiles the arm out, leaving c_blind1; else a power of two
     *  from 2 to 16: BLIND_MEM_N/2 sets of 2 ways keyed by robot id, the older way replaced) and fires blind at a
     *  remembered tile at most BLIND_MEM_AGE rounds old that it cannot sense now (field evidence, PROMPTS 48-49: the
     *  strong teams fire at the remembered positions of launchers hidden in clouds). Recording rides on Launcher.track's
     *  fighter loop, so it shares its guards (TRACK_MIN_LEFT, TRACK_MAX). Provisional. Costs measured offline with the
     *  engine's instrumenter (no game): recording 37-53 a fighter, so a 12-fighter turn pays about 650 more than c_blind1
     *  before fight(); the arm about 470 for a hit with 1 fresh slot, at most about 1,400 with 8 fresh slots (hit or
     *  none); a turn with no sighting within BLIND_MEM_AGE costs c_blind1's calls plus about 5. */
    public static final int BLIND_MEM_N = 8, BLIND_MEM_AGE = 6;
    /** c_blind2: cooldown debt the memory arm alone may leave for the next own turn (cd + rounded cost <= 10 + this).
     *  0 keeps c_blind1's rule. Under it an unboosted launcher on a cloud (m 1.2, cost 12) never fires blind: the
     *  memory arm fires from a cloud only with m <= 1.0 (two boosters). 2 lets it fire from cd 0 on a cloud and start
     *  its next turn at cd 2, still ready (RULES 5.2: ready below 10).
     *  arch_jm (2): 13, so any action-ready turn (cd <= 9) may fire blind even on a cloud under two destabilize stacks
     *  (m 1.4, cost 14): a jmerle launcher standing on a cloud with an enemy launcher within r2 16 attacks on 85% of
     *  turns (34% of those shots hit), about the most a cloud's cost 12 allows (5 turns in 6); ours attack on 31%, only
     *  when they can see. The arm cannot throw at cd >= 10: memBlocked skips any tile canAttack refuses (it checks
     *  readiness, RobotControllerImpl.assertCanAttack), and blindShot now also skips a turn that is not ready. */
    public static final int BLIND_MEM_DEBT = 13;
    // ==== ARCHETYPE arch_swarm (S1): early mana swarm that besieges the HQ (docs/ARCHETYPES.md 4.1; model
    // jmerle.camel_case_v30_final; members vrangr1, awesomelemonade, jmerle, NotLLeon). A fork of c_line6 (5bc8e7e545ac).
    // Every value below is set from the members' 160 replica panel games (survey medians, ARCHETYPES.md 1 and 4.1).
    /** Mana economy: carriers mine mana (members: Mn share of collection at r100 0.85-0.98, Ad@100 10-92). Before
     *  AD_ROLE_FROM a carrier mines adamantium only while its HQ holds less than AD_NEED and the team is under the
     *  carrier cap (HQ flag in Comms.AD_FLAGS), and then only one carrier in AD_EARLY_EVERY. From AD_ROLE_FROM one in
     *  AD_LATE_EVERY mines adamantium to fund anchors (members' first anchor r262-406).
     *  arch_jm (1): AD_ROLE_FROM 2000 (was 200), the late role off; anchors are funded by AD_ANCHOR_FLAG. */
    public static final int AD_NEED = 50, AD_EARLY_EVERY = 8, AD_ROLE_FROM = 2000, AD_LATE_EVERY = 4;
    /** Carrier cap (team, live carriers by the Comms census): CAP_PER_MN_WELL per known mana well, at least
     *  CAP_MIN_PER_HQ per HQ, at most CAP_MAX (members' carriers per well 3-5, carriers alive at r250 21-28; built
     *  18 by r100 and 29 by r250 on DefaultMap, i.e. every Ad the HQs receive). The design's 4 per mana well counts the
     *  whole map's wells; our shared list holds mostly our half, so 8 per known well (v1: 4 per well and 4 per HQ held
     *  the swarm at 12 carriers to r100 on DefaultMap with 480 Ad banked). */
    public static final int CAP_PER_MN_WELL = 8, CAP_MIN_PER_HQ = 6, CAP_MAX = 30;
    /** ... and the per-HQ minimum grows by one per CAP_GROW_ROUNDS (driver game, MassiveL: one known mana well held the
     *  cap at 12 carriers with 280-430 Ad banked from r150; members' carriers alive grow 12 at r100 to 22 at r250). */
    public static final int CAP_GROW_ROUNDS = 50;
    /** Siege rotation: from SIEGE_ROTATE_FROM the team target moves to the next enemy HQ every SIEGE_ROTATE rounds. Off
     *  (2000): tried for MassiveL, where one fixed target let g_iter0's other HQ anchor 9 of 12 islands, but the driver
     *  game was worse (lost r523 vs r809; pressure on the victim HQs by r250 133 vs 342, engagements at prog 0.45 vs 0.19). */
    public static final int SIEGE_ROTATE_FROM = 2000, SIEGE_ROTATE = 100;
    /** Siege ring around the enemy HQ, r2 RING_MIN..RING_MAX: outside the r2 9 aura, close enough to hit spawn tiles
     *  (members: first pressure on our HQ r75-100, 236-975 enemy launcher-rounds within r2 34 of our HQs by r250). */
    public static final int RING_MIN = 16, RING_MAX = 34;
    /** Carrier raid: predicted enemy wells within r2 RAID_R2 of an enemy HQ; a raided well with no enemy carrier in
     *  view is skipped for RAID_CLEAR_ROUNDS (members killed 4.5-7.3 of our carriers by r150, at prog 0.10-0.14). */
    public static final int RAID_R2 = 100, RAID_CLEAR_ROUNDS = 40;
    /** Launchers hunt enemy-held islands from this round. The design said r250; v2 quick lost ReverseFunnel by conquest
     *  at r224 to g_iter0's anchor rush (the members never lose to it: 0 of 40 losses on that map), so from the start. */
    public static final int ISLAND_HUNT_START = 0;
    /** A shared enemy sighting is an objective only within this r2 of the launcher (the swarm keeps to its siege). */
    public static final int SIGHTING_R2 = 64;
    /** No amplifiers (members jmerle, awesomelemonade: 0; vrangr1's r111 amplifier is the SWARM_DIVE switch, off). */
    public static final boolean SWARM_DIVE = false;
    /** c_def2 raid alarm and recall (research/diagnosis/2026-10-09-g_iter3.md, arm 2). Each HQ publishes in Comms.ALARM
     *  its enemy fighters in vision when they outnumber our launchers there; launchers on our half rally on that HQ.
     *  Home raids r<300 vs the five strong teams: our median peak 1 vs their 3-4, won 11-24%, while 8-22 of our
     *  launchers lived elsewhere; home net -284 per lost game; HQ 't' share r101-300 0.32 (awesomelemonade). */
    public static final boolean RECALL = true;
    /** Alarm level that recalls: 3+ enemy fighters outnumbering us at the HQ (narrow: HOME_DEFENCE_R2 100 left lone
     *  launchers alone 0.32 and c_grp1 failed 7-13; raids carrying the losses are 3-4.5 raiders vs 1). 2 = second variant. */
    public static final int RAID_ALARM = 3;
    /** Only launchers within this r2 of the alarmed HQ (about 15 tiles, 30 rounds) are recalled: raids of 20+ rounds
     *  carry 68-82% of the raid losses, and launchers farther away keep the field and siege gain (+1081 net r<300). */
    public static final int RECALL_R2 = 225;
    /** Recall only before this round: the home deficit is before r300 (home net -1352 summed over the five strong
     *  teams) and HQs are under siege from r200-300; later the siege and islands decide (first anchors r162-503). */
    public static final int RECALL_UNTIL = 600;

    // ---- HQ production
    /** Anchors are built from this round on (rules: anchors decide the game; first guess). */
    public static final int ANCHOR_START = 250;   // arch_swarm (design 4.1: r250)
    /** ... and only after this many launchers have been built by this HQ (an anchor needs an escort). */
    public static final int ANCHOR_MIN_LAUNCHERS = 12;   // arch_swarm
    /** Carriers are built while our live robot count (all types, HQs included) is below ROBOTS_BASE + ROBOTS_PER_WELL x
     *  known wells. Replaced a cap on carriers ever built per HQ (4 + round/40, max 24) that locked production out under
     *  attrition; strong field bots run 50-78 carriers (calib-g_iter0 census of losses: median 78 built vs our 21). */
    public static final int ROBOTS_BASE = 30, ROBOTS_PER_WELL = 15;
    /** Before this round, carriers per HQ are capped by the number BUILT: CARRIER_BASE + round / CARRIER_PER_ROUNDS
     *  (g_iter0's cap); 0 disables. */
    public static final int EARLY_CAP_UNTIL = 0, CARRIER_BASE = 4, CARRIER_PER_ROUNDS = 40;   // arch_swarm: 0, no Ad banking for an early anchor
    /** An HQ builds at most one anchor per this many rounds (foundation2/Forest: anchors built every turn piled up in
     *  carriers that could not place them). */
    public static final int ANCHOR_PERIOD = 30;
    /** A carrier gives up an anchor it could not place within this many turns and returns it to an HQ. */
    public static final int ANCHOR_TIMEOUT = 150;
    /** Spawn on the tile fewest visible enemy fighters can reach (diag-top4: top bots fire at our spawn tiles). */
    public static final boolean SPAWN_SAFETY = true;
    /** HQ threat test: 0 = any enemy fighter in vision (g_iter0); 1 = real danger only (HQ.inDanger). */
    public static final int HQ_THREAT = 1;   // arch_swarm
    public static final int HQ_DANGER_R2 = 20;
    /** Launchers are built in batches of this many in one turn (unless the HQ is threatened). 1 = no batching: c_batch1
     *  (3) failed delivery on diag-top4 (launchers alive r100 -3.0, t -4.6; kills -9.5, t -6.2). */
    public static final int LAUNCHER_BATCH = 1;
    /** Launcher fight scoring: false = g_iter0's; true = c_micro1's (pinned enemies threaten r2 16, step in only where
     *  at most one enemy answers unless superior, stay put on ties). c_micro1 failed delivery on diag-top4 vs c_mana1:
     *  exposure up (+0.029, t +1.75), damage per contact up, kills -5.3 (t -2.3), launchers alive at r100 -1.7. */
    public static final boolean MICRO = false;
    /** Parity hold (Launcher.fight): unless ahead by 2+, do not step into more enemy reach to fire; stay when we can
     *  already hit. Off until its trial. */
    public static final boolean MICRO2 = true;   // arch_swarm: parity hold unless ahead by 2+
    /** Launcher cohesion (arm c_army1): with no enemy in sight a launcher advances only with GROUP_MIN launchers
     *  (itself included) in vision, follows the lowest-id launcher in vision when farther than r2 FOLLOW_R2, and
     *  otherwise regroups (nearest visible ally launcher, else back to the nearest own HQ). diag-top4: by r20 the top
     *  bots fielded 13 launchers in one mass while ours fought in ones and twos and lost 6 for 3. c_army1 passed
     *  delivery vs c_spawn1 (exposure -0.030, t -2.85; launchers lost -17, alive r250 +3.0, t +3.3; kills equal). */
    public static final boolean ARMY = true;   // arch_swarm: groups (members' group size 7-34.5)
    /** arch_jm (3a): GROUP_MIN 2 (was 4), so a launcher leaves home with one ally (jmerle opens with small groups leaving
     *  early: 55% of its r0-100 launcher turns at home against our 78%). */
    public static final int GROUP_MIN = 2, FOLLOW_R2 = 8;
    /** arch_swarm: launchers within this r2 of our nearest HQ are still forming (need GROUP_MIN to leave). */
    public static final int FORM_R2 = 50;
    /** A lone launcher still goes to an enemy sighting this close (r2) to one of our HQs: home defence. */
    public static final int HOME_DEFENCE_R2 = 20;   // arch_swarm: 20 (base 100): on DefaultMap every sighting lay within r2 100 of one of
                                                    // our three HQs, so lone launchers chased them (alone 0.32, exposed 0.18 in a driver game)
    /** Island observations older than this many rounds are not republished (slots carry no timestamp). */
    public static final int ISLAND_FRESH = 8;
    /** One amplifier per this many launchers built (comms coverage in the field). */
    public static final int LAUNCHERS_PER_AMP = 8;

    // ---- carriers
    /** A carrier returns home at this load (capacity 40; full loads maximise kg per trip, RULES economy). */
    public static final int CARRIER_RETURN_LOAD = 30;   // arch_swarm: jmerle deposits 30 kg loads (42 of 47 deposits by r120 on DefaultMap), trip cycle 36 vs our 54
    /** Carriers born before this round alternate adamantium/mana (the HQs need adamantium to grow the carrier fleet). */
    public static final int OPENING_ROUNDS = 40;
    /** Carrier role policy (Carrier.pickRole): 0 balance by HQ stock (c_nav1), 1 mana-first (c_mana1, rejected), 2 c_mana2.
     *  2 won the 174 calibration cells (+5 vs c_nav1) but on the replica panel the balanced policy did better (c_line5,
     *  ROLES 0, +3 vs c_line4, ROLES 2): mana-first starves the early anchor rush of adamantium. */
    public static final int ROLES = 3;   // arch_swarm: 3 = mana only (C.AD_* rules)
    public static final int MANA2_AD_EVERY = 5, MANA2_AD_HIGH = 250, MANA2_AD_LOW = 50, MANA2_MN_HIGH = 300;
    /** After the opening a carrier mines adamantium only while the HQ it delivers to holds less than this (a carrier
     *  plus some margin); otherwise mana. */
    public static final int AD_LOW = 120;
    /** Turns a carrier searches for a well of its own type before taking any well. */
    public static final int WELL_SEARCH_TURNS = 60;
    /** arch_swarm: a carrier still for this many turns while travelling or waiting steps aside (Carrier.unjam). */
    public static final int UNJAM_TURNS = 5;
    /** Turns a carrier waits at a crowded well before trying another well of its type. */
    public static final int WELL_CROWD_PATIENCE = 6;

    // ---- launchers
    /** Enemy fighters within this dist2 of a tile can hit it next turn: attack r2 16 after one step reaches every
     *  offset up to r2 26 ((5,1) steps to (4,0)); (5,2) = 29 cannot (synthesis 4.7; checked by BotTest). */
    public static final int THREAT_R2 = 26;

    // ---- monitoring
    /** Near-miss bar: 90% of the type's bytecode limit. */
    public static final int NEAR_MISS_PCT = 90;
    /** Telemetry (docs/TELEMETRY.md): data dots and the bytecode channel. The v2 indicator string is always on. */
    /** c_nav4: fields are descended only after greedy hits a wall on the way to their target (Nav.fieldOn).
     *  c_nav3 (owner, PROMPTS 35): distance fields (Field) start when wall-following begins farther than r2
     *  FIELD_MIN_D2 from the target; a stale field restarts at most every FIELD_RESTART rounds; a field used for descent
     *  in the last FIELD_KEEP rounds is not replaced by another target's. A launcher forming up at home waits at most
     *  FORM_MAX_TURNS move-ready turns for C.GROUP_MIN launchers (Target, match 1208: 20+ launchers idled 40-150 rounds). */
    public static final int FIELD_MIN_D2 = 20, FIELD_RESTART = 15, FIELD_KEEP = 10, FORM_MAX_TURNS = 15;
    /** A marching launcher plans its team target (the siege HQ) at once; a field also serves a target within r2
     *  FIELD_NEAR_D2 of its own while that target is farther than r2 FIELD_FAR_D2 (raid wells near the enemy HQ). */
    public static final int FIELD_NEAR_D2 = 100, FIELD_FAR_D2 = 150, FIELD_YOUNG = 60;
    /** c_nav5: Field.level stops searching with fewer bytecodes left than this (the turn's own work, unguarded before). */
    public static final int FIELD_LEVEL_GUARD = 3000;
    /** c_nav6 (crowd bytecodes; overruns at r1801-1979 on Cornucopia vs georgezhang, launchers in fight mode using
     *  8,600-9,900 a turn): Launcher.track follows at most TRACK_MAX enemy fighters and runs only with TRACK_MIN_LEFT
     *  bytecodes left; shoot() takes its best target so far under SHOOT_GUARD; fight() scoring stops under FIGHT_GUARD
     *  (was 2,000), leaving room for the second shot and the end of the turn. */
    public static final int TRACK_MAX = 12, TRACK_MIN_LEFT = 6000, SHOOT_GUARD = 1500, FIGHT_GUARD = 2500, FIGHT_MAX_OTHERS = 10;
    public static final boolean TELEMETRY = true;
    /** Bytecode-channel constant, calibrated per A.3; recalibrate whenever Telemetry.pad() or its call site changes. */
    public static final int PADK = 14;       // calibrated 2026-10-08: residue 14 on 8,561/8,561 turns (JDK 8u504, engine 3.0.15)
    /** Bytecodes the end of a turn must have left to build the indicator string (telemetry end-of-turn records plus
     *  indicator measured at 309 for launchers, 930 for HQs (tele_max_cost); the pad keeps its own BCC_GUARD).
     *  Skipped strings cost only that turn's code_str (the bytecode channel still carries the code). */
    public static final int IND_GUARD = 400;
    /** Free 16-bit build tag reported in HDR (0 = working line). */
    public static final int TELE_BUILD = 106;   // arch_jm (101 arch_swarm line, 102-105 the other archetypes)

    // ==== c_anc3: anchors only when they can hold, island scouting, courier survival (replica panel, g_iter4 matches
    // 2122-2131 = 1809-1818: in losses we built 12.4 anchors a game and lost 9.5, the HQ anchor reserve ('a') stopped
    // 22% of HQ turns in r251-600, 31.5 launchers were built in r251-600 and the median team bank_Ad at r500 was 380)
    /** HQ pressure: enemy fighters in HQ vision (r2 34 = hq.csv pressure34) summed per PRESS_BUCKET rounds; an HQ whose
     *  last or current bucket reaches PRESS_SUM is "pressed" (Comms.AD_FLAGS bits 4-7) and no HQ builds an anchor
     *  before ANCHOR_GATE_UNTIL (anchors built under pressure were the ones lost: 9.5 of 12.4 a game in losses). */
    public static final int PRESS_BUCKET = 25, PRESS_SUM = 100, ANCHOR_GATE_UNTIL = 1500;
    /** With no located neutral island, an anchor for an unlocated one only from ANCHOR_BLIND_FROM and at most one per
     *  ANCHOR_BLIND_PERIOD rounds (anchors carried with no target were lost in states E/Q; our earliest win is r464). */
    public static final int ANCHOR_BLIND_FROM = 400, ANCHOR_BLIND_PERIOD = 150;
    /** A late adamantium carrier delivering to an HQ that already holds this much Ad switches to mana (median bank_Ad
     *  at r500 380 in losses; 'poor' HQs still receive 44% of the Ad we deliver, so the role stays).
     *  arch_jm (1): ANCHOR_AD (80, was 150), applied to every Ad carrier now (jmerle's HQ Ad bank 40-75). */
    public static final int AD_BANK_CAP = ANCHOR_AD;
    /** Island scout: from SCOUT_FROM one carrier in SCOUT_EVERY (id % SCOUT_EVERY == 1) looks for islands while none
     *  located is neutral and some are unlocated, for at most SCOUT_MAX_TURNS turns, and brings sightings home to
     *  publish them (ReverseFunnel: no island slot filled before the first anchor; our earliest win r464). */
    public static final boolean SCOUT = true;
    public static final int SCOUT_FROM = 150, SCOUT_EVERY = 16, SCOUT_MAX_TURNS = 200;
    /** Courier survival: an anchor carrier with an enemy fighter in vision places, returns the anchor to an adjacent
     *  HQ, or flees; after COURIER_BLOCKED threatened turns it takes the anchor home. A carrier does not take an
     *  anchor for a located island with a fresh enemy sighting within r2 COURIER_SIGHT_R2 of it (couriers died in K:
     *  9.5 anchors lost of 12.4 built a game in losses). */
    public static final boolean ANCHOR_FLEE = true;
    public static final int COURIER_BLOCKED = 12, COURIER_SIGHT_R2 = 64;
    /** Island loops (up to 35 ids: Comms.islandStats, the scout's unpublished-island check, chooseIsland's located
     *  islands) stop with fewer bytecodes left than this, the reserve chooseIsland's prediction loop already keeps
     *  for the move that follows (carrier limit 12,500; zero overruns is a basics bar). */
    public static final int ISLAND_LOOP_GUARD = 3000;

    // ==== c_aura1: leave an enemy HQ aura (r2 9) instead of standing in it
    /** A launcher inside an enemy HQ aura may step strictly outward through aura tiles (Nav.auraStepOK), marches out
     *  first (Launcher.march), regroups with aura avoidance, and in fight() prefers the aura tile farthest from the HQ
     *  (931 aura deaths on 2430-2439, 873 at hp_before 4, last tokens W 398 / M 265 / N 200; regroup moves without
     *  avoid; Nav.can rejects outward aura tiles). false = c_anc3's behaviour. */
    public static final boolean AURA_SAFE = true;
    /** fight(): penalty per r2 unit an aura tile is nearer the enemy HQ than r2 9. Above the 1,000,000 can-hit bonus
     *  plus every smaller term (threat x 10,000, minD, rally, rand), so the outermost aura tile always wins: at 1,000,000
     *  an inward tile that can hit (r2 5 -> 4) tied with standing still, against the spec's "farthest from the HQ wins". */
    public static final long AURA_OUT_W = 2_000_000L;

    // ==== c_mend1: a wounded launcher heals on an island we own (RULES 8.1: robots within r2 4 of an island square of
    // their team heal). g8 panel census, healed HP per island-round ours vs theirs: pranayagra 1.57 vs 4.29, vrangr1
    // 1.36 vs 2.66, awesomelemonade 1.07 vs 3.77, while our island-rounds match theirs (pranayagra 1,022 vs 1,129);
    // 1,278 of 3,752 of our launcher deaths in losses (34%) came while we owned an island (judge/heal.py, mendx.py).
    /** Arm switch: false = c_aura2's behaviour (Launcher reads getHealth only for telemetry, never walks to heal). */
    public static final boolean MEND = true;
    /** Start mending at or below this HP (4 hits left): 88% of 4,887 dying launchers had a move-ready turn at 80 HP or
     *  less, 63% of them 4+ rounds before death (cx/x34.py, local FIGHT dots). */
    public static final int MEND_HP = 80;
    /** Stop mending at this HP (launcher max 200, one hit short of full): the teams that win the exchange heal 2.7-4.3
     *  HP per island-round against our 1.07-1.57, so a mender returns near full (judge's value, no measurement yet). */
    public static final int MEND_FULL = 180;
    /** Only an owned island tile within this r2 is a mending target: about 12 tiles, a 24-round walk at one move per
     *  two rounds, so walk + about 25 heal rounds + walk back stays near 75 rounds off the front (judge: 256 -> 144). */
    public static final int MEND_R2 = 144;
    /** Rounds between re-checks of the mending target (the up-to-35-id island loop, about 40 bytecodes an id, runs at
     *  most once per this many rounds, from ANCHOR_START, and only for launchers at MEND_HP or less or already mending;
     *  zero overruns is a basics bar, launcher limit 10,000). */
    public static final int MEND_RECHECK = 10;
    /** The re-check runs only with this many bytecodes left at its start, else it waits for the next turn and keeps the
     *  current target: TRACK_MIN_LEFT's line (c_nav6: launcher crowd turns used 8,600-9,900 of 10,000). The island loop
     *  plus Comms.nearestEnemy cost about 1,500 (up to about 2,500 when most of 35 islands are ours) and run before
     *  fight() / march(), so fight keeps 3,500-4,500 against its FIGHT_GUARD 2,500, march keeps room for
     *  pickObjective's unguarded 35-id island loop and the move, and the loop's ISLAND_LOOP_GUARD never cuts a pass
     *  (review: ISLAND_LOOP_GUARD alone let a check turn leave fight() 500 bytecodes and march 1,600). */
    public static final int MEND_MIN_LEFT = 6000;
    /** An owned island with an enemy sighting at most 1 stamp old (Comms.nearestEnemy maxAge 1: up to 31 rounds old)
     *  within this r2 of its tile is not a mending target: 6 tiles, past an enemy fighter's one-step reach of the tile
     *  (C.THREAT_R2 26), so a wounded launcher does not walk into a contested island (judge's value, no measurement yet). */
    public static final int MEND_SIGHT_R2 = 36;
}
