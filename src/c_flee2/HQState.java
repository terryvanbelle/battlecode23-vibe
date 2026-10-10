package c_flee2;

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

    /** c_flee2: our HQ nearest to a location whose pressed flag (Comms.AD_FLAGS bit PRESS_SHIFT + index) is clear;
     *  nearest(from) when every HQ is pressed (null before the HQs register). */
    public static MapLocation safest(MapLocation from) throws GameActionException {
        if (ourHQs == null || ourHQs.length == 0) return null;
        int flags = Comms.read(Comms.AD_FLAGS);
        MapLocation best = null;
        int bd = Integer.MAX_VALUE;
        for (int i = ourHQs.length; --i >= 0; ) {
            MapLocation h = ourHQs[i];
            int idx = Comms.hqIndex(h);
            if (idx >= 0 && ((flags >>> (Comms.PRESS_SHIFT + idx)) & 1) != 0) continue;
            int d = from.distanceSquaredTo(h);
            if (d < bd) { bd = d; best = h; }
        }
        return best != null ? best : nearest(from);
    }

    /** c_flee2: where a carrier takes its load or retreats: the nearest HQ unless it is pressed and an unpressed HQ
     *  lies at most C.HOME_DETOUR x its dist2 away (twice the distance). */
    public static MapLocation homeFor(MapLocation from) throws GameActionException {
        MapLocation n = nearest(from);
        if (n == null) return null;
        int idx = Comms.hqIndex(n);
        if (!Comms.pressed(idx)) return n;
        MapLocation s = safest(from);
        return s != null && !s.equals(n) && from.distanceSquaredTo(s) <= C.HOME_DETOUR * from.distanceSquaredTo(n) ? s : n;
    }
}
