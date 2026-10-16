package c_mid1;

import battlecode.common.MapLocation;

/** c_mid1's contested mana well (Mid): the p band (Mid.inBand), the site choice (Mid.pick) on the 10 panel maps and the
 *  site bits of Comms.SYM_ELIM. Map data: our HQs and mana wells from the c_well9 panel replay 7601 (we are side A;
 *  scratchpad mid1/study/mapinfo_7601b.txt). The study's census: the site should be Forest's (29,48) and a Cornucopia
 *  ring well; nothing on BatSignal, Cat, DefaultMap, Hah, IslandHopping, Maze (its (27,18) is r2 45 from our HQ),
 *  MassiveL (once its home (2,0) is known) and ReverseFunnel; never an enemy home well; the free zone of the hold
 *  (Mid.inFree). Exits non-zero on a failure. */
public class Mid1Test {
    static final int ROT = 1, FLIP_X = 2, FLIP_Y = 4, ALL = 7;

    public static void main(String[] a) {
        // the band: p = a / (a + b) with a^2 = dOwn, b^2 = dEn
        check(Mid.inBand(324, 361), "Forest (29,48): 18 vs 19 tiles is in the band");
        check(!Mid.inBand(208, 2260), "Forest (8,12): r2 208 from (0,0), 2,260 from (52,30), p .23, is not");
        check(Mid.inBand(35 * 35, 65 * 65) && !Mid.inBand(35 * 35 - 1, 65 * 65), "p = .35 is the lower edge, inclusive");
        check(Mid.inBand(65 * 65, 35 * 35) && !Mid.inBand(65 * 65 + 1, 35 * 35), "p = .65 is the upper edge, inclusive");
        check(!Mid.inBand(100, Integer.MAX_VALUE), "no enemy HQ: not in the band");

        // the 10 panel maps, every mana well known, under the true symmetry and while undecided
        map("Forest", 60, 60, FLIP_X, hq(0, 0, 6, 30, 7, 30, 11, 48), mn(8, 12, 51, 12, 29, 48, 30, 48), loc(29, 48));
        map("Cornucopia", 59, 59, ROT, hq(29, 51, 10, 18, 48, 18), mn(26, 24, 32, 24, 23, 29, 35, 29, 26, 34, 32, 34), loc(26, 34));
        map("Maze", 50, 50, ROT, hq(11, 2, 3, 46, 21, 21),
            mn(17, 9, 39, 10, 46, 15, 27, 18, 37, 23, 12, 26, 22, 31, 3, 34, 10, 39, 32, 40), null);
        map("DefaultMap", 32, 32, ROT, hq(4, 26, 13, 23, 25, 18), mn(11, 8, 24, 10, 7, 21, 20, 23), null);
        map("BatSignal", 60, 20, FLIP_X, hq(3, 10), mn(27, 6, 32, 6, 10, 11, 49, 11), null);
        map("Cat", 50, 50, FLIP_X, hq(14, 35, 11, 25), mn(20, 32, 29, 32), null);
        map("Hah", 50, 25, FLIP_X, hq(4, 18, 10, 7), mn(14, 11, 35, 11, 21, 14, 28, 14), null);
        map("IslandHopping", 60, 30, FLIP_X, hq(6, 23, 15, 3), mn(20, 13, 39, 13, 16, 15, 43, 15), null);
        map("MassiveL", 40, 40, ROT, hq(7, 5, 2, 37), mn(2, 0, 39, 0, 18, 14, 21, 25, 0, 39, 37, 39), null);
        map("ReverseFunnel", 40, 20, FLIP_Y, hq(6, 15, 0, 19), mn(2, 2, 21, 9, 21, 10, 2, 17), null);

        // Forest as the knowledge grows: no site until a carrier publishes the pair; either well of it is the site
        MapLocation[] forest = hq(0, 0, 6, 30, 7, 30, 11, 48);
        G.W = 60; G.H = 60;
        check(pick(mn(8, 12), forest, FLIP_X) == 0, "Forest, only the home well (8,12): no site");
        check(pick(mn(8, 12, 51, 12), forest, FLIP_X) == 0, "Forest, (8,12) and their (51,12): no site");
        check(pick(mn(8, 12, 30, 48), forest, ALL) == G.enc(loc(30, 48)), "Forest, (30,48) known first: it is the site");
        // adamantium wells never are: Forest's (21,48) and (38,48), and an adamantium slot at the pair's place
        int[] ad = {(1 << 12) | G.enc(loc(21, 48)), (1 << 12) | G.enc(loc(38, 48)), (1 << 12) | G.enc(loc(29, 48)), mn(8, 12)[0]};
        check(Mid.pick(ad, ad.length, forest, FLIP_X) == 0, "adamantium wells are never the site");
        // a hot or flagged slot (bits 14-15) is still read by type and location
        int[] hot = {mn(29, 48)[0] | (3 << 14), mn(8, 12)[0]};
        check(Mid.pick(hot, hot.length, forest, FLIP_X) == G.enc(loc(29, 48)), "slot bits 14-15 are ignored");
        // MassiveL before the diagonal probe finds (2,0): (18,14) is (7,5)'s nearest known mana well, so it is the site
        // until (2,0) is published (the next choice drops it)
        G.W = 40; G.H = 40;
        check(pick(mn(39, 0, 18, 14, 21, 25, 0, 39, 37, 39), hq(7, 5, 2, 37), ROT) == G.enc(loc(18, 14)),
            "MassiveL without (2,0): (18,14) until (2,0) is known");
        check(Mid.pick(new int[0], 0, forest, FLIP_X) == 0, "no well known: no site");

        // never an enemy home well (r2 C.MID_HOME_D2 of a candidate enemy HQ), though it passes the band while one of
        // our home wells is unknown: Maze's (22,31) is r2 45 from their (28,28) (p .60) and (3,46)'s nearest known mana
        // well until (10,39), (3,34) and (12,26) are; DefaultMap's (24,10) is r2 34 from their (27,5) (p .58) and
        // (25,18)'s nearest until (20,23) is
        G.W = 50; G.H = 50;
        MapLocation[] maze = hq(11, 2, 3, 46, 21, 21);
        int[] mazeEarly = mn(17, 9, 39, 10, 46, 15, 27, 18, 37, 23, 22, 31, 32, 40);
        check(Mid.inBand(101, 45), "Maze (22,31): r2 101 from (21,21), 45 from (28,28), is in the band");
        check(pick(mazeEarly, maze, ROT) == 0, "Maze without (10,39), (3,34), (12,26): no site (not their (22,31))");
        G.W = 32; G.H = 32;
        check(Mid.inBand(65, 34), "DefaultMap (24,10): r2 65 from (25,18), 34 from (27,5), is in the band");
        check(pick(mn(11, 8, 24, 10, 7, 21), hq(4, 26, 13, 23, 25, 18), ROT) == 0, "DefaultMap without (20,23): no site");

        // the free zone (Launcher.midHold): r2 C.MID_FREE_R2 = 8 of the site or of its twin; Forest's pair has 30 tiles
        G.W = 60; G.H = 60;
        MapLocation s = loc(29, 48), t = loc(30, 48);
        check(Mid.inFree(loc(31, 48), s, t) && Mid.inFree(loc(32, 48), s, t) && Mid.inFree(loc(31, 50), s, t),
            "the twin's collect tiles and ring are free");
        check(Mid.inFree(loc(27, 48), s, t) && Mid.inFree(loc(29, 50), s, t) && Mid.inFree(loc(31, 46), s, t),
            "the site's ring is free");
        check(!Mid.inFree(loc(26, 48), s, t) && !Mid.inFree(loc(33, 48), s, t) && !Mid.inFree(loc(29, 45), s, t)
            && !Mid.inFree(loc(30, 51), s, t), "r2 9 from both wells is a hold tile");
        check(Mid.inFree(loc(31, 48), s, null) && !Mid.inFree(loc(32, 48), s, null), "no twin known: the site alone");
        int nFree = 0, nHold = 0;
        for (int x = 20; x < 40; x++) for (int y = 40; y < 57; y++) {
            MapLocation l = loc(x, y);
            if (Mid.inFree(l, s, t)) nFree++;
            else if (l.distanceSquaredTo(s) <= 20) nHold++;
        }
        check(nFree == 30 && nHold == 39, "Forest: 30 free tiles, 39 hold tiles in the disc (" + nFree + ", " + nHold + ")");

        // Comms.SYM_ELIM: eliminations in bits 0-2, the site in bits 3-14
        int e = G.enc(new MapLocation(59, 59));
        check(e == 3836 && Comms.withSite(0, e) <= 0x7fff, "the largest enc fits bits 3-14");
        int v = Comms.withSite(5, G.enc(loc(29, 48)));
        check((v & 7) == 5 && Comms.siteOf(v) == G.enc(loc(29, 48)), "withSite keeps the eliminations");
        check(Comms.siteOf(Comms.withSym(v, 7)) == G.enc(loc(29, 48)) && (Comms.withSym(v, 6) & 7) == 6,
            "withSym keeps the site");
        check(Comms.siteOf(Comms.withSite(v, 0)) == 0 && (Comms.withSite(v, 0) & 7) == 5, "site 0 clears it");
        check(Comms.siteOf(3) == 0, "a c_well10-style slot (eliminations only) has no site");
        System.out.println("contested wells: " + checks + " cases ok");
    }

