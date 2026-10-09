package arch_blob;

/**
 * Every tunable constant and every arm switch, each with the measurement or reason that set it.
 * g_iter0 values are first guesses from the rules (RULES.md) and are to be measured, not trusted.
 */
public final class C {
    // ==== ARCHETYPE arch_blob (S4): attrition blob that anchors only at the end (docs/ARCHETYPES.md 4.3; model
    // britacatalin.FinalBot, panel matches 22/204/539/605). A fork of c_line6 (5bc8e7e545ac). Every value below is set
    // from the member's 40 replica panel games (survey medians, ARCHETYPES.md 1 and 4.3) or its census/timeline rows.
    /** Opening per HQ: launchers first, OPEN_LAUNCHERS of them on r1, then carriers with the adamantium (member: first
     *  builds LLLLC per HQ on r1 and CCC on r2 in all 40 games). Afterwards a launcher whenever Mn >= 45, then a carrier. */
    public static final int OPEN_LAUNCHERS = 4;
    /** Carrier roles (ROLES = 3, the blob's mana-first policy): mana, except that one carrier in AD_EVERY (by id) mines
     *  adamantium while its HQ holds less than AD_NEED. AD_EVERY falls with the phase: before AD_MID_FROM, AD_EVERY_EARLY
     *  (member: Ad collected at r100 0-40 against 0-600 Mn, Mn share 0.87 [0.46-0.91]); then AD_EVERY_MID (member's Ad
     *  income grows to 1/7-1/4 of its Mn and its carriers grow 12 at r250 to 50-170 at r1000); from AD_BANK_FROM one in
     *  AD_EVERY_BANK, to bank 80/80 per anchor (design 4.3). */
    public static final int AD_NEED = 50, AD_EVERY_EARLY = 9, AD_MID_FROM = 250, AD_EVERY_MID = 5, AD_BANK_FROM = 1500, AD_EVERY_BANK = 3;
    /** ... and an adamantium carrier goes back to mana when its HQ holds at least AD_HIGH. */
    public static final int AD_HIGH = 150;
    /** Carriers built per HQ at most CARRIER_CAP0 + round / CARRIER_CAP_ROUNDS (member, BatSignal, 1 HQ: 7 alive at r100,
     *  12 at r250, 22 at r500, 51-62 at r1000, 95-129 at r1500; design 4.3 "3 per well" is the crowd at a well). */
    public static final int CARRIER_CAP0 = 4, CARRIER_CAP_ROUNDS = 30;   // v4: 7 per HQ at r100, 12 at r250, 37 at r1000
    /** ... and at most CARRIERS_PER_WELL per known well (shared slots, any type) shared among our HQs, plus 2, plus one
     *  per CARRIER_REPLACE_ROUNDS for losses (design 4.3: 3 per well; v3 Hah: 111 carriers jammed around one mid-map
     *  well from r800, mana income stopped, the HQs could not afford anchors and the game was lost on the tiebreak). */
    public static final int CARRIERS_PER_WELL = 3, CARRIER_REPLACE_ROUNDS = 150;
    /** ... and no carrier while CARRIER_CROWD of ours stand in the HQ's vision (v2 ReverseFunnel: 30 carriers jammed
     *  around a corner HQ, filled its spawn tiles from r300 and cut mana income to zero; the member runs 17-24 there). */
    public static final int CARRIER_CROWD = 9;
    /** Production stops here; the HQs bank for anchors (member: built_C and built_L freeze at r1800 in every long game,
     *  then Mn banks rise to 800-3,700 by r2000). */
    public static final int SAVE_FROM = 1800;
    /** The blob: launchers gather at the rally point (RALLY_PCT percent of the way from our HQs toward the predicted
     *  enemy HQs) until the leader (lowest id in vision) sees BLOB_MIN launchers (itself included): BLOB_BASE plus one per
     *  BLOB_ROUNDS rounds, at most BLOB_MAX (design 4.3: 12 + round/50, cap 40; member group size in contact 63, 200-580
     *  in its long games). A blob that falls below a third of BLOB_MIN with no enemy in sight returns to the rally.
     *  v2: the member holds midfield from r30 (BatSignal, match 22: its launchers at x 26-32 of 60 at r100-160, first
     *  contact r15-35 at prog 0.4-0.6) and besieges from r200; v1's rally at 35% with BLOB_MIN 12 let g_iter0 anchor 3
     *  islands unopposed and win by conquest at r286 (BatSignal). */
    public static final int BLOB_BASE = 6, BLOB_ROUNDS = 25, BLOB_MAX = 30, RALLY_PCT = 60;
    /** Followers keep within this r2 of the leader; the leader waits while fewer than half of the launchers it sees are
     *  that close ("the blob advances at the leader's pace"). */
    public static final int BLOB_FOLLOW_R2 = 8;
    /** With no enemy in sight a launcher within this r2 of one of our HQs always walks toward the rally point (v2
     *  BatSignal: followers holding beside the HQ jammed it with its carriers from r500). */
    public static final int HOME_CLEAR_R2 = 20;
    /** From QUIET_FROM a leader that has seen no enemy fighter for QUIET_GO rounds advances with 4 or more. */
    public static final int QUIET_FROM = 150, QUIET_GO = 50;
    /** An HQ that sees HELP_MIN or more enemy fighters, and more than our launchers in its vision, calls every launcher
     *  that is not on a siege ring (Comms.HELP). */
    public static final int HELP_MIN = 2;
    /** Spawn camp: a launcher within SIEGE_R2 of an enemy HQ with no enemy in sight holds a free tile at r2
     *  RING_MIN..RING_MAX from it (outside the r2 9 aura, within r2 16 of the near spawn tiles) and fires at newborns
     *  (member: victim robots killed within 5 rounds of birth 60 per game; engagements at prog 0.05-0.15 from r250 on). A
     *  launcher that finds no free ring tile in vision moves on to the next enemy HQ. */
    public static final int SIEGE_R2 = 64, RING_MIN = 10, RING_MAX = 25;
    /** A launcher on a ring that sees more than RING_FULL of our launchers moves on to the next enemy HQ (an HQ that sees
     *  none of ours keeps building anchors: v1 DefaultMap, g_iter0 anchored 5 islands). */
    public static final int RING_FULL = 14;
    /** From CLEAR_FROM two launchers in three hunt enemy-held islands before the anchors go down (design 4.3: the blob
     *  clears enemy islands from about r1700; member: our islands fall to 0 by r1000 in its long games). */
    public static final int CLEAR_FROM = 1700;
    /** ... and from HUNT_FROM one launcher in three hunts them, including the predicted images of the islands on our
     *  side (member: the victim's islands fall from 1-3 at r500 to 0 by r1000 in its long games; v1 Forest: g_iter0 kept
     *  4 islands to r2000 behind our blob and won the tiebreak 4-2). */
    public static final int HUNT_FROM = 400;
    /** Island tiebreak, not conquest: a carrier never places the anchor that would reach 75% of the islands (member:
     *  26 of its 28 wins on the r2000 islands tiebreak, 1-5 islands held at the end). */
    public static final boolean NO_CONQUEST = true;

