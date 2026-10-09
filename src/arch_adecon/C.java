package arch_adecon;

/**
 * Every tunable constant and every arm switch, each with the measurement or reason that set it.
 * g_iter0 values are first guesses from the rules (RULES.md) and are to be measured, not trusted.
 */
public final class C {
    // ==== ARCHETYPE arch_adecon (S5): adamantium economy, light army, long game (docs/ARCHETYPES.md 4.2).
    // Fork of c_line6 (5bc8e7e545ac). Members: battlecode-archive.Sprint1, reeceyang.v5anaconda (models),
    // yaonam.PoonPoonv4 (THROWER switch). Member values: survey of 120 replica panel games (40 per member, matches
    // 19-21/201-203/536-538/602-604), per-bot medians unless marked mean. Built from observed behaviour only (rule 3).
    /** Carriers only before this round; launchers from it on (Sprint1: first 4 builds CCCC in 40/40 games, first
     *  launcher r5 in 40/40). */
    public static final int AE_FIRST_LAUNCHER = 5;
    /** Before this round AE_AD_NUM carriers in AE_AD_DEN mine adamantium and the stock rebalancing is off (members:
     *  Mn share of collection at r100 0.33-0.55, mana share of deposits by r100 0.25-0.43; Ad@100 254-390, Mn@100
     *  172-247; Sprint1 Mn share 0.55). 2 in 3 gave Mn share 0.28 and Ad@100 451 in the Hah diagnostic game, 3 in 5 with
     *  uncapped carriers 0.34 and 509. */
    public static final int AE_AD_UNTIL = 300, AE_AD_NUM = 1, AE_AD_DEN = 2;
    /** Full spending, as observed: members never float (Sprint1 banks 30-350 Ad and 90-250 Mn at every 50-round sample
     *  of matches 19/7 and 19/9) and never cap carriers or launchers (Sprint1 MassiveL: 145 carriers and 155 launchers
     *  built by r900; reeceyang Maze: 188 launchers alive at r750). The army is light only early, by its Ad-leaning
     *  economy and its losses. AE_L_CAPPED restores the design sketch's cap: the team's live launchers <
     *  AE_L_BASE + round / AE_L_PER, live launchers estimated from team builds counted in Comms slots 62-63 and exact
     *  deaths (builds - live robots), a launcher taken to die AE_L_DEATH_W times as often as another unit. */
    public static final boolean AE_L_CAPPED = false;
    public static final int AE_L_BASE = 6, AE_L_PER = 100, AE_L_DEATH_W = 3;
    /** Extra launchers allowed over the cap while the building HQ sees enemy fighters (home defence; AE_L_CAPPED only). */
    public static final int AE_THREAT_EXTRA = 2;
    /** Amplifiers from this round, one per AE_L_PER_AMP launchers this HQ has built, at most AE_AMP_HQ per HQ, plus one
     *  per AE_AMP_PERIOD rounds after AE_AMP_LATE (members: first amplifier r159-176; Sprint1 2 per HQ at r150-200 and
     *  then none, reeceyang one per ~15 launchers; 4.7-11.3 per game mean). */
    public static final int AE_AMP_FROM = 150, AE_L_PER_AMP = 3, AE_AMP_HQ = 2, AE_AMP_LATE = 500, AE_AMP_PERIOD = 250;
    /** Launchers keep to their own half before this round: objectives are sightings nearer our HQs than theirs, then
     *  our and neutral islands on our side, then a guard point AE_GUARD_PCT% of the way to the enemy (members:
     *  engagements at prog 0.51-0.74 in the victim's frame by r300, pressure at the victim's HQ 0 by r250, first
     *  pressure r150-262). From this round on, the base objectives (enemy islands, the enemy HQ). */
    public static final int AE_MIDFIELD_FROM = 900, AE_GUARD_PCT = 45;   // v1-v2: 35 (with wells and neutral islands as posts)
    /** Before AE_FORWARD_FROM the guard point is AE_EARLY_GUARD_PCT% of the way (v3, 45% from the start: launchers alive
     *  at r100 3.5 of 17.5 built against the members' 6-9 of 12-19; Sprint1 9 of 19). */
    public static final int AE_FORWARD_FROM = 100, AE_EARLY_GUARD_PCT = 20;
    /** A launcher redraws its post (Launcher.pickPost) every this many rounds, scattered by up to AE_POST_SCATTER tiles.
     *  v1 (posts at wells, islands and one guard point, redrawn every 100 rounds): group p50 13.5 against the
     *  members' 3-4, ahead share 0.57 against 0.21-0.41 (10 quick cells against g_iter0). v2 (scatter 6, every 50
     *  rounds): group 13.5, ahead share 0.53; our launchers ambushed g_iter0's from posts (L died by r300 18 against
     *  g_iter0's 26; Sprint1 26.5 against 24), so v3 posts them forward, at the guard point only (v3: ahead share
     *  0.37, exposure 0.083, group 8.5). */
    public static final int AE_POST_ROUNDS = 50, AE_POST_SCATTER = 9;   // v2-v3: 6 (v3 group p50 8.5)
    /** Brave micro: with the action ready, step in to fire whatever the local count, at the edge of range, threats only
     *  as a tiebreak; with it spent, hold the tile unless a step lowers the threat by 2 or more (members: exposure
     *  0.071-0.077, damage taken per contact 13.4-21.1, first hit 0.27-0.35, behind in 1033 of Sprint1's 2260
     *  engagements; v1 with the base micro: 0.035, 9.1, 0.51; v2 brave when ready only: 0.036, 10.1, 0.57). */
    public static final boolean AE_BRAVE = true;
    // yaonam's THROWER variant (alternating C/L opening, no amplifiers, carriers throw) is not built (off in v1).

