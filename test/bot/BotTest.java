package bot;

import battlecode.common.*;
import java.util.Random;

/**
 * Pure-logic tests for the bot (no engine): encodings, the comms layout, symmetry images and the inference.
 * Plain main with an exit code (the engine jar has no JUnit). Run by tools/unit-tests.sh.
 */
public class BotTest {
    static int fails, checks;

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) { fails++; System.out.println("FAIL: " + what); }
    }

    public static void main(String[] a) {
        encodings();
        commsLayout();
        symmetryImages();
        symmetryInference();
        threatRadius();
        teleCodeTables();
        teleGoldenVectors();
        teleSaturation();
        teleIndicatorString();
        teleHqReason();
        teleEmitters();
        System.out.println("BotTest: " + checks + " checks, " + fails + " failures");
        if (fails > 0) System.exit(1);
    }

    static void encodings() {
        for (int x = 0; x < 60; x++) for (int y = 0; y < 60; y++) {
            MapLocation l = new MapLocation(x, y);
            int e = G.enc(l);
            check(e > 0 && e < 4096, "enc fits 12 bits " + l);
            check(G.dec(e).equals(l), "dec(enc) " + l);
        }
        check(G.dec(0) == null, "dec(0) is none");
    }

    static void commsLayout() {
        // regions must not overlap and must fit in 64 slots
        int[][] regions = {{Comms.HQ_LOC, 4}, {Comms.SYM_ELIM, 1}, {Comms.WELLS, Comms.NWELLS}, {Comms.ISLANDS + 1, 36},
            {Comms.ENEMY, Comms.NENEMY}};
        boolean[] used = new boolean[64];
        for (int[] r : regions) for (int i = r[0]; i < r[0] + r[1]; i++) {
            check(i >= 0 && i < 64, "slot in range " + i);
            if (i >= 0 && i < 64) { check(!used[i], "slot used once " + i); used[i] = true; }
        }
        // a well entry: type in bits 12-13, location in 12 bits
        int v = (2 << 12) | G.enc(new MapLocation(59, 59));
        check((v >>> 12) == 2 && (v & 0xfff) == G.enc(new MapLocation(59, 59)) && v < 65536, "well entry packing");
        int iv = (2 << 12) | G.enc(new MapLocation(59, 59));
        check(iv < 65536, "island entry fits 16 bits");
    }

    static void symmetryImages() {
        G.W = 30; G.H = 20;
        for (int s = 1; s <= 4; s <<= 1) {
            for (int x = 0; x < G.W; x++) for (int y = 0; y < G.H; y++) {
                int ix = MapMem.imgX(s, x), iy = MapMem.imgY(s, y);
                check(ix >= 0 && ix < G.W && iy >= 0 && iy < G.H, "image on map");
                check(MapMem.imgX(s, ix) == x && MapMem.imgY(s, iy) == y, "image is an involution");
            }
            for (Direction d : G.DIRS) check(MapMem.imgDir(s, MapMem.imgDir(s, d)) == d, "dir image involution " + s + d);
        }
        check(MapMem.imgDir(MapMem.ROT, Direction.NORTH) == Direction.SOUTH, "ROT N->S");
        check(MapMem.imgDir(MapMem.ROT, Direction.NORTHEAST) == Direction.SOUTHWEST, "ROT NE->SW");
        check(MapMem.imgDir(MapMem.FLIP_X, Direction.NORTHEAST) == Direction.NORTHWEST, "FLIP_X NE->NW");
        check(MapMem.imgDir(MapMem.FLIP_X, Direction.NORTH) == Direction.NORTH, "FLIP_X N->N");
        check(MapMem.imgDir(MapMem.FLIP_Y, Direction.NORTHEAST) == Direction.SOUTHEAST, "FLIP_Y NE->SE");
        check(MapMem.imgDir(MapMem.FLIP_Y, Direction.EAST) == Direction.EAST, "FLIP_Y E->E");
    }

    /** C.THREAT_R2 covers every offset from which an enemy launcher can step once and attack (r2 16). */
    static void threatRadius() {
        int worst = 0;
        for (int dx = -7; dx <= 7; dx++) for (int dy = -7; dy <= 7; dy++) {
            boolean reach = dx * dx + dy * dy <= 16;
            for (Direction d : G.DIRS) { int ex = dx - d.dx, ey = dy - d.dy; if (ex * ex + ey * ey <= 16) reach = true; }
            if (reach) worst = Math.max(worst, dx * dx + dy * dy);
        }
        check(worst == 26, "one-step attack reach is r2 26, got " + worst);
        check(C.THREAT_R2 >= worst, "THREAT_R2 covers the one-step reach");
    }

    /**
     * 300 random maps, each symmetric under one candidate (walls, clouds, currents transformed); tiles are revealed in
     * random order through MapMem.checkTile. The true symmetry must never be eliminated, and most maps must be decided.
     */
    static void symmetryInference() {
        Random rnd = new Random(2023);
        int decided = 0, total = 300;
        for (int m = 0; m < total; m++) {
            G.W = 20 + rnd.nextInt(41); G.H = 20 + rnd.nextInt(41);
            int truth = 1 << rnd.nextInt(3);
            char[] full = new char[G.W * G.H];
            for (int x = 0; x < G.W; x++) for (int y = 0; y < G.H; y++) {
                int ix = MapMem.imgX(truth, x), iy = MapMem.imgY(truth, y);
                int idx = x + y * G.W, iidx = ix + iy * G.W;
                if (iidx < idx) continue;        // fill one of each symmetric pair, then mirror it
                int c = 1;
                int r = rnd.nextInt(100);
                if (r < 15) c |= 2; else if (r < 25) c |= 4;
                Direction cur = Direction.CENTER;
                if ((c & 2) == 0 && rnd.nextInt(100) < 8) cur = G.DIRS[rnd.nextInt(8)];
                if (iidx == idx) cur = Direction.CENTER;   // a self-symmetric tile cannot hold a consistent current
                int cc = c, ic = c;
                if (cur != Direction.CENTER) {
                    cc |= (cur.ordinal() + 1) << 3;
                    ic |= (MapMem.imgDir(truth, cur).ordinal() + 1) << 3;
                }
                full[idx] = (char) cc;
                full[iidx] = (char) ic;
            }
            MapMem.tile = new char[G.W * G.H];
            MapMem.cand = 7;
            MapMem.symConflicts = 0;
            int n = G.W * G.H;
            int[] order = new int[n];
            for (int i = 0; i < n; i++) order[i] = i;
            for (int i = n - 1; i > 0; i--) { int j = rnd.nextInt(i + 1); int t = order[i]; order[i] = order[j]; order[j] = t; }
            for (int k = 0; k < n; k++) {
                int idx = order[k];
                MapMem.tile[idx] = full[idx];
                MapMem.checkTile(idx % G.W, idx / G.W);
            }
            check((MapMem.cand & truth) != 0, "true symmetry survives (map " + m + ")");
            check(MapMem.symConflicts == 0, "no conflicts on a consistent map (map " + m + ")");
            if (MapMem.cand == truth) decided++;
        }
        check(decided >= total * 9 / 10, "most random maps decided with full information: " + decided + "/" + total);
    }

    // ---------------------------------------------------------------- telemetry (docs/TELEMETRY.md A.10)

    /** The letter of a code by the tables of TELEMETRY.md 1.1, written independently of Telemetry ('?' = invalid). */
    static char specLetter(int type, int code) {
        switch (type) {
            case 0: { int r = code & 15; return r <= 9 ? ".bgpwcastx".charAt(r) : r == 15 ? '!' : '?'; }
            case 1: return code < 32 ? "!GCWSXRDFVTKQEYP".charAt(code >> 1) : '?';
            case 2: return "NFHMSGW!".charAt(code & 7);
            case 3: return code == 63 ? '!' : (code >> 2) <= 14 ? "FCSH".charAt(code & 3) : '?';
            default: return code == 0 ? 'O' : code == 1 ? '!' : '?';
        }
    }

    static char teleLetter(int type, int code) { return Telemetry.letters(type).charAt(code & 63); }

    static void teleCodeTables() {
        String A = Telemetry.ALPHA;
        check(A.length() == 64, "ALPHA has 64 characters");
        for (int c = 0; c < 64; c++) {
            char ch = A.charAt(c);
            check(A.indexOf(ch) == c && (Character.isLetterOrDigit(ch) || ch == '-' || ch == '_') && ch < 128, "ALPHA[" + c + "] unique ASCII");
        }
        check(A.charAt(Telemetry.SYNC_CODE) == 'g' && A.charAt(5) == '5' && A.charAt(33) == 'X' && A.charAt(36) == 'a', "ALPHA spot values");
        RobotType[] rt = {RobotType.HEADQUARTERS, RobotType.CARRIER, RobotType.LAUNCHER, RobotType.AMPLIFIER, RobotType.DESTABILIZER, RobotType.BOOSTER};
        for (int t = 0; t < 6; t++) check(Telemetry.typeNum(rt[t]) == t, "type number (schema order) of " + rt[t]);
        int[] excCodes = {15, 0, 7, 63, 1, 1};
        for (int t = 0; t < 6; t++) {
            check(Telemetry.letters(t).length() == 64, "letter table length, type " + t);
            check(Telemetry.excCode(t) == excCodes[t] && teleLetter(t, Telemetry.excCode(t)) == '!', "'!' code of type " + t);
            for (int c = 0; c < 64; c++) {
                char want = specLetter(t, c), got = teleLetter(t, c);
                check(got == want, "letter type " + t + " code " + c + ": " + got + " want " + want);
                check(want > 32 && want < 127 && "|,=<>&".indexOf(want) < 0, "letter printable, type " + t + " code " + c);
            }
        }
        int nValid = 0;
        for (int c = 0; c < 64; c++) if (teleLetter(1, c) != '?') nValid++;
        check(nValid == 32, "carrier: 32 valid codes");
        for (int c = 0; c < 64; c++) check(teleLetter(2, c) != '?', "launcher: every code valid " + c);
        for (int c = 10; c <= 14; c++) check(teleLetter(0, c) == '?' && teleLetter(0, c + 16) == '?', "HQ reasons 10-14 invalid");
        // round trips
        for (int st = 0; st < 16; st++) for (int role = 1; role <= 2; role++) {
            int c = Telemetry.carrierCode(st, role);
            check(c >= 0 && c < 32 && c >> 1 == st && (c & 1) == (role == 2 ? 1 : 0), "carrierCode round trip " + st + "/" + role);
            check(teleLetter(1, c) == "!GCWSXRDFVTKQEYP".charAt(st), "carrier letter of state " + st);
        }
        for (int m = 0; m < 8; m++) for (int o = 0; o < 4; o++) for (int out = 0; out < 2; out++) {
            int c = Telemetry.launcherCode(m, o, out == 1);
            check(c >= 0 && c < 64 && (c & 7) == m && (c >> 3 & 3) == o && (c >> 5) == out, "launcherCode round trip " + m + o + out);
        }
        for (int r = 0; r < 16; r++) for (int th = 0; th < 2; th++) for (int w = 0; w < 2; w++) {
            int c = Telemetry.hqCode(r, th == 1, w == 1);
            check(c >= 0 && c < 64 && (c & 15) == r && (c >> 4 & 1) == th && (c >> 5) == w, "hqCode round trip " + r + th + w);
        }
        for (int m = 0; m < 4; m++) for (int n = 0; n <= 20; n++) {
            int c = Telemetry.ampCode(m, n);
            check(c >= 0 && c < 60 && (c & 3) == m && (c >> 2) == Math.min(n, 14) && teleLetter(3, c) == "FCSH".charAt(m), "ampCode round trip " + m + "/" + n);
        }
        check(Telemetry.ampCode(0, -3) == 0, "ampCode clamps a negative count");
        // every state character the carrier assigns has a state number
        for (char ch : "GCWSXRDFVTKQEYP".toCharArray()) check(Telemetry.CARRIER_STATES.indexOf(ch) > 0, "carrier state " + ch);
        // A.9 code examples and the BCC example
        check(Telemetry.carrierCode(2, 2) == 5, "carrier C Mn = code 5");
        check(Telemetry.launcherCode(1, 0, true) == 33, "launcher F sighting outnumbered = code 33");
        check(Telemetry.hqCode(4, false, true) == 36, "HQ w wantAnchor = code 36");
        check(((7173 - 0) & 63) == 5 && teleLetter(1, 5) == 'C', "BCC example: used 7173 decodes as carrier code 5 (C)");
    }

    /** Index of the newest TEST_SINK record. */
    static int[] lastRecord() {
        int i = ((Telemetry.sinkN - 1) % 1024) * 5;
        int[] s = Telemetry.TEST_SINK;
        return new int[]{s[i], s[i + 1], s[i + 2], s[i + 3], s[i + 4]};
    }

    static void checkRecord(int kind, int a, int b, int c, int d, String what) {
        int[] r = lastRecord();
        boolean ok = r[0] == -2 - kind && r[1] == a && r[2] == b && r[3] == c && r[4] == d;
        check(ok, what + ": got x=" + r[0] + " " + r[1] + " " + r[2] + " " + r[3] + " " + r[4]);
    }

    static int loc(int x, int y) { return Telemetry.loc12(new MapLocation(x, y)); }

    /** TELEMETRY.md A.9: the packers and B's --decode-record must agree exactly. */
    static void teleGoldenVectors() {
        G.rc = null;
        check(loc(12, 7) == 776 && loc(20, 33) == 1314 && loc(5, 5) == 326 && Telemetry.loc12(null) == 0, "loc12 values");
        Telemetry.emitHdr(1, 37, loc(12, 7), 2, 0, 0, 1, 3, 16, 42, 0);
        checkRecord(Telemetry.HDR, 2115895297, 9473, 467720, 10768, "golden HDR");
        check(Telemetry.MAGIC == 2115895297, "MAGIC");
        Telemetry.emitRole(2, 1, 1, 30, 420, loc(5, 5), 4);
        checkRecord(Telemetry.ROLE, 274, 30, 420, 16710, "golden ROLE");
        Telemetry.emitWell(loc(20, 33), 2, 2, 2, 45, 5, 7, 0, 0, 0);
        checkRecord(Telemetry.WELL, 304418, 45, 1797, 0, "golden WELL");
        Telemetry.emitTrip(loc(20, 33), 2, 2, 40, 1, 180, 195, 215, 231, 3, 0, 1, 20);
        checkRecord(Telemetry.TRIP, 19440930, 12779700, 15139031, 335609859, "golden TRIP");
        check(G.DIRS9[3] == Direction.EAST, "FIGHT dir 3 is EAST");
        int fa = Telemetry.fightA(true, false, true, true, true, 3, false, false, 0, 1, 3, 1);
        int fb = Telemetry.fightTile(1, true, 13, 0), fc = Telemetry.fightTile(2, true, 9, 9), fd = Telemetry.fightD(140, 4, 10234);
        check(fa == 16990333 && fb == 852225 && fc == 151585026 && fd == 670696588, "golden FIGHT: " + fa + " " + fb + " " + fc + " " + fd);
        // shots_after OR-ed in later (as Launcher.run does) gives the same word
        check((Telemetry.fightA(true, false, true, true, true, 3, false, false, 0, 0, 3, 1) | 1 << 14) == fa, "FIGHT shots_after OR-ed later");
        Telemetry.emitRole(0, 2, 0, -1, -1, 0, 0);
        check(lastRecord()[2] == -1 && lastRecord()[3] == -1, "ROLE hq_ad and hq_mn are signed (-1 = not read)");
    }

    static void teleSaturation() {
        G.rc = null;
        check(Telemetry.sat(300, 8) == 255 && Telemetry.sat(-1, 8) == 0 && Telemetry.sat(17, 8) == 17 && Telemetry.sat(5000, 12) == 4095, "sat");
        check(Telemetry.s8(300) == 255 && Telemetry.s8(-7) == 0 && Telemetry.s16(70000) == 65535 && Telemetry.s16(-1) == 0 && Telemetry.s16(65535) == 65535, "s8/s16");
        Telemetry.emitTrip(loc(20, 33), 2, 2, 300, 1, 180, 195, 215, 231, 3, 0, 1, 20);
        check((lastRecord()[1] >>> 16 & 255) == 255, "TRIP load 300 packs as 255");
        Telemetry.emitTrip(loc(20, 33), 2, 2, -5, 1, -1, 195, 215, 231, -3, 0, 1, 20);
        int[] r = lastRecord();
        check((r[1] >>> 16 & 255) == 0 && (r[2] & 0xffff) == 0 && (r[4] & 255) == 0 && (r[1] & 4095) == 1314, "TRIP negatives pack as 0 and do not spill");
        Telemetry.emitTrip(loc(20, 33), 2, 2, 40, 1, 180, 70000, 215, 231, 999, 0, 1, 20);
        r = lastRecord();
        check((r[2] >>> 16) == 65535 && (r[4] & 255) == 255 && (r[4] >>> 8 & 255) == 0, "TRIP saturation does not spill into the next field");
        check(Telemetry.fightTile(0, false, Integer.MAX_VALUE, 0) >>> 16 == 255, "FIGHT min_d2 with no fighter is 255");
        check(Telemetry.fightD(200, 3, 70000) >>> 16 == 65535, "FIGHT target saturates at 65535");
        Telemetry.emitCnt(70000, 1, 2, 3, 4, 5, 6, 7);
        r = lastRecord();
        check((r[1] & 0xffff) == 65535 && (r[1] >>> 16) == 1, "CNT counter saturates without spilling");
        Telemetry.emitCntm(5, -1, 0, 0, 0, 0, 300, 0, 0, 0, 0);
        r = lastRecord();
        check((r[1] & 7) == 5 && (r[1] >>> 4 & 4095) == 0 && (r[3] >>> 16 & 255) == 255, "CNTM: undecided packs as 0, seen_wells saturates");
        Telemetry.emitCntm(5, 1999, 0, 0, 0, 0, 3, 0, 0, 0, 0);
        check((lastRecord()[1] >>> 4 & 4095) == 2000, "CNTM decided_round + 1");
        Telemetry.emitAnch(2, -1, 3, true, loc(4, 4), 5000, 80000, 77);
        r = lastRecord();
        check((r[1] >>> 4 & 255) == 255 && (r[1] >>> 12 & 3) == 3 && (r[1] >>> 14 & 1) == 1 && (r[2] >>> 12) == 4095 && r[3] == 65535 && r[4] == 77,
            "ANCH: predicted island 255, anchor_turns and d2 saturate");
    }

    static String full(char letter, int code, String rest, int ov, int ex, int nm, int sm, int sd, int wh, int bf, String extra) {
        return "" + letter + Telemetry.ALPHA.charAt(code) + rest + "|ov=" + ov + ",ex=" + ex + ",nm=" + nm + ",sm=" + sm + ",sd=" + sd
            + ",wh=" + wh + ",bf=" + bf + extra;
    }

    static void teleIndicatorString() {
        check(Telemetry.indicatorString('C', 5, "2", 0, 0, 0, 1, 88, 3, 0, "").equals("C52|ov=0,ex=0,nm=0,sm=1,sd=88,wh=3,bf=0"),
            "A.9 carrier string");
        check(Telemetry.indicatorString('F', 33, "0", 0, 0, 0, 7, -1, 0, 0, ",pn=0,ua=0").startsWith("FX0|ov="), "A.9 launcher string");
        check(Telemetry.indicatorString('w', 36, "C3L5A0K0", 0, 0, 0, 1, 40, 0, 0, "").startsWith("waC3L5A0K0|ov="), "A.9 HQ string");
        String[][] cases = {   // type, letter, code, rest, extra
            {"1", "C", "5", "2k-1", ""}, {"1", "K", "23", "1k35", ""}, {"1", "!", "0", "", ""},
            {"2", "F", "33", "0", ",pn=99999,ua=99999"}, {"2", "N", "24", "3", ",pn=99999,ua=99999,rg=99999,fo=99999"},
            {"2", "!", "7", "3", ",pn=1,ua=2,rg=3,fo=4"},
            {"0", "w", "36", "C999L999A99K99", ""}, {"0", "!", "15", "C3L5A0K0", ""},
            {"3", "C", "9", "14", ""}, {"3", "!", "63", "2", ""}, {"4", "O", "0", "", ""}, {"5", "!", "1", "", ""}};
        int[] vals = {0, 7, 99, 12345, 99999};
        for (String[] c : cases) for (int v : vals) for (int sd : new int[]{-1, 1999}) {
            char letter = c[1].charAt(0);
            int code = Integer.parseInt(c[2]);
            check(teleLetter(Integer.parseInt(c[0]), code) == letter, "case letter " + letter + code);
            String f = full(letter, code, c[3], v, v, v, 7, sd, v, v, c[4]);
            String s = Telemetry.indicatorString(letter, code, c[3], v, v, v, 7, sd, v, v, c[4]);
            boolean ascii = true;
            for (int i = 0; i < s.length(); i++) { char ch = s.charAt(i); if (ch < 0x20 || ch > 0x7e || ch == '<' || ch == '>' || ch == '&') ascii = false; }
            check(s.length() <= 64, "string at most 64: " + s);
            check(ascii, "string ASCII without < > &: " + s);
            check(s.charAt(0) == letter && s.charAt(1) == Telemetry.ALPHA.charAt(code), "string starts with letter and code char: " + s);
            check(f.startsWith(s) && (s.length() == f.length() || f.charAt(s.length()) == ','), "only whole trailing fields dropped: " + s);
            check(s.contains("|ov=") && s.indexOf('|') == s.lastIndexOf('|'), "string has one |ov=: " + s);
            check(f.length() <= 64 ? s.equals(f) : s.length() == f.lastIndexOf(',', 64), "cut at the last comma within 64: " + s);
        }
    }

    static void teleHqReason() {
        // args: tileFail, wantAnchor, batchOK, threatened, room, ad, mn, resAd, resMn
        check(Telemetry.hqReason(true, false, true, false, true, 500, 500, 0, 0) == 7, "s: a tryBuild found no tile");
        check(Telemetry.hqReason(true, true, true, false, true, 100, 100, 80, 80) == 7, "s before a (tile fail beats the reserve)");
        check(Telemetry.hqReason(false, true, true, false, false, 0, 100, 80, 80) == 6, "a: reserve blocks a launcher");
        check(Telemetry.hqReason(false, true, false, false, true, 100, 0, 80, 80) == 6, "a: reserve blocks a carrier");
        check(Telemetry.hqReason(false, true, true, true, true, 100, 0, 80, 80) == 3, "not a when threatened and no launcher money: p");
        check(Telemetry.hqReason(false, false, false, false, true, 0, 100, 0, 0) == 4, "w: launcher affordable, batch not OK");
        check(Telemetry.hqReason(false, false, false, false, false, 60, 100, 0, 0) == 4, "w before c");
        check(Telemetry.hqReason(false, false, true, false, false, 60, 0, 0, 0) == 5, "c: carrier affordable, no room");
        check(Telemetry.hqReason(false, false, true, true, false, 60, 0, 0, 0) == 8, "t: carrier affordable but threatened");
        check(Telemetry.hqReason(false, false, true, true, true, 30, 15, 0, 0) == 8, "t: amplifier affordable but threatened");
        check(Telemetry.hqReason(false, false, false, true, false, 60, 100, 0, 0) == 4, "w before t");
        check(Telemetry.hqReason(false, false, true, false, true, 10, 10, 0, 0) == 3, "p: poor");
        check(Telemetry.hqReason(false, false, true, false, true, 49, 44, 0, 0) == 3, "p at the edge");
        check(Telemetry.hqReason(false, false, true, false, true, 60, 0, 0, 0) == 9, "x: carrier affordable with room, not built");
        check(Telemetry.hqReason(false, true, true, false, true, 0, 200, 80, 80) == 9, "x: launcher affordable over the reserve, not built");
        for (int r = 0; r < 16; r++) check(r < 10 || r == 15 ? teleLetter(0, r) != '?' : teleLetter(0, r) == '?', "HQ reason letter " + r);
    }

    static void teleEmitters() {
        G.rc = null;
        int n0 = Telemetry.sinkN;
        Telemetry.emitExc(2, 0, 2, 33, 100, 101, 1);   checkRecord(Telemetry.EXC, 2 | 2 << 12 | 33 << 16, 100, 101, 1, "EXC");
        Telemetry.emitNm(9500, 600, 5, 3, 2, 12, 40, 4, 77);
        checkRecord(Telemetry.NM, 9500 | 600 << 16, 5 | 3 << 8 | 2 << 16 | 12 << 24, 40 | 4 << 16, 77, "NM");
        Telemetry.emitOvr(77, 78, 5, 4, 12000);        checkRecord(Telemetry.OVR, 77, 78, 5 | 4 << 8, 12000, "OVR");
        Telemetry.emitCnt(1, 2, 3, 4, 5, 6, 7, 8);
        checkRecord(Telemetry.CNT, 1 | 2 << 16, 3 | 4 << 16, 5 | 6 << 16, 7 | 8 << 16, "CNT");
        Telemetry.emitCntt(1, 2, 3, 4, 5, 6, 7, 8);
        checkRecord(Telemetry.CNTT, 1 | 2 << 16, 3 | 4 << 16, 5 | 6 << 16, 7 | 8 << 16, "CNTT");
        Telemetry.emitCntm(1, 120, 2, 30, 4, 50, 6, 7, 300, 1, 2);
        checkRecord(Telemetry.CNTM, 1 | 121 << 4 | 2 << 16, 30 | 4 << 16, 50 | 6 << 16 | 7 << 24, 300 | 1 << 16 | 2 << 24, "CNTM");
        Telemetry.emitSym(2, 4, 5, 0, loc(3, 4), 12, 0);  checkRecord(Telemetry.SYM, 2 | 4 << 4 | 5 << 8, loc(3, 4), 12, 0, "SYM");
        Telemetry.emitSym(1, 5, 1, 1, 0, 30, 2);        checkRecord(Telemetry.SYM, 1 | 5 << 4 | 1 << 8 | 1 << 12, 0, 30, 2, "SYM comms conflict");
        Telemetry.emitRole(0, 2, 0, -1, -1, 0, 0);       checkRecord(Telemetry.ROLE, 2 << 4, -1, -1, 0, "ROLE at spawn (hq not read)");
        Telemetry.emitFlee(9, 2, 50, true, false, loc(1, 2), 40, loc(3, 3), 90);
        checkRecord(Telemetry.FLEE, 9 | 2 << 8 | 50 << 16 | 1 << 24, loc(1, 2) | 40 << 12, loc(3, 3), 90, "FLEE");
        Telemetry.emitAnch(6, 12, 0, false, loc(7, 8), 33, 0, 400);
        checkRecord(Telemetry.ANCH, 6 | 12 << 4, loc(7, 8) | 33 << 12, 0, 400, "ANCH placed");
        Telemetry.emitObj(0, 1, 3, 2, 0, loc(9, 9), loc(1, 1), 55);
        checkRecord(Telemetry.OBJ, 0 | 1 << 4 | 3 << 8 | 2 << 16, loc(9, 9), loc(1, 1), 55, "OBJ");
        Telemetry.emitHqs(100, 200, 0, 31, 9, 8, 1, 2, 4, 90, 17);
        checkRecord(Telemetry.HQS, 100 | 200 << 16, 31 << 16, 9 | 8 << 8 | 1 << 16 | 2 << 24, 4 | 90 << 8 | 17 << 16, "HQS");
        Telemetry.emitBug(40, 1, 3, loc(10, 10), loc(2, 2), 100, 140, 300, 20);
        checkRecord(Telemetry.BUG, 40 | 1 << 16 | 3 << 24, loc(10, 10) | loc(2, 2) << 12, 100 | 140 << 16, 300 | 20 << 16, "BUG");
        Telemetry.dot(Telemetry.COMMS + 7, 1 | 2 << 16, 3, 4, 5);
        check(lastRecord()[0] == -2 - 31, "COMMS chunk 7 is kind 31");
        check(Telemetry.sinkN - n0 == 15, "every emitter wrote one record");
        // hooks must not throw on null or empty inputs
        boolean threw = false;
        try {
            MapLocation[] saved = HQState.ourHQs;
            HQState.ourHQs = null;
            Telemetry.trip(null, 0, 1, null, 0);
            HQState.ourHQs = new MapLocation[0];
            Telemetry.trip(new MapLocation(1, 1), 40, 2, null, 0);
            HQState.ourHQs = saved;
            Telemetry.emitWell(Telemetry.loc12(null), 0, 1, 1, 0, 0, 0, 0, 0, Telemetry.loc12(null));
            Telemetry.emitAnch(1, 0, 0, false, Telemetry.loc12(null), 0, 0, 0);
            int ttype = Telemetry.ttype, exc = Telemetry.excCode;
            Telemetry.ttype = 2; Telemetry.excCode = 7; Telemetry.code = 33; Telemetry.phase = 2;
            Telemetry.exc(2, new NullPointerException(), 100);
            checkRecord(Telemetry.EXC, 2 | 2 << 12 | 33 << 16, 100, 100, 1, "exc() of an NPE");
            check(Telemetry.code == 7, "exc() sets the '!' code");
            Telemetry.code = 33;
            Telemetry.exc(1, new GameActionException(GameActionExceptionType.CANT_MOVE_THERE, "x"), 100);
            checkRecord(Telemetry.EXC, 1 | (GameActionExceptionType.CANT_MOVE_THERE.ordinal() + 1) << 4 | 2 << 12 | 33 << 16, 100, 100, 0, "exc() of a GAE");
            Telemetry.exc(2, new IllegalStateException(), 100);
            check(lastRecord()[4] == 7, "exc class IllegalState");
            Telemetry.ttype = ttype; Telemetry.excCode = exc;
        } catch (Exception e) { threw = true; e.printStackTrace(); }
        check(!threw, "emitters and hooks do not throw on null or empty inputs");
        // trip() resets the per-trip counters and stamps the next trip's start
        Telemetry.tWait = 3; Telemetry.tCollect = 9; G.round = 250;
        Telemetry.trip(new MapLocation(2, 2), 40, 2, new MapLocation(20, 33), 2);
        int[] r = lastRecord();
        check(r[0] == -2 - Telemetry.TRIP && (r[3] >>> 16) == 250 && (r[4] & 255) == 3 && (r[4] >>> 24) == 9, "trip() record");
        check(Telemetry.tStart == 250 && Telemetry.tWait == 0 && Telemetry.tCollect == 0, "trip() resets the trip");
        // tripCount from carrier codes
        Telemetry.code = Telemetry.carrierCode(2, 2); Telemetry.tripCount(260);
        Telemetry.code = Telemetry.carrierCode(2, 2); Telemetry.tripCount(261);
        Telemetry.code = Telemetry.carrierCode(4, 2); Telemetry.tripCount(262);
        Telemetry.code = Telemetry.carrierCode(9, 2); Telemetry.tripCount(263);
        Telemetry.code = Telemetry.carrierCode(5, 1); Telemetry.tripCount(264);
        check(Telemetry.tCollect == 2 && Telemetry.tFirst == 260 && Telemetry.tLast == 261 && Telemetry.tWait == 1 && Telemetry.tFlee == 1
            && Telemetry.tExplore == 1, "tripCount");
        G.round = 0;
    }
}
