package arch_horde;

/**
 * Every tunable constant and every arm switch, each with the measurement or reason that set it.
 * g_iter0 values are first guesses from the rules (RULES.md) and are to be measured, not trusted.
 */
public final class C {
    // ==== ARCHETYPE arch_horde (S3): balanced horde with throws, late amplifiers and island holding (docs/ARCHETYPES.md
    // 4.4; model georgezhang02.CB_tuning2, panel matches 8/197/532/598). A fork of c_line6 (5bc8e7e545ac). Every value
    // below is set from the member's 40 replica panel games (survey medians, ARCHETYPES.md 1 and 4.4) or its census and
    // timeline rows (matches/{8,197,532,598}/extract). Base constants changed for the archetype are marked arch_horde.
    /** Opening by map. min(W, H) >= BIG_MAP: carriers only on round 1, 4 per HQ (member: first builds CCCC per HQ on r1,
     *  then LLLL on r2, on Maze, Forest, Cat, Cornucopia and MassiveL in all 20 games). Smaller maps: launchers first on
     *  round 1, then one carrier (design 4.4: 4 launchers and 1 carrier; member: LLL per HQ on r1, carriers on r2). */
    public static final int BIG_MAP = 40;
    /** Carrier cap on LIVE carriers (census, Comms.CENSUS): CARRIERS_PER_WELL per known well (shared slots, any type),
     *  at least CARRIER_MIN_PER_HQ per HQ, at most CARRIER_MAX; no early cap (design 4.4: 6 per well, early cap removed;
     *  member: carriers per well 5 [4-6], 16 alive at r100, 31.5 [14.5-40.5] at r250, 120-860 by r2000 in long games). */
    public static final int CARRIERS_PER_WELL = 6, CARRIER_MIN_PER_HQ = 6, CARRIER_MAX = 150;
    /** Amplifiers: none before AMP_START; from then on one per AMP_PER_L launchers this HQ built since AMP_START
     *  (design 4.4: from r260 one per 4 launchers, >= 20 a game; member: first amplifier r428 [262-477], 26.6 a game). */
    public static final int AMP_START = 260, AMP_PER_L = 7;   // v2 at 4: 54 a game, 207 on Cornucopia
    /** Throws: a carrier holding at least THROW_LOAD throws it at an enemy launcher or carrier within THROW_R2 when one of
     *  our launchers is in its vision (r2 20) or its own health is at most THROW_HP, then goes back to mine (design 4.4;
     *  member: 46 throws a game, 3.6 of our robots killed by a throw). */
    public static final int THROW_LOAD = 20, THROW_R2 = 9, THROW_HP = 90;
    /** Island holding: a launcher with id % GARRISON_MOD == 0 and no enemy in sight stands on a free square of one of our
     *  islands (spread over our islands by id), which heals the anchor and blocks the square (design 4.4: launchers
     *  garrison owned islands; member: island-rounds 2020 a game, 15 of 33 wins on the r2000 island tiebreak). The other
     *  launchers march as the base does (sightings, enemy islands, the enemy HQ ring, where they fire at spawns). */
    public static final int GARRISON_MOD = 3;
    /** Team anchor clock (Comms.ANCHOR_CLOCK): the first anchor from ANCHOR_START, then the n-th next one no sooner than
     *  ANCHOR_GAP0 + (n - 1) x ANCHOR_GAP_STEP rounds after the previous one (member: 3-10 anchors a game, at a slowing
     *  pace: DefaultMap r298, 387, 568, 1184; it held 4 of 6 islands from r1000 to r2000; 15 of its 33 wins on the r2000
     *  island tiebreak, conquests at r828 [612-1200]). v1 (per-HQ period 30) conquered at r509-566 on 4 maps. */
    public static final int ANCHOR_GAP0 = 100, ANCHOR_GAP_STEP = 60;
    /** ... except while the enemy holds at least HURRY_ENEMY_ISLANDS islands (shared slots): then the team gap is
     *  ANCHOR_PERIOD, so our anchors take the free islands its conquest needs (v3: c_line6 conquered Maze at r213,
     *  DefaultMap at r289, Hah at r284 and ReverseFunnel at r584 while our clock waited). */
    public static final int HURRY_ENEMY_ISLANDS = 2;
    /** The carrier cap also grows by one per HQ every CARRIER_GROW rounds (member: alive carriers keep growing, 31 at
     *  r250 to 120-860 at r2000; v1's fixed 6 per well froze Forest at 65 built from r300 with 4,000 Ad unspent). */
    public static final int CARRIER_GROW = 100;
    /** Roles (ROLES = 4): one carrier in ROLE_AD_EVERY (by id) mines adamantium, the others mana, from the first
     *  carrier on; a carrier whose type has no known well takes the other type; from ROLE_BALANCE_FROM it mines what its
     *  HQ is short of (base rule). Member: Mn share at r100 0.49 [0.31-0.71]; Mn collected by r100 370 [238-440],
     *  DefaultMap 979 of 1,084. v2 (nearest-well type) mined no mana by r100 on Maze and Cat (all Ad wells near the
     *  HQs) and lost Maze to c_line6 at r241 and to g_iter0 at r358. */
    public static final int ROLE_AD_EVERY = 4, ROLE_BALANCE_FROM = 100;   // v3 at 3: Mn share 0.458, DefaultMap Mn@100 439 vs g_iter0's 694
    /** A carrier's first search for a well of its type heads toward the map centre, at most this many tiles from home. */
    public static final int EXPLORE_FIRST = 12;
    /** A launcher treats an island it saw enemy-held within this many rounds as enemy-held while the shared slot does not
     *  say it is ours (no amplifier writes comms before AMP_START, so far islands rarely reach the shared slots; v3 lost
     *  Maze, Hah and ReverseFunnel to c_line6's anchors at r213-584 with launchers chasing nothing). */
    public static final int OWN_ISLAND_MEMORY = 100;
    // ---- HQ production
    /** Anchors are built from this round on (rules: anchors decide the game; first guess). */
    public static final int ANCHOR_START = 290;   // arch_horde: design 4.4 (member first anchor 350 [285-574])
    /** ... and only after this many launchers have been built by this HQ (an anchor needs an escort). */
    public static final int ANCHOR_MIN_LAUNCHERS = 6;
    /** Carriers are built while our live robot count (all types, HQs included) is below ROBOTS_BASE + ROBOTS_PER_WELL x
     *  known wells. Replaced a cap on carriers ever built per HQ (4 + round/40, max 24) that locked production out under
     *  attrition; strong field bots run 50-78 carriers (calib-g_iter0 census of losses: median 78 built vs our 21). */
    public static final int ROBOTS_BASE = 30, ROBOTS_PER_WELL = 15;
    /** Before this round, carriers per HQ are capped by the number BUILT: CARRIER_BASE + round / CARRIER_PER_ROUNDS
     *  (g_iter0's cap); 0 disables. */
    public static final int EARLY_CAP_UNTIL = 0, CARRIER_BASE = 4, CARRIER_PER_ROUNDS = 40;   // arch_horde: no early cap (design 4.4)
    /** An HQ builds at most one anchor per this many rounds (foundation2/Forest: anchors built every turn piled up in
     *  carriers that could not place them). */
    public static final int ANCHOR_PERIOD = 30;
    /** A carrier gives up an anchor it could not place within this many turns and returns it to an HQ. */
    public static final int ANCHOR_TIMEOUT = 150;
    /** Spawn on the tile fewest visible enemy fighters can reach (diag-top4: top bots fire at our spawn tiles). */
    public static final boolean SPAWN_SAFETY = true;
    /** HQ threat test: 0 = any enemy fighter in vision (g_iter0); 1 = real danger only (HQ.inDanger). */
    public static final int HQ_THREAT = 1;   // arch_horde: keep building under pressure (real danger only)
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
    public static final boolean MICRO2 = true;   // arch_horde: member exposure 0.010, damage taken low; first_hit 0.87
    /** Launcher cohesion (arm c_army1): with no enemy in sight a launcher advances only with GROUP_MIN launchers
     *  (itself included) in vision, follows the lowest-id launcher in vision when farther than r2 FOLLOW_R2, and
     *  otherwise regroups (nearest visible ally launcher, else back to the nearest own HQ). diag-top4: by r20 the top
     *  bots fielded 13 launchers in one mass while ours fought in ones and twos and lost 6 for 3. c_army1 passed
     *  delivery vs c_spawn1 (exposure -0.030, t -2.85; launchers lost -17, alive r250 +3.0, t +3.3; kills equal). */
    public static final boolean ARMY = false;   // arch_horde v2: off (v1 Forest: 23,747 regroup turns, launchers held our half all game)
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
    public static final int ROLES = 4;   // arch_horde: nearest-well roles (see ROLE_BALANCE_FROM)
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
    public static final int TELE_BUILD = 104;   // arch_horde (ARCHETYPES.md 3.1)
}
