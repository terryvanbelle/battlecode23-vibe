package c_sm1;

import battlecode.common.*;

/**
 * c_mid1 (C.MID): the contested mana well, "the site". jmerle.camel_case_v30_final mines the mana wells that lie
 * halfway between the HQs and are the nearest mana well of one of ours (Forest's axis pair (29,48)/(30,48), 2,990 Mn a
 * game against our 6; Cornucopia's ring wells, which we hold in r0-299 and then lose), and keeps 2-9 launchers there
 * from r0, where we keep none (240 panel games vs c_well9, scratchpad mid1/study).
 *
 * The site is a shared mana well W (Comms well slots) with
 *  - p(W) = d(W, our nearest HQ) / (d(W, our nearest HQ) + d(W, their nearest HQ)) in C.MID_P_LO..C.MID_P_HI percent
 *    under every surviving symmetry candidate (their HQs = images of ours under that candidate),
 *  - farther than r2 C.MID_HOME_D2 from our nearest HQ,
 *  - the nearest shared mana well of at least one of our HQs ("urgent": that HQ has nothing nearer to mine);
 * the one nearest our HQ centroid, ties to the lower enc, so every reader agrees. Also farther than r2 C.MID_HOME_D2
 * from every candidate enemy HQ (banded). HQ 0 chooses it every C.MID_EVERY rounds and publishes it in Comms.SYM_ELIM
 * bits 3-14 (0 = none). The squad (Launcher, id % C.MID_MOD == 0, one tour of C.MID_TOUR rounds each) holds it from
 * outside the free zone (free: r2 C.MID_FREE_R2 of the site or of its twin); carriers treat a well within
 * r2 C.MID_TWIN_R2 of it as the site (Carrier.survive, gather). No RNG anywhere here.
 */
