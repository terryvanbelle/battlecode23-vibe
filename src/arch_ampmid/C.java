package arch_ampmid;

/**
 * Every tunable constant and every arm switch, each with the measurement or reason that set it.
 * g_iter0 values are first guesses from the rules (RULES.md) and are to be measured, not trusted.
 */
public final class C {
    // ==== ARCHETYPE arch_ampmid (S2): mana army with an amplifier at r36 that takes midfield (docs/ARCHETYPES.md 4.5;
    // member pranayagra.finalbotfinal, panel matches 10/199/534/600). Built as arch_swarm (b646f1e92c6b, v4c) plus the
    // section 4.5 edits; arch_swarm is itself a fork of c_line6 (5bc8e7e545ac). Every value below is set from the
    // member's 40 replica panel games (survey rows; matches/10/extract; replay 10.bc23 game 3 --map-at 40-200).
    /** Amplifiers. The first is built by HQ i (Comms HQ_LOC order) from round AMP_FIRST + AMP_STAGGER x i: the member's
     *  first amplifier is born at r36 in 36 of 40 games (r34-37), and further ones follow by HQ: Cat/Hah/MassiveL/
     *  IslandHopping (2 HQs) r36 and r66-84, DefaultMap (3) r34/66/151, Forest (4) r36/76/111/162. Then one more per
     *  AMP_EVERY_L launchers this HQ has built, at most AMP_MAX per game for the team (split over the HQs). The design's
     *  sketch said one per 3 launchers; the member builds 9.4 amplifiers per 190 launchers (built_A / built_L 0.05) and has
     *  2-5 alive at r250 (one per HQ plus 0-2), so one per 3 would hold 12 by r150. Each HQ reserves its first
     *  amplifier's cost from AMP_RESERVE rounds before it is due (HQ.ampDue). */
    public static final int AMP_FIRST = 36, AMP_STAGGER = 33, AMP_EVERY_L = 15, AMP_MAX = 12, AMP_RESERVE = 10;
    /** ... HQ 0 reserves its first amplifier's cost from round 1, so its round-2 carriers leave 30 Ad (v2 quick, Cornucopia:
     *  the HQs spent all 200 Ad on carriers, the 1-in-6 adamantium carriers brought 15 Ad by r100, first amplifier r111). */
    /** Midfield. Before HQ_APPROACH_FROM the launchers' home is the rally point: the midpoint between the team target
     *  (the predicted enemy HQ nearest our HQs' centroid) and our HQ nearest it (Launcher.rallyPoint); launchers hold
     *  within r2 RALLY_HOLD_R2 of it (member: launchers in the middle band at r40-r150 on DefaultMap and Cat;
     *  engagements before r300 at prog 0.48 in our frame; first pressure on our HQs r200). The design said r150; v2
     *  quick (r150) pressed g_iter0's HQs 370 launcher-buckets by r250 (median; member 34), the siege arriving from
     *  r175; by the per-bucket pressure of v2's games, r225 puts the median near 70. */
    public static final int HQ_APPROACH_FROM = 225, RALLY_HOLD_R2 = 10;
    /** ... and nothing before HQ_APPROACH_FROM takes them within r2 NO_APPROACH_R2 of a predicted enemy HQ (objectives,
     *  raid wells, islands, sightings), and marching never steps deeper into r2 NO_APPROACH_R2 of a seen enemy HQ (Nav):
     *  the pressure zone of the victim HQ (member: pressure on our HQs by r250 median 34 launcher-buckets, 0 on 6 of
     *  10 maps against g_iter0). */
    public static final int NO_APPROACH_R2 = 34;
    /** Raids: a group of RAID_GROUP or more launchers in vision (itself included) raids the uncleared predicted enemy well
     *  in the enemy half nearest the rally point, then comes back to the rally point. v1 kept RAID_HOLD = 6 holders at the rally point and
     *  let only the surplus raid: it raided too little (our carriers killed by r300 8.8 against the member's 13.2, first
     *  engagement won 0.5 against 0.85), and on Cat the holders lost the opening brawl 16 kills to 33 where the same
     *  launchers pushing into g_iter0's wells won it 19 to 7 (driver games 6 and 8). The member on Cat at r80: its
     *  launchers at our mana well x 17-20, 13-19 of our carriers dead by r300. RAID_GROUP 3 (v2, v3) -> 4 (v4): v3 won 11
     *  of 20 first engagements (member 0.85; faithful from 0.6); on 10 of v3's cells replayed on the driver, 4 turned
     *  DefaultMap B's first engagement from a 2-1 loss into a 5-3 win and changed no other first engagement or game. */
    public static final int RAID_HOLD = 0, RAID_GROUP = 4;
    /** Engagement: the step-in scoring is used when locally ahead by AHEAD_MIN or more (allies in vision + 1 - enemy
     *  fighters); otherwise the parity hold (member: first engagement won 0.85 with 0.98 more launchers at its start;
     *  ahead share 0.70). arch_swarm used 2. */
    public static final int AHEAD_MIN = 1;
    /** Economy: one carrier in AD_EVERY (by id) mines adamantium, the rest mana (member: Ad@100 122 [48-167], Mn@100
     *  305 [244-562], Mn share 0.70). Replaces arch_swarm's 1-in-8-on-request and 1-in-4-from-r200 rules. */
    public static final int AD_EVERY = 6;   // v1 quick, 1 in 4: Ad@100 215 (driver game, 1 in 3: 222)
    /** A loaded carrier with an enemy fighter within r2 9 throws its load at it once its health is at most THROW_HP
     *  (arch_swarm: 60, after 5 hits of 20 on 150): member 7.1 throws per game; v1 quick 3.9, v2 driver games 0-5. */
    public static final int THROW_HP = 110;