    // ---- HQ production
    /** Anchors are built from this round on (arch_blob: member's first anchor r1858 [1839-1868], none before r1811). */
    public static final int ANCHOR_START = 1820;
    /** ... and only after this many launchers have been built by this HQ (an anchor needs an escort). */
    public static final int ANCHOR_MIN_LAUNCHERS = 0;
    /** Carriers are built while our live robot count (all types, HQs included) is below ROBOTS_BASE + ROBOTS_PER_WELL x
     *  known wells. Replaced a cap on carriers ever built per HQ (4 + round/40, max 24) that locked production out under
     *  attrition; strong field bots run 50-78 carriers (calib-g_iter0 census of losses: median 78 built vs our 21). */
    public static final int ROBOTS_BASE = 30, ROBOTS_PER_WELL = 15;
    /** Before this round, carriers per HQ are capped by the number BUILT: CARRIER_BASE + round / CARRIER_PER_ROUNDS
     *  (g_iter0's cap); 0 disables. */
    public static final int EARLY_CAP_UNTIL = 0, CARRIER_BASE = 4, CARRIER_PER_ROUNDS = 40;
    /** An HQ builds at most one anchor per this many rounds (foundation2/Forest: anchors built every turn piled up in
     *  carriers that could not place them). */
    public static final int ANCHOR_PERIOD = 5;   // arch_blob (design 4.3)
    /** A carrier gives up an anchor it could not place within this many turns and returns it to an HQ. */
    public static final int ANCHOR_TIMEOUT = 150;
    /** Spawn on the tile fewest visible enemy fighters can reach (diag-top4: top bots fire at our spawn tiles). */
    public static final boolean SPAWN_SAFETY = true;
    /** HQ threat test: 0 = any enemy fighter in vision (g_iter0); 1 = real danger only (HQ.inDanger). */
    public static final int HQ_THREAT = 1;   // arch_blob: the HQ keeps building under pressure
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
    public static final boolean MICRO2 = true;   // arch_blob: fire only where at most one enemy answers unless ahead by 2
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
    public static final int ROLES = 3;   // arch_blob: mana-first (see the archetype block)
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
    public static final int TELE_BUILD = 103;   // arch_blob
}
