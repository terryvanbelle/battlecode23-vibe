package c_line4;

/**
 * Every tunable constant and every arm switch, each with the measurement or reason that set it.
 * g_iter0 values are first guesses from the rules (RULES.md) and are to be measured, not trusted.
 */
public final class C {
    // ---- HQ production
    /** Anchors are built from this round on (rules: anchors decide the game; first guess). */
    public static final int ANCHOR_START = 120;
    /** ... and only after this many launchers have been built by this HQ (an anchor needs an escort). */
    public static final int ANCHOR_MIN_LAUNCHERS = 6;
    /** Carriers are built while our live robot count (all types, HQs included) is below ROBOTS_BASE + ROBOTS_PER_WELL x
     *  known wells. Replaced a cap on carriers ever built per HQ (4 + round/40, max 24) that locked production out under
     *  attrition; strong field bots run 50-78 carriers (calib-g_iter0 census of losses: median 78 built vs our 21). */
    public static final int ROBOTS_BASE = 30, ROBOTS_PER_WELL = 15;
    /** An HQ builds at most one anchor per this many rounds (foundation2/Forest: anchors built every turn piled up in
     *  carriers that could not place them). */
    public static final int ANCHOR_PERIOD = 30;
    /** A carrier gives up an anchor it could not place within this many turns and returns it to an HQ. */
    public static final int ANCHOR_TIMEOUT = 150;
    /** Spawn on the tile fewest visible enemy fighters can reach (diag-top4: top bots fire at our spawn tiles). */
    public static final boolean SPAWN_SAFETY = true;
    /** Launchers are built in batches of this many in one turn (unless the HQ is threatened). 1 = no batching: c_batch1
     *  (3) failed delivery on diag-top4 (launchers alive r100 -3.0, t -4.6; kills -9.5, t -6.2). */
    public static final int LAUNCHER_BATCH = 1;
    /** Launcher fight scoring: false = g_iter0's; true = c_micro1's (pinned enemies threaten r2 16, step in only where
     *  at most one enemy answers unless superior, stay put on ties). c_micro1 failed delivery on diag-top4 vs c_mana1:
     *  exposure up (+0.029, t +1.75), damage per contact up, kills -5.3 (t -2.3), launchers alive at r100 -1.7. */
    public static final boolean MICRO = false;
    /** Launcher cohesion (arm c_army1): with no enemy in sight a launcher advances only with GROUP_MIN launchers
     *  (itself included) in vision, follows the lowest-id launcher in vision when farther than r2 FOLLOW_R2, and
     *  otherwise regroups (nearest visible ally launcher, else back to the nearest own HQ). diag-top4: by r20 the top
     *  bots fielded 13 launchers in one mass while ours fought in ones and twos and lost 6 for 3. c_army1 passed
     *  delivery vs c_spawn1 (exposure -0.030, t -2.85; launchers lost -17, alive r250 +3.0, t +3.3; kills equal). */
    public static final boolean ARMY = true;
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
    /** Carrier role policy (Carrier.pickRole): 0 balance by HQ stock (c_nav1), 1 mana-first (c_mana1, rejected), 2 c_mana2
     *  (kept: vs c_nav1 net +5, +1.3 SE; Mn by r100 +62, t +8.9; launchers alive r100 +0.9, r250 +1.3). */
    public static final int ROLES = 2;
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
    public static final int TELE_BUILD = 0;
}
