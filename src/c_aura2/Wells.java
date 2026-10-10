package c_aura2;

import battlecode.common.*;

/** Wells known through comms (cheap membership test used to avoid re-reporting). */
public final class Wells {
    public static boolean known(MapLocation l) {
        try {
            int e = G.enc(l);
            for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
                int c = G.rc.readSharedArray(i);
                if (c == 0) return false;
                if ((c & 0xfff) == e) return true;
            }
        } catch (GameActionException ignored) { }
        return false;
    }
}