    // ---- HQ production
    /** Anchors are built from this round on. arch_adecon: members' first anchor r534-948, in 23-42% of games. */
    public static final int ANCHOR_START = 520;   // v1 500: first anchor median 528
    /** ... and only after this many launchers have been built by this HQ (an anchor needs an escort). */
    public static final int ANCHOR_MIN_LAUNCHERS = 6;
    /** Carriers are built while our live robot count (all types, HQs included) is below ROBOTS_BASE + ROBOTS_PER_WELL x
     *  known wells. Replaced a cap on carriers ever built per HQ (4 + round/40, max 24) that locked production out under
     *  attrition; strong field bots run 50-78 carriers (calib-g_iter0 census of losses: median 78 built vs our 21). */
    public static final int ROBOTS_BASE = 40, ROBOTS_PER_WELL = 20;   // arch_adecon: 30/15 in the base
    /** Before this round, carriers per HQ are capped by the number BUILT: CARRIER_BASE + round / CARRIER_PER_ROUNDS
     *  (g_iter0's cap); 0 disables. */
    public static final int EARLY_CAP_UNTIL = 0, CARRIER_BASE = 4, CARRIER_PER_ROUNDS = 40;   // arch_adecon: off (base 300): members
    // spend all Ad on carriers (Sprint1 RF: 16 built by r100 = 8 on r1 + 588 Ad collected and passive; bank 50-110 Ad).
    // With the cap at 4 + r/25 the Hah diagnostic floated 260-510 Ad from r100 and lost its carriers for good.
    /** An HQ builds at most one anchor per this many rounds (foundation2/Forest: anchors built every turn piled up in
     *  carriers that could not place them). */
    public static final int ANCHOR_PERIOD = 30;
    /** A carrier gives up an anchor it could not place within this many turns and returns it to an HQ. */
    public static final int ANCHOR_TIMEOUT = 150;
    /** Spawn on the tile fewest visible enemy fighters can reach (diag-top4: top bots fire at our spawn tiles). */
    public static final boolean SPAWN_SAFETY = true;
    /** HQ threat test: 0 = any enemy fighter in vision (g_iter0); 1 = real danger only (HQ.inDanger). */
    public static final int HQ_THREAT = 0;
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
    public static final boolean MICRO2 = false;
    /** Launcher cohesion (arm c_army1): with no enemy in sight a launcher advances only with GROUP_MIN launchers
     *  (itself included) in vision, follows the lowest-id launcher in vision when farther than r2 FOLLOW_R2, and
     *  otherwise regroups (nearest visible ally launcher, else back to the nearest own HQ). diag-top4: by r20 the top
     *  bots fielded 13 launchers in one mass while ours fought in ones and twos and lost 6 for 3. c_army1 passed
     *  delivery vs c_spawn1 (exposure -0.030, t -2.85; launchers lost -17, alive r250 +3.0, t +3.3; kills equal). */
    public static final boolean ARMY = false;
    public static final int GROUP_MIN = 3, FOLLOW_R2 = 8;
    /** A lone launcher still goes to an enemy sighting this close (r2) to one of our HQs: home defence. */
    public static final int HOME_DEFENCE_R2 = 100;
    /** Island observations older than this many rounds are not republished (slots carry no timestamp). */
    public static final int ISLAND_FRESH = 8;
    /** One amplifier per this many launchers built (comms coverage in the field). */
    public static final int LAUNCHERS_PER_AMP = 8;

    // ---- carriers
    /** A carrier returns home at this load (capacity 40; full loads maximise kg per trip, RULES economy). */
    public static final int CARRIER_RETURN_LOAD = 40;
    /** Carriers born before this round alternate adamantium/mana (the HQs need adamantium to grow the carrier fleet). */
    public static final int OPENING_ROUNDS = 40;
    /** Carrier role policy (Carrier.pickRole): 0 balance by HQ stock (c_nav1), 1 mana-first (c_mana1, rejected), 2 c_mana2.
     *  2 won the 174 calibration cells (+5 vs c_nav1) but on the replica panel the balanced policy did better (c_line5,
     *  ROLES 0, +3 vs c_line4, ROLES 2): mana-first starves the early anchor rush of adamantium. */
    public static final int ROLES = 0;
    public static final int MANA2_AD_EVERY = 5, MANA2_AD_HIGH = 250, MANA2_AD_LOW = 50, MANA2_MN_HIGH = 300;
    /** After the opening a carrier mines adamantium only while the HQ it delivers to holds less than this (a carrier
     *  plus some margin); otherwise mana. */
    public static final int AD_LOW = 120;
    /** Turns a carrier searches for a well of its own type before taking any well. */
    public static final int WELL_SEARCH_TURNS = 60;
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
    public static final boolean TELEMETRY = true;
    /** Bytecode-channel constant, calibrated per A.3; recalibrate whenever Telemetry.pad() or its call site changes. */
    public static final int PADK = 14;       // calibrated 2026-10-08: residue 14 on 8,561/8,561 turns (JDK 8u504, engine 3.0.15)
    /** Free 16-bit build tag reported in HDR (0 = working line). */
    public static final int TELE_BUILD = 102;   // arch_adecon
}
