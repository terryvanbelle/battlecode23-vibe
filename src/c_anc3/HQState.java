package c_anc3;

import battlecode.common.*;

/** Our HQ locations as published in Comms.HQ_LOC (refreshed until all HQs have registered, i.e. through round 2). */
public final class HQState {
    public static MapLocation[] ourHQs;

    public static void refresh() throws GameActionException {
        if (ourHQs == null || G.round <= 3) ourHQs = Comms.ourHQs();
    }

    /** Our HQ nearest to a location (null before the HQs register). */
    public static MapLocation nearest(MapLocation from) {
        return ourHQs == null || ourHQs.length == 0 ? null : G.nearest(from, ourHQs);
    }
}
