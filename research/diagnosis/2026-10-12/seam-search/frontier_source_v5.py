#!/usr/bin/env python3
"""Scratch coverage arms; no tracked source, field job or map-specific well constants."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('frozen_explore_source', type=Path)
parser.add_argument('new_output', type=Path)
args = parser.parse_args()

def normalized_hash(root, pkg):
    data = b''
    for path in sorted((root / pkg).glob('*.java')):
        text = path.read_text().replace('package ' + pkg + ';', 'package PKG;')
        text = text.replace('import ' + pkg + '.', 'import PKG.').replace('import static ' + pkg + '.', 'import static PKG.')
        data += text.encode()
    return hashlib.sha1(data).hexdigest()[:12]

assert normalized_hash(args.frozen_explore_source, 'c_explore1') == '409cfdfcbfd8'
assert normalized_hash(args.frozen_explore_source, 'c_mend2') == 'd62033781fbd'
args.new_output.mkdir()
shutil.copytree(args.frozen_explore_source / 'c_mend2', args.new_output / 'c_mend2')
for pkg, enabled, rounds in (('c_frontier0', False, 12), ('c_frontier12', True, 12), ('c_frontier24', True, 24)):
    shutil.copytree(args.frozen_explore_source / 'c_explore1', args.new_output / pkg)
    for path in (args.new_output / pkg).glob('*.java'):
        text = path.read_text().replace('package c_explore1;', 'package ' + pkg + ';')
        text = text.replace('import c_explore1.', 'import ' + pkg + '.').replace('import static c_explore1.', 'import static ' + pkg + '.')
        path.write_text(text)
    constants = args.new_output / pkg / 'C.java'
    text = constants.read_text().replace('CROWD_SEARCH = true;', 'CROWD_SEARCH = ' + str(enabled).lower() + ';')
    text = text.replace('CROWD_SEARCH_ROUNDS = 12, CROWD_SEARCH_GUARD = 3000;',
        'CROWD_SEARCH_ROUNDS = ' + str(rounds) + ', CROWD_SEARCH_GUARD = 6000;\n'
        '    public static final int CROWD_GRID_STEP = 6, CROWD_SCAN_MAX = 16, CROWD_SCAN_RESERVE = 4000;\n'
        '    public static final int CROWD_HQ_RADIUS = 24, CROWD_HOP_MAX = 20, CROWD_RETREAT_ROUNDS = 16;')
    constants.write_text(text)
    carrier = args.new_output / pkg / 'Carrier.java'
    text = carrier.read_text()
    text = text.replace('    static MapLocation crowdOutcomeWell;', '''    static MapLocation crowdOutcomeWell;
    static MapLocation crowdWaypoint, crowdRetreatHome, crowdWaypointLastPos;
    static int crowdCursor, crowdRetreatUntil, crowdWaypointStill;
    static boolean crowdCursorInit;
    public static int crowdWaypointChecks, crowdWaypointsReached, crowdRetreats;''')
    text = text.replace('''        if (C.CROWD_SEARCH && crowdOutcomeWell != null && role != 2) crowdOutcomeWell = null;''', '''        if (C.CROWD_SEARCH && crowdOutcomeWell != null && role != 2) crowdOutcomeWell = null;
        if (C.CROWD_SEARCH && crowdRetreatHome != null) {
            if (role != 2 || rc.getWeight() > 0 || G.round >= crowdRetreatUntil || G.here.distanceSquaredTo(crowdRetreatHome) <= 2)
                crowdRetreatHome = null;
            else {
                state = 'R';
                if (Clock.getBytecodesLeft() >= C.CROWD_SCAN_RESERVE) moveTwice(crowdRetreatHome);
                return;
            }
        }''')
    text = text.replace('''            if (role != 2 || rc.getWeight() > 0 || G.round >= crowdExploreUntil) crowdRejected = null;''', '''            if (role != 2 || rc.getWeight() > 0) { crowdRejected = null; crowdWaypoint = null; }
            else if (G.round >= crowdExploreUntil || crowdHQDistance(G.here) > C.CROWD_HQ_RADIUS) {
                crowdBeginRetreat(); state = 'R';
                if (crowdRetreatHome != null && Clock.getBytecodesLeft() >= C.CROWD_SCAN_RESERVE) moveTwice(crowdRetreatHome);
                return;
            }''')
    text = text.replace('well = other; crowdRejected = null; crowdOutcomeWell = other;',
                        'well = other; crowdRejected = null; crowdWaypoint = null; crowdOutcomeWell = other;')
    text = text.replace("state = 'X'; searchTurns++; crowdSearchTurns++; explore(); return;",
                        "searchTurns++; crowdExplore(); return;")
    text = text.replace('crowdExploreUntil = G.round + C.CROWD_SEARCH_ROUNDS; crowdSearchStarts++;',
                        'crowdExploreUntil = G.round + C.CROWD_SEARCH_ROUNDS; crowdWaypoint = null; crowdSearchStarts++;')
    text = text.replace('    static int crowdTrace(', '''    static int crowdHQDistance(MapLocation l) {
        MapLocation[] homes = HQState.ourHQs;
        if (homes == null || homes.length == 0) return Integer.MAX_VALUE;
        int best = Integer.MAX_VALUE;
        for (int i = homes.length; --i >= 0; ) if (homes[i] != null) {
            int d = G.cheb(l, homes[i]); if (d < best) best = d;
        }
        return best;
    }

    static void crowdBeginRetreat() {
        crowdRejected = null; crowdWaypoint = null;
        crowdRetreatHome = HQState.nearest(G.here);
        crowdRetreatUntil = G.round + C.CROWD_RETREAT_ROUNDS; crowdRetreats++;
    }

    /** Point coverage only: no guarantee that first sensing a grid point covers its surrounding tiles or clouds. */
    static void crowdExplore() throws GameActionException {
        if (crowdWaypoint != null) {
            if (crowdWaypointLastPos != null && G.here.equals(crowdWaypointLastPos)) crowdWaypointStill++;
            else crowdWaypointStill = 0;
            crowdWaypointLastPos = G.here;
            if (G.here.equals(crowdWaypoint)) { crowdWaypointsReached++; crowdWaypoint = null; }
            else if (MapMem.isWall(crowdWaypoint.x, crowdWaypoint.y) || Nav.stuckOn(crowdWaypoint) || crowdWaypointStill >= 3) crowdWaypoint = null;
        }
        if (crowdWaypoint == null) {
            MapLocation[] homes = HQState.ourHQs;
            int total = homes == null ? 0 : Math.min(4, homes.length) * 2;
            if (total == 0) { state = 'W'; return; }
            if (!crowdCursorInit) { crowdCursor = (G.id & 0x7fffffff) % total; crowdCursorInit = true; }
            if (crowdCursor >= total) crowdCursor %= total;
            MapLocation best = null; int bestScore = Integer.MIN_VALUE;
            for (int n = 0; n < total && n < C.CROWD_SCAN_MAX; n++) {
                if (Clock.getBytecodesLeft() < C.CROWD_SCAN_RESERVE) break;
                int index = crowdCursor++; if (crowdCursor == total) crowdCursor = 0;
                MapLocation home = homes[index / 2]; if (home == null) continue;
                int x = (index & 1) == 0 ? G.W / 2 : home.x;
                int y = (index & 1) == 0 ? home.y : G.H / 2;
                crowdWaypointChecks++;
                if (!G.onMap(x, y)) continue;
                if (MapMem.known(x, y) || MapMem.isWall(x, y)) continue;
                MapLocation l = new MapLocation(x, y);
                if (crowdRejected != null && crowdRejected.distanceSquaredTo(l) <= 25) continue;
                if (crowdHQDistance(l) > C.CROWD_HQ_RADIUS) continue;
                int score = 4 * (crowdRejected == null ? 0 : G.cheb(crowdRejected, l)) - G.cheb(G.here, l);
                if (score > bestScore) { bestScore = score; best = l; }
            }
            crowdWaypoint = best;
            crowdWaypointLastPos = G.here; crowdWaypointStill = 0;
        }
        state = 'W';
        if (crowdWaypoint != null && Clock.getBytecodesLeft() >= C.CROWD_SCAN_RESERVE) {
            state = 'X'; crowdSearchTurns++; moveTwice(crowdWaypoint);
        }
    }

    static int crowdTrace(''')
    carrier.write_text(text)
    for path in (args.new_output / pkg).glob('*.java'):
        if path.name in ('Carrier.java', 'C.java'):
            continue
        normalized = path.read_text().replace('package ' + pkg + ';', 'package c_mend2;')
        normalized = normalized.replace('import ' + pkg + '.', 'import c_mend2.').replace('import static ' + pkg + '.', 'import static c_mend2.')
        assert normalized == (args.new_output / 'c_mend2' / path.name).read_text(), 'unrelated source change'
info = {pkg: normalized_hash(args.new_output, pkg) for pkg in ('c_mend2', 'c_frontier0', 'c_frontier12', 'c_frontier24')}
(args.new_output / 'source-hashes.json').write_text(json.dumps(info, sort_keys=True, indent=2) + '\n')
print(json.dumps(info, sort_keys=True))
