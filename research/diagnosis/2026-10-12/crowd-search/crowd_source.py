#!/usr/bin/env python3
"""Copy frozen own source and add one scratch-only no-alternative crowd branch."""
import argparse
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('repo', type=Path)
parser.add_argument('new_source_dir', type=Path)
args = parser.parse_args()
args.new_source_dir.mkdir()
for pkg in ('c_mend2', 'c_crowdprobe'):
    shutil.copytree(args.repo / 'src/c_mend2', args.new_source_dir / pkg)
    if pkg == 'c_crowdprobe':
        for path in (args.new_source_dir / pkg).glob('*.java'):
            text = path.read_text().replace('package c_mend2;', 'package c_crowdprobe;')
            text = text.replace('import c_mend2.', 'import c_crowdprobe.').replace('import static c_mend2.', 'import static c_crowdprobe.')
            path.write_text(text)
carrier = args.new_source_dir / 'c_crowdprobe/Carrier.java'
text = carrier.read_text()
assert text.count('    static int searchTurns;') == 1
text = text.replace('    static int searchTurns;', '''    static int searchTurns;
    // Scratch prototype only: one bounded empty-Mana no-alternative crowd search.
    static MapLocation crowdRejected;
    static int crowdExploreUntil;
    static final int CROWD_EXPLORE_TURNS = 12;''')
needle = '''        RobotController rc = G.rc;
        if (well == null) {'''
assert text.count(needle) == 1
text = text.replace(needle, '''        RobotController rc = G.rc;
        if (crowdRejected != null) {
            if (role != 2 || rc.getWeight() > 0 || G.round >= crowdExploreUntil) crowdRejected = null;
            else if (well == null) {
                MapLocation other = crowdKnownMana();
                if (other != null) {
                    well = other; crowdRejected = null;
                    if (C.TELEMETRY) wellHook(5, 2);
                } else {
                    state = 'X'; searchTurns++; explore(); return;
                }
            }
        }
        if (well == null) {''')
needle = 'else if (C.ROLES == 3 && role == 2) { well = null; centreTried = false; searchTurns = 0; }'
assert text.count(needle) == 1
text = text.replace(needle, '''else if (C.ROLES == 3 && role == 2) {
            if (G.rc.getWeight() == 0) { crowdRejected = well; crowdExploreUntil = G.round + CROWD_EXPLORE_TURNS; }
            well = null; centreTried = false; searchTurns = 0;
        }''')
needle = '    /** WELL record: `well` was just set to a non-null tile'
assert text.count(needle) == 1
text = text.replace(needle, '''    static MapLocation crowdKnownMana() throws GameActionException {
        MapLocation best = null; int bd = Integer.MAX_VALUE;
        for (int i = Comms.WELLS; i < Comms.WELLS + Comms.NWELLS; i++) {
            int c = Comms.read(i); if (c == 0) break;
            if ((c >>> 12) != 2) continue;
            MapLocation l = G.dec(c & 0xfff); if (l.equals(crowdRejected)) continue;
            int d = G.here.distanceSquaredTo(l); if (d < bd) { bd = d; best = l; }
        }
        for (int i = MapMem.seenWellCount(); --i >= 0; ) {
            if (MapMem.seenWellTypeAt(i) != 2) continue;
            MapLocation l = MapMem.seenWellAt(i); if (l.equals(crowdRejected)) continue;
            int d = G.here.distanceSquaredTo(l); if (d < bd) { bd = d; best = l; }
        }
        return best;
    }

''' + needle)
carrier.write_text(text)