    // ---- inherited from arch_swarm (S1), still read by the code
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
    /** From HQ_APPROACH_FROM (arch_ampmid): the siege ring around the enemy HQ, r2 RING_MIN..RING_MAX: outside the r2 9
     *  aura, close enough to hit spawn tiles (S1 members: first pressure on our HQ r75-100, 236-975 enemy launcher-rounds within r2 34 of our HQs by r250). */
    public static final int RING_MIN = 16, RING_MAX = 34;
    /** From HQ_APPROACH_FROM (arch_ampmid): carrier raid on predicted enemy wells within r2 RAID_R2 of an enemy HQ; a raided well with no enemy carrier in
     *  view is skipped for RAID_CLEAR_ROUNDS (members killed 4.5-7.3 of our carriers by r150, at prog 0.10-0.14). */
    public static final int RAID_R2 = 100, RAID_CLEAR_ROUNDS = 40;
    /** Launchers hunt enemy-held islands from this round. The design said r250; v2 quick lost ReverseFunnel by conquest
     *  at r224 to g_iter0's anchor rush (the members never lose to it: 0 of 40 losses on that map), so from the start. */
    public static final int ISLAND_HUNT_START = 0;
    /** A shared enemy sighting is an objective only within this r2 of the launcher (the swarm keeps to its siege). */
    public static final int SIGHTING_R2 = 64;

    // ---- HQ production
    /** Anchors are built from this round on (rules: anchors decide the game; first guess). */
    public static final int ANCHOR_START = 425;   // arch_ampmid: design 4.5 says r440; first anchor target 440-470 (member
                                                 // 451); first anchor 43 rounds after ANCHOR_START in arch_swarm (293 vs 250), 28 in v1 quick (438 vs 410)
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
    public static final int GROUP_MIN = 4, FOLLOW_R2 = 8;
    /** arch_swarm: launchers within this r2 of our nearest HQ are still forming (need GROUP_MIN to leave). */
    public static final int FORM_R2 = 50;
    /** A lone launcher still goes to an enemy sighting this close (r2) to one of our HQs: home defence. */
    public static final int HOME_DEFENCE_R2 = 20;   // arch_swarm: 20 (base 100): on DefaultMap every sighting lay within r2 100 of one of
                                                    // our three HQs, so lone launchers chased them (alone 0.32, exposed 0.18 in a driver game)
    /** Island observations older than this many rounds are not republished (slots carry no timestamp). */
    public static final int ISLAND_FRESH = 8;

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
    public static final boolean TELEMETRY = true;
    /** Bytecode-channel constant, calibrated per A.3; recalibrate whenever Telemetry.pad() or its call site changes. */
    public static final int PADK = 14;       // calibrated 2026-10-08: residue 14 on 8,561/8,561 turns (JDK 8u504, engine 3.0.15)
    /** Free 16-bit build tag reported in HDR (0 = working line). */
    public static final int TELE_BUILD = 105;   // arch_ampmid
}