public final class Mid {
    /** HQ 0: choose and publish the site from the shared well slots, our HQs and the surviving symmetries. */
    static void update() throws GameActionException {
        MapLocation[] ours = HQState.ourHQs;
        int enc = 0;
        if (ours != null && ours.length > 0) {
            int[] slots = new int[Comms.NWELLS];
            int n = 0;
            boolean hot = false;
            for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
                int c = Comms.read(i);
                if (c == 0) break;
                slots[n++] = c;
                if (c >= 0x4000) hot = true;
            }
            enc = pick(slots, n, ours, MapMem.cand);
            // C.HOT: the site and its twin are never hot (Carrier.front); a mark set before HQ 0 chose the site (the
            // probe reaches Forest's pair at r20-40) is cleared here instead of keeping carriers off it for 64-96 rounds
            if (hot && enc != 0) {
                MapLocation s = G.dec(enc);
                for (int i = n; --i >= 0; ) {
                    int c = slots[i];
                    if (c >= 0x4000 && G.dec(c & 0xfff).distanceSquaredTo(s) <= C.MID_TWIN_R2) Comms.put(Comms.WELLS + i, c & 0x3fff);
                }
            }
        }
        Comms.setSite(enc);
    }

    /** The site's enc (0 = none) among n well-slot values (Comms layout: type in bits 12-13, enc in bits 0-11). Pure
     *  but for MapMem.img's use of G.W and G.H. */
    static int pick(int[] slots, int n, MapLocation[] ours, int cand) {
        int nh = ours.length;
        // each HQ's nearest shared mana well (dist2), for the urgency test
        int[] near = new int[nh];
        for (int h = nh; --h >= 0; ) near[h] = Integer.MAX_VALUE;
        for (int i = n; --i >= 0; ) {
            if (Comms.wellType(slots[i]) != 2) continue;
            MapLocation l = G.dec(slots[i] & 0xfff);
            for (int h = nh; --h >= 0; ) { int d = l.distanceSquaredTo(ours[h]); if (d < near[h]) near[h] = d; }
        }
        int cx = 0, cy = 0;
        for (int h = nh; --h >= 0; ) { cx += ours[h].x; cy += ours[h].y; }
        MapLocation centre = new MapLocation(cx / nh, cy / nh);
        int best = 0, bd = Integer.MAX_VALUE;
        for (int i = n; --i >= 0; ) {
            if (Comms.wellType(slots[i]) != 2) continue;
            int e = slots[i] & 0xfff;
            MapLocation l = G.dec(e);
            int dOwn = Integer.MAX_VALUE;
            boolean urgent = false;
            for (int h = nh; --h >= 0; ) {
                int d = l.distanceSquaredTo(ours[h]);
                if (d < dOwn) dOwn = d;
                if (d == near[h]) urgent = true;
            }
            if ((C.MID_URGENT && !urgent) || dOwn <= C.MID_HOME_D2 || !banded(l, dOwn, ours, cand)) continue;
            int dc = l.distanceSquaredTo(centre);
            if (dc < bd || (dc == bd && e < best)) { bd = dc; best = e; }
        }
        return best;
    }

    /** Whether l, r2 dOwn from our nearest HQ, is in the band under every candidate in cand (none: false), and farther
     *  than r2 C.MID_HOME_D2 from every candidate enemy HQ (their home wells: Maze's (22,31), DefaultMap's (24,10)). */
    static boolean banded(MapLocation l, int dOwn, MapLocation[] ours, int cand) {
        boolean any = false;
        for (int s = 1; s <= 4; s <<= 1) {
            if ((cand & s) == 0) continue;
            int dEn = Integer.MAX_VALUE;
            for (int k = ours.length; --k >= 0; ) { int d = l.distanceSquaredTo(MapMem.img(s, ours[k])); if (d < dEn) dEn = d; }
            if (dEn <= C.MID_HOME_D2 || !inBand(dOwn, dEn)) return false;
            any = true;
        }
        return any;
    }

    /** p = a / (a + b), a = sqrt(dOwn), b = sqrt(dEn), within C.MID_P_LO..C.MID_P_HI percent, in integers:
     *  p >= lo  <=>  (100 - lo)^2 dOwn >= lo^2 dEn;  p <= hi  <=>  (100 - hi)^2 dOwn <= hi^2 dEn. */
    static boolean inBand(int dOwn, int dEn) {
        long a = dOwn, b = dEn, lo = C.MID_P_LO, hi = C.MID_P_HI;
        return (100 - lo) * (100 - lo) * a >= lo * lo * b && (100 - hi) * (100 - hi) * a <= hi * hi * b;
    }

    // ---------------------------------------------------------------- readers (launchers, carriers)
    static int siteV = -1;
    static MapLocation siteL;

    /** The published site, or null (one shared-array read; decoded only when the slot changes). */
    static MapLocation site() throws GameActionException {
        int v = Comms.siteOf(Comms.read(Comms.SYM_ELIM));
        if (v != siteV) { siteV = v; siteL = G.dec(v); }
        return siteL;
    }

    /** Whether l is the published site or its twin (within r2 C.MID_TWIN_R2). */
    static boolean isSite(MapLocation l) throws GameActionException {
        MapLocation s = site();
        return s != null && l != null && s.distanceSquaredTo(l) <= C.MID_TWIN_R2;
    }

    static int twinV = -1, twinRound;
    static MapLocation twinL;

    /** The site's twin: a shared well (any type) within r2 C.MID_TWIN_R2 of the site, or null. Rescanned when the site
     *  changes and every 20 rounds (a carrier may publish the twin after the site; 16 slots, about 400 bytecodes). */
    static MapLocation twin() throws GameActionException {
        MapLocation s = site();
        if (s == null) return null;
        if (twinV != siteV || G.round - twinRound >= 20) {
            twinV = siteV;
            twinRound = G.round;
            twinL = null;
            for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
                int c = Comms.read(i);
                if (c == 0) break;
                MapLocation l = G.dec(c & 0xfff);
                int d = l.distanceSquaredTo(s);
                if (d > 0 && d <= C.MID_TWIN_R2) { twinL = l; break; }
            }
        }
        return twinL;
    }

    /** Whether l is in the free zone (Launcher.midHold: never a holder's tile): within r2 C.MID_FREE_R2 of the
     *  published site or of its twin. False with no site. */
    static boolean free(MapLocation l) throws GameActionException {
        MapLocation s = site();
        return s != null && inFree(l, s, twin());
    }

    /** free() for site s and twin t (t may be null). Pure. */
    static boolean inFree(MapLocation l, MapLocation s, MapLocation t) {
        return l.distanceSquaredTo(s) <= C.MID_FREE_R2 || (t != null && l.distanceSquaredTo(t) <= C.MID_FREE_R2);
    }
}
