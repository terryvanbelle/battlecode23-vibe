package bot;

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
    /** Carriers per HQ: CARRIER_BASE + round / CARRIER_PER_ROUNDS, capped at CARRIER_MAX (first guess). */
    public static final int CARRIER_BASE = 4, CARRIER_PER_ROUNDS = 40, CARRIER_MAX = 24;
    /** One amplifier per this many launchers built (comms coverage in the field). */
    public static final int LAUNCHERS_PER_AMP = 8;

    // ---- carriers
    /** A carrier returns home at this load (capacity 40; full loads maximise kg per trip, RULES economy). */
    public static final int CARRIER_RETURN_LOAD = 40;
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
}
