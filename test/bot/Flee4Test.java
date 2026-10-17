package c_flee4;

/** c_flee1 (carrier flight) pure helpers: the knobs, the flee-step score (River r157 of 8236 game 1, carrier 10390: c_gp1
 *  stepped to (33,22), r2 1 from the shooter), the fighter memory's slots and live list, Nav's stand-off ring, the
 *  ghost lookup, the move cost, the lightening rule and the far-alternative bar of the second-flight drop. Exits non-zero
 *  on a failure. */
public class Flee4Test {
    public static void main(String[] a) {
        // 1. knobs
        check(C.FLEE1, "arm on");
        check(C.HOT, "the drop rides on c_well6's hot-well checks (gather's hot(well) drop)");
        check(C.FLEE1_STAND >= C.THREAT_R2, "stand-off covers THREAT_R2");
        check(C.FLEE1_NEAR_R2 >= 78, "live list covers a stand-off ring two steps away: (6 + 2 sqrt 2)^2 = 77.9");
        check(C.FLEE1_N <= 8, "memory fits fleeMove's 8 threat points");
        check(8 * 4 < 64 && C.FLEE1_STAND + 1 < 128, "score fields cannot overflow into each other");
        check(C.FLEE1_MIN_LEFT < C.FLEE1_GUARD, "two-step guard above the scoring floor");
        check(C.FLEE1_NAV_GUARD < C.FLEE1_MIN_LEFT, "Nav filter guard below the flight's floor");
        check(C.FLEE1_MEM >= 3, "memory spans the 3 turns of 93% of the return hits");
        check(C.FLEE1_GUARD - C.FLEE1_MIN_LEFT >= 500, "a second-step square (at most about 500) ends above the floor");
        check(C.FLEE1_GHOST_LEFT > C.FLEE1_GUARD, "ghostFlee leaves more for the rest of a working turn than survive");

        // 2. River r157 (8236 g1, carrier 10390): carrier (31,24), threat (33,21), home (39,22)
        int[] tx = {33}, ty = {21};
        int sAway = Carrier.fleeScore(29, 26, tx, ty, 1, 39, 22);
        int sStay = Carrier.fleeScore(31, 24, tx, ty, 1, 39, 22);
        int sGp1 = Carrier.fleeScore(33, 22, tx, ty, 1, 39, 22);
        check(sAway > sStay, "River: (29,26) out of the ring beats staying at (31,24)");
        check(sStay > sGp1, "River: staying beats c_gp1's (33,22), r2 1 from the shooter");

        // 3. danger order: r2 10 (in reach) < 20 (THREAT_R2) < 32 (stand-off) < 40 (clear); the same home distance
        int[] t0x = {0}, t0y = {0};
        int s10 = Carrier.fleeScore(3, 1, t0x, t0y, 1, 4, 1);
        int s20 = Carrier.fleeScore(4, 2, t0x, t0y, 1, 5, 2);
        int s32 = Carrier.fleeScore(4, 4, t0x, t0y, 1, 5, 4);
        int s40 = Carrier.fleeScore(6, 2, t0x, t0y, 1, 7, 2);
        check(s10 < s20 && s20 < s32 && s32 < s40, "danger order r2 10 < 20 < 32 < 40: " + s10 + " " + s20 + " " + s32 + " " + s40);

        // 4. two fighters within r2 16 (nearer home) rank below one fighter within r2 16
        int[] t2x = {0, 4}, t2y = {0, 0};
        int sTwo = Carrier.fleeScore(2, 0, t2x, t2y, 2, 2, 0);      // r2 4 to both, on the home square
        int sOne = Carrier.fleeScore(-3, 0, t2x, t2y, 2, 2, 0);     // r2 9 and 49
        check(sTwo < sOne, "two fighters in reach rank below one, even nearer home");

        // 5. ties: equal danger, the larger least r2 wins though farther from home; clear squares: nearer home wins
        check(Carrier.fleeScore(3, 0, t0x, t0y, 1, 1, 0) > Carrier.fleeScore(2, 0, t0x, t0y, 1, 1, 0),
            "equal danger: r2 9 beats r2 4 though farther from home");
        check(Carrier.fleeScore(12, 0, t0x, t0y, 1, 20, 0) > Carrier.fleeScore(10, 0, t0x, t0y, 1, 20, 0),
            "clear squares: nearer home wins");
        check(Carrier.fleeScore(12, 0, t0x, t0y, 0, 20, 0) > Carrier.fleeScore(10, 0, t0x, t0y, 0, 20, 0),
            "no fighter: nearer home wins");

        // 6. slot
        int N = C.FLEE1_N;
        int[] gx = new int[N], gy = new int[N], gr = new int[N];
        gx[2] = 10; gy[2] = 10; gr[2] = 5;
        check(Carrier.slot(gx, gy, gr, 11, 10, 6) == 2, "a fighter that moved 1 tile reuses its slot");
        check(Carrier.slot(gx, gy, gr, 12, 10, 6) == 2, "r2 4 still merges");
        check(Carrier.slot(gx, gy, gr, 13, 10, 6) != 2, "r2 9 does not merge");
        gr[2] = 6;   // written this round
        int k2 = Carrier.slot(gx, gy, gr, 11, 10, 6);
        check(k2 >= 0 && k2 != 2, "two fighters within r2 4 in the same round take two slots: " + k2);
        int[] fx = new int[N], fy = new int[N], fr = new int[N];
        for (int j = 0; j < N; j++) { fx[j] = 10 * j; fy[j] = 40; fr[j] = 7 + j; }
        fr[3] = 0;   // an empty slot among live ones
        check(Carrier.slot(fx, fy, fr, 0, 0, 20) == 3, "an empty slot is used before the oldest live one");
        fr[3] = 9;   // full: the oldest is slot 0 (round 7)
        check(Carrier.slot(fx, fy, fr, 0, 0, 20) == 0, "a full memory replaces the oldest");
        for (int j = 0; j < N; j++) fr[j] = 20;
        check(Carrier.slot(fx, fy, fr, 0, 0, 20) == -1, "every slot written this round: -1");
        int[] ex = new int[N], ey = new int[N], er = new int[N];
        ex[0] = 1; ey[0] = 1; er[0] = 5;   // the fighter stored in slot 0; slot 1.. empty at (0,0)
        check(Carrier.slot(ex, ey, er, 1, 1, 6) == 0, "an empty slot at (0,0) does not take the stored fighter at (1,1)");
        int[] zx = new int[N], zy = new int[N], zr = new int[N];
        int kz = Carrier.slot(zx, zy, zr, 1, 1, 6);
        check(kz >= 0 && zr[kz] == 0, "all empty: an empty slot");

        // 7. liveNear
        int[] lx = new int[N], ly = new int[N];
        int[] hx = new int[N], hy = new int[N], hr = new int[N];
        int R = 100;
        hx[0] = 10; hy[0] = 10; hr[0] = R - C.FLEE1_MEM;        // age FLEE1_MEM: live
        hx[1] = 11; hy[1] = 10; hr[1] = R - C.FLEE1_MEM - 1;    // one round older: not live
        hx[2] = 10; hy[2] = 19; hr[2] = R;                      // r2 81 from (10,10): beyond FLEE1_NEAR_R2
        hx[3] = 12; hy[3] = 12; hr[3] = R - 1;                  // live
        int nl = Carrier.liveNear(hx, hy, hr, R - C.FLEE1_MEM, 10, 10, C.FLEE1_NEAR_R2, lx, ly);
        check(nl == 2, "two live points near: " + nl);
        boolean got0 = false, got3 = false;
        for (int j = 0; j < nl; j++) { if (lx[j] == 10 && ly[j] == 10) got0 = true; if (lx[j] == 12 && ly[j] == 12) got3 = true; }
        check(got0 && got3, "the live points are the age-FLEE1_MEM and the fresh one");
        hy[2] = 18;   // r2 64: inside
        check(Carrier.liveNear(hx, hy, hr, R - C.FLEE1_MEM, 10, 10, C.FLEE1_NEAR_R2, lx, ly) == 3, "r2 64 is near");
        int[] qx = new int[N], qy = new int[N], qr = new int[N];
        check(Carrier.liveNear(qx, qy, qr, 3 - C.FLEE1_MEM, 0, 0, C.FLEE1_NEAR_R2, lx, ly) == 0, "gr 0 never live at round 3");

        // 8. Nav.ringBlocks, the point at (10,10)
        int[] px = {10}, py = {10};
        check(Nav.ringBlocks(13, 10, 12, 10, px, py, 1), "inward step blocked");
        check(!Nav.ringBlocks(12, 10, 13, 10, px, py, 1), "outward step allowed");
        check(Nav.ringBlocks(12, 11, 11, 12, px, py, 1), "sideways step at equal r2 inside blocked");
        check(!Nav.ringBlocks(17, 11, 16, 11, px, py, 1), "a step ending at r2 37 allowed, even inward");
        check(!Nav.ringBlocks(13, 10, 12, 10, px, py, 0), "n = 0 never blocks");
        int[] p2x = {10, 20}, p2y = {10, 10};
        check(Nav.ringBlocks(14, 10, 15, 10, p2x, p2y, 2), "outward from one point, inward to the other: blocked");

        // 9. ghostAt
        int[] gax = {0, 3}, gay = {0, 0};
        check(Carrier.ghostAt(5, 0, gax, gay, 2) == 1, "nearest point within r2 36");
        check(Carrier.ghostAt(-6, 0, gax, gay, 2) == 0, "r2 36 counts");
        check(Carrier.ghostAt(-6, 1, gax, gay, 2) == -1, "r2 37: none");
        check(Carrier.ghostAt(0, 0, gax, gay, 0) == -1, "no point: none");

        // 10. moveCost
        check(Carrier.moveCost(0, false) == 5, "0 kg: 5");
        check(Carrier.moveCost(13, false) == 9, "13 kg: 9");
        check(Carrier.moveCost(14, false) == 10, "14 kg: 10");
        check(Carrier.moveCost(30, false) == 16, "30 kg: 16");
        check(Carrier.moveCost(40, false) == 20, "40 kg: 20");
        check(Carrier.moveCost(0, true) == 6, "0 kg cloud: 6");
        check(Carrier.moveCost(30, true) == 19, "30 kg cloud: 19");
        check(Carrier.moveCost(C.FLEE1_LIGHT_W - 1, false) < 10 && Carrier.moveCost(C.FLEE1_LIGHT_W, false) >= 10,
            "FLEE1_LIGHT_W is the first weight with one move a turn or fewer");

        // 11. shouldLighten
        check(!Carrier.shouldLighten(13, 0, 26, 100, 90), "13 kg: no");
        check(!Carrier.shouldLighten(14, 1, 26, 100, 90), "with an anchor: no");
        check(!Carrier.shouldLighten(14, 0, 27, 100, 90), "bd 27: no");
        check(!Carrier.shouldLighten(14, 0, 26, 100, 89), "11 rounds after a hit: no");
        check(Carrier.shouldLighten(14, 0, 26, 100, 90), "14 kg, bd 26, hit 10 rounds earlier: yes");
        check(!Carrier.shouldLighten(30, 0, 9, 100, -100), "never hit: no");

        // 12. farAlt
        check(!Carrier.farAlt(90, 25), "raided at r2 25: an alternative at 90 is near");
        check(Carrier.farAlt(120, 25), "raided at r2 25: 120 is far (bar 100)");
        check(!Carrier.farAlt(1600, 400) && Carrier.farAlt(1601, 400), "raided at r2 400: bar 1,600");
        check(!Carrier.farAlt(40000, Integer.MAX_VALUE) && Carrier.farAlt(40001, Integer.MAX_VALUE),
            "no HQ (Integer.MAX_VALUE): bar 40,000, no overflow");
        check(Carrier.farAlt(Integer.MAX_VALUE, 25), "no alternative distance: far");

        // 13. backToRaided: no alternative of the role (none, or the any-type fallback's) brings the raided well back
        check(Carrier.backToRaided(true, 0, 25), "no well: back to the raided one");
        check(Carrier.backToRaided(true, 40, 25), "a near any-type well (home Ad for a mana carrier): back to the raided one");
        check(!Carrier.backToRaided(false, 90, 25), "a near alternative of the role: kept");
        check(Carrier.backToRaided(false, 120, 25), "a far alternative of the role: back to the raided one");

        // 14. takeBest: fleeMove's second-step order (best single step first; unmovable and expanded entries skipped)
        int M = Integer.MIN_VALUE;
        int[] sb = {5, M, 9, 9, 1, M, 7, M};
        check(Carrier.takeBest(sb) == 3 && sb[3] == M, "the largest first, the highest index on a tie");
        check(Carrier.takeBest(sb) == 2, "then the tied one");
        check(Carrier.takeBest(sb) == 6 && Carrier.takeBest(sb) == 0 && Carrier.takeBest(sb) == 4, "then descending");
        check(Carrier.takeBest(sb) == -1, "none left: -1");
        int[] sm = {M, M, M, M, M, M, M, M};
        check(Carrier.takeBest(sm) == -1, "no movable step: -1");

        System.out.println("flee4 score + memory + ring + lighten + drop: " + checks + " cases ok");
    }

    static int checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