    /** The site on a map under its true symmetry and under all three candidates (the study: no change on these maps). */
    static void map(String name, int w, int h, int sym, MapLocation[] ours, int[] slots, MapLocation want) {
        G.W = w; G.H = h;
        int e = want == null ? 0 : G.enc(want);
        int got = Mid.pick(slots, slots.length, ours, sym);
        check(got == e, name + ": site " + G.dec(got) + ", want " + want);
        check(Mid.pick(slots, slots.length, ours, ALL) == e, name + " undecided: the same site");
    }

    static int pick(int[] slots, MapLocation[] ours, int cand) { return Mid.pick(slots, slots.length, ours, cand); }

    static MapLocation loc(int x, int y) { return new MapLocation(x, y); }

    static MapLocation[] hq(int... xy) {
        MapLocation[] o = new MapLocation[xy.length / 2];
        for (int i = 0; i < o.length; i++) o[i] = loc(xy[2 * i], xy[2 * i + 1]);
        return o;
    }

    /** Mana well slots (type 2) for the listed coordinates. */
    static int[] mn(int... xy) {
        int[] s = new int[xy.length / 2];
        for (int i = 0; i < s.length; i++) s[i] = (2 << 12) | G.enc(loc(xy[2 * i], xy[2 * i + 1]));
        return s;
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
